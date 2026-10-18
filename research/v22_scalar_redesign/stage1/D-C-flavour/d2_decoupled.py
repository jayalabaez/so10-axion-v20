"""D2 decisive proxy for the one-step designs, decoupled form (replaces the brute-force 35-parameter DE of d2_eft_fit.py,
which converged poorly; the model is identical).

Logic (EXACT given the model of d2_eft_fit.py with sigma = 0):
  charged sector  : Yd = H + F (pinned eigenvalues), Ye = H - 3F, Yu = r H + rho F  -> 13 observables
                    (9 masses, 4 CKM) depend only on (W, r, rho, mass offsets);
  neutrino sector : Ynu = r H - 3 rho F is then fixed; ANY light-neutrino matrix m_nu consistent with the data is
                    obtained from  M_R = -v^2 Ynu^T m_nu^-1 Ynu  (type-I inversion), so chi2_nu = 0 is always
                    reachable when M_R is free.  In the model M_R = v_R (C_R F / c_d126 + tau K), so the inversion is
                    realisable iff  |K_ij| = |M_R,ij / v_R - C_R F_ij / c_d126| / |tau| <= eps  for some admissible
                    c_d126 <= c_max(rho) = sqrt(0.9 / (1 + |rho|^2)) and Clebsch |tau| <= TAU.
  Feasibility ratio Q = min over (c_d126, m1, Majorana phases, delta_PMNS) of max_ij |M_R/v_R - C_R F/c_d126|_ij / (TAU eps).
  Q <= 1  <=>  the O5 operator with |S_ij| <= 1 makes the whole 18-observable fit equal to the charged-sector fit.
  The renormalizable model is the special case K = 0 (requires the M_R ~ F relation exactly).
Stage 1: map chi2_13,min as a function of an upper bound rho_max on |rho| (DE, batched, + TRF polish).
Stage 2: for the best charged solutions, minimise Q at v_R = 1e15, 3e15, 1e16 and record M_R and the cancellation
         ratio ||M_R/v_R|| / ||C_R F/c_d126|| (<< 1 means the d=5 term cancels the renormalizable one = a coincidence).
usage: python -B d2_decoupled.py <chain a|b> <out.json> [nseeds] [floor]
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from scipy.optimize import differential_evolution, least_squares, minimize

import lib_flav as L
import d2_targets as TG
from d2_eft_fit import angles1, umix1

V = L.VEV
C_R = 2 * math.sqrt(6)
CMAX2 = 0.9
NP = 18
CH = list(range(13))     # observable indices 0..12 (masses + CKM)


def W_of(x):
    U = umix1(x[0], x[1], x[2], x[3])
    P1 = np.exp(1j * np.array([x[4], x[5], 0.0])); P2 = np.exp(1j * np.array([x[6], x[7], x[8]]))
    return P1[:, None] * U * P2[None, :]


def charged_mats(x, tg):
    W = W_of(x)
    sd = tg["sd0"] * np.exp(x[12:15]); se = tg["se0"] * np.exp(x[15:18])
    Yd = np.diag(sd).astype(complex); Ye = (W * se[None, :]) @ W.T
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0 ** x[9]; rho = 10.0 ** x[10] * np.exp(1j * x[11])
    Yu = r * H + rho * F
    return dict(W=W, sd=sd, se=se, H=H, F=F, r=r, rho=rho, Yu=Yu, Yn=r * H - 3 * rho * F)


def charged_res(x, tg):
    m = charged_mats(x, tg)
    w, Eu = np.linalg.eigh(m["Yu"] @ m["Yu"].conj().T)
    mu = np.sqrt(np.clip(w, 0, None)) * V
    s12, s23, s13, d = angles1(Eu.T)
    o = np.concatenate([mu, m["sd"] * V, m["se"] * V, [s12, s23, s13, abs(d)]])
    T, S = tg["T"], tg["S"]
    R = np.empty(13)
    for i in range(13):
        if i < 9:
            R[i] = math.log(max(o[i], 1e-300) / T[i]) * T[i] / S[i]
        elif i == 12:
            R[i] = ((o[i] - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        else:
            R[i] = (o[i] - T[i]) / S[i]
    return np.where(np.isfinite(R), R, 1e3)


def charged_batch(X, tg):
    N = X.shape[0]
    U0 = L.umix_b(X[:, 0], X[:, 1], X[:, 2], X[:, 3])
    P1 = np.exp(1j * np.stack([X[:, 4], X[:, 5], np.zeros(N)], 1)); P2 = np.exp(1j * X[:, 6:9])
    W = P1[:, :, None] * U0 * P2[:, None, :]
    sd = tg["sd0"][None] * np.exp(X[:, 12:15]); se = tg["se0"][None] * np.exp(X[:, 15:18])
    Yd = np.zeros((N, 3, 3), complex); Yd[:, [0, 1, 2], [0, 1, 2]] = sd
    Ye = (W * se[:, None, :]) @ np.swapaxes(W, 1, 2)
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0 ** X[:, 9]; rho = 10.0 ** X[:, 10] * np.exp(1j * X[:, 11])
    Yu = r[:, None, None] * H + rho[:, None, None] * F
    w, Eu = np.linalg.eigh(Yu @ L.herm(Yu))
    mu = np.sqrt(np.clip(w, 0, None)) * V
    s12, s23, s13, d = L.angles_b(np.swapaxes(Eu, 1, 2))
    o = np.concatenate([mu, sd * V, se * V, np.stack([s12, s23, s13, np.abs(d)], 1)], 1)
    T, S = tg["T"], tg["S"]
    R = np.empty((N, 13))
    R[:, :9] = np.log(np.clip(o[:, :9], 1e-300, None) / T[None, :9]) * T[None, :9] / S[None, :9]
    R[:, 9:12] = (o[:, 9:12] - T[None, 9:12]) / S[None, 9:12]
    R[:, 12] = ((o[:, 12] - T[12] + math.pi) % (2 * math.pi) - math.pi) / S[12]
    R = np.where(np.isfinite(R), R, 1e3)
    return np.sum(R * R, 1)


def bnds(rho_max):
    lo = np.array([-math.pi] * 9 + [1.0, -2.5, -math.pi] + [-0.08] * 6)
    hi = np.array([math.pi] * 9 + [2.5, math.log10(rho_max), math.pi] + [0.08] * 6)
    return lo, hi


def fit_charged(tg, rho_max, seed, maxiter=2500, popsize=15):
    lo, hi = bnds(rho_max)
    res = differential_evolution(lambda Xt: charged_batch(Xt.T, tg), list(zip(lo, hi)), popsize=popsize,
                                 maxiter=maxiter, tol=1e-12, seed=seed, polish=False, vectorized=True,
                                 updating="deferred", mutation=(0.5, 1.0), recombination=0.9)
    x = np.clip(res.x, lo + 1e-12, hi - 1e-12)
    s = least_squares(charged_res, x, args=(tg,), bounds=(lo, hi), method="trf", max_nfev=4000, xtol=1e-13, ftol=1e-13)
    c = float(s.fun @ s.fun)
    if c > res.fun:
        return res.x, float(res.fun)
    return s.x, c


# ------------------------------------------------------------------------------------------------- neutrino side
def pmns(s12sq, s23sq, s13sq, d, a21, a31):
    U = umix1(math.asin(math.sqrt(s12sq)), math.asin(math.sqrt(s13sq)), math.asin(math.sqrt(s23sq)), d)
    return U * np.exp(1j * np.array([0.0, a21 / 2, a31 / 2]))[None, :]


def required_MR(m, tg, y, data):
    """y = (log10 m1[eV], a21, a31, delta, pulls of the 5 nu observables (sin^2 x3, dm21, dm31))."""
    m1 = 10.0 ** y[0]
    s12 = data["sin2_th12"][0] + y[4] * data["sin2_th12"][1]
    s23 = data["sin2_th23"][0] + y[5] * data["sin2_th23"][1]
    s13 = data["sin2_th13"][0] + y[6] * data["sin2_th13"][1]
    dm21 = data["dm21"][0] + y[7] * data["dm21"][1]; dm31 = data["dm31"][0] + y[8] * data["dm31"][1]
    if not (0 < s12 < 1 and 0 < s23 < 1 and 0 < s13 < 1) or dm21 <= 0 or dm31 <= 0:
        return None, None
    mn = np.array([m1, math.sqrt(m1 ** 2 + dm21), math.sqrt(m1 ** 2 + dm31)]) * 1e-9 / tg["eta"]   # GeV at M_U
    U = pmns(s12, s23, s13, y[3], y[1], y[2])
    W = m["W"]
    mnu = W @ U.conj() @ np.diag(mn) @ U.conj().T @ W.T
    try:
        MR = -(V ** 2) * m["Yn"].T @ np.linalg.solve(mnu, m["Yn"])
    except np.linalg.LinAlgError:
        return None, None
    return MR, float(np.sum(np.array(y[4:9]) ** 2))


def Q_of(m, tg, vR, y, lcd, data, tau_max, eps):
    MR, chi2nu = required_MR(m, tg, y, data)
    if MR is None:
        return 1e9, None
    cmax = math.sqrt(CMAX2 / (1 + abs(m["rho"]) ** 2))
    cd = cmax / (1 + math.exp(-lcd))
    D = MR / vR - C_R * m["F"] / cd
    return float(np.abs(D).max() / (tau_max * eps)), dict(MR=MR, cd=cd, chi2nu=chi2nu, D=D)


def minimise_Q(m, tg, vR, data, tau_max, eps, seed=0, nstart=40, pull_cap=1.0):
    """minimise Q over (log m1, a21, a31, delta, lcd) with the nu observables allowed to move within |pull| <= pull_cap."""
    rng = np.random.default_rng(seed)
    best = (1e18, None, None)

    def f(z):
        y = np.concatenate([z[:4], np.clip(z[5:10], -pull_cap, pull_cap)])
        q, _ = Q_of(m, tg, vR, y, z[4], data, tau_max, eps)
        return q
    for k in range(nstart):
        z0 = np.array([rng.uniform(-4.5, -1.3), rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi),
                       rng.uniform(0, 2 * math.pi), rng.uniform(-2, 8)] + list(rng.uniform(-0.5, 0.5, 5)))
        r = minimize(f, z0, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-9, fatol=1e-12))
        if r.fun < best[0]:
            best = (float(r.fun), r.x, None)
    z = best[1]
    y = np.concatenate([z[:4], np.clip(z[5:10], -pull_cap, pull_cap)])
    q, info = Q_of(m, tg, vR, y, z[4], data, tau_max, eps)
    MR = info["MR"]
    mR = np.sort(np.linalg.svd(MR, compute_uv=False))
    ren = vR * C_R * m["F"] / info["cd"]
    return {"Q": q, "c_d126": info["cd"], "c_max": math.sqrt(CMAX2 / (1 + abs(m["rho"]) ** 2)),
            "m1_eV": 10.0 ** z[0], "a21": z[1] % (2 * math.pi), "a31": z[2] % (2 * math.pi), "delta_pmns": z[3] % (2 * math.pi),
            "nu_pulls": np.clip(z[5:10], -pull_cap, pull_cap).tolist(), "chi2_nu": info["chi2nu"],
            "M_R_GeV": mR.tolist(), "cancellation_ratio": float(np.linalg.norm(MR) / np.linalg.norm(ren)),
            "max|D|": float(np.abs(info["D"]).max()), "max|C_R F/c_d126|": float(np.abs(C_R * m["F"] / info["cd"]).max())}


def main():
    chain, out = sys.argv[1], sys.argv[2]
    nseeds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    floor = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    tg = TG.gut_targets(chain, floor=floor)
    data = tg["data"]
    t0 = time.time()
    res = {"chain": chain, "floor": floor, "MU": tg["MU"], "eta": tg["eta"], "stage1": {}, "stage2": {}}
    sols = []
    for rho_max in (300.0, 30.0, 15.0, 10.0, 6.0, 3.0, 1.0):
        rows = []
        for s in range(nseeds):
            x, c = fit_charged(tg, rho_max, 100 + s)
            m = charged_mats(x, tg)
            R = charged_res(x, tg)
            rows.append({"chi2_13": c, "rho_abs": abs(m["rho"]), "r": m["r"], "s=|rho|/r": abs(m["rho"]) / m["r"],
                         "max|F|": float(np.abs(m["F"]).max()), "F_sv": np.sort(np.linalg.svd(m["F"], compute_uv=False)).tolist(),
                         "pulls": dict(zip(L.ALL_KEYS[:13], [float(v) for v in R])), "x": x.tolist()})
            sols.append((rho_max, c, x))
            print(f"[{chain}] rho_max={rho_max:6.1f} seed {s}: chi2_13 = {c:9.3f}  |rho| = {abs(m['rho']):7.3f}  r = {m['r']:6.2f}  "
                  f"max|F| = {np.abs(m['F']).max():.3e}  t={time.time() - t0:.0f}s", flush=True)
        rows.sort(key=lambda r: r["chi2_13"])
        res["stage1"][str(rho_max)] = rows
    # stage 2: best solution per rho_max with chi2_13 <= 25
    for rho_max in (300.0, 30.0, 15.0, 10.0, 6.0, 3.0, 1.0):
        best = res["stage1"][str(rho_max)][0]
        if best["chi2_13"] > 25:
            continue
        m = charged_mats(np.array(best["x"]), tg)
        res["stage2"][str(rho_max)] = {}
        for vR in (1e15, 3e15, 1e16):
            for tau_max, eps in ((5.0, 0.011), (12.0, 0.024)):
                q = minimise_Q(m, tg, vR, data, tau_max, eps)
                key = f"vR={vR:.0e},TAU={tau_max},eps={eps}"
                res["stage2"][str(rho_max)][key] = q
                print(f"[{chain}] stage2 rho_max={rho_max} chi2_13={best['chi2_13']:.2f} |rho|={best['rho_abs']:.2f} {key}: "
                      f"Q = {q['Q']:.3f}  c_d126 = {q['c_d126']:.3f}/{q['c_max']:.3f}  M_R = {np.array(q['M_R_GeV'])}  "
                      f"cancel = {q['cancellation_ratio']:.3g}  chi2_nu = {q['chi2_nu']:.2f}", flush=True)
    res["seconds"] = time.time() - t0
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
