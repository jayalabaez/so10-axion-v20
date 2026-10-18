"""D2 stage 3: full 18-observable fit of the one-step O5-EFT model (d2_eft_fit.model, sigma != 0 allowed) seeded from
the decoupled stage-1 charged solutions + a type-I inversion for M_R, as a function of the coefficient cap
|S_ij| <= cap (operator coefficient in units of 1/M_Pl,red) and of the Clebsch bounds.

Clebsch normalisation (stated): O5 = S_ij (F_i F_j)_126 (Delta Phi)_126bar / Lambda with (Delta Phi)_126bar the
orthogonal (unit-norm) projection of Delta x Phi, contracted like the renormalizable F.F.Delta (Y126 'def'
normalisation, M_R = C_R v_R Y126).  Then M_R = C_R v_R (Y126 + eps kR' S), F = c_d126 (Y126 + eps kd' S),
up 126-part = c_u126 (Y126 + eps ku' S) + c_phi (v_R/|Phi|) eps lam' S, with projector matrix elements |k'|, |lam'| <= 1:
   tau = C_R (kR' - kd'),  |tau| <= 2 C_R = 9.80 ;  sigma = c_u126 (ku' - kd') + c_phi lam' v_R/|Phi|, |sigma| <= ~1.5.
Settings: 'optimistic' (TAU = 9.8, SIG = 1.5) and 'typical' (TAU = 3, SIG = 0.5).  eps = |Phi|/M_Pl,red with
|Phi| = 2.7 M_U (R2-C/R2-A vector-mass relation): chain a (M_U = 1.02e16) 0.0113, chain b (M_U = 2.16e16) 0.024.
usage: python -B d2_joint.py <decoupled.json> <chain> <out.json>
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from scipy.optimize import least_squares

import lib_flav as L
import d2_targets as TG
import d2_eft_fit as E
import d2_decoupled as Dc

C_R = E.C_R


def logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def seed_full(x1, tg, vR, eps_eff, nu, tau_phase=0.0):
    """Build a 35-vector for d2_eft_fit.model from a charged solution x1 (18) and neutrino params nu (dict from
    minimise_Q): c_d126 -> 0.98 c_max, tau = TAU e^{i phase}, sigma = 0, K = (M_R/v_R - C_R F/c_d126)/tau clipped."""
    m = Dc.charged_mats(x1, tg)
    x = np.zeros(E.NPAR)
    x[0:12] = x1[0:12]; x[29:35] = x1[12:18]
    cmax = math.sqrt(E.CMAX2 / (1 + abs(m["rho"]) ** 2))
    cd = min(nu["c_d126"], 0.98 * cmax)
    x[28] = logit(cd / cmax)
    x[12] = -12.0; x[13] = 0.0                                     # sigma ~ 0
    tau = E.TAU * 0.999 * np.exp(1j * tau_phase)
    x[14] = logit(0.999); x[15] = tau_phase
    y = np.array([math.log10(nu["m1_eV"]), nu["a21"], nu["a31"], nu["delta_pmns"]] + list(nu["nu_pulls"]))
    MR, _ = Dc.required_MR(m, tg, y, tg["data"])
    K = (MR / vR - C_R * m["F"] / cd) / tau
    for n, (i, j) in enumerate(E.SYM):
        v = K[i, j]
        x[16 + 2 * n] = logit(min(abs(v) / eps_eff, 0.999)); x[17 + 2 * n] = math.atan2(v.imag, v.real)
    return x


def fit_full(x0, tg, vR, eps_eff, nfev=6000):
    f = lambda z: E.residuals(z, tg, vR, "o5", eps_eff)
    s = least_squares(f, x0, method="trf", max_nfev=nfev, xtol=1e-12, ftol=1e-12, x_scale="jac")
    return s.x, float(s.fun @ s.fun)


def main():
    dec, chain, out = sys.argv[1], sys.argv[2], sys.argv[3]
    D = json.load(open(dec, encoding="utf-8"))
    tg = TG.gut_targets(chain, floor=D["floor"])
    eps = {"a": 0.0113, "b": 0.024}[chain]
    t0 = time.time()
    res = {"chain": chain, "eps": eps, "runs": []}
    seeds = []
    for key in ("300.0", "30.0"):
        for row in D["stage1"][key][:1]:
            if row["chi2_13"] < 10:
                seeds.append((key, row))
    for setting, (TAU, SIG) in (("optimistic", (9.8, 1.5)), ("typical", (3.0, 0.5))):
        E.TAU, E.SIG = TAU, SIG
        for vR in (1e15, 3e15, 1e16):
            for cap in (0.5, 1.0, 2.0, 4.0):
                eps_eff = cap * eps
                best = (1e18, None)
                for key, row in seeds:
                    x1 = np.array(row["x"])
                    m = Dc.charged_mats(x1, tg)
                    nu = Dc.minimise_Q(m, tg, vR, tg["data"], TAU, eps_eff, seed=1, nstart=12)
                    for ph in (0.0, math.pi):
                        x0 = seed_full(x1, tg, vR, eps_eff, nu, ph)
                        c0 = float(E.residuals(x0, tg, vR, "o5", eps_eff) @ E.residuals(x0, tg, vR, "o5", eps_eff))
                        x, c = fit_full(x0, tg, vR, eps_eff)
                        if c < best[0]:
                            best = (c, x, c0, nu["Q"], key)
                c, x, c0, Q, key = best
                summ = E.summarize(x, tg, vR, "o5", eps_eff)
                summ["max|S|"] = summ["max|K|/eps"] * cap
                rec = {"setting": setting, "TAU": TAU, "SIG": SIG, "vR": vR, "cap": cap, "chi2": c, "chi2_seed": c0,
                       "Q_decoupled(sigma=0)": Q, "seed_rho_max": key, "best": summ}
                res["runs"].append(rec)
                print(f"[{chain} {setting}] vR={vR:.0e} cap={cap}: chi2 = {c:9.3f} (seed {c0:.1f}, Q(sigma=0) = {Q:.2f}) "
                      f"max|S| = {summ['max|S|']:.3f} |sigma| = {abs(complex(*summ['sigma'])):.3f} |tau| = {abs(complex(*summ['tau'])):.2f} "
                      f"c_d126 = {summ['c_d126']:.4f} |rho| = {math.hypot(*summ['rho']):.1f} M_R = {np.array(summ['M_R_GeV'])} "
                      f"cancel = {summ['MR/MR_renorm_norm_ratio']:.3g} n>3 = {summ['n_pull_gt3']} t={time.time() - t0:.0f}s", flush=True)
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
