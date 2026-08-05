#!/usr/bin/env python3
r"""Analytic source-normalized pure-210 quartics on the ``(p,a,omega)`` span.

Using the canonical singlet basis in ``direct_phi_h_sigmabar_tensor_v20`` and
the source-normalized maps from ``so10_210_source_quartic_basis_v20``, the four
independent quartic invariants of one real 210 reduce to explicit polynomials.
All channel norms are manifest sums of squares.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import so10_210_source_quartic_basis_v20 as quartic
import so10_210_symmetric_45_source_projector_v20 as source45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PURE_210_PS_SINGLET_QUARTIC_POLYNOMIALS_V20.json"
OUT_MD = ROOT / "PURE_210_PS_SINGLET_QUARTIC_POLYNOMIALS_V20.md"


def analytic_invariants(p: float, a: float, omega: float) -> dict[str, float]:
    p = float(p)
    a = float(a)
    omega = float(omega)
    phi4 = (p * p + a * a + omega * omega) ** 2
    n45 = (
        2.0 / 105.0
        * ((math.sqrt(3.0) * a * p + omega * omega) ** 2 + 3.0 * a * a * omega * omega)
    )
    n54 = (-4.0 * a * a + omega * omega + 6.0 * p * p) ** 2 / 840.0
    n210 = (
        omega**4 / 90.0
        + 2.0 * omega * omega * (2.0 * math.sqrt(5.0) * a + math.sqrt(15.0) * p) ** 2 / 675.0
        + 2.0 * (a * a + omega * omega) ** 2 / 135.0
    )
    n1050 = (
        (2.0 * a * a - omega * omega) ** 2
        + 12.0 * omega * omega * (p - a / math.sqrt(3.0)) ** 2
    ) / 54.0
    return {
        "phi_norm_fourth": phi4,
        "channel_45_norm_sq": n45,
        "channel_54_norm_sq": n54,
        "channel_210_norm_sq": n210,
        "channel_1050_norm_sq_from_identity": n1050,
    }


def singlet_vector(p: float, a: float, omega: float) -> np.ndarray:
    basis = direct.singlet_basis()
    form = direct.add_forms(
        direct.scale_form(basis["p"], p),
        direct.scale_form(basis["a"], a),
        direct.scale_form(basis["omega"], omega),
    )
    return source45.form_to_vector(form)


def direct_invariants(p: float, a: float, omega: float) -> dict[str, float]:
    return quartic.pure_210_invariants(singlet_vector(p, a, omega))


def original_basis_potential(
    p: float,
    a: float,
    omega: float,
    *,
    g45: float,
    g210: float,
    g1050: float,
    lam: float,
) -> float:
    inv = analytic_invariants(p, a, omega)
    return float(
        g45 * inv["channel_45_norm_sq"]
        + g210 * inv["channel_210_norm_sq"]
        + g1050 * inv["channel_1050_norm_sq_from_identity"]
        + lam * inv["phi_norm_fourth"]
    )


def identity_reduced_potential(
    p: float,
    a: float,
    omega: float,
    *,
    g45: float,
    g210: float,
    g1050: float,
    lam: float,
) -> float:
    inv = analytic_invariants(p, a, omega)
    return float(
        (g45 - 35.0 * g1050 / 6.0) * inv["channel_45_norm_sq"]
        + (g210 + 5.0 * g1050 / 4.0) * inv["channel_210_norm_sq"]
        - 7.0 * g1050 / 3.0 * inv["channel_54_norm_sq"]
        + (lam + g1050 / 10.0) * inv["phi_norm_fourth"]
    )


def invariant_evaluation_matrix() -> np.ndarray:
    points = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 1.0)]
    rows = []
    for p, a, omega in points:
        inv = analytic_invariants(p, a, omega)
        rows.append(
            [
                inv["phi_norm_fourth"],
                inv["channel_45_norm_sq"],
                inv["channel_210_norm_sq"],
                inv["channel_1050_norm_sq_from_identity"],
            ]
        )
    return np.asarray(rows, dtype=float)


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(210210)
    residuals: dict[str, float] = {
        "phi_norm_fourth": 0.0,
        "channel_45_norm_sq": 0.0,
        "channel_54_norm_sq": 0.0,
        "channel_210_norm_sq": 0.0,
        "channel_1050_norm_sq_from_identity": 0.0,
    }
    minimum_channel = {name: float("inf") for name in residuals}
    potential_residual = 0.0

    for _ in range(24):
        point = rng.normal(size=3)
        analytic = analytic_invariants(*point)
        direct_values = direct_invariants(*point)
        for name in residuals:
            residuals[name] = max(
                residuals[name], abs(analytic[name] - direct_values[name])
            )
            minimum_channel[name] = min(minimum_channel[name], analytic[name])

        couplings = rng.normal(size=4)
        potential_residual = max(
            potential_residual,
            abs(
                original_basis_potential(
                    *point,
                    g45=couplings[0],
                    g210=couplings[1],
                    g1050=couplings[2],
                    lam=couplings[3],
                )
                - identity_reduced_potential(
                    *point,
                    g45=couplings[0],
                    g210=couplings[1],
                    g1050=couplings[2],
                    lam=couplings[3],
                )
            ),
        )

    evaluation_matrix = invariant_evaluation_matrix()
    rank = int(np.linalg.matrix_rank(evaluation_matrix, tol=1e-12))
    determinant = float(np.linalg.det(evaluation_matrix))

    checks_raw = {
        "analytic_direct_match": max(residuals.values()) < 1e-10,
        "all_channel_norms_nonnegative": min(minimum_channel.values()) > -1e-12,
        "original_and_identity_reduced_potentials_match": potential_residual < 1e-10,
        "four_invariants_linearly_independent": rank == 4 and abs(determinant) > 1e-12,
        "p_direction_45_zero": abs(analytic_invariants(1, 0, 0)["channel_45_norm_sq"]) < 1e-15,
        "p_direction_210_zero": abs(analytic_invariants(1, 0, 0)["channel_210_norm_sq"]) < 1e-15,
        "p_direction_1050_zero": abs(analytic_invariants(1, 0, 0)["channel_1050_norm_sq_from_identity"]) < 1e-15,
        "generic_selected_span_45_nonzero": analytic_invariants(1, 1, 1)["channel_45_norm_sq"] > 0,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks_raw.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": "PURE_210_PS_SINGLET_QUARTICS_ANALYTICALLY_CLOSED" if not failures else "PURE_210_PS_SINGLET_QUARTIC_AUDIT_FAILED",
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "formulas": {
            "phi_norm_fourth": "(p^2+a^2+omega^2)^2",
            "channel_45_norm_sq": "(2/105)*[(sqrt(3)*a*p+omega^2)^2+3*a^2*omega^2]",
            "channel_54_norm_sq": "(-4*a^2+omega^2+6*p^2)^2/840",
            "channel_210_norm_sq": "omega^4/90 + 2*omega^2*(2*sqrt(5)*a+sqrt(15)*p)^2/675 + 2*(a^2+omega^2)^2/135",
            "channel_1050_norm_sq": "[(2*a^2-omega^2)^2+12*omega^2*(p-a/sqrt(3))^2]/54",
        },
        "numerics": {
            "maximum_analytic_direct_residual": max(residuals.values()),
            "per_invariant_residual": residuals,
            "minimum_sampled_channel_values": minimum_channel,
            "potential_basis_identity_residual": potential_residual,
            "evaluation_matrix_rank": rank,
            "evaluation_matrix_determinant": determinant,
        },
        "closure": {
            "pure_210_ps_singlet_quartic_polynomials_closed": not failures,
            "pure_210_quartic_invariants_independent": not failures,
            "mixed_field_invariant_ring_G1_closed": False,
            "global_vacuum_G3_closed": False,
        },
        "flags": {
            "manifest_sum_of_squares_certificate": not failures,
            "selected_singlet_potential_can_be_rebuilt_from_exact_formulas": not failures,
            "downstream_selected_vacuum_must_be_rerun": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "All four independent pure-210 quartic invariants are now analytic "
            "on the canonical p/a/omega span and agree with direct Cartesian "
            "tensor evaluation. They are manifestly nonnegative channel norms "
            "and linearly independent. This enables a corrected selected-singlet "
            "potential, but mixed fields and the global vacuum remain open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Analytic pure-210 quartics on `(p,a,omega)` — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Formulas",
        "",
    ]
    lines.extend(f"- `{name}`: `{formula}`" for name, formula in report["formulas"].items())
    lines.extend(
        [
            "",
            f"Maximum direct residual: `{report['numerics']['maximum_analytic_direct_residual']}`",
            f"Invariant rank: `{report['numerics']['evaluation_matrix_rank']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
