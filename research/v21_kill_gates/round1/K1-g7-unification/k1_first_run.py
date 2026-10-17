#!/usr/bin/env python3
"""First chain runs (nominal thresholds, c = 0): compare with the critic's C4 table and the RK4 cross-check."""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from k1_lib import M_PL_RED, Segment, rk4_run, run_segment  # noqa: E402
from k1_model import Chain, Params, proton_lifetime_years, set_yt  # noqa: E402

rows = []
t0 = time.time()
for content in ("T2", "T3"):
    for loops in (1, 2, 3):
        for M_s in (5.0e12, 1.0e13):
            for yuk in (False, True):
                p = Params(content=content, loops=loops, M_s=M_s, y_s=0.35, M_phi=1.0e17, yukawa=yuk)
                ch = Chain(p)
                if yuk:
                    set_yt(ch, 3e13)
                sol = ch.solve()
                if yuk:
                    set_yt(ch, sol["v_R"])
                    sol = ch.solve((math.log(sol["v_R"]), math.log(sol["M_U"]), sol["a2R_inv_vR"]))
                row = {"content": content, "loops": loops, "M_s": M_s, "yukawa": yuk, **sol}
                for mphi in ("MU", 1.0e17):
                    p.M_phi = sol["M_U"] if mphi == "MU" else mphi
                    lam = ch.landau(sol["M_U"], sol["alpha_U_inv"])
                    row[f"Lambda_Mphi={mphi}"] = lam["Lambda"]
                    row[f"alpha_inv_MPl_Mphi={mphi}"] = lam["alpha_inv_MPl"]
                row["tau_p_yr"] = proton_lifetime_years(sol["M_U"], sol["alpha_U_inv"])
                rows.append(row)
                print(f"{content} {loops}L M_s={M_s:.1e} yuk={yuk}: ok={sol['ok']} v_R={sol['v_R']:.3e} M_U={sol['M_U']:.3e} "
                      f"aU^-1={sol['alpha_U_inv']:.3f} Lambda(Phi@MU)={row['Lambda_Mphi=MU']:.3e} "
                      f"Lambda(Phi@1e17)={row['Lambda_Mphi=1e+17']:.3e} tau_p={row['tau_p_yr']:.2e} [{time.time()-t0:.0f}s]",
                      flush=True)

# RK4 cross-check of the DOP853 integrator on the SO(10) segment of the last row
p = Params(content="T2", loops=3, M_s=1e13, M_phi=1e17, yukawa=False)
ch = Chain(p)
sol = ch.solve()
lam = ch.landau(sol["M_U"], sol["alpha_U_inv"])
seg = Segment([ch.b_so10_lo[0]], [[ch.b_so10_lo[1]]], b3=[ch.b_so10_lo[2]], loops=3)
y = rk4_run(seg, np.array([sol["alpha_U_inv"]]), math.log(sol["M_U"]), math.log(1e17), h=0.002)
seg2 = Segment([ch.b_so10_hi[0]], [[ch.b_so10_hi[1]]], b3=[ch.b_so10_hi[2]], loops=3)
y2 = rk4_run(seg2, y, math.log(1e17), math.log(M_PL_RED), h=0.002)
y_dop, _, _ = run_segment(seg, np.array([sol["alpha_U_inv"]]), math.log(sol["M_U"]), math.log(1e17))
y_dop2, _, _ = run_segment(seg2, y_dop, math.log(1e17), math.log(M_PL_RED))
print("RK4 vs DOP853 alpha^-1(M_Pl):", float(y2[0]), float(y_dop2[0]), "landau:", lam)
# RK4 cross-check of the full low-energy chain at the solution (two-loop)
p = Params(content="T2", loops=2, M_s=1e13, M_phi=1e17, yukawa=False)
ch = Chain(p)
sol = ch.solve()
res = ch.run_to_MU(math.log(sol["v_R"]), math.log(sol["M_U"]), sol["a2R_inv_vR"])
a = rk4_run(ch.seg_sm0, np.array([59.02, 29.57, 1 / 0.1179]), math.log(91.1876), math.log(1e13), h=0.002)
a = rk4_run(ch.seg_sm1, a, math.log(1e13), math.log(sol["v_R"]), h=0.002)
print("RK4 SM at v_R:", a.tolist(), " DOP853:", res["a_sm_vR"].tolist())
with open(os.path.join(HERE, "k1_first_run.json"), "w") as fh:
    json.dump({"rows": rows, "rk4_vs_dop853_alpha_inv_MPl": [float(y2[0]), float(y_dop2[0])],
               "rk4_sm_vR": a.tolist(), "dop_sm_vR": res["a_sm_vR"].tolist()}, fh, indent=1)
