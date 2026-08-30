from __future__ import annotations

import json

import susy_v45_new_physics_master_audit as audit


def test_one_reconciled_candidate_and_primitive_charge_lattice() -> None:
    report = audit.build_report()
    candidate = report["authoritative_candidate"]
    assert candidate["name"] == "V45 reconciled four-bulk-spinor interval"
    assert len(candidate["bulk_hypers"]) == 4
    assert candidate["charge_normalization"]["Theta_breaking"] == "U(1)_F -> Z3_F"
    assert not candidate["charge_normalization"]["Z9_claim_retained"]
    assert "redundant Bplus/Bminus singlet shining hypermultiplets" in candidate["not_in_candidate"]


def test_exact_group_and_zero_mode_results_are_integrated() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["exact_results"]}
    assert exact["E1"]["value"] == "(SU(3)_C x SU(2)_L x U(1)_Y)/Z6"
    assert exact["E2"]["value"]["continuous_gauge_algebra_dimension"] == 12
    assert exact["E2"]["value"]["massless_adjoint_chiral_supermultiplets"] == 0
    assert exact["E3"]["value"] is False


def test_wall_by_wall_ordinary_anomalies_vanish() -> None:
    report = audit.build_report()
    anomaly = next(row for row in report["exact_results"] if row["id"] == "E4")["value"]
    assert anomaly["PS_boundary"]["U1F_SU2L_squared_doubled"] == 36
    assert anomaly["PS_bulk"]["U1F_SU2L_squared_doubled"] == -36
    assert anomaly["PS_boundary"]["U1F_SU2R_squared_doubled"] == -36
    assert anomaly["PS_bulk"]["U1F_SU2R_squared_doubled"] == 36
    assert all(value == 0 for value in anomaly["PS_combined"].values())
    assert all(value == 0 for value in anomaly["Spin10_combined"].values())


def test_projected_exotic_mass_rank_is_conditional_not_overclaimed() -> None:
    report = audit.build_report()
    mass = next(row for row in report["exact_results"] if row["id"] == "E5")["value"]
    assert mass["rank_if_mL_and_mR_nonzero"] == 4
    assert mass["determinant"] == "mL^2 mR^2"
    assert "not the regulated determinant" in mass["qualification"]


def test_operator_frontier_and_discrete_r_no_go_are_both_retained() -> None:
    report = audit.build_report()
    locality = next(row for row in report["exact_results"] if row["id"] == "E6")["value"]
    r_theorem = next(row for row in report["exact_results"] if row["id"] == "E7")["value"]
    assert locality["first_PS_U1F_invariant_degree"] == 20
    assert locality["first_nonzero_orientation"] == 12
    assert r_theorem["conclusion"].startswith("No Z_N^R")
    assert "can forbid both" in r_theorem["conclusion"]
    assert r_theorem["plus_witness"]["degree"] == 20
    assert r_theorem["minus_witness"]["degree"] == 20


def test_every_stage_and_gate_remains_fail_closed() -> None:
    report = audit.build_report()
    assert len(report["stage_ledger"]) == 5
    assert all(row["status"] != "CLOSED" for row in report["stage_ledger"])
    assert len(report["gate_ledger"]) == 8
    assert all(not row["closed"] for row in report["gate_ledger"])
    assert report["scientific_verdict"]["full_gates_closed"] == 0
    assert not report["scientific_verdict"]["complete_theory_established"]


def test_integrity_checks_and_core_hash() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]


def test_committed_artifacts_are_current() -> None:
    report = audit.build_report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
