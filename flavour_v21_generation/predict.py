"""Is sum m_nu a prediction of the generalised minimal SO(10) Yukawa sector?

Every unconstrained fit at the benchmark landed at sum m_nu = 0.066-0.069 eV
without sum m_nu being a fit target. With 14 physical parameters for 13
observables the solution set is (at least) one-dimensional, so that could be
a real constraint or just where the optimiser lands.

Test: add a tight pull forcing sum m_nu to a chosen value and record the best
achievable fermion chi2. Flat => not predicted. Rising => predicted.
Also reports the effective Majorana mass m_bb and the right-handed neutrino
spectrum at the best point.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import so10fit as S  # noqa: E402

VB = 6.313855e11
TB = 25.0
SIGMA = 0.0005


class Forced(S.Stratum):
    def __init__(self, target):
        super().__init__(TB, VB, planck=False)
        self.target = target

    def residuals(self, p):
        r = super().residuals(p)
        try:
            s = self.observables(p)["lep"]["sum_mnu_eV"]
            extra = (s - self.target) / SIGMA
        except Exception:
            extra = 1e4
        return np.append(r, extra if np.isfinite(extra) else 1e4)


_ST = None


def _init(target):
    global _ST
    _ST = Forced(target)


def _one(seed):
    rng = np.random.default_rng(seed)
    p0 = S.random_start(rng)
    try:
        res = least_squares(_ST.residuals, p0, method="lm", x_scale="jac",
                            max_nfev=6000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        return float(2.0 * res.cost), res.x.tolist()
    except Exception:
        return 1e18, p0.tolist()


def neutrino_extras(st, p):
    o = st.observables(p)
    b = o["build"]
    _, ve = S._takagi(b["me"])
    mprime = ve.conj().T @ b["mnu"] @ ve.conj()
    mz = st.nu_scale * (np.outer(st.nu_f, st.nu_f) * mprime)
    mbb = abs(mz[0, 0]) * 1e9
    mr = np.sort(np.linalg.svd(b["mR"], compute_uv=False))
    return {"m_bb_eV": mbb, "M_R_GeV": [float(v) for v in mr],
            "masses_eV": o["lep"]["mnu_eV"]}


if __name__ == "__main__":
    from multiprocessing import Pool
    targets = [0.0590, 0.0620, 0.0660, 0.0690, 0.0750, 0.0900, 0.1100]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 160
    out = []
    t0 = time.time()
    print(f"{'target':>7} {'got':>7} {'chi2_ferm':>9} {'chi2_tot':>9} {'m_bb':>8} {'hits<16':>7}", flush=True)
    for tgt in targets:
        with Pool(processes=max(1, os.cpu_count() - 2), initializer=_init, initargs=(tgt,)) as pool:
            res = pool.map(_one, range(9000, 9000 + n), chunksize=2)
        c, x = min(res, key=lambda t: t[0])
        st = Forced(tgt)
        p = np.array(x)
        r = st.residuals(p)
        extras = neutrino_extras(st, p)
        row = {"target": tgt, "sum_mnu_eV": st.observables(p)["lep"]["sum_mnu_eV"],
               "chi2_fermion": float(r[:13] @ r[:13]), "chi2_total": float(r @ r),
               "hits_below_16": int(sum(1 for cc, _ in res if cc < 16)), **extras,
               "x": [float(v) for v in p]}
        out.append(row)
        json.dump(out, open("predict.json", "w"), indent=2)
        print(f"{tgt:7.4f} {row['sum_mnu_eV']:7.4f} {row['chi2_fermion']:9.3f} {row['chi2_total']:9.3f}"
              f" {row['m_bb_eV']:8.5f} {row['hits_below_16']:7d}", flush=True)
    print(f"\nelapsed {time.time() - t0:.0f} s", flush=True)
