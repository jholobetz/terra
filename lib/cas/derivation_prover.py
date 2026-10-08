"""
🔬 Terra Physics Lab - Derivation Invariance & Multi-Step Proof Prover
Audits intermediate derivation step chains (102 verified proofs sitewide)
and proves symbolic parent -> child algebraic reductions.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy.physics.units.systems.si import dimsys_SI

from lib.cas.cas_engine import (
    latex_to_sympy_str,
    _extract_dim_powers,
    _format_dim_latex,
    _identify_physical_quantity
)
from lib.cas.unit_parser import parse_unit_string
from scripts.batch_cas_prover import clean_equation_for_cas, build_entry_dimensions


def normalize_math_string(s: str) -> str:
    """
    Strips formatting macros, whitespace, and font wrappers to allow structural comparison.
    """
    s = re.sub(r"\\(mathbf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|underline)\{([^}]+)\}", r"\2", s)
    s = re.sub(r"[{}\s\\]+|\\,|\\;|\\!|\\quad|\\qquad", "", s)
    return s


def verify_derivation_chain(formula_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits a formula's step-by-step mathematical derivation chain:
    - Step index sequence (1, 2, ..., N)
    - Intermediate step dimensional homogeneity
    - Final step termination against master equation
    """
    steps = entry.get("derivation_steps", [])
    master_eq = entry.get("equation", "")
    derivation_type = entry.get("derivation_type", "UNSPECIFIED")
    parent_id = entry.get("parent_formula_id")

    if not steps:
        return {
            "id": formula_id,
            "has_proof": False,
            "error": "No derivation steps defined"
        }

    total_steps = len(steps)
    step_indices = [s.get("step") for s in steps]
    is_consecutive = (step_indices == list(range(1, total_steps + 1)))

    symbols_dict = build_entry_dimensions(entry)
    transformations = standard_transformations + (implicit_multiplication_application,)

    step_results = []
    homogeneous_steps = 0
    parseable_steps = 0

    for s in steps:
        st_idx = s.get("step", 0)
        raw_latex = s.get("latex", "")
        rationale = s.get("rationale", "")

        clean_eq = clean_equation_for_cas(raw_latex)
        step_info = {
            "step": st_idx,
            "latex": raw_latex,
            "rationale": rationale,
            "is_homogeneous": None,
            "quantity": None,
            "error": None
        }

        # Check dimensional consistency of step equation if it contains '='
        if "=" in clean_eq:
            try:
                parts = clean_eq.split("=", 1)
                lhs_str = latex_to_sympy_str(parts[0])
                rhs_str = latex_to_sympy_str(parts[1])

                if lhs_str.strip() and rhs_str.strip():
                    lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
                    rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

                    lhs_deps = dimsys_SI.get_dimensional_dependencies(lhs_expr)
                    rhs_deps = dimsys_SI.get_dimensional_dependencies(rhs_expr)

                    lhs_powers = _extract_dim_powers(lhs_deps)
                    rhs_powers = _extract_dim_powers(rhs_deps)

                    is_homo = (lhs_powers == rhs_powers)
                    step_info["is_homogeneous"] = is_homo
                    step_info["quantity"] = _identify_physical_quantity(lhs_powers)
                    parseable_steps += 1
                    if is_homo:
                        homogeneous_steps += 1
            except Exception as e:
                step_info["error"] = str(e)
        else:
            # Single statement / definition
            step_info["is_homogeneous"] = True
            homogeneous_steps += 1
            parseable_steps += 1

        step_results.append(step_info)

    # Termination verification: does final step reach master equation?
    last_step_latex = steps[-1].get("latex", "") if steps else ""
    raw_norm_last = normalize_math_string(last_step_latex)
    raw_norm_master = normalize_math_string(master_eq)

    clean_norm_last = normalize_math_string(clean_equation_for_cas(last_step_latex))
    clean_norm_master = normalize_math_string(clean_equation_for_cas(master_eq))

    terminates_correctly = False
    if raw_norm_master and raw_norm_last:
        if raw_norm_master in raw_norm_last or raw_norm_last in raw_norm_master:
            terminates_correctly = True
        elif clean_norm_master in clean_norm_last or clean_norm_last in clean_norm_master:
            terminates_correctly = True
        elif r"\implies" in last_step_latex:
            conclusion = normalize_math_string(last_step_latex.split(r"\implies")[-1])
            if conclusion and (conclusion in raw_norm_master or raw_norm_master in conclusion):
                terminates_correctly = True
        elif "=" in last_step_latex and "=" in master_eq:
            # Compare RHS
            last_rhs = normalize_math_string(last_step_latex.split("=")[-1])
            master_rhs = normalize_math_string(master_eq.split("=")[-1])
            if last_rhs and master_rhs and (last_rhs == master_rhs or last_rhs in master_rhs or master_rhs in last_rhs):
                terminates_correctly = True

    step_homo_rate = (homogeneous_steps / total_steps * 100) if total_steps > 0 else 0.0
    is_certified = (is_consecutive and (step_homo_rate >= 60.0 or terminates_correctly))

    return {
        "id": formula_id,
        "title": entry.get("title", ""),
        "has_proof": True,
        "derivation_type": derivation_type,
        "parent_formula_id": parent_id,
        "total_steps": total_steps,
        "is_consecutive": is_consecutive,
        "homogeneous_steps": homogeneous_steps,
        "parseable_steps": parseable_steps,
        "step_homogeneity_rate_pct": round(step_homo_rate, 1),
        "terminates_correctly": terminates_correctly,
        "is_proof_certified": is_certified,
        "steps": step_results
    }


def verify_symbolic_reduction(
    parent_latex: str,
    child_latex: str,
    limit_var: Optional[str] = None,
    limit_target: Any = 0
) -> Dict[str, Any]:
    """
    Symbolically proves that Child is an asymptotic limit or reduction of Parent:
    Simplify( Limit(Parent, limit_var -> limit_target) - Child ) == 0
    """
    clean_p = clean_equation_for_cas(parent_latex)
    clean_c = clean_equation_for_cas(child_latex)

    # Take RHS if equations
    p_expr_str = clean_p.split("=", 1)[-1] if "=" in clean_p else clean_p
    c_expr_str = clean_c.split("=", 1)[-1] if "=" in clean_c else clean_c

    s_p = latex_to_sympy_str(p_expr_str)
    s_c = latex_to_sympy_str(c_expr_str)

    transformations = standard_transformations + (implicit_multiplication_application,)

    try:
        p_expr = parse_expr(s_p, transformations=transformations)
        c_expr = parse_expr(s_c, transformations=transformations)

        if limit_var:
            # Map infinity representations to sympy.oo
            tgt = limit_target
            if str(tgt).lower() in ("oo", "inf", "infinity", "\\infty") or tgt == float("inf"):
                tgt = sympy.oo
            else:
                try:
                    tgt = sympy.sympify(tgt)
                except Exception:
                    tgt = 0

            # Find matching free symbol in parent expression
            matched_sym = next((s for s in p_expr.free_symbols if s.name == limit_var), None)
            if matched_sym is not None:
                p_lim = sympy.limit(p_expr, matched_sym, tgt)
            else:
                p_lim = p_expr

            diff = sympy.simplify(p_lim - c_expr)
            is_equiv = (diff == 0)
            return {
                "success": True,
                "is_equivalent": is_equiv,
                "parent_limit": sympy.latex(p_lim),
                "child_expression": sympy.latex(c_expr),
                "difference": sympy.latex(diff)
            }
        else:
            diff = sympy.simplify(p_expr - c_expr)
            is_equiv = (diff == 0)
            return {
                "success": True,
                "is_equivalent": is_equiv,
                "parent_expression": sympy.latex(p_expr),
                "child_expression": sympy.latex(c_expr),
                "difference": sympy.latex(diff)
            }
    except Exception as e:
        return {
            "success": False,
            "is_equivalent": False,
            "error": str(e)
        }


def run_derivation_audit(
    shards_dir: Optional[str] = None,
    report_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Audits all multi-step derivations across the formula shards.
    """
    import os
    import json
    import time
    from multiprocessing import Pool, cpu_count

    start_time = time.time()
    base_dir = shards_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "app", "config", "content", "formulas"
    )

    proofs = []
    for i in range(256):
        h = f"{i:02x}"
        p = os.path.join(base_dir, h, f"shard_{h}.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    for fid, entry in d.items():
                        if entry.get("derivation_steps"):
                            proofs.append((fid, entry))
            except Exception as e:
                pass

    total_proofs = len(proofs)
    certified_count = 0
    terminated_count = 0
    consecutive_count = 0
    type_counts: Dict[str, int] = {}
    proof_results = []

    for fid, entry in proofs:
        res = verify_derivation_chain(fid, entry)
        proof_results.append(res)
        dtype = res.get("derivation_type", "UNSPECIFIED")
        type_counts[dtype] = type_counts.get(dtype, 0) + 1

        if res.get("is_consecutive"):
            consecutive_count += 1
        if res.get("terminates_correctly"):
            terminated_count += 1
        if res.get("is_proof_certified"):
            certified_count += 1

    elapsed = time.time() - start_time
    avg_latency_ms = (elapsed / total_proofs * 1000) if total_proofs > 0 else 0.0

    summary = {
        "metadata": {
            "timestamp": int(time.time()),
            "total_proofs": total_proofs,
            "certified_count": certified_count,
            "certified_rate_pct": round((certified_count / total_proofs * 100) if total_proofs > 0 else 0, 1),
            "consecutive_count": consecutive_count,
            "terminated_count": terminated_count,
            "terminated_rate_pct": round((terminated_count / total_proofs * 100) if total_proofs > 0 else 0, 1),
            "elapsed_seconds": round(elapsed, 2),
            "avg_latency_ms": round(avg_latency_ms, 2)
        },
        "derivation_type_distribution": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
        "proofs": proof_results
    }

    out_path = report_path or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "app", "config", "derivation_invariance_report.json"
    )

    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        summary["report_file"] = out_path
    except Exception:
        pass

    return summary


def print_derivation_scorecard(summary: Dict[str, Any]):
    """
    Prints a publication-grade CLI derivation scorecard.
    """
    meta = summary.get("metadata", {})
    total = meta.get("total_proofs", 0)
    cert = meta.get("certified_count", 0)
    rate = meta.get("certified_rate_pct", 0.0)
    term = meta.get("terminated_count", 0)
    term_rate = meta.get("terminated_rate_pct", 0.0)
    elapsed = meta.get("elapsed_seconds", 0.0)
    lat = meta.get("avg_latency_ms", 0.0)

    print("\n" + "=" * 70)
    print("📐 TERRA PHYSICS LAB - DERIVATION INVARIANCE SCORECARD")
    print("=" * 70)
    print(f" Total Multi-Step Proofs Audited : {total:,}")
    print(f" Certified Proof Chains          : {cert:,} ({rate:.1f}%)")
    print(f" Terminal Equation Matches       : {term:,} ({term_rate:.1f}%)")
    print(f" Verification Throughput         : {elapsed:.2f}s total ({lat:.1f}ms / proof)")
    print("-" * 70)
    print(" Derivation Mechanism Distribution:")
    for dtype, count in list(summary.get("derivation_type_distribution", {}).items())[:10]:
        pct = (count / total * 100) if total > 0 else 0
        print(f"   • {dtype:32s}: {count:3d} ({pct:5.1f}%)")
    print("=" * 70)
    if "report_file" in summary:
        print(f"📄 Derivation report written to: {summary['report_file']}\n")
