#!/usr/bin/env python3
"""Exact mu_D stability envelope for the 482-real GUT Hessian.

The registered cubic

    mu_D H^dag C(Phi,Sigmabar) + h.c.

has zero H tadpole on the verified p + Delta_R background but produces exact
H--Phi and H--Sigmabar mixed Hessian blocks.  This module appends the twenty
real components of the complex 10_H to the verified 462-real 210+126bar
Hessian at H=0.

The H-only block is deliberately parameterized as an effective isotropic
quadratic coefficient m_H,eff^2 I_20.  On the 429-dimensional physical
210+126bar quotient the enlarged Hessian is

    [ A          mu_D B ]
    [ mu_D B^T   m_H^2 I].

Since A is positive definite, the Schur complement gives the exact necessary
and sufficient condition

    m_H,eff^2 > |mu_D|^2 lambda_max(B^T A^{-1} B).

All quantities use the repository's normalized v_Phi=1 conventions.  This is
an exact conditional stability envelope, not the complete operator-derived
10_H mass matrix or electroweak vacuum.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import coupled_p_delta_physical_chirality_search_v20 as coupled
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phi_hdag_sigmabar_cubic_audit_v20 as cubic_audit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_MUD_482_SCHUR_STABILITY_V20.json"
OUT_MD = ROOT / "EXACT_MUD_482_SCHUR_STABILITY_V20.md"
OLD_DIM = coupled.TOTAL_DIM
H_COMPLEX_DIM = 10
H_REAL_DIM = 20
TOTAL_DIM = OLD_DIM + H_REAL_DIM


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    return value


def _interleaved(vector: np.ndarray) -> np.ndarray:
    z = np.asarray(vector, dtype=complex).reshape(-1)
    result = np.empty(2 * z.size, dtype=float)
    result[0::2] = z.real
    result[1::2] = z.imag
    return result


def complex_map_real_interleaved(matrix: np.ndarray) -> np.ndarray:
    """Real matrix R with x^T R y = Re(z^dag M w)."""
    value = np.asarray(matrix, dtype=complex)
    n_rows, n_cols = value.shape
    standard = np.block(
        [[value.real, -value.imag], [value.imag, value.real]]
    )
    row_order = [item for index in range(n_rows) for item in (index, n_rows + index)]
    col_order = [item for index in range(n_cols) for item in (index, n_cols + index)]
    return standard[np.ix_(row_order, col_order)]


def realification_audit() -> dict[str, Any]:
    rng = np.random.default_rng(1701)
    matrix = rng.normal(size=(4, 5)) + 1j * rng.normal(size=(4, 5))
    left = rng.normal(size=4) + 1j * rng.normal(size=4)
    right = rng.normal(size=5) + 1j * rng.normal(size=5)
    real_map = complex_map_real_interleaved(matrix)
    target = float(2.0 * np.real(np.vdot(left, matrix @ right)))
    reconstructed = float(
        _interleaved(left) @ (2.0 * real_map) @ _interleaved(right)
    )
    return {
        "target_2Re": target,
        "reconstructed": reconstructed,
        "absolute_residual": abs(target - reconstructed),
    }


@lru_cache(maxsize=1)
def old_hessian_data() -> dict[str, Any]:
    coefficients = coupled.coefficient_matrices()
    search = coupled.run_search()
    hessian = coefficients["base"].copy()
    for name in coupled.VARIABLES:
        hessian += float(search["variables"][name]) * coefficients["matrices"][name]
    hessian = 0.5 * (hessian + hessian.T)
    bases = coupled.gauge_bases()
    physical = bases["physical"]
    physical_hessian = 0.5 * (
        physical.T @ hessian @ physical
        + (physical.T @ hessian @ physical).T
    )
    eigenvalues = np.linalg.eigvalsh(physical_hessian)
    return {
        "hessian": hessian,
        "physical": physical,
        "physical_hessian": physical_hessian,
        "physical_eigenvalues": eigenvalues,
        "orbit": bases["orbit"],
        "gauge": bases["gauge"],
        "gauge_rank": bases["rank"],
        "search": search,
    }


@lru_cache(maxsize=1)
def mixed_block_per_unit_mu() -> dict[str, Any]:
    background = coupled.background()
    p_form = background["p_form"]
    delta_form = background["delta_form"]
    sigma_basis = coupled.minus_gate.sigma_basis()

    # C(p,delta_sigma): complex 10 x 126 map.
    h_sigma_complex = direct.contraction_matrix(p_form, sigma_basis)
    h_sigma_real = 2.0 * complex_map_real_interleaved(h_sigma_complex)

    # C(delta_phi,Delta_R): complex 10 x 210 map with real Phi coordinates.
    h_phi_complex = np.column_stack(
        [
            cubic_audit.contract_vector(phi_state, delta_form)
            for phi_state in cubic_audit.four_form_basis()
        ]
    )
    h_phi_real = np.empty((H_REAL_DIM, coupled.PHI_DIM), dtype=float)
    h_phi_real[0::2, :] = 2.0 * h_phi_complex.real
    h_phi_real[1::2, :] = 2.0 * h_phi_complex.imag

    # Old field order is Phi(210), then interleaved Sigmabar(252).
    old_to_h = np.zeros((OLD_DIM, H_REAL_DIM), dtype=float)
    old_to_h[: coupled.PHI_DIM, :] = h_phi_real.T
    old_to_h[coupled.PHI_DIM :, :] = h_sigma_real.T

    old = old_hessian_data()
    gauge_residual = float(np.max(np.abs(old_to_h.T @ old["orbit"])))
    physical_block = old["physical"].T @ old_to_h
    singular_values = np.linalg.svd(physical_block, compute_uv=False)
    return {
        "old_to_h": old_to_h,
        "physical_block": physical_block,
        "H_Sigmabar_complex_rank": int(
            np.linalg.matrix_rank(h_sigma_complex, tol=1.0e-12)
        ),
        "H_Phi_real_rank": int(np.linalg.matrix_rank(h_phi_real, tol=1.0e-12)),
        "combined_physical_rank": int(
            np.linalg.matrix_rank(physical_block, tol=1.0e-12)
        ),
        "combined_physical_singular_values": singular_values,
        "gauge_tangent_annihilation_residual": gauge_residual,
        "frobenius_norm": float(np.linalg.norm(physical_block)),
    }


@lru_cache(maxsize=1)
def schur_data() -> dict[str, Any]:
    old = old_hessian_data()
    block = mixed_block_per_unit_mu()["physical_block"]
    a = old["physical_hessian"]
    solved = np.linalg.solve(a, block)
    schur = 0.5 * (block.T @ solved + (block.T @ solved).T)
    eigenvalues = np.linalg.eigvalsh(schur)
    return {
        "operator": schur,
        "eigenvalues": eigenvalues,
        "lambda_max": float(eigenvalues[-1]),
        "lambda_min": float(eigenvalues[0]),
        "rank": int(np.linalg.matrix_rank(schur, tol=1.0e-11)),
        "symmetry_residual": float(np.max(np.abs(schur - schur.T))),
    }


def physical_matrix(mu_d: float, m_h_squared: float) -> np.ndarray:
    old = old_hessian_data()
    block = mixed_block_per_unit_mu()["physical_block"]
    return np.block(
        [
            [old["physical_hessian"], float(mu_d) * block],
            [float(mu_d) * block.T, float(m_h_squared) * np.eye(H_REAL_DIM)],
        ]
    )


def full_matrix(mu_d: float, m_h_squared: float) -> np.ndarray:
    old = old_hessian_data()
    block = mixed_block_per_unit_mu()["old_to_h"]
    return np.block(
        [
            [old["hessian"], float(mu_d) * block],
            [float(mu_d) * block.T, float(m_h_squared) * np.eye(H_REAL_DIM)],
        ]
    )


def benchmark(mu_d: float, multiplier: float) -> dict[str, Any]:
    critical = float(mu_d) ** 2 * schur_data()["lambda_max"]
    mass_squared = float(multiplier) * critical
    physical = 0.5 * (
        physical_matrix(mu_d, mass_squared)
        + physical_matrix(mu_d, mass_squared).T
    )
    full = 0.5 * (
        full_matrix(mu_d, mass_squared) + full_matrix(mu_d, mass_squared).T
    )
    physical_eigenvalues = np.linalg.eigvalsh(physical)
    full_eigenvalues = np.linalg.eigvalsh(full)
    tolerance = 2.0e-7
    return {
        "mu_D_over_vPhi": float(mu_d),
        "mass_multiplier_of_critical": float(multiplier),
        "critical_mH_squared": critical,
        "mH_effective_squared": mass_squared,
        "physical_minimum_eigenvalue": float(physical_eigenvalues[0]),
        "physical_zero_modes": int(
            np.sum(np.abs(physical_eigenvalues) < tolerance)
        ),
        "physical_negative_modes": int(
            np.sum(physical_eigenvalues < -tolerance)
        ),
        "full_zero_modes": int(np.sum(np.abs(full_eigenvalues) < tolerance)),
        "full_negative_modes": int(np.sum(full_eigenvalues < -tolerance)),
        "full_minimum_eigenvalue": float(full_eigenvalues[0]),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    registration = cubic_audit.build_report()
    realification = realification_audit()
    old = old_hessian_data()
    mixed = mixed_block_per_unit_mu()
    schur = schur_data()
    above = benchmark(1.0, 1.25)
    equality = benchmark(1.0, 1.0)
    below = benchmark(1.0, 0.75)

    checks = {
        "cubic_registered": registration["flag"].get(
            "operator_catalogue_corrected", False
        ),
        "realification_exact": realification["absolute_residual"] < 1.0e-12,
        "old_physical_Hessian_positive": old["physical_eigenvalues"][0]
        > 1.0e-6,
        "old_gauge_rank_33": old["gauge_rank"] == 33,
        "mixed_block_nonzero": mixed["combined_physical_rank"] > 0,
        "mixed_block_annihilates_gauge_orbit": mixed[
            "gauge_tangent_annihilation_residual"
        ]
        < 1.0e-9,
        "schur_symmetric": schur["symmetry_residual"] < 1.0e-10,
        "schur_positive_semidefinite": schur["lambda_min"] > -1.0e-9,
        "schur_nonzero": schur["lambda_max"] > 1.0e-9,
        "above_bound_physical_positive": above["physical_negative_modes"] == 0
        and above["physical_minimum_eigenvalue"] > 1.0e-7,
        "above_bound_preserves_33_full_zeros": above["full_zero_modes"] == 33
        and above["full_negative_modes"] == 0,
        "equality_has_extra_physical_zero": equality["physical_zero_modes"] >= 1,
        "equality_preserves_gauge_zeros": equality["full_zero_modes"] >= 34,
        "below_bound_has_tachyon": below["physical_negative_modes"] >= 1
        and below["full_negative_modes"] >= 1,
        "complete_H_mass_matrix_not_claimed": True,
        "electroweak_vacuum_not_claimed": True,
        "whole_model_validation_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report = {
        "status": (
            "MUD_482_REAL_SCHUR_STABILITY_BOUND_CLOSED__FULL_H_BLOCK_OPEN"
            if not failures
            else "MUD_482_REAL_SCHUR_STABILITY_GATE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "dimensions": {
            "old_real_Hessian": OLD_DIM,
            "old_physical_quotient": int(old["physical_hessian"].shape[0]),
            "H10_real": H_REAL_DIM,
            "enlarged_real_Hessian": TOTAL_DIM,
            "enlarged_physical_quotient": int(
                old["physical_hessian"].shape[0] + H_REAL_DIM
            ),
        },
        "normalization": {
            "vPhi": 1.0,
            "mu_variable": "mu_D/vPhi",
            "mH_squared_variable": "m_H,eff^2/vPhi^2",
            "cubic_real_potential": "2 mu_D Re(H^dag C(Phi,Sigmabar))",
        },
        "realification": realification,
        "old_vacuum": {
            "minimum_physical_eigenvalue": float(old["physical_eigenvalues"][0]),
            "gauge_rank": old["gauge_rank"],
            "source_search": old["search"],
        },
        "mixed_block": {key: value for key, value in mixed.items() if key != "old_to_h" and key != "physical_block"},
        "schur_operator": {
            "eigenvalues": schur["eigenvalues"],
            "rank": schur["rank"],
            "lambda_max": schur["lambda_max"],
            "lambda_min": schur["lambda_min"],
            "stability_theorem": (
                "m_H,eff^2 > |mu_D|^2 lambda_max(B^T A_phys^{-1} B)"
            ),
        },
        "benchmarks": {
            "above_bound": above,
            "at_bound": equality,
            "below_bound": below,
        },
        "flag": {
            "muD_cross_block_inserted": not failures,
            "exact_effective_H_mass_stability_bound": not failures,
            "gauge_goldstones_preserved_above_bound": not failures,
            "tachyon_below_bound_exhibited": not failures,
            "complete_operator_derived_H_mass_matrix": False,
            "nonzero_electroweak_backreaction": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The registered mu_D cubic is compatible with the p+Delta_R vacuum "
            "only when the effective H-only mass block satisfies the exact Schur "
            "bound. This closes a conditional 482-real local-stability envelope; "
            "the complete operator-derived H block and electroweak vacuum remain open."
        ),
    }
    return _jsonable(report)


def write_markdown(report: dict[str, Any]) -> str:
    schur = report["schur_operator"]
    return "\n".join(
        [
            "# mu_D 482-real Schur stability gate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact conditional bound",
            "",
            "`m_H,eff^2 > |mu_D|^2 lambda_max(B^T A_phys^{-1} B)`",
            "",
            f"- `lambda_max = {schur['lambda_max']}`",
            f"- Schur rank: `{schur['rank']}`",
            "",
            "The complete operator-derived H mass matrix remains open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
