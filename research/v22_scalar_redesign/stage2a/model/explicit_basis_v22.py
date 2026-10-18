#!/usr/bin/env python3
"""Stage-2a "model": method (b) - explicit tensor-contraction basis for every SO(10) structure of the v22-L2 scalar
potential that involves the real 45_H "A", verified NUMERICALLY on random field configurations.

Fields (explicit components, physical conventions of the v20 tensor backend):
  A_ab      real antisymmetric 10x10           (45)       K_45  = (1/4) A_ab A_ab   = (1/2) sum_{a<b} A_ab^2
  P_abcd    real totally antisymmetric 4-form  (210)      K_210 = (1/4!) P_abcd P_abcd
  H_a       complex 10-vector                  (10_H, X = -2);  Hb_a = conj(H_a)
  D_abcde   complex 5-form with *D = -i D      (126bar_H, X = -2; the v20 "-i Hodge eigenspace");  Db = conj(D)
            (*X)_{a1..a5} = (1/5!) eps_{a1..a5 b1..b5} X_{b1..b5}
By the first fundamental theorem of invariant theory for SO(10), every polynomial invariant is a linear combination of
complete contractions with delta's and at most one Levi-Civita tensor eps_{a1..a10} (two eps's reduce to deltas);
an eps contracted into a monomial containing D or Db can be traded for deltas (D = i *D), so eps graphs are generated
only for D-free structures.  Because every tensor is totally antisymmetric, a complete contraction is fixed, up to a
sign, by its multigraph (edge multiplicities n_ij between tensor nodes; no self-loops).  For each structure ALL
multigraphs are generated (canonical under permutations of identical nodes), evaluated on random configurations,
and the numerical rank of the value matrix is compared with the EXACT character count of census_v22.py.
A basis is then selected greedily (delta graphs first, fewest edges between distinct field types first), each basis
element is checked for SO(10) invariance under a random finite rotation and, for eps graphs, for sign flip under a
reflection (pseudo-scalar: allowed, the gauge group is SO(10)/Spin(10)).
v20 structures are run as a calibration of the method against the attested v20 counts.
Output: explicit_basis_v22.json (+ log).  Large arrays: none (everything is regenerated from the seed).
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RANKS = {"A": 2, "P": 4, "H": 1, "Hb": 1, "D": 5, "Db": 5, "eps": 10}
CONJ = {"A": "A", "P": "P", "H": "Hb", "Hb": "H", "D": "Db", "Db": "D"}
N = 10
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ----------------------------------------------------------------------------------------------------------------
# antisymmetric tensors
# ----------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def combos(k):
    if k == 0:
        return np.zeros((1, 0), dtype=np.int64)
    return np.array(list(itertools.combinations(range(N), k)), dtype=np.int64).reshape(-1, k)


def perm_parity(seq):
    seq = list(seq); s = 1
    for i in range(len(seq)):
        while seq[i] != i:
            j = seq[i]; seq[i], seq[j] = seq[j], seq[i]; s = -s
    return s


@lru_cache(maxsize=None)
def perm_table(k):
    perms = list(itertools.permutations(range(k)))
    return np.array(perms, dtype=np.int64), np.array([perm_parity(p) for p in perms], dtype=np.int64)


def form_from_components(comp, k, dtype=float):
    """dense totally antisymmetric rank-k array from its C(10,k) independent components (sorted subsets)."""
    T = np.zeros((N,) * k, dtype=dtype)
    C = combos(k)
    perms, signs = perm_table(k)
    for p, s in zip(perms, signs):
        idx = tuple(C[:, p[j]] for j in range(k))
        T[idx] = s * comp
    return T


def components(T, k):
    C = combos(k)
    return T[tuple(C[:, j] for j in range(k))]


@lru_cache(maxsize=None)
def hodge5_table():
    C = combos(5)
    index = {tuple(c): i for i, c in enumerate(C)}
    comp_idx = np.zeros(len(C), dtype=np.int64); sgn = np.zeros(len(C))
    for i, c in enumerate(C):
        rest = tuple(sorted(set(range(N)) - set(c)))
        comp_idx[i] = index[rest]
        sgn[i] = perm_parity(list(c) + list(rest))
    return comp_idx, sgn


def hodge5(comp):
    """components of *X for a 5-form X given by its 252 components: (*X)_I = sgn(I, I^c) X_{I^c}."""
    ci, s = hodge5_table()
    return s * comp[ci]


def random_fields(rng):
    A = rng.normal(size=(N, N)); A = A - A.T
    P = form_from_components(rng.normal(size=210), 4)
    H = rng.normal(size=N) + 1j * rng.normal(size=N)
    X = rng.normal(size=252) + 1j * rng.normal(size=252)
    Dc = X + 1j * hodge5(X)                                  # *D = -i D
    assert np.allclose(hodge5(Dc), -1j * Dc)
    D = form_from_components(Dc, 5, dtype=complex)
    return {"A": A, "P": P, "H": H, "Hb": np.conj(H), "D": D, "Db": np.conj(D)}


def rotate(fields, R):
    out = {}
    out["A"] = R @ fields["A"] @ R.T
    out["P"] = np.einsum("ai,bj,ck,dl,ijkl->abcd", R, R, R, R, fields["P"], optimize=True)
    out["H"] = R @ fields["H"]; out["Hb"] = R @ fields["Hb"]
    out["D"] = np.einsum("ai,bj,ck,dl,em,ijklm->abcde", R, R, R, R, R, fields["D"], optimize=True)
    out["Db"] = np.conj(out["D"])
    return out


def random_rotation(rng, det=1):
    Q, Rr = np.linalg.qr(rng.normal(size=(N, N)))
    Q = Q @ np.diag(np.sign(np.diag(Rr)))
    if np.linalg.det(Q) * det < 0:
        Q[:, 0] = -Q[:, 0]
    return Q


# ----------------------------------------------------------------------------------------------------------------
# multigraph enumeration
# ----------------------------------------------------------------------------------------------------------------
def multigraphs(types, with_eps):
    nodes = list(types) + (["eps"] if with_eps else [])
    deg = [RANKS[t] for t in nodes]
    n = len(nodes)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    res = []

    def rec(pi, rem, edges):
        if pi == len(pairs):
            if all(r == 0 for r in rem):
                res.append(dict(edges))
            return
        i, j = pairs[pi]
        # remaining pairs involving i after this one: if this is the last pair for node i, it must absorb rem[i]
        last_i = all(p[0] != i and p[1] != i for p in pairs[pi + 1:])
        lo = rem[i] if last_i else 0
        hi = min(rem[i], rem[j])
        if lo > hi:
            return
        for m in range(lo, hi + 1):
            rem[i] -= m; rem[j] -= m
            if m:
                edges[(i, j)] = m
            rec(pi + 1, rem, edges)
            if m:
                del edges[(i, j)]
            rem[i] += m; rem[j] += m

    rec(0, deg[:], {})
    # canonicalise under permutations of identical node types
    groups = {}
    for i, t in enumerate(nodes):
        groups.setdefault(t, []).append(i)
    perm_lists = [list(itertools.permutations(g)) for g in groups.values()]
    seen = set(); out = []
    for e in res:
        best = None
        for choice in itertools.product(*perm_lists):
            mp = {}
            for g, p in zip(groups.values(), choice):
                for a, b in zip(g, p):
                    mp[a] = b
            key = tuple(sorted((min(mp[i], mp[j]), max(mp[i], mp[j]), m) for (i, j), m in e.items()))
            if best is None or key < best:
                best = key
        if best not in seen:
            seen.add(best)
            out.append({"nodes": nodes, "edges": e})
    return out


def graph_slots(g):
    """assign index letters: returns per-node list of letters and the eps letters per node."""
    nodes = g["nodes"]
    slots = [[] for _ in nodes]
    li = 0
    eps_node = nodes.index("eps") if "eps" in nodes else None
    internal = []          # letters of tensor-tensor edges
    eps_k = [0] * len(nodes)
    for (i, j), m in sorted(g["edges"].items()):
        for _ in range(m):
            if eps_node is not None and (i == eps_node or j == eps_node):
                t = j if i == eps_node else i
                eps_k[t] += 1
            else:
                L = LETTERS[li]; li += 1
                slots[i].append(L); slots[j].append(L)
                internal.append(L)
    return slots, eps_k, internal


def einsum_string(g):
    slots, eps_k, internal = graph_slots(g)
    nodes = g["nodes"]
    if "eps" not in nodes:
        return ",".join("".join(s) for s in slots) + "->"
    # eps graphs: write eps explicitly with fresh capital letters for eps slots
    caps = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    parts = []; eps_letters = []
    for t, s in enumerate(slots):
        if nodes[t] == "eps":
            continue
        extra = "".join(next(caps) for _ in range(eps_k[t]))
        eps_letters.append(extra)
        parts.append("".join(s) + extra)
    return ",".join(parts) + "," + "".join(eps_letters) + "(eps)->"


# ----------------------------------------------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def wedge_terms(ks):
    """ordered set partitions of {0..9} into blocks of sizes ks: (list of index arrays into combos(k), signs)."""
    idx_lists = [[] for _ in ks]; signs = []
    cidx = [{tuple(c): i for i, c in enumerate(combos(k))} for k in ks]

    def rec(t, remaining, chosen):
        if t == len(ks):
            seq = [x for blk in chosen for x in blk]
            signs.append(perm_parity(seq))
            for u, blk in enumerate(chosen):
                idx_lists[u].append(cidx[u][blk])
            return
        for blk in itertools.combinations(remaining, ks[t]):
            rest = tuple(x for x in remaining if x not in blk)
            rec(t + 1, rest, chosen + [blk])

    rec(0, tuple(range(N)), [])
    return [np.array(l, dtype=np.int64) for l in idx_lists], np.array(signs, dtype=float)


def evaluate(g, F):
    nodes = g["nodes"]
    slots, eps_k, internal = graph_slots(g)
    if "eps" not in nodes:
        ops = []; subs = []
        for t, s in enumerate(slots):
            ops.append(F[nodes[t]]); subs.append("".join(s))
        return complex(np.einsum(",".join(subs) + "->", *ops, optimize="greedy"))
    # eps graph: loop (vectorised) over internal letters, wedge the residual forms
    tensors = [t for t in range(len(nodes)) if nodes[t] != "eps"]
    nint = len(internal)
    if nint:
        E = np.array(list(itertools.product(range(N), repeat=nint)), dtype=np.int64)
    else:
        E = np.zeros((1, 0), dtype=np.int64)
    lpos = {L: i for i, L in enumerate(internal)}
    ks = tuple(eps_k[t] for t in tensors)
    idx, sg = wedge_terms(ks)
    prod = np.ones((len(E), len(sg)), dtype=complex)
    for u, t in enumerate(tensors):
        T = F[nodes[t]]
        k = eps_k[t]
        C = combos(k)
        ind = tuple(E[:, lpos[L]][:, None] for L in slots[t]) + tuple(C[:, j][None, :] for j in range(k))
        form = np.asarray(T[ind])
        form = np.broadcast_to(form, (len(E), form.shape[-1])) if form.ndim == 2 else form.reshape(len(E), -1)
        prod *= form[:, idx[u]]
    return complex((prod @ sg).sum())


# ----------------------------------------------------------------------------------------------------------------
# structures
# ----------------------------------------------------------------------------------------------------------------
STRUCTURES = [
    # name, node types, expected EXACT count from census (None = must vanish), self-conjugate?, role
    ("A^2", ["A", "A"], 1, True, "new"),
    ("A^3", ["A", "A", "A"], 0, True, "new-vanishing"),
    ("A^4", ["A", "A", "A", "A"], 2, True, "new"),
    ("P A", ["P", "A"], 0, True, "new-vanishing"),
    ("P^2 A", ["P", "P", "A"], 1, True, "new"),
    ("P A^2", ["P", "A", "A"], 1, True, "new"),
    ("P^3 A", ["P", "P", "P", "A"], 2, True, "new"),
    ("P^2 A^2", ["P", "P", "A", "A"], 4, True, "new"),
    ("P A^3", ["P", "A", "A", "A"], 1, True, "new"),
    ("A H Hb", ["A", "H", "Hb"], 1, True, "new"),
    ("A^2 H Hb", ["A", "A", "H", "Hb"], 2, True, "new"),
    ("P A H Hb", ["P", "A", "H", "Hb"], 1, True, "new"),
    ("A D Db", ["A", "D", "Db"], 1, True, "new"),
    ("A^2 D Db", ["A", "A", "D", "Db"], 3, True, "new"),
    ("P A D Db", ["P", "A", "D", "Db"], 4, True, "new"),
    ("A Hb D", ["A", "Hb", "D"], 0, False, "new-vanishing"),
    ("A^2 Hb D", ["A", "A", "Hb", "D"], 1, False, "new"),
    ("P A Hb D", ["P", "A", "Hb", "D"], 3, False, "new"),
    ("A H H  [x S]", ["A", "H", "H"], 0, False, "new-vanishing"),
    ("A H D  [x S]", ["A", "H", "D"], 0, False, "new-vanishing"),
    ("A D D  [x S]", ["A", "D", "D"], 0, False, "new-vanishing"),
    # v20 calibration (attested counts)
    ("v20: P^2", ["P", "P"], 1, True, "v20"),
    ("v20: P^3 (O17)", ["P", "P", "P"], 1, True, "v20"),
    ("v20: P^2 H Hb (O46)", ["P", "P", "H", "Hb"], 3, True, "v20"),
    ("v20: P Hb D (O15)", ["P", "Hb", "D"], 1, False, "v20"),
    ("v20: P D Db (O14)", ["P", "D", "Db"], 1, True, "v20"),
    ("v20: P^2 Hb D (O45)", ["P", "P", "Hb", "D"], 2, False, "v20"),
    ("v20: H H Hb Hb (O36)", ["H", "H", "Hb", "Hb"], 2, True, "v20"),
    ("v20: H Hb D Db (O35)", ["H", "Hb", "D", "Db"], 2, True, "v20"),
    ("v20: Hb Hb D D (O31)", ["Hb", "Hb", "D", "D"], 1, False, "v20"),
    ("v20: Hb D D Db (O28)", ["Hb", "D", "D", "Db"], 1, False, "v20"),
    ("v20: P^2 D Db (O44)", ["P", "P", "D", "Db"], 6, True, "v20"),
    ("v20: P^4 (O48)", ["P", "P", "P", "P"], 4, True, "v20"),
]


def priority(g):
    """sort key for greedy basis selection: delta graphs first, then fewer edges to the most 'complex' fields."""
    has_eps = "eps" in g["nodes"]
    e = sorted(g["edges"].items())
    return (has_eps, len(e), tuple((i, j, -m) for (i, j), m in e))


def run_structure(name, types, expected, selfconj, role, rng_seed=20261017, verbose=True):
    t0 = time.time()
    with_eps_ok = not any(t in ("D", "Db") for t in types) and sum(RANKS[t] for t in types) >= 10
    graphs = multigraphs(types, False)
    if with_eps_ok:
        graphs += multigraphs(types, True)
    graphs.sort(key=priority)
    ng = len(graphs)
    nsamp = max(ng + 6, 12)
    rng = np.random.default_rng(rng_seed)
    samples = [random_fields(rng) for _ in range(nsamp)]
    V = np.zeros((ng, nsamp), dtype=complex)
    for i, g in enumerate(graphs):
        for s, F in enumerate(samples):
            V[i, s] = evaluate(g, F)
    norms = np.linalg.norm(V, axis=1)
    # identically-vanishing test against the natural magnitude prod_nodes ||field||_F (x sqrt(10!) for eps graphs)
    ref = np.array([[np.prod([np.linalg.norm(F[t]) for t in g["nodes"] if t != "eps"])
                     * (math.sqrt(math.factorial(10)) if "eps" in g["nodes"] else 1.0) for F in samples]
                    for g in graphs]).reshape(ng, nsamp)
    relmag = np.max(np.abs(V) / ref, axis=1) if ng else np.zeros(0)
    nonzero = relmag > 1e-11
    Vn = V[nonzero] / norms[nonzero, None] if nonzero.any() else np.zeros((0, nsamp))
    sv = np.linalg.svd(Vn, compute_uv=False) if len(Vn) else np.zeros(0)
    tol = 1e-8
    rank = int(np.sum(sv > tol * (sv[0] if len(sv) else 1)))
    # real-basis rank for self-conjugate structures (real coupling count)
    if selfconj and len(Vn):
        Vr = np.vstack([Vn.real, Vn.imag])
        Vr = Vr[np.linalg.norm(Vr, axis=1) > 1e-12]
        svr = np.linalg.svd(Vr, compute_uv=False)
        rank_real = int(np.sum(svr > tol * svr[0]))
    else:
        rank_real = None
    # greedy basis
    basis = []; Bm = np.zeros((0, nsamp), dtype=complex)
    for i, g in enumerate(graphs):
        if not nonzero[i]:
            continue
        cand = np.vstack([Bm, V[i] / norms[i]])
        s = np.linalg.svd(cand, compute_uv=False)
        if s[-1] > 1e-6 * s[0]:
            Bm = cand; basis.append(i)
        if len(basis) == rank:
            break
    sB = np.linalg.svd(Bm, compute_uv=False) if len(basis) else np.zeros(0)
    # invariance checks on the basis
    Rp = random_rotation(np.random.default_rng(7), +1)
    Rm = random_rotation(np.random.default_rng(8), -1)
    F0 = samples[0]; Fp = rotate(F0, Rp); Fm = rotate(F0, Rm)
    binfo = []
    for i in basis:
        g = graphs[i]
        v0 = V[i, 0]; vp = evaluate(g, Fp); vm = evaluate(g, Fm)
        rel = abs(vp - v0) / max(abs(v0), 1e-300)
        parity = "pseudo-scalar (eps)" if "eps" in g["nodes"] else "scalar"
        refl = abs(vm - (-v0 if "eps" in g["nodes"] else v0)) / max(abs(v0), 1e-300)
        vals = V[i]
        reality = ("real" if np.max(np.abs(vals.imag)) < 1e-9 * np.max(np.abs(vals)) else
                   "imaginary" if np.max(np.abs(vals.real)) < 1e-9 * np.max(np.abs(vals)) else "complex")
        binfo.append({"graph_edges": {f"{g['nodes'][a]}{a}-{g['nodes'][b]}{b}": m for (a, b), m in sorted(g["edges"].items())},
                      "einsum": einsum_string(g), "nodes": g["nodes"], "uses_eps": "eps" in g["nodes"],
                      "SO10_rotation_rel_change": float(rel), "O10_reflection_behaviour": parity,
                      "reflection_check_rel_err": float(refl), "value_type_on_physical_configs": reality})
    out = {"structure": name, "types": types, "role": role, "expected_exact_count": expected,
           "self_conjugate": selfconj, "n_candidate_graphs": ng, "eps_graphs_included": with_eps_ok,
           "n_identically_vanishing_graphs": int(ng - nonzero.sum()), "n_samples": nsamp,
           "max_relative_magnitude_of_vanishing_graphs": (float(np.max(relmag[~nonzero])) if (~nonzero).any() else None),
           "min_relative_magnitude_of_nonvanishing_graphs": (float(np.min(relmag[nonzero])) if nonzero.any() else None),
           "vanishing_graphs": [einsum_string(graphs[i]) for i in range(ng) if not nonzero[i]],
           "numerical_rank": rank, "rank_of_real_and_imag_parts": rank_real,
           "singular_values": [float(x) for x in sv[:rank + 3]],
           "gap_ratio_sv[rank]/sv[rank-1]": (float(sv[rank] / sv[rank - 1]) if 0 < rank < len(sv) else
                                             (0.0 if rank == len(sv) else None)),
           "basis_condition_number": (float(sB[0] / sB[-1]) if len(sB) else None),
           "agrees_with_character_count": rank == expected,
           "real_rank_agrees_for_selfconjugate": (rank_real == expected) if selfconj else None,
           "basis": binfo, "seconds": time.time() - t0}
    if verbose:
        print(f"{name:26s} graphs {ng:4d} (eps {'y' if with_eps_ok else 'n'})  rank {rank:2d}  expected {expected}  "
              f"{'OK ' if rank == expected else 'MISMATCH'}  realrank {rank_real}  "
              f"gap {out['gap_ratio_sv[rank]/sv[rank-1]']}  cond {out['basis_condition_number']}  "
              f"({out['seconds']:.1f}s)", flush=True)
    return out


def main():
    which = sys.argv[1:] if len(sys.argv) > 1 else None
    res = []
    for st in STRUCTURES:
        if which and not any(w in st[0] for w in which):
            continue
        res.append(run_structure(*st))
    allok = all(r["agrees_with_character_count"] for r in res)
    allrot = all(b["SO10_rotation_rel_change"] < 1e-8 and b["reflection_check_rel_err"] < 1e-8
                 for r in res for b in r["basis"])
    out = {"structures": res, "all_ranks_agree_with_exact_character_counts": allok,
           "all_basis_elements_SO10_invariant_and_parity_as_stated": allrot}
    tag = "" if not which else "_partial"
    (HERE / f"explicit_basis_v22{tag}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("ALL RANKS AGREE:", allok, "| invariance/parity checks:", allrot)


if __name__ == "__main__":
    main()
