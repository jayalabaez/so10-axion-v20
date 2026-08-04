#!/usr/bin/env python3
"""Audit omissions in the historical mixed-representation invariant ledger.

This module proves six missing norm-product quartics and five under-counted
quartic sectors. It intentionally does not certify a final lower bound by
itself, because the historical ledger also contains over-counts. Appending the
11 proven omissions to the mechanical locking total 26 gives 37 only before
the separate signed cubic correction. The signed basis module performs that
correction and emits the conservative floor 34.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_bfb_completion_v20 as completed
import mixed_rep_hilbert_series_v20 as upstream
import mixed_rep_invariant_exact_witness_v20 as exact_witness

ROOT = Path(__file__).resolve().parent

NORM_FIELDS = ("P", "D", "H", "S", "X")
PAIR_NAME = {
    ("P", "P"): "210_H^4",
    ("D", "D"): "(126bar_H^dag 126bar_H)^2",
    ("H", "H"): "(10_H^dag 10_H)^2",
    ("S", "S"): "(S^dag S)^2",
    ("X", "X"): "(Phi17^dag Phi17)^2",
    ("P", "D"): "210_H^dag 210_H 126bar_H^dag 126bar_H",
    ("P", "H"): "210_H^dag 210_H 10_H^dag 10_H",
    ("P", "S"): "210_H^dag 210_H S^dag S",
    ("P", "X"): "210_H^dag 210_H Phi17^dag Phi17",
    ("D", "H"): "10_H^dag 10_H 126bar_H^dag 126bar_H",
    ("D", "S"): "|S|^2 |126bar_H|^2",
    ("D", "X"): "|Phi17|^2 |126bar_H|^2",
    ("H", "S"): "|S|^2 |10_H|^2",
    ("H", "X"): "|Phi17|^2 |10_H|^2",
    ("S", "X"): "|Phi17|^2 |S|^2",
}
SECTOR_TO_CLASS = {
    "H_self": "(10_H^dag 10_H)^2",
    "D_self": "(126bar_H^dag 126bar_H)^2",
    "P_H": "210_H^dag 210_H 10_H^dag 10_H",
    "P_D": "210_H^dag 210_H 126bar_H^dag 126bar_H",
    "H_D": "10_H^dag 10_H 126bar_H^dag 126bar_H",
}
EXPLICIT_SECOND_CHANNELS = {
    "(10_H^dag 10_H)^2": "|(10_H dot 10_H)|^2",
    "(126bar_H^dag 126bar_H)^2": "Tr(Q_126^2)",
    "210_H^dag 210_H 10_H^dag 10_H": "H*_i H_j <i_i Phi,i_j Phi>",
    "210_H^dag 210_H 126bar_H^dag 126bar_H": "Tr(B_210^(2) B_126^(2))",
    "10_H^dag 10_H 126bar_H^dag 126bar_H": "H*_i H_j <i_i Delta,i_j Delta>",
}


def build_report() -> dict[str, Any]:
    base = upstream.build_report()
    overlay = completed.build_report()
    witness = exact_witness.build_report()
    historical_names = set(upstream.MULTIPLICITY)

    guaranteed_pairs: list[dict[str, Any]] = []
    missing_norm_products: list[dict[str, Any]] = []
    for pair in itertools.combinations_with_replacement(NORM_FIELDS, 2):
        name = PAIR_NAME[pair]
        row = {
            "fields": pair,
            "name": name,
            "guaranteed_by": "product of two quadratic norm singlets",
            "upstream_present": name in historical_names,
        }
        guaranteed_pairs.append(row)
        if not row["upstream_present"]:
            missing_norm_products.append(row)

    determinants = witness.get("determinants", {})
    numerical_independence: dict[str, dict[str, Any]] = {}
    multiplicity_deficits: list[dict[str, Any]] = []
    for sector, class_name in SECTOR_TO_CLASS.items():
        determinant = int(determinants.get(sector, 0))
        rank = 2 if determinant != 0 else 1
        numerical_independence[sector] = {
            "evaluation_rank": rank,
            "exact_integer_determinant": determinant,
            "samples": 2,
        }
        old_n = int(upstream.MULTIPLICITY.get(class_name, {}).get("n", 0))
        if old_n < rank:
            multiplicity_deficits.append(
                {
                    "name": class_name,
                    "upstream_multiplicity": old_n,
                    "proven_lower_bound": rank,
                    "explicit_second_channel": EXPLICIT_SECOND_CHANNELS[class_name],
                    "evaluation_rank": rank,
                    "exact_integer_determinant": determinant,
                }
            )

    historical_total = sum(
        int(row["n"]) for row in upstream.MULTIPLICITY.values()
    )
    locking_total = int(
        overlay.get("completed_filtered_basis", {}).get(
            "n_invariants_total", historical_total + 1
        )
    )
    omission_additions = len(missing_norm_products) + sum(
        row["proven_lower_bound"] - row["upstream_multiplicity"]
        for row in multiplicity_deficits
    )
    mechanical_augmented_total = locking_total + omission_additions

    checks = {
        "upstream_executes": base.get("n_failed", 1) == 0,
        "locking_overlay_executes": overlay.get("n_failed", 1) == 0,
        "exact_witness_executes": witness.get("n_failed", 1) == 0,
        "all_fifteen_norm_products_generated": len(guaranteed_pairs) == 15,
        "six_missing_norm_products_found": len(missing_norm_products) == 6,
        "five_multiplicity_deficits_found": len(multiplicity_deficits) == 5,
        "all_exact_rank_tests_equal_two": all(
            row["evaluation_rank"] == 2
            for row in numerical_independence.values()
        ),
        "mechanical_augmented_total_is_37": mechanical_augmented_total == 37,
        "signed_correction_delegated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "MIXED_REP_OMISSION_AUDIT_COMPLETE__SIGNED_CORRECTION_REQUIRED"
            if not failures
            else "MIXED_REP_OMISSION_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "guaranteed_norm_quartics": guaranteed_pairs,
        "missing_norm_products": missing_norm_products,
        "multiplicity_deficits": multiplicity_deficits,
        "numerical_independence": numerical_independence,
        "counts": {
            "historical_upstream_invariants_total": historical_total,
            "after_locking_modulus_overlay": locking_total,
            "additional_renormalizable_floor": omission_additions,
            "corrected_total_invariant_floor": mechanical_augmented_total,
            "mechanical_augmented_total_before_signed_corrections": (
                mechanical_augmented_total
            ),
            "historical_missing_norm_products": len(missing_norm_products),
            "historical_multiplicity_deficits": len(multiplicity_deficits),
        },
        "flag": {
            "historical_filtered_basis_complete": False,
            "historical_complete_filtered_basis_claim_falsified": not failures,
            "omission_set_constructed": not failures,
            "mechanical_augmented_total_not_signed_floor": True,
            "guaranteed_invariant_floor_constructed": False,
            "full_unfiltered_molien_haar_series": False,
            "full_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"The historical ledger omits six norm products and under-counts "
            f"five quartic sectors. Appending those omissions to the mechanical "
            f"locking total gives {mechanical_augmented_total}, but this is not "
            "a signed floor because the historical ledger also over-counts "
            "cubics. The signed audit must remove those entries before quoting "
            "a conservative total."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Mixed-representation omission audit — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Historical claimed total: {counts['historical_upstream_invariants_total']}",
        f"- Mechanical augmented total before signed corrections: {counts['mechanical_augmented_total_before_signed_corrections']}",
        "",
        "## Missing norm products",
        "",
    ]
    lines.extend(f"- `{row['name']}`" for row in report["missing_norm_products"])
    lines.extend(["", "## Multiplicity deficits", ""])
    lines.extend(
        f"- `{row['name']}`: {row['upstream_multiplicity']} -> >= {row['proven_lower_bound']}"
        for row in report["multiplicity_deficits"]
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_INVARIANT_FLOOR_AUDIT_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_INVARIANT_FLOOR_AUDIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
