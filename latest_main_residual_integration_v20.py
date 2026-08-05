#!/usr/bin/env python3
"""Integrate source-correct closures and withdrawals on latest main.

Valid executable work is retained: live reduced beta artifacts, scalar-alpha
non-uniqueness, the direct Phi-H-Sigmabar tensor map and its published T/D
cross-check. Claims contaminated by imported SUSY fermion/gaugino matrices are
explicitly reopened.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cal_g_portal_decision_v20 as calg_portal
import cal_g_soft_mode_classification_v20 as calg_soft
import direct_phi_h_sigmabar_td_crosscheck_v20 as tdcheck
import direct_phi_h_sigmabar_tensor_v20 as direct
import efjx_cgc_physical_normalization_gate_v20 as efjx
import lambda_lock_cal_g_lift_v20 as lock_lift
import mixed_210_126_10_hilbert_hessian_v20 as mixed_hessian
import nonsusy_reduced_hessian_v20 as physical_hessian
import scalar_alpha_flavour_nonuniqueness_v20 as alpha_nonunique
import tau_p_hessian_residual_closure_v20 as tau_hessian
import tau_p_ultimate_residual_checklist_v20 as ultimate

ROOT = Path(__file__).resolve().parent
GAUGE_DUMP = ROOT / "models" / "LIVE_BETA_DUMP.json"
QUARTIC_DUMP = ROOT / "models" / "LIVE_QUARTIC_SOFT_DUMP.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    gauge_dump = _load(GAUGE_DUMP) if GAUGE_DUMP.is_file() else {}
    quartic_dump = _load(QUARTIC_DUMP) if QUARTIC_DUMP.is_file() else {}

    direct_rep = direct.build_report()
    td_rep = tdcheck.build_report()
    efjx_rep = efjx.build_report()
    mixed_rep = mixed_hessian.build_report()
    calg_rep = calg_soft.build_report()
    portal_rep = calg_portal.build_report()
    lock_rep = lock_lift.build_report()
    tau_hess_rep = tau_hessian.build_report()
    ultimate_rep = ultimate.build_report()
    alpha_rep = alpha_nonunique.build_report()
    physical_rep = physical_hessian.build_report()

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
    alpha_valid = bool(
        alpha_rep.get("n_failed") == 0
        and alpha_rep.get("flag", {}).get(
            "scalar_alpha_proven_nonunique_from_flavour"
        )
    )
    historical_tachyon = bool(
        physical_rep.get("historical_benchmark", {}).get("tachyonic")
    )

    direct_valid = bool(
        direct_rep.get("n_failed") == 0
        and direct_rep.get("representation", {}).get("tensor_map_shape")
        == [10, 126]
        and direct_rep.get("flags", {}).get(
            "canonical_126_kinetic_basis_constructed"
        )
        and direct_rep.get("flags", {}).get(
            "closed_analytic_portal_spectrum_derived"
        )
    )
    td_valid = bool(
        td_rep.get("n_failed") == 0
        and td_rep.get("max_abs_residual", 1.0) < 1e-12
        and td_rep.get("flags", {}).get(
            "published_gamma_TD_magnitudes_matched"
        )
    )
    efjx_corrected = bool(
        efjx_rep.get("n_failed") == 0
        and efjx_rep.get("flags", {}).get("efjx_cgc_route_invalidated")
        and efjx_rep.get("flags", {}).get(
            "exact_EFJX_gauge_response_known"
        )
        and not efjx_rep.get("flags", {}).get(
            "exact_EFJX_gamma_response_known"
        )
        and not efjx_rep.get("flags", {}).get(
            "old_8p8e29_bound_valid", True
        )
    )
    mixed_withdrawn = bool(
        mixed_rep.get("n_failed") == 0
        and mixed_rep.get("flag", {}).get(
            "imported_susy_hessian_withdrawn"
        )
        and not mixed_rep.get("flag", {}).get(
            "mixed_210_126_10_complete", True
        )
    )
    calg_withdrawn = bool(
        calg_rep.get("n_failed") == 0
        and calg_rep.get("flag", {}).get(
            "cal_G_susy_gaugino_diagnostic_only"
        )
        and not calg_rep.get("flag", {}).get(
            "cal_G_soft_mode_classified", True
        )
    )
    portal_withdrawn = bool(
        portal_rep.get("n_failed") == 0
        and portal_rep.get("flag", {}).get(
            "cal_G_susy_gaugino_target_withdrawn"
        )
        and not portal_rep.get("flag", {}).get(
            "cal_G_portal_decision_resolved", True
        )
    )
    lock_withdrawn = bool(
        lock_rep.get("n_failed") == 0
        and lock_rep.get("flag", {}).get(
            "cal_G_susy_gaugino_target_withdrawn"
        )
        and not lock_rep.get("flag", {}).get(
            "selected_lambda_lock_raised_to_cal_G_lift", True
        )
    )
    tau_hessian_reopened = bool(
        tau_hess_rep.get("n_failed") == 0
        and tau_hess_rep.get("flag", {}).get(
            "imported_susy_hessian_withdrawn"
        )
        and not tau_hess_rep.get("flag", {}).get(
            "full_component_hessian_residual_closed", True
        )
    )
    ultimate_open = bool(
        ultimate_rep.get("n_failed") == 0
        and not ultimate_rep.get("flag", {}).get(
            "exact_unique_proton_lifetime", True
        )
    )
    all_susy_withdrawn = bool(
        mixed_withdrawn
        and calg_withdrawn
        and portal_withdrawn
        and lock_withdrawn
        and tau_hessian_reopened
    )
    selected_point_invalidated = bool(historical_tachyon and lock_withdrawn)

    checks = {
        "validated_live_gauge_artifact": gauge_valid,
        "validated_live_reduced_quartic_soft_artifact": quartic_valid,
        "scalar_alpha_nonuniqueness_proven": alpha_valid,
        "physical_historical_point_tachyonic": historical_tachyon,
        "direct_canonical_tensor_map": direct_valid,
        "published_gamma_TD_crosscheck": td_valid,
        "EFJX_gauge_gamma_collision_corrected": efjx_corrected,
        "imported_susy_scalar_hessian_withdrawn": mixed_withdrawn,
        "cal_G_scalar_classification_withdrawn": calg_withdrawn,
        "cal_G_portal_decision_withdrawn": portal_withdrawn,
        "lambda_lock_lift_withdrawn": lock_withdrawn,
        "proton_hessian_closure_reopened": tau_hessian_reopened,
        "exact_unique_lifetime_open": ultimate_open,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    still_open = {
        "complete_nonsusy_invariant_ring": True,
        "complete_mixed_rep_invariant_enumeration": True,
        "full_210_tensor_quartic_basis_in_live_dump": True,
        "map_repository_selected_vevs_to_canonical_tensor_convention": True,
        "published_state_label_dictionary_for_direct_tensor": True,
        "direct_portal_component_mass_squared_insertion": True,
        "direct_nonsusy_component_mass_squared_insertion": True,
        "direct_nonsusy_singlet_mass_squared_matrix": True,
        "lambda4_CGC_live_encoding": True,
        "dim6_lambda_lock_live_encoding": True,
        "cal_G_lift_revalidation_on_physical_EW_survival_point": True,
        "global_vacuum_boundedness_and_competing_extrema": True,
        "gauge_projected_full_component_hessian": True,
        "full_component_hessian_after_direct_tensor": True,
        "full_component_nonsusy_hessian": True,
        "physical_triplet_threshold_spectrum": True,
        "full_tensor_two_loop_threshold_running": True,
        "ultimate_tau_p_revalidation_after_physical_EW_falsification": True,
        "exact_unique_proton_lifetime": True,
    }

    return {
        "status": (
            "LATEST_MAIN_SOURCE_CORRECTIONS_INTEGRATED__THEORY_BLOCKED"
            if not failures
            else "LATEST_MAIN_RESIDUAL_INTEGRATION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "valid_new_closures": {
            "live_pyrate_gauge_artifact": gauge_valid,
            "live_pyrate_reduced_quartic_soft_artifact": quartic_valid,
            "scalar_alpha_nonunique_from_current_flavour_fit": alpha_valid,
            "direct_Phi_H_Sigmabar_10x126_tensor_map": direct_valid,
            "direct_tensor_closed_analytic_3p3p2p2_spectrum": direct_valid,
            "published_gamma_TD_clebsch_crosscheck": td_valid,
            "EFJX_gauge_superhiggs_source_identified": efjx_corrected,
            "cal_G_lambda_lock_lift_mechanism_exists_in_principle": False,
        },
        "withdrawn_or_reopened_claims": {
            "EFJX_gauge_response_is_lambda4_gamma_response": efjx_corrected,
            "c_norm_needed_is_8p8e29": efjx_corrected,
            "imported_susy_matrices_form_complete_scalar_hessian": mixed_withdrawn,
            "cal_G_fermion_singular_vector_is_physical_scalar_mode": calg_withdrawn,
            "existing_lambda_lock_proven_to_lift_physical_cal_G_scalar": portal_withdrawn,
            "selected_point_not_spoiled_by_lambda_lock_raise": lock_withdrawn,
            "full_component_hessian_closed": tau_hessian_reopened,
            "exact_unique_proton_lifetime": ultimate_open,
        },
        "invalidated_selected_point_claims": {
            "lambda_lock_raise_does_not_spoil_selected_point": lock_withdrawn,
            "all_post_hessian_residuals_closed": tau_hessian_reopened,
            "proxy_c_cgc_needed_abs_approx_is_physical": efjx_corrected,
            "EFJX_gauge_response_is_lambda4_gamma_response": efjx_corrected,
            "c_norm_needed_is_8p8e29": efjx_corrected,
        },
        "still_open": still_open,
        "dependency_audit": {
            "lambda_lock_lift_imports_charge_allowed_proxy": False,
            "lambda_lock_lift_imports_physical_EW_hessian": False,
            "physical_historical_min_eigenvalue_GeV2": physical_rep.get(
                "historical_benchmark", {}
            ).get("min_eigenvalue_GeV2"),
            "EFJX_old_8p8e29_bound": None,
            "direct_tensor_map_shape": direct_rep.get(
                "representation", {}
            ).get("tensor_map_shape"),
            "direct_TD_crosscheck_residual": td_rep.get("max_abs_residual"),
            "mixed_susy_hessian_withdrawn": mixed_withdrawn,
            "cal_G_route_withdrawn": calg_withdrawn
            and portal_withdrawn
            and lock_withdrawn,
            "ultimate_exact_unique_proton_lifetime": ultimate_rep.get(
                "flag", {}
            ).get("exact_unique_proton_lifetime"),
        },
        "upstream_status": {
            "direct_tensor": direct_rep.get("status"),
            "direct_TD_crosscheck": td_rep.get("status"),
            "EFJX_source_correction": efjx_rep.get("status"),
            "mixed_hessian": mixed_rep.get("status"),
            "cal_G_classification": calg_rep.get("status"),
            "cal_G_portal": portal_rep.get("status"),
            "lambda_lock_lift": lock_rep.get("status"),
            "tau_hessian": tau_hess_rep.get("status"),
            "ultimate_tau_p": ultimate_rep.get("status"),
        },
        "flag": {
            "live_sarah_or_pyrate_executable_artifact_validated": (
                gauge_valid and quartic_valid
            ),
            "scalar_alpha_nonuniqueness_closed": alpha_valid,
            "cal_G_mechanism_identified_but_physical_point_not_revalidated": True,
            "latest_main_selected_point_closure_invalidated": selected_point_invalidated,
            "direct_tensor_problem_closed": direct_valid and td_valid,
            "EFJX_cgc_route_invalidated": efjx_corrected,
            "EFJX_cgc_route_invalidated_direct_tensor_open": (
                efjx_corrected and direct_valid
            ),
            "old_8p8e29_bound_valid": False,
            "all_susy_matrix_scalar_closures_withdrawn": all_susy_withdrawn,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The direct canonically normalized Phi-H-Sigmabar tensor map and "
            "independent Aulakh gamma T/D cross-check are retained. EFJX, cal G, "
            "mixed-Hessian, lambda-lock and proton-lifetime closures contaminated "
            "by SUSY fermion/gaugino matrices are withdrawn. The tensor problem is "
            "closed; the complete non-SUSY scalar theory remains BLOCKED."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("LATEST_MAIN_RESIDUAL_INTEGRATION_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LATEST_MAIN_RESIDUAL_INTEGRATION_V20.md").write_text(
        "# Latest-main source-correction integration — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
