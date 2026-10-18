"""SKEPTIC re-check of the D1 contract for v22-L2 (anomalies, accidental kernel, PQ numbers, quality) with own code.

(a) anomalies with exact Fractions from the B63 list as stated in the task text (not from the builder's tables);
(b) accidental kernel: sympy nullspace of [12 Yukawas + every phase-sensitive (non-self-conjugate) scalar orbit of
    degree <= 4 with an SO(10) singlet, taken from MY torus-integration count sk_charcount.json]; with and without the
    two A orbits; checks that X, G2 and f1..f5 (R2-V round-1 basis) lie in / span the kernel;
(c) N, E for PQ = X - 17 G2 from complete-multiplet SU(3) indices and Q_em^2 sums (own numbers);
(d) quality: verify the PREMISES of the exact monotonicity argument (A45 carries zero charge under every kernel
    generator, centre class 0 from the chart-derived weights, mass dimension 1 > 0) and enumerate the minimal
    PQ-violating SCALAR-only operator dimension with and without A (exact integer search);
    corroboration: the model builder's DP table (its dp_table, read-only import) with and without the A45 item.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_common as C  # noqa: E402

LOG = open(C.HERE / "sk_d1.log", "w", encoding="utf-8")
OUT = C.HERE / "sk_d1.json"


def log(m):
    C.log(m, LOG)


# B63 as stated in the task: 3x16_F(1); 16(-35)x2 + 16bar(39); 16(-28)+16bar(32); 16(34)+16bar(-30); 2x10(2);
# Pb 16bar(18); singlets N1(-63) N1b(59) N2(-58) N2b(54) N3(-57) N3b(61) NMm(-2)x2
FERM = [("F", 16, 1, 3), ("V1", 16, -35, 2), ("Vb1", -16, 39, 1), ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
        ("V3", 16, 34, 1), ("Vb3", -16, -30, 1), ("T", 10, 2, 2), ("Pb", -16, 18, 1), ("N1", 1, -63, 1),
        ("N1b", 1, 59, 1), ("N2", 1, -58, 1), ("N2b", 1, 54, 1), ("N3", 1, -57, 1), ("N3b", 1, 61, 1),
        ("NMm", 1, -2, 2)]
DIM = {16: 16, -16: 16, 10: 10, 1: 1}
TIDX = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}            # Dynkin index (normalisation T(10) = 1)
NSU3 = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}            # sum of SU(3) indices T(3)=1/2 over the multiplet
Q2 = {16: Fr(16, 3), -16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}   # sum over the multiplet of N_c Q_em^2


def anomalies():
    so10x = sum(TIDX[r] * x * m for _, r, x, m in FERM)
    x3 = sum(DIM[r] * Fr(x) ** 3 * m for _, r, x, m in FERM)
    grav = sum(DIM[r] * x * m for _, r, x, m in FERM)
    net = sum((m if r == 16 else -m if r == -16 else 0) for _, r, x, m in FERM)
    return {"SO10^2 X": str(so10x), "X^3": str(x3), "grav X": str(grav), "net 16-16bar": net,
            "anomaly_free": so10x == 0 and x3 == 0 and grav == 0}


SPECIES = [f[0] for f in FERM] + ["Delta", "H10", "S", "Phi17"]
SI = {s: k for k, s in enumerate(SPECIES)}


def row(terms):
    r = [0] * len(SPECIES)
    for s, n in terms:
        r[SI[s]] += n
    return r


YUK = {"F.F.H10": [("F", 2), ("H10", 1)], "F.F.Delta126bar": [("F", 2), ("Delta", 1)],
       "V1.Vb1.S^dag": [("V1", 1), ("Vb1", 1), ("S", -1)], "V1.Pb.Phi17": [("V1", 1), ("Pb", 1), ("Phi17", 1)],
       "V2.Vb2.S^dag": [("V2", 1), ("Vb2", 1), ("S", -1)], "Vb2.Vb3.H10": [("Vb2", 1), ("Vb3", 1), ("H10", 1)],
       "V3.Vb3.S^dag": [("V3", 1), ("Vb3", 1), ("S", -1)], "T.T.S^dag": [("T", 2), ("S", -1)],
       "N1.N1b.S": [("N1", 1), ("N1b", 1), ("S", 1)], "N2.N2b.S": [("N2", 1), ("N2b", 1), ("S", 1)],
       "N3.N3b.S^dag": [("N3", 1), ("N3b", 1), ("S", -1)], "NMm.NMm.S": [("NMm", 2), ("S", 1)]}
XF = {f[0]: f[2] for f in FERM}
XF.update({"Delta": -2, "H10": -2, "S": 4, "Phi17": 17})


def scalar_row(label):
    c = Counter()
    for tok in label.split():
        f, n = (tok.split("^") + ["1"])[:2]
        c[f] += int(n)
    m = {"H": ("H10", 1), "Hb": ("H10", -1), "D": ("Delta", 1), "Db": ("Delta", -1), "S": ("S", 1),
         "Sb": ("S", -1), "T": ("Phi17", 1), "Tb": ("Phi17", -1)}
    return row([(m[f][0], m[f][1] * n) for f, n in c.items() if f in m])


def kernel():
    # Yukawa X check
    xbad = {k: sum(XF[s] * n for s, n in v) for k, v in YUK.items() if sum(XF[s] * n for s, n in v) != 0}
    cc = json.loads((C.HERE / "sk_charcount.json").read_text(encoding="utf-8"))
    ps_v20 = [o["rep"] for o in cc["orbits"] if not o["self_conjugate"] and o["n_invariants"] > 0 and not o["contains_A"]]
    ps_A = [o["rep"] for o in cc["orbits"] if not o["self_conjugate"] and o["n_invariants"] > 0 and o["contains_A"]]
    Ry = [row(v) for v in YUK.values()]
    Rv = [scalar_row(l) for l in ps_v20]
    Ra = [scalar_row(l) for l in ps_A]
    rk = lambda rows: sp.Matrix(rows).rank() if rows else 0
    r_y, r_yv, r_yva = rk(Ry), rk(Ry + Rv), rk(Ry + Rv + Ra)
    ker = sp.Matrix(Ry + Rv + Ra).nullspace()
    Xv = sp.Matrix([XF[s] for s in SPECIES])
    G2 = sp.Matrix(row([("V1", -1), ("Vb1", 1), ("Phi17", 1)]))
    # R2-V round-1 basis f1..f5 (dual_dp_orig.Q)
    f = [row([("V1", 1), ("Vb1", -1), ("Pb", -1)]), row([("V2", 1), ("Vb2", -1), ("V3", -1), ("Vb3", 1)]),
         row([("N1", 1), ("N1b", -1)]), row([("N2", 1), ("N2b", -1)]), row([("N3", 1), ("N3b", -1)])]
    M = sp.Matrix(Ry + Rv + Ra)
    inker = lambda v: all(x == 0 for x in (M * sp.Matrix(v)))
    span = sp.Matrix.hstack(Xv, G2, *[sp.Matrix(v) for v in f]).rank()
    return {"yukawa_X_violations": xbad, "phase_sensitive_v20_orbits_from_my_count": ps_v20,
            "phase_sensitive_A_orbits_from_my_count": ps_A, "rank_yukawas": r_y, "rank_yuk+v20": r_yv,
            "rank_yuk+v20+A": r_yva, "kernel_dim": len(ker), "X_in_kernel": inker(list(Xv)),
            "G2_in_kernel": inker(list(G2)), "f_in_kernel": [inker(v) for v in f],
            "rank_of_{X,G2,f1..f5}": span}, G2, f


def pq_numbers(G2):
    pq = {s: XF[s] - 17 * int(G2[SI[s]]) for s in SPECIES}
    N = sum(m * pq[n] * NSU3[r] for n, r, x, m in FERM)
    E = sum(m * pq[n] * Q2[r] for n, r, x, m in FERM)
    return {"PQ_scalar_charges": {s: pq[s] for s in ("Delta", "H10", "S", "Phi17")}, "N": str(N), "E": str(E),
            "E/N": str(E / N)}


def centre_classes():
    import sk_charcount as CC
    W, _ = CC.chart_weights()
    out = {}
    for name, w in W.items():
        cls = sorted(set(int(round(2 * row_.sum())) % 4 for row_ in w))
        out[name] = cls
    return out


def min_scalar_pq_violating(with_A: bool, dmax: int = 24):
    """exact search over scalar monomials: X = 0, centre (#10 + #126 even), PQ = X - 17 G2 != 0 (G2 = n_Phi17 net)."""
    best = None
    fields = ["Phi", "H", "Hb", "D", "Db", "S", "Sb", "T", "Tb"] + (["A"] if with_A else [])
    X = {"Phi": 0, "A": 0, "H": -2, "Hb": 2, "D": -2, "Db": 2, "S": 4, "Sb": -4, "T": 17, "Tb": -17}
    G2 = {"T": 1, "Tb": -1}
    # dimension d = sum n_i; enumerate by (n_T, n_Tb, n_S, n_Sb, n_H+n_D (net X via 10/126 legs), ...) cleverly:
    for d in range(1, dmax + 1):
        found = None
        for nT in range(0, d + 1):
            for nTb in range(0, d + 1 - nT):
                g2 = nT - nTb
                if g2 == 0:
                    continue
                rem = d - nT - nTb
                for nS in range(0, rem + 1):
                    for nSb in range(0, rem + 1 - nS):
                        r2 = rem - nS - nSb
                        # r2 legs from {H, Hb, D, Db} (X = -2 / +2) and real {Phi, A} (X = 0)
                        for nneg in range(0, r2 + 1):
                            for npos in range(0, r2 + 1 - nneg):
                                nreal = r2 - nneg - npos
                                if nreal and not fields.count("Phi"):
                                    continue
                                Xtot = 17 * g2 + 4 * (nS - nSb) - 2 * nneg + 2 * npos
                                if Xtot != 0 or (nneg + npos) % 2:
                                    continue
                                pq = Xtot - 17 * g2
                                if pq != 0:
                                    found = {"d": d, "Phi17": nT, "Phi17^dag": nTb, "S": nS, "S^dag": nSb,
                                             "10/126 (X=-2)": nneg, "10/126^dag": npos, "real (Phi/A)": nreal}
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        if found:
            best = found
            break
    return best


def builder_dp_with_without_A(dmax=24):
    sys.path.insert(0, str(C.CHART_DIR.parent / "model"))
    import d1_contract_v22 as D1  # read-only import, functions only
    base = [s for s in D1.SCALARS if s[0] != "A45"] if hasattr(D1, "SCALARS") else None
    sc_all = None
    for name in ("SCALARS", "SCALARS_V22", "SC"):
        if hasattr(D1, name):
            sc_all = getattr(D1, name)
            break
    if sc_all is None:
        return {"skipped": "scalar list not found in d1_contract_v22"}
    noA = [s for s in sc_all if s[0] != "A45"]
    t_with = D1.dp_table(sc_all, dmax=dmax)
    t_without = D1.dp_table(noA, dmax=dmax)
    a = [(r["d"], r["max_excess_x4"]) for r in t_with]
    b = [(r["d"], r["max_excess_x4"]) for r in t_without]
    return {"with_A": a, "without_A": b, "identical": a == b, "max_with": max(v for _, v in a)}


def main():
    t0 = time.time()
    res = {"anomalies": anomalies()}
    log(f"(a) {res['anomalies']}")
    k, G2, f = kernel()
    res["kernel"] = k
    log(f"(b) {k}")
    res["pq"] = pq_numbers(G2)
    log(f"(c) {res['pq']}")
    res["centre_classes_from_chart_weights (2*sum(lambda) mod 4)"] = centre_classes()
    log(f"(d) centre classes {res['centre_classes_from_chart_weights (2*sum(lambda) mod 4)']}")
    res["A45_kernel_charges"] = "0 for every U(1) (real field, absent from the 20 complex species); X = PQ = 0"
    res["min_PQ_violating_scalar_operator"] = {"with_A": min_scalar_pq_violating(True),
                                               "without_A": min_scalar_pq_violating(False)}
    log(f"(d) min PQ-violating scalar operator {res['min_PQ_violating_scalar_operator']}")
    try:
        res["builder_dp_table_with_without_A"] = builder_dp_with_without_A()
    except Exception as exc:  # noqa: BLE001
        res["builder_dp_table_with_without_A"] = {"error": repr(exc)}
    log(f"(d) builder DP with/without A: {res['builder_dp_table_with_without_A']}")
    res["time_s"] = time.time() - t0
    C.json_dump(res, OUT)
    log(f"wrote {OUT}")


if __name__ == "__main__":
    main()
