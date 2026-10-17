#!/usr/bin/env python3
"""Nominal one/two/three-loop solutions for C0, C1, C2, C1p with the B63 fermions (M_s = 1e13, y_s = 0.336,
Phi pair at 1e17, Am45 (3,1,1) ratio), with the S_V matching constant (+1 = MS-bar, 0 = off, -1 = opposite sign)."""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

KEYS = ("ok", "v_R", "M_U", "alpha_U_inv", "M311", "tau_p_yr", "tau_p_yr_alphaH0.0144", "L2", "L3", "L2_ax1", "L3_ax1",
        "L2_ax1_first", "L2_ax1_axMU", "L2_ax3969", "L3_ax3969", "b_G3221", "resid_max")
out = {"settings": "M_s=1e13 y_s=0.336 M_phi=1e17 Y126_tr2=0.5 c=0 v311=0.894 (Am45)"}
t0 = time.time()
for cont in ("C0", "C1", "C2", "C1p"):
    for sv in (+1, 0, -1):
        for loops, sm3 in ((1, False), (2, False), (3, False), (3, True)):
            p = M.Params(light=M.CONTENTS[cont], sv_sign=sv, loops=loops, sm_3loop=sm3)
            ll = () if loops == 1 else ((2,) if loops == 2 else (3,))
            xo = (None,) if loops == 1 else (None, 1.0, 3969.0)
            r = M.full_point(p, landau_loops=ll, x_opts=xo)
            key = f"{cont}|sv{sv:+d}|{loops}L" + ("|sm3L" if sm3 else "")
            out[key] = {k: r.get(k) for k in KEYS if k in r}
            print(key, json.dumps(out[key], default=lambda x: str(x)), flush=True)
out["seconds"] = time.time() - t0
with open(os.path.join(HERE, "r2b_nominal.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
print("done", out["seconds"])
