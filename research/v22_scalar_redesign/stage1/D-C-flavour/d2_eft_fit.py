"""D2 proxy fit for the one-step (SO(10) -> SM at M_U, v_BL = v_R ~ M_U) designs: renormalizable 10_H + 126bar_H
Yukawas, optionally + the X-allowed d = 5 operator O5 = S_ij (F_i F_j)_126 (Delta Phi210)_126bar / Lambda.

GUT-scale structure (Yukawa units, v = 174.1 GeV; d-diagonal basis; X forbids F.F.H10^*):
  renormalizable : Yd = H + F, Ye = H - 3F, Yu = r H + rho F, Ynu = r H - 3 rho F, M_R = v_R C_R F / c_d126
                   (H = c_d10 Y10, F = c_d126 Y126, r = c_u10/c_d10, rho = c_u126/c_d126 = r s; C_R = 2 sqrt6)
  + O5 (EXACT component structure; Clebsch magnitudes treated as O(1) bounded parameters):
     (Delta_d <Phi>)  -> 126bar (15,2,2) down : Yd += c_d126 eps kd S, Ye += -3 c_d126 eps kd S
     (Delta_u <Phi>)  -> up                   : Yu += c_u126 eps ku S, Ynu += -3 (same)
     (Delta_R  phi )  -> up only (B-L + Y conservation: Delta_R has B-L = -2, only the B-L = +2, Y = +1/2 doublet phi of
                         the 210 pairs with it to a B-L = 0 doublet, which is Y = +1/2)  : Yu += c_phi eps_R lam S
     (Delta_R <Phi>)  -> SM singlet of 126bar  : M_R += v_R eps kR S
  Eliminating Y126 with F := c_d126 (Y126 + eps kd S) (fixed by Yd, Ye) and K := eps S (|K_ij| <= eps = |Phi|/Lambda):
     Yu = r H + rho F + sigma K,  Ynu = r H - 3 rho F - 3 sigma K,  M_R = v_R (C_R F / c_d126 + tau K)
     sigma = c_u126 (ku - kd) + c_phi (v_R/|Phi|) lam,  tau = kR - C_R kd   (bounded: |sigma| <= SIG, |tau| <= TAU).
  The O5 contributions keep Yd = H + F, Ye = H - 3F (126-channel Clebsch -3), i.e. the charged sector is the
  renormalizable one; O5 breaks the M_R ~ F relation and shifts the up-sector 126-coefficient.
Normalisation: |c_u10|^2 + |c_d10|^2 + |c_u126|^2 + |c_d126|^2 + |c_phi|^2 = 1 -> c_d126^2 (1 + |rho|^2) <= CMAX2 = 0.9.
Neutrinos: type I, m_nu(M_U) = -v^2 Ynu M_R^-1 Ynu^T; Delta m^2(M_Z) = eta^2 Delta m^2(M_U) (eta from d2_targets).
Observables: 18 (9 masses, 4 CKM, 3 PMNS angles, 2 Delta m^2) against GUT-scale targets (d2_targets.py error model).

usage: python -B d2_eft_fit.py <chain a|b> <vR> <mode ren|o5> <eps> <nstart> <seed> <out.json> [floor]
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

C_R = 2 * math.sqrt(6)
V = L.VEV
CMAX2 = 0.9
SIG, TAU = 2.0, 5.0
SYM = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]
NPAR = 35


def angles1(Vm):
    """scalar version of lib angles_b: s12, s23, s13, delta for a 3x3 unitary."""
    A = np.abs(Vm)
    s13 = min(A[0, 2], 1.0); c13 = math.sqrt(max(1 - s13 * s13, 1e-300))
    s12 = min(A[0, 1] / c13, 1.0); s23 = min(A[1, 2] / c13, 1.0)
    c12 = math.sqrt(max(1 - s12 * s12, 0.0)); c23 = math.sqrt(max(1 - s23 * s23, 0.0))
    J = (Vm[0, 0] * Vm[1, 1] * np.conj(Vm[0, 1]) * np.conj(Vm[1, 0])).imag
    den = c12 * s12 * c23 * s23 * c13 * c13 * s13
    sind = J / (den if abs(den) > 1e-300 else 1e-300)
    num = A[1, 0] ** 2 - (s12 * c23) ** 2 - (c12 * s23 * s13) ** 2
    cosd = num / (2 * s12 * c23 * c12 * s23 * s13 + 1e-300)
    return s12, s23, s13, math.atan2(sind, cosd)


def umix1(th12, th13, th23, d):
    s12, c12 = math.sin(th12), math.cos(th12); s13, c13 = math.sin(th13), math.cos(th13)
    s23, c23 = math.sin(th23), math.cos(th23); e = complex(math.cos(d), math.sin(d))
    return np.array([[c12 * c13, s12 * c13, s13 * e.conjugate()],
                     [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                     [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])


def sigm(u):
    return 1.0 / (1.0 + np.exp(-u))


def wmat(x):
    th12, th13, th23, d = x[0], x[1], x[2], x[3]
    U = umix1(th12, th13, th23, d)
    P1 = np.exp(1j * np.array([x[4], x[5], 0.0]))
    P2 = np.exp(1j * np.array([x[6], x[7], x[8]]))
    return P1[:, None] * U * P2[None, :]


def model(x, tg, vR, mode, eps):
    W = wmat(x)
    sd = tg["sd0"] * np.exp(x[29:32]); se = tg["se0"] * np.exp(x[32:35])
    Yd = np.diag(sd).astype(complex)
    Ye = (W * se[None, :]) @ W.T
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0 ** x[9]
    rho = 10.0 ** x[10] * np.exp(1j * x[11])
    cd126 = sigm(x[28]) * math.sqrt(CMAX2 / (1 + abs(rho) ** 2))
    if mode == "o5":
        sigma = SIG * sigm(x[12]) * np.exp(1j * x[13])
        tau = TAU * sigm(x[14]) * np.exp(1j * x[15])
        K = np.zeros((3, 3), complex)
        for n, (i, j) in enumerate(SYM):
            v = eps * sigm(x[16 + 2 * n]) * np.exp(1j * x[17 + 2 * n])
            K[i, j] = v; K[j, i] = v
    else:
        sigma = tau = 0.0; K = np.zeros((3, 3), complex)
    Yu = r * H + rho * F + sigma * K
    Yn = r * H - 3 * rho * F - 3 * sigma * K
    MR = vR * (C_R * F / cd126 + tau * K)
    return dict(W=W, sd=sd, se=se, Yd=Yd, Ye=Ye, H=H, F=F, r=r, rho=rho, cd126=cd126, sigma=sigma, tau=tau, K=K,
                Yu=Yu, Yn=Yn, MR=MR)


def observables(m, tg):
    w, Eu = np.linalg.eigh(m["Yu"] @ m["Yu"].conj().T)
    mu = np.sqrt(np.clip(w, 0, None)) * V
    CKM = Eu.T                                         # E_u^T E_d^*, E_d = 1
    c12, c23, c13, cd = angles1(CKM)
    try:
        mnu = -(V ** 2) * m["Yn"] @ np.linalg.solve(m["MR"], m["Yn"].T)      # GeV at M_U
    except np.linalg.LinAlgError:
        return None
    if not np.all(np.isfinite(mnu)):
        return None
    wn, N = np.linalg.eigh(mnu.conj().T @ mnu)
    mn = np.sqrt(np.clip(wn, 0, None)) * tg["eta"]      # GeV at M_Z
    U = m["W"].T @ N
    n12, n23, n13, nd = angles1(U)
    o = np.zeros(18)
    o[0:3] = mu; o[3:6] = m["sd"] * V; o[6:9] = m["se"] * V
    o[9] = c12; o[10] = c23; o[11] = c13; o[12] = abs(cd)
    o[13] = n12 ** 2; o[14] = n23 ** 2; o[15] = n13 ** 2
    o[16] = (mn[1] ** 2 - mn[0] ** 2) * 1e18; o[17] = (mn[2] ** 2 - mn[0] ** 2) * 1e18
    return o, dict(mn_eV=(mn * 1e9).tolist(), delta_pmns=nd, U=U)


def residuals(x, tg, vR, mode, eps):
    m = model(x, tg, vR, mode, eps)
    res = observables(m, tg)
    if res is None:
        return np.full(18, 1e3)
    o, _ = res
    T, S = tg["T"], tg["S"]
    R = np.empty(18)
    for i, k in enumerate(L.ALL_KEYS):
        if k in L.MASS_KEYS:
            R[i] = math.log(max(o[i], 1e-300) / T[i]) * T[i] / S[i]
        elif k == "delta":
            R[i] = ((o[i] - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        elif k in ("dm21", "dm31"):
            R[i] = (o[i] - T[i]) / S[i] if o[i] > 0 else 1e3
        else:
            R[i] = (o[i] - T[i]) / S[i]
    R = np.where(np.isfinite(R), R, 1e3)
    return np.clip(R, -1e4, 1e4)


def random_start(rng, mode):
    x = np.zeros(NPAR)
    x[0:3] = rng.uniform(-math.pi, math.pi, 3); x[3] = rng.uniform(-math.pi, math.pi)
    x[4:9] = rng.uniform(-math.pi, math.pi, 5)
    x[9] = rng.uniform(1.4, 2.1)                     # r ~ 25-125
    x[10] = rng.uniform(-1.0, 2.0); x[11] = rng.uniform(-math.pi, math.pi)
    x[12:28] = np.where(np.arange(12, 28) % 2 == 0, rng.normal(0, 2, 16), rng.uniform(-math.pi, math.pi, 16))
    x[28] = rng.normal(0, 2)
    x[29:35] = rng.normal(0, 0.02, 6)
    return x


def summarize(x, tg, vR, mode, eps):
    m = model(x, tg, vR, mode, eps)
    o, ex = observables(m, tg)
    R = residuals(x, tg, vR, mode, eps)
    mR = np.sort(np.linalg.svd(m["MR"], compute_uv=False))
    MRren = vR * C_R * m["F"] / m["cd126"]
    cancel = float(np.linalg.norm(m["MR"]) / max(np.linalg.norm(MRren), 1e-300))
    comp_rest = 1 - m["cd126"] ** 2 * (1 + abs(m["rho"]) ** 2)
    cd10 = math.sqrt(max(comp_rest - 0.0, 0) / (1 + m["r"] ** 2))
    return {"chi2": float(R @ R), "pulls": {k: float(v) for k, v in zip(L.ALL_KEYS, R)},
            "n_pull_gt3": int(np.sum(np.abs(R) > 3)), "max_pull": float(np.max(np.abs(R))),
            "r": m["r"], "rho": [m["rho"].real, m["rho"].imag], "s=rho/r": abs(m["rho"]) / m["r"],
            "c_d126": m["cd126"], "c_u126=|rho| c_d126": abs(m["rho"]) * m["cd126"], "c_d10(max)": cd10,
            "sigma": [complex(m["sigma"]).real, complex(m["sigma"]).imag], "tau": [complex(m["tau"]).real, complex(m["tau"]).imag],
            "max|K|/eps": float(np.abs(m["K"]).max() / eps) if mode == "o5" else 0.0,
            "K_abs": np.abs(m["K"]).tolist(), "M_R_GeV": mR.tolist(), "MR/MR_renorm_norm_ratio": cancel,
            "Y126_eff_sv(F/c_d126)": np.sort(np.linalg.svd(m["F"] / m["cd126"], compute_uv=False)).tolist(),
            "Y10_33_def(H33/c_d10)": float(abs(m["H"][2, 2]) / cd10) if cd10 > 0 else None,
            "m_nu_eV": ex["mn_eV"], "delta_pmns_deg": math.degrees(ex["delta_pmns"]) % 360,
            "obs": {k: float(v) for k, v in zip(L.ALL_KEYS, o)}, "x": x.tolist()}


def main():
    chain, vR, mode, eps = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    nstart, seed, out = int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
    floor = float(sys.argv[8]) if len(sys.argv) > 8 else 0.01
    tg = TG.gut_targets(chain, floor=floor)
    rng = np.random.default_rng(seed)
    t0 = time.time()
    best = []
    for k in range(nstart):
        x0 = random_start(rng, mode)
        try:
            sol = least_squares(residuals, x0, args=(tg, vR, mode, eps), method="trf", max_nfev=4000, xtol=1e-10, ftol=1e-10)
            # a few hop-restarts from the local optimum
            x = sol.x; c = float(sol.fun @ sol.fun)
            for h in range(4):
                xh = x + rng.normal(0, 0.3, NPAR) * (np.arange(NPAR) < 29)
                s2 = least_squares(residuals, xh, args=(tg, vR, mode, eps), method="trf", max_nfev=3000, xtol=1e-10, ftol=1e-10)
                c2 = float(s2.fun @ s2.fun)
                if c2 < c:
                    x, c = s2.x, c2
        except Exception as e:      # noqa
            continue
        best.append((c, x))
        if (k + 1) % 10 == 0:
            cs = sorted(b[0] for b in best)
            print(f"[{chain} vR={vR:.1e} {mode} eps={eps}] {k + 1}/{nstart} best chi2 = {cs[0]:.3f} (5th {cs[min(4, len(cs) - 1)]:.2f}) "
                  f"t={time.time() - t0:.0f}s", flush=True)
    best.sort(key=lambda b: b[0])
    res = {"chain": chain, "vR": vR, "mode": mode, "eps": eps, "floor": floor, "nstart": nstart, "seed": seed,
           "MU": tg["MU"], "eta": tg["eta"], "targets": {k: [float(t), float(s)] for k, t, s in zip(L.ALL_KEYS, tg["T"], tg["S"])},
           "chi2_sorted_top20": [float(b[0]) for b in best[:20]],
           "best": summarize(best[0][1], tg, vR, mode, eps),
           "second_distinct": None, "seconds": time.time() - t0}
    for c, x in best[1:]:
        if c > best[0][0] + 1.0:
            res["second_distinct"] = summarize(x, tg, vR, mode, eps)
            break
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    b = res["best"]
    print(f"DONE {out}: chi2_min = {b['chi2']:.3f}, max pull {b['max_pull']:.2f}, n>3 = {b['n_pull_gt3']}, r = {b['r']:.1f}, "
          f"|s| = {b['s=rho/r']:.3f}, c_d126 = {b['c_d126']:.4f}, M_R = {np.array(b['M_R_GeV'])}, cancel = {b['MR/MR_renorm_norm_ratio']:.3g}, "
          f"max|K|/eps = {b['max|K|/eps']:.3f}", flush=True)


if __name__ == "__main__" and (len(sys.argv) < 2 or sys.argv[1] != "G"):
    main()


# ================================================================================ batched evaluator + global search
def residuals_batch(X, tg, vR, mode, eps):
    """X: (N, NPAR) -> chi2 (N,), residuals (N,18).  Same model as residuals()."""
    X = np.atleast_2d(X)
    N = X.shape[0]
    U0 = L.umix_b(X[:, 0], X[:, 1], X[:, 2], X[:, 3])
    P1 = np.exp(1j * np.stack([X[:, 4], X[:, 5], np.zeros(N)], 1))
    P2 = np.exp(1j * X[:, 6:9])
    W = P1[:, :, None] * U0 * P2[:, None, :]
    sd = tg["sd0"][None, :] * np.exp(X[:, 29:32]); se = tg["se0"][None, :] * np.exp(X[:, 32:35])
    Yd = np.zeros((N, 3, 3), complex); Yd[:, [0, 1, 2], [0, 1, 2]] = sd
    Ye = (W * se[:, None, :]) @ np.swapaxes(W, 1, 2)
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0 ** X[:, 9]
    rho = 10.0 ** X[:, 10] * np.exp(1j * X[:, 11])
    cd126 = sigm(X[:, 28]) * np.sqrt(CMAX2 / (1 + np.abs(rho) ** 2))
    if mode == "o5":
        sigma = SIG * sigm(X[:, 12]) * np.exp(1j * X[:, 13])
        tau = TAU * sigm(X[:, 14]) * np.exp(1j * X[:, 15])
        K = np.zeros((N, 3, 3), complex)
        for n, (i, j) in enumerate(SYM):
            v = eps * sigm(X[:, 16 + 2 * n]) * np.exp(1j * X[:, 17 + 2 * n])
            K[:, i, j] = v; K[:, j, i] = v
    else:
        sigma = np.zeros(N); tau = np.zeros(N); K = np.zeros((N, 3, 3), complex)
    Yu = r[:, None, None] * H + rho[:, None, None] * F + sigma[:, None, None] * K
    Yn = r[:, None, None] * H - 3 * rho[:, None, None] * F - 3 * sigma[:, None, None] * K
    MR = vR * (C_R * F / cd126[:, None, None] + tau[:, None, None] * K)
    w, Eu = np.linalg.eigh(Yu @ L.herm(Yu))
    mu = np.sqrt(np.clip(w, 0, None)) * V
    c12, c23, c13, cd = L.angles_b(np.swapaxes(Eu, 1, 2))
    bad = np.zeros(N, bool)
    try:
        Xs = np.linalg.solve(MR, np.swapaxes(Yn, 1, 2))
    except np.linalg.LinAlgError:
        Xs = np.full((N, 3, 3), np.nan, complex)
    mnu = -(V ** 2) * Yn @ Xs
    bad |= ~np.all(np.isfinite(mnu.reshape(N, -1)), axis=1)
    mnu = np.where(np.isfinite(mnu), mnu, 0)
    wn, Nv = np.linalg.eigh(L.herm(mnu) @ mnu)
    mn = np.sqrt(np.clip(wn, 0, None)) * tg["eta"]
    Upm = np.swapaxes(W, 1, 2) @ Nv
    n12, n23, n13, nd = L.angles_b(Upm)
    o = np.zeros((N, 18))
    o[:, 0:3] = mu; o[:, 3:6] = sd * V; o[:, 6:9] = se * V
    o[:, 9] = c12; o[:, 10] = c23; o[:, 11] = c13; o[:, 12] = np.abs(cd)
    o[:, 13] = n12 ** 2; o[:, 14] = n23 ** 2; o[:, 15] = n13 ** 2
    o[:, 16] = (mn[:, 1] ** 2 - mn[:, 0] ** 2) * 1e18; o[:, 17] = (mn[:, 2] ** 2 - mn[:, 0] ** 2) * 1e18
    T, S = tg["T"], tg["S"]
    R = np.empty((N, 18))
    for i, k in enumerate(L.ALL_KEYS):
        if k in L.MASS_KEYS:
            R[:, i] = np.log(np.clip(o[:, i], 1e-300, None) / T[i]) * T[i] / S[i]
        elif k == "delta":
            R[:, i] = ((o[:, i] - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        elif k in ("dm21", "dm31"):
            R[:, i] = np.where(o[:, i] > 0, (o[:, i] - T[i]) / S[i], 1e3)
        else:
            R[:, i] = (o[:, i] - T[i]) / S[i]
    R = np.where(np.isfinite(R), R, 1e3)
    R = np.clip(R, -1e4, 1e4)
    R[bad] = 1e3
    return np.sum(R * R, axis=1), R


def bounds(mode):
    lo = np.zeros(NPAR); hi = np.zeros(NPAR)
    lo[0:9] = -math.pi; hi[0:9] = math.pi
    lo[9], hi[9] = 1.0, 2.5
    lo[10], hi[10] = -2.5, 2.5
    lo[11], hi[11] = -math.pi, math.pi
    for i in range(12, 28):
        if i % 2 == 0:
            lo[i], hi[i] = -7, 7
        else:
            lo[i], hi[i] = -math.pi, math.pi
    lo[28], hi[28] = -9, 7
    lo[29:35], hi[29:35] = -0.08, 0.08
    if mode != "o5":
        lo[12:28] = 0; hi[12:28] = 1e-9
    return lo, hi


def global_search(tg, vR, mode, eps, seed, popsize=12, maxiter=1500, init=None):
    from scipy.optimize import differential_evolution
    lo, hi = bounds(mode)

    def f(Xt):            # scipy vectorized: Xt shape (NPAR, S)
        c, _ = residuals_batch(Xt.T, tg, vR, mode, eps)
        return c
    kw = dict(popsize=popsize, maxiter=maxiter, tol=1e-10, seed=seed, polish=False, vectorized=True,
              updating="deferred", mutation=(0.5, 1.0), recombination=0.9)
    if init is not None:
        kw["init"] = init
    res = differential_evolution(f, list(zip(lo, hi)), **kw)
    return res.x, float(res.fun)


def polish(x, tg, vR, mode, eps, nfev=3000):
    lo, hi = bounds(mode)
    x = np.clip(x, lo + 1e-12, hi - 1e-12)
    if mode != "o5":
        # freeze unused coordinates: optimise over the active subset only
        act = np.array([i for i in range(NPAR) if not (12 <= i < 28)])
    else:
        act = np.arange(NPAR)

    def fun(z):
        xx = x.copy(); xx[act] = z
        return residuals(xx, tg, vR, mode, eps)
    s = least_squares(fun, x[act], bounds=(lo[act], hi[act]), method="trf", max_nfev=nfev, xtol=1e-12, ftol=1e-12)
    xx = x.copy(); xx[act] = s.x
    return xx, float(s.fun @ s.fun)


def main_global():
    """usage: python -B d2_eft_fit.py G <chain> <vR> <mode> <eps> <nruns> <seed> <out.json> [floor] [maxiter]"""
    chain, vR, mode, eps = sys.argv[2], float(sys.argv[3]), sys.argv[4], float(sys.argv[5])
    nruns, seed, out = int(sys.argv[6]), int(sys.argv[7]), sys.argv[8]
    floor = float(sys.argv[9]) if len(sys.argv) > 9 else 0.01
    maxiter = int(sys.argv[10]) if len(sys.argv) > 10 else 1500
    tg = TG.gut_targets(chain, floor=floor)
    t0 = time.time()
    runs = []
    for k in range(nruns):
        x, c = global_search(tg, vR, mode, eps, seed + k, maxiter=maxiter)
        xp, cp = polish(x, tg, vR, mode, eps)
        if cp > c:
            xp, cp = x, c
        runs.append((cp, xp, c))
        print(f"[{chain} vR={vR:.1e} {mode} eps={eps} floor={floor}] run {k + 1}/{nruns}: DE {c:.3f} -> polish {cp:.3f} "
              f"t={time.time() - t0:.0f}s", flush=True)
    runs.sort(key=lambda r: r[0])
    res = {"chain": chain, "vR": vR, "mode": mode, "eps": eps, "floor": floor, "nruns": nruns, "seed": seed,
           "maxiter": maxiter, "MU": tg["MU"], "eta": tg["eta"],
           "targets": {k: [float(t), float(s)] for k, t, s in zip(L.ALL_KEYS, tg["T"], tg["S"])},
           "chi2_runs": [[float(r[2]), float(r[0])] for r in runs],
           "best": summarize(runs[0][1], tg, vR, mode, eps), "seconds": time.time() - t0}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    b = res["best"]
    print(f"DONE {out}: chi2_min = {b['chi2']:.3f}, max pull {b['max_pull']:.2f}, n>3 = {b['n_pull_gt3']}, r = {b['r']:.1f}, "
          f"|s| = {b['s=rho/r']:.3f}, c_d126 = {b['c_d126']:.4f}, M_R = {np.array(b['M_R_GeV'])}, "
          f"cancel = {b['MR/MR_renorm_norm_ratio']:.3g}, max|K|/eps = {b['max|K|/eps']:.3f}", flush=True)
    print("pulls:", {k: round(v, 2) for k, v in b["pulls"].items()}, flush=True)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "G":
    main_global()
