"""SKEPTIC (D-B-symmetry, D2): independent GUT-scale proxy fit of the V1 Yukawa structure (own code).

V1 at M_U:  Yd = H + F, Ye = H - 3F, Yu = G + s'F, Ynu = G - 3 s'F, M_R = (v^2/kappa) F  (type I),
            H, G independent symmetric (two 10_H), F = Y126 w_d, s' = w_u/w_d.
=> F = (Yd - Ye)/4 fixed by the charged sector up to W, Ynu = Yu - 4 s'F, m_nu = -kappa Ynu F^-1 Ynu^T.
Own parameterisation: W = expm(i Herm(9 params)); Yu = E diag(yu) E^T with E = P1 V_CKM^T P2; s' complex.
Two independent input sets for the GUT-scale charged Yukawas:
  'designer' : the designer's bottom-up targets (lib_r2c/model_r2c imported READ-ONLY from the designer folder),
  'lit'      : my own approximate SM-running GUT values (Xing-Zhang-Zhou-type numbers at ~2e16 GeV, EST),
neutrino data NuFIT 6.0 NO with SK (sin^2 th12 0.308(12), th23 0.470(15), th13 0.02215(57); dm21 7.49(19)e-5,
dm31 2.513(20)e-3 eV^2).  chi2 = 5 neutrino pulls (charged sector exact by construction), scale analytic.
Window: v_R >= M_R3/sqrt(4 pi) (f <= sqrt(4 pi)); v_R <= v^2/(C_R kappa) min(1, 1/|s'|) (|w_u|,|w_d| <= 1).
Also reports the composition implied (|w_u|, |w_d|) and the minimal two-10 Yukawa norms.
usage: python -B sk_d2_fit.py <input_set> <vR> <MRcap or 0> <nstarts> <seed>
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import expm
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
DES = HERE.parent
VEV = 174.1
C_R = 2 * math.sqrt(6)
NU = {"s12sq": (0.308, 0.0115), "s23sq": (0.470, 0.015), "s13sq": (0.02215, 0.00057),
      "dm21": (7.49e-5, 0.19e-5), "dm31": (2.513e-3, 0.020e-3)}


def ckm(s12, s23, s13, d):
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    e = np.exp(-1j * d)
    return np.array([[c12 * c13, s12 * c13, s13 * e],
                     [-s12 * c23 - c12 * s23 * s13 / e, c12 * c23 - s12 * s23 * s13 / e, s23 * c13],
                     [s12 * s23 - c12 * c23 * s13 / e, -c12 * s23 - s12 * c23 * s13 / e, c23 * c13]])


def inputs(kind, vR):
    if kind == "designer":
        sys.path.insert(0, str(DES))
        import lib_r2c as L  # noqa: E402  (read-only)
        import model_r2c as M  # noqa: E402  (read-only)
        content = "R622" if vR >= 1e12 else "C2"
        data = L.data_set("nufit60_sk", floor=0.01)
        setup = M.make_setup(vR, data, content=content, MU=L.R2B_NOMINAL.get(content, (None, None))[1])
        tg = setup["targets"]; T = tg.T
        idx = {k: i for i, k in enumerate(L.ALL_KEYS)}
        yu = np.array(T[[0, 1, 2]]) / L.VEV
        yd = np.array(tg.sd0); ye = np.array(tg.se0)
        V = ckm(T[idx["s12"]], T[idx["s23"]], T[idx["s13"]], T[idx["delta"]])
        return yu, yd, ye, V
    # 'lit': approximate SM-running values at ~2e16 GeV (masses in GeV / 174.1), EST
    mu, mc, mt = 0.48e-3, 0.235, 74.0
    md, ms, mb = 1.14e-3, 21.6e-3, 0.99
    me, mm, mta = 0.4697e-3, 99.14e-3, 1.685
    V = ckm(0.2251, 0.0482, 0.00417, 1.20)
    return (np.array([mu, mc, mt]) / VEV, np.array([md, ms, mb]) / VEV, np.array([me, mm, mta]) / VEV, V)


def herm(p):
    H = np.zeros((3, 3), complex)
    H[0, 0], H[1, 1], H[2, 2] = p[0], p[1], p[2]
    H[0, 1] = p[3] + 1j * p[4]; H[0, 2] = p[5] + 1j * p[6]; H[1, 2] = p[7] + 1j * p[8]
    H[1, 0], H[2, 0], H[2, 1] = np.conj(H[0, 1]), np.conj(H[0, 2]), np.conj(H[1, 2])
    return H


class Model:
    def __init__(self, yu, yd, ye, V):
        self.yu, self.yd, self.ye, self.V = yu, yd, ye, V

    def mats(self, x):
        W = expm(1j * herm(x[0:9]))
        Ye = W @ np.diag(self.ye) @ W.T
        Yd = np.diag(self.yd).astype(complex)
        E = np.diag(np.exp(1j * x[9:12])) @ self.V.T @ np.diag(np.exp(1j * x[12:15]))
        Yu = E @ np.diag(self.yu) @ E.T
        sp = 10.0 ** x[15] * np.exp(1j * x[16])
        F = (Yd - Ye) / 4.0
        Yn = Yu - 4.0 * sp * F
        return W, Ye, Yd, Yu, F, Yn, sp

    def obs(self, x):
        W, Ye, Yd, Yu, F, Yn, sp = self.mats(x)
        try:
            m1 = -Yn @ np.linalg.solve(F, Yn.T)
        except np.linalg.LinAlgError:
            return None
        sc = np.abs(m1).max()
        if not np.isfinite(sc) or sc == 0:
            return None
        m1 = m1 / sc
        w2, Vn = np.linalg.eigh(m1 @ m1.conj().T)     # left rotation (same index convention as Ye Ye^dag = W D^2 W^dag)
        U = W.conj().T @ Vn
        A = np.abs(U)
        s13 = A[0, 2]; c13 = math.sqrt(max(1 - s13**2, 1e-30))
        s12 = A[0, 1] / c13; s23 = A[1, 2] / c13
        w2 = np.clip(w2, 0, None)
        a21, a31 = w2[1] - w2[0], w2[2] - w2[0]
        (t21, e21), (t31, e31) = NU["dm21"], NU["dm31"]
        lam = max((a21 * t21 / e21**2 + a31 * t31 / e31**2) / (a21**2 / e21**2 + a31**2 / e31**2), 1e-300)
        kappa_GeV = 1e-9 * math.sqrt(lam) / sc         # m_nu[GeV] = kappa * (-Yn F^-1 Yn^T)
        sF = np.linalg.svd(F, compute_uv=False)
        MR = np.sort(VEV**2 / kappa_GeV * sF)
        return dict(s12sq=s12**2, s23sq=s23**2, s13sq=s13**2, dm21=lam * a21, dm31=lam * a31, kappa=kappa_GeV,
                    MR=MR, sp=sp, mnu=np.sqrt(w2 * lam), F=F, Yn=Yn, Yu=Yu, Yd=Yd, Ye=Ye)

    def res(self, x, cap):
        o = self.obs(x)
        if o is None:
            return np.full(6, 1e3)
        r = [(o[k] - NU[k][0]) / NU[k][1] for k in ("s12sq", "s23sq", "s13sq", "dm21", "dm31")]
        r.append(10.0 * max(0.0, math.log10(o["MR"][-1] / cap)) if cap > 0 else 0.0)
        return np.array(r)


def main():
    kind, vR, cap, nst, seed = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    mdl = Model(*inputs(kind, vR))
    rng = np.random.default_rng(seed)
    lo = np.array([-np.pi] * 15 + [-1.0, -np.pi]); hi = np.array([np.pi] * 15 + [3.0, np.pi])
    blo = np.array([-10.0] * 15 + [-2.0, -10.0]); bhi = np.array([10.0] * 15 + [3.0, 10.0])
    t0 = time.time(); best = []
    for _ in range(nst):
        x0 = rng.uniform(lo, hi)
        try:
            r = least_squares(lambda x: mdl.res(x, cap), x0, method="trf", bounds=(blo, bhi), max_nfev=3000, x_scale="jac")
        except Exception:
            continue
        best.append((float(np.sum(r.fun**2)), r.x))
    best.sort(key=lambda z: z[0])
    c2, x = best[0]
    o = mdl.obs(x); rr = mdl.res(x, cap)
    cd = C_R * o["kappa"] * vR / VEV**2          # |w_d|
    wu = abs(o["sp"]) * cd
    G = o["Yu"] - o["sp"] * o["F"]; Hm = (3 * o["Yd"] + o["Ye"]) / 4
    sG = np.linalg.svd(G, compute_uv=False)[0]; sH = np.linalg.svd(Hm, compute_uv=False)[0]
    rem = max(1 - wu**2 - cd**2, 0.0)
    # minimal max-Yukawa with v_u1, v_d2 only: minimise max(sG/a, sH/b) s.t. a^2 + b^2 = rem
    a = math.sqrt(rem) * sG / math.hypot(sG, sH); b = math.sqrt(rem) * sH / math.hypot(sG, sH)
    ymax = sG / a if a > 0 else float("inf")
    mD = np.linalg.svd(o["Yn"], compute_uv=False) * VEV
    out = {"input_set": kind, "vR": vR, "MRcap": cap, "nstarts": nst, "seed": seed, "seconds": time.time() - t0,
           "chi2_best": c2, "chi2_nu": float(np.sum(rr[:5]**2)), "pulls": rr[:5].tolist(),
           "chi2_sorted_first8": [b_[0] for b_ in best[:8]],
           "MR_GeV": o["MR"].tolist(), "MR3/sqrt4pi": o["MR"][-1] / math.sqrt(4 * math.pi),
           "vR_max_composition": VEV**2 / (C_R * o["kappa"]) * min(1.0, 1.0 / abs(o["sp"])),
           "window_ok": bool(o["MR"][-1] / math.sqrt(4 * math.pi) <= vR <= VEV**2 / (C_R * o["kappa"]) * min(1, 1 / abs(o["sp"]))),
           "abs_sprime": abs(o["sp"]), "abs_w_d": cd, "abs_w_u": wu, "sigma_max_G": sG, "sigma_max_H": sH,
           "two10_min_max_Yukawa": ymax, "mD_GeV": mD.tolist(), "mnu_eV": o["mnu"].tolist(),
           "yt_GUT": float(mdl.yu[2]), "Dirac_cancellation_sigmaYn/yt": float(mD[0] / VEV / mdl.yu[2]),
           "x": x.tolist()}
    tag = f"sk_d2_{kind}_{vR:.0e}_cap{cap:.0e}_s{seed}"
    (HERE / f"{tag}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(tag, json.dumps({k: v for k, v in out.items() if k not in ("x", "chi2_sorted_first8")}), flush=True)


if __name__ == "__main__":
    main()
