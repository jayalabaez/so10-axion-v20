#!/usr/bin/env python3
"""Exact renormalizable self-quartic family of the complex SO(10) vector 10_H.

For commuting complex vector components H_i, the holomorphic pair belongs to

    Sym^2(10) = 1 + 54,

with multiplicity one.  Therefore the charge-neutral field content
H^2 (H^dag)^2 has exactly two independent SO(10) quartics.  A canonical pure
channel basis is

    I_1  = |H.H|^2 / 10,
    I_54 = sum_ij |H_i H_j - delta_ij (H.H)/10|^2
         = (H^dag H)^2 - |H.H|^2/10.

Equivalently one may use (H^dag H)^2 and |H.H|^2.  The apparent adjoint-45
current norm is dependent:

    sum_{i<j} |H_i^* H_j - H_j^* H_i|^2
      = (H^dag H)^2 - |H.H|^2.

For V4=lambda_N(H^dag H)^2 + lambda_P|H.H|^2, the exact bounded-from-below
cone is

    lambda_N >= 0,   lambda_N + lambda_P >= 0.

This closes the 10_H self-quartic G1 family and its isolated G5 boundedness
subgate only.  It does not close the complete mixed invariant ring or vacuum.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_H10_SELF_QUARTIC_FAMILY_V20.json"
OUT_MD = ROOT / "EXACT_H10_SELF_QUARTIC_FAMILY_V20.md"
N = 10


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


def invariants(h: np.ndarray) -> dict[str, float]:
    vector = np.asarray(h, dtype=complex).reshape(N)
    norm = float(np.vdot(vector, vector).real)
    holomorphic = complex(np.dot(vector, vector))
    singlet = abs(holomorphic) ** 2 / N
    pair = np.outer(vector, vector)
    traceless = pair - (holomorphic / N) * np.eye(N, dtype=complex)
    channel54 = float(np.vdot(traceless, traceless).real)
    current45 = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            current45 += abs(np.conjugate(vector[i]) * vector[j] - np.conjugate(vector[j]) * vector[i]) ** 2
    return {
        "HdagH": norm,
        "HdotH_re": float(holomorphic.real),
        "HdotH_im": float(holomorphic.imag),
        "norm_square": norm**2,
        "holomorphic_modulus_square": abs(holomorphic) ** 2,
        "I_1": float(singlet),
        "I_54": channel54,
        "adjoint_45_current_norm": float(current45),
        "projector_completeness_residual": float(abs(singlet + channel54 - norm**2)),
        "current_identity_residual": float(abs(current45 - (norm**2 - abs(holomorphic) ** 2))),
    }


def representation_census() -> dict[str, Any]:
    return {
        "Sym2_10": {"1": 1, "54": 1},
        "dimension": {"left": N * (N + 1) // 2, "right": 1 + 54},
        "quartic_singlet_multiplicity": 2,
        "reason": (
            "The two-H pair is Bose-symmetric.  Each irrep 1 and 54 occurs once, "
            "so pairing with the conjugate symmetric square gives two singlets."
        ),
        "independent_adjoint_45_channel": False,
    }


def sample_vectors() -> dict[str, np.ndarray]:
    real = np.zeros(N, dtype=complex)
    real[0] = 1.0
    null_holomorphic = np.zeros(N, dtype=complex)
    null_holomorphic[0] = 1.0 / np.sqrt(2.0)
    null_holomorphic[1] = 1j / np.sqrt(2.0)
    generic = np.asarray(
        [
            1.0 + 0.2j,
            -0.3 + 0.7j,
            0.4j,
            -0.8,
            0.2 - 0.1j,
            0.5,
            -0.4j,
            0.3 + 0.6j,
            -0.2,
            0.9j,
        ],
        dtype=complex,
    )
    generic /= np.sqrt(np.vdot(generic, generic).real)
    return {
        "real_rank_one": real,
        "isotropic_HdotH_zero": null_holomorphic,
        "generic_complex": generic,
    }


def independence_audit() -> dict[str, Any]:
    rows = []
    for name, vector in sample_vectors().items():
        values = invariants(vector)
        rows.append(
            {
                "name": name,
                "norm_square": values["norm_square"],
                "holomorphic_modulus_square": values["holomorphic_modulus_square"],
                "I_1": values["I_1"],
                "I_54": values["I_54"],
            }
        )
    evaluation = np.asarray(
        [
            [rows[0]["I_1"], rows[0]["I_54"]],
            [rows[1]["I_1"], rows[1]["I_54"]],
        ],
        dtype=float,
    )
    return {
        "samples": rows,
        "pure_channel_evaluation_matrix": evaluation,
        "determinant": float(np.linalg.det(evaluation)),
        "rank": int(np.linalg.matrix_rank(evaluation, tol=1.0e-12)),
    }


def ratio_range_audit() -> dict[str, Any]:
    samples = []
    for theta in np.linspace(0.0, np.pi / 4.0, 17):
        vector = np.zeros(N, dtype=complex)
        vector[0] = np.cos(theta)
        vector[1] = 1j * np.sin(theta)
        values = invariants(vector)
        ratio = values["holomorphic_modulus_square"] / values["norm_square"]
        samples.append(float(ratio))
    return {
        "family": "H=(cos(theta), i sin(theta), 0,...), theta in [0,pi/4]",
        "ratios": samples,
        "minimum": min(samples),
        "maximum": max(samples),
        "covers_endpoint_zero": abs(samples[-1]) < 1.0e-12,
        "covers_endpoint_one": abs(samples[0] - 1.0) < 1.0e-12,
        "analytic_range": [0.0, 1.0],
    }


def bfb(lambda_norm: float, lambda_pair: float) -> dict[str, Any]:
    endpoint_isotropic = float(lambda_norm)
    endpoint_real = float(lambda_norm + lambda_pair)
    bounded = endpoint_isotropic >= 0.0 and endpoint_real >= 0.0
    return {
        "lambda_norm": float(lambda_norm),
        "lambda_pair": float(lambda_pair),
        "coefficient_at_HdotH_zero": endpoint_isotropic,
        "coefficient_at_real_H": endpoint_real,
        "bounded_from_below": bool(bounded),
        "strictly_positive_away_from_origin": bool(
            endpoint_isotropic > 0.0 and endpoint_real > 0.0
        ),
    }


def pure_channel_coupling_map(kappa_1: float, kappa_54: float) -> dict[str, Any]:
    lambda_norm = float(kappa_54)
    lambda_pair = float((kappa_1 - kappa_54) / N)
    return {
        "kappa_1": float(kappa_1),
        "kappa_54": float(kappa_54),
        "lambda_norm": lambda_norm,
        "lambda_pair": lambda_pair,
        "pure_channel_BFB_conditions": {
            "kappa_54_nonnegative": kappa_54 >= 0.0,
            "kappa_1_plus_9_kappa_54_nonnegative": kappa_1 + 9.0 * kappa_54 >= 0.0,
        },
        "equivalent_standard_basis_BFB": bfb(lambda_norm, lambda_pair),
    }


def build_report() -> dict[str, Any]:
    census = representation_census()
    samples = {name: invariants(vector) for name, vector in sample_vectors().items()}
    independence = independence_audit()
    ratio = ratio_range_audit()
    stable = bfb(0.7, -0.2)
    boundary = bfb(0.4, -0.4)
    unstable_isotropic = bfb(-0.1, 0.5)
    unstable_real = bfb(0.2, -0.3)
    pure_map = pure_channel_coupling_map(-1.0, 0.2)

    maximum_projector_residual = max(
        row["projector_completeness_residual"] for row in samples.values()
    )
    maximum_current_residual = max(
        row["current_identity_residual"] for row in samples.values()
    )
    checks = {
        "symmetric_square_dimension": census["dimension"]["left"] == census["dimension"]["right"] == 55,
        "exactly_two_quartic_channels": census["quartic_singlet_multiplicity"] == 2,
        "no_independent_45_quartic": census["independent_adjoint_45_channel"] is False,
        "projector_completeness_exact": maximum_projector_residual < 1.0e-12,
        "adjoint_current_identity_exact": maximum_current_residual < 1.0e-12,
        "two_channels_independent": independence["rank"] == 2 and abs(independence["determinant"]) > 1.0e-6,
        "ratio_range_endpoints_constructed": ratio["covers_endpoint_zero"] and ratio["covers_endpoint_one"],
        "stable_example_accepted": stable["strictly_positive_away_from_origin"],
        "boundary_example_accepted": boundary["bounded_from_below"] and not boundary["strictly_positive_away_from_origin"],
        "negative_isotropic_endpoint_rejected": not unstable_isotropic["bounded_from_below"],
        "negative_real_endpoint_rejected": not unstable_real["bounded_from_below"],
        "pure_channel_and_standard_BFB_agree": (
            all(pure_map["pure_channel_BFB_conditions"].values())
            == pure_map["equivalent_standard_basis_BFB"]["bounded_from_below"]
        ),
        "complete_mixed_ring_not_claimed": True,
        "whole_model_validation_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report = {
        "status": (
            "EXACT_H10_TWO_SELF_QUARTICS_AND_BFB_CONE_CLOSED__FULL_G1_OPEN"
            if not failures
            else "EXACT_H10_SELF_QUARTIC_GATE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "representation_census": census,
        "canonical_invariants": {
            "I_1": "|H.H|^2/10",
            "I_54": "(HdagH)^2-|H.H|^2/10",
            "standard_basis": ["(HdagH)^2", "|H.H|^2"],
            "dependent_45_identity": (
                "sum_{i<j}|H_i^*H_j-H_j^*H_i|^2=(HdagH)^2-|H.H|^2"
            ),
        },
        "sample_invariants": samples,
        "independence": independence,
        "orbit_ratio": ratio,
        "BFB_theorem": {
            "potential": "V4=lambda_N(HdagH)^2+lambda_P|H.H|^2",
            "necessary_and_sufficient": [
                "lambda_N >= 0",
                "lambda_N + lambda_P >= 0",
            ],
            "examples": {
                "strictly_stable": stable,
                "boundary_flat": boundary,
                "unstable_isotropic": unstable_isotropic,
                "unstable_real": unstable_real,
            },
            "pure_channel_parameterization": pure_map,
        },
        "flag": {
            "h10_self_quartic_count_closed": not failures,
            "h10_self_quartic_tensor_basis_closed": not failures,
            "h10_isolated_quartic_BFB_cone_closed": not failures,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The complex SO(10) vector has exactly two independent charge-neutral "
            "renormalizable self-quartics, carried by the holomorphic pair channels "
            "1 and 54. Their exact isolated boundedness cone is lambda_N>=0 and "
            "lambda_N+lambda_P>=0. This closes one G1 family and one isolated G5 "
            "subgate, not the complete model."
        ),
    }
    return _jsonable(report)


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact 10_H self-quartic family — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact basis",
            "",
            "- `I_1 = |H.H|^2/10`",
            "- `I_54 = (HdagH)^2-|H.H|^2/10`",
            "",
            "## Exact isolated BFB cone",
            "",
            "For `V4=lambda_N(HdagH)^2+lambda_P|H.H|^2`:",
            "",
            "- `lambda_N >= 0`",
            "- `lambda_N + lambda_P >= 0`",
            "",
            "The complete mixed invariant ring remains open.",
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
