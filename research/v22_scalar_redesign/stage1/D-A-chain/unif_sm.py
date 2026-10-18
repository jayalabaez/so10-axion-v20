#!/usr/bin/env python3
"""D-A-chain / D4 screen: SO(10) -> SM DIRECTLY at M_U (SU(2)_R and SU(4) broken at M_U), SM + light split scalars
below M_U, B63 S-sector 3x(16+16bar) + 2x10 (Weyl) at M_s, Phi pair 16+16bar at M_Phi (> M_U, SO(10) phase only).

Exact Machacek-Vaughn one/two-loop coefficients (r2b_lib.mv_coefficients, copied unedited from R2-B), top + y_s
two-loop Yukawa terms in R2-B's convention, heavy-vector MS-bar constant S_V/(12 pi) at M_U for the SM-direct vector
set (3,2,-5/6)+(3,2,1/6)+(3,1,2/3)+(1,1,1) (+cc) + (1,1,0): S_V = (8, 6, 5) (computed below, EXACT).
Unification: alpha_i^-1(M_U) + S_V,i/(12 pi) = alpha_U^-1 for i = 1,2,3 (all heavy scalars at M_U = nominal).
Proton: lattice normalisation (sk2_lib.tau_lattice: W0 = 0.131 GeV^2, X and X' degenerate at M_U) x chain-specific
A_R = 1.25 A_SD, A_SD from the one-loop operator anomalous dimensions integrated along THIS chain (sk2_asd.py method),
channel-weighted A_R^2 = A_L^2 (A_ec^2 + A_e^2)/2.
Landau: SO(10) phase pure gauge from M_U (diagnosis/landau_screen.py method, B63 + 210 + 126bar + 10, Phi pair at 1e17).
Labels: NUM (two-loop, +-0.3 in alpha^-1 from omitted GUT thresholds is NOT included; see thr scan)."""
from __future__ import annotations
import math, json, sys, itertools
from fractions import Fraction as F
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from r2b_lib import SU2, SU3, ysm, mv_coefficients, s_factor, SO10, C_G_SO10, pgj_b, pgj_invariants, Segment, run_segment, M_PL_RED

PI = math.pi
MZ = 91.1876
# PDG 2024: alpha_s(MZ) = 0.1180, alpha_em^-1(MZ) MSbar = 127.951, sin^2 theta_W MSbar = 0.23122
AEM = 127.951; S2W = 0.23122; AS = 0.1180
A0 = np.array([0.6 * (1 - S2W) * AEM, S2W * AEM, 1.0 / AS])
YT_MZ = 0.95
SM_C2 = (F(0), F(2), F(3))


def smrep(y, su2, su3):
    return (ysm(F(y)), SU2[su2], SU3[su3])


SIXTEEN = [("Q", smrep(F(1, 6), "2", "3")), ("uc", smrep(F(-2, 3), "1", "3b")), ("dc", smrep(F(1, 3), "1", "3b")),
           ("L", smrep(F(-1, 2), "2", "1")), ("ec", smrep(1, "1", "1")), ("nuc", smrep(0, "1", "1"))]
TEN = [("D", smrep(F(-1, 3), "1", "3")), ("Dc", smrep(F(1, 3), "1", "3b")), ("Hu", smrep(F(1, 2), "2", "1")),
       ("Hd", smrep(F(-1, 2), "2", "1"))]
# candidate light scalars (SM irreps present in 210 (real), 126bar, 10 after SO(10) -> SM): name -> (kind, Y, su2, su3)
CAND = {
    "(8,3,0)R": ("real", F(0), "3", "8"),       # 210 (15,3,1)
    "(8,1,0)R": ("real", F(0), "1", "8"),       # 210 (15,1,1) / (15,1,3)
    "(1,3,0)R": ("real", F(0), "3", "1"),       # 210 (1,3,1) [(15,3,1) singlet part]
    "(8,2,1/2)": ("cplx", F(1, 2), "2", "8"),   # 126bar (15,2,2)
    "(6,3,1/3)": ("cplx", F(1, 3), "3", "6"),   # 126bar (6,3,1)
    "(3,3,-1/3)": ("cplx", F(-1, 3), "3", "3"),  # 126bar (10,3,1) - leptoquark/diquark (proton!)
    "(1,3,1)": ("cplx", F(1), "3", "1"),        # 126bar Delta_L
    "(1,2,1/2)": ("cplx", F(1, 2), "2", "1"),   # extra doublet
    "(6,2,-1/6)": ("cplx", F(-1, 6), "2", "6"),  # 210 (6,2,2)
    "(3,2,1/6)": ("cplx", F(1, 6), "2", "3"),   # 126bar/210 (leptoquark, proton!)
    "(8,1,1)": ("cplx", F(1), "1", "8"),        # 210 (15,1,3)
}


def cand_rep(name):
    kind, y, l, c = CAND[name]
    return (name, kind, smrep(y, l, c), 1)


def fields(t, light, M_s, n_h=1):
    """field table at scale t (ln mu): SM + light states with mass < mu + B63 above M_s."""
    out = [(n, "weyl", r, 3) for n, r in SIXTEEN]
    out.append(("H", "cplx", smrep(F(1, 2), "2", "1"), n_h))
    if t >= math.log(M_s):
        out += [(n, "weyl", r, 6) for n, r in SIXTEEN] + [(n, "weyl", r, 2) for n, r in TEN]
    for name, m in light:
        if t >= math.log(m):
            out.append(cand_rep(name))
    return out


def sv_sm():
    vec = [smrep(F(-5, 6), "2", "3"), smrep(F(1, 6), "2", "3"), smrep(F(2, 3), "1", "3"), smrep(1, "1", "1")]
    sv = []
    for i in range(3):
        s = F(0)
        for r in vec:
            s += 2 * s_factor(r, i)        # +cc
        sv.append(s)                       # (1,1,0) Z' has no SM charge
    return sv


SV = sv_sm()  # EXACT: (8, 6, 5)
GAM = {"ec": np.array([23 / 20, 9 / 4, 2.0]), "e": np.array([11 / 20, 9 / 4, 2.0])}


def run_chain(light, M_s=1e13, y_s=0.336, t_end=math.log(1e18), loops=2, n_h=1):
    """Return a dense solution object over [ln MZ, t_end] with alpha^-1 and the A_SD integrals (ec, e) appended."""
    thr = sorted(set([math.log(M_s)] + [math.log(m) for _, m in light if MZ < m < math.exp(t_end)]))
    pts = [math.log(MZ)] + [x for x in thr if math.log(MZ) < x < t_end] + [t_end]
    y = np.concatenate([A0, [0.0, 0.0]])
    segs = []
    yt = YT_MZ
    for a, b in zip(pts[:-1], pts[1:]):
        if b <= a:
            continue
        fl = fields(0.5 * (a + b), light, M_s, n_h)
        bb, bij = mv_coefficients(SM_C2, fl)
        bb = np.array([float(x) for x in bb]); bij = np.array([[float(x) for x in r] for r in bij])
        has_s = 0.5 * (a + b) >= math.log(M_s)

        def rhs(t, Y, bb=bb, bij=bij, has_s=has_s):
            ai = Y[:3]; al = 1.0 / ai
            d = -bb / (2 * PI)
            if loops >= 2:
                ytt = Y[5]
                yuk = np.array([1.7, 1.5, 2.0]) * ytt ** 2 + (14.0 * y_s ** 2 if has_s else 0.0)
                d = d - bij.dot(al) / (8 * PI ** 2) + yuk / (32 * PI ** 3)
            g2 = 4 * PI * al
            dyt = Y[5] / (16 * PI ** 2) * (4.5 * Y[5] ** 2 - 8 * g2[2] - 2.25 * g2[1] - 0.85 * g2[0])
            dA = np.array([np.sum(GAM["ec"] * al), np.sum(GAM["e"] * al)]) / (2 * PI)
            return np.concatenate([d, dA, [dyt]])
        Y0 = np.concatenate([y, [yt]])
        sol = solve_ivp(rhs, (a, b), Y0, method="DOP853", rtol=1e-10, atol=1e-12, dense_output=True)
        segs.append((a, b, sol))
        y = sol.y[:5, -1]; yt = sol.y[5, -1]
    return segs


def eval_at(segs, t):
    for a, b, sol in segs:
        if a - 1e-12 <= t <= b + 1e-12:
            return sol.sol(t)
    raise ValueError(t)


def unify(light, M_s=1e13, y_s=0.336, loops=2, n_h=1):
    """M_U from alpha1' = alpha2' (S_V-corrected); returns M_U, alpha_U^-1, mismatch d3 = alpha3' - alpha2'."""
    segs = run_chain(light, M_s, y_s, loops=loops, n_h=n_h)
    sv = np.array([float(x) for x in SV]) / (12 * PI)

    def f12(t):
        Y = eval_at(segs, t); a = Y[:3] + sv
        return a[0] - a[1]
    ts = np.linspace(math.log(1e12), math.log(1e18) - 1e-6, 120)
    vals = [f12(t) for t in ts]
    root = None
    for i in range(len(ts) - 1):
        if vals[i] > 0 >= vals[i + 1] or vals[i] < 0 <= vals[i + 1]:
            root = brentq(f12, ts[i], ts[i + 1], xtol=1e-12); break
    if root is None:
        return None
    Y = eval_at(segs, root); a = Y[:3] + sv
    return {"M_U": math.exp(root), "aU": float(a[1]), "d3": float(a[2] - a[1]), "A_ec": math.exp(Y[3]), "A_e": math.exp(Y[4]),
            "yt_MU": float(Y[5])}


def tau_lattice(MX, aUinv, AR, W0=0.131, Vud=0.9737):
    m_p, m_pi = 0.9382720813, 0.1349768
    HBAR, YEAR = 6.582119569e-25, 365.25 * 24 * 3600
    k2 = 4 * PI / aUinv / (2 * MX ** 2)
    sumC2 = 4 * k2 ** 2 * 2 * (1 + Vud ** 2) ** 2
    gam = (m_p / (32 * PI)) * (1 - (m_pi / m_p) ** 2) ** 2 * AR ** 2 * W0 ** 2 * sumC2
    return HBAR / gam / YEAR


def tau_repo(MX, aUinv):
    f_pi, m_p, a_h, A_R, F_q = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    HBAR, YEAR = 6.582119569e-25, 365.25 * 24 * 3600
    t = (4 / PI) * (f_pi ** 2 / m_p) * MX ** 4 * aUinv ** 2 / (a_h ** 2 * A_R ** 2 * F_q)
    return t * HBAR / YEAR


# ---- SO(10)-phase Landau (diagnosis/landau_screen.py method) ----
BASE = [("16", "weyl", 3), ("16", "weyl", 3), ("16b", "weyl", 3), ("10", "weyl", 2),
        ("210", "real", 1), ("126b", "cplx", 1), ("10", "cplx", 1)]
PHI = [("16", "weyl", 1), ("16b", "weyl", 1)]


def so10_coeffs(content):
    return pgj_b(pgj_invariants(content, SO10, C_G_SO10))


def landau(MU, aU, loops, extra=(), MPHI=1e17):
    content = BASE + list(extra)
    lo = so10_coeffs(content); hi = so10_coeffs(content + PHI)

    def seg(b):
        return Segment([b[0]], [[b[1]]], b3=[b[2]], loops=loops)
    y, t, hit = run_segment(seg(lo), np.array([aU]), math.log(MU), math.log(max(MPHI, MU)), landau_event=True)
    if not hit:
        y, t, hit = run_segment(seg(hi), y, math.log(max(MPHI, MU)), math.log(1e24), landau_event=True)
    return (math.exp(t) / M_PL_RED) if hit else float("inf")


def point(light, M_s=1e13, y_s=0.336, extra_so10=(), n_h=1):
    u = unify(light, M_s, y_s, n_h=n_h)
    if u is None:
        return None
    AR = 1.25 * math.sqrt(0.5 * (u["A_ec"] ** 2 + u["A_e"] ** 2))
    u["A_R"] = AR
    u["tau_lat"] = tau_lattice(u["M_U"], u["aU"], AR)
    u["tau_repo"] = tau_repo(u["M_U"], u["aU"])
    u["L2"] = landau(u["M_U"], u["aU"], 2, extra_so10)
    u["L3"] = landau(u["M_U"], u["aU"], 3, extra_so10)
    return u


if __name__ == "__main__":
    print("S_V (SM-direct heavy vectors) =", [str(x) for x in SV])
    print("alpha^-1(MZ) =", A0)
    base = point([])
    print("SM + B63 only:", {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in base.items()})
    # SM-only A_SD to 1e16 cross-check with sk2 (2.48 / 2.32)
    segs = run_chain([], M_s=1e30, t_end=math.log(1e16))
    Y = eval_at(segs, math.log(1e16))
    print("SM-only A_SD(ec, e) to 1e16 =", math.exp(Y[3]), math.exp(Y[4]))
