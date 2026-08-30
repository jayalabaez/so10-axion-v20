from __future__ import annotations

import json

import numpy as np

import susy_v51_cartesian_source_hessian_audit as audit


EXPECTED_H_SHA256 = "0be2edfe6d050b4d6af0339d4d9aa3b58c294adf815068896cee691bb8d0bc3b"
EXPECTED_PULLBACK_SHA256 = "845f7b776778c6317c8afae3dba04f71a4f309cca6592374210bb0438bcac722"


def test_half_normalized_tensor_contractions_recover_v46_reduced_w() -> None:
    certificate = audit.normalization_certificate()
    assert certificate["quadratic_Phi_weights_p_a_omega"] == {
        "p": 1,
        "a": 3,
        "omega": 6,
    }
    assert certificate["cubic_Tr_A3_over_3_nonzero_coefficients"] == {
        "a*a*a": 2,
        "a*omega*omega": 12,
        "omega*omega*p": 6,
    }
    assert certificate["Sigma_barSigma_half_contraction_at_unit_singlets_re_im"] == ["1", "0"]
    assert certificate["eta_linear_coefficients_p_a_omega"] == {
        "p": 1,
        "a": 3,
        "omega": 6,
    }


def test_all_465_f_terms_are_exactly_zero_at_the_witness() -> None:
    certificate = audit.stationarity_certificate()
    assert certificate["maximum_abs_scaled_real_F_term"] == 0
    assert certificate["maximum_abs_scaled_imaginary_F_term"] == 0
    assert certificate["all_465_F_terms_exact_zero"] is True
    assert certificate["parameters"]["m"] == "-7/2"
    assert certificate["parameters"]["M"] == -10


def test_tuned_cross_couplings_are_not_presented_as_a_symmetry_prediction() -> None:
    certificate = audit.stationarity_certificate()
    assert certificate["parameters"]["m1"] == 0
    assert certificate["parameters"]["M1"] == 0
    assert "not enforced" in certificate["matching_scale_tuning"]
    assert "not claimed radiatively stable" in certificate["matching_scale_tuning"]


def test_published_hessian_is_exact_complex_symmetric_and_frozen() -> None:
    real, imaginary = audit.exact_scaled_hessian()
    assert real.shape == (465, 465)
    assert imaginary.shape == (465, 465)
    assert np.array_equal(real, real.T)
    assert np.array_equal(imaginary, imaginary.T)
    certificate = audit.hessian_certificate()
    published = certificate["published_H"]
    assert published["common_denominator"] == 4
    assert published["upper_triangle_nonzero_entries"] == 4588
    assert published["full_matrix_nonzero_entries"] == 8966
    assert published["canonical_H_sha256"] == EXPECTED_H_SHA256


def test_all_spin10_and_u1f_ward_columns_are_exactly_null() -> None:
    ward = audit.hessian_certificate()["Ward_identity"]
    assert ward["tested_columns"] == "45 Spin(10) generators plus U(1)_F"
    assert ward["maximum_abs_real_residual"] == 0
    assert ward["maximum_abs_imaginary_residual"] == 0
    assert ward["HQ_exact_zero_all_46_columns"] is True


def test_modular_minor_and_exact_kernel_sandwich_prove_rank_443() -> None:
    rank = audit.hessian_certificate()["exact_rank_proof"]
    assert rank["finite_field"] == "F13 with i mapped to 5 because 5^2=-1 mod 13"
    assert rank["denominator_four_invertible_mod_13"] is True
    assert rank["rank_H_mod_13"] == 443
    assert rank["rank_Q_mod_13"] == 22
    assert rank["characteristic_zero_upper_bound_from_22_exact_null_columns"] == 443
    assert rank["characteristic_zero_lower_bound_from_modular_minor"] == 443
    assert rank["exact_rank_H"] == 443
    assert rank["exact_nullity_H"] == 22
    assert rank["kernel_equals_gauge_orbit"] is True


def test_physical_443_pullback_is_nondegenerate() -> None:
    pullback = audit.hessian_certificate()["physical_pullback"]
    assert len(pullback["pivot_rows_for_Q"]) == 22
    assert len(pullback["free_rows"]) == 443
    assert pullback["Q_pivot_minor_rank_mod_13"] == 22
    assert pullback["Q_pivot_minor_determinant_mod_13"] == 10
    assert pullback["shape"] == [443, 443]
    assert pullback["rank_mod_13"] == 443
    assert pullback["determinant_mod_13"] == 8
    assert pullback["nondegenerate_over_characteristic_zero"] is True
    assert pullback["canonical_mod13_pullback_sha256"] == EXPECTED_PULLBACK_SHA256


def test_source_f_term_scalar_mass_is_positive_on_the_quotient() -> None:
    consequence = audit.hessian_certificate()["supersymmetric_scalar_consequence"]
    assert consequence["holomorphic_object"] == "H_IJ=W_IJ"
    assert consequence["rank_on_source_chiral_space"] == 443
    assert consequence["positive_definite_on_443_dimensional_physical_quotient"] is True
    assert "does not include" in consequence["scope_exclusion"]


def test_report_passes_but_does_not_promote_g2() -> None:
    report = audit.build_report()
    assert report["status"] == audit.STATUS
    assert report["n_failed"] == 0
    assert report["failures"] == []
    assert report["gate_effect"]["G2_clause_promoted"] is None
    assert report["gate_effect"]["G1_to_G8_promoted"] == []
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_committed_artifacts_are_reproducible() -> None:
    audit.check_artifacts()
    observed = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert observed["core_sha256"] == audit.canonical_sha(observed)
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(observed)
