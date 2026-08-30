from __future__ import annotations

import json

import susy_v54_theory_redesign_integration_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_ledger"] if row["id"] == route_id)


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def clause(value: dict, clause_id: str) -> dict:
    return next(row for row in value["V54_candidate_clause_ledger"] if row["id"] == clause_id)


def test_master_and_all_upstream_cores_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["integrity_checks"]["all_input_cores_are_canonical_and_expected"]


def test_continuous_parent_control_and_charged_source_rescue() -> None:
    row = route(report(), "R1_CONTINUOUS_PARENT_FI")
    control = row["unchanged_action_control"]
    assert (control["coordinates"], control["H_rank"]) == (271, 237)
    assert control["H_nullity"] == control["Q_rank"] == 34
    assert control["physical_weak_Higgs_zero_modes"] == 0

    rescue = row["exact_local_rescue"]
    assert rescue["spurion_constraint_rank"] == 6
    assert rescue["spurion_constraint_kernel"] == [6, -12, -6, 4, -2, 1, 2]
    assert rescue["all_spurion_F_residuals"] == [0] * 7
    assert (rescue["coordinates"], rescue["H_rank"], rescue["H_nullity"]) == (229, 191, 38)
    assert rescue["Q_rank"] == 34
    assert rescue["kernel_decomposition"] == {
        "Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0,
    }
    assert (rescue["GS_repaired_coordinates"], rescue["GS_repaired_H_rank"]) == (363, 325)
    assert rescue["GS_spectator_count"] == 134
    assert row["fail_closed_boundary"]["first_F4_total_degree"] == 9


def test_degree5_UV_geometry_and_center_corrected_no_go() -> None:
    row = route(report(), "R2_DEGREE5_MESSENGER_UV")
    assert row["exact_advance"]["singlet_H_rank"] == 14
    assert row["exact_advance"]["singlet_H_determinant"] == -81
    assert (row["exact_advance"]["combined_coordinates"], row["exact_advance"]["combined_H_rank"], row["exact_advance"]["combined_H_nullity"]) == (230, 193, 37)
    assert row["fatal_obstruction"]["gauge_invariant_degree6_F4_rows"] == 4
    assert row["fatal_obstruction"]["gauge_invariant_directions"] == 24


def test_nonabelian_declared_kernel_is_destroyed_by_required_operator() -> None:
    row = route(report(), "R3_NONABELIAN_SU2F_FILTER")
    assert (row["exact_advance"]["declared_coordinates"], row["exact_advance"]["declared_H_rank"], row["exact_advance"]["declared_H_nullity"]) == (255, 215, 40)
    assert row["exact_advance"]["combined_Q_rank"] == 36
    assert row["exact_advance"]["declared_weak_modes"] == 4
    assert (row["fatal_obstruction"]["complete_H_rank"], row["fatal_obstruction"]["complete_H_nullity"]) == (219, 36)
    assert "H_a^T A H_b" in row["fatal_obstruction"]["operator"]


def test_selected_blueprint_has_exact_reduced_DT_but_not_one_charge_action() -> None:
    row = route(report(), "R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT")
    exact = row["exact_advance"]
    assert exact["visible_coordinates"] == 179
    assert (exact["doublet_rank"], exact["doublet_nullity"], exact["triplet_rank"]) == (3, 1, 4)
    assert exact["triplet_determinant_formula"] == "2*Y1*a*(Y*c-2*Y2*a)"
    assert exact["abstract_H2barC4_allowed"]
    assert exact["visible_Spin10_b"] == 0
    assert not row["fatal_boundary"]["one_same_action_charge_ledger"]
    assert row["fatal_boundary"]["FI_branch_F12"] == "1/10"
    assert row["fatal_boundary"]["Q4_branch_F12"] == "-11/10"


def test_modern_flavour_kill_test_is_reproduced_and_scoped() -> None:
    row = route(report(), "R5_Q4_MODERN_FLAVOUR_KILL_TEST")
    exact = row["exact_advance"]
    assert abs(exact["theta13_deg"] - 3.5789613556) < 1e-10
    assert abs(exact["sqrt_mass_splitting_ratio"] - 0.1281337928) < 1e-10
    assert exact["published_benchmark_reproduced"]
    assert row["modern_test"]["frozen_failed_observables"] == [
        "theta12_deg", "theta13_deg", "sqrt_delta_m21_sq_over_delta_m31_sq"
    ]
    assert len(row["modern_test"]["bounded_seeds"]) == 4
    assert not row["modern_test"]["bounded_feasible"]
    assert not row["modern_test"]["global_texture_theorem"]


def test_C1_to_C7_have_no_pass_and_G2_conjunction_fails() -> None:
    value = report()
    assert [row["id"] for row in value["V54_candidate_clause_ledger"]] == [f"C{i}" for i in range(1, 8)]
    assert all(not row["status"].startswith("PASS") for row in value["V54_candidate_clause_ledger"])
    assert clause(value, "C6")["status"] == "OPEN_GS_AND_CHARGE_BRANCH_INCOMPATIBLE"
    assert not gate(value, "G2")["V54_candidate_closed"]


def test_no_V54_gate_is_promoted_and_only_frozen_G1_is_retained() -> None:
    value = report()
    assert not any(row["V54_candidate_closed"] for row in value["gate_ledger"])
    assert [row["gate"] for row in value["gate_ledger"] if row["closed"]] == ["G1"]
    assert "frozen" in gate(value, "G1")["scope"]
    assert value["final_decision"]["V54_candidate_closed_gates"] == []
    assert value["final_decision"]["full_gates_closed_for_V54_candidate"] == 0


def test_selected_object_is_a_blueprint_not_a_complete_candidate() -> None:
    value = report()
    selected = value["selected_redesign"]
    decision = value["final_decision"]
    assert selected["complete_candidate"] is None
    assert selected["architecture_blueprint"] == "R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT"
    assert "charged-source dynamical rescue" in selected["executable_frontier_candidate"]
    assert decision["selected_complete_candidate"] is None
    assert not decision["same_action_completion"]
    assert not decision["complete_theory"]
    assert not decision["empirical_new_physics_discovery"]


def test_hard_next_obligations_are_explicit_and_finite() -> None:
    obligations = report()["hard_next_obligations"]
    assert [row["id"] for row in obligations] == [
        "N1_ONE_ACTION", "N2_FULL_GEOMETRY", "N3_COMPLETE_OPERATORS",
        "N4_CURRENT_PHENOMENOLOGY", "N5_SOFT_AND_COSMOLOGY",
    ]
    assert "45 light-matter" in obligations[1]["requirement"]


def test_primary_sources_are_direct_records() -> None:
    urls = [row["url"] for row in report()["primary_sources"]]
    assert len(urls) == 7
    assert all(url.startswith("https://arxiv.org/abs/") or url.startswith("https://www.nu-fit.org/") for url in urls)


def test_integrity_checks_all_pass() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
