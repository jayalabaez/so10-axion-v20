#!/usr/bin/env python3
"""Exact normalisation of the SO(10) Yukawa sums Sum_{A,j,k} |Y_{A,jk}|^2 for 16.16.10_H and 16.16.126bar_H, needed
for the two-loop gauge-Yukawa term Y = (1/d(G)) C2(16) Sum |Y|^2 = (1/8) Sum|Y|^2.

Construction: SO(10) Clifford algebra Gamma_a (32 x 32, Euclidean, {Gamma_a, Gamma_b} = 2 delta), chirality
Gamma_11 = (-i)^5 Gamma_1...Gamma_10 (so that Gamma_11^2 = 1), 16 = positive-chirality subspace, charge-conjugation
B with B Gamma_a B^-1 = Gamma_a^T (here: B = product of the five "imaginary" gammas).  The invariant bilinears
psi^T B Gamma_[a1..an] psi for n = 1 (10), 3 (120), 5 (126 + 126bar; the (anti)self-dual halves).  Restricting
to the 16, the symmetric bilinears are n = 1 and n = 5 (one duality half); the antisymmetric one is n = 3.

Normalisation of Y: y_t = Y10 means the single-component coupling nu^c L H_u (or Q u^c H_u) has coefficient 1 in
L = -(1/2) Y_{A,jk} psi_j psi_k Phi_A: with 16 x 16 -> 10 the 'ratio' lambda = Sum_{A,k} |M^A_{nu^c,k}|^2 / |M^{H_u^0}_{nu^c, nu}|^2;
Sum_{A,j,k}|M|^2 = 16 lambda.  For 126bar the reference entry is nu^c nu^c Delta_R^0 (coefficient 1: M_R = Y126 v_R).
Here we compute lambda_10 and lambda_126 = Sum_A Sum_k |M^A_{r,k}|^2 / max_A |M^A_{r,r'}|^2 with r = the nu^c weight
and the reference entry chosen as the diagonal nu^c nu^c entry (126bar) or the nu^c-L entry (10).
"""
from __future__ import annotations

import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

s1 = np.array([[0, 1], [1, 0]], dtype=complex)
s2 = np.array([[0, -1j], [1j, 0]])
s3 = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def kron(*ms):
    out = np.array([[1.0 + 0j]])
    for m in ms:
        out = np.kron(out, m)
    return out


# Standard construction of 10 Euclidean gamma matrices in 32 dims (5 pairs).
G = []
for k in range(5):
    pre = [s3] * k
    post = [I2] * (4 - k)
    G.append(kron(*pre, s1, *post))
    G.append(kron(*pre, s2, *post))
for a in range(10):
    for b in range(10):
        assert np.allclose(G[a] @ G[b] + G[b] @ G[a], 2 * np.eye(32) * (a == b))
G11 = G[0]
for a in range(1, 10):
    G11 = G11 @ G[a]
G11 = (-1j) ** 5 * G11
assert np.allclose(G11 @ G11, np.eye(32))
# Cartan generators Sigma_{2k-1,2k} = (i/2)[Gamma_{2k-1}, Gamma_{2k}]/2 -> eigenvalues +-1/2
H = [(-1j / 4) * (G[2 * k] @ G[2 * k + 1] - G[2 * k + 1] @ G[2 * k]) for k in range(5)]
for h in H:
    ev = np.linalg.eigvalsh(h)
    assert np.allclose(np.sort(ev), np.array([-0.5] * 16 + [0.5] * 16))
# charge conjugation B: B Gamma_a B^{-1} = Gamma_a^T.  Try products of subsets of gammas.
B = None
for choice in itertools.product([0, 1], repeat=10):
    M = np.eye(32, dtype=complex)
    for a in range(10):
        if choice[a]:
            M = M @ G[a]
    ok = all(np.allclose(M @ G[a] @ np.linalg.inv(M), G[a].T) for a in range(10))
    if ok:
        B = M
        break
assert B is not None
# 16: positive chirality eigenvectors; also simultaneous Cartan eigenbasis (weights)
# Build the weight basis: common eigenvectors of H_k restricted to G11 = +1.
Hs = sum(((3 ** k) * H[k] for k in range(5)))  # generic combination to split degeneracies
evals, evecs = np.linalg.eigh(Hs + 100 * G11)
P16 = evecs[:, evals > 0]  # chirality +1 block (100 +- 60.5 > 0)
assert P16.shape[1] == 16
weights = []
for j in range(16):
    v = P16[:, j]
    weights.append(tuple(round(float((v.conj() @ H[k] @ v).real) * 2) / 2 for k in range(5)))
# nu^c weight: (-1/2,-1/2,-1/2,-1/2,+1/2) in the convention B-L = -(2/3)(h1+h2+h3), T3R = (h4-h5)/2 (see k1 notes)
# (any colour-singlet, SU(2)_L-singlet weight with T3R = -1/2 works; by SO(10) symmetry lambda does not depend on it)
target = (-0.5, -0.5, -0.5, -0.5, 0.5)
idx_nuc = weights.index(target)
# L weights: colour singlet (h1=h2=h3 equal), SU(2)_L doublet: (h4+h5) = +-1 ... L = (+1/2,+1/2,+1/2, +-(1/2,1/2))
# Actually the 16 members: with chirality +, L has h1=h2=h3=+1/2 and (h4,h5) = (+,+) or (-,-).
results = {}


def antisym_product(idx):
    """Gamma_[a1...an] fully antisymmetrised (1/n! sum over permutations)."""
    n = len(idx)
    out = np.zeros((32, 32), dtype=complex)
    for perm in itertools.permutations(range(n)):
        sign = round(np.linalg.det(np.eye(n)[list(perm)]))
        m = np.eye(32, dtype=complex)
        for p_ in perm:
            m = m @ G[idx[p_]]
        out += sign * m
    return out / math.factorial(n)


def bilinears(n):
    """List of 16x16 matrices M^A = P16^T B Gamma_[A] P16 for all index sets A of size n."""
    mats = []
    for idx in itertools.combinations(range(10), n):
        M = P16.T @ B @ antisym_product(idx) @ P16
        mats.append((idx, M))
    return mats


for n in (1, 5):
    mats = bilinears(n)
    # symmetric check
    sym = all(np.allclose(M, M.T) for _, M in mats)
    asym = all(np.allclose(M, -M.T) for _, M in mats)
    # For n = 5: split into self-dual / anti-self-dual combinations: M(A) and M(dual A) with eps sign;
    # the 126 and 126bar halves are M_A +- i^? M_{*A}.  We take the eigen-decomposition of the duality map.
    if n == 5:
        # duality: Gamma_[A] Gamma_11 relates Gamma_[A] to Gamma_[*A]; on the 16 (chirality +1) the 5-forms are
        # automatically (anti)self-dual: Gamma_[A] P16 = Gamma_[A] G11 P16 = +- i Gamma_[*A] P16, so the 252 matrices
        # span only 126 independent ones.  Use an orthonormal basis of the span.
        stack = np.array([M.reshape(-1) for _, M in mats])
        u, s, vh = np.linalg.svd(stack, full_matrices=False)
        rank = int(np.sum(s > 1e-8 * s[0]))
        basis = vh[:rank] * 1.0  # orthonormal in the Frobenius sense
        # rescale so that each basis element has the same normalisation as a single Gamma_[A]-type component:
        # Frobenius norms of the raw M_A are all equal (SO(10) symmetry); use that norm.
        raw_norm = float(np.linalg.norm(mats[0][1]))
        comps = [b.reshape(16, 16) * raw_norm for b in basis]
    else:
        rank = len(mats)
        comps = [M for _, M in mats]
    total = sum(float(np.sum(np.abs(M) ** 2)) for M in comps)
    # invariant operator check: sum_A M^A M^A^dagger proportional to identity
    S = sum(M @ M.conj().T for M in comps)
    prop = float(S[0, 0].real)
    schur_ok = np.allclose(S, prop * np.eye(16), atol=1e-8 * prop)
    # row of nu^c: sum over A and k of |M^A_{nuc,k}|^2 = prop
    row = float(sum(np.sum(np.abs(M[idx_nuc, :]) ** 2) for M in comps))
    # reference entry: n=5: diagonal nu^c nu^c; n=1: max |M^A_{nuc,k}| over A,k (the nu^c L H_u entry)
    if n == 5:
        ref = max(abs(M[idx_nuc, idx_nuc]) ** 2 for M in comps)
        # there are generally 2 components (complex pair) with nonzero diagonal entry: use the sum over A of |M_{nuc,nuc}|^2
        ref_sum = float(sum(abs(M[idx_nuc, idx_nuc]) ** 2 for M in comps))
    else:
        ref = max(float(np.max(np.abs(M[idx_nuc, :]) ** 2)) for M in comps)
        ref_sum = None
    results[f"n={n}"] = {"n_components": rank, "symmetric": bool(sym), "antisymmetric": bool(asym),
                         "schur_proportional_to_identity": bool(schur_ok), "sum_all_|M|^2": total,
                         "row_nuc_sum": row, "ref_entry_|M|^2_max": float(ref), "ref_diag_sum_over_A": ref_sum,
                         "lambda_from_max_entry": row / ref, "sum_all_over_ref": total / ref}
    print(n, results[f"n={n}"])
# nu^c weight sanity
results["nu_c_weight"] = target
results["weights_16"] = [list(w) for w in weights]
with open(os.path.join(HERE, "k1_so10_yukawa_norm.json"), "w") as fh:
    json.dump(results, fh, indent=1)
