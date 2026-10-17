#!/usr/bin/env python3
"""Verifier scans (part A): M_s crossing, Phi placement, b3 scaling, vector-threshold constant convention, Yukawa variants,
2HDM, coherent threshold extremes, W_R-only, (3,1,1) vector, alpha_s, loop-term ratios (below- and above-M_Phi
coefficients), Planck small-c with own Clebsches.  Chain RK4 step 0.02 (checked: chain solution identical to h = 0.004),
Landau step 0.002."""
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
from vp_chain import MPL, PI, Model, full_point, heavy_at_MU, light_at_vR  # noqa: E402

T0 = time.time()
RES = {}
OUT = os.path.join(HERE, "vp_scan2.json")
SMAX = 2.9e13


def log(m):
    print(f"[{time.time()-T0:5.0f}s] {m}", flush=True)


def save():
    json.dump(RES, open(OUT, "w"), indent=1, default=float)


def ys(M_s):
    return M_s / SMAX


KEYS = ("ok", "v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio", "tau_p")


def pick(r):
    return {k: r.get(k) for k in KEYS}


def short(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()
                      if kk in ("L2_ratio", "L3_ratio", "v_R", "M_U", "alpha_U_inv")}
        elif isinstance(v, float):
            out[k] = round(v, 4)
        else:
            out[k] = v
    return out


# 1. M_s scan, Phi at 1e17, 1.25e17 and at M_U
rows = []
for content in ("T2", "T3"):
    for M_s in (3e12, 5e12, 7e12, 8.5e12, 9e12, 9.5e12, 1e13, 2e13):
        for mphi in (1e17, 1.25e17, 1e10):
            yphi = mphi / 1e17 if mphi > 1e16 else 1.0
            r, m = full_point(content=content, loops=3, M_s=M_s, y_s=ys(M_s), M_phi=mphi, y_phi=yphi)
            rows.append({"content": content, "M_s": M_s, "M_phi": mphi, **pick(r)})
            log(f"Ms-scan {content} M_s={M_s:.2e} Mphi={mphi:.3g}: v_R={r['v_R']:.4e} M_U={r['M_U']:.4e} "
                f"aU={r['alpha_U_inv']:.3f} L2={r['L2_ratio']:.4f} L3={r['L3_ratio']:.4f}")
RES["Ms_scan"] = rows
save()
for content in ("T2", "T3"):
    lo, hi = 8.0e12, 1.0e13
    for _ in range(12):
        mid = math.sqrt(lo * hi)
        r, _m = full_point(content=content, loops=3, M_s=mid, y_s=ys(mid), M_phi=1e17)
        if r["L3_ratio"] > 1:
            hi = mid
        else:
            lo = mid
    RES[f"Ms_crossing_{content}"] = math.sqrt(lo * hi)
    log(f"crossing {content}: M_s = {math.sqrt(lo*hi):.4e}")
save()

# 2. systematics at the nominal point
for content in ("T2", "T3"):
    d = {}
    r0, m0 = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
    d["nominal"] = pick(r0)
    for f in (0.5, 0.75, 1.25, 1.5):
        d[f"b3_x{f}"] = m0.landau(r0["M_U"], r0["alpha_U_inv"], loops=3, b3_factor=f)["ratio"]
    aU = r0["alpha_U_inv"]
    b1, b2, b3 = (float(x) for x in m0.so_lo)
    b1h, b2h, b3h = (float(x) for x in m0.so_hi)
    d["2L_over_1L_at_MU_belowMphi"] = (b2 / (8 * PI**2 * aU)) / (b1 / (2 * PI))
    d["2L_over_1L_at_MU_aboveMphi"] = (b2h / (8 * PI**2 * aU)) / (b1h / (2 * PI))
    d["3L_over_2L_at_MU_belowMphi"] = (b3 / (32 * PI**3 * aU * aU)) / (b2 / (8 * PI**2 * aU))
    am = r0["ainv_MPl_3L"]
    d["ainv_MPl_3L"] = am
    if am:
        d["2L_over_1L_at_MPl"] = (b2h / (8 * PI**2 * am)) / (b1h / (2 * PI))
        d["3L_over_2L_at_MPl"] = (b3h / (32 * PI**3 * am * am)) / (b2h / (8 * PI**2 * am))
    d["ainv_where_3L_eq_half_2L"] = b3h / (2 * PI * b2h)
    lan = m0.landau(r0["M_U"], aU, loops=3)
    d["Ylo_Yhi"] = [lan["Ylo"], lan["Yhi"]]
    for kv in (1.0, -1.0, 2.0, -2.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, kappa_V=kv)
        d[f"kappaV={kv:+.0f}"] = pick(r)
    for Y126 in (0.0, 1.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, Y126=Y126)
        d[f"Y126={Y126}"] = pick(r)
    r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, yukawa=False)
    d["yukawa_off"] = pick(r)
    r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, n_higgs=2)
    d["2HDM_below_vR"] = pick(r)
    r, _ = full_point(content=content, loops=1, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
    d["one_loop_chain"] = pick(r)
    hn = [h[0] for h in heavy_at_MU(content)]
    ln_ = [l[0] for l in light_at_vR(content)]
    for gf in (0.5, 1.0, 2.0):
        for lf in (1 / 3, 1.0, 3.0):
            r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17,
                              gut_ratios={n: gf for n in hn}, light_ratios={n: lf for n in ln_}, v311_ratio=gf)
            d[f"coherent_gut{gf}_light{lf:.3f}"] = pick(r)
    for wr in (1 / 3, 3.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17,
                          light_ratios={"W_R": wr, "Z_R": wr})
        d[f"WR_x{wr:.3f}"] = pick(r)
    for v3 in (0.5, 2.0):
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, v311_ratio=v3)
        d[f"V311_x{v3}"] = pick(r)
    for ds in (+0.0009, -0.0009):
        vc.A_MZ[2] = 1.0 / (0.1179 + ds)
        r, _ = full_point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
        d[f"alpha_s{ds:+.4f}"] = pick(r)
        vc.A_MZ[2] = 1.0 / 0.1179
    RES[f"syst_{content}"] = d
    save()
    log(f"syst {content}: " + json.dumps(short(d), default=float))

# 3. Planck-c with own Clebsches (self-consistent), th = 45, 15, 75 deg, s = +-1
planck = []
for content in ("T2", "T3"):
    for s in (1, -1):
        for th_deg in (45, 15, 75):
            th = math.radians(th_deg)
            for c in (-0.3, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.3):
                m = Model(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, planck_c=c)
                sol = m.solve()
                for _ in range(8):
                    g = math.sqrt(4 * PI / sol["alpha_U_inv"])
                    rho = sol["M_U"] / (g * math.sqrt(math.cos(th) ** 2 / 2 + math.sin(th) ** 2))
                    p, a = rho * math.cos(th), rho * math.sin(th)
                    m.planck_eps = tuple(k / MPL for k in (-2 * a, s * 2 * p, -s * 2 * p, 4 * a))
                    sol = m.solve(guess=tuple(sol["x"]))
                    if not sol["ok"]:
                        break
                row = {"content": content, "s": s, "theta": th_deg, "c": c, "ok": sol["ok"], "v_R": sol["v_R"],
                       "M_U": sol["M_U"], "alpha_U_inv": sol["alpha_U_inv"], "eps_per_c": list(m.planck_eps)}
                if sol["ok"]:
                    row["L2_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=2)["ratio"]
                    row["L3_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=3)["ratio"]
                planck.append(row)
                log(f"planck {content} s={s:+d} th={th_deg} c={c:+.2f}: ok={sol['ok']} v_R={sol['v_R']:.3e} "
                    f"M_U={sol['M_U']:.3e} aU={sol['alpha_U_inv']:.3f} L2={row.get('L2_ratio', float('nan')):.3f} "
                    f"L3={row.get('L3_ratio', float('nan')):.3f} eps/c={[round(x, 4) for x in m.planck_eps]}")
            RES["planck"] = planck
            save()
log("done A")
