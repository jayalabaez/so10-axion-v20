"""sk2: SO(10) coupling at M_Pl,red (two loop, complete multiplets, b1 = 8, b2 = 7267/2 recomputed in sk2_numbers.py)
for the R2-B realisable-content unification points (alpha_U^-1, M_U read from R2-B REPORT.txt, section 0, by hand),
and the corresponding change of R2-V's small-instanton EST (measure (2 pi a)^16 e^{-2 pi a} at M_Pl, ratio to R2-V)."""
import json, math
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("n", str(Path(__file__).with_name("sk2_numbers.py")))
n = importlib.util.module_from_spec(spec); spec.loader.exec_module(n)
pts = {"round-1 T2+F17": (2.13e16, 25.9), "C0": (3.02e15, 33.26), "C1": (2.18e15, 33.53), "C2": (6.05e15, 34.64), "C1'": (3.20e15, 34.91)}
out = {}
ref = None
for k, (MU, a) in pts.items():
    aP, pole = n.ainv_at(MU, a)
    meas = (2 * math.pi * aP) ** 16 * math.exp(-2 * math.pi * aP) if aP else None
    if k.startswith("round"):
        ref = meas
    out[k] = {"M_U": MU, "aU^-1": a, "a^-1(MPl) 2L": aP, "pole": pole, "SI measure ratio to round-1 at MPl": (meas / ref if (meas and ref) else None)}
    # Landau scale (2L) beyond MPl
    aE, poleE = n.ainv_at(MU, a, mu_end=1e22)
    out[k]["2L Landau scale / MPl"] = (poleE / n.MPL) if poleE else None
print(json.dumps(out, indent=1))
Path(__file__).with_name("sk2_so10_r2b_env.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
