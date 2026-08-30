from __future__ import annotations

import json
import math

import susy_v48_resolved_source_wall_audit as v48
import susy_v50_local_constrained_transport_regulator_audit as audit


def test_trapezoid_weights_are_positive_and_exactly_normalized() -> None:
    for cells in (1, 2, 3, 8, 17):
        weights = audit.trapezoid_weights(cells)
        assert len(weights) == cells + 1
        assert min(weights) > 0.0
        assert math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=2.0e-15)


def test_constraint_jacobian_is_triangular_with_link_independent_unit_determinant() -> None:
    for ratios in (
        [2.0],
        [1.1 + 0.2j, -0.4 + 0.3j],
        [0.7, -2.3j, 4.1 - 0.8j, -0.2],
    ):
        jacobian = audit.scalar_constraint_jacobian(len(ratios), ratios)
        assert abs(audit.determinant(jacobian) - 1.0) < 2.0e-14
        assert all(jacobian[index][index] == 1.0 for index in range(len(ratios)))


def test_recursive_transport_is_exactly_gauge_covariant() -> None:
    links = [audit.rotation(0.13), audit.rotation(-0.21), audit.rotation(0.34)]
    gauges = [audit.rotation(0.17), audit.rotation(-0.29), audit.rotation(0.11), audit.rotation(0.37)]
    residual = audit.gauge_covariance_residual([0.7, -0.2], links, gauges)
    assert residual < 2.0e-13


def test_positive_completion_has_one_source_zero_and_N_heavy_pairs() -> None:
    for cells in (1, 2, 4, 9):
        incidence = audit.incidence_matrix(cells)
        assert len(incidence) == cells
        assert len(incidence[0]) == cells + 1
        masses = audit.transport_singular_values(cells, 3.0)
        assert len(masses) == cells
        assert min(masses) > 0.0
        expected_product_squared = (3.0 ** (2 * cells)) * (cells + 1)
        actual_product_squared = math.prod(value * value for value in masses)
        assert math.isclose(actual_product_squared, expected_product_squared, rel_tol=3.0e-13)


def test_source_component_count_is_preserved_exactly() -> None:
    report = audit.build_report()
    certificate = report["numerical_certificate"]
    assert sum(audit.SOURCE_DIMENSIONS.values()) == 465
    assert certificate["transport_zero_profile_count_per_original_component"] == 1
    assert certificate["original_source_component_count"] == 465
    assert certificate["intended_source_component_zero_modes"] == 465
    assert certificate["heavy_vectorlike_chiral_pairs"] == 4 * 465


def test_smallest_one_link_completion_is_explicit_and_cutoff_gapped() -> None:
    epsilon = 0.05
    masses = audit.transport_singular_values(1, 1.0 / epsilon)
    assert len(masses) == 1
    assert math.isclose(masses[0], math.sqrt(2.0) / epsilon, rel_tol=2.0e-15)


def test_open_gauge_moose_has_only_the_intended_diagonal_zero() -> None:
    for cells in (1, 3, 8):
        masses = audit.vector_masses(cells, 0.7, 5.0)
        assert abs(masses[0]) < 1.0e-15
        assert sum(abs(value) < 1.0e-13 for value in masses) == 1
        assert min(masses[1:]) > 0.0


def test_local_layered_transfer_is_symplectic_at_every_finite_N() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    for cells in (1, 2, 4, 8, 16):
        transfer = audit.layered_transfer(cells, 0.37, 0.05, source)
        assert v48.j_unitarity_residual(transfer) < 1.0e-12


def test_zero_energy_boundary_map_is_exact_at_every_finite_N() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    for cells in (1, 2, 3, 8, 17):
        boundary = audit.layered_boundary_map(cells, 0.0, 0.05, source)
        assert v48.max_difference(boundary, source) < 2.0e-13


def test_layered_transfer_converges_quadratically_to_square_collar() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    exact = v48.wall_transfer(0.37, 0.05, source)["T"]
    errors = [
        v48.max_difference(audit.layered_transfer(cells, 0.37, 0.05, source), exact)
        for cells in (1, 2, 4, 8, 16)
    ]
    assert all(first > second for first, second in zip(errors[:-1], errors[1:]))
    assert all(first / second > 3.8 for first, second in zip(errors[:-1], errors[1:]))


def test_local_boundary_map_converges_to_exact_resolved_map() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    exact = v48.boundary_map(0.37, 0.05, source)
    errors = [
        v48.max_difference(audit.layered_boundary_map(cells, 0.37, 0.05, source), exact)
        for cells in (1, 2, 4, 8, 16)
    ]
    assert all(first > second for first, second in zip(errors[:-1], errors[1:]))
    assert errors[-1] < 3.0e-6


def test_profile_quadrature_has_second_order_error() -> None:
    errors = [abs(audit.quadratic_profile_average(cells) - 1.0 / 3.0) for cells in (1, 2, 4, 8)]
    assert all(math.isclose(first / second, 4.0, rel_tol=2.0e-14) for first, second in zip(errors[:-1], errors[1:]))


def test_G1_is_preserved_but_only_C2_is_promoted() -> None:
    report = audit.build_report()
    anomaly = report["G1_anomaly_audit"]
    assert "vectorlike" in anomaly["interior_pairs"]
    assert "G1 remains closed" in anomaly["conclusion"]
    decision = report["decision"]
    assert decision["G1_anomaly_closure_preserved"]
    assert decision["C2_explicit_regulator_passes"]
    assert decision["clauses_promoted"] == ["C2"]
    assert not decision["point_local_continuum_5D_UV_completion_proved"]
    assert not decision["complete_full_action_domain_proved"]
    assert not decision["G2_closed_by_this_subaudit"]
    assert decision["gates_promoted"] == []


def test_no_hidden_bilocal_vertex_or_uncontrolled_auxiliary_poles_are_claimed() -> None:
    report = audit.build_report()
    local = report["finite_local_construction"]
    elimination = report["variation_and_exact_elimination"]
    assert "no product" in local["locality"]
    assert "only after" in elimination["effective_solution"]
    certificate = report["numerical_certificate"]
    assert certificate["source_replica_propagating_poles_in_exact_auxiliary_limit"] == 0
    assert certificate["additional_massless_source_profiles_in_positive_completion"] == 0


def test_hashed_artifacts_are_current_and_upstream_is_unchanged() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
