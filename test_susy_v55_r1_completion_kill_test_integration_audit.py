from __future__ import annotations

import json

import susy_v55_r1_completion_kill_test_integration_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def branch(value: dict, branch_id: str) -> dict:
    return next(row for row in value["anomaly_branch_ledger"] if row["id"] == branch_id)


def test_master_and_all_upstream_cores_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["integrity_checks"]["all_input_cores_are_canonical_and_expected"]


def test_sparse_matter_hessian_certificate_is_preserved_exactly() -> None:
    sparse = report()["sparse_matter_completion"]
    assert (sparse["coordinates"], sparse["H_rank"], sparse["H_nullity"]) == (
        280,
        197,
        83,
    )
    assert sparse["Q_rank"] == 34
    assert sparse["kernel_decomposition"] == {
        "Spin10_gauge": 33,
        "U1_gauge": 1,
        "extra": 0,
        "light_matter": 45,
        "weak_Higgs": 4,
    }
    assert sparse["matter_block"] == {
        "coordinates": 51,
        "rank": 6,
        "nullity": 45,
        "heavy_RHN_determinant_identity": (
            "det([[0,400 Lambda],[400 Lambda^T,40 Mu]])=-400^6 det(Lambda)^2"
        ),
    }


def test_universal_family_action_is_not_a_protected_texture() -> None:
    sparse = report()["sparse_matter_completion"]
    assert sparse["family_charges"] == [11, 11, 11]
    assert sparse["RH_neutrino_charges"] == [-10, -10, -10]
    assert sparse["all_displayed_terms_neutral"]
    assert not sparse["texture_protected_by_U1"]
    assert "every entry" in sparse["symmetry_complete_flavor_statement"]


def test_source_filter_topology_forces_both_fatal_fillers() -> None:
    kill = report()["symmetry_completion_kill_test"]
    assert kill["forced_operators"] == ["h_10 A45 H2_10", "L h_10 H2_10"]
    assert kill["actual_charge_arithmetic"] == {
        "L_h_H2": "1-4+3=0",
        "h_A_H2": "-4+1+3=0",
    }
    assert not kill["removing_L_alone_is_sufficient"]
    assert not kill["fixed_topology_additive_selector_rescue_exists"]
    assert kill["G4_result"] == "FAILED_FOR_R1"


def test_forced_filler_removes_all_four_weak_modes() -> None:
    kill = report()["symmetry_completion_kill_test"]
    assert kill["one_weak_component_determinant"] == "x^2"
    assert kill["A_weak_block_coefficient"] == 3
    assert kill["one_weak_component_actual_determinant"] == 9
    assert (kill["weak_rank_before"], kill["weak_rank_after"]) == (12, 16)
    assert kill["weak_Higgs_nullity_after"] == 0


def test_symmetry_complete_280_coordinate_rank_consequence_is_exact() -> None:
    completed = report()["symmetry_completion_kill_test"][
        "generic_symmetry_complete_280_coordinate_consequence"
    ]
    assert (completed["coordinates"], completed["H_rank"], completed["H_nullity"]) == (
        280,
        201,
        79,
    )
    assert completed["kernel_decomposition"] == {
        "Spin10_gauge": 33,
        "U1_gauge": 1,
        "light_matter": 45,
        "weak_Higgs": 0,
        "extra": 0,
    }


def test_exact_tensor_audit_corrects_single_family_proxy() -> None:
    tensor = report()["matter_tensor_and_family_results"]["exact_D5_tensor_correction"]
    assert tensor["same_family_Fi4_absent"]
    assert tensor["three_plus_one_absent"]
    assert tensor["genuine_mixed_patterns"] == [
        [2, 2, 0],
        [2, 0, 2],
        [0, 2, 2],
        [2, 1, 1],
        [1, 2, 1],
        [1, 1, 2],
    ]
    assert tensor["multiplicity_each"] == [1] * 6


def test_family_search_has_survivors_but_none_keep_fixed_GS_repair() -> None:
    matter = report()["matter_tensor_and_family_results"]
    assert matter["half_integer_low_degree_search"]["strict_solution_count"] == 0
    assert matter["half_integer_low_degree_search"][
        "nearest_candidate_first_F4_total_degree"
    ] == 8
    broad = matter["broader_integer_proxy_search"]
    assert (broad["triples_scanned"], broad["hierarchical_proxy_survivors"]) == (
        820,
        626,
    )
    assert broad["strict_monotone_survivors"] == 178
    assert broad["maximum_first_proton_dressing_insertions"] == 10
    assert broad["lowest_charge_strict_example"] == [45, 39, 11]
    assert broad["fixed_GS_repair_survivors"] == 0


def test_anomaly_repairs_are_explicitly_kept_in_separate_actions() -> None:
    value = report()
    a1 = branch(value, "A1_UNIVERSAL_MATTER_PLUS_RHN")
    a2 = branch(value, "A2_Q11_FAMILY_ONLY_REDUCED_REPAIR")
    a3 = branch(value, "A3_DIFFERENTIATED_FORMAL_REPAIR")
    assert (a1["spectator_count"], a2["spectator_count"], a3["spectator_count"]) == (
        133,
        128,
        5,
    )
    assert a1["RH_neutrinos_included"] and not a2["RH_neutrinos_included"]
    assert a3["family_charges"] == [-2, 1, 11]
    assert a3["spectator_charges"] == [1, -20, 32, -19, 31]
    assert a3["spectator_H_rank"] == 5
    assert not any(row["physical_GS_completion"] for row in value["anomaly_branch_ledger"])


def test_degree9_proton_result_is_parameterized_not_overclaimed() -> None:
    proton = report()["proton_feasibility"]
    assert proton["operator"] == "(F1^2 F2^2)_Spin10-singlet S^4 R / Lambda^6"
    assert proton["total_degree"] == 9
    assert proton["experimental_lower_limit_yr"] == 5.9e33
    assert abs(proton["published_reference_maximum_c_kappa_eta"] - 0.05468932432454966) < 1e-15
    assert not proton["automatically_fatal"]
    assert not proton["proved_safe"]
    assert not proton["G7_closed"]


def test_C1_to_C7_have_no_pass_and_include_two_failures() -> None:
    clauses = report()["V55_candidate_clause_ledger"]
    assert [row["id"] for row in clauses] == [f"C{i}" for i in range(1, 8)]
    assert all(not row["status"].startswith("PASS") for row in clauses)
    assert clauses[0]["status"] == "FAIL_OPERATOR_COMPLETENESS"
    assert clauses[2]["status"] == "FAIL_INTENDED_KERNEL_AFTER_COMPLETION"


def test_zero_V55_gates_close_and_only_frozen_G1_is_retained() -> None:
    value = report()
    assert not any(row["V55_candidate_closed"] for row in value["gate_ledger"])
    assert [row["gate"] for row in value["gate_ledger"] if row["closed"]] == ["G1"]
    assert "FAILED for R1" in gate(value, "G4")["decision"]
    assert value["final_decision"]["full_gates_closed_for_V55_candidate"] == 0


def test_R1_is_rejected_and_next_step_requires_topology_change() -> None:
    value = report()
    decision = value["final_decision"]
    assert decision["bounded_V55_R1_analysis_finished"]
    assert decision["R1_fixed_topology_rejected"]
    assert decision["selected_complete_candidate"] is None
    assert decision["selected_executable_frontier_candidate"] is None
    assert not decision["same_action_completion"]
    assert not decision["complete_theory"]
    assert not decision["empirical_new_physics_discovery"]
    obligations = value["hard_next_architecture_obligations"]
    assert [row["id"] for row in obligations] == [
        "N1_CHANGE_SOURCE_FILTER_TOPOLOGY",
        "N2_PROTECT_THE_FILTER",
        "N3_RECOMPUTE_FULL_GEOMETRY",
        "N4_ONE_ACTION_MATTER_GS_OPERATORS",
        "N5_MATCH_AND_TEST",
    ]
    assert "Merely removing L is insufficient" in obligations[0]["requirement"]


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
