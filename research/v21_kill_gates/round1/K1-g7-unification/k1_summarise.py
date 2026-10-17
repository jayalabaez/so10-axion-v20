#!/usr/bin/env python3
"""Summarise k1_scan.json into the K1 tables (prints text; writes k1_summary.json)."""
from __future__ import annotations

import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
M_PL = 2.435e18
d = json.load(open(os.path.join(HERE, "k1_scan.json")))
summary = {}

print("=== S0 nominal grid (c = 0, all thresholds at scale; Y126_33 = 0.5) ===")
print(f"{'content':8s} {'M_s':>8s} {'y_s':>6s} {'M_phi':>8s} {'v_R':>10s} {'M_U':>10s} {'aU^-1':>7s} {'L2/MPl':>7s} {'L3/MPl':>7s} {'tau_p':>9s}")
s0 = []
for r in d.get("S0_nominal_grid", []):
    if r["Y126_33"] != 0.5 or not r["ok"]:
        continue
    mphi = r["M_phi"] if r["M_phi"] != "MU" else "M_U"
    print(f"{r['content']:8s} {r['M_s']:8.1e} {r['y_s']:6.3f} {str(mphi):>8s} {r['v_R']:10.3e} {r['M_U']:10.3e} {r['alpha_U_inv']:7.3f} "
          f"{r['Lambda_2L']/M_PL:7.3f} {r['Lambda_3L']/M_PL:7.3f} {r['tau_p_yr']:9.2e}")
    s0.append({k: r[k] for k in ("content", "M_s", "y_s", "M_phi", "v_R", "M_U", "alpha_U_inv", "Lambda_2L", "Lambda_3L", "tau_p_yr")})
summary["S0"] = s0
# Y126 effect
y126 = {}
for r in d.get("S0_nominal_grid", []):
    if r["M_s"] == 1e13 and r["M_phi"] == 1e17 and r["ok"]:
        y126[f"{r['content']}_Y126={r['Y126_33']}"] = {"Lambda_3L": r["Lambda_3L"], "Lambda_2L": r["Lambda_2L"], "Y_hi": r["Y_hi"]}
summary["Y126_effect"] = y126
print("Y126 effect:", json.dumps(y126, indent=0))

print("\n=== S1 Planck gauge-kinetic operator: c range with Lambda_3L > M_Pl,red (continuation from c = 0) ===")
s1 = {}
rows = d.get("S1_planck_scan", [])
for content in ("T2", "T3"):
    for th in sorted(set(r["theta_deg"] for r in rows if r["content"] == content)):
        for s in (1, -1):
            sub = [r for r in rows if r["content"] == content and r["theta_deg"] == th and r["s_sign"] == s]
            ok = [r for r in sub if r["ok"]]
            pas = sorted(r["c"] for r in ok if r["Lambda_3L"] > M_PL)
            fail = sorted(r["c"] for r in ok if r["Lambda_3L"] <= M_PL)
            nosol = sorted(r["c"] for r in sub if not r["ok"])
            # extremes
            lam = {r["c"]: r["Lambda_3L"] / M_PL for r in ok}
            vr = {r["c"]: r["v_R"] for r in ok}
            mu = {r["c"]: r["M_U"] for r in ok}
            au = {r["c"]: r["alpha_U_inv"] for r in ok}
            key = f"{content}_theta{th}_s{s:+d}"
            s1[key] = {"pass_c": pas, "fail_c": fail, "no_solution_c": nosol,
                       "Lambda3_over_MPl_at_c": {str(c): round(v, 3) for c, v in sorted(lam.items())},
                       "v_R_at_c": {str(c): vr[c] for c in sorted(vr)}, "M_U_at_c": {str(c): mu[c] for c in sorted(mu)},
                       "alphaU_inv_at_c": {str(c): au[c] for c in sorted(au)}}
            cmin = min(pas) if pas else None
            cmax = max(pas) if pas else None
            print(f"{content} theta={th:3d} s={s:+d}: pass c in [{cmin}, {cmax}] (n_pass={len(pas)}/{len(ok)} solved; no-solution c: {nosol}); "
                  f"L3/MPl at c=-1,-0.5,0,0.5,1 = {[round(lam.get(c, float('nan')), 3) for c in (-1.0, -0.5, 0.0, 0.5, 1.0)]}; "
                  f"v_R at c=+-1: {vr.get(-1.0, float('nan')):.2e}, {vr.get(1.0, float('nan')):.2e}; aU^-1 at c=+-1: {au.get(-1.0, float('nan')):.2f}, {au.get(1.0, float('nan')):.2f}")
summary["S1"] = s1
# per-content: c-interval that passes for ALL directions (robust) and for SOME direction
for content in ("T2", "T3"):
    keys = [k for k in s1 if k.startswith(content)]
    if not keys:
        continue
    allc = [round(x, 1) for x in np.linspace(-1, 1, 21)]
    robust = [c for c in allc if all(c in s1[k]["pass_c"] for k in keys)]
    some = [c for c in allc if any(c in s1[k]["pass_c"] for k in keys)]
    summary[f"{content}_c_pass_all_directions"] = robust
    summary[f"{content}_c_pass_some_direction"] = some
    print(f"{content}: c passing for ALL (theta, s): {robust}; for SOME: {some}")
    okrows = [r for r in rows if r["content"] == content and r["ok"]]
    # physical acceptance: v_R within [8e12, 1e14] (seesaw window x3 around 2.5-3.4e13), M_U <= 1e17 (M_U/M_Pl < 0.04)
    def phys(r):
        return 8e12 <= r["v_R"] <= 1e14 and r["M_U"] <= 1e17
    acc = {}
    for th in sorted(set(r["theta_deg"] for r in okrows)):
        for sg in (1, -1):
            sub = [r for r in okrows if r["theta_deg"] == th and r["s_sign"] == sg]
            cs_phys = sorted(r["c"] for r in sub if phys(r))
            cs_phys_pass = sorted(r["c"] for r in sub if phys(r) and r["Lambda_3L"] > M_PL)
            cs_phys_fail = sorted(r["c"] for r in sub if phys(r) and r["Lambda_3L"] <= M_PL)
            acc[f"theta{th}_s{sg:+d}"] = {"c_physical": [min(cs_phys), max(cs_phys)] if cs_phys else None,
                                         "c_physical_and_3Lpass": cs_phys_pass, "c_physical_and_3Lfail": cs_phys_fail}
    allc = [round(x, 1) for x in np.linspace(-1, 1, 21)]
    phys_all = [c for c in allc if all(c in v["c_physical_and_3Lpass"] or c in v["c_physical_and_3Lfail"] for v in acc.values())]
    pass_all_phys = [c for c in allc if all(c in v["c_physical_and_3Lpass"] for v in acc.values())]
    fail_any_phys = [c for c in allc if any(c in v["c_physical_and_3Lfail"] for v in acc.values())]
    summary[f"{content}_S1_physical_acceptance"] = {"per_direction": acc, "c_physical_for_all_directions": phys_all,
                                                     "c_3Lpass_physical_all_directions": pass_all_phys, "c_3Lfail_physical_some_direction": fail_any_phys}
    print(f"{content}: c physical (v_R in [8e12,1e14], M_U <= 1e17) for ALL directions: {phys_all}; 3L pass AND physical for ALL directions: {pass_all_phys}; "
          f"3L fail (physical) for SOME direction: {fail_any_phys}")
    for k, v in acc.items():
        print(f"   {k}: physical c in {v['c_physical']}; pass {v['c_physical_and_3Lpass']}; fail {v['c_physical_and_3Lfail']}")
    l2min = min(r["Lambda_2L"] for r in okrows) / M_PL
    l2fail = sorted(set((r["theta_deg"], r["s_sign"], r["c"]) for r in okrows if r["Lambda_2L"] <= M_PL))
    nosol = sorted(set((r["theta_deg"], r["s_sign"], r["c"]) for r in rows if r["content"] == content and not r["ok"]))
    vr = [r["v_R"] for r in okrows]; mu = [r["M_U"] for r in okrows]; au = [r["alpha_U_inv"] for r in okrows]
    summary[f"{content}_S1_two_loop"] = {"min_Lambda2_over_MPl": l2min, "two_loop_fail_points": l2fail, "no_solution_points": nosol,
                                         "v_R_range": [min(vr), max(vr)], "M_U_range": [min(mu), max(mu)], "alphaU_inv_range": [min(au), max(au)],
                                         "n_solved": len(okrows), "n_total": len([r for r in rows if r["content"] == content])}
    print(f"{content}: two-loop: min Lambda_2L/MPl over the whole c-scan = {l2min:.3f}; 2L-fail points: {l2fail}; "
          f"no-solution points (continuation stopped): {nosol}; v_R range {min(vr):.2e}-{max(vr):.2e}, M_U range {min(mu):.2e}-{max(mu):.2e}, aU^-1 range {min(au):.2f}-{max(au):.2f}")
if "S1d_planck_small_c" in d:
    print("small-c derivative (theta=45, s=+1):")
    for r in d["S1d_planck_small_c"]:
        if r["ok"]:
            print(f"  {r['content']} c={r['c']:+.2f}: v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU^-1={r['alpha_U_inv']:.3f} L3/MPl={r['Lambda_3L']/M_PL:.3f} eps={[round(e, 4) for e in r['planck_eps']]}")
    summary["S1d"] = d["S1d_planck_small_c"]

for sec, lab in (("S2_gut_threshold_mc", "GUT scalars x1/2..x2"), ("S2u_gut_threshold_mc_unitarity_window", "GUT scalars x1/2..x1"),
                 ("S3_light_threshold_mc", "light x1/3..x3"), ("S4_combined_mc", "combined")):
    if sec not in d:
        continue
    print(f"\n=== {sec} ({lab}) ===")
    summary[sec] = {}
    for content, blk in d[sec].items():
        sm = blk["summary"]
        summary[sec][content] = sm
        print(f"{content}: n_ok={sm['n_ok']}/{sm['n']} pass3={sm['pass_fraction_3L']:.3f} pass2={sm['pass_fraction_2L']:.3f} "
              f"L3/MPl min/p05/med/p95/max = {sm['Lambda_3L']['min']/M_PL:.3f}/{sm['Lambda_3L']['p05']/M_PL:.3f}/{sm['Lambda_3L']['median']/M_PL:.3f}/"
              f"{sm['Lambda_3L']['p95']/M_PL:.3f}/{sm['Lambda_3L']['max']/M_PL:.3f}; L2/MPl min/med/max = {sm['Lambda_2L']['min']/M_PL:.3f}/"
              f"{sm['Lambda_2L']['median']/M_PL:.3f}/{sm['Lambda_2L']['max']/M_PL:.3f}; v_R min/med/max = {sm['v_R']['min']:.2e}/{sm['v_R']['median']:.2e}/{sm['v_R']['max']:.2e}; "
              f"M_U min/med/max = {sm['M_U']['min']:.2e}/{sm['M_U']['median']:.2e}/{sm['M_U']['max']:.2e}; aU^-1 min/med/max = {sm['alpha_U_inv']['min']:.2f}/"
              f"{sm['alpha_U_inv']['median']:.2f}/{sm['alpha_U_inv']['max']:.2f}; tau_p min/med = {sm['tau_p_yr']['min']:.2e}/{sm['tau_p_yr']['median']:.2e}")
        # which thresholds matter most: correlation of ln Lambda_3L with ln r_k
        rows = [r for r in blk["rows"] if r["ok"]]
        if rows and (rows[0]["gut_ratios"] or rows[0]["light_ratios"]):
            y = np.array([math.log(r["Lambda_3L"]) for r in rows])
            corr = {}
            for nm in list(rows[0]["gut_ratios"].keys()) + list(rows[0]["light_ratios"].keys()) + ["v311"]:
                if nm == "v311":
                    x = np.array([math.log(r["v311_ratio"]) for r in rows])
                else:
                    x = np.array([math.log(r["gut_ratios"].get(nm, r["light_ratios"].get(nm, 1.0))) for r in rows])
                if np.std(x) > 0:
                    corr[nm] = float(np.corrcoef(x, y)[0, 1])
            top = sorted(corr.items(), key=lambda kv: -abs(kv[1]))[:6]
            summary[sec][content]["top_correlations_lnLambda3_vs_ln_r"] = top
            print("   strongest threshold correlations with ln Lambda_3L:", [(k, round(v, 2)) for k, v in top])

if "S5_coherent_extremes" in d:
    print("\n=== S5 coherent extremes (M_s = 1e13, Phi at 1e17) ===")
    summary["S5"] = []
    for r in d["S5_coherent_extremes"]:
        if r["ok"]:
            print(f"{r['content']} GUT x{r['gut_factor']:<4} light x{r['light_factor']:<5.3f}: v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU^-1={r['alpha_U_inv']:.3f} "
                  f"L2/MPl={r['Lambda_2L']/M_PL:.3f} L3/MPl={r['Lambda_3L']/M_PL:.3f} tau_p={r['tau_p_yr']:.2e}")
            summary["S5"].append({k: r[k] for k in ("content", "gut_factor", "light_factor", "v_R", "M_U", "alpha_U_inv", "Lambda_2L", "Lambda_3L", "tau_p_yr")})
        else:
            print(f"{r['content']} GUT x{r['gut_factor']} light x{r['light_factor']:.3f}: NO SOLUTION")

if "S6_systematics" in d:
    print("\n=== S6 systematics (M_s = 1e13, Phi at 1e17, c = 0) ===")
    summary["S6"] = {}
    for content, blk in d["S6_systematics"].items():
        summary["S6"][content] = {}
        for k, v in blk.items():
            if isinstance(v, dict) and "Lambda_3L" in v:
                extra = f" v_R={v['v_R']:.3e} M_U={v['M_U']:.3e} aU^-1={v['alpha_U_inv']:.3f}" if "v_R" in v else ""
                print(f"{content} {k:40s}: L3/MPl={v['Lambda_3L']/M_PL:.4f}" + (f" L2/MPl={v['Lambda_2L']/M_PL:.4f}" if "Lambda_2L" in v else "") + extra)
                summary["S6"][content][k] = {kk: v[kk] for kk in v if kk in ("Lambda_3L", "Lambda_2L", "v_R", "M_U", "alpha_U_inv", "alpha_inv_MPl")}
            elif not isinstance(v, dict):
                print(f"{content} {k:40s}: {v}")
                summary["S6"][content][k] = v

if "S7_Ms_scan" in d:
    print("\n=== S7 M_s scan (y_s at the quality minimum, c = 0) ===")
    summary["S7"] = []
    for r in d["S7_Ms_scan"]:
        if r["ok"]:
            print(f"{r['content']} M_s={r['M_s']:.2e} y_s_min={r['y_s_min_quality']:.3f} Mphi={r['M_phi']:.3g}: v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU^-1={r['alpha_U_inv']:.3f} L2/MPl={r['Lambda_2L']/M_PL:.3f} L3/MPl={r['Lambda_3L']/M_PL:.3f}")
            summary["S7"].append({k: r[k] for k in ("content", "M_s", "y_s_min_quality", "M_phi", "v_R", "M_U", "alpha_U_inv", "Lambda_2L", "Lambda_3L")})
    # threshold M_s where L3 = M_Pl (interpolate) per content and M_phi
    for content in ("T2", "T3"):
        for mphi in (1e17, 1.25e17):
            pts = sorted([(r["M_s"], r["Lambda_3L"] / M_PL) for r in d["S7_Ms_scan"] if r["ok"] and r["content"] == content and r["M_phi"] == mphi])
            cross = None
            for (m1, l1), (m2, l2) in zip(pts, pts[1:]):
                if (l1 - 1) * (l2 - 1) < 0:
                    f = (1 - l1) / (l2 - l1)
                    cross = math.exp(math.log(m1) + f * (math.log(m2) - math.log(m1)))
            summary[f"S7_Ms_crossing_{content}_Mphi={mphi:.3g}"] = cross
            print(f"{content} Mphi={mphi:.3g}: Lambda_3L = M_Pl,red at M_s = {cross}")

with open(os.path.join(HERE, "k1_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=1, default=float)
