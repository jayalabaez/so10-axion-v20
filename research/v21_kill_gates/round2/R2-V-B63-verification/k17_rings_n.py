"""R2-V continuation: one-loop K = 17 rings with n = 2..5 tight two-fermion operators (exhaustive over multisets of the
tight operators of k17_oneloop.py; a multiset counts once if SOME cyclic order and fermion orientation closes with
high-scale mass paths).  Writes k17_rings_n.json."""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import k17_oneloop as k

HERE = Path(__file__).resolve().parent


def ring_ok(seq):
    """seq: list of ops in cyclic order; try all fermion orientations."""
    n = len(seq)
    for orient in itertools.product((0, 1), repeat=n):
        lines = []
        ok = True
        for t in range(n):
            A, B = seq[t], seq[(t + 1) % n]
            a_out = A["items"][1 - orient[t]]
            b_in = B["items"][orient[(t + 1) % n]]
            lp = k.line_paths(a_out, b_in)
            if not lp:
                ok = False
                break
            lines.append(lp[0])
        if ok:
            return lines
    return None


def main():
    ops, _ = k.tight_two_fermion_ops()
    seen = {}
    for o in ops:
        seen.setdefault(k.op_name(o), o)
    ops = sorted(seen.values(), key=lambda o: (o["d"], k.op_name(o)))
    for o in ops:
        print("  tight: d=%2d  %-34s q=%s" % (o["d"], k.op_name(o), o["q"]))
    out = {"tight_ops": [{"op": k.op_name(o), "d": o["d"], "q": o["q"]} for o in ops], "rings": {}}
    L = math.log(k.MPL ** 2 / k.MS ** 2)
    for n in range(2, 6):
        found = []
        for combo in itertools.combinations_with_replacement(range(len(ops)), n):
            qs = [ops[i]["q"] for i in combo]
            if tuple(sum(c) for c in zip(*qs)) != k.TARGET:
                continue
            first = combo[0]
            rest = list(combo[1:])
            hit = None
            for perm in set(itertools.permutations(rest)):
                seq = [ops[first]] + [ops[i] for i in perm]
                lines = ring_ok(seq)
                if lines:
                    hit = ([k.op_name(s) for s in seq], lines)
                    break
            if hit:
                found.append({"ops": hit[0], "lines": hit[1], "K": sum(ops[i]["d"] for i in combo) - 4 * n})
        ninsert = [sum(len(l) for l in f["lines"]) for f in found]
        out["rings"][n] = {"count": len(found), "examples": found[:50], "insertions": ninsert[:50]}
        print("n=%d rings: %d" % (n, len(found)), flush=True)
    # NDA total (coherent and random-phase), one Yukawa per insertion, O(1) operator coefficients
    tot = {}
    for y in (0.304, 0.35, 0.368):
        coh = 0.0
        rnd = 0.0
        for n, r in out["rings"].items():
            for f in r["examples"] if r["count"] <= 50 else []:
                m = sum(len(l) for l in f["lines"])
                a = y ** m / (16 * math.pi ** 2) * L
                coh += a
                rnd += a * a
        tot["y=%.3f" % y] = {"coherent_sum_over_rings": coh, "random_phase_rms": math.sqrt(rnd)}
    out["nda_total_relative_to_tree"] = tot
    out["L"] = L
    print(json.dumps(tot, indent=1))
    (HERE / "k17_rings_n.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
