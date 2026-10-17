#!/usr/bin/env python3
"""Verifier scans (part B): reduced threshold Monte Carlo with an independent RNG seed (log-uniform ratios, every
multiplet independent, as the researcher did)."""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_chain as vc  # noqa: E402

_orig_rk4 = vc.rk4


def _rk4_fast(seg, a0, t0, t1, h=0.02, stop_at_alpha_inv=None):
    return _orig_rk4(seg, a0, t0, t1, h=h, stop_at_alpha_inv=stop_at_alpha_inv)


vc.rk4 = _rk4_fast
from vp_chain import full_point, heavy_at_MU, light_at_vR  # noqa: E402

T0 = time.time()
RES = {}
OUT = os.path.join(HERE, "vp_mc.json")
SMAX = 2.9e13


def log(m):
    print(f"[{time.time()-T0:5.0f}s] {m}", flush=True)


def save():
    json.dump(RES, open(OUT, "w"), indent=1, default=float)


def ys(M_s):
    return M_s / SMAX


rng = np.random.default_rng(20261016)


def mc(content, n, gut, light, M_s=1e13, M_phi=1e17):
    hn = [h[0] for h in heavy_at_MU(content)]
    ln_ = [l[0] for l in light_at_vR(content)]
    L2, L3, vr, mu, tp = [], [], [], [], []
    for _ in range(n):
        gr, v311 = {}, 1.0
        if gut:
            gr = {nm: float(math.exp(rng.uniform(math.log(gut[0]), math.log(gut[1])))) for nm in hn}
            v311 = float(math.exp(rng.uniform(math.log(gut[0]), math.log(gut[1]))))
        lr = {}
        if light:
            lr = {nm: float(math.exp(rng.uniform(math.log(light[0]), math.log(light[1])))) for nm in ln_}
        r, _ = full_point(content=content, loops=3, M_s=M_s, y_s=ys(M_s), M_phi=M_phi, gut_ratios=gr,
                          light_ratios=lr, v311_ratio=v311)
        if r["ok"]:
            L2.append(r["L2_ratio"])
            L3.append(r["L3_ratio"])
            vr.append(r["v_R"])
            mu.append(r["M_U"])
            tp.append(r["tau_p"])
    L2, L3, tp = np.array(L2), np.array(L3), np.array(tp)
    return {"n_ok": int(len(L2)), "n": n, "pass3": float(np.mean(L3 > 1)), "pass2": float(np.mean(L2 > 1)),
            "L3_min_p05_med_p95_max": [float(L3.min()), float(np.percentile(L3, 5)), float(np.median(L3)),
                                       float(np.percentile(L3, 95)), float(L3.max())],
            "L2_min_med_max": [float(L2.min()), float(np.median(L2)), float(L2.max())],
            "vR_min_med_max": [float(min(vr)), float(np.median(vr)), float(max(vr))],
            "MU_min_med_max": [float(min(mu)), float(np.median(mu)), float(max(mu))],
            "tau_min_med": [float(tp.min()), float(np.median(tp))],
            "frac_tau_below_2.4e34": float(np.mean(tp < 2.4e34))}


for content in ("T2", "T3"):
    for tag, gut, light, M_s, n in (("gut_half_2", (0.5, 2.0), None, 1e13, 60),
                                    ("gut_half_1", (0.5, 1.0), None, 1e13, 40),
                                    ("light_third_3", None, (1 / 3, 3.0), 1e13, 60),
                                    ("combined_1e13", (0.5, 2.0), (1 / 3, 3.0), 1e13, 80),
                                    ("combined_5e12", (0.5, 2.0), (1 / 3, 3.0), 5e12, 40),
                                    ("combined_3e12", (0.5, 2.0), (1 / 3, 3.0), 3e12, 40)):
        s = mc(content, n, gut, light, M_s=M_s)
        RES[f"mc_{content}_{tag}"] = s
        save()
        log(f"MC {content} {tag}: {json.dumps(s)}")
log("done B")
