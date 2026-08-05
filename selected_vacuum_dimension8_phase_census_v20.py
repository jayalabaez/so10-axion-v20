#!/usr/bin/env python3
"""Dimension-eight phase-sensitive operator census for the selected vacuum.

The selected-vacuum phase-lifting search is closed through dimension seven.
Before evaluating dimension-eight contractions, this module performs an exact
charge/tensor census and computes the number of pairwise metric-contraction
multigraphs with a memoized count-only recurrence.  It therefore ranks the
next finite workloads without materializing potentially large graph lists.

No coefficient is evaluated here.  The output is a workload and provenance
contract for subsequent exact tensor waves, not a phase-lifting claim.
"""
from __future__ import annotations

import argparse
import functools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIMENSION8_PHASE_CENSUS_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIMENSION8_PHASE_CENSUS_V20.md"


def bounded_compositions(total: int, bounds: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    if not bounds:
        if total == 0:
            yield ()
        return
    first, rest = bounds[0], bounds[1:]
    for value in range(min(first, total) + 1):
        for tail in bounded_compositions(total - value, rest):
            yield (value,) + tail


@functools.lru_cache(maxsize=None)
def count_pairwise_multigraphs(degrees: tuple[int, ...]) -> int:
    """Count loop-free labeled multigraphs with the requested vertex degrees.

    Sorting is a memoization canonicalization only; the count depends on the
    degree multiset and is invariant under relabeling of vertices.
    """
    state = tuple(sorted((int(d) for d in degrees if d), reverse=True))
    if not state:
        return 1
    if sum(state) % 2:
        return 0
    first, rest = state[0], state[1:]
    if first > sum(rest):
        return 0
    total = 0
    for edges in bounded_compositions(first, rest):
        reduced = tuple(rest[i] - edges[i] for i in range(len(rest)))
        if min(reduced, default=0) < 0:
            continue
        total += count_pairwise_multigraphs(reduced)
    return total


def canonical_representatives(dimension: int) -> tuple[
    list[dict[str, Any]],
    set[metric.TensorSignature],
    set[metric.TensorSignature],
    list[metric.TensorSignature],
    defaultdict[metric.TensorSignature, list[dict[str, Any]]],
]:
    candidates = dim7.exact_dimension_candidates(dimension)
    signatures = {
        metric.tensor_signature(row["counts"]) for row in candidates
    }
    odd_h = {
        signature
        for signature in signatures
        if (signature[3] + signature[4]) % 2 == 1
    }
    even_h = signatures.difference(odd_h)
    representatives = sorted(
        {metric.canonical_signature(signature) for signature in even_h}
    )
    candidate_map: defaultdict[metric.TensorSignature, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        canonical = tuple(row["canonical_signature"])
        if canonical in representatives:
            candidate_map[canonical].append(row)
    return candidates, signatures, odd_h, representatives, candidate_map


def prior_representatives(max_dimension: int = 7) -> set[metric.TensorSignature]:
    out: set[metric.TensorSignature] = set()
    for dimension in range(1, max_dimension + 1):
        for row in dim7.exact_dimension_candidates(dimension):
            signature = metric.tensor_signature(row["counts"])
            if (signature[3] + signature[4]) % 2 == 0:
                out.add(metric.canonical_signature(signature))
    return out


def norm_reduction_targets(signature: metric.TensorSignature) -> list[dict[str, Any]]:
    p, d, db, h, hb = signature
    reductions: list[dict[str, Any]] = []
    for name, reduced in (
        ("Phi210_norm_pair", (p - 2, d, db, h, hb)),
        ("Delta_norm_pair", (p, d - 1, db - 1, h, hb)),
        ("H10_norm_pair", (p, d, db, h - 1, hb - 1)),
    ):
        if min(reduced) < 0:
            continue
        reductions.append(
            {
                "factor": name,
                "reduced_signature": list(
                    metric.canonical_signature(reduced)
                ),
            }
        )
    return reductions


def build_report() -> dict[str, Any]:
    candidates, signatures, odd_h, representatives, candidate_map = canonical_representatives(8)
    prior = prior_representatives(7)

    rows: list[dict[str, Any]] = []
    for signature in representatives:
        degrees = tuple(metric.tensor_degrees(signature))
        graph_count = count_pairwise_multigraphs(degrees)
        assignments = 2 ** (signature[3] + signature[4])
        cost = graph_count * assignments
        reductions = norm_reduction_targets(signature)
        rows.append(
            {
                "signature_P_D_Db_H_Hb": list(signature),
                "tensor_degrees": list(degrees),
                "n_metric_graphs": graph_count,
                "n_neutral_H_assignments": assignments,
                "planned_graph_coefficient_evaluations": cost,
                "canonical_signature_seen_through_dimension7": signature in prior,
                "norm_pair_reduction_targets": reductions,
                "dimension8_monomials": candidate_map[signature],
            }
        )
    rows.sort(
        key=lambda row: (
            row["planned_graph_coefficient_evaluations"],
            row["signature_P_D_Db_H_Hb"],
        )
    )

    new_rows = [
        row
        for row in rows
        if not row["canonical_signature_seen_through_dimension7"]
    ]
    reused_rows = [
        row
        for row in rows
        if row["canonical_signature_seen_through_dimension7"]
    ]
    low_cost = [
        row
        for row in new_rows
        if row["planned_graph_coefficient_evaluations"] <= 20000
    ]

    all_charge_allowed = all(
        row["charge_allowed"]["all"] for row in candidates
    )
    all_exact_dimension = all(
        sum(row["counts"].values()) == 8 for row in candidates
    )
    all_have_126 = all(
        row["counts"]["D"] + row["counts"]["Db"] > 0
        for row in candidates
    )
    calibration = {
        "dim7_signature_4_0_2_0_0": count_pairwise_multigraphs(
            tuple(metric.tensor_degrees((4, 0, 2, 0, 0)))
        ),
        "dim7_signature_0_2_4_0_0": count_pairwise_multigraphs(
            tuple(metric.tensor_degrees((0, 2, 4, 0, 0)))
        ),
        "dim7_signature_3_0_2_2_0": count_pairwise_multigraphs(
            tuple(metric.tensor_degrees((3, 0, 2, 2, 0)))
        ),
    }
    checks = {
        "all_dimension8_candidates_charge_allowed": all_charge_allowed,
        "all_candidates_have_exact_dimension8": all_exact_dimension,
        "all_candidates_contain_126_five_form": all_have_126,
        "every_even_signature_has_candidate_rows": all(
            candidate_map[signature] for signature in representatives
        ),
        "count_only_calibration_4691": calibration[
            "dim7_signature_4_0_2_0_0"
        ]
        == 4691,
        "count_only_calibration_12043": calibration[
            "dim7_signature_0_2_4_0_0"
        ]
        == 12043,
        "count_only_calibration_3387": calibration[
            "dim7_signature_3_0_2_2_0"
        ]
        == 3387,
        "all_graph_counts_positive": all(row["n_metric_graphs"] > 0 for row in rows),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    status = (
        "DIMENSION8_PHASE_CENSUS_COMPLETE__COEFFICIENT_SCREEN_OPEN"
        if not failures
        else "DIMENSION8_PHASE_CENSUS_FAILED"
    )
    return {
        "status": status,
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "calibration": calibration,
        "counts": {
            "dimension8_charge_allowed_phase_sensitive_monomials": len(candidates),
            "dimension8_tensor_signatures": len(signatures),
            "dimension8_odd_H_signatures_removed": len(odd_h),
            "dimension8_even_H_conjugacy_representatives": len(representatives),
            "representatives_seen_through_dimension7": len(reused_rows),
            "genuinely_new_representatives": len(new_rows),
            "new_representatives_at_or_below_20000_evaluations": len(low_cost),
        },
        "ranked_even_H_representatives": rows,
        "ranked_genuinely_new_representatives": new_rows,
        "first_exact_wave_candidates": low_cost,
        "flags": {
            "dimension7_no_go_consumed_as_upstream_boundary": True,
            "dimension8_charge_tensor_census_complete": not bool(failures),
            "dimension8_coefficients_evaluated": False,
            "dimension8_phase_lifting_no_go_proven": False,
            "nonzero_dimension8_channel_found": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Execute the lowest-cost genuinely new dimension-eight representatives "
            "in parallel using the exact neutral-H coefficient evaluator."
        ),
        "verdict": (
            "Dimension-eight charge and tensor signatures are enumerated and ranked "
            "without materializing the contraction graphs. No dimension-eight "
            "coefficient has yet been evaluated."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    OUT_MD.write_text(
        "# Selected-vacuum dimension-eight phase census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Charge-allowed monomials: `{counts['dimension8_charge_allowed_phase_sensitive_monomials']}`\n"
        f"- Even-H representatives: `{counts['dimension8_even_H_conjugacy_representatives']}`\n"
        f"- Genuinely new representatives: `{counts['genuinely_new_representatives']}`\n"
        f"- First-wave candidates <=20,000 evaluations: `{counts['new_representatives_at_or_below_20000_evaluations']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
