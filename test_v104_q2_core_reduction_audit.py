"""Tests for the V104 Q2 core-reduction helper."""
from __future__ import annotations

import copy

import pytest

import susy_v91_multipath_g1_frontier_master_audit as common
import v104_q2_core_reduction_audit as q2


@pytest.fixture(scope="module")
def report():
    value = q2.build_certificate()
    q2.validate_certificate(value)
    return value


def test_core_is_canonical(report):
    assert report["core_sha256"] == common.canonical_sha(report)


def test_binds_immutable_v103_geometry(report):
    assert report["input_core_hashes"]["v103_route"] == q2.V103_ROUTE_CORE
    assert report["input_core_hashes"]["v103_quartic"] == q2.V103_QUARTIC_CORE


def test_leading_coefficient_identity_is_exact(report):
    identity = report["leading_coefficient_identity"]
    assert identity["verified_exactly"]
    assert identity["A2_nonzero_on_Q2"]
    assert identity["statement"].startswith("A2 = -1296 * t^6 * M")


def test_l_zero_residual_is_the_quadratic(report):
    assert report["l_zero_quadratic"]["verified_exactly"]


def test_discriminant_is_h_independent(report):
    discriminant = report["discriminant"]
    assert discriminant["h_degree"] == 0
    assert discriminant["is_independent_of_h"]
    assert discriminant["rational_q_requires_Delta_square_in_C_X"]


def test_leading_cores_have_exact_t_and_M_content(report):
    cores = report["leading_cores"]
    assert cores["R4core_t_and_M_powers_removed"] == [6, 2]
    assert cores["C43core_t_and_M_powers_removed"] == [3, 2]
    assert cores["R4core_term_count"] > 0
    assert cores["C43core_term_count"] > 0


def test_modular_witnesses_are_nonzero_on_Q2(report):
    witnesses = report["fixed_modular_witnesses"]
    assert witnesses["modulus"] == 101
    assert witnesses["leading_pair_resultant_is_nonzero_polynomial"]
    points = witnesses["points"]
    assert [(row["t"], row["p"]) for row in points] == [(2, 1), (3, 1), (2, 3)]
    assert all(row["on_Q2_M_nonzero"] for row in points)
    assert any(row["nonzero"] for row in points)
    assert [row["h_resultant_mod101"] for row in points] == [28, 97, 91]


def test_q2_is_confined_but_open(report):
    conclusion = report["q2_conclusion"]
    assert conclusion["R4_and_C43_are_both_necessary_on_Q2"]
    assert conclusion["h_resultant_nonzero_so_no_open_two_parameter_family"]
    assert not conclusion["Q2_solved"]
    assert not conclusion["Q2_excluded"]
    assert conclusion["degenerate_ell4_ell3_zero_locus_retained"]


def test_no_gate_or_rank_promotion(report):
    decision = report["terminal_decision"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]
    assert not decision["actual_nonzero_original_section_constructed"]
    assert not decision["original_exact_MW_rank_computed"]
    assert not decision["same_action_microscopic_parent_accepted"]


def test_validate_rejects_mutation(report):
    mutated = copy.deepcopy(report)
    mutated["q2_conclusion"]["Q2_solved"] = True
    with pytest.raises(Exception):
        q2.validate_certificate(mutated)
