from __future__ import annotations

import subprocess
import sys

import susy_v29_g1_microscopic_completion_verdict as verdict


def test_upstream_pins_and_cores_match() -> None:
    report = verdict.build_report()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["V27_core_matches"] is True
    assert report["checks"]["V28_core_matches"] is True


def test_all_17_models_have_unique_exact_hidden_factor_counts() -> None:
    rows = verdict.build_report()["published_model_ledger"]
    assert len(rows) == 17
    assert len({row["model_id"] for row in rows}) == 17
    counts = {row["model_id"]: row["maximum_independent_hidden_gauge_kinetic_functions"] for row in rows}
    assert counts["r15f1"] == 5
    assert counts["r26f4"] == 10
    assert counts["r33f4"] == 11


def test_condensate_hessian_rank_theorem_is_applied_to_every_model() -> None:
    report = verdict.build_report()
    theorem = report["condensate_Hessian_rank_theorem"]
    assert theorem["rank_bound"] == "rank(W_ij)<=rank(Q)<=m"
    assert theorem["none_of_these_evasions_is_derived_in_the_17_models"] is True
    for row in report["published_model_ledger"]:
        assert (
            row["standard_condensate_moduli_Hessian_rank_upper_bound"]
            == row["maximum_independent_hidden_gauge_kinetic_functions"]
        )


def test_maximum_published_hidden_span_is_11_and_envelope_gap_is_40() -> None:
    bound = verdict.build_report()["all_model_bound"]
    assert bound["V28_conservative_complex_moduli_envelope"] == 51
    assert bound["maximum_published_hidden_factor_count"] == 11
    assert bound["model_attaining_maximum"] == "r33f4"
    assert bound["minimum_uncovered_envelope_directions"] == 40
    assert bound["standard_published_hidden_charge_span_can_realize_V28_rank_51"] is False


def test_unpublished_visible_physics_is_not_invented() -> None:
    blockers = verdict.build_report()["other_independent_full_G1_blockers"]
    assert blockers["published_complete_Yukawa_couplings"] is False
    assert blockers["published_twisted_sector_Yukawa_rules"] is False
    assert blockers["published_SUSY_breaking_soft_terms_for_rigid_models"] is False
    assert blockers["published_all_order_operator_and_coefficient_contract"] is False
    assert blockers["published_executable_UV_to_component_matching"] is False


def test_full_g1_stays_fail_closed_while_v28_is_retained() -> None:
    report = verdict.build_report()
    gate = report["G1_gate"]
    assert gate["closed"] is False
    assert gate["full_gate_claim"] is False
    assert gate["V28_local_51_field_scaffold_retained"] is True
    assert gate["V28_promoted_to_microscopic_completion"] is False
    assert report["terminal_decision"]["finish_full_G1_with_V28_and_the_17_published_models"] is False
    assert report["n_failed"] == 0, report["failures"]


def test_frozen_outputs_and_cli() -> None:
    report = verdict.build_report()
    assert verdict.canonical_sha(report) == report["core_sha256"]
    assert verdict.check_outputs(report) is True
    completed = subprocess.run(
        [sys.executable, "-B", str(verdict.ROOT / "susy_v29_g1_microscopic_completion_verdict.py"), "--check"],
        cwd=verdict.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
