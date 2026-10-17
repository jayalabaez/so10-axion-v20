"""SM-isotypic block reduction of the 51 per-parameter Hessians at a G3221 point.

usage: python -B k3_blocks.py <tag>
Reads <tag>_rows.npz, writes <tag>_blocks.npz and <tag>_blocks.json with, per SM isotypic component k:
  label, dimension D_k, multiplicity m_k, slice basis W_k (486 x m_k complex, field-block and T3R/B-L adapted),
  reduced Hessians A[k] (51 x m_k x m_k complex Hermitian), Goldstone vectors inside the slice,
and the stationarity data (rank of the 51 gradient rows, orthonormal row space).
"""
from __future__ import annotations

import sys
import json
import math
import numpy as np

import k3_common as K
from fractions import Fraction

tag = sys.argv[1]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz")
q = Z["q"]; grads = Z["grads"]; hess = Z["hess"]; ids = list(Z["ids"]); tangents = Z["tangents"]
C3, C2L, Y2, G = Z["C3"], Z["C2L"], Z["Y2"], Z["sm_generators"]
n_par = len(ids)
N = K.TOTAL

# --- symmetry tangents (orthonormal basis of the 35-dim orbit tangent space)
u, sv, _ = np.linalg.svd(tangents, full_matrices=False)
rank_T = int(np.sum(sv > 1e-9 * sv[0]))
T = u[:, :rank_T]
print(f"symmetry tangent rank = {rank_T}")

# --- stationarity: gradient matrix J (486 x 51); rank and row space
J = grads.T
uj, sj, vjt = np.linalg.svd(J, full_matrices=False)
rank_J = int(np.sum(sj > 1e-10 * sj[0]))
print(f"gradient rank = {rank_J}; singular values: {sj[:rank_J+2]}")
stat_rows = vjt[:rank_J]  # constraints stat_rows @ c = 0
# Ward check: grad is orthogonal to tangents
print(f"max |T^T J| = {np.max(np.abs(T.T @ J)):.3e}")

# --- isotypic decomposition by the generic Casimir combination
generic = C3 + math.pi * C2L + 7.0 * math.e * Y2
generic = 0.5 * (generic + generic.T)
cas, vec = np.linalg.eigh(generic)
order = np.argsort(cas)
cas, vec = cas[order], vec[:, order]
clusters = []
start = 0
while start < N:
    stop = start + 1
    while stop < N and abs(cas[stop] - cas[start]) <= 1e-6:
        stop += 1
    clusters.append((start, stop))
    start = stop
print(f"{len(clusters)} isotypic components")

COLOUR = {Fraction(0): ("1", 1), Fraction(4, 3): ("3", 3), Fraction(3): ("8", 8), Fraction(10, 3): ("6", 6)}
WEAK = {Fraction(0): ("1", 1), Fraction(3, 4): ("2", 2), Fraction(2): ("3", 3)}


def near(value, table):
    key = min(table, key=lambda f: abs(float(f) - value))
    assert abs(float(key) - value) < 1e-5, (value, table)
    return table[key]


# generic SM Lie-algebra element for highest-weight slices
rng = np.random.default_rng(7)
gamma = rng.normal(size=G.shape[0])
hgen = sum(g * Gk for g, Gk in zip(gamma, G))  # real antisymmetric
# T3R and B-L chart operators (real antisymmetric): T3R = (1/2)(-i) T3R_INTEGER, B-L = -(2/3)(-i) BL_INTEGER
T3R_op = 0.5 * K.candidate.chart_generator(K.hypercharge.T3R_INTEGER)
BL_op = -(2.0 / 3.0) * K.candidate.chart_generator(K.hypercharge.BL_INTEGER)
block_of = np.zeros(N, dtype=int)
for bi, (name, sl) in enumerate(K.BLOCKS.items()):
    block_of[sl] = bi
block_names = list(K.BLOCKS)

blocks = []
for (a, b) in clusters:
    E = vec[:, a:b]
    D = b - a
    c3 = float(np.mean(np.einsum("ij,jk,ki->i", E.T, C3, E)))
    c2 = float(np.mean(np.einsum("ij,jk,ki->i", E.T, C2L, E)))
    y2 = float(np.mean(np.einsum("ij,jk,ki->i", E.T, Y2, E)))
    cname, cdim = near(c3, COLOUR)
    wname, wdim = near(c2, WEAK)
    yabs = math.sqrt(max(y2, 0.0))
    yfrac = Fraction(yabs).limit_denominator(12)
    label = f"({cname},{wname})_|Y|={yfrac}"
    dR = cdim * wdim
    # highest-weight slice: max eigenvalue of i*hgen restricted to E
    Hc = 1j * (E.T @ hgen @ E)
    Hc = 0.5 * (Hc + Hc.conj().T)
    w, v = np.linalg.eigh(Hc)
    wmax = w[-1]
    sel = w > wmax - 1e-7
    m = int(np.sum(sel))
    W = E @ v[:, sel]  # 486 x m complex
    # field-block adapted + T3R/B-L adapted basis of the slice
    cols = []
    meta = []
    for bi, name in enumerate(block_names):
        P = (block_of == bi).astype(float)
        WB = W * P[:, None]
        uu, ss, _ = np.linalg.svd(WB, full_matrices=False)
        mB = int(np.sum(ss > 1e-8))
        if mB == 0:
            continue
        UB = uu[:, :mB]
        # diagonalise i*(T3R + sqrt2 * BL) within the sub-slice
        op = 1j * (UB.conj().T @ (T3R_op + math.sqrt(2.0) * BL_op) @ UB)
        op = 0.5 * (op + op.conj().T)
        ww, vv = np.linalg.eigh(op)
        UB2 = UB @ vv
        for j in range(mB):
            vj = UB2[:, j]
            t3r = float(np.real(vj.conj() @ (1j * T3R_op) @ vj))
            bl = float(np.real(vj.conj() @ (1j * BL_op) @ vj))
            cols.append(vj)
            meta.append({"block": name, "T3R": round(t3r, 6), "BL": round(bl, 6)})
    Wad = np.column_stack(cols)
    assert Wad.shape[1] == m, (Wad.shape, m)
    # orthonormality check
    gram = Wad.conj().T @ Wad
    assert np.max(np.abs(gram - np.eye(m))) < 1e-8
    # reduced Hessians
    A = np.array([Wad.conj().T @ hess[i] @ Wad for i in range(n_par)])
    A = 0.5 * (A + np.transpose(A.conj(), (0, 2, 1)))
    # Goldstones inside the slice
    Gk = Wad.conj().T @ T  # m x 35
    ug, sg, _ = np.linalg.svd(Gk, full_matrices=False)
    ng = int(np.sum(sg > 1e-7))
    gold = ug[:, :ng]
    ctype = 2 if (D == 2 * m * dR) else 1
    assert D == ctype * m * dR, (label, D, m, dR)
    blocks.append({"label": label, "D": D, "m": m, "dR": dR, "ctype": ctype, "n_goldstone": ng,
                   "meta": meta, "W": Wad, "A": A, "gold": gold, "casimir": [c3, c2, y2]})
    print(f"{label:22s} D={D:4d} m={m:2d} dR={dR:2d} ctype={ctype} goldstones={ng} cols={[ (x['block'][:3], x['T3R'], x['BL']) for x in meta]}")

total_gold = sum(b["n_goldstone"] * b["dR"] * b["ctype"] for b in blocks)
print(f"Goldstone real dimension from blocks = {total_gold} (expect {rank_T})")

np.savez_compressed(K.SCRATCH / f"{tag}_blocks.npz",
                    labels=np.array([b["label"] for b in blocks]),
                    m=np.array([b["m"] for b in blocks]), D=np.array([b["D"] for b in blocks]),
                    dR=np.array([b["dR"] for b in blocks]), ctype=np.array([b["ctype"] for b in blocks]),
                    ng=np.array([b["n_goldstone"] for b in blocks]),
                    stat_rows=stat_rows, T=T, ids=np.array(ids), q=q,
                    **{f"A{k}": b["A"] for k, b in enumerate(blocks)},
                    **{f"W{k}": b["W"] for k, b in enumerate(blocks)},
                    **{f"G{k}": b["gold"] for k, b in enumerate(blocks)})
with open(K.SCRATCH / f"{tag}_blocks.json", "w", encoding="utf-8") as f:
    json.dump({"tag": tag, "rank_T": rank_T, "rank_J": rank_J, "singular_values_J": sj[:rank_J + 2].tolist(),
               "blocks": [{k: v for k, v in b.items() if k not in ("W", "A", "gold")} for b in blocks]}, f, indent=1)
print("saved")
