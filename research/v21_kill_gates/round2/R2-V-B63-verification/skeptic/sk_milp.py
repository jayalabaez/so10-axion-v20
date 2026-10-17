"""Skeptic: independent MILP (HiGHS via scipy.optimize.milp) check of the K_min >= 17 dual certificate for B63.

For each dimension d (= 2d/2, fermions 3/2, scalars 1, derivative/field-strength dressing 1 each) solve
    max  4 mu.q(O)      s.t.  X(O) = 0,  sum z = 4k (k integer),  #undotted + nD = 2a,  #dotted + nD = 2b,
                               3 nF + 2 nS + 2 nD = 2d,  all counts integer >= 0
and compare with 4(d-4).  Modes: 'oracle' (nD in {0,1}: at most one derivative, only for odd/odd parity -- round-1
oracle set), 'dressed' (nD >= 0 free: any number of derivatives / field strengths).  Also both signs of mu.
Then: own LP column generation (maximise mu_0 subject to |mu.q| <= d-4 for all generated monomials, MILP oracle),
to get the LP-optimal certificate value 4 mu_0 independently of the round-1 mu.
Every MILP optimum is re-verified exactly in integer arithmetic.
"""
from __future__ import annotations
import json, sys, time
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds, linprog

HERE = Path(__file__).resolve().parent
FER = [("F", 16, 1), ("V1", 16, -35), ("Vb1", -16, 39), ("V2", 16, -28), ("Vb2", -16, 32), ("V3", 16, 34),
       ("Vb3", -16, -30), ("T", 10, 2), ("Pb", -16, 18), ("N1", 1, -63), ("N1b", 1, 59), ("N2", 1, -58),
       ("N2b", 1, 54), ("N3", 1, -57), ("N3b", 1, 61), ("NMm", 1, -2)]
SCA = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
       ("Phi17", 1, 17, False)]
Z = {16: 1, -16: 3, 10: 2, 1: 0, -126: 2, 210: 0}
Qb = {"V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0), "Vb2": (0, 0, -1, 0, 0, 0),
      "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "Pb": (0, -1, 0, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0),
      "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1),
      "N3b": (0, 0, 0, 0, 0, -1), "Phi17": (1, 0, 0, 0, 0, 0)}
MU4 = (17, -14, -28, -57, -48, -51)   # 4 * round-1 mu


def build_items():
    it = []
    for n, r, x in FER:
        q = Qb.get(n, (0,) * 6)
        it.append(dict(lab=n, X=x, z=Z[r] % 4, q=q, w=3, u=1, b=0))
        it.append(dict(lab=n + "*", X=-x, z=(-Z[r]) % 4, q=tuple(-c for c in q), w=3, u=0, b=1))
    for n, r, x, real in SCA:
        q = Qb.get(n, (0,) * 6)
        it.append(dict(lab=n, X=x, z=Z[r] % 4, q=q, w=2, u=0, b=0))
        if not real:
            it.append(dict(lab=n + "*", X=-x, z=(-Z[r]) % 4, q=tuple(-c for c in q), w=2, u=0, b=0))
    return it


ITEMS = build_items()
NI = len(ITEMS)


def solve(d, mu4, mode, sign=1, time_limit=120):
    """max sign*4mu.q at fixed dimension d. variables: n_i (NI), nD, k, a, b"""
    nv = NI + 4
    iD, ik, ia, ib = NI, NI + 1, NI + 2, NI + 3
    c = np.zeros(nv)
    for i, t in enumerate(ITEMS):
        c[i] = -sign * sum(m * q for m, q in zip(mu4, t["q"]))
    A = []; lo = []; hi = []
    # X = 0
    row = np.zeros(nv); row[:NI] = [t["X"] for t in ITEMS]; A.append(row); lo.append(0); hi.append(0)
    # centre: sum z_i n_i - 4k = 0
    row = np.zeros(nv); row[:NI] = [t["z"] for t in ITEMS]; row[ik] = -4; A.append(row); lo.append(0); hi.append(0)
    # undotted + nD - 2a = 0 ; dotted + nD - 2b = 0
    row = np.zeros(nv); row[:NI] = [t["u"] for t in ITEMS]; row[iD] = 1; row[ia] = -2; A.append(row); lo.append(0); hi.append(0)
    row = np.zeros(nv); row[:NI] = [t["b"] for t in ITEMS]; row[iD] = 1; row[ib] = -2; A.append(row); lo.append(0); hi.append(0)
    # dimension: 3 nF + 2 nS + 2 nD = 2d
    row = np.zeros(nv); row[:NI] = [t["w"] for t in ITEMS]; row[iD] = 2; A.append(row); lo.append(2 * d); hi.append(2 * d)
    lb = np.zeros(nv); ub = np.full(nv, float(2 * d))
    lb[ik] = 0; ub[ik] = 200
    if mode == "oracle":
        ub[iD] = 1
    cons = LinearConstraint(np.array(A), np.array(lo, float), np.array(hi, float))
    res = milp(c, constraints=cons, integrality=np.ones(nv), bounds=Bounds(lb, ub),
               options={"time_limit": time_limit, "mip_rel_gap": 0.0, "presolve": True})
    if res.status == 2 or res.x is None:   # infeasible
        return None
    x = np.rint(res.x).astype(int)
    # exact re-verification
    X = sum(x[i] * t["X"] for i, t in enumerate(ITEMS)); zz = sum(x[i] * t["z"] for i, t in enumerate(ITEMS))
    U = sum(x[i] * t["u"] for i, t in enumerate(ITEMS)) + x[iD]; Bv = sum(x[i] * t["b"] for i, t in enumerate(ITEMS)) + x[iD]
    W = sum(x[i] * t["w"] for i, t in enumerate(ITEMS)) + 2 * x[iD]
    ok = (X == 0 and zz % 4 == 0 and U % 2 == 0 and Bv % 2 == 0 and W == 2 * d)
    q = [int(sum(x[i] * t["q"][j] for i, t in enumerate(ITEMS))) for j in range(6)]
    val = sign * sum(m * qq for m, qq in zip(mu4, q))
    mono = {t["lab"]: int(x[i]) for i, t in enumerate(ITEMS) if x[i]}
    if x[iD]:
        mono["D"] = int(x[iD])
    return dict(val=int(val), excess4=int(val - 4 * (d - 4)), q=q, mono=mono, exact_ok=bool(ok), status=int(res.status),
                msg=res.message)


def certificate(mu4, mode, dmin, dmax):
    rows = []; worst = None
    for d in range(dmin, dmax + 1):
        for sign in (1, -1):
            r = solve(d, mu4, mode, sign)
            if r is None:
                rows.append(dict(d=d, sign=sign, infeasible=True)); continue
            r.update(d=d, sign=sign); rows.append(r)
            if d >= 5 and (worst is None or r["excess4"] > worst["excess4"]):
                worst = r
    return rows, worst


def lp_colgen(mode="dressed", dmax=20, iters=300):
    """max mu0 s.t. |mu.q(O)| <= d(O)-4 for generated O; oracle = MILP at each d (both signs)."""
    cuts = []
    mu = np.zeros(6)
    for it in range(iters):
        if cuts:
            A = np.array([c[0] for c in cuts] + [[-v for v in c[0]] for c in cuts], float)
            bb = np.array([c[1] for c in cuts] * 2, float)
        else:
            A = None; bb = None
        res = linprog(np.array([-1.0, 0, 0, 0, 0, 0]), A_ub=A, b_ub=bb, bounds=[(-60, 60)] * 6, method="highs")
        mu = res.x
        # oracle with float mu: maximise mu.q - (d-4) over d; use scaled-integer approx of mu via milp objective directly
        worst = None
        for d in range(5, dmax + 1):
            r = solve_float(d, mu, mode)
            if r is not None and (worst is None or r[0] > worst[0]):
                worst = r
        if worst is None or worst[0] <= 1e-6:
            return dict(mu=mu.tolist(), four_mu0=4 * mu[0], iterations=it, cuts=len(cuts))
        cuts.append((worst[1], worst[2]))
    return dict(mu=mu.tolist(), four_mu0=4 * mu[0], iterations=iters, cuts=len(cuts), converged=False)


def solve_float(d, mu, mode):
    best = None
    for sign in (1, -1):
        nv = NI + 4
        iD, ik, ia, ib = NI, NI + 1, NI + 2, NI + 3
        c = np.zeros(nv)
        for i, t in enumerate(ITEMS):
            c[i] = -sign * float(np.dot(mu, t["q"]))
        A = []; lo = []; hi = []
        row = np.zeros(nv); row[:NI] = [t["X"] for t in ITEMS]; A.append(row); lo.append(0); hi.append(0)
        row = np.zeros(nv); row[:NI] = [t["z"] for t in ITEMS]; row[ik] = -4; A.append(row); lo.append(0); hi.append(0)
        row = np.zeros(nv); row[:NI] = [t["u"] for t in ITEMS]; row[iD] = 1; row[ia] = -2; A.append(row); lo.append(0); hi.append(0)
        row = np.zeros(nv); row[:NI] = [t["b"] for t in ITEMS]; row[iD] = 1; row[ib] = -2; A.append(row); lo.append(0); hi.append(0)
        row = np.zeros(nv); row[:NI] = [t["w"] for t in ITEMS]; row[iD] = 2; A.append(row); lo.append(2 * d); hi.append(2 * d)
        lb = np.zeros(nv); ub = np.full(nv, float(2 * d)); ub[ik] = 200
        if mode == "oracle":
            ub[iD] = 1
        res = milp(c, constraints=LinearConstraint(np.array(A), np.array(lo, float), np.array(hi, float)),
                   integrality=np.ones(nv), bounds=Bounds(lb, ub), options={"time_limit": 60, "mip_rel_gap": 1e-9})
        if res.x is None:
            continue
        x = np.rint(res.x).astype(int)
        q = [int(sum(x[i] * t["q"][j] for i, t in enumerate(ITEMS))) for j in range(6)]
        v = sign * float(np.dot(mu, q)) - (d - 4)
        qq = tuple(sign * qi for qi in q)
        if best is None or v > best[0]:
            best = (v, qq, d - 4)
    return best


def main():
    out = {"mu4_round1": MU4, "items": [t["lab"] for t in ITEMS]}
    t0 = time.time()
    for mode, dmax in (("oracle", 24), ("dressed", 24)):
        rows, worst = certificate(MU4, mode, 1 if mode == "dressed" else 5, dmax)
        out[mode] = dict(rows=rows, worst_d_ge_5=worst,
                         holds=bool(worst["excess4"] <= 0), all_exact_ok=all(r.get("exact_ok", True) for r in rows))
        print(mode, "worst excess(x4) d>=5:", worst["excess4"], "at d", worst["d"], worst["mono"], "holds:",
              worst["excess4"] <= 0, "exact_ok all:", out[mode]["all_exact_ok"], "%.1fs" % (time.time() - t0), flush=True)
        for r in rows:
            if r.get("infeasible"):
                print("   d=%2d sign=%+d infeasible" % (r["d"], r["sign"]))
            else:
                print("   d=%2d sign=%+d 4mu.q=%4d excess4=%4d %s" % (r["d"], r["sign"], r["val"], r["excess4"], r["mono"]))
    # low-dimension (d<=4) monomials, undressed (oracle mode with nD forced to parity only): max |4 mu.q|
    out["lp_colgen_dressed"] = lp_colgen("dressed", 20)
    print("own LP column generation (dressed set, d<=20):", out["lp_colgen_dressed"], flush=True)
    (HERE / "sk_milp.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
