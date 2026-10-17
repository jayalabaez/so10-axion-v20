#!/usr/bin/env python3
"""Skeptic threshold Monte Carlo (own RNG seed, own sampler).  Usage: sk_mc.py N content [content...]"""
import json, math, os, sys, time
import numpy as np
import sk_lib as L
import sk_unify as U

SK = 2.4e34
N = int(sys.argv[1])
conts = sys.argv[2:]
rng = np.random.default_rng(777)
out = {}
for c in conts:
    nl = len(L.light_thr_states(L.CONTENTS[c]))
    nh = len(L.heavy_states(L.CONTENTS[c]))
    rows = []
    t0 = time.time()
    for i in range(N):
        ll = list(np.exp(rng.uniform(math.log(1 / 3), math.log(3), nl)))
        gl = list(np.exp(rng.uniform(math.log(0.5), math.log(2.0), nh)))
        m = U.Model(c, light_list=ll, gut_list=gl)
        r = m.solve()
        if r is None:
            rows.append({"ok": False})
            continue
        r["tau_repo"] = U.tau_repo(r["M_U"], r["aU"])
        r["tau_lat"] = U.tau_lattice(r["M_U"], r["aU"])
        r["L2"] = m.landau(r["M_U"], r["aU"], 2)
        r["ok"] = True
        rows.append(r)
    ok = [r for r in rows if r["ok"]]
    f = lambda cond: sum(1 for r in ok if cond(r)) / N
    summ = {"n": N, "n_ok": len(ok), "nl": nl, "nh": nh,
            "f_pass_repo": f(lambda r: r["tau_repo"] > SK and r["L2"] > 1),
            "f_pass_lat": f(lambda r: r["tau_lat"] > SK and r["L2"] > 1),
            "f_pass_repo_vR_ge_1e11": f(lambda r: r["tau_repo"] > SK and r["L2"] > 1 and r["v_R"] >= 1e11),
            "tau_repo_min_med_max": [float(np.min([r["tau_repo"] for r in ok])), float(np.median([r["tau_repo"] for r in ok])), float(np.max([r["tau_repo"] for r in ok]))],
            "vR_min_max": [float(min(r["v_R"] for r in ok)), float(max(r["v_R"] for r in ok))],
            "L2_min": float(min(r["L2"] for r in ok)), "sec": time.time() - t0}
    out[c] = {"summary": summ, "rows": rows}
    print(c, json.dumps(summ), flush=True)
with open(f"sk_mc_{'_'.join(conts)}_N{N}.json", "w") as fh:
    json.dump(out, fh, indent=1, default=float)
