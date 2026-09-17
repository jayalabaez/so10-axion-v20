#!/usr/bin/env python3
r"""Fail-closed general minimal SO(10) 10+126 Yukawa sector (v21).

The v20 flavour benchmark (``flavour_clebsch_fit_v20``) reconstructs

    M_d = v_d (H + F),  M_e = v_d (H - 3F),  M_u = v_u (H + F),

so ``H + F = M_d / v_d`` as a matrix identity and ``M_u = tan(beta) M_d``.
That ansatz predicts ``V_CKM = 1`` and equal up/down mass ratios in every
generation. ``global_flavour_fit_v20`` places its CKM pulls on the nuisance
rotation used to build the *target* ``M_u``, so those pulls are satisfied while
the model itself still predicts no quark mixing.

This module uses the general minimal Yukawa structure with independent 10/126
doublet vev ratios, at the Pati-Salam scale ``M_I``:

    M_d = H + F               M_e = H - 3F
    M_u = r_H H + r_F F       M_D = r_H H - 3 r_F F
    M_R = (v_R rho / v_d) F   M_L = eps F

with ``r_H = v10^u/v10^d`` (real), ``r_F = v126^u/v126^d`` (complex),
``rho = v_d/|v126^d| >= 1``, the doublet vev sum rules and perturbativity.
Charged-fermion masses and CKM run M_Z -> M_I (type-II 2HDM, one loop plus the
dominant two-loop QCD terms); the light-neutrino matrix runs M_I -> M_Z.

Frozen witnesses in ``FLAVOUR_GENERAL_YUKAWA_V21_WITNESSES.json`` come from
multistart Levenberg-Marquardt fits; this module only *revalidates* them.

Fail-closed:
  * a witness is a proof that a solution exists, never that it is unique;
  * 14 physical parameters fit 13 observables (negative dof), so exact fits are
    expected and show consistency, not confirmation;
  * the light masses arise from a cancellation 50-700 times larger than m_nu;
    capping that cancellation leaves no acceptable fit;
  * the frozen witnesses are tree-level matched: right-handed-neutrino
    thresholds are NOT part of the fit that produced them. They were applied
    afterwards and the fit redone with them, to test whether the predictions
    survive (they do). Heavy-Higgs and two-loop threshold matching are absent.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import flavour_clebsch_fit_v20 as flavour

ROOT = Path(__file__).resolve().parent
WITNESSES = ROOT / "FLAVOUR_GENERAL_YUKAWA_V21_WITNESSES.json"
OUT_JSON = ROOT / "FLAVOUR_GENERAL_YUKAWA_V21_VERDICT.json"
OUT_MD = ROOT / "FLAVOUR_GENERAL_YUKAWA_V21.md"

K = 16.0 * math.pi ** 2
MZ = 91.1876
VEV = 246.0 / math.sqrt(2.0)
BENCHMARK_VR = 6.313855e11
PLANCK_SUM_MNU = 0.12
DESI_SUM_MNU = 0.072

# Huang & Zhou, Phys. Rev. D 103, 016010 (2021), Tables 2-3, full SM at M_Z.
MASS_MZ = {"u": 1.23e-3, "c": 0.620, "t": 168.26, "d": 2.67e-3, "s": 53.16e-3,
           "b": 2.839, "e": 0.48307e-3, "mu": 0.101766, "tau": 1.72856}
REL_ERR_MZ = {"u": 0.21 / 1.23, "c": 0.017 / 0.620, "t": 0.75 / 168.26,
              "d": 0.19 / 2.67, "s": 4.61 / 53.16, "b": 0.026 / 2.839,
              "e": 0.00045 / 0.48307, "mu": 0.000023 / 0.101766,
              "tau": 0.00028 / 1.72856}
G_MZ = {"gp": 0.357254, "g2": 0.65100, "g3": 1.2104}
# Same tables at mu = 1e12 GeV (validation targets for the SM running mode).
HZ_1E12 = {"t": 85.07, "b": 1.194, "c": 0.283, "s": 24.76e-3, "d": 1.24e-3,
           "u": 0.56e-3, "tau": 1.73194, "mu": 0.101936, "e": 0.48388e-3,
           "g3": 0.6017, "g2": 0.55325, "gp": 0.414821}
# PDG 2024 Wolfenstein fit.
CKM_LOW = {"s12": (0.22501, 0.00068), "s23": (0.04182, 0.00085),
           "s13": (0.00369, 0.00011), "J": (3.08e-5, 0.15e-5)}
# NuFIT 6.0 (arXiv:2410.05380), Table 1, IC24 with SK-atm, inverted ordering.
NUFIT_IO = {"sin2_th12": (0.308, 0.012), "sin2_th23": (0.550, 0.015),
            "sin2_th13": (0.02231, 0.00056), "dm21": (7.49e-5, 0.19e-5),
            "dm31": (-2.484e-3, 0.020e-3), "delta_deg": (274.0, 25.0)}

PULL_NAMES = ("m_u", "m_c", "m_t", "s12", "s23", "s13", "J", "th12", "th23",
              "th13", "dm21", "dm31", "dCP", "z_d", "z_s", "z_b",
              "pen_planck", "pen_y126", "pen_sumrule")


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------
def _rhs(_t, y, mode, lam2):
    yu, yd, ye = y[0:3], y[3:6], y[6:9]
    g1, g2, g3 = y[9], y[10], y[11]
    su, sd, se = yu ** 2, yd ** 2, ye ** 2
    if mode == "2hdm":
        b = (21.0 / 5.0, -3.0, -7.0)
        cross = 0.5
        tu = 3 * su.sum()
        td = 3 * sd.sum() + se.sum()
        te = td
    else:
        b = (41.0 / 10.0, -19.0 / 6.0, -7.0)
        cross = -1.5
        tu = td = te = 3 * su.sum() + 3 * sd.sum() + se.sum()
    gu = 8 * g3 ** 2 + 2.25 * g2 ** 2 + 0.85 * g1 ** 2
    gd = 8 * g3 ** 2 + 2.25 * g2 ** 2 + 0.25 * g1 ** 2
    ge = 2.25 * g2 ** 2 + 2.25 * g1 ** 2
    qcd2 = -108.0 * g3 ** 4 / K
    dyu = yu * (1.5 * su + cross * sd + tu - gu + qcd2) / K
    dyd = yd * (1.5 * sd + cross * su + td - gd + qcd2) / K
    dye = ye * (1.5 * se + te - ge) / K
    dg = np.array([b[0] * g1 ** 3, b[1] * g2 ** 3, b[2] * g3 ** 3 - 26.0 * g3 ** 5 / K]) / K
    ckm_coef = 0.5 if mode == "2hdm" else 1.5
    d_ln_s = -ckm_coef * (su[2] + sd[2]) / K
    if mode == "2hdm":
        alpha = -3 * g2 ** 2 + lam2 + 6 * su.sum()
    else:
        alpha = -3 * g2 ** 2 + lam2 + 2 * (3 * su.sum() + 3 * sd.sum() + se.sum())
    return np.concatenate([dyu, dyd, dye, dg, [d_ln_s, alpha / K], se / K])


def run(mu_high: float, tan_beta: float | None = None, mode: str = "2hdm",
        lam2: float = 0.5) -> dict[str, Any]:
    if mode == "2hdm":
        vu = VEV * math.sin(math.atan(tan_beta))
        vd = VEV * math.cos(math.atan(tan_beta))
    else:
        vu = vd = VEV
    m = MASS_MZ
    y0 = np.array([m["u"] / vu, m["c"] / vu, m["t"] / vu,
                   m["d"] / vd, m["s"] / vd, m["b"] / vd,
                   m["e"] / vd, m["mu"] / vd, m["tau"] / vd,
                   math.sqrt(5.0 / 3.0) * G_MZ["gp"], G_MZ["g2"], G_MZ["g3"],
                   0.0, 0.0, 0.0, 0.0, 0.0])
    sol = solve_ivp(_rhs, (math.log(MZ), math.log(mu_high)), y0, args=(mode, lam2),
                    method="DOP853", rtol=1e-10, atol=1e-13)
    y = sol.y[:, -1]
    yu, yd, ye = y[0:3], y[3:6], y[6:9]
    ce = 0.5 if mode == "2hdm" else -1.5
    return {
        "masses": {"u": yu[0] * vu, "c": yu[1] * vu, "t": yu[2] * vu,
                   "d": yd[0] * vd, "s": yd[1] * vd, "b": yd[2] * vd,
                   "e": ye[0] * vd, "mu": ye[1] * vd, "tau": ye[2] * vd},
        "gauge": {"g2": y[10], "g3": y[11], "gp": y[9] / math.sqrt(5.0 / 3.0)},
        "ckm_high": {"s12": CKM_LOW["s12"][0],
                     "s23": CKM_LOW["s23"][0] * math.exp(y[12]),
                     "s13": CKM_LOW["s13"][0] * math.exp(y[12]),
                     "J": CKM_LOW["J"][0] * math.exp(2 * y[12])},
        "nu_scale": math.exp(-y[13]),
        "nu_flavour": np.exp(-ce * y[14:17]),
        "vu": vu, "vd": vd,
    }


def rg_validation() -> dict[str, Any]:
    r = run(1e12, mode="sm")
    rel = {k: (r["masses"][k] - HZ_1E12[k]) / HZ_1E12[k] for k in r["masses"]}
    rel.update({k: (r["gauge"][k] - HZ_1E12[k]) / HZ_1E12[k] for k in ("g2", "g3", "gp")})
    return {"reference": "Huang & Zhou, PRD 103, 016010 (2021), mu = 1e12 GeV",
            "relative_deviation": {k: float(v) for k, v in rel.items()},
            "max_abs_quark_deviation": float(max(abs(rel[k]) for k in ("u", "c", "t", "d", "s", "b"))),
            "max_abs_lepton_deviation": float(max(abs(rel[k]) for k in ("e", "mu", "tau"))),
            "max_abs_gauge_deviation": float(max(abs(rel[k]) for k in ("g2", "g3", "gp")))}


# ---------------------------------------------------------------------------
# General Yukawa model
# ---------------------------------------------------------------------------
def _takagi(matrix: np.ndarray):
    return flavour.takagi(0.5 * (matrix + matrix.T))


def pmns_inverted(mnu: np.ndarray, me_diag: np.ndarray) -> dict[str, Any]:
    sing, u_nu = flavour.takagi(0.5 * (mnu + mnu.T))
    _, u_e = flavour.takagi(me_diag)
    order = [1, 2, 0]
    masses = sing[order] * 1e9
    u = u_e.conj().T @ u_nu[:, order]
    s13 = abs(u[0, 2])
    c13 = math.sqrt(max(1e-30, 1 - s13 ** 2))
    s12 = min(1.0, abs(u[0, 1]) / c13)
    s23 = min(1.0, abs(u[1, 2]) / c13)
    c12 = math.sqrt(max(0.0, 1.0 - s12 ** 2))
    c23 = math.sqrt(max(0.0, 1.0 - s23 ** 2))
    jarl = np.imag(u[0, 0] * u[1, 1] * np.conj(u[0, 1]) * np.conj(u[1, 0]))
    sd = c12 * c23 * c13 ** 2 * s12 * s23 * s13
    sin_d = 0.0 if sd < 1e-30 else float(np.clip(jarl / sd, -1, 1))
    cd = 2.0 * s12 * c12 * c23 * s23 * s13
    cn = abs(u[1, 0]) ** 2 - s12 ** 2 * c23 ** 2 - c12 ** 2 * s23 ** 2 * s13 ** 2
    cos_d = 1.0 if cd < 1e-30 else float(np.clip(cn / cd, -1, 1))
    return {"mnu_eV": masses.tolist(), "sum_mnu_eV": float(masses.sum()),
            "dm21_eV2": float(masses[1] ** 2 - masses[0] ** 2),
            "dm31_eV2": float(masses[2] ** 2 - masses[1] ** 2),
            "sin2_th12": s12 ** 2, "sin2_th23": s23 ** 2, "sin2_th13": s13 ** 2,
            "delta_cp_deg": math.degrees(math.atan2(sin_d, cos_d)) % 360.0}


class Stratum:
    """Running data and residuals at fixed (tan beta, v_R)."""

    def __init__(self, tan_beta: float, v_r: float, *, lam2: float = 0.5,
                 floor: float = 0.05, s12_floor: float = 0.01, y_max: float = 3.0,
                 planck: bool = True, inverted: bool = False):
        self.tb, self.v_r, self.y_max = tan_beta, v_r, y_max
        self.planck, self.inverted = planck, inverted
        r = run(v_r, tan_beta=tan_beta, lam2=lam2)
        self.m, self.vu, self.vd = r["masses"], r["vu"], r["vd"]
        self.ckm, self.nu_scale, self.nu_f = r["ckm_high"], r["nu_scale"], r["nu_flavour"]
        self.nufit = NUFIT_IO if inverted else flavour.NUFIT

        def rel(k):
            return max(REL_ERR_MZ[k], floor)

        self.sig_up = {k: rel(k) * self.m[k] for k in ("u", "c", "t")}
        self.rel_down = {k: rel(k) for k in ("d", "s", "b")}
        self.sig_ckm = {
            "s12": max(CKM_LOW["s12"][1] / CKM_LOW["s12"][0], s12_floor) * self.ckm["s12"],
            "s23": max(CKM_LOW["s23"][1] / CKM_LOW["s23"][0], floor) * self.ckm["s23"],
            "s13": max(CKM_LOW["s13"][1] / CKM_LOW["s13"][0], floor) * self.ckm["s13"],
            "J": max(CKM_LOW["J"][1] / CKM_LOW["J"][0], floor) * self.ckm["J"],
        }
        self.me_diag = np.diag([self.m["e"], self.m["mu"], self.m["tau"]]).astype(complex)

    def build(self, p: np.ndarray) -> dict[str, Any]:
        def s(x):
            return 0.5 * (1.0 + math.tanh(x))

        z = p[14:17]
        md = np.diag([self.m["d"] * (1 + self.rel_down["d"] * z[0]),
                      self.m["s"] * (1 + self.rel_down["s"] * z[1]),
                      self.m["b"] * (1 + self.rel_down["b"] * z[2])]).astype(complex)
        v = np.diag([1.0, np.exp(1j * p[4]), np.exp(1j * p[5])]) @ flavour._rotation(
            s(p[0]), s(p[1]), s(p[2]), p[3])
        de = np.diag([self.m["e"] * np.exp(1j * p[6]), self.m["mu"] * np.exp(1j * p[7]),
                      self.m["tau"] * np.exp(1j * p[8])])
        me = v @ de @ v.T
        h = (3.0 * md + me) / 4.0
        f = (md - me) / 4.0
        r_h = math.exp(p[9])
        r_f = math.exp(p[10]) * np.exp(1j * p[11])
        rho = 1.0 + math.exp(p[12])
        eps = 10.0 ** p[13]
        m_dirac = r_h * h - 3.0 * r_f * f
        m_r = (self.v_r * rho / self.vd) * f
        mnu = eps * f - m_dirac @ np.linalg.solve(m_r, m_dirac.T)
        return {"md": md, "me": me, "H": h, "F": f, "mu": r_h * h + r_f * f,
                "mD": m_dirac, "mR": m_r, "mnu": 0.5 * (mnu + mnu.T),
                "rH": r_h, "rF": r_f, "rho": rho, "eps": eps}

    def observables(self, p: np.ndarray) -> dict[str, Any]:
        b = self.build(p)
        su, vu = _takagi(b["mu"])
        c = vu.conj().T
        ckm = {"s12": abs(c[0, 1]), "s23": abs(c[1, 2]), "s13": abs(c[0, 2]),
               "J": abs(np.imag(c[0, 1] * c[1, 2] * np.conj(c[0, 2]) * np.conj(c[1, 1])))}
        _, ve = _takagi(b["me"])
        mprime = ve.conj().T @ b["mnu"] @ ve.conj()
        mz = self.nu_scale * (np.outer(self.nu_f, self.nu_f) * mprime)
        mz = 0.5 * (mz + mz.T)
        extract = pmns_inverted if self.inverted else flavour._pmns_from_matrices
        lep = extract(mz, self.me_diag)
        rho, r_h, r_f = b["rho"], b["rH"], abs(b["rF"])
        y126 = rho * np.max(np.abs(b["F"])) / self.vd
        x_lo = np.max(np.abs(b["H"])) / (self.y_max * self.vd)
        x_hi = min(math.sqrt(max(0.0, 1.0 - 1.0 / rho ** 2)),
                   math.sqrt(max(0.0, self.tb ** 2 - r_f ** 2 / rho ** 2)) / r_h)
        return {"up": {"u": su[0], "c": su[1], "t": su[2]}, "ckm": ckm, "lep": lep,
                "m_bb_eV": float(abs(mz[0, 0]) * 1e9),
                "y126": float(y126), "x_lo": float(x_lo), "x_hi": float(x_hi), "build": b}

    def residuals(self, p: np.ndarray) -> np.ndarray:
        o = self.observables(p)
        r = [(o["up"][k] - self.m[k]) / self.sig_up[k] for k in ("u", "c", "t")]
        r += [(o["ckm"][k] - self.ckm[k]) / self.sig_ckm[k] for k in ("s12", "s23", "s13", "J")]
        lep = o["lep"]
        for key, obs in (("sin2_th12", "sin2_th12"), ("sin2_th23", "sin2_th23"),
                         ("sin2_th13", "sin2_th13"), ("dm21", "dm21_eV2"), ("dm31", "dm31_eV2")):
            central, sigma = self.nufit[key]
            r.append((lep[obs] - central) / sigma)
        central, sigma = self.nufit["delta_deg"]
        r.append(((lep["delta_cp_deg"] - central + 180.0) % 360.0 - 180.0) / sigma)
        r.extend(list(p[14:17]))
        r.append(math.sqrt(1e5) * max(0.0, lep["sum_mnu_eV"] - PLANCK_SUM_MNU) if self.planck else 0.0)
        r.append(1e2 * max(0.0, o["y126"] - self.y_max))
        r.append(1e2 * max(0.0, o["x_lo"] - o["x_hi"]))
        return np.asarray(r, dtype=float)

    def chi2_parts(self, p: np.ndarray) -> dict[str, float]:
        r = self.residuals(p)
        return {"chi2_fermion": float(r[:13] @ r[:13]),
                "chi2_nuisance": float(r[13:16] @ r[13:16]),
                "penalty": float(r[16:] @ r[16:]),
                "chi2_total": float(r @ r)}


# ---------------------------------------------------------------------------
# v20 structural audit
# ---------------------------------------------------------------------------
def v20_release_ansatz_audit() -> dict[str, Any]:
    """The v20 ansatz forces M_u = tan(beta) M_d and hence V_CKM = 1."""
    rng = np.random.default_rng(20)
    worst_offdiag = 0.0
    worst_identity = 0.0
    for _ in range(25):
        params = rng.normal(size=13)
        params[12] = rng.uniform(-14.0, -6.0)
        data = flavour.build_matrices(params, flavour.VS)
        pred = data["M_u_pred"]
        offdiag = np.max(np.abs(pred - np.diag(np.diag(pred))))
        worst_offdiag = max(worst_offdiag, float(offdiag / max(np.max(np.abs(pred)), 1e-300)))
        ratio = np.diag(pred).real / np.diag(data["M_d"]).real
        worst_identity = max(worst_identity, float(np.max(np.abs(ratio - data["tan_beta"]))
                                                   / data["tan_beta"]))

    targets = flavour.QUARK_LEPTON
    mu = np.diag([targets["m_u"], targets["m_c"], targets["m_t"]])
    md = np.diag([targets["m_d"], targets["m_s"], targets["m_b"]])
    tan_beta = 20.0
    total = float(np.linalg.norm(mu - tan_beta * md) / np.linalg.norm(mu))
    top_only = float(abs(targets["m_t"] - tan_beta * targets["m_b"]) / np.linalg.norm(mu))

    import global_flavour_fit_v20 as global_fit

    circular = rng.normal(size=13)
    circular[12] = -10.0
    circular[8] = math.atanh(2 * (global_fit.CKM_SOFT["sin_theta12"][0] / 0.25) - 1)
    circular[9] = math.atanh(2 * (global_fit.CKM_SOFT["sin_theta23"][0] / 0.05) - 1)
    circular[10] = math.atanh(2 * (global_fit.CKM_SOFT["sin_theta13"][0] / 0.01) - 1)
    pulls = global_fit.ckm_pulls_from_params(circular)
    data = flavour.build_matrices(circular, flavour.VS)
    _, u_pred = flavour.takagi(data["M_u_pred"])
    c = u_pred.conj().T
    model_ckm = [abs(c[0, 1]), abs(c[1, 2]), abs(c[0, 2])]

    return {
        "identity": "H + F = M_d / v_d  =>  M_u = tan(beta) * M_d  (matrix identity)",
        "max_relative_offdiagonal_of_predicted_M_u": worst_offdiag,
        "max_relative_violation_of_mass_ratio_identity": worst_identity,
        "predicted_V_CKM": "identity",
        "mismatch_metric_at_tan_beta_20": {"total": total, "top_entry_only": top_only},
        "global_flavour_fit_v20_ckm_pull_chi2_at_nuisance_match": float(pulls["chi2"]),
        "model_ckm_at_same_point": {"V_us": model_ckm[0], "V_cb": model_ckm[1], "V_ub": model_ckm[2]},
    }


# ---------------------------------------------------------------------------
# Witness revalidation
# ---------------------------------------------------------------------------
V20_WITNESS_CONSUMERS = (
    "push_phenomenology_limits_v20.py",
    "channel_fcnc_rates_v20.py",
    "common_scale_so10_yukawa_v20.py",
    "pati_salam_yukawa_matching_v20.py",
    "physical_cf_matching_v20.py",
    "sarah_pyrate_so10_210_betas_v20.py",
    "two_loop_matrix_flavour_rg_ps_v20.py",
    "two_loop_so10_210_yukawa_v20.py",
    "yukawa_rge_2loop_v20.py",
)


def v20_downstream_contamination() -> dict[str, Any]:
    """The downstream flavour basis is built from the v20 *target* matrix.

    ``push_phenomenology_limits_v20.flavour_sector_bases`` diagonalises
    ``M_u_target``, which carries the free nuisance rotation, rather than the
    model's ``M_u_pred``. The resulting quark mixing is therefore neither the
    model prediction (the identity) nor the measured CKM, and it is propagated
    with ``tan_beta`` into the FCNC and two-loop RG layers.
    """
    report = flavour.run_fit()
    best = report["best_overall"]
    data = flavour.build_matrices(np.asarray(best["params"], dtype=float), best["v_r_GeV"])
    u_up = np.linalg.svd(np.asarray(data["M_u_target"], dtype=complex))[0]
    u_down = np.linalg.svd(np.asarray(data["M_d"], dtype=complex))[0]
    v = u_up.conj().T @ u_down
    downstream = {"V_us": float(abs(v[0, 1])), "V_cb": float(abs(v[1, 2])),
                  "V_ub": float(abs(v[0, 2]))}
    _, u_pred = _takagi(data["M_u_pred"])
    c = u_pred.conj().T
    predicted = {"V_us": float(abs(c[0, 1])), "V_cb": float(abs(c[1, 2])),
                 "V_ub": float(abs(c[0, 2]))}
    measured = {"V_us": CKM_LOW["s12"][0], "V_cb": CKM_LOW["s23"][0], "V_ub": CKM_LOW["s13"][0]}
    return {
        "consumers": list(V20_WITNESS_CONSUMERS),
        "downstream_quark_mixing": downstream,
        "model_predicted_quark_mixing": predicted,
        "measured_quark_mixing": measured,
        "downstream_tan_beta": float(data["tan_beta"]),
        "downstream_v_R_GeV": float(best["v_r_GeV"]),
        "note": ("the downstream basis matches neither the prediction nor the data; "
                 "every coefficient fixed with it has to be recomputed"),
    }


def flavour_v21_bases(tan_beta: float = 10.0) -> dict[str, Any]:
    """Drop-in replacement for the contaminated v20 downstream flavour basis.

    Same keys as ``physical_cf_matching_v20.flavour_mass_bases`` and
    ``push_phenomenology_limits_v20.flavour_sector_bases``, but the quark
    rotations come from the PREDICTED ``M_u`` instead of the nuisance-rotated
    target. ``H`` and ``F`` are divided by ``v_d`` to match the v20 convention.
    """
    witnesses = json.loads(WITNESSES.read_text(encoding="utf-8"))
    entry = [w for w in witnesses["benchmark_fits"]
             if w["tan_beta"] == tan_beta and w["label"] == "Ymax=1"][0]
    st = Stratum(tan_beta, entry["v_R"], **entry.get("config", {}))
    p = np.asarray(entry["x"])
    b = st.build(p)
    _s_nu, u_nu = _takagi(b["mnu"])
    _s_e, u_e = _takagi(b["me"])
    u_u, s_u, vh_u = np.linalg.svd(np.asarray(b["mu"], dtype=complex), full_matrices=True)
    u_d, s_d, vh_d = np.linalg.svd(np.asarray(b["md"], dtype=complex), full_matrices=True)
    chi2 = st.chi2_parts(p)["chi2_fermion"]
    return {
        "tan_beta": float(tan_beta), "v_r_GeV": float(entry["v_R"]), "chi2": float(chi2),
        "U_e": u_e, "U_nu": u_nu, "U_uL": u_u, "U_uR": vh_u.conj().T,
        "U_dL": u_d, "U_dR": vh_d.conj().T,
        "H": np.asarray(b["H"]) / st.vd, "F": np.asarray(b["F"]) / st.vd,
        "v_u": st.vu, "v_d": st.vd,
        "m_u": [float(x) for x in s_u], "m_d": [float(x) for x in s_d],
        "natural_scale_viable": bool(chi2 < 30.0),
        "fit_note": "v21 general Yukawa witness; quark rotations from the predicted M_u.",
    }


def _mixing_in_svd_order(bases: dict[str, Any]) -> dict[str, float]:
    """|U_uL^dag U_dL| in the descending-mass ordering these bases use.

    Row/column 0 is the third generation, so the entries are |V_ts|, |V_cd|,
    |V_td| (measured 0.0413, 0.2245, 0.0086).
    """
    v = np.asarray(bases["U_uL"]).conj().T @ np.asarray(bases["U_dL"])
    return {"V_ts": float(abs(v[0, 1])), "V_cd": float(abs(v[1, 2])), "V_td": float(abs(v[0, 2]))}


def downstream_basis_comparison() -> dict[str, Any]:
    """What the nine consumers get now, versus the corrected basis."""
    report = flavour.run_fit()
    best = report["best_overall"]
    data = flavour.build_matrices(np.asarray(best["params"], dtype=float), best["v_r_GeV"])
    v20 = {"U_uL": np.linalg.svd(np.asarray(data["M_u_target"], dtype=complex))[0],
           "U_dL": np.linalg.svd(np.asarray(data["M_d"], dtype=complex))[0]}
    return {
        "ordering": "SVD descending; entries are |V_ts|, |V_cd|, |V_td|",
        "measured": {"V_ts": 0.0413, "V_cd": 0.22452, "V_td": 0.00857},
        "v20_nuisance_basis": _mixing_in_svd_order(v20),
        "v21_predicted_basis": {str(tb): _mixing_in_svd_order(flavour_v21_bases(tb))
                                for tb in (3.0, 10.0, 25.0, 45.0)},
        "note": ("the v20 basis carries no Cabibbo angle (|V_cd| = 2e-4 against 0.2245); "
                 "the v21 prediction reproduces it for every tan(beta)"),
    }


def fine_tuning(st: Stratum, p: np.ndarray) -> tuple[float, list[float]]:
    """Cancellation measure: sum of |seesaw contributions| over |m_nu|.

    1 means no cancellation. The observed light masses are reproduced only
    through a cancellation between the Type-II term and the individual
    right-handed-neutrino contributions.
    """
    b = st.build(p)
    d, w = flavour.takagi(0.5 * (b["mR"] + b["mR"].T))
    y = w.conj().T @ (b["mD"].T / st.vu)
    parts = [np.linalg.norm(b["eps"] * b["F"])]
    parts += [np.linalg.norm(st.vu ** 2 * np.outer(y[i], y[i]) / d[i]) for i in range(len(d))]
    return float(sum(parts) / max(np.linalg.norm(b["mnu"]), 1e-300)), [float(v) for v in d]


def _stratum_for(entry: dict[str, Any], *, planck: bool = True, inverted: bool = False) -> Stratum:
    return Stratum(entry["tan_beta"], entry["v_R"], planck=planck, inverted=inverted,
                   **entry.get("config", {}))


def revalidate_witnesses(witnesses: dict[str, Any]) -> dict[str, Any]:
    benchmark = []
    for entry in witnesses["benchmark_fits"]:
        st = _stratum_for(entry)
        p = np.asarray(entry["x"])
        parts = st.chi2_parts(p)
        o = st.observables(p)
        tune, _ = fine_tuning(st, p)
        benchmark.append({"label": entry["label"], "tan_beta": entry["tan_beta"], "v_R": entry["v_R"],
                          "config": entry.get("config", {}), **parts,
                          "sum_mnu_eV": o["lep"]["sum_mnu_eV"], "y126": o["y126"],
                          "rho": o["build"]["rho"], "fine_tuning": tune,
                          "sum_rule_margin": o["x_hi"] - o["x_lo"]})
    high = witnesses["disfavoured_high_vR"]
    st = _stratum_for(high)
    p = np.asarray(high["x"])
    o = st.observables(p)
    high_row = {"tan_beta": high["tan_beta"], "v_R": high["v_R"], **st.chi2_parts(p),
                "rho": o["build"]["rho"], "sum_rule_margin": o["x_hi"] - o["x_lo"]}

    window = []
    for entry in witnesses["sum_mnu_window"]:
        st = _stratum_for(entry, planck=False)
        p = np.asarray(entry["x"])
        o = st.observables(p)
        window.append({"target_eV": entry["target_eV"], "sum_mnu_eV": o["lep"]["sum_mnu_eV"],
                       "chi2_fermion": st.chi2_parts(p)["chi2_fermion"],
                       "m_bb_eV": o["m_bb_eV"], "masses_eV": o["lep"]["mnu_eV"],
                       "restarts_reaching_chi2_below_16": entry["restarts_reaching_chi2_below_16"]})

    inverted = []
    for entry in witnesses["inverted_ordering"]:
        st = _stratum_for(entry, inverted=True)
        p = np.asarray(entry["x"])
        inverted.append({"tan_beta": entry["tan_beta"], "v_R": entry["v_R"],
                         "chi2_fermion": st.chi2_parts(p)["chi2_fermion"],
                         "restarts": entry["restarts"],
                         "restarts_reaching_chi2_below_16": entry["restarts_reaching_chi2_below_16"]})
    return {"benchmark": benchmark, "high_vR": high_row, "sum_mnu_window": window,
            "inverted_ordering": inverted}


def build_report() -> dict[str, Any]:
    witnesses = json.loads(WITNESSES.read_text(encoding="utf-8"))
    rg = rg_validation()
    audit = v20_release_ansatz_audit()
    wit = revalidate_witnesses(witnesses)
    contamination = v20_downstream_contamination()
    basis_fix = downstream_basis_comparison()
    impact = witnesses.get("downstream_impact", {})
    closure = witnesses.get("optimiser_closure", {})

    at_benchmark = [w for w in wit["benchmark"] if abs(w["v_R"] - BENCHMARK_VR) / BENCHMARK_VR < 1e-6]
    good = [w for w in at_benchmark if w["chi2_fermion"] < 0.05 and w["penalty"] < 1e-6]
    strict_y = [w for w in good if w["config"].get("y_max") == 1.0]
    strict_err = [w for w in good if w["config"].get("floor") == 0.0]
    inside = [w for w in wit["sum_mnu_window"] if w["chi2_fermion"] < 0.05]
    outside = [w for w in wit["sum_mnu_window"] if w["chi2_fermion"] >= 4.0]
    lo_edge = max((w["sum_mnu_eV"] for w in outside if w["target_eV"] < 0.065), default=None)
    hi_edge = min((w["sum_mnu_eV"] for w in outside if w["target_eV"] > 0.070), default=None)
    window_eV = [min(w["sum_mnu_eV"] for w in inside), max(w["sum_mnu_eV"] for w in inside)] if inside else None
    study = witnesses.get("threshold_study", {})
    thr_refits = [d for d in study.get("refits", []) if d["chi2_fermion"] < 15.0]
    thr_window = ([min(d["sum_mnu_eV"] for d in thr_refits), max(d["sum_mnu_eV"] for d in thr_refits)]
                  if thr_refits else None)
    thr_edges = study.get("forced_edges", [])
    thr_io = [d["chi2_fermion"] for d in study.get("inverted_ordering_refits", [])]
    natural = study.get("natural_search", [])
    tunings = [w["fine_tuning"] for w in at_benchmark]
    io_min = min(w["chi2_fermion"] for w in wit["inverted_ordering"])
    io_closure = closure.get("inverted_ordering", {})
    io_rate = float(io_closure.get("fraction_chi2_below_1", 0.0))
    io_closure_ok = io_rate >= 0.02
    # Probability that multistart misses an inverted-ordering basin as easy to
    # reach as the closure-test one: per tan(beta) stratum, and in all strata.
    io_miss_per_stratum = [(1.0 - io_rate) ** w["restarts"] for w in wit["inverted_ordering"]]
    io_miss_all = float(np.prod(io_miss_per_stratum)) if io_miss_per_stratum else 1.0

    checks = {
        "rg_quarks_within_2_percent_of_huang_zhou": rg["max_abs_quark_deviation"] < 0.02,
        "rg_leptons_within_2_percent_of_huang_zhou": rg["max_abs_lepton_deviation"] < 0.02,
        "rg_gauge_within_1_percent_of_huang_zhou": rg["max_abs_gauge_deviation"] < 0.01,
        "v20_ansatz_predicted_M_u_is_diagonal": audit["max_relative_offdiagonal_of_predicted_M_u"] < 1e-12,
        "v20_ansatz_mass_ratio_identity_exact": audit["max_relative_violation_of_mass_ratio_identity"] < 1e-9,
        "v20_mismatch_metric_is_top_dominated": abs(audit["mismatch_metric_at_tan_beta_20"]["total"]
                                                     - audit["mismatch_metric_at_tan_beta_20"]["top_entry_only"]) < 1e-3,
        "v20_global_ckm_pulls_pass_while_model_ckm_vanishes": (
            audit["global_flavour_fit_v20_ckm_pull_chi2_at_nuisance_match"] < 1e-9
            and max(audit["model_ckm_at_same_point"].values()) < 1e-12),
        "general_sector_fits_at_benchmark": len(good) >= 3,
        "general_sector_fits_with_all_yukawas_at_most_one": len(strict_y) >= 2,
        "general_sector_fits_with_experimental_errors_only": len(strict_err) >= 1,
        "benchmark_witnesses_satisfy_sum_rules": all(w["sum_rule_margin"] >= 0 for w in good),
        "high_vR_1e14_violates_sum_rule_at_tan_beta_10": wit["high_vR"]["sum_rule_margin"] < 0,
        "sum_mnu_window_has_both_edges": lo_edge is not None and hi_edge is not None and bool(inside),
        "inverted_ordering_fails_real_data": io_min > 100.0,
        "seesaw_requires_large_cancellation": bool(tunings) and min(tunings) > 20.0,
        "no_acceptable_fit_without_cancellation": bool(natural) and min(
            d["chi2_fermion"] for d in natural) > 100.0,
        "threshold_refits_reproduce_the_sum_mnu_window": bool(thr_refits) and all(
            0.060 <= d["sum_mnu_eV"] <= 0.076 for d in thr_refits),
        "threshold_forced_edges_still_cost_chi2": bool(thr_edges) and all(
            d["chi2_fermion"] > 20.0 for d in thr_edges),
        "inverted_ordering_still_fails_with_thresholds": bool(thr_io) and min(thr_io) > 100.0,
        "v20_downstream_mixing_is_a_nuisance_artifact": (
            max(contamination["model_predicted_quark_mixing"].values()) < 1e-12
            and abs(contamination["downstream_quark_mixing"]["V_us"]
                    - contamination["measured_quark_mixing"]["V_us"]) > 0.05),
        "v20_basis_misses_the_cabibbo_angle": basis_fix["v20_nuisance_basis"]["V_cd"] < 0.01,
        "v21_basis_reproduces_the_cabibbo_angle": all(
            abs(m["V_cd"] - basis_fix["measured"]["V_cd"]) / basis_fix["measured"]["V_cd"] < 0.05
            for m in basis_fix["v21_predicted_basis"].values()),
        "corrected_basis_changes_downstream_fcnc_rates": bool(impact) and max(
            d["ratio"] for d in impact["mu_to_e_a_branching_ratio"].values()) > 10.0,
        "tan_beta_not_determined_by_fermion_data": (
            max(w["tan_beta"] for w in good) / min(w["tan_beta"] for w in good) > 5.0
            if good else False),
    }
    failures = [k for k, v in checks.items() if not v]
    normal_ordering_required = bool(checks["inverted_ordering_fails_real_data"] and io_closure_ok)

    return {
        "status": ("FLAVOUR_GENERAL_YUKAWA_V21_PASS__BENCHMARK_CONSISTENT__NOT_UNIQUE"
                   if not failures else "FLAVOUR_GENERAL_YUKAWA_V21_FAIL"),
        "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "checks": checks,
        "rg_validation": rg,
        "v20_structural_audit": audit,
        "witnesses": wit,
        "optimiser_closure": closure,
        "v20_downstream_contamination": contamination,
        "downstream_basis_fix": {**basis_fix, "measured_impact": impact},
        "threshold_study": study,
        "fine_tuning": {
            "measure": "sum of |seesaw contributions| / |m_nu| at M_I; 1 means no cancellation",
            "at_benchmark_witnesses": tunings,
            "after_threshold_refit": [d["tuning"] for d in thr_refits],
            "best_chi2_fermion_when_cancellation_is_capped": {
                str(d["T0"]): d["chi2_fermion"] for d in natural},
        },
        "predictions": {
            "sum_mnu_window_eV": window_eV,
            "sum_mnu_window_eV_threshold_aware": thr_window,
            "sum_mnu_excluded_below_eV": lo_edge,
            "sum_mnu_excluded_above_eV": hi_edge,
            "m_bb_eV_range": ([min(w["m_bb_eV"] for w in inside), max(w["m_bb_eV"] for w in inside)]
                              if inside else None),
            "normal_ordering_required": normal_ordering_required,
            "inverted_ordering_best_chi2_fermion": io_min,
            "inverted_ordering_tan_beta_strata": [w["tan_beta"] for w in wit["inverted_ordering"]],
            "inverted_ordering_closure_success_rate": io_rate,
            "inverted_ordering_miss_probability_worst_stratum": float(max(io_miss_per_stratum, default=1.0)),
            "inverted_ordering_miss_probability_all_strata": io_miss_all,
        },
        "flag": {
            "v20_release_ansatz_predicts_identity_ckm": checks["v20_ansatz_predicted_M_u_is_diagonal"],
            "v20_global_fit_ckm_pulls_are_circular": checks["v20_global_ckm_pulls_pass_while_model_ckm_vanishes"],
            "v20_flavour_witness_valid": False,
            "v20_downstream_flavour_basis_contaminated": True,
            "tan_beta_fixed_by_fermion_data": False,
            "corrected_downstream_basis_available": True,
            "downstream_modules_rewired": False,
            "general_yukawa_sector_fits_all_fermion_observables_at_benchmark":
                checks["general_sector_fits_at_benchmark"],
            "ckm_is_a_model_prediction_not_a_nuisance": True,
            "common_scale_RG_inputs_applied": True,
            "two_loop_thresholds_coupled": False,
            # The frozen witnesses are tree-level-matched fits: the thresholds are NOT
            # part of the fit that produced them. They were applied afterwards, and the
            # fit was redone with them, to test whether the predictions survive.
            "right_handed_neutrino_thresholds_included_in_frozen_witnesses": False,
            "right_handed_neutrino_thresholds_applied_in_stability_study": bool(thr_refits),
            "right_handed_neutrino_threshold_stability_checked": bool(thr_refits),
            "sum_mnu_prediction_survives_thresholds": bool(thr_refits) and all(
                0.060 <= d["sum_mnu_eV"] <= 0.076 for d in thr_refits),
            "seesaw_fine_tuning_required": bool(tunings) and min(tunings) > 20.0,
            "heavy_higgs_thresholds_included": False,
            "relative_ckm_pmns_cp_sign_tested": False,
            "unique_fit": False,
            "global_minimum_proved": False,
            "whole_model_validated": False,
        },
        "parameter_count": {"physical_parameters": 14, "nuisance_parameters": 3,
                            "fitted_fermion_observables": 13,
                            "degrees_of_freedom": 13 - 14,
                            "error_model": "diagonal; input correlations (Huang & Zhou Tables 7-8) are not used",
                            "note": "negative dof: exact fits are expected; consistency, not confirmation"},
        "references": {
            "running_masses": "G.-y. Huang and S. Zhou, Phys. Rev. D 103, 016010 (2021)",
            "neutrino_oscillations": "NuFIT 6.0, I. Esteban et al., JHEP 12 (2024) 216, arXiv:2410.05380",
            "ckm": "PDG 2024 Wolfenstein fit",
        },
    }


def write_markdown(report: dict[str, Any]) -> str:
    pred = report["predictions"]
    lines = [
        "# General minimal SO(10) 10+126 Yukawa sector - v21",
        "",
        f"**Status:** `{report['status']}`  ",
        f"**Checks:** {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed",
        "",
        "## v20 structural audit",
        "",
        "The v20 ansatz sets `M_u = v_u (H + F)` with `H + F = M_d / v_d`, i.e.",
        "`M_u = tan(beta) M_d` as a matrix identity. It predicts `V_CKM = 1` and",
        "`m_u/m_d = m_c/m_s = m_t/m_b`. The v20 global fit places its CKM pulls on",
        "the nuisance rotation of the target matrix, so they pass while the model",
        "predicts no quark mixing. **The v20 flavour witness is not valid.**",
        "",
        "## General sector at v_R = v_S = 6.31e11 GeV",
        "",
        "| witness | tan(beta) | chi2 fermion | penalty | sum m_nu (eV) | Y126 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for w in report["witnesses"]["benchmark"]:
        lines.append(f"| {w['label']} | {w['tan_beta']:.0f} | {w['chi2_fermion']:.3f} | "
                     f"{w['penalty']:.3f} | {w['sum_mnu_eV']:.4f} | {w['y126']:.3f} |")
    lines += [
        "",
        "## Predictions",
        "",
        f"- sum m_nu window: `{pred['sum_mnu_window_eV']}` eV "
        f"(excluded below `{pred['sum_mnu_excluded_below_eV']}`, above `{pred['sum_mnu_excluded_above_eV']}`)",
        f"- m_bb range: `{pred['m_bb_eV_range']}` eV",
        f"- normal ordering required: `{pred['normal_ordering_required']}` "
        f"(best inverted-ordering chi2 = {pred['inverted_ordering_best_chi2_fermion']:.1f})",
        "",
        "## Claim boundary",
        "",
        "14 physical parameters fit 13 observables, so an exact fit shows consistency,",
        "not confirmation. Right-handed-neutrino, heavy-Higgs and two-loop threshold",
        "effects are not included. No uniqueness or global minimum is claimed.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, default=float) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "n_failed": report["n_failed"],
                      "failures": report["failures"], "predictions": report["predictions"]},
                     indent=2, default=float))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
