#!/usr/bin/env python3
"""Full 531-chart descents of V_c at a coupling point (the D3 global search; NUMERICAL, exact polynomial V).

V_c = sum_k c_k I_k is evaluated as ONE exact polynomial (vc.FastV: value + gradient ~20 ms, exact Hessian-vector
products).  Each start: L-BFGS to convergence; then the lowest Hessian eigenvalue is computed by Lanczos (exact
Hessian-vector products) and, if negative (saddle), the descent is continued from a step along that eigenvector
(up to 6 escapes).  A start is a RUNAWAY if V < V* - 1e7 or |q| > 2e3 along the way (tree-level unboundedness).
Every endpoint is classified: dV = V_end - V*, block norms, gauge copy of q* (exact row-value vector), unbroken
so(10) stabiliser dimension (SM vacuum: 12; SU(2)_L or colour breaking: smaller), EW-doublet content.
Starts (comma list):
  random:<seed>:<n>        block-scaled random points around the vacuum scale (A included)
  hsray:<seed>:<n>         H-Sigma(-S) configurations |Sigma| ~ 1-5 |Phi*|, |H| ~ 1-2 |Phi*|, A in [0, 1.5]|A*|
  deep:<mode>              every banked deep configuration of R2-A / K3 / Stage-1 D-A (BIG/deep486.npz), embedded
                           with mode = A0 (A = 0), Astar (A = A* x |Phi_k|/|Phi*|) or Arand (random A, |A| ~ |A*|)
  deepend:<mode>           only the endpoints of those banks
  ew:<eps list>            q* + eps u_EW (the tuned doublet direction; '0.05/0.2/0.5/1')
  pert:<seed>:<n>:<scale>  q* + scale * random unit vector
  file:<npz>[:<max>]       starting points Q (n, 531 or 486) from a file
usage: python -B vdesc.py <pt_tag> <solution npz> <out> <starts> [--maxiter 4000] [--escapes 6]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time

import numpy as np
from scipy.optimize import minimize

import vc

C = vc.C
ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("sol")
ap.add_argument("out")
ap.add_argument("starts")
ap.add_argument("--maxiter", type=int, default=4000)
ap.add_argument("--escapes", type=int, default=6)
ap.add_argument("--runaway_V", type=float, default=1e7)
ap.add_argument("--runaway_q", type=float, default=2e3)
ap.add_argument("--first", type=int, default=0)
ap.add_argument("--every", type=int, default=1, help="process starts first, first+every, ... (job splitting)")
args = ap.parse_args()
T0 = time.time()
log = vc.Logger(vc.BIG / f"{args.out}.log")

P = np.load(vc.BIG / f"pt_{args.tag}.npz")
q0 = P["q"]
J0 = P["values"]
S = np.load(args.sol if (":" in args.sol) else vc.BIG / args.sol)
c = S["c"]
assert [str(x) for x in S["ids"]] == list(vc.IDS)
F = vc.FastV(c)
F4 = vc.FastV(c * (vc.DEG == 4))
RUN_DIRS = []
Vstar = float(c @ J0)
Vchk = F.value(q0)
_, g0 = F.value_grad(q0)
log(f"[{args.out}] point {args.tag}, solution {args.sol}: V* = {Vstar:.10g} (FastV {Vchk:.10g}), |grad V*| = {np.linalg.norm(g0):.2e}")
a_ew = S["a_ew"] if "a_ew" in S.files else np.zeros(0)
u_ew = None
if a_ew.size:
    u_ew = np.real(P["neutral"] @ a_ew)
    u_ew /= np.linalg.norm(u_ew)
nb = {k: float(np.linalg.norm(q0[sl])) for k, sl in vc.BLOCKS.items()}
Astar = q0[vc.BLOCKS["A45"]]
sl = list(vc.BLOCKS.items())


def rand_block(rng, name, norm):
    s_ = vc.BLOCKS[name]
    v = rng.normal(size=s_.stop - s_.start)
    return v / np.linalg.norm(v) * norm


def make_starts(spec):
    out = []
    for item in [x for x in spec.split(",") if x]:
        kind = item.split(":")[0]
        if kind == "random":
            _, seed, n = item.split(":")
            rng = np.random.default_rng(int(seed))
            for i in range(int(n)):
                q = np.zeros(vc.N)
                q[vc.BLOCKS["Phi210"]] = rand_block(rng, "Phi210", nb["Phi210"] * rng.uniform(0.3, 1.6))
                q[vc.BLOCKS["A45"]] = rand_block(rng, "A45", max(nb["A45"], 0.3) * rng.uniform(0.0, 1.6))
                q[vc.BLOCKS["H10"]] = rand_block(rng, "H10", rng.uniform(0.0, 1.5))
                q[vc.BLOCKS["Sigma126bar"]] = rand_block(rng, "Sigma126bar", rng.uniform(0.0, 1.5))
                q[vc.BLOCKS["S"]] = rand_block(rng, "S", rng.uniform(0.0, 1.5))
                q[vc.BLOCKS["Phi17"]] = rand_block(rng, "Phi17", nb["Phi17"] * rng.uniform(0.3, 1.3))
                out.append((f"random:{seed}:{i}", q))
        elif kind == "hsray":
            _, seed, n = item.split(":")
            rng = np.random.default_rng(int(seed))
            for i in range(int(n)):
                ph = nb["Phi210"] * rng.uniform(0.3, 1.2)
                q = np.zeros(vc.N)
                q[vc.BLOCKS["Phi210"]] = rand_block(rng, "Phi210", ph)
                q[vc.BLOCKS["H10"]] = rand_block(rng, "H10", ph * rng.uniform(1.0, 2.0))
                q[vc.BLOCKS["Sigma126bar"]] = rand_block(rng, "Sigma126bar", ph * rng.uniform(1.0, 5.0))
                q[vc.BLOCKS["S"]] = rand_block(rng, "S", ph * rng.uniform(0.0, 2.0))
                q[vc.BLOCKS["Phi17"]] = rand_block(rng, "Phi17", nb["Phi17"] * rng.uniform(0.5, 1.2))
                q[vc.BLOCKS["A45"]] = rand_block(rng, "A45", max(nb["A45"], 0.3) * rng.uniform(0.0, 1.5))
                out.append((f"hsray:{seed}:{i}", q))
        elif kind in ("deep", "deepend"):
            mode = item.split(":")[1]
            D = np.load(vc.BIG / "deep486.npz")
            Q486, src, endp = D["Q"], [str(s) for s in D["src"]], D["endpoint"]
            rng = np.random.default_rng(4242)
            for i, (qq, ss, ee) in enumerate(zip(Q486, src, endp)):
                if kind == "deepend" and not ee:
                    continue
                if mode == "A0":
                    A = np.zeros(45)
                elif mode == "Astar":
                    A = Astar * np.linalg.norm(qq[:210]) / nb["Phi210"]
                else:
                    A = rand_block(rng, "A45", max(nb["A45"], 0.3) * rng.uniform(0.5, 1.5))
                out.append((f"{kind}:{mode}:{ss}", np.concatenate([qq, A])))
        elif kind == "ew":
            assert u_ew is not None, "ew starts need an EW direction in the solution"
            for e in item.split(":")[1].split("/"):
                for sg in (1, -1):
                    out.append((f"ew:{sg * float(e)}", q0 + sg * float(e) * u_ew))
        elif kind == "pert":
            _, seed, n, scale = item.split(":")
            rng = np.random.default_rng(int(seed))
            for i in range(int(n)):
                v = rng.normal(size=vc.N)
                out.append((f"pert:{seed}:{i}", q0 + float(scale) * v / np.linalg.norm(v)))
        elif kind == "file":
            parts = item.split(":", 1)[1]
            mx = None
            if parts.count(":") and parts.rsplit(":", 1)[1].isdigit():
                parts, mx = parts.rsplit(":", 1)
                mx = int(mx)
            Z = np.load(parts if (":" in parts) else vc.BIG / parts)
            Q = Z["Q"]
            if Q.shape[1] == 486:
                Q = np.hstack([Q, np.zeros((len(Q), 45))])
            for i, qq in enumerate(Q[:mx]):
                out.append((f"file:{parts}#{i}", qq))
        else:
            raise SystemExit(f"start kind {kind}")
    return out


import vdcore


def descend(q_start, label):
    res, qe, q_run = vdcore.descend(F, q_start, Vstar, maxiter=args.maxiter, escapes=args.escapes,
                                    runaway_V=args.runaway_V, runaway_q=args.runaway_q)
    res["label"] = label
    if q_run is not None:
        u = q_run / np.linalg.norm(q_run)
        f0 = F4.degree4_value(u)
        fmin, umin = vdcore.quartic_min(F4, u)
        res["runaway_dir_V4"] = float(f0)
        res["runaway_refined_V4"] = float(fmin)
        RUN_DIRS.append(umin)
        RUN_DIRS.append(u)
    return res, qe


def classify(q):
    out = {"block_norms": vc.block_norms(q), "|q|": float(np.linalg.norm(q))}
    J = vc.J_values(q[None, :])[0]
    out["gauge_copy_of_vacuum"] = bool(np.max(np.abs(J - J0)) <= 1e-7 * max(1.0, np.max(np.abs(J0))))
    T = C.gauge_tangents(q)
    s_ = np.linalg.svd(T, compute_uv=False)
    rank = int(np.sum(s_ > 1e-7 * s_[0])) if s_[0] > 0 else 0
    out["so10_stabiliser_dim"] = 45 - rank
    # EW breaking: SU(2)_L generators acting on q
    import g3_sigma_hypercharge_audit_v20 as hc
    TL = np.column_stack([C.generator(v) @ q for v in hc.SU2L_INTEGER])
    out["su2L_breaking_norm"] = float(np.linalg.norm(TL))
    return out, J


starts = make_starts(args.starts)
starts = starts[args.first::args.every]
log(f"{len(starts)} starts")
results = []
BQ, BJ = [], []
for i, (lab, qs) in enumerate(starts):
    t1 = time.time()
    res, qe = descend(qs, lab)
    info, J = classify(qe)
    res.update(info)
    res["start_block_norms"] = vc.block_norms(qs)
    res["seconds"] = time.time() - t1
    res["lower"] = bool(res["V_end-V*"] < -1e-8 * max(1.0, abs(Vstar))) and not info["gauge_copy_of_vacuum"]
    results.append(res)
    BQ.append(qe)
    BJ.append(J)
    bn = info["block_norms"]
    log(f"  [{i}] {lab[:60]:60s} dV = {res['V_end-V*']:+.6g}{' RUNAWAY' if res['runaway'] else ''} "
        f"stab {info['so10_stabiliser_dim']} SU2L {info['su2L_breaking_norm']:.3g} copy {info['gauge_copy_of_vacuum']} "
        f"lam {res['lam_min'] if res['lam_min'] is None else round(res['lam_min'], 8)} esc {res['escapes']} "
        f"|Phi| {bn['Phi210']:.3f} |H| {bn['H10']:.3f} |Sig| {bn['Sigma126bar']:.3f} |S| {bn['S']:.3f} "
        f"|X| {bn['Phi17']:.3f} |A| {bn['A45']:.3f} ({res['seconds']:.0f}s)")
    np.savez_compressed(vc.BIG / f"{args.out}_bank.npz", Q=np.array(BQ), J=np.array(BJ), ids=np.array(vc.IDS),
                        dV=np.array([r_["V_end-V*"] for r_ in results]),
                        lower=np.array([r_["lower"] for r_ in results]), runaway=np.array([r_["runaway"] for r_ in results]),
                        run_dirs=np.array(RUN_DIRS) if RUN_DIRS else np.zeros((0, vc.N)))
    json.dump(vc.jsonable({"tag": args.tag, "sol": args.sol, "V_star": Vstar, "results": results}),
              open(vc.BIG / f"{args.out}.json", "w"), indent=1)
n_lower = sum(r_["lower"] for r_ in results)
n_run = sum(r_["runaway"] for r_ in results)
log(f"SUMMARY {args.out}: {len(results)} descents, {n_lower} lower than V* (runaways {n_run}); "
    f"deepest {min([r_['V_end-V*'] for r_ in results] + [0.0]):.6g}; {time.time()-T0:.0f}s")
