from __future__ import annotations

import json
import math
from pathlib import Path

import susy_v46_spinor_kk_determinant_audit as v46
import susy_v47_four_spinor_mixed_kk_audit as audit


ROOT = Path(__file__).resolve().parent


def test_component_projectors_are_exact_8_plus_8_with_one_right_singlet() -> None:
    assert len(audit.INTERNAL_COMPONENTS) == 16
    assert sum(audit.P_LEFT) == 8
    assert sum(audit.P_RIGHT) == 8
    assert sum(audit.P_SU5_SINGLET) == 1
    assert all(left + right == 1 for left, right in zip(audit.P_LEFT, audit.P_RIGHT))
    assert all(
        singlet <= right
        for singlet, right in zip(audit.P_SU5_SINGLET, audit.P_RIGHT)
    )
    assert audit.INTERNAL_COMPONENTS[-1] == "nuC_SU5_singlet"


def test_primitive_u1f_normalization_and_operator_neutrality() -> None:
    assert audit.CHANNELS == (
        "HLF=16_+1",
        "HLA=bar16_-4",
        "HRA=16_-1",
        "HRF=bar16_+4",
    )
    assert audit.PRIMITIVE_U1F == {
        "HLF": 1,
        "HLA": -4,
        "HRA": -1,
        "HRF": 4,
        "ThetaPlus": 3,
        "ThetaMinus": -3,
        "Sigma": 0,
        "barSigma": 0,
    }
    report = audit.build_report()
    assert all(
        value == 0
        for value in report["field_and_component_contract"][
            "U1F_operator_charge_sums"
        ].values()
    )
    rendered = audit.render_markdown(report)
    for stale in ("HLF=16_+3", "HLA=bar16_-12", "HRA=16_-3", "HRF=bar16_+12"):
        assert stale not in rendered


def test_general_transfer_reduces_to_both_v46_characteristics() -> None:
    masses = (0.6, -0.25)
    length = 0.91
    b = 0.43
    boundary = [[0.0, b], [b, 0.0]]
    for signed_mass in (-2.1, -0.7, 0.0, 0.4, 1.8):
        z = signed_mass * signed_mass
        selected = audit.signed_characteristic(
            signed_mass, masses, length, boundary, (True, True)
        )
        unselected = audit.signed_characteristic(
            signed_mass, masses, length, boundary, (False, False)
        )
        assert math.isclose(
            selected.real,
            v46.d_plus_plus(z, masses[0], masses[1], length, b),
            rel_tol=3.0e-13,
            abs_tol=3.0e-13,
        )
        assert math.isclose(
            unselected.real,
            v46.d_minus_plus(z, masses[0], masses[1], length, b),
            rel_tol=3.0e-13,
            abs_tol=3.0e-13,
        )


def test_zero_factorization_for_arbitrary_mixed_hermitian_boundary() -> None:
    boundary = [
        [0.2, 0.3 + 0.1j, 1.4 - 0.2j, -0.7j],
        [0.3 - 0.1j, -0.5, 0.8 + 0.6j, 0.9],
        [1.4 + 0.2j, 0.8 - 0.6j, 0.4, -0.2 + 0.3j],
        [0.7j, 0.9, -0.2 - 0.3j, 0.1],
    ]
    assert audit.is_hermitian(boundary)
    for even in (audit.E_LEFT, audit.E_RIGHT, (True, False, True, False)):
        factors = audit.zero_factorization((0.7, -0.1, 0.4, -0.8), 1.2, boundary, even)
        assert abs(factors["direct"] - factors["factorized"]) < 2.0e-12


def test_only_even_even_block_controls_zero_nullity() -> None:
    # E channels 2,3 have no direct mass.  An invertible pure E--O matrix is
    # nevertheless unable to lift their exact chiral zero modes.
    cross_only = audit.theta_sigma_boundary_matrix(
        0.0, 0.0, 2.0, 3.0, su5_singlet=True
    )
    assert audit.matrix_rank(cross_only) == 4
    assert audit.zero_mode_nullity(cross_only, audit.E_RIGHT) == 2

    # Conversely, the full B can be singular while EBE is full rank.
    tuned = audit.theta_sigma_boundary_matrix(
        0.4, 0.6, 0.8, 0.3, su5_singlet=True
    )
    assert abs(audit.determinant(tuned)) < 1.0e-13
    assert audit.zero_mode_nullity(tuned, audit.E_RIGHT) == 0


def test_v47_exact_component_zero_counts() -> None:
    assert audit.full_zero_count(0.4, 0.6)["total_chiral_component_zero_modes"] == 0
    assert audit.full_zero_count(0.0, 0.6)["total_chiral_component_zero_modes"] == 16
    assert audit.full_zero_count(0.4, 0.0)["total_chiral_component_zero_modes"] == 16
    assert audit.full_zero_count(0.0, 0.0)["total_chiral_component_zero_modes"] == 32


def test_complex_holomorphic_mass_uses_hermitian_nambu_lift() -> None:
    mu = [[0.0j, 1.2 + 0.7j], [1.2 + 0.7j, 0.0j]]
    lifted = audit.nambu_lift(mu)
    assert audit.is_hermitian(lifted)
    assert audit.matrix_rank(lifted) == 4
    assert audit.holomorphic_zero_nullity(mu, (True, True)) == 0

    deficient = [[1.0j, 0.0j], [0.0j, 0.0j]]
    assert audit.holomorphic_zero_nullity(deficient, (True, True)) == 1


def test_hermitian_source_condition_cancels_boundary_form() -> None:
    boundary = audit.theta_sigma_boundary_matrix(
        0.4 + 0.2j, 0.7 - 0.1j, 1.1j, -0.3 + 0.5j, su5_singlet=True
    )
    assert audit.is_hermitian(boundary)
    f_psi = [1.0 + 0.2j, -0.4j, 0.7, -1.1 + 0.3j]
    f_phi = [0.1j, 0.8, -0.5 + 0.4j, 0.2]

    def multiply(matrix: list[list[complex]], vector: list[complex]) -> list[complex]:
        return [sum(row[col] * vector[col] for col in range(4)) for row in matrix]

    g_psi = [-value for value in multiply(boundary, f_psi)]
    g_phi = [-value for value in multiply(boundary, f_phi)]
    first = -sum(f_psi[i].conjugate() * g_phi[i] for i in range(4))
    second = sum(g_psi[i].conjugate() * f_phi[i] for i in range(4))
    assert abs(first + second) < 2.0e-13


def test_squared_characteristic_is_even_and_normalized_at_zero() -> None:
    boundary = audit.theta_sigma_boundary_matrix(
        0.3, 0.5, 1.2, -0.7, su5_singlet=True
    )
    masses = (0.2, -0.4, 0.8, -0.1)
    length = 0.77
    for z in (-1.3, -0.1, 0.0, 0.4, 2.2):
        value = audit.mass_squared_characteristic(z, masses, length, boundary, audit.E_RIGHT)
        mass = math.sqrt(z) if z >= 0.0 else 1j * math.sqrt(-z)
        direct = audit.signed_characteristic(mass, masses, length, boundary, audit.E_RIGHT)
        direct *= audit.signed_characteristic(-mass, masses, length, boundary, audit.E_RIGHT)
        assert abs(value - direct) < 2.0e-12


def test_large_sigma_makes_a_light_but_nonzero_finite_coupling_state() -> None:
    report = audit.build_report()
    roots = report["numerical_certificate"]["flat_singlet_lightest_absolute_signed_mass"]
    assert roots["Sigma_large"] > 0.0
    assert roots["Sigma_large"] < 0.02 * roots["Sigma_zero"]
    assert report["numerical_certificate"]["right_singlet_zero_factorization"]["direct"] != 0.0


def test_report_is_fail_closed_and_artifacts_are_current() -> None:
    report = audit.build_report()
    assert not report["decision"]["S2_closed"]
    assert report["decision"]["gates_promoted"] == []
    assert not report["decision"]["complete_theory"]
    assert "regulator" in report["regulated_spectral_determinant"]["cross_domain_warning"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(ROOT / name)
