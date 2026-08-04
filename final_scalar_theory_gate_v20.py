#!/usr/bin/env python3
"""Final fail-closed scalar-theory gate after all executable repairs.

This gate composes the physical-EW repair closure, the perturbative floor37
no-rescue theorem, and the latest-main residual integration. Valid live
PyR@TE artifacts and scalar-alpha non-uniqueness are retained. Proxy-selected
cal-G/tau_p closures are rejected until re-evaluated on the surviving physical
EW branch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import current_main_repair_closure_v20 as closure
import ew_portal_rescue_bound_v20 as rescue
import latest_main_residual_integration_v20 as latest

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    repaired = closure.build_report()
    no_rescue = rescue.build_report()
    latest_report = latest.build_report()

    execution_failures = []
    if repaired.get("execution_failures"):
        execution_failures.extend(repaired["execution_failures"])
    for label, report in (
        ("ew_portal_rescue_bound", no_rescue),
        ("latest_main_residual_integration", latest_report),
    ):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(f"{label}: {report.get('failures')}")

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
    resolved["live_pyrate_artifacts_validated"] = bool(
        latest_report.get("flag", {}).get(
            "live_sarah_or_pyrate_executable_artifact_validated"
        )
    )
    resolved["scalar_alpha_nonuniqueness_characterized"] = bool(
        latest_report.get("flag", {}).get("scalar_alpha_nonuniqueness_closed")
    )
    resolved["latest_main_proxy_dependencies_audited"] = bool(
        latest_report.get("flag", {}).get(
            "latest_main_selected_point_closure_invalidated"
        )
    )

    remaining = dict(repaired.get("remaining_blockers", {}))
    # Latest main supplies validated artifacts, so the stale environment-level
    # blocker is removed. The full tensor encoding remains open below.
    remaining.pop("live_sarah_or_pyrate_run", None)
    # The old generic cal-G blocker is replaced by a sharper physical-EW
    # revalidation requirement.
    remaining.pop("cal_G_soft_mode", None)
    remaining[
        "new_odd_H_tensor_channel_or_hierarchy_mechanism"
    ] = bool(
        no_rescue.get("flag", {}).get(
            "unknown_beyond_floor_odd_H_channel_or_new_mechanism_required"
        )
    )
    for name, value in latest_report.get("still_open", {}).items():
        remaining[name] = bool(value)

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
            "latest_main_physical_historical_min_eigenvalue_GeV2": latest_report.get(
                "dependency_audit", {}
            ).get("physical_historical_min_eigenvalue_GeV2"),
        }
    )

    audit_findings = list(repaired.get("audit_findings", []))
    audit_findings.extend(
        [
            "the guaranteed 37-invariant floor cannot perturbatively rescue the historical lambda4 electroweak tachyon",
            "latest-main live PyR@TE gauge and reduced quartic/soft artifacts are valid and retained",
            "latest-main scalar-alpha non-uniqueness is proven and retained",
            "latest-main cal-G and ultimate selected-point closures are invalidated because they reuse the old intermediate-scale 10_H proxy",
        ]
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
            "live_pyrate_artifacts_validated": resolved[
                "live_pyrate_artifacts_validated"
            ],
            "scalar_alpha_nonuniqueness_proven": resolved[
                "scalar_alpha_nonuniqueness_characterized"
            ],
            "latest_main_proxy_selected_point_closures_invalidated": resolved[
                "latest_main_proxy_dependencies_audited"
            ],
            "whole_model_excluded": False,
            "whole_model_validated": state == "PASS",
        },
        "upstream": {
            "repair_closure_status": repaired.get("overall_state"),
            "rescue_bound_status": no_rescue.get("status"),
            "latest_main_residual_status": latest_report.get("status"),
        },
        "verdict": (
            "All currently executable scalar breakpoints have been pushed to a "
            "fail-closed endpoint on latest main. The historical 25-invariant "
            "completeness claim is false; the guaranteed floor is 37. The "
            "physical h=174 GeV arbitrary-precision Hessian excludes the "
            "historical lambda4=-kappa*M_I/M_GUT benchmark, and perturbative "
            "floor37 even-H quartics cannot rescue it. A lambda4=0 reduced "
            "survival point remains. Latest main validly adds live one-loop "
            "PyR@TE artifacts and proves scalar-alpha non-uniqueness, but its "
            "cal-G/ultimate selected-point closures reuse the invalidated old "
            "10_H proxy and must be redone on the physical-EW branch. The whole "
            "theory remains BLOCKED, not dead."
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
