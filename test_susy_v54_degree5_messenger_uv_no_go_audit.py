from __future__ import annotations

import json

import susy_v54_degree5_messenger_uv_no_go_audit as audit


def report():
    result = audit.build_report()
    audit.validate_report(result)
    return result


def test_upstream_cores_and_degree5_escape_are_bound() -> None:
    result = report()
    assert result["source_manifest"] == {
        "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json": audit.EXPECTED_SELECTOR_CORE,
        "SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.json": audit.EXPECTED_DRIVER_CORE,
        "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json": audit.EXPECTED_FILTER_CORE,
    }
    assert result["tree_level_matching"]["neutral_monomials"] == ["S*T", "P*T^2", "S*P^4"]


def test_every_selected_UV_term_is_invariant_and_renormalizable() -> None:
    action = report()["selected_renormalizable_UV_action"]
    assert action["all_terms_Z9_invariant"] is True
    assert action["all_terms_renormalizable"] is True
    assert all(row["Z9_charge"] == 0 for row in action["unit_witness_terms"])
    assert max(row["degree"] for row in action["unit_witness_terms"]) == 3


def test_exact_14_coordinate_witness_is_F_flat() -> None:
    action = report()["selected_renormalizable_UV_action"]
    assert action["coordinates"] == audit.COORDINATES
    assert action["witness"] == audit.WITNESS
    assert action["F_terms"] == [0] * 14
    assert audit.gradient() == [0] * 14


def test_exact_singlet_hessian_is_full_rank_with_determinant_minus81() -> None:
    action = report()["selected_renormalizable_UV_action"]
    matrix = audit.hessian()
    assert len(matrix) == 14 and all(len(row) == 14 for row in matrix)
    assert matrix == [list(row) for row in zip(*matrix)]
    assert audit.exact_rank(matrix) == action["hessian_rank_QQ"] == 14
    assert audit.exact_determinant(matrix) == action["hessian_determinant"] == -81
    assert action["hessian_nullity"] == 0
    assert "F-flat messenger-chain locus" in action["determinant_scope"]
    assert action["generic_determinant_on_F_flat_messenger_chain_locus"].startswith("-81")
    assert "MU*MA*MB*MC != 0" in action["generic_open_set"]


def test_effective_exponent_matrix_has_exact_determinant9() -> None:
    matching = report()["tree_level_matching"]
    assert matching["exponent_rows"] == [[0, 1, 1], [1, 0, 2], [4, 1, 0]]
    assert matching["exact_exponent_rank"] == 3
    assert matching["exact_exponent_determinant"] == 9
    assert matching["Z9_orbit_size_at_generic_nonzero_solution"] == 9
    assert matching["tree_elimination_open_set_assumptions"][:4] == [
        "MU != 0", "MA != 0", "MB != 0", "MC != 0",
    ]


def test_selected_combined_geometry_is_explicitly_qualified() -> None:
    geometry = report()["selected_action_combined_geometry"]
    assert geometry["coordinate_inventory"] == {
        "DW_source": 176, "four_filter_10s": 40, "UV_singlet_sector": 14, "total": 230,
    }
    assert geometry["rank_decomposition"] == {
        "DW_source": 143, "four_filter_10s": 36, "UV_singlet_sector": 14, "total": 193,
    }
    assert geometry["nullity_decomposition"] == {
        "broken_gauge_orbit": 33, "intended_weak_Higgs": 4, "extra": 0,
    }
    assert geometry["selected_action_geometry_passes"] is True
    assert geometry["symmetry_complete_geometry_passes"] is False


def test_complete_dangerous_census_applies_Spin10_center_filter() -> None:
    census = report()["symmetry_complete_operator_census"]
    assert census["row_count"] == 91
    assert census["Z9_neutral_row_count_before_center_filter"] == 6
    assert census["center_rejected_row_count"] == 2
    assert [row["dressing"] for row in census["center_rejected_rows"]] == [
        ["C16H", "C_messenger"],
        ["Bbar16H", "B_messenger"],
    ]
    assert [row["Spin10_center_Z4_charge"] for row in census["center_rejected_rows"]] == [1, 3]
    assert all(row["Spin10_singlet_multiplicity"] == 0 for row in census["center_rejected_rows"])
    assert census["allowed_row_count"] == 4
    assert census["allowed_invariant_directions"] == 24
    assert census["all_allowed_rows_are_degree6"] is True
    assert [row["dressing"] for row in census["allowed_rows"]] == [
        ["S", "C_messenger"],
        ["T", "B_messenger"],
        ["U_messenger", "C_messenger"],
        ["A_messenger", "B_messenger"],
    ]
    assert all(row["Spin10_center_neutral"] for row in census["allowed_rows"])
    assert all(row["Spin10_singlet_multiplicity"] == 6 for row in census["allowed_rows"])


def test_charge4_messenger_reopens_the_H1_squared_filler() -> None:
    filler = report()["symmetry_complete_operator_census"]["renormalizable_DT_filler"]
    assert filler["operator"] == "C_messenger H1_10 H1_10"
    assert filler["C_messenger_VEV_nonzero"] is True
    assert filler["filter_rank_before"] == 36
    assert filler["generic_filter_rank_after"] == 40
    assert filler["weak_Higgs_nullity_after"] == 0


def test_tree_no_go_is_factorwise_and_fail_closed() -> None:
    tree = report()["factorwise_tree_no_go"]
    assert tree["product_Abelian_symmetries_fail_factorwise"] is True
    assert tree["matter_parity_repairs_failure"] is False
    assert tree["PP_cherry"]["proton_charge_identity"] == "2p-4p+2p=0"
    assert tree["PS_cherry"]["proton_charge_identity"] == "2p+p-3p=0"


def test_added_singlets_are_anomaly_neutral_and_do_not_change_one_loop_running() -> None:
    scope = report()["anomaly_and_perturbativity_scope"]
    assert scope["added_fields_beyond_existing_P"]["total"] == 13
    assert scope["added_gravity_Z9_mod9"] == 0
    assert scope["added_cubic_Z9_mod9"] == 0
    assert scope["added_SO10_squared_Z9"] == 0
    assert scope["new_anomaly_spectators_required"] is False
    running = scope["one_loop_SO10_running"]
    assert running["total_T_unchanged"] == 46
    assert running["b_unchanged"] == 22
    assert running["above_100x"] is True
    assert running["above_1000x"] is False


def test_no_gate_promotion_and_selected_action_is_not_complete_EFT() -> None:
    result = report()
    assert result["selected_action_vs_complete_EFT"]["strict_same_action_feasibility"] is False
    assert result["selected_action_vs_complete_EFT"]["complete_theory"] is False
    assert result["gate_effect"]["candidate_gate_promotions"] == 0
    assert result["gate_effect"]["G1_through_G8_promotions"] == []


def test_hash_and_generated_artifacts_are_current() -> None:
    result = audit.check_artifacts()
    assert audit.canonical_sha(result) == result["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == result
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.markdown(result)
