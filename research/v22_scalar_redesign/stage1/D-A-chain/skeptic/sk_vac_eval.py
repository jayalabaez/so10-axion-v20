"""SKEPTIC D3 check 1: independent re-evaluation of the designer's decisive 'lower point' numbers (NUM).

For each (coupling solution, descent endpoint):
  1. rebuild q* from the S2 point meta with the repo chart (own loader), compare with the stored S2_rows.npz q;
  2. evaluate the 51 operator values with evaluate_directions + coefficient_jacobian (independent of parameter_rows);
  3. V_c(q*) and V_c(q_min) with the solution's coupling vector c;
  4. stationarity at q*: central finite differences along random unit directions;
  5. gauge invariance of the evaluator at q_min: central differences along the SO(10)+U(1)_X+PQ tangents;
  6. 'is it the same vacuum?': block norms and the H10 / Sigma-doublet content at q_min.
usage: python -B sk_vac_eval.py
"""
from __future__ import annotations
import json, time
import numpy as np
import sk_loader as LD

t0 = time.time()
meta = json.load(open(LD.VAC / "S2_rows_meta.json"))["point"]
st = LD.build_state(meta["p"], meta["a"], meta["omega"], meta["r"], meta["s"], meta["x"])
q_re = LD.chart.pack(st)
Z = np.load(LD.VAC / "S2_rows.npz"); q_st = Z["q"]
out = {"q*_rebuild_maxdev": float(np.max(np.abs(q_re - q_st))), "q*_block_norms": LD.block_norms(q_st)}
print("q* rebuild max dev", out["q*_rebuild_maxdev"], flush=True)

CASES = [("L2/DA_hs11", "L2_S2_U8362_R.npz", "descend_DA_hs11"),
         ("L2/DA_R2hs2end", "L2_S2_U8362_R.npz", "descend_DA_R2hs2end"),
         ("L4/DB_hs21", "L4_S2_U8362_R2.npz", "descend_DB_hs21"),
         ("L6/DC_hs31", "L6_S2_U8362e_R.npz", "descend_DC_hs31"),
         ("L6/DC_rnd32", "L6_S2_U8362e_R.npz", "descend_DC_rnd32")]
rng = np.random.default_rng(20261017)
res = {}
done_sol = {}
for label, solf, dname in CASES:
    sol = np.load(LD.VAC / solf); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
    dj = json.load(open(LD.VAC / f"{dname}.json")); assert dj["sol"] == solf
    qmin = np.load(LD.VAC / f"{dname}.npz")["qmin"]
    if solf not in done_sol:
        Js = LD.J_at(q_re, ids); Vs = float(c @ Js)
        fd = []
        for _ in range(4):
            d = rng.normal(size=q_re.size); d /= np.linalg.norm(d); h = 1e-4
            fd.append(abs(float(c @ LD.J_at(q_re + h * d, ids)) - float(c @ LD.J_at(q_re - h * d, ids))) / (2 * h))
        done_sol[solf] = (Vs, fd)
    Vs, fd = done_sol[solf]
    Vm = float(c @ LD.J_at(qmin, ids))
    full, ranks = LD.candidate.symmetry_matrix(LD.chart.unpack(qmin).validated())
    T = np.asarray(full, float)
    if T.shape[0] != qmin.size:
        T = T.T
    tang = []
    for a in range(T.shape[1]):
        v = T[:, a]; nv = np.linalg.norm(v)
        if nv < 1e-12:
            continue
        v = v / nv; h = 1e-4
        tang.append(abs(float(c @ LD.J_at(qmin + h * v, ids)) - float(c @ LD.J_at(qmin - h * v, ids))) / (2 * h))
    d = rng.normal(size=qmin.size); d /= np.linalg.norm(d); h = 1e-4
    rnd = abs(float(c @ LD.J_at(qmin + h * d, ids)) - float(c @ LD.J_at(qmin - h * d, ids))) / (2 * h)
    res[label] = {"V*_indep": Vs, "V*_designer": dj["V_star"], "Vmin-V*_indep": Vm - Vs, "Vmin-V*_designer": dj["V_min_seen-V*"],
                  "fd_stationarity_at_q*": fd, "max_gauge_tangent_dV_at_qmin": max(tang), "n_tangents": len(tang),
                  "random_dir_dV_at_qmin": rnd, "qmin_block_norms": LD.block_norms(qmin), "qmin_ranks": ranks}
    print(label, json.dumps({k: v for k, v in res[label].items() if k not in ("qmin_ranks",)}, default=float), f"[{time.time()-t0:.0f}s]", flush=True)
out["cases"] = res
json.dump(out, open(LD.HERE / "sk_vac_eval.json", "w"), indent=1, default=float)
print("saved sk_vac_eval.json", f"{time.time()-t0:.0f}s")
