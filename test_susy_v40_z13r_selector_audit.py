"""Tests for the fail-closed V40 Z13R selector audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v40_z13r_selector_audit as audit

ROOT = Path(__file__).resolve().parent
REPORT = audit.build_report()


def test_terms_and_high_scale_ring() -> None:
    assert REPORT["terms"]["all_retained_allowed"]
    assert REPORT["terms"]["all_removed_forbidden"]
    ring = REPORT["ring"]
    assert [x["R13"] for x in ring["pure_same_orientation_classes"]] == [12, 6, 12, 6]
    assert ring["all_four_blocked_on_high_scale_branch"]
    assert ring["V39_Qc4_dressing_retested"]["R13"] == 6


def test_ew_counterexamples_are_not_hidden() -> None:
    ring = REPORT["ring"]
    assert [x["R13"] for x in ring["EW_VEV_counterexamples"]] == [2, 2]
    assert ring["literal_all_VEV_ring_block"] is False
    assert REPORT["decision"]["all_VEV_ring_block"] is False


def test_necessary_gs_and_quality_checks() -> None:
    anomaly = REPORT["necessary_R_anomalies"]
    assert anomaly["standard_A"] == {"SU4": 41, "SU2L": 80, "SU2R": 2}
    assert anomaly["standard_A_mod13"] == {"SU4": 2, "SU2L": 2, "SU2R": 2}
    assert anomaly["gravity_A_mod13"] == anomaly["24rho_mod13"] == 9
    assert REPORT["PQ_quality"]["W_charge_lattice_lower_bound"] == 33
    assert REPORT["PQ_quality"]["Kahler_charge_lattice_lower_bound"] == 32


def test_write_check_roundtrip() -> None:
    result = subprocess.run([sys.executable, "-B", str(ROOT / "susy_v40_z13r_selector_audit.py"), "--write", "--check"], check=True, capture_output=True, text=True)
    assert "SUSY V40 Z13R selector audit: PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V40_Z13R_SELECTOR_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["core_sha256"] == audit.sha(payload)
