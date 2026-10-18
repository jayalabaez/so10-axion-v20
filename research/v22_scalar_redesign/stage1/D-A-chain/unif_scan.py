#!/usr/bin/env python3
"""Scan of minimal light-scalar sets for SO(10) -> SM direct (unif_sm.py). For every pair (A, B) of candidate light
multiplets: grid in m_A, solve m_B from exact two-loop unification (d3 = 0), record M_U, alpha_U^-1, tau (lattice x
chain A_R), Lambda_2L/3L.  Also single states (with M_s free in [3e12, 1.21e13]).  NUM."""
import math, json, sys, itertools, time
import numpy as np
from scipy.optimize import brentq
import unif_sm as U

pairs = [("(8,3,0)R", "(8,1,0)R"), ("(8,3,0)R", "(8,2,1/2)"), ("(6,3,1/3)", "(8,2,1/2)"), ("(8,3,0)R", "(6,2,-1/6)"),
         ("(6,3,1/3)", "(8,1,0)R"), ("(8,3,0)R", "(1,3,0)R"), ("(8,3,0)R", "(1,2,1/2)"), ("(6,3,1/3)", "(6,2,-1/6)"),
         ("(8,3,0)R", "(1,3,1)"), ("(6,3,1/3)", "(1,3,1)"), ("(8,2,1/2)", "(1,3,0)R"), ("(8,2,1/2)", "(1,3,1)"),
         ("(8,3,0)R", "(8,1,1)"), ("(6,3,1/3)", "(8,1,1)")]
MLO = 3e3
out = {}
t0 = time.time()
for A, B in pairs:
    rows = []
    for lmA in np.linspace(math.log10(MLO), 15.5, 26):
        mA = 10 ** lmA

        def d3(lmB):
            u = U.unify([(A, mA), (B, 10 ** lmB)])
            return 1e3 if u is None else u["d3"]
        grid = np.linspace(math.log10(MLO), 16.5, 28)
        vals = [d3(x) for x in grid]
        for i in range(len(grid) - 1):
            if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0 and abs(vals[i]) < 100 and abs(vals[i + 1]) < 100:
                lmB = brentq(d3, grid[i], grid[i + 1], xtol=1e-6)
                p = U.point([(A, mA), (B, 10 ** lmB)])
                if p is None or p["M_U"] < max(mA, 10 ** lmB):
                    continue
                rows.append({"mA": mA, "mB": 10 ** lmB, **{k: p[k] for k in ("M_U", "aU", "A_R", "tau_lat", "tau_repo", "L2", "L3")}})
    good = [r for r in rows if r["tau_lat"] > 2.4e34 and r["L2"] > 1.0]
    best = max(rows, key=lambda r: r["tau_lat"]) if rows else None
    out[f"{A}+{B}"] = {"n": len(rows), "n_pass_tau_L2": len(good), "best_tau": best,
                       "best_pass": (max(good, key=lambda r: r["L2"]) if good else None), "rows": rows}
    bt = best
    print(f"{A:11s}+{B:11s} n={len(rows):3d} pass(tau,L2)={len(good):3d}  best tau: " +
          (f"mA={bt['mA']:.2e} mB={bt['mB']:.2e} MU={bt['M_U']:.3e} aU={bt['aU']:.2f} AR={bt['A_R']:.2f} tau={bt['tau_lat']:.2e} L2={bt['L2']:.2f} L3={bt['L3']:.2f}" if bt else "none"),
          f"[{time.time()-t0:.0f}s]", flush=True)
json.dump(out, open("unif_scan.json", "w"), indent=1)
