from __future__ import annotations

import json

import susy_v46_microscopic_kill_test_audit as audit


def test_only_neutral_210_full_spin10_route_survives() -> None:
    report = audit.build_report()
    assert report["route_decision"]["continue"] == "neutral-210-repaired full-Spin10 source wall"
    assert len(report["route_decision"]["kill"]) == 2
    candidate = report["authoritative_candidate"]
    assert candidate["name"] == "V46 neutral-210-repaired four-bulk-spinor interval"
    assert "Phi_210,0" in candidate["Spin10_source_wall_yL"]["boundary_chirals"]


def test_singlet_only_no_go_and_210_rank_repair() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["V46_exact_results"]}
    assert exact["E8"]["value"] == 230
    counts = exact["E9"]["value"]
    assert counts["total_chiral_components"] == 462
    assert counts["eaten_chiral_components"] == 21
    assert counts["generic_massive_uneaten_chiral_components"] == 441
    assert counts["generic_physical_massless_chiral_components"] == 0


def test_5d_ps_gg_shortcut_is_decisively_rejected() -> None:
    report = audit.build_report()
    value = next(row for row in report["V46_exact_results"] if row["id"] == "E10")["value"]
    assert value["adjoint_chiral_zero_modes"] == 12
    assert value["anomaly_free_sign_assignments"] == 0


def test_idealized_full_kk_zero_and_tachyon_theorem() -> None:
    report = audit.build_report()
    value = next(row for row in report["V46_exact_results"] if row["id"] == "E11")["value"]
    assert value["finite_nonzero_b"]["selected_zero_modes_remaining_per_pair"] == 0
    assert value["finite_nonzero_b"]["unselected_zero_modes_per_pair"] == 0
    assert value["tachyon_result"].startswith("none")
    assert "D_++" in value["selected"]
    assert "D_-+" in value["unselected"]


def test_global_screens_pass_without_overclaiming_relative_eta() -> None:
    report = audit.build_report()
    exact = {row["id"]: row for row in report["V46_exact_results"]}
    assert exact["E13"]["value"]["all_integral"]
    assert exact["E13"]["value"]["closed_spin_lattice"]
    assert all(value == 0 for value in exact["E13"]["value"]["totals"].values())
    assert exact["E14"]["value"]["actual_interval_certified"] is False


def test_sigma_mixings_are_retained_as_mandatory_obligations() -> None:
    report = audit.build_report()
    obligations = report["authoritative_candidate"]["mandatory_allowed_operator_extension"]
    assert "barSigma HLF HRA" in obligations
    assert "Sigma HLA HRF" in obligations


def test_every_stage_and_gate_remains_fail_closed() -> None:
    report = audit.build_report()
    assert len(report["stage_ledger"]) == 5
    assert all(row["status"] != "CLOSED" for row in report["stage_ledger"])
    assert len(report["gate_ledger"]) == 8
    assert all(not row["closed"] for row in report["gate_ledger"])
    assert report["scientific_verdict"]["full_gates_closed"] == 0
    assert not report["scientific_verdict"]["complete_theory_established"]


def test_integrity_hash_and_committed_artifacts() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
