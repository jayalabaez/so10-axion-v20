#!/usr/bin/env python3
"""Check of the 16.16.10 normalisation: the nu^c-nu entry of the complex H_u^0 combination (phi_9 +- i phi_10)/sqrt2 has
|Y|^2 = 2 (one sign) and 0 (other sign) in raw units, so Y_raw = y_t/sqrt2 and Sum|Y|^2 = 160/2 = 80 y_t^2."""
from __future__ import annotations

import itertools
import json
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


G = []
for k in range(5):
    pre = [s3] * k
    post = [I2] * (4 - k)
    G.append(kron(*pre, s1, *post))
    G.append(kron(*pre, s2, *post))
G11 = G[0]
for a in range(1, 10):
    G11 = G11 @ G[a]
G11 = (-1j) ** 5 * G11
H = [(-1j / 4) * (G[2 * k] @ G[2 * k + 1] - G[2 * k + 1] @ G[2 * k]) for k in range(5)]
B = None
for choice in itertools.product([0, 1], repeat=10):
    M = np.eye(32, dtype=complex)
    for a in range(10):
        if choice[a]:
            M = M @ G[a]
    if all(np.allclose(M @ G[a] @ np.linalg.inv(M), G[a].T) for a in range(10)):
        B = M
        break
Hs = sum(((3 ** k) * H[k] for k in range(5)))
evals, evecs = np.linalg.eigh(Hs + 100 * G11)
P16 = evecs[:, evals > 0]
weights = []
for j in range(16):
    v = P16[:, j]
    weights.append(tuple(round(float((v.conj() @ H[k] @ v).real) * 2) / 2 for k in range(5)))
i_nuc = weights.index((-0.5, -0.5, -0.5, -0.5, 0.5))
i_nu = weights.index((0.5, 0.5, 0.5, 0.5, 0.5))
Ms = [P16.T @ B @ G[a] @ P16 for a in range(10)]
raw = {f"|M^{a+1}_(nuc,nu)|^2": float(abs(Ms[a][i_nuc, i_nu]) ** 2) for a in range(10)}
plus = abs((Ms[8][i_nuc, i_nu] + 1j * Ms[9][i_nuc, i_nu]) / np.sqrt(2)) ** 2
minus = abs((Ms[8][i_nuc, i_nu] - 1j * Ms[9][i_nuc, i_nu]) / np.sqrt(2)) ** 2
# all raw entries have |M| in {0, 1}?
vals = sorted(set(round(float(abs(x)), 6) for M in Ms for x in M.reshape(-1)))
row_sum = sum(float(np.sum(np.abs(M[i_nuc, :]) ** 2)) for M in Ms)
res = {"raw_entries_nuc_nu": raw, "|(M9+iM10)/sqrt2|^2": float(plus), "|(M9-iM10)/sqrt2|^2": float(minus),
       "distinct_|M|_values": vals, "row_sum_nuc": row_sum, "lambda10_in_yt_units": row_sum / max(plus, minus)}
print(json.dumps(res, indent=1))
with open(os.path.join(HERE, "k1_yukawa10_check.json"), "w") as fh:
    json.dump(res, fh, indent=1)
