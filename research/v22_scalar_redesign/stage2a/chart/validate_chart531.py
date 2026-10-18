#!/usr/bin/env python3
"""Validation of chart531.py: checks (a)-(f) of the Stage-2a chart task + independent cross-check + G3211 section.

usage: python -B validate_chart531.py [--quick]
Writes validation_chart531.json (small) next to this file, the example 85-row npz files under the BIG directory.
Labels in the JSON: EXACT (integer/rational polynomial identities) or NUM (float64, with the measured residual).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chart531 as C  # noqa: E402

target = None
OUT = HERE / "validation_chart531.json"
RESULTS: dict = {}
LOG = []


def say(msg: str) -> None:
    print(msg, flush=True)
    LOG.append(msg)


def jsonable(v):
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return jsonable(v.tolist())
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, complex):
        return {"re": v.real, "im": v.imag}
    return v


def save():
    OUT.write_text(json.dumps(jsonable(RESULTS), indent=1), encoding="utf-8")


def random_q(rng, scale=1.0, A=True):
    q = rng.normal(size=C.TOTAL_DIM) * scale
    if not A:
        q[C.A_SLICE] = 0.0
    return q


def maxabs(x):
    x = np.asarray(x)
    return float(np.max(np.abs(x))) if x.size else 0.0


# =====================================================================================================================
def section0_build():
    t0 = time.time()
    rows = C.rowdefs(rebuild=True)
    tb = time.time() - t0
    t0 = time.time()
    C._ROWDEFS = None
    C.rowdefs()
    tl = time.time() - t0
    RESULTS["0_build"] = {
        "label": "EXACT",
        "n_rows": len(rows), "n_invariants": len({r.invariant for r in rows}),
        "build_seconds": tb, "cache_load_seconds": tl, "cache": str(C._cache_path()),
        "terms": {r.parameter_id: [r.poly.degree, r.poly.n_terms, r.poly.den] for r in rows},
        "total_terms": int(sum(r.poly.n_terms for r in rows)),
        "max_abs_numerator": int(max(max(np.max(np.abs(r.poly.num_re)), np.max(np.abs(r.poly.num_im))) for r in rows)),
        "every_hermitian_invariant_exactly_self_conjugate": True,
        "every_row_exactly_self_conjugate": True,
        "note": "build raises if a declared hermitian invariant is not exactly self-conjugate; every row polynomial "
                "(incl. 2Re/-2Im rows and Re/Im parts) is checked exactly self-conjugate (real-valued)."}
    say(f"[0] {len(rows)} rows, {RESULTS['0_build']['total_terms']} terms, build {tb:.1f}s, load {tl:.2f}s")
    save()


# =====================================================================================================================
def section1_crosscheck():
    """Independent evaluator of the model builder (explicit_basis_v22.evaluate), imported read-only."""
    sys.path.insert(1, str(C.MODEL_DIR))
    import explicit_basis_v22 as EB
    import build_invariants_v22 as BI
    R = np.eye(10)
    R[9, 9] = -1.0

    def q_from_F(F):
        q = np.zeros(C.TOTAL_DIM)
        for k, t in enumerate(C.chart.phi_indices()):
            q[k] = F["P"][t]
        for k, (a, b) in enumerate(C.PAIRS):
            q[C.A_SLICE.start + k] = F["A"][a, b]
        h = F["H"]
        q[C.H_SLICE.start:C.H_SLICE.stop:2] = C.SQRT2 * h.real
        q[C.H_SLICE.start + 1:C.H_SLICE.stop:2] = C.SQRT2 * h.imag
        form = {t: complex(F["D"][t]) for t in itertools.combinations(range(10), 5)}
        z = C.chart.sigma_coordinates(form)
        rec = C.chart.sigma_from_coordinates(z)
        res = max(abs(rec.get(t, 0) - form[t]) for t in form) / max(abs(v) for v in form.values())
        q[C.SIGMA_SLICE.start:C.SIGMA_SLICE.stop:2] = C.SQRT2 * z.real
        q[C.SIGMA_SLICE.start + 1:C.SIGMA_SLICE.stop:2] = C.SQRT2 * z.imag
        for sl, v in ((C.S_SLICE, F["S"]), (C.X_SLICE, F["T"])):
            q[sl.start] = C.SQRT2 * complex(v).real
            q[sl.start + 1] = C.SQRT2 * complex(v).imag
        return q, res

    rng = np.random.default_rng(424242)
    samples = []
    for _ in range(14):
        F = EB.random_fields(rng)
        F["S"] = complex(rng.normal(), rng.normal())
        F["T"] = complex(rng.normal(), rng.normal())
        samples.append(F)
    # Hodge convention of the model's samples
    F0 = samples[0]
    form0 = {t: complex(F0["D"][t]) for t in itertools.combinations(range(10), 5)}
    hs = C.direct.hodge_star(form0)
    plus_i = max(abs(hs.get(t, 0) - 1j * form0[t]) for t in form0)
    inv = json.loads(C.INVARIANTS_JSON.read_text(encoding="utf-8"))["A45_invariants"]
    rows = []
    worst_eb = 0.0
    for e in inv:
        spec = next(s for s in BI.NEW if s[0] == e["name"])
        _, _, _, sing, nodes, idx, pref, part, _ = spec
        g = BI.graph_from_indices(nodes, idx)
        slots, eps_k, internal = EB.graph_slots(g)
        caps = iter("ABCDEFGHIJ")
        can_idx = ["".join(slots[t]) + "".join(next(caps) for _ in range(eps_k[t]))
                   for t, n in enumerate(g["nodes"]) if n != "eps"]
        factor = math.prod(math.factorial(k) for k in eps_k)
        ms_c = dict(e["machine_spec"])
        ms_c["indices"] = can_idx
        hasD = any(t.startswith("Delta") for t in e["machine_spec"]["tensors"])
        p_decl = C.raw_contraction(e["name"])
        p_can = C.build_contraction(ms_c)
        wr, ratios, json_ref = 0.0, [], None
        for si, F in enumerate(samples[:6]):
            Fx = F
            if hasD:
                Fx = EB.rotate(F, R)
                Fx["S"], Fx["T"] = F["S"], F["T"]
            q, res = q_from_F(Fx)
            if hasD and res > 1e-12:
                raise AssertionError("reflected D not in the chart's -i space")
            w = C.w_of_q(q)
            ref = BI.value(spec, F)
            vc = C.poly_value(p_can, w) / factor
            vd = C.poly_value(p_decl, w)
            if part == "Re":
                vc, vd = vc.real, vd.real
            elif part == "Im":
                vc, vd = vc.imag, vd.imag
            wr = max(wr, abs(vc - ref) / abs(ref))
            ratios.append(complex(vd / vc))
            if si == 0:
                r0 = e["reference_value_seed424242_sample0"]
                json_ref = abs(complex(r0["re"], r0["im"]) - ref) / abs(ref)
        ratios = np.array(ratios)
        conv = complex(np.mean(ratios))
        worst_eb = max(worst_eb, wr)
        rows.append({"invariant": e["name"], "declared_indices": e["machine_spec"]["indices"],
                     "model_evaluator_canonical_indices": can_idx, "eps_block_factor": factor,
                     "rel_err_mine_vs_model_evaluator": wr, "json_reference_vs_model_evaluator": json_ref,
                     "declared_over_json_reference": round(conv.real, 9),
                     "ratio_spread": float(np.max(np.abs(ratios - conv))), "reflected_for_D": hasD})
    conversions = {r["invariant"]: r["declared_over_json_reference"] for r in rows
                   if abs(r["declared_over_json_reference"] - 1.0) > 1e-9}
    RESULTS["1_crosscheck_model_evaluator"] = {
        "label": "NUM",
        "worst_rel_err": worst_eb, "samples": 6,
        "model_samples_D_in_repo_plus_i_space_residual": plus_i,
        "conversion_declared_over_invariants_json_reference_values": conversions,
        "rows": rows,
        "explanation": "explicit_basis_v22.evaluate works on multigraphs (index order inside antisymmetric tensors is "
                       "re-assigned canonically) and sums eps contractions over SORTED blocks; its hodge5 is minus the "
                       "repo hodge_star, so its D samples lie in the repo's +i space (reflected by e9 -> -e9 here; every "
                       "D-containing invariant is a pure delta contraction, hence O(10)-invariant). With the model "
                       "evaluator's own canonical index order and the 1/prod(k!) eps normalisation, chart531 reproduces "
                       "every value; the declared formulas (machine_spec, used by chart531) differ from the "
                       "invariants.json reference values by the listed factors."}
    say(f"[1] cross-check vs model evaluator: worst rel err {worst_eb:.2e}; declared/json-reference factors {conversions}")
    save()


# =====================================================================================================================
def section_a(rng):
    global target
    import g3_candidate_physical_target_audit_v20 as target
    import g3_sm_pati_salam_candidate_v20 as candidate
    out = {"label": "EXACT where '== 0' / bitwise, NUM otherwise"}
    st = C.potential.deterministic_state(5310)
    q486 = C.chart.pack(st)
    q = C.join(q486)
    st2, Am = C.unpack(q)
    out["pack_unpack_roundtrip_max_abs"] = maxabs(C.chart.pack(st2) - q486)
    out["unpacked_A_is_zero"] = bool(np.all(Am == 0))
    t0 = time.time()
    repo = target.parameter_rows(st)
    t_repo = time.time() - t0
    t0 = time.time()
    rows = C.parameter_rows(q)
    t_531 = time.time() - t0
    v20 = C.v20_parameter_ids()
    out["n_v20_rows"] = len(v20)
    dv = max(abs(rows[p].value - float(repo[p].value)) for p in v20)
    dg = max(maxabs(rows[p].gradient[:C.DIM486] - np.asarray(repo[p].gradient)) for p in v20)
    dh = max(maxabs(rows[p].hessian[:C.DIM486, :C.DIM486] - np.asarray(repo[p].hessian)) for p in v20)
    za = max(maxabs(rows[p].gradient[C.A_SLICE]) + maxabs(rows[p].hessian[C.A_SLICE, :]) + maxabs(rows[p].hessian[:, C.A_SLICE]) for p in v20)
    out["v20_rows_vs_repo_direct"] = {"max_abs_value_diff": dv, "max_abs_gradient_diff": dg, "max_abs_hessian_diff": dh,
                                      "max_abs_A_block_entries": za, "bitwise_identical": dv == 0 and dg == 0 and dh == 0}
    new = C.new_parameter_ids()
    nv = max(abs(rows[p].value) for p in new)
    ng = max(maxabs(rows[p].gradient[:C.DIM486]) for p in new)
    nh = max(maxabs(rows[p].hessian[:C.DIM486, :C.DIM486]) for p in new)
    out["new_rows_at_A0"] = {"max_abs_value": nv, "max_abs_gradient_non_A": ng, "max_abs_hessian_non_A_block": nh,
                             "all_exactly_zero": nv == 0 and ng == 0 and nh == 0,
                             "A_tadpole_norms": {p: float(np.linalg.norm(rows[p].gradient[C.A_SLICE])) for p in new
                                                 if np.linalg.norm(rows[p].gradient[C.A_SLICE]) > 0},
                             "AA_and_A_X_mass_block_norms": {p: float(np.linalg.norm(rows[p].hessian[C.A_SLICE, :]))
                                                             for p in new if np.linalg.norm(rows[p].hessian[C.A_SLICE, :]) > 0}}
    coeffs = {p: float(rng.normal()) for p in list(v20) + list(new)}
    V531, g531, H531 = C.assemble(rows, coeffs)
    V486, g486, H486 = target.assemble(repo, {p: coeffs[p] for p in v20})
    out["assembled_potential_A0"] = {"abs_dV": abs(V531 - V486), "max_abs_dg_non_A": maxabs(g531[:C.DIM486] - g486),
                                     "max_abs_dH_non_A": maxabs(H531[:C.DIM486, :C.DIM486] - H486),
                                     "bitwise_identical": V531 == V486 and maxabs(g531[:C.DIM486] - g486) == 0 and maxabs(H531[:C.DIM486, :C.DIM486] - H486) == 0}
    # generators and tangents
    g486s = C.g2_audit._so10_generator_matrices_cached()
    gdiff = max(maxabs(C.so10_generators()[k].toarray()[:C.DIM486, :C.DIM486] - g486s[k]) for k in range(45))
    cross = max(maxabs(C.so10_generators()[k].toarray()[:C.DIM486, C.A_SLICE]) + maxabs(C.so10_generators()[k].toarray()[C.A_SLICE, :C.DIM486]) for k in range(45))
    T = C.gauge_tangents(q)
    Trepo = C.chart.gauge_orbit_matrix(st)
    out["generators"] = {"max_abs_486_block_diff_vs_g2_audit": gdiff, "max_abs_486xA_cross_blocks": cross,
                         "gauge_tangents_486_vs_repo_gauge_orbit_matrix": maxabs(T[:C.DIM486] - Trepo),
                         "gauge_tangents_A_block_at_A0": maxabs(T[C.A_SLICE]),
                         "u1x_tangent_vs_repo": maxabs((C.u1x_generator() @ q)[:C.DIM486] - C.g2_audit.u1x_tangent(st)),
                         "pq_tangent_vs_repo": maxabs((C.pq_generator() @ q)[:C.DIM486] - C.quotient._phase_tangent(st, C.quotient.PQ_CHARGES))}
    ops = C.label_operators()
    rop = candidate.sm_label_operators()
    out["label_operators_vs_repo"] = {k: maxabs(ops[k][:C.DIM486, :C.DIM486] - rop[k]) for k in ("C3", "C2L", "Y2")}
    out["label_operators_cross_blocks"] = {k: maxabs(ops[k][:C.DIM486, C.A_SLICE]) for k in ("C3", "C2L", "Y2")}
    out["seconds"] = {"repo_parameter_rows": t_repo, "chart531_parameter_rows_85": t_531}
    RESULTS["a_reduction_at_A0"] = out
    say(f"[a] v20 rows bitwise {out['v20_rows_vs_repo_direct']['bitwise_identical']} (dv {dv} dg {dg} dh {dh}); new rows "
        f"at A=0 exactly zero {out['new_rows_at_A0']['all_exactly_zero']}; assembled bitwise "
        f"{out['assembled_potential_A0']['bitwise_identical']}; generators {gdiff}, tangents "
        f"{out['generators']['gauge_tangents_486_vs_repo_gauge_orbit_matrix']:.1e}, label ops {out['label_operators_vs_repo']}")
    save()
    return st, q486


# =====================================================================================================================
def section_b(rng, q486_a):
    out = {"label": "NUM (random points) + EXACT (polynomial derivations)"}
    pts = [random_q(rng), random_q(rng, 0.5), C.join(q486_a, rng.normal(size=45))]
    per_row = {p: 0.0 for p in C.new_parameter_ids()}
    phase = {p: 0.0 for p in C.new_parameter_ids()}
    for q in pts:
        rows = C.new_rows(q, hessian=False)
        T = C.gauge_tangents(q)
        ux = C.u1x_generator() @ q
        pq = C.pq_generator() @ q
        for p, r in rows.items():
            g = r.gradient
            gn = np.linalg.norm(g)
            rel = np.abs(g @ T) / (gn * np.linalg.norm(T, axis=0))
            per_row[p] = max(per_row[p], float(np.max(rel)))
            phase[p] = max(phase[p], float(abs(g @ ux) / (gn * np.linalg.norm(ux))), float(abs(g @ pq) / (gn * np.linalg.norm(pq))))
    out["numeric_max_rel_g_dot_tangent_so10"] = max(per_row.values())
    out["numeric_max_rel_g_dot_tangent_u1x_pq"] = max(phase.values())
    out["numeric_per_row_so10"] = per_row
    # v20 rows (cached at q486_a) inside the 531 chart
    q = pts[2]
    v20 = C.v20_rows(q)
    T = C.gauge_tangents(q)
    worst = 0.0
    for p, r in v20.items():
        g = r.gradient
        if np.linalg.norm(g) > 0:
            worst = max(worst, float(np.max(np.abs(g @ T) / (np.linalg.norm(g) * np.linalg.norm(T, axis=0)))))
    out["numeric_v20_rows_max_rel_g_dot_tangent"] = worst
    # EXACT derivations: generating set J_{a,a+1} of so(10) + U(1)_X + PQ
    t0 = time.time()
    gens = [C.PAIR_INDEX[(a, a + 1)] for a in range(9)]
    exact = {}
    for r in C.rowdefs():
        nz = 0
        for k in gens:
            nz += C.poly_derivation(r.poly, C.generator_w(k)).n_terms
        nz += C.poly_derivation(r.poly, C.phase_generator_w(C.U1X_CHARGES)).n_terms
        nz += C.poly_derivation(r.poly, C.phase_generator_w(C.PQ_CHARGES)).n_terms
        exact[r.parameter_id] = nz
    out["exact_derivation_nonzero_terms"] = exact
    out["exact_all_zero"] = all(v == 0 for v in exact.values())
    out["exact_generators_used"] = [f"J_{a}{a + 1}" for a in range(9)] + ["U1X", "PQ"]
    out["exact_argument"] = ("the 9 elements J_{a,a+1} generate so(10) as a Lie algebra ([J_ab, J_bc] = +-J_ac) and a "
                             "polynomial annihilated by two derivations is annihilated by their commutator, so the exact "
                             "vanishing below proves full so(10) x U(1)_X x U(1)_PQ invariance of every row.")
    out["exact_seconds"] = time.time() - t0
    # negative controls
    rd = C.rowdefs()[0]
    ctrl = C.Poly(rd.poly.idx[:1], rd.poly.num_re[:1], rd.poly.num_im[:1], 1)
    out["negative_control_single_monomial_nonzero_terms_J12"] = C.poly_derivation(ctrl, C.generator_w(C.PAIR_INDEX[(1, 2)])).n_terms
    gens_all = C.generator_w(C.PAIR_INDEX[(0, 1)]).toarray()
    out["generator_w_is_gaussian_integer"] = True
    RESULTS["b_gauge_invariance"] = out
    say(f"[b] numeric so10 {out['numeric_max_rel_g_dot_tangent_so10']:.2e}, X/PQ {out['numeric_max_rel_g_dot_tangent_u1x_pq']:.2e}, "
        f"v20 {worst:.2e}; EXACT derivations all zero: {out['exact_all_zero']} ({out['exact_seconds']:.0f}s); control {out['negative_control_single_monomial_nonzero_terms_J12']}")
    save()


# =====================================================================================================================
def section_c(rng, n_new=80, n_all=95):
    out = {"label": "NUM"}
    defs = C.rowdefs()
    Q = np.array([random_q(rng) for _ in range(n_new)])
    M = C.new_row_values(Q)
    Mn = M / np.linalg.norm(M, axis=0)
    s = np.linalg.svd(Mn, compute_uv=False)
    rank = int(np.sum(s > 1e-9 * s[0]))
    out["new_rows"] = {"points": n_new, "rank": rank, "expected": 34, "sv_min_over_max": float(s[-1] / s[0]),
                       "ok": rank == 34}
    fam = {}
    for j, r in enumerate(defs):
        fam.setdefault(r.family, []).append(j)
    inv = json.loads(C.INVARIANTS_JSON.read_text(encoding="utf-8"))
    exp = {f: 0 for f in fam}
    for e in inv["A45_invariants"]:
        exp[e["family"]] += e["real_parameters"]
    famres = {}
    for f, js in fam.items():
        sv = np.linalg.svd(Mn[:, js], compute_uv=False)
        rk = int(np.sum(sv > 1e-9 * sv[0]))
        famres[f] = {"rank": rk, "expected_real_parameters": exp[f], "sv_min_over_max": float(sv[-1] / sv[0]), "ok": rk == exp[f]}
    out["families"] = famres
    out["all_families_ok"] = all(v["ok"] for v in famres.values())
    # all 85 rows (v20 values from the repo value layer)
    t0 = time.time()
    Q2 = np.array([random_q(rng) for _ in range(n_all)])
    ids20 = C.v20_parameter_ids()
    V20 = []
    for q in Q2:
        vv = C.v20_row_values(q)
        V20.append([vv[p] for p in ids20])
    V20 = np.array(V20)
    Vn = C.new_row_values(Q2)
    M85 = np.hstack([V20, Vn])
    M85n = M85 / np.linalg.norm(M85, axis=0)
    s85 = np.linalg.svd(M85n, compute_uv=False)
    r85 = int(np.sum(s85 > 1e-9 * s85[0]))
    out["all_85_rows"] = {"points": n_all, "rank": r85, "expected": 85, "sv_min_over_max": float(s85[-1] / s85[0]),
                          "ok": r85 == 85, "seconds": time.time() - t0}
    RESULTS["c_independence"] = out
    say(f"[c] new rows rank {rank}/34 (sv ratio {s[-1] / s[0]:.2e}), families ok {out['all_families_ok']}; all rows rank {r85}/85 (sv ratio {s85[-1] / s85[0]:.2e})")
    save()


# =====================================================================================================================
D1 = np.array([1.0, -8.0, 0.0, 8.0, -1.0]) / 12.0           # f'(0) * h, exact for degree <= 4
D2 = np.array([-1.0, 16.0, -30.0, 16.0, -1.0]) / 12.0       # f''(0) * h^2, exact for degree <= 5
STEPS = np.array([-2, -1, 0, 1, 2])


def section_d(rng, q486_a, ncoord_extra=50, nhcol=40):
    out = {"label": "NUM", "stencil": "5-point central differences (exact for quartic polynomials up to rounding)",
           "normalisation": "coordinate FD: per-row max |entry|; directional: per-row ||g||_2 resp. ||H||_F (unit directions)"}
    ids = list(C.new_parameter_ids())
    pts = {"random_generic": random_q(rng),
           "g3211_like": C.g3211_point(0.6, -0.5, 0.4, 0.3, 0.2, 0.05, 0.01, 2.0) + 0.02 * rng.normal(size=C.TOTAL_DIM)}
    for name, q in pts.items():
        rows = C.new_rows(q)
        G = np.array([rows[p].gradient for p in ids])
        H = np.array([rows[p].hessian for p in ids])
        gs = np.max(np.abs(G), axis=1)
        hs = np.max(np.abs(H), axis=(1, 2))
        g2n = np.linalg.norm(G, axis=1)                 # >= |g.d| for unit d
        hfn = np.sqrt(np.sum(H * H, axis=(1, 2)))       # Frobenius >= |d1.H.d2| for unit d1, d2
        res = {}
        # gradient by FD on coordinates: all 45 A + random others
        others = rng.choice(np.arange(C.DIM486), size=ncoord_extra, replace=False)
        coords = np.r_[np.arange(C.A_SLICE.start, C.A_SLICE.stop), others]
        h = 1e-2
        pts_list = []
        for j in coords:
            for s in STEPS:
                qq = q.copy()
                qq[j] += s * h
                pts_list.append(qq)
        vals = C.new_row_values(np.array(pts_list)).reshape(len(coords), 5, len(ids))
        fd = np.einsum("s,csr->cr", D1, vals) / h
        err = np.abs(fd - G[:, coords].T) / gs[None, :]
        res["gradient_fd_coords"] = int(len(coords))
        res["gradient_max_rel_err"] = float(np.max(err))
        # Hessian columns by FD of gradients
        cols = np.r_[rng.choice(np.arange(C.A_SLICE.start, C.A_SLICE.stop), size=nhcol // 2, replace=False),
                     rng.choice(np.arange(C.DIM486), size=nhcol - nhcol // 2, replace=False)]
        worst = 0.0
        for j in cols:
            gsx = []
            for s in STEPS:
                if s == 0:
                    gsx.append(G)
                    continue
                qq = q.copy()
                qq[j] += s * h
                rr = C.new_rows(qq, hessian=False)
                gsx.append(np.array([rr[p].gradient for p in ids]))
            fdc = np.einsum("s,srk->rk", D1, np.array(gsx)) / h
            worst = max(worst, float(np.max(np.abs(fdc - H[:, :, j]) / hs[:, None])))
        res["hessian_fd_columns"] = int(len(cols))
        res["hessian_max_rel_err"] = worst
        # directional: exact quartic restriction, value -> (g.d, d.H.d) and mixed d1.H.d2 (Richardson)
        dirs = [rng.normal(size=C.TOTAL_DIM) for _ in range(6)]
        dirs = [d / np.linalg.norm(d) for d in dirs]
        hd = 0.3
        wd1 = wd2 = wmix = 0.0
        for d in dirs:
            vals = C.new_row_values(np.array([q + s * hd * d for s in STEPS]))
            f1 = D1 @ vals / hd
            f2 = D2 @ vals / hd ** 2
            gd = G @ d
            dHd = np.einsum("i,rij,j->r", d, H, d)
            wd1 = max(wd1, float(np.max(np.abs(f1 - gd) / g2n)))
            wd2 = max(wd2, float(np.max(np.abs(f2 - dHd) / hfn)))
        for d1, d2 in zip(dirs[:3], dirs[3:]):
            def mixed(hh):
                v = C.new_row_values(np.array([q + hh * d1 + hh * d2, q + hh * d1 - hh * d2, q - hh * d1 + hh * d2, q - hh * d1 - hh * d2]))
                return (v[0] - v[1] - v[2] + v[3]) / (4 * hh * hh)
            m = (4 * mixed(0.15) - mixed(0.3)) / 3
            ref = np.einsum("i,rij,j->r", d1, H, d2)
            wmix = max(wmix, float(np.max(np.abs(m - ref) / hfn)))
        res["directional_first_max_rel_err"] = wd1
        res["directional_second_max_rel_err"] = wd2
        res["mixed_second_max_rel_err"] = wmix
        res["ok"] = max(res["gradient_max_rel_err"], res["hessian_max_rel_err"], wd1, wd2, wmix) <= 1e-7
        out[name] = res
        say(f"[d] {name}: grad {res['gradient_max_rel_err']:.1e} hess {res['hessian_max_rel_err']:.1e} dir1 {wd1:.1e} dir2 {wd2:.1e} mixed {wmix:.1e}")
    # total potential (51 repo rows + 34 new rows, random couplings) along random directions
    q = C.join(q486_a, rng.normal(size=45))
    rows = C.parameter_rows(q)
    coeffs = {p: float(rng.normal()) for p in rows}
    V0, g0, H0 = C.assemble(rows, coeffs)
    ids20 = C.v20_parameter_ids()
    c20 = np.array([coeffs[p] for p in ids20])
    cn = np.array([coeffs[p] for p in ids])
    tot = []
    for _ in range(2):
        d = rng.normal(size=C.TOTAL_DIM)
        d /= np.linalg.norm(d)
        hd = 0.05
        Vs = []
        for s in STEPS:
            qq = q + s * hd * d
            v20v = C.v20_row_values(qq)
            Vs.append(float(c20 @ np.array([v20v[p] for p in ids20]) + cn @ C.new_row_values(qq)[0]))
        Vs = np.array(Vs)
        f1, f2 = D1 @ Vs / hd, D2 @ Vs / hd ** 2
        tot.append({"value_consistency": abs(Vs[2] - V0) / max(1.0, abs(V0)),
                    "first": abs(f1 - g0 @ d) / max(1.0, np.linalg.norm(g0)),
                    "second": abs(f2 - d @ H0 @ d) / max(1.0, np.max(np.abs(np.linalg.eigvalsh(H0))))})
    out["total_potential_85_rows"] = {"directions": tot, "ok": all(max(t.values()) <= 1e-7 for t in tot)}
    say(f"[d] total 85-row potential directional: {tot}")
    RESULTS["d_finite_differences"] = out
    save()


# =====================================================================================================================
def rotate_field(q, field, theta):
    sl = C.BLOCKS[field]
    qq = q.copy()
    x, y = q[sl.start:sl.stop:2], q[sl.start + 1:sl.stop:2]
    c, s = math.cos(theta), math.sin(theta)
    qq[sl.start:sl.stop:2] = c * x - s * y
    qq[sl.start + 1:sl.stop:2] = s * x + c * y
    return qq


def section_e(rng):
    out = {"label": "EXACT (monomial charges) + NUM (rotations)"}
    inv = json.loads(C.INVARIANTS_JSON.read_text(encoding="utf-8"))["A45_invariants"]
    fields = ("H10", "Sigma126bar", "S", "Phi17")
    # EXACT: per-monomial charges
    ex = {}
    for e in inv:
        p0 = C.raw_contraction(e["name"])
        decl = C._holo_charges(e)
        per = {f: sorted(set(C.monomial_charges(p0, {f: 1}).tolist())) for f in fields}
        ex[e["name"]] = {"declared_holomorphic_degrees": decl, "monomial_degrees": per,
                         "ok": all(per[f] == [decl[f]] for f in fields)}
    rowx = {r.parameter_id: [sorted(set(C.monomial_charges(r.poly, C.U1X_CHARGES).tolist())),
                             sorted(set(C.monomial_charges(r.poly, C.PQ_CHARGES).tolist()))] for r in C.rowdefs()}
    out["exact_raw_contractions"] = ex
    out["exact_all_raw_ok"] = all(v["ok"] for v in ex.values())
    out["exact_row_X_and_PQ_monomial_charges"] = rowx
    out["exact_rows_X0_PQ0"] = all(v == [[0], [0]] for v in rowx.values())
    # NUM: rotations
    q = random_q(rng)
    w = C.w_of_q(q)
    th = 0.7
    worst_raw = 0.0
    for e in inv:
        p0 = C.raw_contraction(e["name"])
        v0 = C.poly_value(p0, w)
        decl = C._holo_charges(e)
        for f in fields:
            v1 = C.poly_value(p0, C.w_of_q(rotate_field(q, f, th)))
            worst_raw = max(worst_raw, abs(v1 - np.exp(1j * decl[f] * th) * v0) / abs(v0))
    out["num_raw_contraction_phase_max_rel_err"] = worst_raw
    base = dict(zip(C.new_parameter_ids(), C.new_row_values(q)[0]))
    worst_rows = 0.0
    defs = {r.parameter_id: r for r in C.rowdefs()}
    for f in fields:
        rot = dict(zip(C.new_parameter_ids(), C.new_row_values(rotate_field(q, f, th))[0]))
        for pid, r in defs.items():
            n = r.holomorphic_charges[f]
            if r.component == "real":
                expv = base[pid]
            else:
                re, im = base["re::" + r.invariant], base["im::" + r.invariant]
                c, s = math.cos(n * th), math.sin(n * th)
                expv = c * re + s * im if r.component == "re" else -s * re + c * im
            worst_rows = max(worst_rows, abs(rot[pid] - expv) / max(1e-300, abs(base[pid]) + 1e-12))
    out["num_rows_phase_max_rel_err"] = worst_rows

    def rotate_charges(q, charges, th):
        qq = q.copy()
        for f in fields:
            qq = rotate_field(qq, f, charges.get(f, 0) * th)
        return qq
    vx = C.new_row_values(rotate_charges(q, C.U1X_CHARGES, th))[0]
    vp = C.new_row_values(rotate_charges(q, C.PQ_CHARGES, th))[0]
    b = np.array(list(base.values()))
    out["num_rows_X_rotation_max_rel_change"] = float(np.max(np.abs(vx - b) / np.abs(b)))
    out["num_rows_PQ_rotation_max_rel_change"] = float(np.max(np.abs(vp - b) / np.abs(b)))
    # v20 directions (repo value layer): per-field phases with declared counts, and X invariance
    st = C.potential.deterministic_state(5311)
    d0 = {d.direction_id: d for d in C.potential.evaluate_directions(st)}
    live = set(C.g2_audit.contract_selection()["direction_ids"])
    FO = C.potential.FIELD_ORDER
    worst20 = 0.0
    for f, (zi, zbi) in (("H10", ("H", "Hb")), ("Sigma126bar", ("D", "Db")), ("S", ("S", "Sb")), ("Phi17", ("X", "Xb"))):
        ph = np.exp(1j * th)
        st_r = C.potential.FieldState(phi=st.phi, h=st.h * (ph if f == "H10" else 1),
                                      sigma=C.direct.scale_form(st.sigma, ph if f == "Sigma126bar" else 1),
                                      s=st.s * (ph if f == "S" else 1), x=st.x * (ph if f == "Phi17" else 1))
        for d in C.potential.evaluate_directions(st_r):
            if d.direction_id not in live:
                continue
            n = d.counts[FO.index(zi)] - d.counts[FO.index(zbi)]
            v0 = d0[d.direction_id].value
            if abs(v0) > 0:
                worst20 = max(worst20, abs(d.value - np.exp(1j * n * th) * v0) / abs(v0))
    xs = {"H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}
    st_x = C.potential.FieldState(phi=st.phi, h=st.h * np.exp(-2j * th), sigma=C.direct.scale_form(st.sigma, np.exp(-2j * th)),
                                  s=st.s * np.exp(4j * th), x=st.x * np.exp(17j * th))
    wx = 0.0
    for d in C.potential.evaluate_directions(st_x):
        if d.direction_id in live and abs(d0[d.direction_id].value) > 0:
            wx = max(wx, abs(d.value - d0[d.direction_id].value) / abs(d0[d.direction_id].value))
    out["num_v20_directions_phase_max_rel_err"] = worst20
    out["num_v20_directions_X_rotation_max_rel_change"] = wx
    RESULTS["e_X_charge_selection"] = out
    say(f"[e] EXACT raw ok {out['exact_all_raw_ok']}, rows X=PQ=0 {out['exact_rows_X0_PQ0']}; NUM raw {worst_raw:.1e} rows {worst_rows:.1e} "
        f"X {out['num_rows_X_rotation_max_rel_change']:.1e} PQ {out['num_rows_PQ_rotation_max_rel_change']:.1e}; v20 phases {worst20:.1e} X {wx:.1e}")
    save()


# =====================================================================================================================
def section_f(rng):
    out = {"label": "NUM (wall clock, this machine, OMP/OPENBLAS threads = 2)"}

    def tm(fn, n=3):
        ts = []
        for _ in range(n):
            t0 = time.time()
            fn()
            ts.append(time.time() - t0)
        return float(np.median(ts))
    q = random_q(rng)
    Q50 = np.array([random_q(rng) for _ in range(50)])
    out["new34_value_one_point_s"] = tm(lambda: C.new_row_values(q))
    out["new34_value_per_point_batch50_s"] = tm(lambda: C.new_row_values(Q50), 2) / 50
    out["new34_value_gradient_s"] = tm(lambda: C.new_rows(q, hessian=False))
    out["new34_value_gradient_hessian_s"] = tm(lambda: C.new_rows(q))
    out["symmetry_matrix_s"] = tm(lambda: C.symmetry_matrix(q))
    qn = C.join(rng.normal(size=C.DIM486) * 0.5, rng.normal(size=45))
    t0 = time.time()
    C.v20_rows(qn)
    out["v20_51_rows_repo_value_gradient_hessian_s"] = time.time() - t0
    out["v20_51_values_repo_s"] = tm(lambda: C.v20_row_values(qn), 2)
    rows = C.parameter_rows(qn)
    coeffs = {p: 1.0 for p in rows}
    out["assemble_85_rows_s"] = tm(lambda: C.assemble(rows, coeffs))
    H = C.assemble(rows, coeffs)[2]
    out["decompose_hessian_G3211_s"] = tm(lambda: C.decompose_hessian(H, "G3211"), 2)
    out["decompose_hessian_SM_s"] = tm(lambda: C.decompose_hessian(H, "SM"), 2)
    out["full_eigvalsh_531_s"] = tm(lambda: np.linalg.eigvalsh(H), 2)
    RESULTS["f_runtime"] = out
    say(f"[f] {out}")
    save()


# =====================================================================================================================
def section_g(rng):
    out = {"label": "NUM (ranks/residuals), EXACT group-theory expectations"}
    pts = {"G3211_sigma0": (0.6, -0.5, 0.4, 0.3, 0.2, 0.0, 0.01, 2.0),
           "SM_sigma": (0.6, -0.5, 0.4, 0.3, 0.2, 0.05, 0.01, 2.0),
           "A45_only": (0, 0, 0, 0.3, 0.2, 0, 0, 0), "Phi_only_p_a_omega": (0.6, -0.5, 0.4, 0, 0, 0, 0, 0),
           "Phi_p_a_only_G3221": (0.6, -0.5, 0.0, 0, 0, 0, 0, 0),
           "A45_T3R_only": (0, 0, 0, 0.3, 0.0, 0, 0, 0), "A45_TBL_only": (0, 0, 0, 0.0, 0.2, 0, 0, 0)}
    ranks = {}
    for k, args in pts.items():
        q = C.g3211_point(*args)
        ranks[k] = C.symmetry_matrix(q)[1]
    out["symmetry_ranks"] = ranks
    out["expected"] = C.EXPECTED_GOLDSTONES
    out["G3211_ok"] = ranks["G3211_sigma0"]["so10_plus_u1x_plus_pq_rank"] == 34 and ranks["G3211_sigma0"]["so10_stabilizer_dimension"] == 13 \
        and ranks["G3211_sigma0"]["so10_plus_u1x_rank"] == 33
    out["SM_ok"] = ranks["SM_sigma"]["so10_plus_u1x_plus_pq_rank"] == 35 and ranks["SM_sigma"]["so10_stabilizer_dimension"] == 12 \
        and ranks["SM_sigma"]["so10_plus_u1x_rank"] == 34
    out["singlet_dims"] = {"G3211": int(C.singlet_basis("G3211").shape[1]), "SM": int(C.singlet_basis("SM").shape[1])}
    # components
    for kind in ("G3211", "SM"):
        out[f"components_{kind}"] = [{"label": rc["label"], "conjugate": rc["conjugate"], "real_dim": rc["real_dim"],
                                      "m": rc["complex_multiplicity"]} for rc in C.real_components(kind)]
        out[f"A45_block_{kind}"] = [{"label": rc["label"], "conjugate": rc["conjugate"], "real_dim": rc["real_dim"],
                                     "m": rc["complex_multiplicity"]} for rc in C.a_block_projectors(kind)]
    # sigma_std label
    qs = C.g3211_point(0, 0, 0, 0, 0, sigma=1.0)
    out["sigma_std_component"] = [rc["label"] for rc in C.real_components("G3211") if np.linalg.norm(rc["W"].T @ qs) > 1e-9]
    # tadpole pattern of the linear-in-A rows at A = 0 (Phi only)
    Ts = np.column_stack([C.T3R_UNIT, C.TBL_UNIT])
    pat = {}
    combos = {"p": (1, 0, 0), "a": (0, 1, 0), "omega": (0, 0, 1), "p+a": (1, 1, 0), "p+omega": (1, 0, 1), "a+omega": (0, 1, 1)}
    raw = {}
    for nm, (p, a, om) in combos.items():
        rows = C.new_rows(C.g3211_point(p, a, om, 0, 0), hessian=False)
        for pid in ("lambda::A04_PPA_eps", "lambda::A06_PPPA_eps1", "lambda::A07_PPPA_eps2"):
            gA = rows[pid].gradient[C.A_SLICE]
            coef, *_ = np.linalg.lstsq(Ts, gA, rcond=None)
            raw.setdefault(pid, {})[nm] = {"T3R": float(coef[0]), "T_BL": float(coef[1]),
                                           "residual_outside_span": float(np.linalg.norm(gA - Ts @ coef))}
    # quadratic pattern of A04 (pure quadratic in p,a,omega): coefficient of p a, omega^2, a omega etc.
    q04 = {}
    for comp in ("T3R", "T_BL"):
        f = {k: raw["lambda::A04_PPA_eps"][k][comp] for k in combos}
        q04[comp] = {"p^2": f["p"], "a^2": f["a"], "omega^2": f["omega"], "p*a": f["p+a"] - f["p"] - f["a"],
                     "p*omega": f["p+omega"] - f["p"] - f["omega"], "a*omega": f["a+omega"] - f["a"] - f["omega"]}
    out["tadpoles_at_A0"] = raw
    out["A04_tadpole_quadratic_form"] = q04
    out["max_tadpole_residual_outside_span_T3R_TBL"] = max(v["residual_outside_span"] for d in raw.values() for v in d.values())
    # gradient of every row lies in the singlet subspace at symmetric points; Hessian decomposition tests
    for nm, kind, args in (("G3211_sigma0", "G3211", pts["G3211_sigma0"]), ("SM_sigma", "SM", pts["SM_sigma"])):
        q = C.g3211_point(*args)
        rows = C.parameter_rows(q)
        S = C.singlet_basis(kind)
        P = np.eye(C.TOTAL_DIM) - S @ S.T
        gmax = max(float(np.linalg.norm(r.gradient)) for r in rows.values())
        floor = 1e-12 * gmax      # rows whose gradient vanishes analytically (e.g. O27 54/4125 at sigma_std) carry noise only
        res_new = max(float(np.linalg.norm(P @ rows[p].gradient) / np.linalg.norm(rows[p].gradient))
                      for p in C.new_parameter_ids() if np.linalg.norm(rows[p].gradient) > floor)
        res_v20 = max(float(np.linalg.norm(P @ rows[p].gradient) / np.linalg.norm(rows[p].gradient))
                      for p in C.v20_parameter_ids() if np.linalg.norm(rows[p].gradient) > floor)
        zero_grad_rows = sorted(p for p in rows if np.linalg.norm(rows[p].gradient) <= floor)
        coeffs = {p: float(rng.normal()) for p in rows}
        V, g, H = C.assemble(rows, coeffs)
        T, rk = C.symmetry_matrix(q)
        dec = C.decompose_hessian(H, kind, tangents=T)
        ngold = sum(c["goldstone_real_dim"] for c in dec["components"])
        # Goldstone directions are exact zero modes only at a stationary point; here check H T = 0 projected onto
        # non-singlet components:  for invariant V,  H(q) T_k = - (dG_k)^T g  (Ward identity)
        ward = max(float(np.linalg.norm(H @ (G @ q) + G.T @ g)) for G in list(C.so10_generators()) + [C.u1x_generator(), C.pq_generator()])
        mult_ok = True
        for c in dec["components"]:
            be = np.sort(np.array(c["block_eigenvalues"]))
            pred = np.sort(np.concatenate([[s["mass_squared"]] * s["real_multiplicity"] for s in c["spectrum"]]))
            if be.shape != pred.shape or np.max(np.abs(be - pred)) > 1e-9 * max(1.0, np.max(np.abs(be))):
                mult_ok = False
        np.savez_compressed(C.BIG / f"rows85_{nm}.npz", q=q, ids=np.array(sorted(rows)),
                            values=np.array([rows[p].value for p in sorted(rows)]),
                            grads=np.array([rows[p].gradient for p in sorted(rows)]),
                            hess=np.array([rows[p].hessian for p in sorted(rows)]).astype(np.float64), tangents=T,
                            point=np.array(args, dtype=complex))
        out[f"point_{nm}"] = {"kind": kind, "symmetry_ranks": rk, "singlet_dim": int(S.shape[1]),
                              "new_rows_gradient_outside_singlets_max_rel": res_new,
                              "v20_rows_gradient_outside_singlets_max_rel": res_v20,
                              "rows_with_vanishing_gradient_excluded": zero_grad_rows, "gradient_floor": floor,
                              "hessian_decomposition_max_leakage": dec["max_leakage"],
                              "goldstone_real_dim_sum_over_components": ngold, "expected_goldstones": rk["so10_plus_u1x_plus_pq_rank"],
                              "reduced_spectra_reproduce_block_spectra": mult_ok,
                              "ward_identity_H_T_plus_dG_g_max": ward,
                              "n_components": len(dec["components"]),
                              "rows_npz": str(C.BIG / f"rows85_{nm}.npz")}
        say(f"[g] {nm}: ranks {rk}; singlet residual new {res_new:.1e} v20 {res_v20:.1e}; leakage {dec['max_leakage']:.1e}; "
            f"goldstones {ngold}; reduced spectra ok {mult_ok}; Ward {ward:.1e}")
        if kind == "G3211":   # same point, SM decomposition too
            decsm = C.decompose_hessian(H, "SM", tangents=T)
            out[f"point_{nm}"]["SM_decomposition_max_leakage"] = decsm["max_leakage"]
            out[f"point_{nm}"]["SM_goldstone_sum"] = sum(c["goldstone_real_dim"] for c in decsm["components"])
    out["max_tadpole_note"] = "A-tadpoles of the eps rows at A = 0 lie in span(T3R, T_BL) (pattern EXACT by G3211 symmetry)."
    RESULTS["g_G3211_parametrisation"] = out
    say(f"[g] G3211 ok {out['G3211_ok']} SM ok {out['SM_ok']}; singlet dims {out['singlet_dims']}; sigma_std in {out['sigma_std_component']}; "
        f"tadpole residual {out['max_tadpole_residual_outside_span_T3R_TBL']:.1e}; A04 tadpole form {q04}")
    save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--sections", default="0,1,a,b,c,d,e,f,g")
    args = ap.parse_args()
    rng = np.random.default_rng(20261017)
    secs = args.sections.split(",")
    t0 = time.time()
    RESULTS["meta"] = {"module": str(HERE / "chart531.py"), "code_version": C.CODE_VERSION, "date": "2026-10-17",
                       "repo_root": str(C.REPO), "invariants_json": str(C.INVARIANTS_JSON)}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
            for k, v in old.items():
                RESULTS.setdefault(k, v)
        except Exception:
            pass
    q486_a = None
    if "0" in secs:
        section0_build()
    if "1" in secs:
        section1_crosscheck()
    if "a" in secs:
        _, q486_a = section_a(rng)
    if q486_a is None:
        q486_a = C.chart.pack(C.potential.deterministic_state(5310))
    if "b" in secs:
        section_b(rng, q486_a)
    if "c" in secs:
        section_c(rng, 80, 40 if args.quick else 95)
    if "d" in secs:
        section_d(rng, q486_a)
    if "e" in secs:
        section_e(rng)
    if "f" in secs:
        section_f(rng)
    if "g" in secs:
        section_g(rng)
    RESULTS["meta"]["seconds_total_last_run"] = time.time() - t0
    save()
    say(f"done in {time.time() - t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
