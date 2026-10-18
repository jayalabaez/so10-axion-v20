"""D2 sensitivity of the required O5 size max|S| (decoupled inversion, sigma = 0, TAU_eff = 5, eps = 0.0113, chain a,
|rho| = 30 seed) to (i) fixing delta_PMNS at the NuFIT 6.0 NO value 212 deg (+-35), (ii) the light-doublet 126bar
fraction (c_d126 = f c_max, f < 1), at v_R = 1e15 and 1e16."""
import json, math
import numpy as np
from scipy.optimize import minimize
import d2_targets as TG
import d2_decoupled as Dc

D = json.load(open("fits/decoupled_a.json", encoding="utf-8"))
tg = TG.gut_targets("a", floor=D["floor"])
row = D["stage1"]["30.0"][0]
m = Dc.charged_mats(np.array(row["x"]), tg)
cmax = math.sqrt(0.9 / (1 + abs(m["rho"]) ** 2))
out = {}
for vR in (1e15, 1e16):
    for dfix in (None, 212.0, 177.0, 247.0):
        for f in (0.98, 0.5, 0.2):
            rng = np.random.default_rng(5)
            best = 1e18; arg = None
            lcd = math.log(f / (1 - f))
            def fun(z):
                d = math.radians(dfix) if dfix is not None else z[3]
                y = np.concatenate([[z[0], z[1], z[2], d], np.clip(z[4:9], -1, 1)])
                q, _ = Dc.Q_of(m, tg, vR, y, lcd, tg["data"], 5.0, 0.0113)
                return q
            for k in range(25):
                z0 = np.array([rng.uniform(-4.5, -1.3), rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)] + list(rng.uniform(-.5, .5, 5)))
                r = minimize(fun, z0, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-9, fatol=1e-12))
                if r.fun < best:
                    best, arg = r.fun, r.x
            key = f"vR={vR:.0e},delta={'free' if dfix is None else dfix},f={f}"
            out[key] = {"required_max|S|(TAU=5)": best, "m1_eV": 10 ** arg[0], "nu_pulls": np.clip(arg[4:9], -1, 1).tolist()}
            print(key, round(best, 3), flush=True)
json.dump(out, open("fits/d2_sens.json", "w", encoding="utf-8"), indent=1)
