"""K0b: complete exact/NUM dossier of one candidate fermion content.
Usage: verify_candidate.py <spec.json> [out_prefix] [dim_enum]
spec.json: {"label": ..., "fermions": [[name, rep, X, gens], ...]}
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

from k0b_engine import Model, jsonable, label, MPL, CHI

HERE = Path(__file__).resolve().parent
VEV = {"S": 3.0e13, "Phi17": 1.0e17, "Delta": 2.6e13, "Phi210": 2.1e16, "H10": 174.0}
ALPHA2 = 1 / 25.0
HBAR = 6.582e-25  # GeV s
T_UNIVERSE = 4.35e17


def decay_estimates(m, sector_names, qvec_index, M_X=1.0e13):
    """lowest-dimension operators changing the fermion-number charge f_k by one unit (2- and 4-fermion), with
    singlet verification (search the ILP over increasing 'forbidden' sets until a genuine singlet is found),
    and lifetime estimates (EST)."""
    out = {}
    nq = len(m.field_table()[0]["q"])
    for sign in (+1, -1):
        for nf in (2, 4):
            target = [None] * nq
            target[0] = None  # G2 free
            for i in range(1, nq):
                target[i] = 0
            target[qvec_index] = sign
            # restrict fermions to F and the sector's species
            forbid = [n for n in m.fnames if n != "F" and n not in sector_names]
            forbid += [n + "^" for n in forbid]
            best = None
            tries = 0
            extra_forbid = []
            while tries < 12:
                r = m.min_operator(target, forbid=tuple(forbid + extra_forbid), exact_fermions=nf, dim_max=40)
                if r is None:
                    break
                dim, counts, parity = r
                ns = m.is_singlet(counts)
                if ns > 0:
                    best = (dim, counts, parity, ns)
                    break
                # not a singlet: forbid this exact monomial by forbidding one of its labels is too strong;
                # instead raise the dimension floor by re-running with a different parity handled inside; fallback:
                tries += 1
                # crude: forbid the rarest label among the monomial (keeps completeness modulo this heuristic)
                lab = min(counts, key=lambda k: counts[k])
                extra_forbid.append(lab)
            key = "f=%+d,nf=%d" % (sign, nf)
            if best is None:
                out[key] = None
                continue
            dim, counts, parity, ns = best
            vevs = 1.0
            nscal = 0
            for lab, mult in counts.items():
                base = lab.rstrip("^")
                if base in VEV:
                    vevs *= VEV[base] ** mult
                    nscal += mult
            K = float(dim) - 4
            if nf == 2:
                m_mix = vevs / MPL ** K if nscal else 0.0
                theta = m_mix / M_X
                gamma = theta ** 2 * ALPHA2 * M_X
            else:
                gamma = M_X ** 5 * (vevs / MPL ** K) ** 2 / (192 * math.pi ** 3) / M_X ** 0  # [mixing]^2 M^5 ... dim check below
                # operator coefficient c = vevs / MPL^K has mass dimension 4 - 6 = -2 (4 fermions): c^2 M^5 has dim 1
                gamma = (vevs / MPL ** K) ** 2 * M_X ** 5 / (192 * math.pi ** 3)
            tau = HBAR / gamma if gamma > 0 else float("inf")
            out[key] = {"dimension": str(dim), "operator": label(counts), "singlets": ns, "heuristic_forbids": extra_forbid,
                        "Gamma_GeV": gamma, "tau_s": tau, "tau_over_age": tau / T_UNIVERSE}
    return out


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    prefix = sys.argv[2] if len(sys.argv) > 2 else Path(sys.argv[1]).stem
    dim_enum = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    m = Model([tuple(f) for f in spec["fermions"]], spec.get("label", prefix))
    rep = {"label": m.label, "fermions": m.fermions}
    t0 = time.time()
    rep["anomalies"] = m.anomalies()
    t_s = sum(Fr(g) * {1: 0, 10: 1, 16: 2}[abs(r)] for n, r, x, g in m.fermions if n != "F" and spec.get("sector", {}).get(n, "S") == "S")
    t_phi = sum(Fr(g) * {1: 0, 10: 1, 16: 2}[abs(r)] for n, r, x, g in m.fermions if spec.get("sector", {}).get(n, "S") == "Phi")
    rep["T_S"] = t_s
    rep["T_Phi"] = t_phi
    terms = m.renormalizable_terms()
    rep["renormalizable_terms"] = [".".join(t["fermions"]) + "." + t["scalar"] + " [%s]" % t["gens"] for t in terms]
    rep["n_terms"] = len(terms)
    rep["bare_masses"] = [".".join(t["fermions"]) for t in m.bare_masses()]
    rep["phi210_yukawas"] = [".".join(t["fermions"]) for t in m.phi210_yukawas()]
    rep["family_exotic_yukawas"] = [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()]
    k = m.compute_kernel()
    rep["kernel"] = {"rank": k["rank"], "dim": k["dim"], "scalar_rank": k["scalar_rank"], "span_ok": k["span_ok"],
                     "names": k["names"], "G2": [int(e) for e in k["G2"]] if k["G2"] is not None else None,
                     "fermion_only": [[int(e) for e in v] for v in k["fonly"]]}
    rep["pq"] = m.pq_data()
    # dual bound, full certification
    log = []
    db = m.dual_bound(dim_max=20, early_stop_below=0.0, log=log, max_iter=2000)
    rep["dual_bound_dim20"] = {"bound": db["bound"], "certified": db["certified"], "reason": db.get("reason"),
                               "mu": db.get("mu"), "iterations": db.get("iterations"),
                               "cuts": [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log]}
    print("dual bound (dim<=20): %s certified %s after %s iterations (%.0fs)" % (db["bound"], db["certified"], db.get("iterations"), time.time() - t0), flush=True)
    if db["certified"]:
        # robustness: the same mu against monomials up to dim 24 and 28
        for dmax in (24, 28):
            o = m.oracle(db["mu"], dim_max=dmax)
            rep["dual_bound_dim20"]["oracle_check_dim%d" % dmax] = {"min_cost_minus_mu_q": o["value"] if o else None, "op": o["counts"] if o else None}
            print("  oracle check dim<=%d: min(cost - mu.q) = %s at %s" % (dmax, o["value"] if o else None, o["counts"] if o else None), flush=True)
    # explicit closures (K0 integer program)
    t1 = time.time()
    ops, ncand = m.enumerate_operators(dim_max=dim_enum, max_fermions=4, max_210=1)
    rep["explicit_operators"] = {"dim_max": dim_enum, "centre_consistent": ncand, "verified_singlets": len(ops),
                                 "by_dimension": {}}
    for op in ops:
        rep["explicit_operators"]["by_dimension"][str(op["dim"])] = rep["explicit_operators"]["by_dimension"].get(str(op["dim"]), 0) + 1
    rep["explicit_operators"]["dim5_dim6_list"] = [label(op["counts"]) + " (dim %s, q=%s)" % (op["dim"], op["q"]) for op in ops if op["dim"] <= 6]
    best = None
    for g2 in (4, -4):
        r = m.closure_ilp(ops, g2_target=g2, max_ops=16)
        if r and (best is None or r["K"] < best["K"]):
            best = r
    if best is None:
        rep["explicit_closure"] = {"found": False, "note": "no PQ-violating closure with <= 16 Planck operators of dim <= %d and <= 4 fermions" % dim_enum}
    else:
        d = m.describe(best, ops)
        est = {}
        for sigma in (3.0e13, 3.29e13):
            est["<S>=%.3g" % sigma] = m.estimate(d, sigma=sigma)
        rep["explicit_closure"] = {"found": True, **d, "nda": est}
    print("explicit operators dim<=%d: %d verified of %d; cheapest closure K = %s (%.0fs)" % (
        dim_enum, len(ops), ncand, None if best is None else best["K"], time.time() - t1), flush=True)
    # tree-level quality numbers
    q = {}
    for sigma in (3.0e13, 3.29e13, 3.6e13):
        q["<S>=%.3g" % sigma] = 2 * (1e17 / MPL) ** 4 * (sigma / MPL) ** 17 * MPL ** 4 / CHI
    rep["dtheta_tree_dim21_coeff2"] = q
    rep["<S>_max_for_dtheta_1e-10"] = MPL * (1e-10 * CHI / (2 * 1e17 ** 4)) ** (1 / 17)
    # decays
    rep["R_parity"] = m.r_parity()
    names = k["names"]
    dec = {}
    for i, v in enumerate(k["fonly"]):
        sector = [n for j, n in enumerate(m.fnames) if v[j] != 0]
        dec["f%d %s" % (i + 1, sector)] = decay_estimates(m, sector, i + 1)
    rep["decay_operators"] = dec
    rep["seconds"] = time.time() - t0
    (HERE / (prefix + "_dossier.json")).write_text(json.dumps(jsonable(rep), indent=1), encoding="utf-8")
    print(json.dumps(jsonable({k2: v for k2, v in rep.items() if k2 not in ("dual_bound_dim20", "explicit_operators", "renormalizable_terms")}), indent=1)[:6000])
    print("terms:", rep["renormalizable_terms"])
    print("cuts used:", len(rep["dual_bound_dim20"]["cuts"]))


if __name__ == "__main__":
    main()
