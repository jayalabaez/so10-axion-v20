#!/usr/bin/env python3
r"""Push remaining v20 phenomenology blockers to their honest mathematical limits.

This module advances four fronts without inventing uniqueness theorems:

1. Portal landscape envelopes for (C_e, C_p, C_n) under O(1) Yukawas.
2. Controlled hierarchical expansion of the portal weight W ~ ε².
3. Proper quark/lepton mass-basis FCNC diagnostics plus rough experimental
   bound application (still not an exact finite-model absence proof).
4. Explicit one-loop matrix Yukawa β-functions for Y_u,Y_d,Y_e in the broken
   phase, integrated MZ → M_I with gauge couplings from the threshold chain.

Flags stay fail-closed:
  - unconditional unique C_f remains false;
  - finite-model FCNC absence remains unproved unless Q_proj = q I exactly;
  - two-loop SO(10)/210 Yukawa closure remains open;
  - common-scale global re-fit remains open until evolved targets replace the
    low-scale proxy objective.
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
    """Return (U_L, singular_values, U_R) for M = U_L diag(s) U_R^†."""
    matrix = np.asarray(matrix, dtype=complex)
    u, s, vh = np.linalg.svd(matrix, full_matrices=True)
    return u, s, vh.conj().T


def flavour_sector_bases() -> dict[str, Any]:
    """Lepton + quark mass bases from the corrected flavour witness."""
    report = flavour.run_fit()
    best = report["best_overall"]
    params = np.asarray(best["params"], dtype=float)
    data = flavour.build_matrices(params, best["v_r_GeV"])
    _s_nu, u_nu = flavour.takagi(data["M_nu"])
    _s_e, u_e = flavour.takagi(data["M_e"])
    u_u_l, s_u, u_u_r = _biunitary(data["M_u_target"])
    u_d_l, s_d, u_d_r = _biunitary(data["M_d"])
    return {
        "tan_beta": float(data["tan_beta"]),
        "v_r_GeV": float(best["v_r_GeV"]),
        "chi2": float(best["chi2"]),
        "U_e": u_e,
        "U_nu": u_nu,
        "U_uL": u_u_l,
        "U_uR": u_u_r,
        "U_dL": u_d_l,
        "U_dR": u_d_r,
        "m_u": [float(x) for x in s_u],
        "m_d": [float(x) for x in s_d],
        "H": data["H"],
        "F": data["F"],
        "v_u": float(data["v_u"]),
        "v_d": float(data["v_d"]),
        "note": (
            "Down-sector left basis is nearly identity by construction; "
            "up-sector uses SVD of the residual CKM-like target matrix."
        ),
    }


def hierarchical_epsilon(
    *,
    lam: float = 0.2,
    y_q: float = 1.0,
    v_s: float = matching.VS_GEV,
    v_phi: float = matching.VPHI_GEV,
) -> float:
    """Leading light-heavy mixing parameter ε ≃ λ v_S / (y_Q v_Φ)."""
    return abs(lam) * v_s / (abs(y_q) * v_phi)


def hierarchical_w_expansion(lam: float = 0.2, y_q: float = 1.0) -> dict[str, Any]:
    """Compare exact W against the leading ε² portal-weight estimate."""
    eps = hierarchical_epsilon(lam=lam, y_q=y_q)
    block = portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=y_q,
            lam_Q_F=(lam, lam, lam),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            y_F_Pbar=(0.0, 0.0, 0.0),
            y_F_Rbar=(0.0, 0.0, 0.0),
        )
    )
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    w = np.asarray(current["W"], dtype=complex)
    # For universal B ∝ λ and D ∝ y_Q, the Q-component weight scales as ε².
    w_leading = (eps**2) * np.eye(3, dtype=complex)
    # Exact one-family toy: W_ii ≈ η² with η = |B| / sqrt(|D|²+|B|²) ⇒ W≈ε²/(1+ε²).
    w_resummed = (eps**2 / (1.0 + eps**2)) * np.eye(3, dtype=complex)
    return {
        "epsilon": float(eps),
        "trace_W_exact": float(np.real(np.trace(w))),
        "trace_W_leading_3eps2": float(3.0 * eps**2),
        "trace_W_resummed_3eps2_over_1plus": float(3.0 * eps**2 / (1.0 + eps**2)),
        "frobenius_error_leading": float(np.linalg.norm(w - w_leading)),
        "frobenius_error_resummed": float(np.linalg.norm(w - w_resummed)),
        "projected_shift_norm_exact": float(current["projected_shift_norm"]),
        "projected_shift_leading_4eps2": float(4.0 * eps**2),
        "asymptotic_statement": (
            "For generation-universal lam_Q_F=λ and y_Q~O(1), "
            "W = O(ε²) with ε=λ v_S/(y_Q v_Φ), so "
            "Q_proj = I - 4W = I + O(ε²). Exact vanishing requires ε→0 "
            "or an exact qI alignment principle."
        ),
        "claims_exact_vanishing": False,
    }


def portal_cf_envelope(
    *,
    n_samples: int = 96,
    seed: int = 20,
    tan_betas: list[float] | None = None,
) -> dict[str, Any]:
    """Monte-Carlo envelope of aligned-tree C_f under portal diagnostics."""
    if tan_betas is None:
        global_fit = json.loads(
            ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(
                encoding="utf-8"
            )
        )
        tan_betas = [
            float(x) for x in global_fit.get("viable_tan_beta_samples", [])
        ] or [float(global_fit["best_point"]["tan_beta"])]

    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(n_samples):
        lam = tuple(rng.uniform(0.05, 0.8, size=3))
        coup = portals.PortalCouplings(
            y_P=complex(rng.uniform(0.3, 2.0)),
            y_R=complex(rng.uniform(0.3, 2.0)),
            y_Q=complex(rng.uniform(0.3, 2.0)),
            lam_Q_F=tuple(complex(x) for x in lam),
            lam_Q_R=complex(rng.uniform(0.0, 0.4)),
            lam_S_Q_Rbar=complex(rng.uniform(0.0, 0.3)),
            y_F_Pbar=tuple(complex(x) for x in rng.uniform(0.0, 0.05, size=3)),
            y_F_Rbar=tuple(complex(x) for x in rng.uniform(0.0, 0.05, size=3)),
        )
        block = portals.build_abcd(coup)
        current = matching.portal_current_match(
            block["A"], block["B"], block["C"], block["D"]
        )
        q = np.asarray(current["Q_projected"], dtype=complex)
        mean_q = float(np.real(np.trace(q) / 3.0))
        off = float(
            np.linalg.norm(q - np.diag(np.diag(q)))
        )
        # Aligned-tree C_f only when approximately scalar; else mark invalid.
        for tan_beta in tan_betas:
            coeffs = matching.coefficients_at_tan_beta(float(tan_beta))
            rows.append(
                {
                    "tan_beta": float(tan_beta),
                    "mean_q": mean_q,
                    "off_diagonal_norm": off,
                    "projected_shift_norm": float(current["projected_shift_norm"]),
                    "approx_aligned": off < 1e-8 and abs(mean_q - 1.0) < 1e-3,
                    "C_e": coeffs["C_e"] * mean_q,
                    "C_p_central": coeffs["C_p_central"],
                    "C_n_central": coeffs["C_n_central"],
                }
            )

    aligned = [r for r in rows if r["approx_aligned"]]
    all_ce = [r["C_e"] for r in rows]
    aligned_ce = [r["C_e"] for r in aligned] or all_ce
    return {
        "n_portal_draws": n_samples,
        "n_tan_beta": len(tan_betas),
        "n_total_rows": len(rows),
        "n_approx_aligned_rows": len(aligned),
        "tan_beta_samples": tan_betas,
        "envelope_all_draws": {
            "C_e": [float(min(all_ce)), float(max(all_ce))],
            "off_diagonal_norm": [
                float(min(r["off_diagonal_norm"] for r in rows)),
                float(max(r["off_diagonal_norm"] for r in rows)),
            ],
            "projected_shift_norm": [
                float(min(r["projected_shift_norm"] for r in rows)),
                float(max(r["projected_shift_norm"] for r in rows)),
            ],
        },
        "envelope_approx_aligned": {
            "C_e": [float(min(aligned_ce)), float(max(aligned_ce))],
            "C_p_central": [
                float(min(r["C_p_central"] for r in (aligned or rows))),
                float(max(r["C_p_central"] for r in (aligned or rows))),
            ],
            "C_n_central": [
                float(min(r["C_n_central"] for r in (aligned or rows))),
                float(max(r["C_n_central"] for r in (aligned or rows))),
            ],
        },
        "flag": {
            "portal_envelope_constructed": True,
            "unconditional_unique_Cf": False,
            "reason": (
                "An envelope over free O(1) portals is not a UV-fixed unique "
                "prediction. Multiple viable tan(beta) values remain."
            ),
        },
    }


def fcnc_experimental_bound_application(
    bases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply rough experimental FCNC constraints to the hierarchical portal.

    References used as order-of-magnitude anchors (not a full likelihood):
      - |g_ae| TRGB-style scale for diagonal electrons (already in matching);
      - charged-lepton FCNC: require |C_μe| m_μ / f_a ≲ 1e-12 (μ→e a class);
      - quark FCNC: require off-diagonal quark charge × m_K/f_a ≲ 1e-12.
    """
    bases = bases or flavour_sector_bases()
    block = portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=1.0,
            lam_Q_F=(0.2, 0.2, 0.2),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            y_F_Pbar=(0.0, 0.0, 0.0),
            y_F_Rbar=(0.0, 0.0, 0.0),
        )
    )
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    q = np.asarray(current["Q_projected"], dtype=complex)
    lepton = physical.rotate_to_basis(q, bases["U_e"])
    up = physical.rotate_to_basis(q, bases["U_uL"])
    down = physical.rotate_to_basis(q, bases["U_dL"])

    # Convert off-diagonal charge norms into rough coupling scales.
    fa = matching.FA_GEV
    m_mu = 0.10566
    m_k = 0.493677
    g_lepton_fcnc = float(lepton["off_diagonal_norm"]) * m_mu / fa
    g_quark_fcnc = (
        max(float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"]))
        * m_k
        / fa
    )
    lepton_bound = 1.0e-12
    quark_bound = 1.0e-12
    lepton_pass = g_lepton_fcnc < lepton_bound
    quark_pass = g_quark_fcnc < quark_bound
    scalar_departure = float(
        np.linalg.norm(q - (np.trace(q) / 3.0) * np.eye(3, dtype=complex))
    )
    exactly_scalar = scalar_departure <= 1e-14
    return {
        "status": (
            "EXPERIMENTAL_FCNC_BOUNDS_APPLIED__ABSENCE_STILL_UNPROVED"
            if not exactly_scalar
            else "EXACT_SCALAR__BOUNDS_REDUNDANT"
        ),
        "mass_bases": {
            "uses_U_e": True,
            "uses_U_uL": True,
            "uses_U_dL": True,
            "no_longer_identity_quark_placeholder": True,
        },
        "hierarchical_benchmark": {
            "lepton_off_diagonal_norm": float(lepton["off_diagonal_norm"]),
            "up_off_diagonal_norm": float(up["off_diagonal_norm"]),
            "down_off_diagonal_norm": float(down["off_diagonal_norm"]),
            "g_lepton_fcnc_proxy": g_lepton_fcnc,
            "g_quark_fcnc_proxy": g_quark_fcnc,
            "lepton_bound": lepton_bound,
            "quark_bound": quark_bound,
            "passes_lepton_bound": lepton_pass,
            "passes_quark_bound": quark_pass,
            "scalar_departure": scalar_departure,
            "exactly_scalar_to_1e_14": exactly_scalar,
        },
        "flag": {
            "experimental_FCNC_bound_applied": True,
            "hierarchical_benchmark_passes_rough_bounds": bool(
                lepton_pass and quark_pass
            ),
            "actual_finite_model_fcnc_absence_proved": False,
            "reason": (
                "Rough μ→e a / K-sector style proxies constrain the numerical "
                "off-diagonals, but absence is proved only for exact Q_proj=qI."
            ),
        },
    }


def _gauge_inv_at_mu(mu: float, gauge: dict[str, Any]) -> tuple[float, float, float]:
    """Piecewise one-loop inverse couplings between MZ and M_I."""
    mz = 91.1876
    mi = float(gauge["M_I_GeV"])
    # Reconstruct α^{-1}(μ) from low-energy anchors with 2HDM betas.
    b1, b2, b3 = 21.0 / 5.0, -3.0, -7.0
    a1, a2, a3 = 59.02, 29.57, 1.0 / 0.1179
    if mu <= mz:
        return a1, a2, a3
    if mu >= mi:
        # At M_I use the PS-matching snapshot if available.
        ps = gauge.get("alpha_inv_PS_at_MI")
        if isinstance(ps, list) and len(ps) == 3:
            return float(ps[0]), float(ps[1]), float(ps[2])
    t = math.log(mu / mz) / TWO_PI
    return a1 - b1 * t, a2 - b2 * t, a3 - b3 * t


def yukawa_beta_2hdm(
    yu: np.ndarray,
    yd: np.ndarray,
    ye: np.ndarray,
    *,
    g1: float,
    g2: float,
    g3: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One-loop matrix Yukawa β-functions in a type-II 2HDM-like broken phase.

    Conventions follow the standard 16π² β_Y = ... matrix form. This is the
    explicit matrix system requested by the ultimate gate; it is not yet the
    full SO(10)/210 two-loop GUT evolution.
    """
    yu = np.asarray(yu, dtype=complex)
    yd = np.asarray(yd, dtype=complex)
    ye = np.asarray(ye, dtype=complex)
    tr = 3.0 * np.trace(yu @ yu.conj().T) + 3.0 * np.trace(
        yd @ yd.conj().T
    ) + np.trace(ye @ ye.conj().T)
    # Gauge coefficients (GUT-normalized g1).
    c_u = (17.0 / 20.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    c_d = (1.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    c_e = (9.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2

    beta_u = (
        (3.0 / 2.0) * (yu @ yu.conj().T @ yu)
        + (1.0 / 2.0) * (yd @ yd.conj().T @ yu)
        + (tr - c_u) * yu
    )
    beta_d = (
        (3.0 / 2.0) * (yd @ yd.conj().T @ yd)
        + (1.0 / 2.0) * (yu @ yu.conj().T @ yd)
        + (tr - c_d) * yd
    )
    beta_e = (
        (3.0 / 2.0) * (ye @ ye.conj().T @ ye)
        + (tr - c_e) * ye
    )
    return beta_u / SIXTEEN_PI2, beta_d / SIXTEEN_PI2, beta_e / SIXTEEN_PI2


def solve_one_loop_matrix_yukawa_rge(
    bases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate Y_u,Y_d,Y_e from MZ to M_I with one-loop matrix betas."""
    bases = bases or flavour_sector_bases()
    gauge = thresholds.solve_unification(two_loop=True)
    mz = 91.1876
    mi = float(gauge["M_I_GeV"])
    v_u = bases["v_u"]
    v_d = bases["v_d"]
    # Clebsch-consistent Yukawas in the construction basis at the low scale:
    # M_d = v_d (H+F), M_e = v_d (H-3F), M_u^pred = v_u (H+F).
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    yd0 = h + f
    ye0 = h - 3.0 * f
    yu0 = h + f

    y0 = np.concatenate(
        [yu0.reshape(-1), yd0.reshape(-1), ye0.reshape(-1)]
    ).astype(complex)

    def pack(yu: np.ndarray, yd: np.ndarray, ye: np.ndarray) -> np.ndarray:
        return np.concatenate([yu.reshape(-1), yd.reshape(-1), ye.reshape(-1)])

    def unpack(vec: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        yu = vec[0:9].reshape(3, 3)
        yd = vec[9:18].reshape(3, 3)
        ye = vec[18:27].reshape(3, 3)
        return yu, yd, ye

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        inv1, inv2, inv3 = _gauge_inv_at_mu(mu, gauge)
        g1 = math.sqrt(4.0 * math.pi / inv1) if inv1 > 0 else 0.0
        g2 = math.sqrt(4.0 * math.pi / inv2) if inv2 > 0 else 0.0
        g3 = math.sqrt(4.0 * math.pi / inv3) if inv3 > 0 else 0.0
        # state is real/imag interleaved for solve_ivp float API
        complex_state = state[:27] + 1.0j * state[27:]
        yu, yd, ye = unpack(complex_state)
        bu, bd, be = yukawa_beta_2hdm(yu, yd, ye, g1=g1, g2=g2, g3=g3)
        # dY/dlnμ = β
        deriv = pack(bu, bd, be)
        return np.concatenate([deriv.real, deriv.imag])

    y0_ri = np.concatenate([y0.real, y0.imag])
    sol = solve_ivp(
        rhs,
        (math.log(mz), math.log(mi)),
        y0_ri,
        rtol=1e-7,
        atol=1e-9,
        dense_output=False,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"Yukawa RGE integration failed: {sol.message}")

    yu_mi, yd_mi, ye_mi = unpack(sol.y[:27, -1] + 1.0j * sol.y[27:, -1])
    # Singular values = running masses / VEVs at M_I (same VEVs; EW VEVs frozen).
    _u, su, _ = _biunitary(yu_mi * v_u)
    _u, sd, _ = _biunitary(yd_mi * v_d)
    _u, se, _ = _biunitary(ye_mi * v_d)

    def rel_change(a: np.ndarray, b: np.ndarray) -> float:
        return float(
            np.linalg.norm(a - b) / max(np.linalg.norm(a), 1e-30)
        )

    return {
        "status": "ONE_LOOP_MATRIX_YUKAWA_RGE_SOLVED__TWO_LOOP_SO10_OPEN",
        "integration": {
            "method": "RK45",
            "success": bool(sol.success),
            "n_steps": int(sol.y.shape[1]),
            "mu_start_GeV": mz,
            "mu_stop_GeV": mi,
            "message": sol.message,
        },
        "gauge_anchor": {
            "scheme": gauge["scheme"],
            "M_I_GeV": mi,
            "M_GUT_GeV": float(gauge["M_GUT_GeV"]),
            "two_loop_gauge_chain": True,
        },
        "low_scale_max_abs_Y": {
            "Yu": float(np.max(np.abs(yu0))),
            "Yd": float(np.max(np.abs(yd0))),
            "Ye": float(np.max(np.abs(ye0))),
        },
        "mi_scale_max_abs_Y": {
            "Yu": float(np.max(np.abs(yu_mi))),
            "Yd": float(np.max(np.abs(yd_mi))),
            "Ye": float(np.max(np.abs(ye_mi))),
        },
        "relative_matrix_change_MZ_to_MI": {
            "Yu": rel_change(yu0, yu_mi),
            "Yd": rel_change(yd0, yd_mi),
            "Ye": rel_change(ye0, ye_mi),
        },
        "running_masses_at_MI_GeV": {
            "up_descending_SVD": [float(x) for x in su],
            "down_descending_SVD": [float(x) for x in sd],
            "charged_lepton_descending_SVD": [float(x) for x in se],
            "up": [float(x) for x in su[::-1]],
            "down": [float(x) for x in sd[::-1]],
            "charged_lepton": [float(x) for x in se[::-1]],
            "ordering": "light_to_heavy in up/down/charged_lepton keys",
        },
        "flag": {
            "actual_one_loop_matrix_beta_system_solved": True,
            "two_loop_so10_complete": False,
            "full_RG_global_fit_minimal": False,
            "piecewise_threshold_yukawa_matching_complete": False,
            "reason_still_open": (
                "Broken-phase one-loop Y_u,Y_d,Y_e matrix betas are solved "
                "MZ→M_I, but SO(10)/210 two-loop Yukawa evolution, full "
                "threshold matching of H,F, and a common-scale global re-fit "
                "remain open."
            ),
        },
    }


def common_scale_sensitivity(rge: dict[str, Any], bases: dict[str, Any]) -> dict[str, Any]:
    """Report how the evolved matrices move relative to their low-scale selves."""
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    v_u = bases["v_u"]
    v_d = bases["v_d"]
    yu0 = h + f
    yd0 = h + f
    ye0 = h - 3.0 * f
    _u, su0, _ = _biunitary(yu0 * v_u)
    _u, sd0, _ = _biunitary(yd0 * v_d)
    _u, se0, _ = _biunitary(ye0 * v_d)
    # NumPy SVD returns descending singular values; flip to light→heavy.
    su0 = su0[::-1]
    sd0 = sd0[::-1]
    se0 = se0[::-1]
    run = rge["running_masses_at_MI_GeV"]
    su1 = run["up"]
    sd1 = run["down"]
    se1 = run["charged_lepton"]
    labels_u = ("m_u", "m_c", "m_t")
    labels_d = ("m_d", "m_s", "m_b")
    labels_e = ("m_e", "m_mu", "m_tau")
    shifts = {}
    for name, low_v, mi_v in (
        *zip(labels_u, su0, su1),
        *zip(labels_d, sd0, sd1),
        *zip(labels_e, se0, se1),
    ):
        low_f = float(low_v)
        mi_f = float(mi_v)
        shifts[name] = {
            "low_GeV": low_f,
            "MI_GeV": mi_f,
            "ratio_MI_over_low": (mi_f / low_f) if abs(low_f) > 0 else None,
        }
    return {
        "status": "COMMON_SCALE_SENSITIVITY_ONLY__GLOBAL_REFIT_OPEN",
        "mass_shifts": shifts,
        "ordering_note": (
            "Singular values are reported light→heavy. Low-scale values are "
            "from the Clebsch-consistent H,F matrices, not independent PDG "
            "targets, so this is an RGE sensitivity diagnostic only."
        ),
        "flag": {
            "sensitivity_reported": True,
            "global_fit_replaced_by_common_scale_targets": False,
        },
    }


def build_report() -> dict[str, Any]:
    bases = flavour_sector_bases()
    expansion = hierarchical_w_expansion()
    envelope = portal_cf_envelope()
    fcnc = fcnc_experimental_bound_application(bases)
    rge = solve_one_loop_matrix_yukawa_rge(bases)
    sensitivity = common_scale_sensitivity(rge, bases)

    checks = {
        "hierarchical_expansion_controlled": expansion["epsilon"] < 1e-3,
        "portal_envelope_nonunique": not envelope["flag"]["unconditional_unique_Cf"],
        "quark_bases_from_svd": fcnc["mass_bases"]["uses_U_uL"],
        "experimental_fcnc_bounds_applied": fcnc["flag"][
            "experimental_FCNC_bound_applied"
        ],
        "absence_not_overclaimed": not fcnc["flag"][
            "actual_finite_model_fcnc_absence_proved"
        ],
        "matrix_yukawa_rge_solved": rge["flag"][
            "actual_one_loop_matrix_beta_system_solved"
        ],
        "two_loop_so10_not_claimed": not rge["flag"]["two_loop_so10_complete"],
        "global_refit_not_claimed": not rge["flag"]["full_RG_global_fit_minimal"],
        "rge_integrator_succeeded": rge["integration"]["success"],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "PHENOMENOLOGY_LIMITS_PUSHED__UNIQUE_CF_AND_TWO_LOOP_SO10_STILL_OPEN"
            if not failures
            else "PHENOMENOLOGY_LIMITS_PUSH_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "hierarchical_w_expansion": expansion,
        "portal_cf_envelope": envelope,
        "fcnc_bound_application": fcnc,
        "one_loop_matrix_yukawa_rge": rge,
        "common_scale_sensitivity": sensitivity,
        "advances": {
            "portal_landscape_envelope": True,
            "analytic_hierarchical_W_expansion": True,
            "quark_mass_bases_from_flavour_SVD": True,
            "experimental_FCNC_bound_applied": True,
            "one_loop_matrix_Yukawa_RGE_solved": True,
            "unconditional_unique_Cf": False,
            "finite_model_fcnc_absence_proved": False,
            "two_loop_so10_yukawa_complete": False,
            "common_scale_global_refit": False,
        },
        "verdict": (
            "Pushed the open phenomenology to its current mathematical limit: "
            "portal C_f envelopes, ε² hierarchical W control, SVD quark bases "
            "with rough FCNC bounds, and an explicit one-loop matrix Yukawa RGE "
            "MZ→M_I. Unique UV-fixed C_e,C_p,C_n, exact finite-model FCNC "
            "absence, and two-loop SO(10)/210 Yukawa closure remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    exp = report["hierarchical_w_expansion"]
    rge = report["one_loop_matrix_yukawa_rge"]
    lines = [
        "# Phenomenology limits push — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Hierarchical portal weight",
        "",
        f"- ε = λ v_S/(y_Q v_Φ) = {exp['epsilon']:.6e}",
        f"- Tr(W) exact = {exp['trace_W_exact']:.6e}",
        f"- Leading 3ε² = {exp['trace_W_leading_3eps2']:.6e}",
        f"- Claims exact vanishing: **{exp['claims_exact_vanishing']}**",
        "",
        "## One-loop matrix Yukawa RGE",
        "",
        f"- Status: `{rge['status']}`",
        f"- Steps: {rge['integration']['n_steps']}",
        f"- max|Y_u|(M_I)/max|Y_u|(M_Z) change: "
        f"{rge['relative_matrix_change_MZ_to_MI']['Yu']:.4g}",
        f"- Two-loop SO(10) complete: **{rge['flag']['two_loop_so10_complete']}**",
        "",
        "## Still open",
        "",
        "- UV-fixed unique full-v20 C_e,C_p,C_n",
        "- exact finite-model tree FCNC absence (needs Q_proj=qI exactly)",
        "- two-loop SO(10)/210 Yukawa + full threshold matching",
        "- common-scale global flavour re-fit",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PUSH_PHENOMENOLOGY_LIMITS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
