from __future__ import annotations

import json

import sympy as sp

import susy_v52_lean_nonlinear_alignment_audit as audit


EXPECTED_CORE_SHA256 = (
    "e8bf5bc17469e2e463fa12828278bcb957529a2de3d1cdc588cb8029c4c610ab"
)


def test_endpoint_projectors_are_exact_and_resolve_the_45() -> None:
    certificate = audit.projector_incidence_certificate()
    assert certificate["n_failed_checks"] == 0
    assert all(certificate["checks"].values())
    assert certificate["centralizer_dimensions"] == {
        "PS": 21,
        "U5": 25,
        "SU5_after_source_phase_breaks_U1": 24,
    }
    assert certificate["simultaneous_incidence_dimensions"] == {
        "PS_intersection_SU5__SM": 12,
        "PS_only": 9,
        "SU5_only": 12,
        "neither": 12,
    }
    assert certificate["incidence_sum"] == 45


def test_alignment_map_is_exactly_the_neither_projector() -> None:
    linear_map = audit.alignment_linear_map()
    projectors = audit.endpoint_projectors()
    gram = linear_map.T * linear_map
    assert linear_map.shape == (100, 45)
    assert linear_map.rank() == 12
    assert gram == 32 * projectors["neither"]
    assert gram.rank() == 12
    assert 45 - gram.rank() == 33


def test_alignment_function_has_endpoint_gauge_covariance() -> None:
    report = audit.build_report()
    contract = report["alignment_and_spectrum"]["holomorphic_alignment"]
    assert contract["definition"].startswith("C=[P,U J_s U^{-1}]")
    assert "C -> h C h^{-1}" in contract["left_gauge_covariance"]
    assert "J_s->g J_s g^{-1}" in contract["right_gauge_covariance"]
    assert "single edge" in contract["locality"]
    assert contract["renormalizability"].startswith("FAIL")


def test_full_two_site_incidence_has_12_residual_modes_before_alignment() -> None:
    incidence, alignment = audit.goldstone_incidence_matrices()
    assert incidence.shape == (66, 66)
    assert incidence.rank() == 54
    assert incidence.cols - incidence.rank() == 12
    assert incidence.rows - incidence.rank() == 12
    assert alignment.shape == (12, 66)
    assert alignment.rank() == 12
    assert alignment * incidence == sp.zeros(12, 66)


def test_alignment_lifts_all_and_only_the_12_physical_chirals() -> None:
    incidence, alignment = audit.goldstone_incidence_matrices()
    vector = incidence.T * incidence
    goldstone = incidence * incidence.T + alignment.T * alignment
    assert vector.rank() == 54
    assert vector.cols - vector.rank() == 12
    assert goldstone.rank() == 66
    assert goldstone.det() == 68719476736
    assert goldstone.eigenvals() == {
        sp.Integer(2): 36,
        (sp.Integer(3) - sp.sqrt(5)) / 2: 9,
        (sp.Integer(3) + sp.sqrt(5)) / 2: 9,
        sp.Integer(1): 12,
    }


def test_one_neither_block_separates_gauge_and_physical_directions() -> None:
    report = audit.build_report()
    block = report["alignment_and_spectrum"][
        "full_two_site_Rxi_and_alignment"
    ]["neither_block"]
    d = sp.Matrix(block["D"])
    a = sp.Matrix(block["A"])
    assert d.rank() == a.rank() == 1
    assert a * d == sp.zeros(1, 1)
    assert block["alignment_Hessian_eigenvalues_in_unit_mu_convention"] == [0, 2]


def test_lean_link_removes_multiplier_burden_but_not_linear_source_pole() -> None:
    certificate = audit.perturbativity_certificate(0.73)
    v51 = certificate["V51_per_edge"]
    lean = certificate["V52_nonlinear_link"]
    assert v51["unconstrained_link_plus_multiplier_coordinates"] == 1179
    assert v51["left_site_index"] == 106
    assert v51["right_site_index"] == 182
    assert lean["complex_coordinates"] == 45
    assert lean["constraint_multiplier_coordinates"] == 0
    assert lean["alignment_elementary_coordinates"] == 0
    assert lean["adjoint_tangent_index_proxy"] == 8
    assert lean["coordinate_reduction_from_V51"] == 1134
    linear = certificate["linear_V51_source_retained"]
    assert linear["sum_T"] == 142
    assert linear["b_one_loop"] == -118
    assert 3.50 < linear["Landau_pole_over_matching_scale"] < 3.52
    assert not linear["controlled_at_g_0p73"]


def test_composite_source_is_labeled_only_as_an_EFT_hypothesis() -> None:
    certificate = audit.perturbativity_certificate(0.73)
    composite = certificate["fully_nonlinear_source_hypothesis"]
    assert composite["sum_T_proxy"] == 24
    assert composite["b_one_loop_proxy"] == 0
    assert composite["one_loop_logarithmic_pole_in_proxy"] is None
    assert 17.2 < composite["NDA_cutoff_over_vector_mass_4pi_over_g"] < 17.3
    assert composite["status"].startswith("POSSIBLE_EFT_ONLY")


def test_report_resolves_subproblem_but_fail_closes_all_gates() -> None:
    report = audit.build_report()
    assert report["gate_effect"]["V51_12_chiral_subproblem"].startswith(
        "RESOLVED_EXACTLY"
    )
    assert report["gate_effect"]["C2"].startswith("CANDIDATE_LOCALITY_PASS_ONLY")
    assert report["gate_effect"]["C3"].startswith("PARTIAL")
    assert report["gate_effect"]["C4"].startswith("PARTIAL")
    assert report["gate_effect"]["C5"].startswith("OPEN_FOR_NEW_ACTION")
    assert report["gate_effect"]["C6"].startswith("UNASSESSED_FOR_NEW_ACTION")
    assert report["gate_effect"]["C7"].startswith("OPEN_FOR_NEW_ACTION")
    assert report["gate_effect"]["candidate_UV_viability"].startswith("FAIL")
    assert not report["gate_effect"]["G2_closed"]
    assert report["gate_effect"]["gates_promoted"] == []
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert all(report["kill_tests"].values())


def test_artifacts_are_current_and_canonically_hashed() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == EXPECTED_CORE_SHA256
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
