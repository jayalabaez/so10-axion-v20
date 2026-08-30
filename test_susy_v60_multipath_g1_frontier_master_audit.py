from __future__ import annotations

import json

import susy_v60_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_inputs_and_v60_master_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]


def test_v60_supersedes_only_v59_route_a() -> None:
    value = report()
    supersession = value["lineage"]["supersession"]
    assert supersession["superseded_route"]["route_id"] == "A"
    assert supersession["superseded_route"]["route_core"] == (
        "38747dee7e8bafdae38ddea1408c8163d625ff6cb836aaa97304f4479624250b"
    )
    assert supersession["replacement_route"]["route_id"] == "A60"
    assert supersession["replacement_route"]["route_core"] == audit.EXPECTED_CORES[
        "v60_live_heterotic"
    ]
    assert supersession["route_B_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_spin11"
    ]
    assert supersession["route_C_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_gauged_u1r"
    ]
    assert not supersession["V59_master_modified"]


def test_conditional_92_state_reconstruction_and_six_shifts_are_exact() -> None:
    row = route(report(), "A60")
    reconstruction = row["conditional_charge_reconstruction"]
    assert reconstruction["status"] == "PASS"
    assert reconstruction["vendored_fixture_sha256"] == (
        "79ef2c19fd0b9a563ac36a06a3099e4b240966ef3dd8fe968fe4029d9b237f51"
    )
    assert reconstruction["vendored_fixture_matches_expected"]
    assert reconstruction["field_count"] == 92
    assert reconstruction["all_oscillators_absent"]
    assert reconstruction["all_affine_hg_equations_pass"]
    assert reconstruction["changed_field_count"] == 6
    assert [item["field"] for item in reconstruction["changed_fields"]] == [
        "F_41",
        "F_42",
        "F_80",
        "F_81",
        "F_91",
        "F_92",
    ]
    assert all(item["gamma_h"] == "1/2" for item in reconstruction["changed_fields"])
    assert all(
        (item["corrected_q_mod4"] - item["old_q_mod4"]) % 4 == 2
        for item in reconstruction["changed_fields"]
    )


def test_corrected_hidden_anomaly_nonuniversality_is_exact() -> None:
    certificate = route(report(), "A60")["corrected_hidden_anomaly_certificate"]
    assert certificate["factor_order"] == [
        "SU3_C",
        "SU2_L",
        "SU3_hidden",
        "SU2_hidden_1",
        "SU2_hidden_2",
    ]
    assert certificate["anomaly_representatives"] == ["3", "1", "7", "2", "2"]
    assert certificate["residue_vector_mod2"] == ["1", "1", "1", "0", "0"]
    assert not certificate["universal"]
    assert certificate["hidden_nonuniversality"]


def test_every_odd_corrected_plane_r_combination_is_nonuniversal() -> None:
    scan = route(report(), "A60")["complete_tested_Abelian_basis_scan"]
    assert scan["domain"] == "c_i in Z4 with c1+c2+c3 odd, so W has charge 2 mod4"
    assert scan["coefficients_tested"] == 32
    assert scan["residue_pattern_counts"] == {
        "0,0,0,1,1": 16,
        "1,1,1,0,0": 16,
    }
    assert scan["universal_case_count"] == 0
    assert not scan["universal_case_exists"]


def test_all_available_u1_and_printed_space_group_mixings_fail_to_repair() -> None:
    scan = route(report(), "A60")["complete_tested_Abelian_basis_scan"]
    assert scan["continuous_U1_columns_all_universal"]
    assert scan["space_group_mixings_enumerated"] == 64
    assert not scan["space_group_repair_exists"]
    assert scan["available_U1_and_printed_SG_cannot_repair"]
    assert scan["no_combination_in_tested_basis_repairs"]


def test_kappl_candidate_is_rejected_but_not_all_heterotic_physics() -> None:
    value = report()
    row = route(value, "A60")
    decision = value["strict_master_decision"]
    assert row["candidate_G1_completion_rejected"]
    assert not row["full_physical_symmetry_no_go_proved"]
    assert not row["same_action_microscopic_completion"]
    assert decision["Kappl_candidate_G1_completion_rejected"]
    assert not decision["universal_heterotic_no_go"]
    assert not decision["V60_G1_closed"]


def test_rho_tau_class_preservation_and_unknown_obligations_remain_open() -> None:
    row = route(report(), "A60")
    obstruction = row["full_CFT_scope_obstruction"]
    assert obstruction["rho2_tau_equals_tau_minus_e4"]
    assert not obstruction["rho2_tau_in_conjugacy_orbit"]
    assert obstruction["no_h_tau_in_space_group"]
    assert len(row["unknown_obligations"]) == 5
    assert any("threshold" in item for item in row["unknown_obligations"])
    assert any("axion" in item for item in row["unknown_obligations"])


def test_all_32_odd_plane_r_actions_fail_tau_class_preservation() -> None:
    scan = route(report(), "A60")["full_CFT_scope_obstruction"][
        "all_odd_plane_R_tau_class_scan"
    ]
    assert scan["point_group_orbit_size"] == 4
    assert scan["point_group_occupied_flip_counts"] == [0, 2]
    assert scan["coefficient_domain"] == "c_i in Z4 and c1+c2+c3 odd"
    assert scan["combinations_tested"] == 32
    assert scan["R_type_occupied_flip_counts"] == [1, 3]
    assert scan["class_preserving_count"] == 0
    assert scan["every_allowed_combination_fails_class_preservation"]
    assert scan["upstream_point_group_plane_flip_parities"] == [0, 2, 2, 2]
    assert scan["upstream_every_candidate_fails_class_preservation"]
    assert scan["independent_rows_match_upstream_certificate"]
    assert "odd number" in scan["upstream_parity_theorem"]
    assert all(
        sum(item["coefficients_mod4"]) % 2 == 1
        and item["occupied_half_components_flipped"] in (1, 3)
        and not item["in_point_group_conjugacy_orbit"]
        for item in scan["rows"]
    )
    assert "sector-permuting" in scan["scope_caveat"]


def test_spin11_and_gauged_u1r_routes_are_directly_rebound_unchanged() -> None:
    value = report()
    b = route(value, "B")
    c = route(value, "C")
    assert b["bound_core_sha256"] == audit.EXPECTED_CORES["v59_spin11"]
    assert c["bound_core_sha256"] == audit.EXPECTED_CORES["v59_gauged_u1r"]
    assert b["direct_core_rebound_in_V60"]
    assert c["direct_core_rebound_in_V60"]
    assert not b["same_action_microscopic_completion"]
    assert not c["same_action_microscopic_completion"]


def test_cross_route_splicing_is_forbidden() -> None:
    rule = report()["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_G1_closure"]
    assert rule["route_specific_obstructions_remain_scoped"]


def test_all_gates_remain_open_and_theory_is_incomplete() -> None:
    value = report()
    decision = value["strict_master_decision"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V60_master_closed"]
        and not row["cross_route_aggregation_used"]
        for row in value["gate_ledger"]
    )
    assert value["n_failed_integrity_checks"] == 0


def test_generated_json_and_markdown_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)


def test_source_manifest_is_current() -> None:
    value = report()
    paths = [audit.Path(audit.__file__), audit.TEST_PATH, *audit.INPUTS.values()]
    assert all(item["exists"] for item in value["source_manifest"])
    assert {item["path"] for item in value["source_manifest"]} == {
        path.name for path in paths
    }
    for item in value["source_manifest"]:
        path = next(candidate for candidate in paths if candidate.name == item["path"])
        assert item["sha256"] == audit.sha256_file(path)
