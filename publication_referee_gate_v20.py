#!/usr/bin/env python3
r"""Publication referee package for the SO(10) axion v20 theory stack.

This is not a closure certificate. It consolidates the authoritative G1–G8
ledger, the proton-decay honesty flags, and the Issue #106 branching census
into one referee-facing artifact that cannot silently claim whole-model
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

    checks = {
        "ledger_green": led.get("n_failed", 1) == 0,
        "full_gate_green": full.get("n_failed", 1) == 0,
        "branching_census_green": bran.get("n_failed", 1) == 0,
        "overall_blocked": led.get("overall_state") == "BLOCKED"
        and full.get("overall_state") == "BLOCKED",
        "authoritative_closed_set_empty": (
            led.get("summary", {}).get("closed") == []
            and led.get("summary", {}).get("n_closed") == 0
        ),
        "all_authoritative_gates_blocked": all(
            row["status"] == "BLOCKED" for row in led["gates"].values()
        ),
        "historical_option_c_results_scoped": (
            led["historical_option_c_subtheorems"]["G1"]["invariant_directions"]
            == 64
            and led["historical_option_c_subtheorems"]["G3"][
                "massive_physical_quotient_dimension"
            ]
            == 449
        ),
        "no_whole_model_validated": not bool(
            full.get("classification", {}).get("whole_model_validated")
        ),
        "no_whole_model_excluded": not bool(
            full.get("classification", {}).get("whole_model_excluded")
        ),
        "no_guarantee_model_passes": not bool(
            led.get("feasibility", {}).get("guarantee_model_survives_recertification")
        ),
        "tprime_promoted": bool(bran.get("flag", {}).get("tprime_126_promoted_into_census")),
        "cg_still_open": not bool(
            bran.get("flag", {}).get("physical_component_CG_complete")
        ),
    }
    failures = [name for name, ok in checks.items() if not ok]

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
            "PUBLICATION_REFEREE_PACKAGE_READY__THEORY_BLOCKED"
            if not failures
            else "PUBLICATION_REFEREE_PACKAGE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_totals": led.get("summary"),
        "gates": gate_table,
        "dependency_dag": led.get("dependencies"),
        "closure_waves": led.get("closure_waves"),
        "feasibility": led.get("feasibility"),
        "proton_decay": {
            "exact_unique_proton_lifetime": False,
            "proton_decay_observed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
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
            "theory_proven": False,
            "theory_excluded": False,
            "all_g1_g8_closed": False,
            "ready_for_honest_submission_as_blocked_program": not bool(failures),
        },
        "verdict": (
            "Referee package ready: 0/8 authoritative gates closed because the "
            "gauged-U(1)_X executable contract is inconsistent; theory BLOCKED, "
            "Issue #106 PS branching census PARTIAL with T' locked and CG/norm OPEN. "
            "This repository defines an executable closure program; it does not "
            "claim the model is proven."
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
            "- Unique lifetime: `False`",
            "- Whole model validated: `False`",
            "- Whole model excluded: `False`",
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
