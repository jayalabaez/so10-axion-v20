"""Tests for the V104 multipath frontier master."""
from __future__ import annotations

import copy
import json

import pytest

import susy_v91_multipath_g1_frontier_master_audit as common
import susy_v104_multipath_g1_frontier_master_audit as master


@pytest.fixture(scope="module")
def report():
    value = master.build_report()
    master.validate_report(value)
    return value


def test_core_is_canonical(report):
    assert report["core_sha256"] == common.canonical_sha(report)
    assert report["version"] == "V104"


def test_binds_immutable_parents(report):
    assert report["input_core_hashes"] == master.EXPECTED_CORES


def test_history_preserved_and_b104_appended(report):
    rows = report["route_matrix"]
    assert len(rows) == 32
    assert [row["ordinal"] for row in rows] == list(range(1, 33))
    b104 = rows[-1]
    assert b104["route_id"] == "B104"
    assert not b104["accepted"]
    assert not b104["same_action_microscopic_completion"]
    assert len(b104["selected_exact_scaffolds"]) == 4


def test_no_accepted_extension(report):
    assert all(not row["accepted"] for row in report["route_matrix"])
    assert report["consolidated_theory_card"]["accepted_extension_count"] == 0


def test_all_gates_open(report):
    gates = report["gate_ledger"]
    assert set(gates) == {"G" + str(index) for index in range(1, 9)}
    assert all(value.startswith("OPEN") for value in gates.values())


def test_theory_card_records_q2_confinement(report):
    card = report["consolidated_theory_card"]["q2_core_reduction"]
    assert card["Q2_confined_to_proper_subvariety"]
    assert not card["Q2_solved"]
    assert not card["Q2_excluded"]
    assert card["discriminant_h_independent"]
    assert card["R4core_t_and_M_powers_removed"] == [6, 2]
    assert card["leading_pair_h_resultant_nonzero"]


def test_acceptance_criteria_updates_a3(report):
    a3 = next(row for row in report["acceptance_criteria"] if row["id"] == "A3")
    assert "Q2_CONFINED" in a3["status"]


def test_strict_decision_and_next(report):
    decision = report["strict_master_decision"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]
    assert not decision["same_action_microscopic_parent_accepted"]
    assert report["next_required_action"]["id"] == master.NEXT_ID


def test_generated_json_matches(report):
    assert master.OUT_JSON.is_file()
    on_disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
    assert on_disk["core_sha256"] == report["core_sha256"]


def test_validate_rejects_mutation(report):
    mutated = copy.deepcopy(report)
    mutated["gate_ledger"]["G1"] = "CLOSED: fabricated"
    with pytest.raises(Exception):
        master.validate_report(mutated)
