from __future__ import annotations

import json

import susy_v65_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_inputs_and_v65_master_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]
    assert value["n_failed_integrity_checks"] == 0


def test_v65_supersedes_only_v64_route_b() -> None:
    value = report()
    supersession = value["lineage"]["supersession"]
    assert supersession["superseded_route"]["route_id"] == "B64"
    assert supersession["superseded_route"]["route_core"] == (
        "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d"
    )
    assert supersession["replacement_route"]["route_id"] == "B65"
    assert supersession["replacement_route"]["route_core"] == audit.EXPECTED_CORES[
        "v65_orphan_lift"
    ]
    assert supersession["route_A60_core_unchanged"] == audit.EXPECTED_CORES[
        "v60_live_heterotic"
    ]
    assert supersession["route_C_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_gauged_u1r"
    ]
    assert not supersession["V64_master_modified"]


def test_b65_row_binds_the_classification_and_lift() -> None:
    row = route(report(), "B65")
    assert row["gut_scale_channels"]["count"] == 6
    assert row["gut_scale_channels"]["all_closed"]
    assert row["gut_scale_channels"]["ids"] == ["B1", "B2", "B3", "B4", "B5", "B6"]
    assert row["gravitino_lift"]["orphan_pair_charge"] == 0
    assert row["gravitino_lift"]["same_gm_class_as_mu"]
    assert row["gravitino_lift"]["r_parity_survives"]
    assert row["decay_portals"]["orphan"] == [[3, 3]]
    assert sorted(row["decay_portals"]["anti_orphan"]) == [[-5, -1], [-1, -5]]
    assert row["decay_portals"]["unique_and_baryon_safe"]
    assert row["gs_ir_closure"]["ledger"] == {"A3": 1, "A2": -2}
    assert row["gs_ir_closure"]["closes_exactly"]
    assert row["gs_ir_closure"]["wz_term"] == "NONE"
    assert row["unification_shift"] == {
        "b3": "2",
        "b2": "3",
        "b1_GUT_normalized": "1/5",
    }
    assert "conditionally viable" in row["action_status"]
    assert not row["G1_closed"]
    assert row["closed_gates"] == []


def test_corrected_theory_card() -> None:
    card = report()["consolidated_theory_card"]
    assert len(card["action_inventory"]) == 7
    assert len(card["explicitly_absent"]) == 2
    assert any("Wess-Zumino" in item for item in card["explicitly_absent"])
    assert any("GUT-scale orphan mass" in item for item in card["explicitly_absent"])
    assert len(card["certified_passes"]) == 11
    assert len(card["open_obligations"]) == 6
    assert any("orphan pair" in item for item in card["action_inventory"])
    assert "not claimed complete" in card["honesty_clause"]


def test_routes_a60_and_c_are_directly_rebound_unchanged() -> None:
    value = report()
    a = route(value, "A60")
    c = route(value, "C")
    assert a["bound_core_sha256"] == audit.EXPECTED_CORES["v60_live_heterotic"]
    assert c["bound_core_sha256"] == audit.EXPECTED_CORES["v59_gauged_u1r"]
    assert a["direct_core_rebound_in_V65"]
    assert c["direct_core_rebound_in_V65"]


def test_cross_route_splicing_is_forbidden() -> None:
    rule = report()["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_G1_closure"]
    assert rule["route_specific_obstructions_remain_scoped"]


def test_g1_not_closed_by_declaration_and_all_gates_open() -> None:
    value = report()
    decision = value["strict_master_decision"]
    assert decision["gut_scale_lift_excluded"]
    assert decision["gravitino_scale_lift_constructed"]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["V65_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert "not closed" in decision["honest_outcome"]
    assert "declaration" in decision["honest_outcome"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V65_master_closed"]
        and not row["cross_route_aggregation_used"]
        for row in value["gate_ledger"]
    )


def test_g1_decision_names_the_resolution() -> None:
    value = report()
    g1 = next(row for row in value["gate_ledger"] if row["gate"] == "G1")
    assert "conditional viability" in g1["decision"]
    assert "GM mechanism" in g1["decision"]
    assert "no WZ term" in g1["decision"]
    for index in range(2, 9):
        gate = next(
            row for row in value["gate_ledger"] if row["gate"] == f"G{index}"
        )
        assert gate["decision"].startswith("OPEN: V65 adds no same-action proof")


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
