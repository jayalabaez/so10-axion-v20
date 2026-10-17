#!/usr/bin/env python3
"""Verifier (physics lens) for gate K1: independent exact gauge-coupling beta coefficients.

Written from scratch (no import of the researcher's k1_lib).  Conventions identical to the researcher's so that the
numbers can be compared:  dg_i/dt = g_i^3/(16 pi^2) [ b_i + sum_j b_ij g_j^2/(16 pi^2) + b3_i g_i^4/(16 pi^2)^2 ].

Group-theory data are entered by hand (not copied): T(fund SU(N)) = 1/2, C2(fund) = (N^2-1)/(2N), C2(adj) = N,
SU(3) 6: T = 5/2, C2 = 10/3; SU(2) 3: T = 2, C2 = 2.  SO(10) with T(10) = 1: T(16) = 2, T(45) = 8, T(126) = 35,
T(210) = 56 and C2 = 45 T / dim.
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------------------------------------------
# One field: a list of (dim_i, T_i, C2_i) per gauge factor.  kind: W (Weyl), C (complex scalar), R (real scalar).
# ---------------------------------------------------------------------------------------------------------------
def su_n_fund(n):
    return (n, Fr(1, 2), Fr(n * n - 1, 2 * n))


def su2(rep):
    return {1: (1, Fr(0), Fr(0)), 2: (2, Fr(1, 2), Fr(3, 4)), 3: (3, Fr(2), Fr(2))}[rep]


def su3(rep):
    return {1: (1, Fr(0), Fr(0)), 3: (3, Fr(1, 2), Fr(4, 3)), 6: (6, Fr(5, 2), Fr(10, 3)), 8: (8, Fr(3), Fr(3))}[rep]


def u1(qsq):
    qsq = Fr(qsq)
    return (1, qsq, qsq)


def so10(rep):
    T = {1: Fr(0), 10: Fr(1), 16: Fr(2), 45: Fr(8), 54: Fr(12), 120: Fr(28), 126: Fr(35), 210: Fr(56)}[rep]
    return (rep, T, Fr(45) * T / rep if rep else Fr(0))


def mv(group_cg, fields):
    """fields: list of (kind, reps, mult).  Returns exact (b, bij)."""
    n = len(group_cg)
    b = [Fr(-11, 3) * Fr(c) for c in group_cg]
    bij = [[Fr(0)] * n for _ in range(n)]
    for i in range(n):
        bij[i][i] += Fr(-34, 3) * Fr(group_cg[i]) ** 2
    for kind, reps, mult in fields:
        for i in range(n):
            S = Fr(reps[i][1]) * Fr(mult)
            for k in range(n):
                if k != i:
                    S *= reps[k][0]
            if S == 0:
                continue
            if kind == "W":
                b[i] += Fr(2, 3) * S
                bij[i][i] += Fr(10, 3) * Fr(group_cg[i]) * S
                for j in range(n):
                    bij[i][j] += 2 * S * Fr(reps[j][2])
            elif kind == "C":
                b[i] += Fr(1, 3) * S
                bij[i][i] += Fr(2, 3) * Fr(group_cg[i]) * S
                for j in range(n):
                    bij[i][j] += 4 * S * Fr(reps[j][2])
            elif kind == "R":
                b[i] += Fr(1, 6) * S
                bij[i][i] += Fr(1, 3) * Fr(group_cg[i]) * S
                for j in range(n):
                    bij[i][j] += 2 * S * Fr(reps[j][2])
            else:
                raise ValueError(kind)
    return b, bij


# ---------------------------------------------------------------------------------------------------------------
# PGJ three-loop gauge + matter (single simple group).  Table re-transcribed from the repository module
# _record/g7_decoupled_singlet_benchmark_evidence_v20.py (PGJ_COEFFICIENTS); the fermion entries are verified below
# against the Tarasov-Vladimirov-Zharkov / Larin-Vermaseren QCD beta_2 with general Casimirs (independent memory
# of the literature), the scalar entries against the MSS SM values (U(1)_Y, SU(2)_L pure terms).
# beta_g = -g (a1 + 2 b1 + 3 c1);  b3 = -3 c1.  TR, TS = sums of T over Weyl fermions / REAL scalars.
# ---------------------------------------------------------------------------------------------------------------
C1 = {
    ("CG", 3): Fr(2857, 162), ("CG", 2, "TR", 1): Fr(-1415, 162), ("CG", 1, "TR", 2): Fr(79, 162),
    ("CG", 2, "TS", 1): Fr(-545, 648), ("CG", 1, "TR", 1, "TS", 1): Fr(29, 162), ("CG", 1, "TS", 2): Fr(-1, 324),
    ("CG", 1, "CS2", 1): Fr(-1129, 216), ("TR", 1, "CS2", 1): Fr(25, 54), ("TS", 1, "CS2", 1): Fr(49, 216),
    ("CG", 1, "CR2", 1): Fr(-205, 54), ("TR", 1, "CR2", 1): Fr(11, 27), ("TS", 1, "CR2", 1): Fr(23, 108),
    ("CR3", 1): Fr(1, 3), ("CS3", 1): Fr(-29, 12),
}


def b3_single(CG, TR, TS, CR2, CS2, CR3, CS3):
    inv = {"CG": CG, "TR": TR, "TS": TS, "CR2": CR2, "CS2": CS2, "CR3": CR3, "CS3": CS3}
    c1 = 0
    for key, coef in C1.items():
        term = coef
        it = iter(key)
        for name in it:
            power = next(it)
            term = term * inv[name] ** power
        c1 = c1 + term
    return -3 * c1


def single_group_invariants(cg, content):
    """content: list of (kind, (dim, T, C2), mult)."""
    TR = TS = CR2 = CS2 = CR3 = CS3 = Fr(0)
    for kind, (d, T, C2), mult in content:
        m = Fr(mult)
        if kind == "W":
            TR += m * T
            CR2 += m * T * C2
            CR3 += m * T * C2 * C2
        else:
            nr = m * (2 if kind == "C" else 1)
            TS += nr * T
            CS2 += nr * T * C2
            CS3 += nr * T * C2 * C2
    return dict(CG=Fr(cg), TR=TR, TS=TS, CR2=CR2, CS2=CS2, CR3=CR3, CS3=CS3)


def b123_single(cg, content):
    inv = single_group_invariants(cg, content)
    b1 = -(Fr(11, 3) * inv["CG"] - Fr(2, 3) * inv["TR"] - Fr(1, 6) * inv["TS"])
    b2 = -2 * (Fr(17, 3) * inv["CG"] ** 2 - Fr(5, 3) * inv["CG"] * inv["TR"] - Fr(1, 6) * inv["CG"] * inv["TS"]
               - inv["CS2"] - inv["CR2"])
    b3 = b3_single(**inv)
    return b1, b2, b3


# ---------------------------------------------------------------------------------------------------------------
# Checks of the three-loop table.
# ---------------------------------------------------------------------------------------------------------------
def check_qcd():
    """QCD, n_f Dirac flavours: beta2 = 2857/54 CA^3 + 2 CF^2 TF nf - 205/9 CF CA TF nf - 1415/27 CA^2 TF nf
    + 44/9 CF TF^2 nf^2 + 158/27 CA TF^2 nf^2 (Tarasov-Vladimirov-Zharkov 1980; Larin-Vermaseren 1993), b3 = -beta2.
    Checked numerically for (CA, CF, TF) = SU(3) and also SU(2), SU(5) fundamentals at several n_f: an exact identity in
    the Casimirs is implied if all these agree (the fermion part of the table is linear in 5 monomials)."""
    out = {}
    ok = True
    for N in (2, 3, 5):
        CA, CF, TF = Fr(N), Fr(N * N - 1, 2 * N), Fr(1, 2)
        for nf in (0, 1, 3, 5, 6, 12):
            beta2 = (Fr(2857, 54) * CA**3 + 2 * CF**2 * TF * nf - Fr(205, 9) * CF * CA * TF * nf
                     - Fr(1415, 27) * CA**2 * TF * nf + Fr(44, 9) * CF * TF**2 * nf**2 + Fr(158, 27) * CA * TF**2 * nf**2)
            TR = 2 * nf * TF
            b3 = b3_single(CA, TR, Fr(0), TR * CF, Fr(0), TR * CF * CF, Fr(0))
            ok = ok and (b3 == -beta2)
            out[f"SU({N})_nf{nf}"] = str(b3)
    out["all_equal_minus_beta2"] = ok
    out["SU3_nf5_nf6"] = [out["SU(3)_nf5"], out["SU(3)_nf6"]]
    return out


def check_sm_mss():
    """SM pure (alpha_i)^4 three-loop terms: MSS arXiv:1201.5868 give -388613/24000 (U(1)_Y GUT-normalised),
    324953/1728 (SU(2)_L), 65/2 (SU(3)_C) for n_G = 3, one Higgs doublet."""
    q2 = lambda y: Fr(3, 5) * Fr(y) ** 2  # noqa: E731
    fam = [(q2(Fr(1, 6)), 6), (q2(Fr(-2, 3)), 3), (q2(Fr(1, 3)), 3), (q2(Fr(-1, 2)), 2), (q2(1), 1)]
    # U(1)_Y: CG = 0; T = C2 = q^2 for every component
    cont_u1 = [("W", (1, q, q), 3 * m) for q, m in fam] + [("C", (1, q2(Fr(1, 2)), q2(Fr(1, 2))), 2)]  # doublet = 2 complex components
    cont_su2 = [("W", su2(2), 3 * 3), ("W", su2(2), 3), ("C", su2(2), 1)]  # Q (3 colours) and L per family; H
    cont_su3 = [("W", su3(3), 3 * 2), ("W", su3(3), 3), ("W", su3(3), 3)]  # Q (2 isospin), u^c, d^c
    r = {}
    r["U1_Y"] = [str(x) for x in b123_single(0, cont_u1)]
    r["SU2_L"] = [str(x) for x in b123_single(2, cont_su2)]
    r["SU3_C"] = [str(x) for x in b123_single(3, cont_su3)]
    r["matches_MSS"] = (r["U1_Y"] == ["41/10", "199/50", "-388613/24000"] and r["SU2_L"] == ["-19/6", "35/6", "324953/1728"]
                        and r["SU3_C"] == ["-7", "-26", "65/2"])
    return r


# ---------------------------------------------------------------------------------------------------------------
# v21-F17-G3221 content.
# ---------------------------------------------------------------------------------------------------------------
def ysq(y):  # GUT-normalised hypercharge
    return Fr(3, 5) * Fr(y) ** 2


def blsq(q):  # GUT-normalised B-L: sqrt(3/8)(B-L)
    return Fr(3, 8) * Fr(q) ** 2


def sm_rep(y, n2, n3):
    return (u1(ysq(y)), su2(n2), su3(n3))


def g_rep(n3, n2l, n2r, bl):
    return (su3(n3), su2(n2l), su2(n2r), u1(blsq(bl)))


# SM order (U(1)_Y, SU(2)_L, SU(3)_C); G3221 order (SU(3), SU(2)_L, SU(2)_R, U(1)_{B-L}).
SM_CG = (0, 2, 3)
G_CG = (3, 2, 2, 0)


def sm_fields(n16_extra=0, n10=0, n_higgs=1):
    f = []
    per16 = [("W", sm_rep(Fr(1, 6), 2, 3)), ("W", sm_rep(Fr(-2, 3), 1, 3)), ("W", sm_rep(Fr(1, 3), 1, 3)),
             ("W", sm_rep(Fr(-1, 2), 2, 1)), ("W", sm_rep(Fr(1), 1, 1)), ("W", sm_rep(Fr(0), 1, 1))]
    f += [(k, r, 3 + n16_extra) for k, r in per16]
    per10 = [("W", sm_rep(Fr(-1, 3), 1, 3)), ("W", sm_rep(Fr(1, 3), 1, 3)), ("W", sm_rep(Fr(1, 2), 2, 1)),
             ("W", sm_rep(Fr(-1, 2), 2, 1))]
    f += [(k, r, n10) for k, r in per10]
    f.append(("C", sm_rep(Fr(1, 2), 2, 1), n_higgs))
    return f


def g3221_fields(content, with_s=True):
    n16 = 3 + (6 if with_s else 0)
    per16 = [("W", g_rep(3, 2, 1, Fr(1, 3))), ("W", g_rep(3, 1, 2, Fr(-1, 3))), ("W", g_rep(1, 2, 1, Fr(-1))),
             ("W", g_rep(1, 1, 2, Fr(1)))]
    f = [(k, r, n16) for k, r in per16]
    if with_s:
        f += [("W", g_rep(3, 1, 1, Fr(-2, 3)), 2), ("W", g_rep(3, 1, 1, Fr(2, 3)), 2), ("W", g_rep(1, 2, 2, 0), 2)]
    # light scalars
    f += [("C", g_rep(1, 2, 2, 0), 1), ("C", g_rep(1, 1, 3, 2), 1), ("C", g_rep(8, 2, 2, 0), 1),
          ("R", g_rep(8, 3, 1, 0), 1), ("R", g_rep(1, 3, 1, 0), 1)]
    if content == "T3":
        f += [("C", g_rep(1, 2, 2, 0), 1), ("R", g_rep(8, 1, 1, 0), 1)]
    return f


SO10_CONTENT = [("W", so10(16), 3), ("W", so10(16), 6), ("W", so10(10), 2), ("R", so10(210), 1), ("C", so10(126), 1),
                ("C", so10(10), 1)]
SO10_PHI = [("W", so10(16), 2)]
SO10_V20_NOPQR = [("W", so10(16), 13), ("R", so10(210), 1), ("C", so10(126), 1), ("C", so10(10), 1)]
SO10_V20_PQR = SO10_V20_NOPQR + [("W", so10(16), 6)]


def fstr(x):
    if isinstance(x, list):
        return [fstr(y) for y in x]
    return str(x)


if __name__ == "__main__":
    out = {}
    out["qcd"] = check_qcd()
    out["sm_mss"] = check_sm_mss()
    for name, cont in (("v21_below_Mphi", SO10_CONTENT), ("v21_above_Mphi", SO10_CONTENT + SO10_PHI),
                       ("v20_noPQR", SO10_V20_NOPQR), ("v20_withPQR", SO10_V20_PQR)):
        b = b123_single(8, cont)
        # MV cross-check of b1, b2 with the product-group routine (single factor)
        bmv, bijmv = mv((8,), [(k, (r,), m) for k, r, m in cont])
        out[name] = {"b123": fstr(list(b)), "num": [float(x) for x in b], "mv_b1_b2_equal": (bmv[0] == b[0] and bijmv[0][0] == b[1]),
                     "invariants": {k: str(v) for k, v in single_group_invariants(8, cont).items()}}
    out["so10_pins_ok"] = (out["v21_below_Mphi"]["b123"] == ["16/3", "20891/6", "142437589/864"]
                           and out["v21_above_Mphi"]["b123"] == ["8", "7267/2", "5041501/32"]
                           and out["v20_noPQR"]["b123"] == ["28/3", "22283/6", "132706057/864"]
                           and out["v20_withPQR"]["b123"] == ["52/3", "25013/6", "109873879/864"])
    # term-by-term decomposition of the v21 b3 (to show the cancellation structure)
    inv = single_group_invariants(8, SO10_CONTENT)
    terms = {}
    for key, coef in C1.items():
        term = -3 * coef
        it = iter(key)
        label = []
        for nm in it:
            p = next(it)
            term *= inv[nm] ** p
            label.append(f"{nm}^{p}" if p > 1 else nm)
        terms["*".join(label)] = float(term)
    out["v21_b3_terms"] = terms
    for name, flds in (("SM_1HDM", sm_fields()), ("SM_plus_S", sm_fields(6, 2)), ("SM_2HDM", sm_fields(0, 0, 2))):
        b, bij = mv(SM_CG, flds)
        out[name] = {"b": fstr(b), "bij": fstr(bij)}
    for content in ("T2", "T3"):
        for ws in (True, False):
            b, bij = mv(G_CG, g3221_fields(content, ws))
            out[f"G3221_{content}_{'withS' if ws else 'noS'}"] = {"b": fstr(b), "bij": fstr(bij)}
    # comparisons with the researcher's JSON
    rj = json.load(open(os.path.join(HERE, "..", "k1_test_coeffs.json")))
    cmp = {}
    cmp["SM_1HDM"] = out["SM_1HDM"]["b"] == rj["SM_1HDM_b"] and out["SM_1HDM"]["bij"] == rj["SM_1HDM_bij"]
    cmp["SM_plus_S"] = out["SM_plus_S"]["b"] == rj["SM_withS_b"] and out["SM_plus_S"]["bij"] == rj["SM_withS_bij"]
    for content in ("T2", "T3"):
        cmp[f"{content}_withS"] = (out[f"G3221_{content}_withS"]["b"] == rj[f"{content}_G3221_withS_b"]
                                   and out[f"G3221_{content}_withS"]["bij"] == rj[f"{content}_G3221_withS_bij"])
        cmp[f"{content}_noS"] = (out[f"G3221_{content}_noS"]["b"] == rj[f"{content}_G3221_noS_b"]
                                 and out[f"G3221_{content}_noS"]["bij"] == rj[f"{content}_G3221_noS_bij"])
    cmp["SO10_v21"] = (out["v21_below_Mphi"]["b123"] == rj["SO10_v21_below_Mphi"]
                       and out["v21_above_Mphi"]["b123"] == rj["SO10_v21_above_Mphi"])
    out["comparison_with_researcher"] = cmp
    json.dump(out, open(os.path.join(HERE, "vp_coeffs.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k in ("qcd", "sm_mss", "so10_pins_ok", "comparison_with_researcher")}, indent=1))
    for name in ("v21_below_Mphi", "v21_above_Mphi"):
        print(name, out[name]["b123"], out[name]["num"])
    print("b3 terms (v21 below Mphi):")
    for k, v in sorted(terms.items(), key=lambda kv: -abs(kv[1])):
        print(f"   {k:16s} {v:12.1f}")
    for k in ("G3221_T2_withS", "G3221_T3_withS", "SM_plus_S"):
        print(k, out[k])
