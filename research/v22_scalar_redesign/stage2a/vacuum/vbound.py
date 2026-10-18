#!/usr/bin/env python3
"""Block-norm bounds of the quartic rows (for the sufficient 'dominance' BFB condition of vlp.py --bfb_dom).

For every degree-4 row k: its block multidegree n_k (Phi, H, Sigma, S, Phi17, A; H and H^dag both count as H) and the
range [l_k, u_k] of I_k on the product of the unit spheres of the blocks it involves, so that
      l_k prod_B |q_B|^{n_kB}  <=  I_k(q)  <=  u_k prod_B |q_B|^{n_kB}      for every q.
l_k, u_k are found by multistart L-BFGS on the product of spheres (NUM: the true range can only be wider than found,
so a safety factor is applied by the user of the bounds; vlp uses (l, u) widened by --dom_safety, default 10 %).
usage: python -B vbound.py [n_starts]  -> BIG/quartic_bounds.npz, quartic_bounds.json
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from scipy.optimize import minimize

import vc

C = vc.C
NST = int(sys.argv[1]) if len(sys.argv) > 1 else 24
BN = list(vc.BLOCKS)
block_of_var = np.zeros(vc.N, dtype=int)
for bi, (nm, sl) in enumerate(vc.BLOCKS.items()):
    block_of_var[sl] = bi


def multidegree(p):
    ix = p.idx.astype(np.int64)
    md = np.zeros((ix.shape[0], 6), dtype=int)
    for j in range(ix.shape[1]):
        np.add.at(md, (np.arange(ix.shape[0]), block_of_var[ix[:, j]]), 1)
    u = np.unique(md, axis=0)
    assert len(u) == 1, "row with mixed multidegrees"
    return u[0]


def extremes(k, md, rng):
    cvec = np.zeros(vc.NPAR)
    cvec[k] = 1.0
    F = vc.FastV(cvec)
    blocks = [b for b in range(6) if md[b] > 0]
    sls = [list(vc.BLOCKS.values())[b] for b in blocks]

    def embed(v):
        q = np.zeros(vc.N)
        off = 0
        for sl in sls:
            n = sl.stop - sl.start
            x = v[off:off + n]
            q[sl] = x / np.linalg.norm(x)
            off += n
        return q

    def fg(v, sign):
        q = embed(v)
        V, g = F.value_grad(q)
        gv = np.zeros_like(v)
        off = 0
        for sl in sls:
            n = sl.stop - sl.start
            x = v[off:off + n]
            nx = np.linalg.norm(x)
            u = x / nx
            gb = g[sl]
            gv[off:off + n] = (gb - u * (u @ gb)) / nx
            off += n
        return sign * V, sign * gv

    dim = sum(sl.stop - sl.start for sl in sls)
    lo, hi = np.inf, -np.inf
    for _ in range(NST):
        v0 = rng.normal(size=dim)
        for sign in (1.0, -1.0):
            r = minimize(fg, v0, args=(sign,), jac=True, method="L-BFGS-B", options={"maxiter": 600, "gtol": 1e-12})
            val = sign * r.fun
            lo = min(lo, val) if sign > 0 else lo
            hi = max(hi, val) if sign < 0 else hi
    return float(lo), float(hi)


T0 = time.time()
rng = np.random.default_rng(11)
rows = []
L = np.zeros(vc.NPAR)
U = np.zeros(vc.NPAR)
MD = np.zeros((vc.NPAR, 6), dtype=int)
for k, pid in enumerate(vc.IDS):
    p = vc.POLYS[pid]
    md = multidegree(p)
    MD[k] = md
    if p.degree != 4:
        continue
    lo, hi = extremes(k, md, rng)
    L[k], U[k] = lo, hi
    rows.append({"id": pid, "multidegree": dict(zip(BN, md.tolist())), "min": lo, "max": hi})
    print(f"{pid:45s} {md.tolist()} [{lo:+.6g}, {hi:+.6g}]  ({time.time()-T0:.0f}s)", flush=True)
np.savez(vc.BIG / "quartic_bounds.npz", L=L, U=U, MD=MD, ids=np.array(vc.IDS))
json.dump({"n_starts": NST, "rows": rows, "seconds": time.time() - T0}, open(vc.HERE / "quartic_bounds.json", "w"), indent=1)
print("done", time.time() - T0)
