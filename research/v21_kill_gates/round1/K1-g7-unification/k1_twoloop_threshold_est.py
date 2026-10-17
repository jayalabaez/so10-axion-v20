#!/usr/bin/env python3
"""EST of the uncomputed two-loop GUT-threshold corrections: the heavy scalars' two-loop b_ij (G3221 decomposition)
times ln 2 times alpha_j/(8 pi^2) -- the change of alpha_i^-1(M_U) if all heavy states sat at 2 M_U instead of M_U
at two loops (the one-loop part is what the S2/S5 scans include).  Same for the light states at v_R (ln 3)."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k1_lib import mv_coefficients
from k1_model import G3221_C2, SM_C2, heavy_scalars_at_MU, light_thresholds_at_vR
out = {}
for content in ("T2", "T3"):
    heavy = [(n, k, r, m) for n, k, r, m in heavy_scalars_at_MU(content)]
    b, bij = mv_coefficients(G3221_C2, heavy)
    # subtract the pure gauge part (we want the heavy fields' contribution only)
    b0, bij0 = mv_coefficients(G3221_C2, [])
    bh = [float(b[i] - b0[i]) for i in range(4)]
    bijh = [[float(bij[i][j] - bij0[i][j]) for j in range(4)] for i in range(4)]
    aU = 1 / 26.5
    d2 = [sum(bijh[i][j] * aU for j in range(4)) / (8 * math.pi**2) * math.log(2) for i in range(4)]
    d1 = [bh[i] / (2 * math.pi) * math.log(2) for i in range(4)]
    out[content] = {"heavy_b_i": bh, "heavy_bij": bijh, "one_loop_shift_ln2_units": d1, "two_loop_shift_ln2_units": d2,
                    "two_loop_differences_max": max(d2) - min(d2)}
    light = [(n, k, r, m) for n, k, r, m in light_thresholds_at_vR(content) if k != "vector"]
    bl, bijl = mv_coefficients(SM_C2, light)
    bl0, bijl0 = mv_coefficients(SM_C2, [])
    a_vR = [1 / 40.3, 1 / 41.2, 1 / 36.8]
    d2l = [sum(float(bijl[i][j] - bijl0[i][j]) * a_vR[j] for j in range(3)) / (8 * math.pi**2) * math.log(3) for i in range(3)]
    out[content]["light_two_loop_shift_ln3_units"] = d2l
    out[content]["light_two_loop_differences_max"] = max(d2l) - min(d2l)
print(json.dumps(out, indent=1))
json.dump(out, open("k1_twoloop_threshold_est.json", "w"), indent=1)
