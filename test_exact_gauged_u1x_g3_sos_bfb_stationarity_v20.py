"""Tests for the exact end-to-end constructive G3 SOS certificate."""
from __future__ import annotations

from fractions import Fraction

import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as certificate


def test_exact_27_parameter_expansion_matches_candidate() -> None:
    expanded = certificate.expanded_sos_coefficient_map()
    declared = certificate.declared_candidate_coefficient_map()
    assert expanded == declared
    assert len(expanded) == 27
    assert expanded["lambda::O44_B02_Phi2_Sigma_projectors"] == {
        (0, 0, 0): Fraction(73, 8)
    }
    assert expanded["re::O12_B01_Hdag_Hdag_pair"] == {
        (2, -1, 0): Fraction(-1)
    }


def test_exact_mixed_square_identities_and_selected_zeroes() -> None:
    mixed = certificate.exact_mixed_certificate()
    assert mixed["witness_determinant"] != 0
    assert mixed["C_square_unique_weights"] == (Fraction(1),) * 6
    assert all(value == 0 for value in mixed["C_square_identity_residuals"])
    assert mixed["A_square_report"]["n_failed"] == 0
    assert mixed["cubic_operator_exactly_hermitian"]
    assert mixed["C_at_P_Delta_raw_max_abs"] == 0
    assert mixed["M_P_Delta_minus_2_Delta_max_abs"] == 0


def test_exact_126_completeness_fractions_and_full_stationarity_gradient() -> None:
    sigma = certificate.exact_delta_self_certificate()
    assert sigma["projector_polynomial_sum"] == (
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(0),
    )
    assert sigma["delta_projector_fractions"] == certificate.RECORDED_DELTA_FRACTIONS
    assert sigma["weighted_quartic_at_delta"] == Fraction(25, 24)
    assert sigma["maximum_stationarity_gradient_residual"] == 0


def test_exact_global_phi_H_wedge_identity() -> None:
    wedge = certificate.exact_wedge_certificate()
    assert wedge["integer_wedge_nonzero_entries"] == 1260
    assert wedge["integer_interior_nonzero_entries"] == 840
    assert wedge["all_polarized_coefficient_residual"] == 0
    assert wedge["P_operator_equals_diag_1x6_0x4"]
    assert wedge["selected_H_index_6_value"] == 0


def test_end_to_end_BFB_and_stationarity_promote_without_overclaim() -> None:
    report = certificate.build_report(recompute=True)
    assert report["n_failed"] == 0
    flags = report["flags"]
    assert flags["complete_27_parameter_SOS_identity_exactly_source_bound"]
    assert flags["complete_potential_BFB_exactly_certified"]
    assert flags["selected_vacuum_stationarity_exactly_certified"]
    assert not flags["selected_vacuum_global_minimum_certified"]
    assert not flags["selected_vacuum_unique_modulo_symmetry"]
    assert not flags["full_Hessian_exactly_source_bound"]
    assert not flags["strict_local_minimum_certified"]
    assert not flags["G3_closed"]
