#!/usr/bin/env python3
"""Fresh descents at a coupling point with MY OWN driver and MY OWN start families; every end point that is lower
than V* is re-evaluated with my independent evaluator (vsk_eval: repo v20 direction values + my tensor A rows).

Search engine: vc.FastV (the tester's exact polynomial; it agrees with vsk_eval to ~1e-13 relative, vsk_validate.json)
driven by scipy trust-krylov (exact Hessian-vector products) - a different algorithm from the tester's L-BFGS - with
an L-BFGS pre-phase for far starts, a dense-Hessian saddle check at the end and escapes along negative curvature.
Start families (new seeds, none of them the tester's):
  rnd      block-scaled random points, wider scale ranges than the tester's (|Sigma|, |H| up to 3 |Phi*|)
  hsa      CONSTRAINED descents in the H-Sigma-A(-S) sector: Phi210 frozen at 0, at Phi* or at 0.5 Phi*, (H, Sigma, A, S,
           Phi17) minimised first, then everything released
  light    q* + a u, u a random unit vector in the light subspace (octets / sextets / doublet), a = 0.03 .. 0.6
  orbit    random finite SO(10) x U(1)_X x PQ images of the tester's lower end points, perturbed by 0.05 (basin test)
usage: python -B vsk_descend.py <solution npz> <out tag> <families e.g. rnd:16,hsa:12,light:12,orbit:6> [--seed 7]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time

import numpy as np
from scipy.optimize import minimize

import vsk_eval as E

sys.path.insert(0, str(E.HERE.parent))
import vc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("sol")
ap.add_argument("out")
ap.add_argument("fams")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--bank", default="")
ap.add_argument("--first", type=int, default=0)
ap.add_argument("--every", type=int, default=1)
args = ap.parse_args()
log = open(E.BIGS / f"{args.out}.log", "a", encoding="utf-8")


def say(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()


P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
c = E.load_c(args.sol)
cv = np.array([c[p] for p in vc.IDS])
F = vc.FastV(cv)
Vs_fast = F.value(qs)
Vs_mine = E.V(qs, c)
say(f"[{args.out}] sol {args.sol}: V* FastV {Vs_fast:.12g} mine {Vs_mine:.12g}")
BL = vc.BLOCKS
nb = {k: float(np.linalg.norm(qs[s])) for k, s in BL.items()}
rng = np.random.default_rng(args.seed)
H0 = F.hessian(qs)
w0, U0 = np.linalg.eigh(H0)
Ulight = U0[:, (w0 > 1e-9) & (w0 < 3e-5)]


def rb(name, norm):
    s = BL[name]
    v = rng.normal(size=s.stop - s.start)
    return v / np.linalg.norm(v) * norm


def starts():
    out = []
    for item in args.fams.split(","):
        kind, n = item.split(":")
        n = int(n)
        for i in range(n):
            if kind == "rnd":
                q = np.zeros(vc.N)
                q[BL["Phi210"]] = rb("Phi210", rng.uniform(0.0, 1.8))
                q[BL["A45"]] = rb("A45", rng.uniform(0.0, 2.0))
                q[BL["H10"]] = rb("H10", rng.uniform(0.0, 3.0))
                q[BL["Sigma126bar"]] = rb("Sigma126bar", rng.uniform(0.0, 3.0))
                q[BL["S"]] = rb("S", rng.uniform(0.0, 2.0))
                q[BL["Phi17"]] = rb("Phi17", nb["Phi17"] * rng.uniform(0.2, 1.5))
                out.append((f"rnd:{i}", q, None))
            elif kind == "hsa":
                mode = i % 3
                q = np.zeros(vc.N)
                q[BL["Phi210"]] = qs[BL["Phi210"]] * (0.0, 1.0, 0.5)[mode]
                q[BL["A45"]] = rb("A45", rng.uniform(0.3, 2.0))
                q[BL["H10"]] = rb("H10", rng.uniform(0.0, 1.5))
                q[BL["Sigma126bar"]] = rb("Sigma126bar", rng.uniform(0.3, 2.0))
                q[BL["S"]] = rb("S", rng.uniform(0.0, 1.0))
                q[BL["Phi17"]] = qs[BL["Phi17"]]
                frozen = np.zeros(vc.N, bool)
                frozen[BL["Phi210"]] = True
                out.append((f"hsa:Phi={('0', 'Phi*', '0.5Phi*')[mode]}:{i}", q, frozen))
            elif kind == "light":
                x = rng.normal(size=Ulight.shape[1])
                u = Ulight @ x
                u /= np.linalg.norm(u)
                a = float(np.exp(rng.uniform(math.log(0.03), math.log(0.6))))
                out.append((f"light:a={a:.3f}:{i}", qs + a * u, None))
            elif kind == "orbit":
                Z = np.load(args.bank)
                Q = Z["Q"]
                q = Q[rng.integers(len(Q))]
                t = E.tensors(q)
                t = E.phase(E.phase(E.rotate(t, E.random_rotation(rng)), E.XCH, rng.uniform(0, 6.3)), E.pq_charges(),
                            rng.uniform(0, 6.3))
                q2 = E.pack(t)
                v = rng.normal(size=vc.N)
                out.append((f"orbit:{i}", q2 + 0.05 * v / np.linalg.norm(v), None))
    return out


def descend(q, frozen=None):
    q = q.copy()
    if frozen is not None:
        free = ~frozen
        qf = q.copy()

        def fg(x):
            qf[free] = x
            V, g = F.value_grad(qf)
            return V, g[free]
        r = minimize(fg, q[free], jac=True, method="L-BFGS-B",
                     options={"maxiter": 3000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10})
        q[free] = r.x
    # unconstrained: L-BFGS pre-phase then trust-krylov polish
    r = minimize(lambda x: F.value_grad(x), q, jac=True, method="L-BFGS-B",
                 options={"maxiter": 3000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10})
    q = r.x
    if np.linalg.norm(q) > 1e3:
        return q, "runaway?"
    esc = 0
    for _ in range(8):
        try:
            r = minimize(lambda x: F.value(x), q, jac=lambda x: F.value_grad(x)[1], hessp=lambda x, p: F.hvp(x, p),
                         method="trust-krylov", options={"maxiter": 200, "gtol": 1e-11})
            q = r.x
        except Exception:
            pass
        H = F.hessian(q)
        w, Uv = np.linalg.eigh(H)
        if w[0] < -1e-6:
            step = max(1e-3, min(0.3, math.sqrt(-w[0])))
            cands = [q + step * Uv[:, 0], q - step * Uv[:, 0]]
            q = min(cands, key=F.value)
            q = minimize(lambda x: F.value_grad(x), q, jac=True, method="L-BFGS-B",
                         options={"maxiter": 3000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10}).x
            esc += 1
            continue
        return q, f"min (lam_min {w[0]:.2e}, esc {esc})"
    return q, f"saddle? (esc {esc})"


S = starts()[args.first::args.every]
say(f"{len(S)} starts")
res, Qs = [], []
for lab, q0, frozen in S:
    t1 = time.time()
    qe, status = descend(q0, frozen)
    Vf = F.value(qe)
    dVf = Vf - Vs_fast
    rec = {"label": lab, "dV_fast": dVf, "status": status,
           "block_norms": {k: float(np.linalg.norm(qe[s])) for k, s in BL.items()}, "|q|": float(np.linalg.norm(qe))}
    if dVf < -1e-8 * abs(Vs_fast):
        rec["dV_mine"] = E.V(qe, c) - Vs_mine
    res.append(rec)
    Qs.append(qe)
    bn = rec["block_norms"]
    say(f"  {lab[:40]:40s} dV fast {dVf:+.6e} mine {rec.get('dV_mine', float('nan')):+.6e} {status} |Phi| {bn['Phi210']:.3f} "
        f"|H| {bn['H10']:.3f} |Sig| {bn['Sigma126bar']:.3f} |S| {bn['S']:.3f} |X| {bn['Phi17']:.3f} |A| {bn['A45']:.3f} "
        f"({time.time() - t1:.0f}s)")
    np.savez_compressed(E.BIGS / f"{args.out}_bank.npz", Q=np.array(Qs), dV=np.array([r_["dV_fast"] for r_ in res]))
    json.dump({"sol": args.sol, "V_star_fast": Vs_fast, "V_star_mine": Vs_mine, "results": res},
              open(E.BIGS / f"{args.out}.json", "w"), indent=1)
lower = [r_ for r_ in res if "dV_mine" in r_ and r_["dV_mine"] < -1e-8 * abs(Vs_mine)]
say(f"SUMMARY {args.out}: {len(res)} descents, {len(lower)} lower (mine), deepest "
    f"{min([r_['dV_mine'] for r_ in lower] + [0.0]):.6e}")
