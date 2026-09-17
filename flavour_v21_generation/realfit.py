"""Real fits of the generalised minimal SO(10) Yukawa sector.

13 fermion observables (3 up masses, 4 CKM, 6 neutrino) + 3 nuisance priors
(m_d, m_s, m_b), with vev sum rules, perturbativity and (optionally) the
Planck bound as one-sided penalties. 200 restarts per configuration; the
closure test gives a ~6% per-restart success rate on a known solution.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import fitdriver as D  # noqa: E402
import so10fit as S  # noqa: E402

V_BENCH = 6.313855e11


def describe(tb, v_r, planck, chi, x):
    st = S.Stratum(tb, v_r, planck=planck)
    p = np.asarray(x)
    o = st.observables(p)
    r = st.residuals(p)
    b = o["build"]
    names = ["m_u", "m_c", "m_t", "s12", "s23", "s13", "J",
             "th12", "th23", "th13", "dm21", "dm31", "dCP",
             "z_d", "z_s", "z_b", "pen_planck", "pen_y126", "pen_sumrule"]
    return {
        "tan_beta": tb, "v_R": v_r, "planck_on": planck,
        **st.chi2_parts(p),
        "pulls": {n: round(float(v), 3) for n, v in zip(names, r)},
        "sum_mnu_eV": round(o["lep"]["sum_mnu_eV"], 5),
        "planck_ok": o["lep"]["sum_mnu_eV"] < S.PLANCK,
        "desi_ok": o["lep"]["sum_mnu_eV"] < S.DESI,
        "delta_cp_deg": round(o["lep"]["delta_cp_deg"], 1),
        "r_H": round(b["rH"], 4), "abs_r_F": round(abs(b["rF"]), 4),
        "arg_r_F": round(float(np.angle(b["rF"])), 4),
        "rho": round(b["rho"], 4), "eps": float(b["eps"]),
        "y126": round(o["y126"], 4),
        "sum_rule_margin": round(o["x_hi"] - o["x_lo"], 5),
        "x": [float(v) for v in p],
    }


if __name__ == "__main__":
    configs = []
    for tb in (3.0, 10.0, 25.0, 45.0):
        configs.append((tb, V_BENCH, True))
    configs += [(10.0, V_BENCH, False), (10.0, 1.0e13, True), (10.0, 1.0e14, True)]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    out = []
    t0 = time.time()
    print(f"{'tanb':>5} {'v_R':>9} {'Planck':>6} {'chi2_tot':>9} {'chi2_ferm':>9}"
          f" {'penalty':>8} {'sum_mnu':>8} {'rho':>8} {'hits<16':>7}", flush=True)
    for tb, v_r, planck in configs:
        res = D.run_pool("real", (tb, v_r, planck), n, seed0=int(tb * 1000 + v_r % 997))
        chis = np.array([c for c, _ in res])
        best = min(res, key=lambda t: t[0])
        d = describe(tb, v_r, planck, *best)
        d["restarts"] = n
        d["hits_chi2_below_16"] = int((chis < 16.0).sum())
        d["median_chi2"] = float(np.median(chis))
        out.append(d)
        json.dump(out, open("realfit.json", "w"), indent=2)
        print(f"{tb:5.0f} {v_r:9.2e} {str(planck):>6} {d['chi2_total']:9.3f}"
              f" {d['chi2_fermion']:9.3f} {d['penalty']:8.3f} {d['sum_mnu_eV']:8.4f}"
              f" {d['rho']:8.3f} {d['hits_chi2_below_16']:7d}", flush=True)
    print(f"\nelapsed {time.time() - t0:.0f} s", flush=True)
