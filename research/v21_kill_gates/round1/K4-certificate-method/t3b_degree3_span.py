"""t3b: degree-3 flat-mode test (corrected), built on k4van.
For each target, vanishing combinations at Phi0 and the exact gradient span W3; flat modes = normal_dim - dim W3.
Also: family completeness vs exact Sym^3 multiplicities (same points for all covariants)."""
import json, os, sys, time
import numpy as np
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4cov as C
import k4van as VN

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 1)
lab = f"p{P0}_a{A0}"
phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
tans = K.exact_tangent_matrix(np.array([int(x) for x in phi0_int], dtype=object))
Tm = sp.Matrix([[int(x) for x in t] for t in tans])
od = Tm.rank(); nd = 210 - od
out = {"point": [P0, A0], "orbit_dim": int(od), "normal_dim": int(nd)}

# completeness (same random points for every covariant)
rng = np.random.default_rng(5)
pts = [rng.integers(-2, 3, size=210) for _ in range(4)]
comp = {}
for target, fam in VN.FAMILIES.items():
    cubic = [n for n, (f, d) in fam.items() if d == 3]
    cols = []
    for n in cubic:
        cols.append(np.concatenate([VN.flat(target, fam[n][0](C.dense(v))) for v in pts]))
    rk = int(sp.Matrix(np.column_stack(cols).tolist()).rank()) if cols else 0
    comp[target] = {"cubic_names": cubic, "rank_as_maps": rk}
    print("completeness", target, comp[target], f"[{time.time() - t0:.0f}s]", flush=True)
out["completeness"] = comp
out["exact_Sym3_multiplicities"] = {"F4(210)": 5, "F2(45)": 2, "S2(54+1)": 2, "SC(1)": 1}

rows = []
per = {}
for target in ("SC", "F2", "S2", "F4"):
    names, degs, alphas = VN.vanishing_combinations(target, phi0_int)
    per[target] = {"covariants": names, "degrees": degs, "n_vanishing": len(alphas), "alphas": alphas, "ranks": []}
    print(target, "vanishing combos", len(alphas), f"[{time.time() - t0:.0f}s]", flush=True)
    for alpha in alphas:
        J = VN.polarisation_matrix(target, names, degs, alpha, phi0_int)    # target_dim x 210 (object ints)
        Jf = J.astype(float)
        # sanity: the combination vanishes at Phi0 (exact) and gradient rows are orthogonal to tangents
        val = VN.evaluate_combination(target, names, alpha, phi0_int)
        assert all(int(x) == 0 for x in val), "combination does not vanish at Phi0"
        overlap = float(np.max(np.abs(Jf @ np.array([[int(x) for x in t] for t in tans], dtype=float).T)))
        rk = int(np.linalg.matrix_rank(Jf))
        per[target]["ranks"].append(rk)
        per[target].setdefault("tangent_overlaps", []).append(overlap)
        for r in range(J.shape[0]):
            if any(int(x) != 0 for x in J[r]):
                rows.append([int(x) for x in J[r]])
        print(f"   {target} alpha={alpha} grad rank {rk} tangent overlap {overlap:.3g} [{time.time() - t0:.0f}s]", flush=True)
Mall = np.array(rows, dtype=float)
rk_f = int(np.linalg.matrix_rank(Mall)) if len(rows) else 0
rk_e = int(sp.Matrix(rows).rank()) if len(rows) else 0
out["per_target"] = per
out["W3_rank_float"] = rk_f; out["W3_rank_exact"] = rk_e
out["flat_modes_degree3"] = int(nd - rk_e)
out["elapsed_s"] = time.time() - t0
print(json.dumps({k: v for k, v in out.items() if k != "per_target"}, indent=1), flush=True)
json.dump(out, open(os.path.join(HERE, f"t3b_degree3_span_{lab}.json"), "w"), indent=1)
