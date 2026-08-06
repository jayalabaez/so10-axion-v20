#!/usr/bin/env python3
"""Chirality-correct fixed-P Delta_R Hessian certificate.

The direct non-SUSY model defines 126bar_H as the -i Hodge eigenspace.  This
module therefore uses the physical -i all-component mixed projectors, the
complete four-channel 126bar self-potential, and the unique cubic
210_H 126bar_H^dag 126bar_H operator in one coordinate basis.

The benchmark is the Sigma-sector restriction of the independently hosted
coupled P+Delta_R solution.  At fixed Phi=P its complete 252-real angular
Hessian has exactly nine Pati-Salam-to-SM gauge zero modes and no tachyons.
This remains a fixed-P subcertificate; the authoritative coupled 462-real gate
is implemented separately in coupled_p_delta_physical_chirality_search_v20.py.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as self_gate
import exact_phisigma_126bar_minus_projectors_v20 as mixed_gate
import exact_210_126bar_cubic_clebsch_v20 as cubic_gate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_P_DELTA_SECOND_STAGE_HESSIAN_V20.json"
OUT_MD = ROOT / "EXACT_P_DELTA_SECOND_STAGE_HESSIAN_V20.md"
DIM = 126
REAL_DIM = 252
SELF_CHANNELS = ("54", "1050bar", "4125", "2772bar")
MIXED_CHANNELS = ("1", "45", "210", "770", "5940", "8910")

# Sigma-sector restriction of the hosted coupled-vacuum benchmark.
BENCHMARK = {
    "self_54": 17.0,
    "self_1050bar": 55.0 / 4.0,
    "self_4125": 10.0,
    "self_2772bar": 43.0 / 4.0,
    "mixed_1": 250.6354590044523,
    "mixed_45": -2.0416363310896783,
    "mixed_210": 1.598232935579569,
    "mixed_770": -0.5323872152031632,
    "mixed_5940": -7.012499723138351,
    "mixed_8910": 0.7001783786897183,
    "mu_eta": -0.6562032084684658,
}


def _interleaved(vector: np.ndarray) -> np.ndarray:
    value = np.asarray(vector, dtype=complex)
    output = np.empty(2 * len(value), dtype=float)
    output[0::2] = value.real
    output[1::2] = value.imag
    return output


def _hermitian_real(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    real = value.real
    imag = value.imag
    standard = np.block([[real, -imag], [imag, real]])
    order = [item for index in range(DIM) for item in (index, DIM + index)]
    return standard[np.ix_(order, order)]


@lru_cache(maxsize=1)
def self_hessian_coefficients() -> dict[str, object]:
    delta = self_gate.delta_r_coordinates()
    pair = np.outer(delta, delta)
    powers = self_gate._powers(pair)
    projected = {
        channel: self_gate.project(channel, pair, powers)
        for channel in SELF_CHANNELS
    }
    values = {
        channel: float(np.vdot(value, value).real)
        for channel, value in projected.items()
    }
    jacobian = {
        channel: np.empty((2 * DIM * DIM, REAL_DIM), dtype=float)
        for channel in SELF_CHANNELS
    }
    coefficients = {
        channel: np.asarray(
            [float(value) for value in self_gate._poly(channel)], dtype=float
        )
        for channel in SELF_CHANNELS
    }
    for column in range(REAL_DIM):
        index = column // 2
        variation = np.zeros(DIM, dtype=complex)
        variation[index] = 1.0 if column % 2 == 0 else 1.0j
        linear = np.outer(delta, variation) + np.outer(variation, delta)
        linear_powers = self_gate._powers(linear)
        for channel in SELF_CHANNELS:
            response = sum(
                (
                    coefficients[channel][degree] * linear_powers[degree]
                    for degree in range(4)
                ),
                np.zeros((DIM, DIM), dtype=complex),
            ).ravel()
            jacobian[channel][:, column] = np.concatenate(
                (response.real, response.imag)
            )
    identity = np.eye(REAL_DIM)
    matrices: dict[str, np.ndarray] = {}
    for channel in SELF_CHANNELS:
        raw = (
            jacobian[channel].T @ jacobian[channel]
            + self_gate._second_term(projected[channel])
            - 2.0 * values[channel] * identity
        )
        matrices[channel] = 0.5 * (raw + raw.T)
    return {"matrices": matrices, "values": values}


@lru_cache(maxsize=1)
def mixed_hessian_coefficients() -> dict[str, object]:
    delta = self_gate.delta_r_coordinates()
    matrices: dict[str, np.ndarray] = {}
    eigenvalues: dict[str, float] = {}
    residuals: dict[str, float] = {}
    for channel in MIXED_CHANNELS:
        operator = mixed_gate.evaluate_full_sigma_operator(
            channel, 1.0, 0.0, 0.0
        )
        eigenvalue = float(np.vdot(delta, operator @ delta).real)
        residual = float(
            np.linalg.norm(operator @ delta - eigenvalue * delta)
        )
        matrices[channel] = _hermitian_real(
            operator - eigenvalue * np.eye(DIM)
        )
        eigenvalues[channel] = eigenvalue
        residuals[channel] = residual
    return {
        "matrices": matrices,
        "delta_eigenvalues": eigenvalues,
        "delta_eigen_residuals": residuals,
    }


@lru_cache(maxsize=1)
def cubic_operator() -> np.ndarray:
    basis = self_gate._basis()
    phi = direct.singlet_basis()["p"]
    matrix = np.asarray(
        [
            [
                cubic_gate.cubic_invariant(phi, left, right)
                for right in basis
            ]
            for left in basis
        ],
        dtype=complex,
    )
    return 0.5 * (matrix + matrix.conj().T)


def cubic_audit() -> dict[str, object]:
    delta = self_gate.delta_r_coordinates()
    operator = cubic_operator()
    eigenvalue = float(np.vdot(delta, operator @ delta).real)
    eigen_residual = float(
        np.linalg.norm(operator @ delta - eigenvalue * delta)
    )
    spectrum = np.linalg.eigvalsh(operator)
    rounded = np.round(spectrum, 12)
    unique, counts = np.unique(rounded, return_counts=True)
    return {
        "operator": operator,
        "delta_eigenvalue": eigenvalue,
        "delta_eigen_residual": eigen_residual,
        "hermiticity_residual": float(
            np.max(np.abs(operator - operator.conj().T))
        ),
        "spectrum_clusters": {
            str(float(value)): int(count)
            for value, count in zip(unique, counts)
        },
        "angular_matrix": _hermitian_real(
            operator - eigenvalue * np.eye(DIM)
        ),
    }


def _all_matrices() -> tuple[
    dict[str, np.ndarray], dict[str, object], dict[str, object], dict[str, object]
]:
    self_data = self_hessian_coefficients()
    mixed_data = mixed_hessian_coefficients()
    cubic = cubic_audit()
    rows = {
        f"self_{channel}": self_data["matrices"][channel]
        for channel in SELF_CHANNELS
    }
    rows.update(
        {
            f"mixed_{channel}": mixed_data["matrices"][channel]
            for channel in MIXED_CHANNELS
        }
    )
    rows["mu_eta"] = cubic["angular_matrix"]
    return rows, self_data, mixed_data, cubic


def benchmark_audit() -> dict[str, object]:
    matrices, self_data, mixed_data, cubic = _all_matrices()
    maximum_commutator = max(
        float(
            np.max(
                np.abs(
                    matrices[left] @ matrices[right]
                    - matrices[right] @ matrices[left]
                )
            )
        )
        for left, right in itertools.combinations(matrices, 2)
    )
    hessian = sum(
        (BENCHMARK[name] * matrices[name] for name in matrices),
        np.zeros((REAL_DIM, REAL_DIM), dtype=float),
    )
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    zero = eigenvectors[:, np.abs(eigenvalues) < 1.0e-8]

    pairs = list(itertools.combinations(range(10), 2))
    ps_indices = [
        index
        for index, (left, right) in enumerate(pairs)
        if (left < 6 and right < 6) or (left >= 6 and right >= 6)
    ]
    delta = self_gate.delta_r_coordinates()
    generators = self_gate._generators()
    orbit = np.column_stack(
        [_interleaved(generators[index] @ delta) for index in ps_indices]
    )
    u, singular_values, _ = np.linalg.svd(orbit, full_matrices=False)
    rank = int(np.sum(singular_values > 1.0e-10 * singular_values[0]))
    orbit_basis = u[:, :rank]
    alignment = float(
        np.max(
            np.abs(
                (np.eye(REAL_DIM) - zero @ zero.T) @ orbit_basis
            )
        )
    )

    rounded = np.round(eigenvalues, 10)
    unique, counts = np.unique(rounded, return_counts=True)
    self_floor = min(
        BENCHMARK[f"self_{channel}"] for channel in SELF_CHANNELS
    )
    universal_cross = BENCHMARK["mixed_1"] / 21.0
    nonuniversal_bound = sum(
        abs(BENCHMARK[f"mixed_{channel}"])
        for channel in MIXED_CHANNELS
        if channel != "1"
    )
    self_value = sum(
        BENCHMARK[f"self_{channel}"] * self_data["values"][channel]
        for channel in SELF_CHANNELS
    )
    mixed_value = sum(
        BENCHMARK[f"mixed_{channel}"]
        * mixed_data["delta_eigenvalues"][channel]
        for channel in MIXED_CHANNELS
    )
    cubic_value = BENCHMARK["mu_eta"] * cubic["delta_eigenvalue"]
    mass_parameter = 2.0 * self_value + mixed_value + cubic_value
    positive = eigenvalues[eigenvalues > 1.0e-8]
    return {
        "couplings": BENCHMARK,
        "maximum_matrix_commutator": maximum_commutator,
        "eigenvalue_clusters": {
            str(float(value)): int(count)
            for value, count in zip(unique, counts)
        },
        "negative_modes": int(np.sum(eigenvalues < -1.0e-8)),
        "zero_modes": int(np.sum(np.abs(eigenvalues) < 1.0e-8)),
        "minimum_physical_eigenvalue": float(positive[0]),
        "maximum_physical_eigenvalue": float(eigenvalues[-1]),
        "PS_to_SM_orbit_rank": rank,
        "Goldstone_alignment_residual": alignment,
        "boundedness_certificate": {
            "minimum_self_projector_weight": self_floor,
            "self_quartic_lower_bound": f">={self_floor}*||Sigma||^4",
            "universal_mixed_norm_coefficient": universal_cross,
            "absolute_nonuniversal_mixed_bound": nonuniversal_bound,
            "strict_mixed_quartic_margin": (
                universal_cross - nonuniversal_bound
            ),
            "cubic_does_not_affect_large_field_boundedness": True,
        },
        "unit_background_stationarity": {
            "self_quartic_value": self_value,
            "mixed_quadratic_value": mixed_value,
            "cubic_quadratic_value": cubic_value,
            "required_mSigma2": mass_parameter,
        },
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, object]:
    mixed = mixed_hessian_coefficients()
    cubic = cubic_audit()
    audit = benchmark_audit()
    checks = {
        "complete_self_basis_upstream": self_gate.build_report()["n_failed"] == 0,
        "physical_minus_mixed_upstream": mixed_gate.build_report()["n_failed"] == 0,
        "cubic_operator_hermitian": cubic["hermiticity_residual"] < 1.0e-12,
        "cubic_delta_eigenvector": (
            cubic["delta_eigen_residual"] < 1.0e-12
            and abs(cubic["delta_eigenvalue"] - 2.0) < 1.0e-12
        ),
        "cubic_spectrum_exact": cubic["spectrum_clusters"]
        == {"-2.0": 30, "0.0": 66, "2.0": 30},
        "all_mixed_delta_eigenvectors": max(
            mixed["delta_eigen_residuals"].values()
        ) < 1.0e-11,
        "all_Hessian_coefficients_commute": audit[
            "maximum_matrix_commutator"
        ] < 1.0e-10,
        "quartic_boundedness_margin_positive": (
            audit["boundedness_certificate"]["strict_mixed_quartic_margin"]
            > 0.0
            and audit["boundedness_certificate"][
                "minimum_self_projector_weight"
            ]
            > 0.0
        ),
        "no_tachyons": audit["negative_modes"] == 0,
        "exact_nine_Goldstones": (
            audit["zero_modes"] == 9
            and audit["PS_to_SM_orbit_rank"] == 9
        ),
        "Goldstones_align_with_PS_orbit": audit[
            "Goldstone_alignment_residual"
        ] < 1.0e-10,
        "strictly_positive_physical_Sigma_Hessian": audit[
            "minimum_physical_eigenvalue"
        ]
        > 0.0,
        "authoritative_coupled_gate_is_separate": True,
        "physical_thresholds_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "FIXED_P_DELTA_R_PHYSICAL_CHIRALITY_HESSIAN_PASS"
            if not failures
            else "FIXED_P_DELTA_R_PHYSICAL_CHIRALITY_HESSIAN_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "cubic_all_component_audit": {
            key: value
            for key, value in cubic.items()
            if key not in {"operator", "angular_matrix"}
        },
        "mixed_delta_eigenvalues": mixed["delta_eigenvalues"],
        "mixed_delta_eigen_residuals": mixed["delta_eigen_residuals"],
        "benchmark": audit,
        "source_correction": {
            "physical_126bar_chirality": "-i",
            "legacy_plus_i_mixed_export_used": False,
            "benchmark_source": "hosted coupled physical-chirality solution",
        },
        "newly_closed_subproblem": {
            "fixed_P_tachyon_free_Delta_R_Hessian": not failures,
            "bounded_quartic_benchmark": not failures,
            "nine_PS_to_SM_Goldstones": not failures,
        },
        "remaining_blockers": {
            "complete_10H_S_Phi17_potential": True,
            "phase_locking_and_electroweak_vacuum": True,
            "global_uniqueness": True,
            "physical_threshold_spectrum": True,
            "component_two_loop_matching": True,
            "unique_proton_lifetime": True,
        },
        "flag": {
            "fixed_P_second_stage_stabilized": not failures,
            "complete_multifield_model": False,
            "physical_threshold_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "In the physical -i 126bar basis, the hosted coupled benchmark "
            "restricts to a bounded fixed-P Sigma Hessian with exactly nine "
            "Pati-Salam-to-SM Goldstones and no tachyons."
        ),
    }


def write_markdown(report: dict[str, object]) -> str:
    benchmark = report["benchmark"]
    return "\n".join(
        [
            "# Fixed-P Delta_R physical-chirality Hessian — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- zero modes: `{benchmark['zero_modes']}`",
            f"- negative modes: `{benchmark['negative_modes']}`",
            f"- minimum physical eigenvalue: `{benchmark['minimum_physical_eigenvalue']}`",
            f"- Goldstone alignment residual: `{benchmark['Goldstone_alignment_residual']}`",
            "",
        ]
    )


def _default(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
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
