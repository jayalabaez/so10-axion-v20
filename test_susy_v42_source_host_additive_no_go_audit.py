"""Regression tests for the V42 source--host additive-separation no-go."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v42_source_host_additive_no_go_audit as audit


ROOT = Path(__file__).resolve().parent


def test_starting_v40_product_really_allows_the_source_host_bridges() -> None:
    report = audit.build_report()
    ledger = report["V40_charge_starting_point"]
    assert ledger["all_existing_V40_renormalizable_terms_allowed"]
    assert ledger["all_required_terms_allowed"]
    assert ledger["all_listed_bridges_already_allowed"]
    signatures = ledger["V40_field_signatures"]
    assert signatures["STheta"] == signatures["X"] == signatures["Zp"]


def test_additive_no_go_covers_ordinary_discrete_and_r_factors_componentwise() -> None:
    report = audit.build_report()
    theorem = report["additive_no_go"]
    assert "direct product" in theorem["assumptions"][0]
    assert theorem["universal_forbidden_goal_fails"] == [
        "X ThetaPlus ThetaMinus cannot be forbidden by A.",
        "Zp ThetaPlus ThetaMinus cannot be forbidden by A.",
    ]
    finite = report["finite_cyclic_crosscheck"]
    assert finite["constructed_assignments_checked"] == sum(order * order for order in range(2, 65))
    assert finite["counterexamples"] == []
    assert finite["all_finite_cyclic_examples_confirm_the_symbolic_proof"]


def test_generic_isolated_product_branch_is_not_mistaken_for_a_coupled_vacuum() -> None:
    report = audit.build_report()
    coupled = report["coupled_F_branch_boundary"]
    assert coupled["F_terms_on_that_putative_product_branch"]["F_X"] == "partial_X W_host + lambda_X mu_F^2 = lambda_X mu_F^2"
    assert coupled["F_terms_on_that_putative_product_branch"]["F_Zp"] == "partial_Zp W_host + lambda_Z mu_F^2 = lambda_Z mu_F^2"
    assert coupled["generic_result"]["isolated_source_times_unperturbed_host_branch_is_F_flat"] is False
    assert coupled["coupled_full_host_F_D_branch_solved"] is False
    assert coupled["coupled_full_host_F_D_branch_disproved"] is False


def test_fail_closed_decision_and_spurion_boundary() -> None:
    report = audit.build_report()
    decision = report["decision"]
    assert decision["current_V41_source_host_symmetry_protected_separation_exists"] is False
    assert decision["charged_spurion_extension_completed"] is False
    assert decision["full_gate_closed"] == []
    boundary = report["charged_spurion_evasion_boundary"]
    assert boundary["can_be_used_as_evidence_for_current_V41_full_source"] is False
    assert boundary["can_be_used_to_close_a_gate_without_that_reaudit"] is False


def test_write_check_round_trip() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "susy_v42_source_host_additive_no_go_audit.py"), "--write", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SUSY V42 source-host additive no-go audit: PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V42_SOURCE_HOST_ADDITIVE_NO_GO_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == audit.STATUS
    assert payload["core_sha256"] == audit.canonical_sha(payload)
