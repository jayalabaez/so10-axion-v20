from __future__ import annotations

import json

import susy_v63_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_inputs_and_v63_master_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]
    assert value["n_failed_integrity_checks"] == 0


def test_v63_supersedes_only_v62_route_b() -> None:
    value = report()
    supersession = value["lineage"]["supersession"]
    assert supersession["superseded_route"]["route_id"] == "B62"
    assert supersession["superseded_route"]["route_core"] == (
        "f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e"
    )
    assert supersession["replacement_route"]["route_id"] == "B63"
    assert supersession["replacement_route"]["route_core"] == audit.EXPECTED_CORES[
        "v63_wz_inflow"
    ]
    assert supersession["route_A60_core_unchanged"] == audit.EXPECTED_CORES[
        "v60_live_heterotic"
    ]
    assert supersession["route_C_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_gauged_u1r"
    ]
    assert not supersession["V62_master_modified"]


def test_fate_enumeration_and_identification_are_bound() -> None:
    row = route(report(), "B63")
    fates = row["fate_enumeration"]
    assert fates["total_components"] == 32
    assert fates["fate_counts"] == {
        "dissolved_into_AB_tower": 12,
        "eaten_by_zero_mode_gauginos": 9,
        "paired_with_T": 10,
        "paired_with_S": 1,
    }
    assert fates["all_4d_pairings_R_neutral"]
    assert fates["dissolved_ledger"] == {"Delta_A3": "-2", "Delta_A2": "-3"}
    identification = row["deficit_identification"]
    assert identification["identification_exact"]
    assert identification["both_ir_identities_close"]
    assert identification["V62_required_inflow"] == {"SU3": "-2", "SU2_L": "-3"}


def test_wz_term_is_forced_and_route_does_not_close_g1() -> None:
    row = route(report(), "B63")
    assert row["forced_wz_term"]["coefficient_uniquely_forced"]
    assert row["forced_wz_term"]["status"] == (
        "COEFFICIENT_FORCED__DYNAMICAL_EXTRACTION_OPEN"
    )
    assert not row["same_action_microscopic_completion"]
    assert not row["G1_closed"]
    assert row["closed_gates"] == []
    assert len(row["remaining_obligations"]) == 5


def test_consolidated_theory_card_is_scoped() -> None:
    card = report()["consolidated_theory_card"]
    assert len(card["action_inventory"]) == 7
    assert len(card["certified_passes"]) == 10
    assert len(card["open_obligations"]) == 6
    assert "not claimed complete" in card["honesty_clause"]
    assert any("Z4R" in item for item in card["action_inventory"])
    assert any("Wess-Zumino" in item for item in card["action_inventory"])
    assert any("89999" in item for item in card["certified_passes"])
    assert any("Dai-Freed" in item for item in card["open_obligations"])


def test_routes_a60_and_c_are_directly_rebound_unchanged() -> None:
    value = report()
    a = route(value, "A60")
    c = route(value, "C")
    assert a["bound_core_sha256"] == audit.EXPECTED_CORES["v60_live_heterotic"]
    assert c["bound_core_sha256"] == audit.EXPECTED_CORES["v59_gauged_u1r"]
    assert a["direct_core_rebound_in_V63"]
    assert c["direct_core_rebound_in_V63"]
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
    assert decision["inflow_deficits_identified"]
    assert decision["consolidated_candidate_bound"]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["V63_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert not decision["empirical_discovery"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V63_master_closed"]
        and not row["cross_route_aggregation_used"]
        for row in value["gate_ledger"]
    )


def test_g1_decision_names_the_identification_and_the_deficits() -> None:
    value = report()
    g1 = next(row for row in value["gate_ledger"] if row["gate"] == "G1")
    assert "dissolved Goldstone ledger" in g1["decision"]
    assert "WZ" in g1["decision"]
    assert "Dai-Freed" in g1["decision"]
    for index in range(2, 9):
        gate = next(
            row for row in value["gate_ledger"] if row["gate"] == f"G{index}"
        )
        assert gate["decision"].startswith("OPEN: V63 adds no same-action proof")


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
