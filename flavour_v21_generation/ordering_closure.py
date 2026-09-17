"""Closure test for inverted ordering: optimiser failure or physics?

Stage A: search the model for any parameter point whose light-neutrino
         spectrum is inverted-ordering with the observed splittings.
         If the model cannot produce such a spectrum at all, IO is excluded
         structurally.
Stage B: if one exists, take its full observables as synthetic IO targets and
         fit them from random starts. A healthy recovery rate means the real
         IO failure is physics, not the optimiser.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import ordering as O  # noqa: E402
import so10fit as S  # noqa: E402

TB = 10.0
VB = O.VB


def spectrum_residuals(p, st):
    try:
        lep = st.observables(p)["lep"]
    except Exception:
        return np.full(4, 1e4)
    r = [(lep["dm21_eV2"] - 7.49e-5) / 0.19e-5,
         (lep["dm31_eV2"] + 2.484e-3) / 0.02e-3,
         max(0.0, lep["sum_mnu_eV"] - 0.12) * 1e3,
         max(0.0, 0.0 - lep["mnu_eV"][2]) * 1e6]
    r = np.asarray(r, dtype=float)
    return np.where(np.isfinite(r), r, 1e4)


class IOSynthetic(O.InvertedStratum):
    def __init__(self, p_true):
        super().__init__(TB, VB, y_max=1e9, planck=False)
        o = self.observables(p_true)
        self.m = dict(self.m)
        for k in ("u", "c", "t"):
            self.m[k] = o["up"][k]
        self.sig_up = {k: 0.05 * self.m[k] for k in ("u", "c", "t")}
        self.ckm = dict(o["ckm"])
        self.sig_ckm = {k: 0.05 * self.ckm[k] for k in self.ckm}
        lep = o["lep"]
        self.io_targets = {
            "sin2_th12": (lep["sin2_th12"], 0.012), "sin2_th23": (lep["sin2_th23"], 0.015),
            "sin2_th13": (lep["sin2_th13"], 0.00056), "dm21": (lep["dm21_eV2"], 0.19e-5),
            "dm31": (lep["dm31_eV2"], 0.020e-3), "delta_deg": (lep["delta_cp_deg"], 25.0)}

    def residuals(self, p):
        saved_nufit, saved_pmns = S.NUFIT, S.R._pmns_from_matrices
        S.NUFIT, S.R._pmns_from_matrices = self.io_targets, O.pmns_io
        try:
            return S.Stratum.residuals(self, p)
        finally:
            S.NUFIT, S.R._pmns_from_matrices = saved_nufit, saved_pmns


_ST = None


def _init_a():
    global _ST
    _ST = O.InvertedStratum(TB, VB, y_max=1e9, planck=False)


def _one_a(seed):
    rng = np.random.default_rng(seed)
    p0 = S.random_start(rng)
    try:
        res = least_squares(lambda p: spectrum_residuals(p, _ST), p0, method="trf",
                            max_nfev=3000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        return float(2 * res.cost), res.x.tolist()
    except Exception:
        return 1e18, p0.tolist()


def _init_b(p_true):
    global _ST
    _ST = IOSynthetic(np.asarray(p_true))


def _one_b(seed):
    rng = np.random.default_rng(seed)
    p0 = S.random_start(rng)
    try:
        res = least_squares(_ST.residuals, p0, method="lm", x_scale="jac",
                            max_nfev=6000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        return float(2 * res.cost), res.x.tolist()
    except Exception:
        return 1e18, p0.tolist()


def main() -> None:
    from multiprocessing import Pool
    procs = max(1, os.cpu_count() - 2)
    out = {}
    with Pool(procs, initializer=_init_a) as pool:
        stage_a = pool.map(_one_a, range(70000, 70200), chunksize=2)
    chis = np.array([c for c, _ in stage_a])
    best_a = min(stage_a, key=lambda t: t[0])
    out["stage_a"] = {"restarts": 200, "best_spectrum_chi2": float(best_a[0]),
                      "fraction_io_spectrum_found": float(np.mean(chis < 1.0))}
    print("stage A (does the model produce an IO spectrum at all?):", out["stage_a"], flush=True)
    if best_a[0] < 1.0:
        with Pool(procs, initializer=_init_b, initargs=(best_a[1],)) as pool:
            stage_b = pool.map(_one_b, range(80000, 80160), chunksize=2)
        cb = np.array(sorted(c for c, _ in stage_b))
        out["stage_b"] = {"restarts": 160, "best_chi2": float(cb[0]),
                          "fraction_chi2_below_1": float(np.mean(cb < 1.0)),
                          "median_chi2": float(np.median(cb))}
        print("stage B (IO closure recovery):", out["stage_b"], flush=True)
    json.dump(out, open("ordering_closure.json", "w"), indent=2)


if __name__ == "__main__":
    main()
