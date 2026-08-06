#!/usr/bin/env python3
"""Joint 482-real Schur envelope for all selected H10 cross blocks.

At H=0 on the verified p+Delta_R vacuum, three complex operator coefficients
produce old-field--H mixed Hessian blocks:

* mu_D multiplies Phi Hdag Sigmabar + h.c.;
* eta_210 multiplies the canonical 210 channel of Phi^2 H Sigmabar-dag+h.c.;
* eta_1050 multiplies the canonical 1050 channel of that family.

The complete selected-vacuum H-only block is supplied by
``exact_complete_h10_selected_vacuum_mass_block_v20`` and includes both the
Hermitian endomorphism and the holomorphic H^2 S/Phi17 B block.

Let A be the positive 429-dimensional physical Hessian of the verified
210+126bar vacuum and B(c) the 429x20 mixed block, linear in the six real
coefficient components

  c=(Re mu_D, Im mu_D, Re eta_210, Im eta_210,
     Re eta_1050, Im eta_1050).

The enlarged 449-dimensional physical quotient is positive definite iff

  L(c) = M_H - B(c)^T A^{-1} B(c)  > 0.

This module constructs the six basis blocks and the operator-valued quadratic
Gram tensor G_rs, so

  B(c)^T A^{-1}B(c) = sum_rs c_r c_s G_rs.

The condition is exact and necessary-and-sufficient for this selected H=0
local Hessian. It is not the nonzero electroweak vacuum or complete G2
potential.
"""
from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import coupled_p_delta_physical_chirality_search_v20 as coupled
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_complete_h10_selected_vacuum_mass_block_v20 as hmass
import exact_muD_482_schur_stability_v20 as mud
import exact_phi2_h126dag_selected_vacuum_projection_v20 as projection
import exact_phi_hdag_sigmabar_cubic_audit_v20 as cubic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_JOINT_H10_CROSS_SCHUR_STABILITY_V20.json"
OUT_MD = ROOT / "EXACT_JOINT_H10_CROSS_SCHUR_STABILITY_V20.md"
OLD_DIM = coupled.TOTAL_DIM
H_REAL = 20
FULL_DIM = OLD_DIM + H_REAL
COEFFICIENT_NAMES = (
    "Re_mu_D",
    "Im_mu_D",
    "Re_eta_210",
    "Im_eta_210",
    "Re_eta_1050",
    "Im_eta_1050",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def _real_Hdag_map_from_real_phi(matrix: np.ndarray) -> np.ndarray:
    """H-real x Phi-real Hessian for 2 Re(Hdag M phi)."""
    value = np.asarray(matrix, dtype=complex)
    output = np.empty((2 * value.shape[0], value.shape[1]), dtype=float)
    output[0::2, :] = 2.0 * value.real
    output[1::2, :] = 2.0 * value.imag
    return output


def _real_H_map_from_real_phi(matrix: np.ndarray) -> np.ndarray:
    """H-real x Phi-real Hessian for 2 Re(H^T M phi)."""
    value = np.asarray(matrix, dtype=complex)
    output = np.empty((2 * value.shape[0], value.shape[1]), dtype=float)
    output[0::2, :] = 2.0 * value.real
    output[1::2, :] = -2.0 * value.imag
    return output


def _quartic_complex_HPhi_blocks() -> dict[str, np.ndarray]:
    channels = projection.channels
    p, delta_dagger = projection.physical_background()
    sigma_vector = channels.five_to_vector(delta_dagger)
    four_basis = tuple(
        {indices: 1.0 + 0.0j} for indices in channels.C4
    )
    result: dict[str, np.ndarray] = {}
    for name, projector in projection.channel_projectors().items():
        matrix = np.empty((channels.N, len(channels.C4)), dtype=complex)
        for column, state in enumerate(four_basis):
            variation = channels.phi2_bilinear(state, p, +1) + channels.phi2_bilinear(
                p, state, +1
            )
            matrix[:, column] = projection.h_coefficient_vector(
                projector(variation), sigma_vector
            )
        result[name] = matrix
    return result


def _cubic_old_to_h(coefficient: complex) -> np.ndarray:
    background = coupled.background()
    p_form = background["p_form"]
    delta_form = background["delta_form"]
    sigma_basis = coupled.minus_gate.sigma_basis()
    value = complex(coefficient)

    h_sigma_complex = value * direct.contraction_matrix(p_form, sigma_basis)
    h_sigma_real = 2.0 * mud.complex_map_real_interleaved(h_sigma_complex)

    h_phi_complex = value * np.column_stack(
        [
            cubic.contract_vector(phi_state, delta_form)
            for phi_state in cubic.four_form_basis()
        ]
    )
    h_phi_real = _real_Hdag_map_from_real_phi(h_phi_complex)

    old_to_h = np.zeros((OLD_DIM, H_REAL), dtype=float)
    old_to_h[: coupled.PHI_DIM, :] = h_phi_real.T
    old_to_h[coupled.PHI_DIM :, :] = h_sigma_real.T
    return old_to_h


def _quartic_old_to_h(
    eta_210: complex, eta_1050: complex
) -> np.ndarray:
    raw = _quartic_complex_HPhi_blocks()
    combined = complex(eta_210) * raw["210"] + complex(eta_1050) * raw["1050"]
    h_phi_real = _real_H_map_from_real_phi(combined)
    old_to_h = np.zeros((OLD_DIM, H_REAL), dtype=float)
    old_to_h[: coupled.PHI_DIM, :] = h_phi_real.T
    return old_to_h


def combined_old_to_h(
    *, mu_d: complex, eta_210: complex, eta_1050: complex
) -> np.ndarray:
    return _cubic_old_to_h(mu_d) + _quartic_old_to_h(eta_210, eta_1050)


def coefficient_vector(
    *, mu_d: complex, eta_210: complex, eta_1050: complex
) -> np.ndarray:
    return np.asarray(
        [
            complex(mu_d).real,
            complex(mu_d).imag,
            complex(eta_210).real,
            complex(eta_210).imag,
            complex(eta_1050).real,
            complex(eta_1050).imag,
        ],
        dtype=float,
    )


@lru_cache(maxsize=1)
def basis_blocks() -> dict[str, Any]:
    old = mud.old_hessian_data()
    definitions = (
        (1.0 + 0.0j, 0.0j, 0.0j),
        (1.0j, 0.0j, 0.0j),
        (0.0j, 1.0 + 0.0j, 0.0j),
        (0.0j, 1.0j, 0.0j),
        (0.0j, 0.0j, 1.0 + 0.0j),
        (0.0j, 0.0j, 1.0j),
    )
    old_blocks = []
    physical_blocks = []
    rows = []
    for name, (mu_d, eta_210, eta_1050) in zip(COEFFICIENT_NAMES, definitions):
        block = combined_old_to_h(
            mu_d=mu_d, eta_210=eta_210, eta_1050=eta_1050
        )
        physical = old["physical"].T @ block
        gauge_residual = float(np.max(np.abs(block.T @ old["orbit"])))
        old_blocks.append(block)
        physical_blocks.append(physical)
        rows.append(
            {
                "name": name,
                "old_rank": int(np.linalg.matrix_rank(block, 1.0e-11)),
                "physical_rank": int(np.linalg.matrix_rank(physical, 1.0e-11)),
                "old_frobenius": float(np.linalg.norm(block)),
                "physical_frobenius": float(np.linalg.norm(physical)),
                "gauge_residual": gauge_residual,
            }
        )
    return {
        "old": np.stack(old_blocks),
        "physical": np.stack(physical_blocks),
        "rows": rows,
    }


def linear_combination_from_basis(coefficients: np.ndarray) -> dict[str, np.ndarray]:
    values = np.asarray(coefficients, dtype=float).reshape(6)
    basis = basis_blocks()
    return {
        "old": np.tensordot(values, basis["old"], axes=(0, 0)),
        "physical": np.tensordot(values, basis["physical"], axes=(0, 0)),
    }


@lru_cache(maxsize=1)
def gram_data() -> dict[str, Any]:
    old = mud.old_hessian_data()
    physical_blocks = basis_blocks()["physical"]
    solved = np.stack(
        [np.linalg.solve(old["physical_hessian"], block) for block in physical_blocks]
    )
    operators = np.empty((6, 6, H_REAL, H_REAL), dtype=float)
    norm_matrix = np.empty((6, 6), dtype=float)
    for left in range(6):
        for right in range(6):
            operator = 0.5 * (
                physical_blocks[left].T @ solved[right]
                + physical_blocks[right].T @ solved[left]
            )
            operators[left, right] = operator
            norm_matrix[left, right] = np.linalg.norm(operator)
    symmetry_residual = float(
        np.max(np.abs(operators - np.swapaxes(operators, 0, 1)))
    )
    return {
        "operators": operators,
        "operator_frobenius_norms": norm_matrix,
        "coefficient_names": list(COEFFICIENT_NAMES),
        "basis_physical_ranks": [row["physical_rank"] for row in basis_blocks()["rows"]],
        "symmetry_residual": symmetry_residual,
    }


def schur_from_coefficients(coefficients: np.ndarray) -> dict[str, Any]:
    values = np.asarray(coefficients, dtype=float).reshape(6)
    block = linear_combination_from_basis(values)["physical"]
    old = mud.old_hessian_data()
    solved = np.linalg.solve(old["physical_hessian"], block)
    direct_operator = 0.5 * (
        block.T @ solved + (block.T @ solved).T
    )
    gram_operator = np.einsum(
        "r,s,rsij->ij",
        values,
        values,
        gram_data()["operators"],
        optimize=True,
    )
    eigenvalues = np.linalg.eigvalsh(direct_operator)
    return {
        "operator": direct_operator,
        "gram_operator": gram_operator,
        "eigenvalues": eigenvalues,
        "lambda_min": float(eigenvalues[0]),
        "lambda_max": float(eigenvalues[-1]),
        "rank": int(np.linalg.matrix_rank(direct_operator, 1.0e-10)),
        "symmetry_residual": float(
            np.max(np.abs(direct_operator - direct_operator.T))
        ),
        "gram_reconstruction_residual": float(
            np.max(np.abs(direct_operator - gram_operator))
        ),
    }


def complete_h_block_for_soft_mass(
    *, soft_mass_squared: float, b_value: complex
) -> np.ndarray:
    return hmass.complete_mass_matrix(
        b_value=b_value,
        m_h_squared=soft_mass_squared,
        lambda_phih_1=0.0,
        lambda_phih_45=0.0,
        lambda_phih_54=0.0,
        lambda_hsigma_1=0.0,
        lambda_hsigma_45=0.0,
    )["matrix"]


def loewner_data(
    coefficients: np.ndarray, *, soft_mass_squared: float, b_value: complex
) -> dict[str, Any]:
    schur = schur_from_coefficients(coefficients)
    h_block = complete_h_block_for_soft_mass(
        soft_mass_squared=soft_mass_squared, b_value=b_value
    )
    loewner = 0.5 * (
        h_block - schur["operator"] + (h_block - schur["operator"]).T
    )
    eigenvalues = np.linalg.eigvalsh(loewner)
    return {
        "matrix": loewner,
        "eigenvalues": eigenvalues,
        "lambda_min": float(eigenvalues[0]),
        "lambda_max": float(eigenvalues[-1]),
        "positive_definite": bool(eigenvalues[0] > 1.0e-9),
        "semidefinite": bool(eigenvalues[0] >= -1.0e-8),
        "symmetry_residual": float(np.max(np.abs(loewner - loewner.T))),
        "schur": schur,
    }


def critical_soft_mass(coefficients: np.ndarray, *, b_value: complex) -> float:
    schur = schur_from_coefficients(coefficients)["operator"]
    fixed_h = complete_h_block_for_soft_mass(
        soft_mass_squared=0.0, b_value=b_value
    )
    return float(np.linalg.eigvalsh(schur - fixed_h)[-1])


def full_and_physical_spectra(
    coefficients: np.ndarray, *, soft_mass_squared: float, b_value: complex
) -> dict[str, Any]:
    old = mud.old_hessian_data()
    blocks = linear_combination_from_basis(coefficients)
    h_block = complete_h_block_for_soft_mass(
        soft_mass_squared=soft_mass_squared, b_value=b_value
    )
    physical = np.block(
        [
            [old["physical_hessian"], blocks["physical"]],
            [blocks["physical"].T, h_block],
        ]
    )
    full = np.block(
        [
            [old["hessian"], blocks["old"]],
            [blocks["old"].T, h_block],
        ]
    )
    physical = 0.5 * (physical + physical.T)
    full = 0.5 * (full + full.T)
    physical_eigenvalues = np.linalg.eigvalsh(physical)
    full_eigenvalues = np.linalg.eigvalsh(full)
    tolerance = 2.0e-7
    return {
        "physical_dimension": int(physical.shape[0]),
        "full_dimension": int(full.shape[0]),
        "physical_eigenvalues": physical_eigenvalues,
        "full_eigenvalues": full_eigenvalues,
        "physical_zero_modes": int(
            np.sum(np.abs(physical_eigenvalues) < tolerance)
        ),
        "physical_negative_modes": int(
            np.sum(physical_eigenvalues < -tolerance)
        ),
        "physical_minimum": float(physical_eigenvalues[0]),
        "full_zero_modes": int(np.sum(np.abs(full_eigenvalues) < tolerance)),
        "full_negative_modes": int(np.sum(full_eigenvalues < -tolerance)),
        "full_minimum": float(full_eigenvalues[0]),
    }


def cubic_unit_reconstruction_audit() -> dict[str, Any]:
    reconstructed = combined_old_to_h(
        mu_d=1.0, eta_210=0.0, eta_1050=0.0
    )
    authoritative = mud.mixed_block_per_unit_mu()["old_to_h"]
    return {
        "maximum_abs_residual": float(
            np.max(np.abs(reconstructed - authoritative))
        ),
        "reconstructed_rank": int(np.linalg.matrix_rank(reconstructed, 1.0e-11)),
        "authoritative_rank": int(np.linalg.matrix_rank(authoritative, 1.0e-11)),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    hmass_report = hmass.build_report()
    projection_report = projection.build_report()
    old = mud.old_hessian_data()
    cubic_reconstruction = cubic_unit_reconstruction_audit()
    basis = basis_blocks()
    gram = gram_data()

    couplings = {
        "mu_D": 0.42 + 0.18j,
        "eta_210": 0.16 - 0.09j,
        "eta_1050": -0.11 + 0.07j,
    }
    coefficients = coefficient_vector(**{
        "mu_d": couplings["mu_D"],
        "eta_210": couplings["eta_210"],
        "eta_1050": couplings["eta_1050"],
    })
    direct_combined = combined_old_to_h(
        mu_d=couplings["mu_D"],
        eta_210=couplings["eta_210"],
        eta_1050=couplings["eta_1050"],
    )
    basis_combined = linear_combination_from_basis(coefficients)["old"]
    linearity_residual = float(
        np.max(np.abs(direct_combined - basis_combined))
    )
    gauge_residual = float(np.max(np.abs(direct_combined.T @ old["orbit"])))

    b_value = 0.31 - 0.22j
    critical = critical_soft_mass(coefficients, b_value=b_value)
    above_mass = critical + 0.75
    equality_mass = critical
    below_mass = critical - 0.25

    above_loewner = loewner_data(
        coefficients, soft_mass_squared=above_mass, b_value=b_value
    )
    equality_loewner = loewner_data(
        coefficients, soft_mass_squared=equality_mass, b_value=b_value
    )
    below_loewner = loewner_data(
        coefficients, soft_mass_squared=below_mass, b_value=b_value
    )
    above_spectrum = full_and_physical_spectra(
        coefficients, soft_mass_squared=above_mass, b_value=b_value
    )
    equality_spectrum = full_and_physical_spectra(
        coefficients, soft_mass_squared=equality_mass, b_value=b_value
    )
    below_spectrum = full_and_physical_spectra(
        coefficients, soft_mass_squared=below_mass, b_value=b_value
    )
    schur = above_loewner["schur"]

    checks = {
        "complete_selected_H_block_executes": hmass_report["n_failed"] == 0,
        "selected_210_1050_projection_executes": projection_report["n_failed"] == 0,
        "old_physical_Hessian_positive": old["physical_eigenvalues"][0] > 1.0e-6,
        "old_gauge_rank_33": old["gauge_rank"] == 33,
        "cubic_complex_realification_recovers_authoritative_unit_block": (
            cubic_reconstruction["maximum_abs_residual"] < 1.0e-12
        ),
        "all_six_basis_blocks_annihilate_gauge_orbit": all(
            row["gauge_residual"] < 1.0e-9 for row in basis["rows"]
        ),
        "six_real_coefficient_directions_constructed": (
            basis["old"].shape[0] == 6 and basis["physical"].shape[0] == 6
        ),
        "combined_block_linear_in_all_coefficients": linearity_residual < 1.0e-12,
        "combined_block_annihilates_gauge_orbit": gauge_residual < 1.0e-9,
        "operator_gram_symmetric": gram["symmetry_residual"] < 1.0e-10,
        "schur_gram_reconstructs_direct_operator": schur[
            "gram_reconstruction_residual"
        ] < 1.0e-9,
        "joint_schur_positive_semidefinite": schur["lambda_min"] > -1.0e-8,
        "above_bound_loewner_positive": above_loewner["positive_definite"],
        "above_bound_physical_positive": (
            above_spectrum["physical_negative_modes"] == 0
            and above_spectrum["physical_zero_modes"] == 0
            and above_spectrum["physical_minimum"] > 1.0e-7
        ),
        "above_bound_full_preserves_33_gauge_zeros": (
            above_spectrum["full_zero_modes"] == 33
            and above_spectrum["full_negative_modes"] == 0
        ),
        "equality_has_extra_physical_zero": (
            abs(equality_loewner["lambda_min"]) < 1.0e-7
            and equality_spectrum["physical_zero_modes"] >= 1
            and equality_spectrum["full_zero_modes"] >= 34
        ),
        "below_bound_has_tachyon": (
            below_loewner["lambda_min"] < -1.0e-7
            and below_spectrum["physical_negative_modes"] >= 1
            and below_spectrum["full_negative_modes"] >= 1
        ),
        "complete_G2_potential_not_claimed": True,
        "nonzero_electroweak_backreaction_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "JOINT_H10_CROSS_SCHUR_ENVELOPE_CLOSED__EW_BACKREACTION_OPEN"
                if not failures
                else "JOINT_H10_CROSS_SCHUR_ENVELOPE_FAILED"
            ),
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "dimensions": {
                "old_full": OLD_DIM,
                "old_physical": int(old["physical_hessian"].shape[0]),
                "H10_real": H_REAL,
                "enlarged_full": FULL_DIM,
                "enlarged_physical": int(old["physical_hessian"].shape[0] + H_REAL),
                "gauge_rank": old["gauge_rank"],
            },
            "coefficient_basis": {
                "names": list(COEFFICIENT_NAMES),
                "rows": basis["rows"],
                "operator_gram_frobenius_norms": gram[
                    "operator_frobenius_norms"
                ],
            },
            "benchmark_couplings": couplings,
            "benchmark_coefficient_vector": coefficients,
            "b_effective": b_value,
            "cubic_unit_reconstruction": cubic_reconstruction,
            "combined_linearity_residual": linearity_residual,
            "combined_gauge_residual": gauge_residual,
            "joint_schur": {
                "rank": schur["rank"],
                "lambda_min": schur["lambda_min"],
                "lambda_max": schur["lambda_max"],
                "gram_reconstruction_residual": schur[
                    "gram_reconstruction_residual"
                ],
                "theorem": (
                    "M_H - B(c)^T A_phys^{-1} B(c) is positive definite"
                ),
                "quadratic_form": (
                    "S(c)=sum_{r,s=1}^6 c_r c_s G_rs"
                ),
            },
            "critical_soft_mass_squared": critical,
            "benchmarks": {
                "above": {
                    "soft_mass_squared": above_mass,
                    "loewner_minimum": above_loewner["lambda_min"],
                    "spectrum": above_spectrum,
                },
                "equality": {
                    "soft_mass_squared": equality_mass,
                    "loewner_minimum": equality_loewner["lambda_min"],
                    "spectrum": equality_spectrum,
                },
                "below": {
                    "soft_mass_squared": below_mass,
                    "loewner_minimum": below_loewner["lambda_min"],
                    "spectrum": below_spectrum,
                },
            },
            "flags": {
                "complete_selected_H_only_mass_block_used": not failures,
                "complex_muD_block_inserted": not failures,
                "complex_eta210_block_inserted": not failures,
                "complex_eta1050_block_inserted": not failures,
                "six_real_coefficient_operator_gram_derived": not failures,
                "joint_necessary_and_sufficient_local_bound": not failures,
                "33_gauge_goldstones_preserved_above_bound": not failures,
                "tachyon_below_bound_exhibited": not failures,
                "complete_G2_component_potential": False,
                "nonzero_electroweak_backreaction": False,
                "global_vacuum": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Promote the remaining G1 families into one arbitrary-component "
                "64-direction potential evaluator and generate its complete "
                "gradient/Hessian (G2)."
            ),
            "verdict": (
                "The selected H=0 482-real local Hessian now has an exact joint "
                "Schur/Loewner envelope for the complex mu_D, eta_210, and "
                "eta_1050 cross couplings, using the complete H-only quadratic "
                "block. Above the bound the 449-dimensional physical quotient "
                "is positive and the full Hessian has exactly 33 gauge zeros; "
                "equality adds a flat mode and crossing the bound creates a "
                "tachyon. Electroweak backreaction and full G2 remain open."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Joint H10 cross-coupling Schur stability envelope\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
