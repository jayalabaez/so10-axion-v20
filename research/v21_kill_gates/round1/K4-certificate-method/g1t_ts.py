"""g1t: vanishing combinations at Phi0 for the 8085 block, realised in the carrier 210 x Sym^2_0(10) (k4ts).
Same logic as g1 (exact integer Grams tr(Z_i P_8085 Z_j) from traces of C^a Z, generic-point kernel removal,
exact null space over Q, LLL).  Expected: generic multiplicity 3 (= Sym^3 multiplicity of 8085), rank at Phi0 <= 2
(= dim V_8085^H), hence >= 1 vanishing family."""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G
import k4ts as TS

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
lab = f"p{P0}_a{A0}_ts"
TS.set_eigenvalues({"8085": -2, "1050t": 4, "945t": 6, "210t": 10})
so_poly, _ = TS.ts_projector("8085")
print("P_8085 polynomial in C_ts:", [str(c) for c in so_poly], flush=True)
rng = np.random.default_rng(13)
covs = TS.all_ts_covariants(3)
byname = {c.name: c for c in covs}


def eval_all(phi, names=None):
    T4 = G.dense4(phi); T6 = G.dense6_fast(G.HODGE @ np.asarray(phi, dtype=float))
    out = {}
    for c in covs:
        if names is not None and c.name not in names:
            continue
        out[c.name] = TS.sym_traceless(c.evaluate(T4, T6))
    return out


basis_file = os.path.join(HERE, "g1_basis_ts.json")
if os.path.exists(basis_file):
    basis = json.load(open(basis_file))["basis"]
else:
    pts = [(rng.integers(-3, 4, size=210) * (rng.random(210) < 0.35)).astype(float) for _ in range(2)]
    ev = [eval_all(p) for p in pts]
    basis = []
    from scipy.linalg import qr
    for d in range(1, 4):
        names = [c.name for c in covs if c.degree == d]
        A = np.array([np.concatenate([ev[k][n].ravel() for k in range(2)]) for n in names])
        nr = np.linalg.norm(A, axis=1); nr[nr == 0] = 1.0
        Qm, Rm, piv = qr((A / nr[:, None]).T, pivoting=True, mode="economic")
        diag = np.abs(np.diag(Rm)); rk = int(np.sum(diag > 1e-9 * diag[0]))
        chosen = [names[i] for i in piv[:rk]]
        print(f"degree {d}: {len(names)} graphs, rank {rk}", flush=True)
        basis += chosen
    json.dump({"basis": basis, "subs": {n: byname[n].subs for n in basis}, "degree": {n: byname[n].degree for n in basis}}, open(basis_file, "w"), indent=1)
nb = len(basis)
print("ts basis size", nb, "(expected 22)", f"[{time.time()-t0:.0f}s]", flush=True)


def powers_exact(Z, nmax=2):
    pows = [Z]
    for a in range(nmax):
        assert 180.0 * np.abs(pows[-1]).max() < 2.0 ** 52
        pows.append(TS.C_ts(pows[-1]))
    return [G.to_object(p) for p in pows]


def tr(A, B):
    return int(np.sum(A * B))


def exact_gram(phi):
    Z0 = eval_all(phi, set(basis))
    Zs = [Z0[n] for n in basis]
    CZ = [powers_exact(Z) for Z in Zs]
    Gm = sp.zeros(nb, nb)
    for i in range(nb):
        for j in range(i, nb):
            val = Fraction(0)
            for n, pn in enumerate(so_poly):
                a = min(n, 2); b = n - a
                val += pn * tr(CZ[i][a], CZ[j][b])
            Gm[i, j] = sp.Rational(val.numerator, val.denominator); Gm[j, i] = Gm[i, j]
    return Gm


phi0 = K.pao_vector(P0, A0, 0)
G0 = exact_gram(phi0)
print("exact Gram at Phi0 done", f"[{time.time()-t0:.0f}s]", flush=True)
rng_g = np.random.default_rng(99)
Gr = None
for rep in range(3):
    phir = (rng_g.integers(-1, 2, size=210) * (rng_g.random(210) < 0.4)).astype(float)
    g_ = exact_gram(phir)
    Gr = g_ if Gr is None else Gr + g_
print("exact generic Grams done", f"[{time.time()-t0:.0f}s]", flush=True)
rk_generic = Gr.rank()
_, piv = Gr.rref(); B = list(piv)
sub0 = G0.extract(B, B); rk0 = sub0.rank()
ns = sub0.nullspace()
alphas = []
for vec in ns:
    den = sp.ilcm(*[sp.fraction(x)[1] for x in vec]); a_small = [int(x * den) for x in vec]
    g = 0
    for x in a_small:
        g = sp.igcd(g, x)
    if g > 1:
        a_small = [x // g for x in a_small]
    a = [0] * nb
    for pos, idx in enumerate(B):
        a[idx] = a_small[pos]
    alphas.append(a)
for a in alphas:
    av = sp.Matrix(a)
    assert (G0 * av) == sp.zeros(nb, 1) and (Gr * av) != sp.zeros(nb, 1)
out = {"point": [P0, A0], "carrier": "ts", "basis": basis,
       "channels": {"8085": {"m_generic_rank": int(rk_generic), "m_expected": 3, "pivot_set": B, "rank_at_phi0": int(rk0),
                             "n_vanishing": len(alphas), "alphas": alphas, "max_alpha_entry": max((abs(x) for a in alphas for x in a), default=0)}},
       "total_vanishing": len(alphas), "elapsed_s": time.time() - t0}
print("8085: generic multiplicity", rk_generic, "(expected 3) rank at Phi0", rk0, "(dim V^H = 2) vanishing", len(alphas), "alphas", alphas, flush=True)
json.dump(out, open(os.path.join(HERE, f"g1_vanishing_p{P0}_a{A0}_ts.json"), "w"), indent=1)
print("total vanishing combinations:", len(alphas), flush=True)
