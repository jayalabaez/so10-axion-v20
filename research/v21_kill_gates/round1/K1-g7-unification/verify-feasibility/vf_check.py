#!/usr/bin/env python3
"""Independent verifier check of K1 (v21-F17-G3221): own MV coefficients, own PGJ b3, own chain solve, own Landau scales.
Written from scratch (no import of the researcher's k1_* modules).  Gauge-only two-loop + three-loop (SO(10)) chain.
"""
import json, math, os
from fractions import Fraction as F
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

HERE = os.path.dirname(os.path.abspath(__file__))
PI = math.pi
MPL = 2.435e18
MZ = 91.1876
A1, A2, A3 = 59.02, 29.57, 1 / 0.1179
OUT = {}

# ---------------- generic exact MV ----------------
def mv(cg, fields):
    """fields: list of (kind, [(dim,T,C2) per factor], mult). kind in weyl/cplx/real. Returns (b, bij) exact."""
    n = len(cg)
    b = [F(-11, 3) * c for c in cg]
    bij = [[F(-34, 3) * cg[i] ** 2 if i == j else F(0) for j in range(n)] for i in range(n)]
    for kind, reps, m in fields:
        for i in range(n):
            S = F(reps[i][1]) * F(m)
            for k in range(n):
                if k != i:
                    S *= reps[k][0]
            if S == 0:
                continue
            if kind == "weyl":
                b[i] += F(2, 3) * S
                for j in range(n):
                    bij[i][j] += 2 * S * F(reps[j][2])
                bij[i][i] += F(10, 3) * cg[i] * S
            elif kind == "cplx":
                b[i] += F(1, 3) * S
                for j in range(n):
                    bij[i][j] += 4 * S * F(reps[j][2])
                bij[i][i] += F(2, 3) * cg[i] * S
            elif kind == "real":
                b[i] += F(1, 6) * S
                for j in range(n):
                    bij[i][j] += 2 * S * F(reps[j][2])
                bij[i][i] += F(1, 3) * cg[i] * S
    return b, bij

def thr(kind, reps, i, m=1):
    S = F(reps[i][1]) * F(m)
    for k in range(len(reps)):
        if k != i:
            S *= reps[k][0]
    return {"weyl": F(2, 3), "cplx": F(1, 3), "real": F(1, 6), "vector": F(-7, 2)}[kind] * S

# rep data
def su2(d):
    return {1: (1, F(0), F(0)), 2: (2, F(1, 2), F(3, 4)), 3: (3, F(2), F(2))}[d]
def su3(d):
    return {1: (1, F(0), F(0)), 3: (3, F(1, 2), F(4, 3)), 6: (6, F(5, 2), F(10, 3)), 8: (8, F(3), F(3))}[d]
def uy(y):   # GUT-normalised hypercharge
    q2 = F(3, 5) * F(y) ** 2
    return (1, q2, q2)
def ubl(q):  # GUT-normalised B-L
    q2 = F(3, 8) * F(q) ** 2
    return (1, q2, q2)

# ---------------- SM phase: (U1Y, SU2L, SU3) ----------------
SM_CG = (F(0), F(2), F(3))
def smr(y, d2, d3):
    return (uy(y), su2(d2), su3(d3))
SIXTEEN_SM = [smr(F(1, 6), 2, 3), smr(F(-2, 3), 1, 3), smr(F(1, 3), 1, 3), smr(F(-1, 2), 2, 1), smr(F(1), 1, 1), smr(F(0), 1, 1)]
TEN_SM = [smr(F(-1, 3), 1, 3), smr(F(1, 3), 1, 3), smr(F(1, 2), 2, 1), smr(F(-1, 2), 2, 1)]
def sm_fields(extra16=0, n10=0, ndoub=1):
    f = [("weyl", r, 3 + extra16) for r in SIXTEEN_SM] + [("weyl", r, n10) for r in TEN_SM]
    f.append(("cplx", smr(F(1, 2), 2, 1), ndoub))
    return f

# ---------------- G3221: (SU3, SU2L, SU2R, U1BL) ----------------
G_CG = (F(3), F(2), F(2), F(0))
def gr(d3, d2l, d2r, bl):
    return (su3(d3), su2(d2l), su2(d2r), ubl(bl))
SIXTEEN_G = [gr(3, 2, 1, F(1, 3)), gr(3, 1, 2, F(-1, 3)), gr(1, 2, 1, F(-1)), gr(1, 1, 2, F(1))]
TEN_G = [gr(3, 1, 1, F(-2, 3)), gr(3, 1, 1, F(2, 3)), gr(1, 2, 2, F(0))]
def light_scalars(content):
    s = [("cplx", gr(1, 2, 2, 0), 1), ("cplx", gr(1, 1, 3, 2), 1), ("cplx", gr(8, 2, 2, 0), 1),
         ("real", gr(8, 3, 1, 0), 1), ("real", gr(1, 3, 1, 0), 1)]
    if content == "T3":
        s += [("cplx", gr(1, 2, 2, 0), 1), ("real", gr(8, 1, 1, 0), 1)]
    return s
def g_fields(content, withS=True):
    f = [("weyl", r, 3 + (6 if withS else 0)) for r in SIXTEEN_G]
    if withS:
        f += [("weyl", r, 2) for r in TEN_G]
    return f + light_scalars(content)

# ---------------- SO(10) single group with PGJ ----------------
SO10 = {"10": (10, F(1), F(9, 2)), "16": (16, F(2), F(45, 8)), "210": (210, F(56), F(12)), "126": (126, F(35), F(25, 2))}
CG10 = F(8)
PGJ = {"a1": [("CG", F(11, 3)), ("TR", F(-2, 3)), ("TS", F(-1, 6))],
       "b1": [("CG CG", F(17, 3)), ("CG TR", F(-5, 3)), ("CG TS", F(-1, 6)), ("CS2", F(-1)), ("CR2", F(-1))],
       "c1": [("CG CG CG", F(2857, 162)), ("CG CG TR", F(-1415, 162)), ("CG TR TR", F(79, 162)), ("CG CG TS", F(-545, 648)),
              ("CG TR TS", F(29, 162)), ("CG TS TS", F(-1, 324)), ("CG CS2", F(-1129, 216)), ("TR CS2", F(25, 54)),
              ("TS CS2", F(49, 216)), ("CG CR2", F(-205, 54)), ("TR CR2", F(11, 27)), ("TS CR2", F(23, 108)),
              ("CR3", F(1, 3)), ("CS3", F(-29, 12))]}
def pgj(content, cg, reps):
    inv = {"CG": cg, "TR": F(0), "TS": F(0), "CR2": F(0), "CS2": F(0), "CR3": F(0), "CS3": F(0)}
    for rep, kind, m in content:
        d, t, c = reps[rep]
        if kind == "weyl":
            inv["TR"] += m * t; inv["CR2"] += m * t * c; inv["CR3"] += m * t * c * c
        else:
            nr = m * (2 if kind == "cplx" else 1)
            inv["TS"] += nr * t; inv["CS2"] += nr * t * c; inv["CS3"] += nr * t * c * c
    out = {}
    for order, terms in PGJ.items():
        s = F(0)
        for expr, coef in terms:
            v = coef
            for tok in expr.split():
                v *= inv[tok]
            s += v
        out[order] = s
    return (-out["a1"], -2 * out["b1"], -3 * out["c1"])

# QCD check: general Casimir, nf Dirac fundamentals -> compare with literature beta2
def qcd_check():
    import sympy as sp
    CA, CF, TF, nf = sp.symbols("CA CF TF nf")
    inv = {"CG": CA, "TR": 2 * nf * TF, "TS": 0, "CR2": 2 * nf * TF * CF, "CS2": 0, "CR3": 2 * nf * TF * CF ** 2, "CS3": 0}
    s = 0
    for expr, coef in PGJ["c1"]:
        v = sp.Rational(coef.numerator, coef.denominator)
        for tok in expr.split():
            v *= inv[tok]
        s += v
    b3 = -3 * s
    beta2 = (sp.Rational(2857, 54) * CA ** 3 + 2 * CF ** 2 * TF * nf - sp.Rational(205, 9) * CF * CA * TF * nf
             - sp.Rational(1415, 27) * CA ** 2 * TF * nf + sp.Rational(44, 9) * CF * TF ** 2 * nf ** 2 + sp.Rational(158, 27) * CA * TF ** 2 * nf ** 2)
    return sp.simplify(b3 + beta2) == 0

OUT["qcd_pgj_b3_equals_minus_beta2_general_casimir"] = qcd_check()

SO10_BASE = [("16", "weyl", 3), ("16", "weyl", 6), ("10", "weyl", 2), ("210", "real", 1), ("126", "cplx", 1), ("10", "cplx", 1)]
SO10_HI = SO10_BASE + [("16", "weyl", 2)]
SO10_V20 = [("16", "weyl", 3), ("16", "weyl", 10), ("210", "real", 1), ("126", "cplx", 1), ("10", "cplx", 1)]
b_lo = pgj(SO10_BASE, CG10, SO10)
b_hi = pgj(SO10_HI, CG10, SO10)
b_v20 = pgj(SO10_V20, CG10, SO10)
OUT["so10_v21_below_Mphi"] = [str(x) for x in b_lo]
OUT["so10_v21_above_Mphi"] = [str(x) for x in b_hi]
OUT["so10_v20_noPQR_pin_check"] = [str(x) for x in b_v20]
OUT["so10_v21_matches_researcher"] = (b_lo == (F(16, 3), F(20891, 6), F(142437589, 864)) and b_hi == (F(8), F(7267, 2), F(5041501, 32)))
OUT["so10_v20_matches_repo_pin"] = (b_v20 == (F(28, 3), F(22283, 6), F(132706057, 864)))
# MV check of b1,b2 for SO(10) via the generic routine
so10_fields = [("weyl", [SO10["16"]], 9), ("weyl", [SO10["10"]], 2), ("real", [SO10["210"]], 1), ("cplx", [SO10["126"]], 1), ("cplx", [SO10["10"]], 1)]
bmv, bijmv = mv((CG10,), so10_fields)
OUT["so10_mv_b1b2_equal_pgj"] = (bmv[0] == b_lo[0] and bijmv[0][0] == b_lo[1])

# ---------------- segment coefficients ----------------
b_sm0, bij_sm0 = mv(SM_CG, sm_fields(0, 0, 1))
b_sm1, bij_sm1 = mv(SM_CG, sm_fields(6, 2, 1))
coef = {"SM": (b_sm0, bij_sm0), "SMS": (b_sm1, bij_sm1)}
for c in ("T2", "T3"):
    coef[c] = mv(G_CG, g_fields(c, True))
    coef[c + "noS"] = mv(G_CG, g_fields(c, False))
OUT["b_SM"] = [str(x) for x in b_sm0]
OUT["bij_SM"] = [[str(x) for x in r] for r in bij_sm0]
OUT["b_SMS"] = [str(x) for x in b_sm1]
OUT["b_T2"] = [str(x) for x in coef["T2"][0]]
OUT["bij_T2"] = [[str(x) for x in r] for r in coef["T2"][1]]
OUT["b_T3"] = [str(x) for x in coef["T3"][0]]
OUT["bij_T3"] = [[str(x) for x in r] for r in coef["T3"][1]]
OUT["b_T2_matches"] = coef["T2"][0] == [F(47, 6), F(12), F(29, 3), F(89, 6)]
OUT["b_T3_matches"] = coef["T3"][0] == [F(25, 3), F(37, 3), F(10), F(89, 6)]
OUT["bij_T2_SU2L_row_matches_json"] = coef["T2"][1][1] == [F(228), F(241), F(30), F(9, 2)]
OUT["bij_T2_SU3_row_matches_json"] = coef["T2"][1][0] == [F(1147, 3), F(171, 2), F(99, 2), F(13, 6)]
OUT["bij_T2_SU2R_row_matches_json"] = coef["T2"][1][2] == [F(132), F(30), F(527, 3), F(33, 2)]
OUT["bij_T2_BL_row_matches_json"] = coef["T2"][1][3] == [F(52, 3), F(27, 2), F(99, 2), F(229, 6)]
OUT["bij_SM_literature"] = bij_sm0 == [[F(199, 50), F(27, 10), F(44, 5)], [F(9, 10), F(35, 6), F(12)], [F(11, 10), F(9, 2), F(-26)]]

# heavy scalars at M_U (G3221 language) -> only for sum-rule check (nominal thresholds at M_U contribute nothing)
# ---------------- running ----------------
def rhs_factory(b, bij, loops, b3=None):
    bb = np.array([float(x) for x in b]); BB = np.array([[float(x) for x in r] for r in bij])
    b3v = np.zeros(len(bb)) if b3 is None else np.array([float(x) for x in b3])
    def rhs(t, a):
        d = -bb / (2 * PI)
        if loops >= 2:
            d = d - BB.dot(1 / a) / (8 * PI ** 2)
        if loops >= 3:
            d = d - b3v / a ** 2 / (32 * PI ** 3)
        return d
    return rhs

def run(rhs, a0, t0, t1):
    if abs(t1 - t0) < 1e-14:
        return np.array(a0)
    sol = solve_ivp(rhs, (t0, t1), np.array(a0, float), method="DOP853", rtol=1e-11, atol=1e-13)
    return sol.y[:, -1]

def chain(content, loops, M_s, x):
    lnv, lnu, a2R = x
    tz, ts, tv, tu = math.log(MZ), math.log(M_s), lnv, lnu
    r_sm0 = rhs_factory(*coef["SM"], loops)
    r_sm1 = rhs_factory(*coef["SMS"], loops)
    a = np.array([A1, A2, A3])
    if ts < tv:
        a = run(r_sm0, a, tz, ts); a = run(r_sm1, a, ts, tv)
    else:
        a = run(r_sm0, a, tz, tv)
    a1, a2, a3 = a
    aBL = 2.5 * (a1 - 0.6 * a2R)
    g = np.array([a3, a2, a2R, aBL])
    rg = rhs_factory(*coef[content], loops)
    rgn = rhs_factory(*coef[content + "noS"], loops)
    if ts < tv:
        g = run(rg, g, tv, tu)
    else:
        g = run(rgn, g, tv, min(ts, tu))
        if ts < tu:
            g = run(rg, g, ts, tu)
    return g

def solve(content, loops, M_s, guess=(math.log(2.5e13), math.log(2.5e16), 46.0)):
    def fun(x):
        g = chain(content, loops, M_s, x)
        return [g[0] - g[1], g[2] - g[1], g[3] - g[1]]
    x, info, ier, msg = fsolve(fun, np.array(guess), full_output=True, xtol=1e-12)
    g = chain(content, loops, M_s, x)
    return {"ok": ier == 1, "v_R": math.exp(x[0]), "M_U": math.exp(x[1]), "alpha_U_inv": float(g[1]), "resid": float(np.max(np.abs(fun(x))))}

def landau(M_U, aU, loops, M_phi, Y_lo=0.0, Y_hi=0.0, b3fac=1.0, tend=math.log(1e24)):
    """alpha_10 = 1 scale; SO(10) phase below/above M_phi; optional Yukawa 2-loop term Y/(32 pi^3)."""
    def mk(bb, Y):
        b1, b2, b3 = (float(v) for v in bb)
        def rhs(t, a):
            d = -b1 / (2 * PI)
            if loops >= 2:
                d -= b2 / a[0] / (8 * PI ** 2)
                d += Y / (32 * PI ** 3)
            if loops >= 3:
                d -= b3fac * b3 / a[0] ** 2 / (32 * PI ** 3)
            return [d]
        return rhs
    def ev(t, a):
        return a[0] - 1.0
    ev.terminal = True; ev.direction = -1
    tu, tp = math.log(M_U), math.log(max(M_phi, M_U))
    s = solve_ivp(mk(b_lo, Y_lo), (tu, tp), [aU], method="DOP853", rtol=1e-11, atol=1e-13, events=ev)
    if s.t_events[0].size:
        return math.exp(s.t_events[0][0]), s
    s2 = solve_ivp(mk(b_hi, Y_hi), (tp, tend), [s.y[0, -1]], method="DOP853", rtol=1e-11, atol=1e-13, events=ev, dense_output=True)
    if s2.t_events[0].size:
        return math.exp(s2.t_events[0][0]), s2
    return float("inf"), s2

res = {}
for content in ("T2", "T3"):
    r1 = solve(content, 1, 1e13)
    r2 = solve(content, 2, 1e13)
    r2b = solve(content, 2, 5e12)
    res[content] = {"1L_Ms1e13": r1, "2L_Ms1e13": r2, "2L_Ms5e12": r2b}
    for tag, r in (("2L_Ms1e13", r2), ("2L_Ms5e12", r2b)):
        for L in (2, 3):
            for mphi in (1e17, 1e10):
                lam, _ = landau(r["M_U"], r["alpha_U_inv"], L, mphi)
                r[f"Lambda_{L}L_Mphi={mphi:.0e}"] = lam
                r[f"Lambda_{L}L_Mphi={mphi:.0e}_over_MPl"] = lam / MPL
    # with the researcher's Yukawa term values (Y_lo = 11.8, Y_hi = 15.8 for Y126_33 = 0.5): sensitivity only
    r = r2
    lamY, _ = landau(r["M_U"], r["alpha_U_inv"], 3, 1e17, Y_lo=11.81, Y_hi=15.81)
    r["Lambda_3L_with_Yukawa_term_at_gauge_only_solution"] = lamY / MPL
    # b3 scaling
    for f in (0.75, 1.25):
        r[f"Lambda_3L_b3x{f}_over_MPl"] = landau(r["M_U"], r["alpha_U_inv"], 3, 1e17, b3fac=f)[0] / MPL
    # d ln Lambda / d alpha_U^-1
    lp = landau(r["M_U"], r["alpha_U_inv"] + 0.25, 3, 1e17)[0]; lm = landau(r["M_U"], r["alpha_U_inv"] - 0.25, 3, 1e17)[0]
    r["dlnLambda3_dalphaUinv"] = (math.log(lp) - math.log(lm)) / 0.5
    # alpha = 4 pi convention (g = 4 pi)? no: report alpha^-1 at M_Pl at 2L and 3L instead
    for L in (2, 3):
        _, s = landau(r["M_U"], r["alpha_U_inv"], L, 1e17, tend=math.log(MPL))
        r[f"alpha_inv_at_MPl_{L}L"] = float(s.y[0, -1]) if not s.t_events[0].size else None
    # loop-term ratios at M_U (below M_phi coefficients) and at M_Pl (above)
    aU = r["alpha_U_inv"]
    b1, b2, b3 = (float(v) for v in b_lo)
    r["ratio_2L_over_1L_at_MU"] = (b2 / aU / (8 * PI ** 2)) / (b1 / (2 * PI))
    r["ratio_3L_over_2L_at_MU"] = (b3 / aU ** 2 / (32 * PI ** 3)) / (b2 / aU / (8 * PI ** 2))
    b1h, b2h, b3h = (float(v) for v in b_hi)
    aP = r["alpha_inv_at_MPl_3L"]
    if aP:
        r["ratio_2L_over_1L_at_MPl_3Ltraj"] = (b2h / aP / (8 * PI ** 2)) / (b1h / (2 * PI))
        r["ratio_3L_over_2L_at_MPl_3Ltraj"] = (b3h / aP ** 2 / (32 * PI ** 3)) / (b2h / aP / (8 * PI ** 2))
    # scale at which 3L/2L = 0.5 on the 3L trajectory (above M_phi: alpha^-1 = b3h/(2 b2h) * 1/(4 pi) ... solve)
    # 3L/2L = b3 alpha/(4 pi b2) -> alpha^-1 = b3/(4 pi b2 * 0.5)
    r["alpha_inv_where_3L_over_2L_is_half"] = b3h / (4 * PI * b2h * 0.5)
OUT["chain"] = res

# ---------------- quality, axion, U(1)_X ----------------
chi = 0.0755 ** 4
def smax(n, phi):
    return math.exp((math.log(1e-10) + math.log(chi) + 17 * math.log(MPL) - math.log(n) - 4 * math.log(phi)) / 17)
q = {}
for n, phi, lab in ((17, 1e17, "A"), (1, 1e17, "B"), (17, 1e17 / math.sqrt(2), "A_phi_over_sqrt2")):
    S = smax(n, phi)
    fa = math.sqrt(2) * S / 17
    q[lab] = {"S_max": S, "y_s_min_1e13": 1e13 / S, "f_a": fa, "m_a_ueV": 5.70 * 1e12 / fa}
OUT["quality_axion"] = q
# U(1)_X
bx = F(2, 3) * (3 * 16 + 16 * 16 + 16 * 9 + 16 * 49 + 16 * 36 + 16 * 100 + 10 * 1 + 10 * 25 + 2 * 9 + 2 * 1 + 16 * 81 + 16 * 64) + F(1, 3) * (126 * 4 + 10 * 4 + 16 + 289)
OUT["b_X_full"] = str(bx)
axinv = 1 + float(bx) / (2 * PI) * math.log(MPL / 1e17)
OUT["gX_max_1e17"] = math.sqrt(4 * PI / axinv)
# proton lifetime repo normalisation
def tau_p(MX, ainv):
    f_pi, m_p, aH, AR, Fq = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    tau = (4 / PI) * (f_pi ** 2 / m_p) * (MX ** 4 * ainv ** 2) / (aH ** 2 * AR ** 2 * Fq)
    return tau * 6.582119569e-25 / (365.25 * 24 * 3600)
OUT["tau_p_T2_nominal"] = tau_p(2.045e16, 27.102)
OUT["tau_p_T3_nominal"] = tau_p(2.914e16, 26.129)

with open(os.path.join(HERE, "vf_check.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
