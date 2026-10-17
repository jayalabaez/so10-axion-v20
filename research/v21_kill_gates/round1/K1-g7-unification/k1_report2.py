#!/usr/bin/env python3
"""Generate REPORT_part2.txt (results tables) from k1_summary.json, k1_scan.json and k1_scan_bottom.json."""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
M_PL = 2.435e18
S = json.load(open(os.path.join(HERE, "k1_summary.json")))
B = json.load(open(os.path.join(HERE, "k1_scan_bottom.json"))) if os.path.exists(os.path.join(HERE, "k1_scan_bottom.json")) else {}
L = []
P = L.append

P("6. Unification solutions and Landau scales, nominal thresholds, c = 0 [NUM]")
P("-" * 78)
P("(all tuned multiplets at v_R, all heavy scalars and vectors at M_U, Y126_33 = 0.5, Y10_33 = y_t(M_U), y_s = M_s/<S>_max,")
P(" y_phi = M_phi/1e17; 'M_U' in the M_phi column = Phi pair at M_U)")
P(f"{'cont':5s} {'M_s':>8s} {'y_s':>6s} {'M_phi':>8s} {'v_R':>10s} {'M_U':>10s} {'aU^-1':>7s} {'L2/MPl':>7s} {'L3/MPl':>7s} {'tau_p[yr]':>10s}")
for r in S["S0"]:
    mphi = "M_U" if r["M_phi"] == "MU" else f"{r['M_phi']:.3g}"
    P(f"{r['content']:5s} {r['M_s']:8.1e} {r['y_s']:6.3f} {mphi:>8s} {r['v_R']:10.3e} {r['M_U']:10.3e} {r['alpha_U_inv']:7.3f} "
      f"{r['Lambda_2L']/M_PL:7.3f} {r['Lambda_3L']/M_PL:7.3f} {r['tau_p_yr']:10.2e}")
P("")
P("One-loop solutions (independent of the S-sector mass, EXACT universality): T2 v_R = 1.406e13, M_U = 4.631e16,")
P("alpha_U^-1 = 26.58 (M_s = 1e13); T3 v_R = 1.648e13, M_U = 6.533e16, alpha_U^-1 = 25.63.  Two-loop (gauge-only,")
P("Yukawa terms off) reproduces the critic's C4 table to 3-4 digits (k1_first_run.log): T2 at M_s = 5e12: v_R 2.597e13,")
P("M_U 2.131e16, alpha_U^-1 25.908, Lambda_2L 3.147e18 / 4.016e18 (Phi at M_U / 1e17), Lambda_3L 1.449e18; T3: 3.084e13,")
P("3.047e16, 24.924, 3.271e18 / 3.937e18, 1.541e18; the three-loop point M_s = 1e13, Phi at 1e17: 2.501e18 (+2.7%).")
P("Yukawa two-loop terms (y_t, y_s, y_phi, Y10, Y126): +1.5% (Y126_33 = 0) to +3.7% (Y126_33 = 1) on Lambda_3L.")
y = S.get("Y126_effect", {})
for k, v in y.items():
    P(f"   {k}: Lambda_2L = {v['Lambda_2L']:.4e}, Lambda_3L = {v['Lambda_3L']:.4e} (Y_SO10 above M_phi = {v['Y_hi']:.2f})")
P("")
if "S7" in S:
    P("M_s scan (y_s at the quality minimum, c = 0): Lambda_3L crosses M_Pl,red at")
    for k, v in S.items():
        if k.startswith("S7_Ms_crossing"):
            P(f"   {k}: M_s = {v:.3e}" if v else f"   {k}: no crossing")
    P("")

P("7. Planck gauge-kinetic operator scan [NUM; exact Clebsches of section 3], M_s = 1e13, Phi at 1e17")
P("-" * 78)
P("Self-consistent re-solve of (v_R, M_U, alpha_2R^-1) with alpha_i^-1(M_U) = alpha_U^-1 (1 + c K_i/M_Pl,red),")
P("K = (-2a, s 2p, -s 2p, 4a) for (SU3, SU2L, SU2R, B-L), (p, a) = rho (cos th, sin th), rho from M_U; th in 15..165 deg,")
P("s = +-1, c in [-1, 1] by continuation from c = 0 (the continuation stops where no perturbative solution exists).")
P("'physical' = v_R in [8e12, 1e14] and M_U <= 1e17 (outside this the 'solutions' have M_U up to 6e19 or v_R ~ 1e10).")
for content in ("T2", "T3"):
    k2 = S.get(f"{content}_S1_two_loop")
    pa = S.get(f"{content}_S1_physical_acceptance")
    if not k2:
        continue
    P(f"{content}: three-loop pass for ALL (th, s) at c in {S.get(content + '_c_pass_all_directions')}; pass for SOME at {S.get(content + '_c_pass_some_direction')}")
    P(f"{content}: physical solutions for ALL directions at c in {pa['c_physical_for_all_directions']}; three-loop pass AND physical for ALL directions: "
      f"{pa['c_3Lpass_physical_all_directions']}; three-loop FAIL (physical) for SOME direction: {pa['c_3Lfail_physical_some_direction']}")
    P(f"{content}: two-loop: min Lambda_2L/M_Pl over all solved points = {k2['min_Lambda2_over_MPl']:.3f}; two-loop failures: {k2['two_loop_fail_points']}; "
      f"v_R range {k2['v_R_range'][0]:.2e}-{k2['v_R_range'][1]:.2e}, M_U range {k2['M_U_range'][0]:.2e}-{k2['M_U_range'][1]:.2e}, "
      f"alpha_U^-1 range {k2['alphaU_inv_range'][0]:.2f}-{k2['alphaU_inv_range'][1]:.2f}; solved {k2['n_solved']}/{k2['n_total']}")
    for key, v in S["S1"].items():
        if key.startswith(content):
            lam = v["Lambda3_over_MPl_at_c"]
            P(f"   {key:16s}: pass c {v['pass_c'][:1]}..{v['pass_c'][-1:]} (n={len(v['pass_c'])}); L3/MPl(c=-0.3,-0.2,-0.1,0,0.1,0.2,0.3) = "
              + str([lam.get(str(c), None) for c in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3)]) + f"; no-solution c: {v['no_solution_c']}")
if "S1d" in S:
    P("Small-c derivative (th = 45 deg, s = +1):")
    for r in S["S1d"]:
        if r["ok"]:
            P(f"   {r['content']} c = {r['c']:+.2f}: v_R = {r['v_R']:.3e}, M_U = {r['M_U']:.3e}, alpha_U^-1 = {r['alpha_U_inv']:.3f}, "
              f"L2/MPl = {r['Lambda_2L']/M_PL:.3f}, L3/MPl = {r['Lambda_3L']/M_PL:.3f}, eps_i per unit c = {[round(e, 4) for e in r['planck_eps']]}")
P("")

P("8. Threshold Monte Carlo [NUM], M_s = 1e13, Phi at 1e17, c = 0 (log-uniform ratios, every multiplet independent)")
P("-" * 78)
for sec, lab in (("S2_gut_threshold_mc", "GUT scalars x1/2..x2 (+ (3,1,1) vector)"), ("S2u_gut_threshold_mc_unitarity_window", "GUT scalars x1/2..x1 (unitarity-favoured half)"),
                 ("S3_light_threshold_mc", "light multiplets at v_R x1/3..x3 (incl. W_R)"), ("S4_combined_mc", "both combined")):
    if sec not in S:
        continue
    P(f"{lab}:")
    for content, sm in S[sec].items():
        P(f"   {content}: n = {sm['n_ok']}/{sm['n']}; pass fraction 3L = {sm['pass_fraction_3L']:.2f}, 2L = {sm['pass_fraction_2L']:.2f}; "
          f"L3/MPl min/p05/med/p95/max = {sm['Lambda_3L']['min']/M_PL:.3f}/{sm['Lambda_3L']['p05']/M_PL:.3f}/{sm['Lambda_3L']['median']/M_PL:.3f}/{sm['Lambda_3L']['p95']/M_PL:.3f}/{sm['Lambda_3L']['max']/M_PL:.3f}; "
          f"L2/MPl min/med/max = {sm['Lambda_2L']['min']/M_PL:.3f}/{sm['Lambda_2L']['median']/M_PL:.3f}/{sm['Lambda_2L']['max']/M_PL:.3f}")
        P(f"        v_R min/med/max = {sm['v_R']['min']:.2e}/{sm['v_R']['median']:.2e}/{sm['v_R']['max']:.2e}; M_U = {sm['M_U']['min']:.2e}/{sm['M_U']['median']:.2e}/{sm['M_U']['max']:.2e}; "
          f"alpha_U^-1 = {sm['alpha_U_inv']['min']:.2f}/{sm['alpha_U_inv']['median']:.2f}/{sm['alpha_U_inv']['max']:.2f}; tau_p min/med = {sm['tau_p_yr']['min']:.2e}/{sm['tau_p_yr']['median']:.2e} yr")
        if "top_correlations_lnLambda3_vs_ln_r" in sm:
            P(f"        strongest correlations of ln Lambda_3L with ln(M_k/scale): {[(k, round(v, 2)) for k, v in sm['top_correlations_lnLambda3_vs_ln_r']]}")
if "S5" in S:
    P("Coherent extremes (all heavy scalars x f_GUT, all light states x f_light):")
    for r in S["S5"]:
        P(f"   {r['content']} GUT x{r['gut_factor']:<4} light x{r['light_factor']:<5.3f}: v_R = {r['v_R']:.3e}, M_U = {r['M_U']:.3e}, alpha_U^-1 = {r['alpha_U_inv']:.3f}, "
          f"L2/MPl = {r['Lambda_2L']/M_PL:.3f}, L3/MPl = {r['Lambda_3L']/M_PL:.3f}, tau_p = {r['tau_p_yr']:.2e}")
MID = json.load(open(os.path.join(HERE, "k1_scan_mid.json"))) if os.path.exists(os.path.join(HERE, "k1_scan_mid.json")) else {}
if B or MID:
    P("Bottom and middle of the window (combined GUT x1/2..x2 and light x1/3..x3 thresholds; 150 / 100 samples):")
    for k, v in list(B.items()) + list(MID.items()):
        P(f"   {k}: pass2 = {v['pass2']:.2f}, pass3 = {v['pass3']:.2f}; L2/MPl min/p05/med/p95/max = {[round(x, 3) for x in v['L2_min_p05_med_p95_max']]}; "
          f"L3/MPl min/med/max = {[round(x, 3) for x in v['L3_min_med_max']]}; v_R min/med/max = {[f'{x:.2e}' for x in v['v_R_min_med_max']]}; tau_p min/med = {[f'{x:.2e}' for x in v['tau_min_med']]}")
P("")

P("9. Systematics at M_s = 1e13, Phi at 1e17, c = 0 [NUM / EST]")
P("-" * 78)
if "S6" in S:
    for content, blk in S["S6"].items():
        P(f"{content}:")
        for k, v in blk.items():
            if isinstance(v, dict):
                extra = f"; v_R = {v['v_R']:.3e}, M_U = {v['M_U']:.3e}, alpha_U^-1 = {v['alpha_U_inv']:.3f}" if "v_R" in v else ""
                P(f"   {k:42s}: L3/MPl = {v['Lambda_3L']/M_PL:.4f}" + (f", L2/MPl = {v['Lambda_2L']/M_PL:.4f}" if "Lambda_2L" in v else "") + extra)
            else:
                P(f"   {k:42s}: {v}")
P("")
open(os.path.join(HERE, "REPORT_part2.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
