#!/usr/bin/env python3
import exact_unique_hsigma_chiral_quartics_v20 as gate


def test_graph_enumeration_and_selected_contractions():
    graphs_a = gate.graph_solutions(gate.FAMILY_A_DEGREES)
    graphs_b = gate.graph_solutions(gate.FAMILY_B_DEGREES)
    assert len(graphs_a) == 3
    assert len(graphs_b) == 3
    assert gate.FAMILY_A_SELECTED in graphs_a
    assert gate.FAMILY_B_SELECTED in graphs_b


def test_selected_contractions_are_nonzero():
    hdag, sigma, sigmadag, _, _ = gate.deterministic_fields(1)
    assert abs(gate.invariant_hdag_sigma2_sigmadag(hdag, sigma, sigmadag)) > 1e-8
    assert abs(gate.invariant_hdag2_sigma2(hdag, sigma)) > 1e-8


def test_all_generators_leave_both_invariants_unchanged():
    residuals = gate.covariance_residuals(1)
    assert residuals['hdag_sigma2_sigmadag'] < 1e-9
    assert residuals['hdag2_sigma2'] < 1e-9


def test_certificate_is_exact_and_fail_closed():
    report = gate.build_report()
    assert report['n_failed'] == 0, report['failures']
    assert report['families']['10dag_126bar2_126dag']['character_multiplicity'] == 1
    assert report['families']['10dag2_126bar2']['character_multiplicity'] == 1
    assert report['closure']['unique_10dag_126bar2_126dag_tensor_closed']
    assert report['closure']['unique_10dag2_126bar2_tensor_closed']
    assert not report['closure']['G2_closed']
    assert not report['flags']['whole_model_validated']
