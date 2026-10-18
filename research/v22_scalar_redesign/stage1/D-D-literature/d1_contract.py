#!/usr/bin/env python3
"""D-D-literature, criterion D1 (contract) for the designs L1 (v20 scalars, one-step SM breaking), L2 (L1 + real 45_H,
X = 0) and L3 (L2 + real 54_H, X = 0).  The B63 fermion sector is unchanged in every design.

What is computed (all exact integer / Fraction arithmetic unless stated):
  (a) anomalies [SO(10)]^2 X, X^3, grav-X of the B63 fermions (scalars do not contribute);
  (b) the accidental-symmetry kernel: charges of the 16 fermion species + the complex scalars, constrained by the 12
      renormalisable Yukawas and by EVERY phase-sensitive renormalisable scalar monomial of the design (enumerated:
      all X-neutral, centre-neutral monomials of degree 3 and 4 in the scalars; for each design the SO(10)-singlet
      existence of the relevant tensor products is listed by hand in SINGLET_OK, see REPORT); rank, kernel dimension,
      PQ = X - 17 G2, N, E/N (E/N from the round-1 E = 272/3, N = 34 since the fermions are unchanged);
  (c) the quality certificate K_min >= 17 re-run for the design's scalar list by
      (c1) the R2-V integer dynamic programme (dual_dp_orig.py functions, exact, all monomials, X = 0, centre,
           Lorentz parity, d <= 40), with the round-1 mu;
      (c2) an own cutting-plane LP with the DP as oracle (re-derives the LP optimum 4 mu_0 = K_min bound);
      (c3) an independent HiGHS MILP (sk_milp.py logic, 'dressed' set = any number of derivatives/field strengths)
           at every 5 <= d <= 24 with the round-1 mu, plus MILP column generation for the LP optimum.
Outputs: d1_contract.json, d1_contract.log (stdout).
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import milp, LinearConstraint, Bounds, linprog

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dual_dp_orig as DP  # noqa: E402  (functions only; its main() is never called)

FERMIONS = DP.FERMIONS          # B63, unchanged
DIM = {16: 16, -16: 16, 10: 10, 1: 1}
TIDX = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}   # T(10) = 1 normalisation
MULT = {"F": 3, "V1": 2, "T": 2, "NMm": 2}            # generation multiplicities (Weyl)
ZC = {16: 1, -16: 3, 10: 2, -10: 2, 126: 2, -126: 2, 1: 0, 210: 0, 45: 0, 54: 0}

V20_SCALARS = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
               ("Phi17", 1, 17, False)]
DESIGNS = {
    "L1_v20_onestep": V20_SCALARS,
    "L2_plus45": V20_SCALARS + [("A45", 45, 0, True)],
    "L3_plus45_54": V20_SCALARS + [("A45", 45, 0, True), ("E54", 54, 0, True)],
    "L3p_45_54_no210": [s for s in V20_SCALARS if s[0] != "Phi210"] + [("A45", 45, 0, True), ("E54", 54, 0, True)],
}
if len(sys.argv) > 1:
    DESIGNS = {k: v for k, v in DESIGNS.items() if k in sys.argv[1:]}


# ------------------------------------------------------------------------------------------------------------------
# (a) anomalies
# ------------------------------------------------------------------------------------------------------------------
def anomalies():
    a2x = Fr(0); x3 = Fr(0); gx = Fr(0)
    rows = []
    for n, r, x in FERMIONS:
        m = MULT.get(n, 1)
        a2x += m * TIDX[r] * x
        x3 += m * DIM[r] * Fr(x) ** 3
        gx += m * DIM[r] * x
        rows.append((n, r, x, m))
    return {"SO10^2_X": str(a2x), "X^3": str(x3), "grav_X": str(gx), "anomaly_free": a2x == 0 and x3 == 0 and gx == 0,
            "species": rows}


# ------------------------------------------------------------------------------------------------------------------
# (b) kernel of the accidental symmetries
# ------------------------------------------------------------------------------------------------------------------
YUKAWAS = [("F", "F", "H10"), ("F", "F", "Delta"), ("V1", "Vb1", "S*"), ("V1", "Pb", "Phi17"), ("V2", "Vb2", "S*"),
           ("Vb2", "Vb3", "H10"), ("V3", "Vb3", "S*"), ("T", "T", "S*"), ("N1", "N1b", "S"), ("N2", "N2b", "S"),
           ("N3", "N3b", "S*"), ("NMm", "NMm", "S")]
COMPLEX_SCALARS = {"Delta": (-2, 2), "H10": (-2, 2), "S": (4, 0), "Phi17": (17, 0)}   # X, centre class of the field


def scalar_monomials(real_fields):
    """All X-neutral, centre-neutral monomials of degree <= 4 in the complex scalars and their conjugates, times any
    number (<= 4 - degree) of real X = 0 fields.  Returns those that are NOT self-conjugate (phase-sensitive)."""
    labels = []
    for n, (x, z) in COMPLEX_SCALARS.items():
        labels.append((n, x, z, +1))
        labels.append((n + "*", -x, (-z) % 4, -1))
    out = []
    for deg in (2, 3, 4):
        for combo in itertools.combinations_with_replacement(range(len(labels)), deg):
            X = sum(labels[i][1] for i in combo)
            Z = sum(labels[i][2] for i in combo) % 4
            if X != 0 or Z != 0:
                continue
            charge = {}
            for i in combo:
                base = labels[i][0].rstrip("*")
                charge[base] = charge.get(base, 0) + labels[i][3]
            if all(v == 0 for v in charge.values()):
                continue           # self-conjugate combination (|.|^2 type): phase-insensitive
            names = [labels[i][0] for i in combo]
            # number of free slots for real X=0 fields (Phi210, A45, E54) up to total degree 4
            out.append({"fields": names, "net": charge, "free_real_slots": 4 - deg})
    return out


def kernel(design):
    species = [f[0] for f in FERMIONS] + list(COMPLEX_SCALARS)
    idx = {n: i for i, n in enumerate(species)}
    rows = []
    for tri in YUKAWAS:
        r = [0] * len(species)
        for f in tri:
            s = -1 if f.endswith("*") else 1
            r[idx[f.rstrip("*")]] += s
        rows.append(r)
    # phase-sensitive scalar terms that exist (SO(10)-singlet) in the v20 contract (R2-V section 7): kappaH H10.H10.S,
    # O15 Phi210.H10*.Delta, O28 H10*.Delta^2.Delta*, O31 H10*^2.Delta^2, O38 Phi210.H10*.Delta*.S*, O45 Phi210^2.H10*.Delta
    terms = [{"H10": 2, "S": 1}, {"H10": -1, "Delta": 1}, {"H10": -1, "Delta": 1}, {"H10": -2, "Delta": 2},
             {"H10": -1, "Delta": -1, "S": -1}, {"H10": -1, "Delta": 1}]
    # every further X/centre-neutral phase-sensitive monomial (whether or not an SO(10) singlet exists) -- adding them
    # can only RAISE the rank; we show it does not
    extra = scalar_monomials(design)
    r_base = []
    for t in terms:
        r = [0] * len(species)
        for k, v in t.items():
            r[idx[k]] += v
        r_base.append(r)
    M0 = sp.Matrix(rows + r_base)
    r_extra = []
    for e in extra:
        r = [0] * len(species)
        for k, v in e["net"].items():
            r[idx[k]] += v
        r_extra.append(r)
    M1 = sp.Matrix(rows + r_base + r_extra)
    X = [x for _, _, x in FERMIONS] + [COMPLEX_SCALARS[n][0] for n in COMPLEX_SCALARS]
    G2 = [0] * len(species); G2[idx["V1"]] = -1; G2[idx["Vb1"]] = 1; G2[idx["Phi17"]] = 1
    inker = lambda v: all(sum(a * b for a, b in zip(row, v)) == 0 for row in (rows + r_base + r_extra))
    return {"n_species": len(species), "rank_contract_terms": int(M0.rank()), "kernel_dim_contract": len(species) - int(M0.rank()),
            "rank_all_phase_sensitive_monomials_deg<=4": int(M1.rank()),
            "kernel_dim_all": len(species) - int(M1.rank()), "n_extra_monomials": len(extra),
            "X_in_kernel": inker(X), "G2_in_kernel": inker(G2),
            "extra_examples": [e["fields"] for e in extra[:12]]}


def pq_anomaly():
    """N and E for PQ = X - 17 G2 (fermions unchanged: recompute N exactly)."""
    # N = sum over Weyl fermions of PQ charge x T(SU(3) part) -> in SO(10) language: N = sum_f q_PQ(f) T_SO10(f) / 2?
    # Use the SO(10) relation N = (1/2) sum q T(R) with T(16) = 2 (one 16 has N-contribution 1 per unit charge... ) --
    # here we follow R2-V: N(X) = 0 (anomaly-free), N(G2) = -2 per unit -> N(PQ) = -17 * (-2) = 34.
    # QCD anomaly coefficient N = sum_Weyl q T_SU3(R); T_SU3 = T_SO10 for 16 (=2) and 10 (=1) in T(10) = 1 units.
    nG2 = Fr(0)
    for n, r, x in FERMIONS:
        m = MULT.get(n, 1)                 # both V1 copies carry G2 = -1 as a charge assignment (R2-V section 3)
        g2 = {"V1": -1, "Vb1": 1}.get(n, 0)
        nG2 += m * g2 * TIDX[r]
    nX = Fr(0)
    for n, r, x in FERMIONS:
        nX += MULT.get(n, 1) * x * TIDX[r]
    return {"N(X)": str(nX), "N(G2)_per_unit(R2-V def)": str(nG2), "N(PQ = X - 17 G2)": str(nX - 17 * nG2),
            "E/N (fermions unchanged; R2-V exact)": "8/3"}


# ------------------------------------------------------------------------------------------------------------------
# (c) quality certificate for a scalar list
# ------------------------------------------------------------------------------------------------------------------
def dp_items(scalars, mu=DP.MU, scale=4):
    out = []
    for n, r, x in FERMIONS:
        for bar in (False, True):
            s = -1 if bar else 1
            q = tuple(s * c for c in DP.Q[n])
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4, "v": v, "w": 3,
                        "u": 0 if bar else 1, "b": 1 if bar else 0, "q": q})
    for n, r, x, real in scalars:
        qn = DP.Q.get(n, (0,) * 6)
        for bar in ((False,) if real else (False, True)):
            s = -1 if bar else 1
            q = tuple(s * c for c in qn)
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4, "v": v, "w": 2,
                        "u": 0, "b": 0, "q": q})
    return out


def dp_certificate(scalars, dmax=40):
    its = dp_items(scalars)
    xmax = max(abs(it["X"]) for it in its)
    best, par = DP.dp(its, 2 * dmax, xmax)
    worst = None; rows = []
    for d in range(5, dmax + 1):
        cands = []
        v0 = int(best[2 * d, xmax, 0, 0, 0])
        if v0 > DP.NEG // 2:
            cands.append((v0 - 4 * (d - 4), 0, 2 * d))
        v1 = int(best[2 * d - 2, xmax, 0, 1, 1])
        if v1 > DP.NEG // 2:
            cands.append((v1 - 4 * (d - 4), 1, 2 * d - 2))
        if not cands:
            continue
        exc, parity, W = max(cands)
        mono = DP.backtrack(best, par, its, W, xmax, parity, parity)
        rows.append({"d": d, "max_excess_x4": exc, "mono": mono})
        if d <= 20 and (worst is None or exc > worst[0]):
            worst = (exc, d, mono)
    return {"max_excess_x4_5<=d<=20": worst[0], "at_d": worst[1], "monomial": worst[2],
            "holds_d<=20": worst[0] <= 0, "max_excess_x4_d<=%d" % dmax: max(r["max_excess_x4"] for r in rows),
            "tight_d": [r["d"] for r in rows if r["max_excess_x4"] == 0]}


def dp_lp_optimum(scalars, dmax=20, iters=300):
    cuts = [((4, 0, 0, 0, 0, 0), 17.0), ((-4, 0, 0, 0, 0, 0), 17.0)]
    for it_ in range(iters):
        A = np.array([c[0] for c in cuts], float); b = np.array([c[1] for c in cuts])
        res = linprog(np.array([-4.0, 0, 0, 0, 0, 0]), A_ub=A, b_ub=b, bounds=[(-40, 40)] * 6, method="highs")
        mu = res.x
        its = dp_items(scalars, mu=tuple(mu), scale=1.0)
        xmax = max(abs(i["X"]) for i in its)
        best, par = DP.dp(its, 2 * dmax, xmax, exact=False)
        worst = None
        for d in range(5, dmax + 1):
            for parity, W in ((0, 2 * d), (1, 2 * d - 2)):
                v = best[W, xmax, 0, parity, parity]
                if v > DP.NEG / 2:
                    exc = v - (d - 4)
                    if worst is None or exc > worst[0]:
                        worst = (exc, d, parity, W)
        if worst[0] <= 1e-7:
            return {"4mu0_LP_optimum": 4 * float(mu[0]), "mu": [float(m) for m in mu], "iterations": it_, "cuts": len(cuts)}
        exc, d, parity, W = worst
        mono = DP.backtrack(best, par, its, W, xmax, parity, parity)
        q = [0] * 6
        for lab, m in mono.items():
            base = lab.rstrip("^"); s = -1 if lab.endswith("^") else 1
            for i in range(6):
                q[i] += m * s * DP.Q.get(base, (0,) * 6)[i]
        cuts.append((tuple(q), float(d - 4))); cuts.append((tuple(-c for c in q), float(d - 4)))
    return {"4mu0_LP_optimum": None}


def milp_items(scalars):
    it = []
    for n, r, x in FERMIONS:
        q = DP.Q[n]
        it.append(dict(lab=n, X=x, z=ZC[r] % 4, q=q, w=3, u=1, b=0))
        it.append(dict(lab=n + "*", X=-x, z=(-ZC[r]) % 4, q=tuple(-c for c in q), w=3, u=0, b=1))
    for n, r, x, real in scalars:
        q = DP.Q.get(n, (0,) * 6)
        it.append(dict(lab=n, X=x, z=ZC[r] % 4, q=q, w=2, u=0, b=0))
        if not real:
            it.append(dict(lab=n + "*", X=-x, z=(-ZC[r]) % 4, q=tuple(-c for c in q), w=2, u=0, b=0))
    return it


def milp_solve(ITEMS, d, mu, sign, dressed=True):
    NI = len(ITEMS); nv = NI + 4
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
    if not dressed:
        ub[iD] = 1
    res = milp(c, constraints=LinearConstraint(np.array(A), np.array(lo, float), np.array(hi, float)),
               integrality=np.ones(nv), bounds=Bounds(lb, ub), options={"time_limit": 120, "mip_rel_gap": 0.0})
    if res.x is None:
        return None
    x = np.rint(res.x).astype(int)
    q = [int(sum(x[i] * t["q"][j] for i, t in enumerate(ITEMS))) for j in range(6)]
    Xs = sum(x[i] * t["X"] for i, t in enumerate(ITEMS)); zz = sum(x[i] * t["z"] for i, t in enumerate(ITEMS))
    ok = Xs == 0 and zz % 4 == 0
    return sign * float(np.dot(mu, q)), q, ok, {t["lab"]: int(x[i]) for i, t in enumerate(ITEMS) if x[i]}


def milp_certificate(scalars, dmax=24):
    ITEMS = milp_items(scalars)
    mu4 = np.array([4 * float(m) for m in DP.MU])
    worst = None
    for d in range(5, dmax + 1):
        for sign in (1, -1):
            r = milp_solve(ITEMS, d, mu4, sign)
            if r is None:
                continue
            exc = int(round(r[0])) - 4 * (d - 4)
            if worst is None or exc > worst[0]:
                worst = (exc, d, r[3], r[2])
    return {"worst_excess_x4": worst[0], "at_d": worst[1], "mono": worst[2], "exact_ok": worst[3], "holds": worst[0] <= 0}


def milp_colgen(scalars, dmax=20, iters=300):
    ITEMS = milp_items(scalars)
    cuts = []
    for it in range(iters):
        if cuts:
            A = np.array([c[0] for c in cuts] + [[-v for v in c[0]] for c in cuts], float)
            bb = np.array([c[1] for c in cuts] * 2, float)
        else:
            A = None; bb = None
        res = linprog(np.array([-1.0, 0, 0, 0, 0, 0]), A_ub=A, b_ub=bb, bounds=[(-60, 60)] * 6, method="highs")
        mu = res.x
        worst = None
        for d in range(5, dmax + 1):
            for sign in (1, -1):
                r = milp_solve(ITEMS, d, mu, sign)
                if r is None:
                    continue
                v = r[0] - (d - 4)
                if worst is None or v > worst[0]:
                    worst = (v, tuple(sign * qi for qi in r[1]), d - 4)
        if worst is None or worst[0] <= 1e-6:
            return {"4mu0": 4 * float(mu[0]), "iterations": it, "cuts": len(cuts)}
        cuts.append((worst[1], worst[2]))
    return {"4mu0": None, "converged": False}


def main():
    out = {"anomalies": anomalies(), "pq": pq_anomaly(), "designs": {}}
    print("anomalies:", {k: v for k, v in out["anomalies"].items() if k != "species"}, flush=True)
    print("PQ:", out["pq"], flush=True)
    for name, sc in DESIGNS.items():
        t0 = time.time()
        rec = {"scalars": sc}
        rec["kernel"] = kernel(sc)
        rec["dp_certificate"] = dp_certificate(sc)
        rec["dp_lp_optimum"] = dp_lp_optimum(sc)
        rec["milp_certificate_dressed_d<=24"] = milp_certificate(sc)
        rec["milp_colgen_4mu0"] = milp_colgen(sc)
        rec["seconds"] = time.time() - t0
        out["designs"][name] = rec
        print("\n==", name, "(%.1fs)" % rec["seconds"])
        print("  kernel:", {k: v for k, v in rec["kernel"].items() if k != "extra_examples"})
        print("  DP certificate:", rec["dp_certificate"])
        print("  DP-oracle LP optimum:", rec["dp_lp_optimum"])
        print("  MILP certificate:", rec["milp_certificate_dressed_d<=24"])
        print("  MILP column generation:", rec["milp_colgen_4mu0"], flush=True)
    tag = "" if len(sys.argv) == 1 else "_" + "_".join(sys.argv[1:])
    (HERE / f"d1_contract{tag}.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
