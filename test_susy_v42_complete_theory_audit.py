"""Regression tests for the integrated V42 theory ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v42_complete_theory_audit as v42


ROOT = Path(__file__).resolve().parent


def test_inputs_verify_and_no_gate_is_promoted() -> None:
    report = v42.build_report()
    checks = report["integrity_checks"]
    assert checks["all_input_cores_verify"]
    assert checks["neutral_parameter_additive_source_host_no_go_verified"]
    assert checks["generic_isolated_source_host_product_branch_is_not_F_flat"]
    assert checks["local_product_all_ten_U1_cubic_rows_vanish"]
    assert checks["local_product_all_nine_U1_PS_squared_rows_vanish"]
    assert checks["local_product_all_three_U1_gravity_rows_vanish"]
    assert checks["local_product_spectator_mass_witnesses_are_full_rank"]
    assert checks["local_product_preserves_Z9"]
    assert checks["local_product_does_not_silently_preserve_old_Z5610"]
    assert checks["G7_low_degree_same_orientation_protection_survives"]
    assert checks["G7_selector_clean_six_matter_witness_exists"]
    assert checks["G7_is_not_promoted"]
    assert checks["no_full_gate_promoted"]
    assert report["complete_theory_exists"] is False
    assert report["established_full_predictive_closed_count"] == 0


def test_g1_boundaries_are_not_overclaimed() -> None:
    report = v42.build_report()
    g1 = next(row for row in report["gate_ledger"] if row["gate"] == "G1")
    assert not g1["closed"]
    assert "Xi(+/-1)" in g1["blocker"]
    assert "Z66/Z5610" in g1["blocker"]
    assert "Majorana/Pfaffian" in g1["blocker"]


def test_source_and_g7_counterexamples_are_explicit() -> None:
    report = v42.build_report()
    g2 = next(row for row in report["gate_ledger"] if row["gate"] == "G2")
    g3 = next(row for row in report["gate_ledger"] if row["gate"] == "G3")
    g7 = next(row for row in report["gate_ledger"] if row["gate"] == "G7")
    assert not g2["closed"]
    assert "not F-flat" in g2["blocker"]
    assert not g3["closed"]
    assert "unavoidable" in g3["blocker"]
    assert not g7["closed"]
    assert "ThetaPlus^2 (Qc)^6 (Sbc)^2 / M^7" in g7["blocker"]
    assert "not a proton-lifetime claim" in g7["blocker"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v42_complete_theory_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v42_complete_theory_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V42_COMPLETE_THEORY_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v42.STATUS
    assert payload["core_sha256"] == v42.canonical_sha(payload)
