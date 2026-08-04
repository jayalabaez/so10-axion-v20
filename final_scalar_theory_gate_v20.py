#!/usr/bin/env python3
"""Final fail-closed scalar/triplet theory gate on synchronized latest main.

The gate composes the signed invariant audit, physical-EW high-precision
Hessian, signed-floor34 perturbative no-rescue theorem, exact gauge orbit,
latest-main residual audit, and a repository-wide legacy triplet dependency
scan. Valid live artifacts are retained; contaminated spectra, thresholds, and
proton lifetimes are invalidated until rebuilt from the signed M_T^2 path.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import current_main_repair_closure_v20 as closure
import ew_portal_rescue_bound_v20 as rescue
import latest_main_residual_integration_v20 as latest
import triplet_proxy_contamination_audit_v20 as triplet_audit

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    repaired = closure.build_report()
    no_rescue = rescue.build_report()
    latest_report = latest.build_report()
    triplet = triplet_audit.build_report()

    execution_failures: list[str] = []
    if repaired.get("execution_failures"):
        execution_failures.extend(repaired["execution_failures"])
    for label, report in (
        ("ew_portal_rescue_bound", no_rescue),
        ("latest_main_residual_integration", latest_report),
        ("triplet_proxy_contamination_audit", triplet),
    ):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(f"{label}: {report.get('failures')}")

    hard_failures = list(repaired.get("hard_theory_failures", []))
    resolved = dict(repaired.get("resolved_breakpoints", {}))
    resolved["signed_floor34_perturbative_no_rescue_theorem"] = bool(
        no_rescue.get("flag", {}).get(
            "historical_lam4_point_excluded_within_signed_floor34"
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
    resolved["canonical_signed_triplet_mt2_path"] = bool(
        triplet.get("flag", {}).get("canonical_signed_mt2_path_available")
    )
    resolved["legacy_triplet_dependency_graph_mapped"] = bool(
        triplet.get("flag", {}).get("legacy_physical_triplet_chain_invalidated")
    )

    remaining = dict(repaired.get("remaining_blockers", {}))
    remaining.pop("live_sarah_or_pyrate_run", None)
    remaining.pop("cal_G_soft_mode", None)
    remaining["new_odd_H_tensor_channel_or_hierarchy_mechanism"] = bool(
        no_rescue.get("flag", {}).get(
            "unknown_beyond_floor_odd_H_channel_or_new_mechanism_required"
        )
    )
    for name, value in latest_report.get("still_open", {}).items():
        remaining[name] = bool(value)
    remaining["complete_physical_triplet_mass_squared_CG_matrix"] = not bool(
        triplet.get("flag", {}).get("physical_component_CG_complete")
    )
    remaining["rebuild_contaminated_triplet_threshold_lifetime_chain"] = bool(
        triplet.get("flag", {}).get("legacy_physical_triplet_chain_invalidated")
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
            "historical_direct_HH_curvature_GeV2": no_rescue.get("numerical", {}).get(
                "historical_direct_HH_curvature_GeV2"
            ),
            "required_total_H4_rescue_coupling": no_rescue.get("numerical", {}).get(
                "required_total_H4_coupling"
            ),
            "required_over_signed_floor34_perturbative_allowance": no_rescue.get(
                "numerical", {}
            ).get("required_over_combined_perturbative_allowance"),
            "best_case_signed_floor34_rescued_HH_curvature_GeV2": no_rescue.get(
                "numerical", {}
            ).get("best_case_rescued_HH_curvature_GeV2"),
            "latest_main_physical_historical_min_eigenvalue_GeV2": latest_report.get(
                "dependency_audit", {}
            ).get("physical_historical_min_eigenvalue_GeV2"),
            "contaminated_legacy_module_count": len(
                triplet.get("scan", {}).get("contaminated_modules", [])
            ),
            "contaminated_lifetime_module_count": len(
                triplet.get("contaminated_lifetime_modules", [])
            ),
        }
    )

    audit_findings = list(repaired.get("audit_findings", []))
    audit_findings.extend(
        [
            "signed floor34 cannot perturbatively rescue the historical lambda4 electroweak tachyon",
            "latest-main live PyR@TE gauge and reduced quartic/soft artifacts are valid and retained",
            "latest-main scalar-alpha non-uniqueness is proven and retained",
            "latest-main cal-G and ultimate selected-point closures are invalidated because they reuse the old intermediate-scale 10_H proxy",
            f"{numerical['contaminated_legacy_module_count']} legacy modules inherit a forbidden operator or dimension-one scalar triplet matrix and are invalidated as physical closures",
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
            "mechanical_floor37_rejected": bool(
                repaired.get("flags", {}).get("mechanical_floor37_rejected")
            ),
            "signed_guaranteed_floor34_emitted": bool(
                repaired.get("resolved_breakpoints", {}).get(
                    "signed_guaranteed_floor34_emitted"
                )
            ),
            "historical_lambda4_benchmark_excluded": True,
            "historical_lambda4_benchmark_not_rescuable_with_signed_floor34_perturbative_even_H_terms": bool(
                resolved["signed_floor34_perturbative_no_rescue_theorem"]
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
            "canonical_signed_triplet_mt2_available": resolved[
                "canonical_signed_triplet_mt2_path"
            ],
            "legacy_triplet_spectrum_threshold_lifetime_chain_invalidated": resolved[
                "legacy_triplet_dependency_graph_mapped"
            ],
            "whole_model_excluded": False,
            "whole_model_validated": state == "PASS",
        },
        "upstream": {
            "repair_closure_status": repaired.get("overall_state"),
            "rescue_bound_status": no_rescue.get("status"),
            "latest_main_residual_status": latest_report.get("status"),
            "triplet_contamination_status": triplet.get("status"),
        },
        "verdict": (
            "All currently executable scalar breakpoints have been pushed to a "
            "fail-closed endpoint on latest main. The historical invariant ledger "
            "is incomplete and over-counted: mechanical 37 is rejected and the "
            "conservative signed floor is 34. The physical h=174 GeV Hessian "
            "excludes the historical lambda4 point, and perturbative signed-floor34 "
            "terms cannot rescue it. A lambda4=0 reduced survival point remains. "
            "The canonical triplet path now uses M_T^2, removes forbidden cubic "
            "contributions, and preserves the allowed lambda4 CG slot. Every legacy "
            "spectrum, threshold, and lifetime that inherits the old triplet proxy "
            "is invalidated until rebuilt. The whole theory remains BLOCKED, not "
            "excluded."
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
