from __future__ import annotations

import json

import susy_v51_new_physics_candidate_integration_audit as audit


def exact_result(report: dict, identifier: str) -> dict:
    return next(row for row in report["V51_exact_results"] if row["id"] == identifier)


def candidate_clause(report: dict, identifier: str) -> dict:
    return next(
        row
        for row in report["V51_candidate_clause_assessment"]
        if row["id"] == identifier
    )


def test_all_upstream_cores_are_canonical_and_bound() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["all_input_core_hashes_valid"]
    for name, path in audit.INPUTS.items():
        upstream = audit.load_hashed_json(path)
        assert report["input_core_hashes"][name] == upstream["core_sha256"]


def test_exact_source_orbit_and_hessian_are_integrated() -> None:
    report = audit.build_report()
    orbit = exact_result(report, "E46")["value"]
    hessian = exact_result(report, "E47")["value"]
    assert orbit["Q_shape"] == [465, 22]
    assert orbit["Q_rank"] == 22
    assert orbit["Z_shape"] == [465, 465]
    assert orbit["Z_rank"] == 443
    assert hessian["H_shape"] == [465, 465]
    assert hessian["H_rank"] == 443
    assert hessian["H_nullity"] == 22
    assert hessian["HQ_exact_zero"]
    assert hessian["physical_pullback_shape"] == [443, 443]


def test_corrected_PS_tensors_and_all_factor_rows_are_resolved() -> None:
    report = audit.build_report()
    ps = exact_result(report, "E48")["value"]
    d4 = exact_result(report, "E49")["value"]
    assert ps["low_degree_rows"] == 48
    assert ps["low_degree_resolution"] == {
        "RESOLVED_EMPTY": 28,
        "RESOLVED_NONEMPTY_CARTESIAN": 20,
    }
    assert ps["PS_primitives"] == 34
    assert ps["bar16_PS_covariance_residual"] < 1.0e-12
    assert d4["total_rows"] == 120
    assert d4["zero_rows"] == 76
    assert d4["nonempty_rows"] == 44
    assert d4["total_invariant_directions"] == 72
    assert d4["multiplicity_histogram"] == {"0": 76, "1": 28, "2": 4, "3": 12}
    assert d4["all_nonzero_copy_multiplicities_one"]


def test_candidate_link_and_transport_theorems_are_exact() -> None:
    report = audit.build_report()
    value = exact_result(report, "E50")["value"]
    assert value["sites"] == 5
    assert value["edges"] == 4
    assert value["link_constraint_dimension"] == 567
    assert value["link_rank"] == 567
    assert value["link_nullity"] == 45
    assert value["transport_profiles"] == 32
    assert value["extra_transport_profiles"] == 0


def test_U1_normalization_matches_but_endpoint_leaves_12_chirals() -> None:
    report = audit.build_report()
    value = exact_result(report, "E51")["value"]
    assert value["U1F"]["primitive_Theta_charges"] == [3, -3]
    assert value["U1F"]["candidate_charge_norm_squared"] == 18
    assert value["U1F"]["source_orbit_norm_squared"] == 18
    assert value["U1F"]["candidate_source_normalization_matches"]
    assert value["partition"] == {
        "PS_intersection_SU5__SM": 12,
        "PS_only": 9,
        "SU5_only": 12,
        "neither": 12,
        "sum": 45,
    }
    assert value["uneaten_A5_like_chirals"] == 12


def test_perturbative_polynomial_moose_is_killed() -> None:
    report = audit.build_report()
    value = exact_result(report, "E52")["value"]
    assert value["g_link"] == 0.73
    assert value["interior_b"] == -280
    assert value["source_b"] == -292
    assert value["interior_pole_ratio"] < 1.70
    assert value["source_pole_ratio"] < 1.67
    assert not value["controlled_perturbative_window"]
    assert not report["scientific_verdict"]["controlled_perturbative_UV_completion"]


def test_same_action_rule_prevents_cross_action_promotion() -> None:
    report = audit.build_report()
    same = report["same_action_decision"]
    assert same["V50_shared_action_sha256"] == audit.V50_SHARED_ACTION_SHA256
    assert same["V51_shared_action_sha256"] is None
    assert not same["equivalence_proved"]
    assert candidate_clause(report, "C1")["status"] == "unassessed_for_new_action"
    assert candidate_clause(report, "C2")["status"] == "candidate_locality_only"
    assert candidate_clause(report, "C6")["status"] == "unassessed_for_new_action"
    assert all(
        row["status"] != "pass"
        for row in report["V51_candidate_clause_assessment"]
    )


def test_frontier_and_full_gate_ledgers_stay_fail_closed() -> None:
    report = audit.build_report()
    assert report["V50_frontier_fully_passed_clauses"] == ["C1", "C2", "C6"]
    assert not report["scientific_verdict"]["G2_closed"]
    assert report["scientific_verdict"]["full_gates_closed"] == 1
    assert [row["gate"] for row in report["gate_ledger"] if row["closed"]] == [
        "G1"
    ]


def test_verdict_distinguishes_possible_route_from_complete_theory() -> None:
    verdict = audit.build_report()["scientific_verdict"]
    assert verdict["possible_solution_candidate"]
    assert not verdict["complete_theory"]
    assert not verdict["new_physics_discovery"]
    assert len(audit.build_report()["unresolved_defects"]) == 5


def test_master_artifacts_are_current_and_hashed() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    assert all(row["exists"] and row["sha256"] for row in report["source_manifest"])
