"""Regression tests for the V41 mixed Pati-Salam four-matter audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v41_mixed_four_matter_audit as v41


ROOT = Path(__file__).resolve().parent


def test_exact_four_matter_su4_tensor_classes() -> None:
    report = v41.build_report()
    rows = report["four_matter_tensor_classification"]["four_matter_rows"]
    assert [(row["n_4"], row["n_bar4"], row["SU4_singlet_exists"]) for row in rows] == [
        (0, 4, True), (1, 3, False), (2, 2, True), (3, 1, False), (4, 0, True),
    ]
    assert [row["Z9_charge"] for row in rows] == [6, 3, 0, 6, 3]


def test_mixed_class_is_not_the_conventional_epsilon_proton_source() -> None:
    section = v41.build_report()["four_matter_tensor_classification"]
    mixed = section["mixed_4_squared_bar4_squared"]
    assert mixed["selector_Z9_charge"] == 0
    assert mixed["epsilon_SU4_available"] is False
    assert mixed["is_conventional_proton_decay_source"] is False
    assert section["same_orientation_classes"]["four_4"]["selector_forbidden"]
    assert section["same_orientation_classes"]["four_bar4"]["selector_forbidden"]


def test_net_plus_or_minus_four_matter_only_classes_are_forbidden() -> None:
    section = v41.build_report()["four_matter_tensor_classification"]
    result = section["all_matter_only_net_plus_or_minus_four_classes_through_degree_12"]
    assert result["row_count"] > 0
    assert result["all_Z9_forbidden"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_mixed_four_matter_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_mixed_four_matter_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V41_MIXED_FOUR_MATTER_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v41.STATUS
