#!/usr/bin/env python3
"""Validation of r2b_model against K1 (round 1) and the K1 feasibility skeptic's K3-content runs."""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

out = {}
t0 = time.time()
# K1 nominal T2/T3: M_s = 1e13, y_s = 0.345, Phi at 1e17, Y126 = 0.5, c = 0, no S_V constant, (3,1,1) at M_U
for cont in ("T2", "T3"):
    p = M.Params(light=M.CONTENTS[cont], M_s=1e13, y_s=0.345, sv_sign=0, v311_ratio=1.0, loops=2)
    r2 = M.full_point(p, landau_loops=(2,))
    p3 = M.Params(light=M.CONTENTS[cont], M_s=1e13, y_s=0.345, sv_sign=0, v311_ratio=1.0, loops=3)
    r3 = M.full_point(p3, landau_loops=(3,))
    p1 = M.Params(light=M.CONTENTS[cont], M_s=1e13, y_s=0.345, sv_sign=0, v311_ratio=1.0, loops=1)
    r1 = M.full_point(p1, landau_loops=())
    out[cont] = {"1L": {k: r1.get(k) for k in ("v_R", "M_U", "alpha_U_inv", "b_G3221")},
                 "2L": {k: r2.get(k) for k in ("v_R", "M_U", "alpha_U_inv", "L2", "tau_p_yr", "b_G3221")},
                 "3L": {k: r3.get(k) for k in ("v_R", "M_U", "alpha_U_inv", "L3")}}
    print(cont, json.dumps(out[cont], default=str), flush=True)
out["K1_reference"] = {"T2": "1L 1.406e13/4.631e16/26.58; 2L 2.496e13/2.045e16/27.102 L2 2.417 L3 1.051 tau 8.64e36",
                       "T3": "1L 1.648e13/6.533e16/25.63; 2L 2.958e13/2.914e16/26.129 L2 2.346 L3 1.049 tau 3.31e37"}
# skeptic (vf_k3_contents.json): bid_DR v_R 2.863e9 M_U 1.788e16 aU 33.92; T2-minus-822 8.017e12 / 2.297e15 / 33.27
for cont, extra in (("bid_DR", ()), ("C0", ("210:(1,3,1)_0",))):
    light = M.content_with(cont, extra)
    p = M.Params(light=light, M_s=1e13, y_s=0.345, sv_sign=0, v311_ratio=1.0, loops=2, yukawa=False)
    r = M.full_point(p, landau_loops=(2,))
    key = cont + ("+" + "+".join(extra) if extra else "")
    out["skeptic_" + key] = {k: r.get(k) for k in ("v_R", "M_U", "alpha_U_inv", "L2", "tau_p_yr", "b_G3221")}
    print(key, json.dumps(out["skeptic_" + key], default=str), flush=True)
out["skeptic_reference"] = {"bid_DR": "2.863e9 / 1.788e16 / 33.917 tau 7.9e36",
                            "T2_minus_822": "8.017e12 / 2.297e15 / 33.267 tau 2.07e33 (b 23/6, 28/3, 7, 89/6)"}
out["S_V"] = {"M_U": M.SV_MU_STR, "Y_at_vR": M.SV_Y_STR, "R311_Am45": M.R311_AM45, "MX_over_gPhi": M.MX_OVER_G_PHI}
out["seconds"] = time.time() - t0
with open(os.path.join(HERE, "r2b_validate.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
print("done", out["seconds"])
