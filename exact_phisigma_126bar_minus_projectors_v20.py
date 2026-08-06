#!/usr/bin/env python3
"""All-component Phi-Sigma projectors in the physical 126bar (-i) basis.

The direct non-SUSY model defines 126bar_H as the -i Hodge eigenspace of
complex five-forms.  The older all-component projector export used the +i
basis.  Although both spaces have dimension 126, their coordinate matrices
cannot be mixed in a coupled Hessian.

This module rebuilds the six pure mixed quartic operators

    210_H^2 126bar_H^dag 126bar_H

in the canonical kinetic-orthonormal -i basis used by delta_r(), the 126bar
self-potential, and the cubic 210_H 126bar_H^dag 126bar_H calculation.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplets
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHISIGMA_126BAR_MINUS_PROJECTORS_V20.json"
OUT_MD = ROOT / "EXACT_PHISIGMA_126BAR_MINUS_PROJECTORS_V20.md"
CHANNELS = tuple(projectors.COMMON_CHANNEL_EIGENVALUES)
MONOMIALS = projectors.MONOMIALS
SPECTRAL_NAME = {
    "1": "1",
    "45": "45",
    "210": "210",
    "770": "770_plus_1050_plus_1050bar",
    "5940": "5940",
    "8910": "8910",
}


@lru_cache(maxsize=1)
def sigma_basis() -> tuple[direct.Form, ...]:
    return tuple(direct.anti_self_dual_five_form_basis())


def sigma_coordinates(form: direct.Form) -> np.ndarray:
    return np.asarray(
        [direct.sigma_kinetic_inner(state, form) for state in sigma_basis()],
        dtype=complex,
    )


@lru_cache(maxsize=1)
def full_contraction_tensor() -> np.ndarray:
    basis = sigma_basis()
    tensor = np.zeros((10, 210, 126), dtype=complex)
    for phi_index, phi_state in enumerate(projectors.FOUR_BASIS):
        tensor[:, phi_index, :] = direct.contraction_matrix(
            phi_state, list(basis)
        )
    return tensor


def full_sigma_operator(pair: np.ndarray) -> np.ndarray:
    value = np.asarray(pair, dtype=complex)
    if value.shape != (210, 210):
        raise ValueError("pair matrix must be 210x210")
    tensor = full_contraction_tensor()
    result = np.zeros((126, 126), dtype=complex)
    for vector_index in range(10):
        block = tensor[vector_index]
        result += block.conj().T @ value @ block
    return 0.5 * (result + result.conj().T)


@lru_cache(maxsize=1)
def all_component_coefficients() -> dict[str, dict[str, np.ndarray]]:
    projected = projectors.projected_monomials()
    return {
        channel: {
            monomial: full_sigma_operator(
                projected[SPECTRAL_NAME[channel]][monomial]
            )
            for monomial in MONOMIALS
        }
        for channel in CHANNELS
    }


def evaluate_full_sigma_operator(
    channel: str, p: float, a: float, omega: float
) -> np.ndarray:
    if channel not in CHANNELS:
        raise KeyError(channel)
    values = {
        "p2": p * p,
        "a2": a * a,
        "omega2": omega * omega,
        "p_a": p * a,
        "p_omega": p * omega,
        "a_omega": a * omega,
    }
    coefficients = all_component_coefficients()[channel]
    return sum(
        (values[name] * coefficients[name] for name in MONOMIALS),
        np.zeros((126, 126), dtype=complex),
    )


def _random_phi(rng: np.random.Generator) -> tuple[direct.Form, np.ndarray]:
    vector = rng.normal(size=210)
    vector /= np.linalg.norm(vector)
    form = {
        indices: complex(vector[index])
        for index, indices in enumerate(projectors.FOUR_INDICES)
        if abs(vector[index]) > 1.0e-14
    }
    return form, vector


def _chirality_audit() -> dict[str, float]:
    minus = sigma_basis()
    plus = tuple(triplets._hodge_basis("+i"))
    gram = np.asarray(
        [
            [direct.sigma_kinetic_inner(left, right) for right in minus]
            for left in minus
        ],
        dtype=complex,
    )
    cross = np.asarray(
        [
            [direct.sigma_kinetic_inner(left, right) for right in plus]
            for left in minus
        ],
        dtype=complex,
    )
    chirality = max(
        direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(state), direct.scale_form(state, 1j)
            )
        )
        for state in minus
    )
    delta = direct.delta_r()
    delta_coords = sigma_coordinates(delta)
    reconstructed = direct.add_forms(
        *[
            direct.scale_form(minus[index], coefficient)
            for index, coefficient in enumerate(delta_coords)
            if abs(coefficient) > 1.0e-13
        ]
    )
    delta_residual = direct.tensor_norm(
        direct.add_forms(reconstructed, direct.scale_form(delta, -1.0))
    )
    return {
        "minus_basis_gram_residual": float(
            np.max(np.abs(gram - np.eye(126)))
        ),
        "minus_basis_hodge_residual": float(chirality),
        "opposite_chirality_overlap_residual": float(np.max(np.abs(cross))),
        "delta_coordinate_reconstruction_residual": float(delta_residual),
    }


def _generic_reconstruction_audit() -> dict[str, Any]:
    rng = np.random.default_rng(20260806)
    phi_form, phi_vector = _random_phi(rng)
    pair = np.outer(phi_vector, phi_vector)
    powers = projectors.casimir_powers(pair)
    operators = {
        channel: full_sigma_operator(
            projectors.project_from_powers(
                powers, projectors.COMMON_CHANNEL_EIGENVALUES[channel]
            )
        )
        for channel in CHANNELS
    }
    total = sum(operators.values(), np.zeros((126, 126), dtype=complex))
    direct_map = direct.contraction_matrix(phi_form, list(sigma_basis()))
    expected = direct_map.conj().T @ direct_map
    noncommon = {
        name: float(
            np.max(
                np.abs(
                    full_sigma_operator(
                        projectors.project_from_powers(powers, eigenvalue)
                    )
                )
            )
        )
        for name, eigenvalue in projectors.NONCOMMON_EIGENVALUES.items()
    }
    minimum_norm = min(float(np.linalg.norm(value)) for value in operators.values())
    return {
        "six_channel_reconstruction_residual": float(
            np.max(np.abs(total - expected))
        ),
        "minimum_common_channel_operator_norm": minimum_norm,
        "noncommon_operator_residuals": noncommon,
        "maximum_hermiticity_residual": max(
            float(np.max(np.abs(value - value.conj().T)))
            for value in operators.values()
        ),
    }


def _delta_audit() -> dict[str, Any]:
    delta = sigma_coordinates(direct.delta_r())
    operators = {
        channel: evaluate_full_sigma_operator(channel, 1.0, 0.0, 0.0)
        for channel in CHANNELS
    }
    eigenvalues: dict[str, float] = {}
    residuals: dict[str, float] = {}
    for channel, operator in operators.items():
        eigenvalue = float(np.vdot(delta, operator @ delta).real)
        eigenvalues[channel] = eigenvalue
        residuals[channel] = float(
            np.linalg.norm(operator @ delta - eigenvalue * delta)
        )
    return {
        "delta_norm_residual": abs(float(np.vdot(delta, delta).real) - 1.0),
        "channel_eigenvalues": eigenvalues,
        "channel_eigenvector_residuals": residuals,
        "maximum_eigenvector_residual": max(residuals.values()),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    chirality = _chirality_audit()
    reconstruction = _generic_reconstruction_audit()
    delta = _delta_audit()
    checks = {
        "canonical_minus_basis": chirality["minus_basis_gram_residual"] < 1.0e-12,
        "minus_i_hodge_chirality": chirality["minus_basis_hodge_residual"] < 1.0e-12,
        "plus_and_minus_spaces_orthogonal": chirality[
            "opposite_chirality_overlap_residual"
        ] < 1.0e-12,
        "delta_reconstructs_in_minus_basis": chirality[
            "delta_coordinate_reconstruction_residual"
        ] < 1.0e-12,
        "six_channels_reconstruct_direct_contraction": reconstruction[
            "six_channel_reconstruction_residual"
        ] < 1.0e-11,
        "all_six_common_channels_nonzero": reconstruction[
            "minimum_common_channel_operator_norm"
        ] > 1.0e-8,
        "noncommon_channels_decouple": max(
            reconstruction["noncommon_operator_residuals"].values()
        ) < 1.0e-11,
        "operators_hermitian": reconstruction[
            "maximum_hermiticity_residual"
        ] < 1.0e-12,
        "delta_is_common_eigenvector": delta[
            "maximum_eigenvector_residual"
        ] < 1.0e-11,
        "complete_model_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_PHISIGMA_126BAR_MINUS_PROJECTORS_PASS"
            if not failures
            else "EXACT_PHISIGMA_126BAR_MINUS_PROJECTORS_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "chirality_audit": chirality,
        "generic_reconstruction_audit": reconstruction,
        "delta_R_audit": delta,
        "source_correction": {
            "physical_126bar_chirality": "-i",
            "legacy_all_component_export_chirality": "+i",
            "coordinate_matrices_interchangeable": False,
        },
        "newly_closed_subproblem": {
            "physical_126bar_all_component_mixed_projectors": not failures,
            "physical_126bar_delta_R_mixed_operators": not failures,
        },
        "remaining_blockers": {
            "rebuild_coupled_cross_Hessian_with_minus_basis": True,
            "solve_full_462_real_Hessian": True,
            "other_scalar_sectors": True,
            "physical_threshold_spectrum": True,
            "component_two_loop_matching": True,
            "unique_proton_lifetime": True,
        },
        "flag": {
            "physical_126bar_projector_basis_complete": not failures,
            "coupled_210_126bar_local_vacuum_complete": False,
            "complete_multifield_model": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The six all-component mixed projectors are reconstructed in the "
            "physical -i 126bar basis.  The old +i coordinate matrices must not "
            "be inserted into the Delta_R coupled Hessian."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Physical 126bar (-i) all-component mixed projectors — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "Next: rebuild every mixed cross derivative in the same -i basis and rerun the full 462-real Noether/Hessian gate.",
            "",
        ]
    )


def _default(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    raise TypeError(type(value).__name__)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
