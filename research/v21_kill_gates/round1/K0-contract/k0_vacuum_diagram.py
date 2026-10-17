"""Gate K0 (3), refined: minimal Planck power of a PQ-violating VACUUM diagram of the v21-F17 theory,
with (i) candidate Planck operators restricted to genuine SO(10) singlets (Susyno ReduceRepProduct count),
(ii) exact closure: every fermion species must balance (unbarred - barred = 0 over Planck operators and
renormalizable Yukawa vertices), (iii) PQ violation = net Phi17 number of the vev monomial = +-4 (lemma),
and (iv) an NDA-style estimate of the induced theta shift for the optimal diagrams.

Why this matters: the single-operator analysis (k0_quality_relics.py) shows the minimal PQ-violating
X-invariant operator has dimension 21 (scalar) / 19 (fermionic), but products of several lower-dimension
Planck operators whose fermion-number charges cancel can close into a PQ-violating vacuum diagram with a
smaller total Planck power K = sum(d_i - 4); the manuscript's v20 NDA bound (P = 12) is exactly this effect.
"""
from __future__ import annotations

import itertools
import json
import math
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from k0_quality_relics import FIELDS, all_fields  # noqa: E402

WOLFRAM = r"C:\Program Files\Wolfram Research\Wolfram Engine\15.0\wolframscript.exe"
SUSYNO_WLS = HERE / "tools" / "so10_singlets.wls"
REP = {"F": 16, "TenA": 10, "TenB": 10, "Vec1": 16, "Vec1bar": -16, "Vec2": 16, "Vec2bar": -16, "Vec3": 16,
       "Vec3bar": -16, "PhiV": 16, "PhiVbar": -16, "SingN": 1, "SingM": 1, "H10": 10, "Delta": -126, "S": 1, "Phi17": 1}
SELF = {1, 10, 210}
FERMION_NAMES = [n for n in FIELDS if FIELDS[n][7]]
SCALAR_NAMES = ["H10", "Delta", "S", "Phi17"]
MPL = 2.435e18
CHI = 0.0755 ** 4

# renormalizable Yukawa vertices: fermion fields (unbarred) and scalar fields with sign (+1 field, -1 conj)
YUKAWAS = {
    "Y10": (["F", "F"], {"H10": 1}), "Y126": (["F", "F"], {"Delta": 1}), "lamF2": (["F", "Vec2"], {"H10": -1}),
    "lam3P": (["Vec3bar", "PhiVbar"], {"H10": 1}), "y1": (["Vec1", "Vec1bar"], {"S": -1}),
    "y2": (["Vec2", "Vec2bar"], {"S": -1}), "y3": (["Vec3", "Vec3bar"], {"S": -1}),
    "yP": (["PhiV", "PhiVbar"], {"Phi17": 1}), "yAB": (["TenA", "TenB"], {"S": -1}),
    "yAM": (["TenA", "SingM"], {"H10": -1}), "yBN": (["TenB", "SingN"], {"H10": 1}), "yNM": (["SingN", "SingM"], {"S": 1}),
}


def rep_of(label):
    base = label.rstrip("^")
    r = REP[base]
    if label.endswith("^") and abs(r) not in SELF:
        r = -r
    return r


def enumerate_candidates(max_fermions=4, dim_max=Fr(8)):
    """Planck operators (dim 5..dim_max) with <= max_fermions fermion fields: X = 0, centre, Lorentz."""
    fields = all_fields(False)
    ferms = [f for f in fields if f[8]]
    cands = []
    for nf in range(0, max_fermions + 1):
        for combo in itertools.combinations_with_replacement(range(len(ferms)), nf):
            fs = [ferms[i] for i in combo]
            nu = sum(1 for f in fs if not f[9])
            nb = sum(1 for f in fs if f[9])
            if (nu + nb) % 2:
                continue
            deriv = 1 if nu % 2 == 1 else 0
            fx = sum(f[1] for f in fs)
            fz = sum(f[2] for f in fs)
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
                        if (fz + 2 * nh + 2 * nd) % 4:
                            continue
                        counts = {}
                        for f in fs:
                            counts[f[0]] = counts.get(f[0], 0) + 1
                        for name, n in (("H10", nh), ("Delta", nd), ("S", ns), ("Phi17", npp)):
                            if n > 0:
                                counts[name] = n
                            elif n < 0:
                                counts[name + "^"] = -n
                        cands.append({"counts": counts, "dim": dim, "derivative": deriv, "nf": nf})
    return cands


def rep_multiset(counts):
    reps = []
    for lab, n in counts.items():
        r = rep_of(lab)
        if r != 1:
            reps += [r] * n
    return tuple(sorted(reps))


def verify_with_susyno(multisets):
    inp = HERE / "susyno" / "cand_in.txt"
    outp = HERE / "susyno" / "cand_out.txt"
    lines = ["m%d %s" % (i, " ".join(str(r) for r in ms) if ms else "1") for i, ms in enumerate(multisets)]
    inp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    subprocess.run([WOLFRAM, "-file", str(SUSYNO_WLS), str(inp), str(outp)], check=True, capture_output=True, timeout=3600)
    res = {}
    for line in outp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        k, v = line.split()
        res[int(k[1:])] = int(v)
    return {ms: res[i] for i, ms in enumerate(multisets)}


def charge_vector(counts):
    """(X, G2, f1, f2, f3, per-species chirality dict, scalar net dict)."""
    x = g2 = f1 = f2 = f3 = 0
    chir = {n: 0 for n in FERMION_NAMES}
    snet = {n: 0 for n in SCALAR_NAMES}
    for lab, n in counts.items():
        base = lab.rstrip("^")
        s = -1 if lab.endswith("^") else 1
        X, _z, G2, F1, F2, F3, _c, ferm = FIELDS[base]
        x += s * n * X
        g2 += s * n * G2
        f1 += s * n * F1
        f2 += s * n * F2
        f3 += s * n * F3
        if ferm:
            chir[base] += s * n
        else:
            snet[base] += s * n
    return x, g2, f1, f2, f3, chir, snet


def closure_ilp(ops, eft_cost=False, g2_target=4, forbid_ops=(), forbid_yuk=(), max_ops=12):
    """Variables: m_j (ops), v_k (Yukawa vertices and conjugates).  Constraints: chirality balance per species,
    net Phi17 = g2_target.  Objective: sum m_j (d_j - 4) [UV] or with Phi17 fields free [EFT]."""
    yuk = []
    for name, (ferms, scal) in YUKAWAS.items():
        yuk.append((name, ferms, scal, +1))
        yuk.append((name + "*", ferms, scal, -1))
    nop, ny = len(ops), len(yuk)
    cost = []
    for op in ops:
        d = op["dim"]
        if eft_cost:
            d -= op["counts"].get("Phi17", 0) + op["counts"].get("Phi17^", 0)
        cost.append(float(d - 4))
    c = np.array([x + 1e-3 for x in cost] + [1e-3] * ny)
    rows, lbs, ubs = [], [], []
    for sp in FERMION_NAMES:
        row = [op["chir"][sp] for op in ops] + [s * ferms.count(sp) for _n, ferms, _sc, s in yuk]
        rows.append(row)
        lbs.append(0)
        ubs.append(0)
    # net Phi17 (vev monomial G2) = target
    row = [op["snet"]["Phi17"] for op in ops] + [s * scal.get("Phi17", 0) for _n, _f, scal, s in yuk]
    rows.append(row)
    lbs.append(g2_target)
    ubs.append(g2_target)
    # at least one Planck operator
    rows.append([1] * nop + [0] * ny)
    lbs.append(1)
    ubs.append(max_ops)
    ub = np.full(nop + ny, 12.0)
    for j, op in enumerate(ops):
        if j in forbid_ops:
            ub[j] = 0
    for k, (name, *_r) in enumerate(yuk):
        if name in forbid_yuk:
            ub[nop + k] = 0
    res = milp(c, constraints=LinearConstraint(np.array(rows, dtype=float), lbs, ubs), integrality=np.ones(nop + ny),
               bounds=Bounds(np.zeros(nop + ny), ub))
    if not res.success:
        return None
    m = {j: int(round(res.x[j])) for j in range(nop) if round(res.x[j]) > 0}
    v = {yuk[k][0]: int(round(res.x[nop + k])) for k in range(ny) if round(res.x[nop + k]) > 0}
    return {"K": float(round(res.fun)), "ops": m, "yukawas": v}


def describe(sol, ops):
    """Vev monomial, Planck power, loop count and an NDA-style estimate of dtheta."""
    yuk_def = {}
    for name, (ferms, scal) in YUKAWAS.items():
        yuk_def[name] = (ferms, scal, 1)
        yuk_def[name + "*"] = (ferms, scal, -1)
    snet = {n: 0 for n in SCALAR_NAMES}
    nferm = 0
    K_uv = 0
    nvert = 0
    op_list = []
    for j, m in sol["ops"].items():
        op = ops[j]
        op_list.append("%d x [%s] (dim %s)" % (m, label(op["counts"]), op["dim"]))
        for n in SCALAR_NAMES:
            snet[n] += m * op["snet"][n]
        nferm += m * op["nf"]
        K_uv += m * (op["dim"] - 4)
        nvert += m
    for name, m in sol["yukawas"].items():
        ferms, scal, s = yuk_def[name]
        for n, q in scal.items():
            snet[n] += m * s * q
        nferm += 2 * m
        nvert += m
    # scalar handling: S, Phi17, Delta net counts are vevs (|net| vevs); H10 must be internal lines (pairs) or EW vevs
    n_h = snet["H10"]
    vev_dim = abs(snet["S"]) + abs(snet["Phi17"]) + abs(snet["Delta"])
    h_internal = abs(n_h) // 2 * 2
    h_ew = abs(n_h) - h_internal
    # extra scalar vertices to pair H10 lines: kappa H H S (or conj) each absorbs two H10 of the same sign
    n_kappa = h_internal // 2
    vev_dim += n_kappa  # each kappa vertex brings one S vev ... and a dimensionful kappa (counted in couplings)
    nvert += n_kappa
    props = nferm // 2 + h_internal  # fermion propagators + H10 internal lines (Delta/S/Phi17 as vevs)
    loops = props - nvert + 1
    D = 4 + int(K_uv) - vev_dim - h_ew - n_kappa  # dimension supplied by loop integrals (kappa has dim 1)
    return {"planck_operators": op_list, "yukawa_vertices": sol["yukawas"], "K_uv": int(K_uv),
            "vev_monomial": {k: v for k, v in snet.items() if v}, "H10_internal_lines": h_internal, "H10_EW_vevs": h_ew,
            "kappa_vertices": n_kappa, "fermion_fields": nferm, "loops": loops, "loop_integral_dimension_D": D}


def estimate(desc, m_s=1.0e13, sigma=3.3e13, phi=1.0e17, v_r=2.6e13, y=0.35, lam=1.0, Y=0.5, kappa=5.0e12, v_ew=174.0):
    """V ~ (16 pi^2)^-L * couplings * kappa^n * vevs * M_loop^D / M_Pl^K; D<0: M_loop = m_s (lightest heavy line),
    D>0: M_loop = M_Pl (UV dominated).  Returns dtheta = V/chi and the ratio to the declared dim-21 estimate."""
    L = desc["loops"]
    lg = -L * math.log10(16 * math.pi ** 2)
    for name, m in desc["yukawa_vertices"].items():
        base = name.rstrip("*")
        if base in ("y1", "y2", "y3", "yAB", "yNM", "yP"):
            lg += m * math.log10(y)
        elif base in ("lamF2", "lam3P", "yAM", "yBN"):
            lg += m * math.log10(lam)
        else:
            lg += m * math.log10(Y)
    vm = desc["vev_monomial"]
    lg += abs(vm.get("S", 0)) * math.log10(sigma) + abs(vm.get("Phi17", 0)) * math.log10(phi)
    lg += abs(vm.get("Delta", 0)) * math.log10(v_r) + desc["H10_EW_vevs"] * math.log10(v_ew)
    lg += desc["kappa_vertices"] * (math.log10(sigma) + math.log10(kappa))
    D = desc["loop_integral_dimension_D"]
    mloop = m_s if D < 0 else MPL
    lg += D * math.log10(mloop) - desc["K_uv"] * math.log10(MPL)
    lg_tree = math.log10(2) + 4 * math.log10(phi) + 17 * math.log10(sigma) - 17 * math.log10(MPL)
    return {"log10_V_GeV4": lg, "log10_dtheta": lg - math.log10(CHI), "dtheta": 10 ** (lg - math.log10(CHI)) if lg - math.log10(CHI) < 300 else "huge",
            "log10_ratio_to_declared_tree_operator": lg - lg_tree, "M_loop": mloop,
            "assumptions": {"y": y, "lam(H10-type Yukawas)": lam, "Y10/126": Y, "kappa_GeV": kappa, "<S>": sigma, "<Phi17>": phi, "v_R": v_r, "m_s": m_s}}


def label(counts):
    return " ".join("%s^%d" % (k, v) if v > 1 else k for k, v in counts.items())


def main() -> int:
    dim_max = Fr(int(sys.argv[1])) if len(sys.argv) > 1 else Fr(8)
    cands = enumerate_candidates(max_fermions=4, dim_max=dim_max)
    multisets = sorted({rep_multiset(c["counts"]) for c in cands})
    print("candidates:", len(cands), "distinct rep multisets:", len(multisets), flush=True)
    singlets = verify_with_susyno(multisets)
    ops = []
    for c in cands:
        ms = rep_multiset(c["counts"])
        if singlets[ms] <= 0:
            continue
        x, g2, f1, f2, f3, chir, snet = charge_vector(c["counts"])
        assert x == 0
        c.update({"G2": g2, "f": (f1, f2, f3), "chir": chir, "snet": snet, "singlets": singlets[ms]})
        ops.append(c)
    print("verified SO(10)-singlet Planck operators (dim<=%s, <=4 fermions):" % dim_max, len(ops), flush=True)
    by_dim = {}
    for op in ops:
        by_dim.setdefault(str(op["dim"]), []).append(label(op["counts"]))
    results = {"dim_max": str(dim_max), "n_candidates_centre_only": len(cands), "n_verified": len(ops),
               "verified_by_dimension_count": {k: len(v) for k, v in by_dim.items()},
               "verified_dim5_dim6": {k: v for k, v in by_dim.items() if Fr(k) <= 6},
               "rejected_examples": [label(c["counts"]) for c in cands if singlets[rep_multiset(c["counts"])] == 0][:20]}
    # optimal vacuum diagrams (minimal Planck power, then minimal number of vertices)
    phiv_ops = [j for j, op in enumerate(ops) if any(k.rstrip("^") in ("PhiV", "PhiVbar") for k in op["counts"])]
    h10_yuk = ("lamF2", "lamF2*", "lam3P", "lam3P*", "yAM", "yAM*", "yBN", "yBN*")
    variants = {
        "A_UV_all": dict(eft_cost=False),
        "B_UV_no_PhiSector_lines": dict(eft_cost=False, forbid_ops=phiv_ops, forbid_yuk=("yP", "yP*", "lam3P", "lam3P*")),
        "C_UV_no_PhiSector_lines_lamF2=0": dict(eft_cost=False, forbid_ops=phiv_ops, forbid_yuk=("yP", "yP*", "lam3P", "lam3P*", "lamF2", "lamF2*")),
        "D_UV_no_H10type_Yukawas": dict(eft_cost=False, forbid_yuk=h10_yuk),
        "E_UV_no_PhiSector_no_H10type_Yukawas": dict(eft_cost=False, forbid_ops=phiv_ops, forbid_yuk=h10_yuk + ("yP", "yP*")),
        "F_EFT_manuscript_P_all": dict(eft_cost=True),
        "G_EFT_manuscript_P_no_PhiSector": dict(eft_cost=True, forbid_ops=phiv_ops, forbid_yuk=("yP", "yP*", "lam3P", "lam3P*")),
    }
    sols = {}
    for tag, kw in variants.items():
        best = None
        for g2 in (4, -4):
            r = closure_ilp(ops, g2_target=g2, **kw)
            if r and (best is None or r["K"] < best["K"]):
                best = r
        if best is None:
            sols[tag] = None
            continue
        d = describe(best, ops)
        for lam in (1.0, 0.1, 0.01):
            d["estimate_all_lines_at_Ms_lam=%g" % lam] = estimate(d, lam=lam)
        sols[tag] = {"K_or_P": best["K"], **d}
    results["vacuum_diagrams"] = sols
    results["scan_forbidding_low_dimension_operators"] = None
    (HERE / "k0_vacuum_diagram.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k not in ("verified_dim5_dim6",)}, indent=1, default=str))
    print("dim-5/6 verified operators:", json.dumps(results["verified_dim5_dim6"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
