#!/usr/bin/env python3
"""Point-independent preparation data for the v22-L2 vacuum tests (531 chart).

  unit   : singlet-channel unitarity traces  tr_A Hess_k(e_B)  for the 6 field blocks (K3 / R2-A trace lemma,
           extended by the A45 block) -> BIG/unit_traces.npz
  banks  : every deep configuration banked by R2-A (all descent banks + endpoints, K3 P831 banks), its skeptic
           (DPB/DPD endpoints), Stage-1 D-A (descend_D*_bank, skeptic_endpoints_bank) and the D-A skeptic runaway
           endpoints (sk_descend_*.npz) -> BIG/deep486.npz  (Q486, source, is_endpoint)
  rays   : BFB ray bank on the 531 unit sphere: random rays, every 1-/2-/3-block combination, H-Sigma(-S) rays with
           and without A, the old 486 ray banks embedded, the directions of the banked deep points -> BIG/rays.npz
           (Q unit rays, J4 = degree-4 row values)
  subfit : exact polynomial fit of V restricted to the SM-singlet subspace z = (p,a,omega,omega_R,omega_BL,|sigma|,
           |S|,|x|) -> BIG/subfit.npz (monomial exponents, Kfit with V_c(z) = X(z) . (Kfit c))
usage: python -B vprep.py unit|banks|rays|subfit
"""
from __future__ import annotations

import glob
import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

import vc

C = vc.C
R2A = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
           r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21R2\R2-A-vacuum-two-bidoublets")
DAC = vc.HERE.parents[1] / "stage1" / "D-A-chain"
BNAMES = list(vc.BLOCKS)


def unit_vectors():
    out = {}
    out["Phi210"] = C.g3211_point(1.0, 0, 0, 0, 0)
    h = np.zeros(10, complex)
    h[0] = 1 / math.sqrt(2)
    out["H10"] = C.g3211_point(0, 0, 0, 0, 0, h=h)
    out["Sigma126bar"] = C.g3211_point(0, 0, 0, 0, 0, sigma=1 / math.sqrt(2))
    out["S"] = C.g3211_point(0, 0, 0, 0, 0, s=1 / math.sqrt(2))
    out["Phi17"] = C.g3211_point(0, 0, 0, 0, 0, x=1 / math.sqrt(2))
    out["A45"] = C.g3211_point(0, 0, 0, 1.0, 0)
    return out


def do_unit():
    U = unit_vectors()
    TR = np.zeros((vc.NPAR, 6, 6))     # TR[k, A, B] = tr_A Hess_k(e_B)
    norms = {}
    for jb, Bn in enumerate(BNAMES):
        q = U[Bn]
        norms[Bn] = vc.block_norms(q)
        _, _, hess = vc.rows_at(q, hessian=True)
        for ia, An in enumerate(BNAMES):
            sl = vc.BLOCKS[An]
            TR[:, ia, jb] = np.einsum("kii->k", hess[:, sl, sl])
        print(Bn, norms[Bn], flush=True)
    nsz = np.array([vc.BLOCKS[b].stop - vc.BLOCKS[b].start for b in BNAMES], float)
    Mi = np.zeros_like(TR)
    for k in range(vc.NPAR):
        if vc.DEG[k] != 4:
            continue
        for ia in range(6):
            for jb in range(6):
                Mi[k, ia, jb] = TR[k, ia, jb] if ia == jb else math.sqrt(nsz[jb] / nsz[ia]) * TR[k, ia, jb]
    Mi = 0.5 * (Mi + np.transpose(Mi, (0, 2, 1)))
    # cross-check against the R2-A / K3 traces for the v20 rows (5 old blocks)
    chk = {}
    try:
        old = json.load(open(vc.HERE.parents[2] / "v21_kill_gates" / "round2" / "R2-A-vacuum-two-bidoublets" /
                             "unit_rows_traces.json", encoding="utf-8"))
        md = 0.0
        for k, pid in enumerate(vc.IDS):
            if pid in old["blocks"]["Phi210"]["traces"]:
                for jb, Bn in enumerate(BNAMES[:5]):
                    for ia, An in enumerate(BNAMES[:5]):
                        md = max(md, abs(old["blocks"][Bn]["traces"][pid][An] - TR[k, ia, jb]) /
                                 max(1.0, abs(TR[k, ia, jb])))
        chk["max_rel_diff_vs_R2A_unit_rows_traces"] = md
    except Exception as e:  # pragma: no cover
        chk["error"] = repr(e)
    print("cross-check", chk)
    np.savez(vc.BIG / "unit_traces.npz", TR=TR, Mi=Mi, ids=np.array(vc.IDS), blocks=np.array(BNAMES), nsz=nsz)
    json.dump(vc.jsonable({"norms": norms, "check": chk}), open(vc.BIG / "unit_traces.json", "w"), indent=1)


def do_banks():
    Q, src, endp = [], [], []

    def add(arr, name, is_end):
        arr = np.atleast_2d(np.asarray(arr, float))
        assert arr.shape[1] == 486, (name, arr.shape)
        for i, qq in enumerate(arr):
            Q.append(qq)
            src.append(f"{name}#{i}")
            endp.append(bool(is_end[i]) if hasattr(is_end, "__len__") else bool(is_end))

    for f in sorted(glob.glob(str(R2A / "descend_*_bank.npz"))):
        z = np.load(f)
        n = z["Q"].shape[0]
        add(z["Q"], "R2A/" + os.path.basename(f)[:-4], [i == n - 1 for i in range(n)])
    for f in sorted(glob.glob(str(R2A / "descend_*.npz"))):
        if f.endswith("_bank.npz"):
            continue
        z = np.load(f)
        for key in ("q", "qmin"):
            if key in z.files:
                add(z[key][None, :], "R2A/" + os.path.basename(f)[:-4] + ":" + key, True)
    for f in sorted(glob.glob(str(R2A / "skeptic" / "DP*_*.npz"))):
        z = np.load(f)
        add(z["qmin"][None, :], "R2Ask/" + os.path.basename(f)[:-4], True)
    for f in sorted(glob.glob(str(DAC / "vac" / "descend_*_bank.npz"))) + [str(DAC / "vac" / "skeptic_endpoints_bank.npz")]:
        z = np.load(f)
        n = z["Q"].shape[0]
        add(z["Q"], "DA/" + os.path.basename(f)[:-4], [i == n - 1 for i in range(n)] if "skeptic" not in f else [True] * n)
    for f in sorted(glob.glob(str(DAC / "vac" / "descend_*.npz"))):
        if f.endswith("_bank.npz"):
            continue
        z = np.load(f)
        for key in ("q", "qmin"):
            if key in z.files:
                add(z[key][None, :], "DA/" + os.path.basename(f)[:-4] + ":" + key, True)
    for f in sorted(glob.glob(str(DAC / "skeptic" / "sk_descend_*.npz"))):
        z = np.load(f)
        add(z["qbest"][None, :], "DAsk/" + os.path.basename(f)[:-4], True)
    Q = np.array(Q)
    # drop exact duplicates
    _, ui = np.unique(np.round(Q, 12), axis=0, return_index=True)
    ui = np.sort(ui)
    Q, src, endp = Q[ui], [src[i] for i in ui], np.array(endp)[ui]
    bn = np.array([[np.linalg.norm(q[sl]) for sl in list(vc.BLOCKS.values())[:5]] for q in Q])
    np.savez(vc.BIG / "deep486.npz", Q=Q, src=np.array(src), endpoint=endp, block_norms=bn)
    print(f"deep configurations: {len(Q)} ({int(endp.sum())} endpoints)")
    for s_, e_, b_ in list(zip(src, endp, bn))[:5]:
        print("  ", s_, e_, np.round(b_, 3))


def random_unit(rng, n):
    v = rng.normal(size=(n, vc.N))
    return v / np.linalg.norm(v, axis=1)[:, None]


def do_rays():
    rng = np.random.default_rng(531)
    rays = [random_unit(rng, 600)]
    sl = list(vc.BLOCKS.values())
    for r_ in (1, 2, 3):
        for combo in itertools.combinations(range(6), r_):
            n = 12 if r_ == 1 else (10 if r_ == 2 else 6)
            v = np.zeros((n, vc.N))
            for b in combo:
                x = rng.normal(size=(n, sl[b].stop - sl[b].start))
                x /= np.linalg.norm(x, axis=1)[:, None]
                v[:, sl[b]] = x * rng.uniform(0.3, 1.0, size=(n, 1))
            rays.append(v / np.linalg.norm(v, axis=1)[:, None])
    # H-Sigma(-S)(-Phi)(-A) rays with the deep-vacuum proportions |Sigma| ~ 1-5|Phi|, |H| ~ 1-2|Phi|
    n = 300
    v = np.zeros((n, vc.N))
    for name, lo, hi in (("Phi210", 0.3, 1.0), ("H10", 1.0, 2.0), ("Sigma126bar", 1.0, 5.0), ("S", 0.0, 2.0),
                         ("Phi17", 0.0, 1.5), ("A45", 0.0, 1.0)):
        s_ = vc.BLOCKS[name]
        x = rng.normal(size=(n, s_.stop - s_.start))
        x /= np.linalg.norm(x, axis=1)[:, None]
        v[:, s_] = x * rng.uniform(lo, hi, size=(n, 1))
    rays.append(v / np.linalg.norm(v, axis=1)[:, None])
    # old 486 ray banks (A = 0)
    for f in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):
        z = np.load(R2A / f)
        Q = np.hstack([z["Q"], np.zeros((z["Q"].shape[0], 45))])
        rays.append(Q / np.linalg.norm(Q, axis=1)[:, None])
    # directions of the banked deep points, with A = 0 and with a random A of 0.5 |q|
    deep = np.load(vc.BIG / "deep486.npz")["Q"]
    Q = np.hstack([deep, np.zeros((deep.shape[0], 45))])
    rays.append(Q / np.linalg.norm(Q, axis=1)[:, None])
    x = rng.normal(size=(deep.shape[0], 45))
    x *= (0.5 * np.linalg.norm(deep, axis=1) / np.linalg.norm(x, axis=1))[:, None]
    Q2 = np.hstack([deep, x])
    rays.append(Q2 / np.linalg.norm(Q2, axis=1)[:, None])
    R = np.vstack(rays)
    t0 = time.time()
    J = vc.J_values(R)
    J4 = J * (vc.DEG == 4)[None, :]
    print(f"rays: {R.shape[0]} unit rays, J in {time.time()-t0:.1f}s")
    np.savez_compressed(vc.BIG / "rays.npz", Q=R, J4=J4)


# ------------------------------------------------------------------------------------------------------------------
SUB_DEGS = np.array([1, 1, 1, 1, 1, 2, 2, 2])


def sub_monomials():
    mons = [pw for pw in itertools.product(range(5), repeat=8) if 2 <= int(np.dot(pw, SUB_DEGS)) <= 4]
    return np.array(mons, dtype=int)


def sub_var(z):
    z = np.atleast_2d(z)
    return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3], z[:, 4], z[:, 5] ** 2, z[:, 6] ** 2, z[:, 7] ** 2])


def sub_X(z, mons):
    v = sub_var(z)
    return np.prod(v[:, None, :] ** mons[None, :, :], axis=2)


def q_of_z(z):
    return C.g3211_point(z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7])


def do_subfit():
    mons = sub_monomials()
    rng = np.random.default_rng(88)
    n = 3 * len(mons)
    Z = np.column_stack([rng.uniform(-2, 2, (n, 5)), rng.uniform(0, 2, (n, 2)), rng.uniform(0, 5, (n, 1))])
    Q = np.array([q_of_z(z) for z in Z])
    t0 = time.time()
    J = vc.J_values(Q)
    X = sub_X(Z, mons)
    Kfit, *_ = np.linalg.lstsq(X, J, rcond=None)      # (n_mono, 85)
    resid = float(np.max(np.abs(X @ Kfit - J)) / max(1.0, np.max(np.abs(J))))
    # fresh check
    Z2 = np.column_stack([rng.uniform(-2, 2, (60, 5)), rng.uniform(0, 2, (60, 2)), rng.uniform(0, 5, (60, 1))])
    J2 = vc.J_values(np.array([q_of_z(z) for z in Z2]))
    resid2 = float(np.max(np.abs(sub_X(Z2, mons) @ Kfit - J2)) / max(1.0, np.max(np.abs(J2))))
    rank = int(np.linalg.matrix_rank(X))
    print(f"subfit: {len(mons)} monomials, rank {rank}, fit residual {resid:.2e}, fresh residual {resid2:.2e}, "
          f"{time.time()-t0:.1f}s")
    np.savez(vc.BIG / "subfit.npz", mons=mons, Kfit=Kfit, resid=resid, resid_fresh=resid2, rank=rank)


if __name__ == "__main__":
    {"unit": do_unit, "banks": do_banks, "rays": do_rays, "subfit": do_subfit}[sys.argv[1]]()
