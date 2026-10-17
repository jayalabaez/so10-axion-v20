"""t3: degree-3 flat-mode test at the G3221 point Phi0 = p P + a A (exact integer arithmetic).

For each target irrep (4-forms=210, 2-forms=45, symmetric traceless=54, scalars=1) we take the explicit
covariants C_i (degree <= 3), evaluate at Phi0, find all combinations alpha with sum alpha_i C_i(Phi0) = 0
(these polynomials vanish on the whole orbit O = SO(10).Phi0), and compute the span W3 of their gradients at
Phi0.  Any SOS certificate  h (V - V0) = sum s_k^2  with deg s_k <= 3 has  rank Hess <= dim W3, so
flat modes >= (210 - dim O) - dim W3.  We also check the completeness of the explicit families against the
exact Sym^3 multiplicities (210:5, 45:2, 54:1, 1:1) by rank at random integer points.
"""
import json, os, sys, time
import numpy as np
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4cov as C

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 1)
lab = f"p{P0}_a{A0}"
out = {"point": [P0, A0]}


def flat(target, X):
    if target == "F4":
        return C.from_dense(X).astype(np.int64)
    if target == "F2":
        return np.array([X[i, j] for (i, j) in K.TWO], dtype=np.int64)
    if target == "S2":
        return np.array([X[i, j] for i in range(10) for j in range(i, 10)], dtype=np.int64)
    return np.array([X], dtype=np.int64)


FAMILIES = {"F4": C.F4_COVARIANTS, "F2": C.F2_COVARIANTS, "S2": C.S2_COVARIANTS, "SC": C.SC_COVARIANTS}
EXPECTED_SYM3 = {"F4": 5, "F2": 2, "S2": 1 + 1, "SC": 1}   # S2 = 54 + trivial (I2*delta is quadratic; chain/cross/SS cubic: 54 once + 1 once)


def polarise(func, deg, T0, Tx):
    if deg == 3:
        return (func(T0 + Tx) - func(T0 - Tx)) // 2 - func(Tx)
    if deg == 2:
        return (func(T0 + Tx) - func(T0 - Tx)) // 2
    if deg == 1:
        return func(Tx)
    return None


phi0 = K.pao_vector(P0, A0, 0, dtype=object)
T0 = C.dense(phi0)
unb, tan = K.stabilizer(K.pao_vector(P0, A0, 0))
od = int(np.linalg.matrix_rank(tan)); nd = 210 - od
out["orbit_dim"] = od; out["normal_dim"] = nd

# --- completeness check of cubic families at random integer points (rank as polynomial maps)
rng = np.random.default_rng(5)
comp = {}
for target, fam in FAMILIES.items():
    cubic = [(n, f) for n, (f, d) in fam.items() if d == 3]
    cols = []
    for n, f in cubic:
        vals = []
        for k in range(4):
            v = rng.integers(-2, 3, size=210)
            vals.append(flat(target, f(C.dense(v))))
        cols.append(np.concatenate(vals))
    Mx = sp.Matrix(np.column_stack(cols).tolist())
    rk = Mx.rank()
    comp[target] = {"n_cubic_candidates": len(cubic), "rank_as_polynomial_maps": int(rk), "names": [n for n, _ in cubic]}
    print(target, comp[target], f"[{time.time() - t0:.0f}s]", flush=True)
out["cubic_family_completeness"] = comp

# --- values at Phi0, vanishing combinations, gradient span
all_rows = []
per_target = {}
basis_T = [C.dense(np.eye(210, dtype=np.int64)[j]) for j in range(210)]
for target, fam in FAMILIES.items():
    names = list(fam.keys())
    vals = [flat(target, fam[n][0](T0)) for n in names]
    V = sp.Matrix(np.column_stack(vals).tolist())
    ns = V.nullspace()
    per_target[target] = {"covariants": names, "n_covariants": len(names), "rank_at_phi0": int(V.rank()), "n_vanishing_combinations": len(ns)}
    print(target, "values rank", V.rank(), "vanishing combos", len(ns), f"[{time.time() - t0:.0f}s]", flush=True)
    if not ns:
        continue
    # gradient maps: for each covariant, the matrix D_i (dim_target x 210) with column j = dC_i(Phi0)[e_j]
    D = {}
    for n in names:
        f, d = fam[n]
        if d == 0:
            D[n] = None; continue
        cols = []
        for j in range(210):
            pol = polarise(f, d, T0, basis_T[j])
            cols.append(flat(target, pol))
        D[n] = np.column_stack(cols).astype(object)
    ranks = []
    for alpha in ns:
        alpha = alpha / max(1, max(abs(x) for x in alpha))  # scale
        # clear denominators
        den = sp.ilcm(*[sp.fraction(x)[1] for x in alpha]) if any(x != 0 for x in alpha) else 1
        al = [int(x * den) for x in alpha]
        J = None
        for n, a_i in zip(names, al):
            if a_i == 0 or D[n] is None:
                continue
            J = (a_i * D[n]) if J is None else J + a_i * D[n]
        if J is None:
            continue
        Jm = sp.Matrix(J.tolist())
        rk = Jm.rank()
        ranks.append(int(rk))
        for r in range(Jm.rows):
            row = Jm.row(r)
            if any(x != 0 for x in row):
                all_rows.append([int(x) for x in row])
    per_target[target]["gradient_ranks_per_combination"] = ranks
    print(target, "gradient ranks", ranks, f"[{time.time() - t0:.0f}s]", flush=True)

# total span (exact rank of the stacked integer matrix) -- use float rank first then exact
Mall = np.array(all_rows, dtype=float)
rk_float = int(np.linalg.matrix_rank(Mall)) if len(all_rows) else 0
print("stacked rows", len(all_rows), "float rank", rk_float, flush=True)
# exact rank via modular arithmetic (rank over Q >= rank mod p; equality generic) and sympy on a reduced set
rk_exact = None
try:
    Ms = sp.Matrix(all_rows)
    rk_exact = int(Ms.rank())
except Exception as e:
    print("exact rank failed:", e)
out["per_target"] = per_target
out["W3_rank_float"] = rk_float
out["W3_rank_exact"] = rk_exact
out["flat_modes_degree3_lower_bound"] = nd - (rk_exact if rk_exact is not None else rk_float)
# check all rows are orthogonal to tangents (sanity)
tanT = np.array([[int(x) for x in t] for t in K.exact_tangent_matrix(phi0)], dtype=float)
out["max_tangent_overlap"] = float(np.max(np.abs(Mall @ tanT.T))) if len(all_rows) else 0.0
out["elapsed_s"] = time.time() - t0
print(json.dumps({k: v for k, v in out.items() if k != "per_target"}, indent=1))
json.dump(out, open(os.path.join(HERE, f"t3_degree3_flat_modes_{lab}.json"), "w"), indent=1)
