#!/usr/bin/env python3
"""Full-transverse-stationarity optimizer for the coupled P+Delta_R Hessian.

The named a/omega stationarity coordinates do not by themselves certify the
complete Phi gradient.  This driver imposes the basis-independent condition
(I-P P^T) grad_Phi V=0 in all 210 components, reduces that system to its exact
independent row rank, and optimizes the source-derived 462-real Hessian.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

import coupled_p_delta_backreaction_scan_v20 as base

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "COUPLED_P_DELTA_FULL_STATIONARITY_SEARCH_V20.json"
OUT_MD = ROOT / "COUPLED_P_DELTA_FULL_STATIONARITY_SEARCH_V20.md"


def independent_rows(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=float)
    u, singular_values, _ = np.linalg.svd(value, full_matrices=False)
    if singular_values.size == 0 or singular_values[0] == 0.0:
        return np.zeros((0, value.shape[1]), dtype=float)
    rank = int(np.sum(singular_values > 1.0e-11 * singular_values[0]))
    return u[:, :rank].T @ value


def feasible_start(stationarity: np.ndarray) -> np.ndarray:
    x = base.INITIAL.copy()
    reduced = independent_rows(stationarity)
    variables = x[1:]
    if reduced.shape[0]:
        variables -= reduced.T @ np.linalg.solve(
            reduced @ reduced.T, reduced @ variables
        )
    x[1:] = variables
    nonuniversal = float(np.sum(np.abs(x[2:7])))
    x[1] = max(x[1], 21.0 * (nonuniversal + 0.5))
    return x


def bfb_margin(x: np.ndarray) -> float:
    return float(x[1] / 21.0 - np.sum(np.abs(x[2:7])))


@lru_cache(maxsize=1)
def run_search() -> dict[str, Any]:
    coefficients = base.coefficient_matrices()
    bases = base.gauge_bases()
    physical = bases["physical"]
    base_physical = physical.T @ coefficients["base"] @ physical
    projected = {
        name: physical.T @ matrix @ physical
        for name, matrix in coefficients["matrices"].items()
    }
    gradient_matrix = np.column_stack([
        coefficients["gradient_columns"][name]
        for name in base.VARIABLES[1:]
    ])
    p = base.background()["p"]
    projector_perp = np.eye(base.PHI_DIM) - np.outer(p, p)
    stationarity = projector_perp @ gradient_matrix
    reduced = independent_rows(stationarity)
    start = feasible_start(stationarity)

    def physical_matrix(x: np.ndarray) -> np.ndarray:
        result = base_physical.copy()
        for value, name in zip(x, base.VARIABLES):
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
            {"type": "ineq", "fun": lambda x: bfb_margin(x) - 0.05},
            {
                "type": "ineq",
                "fun": lambda x: float(
                    1.0
                    + sum(
                        x[index + 1]
                        * float(
                            base.background()["p"]
                            @ coefficients["gradient_columns"][name]
                        )
                        for index, name in enumerate(base.VARIABLES[1:])
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

    full_hessian = coefficients["base"].copy()
    for value, name in zip(x, base.VARIABLES):
        full_hessian += float(value) * coefficients["matrices"][name]
    full_hessian = 0.5 * (full_hessian + full_hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(full_hessian)
    zero = eigenvectors[:, np.abs(eigenvalues) < 2.0e-7]
    gauge = bases["gauge"]
    alignment = (
        float(
            np.max(
                np.abs(
                    (np.eye(base.TOTAL_DIM) - zero @ zero.T) @ gauge
                )
            )
        )
        if zero.shape[1]
        else float("inf")
    )
    physical_eigenvalues = np.linalg.eigvalsh(
        physical.T @ full_hessian @ physical
    )

    gradient_total = sum(
        x[index + 1] * coefficients["gradient_columns"][name]
        for index, name in enumerate(base.VARIABLES[1:])
    )
    radial = float(base.background()["p"] @ gradient_total)
    transverse = gradient_total - radial * base.background()["p"]
    vphi_sq = 1.0 + radial / (4.0 * x[0])

    self_value = sum(
        base.fixed_gate.BENCHMARK[f"self_{q}"]
        * coefficients["self_values"][q]
        for q in base.fixed_gate.SELF_CHANNELS
    )
    mixed_value = sum(
        x[index + 1] * coefficients["mixed_delta_values"][q]
        for index, q in enumerate(base.CHANNELS)
    )
    cubic_value = x[-1] * coefficients["cubic_delta_value"]

    return {
        "optimizer": {
            "success": bool(result.success),
            "message": str(result.message),
            "iterations": int(result.nit),
            "objective": float(result.fun),
        },
        "full_transverse_stationarity_rank": int(reduced.shape[0]),
        "legacy_named_stationarity_matrix": coefficients["stationarity"].tolist(),
        "reduced_full_stationarity_matrix": reduced.tolist(),
        "variables": {
            name: float(value) for name, value in zip(base.VARIABLES, x)
        },
        "stationarity_residuals": [
            float(value) for value in stationarity @ x[1:]
        ],
        "transverse_phi_gradient_norm": float(np.linalg.norm(transverse)),
        "vPhi_squared": float(vphi_sq),
        "mSigma_squared": float(
            2.0 * self_value + mixed_value + cubic_value
        ),
        "bfb_margin": bfb_margin(x),
        "gauge_orbit_rank": bases["rank"],
        "gauge_alignment_residual": alignment,
        "negative_modes": int(np.sum(eigenvalues < -2.0e-7)),
        "zero_modes": int(np.sum(np.abs(eigenvalues) < 2.0e-7)),
        "minimum_physical_eigenvalue": float(physical_eigenvalues[0]),
        "maximum_physical_eigenvalue": float(physical_eigenvalues[-1]),
        "normalization_residuals": coefficients["normalization_residuals"],
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    result = run_search()
    checks = {
        "full_transverse_stationarity_rank_resolved": result["full_transverse_stationarity_rank"] >= 1,
        "mixed_projector_normalization": max(
            result["normalization_residuals"].values()
        ) < 1.0e-10,
        "optimizer_completed": result["optimizer"]["success"],
        "stationarity": max(
            abs(value) for value in result["stationarity_residuals"]
        ) < 1.0e-7,
        "transverse_phi_stationarity": result[
            "transverse_phi_gradient_norm"
        ] < 1.0e-7,
        "positive_vPhi_squared": result["vPhi_squared"] > 0.0,
        "strict_bfb_margin": result["bfb_margin"] > 0.0,
        "gauge_rank_33": result["gauge_orbit_rank"] == 33,
        "no_tachyons": result["negative_modes"] == 0,
        "exactly_33_zeros": result["zero_modes"] == 33,
        "Goldstone_alignment": result["gauge_alignment_residual"] < 1.0e-6,
        "positive_physical_Hessian": result[
            "minimum_physical_eigenvalue"
        ] > 1.0e-6,
        "complete_other_fields_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "COUPLED_P_DELTA_FULL_STATIONARITY_HESSIAN_PASS__OTHER_FIELDS_OPEN"
            if not failures
            else "COUPLED_P_DELTA_FULL_STATIONARITY_SEARCH_BLOCKED"
        ),
        "overall_state": "PARTIAL" if not failures else "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "search": result,
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
            "The complete transverse Phi stationarity system is rank-reduced before optimizing "
            "the complete gauge-quotiented 462-real Hessian."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    result = report["search"]
    return "\n".join(
        [
            "# Coupled P + Delta_R full-stationarity search — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- transverse stationarity rank: `{result['full_transverse_stationarity_rank']}`",
            f"- optimizer success: `{result['optimizer']['success']}`",
            f"- negative modes: `{result['negative_modes']}`",
            f"- zero modes: `{result['zero_modes']}`",
            f"- physical minimum: `{result['minimum_physical_eigenvalue']}`",
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
