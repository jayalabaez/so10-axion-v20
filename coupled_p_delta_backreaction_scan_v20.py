#!/usr/bin/env python3
"""Search the complete 462-real P+Delta_R coupled Hessian.

The exact first-stage Phi=P vacuum and the exact fixed-P Delta_R Hessian are
both known.  This module constructs the missing 210--126bar cross Hessian for
all six pure mixed quartics and for the unique cubic Phi Sigma^dag Sigma.  It
then imposes exact singlet stationarity, retunes the two radial mass parameters,
projects out the 33 SO(10)-to-SM gauge tangents, and maximizes the minimum
physical eigenvalue over a bounded set of couplings.

This is a deterministic numerical existence scan.  A successful point is a
local coupled-vacuum certificate, not a proof of global uniqueness and not the
complete model with 10_H, S and Phi17.
"""
from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_pati_salam_global_vacuum_v20 as phi_gate
import exact_p_delta_second_stage_hessian_v20 as fixed_gate
import exact_phisigma_all_component_projectors_v20 as mixed_gate
import exact_phisigma_casimir_projectors_v20 as projectors
import exact_210_126bar_cubic_clebsch_v20 as cubic_gate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "COUPLED_P_DELTA_BACKREACTION_SCAN_V20.json"
OUT_MD = ROOT / "COUPLED_P_DELTA_BACKREACTION_SCAN_V20.md"
PHI_DIM = 210
SIGMA_COMPLEX_DIM = 126
SIGMA_REAL_DIM = 252
TOTAL_DIM = 462
CHANNELS = ("1", "45", "210", "770", "5940", "8910")
VARIABLES = ("rho_phi",) + tuple(f"lambda_{q}" for q in CHANNELS) + ("mu_eta",)

INITIAL = np.asarray([8.0, 31.5, 0.0, 0.0, 1.25, 0.0, 0.0, -0.375], dtype=float)


def _interleaved(vector: np.ndarray) -> np.ndarray:
    z = np.asarray(vector, dtype=complex)
    output = np.empty(2 * z.size, dtype=float)
    output[0::2] = z.real
    output[1::2] = z.imag
    return output


def _real_symmetric(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    residual = float(np.max(np.abs(value.imag)))
    if residual > 1.0e-9:
        raise AssertionError(f"expected real pair matrix, imag residual={residual}")
    result = value.real
    return 0.5 * (result + result.T)


@lru_cache(maxsize=1)
def background() -> dict[str, Any]:
    singlets = direct.singlet_basis()
    p_form = singlets["p"]
    a_form = singlets["a"]
    omega_form = singlets["omega"]
    p = projectors._form_to_vector(p_form).real
    a = projectors._form_to_vector(a_form).real
    omega = projectors._form_to_vector(omega_form).real
    delta_form = direct.delta_r()
    delta = fixed_gate.self_gate.delta_r_coordinates()
    return {
        "p_form": p_form,
        "a_form": a_form,
        "omega_form": omega_form,
        "p": p,
        "a": a,
        "omega": omega,
        "delta_form": delta_form,
        "delta": delta,
    }


def _project_channel(channel: str, pair: np.ndarray, powers=None) -> np.ndarray:
    target = projectors.COMMON_CHANNEL_EIGENVALUES[channel]
    if powers is None:
        powers = projectors.casimir_powers(pair)
    return projectors.project_from_powers(powers, target)


@lru_cache(maxsize=1)
def mixed_phi_and_cross_coefficients() -> dict[str, Any]:
    bg = background()
    p = bg["p"]
    delta = bg["delta"]
    delta_form = bg["delta_form"]
    tensor = mixed_gate.full_contraction_tensor()
    c_delta = np.einsum("aik,k->ai", tensor, delta, optimize=True)
    kernel = c_delta.conj().T @ c_delta
    symmetric_kernel = 0.5 * (kernel + kernel.T)
    powers = projectors.casimir_powers(symmetric_kernel)

    phi_matrices: dict[str, np.ndarray] = {}
    phi_gradients: dict[str, np.ndarray] = {}
    cross: dict[str, np.ndarray] = {
        channel: np.zeros((PHI_DIM, SIGMA_REAL_DIM), dtype=float)
        for channel in CHANNELS
    }
    normalization_residuals: dict[str, float] = {}
    for channel in CHANNELS:
        phi_matrix = _real_symmetric(_project_channel(channel, symmetric_kernel, powers))
        phi_matrices[channel] = phi_matrix
        phi_gradients[channel] = 2.0 * phi_matrix @ p
        target = mixed_gate.pure_invariant(
            channel,
            bg["p_form"],
            bg["p_form"],
            delta_form,
            delta_form,
        )
        normalization_residuals[channel] = abs(float(np.real(target)) - float(p @ phi_matrix @ p))

    for index in range(SIGMA_COMPLEX_DIM):
        base = tensor[:, :, index]
        for imaginary, column in ((False, 2 * index), (True, 2 * index + 1)):
            c_variation = 1j * base if imaginary else base
            delta_kernel = (
                c_variation.conj().T @ c_delta
                + c_delta.conj().T @ c_variation
            )
            symmetric_delta = 0.5 * (delta_kernel + delta_kernel.T)
            delta_powers = projectors.casimir_powers(symmetric_delta)
            for channel in CHANNELS:
                derivative = _project_channel(channel, symmetric_delta, delta_powers)
                cross[channel][:, column] = 2.0 * np.real(derivative @ p)

    return {
        "phi_matrices": phi_matrices,
        "phi_gradients": phi_gradients,
        "cross": cross,
        "normalization_residuals": normalization_residuals,
    }


@lru_cache(maxsize=1)
def cubic_coefficients() -> dict[str, Any]:
    bg = background()
    delta_form = bg["delta_form"]
    sigma_basis = fixed_gate.self_gate._basis()
    gradient = np.asarray(
        [
            float(np.real(cubic_gate.cubic_invariant(phi, delta_form, delta_form)))
            for phi in projectors.FOUR_BASIS
        ],
        dtype=float,
    )
    linear = np.empty((PHI_DIM, SIGMA_COMPLEX_DIM), dtype=complex)
    for phi_index, phi in enumerate(projectors.FOUR_BASIS):
        for sigma_index, sigma in enumerate(sigma_basis):
            linear[phi_index, sigma_index] = cubic_gate.cubic_invariant(
                phi, delta_form, sigma
            )
    cross = np.empty((PHI_DIM, SIGMA_REAL_DIM), dtype=float)
    cross[:, 0::2] = 2.0 * linear.real
    cross[:, 1::2] = -2.0 * linear.imag
    return {
        "phi_gradient": gradient,
        "cross": cross,
    }


@lru_cache(maxsize=1)
def gauge_bases() -> dict[str, Any]:
    bg = background()
    phi_generators = projectors.generator_matrices()
    sigma_generators = fixed_gate.self_gate._generators()
    columns = []
    for phi_generator, sigma_generator in zip(phi_generators, sigma_generators):
        columns.append(
            np.concatenate(
                (
                    np.asarray(phi_generator @ bg["p"]).reshape(-1),
                    _interleaved(sigma_generator @ bg["delta"]),
                )
            )
        )
    orbit = np.column_stack(columns)
    u, singular_values, _ = np.linalg.svd(orbit, full_matrices=True)
    rank = int(np.sum(singular_values > 1.0e-10 * singular_values[0]))
    return {
        "orbit": orbit,
        "gauge": u[:, :rank],
        "physical": u[:, rank:],
        "rank": rank,
        "minimum_nonzero_singular_value": float(singular_values[rank - 1]),
    }


@lru_cache(maxsize=1)
def coefficient_matrices() -> dict[str, Any]:
    bg = background()
    mixed = mixed_phi_and_cross_coefficients()
    cubic = cubic_coefficients()
    fixed_rows, self_data, mixed_data, cubic_data = fixed_gate._all_matrices()

    _, phi_gradient, phi_hessian = phi_gate.potential_gradient_hessian(
        bg["p"], v=1.0
    )
    sigma_self = sum(
        fixed_gate.BENCHMARK[f"self_{channel}"] * fixed_rows[f"self_{channel}"]
        for channel in fixed_gate.SELF_CHANNELS
    )
    base = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
    base[:PHI_DIM, :PHI_DIM] = phi_hessian
    base[PHI_DIM:, PHI_DIM:] = sigma_self

    matrices: dict[str, np.ndarray] = {"rho_phi": base.copy()}
    matrices["rho_phi"][PHI_DIM:, PHI_DIM:] = 0.0
    base[:PHI_DIM, :PHI_DIM] = 0.0

    gradient_columns: dict[str, np.ndarray] = {}
    for channel in CHANNELS:
        gradient = mixed["phi_gradients"][channel]
        radial = float(bg["p"] @ gradient)
        matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
        matrix[:PHI_DIM, :PHI_DIM] = (
            2.0 * mixed["phi_matrices"][channel]
            - radial * np.eye(PHI_DIM)
        )
        matrix[:PHI_DIM, PHI_DIM:] = mixed["cross"][channel]
        matrix[PHI_DIM:, :PHI_DIM] = mixed["cross"][channel].T
        matrix[PHI_DIM:, PHI_DIM:] = fixed_rows[f"mixed_{channel}"]
        matrices[f"lambda_{channel}"] = 0.5 * (matrix + matrix.T)
        gradient_columns[f"lambda_{channel}"] = gradient

    cubic_gradient = cubic["phi_gradient"]
    cubic_radial = float(bg["p"] @ cubic_gradient)
    cubic_matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
    cubic_matrix[:PHI_DIM, :PHI_DIM] = -cubic_radial * np.eye(PHI_DIM)
    cubic_matrix[:PHI_DIM, PHI_DIM:] = cubic["cross"]
    cubic_matrix[PHI_DIM:, :PHI_DIM] = cubic["cross"].T
    cubic_matrix[PHI_DIM:, PHI_DIM:] = fixed_rows["mu_eta"]
    matrices["mu_eta"] = 0.5 * (cubic_matrix + cubic_matrix.T)
    gradient_columns["mu_eta"] = cubic_gradient

    base[PHI_DIM:, PHI_DIM:] = sigma_self
    base = 0.5 * (base + base.T)

    stationarity = np.asarray(
        [
            [float(bg[direction] @ gradient_columns[name]) for name in VARIABLES[1:]]
            for direction in ("a", "omega")
        ],
        dtype=float,
    )
    return {
        "base": base,
        "matrices": matrices,
        "gradient_columns": gradient_columns,
        "stationarity": stationarity,
        "normalization_residuals": mixed["normalization_residuals"],
        "phi_self_gradient_residual": float(np.linalg.norm(phi_gradient)),
        "self_values": self_data["values"],
        "mixed_delta_values": mixed_data["delta_eigenvalues"],
        "cubic_delta_value": cubic_data["delta_eigenvalue"],
    }


def _feasible_start(stationarity: np.ndarray) -> np.ndarray:
    x = INITIAL.copy()
    variables = x[1:]
    gram = stationarity @ stationarity.T
    if np.linalg.matrix_rank(gram) == stationarity.shape[0]:
        variables -= stationarity.T @ np.linalg.solve(gram, stationarity @ variables)
    x[1:] = variables
    nonuniversal = float(np.sum(np.abs(x[2:7])))
    x[1] = max(x[1], 21.0 * (nonuniversal + 0.5))
    return x


def _bfb_margin(x: np.ndarray) -> float:
    return float(x[1] / 21.0 - np.sum(np.abs(x[2:7])))


@lru_cache(maxsize=1)
def scan() -> dict[str, Any]:
    coefficients = coefficient_matrices()
    bases = gauge_bases()
    physical = bases["physical"]
    base_physical = physical.T @ coefficients["base"] @ physical
    projected = {
        name: physical.T @ matrix @ physical
        for name, matrix in coefficients["matrices"].items()
    }
    stationarity = coefficients["stationarity"]
    start = _feasible_start(stationarity)

    def physical_matrix(x: np.ndarray) -> np.ndarray:
        result = base_physical.copy()
        for value, name in zip(x, VARIABLES):
            result += float(value) * projected[name]
        return 0.5 * (result + result.T)

    def objective(x: np.ndarray) -> float:
        minimum = float(np.linalg.eigvalsh(physical_matrix(x))[0])
        regularization = 1.0e-7 * float(np.sum((x - start) ** 2))
        return -minimum + regularization

    constraints = [
        {
            "type": "eq",
            "fun": lambda x, row=row: float(row @ x[1:]),
        }
        for row in stationarity
    ]
    constraints.extend(
        [
            {"type": "ineq", "fun": lambda x: _bfb_margin(x) - 0.05},
            {
                "type": "ineq",
                "fun": lambda x: float(
                    1.0
                    + sum(
                        x[index + 1]
                        * float(background()["p"] @ coefficients["gradient_columns"][name])
                        for index, name in enumerate(VARIABLES[1:])
                    )
                    / (4.0 * x[0])
                ),
            },
        ]
    )
    bounds = [(0.25, 100.0), (0.0, 500.0)] + [(-25.0, 25.0)] * 5 + [(-10.0, 10.0)]
    result = optimize.minimize(
        objective,
        start,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 180, "ftol": 1.0e-10, "disp": False},
    )
    x = np.asarray(result.x, dtype=float)

    full_hessian = coefficients["base"].copy()
    for value, name in zip(x, VARIABLES):
        full_hessian += float(value) * coefficients["matrices"][name]
    full_hessian = 0.5 * (full_hessian + full_hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(full_hessian)
    zero = eigenvectors[:, np.abs(eigenvalues) < 2.0e-7]
    gauge = bases["gauge"]
    alignment = float(
        np.max(np.abs((np.eye(TOTAL_DIM) - zero @ zero.T) @ gauge))
    ) if zero.shape[1] else float("inf")
    physical_eigenvalues = np.linalg.eigvalsh(physical.T @ full_hessian @ physical)

    gradient_total = sum(
        x[index + 1] * coefficients["gradient_columns"][name]
        for index, name in enumerate(VARIABLES[1:])
    )
    radial_phi = float(background()["p"] @ gradient_total)
    vphi_sq = 1.0 + radial_phi / (4.0 * x[0])
    transverse_gradient = gradient_total - radial_phi * background()["p"]

    self_value = sum(
        fixed_gate.BENCHMARK[f"self_{q}"] * coefficients["self_values"][q]
        for q in fixed_gate.SELF_CHANNELS
    )
    mixed_value = sum(
        x[index + 1] * coefficients["mixed_delta_values"][q]
        for index, q in enumerate(CHANNELS)
    )
    cubic_value = x[-1] * coefficients["cubic_delta_value"]
    m_sigma_sq = 2.0 * self_value + mixed_value + cubic_value

    rounded = np.round(eigenvalues, 7)
    unique, counts = np.unique(rounded, return_counts=True)
    return {
        "optimizer": {
            "success": bool(result.success),
            "message": str(result.message),
            "iterations": int(result.nit),
            "objective": float(result.fun),
        },
        "variables": {name: float(value) for name, value in zip(VARIABLES, x)},
        "stationarity_residuals": [float(value) for value in stationarity @ x[1:]],
        "full_transverse_phi_gradient_norm": float(np.linalg.norm(transverse_gradient)),
        "vPhi_squared": float(vphi_sq),
        "mSigma_squared": float(m_sigma_sq),
        "bfb_margin": _bfb_margin(x),
        "gauge_orbit_rank": bases["rank"],
        "gauge_alignment_residual": alignment,
        "negative_modes": int(np.sum(eigenvalues < -2.0e-7)),
        "zero_modes": int(np.sum(np.abs(eigenvalues) < 2.0e-7)),
        "minimum_full_eigenvalue": float(eigenvalues[0]),
        "minimum_physical_eigenvalue": float(physical_eigenvalues[0]),
        "maximum_physical_eigenvalue": float(physical_eigenvalues[-1]),
        "eigenvalue_clusters": {
            str(float(value)): int(count) for value, count in zip(unique, counts)
        },
        "normalization_residuals": coefficients["normalization_residuals"],
        "minimum_gauge_tangent_singular_value": bases["minimum_nonzero_singular_value"],
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    result = scan()
    checks = {
        "mixed_projector_normalization": max(result["normalization_residuals"].values()) < 1.0e-10,
        "optimizer_completed": result["optimizer"]["success"],
        "singlet_stationarity": max(abs(value) for value in result["stationarity_residuals"]) < 1.0e-7,
        "full_phi_transverse_stationarity": result["full_transverse_phi_gradient_norm"] < 1.0e-7,
        "positive_radial_mass_solution": result["vPhi_squared"] > 0.0,
        "strict_quartic_boundedness_margin": result["bfb_margin"] > 0.0,
        "full_gauge_orbit_rank_33": result["gauge_orbit_rank"] == 33,
        "no_tachyons": result["negative_modes"] == 0,
        "exactly_33_gauge_zero_modes": result["zero_modes"] == 33,
        "Goldstone_alignment": result["gauge_alignment_residual"] < 1.0e-6,
        "positive_coupled_physical_Hessian": result["minimum_physical_eigenvalue"] > 1.0e-6,
        "other_scalar_sectors_not_claimed": True,
        "unique_global_vacuum_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "COUPLED_P_DELTA_LOCAL_HESSIAN_PASS__OTHER_FIELDS_AND_GLOBALITY_OPEN"
            if not failures
            else "COUPLED_P_DELTA_BACKREACTION_SCAN_BLOCKED"
        ),
        "overall_state": "PARTIAL" if not failures else "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scan": result,
        "newly_tested": {
            "all_six_mixed_phi_blocks": True,
            "all_six_mixed_cross_blocks": True,
            "all_component_cubic_cross_block": True,
            "full_462_real_Hessian": True,
            "radial_mass_retuning": True,
        },
        "remaining_blockers": {
            "complete_10H_S_Phi17_potential": True,
            "phase_locking_and_EW_vacuum": True,
            "global_uniqueness_of_coupled_vacuum": True,
            "full_physical_threshold_spectrum": True,
            "component_two_loop_matching": True,
            "unique_proton_lifetime": True,
        },
        "flag": {
            "coupled_210_126bar_local_vacuum_complete": not failures,
            "complete_multifield_model": False,
            "global_vacuum_unique": False,
            "physical_threshold_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The scan constructs the full coupled 210+126bar Hessian and tests "
            "whether a bounded stationary P+Delta_R benchmark has exactly the "
            "33 SO(10)-to-SM Goldstones and a positive physical Hessian."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    scan_result = report["scan"]
    return "\n".join(
        [
            "# Coupled P + Delta_R backreaction scan — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- optimizer success: `{scan_result['optimizer']['success']}`",
            f"- negative modes: `{scan_result['negative_modes']}`",
            f"- zero modes: `{scan_result['zero_modes']}`",
            f"- physical minimum: `{scan_result['minimum_physical_eigenvalue']}`",
            f"- BFB margin: `{scan_result['bfb_margin']}`",
            "",
        ]
    )


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    raise TypeError(type(value).__name__)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
