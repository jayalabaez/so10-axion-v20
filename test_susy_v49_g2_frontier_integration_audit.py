from __future__ import annotations

import json

import susy_v49_g2_frontier_integration_audit as audit


def test_all_upstream_core_hashes_are_current() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["all_input_core_hashes_valid"]
    for name, path in audit.INPUTS.items():
        value = audit.load_hashed_json(path)
        assert report["input_core_hashes"][name] == value["core_sha256"]


def test_strictly_4d_sources_remove_only_the_spurious_source_tower() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["strictly_4D_sources_have_no_KK_tower"]
    assert report["integrity_checks"]["regulator_artifact_rejects_microscopic_closure"]
    c2 = next(row for row in report["G2_closure_assessment"] if row["id"] == "C2")
    assert c2["status"] == "conditional"
    assert "bilocal" in c2["blocker"]


def test_strong_collar_Hc_terms_are_leading_not_remainders() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["strong_collar_Hc_terms_are_unsuppressed"]
    result = next(row for row in report["V49_exact_results"] if row["id"] == "E31")
    assert "O(1)" in result["statement"]
    assert "Hc(s)" in result["statement"]


def test_exact_quartic_census_closes_C1_abstractly() -> None:
    report = audit.build_report()
    result = next(row for row in report["V49_exact_results"] if row["id"] == "E32")
    assert result["value"] == {"sector_count": 12, "direction_count": 23}
    c1 = next(row for row in report["G2_closure_assessment"] if row["id"] == "C1")
    assert c1["status"] == "pass"


def test_general_collar_transfer_is_symplectic_but_not_full_kernel() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["full_collar_generator_certificate_is_symplectic"]
    c3 = next(row for row in report["G2_closure_assessment"] if row["id"] == "C3")
    c7 = next(row for row in report["G2_closure_assessment"] if row["id"] == "C7")
    assert c3["status"] == "partial"
    assert c7["status"] == "partial"
    assert "zero-Hc-counterterm" in c7["blocker"]


def test_restricted_64_trace_kernel_passes_only_its_scope() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["restricted_pencil_integrity_passes"]
    assert report["integrity_checks"]["restricted_pencil_rejects_G2_closure"]
    result = next(row for row in report["V49_exact_results"] if row["id"] == "E35")
    assert result["value"]["coordinate_count"] == 64
    assert result["value"]["pencil_verdict"] == "G2_REMAINS_OPEN"


def test_only_C1_and_C6_pass_the_frozen_contract() -> None:
    report = audit.build_report()
    assert report["fully_passed_clauses"] == ["C1", "C6"]
    assert report["number_of_clauses"] == 7
    assert report["integrity_checks"]["G2_conjunction_is_false"]


def test_gate_ledger_stays_one_of_eight() -> None:
    report = audit.build_report()
    closed = [row["gate"] for row in report["gate_ledger"] if row["closed"]]
    assert closed == ["G1"]
    assert report["scientific_verdict"]["full_gates_closed"] == 1
    assert not report["scientific_verdict"]["G2_closed"]


def test_smallest_patch_targets_every_live_blocker() -> None:
    report = audit.build_report()
    joined = " ".join(report["smallest_next_closure_patch"])
    for token in ("deconstruction", "A,Xi,C", "positivity", "second smooth profile", "SO10-to-PS"):
        assert token in joined


def test_artifacts_are_current_and_hashed() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    assert all(row["exists"] and row["sha256"] for row in report["source_manifest"])
