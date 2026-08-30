from __future__ import annotations

import json
import subprocess
import sys

import susy_v38_g1_uv_completion_audit as v38


REPORT = v38.build_report()


def test_v37_charge_lifts_and_all_continuous_anomaly_rows_are_exact() -> None:
    rows = REPORT["visible_continuous_charge_packet"]
    assert len(rows) == 20
    by_name = {row["field"]: row for row in rows}
    assert by_name["PsiBar"]["U1X_charge_lift"] == -2
    assert by_name["PsiCBar"]["U1X_charge_lift"] == -2
    assert by_name["A15"]["U1H_charge_lift"] == 69
    assert by_name["A17"]["U1H_charge_lift"] == -69

    ledger = REPORT["visible_anomaly_ledger"]
    assert ledger["U1X_PS_squared_doubled_SU4_SU2L_SU2R"] == [-8, -8, -8]
    assert ledger["U1X_cubed"] == 5247
    assert ledger["U1X_gravity"] == -33
    assert ledger["U1X_squared_U1H"] == 432
    assert ledger["U1X_U1H_squared"] == -9520
    assert ledger["U1H_PS_squared_doubled_SU4_SU2L_SU2R"] == [0, 0, 0]
    assert ledger["U1H_cubed"] == 0
    assert ledger["U1H_gravity"] == 0
    assert ledger["chiral_matter_Z4R_U1H_squared"] == 9520
    assert ledger["chiral_matter_Z4R_cubed"] == 117
    assert ledger["chiral_matter_Z4R_gravity"] == 21
    assert ledger["pure_PS_gauge_anomaly_absent"] is True


def test_ordinary_4d_higgsed_parent_no_go_is_nonvacuous() -> None:
    nogo = REPORT["four_dimensional_no_go"]
    assert nogo["light_U1X_PS_squared_doubled"] == [-8, -8, -8]
    assert nogo["light_residue_mod66"] == [58, 58, 58]
    assert nogo["light_residue_mod33_even_order_relaxation"] == [25, 25, 25]
    assert nogo["combined_Z5610_PS_squared_doubled"] == [-680, -680, -680]
    assert nogo["combined_residue_mod5610"] == [4930, 4930, 4930]
    assert nogo["combined_residue_mod2805_even_order_relaxation"] == [2125, 2125, 2125]
    assert nogo["single_compact_GS_axion_subcase"]["integer_solution_exists"] is False
    assert "cannot" in nogo["conclusion"]


def test_isolated_u1h_parent_and_running_boundary_are_quantified() -> None:
    parent = REPORT["isolated_U1H_parent"]
    assert parent["isolated_U1H_gauge_anomalies"]["all_vanish"] is True
    running = parent["one_loop_N1SUSY_abelian_b"]
    assert running["light_anomalons"] == 9524
    assert running["Higgs_pair"] == 14450
    assert running["total"] == 23974
    assert 0.02 < running["gH_max_at_M_for_100x_scale_headroom"] < 0.03


def test_explicit_mirror_packet_cancels_the_5d_continuous_anomaly_ledger() -> None:
    inflow = REPORT["five_dimensional_interval_EFT"]
    assert len(inflow["mirror_packet"]) == 20
    assert inflow["integer_anomaly_polynomial_coefficient_ledger"]["all_net_rows_zero"] is True
    assert inflow["integer_anomaly_polynomial_coefficient_ledger"]["net"] == {
        "U1X_PS_squared_doubled_SU4_SU2L_SU2R": [0, 0, 0],
        "U1H_PS_squared_doubled_SU4_SU2L_SU2R": [0, 0, 0],
        "U1X_cubed": 0,
        "U1H_cubed": 0,
        "U1X_squared_U1H": 0,
        "U1X_U1H_squared": 0,
        "U1X_gravity": 0,
        "U1H_gravity": 0,
        "chiral_matter_Z4R_U1X_squared": 0,
        "chiral_matter_Z4R_U1H_squared": 0,
        "chiral_matter_Z4R_squared_U1X": 0,
        "chiral_matter_Z4R_squared_U1H": 0,
        "chiral_matter_Z4R_U1X_U1H": 0,
        "chiral_matter_Z4R_cubed": 0,
        "chiral_matter_Z4R_gravity": 0,
    }
    assert inflow["established_microscopic_UV_completion"] is False
    assert any("gravitino" in row for row in inflow["what_it_does_not_close"])


def test_fail_closed_decision_and_frozen_outputs_replay() -> None:
    decision = REPORT["gate_decision"]
    assert decision["G1_closed"] is False
    assert decision["G1_anomaly_subproblem_improved"] is True
    assert decision["ordinary_4D_Higgsed_U1X_solution_exists_under_theorem_assumptions"] is False
    assert decision["local_5D_continuous_anomaly_EFT_packet_exists"] is True
    assert REPORT["n_failed"] == 0
    assert REPORT["core_sha256"] == v38.canonical_sha(REPORT)
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])

    if v38.REPORT_JSON.is_file():
        stored = json.loads(v38.REPORT_JSON.read_text(encoding="utf-8"))
        assert stored["core_sha256"] == v38.canonical_sha(stored)
        assert stored["gate_decision"] == REPORT["gate_decision"]

    result = subprocess.run(
        [sys.executable, "-B", str(v38.ROOT / "susy_v38_g1_uv_completion_audit.py"), "--check"],
        cwd=v38.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V38_G1_UV_AUDIT PASS" in result.stdout
