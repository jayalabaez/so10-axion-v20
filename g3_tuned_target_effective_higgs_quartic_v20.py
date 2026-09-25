#!/usr/bin/env python3
"""Effective Higgs quartic at the tuned r = 1/5 G3 point (tree level).

``g3_candidate_physical_target_audit_v20`` shows that the certified G3 point
is not a physical vacuum.  Its tuned counterpart keeps
(Phi, Sigma, S, Phi17) = (F, r Delta_R, r, 1) with r = 1/5 and retunes only the
H mass coefficient O06 (-2 -> 0), so one doublet of the 10_H is exactly
massless at H = 0.  Near that point the light doublet h has, at tree level,

    V = lambda_eff (h^dag h)^2,
    lambda_eff = lambda_direct - (1/2) sum_a c_a^2 / m_a^2  (per real direction),

where lambda_direct is the pure-H quartic and c_a the trilinear coupling of
|h|^2 to heavy mode a.  Along a unit real chart direction u of the doublet the
exact polynomial identities

    c(u) = grad V(q0+u) + grad V(q0-u) - 2 grad V(q0),
    Q(u) = u.(Hess V(q0+u) + Hess V(q0-u) - 2 Hess V(q0)).u

give lambda_direct = Q/6 and lambda_eff = (Q - 3 c.M^+.c)/6.  All derivatives
come from the repository's live 51-parameter exact-X compiler on the 486-real
canonical chart.

Results (tree level, float64):
* The tuned point is stationary.  Its Hessian is positive semidefinite with 39
  zero modes: 33 broken SO(10) generators, the U(1)_X and PQ phases, and the
  four real components of the massless doublet.  The 12-dimensional unbroken
  group is SU(3)_c x SU(2)_L x U(1)_T3R, not the SM, because the certified
  Delta_R is the T3R = 0, Y = -1 component of the 126bar triplet
  (g3_sigma_hypercharge_audit_v20).
* c vanishes identically (the light-doublet projections of the O46 and O35
  couplings cancel), so lambda_eff = lambda_direct = 1 (from O36_B02).
* Because the doublet is exactly flat, the tuned point is a tree-level local
  minimum only if lambda_eff >= 0; this bounds every tree-level matching
  contribution (see g3_tuned_target_portal_threshold_v20).

Conditional running statement: IF this were an SM vacuum with pure SM running
below M_GUT, two-loop running (g3_physical_hierarchy_higgs_stability_v20)
would need lambda(M_GUT) ~ -0.015 for the measured Higgs mass, incompatible
with the local-minimality condition, and lambda_eff = 1 would give
m_h ~ 173 GeV.  Neither premise holds for this benchmark: its stabilizer is
not the SM, and its spectrum below M_GUT contains non-SM scalars with O(1)
couplings to |h|^2.  The manuscript's own RG anchor also uses a 2HDM and a
Pati-Salam stage.  Nothing is closed or excluded; G3 stays open.
"""
from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as candidate_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import g3_candidate_physical_target_audit_v20 as target
import g3_physical_hierarchy_higgs_stability_v20 as stability
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_TUNED_TARGET_EFFECTIVE_HIGGS_QUARTIC_V20.json"
OUT_MD = ROOT / "G3_TUNED_TARGET_EFFECTIVE_HIGGS_QUARTIC_V20.md"

MODEL_CONTRACT_ID = target.MODEL_CONTRACT_ID
ZERO_MODE_ATOL = 1.0e-9
COUPLING_ATOL = 1.0e-10
QUARTIC_ATOL = 1.0e-10
LIGHT_STATE_THRESHOLD = 1.0e-2
EXPECTED_GAUGE_ORBIT_RANK = 33
EXPECTED_SYMMETRY_ORBIT_RANK = 35
EXPECTED_LIGHT_DOUBLET_REAL_DIM = 4

M_H_OBSERVED_GEV = 125.20
BETA_SCAN = (1 / 20, 1 / 40, 1 / 80, 1 / 160)


def tuned_coefficients() -> dict[str, float]:
    coefficients = target.candidate_coefficients()
    coefficients[target.O06_ID] = target.o06_tuning_audit()["tuned_O06"]
    return coefficients


@lru_cache(maxsize=1)
def _h_rows_at_tuned_point() -> dict[str, Any]:
    return target.parameter_rows(
        target.gut_point_state(), include=target.involves_fields(target.H_FIELDS)
    )


@lru_cache(maxsize=1)
def tuned_point_hessian() -> dict[str, Any]:
    state = target.gut_point_state()
    _, gradient, hessian = target.assemble(target.gut_point_rows(), tuned_coefficients())
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    return {
        "state": state,
        "q": chart.pack(state),
        "gradient": gradient,
        "hessian": hessian,
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
    }


def symmetry_orbit(state: Any) -> tuple[np.ndarray, int]:
    gauge = chart.gauge_orbit_matrix(state)
    orbit = np.column_stack(
        (
            gauge,
            g2_audit.u1x_tangent(state),
            quotient_source._phase_tangent(state, quotient_source.PQ_CHARGES),
        )
    )
    gauge_rank = int(np.linalg.matrix_rank(gauge, tol=1.0e-10))
    return orbit, gauge_rank


def light_doublet_directions(hessian: np.ndarray) -> np.ndarray:
    """Unit real chart directions spanning the massless doublet (rows)."""
    matrix, _ = target.hermitian_h_mass_matrix(hessian)
    values, vectors = np.linalg.eigh(matrix[target.DOUBLET_BLOCK, target.DOUBLET_BLOCK])
    directions = []
    for value, vector in zip(values, vectors.T):
        if abs(value) > target.SPECTRUM_ATOL:
            continue
        h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
        h[target.DOUBLET_BLOCK] = vector
        for phase in (1.0, 1.0j):
            q = np.zeros(chart.TOTAL_DIM, dtype=float)
            q[chart.H_SLICE] = chart._pack_complex_interleaved(phase * h / math.sqrt(2.0))
            directions.append(q / np.linalg.norm(q))
    return np.asarray(directions)


def _block_weights(vectors: np.ndarray) -> dict[str, float]:
    blocks = {
        "Phi210": chart.PHI_SLICE,
        "H10": chart.H_SLICE,
        "Sigma126bar": chart.SIGMA_SLICE,
        "S": chart.S_SLICE,
        "Phi17": chart.X_SLICE,
    }
    total = float(np.sum(vectors**2))
    return {
        name: float(np.sum(vectors[block] ** 2)) / total
        for name, block in blocks.items()
        if float(np.sum(vectors[block] ** 2)) / total > 1.0e-3
    }


def hessian_audit() -> dict[str, Any]:
    data = tuned_point_hessian()
    eigenvalues = data["eigenvalues"]
    eigenvectors = data["eigenvectors"]
    hessian = data["hessian"]
    orbit, gauge_rank = symmetry_orbit(data["state"])
    singular_values = np.linalg.svd(orbit, compute_uv=False)
    orbit_rank = int(np.sum(singular_values > 1.0e-10 * singular_values[0]))
    light = light_doublet_directions(hessian)
    zero = eigenvectors[:, np.abs(eigenvalues) <= ZERO_MODE_ATOL]
    span = np.column_stack((orbit, light.T))
    coefficients = np.linalg.lstsq(span, zero, rcond=None)[0]
    matrix, _ = target.hermitian_h_mass_matrix(hessian)

    light_states = []
    massive = eigenvalues > ZERO_MODE_ATOL
    values = eigenvalues[massive & (eigenvalues < LIGHT_STATE_THRESHOLD)]
    for value in np.unique(np.round(values, 9)):
        members = np.abs(eigenvalues - value) <= 1.0e-8
        light_states.append(
            {
                "mass_squared": float(value),
                "real_multiplicity": int(np.sum(members)),
                "field_weights": _block_weights(eigenvectors[:, members]),
            }
        )
    return {
        "state": "(F, r Delta_R, H=0, r, 1) with O06 tuned to the massless-doublet value",
        "gradient_max_abs": float(np.max(np.abs(data["gradient"]))),
        "minimum_eigenvalue": float(eigenvalues[0]),
        "negative_eigenvalues_below_minus_1e_minus_9": int(np.sum(eigenvalues < -ZERO_MODE_ATOL)),
        "zero_modes": int(zero.shape[1]),
        "gauge_orbit_rank": gauge_rank,
        "symmetry_orbit_rank_gauge_plus_X_plus_PQ": orbit_rank,
        "light_doublet_real_dimension": int(light.shape[0]),
        "hessian_on_symmetry_orbit_max_abs": float(np.max(np.abs(hessian @ orbit))),
        "hessian_on_light_doublet_max_abs": float(np.max(np.abs(hessian @ light.T))),
        "zero_modes_outside_orbit_plus_light_doublet": float(
            np.max(np.abs(span @ coefficients - zero))
        ),
        "heavy_sector_zero_modes": int(zero.shape[1]) - int(light.shape[0]),
        "smallest_nonzero_eigenvalue": float(eigenvalues[massive][0]),
        "light_h_spectrum": target.sm_branch_spectrum(matrix),
        "light_non_goldstone_states_below_1e_minus_2": light_states,
    }


def _h_rows_at(q: np.ndarray, parameter_ids: frozenset[str]) -> dict[str, Any]:
    rows = target.parameter_rows(
        chart.unpack(q), include=target.involves_fields(target.H_FIELDS)
    )
    if frozenset(rows) != parameter_ids:
        raise AssertionError("H-involving parameter rows changed between states")
    return rows


def effective_quartic_audit() -> dict[str, Any]:
    """lambda_direct and lambda_eff along each light-doublet chart direction.

    Terms without H are identical at q0 and q0 +/- u, so only H-involving
    rows enter the exact polynomial differences.
    """
    data = tuned_point_hessian()
    q0 = data["q"]
    eigenvalues = data["eigenvalues"]
    eigenvectors = data["eigenvectors"]
    massive = np.abs(eigenvalues) > ZERO_MODE_ATOL
    heavy_vectors = eigenvectors[:, massive]
    heavy_values = eigenvalues[massive]
    zero_vectors = eigenvectors[:, ~massive]

    base_rows = _h_rows_at_tuned_point()
    parameter_ids = frozenset(base_rows)
    coefficients = {
        key: value for key, value in tuned_coefficients().items() if key in parameter_ids
    }
    _, g0, h0 = target.assemble(base_rows, coefficients)

    light = light_doublet_directions(data["hessian"])
    directions = {f"u{index}": vector for index, vector in enumerate(light)}
    directions["mixed_u0_u2"] = (light[0] + light[2]) / math.sqrt(2.0)
    rows_out: dict[str, Any] = {}
    for name, u in directions.items():
        plus = _h_rows_at(q0 + u, parameter_ids)
        minus = _h_rows_at(q0 - u, parameter_ids)
        _, gp, hp = target.assemble(plus, coefficients)
        _, gm, hm = target.assemble(minus, coefficients)
        coupling = gp + gm - 2.0 * g0
        quartic = float(u @ (hp + hm - 2.0 * h0) @ u)
        heavy_components = heavy_vectors.T @ coupling
        shift = 3.0 * float(np.sum(heavy_components**2 / heavy_values))
        per_parameter = {}
        for key, value in coefficients.items():
            term = {key: value}
            contribution = float(
                u
                @ (
                    target.assemble({key: plus[key]}, term)[2]
                    + target.assemble({key: minus[key]}, term)[2]
                    - 2.0 * target.assemble({key: base_rows[key]}, term)[2]
                )
                @ u
            )
            if abs(contribution) > QUARTIC_ATOL:
                per_parameter[key] = contribution / 6.0
        rows_out[name] = {
            "coupling_vector_norm": float(np.linalg.norm(coupling)),
            "coupling_heavy_projection_norm": float(np.linalg.norm(heavy_components)),
            "coupling_zero_mode_projection_norm": float(
                np.linalg.norm(zero_vectors.T @ coupling)
            ),
            "Q_fourth_derivative": quartic,
            "lambda_direct": quartic / 6.0,
            "heavy_exchange_shift": shift / 6.0,
            "lambda_eff": (quartic - shift) / 6.0,
            "lambda_direct_by_parameter": per_parameter,
        }
    lambdas = [row["lambda_eff"] for row in rows_out.values()]
    directs = [row["lambda_direct"] for row in rows_out.values()]
    return {
        "normalization": "V = lambda (h^dag h)^2 with canonically normalized h; lambda = Q/6 along a unit chart direction",
        "directions": rows_out,
        "max_coupling_vector_norm": max(row["coupling_vector_norm"] for row in rows_out.values()),
        "lambda_direct": float(np.mean(directs)),
        "lambda_eff": float(np.mean(lambdas)),
        "lambda_spread_over_directions": float(max(directs) - min(directs)),
        "lambda_eff_minus_direct": float(np.mean(lambdas) - np.mean(directs)),
    }


def lambda_at_top(lambda_gut: float, loops: int = 2) -> float:
    """lambda(M_t) from lambda(M_GUT): SM couplings run up, then down, at the same loop order."""
    high = stability.run_sm(stability.BUTTAZZO_INPUTS, stability.MT_REF, stability.M_GUT_GEV, loops=loops)
    high["lam"] = lambda_gut
    return float(stability.run_sm(high, stability.M_GUT_GEV, stability.MT_REF, loops=loops)["lam"])


def sm_running_audit(lambda_eff: float) -> dict[str, Any]:
    """Conditional two-loop statement: only meaningful for an SM vacuum with SM running below M_GUT."""
    floor = float(2 * candidate_source.BETA**2)
    predictions = {}
    for label, value in (
        ("certified_lambda_eff", lambda_eff),
        ("sufficient_BFB_floor_2beta2_boundary", floor),
        ("zero", 0.0),
    ):
        lam_top = lambda_at_top(value)
        predictions[label] = {"lambda_gut": value, "lambda_at_mt": lam_top, **stability.higgs_mass_estimates(lam_top)}
    required = float(stability.sm_profile(loops=2).lam(stability.M_GUT_GEV))
    return {
        "scheme": (
            "two-loop SM RGEs from g3_physical_hierarchy_higgs_stability_v20 (Buttazzo et al. 2013 inputs at "
            "M_t = 173.34 GeV), tree-level matching lambda(M_GUT) = lambda_eff"
        ),
        "M_GUT_GeV": stability.M_GUT_GEV,
        "predictions": predictions,
        "lambda_gut_required_for_sm_two_loop": required,
        "applicability": (
            "Only for an SM vacuum with pure SM running below M_GUT. Neither holds for the r = 1/5 benchmark: its "
            "stabilizer is SU(3) x SU(2)_L x U(1)_T3R, and its spectrum below M_GUT has non-SM scalars (m^2 ~ 2e-4 to "
            "5e-3 M^2) with O(1) couplings to |h|^2, whose one-loop logs shift lambda by O(0.1)."
        ),
    }


def beta_tradeoff_audit() -> dict[str, Any]:
    """beta sets the sufficient BFB bound on lambda_H and, for this Delta_R, the triplet partner mass."""
    t = float(candidate_source.SIGMA_SCALE)
    r = float(candidate_source.R)
    rows = []
    for beta in BETA_SCAN:
        floor = beta * beta / (4.0 * t)
        lam_top = lambda_at_top(floor)
        rows.append(
            {
                "beta": beta,
                "lambda_H_BFB_boundary": floor,
                "m_h_tree_GeV_at_boundary_two_loop": stability.higgs_mass_estimates(lam_top)["m_h_tree_GeV"],
                "partner_triplet_mass_over_M": math.sqrt(beta) * r,
            }
        )
    return {
        "BFB_certificate": (
            "lambda_H N_H^2 + t N_Sigma^2 - beta N_H N_Sigma >= 0 needs beta^2 < 4 t lambda_H (strict), t = 1/8; "
            "lambda_H = beta^2/(4t) is the boundary where the sufficient certificate stops proving BFB"
        ),
        "triplet_partner_note": "sqrt(beta) r M is a property of the T3R = 0 Delta_R configuration, not of an SM vacuum",
        "rows": rows,
        "lambda_H_boundary_is_2_beta_squared": all(
            abs(row["lambda_H_BFB_boundary"] - 2.0 * row["beta"] ** 2) < 1.0e-15 for row in rows
        ),
    }


def build_report() -> dict[str, Any]:
    hessian = hessian_audit()
    quartic = effective_quartic_audit()
    running = sm_running_audit(quartic["lambda_eff"])
    tradeoff = beta_tradeoff_audit()
    spectrum = hessian["light_h_spectrum"]
    beta_r2 = float(target.BETA_R2)
    checks = {
        "tuned_O06_is_zero": abs(tuned_coefficients()[target.O06_ID]) <= target.SPECTRUM_ATOL,
        "tuned_point_is_stationary": hessian["gradient_max_abs"] < target.STATIONARITY_ATOL,
        "tuned_hessian_is_positive_semidefinite": hessian["negative_eigenvalues_below_minus_1e_minus_9"] == 0,
        "gauge_orbit_rank_is_33": hessian["gauge_orbit_rank"] == EXPECTED_GAUGE_ORBIT_RANK,
        "symmetry_orbit_rank_is_35": (
            hessian["symmetry_orbit_rank_gauge_plus_X_plus_PQ"] == EXPECTED_SYMMETRY_ORBIT_RANK
        ),
        "hessian_annihilates_orbit_and_light_doublet": (
            hessian["hessian_on_symmetry_orbit_max_abs"] < 1.0e-10
            and hessian["hessian_on_light_doublet_max_abs"] < 1.0e-10
        ),
        "zero_modes_are_goldstones_plus_massless_doublet": (
            hessian["zero_modes"] == EXPECTED_SYMMETRY_ORBIT_RANK + EXPECTED_LIGHT_DOUBLET_REAL_DIM
            and hessian["light_doublet_real_dimension"] == EXPECTED_LIGHT_DOUBLET_REAL_DIM
            and hessian["zero_modes_outside_orbit_plus_light_doublet"] < 1.0e-9
        ),
        "light_h_spectrum_is_massless_doublet_and_beta_r2_triplet": (
            target._close(target._values(spectrum["weak_doublets"]), [0.0, 1.2])
            and target._close(
                target._values(spectrum["colour_triplets"]), [beta_r2, 1.2 - beta_r2]
            )
        ),
        "light_doublet_has_no_heavy_mode_coupling": quartic["max_coupling_vector_norm"] < COUPLING_ATOL,
        "quartic_is_su2_x_u1_invariant_on_the_doublet": (
            quartic["lambda_spread_over_directions"] < QUARTIC_ATOL
        ),
        "lambda_eff_equals_lambda_direct": abs(quartic["lambda_eff_minus_direct"]) < QUARTIC_ATOL,
        "two_loop_sm_target_is_negative": running["lambda_gut_required_for_sm_two_loop"] < 0,
        "no_gate_closed_or_model_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    required = running["lambda_gut_required_for_sm_two_loop"]
    outcomes = {
        "lambda_eff_at_certified_couplings": quartic["lambda_eff"],
        "tree_level_local_minimum_requires_lambda_eff_nonnegative": True,
        "sm_matching_would_require_negative_lambda_eff_two_loop": ok and required < 0,
        "if_sm_vacuum_certified_couplings_m_h_two_loop_GeV": running["predictions"]["certified_lambda_eff"]["m_h_tree_GeV"],
        "if_sm_vacuum_lambda_eff_zero_m_h_two_loop_GeV": running["predictions"]["zero"]["m_h_tree_GeV"],
        "conclusions_conditional_on_sm_vacuum_and_sm_running": True,
        "certified_point_is_sm_vacuum": False,
        "light_doublet_projection_of_heavy_couplings_vanishes": ok,
    }
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": (
            "G3_TUNED_POINT_LAMBDA_EFF_EQUALS_DIRECT_H_QUARTIC__LOCAL_MINIMALITY_NEEDS_LAMBDA_EFF_NONNEGATIVE__G3_OPEN"
            if ok
            else "G3_TUNED_TARGET_HIGGS_QUARTIC_AUDIT_FAILED"
        ),
        "overall_state": "TREE_LEVEL_STRUCTURE_AUDITED" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scientific_outcomes": outcomes,
        "units": target.UNITS,
        "tuned_point_hessian": hessian,
        "effective_quartic": quartic,
        "sm_running": running,
        "beta_tradeoff": tradeoff,
        "flags": {
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "tree_level_only": True,
            "benchmark_hierarchy_r_one_fifth": True,
        },
        "scope": (
            "The r = 1/5 benchmark point with the certified Delta_R, which is not the SM singlet of the 126bar "
            "(g3_sigma_hypercharge_audit_v20). The two-loop running statement is conditional on an SM vacuum "
            "with pure SM running below M_GUT; the manuscript's RG anchor uses a 2HDM and a Pati-Salam stage."
        ),
        "verdict": (
            "At the r = 1/5 tuned point the light doublet has no tree-level coupling to heavy modes, so lambda_eff "
            f"equals the direct H quartic, {quartic['lambda_eff']:.6g}. The Hessian is PSD with 39 zero modes (33 broken "
            "SO(10) generators, U(1)_X, PQ and the doublet); the unbroken group is SU(3) x SU(2)_L x U(1)_T3R, not the "
            "SM, because the certified Delta_R carries hypercharge. Since the doublet is exactly flat, local "
            "minimality at tree level requires lambda_eff >= 0. If this were an SM vacuum with pure SM running below "
            f"M_GUT, two-loop running would need lambda(M_GUT) = {required:.4f} for the measured Higgs mass, which "
            "that condition forbids, and lambda_eff = 1 would give m_h ~ "
            f"{running['predictions']['certified_lambda_eff']['m_h_tree_GeV']:.0f} GeV; neither premise holds for "
            "this benchmark. G3 stays open; nothing is excluded."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    running = report["sm_running"]
    hessian = report["tuned_point_hessian"]
    predictions = running["predictions"]
    return "\n".join(
        [
            "# Effective Higgs quartic at the tuned r = 1/5 G3 point -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- tuned-point Hessian: PSD, {hessian['zero_modes']} zero modes "
            f"({hessian['symmetry_orbit_rank_gauge_plus_X_plus_PQ']} symmetry + "
            f"{hessian['light_doublet_real_dimension']} light doublet); unbroken group SU(3) x SU(2)_L x U(1)_T3R;",
            f"- lambda_eff = lambda_direct = `{report['effective_quartic']['lambda_eff']:.12g}`;",
            "- conditional two-loop statement (SM vacuum, SM running below M_GUT): "
            f"certified `{predictions['certified_lambda_eff']['m_h_tree_GeV']:.1f}` GeV, lambda = 0 "
            f"`{predictions['zero']['m_h_tree_GeV']:.1f}` GeV (tree-level m_h); SM needs lambda(M_GUT) = "
            f"`{running['lambda_gut_required_for_sm_two_loop']:.4f}`;",
            "- G3: `OPEN`; whole model: neither validated nor excluded.",
            "",
        ]
    )


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
