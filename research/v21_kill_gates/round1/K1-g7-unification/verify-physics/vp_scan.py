#!/usr/bin/env python3
"""Verifier scans: M_s crossing, Phi placement, b3 scaling, vector-threshold constant convention, coherent threshold
extremes, reduced threshold Monte Carlo, Planck-c sensitivity (own Clebsches), 2HDM, loop-term ratios."""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vp_chain import MPL, PI, Model, full_point, heavy_at_MU, light_at_vR, proton_tau_years  # noqa: E402

T0 = time.time()
RES = {}
OUT = os.path.join(HERE, "vp_scan.json")
SMAX = 2.9e13


def log(m):
    print(f"[{time.time()-T0:5.0f}s] {m}", flush=True)


def save():
    json.dump(RES, open(OUT, "w"), indent=1, default=float)


def ys(M_s):
    return M_s / SMAX


# 1. M_s scan (y_s at quality minimum), Phi at 1e17 and at M_U, both contents, 3L
rows = []
for content in ("T2", "T3"):
    for M_s in (3e12, 5e12, 7e12, 8.5e12, 9e12, 9.5e12, 1e13, 2e13):
        for mphi in (1e17, 1e10):
            r, m = full_point(content=content, loops=3, M_s=M_s, y_s=ys(M_s), M_phi=mphi)
            rows.append({"content": content, "M_s": M_s, "M_phi": mphi, **{k: r[k] for k in ("ok", "v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio", "tau_p")}})
            log(f"Ms-scan {content} M_s={M_s:.2e} Mphi={mphi:.0e}: v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU={r['alpha_U_inv']:.3f} L2={r['L2_ratio']:.3f} L3={r['L3_ratio']:.3f}")
RES["Ms_scan"] = rows
save()

# 2. systematics at the nominal point
for content in ("T2", "T3"):
    d = {}
    r0, m0 = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
    d["nominal"] = r0
    for f in (0.5, 0.75, 1.25, 1.5):
        d[f"b3_x{f}"] = m0.landau(r0["M_U"], r0["alpha_U_inv"], loops=3, b3_factor=f)["ratio"]
    # loop-term ratios at M_U (below M_phi coefficients) and at M_Pl (above)
    aU = r0["alpha_U_inv"]
    b1, b2, b3 = (float(x) for x in m0.so_lo)
    d["2L_over_1L_at_MU_belowMphi_coeffs"] = (b2 / (8 * PI**2 * aU)) / (b1 / (2 * PI))
    d["3L_over_2L_at_MU"] = (b3 / (32 * PI**3 * aU * aU)) / (b2 / (8 * PI**2 * aU))
    b1h, b2h, b3h = (float(x) for x in m0.so_hi)
    d["2L_over_1L_at_MU_aboveMphi_coeffs"] = (b2h / (8 * PI**2 * aU)) / (b1h / (2 * PI))
    am = r0["ainv_MPl_3L"]
    if am:
        d["ainv_MPl_3L"] = am
        d["2L_over_1L_at_MPl"] = (b2h / (8 * PI**2 * am)) / (b1h / (2 * PI))
        d["3L_over_2L_at_MPl"] = (b3h / (32 * PI**3 * am * am)) / (b2h / (8 * PI**2 * am))
    # scale where 3L/2L = 0.5 on the 3L trajectory: alpha^-1 = b3h/(2 b2h) * 2/(4 pi)...: ratio = b3 /(4 pi b2 a) = 0.5 -> a = b3/(2 pi b2)
    d["ainv_where_3L_eq_half_2L"] = b3h / (2 * PI * b2h)
    # vector-threshold constant convention kappa_V = +-2 (DR-bar-like constant 2 S_i(V)/(12 pi)) -- EXACT size test
    for kv in (2.0, -2.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, kappa_V=kv)
        d[f"kappaV={kv:+.0f}"] = {k: r[k] for k in ("v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio")}
    # Yukawa variants
    for Y126 in (0.0, 1.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, Y126=Y126)
        d[f"Y126={Y126}"] = {k: r[k] for k in ("L2_ratio", "L3_ratio")}
    r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, yukawa=False)
    d["yukawa_off"] = {k: r[k] for k in ("v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio")}
    # Phi placement
    for mphi, yphi in ((1.25e17, 1.25), (3.5e17, 3.5), (1e10, 1.0)):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=mphi, y_phi=yphi)
        d[f"Mphi={mphi:.3g}"] = {k: r[k] for k in ("L2_ratio", "L3_ratio")}
    # 2HDM below v_R
    r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, n_higgs=2)
    d["2HDM_below_vR"] = {k: r[k] for k in ("v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio")}
    # coherent extremes
    hn = [h[0] for h in heavy_at_MU(content)]
    ln = [l[0] for l in light_at_vR(content)]
    for gf in (0.5, 1.0, 2.0):
        for lf in (1 / 3, 1.0, 3.0):
            r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17,
                              gut_ratios={n: gf for n in hn}, light_ratios={n: lf for n in ln}, v311_ratio=gf)
            d[f"coherent_gut{gf}_light{lf:.3f}"] = {k: r[k] for k in ("v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio", "tau_p")}
    # only W_R heavier / lighter (the dominant light threshold per the researcher)
    for wr in (1 / 3, 3.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, light_ratios={"W_R": wr, "Z_R": wr})
        d[f"WR_ZR_x{wr:.3f}"] = {k: r[k] for k in ("v_R", "M_U", "alpha_U_inv", "L3_ratio")}
    RES[f"syst_{content}"] = d
    save()
    log(f"syst {content}: " + json.dumps({k: (v if not isinstance(v, dict) else {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk in ('L2_ratio', 'L3_ratio', 'v_R', 'M_U', 'alpha_U_inv')}) for k, v in d.items() if k != 'nominal'}, default=float))

# 3. Planck-c sensitivity with own Clebsches (self-consistent iteration), T2/T3, theta = 45 deg, s = +1 and -1
planck = []
for content in ("T2", "T3"):
    for s in (1, -1):
        for th_deg in (45, 15):
            th = math.radians(th_deg)
            for c in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3):
                m = Model(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, planck_c=c)
                sol = m.solve()
                for _ in range(6):
                    g = math.sqrt(4 * PI / sol["alpha_U_inv"])
                    rho = sol["M_U"] / (g * math.sqrt(math.cos(th) ** 2 / 2 + math.sin(th) ** 2))
                    p, a = rho * math.cos(th), rho * math.sin(th)
                    m.planck_eps = tuple(k / MPL for k in (-2 * a, s * 2 * p, -s * 2 * p, 4 * a))
                    sol = m.solve(guess=tuple(sol["x"]))
                    if not sol["ok"]:
                        break
                row = {"content": content, "s": s, "theta": th_deg, "c": c, "ok": sol["ok"], "v_R": sol["v_R"], "M_U": sol["M_U"],
                       "alpha_U_inv": sol["alpha_U_inv"], "eps_per_c": list(m.planck_eps)}
                if sol["ok"]:
                    row["L2_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=2)["ratio"]
                    row["L3_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=3)["ratio"]
                planck.append(row)
                log(f"planck {content} s={s:+d} th={th_deg} c={c:+.1f}: ok={sol['ok']} v_R={sol['v_R']:.3e} M_U={sol['M_U']:.3e} aU={sol['alpha_U_inv']:.3f} "
                    f"L2={row.get('L2_ratio', float('nan')):.3f} L3={row.get('L3_ratio', float('nan')):.3f} eps/c={[round(x, 4) for x in m.planck_eps]}")
RES["planck"] = planck
save()

# 4. reduced threshold Monte Carlo (own RNG), GUT x1/2..x2, x1/2..x1, light x1/3..x3, combined; n = 60 each
rng = np.random.default_rng(7)


def mc(content, n, gut, light, M_s=1e13, M_phi=1e17):
    hn = [h[0] for h in heavy_at_MU(content)]
    ln = [l[0] for l in light_at_vR(content)]
    L2, L3, vr, mu = [], [], [], []
    for _ in range(n):
        gr, v311 = {}, 1.0
        if gut:
            gr = {nm: float(math.exp(rng.uniform(math.log(gut[0]), math.log(gut[1])))) for nm in hn}
            v311 = float(math.exp(rng.uniform(math.log(gut[0]), math.log(gut[1]))))
        lr = {}
        if light:
            lr = {nm: float(math.exp(rng.uniform(math.log(light[0]), math.log(light[1])))) for nm in ln}
        r, _ = full_point(content=content, loops=3, M_s=M_s, y_s=ys(M_s), M_phi=M_phi, gut_ratios=gr, light_ratios=lr, v311_ratio=v311)
        if r["ok"]:
            L2.append(r["L2_ratio"]); L3.append(r["L3_ratio"]); vr.append(r["v_R"]); mu.append(r["M_U"])
    L2, L3 = np.array(L2), np.array(L3)
    return {"n_ok": len(L2), "pass3": float(np.mean(L3 > 1)), "pass2": float(np.mean(L2 > 1)),
            "L3_min_med_max": [float(L3.min()), float(np.median(L3)), float(L3.max())],
            "L2_min_med_max": [float(L2.min()), float(np.median(L2)), float(L2.max())],
            "vR_min_med_max": [float(min(vr)), float(np.median(vr)), float(max(vr))],
            "MU_min_med_max": [float(min(mu)), float(np.median(mu)), float(max(mu))]}


for content in ("T2", "T3"):
    for tag, gut, light, M_s in (("gut_half_2", (0.5, 2.0), None, 1e13), ("gut_half_1", (0.5, 1.0), None, 1e13),
                                 ("light_third_3", None, (1 / 3, 3.0), 1e13), ("combined_1e13", (0.5, 2.0), (1 / 3, 3.0), 1e13),
                                 ("combined_5e12", (0.5, 2.0), (1 / 3, 3.0), 5e12)):
        s = mc(content, 60, gut, light, M_s=M_s)
        RES[f"mc_{content}_{tag}"] = s
        save()
        log(f"MC {content} {tag}: {json.dumps(s)}")
log("done")
