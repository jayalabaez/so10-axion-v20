"""R2-V item (4): exact, independent check of the round-1 dual-LP quality certificate K_min >= 17 for v21-F17-B63.

Certificate logic (re-derived, see REPORT): for a closed PQ-violating vacuum diagram built from Planck operators O_i
(SO(10) x U(1)_X singlets, Lorentz scalars, d_i >= 5, coefficient M_Pl^-(d_i-4)) and renormalizable vertices
(which conserve every accidental charge q = (G2, f1..f5)), sum_i q(O_i) = q(vev legs) = (G2_vev, 0,...,0) with
G2_vev = 0 mod 4 (Spin(10) centre lemma) and != 0.  If |mu.q(O)| <= d(O) - 4 for every admissible O with
5 <= d <= 20, then K = sum (d_i - 4) >= |mu_0 G2_vev| >= 4 mu_0 for every diagram with K <= 16 -> contradiction
when 4 mu_0 = 17.  Operators may be used any number of times (linearity).

Here: exact integer dynamic programme (no LP/MILP solver) for
    max over monomials O [ 4 mu.q(O) - 4 (d(O) - 4) ]
over ALL monomials in the 16 fermion species, their conjugates and the 9 scalar fields, subject to the necessary
conditions X = 0, centre z = 0 mod 4, Lorentz parity (#psi, #psibar both even, or both odd with one derivative
costing +1), for every dimension d = 5..DMAX.  The certificate holds iff the maximum is <= 0 for d <= 20.

Ordering lemma used for the finite X window: any multiset with total X = 0 can be ordered so that every partial
sum lies in [-max|X_i|, +max|X_i|] (add a positive item when the partial sum is <= 0, else a negative one), so a DP
over partial sums restricted to |X| <= 63 is exact.
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
FERMIONS = [("F", 16, 1), ("V1", 16, -35), ("Vb1", -16, 39), ("V2", 16, -28), ("Vb2", -16, 32), ("V3", 16, 34),
            ("Vb3", -16, -30), ("T", 10, 2), ("Pb", -16, 18), ("N1", 1, -63), ("N1b", 1, 59), ("N2", 1, -58),
            ("N2b", 1, 54), ("N3", 1, -57), ("N3b", 1, 61), ("NMm", 1, -2)]
SCALARS = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
           ("Phi17", 1, 17, False)]
ZC = {16: 1, -16: 3, 10: 2, -10: 2, 126: 2, -126: 2, 1: 0, 210: 0}
# round-1 kernel basis (verified to span the kernel in b63_verify.py): q = (G2, f1, f2, f3, f4, f5)
Q = {"F": (0, 0, 0, 0, 0, 0), "V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0),
     "Vb2": (0, 0, -1, 0, 0, 0), "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "T": (0,) * 6,
     "Pb": (0, -1, 0, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0), "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0),
     "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1), "N3b": (0, 0, 0, 0, 0, -1), "NMm": (0,) * 6,
     "Phi210": (0,) * 6, "Delta": (0,) * 6, "H10": (0,) * 6, "S": (0,) * 6, "Phi17": (1, 0, 0, 0, 0, 0)}
MU = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))  # round-1 mu (exact quarter-integers)
NEG = -10 ** 9


def items(mu=MU, scale=4, use_centre=True):
    out = []
    for n, r, x in FERMIONS:
        for bar in (False, True):
            s = -1 if bar else 1
            q = tuple(s * c for c in Q[n])
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4 if use_centre else 0,
                        "v": v, "w": 3, "u": 0 if bar else 1, "b": 1 if bar else 0, "q": q})
    for n, r, x, real in SCALARS:
        for bar in ((False,) if real else (False, True)):
            s = -1 if bar else 1
            q = tuple(s * c for c in Q[n])
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4 if use_centre else 0,
                        "v": v, "w": 2, "u": 0, "b": 0, "q": q})
    return out


def dp(its, wmax, xmax=63, exact=True):
    """best[W, X+xmax, z, pu, pb] = max sum v over multisets with total weight W (=2*dim without derivative)."""
    nx = 2 * xmax + 1
    dtype = object if False else (np.int64 if exact else np.float64)
    best = np.full((wmax + 1, nx, 4, 2, 2), NEG, dtype=dtype)
    par = np.full((wmax + 1, nx, 4, 2, 2), -1, dtype=np.int16)
    best[0, xmax, 0, 0, 0] = 0
    vals = [int(it["v"]) if exact else float(it["v"]) for it in its]
    for W in range(1, wmax + 1):
        cur = best[W]
        for k, it in enumerate(its):
            w = it["w"]
            if w > W:
                continue
            prev = best[W - w]
            x = it["X"]
            # shift X: new[X] = prev[X - x]
            if x >= 0:
                src = prev[0:nx - x] if x > 0 else prev
                dst_sl = slice(x, nx)
            else:
                src = prev[-x:nx]
                dst_sl = slice(0, nx + x)
            # shift z and flip parities
            src = np.roll(src, it["z"], axis=1)
            if it["u"]:
                src = src[:, :, ::-1, :]
            if it["b"]:
                src = src[:, :, :, ::-1]
            cand = np.where(src > NEG // 2, src + vals[k], NEG)
            tgt = cur[dst_sl]
            better = cand > tgt
            if better.any():
                tgt[better] = cand[better]
                p = par[W][dst_sl]
                p[better] = k
    return best, par


def backtrack(best, par, its, W, xmax, pu, pb):
    counts = {}
    X, z = 0, 0
    w = W
    while w > 0:
        k = int(par[w, X + xmax, z, pu, pb])
        if k < 0:
            return None
        it = its[k]
        counts[it["label"]] = counts.get(it["label"], 0) + 1
        X -= it["X"]
        z = (z - it["z"]) % 4
        if it["u"]:
            pu ^= 1
        if it["b"]:
            pb ^= 1
        w -= it["w"]
    assert X == 0 and z == 0 and pu == 0 and pb == 0
    return counts


def certificate(dmax=40, use_centre=True, label="oracle"):
    its = items(use_centre=use_centre)
    xmax = max(abs(it["X"]) for it in its)
    t0 = time.time()
    best, par = dp(its, 2 * dmax, xmax)
    rows = []
    worst = None
    for d in range(5, dmax + 1):
        cands = []
        v0 = int(best[2 * d, xmax, 0, 0, 0])
        if v0 > NEG // 2:
            cands.append((v0 - 4 * (d - 4), 0, 2 * d))
        if 2 * d - 2 >= 0:
            v1 = int(best[2 * d - 2, xmax, 0, 1, 1])
            if v1 > NEG // 2:
                cands.append((v1 - 4 * (d - 4), 1, 2 * d - 2))
        if not cands:
            rows.append({"d": d, "max_4(mu.q-(d-4))": None})
            continue
        exc, parity, W = max(cands)
        mono = backtrack(best, par, its, W, xmax, parity, parity)
        rows.append({"d": d, "max_excess_x4": exc, "parity_derivative": parity, "argmax_monomial": mono})
        if d <= 20 and (worst is None or exc > worst[0]):
            worst = (exc, d, mono)
    return {"label": label, "use_centre": use_centre, "dmax": dmax, "seconds": time.time() - t0, "rows": rows,
            "max_excess_x4_over_5<=d<=20": worst[0], "at_d": worst[1], "monomial": worst[2],
            "certificate_holds_d<=20": worst[0] <= 0,
            "max_excess_x4_over_all_d<=%d" % dmax: max(r["max_excess_x4"] for r in rows if r.get("max_excess_x4") is not None)}


def brute_force_check(dmax=8):
    """direct enumeration of all monomials with d <= dmax (small) to validate the DP."""
    its = items()
    best = {}
    # enumerate multisets by weight using recursion on item index
    W = 2 * dmax
    res = {}

    def rec(k, w, X, z, pu, pb, v):
        if k == len(its):
            key = (w, pu)
            if X == 0 and z % 4 == 0 and pu == pb:
                d = w // 2 + (1 if pu else 0)
                if 5 <= d <= dmax and w % 2 == 0:
                    if d not in res or v - 4 * (d - 4) > res[d]:
                        res[d] = v - 4 * (d - 4)
            return
        it = its[k]
        m = 0
        while w + m * it["w"] <= W:
            rec(k + 1, w + m * it["w"], X + m * it["X"], z + m * it["z"], pu ^ (m * it["u"] & 1), pb ^ (m * it["b"] & 1),
                v + m * it["v"])
            m += 1
    rec(0, 0, 0, 0, 0, 0, 0)
    return res


def lp_optimum(dmax=20, iters=200):
    """own cutting-plane LP (scipy linprog) with the DP as separation oracle (float values; diagnostic only)."""
    from scipy.optimize import linprog
    cuts = [((4, 0, 0, 0, 0, 0), 17.0), ((-4, 0, 0, 0, 0, 0), 17.0)]
    for it_ in range(iters):
        A = np.array([c[0] for c in cuts], dtype=float)
        b = np.array([c[1] for c in cuts])
        res = linprog(np.array([-4.0, 0, 0, 0, 0, 0]), A_ub=A, b_ub=b, bounds=[(-40, 40)] * 6, method="highs")
        mu = res.x
        # exact-ish oracle: use float values scaled
        its = items(mu=tuple(mu), scale=1.0)
        xmax = max(abs(i["X"]) for i in its)
        best, par = dp(its, 2 * dmax, xmax, exact=False)
        worst = None
        for d in range(5, dmax + 1):
            for parity, W in ((0, 2 * d), (1, 2 * d - 2)):
                v = best[W, xmax, 0, parity, parity]
                if v > NEG / 2:
                    exc = v - (d - 4)
                    if worst is None or exc > worst[0]:
                        worst = (exc, d, parity, W)
        if worst[0] <= 1e-7:
            return {"mu_0_max": float(mu[0]), "4mu0": 4 * float(mu[0]), "mu": mu.tolist(), "iterations": it_, "cuts": len(cuts)}
        exc, d, parity, W = worst
        mono = backtrack(best, par, its, W, xmax, parity, parity)
        q = [0] * 6
        for lab, m in mono.items():
            base = lab.rstrip("^")
            s = -1 if lab.endswith("^") else 1
            for i in range(6):
                q[i] += m * s * Q[base][i]
        cuts.append((tuple(q), float(d - 4)))
        cuts.append((tuple(-c for c in q), float(d - 4)))
    return {"mu_0_max": None, "iterations": iters}


def main():
    out = {"mu_round1": [str(m) for m in MU]}
    # validate DP against brute force at small d
    bf = brute_force_check(7)
    its = items()
    xmax = max(abs(i["X"]) for i in its)
    best, par = dp(its, 16, xmax)
    dpv = {}
    for d in range(5, 8):
        c = []
        v0 = int(best[2 * d, xmax, 0, 0, 0])
        if v0 > NEG // 2:
            c.append(v0 - 4 * (d - 4))
        v1 = int(best[2 * d - 2, xmax, 0, 1, 1])
        if v1 > NEG // 2:
            c.append(v1 - 4 * (d - 4))
        dpv[d] = max(c) if c else None
    out["dp_vs_bruteforce_d<=7"] = {"dp": dpv, "brute": bf, "agree": all(dpv[d] == bf.get(d) for d in dpv)}
    print("DP vs brute force:", out["dp_vs_bruteforce_d<=7"], flush=True)
    out["certificate_oracle_set"] = certificate(40, True, "round-1 oracle set (X=0, centre, Lorentz)")
    c = out["certificate_oracle_set"]
    print("oracle set: max excess(x4) d<=20 =", c["max_excess_x4_over_5<=d<=20"], "at d", c["at_d"], c["monomial"],
          "| holds:", c["certificate_holds_d<=20"], "| max to d=40:", c["max_excess_x4_over_all_d<=40"], flush=True)
    for r in c["rows"]:
        print("   d=%2d  max 4(mu.q)-4(d-4) = %5s  deriv=%s  %s" % (r["d"], r.get("max_excess_x4"), r.get("parity_derivative"),
                                                             r.get("argmax_monomial")))
    out["certificate_no_centre"] = certificate(28, False, "superset without the centre condition")
    c2 = out["certificate_no_centre"]
    print("no-centre superset: max excess d<=20 =", c2["max_excess_x4_over_5<=d<=20"], "at d", c2["at_d"], c2["monomial"],
          "| holds:", c2["certificate_holds_d<=20"], flush=True)
    out["own_lp"] = lp_optimum(20)
    print("own LP optimum:", out["own_lp"], flush=True)
    (HERE / "dual_dp.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
