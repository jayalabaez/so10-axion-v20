#!/usr/bin/env python3
"""Historical mixed-representation invariant ledger, retained for signed audit.

This module no longer claims a closed filtered Hilbert series. Its 25-count
ledger is preserved as an auditable historical input because downstream signed
modules must show both omissions and over-counts explicitly. The signed audit
proves that ``210_H 10_H^dag 10_H`` is forbidden, conservatively reduces two
unsupported multiplicities, adds proven omissions, rejects mechanical total
37, and emits a guaranteed floor of 34.

A complete mixed-representation Molien/Haar series remains open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent

# Historical ledger exactly as previously claimed. Do not silently edit this
# snapshot: signed corrections are emitted by mixed_rep_enlarged_floor_basis_v20.
MULTIPLICITY: dict[str, dict[str, Any]] = {
    "210_H^dag 210_H": {"n": 1, "grade": "t2", "sector": "pure_210"},
    "210_H^3": {"n": 2, "grade": "t3", "sector": "pure_210"},
    "210_H^4": {"n": 4, "grade": "t4", "sector": "pure_210"},
    "10_H^dag 10_H": {"n": 1, "grade": "t2", "sector": "mass"},
    "126bar_H^dag 126bar_H": {"n": 1, "grade": "t2", "sector": "mass"},
    "S^dag S": {"n": 1, "grade": "t2", "sector": "singlet"},
    "Phi17^dag Phi17": {"n": 1, "grade": "t2", "sector": "singlet"},
    "210_H 10_H^dag 10_H": {"n": 1, "grade": "t3", "sector": "historical_forbidden"},
    "210_H 126bar_H^dag 126bar_H": {"n": 2, "grade": "t3", "sector": "mixed_210_126"},
    "10_H^2 S": {"n": 1, "grade": "t3", "sector": "portal_kappa"},
    "210 · 10 · 126 · S": {"n": 1, "grade": "t4", "sector": "portal_lam4"},
    "(10_H^dag 10_H)^2": {"n": 1, "grade": "t4", "sector": "quartic_10"},
    "(126bar_H^dag 126bar_H)^2": {"n": 1, "grade": "t4", "sector": "quartic_126"},
    "10_H^dag 10_H 126bar_H^dag 126bar_H": {"n": 1, "grade": "t4", "sector": "quartic_mixed"},
    "210_H^dag 210_H 10_H^dag 10_H": {"n": 1, "grade": "t4", "sector": "quartic_mixed"},
    "210_H^dag 210_H 126bar_H^dag 126bar_H": {"n": 1, "grade": "t4", "sector": "quartic_mixed"},
    "|S|^2 |10_H|^2": {"n": 1, "grade": "t4", "sector": "portal_soft"},
    "|S|^2 |126bar_H|^2": {"n": 1, "grade": "t4", "sector": "portal_soft"},
    "|Phi17|^2 |S|^2": {"n": 1, "grade": "t4", "sector": "hierarchy"},
    "126bar_H^2 10_H^2 S^2": {"n": 1, "grade": "t6", "sector": "locking"},
}

FORBIDDEN_EXPLICIT = [
    {"name": "10_H 126bar_H S", "reason": "SO(10)-forbidden"},
    {"name": "126bar_H^2 S", "reason": "SO(10)-forbidden"},
    {"name": "bare_10_H^2", "reason": "PQ-forbidden"},
    {"name": "210_H 10_H^dag 10_H", "reason": "SO(10)-forbidden; historical over-count"},
]


def build_filtered_basis() -> dict[str, Any]:
    canonical_ops = {row["name"]: row for row in z17.operator_catalogue()}
    included: list[dict[str, Any]] = []
    for name, meta in MULTIPLICITY.items():
        canonical = canonical_ops.get(name)
        signed_valid = not (
            canonical is not None and canonical.get("status") == "SO10_FORBIDDEN"
        )
        included.append(
            {
                "name": name,
                "multiplicity": int(meta["n"]),
                "grade": meta["grade"],
                "sector": meta["sector"],
                "historical_included": True,
                "signed_valid": signed_valid,
                "canonical_status": None if canonical is None else canonical.get("status"),
                "included": True,
            }
        )

    by_grade: dict[str, int] = {}
    for row in included:
        by_grade[row["grade"]] = by_grade.get(row["grade"], 0) + int(
            row["multiplicity"]
        )
    historical_total = sum(int(row["multiplicity"]) for row in included)
    generating = " + ".join(
        f"{multiplicity} t^{grade[1:]}"
        for grade, multiplicity in sorted(by_grade.items())
    )
    invalid = [row for row in included if not row["signed_valid"]]
    return {
        "included": included,
        "excluded": FORBIDDEN_EXPLICIT,
        "n_classes": len(included),
        "n_invariants_total": historical_total,
        "historical_claimed_total": historical_total,
        "multiplicity_by_grade": by_grade,
        "generating_function_filtered": generating,
        "historical_invalid_entries": invalid,
        "complete_filtered_renorm_basis": False,
        "signed_audit_required": True,
        "is_historical_snapshot": True,
    }


def build_report() -> dict[str, Any]:
    basis = build_filtered_basis()
    invalid_names = {row["name"] for row in basis["historical_invalid_entries"]}
    checks = {
        "historical_total_is_25": basis["historical_claimed_total"] == 25,
        "five_quadratic_invariants_recorded": basis["multiplicity_by_grade"].get("t2") == 5,
        "forbidden_210_10dag10_detected": "210_H 10_H^dag 10_H" in invalid_names,
        "historical_snapshot_not_called_complete": not basis["complete_filtered_renorm_basis"],
        "signed_audit_required": basis["signed_audit_required"],
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "HISTORICAL_MIXED_REP_LEDGER_EXECUTED__SIGNED_AUDIT_REQUIRED"
            if not failures
            else "HISTORICAL_MIXED_REP_LEDGER_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "filtered_basis": basis,
        "forbidden_explicit": FORBIDDEN_EXPLICIT,
        "flag": {
            "historical_ledger_snapshot": True,
            "historical_complete_claim_falsified": True,
            "mixed_rep_charge_so10_filtered_renorm_hilbert_closed": False,
            "mixed_rep_full_hilbert_series": False,
            "mixed_rep_unfiltered_molien_haar_series": False,
            "kronecker_forbidden_channels_excluded": False,
            "signed_audit_required": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The 25-entry object is retained only as the historical ledger "
            "being audited. It is neither charge+SO(10)-complete nor a Hilbert "
            "series. Signed corrections and proven omissions are applied in "
            "mixed_rep_enlarged_floor_basis_v20."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    basis = report["filtered_basis"]
    return "\n".join(
        [
            "# Historical mixed-representation ledger — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Historical claimed total: {basis['historical_claimed_total']}",
            f"- Invalid entries already detected: {len(basis['historical_invalid_entries'])}",
            f"- Complete filtered basis: {basis['complete_filtered_renorm_basis']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_HILBERT_SERIES_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_HILBERT_SERIES_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
