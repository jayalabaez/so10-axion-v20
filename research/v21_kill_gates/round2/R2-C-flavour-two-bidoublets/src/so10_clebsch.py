"""Exact SO(10) Clebsch factors for 16.16.10 and 16.16.126bar Yukawa couplings (K2 gate, self-contained).

Spin(10) Clifford algebra in a Jordan-Wigner oscillator basis (5 oscillators = the 5 of SU(5)).
The 16 is the even-occupation chirality block; states are named by (colour occupation, weak occupation).
Bilinears  16^T C Gamma_[i1..ip] 16  for p = 1 (the 10) and p = 5 (the 126 / 126bar) are built explicitly.
For each SM-singlet / neutral-doublet direction we find the unit-norm p-form component (canonical kinetic
normalisation = unit norm in the ordered-index basis) whose bilinear is supported only on the required
fermion pairs, and read off the coupling coefficients.  Output: ratios  c_e/c_d, c_nu/c_u  (expected +1 for the
10, -3 for the 126bar) and the singlet-neutrino coefficient  c_R  relative to the doublet coefficient  c_d.
Everything is numerically exact to machine precision (rational/sqrt numbers are reported).
"""
import itertools, json, sys
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "clebsch.json"

# --- oscillators -----------------------------------------------------------
sm = np.array([[0, 0], [1, 0]], dtype=complex)   # b (annihilation acting on |n>: b|1> = |0>) in basis (|0>,|1>)
sz = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)

def kron_all(mats):
    out = np.array([[1.0 + 0j]])
    for m in mats:
        out = np.kron(out, m)
    return out

B = []
for k in range(5):
    mats = [sz] * k + [sm.T] + [I2] * (4 - k)   # b_k annihilation with JW string; sm.T = |0><1|
    B.append(kron_all(mats))
Bd = [b.conj().T for b in B]
for k in range(5):
    for l in range(5):
        anti = B[k] @ Bd[l] + Bd[l] @ B[k]
        assert np.allclose(anti, np.eye(32) * (k == l)), "oscillator algebra"
        assert np.allclose(B[k] @ B[l] + B[l] @ B[k], 0)

Gam = []
for k in range(5):
    Gam.append(B[k] + Bd[k])                 # Gamma_{2k+1}
    Gam.append(-1j * (B[k] - Bd[k]))         # Gamma_{2k+2}
for i in range(10):
    for j in range(10):
        assert np.allclose(Gam[i] @ Gam[j] + Gam[j] @ Gam[i], 2 * np.eye(32) * (i == j)), "Clifford"

# number operators and chirality
N = [Bd[k] @ B[k] for k in range(5)]
Ntot = sum(N)
occ = np.array([[(s >> (4 - k)) & 1 for k in range(5)] for s in range(32)])  # occupation of state s (kron order)
# check: N_k diagonal with these occupations
for k in range(5):
    assert np.allclose(np.diag(N[k]).real, occ[:, k])
even = [s for s in range(32) if occ[s].sum() % 2 == 0]
P = np.zeros((32, 16), dtype=complex)
for a, s in enumerate(even):
    P[s, a] = 1.0

# charge conjugation: C Gamma_i C^-1 = -Gamma_i^T for all i  (product of the five even gammas)
C = np.eye(32, dtype=complex)
for k in range(5):
    C = C @ Gam[2 * k + 1]
Cinv = np.linalg.inv(C)
for i in range(10):
    assert np.allclose(C @ Gam[i] @ Cinv, -Gam[i].T), "C property"

# --- state names ------------------------------------------------------------
# colour oscillators k=0,1,2 (Y=-1/3 each), weak k=3 (T3=+1/2), k=4 (T3=-1/2), Y=+1/2 each
def name(s):
    o = occ[s]
    nc, nw = o[:3].sum(), o[3:].sum()
    Y = -nc / 3 + nw / 2
    if (nc, nw) == (0, 0):
        return ("nuc", None), Y
    if (nc, nw) == (2, 0):
        col = [k for k in range(3) if o[k] == 0][0]
        return ("uc", col), Y
    if (nc, nw) == (0, 2):
        return ("ec", None), Y
    if (nc, nw) == (1, 1):
        col = [k for k in range(3) if o[k] == 1][0]
        return (("uL" if o[3] == 1 else "dL"), col), Y
    if (nc, nw) == (2, 2):
        col = [k for k in range(3) if o[k] == 0][0]
        return ("dc", col), Y
    if (nc, nw) == (3, 1):
        return (("nuL" if o[3] == 1 else "eL"), None), Y
    raise ValueError
names = {a: name(s) for a, s in enumerate(even)}
# SU(3)_c generators on the Fock space, restricted to the 16: T^a = sum b_k^dag (lambda^a/2)_kl b_l
_l = np.zeros((8, 3, 3), dtype=complex)
_l[0][0, 1] = _l[0][1, 0] = 1; _l[1][0, 1] = -1j; _l[1][1, 0] = 1j; _l[2][0, 0] = 1; _l[2][1, 1] = -1
_l[3][0, 2] = _l[3][2, 0] = 1; _l[4][0, 2] = -1j; _l[4][2, 0] = 1j; _l[5][1, 2] = _l[5][2, 1] = 1
_l[6][1, 2] = -1j; _l[6][2, 1] = 1j; _l[7][0, 0] = _l[7][1, 1] = 1 / np.sqrt(3); _l[7][2, 2] = -2 / np.sqrt(3)
SU3_GENS = []
for a in range(8):
    T = sum(Bd[k] @ B[l] * _l[a][k, l] / 2 for k in range(3) for l in range(3))
    SU3_GENS.append(P.T @ T @ P)
idx = {}
for a, (nm, Y) in names.items():
    idx.setdefault(nm[0], {})[nm[1]] = a
assert set(idx) == {"nuc", "uc", "ec", "uL", "dL", "dc", "nuL", "eL"}

# --- p-form bilinears --------------------------------------------------------
def gamma_product(ind):
    m = np.eye(32, dtype=complex)
    for i in ind:
        m = m @ Gam[i]
    return m

def bilinears(p):
    combos = list(itertools.combinations(range(10), p))
    mats = []
    for ind in combos:
        G = gamma_product(ind)          # ordered product = antisymmetrised product for distinct indices
        mats.append(P.T @ (C @ G) @ P)  # 16 x 16
    return combos, mats

def entry_list(mat, pairs):
    return [mat[a, b] for a, b in pairs]

def pair_indices():
    pr = {}
    pr["dd"] = [(idx["dL"][c], idx["dc"][c]) for c in range(3)]
    pr["uu"] = [(idx["uL"][c], idx["uc"][c]) for c in range(3)]
    pr["ee"] = [(idx["eL"][None], idx["ec"][None])]
    pr["nunu"] = [(idx["nuL"][None], idx["nuc"][None])]
    pr["ncnc"] = [(idx["nuc"][None], idx["nuc"][None])]
    pr["nLnL"] = [(idx["nuL"][None], idx["nuL"][None])]
    return pr

def colour_groups(pairs):
    groups = {}
    for a, b in pairs:
        key = (names[a][0][0], names[b][0][0])
        groups.setdefault(key, []).append((a, b))
    return [g for g in groups.values() if len(g) > 1]

def solve_direction(mats, allowed_pairs):
    """Unit-norm p-form direction v (in the span where bilinears live) with B(v) supported only on allowed pairs
    (and their transposes).  Returns the coefficients on the allowed pairs and the dimension of the solution space."""
    n = len(mats)
    M = np.array([m.reshape(-1) for m in mats]).T  # 256 x n : B(v) = M v
    # restrict to the subspace where M is injective (the (anti)self-dual part): row space of M
    U, S, Vh = np.linalg.svd(M, full_matrices=False)
    rank = int((S > 1e-9 * S[0]).sum())
    Vr = Vh[:rank].conj().T           # n x rank basis of the row space (v = Vr w)
    allowed = set()
    for a, b in allowed_pairs:
        allowed.add(a * 16 + b); allowed.add(b * 16 + a)
    forbid = [r for r in range(256) if r not in allowed]
    A = M[forbid] @ Vr                  # constraints A w = 0
    # colour-singlet condition on the (3, 3bar) blocks: t_a^T X + X t'_a = 0 for the eight SU(3) generators
    rows = []
    for group in colour_groups(allowed_pairs):
        ra = [a for a, b in group]
        cb = [b for a, b in group]
        for ta in SU3_GENS:
            t1 = ta[np.ix_(ra, ra)]
            t2 = ta[np.ix_(cb, cb)]
            for j in range(Vr.shape[1]):
                pass
            # linear map w -> X(w) block; build rows for each entry
            Xj = [(M[:, :] @ Vr[:, j]).reshape(16, 16)[np.ix_(ra, cb)] for j in range(Vr.shape[1])]
            for c in range(len(ra)):
                for cp in range(len(cb)):
                    rows.append(np.array([(t1.T @ X + X @ t2)[c, cp] for X in Xj]))
    if rows:
        A = np.vstack([A, np.array(rows)])
    Ua, Sa, Vha = np.linalg.svd(A, full_matrices=True)
    ra = int((Sa > 1e-9 * max(Sa[0], 1e-300)).sum())
    null = Vha[ra:].conj().T            # rank x k
    k = null.shape[1]
    sols = []
    for j in range(k):
        v = Vr @ null[:, j]
        v = v / np.linalg.norm(v)
        Bv = (M @ v).reshape(16, 16)
        sols.append((v, Bv))
    return rank, k, sols

results = {}
pr = pair_indices()
for p, label in [(1, "10"), (5, "126")]:
    combos, mats = bilinears(p)
    sym = all(np.allclose(m, m.T) for m in mats)
    anti = all(np.allclose(m, -m.T) for m in mats)
    res = {"p": p, "symmetric": sym, "antisymmetric": anti, "n_forms": len(combos)}
    for key, pairs in [("down", pr["dd"] + pr["ee"]), ("up", pr["uu"] + pr["nunu"]),
                       ("singlet_R", pr["ncnc"]), ("triplet_L", pr["nLnL"])]:
        rank, k, sols = solve_direction(mats, pairs)
        res.setdefault("rank_of_bilinear_map", rank)
        entry = {"n_solutions": k}
        for j, (v, Bv) in enumerate(sols):
            d = {}
            for pname in ["dd", "uu", "ee", "nunu", "ncnc", "nLnL"]:
                vals = entry_list(Bv, pr[pname])
                d[pname] = [complex(x) for x in vals]
            # off-support check
            supp = np.zeros((16, 16), dtype=bool)
            for a, b in pairs:
                supp[a, b] = supp[b, a] = True
            d["max_off_support"] = float(np.abs(Bv[~supp]).max())
            entry[f"sol{j}"] = d
        res[key] = entry
    results[label] = res

# summarise the physically relevant numbers
def mag(z):
    return abs(z)
summary = {}
for label in ["10", "126"]:
    r = results[label]
    s = {}
    for key in ["down", "up", "singlet_R", "triplet_L"]:
        e = r[key]
        if e["n_solutions"] >= 1:
            d = e["sol0"]
            s[key] = {"n_solutions": e["n_solutions"], "max_off_support": d["max_off_support"],
                      "c_d": mag(d["dd"][0]), "c_e": mag(d["ee"][0]), "ratio_e_over_d": (d["ee"][0] / d["dd"][0]) if abs(d["dd"][0]) > 1e-12 else None,
                      "c_u": mag(d["uu"][0]), "c_nu": mag(d["nunu"][0]), "ratio_nu_over_u": (d["nunu"][0] / d["uu"][0]) if abs(d["uu"][0]) > 1e-12 else None,
                      "c_ncnc": mag(d["ncnc"][0]), "c_nLnL": mag(d["nLnL"][0]),
                      "colour_universality_dd": float(np.std([abs(x) for x in d["dd"]])),
                      "colour_universality_uu": float(np.std([abs(x) for x in d["uu"]]))}
        else:
            s[key] = {"n_solutions": 0}
    summary[label] = s

def jsonable(o):
    if isinstance(o, complex):
        return [o.real, o.imag]
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [jsonable(v) for v in o]
    return o

json.dump({"summary": jsonable(summary), "full": jsonable(results)}, open(OUT, "w"), indent=1)
for label in ["10", "126"]:
    print("==", label, "rank", results[label]["rank_of_bilinear_map"], "sym", results[label]["symmetric"])
    for key, s in summary[label].items():
        print(key, {k: (round(v, 6) if isinstance(v, float) else (None if v is None else (round(v.real, 6), round(v.imag, 6)) if isinstance(v, complex) else v)) for k, v in s.items()})
