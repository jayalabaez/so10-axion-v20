"""Consistency check of the K = 17 one-loop rings: rebuild each ring with explicit line orientation and verify that
the total vev monomial (operator scalar legs + line insertions) is X-neutral with Phi17 number +4, i.e.
S*^17 Phi17^4 x (neutral), and that the loop-integral dimension [I] = 4 + K - n_vev is <= 0.
External vev at an insertion: a line leaving field psi_A (undotted) meets the h.c. vertex phi* psi_A^dag psi_B^dag
(external phi*); leaving psi_A^dag (dotted) it meets phi psi_A psi_B (external phi).  Chirality alternates."""
from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from pathlib import Path

import k17_oneloop as k

HERE = Path(__file__).resolve().parent
XS = {"S": 4, "S*": -4, "Phi17": 17, "Phi17*": -17, "Delta": -2, "Delta*": 2}
CONJ = {"S": "S*", "S*": "S", "Phi17": "Phi17*", "Phi17*": "Phi17", "Delta": "Delta*", "Delta*": "Delta"}


def line_walks(u, v, maxlen=3):
    """all walks from field u to field v (as fields in the two operators) with external vevs, minimal length."""
    if u[1] != v[1] and u[0] == v[0]:
        return [[]]
    res = []
    frontier = [(u[0], u[1], [])]  # current species, chirality of the field that must be contracted (as in operator)
    for L in range(1, maxlen + 1):
        nxt = []
        for sp, dotted, ext in frontier:
            for nb, phi, _v in k.ADJ.get(sp, []):
                e = CONJ[phi] if not dotted else phi
                # after the vertex the line continues from field nb with chirality: vertex field nb has chirality
                # opposite to the contracted vertex field; the operator field it can end on has chirality = 'dotted'
                nxt.append((nb, dotted, ext + [e]))
        for sp, dotted, ext in nxt:
            # ends on v if species matches and chirality rule: odd L -> same chirality as u, even -> opposite
            same = (L % 2 == 1)
            if sp == v[0] and ((v[1] == u[1]) == same):
                res.append(ext)
        if res:
            return res
        # flip chirality bookkeeping for the next step: the next vertex is contracted with nb^(opposite)
        frontier = [(sp, not dotted, ext) for sp, dotted, ext in nxt]
    return res


def op_vevs(o):
    c = Counter()
    if o["p"] > 0:
        c["Phi17"] += o["p"]
    if o["p"] < 0:
        c["Phi17*"] += -o["p"]
    if o["s"] > 0:
        c["S"] += o["s"]
    if o["s"] < 0:
        c["S*"] += -o["s"]
    for kk in ("H10", "H10^", "Delta", "Delta^"):
        if o[kk]:
            c[kk.replace("^", "*")] += o[kk]
    return c


def main():
    ops, _ = k.tight_two_fermion_ops()
    seen = {}
    for o in ops:
        seen.setdefault(k.op_name(o), o)
    ops = sorted(seen.values(), key=lambda o: (o["d"], k.op_name(o)))
    XS2 = dict(XS)
    XS2.update({"H10": -2, "H10*": 2})
    results = []
    for n in (2, 3):
        for combo in itertools.combinations_with_replacement(range(len(ops)), n):
            qs = [ops[i]["q"] for i in combo]
            if tuple(sum(c) for c in zip(*qs)) != k.TARGET:
                continue
            best = None
            for perm in set(itertools.permutations(combo[1:])):
                seq = [ops[combo[0]]] + [ops[i] for i in perm]
                for orient in itertools.product((0, 1), repeat=n):
                    exts = []
                    ok = True
                    for t in range(n):
                        A, B = seq[t], seq[(t + 1) % n]
                        a_out = A["items"][1 - orient[t]]
                        b_in = B["items"][orient[(t + 1) % n]]
                        w = line_walks(a_out, b_in)
                        if not w:
                            ok = False
                            break
                        exts.append(w[0])
                    if not ok:
                        continue
                    vev = Counter()
                    for o in seq:
                        vev += op_vevs(o)
                    for e in exts:
                        vev += Counter(e)
                    X = sum(XS2[f] * m for f, m in vev.items())
                    G2 = vev["Phi17"] - vev["Phi17*"]
                    nvev = sum(vev.values())
                    K = sum(o["d"] for o in seq) - 4 * n
                    I = 4 + K - nvev
                    rec = {"ops": [k.op_name(o) for o in seq], "line_externals": exts, "vev_monomial": dict(vev),
                           "X": X, "G2": G2, "n_vev": nvev, "K": K, "I_dim": I,
                           "n_yukawa": sum(len(e) for e in exts)}
                    if best is None or rec["n_vev"] < best["n_vev"]:
                        best = rec
            if best:
                results.append(best)
    bad = [r for r in results if r["X"] != 0 or r["G2"] != 4 or r["I_dim"] > 0]
    for r in results:
        print(r["ops"], "| vev", r["vev_monomial"], "| X", r["X"], "G2", r["G2"], "n_vev", r["n_vev"], "[I]", r["I_dim"],
              "| yukawas", r["n_yukawa"])
    print("rings:", len(results), " inconsistent:", len(bad))
    L = math.log(k.MPL ** 2 / k.MS ** 2)
    tot = {}
    for y in (0.304, 0.35, 0.368):
        amps = [y ** r["n_yukawa"] / (16 * math.pi ** 2) * (L if r["I_dim"] == 0 else 1.0) for r in results]
        tot["y=%.3f" % y] = {"coherent": sum(amps), "rms": math.sqrt(sum(a * a for a in amps)), "max_single": max(amps)}
    print(json.dumps(tot, indent=1))
    (HERE / "k17_check_vev.json").write_text(json.dumps({"rings": results, "inconsistent": bad, "nda": tot, "L": L},
                                                       indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
