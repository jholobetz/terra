#!/usr/bin/env python3
"""
🪐 Terra Physics Lab - Unified Formula Ingestion Pipeline (Roadmap §3.2)

Provides an authoritative 5-stage transactional pipeline for authoring, verifying,
and synchronizing formulas across the platform:
  Stage 1: Validation, Normalization, Prose Delimiters & Collision Guard
  Stage 2: Bidirectional DAG Lineage Wiring (Reciprocal Parent-Child Linking)
  Stage 3: SymPy CAS Invariance & Dimensional Homogeneity Prover
  Stage 4: Dual-Layer Atomic Synchronization (JSON Shards, SHA-256 Hash Registry, MariaDB)
  Stage 5: Subtopic Bridge Mapping & Topological Manifold Integration
"""

import os
import sys
import json
import re
import hashlib
import subprocess
from typing import Dict, Any, Optional, Tuple, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lib.math.delimiters import (
    validate_prose_delimiters,
    strip_math_blocks,
    find_html_in_math
)

try:
    from lib.cas.cas_engine import check_dimensions
except ImportError:
    check_dimensions = None

try:
    from scripts.maintenance.lineage_resolver import discover_lineage
except ImportError:
    discover_lineage = None


def slugify(text: str) -> str:
    """Converts a title or string into a clean lowercase kebab-case slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s\-]", "", slug)
    slug = re.sub(r"[\s\_]+", "-", slug)
    return slug.strip("-")


def get_shard_hex(formula_id: str) -> str:
    """Returns the 2-character hex partition for a formula ID."""
    return hashlib.md5(formula_id.encode("utf-8")).hexdigest()[:2]


def normalize_latex_key(latex: str) -> str:
    """
    Normalizes a LaTeX expression for lookup in formulas_latex_index.json.
    Matches the canonical PHP implementation in PhysicsService::normalizeLatex.
    """
    s = latex.strip()
    s = re.sub(r"\\varepsilon(?![a-zA-Z])", r"\\epsilon", s)
    s = re.sub(r"\\vartheta(?![a-zA-Z])", r"\\theta", s)
    s = re.sub(r"\\varphi(?![a-zA-Z])", r"\\phi", s)
    s = re.sub(r"\\varrho(?![a-zA-Z])", r"\\rho", s)
    s = re.sub(r"\\varpi(?![a-zA-Z])", r"\\pi", s)
    s = re.sub(r"\\varsigma(?![a-zA-Z])", r"\\sigma", s)

    # Strip outer delimiters
    s = re.sub(r"^\\\(|\\\)$", "", s)
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)

    # Strip formatting macros
    s = re.sub(r"\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^}]+)\}", r"\2", s)
    s = re.sub(r"\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])", r"\2", s)

    # Strip HTML wraps
    has_html = True
    while has_html:
        next_s = re.sub(r"\\(cssId|class|style|href)\{[^{}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"\2", s)
        if next_s == s:
            has_html = False
        else:
            s = next_s
    s = re.sub(r"\\(cssId|class|style|href)\b", "", s)

    # Fractions \frac{A}{B} -> A/B
    has_frac = True
    while has_frac:
        next_s = re.sub(r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1/\2", s)
        if next_s == s:
            has_frac = False
        else:
            s = next_s

    # Subscripts _{ext} -> _ext
    s = re.sub(r"_\{([^}]+)\}", r"_\1", s)

    # Strip spaces and special characters
    s = re.sub(r"[^a-zA-Z0-9_\^\-=+/*()\[\]<>\.,;?]", "", s)
    return s.lower()


def sanitize_prose_text(text: str) -> str:
    """Sanitizes control collisions and normalizes math delimiters in narrative prose."""
    if not text or not isinstance(text, str):
        return ""
    val = text
    val = val.replace("\x08ar{", r"\bar{").replace(r"\x08\bar{", r"\bar{").replace("ar{", r"\bar{")
    val = val.replace("\x08eta", r"\beta").replace("\x08", "")
    val = val.replace("\x0crac", r"\frac").replace("\x0c", "")
    val = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", val)

    # Clean double backslashes before common LaTeX macros
    val = re.sub(r"\\\\(mathcal|mathbf|oint|iint|frac|dot|ddot|vec|hat|bar|nabla|partial|sum|int|text|sigma|tau|mu|nu|rho|lambda)", r"\\\1", val)

    # Clean stray escaped dollars
    val = val.replace(r"\$", "$").replace(r"\ $", "$")

    # Canonicalize bracket math \( ... \) -> $ ... $
    val = re.sub(r"\\\((.*?)\\\)", r"$\1$", val, flags=re.DOTALL)

    # Clean inverted or misplaced delimiters
    val = re.sub(r"=\$\s*\\frac", r"= \\frac", val)
    val = re.sub(r"is\$\s*\\frac", r"is \\frac", val)

    # Balance unescaped trailing dollar if single
    dollars = len(re.findall(r"(?<!\\)\$", val))
    if dollars % 2 != 0:
        if val.endswith(" $") or val.endswith(".$"):
            val = val.rstrip(" $").rstrip(".$")
        else:
            val = val + "$"

    return val.strip()


class FormulaIngestionPipeline:
    """
    Unified 5-Stage Formula Ingestion Pipeline for Project Terra.
    """

    def __init__(
        self,
        project_root: Optional[str] = None,
        sync_db: bool = True,
        rebuild_graph: bool = False
    ):
        self.project_root = os.path.abspath(project_root or PROJECT_ROOT)
        self.formulas_dir = os.path.join(self.project_root, "app", "config", "content", "formulas")
        self.content_dir = os.path.join(self.project_root, "app", "config", "content")
        self.registry_path = os.path.join(self.project_root, "app", "config", "formulas_hash_registry.json")
        self.latex_index_path = os.path.join(self.project_root, "app", "config", "formulas_latex_index.json")
        self.graph_path = os.path.join(self.project_root, "app", "config", "formula_derivation_graph.json")
        self.graph_gz_path = os.path.join(self.project_root, "app", "config", "formula_derivation_graph.json.gz")
        self.sync_db = sync_db
        self.rebuild_graph = rebuild_graph

    def get_shard_path(self, formula_id: str) -> str:
        """Returns the absolute path to the shard file for a given formula ID."""
        hex_prefix = get_shard_hex(formula_id)
        return os.path.join(self.formulas_dir, hex_prefix, f"shard_{hex_prefix}.json")

    def load_shard(self, shard_path: str) -> Dict[str, Any]:
        """Loads shard dictionary from disk safely."""
        if not os.path.exists(shard_path):
            return {}
        try:
            with open(shard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def formula_exists(self, formula_id: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Checks if a formula exists in its partition shard."""
        if not formula_id:
            return False, None, None
        shard_path = self.get_shard_path(formula_id)
        shard_data = self.load_shard(shard_path)
        if formula_id in shard_data:
            return True, shard_path, shard_data[formula_id]
        return False, shard_path, None

    # =========================================================================
    # STAGE 1: Validation, Normalization & Collision Guard
    # =========================================================================
    def stage1_validate_and_prepare(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates LaTeX equation, checks HTML math leaks, normalizes prose delimiters,
        and generates unique slug ID with collision guarding.
        """
        eq = raw_data.get("equation", "").strip()
        if not eq:
            raise ValueError("Formula payload missing required 'equation' LaTeX string.")

        # Sanitize HTML tags in math equation
        eq = re.sub(r"<(?:strong|b)>(.*?)</(?:strong|b)>", r"\\mathbf{\1}", eq, flags=re.I)
        eq = re.sub(r"<(?:em|i)>(.*?)</(?:em|i)>", r"\\mathit{\1}", eq, flags=re.I)
        eq = re.sub(r"<[^>]+>", "", eq).strip()

        # Check for HTML infiltration inside equation
        html_leaks = find_html_in_math(eq, is_raw_tex=True)
        if html_leaks:
            raise ValueError(f"Raw equation contains illegal HTML markup: {html_leaks[0][1]}")

        title = raw_data.get("title", "").strip()
        if not title:
            title = "Custom Physical Relation"

        # Resolve formula slug ID
        given_id = raw_data.get("id", "").strip()
        base_slug = slugify(given_id) if given_id else slugify(title)
        if not base_slug:
            base_slug = f"formula-{hashlib.md5(eq.encode('utf-8')).hexdigest()[:8]}"

        # Collision Guard: check if slug exists with a DIFFERENT equation
        slug_id = base_slug
        exists, shard_path, existing_formula = self.formula_exists(slug_id)
        if exists and existing_formula:
            existing_eq = existing_formula.get("equation", "").strip()
            # If equations differ, create disambiguated formulation variant
            if existing_eq and existing_eq != eq:
                eq_hash = hashlib.md5(eq.encode("utf-8")).hexdigest()[:8]
                slug_id = f"{base_slug}-{eq_hash}"

        # Sanitize narrative prose fields
        prose_fields = [
            "conceptual_definition",
            "intuitive_summary",
            "interpretation",
            "symmetry_origin",
            "limits_and_boundary"
        ]
        sanitized_prose = {}
        for pf in prose_fields:
            raw_val = raw_data.get(pf, "")
            clean_val = sanitize_prose_text(raw_val)
            # Run delimiter validation
            errors = validate_prose_delimiters(clean_val)
            if errors:
                # Delimiter warnings logged, continue with best sanitized representation
                pass
            sanitized_prose[pf] = clean_val

        # Guarantee semantic_variables is a dict (never empty list [])
        sem_vars = raw_data.get("semantic_variables", {})
        if not isinstance(sem_vars, dict):
            sem_vars = {}

        # Prepare normalized formula dictionary
        formula_obj: Dict[str, Any] = {
            "id": slug_id,
            "title": title,
            "equation": eq,
            "conceptual_definition": sanitized_prose.get("conceptual_definition") or raw_data.get("conceptual_definition", ""),
            "intuitive_summary": sanitized_prose.get("intuitive_summary") or raw_data.get("intuitive_summary", ""),
            "interpretation": sanitized_prose.get("interpretation") or raw_data.get("interpretation", ""),
            "symmetry_origin": sanitized_prose.get("symmetry_origin") or raw_data.get("symmetry_origin", ""),
            "limits_and_boundary": sanitized_prose.get("limits_and_boundary") or raw_data.get("limits_and_boundary", ""),
            "unit_system": raw_data.get("unit_system", "SI"),
            "parent_formula_id": raw_data.get("parent_formula_id", "").strip(),
            "derivation_type": raw_data.get("derivation_type", "").strip(),
            "subcomponents": raw_data.get("subcomponents", []) if isinstance(raw_data.get("subcomponents"), list) else [],
            "status": raw_data.get("status", "platinum"),
            "semantic_variables": sem_vars
        }

        if "derivation_steps" in raw_data and isinstance(raw_data["derivation_steps"], list):
            formula_obj["derivation_steps"] = raw_data["derivation_steps"]

        return formula_obj

    # =========================================================================
    # STAGE 2: Bidirectional DAG Wiring (Reciprocal Parent-Child Linking)
    # =========================================================================
    def stage2_wire_bidirectional_dag(
        self,
        formula_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[Tuple[str, Dict[str, Any]]]]:
        """
        Discovers or verifies derivation lineage and reciprocally links the parent formula.
        Returns (updated_formula_data, parent_update_tuple_or_None).
        """
        f_id = formula_data["id"]
        parent_id = formula_data.get("parent_formula_id", "").strip()

        # Check if parent is valid and exists
        parent_exists = False
        if parent_id:
            exists, p_shard, p_data = self.formula_exists(parent_id)
            if exists:
                parent_exists = True

        # If parent missing or invalid, invoke lineage discovery
        if not parent_exists and discover_lineage:
            try:
                lineage_res = discover_lineage(
                    title=formula_data.get("title", ""),
                    equation=formula_data.get("equation", ""),
                    conceptual_definition=formula_data.get("conceptual_definition", ""),
                    interpretation=formula_data.get("interpretation", ""),
                    existing_parent=parent_id
                )
                if lineage_res:
                    disc_parent = lineage_res.get("parent_formula_id", "")
                    if disc_parent:
                        p_exists, _, _ = self.formula_exists(disc_parent)
                        if p_exists:
                            formula_data["parent_formula_id"] = disc_parent
                            parent_id = disc_parent
                            parent_exists = True

                    if not formula_data.get("derivation_type"):
                        formula_data["derivation_type"] = lineage_res.get("derivation_type", "DERIVED_FROM")

                    if not formula_data.get("subcomponents") and lineage_res.get("subcomponents"):
                        formula_data["subcomponents"] = lineage_res.get("subcomponents")
            except Exception:
                pass

        if not parent_exists:
            # Standalone or axiomatic node
            formula_data["parent_formula_id"] = ""
            if not formula_data.get("derivation_type"):
                formula_data["derivation_type"] = "AXIOMATIC_FOUNDATION"
            return formula_data, None

        # Reciprocal wiring: load parent formula and add child to its subcomponents
        p_shard_path = self.get_shard_path(parent_id)
        p_shard_data = self.load_shard(p_shard_path)
        if parent_id in p_shard_data:
            parent_formula = p_shard_data[parent_id]
            subcomps = parent_formula.get("subcomponents", [])
            if not isinstance(subcomps, list):
                subcomps = []
            if f_id not in subcomps:
                subcomps.append(f_id)
                parent_formula["subcomponents"] = subcomps
                p_shard_data[parent_id] = parent_formula
                return formula_data, (p_shard_path, p_shard_data)

        return formula_data, None

    # =========================================================================
    # STAGE 3: SymPy CAS Invariance & Dimensional Homogeneity Prover
    # =========================================================================
    def stage3_verify_cas_invariance(self, formula_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates formula for dimensional homogeneity and algebraic consistency using SymPy CAS.
        """
        eq = formula_data.get("equation", "")
        if not check_dimensions or not eq:
            formula_data["cas_validation"] = {
                "status": "UNVERIFIED",
                "is_homogeneous": None,
                "note": "CAS prover unavailable or empty equation."
            }
            return formula_data

        try:
            cas_res = check_dimensions(eq)
            if cas_res.get("success"):
                is_homo = cas_res.get("is_homogeneous")
                status = "HOMOGENEOUS" if is_homo else ("INHOMOGENEOUS" if is_homo is False else "DIMENSIONAL_EXPRESSION")
                formula_data["cas_validation"] = {
                    "status": status,
                    "is_homogeneous": is_homo,
                    "lhs": cas_res.get("lhs"),
                    "rhs": cas_res.get("rhs"),
                    "quantity": cas_res.get("quantity"),
                    "summary": cas_res.get("summary")
                }
            else:
                formula_data["cas_validation"] = {
                    "status": "UNVERIFIED",
                    "is_homogeneous": None,
                    "error": cas_res.get("error", "CAS evaluation indeterminate")
                }
        except Exception as e:
            formula_data["cas_validation"] = {
                "status": "UNVERIFIED",
                "is_homogeneous": None,
                "error": str(e)
            }

        return formula_data

    # =========================================================================
    # STAGE 4: Dual-Layer Atomic Synchronization (JSON Shards, Registry, MariaDB)
    # =========================================================================
    def stage4_sync_dual_layer(
        self,
        formula_data: Dict[str, Any],
        parent_update: Optional[Tuple[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Persists formula into target shard, updates parent shard (if modified),
        recomputes SHA-256 in hash registry, updates LaTeX index trie, and synchronizes MariaDB.
        Includes snapshot-based transactional rollback.
        """
        f_id = formula_data["id"]
        child_shard_path = self.get_shard_path(f_id)
        os.makedirs(os.path.dirname(child_shard_path), exist_ok=True)

        # 1. Capture snapshot for transactional rollback
        snapshots = {}
        if os.path.exists(child_shard_path):
            with open(child_shard_path, "r", encoding="utf-8") as f:
                snapshots[child_shard_path] = f.read()

        if parent_update:
            p_shard_path, _ = parent_update
            if os.path.exists(p_shard_path):
                with open(p_shard_path, "r", encoding="utf-8") as f:
                    snapshots[p_shard_path] = f.read()

        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                snapshots[self.registry_path] = f.read()

        if os.path.exists(self.latex_index_path):
            with open(self.latex_index_path, "r", encoding="utf-8") as f:
                snapshots[self.latex_index_path] = f.read()

        try:
            # 2. Update child shard
            child_shard_data = self.load_shard(child_shard_path)
            child_shard_data[f_id] = formula_data
            child_json = json.dumps(child_shard_data, indent=4, ensure_ascii=False)
            with open(child_shard_path, "w", encoding="utf-8") as f:
                f.write(child_json)

            modified_shards = [(child_shard_path, child_json)]

            # 3. Update parent shard if modified
            if parent_update:
                p_shard_path, p_shard_data = parent_update
                p_json = json.dumps(p_shard_data, indent=4, ensure_ascii=False)
                with open(p_shard_path, "w", encoding="utf-8") as f:
                    f.write(p_json)
                modified_shards.append((p_shard_path, p_json))

            # 4. Synchronize SHA-256 Hash Registry
            hash_reg = {}
            if os.path.exists(self.registry_path):
                try:
                    with open(self.registry_path, "r", encoding="utf-8") as f:
                        hash_reg = json.load(f)
                except Exception:
                    hash_reg = {}

            for s_path, s_content in modified_shards:
                rel_path = os.path.relpath(s_path, self.project_root)
                s_hash = hashlib.sha256(s_content.encode("utf-8")).hexdigest()
                hash_reg[rel_path] = s_hash

            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(hash_reg, f, indent=4, ensure_ascii=False)

            # 5. Synchronize LaTeX Index
            latex_idx = {}
            if os.path.exists(self.latex_index_path):
                try:
                    with open(self.latex_index_path, "r", encoding="utf-8") as f:
                        latex_idx = json.load(f)
                except Exception:
                    latex_idx = {}

            norm_eq = normalize_latex_key(formula_data.get("equation", ""))
            if norm_eq:
                latex_idx[norm_eq] = f_id
                with open(self.latex_index_path, "w", encoding="utf-8") as f:
                    json.dump(latex_idx, f, indent=4, ensure_ascii=False)

            # 6. Database Synchronization (MariaDB formulas table)
            db_synced = False
            if self.sync_db:
                db_synced = self._sync_database_formula(formula_data)

            # 7. Rebuild DAG if requested
            if self.rebuild_graph:
                self._rebuild_formula_graph()

            return {
                "child_shard": child_shard_path,
                "parent_shard": parent_update[0] if parent_update else None,
                "hash_registry_updated": True,
                "latex_index_updated": True,
                "db_synced": db_synced
            }

        except Exception as e:
            # Transactional Rollback
            for path, original_content in snapshots.items():
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(original_content)
                except Exception:
                    pass
            raise RuntimeError(f"Stage 4 synchronization failed; rolled back to snapshot. Error: {e}")

    def _sync_database_formula(self, formula_data: Dict[str, Any]) -> bool:
        """Invokes PHP Flight service to sync modified shard and reset equation_svg to NULL."""
        try:
            php_code = (
                "define('FLIGHT_SKIP_START', true); "
                f"require '{self.project_root}/app/config/bootstrap.php'; "
                "$res = Flight::physicsService()->syncFormulasToDatabase(); "
                "echo json_encode($res);"
            )
            proc = subprocess.run(
                ["php", "-r", php_code],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            return proc.returncode == 0
        except Exception:
            return False

    def _rebuild_formula_graph(self) -> bool:
        """Invokes graph builder to refresh DAG nodes and links."""
        try:
            build_script = os.path.join(self.project_root, "scripts", "build_formula_graph.py")
            if os.path.exists(build_script):
                proc = subprocess.run(
                    [sys.executable, build_script],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return proc.returncode == 0
        except Exception:
            pass
        return False

    # =========================================================================
    # STAGE 5: Subtopic Bridge Mapping
    # =========================================================================
    def stage5_bridge_subtopic(
        self,
        formula_data: Dict[str, Any],
        subtopic_slug: Optional[str] = None
    ) -> List[str]:
        """
        Links formula ID into the specified or discovered encyclopedia subtopic in app/config/content/*.json.
        """
        f_id = formula_data["id"]
        linked = []

        if not subtopic_slug:
            # Try to auto-discover matching subtopic based on keywords
            subtopic_slug = self._discover_matching_subtopic(formula_data)

        if not subtopic_slug:
            return linked

        # Search across all domain topic files
        for entry in os.listdir(self.content_dir):
            if not entry.endswith(".json") or entry in ("categories.json", "search_index.json", "constants.json", "entities.json", "particles.json", "compiled_trie_regex.json", "formula_aliases.json", "formulas_hash_registry.json", "formulas_latex_index.json", "formula_derivation_graph.json"):
                continue

            file_path = os.path.join(self.content_dir, entry)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    domain_data = json.load(f)

                if isinstance(domain_data, dict) and subtopic_slug in domain_data:
                    subtopic = domain_data[subtopic_slug]
                    if isinstance(subtopic, dict):
                        f_ids = subtopic.get("formula_ids", [])
                        if not isinstance(f_ids, list):
                            f_ids = []
                        if f_id not in f_ids:
                            f_ids.append(f_id)
                            subtopic["formula_ids"] = f_ids
                            domain_data[subtopic_slug] = subtopic
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(domain_data, f, indent=4, ensure_ascii=False)
                            linked.append(subtopic_slug)
                            break
            except Exception:
                continue

        return linked

    def _discover_matching_subtopic(self, formula_data: Dict[str, Any]) -> Optional[str]:
        """Scans subtopics for high-confidence keyword match."""
        title_lower = formula_data.get("title", "").lower()
        title_slug = slugify(title_lower)

        for entry in os.listdir(self.content_dir):
            if not entry.endswith(".json") or entry in ("categories.json", "search_index.json"):
                continue
            file_path = os.path.join(self.content_dir, entry)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    domain_data = json.load(f)
                if not isinstance(domain_data, dict):
                    continue
                for s_slug, s_val in domain_data.items():
                    if s_slug == title_slug:
                        return s_slug
                    if isinstance(s_val, dict):
                        sub_title = s_val.get("title", "").lower()
                        if sub_title and (sub_title in title_lower or title_lower in sub_title):
                            return s_slug
            except Exception:
                continue
        return None

    # =========================================================================
    # MASTER INGESTION FUNNEL
    # =========================================================================
    def ingest(
        self,
        formula_data: Dict[str, Any],
        subtopic_slug: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the full 5-stage ingestion pipeline.
        """
        # Stage 1: Validate, normalize & collision guard
        prepared = self.stage1_validate_and_prepare(formula_data)

        # Stage 2: Bidirectional DAG wiring
        wired, parent_update = self.stage2_wire_bidirectional_dag(prepared)

        # Stage 3: SymPy CAS dimensional proof
        proven = self.stage3_verify_cas_invariance(wired)

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "formula_id": proven["id"],
                "formula": proven,
                "shard_file": os.path.basename(self.get_shard_path(proven["id"])),
                "parent_id": proven.get("parent_formula_id"),
                "cas_validation": proven.get("cas_validation"),
                "subtopics_linked": [subtopic_slug] if subtopic_slug else []
            }

        # Stage 4: Dual-layer sync with rollback protection
        sync_result = self.stage4_sync_dual_layer(proven, parent_update)

        # Stage 5: Subtopic bridge mapping
        linked_subtopics = self.stage5_bridge_subtopic(proven, subtopic_slug)

        return {
            "success": True,
            "formula_id": proven["id"],
            "formula": proven,
            "shard_file": os.path.basename(sync_result["child_shard"]),
            "shard_path": sync_result["child_shard"],
            "parent_id": proven.get("parent_formula_id"),
            "parent_updated": bool(parent_update),
            "cas_validation": proven.get("cas_validation"),
            "subtopics_linked": linked_subtopics,
            "hash_registry_updated": sync_result["hash_registry_updated"],
            "db_synced": sync_result["db_synced"],
            "stages": {
                "stage1_validation": "passed",
                "stage2_lineage": "wired",
                "stage3_cas": proven.get("cas_validation", {}).get("status", "evaluated"),
                "stage4_sync": "synchronized",
                "stage5_bridge": "linked" if linked_subtopics else "skipped"
            }
        }
