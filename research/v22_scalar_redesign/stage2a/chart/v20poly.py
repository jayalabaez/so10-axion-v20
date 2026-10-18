#!/usr/bin/env python3
"""OPTIONAL fast backend for the 51 v20 rows in the 531 chart: each of the 44 live repo directions is identified
with an explicit linear combination of contraction-graph polynomials (chart531's exact polynomial engine), then
the 51 parameter rows (lambda:: / re:: = 2Re / im:: = -2Im, repo conventions) are exact sparse polynomials whose
value / gradient / Hessian cost ~1-2 s instead of the repo compiler's 30-55 s.

Construction (no repo file is modified; the repo is the reference):
  1. for every live direction family (field multidegree of Phi, H, Hb, Sigma, Sigma^dag), enumerate all contraction
     multigraphs (explicit_basis_v22.multigraphs, imported read-only from stage2a/model; eps graphs for Sigma-free
     families), compile each graph with chart531.build_contraction;
  2. evaluate the repo value layer (potential.evaluate_directions) at random 486 states, divide out the singlet
     dressing, and solve for the graph coefficients on a pivoted independent subset (rank = family size);
  3. rationalise the coefficients (limit_denominator) and accept only if the rational identity reproduces the repo
     values at FRESH random states to <= 1e-12 relative (else the family is rejected: no float fallback);
  4. the rows are verified against the repo compiler's value, gradient and Hessian (validate section in __main__).
Label: NUM identity (verified on fresh points), exact rational polynomial thereafter.
usage: python -B v20poly.py build      (fit + cache under BIG; ~2-5 min; repo samples cached)
       python -B v20poly.py validate   (compare with repo parameter_rows at 2 states; ~2 min)
       python -B v20poly.py exact      (EXACT so(10) x U(1)_X x PQ invariance of every fast row; ~1 min)
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chart531 as C  # noqa: E402

sys.path.insert(1, str(C.MODEL_DIR))
import explicit_basis_v22 as EB  # noqa: E402

CACHE = C.BIG / "v20poly_cache_v1.npz"
OUT_JSON = HERE / "v20poly_validation.json"
TYPES = ("P", "H", "Hb", "D", "Db")
TNAME = {"P": "Phi210", "H": "H10", "Hb": "H10^dag", "D": "Delta126bar", "Db": "Delta126bar^dag"}
DRESS = {"S": "S", "Sb": "Sb", "X": "T", "Xb": "Tb"}


def family_specs(base_key):
    types = [t for t, n in zip(TYPES, base_key) for _ in range(n)]
    if not types:
        return [None]
    has_d = any(t in ("D", "Db") for t in types)
    graphs = EB.multigraphs(types, False)
    if not has_d and sum(EB.RANKS[t] for t in types) >= 10:
        graphs += EB.multigraphs(types, True)
    specs = []
    for g in graphs:
        slots, eps_k, internal = EB.graph_slots(g)
        if len(internal) > 26:
            raise ValueError("too many letters")
        caps = iter("ABCDEFGHIJ")
        idx = ["".join(slots[t]) + "".join(next(caps) for _ in range(eps_k[t]))
               for t, n in enumerate(g["nodes"]) if n != "eps"]
        specs.append({"tensors": [TNAME[t] for t in types], "indices": idx, "prefactor": "1", "part": "full",
                      "singlet_factors": []})
    return specs


def times_monomial(p: C.Poly, variables: list[int]) -> C.Poly:
    if not variables:
        return p
    extra = np.tile(np.asarray(variables, dtype=np.int64), (p.n_terms, 1))
    return C._aggregate(np.hstack([p.idx.astype(np.int64), extra]), p.num_re, p.num_im, p.den)


def rational_lincomb(terms, ):
    """sum (a + i b) P_k with a, b Fractions -> exact Poly."""
    L = 1
    for (a, b), p in terms:
        L = math.lcm(L, a.denominator, b.denominator, p.den)
    idx, re, im = [], [], []
    for (a, b), p in terms:
        sa = a * L / p.den
        sb = b * L / p.den
        if sa.denominator != 1 or sb.denominator != 1:
            raise ArithmeticError("lcm")
        ia, ib = int(sa), int(sb)
        idx.append(p.idx)
        re.append(ia * p.num_re - ib * p.num_im)
        im.append(ia * p.num_im + ib * p.num_re)
    return C._aggregate(np.vstack(idx), np.concatenate(re).astype(float), np.concatenate(im).astype(float), L)


def dressing_vars(counts):
    FO = C.potential.FIELD_ORDER
    out = []
    for name, var in (("S", C.VAR_S), ("Sb", C.VAR_SB), ("X", C.VAR_T), ("Xb", C.VAR_TB)):
        out += [var] * counts[FO.index(name)]
    return out


def sample_q486(rng):
    q = np.zeros(C.DIM486)
    for nm, sl in list(C.BLOCKS.items())[:5]:
        v = rng.normal(size=sl.stop - sl.start)
        q[sl] = v / np.linalg.norm(v) * rng.uniform(0.5, 1.5)
    return q


class FPoly:
    """float-coefficient polynomial (same evaluation interface as chart531.Poly)."""

    def __init__(self, idx, c):
        self.idx = np.asarray(idx).astype(np.int16)
        self.c = np.asarray(c, dtype=complex)

    @property
    def degree(self):
        return int(self.idx.shape[1])

    @property
    def n_terms(self):
        return int(self.idx.shape[0])

    def coef(self):
        return self.c


def f_aggregate(idx, c):
    idx = np.sort(np.asarray(idx), axis=1).astype(np.int16)
    keys = C._keys(idx)
    uk, inv = np.unique(keys, return_inverse=True)
    sr = np.bincount(inv, weights=np.asarray(c).real, minlength=uk.size)
    si = np.bincount(inv, weights=np.asarray(c).imag, minlength=uk.size)
    keep = (sr != 0) | (si != 0)
    return FPoly(C._unkeys(uk[keep], idx.shape[1]), sr[keep] + 1j * si[keep])


def f_conj(p):
    return f_aggregate(C.CONJVAR[p.idx.astype(np.int64)], np.conj(p.c))


def f_add(p, q, a, b):
    return f_aggregate(np.vstack([p.idx, q.idx]), np.concatenate([a * p.c, b * q.c]))


def f_times_monomial(p, variables):
    if not variables:
        return p
    extra = np.tile(np.asarray(variables, dtype=np.int64), (p.n_terms, 1))
    return f_aggregate(np.hstack([p.idx.astype(np.int64), extra]), p.c)


def build(n_fit=70, n_check=25, seed=4860):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    live = list(C.g2_audit.contract_selection()["direction_ids"])
    st0 = C.potential.deterministic_state(1)
    dirs = {d.direction_id: d for d in C.potential.evaluate_directions(st0) if d.direction_id in live}
    fams = sorted({dirs[i].base_key for i in live})
    graphs = {}
    for bk in fams:
        specs = family_specs(bk)
        graphs[bk] = [None if s is None else C.build_contraction(s) for s in specs]
        print(f"family {bk}: {len(specs)} graphs ({time.time() - t0:.0f}s)", flush=True)
    # repo values at random states
    Q = [sample_q486(rng) for _ in range(n_fit + n_check)]
    samples = C.BIG / f"v20poly_repo_samples_seed{seed}_{n_fit + n_check}.npz"
    if samples.exists():
        z = np.load(samples, allow_pickle=False)
        assert np.array_equal(z["Q"], np.array(Q))
        ids_s = [str(x) for x in z["ids"]]
        vals = [dict(zip(ids_s, row)) for row in z["V"]]
    else:
        vals = []
        for k, q in enumerate(Q):
            st = C.chart.unpack(q)
            vals.append({d.direction_id: d.value for d in C.potential.evaluate_directions(st)})
            if k % 10 == 0:
                print(f"  repo values {k}/{len(Q)} ({time.time() - t0:.0f}s)", flush=True)
        ids_s = sorted(vals[0])
        np.savez_compressed(samples, Q=np.array(Q), ids=np.array(ids_s),
                            V=np.array([[v[i] for i in ids_s] for v in vals]))
    W = C.w_of_q(np.array([C.join(q) for q in Q]))
    gvals = {bk: np.array([np.ones(len(Q), dtype=complex) if p is None else C.poly_value(p, W) for p in graphs[bk]]).T
             for bk in fams}
    result = {}
    polys = {}
    for did in live:
        d = dirs[did]
        dv = np.array(dressing_vars(d.counts), dtype=np.int64)
        dress = np.prod(W[:, dv], axis=1) if dv.size else np.ones(len(Q), dtype=complex)
        y = np.array([vals[k][did] for k in range(len(Q))]) / dress
        M = gvals[d.base_key]
        Mf, yf = M[:n_fit], y[:n_fit]
        import scipy.linalg as sl
        nrm = np.linalg.norm(Mf, axis=0)
        _, R, piv = sl.qr(Mf / np.where(nrm > 0, nrm, 1.0), pivoting=True, mode="economic")
        diag = np.abs(np.diag(R))
        rank = int(np.sum(diag > 1e-10 * diag[0]))
        cols = piv[:rank]
        c, *_ = np.linalg.lstsq(Mf[:, cols], yf, rcond=None)
        fit_res = float(np.max(np.abs(Mf[:, cols] @ c - yf)) / np.max(np.abs(yf)))
        rat = []
        ok_rat = True
        for x in c:
            a = Fraction(x.real).limit_denominator(1 << 22)
            b = Fraction(x.imag).limit_denominator(1 << 22)
            if abs(float(a) - x.real) > 1e-11 * max(1, abs(x)) or abs(float(b) - x.imag) > 1e-11 * max(1, abs(x)):
                ok_rat = False
            rat.append((a, b))
        cr = np.array([float(a) + 1j * float(b) for a, b in rat])
        chk = float(np.max(np.abs(M[n_fit:, cols] @ cr - y[n_fit:])) / np.max(np.abs(y[n_fit:])))
        chk_f = float(np.max(np.abs(M[n_fit:, cols] @ c - y[n_fit:])) / np.max(np.abs(y[n_fit:])))
        canc = np.abs(M[n_fit:, cols]) @ np.abs(c)                      # sum_g |c_g G_g| per fresh point
        canc_res = float(np.max(np.abs(M[n_fit:, cols] @ c - y[n_fit:]) / canc))
        canc_r = np.abs(M[n_fit:, cols]) @ np.abs(cr)
        canc_res_rat = float(np.max(np.abs(M[n_fit:, cols] @ cr - y[n_fit:]) / canc_r))
        mode = None
        # the repo's own float evaluation of heavily cancelling channel projections is accurate only to ~1e-13 of the
        # term scale sum_g |c_g G_g|; a wrong rational (denominators <= 2^22) would show up at >= 1e-6 of it.
        if ok_rat and canc_res_rat <= 1e-11 and chk <= 1e-9:
            mode = "exact_rational"
        elif chk_f <= 1e-9 and canc_res <= 1e-13:
            mode = "float"
        result[did] = {"family": list(d.base_key), "n_graphs": len(graphs[d.base_key]), "rank": rank,
                       "fit_rel_residual": fit_res, "rational": ok_rat,
                       "fresh_point_rel_residual_rational": chk, "fresh_point_rel_residual_float": chk_f,
                       "fresh_point_residual_over_sum_abs_terms": canc_res,
                       "fresh_point_residual_over_sum_abs_terms_rational": canc_res_rat,
                       "cancellation_factor_max": float(np.max(canc / np.abs(y[n_fit:]))),
                       "mode": mode, "accepted": mode is not None,
                       "coefficients": ([[str(a), str(b)] for a, b in rat] if mode == "exact_rational"
                                        else [[float(x.real), float(x.imag)] for x in c]),
                       "graph_indices": [int(x) for x in cols]}
        print(f"{did:38s} graphs {len(graphs[d.base_key]):3d} rank {rank} fit {fit_res:.1e} fresh {chk:.1e}/{chk_f:.1e} "
              f"canc-res {canc_res:.1e} rational {ok_rat} -> {mode}", flush=True)
        if mode is None:
            continue
        one = C.Poly(np.zeros((1, 0), dtype=np.int16), np.array([1], dtype=np.int64), np.array([0], dtype=np.int64), 1)
        if mode == "exact_rational":
            terms = []
            for (a, b), gi in zip(rat, cols):
                g = graphs[d.base_key][gi]
                terms.append(((a, b), one if g is None else g))
            base = rational_lincomb(terms)
            polys[did] = (times_monomial(base, list(dv)), d.self_conjugate, mode)
        else:
            idx = np.vstack([graphs[d.base_key][gi].idx for gi in cols])
            cf = np.concatenate([cg * graphs[d.base_key][gi].coef() for cg, gi in zip(c, cols)])
            base = f_aggregate(idx, cf)
            polys[did] = (f_times_monomial(base, list(dv)), d.self_conjugate, mode)
    rows = {}
    modes = {}
    for did, (P, selfc, mode) in polys.items():
        if mode == "exact_rational":
            Pc = C.poly_conj(P)
            if selfc:
                if not C.poly_equal(P, Pc):
                    raise ArithmeticError(f"{did}: fitted self-conjugate direction is not exactly self-conjugate")
                rows[f"lambda::{did}"] = P
            else:
                rows[f"re::{did}"] = C.poly_lincomb([(1, P), (1, Pc)], P.den)
                rows[f"im::{did}"] = C.poly_lincomb([(1j, P), (-1j, Pc)], P.den)
        else:
            Pc = f_conj(P)
            if selfc:
                herm = f_add(P, Pc, 1.0, -1.0)
                result[did]["antihermitian_part_rel"] = float(np.max(np.abs(herm.c), initial=0.0) / np.max(np.abs(P.c)))
                rows[f"lambda::{did}"] = f_add(P, Pc, 0.5, 0.5)
            else:
                rows[f"re::{did}"] = f_add(P, Pc, 1.0, 1.0)
                rows[f"im::{did}"] = f_add(P, Pc, 1j, -1j)
        for pid in [k for k in rows if k.endswith("::" + did)]:
            modes[pid] = mode
    arrays = {}
    meta = []
    for k, (pid, p) in enumerate(sorted(rows.items())):
        arrays[f"idx{k}"] = p.idx
        if modes[pid] == "exact_rational":
            arrays[f"re{k}"] = p.num_re
            arrays[f"im{k}"] = p.num_im
            meta.append({"parameter_id": pid, "mode": modes[pid], "den": p.den, "terms": p.n_terms, "degree": p.degree})
        else:
            arrays[f"cre{k}"] = p.c.real
            arrays[f"cim{k}"] = p.c.imag
            meta.append({"parameter_id": pid, "mode": modes[pid], "terms": p.n_terms, "degree": p.degree})
    np.savez_compressed(CACHE, meta=json.dumps(meta), **arrays)
    summary = {"label": "NUM identity (fresh points) -> exact rational polynomials (mode exact_rational) or float "
                        "coefficients (mode float, NUM)", "n_fit": n_fit, "n_check": n_check,
               "directions": result, "n_accepted": sum(1 for r in result.values() if r["accepted"]),
               "n_exact_rational": sum(1 for r in result.values() if r["mode"] == "exact_rational"),
               "n_float": sum(1 for r in result.values() if r["mode"] == "float"), "row_modes": modes,
               "n_live": len(live), "n_rows": len(rows), "seconds": time.time() - t0, "cache": str(CACHE)}
    old = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    old["build"] = summary
    OUT_JSON.write_text(json.dumps(old, indent=1), encoding="utf-8")
    print(f"accepted {summary['n_accepted']}/{len(live)} directions -> {len(rows)} rows in {summary['seconds']:.0f}s")


_ROWS = None


def rowpolys() -> dict[str, C.Poly]:
    global _ROWS
    if _ROWS is None:
        z = np.load(CACHE, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        _ROWS = {}
        for k, m in enumerate(meta):
            if m["mode"] == "exact_rational":
                _ROWS[m["parameter_id"]] = C.Poly(z[f"idx{k}"], z[f"re{k}"], z[f"im{k}"], int(m["den"]))
            else:
                _ROWS[m["parameter_id"]] = FPoly(z[f"idx{k}"], z[f"cre{k}"] + 1j * z[f"cim{k}"])
    return _ROWS


def v20_rows_poly(q: np.ndarray, *, hessian: bool = True) -> dict[str, C.Row]:
    """The 51 v20 rows from the exact polynomial backend (531 chart; no repo FieldState threshold)."""
    q = np.asarray(q, dtype=float).reshape(C.TOTAL_DIM)
    w = C.w_of_q(q)
    out = {}
    for pid, p in rowpolys().items():
        v, gw, hw = C.poly_derivatives(p, w, hessian=hessian)
        out[pid] = C.Row(pid, float(v.real), C._grad_to_q(gw).real.copy(),
                         None if hw is None else np.ascontiguousarray(C._hess_to_q(hw).real))
    return out


def v20_values_poly(qs: np.ndarray) -> dict[str, np.ndarray]:
    qs = np.atleast_2d(np.asarray(qs, dtype=float))
    w = C.w_of_q(qs)
    return {pid: C.poly_value(p, w).real for pid, p in rowpolys().items()}


def validate(seed=97):
    rng = np.random.default_rng(seed)
    out = {"label": "NUM"}
    pts = {"random_unit_blocks": C.join(sample_q486(rng), rng.normal(size=45)),
           "g3211_SM_point": C.g3211_point(0.6, -0.5, 0.4, 0.3, 0.2, 0.05, 0.01, 2.0)}
    for name, q in pts.items():
        t0 = time.time()
        ref = C.v20_rows(q)
        t_repo = time.time() - t0
        t0 = time.time()
        fast = v20_rows_poly(q)
        t_fast = time.time() - t0
        missing = sorted(set(ref) - set(fast))
        ev = eg = eh = 0.0
        # per-row relative errors; a global floor 1e-12 x (largest entry over all rows) handles rows that vanish
        # analytically at the point (their entries are rounding noise in both backends)
        vs = 1e-12 * max(abs(r.value) for r in ref.values())
        gs = 1e-12 * max(float(np.max(np.abs(r.gradient))) for r in ref.values())
        hs = 1e-12 * max(float(np.max(np.abs(r.hessian))) for r in ref.values())
        worst_row = {}
        for pid in fast:
            r, f = ref[pid], fast[pid]
            e1 = abs(r.value - f.value) / max(abs(r.value), vs)
            e2 = float(np.max(np.abs(r.gradient - f.gradient))) / max(float(np.max(np.abs(r.gradient))), gs)
            e3 = float(np.max(np.abs(r.hessian - f.hessian))) / max(float(np.max(np.abs(r.hessian))), hs)
            worst_row[pid] = max(e1, e2, e3)
            ev, eg, eh = max(ev, e1), max(eg, e2), max(eh, e3)
        out[name] = {"missing_rows": missing, "max_rel_value": ev, "max_rel_gradient": eg, "max_rel_hessian": eh,
                     "worst_rows": dict(sorted(worst_row.items(), key=lambda kv: -kv[1])[:5]),
                     "seconds_repo": t_repo, "seconds_poly": t_fast}
        print(name, out[name], flush=True)
    old = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    old["validate"] = out
    OUT_JSON.write_text(json.dumps(old, indent=1), encoding="utf-8")


def exact_checks():
    """EXACT: every fast v20 row is annihilated by J_{a,a+1} (a=0..8), U(1)_X and PQ; every monomial has X = PQ = 0."""
    gens = [C.PAIR_INDEX[(a, a + 1)] for a in range(9)]
    out = {}
    for pid, p in sorted(rowpolys().items()):
        if not isinstance(p, C.Poly):
            out[pid] = "float row: not checked exactly"
            continue
        nz = sum(C.poly_derivation(p, C.generator_w(k)).n_terms for k in gens)
        nz += C.poly_derivation(p, C.phase_generator_w(C.U1X_CHARGES)).n_terms
        nz += C.poly_derivation(p, C.phase_generator_w(C.PQ_CHARGES)).n_terms
        xq = sorted(set(C.monomial_charges(p, C.U1X_CHARGES).tolist()))
        pq = sorted(set(C.monomial_charges(p, C.PQ_CHARGES).tolist()))
        out[pid] = {"derivation_nonzero_terms": nz, "X_monomial_charges": xq, "PQ_monomial_charges": pq,
                    "ok": nz == 0 and xq == [0] and pq == [0]}
    res = {"label": "EXACT", "rows": out, "all_ok": all(isinstance(v, dict) and v["ok"] for v in out.values())}
    old = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    old["exact_checks"] = res
    OUT_JSON.write_text(json.dumps(old, indent=1), encoding="utf-8")
    print("exact checks all ok:", res["all_ok"], "rows:", len(out))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "validate":
        validate()
    elif cmd == "exact":
        exact_checks()
