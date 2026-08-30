from __future__ import annotations

import json

import susy_v53_theory_completion_verification_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def advance(value: dict, advance_id: str) -> dict:
    return next(row for row in value["exact_advance_ledger"] if row["id"] == advance_id)


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def clause(value: dict, clause_id: str) -> dict:
    return next(row for row in value["V53_candidate_clause_ledger"] if row["id"] == clause_id)


def test_master_core_and_all_inputs_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["integrity_checks"]["all_input_cores_are_canonical_and_expected"]


def test_193_coordinate_whole_action_kernel_certificate() -> None:
    row = advance(report(), "A1_declared_sparse_whole_action")
    assert row["coordinates"] == 193
    assert (row["H_rank"], row["H_nullity"], row["Q_rank"]) == (111, 82, 33)
    assert "45 light matter" in row["kernel"]
    assert "4 weak-Higgs" in row["kernel"]


def test_unchanged_action_selector_no_go_is_integrated() -> None:
    row = advance(report(), "A2_unchanged_action_selector_no_go")
    assert row["invariant_multidegrees"] == 66
    assert row["invariant_directions"] == 365
    assert row["F16_power4_family_invariants"] == 6
    assert row["required_charge_assignments"] == 227
    assert row["proton_safe_assignments"] == 0


def test_cross_coupled_DW_source_is_exactly_isolated() -> None:
    row = advance(report(), "A3_cross_coupled_DW_source_and_two10_rank_split")
    assert (row["source_H_rank"], row["source_H_nullity"], row["source_Q_rank"]) == (143, 33, 33)
    assert row["uncoupled_control_extra_moduli"] == 6


def test_two10_rank_split_is_open_but_unprotected() -> None:
    row = advance(report(), "A3_cross_coupled_DW_source_and_two10_rank_split")
    assert row["two10_full_rank"] == 16
    assert row["two10_weak_nullity"] == 4
    assert "H1^2" in row["limitation"]


def test_elementary_filter_full_Hessian_certificate() -> None:
    row = advance(report(), "A4_elementary_filter_Hessian")
    assert row["coordinates"] == 218
    assert (row["H_rank"], row["H_nullity"], row["Q_rank"]) == (181, 37, 33)
    assert (row["filter_color_rank"], row["filter_weak_rank"], row["filter_weak_nullity"]) == (24, 12, 4)
    assert row["extra_zero_modes"] == 0


def test_selector_candidate_scope_and_degree8_leak() -> None:
    row = advance(report(), "A5_bounded_Z9xZ2_selector_candidate")
    assert row["smallest_modulus_through_Z32"] == 9
    assert row["screened_rows"] == 28
    assert row["all_screened_forbidden"]
    assert row["first_exposed_degree"] == 8
    assert row["first_exposed_multiplicity"] == 72


def test_selector_anomaly_residues_and_matter_parity() -> None:
    row = advance(report(), "A5_bounded_Z9xZ2_selector_candidate")
    assert all(value == 0 for value in row["anomaly_residues_after_spectators"].values())
    assert row["exact_matter_parity"]


def test_elementary_driver_is_not_Z9_invariant() -> None:
    same = report()["same_action_compatibility"]
    assert same["Z9_charge_of_P_squared"] == 4
    assert not same["elementary_driver_Z9_invariant"]
    assert not same["same_action_filter_Hessian_and_selector_certificate"]


def test_safe_renormalizable_driver_search_is_rank_deficient() -> None:
    row = advance(report(), "A6_filter_driver_compatibility_no_go")
    assert row["safe_charge_multisets_by_added_fields"] == [1, 4, 10, 20, 35, 56, 84]
    assert row["minimum_rank_deficit_by_added_fields"] == [1] * 7
    assert not row["renormalizable_compatible_driver_found"]


def test_first_bounded_driver_escape_is_nonrenormalizable_degree5() -> None:
    value = report()
    row = advance(value, "A6_filter_driver_compatibility_no_go")
    escape = value["bounded_stopping_theorem"]["smallest_bounded_algebraic_escape"]
    assert row["first_bounded_escape_degree"] == 5
    assert escape["driver_degree"] == 5
    assert escape["added_Z9_charges"] == [1, 8]
    assert "nonrenormalizable" in escape["status"]


def test_perturbativity_comparison_keeps_distinct_actions_distinct() -> None:
    rows = report()["perturbativity_route_comparison"]
    assert [row["b_Landau"] for row in rows] == [7, 16, 18, 22]
    assert rows[0]["pole_over_matching"] > 1.0e9
    assert rows[2]["passes_1000x"]
    assert rows[3]["passes_100x"] and not rows[3]["passes_1000x"]


def test_clause_ledger_has_only_local_C2_pass() -> None:
    value = report()
    assert [row["id"] for row in value["V53_candidate_clause_ledger"]] == [
        "C1", "C2", "C3", "C4", "C5", "C6", "C7"
    ]
    assert clause(value, "C2")["status"] == "PASS_LOCAL_ACTION_ONLY"
    assert clause(value, "C6")["status"] == "OPEN_INCOMPATIBLE"
    assert all(row["status"] != "PASS" for row in value["V53_candidate_clause_ledger"])


def test_G2_conjunction_and_all_V53_gate_promotions_fail_closed() -> None:
    value = report()
    assert not gate(value, "G2")["closed"]
    assert not any(row["V53_candidate_closed"] for row in value["gate_ledger"])
    assert value["final_decision"]["V53_candidate_closed_gates"] == []
    assert value["final_decision"]["full_gates_closed_for_V53_candidate"] == 0


def test_only_historical_G1_is_cumulatively_reusable() -> None:
    value = report()
    assert [row["gate"] for row in value["gate_ledger"] if row["closed"]] == ["G1"]
    assert value["final_decision"]["cumulative_reusable_closed_gates"] == ["G1"]
    assert "frozen" in gate(value, "G1")["scope"]


def test_G3_to_G8_all_remain_open() -> None:
    value = report()
    assert all(not gate(value, f"G{i}")["closed"] for i in range(3, 9))


def test_bounded_route_is_finished_without_global_no_go_claim() -> None:
    stop = report()["bounded_stopping_theorem"]
    assert stop["route_exhausted"]
    assert "not a theorem against all" in stop["not_claimed"]
    assert [row["id"] for row in stop["honest_next_architectures"]] == [
        "N1_nonAbelian_or_continuous_parent",
        "N2_degree5_UV_completion",
        "N3_anomalous_U1A_missing_VEV_branch",
    ]


def test_completion_and_discovery_are_not_overclaimed() -> None:
    decision = report()["final_decision"]
    assert decision["bounded_V53_analysis_finished"]
    assert not decision["complete_theory"]
    assert not decision["empirical_new_physics_discovery"]
    assert not decision["same_action_completion"]
    assert decision["selected_complete_candidate"] is None


def test_scoped_intermediate_referee_verdict_is_cryptographically_bound() -> None:
    value = report()
    referee = value["independent_intermediate_referee"]
    assert referee["exact_checks"] == 20
    assert "REJECT_THEORY_OR_G2_PROMOTION" in referee["status"]
    assert "does not independently certify" in referee["scope"]
    assert len(referee["files"]) == 3
    assert referee["expected_sha256"] == audit.EXPECTED_REFEREE_HASHES
    assert value["integrity_checks"]["scoped_intermediate_referee_files_are_bound"]


def test_primary_sources_are_direct_arxiv_records() -> None:
    sources = report()["primary_sources"]
    assert len(sources) == 4
    assert all(row["url"].startswith("https://arxiv.org/abs/") for row in sources)


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
