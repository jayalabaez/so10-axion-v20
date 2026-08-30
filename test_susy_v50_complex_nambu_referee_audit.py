from __future__ import annotations

import hashlib
import json
import math

import numpy as np

import susy_v50_complex_nambu_referee_audit as audit
import susy_v50_finite_moose_action_spec as action_spec


def matrices() -> dict:
    return action_spec.compressed_action_matrices()


def test_one_canonical_action_hash_matches_module_bytes_without_peer_dependency() -> None:
    certificate = audit.shared_action_fingerprint_certificate()
    assert certificate["canonical_hash_matches_independent_bytes"]
    assert certificate["canonical_module_sha256"] == hashlib.sha256(
        action_spec.canonical_action_bytes()
    ).hexdigest()
    assert certificate["canonical_module_sha256"] == action_spec.action_fingerprint()
    assert certificate["external_certificate_dependency"] is None
    action_spec.assert_matrix_fingerprint(matrices())
    assert action_spec.ACTION_SPEC["physical_identification_status"]["status"] == (
        "OPEN_NOT_A_V47_V49_SAME_ACTION_CERTIFICATE"
    )


def test_uniform_K_bound_is_exact_rational_and_not_a_grid_claim() -> None:
    result = audit.exact_uniform_K_certificate(matrices())
    assert "/" in result["delta_even_frobenius_square_exact"]
    assert "/" in result["delta_odd_frobenius_square_exact"]
    assert "/" in result["uniform_sigma_min_lower_bound_exact"]
    assert result["uses_grid_in_proof"] is False
    assert result["uniform_sigma_min_lower_bound"] > 0.9
    assert result["invertible_for_every_t"]
    assert "binary-rational" in result["proof"]


def test_uniform_K_bound_is_below_every_sample_as_secondary_check() -> None:
    delta_even, delta_odd = audit.fifth_derivative_blocks(matrices())
    lower = audit.exact_uniform_K_certificate(matrices())[
        "uniform_sigma_min_lower_bound"
    ]
    identity = np.eye(action_spec.N_CHANNELS)
    for point in np.linspace(0.0, 1.0, 1001):
        k0 = identity
        k0 = k0 + math.sin(math.pi * point) ** 2 * delta_even
        k0 = k0 + math.sin(2.0 * math.pi * point) * delta_odd
        actual = float(np.min(np.linalg.svd(k0, compute_uv=False)))
        assert actual + 1.0e-13 >= lower


def test_complex_collar_and_sources_have_Hermitian_Nambu_pencils() -> None:
    frozen = matrices()
    for mass_name, metric_name in (
        ("collar_M", "collar_Z"),
        ("source_M_physical", "source_Z_physical"),
        ("source_M_gauge_orbit", "source_Z_gauge_orbit"),
    ):
        result = audit.independent_nambu_certificate(
            frozen[mass_name], frozen[metric_name]
        )
        assert result["M_transpose_symmetry_residual"] < 1.0e-12
        assert result["M_maximum_imaginary_entry"] > 1.0e-6
        assert result["Z_minimum_eigenvalue"] > 0.0
        assert result["H_N_Hermitian_residual"] < 1.0e-12
        assert result["whitened_Hermitian_residual"] < 1.0e-10
        assert result["plus_minus_pairing_residual"] < 1.0e-9


def test_combined_action_operator_is_one_positive_metric_Hermitian_pencil() -> None:
    result = audit.combined_operator_certificate(matrices())
    assert result["representative_pencil_dimension"] == 138
    assert result["operator_Hermitian_residual"] < 1.0e-12
    assert result["metric_Hermitian_residual"] < 1.0e-12
    assert result["metric_minimum_eigenvalue"] > 0.0
    assert result["whitened_operator_Hermitian_residual"] < 1.0e-10


def test_full_direct_sum_metric_has_exact_5303_count_and_open_ball() -> None:
    result = audit.full_metric_certificate(matrices())
    assert result["sector_dimensions"] == {
        "collar": 704,
        "source_physical": 3987,
        "source_gauge_orbit": 198,
        "gauge_unbroken": 120,
        "gauge_broken": 110,
        "link": 184,
    }
    assert result["full_gauge_fixed_coordinate_dimension"] == 5303
    assert result["full_positive_eigenvalue_count"] == 5303
    assert result["full_minimum_from_core_spectra"] > 0.0
    assert result["certified_full_metric_lower_bound"] > 0.0
    assert result["post_perturbation_lower_bound"] > 0.0
    assert result["representative_core_dimension"] == 76


def test_mixed_Kahler_has_Schur_and_rational_Gershgorin_bounds() -> None:
    result = audit.mixed_kahler_certificate(matrices())
    assert result["H_block_minimum"] > 0.0
    assert result["Hc_block_minimum"] > 0.0
    assert result["operator_norm_Schur_lower_bound"] > 0.0
    assert result["exact_Schur_minimum"] > 0.0
    assert result["unrounded_generator_Gershgorin_lower_bound"] > 0.2
    assert "/" in result["unrounded_generator_Gershgorin_lower_bound_exact"]


def test_endpoint_auxiliaries_are_retained_positive_and_local() -> None:
    result = audit.endpoint_auxiliary_certificate(matrices())
    assert result["collar_dimension"] == 44
    assert result["node_dimension"] == 40
    assert result["retained_auxiliary_dimension"] == 4
    assert result["auxiliary_metric_minimum"] > 0.8
    assert result["host_auxiliary_coupling_norm"] > 0.0
    assert result["source_auxiliary_coupling_norm"] > 0.0
    assert result["auxiliary_to_interior_maximum"] < 1.0e-13
    for endpoint in result["endpoint_positive_metric_minima"].values():
        assert endpoint["Z"] > 0.0
        assert endpoint["W"] > 0.0
    for endpoint in result["endpoint_unrounded_Gershgorin_lower_bounds"].values():
        assert endpoint["Z"] > 0.0
        assert endpoint["W"] > 0.0


def test_all_fundamental_collar_and_source_terms_are_local() -> None:
    frozen = matrices()
    result = audit.locality_certificate(frozen)
    assert result["collar_non_nearest_neighbour_violations"] == 0
    assert result["endpoint_auxiliary_to_bulk_interior_maximum"] < 1.0e-13
    assert result["source_XP_cross_nonzero_count"] == 8
    assert result["all_fundamental_terms_site_or_nearest_neighbour"]
    assert all(
        max(frozen["collar_metadata"]["block_spectral_norms"][name]) > 0.0
        for name in ("A", "Xi", "C", "R7", "R8", "Z")
    )


def test_candidate_quotient_arithmetic_and_abstract_metric_are_sound() -> None:
    result = audit.gauge_domain_certificate(matrices())
    assert result["source_gauge_profile_Nambu_zero_count"] == 2
    assert result["unbroken_vector"]["zero_count_at_1e_minus_9"] == 1
    assert result["broken_vector"]["zero_count_at_1e_minus_9"] == 0
    assert result["link_Rxi"]["zero_count_at_1e_minus_9"] == 0
    assert result["removed_source_gauge_orbit_profiles"] == 22
    assert result["removed_link_Goldstones"] == 184
    assert result["full_gauge_fixed_dimension"] == 5303
    assert result["full_gauge_reduced_dimension"] == 5097
    assert "inherits strict positivity" in result["quotient_proof"]
    assert "requires the missing explicit orbit map" in result["quotient_proof"]


def test_report_passes_abstract_witness_but_fail_closes_physical_C3_C4() -> None:
    report = audit.build_report()
    decision = report["clause_decision"]
    assert decision["abstract_finite_matrix_C3_witness"] == "PASS"
    assert decision["abstract_finite_matrix_C4_witness"] == "PASS"
    assert decision["C3_physical_same_action_domain_and_self_adjointness"] == (
        "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
    )
    assert decision["C4_physical_full_kinetic_positivity"] == (
        "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
    )
    assert decision["C5_counterterm_and_profile_matching"] == "REMAINS_PARTIAL"
    assert decision["C7_component_Wilson_matching"] == "REMAINS_PARTIAL"
    assert decision["G2_closed"] is False
    assert decision["gates_promoted"] == []
    assert len(report["physical_identification_obstructions"]) == 5
    assert report["canonical_action_fingerprint"]["external_certificate_dependency"] is None
    assert report["n_failed_integrity_checks"] == 0


def test_report_hash_is_deterministic() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["shared_action_sha256"] == action_spec.SHARED_ACTION_SHA256


def test_checked_artifacts_are_current() -> None:
    report = audit.build_report()
    audit.validate(report)
    audit.check_artifacts(report)
    stored = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == report["core_sha256"]
