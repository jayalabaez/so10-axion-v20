#!/usr/bin/env python3
"""H-S portal threshold at the tuned G3 point: exact formula and its limit.

``g3_tuned_target_effective_higgs_quartic_v20`` shows that at the tuned point
(certified couplings with O06 retuned to 0, H = 0) the light doublet has no
tree-level coupling to heavy modes, so lambda_eff equals the direct H quartic.
This module switches on the declared renormalizable H-S portal

    O34 = 10_H 10_H^dag S S^dag = lambda_HS |H|^2 |S|^2,

retunes O06 so the doublet stays massless, and establishes on the live exact-X
compiler:

* the singlet threshold lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S), with
  lambda_H the O36_B02 quartic and lambda_S the O23 coefficient (census
  normalization V > lambda_S |S|^4);
* its limit.  In the (H, S) block, with y = |h|^2 and x = |S|^2 - r^2,

      V - V0 = lambda_H y^2 + lambda_HS x y + lambda_S x^2 .

  The tuned point is a tree-level local minimum only if lambda_eff >= 0, i.e.
  lambda_HS <= 2 sqrt(lambda_H lambda_S).  The Hessian stays PSD beyond that
  bound, but the exactly flat doublet then descends along the H-S valley
  (V - V0 = lambda_eff y^2), and the S = 0 branch reaches
  V - V0 = r^4 lambda_S lambda_eff / lambda_H < 0 at |h|^2 = lambda_HS r^2 /
  (2 lambda_H): electroweak symmetry breaks near M_GUT/5 and PQ is restored.

Two-loop SM running (g3_physical_hierarchy_higgs_stability_v20) needs
lambda(M_GUT) ~ -0.015 for the measured Higgs mass.  Reaching it through this
portal at lambda_H = lambda_S = 1 needs lambda_HS ~ 2.015 > 2, so the matched
point is a degenerate saddle.  A tree-level portal threshold therefore cannot
produce the negative matching quartic at a G3-admissible (locally minimal)
point.  The same local-minimality bound applies to any tree-level |h|^2
coupling to a heavy mode.  Separately, the certified Delta_R is not the SM
singlet of the 126bar (see g3_sigma_hypercharge_audit_v20), so this point is
not an SM vacuum in any case.  Nothing is closed or excluded.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as candidate_source
import g3_candidate_physical_target_audit_v20 as target
import g3_physical_hierarchy_higgs_stability_v20 as stability
import g3_tuned_target_effective_higgs_quartic_v20 as quartic
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_TUNED_TARGET_PORTAL_THRESHOLD_V20.json"
OUT_MD = ROOT / "G3_TUNED_TARGET_PORTAL_THRESHOLD_V20.md"

PORTAL_ID = "lambda::O34_B01_Hdag_H_norm"
H_QUARTIC_ID = "lambda::O36_B02_H_self_quartics"
S_QUARTIC_ID = "lambda::O23_B01_singlet_polynomial"
PORTAL_SCAN = (0.5, 1.0, 2.0)
VALLEY_Y = (0.005, 0.01)
FORMULA_ATOL = 1.0e-9
ENERGY_ATOL = 1.0e-12
R = float(candidate_source.R)


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


def compiler_threshold(portal: float) -> dict[str, Any]:
    """lambda_eff from exact polynomial differences on the compiler."""
    coefficients = portal_coefficients(portal)
    q0 = chart.pack(target.gut_point_state())
    _, gradient, hessian = target.assemble(target.gut_point_rows(), coefficients)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    massive = np.abs(eigenvalues) > quartic.ZERO_MODE_ATOL
    base_rows = quartic._h_rows_at_tuned_point()
    parameter_ids = frozenset(base_rows)
    h_coefficients = {key: value for key, value in coefficients.items() if key in parameter_ids}
    _, g0, h0 = target.assemble(base_rows, h_coefficients)
    u = quartic.light_doublet_directions(hessian)[0]
    _, gp, hp = target.assemble(quartic._h_rows_at(q0 + u, parameter_ids), h_coefficients)
    _, gm, hm = target.assemble(quartic._h_rows_at(q0 - u, parameter_ids), h_coefficients)
    coupling = gp + gm - 2.0 * g0
    fourth = float(u @ (hp + hm - 2.0 * h0) @ u)
    components = eigenvectors[:, massive].T @ coupling
    shift = 3.0 * float(np.sum(components**2 / eigenvalues[massive]))
    lambda_h = coefficients[H_QUARTIC_ID]
    lambda_s = coefficients[S_QUARTIC_ID]
    formula = lambda_h - portal**2 / (4.0 * lambda_s)
    lambda_eff = (fourth - shift) / 6.0
    return {
        "lambda_HS": portal,
        "retuned_O06": coefficients[target.O06_ID],
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "negative_hessian_eigenvalues": int(np.sum(eigenvalues < -quartic.ZERO_MODE_ATOL)),
        "zero_modes": int(np.sum(~massive)),
        "coupling_S_block_norm": float(np.linalg.norm(coupling[chart.S_SLICE])),
        "lambda_direct": fourth / 6.0,
        "lambda_eff": lambda_eff,
        "lambda_eff_formula": formula,
        "formula_residual": abs(lambda_eff - formula),
    }


def _energy(state: potential.FieldState, coefficients: dict[str, float]) -> float:
    return potential.potential_value(potential.evaluate_directions(state), coefficients)


def _state(y: float, s_abs: float) -> potential.FieldState:
    base = target.gut_point_state()
    h = math.sqrt(y) * candidate_source.h_vector(chiral=True)
    return potential.FieldState(
        phi=base.phi, h=h, sigma=base.sigma, s=complex(s_abs), x=base.x
    ).validated()


def valley_audit(portal: float) -> dict[str, Any]:
    """Tree-level (H, S) block: analytic predictions against the compiler."""
    coefficients = portal_coefficients(portal)
    lambda_h = coefficients[H_QUARTIC_ID]
    lambda_s = coefficients[S_QUARTIC_ID]
    lambda_eff = lambda_h - portal**2 / (4.0 * lambda_s)
    v0 = _energy(target.gut_point_state(), coefficients)
    valley = []
    for y in VALLEY_Y:
        s2 = R * R - portal * y / (2.0 * lambda_s)
        observed = _energy(_state(y, math.sqrt(s2)), coefficients) - v0
        valley.append({"y": y, "S_abs_squared": s2, "delta_V": observed, "lambda_eff_y2": lambda_eff * y * y})
    y_star = portal * R * R / (2.0 * lambda_h)
    branch = _energy(_state(y_star, 0.0), coefficients) - v0
    return {
        "lambda_HS": portal,
        "lambda_eff": lambda_eff,
        "local_minimum_bound_lambda_HS_max": 2.0 * math.sqrt(lambda_h * lambda_s),
        "tuned_point_is_tree_level_local_minimum": lambda_eff >= 0.0,
        "V0": v0,
        "valley": valley,
        "valley_identity_max_residual": max(abs(row["delta_V"] - row["lambda_eff_y2"]) for row in valley),
        "S_zero_branch": {
            "H_norm_squared": y_star,
            "H_norm_over_Phi": math.sqrt(y_star),
            "delta_V": branch,
            "analytic": R**4 * lambda_s * lambda_eff / lambda_h,
            "lower_than_tuned_point": branch < -ENERGY_ATOL,
        },
    }


def build_report() -> dict[str, Any]:
    scan = [compiler_threshold(value) for value in PORTAL_SCAN]
    coefficients = quartic.tuned_coefficients()
    lambda_h = coefficients[H_QUARTIC_ID]
    lambda_s = coefficients[S_QUARTIC_ID]
    profile = stability.sm_profile(loops=2)
    lambda_target = float(profile.lam(stability.M_GUT_GEV))
    needed = 2.0 * math.sqrt(lambda_s * (lambda_h - lambda_target))
    matched = compiler_threshold(needed)
    stable_control = valley_audit(1.0)
    matched_valley = valley_audit(needed)
    points = scan + [matched]
    checks = {
        "every_point_is_stationary": all(p["gradient_max_abs"] < target.STATIONARITY_ATOL for p in points),
        "hessian_is_psd_at_every_point": all(p["negative_hessian_eigenvalues"] == 0 for p in points),
        "doublet_massless_after_O06_retune": all(p["zero_modes"] == 39 for p in points),
        "portal_couples_the_doublet_to_the_S_radial_mode": all(p["coupling_S_block_norm"] > 1.0e-3 for p in points),
        "compiler_matches_singlet_threshold_formula": all(p["formula_residual"] < FORMULA_ATOL for p in points),
        "compiler_confirms_valley_identity": max(
            stable_control["valley_identity_max_residual"], matched_valley["valley_identity_max_residual"]
        ) < ENERGY_ATOL,
        "compiler_confirms_S_zero_branch_energy": all(
            abs(audit["S_zero_branch"]["delta_V"] - audit["S_zero_branch"]["analytic"]) < ENERGY_ATOL
            for audit in (stable_control, matched_valley)
        ),
        "two_loop_sm_target_is_negative": lambda_target < 0.0,
        "no_gate_closed_or_model_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    outcomes = {
        "local_minimum_requires_lambda_HS_at_most": 2.0 * math.sqrt(lambda_h * lambda_s),
        "sm_matched_lambda_HS": needed,
        "sm_matched_point_is_tree_level_local_minimum": matched_valley["tuned_point_is_tree_level_local_minimum"],
        "sm_matched_point_has_lower_EW_breaking_PQ_restoring_configuration": matched_valley["S_zero_branch"][
            "lower_than_tuned_point"
        ],
        "stable_control_lambda_HS_1_has_no_lower_S_zero_branch": not stable_control["S_zero_branch"][
            "lower_than_tuned_point"
        ],
        "higgs_mass_tension_resolvable_by_tree_level_portal_at_a_local_minimum": False,
    }
    return {
        "model_contract_id": target.MODEL_CONTRACT_ID,
        "status": (
            "G3_PORTAL_THRESHOLD_EXACT__SM_MATCHED_PORTAL_MAKES_TUNED_POINT_A_SADDLE__G3_OPEN"
            if ok
            else "G3_TUNED_TARGET_PORTAL_THRESHOLD_AUDIT_FAILED"
        ),
        "overall_state": "CONSTRAINT" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scientific_outcomes": outcomes,
        "units": target.UNITS,
        "couplings": {
            "lambda_H": lambda_h,
            "lambda_S": lambda_s,
            "portal_parameter": PORTAL_ID,
            "normalization": "V > lambda_H (H^dag H)^2 + lambda_S |S|^4 + lambda_HS (H^dag H)|S|^2 (census; SARAH writes lambdaS/2 |S|^4)",
        },
        "formula": "lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S); local minimum iff lambda_eff >= 0",
        "scan": scan,
        "sm_matching": {
            "lambda_gut_required_two_loop": lambda_target,
            "source": "g3_physical_hierarchy_higgs_stability_v20 (two-loop SM running, Buttazzo et al. inputs)",
            "lambda_HS_required_at_benchmark_lambda_H_lambda_S": needed,
            "compiler_point": matched,
            "valley": matched_valley,
        },
        "stable_control": stable_control,
        "flags": {
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "tree_level_only": True,
            "certified_point_is_sm_vacuum": False,
        },
        "scope": (
            "Tree level at the r = 1/5 benchmark point with the certified Delta_R, which is not the SM singlet "
            "(g3_sigma_hypercharge_audit_v20). The two-loop SM target assumes SM running all the way to M_GUT."
        ),
        "verdict": (
            "The declared H-S portal gives the exact singlet threshold lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S), "
            "but the tuned point stays a tree-level local minimum only while lambda_eff >= 0 (lambda_HS <= 2 at the "
            f"benchmark). Matching the two-loop SM value lambda(M_GUT) = {lambda_target:.4f} needs lambda_HS = {needed:.4f}; "
            "the point is then a PSD but degenerate saddle that descends along the H-S valley to an electroweak-breaking, "
            "PQ-restoring configuration with S = 0. A tree-level portal threshold therefore cannot supply the negative "
            "matching quartic at a G3-admissible point. G3 stays open; nothing is excluded."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    matching = report["sm_matching"]
    valley = matching["valley"]
    lines = [
        "# H-S portal threshold at the tuned G3 point -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "| lambda_HS | retuned O06 | lambda_eff (compiler) | formula |",
        "|---|---|---|---|",
    ]
    for point in report["scan"] + [matching["compiler_point"]]:
        lines.append(
            f"| {point['lambda_HS']:.6g} | {point['retuned_O06']:.6g} | "
            f"{point['lambda_eff']:.10g} | {point['lambda_eff_formula']:.10g} |"
        )
    lines += [
        "",
        f"- local minimum requires lambda_HS <= `{report['scientific_outcomes']['local_minimum_requires_lambda_HS_at_most']:.6g}`;",
        f"- two-loop SM target lambda(M_GUT) = `{matching['lambda_gut_required_two_loop']:.5f}` needs lambda_HS = "
        f"`{matching['lambda_HS_required_at_benchmark_lambda_H_lambda_S']:.5f}`;",
        f"- at that coupling the S = 0 branch lies `{valley['S_zero_branch']['delta_V']:.3e}` M^4 below the tuned point "
        f"(analytic `{valley['S_zero_branch']['analytic']:.3e}`), at |H|/|Phi| = `{valley['S_zero_branch']['H_norm_over_Phi']:.3f}`;",
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
