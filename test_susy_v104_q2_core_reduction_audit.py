"""Tests for the V104 Q2 core-reduction route audit."""
from __future__ import annotations

import copy
import json

import pytest

import susy_v91_multipath_g1_frontier_master_audit as common
import susy_v104_q2_core_reduction_audit as route


@pytest.fixture(scope="module")
def report():
    value = route.build_report()
    route.validate_report(value)
    return value


def test_core_is_canonical(report):
    assert report["core_sha256"] == common.canonical_sha(report)
    assert report["version"] == "V104"


def test_binds_immutable_v103_cores(report):
    assert report["input_core_hashes"] == route.EXPECTED_CORES
    assert report["parent_obligation"] == route.PARENT_OBLIGATION


def test_wraps_the_helper_certificate(report):
    helper = report["q2_core_reduction"]
    assert helper["core_sha256"] == common.canonical_sha(helper)
    assert helper["discriminant"]["is_independent_of_h"]
    assert helper["leading_cores"]["R4core_t_and_M_powers_removed"] == [6, 2]


def test_all_gates_open(report):
    gates = report["gate_ledger"]
    assert set(gates) == {"G" + str(index) for index in range(1, 9)}
    assert all(value.startswith("OPEN") for value in gates.values())
    assert "confined to a proper subvariety" in gates["G8"] or "confined" in gates["G8"]


def test_terminal_decision_promotes_nothing(report):
    decision = report["terminal_decision"]
    assert decision["Q2_reduced_to_proper_subvariety"]
    assert not decision["Q2_solved"]
    assert not decision["Q2_excluded"]
    assert not decision["covariant_action_repair_constructed"]
    assert not decision["theory_complete"]
    assert decision["closed_gates"] == []


def test_next_obligation_is_f105(report):
    assert report["next_required_action"]["id"] == route.NEXT_ID
    assert "F105" in report["next_required_action"]["id"]


def test_crosscheck_flags(report):
    checks = report["cross_sector_scope_checks"]
    assert checks["helper_binds_identical_V103_route_and_member"]
    assert checks["Q2_confined_not_solved_not_excluded"]
    assert checks["no_gate_promotion"]


def test_generated_json_matches(report, tmp_path=None):
    route.build_report()  # smoke
    assert route.OUT_JSON.is_file()
    on_disk = json.loads(route.OUT_JSON.read_text(encoding="utf-8"))
    assert on_disk["core_sha256"] == report["core_sha256"]


def test_validate_rejects_mutation(report):
    mutated = copy.deepcopy(report)
    mutated["terminal_decision"]["Q2_solved"] = True
    with pytest.raises(Exception):
        route.validate_report(mutated)
