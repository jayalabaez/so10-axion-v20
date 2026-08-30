"""Regression tests for the integrated V41 theory ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v41_complete_theory_audit as v41


ROOT = Path(__file__).resolve().parent


def test_every_input_verifies_and_no_gate_is_promoted() -> None:
    report = v41.build_report()
    checks = report["integrity_checks"]
    assert checks["all_input_cores_verify"]
    assert checks["canonical_U1F_to_Z9_source_branch_exists"]
    assert checks["source_branch_preserves_exact_Z9"]
    assert checks["source_branch_masses_all_listed_U1F_fields"]
    assert checks["Dirac_messenger_matches_tree_level_operator"]
    assert checks["Dirac_messenger_preserves_incremental_local_anomalies"]
    assert checks["mixed_QQ_QcQc_is_not_a_conventional_epsilon_source"]
    assert checks["net_four_epsilon_matter_classes_through_degree_twelve_are_Z9_forbidden"]
    assert checks["P_Pbar_packet_cancels_five_genuine_F_X_H_triangle_rows"]
    assert checks["theta_only_residual_preserving_product_repair_is_no_go"]
    assert checks["simple_one_axion_GS_subcase_is_obstructed"]
    assert checks["all_order_single_GS_type_I_R_completion_is_no_go"]
    assert checks["no_full_gate_promoted"]
    assert report["complete_theory_exists"] is False
    assert report["established_full_predictive_closed_count"] == 0


def test_real_v41_g7_and_g8_advances_are_not_overclaimed() -> None:
    report = v41.build_report()
    g7 = next(row for row in report["gate_ledger"] if row["gate"] == "G7")
    g8 = next(row for row in report["gate_ledger"] if row["gate"] == "G8")
    assert not g7["closed"]
    assert "two-delta" in g7["advance"]
    assert "proton lifetime" in g7["blocker"]
    assert not g8["closed"]
    assert "matches to" in g8["advance"]
    assert "PMNS/CKM" in g8["blocker"]


def test_g1_and_vacuum_boundaries_remain_explicit() -> None:
    report = v41.build_report()
    g1 = next(row for row in report["gate_ledger"] if row["gate"] == "G1")
    g2 = next(row for row in report["gate_ledger"] if row["gate"] == "G2")
    g3 = next(row for row in report["gate_ledger"] if row["gate"] == "G3")
    assert not g1["closed"]
    assert "primitive X charges" in g1["blocker"]
    assert "one-axion" in g1["blocker"]
    assert not g2["closed"]
    assert "Kähler/soft" in g2["blocker"]
    assert not g3["closed"]
    assert "identical declared product signatures" in g3["blocker"]


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_complete_theory_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v41_complete_theory_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V41_COMPLETE_THEORY_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v41.STATUS
    assert payload["core_sha256"] == v41.canonical_sha(payload)
