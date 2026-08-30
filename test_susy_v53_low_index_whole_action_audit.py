from __future__ import annotations

import json

import numpy as np

import susy_v52_low_index_source_audit as source
import susy_v53_low_index_whole_action_audit as audit


EXPECTED_CORE_SHA256 = (
    "9218b06e866c00dcc6e3348751ace04fea2e1958cb6fe046fc5c9b912896bcb8"
)
EXPECTED_ELEMENTARY_H_SHA256 = (
    "6502a532aabf301ab17accf3ab880ff8d89b158bffb2d936e3b1ffe5ee37615b"
)
EXPECTED_HYBRID_H_SHA256 = (
    "c80273c42753cceaed5a5d990cf4fceca1772dd00d49cae6040bde670f50620b"
)


def test_upstreams_are_bound_without_cross_action_promotion() -> None:
    binding = audit.upstream_binding()
    assert binding["source"]["coordinates"] == 131
    assert binding["source"]["H_rank"] == 98
    assert binding["source"]["Q_rank"] == 33
    assert binding["minimal_repair"]["H10_count"] == 1
    assert binding["minimal_repair"]["singlet_count"] == 4
    assert binding["nonlinear_hybrid"]["coordinates"] == 176


def test_matter_singlet_block_has_rank7_and_45_light_matter_modes() -> None:
    matrix = audit.matter_singlet_hessian()
    assert matrix.shape == (52, 52)
    assert np.array_equal(matrix, matrix.T)
    assert source.modular_rank(source._modular_matrix(matrix)) == 7
    assert matrix.shape[0] - source.modular_rank(source._modular_matrix(matrix)) == 45
    for family, coefficient in enumerate((10, 20, 30)):
        assert matrix[16 * family + 15, 48 + family] == coefficient
    assert matrix[51, 51] == 4000


def test_H10_block_has_triplet_rank6_and_weak_nullity4() -> None:
    matrix = audit.higgs_hessian()
    assert matrix.shape == (10, 10)
    assert list(np.diag(matrix).real.astype(int)) == [5] * 6 + [0] * 4
    assert source.modular_rank(source._modular_matrix(matrix)) == 6


def test_elementary_193_Hessian_kernel_is_exactly_gauge_plus49_light() -> None:
    hessian, orbit = audit.elementary_whole_hessian_and_orbit()
    light = audit.intended_light_kernel(True)
    combined = np.column_stack((orbit, light))
    assert hessian.shape == (193, 193)
    assert orbit.shape == (193, 45)
    assert light.shape == (193, 49)
    assert source.modular_rank(source._modular_matrix(hessian)) == 111
    assert source.modular_rank(source._modular_matrix(orbit)) == 33
    assert source.modular_rank(source._modular_matrix(light)) == 49
    assert source.modular_rank(source._modular_matrix(combined)) == 82
    assert np.count_nonzero(hessian @ orbit) == 0
    assert np.count_nonzero(hessian @ light) == 0
    assert 111 + 82 == 193
    assert source.gaussian_matrix_sha(hessian) == EXPECTED_ELEMENTARY_H_SHA256


def test_optional_238_hybrid_kernel_is_exactly_gauge_plus49_light() -> None:
    hessian, orbit = audit.hybrid_whole_hessian_and_orbit()
    light = audit.intended_light_kernel(False)
    combined = np.column_stack((orbit, light))
    assert hessian.shape == (238, 238)
    assert orbit.shape == (238, 66)
    assert light.shape == (238, 49)
    assert source.modular_rank(source._modular_matrix(hessian)) == 135
    assert source.modular_rank(source._modular_matrix(orbit)) == 54
    assert source.modular_rank(source._modular_matrix(combined)) == 103
    assert np.count_nonzero(hessian @ combined) == 0
    assert 135 + 103 == 238
    assert source.gaussian_matrix_sha(hessian) == EXPECTED_HYBRID_H_SHA256


def test_Abelian_selector_cannot_enforce_the_DT_coefficient_relation() -> None:
    certificate = audit.natural_dt_obstruction()
    selector = certificate["ordinary_Abelian_selector_no_go"]
    assert selector["charge_equations"].startswith("2 qE=0 and 3 qE=0")
    assert selector["consequence"] == "H^2 and H E H both carry charge 2 qH"
    assert not selector["can_enforce_mH_equals_3kH"]
    tuned = certificate["tuned_block"]
    assert tuned["codimension"] == 1
    assert tuned["unit_perturbation_mH_3_to_4_gives_rank"] == 10


def test_existing_E_A_and_singlets_do_not_supply_a_missing_weak_eigenvalue() -> None:
    tests = audit.natural_dt_obstruction()["existing_field_missing_eigenvalue_tests"]
    assert tests["E0_rank"] == 10
    assert tests["E0_determinant"] == 5184
    assert tests["A0_rank"] == 10
    assert tests["A0_determinant"] == 81
    assert tests["A0_plane_coefficients"] == [1, 1, 1, 3, 3]
    assert not tests["A0_has_DW_missing_weak_entry"]
    assert tests["one_H_transpose_A_H_identically_zero"]
    assert not tests["singlets_can_distinguish_triplet_from_doublet"]
    assert tests["two_H_A0_only_block_rank"] == 20


def test_alternatives_are_not_mislabeled_same_action_solutions() -> None:
    alternatives = audit.alternative_route_stress_test()
    missing = alternatives["extended_missing_VEV_same_gauge_group"]
    assert missing["minimum_new_non_singlet_coordinates"] == 109
    assert missing["with_second_10_new_non_singlet_coordinates"] == 119
    assert missing["Landau_b_sumT_minus3C2_range"] == [23, 24]
    assert missing["decision"].endswith("not an exact V53 completion")
    assert alternatives["flipped_Spin10_times_U1X"]["decision"].startswith("not a same-lineage")
    assert alternatives["product_group"]["decision"] == "research alternative only"
    bpt = alternatives["Babu_Pati_Tavartkiladze_single_adjoint_U1A"]
    assert bpt["Higgs_complex_coordinates"] == 131
    assert bpt["with_three_matter_16_coordinates"] == 179
    assert bpt["Spin10_Dynkin_index"] == {
        "Higgs": 18,
        "three_families": 6,
        "sum": 24,
        "b_Landau_sumT_minus3C2": 0,
    }
    assert bpt["naive_exact_Hessian_target"]["broken_gauge_orbit_if_U1A_fully_included"] == 34
    assert bpt["naive_exact_Hessian_target"]["131_coordinate_Higgs_rank_needed_if_no_physical_modulus"] == 97
    assert "replacement action" in bpt["decision"]


def test_elementary_running_is_wide_but_excludes_future_naturalizer() -> None:
    certificate = audit.perturbativity_certificate(0.73)
    elementary = certificate["elementary_whole_action"]
    assert elementary["sum_T"] == 31
    assert elementary["b_Landau"] == 7
    assert elementary["b_asymptotic_freedom"] == -7
    assert elementary["pole_over_matching_scale"] > 1.0e9
    assert "23-24" in certificate["natural_missing_VEV_cost"]


def test_report_passes_local_rank_but_fail_closes_completeness_and_G2() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    gate = report["gate_effect"]
    assert gate["C1"].startswith("PARTIAL")
    assert gate["C3"].startswith("LOCAL_WHOLE_ACTION_PASS")
    assert gate["C4"].startswith("PARTIAL")
    assert gate["C5"].startswith("OPEN")
    assert gate["C6"].startswith("PARTIAL")
    assert gate["C7"].startswith("OPEN")
    assert gate["G2"] == "OPEN"
    assert gate["gates_promoted"] == []


def test_artifacts_are_current_and_hashed() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == EXPECTED_CORE_SHA256
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["files"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
