"""Do natural (untuned) solutions of the general minimal SO(10) Yukawa sector exist?

Every good witness so far reproduces m_nu through a cancellation between
type-II and type-I contributions that are 170-700 times larger than m_nu.
Such points are unstable: one-loop right-handed-neutrino thresholds shift
sum m_nu by O(100%), with an O(1) dependence on the unknown quartic lam2.

Tuning measure at M_I (Takagi basis of M_R):
    T = ( |M_L| + sum_n |v_u^2 y_n^T y_n / M_n| ) / |m_nu|      (Frobenius norms)
T ~ 1 means no cancellation.

Search: the fast tree-level objective plus a one-sided tuning penalty
w * max(0, ln(T / T0)). Threshold corrections are small for natural points,
so the fast objective is adequate there; survivors are then re-checked with
the full threshold running (thresholds.py) at lam2 = 0, 0.5, 1.
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
import so10fit as S  # noqa: E402

VB = 6.313855e11
W_TUNE = 10.0


def tuning(st, p):
    b = st.build(p)
    vu = st.vu
    d, w = S.R.takagi(0.5 * (b["mR"] + b["mR"].T))
    y = w.conj().T @ (b["mD"].T / vu)
    parts = [np.linalg.norm(b["eps"] * b["F"])]
    parts += [np.linalg.norm(vu ** 2 * np.outer(y[i], y[i]) / d[i]) for i in range(3)]
    return float(sum(parts) / max(np.linalg.norm(b["mnu"]), 1e-300)), [float(v) for v in d]


class NaturalStratum(S.Stratum):
    def __init__(self, tan_beta, v_r, t0, **kw):
        super().__init__(tan_beta, v_r, **kw)
        self.t0 = t0

    def residuals(self, p):
        r = super().residuals(p)
        try:
            t, _ = tuning(self, p)
            extra = W_TUNE * max(0.0, math.log(t / self.t0))
        except Exception:
            extra = 1e4
        return np.append(r, extra if np.isfinite(extra) else 1e4)


_ST = None


def _init(tb, t0):
    global _ST
    _ST = NaturalStratum(tb, VB, t0)


def _one(seed):
    rng = np.random.default_rng(seed)
    p0 = S.random_start(rng)
    try:
        res = least_squares(_ST.residuals, p0, method="lm", x_scale="jac",
                            max_nfev=6000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        return float(2.0 * res.cost), res.x.tolist()
    except Exception:
        return 1e18, p0.tolist()


def main() -> None:
    from multiprocessing import Pool
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0_values = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [3.0, 10.0]
    out = []
    start = time.time()
    print(f"{'T0':>5} {'tanb':>5} {'chi2_ferm':>9} {'penalty':>8} {'tuning':>8} {'sum_mnu':>8} {'hits<16':>7}", flush=True)
    for t0 in t0_values:
        for tb in (3.0, 10.0, 25.0, 45.0):
            with Pool(max(1, os.cpu_count() - 2), initializer=_init, initargs=(tb, t0)) as pool:
                res = pool.map(_one, range(90000 + int(10 * t0) * 100 + int(tb), 90000 + int(10 * t0) * 100 + int(tb) + n),
                               chunksize=2)
            chis = np.array([c for c, _ in res])
            _, x = min(res, key=lambda q: q[0])
            st = NaturalStratum(tb, VB, t0)
            p = np.array(x)
            r = st.residuals(p)
            t, masses = tuning(st, p)
            lep = st.observables(p)["lep"]
            row = {"T0": t0, "tan_beta": tb, "v_R": VB, "chi2_fermion": float(r[:13] @ r[:13]),
                   "penalty": float(r[16:] @ r[16:]), "tuning": t, "M_R_GeV": masses,
                   "sum_mnu_eV": lep["sum_mnu_eV"], "hits_below_16": int((chis < 16).sum()),
                   "x": [float(v) for v in p]}
            out.append(row)
            json.dump(out, open("natural.json", "w"), indent=2)
            print(f"{t0:5.0f} {tb:5.0f} {row['chi2_fermion']:9.3f} {row['penalty']:8.3f} {t:8.2f}"
                  f" {row['sum_mnu_eV']:8.4f} {row['hits_below_16']:7d}", flush=True)
    print(f"\nelapsed {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
