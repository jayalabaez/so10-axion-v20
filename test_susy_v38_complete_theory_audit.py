"""Regression tests for the V38 master complete-theory audit."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v38_complete_theory_audit as audit


ROOT = Path(__file__).resolve().parent
DATA = audit.report()


def test_no_gate_is_promoted_without_the_required_physics() -> None:
    assert DATA["complete_theory_exists"] is False
    assert DATA["established_full_predictive_closed_count"] == 0
    assert [row["closed"] for row in DATA["gate_ledger"]] == [False] * 8
    assert DATA["integrity_checks"]["no_full_gate_is_promoted"] is True


def test_all_input_certificates_verify_and_the_key_no_go_results_survive() -> None:
    checks = DATA["integrity_checks"]
    assert all(checks.values())
    assert DATA["gate_ledger"][0]["closed"] is False
    assert DATA["gate_ledger"][4]["closed"] is False


def test_g7_additive_abelian_no_go_is_symbolically_exact() -> None:
    proof = DATA["g7_additive_abelian_selector_no_go"]
    assert all(proof["source_term_presence"].values())
    assert proof["ordinary_non_R"]["derived_charge_vectors"] == {
        "4qQ": {"Q": 4},
        "4qQc": {"Qc": 4},
    }
    assert proof["additive_R"]["derived_charge_vectors"] == {
        "4rQ": {"Q": 4},
        "4rQc": {"Qc": 4},
    }
    assert proof["verified"] is True


def test_promotion_contract_has_one_concrete_entry_per_gate() -> None:
    contract = DATA["promotion_contract"]
    assert set(contract) == {f"G{index}" for index in range(1, 9)}
    assert all(contract[gate] for gate in contract)


def test_core_hash_and_written_certificate_are_reproducible() -> None:
    assert audit.canonical_sha(DATA) == DATA["core_sha256"]
    path = ROOT / "SUSY_V38_COMPLETE_THEORY_AUDIT.json"
    if path.is_file():
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(on_disk) == on_disk["core_sha256"]
        assert on_disk["established_full_predictive_closed_count"] == 0
