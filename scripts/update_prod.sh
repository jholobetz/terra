#!/usr/bin/env bash
# ============================================================================
# Terra Physics Lab — Git-Native Production Update & Rollback Script
# Target Host: Debian 13 (/srv/www/terra, DocumentRoot /srv/www/terra/public)
# Domain:      https://physicslab.ca
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

MODE="standard"
ROLLBACK_REF=""
DRY_RUN=0
SKIP_HEALTH=0
BRANCH="master"
DOMAIN="physicslab.ca"
HEALTH_URL="https://physicslab.ca/healthz"
WEB_GROUP="www-data"
LAST_SHA_FILE="${REPO_ROOT}/app/log/.last_deployed_sha"

usage() {
    cat <<'EOF'
Usage: bash scripts/update_prod.sh [options]

Modes:
  (default)             Full update: git pull --ff-only, conditional composer/pip refresh,
                        DB migrations + delta shard sync + incremental HTML cache warm,
                        graceful PHP/Apache reload (when .php/.htaccess changed), and /healthz check.
  --quick               Fast content/equation delta sync: git pull --ff-only + cli_sync.php --warm-cache.
  --rollback [ref]      Roll back working tree to [ref] (defaults to prior deployed SHA),
                        sync shards/caches, reload PHP/Apache, and verify /healthz.

Options:
  --dry-run             Preview incoming commits and changed files without modifying anything.
  --branch <name>       Git branch to pull in standard/quick mode (default: master).
  --health-url <url>    Readiness probe URL (default: https://physicslab.ca/healthz).
  --skip-health         Skip post-update HTTP /healthz verification.
  -h, --help            Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick)
            MODE="quick"
            shift
            ;;
        --rollback)
            MODE="rollback"
            if [[ $# -gt 1 && ! "$2" =~ ^-- ]]; then
                ROLLBACK_REF="$2"
                shift 2
            else
                shift
            fi
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --branch)
            BRANCH="${2:?Missing branch name after --branch}"
            shift 2
            ;;
        --health-url)
            HEALTH_URL="${2:?Missing URL after --health-url}"
            shift 2
            ;;
        --skip-health)
            SKIP_HEALTH=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

ensure_clean_tracked_tree() {
    local dirty
    dirty="$(git status --porcelain --untracked-files=no)"
    if [[ -n "${dirty}" ]]; then
        echo "[ERROR] Tracked files in ${REPO_ROOT} have uncommitted local changes:" >&2
        echo "${dirty}" >&2
        echo "Commit & push (or git checkout -- <file>) before pulling to avoid split-brain conflicts." >&2
        exit 1
    fi
}

fix_runtime_permissions() {
    mkdir -p "${REPO_ROOT}/app/log" "${REPO_ROOT}/public/cache"
    if getent group "${WEB_GROUP}" >/dev/null 2>&1; then
        chgrp -R "${WEB_GROUP}" "${REPO_ROOT}/app/log" "${REPO_ROOT}/public/cache" 2>/dev/null || sudo -n chgrp -R "${WEB_GROUP}" "${REPO_ROOT}/app/log" "${REPO_ROOT}/public/cache" 2>/dev/null || true

        local cfg_file="${REPO_ROOT}/app/config/config.php"
        if [[ -f "${cfg_file}" ]]; then
            local cfg_group=""
            cfg_group="$(stat -c '%G' "${cfg_file}" 2>/dev/null || stat -f '%Sg' "${cfg_file}" 2>/dev/null || echo "")"
            if [[ "${cfg_group}" != "${WEB_GROUP}" ]]; then
                echo "-> Restoring ${WEB_GROUP} group read access on app/config/config.php..."
                if chgrp "${WEB_GROUP}" "${cfg_file}" 2>/dev/null || sudo -n chgrp "${WEB_GROUP}" "${cfg_file}" 2>/dev/null; then
                    chmod 640 "${cfg_file}" 2>/dev/null || true
                elif [[ -t 0 && -t 1 ]]; then
                    sudo chgrp "${WEB_GROUP}" "${cfg_file}" && chmod 640 "${cfg_file}" 2>/dev/null || true
                else
                    echo "[WARN] app/config/config.php group is '${cfg_group}' (expected '${WEB_GROUP}'); run 'sudo chgrp ${WEB_GROUP} ${cfg_file} && chmod 640 ${cfg_file}'." >&2
                fi
            else
                chmod 640 "${cfg_file}" 2>/dev/null || true
            fi
        fi
    fi
    chmod 2775 "${REPO_ROOT}/app/log" "${REPO_ROOT}/public/cache" 2>/dev/null || true
    chmod -R g+rwX "${REPO_ROOT}/app/log" "${REPO_ROOT}/public/cache" 2>/dev/null || true
}

reload_web_workers() {
    echo "-> Reloading PHP / Apache workers to refresh OPcache..."
    if ! command -v systemctl >/dev/null 2>&1; then
        return 0
    fi

    local active_svcs=()
    for svc in php8.4-fpm php8.3-fpm php8.2-fpm php-fpm apache2; do
        if systemctl is-active --quiet "${svc}" 2>/dev/null; then
            active_svcs+=("${svc}")
        fi
    done

    if [[ "${#active_svcs[@]}" -eq 0 ]]; then
        return 0
    fi

    if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
        systemctl --no-ask-password reload "${active_svcs[@]}"
        echo "✓ Reloaded: ${active_svcs[*]}"
    elif sudo -n systemctl reload "${active_svcs[@]}" 2>/dev/null; then
        echo "✓ Reloaded: ${active_svcs[*]}"
    elif [[ -t 0 && -t 1 ]]; then
        if sudo systemctl reload "${active_svcs[@]}"; then
            echo "✓ Reloaded: ${active_svcs[*]}"
        else
            echo "   [NOTE] Run 'sudo systemctl reload ${active_svcs[*]}' to flush OPcache."
        fi
    else
        echo "   [NOTE] Run 'sudo systemctl reload ${active_svcs[*]}' to flush OPcache."
    fi
}

verify_healthz() {
    if [[ "${SKIP_HEALTH}" -eq 1 ]]; then
        echo "-> Skipping /healthz probe (--skip-health)."
        return 0
    fi
    echo "-> Probing readiness endpoint (${HEALTH_URL})..."
    local resp=""
    if [[ "${HEALTH_URL}" == "https://${DOMAIN}/healthz" ]]; then
        resp="$(curl -fsSL --max-time 5 --resolve "${DOMAIN}:443:127.0.0.1" "${HEALTH_URL}" 2>/dev/null || curl -fsSL --max-time 5 "${HEALTH_URL}")"
    else
        resp="$(curl -fsSL --max-time 5 "${HEALTH_URL}")"
    fi

    if [[ "${resp}" == *'"status":"ok"'* ]]; then
        echo "✓ Health check passed: ${resp}"
    else
        echo "[ERROR] Health check did not return status=ok: ${resp}" >&2
        exit 1
    fi
}

ensure_clean_tracked_tree
PRE_SHA="$(git rev-parse HEAD)"

if [[ "${MODE}" == "rollback" ]]; then
    if [[ -z "${ROLLBACK_REF}" ]]; then
        if [[ -f "${LAST_SHA_FILE}" ]]; then
            ROLLBACK_REF="$(tr -d '[:space:]' < "${LAST_SHA_FILE}")"
        else
            echo "[ERROR] No rollback ref provided and ${LAST_SHA_FILE} does not exist." >&2
            exit 1
        fi
    fi

    echo "=== Rolling back ${REPO_ROOT} from ${PRE_SHA:0:9} to ${ROLLBACK_REF} ==="
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        git diff --stat "${PRE_SHA}" "${ROLLBACK_REF}"
        echo "[DRY-RUN] No changes applied."
        exit 0
    fi

    # Stay attached to ${BRANCH} rather than leaving production in detached HEAD
    git checkout -B "${BRANCH}" "${ROLLBACK_REF}"
    if git diff --name-only "${PRE_SHA}" "${ROLLBACK_REF}" | grep -qE '^composer\.(json|lock)$'; then
        if command -v composer >/dev/null 2>&1; then
            echo "=== Reconciling Composer production dependencies ==="
            composer install --no-dev --optimize-autoloader --no-interaction
        fi
    fi
    if git diff --name-only "${PRE_SHA}" "${ROLLBACK_REF}" | grep -qE '^requirements(-prod)?\.txt$'; then
        if [[ -x "${REPO_ROOT}/.venv/bin/pip" && -f "${REPO_ROOT}/requirements-prod.txt" ]]; then
            echo "=== Reconciling Python production dependencies ==="
            "${REPO_ROOT}/.venv/bin/pip" install -q -r "${REPO_ROOT}/requirements-prod.txt"
        fi
    fi
    APP_ENV=production php "${REPO_ROOT}/cli_sync.php" --warm-cache
    fix_runtime_permissions
    reload_web_workers
    verify_healthz
    echo "✓ Rollback to $(git rev-parse --short HEAD) on branch '${BRANCH}' complete."
    exit 0
fi

echo "=== Fetching latest commits from origin/${BRANCH} ==="
git fetch origin "${BRANCH}"
REMOTE_SHA="$(git rev-parse "origin/${BRANCH}")"

if [[ "${PRE_SHA}" == "${REMOTE_SHA}" ]]; then
    echo "Working tree already at latest origin/${BRANCH} (${PRE_SHA:0:9})."
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        exit 0
    fi
    APP_ENV=production php "${REPO_ROOT}/cli_sync.php" --warm-cache
    fix_runtime_permissions
    verify_healthz
    exit 0
fi

CHANGED_FILES="$(git diff --name-only "${PRE_SHA}..${REMOTE_SHA}")"
echo "Incoming commits (${PRE_SHA:0:9} -> ${REMOTE_SHA:0:9}):"
git log --oneline "${PRE_SHA}..${REMOTE_SHA}"

if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo ""
    echo "Changed files:"
    echo "${CHANGED_FILES}"
    echo "[DRY-RUN] No changes applied."
    exit 0
fi

mkdir -p "$(dirname "${LAST_SHA_FILE}")"
echo "${PRE_SHA}" > "${LAST_SHA_FILE}"

echo "-> Pulling fast-forward delta..."
git pull --ff-only origin "${BRANCH}"

if [[ "${MODE}" == "standard" ]]; then
    if echo "${CHANGED_FILES}" | grep -Eq '^composer\.(json|lock)$'; then
        echo "-> composer.json/lock changed; updating vendor/ (--no-dev)..."
        composer install --no-dev --optimize-autoloader --no-interaction
    fi

    if echo "${CHANGED_FILES}" | grep -Eq '^requirements\.txt$'; then
        if [[ -x "${REPO_ROOT}/.venv/bin/pip" ]]; then
            echo "-> requirements.txt changed; updating Python .venv..."
            "${REPO_ROOT}/.venv/bin/pip" install -r "${REPO_ROOT}/requirements.txt"
        fi
    fi
fi

echo "-> Running MariaDB delta sync, migrations, and incremental HTML cache warmer..."
APP_ENV=production php "${REPO_ROOT}/cli_sync.php" --warm-cache
fix_runtime_permissions

if echo "${CHANGED_FILES}" | grep -Eq '\.php$|^\.htaccess$|^public/\.htaccess$'; then
    reload_web_workers
fi

verify_healthz
echo "✓ Production update complete (${PRE_SHA:0:9} -> ${REMOTE_SHA:0:9})."
