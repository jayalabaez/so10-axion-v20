#!/usr/bin/env python3
"""SKEPTIC D2: proxy fit with the EXACT SO(10) Clebsch structure of the d=5 operator the design names.

EXACT input (sk_clebsch.py): at the design orientation omega = 0, Phi210 = p P + a A,
  (H10 x Phi210)_120 = interior(H, Phi): the A (15,1,1) form has no SO(4) index -> contributes nothing for the doublet;
  the P form gives the SU(4)-singlet (1,2,2) of the 120 built from the SAME H10 doublet components.
  => G enters  M_d = H + F + G,  M_e = H - 3F + G,  M_u = r(H + sF + G),  M_D = r(H - 3sF + G)
     i.e. c_e = c_u = c_D = 1 EXACTLY (the designer fitted c_e, c_u, c_D as free reals: (-0.33, 0.12, 13.0) etc.).
  (H10 x Phi210)_126 = (H ^ A) projected: (15,2,2) along B-L with the H10 doublet ratio r:
     F' enters  M_d += F', M_e += -3F', M_u += r F', M_D += -3 r F'   (complex symmetric F').
Modes: free (designer structure, reproduction), x120 (exact 120 channel only), x120_126 (both channels of
F.F.H10.Phi210/Lambda).  Size bounds (stated): |r G_ij|, |r F'_ij| <= umax GeV in the UP sector
  (r G = c p |Phi|/Lambda v_u^10 N ~ 1.65 c GeV for |Phi|/Lambda = 0.019, v_u^10 ~ 123 GeV, N ~ 1;
   umax = 5 -> c <~ 3 ; the designer's |G| <= 0.5 GeV in down units corresponds to umax ~ 33 GeV, c ~ 20).
Targets = the designer's GUT-scale targets (N8362, 1% floor) read from their JSON (same lib_r2c RG); error model unchanged.
usage: python -B sk_flavour.py <mode> <minutes> <umax> [Rmin] [seed]
"""
from __future__ import annotations
import sys, json, math, time
import numpy as np
from scipy.optimize import least_squares
from scipy.linalg import expm
from pathlib import Path
import lib_r2c as L

HERE = Path(__file__).resolve().parent
mode, minutes, umax = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
Rmin = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "none" else None
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 11
D = json.load(open(HERE.parent / "flavour" / "fit_N8362_d5_f0.01_g0.5.json"))
TG = {k: tuple(v) for k, v in D["targets"].items()}
X_DES = np.array(D["x"])
D2 = json.load(open(HERE.parent / "flavour" / "fit_N8362_d5_f0.01_g0.5_R5e+15.json")); X_DES2 = np.array(D2["x"])
V = L.VEV
NB = 19
NP = {"free": NB + 9, "x120": NB + 6, "x120_126": NB + 6 + 12}[mode]


def herm9(v):
    Hm = np.zeros((3, 3), complex)
    Hm[0, 0], Hm[1, 1], Hm[2, 2] = v[0], v[1], v[2]
    Hm[0, 1] = v[3] + 1j * v[4]; Hm[0, 2] = v[5] + 1j * v[6]; Hm[1, 2] = v[7] + 1j * v[8]
    return Hm + np.triu(Hm, 1).conj().T


def unpack(x):
    d = x[0:3]; e = x[3:6]; W = expm(1j * herm9(x[6:15]))
    Sd = np.diag(d).astype(complex); Se = W.T @ np.diag(e) @ W
    H = (3 * Sd + Se) / 4; F = (Sd - Se) / 4
    r = math.exp(min(max(x[15], -30), 30)); s = x[16] + 1j * x[17]; lR = min(max(x[18], -80), 80)
    g = x[19:25]; G = np.zeros((3, 3), complex); G[0, 1], G[0, 2], G[1, 2] = g[0] + 1j * g[1], g[2] + 1j * g[3], g[4] + 1j * g[5]
    G = G - G.T
    ce = cu = cD = 1.0; Fp = np.zeros((3, 3), complex)
    if mode == "free":
        ce, cu, cD = x[25:28]
    if mode == "x120_126":
        f = x[25:37]; Fp = np.array([[f[0] + 1j * f[1], f[2] + 1j * f[3], f[4] + 1j * f[5]],
                                     [f[2] + 1j * f[3], f[6] + 1j * f[7], f[8] + 1j * f[9]],
                                     [f[4] + 1j * f[5], f[8] + 1j * f[9], f[10] + 1j * f[11]]])
    return H, F, r, s, lR, G, ce, cu, cD, Fp


def model(x):
    H, F, r, s, lR, G, ce, cu, cD, Fp = unpack(x)
    # H, F are defined from S_d = H + F (+F' absorbed: the pinned symmetric parts are S_d = H + F + F', S_e = H - 3F - 3F')
    # so that F_ren (entering M_u with s and M_R) = F - F'.
    Fr = F - Fp
    Md = H + Fr + Fp + G; Me = H - 3 * Fr - 3 * Fp + ce * G
    Mu = r * (H + s * Fr + Fp + cu * G); MD = r * (H - 3 * s * Fr - 3 * Fp + cD * G)
    try:
        Finv = np.linalg.inv(Fr)
    except np.linalg.LinAlgError:
        return None
    if not np.all(np.isfinite(Finv)):
        return None
    mnu = -(MD @ Finv @ MD.T) * math.exp(-lR)
    return Mu, Md, Me, mnu, (H, Fr, r, s, lR, G, ce, cu, cD, Fp)


def residuals(x):
    m = model(x)
    if m is None:
        return np.full(20, 1e3)
    Mu, Md, Me, mnu, par = m
    o = L.observables(Mu / V, Md / V, Me / V, mnu)
    res = []
    for k in L.ALL_KEYS:
        c, s = TG[k]
        if k in L.MASS_KEYS:
            res.append(math.log(max(o[k], 1e-300) / c) * c / s)
        elif k == "delta":
            res.append(((abs(o[k]) - c + math.pi) % (2 * math.pi) - math.pi) / s)
        else:
            res.append((o[k] - c) / s)
    r = par[2]; G = par[5]; Fp = par[9]
    over1 = max(0.0, r * float(np.max(np.abs(G))) - umax)
    over2 = max(0.0, r * float(np.max(np.abs(Fp))) - umax)
    res.append(over1 / (0.02 * umax)); res.append(over2 / (0.02 * umax))
    return np.array(res)


rng = np.random.default_rng(seed)
lb = np.full(NP, -np.inf); ub = -lb
if Rmin is not None:
    lb[18] = math.log(Rmin)


def start():
    x = np.zeros(NP)
    u = rng.random()
    if u < 0.3:   # warm start from the designer's best points (their c's dropped / set to the exact values)
        src = X_DES if (Rmin is None or rng.random() < 0.5) else X_DES2
        x[:25] = src[:25] + rng.normal(0, 0.02, 25) * (np.abs(src[:25]) + 1e-3)
    else:
        x[0:3] = [TG["m_d"][0], TG["m_s"][0], TG["m_b"][0]] * rng.choice([-1, 1], 3)
        x[3:6] = [TG["m_e"][0], TG["m_mu"][0], TG["m_tau"][0]] * rng.choice([-1, 1], 3)
        x[6:15] = rng.normal(0, 1.0, 9) * rng.choice([0.1, 0.5, 1.5])
        x[15] = math.log(TG["m_t"][0] / TG["m_b"][0]) + rng.normal(0, 1.0)
        x[16:18] = rng.normal(0, 1.0, 2)
        x[18] = math.log(10 ** rng.uniform(11, 16))
        x[19:25] = rng.normal(0, 1, 6) * 0.02
    if mode == "free":
        x[25:28] = X_DES[25:28] if u < 0.3 else rng.normal(0, 1.5, 3)
    if mode == "x120_126":
        x[25:37] = rng.normal(0, 1, 12) * 0.01
    if Rmin is not None:
        x[18] = max(x[18], math.log(Rmin) + abs(rng.normal(0, 1)))
    return x


def solve(x0, nfev):
    x0 = np.clip(x0, lb + 1e-9, ub - 1e-9) if Rmin is not None else x0
    kw = dict(bounds=(lb, ub)) if Rmin is not None else {}
    r = least_squares(residuals, x0, method="trf", max_nfev=nfev, x_scale="jac", **kw)
    return float(np.sum(r.fun ** 2)), r.x


T0 = time.time(); TL = minutes * 60
screen = []
while time.time() - T0 < 0.5 * TL:
    try:
        screen.append(solve(start(), 800))
    except Exception:
        pass
screen.sort(key=lambda t: t[0])
print(f"[{mode} umax={umax} Rmin={Rmin}] screened {len(screen)}; best: {[round(c, 1) for c, _ in screen[:10]]}", flush=True)
pol = []
for c0, x in screen[:8]:
    if time.time() - T0 > 0.75 * TL:
        break
    try:
        pol.append(solve(x, 6000))
    except Exception:
        pass
pol.sort(key=lambda t: t[0]); best = pol[0] if pol else screen[0]
print(f"   polished: {[round(c, 2) for c, _ in pol]}", flush=True)
nh = 0
while time.time() - T0 < TL:
    x = best[1] + rng.normal(0, 1, NP) * np.where(np.arange(NP) < 6, 0.0, 0.15)
    try:
        c, xn = solve(x, 3000)
    except Exception:
        continue
    nh += 1
    if c < best[0]:
        best = (c, xn); print(f"   hop {nh}: chi2 -> {c:.3f}", flush=True)
x = best[1]; Mu, Md, Me, mnu, par = model(x); o = L.observables(Mu / V, Md / V, Me / V, mnu); res = residuals(x)
H, Fr, r, s, lR, G, ce, cu, cD, Fp = par
rep = {"mode": mode, "umax": umax, "Rmin": Rmin, "chi2": float(np.sum(res[:18] ** 2)), "penalty": float(np.sum(res[18:] ** 2)),
       "pulls": {k: float(v) for k, v in zip(L.ALL_KEYS, res[:18])}, "ms_md": float(o["m_s"] / o["m_d"]), "r": r, "s": [s.real, s.imag],
       "rG_max_GeV": r * float(np.max(np.abs(G))), "G_max_GeV_down_units": float(np.max(np.abs(G))),
       "rFp_max_GeV": r * float(np.max(np.abs(Fp))), "c_e_u_D": [ce, cu, cD], "R": math.exp(lR),
       "MR_eigs": sorted(np.abs(np.linalg.eigvals(Fr * math.exp(lR))).tolist()), "n_screen": len(screen), "n_hops": nh,
       "screen_best": [c for c, _ in screen[:20]], "polished": [c for c, _ in pol], "x": x.tolist()}
print(f"[{mode} umax={umax} Rmin={Rmin}] chi2_min = {rep['chi2']:.3f} (penalty {rep['penalty']:.2e}); "
      f"pulls>2: { {k: round(v, 2) for k, v in rep['pulls'].items() if abs(v) > 2} }; ms/md = {rep['ms_md']:.2f}; "
      f"rG_max = {rep['rG_max_GeV']:.3g} GeV; rF'_max = {rep['rFp_max_GeV']:.3g}; r = {r:.3g}; R = {rep['R']:.3e}", flush=True)
json.dump(rep, open(str(HERE / f"sk_fit_{mode}_u{umax:g}") + (f"_R{Rmin:.0e}" if Rmin else "") + f"_s{seed}.json", "w"), indent=1, default=float)
