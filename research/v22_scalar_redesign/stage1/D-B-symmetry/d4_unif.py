"""D-B-symmetry, criterion D4 (two-loop unification, proton decay in the lattice x A_R normalisation, Landau) for V1.

V1 changes, relative to the R2-B contents: (i) the SO(10) phase gains one complex 10 (H2); (ii) the two light (1,2,2)_0
are the H1 and H2 bidoublets instead of H10 + Sigma (gauge-identical: no change below M_U); (iii) the heavy spectrum
gains H2's colour triplets and loses the H2 bidoublet / gains the Sigma bidoublet (nominal: all heavy at M_U -> no
one-loop threshold change).  So v_R, M_U, alpha_U and tau are the R2-B values; Lambda_2L / Lambda_3L move.
r2b_lib.py / r2b_model.py copied UNEDITED from R2-B; the extra 10 is added by monkey-patching SO10_BASE / X_CPLX.
tau_LA = direct lattice W0 = 0.131 GeV^2 with the chain A_R = 3.28 (= repository / (4.53 x 1.45) ~ repository / 6.5).
Writes d4_unif.json.
"""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2b_model as M   # noqa: E402

KEYS = ("ok", "v_R", "M_U", "alpha_U_inv", "tau_p_yr", "L2", "L3", "b_G3221", "resid_max")
BASE = list(M.SO10_BASE)
XC = list(M.X_CPLX)
out = {"settings": "R2-B nominal: M_s=1e13, y_s=0.336, M_phi=1e17, MS-bar S_V (+1), c=0, Am45 (3,1,1) ratio; 2L"}
t0 = time.time()
for cont in ("C2", "C1+622", "C1", "C1p"):
    for label, extra10 in (("R2B_reference", 0), ("V1_plus_H2", 1)):
        M.SO10_BASE = BASE + ([("10", "cplx", 1)] if extra10 else [])
        M.X_CPLX = XC + ([("10", -2, 1)] if extra10 else [])
        for ys, Ms in ((0.336, 1e13), (0.368, 1.21e13), (0.304, 1e13)):
            p = M.Params(light=M.CONTENTS[cont], loops=2, sv_sign=+1, y_s=ys, M_s=Ms)
            r = M.full_point(p, landau_loops=(2, 3))
            rec = {k: r.get(k) for k in KEYS if k in r}
            if r.get("ok"):
                rec["tau_LA_yr"] = M.proton_lifetime_direct_years(r["M_U"], r["alpha_U_inv"], A=3.28)
                rec["tau_dir_yr"] = M.proton_lifetime_direct_years(r["M_U"], r["alpha_U_inv"])
                rec["b_so10_lo"] = [str(x) for x in M.so10_coeffs(M.SO10_BASE)]
            key = f"{cont}|{label}|ys{ys}|Ms{Ms:.3g}"
            out[key] = rec
            print(key, json.dumps({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in rec.items() if k not in ("b_G3221",)},
                                  default=str), flush=True)
M.SO10_BASE = BASE; M.X_CPLX = XC
out["seconds"] = time.time() - t0
(HERE / "d4_unif.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("done", out["seconds"])
