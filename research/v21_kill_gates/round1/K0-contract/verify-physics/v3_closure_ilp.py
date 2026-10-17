"""Verifier: independent enumeration of X-neutral SO(10)-singlet Planck operators (dim 5..8, <= 4 fermions)
with my own Klimyk singlet counter, and my own integer program for the cheapest PQ-violating VACUUM closure.

Differences from the researcher's ILP (deliberate, to test robustness of the kill):
  * H10 lines must be paired explicitly: net H10 = 0 after adding kappa (H H S) / kappa* (H* H* S*) vertices
    and the H H* propagator; H10 EW vevs are NOT allowed (they are ~1e-11 of the heavy scale).
  * Delta126bar lines: allowed as vevs (v_R) only when the net count is what remains; a Delta Delta* pair is a
    propagator (fine); I report the Delta vev content.
  * Phi210 is NOT included as a field (same as the researcher; adding it can only lower K).
  * per-species fermion chirality balance: unbarred - barred = 0 for every species over operators + Yukawas.
  * PQ violation: net Phi17 number of the vev monomial = +-4 (lemma); I also require net S != 0 consistency.
Objective: K = sum_j m_j (d_j - 4), then fewest vertices.
Variants: ALL; no Phi-sector lines; no Phi-sector and no H10-type Yukawas (lamF2, lam3P, yAM, yBN) and no family
Yukawas (Y10, Y126) = researcher's E; additionally a variant forbidding every dim-5 operator (robustness).
Then an NDA estimate of dtheta for the solutions with my own counting (explicit epsilon couplings after vevs).
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from so10_singlets_klimyk import singlets  # noqa: E402

# name: (rep, X, is_fermion)
FIELDS = {"F": (16, 1, True), "TenA": (10, -1, True), "TenB": (10, 5, True), "Vec1": (16, 0, True), "Vec1bar": (-16, 4, True),
          "Vec2": (16, -3, True), "Vec2bar": (-16, 7, True), "Vec3": (16, -6, True), "Vec3bar": (-16, 10, True),
          "PhiV": (16, -9, True), "PhiVbar": (-16, -8, True), "SingN": (1, -3, True), "SingM": (1, -1, True),
          "H10": (10, -2, False), "Delta": (-126, -2, False), "S": (1, 4, False), "Phi17": (1, 17, False)}
FERMS = [n for n, v in FIELDS.items() if v[2]]
SELF = {1, 10}
YUK = {"Y10": (["F", "F"], {"H10": 1}), "Y126": (["F", "F"], {"Delta": 1}), "lamF2": (["F", "Vec2"], {"H10": -1}),
       "lam3P": (["Vec3bar", "PhiVbar"], {"H10": 1}), "y1": (["Vec1", "Vec1bar"], {"S": -1}), "y2": (["Vec2", "Vec2bar"], {"S": -1}),
       "y3": (["Vec3", "Vec3bar"], {"S": -1}), "yP": (["PhiV", "PhiVbar"], {"Phi17": 1}), "yAB": (["TenA", "TenB"], {"S": -1}),
       "yAM": (["TenA", "SingM"], {"H10": -1}), "yBN": (["TenB", "SingN"], {"H10": 1}), "yNM": (["SingN", "SingM"], {"S": 1})}
MPL = 2.435e18
CHI = 0.0755 ** 4


def rep_of(name, barred):
    r = FIELDS[name][0]
    return r if (abs(r) in SELF or not barred) else -r


def enumerate_ops(dim_max=Fr(8), max_f=4):
    """Operators as dicts {(name, barred): count}; X = 0; dim in [5, dim_max]; Lorentz: (#unbarred, #barred)
    fermions both even or both odd (one derivative, +1 dim); SO(10) singlet verified by Klimyk."""
    fl = [(n, b) for n in FERMS for b in (False, True)]
    ops = []
    cache = {}
    for nf in range(0, max_f + 1):
        for combo in itertools.combinations_with_replacement(range(len(fl)), nf):
            fs = [fl[i] for i in combo]
            nu = sum(1 for _n, b in fs if not b)
            nb = nf - nu
            if (nu - nb) % 2:
                continue
            deriv = 1 if nu % 2 else 0
            fx = sum((-1 if b else 1) * FIELDS[n][1] for n, b in fs)
            fcost = Fr(3 * nf, 2) + deriv
            budget = dim_max - fcost
            if budget < 0:
                continue
            R = int(budget)
            for nh in range(-R, R + 1):
                for nd in range(-R, R + 1):
                    for npp in range(-R, R + 1):
                        c = abs(nh) + abs(nd) + abs(npp)
                        if c > budget:
                            continue
                        xs = fx - 2 * nh - 2 * nd + 17 * npp
                        if xs % 4:
                            continue
                        ns = -xs // 4
                        dim = fcost + c + abs(ns)
                        if dim > dim_max or dim < 5:
                            continue
                        counts = {}
                        for n, b in fs:
                            counts[(n, b)] = counts.get((n, b), 0) + 1
                        for name, k in (("H10", nh), ("Delta", nd), ("S", ns), ("Phi17", npp)):
                            if k:
                                counts[(name, k < 0)] = abs(k)
                        reps = []
                        for (n, b), k in counts.items():
                            r = rep_of(n, b)
                            if r != 1:
                                reps += [r] * k
                        key = tuple(sorted(reps))
                        if key not in cache:
                            cache[key] = singlets(list(key))
                        if cache[key] == 0:
                            continue
                        ops.append({"counts": counts, "dim": dim, "deriv": deriv, "nf": nf, "singlets": cache[key]})
    return ops, cache


def label(counts):
    return " ".join("%s%s%s" % (n, "*" if b else "", "^%d" % k if k > 1 else "") for (n, b), k in counts.items())


def build_ilp(ops, forbid_names=(), forbid_yuk=(), forbid_dim=(), require_no_delta_vev=False):
    """Columns: ops, Yukawa vertices (+ conj), kappa, kappa*.  Rows: chirality per species; net H10 = 0;
    net Phi17 = +-4 (two runs)."""
    cols = []
    for j, op in enumerate(ops):
        if op["dim"] in forbid_dim:
            continue
        if any(n in forbid_names for (n, b) in op["counts"]):
            continue
        cols.append(("op", j))
    for name in YUK:
        if name in forbid_yuk:
            continue
        cols.append(("yuk", name, +1))
        cols.append(("yuk", name, -1))
    cols.append(("kappa", +1))
    cols.append(("kappa", -1))

    def col_vec(col):
        chir = {n: 0 for n in FERMS}
        sc = {"H10": 0, "Delta": 0, "S": 0, "Phi17": 0}
        cost = 0.0
        if col[0] == "op":
            op = ops[col[1]]
            for (n, b), k in op["counts"].items():
                s = -1 if b else 1
                if FIELDS[n][2]:
                    chir[n] += s * k
                else:
                    sc[n] += s * k
            cost = float(op["dim"] - 4)
        elif col[0] == "yuk":
            ferms, scal = YUK[col[1]]
            s = col[2]
            for f in ferms:
                chir[f] += s
            for n, q in scal.items():
                sc[n] += s * q
        else:
            s = col[1]
            sc["H10"] += 2 * s
            sc["S"] += s
        return chir, sc, cost

    vecs = [col_vec(c) for c in cols]
    n = len(cols)
    c = np.array([v[2] + 1e-3 for v in vecs])
    rows, lb, ub = [], [], []
    for sp in FERMS:
        rows.append([v[0][sp] for v in vecs])
        lb.append(0)
        ub.append(0)
    rows.append([v[1]["H10"] for v in vecs])
    lb.append(0)
    ub.append(0)
    if require_no_delta_vev:
        rows.append([v[1]["Delta"] for v in vecs])
        lb.append(0)
        ub.append(0)
    phi_row = [v[1]["Phi17"] for v in vecs]
    nop_row = [1.0 if col[0] == "op" else 0.0 for col in cols]
    best = None
    for target in (4, -4):
        A = np.array(rows + [phi_row, nop_row], dtype=float)
        lbs = lb + [target, 1]
        ubs = ub + [target, 40]
        res = milp(c, constraints=LinearConstraint(A, lbs, ubs), integrality=np.ones(n),
                   bounds=Bounds(np.zeros(n), np.full(n, 16.0)))
        if res.success and (best is None or res.fun < best[0]):
            sol = {cols[i]: int(round(res.x[i])) for i in range(n) if round(res.x[i]) > 0}
            best = (res.fun, sol, target)
    if best is None:
        return None
    K = sum(float(ops[col[1]]["dim"] - 4) * m for col, m in best[1].items() if col[0] == "op")
    # vev monomial and loop count
    sc = {"H10": 0, "Delta": 0, "S": 0, "Phi17": 0}
    nferm = 0
    nvert = 0
    nH = 0
    for col, m in best[1].items():
        chir, s, _ = col_vec(col)
        for k in sc:
            sc[k] += m * s[k]
        nvert += m
        if col[0] == "op":
            nferm += m * ops[col[1]]["nf"]
            nH += m * sum(k for (n, b), k in ops[col[1]]["counts"].items() if n == "H10")
        elif col[0] == "yuk":
            nferm += 2 * m
            nH += m * abs(YUK[col[1]][1].get("H10", 0))
        else:
            nH += 2 * m
    props = nferm // 2 + nH // 2
    loops = props - nvert + 1
    desc = {"K": K, "target_Phi17": best[2],
            "ops": ["%d x [%s] (dim %s)" % (m, label(ops[col[1]]["counts"]), ops[col[1]]["dim"]) for col, m in best[1].items() if col[0] == "op"],
            "yukawas": {"%s%s" % (col[1], "" if col[2] > 0 else "*"): m for col, m in best[1].items() if col[0] == "yuk"},
            "kappa": {("kappa" if col[1] > 0 else "kappa*"): m for col, m in best[1].items() if col[0] == "kappa"},
            "vev_monomial": {k: v for k, v in sc.items() if v}, "fermion_fields": nferm, "H10_propagators": nH // 2,
            "vertices": nvert, "loops": loops}
    return desc


def nda(desc, Ms=1.0e13, S=3.3e13, Phi=1.0e17, vR=2.6e13, y=0.35, lamH=1.0, Y=0.5, kappa=5.0e12, mH=1.0e13):
    """V ~ (16pi^2)^-L * prod(couplings) * prod(Planck-operator vev factors) * kappa^n * loop-scale factors.
    Counting: each Planck operator of dim d with v vev fields contributes vevs/M_Pl^(d-4); the remaining mass
    dimension of V (4) minus what the vevs/kappa/eps supply is made of the loop mass scale M = Ms for
    fermion-dominated integrals (IR dominated when the integral converges).  H10 lines at mH: each H10
    propagator pair carries a factor (Ms/mH)^2 relative to the all-at-Ms estimate (D<0 only)."""
    L = desc["loops"]
    lg = -L * math.log10(16 * math.pi ** 2)
    for name, m in desc["yukawas"].items():
        base = name.rstrip("*")
        lg += m * math.log10(y if base in ("y1", "y2", "y3", "yAB", "yNM", "yP") else (lamH if base in ("lamF2", "lam3P", "yAM", "yBN") else Y))
    vm = desc["vev_monomial"]
    nk = sum(desc["kappa"].values())
    lg += abs(vm.get("S", 0)) * math.log10(S) + abs(vm.get("Phi17", 0)) * math.log10(Phi) + abs(vm.get("Delta", 0)) * math.log10(vR)
    lg += nk * math.log10(kappa)
    K = desc["K"]
    D = 4 + K - (abs(vm.get("S", 0)) + abs(vm.get("Phi17", 0)) + abs(vm.get("Delta", 0))) - nk
    Mloop = Ms if D < 0 else MPL
    lg += D * math.log10(Mloop) - K * math.log10(MPL)
    # heavy H10 lines: suppression (Ms/mH)^(2 per H10 propagator) when IR dominated
    lg_heavyH = lg + (2 * desc["H10_propagators"] * math.log10(Ms / mH) if D < 0 else 0.0)
    lg_tree = math.log10(2) + 4 * math.log10(Phi) + 17 * math.log10(S) - 17 * math.log10(MPL)
    return {"loop_dim_D": D, "log10_V": lg, "log10_dtheta": lg - math.log10(CHI), "log10_dtheta_H10_at_mH": lg_heavyH - math.log10(CHI),
            "log10_ratio_to_tree": lg - lg_tree}


def main():
    ops, cache = enumerate_ops()
    print("verified operators (dim<=8, <=4 fermions):", len(ops), "| distinct rep multisets:", len(cache),
          "| zero-singlet multisets:", sum(1 for v in cache.values() if v == 0))
    by_dim = {}
    for op in ops:
        by_dim[str(op["dim"])] = by_dim.get(str(op["dim"]), 0) + 1
    print("by dimension:", by_dim)
    phi_names = ("PhiV", "PhiVbar")
    h10yuk = ("lamF2", "lam3P", "yAM", "yBN")
    variants = {
        "A_all": dict(),
        "B_no_PhiSector": dict(forbid_names=phi_names, forbid_yuk=("yP", "lam3P")),
        "C_no_PhiSector_lamF2=0": dict(forbid_names=phi_names, forbid_yuk=("yP", "lam3P", "lamF2")),
        "E_no_PhiSector_no_H10Yuk_no_familyYuk": dict(forbid_names=phi_names, forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126")),
        "E_plus_no_Delta_vev": dict(forbid_names=phi_names, forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126"), require_no_delta_vev=True),
        "E_plus_no_dim5_ops": dict(forbid_names=phi_names, forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126"), forbid_dim=(Fr(5),)),
        "E_plus_no_dim5_dim6_ops": dict(forbid_names=phi_names, forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126"), forbid_dim=(Fr(5), Fr(6))),
        "E_no_kappa_needed(no_H10_at_all)": dict(forbid_names=phi_names + ("H10",), forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126")),
        "S_sector_only_no_F_no_Delta_no_H10": dict(forbid_names=phi_names + ("H10", "Delta", "F", "TenA", "TenB", "SingN", "SingM"),
                                                   forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126", "yAB", "yNM")),
    }
    out = {"n_ops": len(ops), "by_dim": by_dim, "variants": {}}
    for tag, kw in variants.items():
        d = build_ilp(ops, **kw)
        if d is None:
            print("==", tag, ": infeasible")
            out["variants"][tag] = None
            continue
        d["nda_all_lines_Ms"] = nda(d)
        d["nda_H10_at_MU"] = nda(d, mH=2.1e16)
        d["nda_kappa_1e9"] = nda(d, kappa=1.0e9)
        out["variants"][tag] = d
        print("==", tag, "K =", d["K"], "| loops", d["loops"], "| vev", d["vev_monomial"], "| kappa", d["kappa"])
        for o in d["ops"]:
            print("     ", o)
        print("      yukawas", d["yukawas"])
        print("      NDA: D=%d log10 dtheta = %.1f (H10 at M_U: %.1f; kappa=1e9: %.1f; ratio to tree 10^%.1f)" % (
            d["nda_all_lines_Ms"]["loop_dim_D"], d["nda_all_lines_Ms"]["log10_dtheta"], d["nda_H10_at_MU"]["log10_dtheta"],
            d["nda_kappa_1e9"]["log10_dtheta"], d["nda_all_lines_Ms"]["log10_ratio_to_tree"]))
    # list of the dim-5 PQ-relevant operators mixing sectors (for the record)
    d5 = [label(op["counts"]) for op in ops if op["dim"] == 5]
    out["dim5_ops"] = d5
    print("dim-5 operators:", len(d5))
    (HERE / "v3_closure_ilp.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
