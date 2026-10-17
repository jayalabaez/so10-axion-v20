"""Skeptic: mu-independent PRIMAL search for the cheapest PQ-violating closure with J operator slots.

min sum_j (d_j - 4 u_j)  s.t. each used slot j is an admissible monomial (X=0, centre z=0 mod 4, Lorentz parity with
any number of derivative/field-strength dressings D_j, 5 <= d_j <= 20), unused slots empty, and
sum_j q(O_j) = (G2target, 0, 0, 0, 0, 0).  Multiplicities are realised by repeated slots.
A K <= 16 closure has at most 16 operators, so J = 16 would be exhaustive; smaller J is a heuristic upper bound.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sk_milp import ITEMS, NI

HERE = Path(__file__).resolve().parent


def primal(J, G2t=4, time_limit=300, kmax=None):
    per = NI + 5   # n_i, D, k, a, b, u
    nv = J * per
    c = np.zeros(nv)
    A = []; lo = []; hi = []
    def off(j):
        return j * per
    for j in range(J):
        o = off(j); iD, ik, ia, ib, iu = o + NI, o + NI + 1, o + NI + 2, o + NI + 3, o + NI + 4
        for i, t in enumerate(ITEMS):
            c[o + i] = t["w"] / 2.0
        c[iD] = 1.0; c[iu] = -4.0
        r = np.zeros(nv); r[o:o + NI] = [t["X"] for t in ITEMS]; A.append(r); lo.append(0); hi.append(0)
        r = np.zeros(nv); r[o:o + NI] = [t["z"] for t in ITEMS]; r[ik] = -4; A.append(r); lo.append(0); hi.append(0)
        r = np.zeros(nv); r[o:o + NI] = [t["u"] for t in ITEMS]; r[iD] = 1; r[ia] = -2; A.append(r); lo.append(0); hi.append(0)
        r = np.zeros(nv); r[o:o + NI] = [t["b"] for t in ITEMS]; r[iD] = 1; r[ib] = -2; A.append(r); lo.append(0); hi.append(0)
        # 10 u <= 2d <= 40 u
        r = np.zeros(nv); r[o:o + NI] = [t["w"] for t in ITEMS]; r[iD] = 2; r[iu] = -10; A.append(r); lo.append(0); hi.append(np.inf)
        r = np.zeros(nv); r[o:o + NI] = [t["w"] for t in ITEMS]; r[iD] = 2; r[iu] = -40; A.append(r); lo.append(-np.inf); hi.append(0)
        if j + 1 < J:   # symmetry breaking: 2d_j >= 2d_{j+1}
            o2 = off(j + 1)
            r = np.zeros(nv); r[o:o + NI] = [t["w"] for t in ITEMS]; r[iD] = 2
            r[o2:o2 + NI] = [-t["w"] for t in ITEMS]; r[o2 + NI] = -2
            A.append(r); lo.append(0); hi.append(np.inf)
    for m in range(6):
        r = np.zeros(nv)
        for j in range(J):
            r[off(j):off(j) + NI] = [t["q"][m] for t in ITEMS]
        A.append(r); tgt = G2t if m == 0 else 0; lo.append(tgt); hi.append(tgt)
    if kmax is not None:
        A.append(c.copy()); lo.append(-np.inf); hi.append(kmax)
    lb = np.zeros(nv); ub = np.full(nv, 40.0)
    for j in range(J):
        o = off(j); ub[o + NI + 1] = 100; ub[o + NI + 4] = 1
    res = milp(c, constraints=LinearConstraint(np.array(A), np.array(lo, float), np.array(hi, float)),
               integrality=np.ones(nv), bounds=Bounds(lb, ub),
               options={"time_limit": time_limit, "mip_rel_gap": 0.0, "disp": False})
    out = {"J": J, "G2target": G2t, "status": int(res.status), "message": res.message,
           "objective": None if res.x is None else float(res.fun),
           "dual_bound": getattr(res, "mip_dual_bound", None)}
    if res.x is not None:
        x = np.rint(res.x).astype(int)
        ops = []
        for j in range(J):
            o = off(j)
            if x[o + NI + 4]:
                mono = {t["lab"]: int(x[o + i]) for i, t in enumerate(ITEMS) if x[o + i]}
                if x[o + NI]:
                    mono["D"] = int(x[o + NI])
                d2 = sum(t["w"] * x[o + i] for i, t in enumerate(ITEMS)) + 2 * x[o + NI]
                ops.append({"d": d2 / 2, "mono": mono})
        out["ops"] = ops
        out["K"] = sum(op["d"] - 4 for op in ops)
    return out


def main():
    res = []
    for J, tl in ((1, 60), (2, 120), (3, 300), (4, 400), (5, 500), (7, 600)):
        t0 = time.time()
        r = primal(J, 4, tl)
        r["seconds"] = time.time() - t0
        res.append(r)
        print(json.dumps(r, default=str), flush=True)
        (HERE / "sk_primal.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
