"""K0b: 'slack' of a sub-theory = LP optimum of 4 mu_0 WITHOUT the pure-scalar cap (mu_0 <= 17/4 removed, box 12),
i.e. the Planck power the fermion-assisted closures alone would allow if the scalar operator did not exist.
A sub-theory with slack exactly 17 is marginal (any extra field can push it below); large slack is robust.
Usage: slack_single.py <type> <min> <max> <tag>   (types S16, P16, S10, N4, Nm4, N17, Nm17)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from k0b_engine import Model, jsonable
from scan_pairs import multiplet

HERE = Path(__file__).resolve().parent


def slack_bound(m, dim_max=20, mu_box=12.0, max_iter=400, cap=48.0):
    fields = m.field_table()
    nq = len(fields[0]["q"])
    cuts = []
    mu = None
    for it in range(max_iter):
        cvec = np.zeros(nq)
        cvec[0] = -4.0
        bounds = [(-mu_box, mu_box)] * nq
        bounds[0] = (-mu_box, cap / 4.0)
        if cuts:
            res = linprog(cvec, A_ub=np.array([c[0] for c in cuts], dtype=float), b_ub=np.array([c[1] for c in cuts], dtype=float),
                          bounds=bounds, method="highs")
        else:
            res = linprog(cvec, bounds=bounds, method="highs")
        if not res.success:
            return None, cuts
        mu = res.x
        bound = -res.fun
        o = m.oracle(mu, dim_max=dim_max, fields=fields)
        if o is None or o["value"] >= -1e-7:
            return bound, cuts
        q, dim2, _x, _z = m.charges_of(o["counts"], fields)
        cost = dim2 / 2.0 + o["parity"] - 4.0
        cuts.append((q, cost))
        cuts.append(([-c for c in q], cost))
    return None, cuts


def main():
    tag_type, lo, hi, tag = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    out = []
    t0 = time.time()
    for ch in range(lo, hi + 1):
        try:
            content = [("F", 16, 1, 3)] + multiplet(tag_type, ch, "1")
        except Exception:
            continue
        m = Model(content)
        if m.bare_masses() or m.phi210_yukawas():
            out.append({"type": tag_type, "charge": ch, "slack": None, "reason": "bare/210"})
            continue
        k = m.compute_kernel()
        if k["G2"] is None or k["scalar_rank"] < 2:
            out.append({"type": tag_type, "charge": ch, "slack": None, "reason": "PQ broken"})
            continue
        s, cuts = slack_bound(m)
        out.append({"type": tag_type, "charge": ch, "slack": s, "n_cuts": len(cuts) // 2,
                    "binding": [{"q": c[0], "cost": c[1]} for c in cuts[-6:]]})
        print("%s %4d slack %s (%d cuts, %.0fs)" % (tag_type, ch, None if s is None else round(s, 2), len(cuts) // 2, time.time() - t0), flush=True)
    (HERE / ("slack_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=0), encoding="utf-8")
    print("DONE", tag)


if __name__ == "__main__":
    main()
