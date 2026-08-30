"""Regression tests for the V40 U(1)_F to Z9 selector architecture."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v40_all_ring_selector as v40


ROOT = Path(__file__).resolve().parent


def test_local_u1f_parent_and_finite_z9_arithmetic() -> None:
    report = v40.build_report()
    u1 = report["U1F_continuous_anomaly_audit"]
    finite = report["finite_Z9_anomaly_audit"]
    assert u1["mixed_U1F_PS_squared"] == {"SU4": 0, "SU2L": 0, "SU2R": 0}
    assert u1["U1F_gravitational"] == 0
    assert u1["U1F_cubic"] == 0
    assert u1["all_SU2_Witten_parities_even"]
    assert finite["both_vanish"]
    cross = report["conditional_V38_parent_cross_anomaly_audit"]
    assert cross["rows"] == {
        "C_F_X_squared": -360,
        "C_F_squared_X": -270,
        "C_F_H_squared": 0,
        "C_F_squared_H": 0,
        "C_F_X_H": 6,
        "C_F_squared_X_H": -540,
    }
    assert not cross["all_rows_vanish"]


def test_terms_and_declared_vevs_preserve_unbroken_z9() -> None:
    report = v40.build_report()
    terms = report["operator_and_charge_audit"]
    ring = report["same_orientation_baryon_ring_proof"]
    assert terms["all_listed_terms_U1F_neutral"]
    assert terms["all_listed_terms_Z9_neutral"]
    assert terms["all_listed_terms_Z4R_charge_two"]
    assert terms["all_listed_terms_Z5610_neutral"]
    assert terms["all_listed_terms_PQ_neutral"]
    assert ring["all_declared_VEVs_preserve_Z9"]
    assert ring["VEV_field_Z9_residues"] == {
        "Sc": 0, "Sbc": 0, "P": 0, "Pb": 0, "ThetaPlus": 0, "ThetaMinus": 0,
    }


def test_same_orientation_ring_is_forbidden_but_mixed_scope_is_not_overclaimed() -> None:
    report = v40.build_report()
    ring = report["same_orientation_baryon_ring_proof"]
    assert [row["Z9"] for row in ring["local_driver_dressed_Q4_Qc4_sources"]] == [3, 6, 3, 6]
    assert ring["all_local_sources_forbidden"]
    assert ring["all_same_orientation_four_matter_tuples_forbidden"]
    assert ring["all_order_same_orientation_Q4_Qc4_VEV_dressing_forbidden"]
    assert ring["mixed_orientation_caveat"]["Z9"] == 0


def test_majorana_no_go_and_fail_closed_gates() -> None:
    report = v40.build_report()
    deduction = report["Majorana_no_go_and_Dirac_rebuild"]["majorana_no_go"]["deduction"]
    assert "therefore 4q(Qc)=0" in deduction[2]
    assert all(not row["full_gate_closed"] for row in report["gate_statuses"])
    assert not report["complete_theory_exists"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v40_all_ring_selector.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v40_all_ring_selector.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V40_ALL_RING_SELECTOR.json").read_text(encoding="utf-8"))
    assert payload["status"] == v40.STATUS
