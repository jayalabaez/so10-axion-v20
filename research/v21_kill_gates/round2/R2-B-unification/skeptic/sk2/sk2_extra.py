#!/usr/bin/env python3
"""Extra checks: (a) C2/C1p MC pass fractions with lattice normalisation x chain-specific A_R factor (0.69, from
sk2_asd.json); (b) C2 nominal Lambda_2L for a Phi-pair mass consistent with <Phi17> ~ 1.4 |Phi| and y_phi <= 1."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sk2_lib as L
mc = json.load(open(os.path.join(HERE, "sk2_spectra_mc.json")))["mc"]
asd = json.load(open(os.path.join(HERE, "sk2_asd.json")))["rows"]
out = {}
for c, key in [("C2", "C2"), ("C1p", "C1p"), ("C1", "C1"), ("C0", "C0")]:
    f = asd[key]["tau_factor_vs_2.726"]
    ok = [x for x in mc[c]["samples"] if x]
    n = len(ok)
    out[c] = {"A_R_factor": f,
              "f_repo": sum(x[3] > 2.4e34 and x[5] > 1 for x in ok) / n,
              "f_repo_x_AR": sum(x[3] * f > 2.4e34 and x[5] > 1 for x in ok) / n,
              "f_lat": sum(x[4] > 2.4e34 and x[5] > 1 for x in ok) / n,
              "f_lat_x_AR": sum(x[4] * f > 2.4e34 and x[5] > 1 for x in ok) / n,
              "f_lat_x_AR_W0_0.10": sum(x[4] * f * (0.131 / 0.10) ** 2 > 2.4e34 and x[5] > 1 for x in ok) / n,
              "f_lat_x_AR_and_vR_ge_1e11": sum(x[4] * f > 2.4e34 and x[5] > 1 and x[0] >= 1e11 for x in ok) / n,
              "n": n}
    print(c, out[c])
m = L.Model("C2"); s = m.solve((math.log(2e10), math.log(6e15), 40.0))
phi = s["M_U"] / (math.sqrt(0.25 + 1 / 6) * math.sqrt(4 * math.pi / s["aU"]))
out["C2_nominal"] = {"v_R": s["v_R"], "M_U": s["M_U"], "aU": s["aU"], "|Phi|": phi, "<Phi17>~1.4|Phi|": 1.4 * phi}
for Mphi in [1e17, 3e16, 1.4 * phi, s["M_U"]]:
    out["C2_nominal"][f"L2_Mphi_{Mphi:.3g}"] = L.landau_2l(s["M_U"], s["aU"], M_phi=Mphi)
print(out["C2_nominal"])
json.dump(out, open(os.path.join(HERE, "sk2_extra.json"), "w"), indent=1)
