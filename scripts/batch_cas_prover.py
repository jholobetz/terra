#!/usr/bin/env python3
"""
🔬 Terra Physics Lab - Database-Wide SymPy CAS Prover & Invariance Harness
Executes multi-core batch dimensional and algebraic invariance audits across
all 14,613 formulas in the 256 Git shards.
"""

import sys
import os
import json
import re
import time
import argparse
import warnings
from typing import Dict, Any, List, Optional, Tuple
from multiprocessing import Pool, cpu_count

# Suppress internal SymPy unit dimension deprecation warnings
warnings.filterwarnings("ignore", message=".*Using non-Expr arguments in Pow is deprecated.*")

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units import length, mass, time as sympy_time, current, temperature

from lib.cas.cas_engine import (
    STANDARD_PHYSICS_DIMENSIONS,
    latex_to_sympy_str,
    _extract_dim_powers,
    _format_dim_latex,
    _identify_physical_quantity
)
from lib.cas.unit_parser import parse_unit_string, get_dimension_signature


SHARDS_BASE_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")
DEFAULT_REPORT_PATH = os.path.join(PROJECT_ROOT, "app", "config", "cas_validation_report.json")


def clean_equation_for_cas(latex: str) -> str:
    """
    Strips non-algebraic annotations, conditional clauses, and conjunctions from raw equation strings.
    """
    s = latex.strip()

    # Strip display delimiters
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)

    # Strip trailing text clauses (e.g. \quad (\text{Fermi Energy}), \text{where } ...)
    s = re.sub(r"\\quad\s*\\text\{[^}]+\}", "", s)
    s = re.sub(r"\\quad\s*\([^)]*\)", "", s)
    s = re.sub(r"\\text\{where\s+[^}]+\}", "", s)
    s = re.sub(r"\\text\{for\s+[^}]+\}", "", s)

    # Handle conjunctions: if \iff or \implies is present, take the primary right-hand condition or main equality
    if r"\iff" in s:
        parts = s.split(r"\iff")
        # Prefer the part with more mathematical content / variables
        s = parts[1].strip() if "=" in parts[1] else parts[0].strip()
    elif r"\implies" in s:
        parts = s.split(r"\implies")
        s = parts[1].strip() if "=" in parts[1] else parts[0].strip()

    # Normalize relations for dimensional comparison
    # Any physical relation A \approx B or A \sim B or A \ge B implies dim(A) == dim(B)
    s = re.sub(r"\\approx|\\equiv|\\sim|\\propto|\\ge|\\le|\\geq|\\leq|>|<", "=", s)

    # Strip error margins: 2.73 \pm 0.02 -> 2.73
    s = re.sub(r"\\pm\s*[0-9]+(?:\.[0-9]+)?", "", s)

    # Normalize differentials and differences: \Delta S -> Delta_S, d\mathbf{x} -> dx
    s = re.sub(r"\\Delta\s*([a-zA-Z])", r"Delta_\1", s)
    s = re.sub(r"\\mathrm\{d\}\s*([a-zA-Z])", r"d\1", s)

    # Normalize common function notations: x(t) -> x, \mathbf{x}(t) -> x, a(t) -> a
    s = re.sub(r"([a-zA-Z])\s*\([t]\)", r"\1", s)

    # If multiple '=' exist (e.g. A = B = C), take first two: A = B
    if s.count("=") > 1:
        eq_parts = s.split("=")
        s = f"{eq_parts[0]} = {eq_parts[1]}"

    return s.strip()


def build_entry_dimensions(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a localized symbol-to-dimension map by prioritizing the formula's
    semantic_variables unit fields, falling back to STANDARD_PHYSICS_DIMENSIONS.
    """
    local_dims = dict(STANDARD_PHYSICS_DIMENSIONS)

    semantic_vars = entry.get("semantic_variables", {})
    if isinstance(semantic_vars, dict):
        for raw_sym, var_meta in semantic_vars.items():
            if isinstance(var_meta, dict):
                unit_str = var_meta.get("unit")
                if unit_str:
                    dim_expr = parse_unit_string(unit_str)
                    if dim_expr is not None:
                        clean_sym = latex_to_sympy_str(raw_sym).strip()
                        clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", clean_sym)
                        if clean_sym:
                            local_dims[clean_sym] = dim_expr

    return local_dims


def evaluate_formula_invariance(formula_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates dimensional homogeneity and algebraic consistency for a single formula.
    """
    raw_equation = entry.get("equation", "")
    if not raw_equation:
        return {
            "id": formula_id,
            "status": "NO_EQUATION",
            "is_homogeneous": False,
            "error": "Empty equation string"
        }

    clean_eq = clean_equation_for_cas(raw_equation)
    symbols_dict = build_entry_dimensions(entry)
    transformations = standard_transformations + (implicit_multiplication_application,)

    # Detect abstract / operator syntax that is structurally non-scalar
    if re.search(r"\\langle|\\rangle|\|[a-zA-Z0-9\s]+\\rangle|\\nabla\s*\\times|\\partial_\{\\mu\}", clean_eq):
        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "OPERATOR_OR_TENSOR",
            "is_homogeneous": None,
            "note": "Differential operator, tensor index, or bra-ket formulation"
        }

    try:
        if "=" in clean_eq:
            lhs_latex, rhs_latex = clean_eq.split("=", 1)
            lhs_str = latex_to_sympy_str(lhs_latex)
            rhs_str = latex_to_sympy_str(rhs_latex)

            if not lhs_str.strip() or not rhs_str.strip():
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": raw_equation,
                    "status": "PARSE_SKIPPED",
                    "is_homogeneous": False,
                    "error": "Empty LHS or RHS after sanitization"
                }

            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

            lhs_deps = dimsys_SI.get_dimensional_dependencies(lhs_expr)
            rhs_deps = dimsys_SI.get_dimensional_dependencies(rhs_expr)

            lhs_powers = _extract_dim_powers(lhs_deps)
            rhs_powers = _extract_dim_powers(rhs_deps)

            is_homo = (lhs_powers == rhs_powers)
            quantity = _identify_physical_quantity(lhs_powers)

            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "cleaned_equation": clean_eq,
                "status": "HOMOGENEOUS" if is_homo else "INHOMOGENEOUS",
                "is_homogeneous": is_homo,
                "quantity": quantity,
                "dimension_latex": _format_dim_latex(lhs_powers),
                "lhs_powers": lhs_powers,
                "rhs_powers": rhs_powers
            }
        else:
            # Single expression
            expr_str = latex_to_sympy_str(clean_eq)
            expr = parse_expr(expr_str, local_dict=symbols_dict, transformations=transformations)
            deps = dimsys_SI.get_dimensional_dependencies(expr)
            powers = _extract_dim_powers(deps)
            quantity = _identify_physical_quantity(powers)

            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "status": "DIMENSIONAL_EXPRESSION",
                "is_homogeneous": True,
                "quantity": quantity,
                "dimension_latex": _format_dim_latex(powers),
                "powers": powers
            }
    except Exception as e:
        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "PARSE_ERROR",
            "is_homogeneous": False,
            "error": str(e)
        }


def _worker_wrapper(item: Tuple[str, Dict[str, Any], str]) -> Tuple[Dict[str, Any], str]:
    warnings.filterwarnings("ignore")
    formula_id, entry, shard_path = item
    res = evaluate_formula_invariance(formula_id, entry)
    return res, shard_path


def load_shard_formulas(shard_hex: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple[str, Dict[str, Any], str]]:
    """
    Loads formula items from one or all 256 Git shards with their shard paths.
    """
    items = []
    shards_to_load = []

    if shard_hex:
        shards_to_load = [f"shard_{shard_hex.lower()}.json"]
    else:
        for i in range(256):
            h = f"{i:02x}"
            shards_to_load.append(f"shard_{h}.json")

    for shard_file in shards_to_load:
        shard_hex_code = shard_file.replace("shard_", "").replace(".json", "")
        shard_path = os.path.join(SHARDS_BASE_DIR, shard_hex_code, shard_file)
        if not os.path.exists(shard_path):
            continue

        try:
            with open(shard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for fid, entry in data.items():
                    items.append((fid, entry, shard_path))
                    if limit and len(items) >= limit:
                        return items
        except Exception as e:
            print(f"⚠️ Error reading {shard_path}: {e}", file=sys.stderr)

    return items


def run_batch_prover(
    shard_hex: Optional[str] = None,
    limit: Optional[int] = None,
    target_id: Optional[str] = None,
    num_workers: Optional[int] = None,
    report_path: Optional[str] = None,
    tag: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Executes the batch CAS invariance audit across formula shards, optionally tagging verified formulas.
    """
    start_time = time.time()

    if target_id:
        # Search for specific formula ID across shards
        items = []
        found = False
        for i in range(256):
            h = f"{i:02x}"
            p = os.path.join(SHARDS_BASE_DIR, h, f"shard_{h}.json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if target_id in d:
                        items = [(target_id, d[target_id], p)]
                        found = True
                        break
        if not found:
            print(f"❌ Formula ID '{target_id}' not found in any shard.", file=sys.stderr)
            return {"error": "Target ID not found"}
    else:
        items = load_shard_formulas(shard_hex=shard_hex, limit=limit)

    total_formulas = len(items)
    if total_formulas == 0:
        print("No formulas found matching criteria.", file=sys.stderr)
        return {}

    workers = num_workers or max(1, cpu_count() - 1)
    if total_formulas <= 5 or workers == 1:
        raw_results = [_worker_wrapper(item) for item in items]
    else:
        with Pool(processes=workers) as pool:
            raw_results = pool.map(_worker_wrapper, items)

    results = [r[0] for r in raw_results]

    elapsed_time = time.time() - start_time
    avg_latency_ms = (elapsed_time / total_formulas) * 1000 if total_formulas > 0 else 0

    # Aggregate Statistics
    status_counts: Dict[str, int] = {}
    quantity_counts: Dict[str, int] = {}
    homogeneous_count = 0

    for r in results:
        st = r.get("status", "UNKNOWN")
        status_counts[st] = status_counts.get(st, 0) + 1
        if r.get("is_homogeneous") is True:
            homogeneous_count += 1
        qty = r.get("quantity")
        if qty:
            quantity_counts[qty] = quantity_counts.get(qty, 0) + 1

    homogeneous_rate = (homogeneous_count / total_formulas * 100) if total_formulas > 0 else 0.0

    # Apply tagging to shards if requested
    tagged_count = 0
    if tag:
        shards_to_update: Dict[str, Dict[str, Any]] = {}
        for r, shard_path in raw_results:
            if r.get("is_homogeneous") is True and shard_path:
                fid = r.get("id")
                if fid:
                    if shard_path not in shards_to_update:
                        shards_to_update[shard_path] = {}
                    shards_to_update[shard_path][fid] = {
                        "status": r.get("status", "HOMOGENEOUS"),
                        "is_homogeneous": True,
                        "quantity": r.get("quantity"),
                        "dimension_latex": r.get("dimension_latex"),
                        "verified_at": int(time.time())
                    }
                    tagged_count += 1

        for s_path, updates in shards_to_update.items():
            try:
                with open(s_path, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                for fid, meta in updates.items():
                    if fid in s_data:
                        s_data[fid]["cas_validation"] = meta
                with open(s_path, "w", encoding="utf-8") as f:
                    json.dump(s_data, f, indent=4, ensure_ascii=False)
                    f.write("\n")
            except Exception as e:
                print(f"⚠️ Failed to tag shard {s_path}: {e}", file=sys.stderr)

    summary = {
        "metadata": {
            "timestamp": int(time.time()),
            "total_audited": total_formulas,
            "workers": workers,
            "elapsed_seconds": round(elapsed_time, 2),
            "avg_latency_ms": round(avg_latency_ms, 2),
            "homogeneous_count": homogeneous_count,
            "homogeneous_rate_pct": round(homogeneous_rate, 2),
            "tagged_count": tagged_count
        },
        "status_distribution": status_counts,
        "top_physical_quantities": dict(sorted(quantity_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "results": results if total_formulas <= 100 else results[:100]
    }

    # Save validation report (skip on single target query unless explicitly requested)
    if not target_id or report_path:
        out_path = report_path or DEFAULT_REPORT_PATH
        try:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            summary["report_file"] = out_path
        except Exception as e:
            if report_path:
                print(f"⚠️ Failed to write report to {out_path}: {e}", file=sys.stderr)

    return summary


def print_summary_scorecard(summary: Dict[str, Any]):
    """
    Prints a publication-grade CLI scorecard.
    """
    meta = summary.get("metadata", {})
    total = meta.get("total_audited", 0)
    homo = meta.get("homogeneous_count", 0)
    rate = meta.get("homogeneous_rate_pct", 0.0)
    elapsed = meta.get("elapsed_seconds", 0.0)
    lat = meta.get("avg_latency_ms", 0.0)

    print("\n" + "=" * 70)
    print("🔬 TERRA PHYSICS LAB - SYMPY CAS PROVER SCORECARD")
    print("=" * 70)
    print(f" Total Formulas Audited  : {total:,}")
    print(f" Homogeneous Certified   : {homo:,} ({rate:.1f}%)")
    tagged = meta.get("tagged_count", 0)
    if tagged > 0:
        print(f" Tagged into Git Shards  : {tagged:,}")
    print(f" Multi-core Throughput   : {elapsed:.2f}s total ({lat:.1f}ms / formula)")
    print("-" * 70)
    print(" Status Breakdown:")
    for st, count in summary.get("status_distribution", {}).items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"   • {st:22s}: {count:5d} ({pct:5.1f}%)")
    print("-" * 70)
    print(" Top Identified Physical Invariants:")
    for q, count in summary.get("top_physical_quantities", {}).items():
        print(f"   • {q:32s}: {count:4d}")
    print("=" * 70)
    if "report_file" in summary:
        print(f"📄 Validation report written to: {summary['report_file']}\n")


def main():
    parser = argparse.ArgumentParser(description="Terra Physics Lab - Database-Wide SymPy CAS Prover CLI")
    parser.add_argument("--all", action="store_true", help="Audit all 256 shards across the encyclopedia")
    parser.add_argument("--derivations", action="store_true", help="Audit all 102 multi-step derivation proofs sitewide")
    parser.add_argument("--tag", action="store_true", help="Tag verified formulas directly into shard files with cas_validation metadata")
    parser.add_argument("--shard", type=str, help="Specific formula shard hex (e.g. 00, 4f, ff)")
    parser.add_argument("--limit", type=int, help="Limit number of formulas to process")
    parser.add_argument("--target-id", type=str, help="Audit a single specific formula by ID")
    parser.add_argument("--workers", type=int, help="Number of worker processes")
    parser.add_argument("--report", type=str, help="Output JSON report file path")
    parser.add_argument("--summary", action="store_true", help="Print scorecard summary")
    parser.add_argument("--verbose", action="store_true", help="Print detailed formula outputs")

    args = parser.parse_args()

    if args.derivations:
        from lib.cas.derivation_prover import run_derivation_audit, print_derivation_scorecard
        d_summary = run_derivation_audit(report_path=args.report)
        print_derivation_scorecard(d_summary)
        return

    summary = run_batch_prover(
        shard_hex=args.shard,
        limit=args.limit,
        target_id=args.target_id,
        num_workers=args.workers,
        report_path=args.report,
        tag=args.tag,
        verbose=args.verbose
    )

    if args.summary or not args.target_id:
        print_summary_scorecard(summary)
    elif args.target_id and "results" in summary and summary["results"]:
        print(json.dumps(summary["results"][0], indent=2))


if __name__ == "__main__":
    main()
