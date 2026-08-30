from __future__ import annotations

import json
import subprocess
import sys

import susy_v27_g1_architecture_change_audit as audit


def test_source_pins_and_upstream_cores_match() -> None:
    report = audit.build_report()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["V26_core_matches"] is True
    assert report["checks"]["V25_core_matches"] is True
    assert report["checks"]["V24_non_GS_core_matches"] is True


def test_every_candidate_is_tested_against_the_same_six_requirements() -> None:
    report = audit.build_report()
    requirement_ids = {
        row["requirement_id"] for row in report["acceptance_requirements"]
    }
    assert len(requirement_ids) == 6
    assert all(
        set(candidate["requirements"]) == requirement_ids
        for candidate in report["candidate_ledger"]
    )


def test_no_candidate_passes_and_no_cross_theory_union_is_allowed() -> None:
    report = audit.build_report()
    assert len(report["candidate_ledger"]) == 6
    assert all(candidate["full_G1_pass"] is False for candidate in report["candidate_ledger"])
    assert report["conjunction_rule"]["Frankenstein_union_allowed"] is False
    assert report["closure_counts"]["candidate_routes_passing"] == 0


def test_v26_and_rigid_dbrane_candidates_have_complementary_but_incomplete_progress() -> None:
    report = audit.build_report()
    candidates = {row["candidate_id"]: row for row in report["candidate_ledger"]}
    v26 = candidates["V26_BOTTOM_UP_GS_RACETRACK"]
    rigid = candidates["RIGID_DBRANE_PS_2026"]
    assert v26["requirements"]["R6_executable_matching_to_visible_source"]["passes"] is True
    assert v26["requirements"]["R1_microscopic_UV_source"]["passes"] is False
    assert rigid["requirements"]["R1_microscopic_UV_source"]["passes"] is True
    assert rigid["requirements"]["R3_all_order_operator_and_coefficient_contract"]["passes"] is False
    assert rigid["requirements"]["R4_all_moduli_stabilized_and_branch_quotient"]["passes"] is False


def test_architecture_change_is_audited_without_false_promotion() -> None:
    report = audit.build_report()
    decision = report["new_physics_decision"]
    assert decision["new_physics_was_allowed_and_tested"] is True
    assert decision["replace_V24_source_now"] is False
    assert decision["retain_V26_as_qualified_dynamical_GS_EFT_frontier"] is True
    assert decision["full_G1_closed"] is False
    assert report["G1_gate"]["closed"] is False
    assert report["G1_gate"]["full_gate_claim"] is False


def test_generated_uv_submission_schema_is_strict_and_complete() -> None:
    schema = audit.uv_input_schema()
    required = set(schema["required"])
    assert schema["additionalProperties"] is False
    assert {
        "microscopic_source",
        "selector_and_anomalies",
        "operator_contract",
        "moduli_and_vacuum",
        "hidden_and_parity",
        "executable_matching",
    } <= required
    for name in required - {"candidate_id", "evidence_manifest", "all_acceptance_checks_pass"}:
        assert schema["properties"][name]["additionalProperties"] is False
    assert schema["properties"]["all_acceptance_checks_pass"]["const"] is True


def test_schema_parses_and_frozen_outputs_match() -> None:
    report = audit.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert audit.check_outputs(report) is True
    frozen_schema = json.loads(audit.SCHEMA_PATH.read_text(encoding="utf-8"))
    assert frozen_schema == audit.uv_input_schema()
    completed = subprocess.run(
        [sys.executable, "-B", str(audit.ROOT / audit.__file__.split("\\")[-1]), "--check"],
        cwd=audit.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
