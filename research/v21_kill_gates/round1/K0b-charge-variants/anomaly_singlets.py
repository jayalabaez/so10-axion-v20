"""K0b: exact anomaly bookkeeping and singlet-fermion completion for an F17-type content.

Lemma A (EXACT, proved in REPORT): with 3 x 16_F(1) and every exotic mass from <S> (sum of pair charges +-4) or
<Phi17> (sum +-17), [SO(10)]^2 X = 0 reads  6 + 2 (T_S* - T_S) + (17/2)(T_Phi* - T_Phi) = 0  (T = Dynkin index of
the multiplet pair, T(16)=2, T(10)=1), and the QCD anomaly of the accidental PQ = X - 17 G2 is N = (17/2)(T_Phi - T_Phi*)
= 2 (T_S* - T_S) + 6.  Within T_S* + T_S <= 16 the only solutions are (T_S*, T_S, T_Phi - T_Phi*) = (14, 0, 4) [N = 34]
and (T_S* - T_S = -3, 0) [N = 0: no axion].  (15, 1, 4) requires a Majorana 10(-2) together with an odd number of
Majorana 10(+2): their bare mass 10(2).10(-2) is X-neutral, excluded by the 'every mass from a vev' rule.

This module: given the 16/10 content (charges), solve grav-X = 0 and X^3 = 0 with SO(10)-singlet Weyl fermions whose
masses are renormalizable from <S> (pairs (d, 4-d), (d, -4-d), Majorana +-2) or <Phi17> (pairs (d, +-17-d)).
"""
from __future__ import annotations

import itertools
from fractions import Fraction as Fr

DIM = {1: 1, 10: 10, 16: 16}
T = {1: Fr(0), 10: Fr(1), 16: Fr(2)}


def sums(content):
    a1 = sum(Fr(g) * T[abs(r)] * x for _n, r, x, g in content)
    ag = sum(g * DIM[abs(r)] * x for _n, r, x, g in content)
    a3 = sum(g * DIM[abs(r)] * x ** 3 for _n, r, x, g in content)
    return a1, ag, a3


def pair_cube(s, d):
    return s ** 3 - 3 * s * d * (s - d)


def singlet_completions(content, max_pairs=3, max_maj=2, dbox=60, forbid_charges=(), max_results=50):
    """Return singlet sets [(d, gens)...] (as list of (name, 1, d, 1) rows) fixing grav and X^3.
    Pair types: sums +4, -4, +17, -17; Majorana charges +2, -2.  Excludes d = 0 (bare Majorana mass), pairs with
    d + d' = 0 across the set (bare Dirac mass), and charges in forbid_charges."""
    a1, ag, a3 = sums(content)
    assert a1 == 0, "SO(10)^2 X must vanish before singlets (singlets have T = 0): %s" % a1
    need_sum = -ag
    need_cube = -a3
    results = []
    pair_sums = (4, -4, 17, -17)
    for npairs in range(0, max_pairs + 1):
        for nmaj_p in range(0, max_maj + 1):
            for nmaj_m in range(0, max_maj + 1 - nmaj_p):
                base_sum = 2 * nmaj_p - 2 * nmaj_m
                base_cube = 8 * nmaj_p - 8 * nmaj_m
                for stypes in itertools.combinations_with_replacement(pair_sums, npairs):
                    if base_sum + sum(stypes) != need_sum:
                        continue
                    target = need_cube - base_cube - sum(s ** 3 for s in stypes)  # = -3 sum s_j d_j (s_j - d_j)
                    # enumerate all but the last pair's d, solve the last
                    if npairs == 0:
                        if target == 0:
                            results.append(_rows([], nmaj_p, nmaj_m))
                        continue
                    ranges = [range(-dbox, dbox + 1)] * (npairs - 1)
                    for ds in itertools.product(*ranges):
                        # canonical: d <= s - d for each pair
                        if any(d > s - d for d, s in zip(ds, stypes[:-1])):
                            continue
                        partial = sum(-3 * s * d * (s - d) for d, s in zip(ds, stypes[:-1]))
                        rest = target - partial  # = -3 s_k d (s_k - d)
                        s = stypes[-1]
                        if rest % (3 * s) != 0:
                            continue
                        u = -rest // (3 * s)  # d (s - d) = u -> d^2 - s d + u = 0
                        disc = s * s - 4 * u
                        if disc < 0:
                            continue
                        r = int(round(disc ** 0.5))
                        if r * r != disc or (s + r) % 2:
                            continue
                        for d in {(s - r) // 2, (s + r) // 2}:
                            if d > s - d:
                                continue
                            if abs(d) > dbox or abs(s - d) > dbox:
                                continue
                            allds = list(ds) + [d]
                            # order pairs canonically to avoid duplicates
                            key = tuple(sorted(zip(stypes, allds)))
                            rows = _rows(list(key), nmaj_p, nmaj_m)
                            charges = [x for _n, _r, x, g in rows for _ in range(g)]
                            if 0 in charges or any(x in forbid_charges for x in charges):
                                continue
                            if any(x + y == 0 for x, y in itertools.combinations(charges, 2)):
                                continue
                            if rows not in results:
                                results.append(rows)
                            if len(results) >= max_results:
                                return results
    return results


def _rows(pairs, nmaj_p, nmaj_m):
    rows = []
    k = 0
    for s, d in pairs:
        k += 1
        if 2 * d == s:
            rows.append(("N%d" % k, 1, d, 2))
        else:
            rows.append(("N%d" % k, 1, d, 1))
            rows.append(("N%db" % k, 1, s - d, 1))
    if nmaj_p:
        rows.append(("NMp", 1, 2, nmaj_p))
    if nmaj_m:
        rows.append(("NMm", 1, -2, nmaj_m))
    return rows


def merge_rows(rows):
    """merge identical (rep, X) rows into generations."""
    out = {}
    order = []
    for n, r, x, g in rows:
        key = (r, x)
        if key in out:
            out[key][3] += g
        else:
            out[key] = [n, r, x, g]
            order.append(key)
    return [tuple(out[k]) for k in order]


if __name__ == "__main__":
    # F17 check: singlets must reproduce 2 x [1(-3) + 1(-1)] among the solutions
    core = [("F", 16, 1, 3), ("TenA", 10, -1, 1), ("TenB", 10, 5, 1), ("Vec1", 16, 0, 1), ("Vec1bar", -16, 4, 1),
            ("Vec2", 16, -3, 1), ("Vec2bar", -16, 7, 1), ("Vec3", 16, -6, 1), ("Vec3bar", -16, 10, 1),
            ("PhiV", 16, -9, 1), ("PhiVbar", -16, -8, 1)]
    print(sums(core))
    sols = singlet_completions(core, max_pairs=2, dbox=30)
    for s in sols:
        print(s)
