#!/usr/bin/env python3
import live_g1_g8_gate_ledger_v20 as ledger


def test_live_gate_summary_is_two_closed_five_partial_one_open():
    report = ledger.build_report()
    assert report["n_failed"] == 0, report
    assert report["summary"]["closed"] == ["G1", "G2"]
    assert report["summary"]["n_closed"] == 2
    assert report["summary"]["n_partial"] == 5
    assert report["summary"]["n_open"] == 1
    assert report["summary"]["n_blocked"] == 0


def test_g1_and_g2_are_closed_and_downstream_gates_fail_closed():
    report = ledger.build_report()
    assert report["gates"]["G1"]["status"] == "CLOSED"
    assert report["gates"]["G2"]["status"] == "CLOSED"
    assert report["gates"]["G1"]["corrections"]["live_independent_invariant_coefficients"] == 64
    assert report["gates"]["G1"]["corrections"]["all_live_tensor_directions_explicit"]
    for gate in ("G3", "G4", "G5", "G6", "G7", "G8"):
        assert report["gates"][gate]["status"] != "CLOSED"
    assert not report["flags"]["all_g1_g8_closed"]
    assert not report["flags"]["whole_model_validated"]


def test_wave_three_is_the_active_frontier():
    report = ledger.build_report()
    assert report["closure_waves"][0]["status"] == "COMPLETE"
    assert report["closure_waves"][1]["status"] == "COMPLETE"
    assert report["closure_waves"][2]["gates"] == ["G3", "G4", "G5"]
    assert report["closure_waves"][2]["status"] == "ACTIVE"
    assert "G3" in report["next_exact_target"]
