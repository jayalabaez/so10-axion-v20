#!/usr/bin/env python3
"""Reduced T3 Planck-coefficient check (theta = 45 deg, s = +-1, c = +-0.1, +-0.2), self-consistent in the 210 vev,
own Clebsches K = (-2a, s 2p, -s 2p, 4a).  Output: vp_planck_t3.json."""
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
from vp_chain import MPL, PI, Model  # noqa: E402

T0 = time.time()
rows = []
for s in (1, -1):
    th = math.radians(45)
    for c in (-0.2, -0.1, 0.1, 0.2):
        m = Model(content="T3", loops=3, M_s=1e13, y_s=1e13 / 2.9e13, M_phi=1e17, planck_c=c)
        sol = m.solve()
        ok = sol["resid"] < 1e-6
        for _ in range(6):
            if not ok:
                break
            g = math.sqrt(4 * PI / sol["alpha_U_inv"])
            rho = sol["M_U"] / (g * math.sqrt(math.cos(th) ** 2 / 2 + math.sin(th) ** 2))
            p, a = rho * math.cos(th), rho * math.sin(th)
            m.planck_eps = tuple(k / MPL for k in (-2 * a, s * 2 * p, -s * 2 * p, 4 * a))
            sol = m.solve(guess=tuple(sol["x"]))
            ok = sol["resid"] < 1e-6 and np.isfinite(sol["resid"])
        row = {"s": s, "c": c, "ok": bool(ok), "v_R": sol["v_R"], "M_U": sol["M_U"], "alpha_U_inv": sol["alpha_U_inv"],
               "eps_per_c": list(m.planck_eps)}
        if ok:
            row["L2_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=2)["ratio"]
            row["L3_ratio"] = m.landau(sol["M_U"], sol["alpha_U_inv"], loops=3)["ratio"]
        rows.append(row)
        print(f"[{time.time()-T0:4.0f}s] T3 s={s:+d} th=45 c={c:+.2f}: ok={ok} v_R={sol['v_R']:.3e} M_U={sol['M_U']:.3e} "
              f"aU={sol['alpha_U_inv']:.3f} L2={row.get('L2_ratio', float('nan')):.3f} L3={row.get('L3_ratio', float('nan')):.3f}",
              flush=True)
json.dump(rows, open(os.path.join(HERE, "vp_planck_t3.json"), "w"), indent=1, default=float)
