"""Regression tests for the integrated V40 theory ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v40_complete_theory_audit as v40


ROOT = Path(__file__).resolve().parent


def test_all_inputs_verify_and_no_gate_is_promoted() -> None:
    report = v40.build_report()
    checks = report["integrity_checks"]
    assert checks["all_input_cores_verify"]
    assert checks["new_U1F_PS_local_anomalies_cancel"]
    assert checks["new_Z9_finite_arithmetic_passes"]
    assert checks["same_orientation_Q4_Qc4_declared_VEV_dressings_are_forbidden"]
    assert checks["V39_Qc4_degree9_counterexample_is_blocked_by_Z9"]
    assert checks["type_I_seesaw_no_go_for_Z9_route_verified"]
    assert checks["Z13R_high_scale_type_I_route_verified_but_EW_counterexamples_present"]
    assert checks["V39_pure_yukawa_G5_no_go_preserved"]
    assert checks["no_full_gate_promoted"]
    assert report["established_full_predictive_closed_count"] == 0
    assert report["complete_theory_exists"] is False


def test_g7_and_g1_boundaries_are_not_overclaimed() -> None:
    report = v40.build_report()
    g1 = next(row for row in report["gate_ledger"] if row["gate"] == "G1")
    g7 = next(row for row in report["gate_ledger"] if row["gate"] == "G7")
    assert not g1["closed"]
    assert "cross rows" in g1["blocker"]
    assert not g7["closed"]
    assert "Mixed-orientation" in g7["blocker"]
    assert "Dirac-neutrino" in g7["blocker"]
    assert "(H.H)^12" in g7["blocker"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v40_complete_theory_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v40_complete_theory_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V40_COMPLETE_THEORY_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v40.STATUS
