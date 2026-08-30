"""Regression tests for the V41 Dirac-neutrino messenger matching."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v41_dirac_messenger_audit as v41


ROOT = Path(__file__).resolve().parent


def test_all_uv_terms_and_effective_operator_are_selector_allowed() -> None:
    report = v41.build_report()
    terms = report["term_audit"]
    assert terms["all_U1F_neutral"]
    assert terms["all_Z9_neutral"]
    assert terms["all_Z4R_charge_two"]
    assert terms["all_Z5610_and_PQ_neutral"]
    assert terms["effective_operator"] == {
        "fields": ["Q", "H", "Sc", "NDirac"], "U1F": 0, "Z9": 0, "Z4R": 2,
    }


def test_messenger_anomaly_increment_is_zero_and_witten_safe() -> None:
    increment = v41.build_report()["anomaly_increment"]
    assert increment["delta_U1F_PS_squared"] == {"SU4": 0, "SU2L": 0, "SU2R": 0}
    assert increment["delta_U1F_gravitational"] == 0
    assert increment["delta_U1F_cubic"] == 0
    assert increment["SU2R_doublet_increment"] == 8
    assert increment["Witten_parity_preserved"]


def test_tree_level_matching_is_explicit() -> None:
    matching = v41.build_report()["tree_level_matching"]
    assert matching["matching_is_tree_level"]
    assert matching["matched_superpotential"] == "W_eff = -(y1 y2/M_F) Q H Sc NDirac"
    assert "does not require a charged VEV" in matching["selector_preservation"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_dirac_messenger_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_dirac_messenger_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V41_DIRAC_MESSENGER_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v41.STATUS
