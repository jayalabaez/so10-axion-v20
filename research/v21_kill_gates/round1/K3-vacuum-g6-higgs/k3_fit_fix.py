"""Re-evaluate the exact SM-singlet-subspace polynomial of V_c at the TRUE G3221 point of each solution
(the previous k3_subspace_fit.py hard-coded the A45 point (p,a)=(+,+) as reference while screening Am45 solutions).
usage: python -B k3_fit_fix.py <points npz> <solution npz> <mode> [p a om r s x]
"""
from __future__ import annotations
import sys, json, itertools, numpy as np
from scipy.optimize import minimize
import k3_common as K
pts = np.load(K.SCRATCH / sys.argv[1]); sol = np.load(K.SCRATCH / sys.argv[2]); mode = sys.argv[3]
meta = json.load(open(K.SCRATCH / "Am45_rows_meta.json"))["point"]
zs = [float(v) for v in sys.argv[4:10]] if len(sys.argv) > 4 else [meta["p"], meta["a"], meta["omega"], meta["r"], meta["s"], meta["x"]]
Q = pts["Q"]; vals = pts["values"]; dids = [str(x) for x in pts["ids"]]; c = sol["c"]; ids = [str(x) for x in sol["ids"]]
chart = K.chart; basis = K.direct.singlet_basis()
def pk(**kw):
    d = dict(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=0j); d.update(kw); return chart.pack(K.potential.FieldState(**d))
Pv, Av, Ov = pk(phi=basis["p"]), pk(phi=basis["a"]), pk(phi=basis["omega"])
Sv = pk(sigma=chart.sigma_from_coordinates(K.candidate.sigma_std_unit_coordinates()))
drc = chart.sigma_coordinates(K.direct.delta_r()); drc /= np.linalg.norm(drc); Dv = pk(sigma=chart.sigma_from_coordinates(drc))
Sc = pk(s=1 + 0j); Xc = pk(x=1 + 0j)
dirs = [Pv, Av, Ov, Sv, Dv, Sc, Xc]
coords = np.array([[float(q @ d) / float(d @ d) for d in dirs] for q in Q])
if mode == "smsinglet":
    var = lambda z: np.array([z[0], z[1], z[2], z[3] ** 2, z[5] ** 2, z[6] ** 2]); degs = [1, 1, 1, 2, 2, 2]
else:
    var = lambda z: np.array([z[0], z[1], z[2], z[3] ** 2, z[4] ** 2, z[5] ** 2, z[6] ** 2]); degs = [1, 1, 1, 2, 2, 2, 2]
monos = [pw for pw in itertools.product(range(5), repeat=len(degs)) if sum(p * d for p, d in zip(pw, degs)) <= 4]
Xmat = np.array([[np.prod(var(z) ** np.array(m)) for m in monos] for z in coords])
dindex = {d: j for j, d in enumerate(dids)}; Vvals = np.zeros(len(Q))
for i, pid in enumerate(ids):
    comp, did = pid.split("::"); j = dindex[did]
    Vvals += c[i] * (vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag))
coef, res, rk, sv = np.linalg.lstsq(Xmat, Vvals, rcond=None)
fitres = float(np.max(np.abs(Xmat @ coef - Vvals)))
def Vpoly(z): v = var(z); return float(sum(cf * np.prod(v ** np.array(m)) for cf, m in zip(coef, monos)))
# true reference point in the 7-vector convention (p, a, om, r1, r2, s, x)
zstar = np.array([zs[0], zs[1], zs[2], zs[3], 0.0, zs[4], zs[5]])
Vstar = Vpoly(zstar)
# the exact V at the chart point from the stored rows (independent check)
Z = np.load(K.SCRATCH / "Am45_rows.npz"); V_rows = float(np.dot(c, Z["values"]))
grad_poly = np.array([(Vpoly(zstar + 1e-6 * e) - Vpoly(zstar - 1e-6 * e)) / 2e-6 for e in np.eye(7)])
rng = np.random.default_rng(7); best = []
for trial in range(3000):
    z0 = np.concatenate([rng.uniform(-1.5, 1.5, 3), rng.uniform(0, 1.5, 2), rng.uniform(0, 1.5, 1), rng.uniform(0, 6, 1)])
    r = minimize(Vpoly, z0, method="BFGS", options={"gtol": 1e-10, "maxiter": 3000}); best.append((r.fun, r.x))
best.sort(key=lambda t: t[0])
lower = [b for b in best if b[0] < Vstar - 1e-9 * max(1, abs(Vstar))]
# cluster the distinct minima among the lowest 300
clusters = []
for f, z in best[:300]:
    key = (round(abs(z[0]), 2), round(abs(z[1]), 2), round(abs(z[2]), 2), round(z[3] ** 2, 4), round(z[4] ** 2, 4), round(z[6] ** 2, 2))
    if not any(abs(f - cf) < 1e-6 * max(1, abs(f)) and ck[:3] == key[:3] for cf, ck, _ in clusters): clusters.append((f, key, z))
out = {"solution": sys.argv[2], "mode": mode, "fit_residual": fitres, "zstar": zstar.tolist(), "V_star_poly": Vstar, "V_star_rows": V_rows,
       "grad_poly_at_zstar": grad_poly.tolist(), "V_min_subspace": best[0][0], "argmin": best[0][1].tolist(), "n_lower_of_3000": len(lower),
       "distinct_lowest": [{"V": f, "z": z.tolist()} for f, _, z in clusters[:8]]}
print(json.dumps({k: v for k, v in out.items() if k != "distinct_lowest"}, indent=None))
for f, _, z in clusters[:8]: print(f"   V = {f:.6f}  z = {np.array2string(z, precision=4)}")
json.dump(out, open(K.SCRATCH / f"fitfix_{mode}_{sys.argv[2].replace('.npz','')}.json", "w"), indent=1)
