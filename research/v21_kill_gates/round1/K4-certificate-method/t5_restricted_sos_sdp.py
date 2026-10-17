"""t5: restricted degree-3 SOS certificate attempt for the prototype 210-only potential at Phi0 = (p,a).

Ansatz:  h(Phi) (V(Phi) - V0) = sum_targets sum_{a,b} Q^tau_ab <s_a(Phi), s_b(Phi)>_tau ,  Q^tau >= 0,
         h = h0 + h1 I2,  h0 >= 1 (normalisation), h1 >= 0,
where the s_a are the vanishing covariant combinations (degree <= 3) of k4van for the targets 210, 45, 54+1, 1.
The polynomial identity is imposed at K random integer points (exact rational evaluation).  The SDP is solved
numerically (cvxpy/Clarabel).  Feasible -> candidate certificate (then exact rounding is attempted separately);
infeasible -> this restricted ansatz (small-irrep covariants only) cannot certify; the residual is reported.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
import cvxpy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4fast as F
import k4van as VN

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
KPTS = int(sys.argv[3]) if len(sys.argv) > 3 else 80
lab = f"p{P0}_a{A0}"
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
c_q = [Fraction(proto["couplings"][n]) for n in NAMES]
cf = tuple(float(x) for x in c_q)
phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
# drop redundant covariants (eps3x3x3, eps4x3x2 are proportional to MPhi as maps; F2 'chain' is identically zero)
import k4cov as C
VN.FAMILIES = {
    "F4": {n: v for n, v in C.F4_COVARIANTS.items() if n not in ("eps3x3x3", "eps4x3x2")},
    "F2": {n: v for n, v in C.F2_COVARIANTS.items() if n != "chain"},
    "S2": dict(C.S2_COVARIANTS), "SC": dict(C.SC_COVARIANTS)}


def V_exact(phi_int):
    vo = np.array([int(x) for x in phi_int], dtype=object)
    inv = K.invariants(vo)
    return sum(c * Fraction(inv[n]) for c, n in zip(c_q, NAMES))


V0 = V_exact(phi0_int)
print("V0 =", V0, float(V0), flush=True)

# vanishing combinations per target
combos = {}
for target in ("SC", "F2", "S2", "F4"):
    names, degs, alphas = VN.vanishing_combinations(target, phi0_int)
    combos[target] = (names, degs, alphas)
    print(target, "n_vanishing", len(alphas), [dict((n, a) for n, a in zip(names, al) if a) for al in alphas], flush=True)

# random integer evaluation points (sparse-ish to keep exact evaluation cheap but generic)
rng = np.random.default_rng(2024)
pts = []
for k in range(KPTS):
    v = rng.integers(-3, 4, size=210)
    mask = rng.random(210) < 0.35
    v = v * mask
    if np.count_nonzero(v) < 8:
        continue
    pts.append(v.astype(np.int64))
KPTS = len(pts)
# evaluate every covariant once per point, then form the combinations
S_vals = {}
for target, (names, degs, alphas) in combos.items():
    cov_pts = []
    for p in pts:
        T = C.dense(p)
        cov_pts.append({n: VN.flat(target, VN.FAMILIES[target][n][0](T)) for n in names})
    S_vals[target] = []
    for alpha in alphas:
        vals = []
        for cp_ in cov_pts:
            tot = None
            for n, a in zip(names, alpha):
                if a == 0:
                    continue
                tot = a * cp_[n] if tot is None else tot + a * cp_[n]
            vals.append(tot)
        S_vals[target].append(vals)
    print(target, "evaluated", f"[{time.time() - t0:.0f}s]", flush=True)
# Gram-product matrices G^tau_ab(k) = <s_a, s_b>(pt k) (exact ints) -> float for SDP
prod = {}
for target, (names, degs, alphas) in combos.items():
    n = len(alphas); w = VN.inner_weights(target)
    P = np.zeros((KPTS, n, n))
    for k in range(KPTS):
        for a in range(n):
            for b in range(a, n):
                val = sum(int(w[i]) * int(S_vals[target][a][k][i]) * int(S_vals[target][b][k][i]) for i in range(len(w)))
                P[k, a, b] = val; P[k, b, a] = val
    prod[target] = P
rhs_V = np.array([float(V_exact(p) - V0) for p in pts])
I2pts = np.array([float(p @ p) for p in pts])
# normalise scale: divide all by typical magnitude
scale = max(1.0, np.max(np.abs(rhs_V)))
Qs = {t: cp.Variable((len(combos[t][2]), len(combos[t][2])), PSD=True) for t in combos if len(combos[t][2]) > 0}
h0 = cp.Variable(); h1 = cp.Variable()
cons = [h0 >= 1.0, h1 >= 0.0]
resid = []
for k in range(KPTS):
    lhs = (h0 + h1 * I2pts[k]) * rhs_V[k] / scale
    rhs = 0
    for t, Q in Qs.items():
        rhs = rhs + cp.sum(cp.multiply(Q, prod[t][k] / scale))
    resid.append(lhs - rhs)
resid = cp.hstack(resid)
# phase 1: least-squares feasibility (minimise residual norm); exact feasibility iff optimum ~ 0
prob = cp.Problem(cp.Minimize(cp.norm(resid, 2) + 1e-6 * sum(cp.trace(Q) for Q in Qs.values())), cons)
prob.solve(solver=cp.CLARABEL)
res_norm = float(np.linalg.norm(resid.value))
out = {"point": [P0, A0], "V0": str(V0), "n_points": KPTS, "n_combos": {t: len(c[2]) for t, c in combos.items()},
       "status": prob.status, "residual_norm_scaled": res_norm, "residual_max_scaled": float(np.max(np.abs(resid.value))),
       "h0": float(h0.value), "h1": float(h1.value), "rhs_scale": scale,
       "Q_eigs": {t: np.linalg.eigvalsh(Q.value).tolist() for t, Q in Qs.items()}}
print(json.dumps(out, indent=1), flush=True)
# diagnostic: is h(V-V0) in the span of the products at all (ignoring PSD)?  Linear least squares.
cols = []
for t in Qs:
    n = prod[t].shape[1]
    for a in range(n):
        for b in range(a, n):
            cols.append(prod[t][:, a, b] * (1.0 if a == b else 2.0))
A = np.column_stack(cols + [-rhs_V, -rhs_V * I2pts])
sv = np.linalg.svd(A, compute_uv=False)
# solve A x = 0 with x_h0 = 1: least squares
x, res, rk, _ = np.linalg.lstsq(A[:, :-2], rhs_V, rcond=None)
out["span_test_residual_h1_0"] = float(np.linalg.norm(A[:, :-2] @ x - rhs_V) / np.linalg.norm(rhs_V))
x2, res2, rk2, _ = np.linalg.lstsq(np.column_stack([A[:, :-2], -rhs_V * I2pts]), rhs_V, rcond=None)
out["span_test_residual_free_h1"] = float(np.linalg.norm(np.column_stack([A[:, :-2], -rhs_V * I2pts]) @ x2 - rhs_V) / np.linalg.norm(rhs_V))
out["design_rank"] = int(rk), "n_product_columns", len(cols)
print("span test (no PSD): residual with h=1:", out["span_test_residual_h1_0"], " with h=1+h1 I2:", out["span_test_residual_free_h1"], "rank", rk, "/", len(cols), flush=True)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, f"t5_restricted_sos_{lab}.json"), "w"), indent=1, default=str)
