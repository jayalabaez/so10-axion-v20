"""Threshold-aware refits: can the tuned solutions re-tune once RHN thresholds are included?

Starting from each tree-level witness, refit with the neutrino observables
computed by full threshold running (thresholds.py) at a fixed lam2. If a
re-tuned solution exists, report its sum m_nu as a function of lam2: a strong
lam2 dependence means sum m_nu is not predicted without the scalar potential.
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
import so10fit as S  # noqa: E402
import thresholds as T  # noqa: E402


def residuals_with_thresholds(st, p, lam2):
    try:
        b = st.build(p)
        if np.linalg.svd(b["mD"].T / st.vu, compute_uv=False).max() > 3.0:
            return np.full(19, 1e3)                     # non-perturbative: skip the stiff running
        o = st.observables(p)
        lep, _ = T.observables_with_thresholds(st, p, lam2=lam2, rtol=1e-7, time_budget=3.0)
    except Exception:
        return np.full(19, 1e4)
    r = [(o["up"][k] - st.m[k]) / st.sig_up[k] for k in ("u", "c", "t")]
    r += [(o["ckm"][k] - st.ckm[k]) / st.sig_ckm[k] for k in ("s12", "s23", "s13", "J")]
    for key, obs in (("sin2_th12", "sin2_th12"), ("sin2_th23", "sin2_th23"), ("sin2_th13", "sin2_th13"),
                     ("dm21", "dm21_eV2"), ("dm31", "dm31_eV2")):
        c, s = S.NUFIT[key]
        r.append((lep[obs] - c) / s)
    c, s = S.NUFIT["delta_deg"]
    r.append(((lep["delta_cp_deg"] - c + 180.0) % 360.0 - 180.0) / s)
    r.extend(list(p[14:17]))
    r.append(math.sqrt(1e5) * max(0.0, lep["sum_mnu_eV"] - S.PLANCK) if st.planck else 0.0)
    r.append(1e2 * max(0.0, o["y126"] - st.y_max))
    r.append(1e2 * max(0.0, o["x_lo"] - o["x_hi"]))
    r = np.asarray(r, dtype=float)
    return np.where(np.isfinite(r), r, 1e4)


def refine(task):
    label, tb, vr, kw, x, lam2 = task
    st = S.Stratum(tb, vr, **kw)
    p0 = np.asarray(x)
    start = residuals_with_thresholds(st, p0, lam2)
    res = least_squares(lambda q: residuals_with_thresholds(st, q, lam2), p0, method="lm",
                        x_scale="jac", max_nfev=900, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    p = res.x
    r = residuals_with_thresholds(st, p, lam2)
    try:
        lep, _ = T.observables_with_thresholds(st, p, lam2=lam2, time_budget=30.0)
    except Exception:
        lep = {"sum_mnu_eV": float("nan")}
    tune, masses = N.tuning(st, p)
    return {"label": label, "tan_beta": tb, "lam2": lam2,
            "chi2_fermion_start": float(start[:13] @ start[:13]),
            "chi2_fermion": float(r[:13] @ r[:13]), "penalty": float(r[16:] @ r[16:]),
            "sum_mnu_eV": lep["sum_mnu_eV"], "tuning": tune, "M_R_GeV": masses,
            "nfev": int(res.nfev), "x": [float(v) for v in p]}


def main() -> None:
    from multiprocessing import Pool
    tasks = []
    for r in json.load(open("robust.json")):
        if r["case"] == "Ymax=1":
            for lam2 in (0.0, 0.5, 1.0):
                tasks.append((r["case"], r["tan_beta"], r["v_R"], {"y_max": 1.0}, r["x"], lam2))
    t0 = time.time()
    rows = []
    with Pool(max(1, os.cpu_count() - 2)) as pool:
        for d in pool.imap_unordered(refine, tasks, chunksize=1):
            rows.append(d)
            json.dump(rows, open("refit_thresholds.json", "w"), indent=2)
            print(f"done tanb={d['tan_beta']:.0f} lam2={d['lam2']:.2f} chi2 {d['chi2_fermion_start']:.1f} -> "
                  f"{d['chi2_fermion']:.3f}  sum_mnu={d['sum_mnu_eV']:.4f}  tuning={d['tuning']:.1f}  "
                  f"nfev={d['nfev']}  ({time.time() - t0:.0f}s)", flush=True)
    print(f"{'tanb':>5} {'lam2':>5} {'chi2 start':>11} {'chi2 refit':>11} {'penalty':>8} {'sum_mnu':>8} {'tuning':>8} {'nfev':>5}")
    for d in sorted(rows, key=lambda z: (z["tan_beta"], z["lam2"])):
        print(f"{d['tan_beta']:5.0f} {d['lam2']:5.2f} {d['chi2_fermion_start']:11.1f} {d['chi2_fermion']:11.3f}"
              f" {d['penalty']:8.3f} {d['sum_mnu_eV']:8.4f} {d['tuning']:8.1f} {d['nfev']:5d}")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
