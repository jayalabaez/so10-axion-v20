from __future__ import annotations

import json

import numpy as np
import pytest

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_source_operator_wilson_audit as v48
import susy_v49_generalized_boundary_pencil_audit as audit


def test_passive_pencil_is_hermitian_and_has_positive_derivative_metric() -> None:
    mass = np.asarray([[0.2, 0.03j], [-0.03j, -0.1]], dtype=np.complex128)
    kinetic = np.asarray([[0.3, 0.02], [0.02, 0.25]], dtype=np.complex128)
    coupling = np.asarray([[0.04, -0.01j]], dtype=np.complex128)
    hamiltonian = np.asarray([[2.0]], dtype=np.complex128)
    metric = np.asarray([[1.2]], dtype=np.complex128)
    pencil = audit.passive_boundary_pencil(
        0.15, mass, kinetic, coupling, hamiltonian, metric
    )
    derivative_metric = audit.passive_derivative_metric(
        0.15, kinetic, coupling, hamiltonian, metric
    )
    assert audit.hermitian_residual(pencil) < 1.0e-12
    assert audit.minimum_eigenvalue(derivative_metric) > 0.0


def test_passive_pencil_rejects_nonpositive_auxiliary_metric() -> None:
    with pytest.raises(ValueError):
        audit.passive_boundary_pencil(
            0.1,
            np.eye(2),
            np.eye(2),
            np.ones((1, 2)),
            np.eye(1),
            -np.eye(1),
        )


def test_normal_derivative_relation_requires_hermitian_graph() -> None:
    arel = np.asarray([[1.0, 0.1], [0.1, 1.0]])
    target = np.asarray([[0.2, 0.03j], [-0.03j, -0.1]])
    brel = arel @ target
    assert np.max(np.abs(audit.relation_to_graph_pencil(arel, brel) - target)) < 1.0e-12
    with pytest.raises(ValueError):
        audit.relation_to_graph_pencil(np.eye(2), np.asarray([[0.0, 1.0], [0.0, 0.0]]))


def test_generalized_kernel_reduces_to_v48_when_wall_pencils_vanish() -> None:
    masses = (0.0, 0.0, 0.0, 0.0)
    boundary = np.asarray(
        v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -1.0 / 6.0, su5_singlet=True)
    )
    zero = np.zeros((4, 4), dtype=np.complex128)
    k49, n49 = audit.generalized_host_pair(
        0.21, masses, 1.0, boundary, v47.E_RIGHT, 0.05, zero
    )
    k48, n48 = v48.regulated_host_pair(
        0.21, masses, 1.0, boundary, v47.E_RIGHT, 0.05
    )
    assert np.max(np.abs(k49 - k48)) < 1.0e-12
    assert np.max(np.abs(n49 - n48)) < 1.0e-12


def test_ps_clebsch_norm_and_permutation() -> None:
    higgs = np.asarray([[0.07, -0.02], [0.03, 0.05]])
    clebsch = audit.ps_higgs_clebsch(higgs)
    assert clebsch.shape == (8, 8)
    assert np.sum(np.abs(clebsch) ** 2) == pytest.approx(4.0 * np.sum(np.abs(higgs) ** 2))
    permutation = audit.v47_to_ps_right_permutation()
    assert np.max(np.abs(permutation @ permutation.T - np.eye(8))) < 1.0e-12


def test_full_64_vertex_contains_all_four_hermitian_blocks() -> None:
    higgs = np.asarray([[0.07, -0.02], [0.03, 0.05]])
    vertex = audit.full_64_ps_vertex(higgs, (0.31, -0.23, 0.19, -0.17))
    assert vertex.shape == (64, 64)
    assert audit.hermitian_residual(vertex) < 1.0e-12
    clebsch_nonzero = np.count_nonzero(np.abs(audit.ps_higgs_clebsch(higgs)) > 1.0e-14)
    assert np.count_nonzero(np.triu(np.abs(vertex) > 1.0e-14, 1)) == 4 * clebsch_nonzero


def test_full_64_current_has_six_family_vertices_and_expected_support() -> None:
    higgs = np.asarray([[0.07, -0.02], [0.03, 0.05]])
    q = np.asarray([[0.01 * (1 + i + j) for j in range(8)] for i in range(3)])
    qc = -0.8 * q
    current = audit.full_64_current(
        higgs, q, qc, (0.11, -0.07, 0.05), (0.09, 0.04, -0.06)
    )
    assert current.shape == (64,)
    assert np.count_nonzero(np.abs(current) > 1.0e-14) == 16
    support = np.flatnonzero(np.abs(current) > 1.0e-14)
    assert all(index % 4 in (0, 2) for index in support)


def test_full_64_bulk_blocks_are_finite_and_correct_size() -> None:
    zero = np.zeros((4, 4), dtype=np.complex128)
    kblock, nblock = audit.full_64_bulk_blocks(
        0.13, (0.0, 0.0, 0.0, 0.0), 1.0, 0.4, 0.6, 0.2, -1.0 / 6.0, 0.05, zero
    )
    assert kblock.shape == (64, 64)
    assert nblock.shape == (64, 64)
    assert np.isfinite(kblock).all()
    assert np.isfinite(nblock).all()


def test_representative_poles_residue_locality_and_decoupling() -> None:
    result = audit.representative_certificate()
    roots = result["roots_and_residue"]
    assert len(roots["first_three_positive_roots"]) == 3
    assert roots["first_three_positive_roots"] == sorted(roots["first_three_positive_roots"])
    assert roots["det_at_first_abs"] < 1.0e-9
    assert abs(roots["first_derivative"]) > 1.0e-4
    assert roots["near_pole_residue_residual"] < 5.0e-6
    assert result["euclidean_locality"]["norm8_over_norm4"] < 0.04
    assert result["auxiliary_decoupling"]["monotone"]
    assert result["auxiliary_decoupling"]["norm16_over_norm8"] < 0.6


def test_collar_linear_remainder_scales_as_second_order() -> None:
    result = audit.representative_certificate()["collar_linear_remainder"]
    assert result["exact_minus_linear_norm"] > 0.0
    assert result["normalized_by_m2_epsilon2"] < 2.0


def test_full_component_universal_admissible_trials_pass() -> None:
    result = audit.full_component_certificate()
    assert result["coordinate_count"] == 64
    assert result["independent_nonzero_vertex_entries"] == result["expected_nonzero_entries"]
    assert result["current_nonzero_entries"] == result["expected_current_nonzero_entries"]
    assert result["full_kernel_finite"]
    for row in result["deterministic_admissible_tensor_trials"]:
        assert row["kinetic_min_eigenvalue"] > 0.0
        assert row["host_hermitian_residual"] < 1.0e-12
        assert row["kernel_finite"]


def test_action_contract_includes_every_v48_adversarial_omission() -> None:
    action = audit.retained_v49_action_contract()
    text = json.dumps(action)
    for required in (
        "mu_H",
        "O7/O8",
        "nabla5(HLFc)",
        "nabla5(HRAc)",
        "four conjugate Hc-Hc portals",
        "B4_source",
        "Zhat",
    ):
        assert required in text


def test_report_is_honest_and_deterministically_hashed() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert report["G2_decision"]["closed"] is False
    assert report["G2_decision"]["closed_gate_count"] == 1
    assert len(report["G2_decision"]["precise_remaining_objects"]) == 6
    assert any(
        "strong-collar generator" in item
        for item in report["G2_decision"]["precise_remaining_objects"]
    )
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_checked_artifacts_are_current() -> None:
    audit.check_artifacts()
    stored = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == audit.build_report()["core_sha256"]
