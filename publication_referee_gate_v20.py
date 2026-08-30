#!/usr/bin/env python3
r"""Publication referee package for the SO(10) axion v20 theory stack.

This is not itself a closure certificate. It renders the qualified canonical
G1–G8 decision together with legacy scalar-ledger and branching diagnostics.
Only the live canonical verifier chain can approve or veto whole-model
validation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import authoritative_full_model_gate_v20 as full_gate
import g1_g8_gate_ledger_v20 as ledger
import nonsusy_sm_triplet_branching_census_v20 as census

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PUBLICATION_REFEREE_GATE_V20.json"
OUT_MD = ROOT / "PUBLICATION_REFEREE_GATE_V20.md"


def build_report() -> dict[str, Any]:
    led = ledger.build_report()
    full = full_gate.build_report()
    bran = census.build_report()

    canonical_validated = (
        full.get("classification", {}).get("whole_model_validated") is True
    )
    expected_full_state = "PASS" if canonical_validated else "BLOCKED"
    checks = {
        "authoritative_full_gate_executes": (
            type(full.get("n_failed")) is int and full.get("n_failed") == 0
        ),
        "canonical_state_is_rendered_without_legacy_veto": (
            full.get("overall_state") == expected_full_state
        ),
        "legacy_scalar_ledger_is_diagnostic_only": True,
        "legacy_branching_census_is_diagnostic_only": True,
        "historical_option_c_results_scoped": (
            led["historical_option_c_subtheorems"]["G1"]["invariant_directions"]
            == 64
            and led["historical_option_c_subtheorems"]["G3"][
                "massive_physical_quotient_dimension"
            ]
            == 449
        ),
        "legacy_gate_numbers_are_not_authoritative": (
            full.get("flag", {}).get("legacy_ledger_controls_authoritative_closure")
            is False
        ),
    }
    failures = [name for name, ok in checks.items() if not ok]
    diagnostic_failures = []
    if led.get("n_failed", 1):
        diagnostic_failures.extend(
            f"legacy scalar ledger: {item}"
            for item in led.get("failures", ["failed"])
        )
    if bran.get("n_failed", 1):
        diagnostic_failures.extend(
            f"legacy branching census: {item}"
            for item in bran.get("failures", ["failed"])
        )

    gate_table = {
        name: {
            "status": row["status"],
            "closed_scope": row.get("authoritative_closed_scope", []),
            "open_scope": row.get("open_scope", []),
        }
        for name, row in led["gates"].items()
    }

    return {
        "status": (
            "PUBLICATION_REFEREE_PACKAGE_READY__CANONICAL_THEORY_VALIDATED"
            if canonical_validated and not failures
            else (
                "PUBLICATION_REFEREE_PACKAGE_READY__THEORY_BLOCKED"
                if not failures
                else "PUBLICATION_REFEREE_PACKAGE_FAILED"
            )
        ),
        "overall_state": expected_full_state if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "diagnostic_failures": diagnostic_failures,
        "canonical_summary": full.get("canonical_g1_g8_summary"),
        "authoritative_totals": led.get("summary"),
        "gates": gate_table,
        "dependency_dag": led.get("dependencies"),
        "closure_waves": led.get("closure_waves"),
        "feasibility": led.get("feasibility"),
        "proton_decay": {
            "exact_unique_proton_lifetime": full.get("classification", {}).get(
                "exact_unique_proton_lifetime"
            )
            is True,
            "proton_decay_observed": full.get("classification", {}).get(
                "proton_decay_observed"
            )
            is True,
            "whole_model_validated": canonical_validated,
            "whole_model_excluded": full.get("classification", {}).get(
                "whole_model_excluded"
            )
            is True,
            "note": (
                "Conditional X/Y and signed-scalar lifetimes exist as stress tests; "
                "they are not unique UV predictions."
            ),
        },
        "issue_106_branching": {
            "status": bran.get("status"),
            "working_light_basis": bran.get("working_light_basis"),
            "aulakh_mapping": bran.get("aulakh_mapping"),
            "next_exact_calculation": bran.get("next_exact_calculation"),
        },
        "issues": {
            "106": "Derive complete nonsusy M_T^2 and component Clebsches",
            "107": "Execute full G1-G8 program; survival not guaranteed",
        },
        "flag": {
            "publication_referee_package": True,
            "theory_proven": canonical_validated,
            "theory_excluded": full.get("classification", {}).get(
                "whole_model_excluded"
            )
            is True,
            "all_g1_g8_closed": full.get("classification", {}).get(
                "all_g1_g8_closed"
            )
            is True,
            "ready_for_honest_submission_as_blocked_program": (
                not failures and not canonical_validated
            ),
        },
        "verdict": (
            "Referee package ready: the qualified canonical V21 verifier chain "
            "has closed all eight gates and validated the whole model. Legacy "
            "scalar-ledger and branching results remain diagnostic context."
            if canonical_validated
            else "Referee package ready: the qualified canonical V21 chain remains "
            "open. Legacy scalar-ledger and branching results are diagnostic only; "
            "this package does not claim the model is proven."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Publication referee gate — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Gate ledger",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    for name, row in report["gates"].items():
        lines.append(f"| {name} | {row['status']} |")
    lines.extend(
        [
            "",
            "## Issue #106 branching",
            "",
            f"- Working basis: `{report['issue_106_branching']['working_light_basis']}`",
            f"- Status: `{report['issue_106_branching']['status']}`",
            "",
            "## Proton decay honesty",
            "",
            f"- Unique lifetime: `{report['proton_decay']['exact_unique_proton_lifetime']}`",
            f"- Whole model validated: `{report['proton_decay']['whole_model_validated']}`",
            f"- Whole model excluded: `{report['proton_decay']['whole_model_excluded']}`",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
