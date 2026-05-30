"""Shared fixtures for Physics Lab tests.

Tests drive scripts as black-box subprocesses against an isolated tempdir.
This file owns workspace setup and the gate-runner helper; individual test
files own their payload construction.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "maintenance" / "run_gqs_sprint.py"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3"

# Make `from scripts.maintenance.X import Y` resolvable for unit tests that
# import helpers directly. Black-box subprocess tests don't need this.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _isolated_git_env():
    return {
        **os.environ,
        "GIT_AUTHOR_NAME": "Physics Lab Test",
        "GIT_AUTHOR_EMAIL": "test@physicslab.invalid",
        "GIT_COMMITTER_NAME": "Physics Lab Test",
        "GIT_COMMITTER_EMAIL": "test@physicslab.invalid",
    }


@pytest.fixture
def workspace(tmp_path):
    """Tempdir with subfiles/ and a fresh git repo, ready for run_gqs_sprint.py."""
    (tmp_path / "subfiles").mkdir()
    subprocess.run(
        ["git", "init", "-q"],
        cwd=tmp_path,
        env=_isolated_git_env(),
        check=True,
    )
    return tmp_path


@pytest.fixture
def backlog_workspace(tmp_path, monkeypatch):
    """Tempdir with app/config/content/ and subfiles/; chdir's into the workspace.

    sync_backlog.py uses cwd-relative CONTENT_DIR and BACKLOG_PATH constants,
    so tests need both directories present and the process rooted in tmp_path.
    """
    (tmp_path / "app" / "config" / "content").mkdir(parents=True)
    (tmp_path / "subfiles").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def shield_workspace(tmp_path, monkeypatch):
    """Tempdir with app/config/content/ scaffold; chdir's into the workspace.

    IntegrityShield reads global_slug_registry.json from cwd in its targeted
    path, so each test runs from its own workspace to avoid leaking real
    project state. Returns the content_dir Path; tests populate it.
    """
    content_dir = tmp_path / "app" / "config" / "content"
    content_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return content_dir


@pytest.fixture
def run_gates(workspace):
    """Returns a function: payload_dict -> CompletedProcess from run_gqs_sprint.py --dry-run."""
    def _run(payload):
        payload_path = workspace / "subfiles" / "batch_payload.json"
        payload_path.write_text(json.dumps(payload))
        return subprocess.run(
            [str(VENV_PYTHON), str(SCRIPT_PATH), "--dry-run"],
            cwd=workspace,
            env=_isolated_git_env(),
            capture_output=True,
            text=True,
        )
    return _run
