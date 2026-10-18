#!/usr/bin/env python3
"""Stage-2a "model": D1 contract re-check for the FINAL v22-L2 content
    B63 fermions (verbatim)  +  Phi210 (real, X 0), Delta126bar (X -2), H10 (complex, X -2), S (X 4), Phi17 (X 17)
    +  A45 (real 45_H, X 0, Z17 phase 1, centre class 0)
with the scalar potential = the v20 51-parameter exact-X potential + the 34 new real A-parameters of census_v22.py.

(a) anomalies [EXACT, Fractions]: [SO(10)]^2 X, X^3, grav-X (scalars do not contribute); [SO(10)]^3 vanishes
    identically (no cubic Casimir), no Witten anomaly for SO(10).
(b) accidental U(1) kernel [EXACT, sympy rank]: 16 fermion species + the complex scalars Delta, H10, S, Phi17 (real
    fields carry charge 0 under every U(1)).  Constraint rows: the Yukawa structures FOUND by the exhaustive fermion
    catalogue of census_v22.py (must be the 12) + EVERY phase-sensitive renormalizable scalar invariant FOUND by the
    exact census (v20 orbits and the new A orbits; no hand-entered singlet list).  Also the superset of all
    X/centre-neutral phase-sensitive monomials of degree <= 4 (whether or not SO(10) singlets exist).
    PQ = X - 17 G2: N and E recomputed from SU(3) Dynkin indices and electric-charge sums of complete SO(10)
    multiplets; E/N; N_DW.
(c) quality certificate K_min >= 17 [EXACT]: R2-V integer DP (dual_dp_orig.py, copied unedited: functions dp,
    backtrack) with the FINAL scalar item list (A45 included explicitly), brute-force validation of the DP for
    d <= 7 with A45 present, own cutting-plane LP (DP oracle), independent HiGHS MILP certificate (dressed set,
    d <= 24, both signs) and MILP column generation.
Outputs: d1_contract_v22.json (+ log on stdout).
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction as Fr
from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dual_dp_orig as DP  # noqa: E402  (functions only; main() never called)

CENSUS = json.loads((HERE / "census_v22.json").read_text(encoding="utf-8"))

FERMIONS = DP.FERMIONS            # B63, verbatim (name, signed SO(10) dim, X)
MULT = {"F": 3, "V1": 2, "T": 2, "NMm": 2}
DIM = {16: 16, -16: 16, 10: 10, 1: 1}
T_SO10 = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}         # Dynkin index, T(10) = 1
N_SU3 = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}          # sum of SU(3) indices (T(3) = 1/2): 16 -> 4 x 1/2
Q2SUM = {16: Fr(16, 3), -16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}  # sum of Q_em^2 over the multiplet
ZC = {16: 1, -16: 3, 10: 2, -10: 2, 126: 2, -126: 2, 1: 0, 210: 0, 45: 0}

SCALARS_V22 = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
               ("Phi17", 1, 17, False), ("A45", 45, 0, True)]
CENSUS_NAME = {"P": "Phi210", "A": "A45", "H": "H10", "Hb": "H10*", "D": "Delta", "Db": "Delta*", "S": "S",
               "Sb": "S*", "T": "Phi17", "Tb": "Phi17*"}
CPLX = {"Delta": (-2, 2), "H10": (-2, 2), "S": (4, 0), "Phi17": (17, 0)}
FERM_NAME = {"T10": "T"}


# ----------------------------------------------------------------------------------------------------------------
def anomalies():
    a2x = Fr(0); x3 = Fr(0); gx = Fr(0); rows = []
    for n, r, x in FERMIONS:
        m = MULT.get(n, 1)
        a2x += m * T_SO10[r] * x
        x3 += m * DIM[r] * Fr(x) ** 3
        gx += m * DIM[r] * x
        rows.append({"field": n, "rep": r, "X": x, "copies": m})
    net16 = sum(MULT.get(n, 1) * (1 if r == 16 else -1 if r == -16 else 0) for n, r, _ in FERMIONS)
    return {"SO10^2_X": str(a2x), "X^3": str(x3), "grav_X": str(gx), "SO10^3": "0 (no cubic Casimir of SO(10))",
            "Witten": "none (pi_4(Spin(10)) = 0)", "anomaly_free": a2x == 0 and x3 == 0 and gx == 0,
            "net_16_minus_16bar": net16, "species": rows,
            "note": "scalars (incl. the new real 45_H) do not contribute to gauge anomalies"}


# ----------------------------------------------------------------------------------------------------------------
def kernel():
    species = [f[0] for f in FERMIONS] + list(CPLX)
    idx = {n: i for i, n in enumerate(species)}
    # Yukawas from the exhaustive catalogue
    yuk_rows = []; yuk_list = []
    for r in CENSUS["fermion_catalogue"]["invariant"]:
        a, b = r["pair"]; a = FERM_NAME.get(a, a); b = FERM_NAME.get(b, b)
        row = [0] * len(species)
        row[idx[a]] += 1; row[idx[b]] += 1
        s = r["scalar"]
        sm = {"H10": ("H10", 1), "H10^dag": ("H10", -1), "Delta126bar": ("Delta", 1), "Delta126bar^dag": ("Delta", -1),
              "S": ("S", 1), "S^dag": ("S", -1), "Phi17": ("Phi17", 1), "Phi17^dag": ("Phi17", -1)}.get(s)
        if sm:
            row[idx[sm[0]]] += sm[1]
        yuk_rows.append(row); yuk_list.append(f"{a}.{b}.{s}")

    def orbit_rows(orbits):
        rows, names = [], []
        for o in orbits:
            md = o["md"] if "md" in o else o
            net = {}
            for f, n in md.items():
                nm = CENSUS_NAME[f]
                base = nm.rstrip("*"); sgn = -1 if nm.endswith("*") else 1
                if base in CPLX:
                    net[base] = net.get(base, 0) + sgn * n
            if any(v for v in net.values()):
                row = [0] * len(species)
                for k, v in net.items():
                    row[idx[k]] += v
                rows.append(row); names.append(o.get("multidegree", str(md)))
        return rows, names

    # v20 orbits: the attested v20 direction list (census_v22.V20_ORBITS, reproduced exactly by the census);
    # new A orbits: taken from census_v22.json (no hand-entered singlet list)
    import census_v22 as C  # noqa: E402
    v20_mds = [dict(md, multidegree=oid) for oid, (md, n) in C.V20_ORBITS.items()]
    r20, n20 = orbit_rows([{"md": {k: v for k, v in m.items() if k != "multidegree"}, "multidegree": m["multidegree"]}
                           for m in v20_mds])
    rA, nA = orbit_rows(CENSUS["v22_new_A_orbits"])
    M_y = sp.Matrix(yuk_rows)
    M_v20 = sp.Matrix(yuk_rows + r20)
    M_v22 = sp.Matrix(yuk_rows + r20 + rA) if rA else M_v20
    # superset: every X- and centre-neutral, non-self-conjugate monomial of degree <= 4 in the complex scalars
    labels = []
    for n, (x, z) in CPLX.items():
        labels.append((n, x, z, +1)); labels.append((n + "*", -x, (-z) % 4, -1))
    sup = []
    for deg in (2, 3, 4):
        for combo in itertools.combinations_with_replacement(range(len(labels)), deg):
            if sum(labels[i][1] for i in combo) != 0 or sum(labels[i][2] for i in combo) % 4:
                continue
            net = {}
            for i in combo:
                net[labels[i][0].rstrip("*")] = net.get(labels[i][0].rstrip("*"), 0) + labels[i][3]
            if all(v == 0 for v in net.values()):
                continue
            row = [0] * len(species)
            for k, v in net.items():
                row[idx[k]] += v
            sup.append(row)
    M_sup = sp.Matrix(yuk_rows + r20 + rA + sup)
    X = [x for _, _, x in FERMIONS] + [CPLX[n][0] for n in CPLX]
    G2 = [0] * len(species); G2[idx["V1"]] = -1; G2[idx["Vb1"]] = 1; G2[idx["Phi17"]] = 1
    allrows = yuk_rows + r20 + rA + sup
    inker = lambda v: all(sum(a * b for a, b in zip(row, v)) == 0 for row in allrows)
    # round-1 kernel basis Q = (G2, f1..f5) (incl. scalar entries, Phi17 G2 = 1) + X must span the kernel
    basis = [X]
    for j in range(6):
        basis.append([DP.Q.get(n, (0,) * 6)[j] for n in species])
    B = sp.Matrix(basis)
    ns = M_v22.nullspace()
    span_ok = (B.rank() == 7 and all(inker(b) for b in basis) and len(ns) == 7)
    new_rows_in_v20_rowspace = (M_v22.rank() == M_v20.rank())
    return {"species": species, "n_species": len(species), "yukawa_structures": yuk_list,
            "n_yukawa_structures": len(yuk_rows), "rank_yukawas_only": int(M_y.rank()),
            "v20_phase_sensitive_orbits": n20, "rank_yukawas_plus_v20": int(M_v20.rank()),
            "new_A_phase_sensitive_orbits": nA, "rank_yukawas_plus_v20_plus_A": int(M_v22.rank()),
            "kernel_dim_final": len(species) - int(M_v22.rank()),
            "new_A_rows_add_no_constraint": bool(new_rows_in_v20_rowspace),
            "rank_with_superset_of_all_X_centre_neutral_phase_monomials_deg<=4": int(M_sup.rank()),
            "n_superset_monomials": len(sup),
            "X_in_kernel": inker(X), "G2_in_kernel": inker(G2),
            "kernel_spanned_by_X_G2_f1..f5_(round-1_basis)": bool(span_ok)}


def pq_numbers():
    G2 = {"V1": -1, "Vb1": 1}
    nX = sum(MULT.get(n, 1) * x * N_SU3[r] for n, r, x in FERMIONS)
    nG2 = sum(MULT.get(n, 1) * G2.get(n, 0) * N_SU3[r] for n, r, x in FERMIONS)
    eX = sum(MULT.get(n, 1) * x * Q2SUM[r] for n, r, x in FERMIONS)
    eG2 = sum(MULT.get(n, 1) * G2.get(n, 0) * Q2SUM[r] for n, r, x in FERMIONS)
    N = nX - 17 * nG2; E = eX - 17 * eG2
    # f-symmetries carry no QCD anomaly
    fN = []
    for j in range(1, 6):
        fN.append(str(sum(MULT.get(n, 1) * DP.Q[n][j] * N_SU3[r] for n, r, x in FERMIONS)))
    # PQ charges of the scalars (PQ = X - 17 G2): Phi17 neutral, S 4, H10 -2, Delta -2, Phi210 0, A45 0
    pq_sc = {"Phi210": 0, "A45": 0, "Delta": -2, "H10": -2, "S": 4, "Phi17": 17 - 17 * 1}
    # domain-wall number: PQ-violating vev monomial S*^17 Phi17^4 (R2-V); theta_eff = 17 theta_S - 4 theta_17;
    # the axion is the gauge-orthogonal combination; N_DW = 1 mod gauge iff gcd(17, 4) = 1
    return {"N(X)": str(nX), "N(G2)": str(nG2), "N(f1..f5)": fN, "N(PQ=X-17G2)": str(N),
            "E(X)": str(eX), "E(G2)": str(eG2), "E(PQ)": str(E), "E/N": str(E / N) if N else None,
            "PQ_charges_scalars": pq_sc,
            "N_DW_mod_gauge": "1 (gcd(17,4) = %d; A45 is real, X = 0, PQ = 0, centre class 0: adds no vev phase)" % gcd(17, 4)}


# ----------------------------------------------------------------------------------------------------------------
def dp_items(scalars, mu=DP.MU, scale=4, use_centre=True):
    out = []
    for n, r, x in FERMIONS:
        for bar in (False, True):
            s = -1 if bar else 1
            q = tuple(s * c for c in DP.Q[n])
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4 if use_centre else 0,
                        "v": v, "w": 3, "u": 0 if bar else 1, "b": 1 if bar else 0, "q": q})
    for n, r, x, real in scalars:
        qn = DP.Q.get(n, (0,) * 6)
        for bar in ((False,) if real else (False, True)):
            s = -1 if bar else 1
            q = tuple(s * c for c in qn)
            v = scale * sum(m * c for m, c in zip(mu, q))
            out.append({"label": n + ("^" if bar else ""), "X": s * x, "z": (s * ZC[r]) % 4 if use_centre else 0,
                        "v": v, "w": 2, "u": 0, "b": 0, "q": q})
    return out


def brute_force(scalars, dmax=7):
    its = dp_items(scalars)
    res = {}
    W = 2 * dmax

    def rec(k, w, X, z, pu, pb, v):
        if k == len(its):
            if X == 0 and z % 4 == 0 and pu == pb:
                d = w // 2 + (1 if pu else 0)
                if 5 <= d <= dmax and w % 2 == 0:
                    e = int(v) - 4 * (d - 4)
                    if d not in res or e > res[d]:
                        res[d] = e
            return
        it = its[k]; m = 0
        while w + m * it["w"] <= W:
            rec(k + 1, w + m * it["w"], X + m * it["X"], z + m * it["z"], pu ^ (m * it["u"] & 1),
                pb ^ (m * it["b"] & 1), v + m * it["v"])
            m += 1
    rec(0, 0, 0, 0, 0, 0, 0)
    return res


def dp_table(scalars, dmax=40, use_centre=True):
    its = dp_items(scalars, use_centre=use_centre)
    xmax = max(abs(it["X"]) for it in its)
    best, par = DP.dp(its, 2 * dmax, xmax)
    rows = []
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
        rows.append({"d": d, "max_excess_x4": exc, "derivative": parity, "argmax": mono})
    return rows


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
            return {"4mu0_LP_optimum": 4 * float(mu[0]), "mu": [float(m) for m in mu], "iterations": it_,
                    "cuts": len(cuts)}
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


def milp_solve(ITEMS, d, mu, sign):
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
    res = milp(c, constraints=LinearConstraint(np.array(A), np.array(lo, float), np.array(hi, float)),
               integrality=np.ones(nv), bounds=Bounds(lb, ub), options={"time_limit": 120, "mip_rel_gap": 0.0})
    if res.x is None:
        return None
    x = np.rint(res.x).astype(int)
    q = [int(sum(x[i] * t["q"][j] for i, t in enumerate(ITEMS))) for j in range(6)]
    Xs = sum(x[i] * t["X"] for i, t in enumerate(ITEMS)); zz = sum(x[i] * t["z"] for i, t in enumerate(ITEMS))
    return sign * float(np.dot(mu, q)), q, bool(Xs == 0 and zz % 4 == 0), {t["lab"]: int(x[i]) for i, t in enumerate(ITEMS) if x[i]}


def milp_certificate(scalars, dmax=24):
    ITEMS = milp_items(scalars)
    mu4 = np.array([4 * float(m) for m in DP.MU])
    worst = None; per_d = []
    for d in range(5, dmax + 1):
        for sign in (1, -1):
            r = milp_solve(ITEMS, d, mu4, sign)
            if r is None:
                continue
            exc = int(round(r[0])) - 4 * (d - 4)
            per_d.append((d, sign, exc))
            if worst is None or exc > worst[0]:
                worst = (exc, d, r[3], r[2])
    return {"worst_excess_x4": worst[0], "at_d": worst[1], "mono": worst[2], "exact_ok": worst[3],
            "holds": worst[0] <= 0, "per_d_sign_excess": per_d}


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
    t0 = time.time()
    out = {"content": "B63 fermions + Phi210, Delta126bar, H10, S, Phi17 + A45 (real 45_H, X=0)"}
    out["anomalies"] = anomalies()
    print("(a) anomalies:", {k: v for k, v in out["anomalies"].items() if k != "species"}, flush=True)
    out["kernel"] = kernel()
    print("(b) kernel:", {k: v for k, v in out["kernel"].items() if k not in ("species",)}, flush=True)
    out["pq"] = pq_numbers()
    print("    PQ:", out["pq"], flush=True)
    sc = SCALARS_V22
    # item-type identity of A45 and Phi210 in the DP (the structural reason nothing can change)
    its = dp_items(sc)
    tA = [(i["X"], i["z"], i["v"], i["w"], i["u"], i["b"], i["q"]) for i in its if i["label"] == "A45"]
    tP = [(i["X"], i["z"], i["v"], i["w"], i["u"], i["b"], i["q"]) for i in its if i["label"] == "Phi210"]
    out["A45_item_type_equals_Phi210"] = tA == tP
    bf = brute_force(sc, 7)
    tab = dp_table(sc, 40)
    dpd = {r["d"]: r["max_excess_x4"] for r in tab}
    out["dp_vs_bruteforce_d<=7"] = {"dp": {d: dpd.get(d) for d in range(5, 8)}, "brute": bf,
                                   "agree": all(dpd.get(d) == bf.get(d) for d in range(5, 8))}
    print("(c) A45 item type == Phi210:", out["A45_item_type_equals_Phi210"], "| DP vs brute force d<=7:",
          out["dp_vs_bruteforce_d<=7"], flush=True)
    out["dp_rows"] = tab
    w20 = max(r["max_excess_x4"] for r in tab if r["d"] <= 20)
    out["dp_certificate"] = {"max_excess_x4_5<=d<=20": w20, "holds_d<=20": w20 <= 0,
                             "max_excess_x4_d<=40": max(r["max_excess_x4"] for r in tab),
                             "tight_d": [r["d"] for r in tab if r["max_excess_x4"] == 0],
                             "A45_in_any_argmax": any("A45" in (r["argmax"] or {}) for r in tab)}
    print("    DP certificate:", out["dp_certificate"], flush=True)
    for r in tab:
        print("      d=%2d  max 4(mu.q)-4(d-4) = %3d  deriv=%d  %s" % (r["d"], r["max_excess_x4"], r["derivative"], r["argmax"]))
    nc = dp_table(sc, 12, use_centre=False)
    out["no_centre_superset_d<=12"] = {"max_excess_x4": max(r["max_excess_x4"] for r in nc),
                                       "first_violation_d": next((r["d"] for r in nc if r["max_excess_x4"] > 0), None),
                                       "rows": nc}
    print("    no-centre superset (control):", {k: v for k, v in out["no_centre_superset_d<=12"].items() if k != "rows"}, flush=True)
    out["dp_lp_optimum"] = dp_lp_optimum(sc)
    print("    DP-oracle LP optimum:", out["dp_lp_optimum"], flush=True)
    out["milp_certificate_dressed_d<=24"] = milp_certificate(sc)
    print("    MILP certificate:", {k: v for k, v in out["milp_certificate_dressed_d<=24"].items() if k != "per_d_sign_excess"}, flush=True)
    out["milp_colgen"] = milp_colgen(sc)
    print("    MILP column generation:", out["milp_colgen"], flush=True)
    out["K_min_ge_17"] = bool(out["dp_certificate"]["holds_d<=20"] and out["milp_certificate_dressed_d<=24"]["holds"]
                              and abs(out["dp_lp_optimum"]["4mu0_LP_optimum"] - 17) < 1e-6
                              and out["milp_colgen"]["4mu0"] is not None and abs(out["milp_colgen"]["4mu0"] - 17) < 1e-6)
    out["seconds"] = time.time() - t0
    (HERE / "d1_contract_v22.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("K_min >= 17:", out["K_min_ge_17"], f"({out['seconds']:.0f}s)")


if __name__ == "__main__":
    main()
