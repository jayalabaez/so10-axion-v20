"""Parallel least-squares driver for so10fit, with a closure test.

Closure test: generate observables from a random parameter point, then fit
them from random starts. The per-restart recovery rate calibrates how many
restarts a real fit needs before "no good fit found" can be read as physics
rather than optimiser failure.
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

V_BENCH = 6.313855e11


class SyntheticStratum(S.Stratum):
    """Stratum whose targets are the observables of a chosen parameter point."""

    def __init__(self, tan_beta, v_r, p_true):
        super().__init__(tan_beta, v_r, y_max=1e9, planck=False)
        o = self.observables(p_true)
        self.m = dict(self.m)
        for k in ("u", "c", "t"):
            self.m[k] = o["up"][k]
        self.sig_up = {k: 0.05 * self.m[k] for k in ("u", "c", "t")}
        self.ckm = dict(o["ckm"])
        self.sig_ckm = {k: 0.05 * self.ckm[k] for k in self.ckm}
        lep = o["lep"]
        self.nufit = {"sin2_th12": (lep["sin2_th12"], 0.012),
                      "sin2_th23": (lep["sin2_th23"], 0.015),
                      "sin2_th13": (lep["sin2_th13"], 0.0006),
                      "dm21": (lep["dm21_eV2"], 0.02 * lep["dm21_eV2"]),
                      "dm31": (lep["dm31_eV2"], 0.01 * lep["dm31_eV2"]),
                      "delta_deg": (lep["delta_cp_deg"], 35.0)}

    def residuals(self, p):
        saved = S.NUFIT
        S.NUFIT = self.nufit
        try:
            return super().residuals(p)
        finally:
            S.NUFIT = saved


_ST = None


def _init(kind, args):
    global _ST
    if kind == "synthetic":
        _ST = SyntheticStratum(*args)
    elif kind == "custom":
        tb, v_r, kw = args
        _ST = S.Stratum(tb, v_r, **kw)
    else:
        _ST = S.Stratum(*args[:2], planck=args[2])


def _one(seed):
    rng = np.random.default_rng(seed)
    p0 = S.random_start(rng)
    try:
        res = least_squares(_ST.residuals, p0, method="lm", x_scale="jac",
                            max_nfev=6000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        return float(2.0 * res.cost), res.x.tolist()
    except Exception:
        return 1e18, p0.tolist()


def run_pool(kind, args, n, seed0=0):
    from multiprocessing import Pool
    with Pool(processes=max(1, os.cpu_count() - 2), initializer=_init,
              initargs=(kind, args)) as pool:
        return pool.map(_one, range(seed0, seed0 + n), chunksize=2)


def closure(n=160):
    rng = np.random.default_rng(424242)
    p_true = S.random_start(rng)
    p_true[14:17] = 0.0
    t = time.time()
    res = run_pool("synthetic", (10.0, V_BENCH, p_true), n)
    chis = np.array(sorted(c for c, _ in res))
    return {"restarts": n, "best_chi2": float(chis[0]),
            "fraction_chi2_below_1": float(np.mean(chis < 1.0)),
            "fraction_chi2_below_0.01": float(np.mean(chis < 0.01)),
            "median_chi2": float(np.median(chis)), "seconds": round(time.time() - t, 1)}


if __name__ == "__main__":
    print(json.dumps(closure(int(sys.argv[1]) if len(sys.argv) > 1 else 160), indent=2))
