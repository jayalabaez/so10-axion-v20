from __future__ import annotations

import cmath
import json
import math

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_resolved_source_wall_audit as audit


def test_source_matrix_is_the_v47_theta_sigma_matrix_on_the_CP_real_slice() -> None:
    candidate = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    upstream = v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    assert audit.max_difference(candidate, upstream) == 0.0
    assert v47.is_hermitian(candidate)
    assert candidate == [
        [0j, 0.4 + 0j, 0.2 + 0j, 0j],
        [0.4 + 0j, 0j, 0j, -0.15 + 0j],
        [0.2 + 0j, 0j, 0j, 0.6 + 0j],
        [0j, -0.15 + 0j, 0.6 + 0j, 0j],
    ]


def test_source_collar_profile_preserves_the_V47_four_dimensional_normalization() -> None:
    length = 1.0
    epsilon = 0.05
    assert audit.collar_profile(0.5, length, epsilon) == 0.0
    assert audit.collar_profile(0.975, length, epsilon) == 1.0 / epsilon
    assert audit.constant_source_mode_norm(epsilon) == 1.0
    report = audit.build_report()
    normalization = report["numerical_certificate"]["source_collar_normalization"]
    assert normalization["rho_epsilon_inside"] == 20.0
    assert normalization["integral_rho_epsilon_dy"] == 1.0
    assert normalization["constant_mode_Kahler_multiplier"] == 1.0
    assert normalization["scaled_y_stiffness_weight_rho_epsilon_epsilon_squared"] == epsilon
    collar = report["microscopic_regulator"]["dynamical_source_collar"]
    assert "rho_epsilon" in collar["action"]
    assert "four-dimensional chiral dimension one" in collar["dimensions"]


def test_general_complex_holomorphic_source_has_a_hermitian_nambu_lift() -> None:
    holomorphic = [
        [0.0j, 0.4 + 0.2j, 0.0j, 0.0j],
        [0.4 + 0.2j, 0.0j, 0.0j, 0.0j],
        [0.0j, 0.0j, 0.0j, 0.6 - 0.1j],
        [0.0j, 0.0j, 0.6 - 0.1j, 0.0j],
    ]
    lifted = audit.nambu_source_matrix(holomorphic)
    assert len(lifted) == 8
    assert v47.is_hermitian(lifted)


def test_entire_matrix_functions_match_scalar_cosh_and_sinhc() -> None:
    for value in (-1.7, -0.2, 0.0, 0.4, 2.3):
        argument = [[complex(value)]]
        obtained_d = audit.analytic_even_series(argument, sinhc=False)[0][0]
        obtained_h = audit.analytic_even_series(argument, sinhc=True)[0][0]
        root = cmath.sqrt(value)
        expected_d = cmath.cosh(root)
        expected_h = 1.0 + 0.0j if value == 0.0 else cmath.sinh(root) / root
        assert abs(obtained_d - expected_d) < 3.0e-14
        assert abs(obtained_h - expected_h) < 3.0e-14


def test_exact_zero_energy_map_is_Lambda_for_every_positive_width() -> None:
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    for epsilon in (1.0, 0.2, 0.01, 1.0e-5):
        boundary = audit.boundary_map(0.0, epsilon, source)
        assert audit.max_difference(boundary, source) < 2.0e-14


def test_linear_and_quadratic_derivative_coefficients_are_exact_Taylor_data() -> None:
    epsilon = 0.07
    source = audit.source_matrix(0.35, 0.52, -0.17, 0.11, su5_singlet=True)
    z_boundary = audit.induced_boundary_kinetic(epsilon, source)
    y_boundary = audit.second_derivative_coefficient(epsilon, source)
    step = 1.0e-3
    b_plus = audit.boundary_map(step, epsilon, source)
    b_minus = audit.boundary_map(-step, epsilon, source)
    first_numerical = audit.matrix_scale(1.0 / (2.0 * step), audit.matrix_add(b_plus, audit.matrix_scale(-1.0, b_minus)))
    second_numerical = audit.matrix_scale(
        1.0 / (2.0 * step * step),
        audit.matrix_add(
            audit.matrix_add(b_plus, b_minus),
            audit.matrix_scale(-2.0, source),
        ),
    )
    assert audit.max_difference(first_numerical, audit.matrix_scale(-1.0, z_boundary)) < 2.0e-10
    assert audit.max_difference(second_numerical, y_boundary) < 2.0e-9


def test_induced_boundary_kinetic_matrix_has_the_positive_slab_norm() -> None:
    epsilon = 0.05
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    z_boundary = audit.induced_boundary_kinetic(epsilon, source)
    vectors = (
        (1.0, 0.0, 0.0, 0.0),
        (1.0, -0.4, 0.7, 0.2),
        (-0.3, 0.2, 1.4, -0.8),
    )
    for vector in vectors:
        source_vector = [
            sum(source[row][column] * vector[column] for column in range(4))
            for row in range(4)
        ]
        direct = epsilon * (
            sum(value * value for value in vector)
            + sum(abs(value) ** 2 for value in source_vector) / 3.0
        )
        quadratic = audit.quadratic_form(vector, z_boundary)
        assert math.isclose(quadratic, direct, rel_tol=2.0e-14, abs_tol=2.0e-14)
        assert quadratic >= epsilon * sum(value * value for value in vector)


def test_wall_transfer_is_J_unitary_for_real_mass_and_hermitian_source() -> None:
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    for signed_mass in (-2.0, -0.4, 0.0, 0.37, 1.8):
        transfer = audit.wall_transfer(signed_mass, 0.05, source)["T"]
        assert audit.j_unitarity_residual(transfer) < 3.0e-13


def test_pole_free_characteristic_equals_D_times_effective_characteristic() -> None:
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    bulk_masses = (0.2, -0.4, 0.8, -0.1)
    for even in (v47.E_LEFT, v47.E_RIGHT):
        for signed_mass in (-1.2, -0.1, 0.0, 0.37, 1.1):
            resolved = audit.resolved_characteristic_matrix(
                signed_mass, bulk_masses, 1.0, 0.05, source, even
            )
            effective = audit.effective_characteristic_matrix(
                signed_mass, bulk_masses, 1.0, 0.05, source, even
            )
            d_block = audit.wall_transfer(signed_mass, 0.05, source)["D"]
            assert audit.max_difference(resolved, audit.matrix_multiply(d_block, effective)) < 4.0e-13


def test_resolved_characteristic_converges_to_the_v47_characteristic() -> None:
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    masses = (0.2, -0.4, 0.8, -0.1)
    signed_mass = 0.37
    target = v47.characteristic_matrix(signed_mass, masses, 1.0, source, v47.E_RIGHT)
    errors = []
    for epsilon in (0.1, 0.05, 0.02, 0.01, 0.005):
        finite = audit.resolved_characteristic_matrix(
            signed_mass, masses, 1.0, epsilon, source, v47.E_RIGHT
        )
        errors.append(audit.max_difference(finite, target))
    assert all(later < earlier for earlier, later in zip(errors, errors[1:]))
    assert errors[-1] < 0.06 * errors[0]


def test_resolved_wall_retains_the_v47_no_zero_theorem() -> None:
    source = audit.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    non_singlet = audit.source_matrix(0.4, 0.6, 0.0, 0.0, su5_singlet=False)
    assert v47.zero_mode_nullity(non_singlet, v47.E_LEFT) == 0
    assert v47.zero_mode_nullity(non_singlet, v47.E_RIGHT) == 0
    assert v47.zero_mode_nullity(source, v47.E_RIGHT) == 0
    for epsilon in (0.2, 0.05, 0.01):
        assert audit.max_difference(audit.boundary_map(0.0, epsilon, source), source) < 2.0e-14


def test_report_is_explicit_but_fail_closed_on_universality_and_gate_status() -> None:
    report = audit.build_report()
    decision = report["decision"]
    assert decision["explicit_supersymmetric_resolved_regulator_exists"]
    assert decision["bare_to_Wilsonian_boundary_map_exact_in_declared_scheme"]
    assert decision["induced_boundary_kinetic_and_derivative_tower_included"]
    assert decision["fundamental_problem_self_adjoint_and_positive"]
    assert decision["thin_wall_reproduces_V47_characteristic"]
    assert not decision["regulator_independent_map_proved"]
    assert not decision["S2_closed"]
    assert not decision["G2_closed_by_this_subaudit"]
    assert decision["gates_promoted"] == []


def test_hashed_artifacts_are_current_and_upstream_is_unchanged() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
