#!/usr/bin/env python3
"""Build the data of one G3211/SM vacuum point of v22-L2 on the 531-real chart.

point = (p, a, omega, omega_R, omega_BL, r, s, x):  Phi210 = p P + a A + omega W, A45 = omega_R T3R + omega_BL T_BL,
Sigma = r sigma_std (SM singlet, T3R = +1, B-L = -2), S = s, Phi17 = x  (chart531.g3211_point; kinetic-normalised).
Writes BIG/pt_<tag>.npz + BIG/pt_<tag>.json:
  q*, values (85), gradient rows (85 x 531) -> stationarity row space (exact null space later),
  symmetry tangents (531 x 47) and ranks (expected 35 = 34 gauge + PQ for r != 0),
  SM isotypic decomposition (chart531.isotypic_components('SM')): per canonical component k a field-block adapted
  highest-weight slice W_k (531 x m_k complex), reduced Hessians A_k (85 x m_k x m_k), Goldstone vectors inside the
  slice, meta (field block, T3R, B-L, X of every slice vector),
  for the (1,2)_{1/2} component the neutral-component vectors (SU(2)_L lowering of the slice) for the EW composition map.
usage: python -B vpoint.py <tag> p a omega omega_R omega_BL r s x
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np

import vc

C = vc.C


def sm_blocks(q, hess, tangents):
    comps = [c for c in C.isotypic_components("SM") if c.canonical]
    ops = C.label_operators()
    T3R, BL = ops["T3R_op"], ops["BL_op"]
    Xg = C.u1x_generator().toarray()
    u, sv, _ = np.linalg.svd(tangents, full_matrices=False)
    rT = int(np.sum(sv > 1e-9 * sv[0]))
    Tn = u[:, :rT]
    block_of = np.zeros(vc.N, dtype=int)
    bnames = list(vc.BLOCKS)
    for bi, (nm, sl) in enumerate(vc.BLOCKS.items()):
        block_of[sl] = bi
    out = []
    for c in comps:
        W = c.hw
        cols, meta = [], []
        for bi, nm in enumerate(bnames):
            P = (block_of == bi).astype(float)
            WB = W * P[:, None]
            uu, ss, _ = np.linalg.svd(WB, full_matrices=False)
            mB = int(np.sum(ss > 1e-8))
            if mB == 0:
                continue
            UB = uu[:, :mB]
            op = 1j * (UB.conj().T @ (T3R + math.sqrt(2.0) * BL + 0.1 * math.pi * Xg) @ UB)
            op = 0.5 * (op + op.conj().T)
            ww, vv = np.linalg.eigh(op)
            UB2 = UB @ vv
            for j in range(mB):
                vj = UB2[:, j]
                meta.append({"block": nm, "T3R": round(float(np.real(vj.conj() @ (-1j * T3R) @ vj)), 6),
                             "BL": round(float(np.real(vj.conj() @ (-1j * BL) @ vj)), 6),
                             "X": round(float(np.real(vj.conj() @ (-1j * Xg) @ vj)), 6)})
                cols.append(vj)
        Wad = np.column_stack(cols)
        assert Wad.shape[1] == c.m, (c.label, Wad.shape, c.m)
        assert np.max(np.abs(Wad.conj().T @ Wad - np.eye(c.m))) < 1e-8
        A = np.einsum("ia,kij,jb->kab", Wad.conj(), hess, Wad, optimize=True)
        A = 0.5 * (A + np.transpose(A.conj(), (0, 2, 1)))
        Gk = Wad.conj().T @ Tn
        ug, sg, _ = np.linalg.svd(Gk, full_matrices=False)
        ng = int(np.sum(sg > 1e-7))
        out.append({"label": c.label, "m": c.m, "irrep_dim": c.irrep_dim, "self_conjugate": c.self_conjugate,
                    "colour": c.colour, "weak": c.weak, "Y": str(c.charges["Y"]),
                    "W": Wad, "A": A, "G": ug[:, :ng], "ng": ng, "meta": meta,
                    "real_mult": c.irrep_dim * (1 if c.self_conjugate else 2)})
    return out, rT


def lowering_L():
    """complex T^-_L = T1L - i T2L on the complexified chart (real antisymmetric generators; charge = -i G)."""
    import g3_sigma_hypercharge_audit_v20 as hc
    gens = [0.5 * C.generator(v).toarray() for v in hc.SU2L_INTEGER]
    # Hermitian charges Q_a = -i G_a ; T^- = Q_1 - i Q_2
    Q = [-1j * g for g in gens]
    T3 = 0.5 * C.generator(hc.T3L_INTEGER).toarray() * (-1j)
    # identify which pair (Q1, Q2) closes with T3: [Q1, Q2] = i T3
    best = None
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            comm = Q[i] @ Q[j] - Q[j] @ Q[i]
            err = np.max(np.abs(comm - 1j * T3))
            if best is None or err < best[0]:
                best = (err, i, j)
    _, i, j = best
    assert best[0] < 1e-10, best
    return Q[i] - 1j * Q[j], T3


def main():
    tag = sys.argv[1]
    p, a, om, oR, oBL, r, s, x = map(float, sys.argv[2:10])
    t0 = time.time()
    q = C.g3211_point(p, a, om, oR, oBL, r, s, x)
    vals, grads, hess = vc.rows_at(q, hessian=True, backend="poly")
    tangents, ranks = C.symmetry_matrix(q)
    blocks, rT = sm_blocks(q, hess, tangents)
    total_gold = sum(b["ng"] * b["real_mult"] for b in blocks)
    total_dim = sum(b["m"] * b["real_mult"] for b in blocks)
    # stationarity: J = grads^T (531 x 85); row space
    J = grads.T
    uj, sj, vjt = np.linalg.svd(J, full_matrices=False)
    rank_J = int(np.sum(sj > 1e-10 * sj[0]))
    ward = float(np.max(np.abs(tangents.T @ J)))
    # neutral vectors of the (1,2)_{1/2} component
    kd = [k for k, b in enumerate(blocks) if b["colour"] == "1" and b["weak"] == "2" and b["Y"] == "1/2"][0]
    Tm, T3 = lowering_L()
    Wd = blocks[kd]["W"]
    t3hw = np.real(np.einsum("ij,jk,ki->i", Wd.conj().T, T3, Wd))
    Nn = Tm @ Wd
    Nn = Nn / np.linalg.norm(Nn, axis=0)[None, :]
    t3n = np.real(np.einsum("ij,jk,ki->i", Nn.conj().T, T3, Nn))
    info = {"tag": tag, "point": {"p": p, "a": a, "omega": om, "omega_R": oR, "omega_BL": oBL, "r": r, "s": s, "x": x},
            "ranks": ranks, "rank_tangents": rT, "goldstone_from_blocks": total_gold, "dim_from_blocks": total_dim,
            "rank_stationarity_rows": rank_J, "sv_stationarity": sj[:rank_J + 3].tolist(), "ward_max": ward,
            "block_norms": vc.block_norms(q), "doublet_T3L_hw": t3hw.tolist(), "doublet_T3L_neutral": t3n.tolist(),
            "blocks": [{k: v for k, v in b.items() if k not in ("W", "A", "G")} for b in blocks],
            "seconds": time.time() - t0}
    np.savez_compressed(vc.BIG / f"pt_{tag}.npz", q=q, ids=np.array(vc.IDS), values=vals, grads=grads,
                        stat_rows=vjt[:rank_J], tangents=tangents, neutral=Nn, kd=kd,
                        labels=np.array([b["label"] for b in blocks]), m=np.array([b["m"] for b in blocks]),
                        real_mult=np.array([b["real_mult"] for b in blocks]),
                        **{f"A{k}": b["A"] for k, b in enumerate(blocks)},
                        **{f"W{k}": b["W"] for k, b in enumerate(blocks)},
                        **{f"G{k}": b["G"] for k, b in enumerate(blocks)})
    json.dump(vc.jsonable(info), open(vc.BIG / f"pt_{tag}.json", "w"), indent=1)
    print(f"[{tag}] ranks {ranks}; tangent rank {rT}; Goldstones from blocks {total_gold}; dims {total_dim}; "
          f"stationarity rank {rank_J}; Ward {ward:.2e}; {time.time()-t0:.1f}s")
    for b in blocks:
        comp = {}
        for mm in b["meta"]:
            comp[mm["block"]] = comp.get(mm["block"], 0) + 1
        print(f"   {b['label']:14s} m={b['m']:2d} ng={b['ng']} mult={b['real_mult']:2d} {comp}")


if __name__ == "__main__":
    main()
