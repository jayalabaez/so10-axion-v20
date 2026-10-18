"""SKEPTIC tests of the 34 new chart531 rows with my own code.

 S1  generators: my A-block (derived from the repo H10 block) vs chart531; so(10) structure constants on all 531 coords
 S2  multidegree of every row by block scaling / phase Fourier analysis (no use of chart531 polynomial metadata)
 S3  FINITE SO(10) rotations exp(theta.G) with my generators, U(1)_X and PQ phases; negative controls
 S4  rank per class and total vs my character count (sk_charcount.json)
 S5  my tensor evaluator (repo chart.unpack -> dense tensors; literal eps sum over 10!) vs chart531 rows for all 30
     declared machine_specs; reproduction of the invariants.json reference values (finding F1)
 S6  completeness: my own extra contraction patterns (incl. eps graphs not in the basis) must lie in the row span
 S7  A = 0: new rows vanish with zero non-A gradient
 S8  F2 tadpole of A04 at A = 0 with my evaluator; G3211 directions vs repo SM generators; stabilizers
 S9  finite-difference check of chart531 gradients/Hessians along random directions
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_common as C  # noqa: E402
import sk_eval as E  # noqa: E402
import chart531 as CH  # noqa: E402  (builder module, read-only import)

OUT = C.HERE / "sk_rows.json"
LOG = open(C.HERE / "sk_rows.log", "w", encoding="utf-8")
R = {}
rng = np.random.default_rng(20261017)


def log(m):
    C.log(m, LOG)


def rows_at(Q):
    return CH.new_row_values(np.atleast_2d(Q))


IDS = list(CH.new_parameter_ids())
NR = len(IDS)


# ------------------------------------------------------------------------------------------------------------------
def s1_generators():
    t0 = time.time()
    mine = C.my_adjoint_block()
    theirs = CH.adjoint_generators_45()
    dA = max(float(np.max(np.abs(a - b))) for a, b in zip(mine, theirs))
    G = C.my_generators531()
    G486 = C.repo_generators486()
    # structure constants from the 10x10 vector matrices
    Ls = C.h_block_vector_matrices()
    Lflat = np.array([L.ravel() for L in Ls]).T          # 100 x 45
    worst = 0.0
    worst_flipped = 0.0
    for i in range(45):
        for j in range(i + 1, 45):
            comm = Ls[i] @ Ls[j] - Ls[j] @ Ls[i]
            f = np.linalg.lstsq(Lflat, comm.ravel(), rcond=None)[0]
            lhs = G[i] @ G[j] - G[j] @ G[i]
            rhs = sum(fc * G[k] for k, fc in enumerate(f) if abs(fc) > 1e-12)
            worst = max(worst, float(np.max(np.abs(lhs - rhs))))
            # flipped-sign A block would satisfy [-ad,-ad] = +ad[.,.] != -ad[.,.]: control on the A block only
            Ai, Aj = -mine[i], -mine[j]
            rhsA = sum(fc * (-mine[k]) for k, fc in enumerate(f) if abs(fc) > 1e-12)
            if isinstance(rhsA, np.ndarray):
                worst_flipped = max(worst_flipped, float(np.max(np.abs(Ai @ Aj - Aj @ Ai - rhsA))))
    gens_ch = CH.so10_generators()
    d531 = max(float(np.max(np.abs(gens_ch[k].toarray() - G[k]))) for k in range(45))
    R["S1_generators"] = {"A_block_mine_vs_chart531_maxdiff": dA, "all531_mine_vs_chart531_maxdiff": d531,
                          "so10_structure_constants_on_531_maxresid": worst,
                          "control_sign_flipped_A_block_resid": worst_flipped,
                          "H_block_is_L_ab=E_ab-E_ba": bool(all(
                              np.array_equal(Ls[k], _E(a, b)) for k, (a, b) in enumerate(C.PAIRS))),
                          "time_s": time.time() - t0}
    log(f"S1 {R['S1_generators']}")
    return G


def _E(a, b):
    m = np.zeros((10, 10))
    m[a, b], m[b, a] = 1.0, -1.0
    return m


# ------------------------------------------------------------------------------------------------------------------
def s2_multidegrees():
    t0 = time.time()
    base = rng.normal(size=(4, C.NTOT))
    r0 = rows_at(base)
    deg = {}
    for f in ("P", "A", "H", "D", "S", "T"):
        Q = base.copy()
        Q[:, C.SL[f]] *= 2.0
        r1 = rows_at(Q)
        with np.errstate(divide="ignore", invalid="ignore"):
            n = np.log2(np.abs(r1 / r0))
        nmed = np.nanmedian(n, axis=0)
        assert np.all(np.abs(nmed - np.rint(nmed)) < 1e-6), (f, nmed)
        deg[f] = np.rint(nmed).astype(int)
    holo = {}
    for f in ("H", "D", "S", "T"):
        vals = []
        for j in range(8):
            Rm = C.phase_rotation({f: 2 * math.pi * j / 8})
            vals.append(rows_at(base[:2] @ Rm.T))
        vals = np.array(vals)          # 8 x 2 x NR
        c = np.abs(np.fft.fft(vals, axis=0)).max(axis=1)       # 8 x NR
        m = []
        for r in range(NR):
            ks = [k for k in range(8) if c[k, r] > 1e-9 * c[:, r].max()]
            freqs = sorted(set(min(k, 8 - k) for k in ks))
            assert len(freqs) == 1, (IDS[r], f, ks)
            m.append(freqs[0])
        holo[f] = np.array(m)
    keys = []
    for r in range(NR):
        keys.append((int(deg["P"][r]), int(deg["A"][r]), int(deg["H"][r]), int(holo["H"][r]), int(deg["D"][r]),
                     int(holo["D"][r]), int(deg["S"][r]), int(holo["S"][r]), int(deg["T"][r]), int(holo["T"][r])))
    R["S2_multidegrees"] = {IDS[r]: keys[r] for r in range(NR)}
    R["S2_key_format"] = "(n_P, n_A, n_H+n_Hb, |n_H-n_Hb|, n_D+n_Db, |n_D-n_Db|, n_S+n_Sb, |..|, n_T+n_Tb, |..|)"
    log(f"S2 multidegrees determined ({time.time() - t0:.1f}s)")
    return keys


def orbit_key(label: str):
    c = Counter()
    for tok in label.split():
        if "^" in tok:
            f, n = tok.split("^")
            c[f] += int(n)
        else:
            c[tok] += 1
    return (c["P"], c["A"], c["H"] + c["Hb"], abs(c["H"] - c["Hb"]), c["D"] + c["Db"], abs(c["D"] - c["Db"]),
            c["S"] + c["Sb"], abs(c["S"] - c["Sb"]), c["T"] + c["Tb"], abs(c["T"] - c["Tb"]))


# ------------------------------------------------------------------------------------------------------------------
def s3_invariance(G):
    t0 = time.time()
    Q = rng.normal(size=(6, C.NTOT))
    r0 = rows_at(Q)
    scale = np.max(np.abs(r0), axis=0)
    out = {}
    worst = np.zeros(NR)
    for trial in range(3):
        th = rng.normal(scale=0.8, size=45)
        Gs = sum(t * g for t, g in zip(th, G))
        Rm = expm(Gs)
        orth = float(np.max(np.abs(Rm @ Rm.T - np.eye(C.NTOT))))
        r1 = rows_at(Q @ Rm.T)
        worst = np.maximum(worst, np.max(np.abs(r1 - r0), axis=0) / scale)
        out[f"rotation{trial}_orthogonality"] = orth
    out["so10_finite_rotation_max_rel_change_per_row"] = {IDS[k]: float(worst[k]) for k in range(NR)}
    out["so10_finite_rotation_max_rel_change"] = float(worst.max())
    # U(1)_X and PQ finite phases
    for name, ch in (("U1X", {"H": -2, "D": -2, "S": 4, "T": 17}), ("PQ", {"H": -2, "D": -2, "S": 4, "T": 0})):
        w = 0.0
        for th in (0.37, 1.9, -2.6):
            Rm = C.phase_rotation({f: q * th for f, q in ch.items()})
            w = max(w, float(np.max(np.abs(rows_at(Q @ Rm.T) - r0) / scale)))
        out[f"{name}_max_rel_change"] = w
    # negative controls: (a) rotate the 486 block only; (b) sign-flipped adjoint on A
    th = rng.normal(scale=0.8, size=45)
    Gs = sum(t * g for t, g in zip(th, G))
    Rm = expm(Gs)
    Ra = Rm.copy()
    Ra[C.N486:, C.N486:] = np.eye(45)
    Rb = Rm.copy()
    Rb[C.N486:, C.N486:] = expm(-Gs[C.N486:, C.N486:])
    ca = np.max(np.abs(rows_at(Q @ Ra.T) - r0), axis=0) / scale
    cb = np.max(np.abs(rows_at(Q @ Rb.T) - r0), axis=0) / scale
    out["control_rotate_486_only_rel_change_per_row"] = {IDS[k]: float(ca[k]) for k in range(NR)}
    out["control_flipped_adjoint_rel_change_per_row"] = {IDS[k]: float(cb[k]) for k in range(NR)}
    R["S3_invariance"] = out
    R["S3_time_s"] = time.time() - t0
    log(f"S3 so10 finite rotations max rel change {out['so10_finite_rotation_max_rel_change']:.2e}; "
        f"U1X {out['U1X_max_rel_change']:.2e}; PQ {out['PQ_max_rel_change']:.2e}")
    log(f"S3 controls: 486-only min over mixed rows "
        f"{min(v for k, v in out['control_rotate_486_only_rel_change_per_row'].items()):.2e}; flipped-adjoint per row "
        f"{ {k: round(v, 3) for k, v in out['control_flipped_adjoint_rel_change_per_row'].items()} }")


# ------------------------------------------------------------------------------------------------------------------
def s4_rank(keys):
    t0 = time.time()
    cc = json.loads((C.HERE / "sk_charcount.json").read_text(encoding="utf-8"))
    count_by_key = {}
    for o in cc["orbits"]:
        if o["contains_A"] and o["n_invariants"] > 0:
            count_by_key[orbit_key(o["rep"])] = (o["rep"], o["real_parameters"])
    res = {}
    allok = True
    for trial, nq in ((0, 160), (1, 200)):
        Q = rng.normal(size=(nq, C.NTOT)) * (1.0 if trial == 0 else rng.uniform(0.3, 2.0, size=(nq, 1)))
        V = rows_at(Q)
        Vn = V / np.linalg.norm(V, axis=0)
        s = np.linalg.svd(Vn, compute_uv=False)
        res[f"trial{trial}_total"] = {"rank": int(np.sum(s > 1e-9 * s[0])), "sv_min_over_max": float(s[-1] / s[0])}
        for key in sorted(set(keys)):
            cols = [r for r in range(NR) if keys[r] == key]
            sv = np.linalg.svd(Vn[:, cols], compute_uv=False)
            rank = int(np.sum(sv > 1e-9 * sv[0]))
            rep, expect = count_by_key.get(key, ("NOT IN MY COUNT", None))
            ok = (rank == len(cols) == expect)
            allok &= ok
            res.setdefault(rep, {})[f"trial{trial}"] = {"rows": [IDS[c] for c in cols], "rank": rank,
                                                       "my_count_real": expect, "sv_min_over_max": float(sv[-1] / sv[0]),
                                                       "ok": ok}
    missing = [rep for key, (rep, n) in count_by_key.items() if key not in set(keys)]
    res["orbits_in_my_count_without_rows"] = missing
    res["all_ok"] = bool(allok and not missing and res["trial0_total"]["rank"] == 34 == res["trial1_total"]["rank"])
    R["S4_rank"] = res
    log(f"S4 rank: total {res['trial0_total']}, {res['trial1_total']}; missing orbits {missing}; all_ok {res['all_ok']}"
        f" ({time.time() - t0:.1f}s)")


# ------------------------------------------------------------------------------------------------------------------
def s5_declared():
    t0 = time.time()
    inv = json.loads(CH.INVARIANTS_JSON.read_text(encoding="utf-8"))["A45_invariants"]
    Q = rng.normal(size=(3, C.NTOT))
    V = rows_at(Q)
    col = {pid: k for k, pid in enumerate(IDS)}
    T = [C.tensors_from_q(q) for q in Q]
    res = {}
    worst = 0.0
    for e in inv:
        name = e["name"]
        mine = np.array([E.evaluate_spec(t, e["machine_spec"]) for t in T])
        if e["real_parameters"] == 2:
            ch_re, ch_im = V[:, col[f"re::{name}"]], V[:, col[f"im::{name}"]]
            ref = np.concatenate([2 * mine.real, -2 * mine.imag])
            got = np.concatenate([ch_re, ch_im])
        else:
            assert np.max(np.abs(mine.imag)) <= 1e-9 * np.max(np.abs(mine)), (name, mine)
            ref = mine.real
            got = V[:, col[f"lambda::{name}"]]
        rel = float(np.max(np.abs(got - ref)) / np.max(np.abs(ref)))
        ratio = float(np.median(got / ref))
        worst = max(worst, rel)
        res[name] = {"rel_diff_chart531_vs_my_literal_evaluation": rel, "ratio": ratio}
    R["S5_declared_formula"] = {"per_invariant": res, "worst_rel_diff": worst, "time_s": time.time() - t0}
    log(f"S5 chart531 rows vs my literal evaluation of the declared formulas: worst rel diff {worst:.2e}")
    # F1: reproduce invariants.json reference values on the model builder's own sample (its sampler, read-only)
    sys.path.insert(0, str(C.CHART_DIR.parent / "model"))
    import explicit_basis_v22 as EB  # noqa: E402
    g = np.random.default_rng(424242)
    F = EB.random_fields(g)
    F["S"] = complex(g.normal(), g.normal())
    F["T"] = complex(g.normal(), g.normal())
    f1 = {}
    for e in inv:
        mine = E.evaluate_spec(F, e["machine_spec"])
        rv = e["reference_value_seed424242_sample0"]
        refv = complex(rv["re"], rv["im"])
        f1[e["name"]] = {"declared_over_reference": [(mine / refv).real, (mine / refv).imag]}
    R["S5_F1_reference_values"] = f1
    log("S5 F1 declared/reference: " + ", ".join(f"{k}:{v['declared_over_reference'][0]:.6g}"
                                               for k, v in f1.items() if abs(v['declared_over_reference'][0] - 1) > 1e-9
                                               or abs(v['declared_over_reference'][1]) > 1e-9))


# ------------------------------------------------------------------------------------------------------------------
CANDIDATES = {
    "A^2": [[("A", "ab"), ("A", "ab")]],
    "A^4": [[("A", "ab"), ("A", "ab"), ("A", "cd"), ("A", "cd")], [("A", "ab"), ("A", "bc"), ("A", "cd"), ("A", "da")],
            [("A", "ab"), ("A", "cd"), ("A", "ac"), ("A", "bd")]],
    "P A^2": [[("P", "abcd"), ("A", "ab"), ("A", "cd")], [("P", "abcd"), ("A", "ac"), ("A", "bd")]],
    "P^2 A": [[("P", "ABCD"), ("P", "EFGH"), ("A", "IJ")], [("P", "acde"), ("P", "bcde"), ("A", "ab")]],
    "P^3 A": [[("P", "ABCD"), ("P", "EFGH"), ("P", "IJab"), ("A", "ab")],
              [("P", "ABCD"), ("P", "abEF"), ("P", "abGH"), ("A", "IJ")],
              [("P", "ABCa"), ("P", "DEFb"), ("P", "GHIJ"), ("A", "ab")],
              [("P", "ABCa"), ("P", "DEFa"), ("P", "GHIb"), ("A", "bJ")],
              [("P", "abcd"), ("P", "abef"), ("P", "cdeg"), ("A", "fg")],
              [("P", "abcd"), ("P", "aefg"), ("P", "bcef"), ("A", "dg")],
              [("P", "abcd"), ("P", "abce"), ("P", "defg"), ("A", "fg")]],
    "P^2 A^2": [[("P", "abcd"), ("P", "abcd"), ("A", "ef"), ("A", "ef")],
                [("P", "abcd"), ("P", "abef"), ("A", "ef"), ("A", "cd")],
                [("P", "abcd"), ("P", "abce"), ("A", "ef"), ("A", "df")],
                [("P", "abcd"), ("P", "abef"), ("A", "ce"), ("A", "df")],
                [("P", "abcd"), ("P", "abef"), ("A", "cf"), ("A", "de")],
                [("P", "ABCa"), ("P", "DEFG"), ("A", "Ha"), ("A", "IJ")],
                [("P", "ABCa"), ("P", "DEFa"), ("A", "GH"), ("A", "IJ")]],
    "P A^3": [[("P", "ABCD"), ("A", "EF"), ("A", "GH"), ("A", "IJ")], [("P", "abcd"), ("A", "ab"), ("A", "ce"), ("A", "de")]],
    "A H Hb": [[("A", "ab"), ("H", "b"), ("Hb", "a")]],
    "A^2 H Hb": [[("A", "ab"), ("A", "ab"), ("H", "c"), ("Hb", "c")], [("A", "ab"), ("A", "ac"), ("H", "c"), ("Hb", "b")],
                 [("A", "ab"), ("A", "bc"), ("H", "a"), ("Hb", "c")]],
    "P A H Hb": [[("P", "abcd"), ("A", "ab"), ("H", "c"), ("Hb", "d")], [("P", "abcd"), ("A", "ac"), ("H", "b"), ("Hb", "d")]],
    "A D Db": [[("A", "ab"), ("D", "bcdef"), ("Db", "acdef")]],
    "A^2 D Db": [[("A", "ab"), ("A", "ab"), ("D", "cdefg"), ("Db", "cdefg")],
                 [("A", "ab"), ("A", "cd"), ("D", "cdefg"), ("Db", "abefg")],
                 [("A", "ab"), ("A", "cd"), ("D", "acefg"), ("Db", "bdefg")],
                 [("A", "ab"), ("A", "bc"), ("D", "adefg"), ("Db", "cdefg")]],
    "P A D Db": [[("P", "abcd"), ("A", "ab"), ("D", "cefgh"), ("Db", "defgh")],
                 [("P", "abcd"), ("A", "ef"), ("D", "abcgh"), ("Db", "defgh")],
                 [("P", "abcd"), ("A", "ef"), ("D", "defgh"), ("Db", "abcgh")],
                 [("P", "abcd"), ("A", "ef"), ("D", "abegh"), ("Db", "cdfgh")],
                 [("P", "abcd"), ("A", "ae"), ("D", "bcfgh"), ("Db", "defgh")],
                 [("P", "abcd"), ("A", "ae"), ("D", "defgh"), ("Db", "bcfgh")]],
    "A^2 H Db": [[("A", "ab"), ("A", "cd"), ("Hb", "e"), ("D", "abcde")], [("A", "ab"), ("A", "cd"), ("H", "e"), ("Db", "abcde")]],
    "P A H Db": [[("P", "abcd"), ("A", "ef"), ("Hb", "a"), ("D", "bcdef")], [("P", "abcd"), ("A", "ef"), ("Hb", "e"), ("D", "abcdf")],
                 [("P", "abcd"), ("A", "ae"), ("Hb", "f"), ("D", "bcdef")], [("P", "abcd"), ("A", "ef"), ("H", "a"), ("Db", "bcdef")],
                 [("P", "abcd"), ("A", "ae"), ("H", "f"), ("Db", "bcdef")]],
}


def s6_completeness(keys):
    t0 = time.time()
    res = {}
    allok = True
    for rep, cands in CANDIDATES.items():
        key = orbit_key(rep)
        cols = [r for r in range(NR) if keys[r] == key]
        has_eps = any(ch.isupper() for c in cands for _, s in c for ch in s)
        npts = 10 if has_eps else 14
        Q = rng.normal(size=(npts, C.NTOT))
        V = rows_at(Q)[:, cols]
        Vn = V / np.linalg.norm(V, axis=0)
        T = [C.tensors_from_q(q) for q in Q]
        out = []
        for c in cands:
            fscale = np.array([np.prod([np.linalg.norm(np.ravel(E.tensor_of(t, f))) for f, _ in c]) for t in T])
            vals = np.array([E.evaluate(t, c) for t in T])
            for part, v in (("Re", vals.real), ("Im", vals.imag)):
                nv = np.linalg.norm(v)
                rel_size = float(np.max(np.abs(v) / fscale))
                if rel_size < 1e-11:
                    out.append({"candidate": c, "part": part, "status": "identically zero", "max|v|/prod|field|": rel_size})
                    continue
                x, *_ = np.linalg.lstsq(Vn, v / nv, rcond=None)
                resid = float(np.linalg.norm(Vn @ x - v / nv))
                ok = resid < 1e-9
                allok &= ok
                out.append({"candidate": c, "part": part, "status": "in row span" if ok else "OUTSIDE ROW SPAN",
                            "rel_residual": resid})
        res[rep] = {"rows": [IDS[c] for c in cols], "npts": npts, "candidates": out}
        log(f"S6 {rep:10s}: " + "; ".join(f"{o['part']}:{o['status']}" + (f"({o.get('rel_residual', 0):.1e})"
                                                                           if 'rel_residual' in o else "") for o in out))
    res["all_ok"] = bool(allok)
    res["time_s"] = time.time() - t0
    R["S6_completeness"] = res


# ------------------------------------------------------------------------------------------------------------------
def s7_a0():
    t0 = time.time()
    Q = rng.normal(size=(12, C.NTOT))
    Q[:, C.SL["A"]] = 0.0
    v = rows_at(Q)
    q = Q[0]
    rows = CH.new_rows(q, hessian=True)
    g_nonA = max(float(np.max(np.abs(r.gradient[:C.N486]))) for r in rows.values())
    h_nonA = max(float(np.max(np.abs(r.hessian[:C.N486, :C.N486]))) for r in rows.values())
    lin = [pid for pid, r in rows.items() if np.max(np.abs(r.gradient[C.N486:])) > 0]
    R["S7_A0"] = {"max_abs_value_at_A0": float(np.max(np.abs(v))), "max_abs_nonA_gradient": g_nonA,
                  "max_abs_nonA_hessian": h_nonA, "rows_with_A_tadpole_at_generic_A0_point": lin,
                  "time_s": time.time() - t0}
    log(f"S7 A=0: {R['S7_A0']}")


# ------------------------------------------------------------------------------------------------------------------
def s8_g3211(G):
    t0 = time.time()
    import g3_sigma_hypercharge_audit_v20 as hc
    out = {}
    t3r = np.array(hc.T3R_INTEGER, float) / math.sqrt(2.0)
    tbl = np.array(hc.BL_INTEGER, float) / math.sqrt(3.0)
    out["chart531_T3R_unit_equals_repo_T3R_INTEGER/sqrt2"] = float(np.max(np.abs(CH.T3R_UNIT - t3r)))
    out["chart531_TBL_unit_equals_repo_BL_INTEGER/sqrt3"] = float(np.max(np.abs(CH.TBL_UNIT - tbl)))
    sm = hc.standard_sm_integer_basis()
    ad = C.my_adjoint_block()
    def act(vec, qa):
        M = sum(float(c) * ad[k] for k, c in enumerate(vec) if c)
        return M @ qa
    out["SM_generators_annihilate_T3R_vev"] = max(float(np.max(np.abs(act(v, t3r)))) for v in sm)
    out["SM_generators_annihilate_TBL_vev"] = max(float(np.max(np.abs(act(v, tbl)))) for v in sm)
    t3l = np.array(hc.T3L_INTEGER, float)
    out["T3R_vev_is_not_T3L (overlap)"] = float(abs(t3r @ t3l) / (np.linalg.norm(t3l)))
    # stabilizers with MY generators
    def stab(q):
        Tm = np.column_stack([g @ q for g in G])
        s = np.linalg.svd(Tm, compute_uv=False)
        return 45 - int(np.sum(s > 1e-9 * s[0]))
    pts = {"A only (omega_R, omega_BL)": CH.g3211_point(0, 0, 0, 0.3, 0.2),
           "A only T3R": CH.g3211_point(0, 0, 0, 0.3, 0.0),
           "Phi (p,a,omega) + A": CH.g3211_point(0.6, -0.5, 0.4, 0.3, 0.2, s=0.01, x=2.0),
           "... + sigma": CH.g3211_point(0.6, -0.5, 0.4, 0.3, 0.2, sigma=0.05, s=0.01, x=2.0)}
    out["stabilizer_dims_my_generators"] = {k: stab(q) for k, q in pts.items()}
    # F2: A-gradient of A04 at A = 0 with MY literal evaluator (linear in A: g_k = I(P, E_k))
    inv = {e["name"]: e for e in json.loads(CH.INVARIANTS_JSON.read_text(encoding="utf-8"))["A45_invariants"]}
    f2 = {}
    for (p, a, w) in ((0.6, -0.5, 0.4), (1.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        q = CH.g3211_point(p, a, w, 0.0, 0.0)
        t = C.tensors_from_q(q)
        g = np.zeros(45)
        for k in range(45):
            e = np.zeros(45)
            e[k] = 1.0
            t["A"] = C.a_matrix(e)
            g[k] = E.evaluate_spec(t, inv["A04_PPA_eps"]["machine_spec"]).real
        cT, cB = g @ t3r, g @ tbl
        resid = float(np.linalg.norm(g - cT * t3r - cB * tbl) / max(1e-300, np.linalg.norm(g)) if np.linalg.norm(g) else 0.0)
        f2[f"p={p},a={a},omega={w}"] = {"T3R_component": float(cT), "TBL_component": float(cB),
                                        "builder_formula_T3R": 2304 * a * w,
                                        "builder_formula_TBL": 2304 * p * a + 2304 / math.sqrt(3) * w * w,
                                        "residual_outside_span": resid}
    out["F2_A04_tadpole_my_evaluator"] = f2
    out["time_s"] = time.time() - t0
    R["S8_G3211"] = out
    log(f"S8 {out}")


# ------------------------------------------------------------------------------------------------------------------
def s9_fd():
    t0 = time.time()
    q = rng.normal(size=C.NTOT)
    rows = CH.new_rows(q, hessian=True)
    G = np.array([rows[i].gradient for i in IDS])
    worst_g = worst_h = 0.0
    for trial in range(3):
        u = rng.normal(size=C.NTOT)
        u /= np.linalg.norm(u)
        v = rng.normal(size=C.NTOT)
        v /= np.linalg.norm(v)
        h = 1e-3
        # rows are polynomials of degree <= 4: 5-point stencil exact up to rounding for d<=4
        f = lambda s: rows_at(q + s * u)[0]
        d1 = (-f(2 * h) + 8 * f(h) - 8 * f(-h) + f(-2 * h)) / (12 * h)
        an = G @ u
        worst_g = max(worst_g, float(np.max(np.abs(d1 - an) / np.linalg.norm(G, axis=1))))
        # mixed second derivative u^T H v
        fm = lambda a, b: rows_at(q + a * u + b * v)[0]
        mix = (fm(h, h) - fm(h, -h) - fm(-h, h) + fm(-h, -h)) / (4 * h * h)
        an2 = np.array([u @ rows[i].hessian @ v for i in IDS])
        hs = np.array([np.linalg.norm(rows[i].hessian) for i in IDS])
        worst_h = max(worst_h, float(np.max(np.abs(mix - an2) / hs)))
    R["S9_fd"] = {"worst_rel_gradient": worst_g, "worst_rel_mixed_hessian(O(h^2) stencil, h=1e-3)": worst_h,
                  "time_s": time.time() - t0}
    log(f"S9 {R['S9_fd']}")


def main():
    t0 = time.time()
    G = s1_generators()
    keys = s2_multidegrees()
    s3_invariance(G)
    s4_rank(keys)
    s7_a0()
    s9_fd()
    s8_g3211(G)
    s5_declared()
    s6_completeness(keys)
    R["total_time_s"] = time.time() - t0
    C.json_dump(R, OUT)
    log(f"wrote {OUT} ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
