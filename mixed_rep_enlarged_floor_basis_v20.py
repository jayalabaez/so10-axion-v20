#!/usr/bin/env python3
"""Emit the canonical guaranteed 37-invariant floor without claiming completeness.

The historical filtered ledger contains 25 invariants.  The locking-modulus
repair raises that to 26.  The independent floor audit then proves six missing
norm-product quartics and five additional tensor channels.  This module emits
all 37 guaranteed invariants in one canonical ledger consumed by subsequent
vacuum audits.

This is a lower bound, not a full Molien/Haar enumeration.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_bfb_completion_v20 as completion
import mixed_rep_invariant_exact_witness_v20 as exact_witness
import mixed_rep_invariant_floor_audit_v20 as floor_audit

ROOT = Path(__file__).resolve().parent


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


def build_report() -> dict[str, Any]:
    base = completion.build_report()
    audit = floor_audit.build_report()
    witness = exact_witness.build_report()

    execution_failures: list[str] = []
    for label, report in (
        ("locking_completion", base),
        ("floor_audit", audit),
        ("exact_witness", witness),
    ):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(label)

    included = copy.deepcopy(
        base.get("completed_filtered_basis", {}).get("included", [])
    )
    proposed: list[dict[str, Any]] = []
    proposed.extend(_norm_entry(row) for row in audit.get("missing_norm_products", []))
    proposed.extend(
        _channel_entry(row, index)
        for index, row in enumerate(audit.get("multiplicity_deficits", []))
    )

    existing = {
        row.get("name") for row in included if isinstance(row, dict)
    }
    appended: list[dict[str, Any]] = []
    for row in proposed:
        if row["name"] in existing:
            continue
        included.append(copy.deepcopy(row))
        appended.append(copy.deepcopy(row))
        existing.add(row["name"])

    base_total = int(
        base.get("completed_filtered_basis", {}).get("n_invariants_total", 0)
    )
    total = base_total + sum(int(row.get("multiplicity", 1)) for row in appended)
    n_norm = sum(
        row["sector"] == "guaranteed_missing_norm_product" for row in appended
    )
    n_channels = sum(
        row["sector"] == "guaranteed_additional_tensor_channel"
        for row in appended
    )

    checks = {
        "upstreams_execute": not execution_failures,
        "locking_completion_total_is_26": base_total == 26,
        "six_norm_products_appended": n_norm == 6,
        "five_tensor_channels_appended": n_channels == 5,
        "exact_witnesses_nonzero": bool(
            witness.get("flag", {}).get("five_rank_two_sectors_exactly_witnessed")
        )
        and all(int(value) != 0 for value in witness.get("determinants", {}).values()),
        "guaranteed_floor_total_is_37": total == 37,
        "historical_claim_falsified": bool(
            audit.get("flag", {}).get(
                "historical_complete_filtered_basis_claim_falsified"
            )
        ),
    }
    failures = execution_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "CANONICAL_GUARANTEED_37_INVARIANT_FLOOR_EMITTED__FULL_RING_OPEN"
            if not failures
            else "ENLARGED_FLOOR_BASIS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "counts": {
            "historical_ledger_total": 25,
            "locking_completion_total": base_total,
            "new_norm_products": n_norm,
            "new_independent_tensor_channels": n_channels,
            "guaranteed_floor_total": total,
        },
        "guaranteed_floor_basis": {
            "included": included,
            "appended": appended,
            "n_invariants_total": total,
            "is_complete_invariant_ring": False,
        },
        "exact_witness_determinants": witness.get("determinants", {}),
        "flag": {
            "canonical_floor_37_emitted": not failures,
            "historical_complete_filtered_basis_claim_falsified": True,
            "full_unfiltered_molien_haar_series": False,
            "full_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "A canonical 37-invariant lower-bound ledger is emitted. It contains "
            "every historical entry, the locking modulus companion, six missing "
            "norm products, and five exactly witnessed second tensor channels. "
            "It is a guaranteed floor, not a complete Molien/Haar enumeration."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_ENLARGED_FLOOR_BASIS_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_ENLARGED_FLOOR_BASIS_V20.md").write_text(
        "# Canonical guaranteed 37-invariant floor\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
