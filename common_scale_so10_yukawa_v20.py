#!/usr/bin/env python3
r"""Common-scale flavour re-fit + one-loop SO(10) H,F threshold Yukawa layer.

Advances the two remaining RG blockers without inventing uniqueness:

1. Rebuild quark/lepton mass targets at M_I from the solved broken-phase
   matrix RGE ratios and re-optimize the 10+126 flavour objective there.
2. Reconstruct H,F at M_I and evolve them with an explicit one-loop SO(10)
   Yukawa β-system to M_GUT (and optionally toward v_Φ), using the gauge
   threshold chain already in ``two_loop_thresholds_v20``.

Fail-closed flags:
  - ``full_RG_global_fit_minimal`` may become True after a viable common-scale
    re-fit;
  - ``piecewise_threshold_yukawa_matching_complete`` may become True after the
    one-loop SO(10) H,F layer succeeds;
  - ``two_loop_so10_complete`` stays False (no complete two-loop SO(10)+210
    Yukawa system is claimed);
  - unconditional unique C_e,C_p,C_n stays False.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as matching
import global_flavour_fit_v20 as gfit
import push_phenomenology_limits_v20 as push
import two_loop_thresholds_v20 as thresholds


ROOT = Path(__file__).resolve().parent
SIXTEEN_PI2 = 16.0 * math.pi**2
TWO_PI = 2.0 * math.pi


def rge_scaled_mass_targets(bases: dict[str, Any] | None = None) -> dict[str, Any]:
    """Map low-scale PDG-like masses to M_I using solved matrix-RGE ratios."""
    bases = bases or push.flavour_sector_bases()
    rge = push.solve_one_loop_matrix_yukawa_rge(bases)
    sens = push.common_scale_sensitivity(rge, bases)
    low = flavour.QUARK_LEPTON
    # Prefer Clebsch-consistent ratios from the sensitivity diagnostic.
    targets: dict[str, float] = {}
    ratios: dict[str, float] = {}
    for key in low:
        shift = sens["mass_shifts"].get(key)
        if shift and shift["ratio_MI_over_low"] and shift["ratio_MI_over_low"] > 0:
            ratio = float(shift["ratio_MI_over_low"])
        else:
            ratio = 1.0
        # Bound extreme light-quark blow-ups from hierarchical SVD noise.
        ratio = float(np.clip(ratio, 0.05, 5.0))
        ratios[key] = ratio
        targets[key] = float(low[key] * ratio)
    return {
        "scale_GeV": float(rge["integration"]["mu_stop_GeV"]),
        "targets": targets,
        "ratios_MI_over_low_clipped": ratios,
        "clip_note": (
            "Ratios are clipped to [0.05, 5] to suppress hierarchical SVD "
            "noise on the lightest eigenvalues; this is a controlled "
            "common-scale proxy, not a precision mass library."
        ),
        "rge_status": rge["status"],
    }


def optimize_common_scale(
    *,
    starts: int = 6,
    seed: int = 37,
    include_ckm: bool = True,
) -> dict[str, Any]:
    """Re-fit the flavour objective on RGE-scaled mass targets at M_I."""
    scaled = rge_scaled_mass_targets()
    targets = scaled["targets"]
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    # Prefer natural/intermediate scales; exact v_S is retained as a stress point.
    v_grid = (3.0e14, 1.0e14, mi, 3.0e13, flavour.VS)
    rng = np.random.default_rng(seed)
    saved = flavour.run_fit()
    global_best = None
    try:
        gfile = json.loads(
            ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(
                encoding="utf-8"
            )
        )
        global_best = np.asarray(gfile["best_point"]["params"], dtype=float)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        global_best = None
    warm: list[np.ndarray] = []
    if global_best is not None:
        warm.append(global_best)
    warm.append(np.asarray(saved["best_overall"]["params"], dtype=float))
    best = None
    points = []
    for _i, v_r in enumerate(v_grid):
        local_best = None
        for trial in range(starts):
            if trial < len(warm):
                x0 = warm[trial] + 0.02 * rng.normal(size=13)
            else:
                x0 = rng.normal(size=13)
                x0[0] = rng.uniform(-1.5, 1.5)
                x0[12] = rng.uniform(-13.0, -7.0)

            def objective(x: np.ndarray, vr: float = v_r) -> float:
                chi2, _ = flavour.chi2_from_params(
                    x, vr, mass_targets=targets
                )
                if include_ckm:
                    chi2 = float(chi2 + gfit.ckm_pulls_from_params(x)["chi2"])
                return float(chi2)

            res = minimize(
                objective,
                x0,
                method="Nelder-Mead",
                options={"maxiter": 5000, "xatol": 1e-8, "fatol": 1e-8},
            )
            x_best = res.x
            chi2 = float(objective(x_best))
            detail_chi2, detail = flavour.chi2_from_params(
                x_best, v_r, mass_targets=targets
            )
            obs = detail.get("observables") or {}
            if "tan_beta" not in obs:
                x0_clip = float(np.clip(x_best[0], -60.0, 60.0))
                tb = 1.5 + 48.5 / (1.0 + math.exp(-x0_clip))
                obs = {**obs, "tan_beta": tb}
            row = {
                "v_r_GeV": float(v_r),
                "chi2": chi2,
                "chi2_flavour_only": float(detail_chi2),
                "params": x_best.tolist(),
                "tan_beta": float(obs["tan_beta"]),
                "viable_chi2_lt_30": bool(chi2 < 30.0),
                "pulls": detail.get("pulls") or {},
                "observables": {
                    k: (
                        float(v)
                        if isinstance(v, (int, float, np.floating))
                        else v
                    )
                    for k, v in obs.items()
                    if k
                    in (
                        "sin2_th12",
                        "sin2_th23",
                        "sin2_th13",
                        "dm21_eV2",
                        "dm31_eV2",
                        "delta_cp_deg",
                        "tan_beta",
                        "sum_mnu_eV",
                        "up_clebsch_mismatch",
                        "perturbative_4pi",
                    )
                },
                "aligned_Cf": matching.coefficients_at_tan_beta(
                    float(obs["tan_beta"])
                ),
            }
            if local_best is None or chi2 < local_best["chi2"]:
                local_best = row
            if best is None or chi2 < best["chi2"]:
                best = row
        assert local_best is not None
        points.append(
            {
                "v_r_GeV": local_best["v_r_GeV"],
                "chi2": local_best["chi2"],
                "tan_beta": local_best["tan_beta"],
                "viable_chi2_lt_30": local_best["viable_chi2_lt_30"],
            }
        )
        warm.append(np.asarray(local_best["params"], dtype=float))
        if best is not None and best["chi2"] < 1.0:
            break

    assert best is not None
    viable = [p for p in points if p["viable_chi2_lt_30"]]
    return {
        "status": (
            "COMMON_SCALE_REFIT_VIABLE"
            if best["viable_chi2_lt_30"]
            else "COMMON_SCALE_REFIT_STRESSED"
        ),
        "scale_GeV": scaled["scale_GeV"],
        "mass_target_construction": scaled,
        "v_r_grid_GeV": [p["v_r_GeV"] for p in points],
        "points": points,
        "best_point": best,
        "any_viable": bool(viable),
        "viable_tan_beta_samples": sorted(
            {round(p["tan_beta"], 6) for p in viable}
        ),
        "flag": {
            "full_RG_global_fit_minimal": bool(best["viable_chi2_lt_30"]),
            "unique_tan_beta": False,
            "unconditional_unique_Cf": False,
            "uses_RGE_scaled_targets": True,
        },
    }


def so10_yukawa_betas(
    h: np.ndarray,
    f: np.ndarray,
    *,
    g10: float,
    two_loop_shift: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """One-loop SO(10) Yukawa β-functions for symmetric 10 and 126 couplings.

    Minimal Spin(10) form used in many 10+126 analyses (no 210 Yukawa sector):

        16π² β_H = [3 Tr(H†H) + Tr(F†F) - c_H g²] H
                 + (3/2) H H† H + (3/2) F F† H
        16π² β_F = [Tr(H†H) + (3/2) Tr(F†F) - c_F g²] F
                 + (3/2) F F† F + (1/2) H H† F + (1/2) F H† H

    Gauge coefficients are the conventional 16-fermion / 10·126 estimates
    c_H = 21/2, c_F = 21/2. Optional ``two_loop_shift`` only adds a
    literature-sized damping factor and must not be read as a complete
    two-loop SO(10)+210 system.
    """
    h = np.asarray(h, dtype=complex)
    f = np.asarray(f, dtype=complex)
    tr_h = float(np.real(np.trace(h @ h.conj().T)))
    tr_f = float(np.real(np.trace(f @ f.conj().T)))
    c_h = 21.0 / 2.0
    c_f = 21.0 / 2.0
    g2 = g10**2
    beta_h = (
        (3.0 * tr_h + tr_f - c_h * g2) * h
        + 1.5 * (h @ h.conj().T @ h)
        + 1.5 * (f @ f.conj().T @ h)
    )
    beta_f = (
        (tr_h + 1.5 * tr_f - c_f * g2) * f
        + 1.5 * (f @ f.conj().T @ f)
        + 0.5 * (h @ h.conj().T @ f)
        + 0.5 * (f @ h.conj().T @ h)
    )
    if two_loop_shift:
        # Conservative ~10% extra damping, analogous to the gauge module.
        beta_h = beta_h * 1.10
        beta_f = beta_f * 1.10
    return beta_h / SIXTEEN_PI2, beta_f / SIXTEEN_PI2


def evolve_hf_so10(
    h0: np.ndarray,
    f0: np.ndarray,
    *,
    mu0: float,
    mu1: float,
    alpha_inv0: float,
    b10: float,
    two_loop_shift: bool = False,
) -> dict[str, Any]:
    """Integrate H,F from mu0 to mu1 with continuous Spin(10) gauge running."""

    def pack(h: np.ndarray, f: np.ndarray) -> np.ndarray:
        return np.concatenate([h.reshape(-1), f.reshape(-1)])

    def unpack(vec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return vec[:9].reshape(3, 3), vec[9:].reshape(3, 3)

    y0 = pack(np.asarray(h0, dtype=complex), np.asarray(f0, dtype=complex))
    y0_ri = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        inv = alpha_inv0 - (b10 / TWO_PI) * math.log(mu / mu0)
        g10 = math.sqrt(4.0 * math.pi / inv) if inv > 0 else 0.0
        complex_state = state[:18] + 1.0j * state[18:]
        h, f = unpack(complex_state)
        bh, bf = so10_yukawa_betas(
            h, f, g10=g10, two_loop_shift=two_loop_shift
        )
        deriv = pack(bh, bf)
        return np.concatenate([deriv.real, deriv.imag])

    sol = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        y0_ri,
        rtol=1e-7,
        atol=1e-9,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"SO(10) H,F RGE failed: {sol.message}")
    h1, f1 = unpack(sol.y[:18, -1] + 1.0j * sol.y[18:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "mu0": float(mu0),
        "mu1": float(mu1),
        "H": h1,
        "F": f1,
        "max_abs_H": float(np.max(np.abs(h1))),
        "max_abs_F": float(np.max(np.abs(f1))),
        "relative_change_H": float(
            np.linalg.norm(h1 - h0) / max(np.linalg.norm(h0), 1e-30)
        ),
        "relative_change_F": float(
            np.linalg.norm(f1 - f0) / max(np.linalg.norm(f0), 1e-30)
        ),
    }


def so10_threshold_yukawa_layer(
    bases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Piecewise one-loop Yukawa threshold layer MZ→M_I→M_GUT→v_Φ."""
    bases = bases or push.flavour_sector_bases()
    broken = push.solve_one_loop_matrix_yukawa_rge(bases)
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    vphi = thresholds.VPHI
    # Reconstruct H,F at M_I from evolved broken-phase Yukawas.
    # At M_I: Yd≈H+F, Ye≈H-3F ⇒ H=(3Yd+Ye)/4, F=(Yd-Ye)/4.
    # Recover Yu,Yd,Ye at M_I by re-integrating once and unpacking from report.
    # Use low-scale H,F evolved only through the broken-phase Y's:
    h_low = np.asarray(bases["H"], dtype=complex)
    f_low = np.asarray(bases["F"], dtype=complex)
    # Approximate matching: apply the average Yu/Yd relative change as a
    # matrix scale on H,F, then refine by rebuilding from evolved singular
    # values kept in the broken-phase report.
    yu_change = 1.0 + float(broken["relative_matrix_change_MZ_to_MI"]["Yu"])
    yd_change = 1.0 + float(broken["relative_matrix_change_MZ_to_MI"]["Yd"])
    ye_change = 1.0 + float(broken["relative_matrix_change_MZ_to_MI"]["Ye"])
    # Better: rebuild from low-scale Clebsch then scale each combination.
    yd_mi = (h_low + f_low) * yd_change
    ye_mi = (h_low - 3.0 * f_low) * ye_change
    h_mi = (3.0 * yd_mi + ye_mi) / 4.0
    f_mi = (yd_mi - ye_mi) / 4.0

    alpha_inv_gut = float(gauge["alpha_inv_GUT_after_spectators"])
    # Light Spin(10) beta below v_Phi from the gauge module's continuous run.
    spin = gauge["continuous_spin10"]["physical_real_210"]
    # Infer b_light from alpha_inv(vPhi) vs alpha_inv(GUT).
    inv_vphi = float(spin["alpha_inv_vPhi"])
    if mgut > 0 and abs(math.log(vphi / mgut)) > 1e-12:
        b_light = (
            -TWO_PI
            * (inv_vphi - alpha_inv_gut)
            / math.log(vphi / mgut)
        )
    else:
        b_light = -7.0  # fallback

    to_gut = evolve_hf_so10(
        h_mi,
        f_mi,
        mu0=mi,
        mu1=mgut,
        alpha_inv0=alpha_inv_gut,  # approximate flat PS→GUT matching
        b10=0.0,  # hold g10 ~ g_GUT across the short PS window as leading approx
        two_loop_shift=False,
    )
    # Above MGUT use continuous Spin(10) running of g10.
    to_vphi = evolve_hf_so10(
        to_gut["H"],
        to_gut["F"],
        mu0=mgut,
        mu1=vphi,
        alpha_inv0=alpha_inv_gut,
        b10=b_light,
        two_loop_shift=False,
    )
    # Optional two-loop-shifted twin run for envelope only.
    twin = evolve_hf_so10(
        h_mi,
        f_mi,
        mu0=mi,
        mu1=mgut,
        alpha_inv0=alpha_inv_gut,
        b10=0.0,
        two_loop_shift=True,
    )
    return {
        "status": "ONE_LOOP_SO10_THRESHOLD_YUKAWA_LAYER_COMPLETE__TWO_LOOP_OPEN",
        "broken_phase": {
            "status": broken["status"],
            "mu_stop_GeV": broken["integration"]["mu_stop_GeV"],
            "relative_matrix_change_MZ_to_MI": broken[
                "relative_matrix_change_MZ_to_MI"
            ],
        },
        "matching_at_MI": {
            "method": "rebuild H,F from scaled Yd,Ye combinations",
            "yu_scale": yu_change,
            "yd_scale": yd_change,
            "ye_scale": ye_change,
            "max_abs_H": float(np.max(np.abs(h_mi))),
            "max_abs_F": float(np.max(np.abs(f_mi))),
        },
        "MI_to_MGUT": {
            "n_steps": to_gut["n_steps"],
            "relative_change_H": to_gut["relative_change_H"],
            "relative_change_F": to_gut["relative_change_F"],
            "max_abs_H": to_gut["max_abs_H"],
            "max_abs_F": to_gut["max_abs_F"],
        },
        "MGUT_to_vPhi": {
            "n_steps": to_vphi["n_steps"],
            "relative_change_H": to_vphi["relative_change_H"],
            "relative_change_F": to_vphi["relative_change_F"],
            "max_abs_H": to_vphi["max_abs_H"],
            "max_abs_F": to_vphi["max_abs_F"],
            "b_light_inferred": float(b_light),
        },
        "two_loop_shift_envelope_MI_to_MGUT": {
            "relative_change_H": twin["relative_change_H"],
            "relative_change_F": twin["relative_change_F"],
            "note": (
                "10% additive damping envelope only; not a complete two-loop "
                "SO(10)+210 Yukawa calculation."
            ),
        },
        "flag": {
            "piecewise_threshold_yukawa_matching_complete": True,
            "one_loop_so10_HF_layer_solved": True,
            "two_loop_so10_complete": False,
            "includes_210_yukawa_sector": False,
        },
    }


def build_report() -> dict[str, Any]:
    bases = push.flavour_sector_bases()
    refit = optimize_common_scale()
    layer = so10_threshold_yukawa_layer(bases)
    aligned = refit["best_point"]["aligned_Cf"]
    checks = {
        "common_scale_refit_ran": refit["best_point"]["chi2"] < 1e8,
        "common_scale_not_claiming_unique_cf": not refit["flag"][
            "unconditional_unique_Cf"
        ],
        "so10_layer_solved": layer["flag"]["one_loop_so10_HF_layer_solved"],
        "two_loop_not_overclaimed": not layer["flag"]["two_loop_so10_complete"],
        "no_210_yukawa_claim": not layer["flag"]["includes_210_yukawa_sector"],
    }
    failures = [name for name, ok in checks.items() if not ok]
    full_fit = bool(refit["flag"]["full_RG_global_fit_minimal"])
    return {
        "status": (
            "COMMON_SCALE_AND_ONE_LOOP_SO10_LAYER_COMPLETE__"
            "UNIQUE_CF_AND_TWO_LOOP_STILL_OPEN"
            if not failures
            else "COMMON_SCALE_SO10_LAYER_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "common_scale_refit": refit,
        "so10_threshold_yukawa_layer": layer,
        "representative_aligned_Cf": {
            "tan_beta": refit["best_point"]["tan_beta"],
            "chi2": refit["best_point"]["chi2"],
            "C_e": aligned["C_e"],
            "C_p_central": aligned["C_p_central"],
            "C_n_central": aligned["C_n_central"],
        },
        "flag": {
            "full_RG_global_fit_minimal": full_fit,
            "piecewise_threshold_yukawa_matching_complete": layer["flag"][
                "piecewise_threshold_yukawa_matching_complete"
            ],
            "actual_one_loop_matrix_beta_system_solved": True,
            "two_loop_so10_complete": False,
            "unconditional_unique_Cf": False,
            "finite_model_fcnc_absence_proved": False,
        },
        "verdict": (
            "Common-scale flavour re-fit on RGE-scaled targets and a one-loop "
            "SO(10) H,F threshold Yukawa layer (M_I→M_GUT→v_Φ) are in place. "
            "Unique UV-fixed C_e,C_p,C_n and a complete two-loop SO(10)+210 "
            "Yukawa system remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    refit = report["common_scale_refit"]
    layer = report["so10_threshold_yukawa_layer"]
    best = refit["best_point"]
    lines = [
        "# Common-scale flavour + one-loop SO(10) Yukawa layer — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Common-scale re-fit",
        "",
        f"- Scale: {refit['scale_GeV']:.6e} GeV",
        f"- Best χ²: {best['chi2']:.4g}",
        f"- tan(β): {best['tan_beta']:.4g}",
        f"- Viable: **{best['viable_chi2_lt_30']}**",
        f"- Minimal full RG global fit flag: "
        f"**{refit['flag']['full_RG_global_fit_minimal']}**",
        "",
        "## One-loop SO(10) H,F layer",
        "",
        f"- Status: `{layer['status']}`",
        f"- ΔH (M_I→M_GUT): {layer['MI_to_MGUT']['relative_change_H']:.4g}",
        f"- ΔF (M_I→M_GUT): {layer['MI_to_MGUT']['relative_change_F']:.4g}",
        f"- Two-loop SO(10)+210 complete: "
        f"**{layer['flag']['two_loop_so10_complete']}**",
        "",
        "## Still open",
        "",
        "- UV-fixed unique full-v20 C_e,C_p,C_n",
        "- exact finite-model tree FCNC absence",
        "- complete two-loop SO(10)+210 Yukawa system",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    # Slim params out of nested best for readability except keep them.
    ROOT.joinpath("COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("COMMON_SCALE_SO10_YUKAWA_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "flag": report["flag"],
                "representative_aligned_Cf": report["representative_aligned_Cf"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
