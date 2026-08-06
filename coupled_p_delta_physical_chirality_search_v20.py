#!/usr/bin/env python3
"""Full coupled P+Delta_R search in one physical 126bar coordinate basis.

All 126bar objects in this module use the canonical -i Hodge basis: Delta_R,
SO(10) generators, self-projectors, six mixed projectors, the cubic operator,
and every mixed cross derivative.  The complete real 462x462 Hessian is built
with canonical second-derivative normalization, full transverse Phi
stationarity, radial mass retuning, a strict sufficient quartic boundedness
margin, and a direct Noether identity test on all 33 gauge tangents.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_126bar_cubic_clebsch_v20 as cubic_gate
import exact_210_pati_salam_global_vacuum_v20 as phi_gate
import exact_p_delta_second_stage_hessian_v20 as fixed_gate
import exact_phisigma_126bar_minus_projectors_v20 as minus_gate
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "COUPLED_P_DELTA_PHYSICAL_CHIRALITY_SEARCH_V20.json"
OUT_MD = ROOT / "COUPLED_P_DELTA_PHYSICAL_CHIRALITY_SEARCH_V20.md"
PHI_DIM = 210
SIGMA_DIM = 126
SIGMA_REAL_DIM = 252
TOTAL_DIM = 462
CHANNELS = ("1", "45", "210", "770", "5940", "8910")
VARIABLES = ("rho_phi",) + tuple(f"lambda_{q}" for q in CHANNELS) + ("mu_eta",)
INITIAL = np.asarray([8.0, 31.5, 0.0, 0.0, 1.25, 0.0, 0.0, -0.375], dtype=float)


def _interleaved(vector: np.ndarray) -> np.ndarray:
    z = np.asarray(vector, dtype=complex)
    result = np.empty(2 * z.size, dtype=float)
    result[0::2] = z.real
    result[1::2] = z.imag
    return result


def _hermitian_real(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    real = value.real
    imag = value.imag
    standard = np.block([[real, -imag], [imag, real]])
    order = [item for index in range(SIGMA_DIM) for item in (index, SIGMA_DIM + index)]
    return standard[np.ix_(order, order)]


def _real_symmetric(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if np.max(np.abs(value.imag), initial=0.0) > 1.0e-9:
        raise AssertionError("real 210 pair acquired an imaginary component")
    result = value.real
    return 0.5 * (result + result.T)


def _independent_rows(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=float)
    u, singular_values, _ = np.linalg.svd(value, full_matrices=False)
    if singular_values.size == 0 or singular_values[0] == 0.0:
        return np.zeros((0, value.shape[1]), dtype=float)
    rank = int(np.sum(singular_values > 1.0e-11 * singular_values[0]))
    return u[:, :rank].T @ value


@lru_cache(maxsize=1)
def background() -> dict[str, Any]:
    p_form = direct.singlet_basis()["p"]
    delta_form = direct.delta_r()
    return {
        "p_form": p_form,
        "p": projectors._form_to_vector(p_form).real,
        "delta_form": delta_form,
        "delta": minus_gate.sigma_coordinates(delta_form),
    }


@lru_cache(maxsize=1)
def mixed_coefficients() -> dict[str, Any]:
    bg = background()
    p = bg["p"]
    delta = bg["delta"]
    tensor = minus_gate.full_contraction_tensor()
    c_delta = np.einsum("aik,k->ai", tensor, delta, optimize=True)
    kernel = c_delta.conj().T @ c_delta
    symmetric_kernel = 0.5 * (kernel + kernel.T)
    powers = projectors.casimir_powers(symmetric_kernel)

    phi_matrices: dict[str, np.ndarray] = {}
    phi_gradients: dict[str, np.ndarray] = {}
    sigma_operators: dict[str, np.ndarray] = {}
    sigma_eigenvalues: dict[str, float] = {}
    sigma_eigen_residuals: dict[str, float] = {}
    cross = {
        channel: np.zeros((PHI_DIM, SIGMA_REAL_DIM), dtype=float)
        for channel in CHANNELS
    }
    normalization_residuals: dict[str, float] = {}

    for channel in CHANNELS:
        eigenvalue = projectors.COMMON_CHANNEL_EIGENVALUES[channel]
        phi_matrix = _real_symmetric(
            projectors.project_from_powers(powers, eigenvalue)
        )
        sigma_operator = minus_gate.evaluate_full_sigma_operator(
            channel, 1.0, 0.0, 0.0
        )
        sigma_eigenvalue = float(np.vdot(delta, sigma_operator @ delta).real)
        phi_value = float(p @ phi_matrix @ p)
        phi_matrices[channel] = phi_matrix
        phi_gradients[channel] = 2.0 * phi_matrix @ p
        sigma_operators[channel] = sigma_operator
        sigma_eigenvalues[channel] = sigma_eigenvalue
        sigma_eigen_residuals[channel] = float(
            np.linalg.norm(sigma_operator @ delta - sigma_eigenvalue * delta)
        )
        normalization_residuals[channel] = abs(phi_value - sigma_eigenvalue)

    for sigma_index in range(SIGMA_DIM):
        basis_map = tensor[:, :, sigma_index]
        for imaginary, column in ((False, 2 * sigma_index), (True, 2 * sigma_index + 1)):
            c_variation = 1j * basis_map if imaginary else basis_map
            derivative_kernel = (
                c_variation.conj().T @ c_delta
                + c_delta.conj().T @ c_variation
            )
            symmetric_derivative = 0.5 * (
                derivative_kernel + derivative_kernel.T
            )
            derivative_powers = projectors.casimir_powers(symmetric_derivative)
            for channel in CHANNELS:
                derivative = projectors.project_from_powers(
                    derivative_powers,
                    projectors.COMMON_CHANNEL_EIGENVALUES[channel],
                )
                cross[channel][:, column] = 2.0 * np.real(derivative @ p)

    return {
        "phi_matrices": phi_matrices,
        "phi_gradients": phi_gradients,
        "sigma_operators": sigma_operators,
        "sigma_eigenvalues": sigma_eigenvalues,
        "sigma_eigen_residuals": sigma_eigen_residuals,
        "cross": cross,
        "normalization_residuals": normalization_residuals,
    }


@lru_cache(maxsize=1)
def cubic_coefficients() -> dict[str, Any]:
    bg = background()
    basis = minus_gate.sigma_basis()
    delta_form = bg["delta_form"]
    gradient = np.asarray(
        [
            float(np.real(cubic_gate.cubic_invariant(phi, delta_form, delta_form)))
            for phi in projectors.FOUR_BASIS
        ],
        dtype=float,
    )
    operator = np.asarray(
        [
            [
                cubic_gate.cubic_invariant(bg["p_form"], left, right)
                for right in basis
            ]
            for left in basis
        ],
        dtype=complex,
    )
    operator = 0.5 * (operator + operator.conj().T)
    delta = bg["delta"]
    eigenvalue = float(np.vdot(delta, operator @ delta).real)
    eigen_residual = float(np.linalg.norm(operator @ delta - eigenvalue * delta))

    linear = np.empty((PHI_DIM, SIGMA_DIM), dtype=complex)
    for phi_index, phi in enumerate(projectors.FOUR_BASIS):
        for sigma_index, sigma in enumerate(basis):
            linear[phi_index, sigma_index] = cubic_gate.cubic_invariant(
                phi, delta_form, sigma
            )
    cross = np.empty((PHI_DIM, SIGMA_REAL_DIM), dtype=float)
    cross[:, 0::2] = 2.0 * linear.real
    cross[:, 1::2] = -2.0 * linear.imag
    return {
        "phi_gradient": gradient,
        "sigma_operator": operator,
        "sigma_eigenvalue": eigenvalue,
        "sigma_eigen_residual": eigen_residual,
        "cross": cross,
    }


@lru_cache(maxsize=1)
def gauge_bases() -> dict[str, Any]:
    bg = background()
    columns = []
    for phi_generator, sigma_generator in zip(
        projectors.generator_matrices(), fixed_gate.self_gate._generators()
    ):
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
    mixed = mixed_coefficients()
    cubic = cubic_coefficients()
    fixed_rows, self_data, _, _ = fixed_gate._all_matrices()
    _, phi_gradient, phi_hessian = phi_gate.potential_gradient_hessian(
        bg["p"], v=1.0
    )

    sigma_self_angular = sum(
        fixed_gate.BENCHMARK[f"self_{channel}"] * fixed_rows[f"self_{channel}"]
        for channel in fixed_gate.SELF_CHANNELS
    )
    base_matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
    base_matrix[PHI_DIM:, PHI_DIM:] = 2.0 * sigma_self_angular

    rho_matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
    rho_matrix[:PHI_DIM, :PHI_DIM] = phi_hessian
    matrices: dict[str, np.ndarray] = {"rho_phi": rho_matrix}
    gradient_columns: dict[str, np.ndarray] = {}

    for channel in CHANNELS:
        gradient = mixed["phi_gradients"][channel]
        radial = float(bg["p"] @ gradient)
        sigma_angular = _hermitian_real(
            mixed["sigma_operators"][channel]
            - mixed["sigma_eigenvalues"][channel] * np.eye(SIGMA_DIM)
        )
        matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
        matrix[:PHI_DIM, :PHI_DIM] = (
            2.0 * mixed["phi_matrices"][channel]
            - radial * np.eye(PHI_DIM)
        )
        matrix[PHI_DIM:, PHI_DIM:] = 2.0 * sigma_angular
        matrix[:PHI_DIM, PHI_DIM:] = mixed["cross"][channel]
        matrix[PHI_DIM:, :PHI_DIM] = mixed["cross"][channel].T
        matrices[f"lambda_{channel}"] = 0.5 * (matrix + matrix.T)
        gradient_columns[f"lambda_{channel}"] = gradient

    cubic_gradient = cubic["phi_gradient"]
    cubic_radial = float(bg["p"] @ cubic_gradient)
    cubic_angular = _hermitian_real(
        cubic["sigma_operator"]
        - cubic["sigma_eigenvalue"] * np.eye(SIGMA_DIM)
    )
    cubic_matrix = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=float)
    cubic_matrix[:PHI_DIM, :PHI_DIM] = -cubic_radial * np.eye(PHI_DIM)
    cubic_matrix[PHI_DIM:, PHI_DIM:] = 2.0 * cubic_angular
    cubic_matrix[:PHI_DIM, PHI_DIM:] = cubic["cross"]
    cubic_matrix[PHI_DIM:, :PHI_DIM] = cubic["cross"].T
    matrices["mu_eta"] = 0.5 * (cubic_matrix + cubic_matrix.T)
    gradient_columns["mu_eta"] = cubic_gradient

    return {
        "base": base_matrix,
        "matrices": matrices,
        "gradient_columns": gradient_columns,
        "phi_self_gradient_residual": float(np.linalg.norm(phi_gradient)),
        "self_values": self_data["values"],
        "mixed_delta_values": mixed["sigma_eigenvalues"],
        "cubic_delta_value": cubic["sigma_eigenvalue"],
        "mixed_normalization_residuals": mixed["normalization_residuals"],
        "mixed_delta_eigen_residuals": mixed["sigma_eigen_residuals"],
        "cubic_delta_eigen_residual": cubic["sigma_eigen_residual"],
    }


def _bfb_margin(x: np.ndarray) -> float:
    return float(x[1] / 21.0 - np.sum(np.abs(x[2:7])))


def _feasible_start(stationarity: np.ndarray) -> np.ndarray:
    x = INITIAL.copy()
    reduced = _independent_rows(stationarity)
    variables = x[1:]
    if reduced.shape[0]:
        variables -= reduced.T @ np.linalg.solve(
            reduced @ reduced.T, reduced @ variables
        )
    x[1:] = variables
    nonuniversal = float(np.sum(np.abs(x[2:7])))
    x[1] = max(x[1], 21.0 * (nonuniversal + 0.5))
    return x


@lru_cache(maxsize=1)
def run_search() -> dict[str, Any]:
    coefficients = coefficient_matrices()
    bases = gauge_bases()
    physical = bases["physical"]
    base_physical = physical.T @ coefficients["base"] @ physical
    projected = {
        name: physical.T @ matrix @ physical
        for name, matrix in coefficients["matrices"].items()
    }

    gradient_matrix = np.column_stack(
        [coefficients["gradient_columns"][name] for name in VARIABLES[1:]]
    )
    p = background()["p"]
    stationarity = (np.eye(PHI_DIM) - np.outer(p, p)) @ gradient_matrix
    reduced = _independent_rows(stationarity)
    start = _feasible_start(stationarity)

    def physical_matrix(x: np.ndarray) -> np.ndarray:
        result = base_physical.copy()
        for value, name in zip(x, VARIABLES):
            result += float(value) * projected[name]
        return 0.5 * (result + result.T)

    def objective(x: np.ndarray) -> float:
        minimum = float(np.linalg.eigvalsh(physical_matrix(x))[0])
        return -minimum + 1.0e-8 * float(np.sum((x - start) ** 2))

    constraints = [
        {"type": "eq", "fun": lambda x, row=row: float(row @ x[1:])}
        for row in reduced
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
                        * float(
                            p @ coefficients["gradient_columns"][name]
                        )
                        for index, name in enumerate(VARIABLES[1:])
                    )
                    / (4.0 * x[0])
                ),
            },
        ]
    )
    bounds = (
        [(0.25, 250.0), (0.0, 1000.0)]
        + [(-50.0, 50.0)] * 5
        + [(-20.0, 20.0)]
    )
    result = optimize.minimize(
        objective,
        start,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 300, "ftol": 1.0e-11, "disp": False},
    )
    x = np.asarray(result.x, dtype=float)

    hessian = coefficients["base"].copy()
    for value, name in zip(x, VARIABLES):
        hessian += float(value) * coefficients["matrices"][name]
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    physical_eigenvalues = np.linalg.eigvalsh(
        physical.T @ hessian @ physical
    )
    zero = eigenvectors[:, np.abs(eigenvalues) < 2.0e-7]
    gauge = bases["gauge"]
    alignment = (
        float(
            np.max(
                np.abs((np.eye(TOTAL_DIM) - zero @ zero.T) @ gauge)
            )
        )
        if zero.shape[1]
        else float("inf")
    )
    noether = float(np.max(np.abs(hessian @ bases["orbit"])))

    gradient_total = sum(
        x[index + 1] * coefficients["gradient_columns"][name]
        for index, name in enumerate(VARIABLES[1:])
    )
    radial = float(p @ gradient_total)
    transverse = gradient_total - radial * p
    vphi_squared = 1.0 + radial / (4.0 * x[0])

    self_value = sum(
        fixed_gate.BENCHMARK[f"self_{channel}"]
        * coefficients["self_values"][channel]
        for channel in fixed_gate.SELF_CHANNELS
    )
    mixed_value = sum(
        x[index + 1] * coefficients["mixed_delta_values"][channel]
        for index, channel in enumerate(CHANNELS)
    )
    cubic_value = x[-1] * coefficients["cubic_delta_value"]

    return {
        "optimizer": {
            "success": bool(result.success),
            "message": str(result.message),
            "iterations": int(result.nit),
            "objective": float(result.fun),
        },
        "stationarity_rank": int(reduced.shape[0]),
        "variables": {name: float(value) for name, value in zip(VARIABLES, x)},
        "stationarity_residuals": [
            float(value) for value in stationarity @ x[1:]
        ],
        "transverse_phi_gradient_norm": float(np.linalg.norm(transverse)),
        "vPhi_squared": float(vphi_squared),
        "mSigma_squared": float(2.0 * self_value + mixed_value + cubic_value),
        "bfb_margin": _bfb_margin(x),
        "gauge_orbit_rank": bases["rank"],
        "Noether_H_times_orbit_residual": noether,
        "gauge_alignment_residual": alignment,
        "negative_modes": int(np.sum(eigenvalues < -2.0e-7)),
        "zero_modes": int(np.sum(np.abs(eigenvalues) < 2.0e-7)),
        "minimum_physical_eigenvalue": float(physical_eigenvalues[0]),
        "maximum_physical_eigenvalue": float(physical_eigenvalues[-1]),
        "mixed_normalization_residuals": coefficients[
            "mixed_normalization_residuals"
        ],
        "mixed_delta_eigen_residuals": coefficients[
            "mixed_delta_eigen_residuals"
        ],
        "cubic_delta_eigen_residual": coefficients[
            "cubic_delta_eigen_residual"
        ],
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    upstream = minus_gate.build_report()
    result = run_search()
    checks = {
        "physical_minus_projectors_green": upstream["n_failed"] == 0,
        "mixed_normalization": max(
            result["mixed_normalization_residuals"].values()
        ) < 1.0e-10,
        "all_delta_eigenvectors": max(
            result["mixed_delta_eigen_residuals"].values()
        ) < 1.0e-10
        and result["cubic_delta_eigen_residual"] < 1.0e-10,
        "optimizer_completed": result["optimizer"]["success"],
        "full_transverse_stationarity": result[
            "transverse_phi_gradient_norm"
        ] < 1.0e-7,
        "positive_vPhi_squared": result["vPhi_squared"] > 0.0,
        "strict_bfb_margin": result["bfb_margin"] > 0.0,
        "gauge_orbit_rank_33": result["gauge_orbit_rank"] == 33,
        "Noether_identity": result["Noether_H_times_orbit_residual"] < 1.0e-7,
        "no_tachyons": result["negative_modes"] == 0,
        "exactly_33_zeros": result["zero_modes"] == 33,
        "Goldstone_alignment": result["gauge_alignment_residual"] < 1.0e-6,
        "positive_physical_Hessian": result[
            "minimum_physical_eigenvalue"
        ] > 1.0e-6,
        "other_scalar_sectors_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "COUPLED_P_DELTA_PHYSICAL_CHIRALITY_HESSIAN_PASS__OTHER_FIELDS_OPEN"
            if not failures
            else "COUPLED_P_DELTA_PHYSICAL_CHIRALITY_SEARCH_BLOCKED"
        ),
        "overall_state": "PARTIAL" if not failures else "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "search": result,
        "source_correction": {
            "all_126bar_blocks_use_minus_i_basis": True,
            "legacy_plus_i_mixed_matrices_used": False,
            "canonical_SigmaSigma_factor": 2.0,
            "cross_derivatives_rebuilt_in_minus_i_basis": True,
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
        "remaining_blockers": {
            "complete_10H_S_Phi17_potential": True,
            "phase_locking_and_electroweak_vacuum": True,
            "global_uniqueness": True,
            "physical_threshold_spectrum": True,
            "component_two_loop_matching": True,
            "unique_proton_lifetime": True,
        },
        "verdict": (
            "The complete 210+126bar local Hessian is reconstructed in one "
            "physical -i coordinate basis and accepted only if stationarity, "
            "Noether, Goldstone, boundedness, and physical positivity gates all pass."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    result = report["search"]
    return "\n".join(
        [
            "# Coupled P + Delta_R physical-chirality search — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- optimizer success: `{result['optimizer']['success']}`",
            f"- Noether residual: `{result['Noether_H_times_orbit_residual']}`",
            f"- negative modes: `{result['negative_modes']}`",
            f"- zero modes: `{result['zero_modes']}`",
            f"- minimum physical eigenvalue: `{result['minimum_physical_eigenvalue']}`",
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
