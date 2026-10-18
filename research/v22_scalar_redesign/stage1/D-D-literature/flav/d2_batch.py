#!/usr/bin/env python3
"""D-D-literature, D2 proxy fit -- batched, near-pinned parametrisation (R2-C 'free-mass' layout + d=5 120-like term).

Layout (all at M_U, doublet-LEFT, units of v = 174.1 GeV):
  S_d = diag(sd0 e^{o_d}),  S_e = W diag(se0 e^{o_e}) W^T     (sd0, se0 = target eigenvalues at M_U; |o| <= 0.5)
  H = (3 S_d + S_e)/4,  F = (S_d - S_e)/4                     (renormalisable 10 + 126bar, symmetric)
  Yd = S_d + A,  Ye = S_e + k_e A,  Yu = r (H + s F + k_u A),  Yn = r (H - 3 s F + k_D A)
  A antisymmetric (d=5, (16 16)_120 (10 210)_120), k_e = (1-3rho)/(1+rho), k_u = (1+eps rho)/(1+rho), k_D = (1-3 eps rho)/(1+rho)
  type I: m_nu = -rho_nu Yn F^-1 Yn^T  (+ t F for the type-II variant)
Physical bounds (see d2_proxy.py docstring): composition normalisation, perturbativity, d=5 coefficient
  c5 = max(|A_1|,|A_15|)/(kappa_Phi c_d10) <= c5max, sigma window [sig_lo, sig_hi] from rho_nu = v^2 c_d126/(C_R sigma).
Search: scipy differential_evolution (vectorised, batched numpy) + least-squares polish of the best members.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lib_r2c as L  # noqa: E402
import d2_proxy as P  # noqa: E402  (targets, error model)

V = L.VEV
C_R = L.C_R
KEYS = L.ALL_KEYS
IM = {k: i for i, k in enumerate(KEYS)}


def herm(M):
    return np.conj(np.swapaxes(M, -1, -2))


def W_batch(X):
    U = L.umix_b(X[:, 0], X[:, 1], X[:, 2], X[:, 3])
    P1 = np.exp(1j * np.stack([X[:, 4], X[:, 5], np.zeros(len(X))], 1))
    P2 = np.exp(1j * X[:, 6:9])
    return P1[:, :, None] * U * P2[:, None, :]


class Problem:
    def __init__(self, T, S, opts):
        self.T, self.S, self.o = T, S, opts
        self.sd0 = T[[3, 4, 5]] / V
        self.se0 = T[[6, 7, 8]] / V
        self.nA = 8 if opts["use_A"] else 0
        self.nt = 2 if opts["typeII"] else 0
        self.n = 18 + self.nA + self.nt
        lo = [-math.pi, -math.pi / 2, -math.pi, -math.pi, -math.pi, -math.pi, -math.pi, -math.pi, -math.pi,
              1.0, -2.5, -math.pi] + [-opts["off"]] * 6
        hi = [math.pi, math.pi / 2, math.pi, math.pi, math.pi, math.pi, math.pi, math.pi, math.pi,
              2.4, 0.6, math.pi] + [opts["off"]] * 6
        if opts["use_A"]:
            lo += [-opts["Arange"]] * 6 + [-3.0, -3.0]
            hi += [opts["Arange"]] * 6 + [3.0, 3.0]
        if opts["typeII"]:
            lo += [-3.0, -math.pi]; hi += [3.0, math.pi]
        self.bounds = list(zip(lo, hi))

    def mats(self, X):
        X = np.atleast_2d(X)
        N = len(X)
        W = W_batch(X)
        sd = self.sd0[None, :] * np.exp(X[:, 12:15]); se = self.se0[None, :] * np.exp(X[:, 15:18])
        Sd = np.zeros((N, 3, 3), complex); Sd[:, [0, 1, 2], [0, 1, 2]] = sd
        Se = (W * se[:, None, :]) @ np.swapaxes(W, 1, 2)
        H = (3 * Sd + Se) / 4; F = (Sd - Se) / 4
        r = 10.0 ** X[:, 9]; s = 10.0 ** X[:, 10] * np.exp(1j * X[:, 11])
        A = np.zeros((N, 3, 3), complex); rho = np.zeros(N); eps = np.zeros(N)
        if self.nA:
            a = X[:, 18:24] * 1e-4
            for k, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
                A[:, i, j] = a[:, 2 * k] + 1j * a[:, 2 * k + 1]; A[:, j, i] = -A[:, i, j]
            rho = X[:, 24]; eps = X[:, 25]
            if self.o.get("eps_fixed") is not None:
                eps = np.full(N, float(self.o["eps_fixed"]))
        eta1 = float(self.o.get("eta1", 1.0))   # up/down ratio of the (1,2,2)_120 channel (p: +1; 45 omega_R: -1)
        den = 1 + rho
        den = np.where(np.abs(den) < 1e-3, 1e-3, den)
        ke, ku, kD = (1 - 3 * rho) / den, (eta1 + eps * rho) / den, (eta1 - 3 * eps * rho) / den
        Yd = Sd + A
        Ye = Se + ke[:, None, None] * A
        Yu = r[:, None, None] * (H + s[:, None, None] * F + ku[:, None, None] * A)
        Yn = r[:, None, None] * (H - 3 * s[:, None, None] * F + kD[:, None, None] * A)
        t = None
        if self.nt:
            i0 = 18 + self.nA
            t = 10.0 ** X[:, i0] * np.exp(1j * X[:, i0 + 1])
        return dict(H=H, F=F, A=A, rho=rho, eps=eps, r=r, s=s, t=t, Yd=Yd, Ye=Ye, Yu=Yu, Yn=Yn)

    def evaluate(self, X, want=False):
        M = self.mats(X)
        N = M["Yu"].shape[0]
        T, S = self.T, self.S
        Yb = np.stack([M["Yu"], M["Yd"], M["Ye"]], 1)
        w, E = np.linalg.eigh(Yb @ herm(Yb))
        sv = np.sqrt(np.clip(w, 0, None)) * V
        Eu, Ed, Ee = E[:, 0], E[:, 1], E[:, 2]
        CKM = np.swapaxes(Eu, 1, 2) @ np.conj(Ed)
        c12, c23, c13, cd = L.angles_b(CKM)
        F = M["F"]
        bad = np.zeros(N, bool)
        try:
            X1 = np.linalg.solve(F, np.swapaxes(M["Yn"], 1, 2))
        except np.linalg.LinAlgError:
            X1 = np.full((N, 3, 3), np.nan, complex); bad[:] = True
        m1 = -M["Yn"] @ X1
        if self.nt:
            nm1 = np.linalg.norm(m1, axis=(1, 2)); nF = np.linalg.norm(F, axis=(1, 2))
            m1 = m1 + (M["t"] * nm1 / np.where(nF > 0, nF, 1))[:, None, None] * F
        sc = np.abs(m1).max(axis=(1, 2))
        bad |= ~np.isfinite(sc) | (sc <= 0)
        sc = np.where(bad, 1.0, sc)
        m1n = np.where(np.isfinite(m1), m1, 0) / sc[:, None, None]
        wn, Nv = np.linalg.eigh(herm(m1n) @ m1n)
        mn = np.sqrt(np.clip(wn, 0, None))
        U = np.swapaxes(Ee, 1, 2) @ Nv
        n12, n23, n13, nd = L.angles_b(U)
        a21 = mn[:, 1] ** 2 - mn[:, 0] ** 2; a31 = mn[:, 2] ** 2 - mn[:, 0] ** 2
        i21, i31 = IM["dm21"], IM["dm31"]
        num = a21 * T[i21] / S[i21] ** 2 + a31 * T[i31] / S[i31] ** 2
        den = a21 ** 2 / S[i21] ** 2 + a31 ** 2 / S[i31] ** 2
        lam = np.clip(num / np.where(den > 0, den, 1e-300), 1e-300, None)
        obs = np.zeros((N, 18))
        obs[:, 0:3] = sv[:, 0]; obs[:, 3:6] = sv[:, 1]; obs[:, 6:9] = sv[:, 2]
        obs[:, 9] = c12; obs[:, 10] = c23; obs[:, 11] = c13; obs[:, 12] = cd
        obs[:, 13] = n12 ** 2; obs[:, 14] = n23 ** 2; obs[:, 15] = n13 ** 2
        obs[:, 16] = lam * a21; obs[:, 17] = lam * a31
        R = np.empty((N, 18))
        for i, k in enumerate(KEYS):
            if k in L.MASS_KEYS:
                R[:, i] = np.log(np.clip(obs[:, i], 1e-300, None) / T[i]) * T[i] / S[i]
            elif k == "delta":
                R[:, i] = ((np.abs(obs[:, i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
            else:
                R[:, i] = (obs[:, i] - T[i]) / S[i]
        R = np.where(np.isfinite(R), R, 1e3); R[bad] = 1e3
        rho_nu = np.sqrt(lam) * 1e-9 / sc
        D = self.derived(M, rho_nu)
        o = self.o
        pen = np.zeros((N, 3))
        if self.nA:
            pen[:, 0] = np.clip(np.log(np.clip(D["c5_needed"], 1e-300, 1e300) / o["c5_max"]), 0, None) / 0.05
        pen[:, 1] = np.clip(np.log(np.clip(D["c126_lo"], 1e-300, None) / np.clip(D["c126_hi"], 1e-300, None)), 0, None) / 0.05
        pen[:, 2] = np.clip(np.log(np.clip(D["cd10_min"], 1e-300, None) / np.clip(D["c10_allow"], 1e-300, None)), 0, None) / 0.05
        pen = np.where(np.isfinite(pen), pen, 1e3)
        res = np.concatenate([R, pen], 1)
        if want:
            return res, dict(obs=obs, M=M, D=D, rho_nu=rho_nu, lam=lam, mn=mn * np.sqrt(lam)[:, None] * 1e-9 * 1e9,
                             delta_pmns=nd)
        return res

    def derived(self, M, rho_nu):
        o = self.o
        r, s = M["r"], M["s"]
        Hmax = np.abs(M["H"]).max(axis=(1, 2)); Fmax = np.abs(M["F"]).max(axis=(1, 2))
        rho = M["rho"]
        A1 = np.abs(M["A"]).max(axis=(1, 2)) / np.clip(np.abs(1 + rho), 1e-3, None)
        Amax = np.maximum(A1, np.abs(rho) * A1)
        rs2 = np.abs(r * s) ** 2
        cd10_min = Hmax * L.Y10_ACT / 1.5
        cd126_min = np.maximum(Fmax * L.Y126_ACT / 1.5, Fmax * C_R / math.sqrt(4 * math.pi))
        kfac = C_R * rho_nu / V ** 2
        c126_lo = np.maximum(cd126_min, o["sigma_lo"] * kfac)
        c126_hi = o["sigma_hi"] * kfac
        rem = 1 - (1 + rs2) * c126_lo ** 2
        c10_allow = np.sqrt(np.clip(rem, 0, None) / (1 + r ** 2))
        c5_needed = np.where(Amax > 0, Amax / (o["kappa_phi"] * np.clip(c10_allow, 1e-300, None)), 0.0)
        c10_req = np.maximum(cd10_min, Amax / (o["kappa_phi"] * o["c5_max"]))
        rem2 = 1 - (1 + r ** 2) * c10_req ** 2
        c126_max = np.sqrt(np.clip(rem2, 0, None) / (1 + rs2))
        return dict(cd10_min=cd10_min, cd126_min=cd126_min, c126_lo=c126_lo, c126_hi=c126_hi, c10_allow=c10_allow,
                    c5_needed=c5_needed, c10_req=c10_req, c126_max=c126_max, sigma_max=c126_max / kfac,
                    sigma_min=cd126_min / kfac, Amax=Amax)

    def chi2(self, X):
        res = self.evaluate(X)
        return np.sum(res ** 2, axis=1)


def run(prob, popsize=25, maxiter=1500, seed=1, npolish=8, tol=1e-9, workers=1):
    t0 = time.time()

    def f(Xt):        # vectorised: Xt shape (D, S)
        return prob.chi2(Xt.T)
    res = differential_evolution(f, prob.bounds, popsize=popsize, maxiter=maxiter, seed=seed, tol=tol, polish=False,
                                 vectorized=True, updating="deferred", mutation=(0.5, 1.0), recombination=0.9,
                                 init="sobol")
    pop = res.population if hasattr(res, "population") else np.atleast_2d(res.x)
    en = res.population_energies if hasattr(res, "population_energies") else np.array([res.fun])
    order = np.argsort(en)
    best = None
    lo = np.array([b[0] for b in prob.bounds]); hi = np.array([b[1] for b in prob.bounds])
    seen = []
    for idx in order[: max(npolish * 4, npolish)]:
        x0 = pop[idx]
        if any(np.linalg.norm(x0 - y) < 1e-3 for y in seen):
            continue
        seen.append(x0)
        def jac(x):
            h = 1e-6 * (1 + np.abs(x))
            Xs = np.vstack([x[None]] + [x[None] + np.eye(len(x))[k:k + 1] * h[k] for k in range(len(x))])
            Rb = prob.evaluate(Xs)
            return ((Rb[1:] - Rb[0][None]) / h[:, None]).T
        try:
            ls = least_squares(lambda x: prob.evaluate(x[None])[0], np.clip(x0, lo + 1e-9, hi - 1e-9), bounds=(lo, hi),
                               jac=jac, method="trf", max_nfev=3000, x_scale="jac")
            c = float(np.sum(ls.fun ** 2)); x = ls.x
        except Exception:
            c = float(en[idx]); x = x0
        if best is None or c < best[1]:
            best = (x, c)
        if len(seen) >= npolish:
            break
    return best, float(res.fun), time.time() - t0


def summary(prob, x):
    res, info = prob.evaluate(x[None], want=True)
    R = res[0, :18]; pen = res[0, 18:]
    D = {k: float(v[0]) for k, v in info["D"].items()}
    M = info["M"]
    obs = info["obs"][0]
    return {"chi2_obs": float(np.sum(R ** 2)), "penalty2": float(np.sum(pen ** 2)), "n_pulls_gt3": int(np.sum(np.abs(R) > 3)),
            "pulls": {k: round(float(v), 3) for k, v in zip(KEYS, R)}, "r": float(M["r"][0]),
            "s": [float(M["s"][0].real), float(M["s"][0].imag)], "rho": float(M["rho"][0]), "eps": float(M["eps"][0]),
            "A_abs_max": float(np.abs(M["A"][0]).max()), "F_abs_max": float(np.abs(M["F"][0]).max()),
            "H_abs_max": float(np.abs(M["H"][0]).max()), "derived": D, "rho_nu_GeV": float(info["rho_nu"][0]),
            "m_nu_eV": [float(m) for m in info["mn"][0]], "sin2_th23": float(obs[IM["sin2_th23"]]),
            "ms_over_md_MU": float(obs[4] / obs[3]), "target_ms_over_md_MU": float(prob.T[4] / prob.T[3]),
            "delta_pmns_rad": float(info["delta_pmns"][0])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--MU", type=float, default=1.28e16)
    ap.add_argument("--light", default="BOP")
    ap.add_argument("--useA", type=int, default=1)
    ap.add_argument("--typeII", type=int, default=0)
    ap.add_argument("--kappa", type=float, default=0.01)
    ap.add_argument("--c5max", type=float, default=1.0)
    ap.add_argument("--siglo", type=float, default=1e9)
    ap.add_argument("--sighi", type=float, default=1e17)
    ap.add_argument("--Arange", type=float, default=30.0)
    ap.add_argument("--off", type=float, default=0.3)
    ap.add_argument("--popsize", type=int, default=25)
    ap.add_argument("--maxiter", type=int, default=1500)
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--floor", type=float, default=0.01)
    a = ap.parse_args()
    light = {"BOP": [(1e3, (0.0, 0.0, 0.5)), (1.7e9, (0.0, 8 / 3, 1.5))], "none": []}[a.light]
    T, S, info = P.make_targets(a.MU, light, floor=a.floor)
    opts = dict(typeII=bool(a.typeII), use_A=bool(a.useA), kappa_phi=a.kappa, c5_max=a.c5max, sigma_lo=a.siglo,
                sigma_hi=a.sighi, Arange=a.Arange, off=a.off)
    prob = Problem(T, S, opts)
    print("label", a.label, opts, "MU", a.MU, "light", a.light, flush=True)
    runs = []
    best = None
    for sd in [int(z) for z in a.seeds.split(",")]:
        b, de_best, dt = run(prob, popsize=a.popsize, maxiter=a.maxiter, seed=sd)
        sm = summary(prob, b[0])
        runs.append({"seed": sd, "de_best": de_best, "polished_total": b[1], "chi2_obs": sm["chi2_obs"],
                     "penalty2": sm["penalty2"], "seconds": dt})
        print(f" seed {sd}: DE {de_best:.3f} -> polished total {b[1]:.3f} (chi2_obs {sm['chi2_obs']:.3f}, pen "
              f"{sm['penalty2']:.3g}) {dt:.0f}s", flush=True)
        if best is None or b[1] < best[1]:
            best = b
    sm = summary(prob, best[0])
    sm.update({"label": a.label, "opts": opts, "MU": a.MU, "light": a.light, "total": best[1], "runs": runs,
               "x": best[0].tolist(), "targets": {k: float(v) for k, v in zip(KEYS, T)},
               "errors": {k: float(v) for k, v in zip(KEYS, S)}})
    print(json.dumps({k: v for k, v in sm.items() if k not in ("x", "targets", "errors")}, indent=1, default=str))
    (HERE / f"d2b_{a.label}.json").write_text(json.dumps(sm, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
