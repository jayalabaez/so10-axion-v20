#!/usr/bin/env python3
"""D2 proxy fit, improved search: (R) renormalisable 10+126bar global search (DE, several seeds, batched least-squares
polish of the best distinct members), then (A) continuation: the d=5 120-like term A (and optionally type II) is
switched on from each renormalisable candidate with many random initialisations + basin hopping.
Physics and bounds: d2_batch.Problem (see its docstring and d2_proxy.py)."""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d2_batch as B  # noqa: E402
import d2_proxy as P  # noqa: E402

LIGHT = {"BOP": [(1e3, (0.0, 0.0, 0.5)), (1.7e9, (0.0, 8 / 3, 1.5))], "none": [],
         "L3": [(1e3, (0.0, 0.0, 0.5)), (1.06e11, (0.4, 4.0, 2.5))]}


def polish(prob, x0, max_nfev=4000):
    lo = np.array([b[0] for b in prob.bounds]); hi = np.array([b[1] for b in prob.bounds])

    def jac(x):
        h = 1e-6 * (1 + np.abs(x))
        Xs = np.vstack([x[None]] + [x[None] + np.eye(len(x))[k:k + 1] * h[k] for k in range(len(x))])
        Rb = prob.evaluate(Xs)
        return ((Rb[1:] - Rb[0][None]) / h[:, None]).T
    x0 = np.clip(x0, lo + 1e-9, hi - 1e-9)
    try:
        ls = least_squares(lambda x: prob.evaluate(x[None])[0], x0, bounds=(lo, hi), jac=jac, method="trf",
                           max_nfev=max_nfev, x_scale="jac")
        return ls.x, float(np.sum(ls.fun ** 2))
    except Exception:
        return x0, float(prob.chi2(x0[None])[0])


def stage_R(probR, seeds, popsize, maxiter, ntop=10):
    cands = []
    for sd in seeds:
        t0 = time.time()
        res = differential_evolution(lambda Xt: probR.chi2(Xt.T), probR.bounds, popsize=popsize, maxiter=maxiter,
                                     seed=sd, tol=1e-12, polish=False, vectorized=True, updating="deferred",
                                     mutation=(0.5, 1.0), recombination=0.9, init="sobol")
        pop, en = res.population, res.population_energies
        order = np.argsort(en)
        kept = []
        for idx in order:
            if any(np.linalg.norm(pop[idx] - y) < 0.05 for y in kept):
                continue
            kept.append(pop[idx])
            if len(kept) >= 4:
                break
        for x0 in kept:
            x, c = polish(probR, x0)
            cands.append((c, x))
        print(f"  [R] seed {sd}: DE {res.fun:.2f} -> best polished {min(c for c, _ in cands[-len(kept):]):.2f} "
              f"({time.time() - t0:.0f}s)", flush=True)
    cands.sort(key=lambda z: z[0])
    out = []
    for c, x in cands:
        if any(np.linalg.norm(x - y) < 0.05 for _, y in out):
            continue
        out.append((c, x))
        if len(out) >= ntop:
            break
    return out


def stage_A(probA, candsR, ninit, hops, rng):
    nR = 18
    best = None
    t0 = time.time()
    for ci, (cR, xR) in enumerate(candsR):
        local_best = None
        for k in range(ninit):
            x = np.zeros(probA.n)
            x[:nR] = xR[:nR]
            if probA.nA:
                sc = [0.3, 1.0, 3.0, 10.0][k % 4]
                x[18:24] = rng.normal(scale=sc, size=6)
                x[24] = rng.normal(scale=1.0)
                x[25] = rng.choice([-1.0, 1.0]) * rng.uniform(0.2, 2.0)
            if probA.nt:
                i0 = 18 + probA.nA
                x[i0] = rng.uniform(-2, 1); x[i0 + 1] = rng.uniform(-math.pi, math.pi)
            xp, c = polish(probA, x)
            if local_best is None or c < local_best[1]:
                local_best = (xp, c)
        xb, cb = local_best
        for h in range(hops):
            xp = xb.copy()
            xp[:nR] += rng.normal(scale=0.02, size=nR)
            if probA.nA:
                xp[18:26] += rng.normal(scale=0.3, size=8) * (1 + np.abs(xp[18:26]))
            if probA.nt:
                i0 = 18 + probA.nA
                xp[i0:i0 + 2] += rng.normal(scale=0.3, size=2)
            x2, c2 = polish(probA, xp)
            if c2 < cb:
                xb, cb = x2, c2
        print(f"  [A] cand {ci} (renorm {cR:.2f}) -> {cb:.3f} ({time.time() - t0:.0f}s)", flush=True)
        if best is None or cb < best[1]:
            best = (xb, cb)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--MU", type=float, default=1.28e16)
    ap.add_argument("--light", default="BOP")
    ap.add_argument("--typeII", type=int, default=0)
    ap.add_argument("--useA", type=int, default=1)
    ap.add_argument("--kappa", type=float, default=0.01)
    ap.add_argument("--c5max", type=float, default=1.0)
    ap.add_argument("--siglo", type=float, default=2e12)
    ap.add_argument("--sighi", type=float, default=1e15)
    ap.add_argument("--Arange", type=float, default=60.0)
    ap.add_argument("--off", type=float, default=0.3)
    ap.add_argument("--seeds", default="1,2,3,4")
    ap.add_argument("--popsize", type=int, default=40)
    ap.add_argument("--maxiter", type=int, default=6000)
    ap.add_argument("--ntop", type=int, default=8)
    ap.add_argument("--ninit", type=int, default=12)
    ap.add_argument("--hops", type=int, default=15)
    ap.add_argument("--Rfile", default=None, help="reuse renormalisable candidates from an earlier run (npz)")
    ap.add_argument("--floor", type=float, default=0.01)
    ap.add_argument("--nuse", type=int, default=99, help="use only the best n renormalisable candidates in stage A")
    ap.add_argument("--eta1", type=float, default=1.0)
    ap.add_argument("--eps_fixed", type=float, default=None)
    a = ap.parse_args()
    T, S, info = P.make_targets(a.MU, LIGHT[a.light], floor=a.floor)
    base = dict(kappa_phi=a.kappa, c5_max=a.c5max, sigma_lo=a.siglo, sigma_hi=a.sighi, Arange=a.Arange, off=a.off,
                eta1=a.eta1, eps_fixed=a.eps_fixed)
    probR = B.Problem(T, S, dict(base, use_A=False, typeII=False))
    probA = B.Problem(T, S, dict(base, use_A=bool(a.useA), typeII=bool(a.typeII)))
    print("label", a.label, base, "useA", a.useA, "typeII", a.typeII, "MU", a.MU, "light", a.light, flush=True)
    rng = np.random.default_rng(12345)
    if a.Rfile:
        z = np.load(HERE / a.Rfile)
        candsR = [(float(c), x) for c, x in zip(z["c"], z["x"])]
        # re-evaluate under this run's sigma window
        candsR = [(float(probR.chi2(x[None])[0]), x) for _, x in candsR]
        candsR.sort(key=lambda t: t[0])
        print("  [R] reused", len(candsR), "candidates; best under this window", candsR[0][0], flush=True)
    else:
        candsR = stage_R(probR, [int(s) for s in a.seeds.split(",")], a.popsize, a.maxiter, a.ntop)
        np.savez(HERE / f"d2c_{a.label}_R.npz", c=np.array([c for c, _ in candsR]), x=np.array([x for _, x in candsR]))
    smR = B.summary(probR, candsR[0][1])
    print("  [R] best renormalisable:", round(candsR[0][0], 3), "chi2_obs", round(smR["chi2_obs"], 3),
          "sigma_max %.3g" % smR["derived"]["sigma_max"], flush=True)
    out = {"label": a.label, "opts": dict(base, useA=a.useA, typeII=a.typeII), "MU": a.MU, "light": a.light,
           "renorm_best": smR, "renorm_totals": [c for c, _ in candsR]}
    if a.useA or a.typeII:
        best = stage_A(probA, candsR[: a.nuse], a.ninit, a.hops, rng)
        sm = B.summary(probA, best[0])
        sm["total"] = best[1]; sm["x"] = best[0].tolist()
        out["with_d5"] = sm
        print(json.dumps({k: v for k, v in sm.items() if k != "x"}, indent=1, default=str), flush=True)
    out["targets"] = {k: float(v) for k, v in zip(B.KEYS, T)}
    out["errors"] = {k: float(v) for k, v in zip(B.KEYS, S)}
    (HERE / f"d2c_{a.label}.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
