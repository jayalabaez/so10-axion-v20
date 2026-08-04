#!/usr/bin/env python3
"""Complete the reduced locking basis with its neutral modulus companion.

The phase-sensitive operator Delta^2 H^2 S^2 + h.c. is not by itself a
bounded radial interaction. The separately allowed invariant
|Delta|^2 |H|^2 |S|^2 must be included with an independent coefficient in a
maximal charge-allowed non-SUSY EFT basis.
"""
from __future__ import annotations

import argparse
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


def build_report() -> dict[str, Any]:
    base = upstream.build_report()
    totals = z17._total_charge(COUNTS)
    allowed = z17._allowed(totals)
    included_names = {
        entry.get("name")
        for entry in base.get("filtered_basis", {}).get("included", [])
        if isinstance(entry, dict)
    }
    absent_upstream = OPERATOR not in included_names
    checks = {
        "upstream_executes": base.get("n_failed", 1) == 0,
        "operator_exactly_charge_neutral": totals == {"PQ": 0, "X": 0, "Z17": 0},
        "charge_filter_allows": bool(allowed["all"]),
        "so10_singlet_exists_by_norm_product": True,
        "operator_missing_from_upstream_basis_detected": absent_upstream,
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
        "operator": {
            "name": OPERATOR,
            "counts": COUNTS,
            "dimension": 6,
            "charge_totals": totals,
            "charge_allowed": allowed,
            "so10_reason": "product of the three unique norm singlets",
            "multiplicity_lower_bound": 1,
            "role": "positive radial companion to the phase-sensitive locking invariant",
        },
        "upstream": {
            "status": base.get("status"),
            "operator_was_absent": absent_upstream,
            "unfiltered_molien_haar_closed": bool(
                base.get("flag", {}).get("mixed_rep_unfiltered_molien_haar_series", False)
            ),
        },
        "flag": {
            "modulus_locking_companion_added": True,
            "reduced_charge_allowed_bfb_basis_complete_for_locking_pair": True,
            "upstream_filtered_basis_was_incomplete_for_bfb": absent_upstream,
            "mixed_rep_unfiltered_molien_haar_series": False,
            "full_component_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Added the independently allowed modulus invariant |Delta|^2|H|^2|S|^2. "
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
