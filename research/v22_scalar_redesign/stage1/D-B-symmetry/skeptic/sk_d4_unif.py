"""SKEPTIC (D-B-symmetry, D4): independent two-loop gauge unification for V1-C2 and V1-C1622 (own code).

Own implementation of the Machacek-Vaughn one- and two-loop gauge coefficients from a multiplet list (Weyl fermions,
complex / real scalars), checked against the textbook SM values.  Chain: SM (M_Z -> v_R; 2-loop gauge + 1-loop top
Yukawa feedback) -> G3221 (v_R -> M_U; B63 exotic fermions 3x(16+16bar) + 2x10 from M_s = 1e13; approximate
bidoublet-top Yukawa feedback c = (4,3,3,1) y^2, EST) -> SO(10) (2-loop Landau scan, Phi17 pair from 1e17).
All heavy states at M_U (nominal), MS-bar, no threshold conversion terms.  Bottom-up solve for (v_R, alpha_R(v_R), M_U).
Proton: Gamma = m_p/(32 pi) (1 - m_pi^2/m_p^2)^2 A_R^2 (4 pi alpha_U / M_U^2)^2 * 2 (1+|V_ud|^2)^2 W0^2,
W0 = 0.131 GeV^2 (lattice, LIT-unverified per FINAL), A_R = 3.28 (chain value adopted in round 2) -- EST.
Writes sk_d4_unif.json.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

HERE = Path(__file__).resolve().parent
SU3 = {1: (Fr(0), Fr(0)), 3: (Fr(1, 2), Fr(4, 3)), 6: (Fr(5, 2), Fr(10, 3)), 8: (Fr(3), Fr(3))}
SU2 = {1: (Fr(0), Fr(0)), 2: (Fr(1, 2), Fr(3, 4)), 3: (Fr(2), Fr(2))}


def coeffs(groups, mults):
    """groups: list of ('SU3'|'SU2'|'U1'); mults: list of (dims tuple / charge, kind, n) where for U1 the entry is the
    GUT-normalised charge.  kind: 'W' Weyl fermion, 'C' complex scalar, 'R' real scalar.  Returns b (list), bij."""
    ng = len(groups)
    CG = [Fr(3) if g == "SU3" else Fr(2) if g == "SU2" else Fr(0) for g in groups]
    b = [Fr(-11, 3) * c for c in CG]
    bij = [[Fr(-34, 3) * CG[i] ** 2 if i == j else Fr(0) for j in range(ng)] for i in range(ng)]
    for reps, kind, n in mults:
        T, C, D = [], [], []
        for g, r in zip(groups, reps):
            if g == "SU3":
                t, c = SU3[r]; d = r
            elif g == "SU2":
                t, c = SU2[r]; d = r
            else:
                q = Fr(r); t, c, d = q * q, q * q, 1
            T.append(t); C.append(c); D.append(d)
        dim = 1
        for d in D:
            dim *= d
        for i in range(ng):
            S = T[i] * Fr(dim, D[i])
            if kind == "W":
                b[i] += Fr(2, 3) * S * n
                for j in range(ng):
                    bij[i][j] += n * S * (2 * C[j] + (Fr(10, 3) * CG[i] if i == j else 0))
            else:
                eta = Fr(1) if kind == "C" else Fr(1, 2)
                b[i] += Fr(1, 3) * S * n * eta
                for j in range(ng):
                    bij[i][j] += n * eta * S * (4 * C[j] + (Fr(2, 3) * CG[i] if i == j else 0))
    return b, bij


SMG = ["U1", "SU2", "SU3"]


class Q:
    """charge with exact square (3/5 Y^2)."""
    def __init__(self, sq):
        self.sq = Fr(sq)

    def __mul__(self, other):
        return self.sq


def coeffs_q(groups, mults):
    # same as coeffs but U1 charges given as Q objects (exact squares)
    fixed = []
    for reps, kind, n in mults:
        fixed.append((reps, kind, n))
    ng = len(groups)
    CG = [Fr(3) if g == "SU3" else Fr(2) if g == "SU2" else Fr(0) for g in groups]
    b = [Fr(-11, 3) * c for c in CG]
    bij = [[Fr(-34, 3) * CG[i] ** 2 if i == j else Fr(0) for j in range(ng)] for i in range(ng)]
    for reps, kind, n in fixed:
        T, C, D = [], [], []
        for g, r in zip(groups, reps):
            if g == "SU3":
                t, c = SU3[r]; d = r
            elif g == "SU2":
                t, c = SU2[r]; d = r
            else:
                t = c = r.sq; d = 1
            T.append(t); C.append(c); D.append(d)
        dim = 1
        for d in D:
            dim *= d
        for i in range(ng):
            S = T[i] * Fr(dim, D[i])
            if kind == "W":
                b[i] += Fr(2, 3) * S * n
                for j in range(ng):
                    bij[i][j] += n * S * (2 * C[j] + (Fr(10, 3) * CG[i] if i == j else 0))
            else:
                eta = Fr(1) if kind == "C" else Fr(1, 2)
                b[i] += Fr(1, 3) * S * n * eta
                for j in range(ng):
                    bij[i][j] += n * eta * S * (4 * C[j] + (Fr(2, 3) * CG[i] if i == j else 0))
    return b, bij


Y = lambda y: Q(Fr(3, 5) * Fr(y) ** 2)
SM = [((Y(Fr(1, 6)), 2, 3), "W", 3), ((Y(Fr(-2, 3)), 1, 3), "W", 3), ((Y(Fr(1, 3)), 1, 3), "W", 3),
      ((Y(Fr(-1, 2)), 2, 1), "W", 3), ((Y(Fr(1)), 1, 1), "W", 3), ((Y(Fr(1, 2)), 2, 1), "C", 1)]
bSM, bijSM = coeffs_q(SMG, SM)
assert bSM == [Fr(41, 10), Fr(-19, 6), Fr(-7)], bSM
assert bijSM == [[Fr(199, 50), Fr(27, 10), Fr(44, 5)], [Fr(9, 10), Fr(35, 6), Fr(12)], [Fr(11, 10), Fr(9, 2), Fr(-26)]], bijSM

# G3221: groups (SU3, SU2L, SU2R, U1_BL) with T_BL = sqrt(3/8)(B-L)
G = ["SU3", "SU2", "SU2", "U1"]
BL = lambda x: Q(Fr(3, 8) * Fr(x) ** 2)
GEN = [((3, 2, 1, BL(Fr(1, 3))), "W", 3), ((3, 1, 2, BL(Fr(-1, 3))), "W", 3), ((1, 2, 1, BL(-1)), "W", 3),
       ((1, 1, 2, BL(1)), "W", 3)]
BID = ((1, 2, 2, BL(0)), "C", 1)
DR = ((1, 1, 3, BL(2)), "C", 1)
O831 = ((8, 3, 1, BL(0)), "R", 1)
S622 = ((6, 2, 2, BL(Fr(2, 3))), "C", 1)
# B63 exotics at M_s: 3 x (16 + 16bar) = 6 Weyl 16s (16bar has same indices), 2 Weyl 10s
def w16(n):
    return [((3, 2, 1, BL(Fr(1, 3))), "W", n), ((3, 1, 2, BL(Fr(-1, 3))), "W", n), ((1, 2, 1, BL(-1)), "W", n),
            ((1, 1, 2, BL(1)), "W", n)]
def w10(n):
    return [((1, 2, 2, BL(0)), "W", n), ((3, 1, 1, BL(Fr(-2, 3))), "W", n), ((3, 1, 1, BL(Fr(2, 3))), "W", n)]
EXO = w16(6) + w10(2)

CONTENTS = {"V1-C2": [BID, BID, DR], "V1-C1622": [BID, BID, DR, O831, S622]}

# SO(10): T(10)=1, C2 = T*45/dim
SO10 = {10: (Fr(1), Fr(9, 2)), 16: (Fr(2), Fr(45, 8)), 126: (Fr(35), Fr(25, 2)), 210: (Fr(56), Fr(12))}


def so10_coeffs(fermions, scalars):
    CGv = Fr(8)
    b = Fr(-11, 3) * CGv; b2 = Fr(-34, 3) * CGv ** 2
    for r, n in fermions:
        T, C = SO10[r]; b += Fr(2, 3) * T * n; b2 += n * T * (2 * C + Fr(10, 3) * CGv)
    for r, kind, n in scalars:
        T, C = SO10[r]; eta = Fr(1) if kind == "C" else Fr(1, 2)
        b += Fr(1, 3) * eta * T * n; b2 += n * eta * T * (4 * C + Fr(2, 3) * CGv)
    return b, b2


SO10_F = [(16, 3), (16, 6), (10, 2)]
SO10_S_V1 = [(210, "R", 1), (126, "C", 1), (10, "C", 2)]
SO10_S_R2B = [(210, "R", 1), (126, "C", 1), (10, "C", 1)]


def rge(t, y, b, bij, c_y, ny):
    """y = [alpha_i^-1 ..., y_top]; d alpha_i^-1 / dt = -(1/2pi)[b_i + sum_j bij alpha_j/(4pi) - c_i y^2/(16 pi^2)]."""
    n = len(b)
    ainv = y[:n]; yt = y[n]
    al = 1.0 / ainv
    d = np.zeros(n + 1)
    for i in range(n):
        d[i] = -(b[i] + sum(bij[i][j] * al[j] for j in range(n)) / (4 * math.pi) - c_y[i] * yt**2 / (16 * math.pi**2)) / (2 * math.pi)
    g2 = 4 * math.pi * al
    d[n] = yt / (16 * math.pi**2) * (ny[0] * yt**2 - sum(ny[1 + i] * g2[i] for i in range(n)))
    return d


def run(y0, t0, t1, b, bij, c_y, ny):
    s = solve_ivp(rge, (t0, t1), y0, args=([float(x) for x in b], [[float(x) for x in r] for r in bij], c_y, ny),
                  rtol=1e-10, atol=1e-12, method="DOP853")
    return s.y[:, -1]


MZ = 91.1876
AEM_INV, S2W, AS = 127.951, 0.23122, 0.1180
A1 = (3 / 5) * AEM_INV * (1 - S2W)
A2 = AEM_INV * S2W
A3 = 1 / AS
YT_MZ = 0.97   # MS-bar y_t(M_Z) ~ 0.97 (from m_t(m_t) ~ 162.5 GeV), EST


def solve_content(name, Ms=1e13):
    light = CONTENTS[name]
    bA, bijA = coeffs_q(G, GEN + light)
    bB, bijB = coeffs_q(G, GEN + light + EXO)
    cG = [4.0, 3.0, 3.0, 1.0]; nyG = [5.0, 8.0, 9 / 4, 9 / 4, 1 / 4]   # EST bidoublet-top feedback
    cS = [17 / 10, 3 / 2, 2.0]; nyS = [4.5, 17 / 20, 9 / 4, 8.0]

    def sm_to(vR):
        y0 = np.array([A1, A2, A3, YT_MZ])
        return run(y0, math.log(MZ), math.log(vR), bSM, bijSM, cS, nyS)

    def g_up(x):
        lvR, aRinv, lMU = x
        vR = math.exp(lvR)
        s = sm_to(vR)
        a1, a2, a3, yt = s
        aBLinv = (a1 - 0.6 * aRinv) / 0.4
        y = np.array([a3, a2, aRinv, aBLinv, yt])
        if math.log(Ms) > lvR:
            y = run(y, lvR, math.log(Ms), bA, bijA, cG, nyG)
            y = run(y, math.log(Ms), lMU, bB, bijB, cG, nyG)
        else:
            y = run(y, lvR, lMU, bB, bijB, cG, nyG)
        return y

    def eqs(x):
        y = g_up(x)
        return [y[0] - y[1], y[1] - y[2], y[2] - y[3]]

    best = None
    for guess in ([math.log(2e10), 50.0, math.log(6e15)], [math.log(1e13), 40.0, math.log(2e16)], [math.log(1e11), 45.0, math.log(1e16)]):
        sol, info, ier, msg = fsolve(eqs, guess, full_output=True, xtol=1e-12)
        r = max(abs(v) for v in eqs(sol))
        if best is None or r < best[1]:
            best = (sol, r)
    sol, r = best
    y = g_up(sol)
    return {"content": name, "v_R": math.exp(sol[0]), "alphaR_inv_vR": sol[1], "M_U": math.exp(sol[2]),
            "alpha_U_inv": float(np.mean(y[:4])), "resid": r, "b_G3221_below_Ms": [str(v) for v in bA],
            "b_G3221_above_Ms": [str(v) for v in bB], "yt_MU": float(y[4])}


def landau(aUinv, MU, scal, Mphi=1e17, MPl=2.435e18):
    """two-loop SO(10) running (no Yukawas) until alpha^-1 -> 0; returns Lambda/M_Pl,red."""
    bA, b2A = so10_coeffs(SO10_F, scal)
    bB, b2B = so10_coeffs(SO10_F + [(16, 2)], scal)

    def f(t, y, b, b2):
        a = 1.0 / y[0]
        return [-(float(b) + float(b2) * a / (4 * math.pi)) / (2 * math.pi)]

    def hit(t, y, b, b2):
        return y[0] - 1e-3
    hit.terminal = True
    t0 = math.log(MU)
    y = [aUinv]
    if Mphi > MU:
        s = solve_ivp(f, (t0, math.log(Mphi)), y, args=(bA, b2A), events=hit, rtol=1e-10, atol=1e-12)
        if s.t_events[0].size:
            return math.exp(s.t_events[0][0]) / MPl, (str(bA), str(b2A))
        y = [s.y[0, -1]]; t0 = math.log(Mphi)
    s = solve_ivp(f, (t0, t0 + 200), y, args=(bB, b2B), events=hit, rtol=1e-10, atol=1e-12)
    return math.exp(s.t_events[0][0]) / MPl, (str(bA), str(b2A))


def tau_years(MU, aUinv, AR=3.28, W0=0.131, Vud=0.9737):
    mp, mpi = 0.93827, 0.13498
    G_ = mp / (32 * math.pi) * (1 - mpi**2 / mp**2) ** 2 * AR**2 * (4 * math.pi / aUinv) ** 2 / MU**4 * 2 * (1 + Vud**2) ** 2 * W0**2
    return 6.582119569e-25 / G_ / 3.15576e7


def main():
    out = {"inputs": {"alpha_em^-1(MZ)": AEM_INV, "s2w": S2W, "alpha_s": AS, "yt(MZ)": YT_MZ, "M_s": 1e13, "M_Phi17": 1e17},
           "SM_check": "b and bij reproduce 41/10,-19/6,-7 and the textbook 2-loop matrix (asserted)"}
    for name in ("V1-C2", "V1-C1622"):
        r = solve_content(name)
        r["tau_LA_yr(A_R=3.28,W0=0.131)"] = tau_years(r["M_U"], r["alpha_U_inv"])
        r["tau_LA/SuperK(2.4e34)"] = r["tau_LA_yr(A_R=3.28,W0=0.131)"] / 2.4e34
        r["Lambda2L/MPl_red(V1, +H2)"], r["so10_b_V1"] = landau(r["alpha_U_inv"], r["M_U"], SO10_S_V1)
        r["Lambda2L/MPl_red(R2B, no H2)"], r["so10_b_R2B"] = landau(r["alpha_U_inv"], r["M_U"], SO10_S_R2B)
        out[name] = r
        print(json.dumps(r), flush=True)
    # calibration of the proton formula against round 2: R2-B C2 nominal (M_U 6.05e15, aU^-1 34.64) -> 1.67e34 yr
    out["calibration_R2B_C2"] = tau_years(6.05e15, 34.64)
    print("calibration (6.05e15, 34.64):", out["calibration_R2B_C2"])
    (HERE / "sk_d4_unif.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
