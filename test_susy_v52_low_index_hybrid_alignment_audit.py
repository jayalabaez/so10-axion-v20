from __future__ import annotations

import json

import numpy as np
import sympy as sp

import susy_v52_low_index_hybrid_alignment_audit as audit
import susy_v52_low_index_source_audit as source


EXPECTED_CORE_SHA256 = (
    "234442c35dfee6c0374b5562ac6e42a9674d54f6dc985f1d982d32207ea46365"
)
EXPECTED_H_SHA256 = (
    "1a33e5069aa6165f9973ba34f07bd9183c9bf1dbe5e53ce3697919a07c9dfc2c"
)
EXPECTED_Q_SHA256 = (
    "6613b9208a75cfe0405ceb599e53281d7d0f100a9744d5a67b0635693231f237"
)


def test_low_index_source_binding_is_exact_and_isolated() -> None:
    binding = audit.source_binding()
    assert binding["F_terms_all_zero"]
    assert binding["D_terms_all_zero"]
    assert binding["coordinates"] == 131
    assert binding["orbit_rank"] == 33
    assert binding["stabilizer_dimension"] == 12
    assert binding["source_Hessian_rank"] == 98
    assert binding["source_Hessian_nullity"] == 33
    assert binding["source_kernel_equals_orbit"]
    assert binding["source_sum_T"] == 24


def test_E0_affine_identity_puts_source_SM_inside_host_PS() -> None:
    certificate = audit.endpoint_partition_certificate()
    assert certificate["affine_identity_holds"]
    assert certificate["source_stabilizer_is_subalgebra_of_PS"]
    assert certificate["dimensions"] == {
        "PS_intersection_source_SM": 12,
        "PS_only": 9,
        "source_SM_only": 0,
        "neither": 24,
    }
    assert certificate["sum"] == 45


def test_source_order_parameter_alignment_map_is_exact_rank24() -> None:
    link_map = audit.alignment_map()
    gram = link_map.T @ link_map
    assert link_map.shape == (100, 45)
    assert source.modular_rank(source._modular_matrix(link_map)) == 24
    diagonal = np.diag(gram)
    assert np.count_nonzero(diagonal == 200) == 24
    assert np.count_nonzero(diagonal == 0) == 21
    assert np.count_nonzero(gram - np.diag(diagonal)) == 0


def test_hybrid_incidence_has_24_residuals_and_alignment_lifts_them() -> None:
    incidence, alignment = audit.hybrid_goldstone_incidence()
    assert incidence.shape == (78, 66)
    assert np.linalg.matrix_rank(incidence) == 54
    assert incidence.shape[1] - np.linalg.matrix_rank(incidence) == 12
    assert incidence.shape[0] - np.linalg.matrix_rank(incidence) == 24
    assert alignment.shape == (24, 78)
    assert np.linalg.matrix_rank(alignment) == 24
    assert np.count_nonzero(alignment @ incidence) == 0
    combined = incidence @ incidence.T + alignment.T @ alignment
    assert np.linalg.matrix_rank(combined) == 78
    assert int(sp.Matrix(combined.tolist()).det()) == 2**60


def test_full_176_hessian_has_kernel_exactly_equal_to_gauge_orbit() -> None:
    hessian, orbit, alignment_map = audit.full_hessian_and_orbit_numerators()
    assert hessian.shape == (176, 176)
    assert orbit.shape == (176, 66)
    assert alignment_map.shape == (100, 176)
    assert np.array_equal(hessian, hessian.T)
    assert source.modular_rank(source._modular_matrix(hessian)) == 122
    assert source.modular_rank(source._modular_matrix(orbit)) == 54
    assert source.modular_rank(source._modular_matrix(alignment_map)) == 24
    assert np.count_nonzero(hessian @ orbit) == 0
    assert 122 + 54 == 176
    assert source.gaussian_matrix_sha(hessian) == EXPECTED_H_SHA256
    assert source.gaussian_matrix_sha(orbit) == EXPECTED_Q_SHA256


def test_alignment_is_gauge_invariant_local_but_not_elementary_renormalizable() -> None:
    certificate = audit.exact_hybrid_certificate()["alignment_action"]
    assert certificate["definition"].startswith("C=[P,U E U^T]")
    assert certificate["holomorphic"]
    assert "C->h C h^T" in certificate["host_PS_covariance"]
    assert "source-gauge invariant" in certificate["source_Spin10_covariance"]
    assert "single V52 edge" in certificate["theory_space_locality"]
    assert not certificate["renormalizable_elementary_link_completion"]


def test_running_proxy_moves_pole_above_sigma_cutoff() -> None:
    certificate = audit.perturbativity_certificate(0.73)
    assert certificate["components"] == {
        "54_plus_45_plus_16_plus_bar16": 24,
        "nonlinear_link_adjoint_tangent_proxy": 8,
        "four_transport_spinors": 8,
        "three_16_families_plus_one_10H_if_colocated": 7,
        "alignment_extra_index": 0,
    }
    same = certificate[
        "same_inventory_as_V51_source_site_except_source_and_link_replaced"
    ]
    assert same["sum_T"] == 40
    assert same["b"] == -16
    assert same["b_asymptotic_freedom__3C2_minus_sumT"] == -16
    assert same["b_Landau__sumT_minus_3C2"] == 16
    assert same["pole_over_matching_scale"] > 10000
    visible = certificate["including_colocated_visible_families_and_10H"]
    assert visible["sum_T"] == 47
    assert visible["b"] == -23
    assert visible["b_asymptotic_freedom__3C2_minus_sumT"] == -23
    assert visible["b_Landau__sumT_minus_3C2"] == 23
    assert visible["pole_over_matching_scale"] > 600
    assert visible["pole_over_matching_scale"] > certificate[
        "nonlinear_sigma_NDA_cutoff_over_vector_mass"
    ]


def test_report_is_strong_locally_but_fail_closed_globally() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    gate = report["gate_effect"]
    assert gate["V51_link_multiplier_blocker"].startswith("REPAIRED")
    assert gate["V51_residual_A5_blocker"].startswith("REPAIRED")
    assert gate["C2"].startswith("NEW_ACTION")
    assert gate["C3"].startswith("PARTIAL")
    assert gate["C4"].startswith("PARTIAL")
    assert gate["C5"].startswith("OPEN_FOR_NEW_ACTION")
    assert gate["C6"].startswith("UNASSESSED_FOR_NEW_ACTION")
    assert gate["C7"].startswith("OPEN_FOR_NEW_ACTION")
    assert gate["candidate_UV_viability"].startswith("PARTIAL_EFT_ONLY")
    assert not gate["G2_closed"]
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
