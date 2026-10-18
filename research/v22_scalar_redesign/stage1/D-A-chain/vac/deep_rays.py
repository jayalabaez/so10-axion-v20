"""D3 sanity check (NUM): evaluate an lp_sm solution c on the round-1/round-2 deep H-Sigma configurations.
For every banked point q_k of the R2-A descents (52 gate + P831 descents) and the 8 R2-A-skeptic endpoints:
   dV_k = V_c(q_k) - V_c(q*)   (V linear in c: V_c(q) = c . J(q));
   V4_k = c . J4(q_k) / |q_k|^4  (degree-4 part along the ray q_k/|q_k|; positivity = the deep ray is lifted at large field).
usage: python -B deep_rays.py <tag> <solution stem> [<solution stem> ...]
"""
import sys, glob, json, os
import numpy as np
import k3_common as K

tag = sys.argv[1]; stems = sys.argv[2:]
TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8"))["degrees"]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); ids = [str(x) for x in Z["ids"]]; VAL0 = Z["values"]
deg4 = np.array([TR[p.split("::")[1]] == 4 for p in ids])
banks = sorted(glob.glob(str(K.BANKDIR / "descend_*_bank.npz")))
if (K.SCRATCH / "skeptic_endpoints_bank.npz").exists():
    banks.append(str(K.SCRATCH / "skeptic_endpoints_bank.npz"))
Qs, Js, src, isend = [], [], [], []
for b in banks:
    z = np.load(b); bid = [str(x) for x in z["ids"]]
    if "J" not in z.files or set(bid) != set(ids):
        print("skip (ids/J mismatch):", os.path.basename(b)); continue
    perm = [bid.index(p) for p in ids]
    n = z["Q"].shape[0]
    for i in range(n):
        Qs.append(z["Q"][i]); Js.append(np.asarray(z["J"][i])[perm]); src.append(os.path.basename(b)); isend.append(i == n - 1 or "skeptic" in b)
Qs = np.array(Qs); Js = np.array(Js); isend = np.array(isend)
nq = np.linalg.norm(Qs, axis=1)
out = {"tag": tag, "n_points": int(len(Qs)), "n_endpoints": int(isend.sum()), "banks": len(banks), "solutions": {}}
for st in stems:
    c = np.load(K.SCRATCH / f"{st}.npz")["c"]
    Vs = float(VAL0 @ c); dV = Js @ c - Vs; V4 = (Js * deg4[None, :]) @ c / nq ** 4
    j = int(np.argmin(dV)); j4 = int(np.argmin(V4))
    res = {"V_star": Vs, "min_dV_all": float(dV.min()), "argmin_src": src[j], "n_lower_all": int(np.sum(dV < 0)),
           "min_dV_endpoints": float(dV[isend].min()), "n_lower_endpoints": int(np.sum(dV[isend] < 0)),
           "min_V4_rays": float(V4.min()), "argmin_V4_src": src[j4], "n_negative_V4_rays": int(np.sum(V4 < 0)),
           "frac_endpoints_lifted": float(np.mean(dV[isend] > 0))}
    out["solutions"][st] = res
    print(st, json.dumps(res))
json.dump(out, open(K.SCRATCH / f"deep_rays_{tag}_{'_'.join(stems)}.json", "w"), indent=1)
