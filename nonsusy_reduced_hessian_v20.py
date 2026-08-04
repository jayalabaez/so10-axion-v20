#!/usr/bin/env python3
"""Physical-EW arbitrary-precision reduced non-SUSY Hessian audit.

The complete 10_H amplitude is evaluated at the repository's physical target
h=174 GeV, not at M_I. Every cross quartic in the original radial witness is
restored. The operator provenance is the signed guaranteed floor of 34; the
mechanical 37 count is explicitly rejected.

The historical lambda4=-kappa*M_I/M_GUT benchmark is tachyonic. A lambda4=0
reduced survival point remains. This is a five-amplitude certificate, not the
full component Hessian.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

import mixed_rep_enlarged_floor_basis_v20 as signed_basis
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
FIELDS = ("P_210", "DeltaR_126bar", "H10_EW", "S_PQ", "Phi17_X")
SOURCE_FIELDS = (
    "P_210_PS",
    "DeltaR_126bar",
    "h_EW_effective",
    "S_PQ",
    "Phi17_X",
)


def _mp(value: float | str) -> mp.mpf:
    return mp.mpf(str(value))


def radial_quartic_matrix(
    radial: dict[str, Any],
) -> tuple[np.ndarray, dict[str, float], dict[str, float]]:
    definition = radial["potential_definition"]
    self_quartics = definition["self_quartics"]
    source_vevs = definition["target_vevs_GeV"]
    source_cross = definition["cross_quartics_epsilon"]
    lambdas = {
        target: float(self_quartics[source])
        for target, source in zip(FIELDS, SOURCE_FIELDS)
    }
    targets = {
        target: float(source_vevs[source])
        for target, source in zip(FIELDS, SOURCE_FIELDS)
    }
    matrix = np.diag([lambdas[name] for name in FIELDS]).astype(float)
    index = {name: i for i, name in enumerate(SOURCE_FIELDS)}
    for key, epsilon in source_cross.items():
        left, right = key.split("__")
        if left in index and right in index:
            i, j = index[left], index[right]
            matrix[i, j] = matrix[j, i] = 0.5 * float(epsilon)
    return matrix, lambdas, targets


def missing_norm_crosses(radial: dict[str, Any]) -> list[str]:
    present = set(radial["potential_definition"]["cross_quartics_epsilon"])
    all_keys = {
        f"{SOURCE_FIELDS[i]}__{SOURCE_FIELDS[j]}"
        for i in range(len(SOURCE_FIELDS))
        for j in range(i + 1, len(SOURCE_FIELDS))
    }
    return sorted(all_keys - present)


def interaction_parameters(
    m_i: float, m_gut: float, lam4: float, *, kappa: float = 0.05
) -> dict[str, float]:
    return {
        "kappa": float(kappa),
        "lam4": float(lam4),
        "lambda_phase": 1.0,
        "lambda_abs": 1.001,
        "m_i": float(m_i),
        "m_gut": float(m_gut),
        "c_lock": 1.0,
    }


def high_precision_hessian(
    targets: dict[str, float],
    quartic_matrix: np.ndarray,
    parameters: dict[str, float],
    *,
    dps: int = 100,
) -> mp.matrix:
    mp.mp.dps = dps
    v = [_mp(targets[name]) for name in FIELDS]
    p, delta, higgs, singlet, _phi = v
    kappa = _mp(parameters["kappa"])
    lam4 = _mp(parameters["lam4"])
    m_i = _mp(parameters["m_i"])
    m_gut = _mp(parameters["m_gut"])
    q = (
        _mp(parameters["c_lock"])
        * (_mp(parameters["lambda_abs"]) - abs(_mp(parameters["lambda_phase"])))
        / m_gut**2
    )

    gradient = [
        -lam4 * delta * higgs * singlet,
        -lam4 * p * higgs * singlet + 2 * q * delta * higgs**2 * singlet**2,
        -2 * kappa * m_i * higgs * singlet
        - lam4 * p * delta * singlet
        + 2 * q * higgs * delta**2 * singlet**2,
        -kappa * m_i * higgs**2
        - lam4 * p * delta * higgs
        + 2 * q * singlet * delta**2 * higgs**2,
        mp.mpf("0"),
    ]
    dm2 = [-gradient[i] / v[i] for i in range(5)]

    hessian = mp.matrix(5, 5)
    for i in range(5):
        for j in range(5):
            hessian[i, j] = 2 * v[i] * _mp(quartic_matrix[i, j]) * v[j]
        hessian[i, i] += dm2[i]

    hessian[1, 1] += 2 * q * higgs**2 * singlet**2
    hessian[2, 2] += -2 * kappa * m_i * singlet + 2 * q * delta**2 * singlet**2
    hessian[3, 3] += 2 * q * delta**2 * higgs**2
    off = {
        (0, 1): -lam4 * higgs * singlet,
        (0, 2): -lam4 * delta * singlet,
        (0, 3): -lam4 * delta * higgs,
        (1, 2): -lam4 * p * singlet + 4 * q * delta * higgs * singlet**2,
        (1, 3): -lam4 * p * higgs + 4 * q * delta * singlet * higgs**2,
        (2, 3): -2 * kappa * m_i * higgs
        - lam4 * p * delta
        + 4 * q * higgs * singlet * delta**2,
    }
    for (i, j), value in off.items():
        hessian[i, j] += value
        hessian[j, i] += value
    return hessian


def high_precision_eigenvalues(matrix: mp.matrix) -> list[float]:
    return [float(value) for value in mp.eigsy(matrix, eigvals_only=True)]


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    basis = signed_basis.build_report()
    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if not anchor.get("available") or basis.get("n_failed", 1) != 0:
        return {
            "status": "PHYSICAL_EW_REDUCED_HESSIAN_NOT_EXECUTED",
            "n_failed": 1,
            "failures": ["upstream"],
        }

    quartic_matrix, lambdas, targets = radial_quartic_matrix(radial)
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    h = float(targets["H10_EW"])
    historical_lam4 = -0.05 * m_i / m_gut

    survival_matrix = high_precision_hessian(
        targets, quartic_matrix, interaction_parameters(m_i, m_gut, 0.0)
    )
    historical_matrix = high_precision_hessian(
        targets,
        quartic_matrix,
        interaction_parameters(m_i, m_gut, historical_lam4),
    )
    survival_eigs = high_precision_eigenvalues(survival_matrix)
    historical_eigs = high_precision_eigenvalues(historical_matrix)
    float64_min = float(np.linalg.eigvalsh(np.array(survival_matrix.tolist(), dtype=float))[0])
    quartic_eigs = np.linalg.eigvalsh(quartic_matrix)

    portal_coefficient = m_gut * m_i**2 / h
    ew_curvature = 2.0 * lambdas["H10_EW"] * h**2
    lam4_bound = ew_curvature / portal_coefficient
    historical_over_bound = abs(historical_lam4) / lam4_bound
    float64_relative_error = abs(float64_min - survival_eigs[0]) / survival_eigs[0]
    missing = missing_norm_crosses(radial)

    checks = {
        "signed_floor34_loaded": bool(
            basis.get("flag", {}).get("canonical_signed_floor_34_emitted")
        )
        and basis.get("counts", {}).get("signed_guaranteed_floor_total") == 34,
        "mechanical_floor37_rejected": bool(
            basis.get("flag", {}).get("mechanical_floor37_rejected")
        ),
        "physical_h_is_174_GeV": abs(h - 174.0) < 1e-12,
        "historical_radial_quartic_matrix_positive": bool(min(quartic_eigs) > 0.0),
        "four_norm_crosses_missing_from_radial_witness": len(missing) == 4,
        "zero_lam4_survival_benchmark_positive": survival_eigs[0] > 0.0,
        "historical_lam4_benchmark_tachyonic": historical_eigs[0] < 0.0,
        "float64_light_mode_is_unreliable": float64_relative_error > 100.0,
        "full_component_scope_remains_open": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PHYSICAL_EW_REDUCED_HESSIAN_REPAIRED__HISTORICAL_LAM4_POINT_FAILS"
            if not failures
            else "PHYSICAL_EW_REDUCED_HESSIAN_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "fields": list(FIELDS),
        "target_vevs_GeV": targets,
        "enlarged_basis": {
            "signed_guaranteed_floor_total": basis["counts"][
                "signed_guaranteed_floor_total"
            ],
            "mechanical_augmented_total_rejected": basis["counts"][
                "mechanical_augmented_total_before_signed_corrections"
            ],
            "full_invariant_ring_complete": False,
        },
        "radial_coverage": {
            "norm_monomials_total": 15,
            "historical_witness_monomials": 11,
            "missing_cross_monomials": missing,
            "independent_tensor_channels_resolved_in_five_amplitudes": False,
        },
        "bfb_certificate": {
            "quartic_matrix_eigenvalues": [float(v) for v in quartic_eigs],
            "quartic_matrix_positive_definite": bool(min(quartic_eigs) > 0.0),
            "locking_sextic_coefficient_positive": True,
            "reduced_polynomial_bounded_from_below": bool(min(quartic_eigs) > 0.0),
        },
        "survival_benchmark": {
            "lam4": 0.0,
            "eigenvalues_GeV2": survival_eigs,
            "min_eigenvalue_GeV2": survival_eigs[0],
            "lightest_mass_GeV": math.sqrt(survival_eigs[0]),
            "positive_definite": survival_eigs[0] > 0.0,
        },
        "historical_benchmark": {
            "lam4": historical_lam4,
            "formula": "-kappa*M_I/M_GUT",
            "min_eigenvalue_GeV2": historical_eigs[0],
            "tachyonic": historical_eigs[0] < 0.0,
            "conditionally_excluded": historical_eigs[0] < 0.0,
        },
        "ew_portal_consistency": {
            "portal_curvature_coefficient_GeV2_per_lam4": portal_coefficient,
            "ew_target_curvature_GeV2": ew_curvature,
            "abs_lam4_O1_naturalness_bound": lam4_bound,
            "historical_abs_lam4_over_bound": historical_over_bound,
            "requires_cancellation_or_tiny_lam4": historical_over_bound > 1e10,
        },
        "numerics": {
            "high_precision_dps": 100,
            "float64_min_eigenvalue_GeV2": float64_min,
            "high_precision_min_eigenvalue_GeV2": survival_eigs[0],
            "float64_relative_error": float64_relative_error,
        },
        "flag": {
            "signed_floor34_used": True,
            "mechanical_floor37_rejected": True,
            "physical_electroweak_10_vev_used": True,
            "historical_equal_MI_10_vev_rejected": True,
            "cross_quartics_from_radial_witness_included": True,
            "arbitrary_precision_diagonalization_used": True,
            "independent_nonsusy_reduced_hessian": True,
            "reduced_potential_bounded_from_below": bool(min(quartic_eigs) > 0.0),
            "reduced_local_minimum_positive_definite": survival_eigs[0] > 0.0,
            "historical_selected_lam4_point_excluded": historical_eigs[0] < 0.0,
            "uses_aulakh_or_msgut_component_matrices": False,
            "full_component_nonsusy_hessian": False,
            "full_component_global_vacuum_proof": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Using the signed invariant floor34, physical h=174 GeV, and all "
            f"radial cross quartics, lambda4=0 has min m^2={survival_eigs[0]:.6e} "
            f"GeV^2 while the historical point has min m^2={historical_eigs[0]:.6e} "
            f"GeV^2 and is tachyonic. Its portal is {historical_over_bound:.3e} "
            "times the O(1) EW-curvature bound."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Physical-EW non-SUSY reduced Hessian — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Signed guaranteed invariant floor: {report['enlarged_basis']['signed_guaranteed_floor_total']}",
            f"- Survival lightest mass: {report['survival_benchmark']['lightest_mass_GeV']:.6f} GeV",
            f"- Historical min eigenvalue: {report['historical_benchmark']['min_eigenvalue_GeV2']:.6e} GeV^2",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_REDUCED_HESSIAN_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NONSUSY_REDUCED_HESSIAN_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
