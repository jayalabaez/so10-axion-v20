#!/usr/bin/env python3
"""Chain-specific short-distance enhancement A_SD of the gauge d = 6 operators (one-loop anomalous dimensions,
couplings from the two-loop chain of sk2_lib), compared with the fixed A_R = 2.726 of the repository formula.

gamma for an operator (psi1 psi2)(psi3 psi4) of left-handed Weyl fields: gamma = -3 sum_{same-bilinear pairs} T_i.T_j
(reproduces the SM values 2, 9/4, 23/20 and 11/20 exactly - checked below).  G3221 operators from (3,2,2) exchange:
(Q Q)(Q^c L^c), (Q L)(Q^c Q^c): gamma = (2, 9/4, 9/4, 1/4).  A_SD = exp( int_{MZ}^{MU} sum_i gamma_i alpha_i / (2 pi) dt ).
Also: Super-K survival of the C2 nominal point and the R2-A C2-family spectra with A_R = 1.25 * A_SD (EST)."""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sk2_lib as L

# --- check the gamma formula on the SM operators ---
def gam_u1(pairs, norm):
    return -3 * norm * sum(a * b for a, b in pairs)

g1_ec = gam_u1([(Fr(1, 6), Fr(1, 6)), (Fr(-2, 3), Fr(1))], Fr(3, 5))
g1_e = gam_u1([(Fr(1, 6), Fr(-1, 2)), (Fr(-2, 3), Fr(1, 3))], Fr(3, 5))
gBL_1 = gam_u1([(Fr(1, 3), Fr(1, 3)), (Fr(-1, 3), Fr(1))], Fr(3, 8))
gBL_2 = gam_u1([(Fr(1, 3), Fr(-1)), (Fr(-1, 3), Fr(-1, 3))], Fr(3, 8))
su2_pair = -3 * (Fr(0) - 2 * Fr(3, 4)) / 2          # two doublets -> singlet
su3_pair = -3 * (Fr(4, 3) - 2 * Fr(4, 3)) / 2       # two triplets -> antitriplet (third quark completes the singlet)
print("gamma check: U1 e^c", g1_ec, "U1 e", g1_e, "BL", gBL_1, gBL_2, "SU2", su2_pair, "SU3", su3_pair)

G_SM = {"ec": np.array([float(g1_ec), 2.25, 2.0]), "e": np.array([float(g1_e), 2.25, 2.0])}
G_G = np.array([2.0, 2.25, 2.25, float(gBL_1)])


def integ(rhs, a0, t0, t1, gam):
    """run couplings and accumulate int sum gamma_i alpha_i/(2 pi) dt."""
    if abs(t1 - t0) < 1e-14:
        return np.array(a0, float), 0.0

    def f(t, y):
        a = y[:-1]
        return np.concatenate([rhs(t, a), [float(np.sum(gam / a)) / (2 * math.pi)]])
    s = solve_ivp(f, (t0, t1), np.concatenate([np.array(a0, float), [0.0]]), method="DOP853", rtol=1e-11, atol=1e-12)
    return s.y[:-1, -1], s.y[-1, -1]


def asd(model, sol, chir):
    lvR, lMU = math.log(sol["v_R"]), math.log(sol["M_U"])
    t0, ts = math.log(L.MZ), math.log(model.M_s)
    a = np.array([L.A1I_MZ, L.A2I_MZ, 1 / L.A3_MZ])
    I = 0.0
    if ts < lvR:
        a, i1 = integ(model.segs["sm0"][2], a, t0, ts, G_SM[chir]); I += i1
        a, i1 = integ(model.segs["sm1"][2], a, ts, lvR, G_SM[chir]); I += i1
    else:
        a, i1 = integ(model.segs["sm0"][2], a, t0, lvR, G_SM[chir]); I += i1
    a = a + model.Dl
    gg = np.array([a[2], a[1], sol["a2R"], 2.5 * (a[0] - 0.6 * sol["a2R"])])
    if ts < lvR:
        gg, i1 = integ(model.segs["g1"][2], gg, lvR, lMU, G_G); I += i1
    elif ts < lMU:
        gg, i1 = integ(model.segs["g0"][2], gg, lvR, ts, G_G); I += i1
        gg, i1 = integ(model.segs["g1"][2], gg, ts, lMU, G_G); I += i1
    else:
        gg, i1 = integ(model.segs["g0"][2], gg, lvR, lMU, G_G); I += i1
    return math.exp(I)


out = {"gamma": {"U1_ec": str(g1_ec), "U1_e": str(g1_e), "BL": str(gBL_1), "SU2": str(su2_pair), "SU3": str(su3_pair)}}
A_L = 1.25
cases = []
for c, guess in [("C2", (math.log(2e10), math.log(6e15), 40.0)), ("C1p", (math.log(1e11), math.log(3e15), 40.0)),
                 ("C1", (math.log(8e12), math.log(2e15), 40.0)), ("C0", (math.log(6e12), math.log(3e15), 40.0))]:
    m = L.Model(c)
    s = m.solve(guess)
    cases.append((c, m, s))
# R2-A C2-family spectra
src = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "r2b_r2a_c2check.json")))
MAPN = {
    "210:(3,1,3)_4/3": "210(3,1,3)", "126b:(6b,1,3)_-2/3": "126(6b,1,3)", "126b:(3b,1,3)_2/3": "126(3b,1,3)",
    "210:(8,1,3)_0": "210(8,1,3)", "210:(1,1,3)_0": "210(1,1,3)", "210:(6,2,2)_2/3": "210(6,2,2)",
    "210:(3,2,2)_-2/3 phys": "210(3,2,2)", "210:(1,2,2)_-2": "210(1,2,2)-2", "126b:(3,2,2)_4/3": "126(3,2,2)",
    "126b:(3b,2,2)_-4/3": "126(3b,2,2)", "126b:(8,2,2)_0": "126(8,2,2)", "210:(8,1,1)_0": "210(8,1,1)",
    "210:(3,3,1)_4/3": "210(3,3,1)", "210:(8,3,1)_0": "210(8,3,1)", "210:(1,3,1)_0": "210(1,3,1)",
    "126b:(3,1,1)_-2/3": "126(3,1,1)", "126b:(3b,1,1)_2/3": "126(3b,1,1)", "126b:(6,3,1)_2/3": "126(6,3,1)",
    "126b:(3,3,1)_-2/3": "126(3,3,1)", "126b:(1,3,1)_-2 Delta_L": "126(1,3,1)", "10:(3,1,1)_-2/3": "10(3,1,1)",
    "10:(3b,1,1)_2/3": "10(3b,1,1)",
}
MXG = math.sqrt(0.25 + 1.0 / 6.0)
for pt, d in src.items():
    m2 = {MAPN[k]: v for k, v in d["assigned_m2_over_Phi2"].items()}
    aU, guess = 32.0, (math.log(3e10), math.log(7e15), 40.0)
    for it in range(30):
        gU = math.sqrt(4 * math.pi / aU)
        rat = {n: math.sqrt(v) / (MXG * gU) for n, v in m2.items()}
        m = L.Model("C2", gut_r=rat)
        s = m.solve(guess)
        guess = (math.log(s["v_R"]), math.log(s["M_U"]), s["a2R"])
        if abs(s["aU"] - aU) < 1e-10:
            break
        aU = s["aU"]
    cases.append((pt, m, s))

# reference: pure SM running M_Z -> 1e16 (no intermediate scale) for comparison with the literature A_SD ~ 2.2-2.4
def sm_only(chir, MU=1e16):
    m = L.Model("C2")
    a, I = integ(m.segs["sm0"][2], np.array([L.A1I_MZ, L.A2I_MZ, 1 / L.A3_MZ]), math.log(L.MZ), math.log(MU), G_SM[chir])
    return math.exp(I)
out["A_SD_SM_only_to_1e16"] = {ch: sm_only(ch) for ch in ("ec", "e")}
print("SM-only A_SD to 1e16:", out["A_SD_SM_only_to_1e16"])
rows = {}
for name, m, s in cases:
    a_ec, a_e = asd(m, s, "ec"), asd(m, s, "e")
    # channel-weighted A_R^2 (the two chiralities have |C|^2 weights (1+Vud^2)^2 each in sk2_lib.tau_lattice)
    AR2 = A_L ** 2 * 0.5 * (a_ec ** 2 + a_e ** 2)
    corr = 2.726 ** 2 / AR2
    tl = L.tau_lattice(s["M_U"], s["aU"]) * corr
    tr = L.tau_repo(s["M_U"], s["aU"]) * corr
    rows[name] = {"v_R": s["v_R"], "M_U": s["M_U"], "aU": s["aU"], "A_SD_ec": a_ec, "A_SD_e": a_e,
                  "A_R_eff": math.sqrt(AR2), "tau_factor_vs_2.726": corr, "tau_repo_corr": tr, "tau_lat_corr": tl,
                  "tau_lat_uncorr": L.tau_lattice(s["M_U"], s["aU"])}
    print(f"{name:16s} vR={s['v_R']:.3e} MU={s['M_U']:.3e} aU={s['aU']:.2f} A_SD(ec,e)=({a_ec:.3f},{a_e:.3f}) "
          f"A_R_eff={math.sqrt(AR2):.3f} tau x{corr:.3f}: repo {tr:.3e} lat {tl:.3e} (lat uncorr {rows[name]['tau_lat_uncorr']:.3e})")
out["rows"] = rows
json.dump(out, open(os.path.join(HERE, "sk2_asd.json"), "w"), indent=1)
