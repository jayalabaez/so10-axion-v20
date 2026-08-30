from __future__ import annotations

import json

import numpy as np
import pytest

import susy_v50_full_same_action_collar_audit as audit


def test_A_Xi_C_basis_spans_full_sp8() -> None:
    result = audit.sp_span_certificate(4)
    assert result["basis_count"] == 36
    assert result["matrix_rank"] == 36
    assert result["expected_dimension_n_2n_plus_1"] == 36
    assert result["maximum_Hamiltonian_residual"] < 1.0e-12
    assert result["spanned"]


def test_sp_generator_requires_symmetric_A_and_Xi() -> None:
    zero = np.zeros((2, 2))
    with pytest.raises(ValueError):
        audit.sp_generator(np.asarray([[0.0, 1.0], [0.0, 0.0]]), zero, zero)
    with pytest.raises(ValueError):
        audit.sp_generator(zero, np.asarray([[0.0, 1.0], [0.0, 0.0]]), zero)


def test_O7_O8_exact_IBP_normal_form_and_Darboux_congruence() -> None:
    data = audit.deterministic_collar_data(4)
    callback = audit.deterministic_collar_blocks(data)
    normal = audit.collar_normal_form(0.37, 0.23, callback)
    assert audit.maximum_abs(normal["J"] - (normal["D_raw"] - normal["D_raw"].T)) < 1.0e-13
    assert audit.maximum_abs(normal["S"] - (normal["D_raw"] + normal["D_raw"].T) / 2.0) < 1.0e-13
    assert audit.maximum_abs(normal["J"] + normal["J"].T) < 1.0e-13
    assert audit.transpose_symmetry_residual(normal["Q"]) < 1.0e-12
    darboux = normal["Darboux"]
    assert audit.maximum_abs(darboux.T @ audit.j_form(4) @ darboux - normal["J"]) < 1.0e-12


def test_canonical_generator_is_Hamiltonian_through_profile() -> None:
    callback = audit.deterministic_collar_blocks(audit.deterministic_collar_data(4))
    minima = []
    for point in np.linspace(0.0, 1.0, 17):
        _, checks = audit.canonical_generator(float(point), 0.29, callback)
        assert checks["raw_J_skew_residual"] < 1.0e-12
        assert checks["Q_symmetric_residual"] < 1.0e-12
        assert checks["canonical_Hamiltonian_residual"] < 1.0e-10
        minima.append(checks["K_min_singular_value"])
    assert min(minima) > 0.5


def test_constant_A_limit_is_the_exact_strong_wall_shear() -> None:
    channels = 2
    amat = np.asarray([[0.4, 0.07], [0.07, -0.2]], dtype=np.complex128)

    def callback(t: float, mass: complex) -> dict[str, np.ndarray]:
        zero = np.zeros((channels, channels), dtype=np.complex128)
        return {
            "A": amat,
            "Xi": zero,
            "C": zero,
            "R7": zero,
            "R8": zero,
            "R7_prime": zero,
            "R8_prime": zero,
            "spectral_metric": np.zeros((2 * channels, 2 * channels)),
        }

    transfer = audit.path_ordered_collar_transfer(0.0, callback, channels, steps=7)
    expected = np.block(
        [
            [np.eye(channels), np.zeros((channels, channels))],
            [-amat, np.eye(channels)],
        ]
    )
    assert audit.maximum_abs(transfer - expected) < 1.0e-12


def test_path_ordered_transfer_is_symplectic_and_convergent() -> None:
    callback = audit.deterministic_collar_blocks(audit.deterministic_collar_data(4))
    coarse = audit.path_ordered_collar_transfer(0.31, callback, 4, steps=18)
    fine = audit.path_ordered_collar_transfer(0.31, callback, 4, steps=36)
    assert audit.symplectic_residual(coarse, 4) < 1.0e-11
    assert audit.symplectic_residual(coarse, 4, hermitian=True) < 1.0e-11
    assert np.linalg.norm(fine - coarse, 2) < 2.0e-4


def test_bulk_and_total_transfer_are_symplectic() -> None:
    masses = (0.0, 0.07, -0.04, 0.025)
    even = (True, False, False, True)
    callback = audit.deterministic_collar_blocks(audit.deterministic_collar_data(4))
    bulk = audit.bulk_transfer(0.22, masses, 0.93, even)
    total = audit.total_transfer(0.22, callback, masses, 0.93, even, steps=18)
    assert audit.symplectic_residual(bulk, 4) < 1.0e-12
    assert audit.symplectic_residual(total, 4) < 1.0e-11


def test_endpoint_graphs_are_maximal_isotropic_on_real_slice() -> None:
    host = audit.endpoint_data(4, 601)
    source = audit.endpoint_data(4, 611)
    p0 = audit.endpoint_pencil(0.31, host)
    p1 = audit.endpoint_pencil(0.31, source)
    assert audit.hermitian_residual(p0) < 1.0e-12
    assert audit.hermitian_residual(p1) < 1.0e-12
    assert audit.graph_isotropy_residual(p0, +1.0) < 1.0e-12
    assert audit.graph_isotropy_residual(p1, -1.0) < 1.0e-12


def test_positive_admissible_cone_has_strict_witness() -> None:
    result = audit.representative_certificate()["positive_norm"]
    assert min(result.values()) > 0.0
    assert result["collar_mixed_Schur_min_eigenvalue"] > 0.25


def test_enlarged_characteristic_is_undivided_and_matches_schur_form() -> None:
    callback = audit.deterministic_collar_blocks(audit.deterministic_collar_data(4))
    masses = (0.0, 0.07, -0.04, 0.025)
    even = (True, False, False, True)
    host = audit.endpoint_data(4, 601)
    source = audit.endpoint_data(4, 611)
    for mass in (-0.4, 0.0, 0.31, 1.1):
        transfer = audit.total_transfer(mass, callback, masses, 0.93, even, steps=18)
        full = audit.enlarged_characteristic(transfer, mass, host, source)
        assert full.shape == (8, 8)
        assert audit.undivided_reduced_identity(transfer, mass, host, source) < 1.0e-10


def test_deterministic_poles_residue_locality_and_Wilson_response() -> None:
    result = audit.representative_certificate()
    poles = result["undivided_characteristic"]
    wilson = result["Wilson_witness"]
    assert len(poles["first_three_signed_positive_roots"]) == 3
    assert poles["first_three_signed_positive_roots"] == sorted(
        poles["first_three_signed_positive_roots"]
    )
    assert poles["determinant_at_first_root_abs"] < 1.0e-10
    assert abs(poles["first_root_derivative"]) > 1.0e-5
    assert poles["near_pole_full_residue_residual"] < 1.0e-5
    assert wilson["G00_finite"]
    assert wilson["norm8_over_norm4"] < 0.08


def test_profile_callback_is_a_regulator_independent_interface() -> None:
    channels = 2

    def local_constrained_profile(t: float, mass: complex) -> dict[str, np.ndarray]:
        zero = np.zeros((channels, channels), dtype=np.complex128)
        profile = 6.0 * t * (1.0 - t)
        return {
            "A": profile * np.diag([0.3, 0.5]),
            "Xi": profile * np.diag([0.08, 0.12]),
            "C": profile * np.asarray([[0.01, 0.04], [-0.03, 0.02]]),
            "R7": zero,
            "R8": zero,
            "R7_prime": zero,
            "R8_prime": zero,
            "spectral_metric": 0.04 * np.eye(2 * channels),
        }

    transfer = audit.path_ordered_collar_transfer(0.2, local_constrained_profile, channels, steps=20)
    assert np.isfinite(transfer).all()
    assert audit.symplectic_residual(transfer, channels) < 1.0e-11


def test_report_closes_only_the_supported_clause_scope() -> None:
    report = audit.build_report()
    clauses = report["C3_C4_C7_decision"]
    assert clauses["C3"]["status"] == "PASS_AT_DECLARED_QUADRATIC_ACTION_LEVEL"
    assert clauses["C4"]["status"] == "PASS_ON_EXPLICIT_POSITIVE_ADMISSIBLE_CONE_AT_QUADRATIC_LEVEL"
    assert clauses["C7"]["status"] == "PARTIAL"
    assert len(clauses["C7"]["remaining"]) == 3
    assert report["G2_decision"]["closed"] is False
    assert report["G2_decision"]["closed_full_gate_count"] == 1
    assert report["n_failed_integrity_checks"] == 0


def test_report_hash_is_deterministic_and_action_contains_named_blocks() -> None:
    report = audit.build_report()
    theorem_text = json.dumps(report["action_and_domain_theorem"])
    for required in ("A,Xi,C", "R7", "R8", "J", "Darboux", "auxiliary"):
        assert required in theorem_text
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_checked_artifacts_are_current() -> None:
    audit.check_artifacts()
    stored = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == audit.build_report()["core_sha256"]
