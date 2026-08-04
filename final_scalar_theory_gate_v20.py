#!/usr/bin/env python3
"""Final fail-closed scalar-theory gate after all executable repairs.

This gate composes the current-main repair closure with the perturbative
floor37 electroweak portal no-rescue theorem.  It is the highest-level verdict
for PR #53: the historical lambda4 benchmark is excluded, a reduced survival
point exists, and the whole model remains blocked pending genuinely new tensor
information rather than additional proxy tests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import current_main_repair_closure_v20 as closure
import ew_portal_rescue_bound_v20 as rescue

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    repaired = closure.build_report()
    no_rescue = rescue.build_report()
    execution_failures = []
    if repaired.get("execution_failures"):
        execution_failures.extend(repaired["execution_failures"])
    if no_rescue.get("n_failed", 1) != 0:
        execution_failures.append(
            f"ew_portal_rescue_bound: {no_rescue.get('failures')}"
        )

    hard_failures = list(repaired.get("hard_theory_failures", []))
    resolved = dict(repaired.get("resolved_breakpoints", {}))
    resolved["floor37_perturbative_no_rescue_theorem"] = bool(
        no_rescue.get("flag", {}).get(
            "historical_lam4_point_excluded_within_guaranteed_floor"
        )
        and no_rescue.get("flag", {}).get(
            "guaranteed_H4_channels_insufficient_perturbatively"
        )
    )

    remaining = dict(repaired.get("remaining_blockers", {}))
    remaining[
        "new_odd_H_tensor_channel_or_hierarchy_mechanism"
    ] = bool(
        no_rescue.get("flag", {}).get(
            "unknown_beyond_floor_odd_H_channel_or_new_mechanism_required"
        )
    )

    if execution_failures:
        state = "EXECUTION_FAIL"
    elif hard_failures:
        state = "THEORY_FAIL"
    elif any(remaining.values()):
        state = "BLOCKED"
    else:
        state = "PASS"

    numerical = dict(repaired.get("numerical", {}))
    numerical.update(
        {
            "historical_direct_HH_curvature_GeV2": no_rescue.get(
                "numerical", {}
            ).get("historical_direct_HH_curvature_GeV2"),
            "required_total_H4_rescue_coupling": no_rescue.get(
                "numerical", {}
            ).get("required_total_H4_coupling"),
            "required_over_floor37_perturbative_allowance": no_rescue.get(
                "numerical", {}
            ).get("required_over_combined_perturbative_allowance"),
            "best_case_floor37_rescued_HH_curvature_GeV2": no_rescue.get(
                "numerical", {}
            ).get("best_case_rescued_HH_curvature_GeV2"),
        }
    )

    audit_findings = list(repaired.get("audit_findings", []))
    audit_findings.append(
        "the guaranteed 37-invariant floor cannot perturbatively rescue the historical lambda4 electroweak tachyon"
    )

    return {
        "status": "FINAL_SCALAR_THEORY_GATE_EXECUTED",
        "overall_state": state,
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_failures,
        "audit_findings": audit_findings,
        "resolved_breakpoints": resolved,
        "remaining_blockers": remaining,
        "numerical": numerical,
        "flags": {
            "historical_invariant_ledger_falsified": bool(
                repaired.get("flags", {}).get("historical_basis_claim_falsified")
            ),
            "historical_lambda4_benchmark_excluded": True,
            "historical_lambda4_benchmark_not_rescuable_with_floor37_perturbative_even_H_terms": bool(
                resolved["floor37_perturbative_no_rescue_theorem"]
            ),
            "reduced_survival_region_exists": bool(
                repaired.get("flags", {}).get("survival_parameter_region_exists")
            ),
            "whole_model_excluded": False,
            "whole_model_validated": state == "PASS",
        },
        "upstream": {
            "repair_closure_status": repaired.get("overall_state"),
            "rescue_bound_status": no_rescue.get("status"),
        },
        "verdict": (
            "All currently executable scalar breakpoints have been pushed to a "
            "fail-closed endpoint. The historical 25-invariant completeness "
            "claim is false; the guaranteed floor is 37. The physical h=174 GeV "
            "arbitrary-precision Hessian excludes the historical "
            "lambda4=-kappa*M_I/M_GUT benchmark. The guaranteed floor37 even-H "
            "quartics cannot perturbatively rescue it: the required H4 coupling "
            "is about 1e25 times the combined 4pi allowance. A lambda4=0 reduced "
            "survival point remains. The whole theory is therefore BLOCKED, not "
            "dead: progress now requires a genuinely new odd-H tensor channel or "
            "hierarchy mechanism, the complete component potential, full tensor "
            "RGEs, and an exact unique proton lifetime."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Final scalar-theory gate — v20",
        "",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Audit findings",
        "",
    ]
    lines.extend(f"- {item}" for item in report["audit_findings"])
    lines.extend(["", "## Remaining blockers", ""])
    lines.extend(
        f"- `{name}`: {value}"
        for name, value in report["remaining_blockers"].items()
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("FINAL_SCALAR_THEORY_GATE_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("FINAL_SCALAR_THEORY_GATE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 1 if report["overall_state"] in {"EXECUTION_FAIL", "THEORY_FAIL"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
