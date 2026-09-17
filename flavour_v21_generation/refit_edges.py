"""Threshold-aware tests of the two predictions.

A. Sum m_nu window edges: starting from converged threshold-aware solutions,
   force sum m_nu to targets outside the observed band and refit. A healthy
   fit at the forced value means the edge moved; a failure means it holds.
B. Normal ordering: refit the inverted-ordering witnesses with full threshold
   running at lam2 = 0.5.

Local refits only (global multistart with ~80 ms threshold evaluations is too
costly); they complement the tree-level global scans.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import natural as N  # noqa: E402
import ordering as O  # noqa: E402
import so10fit as S  # noqa: E402
import thresholds as T  # noqa: E402

VB = 6.313855e11
FORCE_SIGMA = 0.0005


def residuals(st, p, lam2, *, inverted=False, force=None):
    n_out = 19 + (1 if force is not None else 0)
    try:
        b = st.build(p)
        if np.linalg.svd(b["mD"].T / st.vu, compute_uv=False).max() > 3.0:
            return np.full(n_out, 1e3)
        o = st.observables(p)
        saved = S.R._pmns_from_matrices
        if inverted:
            S.R._pmns_from_matrices = O.pmns_io
        try:
            lep, _ = T.observables_with_thresholds(st, p, lam2=lam2, rtol=1e-7, time_budget=3.0)
        finally:
            S.R._pmns_from_matrices = saved
    except Exception:
        return np.full(n_out, 1e4)
    nufit = O.NUFIT_IO if inverted else S.NUFIT
    r = [(o["up"][k] - st.m[k]) / st.sig_up[k] for k in ("u", "c", "t")]
    r += [(o["ckm"][k] - st.ckm[k]) / st.sig_ckm[k] for k in ("s12", "s23", "s13", "J")]
    for key, obs in (("sin2_th12", "sin2_th12"), ("sin2_th23", "sin2_th23"), ("sin2_th13", "sin2_th13"),
                     ("dm21", "dm21_eV2"), ("dm31", "dm31_eV2")):
        c, s = nufit[key]
        r.append((lep[obs] - c) / s)
    c, s = nufit["delta_deg"]
    r.append(((lep["delta_cp_deg"] - c + 180.0) % 360.0 - 180.0) / s)
    r.extend(list(p[14:17]))
    r.append(math.sqrt(1e5) * max(0.0, lep["sum_mnu_eV"] - S.PLANCK) if st.planck else 0.0)
    r.append(1e2 * max(0.0, o["y126"] - st.y_max))
    r.append(1e2 * max(0.0, o["x_lo"] - o["x_hi"]))
    if force is not None:
        r.append((lep["sum_mnu_eV"] - force) / FORCE_SIGMA)
    r = np.asarray(r, dtype=float)
    return np.where(np.isfinite(r), r, 1e4)


def run_task(task):
    kind, tb, lam2, x, force, kw = task
    st = S.Stratum(tb, VB, **kw)
    inverted = kind == "io"
    p0 = np.asarray(x)
    start = residuals(st, p0, lam2, inverted=inverted, force=force)
    res = least_squares(lambda q: residuals(st, q, lam2, inverted=inverted, force=force), p0,
                        method="lm", x_scale="jac", max_nfev=900, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    p = res.x
    r = residuals(st, p, lam2, inverted=inverted, force=force)
    saved = S.R._pmns_from_matrices
    if inverted:
        S.R._pmns_from_matrices = O.pmns_io
    try:
        lep, _ = T.observables_with_thresholds(st, p, lam2=lam2, time_budget=30.0)
        smnu = lep["sum_mnu_eV"]
    except Exception:
        smnu = float("nan")
    finally:
        S.R._pmns_from_matrices = saved
    try:
        tune = N.tuning(st, p)[0]
    except Exception:
        tune = float("nan")
    return {"kind": kind, "tan_beta": tb, "lam2": lam2, "force_eV": force,
            "chi2_fermion_start": float(start[:13] @ start[:13]),
            "chi2_fermion": float(r[:13] @ r[:13]), "penalty": float(r[16:19] @ r[16:19]),
            "sum_mnu_eV": smnu, "tuning": tune, "nfev": int(res.nfev), "x": [float(v) for v in p]}


def main() -> None:
    from multiprocessing import Pool
    refits = json.load(open("refit_thresholds.json"))
    tasks = []
    for lam2 in (0.0, 0.5):
        base = [d for d in refits if d["tan_beta"] == 10.0 and d["lam2"] == lam2][0]
        for target in (0.058, 0.061, 0.076, 0.082):
            tasks.append(("forced", 10.0, lam2, base["x"], target, {"y_max": 1.0, "planck": False}))
    io_witnesses = json.load(open("ordering.json")) + json.load(open("ordering_extra.json"))
    for d in io_witnesses:
        tasks.append(("io", d["tan_beta"], 0.5, d["x"], None, {}))
    t0 = time.time()
    rows = []
    with Pool(max(1, os.cpu_count() - 2)) as pool:
        for d in pool.imap_unordered(run_task, tasks, chunksize=1):
            rows.append(d)
            json.dump(rows, open("refit_edges.json", "w"), indent=2)
            tag = f"force={d['force_eV']}" if d["kind"] == "forced" else "inverted ordering"
            print(f"done {d['kind']:6s} tanb={d['tan_beta']:.0f} lam2={d['lam2']:.1f} {tag:18s} "
                  f"chi2 {d['chi2_fermion_start']:.1f} -> {d['chi2_fermion']:.3f}  sum_mnu={d['sum_mnu_eV']:.4f}  "
                  f"tuning={d['tuning']:.1f}  nfev={d['nfev']}  ({time.time() - t0:.0f}s)", flush=True)
    print(f"\nelapsed {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
