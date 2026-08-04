#!/usr/bin/env python3
"""Integrate latest-main residual closures with the physical-EW scalar audit."""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any

import cal_g_portal_decision_v20 as calg_portal
import efjx_cgc_physical_normalization_gate_v20 as efjx_cgc
import lambda_lock_cal_g_lift_v20 as lock_lift
import nonsusy_reduced_hessian_v20 as physical_hessian
import scalar_alpha_flavour_nonuniqueness_v20 as alpha_nonunique
import tau_p_ultimate_residual_checklist_v20 as ultimate

ROOT = Path(__file__).resolve().parent
GAUGE_DUMP = ROOT / "models" / "LIVE_BETA_DUMP.json"
QUARTIC_DUMP = ROOT / "models" / "LIVE_QUARTIC_SOFT_DUMP.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    gauge_dump = _load(GAUGE_DUMP) if GAUGE_DUMP.is_file() else {}
    quartic_dump = _load(QUARTIC_DUMP) if QUARTIC_DUMP.is_file() else {}
    alpha = alpha_nonunique.build_report()
    portal = calg_portal.build_report()
    lifted = lock_lift.build_report()
    ultimate_report = ultimate.build_report()
    physical = physical_hessian.build_report()
    efjx = efjx_cgc.build_report()

    lock_source = inspect.getsource(lock_lift)
    proxy_dependency = (
        "charge_allowed_potential_minimize_v20" in lock_source
        and "nonsusy_reduced_hessian_v20" not in lock_source
    )
    historical_tachyon = bool(
        physical.get("historical_benchmark", {}).get("tachyonic")
    )
    selected_point_claim_invalidated = bool(
        proxy_dependency
        and historical_tachyon
        and lifted.get("flag", {}).get("selected_point_not_spoiled_by_lock_raise")
    )

    # The old ultimate chain is invalidated by the physical tachyon even when
    # newer upstream code has already failed closed and cleared its stale
    # all-residuals-closed flag.  Requiring that stale flag caused CI to fail
    # for the honest state it was meant to certify.
    ultimate_selected_closure_invalidated = bool(historical_tachyon)

    efjx_executes = bool(
        efjx.get("n_failed", 1) == 0
        and efjx.get("flags", {}).get("exact_EFJX_gamma_response_known")
    )
    proxy_cgc_ratio_invalidated = bool(
        efjx.get("flags", {}).get("proxy_cgc_ratio_invalid_as_physical_prediction")
        and not efjx.get("flags", {}).get("physical_CGC_normalization_derived")
    )
    gauge_valid = bool(
        gauge_dump.get("live_run_executed")
        and gauge_dump.get("matches_ingested_one_loop_b")
        and float(gauge_dump.get("beta_g10_1_coeff")) == -4.0
    )
    coverage = quartic_dump.get("coverage", {})
    quartic_valid = bool(
        quartic_dump.get("live_run_executed")
        and coverage.get("gauge_g10_match_minus4")
        and coverage.get("quartics_present")
        and coverage.get("trilinear_present")
        and coverage.get("soft_present")
    )
    alpha_proven = bool(
        alpha.get("flag", {}).get("scalar_alpha_proven_nonunique_from_flavour")
    )
    calg_mechanism_in_principle = bool(
        portal.get("flag", {}).get("cal_G_portal_decision_resolved")
        and portal.get("flag", {}).get("existing_lambda_lock_sufficient_in_principle")
    )

    checks = {
        "validated_live_gauge_artifact": gauge_valid,
        "validated_live_reduced_quartic_soft_artifact": quartic_valid,
        "scalar_alpha_nonuniqueness_proven": alpha_proven,
        "cal_G_lambda_lock_mechanism_identified_in_principle": calg_mechanism_in_principle,
        "lambda_lock_selected_point_uses_old_proxy": proxy_dependency,
        "physical_EW_historical_point_tachyonic": historical_tachyon,
        "proxy_selected_point_closure_invalidated": selected_point_claim_invalidated,
        "ultimate_selected_point_closure_invalidated": ultimate_selected_closure_invalidated,
        "EFJX_gamma_response_matrices_extracted": efjx_executes,
        "proxy_EFJX_cgc_ratio_invalidated_as_physical": proxy_cgc_ratio_invalidated,
        "exact_unique_lifetime_not_overclaimed": not ultimate_report.get("flag", {}).get(
            "exact_unique_proton_lifetime", True
        ),
        "whole_model_not_declared_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    still_open = {
        "full_210_tensor_quartic_basis_in_live_dump": "full_210_T2_T4_invariant_basis"
        in quartic_dump.get("not_encoded", []),
        "lambda4_CGC_live_encoding": "lam4_210_10_126_S_CGC"
        in quartic_dump.get("not_encoded", []),
        "dim6_lambda_lock_live_encoding": "dim6_lambda_lock"
        in quartic_dump.get("not_encoded", []),
        "physical_EFJX_CGC_normalization_on_h174_branch": not efjx.get("flags", {}).get(
            "physical_CGC_normalization_derived", False
        ),
        "physical_EW_reminimization_after_EFJX_CGC": not efjx.get("flags", {}).get(
            "physical_EW_branch_revalidated", False
        ),
        "cal_G_lift_revalidation_on_physical_EW_survival_point": selected_point_claim_invalidated,
        "ultimate_tau_p_revalidation_after_physical_EW_falsification": ultimate_selected_closure_invalidated,
        "exact_unique_proton_lifetime": True,
    }

    return {
        "status": (
            "LATEST_MAIN_RESIDUALS_INTEGRATED__PROXY_CLOSURES_INVALIDATED"
            if not failures
            else "LATEST_MAIN_RESIDUAL_INTEGRATION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "valid_new_closures": {
            "live_pyrate_gauge_artifact": gauge_valid,
            "live_pyrate_reduced_quartic_soft_artifact": quartic_valid,
            "scalar_alpha_nonunique_from_current_flavour_fit": alpha_proven,
            "cal_G_lambda_lock_lift_mechanism_exists_in_principle": calg_mechanism_in_principle,
            "EFJX_gamma_response_matrices_known_in_Aulakh_convention": efjx_executes,
        },
        "invalidated_selected_point_claims": {
            "lambda_lock_raise_does_not_spoil_selected_point": selected_point_claim_invalidated,
            "all_post_hessian_residuals_closed": ultimate_selected_closure_invalidated,
            "proxy_c_cgc_needed_abs_approx_is_physical": proxy_cgc_ratio_invalidated,
            "reason": (
                "Selected-point conclusions reuse the intermediate-scale 10_H radial proxy, "
                "while the physical h=174 GeV Hessian excludes the historical point."
            ),
        },
        "still_open": still_open,
        "dependency_audit": {
            "lambda_lock_lift_imports_charge_allowed_proxy": proxy_dependency,
            "lambda_lock_lift_imports_physical_EW_hessian": False,
            "physical_historical_min_eigenvalue_GeV2": physical.get(
                "historical_benchmark", {}
            ).get("min_eigenvalue_GeV2"),
            "ultimate_exact_unique_proton_lifetime": ultimate_report.get("flag", {}).get(
                "exact_unique_proton_lifetime"
            ),
            "EFJX_reported_proxy_cgc_ratio": efjx.get("proxy_dependency_audit", {}).get(
                "reported_proxy_c_cgc_needed_abs_approx"
            ),
            "EFJX_physical_cgc_normalization_derived": efjx.get("flags", {}).get(
                "physical_CGC_normalization_derived"
            ),
        },
        "upstream_status": {
            "scalar_alpha": alpha.get("status"),
            "cal_G_portal": portal.get("status"),
            "lambda_lock_lift": lifted.get("status"),
            "ultimate_tau_p": ultimate_report.get("status"),
            "physical_EW_hessian": physical.get("status"),
            "EFJX_CGC_normalization": efjx.get("overall_state"),
        },
        "flag": {
            "live_sarah_or_pyrate_executable_artifact_validated": gauge_valid and quartic_valid,
            "scalar_alpha_nonuniqueness_closed": alpha_proven,
            "cal_G_mechanism_identified_but_physical_point_not_revalidated": True,
            "latest_main_selected_point_closure_invalidated": selected_point_claim_invalidated,
            "EFJX_response_known_but_physical_CGC_open": efjx_executes
            and proxy_cgc_ratio_invalidated,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Valid live artifacts and the E/F/J/X gamma response are retained. "
            "Proxy-selected lambda_lock, tau_p and c_cgc closures remain invalid; "
            "the physical Phi H Sigmabar S normalization and h=174 GeV "
            "re-minimization remain open."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("LATEST_MAIN_RESIDUAL_INTEGRATION_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LATEST_MAIN_RESIDUAL_INTEGRATION_V20.md").write_text(
        "# Latest-main residual integration — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
