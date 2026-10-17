"""Fit the restriction of every direction value to a low-dimensional vev subspace as a polynomial, then
minimise V = sum c_i D_i over the subspace from many random starts (global screening within the subspace).

usage: python -B k3_subspace_fit.py <points npz from k3_eval_points> <solution npz (c, ids)> <mode: smsinglet|deltar>
Variables: smsinglet -> (p, a, om, R=r^2, S2=s^2, X2=x^2); deltar -> (p, a, om, R1, R2, S2, X2).
Monomials: total weighted degree <= 4 with deg(p,a,om)=1, deg(R..)=2.
"""
from __future__ import annotations
import sys, json, itertools, math, numpy as np
from scipy.optimize import minimize
import k3_common as K

pts = np.load(K.SCRATCH / sys.argv[1]); sol = np.load(K.SCRATCH / sys.argv[2]) if not sys.argv[2].startswith("/") else np.load(sys.argv[2])
mode = sys.argv[3]
Q = pts["Q"]; vals = pts["values"]; dids = [str(x) for x in pts["ids"]]
c = sol["c"]; ids = [str(x) for x in sol["ids"]]
chart = K.chart
# recover subspace coordinates from Q
basis = K.direct.singlet_basis()
Pv = chart.pack(K.potential.FieldState(phi=basis["p"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))
Av = chart.pack(K.potential.FieldState(phi=basis["a"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))
Ov = chart.pack(K.potential.FieldState(phi=basis["omega"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))
sig = chart.sigma_from_coordinates(K.candidate.sigma_std_unit_coordinates()); Sv = chart.pack(K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma=sig, s=0j, x=0j))
drc = chart.sigma_coordinates(K.direct.delta_r()); drc /= np.linalg.norm(drc); Dv = chart.pack(K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma=chart.sigma_from_coordinates(drc), s=0j, x=0j))
Sc = chart.pack(K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma={}, s=1 + 0j, x=0j))
Xc = chart.pack(K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=1 + 0j))
dirs = [Pv, Av, Ov, Sv, Dv, Sc, Xc]
names = ["p", "a", "om", "r1", "r2", "s", "x"]
coords = np.array([[float(q @ d) / float(d @ d) for d in dirs] for q in Q])
resid = np.max(np.abs(Q - coords @ np.array(dirs)))
print("subspace reconstruction residual:", resid)
if mode == "smsinglet":
    var = lambda z: np.array([z[0], z[1], z[2], z[3] ** 2, z[5] ** 2, z[6] ** 2])
    vnames = ["p", "a", "om", "R", "S2", "X2"]; degs = [1, 1, 1, 2, 2, 2]
else:
    var = lambda z: np.array([z[0], z[1], z[2], z[3] ** 2, z[4] ** 2, z[5] ** 2, z[6] ** 2])
    vnames = ["p", "a", "om", "R1", "R2", "S2", "X2"]; degs = [1, 1, 1, 2, 2, 2, 2]
nv = len(vnames)
monos = []
for powers in itertools.product(range(5), repeat=nv):
    if sum(pw * d for pw, d in zip(powers, degs)) <= 4: monos.append(powers)
print(f"{len(monos)} monomials, {len(Q)} points")
Xmat = np.array([[np.prod(var(z) ** np.array(m)) for m in monos] for z in coords])
# V values at the points for the coupling vector c: V = sum_i c_i * jac_i(direction values)
pid_to_dir = {p: p.split("::")[1] for p in ids}
Vvals = np.zeros(len(Q)); contrib = {}
dindex = {d: j for j, d in enumerate(dids)}
for i, pid in enumerate(ids):
    j = dindex[pid_to_dir[pid]]; comp = pid.split("::")[0]
    if comp == "lambda": Vvals += c[i] * vals[:, j].real
    elif comp == "re": Vvals += c[i] * 2 * vals[:, j].real
    else: Vvals += c[i] * (-2) * vals[:, j].imag
coef, res, rk, sv = np.linalg.lstsq(Xmat, Vvals, rcond=None)
fit = Xmat @ coef
print(f"fit rank {rk}/{len(monos)}, max |residual| = {np.max(np.abs(fit - Vvals)):.3e}, |V| scale = {np.max(np.abs(Vvals)):.3e}")


def Vpoly(z):
    v = var(z); return float(sum(cf * np.prod(v ** np.array(m)) for cf, m in zip(coef, monos)))


# reference: the G3221 point
zstar = np.array([0.70710678, 0.70710678, 0.0, 1.2e-3, 0.0, 1.6e-3, 4.0])
# locate the actual minimum near zstar
def obj(z): return Vpoly(z)
loc = minimize(obj, zstar, method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 20000})
print("V(zstar) =", Vpoly(zstar), " local min near zstar:", loc.fun, "at", np.round(loc.x, 5))
rng = np.random.default_rng(7)
best = []
for trial in range(4000):
    z0 = np.concatenate([rng.uniform(-1.5, 1.5, 3), rng.uniform(0, 1.5, 2), rng.uniform(0, 1.5, 1), rng.uniform(0, 6, 1)])
    r = minimize(obj, z0, method="BFGS", options={"gtol": 1e-10, "maxiter": 2000})
    best.append((r.fun, r.x))
best.sort(key=lambda t: t[0])
print("lowest 8 minima found in the subspace:")
for f, z in best[:8]: print(f"  V = {f:.6e}  at {np.round(z, 4)}")
vstar = Vpoly(zstar)
lower = [b for b in best if b[0] < vstar - 1e-9 * max(1, abs(vstar))]
print(f"V* = {vstar:.6e};  points lower than V*: {len(lower)} of {len(best)}; global-in-subspace min = {best[0][0]:.6e}")
json.dump({"mode": mode, "n_points": len(Q), "n_monomials": len(monos), "fit_residual": float(np.max(np.abs(fit - Vvals))),
           "V_star": vstar, "V_min_subspace": best[0][0], "argmin": best[0][1].tolist(), "n_lower": len(lower),
           "lowest": [{"V": f, "z": z.tolist()} for f, z in best[:10]]},
          open(K.SCRATCH / f"subspace_fit_{mode}_{sys.argv[2].split('/')[-1].replace('.npz','')}.json", "w"), indent=1)
