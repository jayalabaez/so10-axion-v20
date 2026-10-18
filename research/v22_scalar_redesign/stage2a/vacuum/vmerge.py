#!/usr/bin/env python3
"""Merge the job outputs of one global search (vdesc.py runs) into <out>.json / <out>_bank.npz (lower endpoints and
runaway directions, ready to be fed back to vlp.py --banks / as BFB rays) and print a summary.
usage: python -B vmerge.py <out> <job1> [<job2> ...]
"""
from __future__ import annotations

import json
import sys

import numpy as np

import vc

out = sys.argv[1]
jobs = sys.argv[2:]
results, Q, J, RD = [], [], [], []
Vstar = None
for jb in jobs:
    d = json.load(open(vc.BIG / f"{jb}.json"))
    Vstar = d["V_star"]
    z = np.load(vc.BIG / f"{jb}_bank.npz")
    for r, q, j in zip(d["results"], z["Q"], z["J"]):
        results.append(r)
        if r["lower"] or r["runaway"]:
            Q.append(q)
            J.append(j)
    if "run_dirs" in z.files and z["run_dirs"].size:
        RD.append(z["run_dirs"])
n = len(results)
lower = [r for r in results if r["lower"]]
run = [r for r in results if r["runaway"]]
finite_lower = [r for r in lower if not r["runaway"]]
by_kind = {}
for r in results:
    k = r["label"].split(":")[0] + (":" + r["label"].split(":")[1] if r["label"].startswith("deep") else "")
    e = by_kind.setdefault(k, {"n": 0, "lower": 0, "runaway": 0, "deepest": 0.0})
    e["n"] += 1
    e["lower"] += int(r["lower"])
    e["runaway"] += int(r["runaway"])
    e["deepest"] = min(e["deepest"], r["V_end-V*"])
summary = {"out": out, "jobs": jobs, "V_star": Vstar, "n_descents": n, "n_lower": len(lower), "n_runaway": len(run),
           "n_finite_lower": len(finite_lower),
           "deepest_finite": min([r["V_end-V*"] for r in finite_lower] + [0.0]),
           "n_copies_of_vacuum": sum(r["gauge_copy_of_vacuum"] for r in results),
           "by_start_kind": by_kind,
           "lowest10": sorted([(r["V_end-V*"], r["label"], r["runaway"], r["so10_stabiliser_dim"], r["su2L_breaking_norm"],
                                r["block_norms"]) for r in results], key=lambda t: t[0])[:10]}
json.dump(vc.jsonable(summary), open(vc.BIG / f"{out}.json", "w"), indent=1)
np.savez_compressed(vc.BIG / f"{out}_bank.npz", Q=np.array(Q) if Q else np.zeros((0, vc.N)),
                    J=np.array(J) if J else np.zeros((0, vc.NPAR)), ids=np.array(vc.IDS),
                    run_dirs=np.vstack(RD) if RD else np.zeros((0, vc.N)))
print(json.dumps({k: v for k, v in vc.jsonable(summary).items() if k != "lowest10"}, indent=1))
for t in summary["lowest10"][:6]:
    print("  ", t[0], t[1][:60], "runaway" if t[2] else "", "stab", t[3], "SU2L", round(t[4], 4))
