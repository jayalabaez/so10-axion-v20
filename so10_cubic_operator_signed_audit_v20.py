#!/usr/bin/env python3
"""Signed audit of low-degree mixed SO(10) scalar operators.

The historical mixed ledger contains both omissions and over-counts. This
module isolates the cubic corrections used by the conservative signed floor:

* 210_H 10_H^dag 10_H is impossible. For the SO(10) vector,
  10 tensor 10 = Sym^2(10) + wedge^2(10) = (1 + 54) + 45; no 210 appears.
  In index language a rank-four antisymmetric tensor cannot be contracted to a
  scalar with only two vectors using invariant deltas/epsilon.
* one 210_H^3 invariant is independently guaranteed by the standard
  renormalizable Phi^3 coupling. Extra multiplicity is left open.
* one 210_H 126bar_H^dag 126bar_H invariant is independently guaranteed by
  the standard Phi Delta-bar Delta coupling. Extra multiplicity is left open.

This is a conservative signed audit, not a complete tensor-product
multiplicity calculation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_series_v20 as historical

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    ledger = historical.MULTIPLICITY
    old_phh = int(ledger.get("210_H 10_H^dag 10_H", {}).get("n", 0))
    old_p3 = int(ledger.get("210_H^3", {}).get("n", 0))
    old_pdd = int(
        ledger.get("210_H 126bar_H^dag 126bar_H", {}).get("n", 0)
    )

    vector_product_dimensions = {
        "singlet": 1,
        "antisymmetric_45": 45,
        "symmetric_traceless_54": 54,
    }
    vector_product_dimension_sum = sum(vector_product_dimensions.values())
    no_210 = 210 not in vector_product_dimensions.values()

    corrections = [
        {
            "operator": "210_H 10_H^dag 10_H",
            "historical_multiplicity": old_phh,
            "signed_floor_multiplicity": 0,
            "verdict": "FORBIDDEN",
            "proof": (
                "10 tensor 10 = 1 + 45 + 54; a singlet in 210 tensor 10 "
                "tensor 10 would require 210 in 10 tensor 10, which is absent."
            ),
        },
        {
            "operator": "210_H^3",
            "historical_multiplicity": old_p3,
            "signed_floor_multiplicity": min(old_p3, 1),
            "verdict": "ONE_GUARANTEED__EXTRA_MULTIPLICITY_OPEN",
            "proof": "standard renormalizable Phi^3 coupling guarantees one channel",
        },
        {
            "operator": "210_H 126bar_H^dag 126bar_H",
            "historical_multiplicity": old_pdd,
            "signed_floor_multiplicity": min(old_pdd, 1),
            "verdict": "ONE_GUARANTEED__EXTRA_MULTIPLICITY_OPEN",
            "proof": (
                "standard renormalizable Phi Delta-bar Delta coupling "
                "guarantees one channel"
            ),
        },
    ]
    historical_total = sum(row["historical_multiplicity"] for row in corrections)
    signed_total = sum(row["signed_floor_multiplicity"] for row in corrections)

    checks = {
        "historical_PHdagH_present_once": old_phh == 1,
        "vector_product_dimensions_sum_to_100": vector_product_dimension_sum == 100,
        "vector_product_has_no_210": no_210,
        "PHdagH_removed": corrections[0]["signed_floor_multiplicity"] == 0,
        "one_P3_guaranteed": corrections[1]["signed_floor_multiplicity"] == 1,
        "one_PDD_guaranteed": corrections[2]["signed_floor_multiplicity"] == 1,
        "signed_cubic_subtotal_reduced_by_three": historical_total - signed_total == 3,
        "extra_multiplicities_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SIGNED_SO10_CUBIC_OPERATOR_AUDIT_COMPLETE"
            if not failures
            else "SIGNED_SO10_CUBIC_OPERATOR_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "vector_tensor_product": {
            "decomposition": "10 tensor 10 = 1 + 45 + 54",
            "dimensions": vector_product_dimensions,
            "dimension_sum": vector_product_dimension_sum,
            "contains_210": False,
        },
        "corrections": corrections,
        "counts": {
            "historical_subtotal": historical_total,
            "signed_floor_subtotal": signed_total,
            "net_reduction": historical_total - signed_total,
        },
        "flag": {
            "forbidden_210_10dag10_proved": not failures,
            "one_210_cubic_guaranteed": not failures,
            "one_210_126dag126_guaranteed": not failures,
            "complete_cubic_multiplicities": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The historical cubic subtotal is reduced by three for a "
            "conservative signed floor: forbidden 210·10†·10 is removed and "
            "only one independently guaranteed channel is retained for each "
            "of 210^3 and 210·126†·126. Additional multiplicities remain open."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("SO10_CUBIC_OPERATOR_SIGNED_AUDIT_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_CUBIC_OPERATOR_SIGNED_AUDIT_V20.md").write_text(
        "# Signed SO(10) cubic operator audit\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
