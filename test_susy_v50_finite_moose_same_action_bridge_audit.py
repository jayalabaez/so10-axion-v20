from __future__ import annotations

import json

import numpy as np

import susy_v50_finite_moose_action_spec as shared_action
import susy_v50_finite_moose_same_action_bridge_audit as audit


EXPECTED_SHARED_ACTION_SHA256 = "04c6e60038412d99b7c2e9a80c4159fb1a6ba328a159df7b62a8fb45ec1158e4"


def test_one_shared_canonical_action_fingerprint_is_used_by_C2_C3_C4() -> None:
    report = audit.build_report()
    references = report["same_action_clause_references"]
    assert len(set(references.values())) == 1
    assert set(references.values()) == {report["shared_action_sha256"]}
    assert audit.action_fingerprint() == report["shared_action_sha256"]
    assert audit.action_fingerprint() == shared_action.action_fingerprint()
    assert audit.action_fingerprint() == EXPECTED_SHARED_ACTION_SHA256
    assert audit.canonical_bytes(audit.action_manifest()) == shared_action.canonical_action_bytes()
    shared_action.assert_matrix_fingerprint(audit.compressed_action_matrices())


def test_matrix_fingerprint_is_exact_bitwise_not_decimal_rounded() -> None:
    matrix = audit.compressed_action_matrices()["collar_M"]
    changed = matrix.copy()
    changed[0, 0] = complex(np.nextafter(changed[0, 0].real, np.inf), changed[0, 0].imag)
    assert shared_action.matrix_sha256(changed) != shared_action.matrix_sha256(matrix)


def test_compressed_action_contains_every_named_block_and_endpoint_auxiliaries() -> None:
    matrices = audit.compressed_action_matrices()
    assert matrices["collar_M"].shape == matrices["collar_Z"].shape == (44, 44)
    norms = matrices["collar_metadata"]["block_spectral_norms"]
    for name in ("A", "Xi", "C", "R7", "R8", "Z"):
        assert max(norms[name]) > 0.0
    assert matrices["source_M_physical"].shape == (9, 9)
    assert matrices["gauge_L_unbroken"].shape == (5, 5)
    assert matrices["link_L"].shape == (4, 4)


def test_literal_finite_collar_hessian_is_symmetric_and_nearest_neighbour() -> None:
    matrices = audit.compressed_action_matrices()
    mass = matrices["collar_M"]
    assert audit.maximum_abs(mass - mass.T) < 1.0e-12
    locality = audit.locality_certificate(matrices)
    assert locality["collar_non_nearest_neighbour_block_violations"] == 0
    assert locality["source_incidence_nonzero_count"] == 2 * audit.N_CELLS
    assert locality["all_fundamental_terms_site_or_nearest_neighbour"]
    assert not locality["fundamental_endpoint_to_interior_product_present"]


def test_positive_Kahler_transport_completion_is_the_frozen_action() -> None:
    manifest = audit.action_manifest()
    assert "positive-Kahler" in manifest["regulator_choice"]
    matrices = audit.compressed_action_matrices()
    source_metric = matrices["source_Z_physical"]
    assert np.min(np.linalg.eigvalsh(source_metric)) > 0.0
    assert np.allclose(np.diag(source_metric)[:5], 0.2)
    assert np.allclose(np.diag(source_metric)[5:], 1.0)


def test_complex_Nambu_pencils_are_Hermitian_and_plus_minus_paired() -> None:
    matrices = audit.compressed_action_matrices()
    for mass_name, metric_name in (
        ("collar_M", "collar_Z"),
        ("source_M_physical", "source_Z_physical"),
        ("source_M_gauge_orbit", "source_Z_gauge_orbit"),
    ):
        certificate = audit.nambu_certificate(matrices[mass_name], matrices[metric_name])
        assert certificate["M_transpose_symmetry_residual"] < 1.0e-11
        assert certificate["H_N_Hermitian_residual"] < 1.0e-12
        assert certificate["Z_N_Hermitian_residual"] < 1.0e-12
        assert certificate["Z_N_minimum_eigenvalue"] > 0.0
        assert certificate["whitened_Hermitian_residual"] < 1.0e-10
        assert certificate["plus_minus_pairing_residual"] < 1.0e-9


def test_Nambu_construction_handles_nontrivial_complex_symmetric_input() -> None:
    mass = np.asarray(
        [[0.4 + 0.2j, -0.1 + 0.07j], [-0.1 + 0.07j, 0.3 - 0.11j]],
        dtype=np.complex128,
    )
    metric = np.asarray([[1.2, 0.08j], [-0.08j, 0.9]], dtype=np.complex128)
    certificate = audit.nambu_certificate(mass, metric)
    assert certificate["H_N_Hermitian_residual"] < 1.0e-14
    assert certificate["whitened_Hermitian_residual"] < 1.0e-13
    assert certificate["plus_minus_pairing_residual"] < 1.0e-12


def test_exact_direct_sum_proves_all_5303_kinetic_eigenvalues_positive() -> None:
    matrices = audit.compressed_action_matrices()
    certificate = audit.direct_sum_kinetic_certificate(matrices)
    assert certificate["full_gauge_fixed_coordinate_dimension"] == 5303
    assert certificate["full_metric_positive_eigenvalue_count"] == 5303
    assert certificate["full_metric_minimum_from_exact_core_spectra"] > 0.0
    assert certificate["analytic_full_metric_lower_bound"] > 0.0
    assert certificate["representative_all_sector_minimum"] > 0.0
    assert "multiset union" in certificate["Kronecker_direct_sum_proof"]


def test_mixed_Kahler_Schur_bound_is_global_and_strict() -> None:
    certificate = audit.mixed_kahler_schur_certificate()
    assert certificate["H_block_minimum"] > 0.0
    assert certificate["Hc_block_minimum"] > 0.0
    assert certificate["global_operator_norm_Schur_lower_bound"] > 0.0
    assert certificate["exact_Schur_minimum"] > 0.0
    assert certificate["full_metric_minimum"] > 0.0


def test_fifth_derivative_form_has_an_all_profile_analytic_bound() -> None:
    certificate = audit.analytic_fifth_derivative_bound()
    assert certificate["analytic_all_t_lower_bound"] > 0.9
    assert certificate["dense_2001_point_crosscheck"] >= certificate[
        "analytic_all_t_lower_bound"
    ] - 2.0e-13


def test_formal_gauge_arithmetic_is_explicitly_not_a_physical_quotient() -> None:
    matrices = audit.compressed_action_matrices()
    certificate = audit.gauge_reduction_certificate(matrices)
    assert certificate["removed_source_gauge_orbit_complex_profiles"] == 22
    assert certificate["removed_link_Goldstone_coordinates"] == 184
    assert certificate["full_gauge_fixed_dimension"] == 5303
    assert certificate["full_unitary_gauge_dimension"] == 5097
    assert certificate["formal_reduced_chiral_Nambu_dimension"] == 9734
    assert certificate["unbroken_vector_zero_modes_per_generator"] == 1
    assert certificate["broken_vector_zero_modes_per_generator"] == 0
    assert certificate["link_zero_modes_per_generator"] == 0
    assert certificate["total_physical_unbroken_vector_zero_modes"] == 24
    assert not certificate["physical_465_by_22_orbit_map_constructed"]
    assert not certificate["Z_orthogonal_projector_constructed"]
    assert not certificate["coupled_endpoint_link_Rxi_Goldstone_block_constructed"]


def test_source_transport_has_one_intended_profile_and_a_uniform_heavy_gap() -> None:
    certificate = audit.source_transport_spectrum_certificate(
        audit.compressed_action_matrices()
    )
    assert certificate["intended_profiles_per_original_source"] == 1
    assert certificate["heavy_vectorlike_pairs_per_original_source"] == 4
    assert certificate["total_heavy_vectorlike_pairs"] == 1860
    assert certificate["gauge_orbit_heavy_mass_residual_against_incidence_formula"] < 1.0e-10
    assert certificate["analytic_physical_heavy_mass_lower_bound"] > 0.0
    assert certificate["additional_uncontrolled_light_profiles"] == 0


def test_report_passes_C2_but_fail_closes_physical_C3_C4() -> None:
    report = audit.build_report()
    decision = report["clause_decision"]
    assert decision["C2_same_finite_regulator"].startswith("PASS")
    assert decision["C3_same_action_variational_domain_and_self_adjointness"].startswith("PARTIAL")
    assert decision["C4_same_action_full_kinetic_positivity"].startswith("PARTIAL")
    assert "OPEN" in decision["C5_counterterm_and_matching"]
    assert "OPEN" in decision["C7_component_Wilson_matching"]
    assert not decision["G2_closed"]
    assert decision["gates_promoted"] == []
    obstruction = report["physical_identification_obstruction"]
    assert obstruction["status"] == "OPEN_FIVE_EXPLICIT_MAPS_REQUIRED"
    assert len(obstruction["missing_maps"]) == 5


def test_artifacts_are_current_hashed_and_upstreams_unchanged() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
