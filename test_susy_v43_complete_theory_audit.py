"""Regression tests for the integrated V43 theory ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v43_complete_theory_audit as v43


ROOT = Path(__file__).resolve().parent


def test_inputs_verify_and_no_gate_is_promoted() -> None:
    report = v43.build_report()
    checks = report["integrity_checks"]
    assert checks["all_input_cores_verify"]
    assert checks["spurion_evasion_of_V42_at_renormalizable_F_level_verified"]
    assert checks["spurion_formal_F_flat_branch_verified"]
    assert checks["minimal_zero_FI_spurion_D_flat_branch_is_no_go"]
    assert checks["new_U1S_parent_not_silently_claimed"]
    assert checks["self_majorana_gravity_escape_verified"]
    assert checks["self_paired_Pfaffian_PS_threshold_class_is_no_go"]
    assert checks["Z4M_blocks_V42_witness_at_charge_level"]
    assert checks["Z4M_preserves_required_V40_V41_terms"]
    assert checks["Z4M_is_not_misrepresented_as_anomaly_complete"]
    assert checks["ordinary_no_GS_G7_repair_class_is_no_go"]
    assert checks["no_full_gate_promoted"]
    assert report["complete_theory_exists"] is False
    assert report["established_full_predictive_closed_count"] == 0


def test_g1_and_source_boundaries_are_explicit() -> None:
    report = v43.build_report()
    g1 = next(row for row in report["gate_ledger"] if row["gate"] == "G1")
    g2 = next(row for row in report["gate_ledger"] if row["gate"] == "G2")
    g3 = next(row for row in report["gate_ledger"] if row["gate"] == "G3")
    assert not g1["closed"]
    assert "33 Z" in g1["blocker"]
    assert "Pfaffian" in g1["blocker"]
    assert not g2["closed"]
    assert "zero-FI" in g2["blocker"]
    assert not g3["closed"]
    assert "X Omega Omegabar" in g3["blocker"]


def test_z4m_g7_repair_is_not_overclaimed() -> None:
    report = v43.build_report()
    g7 = next(row for row in report["gate_ledger"] if row["gate"] == "G7")
    assert not g7["closed"]
    assert "Z4_M" in g7["advance"]
    assert "gravitational" in g7["blocker"]
    assert "2, 3, and 6" in g7["blocker"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v43_complete_theory_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v43_complete_theory_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V43_COMPLETE_THEORY_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v43.STATUS
    assert payload["core_sha256"] == v43.canonical_sha(payload)
