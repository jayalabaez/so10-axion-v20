#!/usr/bin/env python3
import numpy as np
import exact_phi2_h_126dag_210_1050_channels_v20 as gate


def test_injection_and_projectors():
    matrix = gate.injection_matrix(+1)
    assert matrix.shape == (2520, 210)
    assert np.linalg.matrix_rank(matrix, tol=1e-11) == 210
    assert np.max(np.abs(matrix.conj().T @ matrix - 3.0 * np.eye(210))) < 1e-12


def test_210_1050_split_and_contraction_kernel():
    p, a, omega = gate.singlet_basis()
    phi = gate.add_forms(p, gate.scale_form(a, 0.7), gate.scale_form(omega, -0.4))
    tensor = gate.phi2_bilinear(phi, phi, +1)
    p210 = gate.project_210(tensor, +1)
    p1050 = gate.project_1050(tensor, +1)
    assert gate.tensor_norm(tensor - p210 - p1050) < 1e-12
    assert gate.tensor_norm(gate.contract_vector_five(p1050)) < 1e-11
    assert abs(np.vdot(p210, p1050)) < 1e-11
    assert gate.tensor_norm(p210) > 1e-8
    assert gate.tensor_norm(p1050) > 1e-8


def test_symmetric_covariant_bilinear():
    p, a, omega = gate.singlet_basis()
    left = gate.add_forms(p, gate.scale_form(a, 0.7), gate.scale_form(omega, -0.4))
    right = gate.add_forms(gate.scale_form(a, -0.2), gate.scale_form(omega, 0.9))
    assert gate.tensor_norm(
        gate.phi2_bilinear(left, right) - gate.phi2_bilinear(right, left)
    ) < 1e-12
    base = gate.phi2_bilinear(left, right)
    for first, second in [(0, 1), (2, 7), (6, 9)]:
        lhs = gate.phi2_bilinear(gate.generator_action(left, first, second), right)
        lhs += gate.phi2_bilinear(left, gate.generator_action(right, first, second))
        rhs = gate.generator_action_vector_five(base, first, second)
        assert gate.tensor_norm(lhs - rhs) < 1e-11


def test_full_certificate_is_fail_closed():
    report = gate.build_report()
    assert report['n_failed'] == 0, report['failures']
    assert report['representation']['character_multiplicity'] == 2
    assert report['closure']['multiplicity_two_tensor_family_closed']
    assert report['closure']['1050_channel_closed_without_tabulated_CG']
    assert not report['closure']['all_64_live_G1_tensor_directions_closed']
    assert not report['closure']['G1_closed']
    assert not report['closure']['G2_closed']
    assert not report['flags']['whole_model_validated']
