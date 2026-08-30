from __future__ import annotations

import json

import susy_v54_anomalous_u1a_blueprint_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_core_and_v53_binding_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["upstream"]["core_sha256"] == audit.EXPECTED_UPSTREAM_CORE


def test_k5_charge_assignment_is_exact() -> None:
    assert report()["U1A_charges"] == {
        "A": "0",
        "H": "1",
        "Hp": "-1",
        "C": "9/10",
        "barC": "-1/2",
        "Z": "2/5",
        "S": "2/5",
        "Cp": "1/10",
        "barCp": "-13/10",
        "F12": "1/10",
        "F3": "-1/2",
    }


def test_every_declared_blueprint_term_is_invariant() -> None:
    rows = report()["required_term_ledger"]
    assert len(rows) == 14
    assert all(row["U1A_charge"] == "0" for row in rows)
    assert all(row["Z2_parity"] == 0 for row in rows)
    assert all(row["allowed"] for row in rows)


def test_all_order_vacuum_active_HuHd_zero_without_operator_overclaim() -> None:
    protection = report()["all_order_DT_protection"]
    assert protection["H_squared_charge"] == "2"
    assert set(protection["effective_VEV_singlet_generators"].values()) == {"2/5"}
    assert protection["A_is_Z2_odd"]
    assert protection["vacuum_active_HuHd_mass_forbidden_to_all_holomorphic_orders"]
    assert not protection["abstract_H_squared_operators_forbidden_to_all_orders"]
    stress = protection["operator_level_stress_test"]
    assert stress["schematic_class"] == "H^2 barC^4"
    assert stress["total_degree"] == 6
    assert stress["U1A_charge"] == "0"
    assert stress["symmetry_allowed"]
    assert stress["canonical_HuHd_mass_component"] == "absent"
    assert protection["all_n_algebra"]["strictly_positive_for_all_n"]
    assert "arbitrary nonnegative integers" in protection["all_n_algebra"]["domain"]
    assert all(not row["neutral"] for row in protection["bounded_rows"])


def test_exact_doublet_triplet_rank_split() -> None:
    dt = report()["exact_DT_mass_matrices"]
    assert (dt["doublet_rank"], dt["doublet_nullity"]) == (3, 1)
    assert (dt["triplet_rank"], dt["triplet_nullity"]) == (4, 0)
    assert dt["triplet_determinant"] != "0"
    assert dt["symbolic_doublet_determinant"] == "0"
    assert dt["symbolic_triplet_determinant"] == "2*Y1*a*(Y*c-2*Y2*a)"
    assert dt["symbolic_triplet_formula_verified"]
    assert "c*Y-2*a*Y2" in dt["rank_split_conditions"]["triplet_rank4_necessary_and_sufficient"]
    assert not dt["coefficient_equality_required"]


def test_visible_coordinate_and_Dynkin_inventory() -> None:
    value = report()
    assert value["candidate"]["visible_complex_coordinates"] == 179
    running = value["perturbativity"]
    assert running["Higgs_T"] == 18
    assert running["three_families_T"] == 6
    assert running["total_T"] == 24
    assert running["Spin10_one_loop_b_Landau"] == 0


def test_anomalous_U1_is_not_mislabeled_as_ordinary_anomaly_free() -> None:
    anomaly = report()["anomaly_and_FI_scope"]
    assert anomaly["Tr_Q"] == "-84/5"
    assert anomaly["SO10_squared_U1A"] == "-11/5"
    assert anomaly["FI_trace_benchmark_F12_charge"] == "1/10"
    assert anomaly["later_Q4_flavour_F12_charge"] == "-11/10"
    assert "separate full anomaly ledger" in anomaly["charge_branch_scope"]
    later = anomaly["later_Q4_branch_partial_ledger"]
    assert later["Tr_Q_before_XY"] == "-276/5"
    assert later["SO10_squared_U1A_before_XY"] == "-7"
    assert later["Tr_Q_after_XY"] == "-256/5"
    assert not anomaly["ordinary_anomaly_free"]
    assert "Green-Schwarz" in anomaly["required_completion"]


def test_family_charge_branch_mismatch_and_Q4_proton_obligation_are_explicit() -> None:
    proton = report()["proton_operator_screen"]
    assert proton["branch_mismatch_exposed"]
    assert proton["FI_trace_benchmark_F12_charge"] == "1/10"
    assert proton["later_Q4_flavour_charges"]["F12"] == "-11/10"
    assert report()["Z2_parities"]["F12"] is None
    assert not proton["Z2_and_Q4_tensor_census_complete"]
    row = proton["lowest_degree_charge_neutral_candidate"]
    assert row["third_family_spinors"] == 4
    assert row["minimum_positive_VEV_dressings"] == 2
    assert row["witness"] == {
        "Z_or_S_or_CbarC": 0,
        "X_Q4_doublet": 1,
        "Y_Q4_doublet": 1,
    }
    assert row["total_degree_if_Q4_allows_contraction"] == 6
    assert "Q4" in proton["decision"]


def test_blueprint_is_selected_but_not_overpromoted() -> None:
    value = report()
    assert value["verdict"]["selected_V54_blueprint"]
    assert not value["verdict"]["complete_theory"]
    assert not value["verdict"]["empirical_discovery"]
    assert value["gate_effect"]["promotions"] == []
    assert not value["candidate"]["one_same_action_charge_ledger"]
    assert len(value["same_action_open_items"]) == 8


def test_integrity_checks_all_pass() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())


def test_primary_sources_are_direct_arxiv_records() -> None:
    assert all(
        row["url"].startswith("https://arxiv.org/abs/")
        for row in report()["primary_sources"]
    )


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
