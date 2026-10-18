"""D-B-symmetry, criterion D1 (contract) for the design variants.

V1 ('two-10 split'): B63 fermions unchanged; scalars Phi210 (X=0, real), Delta126bar (-2), H1 = H10 (-2),
H2 = second complex 10 (-2), S (4), Phi17 (17).  Re-derives, with H2 included:
  (a) anomalies ([SO(10)]^2 X, X^3, grav-X) - exact Fractions (fermions unchanged, recomputed anyway);
  (b) the renormalizable fermion couplings with the H2 insertion (exact SO(10) singlet counting, so10_chars.py);
  (c) the accidental kernel with every phase-sensitive renormalizable scalar term that contains H2
      (kappa H_a H_b S, Phi H_a* Delta, Phi H_a* Delta* S*, Delta^2 H_a* H_b*, H_a* Delta^2 Delta*, H1* H2 (mass), ...);
  (d) PQ = X - 17 G2, N, E/N, N_DW (unchanged iff H2 carries the H1 accidental charges);
  (e) the exact quality certificate: integer DP (dual_dp.py, copied unedited) and HiGHS MILP + own LP column
      generation (sk_milp.py, copied unedited) with the H2 item added -> K_min.
V2 ('texture Z_n'): a family-dependent Z_n is NOT gauged (no new field); its effect on the DP is nil (DP counts
SO(10) x U(1)_X singlets); the discrete-anomaly status is reported separately in v2_textures.py.
Writes d1_contract.json (small).
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import so10_chars as so            # noqa: E402  (copied unedited from R2-V)
import b63_verify as bv            # noqa: E402  (copied unedited from R2-V)
import dual_dp as ddp              # noqa: E402  (copied unedited from R2-V)
import sk_milp as skm              # noqa: E402  (copied unedited from R2-V skeptic)


def anomalies_v1():
    # fermion content is unchanged by V1 (H2 is a scalar) -> recompute with the R2-V routine
    return bv.anomalies()


def couplings_v1():
    """Renormalizable fermion structures with the extra scalar H2 (10, X=-2)."""
    bv.SCALARS = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
                  ("Phi17", 1, 17, False), ("H2", 10, -2, False)]
    c = bv.couplings()
    return c


def kernel_v1(terms):
    names = [f[0] for f in bv.FERMIONS] + ["H10", "H2", "Delta", "S", "Phi17"]
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    rows, labels = [], []
    for t in terms:
        row = [0] * n
        for f in t["fermions"]:
            row[idx[f]] += 1
        s = t["insertion"]
        if s not in ("mass", "Phi210"):
            if s.startswith("conj["):
                row[idx[s[5:-1]]] -= 1
            else:
                row[idx[s]] += 1
        rows.append(row)
        labels.append(".".join(t["fermions"]) + "." + s)
    h1, h2, d, s_ = idx["H10"], idx["H2"], idx["Delta"], idx["S"]
    # phase-sensitive renormalizable scalar terms (each is an SO(10) singlet; checked below with so10_chars)
    scal = [("kappa11 H1.H1.S", {h1: 2, s_: 1}, [10, 10]),
            ("kappa12 H1.H2.S", {h1: 1, h2: 1, s_: 1}, [10, 10]),
            ("kappa22 H2.H2.S", {h2: 2, s_: 1}, [10, 10]),
            ("m12^2 conj[H1].H2", {h1: -1, h2: 1}, [10, 10]),
            ("Phi210.conj[H1].Delta (O15)", {h1: -1, d: 1}, [210, 10, -126]),
            ("Phi210.conj[H2].Delta (O15')", {h2: -1, d: 1}, [210, 10, -126]),
            ("Phi210.conj[H2].conj[Delta].conj[S] (O38')", {h2: -1, d: -1, s_: -1}, [210, 10, 126]),
            ("Delta^2.conj[H1].conj[H2] (O31')", {d: 2, h1: -1, h2: -1}, [-126, -126, 10, 10]),
            ("Delta^2.conj[H2]^2 (O31'')", {d: 2, h2: -2}, [-126, -126, 10, 10]),
            ("conj[H2].Delta^2.conj[Delta] (O28')", {h2: -1, d: 1}, [10, -126, -126, 126]),
            ("conj[H1]H2 Phi210^2 (portal mixing)", {h1: -1, h2: 1}, [10, 10, 210, 210])]
    scal_info = {}
    for lab, cf, reps in scal:
        row = [0] * n
        for k, v in cf.items():
            row[k] = v
        rows.append(row)
        labels.append(lab)
        scal_info[lab] = so.singlets_of(reps)
    # the original v20 phase-sensitive rows (as in R2-V)
    for lab, cf in [("kappaH H10.H10.S", {h1: 2, s_: 1}), ("Phi210.conj[H10].Delta", {h1: -1, d: 1}),
                    ("O38", {h1: -1, d: -1, s_: -1}), ("Delta^2.conj[H10]^2", {d: 2, h1: -2})]:
        row = [0] * n
        for k, v in cf.items():
            row[k] = v
        rows.append(row)
        labels.append(lab)
    null, rank = bv.nullspace_fr(rows, n)
    xvec = [Fr(f[2]) for f in bv.FERMIONS] + [Fr(-2), Fr(-2), Fr(-2), Fr(4), Fr(17)]
    x_in = all(sum(Fr(r[k]) * xvec[k] for k in range(n)) == 0 for r in rows)
    # H2 charge equals H1 charge on the whole kernel?
    h2_eq_h1 = all(v[h1] == v[h2] for v in null)
    scal_rank = bv.rank_fr([v[len(bv.FERMIONS):] for v in null], 5)
    return {"n_charges": n, "constraint_rank": rank, "kernel_dim": len(null), "X_in_kernel": x_in,
            "H2_charge_equals_H1_charge_on_kernel": h2_eq_h1, "scalar_projection_rank": scal_rank,
            "new_scalar_terms_SO10_singlets": scal_info}


def dp_v1():
    ddp.SCALARS = list(ddp.SCALARS) + [("H2", 10, -2, False)]
    ddp.Q = dict(ddp.Q); ddp.Q["H2"] = (0, 0, 0, 0, 0, 0)
    t0 = time.time()
    cert = ddp.certificate(30, True, "V1 oracle set (X=0, centre, Lorentz) with H2")
    nc = ddp.certificate(24, False, "V1 superset without centre")
    lp = ddp.lp_optimum(20)
    return {"certificate": {k: v for k, v in cert.items() if k != "rows"},
            "rows_excess": {r["d"]: r.get("max_excess_x4") for r in cert["rows"]},
            "no_centre": {k: v for k, v in nc.items() if k != "rows"},
            "own_lp_4mu0": lp, "seconds": time.time() - t0}


def milp_v1():
    skm.SCA = list(skm.SCA) + [("H2", 10, -2, False)]
    skm.ITEMS = skm.build_items(); skm.NI = len(skm.ITEMS)
    out = {}
    for mode, dmin, dmax in (("oracle", 5, 22), ("dressed", 1, 22)):
        rows, worst = skm.certificate(skm.MU4, mode, dmin, dmax)
        out[mode] = {"worst_d_ge_5": worst, "holds": bool(worst["excess4"] <= 0),
                     "all_exact_ok": all(r.get("exact_ok", True) for r in rows)}
    out["lp_colgen_dressed_4mu0"] = skm.lp_colgen("dressed", 20)
    return out


def main():
    out = {"design": "V1 two-10 split: + H2 = 10_H(X=-2)"}
    out["anomalies"] = anomalies_v1()
    c = couplings_v1()
    out["n_structures"] = c["n_structures"]
    out["structures"] = [".".join(t["fermions"]) + "." + t["insertion"] for t in c["terms"]]
    k = kernel_v1(c["terms"])
    out["kernel"] = k
    print("anomalies:", {kk: out["anomalies"][kk] for kk in ("SO10^2_X", "grav_X", "X^3", "all_zero")}, flush=True)
    print("structures (%d):" % c["n_structures"], out["structures"], flush=True)
    print("kernel:", k, flush=True)
    out["dp"] = dp_v1()
    print("DP:", json.dumps(out["dp"]["certificate"], default=str), flush=True)
    print("DP own LP:", out["dp"]["own_lp_4mu0"], flush=True)
    out["milp"] = milp_v1()
    print("MILP:", json.dumps({m: {kk: out["milp"][m][kk] for kk in ("holds", "all_exact_ok")} for m in ("oracle", "dressed")}),
          "colgen:", out["milp"]["lp_colgen_dressed_4mu0"], flush=True)
    (HERE / "d1_contract.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
