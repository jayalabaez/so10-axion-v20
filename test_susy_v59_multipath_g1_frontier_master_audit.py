from __future__ import annotations

import json

import susy_v59_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_matrix"] if row["route_id"] == route_id)


def test_all_four_upstream_cores_and_master_core_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "all_four_input_cores_are_canonical_and_expected"
    ]


def test_v58_is_bound_as_a_near_match_not_a_completed_action() -> None:
    baseline = report()["V58_baseline"]
    assert baseline["strongest_near_match"] == "V58_E8xE8_Z2xZ2_FREE_Z2_Z4R_MSSM"
    assert not baseline["same_action_G1_completion"]
    assert baseline["selected_lead_action"] is None


def test_route_a_is_an_information_frontier_not_a_physical_no_go() -> None:
    row = route(report(), "A")
    assert row["classification"] == "SOURCE_DATA_FRONTIER__NOT_A_PHYSICAL_NO_GO"
    assert not row["blocking_certificate"]["physical_Z4R_no_go"]
    assert row["requires_new_worldsheet_or_Orbifolder_calculation"]
    assert row["supersedable_by_live_regeneration"]
    assert not row["same_action_microscopic_completion"]


def test_route_a_charge_equation_and_ambiguity_witness_are_exact() -> None:
    row = route(report(), "A")
    assert row["blocking_certificate"]["equation"] == (
        "r_alpha = sum_i M xi_i (q_sh^i-N_L^i+Nbar_L^i) - M gamma_hg mod M"
    )
    witness = row["exact_gains"][2]["certificate"]
    assert witness["gamma_pair"] == ["0", "1/2"]
    assert witness["charge_difference_mod_4"] == "2"
    assert witness["SU2_anomaly_difference_mod_2"] == "1"


def test_route_a_old_visible_anomalies_keep_their_historical_scope() -> None:
    certificate = route(report(), "A")["exact_gains"][0]["certificate"]
    assert certificate == {
        "A_SU3": "3",
        "A_SU2": "1",
        "eta": 2,
        "universal_mod_eta": True,
    }


def test_route_b_projector_and_rank_breaking_certificates_are_exact() -> None:
    row = route(report(), "B")
    projector = row["exact_gains"][0]["certificate"]
    rank = row["exact_gains"][1]["certificate"]
    assert projector["weak_chiral_zero_modes"] == 2
    assert projector["colored_chiral_zero_modes"] == 0
    assert projector["Sigma_zero_component_count"] == 4
    assert rank["determinant"] == "-lambda*lambdabar*v^2"
    assert rank["normalized_example_determinant"] == "-1"
    assert rank["new_light_colored_states"] == 0


def test_route_b_selector_no_go_is_sharp_but_scoped() -> None:
    row = route(report(), "B")
    obstruction = row["blocking_certificate"]
    assert row["sharp_obstruction_proved"]
    assert obstruction["finite_scan"]["full_rank_charge_assignments_checked"] == 1295
    assert obstruction["finite_scan"]["moduli_scanned"] == [2, 24]
    assert obstruction["finite_scan"]["no_counterexample"]
    assert "an exact R symmetry" in obstruction["loopholes_not_excluded"]
    assert not row["same_action_microscopic_completion"]


def test_route_c_integrated_seed_and_singlet_solution_are_exact() -> None:
    row = route(report(), "C")
    seed = row["exact_gains"][0]["certificate"]
    singlets = row["exact_gains"][1]["certificate"]
    assert (seed["T"], seed["V"], seed["H"]) == (1, 46, 290)
    assert seed["H_minus_V_plus_29T"] == 273
    assert seed["factorization_exact"]
    assert seed["integral_unimodular"]
    assert singlets["all_270_singlets_assigned"]
    assert singlets["q0_global_zero_modes"] == 1
    assert singlets["q4_global_zero_modes"] == 1


def test_route_c_exact_existing_local_gs_rejection_is_bound() -> None:
    row = route(report(), "C")
    obstruction = row["blocking_certificate"]
    certificate = row["exact_gains"][2]["certificate"]
    assert obstruction["failed_fixed_points"] == ["O_GG", "O_flipped", "O_PS"]
    assert not obstruction["passes_all_four"]
    assert certificate["O_GG"]["minors"] == {"SU5_squared__X_squared": 800}
    assert certificate["O_flipped"]["minors"] == {
        "SU5prime_squared__Xprime_squared": 800
    }
    assert certificate["O_PS"]["minors"] == {
        "SU4_squared__SU2L_squared": 32,
        "SU4_squared__SU2R_squared": 32,
        "SU2L_squared__SU2R_squared": 0,
    }
    assert not row["same_action_microscopic_completion"]


def test_cross_route_splicing_is_explicitly_forbidden() -> None:
    rule = report()["cross_route_composition_rule"]
    assert rule["route_action_families_are_distinct"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_G1_closure"]
    assert len(rule["examples_forbidden"]) == 3


def test_live_orbifolder_extension_can_replace_only_route_a() -> None:
    extension = report()["live_heterotic_regeneration_extension"]
    semantics = extension["supersession_semantics"]
    assert extension["state"] == "AWAITING_EXTERNAL_REGENERATION"
    assert extension["current_bound_route_core"] == audit.EXPECTED_CORES[
        "route_a_heterotic"
    ]
    assert extension["current_row_is_supersedable"]
    assert semantics["supersedes_only"] == "route A data-sufficiency row"
    assert semantics["does_not_retroactively_close_G1"]
    assert semantics["does_not_change_route_B_or_C_certificates"]
    assert len(extension["minimum_replacement_payload"]) == 8
    assert len(extension["replacement_contract"]) == 5


def test_master_is_fail_closed_and_promotes_no_gate() -> None:
    value = report()
    decision = value["strict_master_decision"]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["V59_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert not decision["empirical_discovery"]
    assert decision["master_is_a_frontier_certificate_not_an_action"]
    assert len(value["gate_ledger"]) == 8
    assert all(
        row["status"] == "OPEN"
        and not row["V59_master_closed"]
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
    assert all(item["exists"] for item in value["source_manifest"])
    assert {item["path"] for item in value["source_manifest"]} == {
        audit.Path(__file__).name,
        audit.Path(audit.__file__).name,
        *(path.name for path in audit.INPUTS.values()),
    }
    for item in value["source_manifest"]:
        candidates = [audit.Path(audit.__file__), audit.TEST_PATH, *audit.INPUTS.values()]
        path = next(candidate for candidate in candidates if candidate.name == item["path"])
        assert item["sha256"] == audit.sha256_file(path)
