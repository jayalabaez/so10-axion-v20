from __future__ import annotations

import json

import susy_v48_g2_frontier_integration_audit as audit


def test_only_G1_is_closed_and_G2_fails_closed() -> None:
    report = audit.build_report()
    verdict = report["scientific_verdict"]
    assert verdict["closed_gates"] == ["G1"]
    assert verdict["full_gates_closed"] == 1
    assert not verdict["G2_closed"]
    assert not verdict["complete_theory_established"]


def test_same_action_G2_contract_has_seven_clauses_and_only_C2_passes() -> None:
    report = audit.build_report()
    rows = {row["id"]: row for row in report["G2_closure_assessment"]}
    assert set(rows) == {f"C{i}" for i in range(1, 8)}
    assert report["fully_passed_clauses"] == ["C2"]
    assert rows["C1"]["status"] == "fail"
    assert rows["C2"]["status"] == "pass"
    assert all(rows[f"C{i}"]["status"] == "partial" for i in range(3, 8))


def test_resolved_wall_exact_map_and_positive_induced_norm_are_retained() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["V48_exact_results"]}
    assert "B_epsilon=D^-1 C" in exact["E23"]["statement"]
    assert "Z_b=epsilon(I+A^2/3)" in exact["E24"]["statement"]
    assert "K_reg=" in exact["E25"]["statement"]


def test_operator_and_PS_counts_are_recorded_without_overclaim() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["V48_exact_results"]}
    value = exact["E26"]["value"]
    assert value == {
        "renormalizable_raw": 16,
        "leading_two_bulk_portals": 12,
        "PS_yukawa_coefficients": 19,
    }
    assert "missing Higgs mass" in exact["E26"]["statement"]


def test_restricted_Schur_kernel_and_pole_witness_are_retained() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["V48_exact_results"]}
    matching = exact["E27"]["value"]
    spectral = exact["E28"]["value"]["spectral"]
    assert matching["all_four_source_projectors_are_seen"]
    assert len(spectral["first_three_positive_signed_roots"]) == 3
    assert spectral["near_pole_residue_max_residual"] < 2.0e-6


def test_all_seven_concrete_defects_are_fail_closed() -> None:
    report = audit.build_report()
    defects = {row["id"]: row for row in report["unresolved_defects"]}
    assert set(defects) == {f"D{i}" for i in range(1, 8)}
    assert "mu_H" in defects["D1"]["statement"]
    assert "Pure-source" in defects["D2"]["statement"]
    assert "HcHc" in defects["D3"]["statement"]
    assert "nabla5" in defects["D4"]["statement"]
    assert "not by itself a supersymmetric transverse mass" in defects["D5"]["statement"]
    assert "generalized norm" in defects["D6"]["statement"]
    assert "Clebsches" in defects["D7"]["statement"]


def test_later_gate_work_is_not_moved_into_G2() -> None:
    report = audit.build_report()
    excluded = report["frozen_G2_contract"]["not_required_for_G2"]
    assert set(excluded) == {"G3", "G6", "G7", "G8", "UV"}
    assert "vacuum" in excluded["G3"]
    assert "pole tower" in excluded["G6"]
    assert "B/L" in excluded["G7"]


def test_stage_and_gate_ledgers_are_fail_closed() -> None:
    report = audit.build_report()
    gates = {row["gate"]: row for row in report["gate_ledger"]}
    assert len(gates) == 8
    assert gates["G1"]["closed"]
    assert all(not gates[f"G{i}"]["closed"] for i in range(2, 9))
    assert [row["stage"] for row in report["stage_ledger"] if row["status"] == "CLOSED"] == ["S1"]


def test_next_patch_targets_the_actual_G2_blockers() -> None:
    report = audit.build_report()
    patch = " ".join(report["smallest_next_closure_patch"])
    assert "source" in patch and "light" in patch
    assert "mu_H" in patch
    assert "K_reg,N_reg" in patch
    assert "Clebsch" in patch


def test_integrity_hashes_and_rendered_artifacts_are_current() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)

