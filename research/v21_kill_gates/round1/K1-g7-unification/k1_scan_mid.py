#!/usr/bin/env python3
"""Two-loop robustness at the bottom of the M_s window (M_s = 3e12): combined threshold Monte Carlo, Phi pair at M_U and 1e17."""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from k1_lib import M_PL_RED
from k1_model import Chain, Params, heavy_scalars_at_MU, light_thresholds_at_vR, proton_lifetime_years, set_yt
S_MAX = 2.9e13
rng = np.random.default_rng(11)
def solve_point(p):
    try:
        ch = Chain(p); set_yt(ch, 3e13); sol = ch.solve()
        if not sol["ok"]: return {"ok": False}
        set_yt(ch, sol["v_R"]); sol = ch.solve((math.log(sol["v_R"]), math.log(sol["M_U"]), sol["a2R_inv_vR"]))
        if not sol["ok"]: return {"ok": False}
        out = {"ok": True, "v_R": sol["v_R"], "M_U": sol["M_U"], "alpha_U_inv": sol["alpha_U_inv"]}
        for L in (2, 3):
            out[f"Lambda_{L}L"] = ch.landau(sol["M_U"], sol["alpha_U_inv"], loops=L)["Lambda"]
        out["tau_p_yr"] = proton_lifetime_years(sol["M_U"], sol["alpha_U_inv"]); return out
    except Exception as e:
        return {"ok": False, "error": str(e)}
RES = {}
t0 = time.time()
for content in ("T2", "T3"):
    for M_S in (5e12, 7e12):
        heavy = [h[0] for h in heavy_scalars_at_MU(content)]; light = [l[0] for l in light_thresholds_at_vR(content)]
        rows = []
        for k in range(100):
            gr = {n: float(math.exp(rng.uniform(math.log(0.5), math.log(2)))) for n in heavy}
            lr = {n: float(math.exp(rng.uniform(math.log(1/3), math.log(3)))) for n in light}
            v311 = float(math.exp(rng.uniform(math.log(0.5), math.log(2))))
            p = Params(content=content, loops=3, M_s=M_S, y_s=M_S / S_MAX, M_phi=1e17, Y126_tr2=0.25, gut_ratios=gr, light_ratios=lr, v311_ratio=v311)
            rows.append(solve_point(p))
        ok = [r for r in rows if r["ok"]]
        l2 = np.array([r["Lambda_2L"] for r in ok]) / M_PL_RED; l3 = np.array([r["Lambda_3L"] for r in ok]) / M_PL_RED
        vr = np.array([r["v_R"] for r in ok]); tau = np.array([r["tau_p_yr"] for r in ok])
        key = f"{content}_Ms={M_S:.0e}_Mphi=1e17"
        RES[key] = {"n_ok": len(ok), "pass2": float(np.mean(l2 > 1)), "pass3": float(np.mean(l3 > 1)),
                    "L2_min_p05_med_p95_max": [float(l2.min()), float(np.percentile(l2, 5)), float(np.median(l2)), float(np.percentile(l2, 95)), float(l2.max())],
                    "L3_min_med_max": [float(l3.min()), float(np.median(l3)), float(l3.max())],
                    "v_R_min_med_max": [float(vr.min()), float(np.median(vr)), float(vr.max())], "tau_min_med": [float(tau.min()), float(np.median(tau))]}
        print(f"[{time.time()-t0:.0f}s] {key}: {RES[key]}", flush=True)
        json.dump(RES, open(os.path.join(HERE, "k1_scan_mid.json"), "w"), indent=1)
print("mid done")
