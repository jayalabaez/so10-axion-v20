#!/usr/bin/env python3
"""Fail-closed global-gap reduction for the SU(5)+Delta+chiral-H candidate.

The full-H candidate in
``exact_gauged_u1x_g3_su5_delta_hsx_extension_v20`` has all of the local
properties needed by G3, but its small positive adjoint-current deformation

    beta I_45(H,Sigma),       beta = 1/20,

is not itself a sum of squares.  This module records the exact mathematical
test which remains before that candidate can be called a global vacuum.

Write ``V0`` for the candidate with beta set to zero and with its irrelevant
constant removed.  It is the explicit nonnegative sum

    V_PD + (N_H-1)^2 + |H.H|^2
         + 2 ||P_chi(H wedge Phi)||^2
         + (|S|^2-1/25)^2 + (|X|^2-1)^2/32.

Consequently its equality set is compact.  On the explicitly constructed
SU(5) stratum, the Phi/Sigma residuals put Sigma in the complex 10; the
Sigma-1050bar residual is the Pluecker condition, so Sigma is a decomposable
two-plane.  The chiral H square puts H in the complex 5.  After an SU(5)
rotation to the canonical Delta representative, the current is nonnegative:
it is zero on the two-plane and positive on its three-dimensional complement.
Thus beta I_45 selects precisely an electroweak vector on this stratum.

A standard compact Morse--Bott perturbation argument would then prove that
``V0+beta I45`` has the same global lower bound for every sufficiently small
positive beta, provided *all* equality components of the PD SOS are first
classified and have the same current property.  The upstream PD certificate
deliberately leaves that global equality-orbit classification open.  This
module therefore does not turn the conditional argument into a G3 claim.

The output is a final acceptance test, not another local candidate.  The exact
full Hessian/rank certificate is now supplied independently; G3 may be promoted
only when the missing global equality classification and a uniform finite-field
gap are also supplied.  No random scan is treated as proof.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd
import exact_gauged_u1x_g3_su5_equality_orbit_v20 as equality

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.md"
EXACT_HESSIAN_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
)
FIXED_F_OFFKERNEL_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
)

T = Fraction(1, 8)
R = Fraction(1, 5)
BETA = Fraction(1, 20)
SIGMA_ZERO_GAP = T * R**4


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    return value


def _load_exact_hessian_report() -> dict[str, Any]:
    """Load the independently generated exact certificate without recomputing it."""
    try:
        report = json.loads(EXACT_HESSIAN_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return report if isinstance(report, dict) else {}


def _load_fixed_f_offkernel_report() -> dict[str, Any]:
    """Load the source-bound fixed-F global certificate without recomputing it."""
    try:
        report = json.loads(FIXED_F_OFFKERNEL_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return report if isinstance(report, dict) else {}


def perturbation_theorem_audit() -> dict[str, Any]:
    """Expose every hypothesis of the small-positive-beta theorem."""
    pd_report = pd.build_report()
    hsx_report = hsx.build_report(recompute_heavy=False)
    equality_report = equality.build_report()
    exact_hessian_report = _load_exact_hessian_report()
    fixed_f_report = _load_fixed_f_offkernel_report()
    pd_scope = pd_report["scope"]
    global_status = hsx_report["global_status"]
    equality_scope = equality_report["scope"]
    exact_hessian_flags = exact_hessian_report.get("flags", {})
    exact_hessian_closed = bool(
        exact_hessian_report.get("status")
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and exact_hessian_report.get("overall_state")
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and exact_hessian_report.get("model_contract_id") == hsx.MODEL_CONTRACT_ID
        and exact_hessian_report.get("n_failed") == 0
        and exact_hessian_flags.get("exact_rank_448") is True
        and exact_hessian_flags.get("exact_nullity_38") is True
        and exact_hessian_flags.get("exact_PSD") is True
        and exact_hessian_flags.get("strict_quotient_positive") is True
        and exact_hessian_flags.get("kernel_equals_38_symmetry_tangents") is True
        and exact_hessian_flags.get("source_binding_exact") is True
        and exact_hessian_flags.get("proof_grade") is True
    )
    fixed_f_scope = fixed_f_report.get("scope", {})
    fixed_f_checks = fixed_f_report.get("checks", {})
    fixed_f_global_closed = bool(
        fixed_f_report.get("status")
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and fixed_f_report.get("overall_state")
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_report.get("n_failed") == 0
        and fixed_f_checks.get("mixed_offkernel_gap_at_least_6_over_5_exact")
        is True
        and fixed_f_checks.get("pure_hplus_current_error_bound_exact") is True
        and fixed_f_checks.get("cross_block_bound_exact") is True
        and fixed_f_checks.get("rational_inside_outside_patch_positive") is True
        and fixed_f_checks.get("full_fixed_F_equality_orbit_exact") is True
        and fixed_f_scope.get("Phi_fixed_to_F") is True
        and fixed_f_scope.get("H_arbitrary") is True
        and fixed_f_scope.get("Sigma_arbitrary") is True
        and fixed_f_scope.get("beta_equals_1_over_20") is True
        and fixed_f_scope.get(
            "global_gap_nonnegative_on_full_fixed_F_stratum"
        )
        is True
        and fixed_f_scope.get("equality_is_selected_SU5_flag_orbit") is True
        and fixed_f_scope.get("arbitrary_Phi_proved") is False
        and fixed_f_scope.get("G3_closed") is False
    )

    hypotheses = {
        "V0_is_an_explicit_nonnegative_sum_of_squares": bool(
            pd_scope["Phi_Sigma_global_minimum_exact"]
            and hsx_report["checks"]["chiral_Phi_H_square_exact"]
        ),
        "V0_is_coercive_and_its_equality_set_is_compact": True,
        "selected_flag_has_zero_current_and_zero_full_gradient": bool(
            hsx_report["checks"]["live_full_gradient_zero"]
        ),
        "selected_flag_has_positive_448_quotient_Hessian_numerically": bool(
            hsx_report["checks"]["live_448_quotient_positive"]
        ),
        "homogeneous_quartic_remains_BFB_exactly": bool(
            hsx_report["checks"]["quartic_BFB_bound"]
        ),
        "fixed_F_Sigma_equalities_are_one_Pluecker_orbit": bool(
            equality_scope["fixed_F_Sigma_global_equality_classified"]
        ),
        "fixed_F_full_offkernel_beta_1_over_20_gap_is_exact": (
            fixed_f_global_closed
        ),
        "pair_plane_diagonal_Phi_equalities_are_one_physical_orbit": bool(
            equality_scope["fixed_Delta_diagonal_Phi_global_equality_classified"]
            and equality_scope["two_visible_sign_branches_equivalent"]
        ),
        "signed_Phi_orbits_are_exactly_isolated_local_components": bool(
            equality_scope["signed_Phi_orbits_locally_isolated_exactly"]
            and not equality_scope["distant_disconnected_Phi_components_excluded"]
        ),
        "all_PD_global_equality_components_are_classified": bool(
            pd_scope["global_orbit_uniqueness"]
            and equality_scope["global_equality_orbit_classification_complete"]
        ),
        "current_is_nonnegative_on_every_PD_equality_component": False,
        "every_zero_of_current_on_the_PD_equality_set_is_the_selected_flag_orbit": False,
        "exact_full_486_Hessian_kernel_equals_the_38_symmetry_tangents": (
            exact_hessian_closed
        ),
    }
    theorem_ready = all(hypotheses.values())
    return {
        "theorem": (
            "compact Morse-Bott small-parameter stability of a nonnegative "
            "coercive polynomial under beta*I45"
        ),
        "hypotheses": hypotheses,
        "theorem_ready": theorem_ready,
        "conclusion_if_ready": (
            "there exists beta_star>0 such that every 0<beta<beta_star "
            "preserves the global lower bound and selects the chiral SM flag"
        ),
        "beta_equals_1_over_20_covered_by_theorem": False,
        "upstream_global_status": global_status,
        "exact_local_Hessian_status": exact_hessian_report.get("status"),
        "fixed_F_global_status": fixed_f_report.get("status"),
        "exact_equality_reduction": {
            "fixed_F_mixed_kernel": "complex 10",
            "Sigma_1050bar_zero_condition": (
                "(256/9) times the sum of five squared Pluecker Pfaffians"
            ),
            "fixed_F_normalized_Sigma_zero_set": "one U(5) orbit",
            "fixed_F_arbitrary_H_Sigma_beta_gap": "exactly nonnegative",
            "fixed_F_gap_equality_set": "one determinant-corrected SU(5) flag orbit",
            "pair_plane_diagonal_Phi_zero_set": "F+ and F-, one physical orbit",
            "signed_Phi_orbits_locally_isolated": True,
            "distant_disconnected_Phi_components_excluded": False,
            "remaining_lemma": equality_report["remaining_global_lemma"],
        },
    }


def exact_dangerous_strata() -> dict[str, Any]:
    """Record exact strata which a putative global proof must include."""
    fixed = hsx.fixed_pd_equal_norm_h_orientation_certificate()
    return {
        "Sigma_equals_zero": {
            "gap_above_selected_orbit": SIGMA_ZERO_GAP,
            "decimal_gap": float(SIGMA_ZERO_GAP),
            "derivation": "t*(0-r^2)^2=(1/8)*(1/5)^4",
            "strictly_above_target": SIGMA_ZERO_GAP > 0,
            "importance": (
                "this is the nearest known boundary stratum and fixes the "
                "scale required in any uniform beta bound"
            ),
        },
        "fixed_F_Delta_equal_norm_H": fixed,
        "two_singlet_representatives": {
            "normalized_ratios": [
                "(1,sqrt(3),+sqrt(6))/sqrt(10)",
                "(1,sqrt(3),-sqrt(6))/sqrt(10)",
            ],
            "both_require_equality_orbit_classification": True,
        },
        "known_lower_field_witness": False,
        "random_or_floating_search_counts_as_proof": False,
    }


def build_report() -> dict[str, Any]:
    theorem = perturbation_theorem_audit()
    strata = exact_dangerous_strata()
    checks = {
        "sigma_zero_exact_gap_is_1_over_5000": (
            strata["Sigma_equals_zero"]["gap_above_selected_orbit"]
            == Fraction(1, 5000)
        ),
        "fixed_PD_H_orientation_has_no_lower_direction": bool(
            strata["fixed_F_Delta_equal_norm_H"]["all_nonnegative"]
            and not strata["fixed_F_Delta_equal_norm_H"][
                "lower_equal_norm_H_orientation_found"
            ]
        ),
        "quartic_BFB_is_not_confused_with_globality": bool(
            theorem["hypotheses"]["homogeneous_quartic_remains_BFB_exactly"]
            and not theorem["beta_equals_1_over_20_covered_by_theorem"]
        ),
        "PD_global_equality_classification_is_fail_closed": not theorem[
            "hypotheses"
        ]["all_PD_global_equality_components_are_classified"],
        "fixed_F_Pluecker_reduction_is_exact": theorem["hypotheses"][
            "fixed_F_Sigma_equalities_are_one_Pluecker_orbit"
        ],
        "fixed_F_full_offkernel_beta_gap_is_exact": theorem["hypotheses"][
            "fixed_F_full_offkernel_beta_1_over_20_gap_is_exact"
        ],
        "diagonal_Phi_slice_is_exact": theorem["hypotheses"][
            "pair_plane_diagonal_Phi_equalities_are_one_physical_orbit"
        ],
        "exact_full_Hessian_is_closed": theorem["hypotheses"][
            "exact_full_486_Hessian_kernel_equals_the_38_symmetry_tangents"
        ],
        "G3_is_not_promoted_without_the_final_gap": not theorem["theorem_ready"],
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "GLOBAL_GAP_REDUCED_TO_PD_EQUALITY_CLASSIFICATION"
                if not failures
                else "GLOBAL_GAP_REDUCTION_INTEGRITY_FAILED"
            ),
            "overall_state": "FINAL_G3_TEST_OPEN" if not failures else "EXECUTION_FAIL",
            "model_contract_id": hsx.MODEL_CONTRACT_ID,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "candidate": {
                "Phi": "F0/sqrt(10)",
                "Sigma": "Delta_R/5",
                "H": "(e6+i e7)/sqrt(2)",
                "S": "1/5",
                "Phi17": "1",
                "beta_O35_45": BETA,
            },
            "exact_dangerous_strata": strata,
            "small_beta_global_reduction": theorem,
            "final_acceptance_test": {
                "required_statement": (
                    "For every 486-real field q, V_beta(q)-V_beta(q0)>=0; "
                    "equality holds only on the SO(10)xU(1)_XxPQ orbit of q0."
                ),
                "required_evidence": [
                    "classify every equality component of the beta=0 PD SOS",
                    "prove I45(H,Sigma)>=0 on each full-SOS equality component",
                    "prove all zeros of that restriction are the selected chiral flag orbit",
                    "supply an explicit beta interval containing beta=1/20, or lower beta to a certified interval",
                ],
                "currently_passes": False,
            },
            "flags": {
                "lower_witness_found": False,
                "conditional_small_positive_beta_route_exists": True,
                "beta_1_over_20_global_minimum_certified": False,
                "global_equality_orbits_classified": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
            "verdict": (
                "The chiral-H candidate has survived the exact Sigma=0 and "
                "fixed-PD orientation tests, and no lower witness is known. "
                "The final global question is reduced to the unproved global "
                "equality classification of the PD SOS and a uniform bound "
                "away from the signed Phi strata. The complete Phi=F stratum "
                "is now certified at beta=1/20 for arbitrary H and Sigma, but "
                "that subtheorem does not by itself close G3."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SU(5) chiral-H global-gap reduction -- v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        "- exact Sigma=0 gap: `1/5000`;\n"
        "- lower witness found: `false`;\n"
        "- beta=1/20 finite-field global gap: `OPEN`;\n"
        "- exact full-Hessian certificate: `OPEN`;\n"
        "- G3: `OPEN`.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
