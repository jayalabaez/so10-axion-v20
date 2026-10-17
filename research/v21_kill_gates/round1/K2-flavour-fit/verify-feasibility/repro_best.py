"""Verifier: reproduce the researcher's best point (proxy and full-RG chi2), recompute the doublet composition
with the correct normalisation |c_d10|^2 (1+|r|^2) + |c_d126|^2 (1+|rs|^2) = 1, and the actual max|Y10_act|."""
import json, math, time, numpy as np, fit
inp = json.load(open("inputs_mz.json"))
t0 = time.time()
R = fit.Runner(inp, 2.6e13, 2.13e16, "T2"); T = fit.build_targets(inp, 0.01)
P = fit.Proxy2(R, T, type2=False)
print("runner+proxy init %.1fs" % (time.time() - t0))
# proxy chi2 at the DE point
w = json.load(open("de_I_0.json")); x = np.array(w["x"])
t0 = time.time(); res, obs, pl, extra = P.residuals(x, full=False, log_masses=False); dt = time.time() - t0
print("proxy eval time %.4fs" % dt)
print("proxy chi2 (recomputed) = %.3f  (stored %.3f)" % (np.sum(res[:18]**2), w["chi2"]))
# full chi2 at the refit point
s2 = json.load(open("s2_de_I_0.json"))["results"][0]; x2 = np.array(s2["x"])
t0 = time.time(); res2, obs2, pl2, extra2 = P.residuals(x2, full=True, log_masses=False); dt = time.time() - t0
print("full eval time %.2fs" % dt)
print("full chi2 (recomputed) = %.3f  (stored %.3f)" % (np.sum(res2[:18]**2), s2["chi2"]))
print("pulls:", {k: round(v, 2) for k, v in pl2.items()})
# composition, researcher's vs corrected
Yu, Yd, Ye, Yn, MR, ML, Hm, F, r, s, cd126 = P.matrices(x2)
rs = r * s
rem = 1 - cd126**2 * (1 + abs(rs)**2)
cd10_res = math.sqrt(rem)                       # researcher's code
cd10_cor = math.sqrt(rem / (1 + abs(r)**2))     # correct normalisation
for lab, cd10 in [("researcher", cd10_res), ("corrected", cd10_cor)]:
    cu10 = r * cd10; cu126 = rs * cd126
    Y10 = Hm / cd10; Y126 = F / cd126
    print(f"[{lab}] c_u10={abs(cu10):.4f} c_u126={abs(cu126):.4f} c_d10={cd10:.5f} c_d126={cd126:.5f} sum|c|^2={abs(cu10)**2+abs(cu126)**2+cd10**2+cd126**2:.4f}"
          f"  max|Y10_act|={np.abs(Y10*fit.N10_ACT).max():.4f} max|Y126_act|={np.abs(Y126*fit.N126_ACT).max():.4f}")
print("|r|=%.2f arg r=%.3f |s|=%.3f arg s=%.3f  -> c_u126/c_u10 = %.3f  c_d126/c_d10 = %.3f  (equal iff s=1)" %
      (abs(r), np.angle(r), abs(s), np.angle(s), abs(rs*cd126/(r*cd10_cor)), cd126/cd10_cor))
# the T2 (single G3221 bidoublet) structural constraint: s = 1 exactly => Yu = r Yd. Evaluate the chi2 with s forced to 1
x_s1 = x2.copy(); x_s1[14] = 1.0; x_s1[15] = 0.0
res3, obs3, pl3, _ = P.residuals(x_s1, full=False, log_masses=False)
print("s=1 forced (T2-realisable): proxy chi2 = %.3g ; CKM s12=%.3g s23=%.3g s13=%.3g ; m_t/m_b=%.3g m_c/m_s=%.3g m_u/m_d=%.3g" %
      (np.sum(res3[:18]**2), obs3["s12"], obs3["s23"], obs3["s13"], obs3["m_t"]/obs3["m_b"], obs3["m_c"]/obs3["m_s"], obs3["m_u"]/obs3["m_d"]))
json.dump({"proxy_chi2_recomputed": float(np.sum(res[:18]**2)), "full_chi2_recomputed": float(np.sum(res2[:18]**2)),
           "pulls_full": {k: float(v) for k, v in pl2.items()},
           "composition_corrected": {"c_u10": abs(r*cd10_cor), "c_u126": abs(rs*cd126), "c_d10": cd10_cor, "c_d126": cd126,
                                     "Y10_act_max": float(np.abs(Hm/cd10_cor*fit.N10_ACT).max()), "Y126_act_max": float(np.abs(F/cd126*fit.N126_ACT).max())},
           "composition_researcher": {"c_u10": abs(r*cd10_res), "c_d10": cd10_res, "Y10_act_max": float(np.abs(Hm/cd10_res*fit.N10_ACT).max())},
           "s_forced_1_proxy_chi2": float(np.sum(res3[:18]**2))}, open("repro_best.json", "w"), indent=1)
