#!/usr/bin/env python3
import exact_phi2_126dag126_six_contractions_v20 as gate


def test_graph_enumeration_and_selected_basis():
    graphs = gate.graph_solutions()
    assert len(graphs) == 15
    assert len(set(graphs)) == 15
    assert len(gate.SELECTED_EDGES) == 6
    assert all(edges in graphs for edges in gate.SELECTED_EDGES)
    assert all(gate.graph_subscript(edges).endswith('->') for edges in graphs)


def test_exact_integer_independence_witness():
    matrix = gate.witness_matrix()
    assert len(matrix) == 6
    assert all(len(row) == 6 for row in matrix)
    determinant = gate.bareiss_determinant(matrix)
    assert determinant == gate.EXPECTED_WITNESS_DETERMINANT
    assert determinant != 0


def test_all_generators_leave_basis_invariant():
    assert gate.infinitesimal_invariance_residual() < 1e-9


def test_complete_family_certificate_is_fail_closed():
    report = gate.build_report()
    assert report['n_failed'] == 0, report['failures']
    assert report['live_character_multiplicity'] == 6
    assert report['closure']['complete_six_invariant_tensor_basis_closed']
    assert report['covariance']['generators_checked'] == 45
    assert not report['closure']['all_64_live_G1_tensor_directions_closed']
    assert not report['closure']['G1_closed']
    assert not report['closure']['G2_closed']
    assert not report['flags']['whole_model_validated']
