#!/usr/bin/env python3
"""Skeptic extra checks: C2 sensitivity (Yukawa conventions, y_t(MZ), integrator, S_V sign), coherent extremes,
Planck operator corners, rescue contents, M_s dependence, flavour-factor of the direct normalisation."""
import json, math
import numpy as np
import sk_lib as L
import sk_unify as U

out = {}
def run(tag, content, **kw):
    r, m = U.point(content, **kw)
    if r is None:
        print(tag, "no solution"); out[tag] = None; return None
    r["L2"] = m.landau(r["M_U"], r["aU"], 2)
    r["L3"] = m.landau(r["M_U"], r["aU"], 3)
    out[tag] = r
    print(f"{tag:42s} vR={r['v_R']:.3e} MU={r['M_U']:.3e} aU={r['aU']:.3f} tau={r['tau_repo']:.3e} "
          f"dir={r['tau_lat']:.3e} L2={r['L2']:.2f} L3={r['L3']:.2f}", flush=True)
    return r

run("C2 nominal", "C2")
run("C2 yuk_g=(4,3,3,1)", "C2", yuk_g=(4, 3, 3, 1))
run("C2 yt(MZ)=0.99", "C2", yt_mz=0.99)
run("C2 no Yukawa 2L terms", "C2", yukawa=False)
run("C2 RK45 rtol1e-9", "C2", method="RK45", rtol=1e-9)
run("C2 S_V off", "C2", sv=0)
run("C2 S_V opposite", "C2", sv=-1)
run("C2 (3,1,1) at M_X", "C2", r311=1.0)
for Ms, ys in ((3e12, 0.2), (8.2e12, 0.336), (1.21e13, 0.368)):
    run(f"C2 M_s={Ms:.3g}", "C2", M_s=Ms, y_s=ys)
for fg in (0.5, 2.0):
    for fl in (1 / 3, 3.0):
        run(f"C2 coherent GUTx{fg} lightx{fl:.3g}", "C2", gut_r={"*": fg}, light_r={"*": fl})
for s in (+1, -1):
    for c in (-1.0, 1.0, 0.5):
        run(f"C2 Planck s={s} c={c}", "C2", planck_c=c, planck_s=s)
for c in ("C1+813", "C1+622", "bidDR", "T2"):
    run(f"{c} nominal", c)
# T2 validation against K1 setting (S_V off, (3,1,1) at M_U, y_s=0.345)
run("T2 K1-setting", "T2", sv=0, r311=1.0, y_s=0.345)
# flavour factor of the direct normalisation: C_RL = 2k^2(1+|Vud|^2) instead of 4k^2
r = out["C2 nominal"]
t_alt = U.tau_lattice(r["M_U"], r["aU"], kRL=2 * (1 + 0.9737 ** 2))
print("C2 direct tau with C_RL=2k^2(1+Vud^2):", f"{t_alt:.3e}", " ratio to SK:", t_alt / 2.4e34)
print("C2 direct tau with W0=0.131+-0.017 (stat+sys, EST):", f"{U.tau_lattice(r['M_U'], r['aU'], W0=0.148):.3e}",
      f"{U.tau_lattice(r['M_U'], r['aU'], W0=0.114):.3e}")
# M_X needed for Super-K at aU=34.5
from scipy.optimize import brentq
print("M_X(SK) repo:", f"{brentq(lambda x: U.tau_repo(x, 34.5) - 2.4e34, 1e14, 1e17):.3e}",
      " direct:", f"{brentq(lambda x: U.tau_lattice(x, 34.5) - 2.4e34, 1e14, 1e17):.3e}")
print("MEMPHYS-rule check at (1e16, 25): repo", f"{U.tau_repo(1e16, 25):.3e}", " direct", f"{U.tau_lattice(1e16, 25):.3e}")
out["tau_dir_alt_flavour"] = t_alt
json.dump(out, open("sk_checks.json", "w"), indent=1, default=float)
