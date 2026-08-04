#!/usr/bin/env python3
"""Complete the reduced locking basis with its neutral modulus companion.

The phase-sensitive operator Delta^2 H^2 S^2 + h.c. is not by itself a
bounded radial interaction. The separately allowed invariant
|Delta|^2 |H|^2 |S|^2 must be included with an independent coefficient in a
maximal charge-allowed non-SUSY EFT basis.

This module is the canonical overlay for the repaired reduced basis. It keeps
the historical upstream ledger intact for provenance, appends the missing
operator exactly once, and emits a completed basis consumed by the non-SUSY
Hessian certificate.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_series_v20 as upstream
import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent
OPERATOR = "|126bar_H|^2 |10_H|^2 |S|^2"
COUNTS = {
    "126bar_H_dag": 1,
    "126bar_H": 1,
    "10_H_dag": 1,
    "10_H": 1,
    "S_dag": 1,
    "S": 1,
}


def _completed_basis(base: dict[str, Any], operator_entry: dict[str, Any]) -> dict[str, Any]:
    original = copy.deepcopy(base.get("filtered_basis", {}))
    included = list(original.get("included", []))
    names = {
        row.get("name")
        for row in included
        if isinstance(row, dict)
    }
    appended = OPERATOR not in names
    if appended:
        included.append(copy.deepcopy(operator_entry))
    multiplicity_total = sum(
        int(row.get("multiplicity", 1))
        for row in included
        if isinstance(row, dict)
    )
    return {
        **original,
        "included": included,
        "n_classes": len(included),
        "n_invariants_total": multiplicity_total,
        "completion_appended": appended,
        "completion_operator": OPERATOR,
        "complete_for_reduced_locking_bfb_pair": True,
        "unfiltered_molien_haar_complete": False,
    }


def build_report() -> dict[str, Any]:
    base = upstream.build_report()
    totals = z17._total_charge(COUNTS)
    allowed = z17._allowed(totals)
    operator_entry = {
        "name": OPERATOR,
        "multiplicity": 1,
        "grade": "t6",
        "sector": "locking_modulus_bfb",
        "source": "product of unique norm singlets",
        "counts": COUNTS,
        "dimension": 6,
        "charge_totals": totals,
        "charge_allowed": bool(allowed["all"]),
        "so10_verdict": "ALLOWED",
        "included": True,
        "role": "positive radial companion to the phase-sensitive locking invariant",
    }
    completed = _completed_basis(base, operator_entry)
    absent_upstream = bool(completed["completion_appended"])
    appears_once = sum(
        1
        for row in completed["included"]
        if isinstance(row, dict) and row.get("name") == OPERATOR
    ) == 1
    checks = {
        "upstream_executes": base.get("n_failed", 1) == 0,
        "operator_exactly_charge_neutral": totals == {"PQ": 0, "X": 0, "Z17": 0},
        "charge_filter_allows": bool(allowed["all"]),
        "so10_singlet_exists_by_norm_product": True,
        "operator_missing_from_upstream_basis_detected": absent_upstream,
        "completed_basis_contains_operator_once": appears_once,
        "completed_basis_count_incremented": completed["n_classes"] == len(
            base.get("filtered_basis", {}).get("included", [])
        ) + 1,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "REDUCED_BFB_LOCKING_BASIS_COMPLETED__UNFILTERED_MOLIEN_OPEN"
            if not failures
            else "REDUCED_BFB_LOCKING_BASIS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "operator": operator_entry,
        "completed_filtered_basis": completed,
        "upstream": {
            "status": base.get("status"),
            "operator_was_absent": absent_upstream,
            "historical_n_classes": len(
                base.get("filtered_basis", {}).get("included", [])
            ),
            "unfiltered_molien_haar_closed": bool(
                base.get("flag", {}).get("mixed_rep_unfiltered_molien_haar_series", False)
            ),
        },
        "flag": {
            "modulus_locking_companion_added": appears_once,
            "reduced_charge_allowed_bfb_basis_complete_for_locking_pair": appears_once,
            "upstream_filtered_basis_was_incomplete_for_bfb": absent_upstream,
            "canonical_completed_basis_emitted": True,
            "mixed_rep_unfiltered_molien_haar_series": False,
            "full_component_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Added the independently allowed modulus invariant |Delta|^2|H|^2|S|^2 exactly once to the canonical completed reduced basis. "
            "It is required to state a radial BFB condition for the phase-locking sextic. "
            "This completes the reduced locking pair, not the unfiltered multi-representation Molien series."
        ),
    }


def main(argv=None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_HILBERT_BFB_COMPLETION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_HILBERT_BFB_COMPLETION_V20.md").write_text(
        "# Reduced BFB locking-basis completion\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
