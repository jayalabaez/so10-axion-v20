from __future__ import annotations

import json
import math

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_resolved_source_wall_audit as v48
import susy_v49_fixed_profile_source_regulator_audit as audit


def test_source_multiplets_are_strictly_four_dimensional_with_no_KK_label() -> None:
    report = audit.build_report()
    source = report["strictly_4D_source_action"]
    assert source["fields"] == list(audit.SOURCE_FIELDS)
    assert "not y" in source["no_source_KK_tower"]
    certificate = report["numerical_certificate"]
    assert certificate["source_field_count_with_y_dependence"] == 0
    assert not certificate["source_KK_tower_present"]


def test_one_sided_and_doubled_profiles_have_unit_normalization() -> None:
    epsilon = 0.05
    length = 1.0
    assert audit.normalized_square_profile(0.975, length, epsilon) == 1.0 / epsilon
    assert audit.normalized_square_profile(0.8, length, epsilon) == 0.0
    assert audit.doubled_orbifold_profile(0.02, epsilon) == 1.0 / (2.0 * epsilon)
    assert audit.doubled_orbifold_profile(-0.02, epsilon) == 1.0 / (2.0 * epsilon)
    assert audit.doubled_orbifold_profile(0.08, epsilon) == 0.0
    assert audit.square_profile_moment(epsilon, 0) == 1.0
    assert audit.square_profile_moment(epsilon, 0, doubled_orbifold=True) == 1.0


def test_even_orbifold_profile_kills_all_odd_moments_exactly() -> None:
    epsilon = 0.13
    for power in (1, 3, 5, 7):
        assert audit.square_profile_moment(epsilon, power, doubled_orbifold=True) == 0.0
    for power in (0, 2, 4, 6):
        expected = epsilon**power / (power + 1)
        assert math.isclose(
            audit.square_profile_moment(epsilon, power, doubled_orbifold=True),
            expected,
            rel_tol=0.0,
            abs_tol=2.0e-16,
        )


def test_fixed_slope_profile_moments_before_strong_wall_dynamics() -> None:
    epsilon = 0.07
    values = audit.smeared_near_endpoint_bilinears(epsilon, 1.2, -0.3, 0.7)
    assert values["H_Hc"] == 0.0j
    assert values["leading_H_Hc"] == 0.0j
    assert math.isclose(values["Hc_Hc"].real, 0.7**2 * epsilon**2 / 3.0, rel_tol=2.0e-15)
    half_width = audit.smeared_near_endpoint_bilinears(epsilon / 2.0, 1.2, -0.3, 0.7)
    assert math.isclose(half_width["Hc_Hc"].real / values["Hc_Hc"].real, 0.25, rel_tol=2.0e-15)


def test_fixed_slope_odd_profile_moment_before_strong_wall_dynamics() -> None:
    epsilon = 0.07
    value = audit.odd_profile_mixed_bilinear(epsilon, 1.2, 0.7)
    assert math.isclose(value.real, 1.2 * 0.7 * epsilon / 3.0, rel_tol=2.0e-15)
    half_width = audit.odd_profile_mixed_bilinear(epsilon / 2.0, 1.2, 0.7)
    assert math.isclose(half_width.real / value.real, 0.5, rel_tol=2.0e-15)


def test_exact_strong_collar_cancels_naive_epsilon_suppression() -> None:
    first = audit.strong_collar_leading_bilinears(0.07, 1.2, 0.4)
    second = audit.strong_collar_leading_bilinears(0.035, 1.2, 0.4)
    assert first == second
    assert math.isclose(first["Hc_Hc_even_profile"].real, 1.2**2 * 0.4**2 / 3.0)
    assert math.isclose(first["H_Hc_odd_sign_profile"].real, -(1.2**2) * 0.4 / 2.0)
    assert math.isclose(first["H_Hc_odd_linear_profile"].real, -(1.2**2) * 0.4 / 3.0)


def test_fixed_profile_uses_the_exact_V48_source_matrix_and_boundary_map() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    report = audit.build_report()
    assert report["numerical_certificate"]["Lambda"] == audit._real_matrix(source)
    boundary = v48.boundary_map(0.37, 0.05, source)
    assert report["numerical_certificate"]["B_epsilon_at_sample_mass"] == audit._real_matrix(boundary)


def test_exact_resolved_pencil_retains_J_unitarity_and_D_factorization() -> None:
    report = audit.build_report()
    certificate = report["numerical_certificate"]
    assert certificate["wall_J_unitarity_residual"] < 2.0e-12
    assert certificate["K_res_minus_D_K_eff_residual"] < 2.0e-12


def test_zero_energy_map_and_no_exotic_zero_modes_survive() -> None:
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    for epsilon in (0.2, 0.05, 0.01):
        assert v48.max_difference(v48.boundary_map(0.0, epsilon, source), source) < 2.0e-14
    report = audit.build_report()
    assert report["numerical_certificate"]["total_exotic_chiral_zero_modes"] == 0


def test_gauge_covariance_and_quadratic_variation_contract_are_explicit() -> None:
    report = audit.build_report()
    smearing = report["gauge_covariant_fixed_smearing"]
    assert "g_R(L)" in smearing["gauge_law"]
    assert "Spin(10)xU(1)F invariant" in smearing["local_gauge_statement"]
    variation = report["variation_and_quadratic_reduction"]
    assert "cubic" in variation["delta_Wilson_line"]
    assert "H=0" in variation["vacuum"]


def test_Hc_power_counting_does_not_claim_a_symmetry_for_Hc_Hc() -> None:
    report = audit.build_report()
    power = report["Hc_and_mixed_operator_power_counting"]
    exact = power["exact_m0_strong_collar"]
    assert "zero" in exact["even_profile_H_Hc"]
    assert "O(1)" in exact["odd_sign_profile_H_Hc"]
    assert "O(1)" in exact["even_profile_Hc_Hc"]
    assert "inconsistent" in power["naive_smooth_profile_warning"]
    assert "zero is not symmetry-enforced" in power["candidate_matching_input"]
    assert "may generate" in power["radiative_statement"]
    assert "different singular regulator" in power["excluded_singular_scalings"]


def test_report_closes_only_the_regulator_candidate_and_not_G2() -> None:
    report = audit.build_report()
    decision = report["decision"]
    assert decision["strictly_4D_source_regulator_defined"]
    assert decision["gauge_covariant_smearing_defined"]
    assert decision["extra_source_KK_tower_absent"]
    assert decision["explicit_finite_resolution_tree_prescription_defined"]
    assert decision["exact_finite_epsilon_H_boundary_pencil_retained_only_at_zero_counterterm_point"]
    assert decision["strong_collar_Hc_terms_unsuppressed"]
    assert decision["odd_profile_normal_derivative_counterterm_required"]
    assert not decision["regulator_microscopic_candidate_condition_closed"]
    assert not decision["point_local_5D_regulator_defined"]
    assert not decision["point_local_5D_UV_completion_proved"]
    assert not decision["complete_boundary_EFT_basis_proved_here"]
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
