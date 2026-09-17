"""Does the general minimal SO(10) Yukawa sector require normal ordering?

Fits the inverted-ordering (IO) NuFIT 6.0 data (IC24 with SK-atm variant, the
same variant the release uses for NO) at the axion benchmark scale, with the
same machinery, penalties and restart budget as realfit.py.

NuFIT 6.0, arXiv:2410.05380, Table 1, IO column (larger of the asymmetric
1-sigma errors used, as the release does for NO):
  sin^2 th12 = 0.308 +/- 0.012     sin^2 th23 = 0.550 +/- 0.015
  sin^2 th13 = 0.02231 +/- 0.00056 delta_CP  = 274 +/- 25 deg
  dm21 = 7.49e-5 +/- 0.19e-5       dm32 = -2.484e-3 +/- 0.020e-3
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
NUFIT_IO = {
    "sin2_th12": (0.308, 0.012),
    "sin2_th23": (0.550, 0.015),
    "sin2_th13": (0.02231, 0.00056),
    "dm21": (7.49e-5, 0.19e-5),
    "dm31": (-2.484e-3, 0.020e-3),   # holds dm32 for IO
    "delta_deg": (274.0, 25.0),
}


def pmns_io(mnu, me_diag):
    """PMNS extraction for inverted ordering (m3 < m1 < m2)."""
    sing, u_nu = S.R.takagi(0.5 * (mnu + mnu.T))
    _, u_e = S.R.takagi(me_diag)
    order = [1, 2, 0]
    masses = sing[order] * 1e9
    u = u_e.conj().T @ u_nu[:, order]
    s13 = abs(u[0, 2])
    c13 = math.sqrt(max(1e-30, 1 - s13 ** 2))
    s12 = min(1.0, abs(u[0, 1]) / c13)
    s23 = min(1.0, abs(u[1, 2]) / c13)
    c12 = math.sqrt(max(0.0, 1.0 - s12 ** 2))
    c23 = math.sqrt(max(0.0, 1.0 - s23 ** 2))
    jarl = np.imag(u[0, 0] * u[1, 1] * np.conj(u[0, 1]) * np.conj(u[1, 0]))
    sd = c12 * c23 * c13 ** 2 * s12 * s23 * s13
    sin_d = 0.0 if sd < 1e-30 else float(np.clip(jarl / sd, -1, 1))
    cd = 2.0 * s12 * c12 * c23 * s23 * s13
    cn = abs(u[1, 0]) ** 2 - s12 ** 2 * c23 ** 2 - c12 ** 2 * s23 ** 2 * s13 ** 2
    cos_d = 1.0 if cd < 1e-30 else float(np.clip(cn / cd, -1, 1))
    return {"mnu_eV": masses.tolist(), "sum_mnu_eV": float(masses.sum()),
            "dm21_eV2": float(masses[1] ** 2 - masses[0] ** 2),
            "dm31_eV2": float(masses[2] ** 2 - masses[1] ** 2),   # dm32
            "sin2_th12": s12 ** 2, "sin2_th23": s23 ** 2, "sin2_th13": s13 ** 2,
            "delta_cp_deg": math.degrees(math.atan2(sin_d, cos_d)) % 360.0}


class InvertedStratum(S.Stratum):
    def observables(self, p):
        saved = S.R._pmns_from_matrices
        S.R._pmns_from_matrices = pmns_io
        try:
            return super().observables(p)
        finally:
            S.R._pmns_from_matrices = saved

    def residuals(self, p):
        saved = S.NUFIT
        S.NUFIT = NUFIT_IO
        try:
            return super().residuals(p)
        finally:
            S.NUFIT = saved


_ST = None


def _init(tb):
    global _ST
    _ST = InvertedStratum(tb, VB)


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
    names = ["m_u", "m_c", "m_t", "s12", "s23", "s13", "J", "th12", "th23", "th13",
             "dm21", "dm32", "dCP", "z_d", "z_s", "z_b", "pen_planck", "pen_y126", "pen_sumrule"]
    out = []
    t0 = time.time()
    print(f"{'tanb':>5} {'chi2_tot':>9} {'chi2_ferm':>9} {'penalty':>8} {'sum_mnu':>8} {'hits<16':>7}", flush=True)
    tbs = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [10.0, 25.0]
    for tb in tbs:
        with Pool(processes=max(1, os.cpu_count() - 2), initializer=_init, initargs=(tb,)) as pool:
            res = pool.map(_one, range(50000 + int(tb), 50000 + int(tb) + n), chunksize=2)
        chis = np.array([c for c, _ in res])
        _, x = min(res, key=lambda t: t[0])
        st = InvertedStratum(tb, VB)
        p = np.array(x)
        parts = st.chi2_parts(p)
        o = st.observables(p)
        row = {"ordering": "IO", "tan_beta": tb, "v_R": VB, **parts,
               "sum_mnu_eV": o["lep"]["sum_mnu_eV"], "masses_eV": o["lep"]["mnu_eV"],
               "hits_below_16": int((chis < 16).sum()),
               "pulls": {k: round(float(v), 3) for k, v in zip(names, st.residuals(p))},
               "x": [float(v) for v in p]}
        out.append(row)
        json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else "ordering.json", "w"), indent=2)
        print(f"{tb:5.0f} {parts['chi2_total']:9.3f} {parts['chi2_fermion']:9.3f}"
              f" {parts['penalty']:8.3f} {row['sum_mnu_eV']:8.4f} {row['hits_below_16']:7d}", flush=True)
        print("      pulls:", row["pulls"], flush=True)
    print(f"\nelapsed {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
