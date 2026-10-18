"""Minimum alpha_U^-1 at M_U for Lambda_nL >= M_Pl,red (SO(10) phase, pure gauge, copy of R2-B lib; EST +-1 unit)."""
import json, math
from scipy.optimize import brentq
from landau_screen import BASE, landau
VAR = {"B63+v20": BASE, "+45_H": BASE + [("45", "real", 1)], "+45_H+54_H": BASE + [("45", "real", 1), ("54", "real", 1)],
       "+16_H": BASE + [("16", "cplx", 1)], "+120_H(cplx)": BASE + [("120", "cplx", 1)], "-210+45+54": [c for c in BASE if c[0] != "210"] + [("45", "real", 1), ("54", "real", 1)]}
out = {}
for name, cont in VAR.items():
    row = {}
    for MU in (3e15, 6e15, 1e16, 2e16):
        for L in (2, 3):
            f = lambda a: landau(cont, MU, a, L) - 1.0
            try:
                row[f"{MU:.0e}_L{L}"] = round(brentq(f, 5.0, 80.0, xtol=1e-3), 2)
            except ValueError:
                row[f"{MU:.0e}_L{L}"] = None
    out[name] = row; print(name, row)
json.dump(out, open("landau_threshold.json", "w"), indent=1)
