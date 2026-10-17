"""g1: (i) choose a basis of the Sym^2(210)-valued covariants of degree <= 3 from the graph-generated set
(numerically, pivoted QR on evaluations at random points; expected dimension 41 = 1+1+10+29);
(ii) at Phi0 = p P + a A compute, EXACTLY (integer arithmetic), the channel Gram matrices
      G^kappa_ij = tr( X_i(Phi0) P_kappa X_j(Phi0) )
   via P_kappa = so_poly(C) gl_poly(K), tr(X C^n X') = tr((C^a X)(C^b X')) with a+b = n, all matrices exact
   integers in float64 (bounds checked) and the traces in Python integers;
(iii) the exact null vectors alpha (primitive integers) of each G^kappa = the vanishing covariant combinations
   s_alpha = P_kappa( sum_i alpha_i X_i(Phi) ), which vanish on the whole orbit SO(10).Phi0.
Output: g1_basis.json (basis names + einsum subscripts), g1_vanishing_p{p}_a{a}.json (ranks, nullities, alphas)."""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
CARRIER = sys.argv[3] if len(sys.argv) > 3 else "sym"
lab = f"p{P0}_a{A0}" + ("" if CARRIER == "sym" else "_anti")
CHANNELS = G.CHANNELS if CARRIER == "sym" else G.ANTI_CHANNELS
PROJ = G.PROJ if CARRIER == "sym" else G.PROJ_ANTI
rng = np.random.default_rng(11)
covs = G.all_graph_covariants(3, include_odd=True)
byname = {c.name: c for c in covs}


def eval_all(phi, names=None):
    T4 = G.dense4(phi)
    T6 = G.dense6_fast(G.HODGE @ np.asarray(phi, dtype=float))
    out = {}
    for c in covs:
        if names is not None and c.name not in names:
            continue
        X = c.evaluate(T4, T6)
        out[c.name] = (X + X.T) if CARRIER == "sym" else (X - X.T)
    return out


# ---- (i) basis selection: 2 random points, pivoted QR per degree (keep lower degrees first)
basis_file = os.path.join(HERE, "g1_basis.json" if CARRIER == "sym" else "g1_basis_anti.json")
if os.path.exists(basis_file):
    basis = json.load(open(basis_file))["basis"]
    print("loaded basis", len(basis), flush=True)
else:
    pts = [(rng.integers(-3, 4, size=210) * (rng.random(210) < 0.35)).astype(float) for _ in range(2)]
    ev = [eval_all(p) for p in pts]
    basis = []
    for d in range(4):
        names = [c.name for c in covs if c.degree == d]
        A = np.array([np.concatenate([ev[k][n].ravel() for k in range(2)]) for n in names])   # rows
        # normalise rows
        nr = np.linalg.norm(A, axis=1); nr[nr == 0] = 1.0
        An = A / nr[:, None]
        # pivoted QR on An^T to choose independent rows
        from scipy.linalg import qr
        Qm, Rm, piv = qr(An.T, pivoting=True, mode="economic")
        diag = np.abs(np.diag(Rm))
        rk = int(np.sum(diag > 1e-9 * diag[0]))
        chosen = [names[i] for i in piv[:rk]]
        print(f"degree {d}: {len(names)} graphs, rank {rk}, chosen {chosen}", flush=True)
        basis += chosen
    json.dump({"basis": basis, "subs": {n: byname[n].subs for n in basis}, "degree": {n: byname[n].degree for n in basis},
               "parity": {n: byname[n].parity for n in basis}}, open(basis_file, "w"), indent=1)
print("basis size", len(basis), f"[{time.time()-t0:.0f}s]", flush=True)
nb = len(basis)

# ---- (ii) exact channel Grams (integer arithmetic) at a point
def powers_exact(X, nmax=4):
    """C^a X for a=0..nmax as float64 exact integers (bound-checked), returned as object arrays."""
    pows = [X]
    for a in range(nmax):
        prev = pows[-1]
        assert 45.0 * np.abs(prev).max() < 2.0 ** 52, "exactness bound (C)"
        pows.append(G.C_so(prev))
    return [G.to_object(p) for p in pows]


def K_exact(X):
    assert 100.0 * np.abs(X).max() < 2.0 ** 52, "exactness bound (K)"
    return G.K_gl(X)


def tr(Aobj, Bobj):
    return int(np.sum(Aobj * Bobj))


def exact_grams(phi):
    """dict channel -> sympy rational nb x nb Gram matrix G_ij = tr(X_i(phi) P_kappa X_j(phi))."""
    X0 = eval_all(phi, set(basis))
    Xs = [X0[n] for n in basis]
    print("  max |X_i| =", max(np.abs(X).max() for X in Xs), flush=True)
    CX = [powers_exact(X) for X in Xs]
    KX = [K_exact(X) for X in Xs]
    CKX = [powers_exact(KX_) for KX_ in KX]
    T0 = {}; T1 = {}; T2 = {}
    for i in range(nb):
        for j in range(i, nb):
            for n in range(8):
                a = min(n, 4); b = n - a
                T0[(i, j, n)] = tr(CX[i][a], CX[j][b])
                T1[(i, j, n)] = tr(CX[i][a], CKX[j][b])
                T2[(i, j, n)] = tr(CKX[i][a], CKX[j][b])
    assert tr(CKX[0][0], CX[1][2]) == T1[(0, 1, 2)]
    grams = {}
    for ch in CHANNELS:
        so_poly, gl_poly = PROJ[ch]
        Gm = sp.zeros(nb, nb)
        for i in range(nb):
            for j in range(i, nb):
                val = Fraction(0)
                for n, pn in enumerate(so_poly):
                    if pn == 0:
                        continue
                    if len(gl_poly) == 1:
                        val += pn * T0[(i, j, n)]
                    else:
                        val += pn * (gl_poly[0] * T0[(i, j, n)] + gl_poly[1] * T1[(i, j, n)] + gl_poly[2] * T2[(i, j, n)])
                Gm[i, j] = sp.Rational(val.numerator, val.denominator); Gm[j, i] = Gm[i, j]
        grams[ch] = Gm
    return grams


M_EXPECTED = {"1": 3, "45": 3, "54": 2, "210": 7, "770": 3, "1050": 8, "4125": 4, "5940": 7, "8910": 4} if CARRIER == "sym" else G.ANTI_M_EXPECTED
phi0 = K.pao_vector(P0, A0, 0)
t1 = time.time()
grams0 = exact_grams(phi0)
print("exact Grams at Phi0 done", f"[{time.time()-t1:.0f}s]", flush=True)
# generic point (small entries) to identify the identically-vanishing kernel of X -> P_kappa X
rng_g = np.random.default_rng(99)
gramsr = None
for rep in range(3):
    phir = (rng_g.integers(-1, 2, size=210) * (rng_g.random(210) < 0.4)).astype(float)
    t1 = time.time()
    g_ = exact_grams(phir)
    gramsr = g_ if gramsr is None else {ch: gramsr[ch] + g_[ch] for ch in g_}
    print("exact Grams at generic point", rep, "done", f"[{time.time()-t1:.0f}s]", flush=True)
# (sum of PSD Grams over 3 generic points: its null space = covariant combinations whose kappa-projection vanishes
#  identically; multiples by the invariants 1, I2, I3 are separated only with >= 3 points)


def primitive_int(vec):
    den = sp.ilcm(*[sp.fraction(x)[1] for x in vec])
    a = [int(x * den) for x in vec]
    g = 0
    for x in a:
        g = sp.igcd(g, x)
    if g > 1:
        a = [x // g for x in a]
    return a


def lll_rows(rows):
    """LLL-reduce an integer row basis (sympy DomainMatrix); falls back to the input."""
    try:
        from sympy.polys.matrices import DomainMatrix
        from sympy import ZZ
        dm = DomainMatrix([[ZZ(int(x)) for x in r] for r in rows], (len(rows), len(rows[0])), ZZ)
        red = dm.lll()
        return [[int(x) for x in r] for r in red.to_Matrix().tolist()]
    except Exception as e:
        print("  LLL unavailable:", e, flush=True)
        return rows


out = {"point": [P0, A0], "basis": basis, "channels": {}}
alphas_all = {}
out["carrier"] = CARRIER
for ch in CHANNELS:
    Gr = gramsr[ch]; G0 = grams0[ch]
    rk_generic = Gr.rank()
    # pivot set B: a maximal subset of basis covariants with non-degenerate generic Gram (= independent maps into kappa)
    _, piv = Gr.rref()
    B = list(piv)
    assert len(B) == rk_generic
    sub0 = G0.extract(B, B)
    rk0 = sub0.rank()
    ns = sub0.nullspace()
    alphas = []
    for vec in ns:
        a_small = primitive_int(vec)
        a = [0] * nb
        for pos, idx in enumerate(B):
            a[idx] = a_small[pos]
        alphas.append(a)
    if len(alphas) > 1:
        alphas = lll_rows(alphas)
    # exact check: each alpha annihilates G0 (G0 alpha = 0) and is NOT in the generic kernel (Gr alpha != 0)
    for a in alphas:
        av = sp.Matrix(a)
        assert (G0 * av) == sp.zeros(nb, 1)
        assert (Gr * av) != sp.zeros(nb, 1)
    alphas_all[ch] = alphas
    out["channels"][ch] = {"m_generic_rank": int(rk_generic), "m_expected": M_EXPECTED[ch], "pivot_set": B,
                           "rank_at_phi0": int(rk0), "n_vanishing": len(alphas), "alphas": alphas,
                           "max_alpha_entry": max((abs(x) for a in alphas for x in a), default=0)}
    print(ch, "generic multiplicity", rk_generic, "(expected", M_EXPECTED[ch], ") rank at Phi0", rk0, "vanishing", len(alphas),
          "max|alpha|", out["channels"][ch]["max_alpha_entry"], f"[{time.time()-t0:.0f}s]", flush=True)
out["total_vanishing"] = sum(len(v) for v in alphas_all.values())
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, f"g1_vanishing_{lab}.json"), "w"), indent=1)
print("total vanishing combinations:", out["total_vanishing"], flush=True)
