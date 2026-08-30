from __future__ import annotations

import json

import susy_v47_source_completion_route_audit as audit


def test_coupled_210_branch_and_counting() -> None:
    report = audit.build_report()
    source = report["coupled_210_source"]
    assert source["exact_branch"]["STheta"] == 0
    assert source["counting"]["total_chiral_components"] == 465
    assert source["counting"]["eaten_chiral_components"] == 22
    assert source["counting"]["generic_massive_uneaten_chiral_components"] == 443
    assert source["counting"]["generic_physical_massless_chiral_components"] == 0


def test_cross_coupling_hessian_lemma() -> None:
    lemma = audit.build_report()["coupled_210_source"]["physical_hessian_lemma"]
    assert lemma["matrix"] == "[[H,0,c],[0,0,a],[c^T,a,d]]"
    assert lemma["determinant"].startswith("det(Mphys)=-a^2 det(H)")
    certificate = lemma["certificate"]
    assert certificate["all_witnesses_pass"]
    assert [row["n_GUT_physical_modes"] for row in certificate["exact_rational_witnesses"]] == [1, 2, 3, 4]
    assert all(
        row["det_Mphys"] == row["minus_a_squared_det_H"]
        for row in certificate["exact_rational_witnesses"]
    )


def test_exact_fraction_determinant_handles_row_swaps_and_singular_matrices() -> None:
    assert audit.determinant([[0, 1], [1, 0]]) == -1
    assert audit.determinant([[1, 2], [2, 4]]) == 0


def test_parameter_neutral_selector_no_go() -> None:
    no_go = audit.build_report()["parameter_neutral_selector_no_go"]
    assert no_go["ordinary_ZN"]["forced_cross_terms"] == [
        "STheta Phi^2",
        "STheta Sigma.barSigma",
    ]
    assert no_go["ZN_R"]["conclusion"].startswith("only N dividing two")
    assert no_go["decision"] == "include the cross couplings rather than setting them to zero by assertion"


def test_45_54_exact_su5_branch_but_rank_is_fail_closed() -> None:
    alt = audit.build_report()["alternative_45_plus_54"]
    branch = alt["SU5_branch"]
    assert branch["unbroken_group"] == "SU(5)"
    assert branch["exact_rational_rescaled_witness"]["all_residuals_zero"]
    assert alt["rank_status"]["published_complete_mass_matrices_exist"]
    assert not alt["rank_status"]["independent_full_physical_hessian_replayed_here"]


def test_45_54_has_better_naive_index_window() -> None:
    stress = audit.build_report()["perturbative_window_stress_test"]
    r210 = stress["routes"]["210+126+bar126"]
    r4554 = stress["routes"]["45+54+126+bar126"]
    assert r210["sum_chiral_Dynkin_indices"] == 126
    assert r4554["sum_chiral_Dynkin_indices"] == 90
    assert r210["b_4D_N1_including_minus_3C2"] == 102
    assert r4554["b_4D_N1_including_minus_3C2"] == 66
    assert r4554["naive_Landau_ratio_including_vector"] > r210["naive_Landau_ratio_including_vector"]
    assert stress["representation_data"] == {
        "45": {"dimension": 45, "C2": "8", "computed_T": 8},
        "54": {"dimension": 54, "C2": "10", "computed_T": 12},
        "126": {"dimension": 126, "C2": "25/2", "computed_T": 35},
        "bar126": {"dimension": 126, "C2": "25/2", "computed_T": 35},
        "210": {"dimension": 210, "C2": "12", "computed_T": 56},
    }
    assert "source-Higgs-sector-only" in stress["qualification"]


def test_decision_retains_only_rank_certified_route() -> None:
    decision = audit.build_report()["decision"]
    assert decision["authoritative_source_route"].startswith("retain neutral 210")
    assert decision["G3_source_superpotential_existence_subproblem"] == "closed"
    assert not decision["G3_full_gate_closed"]
    assert decision["gates_promoted"] == []


def test_integrity_and_artifacts() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
