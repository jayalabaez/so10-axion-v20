"""Regression tests for the V44 terminal theory decision."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v44_terminal_theory_decision as v44


REPORT = v44.build_report()


def test_v43_is_closed_as_complete_theory_but_not_mislabelled_empirically_falsified() -> None:
    current = REPORT["current_candidate"]
    assert current["complete_theory_status"] == "CLOSED_AND_FROZEN"
    assert current["complete_theory_exists_from_supplied_data"] is False
    assert current["empirically_falsified_by_a_joint_likelihood"] is False
    assert current["one_integrated_action_was_established"] is False
    assert current["closed_gate_count"] == 0
    assert current["total_gate_count"] == 8
    assert current["ordinary_additive_charge_iteration_allowed"] is False


def test_omitted_portal_is_independently_rederived_and_scoped() -> None:
    portal = REPORT["v43_portal_erratum"]
    assert portal["fields"] == ["NDirac", "E3", "Omega"]
    assert portal["total_charges"] == {
        "U1F": 0,
        "U1S": 0,
        "Z4R": 2,
        "Z5610": 0,
        "PQ_numerator_over_170": 0,
    }
    assert portal["all_fields_are_PS_singlets"]
    assert portal["renormalizable_superpotential_operator_is_allowed"]
    assert not portal["E3_was_in_original_scan_candidates"]
    assert ["NDirac", "E3", "Omega"] in portal[
        "full_table_PS_singlet_mixed_rows_through_degree_three"
    ]
    assert portal["full_table_direct_X_or_Zp_source_rows_through_degree_three"] == []
    assert portal["target_zero_NDirac_zero_E3_branch_survives_this_operator"]


def test_generic_singlet_mass_mixing_is_rank_two_not_silently_ignored() -> None:
    portal = REPORT["v43_portal_erratum"]
    assert portal["generic_singlet_mass_matrix_basis"] == ["E3", "E6", "N1", "N2", "N3"]
    assert portal["generic_example_mass_matrix_rank"] == 2
    assert portal["generic_example_mass_matrix_nullity"] == 3


def test_all_eight_gates_remain_open_and_scoped_results_are_retained() -> None:
    gates = REPORT["corrected_gate_ledger"]
    assert [row["gate"] for row in gates] == [f"G{index}" for index in range(1, 9)]
    assert all(not row["closed"] for row in gates)
    assert any("Dirac-messenger" in item for item in REPORT["surviving_scoped_results"])
    assert any("33Z/66Z" in item for item in REPORT["surviving_scoped_results"])


def test_5d_successor_is_one_fail_closed_route_not_a_promoted_theory() -> None:
    successor = REPORT["selected_successor"]
    assert successor["selected_route"] == "SEQUESTERED_5D_SPIN10_INTERVAL"
    assert successor["current_status"] == "PREREGISTERED_REPLACEMENT_ARCHITECTURE_NOT_INSTANTIATED"
    assert successor["current_closed_gate_count"] == 0
    assert successor["provisional_skeleton"]["V43_Omega_and_U1S_retained"] is False
    assert len(successor["ordered_stages"]) == 5
    assert [row["id"].split("-")[0] for row in successor["ordered_stages"]] == [
        "S0",
        "S1",
        "S2",
        "S3",
        "S4",
    ]
    assert "passes S0--S3 simultaneously" in successor["reopen_rule"]


def test_integrity_and_written_artifacts_are_reproducible() -> None:
    assert REPORT["n_failed_integrity_checks"] == 0
    assert all(REPORT["integrity_checks"].values())
    assert REPORT["core_sha256"] == v44.canonical_sha(REPORT)
    result = subprocess.run(
        [sys.executable, "-B", str(v44.JSON_PATH.parent / "susy_v44_terminal_theory_decision.py"), "--check"],
        cwd=v44.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V44_TERMINAL_THEORY_DECISION_CHECK_PASS" in result.stdout
    stored = json.loads(v44.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == v44.canonical_sha(stored)
