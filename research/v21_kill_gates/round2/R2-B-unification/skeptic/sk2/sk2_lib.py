#!/usr/bin/env python3
"""Second (adversarial) skeptic of R2-B: fully independent re-implementation (no import of r2b_*/k1_*/sk_* code).

Group theory, Machacek-Vaughn one/two-loop coefficients, G3221 field content of 210 (real) + 126bar + 10 (complex),
B63 S-sector, one-loop MS-bar matching incl. the heavy-vector constant (Hall/Weinberg form), two-loop running,
unification solve, SO(10) two-loop alpha = 1 scale, proton lifetime in two normalisations.
Conventions: t = ln(mu/GeV); d alpha_i^-1/dt = -b_i/(2 pi) - sum_j b_ij alpha_j/(8 pi^2) + Y_i/(32 pi^3).
"""
from __future__ import annotations

import math
from fractions import Fraction as Fr

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

PI = math.pi
MZ = 91.1876
A1I_MZ, A2I_MZ, A3_MZ = 59.02, 29.57, 0.1179     # same inputs as the gate (repository inputs)
MPL = 2.435e18

# ---------------- representation data (dim, Dynkin index T, quadratic Casimir C) ----------------
SU3 = {"1": (1, Fr(0), Fr(0)), "3": (3, Fr(1, 2), Fr(4, 3)), "3b": (3, Fr(1, 2), Fr(4, 3)),
       "6": (6, Fr(5, 2), Fr(10, 3)), "6b": (6, Fr(5, 2), Fr(10, 3)), "8": (8, Fr(3), Fr(3))}
SU2 = {"1": (1, Fr(0), Fr(0)), "2": (2, Fr(1, 2), Fr(3, 4)), "3": (3, Fr(2), Fr(2))}


def u1(q2: Fr):
    return (1, q2, q2)


def qY(Y):      # GUT-normalised hypercharge squared
    return u1(Fr(3, 5) * Fr(Y) ** 2)


def qBL(x):     # GUT-normalised B-L squared, X = sqrt(3/8)(B-L)
    return u1(Fr(3, 8) * Fr(x) ** 2)


# factor orders: SM = (U1Y, SU2L, SU3);  G = (SU3, SU2L, SU2R, U1BL)
CG_SM = (Fr(0), Fr(2), Fr(3))
CG_G = (Fr(3), Fr(2), Fr(2), Fr(0))


def sm(Y, l, c):
    return (qY(Y), SU2[l], SU3[c])


def g(c, l, r, x):
    return (SU3[c], SU2[l], SU2[r], qBL(x))


def mv(cg, fields):
    """fields: list of (kind, reps, mult) with kind in weyl/cplx/real. Returns b (list Fr), bij (matrix Fr)."""
    n = len(cg)
    b = [Fr(-11, 3) * cg[i] for i in range(n)]
    bij = [[(Fr(-34, 3) * cg[i] ** 2 if i == j else Fr(0)) for j in range(n)] for i in range(n)]
    for kind, reps, m in fields:
        for i in range(n):
            Dm = Fr(1)
            for k in range(n):
                if k != i:
                    Dm *= reps[k][0]
            S = reps[i][1] * Dm * m          # index of the whole multiplet w.r.t. factor i
            if S == 0:
                continue
            if kind == "weyl":
                b[i] += Fr(2, 3) * S
                for j in range(n):
                    bij[i][j] += S * (2 * reps[j][2] + (Fr(10, 3) * cg[i] if i == j else 0))
            elif kind in ("cplx", "real"):
                w = Fr(1) if kind == "cplx" else Fr(1, 2)
                b[i] += Fr(1, 3) * w * S
                for j in range(n):
                    bij[i][j] += w * S * (4 * reps[j][2] + (Fr(2, 3) * cg[i] if i == j else 0))
            else:
                raise ValueError(kind)
    return b, bij


def thr_b(kind, reps, mult):
    """one-loop b of a multiplet being integrated out; 'vec' = complex massive vector + its eaten Goldstone,
    mult counts the complex vector and its conjugate as 2 (so S = 2 T D)."""
    n = len(reps)
    out = []
    for i in range(n):
        Dm = Fr(1)
        for k in range(n):
            if k != i:
                Dm *= reps[k][0]
        S = reps[i][1] * Dm * mult
        if kind == "cplx":
            out.append(Fr(1, 3) * S)
        elif kind == "real":
            out.append(Fr(1, 6) * S)
        elif kind == "vec":
            out.append((Fr(-11, 3) + Fr(1, 6)) * S)
        elif kind == "weyl":
            out.append(Fr(2, 3) * S)
    return out


def sv_const(reps, mult):
    """heavy-vector MS-bar constant per factor: index of the real vectors = T D mult."""
    n = len(reps)
    out = []
    for i in range(n):
        Dm = Fr(1)
        for k in range(n):
            if k != i:
                Dm *= reps[k][0]
        out.append(reps[i][1] * Dm * mult)
    return out


# ---------------- field content ----------------
# 16 of SO(10)
F16_SM = [sm(Fr(1, 6), "2", "3"), sm(Fr(-2, 3), "1", "3b"), sm(Fr(1, 3), "1", "3b"), sm(Fr(-1, 2), "2", "1"),
          sm(1, "1", "1")]
F10_SM = [sm(Fr(-1, 3), "1", "3"), sm(Fr(1, 3), "1", "3b"), sm(Fr(1, 2), "2", "1"), sm(Fr(-1, 2), "2", "1")]
F16_G = [g("3", "2", "1", Fr(1, 3)), g("3b", "1", "2", Fr(-1, 3)), g("1", "2", "1", -1), g("1", "1", "2", 1)]
F10_G = [g("3", "1", "1", Fr(-2, 3)), g("3b", "1", "1", Fr(2, 3)), g("1", "2", "2", 0)]

# Scalars: name -> (kind, c, 2L, 2R, B-L), Goldstones (210 (3,1,1)_{4/3} cplx, one (3,2,2)_{-2/3} cplx) removed,
# derived by hand from the PS decompositions (checked dimension-wise in check_completeness()).
SCAL = {
    "210(8,1,1)": ("real", "8", "1", "1", 0), "210(3,3,1)": ("cplx", "3", "3", "1", Fr(4, 3)),
    "210(8,3,1)": ("real", "8", "3", "1", 0), "210(1,3,1)": ("real", "1", "3", "1", 0),
    "210(3,1,3)": ("cplx", "3", "1", "3", Fr(4, 3)), "210(8,1,3)": ("real", "8", "1", "3", 0),
    "210(1,1,3)": ("real", "1", "1", "3", 0), "210(1,2,2)-2": ("cplx", "1", "2", "2", -2),
    "210(3,2,2)": ("cplx", "3", "2", "2", Fr(-2, 3)), "210(6,2,2)": ("cplx", "6", "2", "2", Fr(2, 3)),
    "126(3,1,1)": ("cplx", "3", "1", "1", Fr(-2, 3)), "126(3b,1,1)": ("cplx", "3b", "1", "1", Fr(2, 3)),
    "126(1,3,1)": ("cplx", "1", "3", "1", -2), "126(3,3,1)": ("cplx", "3", "3", "1", Fr(-2, 3)),
    "126(6,3,1)": ("cplx", "6", "3", "1", Fr(2, 3)), "126(1,1,3)DR": ("cplx", "1", "1", "3", 2),
    "126(3b,1,3)": ("cplx", "3b", "1", "3", Fr(2, 3)), "126(6b,1,3)": ("cplx", "6b", "1", "3", Fr(-2, 3)),
    "126(1,2,2)": ("cplx", "1", "2", "2", 0), "126(3,2,2)": ("cplx", "3", "2", "2", Fr(4, 3)),
    "126(3b,2,2)": ("cplx", "3b", "2", "2", Fr(-4, 3)), "126(8,2,2)": ("cplx", "8", "2", "2", 0),
    "10(3,1,1)": ("cplx", "3", "1", "1", Fr(-2, 3)), "10(3b,1,1)": ("cplx", "3b", "1", "1", Fr(2, 3)),
    "10(1,2,2)": ("cplx", "1", "2", "2", 0),
}
VEC322 = g("3", "2", "2", Fr(-2, 3))
VEC311 = g("3", "1", "1", Fr(4, 3))

CONT = {
    "C0": ("126(1,2,2)", "126(1,1,3)DR", "210(8,3,1)"),
    "C1": ("126(1,2,2)", "10(1,2,2)", "126(1,1,3)DR", "210(8,3,1)"),
    "C2": ("126(1,2,2)", "10(1,2,2)", "126(1,1,3)DR"),
    "C1p": ("126(1,2,2)", "10(1,2,2)", "126(1,1,3)DR", "210(1,3,1)"),
}


def check_completeness():
    dims = {"210": 0, "126": 0, "10": 0}
    for name, (kind, c, l, r, x) in SCAL.items():
        d = SU3[c][0] * SU2[l][0] * SU2[r][0] * (1 if kind == "real" else 2)
        dims[name.split("(")[0]] += d
    # 210: + 2 real singlets + Goldstones 6 + 24 = 32 ; 126bar: complex 126 -> 252 real ; 10 complex -> 20 real
    return {"210_real": dims["210"] + 2 + 30, "126_real": dims["126"], "10_real": dims["10"]}


def gscal(name):
    kind, c, l, r, x = SCAL[name]
    return (kind, g(c, l, r, x), 1)


def sm_pieces(name):
    kind, c, l, r, x = SCAL[name]
    nr = SU2[r][0]
    out = []
    for k in range(nr):
        t3 = Fr(nr - 1, 2) - k
        Y = t3 + Fr(x) / 2
        out.append((f"{name}|Y={Y}", kind, sm(Y, l, c)))
    return out


def light_states(content):
    """SM-language states at ~v_R: W_R (vector), all SM pieces of light multiplets minus SM Higgs and minus the
    Delta_R^+ Goldstone; the neutral singlets carry no gauge charge (harmless)."""
    out = [("W_R", "vec", sm(1, "1", "1"), 2)]
    higgs = False
    for name in content:
        for pname, kind, reps in sm_pieces(name):
            if name == "126(1,1,3)DR" and pname.endswith("|Y=1"):
                continue
            if (not higgs) and name.endswith("(1,2,2)") and pname.endswith("|Y=1/2"):
                higgs = True
                continue
            out.append((pname, kind, reps, 1))
    return out


def heavy_states(content):
    return [(n, SCAL[n][0], g(*SCAL[n][1:]), 1) for n in SCAL if n not in content]


def sm_fields(withS):
    f = [("weyl", r, 3 + (6 if withS else 0)) for r in F16_SM]
    if withS:
        f += [("weyl", r, 2) for r in F10_SM]
    f.append(("cplx", sm(Fr(1, 2), "2", "1"), 1))
    return f


def g_fields(content, withS):
    f = [("weyl", r, 3 + (6 if withS else 0)) for r in F16_G]
    if withS:
        f += [("weyl", r, 2) for r in F10_G]
    f += [gscal(n) for n in content]
    return f


# SO(10) single-group coefficients (own computation)
SO10R = {"16": (16, Fr(2), Fr(45, 8)), "10": (10, Fr(1), Fr(9, 2)), "126": (126, Fr(35), Fr(25, 2)),
         "210": (210, Fr(56), Fr(12))}


def so10_b(withPhi):
    CA = Fr(8)
    b1 = Fr(-11, 3) * CA
    b2 = Fr(-34, 3) * CA ** 2
    weyl = [("16", 3), ("16", 6), ("10", 2)] + ([("16", 2)] if withPhi else [])
    for rep, m in weyl:
        d, T, C = SO10R[rep]
        b1 += Fr(2, 3) * T * m
        b2 += m * T * (2 * C + Fr(10, 3) * CA)
    for rep, kind in [("210", "real"), ("126", "cplx"), ("10", "cplx")]:
        d, T, C = SO10R[rep]
        w = Fr(1) if kind == "cplx" else Fr(1, 2)
        b1 += Fr(1, 3) * w * T
        b2 += w * T * (4 * C + Fr(2, 3) * CA)
    return b1, b2


# ---------------- running ----------------
def make_rhs(b, bij, yuk):
    b = np.array([float(x) for x in b])
    B = np.array([[float(x) for x in row] for row in bij])
    yuk = np.zeros(len(b)) if yuk is None else np.asarray(yuk, float)

    def rhs(t, ai):
        al = 1.0 / ai
        return -b / (2 * PI) - B @ al / (8 * PI ** 2) + yuk / (32 * PI ** 3)
    return rhs


def run(rhs, a0, t0, t1):
    if abs(t1 - t0) < 1e-14:
        return np.array(a0, float)
    s = solve_ivp(rhs, (t0, t1), np.array(a0, float), method="DOP853", rtol=1e-11, atol=1e-12)
    return s.y[:, -1]


class Model:
    def __init__(self, content, loops=2, M_s=1e13, y_s=0.336, sv=1.0, r311=math.sqrt(0.8), light_r=None,
                 gut_r=None, yukawa=True, yt2=0.30):
        self.content = CONT[content] if isinstance(content, str) else content
        self.loops, self.M_s, self.y_s, self.sv, self.r311 = loops, M_s, y_s, sv, r311
        self.light_r = light_r or {}
        self.gut_r = gut_r or {}
        L2 = 1.0 if loops >= 2 else 0.0
        # crude constant Yukawa terms (percent-level irrelevant; checked by switching off)
        yt2 = yt2 if yukawa else 0.0
        ys2 = 14 * y_s ** 2 if yukawa else 0.0
        segs = {}
        for key, (cg, fl, yk) in {
            "sm0": (CG_SM, sm_fields(False), np.array([1.7, 1.5, 2.0]) * yt2),
            "sm1": (CG_SM, sm_fields(True), np.array([1.7, 1.5, 2.0]) * yt2 + ys2),
            "g0": (CG_G, g_fields(self.content, False), np.array([4, 3, 3, 1.0]) * yt2),
            "g1": (CG_G, g_fields(self.content, True), np.array([4, 3, 3, 1.0]) * yt2 + ys2),
        }.items():
            b, bij = mv(cg, fl)
            bij = [[x * Fr(int(L2)) for x in row] for row in bij]
            segs[key] = (b, bij, make_rhs(b, bij, yk * L2))
        self.segs = segs
        # thresholds
        self.Dl = np.zeros(3)
        for name, kind, reps, m in light_states(self.content):
            r = self.light_r.get(name, 1.0)
            if r != 1.0:
                self.Dl += np.array([float(x) for x in thr_b(kind, reps, m)]) * math.log(r) / (2 * PI)
        self.Dl[0] += sv * float(sv_const(sm(1, "1", "1"), 2)[0]) / (12 * PI)
        self.Dg = np.zeros(4)
        for name, kind, reps, m in heavy_states(self.content):
            r = self.gut_r.get(name, 1.0)
            if r != 1.0:
                self.Dg += np.array([float(x) for x in thr_b(kind, reps, m)]) * math.log(r) / (2 * PI)
        if r311 != 1.0:
            self.Dg += np.array([float(x) for x in thr_b("vec", VEC311, 2)]) * math.log(r311) / (2 * PI)
        SV = np.array([float(a + b) for a, b in zip(sv_const(VEC322, 2), sv_const(VEC311, 2))])
        self.SV = SV
        self.Dg += sv * SV / (12 * PI)

    def run_up(self, x):
        lvR, lMU, a2R = x
        t0, ts = math.log(MZ), math.log(self.M_s)
        a = np.array([A1I_MZ, A2I_MZ, 1 / A3_MZ])
        if ts < lvR:
            a = run(self.segs["sm0"][2], a, t0, ts)
            a = run(self.segs["sm1"][2], a, ts, lvR)
        else:
            a = run(self.segs["sm0"][2], a, t0, lvR)
        a = a + self.Dl
        aBL = 2.5 * (a[0] - 0.6 * a2R)
        gg = np.array([a[2], a[1], a2R, aBL])
        if ts < lvR:
            gg = run(self.segs["g1"][2], gg, lvR, lMU)
        elif ts < lMU:
            gg = run(self.segs["g0"][2], gg, lvR, ts)
            gg = run(self.segs["g1"][2], gg, ts, lMU)
        else:
            gg = run(self.segs["g0"][2], gg, lvR, lMU)
        return gg + self.Dg

    def solve(self, guess):
        def f(x):
            E = self.run_up(x)
            return [E[0] - E[1], E[2] - E[1], E[3] - E[1]]
        x, info, ier, msg = fsolve(f, np.array(guess, float), full_output=True, xtol=1e-12)
        E = self.run_up(x)
        res = max(abs(E[0] - E[1]), abs(E[2] - E[1]), abs(E[3] - E[1]))
        return {"v_R": math.exp(x[0]), "M_U": math.exp(x[1]), "a2R": x[2], "aU": float(E[1]), "res": res,
                "ok": bool(res < 1e-8 and x[0] < x[1] and E[1] > 1)}


def landau_2l(M_U, aU, M_phi=1e17, yuk=True, y_s=0.336, yt2=0.30, loops=2):
    b1l, b2l = so10_b(False)
    b1h, b2h = so10_b(True)
    Ylo = (14 * y_s ** 2 + 10 * yt2 + 2 * (126 / 16) * 0.5) if yuk else 0.0
    Yhi = Ylo + (4.0 if yuk else 0.0)
    L2 = 1.0 if loops >= 2 else 0.0

    def mk(b1, b2, Y):
        return lambda t, a: [-float(b1) / (2 * PI) - L2 * float(b2) / (8 * PI ** 2 * a[0]) + L2 * Y / (32 * PI ** 3)]

    def ev(t, a):
        return a[0] - 1.0
    ev.terminal = True
    tU, tP = math.log(M_U), math.log(max(M_phi, M_U))
    s = solve_ivp(mk(b1l, b2l, Ylo), (tU, tP), [aU], method="DOP853", rtol=1e-11, atol=1e-12, events=ev)
    if s.t_events[0].size:
        return math.exp(s.t_events[0][0]) / MPL
    s2 = solve_ivp(mk(b1h, b2h, Yhi), (tP, math.log(1e30)), [s.y[0, -1]], method="DOP853", rtol=1e-11,
                   atol=1e-12, events=ev)
    return math.exp(s2.t_events[0][0]) / MPL if s2.t_events[0].size else float("inf")


HBAR, YEAR = 6.582119569e-25, 365.25 * 24 * 3600


def tau_repo(MX, aUinv):
    # repository gauge_lifetime_years (proton_decay_falsification_gate_v20), re-typed
    f_pi, m_p, a_h, A_R, F_q = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    t = (4 / PI) * (f_pi ** 2 / m_p) * MX ** 4 * aUinv ** 2 / (a_h ** 2 * A_R ** 2 * F_q)
    return t * HBAR / YEAR


def tau_bchpt(MX, aUinv, alpha=0.0144, DF=1.267, f=0.1307, A_R=2.726, Vud=0.9737):
    """BChPT form with the chiral factor kept explicitly: Gamma = (pi m_p / 4 f^2) alpha_U^2 A_R^2 alpha^2 (1+D+F)^2
    * 2 (1+|Vud|^2)^2 / M^4 (same structure as 1312.3185 with alpha_H = alpha_bar (1+D+F)); alpha = |<0|(ud)u|p>|."""
    m_p = 0.9382720813
    gam = (PI * m_p / (4 * f ** 2)) * (1 / aUinv) ** 2 * A_R ** 2 * alpha ** 2 * (1 + DF) ** 2 * \
        2 * (1 + Vud ** 2) ** 2 / MX ** 4
    return HBAR / gam / YEAR


def tau_lattice(MX, aUinv, W0=0.131, A_R=2.726, Vud=0.9737):
    """Aoki-type formula Gamma = (m_p/32 pi)(1 - m_pi^2/m_p^2)^2 A^2 W0^2 sum|C|^2 with
    sum|C|^2 = 4 k^4 * 2 (1+|Vud|^2)^2 (Fierz-2, X and X' degenerate), k^2 = g^2/(2 M^2)  (own derivation)."""
    m_p, m_pi = 0.9382720813, 0.1349768
    k2 = 4 * PI / aUinv / (2 * MX ** 2)
    sumC2 = 4 * k2 ** 2 * 2 * (1 + Vud ** 2) ** 2
    gam = (m_p / (32 * PI)) * (1 - (m_pi / m_p) ** 2) ** 2 * A_R ** 2 * W0 ** 2 * sumC2
    return HBAR / gam / YEAR
