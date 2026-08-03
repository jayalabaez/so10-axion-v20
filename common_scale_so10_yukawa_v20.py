#!/usr/bin/env python3
r"""Fail-closed common-scale and SO(10)-style Yukawa sensitivity layer.

Clipped singular-value ratios, approximate matching, and a GUT-coupling ansatz
through the broken Pati-Salam interval are retained only as diagnostics. They
do not establish a precision common-scale fit or threshold/RG closure.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as matching
import push_phenomenology_limits_v20 as push
import two_loop_thresholds_v20 as thresholds

ROOT = Path(__file__).resolve().parent
SIXTEEN_PI2 = 16.0 * math.pi**2
TWO_PI = 2.0 * math.pi


def rge_scaled_mass_targets(bases: dict[str, Any] | None = None) -> dict[str, Any]:
    bases = bases or push.flavour_sector_bases()
    rge = push.solve_one_loop_matrix_yukawa_rge(bases)
    sensitivity = push.common_scale_sensitivity(rge, bases)
    targets, ratios, clipped = {}, {}, []
    for key, low_value in flavour.QUARK_LEPTON.items():
        raw = float(sensitivity["mass_shifts"].get(key, {}).get("ratio_MI_over_low", 1.0))
        bounded = float(np.clip(raw, 0.05, 5.0))
        if raw != bounded:
            clipped.append(key)
        ratios[key] = bounded
        targets[key] = float(low_value * bounded)
    return {
        "status": "CLIPPED_DIAGNOSTIC_TARGETS__PRECISION_COMMON_SCALE_OPEN",
        "scale_GeV": float(rge["integration"]["mu_stop_GeV"]),
        "targets": targets, "ratios_MI_over_low_clipped": ratios,
        "clipped_channels": clipped,
        "clip_note": "Clipping and diagnostic singular-value ratios prevent these targets from serving as a precision common-scale data set.",
        "rge_status": rge["status"],
        "flag": {"diagnostic_targets_constructed": True,
                 "precision_common_scale_targets": False,
                 "validated_one_loop_matrix_rge": False},
    }


def optimize_common_scale(*, starts: int = 6, seed: int = 37,
                          include_ckm: bool = True) -> dict[str, Any]:
    _ = (starts, seed, include_ckm)
    scaled = rge_scaled_mass_targets()
    global_fit = json.loads((ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(encoding="utf-8"))
    raw_best = global_fit["best_point"]
    tan_beta, chi2 = float(raw_best["tan_beta"]), float(raw_best["chi2"])
    best = {"v_r_GeV": float(raw_best["v_r_GeV"]), "chi2": chi2,
            "chi2_flavour_only": chi2, "params": raw_best.get("params", []),
            "tan_beta": tan_beta,
            "viable_chi2_lt_30": bool(raw_best.get("viable_chi2_lt_30", chi2 < 30.0)),
            "pulls": raw_best.get("pulls", {}), "observables": raw_best.get("observables", {}),
            "aligned_Cf": matching.coefficients_at_tan_beta(tan_beta)}
    viable_tans = [float(x) for x in global_fit.get("viable_tan_beta_samples", [])] or [tan_beta]
    points = []
    for row in global_fit.get("viable_points", []):
        if row.get("v_r_GeV") is not None:
            points.append({"v_r_GeV": float(row["v_r_GeV"]), "chi2": float(row["chi2"]),
                           "tan_beta": float(row["tan_beta"]),
                           "viable_chi2_lt_30": bool(row.get("viable_chi2_lt_30", False))})
    return {
        "status": "COMMON_SCALE_PROXY_WITNESS__PRECISION_REFIT_OPEN",
        "scale_GeV": scaled["scale_GeV"], "mass_target_construction": scaled,
        "v_r_grid_GeV": [row["v_r_GeV"] for row in points], "points": points,
        "best_point": best, "any_viable": bool(global_fit.get("any_viable", best["viable_chi2_lt_30"])),
        "viable_tan_beta_samples": viable_tans,
        "flag": {"proxy_witness_available": True, "full_RG_global_fit_minimal": False,
                 "precision_common_scale_refit": False, "global_minimum_proved": False,
                 "unique_tan_beta": False, "unconditional_unique_Cf": False,
                 "uses_RGE_scaled_targets": False},
    }


def so10_yukawa_betas(h: np.ndarray, f: np.ndarray, *, g10: float,
                      two_loop_shift: bool = False) -> tuple[np.ndarray, np.ndarray]:
    h, f = np.asarray(h, dtype=complex), np.asarray(f, dtype=complex)
    tr_h = float(np.real(np.trace(h @ h.conj().T)))
    tr_f = float(np.real(np.trace(f @ f.conj().T)))
    g2 = g10**2
    beta_h = ((3.0 * tr_h + tr_f - 10.5 * g2) * h
              + 1.5 * h @ h.conj().T @ h + 1.5 * f @ f.conj().T @ h)
    beta_f = ((tr_h + 1.5 * tr_f - 10.5 * g2) * f
              + 1.5 * f @ f.conj().T @ f
              + 0.5 * h @ h.conj().T @ f + 0.5 * f @ h.conj().T @ h)
    if two_loop_shift:
        beta_h *= 1.10; beta_f *= 1.10
    return beta_h / SIXTEEN_PI2, beta_f / SIXTEEN_PI2


def evolve_hf_so10(h0: np.ndarray, f0: np.ndarray, *, mu0: float, mu1: float,
                    alpha_inv0: float, b10: float,
                    two_loop_shift: bool = False) -> dict[str, Any]:
    h0, f0 = np.asarray(h0, dtype=complex), np.asarray(f0, dtype=complex)
    def pack(h, f): return np.concatenate([h.reshape(-1), f.reshape(-1)])
    def unpack(v): return v[:9].reshape(3,3), v[9:].reshape(3,3)
    y0 = pack(h0, f0); state0 = np.concatenate([y0.real, y0.imag])
    def rhs(log_mu, state):
        mu = math.exp(log_mu); inv = alpha_inv0 - b10 / TWO_PI * math.log(mu / mu0)
        if inv <= 0: raise RuntimeError("diagnostic gauge coupling reached a pole")
        h, f = unpack(state[:18] + 1j * state[18:])
        bh, bf = so10_yukawa_betas(h, f, g10=math.sqrt(4.0 * math.pi / inv),
                                   two_loop_shift=two_loop_shift)
        d = pack(bh, bf); return np.concatenate([d.real, d.imag])
    sol = solve_ivp(rhs, (math.log(mu0), math.log(mu1)), state0,
                    rtol=1e-7, atol=1e-9, method="RK45")
    if not sol.success: raise RuntimeError(f"SO(10)-style diagnostic ODE failed: {sol.message}")
    h1, f1 = unpack(sol.y[:18,-1] + 1j * sol.y[18:,-1])
    return {"success": True, "n_steps": int(sol.y.shape[1]), "mu0": float(mu0), "mu1": float(mu1),
            "H": h1, "F": f1, "max_abs_H": float(np.max(np.abs(h1))),
            "max_abs_F": float(np.max(np.abs(f1))),
            "relative_change_H": float(np.linalg.norm(h1-h0)/max(np.linalg.norm(h0),1e-30)),
            "relative_change_F": float(np.linalg.norm(f1-f0)/max(np.linalg.norm(f0),1e-30))}


def so10_threshold_yukawa_layer(bases: dict[str, Any] | None = None) -> dict[str, Any]:
    bases = bases or push.flavour_sector_bases()
    broken = push.solve_one_loop_matrix_yukawa_rge(bases)
    gauge = thresholds.solve_unification(two_loop=True)
    mi, mgut = float(gauge["M_I_GeV"]), float(gauge["M_GUT_GeV"])
    alpha_inv_gut = float(gauge["alpha_inv_GUT_after_spectators"])
    envelope = evolve_hf_so10(np.asarray(bases["H"], dtype=complex),
                              np.asarray(bases["F"], dtype=complex),
                              mu0=mi, mu1=mgut, alpha_inv0=alpha_inv_gut,
                              b10=0.0, two_loop_shift=False)
    return {
        "status": "SO10_STYLE_ENVELOPE_ONLY__PATI_SALAM_MATCHING_OPEN",
        "broken_phase": {"status": broken["status"], "mu_stop_GeV": broken["integration"]["mu_stop_GeV"],
                         "relative_matrix_change_MZ_to_MI": broken["relative_matrix_change_MZ_to_MI"]},
        "matching_at_MI": {"method": "not performed", "pati_salam_decomposition_included": False,
                           "exact_matching_matrices_included": False},
        "MI_to_MGUT_diagnostic": {"n_steps": envelope["n_steps"],
                                  "relative_change_H": envelope["relative_change_H"],
                                  "relative_change_F": envelope["relative_change_F"],
                                  "max_abs_H": envelope["max_abs_H"], "max_abs_F": envelope["max_abs_F"],
                                  "uses_GUT_coupling_across_broken_interval": True},
        "flag": {"diagnostic_so10_HF_envelope_integrated": True,
                 "one_loop_so10_HF_layer_solved": False,
                 "piecewise_threshold_yukawa_matching_complete": False,
                 "full_RG_global_fit_minimal": False, "two_loop_so10_complete": False,
                 "includes_210_yukawa_sector": False},
    }


def build_report() -> dict[str, Any]:
    bases = push.flavour_sector_bases(); witness = optimize_common_scale()
    layer = so10_threshold_yukawa_layer(bases); aligned = witness["best_point"]["aligned_Cf"]
    checks = {"proxy_witness_available": witness["flag"]["proxy_witness_available"],
              "precision_fit_not_overclaimed": not witness["flag"]["full_RG_global_fit_minimal"],
              "threshold_matching_not_overclaimed": not layer["flag"]["piecewise_threshold_yukawa_matching_complete"],
              "two_loop_not_overclaimed": not layer["flag"]["two_loop_so10_complete"],
              "unique_cf_not_overclaimed": not witness["flag"]["unconditional_unique_Cf"]}
    failures = [n for n, ok in checks.items() if not ok]
    return {"status": "COMMON_SCALE_AND_SO10_DIAGNOSTICS_PASS__PRECISION_RG_OPEN" if not failures else "COMMON_SCALE_DIAGNOSTIC_AUDIT_FAILED",
            "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
            "common_scale_refit": witness, "so10_threshold_yukawa_layer": layer,
            "representative_aligned_Cf": {"tan_beta": witness["best_point"]["tan_beta"],
                "chi2": witness["best_point"]["chi2"], "C_e": aligned["C_e"],
                "C_p_central": aligned["C_p_central"], "C_n_central": aligned["C_n_central"]},
            "flag": {"full_RG_global_fit_minimal": False,
                     "piecewise_threshold_yukawa_matching_complete": False,
                     "actual_one_loop_matrix_beta_system_solved": False,
                     "diagnostic_matrix_ODE_integrated": True,
                     "two_loop_so10_complete": False, "unconditional_unique_Cf": False,
                     "finite_model_fcnc_absence_proved": False},
            "verdict": "A diagnostic common-scale witness and SO(10)-style evolution envelope exist. Clipped targets, unvalidated matrix coefficients, and absent Pati-Salam matching prevent RG or threshold closure."}


def write_markdown(report):
    return "\n".join(["# Common-scale and SO(10) Yukawa audit — v20", "",
                      f"**Status:** `{report['status']}`", "", "- Diagnostic free-v_R witness retained.",
                      "- Precision common-scale re-fit: open.", "- Pati-Salam matching: open.",
                      "- Validated one-loop matrix RGE: open.", "- Two-loop SO(10)+210 system: open.",
                      "", report["verdict"], ""])


def main():
    report = build_report()
    ROOT.joinpath("COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    ROOT.joinpath("COMMON_SCALE_SO10_YUKAWA_V20.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "n_failed": report["n_failed"],
                      "flag": report["flag"], "representative_aligned_Cf": report["representative_aligned_Cf"],
                      "verdict": report["verdict"]}, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
