#!/usr/bin/env python3
"""SKEPTIC D4 (own code, NUM): two-loop gauge unification for the A1 SM-direct content, proton decay in the lattice
normalisation, SO(10)-phase two-loop Landau pole.

Own Machacek-Vaughn implementation (not r2b_lib):
  b_i  = -11/3 C(G_i) + 2/3 sum_Weyl S_i(F) + 1/3 sum_cplx S_i(S) + 1/6 sum_real S_i(S)
  b_ij = -34/3 C(G_i)^2 d_ij + sum_Weyl S_i(F)[2 C_j(F) + 10/3 C(G_i) d_ij] + sum_cplx S_i(S)[4 C_j(S) + 2/3 C(G_i) d_ij]
         (+ 1/2 of the complex-scalar term for real scalars)
  with S_i(R) = Dynkin index x dimension of the other factors, U(1)_Y in GUT normalisation (3/5 Y^2).
  dalpha_i^-1/dt = -b_i/(2pi) - sum_j b_ij alpha_j/(8 pi^2) + c_i y_t^2/(32 pi^3) [+ 14 y_s^2/(32 pi^3) above M_s, the
  designer's B63 Yukawa term; switchable].
Inputs PDG 2024 at M_Z: alpha_s = 0.1180, alpha_em^-1 = 127.951, sin^2 = 0.23122 (MSbar); y_t(M_Z) = 0.95 (designer)
and 0.94 (variation).
Matching at M_U: alpha_i^-1(M_U) + S_V,i/(12 pi) = alpha_U^-1, S_V = (8, 6, 5) (heavy vectors; own count below).
Proton: tau(p -> e+ pi0) = [m_p/(32 pi) (1 - m_pi^2/m_p^2)^2 A_R^2 W0^2 sum|C|^2]^-1, C = 2 k^2 (1 + |V_ud|^2) for each
chirality, k^2 = g_U^2/(2 M_X^2), M_X = M_U, W0 = 0.131 GeV^2; A_R = A_L x A_SD with A_L = 1.25 and A_SD from the
one-loop operator anomalous dimensions integrated with the two-loop couplings (gamma_ec = (23/20, 9/4, 2),
gamma_e = (11/20, 9/4, 2)); A_SD^2 = (A_ec^2 + A_e^2)/2.  (Same normalisation as R2-B skeptic / designer.)
Landau: SO(10) phase, b = -88/3 + 2/3*2*(#16) + 2/3*(#10_F) + 1/3*35 + 1/3*1 + 1/6*56 and own two-loop coefficient.
"""
import math, json, sys
from fractions import Fraction as Fr
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

PI = math.pi; MZ = 91.1876
AEM, S2W, AS = 127.951, 0.23122, 0.1180
A0 = np.array([0.6 * (1 - S2W) * AEM, S2W * AEM, 1.0 / AS])
CG = [0.0, 2.0, 3.0]
SU2 = {1: (0.0, 0.0), 2: (0.5, 0.75), 3: (2.0, 2.0)}                 # dim: (T, C2)
SU3 = {1: (0.0, 0.0), 3: (0.5, 4 / 3), 6: (2.5, 10 / 3), 8: (3.0, 3.0)}


def rep(d3, d2, y):
    T3, C3 = SU3[d3]; T2, C2 = SU2[d2]; y1 = 0.6 * y * y
    S = [y1 * d3 * d2, T2 * d3, T3 * d2]          # S_i (index x other dims), U(1): 3/5 Y^2 x dim
    C = [y1, C2, C3]
    return S, C


def coeffs(content):
    """content: list of (kind, d3, d2, Y, multiplicity), kind in weyl/cplx/real."""
    b = np.array([-11 / 3 * c for c in CG]); bij = np.diag([-34 / 3 * c * c for c in CG])
    for kind, d3, d2, y, n in content:
        S, C = rep(d3, d2, y)
        for i in range(3):
            if kind == "weyl":
                b[i] += n * 2 / 3 * S[i]
                for j in range(3):
                    bij[i, j] += n * S[i] * (2 * C[j] + (10 / 3 * CG[i] if i == j else 0))
            else:
                f = 1.0 if kind == "cplx" else 0.5
                b[i] += n * f * 1 / 3 * S[i]
                for j in range(3):
                    bij[i, j] += n * f * S[i] * (4 * C[j] + (2 / 3 * CG[i] if i == j else 0))
    return b, bij


GEN = [("weyl", 3, 2, 1 / 6, 1), ("weyl", 3, 1, -2 / 3, 1), ("weyl", 3, 1, 1 / 3, 1), ("weyl", 1, 2, -1 / 2, 1), ("weyl", 1, 1, 1, 1)]
NUC = [("weyl", 1, 1, 0, 1)]
TEN = [("weyl", 3, 1, -1 / 3, 1), ("weyl", 3, 1, 1 / 3, 1), ("weyl", 1, 2, 1 / 2, 1), ("weyl", 1, 2, -1 / 2, 1)]
SM = [(k, a, b, y, 3 * n) for k, a, b, y, n in GEN] + [("cplx", 1, 2, 1 / 2, 1)]
B63 = [(k, a, b, y, 6 * n) for k, a, b, y, n in GEN + NUC] + [(k, a, b, y, 2 * n) for k, a, b, y, n in TEN]   # 3x(16+16bar) + 2x10
LIGHT = {"(8,3,0)": ("real", 8, 3, 0.0, 1), "(6,2,-1/6)": ("cplx", 6, 2, -1 / 6, 1)}
GAM_EC = np.array([23 / 20, 9 / 4, 2.0]); GAM_E = np.array([11 / 20, 9 / 4, 2.0])
CT = np.array([17 / 10, 3 / 2, 2.0])


def check_sm():
    b, bij = coeffs(SM)
    return b, bij


def run(m8, m6, M_s=1e13, y_s=0.336, yt0=0.95, ys_term=True, t_end=math.log(3e18)):
    thr = sorted([(math.log(M_s), "B63"), (math.log(m8), "(8,3,0)"), (math.log(m6), "(6,2,-1/6)")])
    pts = [math.log(MZ)] + [t for t, _ in thr] + [t_end]
    active = []
    Y = np.concatenate([A0, [0.0, 0.0, yt0]])
    segs = []
    for k, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        content = list(SM)
        has_s = False
        for t, nm in thr:
            if t <= a + 1e-12:
                if nm == "B63":
                    content += B63; has_s = True
                else:
                    content.append(LIGHT[nm])
        bb, bij = coeffs(content)

        def rhs(t, Yv, bb=bb, bij=bij, has_s=has_s):
            ai = Yv[:3]; al = 1 / ai; yt = Yv[5]
            d = -bb / (2 * PI) - bij @ al / (8 * PI ** 2) + CT * yt ** 2 / (32 * PI ** 3)
            if has_s and ys_term:
                d = d + 14 * y_s ** 2 / (32 * PI ** 3)
            g2 = 4 * PI * al
            dyt = yt / (16 * PI ** 2) * (4.5 * yt ** 2 - 8 * g2[2] - 2.25 * g2[1] - 0.85 * g2[0])
            dA = np.array([GAM_EC @ al, GAM_E @ al]) / (2 * PI)
            return np.concatenate([d, dA, [dyt]])
        sol = solve_ivp(rhs, (a, b), Y, method="DOP853", rtol=1e-11, atol=1e-13, dense_output=True)
        segs.append((a, b, sol)); Y = sol.y[:, -1]
    return segs


def at(segs, t):
    for a, b, s in segs:
        if a - 1e-9 <= t <= b + 1e-9:
            return s.sol(t)
    raise ValueError


SV = np.array([8.0, 6.0, 5.0]) / (12 * PI)


def unify(m8, m6, **kw):
    segs = run(m8, m6, **kw)
    f = lambda t: (at(segs, t)[0] + SV[0]) - (at(segs, t)[1] + SV[1])
    ts = np.linspace(math.log(1e13), math.log(2.9e18), 200); v = [f(t) for t in ts]
    for i in range(len(ts) - 1):
        if v[i] * v[i + 1] < 0:
            r = brentq(f, ts[i], ts[i + 1], xtol=1e-13); Y = at(segs, r)
            a = Y[:3] + SV
            return {"M_U": math.exp(r), "aU": float(a[1]), "d3": float(a[2] - a[1]), "A_SD": math.sqrt(0.5 * (math.exp(2 * Y[3]) + math.exp(2 * Y[4]))),
                    "yt_MU": float(Y[5])}
    return None


def tau_lat(MX, aU, AR, W0=0.131, Vud=0.97367):
    mp, mpi = 0.93827208816, 0.1349768; hbar = 6.582119569e-25; yr = 3.15576e7
    k2 = (4 * PI / aU) / (2 * MX ** 2)
    C = 2 * k2 * (1 + Vud ** 2)
    G = mp / (32 * PI) * (1 - (mpi / mp) ** 2) ** 2 * AR ** 2 * W0 ** 2 * 2 * C ** 2
    return hbar / G / yr


# SO(10) phase (index T(10) = 1; C2(R) = T(R) * 45 / dim R)
SO10 = {"10": (1, 10), "16": (2, 16), "126": (35, 126), "210": (56, 210), "45": (8, 45)}


def so10_b(content):
    CGs = 8.0; b1 = -11 / 3 * CGs; b2 = -34 / 3 * CGs ** 2
    for kind, r, n in content:
        T, d = SO10[r]; C2 = T * 45 / d
        if kind == "weyl":
            b1 += n * 2 / 3 * T; b2 += n * T * (2 * C2 + 10 / 3 * CGs)
        else:
            f = 1.0 if kind == "cplx" else 0.5
            b1 += n * f / 3 * T; b2 += n * f * T * (4 * C2 + 2 / 3 * CGs)
    return b1, b2


def landau(MU, aU, MPHI=1e17, MPL=2.435e18):
    base = [("weyl", "16", 9), ("weyl", "10", 2), ("real", "210", 1), ("cplx", "126", 1), ("cplx", "10", 1)]
    hi = base + [("weyl", "16", 2)]
    b_lo, b2_lo = so10_b(base); b_hi, b2_hi = so10_b(hi)

    def rhs(t, y, b1, b2):
        a = 1 / y[0]
        return [-b1 / (2 * PI) - b2 * a / (8 * PI ** 2)]
    ev = lambda t, y, b1, b2: y[0] - 1e-3
    ev.terminal = True
    t0 = math.log(MU); t1 = math.log(max(MPHI, MU))
    s = solve_ivp(rhs, (t0, t1), [aU], args=(b_lo, b2_lo), events=ev, rtol=1e-10, atol=1e-12)
    if s.status == 1:
        return math.exp(s.t[-1]) / MPL, (b_lo, b2_lo)
    s2 = solve_ivp(rhs, (t1, math.log(1e25)), [s.y[0, -1]], args=(b_hi, b2_hi), events=ev, rtol=1e-10, atol=1e-12)
    return (math.exp(s2.t[-1]) / MPL if s2.status == 1 else float("inf")), (b_lo, b2_lo)


if __name__ == "__main__":
    out = {}
    b, bij = check_sm()
    out["SM_b"] = b.tolist(); out["SM_bij"] = bij.tolist()
    print("SM check b =", np.round(b, 4), "\nbij =", np.round(bij, 4))
    # heavy vector S_V: (3,2,-5/6)+(3,2,1/6)+(3,1,2/3)+(1,1,1) (+cc), each a complex vector: S_i summed x2 (cc)
    sv = np.zeros(3)
    for d3, d2, y in ((3, 2, -5 / 6), (3, 2, 1 / 6), (3, 1, 2 / 3), (1, 1, 1)):
        S, _ = rep(d3, d2, y); sv += 2 * np.array(S)
    out["S_V_own"] = sv.tolist(); print("S_V own =", sv)
    res = {}
    for label, kw in (("nominal", {}), ("no_ys_term", {"ys_term": False}), ("yt0.94", {"yt0": 0.94}), ("Ms5e12", {"M_s": 5e12}),
                      ("Ms1.21e13_ys0.368", {"M_s": 1.21e13, "y_s": 0.368})):
        u = unify(2.51e11, 1.99e9, **kw)
        AR = 1.25 * u["A_SD"]
        u["A_R"] = AR; u["tau_lat"] = tau_lat(u["M_U"], u["aU"], AR)
        L2, bb = landau(u["M_U"], u["aU"]); u["L2"] = L2; u["so10_b1_b2"] = bb
        res[label] = u
        print(label, json.dumps(u, default=float))
    # solve the family: for m8 given, find m6 with d3 = 0
    fam = []
    for lm8 in np.linspace(10.6, 12.6, 11):
        g = lambda lm6: unify(10 ** lm8, 10 ** lm6)["d3"]
        grid = np.linspace(3.5, 15.0, 47); vals = []
        for x in grid:
            try:
                vals.append(g(x))
            except Exception:
                vals.append(float("nan"))
        for i in range(len(grid) - 1):
            if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0:
                lm6 = brentq(g, grid[i], grid[i + 1], xtol=1e-6); u = unify(10 ** lm8, 10 ** lm6)
                AR = 1.25 * u["A_SD"]; tau = tau_lat(u["M_U"], u["aU"], AR); L2, _ = landau(u["M_U"], u["aU"])
                fam.append({"m8": 10 ** lm8, "m6": 10 ** lm6, "M_U": u["M_U"], "aU": u["aU"], "A_R": AR, "tau": tau, "L2": L2})
                print(f"  m8={10**lm8:.3e} m6={10**lm6:.3e} M_U={u['M_U']:.3e} aU={u['aU']:.2f} A_R={AR:.2f} tau={tau:.2e} L2={L2:.2f}", flush=True)
                break
    out["nominal_point_variants"] = res; out["family"] = fam
    json.dump(out, open("sk_unif.json", "w"), indent=1, default=float)
