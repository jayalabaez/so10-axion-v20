#!/usr/bin/env python3
"""Higgs-portal threshold at the tuned G3 target.

``g3_tuned_target_effective_higgs_quartic_v20`` shows that with the
certified couplings the light doublet has no tree-level coupling to heavy
modes, so lambda_eff equals the direct H quartic (1).  Any nonnegative
matching quartic then gives m_h >= 133.6 GeV at one loop, while the SM needs
lambda(M_GUT) ~ -0.034.

The benchmark sets every S portal to zero.  This module switches on the one
declared renormalizable H-S portal,

    O34 = 10_H 10_H^dag S S^dag = lambda_HS |H|^2 |S|^2,

and retunes O06 so the doublet stays massless.  With <S> = r M, the
radial S mode then couples to |h|^2 and heavy exchange lowers the quartic:

    lambda_eff = lambda_H - lambda_HS^2 / (4 lambda_S),

with lambda_H the O36_B02 quartic and lambda_S the O23 coefficient.  This is
the familiar singlet threshold of Higgs-portal stabilization (for example
Elias-Miro et al. 2012; the SMASH axion model).  Every number is recomputed on
the live exact-X compiler through the same exact polynomial differences as the
parent module.  Positive lambda_HS adds a nonnegative quartic, so the existing
BFB certificate survives.

Scope: tree-level matching at M_GUT with the certified hierarchy r = 1/5.  At
the physical hierarchy S sits at M_I and the threshold would sit there
instead, which is a different running problem.  Nothing is closed or
excluded.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_tuned_target_effective_higgs_quartic_v20 as quartic
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_TUNED_TARGET_PORTAL_THRESHOLD_V20.json"
OUT_MD = ROOT / "G3_TUNED_TARGET_PORTAL_THRESHOLD_V20.md"

PORTAL_ID = "lambda::O34_B01_Hdag_H_norm"
H_QUARTIC_ID = "lambda::O36_B02_H_self_quartics"
S_QUARTIC_ID = "lambda::O23_B01_singlet_polynomial"
PORTAL_SCAN = (0.5, 1.0, 2.0)
FORMULA_ATOL = 1.0e-9
PERTURBATIVE_LIMIT = 4.0 * math.pi


def portal_coefficients(portal: float) -> dict[str, float]:
    """Tuned coefficients plus the portal, with O06 retuned to a massless doublet."""
    coefficients = quartic.tuned_coefficients()
    coefficients[PORTAL_ID] = portal
    _, _, hessian = target.assemble(target.gut_point_rows(), coefficients)
    matrix, _ = target.hermitian_h_mass_matrix(hessian)
    lightest = float(
        np.min(np.linalg.eigvalsh(matrix[target.DOUBLET_BLOCK, target.DOUBLET_BLOCK]))
    )
    coefficients[target.O06_ID] -= lightest
    return coefficients


def portal_point(portal: float) -> dict[str, Any]:
    coefficients = portal_coefficients(portal)
    q0 = chart.pack(target.gut_point_state())
    _, gradient, hessian = target.assemble(target.gut_point_rows(), coefficients)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    massive = np.abs(eigenvalues) > quartic.ZERO_MODE_ATOL
    heavy_vectors = eigenvectors[:, massive]
    heavy_values = eigenvalues[massive]
    matrix, _ = target.hermitian_h_mass_matrix(hessian)
    spectrum = target.sm_branch_spectrum(matrix)

    base_rows = quartic._h_rows_at_tuned_point()
    parameter_ids = frozenset(base_rows)
    h_coefficients = {key: value for key, value in coefficients.items() if key in parameter_ids}
    _, g0, h0 = target.assemble(base_rows, h_coefficients)
    light = quartic.light_doublet_directions(hessian)
    directions = {"u0": light[0], "mixed_u0_u2": (light[0] + light[2]) / math.sqrt(2.0)}
    rows = {}
    for name, u in directions.items():
        _, gp, hp = target.assemble(quartic._h_rows_at(q0 + u, parameter_ids), h_coefficients)
        _, gm, hm = target.assemble(quartic._h_rows_at(q0 - u, parameter_ids), h_coefficients)
        coupling = gp + gm - 2.0 * g0
        fourth = float(u @ (hp + hm - 2.0 * h0) @ u)
        components = heavy_vectors.T @ coupling
        shift = 3.0 * float(np.sum(components**2 / heavy_values))
        rows[name] = {
            "coupling_vector_norm": float(np.linalg.norm(coupling)),
            "coupling_S_block_norm": float(np.linalg.norm(coupling[chart.S_SLICE])),
            "lambda_direct": fourth / 6.0,
            "heavy_exchange_shift": shift / 6.0,
            "lambda_eff": (fourth - shift) / 6.0,
        }
    lambda_h = coefficients[H_QUARTIC_ID]
    lambda_s = coefficients[S_QUARTIC_ID]
    formula = lambda_h - portal**2 / (4.0 * lambda_s)
    lambda_eff = float(np.mean([row["lambda_eff"] for row in rows.values()]))
    return {
        "lambda_HS": portal,
        "retuned_O06": coefficients[target.O06_ID],
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "negative_eigenvalues_below_minus_1e_minus_9": int(
            np.sum(eigenvalues < -quartic.ZERO_MODE_ATOL)
        ),
        "zero_modes": int(np.sum(~massive)),
        "light_h_spectrum": spectrum,
        "directions": rows,
        "lambda_eff": lambda_eff,
        "lambda_eff_formula": formula,
        "formula_residual": abs(lambda_eff - formula),
        "lambda_eff_spread": float(
            max(row["lambda_eff"] for row in rows.values())
            - min(row["lambda_eff"] for row in rows.values())
        ),
    }


def required_portal(lambda_target: float, lambda_h: float, lambda_s: float) -> float:
    return 2.0 * math.sqrt(lambda_s * (lambda_h - lambda_target))


def build_report() -> dict[str, Any]:
    points = [portal_point(value) for value in PORTAL_SCAN]
    coefficients = quartic.tuned_coefficients()
    lambda_h = coefficients[H_QUARTIC_ID]
    lambda_s = coefficients[S_QUARTIC_ID]
    lambda_target = quartic.lambda_gut_for_sm(quartic.M_GUT_REFERENCE_GEV)
    needed = required_portal(lambda_target, lambda_h, lambda_s)
    solution = portal_point(needed)
    lam_top = quartic.lambda_at_top(solution["lambda_eff"], quartic.M_GUT_REFERENCE_GEV)
    bfb_floor = float(2 * target.BETA**2)
    needed_at_floor = required_portal(lambda_target, bfb_floor, lambda_s)
    checks = {
        "every_portal_point_is_stationary": all(
            point["gradient_max_abs"] < target.STATIONARITY_ATOL for point in points + [solution]
        ),
        "every_portal_point_is_psd": all(
            point["negative_eigenvalues_below_minus_1e_minus_9"] == 0 for point in points + [solution]
        ),
        "doublet_stays_massless_after_O06_retune": all(
            abs(point["light_h_spectrum"]["weak_doublets"][0]["mass_squared"]) <= target.SPECTRUM_ATOL
            for point in points + [solution]
        ),
        "portal_couples_the_doublet_to_the_S_radial_mode": all(
            row["coupling_S_block_norm"] > 1.0e-3
            for point in points + [solution]
            for row in point["directions"].values()
        ),
        "exact_compiler_matches_singlet_threshold_formula": all(
            point["formula_residual"] < FORMULA_ATOL for point in points + [solution]
        ),
        "quartic_is_su2_x_u1_invariant": all(
            point["lambda_eff_spread"] < FORMULA_ATOL for point in points + [solution]
        ),
        "solution_reproduces_sm_lambda_at_mt": abs(lam_top - quartic.LAMBDA_SM_AT_MT) < 1.0e-8,
        "no_gate_closed_or_model_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    return {
        "model_contract_id": target.MODEL_CONTRACT_ID,
        "status": (
            "G3_TUNED_TARGET_HS_PORTAL_THRESHOLD_CAN_MATCH_SM_HIGGS_QUARTIC__G3_OPEN"
            if ok
            else "G3_TUNED_TARGET_PORTAL_THRESHOLD_AUDIT_FAILED"
        ),
        "overall_state": "CONSTRUCTIVE_TREE_LEVEL_RESOLUTION" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "units": target.UNITS,
        "couplings": {"lambda_H": lambda_h, "lambda_S": lambda_s, "portal_parameter": PORTAL_ID},
        "formula": "lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S)",
        "scan": points,
        "sm_matching": {
            "lambda_gut_required_one_loop": lambda_target,
            "M_GUT_GeV": quartic.M_GUT_REFERENCE_GEV,
            "lambda_HS_required_at_certified_lambda_H": needed,
            "lambda_HS_required_at_BFB_floor_lambda_H": needed_at_floor,
            "solution": solution,
            "solution_lambda_at_mt": lam_top,
            "solution_m_h_tree_GeV": quartic.higgs_mass_tree(lam_top),
            "portal_perturbative": needed < PERTURBATIVE_LIMIT,
        },
        "bfb": (
            "lambda_HS > 0 adds the nonnegative quartic |H|^2 |S|^2, so every BFB "
            "certificate of the tuned potential survives unchanged."
        ),
        "flags": {
            "higgs_mass_tension_resolvable_by_declared_hs_portal": ok,
            "requires_nonzero_axion_portal": True,
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "tree_level_matching_only": True,
        },
        "scope": (
            "Tree-level matching at M_GUT with the certified hierarchy r = 1/5. At the "
            "physical hierarchy S sits at M_I and the same threshold would act there, "
            "which needs two-stage running."
        ),
        "verdict": (
            "Switching on the declared H-S portal O34 couples the light doublet to the "
            "S radial mode. The exact compiler reproduces the singlet threshold "
            "lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S) to machine precision. With the "
            "certified lambda_H = lambda_S = 1, lambda_HS = "
            f"{needed:.4f} gives the one-loop SM value lambda(M_GUT) = {lambda_target:.4f}; "
            "that is perturbative and keeps the potential bounded below. "
            "The Higgs-mass tension is therefore not structural: it asks for exactly "
            "the axion-Higgs portal the benchmark switched off. G3 stays open."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    matching = report["sm_matching"]
    lines = [
        "# H-S portal threshold at the tuned G3 target -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "| lambda_HS | retuned O06 | lambda_eff (compiler) | formula |",
        "|---|---|---|---|",
    ]
    for point in report["scan"] + [matching["solution"]]:
        lines.append(
            f"| {point['lambda_HS']:.6g} | {point['retuned_O06']:.6g} | "
            f"{point['lambda_eff']:.10g} | {point['lambda_eff_formula']:.10g} |"
        )
    lines += [
        "",
        f"- lambda_HS needed at lambda_H = 1: `{matching['lambda_HS_required_at_certified_lambda_H']:.6g}`;"
        f" at the BFB floor lambda_H = 1/200: `{matching['lambda_HS_required_at_BFB_floor_lambda_H']:.6g}`;",
        f"- resulting m_h (tree-level from one-loop lambda(M_t)): `{matching['solution_m_h_tree_GeV']:.2f}` GeV"
        " (the SM calibration gives 123.6 GeV tree-level for the measured mass);",
        "- G3: `OPEN`; whole model: neither validated nor excluded.",
        "",
    ]
    return "\n".join(lines)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(target._jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(target._jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
