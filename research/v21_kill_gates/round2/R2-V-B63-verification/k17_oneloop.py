"""R2-V continuation (2026-10-17): how many K = 17 ONE-LOOP closures exist, and can their sum spoil
'dtheta ~ dtheta_tree up to O(1)'?

EXACT characterisation used: K = sum_i (d_i - 4) >= sum_i mu.q_i = mu.(4,0,0,0,0,0) = 17 (round-1 mu, verified in
dual_dp.py).  Equality K = 17 holds iff EVERY operator in the closure is mu-tight (d_i - 4 = mu.q_i).  So all K = 17
closures are built from tight operators only.  Pure-scalar tight operators: q = (p,0..0), X = 0 and the centre lemma force
p = 0 mod 4, hence p = 4 and d >= 21: only the tree operator S*^17 Phi17^4 itself.  Every other K = 17 closure is made of
fermion-containing tight operators.  One-loop closures are rings O_1 ... O_n of TWO-fermion tight operators joined by
fermion lines.

Here:
 (a) enumerate all tight two-fermion operators psi_u psi_v x (scalar monomial), d in [5, 20], with the necessary
     conditions X = 0, centre, Lorentz (one derivative if u, v have opposite chirality) AND an exact SO(10) singlet check
     (so10_chars.py; identical scalars and identical one-generation fermions use symmetric powers);
 (b) build the high-scale mass graph from the 12 renormalizable Yukawas (EW-vev edges F.F.H10 and Vb2.Vb3.H10 excluded,
     F.F.Delta kept: <Delta> = v_R);
 (c) count rings of n = 2 and n = 3 tight operators with sum q = (4,0,0,0,0,0) whose consecutive fermions are joined by
     a mass-graph path of the right chirality parity (u, v same chirality: odd path; opposite: even, 0 allowed if
     v = conj(u));
 (d) NDA: each ring ~ prod(c_i) * prod(y) / (16 pi^2) * L, L = ln(M_Pl^2/M_s^2) for a log-divergent ring.
Writes k17_oneloop.json.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from collections import Counter, deque
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import so10_chars as so  # noqa: E402

FERM = [("F", 16, 1, 3), ("V1", 16, -35, 2), ("Vb1", -16, 39, 1), ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
        ("V3", 16, 34, 1), ("Vb3", -16, -30, 1), ("T", 10, 2, 2), ("Pb", -16, 18, 1), ("N1", 1, -63, 1),
        ("N1b", 1, 59, 1), ("N2", 1, -58, 1), ("N2b", 1, 54, 1), ("N3", 1, -57, 1), ("N3b", 1, 61, 1),
        ("NMm", 1, -2, 2)]
GENS = {n: g for n, r, x, g in FERM}
REP = {n: r for n, r, x, g in FERM}
XCH = {n: x for n, r, x, g in FERM}
ZC = {16: 1, -16: 3, 10: 2, 1: 0}
Q = {"F": (0, 0, 0, 0, 0, 0), "V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0),
     "Vb2": (0, 0, -1, 0, 0, 0), "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "T": (0,) * 6,
     "Pb": (0, -1, 0, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0), "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0),
     "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1), "N3b": (0, 0, 0, 0, 0, -1), "NMm": (0,) * 6}
MU = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))
TARGET = (4, 0, 0, 0, 0, 0)
MPL, MS = 2.435e18, 1.0e13

# fermion items: (species, conj)  conj=True means psi^dagger (dotted)
ITEMS = [(n, c) for n, *_ in FERM for c in (False, True)]


def it_label(it):
    return it[0] + ("^" if it[1] else "")


def it_X(it):
    return -XCH[it[0]] if it[1] else XCH[it[0]]


def it_z(it):
    return (-ZC[REP[it[0]]]) % 4 if it[1] else ZC[REP[it[0]]] % 4


def it_q(it):
    s = -1 if it[1] else 1
    return tuple(s * c for c in Q[it[0]])


def it_rep(it):
    r = REP[it[0]]
    return so.conj_code(r) if it[1] else r


# ---- symmetric powers via Adams operations ------------------------------------------------------------------
def adams(ch, k):
    return Counter({tuple(k * a for a in w): m for w, m in ch.items()})


def cdiv(ch, n):
    out = Counter()
    for w, m in ch.items():
        assert m % n == 0, "non-integral symmetric power"
        if m:
            out[w] = m // n
    return out


def cadd(*terms):
    out = Counter()
    for coef, ch in terms:
        for w, m in ch.items():
            out[w] += coef * m
    return out


def sympow(ch, n):
    if n == 1:
        return ch
    if n == 2:
        return cdiv(cadd((1, so.product(ch, ch)), (1, adams(ch, 2))), 2)
    if n == 3:
        return cdiv(cadd((1, so.product(ch, ch, ch)), (3, so.product(adams(ch, 2), ch)), (2, adams(ch, 3))), 6)
    raise ValueError(n)


def singlet_exists(fitems, scal_counts):
    """fitems: two fermion items; scal_counts: {signed rep code: multiplicity} of the non-singlet scalars."""
    chars = []
    a, b = fitems
    if a == b and GENS[a[0]] == 1:
        chars.append(sympow(so.CHAR[it_rep(a)], 2))
    else:
        chars += [so.CHAR[it_rep(a)], so.CHAR[it_rep(b)]]
    for code, m in scal_counts.items():
        if m:
            chars.append(sympow(so.CHAR[code], m))
    return so.n_singlets(so.product(*chars)) > 0


def mudot(q):
    return sum(m * c for m, c in zip(MU, q))


# ---- (a) tight two-fermion operators ---------------------------------------------------------------------------
def tight_two_fermion_ops(dmax=20):
    ops = []
    checked = 0
    for i, j in itertools.combinations_with_replacement(range(len(ITEMS)), 2):
        a, b = ITEMS[i], ITEMS[j]
        der = 1 if a[1] != b[1] else 0
        qf = tuple(x + y for x, y in zip(it_q(a), it_q(b)))
        if any(qf[1:]) and False:
            pass
        Xf = it_X(a) + it_X(b)
        zf = it_z(a) + it_z(b)
        for p in range(-8, 9):
            q = (qf[0] + p,) + qf[1:]
            target_d = 4 + mudot(q)
            if target_d.denominator != 1 or target_d < 5 or target_d > dmax:
                continue
            # scalar completion: H10 (X-2), H10^ (+2), Delta (-2), Delta^ (+2) counts, S net s
            for hp, hm, dp, dm in itertools.product(range(4), repeat=4):
                nhd = hp + hm + dp + dm
                if nhd > 3:
                    continue
                if (zf + 2 * nhd) % 4:
                    continue
                rest = Xf + 17 * p - 2 * hp + 2 * hm - 2 * dp + 2 * dm
                if rest % 4:
                    continue
                s = -rest // 4
                d = 3 + der + abs(p) + abs(s) + nhd
                checked += 1
                if d != target_d:
                    continue
                scal = {10: hp + hm, -126: dp, 126: dm}
                # H10 and H10^ both are the 10 (real rep); identical-boson symmetry only for same field
                sc_chars = Counter()
                if hp:
                    sc_chars[("H10", 10)] = hp
                if hm:
                    sc_chars[("H10^", 10)] = hm
                if dp:
                    sc_chars[("Delta", -126)] = dp
                if dm:
                    sc_chars[("Delta^", 126)] = dm
                # build character list with symmetric powers per distinct field
                chars_codes = {}
                ok = singlet_exists_fields((a, b), sc_chars)
                if not ok:
                    continue
                ops.append({"f": [it_label(a), it_label(b)], "items": [a, b], "p": p, "s": s,
                            "H10": hp, "H10^": hm, "Delta": dp, "Delta^": dm, "der": der, "d": d,
                            "q": q, "K_cost": d - 4})
    return ops, checked


def singlet_exists_fields(fitems, sc_fields):
    a, b = fitems
    chars = []
    if a == b and GENS[a[0]] == 1:
        chars.append(sympow(so.CHAR[it_rep(a)], 2))
    else:
        chars += [so.CHAR[it_rep(a)], so.CHAR[it_rep(b)]]
    for (name, code), m in sc_fields.items():
        chars.append(sympow(so.CHAR[code], m))
    return so.n_singlets(so.product(*chars)) > 0


def op_name(o):
    parts = list(o["f"])
    if o["p"] > 0:
        parts.append("Phi17^%d" % o["p"] if o["p"] > 1 else "Phi17")
    elif o["p"] < 0:
        parts.append("Phi17*^%d" % -o["p"] if o["p"] < -1 else "Phi17*")
    if o["s"] > 0:
        parts.append("S^%d" % o["s"] if o["s"] > 1 else "S")
    elif o["s"] < 0:
        parts.append("S*^%d" % -o["s"] if o["s"] < -1 else "S*")
    for k in ("H10", "H10^", "Delta", "Delta^"):
        if o[k]:
            parts.append(k + ("^%d" % o[k] if o[k] > 1 else ""))
    if o["der"]:
        parts.append("D")
    return " ".join(parts)


# ---- (b) mass graph ---------------------------------------------------------------------------------------------
YUK = [("F", "F", "Delta", 2.6e13), ("V1", "Vb1", "S*", 3.0e13), ("V1", "Pb", "Phi17", 1.0e17),
       ("V2", "Vb2", "S*", 3.0e13), ("V3", "Vb3", "S*", 3.0e13), ("T", "T", "S*", 3.0e13),
       ("N1", "N1b", "S", 3.0e13), ("N2", "N2b", "S", 3.0e13), ("N3", "N3b", "S*", 3.0e13),
       ("NMm", "NMm", "S", 3.0e13)]
# excluded (EW vev only): F.F.H10, Vb2.Vb3.H10
ADJ = {}
for a, b, phi, v in YUK:
    ADJ.setdefault(a, []).append((b, phi, v))
    if a != b:
        ADJ.setdefault(b, []).append((a, phi, v))


def line_paths(u, v, maxlen=3):
    """fermion line from field u (in one operator) to field v (in the next). Returns list of minimal-length
    insertion sequences (vev labels).  Rule: a line from species A (undotted) through Yukawa phi.A.B ends on B
    (undotted) with external phi*; chirality flips at each insertion.  u, v same chirality -> odd number of
    insertions; opposite chirality -> even (0 allowed iff v is conj(u))."""
    same_chir = (u[1] == v[1])
    if not same_chir and u[0] == v[0]:
        return [[]]
    # BFS over species with parity
    start = u[0]
    out = []
    frontier = [(start, [])]
    for L in range(1, maxlen + 1):
        nxt = []
        for sp, ins in frontier:
            for nb, phi, vv in ADJ.get(sp, []):
                nxt.append((nb, ins + [phi]))
        for sp, ins in nxt:
            if sp == v[0] and ((L % 2 == 1) == same_chir):
                out.append(ins)
        if out:
            return out
        frontier = nxt
    return out


def main():
    ops, checked = tight_two_fermion_ops()
    # dedupe by name
    seen = {}
    for o in ops:
        seen.setdefault(op_name(o), o)
    ops = list(seen.values())
    ops.sort(key=lambda o: (o["d"], op_name(o)))
    print("tight two-fermion operators:", len(ops), "(scalar completions tested %d)" % checked, flush=True)
    by_q = {}
    for o in ops:
        by_q.setdefault(o["q"], []).append(o)
    # rings n = 2
    rings2 = []
    keys = list(by_q)
    for qa in keys:
        qb = tuple(t - x for t, x in zip(TARGET, qa))
        if qb not in by_q or qb < qa:
            continue
        for oa in by_q[qa]:
            for ob in by_q[qb]:
                if qa == qb and op_name(ob) < op_name(oa):
                    continue
                a1, a2 = oa["items"]
                b1, b2 = ob["items"]
                for (x1, y1), (x2, y2) in (((a2, b1), (b2, a1)), ((a2, b2), (b1, a1))):
                    p1 = line_paths(x1, y1)
                    p2 = line_paths(x2, y2)
                    if p1 and p2:
                        rings2.append({"ops": [op_name(oa), op_name(ob)], "d": [oa["d"], ob["d"]],
                                       "K": oa["d"] + ob["d"] - 8, "lines": [p1[0], p2[0]],
                                       "n_insertions": len(p1[0]) + len(p2[0])})
                        break
    print("one-loop rings n=2 (K=17):", len(rings2), flush=True)
    # rings n = 3 (unordered triples up to cyclic order; we count each triple once if SOME cyclic arrangement works)
    rings3 = []
    ops_idx = list(range(len(ops)))
    qs = [o["q"] for o in ops]
    qset = {}
    for k, q in enumerate(qs):
        qset.setdefault(q, []).append(k)
    seen3 = set()
    for i in ops_idx:
        for j in ops_idx:
            if j < i:
                continue
            qk = tuple(t - a - b for t, a, b in zip(TARGET, qs[i], qs[j]))
            for k in qset.get(qk, []):
                if k < j:
                    continue
                key = (i, j, k)
                if key in seen3:
                    continue
                trio = [ops[i], ops[j], ops[k]]
                found = None
                for perm in ((0, 1, 2), (0, 2, 1)):
                    A, B, C = (trio[t] for t in perm)
                    for fa in (0, 1):
                        for fb in (0, 1):
                            for fc in (0, 1):
                                a_in, a_out = A["items"][fa], A["items"][1 - fa]
                                b_in, b_out = B["items"][fb], B["items"][1 - fb]
                                c_in, c_out = C["items"][fc], C["items"][1 - fc]
                                l1 = line_paths(a_out, b_in)
                                l2 = line_paths(b_out, c_in) if l1 else []
                                l3 = line_paths(c_out, a_in) if l2 else []
                                if l1 and l2 and l3:
                                    found = [l1[0], l2[0], l3[0]]
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    seen3.add(key)
                    rings3.append({"ops": [op_name(ops[t]) for t in key], "d": [ops[t]["d"] for t in key],
                                   "K": sum(ops[t]["d"] for t in key) - 12, "lines": found})
    print("one-loop rings n=3 (K=17):", len(rings3), flush=True)
    # NDA
    L = math.log(MPL ** 2 / MS ** 2)
    nda = {}
    for y in (0.304, 0.35, 0.368):
        per2 = y ** 2 / (16 * math.pi ** 2) * L
        per3 = y ** 3 / (16 * math.pi ** 2) * L  # three insertions (one per line), O(1) operator coefficients
        nda["y=%.3f" % y] = {"per_n2_ring": per2, "coherent_sum_n2": len(rings2) * per2,
                             "random_phase_sum_n2": math.sqrt(max(len(rings2), 1)) * per2,
                             "per_n3_ring(y^3, upper)": per3, "coherent_sum_n3": len(rings3) * per3,
                             "random_phase_sum_n3": math.sqrt(max(len(rings3), 1)) * per3}
    for k, v in nda.items():
        print(k, {a: "%.3g" % b for a, b in v.items()})
    hist_d = Counter(o["d"] for o in ops)
    out = {"n_tight_two_fermion_ops": len(ops), "tight_ops_by_dimension": dict(sorted(hist_d.items())),
           "tight_ops": [{"op": op_name(o), "d": o["d"], "q": o["q"]} for o in ops],
           "n_rings_2": len(rings2), "rings_2": rings2, "n_rings_3": len(rings3), "rings_3": rings3[:400],
           "L=ln(MPl^2/Ms^2)": L, "nda_relative_to_tree": nda,
           "notes": "rings counted once per operator set; each needs nonzero high-scale mass paths; K = 17 automatic "
                    "(all operators mu-tight, sum q = (4,0,...)). Operator coefficients O(1) (cost model)."}
    (HERE / "k17_oneloop.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for r in rings2[:60]:
        print("  ring2:", r["ops"], "d", r["d"], "lines", r["lines"])


if __name__ == "__main__":
    main()
