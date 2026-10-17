#!/usr/bin/env python3
"""Independent nominal checks of R2-B (own code sk2_lib.py)."""
import json
import math
import sys
from fractions import Fraction as Fr

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
import sk2_lib as L

out = {}
out["completeness"] = L.check_completeness()
b, bij = L.mv(L.CG_SM, L.sm_fields(False))
out["SM_b"] = [str(x) for x in b]
out["SM_bij"] = [[str(x) for x in r] for r in bij]
bS, _ = L.mv(L.CG_SM, L.sm_fields(True))
out["SM+S_b"] = [str(x) for x in bS]
for c in ["C0", "C1", "C2", "C1p"]:
    b1, bij1 = L.mv(L.CG_G, L.g_fields(L.CONT[c], True))
    b0, _ = L.mv(L.CG_G, L.g_fields(L.CONT[c], False))
    out[f"{c}_b_withS"] = [str(x) for x in b1]
    out[f"{c}_b_noS"] = [str(x) for x in b0]
    out[f"{c}_bij_withS"] = [[str(x) for x in r] for r in bij1]
out["SO10_b_lo"] = [str(x) for x in L.so10_b(False)]
out["SO10_b_hi"] = [str(x) for x in L.so10_b(True)]
SV = [a + b for a, b in zip(L.sv_const(L.VEC322, 2), L.sv_const(L.VEC311, 2))]
out["S_V_MU"] = [str(x) for x in SV]
out["S_V_Y_vR"] = str(L.sv_const(L.sm(1, "1", "1"), 2)[0])
print(json.dumps({k: out[k] for k in out}, indent=None)[:3000])

guess = {"C0": (math.log(6e12), math.log(3e15), 40.0), "C1": (math.log(8e12), math.log(2e15), 40.0),
         "C2": (math.log(2e10), math.log(6e15), 40.0), "C1p": (math.log(1e11), math.log(3e15), 40.0)}
rows = []
for c in ["C0", "C1", "C2", "C1p"]:
    for loops in (1, 2):
        for sv in (1.0, 0.0, -1.0):
            if loops == 1 and sv != 1.0:
                continue
            for yuk in ((True, False) if (loops == 2 and sv == 1.0) else (True,)):
                m = L.Model(c, loops=loops, sv=sv, yukawa=yuk)
                r = m.solve(guess[c])
                if not r["ok"]:
                    # retry with other guesses
                    for gss in [(math.log(1e10), math.log(1e16), 45.0), (math.log(1e12), math.log(5e15), 45.0)]:
                        r = m.solve(gss)
                        if r["ok"]:
                            break
                row = {"content": c, "loops": loops, "sv": sv, "yukawa": yuk, **r}
                if r["ok"]:
                    row["tau_repo"] = L.tau_repo(r["M_U"], r["aU"])
                    row["tau_lat_W0.131"] = L.tau_lattice(r["M_U"], r["aU"])
                    row["tau_bchpt_a0.0144"] = L.tau_bchpt(r["M_U"], r["aU"])
                    row["tau_bchpt_a0.0112"] = L.tau_bchpt(r["M_U"], r["aU"], alpha=0.0112)
                    if loops == 2:
                        row["L2_MPl"] = L.landau_2l(r["M_U"], r["aU"], yuk=yuk)
                rows.append(row)
                print(f"{c:4s} {loops}L sv={sv:+.0f} yuk={int(yuk)}  vR={r['v_R']:.3e} MU={r['M_U']:.3e} "
                      f"aU={r['aU']:.3f} res={r['res']:.1e} ok={r['ok']}"
                      + (f" tau_repo={row['tau_repo']:.3e} tau_lat={row['tau_lat_W0.131']:.3e} "
                         f"tau_bchpt144={row['tau_bchpt_a0.0144']:.3e} L2={row.get('L2_MPl', float('nan')):.2f}"
                         if r["ok"] else ""), flush=True)
out["rows"] = rows
# normalisation ratios and Super-K mass bounds at aU^-1 = 34.5
out["ratio_repo_over_lattice"] = L.tau_repo(1e16, 34.5) / L.tau_lattice(1e16, 34.5)
out["ratio_repo_over_bchpt0.0144"] = L.tau_repo(1e16, 34.5) / L.tau_bchpt(1e16, 34.5)
out["ratio_repo_over_bchpt0.0112"] = L.tau_repo(1e16, 34.5) / L.tau_bchpt(1e16, 34.5, alpha=0.0112)
for nm, fn in [("repo", L.tau_repo), ("lat", L.tau_lattice), ("bchpt144", L.tau_bchpt)]:
    out[f"MX_SK_{nm}_aU34.5"] = (2.4e34 / fn(1.0, 34.5)) ** 0.25
    out[f"tau_{nm}_1e16_aU25"] = fn(1e16, 25.0)
print({k: v for k, v in out.items() if k.startswith(("ratio", "MX_", "tau_"))})
json.dump(out, open(__file__.replace(".py", ".json"), "w"), indent=1, default=str)
