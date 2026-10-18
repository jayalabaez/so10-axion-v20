#!/usr/bin/env python3
"""Fine scan of the one-parameter unification families of the selected light contents (unif_sm.py, two loops):
for m_A on a fine grid solve m_B from d3 = 0; record M_U, alpha_U^-1, A_R, tau (lattice x chain A_R), Lambda_2L/3L.
Also: sensitivity to M_s in [5e12, 1.21e13] (y_s window ends) and a GUT-threshold envelope (all heavy scalar SM pieces
at M_U x 10^{+-1/2} is not implemented generically; instead the S_V constant is switched off/on as a convention check)."""
import math, json, sys
import numpy as np
from scipy.optimize import brentq
import unif_sm as U

FAMS = {"U8362": ("(8,3,0)R", "(6,2,-1/6)"), "U6362": ("(6,3,1/3)", "(6,2,-1/6)"), "U6381": ("(6,3,1/3)", "(8,1,0)R")}


def family(A, B, lmA_grid, M_s=1e13, y_s=0.336):
    rows = []
    for lmA in lmA_grid:
        mA = 10 ** lmA

        def d3(lmB):
            u = U.unify([(A, mA), (B, 10 ** lmB)], M_s=M_s, y_s=y_s)
            return float("nan") if u is None else u["d3"]
        grid = np.linspace(3.5, 16.8, 54); vals = [d3(x) for x in grid]
        for i in range(len(grid) - 1):
            if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0 and abs(vals[i] - vals[i + 1]) < 20:
                lmB = brentq(d3, grid[i], grid[i + 1], xtol=1e-7)
                p = U.point([(A, mA), (B, 10 ** lmB)], M_s=M_s, y_s=y_s)
                if p is None or p["M_U"] < max(mA, 10 ** lmB):
                    continue
                rows.append({"mA": mA, "mB": 10 ** lmB, **{k: p[k] for k in ("M_U", "aU", "A_R", "tau_lat", "tau_repo", "L2", "L3")}})
    return rows


if __name__ == "__main__":
    which = sys.argv[1:] or list(FAMS)
    out = {}
    for name in which:
        A, B = FAMS[name]
        res = {}
        for tag, Ms, ys in (("nominal", 1e13, 0.336), ("Ms5e12", 5e12, 0.336), ("Ms1.21e13_ys0.368", 1.21e13, 0.368)):
            rows = family(A, B, np.linspace(9.0, 14.0, 41) if name != "U6381" else np.linspace(9.5, 12.5, 31), Ms, ys)
            res[tag] = rows
            ok = [r for r in rows if r["tau_lat"] > 2.4e34 and r["L2"] > 1.0]
            print(f"{name} {tag}: {len(rows)} solutions, {len(ok)} with tau_lat > 2.4e34 and L2 > 1", flush=True)
            for r in rows:
                print(f"   mA={r['mA']:.3e} mB={r['mB']:.3e} MU={r['M_U']:.3e} aU={r['aU']:.2f} AR={r['A_R']:.2f} "
                      f"tau={r['tau_lat']:.2e} L2={r['L2']:.2f} L3={r['L3']:.2f}", flush=True)
        out[name] = res
    json.dump(out, open("unif_family_" + "_".join(which) + ".json", "w"), indent=1)
