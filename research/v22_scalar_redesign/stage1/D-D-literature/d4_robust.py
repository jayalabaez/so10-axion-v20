#!/usr/bin/env python3
"""D4 robustness: nominal points and a threshold Monte Carlo for the three designs (d4_unif.py machinery).
Samples (EST ranges, R2-B-like): every heavy scalar SM multiplet x [1/2, 2] (log-uniform, independent),
heavy vectors (3,1,2/3), W_R, Z' at [0.4, 1.2] x M_X, M_s in [3e12, 1.21e13], y_s in [0.304, 0.368];
the first light state is held at M_8 (grid), the second is solved for.  Pass = tau_lat(A_R chain) > 2.4e34 yr and
Lambda_2L > M_Pl,red; the three-loop scale is recorded (not a D4 criterion)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d4_unif as U  # noqa: E402

DESIGNS = {
    "L1_BOP_v20": (("210", "126b", "10"), ["(8,1,0)", "(8,3,0)"]),
    "L2_BOP_plus45": (("210", "126b", "10", "45"), ["(8,1,0)", "(8,3,0)"]),
    "L3p_45_54_no210": (("45", "54", "126b", "10"), ["(8,1,0)", "(6,3,1/3)"]),
}


def nominal(so10, names, m8):
    r = U.point(names, [m8, 1e9], 1, so10=so10)
    if r is None:
        return None
    L = U.landau(r["M_U"], r["alpha_U_inv"], so10)
    return {"M8": m8, "M_second": r["M_light"][1], "M_U": r["M_U"], "aU_inv": r["alpha_U_inv"],
            "tau_lat": float(r["tau_lat_yr"]), "A_R": float(r["A_R"]), "L2": L["L2"], "L3": L["L3"], "b_so10": L["b_so10"]}


def mc(so10, names, m8, n=60, seed=7):
    rng = np.random.default_rng(seed)
    ch0 = U.Chain1([U.CAT[x] for x in names], [m8, 1e9], so10_scalars=so10)
    keys = sorted(set(U.key(p[0], p[1], p[2]) for p in ch0.heavy))
    rows = []
    for i in range(n):
        hr = {k: float(math.exp(rng.uniform(math.log(0.5), math.log(2.0)))) for k in keys}
        vr = {"V3": float(rng.uniform(0.4, 1.2)), "WR": float(rng.uniform(0.4, 1.2)), "Zp": float(rng.uniform(0.4, 1.2))}
        Ms = float(math.exp(rng.uniform(math.log(3e12), math.log(1.21e13))))
        ys = float(rng.uniform(0.304, 0.368))
        r = U.point(names, [m8, 1e9], 1, so10=so10, M_s=Ms, y_s=ys, heavy_ratios=hr, vec_ratios=vr)
        if r is None:
            rows.append(None)
            continue
        L = U.landau(r["M_U"], r["alpha_U_inv"], so10, M_s=Ms, y_s=ys)
        rows.append({"M_U": r["M_U"], "aU_inv": r["alpha_U_inv"], "tau": float(r["tau_lat_yr"]), "L2": L["L2"],
                     "L3": L["L3"], "M2": r["M_light"][1]})
    ok = [z for z in rows if z]
    frac = lambda f: sum(1 for z in ok if f(z)) / max(len(ok), 1)
    return {"n": n, "n_solved": len(ok), "frac_tau": frac(lambda z: z["tau"] > 2.4e34),
            "frac_L2": frac(lambda z: z["L2"] > 1.0), "frac_D4": frac(lambda z: z["tau"] > 2.4e34 and z["L2"] > 1.0),
            "frac_L3": frac(lambda z: z["L3"] > 1.0),
            "tau_min_max": [min(z["tau"] for z in ok), max(z["tau"] for z in ok)] if ok else None,
            "L2_min_max": [min(z["L2"] for z in ok), max(z["L2"] for z in ok)] if ok else None,
            "aU_min_max": [min(z["aU_inv"] for z in ok), max(z["aU_inv"] for z in ok)] if ok else None,
            "M2_min_max": [min(z["M2"] for z in ok), max(z["M2"] for z in ok)] if ok else None}


def main():
    out = {}
    for name, (so10, names) in DESIGNS.items():
        rec = {"light": names, "so10": so10, "nominal": {}, "mc": {}}
        for m8 in (1e3, 1e4, 1e5):
            rec["nominal"][f"{m8:.0e}"] = nominal(so10, names, m8)
            print(name, "nominal", f"{m8:.0e}", rec["nominal"][f"{m8:.0e}"], flush=True)
        for m8 in (1e3, 1e4):
            rec["mc"][f"{m8:.0e}"] = mc(so10, names, m8)
            print(name, "MC", f"{m8:.0e}", rec["mc"][f"{m8:.0e}"], flush=True)
        out[name] = rec
    (HERE / "d4_robust.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
