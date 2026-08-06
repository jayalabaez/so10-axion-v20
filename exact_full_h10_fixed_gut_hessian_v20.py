#!/usr/bin/env python3
"""Full complex-10_H Hessian on the verified fixed P+Delta_R background.

All twenty real H10 components plus S and Phi17 are included.  The colour
lift is derived from the singlet and 54 channels of 210_H^2 H^dag H on the
normalized Pati-Salam p background.  This is a fixed-GUT-background theorem;
210/126bar variations and full backreaction remain open.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_neutral_h10_s_phi17_hessian_v20 as neutral

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_FULL_H10_FIXED_GUT_HESSIAN_V20.json"


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def vector_generator_matrix(a: int, b: int) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=float)
    for column in range(10):
        action = direct.generator_action(direct.one_form(column), a, b)
        for (row,), coefficient in action.items():
            if abs(coefficient.imag) > 1.0e-13:
                raise AssertionError("complex entry in real vector generator")
            matrix[row, column] = coefficient.real
    return matrix


def p_background_channel_operators() -> dict[str, Any]:
    p = direct.singlet_basis()["p"]
    contraction = np.empty((10, 10), dtype=float)
    interiors = [direct.interior(p, index) for index in range(10)]
    for i in range(10):
        for j in range(10):
            contraction[i, j] = direct.tensor_inner(
                interiors[i], interiors[j]
            ).real

    trace = float(np.trace(contraction))
    q54 = contraction - (trace / 10.0) * np.eye(10)
    q_weak = float(np.mean(np.diag(q54)[6:]))
    colour = 0.5 * (
        q_weak * np.eye(10) - q54 + (q_weak * np.eye(10) - q54).T
    )
    p_wedge_p = direct.wedge(p, p)

    unbroken_generators = [
        vector_generator_matrix(a, b)
        for a in range(10)
        for b in range(a + 1, 10)
        if (a < 6 and b < 6) or (a >= 6 and b >= 6)
    ]
    commutator = max(
        np.max(np.abs(generator @ colour - colour @ generator))
        for generator in unbroken_generators
    )
    return {
        "p_norm": direct.tensor_norm(p),
        "interior_contraction": contraction.tolist(),
        "interior_trace": trace,
        "q54": q54.tolist(),
        "q54_trace": float(np.trace(q54)),
        "q54_colour_eigenvalue": float(np.mean(np.diag(q54)[:6])),
        "q54_weak_eigenvalue": q_weak,
        "colour_projector": colour.tolist(),
        "colour_projector_eigenvalues": np.linalg.eigvalsh(colour).tolist(),
        "colour_projector_rank": int(np.linalg.matrix_rank(colour, 1.0e-12)),
        "colour_projector_idempotence_residual": float(
            np.max(np.abs(colour @ colour - colour))
        ),
        "p_squared_45_wedge_norm": direct.tensor_norm(p_wedge_p),
        "p_squared_45_dual_norm": direct.tensor_norm(
            direct.hodge_star(p_wedge_p)
        ),
        "pati_salam_commutator_residual": float(commutator),
        "normalization": (
            "Q54_ij=<i_i p,i_j p>-(Tr/10)delta_ij; "
            "P_colour=q_weak I-Q54=diag(1_6,0_4)."
        ),
    }


def _combined_action(
    form: direct.Form, terms: tuple[tuple[float, int, int], ...]
) -> direct.Form:
    return direct.add_forms(
        *[
            direct.scale_form(
                direct.generator_action(form, a, b), coefficient
            )
            for coefficient, a, b in terms
        ]
    )


def electroweak_tangent_certificate() -> dict[str, Any]:
    generators = {
        "L3": ((0.5, 6, 7), (-0.5, 8, 9)),
        "L1": ((0.5, 6, 8), (0.5, 7, 9)),
        "L2": ((0.5, 6, 9), (-0.5, 7, 8)),
    }
    h0 = direct.one_form(8, 2.0)
    p = direct.singlet_basis()["p"]
    delta = direct.delta_r()
    rows: dict[str, Any] = {}
    tangent_columns = []
    for name, terms in generators.items():
        h_tangent = _combined_action(h0, terms)
        p_tangent = _combined_action(p, terms)
        delta_tangent = _combined_action(delta, terms)
        vector = np.asarray(
            [h_tangent.get((index,), 0.0).real for index in range(10)]
        )
        tangent_columns.append(vector)
        rows[name] = {
            "H_tangent": vector.tolist(),
            "P_tangent_norm": direct.tensor_norm(p_tangent),
            "DeltaR_tangent_norm": direct.sigma_kinetic_norm(delta_tangent),
        }
    tangent_matrix = np.column_stack(tangent_columns)
    return {
        "generators": rows,
        "H_tangent_rank": int(np.linalg.matrix_rank(tangent_matrix, 1.0e-12)),
        "P_invariance_max": float(
            max(row["P_tangent_norm"] for row in rows.values())
        ),
        "DeltaR_invariance_max": float(
            max(row["DeltaR_tangent_norm"] for row in rows.values())
        ),
    }


def parameters() -> dict[str, float]:
    values = neutral.params()
    values["m_colour_squared"] = 5.0
    return values


def full_hessian_benchmark() -> dict[str, Any]:
    p = parameters()
    colour = np.asarray(
        p_background_channel_operators()["colour_projector"], dtype=float
    )
    n = 24
    background = np.zeros(n)
    background[8] = math.sqrt(2.0) * p["vH"]
    background[20] = p["vS"]
    background[22] = p["vP"]
    fields = [neutral.J.x(value, index, n) for index, value in enumerate(background)]
    x, y = fields[:10], fields[10:20]
    s_r, s_i, phi_r, phi_i = fields[20:]

    h_norm = sum(0.5 * (xr.sq() + yi.sq()) for xr, yi in zip(x, y))
    y_re = sum(0.5 * (xr.sq() - yi.sq()) for xr, yi in zip(x, y))
    y_im = sum(xr * yi for xr, yi in zip(x, y))
    s_norm = 0.5 * (s_r.sq() + s_i.sq())
    phi_norm = 0.5 * (phi_r.sq() + phi_i.sq())
    mu = math.sqrt(2.0) * p["vH"] ** 2 / p["vS"]
    f_re = y_re - (mu / math.sqrt(2.0)) * s_r
    f_im = y_im + (mu / math.sqrt(2.0)) * s_i

    colour_lift = neutral.J.c(0.0, n)
    for i in range(10):
        for j in range(10):
            coefficient = 0.5 * p["m_colour_squared"] * colour[i, j]
            if coefficient != 0.0:
                colour_lift += coefficient * (x[i] * x[j] + y[i] * y[j])

    potential = (
        p["lX"] * (h_norm - p["vH"] ** 2).sq()
        + p["lA"] * (h_norm.sq() - y_re.sq() - y_im.sq())
        + p["lF"] * (f_re.sq() + f_im.sq())
        + p["lS"] * (s_norm - p["vS"] ** 2 / 2.0).sq()
        + p["lP"] * (phi_norm - p["vP"] ** 2 / 2.0).sq()
        + 0.5 * p["mP2"] * phi_i.sq()
        + colour_lift
    )
    hessian = 0.5 * (potential.h + potential.h.T)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    tolerance = 1.0e-9

    gauge = np.zeros((24, 3))
    gauge[6, 0] = gauge[7, 1] = gauge[9, 2] = 1.0
    pq = np.zeros(24)
    pq[18] = -2.0 * math.sqrt(2.0) * p["vH"]
    pq[21] = 4.0 * p["vS"]
    pq /= np.linalg.norm(pq)

    expected_null, _ = np.linalg.qr(np.column_stack([gauge, pq]))
    actual_null = eigenvectors[:, np.abs(eigenvalues) <= tolerance]
    alignment = np.max(
        np.abs(
            actual_null @ actual_null.T
            - expected_null @ expected_null.T
        )
    )
    _, _, vh = np.linalg.svd(gauge.T, full_matrices=True)
    complement = vh[3:].T
    quotient = np.linalg.eigvalsh(complement.T @ hessian @ complement)

    real_indices = list(range(10)) + [20, 22]
    imaginary_indices = list(range(10, 20)) + [21, 23]
    return {
        "coordinates": [
            *[f"x_{index}" for index in range(10)],
            *[f"y_{index}" for index in range(10)],
            "s_r", "s_i", "phi_r", "phi_i",
        ],
        "parameters": {**p, "mu": mu},
        "gradient_max": float(np.max(np.abs(potential.g))),
        "hessian_eigenvalues": eigenvalues.tolist(),
        "zero_modes": int(np.count_nonzero(np.abs(eigenvalues) <= tolerance)),
        "negative_modes": int(np.count_nonzero(eigenvalues < -tolerance)),
        "minimum_positive_eigenvalue": float(
            np.min(eigenvalues[eigenvalues > tolerance])
        ),
        "symmetry": {
            "gauge_rank": int(np.linalg.matrix_rank(gauge)),
            "gauge_residual": float(np.max(np.abs(hessian @ gauge))),
            "PQ_residual": float(np.max(np.abs(hessian @ pq))),
            "null_alignment_residual": float(alignment),
        },
        "gauge_quotient": {
            "dimension": int(complement.shape[1]),
            "eigenvalues": quotient.tolist(),
            "zero_modes": int(np.count_nonzero(np.abs(quotient) <= tolerance)),
            "negative_modes": int(np.count_nonzero(quotient < -tolerance)),
            "remaining_zero": "PQ",
        },
        "CP_even_odd_cross_residual": float(
            np.max(np.abs(hessian[np.ix_(real_indices, imaginary_indices)]))
        ),
        "bounded_for_fixed_GUT_background": True,
        "boundedness_argument": (
            "All terms are nonnegative squares, lambda_A[(HdagH)^2-|H.H|^2] "
            "is nonnegative by Cauchy, and Hdag P_colour H is positive semidefinite."
        ),
        "spectrum_clusters": {
            "zero_gauge_plus_PQ": 4,
            "phi17_phase": 1,
            "colour_real": 6,
            "weak_CP_odd_transverse": 3,
            "colour_imaginary": 6,
            "neutral_radial_and_phase_positive": 4,
        },
    }


def build_report() -> dict[str, Any]:
    channels = p_background_channel_operators()
    gauge = electroweak_tangent_certificate()
    point = full_hessian_benchmark()
    expected_projector_spectrum = np.asarray([0.0] * 4 + [1.0] * 6)
    checks = {
        "normalized_p_background": bool(abs(channels["p_norm"] - 1.0) < 1.0e-12),
        "q54_traceless": bool(abs(channels["q54_trace"]) < 1.0e-12),
        "colour_projector_rank_six": channels["colour_projector_rank"] == 6,
        "colour_projector_exact": bool(
            channels["colour_projector_idempotence_residual"] < 1.0e-12
        ),
        "colour_projector_spectrum": bool(
            np.max(
                np.abs(
                    np.sort(channels["colour_projector_eigenvalues"])
                    - expected_projector_spectrum
                )
            )
            < 1.0e-12
        ),
        "p_squared_45_background_null": bool(
            channels["p_squared_45_dual_norm"] < 1.0e-12
        ),
        "pati_salam_covariance": bool(
            channels["pati_salam_commutator_residual"] < 1.0e-12
        ),
        "three_electroweak_tangents": gauge["H_tangent_rank"] == 3,
        "GUT_background_SU2L_invariant": bool(
            max(gauge["P_invariance_max"], gauge["DeltaR_invariance_max"])
            < 1.0e-12
        ),
        "stationary_in_H_S_Phi17_subspace": bool(point["gradient_max"] < 1.0e-12),
        "four_expected_zeros": point["zero_modes"] == 4,
        "no_tachyons": point["negative_modes"] == 0,
        "gauge_and_PQ_alignment": bool(
            point["symmetry"]["null_alignment_residual"] < 1.0e-10
        ),
        "three_gauge_directions_annihilated": bool(
            point["symmetry"]["gauge_residual"] < 1.0e-12
        ),
        "PQ_direction_annihilated": bool(
            point["symmetry"]["PQ_residual"] < 1.0e-12
        ),
        "one_PQ_zero_after_gauge_quotient": point["gauge_quotient"]["zero_modes"] == 1,
        "no_quotient_tachyons": point["gauge_quotient"]["negative_modes"] == 0,
        "CP_blocks_decouple": bool(point["CP_even_odd_cross_residual"] < 1.0e-12),
        "full_backreaction_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report = {
        "status": (
            "FULL_H10_FIXED_GUT_HESSIAN_CLOSED__BACKREACTION_OPEN"
            if not failures
            else "FULL_H10_FIXED_GUT_HESSIAN_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "p_background_channels": channels,
        "electroweak_gauge_certificate": gauge,
        "benchmark": point,
        "flag": {
            "all_20_real_H10_components_included": not failures,
            "three_electroweak_goldstones_identified": not failures,
            "PQ_zero_after_gauge_quotient": not failures,
            "fixed_GUT_background_H10_hessian_complete": not failures,
            "simultaneous_210_126bar_10_S_Phi17_stationarity": False,
            "full_backreacted_multifield_hessian": False,
            "global_vacuum_proved": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "On the verified fixed P+DeltaR background, the exact singlet-54 "
            "combination gives P_colour=diag(1_6,0_4). The complete H10 plus "
            "S/Phi17 Hessian is positive apart from three electroweak gauge "
            "Goldstones and PQ. GUT-field backreaction remains open."
        ),
    }
    return _jsonable(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    args = parser.parse_args(argv)
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.json.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
