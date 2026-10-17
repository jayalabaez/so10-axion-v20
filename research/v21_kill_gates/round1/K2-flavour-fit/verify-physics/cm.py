"""Charged-manifold search: (1) exact charged-sector solutions (7 residuals, 12 params; 'trf' least squares) from random
starts; (2) from each, joint LM on all 12 residuals with staged neutrino weights (inflate 10 -> 3 -> 1) and a few
perturbed restarts; keep the best.   usage: cm.py content seed n_charged
"""
import sys, os, json, math, time
import numpy as np
from scipy.optimize import least_squares
import k2v

content = sys.argv[1]; seed = int(sys.argv[2]); nch = int(sys.argv[3])
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
T, info, _ = k2v.build_targets(vR, MU, content)
M = k2v.Model(T, info["rnu"])
rng = np.random.default_rng(seed)
CH = ["m_u", "m_c", "m_t"] + k2v.CKM_KEYS

def charged_res(p):
    r, o, rho = M.residuals(p)
    if o is None:
        return np.full(7, 1e3)
    return r[:7]

t0 = time.time(); best = None; recs = []; nsol = 0
for i in range(nch * 4):
    if nsol >= nch:
        break
    p0 = M.random_start(rng)
    try:
        rc = least_squares(charged_res, p0, method="trf", max_nfev=2000, xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
    except Exception:
        continue
    c2c = float(np.sum(rc.fun**2))
    if c2c > 1e-3:
        continue
    nsol += 1
    # joint fits from this charged solution: staged nu weights
    loc = None
    for trial in range(4):
        p = rc.x.copy() if trial == 0 else rc.x + rng.normal(0, 0.1, M.n)
        try:
            for infl in (10.0, 3.0, 1.0):
                M.nuw = 1.0 / infl
                x, c2, nf = k2v.lm_fit(M, p, max_nfev=2000)
                p = x
            M.nuw = 1.0
            c2 = M.chi2(p)
        except Exception:
            M.nuw = 1.0
            continue
        if loc is None or c2 < loc[1]:
            loc = (p, c2)
    if loc is None:
        continue
    if best is None or loc[1] < best[1]:
        best = loc
        print(f"charged sol {nsol} (start {i}): joint chi2={loc[1]:.3f}  best so far  t={time.time()-t0:.0f}s", flush=True)
    if loc[1] < 100:
        recs.append(k2v.result_record(M, loc[0], vR, f"cm{nsol}"))
recs.sort(key=lambda r: r["chi2_18"])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"cm_{content}_{seed}.json")
json.dump({"content": content, "vR": vR, "MU": MU, "seed": seed, "n_charged": nsol, "best_chi2": best[1] if best else None,
           "records": recs[:20], "info": info}, open(out, "w"), indent=1)
if best:
    rec = k2v.result_record(M, best[0], vR, "best")
    print("BEST chi2_18 =", round(rec["chi2_18"], 4), "max|pull| =", round(rec["max_abs_pull"], 3))
    print("pulls:", {k: round(v, 2) for k, v in rec["pulls"].items()})
    print("comp:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in rec["comp"].items()})
