#!/usr/bin/env python3
"""Stage-2a "model": EXACT census of renormalizable SO(10) x U(1)_X x Lorentz scalar invariants (method (a)).

Uses only the own Weyl-character engine so10_weyl_chars.py (exact integers).  For every multidegree (exponent vector
of the bosonic fields P = Phi210 (real), A = 45_H (real), H, Hb = H10, H10^dag, D, Db = Delta126bar, Delta126bar^dag,
S, Sb, T, Tb = Phi17, Phi17^dag) with total degree 1..4 and X = 0, the number of independent invariants is
    n = mult(1 in  Sym^{k_P}(210) x Sym^{k_A}(45) x Sym^{k_H}(10) x Sym^{k_Hb}(10) x Sym^{k_D}(126bar) x Sym^{k_Db}(126))
(scalar bosons commute; the singlets S, T only carry X).  Hermitian-conjugate multidegrees are grouped into orbits:
a self-conjugate orbit gives n real couplings, a conjugate pair gives n complex couplings (2n real parameters).

Checks: (1) the v20 field set must reproduce the attested v20 contract EXACTLY: 34 multidegrees, 28 conjugacy
orbits, 44 invariant directions, 51 real parameters (GAUGED_U1X_SCALAR_CONTRACT_V20.json); per-orbit counts are
compared with the v20 direction list.  (2) the v22 set = v20 + real 45 (X = 0): every new multidegree is listed.
Also: fermion bilinear catalogue (B63 fermions x {no scalar, every scalar and conjugate}) -> the 12 Yukawa
structures, no bare mass, no 45_H Yukawa.  Output: census_v22.json (+ stdout log).
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import so10_weyl_chars as W  # noqa: E402

# field: (SO(10) rep name, X, conjugate field name, real?)
FIELDS_V20 = {
    "P": ("210", 0, "P", True),
    "H": ("10", -2, "Hb", False), "Hb": ("10", 2, "H", False),
    "D": ("126bar", -2, "Db", False), "Db": ("126", 2, "D", False),
    "S": ("1", 4, "Sb", False), "Sb": ("1", -4, "S", False),
    "T": ("1", 17, "Tb", False), "Tb": ("1", -17, "T", False),
}
FIELDS_V22 = dict(FIELDS_V20)
FIELDS_V22["A"] = ("45", 0, "A", True)
PRETTY = {"P": "Phi210", "A": "A45", "H": "H10", "Hb": "H10^dag", "D": "Delta126bar", "Db": "Delta126bar^dag",
          "S": "S", "Sb": "S^dag", "T": "Phi17", "Tb": "Phi17^dag"}

# v20 attested per-orbit counts (direction ids -> representative multidegree), from GAUGED_U1X_SCALAR_CONTRACT_V20.json
V20_ORBITS = {
    "O03": ({"T": 1, "Tb": 1}, 1), "O04": ({"S": 1, "Sb": 1}, 1), "O05": ({"D": 1, "Db": 1}, 1),
    "O06": ({"H": 1, "Hb": 1}, 1), "O07": ({"P": 2}, 1), "O12": ({"Hb": 2, "Sb": 1}, 1),
    "O14": ({"P": 1, "D": 1, "Db": 1}, 1), "O15": ({"P": 1, "Hb": 1, "D": 1}, 1), "O17": ({"P": 3}, 1),
    "O20": ({"T": 2, "Tb": 2}, 1), "O22": ({"S": 1, "Sb": 1, "T": 1, "Tb": 1}, 1), "O23": ({"S": 2, "Sb": 2}, 1),
    "O25": ({"D": 1, "Db": 1, "T": 1, "Tb": 1}, 1), "O26": ({"D": 1, "Db": 1, "S": 1, "Sb": 1}, 1),
    "O27": ({"D": 2, "Db": 2}, 4), "O28": ({"Hb": 1, "D": 2, "Db": 1}, 1), "O31": ({"Hb": 2, "D": 2}, 1),
    "O33": ({"H": 1, "Hb": 1, "T": 1, "Tb": 1}, 1), "O34": ({"H": 1, "Hb": 1, "S": 1, "Sb": 1}, 1),
    "O35": ({"H": 1, "Hb": 1, "D": 1, "Db": 1}, 2), "O36": ({"H": 2, "Hb": 2}, 2),
    "O38": ({"P": 1, "Hb": 1, "Db": 1, "Sb": 1}, 1), "O42": ({"P": 2, "T": 1, "Tb": 1}, 1),
    "O43": ({"P": 2, "S": 1, "Sb": 1}, 1), "O44": ({"P": 2, "D": 1, "Db": 1}, 6), "O45": ({"P": 2, "Hb": 1, "D": 1}, 2),
    "O46": ({"P": 2, "H": 1, "Hb": 1}, 3), "O48": ({"P": 4}, 4),
}


def key_of(md):
    return tuple(sorted((k, v) for k, v in md.items() if v))


def conj_md(md, fields):
    out = {}
    for k, v in md.items():
        if v:
            c = fields[k][2]
            out[c] = out.get(c, 0) + v
    return out


_char_cache = {}


def field_power_char(rep, n):
    if rep == "1" or n == 0:
        return W.trivial()
    key = (rep, n)
    if key not in _char_cache:
        _char_cache[key] = W.sym_power(W.REPS[rep](), n)
    return _char_cache[key]


def count_invariants(md, fields):
    ch = W.trivial()
    # multiply smallest first
    parts = []
    for f, n in md.items():
        if n:
            rep = fields[f][0]
            if rep != "1":
                parts.append(field_power_char(rep, n))
    parts.sort(key=lambda c: len(c.M))
    for c in parts:
        ch = ch * c
    return W.n_singlets(ch)


def enumerate_multidegrees(fields, dmax=4, must_contain=None):
    names = list(fields)
    out = []
    for deg in range(1, dmax + 1):
        for combo in itertools.combinations_with_replacement(names, deg):
            md = {}
            for f in combo:
                md[f] = md.get(f, 0) + 1
            if sum(fields[f][1] * n for f, n in md.items()) != 0:
                continue
            if must_contain and not md.get(must_contain):
                continue
            out.append(md)
    return out


def census(fields, must_contain=None):
    mds = enumerate_multidegrees(fields, must_contain=must_contain)
    rows = []
    for md in mds:
        n = count_invariants(md, fields)
        rows.append({"md": md, "key": key_of(md), "n": n})
    nonzero = [r for r in rows if r["n"] > 0]
    zero = [r for r in rows if r["n"] == 0]
    # orbits
    seen = set(); orbits = []
    for r in nonzero:
        if r["key"] in seen:
            continue
        ck = key_of(conj_md(r["md"], fields))
        selfc = ck == r["key"]
        seen.add(r["key"]); seen.add(ck)
        partner = next((x for x in nonzero if x["key"] == ck), None)
        assert partner is not None and partner["n"] == r["n"], "conjugate multidegree must have the same count"
        orbits.append({"md": r["md"], "self_conjugate": selfc, "n": r["n"],
                       "real_parameters": r["n"] if selfc else 2 * r["n"]})
    return {"multidegrees_considered": len(rows), "multidegrees_nonzero": len(nonzero), "orbits": orbits,
            "n_orbits": len(orbits), "n_directions": sum(o["n"] for o in orbits),
            "n_real_parameters": sum(o["real_parameters"] for o in orbits),
            "zero_multidegrees": [r["md"] for r in zero]}


def md_str(md):
    return " ".join(PRETTY[k] + (f"^{v}" if v > 1 else "") for k, v in sorted(md.items(), key=lambda t: list(FIELDS_V22).index(t[0])) if v)


# ----------------------------------------------------------------------------------------------------------------
# fermion bilinears (B63)
# ----------------------------------------------------------------------------------------------------------------
B63 = [("F", "16", 1, 3), ("V1", "16", -35, 2), ("Vb1", "16bar", 39, 1), ("V2", "16", -28, 1), ("Vb2", "16bar", 32, 1),
       ("V3", "16", 34, 1), ("Vb3", "16bar", -30, 1), ("T10", "10", 2, 2), ("Pb", "16bar", 18, 1),
       ("N1", "1", -63, 1), ("N1b", "1", 59, 1), ("N2", "1", -58, 1), ("N2b", "1", 54, 1), ("N3", "1", -57, 1),
       ("N3b", "1", 61, 1), ("NMm", "1", -2, 2)]
SCALAR_INSERTIONS = [(None, "1", 0)] + [(f, FIELDS_V22[f][0], FIELDS_V22[f][1]) for f in FIELDS_V22]


def fermion_catalogue():
    """all Lorentz-scalar fermion bilinears psi_i psi_j (two left-handed Weyl fields; same field: symmetric part,
    i.e. allowed for generations > 1 or SO(10)-symmetric channel) x {1, one scalar or conjugate}, SO(10) singlet and
    X = 0."""
    found = []
    for (i, fi), (j, fj) in itertools.combinations_with_replacement(list(enumerate(B63)), 2):
        for s, srep, sx in SCALAR_INSERTIONS:
            X = fi[2] + fj[2] + sx
            if X != 0:
                continue
            if i == j:
                # same multiplet: psi_a psi_b with Lorentz epsilon is symmetric in flavour x gauge -> Sym^2 of the
                # gauge rep for a single generation; for g > 1 copies both Sym^2 and Lambda^2 contribute
                rep = W.REPS[fi[1]]()
                ch = W.sym_power(rep, 2)
                if fi[3] > 1:
                    ch = rep * rep
            else:
                ch = W.REPS[fi[1]]() * W.REPS[fj[1]]()
            if srep != "1":
                ch = ch * W.REPS[srep]()
            n = W.n_singlets(ch)
            found.append({"pair": (fi[0], fj[0]), "scalar": PRETTY.get(s, "none"), "X_sum": X, "n_SO10_singlets": n})
    return found


def main():
    t0 = time.time()
    out = {"engine": "so10_weyl_chars.py (own D5 Weyl characters, exact integers)"}
    # sanity decompositions
    out["sanity"] = {
        "Sym2(45)": W.pretty(W.decompose(W.sym_power(W.rep45(), 2))),
        "Sym2(210)": W.pretty(W.decompose(W.sym_power(W.rep210(), 2))),
        "Lambda2(210)": W.pretty(W.decompose(W.exterior_power(W.rep210(), 2))),
        "Sym3(45)": W.pretty(W.decompose(W.sym_power(W.rep45(), 3))),
        "45x210": W.pretty(W.decompose(W.rep45() * W.rep210())),
        "10x10": W.pretty(W.decompose(W.vector10() * W.vector10())),
        "10x126bar": W.pretty(W.decompose(W.vector10() * W.rep126bar())),
        "126x126bar": W.pretty(W.decompose(W.rep126() * W.rep126bar())),
        "Sym2(126bar)": W.pretty(W.decompose(W.sym_power(W.rep126bar(), 2))),
        "16x16": W.pretty(W.decompose(W.rep16() * W.rep16())),
        "16x16bar": W.pretty(W.decompose(W.rep16() * W.rep16bar())),
    }
    for k, v in out["sanity"].items():
        print(f"{k:14s} = {v}", flush=True)

    # (1) v20 reproduction
    c20 = census(FIELDS_V20)
    print(f"\nv20 census: nonzero multidegrees {c20['multidegrees_nonzero']}, orbits {c20['n_orbits']}, "
          f"directions {c20['n_directions']}, real parameters {c20['n_real_parameters']}  ({time.time()-t0:.1f}s)",
          flush=True)
    per = []
    ok = True
    by_key = {}
    for o in c20["orbits"]:
        by_key[key_of(o["md"])] = o
        by_key[key_of(conj_md(o["md"], FIELDS_V20))] = o
    for oid, (md, n) in V20_ORBITS.items():
        o = by_key.get(key_of(md))
        got = o["n"] if o else 0
        per.append({"v20_id": oid, "md": md_str(md), "attested": n, "own": got, "agree": got == n})
        ok &= got == n
    out["v20_reproduction"] = {
        "multidegrees_nonzero": c20["multidegrees_nonzero"], "orbits": c20["n_orbits"],
        "directions": c20["n_directions"], "real_parameters": c20["n_real_parameters"],
        "matches_attested_34_28_44_51": (c20["multidegrees_nonzero"], c20["n_orbits"], c20["n_directions"],
                                         c20["n_real_parameters"]) == (34, 28, 44, 51),
        "per_orbit_agree_with_v20_direction_list": ok, "per_orbit": per,
        "orbits_not_in_v20_list": [md_str(o["md"]) for o in c20["orbits"]
                                   if not any(key_of(md) in (key_of(o["md"]), key_of(conj_md(o["md"], FIELDS_V20)))
                                              for md, _ in V20_ORBITS.values())],
    }
    print("v20 per-orbit agreement:", ok, "| extra orbits:", out["v20_reproduction"]["orbits_not_in_v20_list"])

    # (2) v22: all orbits, and those containing A
    c22 = census(FIELDS_V22)
    cA = census(FIELDS_V22, must_contain="A")
    print(f"\nv22 census: nonzero multidegrees {c22['multidegrees_nonzero']}, orbits {c22['n_orbits']}, "
          f"directions {c22['n_directions']}, real parameters {c22['n_real_parameters']}")
    print(f"  new (containing A): nonzero multidegrees {cA['multidegrees_nonzero']}, orbits {cA['n_orbits']}, "
          f"directions {cA['n_directions']}, real parameters {cA['n_real_parameters']}  ({time.time()-t0:.1f}s)")
    rowsA = []
    for o in cA["orbits"]:
        rowsA.append({"multidegree": md_str(o["md"]), "md": o["md"], "n_invariants": o["n"],
                      "self_conjugate": o["self_conjugate"], "real_parameters": o["real_parameters"]})
        print(f"   {md_str(o['md']):40s} n={o['n']}  {'real' if o['self_conjugate'] else 'complex (+h.c.)'}")
    zA = [md_str(m) for m in cA["zero_multidegrees"]]
    print("  X-allowed multidegrees containing A with NO SO(10) singlet:", zA)
    out["v22_total"] = {k: c22[k] for k in ("multidegrees_nonzero", "n_orbits", "n_directions", "n_real_parameters")}
    out["v22_new_A_orbits"] = rowsA
    out["v22_new_A_counts"] = {k: cA[k] for k in ("multidegrees_nonzero", "n_orbits", "n_directions",
                                                   "n_real_parameters")}
    out["v22_A_multidegrees_vanishing"] = zA
    out["consistency_v22_equals_v20_plus_A"] = (
        c22["n_directions"] == c20["n_directions"] + cA["n_directions"]
        and c22["n_real_parameters"] == c20["n_real_parameters"] + cA["n_real_parameters"])

    # (3) fermion catalogue
    fc = fermion_catalogue()
    allowed = [r for r in fc if r["n_SO10_singlets"] > 0]
    print("\nfermion terms: X-neutral combinations", len(fc), "| SO(10)-invariant:", len(allowed))
    for r in allowed:
        print("   ", r["pair"], r["scalar"], "n =", r["n_SO10_singlets"])
    out["fermion_catalogue"] = {"x_neutral_combinations": fc, "invariant": allowed,
                                "n_invariant_structures": len(allowed),
                                "any_A45_yukawa": any(r["scalar"] == "A45" for r in allowed),
                                "any_bare_mass": any(r["scalar"] == "none" for r in allowed)}
    out["seconds"] = time.time() - t0
    (HERE / "census_v22.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("wrote census_v22.json", f"({out['seconds']:.1f}s)")


if __name__ == "__main__":
    main()
