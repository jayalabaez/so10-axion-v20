"""SKEPTIC D2: robustness of the required O5 size at the EXACT Clebsch over charged-sector basins (chain b, v_R = 1e16).
Fresh charged-sector fits (designer's d2_decoupled.fit_charged, read-only import) for several |rho| caps and DE seeds,
then the decoupled required coefficient Q = max|S| (sigma = 0) at TAU = (sqrt3-1)/5 with the neutrino observables allowed
to move by |pull| <= 1 and <= 2 (chi2_nu up to 5 / 20).  A chi2_total <= 25 with |S| <= 1 would need Q <= 1 at
chi2_13 + chi2_nu <= 25.  Output: sk_d2_basins.json
"""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import d2_targets as TG  # noqa: E402
import d2_decoupled as Dc  # noqa: E402

TAU = (math.sqrt(3) - 1) / 5
EPS = 0.024
vR = 1e16
tg = TG.gut_targets("b", floor=0.01)
out = {"TAU": TAU, "vR": vR, "rows": []}
t0 = time.time()
for rho_max in (20.0, 30.0, 50.0, 100.0, 300.0):
    for seed in (11, 12):
        x, c = Dc.fit_charged(tg, rho_max, seed, maxiter=1500)
        m = Dc.charged_mats(x, tg)
        row = {"rho_max": rho_max, "seed": seed, "chi2_13": c, "|rho|": abs(m["rho"]), "r": m["r"]}
        for pc in (1.0, 2.0):
            q = Dc.minimise_Q(m, tg, vR, tg["data"], TAU, EPS, seed=3, nstart=12, pull_cap=pc)
            row[f"Q_pull{pc:.0f}"] = q["Q"]; row[f"chi2_nu_pull{pc:.0f}"] = q["chi2_nu"]
        out["rows"].append(row)
        print(f"rho_max {rho_max:6.1f} seed {seed}: chi2_13 = {c:8.3f} |rho| = {abs(m['rho']):6.2f}  Q(pull<=1) = {row['Q_pull1']:.2f} "
              f"(chi2_nu {row['chi2_nu_pull1']:.2f})  Q(pull<=2) = {row['Q_pull2']:.2f} (chi2_nu {row['chi2_nu_pull2']:.2f})  t={time.time()-t0:.0f}s", flush=True)
        json.dump(out, open(HERE / "sk_d2_basins.json", "w"), indent=1)
print("done")
