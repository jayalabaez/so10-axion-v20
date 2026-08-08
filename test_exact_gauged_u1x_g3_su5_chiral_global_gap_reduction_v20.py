#!/usr/bin/env python3
"""Regression tests for the fail-closed chiral-H global-gap reduction."""
from fractions import Fraction

import exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20 as audit


def test_exact_boundary_gap_and_fixed_orientation() -> None:
    report = audit.build_report()
    strata = report["exact_dangerous_strata"]
    assert strata["Sigma_equals_zero"]["gap_above_selected_orbit"] == "1/5000"
    assert strata["Sigma_equals_zero"]["strictly_above_target"] is True
    assert strata["fixed_F_Delta_equal_norm_H"]["all_nonnegative"] is True
    assert report["n_failed"] == 0


def test_small_beta_theorem_is_fail_closed_on_missing_hypotheses() -> None:
    theorem = audit.perturbation_theorem_audit()
    assert theorem["hypotheses"]["V0_is_an_explicit_nonnegative_sum_of_squares"]
    assert theorem["hypotheses"]["homogeneous_quartic_remains_BFB_exactly"]
    assert theorem["hypotheses"]["fixed_F_Sigma_equalities_are_one_Pluecker_orbit"]
    assert theorem["hypotheses"][
        "fixed_F_full_offkernel_beta_1_over_20_gap_is_exact"
    ]
    assert theorem["hypotheses"][
        "pair_plane_diagonal_Phi_equalities_are_one_physical_orbit"
    ]
    assert theorem["hypotheses"][
        "signed_Phi_orbits_are_exactly_isolated_local_components"
    ]
    assert theorem["hypotheses"][
        "exact_full_486_Hessian_kernel_equals_the_38_symmetry_tangents"
    ]
    assert not theorem["hypotheses"]["all_PD_global_equality_components_are_classified"]
    assert not theorem["theorem_ready"]
    assert not theorem["beta_equals_1_over_20_covered_by_theorem"]


def test_final_acceptance_contract_does_not_promote_g3() -> None:
    report = audit.build_report()
    assert audit.SIGMA_ZERO_GAP == Fraction(1, 5000)
    assert report["final_acceptance_test"]["currently_passes"] is False
    assert report["flags"]["lower_witness_found"] is False
    assert report["flags"]["beta_1_over_20_global_minimum_certified"] is False
    assert report["flags"]["G3_closed"] is False
    assert report["flags"]["whole_model_excluded"] is False
