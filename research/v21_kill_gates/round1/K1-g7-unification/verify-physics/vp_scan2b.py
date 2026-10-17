#!/usr/bin/env python3
"""Verifier scans (part A, second half): systematics at the nominal point and the Planck small-c scan.  Loads the
M_s grid saved by vp_scan2.py.  Tolerant acceptance: a solution is accepted when max|residual| < 1e-6 even if
fsolve's ier != 1 (the bisection crash of vp_scan2.py was one such point)."""
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
from vp_chain import MPL, PI, Model, heavy_at_MU, light_at_vR, proton_tau_years  # noqa: E402

T0 = time.time()
OUT = os.path.join(HERE, "vp_scan2.json")
RES = json.load(open(OUT)) if os.path.exists(OUT) else {}
SMAX = 2.9e13


def log(m):
    print(f"[{time.time()-T0:5.0f}s] {m}", flush=True)


def save():
    json.dump(RES, open(OUT, "w"), indent=1, default=float)


def ys(M_s):
    return M_s / SMAX


def point(**kw):
    m = Model(**kw)
    s = m.solve()
    ok = s["resid"] < 1e-6 and np.isfinite(s["resid"])
    out = dict(s)
    out["ok"] = bool(ok)
    if ok:
        for L in (2, 3):
            lam = m.landau(s["M_U"], s["alpha_U_inv"], loops=L)
            out[f"L{L}_ratio"] = lam["ratio"]
            out[f"ainv_MPl_{L}L"] = lam["a_inv_MPl"]
        out["tau_p"] = proton_tau_years(s["M_U"], s["alpha_U_inv"])
    else:
        out["L2_ratio"] = out["L3_ratio"] = float("nan")
        out["tau_p"] = float("nan")
    return out, m


KEYS = ("ok", "v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio", "tau_p", "resid")


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


# crossing from the saved grid (linear interpolation in ln M_s between the bracketing points, Phi at 1e17 and 1.25e17)
for content in ("T2", "T3"):
    for mphi in (1e17, 1.25e17):
        rows = sorted([r for r in RES.get("Ms_scan", []) if r["content"] == content and r["M_phi"] == mphi],
                      key=lambda r: r["M_s"])
        for a, b in zip(rows[:-1], rows[1:]):
            if a["L3_ratio"] < 1 <= b["L3_ratio"]:
                f = (1 - a["L3_ratio"]) / (b["L3_ratio"] - a["L3_ratio"])
                RES[f"Ms_crossing_{content}_Mphi{mphi:.3g}"] = math.exp(math.log(a["M_s"]) + f * math.log(b["M_s"] / a["M_s"]))
                log(f"crossing {content} Mphi={mphi:.3g}: {RES[f'Ms_crossing_{content}_Mphi{mphi:.3g}']:.4e}")
save()

# 2. systematics at the nominal point
for content in ("T2", "T3"):
    d = {}
    r0, m0 = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
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
    d["yt_at_vR"] = m0.yt_cache[1]
    for kv in (1.0, -1.0, 2.0, -2.0):
        r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, kappa_V=kv)
        d[f"kappaV={kv:+.0f}"] = pick(r)
    for Y126 in (0.0, 1.0):
        r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, Y126=Y126)
        d[f"Y126={Y126}"] = pick(r)
    r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, yukawa=False)
    d["yukawa_off"] = pick(r)
    r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, n_higgs=2)
    d["2HDM_below_vR"] = pick(r)
    r, _ = point(content=content, loops=1, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
    d["one_loop_chain"] = pick(r)
    hn = [h[0] for h in heavy_at_MU(content)]
    ln_ = [l[0] for l in light_at_vR(content)]
    for gf in (0.5, 1.0, 2.0):
        for lf in (1 / 3, 1.0, 3.0):
            r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17,
                         gut_ratios={n: gf for n in hn}, light_ratios={n: lf for n in ln_}, v311_ratio=gf)
            d[f"coherent_gut{gf}_light{lf:.3f}"] = pick(r)
    for wr in (1 / 3, 3.0):
        r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17,
                     light_ratios={"W_R": wr, "Z_R": wr})
        d[f"WR_x{wr:.3f}"] = pick(r)
    for v3 in (0.5, 2.0):
        r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17, v311_ratio=v3)
        d[f"V311_x{v3}"] = pick(r)
    for ds in (+0.0009, -0.0009):
        vc.A_MZ[2] = 1.0 / (0.1179 + ds)
        r, _ = point(content=content, loops=3, M_s=1e13, y_s=ys(1e13), M_phi=1e17)
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
                ok = sol["resid"] < 1e-6
                for _ in range(8):
                    if not ok:
                        break
                    g = math.sqrt(4 * PI / sol["alpha_U_inv"])
                    rho = sol["M_U"] / (g * math.sqrt(math.cos(th) ** 2 / 2 + math.sin(th) ** 2))
                    p, a = rho * math.cos(th), rho * math.sin(th)
                    m.planck_eps = tuple(k / MPL for k in (-2 * a, s * 2 * p, -s * 2 * p, 4 * a))
                    sol = m.solve(guess=tuple(sol["x"]))
                    ok = sol["resid"] < 1e-6 and np.isfinite(sol["resid"])
                row = {"content": content, "s": s, "theta": th_deg, "c": c, "ok": bool(ok), "v_R": sol["v_R"],
                       "M_U": sol["M_U"], "alpha_U_inv": sol["alpha_U_inv"], "eps_per_c": list(m.planck_eps),
                       "resid": sol["resid"]}
                if ok:
                    row["L2_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=2)["ratio"]
                    row["L3_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=3)["ratio"]
                planck.append(row)
                log(f"planck {content} s={s:+d} th={th_deg} c={c:+.2f}: ok={ok} v_R={sol['v_R']:.3e} "
                    f"M_U={sol['M_U']:.3e} aU={sol['alpha_U_inv']:.3f} L2={row.get('L2_ratio', float('nan')):.3f} "
                    f"L3={row.get('L3_ratio', float('nan')):.3f} eps/c={[round(x, 4) for x in m.planck_eps]}")
            RES["planck"] = planck
            save()
log("done A2")
