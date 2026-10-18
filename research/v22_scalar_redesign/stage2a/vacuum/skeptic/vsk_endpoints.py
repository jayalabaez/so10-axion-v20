#!/usr/bin/env python3
"""Re-evaluate EVERY formal-round descent end point with my independent evaluator (vsk_eval) and compare with the
tester's reported dV.  For each round: V*(mine) at q* (pt_O11), the 85 rows J at every end point, dV(mine), the
gauge-invariant fingerprint (block norms, |J - J*|), and my own so(10) stabiliser dimension (tensor generator action,
not chart531's generators).  The deepest end point of each round is also re-evaluated after a random finite SO(10)
rotation + U(1)_X + PQ phase (my tensor rotation, re-packed) - it must keep its energy.
usage: python -B vsk_endpoints.py <content Lb|Lae>
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

import vsk_eval as E

content = sys.argv[1]
rounds = {
    "Lb": [("R1d_Lb_O11.npz", ["G1d_Lb_O11"]), ("R2d_Lb_O11.npz", ["G2d_Lb_O11_j0", "G2d_Lb_O11_j1"]),
           ("R3d_Lb_O11.npz", ["G3d_Lb_O11_j0", "G3d_Lb_O11_j1"])],
    "Lae": [("R1d_Lae_O11.npz", ["G1d_Lae_O11_j0", "G1d_Lae_O11_j1"]),
            ("R2d_Lae_O11.npz", ["G2d_Lae_O11_j0", "G2d_Lae_O11_j1"]),
            ("R3d_Lae_O11.npz", ["G3d_Lae_O11_j0", "G3d_Lae_O11_j1"])],
}[content]
log = open(E.BIGS / f"endpoints_{content}.log", "w", encoding="utf-8")


def say(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()


def so10_stabiliser(q, tol=1e-7):
    t = E.tensors(q)
    cols = []
    for a, b in E.PAIRS:
        L = np.zeros((10, 10))
        L[a, b], L[b, a] = 1.0, -1.0
        # infinitesimal rotation R = 1 + eps L  ->  delta tensors
        dP = sum(np.moveaxis(np.tensordot(L, t["P"], axes=([1], [ax])), 0, ax) for ax in range(4))
        dD = sum(np.moveaxis(np.tensordot(L, t["D"], axes=([1], [ax])), 0, ax) for ax in range(5))
        dA = L @ t["A"] - t["A"] @ L
        dH = L @ t["H"]
        cols.append(np.concatenate([dP.reshape(-1), dD.reshape(-1).real, dD.reshape(-1).imag, dA.reshape(-1),
                                    dH.real, dH.imag]))
    M = np.array(cols).T
    s = np.linalg.svd(M, compute_uv=False)
    rank = int(np.sum(s > tol * s[0])) if s[0] > 0 else 0
    return 45 - rank


P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
ids = [str(x) for x in P["ids"]]
rng = np.random.default_rng(11)
summary = {"content": content, "rounds": []}
for sol, jobs in rounds:
    c = E.load_c(sol)
    cv = np.array([c[p] for p in ids])
    Js = E.all_rows(qs)
    Jsv = np.array([Js[p] for p in ids])
    Vs = float(cv @ Jsv)
    recs = []
    Qall = []
    for jb in jobs:
        d = json.load(open(E.BIGV / f"{jb}.json"))
        z = np.load(E.BIGV / f"{jb}_bank.npz")
        assert abs(d["V_star"] - Vs) < 1e-9 * abs(Vs), (d["V_star"], Vs)
        for r, q in zip(d["results"], z["Q"]):
            J = E.all_rows(q)
            Jv = np.array([J[p] for p in ids])
            Vm = float(cv @ Jv)
            bn = {k: float(np.linalg.norm(q[sl])) for k, sl in
                  (("Phi", E.PHS), ("H", E.HS), ("Sig", E.SGS), ("S", E.SS), ("X", E.XS), ("A", E.AS))}
            recs.append({"job": jb, "label": r["label"], "dV_reported": r["V_end-V*"], "dV_mine": Vm - Vs,
                         "lower_reported": r["lower"], "runaway": r["runaway"], "max|J-J*|": float(np.max(np.abs(Jv - Jsv))),
                         "block_norms": bn, "stab_reported": r["so10_stabiliser_dim"]})
            Qall.append(q)
    Qall = np.array(Qall)
    dm = np.array([x["dV_mine"] for x in recs])
    dr = np.array([x["dV_reported"] for x in recs])
    lower_mine = dm < -1e-8 * max(1.0, abs(Vs))
    # stabiliser + rotation test on the 5 deepest
    order = np.argsort(dm)
    deep = []
    for i in order[:5]:
        q = Qall[i]
        t = E.tensors(q)
        R = E.random_rotation(rng)
        t2 = E.phase(E.phase(E.rotate(t, R), E.XCH, rng.uniform(0, 6.28)), E.pq_charges(), rng.uniform(0, 6.28))
        q2 = E.pack(t2)
        V2 = E.V(q2, c)
        stab = so10_stabiliser(q)
        deep.append({"i": int(i), "label": recs[i]["label"], "dV_mine": float(dm[i]), "dV_after_gauge_transform": V2 - Vs,
                     "|q2-q|": float(np.linalg.norm(q2 - q)), "so10_stabiliser_mine": stab,
                     "block_norms": recs[i]["block_norms"]})
        say(f"  deep {recs[i]['label'][:50]:50s} dV mine {dm[i]:+.10e} after gauge {V2 - Vs:+.10e} stab {stab}")
    stab_q = so10_stabiliser(qs)
    rs = {"sol": sol, "V_star_mine": Vs, "n": len(recs), "n_lower_mine": int(lower_mine.sum()),
          "n_lower_reported": int(sum(x["lower_reported"] for x in recs)),
          "agree_lower_flags": int(sum(bool(a) == bool(b["lower_reported"]) for a, b in zip(lower_mine, recs))),
          "deepest_mine": float(dm.min()), "deepest_reported": float(dr.min()),
          "max_abs_dV_diff": float(np.max(np.abs(dm - dr))), "min_max|J-J*|_over_lower": float(min(
              [x["max|J-J*|"] for x, l in zip(recs, lower_mine) if l] + [np.inf])),
          "qstar_so10_stabiliser_mine": stab_q, "deepest5": deep, "records": recs}
    summary["rounds"].append(rs)
    say(f"{sol}: V* {Vs:.12g}; {rs['n_lower_mine']}/{rs['n']} lower (reported {rs['n_lower_reported']}); deepest mine "
        f"{rs['deepest_mine']:.6e} reported {rs['deepest_reported']:.6e}; max |dV diff| {rs['max_abs_dV_diff']:.2e}; "
        f"flags agree {rs['agree_lower_flags']}/{rs['n']}; min |J-J*| over lower {rs['min_max|J-J*|_over_lower']:.3e}; "
        f"stab(q*) {stab_q}")
    np.savez_compressed(E.BIGS / f"endpoints_{content}_{sol[:2]}.npz", Q=Qall, dV=dm)
    json.dump(summary, open(E.BIGS / f"endpoints_{content}.json", "w"), indent=1, default=float)
say("done")
