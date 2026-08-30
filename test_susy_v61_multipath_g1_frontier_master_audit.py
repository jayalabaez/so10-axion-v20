from __future__ import annotations

import json

import susy_v61_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_inputs_and_v61_master_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]
    assert value["n_failed_integrity_checks"] == 0


def test_v61_supersedes_only_v59_route_b() -> None:
    value = report()
    supersession = value["lineage"]["supersession"]
    assert supersession["superseded_route"]["route_id"] == "B"
    assert supersession["superseded_route"]["route_core"] == (
        "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42"
    )
    assert supersession["superseded_route"]["classification"] == (
        "MATHEMATICAL_CANDIDATE_WITH_SCOPED_SELECTOR_NO_GO"
    )
    assert supersession["replacement_route"]["route_id"] == "B61"
    assert supersession["replacement_route"]["route_core"] == audit.EXPECTED_CORES[
        "v61_z4r_escape"
    ]
    assert supersession["route_A60_core_unchanged"] == audit.EXPECTED_CORES[
        "v60_live_heterotic"
    ]
    assert supersession["route_C_core_unchanged"] == audit.EXPECTED_CORES[
        "v59_gauged_u1r"
    ]
    assert not supersession["V60_master_modified"]


def test_escape_certificate_is_bound_exactly() -> None:
    escape = route(report(), "B61")["escape_certificate"]
    assert escape["v59_non_R_scan_had_zero_selectors"]
    assert escape["v59_first_loophole_was_exact_R"]
    assert escape["odd_cycle_argument_inverts_for_R_type"]
    assert escape["assignments_scanned"] == 89999
    assert escape["arithmetic_selectors_exist_beyond_M4"]
    assert escape["GS_universality_selects_only_M4"]
    assert sorted(tuple(v) for v in escape["raw_solutions"]) == [
        (1, 1, 1),
        (3, 3, 3),
    ]
    assert escape["physical_class_count"] == 1
    assert escape["canonical_class"] == {"M": 4, "matter_charges": [1, 1, 1]}


def test_anomaly_universality_passes_where_heterotic_failed() -> None:
    anomaly = route(report(), "B61")["anomaly_certificate"]
    assert anomaly["A3"] == "3"
    assert anomaly["A2"] == "1"
    assert anomaly["eta"] == 2
    assert anomaly["universal_mod_eta"]
    assert anomaly["GS_axion_required"]
    assert not anomaly["GS_axion_exhibited"]
    assert anomaly["heterotic_contrast_bound"] == ["1", "1", "1", "0", "0"]


def test_proton_upgrade_is_bound_but_scoped() -> None:
    proton = route(report(), "B61")["proton_upgrade"]
    assert proton["W_dim5_forbidden_all_orders"]
    assert proton["Kahler_dim5_forbidden"]
    assert proton["dimension_six_and_numerics_open"]


def test_route_b61_does_not_close_g1() -> None:
    row = route(report(), "B61")
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
    assert a["direct_core_rebound_in_V61"]
    assert c["direct_core_rebound_in_V61"]
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
    assert decision["selector_escape_proved"]
    assert decision["unique_selector_class"] == "Z4R with matter charge one"
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["V61_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert not decision["empirical_discovery"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V61_master_closed"]
        and not row["cross_route_aggregation_used"]
        for row in value["gate_ledger"]
    )


def test_g1_decision_names_the_escape_and_the_deficits() -> None:
    value = report()
    g1 = next(row for row in value["gate_ledger"] if row["gate"] == "G1")
    assert "R-type arithmetic" in g1["decision"]
    assert "GS axion" in g1["decision"]
    assert "Dai-Freed" in g1["decision"]
    for index in range(2, 9):
        gate = next(
            row for row in value["gate_ledger"] if row["gate"] == f"G{index}"
        )
        assert gate["decision"].startswith("OPEN: V61 adds no same-action proof")


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
