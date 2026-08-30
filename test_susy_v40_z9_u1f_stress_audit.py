"""Regression tests for the V40 U(1)_F -> Z9 stress audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v40_z9_u1f_stress_audit as audit


ROOT = Path(__file__).resolve().parent


def test_parent_anomalies_cancel_but_cross_parent_data_remains_open() -> None:
    report = audit.build_report()
    u1f = report["ordinary_U1F_anomaly_audit"]
    assert u1f["total_PS_squared_U1F_doubled"] == {"SU4": 0, "SU2L": 0, "SU2R": 0}
    assert u1f["total_gravity_squared_U1F"] == 0
    assert u1f["total_U1F_cubed"] == 0
    cross = report["old_parent_cross_anomaly_boundary"]["selected_residues"]
    assert cross["F_X_squared_mod66"] == 36
    assert cross["F_squared_X_mod66"] == 60
    assert cross["F_squared_H_mod85"] == 0


def test_full_pure_q4_ring_and_v39_qc_witness_are_blocked() -> None:
    report = audit.build_report()
    ring = report["pure_Q4_Qc4_holomorphic_ring"]
    assert [row["Z9_residue"] for row in ring["four_pure_operator_classes"]] == [3, 6, 3, 6]
    assert all(row["forbidden"] for row in ring["four_pure_operator_classes"])
    witness = ring["canonical_PSVev_counterexample_retested"]
    assert witness["Z9_residue"] == 6
    assert witness["integer_solution_exists"] is False


def test_exact_majorana_type_i_no_go_is_explicit() -> None:
    report = audit.build_report()
    no_go = report["Majorana_seesaw_no_go"]
    assert no_go["explicit_ND_Majorana_test"]["Z9_residue"] == 3
    assert no_go["explicit_ND_Majorana_test"]["integer_solution_exists"] is False
    assert "4 q_Qc = 0" in no_go["type_I_general_theorem"]["deduction"][-1]
    assert report["decision"]["retained_V39_type_I_Majorana_seesaw_survives"] is False


def test_write_check_round_trip(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "susy_v40_z9_u1f_stress_audit.py"), "--write", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SUSY V40 Z9 U1F stress audit: PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V40_Z9_U1F_STRESS_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["core_sha256"] == audit.canonical_sha(payload)
