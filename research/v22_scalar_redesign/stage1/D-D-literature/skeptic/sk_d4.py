#!/usr/bin/env python3
"""SKEPTIC (D-D-literature, design L2 = v20 + real 45_H): independent D4 recomputation.

Written from scratch (no import of the designer's r2b_lib / r2b_model / d4_unif):
  * Machacek-Vaughn one- and two-loop gauge coefficients computed here with Fractions from the field table;
  * SM phase: SM + 1 Higgs doublet + light (8,1,0)_real + (8,3,0)_real + B63 S-sector (3x(16+16bar) + 2x10 Weyl) at M_s;
    two-loop gauge + one-loop-run top Yukawa (SM 2-loop Yukawa coefficients 17/10, 3/2, 2) + B63 y_s term;
  * one-loop MS-bar matching at M_U: alpha_i^-1(M_U) = alpha_U^-1 - S_V,i/(12 pi), S_V = (8, 6, 5) recomputed here;
  * SO(10) phase two-loop with the design's content, Landau := alpha_U = 1 (the designer's definition);
  * tau(p -> e+ pi0), direct lattice normalisation, W0 = 0.131 GeV^2, A_R = A_L * A_SD with A_SD recomputed from the
    one-loop segment exponents (gamma = 2 for SU(3), 9/4 SU(2), 23/20 U(1)), A_L = 1.25.
Sensitivity variants (the decisive item is Lambda_2L / M_Pl,red, nominal 1.04 per the designer).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

HERE = Path(__file__).resolve().parent
PI = math.pi
MZ = 91.1876
MPL = 2.435e18

# ---------------- group data ----------------
SU3 = {"1": (1, F(0), F(0)), "3": (3, F(1, 2), F(4, 3)), "8": (8, F(3), F(3)), "6": (6, F(5, 2), F(10, 3))}
SU2 = {"1": (1, F(0), F(0)), "2": (2, F(1, 2), F(3, 4)), "3": (3, F(2), F(2))}
CG_SM = (F(0), F(2), F(3))


def reps(su3, su2, Y):
    q2 = F(3, 5) * F(Y) ** 2
    return [(1, q2, q2), SU2[su2], SU3[su3]]


def mv(fields, CG):
    """fields: list of (kind, reps(list of (dim,T,C2) per factor), mult). Returns b (list), bij (matrix) exact."""
    n = len(CG)
    b = [F(-11, 3) * CG[i] for i in range(n)]
    bij = [[(F(-34, 3) * CG[i] ** 2 if i == j else F(0)) for j in range(n)] for i in range(n)]
    for kind, rp, m in fields:
        for i in range(n):
            S = rp[i][1]
            for k in range(n):
                if k != i:
                    S *= rp[k][0]
            S *= m
            if S == 0:
                continue
            c1 = {"weyl": F(2, 3), "cplx": F(1, 3), "real": F(1, 6)}[kind]
            b[i] += c1 * S
            for j in range(n):
                c2j = rp[j][2]
                if kind == "weyl":
                    bij[i][j] += S * (2 * c2j + (F(10, 3) * CG[i] if i == j else 0))
                elif kind == "cplx":
                    bij[i][j] += S * (4 * c2j + (F(2, 3) * CG[i] if i == j else 0))
                else:
                    bij[i][j] += S * (2 * c2j + (F(1, 3) * CG[i] if i == j else 0))
    return b, bij


GEN = [("weyl", reps("3", "2", F(1, 6)), 1), ("weyl", reps("3", "1", F(-2, 3)), 1), ("weyl", reps("3", "1", F(1, 3)), 1),
       ("weyl", reps("1", "2", F(-1, 2)), 1), ("weyl", reps("1", "1", F(1)), 1)]   # nu^c is a gauge singlet
TEN = [("weyl", reps("3", "1", F(-1, 3)), 1), ("weyl", reps("3", "1", F(1, 3)), 1), ("weyl", reps("1", "2", F(1, 2)), 1),
       ("weyl", reps("1", "2", F(-1, 2)), 1)]
HIGGS = [("cplx", reps("1", "2", F(1, 2)), 1)]
LIGHT = {"(8,1,0)": [("real", reps("8", "1", 0), 1)], "(8,3,0)": [("real", reps("8", "3", 0), 1)],
         "(6,3,1/3)": [("cplx", reps("6", "3", F(1, 3)), 1)], "Hd2": [("cplx", reps("1", "2", F(1, 2)), 2)]}


def scale(fl, m):
    return [(k, r, mm * m) for k, r, mm in fl]


def sm_content(active, with_s):
    f = scale(GEN, 3) + HIGGS
    if with_s:
        f += scale(GEN, 6) + scale(TEN, 2)
    for a in active:
        f += LIGHT[a]
    return f


# ---------------- check SM coefficients ----------------
b_sm, bij_sm = mv(sm_content([], False), CG_SM)
assert b_sm == [F(41, 10), F(-19, 6), F(-7)], b_sm
assert bij_sm == [[F(199, 50), F(27, 10), F(44, 5)], [F(9, 10), F(35, 6), F(12)], [F(11, 10), F(9, 2), F(-26)]], bij_sm

# heavy vectors (complex, each counted with its conjugate -> x2 real-vector multiplets): S_V per SM factor


def sv():
    vec = [(reps("3", "2", F(-5, 6)), 2), (reps("3", "2", F(1, 6)), 2), (reps("3", "1", F(2, 3)), 2),
           (reps("1", "1", F(1)), 2)]
    out = []
    for i in range(3):
        s = F(0)
        for rp, m in vec:
            S = rp[i][1]
            for k in range(3):
                if k != i:
                    S *= rp[k][0]
            s += S * m / 2 * 2   # each complex vector = 2 real; Dynkin per complex rep incl. conjugate: m counts rep+cc
        out.append(s)
    return out


SV = sv()
# rep + cc each with Dynkin index: X: SU3 2*(2 x 1/2)=2, X':2, V3: 1 -> 5; SU2: X 3, X' 3 -> 6; U1 -> 8
assert [x for x in SV] == [F(8), F(6), F(5)], SV


class SMRun:
    def __init__(self, a0=(59.02, 29.57, 1 / 0.1179), yt0=0.97, M_s=1e13, y_s=0.336, light=(), M_light=(),
                 cY_s=14.0):
        self.a0 = np.array(a0, float)
        self.yt0, self.M_s, self.y_s, self.cY_s = yt0, M_s, y_s, cY_s
        self.light, self.M_light = list(light), list(M_light)
        self.cache = {}

    def coeffs(self, active, with_s):
        k = (tuple(sorted(active)), with_s)
        if k not in self.cache:
            b, bij = mv(sm_content(active, with_s), CG_SM)
            self.cache[k] = (np.array([float(x) for x in b]), np.array([[float(x) for x in r] for r in bij]))
        return self.cache[k]

    def rhs_factory(self, active, with_s):
        b, bij = self.coeffs(active, with_s)
        cy = np.array([1.7, 1.5, 2.0])
        ys2 = self.y_s ** 2 if with_s else 0.0
        cs = self.cY_s

        def rhs(t, y):
            ainv = y[:3]
            yt = y[3]
            al = 1 / ainv
            g2 = 4 * PI * al
            da = -b / (2 * PI) - bij @ al / (8 * PI ** 2) + (cy * yt ** 2 + cs * ys2) / (32 * PI ** 3)
            dyt = yt / (16 * PI ** 2) * (4.5 * yt ** 2 - 0.85 * g2[0] - 2.25 * g2[1] - 8 * g2[2])
            return np.concatenate([da, [dyt]])
        return rhs

    def run(self, M_U, segments=False):
        pts = sorted([(m, n) for n, m in zip(self.light, self.M_light) if m < M_U] +
                     ([(self.M_s, "S")] if self.M_s < M_U else []))
        y = np.concatenate([self.a0, [self.yt0]])
        t = math.log(MZ)
        active, with_s = [], False
        segs = []
        for m, n in pts + [(M_U, None)]:
            tm = math.log(max(m, MZ))
            if tm > t:
                y0 = y.copy()
                sol = solve_ivp(self.rhs_factory(active, with_s), (t, tm), y, method="DOP853", rtol=1e-11, atol=1e-13)
                y = sol.y[:, -1]
                segs.append((t, tm, y0[:3].copy(), y[:3].copy(), self.coeffs(active, with_s)[0].copy()))
                t = tm
            if n == "S":
                with_s = True
            elif n is not None:
                active.append(n)
        return (y, segs) if segments else y


def solve_unif(run: SMRun, free_idx, guess=(math.log(1.3e16), 27.0, math.log(1.7e9))):
    def f(x):
        lnMU, aU, lnML = x
        run.M_light[free_idx] = math.exp(lnML)
        y = run.run(math.exp(lnMU))
        return y[:3] + np.array([float(s) for s in SV]) / (12 * PI) - aU
    best = None
    for g in [guess, (math.log(1e16), 28.0, math.log(3e9)), (math.log(2e16), 26.0, math.log(1e9))]:
        x, info, ier, msg = fsolve(f, np.array(g, float), full_output=True, xtol=1e-13)
        r = np.max(np.abs(f(x)))
        if r < 1e-8 and (best is None or r < best[1]):
            best = (x, r)
    if best is None:
        return None
    x = best[0]
    run.M_light[free_idx] = math.exp(x[2])
    y, segs = run.run(math.exp(x[0]), segments=True)
    return {"M_U": math.exp(x[0]), "aU_inv": float(x[1]), "M_free": math.exp(x[2]), "resid": best[1],
            "yt_MU": float(y[3]), "segs": segs}


def A_SD(segs, gam=(23 / 20, 9 / 4, 2.0)):
    A = 1.0
    for t0, t1, a0, a1, b in segs:
        for i in range(3):
            if abs(b[i]) < 1e-12:
                A *= math.exp(gam[i] * (t1 - t0) / (2 * PI * a0[i]))
            else:
                A *= (a1[i] / a0[i]) ** (-gam[i] / b[i])
    return A


def tau_lattice(M_X, aU_inv, A_R, W0=0.131, Vud=0.97367):
    m_p, m_pi = 0.93827, 0.13498
    x = (m_pi / m_p) ** 2
    al = 1 / aU_inv
    gam = (PI * m_p / 2) * (1 - x) ** 2 * A_R ** 2 * W0 ** 2 * al ** 2 * ((1 + Vud ** 2) ** 2 + 4) / M_X ** 4
    return 6.582119569e-25 / gam / 3.15576e7


# ---------------- SO(10) phase ----------------
SO10 = {"10": (10, F(1), F(9, 2)), "16": (16, F(2), F(45, 8)), "45": (45, F(8), F(8)), "54": (54, F(12), F(10)),
        "126": (126, F(35), F(25, 2)), "210": (210, F(56), F(12))}


def so10_b(content):
    """content: list of (irrep, kind, mult)"""
    f = [(k, [SO10[r]], m) for r, k, m in content]
    b, bij = mv(f, (F(8),))
    return b[0], bij[0][0]


def so10_contents(scalars):
    ferm_lo = [("16", "weyl", 9), ("10", "weyl", 2)]
    ferm_hi = [("16", "weyl", 11), ("10", "weyl", 2)]
    sc = []
    for s in scalars:
        sc.append({"210": ("210", "real", 1), "126b": ("126", "cplx", 1), "10": ("10", "cplx", 1),
                   "45": ("45", "real", 1), "54": ("54", "real", 1)}[s])
    return ferm_lo + sc, ferm_hi + sc


def landau(M_U, aU_inv, scalars, Y_lo, Y_hi, M_phi=1e17, b3=None):
    lo, hi = so10_contents(scalars)
    b1l, b2l = [float(x) for x in so10_b(lo)]
    b1h, b2h = [float(x) for x in so10_b(hi)]

    def rhs_f(b1, b2, Y):
        def rhs(t, y):
            a = 1 / y[0]
            return [-b1 / (2 * PI) - b2 * a / (8 * PI ** 2) + Y / (32 * PI ** 3)]
        return rhs

    def ev(t, y):
        return y[0] - 1.0
    ev.terminal = True
    ev.direction = -1
    t0, tp = math.log(M_U), math.log(max(M_phi, M_U))
    sol = solve_ivp(rhs_f(b1l, b2l, Y_lo), (t0, tp), [aU_inv], events=ev, rtol=1e-11, atol=1e-12, max_step=0.05)
    if sol.t_events[0].size:
        return math.exp(sol.t_events[0][0]) / MPL, (b1l, b2l)
    sol2 = solve_ivp(rhs_f(b1h, b2h, Y_hi), (tp, math.log(1e25)), [sol.y[0, -1]], events=ev, rtol=1e-11, atol=1e-12,
                     max_step=0.05)
    if sol2.t_events[0].size:
        return math.exp(sol2.t_events[0][0]) / MPL, (b1l, b2l)
    return float("inf"), (b1l, b2l)


def point(M8=1e3, a0=(59.02, 29.57, 1 / 0.1179), M_s=1e13, y_s=0.336, scalars=("210", "126b", "10", "45"),
          extra_light=(), Y126_tr2=0.5, c_u10=1.0, yt0=0.97, M_phi=1e17, y_phi=1.0, light2="(8,3,0)"):
    light = ["(8,1,0)", light2] + [e[0] for e in extra_light]
    ML = [M8, 1.7e9] + [e[1] for e in extra_light]
    run = SMRun(a0=a0, yt0=yt0, M_s=M_s, y_s=y_s, light=light, M_light=ML)
    r = solve_unif(run, 1)
    if r is None:
        return None
    A = 1.25 * A_SD(r["segs"])
    Y10sq = r["yt_MU"] ** 2 / c_u10 ** 2
    Y_lo = 14 * y_s ** 2 + 10 * Y10sq + 2 * (126 / 16) * Y126_tr2
    Y_hi = Y_lo + 4 * y_phi ** 2
    L2, bb = landau(r["M_U"], r["aU_inv"], scalars, Y_lo, Y_hi, M_phi=M_phi)
    return {"M8": M8, "M_second": r["M_free"], "M_U": r["M_U"], "aU_inv": r["aU_inv"], "A_R": A,
            "tau_lat_yr": tau_lattice(r["M_U"], r["aU_inv"], A), "L2_over_MPl": L2, "yt_MU": r["yt_MU"],
            "b_so10_lo": bb, "Y_lo": Y_lo}


def main():
    out = {"S_V": [str(x) for x in SV]}
    lo, hi = so10_contents(("210", "126b", "10", "45"))
    out["b_so10_L2_lo"] = [str(x) for x in so10_b(lo)]
    lo1, _ = so10_contents(("210", "126b", "10"))
    out["b_so10_L1_lo"] = [str(x) for x in so10_b(lo1)]
    print("S_V", out["S_V"], "b_so10 L2", out["b_so10_L2_lo"], "L1", out["b_so10_L1_lo"], flush=True)
    rows = {}

    def rec(name, **kw):
        r = point(**kw)
        rows[name] = {k: v for k, v in (r or {}).items()}
        if r:
            print(f"{name:58s} M2nd {r['M_second']:.3g} M_U {r['M_U']:.4g} aU^-1 {r['aU_inv']:.3f} A_R {r['A_R']:.2f} "
                  f"tau {r['tau_lat_yr']:.3g} L2L/MPl {r['L2_over_MPl']:.3f}", flush=True)
        else:
            print(name, "no solution", flush=True)

    # designer-like nominal
    rec("L2 nominal (designer inputs) M8=1e3", M8=1e3)
    rec("L2 nominal M8=1e4", M8=1e4)
    rec("L1 nominal (no 45) M8=1e3", M8=1e3, scalars=("210", "126b", "10"))
    # PDG 2024 central alpha_s and its 1-sigma band; alpha^-1(MZ)=127.930, s2=0.23129 -> a1, a2
    for nm, aem, s2 in (("PDG24 a=127.930 s2=0.23129", 127.930, 0.23129), ("PDG24 a=127.951 s2=0.23121", 127.951, 0.23121)):
        a1 = 0.6 * aem * (1 - s2)
        a2 = aem * s2
        for als in (0.1171, 0.1180, 0.1189):
            rec(f"L2 {nm} als={als} M8=1e3", M8=1e3, a0=(a1, a2, 1 / als))
    # flavour-consistent Yukawa traces (D2 best point: Y126 <= 0.08, c_u10 = 0.91)
    rec("L2 Y126_tr2=0.006 c_u10=0.91 M8=1e3", M8=1e3, Y126_tr2=0.006, c_u10=0.91)
    # LHC-motivated octet masses
    for m8 in (1.5e3, 2e3, 3e3):
        rec(f"L2 M8={m8:.0e}", M8=m8)
    # forced intermediate down-type doublets (PQ cross-mixing, EST m_D ~ 5e15)
    rec("L2 + 2 doublets at 5e15 M8=1e3", M8=1e3, extra_light=(("Hd2", 5e15),))
    # y_s at the gauge-independent cap and M_s variants
    rec("L2 y_s=0.3166 M_s=1e13 M8=1e3", M8=1e3, y_s=0.3166)
    rec("L2 M_s=1.21e13 y_s=0.368 M8=1e3", M8=1e3, M_s=1.21e13, y_s=0.368)
    rec("L2 M_s=8e12 M8=1e3", M8=1e3, M_s=8e12)
    rec("L2 M_s=5e12 M8=1e3", M8=1e3, M_s=5e12)
    # combined 'realistic nominal': PDG24 central, flavour Yukawas, M8 = 2 TeV
    a1 = 0.6 * 127.930 * (1 - 0.23129)
    a2 = 127.930 * 0.23129
    rec("L2 combined: PDG24(127.930,0.23129,0.1180), Y126 0.006, c_u10 0.91, M8=2e3", M8=2e3, a0=(a1, a2, 1 / 0.1180),
        Y126_tr2=0.006, c_u10=0.91)
    rec("L2 combined + 2 doublets 5e15", M8=2e3, a0=(a1, a2, 1 / 0.1180), Y126_tr2=0.006, c_u10=0.91,
        extra_light=(("Hd2", 5e15),))
    out["rows"] = rows
    (HERE / "sk_d4.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
