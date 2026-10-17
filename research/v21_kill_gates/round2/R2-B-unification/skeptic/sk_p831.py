#!/usr/bin/env python3
"""Skeptic check of the P831-spectrum transplant: uses ONLY the researcher's assigned m^2/|Phi|^2 values (data) from
r2b_p831.json, mapped onto the skeptic's own G3221 table; own solver.  Also: which heavy states drive the C2 result."""
import json, math, os, sys
import numpy as np
from fractions import Fraction as Fr
import sk_lib as L
import sk_unify as U

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "..", "r2b_p831.json")))
CONJ = {"3": "3b", "3b": "3", "6": "6b", "6b": "6", "1": "1", "8": "8"}

def key_of(parent, c3, l, r, q):
    # conjugation-invariant key: (parent, dim3, l, r, |q|) plus orientation-independent colour type
    return (parent, L.SU3R[c3][0], int(l), int(r), abs(Fr(q)))

def parse_their(name):
    parent, rest = name.split(":")
    rest = rest.split(" ")[0]
    reps, q = rest.split(")_")
    c3, l, r = reps.strip("(").split(",")
    return parent, c3, l, r, Fr(q)

def mapped_m2(tag):
    m2 = d[tag]["assigned_m2_over_Phi2"]
    pool = {}
    for n, v in m2.items():
        k = key_of(*parse_their(n))
        pool.setdefault(k, []).append(v)
    out = {}
    for n, (kind, c3, l, r, q) in L.TAB.items():
        parent = n.split(":")[0]
        k = key_of(parent, c3, l, r, q)
        if k in pool and pool[k]:
            out[n] = pool[k].pop(0)
    left = {k: v for k, v in pool.items() if v}
    return out, left

def solve_spec(content, m2, extra=None, loops=2, sv=+1):
    aU = 33.0
    r = m = None
    for it in range(6):
        g = math.sqrt(4 * math.pi / aU)
        mx = 0.6454972243679028 * g
        gr = {n: math.sqrt(v) / mx for n, v in m2.items()}
        if extra:
            gr.update(extra)
        m = U.Model(content, gut_r=gr, loops=loops, sv=sv)
        r = m.solve()
        if r is None:
            return None
        if abs(r["aU"] - aU) < 1e-6:
            break
        aU = r["aU"]
    r["tau_repo"] = U.tau_repo(r["M_U"], r["aU"])
    r["tau_lat"] = U.tau_lattice(r["M_U"], r["aU"])
    r["L2"] = m.landau(r["M_U"], r["aU"], 2)
    r["L3"] = m.landau(r["M_U"], r["aU"], 3)
    return r

res = {}
for tag in ("P831", "P831b"):
    m2, left = mapped_m2(tag)
    print(tag, "mapped", len(m2), "left", left)
    light0 = set(L.CONTENTS["C0"])
    # which multiplet is light at P831: researcher labels 126b:(1,2,2)_0 light, 10:(1,2,2)_0 heavy
    r = solve_spec("C0", {n: v for n, v in m2.items() if n not in light0})
    res[f"{tag}|C0"] = r
    print(tag, "C0", {k: f"{v:.4g}" for k, v in r.items()})
    for c in ("C2", "C1p", "C1"):
        lightc = set(L.CONTENTS[c])
        for f in ((0.3, 1.0, 2.0) if L.O831 not in lightc else (None,)):
            extra = {L.O831: f} if f else None
            mm = {n: v for n, v in m2.items() if n not in lightc}
            r = solve_spec(c, mm, extra)
            res[f"{tag}|{c}|f831={f}"] = r
            print(tag, c, f, {k: f"{v:.4g}" for k, v in r.items()}, flush=True)

# attribution for C2 (P831): restore each heavy multiplet to M_X one at a time, see tau change
m2, _ = mapped_m2("P831")
lightc = set(L.CONTENTS["C2"])
mm = {n: v for n, v in m2.items() if n not in lightc}
base = solve_spec("C2", mm, {L.O831: 1.0})
attr = {}
g = math.sqrt(4 * math.pi / base["aU"]); mx = 0.6454972243679028 * g
for n in mm:
    mm2 = dict(mm)
    mm2[n] = mx ** 2          # put this one at M_X
    r = solve_spec("C2", mm2, {L.O831: 1.0})
    attr[n] = (math.sqrt(mm[n]) / mx, r["tau_repo"] / base["tau_repo"], r["v_R"])
print("C2 attribution (ratio m/M_X, tau factor if moved to M_X, v_R):")
for n, v in sorted(attr.items(), key=lambda kv: -kv[1][1]):
    print(f"  {n:34s} r={v[0]:.3f}  tau x{v[1]:.3f}  vR={v[2]:.3g}")
res["attribution_C2_P831"] = attr
json.dump(res, open(os.path.join(HERE, "sk_p831.json"), "w"), indent=1, default=float)
