#!/usr/bin/env python3
"""Reduced electroweak backreaction and hierarchy-tuning gate for v20.

This module extends the repository's five-field radial witness

    r = (P_210, Delta_R, S, Phi17, h_EW)

by turning on every reduced radial h^2 r_i^2 portal.  It reconstructs the
unshifted quadratic mass parameters required to keep the declared hierarchy
stationary, proves boundedness and radial Hessian positivity by congruence, and
quantifies the electroweak hierarchy cancellation induced by generic portals.

The result is deliberately fail-closed.  It closes a reduced G3/G5 subproblem;
it does not project the complete SO(10) invariant ring, vary all 210/126bar
components, or prove the full physical vacuum.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_REDUCED_EW_BACKREACTION_V20.json"
OUT_MD = ROOT / "EXACT_REDUCED_EW_BACKREACTION_V20.md"

NAMES = ("P_210_PS", "DeltaR_126bar", "S_PQ", "Phi17", "h_EW")
H_INDEX = 4
LAMBDAS = np.asarray([0.55, 0.65, 0.45, 0.75, 0.258], dtype=float)
BASE_CROSS = {
    (0, 1): 0.05,
    (0, 2): 0.01,
    (0, 3): 0.02,
    (1, 2): 0.04,
    (1, 3): 0.01,
    (2, 3): 0.03,
}
GENERIC_H_PORTALS = {
    "P_210_PS": 0.008,
    "DeltaR_126bar": 0.012,
    "S_PQ": 0.015,
    "Phi17": 0.006,
}


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


def target_vevs() -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import scalar_vacuum_proton_decay_v20 as scalar

        anchor = scalar._unification_anchor()
    except Exception as exc:
        raise RuntimeError(f"unification anchor import failed: {type(exc).__name__}: {exc}") from exc
    if not anchor.get("available"):
        raise RuntimeError(f"unification anchor unavailable: {anchor.get('error')}")
    vevs = np.asarray(
        [
            anchor["M_GUT_GeV"],
            anchor["M_I_GeV"],
            anchor["M_I_GeV"],
            1.0e17,
            174.0,
        ],
        dtype=float,
    )
    return vevs, anchor


def epsilon_matrix(h_portals: dict[str, float]) -> np.ndarray:
    eps = np.zeros((len(NAMES), len(NAMES)), dtype=float)
    for (i, j), value in BASE_CROSS.items():
        eps[i, j] = eps[j, i] = float(value)
    for i, name in enumerate(NAMES[:-1]):
        value = float(h_portals[name])
        eps[i, H_INDEX] = eps[H_INDEX, i] = value
    return eps


def quartic_matrix(eps: np.ndarray) -> np.ndarray:
    return np.diag(LAMBDAS) + 0.5 * np.asarray(eps, dtype=float)


def reconstructed_mass_squared(vevs: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Mass parameters in V=-1/2 m_i^2 r_i^2 + quartics + constant."""
    v2 = np.asarray(vevs, dtype=float) ** 2
    return LAMBDAS * v2 + 0.5 * np.asarray(eps, dtype=float) @ v2


def stationarity_residual(vevs: np.ndarray, eps: np.ndarray, mass2: np.ndarray) -> dict[str, Any]:
    v = np.asarray(vevs, dtype=float)
    portal = 0.5 * v * (np.asarray(eps, dtype=float) @ (v**2))
    self_term = LAMBDAS * v**3
    mass_term = mass2 * v
    gradient = -mass_term + self_term + portal
    scale = np.abs(mass_term) + np.abs(self_term) + np.abs(portal) + 1.0
    relative = np.abs(gradient) / scale
    return {
        "gradient_GeV3": gradient,
        "relative_residuals": relative,
        "maximum_relative_residual": float(np.max(relative)),
        "mass_reconstruction_residual_GeV2": mass2
        - (LAMBDAS * v**2 + 0.5 * np.asarray(eps, dtype=float) @ (v**2)),
    }


def naturalness_bounds(vevs: np.ndarray, *, tuning_budget: float = 10.0) -> dict[str, float]:
    h_self = LAMBDAS[H_INDEX] * float(vevs[H_INDEX] ** 2)
    return {
        name: float(2.0 * tuning_budget * h_self / vevs[i] ** 2)
        for i, name in enumerate(NAMES[:-1])
    }


def scenario(name: str, vevs: np.ndarray, h_portals: dict[str, float]) -> dict[str, Any]:
    eps = epsilon_matrix(h_portals)
    b = quartic_matrix(eps)
    b_eigs = np.linalg.eigvalsh(b)
    mass2 = reconstructed_mass_squared(vevs, eps)
    residual = stationarity_residual(vevs, eps, mass2)

    # H_radial = 2 D_v B D_v.  Since D_v is invertible, Sylvester's law of
    # inertia makes H positive definite exactly when B is positive definite.
    d = np.diag(vevs)
    hessian = 2.0 * d @ b @ d
    b_positive = bool(np.min(b_eigs) > 0.0)
    hessian_positive_by_congruence = b_positive and bool(np.all(vevs != 0.0))

    h_self = LAMBDAS[H_INDEX] * float(vevs[H_INDEX] ** 2)
    h_portal_terms = {
        NAMES[i]: float(0.5 * eps[H_INDEX, i] * vevs[i] ** 2)
        for i in range(H_INDEX)
    }
    aggregate = float(sum(abs(value) for value in h_portal_terms.values()) / h_self)
    largest = float(max(abs(value) for value in h_portal_terms.values()) / h_self)
    h_mass_ratio = float(abs(mass2[H_INDEX]) / h_self)

    gut_ew_shifts = {
        NAMES[i]: {
            "delta_m2_from_h_GeV2": float(0.5 * eps[i, H_INDEX] * vevs[H_INDEX] ** 2),
            "relative_to_self_mass_parameter": float(
                abs(0.5 * eps[i, H_INDEX] * vevs[H_INDEX] ** 2)
                / (LAMBDAS[i] * vevs[i] ** 2)
            ),
        }
        for i in range(H_INDEX)
    }

    return {
        "name": name,
        "h_portals": dict(h_portals),
        "epsilon_matrix": eps,
        "normalized_quartic_matrix": b,
        "normalized_quartic_eigenvalues": b_eigs,
        "quartic_positive_definite": b_positive,
        "radial_hessian_GeV2": hessian,
        "radial_hessian_positive_by_congruence": hessian_positive_by_congruence,
        "congruence_identity_residual": float(
            np.max(np.abs(hessian - 2.0 * d @ b @ d))
        ),
        "quadratic_mass_parameters_GeV2": {
            field: float(value) for field, value in zip(NAMES, mass2)
        },
        "stationarity": residual,
        "global_radial_minimum": b_positive,
        "global_argument": (
            "With q_i=r_i^2-v_i^2, V=(1/4) q^T B q.  Positive-definite B "
            "implies V>=0 globally in the reduced radial space."
        ),
        "electroweak_hierarchy": {
            "h_self_target_GeV2": h_self,
            "portal_contributions_to_h_mass_GeV2": h_portal_terms,
            "aggregate_abs_portal_over_h_self": aggregate,
            "largest_abs_portal_over_h_self": largest,
            "reconstructed_h_mass_parameter_over_h_self": h_mass_ratio,
        },
        "GUT_mass_backreaction_from_h": gut_ew_shifts,
    }


def build_report() -> dict[str, Any]:
    try:
        vevs, anchor = target_vevs()
    except Exception as exc:
        return {
            "status": "REDUCED_EW_BACKREACTION_NOT_EXECUTED__ANCHOR_MISSING",
            "n_checks": 1,
            "n_failed": 1,
            "failures": [f"anchor: {type(exc).__name__}: {exc}"],
            "flag": {
                "reduced_ew_backreaction_closed": False,
                "complete_tensor_backreaction": False,
                "whole_model_validated": False,
            },
        }

    generic = scenario("generic_nonzero_portals", vevs, GENERIC_H_PORTALS)
    bounds = naturalness_bounds(vevs, tuning_budget=10.0)
    # One quarter of each individual T=10 bound gives four equal 2.5-self
    # contributions, so the aggregate portal burden is exactly ten self units.
    sequestered_portals = {name: 0.25 * bound for name, bound in bounds.items()}
    sequestered = scenario("tuning_budget_10_sequestered", vevs, sequestered_portals)

    generic_tuning = generic["electroweak_hierarchy"]["aggregate_abs_portal_over_h_self"]
    sequestered_tuning = sequestered["electroweak_hierarchy"][
        "aggregate_abs_portal_over_h_self"
    ]
    checks = {
        "all_four_generic_h_portals_nonzero": all(
            abs(value) > 0.0 for value in GENERIC_H_PORTALS.values()
        ),
        "generic_quartic_positive": generic["quartic_positive_definite"],
        "generic_hessian_positive": generic["radial_hessian_positive_by_congruence"],
        "generic_stationary": generic["stationarity"]["maximum_relative_residual"]
        < 1.0e-14,
        "generic_global_radial_minimum": generic["global_radial_minimum"],
        "generic_portals_expose_hierarchy_problem": generic_tuning > 1.0e20,
        "naturalness_bounds_are_extremely_small": max(bounds.values()) < 1.0e-12,
        "sequestered_quartic_positive": sequestered["quartic_positive_definite"],
        "sequestered_hessian_positive": sequestered[
            "radial_hessian_positive_by_congruence"
        ],
        "sequestered_stationary": sequestered["stationarity"][
            "maximum_relative_residual"
        ]
        < 1.0e-14,
        "sequestered_aggregate_within_budget": sequestered_tuning <= 10.0 * (
            1.0 + 1.0e-12
        ),
        "complete_tensor_backreaction_not_claimed": True,
        "whole_model_validation_not_claimed": True,
    }
    failures = [key for key, passed in checks.items() if not passed]
    report = {
        "status": (
            "REDUCED_EW_BACKREACTION_AND_BFB_CLOSED__FULL_TENSOR_MODEL_OPEN"
            if not failures
            else "REDUCED_EW_BACKREACTION_GATE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "fields": list(NAMES),
        "target_vevs_GeV": {name: float(value) for name, value in zip(NAMES, vevs)},
        "unification_anchor": anchor,
        "potential": {
            "shifted_form": (
                "V=1/4 sum_i lambda_i(r_i^2-v_i^2)^2 + "
                "1/4 sum_{i<j} epsilon_ij(r_i^2-v_i^2)(r_j^2-v_j^2)"
            ),
            "unshifted_mass_reconstruction": (
                "m_i^2=lambda_i v_i^2 + (1/2) sum_{j!=i} epsilon_ij v_j^2"
            ),
            "radial_hessian_identity": "H=2 diag(v) B diag(v)",
        },
        "generic_portal_scenario": generic,
        "tuning_budget": 10.0,
        "portal_bounds_for_tuning_budget_10": bounds,
        "sequestered_scenario": sequestered,
        "checks": checks,
        "flag": {
            "all_reduced_h_radial_portals_enabled": not failures,
            "quadratic_backreaction_retuning_solved": not failures,
            "reduced_radial_stationarity_proved": not failures,
            "reduced_radial_BFB_proved": not failures,
            "reduced_radial_hessian_positive": not failures,
            "generic_portals_naturally_explain_EW_hierarchy": False,
            "UV_sequestering_or_hierarchy_mechanism_required": True,
            "complete_tensor_backreaction": False,
            "complete_component_potential": False,
            "complete_global_vacuum": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The coupled five-field radial hierarchy is mathematically consistent "
            "after exact quadratic retuning and remains globally bounded.  However, "
            "generic nonzero portals induce an enormous electroweak mass cancellation; "
            "avoiding it requires extremely small portal couplings or a UV hierarchy "
            "mechanism.  Full SO(10) tensor backreaction remains open."
        ),
    }
    return _jsonable(report)


def write_markdown(report: dict[str, Any]) -> str:
    if report.get("n_failed"):
        return "\n".join(
            [
                "# Reduced electroweak backreaction gate — v20",
                "",
                f"**Status:** `{report['status']}`",
                "",
                f"Failures: `{report.get('failures', [])}`",
                "",
            ]
        )
    generic = report["generic_portal_scenario"]["electroweak_hierarchy"]
    bounds = report["portal_bounds_for_tuning_budget_10"]
    return "\n".join(
        [
            "# Reduced electroweak backreaction and hierarchy gate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact reduced result",
            "",
            "- All four reduced `h^2 r_i^2` portals are nonzero.",
            "- The target hierarchy is exactly stationary after reconstructing the quadratic mass parameters.",
            "- The quartic matrix is positive definite.",
            "- The radial Hessian is positive definite by `H=2 diag(v) B diag(v)`.",
            "",
            "## Hierarchy result",
            "",
            f"- Generic aggregate portal burden: `{generic['aggregate_abs_portal_over_h_self']:.6e}` times the electroweak self term.",
            "- Portal bounds for a tuning budget of ten:",
            *[f"  - `{name}`: `{value:.6e}`" for name, value in bounds.items()],
            "",
            "This is a reduced G3/G5 subtheorem, not the complete tensor vacuum.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    args = parser.parse_args(argv)
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.json.write_text(text, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(text, end="")
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
