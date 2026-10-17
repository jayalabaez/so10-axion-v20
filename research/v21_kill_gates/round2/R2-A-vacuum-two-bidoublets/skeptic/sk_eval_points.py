"""SKEPTIC (R2-A): independent re-evaluation of the decisive 'lower point' numbers.

For each (coupling solution, tag, descent endpoint) we
  1. rebuild q* from the tag's point meta with the REPO chart (not from the stored rows npz) and compare,
  2. re-evaluate the 51 operator values J at q* and at the descent minimum via potential.evaluate_directions +
     coefficient_jacobian (the J_at_state path; NOT the parameter_rows/adapters path that produced the banks),
  3. compute V_c(q_min) - V_c(q*) with the solution's coupling vector c,
  4. check gauge invariance of the evaluator at q_min: central finite differences of V_c along every symmetry tangent
     T_a q_min (should vanish to O(eps^2)), and along random directions as a scale reference,
  5. report the field content of q_min: doublet (1,2)_{1/2} components of H10 / Sigma, colour-triplet components.
usage: python -B sk_eval_points.py
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))   # read-only import of the researcher's k3_common (repo loader); nothing is written there
import k3_common as K  # noqa: E402

chart = K.chart; potential = K.potential


def J_at(q, ids):
    st = chart.unpack(np.asarray(q, float)).validated()
    dirs = potential.evaluate_directions(st); jac = potential.coefficient_jacobian(dirs)
    return np.array([float(np.real(jac[pid])) for pid in ids])


def V_at(q, c, ids):
    return float(c @ J_at(q, ids))


CASES = [
    # (label, solution npz, tag, descent json (for start/meta), which bank to take qmin from)
    ("R1_bankA", "G7_D470_C1622_K2.npz", "D470", "descend_R1_bankA"),
    ("R1_hs2", "G7_D470_C1622_K2.npz", "D470", "descend_R1_hs2"),
    ("R3_rnd41", "G14_Am45_C2_K2f09_R12.npz", "Am45", "descend_R3_rnd41"),
    ("X3_first", "G15_Am45x_C1622_K2_X12.npz", "Am45x", None),
    ("N1_rnd61", "G13_Am45_C2noew_R12.npz", "Am45", "descend_N1_rnd61"),
]

out = {}
t0 = time.time()
for label, solf, tag, dname in CASES:
    sol = np.load(PARENT / solf); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
    Z = np.load(PARENT / f"{tag}_rows.npz"); qstar_stored = Z["q"]; vals_stored = Z["values"]
    meta = json.load(open(PARENT / f"{tag}_rows_meta.json"))["point"]
    st = K.g3221_state(meta["p"], meta["a"], meta["omega"], meta["r"], meta["s"], meta["x"])
    qstar = chart.pack(st)
    if dname is None:
        # first X3 descent json found
        import glob
        cands = sorted(glob.glob(str(PARENT / "descend_X3_*.json")))
        dname = Path(cands[0]).stem
    dj = json.load(open(PARENT / f"{dname}.json"))
    assert dj["sol"] == solf, (dj["sol"], solf)
    dn = np.load(PARENT / f"{dname}.npz"); qmin = dn["qmin"]
    Jstar = J_at(qstar, ids); Jmin = J_at(qmin, ids)
    Vstar = float(c @ Jstar); Vmin = float(c @ Jmin)
    # stationarity at q* from stored grads (rows) -- and an independent finite-difference gradient along random dirs
    rng = np.random.default_rng(7)
    fd_grad = []
    for _ in range(3):
        d = rng.normal(size=qstar.size); d /= np.linalg.norm(d); h = 1e-4
        fd_grad.append((V_at(qstar + h * d, c, ids) - V_at(qstar - h * d, c, ids)) / (2 * h))
    # gauge invariance at qmin: tangents
    full, ranks = K.symmetry_tangents(chart.unpack(qmin).validated())
    T = np.asarray(full, float)
    if T.shape[0] != qmin.size: T = T.T
    inv = []
    h = 1e-4
    for a in range(min(T.shape[1], 46)):
        v = T[:, a]; nv = np.linalg.norm(v)
        if nv < 1e-12: continue
        v = v / nv
        inv.append(abs(V_at(qmin + h * v, c, ids) - V_at(qmin - h * v, c, ids)) / (2 * h))
    ref = []
    for _ in range(3):
        d = rng.normal(size=qmin.size); d /= np.linalg.norm(d)
        ref.append(abs(V_at(qmin + h * d, c, ids) - V_at(qmin - h * d, c, ids)) / (2 * h))
    blocks = {name: float(np.linalg.norm(qmin[sl])) for name, sl in K.BLOCKS.items()}
    rec = {"solution": solf, "tag": tag, "descent": dname, "start": dj["start"],
           "qstar_rebuilt_vs_stored_maxdiff": float(np.max(np.abs(qstar - qstar_stored))),
           "Jstar_vs_stored_rows_maxdiff": float(np.max(np.abs(Jstar - vals_stored))),
           "V_star_indep": Vstar, "V_star_reported": dj["V_star"],
           "V_min_indep": Vmin, "Vmin_minus_Vstar_indep": Vmin - Vstar, "Vmin_minus_Vstar_reported": dj["V_min_seen-V*"],
           "fd_directional_grad_at_qstar": fd_grad,
           "gauge_inv_max_|dV/ds|_along_tangents_at_qmin": float(max(inv)) if inv else None, "n_tangents": len(inv),
           "random_dir_|dV/ds|_at_qmin_reference": ref, "qmin_block_norms": blocks,
           "seconds": time.time() - t0}
    out[label] = rec
    print(label, json.dumps({k: v for k, v in rec.items() if k not in ()}, default=float), flush=True)
    json.dump(out, open(HERE / "sk_eval_points.json", "w"), indent=1, default=float)
print("done", time.time() - t0)
