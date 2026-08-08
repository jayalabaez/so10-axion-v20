#!/usr/bin/env python3
import live_g1_g8_gate_ledger_v20 as ledger


def test_historical_gate_summary_has_only_option_c_g1_closed():
    report = ledger.build_report()
    assert report["n_failed"] == 0, report
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["overall_state"] == "HISTORICAL"
    assert report["supersedes_for_current_status"] is False
    assert report["summary"]["closed"] == ["G1"]
    assert report["summary"]["n_closed"] == 1
    assert report["summary"]["n_partial"] == 6
    assert report["summary"]["n_open"] == 1
    assert report["summary"]["n_blocked"] == 0


def test_historical_g1_closed_g2_value_and_chart_partial():
    report = ledger.build_report()
    assert report["gates"]["G1"]["status"] == "CLOSED"
    assert report["gates"]["G2"]["status"] == "PARTIAL"
    assert report["gates"]["G1"]["corrections"]["live_independent_invariant_coefficients"] == 64
    assert report["gates"]["G1"]["corrections"]["all_live_tensor_directions_explicit"]
    corrections = report["gates"]["G2"]["corrections"]
    assert corrections["complete_real_field_dimension"] == 486
    assert corrections["complete_symmetric_Hessian_entries"] == 118341
    assert corrections["canonical_field_chart_closed"] is True
    assert len(report["gates"]["G2"]["open_scope"]) == 3
    assert report["flags"]["historical_option_c_g1_closed"]
    assert report["flags"]["historical_option_c_g2_value_layer_complete"]
    assert report["flags"]["historical_option_c_g2_canonical_field_chart_complete"]
    assert not report["flags"]["authoritative_manuscript_g1_closed"]
    assert not report["flags"]["authoritative_manuscript_g2_closed"]
    assert not report["flags"]["g1_closed"]
    assert not report["flags"]["g2_value_layer_complete"]
    assert not report["flags"]["g2_canonical_field_chart_complete"]
    assert not report["flags"]["g2_complete_gradient"]
    assert not report["flags"]["g2_complete_Hessian"]
    assert not report["flags"]["g2_closed"]


def test_downstream_gates_remain_fail_closed():
    report = ledger.build_report()
    for gate in ("G2", "G3", "G4", "G5", "G6", "G7", "G8"):
        assert report["gates"][gate]["status"] != "CLOSED"
    assert not report["flags"]["all_g1_g8_closed"]
    assert not report["flags"]["whole_model_validated"]


def test_wave_two_is_only_the_historical_derivative_frontier():
    report = ledger.build_report()
    assert report["closure_waves"][0]["status"] == "COMPLETE"
    wave = report["closure_waves"][1]
    assert wave["gates"] == ["G2"]
    assert wave["status"] == "ACTIVE_PARTIAL"
    assert "canonical 486-real physical chart" in wave["completed"]
    assert report["closure_waves"][2]["status"] == "BLOCKED_BY_G2"
    assert "44/51" in report["next_exact_target"]
