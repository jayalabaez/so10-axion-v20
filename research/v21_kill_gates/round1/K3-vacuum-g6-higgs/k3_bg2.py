"""Barbieri-Giudice sensitivities at a solution: light levels (Hellmann-Feynman dm^2/dc_i = v^T Hess_i v) and lambda_eff
(central finite differences in each coupling), plus the tuning count (independent cancellations).
usage: python -B k3_bg2.py <solution npz> <tag>
"""
from __future__ import annotations
import sys, json, numpy as np
import k3_common as K
import k3_verify as VF

sol = np.load(K.SCRATCH / sys.argv[1]); c = sol["c"]; ids = VF.ids; tag = sys.argv[2]
H = VF.full_hessian(c); w, V = np.linalg.eigh(H)
ops = K.candidate.sm_label_operators(); C2L, C3 = ops["C2L"], ops["C3"]
light = [j for j in range(len(w)) if 1e-9 < w[j] < 10 * VF.EPS_HI]
rows = []
for j in light:
    v = V[:, j]; d = np.array([v @ VF.HESS[i] @ v for i in range(len(ids))]); sens = np.abs(c * d) / w[j]
    k = int(np.argmax(sens)); c2l = float(v @ C2L @ v); c3 = float(v @ C3 @ v)
    lab = "(1,2)" if abs(c2l - 0.75) < 1e-6 and abs(c3) < 1e-6 else ("(8,3)" if abs(c2l - 2) < 1e-6 and abs(c3 - 3) < 1e-6 else ("(1,1)" if c2l < 1e-6 and c3 < 1e-6 else f"C2L={c2l:.2f},C3={c3:.2f}"))
    rows.append({"m2": float(w[j]), "label": lab, "BG_max": float(sens[k]), "driver": ids[k], "top3": [(ids[i], float(sens[i])) for i in np.argsort(-sens)[:3]]})
# group by level
levels = {}
for r in rows:
    key = (r["label"], round(r["m2"], 9)); levels.setdefault(key, []).append(r)
summary = [{"label": k[0], "m2": k[1], "multiplicity": len(v), "BG_max": max(r["BG_max"] for r in v), "driver": v[0]["driver"], "top3": v[0]["top3"]} for k, v in sorted(levels.items(), key=lambda kv: kv[0][1])]
# lambda_eff sensitivity
lam0 = VF.lambda_eff_exact(c)["lambda_eff_all"]; sens_l = []
for i in range(len(ids)):
    h = 1e-4 * max(abs(c[i]), 1e-3); cp = c.copy(); cm = c.copy(); cp[i] += h; cm[i] -= h
    # keep stationarity: the gradient rows are linear in c; a single-coupling shift breaks it, so project onto the null space
    dl = (VF.lambda_eff_exact(cp)["lambda_eff_all"] - VF.lambda_eff_exact(cm)["lambda_eff_all"]) / (2 * h)
    sens_l.append((ids[i], float(abs(c[i] * dl) / abs(lam0))))
sens_l.sort(key=lambda t: -t[1])
out = {"solution": sys.argv[1], "light_levels": summary, "lambda_eff": lam0, "BG_lambda_top5": sens_l[:5],
       "note": "BG_max = max_i |c_i dX/dc_i| / |X| with X the light mass^2 (Hellmann-Feynman) or lambda_eff (finite differences; single-coupling shifts, stationarity not re-imposed)"}
json.dump(out, open(K.SCRATCH / f"bg2_{tag}.json", "w"), indent=1, default=float)
for s in summary: print(f"{s['label']:6s} m2 = {s['m2']:.4e} x{s['multiplicity']:2d}  BG = {s['BG_max']:.3g}  driver {s['driver']}  top3 {[(a.split('::')[1][:3], round(b, 1)) for a, b in s['top3']]}")
print("lambda_eff =", lam0, " BG_lambda top5:", [(a.split('::')[1][:3], round(b, 1)) for a, b in sens_l[:5]])
