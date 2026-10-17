"""sk2: own enumeration of mu-tight TWO-fermion operators (building blocks of every K = 17 one-loop closure).

Reduction (EXACT, uses only the certificate): an operator containing Phi210, an S S* pair, a Phi17 Phi17* pair, an
H-type pair, or two H-type legs (H10/Delta replaced by S*/S) is never mu-tight, because removing/replacing those fields
keeps X, z and q and lowers d, and the certificate (verified in sk2_cert.py on the superset) bounds the reduced
operator.  So tight two-fermion operators are psi_a psi_b x S^k x Phi17^p x (at most one of H10, H10*, Delta, Delta*)
(x one derivative for opposite chirality).  SO(10) singlet: textbook bilinear decompositions (Slansky).
Writes sk2_tight2.json."""
from __future__ import annotations

import itertools
import json
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
FERM = [("F", "16", 1, 3), ("V1", "16", -35, 2), ("Vb1", "16b", 39, 1), ("V2", "16", -28, 1), ("Vb2", "16b", 32, 1),
        ("V3", "16", 34, 1), ("Vb3", "16b", -30, 1), ("T", "10", 2, 2), ("Pb", "16b", 18, 1), ("N1", "1", -63, 1),
        ("N1b", "1", 59, 1), ("N2", "1", -58, 1), ("N2b", "1", 54, 1), ("N3", "1", -57, 1), ("N3b", "1", 61, 1),
        ("NMm", "1", -2, 2)]
QF = {"V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "Pb": (0, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0),
      "Vb2": (0, 0, -1, 0, 0, 0), "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0),
      "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1),
      "N3b": (0, 0, 0, 0, 0, -1)}
MU = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))
ZC = {"16": 1, "16b": 3, "10": 2, "1": 0, "126": 2, "126b": 2}
CONJ = {"16": "16b", "16b": "16", "10": "10", "1": "1", "126": "126b", "126b": "126"}
PROD = {("16", "16"): {"10": "s", "126": "s", "120": "a"}, ("16b", "16b"): {"10": "s", "126b": "s", "120": "a"},
        ("16", "16b"): {"1": None, "45": None, "210": None}, ("10", "10"): {"1": "s", "45": "a", "54": "s"},
        ("10", "16"): {"16b": None, "144": None}, ("10", "16b"): {"16": None, "144b": None}}
HTYPE = [("none", "1", 0), ("H10", "10", -2), ("H10*", "10", 2), ("Delta", "126b", -2), ("Delta*", "126", 2)]


def prod(a, b):
    if (a, b) in PROD:
        return PROD[(a, b)]
    if (b, a) in PROD:
        return PROD[(b, a)]
    if a == "1":
        return {b: "s"}
    if b == "1":
        return {a: "s"}
    raise KeyError((a, b))


def main():
    items = []
    for n, r, x, g in FERM:
        q = QF.get(n, (0,) * 6)
        items.append(dict(lab=n, rep=r, X=x, z=ZC[r], q=q, dot=0, sp=n, g=g))
        items.append(dict(lab=n + "^", rep=CONJ[r], X=-x, z=(-ZC[r]) % 4, q=tuple(-c for c in q), dot=1, sp=n, g=g))
    found = []
    for i, j in itertools.combinations_with_replacement(range(len(items)), 2):
        a, b = items[i], items[j]
        deriv = 1 if a["dot"] != b["dot"] else 0
        if a["dot"] != b["dot"] and a["sp"] == b["sp"]:
            continue  # psi^dag dsigma psi: q = 0, kinetic-type, never PQ-relevant
        for hn, hr, hx in HTYPE:
            if (a["z"] + b["z"] + ZC[hr]) % 4:
                continue
            need = CONJ[hr]
            pr = prod(a["rep"], b["rep"])
            if need not in pr:
                continue
            if i == j and a["g"] == 1 and pr[need] == "a":
                continue  # identical one-generation Weyl field needs a symmetric invariant
            mq = sum(m * (qa + qb) for m, qa, qb in zip(MU, a["q"], b["q"]))
            for p in range(-20, 21):
                rest = -(a["X"] + b["X"] + hx + 17 * p)
                if rest % 4:
                    continue
                k = rest // 4
                d = 3 + deriv + (0 if hn == "none" else 1) + abs(k) + abs(p)
                if not 5 <= d <= 20:
                    continue
                if mq + Fr(17, 4) * p == d - 4:
                    q = tuple(qa + qb + (p if t == 0 else 0) for t, (qa, qb) in enumerate(zip(a["q"], b["q"])))
                    found.append({"op": f"{a['lab']} {b['lab']} " + (hn + " " if hn != "none" else "") +
                                  (f"Phi17^{p} " if p > 0 else f"Phi17*^{-p} " if p < 0 else "") +
                                  (f"S^{k}" if k > 0 else f"S*^{-k}" if k < 0 else "") + (" D" if deriv else ""),
                                  "d": d, "q": q})
    found.sort(key=lambda r: (r["d"], r["op"]))
    for r in found:
        print("d=%2d %-40s q=%s" % (r["d"], r["op"], r["q"]))
    print("count:", len(found))
    (HERE / "sk2_tight2.json").write_text(json.dumps({"count": len(found), "ops": found}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
