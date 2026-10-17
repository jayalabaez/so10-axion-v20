#!/usr/bin/env python3
"""Verifier: re-solve the two-loop chain with K3-compatible light contents (K3 says neither (8,2,2)_0 nor the
(8,3,1)+(1,3,1) pair can be light while the rest is heavy).  Uses vf_check's own MV routine and chain."""
import json, math, os, sys
from fractions import Fraction as F
import numpy as np
sys.argv = [sys.argv[0]]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("vf", os.path.join(HERE, "vf_check.py"))
# avoid re-running the whole script: exec only definitions by loading module (it prints; acceptable)
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    vf = importlib.util.module_from_spec(spec); spec.loader.exec_module(vf)

def light(content):
    base = [("cplx", vf.gr(1, 2, 2, 0), 1), ("cplx", vf.gr(1, 1, 3, 2), 1)]
    if content == "bid_DR":
        return base
    if content == "T2_minus_822":
        return base + [("real", vf.gr(8, 3, 1, 0), 1), ("real", vf.gr(1, 3, 1, 0), 1)]
    if content == "T2_minus_831_131":
        return base + [("cplx", vf.gr(8, 2, 2, 0), 1)]
    if content == "bid_DR_811":
        return base + [("real", vf.gr(8, 1, 1, 0), 1)]
    raise ValueError(content)

out = {}
for content in ("bid_DR", "T2_minus_822", "T2_minus_831_131", "bid_DR_811"):
    f = [("weyl", r, 9) for r in vf.SIXTEEN_G] + [("weyl", r, 2) for r in vf.TEN_G] + light(content)
    fn = [("weyl", r, 3) for r in vf.SIXTEEN_G] + light(content)
    vf.coef[content] = vf.mv(vf.G_CG, f)
    vf.coef[content + "noS"] = vf.mv(vf.G_CG, fn)
    row = {"b": [str(x) for x in vf.coef[content][0]]}
    for guess in ((math.log(2.5e13), math.log(2.5e16), 46.0), (math.log(1e10), math.log(1e16), 50.0), (math.log(1e12), math.log(3e15), 48.0)):
        r = vf.solve(content, 2, 1e13, guess)
        if r["ok"] and r["resid"] < 1e-8:
            break
    row.update(r)
    if r["ok"]:
        for L in (2, 3):
            row[f"Lambda_{L}L_over_MPl"] = vf.landau(r["M_U"], r["alpha_U_inv"], L, 1e17)[0] / vf.MPL
        row["tau_p_yr"] = vf.tau_p(r["M_U"], r["alpha_U_inv"])
    out[content] = row
    print(content, json.dumps(row, default=str))
with open(os.path.join(HERE, "vf_k3_contents.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)

# ---- MS-bar heavy-vector matching constant: alpha_high^-1 = alpha_low^-1 + S_V^i/(12 pi) at mu = M_V (Weinberg-Hall, LIT-abstract) ----
# S_V per G3221 factor for (3,2,2)_{-2/3}+cc and (3,1,1)_{4/3}+cc
SV = {}
for i in range(4):
    s = F(0)
    for reps, m in ((vf.gr(3, 2, 2, F(-2, 3)), 2), (vf.gr(3, 1, 1, F(4, 3)), 2)):
        S = F(reps[i][1]) * m
        for k in range(4):
            if k != i:
                S *= reps[k][0]
        s += S
    SV[i] = s
D = np.array([float(SV[i]) / (12 * math.pi) for i in range(4)])
print("S_V per factor (SU3,SU2L,SU2R,BL):", [str(SV[i]) for i in range(4)], "constant shift units:", D.round(4).tolist())
orig_chain = vf.chain
res = {}
for sign in (+1, -1):
    def chain_c(content, loops, M_s, x, _s=sign):
        g = orig_chain(content, loops, M_s, x)
        return g + _s * D   # alpha_high^-1 = alpha_low^-1 + D  (sign +1 is the MS-bar constant as quoted; -1 for the opposite convention)
    vf.chain = chain_c
    for content in ("T2", "T3"):
        r = vf.solve(content, 2, 1e13)
        for L in (2, 3):
            r[f"Lambda_{L}L_over_MPl"] = vf.landau(r["M_U"], r["alpha_U_inv"], L, 1e17)[0] / vf.MPL
        r["tau_p_yr"] = vf.tau_p(r["M_U"], r["alpha_U_inv"])
        res[f"{content}_vector_constant_sign{sign:+d}"] = r
        print(content, sign, json.dumps(r, default=str))
vf.chain = orig_chain
out["vector_matching_constant"] = {"S_V": [str(SV[i]) for i in range(4)], "shift_units": D.tolist(), "runs": res}
with open(os.path.join(HERE, "vf_k3_contents.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
