from __future__ import annotations

import json

import susy_v69_spin11_order4_geometric_rank_escape_audit as audit


def report():
    return audit.build_report()


def test_v69_canonical_recomputation_and_integrity():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_bound_lineage_and_nonimport_are_exact():
    value = report()
    lineage = value["lineage_and_nonimport"]
    assert lineage["bound_input_cores"] == audit.EXPECTED_CORES
    assert lineage["current_V68_action_status"] == "REJECTED"
    assert lineage["V56_V57_role"] == "TEMPLATE_ONLY_NOT_SPIN11_CLOSURE_EVIDENCE"
    assert not lineage["V62_5D_half_wall_GS_imported"]
    assert not lineage["V67_5D_tangent_spectrum_imported"]


def test_direct_hall_lift_is_order_four_not_a_parity():
    direct = report()["direct_order2_lift_audit"]
    obstruction = direct["order_obstruction"]
    assert direct["status"] == "DIRECT_T2_Z2XZ2_PRIME_SPIN11_LIFT_REJECTED"
    assert obstruction["adjoint_order_on_so10"] == 2
    assert obstruction["adjoint_order_on_spin11_coset"] == 4
    assert not obstruction["valid_Z2_parity"]


def test_formal_coset_leakage_is_unavoidable():
    leakage = report()["direct_order2_lift_audit"]["formal_complex_leakage_diagnostic"]
    assert [row["formal_coset_even_even_multiplicity"] for row in leakage["rows"]] == [2, 3, 2, 3]
    assert leakage["minimum_leakage"] == 2
    assert leakage["maximum_leakage"] == 3


def test_published_scalar_projection_full_hyper_import_is_scoped():
    imported = report()["direct_order2_lift_audit"]["published_6D_Spin11_scalar_import"]
    assert imported["conventional_SUSY_hyper_H_zero"] == ["(1,2,4bar)"]
    assert imported["conventional_SUSY_hyper_Hc_left_chiral_zero"] == ["(2,1,4)"]
    assert imported["Q_returns"]
    assert not imported["conventional_full_hyper_import_valid"]
    assert imported["pseudoreal_half_32_projection"] == "OPEN_NOT_COMPUTED"
    assert not imported["general_SUSY_import_closed"]


def test_q4_and_wilson_space_group_relations_pass_exactly():
    skeleton = audit.vector_gauge_skeleton()
    assert skeleton["all_vector_space_group_relations_pass"]
    assert all(skeleton["relation_checks"].values())


def test_order_four_matrix_powers_are_exact():
    q = audit.q4_matrix()
    assert audit.matpow(q, 4) == audit.identity(11)
    assert audit.matpow(q, 2) == audit.diagonal([-1] * 10 + [1])
    assert audit.matmul(q, audit.transpose(q)) == audit.identity(11)


def test_fixed_algebra_dimensions_are_exact():
    dims = report()["order4_space_group_and_fixed_algebra_audit"]["fixed_algebra_dimensions"]
    assert dims == {
        "Spin11_bulk": 55,
        "C_Q_U5": 25,
        "C_Q2_SO10": 45,
        "C_R_SO4xSO7": 27,
        "C_W_SO5xSO6": 25,
        "C_WQ_other_U5": 25,
        "C_Q_and_W_common_G3211": 13,
        "C_Q_and_R_common_G3211": 13,
    }


def test_common_group_is_g3211_but_spin_lift_remains_open():
    skeleton = report()["order4_space_group_and_fixed_algebra_audit"]
    assert skeleton["common_group"] == "G3211"
    assert skeleton["spin_lift_audit"]["status"] == "OPEN_CENTRAL_PHASE_AND_R_TWIST_REQUIRED"
    assert len(skeleton["not_yet_proved"]) == 4


def test_published_n3_spin11_anomaly_parent_counts():
    variants = {
        row["name"]: row
        for row in report()["bulk_and_fixed_locus_anomaly_audit"]["variants"]
    }
    row = variants["PUBLISHED_N3_HALF_SPINOR_PARENT"]
    assert row["published_spectrum"]
    assert row["multiplicities"] == {"11": "6", "32": "3/2", "neutral": 185}
    assert row["gravity"]["charged_H_dimension"] == "114"
    assert row["gravity"]["total_H"] == "299"
    assert row["gravity"]["H_minus_V"] == "244"


def test_published_n3_spin11_anomaly_factorization_and_lattice():
    row = report()["bulk_and_fixed_locus_anomaly_audit"]["variants"][0]
    assert row["residual_adj_minus_hypers"] == {"A2": "-3", "B4": "0", "C22": "3/4"}
    assert row["GS_inner_products"] == {
        "a_squared_required": 8,
        "a_dot_b_required": "-1",
        "b_squared_required": "-1",
    }
    assert row["lattice_witness"]["a"] == [3, 1]
    assert row["lattice_witness"]["b"] == [0, 1]
    assert row["lattice_witness"]["a_characteristic"]
    assert row["factorization_passes"]


def test_localized_family_bulk_parent_factorizes_without_bulk_spinors():
    row = report()["bulk_and_fixed_locus_anomaly_audit"]["variants"][1]
    assert row["multiplicities"] == {"11": "3", "32": "0", "neutral": 266}
    assert row["residual_adj_minus_hypers"] == {"A2": "6", "B4": "0", "C22": "3"}
    assert row["lattice_witness"]["Omega"] == [[0, 1], [1, 0]]
    assert row["lattice_witness"]["a_squared"] == 8
    assert row["lattice_witness"]["a_dot_b"] == 2
    assert row["lattice_witness"]["b_squared"] == -4
    assert row["factorization_passes"]


def test_integrated_anomaly_is_not_fixed_point_completion():
    anomaly = report()["bulk_and_fixed_locus_anomaly_audit"]
    assert anomaly["status"].endswith("NOT_FIXED_POINT_COMPLETIONS")
    assert "projector weights" in anomaly["nonimport_rule"]
    assert "Z4R anomalies" in anomaly["ordinary_connected_Spin11_torsion"]["does_not_close"]


def test_local_rank_branch_is_exact_and_has_no_colored_fields():
    rank = report()["geometric_rank_replacement"]
    assert rank["supersymmetric_branch"]["F_S"] == "X Xbar-vX^2=0"
    assert rank["supersymmetric_branch"]["D_flat"] == "|X|=|Xbar|"
    assert rank["orphan_statement"]["colored_rank_fields"] == 0
    assert rank["orphan_statement"]["classification"] == "ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED"


def test_local_rank_gauge_and_z4r_operator_charges():
    rank = report()["geometric_rank_replacement"]
    assert rank["gauge_charge_checks"]["Ncharge_plus_Ncharge_plus_X"] == 0
    z4r = rank["Z4R_operator_checks"]
    assert z4r["W_rank_allowed"]
    assert z4r["Majorana_NNX_allowed"]
    assert z4r["bare_mu_forbidden"]
    assert z4r["matter16_four_forbidden"]
    assert not z4r["globally_gauged_origin_proved"]


def test_acceptance_matrix_is_fail_closed():
    rows = {row["id"]: row for row in report()["acceptance_matrix"]}
    assert rows["A1"]["status"] == "REJECTED"
    assert rows["A2"]["status"] == "REJECTED_SCOPED"
    assert rows["A3"]["status"] == "PASS_KINEMATIC"
    assert rows["A5"]["status"] == "PASS_CLASSICAL_LOCAL"
    assert rows["A6"]["status"] == "PASS_INTEGRATED"
    assert all(row["status"] != "ACCEPTED" for row in rows.values())


def test_all_gates_remain_open_and_current_action_rejected():
    value = report()
    assert all(row["status"] == "OPEN" and not row["V69_closed"] for row in value["gate_ledger"])
    terminal = value["terminal_decision"]
    assert terminal["current_bound_Spin11_action"] == "REJECTED"
    assert not terminal["V69_new_action_accepted"]
    assert not terminal["same_action_microscopic_completion_found"]
    assert terminal["closed_gates"] == []
    assert not terminal["complete_theory"]


def test_generated_artifacts_match_when_present():
    value = report()
    if audit.JSON_PATH.is_file():
        assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    if audit.MD_PATH.is_file():
        assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
