#!/usr/bin/env python3
"""Skeptic re-implementation for gate R2-B (written independently; does NOT import r2b_* or k1_*).

Approach differences w.r.t. the researcher:
  * the G3221 scalar content is generated automatically from the Pati-Salam content of 210 (real), 126bar, 10 via
    SU(4) -> SU(3) x U(1)_{B-L} branching, Goldstones removed by name ((3,1,1)_{4/3} and one (3,2,2)_{-2/3} of 210);
  * the unification condition is solved by TOP-DOWN/BOTTOM-UP shooting with unknowns (ln v_R, ln M_U, alpha_U^-1)
    (researcher: bottom-up with alpha_2R^-1(v_R));
  * integrator: scipy LSODA / RK45 (researcher DOP853);  top Yukawa run jointly with the gauge couplings at one loop.
Conventions: t = ln(mu/GeV); d a_i/dt = -b_i/2pi - sum_j b_ij /(8 pi^2 a_j) + Y_i/(32 pi^3), a = alpha^-1.
Matching at a heavy threshold M_k (mu = matching scale): a_low = a_high - sum_k b^k ln(M_k/mu)/(2 pi) [- S_V/(12 pi) for
heavy vectors in MS-bar, sign selectable].
"""
from __future__ import annotations
import math
from fractions import Fraction as Fr
import numpy as np
from scipy.integrate import solve_ivp

PI = math.pi
MZ = 91.1876
MPL = 2.435e18
AINV_MZ = np.array([59.02, 29.57, 1.0 / 0.1179])   # (U1_Y GUT, SU2_L, SU3_C), same inputs as the repository

# ---------------- representation data (dim, Dynkin index T, Casimir C2) ----------------
def su2(n):
    j = Fr(n - 1, 2)
    return (n, Fr(n * (n * n - 1), 12), j * (j + 1))

SU3R = {"1": (1, Fr(0), Fr(0)), "3": (3, Fr(1, 2), Fr(4, 3)), "3b": (3, Fr(1, 2), Fr(4, 3)),
        "6": (6, Fr(5, 2), Fr(10, 3)), "6b": (6, Fr(5, 2), Fr(10, 3)), "8": (8, Fr(3), Fr(3))}

def u1(q2):
    q2 = Fr(q2)
    return (1, q2, q2)

def BL(q):            # GUT-normalised B-L: q_norm^2 = 3/8 (B-L)^2
    return u1(Fr(3, 8) * Fr(q) ** 2)

def YY(y):            # GUT-normalised hypercharge: 3/5 Y^2
    return u1(Fr(3, 5) * Fr(y) ** 2)

# ---------------- Pati-Salam -> G3221 branching ----------------
SU4_BRANCH = {   # SU(4) irrep -> list of (SU3 irrep, B-L)
    "1": [("1", Fr(0))],
    "4": [("3", Fr(1, 3)), ("1", Fr(-1))],
    "4b": [("3b", Fr(-1, 3)), ("1", Fr(1))],
    "6": [("3", Fr(-2, 3)), ("3b", Fr(2, 3))],
    "10": [("6", Fr(2, 3)), ("3", Fr(-2, 3)), ("1", Fr(-2))],
    "10b": [("6b", Fr(-2, 3)), ("3b", Fr(2, 3)), ("1", Fr(2))],
    "15": [("8", Fr(0)), ("3", Fr(4, 3)), ("3b", Fr(-4, 3)), ("1", Fr(0))],
}
CONJ3 = {"1": "1", "3": "3b", "3b": "3", "6": "6b", "6b": "6", "8": "8"}

def ps_to_g3221_complex(su4, l, r):
    return [(c3, l, r, q) for c3, q in SU4_BRANCH[su4]]

def ps_to_g3221_real(su4, l, r):
    """Real PS irrep (self-conjugate): pair conjugate G3221 pieces into one complex field; self-conjugate pieces real."""
    pieces = ps_to_g3221_complex(su4, l, r)
    out, used = [], set()
    for i, (c3, l_, r_, q) in enumerate(pieces):
        if i in used:
            continue
        if c3 == CONJ3[c3] and q == 0:
            out.append(("real", c3, l_, r_, q))
            used.add(i)
            continue
        # find conjugate partner
        for j in range(i + 1, len(pieces)):
            if j not in used and pieces[j][0] == CONJ3[c3] and pieces[j][3] == -q:
                used.update({i, j})
                out.append(("cplx", c3, l_, r_, q))
                break
        else:
            raise RuntimeError("no partner")
    return out

def g3221_scalar_table():
    """All G3221 scalar multiplets of 210 (real) + 126bar (cplx) + 10 (cplx), as dict name -> (kind,c3,l,r,q)."""
    tab = {}
    # 210 = (1,1,1)+(15,1,1)+(6,2,2)+(15,3,1)+(15,1,3) [real] + (10,2,2) [complex, with its conjugate (10b,2,2)]
    for su4, l, r in (("1", 1, 1), ("15", 1, 1), ("6", 2, 2), ("15", 3, 1), ("15", 1, 3)):
        for kind, c3, l_, r_, q in ps_to_g3221_real(su4, l, r):
            name = f"210:({c3},{l_},{r_})_{q}@({su4},{l},{r})"
            tab[name] = (kind, c3, l_, r_, q)
    for c3, l_, r_, q in ps_to_g3221_complex("10", 2, 2):
        tab[f"210:({c3},{l_},{r_})_{q}@(10,2,2)"] = ("cplx", c3, l_, r_, q)
    # 126bar = (6,1,1)+(10b,3,1)+(10,1,3)+(15,2,2)  (complex)
    for su4, l, r in (("6", 1, 1), ("10b", 3, 1), ("10", 1, 3), ("15", 2, 2)):
        for c3, l_, r_, q in ps_to_g3221_complex(su4, l, r):
            tab[f"126b:({c3},{l_},{r_})_{q}@({su4},{l},{r})"] = ("cplx", c3, l_, r_, q)
    # 10 = (6,1,1)+(1,2,2) complex (H10 complex)
    for su4, l, r in (("6", 1, 1), ("1", 2, 2)):
        for c3, l_, r_, q in ps_to_g3221_complex(su4, l, r):
            tab[f"10:({c3},{l_},{r_})_{q}@({su4},{l},{r})"] = ("cplx", c3, l_, r_, q)
    # Goldstones of SO(10)->G3221 (only the 210 gets an M_U vev): (3,1,1)_{4/3} of (15,1,1) and the
    # (3,2,2)_{-2/3} combination; we remove the one in (6,2,2) (beta functions do not care which combination).
    gold = [k for k in tab if k.startswith("210:(3,1,1)_4/3@(15,1,1)")] + \
           [k for k in tab if k.startswith("210:(3,2,2)_-2/3@(6,2,2)")]
    assert len(gold) == 2, gold
    for k in gold:
        del tab[k]
    # count real d.o.f.
    def ndof(v):
        kind, c3, l, r, q = v
        d = SU3R[c3][0] * l * r
        return d * (2 if kind == "cplx" else 1)
    n210 = sum(ndof(v) for k, v in tab.items() if k.startswith("210:"))
    n126 = sum(ndof(v) for k, v in tab.items() if k.startswith("126b:"))
    n10 = sum(ndof(v) for k, v in tab.items() if k.startswith("10:"))
    assert (n210, n126, n10) == (210 - 30, 252, 20), (n210, n126, n10)
    return tab

TAB = g3221_scalar_table()

def find(prefix):
    ks = [k for k in TAB if k.startswith(prefix)]
    assert len(ks) == 1, (prefix, ks)
    return ks[0]

BID126 = find("126b:(1,2,2)_0")
BID10 = find("10:(1,2,2)_0")
DELTA_R = find("126b:(1,1,3)_-2")
O831 = find("210:(8,3,1)_0")
O131 = find("210:(1,3,1)_0")
O813 = find("210:(8,1,3)_0")
O622 = find("210:(6,2,2)_2/3")
O822 = find("126b:(8,2,2)_0")
O811 = find("210:(8,1,1)_0")

CONTENTS = {
    "C0": [BID126, DELTA_R, O831],
    "C1": [BID126, BID10, DELTA_R, O831],
    "C2": [BID126, BID10, DELTA_R],
    "C1p": [BID126, BID10, DELTA_R, O131],
    "T2": [BID126, DELTA_R, O822, O831, O131],
    "bidDR": [BID126, DELTA_R],
    "C1+813": [BID126, BID10, DELTA_R, O831, O813],
    "C1+622": [BID126, BID10, DELTA_R, O831, O622],
}

# ---------------- fields -> (group-factor reps) ----------------
def g_reps(c3, l, r, q):
    return (SU3R[c3], su2(l), su2(r), BL(q))

G3221_CG = (Fr(3), Fr(2), Fr(2), Fr(0))
SM_CG = (Fr(0), Fr(2), Fr(3))   # (U1_Y, SU2L, SU3C)

def sm_reps(y, l, c3):
    return (YY(y), su2(l), SU3R[c3])

def S_index(reps, i):
    s = reps[i][1]
    for k, rr in enumerate(reps):
        if k != i:
            s = s * rr[0]
    return s

def mv(cg, fields):
    """fields: list of (kind, reps, mult); kind in weyl/cplx/real.  Exact MV one/two-loop coefficients."""
    n = len(cg)
    b = [Fr(-11, 3) * c for c in cg]
    B = [[Fr(-34, 3) * cg[i] ** 2 if i == j else Fr(0) for j in range(n)] for i in range(n)]
    coef = {"weyl": (Fr(2, 3), 2, Fr(10, 3)), "cplx": (Fr(1, 3), 4, Fr(2, 3)), "real": (Fr(1, 6), 2, Fr(1, 3))}
    for kind, reps, mult in fields:
        c1, c2, c3 = coef[kind]
        for i in range(n):
            s = S_index(reps, i) * mult
            if s == 0:
                continue
            b[i] += c1 * s
            for j in range(n):
                B[i][j] += c2 * s * reps[j][2]
            B[i][i] += c3 * cg[i] * s
    return b, B

def thr_b(kind, reps, i, mult=1):
    return {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6), "vector": Fr(-7, 2)}[kind] * S_index(reps, i) * mult

# fermions
F16_G = [g_reps("3", 2, 1, Fr(1, 3)), g_reps("3b", 1, 2, Fr(-1, 3)), g_reps("1", 2, 1, Fr(-1)), g_reps("1", 1, 2, Fr(1))]
F10_G = [g_reps("3", 1, 1, Fr(-2, 3)), g_reps("3b", 1, 1, Fr(2, 3)), g_reps("1", 2, 2, Fr(0))]
F16_SM = [sm_reps(Fr(1, 6), 2, "3"), sm_reps(Fr(-2, 3), 1, "3b"), sm_reps(Fr(1, 3), 1, "3b"), sm_reps(Fr(-1, 2), 2, "1"),
          sm_reps(Fr(1), 1, "1"), sm_reps(Fr(0), 1, "1")]
F10_SM = [sm_reps(Fr(-1, 3), 1, "3"), sm_reps(Fr(1, 3), 1, "3b"), sm_reps(Fr(1, 2), 2, "1"), sm_reps(Fr(-1, 2), 2, "1")]
N16S, N10S = 6, 2     # B63 S-sector: 3x(16+16bar) + 2x10 Weyl  (T_S = 6*2 + 2 = 14)

def fields_sm(withS):
    f = [("weyl", r, 3 + (N16S if withS else 0)) for r in F16_SM]
    if withS:
        f += [("weyl", r, N10S) for r in F10_SM]
    f.append(("cplx", sm_reps(Fr(1, 2), 2, "1"), 1))
    return f

def fields_g(light, withS):
    f = [("weyl", r, 3 + (N16S if withS else 0)) for r in F16_G]
    if withS:
        f += [("weyl", r, N10S) for r in F10_G]
    for name in light:
        kind, c3, l, r, q = TAB[name]
        f.append((kind, g_reps(c3, l, r, q), 1))
    return f

def sm_split(name):
    """SM pieces of a G3221 scalar: Y = T3R + (B-L)/2."""
    kind, c3, l, r, q = TAB[name]
    out = []
    for k in range(r):
        t3r = Fr(r - 1, 2) - k
        out.append((kind, sm_reps(t3r + q / 2, l, c3), Fr(t3r)))
    return out

def light_thr_states(light):
    """SM-language states integrated out at v_R."""
    st = [("vector", sm_reps(Fr(1), 1, "1"), 2, "W_R")]
    higgs_done = False
    for name in light:
        for kind, reps, t3r in sm_split(name):
            if name == DELTA_R and reps[0][1] == Fr(3, 5):     # |Y| = 1 component eaten by W_R
                continue
            if name == DELTA_R and reps[0][1] == 0:            # neutral: no SM charge (Goldstone of Z' / physical)
                continue
            if (not higgs_done) and name in (BID126, BID10) and reps[1][0] == 2 and reps[0][1] == Fr(3, 20):
                higgs_done = True
                continue
            st.append((kind, reps, 1, name))
    assert higgs_done or not any(n in (BID126, BID10) for n in light)
    return st

HEAVY_VEC = [("vector", g_reps("3", 2, 2, Fr(-2, 3)), 2, "V322"), ("vector", g_reps("3", 1, 1, Fr(4, 3)), 2, "V311")]

def heavy_states(light):
    return [(TAB[n][0], g_reps(*TAB[n][1:]), 1, n) for n in TAB if n not in light]

def SV():
    sv = [sum(S_index(reps, i) * m for _k, reps, m, _n in HEAVY_VEC) for i in range(4)]
    svY = S_index(sm_reps(Fr(1), 1, "1"), 0) * 2
    return sv, svY

# ---------------- SO(10) phase ----------------
SO10R = {"10": (10, Fr(1), Fr(9, 2)), "16": (16, Fr(2), Fr(45, 8)), "126": (126, Fr(35), Fr(25, 2)),
         "210": (210, Fr(56), Fr(12))}

def mv_so10(content):
    cg = Fr(8)
    b = Fr(-11, 3) * cg
    B = Fr(-34, 3) * cg * cg
    coef = {"weyl": (Fr(2, 3), 2, Fr(10, 3)), "cplx": (Fr(1, 3), 4, Fr(2, 3)), "real": (Fr(1, 6), 2, Fr(1, 3))}
    for rep, kind, m in content:
        d, t, c = SO10R[rep]
        c1, c2, c3 = coef[kind]
        b += c1 * t * m
        B += t * m * (c2 * c + c3 * cg)
    return b, B

SO10_LO = [("16", "weyl", 9), ("10", "weyl", 2), ("210", "real", 1), ("126", "cplx", 1), ("10", "cplx", 1)]
SO10_HI = SO10_LO + [("16", "weyl", 2)]
