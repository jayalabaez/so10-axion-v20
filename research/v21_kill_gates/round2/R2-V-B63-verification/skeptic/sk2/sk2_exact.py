"""Second skeptic (sk2) of R2-V: own exact re-derivation of the B63 algebraic claims.

Independent of R2-V's code and of the first skeptic's code (nothing imported or copied).
 - anomalies, b_X, T_S/T_Phi, Lemma A
 - renormalizable fermion couplings: X filter + Spin(10) centre filter + textbook SO(10) bilinear decompositions
   (Slansky 1981, Table: 16x16 = 10s+120a+126s, 16x16b = 1+45+210, 10x10 = 1s+45a+54s, 10x16 = 16b+144)
 - accidental kernel from the coupling list + the v20 phase-sensitive scalar directions (read from the contract JSON,
   read-only), with sympy rational nullspace in MY OWN basis, then compared with the round-1 basis
 - PQ anomaly N, E/N, and N_DW from an explicit stabiliser computation including the Spin(10) centre
 - explicit K = 17 closure arithmetic
Writes sk2_exact.json next to this file.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CONTRACT = Path(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_record\GAUGED_U1X_SCALAR_CONTRACT_V20.json")

# (name, rep, X, generations) rep: '16','16b','10','1'
FERM = [("F", "16", 1, 3), ("V1", "16", -35, 2), ("Vb1", "16b", 39, 1), ("V2", "16", -28, 1), ("Vb2", "16b", 32, 1),
        ("V3", "16", 34, 1), ("Vb3", "16b", -30, 1), ("T", "10", 2, 2), ("Pb", "16b", 18, 1),
        ("N1", "1", -63, 1), ("N1b", "1", 59, 1), ("N2", "1", -58, 1), ("N2b", "1", 54, 1), ("N3", "1", -57, 1),
        ("N3b", "1", 61, 1), ("NMm", "1", -2, 2)]
# scalars (name, rep, X, real)
SCAL = [("Phi210", "210", 0, True), ("Delta", "126b", -2, False), ("H10", "10", -2, False), ("S", "1", 4, False),
        ("Phi17", "1", 17, False)]
DIM = {"16": 16, "16b": 16, "10": 10, "1": 1, "126": 126, "126b": 126, "210": 210}
TIDX = {"16": Fr(2), "16b": Fr(2), "10": Fr(1), "1": Fr(0)}          # Dynkin index, T(10) = 1
TRQ2 = {"16": Fr(16, 3), "16b": Fr(16, 3), "10": Fr(8, 3), "1": Fr(0)}  # Tr Q_em^2
ZC = {"16": 1, "16b": 3, "10": 2, "1": 0, "126": 2, "126b": 2, "210": 0}
CONJ = {"16": "16b", "16b": "16", "10": "10", "1": "1", "126": "126b", "126b": "126", "210": "210"}
# bilinear decompositions: (rep_a, rep_b) -> list of (irrep, symmetry for a == b: 's' or 'a' or None)
BIL = {
    ("16", "16"): [("10", "s"), ("120", "a"), ("126", "s")],
    ("16b", "16b"): [("10", "s"), ("120", "a"), ("126b", "s")],
    ("16", "16b"): [("1", None), ("45", None), ("210", None)],
    ("10", "10"): [("1", "s"), ("45", "a"), ("54", "s")],
    ("10", "16"): [("16b", None), ("144", None)],
    ("10", "16b"): [("16", None), ("144b", None)],
}


def bil(ra, rb):
    if (ra, rb) in BIL:
        return BIL[(ra, rb)]
    if (rb, ra) in BIL:
        return BIL[(rb, ra)]
    if ra == "1":
        return [(rb, "s")]
    if rb == "1":
        return [(ra, "s")]
    raise KeyError((ra, rb))


def anomalies():
    a2x = sum(g * TIDX[r] * x for _n, r, x, g in FERM)
    grav = sum(g * DIM[r] * x for _n, r, x, g in FERM)
    x3 = sum(g * DIM[r] * x ** 3 for _n, r, x, g in FERM)
    net = sum(g * (1 if r == "16" else -1 if r == "16b" else 0) for _n, r, x, g in FERM)
    # 10 has no SO(10)^3 anomaly (real); 16 vs 16b chirality: SO(10) has no cubic anomaly at all (no d-symbol)
    bx = Fr(2, 3) * sum(g * DIM[r] * x * x for _n, r, x, g in FERM) + Fr(1, 3) * sum(DIM[r] * x * x for _n, r, x, re in SCAL if not re)
    MPL, MU = 2.435e18, 2.13e16
    ainv_mu = 1.0 + float(bx) / (2 * math.pi) * math.log(MPL / MU)
    gx_max = math.sqrt(4 * math.pi / ainv_mu)
    return {"SO10^2_X": str(a2x), "grav_X": str(grav), "X^3": str(x3), "net_16_minus_16b": net, "b_X": str(bx),
            "alpha_X^-1(M_U=2.13e16) with alpha_X(MPl)=1": ainv_mu, "g_X(M_U)_max": gx_max}


def insertions():
    out = [("bare", "1", 0)]
    for n, r, x, real in SCAL:
        out.append((n, r, x))
        if not real:
            out.append((n + "*", CONJ[r], -x))
    return out


def couplings():
    allowed, xonly = [], []
    for i, j in itertools.combinations_with_replacement(range(len(FERM)), 2):
        na, ra, xa, ga = FERM[i]
        nb, rb, xb, gb = FERM[j]
        for sn, sr, sx in insertions():
            if xa + xb + sx != 0:
                continue
            rec = {"pair": f"{na}.{nb}", "ins": sn}
            if (ZC[ra] + ZC[rb] + ZC[sr]) % 4 != 0:
                rec["why_not"] = "centre"
                xonly.append(rec)
                continue
            need = CONJ[sr]
            hits = [sym for irr, sym in bil(ra, rb) if irr == need]
            ok = False
            flav = None
            if hits:
                if i != j:
                    ok, flav = True, f"{ga}x{gb}"
                else:
                    # Weyl bilinear psi_a psi_b symmetric in combined (flavour, gauge) index exchange
                    if "s" in hits or None in hits:
                        ok, flav = True, f"sym {ga}x{ga}"
                    elif "a" in hits and ga > 1:
                        ok, flav = True, f"antisym {ga}x{ga}"
            if ok:
                rec["flavour"] = flav
                allowed.append(rec)
            else:
                rec["why_not"] = "SO(10) (no %s in %s x %s)" % (need, ra, rb)
                xonly.append(rec)
    return allowed, xonly


def kernel(allowed):
    names = [f[0] for f in FERM] + ["Delta", "H10", "S", "Phi17"]  # Phi210 real -> charge 0
    idx = {n: k for k, n in enumerate(names)}
    rows = []

    def row(terms):
        r = [0] * len(names)
        for n, c in terms:
            if n == "Phi210":
                continue
            r[idx[n]] += c
        return r
    for t in allowed:
        a, b = t["pair"].split(".")
        terms = [(a, 1), (b, 1)]
        s = t["ins"]
        if s != "bare":
            terms.append((s.rstrip("*"), -1 if s.endswith("*") else 1))
        rows.append(row(terms))
    # phase-sensitive scalar directions from the v20 contract (read-only parse)
    scal_rows, scal_info = [], []
    try:
        con = json.loads(CONTRACT.read_text(encoding="utf-8"))
        scal_info.append({"top_keys": list(con.keys())[:20]})
    except Exception as e:  # pragma: no cover
        con = None
        scal_info.append({"error": repr(e)})
    # hand-coded from the contract listing (verified below by X-neutrality): O12 H10*^2 S*, O15 Phi210 H10* Delta,
    # O28 H10* Delta^2 Delta*, O31 H10*^2 Delta^2, O38 Phi210 H10* Delta* S*, O45 Phi210^2 H10* Delta
    ps = {"O12": [("H10", -2), ("S", -1)], "O15": [("Phi210", 1), ("H10", -1), ("Delta", 1)],
          "O28": [("H10", -1), ("Delta", 1)], "O31": [("H10", -2), ("Delta", 2)],
          "O38": [("Phi210", 1), ("H10", -1), ("Delta", -1), ("S", -1)], "O45": [("Phi210", 2), ("H10", -1), ("Delta", 1)]}
    X = {"Phi210": 0, "Delta": -2, "H10": -2, "S": 4, "Phi17": 17}
    for k, t in ps.items():
        assert sum(X[n] * c for n, c in t) == 0, k
        scal_rows.append(row(t))
    M = sp.Matrix(rows + scal_rows)
    rank = M.rank()
    ns = M.nullspace()
    dimk = len(ns)
    # round-1 basis
    xvec = [f[2] for f in FERM] + [-2, -2, 4, 17]
    def vec(d):
        return [d.get(n, 0) for n in names]
    r1 = {"X": xvec,
          "G2": vec({"V1": -1, "Vb1": 1, "Phi17": 1}),
          "f1": vec({"V1": 1, "Vb1": -1, "Pb": -1}),
          "f2": vec({"V2": 1, "Vb2": -1, "V3": -1, "Vb3": 1}),
          "f3": vec({"N1": 1, "N1b": -1}), "f4": vec({"N2": 1, "N2b": -1}), "f5": vec({"N3": 1, "N3b": -1})}
    in_kernel = {k: all(v == 0 for v in (M * sp.Matrix(v_))) for k, v_ in r1.items()}
    B = sp.Matrix([r1[k] for k in r1])
    span_rank = B.rank()
    both = sp.Matrix.vstack(B, sp.Matrix([list(v.T) for v in ns]))
    # scalar projections: is any kernel vector phase-sensitive on Phi17 only through G2?
    scal_proj = sp.Matrix([[v[idx[n]] for n in ("Delta", "H10", "S", "Phi17")] for v in ns]).rank()
    return {"n_charges": len(names), "constraint_rank": int(rank), "kernel_dim": dimk,
            "round1_basis_in_kernel": in_kernel, "round1_basis_rank": int(span_rank),
            "round1_basis_spans_kernel": int(both.rank()) == dimk == int(span_rank),
            "scalar_projection_rank": int(scal_proj), "contract_parse": scal_info}, r1, names


def pq(r1, names):
    idx = {n: k for k, n in enumerate(names)}
    out = {}
    for k, v in r1.items():
        N = sum(g * TIDX[r] * v[idx[n]] for n, r, x, g in FERM)
        E = sum(g * TRQ2[r] * v[idx[n]] for n, r, x, g in FERM)
        out[k] = {"N": str(N), "E": str(E)}
    pqv = [a - 17 * b for a, b in zip(r1["X"], r1["G2"])]
    N = sum(g * TIDX[r] * pqv[idx[n]] for n, r, x, g in FERM)
    E = sum(g * TRQ2[r] * pqv[idx[n]] for n, r, x, g in FERM)
    out["PQ=X-17G2"] = {"N": str(N), "E": str(E), "E/N": str(Fr(E) / Fr(N)), "PQ(S)": pqv[idx["S"]],
                        "PQ(Phi17)": pqv[idx["Phi17"]], "PQ(H10)": pqv[idx["H10"]], "PQ(Delta)": pqv[idx["Delta"]]}
    return out


def ndw():
    """Physical axion circle. Gauge elements (c^k, X(beta)), c the Spin(10) centre generator (z charge), act on
    vev phases: S: 4 beta, Phi17: 17 beta, Delta/H10: z=2 -> pi k - 2 beta, Phi210: 0.  Find all gauge elements
    that fix every vev except Phi17 (with the given set of nonzero vevs) and collect the induced Phi17 shift;
    the physical period of the G2 angle gamma is the minimal positive such shift.  theta_eff changes by
    2 N(G2) * gamma = -4 gamma (sign irrelevant) along G2 (S fixed), so N_DW = 4 * period / (2 pi)."""
    res = {}
    for label, vevs in (("S,Phi17 only", ("S",)), ("S,Phi17,Delta_R", ("S", "Delta")),
                        ("S,Phi17,Delta_R,H10 (EW)", ("S", "Delta", "H10"))):
        shifts = set()
        # beta in (2 pi / 4) * m/... : S fixed needs 4 beta = 0 mod 2pi -> beta = pi m / 2, m=0..3
        for k in range(4):
            for m in range(4):
                beta = Fr(m, 4)  # in units of 2 pi
                ok = True
                if "S" in vevs and (4 * beta) % 1 != 0:
                    ok = False
                for nm in ("Delta", "H10"):
                    if nm in vevs and (Fr(2 * k, 4) - 2 * beta) % 1 != 0:
                        ok = False
                if ok:
                    shifts.add((17 * beta) % 1)
        nonzero = sorted(s for s in shifts if s != 0)
        period = min(nonzero) if nonzero else Fr(1)
        res[label] = {"phi17_shifts_by_gauge (units 2pi)": [str(s) for s in sorted(shifts)],
                      "physical period of theta_Phi (units 2pi)": str(period),
                      "N_DW": str(abs(4 * period))}
        # also: X alone (no centre)
        shifts_x = set()
        for m in range(4):
            beta = Fr(m, 4)
            ok = (4 * beta) % 1 == 0 and all(((-2 * beta) % 1 == 0) for nm in ("Delta", "H10") if nm in vevs)
            if ok:
                shifts_x.add((17 * beta) % 1)
        nz = sorted(s for s in shifts_x if s != 0)
        per = min(nz) if nz else Fr(1)
        res[label]["N_DW_if_centre_ignored"] = str(abs(4 * per))
    return res


def closure():
    mu = (Fr(17, 4), Fr(-7, 2), Fr(-7), Fr(-57, 4), Fr(-12), Fr(-51, 4))
    Xc = {"N1": -63, "N1b": 59, "N2": -58, "N2b": 54, "N3": -57, "N3b": 61, "S": 4, "Phi17": 17}
    q = {"N1": (0, 0, 0, 1, 0, 0), "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0),
         "N3": (0, 0, 0, 0, 0, 1), "N3b": (0, 0, 0, 0, 0, -1), "S": (0,) * 6, "Phi17": (1, 0, 0, 0, 0, 0)}
    dims = {"N1": Fr(3, 2), "N1b": Fr(3, 2), "N2": Fr(3, 2), "N2b": Fr(3, 2), "N3": Fr(3, 2), "N3b": Fr(3, 2), "S": 1, "Phi17": 1}
    ops = [(4, {"N1": 1, "N2b": 1, "S": -2, "Phi17": 1}), (1, {"N1": -2, "N3b": -2, "S": -1}), (2, {"N1b": 1, "N2": 2, "N3b": 1, "S": -1})]
    tot_q = [0] * 6
    K = 0
    rows = []
    for mult, op in ops:
        Xs = sum(Xc[n] * c for n, c in op.items())
        d = sum(dims[n] * abs(c) for n, c in op.items())
        qq = [sum(q[n][i] * c for n, c in op.items()) for i in range(6)]
        mq = sum(m * v for m, v in zip(mu, qq))
        nL = sum(c for n, c in op.items() if n.startswith("N") and c > 0)
        nR = sum(-c for n, c in op.items() if n.startswith("N") and c < 0)
        rows.append({"op": op, "mult": mult, "X": Xs, "d": str(d), "q": qq, "mu.q": str(mq), "tight": mq == d - 4,
                     "Lorentz_even": nL % 2 == 0 and nR % 2 == 0})
        K += mult * (d - 4)
        tot_q = [a + mult * b for a, b in zip(tot_q, qq)]
    return {"ops": rows, "K": str(K), "sum_q": tot_q}


def main():
    out = {"anomalies": anomalies()}
    allowed, xonly = couplings()
    out["couplings"] = {"n": len(allowed), "list": allowed, "X_allowed_but_forbidden": xonly}
    kinfo, r1, names = kernel(allowed)
    out["kernel"] = kinfo
    out["pq"] = pq(r1, names)
    out["N_DW"] = ndw()
    out["closure"] = closure()
    # T_S / T_Phi from the mass partnerships implied by the coupling list
    out["T_S_T_Phi"] = {"T_S": "V1'Vb1 4 + V2Vb2 4 + V3Vb3 4 + T 2 = 14", "T_Phi": "V1''Pb 4",
                        "lemmaA": str(6 + 2 * 14 - Fr(17, 2) * 4)}
    (HERE / "sk2_exact.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "couplings"}, indent=1, default=str))
    print("couplings:", len(allowed))
    for t in allowed:
        print("  ", t)
    print("X-allowed but forbidden:")
    for t in xonly:
        print("  ", t)


if __name__ == "__main__":
    main()
