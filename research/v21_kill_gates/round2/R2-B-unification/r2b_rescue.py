#!/usr/bin/env python3
"""Minimal-addition rescue search: add one or two G3221 multiplets of 210 + 126bar + 10 (from the heavy remainder)
to the light content of C1, C2, C1p (and C0 for reference), two loops, nominal B63 point (M_s = 1e13, y_s = 0.336,
Phi pair at 1e17, MS-bar S_V constant, Am45 (3,1,1) ratio, c = 0).
Targets: (A) tau_p > 2.4e34 yr and Lambda_2L > M_Pl,red;  (B) = (A) and v_R in [1e11, 1e14] (type-I seesaw window);
(C) = (B) and tau_p > 7.8e34 (beyond the Hyper-K 90% CL sensitivity).  Every hit needs R2-A realisability."""
import itertools
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

SK, HK = 2.4e34, 7.8e34
BASES = sys.argv[1:] or ["C1", "C2", "C1p", "C0"]
logf = open(os.path.join(HERE, f"r2b_rescue_{'_'.join(BASES)}.log"), "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n")
    logf.flush()


def run(light):
    p = M.Params(light=light, loops=2)
    ch = M.Chain(p)
    r = ch.solve()
    if r.get("ok"):
        M.set_yt(ch, r["v_R"])
        r2 = ch.solve(guesses=[(math.log(r["v_R"]), math.log(r["M_U"]), r["a2R_inv_vR"])])
        if r2.get("ok"):
            r = r2
    row = {"ok": bool(r.get("ok")), "b": ch.b_g}
    if not r.get("ok"):
        return row
    row.update({k: r[k] for k in ("v_R", "M_U", "alpha_U_inv")})
    row["tau_p"] = M.proton_lifetime_years(r["M_U"], r["alpha_U_inv"])
    if r["M_U"] < 1e19 and r["v_R"] < r["M_U"]:
        row["L2"] = ch.landau(r["M_U"], r["alpha_U_inv"], loops=2)["Lambda_over_MPl"]
    else:
        row["L2"] = None
    L2 = row["L2"] or 0.0
    row["A"] = row["tau_p"] > SK and L2 > 1
    row["B"] = row["A"] and 1e11 <= r["v_R"] <= 1e14 and r["M_U"] < 1e18
    row["C"] = row["B"] and row["tau_p"] > HK
    return row


out = {"criteria": __doc__}
t0 = time.time()
for base in BASES:
    light0 = M.CONTENTS[base]
    cands = [n for n in M.SCALAR_TABLE if n not in light0]
    res = {"base": run(light0)}
    log(base, "base", res["base"])
    singles = {}
    for c in cands:
        singles[c] = run(light0 + (c,))
        r = singles[c]
        log(base, "+", c, {k: (f"{v:.3g}" if isinstance(v, float) else v) for k, v in r.items() if k != "b"})
    res["singles"] = singles
    pairs = {}
    for c1, c2 in itertools.combinations(cands, 2):
        r = run(light0 + (c1, c2))
        pairs[c1 + " + " + c2] = r
        if r.get("B"):
            log(base, "++", c1, "+", c2, {k: (f"{v:.3g}" if isinstance(v, float) else v) for k, v in r.items() if k != "b"})
    res["pairs"] = pairs
    for crit in ("A", "B", "C"):
        res[f"singles_{crit}"] = [c for c, r in singles.items() if r.get(crit)]
        res[f"pairs_{crit}"] = [c for c, r in pairs.items() if r.get(crit)]
    log(base, "summary singles A/B/C:", len(res["singles_A"]), len(res["singles_B"]), len(res["singles_C"]),
        "pairs A/B/C:", len(res["pairs_A"]), len(res["pairs_B"]), len(res["pairs_C"]), "of", len(pairs))
    out[base] = res
out["seconds"] = time.time() - t0
with open(os.path.join(HERE, f"r2b_rescue_{'_'.join(BASES)}.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
log("done", out["seconds"])
