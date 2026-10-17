"""sk2: own exact check of the quality certificate K_min >= 17 for v21-F17-B63.

Method (different from R2-V's partial-sum-window DP and from skeptic-1's MILP):
  dimension-ordered unbounded-knapsack DP with an X range wide enough to hold EVERY partial sum
  (|X| <= 21 * W, W = 2 * dim), so no ordering lemma is needed.  State (W, X, z mod 4, undotted parity,
  dotted parity); value = max 4 mu.q.  Items: 16 fermion species and conjugates (W = 3), 9 scalar items (W = 2),
  optionally a derivative D (W = 2, flips both parities) and a field strength F (W = 4, neutral).
  Constraints imposed: X = 0, centre z = 0 mod 4, Lorentz parity.  (Necessary conditions only -> superset.)
Also: brute-force enumeration for d <= 7 by itertools (third independent code path), my own cutting-plane LP
from scratch (mu not taken from round 1) with exact rational re-check, and sensitivity runs.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FERM = [("F", "16", 1), ("V1", "16", -35), ("Vb1", "16b", 39), ("V2", "16", -28), ("Vb2", "16b", 32),
        ("V3", "16", 34), ("Vb3", "16b", -30), ("T", "10", 2), ("Pb", "16b", 18), ("N1", "1", -63), ("N1b", "1", 59),
        ("N2", "1", -58), ("N2b", "1", 54), ("N3", "1", -57), ("N3b", "1", 61), ("NMm", "1", -2)]
SCAL = [("Phi210", "210", 0, True), ("Delta", "126b", -2, False), ("H10", "10", -2, False), ("S", "1", 4, False),
        ("Phi17", "1", 17, False)]
ZC = {"16": 1, "16b": 3, "10": 2, "1": 0, "126b": 2, "210": 0}
# kernel basis verified in sk2_exact.py: (G2, f1, f2, f3, f4, f5)
QF = {"V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "Pb": (0, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0),
      "Vb2": (0, 0, -1, 0, 0, 0), "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0),
      "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1),
      "N3b": (0, 0, 0, 0, 0, -1), "Phi17": (1, 0, 0, 0, 0, 0)}
ZERO = (0,) * 6
MU_R1 = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))
NEG = -(10 ** 12)


def make_items(dressed=False, centre=True):
    its = []
    for n, r, x in FERM:
        q = QF.get(n, ZERO)
        its.append(dict(lab=n, X=x, z=ZC[r] if centre else 0, q=q, w=3, a=1, b=0))
        its.append(dict(lab=n + "~", X=-x, z=(-ZC[r]) % 4 if centre else 0, q=tuple(-c for c in q), w=3, a=0, b=1))
    for n, r, x, real in SCAL:
        q = QF.get(n, ZERO)
        its.append(dict(lab=n, X=x, z=ZC[r] if centre else 0, q=q, w=2, a=0, b=0))
        if not real:
            its.append(dict(lab=n + "~", X=-x, z=(-ZC[r]) % 4 if centre else 0, q=tuple(-c for c in q), w=2, a=0, b=0))
    if dressed:
        its.append(dict(lab="D", X=0, z=0, q=ZERO, w=2, a=1, b=1))
        its.append(dict(lab="Fmunu", X=0, z=0, q=ZERO, w=4, a=0, b=0))
    return its


def run_dp(its, vals, Wmax, dtype=np.int64, keep_parent=False):
    xmax = 21 * Wmax
    nx = 2 * xmax + 1
    neg = NEG if dtype == np.int64 else -1e18
    best = np.full((Wmax + 1, nx, 4, 2, 2), neg, dtype=dtype)
    best[0, xmax, 0, 0, 0] = 0
    par = np.full((Wmax + 1, nx, 4, 2, 2), -1, dtype=np.int16) if keep_parent else None
    for W in range(1, Wmax + 1):
        cur = best[W]
        for k, it in enumerate(its):
            if it["w"] > W:
                continue
            prev = best[W - it["w"]]
            x = it["X"]
            # new[X] = prev[X - x]
            src = np.full_like(prev, neg)
            if x > 0:
                src[x:] = prev[:-x]
            elif x < 0:
                src[:x] = prev[-x:]
            else:
                src[:] = prev
            src = np.roll(src, it["z"], axis=1)
            if it["a"]:
                src = src[:, :, ::-1, :]
            if it["b"]:
                src = src[:, :, :, ::-1]
            valid = src > neg / 2
            cand = np.where(valid, src + vals[k], neg)
            upd = cand > cur
            if upd.any():
                cur[upd] = cand[upd]
                if keep_parent:
                    par[W][upd] = k
    return best, par, xmax


def backtrack(par, its, W, xmax, a, b):
    out = {}
    X, z = 0, 0
    while W > 0:
        k = int(par[W, X + xmax, z, a, b])
        it = its[k]
        out[it["lab"]] = out.get(it["lab"], 0) + 1
        X -= it["X"]
        z = (z - it["z"]) % 4
        a ^= it["a"]
        b ^= it["b"]
        W -= it["w"]
    assert X == 0 and z == 0 and a == 0 and b == 0
    return out


def excess_table(mu, dmax, dressed, centre=True, keep_parent=True):
    its = make_items(dressed, centre)
    vals = [int(4 * sum(m * c for m, c in zip(mu, it["q"]))) for it in its]
    assert all(4 * sum(m * c for m, c in zip(mu, it["q"])) == v for it, v in zip(its, vals))
    t0 = time.time()
    best, par, xmax = run_dp(its, vals, 2 * dmax, keep_parent=keep_parent)
    rows = []
    for d in range(1, dmax + 1):
        cands = []
        v = best[2 * d, xmax, 0, 0, 0]
        if v > NEG / 2:
            cands.append((int(v), 2 * d, 0))
        if not dressed and 2 * d - 2 >= 0:
            v = best[2 * d - 2, xmax, 0, 1, 1]
            if v > NEG / 2:
                cands.append((int(v), 2 * d - 2, 1))
        if not cands:
            rows.append({"d": d, "max4muq": None})
            continue
        v, W, p = max(cands)
        mono = backtrack(par, its, W, xmax, p, p) if keep_parent else None
        rows.append({"d": d, "max4muq": v, "excess4": v - 4 * (d - 4), "deriv": p, "argmax": mono})
    return rows, time.time() - t0


def brute(mu, dmax=7):
    """third code path: explicit multisets via combinations_with_replacement, undressed oracle set."""
    its = make_items(False, True)
    res = {}
    # number of fields: fermions w=3, scalars w=2; total W <= 2*dmax
    for nf in range(0, 2 * dmax // 3 + 1):
        ferm = [it for it in its if it["w"] == 3]
        scal = [it for it in its if it["w"] == 2]
        for fc in itertools.combinations_with_replacement(range(len(ferm)), nf):
            Wf = 3 * nf
            Xf = sum(ferm[i]["X"] for i in fc)
            zf = sum(ferm[i]["z"] for i in fc)
            af = sum(ferm[i]["a"] for i in fc) % 2
            bf = sum(ferm[i]["b"] for i in fc) % 2
            vf = sum(4 * sum(m * c for m, c in zip(mu, ferm[i]["q"])) for i in fc)
            if af != bf:
                continue
            for ns in range(0, (2 * dmax - Wf) // 2 + 1):
                for sc in itertools.combinations_with_replacement(range(len(scal)), ns):
                    X = Xf + sum(scal[i]["X"] for i in sc)
                    if X != 0:
                        continue
                    if (zf + sum(scal[i]["z"] for i in sc)) % 4:
                        continue
                    W = Wf + 2 * ns
                    if W % 2:
                        continue
                    d = W // 2 + af
                    if d < 5 or d > dmax:
                        continue
                    v = vf + sum(4 * sum(m * c for m, c in zip(mu, scal[i]["q"])) for i in sc)
                    e = v - 4 * (d - 4)
                    if d not in res or e > res[d]:
                        res[d] = int(e)
    return res


def own_lp(dmax=20, iters=300):
    from scipy.optimize import linprog
    its = make_items(True, True)  # dressed set (superset)
    cuts = [((4, 0, 0, 0, 0, 0), 17), ((-4, 0, 0, 0, 0, 0), 17)]
    hist = []
    for it_ in range(iters):
        A = np.array([c[0] for c in cuts], float)
        b = np.array([c[1] for c in cuts], float)
        r = linprog([-1, 0, 0, 0, 0, 0], A_ub=A, b_ub=b, bounds=[(-60, 60)] * 6, method="highs")
        mu = r.x
        vals = [float(sum(m * c for m, c in zip(mu, itm["q"]))) for itm in its]
        best, par, xmax = run_dp(its, vals, 2 * dmax, dtype=np.float64, keep_parent=True)
        worst = None
        for d in range(5, dmax + 1):
            v = best[2 * d, xmax, 0, 0, 0]
            if v > -1e17:
                e = v - (d - 4)
                if worst is None or e > worst[0]:
                    worst = (e, d)
        hist.append((it_, float(4 * mu[0]), float(worst[0])))
        if worst[0] <= 1e-9:
            return {"4mu0": float(4 * mu[0]), "mu": [float(m) for m in mu], "iterations": it_, "ncuts": len(cuts)}, hist
        e, d = worst
        mono = backtrack(par, its, 2 * d, xmax, 0, 0)
        q = [0] * 6
        for lab, m in mono.items():
            base = lab.rstrip("~")
            s = -1 if lab.endswith("~") else 1
            for i in range(6):
                q[i] += m * s * QF.get(base, ZERO)[i]
        cuts.append((tuple(q), d - 4))
        cuts.append((tuple(-c for c in q), d - 4))
    return {"4mu0": None}, hist


def main():
    out = {}
    t0 = time.time()
    bf = brute(MU_R1, 7)
    out["bruteforce_d<=7"] = bf
    print("brute force (undressed) excess4 by d:", bf, flush=True)
    rows, dt = excess_table(MU_R1, 40, dressed=False)
    out["undressed_d<=40"] = rows
    out["undressed_seconds"] = dt
    mx20 = max(r["excess4"] for r in rows if r.get("excess4") is not None and 5 <= r["d"] <= 20)
    mx40 = max(r["excess4"] for r in rows if r.get("excess4") is not None and 5 <= r["d"] <= 40)
    out["undressed_max_excess4_5..20"] = mx20
    out["undressed_max_excess4_5..40"] = mx40
    print("undressed: max excess4 d 5..20 =", mx20, " d 5..40 =", mx40, " (%.1fs)" % dt, flush=True)
    for r in rows:
        if r.get("excess4") is not None and r["d"] <= 24:
            print("   d=%2d excess4=%4d deriv=%d %s" % (r["d"], r["excess4"], r["deriv"], r["argmax"]), flush=True)
    agree = all(bf.get(r["d"]) == r["excess4"] for r in rows if 5 <= r["d"] <= 7 and r.get("excess4") is not None)
    out["dp_equals_bruteforce_d5..7"] = agree
    print("DP == brute force for d 5..7:", agree, flush=True)
    rowsD, dtD = excess_table(MU_R1, 30, dressed=True)
    out["dressed_d<=30"] = rowsD
    low = [r for r in rowsD if r["d"] <= 4 and r.get("max4muq") is not None]
    out["dressed_d<=4_max4muq"] = {r["d"]: r["max4muq"] for r in low}
    mxD = max(r["excess4"] for r in rowsD if r.get("excess4") is not None and 5 <= r["d"] <= 30)
    out["dressed_max_excess4_5..30"] = mxD
    print("dressed: d<=4 max 4mu.q:", out["dressed_d<=4_max4muq"], "; max excess4 d 5..30 =", mxD, "(%.1fs)" % dtD, flush=True)
    # sensitivity: drop the centre condition
    rowsN, _ = excess_table(MU_R1, 12, dressed=False, centre=False)
    out["no_centre_d<=12"] = [r for r in rowsN if r["d"] >= 5]
    print("no centre: excess4 by d:", [(r["d"], r["excess4"], r["argmax"]) for r in rowsN if r["d"] >= 5 and r["d"] <= 8], flush=True)
    # own LP from scratch (dressed superset, d <= 20)
    lp, hist = own_lp(20)
    out["own_lp_from_scratch"] = lp
    out["own_lp_history_tail"] = hist[-5:]
    print("own LP from scratch:", lp, flush=True)
    if lp.get("4mu0") is not None:
        mu_rat = tuple(Fr(m).limit_denominator(8) for m in lp["mu"])
        rowsL, _ = excess_table(mu_rat, 24, dressed=True)
        mxL = max(r["excess4"] for r in rowsL if r.get("excess4") is not None and 5 <= r["d"] <= 24)
        out["own_lp_mu_rational"] = [str(m) for m in mu_rat]
        out["own_lp_mu_exact_recheck_max_excess4_5..24"] = mxL
        out["own_lp_mu_4mu0"] = str(4 * mu_rat[0])
        print("own LP mu rationalised", [str(m) for m in mu_rat], "exact recheck max excess4 (dressed, 5..24) =", mxL, flush=True)
    out["total_seconds"] = time.time() - t0
    (HERE / "sk2_cert.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
