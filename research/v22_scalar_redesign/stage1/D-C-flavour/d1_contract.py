"""D1 (contract) for the D-C-flavour designs: exact anomaly arithmetic + exact quality DP (K_min) per variant.

Variants (scalar content changes only; the B63 fermion sector is kept verbatim):
  V1  A1-EFT     : no new field (Phi210, Delta126bar, H10, S, Phi17)            -> DP must reproduce K_min = 17
  V2  A2-EFT     : + 45_H  (X = 0, real, centre class z0, accidental q = 0)
  V3  A1+120_H   : + 120_H (X = -2, complex, z2, q = 0; Yukawas F.F.120, Vb2.Vb3.120 duplicate the H10 structures)
The DP (dp_core.py = verbatim copy of R2-V dual_dp.py) maximises 4[mu.q(O) - (d(O)-4)] over ALL monomials in the
fermion items, their conjugates and the scalar items, subject to X = 0, centre z = 0 mod 4 and Lorentz parity; the
certificate K_min >= 17 holds iff the maximum is <= 0 for every 5 <= d <= 20.  For each variant we also re-run the own
cutting-plane LP (DP oracle) that maximises mu_0, i.e. the LP-optimal certificate value 4 mu_0, and brute force d <= 7.
An added scalar enters the DP as an extra item (X, z, q); a scalar whose (X, z, q) equals an existing item cannot change
any DP value (EXACT: identical item columns) -- the run is done anyway as a check.
"""
from __future__ import annotations

import json
import time
from fractions import Fraction as Fr
from pathlib import Path

import dp_core as D

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------------------------- anomalies (EXACT)
# Weyl species (rep dim with sign for conjugate, X, multiplicity); T(16)=2, T(10)=1, T(1)=0 (SO(10) index, 10 -> 1)
SPECIES = [("F", 16, 1, 3), ("V1", 16, -35, 2), ("Vb1", -16, 39, 1), ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
           ("V3", 16, 34, 1), ("Vb3", -16, -30, 1), ("T", 10, 2, 2), ("Pb", -16, 18, 1), ("N1", 1, -63, 1),
           ("N1b", 1, 59, 1), ("N2", 1, -58, 1), ("N2b", 1, 54, 1), ("N3", 1, -57, 1), ("N3b", 1, 61, 1),
           ("NMm", 1, -2, 2)]
TIDX = {16: Fr(2), 10: Fr(1), 1: Fr(0)}


def anomalies():
    a2x = sum(TIDX[abs(r)] * x * m for _n, r, x, m in SPECIES)
    x3 = sum(abs(r) * Fr(x) ** 3 * m for _n, r, x, m in SPECIES)
    gx = sum(abs(r) * x * m for _n, r, x, m in SPECIES)
    net16 = sum((1 if r == 16 else -1 if r == -16 else 0) * m for _n, r, _x, m in SPECIES)
    # Witten-type global anomaly: SO(10) has none (pi_4(SO(10)) = 0); U(1)_X^3/grav are the only abelian ones.
    return {"[SO(10)]^2 X": str(a2x), "X^3": str(x3), "grav-X": str(gx), "net 16-16bar": net16,
            "all_zero": a2x == 0 and x3 == 0 and gx == 0}


# ----------------------------------------------------------------------------------------------- DP per variant
BASE_SCALARS = list(D.SCALARS)
BASE_Q = dict(D.Q)
BASE_ZC = dict(D.ZC)

VARIANTS = {
    "V1_A1-EFT(no new field)": [],
    "V2_A2-EFT(+45_H,X=0)": [("H45", 45, 0, True)],
    "V3_A1+120_H(X=-2)": [("H120", 120, -2, False)],
}


def set_variant(extra):
    D.SCALARS[:] = BASE_SCALARS + extra
    D.Q.clear(); D.Q.update(BASE_Q)
    D.ZC.clear(); D.ZC.update(BASE_ZC)
    for name, rep, x, real in extra:
        D.Q[name] = (0,) * 6            # no renormalizable coupling to the q-charged fermions/Phi17 (checked below)
        D.ZC[rep] = {45: 0, 120: 2, 16: 1}[rep]


def run_variant(name, extra):
    set_variant(extra)
    t0 = time.time()
    its = D.items()
    xmax = max(abs(i["X"]) for i in its)
    bf = D.brute_force_check(7)
    best, par = D.dp(its, 16, xmax)
    dpv = {}
    for d in range(5, 8):
        c = []
        v0 = int(best[2 * d, xmax, 0, 0, 0])
        if v0 > D.NEG // 2:
            c.append(v0 - 4 * (d - 4))
        v1 = int(best[2 * d - 2, xmax, 0, 1, 1])
        if v1 > D.NEG // 2:
            c.append(v1 - 4 * (d - 4))
        dpv[d] = max(c) if c else None
    cert = D.certificate(30, True, name)
    lp = D.lp_optimum(20)
    out = {"variant": name, "extra_scalars": extra, "n_items": len(its),
           "dp_vs_bruteforce_d<=7": {"dp": dpv, "brute": bf, "agree": all(dpv[d] == bf.get(d) for d in dpv)},
           "max_excess_x4_5<=d<=20": cert["max_excess_x4_over_5<=d<=20"], "at_d": cert["at_d"],
           "argmax_monomial": cert["monomial"], "certificate_holds_d<=20": cert["certificate_holds_d<=20"],
           "max_excess_x4_d<=30": cert["max_excess_x4_over_all_d<=30"],
           "tight_dims": [r["d"] for r in cert["rows"] if r.get("max_excess_x4") == 0],
           "own_LP_4mu0": lp.get("4mu0"), "own_LP_mu": lp.get("mu"), "seconds": time.time() - t0}
    print(json.dumps({k: v for k, v in out.items() if k not in ("own_LP_mu",)}, default=str), flush=True)
    return out


# ------------------------------------------------------------------- renormalizable couplings of the new scalars
def new_yukawa_scan():
    """Which renormalizable fermion bilinears can couple to 45_H (X=0) or 120_H (X=-2)?  16x16bar contains 45 (not
    120); 16x16 and 16bar x 16bar contain 120 (not 45); 10x10 contains 45 (antisymmetric); 1 x anything: no."""
    fer = [(n, r, x) for n, r, x, _m in SPECIES]
    res = {"45_H(X=0)": [], "120_H(X=-2)": []}
    for i, (n1, r1, x1) in enumerate(fer):
        for n2, r2, x2 in fer[i:]:
            pair = {r1, r2} if r1 != r2 else {r1}
            if (r1, r2) in ((16, -16), (-16, 16)) and x1 + x2 == 0:
                res["45_H(X=0)"].append(f"{n1}.{n2}.45")
            if r1 == r2 == 10 and x1 + x2 == 0 and n1 != n2:
                res["45_H(X=0)"].append(f"{n1}.{n2}.45")
            if r1 == r2 == 10 and x1 + x2 == 0 and n1 == n2:
                res["45_H(X=0)"].append(f"{n1}.{n2}.45 (2 copies, antisym)")
            if r1 == r2 and abs(r1) == 16 and x1 + x2 - 2 == 0:
                res["120_H(X=-2)"].append(f"{n1}.{n2}.120")
            if r1 == r2 and abs(r1) == 16 and x1 + x2 + 2 == 0:
                res["120_H(X=-2)"].append(f"{n1}.{n2}.120*")
    return res


def main():
    out = {"anomalies_B63_fermions": anomalies(), "new_scalar_yukawas": new_yukawa_scan(), "variants": {}}
    print(out["anomalies_B63_fermions"], flush=True)
    print(out["new_scalar_yukawas"], flush=True)
    for name, extra in VARIANTS.items():
        out["variants"][name] = run_variant(name, extra)
    set_variant([])
    (HERE / "d1_contract.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
