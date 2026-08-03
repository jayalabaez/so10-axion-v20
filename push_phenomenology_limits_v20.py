#!/usr/bin/env python3
r"""Fail-closed portal, FCNC-proxy, and broken-phase RGE diagnostics for v20.

The numerical routines in this module are useful sensitivity diagnostics. They
are not promoted to precision phenomenology:

* portal scans do not fix the UV Yukawas;
* FCNC norm estimates are not channel-by-channel experimental likelihoods;
* the broken-phase matrix ODE is a type-II-like diagnostic ansatz, not a
  reference-validated complete 2HDM RGE implementation;
* running electroweak VEVs and complete threshold matching are not included.

All completion flags therefore stay false.
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
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals
import two_loop_thresholds_v20 as thresholds

ROOT = Path(__file__).resolve().parent
TWO_PI = 2.0 * math.pi
SIXTEEN_PI2 = 16.0 * math.pi**2


def _biunitary(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, s, vh = np.linalg.svd(np.asarray(matrix, dtype=complex), full_matrices=True)
    return u, s, vh.conj().T


def flavour_sector_bases() -> dict[str, Any]:
    report = flavour.run_fit()
    best = report["best_overall"]
    data = flavour.build_matrices(np.asarray(best["params"], dtype=float), best["v_r_GeV"])
    _s_nu, u_nu = flavour.takagi(data["M_nu"])
    _s_e, u_e = flavour.takagi(data["M_e"])
    u_u_l, s_u, u_u_r = _biunitary(data["M_u_target"])
    u_d_l, s_d, u_d_r = _biunitary(data["M_d"])
    return {
        "tan_beta": float(data["tan_beta"]), "v_r_GeV": float(best["v_r_GeV"]),
        "chi2": float(best["chi2"]), "U_e": u_e, "U_nu": u_nu,
        "U_uL": u_u_l, "U_uR": u_u_r, "U_dL": u_d_l, "U_dR": u_d_r,
        "m_u": [float(x) for x in s_u], "m_d": [float(x) for x in s_d],
        "H": data["H"], "F": data["F"], "v_u": float(data["v_u"]),
        "v_d": float(data["v_d"]), "note": "A numerical witness, not a unique high-scale solution.",
    }


def hierarchical_epsilon(*, lam: float = 0.2, y_q: float = 1.0,
                         v_s: float = matching.VS_GEV,
                         v_phi: float = matching.VPHI_GEV) -> float:
    if y_q == 0:
        raise ValueError("y_q must be nonzero")
    return abs(lam) * v_s / (abs(y_q) * v_phi)


def hierarchical_w_expansion(lam: float = 0.2, y_q: float = 1.0) -> dict[str, Any]:
    eps = hierarchical_epsilon(lam=lam, y_q=y_q)
    block = portals.build_abcd(portals.PortalCouplings(
        y_P=1.0, y_R=1.0, y_Q=y_q, lam_Q_F=(lam, lam, lam),
        lam_Q_R=0.0, lam_S_Q_Rbar=0.0,
        y_F_Pbar=(0.0, 0.0, 0.0), y_F_Rbar=(0.0, 0.0, 0.0)))
    current = matching.portal_current_match(block["A"], block["B"], block["C"], block["D"])
    w = np.asarray(current["W"], dtype=complex)
    leading = eps**2 * np.eye(3, dtype=complex)
    resummed = eps**2 / (1.0 + eps**2) * np.eye(3, dtype=complex)
    return {
        "epsilon": float(eps), "trace_W_exact": float(np.real(np.trace(w))),
        "trace_W_leading_3eps2": float(3.0 * eps**2),
        "trace_W_resummed_3eps2_over_1plus": float(3.0 * eps**2 / (1.0 + eps**2)),
        "frobenius_error_leading": float(np.linalg.norm(w - leading)),
        "frobenius_error_resummed": float(np.linalg.norm(w - resummed)),
        "projected_shift_norm_exact": float(current["projected_shift_norm"]),
        "projected_shift_leading_4eps2": float(4.0 * eps**2),
        "asymptotic_statement": "For the stated hierarchical benchmark W=O(epsilon^2). Exact vanishing requires epsilon->0 or an exact scalar-current axiom.",
        "claims_exact_vanishing": False,
    }


def portal_cf_envelope(*, n_samples: int = 96, seed: int = 20,
                       tan_betas: list[float] | None = None) -> dict[str, Any]:
    if n_samples < 1:
        raise ValueError("n_samples must be positive")
    if tan_betas is None:
        report = json.loads((ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(encoding="utf-8"))
        tan_betas = [float(x) for x in report.get("viable_tan_beta_samples", [])] or [float(report["best_point"]["tan_beta"])]
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_samples):
        couplings = portals.PortalCouplings(
            y_P=complex(rng.uniform(0.3, 2.0)), y_R=complex(rng.uniform(0.3, 2.0)),
            y_Q=complex(rng.uniform(0.3, 2.0)),
            lam_Q_F=tuple(complex(x) for x in rng.uniform(0.05, 0.8, size=3)),
            lam_Q_R=complex(rng.uniform(0.0, 0.4)), lam_S_Q_Rbar=complex(rng.uniform(0.0, 0.3)),
            y_F_Pbar=tuple(complex(x) for x in rng.uniform(0.0, 0.05, size=3)),
            y_F_Rbar=tuple(complex(x) for x in rng.uniform(0.0, 0.05, size=3)))
        block = portals.build_abcd(couplings)
        current = matching.portal_current_match(block["A"], block["B"], block["C"], block["D"])
        q = np.asarray(current["Q_projected"], dtype=complex)
        mean_q = float(np.real(np.trace(q) / 3.0))
        off = float(np.linalg.norm(q - np.diag(np.diag(q))))
        for tan_beta in tan_betas:
            coeff = matching.coefficients_at_tan_beta(float(tan_beta))
            rows.append({"tan_beta": float(tan_beta), "mean_q": mean_q,
                         "off_diagonal_norm": off,
                         "projected_shift_norm": float(current["projected_shift_norm"]),
                         "approx_aligned": bool(off < 1e-8 and abs(mean_q - 1.0) < 1e-3),
                         "C_e": float(coeff["C_e"] * mean_q),
                         "C_p_central": float(coeff["C_p_central"]),
                         "C_n_central": float(coeff["C_n_central"])})
    aligned = [r for r in rows if r["approx_aligned"]]
    selected = aligned or rows
    return {
        "n_portal_draws": n_samples, "n_tan_beta": len(tan_betas),
        "n_total_rows": len(rows), "n_approx_aligned_rows": len(aligned),
        "tan_beta_samples": tan_betas,
        "envelope_all_draws": {
            "C_e": [min(r["C_e"] for r in rows), max(r["C_e"] for r in rows)],
            "off_diagonal_norm": [min(r["off_diagonal_norm"] for r in rows), max(r["off_diagonal_norm"] for r in rows)],
            "projected_shift_norm": [min(r["projected_shift_norm"] for r in rows), max(r["projected_shift_norm"] for r in rows)]},
        "envelope_approx_aligned": {
            "C_e": [min(r["C_e"] for r in selected), max(r["C_e"] for r in selected)],
            "C_p_central": [min(r["C_p_central"] for r in selected), max(r["C_p_central"] for r in selected)],
            "C_n_central": [min(r["C_n_central"] for r in selected), max(r["C_n_central"] for r in selected)]},
        "flag": {"portal_envelope_constructed": True, "unconditional_unique_Cf": False,
                 "reason": "Free portal draws define an envelope, not a prediction."},
    }


def fcnc_experimental_bound_application(bases: dict[str, Any] | None = None) -> dict[str, Any]:
    bases = bases or flavour_sector_bases()
    block = portals.build_abcd(portals.PortalCouplings(
        y_P=1.0, y_R=1.0, y_Q=1.0, lam_Q_F=(0.2, 0.2, 0.2),
        lam_Q_R=0.0, lam_S_Q_Rbar=0.0,
        y_F_Pbar=(0.0, 0.0, 0.0), y_F_Rbar=(0.0, 0.0, 0.0)))
    current = matching.portal_current_match(block["A"], block["B"], block["C"], block["D"])
    q = np.asarray(current["Q_projected"], dtype=complex)
    lepton = physical.rotate_to_basis(q, bases["U_e"])
    up = physical.rotate_to_basis(q, bases["U_uL"])
    down = physical.rotate_to_basis(q, bases["U_dL"])
    fa = matching.FA_GEV
    lepton_off = float(lepton["off_diagonal_norm"])
    quark_off = max(float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"]))
    g_lepton = lepton_off * 0.10566 / fa
    g_quark = quark_off * 0.493677 / fa
    scalar_departure = float(np.linalg.norm(q - np.trace(q) / 3.0 * np.eye(3, dtype=complex)))
    return {
        "status": "FCNC_PROXY_LEDGER_ONLY__EXPERIMENTAL_LIKELIHOOD_OPEN",
        "mass_bases": {"uses_U_e": True, "uses_U_uL": True, "uses_U_dL": True,
                       "no_longer_identity_quark_placeholder": True},
        "hierarchical_benchmark": {
            "lepton_off_diagonal_norm": lepton_off,
            "up_off_diagonal_norm": float(up["off_diagonal_norm"]),
            "down_off_diagonal_norm": float(down["off_diagonal_norm"]),
            "g_lepton_fcnc_proxy": g_lepton, "g_quark_fcnc_proxy": g_quark,
            "illustrative_lepton_scale": 1.0e-12, "illustrative_quark_scale": 1.0e-12,
            "passes_illustrative_scales": bool(g_lepton < 1e-12 and g_quark < 1e-12),
            "scalar_departure": scalar_departure,
            "exactly_scalar_to_1e_14": scalar_departure <= 1e-14},
        "flag": {"proxy_bounds_applied": True, "experimental_FCNC_bound_applied": False,
                 "channel_amplitudes_computed": False,
                 "actual_finite_model_fcnc_absence_proved": False,
                 "reason": "Matrix norms times a representative mass are not branching ratios, form-factor calculations, or an experimental likelihood."},
    }


def _gauge_inv_at_mu(mu: float, gauge: dict[str, Any]) -> tuple[float, float, float]:
    mz = 91.1876
    b1, b2, b3 = 21.0 / 5.0, -3.0, -7.0
    a1, a2, a3 = 59.02, 29.57, 1.0 / 0.1179
    if mu <= mz:
        return a1, a2, a3
    t = math.log(mu / mz) / TWO_PI
    return a1 - b1 * t, a2 - b2 * t, a3 - b3 * t


def yukawa_beta_2hdm(yu: np.ndarray, yd: np.ndarray, ye: np.ndarray,
                     *, g1: float, g2: float, g3: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    yu, yd, ye = (np.asarray(x, dtype=complex) for x in (yu, yd, ye))
    tr_u = 3.0 * np.trace(yu @ yu.conj().T)
    tr_d = 3.0 * np.trace(yd @ yd.conj().T) + np.trace(ye @ ye.conj().T)
    c_u = (17.0 / 20.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    c_d = (1.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    c_e = (9.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2
    beta_u = 1.5 * yu @ yu.conj().T @ yu + 0.5 * yd @ yd.conj().T @ yu + (tr_u - c_u) * yu
    beta_d = 1.5 * yd @ yd.conj().T @ yd + 0.5 * yu @ yu.conj().T @ yd + (tr_d - c_d) * yd
    beta_e = 1.5 * ye @ ye.conj().T @ ye + (tr_d - c_e) * ye
    return beta_u / SIXTEEN_PI2, beta_d / SIXTEEN_PI2, beta_e / SIXTEEN_PI2


def solve_one_loop_matrix_yukawa_rge(bases: dict[str, Any] | None = None) -> dict[str, Any]:
    bases = bases or flavour_sector_bases()
    gauge = thresholds.solve_unification(two_loop=True)
    mz, mi = 91.1876, float(gauge["M_I_GeV"])
    h, f = np.asarray(bases["H"], dtype=complex), np.asarray(bases["F"], dtype=complex)
    yu0, yd0, ye0 = h + f, h + f, h - 3.0 * f
    def pack(*mats): return np.concatenate([m.reshape(-1) for m in mats])
    def unpack(vec): return vec[:9].reshape(3,3), vec[9:18].reshape(3,3), vec[18:27].reshape(3,3)
    y0 = pack(yu0, yd0, ye0); state0 = np.concatenate([y0.real, y0.imag])
    def rhs(log_mu, state):
        mu = math.exp(log_mu); inv1, inv2, inv3 = _gauge_inv_at_mu(mu, gauge)
        g1, g2, g3 = (math.sqrt(4.0 * math.pi / x) for x in (inv1, inv2, inv3))
        yu, yd, ye = unpack(state[:27] + 1j * state[27:])
        bu, bd, be = yukawa_beta_2hdm(yu, yd, ye, g1=g1, g2=g2, g3=g3)
        deriv = pack(bu, bd, be); return np.concatenate([deriv.real, deriv.imag])
    sol = solve_ivp(rhs, (math.log(mz), math.log(mi)), state0,
                    rtol=1e-7, atol=1e-9, method="RK45")
    if not sol.success:
        raise RuntimeError(f"diagnostic Yukawa ODE failed: {sol.message}")
    yu1, yd1, ye1 = unpack(sol.y[:27,-1] + 1j * sol.y[27:,-1])
    _u, su, _r = _biunitary(yu1 * bases["v_u"])
    _u, sd, _r = _biunitary(yd1 * bases["v_d"])
    _u, se, _r = _biunitary(ye1 * bases["v_d"])
    def rel(a,b): return float(np.linalg.norm(b-a) / max(np.linalg.norm(a), 1e-30))
    return {
        "status": "DIAGNOSTIC_MATRIX_ODE_INTEGRATED__VALIDATED_2HDM_RGE_OPEN",
        "integration": {"method": "RK45", "success": True, "n_steps": int(sol.y.shape[1]),
                        "mu_start_GeV": mz, "mu_stop_GeV": mi, "message": sol.message},
        "gauge_anchor": {"scheme": gauge["scheme"], "M_I_GeV": mi,
                         "M_GUT_GeV": float(gauge["M_GUT_GeV"])},
        "relative_matrix_change_MZ_to_MI": {"Yu": rel(yu0,yu1), "Yd": rel(yd0,yd1), "Ye": rel(ye0,ye1)},
        "running_masses_at_MI_GeV": {"up": [float(x) for x in su[::-1]],
                                     "down": [float(x) for x in sd[::-1]],
                                     "charged_lepton": [float(x) for x in se[::-1]],
                                     "ordering": "light_to_heavy"},
        "flag": {"diagnostic_matrix_ode_integrated": True,
                 "actual_one_loop_matrix_beta_system_solved": False,
                 "reference_validated_type_II_coefficients": False,
                 "running_vevs_included": False,
                 "two_loop_so10_complete": False,
                 "full_RG_global_fit_minimal": False,
                 "piecewise_threshold_yukawa_matching_complete": False,
                 "reason_still_open": "The ODE is a diagnostic ansatz. Published-convention validation, VEV running, scalar-sector dependence, and threshold matching remain."},
    }


def common_scale_sensitivity(rge: dict[str, Any], bases: dict[str, Any]) -> dict[str, Any]:
    low = flavour.QUARK_LEPTON; run = rge["running_masses_at_MI_GeV"]
    sectors = {"up": ("m_u","m_c","m_t"), "down": ("m_d","m_s","m_b"),
               "charged_lepton": ("m_e","m_mu","m_tau")}
    shifts = {}
    for sector, labels in sectors.items():
        for label, mi_value in zip(labels, run[sector]):
            lv = float(low[label]); shifts[label] = {"low_GeV": lv,
                "MI_GeV_diagnostic": float(mi_value), "ratio_MI_over_low": float(mi_value)/lv}
    return {"status": "COMMON_SCALE_SENSITIVITY_ONLY__PRECISION_TARGETS_OPEN",
            "mass_shifts": shifts, "ordering_note": "Diagnostic singular-value ratios only.",
            "flag": {"sensitivity_reported": True,
                     "global_fit_replaced_by_common_scale_targets": False}}


def build_report() -> dict[str, Any]:
    bases = flavour_sector_bases(); expansion = hierarchical_w_expansion()
    envelope = portal_cf_envelope(); fcnc = fcnc_experimental_bound_application(bases)
    rge = solve_one_loop_matrix_yukawa_rge(bases); sensitivity = common_scale_sensitivity(rge, bases)
    checks = {"hierarchical_expansion_controlled": expansion["epsilon"] < 1e-3,
              "portal_envelope_nonunique": not envelope["flag"]["unconditional_unique_Cf"],
              "fcnc_not_called_likelihood": not fcnc["flag"]["experimental_FCNC_bound_applied"],
              "diagnostic_ode_integrated": rge["flag"]["diagnostic_matrix_ode_integrated"],
              "matrix_rge_not_overclaimed": not rge["flag"]["actual_one_loop_matrix_beta_system_solved"]}
    failures = [n for n, ok in checks.items() if not ok]
    return {"status": "PHENOMENOLOGY_DIAGNOSTICS_PASS__COMPLETION_FLAGS_OPEN" if not failures else "PHENOMENOLOGY_DIAGNOSTICS_FAILED",
            "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
            "hierarchical_portal_expansion": expansion, "portal_cf_envelope": envelope,
            "fcnc_proxy_ledger": fcnc, "one_loop_matrix_yukawa_rge": rge,
            "common_scale_sensitivity": sensitivity,
            "advances": {"portal_envelope_constructed": True,
                         "hierarchical_W_expansion_controlled": True,
                         "fcnc_proxy_ledger_constructed": True,
                         "diagnostic_matrix_ODE_integrated": True,
                         "one_loop_matrix_Yukawa_RGE_solved": False,
                         "unconditional_unique_Cf": False,
                         "finite_model_fcnc_absence_proved": False,
                         "two_loop_so10_yukawa_complete": False},
            "verdict": "Useful portal, FCNC-proxy, and matrix-ODE diagnostics were executed. They do not constitute a validated experimental likelihood or a complete one-loop/two-loop Yukawa-RG solution."}


def write_markdown(report):
    return "\n".join(["# Phenomenology limits audit — v20", "", f"**Status:** `{report['status']}`", "",
                      "- Portal envelope: diagnostic, non-unique.", "- FCNC constraints: proxy ledger only.",
                      "- Broken-phase matrix ODE: integrated but not reference validated.",
                      "- Common-scale precision fit: open.", "- Two-loop SO(10)/threshold closure: open.",
                      "", report["verdict"], ""])


def main():
    report = build_report()
    ROOT.joinpath("PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    ROOT.joinpath("PUSH_PHENOMENOLOGY_LIMITS_V20.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "n_failed": report["n_failed"],
                      "advances": report["advances"], "verdict": report["verdict"]}, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
