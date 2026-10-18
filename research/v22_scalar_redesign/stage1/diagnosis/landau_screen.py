"""Cheap screen: SO(10)-phase Landau scale (1/2/3 loops, exact MV + PGJ coefficients from a copy of R2-B's r2b_lib.py)
for the B63 + v20 scalar content and for candidate scalar additions.  Pure gauge running from M_U (Yukawa and U(1)_X
omitted, which makes the estimate slightly pessimistic, EST +-10-20% on Lambda); the 16+16bar Phi17 pair enters at
M_Phi = 1e17 as in R2-B.  Validation: reproduce R2-B's C0 / C2 Lambda_2L to the stated tolerance.  NUM/EST."""
import math, json
from fractions import Fraction as F
import numpy as np
from r2b_lib import SO10, C_G_SO10, pgj_b, pgj_invariants, Segment, run_segment, M_PL_RED

BASE = [("16", "weyl", 3), ("16", "weyl", 3), ("16b", "weyl", 3), ("10", "weyl", 2),
        ("210", "real", 1), ("126b", "cplx", 1), ("10", "cplx", 1)]
PHI = [("16", "weyl", 1), ("16b", "weyl", 1)]
VARIANTS = {
    "B63+v20 scalars": [],
    "+45_H (real)": [("45", "real", 1)],
    "+54_H (real)": [("54", "real", 1)],
    "+45_H+54_H": [("45", "real", 1), ("54", "real", 1)],
    "+second 10_H (cplx)": [("10", "cplx", 1)],
    "+16_H (cplx)": [("16", "cplx", 1)],
    "+120_H (cplx)": [("120", "cplx", 1)],
    "+120_H (real)": [("120", "real", 1)],
    "+second 126bar (cplx)": [("126b", "cplx", 1)],
    "-210 +45_H+54_H": "SWAP",
}

def coeffs(content):
    return pgj_b(pgj_invariants(content, SO10, C_G_SO10))

def landau(content, MU, aU, loops, MPHI=1e17):
    lo = coeffs(content); hi = coeffs(content + PHI)
    def seg(b):
        return Segment([b[0]], [[b[1]]], b3=[b[2]], loops=loops)
    y, t, hit = run_segment(seg(lo), np.array([aU]), math.log(MU), math.log(max(MPHI, MU)), landau_event=True)
    if not hit:
        y, t, hit = run_segment(seg(hi), y, math.log(max(MPHI, MU)), math.log(1e24), landau_event=True)
    return (math.exp(t) / M_PL_RED) if hit else float("inf")

out = {}
points = {"C0-like (3.0e15, 33.3)": (3.02e15, 33.26), "C2-like (6.05e15, 34.6)": (6.05e15, 34.64), "1.4e16, 35.5": (1.4e16, 35.5)}
for name, extra in VARIANTS.items():
    if extra == "SWAP":
        content = [c for c in BASE if c[0] != "210"] + [("45", "real", 1), ("54", "real", 1)]
    else:
        content = BASE + extra
    b = coeffs(content)
    row = {"b1": str(b[0]), "b2": str(b[1]), "b3": str(b[2])}
    for pn, (MU, aU) in points.items():
        row[pn] = {f"L{l}": round(landau(content, MU, aU, l), 3) for l in (1, 2, 3)}
    out[name] = row
    print(f"{name:24s} b=({float(b[0]):6.2f},{float(b[1]):8.1f},{float(b[2]):9.0f})  " +
          "  ".join(f"{pn}: L2={row[pn]['L2']:.2f} L3={row[pn]['L3']:.2f}" for pn in points))
json.dump(out, open("landau_screen.json", "w"), indent=1)
