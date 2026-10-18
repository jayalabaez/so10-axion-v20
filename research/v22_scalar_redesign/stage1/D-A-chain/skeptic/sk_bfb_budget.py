"""SKEPTIC: per-operator budget of the negative quartic a4 along the unbounded L6 direction (Phi+H10+Sigma+S part of my
H05 endpoint, and the full endpoint).  Operators are homogeneous, degree from J(2d)/J(d)."""
import json
import numpy as np
import sk_loader as LD
sol = np.load(LD.VAC / "L6_S2_U8362e_R.npz"); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
q = np.load(LD.HERE / "sk_descend_H05.npz")["qbest"]
out = {}
for tag, keep in (("Phi+H+Sigma+S", ["Phi210", "H10", "Sigma126bar", "S"]), ("full", list(LD.BLOCKS))):
    qq = np.zeros_like(q)
    for n in keep: qq[LD.BLOCKS[n]] = q[LD.BLOCKS[n]]
    d = qq / np.linalg.norm(qq)
    J1 = LD.J_at(d, ids); J2 = LD.J_at(2 * d, ids)
    deg = np.where(np.abs(J1) > 1e-14, np.round(np.log2(np.abs(J2) / np.maximum(np.abs(J1), 1e-300))), -1)
    contrib = {ids[i]: float(c[i] * J1[i]) for i in range(len(ids)) if deg[i] == 4}
    a4 = sum(contrib.values())
    top = sorted(contrib.items(), key=lambda kv: kv[1])[:8]
    out[tag] = {"a4": a4, "most_negative": top, "c_of_top": {k: float(c[ids.index(k)]) for k, _ in top}}
    print(tag, "a4 =", round(a4, 6)); [print("   %-48s %+.5f (c = %+.4f)" % (k, v, c[ids.index(k)])) for k, v in top]
json.dump(out, open(LD.HERE / "sk_bfb_budget.json", "w"), indent=1)
