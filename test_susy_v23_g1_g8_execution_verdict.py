from __future__ import annotations

import copy
import json
import subprocess
import sys

import susy_v23_g1_g8_execution_verdict as verdict


def test_all_raw_sources_and_upstream_cores_are_pinned() -> None:
    report = verdict.build_report()
    assert report["checks"]["all_pinned_sources_match"] is True
    assert all(row["matches"] for row in report["source_manifest"])
    assert set(report["upstream_core_pins"]) == set(verdict.UPSTREAMS)
    assert all(
        row["matches"] and row["canonical_core_valid"]
        for row in report["upstream_core_pins"].values()
    )


def test_exact_route_decision_and_primary_frontier() -> None:
    report = verdict.build_report()
    decision = report["route_decision"]
    routes = {row["route"]: row for row in decision["routes"]}
    assert decision["complete_theory_selected"] is None
    assert decision["primary_research_frontier"] == "flipped_missing_partner_route"
    assert decision["decision_valid"] is True
    assert routes["chacko_unchanged_route"]["disposition"] == (
        "EXACTLY_REJECTED_AT_STATED_UNCHANGED_ROUTE_SCOPE"
    )
    assert routes["barr_raby_route"]["disposition"] == (
        "EXACTLY_REJECTED_AS_ALL_ORDER_COMPLETION"
    )
    assert routes["flipped_missing_partner_route"]["disposition"] == (
        "PRIMARY_RESEARCH_FRONTIER__NOT_PROMOTED_TO_COMPLETE_THEORY"
    )
    assert routes["chacko_unchanged_route"]["architecture_exactly_rejected"] is True
    assert routes["barr_raby_route"]["architecture_exactly_rejected"] is True
    assert routes["flipped_missing_partner_route"]["architecture_exactly_rejected"] is False
    assert all(row["accepted_as_complete_theory"] is False for row in routes.values())


def test_all_full_G1_through_G8_gates_remain_false() -> None:
    report = verdict.build_report()
    assert report["closure_counts"] == {"closed": 0, "open": 8}
    assert [row["gate"] for row in report["gates"]] == [f"G{i}" for i in range(1, 9)]
    assert all(
        row["closed"] is False and row["full_gate_claim"] is False
        for row in report["gates"]
    )
    terminal = report["terminal_verdict"]
    assert terminal["complete_G1_G8_solution_exists_in_this_repository"] is False
    assert terminal["safe_to_claim_a_complete_predictive_theory"] is False
    assert terminal["new_complete_physics_model_created"] is False
    assert terminal["reproducible_research_progress_created"] is True


def test_zero_W_scaffolds_are_not_executable_SARAH_models() -> None:
    report = verdict.build_report()
    classification = report["model_artifact_classification"]
    for route in ("v22r_degree4_eft", "barr_raby_route", "flipped_missing_partner_route"):
        row = classification[route]
        assert row["wolfram_syntax_zero_W_stub"] is True
        assert row["executable_SARAH_model_landed"] is False
        model = (verdict.ROOT / row["path"]).read_text(encoding="utf-8")
        assert model.count("SuperPotential = 0;") == 1
        assert model.count("NameOfStates = {GaugeES};") == 1
    assert classification["barr_raby_route"]["Wolfram_syntax_parse_observed"] is True
    assert classification["barr_raby_route"]["SARAH_initialization_attested"] is False
    assert classification["flipped_missing_partner_route"]["Wolfram_syntax_parse_observed"] is True
    assert classification["flipped_missing_partner_route"]["SARAH_initialization_attested"] is False


def test_terminal_checks_encode_the_exact_physics_boundary() -> None:
    report = verdict.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["checks"]["Chacko_unchanged_route_is_exactly_rejected"] is True
    assert report["checks"]["Barr_Raby_all_order_architecture_is_exactly_rejected"] is True
    assert report["checks"]["flipped_route_is_primary_research_frontier_only"] is True
    assert report["checks"]["flipped_published_structural_ranks_are_7_and_3"] is True
    assert report["checks"]["flipped_anomalous_U1A_Planck_and_GS_completion_remain_open"] is True
    assert report["checks"]["flipped_formal_running_is_not_promoted_to_physical_RGE_closure"] is True
    assert report["checks"]["flipped_single_10_KSVZ_extension_is_exactly_rejected"] is True


def test_missing_sources_fail_closed(tmp_path) -> None:
    report = verdict.build_report(tmp_path)
    assert report["overall_state"] == "FAIL_CLOSED"
    assert report["n_failed"] == len(verdict.SOURCE_PINS)
    assert report["closure_counts"] == {"closed": 0, "open": 8}
    assert all(row["closed"] is False for row in report["gates"])
    assert report["route_decision"]["decision_valid"] is False
    assert report["terminal_verdict"]["complete_G1_G8_solution_exists_in_this_repository"] is False


def test_frozen_outputs_core_hash_and_check_cli() -> None:
    report = verdict.build_report()
    assert json.loads(verdict.OUT_JSON.read_text(encoding="utf-8")) == report
    assert verdict.OUT_MD.read_text(encoding="utf-8") == verdict.markdown(report)
    assert verdict.canonical_sha(report) == report["core_sha256"]
    changed = copy.deepcopy(report)
    changed["terminal_verdict"]["safe_to_claim_a_complete_predictive_theory"] = True
    assert verdict.canonical_sha(changed) != verdict.canonical_sha(report)
    completed = subprocess.run(
        [sys.executable, str(verdict.ROOT / "susy_v23_g1_g8_execution_verdict.py"), "--check"],
        cwd=verdict.ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
