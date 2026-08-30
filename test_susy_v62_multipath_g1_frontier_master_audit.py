from __future__ import annotations

import json

import susy_v62_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_inputs_and_v62_master_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]
    assert value["n_failed_integrity_checks"] == 0


def test_v62_supersedes_only_v61_route_b() -> None:
    value = report()
    supersession = value["lineage"]["supersession"]
    assert supersession["superseded_route"]["route_id"] == "B61"
    assert supersession["superseded_route"]["route_core"] == (
        "6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a"
    )
    assert supersession["replacement_route"]["route_id"] == "B62"
    assert supersession["replacement_route"]["route_core"] == audit.EXPECTED_CORES[
        "v62_localized_gs"
    ]
    assert supersession["route_A60_core_unchanged"] == audit.EXPECTED_CORES[
        "v60_live_heterotic"
    ]
    assert supersession["route_C_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_gauged_u1r"
    ]
    assert not supersession["V61_master_modified"]


def test_localized_ledger_is_bound_exactly() -> None:
    ledger = route(report(), "B62")["localized_ledger"]
    assert ledger["A_y0_Spin10"] == "1/2"
    assert ledger["A_yL"] == {"SU2_L": "-5/2", "SU2_R": "-5/2", "SO7": "1/2"}
    assert ledger["matter_and_mirror_mediators_drop_out"]
    assert ledger["integrated_matching_checks"] == 3
    assert ledger["all_matching_checks_pass"]


def test_nonuniversality_and_gs_sector_are_bound() -> None:
    row = route(report(), "B62")
    assert row["nonuniversality"]["difference_A"] == "-3"
    assert row["nonuniversality"]["matter_free"]
    assert row["nonuniversality"]["heterotic_parallel_noted"]
    gs = row["gs_sector"]
    assert gs["even_shift_impossible"]
    assert gs["universal_yL_coupling_impossible"]
    assert gs["selected_couplings_mod_4"] == {
        "Spin10@y0": 3,
        "SU2_L@yL": 1,
        "SU2_R@yL": 1,
        "SO7@yL": 3,
    }
    assert gs["all_four_wall_phases_cancel"]


def test_inflow_deficits_remain_open_and_route_does_not_close_g1() -> None:
    row = route(report(), "B62")
    assert row["post_vev_inflow"]["required_inflow"] == {
        "SU3": "-2",
        "SU2_L": "-3",
    }
    assert row["post_vev_inflow"]["status"] == "OPEN"
    assert not row["same_action_microscopic_completion"]
    assert not row["G1_closed"]
    assert row["closed_gates"] == []
    assert len(row["remaining_obligations"]) == 5


def test_routes_a60_and_c_are_directly_rebound_unchanged() -> None:
    value = report()
    a = route(value, "A60")
    c = route(value, "C")
    assert a["bound_core_sha256"] == audit.EXPECTED_CORES["v60_live_heterotic"]
    assert c["bound_core_sha256"] == audit.EXPECTED_CORES["v59_gauged_u1r"]
    assert a["direct_core_rebound_in_V62"]
    assert c["direct_core_rebound_in_V62"]
    assert not a["same_action_microscopic_completion"]
    assert not c["same_action_microscopic_completion"]


def test_cross_route_splicing_is_forbidden() -> None:
    rule = report()["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_G1_closure"]
    assert rule["route_specific_obstructions_remain_scoped"]


def test_all_gates_remain_open_and_theory_is_incomplete() -> None:
    value = report()
    decision = value["strict_master_decision"]
    assert decision["localized_ledger_computed"]
    assert decision["gs_sector_exhibited"]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["V62_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert not decision["empirical_discovery"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V62_master_closed"]
        and not row["cross_route_aggregation_used"]
        for row in value["gate_ledger"]
    )


def test_g1_decision_names_the_ledger_and_the_deficits() -> None:
    value = report()
    g1 = next(row for row in value["gate_ledger"] if row["gate"] == "G1")
    assert "3,1,1,3" in g1["decision"]
    assert "(-2, -3)" in g1["decision"]
    assert "Dai-Freed" in g1["decision"]
    for index in range(2, 9):
        gate = next(
            row for row in value["gate_ledger"] if row["gate"] == f"G{index}"
        )
        assert gate["decision"].startswith("OPEN: V62 adds no same-action proof")


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
