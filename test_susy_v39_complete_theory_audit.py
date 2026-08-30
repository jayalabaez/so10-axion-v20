"""Regression tests for the fail-closed V39 master integration audit."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v39_complete_theory_audit as audit


ROOT = Path(__file__).resolve().parent


def test_no_gate_is_promoted_without_independent_physical_input() -> None:
    data = audit.report()
    assert data["complete_theory_exists"] is False
    assert data["established_full_predictive_closed_count"] == 0
    assert [row["gate"] for row in data["gate_ledger"]] == [f"G{i}" for i in range(1, 9)]
    assert [row["closed"] for row in data["gate_ledger"]] == [False] * 8


def test_every_integrity_assertion_passes() -> None:
    checks = audit.report()["integrity_checks"]
    assert checks
    assert all(checks.values())


def test_active_redesign_not_v37_is_integrated() -> None:
    data = audit.report()
    assert data["active_model"] == "PSZ4RZ5610Z3SUSYV39"
    assert data["integrity_checks"]["active_V39_one_loop_PS_coefficients_are_2_5_9"]
    g7 = next(row for row in data["gate_ledger"] if row["gate"] == "G7")
    assert g7["local_sources_forbidden"] is True


def test_promotion_contract_is_complete() -> None:
    contract = audit.report()["promotion_contract"]
    assert set(contract) == {f"G{i}" for i in range(1, 9)}
    assert all(contract[gate] for gate in contract)


def test_core_hash_and_written_certificate_are_reproducible() -> None:
    data = audit.report()
    assert audit.canonical_sha(data) == data["core_sha256"]
    if audit.REPORT_JSON.is_file():
        disk = json.loads(audit.REPORT_JSON.read_text(encoding="utf-8"))
        assert disk == data
        assert audit.canonical_sha(disk) == disk["core_sha256"]
    if audit.REPORT_MD.is_file():
        assert audit.REPORT_MD.read_text(encoding="utf-8") == audit.markdown(data)


def test_all_manifest_entries_exist() -> None:
    manifest = audit.report()["source_manifest"]
    assert all(row["exists"] for row in manifest)
    assert all(isinstance(row["sha256"], str) and len(row["sha256"]) == 64 for row in manifest)
