#!/usr/bin/env python3
"""SKEPTIC D3 check 4 (NUM, exact polynomial interpolation): boundedness from below of the L6 potential along the
direction reached by my descent(s).  V_c(lambda d) is an exact quartic polynomial in lambda (V is a quartic in the chart
coordinates), so five J-path evaluations fix its coefficients a0..a4 exactly (up to floating point); a4 < 0 means V is
unbounded below along the ray d (tree level), i.e. the design point has NO global minimum at all.
Also evaluates a4 along the pure H10 / Sigma / S sub-directions of d and along the designer's own deep endpoints.
usage: python -B sk_bfb.py <npz with qbest or qmin> [key]
"""
import sys, json
import numpy as np
from fractions import Fraction
import sk_loader as LD

f = sys.argv[1]; key = sys.argv[2] if len(sys.argv) > 2 else "qbest"
sol = np.load(LD.VAC / "L6_S2_U8362e_R.npz"); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
q = np.load(f)[key]


def coeffs_along(d, scale=1.0):
    lams = np.array([0.0, 1.0, 2.0, 3.0, 4.0]) * scale
    Vs = np.array([float(c @ LD.J_at(l * d, ids)) for l in lams])
    A = np.vander(lams, 5, increasing=True)
    a = np.linalg.solve(A, Vs)
    # check with a sixth point
    l6 = 5.0 * scale; pred = sum(a[k] * l6 ** k for k in range(5)); actual = float(c @ LD.J_at(l6 * d, ids))
    return a.tolist(), abs(pred - actual) / max(1.0, abs(actual))


out = {"file": f, "|q|": float(np.linalg.norm(q)), "blocks": LD.block_norms(q)}
d = q / np.linalg.norm(q)
a, err = coeffs_along(d)
out["full_direction"] = {"a0..a4": a, "check_rel_err": err}
print("full direction: a =", np.round(a, 6), "rel err", err, flush=True)
# sub-directions: keep only some blocks
for name, keep in (("H10+Sigma+S", ["H10", "Sigma126bar", "S"]), ("H10+Sigma", ["H10", "Sigma126bar"]),
                   ("Phi+H10+Sigma+S (no Phi17)", ["Phi210", "H10", "Sigma126bar", "S"])):
    qq = np.zeros_like(q)
    for k in keep:
        qq[LD.BLOCKS[k]] = q[LD.BLOCKS[k]]
    dd = qq / np.linalg.norm(qq)
    a2, e2 = coeffs_along(dd)
    out[name] = {"a0..a4": a2, "check_rel_err": e2}
    print(name, ": a =", np.round(a2, 6), "rel err", e2, flush=True)
json.dump(out, open(LD.HERE / ("sk_bfb_" + f.split("\\")[-1].split("/")[-1].replace(".npz", "") + ".json"), "w"), indent=1)
