#!/usr/bin/env python3
"""Physical-EW reduced non-SUSY Hessian and portal-consistency audit.

This supersedes the earlier reduced certificate that assigned the complete
10_H amplitude the intermediate-scale VEV M_I.  The repository's original
vacuum witness instead has the electroweak target h=174 GeV.  At the enormous
M_GUT/M_EW hierarchy, ordinary float64 eigensolvers also lose the light mode,
so this module constructs and diagonalizes the Hessian with arbitrary
precision.

The audit consumes the canonical guaranteed 37-invariant floor, restores every
cross quartic already present in the radial witness, and distinguishes a stable
lambda4=0 survival benchmark from the historical
lambda4=-kappa*M_I/M_GUT point.  The latter is tachyonic at the physical EW
vacuum.  This excludes that benchmark, not the whole model, because unresolved
independent tensor channels may provide additional cancellations.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

import mixed_rep_enlarged_floor_basis_v20 as enlarged
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
    """Recover the complete five-field q^T B q witness in physical field order."""
    definition = radial["potential_definition"]
    self_quartics = definition["self_quartics"]
    source_vevs = definition["target_vevs_GeV"]
    source_cross = definition["cross_quartics_epsilon"]

    lambdas = {
        target_name: float(self_quartics[source_name])
        for target_name, source_name in zip(FIELDS, SOURCE_FIELDS)
    }
    targets = {
        target_name: float(source_vevs[source_name])
        for target_name, source_name in zip(FIELDS, SOURCE_FIELDS)
    }
    matrix = np.diag([lambdas[name] for name in FIELDS]).astype(float)
    source_index = {name: index for index, name in enumerate(SOURCE_FIELDS)}
    for key, epsilon in source_cross.items():
        left, right = key.split("__")
        if left not in source_index or right not in source_index:
            continue
        i, j = source_index[left], source_index[right]
        matrix[i, j] = matrix[j, i] = 0.5 * float(epsilon)
    return matrix, lambdas, targets


def missing_norm_crosses(radial: dict[str, Any]) -> list[str]:
    """List norm-product monomials absent from the historical radial witness."""
    present = set(radial["potential_definition"]["cross_quartics_epsilon"])
    source = list(SOURCE_FIELDS)
    all_keys = {
        f"{source[i]}__{source[j]}"
        for i in range(len(source))
        for j in range(i + 1, len(source))
    }
    return sorted(all_keys - present)


def interaction_parameters(
    m_i: float,
    m_gut: float,
    lam4: float,
    *,
    kappa: float = 0.05,
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


def _q_mp(parameters: dict[str, float]) -> mp.mpf:
    return (
        _mp(parameters["c_lock"])
        * (
            _mp(parameters["lambda_abs"])
            - abs(_mp(parameters["lambda_phase"]))
        )
        / _mp(parameters["m_gut"]) ** 2
    )


def high_precision_hessian(
    targets: dict[str, float],
    quartic_matrix: np.ndarray,
    parameters: dict[str, float],
    *,
    dps: int = 100,
) -> mp.matrix:
    """Construct the physical Hessian without float64 cancellation.

    The radial witness is V_q=(1/4) q^T B q with q_i=r_i^2-v_i^2.
    The interaction gradients are cancelled by independent quadratic shifts,
    exactly as in the earlier reduced construction.  Every operation that can
    mix M_GUT^2 and M_EW^2 is evaluated with ``mpmath`` precision.
    """
    mp.mp.dps = dps
    values = [_mp(targets[name]) for name in FIELDS]
    p, delta, higgs, singlet, _phi17 = values
    kappa = _mp(parameters["kappa"])
    lam4 = _mp(parameters["lam4"])
    m_i = _mp(parameters["m_i"])
    q_lock = _q_mp(parameters)

    interaction_gradient = [
        -lam4 * delta * higgs * singlet,
        -lam4 * p * higgs * singlet
        + 2 * q_lock * delta * higgs**2 * singlet**2,
        -2 * kappa * m_i * higgs * singlet
        - lam4 * p * delta * singlet
        + 2 * q_lock * higgs * delta**2 * singlet**2,
        -kappa * m_i * higgs**2
        - lam4 * p * delta * higgs
        + 2 * q_lock * singlet * delta**2 * higgs**2,
        mp.mpf("0"),
    ]
    delta_m2 = [
        -interaction_gradient[index] / values[index] for index in range(5)
    ]

    hessian = mp.matrix(5, 5)
    for i in range(5):
        for j in range(5):
            hessian[i, j] = (
                2
                * values[i]
                * _mp(quartic_matrix[i, j])
                * values[j]
            )
        hessian[i, i] += delta_m2[i]

    hessian[2, 2] += (
        -2 * kappa * m_i * singlet
        + 2 * q_lock * delta**2 * singlet**2
    )
    hessian[1, 1] += 2 * q_lock * higgs**2 * singlet**2
    hessian[3, 3] += 2 * q_lock * delta**2 * higgs**2

    off_diagonal = {
        (0, 1): -lam4 * higgs * singlet,
        (0, 2): -lam4 * delta * singlet,
        (0, 3): -lam4 * delta * higgs,
        (1, 2): -lam4 * p * singlet
        + 4 * q_lock * delta * higgs * singlet**2,
        (1, 3): -lam4 * p * higgs
        + 4 * q_lock * delta * singlet * higgs**2,
        (2, 3): -2 * kappa * m_i * higgs
        - lam4 * p * delta
        + 4 * q_lock * higgs * singlet * delta**2,
    }
    for (i, j), value in off_diagonal.items():
        hessian[i, j] += value
        hessian[j, i] += value
    return hessian


def high_precision_eigenvalues(matrix: mp.matrix) -> list[float]:
    return [float(value) for value in mp.eigsy(matrix, eigvals_only=True)]


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    floor = enlarged.build_report()
    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if not anchor.get("available") or floor.get("n_failed", 1) != 0:
        return {
            "status": "PHYSICAL_EW_REDUCED_HESSIAN_NOT_EXECUTED",
            "n_failed": 1,
            "failures": ["upstream"],
        }

    quartic_matrix, lambdas, targets = radial_quartic_matrix(radial)
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    physical_h = float(targets["H10_EW"])

    survival_lam4 = 0.0
    historical_lam4 = -0.05 * m_i / m_gut
    survival_matrix = high_precision_hessian(
        targets,
        quartic_matrix,
        interaction_parameters(m_i, m_gut, survival_lam4),
    )
    historical_matrix = high_precision_hessian(
        targets,
        quartic_matrix,
        interaction_parameters(m_i, m_gut, historical_lam4),
    )
    survival_eigenvalues = high_precision_eigenvalues(survival_matrix)
    historical_eigenvalues = high_precision_eigenvalues(historical_matrix)

    # This intentionally demonstrates why float64 cannot certify the light mode.
    float64_matrix = np.array(survival_matrix.tolist(), dtype=float)
    float64_eigenvalues = np.linalg.eigvalsh(float64_matrix)
    quartic_eigenvalues = np.linalg.eigvalsh(quartic_matrix)
    missing_crosses = missing_norm_crosses(radial)

    # Four absent off-diagonal epsilon entries contribute at most
    # ||Delta B||_2 <= ||Delta B||_F <= sqrt(2)*epsilon_max.  Weyl's inequality
    # therefore gives this sufficient hypercube for positive definiteness.
    missing_cross_epsilon_bound = float(
        np.min(quartic_eigenvalues) / math.sqrt(2.0)
    )

    portal_curvature_coefficient = m_gut * m_i * m_i / physical_h
    ew_target_curvature = 2.0 * lambdas["H10_EW"] * physical_h**2
    naturalness_bound = ew_target_curvature / portal_curvature_coefficient
    historical_over_bound = (
        abs(historical_lam4)
        * portal_curvature_coefficient
        / ew_target_curvature
    )
    float64_relative_error = abs(
        float(float64_eigenvalues[0]) - survival_eigenvalues[0]
    ) / survival_eigenvalues[0]

    checks = {
        "canonical_floor_37_loaded": bool(
            floor.get("flag", {}).get("canonical_floor_37_emitted")
        ),
        "physical_h_is_174_GeV": abs(physical_h - 174.0) < 1e-12,
        "historical_radial_quartic_matrix_positive": bool(
            np.min(quartic_eigenvalues) > 0.0
        ),
        "four_norm_crosses_missing_from_radial_witness": len(missing_crosses) == 4,
        "zero_lam4_survival_benchmark_positive": survival_eigenvalues[0] > 0.0,
        "historical_lam4_benchmark_tachyonic": historical_eigenvalues[0] < 0.0,
        "float64_light_mode_is_unreliable": float64_relative_error > 100.0,
        "full_component_scope_remains_open": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    report = {
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
            "guaranteed_floor_total": floor.get("counts", {}).get(
                "guaranteed_floor_total"
            ),
            "full_invariant_ring_complete": False,
        },
        "radial_coverage": {
            "norm_monomials_total": 15,
            "historical_witness_monomials": 11,
            "missing_cross_monomials": missing_crosses,
            "missing_cross_epsilon_hypercube_sufficient_PD_bound": (
                missing_cross_epsilon_bound
            ),
            "independent_tensor_channels_resolved_in_five_amplitudes": False,
            "interpretation": (
                "The five-amplitude reduction can absorb only one linear "
                "combination per radial monomial; it cannot distinguish all "
                "independent off-direction tensor contractions."
            ),
        },
        "bfb_certificate": {
            "quartic_matrix_eigenvalues": [
                float(value) for value in quartic_eigenvalues
            ],
            "quartic_matrix_positive_definite": bool(
                np.min(quartic_eigenvalues) > 0.0
            ),
            "locking_sextic_coefficient_positive": True,
            "reduced_polynomial_bounded_from_below": bool(
                np.min(quartic_eigenvalues) > 0.0
            ),
        },
        "survival_benchmark": {
            "lam4": survival_lam4,
            "eigenvalues_GeV2": survival_eigenvalues,
            "min_eigenvalue_GeV2": survival_eigenvalues[0],
            "lightest_mass_GeV": math.sqrt(survival_eigenvalues[0]),
            "positive_definite": survival_eigenvalues[0] > 0.0,
        },
        "historical_benchmark": {
            "lam4": historical_lam4,
            "formula": "-kappa*M_I/M_GUT",
            "min_eigenvalue_GeV2": historical_eigenvalues[0],
            "tachyonic": historical_eigenvalues[0] < 0.0,
            "conditionally_excluded": historical_eigenvalues[0] < 0.0,
        },
        "ew_portal_consistency": {
            "portal_curvature_coefficient_GeV2_per_lam4": (
                portal_curvature_coefficient
            ),
            "ew_target_curvature_GeV2": ew_target_curvature,
            "abs_lam4_O1_naturalness_bound": naturalness_bound,
            "historical_abs_lam4_over_bound": historical_over_bound,
            "requires_cancellation_or_tiny_lam4": historical_over_bound > 1e10,
        },
        "numerics": {
            "high_precision_dps": 100,
            "float64_min_eigenvalue_GeV2": float(float64_eigenvalues[0]),
            "high_precision_min_eigenvalue_GeV2": survival_eigenvalues[0],
            "float64_relative_error": float64_relative_error,
        },
        "flag": {
            "physical_electroweak_10_vev_used": True,
            "historical_equal_MI_10_vev_rejected": True,
            "cross_quartics_from_radial_witness_included": True,
            "arbitrary_precision_diagonalization_used": True,
            "independent_nonsusy_reduced_hessian": True,
            "reduced_potential_bounded_from_below": bool(
                np.min(quartic_eigenvalues) > 0.0
            ),
            "reduced_local_minimum_positive_definite": (
                survival_eigenvalues[0] > 0.0
            ),
            "historical_selected_lam4_point_excluded": (
                historical_eigenvalues[0] < 0.0
            ),
            "uses_aulakh_or_msgut_component_matrices": False,
            "full_component_nonsusy_hessian": False,
            "full_component_global_vacuum_proof": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Using the physical h=174 GeV target and every cross quartic in the "
            f"radial witness, lambda4=0 has min m^2={survival_eigenvalues[0]:.6e} "
            f"GeV^2, while the historical lambda4=-kappa*M_I/M_GUT point has "
            f"min m^2={historical_eigenvalues[0]:.6e} GeV^2 and is tachyonic. "
            f"That portal exceeds the O(1) EW-curvature bound by "
            f"{historical_over_bound:.3e}. The selected benchmark fails; the "
            "whole model remains open because unresolved tensor channels can "
            "supply additional cancellations."
        ),
    }
    return report


def write_markdown(report: dict[str, Any]) -> str:
    survival = report["survival_benchmark"]
    historical = report["historical_benchmark"]
    portal = report["ew_portal_consistency"]
    return "\n".join(
        [
            "# Physical-EW non-SUSY reduced Hessian — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Physical h target: {report['target_vevs_GeV']['H10_EW']} GeV",
            f"- Survival min eigenvalue: {survival['min_eigenvalue_GeV2']:.6e} GeV^2",
            f"- Survival lightest mass: {survival['lightest_mass_GeV']:.6f} GeV",
            f"- Historical min eigenvalue: {historical['min_eigenvalue_GeV2']:.6e} GeV^2",
            f"- Historical |lambda4| / EW bound: {portal['historical_abs_lam4_over_bound']:.6e}",
            "",
            "The historical benchmark is excluded conditionally. The complete tensor potential remains open.",
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
