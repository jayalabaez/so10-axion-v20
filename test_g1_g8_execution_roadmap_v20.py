#!/usr/bin/env python3
"""Tests for the machine-readable G1-G8 execution roadmap."""
from __future__ import annotations

import g1_g8_execution_roadmap_v20 as mod


def test_roadmap_contract():
    report = mod.build_report()
    assert report["status"] == (
        "G1_G8_EXECUTION_ROADMAP_READY__PHYSICS_GATES_REMAIN_OPEN"
    )
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())


def test_dependency_graph_and_critical_path():
    report = mod.build_report()
    assert mod.acyclic() is True
    assert report["critical_path"] == [
        "G1",
        "G2",
        "G3/G4/G5",
        "G6",
        "G7",
        "G8",
    ]
    assert report["dependencies"]["G7"] == ["G6"]
    assert report["dependencies"]["G8"] == ["G3", "G6", "G7"]


def test_all_gates_remain_fail_closed():
    gates = mod.build_report()["gates"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert gates["G1"]["status"] == "OPEN"
    assert gates["G7"]["status"] == "OPEN"
    assert all(row["status"] != "CLOSED" for row in gates.values())
    assert gates["G3"]["status"] == "PARTIAL"
    assert gates["G5"]["status"] == "PARTIAL"


def test_every_gate_has_actionable_task():
    report = mod.build_report()
    gates_with_tasks = {
        gate for task in report["tasks"] for gate in task["gates"]
    }
    assert gates_with_tasks == set(report["gates"])
    assert all(task["deliverable"] for task in report["tasks"])
    assert all(task["acceptance"] for task in report["tasks"])


def test_reduced_backreaction_is_not_promoted_to_full_closure():
    report = mod.build_report()
    task = next(
        row
        for row in report["tasks"]
        if row["id"] == "W3-G3G5-EW-BACKREACTION"
    )
    assert task["status"] == "EXECUTED_IN_THIS_CHANGE"
    assert report["gates"]["G3"]["status"] == "PARTIAL"
    assert report["gates"]["G5"]["status"] == "PARTIAL"
    assert "empirical discovery" in report["new_physics_policy"]


def test_exact_phi2_hdagh_family_is_a_subgate_only():
    import exact_phi2_hdagh_channel_family_v20 as family

    report = family.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["representation_census"]["common_channels"] == {
        "1": 1,
        "45": 1,
        "54": 1,
    }
    assert report["flag"]["phi2_hdagh_channel_count_closed"] is True
    assert report["flag"]["complete_mixed_invariant_ring"] is False
    assert report["flag"]["whole_model_validated"] is False
