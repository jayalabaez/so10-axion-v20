from __future__ import annotations

import json

import susy_v47_g1_closure_frontier_audit as audit


def test_exactly_g1_is_closed() -> None:
    report = audit.build_report()
    verdict = report["scientific_verdict"]
    assert verdict["full_gates_closed"] == 1
    assert verdict["full_gates_total"] == 8
    assert verdict["closed_gates"] == ["G1"]
    assert [row["gate"] for row in report["gate_ledger"] if row["closed"]] == ["G1"]


def test_global_quotient_and_relative_groups_vanish() -> None:
    report = audit.build_report()
    rows = {row["id"]: row for row in report["V47_exact_results"]}
    assert rows["E15"]["value"] == {"Omega5_BP": "0", "Omega5_BPxU1F": "0"}
    assert rows["E16"]["value"]["Omega6Spin_relative"] == "0"
    assert rows["E16"]["value"]["surjectivity_witness"]["map_Omega6_is_surjective"]


def test_absolute_aps_phase_is_not_overclaimed() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["absolute_APS_not_overclaimed"]
    assert "absolute_KK_eta_phase" not in report["authoritative_candidate"]


def test_coupled_source_count_and_rank_certificate() -> None:
    report = audit.build_report()
    wall = report["authoritative_candidate"]["Spin10_source_wall_yL"]
    counts = wall["coupled_physical_counting"]
    assert counts["total_chiral_components"] == 465
    assert counts["eaten_chiral_components"] == 22
    assert counts["generic_massive_uneaten_chiral_components"] == 443
    assert counts["generic_physical_massless_chiral_components"] == 0
    assert report["integrity_checks"]["source_hessian_exact_witnesses_pass"]


def test_four_spinor_characteristic_and_zero_count() -> None:
    report = audit.build_report()
    boundary = report["authoritative_candidate"]["four_spinor_boundary_extension"]
    assert boundary["characteristic"] == "K(m)=(-m S+B F)E+(G+m B S)O"
    assert boundary["exact_zero_modes_for_finite_nonzero_Theta_blocks"] == 0
    assert report["integrity_checks"]["KK_self_adjoint_stability_certified"]


def test_only_anomaly_stage_is_closed() -> None:
    report = audit.build_report()
    assert [row["stage"] for row in report["stage_ledger"] if row["status"] == "CLOSED"] == [
        "S1"
    ]
    assert all(
        row["status"] != "CLOSED" for row in report["stage_ledger"] if row["stage"] != "S1"
    )


def test_route_is_retained_and_alternative_fail_closed() -> None:
    report = audit.build_report()
    decision = report["route_decision"]
    assert decision["continue"].startswith("neutral-210")
    assert "pending" in decision["45_plus_54"]
    assert not report["scientific_verdict"]["complete_theory_established"]
    assert not report["scientific_verdict"]["empirically_validated"]


def test_integrity_core_and_artifacts() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
