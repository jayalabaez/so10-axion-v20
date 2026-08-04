#!/usr/bin/env python3
"""Emit a signed guaranteed mixed-representation invariant floor.

The earlier 37 count mechanically appended proven omissions to a historical
25-entry ledger.  A signed audit shows that the historical ledger also
contains an impossible cubic and unsupported excess multiplicities:

* ``210_H 10_H^dag 10_H`` is forbidden because
  ``10 tensor 10 = 1 + 45 + 54`` contains no 210.  Equivalently, a rank-four
  antisymmetric tensor cannot be contracted to a scalar with only two vector
  fields using SO(10) deltas or epsilon.
* one ``210_H^3`` channel is guaranteed; the second historical channel is not
  counted in a conservative floor until independently established;
* one ``210_H 126bar_H^dag 126bar_H`` channel is guaranteed by the standard
  Phi Delta-bar Delta coupling; the second historical channel is likewise
  left open rather than counted.

After these signed corrections, the locking modulus companion, six guaranteed
norm products, and five exact second-channel witnesses give a defensible floor
of 34.  Additional channels may raise this number.  This is not a complete
Molien/Haar enumeration.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_bfb_completion_v20 as completion
import mixed_rep_invariant_exact_witness_v20 as exact_witness
import mixed_rep_invariant_floor_audit_v20 as omission_audit

ROOT = Path(__file__).resolve().parent

FORBIDDEN_HISTORICAL = {
    "210_H 10_H^dag 10_H": (
        "FORBIDDEN: 10 tensor 10 = 1 + 45 + 54 contains no 210; "
        "no SO(10) scalar can be formed from one four-form and two vectors"
    )
}
CONSERVATIVE_MULTIPLICITY = {
    "210_H^3": 1,
    "210_H 126bar_H^dag 126bar_H": 1,
}


def _norm_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": row["name"],
        "multiplicity": 1,
        "dimension": 4,
        "grade": "t4",
        "sector": "guaranteed_missing_norm_product",
        "source": "product of quadratic SO(10) norm singlets",
        "independence": "algebraic by distinct field multi-degree",
        "included": True,
    }


def _channel_entry(row: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "name": f"{row['name']} :: independent_channel_2",
        "parent_class": row["name"],
        "multiplicity": 1,
        "dimension": 4,
        "grade": "t4",
        "sector": "guaranteed_additional_tensor_channel",
        "source": row.get("explicit_second_channel"),
        "independence": (
            "exact nonzero 2x2 Gaussian-integer evaluation determinant "
            f"witness #{index + 1}"
        ),
        "included": True,
    }


def _signed_historical_basis(
    historical: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    signed: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    for original in historical:
        row = copy.deepcopy(original)
        name = row.get("name")
        old_n = int(row.get("multiplicity", 1))
        if name in FORBIDDEN_HISTORICAL:
            corrections.append(
                {
                    "name": name,
                    "historical_multiplicity": old_n,
                    "signed_floor_multiplicity": 0,
                    "reason": FORBIDDEN_HISTORICAL[name],
                }
            )
            continue
        if name in CONSERVATIVE_MULTIPLICITY:
            new_n = min(old_n, CONSERVATIVE_MULTIPLICITY[name])
            if new_n != old_n:
                corrections.append(
                    {
                        "name": name,
                        "historical_multiplicity": old_n,
                        "signed_floor_multiplicity": new_n,
                        "reason": (
                            "Only one channel is independently guaranteed by the "
                            "standard complete renormalizable coupling catalogue; "
                            "any additional multiplicity remains open."
                        ),
                    }
                )
            row["multiplicity"] = new_n
            row["signed_floor_conservative"] = True
        signed.append(row)
    return signed, corrections


def build_report() -> dict[str, Any]:
    base = completion.build_report()
    audit = omission_audit.build_report()
    witness = exact_witness.build_report()

    execution_failures: list[str] = []
    for label, report in (
        ("locking_completion", base),
        ("omission_audit", audit),
        ("exact_witness", witness),
    ):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(label)

    mechanical = copy.deepcopy(
        base.get("completed_filtered_basis", {}).get("included", [])
    )
    signed, corrections = _signed_historical_basis(mechanical)
    proposed: list[dict[str, Any]] = []
    proposed.extend(
        _norm_entry(row) for row in audit.get("missing_norm_products", [])
    )
    proposed.extend(
        _channel_entry(row, index)
        for index, row in enumerate(audit.get("multiplicity_deficits", []))
    )

    existing = {row.get("name") for row in signed if isinstance(row, dict)}
    appended: list[dict[str, Any]] = []
    for row in proposed:
        if row["name"] in existing:
            continue
        signed.append(copy.deepcopy(row))
        appended.append(copy.deepcopy(row))
        existing.add(row["name"])

    mechanical_base_total = int(
        base.get("completed_filtered_basis", {}).get("n_invariants_total", 0)
    )
    signed_base_total = sum(
        int(row.get("multiplicity", 1)) for row in signed if row not in appended
    )
    appended_total = sum(int(row.get("multiplicity", 1)) for row in appended)
    signed_total = signed_base_total + appended_total
    mechanical_augmented_total = mechanical_base_total + appended_total
    n_norm = sum(
        row["sector"] == "guaranteed_missing_norm_product" for row in appended
    )
    n_channels = sum(
        row["sector"] == "guaranteed_additional_tensor_channel"
        for row in appended
    )

    checks = {
        "upstreams_execute": not execution_failures,
        "mechanical_locking_completion_total_is_26": mechanical_base_total == 26,
        "forbidden_210_10dag10_removed": any(
            row["name"] == "210_H 10_H^dag 10_H"
            and row["signed_floor_multiplicity"] == 0
            for row in corrections
        ),
        "two_excess_multiplicities_conservatively_reduced": sum(
            row["historical_multiplicity"] > row["signed_floor_multiplicity"] > 0
            for row in corrections
        )
        == 2,
        "signed_base_total_is_23": signed_base_total == 23,
        "six_norm_products_appended": n_norm == 6,
        "five_tensor_channels_appended": n_channels == 5,
        "exact_witnesses_nonzero": bool(
            witness.get("flag", {}).get("five_rank_two_sectors_exactly_witnessed")
        )
        and all(
            int(value) != 0 for value in witness.get("determinants", {}).values()
        ),
        "mechanical_augmented_total_is_37": mechanical_augmented_total == 37,
        "signed_guaranteed_floor_is_34": signed_total == 34,
    }
    failures = execution_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SIGNED_GUARANTEED_34_INVARIANT_FLOOR_EMITTED__FULL_RING_OPEN"
            if not failures
            else "SIGNED_INVARIANT_FLOOR_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "counts": {
            "historical_ledger_claimed_total": 25,
            "mechanical_locking_completion_total": mechanical_base_total,
            "mechanical_augmented_total_before_signed_corrections": (
                mechanical_augmented_total
            ),
            "signed_base_total_after_forbidden_and_unproven_removal": (
                signed_base_total
            ),
            "new_norm_products": n_norm,
            "new_independent_tensor_channels": n_channels,
            "signed_guaranteed_floor_total": signed_total,
        },
        "signed_corrections": corrections,
        "guaranteed_floor_basis": {
            "included": signed,
            "appended": appended,
            "n_invariants_total": signed_total,
            "is_complete_invariant_ring": False,
        },
        "exact_witness_determinants": witness.get("determinants", {}),
        "flag": {
            "mechanical_floor37_rejected": True,
            "canonical_signed_floor_34_emitted": not failures,
            "forbidden_210_10dag10_removed": True,
            "historical_complete_filtered_basis_claim_falsified": True,
            "full_unfiltered_molien_haar_series": False,
            "full_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The prior 37 count was a mechanical augmentation, not a valid "
            "floor. After removing forbidden 210·10†·10 and counting only one "
            "independently guaranteed 210^3 and 210·126†·126 channel, the "
            "signed base is 23. Adding six guaranteed norm products and five "
            "exact second-channel witnesses gives a defensible floor of 34. "
            "Further channels may increase it; the full ring remains open."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_ENLARGED_FLOOR_BASIS_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_ENLARGED_FLOOR_BASIS_V20.md").write_text(
        "# Signed guaranteed 34-invariant floor\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
