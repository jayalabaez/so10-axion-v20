#!/usr/bin/env python3
"""SKEPTIC D4 check 2 (NUM): two-loop unification + proton decay WITH THE DESIGNER'S OWN FINAL-POINT SPECTRUM (L6) instead
of 'every heavy state at M_U'.

* Heavy vectors: M_V^2 = g_U^2 eig[(1/2) T^T T], T = repo gauge_orbit_matrix at q* (canonical chart, K = q.q/2; the
  generators L_ab of the chart have index 2 in the 10, so t = L/sqrt2 has T(10) = 1, the GUT normalisation).  SM labels
  from the hypercharge found as the centre of the massless subalgebra (ad_Y^2 eigenvalues, normalised to max 1).
* Heavy scalars: the L6 SM-block eigenvalues (designer's post_L6 json = exact compiler rows); Goldstones (0) removed;
  the tuned light states ((8,3), (6,2)_1/6, the doublet, the S radial mode) are removed and run explicitly.
* One-loop matching at M_ref = M_X(3,2,5/6):  alpha_i^-1(M_ref)|EFT = alpha_U^-1 + D_i,
     D_i = -(1/12 pi) [ sum_V S_i(V) (1 - 21 ln(M_V/M_ref)) + sum_S eta S_i(S) ln(M_S/M_ref) ],  eta = 2 complex, 1 real.
* EFT running: own two-loop code (sk_unif.run) with SM + B63 + (8,3,0) at m8 + (6,2,-1/6) at m6.
* tau(p -> e+ pi0), lattice W0 = 0.131, non-degenerate X, X':  C(e^c,d) = 2 k1^2 (1+|Vud|^2), C(e,d^c) = 2 (k1^2 + k2^2 |Vud|^2).
usage: python -B sk_thresh.py
"""
import json, math, itertools
import numpy as np
from scipy.optimize import brentq
import sk_loader as LD
import sk_unif as U

PI = math.pi
meta = json.load(open(LD.VAC / "S2_rows_meta.json"))["point"]
st = LD.build_state(meta["p"], meta["a"], meta["omega"], meta["r"], meta["s"], meta["x"])
T = LD.chart.gauge_orbit_matrix(st)                  # 486 x 45
MV = 0.5 * T.T @ T                                   # M_V^2 / g^2
gens = []
for a, b in itertools.combinations(range(10), 2):
    L = np.zeros((10, 10)); L[a, b] = 1.0; L[b, a] = -1.0; gens.append(L)
gens = np.array(gens)
wv, Av = np.linalg.eigh(MV)
zero = np.where(wv < 1e-10)[0]
assert len(zero) == 12, wv[:14]
Xs = np.einsum("kn,kij->nij", Av[:, zero], gens)    # massless generators (12)
# hypercharge = centre of the massless algebra
rows = []
for j in range(12):
    rows.append(np.array([(Xs[k] @ Xs[j] - Xs[j] @ Xs[k]).ravel() for k in range(12)]).T)
Msys = np.vstack(rows)
_, sv, vt = np.linalg.svd(Msys)
ycoef = vt[-1]; assert sv[-1] < 1e-9 and sv[-2] > 1e-6, sv[-3:]
Y = np.einsum("k,kij->ij", ycoef, Xs)
# ad_Y^2 on the adjoint (basis gens, Frobenius metric: gens orthogonal with norm^2 2)
adY = np.array([[np.sum(gens[m] * (Y @ gens[n] - gens[n] @ Y)) / 2.0 for n in range(45)] for m in range(45)])
adY2 = adY @ adY
# simultaneous diagonalisation (they commute): diagonalise MV + tiny * adY2
comm = np.max(np.abs(MV @ adY2 - adY2 @ MV))
w2, V2 = np.linalg.eigh(MV + 1e-3 * adY2 / max(1e-30, np.max(np.abs(adY2))))
mv = np.array([V2[:, n] @ MV @ V2[:, n] for n in range(45)]); y2 = np.array([-(V2[:, n] @ adY2 @ V2[:, n]) for n in range(45)])
heavy = mv > 1e-10
y2 = y2 / np.max(y2[heavy])
groups = {}
for m, yy in zip(mv[heavy], y2[heavy]):
    key = (round(m, 8), round(yy * 36))
    groups[key] = groups.get(key, 0) + 1
vec_list = []
LAB = {25: ("(3,2,5/6)", 3, 2, 5 / 6), 1: ("(3,2,1/6)", 3, 2, 1 / 6), 16: ("(3,1,2/3)", 3, 1, 2 / 3), 36: ("(1,1,1)", 1, 1, 1.0), 0: ("(1,1,0)", 1, 1, 0.0)}
for (m, y36), n in sorted(groups.items()):
    lab = LAB[y36]
    vec_list.append({"label": lab[0], "M2_over_g2": m, "real_dof": n, "d3": lab[1], "d2": lab[2], "Y": lab[3]})
print("commutator |[MV, adY2]| =", comm)
for v in vec_list:
    print("vector", v)
# scalar spectrum at L6
post = json.load(open(LD.VAC / "post_L6_S2_U8362e_R.json"))["blocks"]
bm = {b["label"]: b for b in json.load(open(LD.VAC / "S2_blocks.json"))["blocks"]}
sc_list = []
for lab, eigs in post.items():
    d3, d2 = [int(x) for x in lab.split(")")[0][1:].split(",")]
    y = eval(lab.split("=")[1])
    ctype = bm[lab]["ctype"]
    for e in eigs:
        if abs(e) < 1e-9:
            continue                                  # Goldstone
        if e < 1e-4:
            continue                                  # tuned light states: run explicitly / irrelevant singlet
        sc_list.append({"label": lab, "m2": e, "d3": d3, "d2": d2, "Y": y, "eta": 2 if ctype == 2 else 1})
print("n heavy scalar multiplets:", len(sc_list), " m2 range:", min(s["m2"] for s in sc_list), max(s["m2"] for s in sc_list))


def S_of(d3, d2, y):
    S, _ = U.rep(d3, d2, y)
    return np.array(S)


def Delta(gU):
    """threshold vector D_i at M_ref = M_X(3,2,5/6), for gauge coupling gU (scalar/vector mass ratio depends on it)."""
    mX2 = [v["M2_over_g2"] for v in vec_list if v["label"] == "(3,2,5/6)"][0]
    D = np.zeros(3)
    for v in vec_list:
        npair = v["real_dof"] / (2 * v["d3"] * v["d2"]) if v["Y"] != 0 else 0   # complex vector multiplets r + rbar
        Sv = 2 * S_of(v["d3"], v["d2"], v["Y"]) * npair
        D += Sv * (1 - 21 * 0.5 * math.log(v["M2_over_g2"] / mX2))
    for s in sc_list:
        lnr = 0.5 * math.log(s["m2"] / (gU ** 2 * mX2))
        D += s["eta"] * S_of(s["d3"], s["d2"], s["Y"]) * lnr
    return -D / (12 * PI), mX2


def solve_point(m8, m6, aU_guess=26.0):
    aU = aU_guess
    for _ in range(30):
        D, mX2 = Delta(math.sqrt(4 * PI / aU))
        segs = U.run(m8, m6)
        f = lambda t: (U.at(segs, t)[0] - D[0]) - (U.at(segs, t)[1] - D[1])
        ts = np.linspace(math.log(1e13), math.log(2.9e18), 200); v = [f(t) for t in ts]
        root = None
        for i in range(len(ts) - 1):
            if v[i] * v[i + 1] < 0:
                root = brentq(f, ts[i], ts[i + 1], xtol=1e-13); break
        if root is None:
            return None
        Yv = U.at(segs, root); a = Yv[:3] - D
        new = float(a[1])
        if abs(new - aU) < 1e-9:
            break
        aU = new
    return {"M_X": math.exp(root), "aU": aU, "d3": float(a[2] - a[1]), "A_SD": math.sqrt(0.5 * (math.exp(2 * Yv[3]) + math.exp(2 * Yv[4]))),
            "D": D.tolist(), "mX2_over_g2": mX2}


def tau_nd(MX, MXp, aU, AR, W0=0.131, Vud=0.97367):
    mp, mpi = 0.93827208816, 0.1349768; hbar = 6.582119569e-25; yr = 3.15576e7
    g2 = 4 * PI / aU; k1 = g2 / (2 * MX ** 2); k2 = g2 / (2 * MXp ** 2)
    C1 = 2 * k1 * (1 + Vud ** 2); C2 = 2 * (k1 + k2 * Vud ** 2)
    G = mp / (32 * PI) * (1 - (mpi / mp) ** 2) ** 2 * AR ** 2 * W0 ** 2 * (C1 ** 2 + C2 ** 2)
    return hbar / G / yr


out = {"vectors": vec_list, "commutator": comm, "n_heavy_scalars": len(sc_list)}
mX2 = [v["M2_over_g2"] for v in vec_list if v["label"] == "(3,2,5/6)"][0]
mXp2 = [v["M2_over_g2"] for v in vec_list if v["label"] == "(3,2,1/6)"][0]
out["MXp_over_MX"] = math.sqrt(mXp2 / mX2)
D_deg, _ = Delta(math.sqrt(4 * PI / 26.0))
out["Delta_at_aU26"] = D_deg.tolist(); out["Delta_designer_degenerate"] = (-np.array([8, 6, 5]) / (12 * PI)).tolist()
print("Delta (L6 spectrum, aU=26):", D_deg, " designer (all at M_U):", -np.array([8, 6, 5]) / (12 * PI))
fam = []
for lm8 in np.linspace(10.0, 12.5, 11):
    def g(lm6):
        p = solve_point(10 ** lm8, 10 ** lm6)
        return float("nan") if p is None else p["d3"]
    grid = np.linspace(3.0, 15.5, 26); vals = [g(x) for x in grid]
    for i in range(len(grid) - 1):
        if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0 and abs(vals[i] - vals[i + 1]) < 5:
            lm6 = brentq(g, grid[i], grid[i + 1], xtol=1e-6)
            p = solve_point(10 ** lm8, 10 ** lm6)
            AR = 1.25 * p["A_SD"]; MXp = p["M_X"] * out["MXp_over_MX"]
            tau = tau_nd(p["M_X"], MXp, p["aU"], AR)
            L2, _ = U.landau(p["M_X"], p["aU"])
            row = {"m8": 10 ** lm8, "m6": 10 ** lm6, "M_X": p["M_X"], "M_Xp": MXp, "aU": p["aU"], "A_R": AR, "tau": tau, "L2": L2,
                   "Phi_vev_GeV": p["M_X"] / math.sqrt(4 * PI / p["aU"] * mX2)}
            fam.append(row)
            print("  " + " ".join(f"{k}={v:.3e}" for k, v in row.items()), flush=True)
            break
out["family"] = fam
json.dump(out, open(LD.HERE / "sk_thresh.json", "w"), indent=1, default=float)
