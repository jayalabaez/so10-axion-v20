#!/usr/bin/env python3
"""Cross-check of my integrator + root solve against the repository's genuine two-loop PS witness chain
(two_loop_thresholds_v20.TWO_LOOP_REFERENCE: M_I = 6.5608359043e10, M_GUT = 1.2515088239e16, alpha_U^-1 = 33.46890875),
using the repository's pinned coefficient tables (read-only import) but MY Segment/DOP853 runner and MY root finder."""
import json, math, os, sys
import numpy as np
from scipy.optimize import brentq
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo")
import two_loop_thresholds_v20 as repo
from k1_lib import Segment, run_segment
seg_low = Segment(repo.B2_LOW_2HDM, repo.BIJ_LOW_2HDM, loops=2)
seg_ps = Segment(repo.B2_PS_ANCHOR, repo.BIJ_PS_ANCHOR, loops=2)
A = np.array([repo.A1, repo.A2, repo.A3])
def residual(log10_mi):
    t_mi = log10_mi * math.log(10.0)
    a, _, _ = run_segment(seg_low, A, math.log(repo.MZ), t_mi)
    i1, i2, i3 = a
    v0 = np.array([i3, i2, (5.0 * i1 - 2.0 * i3) / 3.0])  # (SU4, SU2L, SU2R)
    # find crossing alpha_4^-1 = alpha_L^-1 by integrating to a dense grid and bisection on t
    def diff(t):
        y, _, _ = run_segment(seg_ps, v0, t_mi, t)
        return y[0] - y[1], y
    t_hi = math.log(1e19)
    d0, _ = diff(t_mi + 1e-9)
    d1, _ = diff(t_hi)
    if d0 * d1 > 0:
        return float("nan"), None
    t_cross = brentq(lambda t: diff(t)[0], t_mi + 1e-9, t_hi, xtol=1e-13)
    _, y = diff(t_cross)
    return y[0] - y[2], (t_cross, y)
root = brentq(lambda x: residual(x)[0], 10.0, 11.5, xtol=1e-12)
r, (t_cross, y) = residual(root)
out = {"M_I": 10 ** root, "M_GUT": math.exp(t_cross), "alpha_inv_U": float(y[1]), "residual": r,
       "reference": dict(repo.TWO_LOOP_REFERENCE)}
out["rel_dev_M_I"] = out["M_I"] / repo.TWO_LOOP_REFERENCE["M_I_GeV"] - 1
out["rel_dev_M_GUT"] = out["M_GUT"] / repo.TWO_LOOP_REFERENCE["M_GUT_GeV"] - 1
out["abs_dev_alpha_inv"] = out["alpha_inv_U"] - repo.TWO_LOOP_REFERENCE["alpha_inv_GUT"]
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "k1_repo_chain_check.json"), "w"), indent=1)
