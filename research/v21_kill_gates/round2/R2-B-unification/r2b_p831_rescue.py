#!/usr/bin/env python3
"""P831 / P831b heavy spectrum (r2b_p831.json, assigned m^2/|Phi|^2) transplanted (EST) onto the rescue candidates
C1+813, C1+622, C1+822 and onto C2 with the direct-lattice lifetime added; also the S_V sign variants for C2."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

P = json.load(open(os.path.join(HERE, "r2b_p831.json")))


def solve(light, m2, loops=2, extra=None, sv=+1):
    aU = 33.0
    row = None
    for _ in range(5):
        g = math.sqrt(4 * math.pi / aU)
        mx_phi = M.MX_OVER_G_PHI * g
        gr = {n: math.sqrt(v) / mx_phi for n, v in m2.items() if n not in light}
        if extra:
            gr.update(extra)
        p = M.Params(light=light, gut_ratios=gr, loops=loops, sv_sign=sv)
        row = M.full_point(p, landau_loops=(loops,), x_opts=(None,))
        if not row.get("ok"):
            break
        if abs(row["alpha_U_inv"] - aU) < 1e-4:
            break
        aU = row["alpha_U_inv"]
    out = {k: row.get(k) for k in ("ok", "v_R", "M_U", "alpha_U_inv", "tau_p_yr", f"L{loops}")}
    if row.get("ok"):
        out["tau_dir"] = M.proton_lifetime_direct_years(row["M_U"], row["alpha_U_inv"])
    return out


res = {}
for tag in ("P831", "P831b"):
    m2 = P[tag]["assigned_m2_over_Phi2"]
    for cont in ("C1+813", "C1+622", "C1+822"):
        light = M.CONTENTS[cont]
        for loops in (2, 3):
            key = f"{tag}|{cont}|{loops}L"
            res[key] = solve(light, m2, loops)
            print(key, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in res[key].items()}, flush=True)
    for f in (0.3, 1.0, 2.0):
        for sv in (+1, -1):
            key = f"{tag}|C2|(8,3,1)x{f:g}|sv{sv:+d}"
            res[key] = solve(M.CONTENTS["C2"], m2, 2, extra={"210:(8,3,1)_0": f}, sv=sv)
            print(key, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in res[key].items()}, flush=True)
    # spectrum rescaled by a common factor (all heavy scalars x lam), C2 and C0
    for lam in (1.0, 2.0, 3.0, 5.0):
        for cont in ("C0", "C2"):
            m2s = {n: v * lam ** 2 for n, v in m2.items()}
            extra = {"210:(8,3,1)_0": 1.0 * lam} if cont == "C2" else None
            key = f"{tag}|{cont}|spectrum_x{lam:g}"
            res[key] = solve(M.CONTENTS[cont], m2s, 2, extra=extra)
            print(key, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in res[key].items()}, flush=True)
with open(os.path.join(HERE, "r2b_p831_rescue.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print("done")
