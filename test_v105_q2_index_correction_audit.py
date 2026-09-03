from __future__ import annotations
import copy
import pytest
import susy_v91_multipath_g1_frontier_master_audit as common
import v105_q2_index_correction_audit as fix

@pytest.fixture(scope="module")
def report():
    value = fix.build_certificate()
    assert fix.validate_certificate(value)
    return value

def test_hash(report):
    assert report["core_sha256"] == common.canonical_sha(report)

def test_v104_core_values_are_superseded(report):
    assert report["old_witness_values_mod101"] == [28, 97, 91]
    assert report["corrected_witness_values_mod101"] == [65, 52, 20]
    assert report["old_witness_values_mod101"] != report["corrected_witness_values_mod101"]

def test_corrected_witnesses_still_confine_q2(report):
    assert all(row["on_Q2_M_nonzero"] and row["nonzero"] for row in report["corrected_witnesses"])
    assert report["conclusion"]["corrected_leading_pair_resultant_is_nonzero_polynomial"]
    assert report["conclusion"]["Q2_still_confined_to_a_proper_subvariety"]

def test_scope_remains_open(report):
    assert not report["conclusion"]["Q2_solved"]
    assert not report["conclusion"]["Q2_excluded"]
    assert not report["conclusion"]["gate_promotion"]
    assert not report["conclusion"]["old_saved_cores_may_be_used_for_F105"]

def test_delta_fact_survives(report):
    assert report["corrected_linear_reduction"]["delta_h_degree"] == 0

def test_mutation_rejected(report):
    changed = copy.deepcopy(report)
    changed["conclusion"]["Q2_excluded"] = True
    with pytest.raises(Exception):
        fix.validate_certificate(changed)
