"""Singlet-channel tree s-wave amplitude a0 of the quartic potential sum_i c_i D_i (degree-4 directions only).

Method (the repo's exact lemma, g3_sm_pati_salam_witness_unitarity_v20 (A), re-derived here): with the five
G-irreducible blocks A (n_A real components) and unit chart vectors e_A,
   alpha_A      = Tr_A Hess V4(e_A),       beta_{A|B} = Tr_A Hess V4(e_B)  (A != B),
   M_AA = alpha_A,  M_AB = sqrt(n_B/n_A) beta_{A|B},   a0 = eig(M)/(16 pi).
Calibration: V = lambda (H^dag H)^2 on a complex doublet gives a0 = 3 lambda/(8 pi).
usage: python -B k3_unitarity.py <solution npz with c, ids>  [scale]
"""
from __future__ import annotations
import sys, json, math, numpy as np
import k3_common as K

sol = np.load(sys.argv[1]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
T = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8"))
degrees = T["degrees"]; blocks = list(K.BLOCKS); n = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in blocks}


def a0_of(c):
    beta = np.zeros((5, 5))  # beta[A,B] = Tr_A Hess V4(e_B)
    for jb, Bn in enumerate(blocks):
        tr = T["blocks"][Bn]["traces"]
        for i, pid in enumerate(ids):
            if degrees[pid.split("::")[1]] != 4: continue
            for ia, An in enumerate(blocks):
                beta[ia, jb] += c[i] * tr[pid][An]
    M = np.zeros((5, 5))
    for ia, An in enumerate(blocks):
        for jb, Bn in enumerate(blocks):
            M[ia, jb] = beta[ia, jb] if ia == jb else math.sqrt(n[Bn] / n[An]) * beta[ia, jb]
    sym = np.max(np.abs(M - M.T))
    w = np.linalg.eigvalsh(0.5 * (M + M.T))
    return w / (16 * math.pi), beta, M, sym


a0, beta, M, sym = a0_of(scale * c)
print("blocks:", blocks, "n =", n)
print("beta[A|B] = Tr_A Hess V4(e_B):\n", np.array2string(beta, precision=4))
print("symmetry check n_B beta_AB == n_A beta_BA: max asym of M =", sym)
print("a0 eigenvalues (singlet channel):", np.array2string(a0, precision=4))
print("max |a0| =", np.max(np.abs(a0)), " -> rescale factor for |a0|<=1/2:", 0.5 / np.max(np.abs(a0)))
json.dump({"scale": scale, "a0": a0.tolist(), "beta": beta.tolist(), "M": M.tolist(), "max_abs_a0": float(np.max(np.abs(a0))),
           "rescale_for_half": float(0.5 / np.max(np.abs(a0)))}, open(str(sys.argv[1]).replace(".npz", "_unitarity.json"), "w"), indent=1)
