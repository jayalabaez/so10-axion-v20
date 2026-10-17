"""SKEPTIC (R2-A): SM-singlet / Delta_R subspace screen at a coupling point (own implementation of the gate's idea).

V_c restricted to z = (p, a, omega, r_sigma, r_DeltaR, s, x) is a polynomial; it is fitted EXACTLY from the stored
subspace banks (smsinglet_pts.npz: r_DeltaR = 0; deltar_pts.npz) and minimised from 40000 random starts + polish.
Every candidate lower point (outside the G3221 orbit of z*) is re-evaluated with the exact operator values (J_at path).
usage: python -B sk_screen.py <solution npz in skeptic/> <tag>
"""
import sys, json, math, itertools, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import k3_common as K  # noqa: E402

solf, tag = sys.argv[1], sys.argv[2]
sol = np.load(HERE / solf if (HERE / solf).exists() else PARENT / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
SUB = np.load(HERE / "subdirs.npz")["D"]
meta = json.load(open(PARENT / f"{tag}_rows_meta.json"))["point"]
zstar = np.array([meta["p"], meta["a"], meta["omega"], meta["r"], 0.0, meta["s"], meta["x"]])
Vstar_rows = float(c @ np.load(PARENT / f"{tag}_rows.npz")["values"])
chart = K.chart; pot = K.potential


def J_from_values(vals, dids):
    di = {d: j for j, d in enumerate(dids)}; J = np.zeros((vals.shape[0], len(ids)))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = di[did]
        J[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return J


def J_at(q):
    jac = pot.coefficient_jacobian(pot.evaluate_directions(chart.unpack(q).validated())); return np.array([float(np.real(jac[p])) for p in ids])


def q_of_z(z):
    return sum(zi * d for zi, d in zip(z, SUB))


def in_orbit(z):
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-3 and abs(abs(z[1]) - abs(zstar[1])) < 2e-3 and abs(z[2]) < 2e-3
            and abs(z[6] - zstar[6]) < 2e-2 and math.hypot(z[3], z[4]) < 0.02)


out = {"solution": solf, "tag": tag, "V_star_rows": Vstar_rows, "fits": []}
rng = np.random.default_rng(11)
for fn, mode in (("smsinglet_pts.npz", "smsinglet"), ("deltar_pts.npz", "deltar")):
    b = np.load(PARENT / fn); Q = b["Q"]; J = J_from_values(b["values"], [str(x) for x in b["ids"]])
    Z = np.array([[float(q @ d) / float(d @ d) for d in SUB] for q in Q])
    recon = np.max(np.abs(np.array([q_of_z(z) for z in Z]) - Q))
    degs = [1, 1, 1, 2, 2, 2] if mode == "smsinglet" else [1, 1, 1, 2, 2, 2, 2]
    def var(z):
        z = np.atleast_2d(z)
        if mode == "smsinglet": return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
        return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 4] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
    monos = np.array([pw for pw in itertools.product(range(5), repeat=len(degs)) if sum(p * d for p, d in zip(pw, degs)) <= 4])
    X = lambda zs: np.prod(var(zs)[:, None, :] ** monos[None, :, :], axis=2)
    XA = X(Z); Vb = J @ c; coef, *_ = np.linalg.lstsq(XA, Vb, rcond=None); resid = float(np.max(np.abs(XA @ coef - Vb)))
    Vz = lambda z: float(X(np.asarray(z)[None, :])[0] @ coef)
    Vst = Vz(zstar)
    n = 40000
    zs = np.column_stack([rng.uniform(-2, 2, (n, 3)), rng.uniform(-2, 2, (n, 2)), rng.uniform(-1.5, 1.5, (n, 1)), rng.uniform(-7, 7, (n, 1))])
    if mode == "smsinglet": zs[:, 4] = 0
    vs = X(zs) @ coef; order = np.argsort(vs)[:30]
    found = []
    for j in list(order) + [None]:
        z0 = zstar if j is None else zs[j]
        r = minimize(Vz, z0, method="BFGS", options={"gtol": 1e-10, "maxiter": 600})
        zz = np.array(r.x)
        if mode == "smsinglet": zz[4] = 0
        found.append((float(r.fun), zz))
    found.sort(key=lambda t: t[0])
    lower = [(v, z) for v, z in found if v < Vst - 1e-9 * max(1, abs(Vst)) and not in_orbit(z) and np.max(np.abs(z)) < 30]
    runaway = [(v, z) for v, z in found if np.max(np.abs(z)) >= 30]
    exact = []
    for v, z in lower[:3]:
        Ve = float(c @ J_at(q_of_z(z))); exact.append({"z": z.tolist(), "V_fit-V*": v - Vst, "V_exact-V*": Ve - Vstar_rows})
    rec = {"mode": mode, "n_bank": int(len(Q)), "chart_reconstruction_err": float(recon), "fit_residual": resid, "rank": int(np.linalg.matrix_rank(XA)), "n_monomials": int(len(monos)),
           "V_star_fit": Vst, "V_star_rows": Vstar_rows, "lowest_found-V*": found[0][0] - Vst, "argmin": found[0][1].tolist(),
           "argmin_in_orbit": bool(in_orbit(found[0][1])), "n_lower_non_orbit": len(lower), "n_runaway": len(runaway), "exact_checks": exact}
    out["fits"].append(rec); print(json.dumps(rec, default=float), flush=True)
json.dump(out, open(HERE / f"screen_{Path(solf).stem}.json", "w"), indent=1, default=float)
