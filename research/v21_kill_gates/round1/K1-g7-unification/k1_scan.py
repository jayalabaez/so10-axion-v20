#!/usr/bin/env python3
"""K1 main scan: nominal grid, Planck-operator scan (self-consistent), GUT/light threshold Monte Carlo, systematics."""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from k1_lib import M_PL_RED  # noqa: E402
from k1_model import (HEAVY_VECTORS, Chain, Params, heavy_scalars_at_MU, light_thresholds_at_vR,  # noqa: E402
                      proton_lifetime_years, set_yt)

OUT = os.path.join(HERE, "k1_scan.json")
RESUME = os.path.exists(OUT)
S_MAX = 2.9e13   # <S>_max from the dimension-21 quality operator with <Phi17> = 1e17 (k1_axion_quality.py, factor-17 convention)
T0 = time.time()
RES: dict = json.load(open(OUT)) if RESUME else {}


def save():
    with open(OUT, "w") as fh:
        json.dump(RES, fh, indent=1)


def log(msg):
    print(f"[{time.time()-T0:6.0f}s] {msg}", flush=True)


def solve_point(p: Params, guess=None, iters_planck: int = 4, theta: float | None = None, s_sign: int = 1):
    """Solve unification (self-consistent in the Planck eps if theta is given) and return the solution + Landau."""
    try:
        return _solve_point(p, guess, iters_planck, theta, s_sign)
    except Exception as exc:  # fail-soft: a diverging RG run means no perturbative solution
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _solve_point(p: Params, guess, iters_planck, theta, s_sign):
    ch = Chain(p)
    set_yt(ch, 3e13)
    sol = ch.solve() if guess is None else ch.solve(guess)
    if not sol["ok"]:
        return {"ok": False, "sol": {k: sol[k] for k in ("v_R", "M_U", "alpha_U_inv", "resid_max")}}
    set_yt(ch, sol["v_R"])
    sol = ch.solve((math.log(sol["v_R"]), math.log(sol["M_U"]), sol["a2R_inv_vR"]))
    if theta is not None and p.planck_c != 0.0:
        for _ in range(iters_planck):
            g = math.sqrt(4 * math.pi / sol["alpha_U_inv"])
            rho = sol["M_U"] / (g * math.sqrt(math.cos(theta) ** 2 / 2 + math.sin(theta) ** 2))
            pp, aa = rho * math.cos(theta), rho * math.sin(theta)
            K = (-2 * aa, s_sign * 2 * pp, -s_sign * 2 * pp, 4 * aa)  # (SU3, SU2L, SU2R, BL)
            p.planck_eps = tuple(k / M_PL_RED for k in K)
            ch = Chain(p)
            set_yt(ch, sol["v_R"])
            sol = ch.solve((math.log(sol["v_R"]), math.log(sol["M_U"]), sol["a2R_inv_vR"]))
            if not sol["ok"]:
                break
    if not sol["ok"]:
        return {"ok": False, "sol": sol}
    out = {"ok": True, **{k: sol[k] for k in ("v_R", "M_U", "alpha_U_inv", "a2R_inv_vR", "resid_max", "aU_i", "g_vR")}}
    out["M_phi_used"] = max(p.M_phi, sol["M_U"])
    for L in (2, 3):
        lam = ch.landau(sol["M_U"], sol["alpha_U_inv"], loops=L)
        out[f"Lambda_{L}L"] = lam["Lambda"]
        out[f"alpha_inv_MPl_{L}L"] = lam["alpha_inv_MPl"]
    out["Y_lo"] = lam["Y_lo"]
    out["Y_hi"] = lam["Y_hi"]
    out["tau_p_yr"] = proton_lifetime_years(sol["M_U"], sol["alpha_U_inv"])
    out["planck_eps"] = list(p.planck_eps)
    return out


def ys_of(M_s):
    return max(M_s / S_MAX, 0.0)


# ---------------------------------------------------------------------------------------------------------------
# S0: nominal grid (all thresholds at their scales, c = 0).
# ---------------------------------------------------------------------------------------------------------------
S0 = []
for content in (() if "S0_nominal_grid" in RES else ("T2", "T3")):
    for M_s in (3e12, 5e12, 7e12, 1e13, 2e13, 3.6e13):
        for mphi in ("MU", 1e17, 1.25e17, 3.5e17):
            for Y126 in (0.0, 0.5, 1.0):
                p = Params(content=content, loops=3, M_s=M_s, y_s=ys_of(M_s), M_phi=(1e10 if mphi == "MU" else mphi),
                           y_phi=(1.0 if mphi in ("MU", 1e17) else mphi / 1e17), Y126_tr2=Y126**2)
                r = solve_point(p)
                row = {"content": content, "M_s": M_s, "y_s": p.y_s, "M_phi": mphi, "y_phi": p.y_phi, "Y126_33": Y126, **r}
                S0.append(row)
                if Y126 == 0.5:
                    log(f"S0 {content} M_s={M_s:.1e} Mphi={mphi} Y126={Y126}: v_R={r.get('v_R',0):.3e} M_U={r.get('M_U',0):.3e} "
                        f"aU^-1={r.get('alpha_U_inv',0):.3f} L2={r.get('Lambda_2L',0):.3e} L3={r.get('Lambda_3L',0):.3e} "
                        f"ratio3={r.get('Lambda_3L',0)/M_PL_RED:.3f} tau={r.get('tau_p_yr',0):.2e}")
if S0:
    RES["S0_nominal_grid"] = S0
save()

# Yukawa-term on/off and the one-loop solutions for the record
S0b = []
for content in (() if "S0b_loop_and_yukawa_variants" in RES else ("T2", "T3")):
    for loops in (1, 2, 3):
        for yuk in (False, True):
            p = Params(content=content, loops=loops, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, yukawa=yuk, Y126_tr2=0.25)
            r = solve_point(p)
            S0b.append({"content": content, "loops_low": min(loops, 2), "yukawa": yuk, **r})
if S0b:
    RES["S0b_loop_and_yukawa_variants"] = S0b
save()
log("S0 done")

# ---------------------------------------------------------------------------------------------------------------
# S1: Planck gauge-kinetic operator scan at the best nominal points (M_s = 1e13, M_phi = 1e17), self-consistent.
# ---------------------------------------------------------------------------------------------------------------
S1 = []
thetas = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]
for content in ("T2", "T3"):
    for th in thetas:
        for s_sign in (1, -1):
            for direction in (1, -1):
                guess = None
                for k in range(0, 11):
                    c = round(direction * 0.1 * k, 3)
                    if k == 0 and direction == -1:
                        continue
                    p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25, planck_c=c)
                    r = solve_point(p, guess=guess, theta=math.radians(th), s_sign=s_sign)
                    S1.append({"content": content, "theta_deg": th, "s_sign": s_sign, "c": c, **r})
                    if not r["ok"]:
                        break
                    guess = (math.log(r["v_R"]), math.log(r["M_U"]), r["a2R_inv_vR"])
            passing3 = [row["c"] for row in S1 if row["content"] == content and row["theta_deg"] == th and row["s_sign"] == s_sign
                        and row["ok"] and row["Lambda_3L"] > M_PL_RED]
            log(f"S1 {content} theta={th} s={s_sign}: 3L-pass c values = {passing3}")
    RES["S1_planck_scan"] = S1
    save()
# small-c derivative at theta = 45, s = +1
S1d = []
for content in ("T2", "T3"):
    for c in (-0.1, -0.05, 0.0, 0.05, 0.1):
        p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25, planck_c=c)
        r = solve_point(p, theta=math.radians(45), s_sign=1)
        S1d.append({"content": content, "c": c, **r})
RES["S1d_planck_small_c"] = S1d
save()
log("S1 done")

# ---------------------------------------------------------------------------------------------------------------
# S2/S3/S4: threshold Monte Carlo.
# ---------------------------------------------------------------------------------------------------------------
rng = np.random.default_rng(20261016)


def mc(content, n, gut_range, light_range, tag, M_s=1e13, M_phi=1e17):
    heavy_names = [h[0] for h in heavy_scalars_at_MU(content)]
    light_names = [l[0] for l in light_thresholds_at_vR(content)]
    rows = []
    for k in range(n):
        gr = {}
        if gut_range is not None:
            lo, hi = gut_range
            for nm in heavy_names:
                gr[nm] = float(math.exp(rng.uniform(math.log(lo), math.log(hi))))
            v311 = float(math.exp(rng.uniform(math.log(lo), math.log(hi))))
        else:
            v311 = 1.0
        lr = {}
        if light_range is not None:
            lo, hi = light_range
            for nm in light_names:
                lr[nm] = float(math.exp(rng.uniform(math.log(lo), math.log(hi))))
        p = Params(content=content, loops=3, M_s=M_s, y_s=ys_of(M_s), M_phi=M_phi, Y126_tr2=0.25, gut_ratios=gr,
                   light_ratios=lr, v311_ratio=v311)
        r = solve_point(p)
        rows.append({"gut_ratios": gr, "light_ratios": lr, "v311_ratio": v311, **r})
    ok = [r for r in rows if r["ok"]]
    def q(key):
        v = np.array([r[key] for r in ok])
        return {"min": float(v.min()), "p05": float(np.percentile(v, 5)), "p16": float(np.percentile(v, 16)),
                "median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "p95": float(np.percentile(v, 95)),
                "max": float(v.max())}
    summ = {"n": n, "n_ok": len(ok), "gut_range": gut_range, "light_range": light_range,
            "pass_fraction_3L": float(np.mean([r["Lambda_3L"] > M_PL_RED for r in ok])),
            "pass_fraction_2L": float(np.mean([r["Lambda_2L"] > M_PL_RED for r in ok])),
            "Lambda_3L": q("Lambda_3L"), "Lambda_2L": q("Lambda_2L"), "v_R": q("v_R"), "M_U": q("M_U"),
            "alpha_U_inv": q("alpha_U_inv"), "tau_p_yr": q("tau_p_yr")}
    log(f"{tag} {content}: pass3={summ['pass_fraction_3L']:.2f} pass2={summ['pass_fraction_2L']:.2f} "
        f"L3 median={summ['Lambda_3L']['median']:.3e} [{summ['Lambda_3L']['p05']:.2e},{summ['Lambda_3L']['p95']:.2e}] "
        f"v_R median={summ['v_R']['median']:.2e} [{summ['v_R']['min']:.1e},{summ['v_R']['max']:.1e}] M_U median={summ['M_U']['median']:.2e}")
    return {"summary": summ, "rows": rows}


S2, S3, S4, S2u = {}, {}, {}, {}
for content in ("T2", "T3"):
    S2[content] = mc(content, 300, (0.5, 2.0), None, "S2 GUT x1/2..x2")
    RES["S2_gut_threshold_mc"] = S2
    save()
    S2u[content] = mc(content, 200, (0.5, 1.0), None, "S2u GUT x1/2..x1 (unitarity-favoured)")
    RES["S2u_gut_threshold_mc_unitarity_window"] = S2u
    save()
    S3[content] = mc(content, 300, None, (1 / 3, 3.0), "S3 light x1/3..x3")
    RES["S3_light_threshold_mc"] = S3
    save()
    S4[content] = mc(content, 400, (0.5, 2.0), (1 / 3, 3.0), "S4 combined")
    RES["S4_combined_mc"] = S4
    save()
log("MC done")

# Coherent extremes: all heavy scalars x2 / x1/2; all light x3 / x1/3.
S5 = []
for content in ("T2", "T3"):
    heavy_names = [h[0] for h in heavy_scalars_at_MU(content)]
    light_names = [l[0] for l in light_thresholds_at_vR(content)]
    for gf in (0.5, 1.0, 2.0):
        for lf in (1 / 3, 1.0, 3.0):
            p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25,
                       gut_ratios={n: gf for n in heavy_names}, light_ratios={n: lf for n in light_names}, v311_ratio=gf)
            r = solve_point(p)
            S5.append({"content": content, "gut_factor": gf, "light_factor": lf, **r})
            log(f"S5 {content} gut x{gf} light x{lf:.3f}: v_R={r.get('v_R',0):.2e} M_U={r.get('M_U',0):.2e} aU={r.get('alpha_U_inv',0):.2f} L3={r.get('Lambda_3L',0):.3e}")
RES["S5_coherent_extremes"] = S5
save()

# ---------------------------------------------------------------------------------------------------------------
# S6: systematics at the nominal best point.
# ---------------------------------------------------------------------------------------------------------------
S6 = {}
for content in ("T2", "T3"):
    base = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25)
    r0 = solve_point(base)
    d = {"nominal": r0}
    # U(1)_X feedback bound: alpha_X^-1(M_Pl,red) = 1 (U(1)_X at its own alpha = 1 at the cutoff) and = 4 pi
    for ax in (1.0, 4 * math.pi, 10.0):
        p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25, alpha_x_inv_mpl=ax)
        d[f"u1x_feedback_alphaX_inv_MPl={ax:.3g}"] = solve_point(p)
    # b3 scaling (truncation sensitivity)
    ch = Chain(base)
    set_yt(ch, r0["v_R"])
    for f in (0.5, 0.75, 1.25, 1.5):
        lam = ch.landau(r0["M_U"], r0["alpha_U_inv"], loops=3, b3_factor=f)
        d[f"b3_x{f}"] = {"Lambda_3L": lam["Lambda"], "alpha_inv_MPl": lam["alpha_inv_MPl"]}
    # d ln Lambda / d alpha_U^-1 at fixed M_U
    for L in (2, 3):
        lp = ch.landau(r0["M_U"], r0["alpha_U_inv"] + 0.25, loops=L)["Lambda"]
        lm = ch.landau(r0["M_U"], r0["alpha_U_inv"] - 0.25, loops=L)["Lambda"]
        d[f"dlnLambda_dalphaUinv_{L}L"] = (math.log(lp) - math.log(lm)) / 0.5
    # loop-term ratios at M_Pl,red on the 3L trajectory: (b3 a^2/32pi^3)/(b2 a/8pi^2) and 2L/1L
    a_mpl = r0["alpha_inv_MPl_3L"]
    if a_mpl:
        b1, b2, b3 = (float(x) for x in ch.b_so10_hi)
        a = 1 / a_mpl
        d["term_ratio_3L_over_2L_at_MPl"] = (b3 * a * a / (32 * math.pi**3)) / (b2 * a / (8 * math.pi**2))
        d["term_ratio_2L_over_1L_at_MPl"] = (b2 * a / (8 * math.pi**2)) / (b1 / (2 * math.pi))
        d["alpha_inv_MPl_3L"] = a_mpl
    # product-group pure three-loop in the SM/G3221 phases (EST: cross terms omitted)
    p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25, sm_3loop=True)
    d["sm_g3221_pure_3loop"] = solve_point(p)
    # 2HDM below v_R (second doublet light): scheme variation
    p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25, n_doublets_sm=2)
    d["2HDM_below_vR"] = solve_point(p)
    # Phi pair at the unitarity-limited mass 1.25e17 and at 3.5e17 (y_phi = sqrt(4 pi)), and at M_U
    for mphi, yphi in ((1.25e17, 1.25), (3.5e17, 3.5), (1e10, 1.0)):
        p = Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=mphi, y_phi=yphi, Y126_tr2=0.25)
        d[f"Mphi={mphi:.3g}"] = solve_point(p)
    # alpha_s input +-0.0009 and alpha_2^-1 +-0.02 (PDG-like input uncertainty)
    import k1_lib as kl
    for name, dA3 in (("alpha_s+1sig", 1 / 0.1188 - 1 / 0.1179), ("alpha_s-1sig", 1 / 0.1170 - 1 / 0.1179)):
        old = kl.A3_MZ
        kl.A3_MZ = old + dA3
        import k1_model as km
        km.A3_MZ = kl.A3_MZ
        d[name] = solve_point(Params(content=content, loops=3, M_s=1e13, y_s=ys_of(1e13), M_phi=1e17, Y126_tr2=0.25))
        kl.A3_MZ = old
        km.A3_MZ = old
    S6[content] = d
    RES["S6_systematics"] = S6
    save()
    log(f"S6 {content}: " + ", ".join(f"{k}: L3={v.get('Lambda_3L', 0):.3e}" for k, v in d.items() if isinstance(v, dict) and "Lambda_3L" in v))

# ---------------------------------------------------------------------------------------------------------------
# S7: M_s scan with y_s at the quality minimum and at fixed y_s values (axion band link), T2 and T3.
# ---------------------------------------------------------------------------------------------------------------
S7 = []
for content in ("T2", "T3"):
    for M_s in np.geomspace(3e12, 3.6e13, 12):
        for mphi in (1e17, 1.25e17):
            p = Params(content=content, loops=3, M_s=float(M_s), y_s=ys_of(M_s), M_phi=mphi, y_phi=mphi / 1e17, Y126_tr2=0.25)
            r = solve_point(p)
            S7.append({"content": content, "M_s": float(M_s), "y_s_min_quality": p.y_s, "M_phi": mphi, **r})
RES["S7_Ms_scan"] = S7
save()
log("all done")
