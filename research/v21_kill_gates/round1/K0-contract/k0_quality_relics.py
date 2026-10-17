"""Gate K0 (3)+(4): exact operator-lattice analysis of the v21-F17 content.

(3) Axion quality.  Every local operator built from the F17 fields that is gauge invariant must satisfy
    the NECESSARY conditions used here (they are what an integer program can check exactly):
      * U(1)_X:  sum X = 0   (UV theory)        or  sum X = 0 mod 17 with free <Phi17> insertions (Z17-EFT);
      * Spin(10) centre Z4 (generator z = i on 16, -i on 16bar, -1 on 10 and 126bar, +1 on 1, 45, 210):
        sum of z-exponents = 0 mod 4  (necessary for an SO(10) singlet);
      * Lorentz: even number of Weyl fermions; (#unbarred, #barred) both even, or both odd with one derivative.
    The PQ-violating effective potential can only come from operators (or products of operators whose
    joint fermion-only charges cancel) that are NOT invariant under any U(1) of the kernel whose scalar
    action equals PQ; for a single operator that means f1 = f2 = f3 = 0 and PQ != 0.
    LEMMA (verified below field by field): X = z + G2 - f1 + 3 f2 + f3 (mod 4) for every field, hence for
    every product.  For an SO(10)-invariant (z = 0), f-neutral operator: X = G2 (mod 4).
      UV:  X = 0 -> G2 = 0 (mod 4); PQ-violating <=> G2 != 0 -> |G2| >= 4 -> >= 4 net Phi17 (or 4 PhiV-type
           fermion) insertions; the integer program finds the minimal dimension and lists the operators.
      EFT: PQ = X - 17 G2 is a multiple of 68 for f-neutral Z17-invariant operators.
    Dimensional analysis then bounds every loop-generated PQ-violating potential term by the tree-level
    minimal operator (only scales: vevs/masses <= <Phi17> and M_Pl).
(4) Relics: minimal-dimension X- and centre-invariant operators that change each fermion-only charge by
    one unit (decay/mixing operators of the Vec1, Vec3/PhiV sectors into the families F), with lifetime
    estimates (EST).  The tensor sector is R-odd (exactly stable lightest state).
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

# field: (X, z-exponent mod 4, G2, f1, f2, f3, dim*2 [half units], is_fermion)
# z: 16 -> 1, 16bar -> 3, 10 -> 2, 126bar -> 2, singlets/210 -> 0.  G2 with the gauge c = a = 0.
FIELDS = {
    "F":       (1, 1, 0, 0, 0, 0, 3, True),
    "TenA":    (-1, 2, 0, 0, 0, 1, 3, True),
    "TenB":    (5, 2, 0, 0, 0, -1, 3, True),
    "Vec1":    (0, 1, 0, 1, 0, 0, 3, True),
    "Vec1bar": (4, 3, 0, -1, 0, 0, 3, True),
    "Vec2":    (-3, 1, 0, 0, 0, 0, 3, True),
    "Vec2bar": (7, 3, 0, 0, 0, 0, 3, True),
    "Vec3":    (-6, 1, 0, 0, -1, 0, 3, True),
    "Vec3bar": (10, 3, 0, 0, 1, 0, 3, True),
    "PhiV":    (-9, 1, -1, 0, 1, 0, 3, True),
    "PhiVbar": (-8, 3, 0, 0, -1, 0, 3, True),
    "SingN":   (-3, 0, 0, 0, 0, 1, 3, True),
    "SingM":   (-1, 0, 0, 0, 0, -1, 3, True),
    "H10":     (-2, 2, 0, 0, 0, 0, 2, False),
    "Delta":   (-2, 2, 0, 0, 0, 0, 2, False),
    "S":       (4, 0, 0, 0, 0, 0, 2, False),
    "Phi17":   (17, 0, 1, 0, 0, 0, 2, False),
}


def all_fields(eft: bool):
    """Return list of (label, X, z, G2, f1, f2, f3, cost_half_units, is_fermion, barred)."""
    out = []
    for name, (x, z, g2, f1, f2, f3, cost, ferm) in FIELDS.items():
        c = 0 if (eft and name == "Phi17") else cost
        out.append((name, x, z, g2, f1, f2, f3, c, ferm, False))
        out.append((name + "^", -x, (-z) % 4, -g2, -f1, -f2, -f3, c, ferm, True))
    return out


def lemma_check():
    """X = z + G2 - f1 + 3 f2 + f3 (mod 4) for every field (and conjugates)."""
    bad = []
    for name, x, z, g2, f1, f2, f3, _c, _f, _b in all_fields(False):
        if (x - (z + g2 - f1 + 3 * f2 + f3)) % 4 != 0:
            bad.append(name)
    return bad


def solve_min(eft: bool, *, g2_target=None, pq_target=None, f_targets=(0, 0, 0), fixed_counts=None,
              allow_f=False, x_mod17=False, max_fermions=None, extra_cost=0, forbid=()):
    """Integer program: minimal dimension operator.  Returns (dim, counts dict) or None.
    Two Lorentz classes are solved and the better one returned."""
    fields = [f for f in all_fields(eft) if f[0] not in forbid]
    n = len(fields)
    best = None
    for parity in (0, 1):  # 0: #unbarred, #barred both even; 1: both odd (+1 derivative)
        cost = np.array([f[7] for f in fields], dtype=float)
        # auxiliary integers: k (z mod 4), a (unbarred pairs), b (barred pairs), m (X/17 if eft mod)
        n_aux = 4
        c = np.concatenate([cost, np.zeros(n_aux)])
        rows, lbs, ubs = [], [], []

        def add(coeffs_fields, aux, lb, ub):
            rows.append(np.concatenate([np.array(coeffs_fields, dtype=float), np.array(aux, dtype=float)]))
            lbs.append(lb)
            ubs.append(ub)

        # X
        if x_mod17:
            add([f[1] for f in fields], [0, 0, 0, -17], 0, 0)
        else:
            add([f[1] for f in fields], [0, 0, 0, 0], 0, 0)
        # centre
        add([f[2] for f in fields], [-4, 0, 0, 0], 0, 0)
        # Lorentz
        add([1 if (f[8] and not f[9]) else 0 for f in fields], [0, -2, 0, 0], parity, parity)
        add([1 if (f[8] and f[9]) else 0 for f in fields], [0, 0, -2, 0], parity, parity)
        # f charges
        if not allow_f:
            for i in range(3):
                add([f[4 + i] for f in fields], [0, 0, 0, 0], f_targets[i], f_targets[i])
        if g2_target is not None:
            add([f[3] for f in fields], [0, 0, 0, 0], g2_target, g2_target)
        if pq_target is not None:
            add([f[1] - 17 * f[3] for f in fields], [0, 0, 0, 0], pq_target, pq_target)
        if fixed_counts:
            for name, val in fixed_counts.items():
                add([1 if f[0] == name else 0 for f in fields], [0, 0, 0, 0], val, val)
        if max_fermions is not None:
            add([1 if f[8] else 0 for f in fields], [0, 0, 0, 0], 0, max_fermions)
        # nonempty
        add([1] * n, [0, 0, 0, 0], 1, 200)
        A = np.vstack(rows)
        lb = np.zeros(n + n_aux)
        ub = np.full(n + n_aux, 60.0)
        lb[n:] = -60
        res = milp(c, constraints=LinearConstraint(A, lbs, ubs), integrality=np.ones(n + n_aux),
                   bounds=Bounds(lb, ub))
        if res.success:
            counts = {fields[i][0]: int(round(res.x[i])) for i in range(n) if round(res.x[i]) > 0}
            dim = Fr(int(round(res.fun)), 2) + parity + extra_cost
            if best is None or dim < best[0]:
                best = (dim, counts, parity)
    return best


def enumerate_two_fermion(eft: bool, *, dim_max: Fr, pq_violating: bool):
    """All primitive operators with <= 2 fermions, f-neutral, X-neutral (UV) and PQ-violating (G2 != 0),
    dimension <= dim_max.  Scalars as signed net counts (no field with its conjugate)."""
    fields = all_fields(eft)
    ferms = [f for f in fields if f[8]]
    sc = {"H10": FIELDS["H10"], "Delta": FIELDS["Delta"], "S": FIELDS["S"], "Phi17": FIELDS["Phi17"]}
    results = []
    combos = [()] + [(a,) for a in range(len(ferms))] + list(itertools.combinations_with_replacement(range(len(ferms)), 2))
    for combo in combos:
        fs = [ferms[i] for i in combo]
        nu = sum(1 for f in fs if not f[9])
        nb = sum(1 for f in fs if f[9])
        if (nu + nb) % 2:
            continue
        deriv = 1 if (nu % 2 == 1) else 0
        fx = sum(f[1] for f in fs)
        fz = sum(f[2] for f in fs)
        fg = sum(f[3] for f in fs)
        if any(sum(f[4 + i] for f in fs) != 0 for i in range(3)):
            continue
        fcost = sum(f[7] for f in fs) / 2 + deriv
        budget = float(dim_max) - fcost
        if budget < 0:
            continue
        R = int(budget) + 1
        for nh in range(-R, R + 1):
            for nd in range(-R, R + 1):
                for np_ in range(-R, R + 1):
                    cost_hdp = abs(nh) + abs(nd) + (0 if eft else abs(np_))
                    if cost_hdp > budget:
                        continue
                    xs = fx - 2 * nh - 2 * nd + 17 * np_
                    if xs % 4:
                        continue
                    ns = -xs // 4
                    if cost_hdp + abs(ns) > budget:
                        continue
                    if (fz + 2 * nh + 2 * nd) % 4:
                        continue
                    g2 = fg + np_
                    if pq_violating and g2 == 0:
                        continue
                    dim = Fr(cost_hdp + abs(ns)) + Fr(fcost)
                    results.append({
                        "fermions": [f[0] for f in fs], "H10": nh, "Delta": nd, "S": ns, "Phi17": np_,
                        "G2": g2, "PQ": 0 - 17 * g2 if not eft else None, "dimension": str(dim), "derivative": deriv,
                    })
    results.sort(key=lambda r: Fr(r["dimension"]))
    return results


def label(counts):
    return " ".join("%s^%d" % (k, v) if v > 1 else k for k, v in counts.items())


def main() -> int:
    out = {"lemma_violations": lemma_check()}
    # ---------------- (3a) UV convention: minimal PQ-violating f-neutral operators -------------------------
    uv = {}
    for g2 in (4, -4, 8, -8):
        r = solve_min(False, g2_target=g2)
        uv["G2=%+d" % g2] = {"dimension": str(r[0]), "operator": label(r[1])} if r else None
    r_scalar = solve_min(False, g2_target=4, max_fermions=0)
    r_ferm2 = solve_min(False, g2_target=4, fixed_counts=None, max_fermions=2, forbid=())
    # force at least one fermion: run with each fermion count >= ... simpler: enumerate 2-fermion list below
    uv["pure_scalar_min"] = {"dimension": str(r_scalar[0]), "operator": label(r_scalar[1])}
    two = enumerate_two_fermion(False, dim_max=Fr(23), pq_violating=True)
    uv["all_primitive_PQ_violating_f_neutral_operators_with_<=2_fermions_dim<=23"] = two
    uv["min_dim_with_fermions"] = str(min((Fr(r["dimension"]) for r in two if r["fermions"]), default=None))
    # 4-fermion minimum (ILP with exactly 4 fermions)
    r4 = None
    for g2 in (4, -4):
        fields4 = solve_min(False, g2_target=g2, max_fermions=4)
        # require >= 4 fermions via a second constraint: emulate by forbidding scalars-only solutions:
        # run ILP with fixed total fermion count = 4
    out["UV_X_invariant"] = uv
    # explicit 4-fermion ILP
    fields = all_fields(False)
    r4 = None
    for g2 in (4, -4):
        res = solve_min_fixed_fermion_count(False, g2, 4)
        if res and (r4 is None or res[0] < r4[0]):
            r4 = res
    out["UV_X_invariant"]["min_with_exactly_4_fermions"] = {"dimension": str(r4[0]), "operator": label(r4[1])} if r4 else None
    r6 = None
    for g2 in (4, -4):
        res = solve_min_fixed_fermion_count(False, g2, 6)
        if res and (r6 is None or res[0] < r6[0]):
            r6 = res
    out["UV_X_invariant"]["min_with_exactly_6_fermions"] = {"dimension": str(r6[0]), "operator": label(r6[1])} if r6 else None
    # ---------------- (3b) Z17-EFT convention (free <Phi17> insertions) --------------------------------------
    eft = {}
    for pq in (68, -68):
        r = solve_min(True, pq_target=pq)
        eft["PQ=%+d" % pq] = {"dimension": str(r[0]), "operator": label(r[1])} if r else None
    r = solve_min(True, pq_target=68, max_fermions=0)
    eft["pure_scalar_min"] = {"dimension": str(r[0]), "operator": label(r[1])}
    r2 = min((solve_min_fixed_fermion_count(True, None, 2, pq_target=pq) for pq in (68, -68)), key=lambda t: t[0] if t else Fr(999))
    eft["min_with_exactly_2_fermions"] = {"dimension": str(r2[0]), "operator": label(r2[1])} if r2 else None
    r4e = min((solve_min_fixed_fermion_count(True, None, 4, pq_target=pq) for pq in (68, -68)), key=lambda t: t[0] if t else Fr(999))
    eft["min_with_exactly_4_fermions"] = {"dimension": str(r4e[0]), "operator": label(r4e[1])} if r4e else None
    # single-operator lower bound on |PQ| for f-neutral Z17 operators: try PQ = 17, 34, 51 -> expect infeasible
    for pq in (17, 34, 51):
        r = solve_min(True, pq_target=pq)
        eft["f_neutral_with_PQ=%d" % pq] = {"dimension": str(r[0]), "operator": label(r[1])} if r else "infeasible (as the lemma requires)"
    out["Z17_EFT_free_Phi17_insertions"] = eft
    # ---------------- (3c) NDA multi-operator products (manuscript P-counting) ----------------------------------
    # cost table c(PQ, f1, f2, f3) = min over single Z17-invariant operators of (dim - 4) [half units]
    table = {}
    for pq in range(-68, 69, 17):
        for f1 in range(-2, 3):
            for f2 in range(-2, 3):
                for f3 in range(-2, 3):
                    if pq == 0 and f1 == 0 and f2 == 0 and f3 == 0:
                        continue
                    r = solve_min(True, pq_target=pq, f_targets=(f1, f2, f3))
                    if r and r[0] >= 5:
                        table[(pq, f1, f2, f3)] = (r[0] - 4, label(r[1]))
    keys = list(table.keys())
    cvec = np.array([float(table[k][0]) for k in keys])
    A = np.array([[k[0] for k in keys], [k[1] for k in keys], [k[2] for k in keys], [k[3] for k in keys]], dtype=float)
    best_nda = None
    for total in (68, -68):
        res = milp(cvec, constraints=LinearConstraint(A, [total, 0, 0, 0], [total, 0, 0, 0]),
                   integrality=np.ones(len(keys)), bounds=Bounds(np.zeros(len(keys)), np.full(len(keys), 8)))
        if res.success and (best_nda is None or res.fun < best_nda[0]):
            chosen = [(keys[i], int(round(res.x[i])), table[keys[i]]) for i in range(len(keys)) if round(res.x[i]) > 0]
            best_nda = (res.fun, chosen)
    out["NDA_multi_operator_Z17_EFT"] = {
        "P_min_sum_(d_i-4)": best_nda[0] if best_nda else None,
        "factors": [{"charges(PQ,f1,f2,f3)": list(k), "multiplicity": m, "dim-4": str(t[0]), "operator": t[1]} for k, m, t in best_nda[1]] if best_nda else None,
        "cost_table_size": len(table),
        "manuscript_v20_value_for_comparison": "P = 12 (eq. qualitybound, v20 fermion content)",
    }
    # ---------------- (4) decay operators of the f-charged exotics --------------------------------------------
    decays = {}
    for sector, fermions_allowed, fvec in (
        ("f1 (Vec1 pair)", ("Vec1", "Vec1bar"), (1, 0, 0)),
        ("f2 (Vec3 pair, PhiV pair)", ("Vec3", "Vec3bar", "PhiV", "PhiVbar"), (0, 1, 0)),
        ("f3 (TenA, TenB, SingN, SingM; R-odd)", ("TenA", "TenB", "SingN", "SingM"), (0, 0, 1)),
    ):
        forbid = [n for n in FIELDS if FIELDS[n][7] and n != "F" and n not in fermions_allowed]
        forbid += [n + "^" for n in forbid]
        rows = {}
        for ft in (fvec, tuple(-v for v in fvec)):
            r_mix = solve_min(False, f_targets=ft, forbid=forbid, max_fermions=2)
            r_four = solve_min_fixed_fermion_count(False, None, 4, f_targets=ft, forbid=forbid)
            rows["f=%s" % (ft,)] = {
                "min_2_fermion_operator": {"dimension": str(r_mix[0]), "operator": label(r_mix[1])} if r_mix else None,
                "min_4_fermion_operator": {"dimension": str(r_four[0]), "operator": label(r_four[1])} if r_four else None,
            }
        decays[sector] = rows
    # also the renormalizable / low-dim mixing of the f-neutral Vec2 pair and the two-fermion list per exotic
    per_exotic = {}
    for name in ("Vec1", "Vec1bar", "Vec2", "Vec2bar", "Vec3", "Vec3bar", "PhiV", "PhiVbar", "TenA", "TenB", "SingN", "SingM"):
        forbid = [n for n in FIELDS if FIELDS[n][7] and n not in ("F", name)]
        forbid += [n + "^" for n in forbid]
        r = solve_min(False, allow_f=True, forbid=forbid, fixed_counts={name: 1}, max_fermions=2)
        per_exotic[name] = {"min_operator_with_one_%s_and_F_only" % name: {"dimension": str(r[0]), "operator": label(r[1])} if r else None}
    out["decay_operators"] = {"by_fermion_number_sector": decays, "per_exotic_two_fermion_with_F": per_exotic}
    (HERE / "k0_quality_relics.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "UV_X_invariant"}, indent=1, default=str))
    uvp = dict(out["UV_X_invariant"])
    lst = uvp.pop("all_primitive_PQ_violating_f_neutral_operators_with_<=2_fermions_dim<=23")
    print(json.dumps(uvp, indent=1, default=str))
    print("two-fermion/scalar PQ-violating list (dim <= 23):", len(lst))
    for r in lst[:40]:
        print("  ", r)
    return 0


def solve_min_fixed_fermion_count(eft, g2_target, nf, pq_target=None, f_targets=(0, 0, 0), forbid=()):
    """Minimal operator with exactly nf fermion fields."""
    fields = [f for f in all_fields(eft) if f[0] not in forbid]
    n = len(fields)
    best = None
    for parity in (0, 1):
        cost = np.array([f[7] for f in fields], dtype=float)
        c = np.concatenate([cost, np.zeros(3)])
        rows, lbs, ubs = [], [], []

        def add(cf, aux, lb, ub):
            rows.append(np.concatenate([np.array(cf, dtype=float), np.array(aux, dtype=float)]))
            lbs.append(lb)
            ubs.append(ub)

        add([f[1] for f in fields], [0, 0, 0], 0, 0)
        add([f[2] for f in fields], [-4, 0, 0], 0, 0)
        add([1 if (f[8] and not f[9]) else 0 for f in fields], [0, -2, 0], parity, parity)
        add([1 if (f[8] and f[9]) else 0 for f in fields], [0, 0, -2], parity, parity)
        for i in range(3):
            add([f[4 + i] for f in fields], [0, 0, 0], f_targets[i], f_targets[i])
        if g2_target is not None:
            add([f[3] for f in fields], [0, 0, 0], g2_target, g2_target)
        if pq_target is not None:
            add([f[1] - 17 * f[3] for f in fields], [0, 0, 0], pq_target, pq_target)
        add([1 if f[8] else 0 for f in fields], [0, 0, 0], nf, nf)
        A = np.vstack(rows)
        lb = np.zeros(n + 3)
        ub = np.full(n + 3, 60.0)
        lb[n:] = -60
        res = milp(c, constraints=LinearConstraint(A, lbs, ubs), integrality=np.ones(n + 3), bounds=Bounds(lb, ub))
        if res.success:
            counts = {fields[i][0]: int(round(res.x[i])) for i in range(n) if round(res.x[i]) > 0}
            dim = Fr(int(round(res.fun)), 2) + parity
            if best is None or dim < best[0]:
                best = (dim, counts, parity)
    return best


if __name__ == "__main__":
    sys.exit(main())
