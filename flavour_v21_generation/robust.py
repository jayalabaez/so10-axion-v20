"""Robustness: strict perturbativity (Y_max = 1) and strict experimental errors."""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import fitdriver as D  # noqa: E402
import so10fit as S  # noqa: E402

VB = 6.313855e11
NAMES = ["m_u", "m_c", "m_t", "s12", "s23", "s13", "J", "th12", "th23", "th13",
         "dm21", "dm31", "dCP", "z_d", "z_s", "z_b", "pen_planck", "pen_y126", "pen_sumrule"]
CONFIGS = [
    ("Ymax=1", 3.0, VB, {"y_max": 1.0}),
    ("Ymax=1", 10.0, VB, {"y_max": 1.0}),
    ("Ymax=1", 25.0, VB, {"y_max": 1.0}),
    ("Ymax=1", 45.0, VB, {"y_max": 1.0}),
    ("strict-errors", 25.0, VB, {"floor": 0.0, "s12_floor": 0.0}),
    ("strict+Ymax=1", 45.0, VB, {"floor": 0.0, "s12_floor": 0.0, "y_max": 1.0}),
]


def main() -> None:
    out = []
    t0 = time.time()
    print(f"{'case':>14} {'tanb':>5} {'chi2_tot':>9} {'chi2_ferm':>9} {'penalty':>8}"
          f" {'sum_mnu':>8} {'y126':>6} {'rho':>8} {'hits<16':>7}", flush=True)
    for tag, tb, vr, kw in CONFIGS:
        res = D.run_pool("custom", (tb, vr, kw), 200, seed0=int(tb * 77) + len(out) * 1000)
        chis = np.array([c for c, _ in res])
        _, x = min(res, key=lambda t: t[0])
        st = S.Stratum(tb, vr, **kw)
        p = np.array(x)
        o = st.observables(p)
        parts = st.chi2_parts(p)
        row = {"case": tag, "tan_beta": tb, "v_R": vr, **kw, **parts,
               "sum_mnu_eV": o["lep"]["sum_mnu_eV"], "y126": float(o["y126"]),
               "rho": o["build"]["rho"], "hits_below_16": int((chis < 16).sum()),
               "pulls": {k: round(float(v), 3) for k, v in zip(NAMES, st.residuals(p))},
               "x": [float(v) for v in p]}
        out.append(row)
        json.dump(out, open("robust.json", "w"), indent=2)
        print(f"{tag:>14} {tb:5.0f} {parts['chi2_total']:9.3f} {parts['chi2_fermion']:9.3f}"
              f" {parts['penalty']:8.3f} {row['sum_mnu_eV']:8.4f} {row['y126']:6.3f}"
              f" {row['rho']:8.3f} {row['hits_below_16']:7d}", flush=True)
    print(f"\nelapsed {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
