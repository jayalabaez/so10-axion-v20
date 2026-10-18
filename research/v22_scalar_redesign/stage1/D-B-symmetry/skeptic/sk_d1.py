"""SKEPTIC (D-B-symmetry, D1): independent re-derivation for V1 (B63 fermions + H2 = second complex 10_H, X = -2).

Own code (no import of the designer's or R2-V's modules):
 (a) exact anomalies [SO(10)]^2 X, grav-X, X^3 (Dynkin index T(10)=1, T(16)=2);
 (b) renormalizable fermion Yukawa / mass census from SO(10) bilinear rules (16x16 > 10,120,126; 16bar x 16bar >
     10,120,126bar; 16 x 16bar > 1,45,210; 10x10 > 1,45,54; 1 x R = R) with X = 0, scalars Phi210(0), Delta 126bar(-2),
     H1, H2 10(-2), S(4), Phi17(17) and conjugates; symmetric/antisymmetric bookkeeping for identical species;
 (c) accidental-symmetry kernel: rephasing charges of 16 fermion species + 5 complex scalars subject to every census
     term and the phase-sensitive scalar terms (generic: kappa_ab H_a H_b S, m12^2 H1* H2, Phi H_a* Delta, Phi H_a* Delta*
     S*, Delta^2 H_a* H_b*, H_a* Delta^2 Delta*); kernel dimension and whether H2 = H1 on the kernel;
 (d) own exact integer DP of max_O [4 mu.q(O) - 4(d(O) - 4)] over all X = 0, centre-0, Lorentz-admissible monomials with
     H2 as a SEPARATE item (dict-based DP, different algorithm from R2-V's array DP), d = 5..30, using the round-1
     certificate mu = (17/4, -7/2, -7, -57/4, -12, -51/4) on the kernel basis (G2, f1..f5) recomputed in (c);
 (e) brute-force enumeration for d <= 8 as a DP cross-check.
Writes sk_d1.json.
"""
from __future__ import annotations

import itertools
import json
from fractions import Fraction as Fr
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
FERM = [("F", 16, 1, 3), ("V1", 16, -35, 2), ("Vb1", -16, 39, 1), ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
        ("V3", 16, 34, 1), ("Vb3", -16, -30, 1), ("T", 10, 2, 2), ("Pb", -16, 18, 1), ("N1", 1, -63, 1),
        ("N1b", 1, 59, 1), ("N2", 1, -58, 1), ("N2b", 1, 54, 1), ("N3", 1, -57, 1), ("N3b", 1, 61, 1), ("NMm", 1, -2, 2)]
SCAL = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H1", 10, -2, False), ("H2", 10, -2, False),
        ("S", 1, 4, False), ("Phi17", 1, 17, False)]
TIDX = {1: 0, 10: 1, 16: 2, -16: 2}
DIM = {1: 1, 10: 10, 16: 16, -16: 16}


def anomalies():
    a1 = sum(Fr(TIDX[r]) * x * n for _, r, x, n in FERM)
    a2 = sum(Fr(DIM[r]) * x * n for _, r, x, n in FERM)
    a3 = sum(Fr(DIM[r]) * Fr(x) ** 3 * n for _, r, x, n in FERM)
    return {"SO10^2_X": str(a1), "grav_X": str(a2), "X^3": str(a3)}


def bilinear_reps(r1, r2):
    """SO(10) irreps (as signed labels) in r1 x r2 for r in {1, 10, 16, -16}; returns set."""
    s = {r1, r2}
    if r1 == 1:
        return {r2}
    if r2 == 1:
        return {r1}
    if r1 == 16 and r2 == 16:
        return {10, 120, 126}
    if r1 == -16 and r2 == -16:
        return {10, 120, -126}
    if s == {16, -16}:
        return {1, 45, 210}
    if r1 == 10 and r2 == 10:
        return {1, 45, 54}
    if s == {10, 16}:
        return {-16, 144}
    if s == {10, -16}:
        return {16, -144}
    raise ValueError((r1, r2))


def conj_rep(r):
    return {10: 10, 1: 1, 210: 210, 126: -126, -126: 126, 16: -16, -16: 16}[r]


def census():
    """renormalizable fermion bilinear x (scalar or mass) terms allowed by SO(10) x U(1)_X."""
    ins = [("mass", 1, 0)]
    for n, r, x, real in SCAL:
        ins.append((n, r, x))
        if not real:
            ins.append(("conj[" + n + "]", conj_rep(r), -x))
    terms = []
    for (i, a), (j, b) in itertools.combinations_with_replacement(list(enumerate(FERM)), 2):
        na, ra, xa, ma = a; nb, rb, xb, mb = b
        if i == j and ma == 1 and ra in (1,):
            pass
        prods = bilinear_reps(ra, rb)
        for sn, sr, sx in ins:
            if xa + xb + sx != 0:
                continue
            need = conj_rep(sr)
            if need not in prods:
                continue
            # identical single species: only symmetric part survives (fermion bilinear psi^T C psi is symmetric in flavour
            # x antisymmetric spinor -> for one copy the SO(10) part must be symmetric): 120 is antisymmetric
            if i == j and ma == 1 and need in (120, 45):
                continue
            if i == j and ma == 1 and ra == 10 and need == 45:
                continue
            terms.append({"fermions": [na, nb], "insertion": sn})
    return terms


def kernel(terms):
    names = [f[0] for f in FERM] + ["Delta", "H1", "H2", "S", "Phi17"]
    idx = {n: k for k, n in enumerate(names)}
    rows = []
    for t in terms:
        row = [0] * len(names)
        for f in t["fermions"]:
            row[idx[f]] += 1
        s = t["insertion"]
        if s not in ("mass", "Phi210"):
            if s.startswith("conj["):
                row[idx[s[5:-1]]] -= 1
            else:
                row[idx[s]] += 1
        rows.append(row)
    D, H1, H2, S = idx["Delta"], idx["H1"], idx["H2"], idx["S"]
    scal = [{H1: 2, S: 1}, {H1: 1, H2: 1, S: 1}, {H2: 2, S: 1}, {H1: -1, H2: 1}, {H1: -1, D: 1}, {H2: -1, D: 1},
            {H1: -1, D: -1, S: -1}, {H2: -1, D: -1, S: -1}, {D: 2, H1: -2}, {D: 2, H1: -1, H2: -1}, {D: 2, H2: -2},
            {H1: -1, D: 1}, {H2: -1, D: 1}]
    for cf in scal:
        row = [0] * len(names)
        for k_, v in cf.items():
            row[k_] = v
        rows.append(row)
    M = sp.Matrix(rows)
    ns = M.nullspace()
    xvec = sp.Matrix([f[2] for f in FERM] + [-2, -2, -2, 4, 17])
    x_in = all((M * xvec)[r] == 0 for r in range(M.rows))
    return names, M.rank(), ns, x_in, M


# round-1 kernel basis (G2, f1..f5) as a checkable hypothesis; verified against the computed kernel below
QB = {"V1": (-1, 1, 0, 0, 0, 0), "Vb1": (1, -1, 0, 0, 0, 0), "V2": (0, 0, 1, 0, 0, 0), "Vb2": (0, 0, -1, 0, 0, 0),
      "V3": (0, 0, -1, 0, 0, 0), "Vb3": (0, 0, 1, 0, 0, 0), "Pb": (0, -1, 0, 0, 0, 0), "N1": (0, 0, 0, 1, 0, 0),
      "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0), "N3": (0, 0, 0, 0, 0, 1),
      "N3b": (0, 0, 0, 0, 0, -1), "Phi17": (1, 0, 0, 0, 0, 0)}
MU = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))
ZC = {16: 1, -16: 3, 10: 2, 1: 0, 210: 0, -126: 2, 126: 2}


def items():
    out = []
    for n, r, x, _m in FERM:
        q = QB.get(n, (0,) * 6)
        for bar in (0, 1):
            s = -1 if bar else 1
            v = 4 * sum(m * s * c for m, c in zip(MU, q))
            out.append((n + ("^" if bar else ""), s * x, (s * ZC[r]) % 4, int(v), 3, 1 - bar, bar))
    for n, r, x, real in SCAL:
        q = QB.get(n, (0,) * 6)
        for bar in ((0,) if real else (0, 1)):
            s = -1 if bar else 1
            v = 4 * sum(m * s * c for m, c in zip(MU, q))
            out.append((n + ("^" if bar else ""), s * x, (s * ZC[r]) % 4, int(v), 2, 0, 0))
    return out


def dp(its, wmax, xcap):
    """layer[W] = dict[(X, z, pu, pb)] -> best value; multisets (unbounded knapsack over weight)."""
    layers = [dict() for _ in range(wmax + 1)]
    layers[0][(0, 0, 0, 0)] = 0
    for W in range(1, wmax + 1):
        cur = layers[W]
        for (lab, x, z, v, w, u, b) in its:
            if w > W:
                continue
            for (X, Z, pu, pb), val in layers[W - w].items():
                nX = X + x
                if abs(nX) > xcap:
                    continue
                key = (nX, (Z + z) % 4, pu ^ u, pb ^ b)
                nv = val + v
                if cur.get(key, -10**9) < nv:
                    cur[key] = nv
    return layers


def brute(its, dmax):
    best = {}

    def rec(k, w, X, Z, pu, pb, v):
        if k == len(its):
            if X == 0 and Z % 4 == 0 and pu == pb and w % 2 == 0:
                d = w // 2 + (1 if pu else 0)
                if 5 <= d <= dmax:
                    best[d] = max(best.get(d, -10**9), v - 4 * (d - 4))
            return
        lab, x, z, vv, ww, u, b = its[k]
        m = 0
        while w + m * ww <= 2 * dmax:
            rec(k + 1, w + m * ww, X + m * x, Z + m * z, pu ^ ((m * u) & 1), pb ^ ((m * b) & 1), v + m * vv)
            m += 1
    rec(0, 0, 0, 0, 0, 0, 0)
    return best


def main():
    out = {"anomalies": anomalies()}
    terms = census()
    out["census"] = [".".join(t["fermions"]) + "." + t["insertion"] for t in terms]
    names, rank, ns, x_in, Mrows = kernel(terms)
    out["kernel"] = {"n_charges": len(names), "rank": int(rank), "dim": len(ns), "X_in_kernel": bool(x_in),
                     "H2_eq_H1_on_kernel": all(v[names.index("H2")] == v[names.index("H1")] for v in ns)}
    # check the QB basis (+ X) spans the computed kernel and lies in it
    basis = []
    for c in range(6):
        vec = [QB.get(n, (0,) * 6)[c] if n in QB else 0 for n in names]
        basis.append(vec)
    basis.append([f[2] for f in FERM] + [-2, -2, -2, 4, 17])
    B = sp.Matrix(basis).T
    K = sp.Matrix.hstack(*ns)
    out["kernel"]["QB+X_rank"] = int(B.rank())
    out["kernel"]["QB+X_in_kernel"] = bool((Mrows * B).is_zero_matrix)
    out["kernel"]["span_equal"] = bool(B.rank() == K.rank() == sp.Matrix.hstack(B, K).rank())
    print(json.dumps(out["anomalies"]), "| census:", len(terms), out["census"], flush=True)
    print("kernel:", out["kernel"], flush=True)
    its = items()
    xcap = max(abs(i[1]) for i in its)
    layers = dp(its, 60, xcap)
    rows = {}
    for d in range(5, 31):
        cands = []
        v0 = layers[2 * d].get((0, 0, 0, 0))
        if v0 is not None:
            cands.append(v0 - 4 * (d - 4))
        v1 = layers[2 * d - 2].get((0, 0, 1, 1))
        if v1 is not None:
            cands.append(v1 - 4 * (d - 4))
        rows[d] = max(cands) if cands else None
    out["dp_max_excess_x4"] = rows
    out["dp_max_d<=20"] = max(v for d, v in rows.items() if d <= 20 and v is not None)
    out["dp_max_d<=30"] = max(v for v in rows.values() if v is not None)
    out["tight_d"] = [d for d, v in rows.items() if v == 0]
    bf = brute(its, 8)
    out["brute_d<=8"] = bf
    out["dp_vs_brute_agree"] = all(rows[d] == bf.get(d) for d in range(5, 9))
    print("DP rows:", rows, flush=True)
    print("max d<=20:", out["dp_max_d<=20"], "max d<=30:", out["dp_max_d<=30"], "tight:", out["tight_d"],
          "brute agree:", out["dp_vs_brute_agree"], flush=True)
    (HERE / "sk_d1.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
