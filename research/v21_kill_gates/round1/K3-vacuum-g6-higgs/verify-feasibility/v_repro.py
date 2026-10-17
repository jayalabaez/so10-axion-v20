"""Verifier reproduction for gate K3 (feasibility/standards lens).

Part 1 (stored rows): for P831 and P831b recompute V*, |grad|, full-Hessian inertia, Goldstone kernel vs symmetry
        tangents, box maxima and the singlet-channel a0 from the researcher's Am45_rows.npz (independent code).
Part 2 (fresh compiler): rebuild the Am45 G3221 state with the repo (read-only), recompute the 51 parameter rows and
        compare value/gradient/Hessian with the stored rows.
Part 3 (deep point): re-evaluate V with the compiler's value-only evaluator at the lowest descent-bank point for
        P831b (and P831), and fit the exact ray polynomial V(t q) = A2 t^2 + A3 t^3 + A4 t^4.
"""
from __future__ import annotations
import sys, json, math, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent  # researcher folder
sys.path.insert(0, str(HERE))
import k3_common as K  # noqa: E402  (copied; imports the repo read-only)

out = {}
t0 = time.time()
Z = np.load(RES / "Am45_rows.npz")
ids = [str(x) for x in Z["ids"]]
VAL0, GR, HESS, q0, TAN = Z["values"], Z["grads"], Z["hess"], Z["q"], Z["tangents"]
meta = json.load(open(RES / "Am45_rows_meta.json"))["point"]
TR = json.load(open(RES / "unit_rows_traces.json", encoding="utf-8"))
DEG = TR["degrees"]
print("degrees table:", DEG, flush=True)
blocks = list(K.BLOCKS); nblk = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in blocks}


def a0_singlet(c):
    beta = np.zeros((5, 5))
    for jb, Bn in enumerate(blocks):
        tr = TR["blocks"][Bn]["traces"]
        for i, pid in enumerate(ids):
            if DEG[pid.split("::")[1]] != 4:
                continue
            for ia, An in enumerate(blocks):
                beta[ia, jb] += c[i] * tr[pid][An]
    M = np.zeros((5, 5))
    for ia, An in enumerate(blocks):
        for jb, Bn in enumerate(blocks):
            M[ia, jb] = beta[ia, jb] if ia == jb else math.sqrt(nblk[Bn] / nblk[An]) * beta[ia, jb]
    asym = float(np.max(np.abs(M - M.T)))
    return (np.linalg.eigvalsh(0.5 * (M + M.T)) / (16 * math.pi)).tolist(), asym


# symmetry tangents: orthonormal basis
u, sv, _ = np.linalg.svd(TAN, full_matrices=False)
rankT = int(np.sum(sv > 1e-9 * sv[0]))
T = u[:, :rankT]
out["tangent_rank"] = rankT
print("tangent rank (so10+X+PQ) =", rankT, flush=True)

for tag in ["P831", "P831b"]:
    sol = np.load(RES / f"{tag}.npz"); c = sol["c"]
    assert [str(x) for x in sol["ids"]] == ids
    V = float(c @ VAL0); g = c @ GR; H = np.einsum("p,pij->ij", c, HESS); H = 0.5 * (H + H.T)
    w, U = np.linalg.eigh(H)
    zero = np.abs(w) < 1e-9; neg = w < -1e-9; light = (w >= 1e-9) & (w < 3e-5); heavy = w >= 3e-5
    # kernel vs tangents: the kernel should be exactly the tangent space
    Uz = U[:, zero]
    proj_err = float(np.max(np.abs(Uz - T @ (T.T @ Uz)))) if Uz.size else None
    HT = float(np.max(np.abs(H @ T)))
    deg = np.array([DEG[p.split("::")[1]] for p in ids])
    a0, asym = a0_singlet(c)
    rec = {"V_star": V, "grad_max": float(np.max(np.abs(g))), "n_zero": int(zero.sum()), "n_neg": int(neg.sum()),
           "n_light": int(light.sum()), "n_heavy": int(heavy.sum()), "min_eig": float(w[0]),
           "min_heavy": float(w[heavy].min()), "light_levels": sorted(set(np.round(w[light], 10).tolist())),
           "kernel_in_tangent_space_maxdev": proj_err, "max_abs_H_times_tangents": HT,
           "box": {"quartic": float(np.max(np.abs(c[deg == 4]))), "cubic": float(np.max(np.abs(c[deg == 3]))), "mass": float(np.max(np.abs(c[deg == 2])))},
           "a0_singlet": a0, "a0_matrix_asymmetry": asym, "a0_max_abs": float(np.max(np.abs(a0)))}
    out[tag] = rec
    print(tag, json.dumps(rec), flush=True)

# ---------------- Part 2: fresh compiler rows at the Am45 point
state = K.g3221_state(meta["p"], meta["a"], meta["omega"], meta["r"], meta["s"], meta["x"])
q = K.chart.pack(state)
out["q_rebuild_maxdiff"] = float(np.max(np.abs(q - q0)))
print("rebuilt q max diff vs stored:", out["q_rebuild_maxdiff"], flush=True)
t1 = time.time()
rows = K.parameter_rows(state)
print(f"fresh rows in {time.time()-t1:.0f}s", flush=True)
rid = sorted(rows)
assert rid == ids, (rid[:3], ids[:3])
dv = max(abs(float(rows[i].value) - float(VAL0[k])) for k, i in enumerate(ids))
dg = max(float(np.max(np.abs(np.asarray(rows[i].gradient, float) - GR[k]))) for k, i in enumerate(ids))
dh = 0.0
for k, i in enumerate(ids):
    Hk = np.asarray(rows[i].hessian, float); Hk = 0.5 * (Hk + Hk.T)
    dh = max(dh, float(np.max(np.abs(Hk - HESS[k]))))
out["fresh_rows_vs_stored"] = {"max_dvalue": dv, "max_dgrad": dg, "max_dhess": dh}
print("fresh rows vs stored:", out["fresh_rows_vs_stored"], flush=True)
full, ranks = K.symmetry_tangents(state)
out["fresh_symmetry_ranks"] = ranks
print("fresh symmetry ranks:", ranks, flush=True)
del rows

# ---------------- Part 3: deep descent point re-evaluation
def J_from_values(vals, dids):
    dindex = {d: j for j, d in enumerate(dids)}; J = np.zeros((vals.shape[0], len(ids)))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = dindex[did]
        J[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return J


def value_at(qv, c):
    dirs = K.potential.evaluate_directions(K.chart.unpack(qv)); jac = K.potential.coefficient_jacobian(dirs)
    return float(sum(c[i] * jac[pid] for i, pid in enumerate(ids)))


for tag, bankname in [("P831b", "descend_P831b_r1s_bank.npz"), ("P831", "descend_P831_r1s_bank.npz")]:
    sol = np.load(RES / f"{tag}.npz"); c = sol["c"]
    bank = np.load(RES / bankname); Q = bank["Q"]; Jb = J_from_values(bank["values"], [str(x) for x in bank["ids"]])
    Vb = Jb @ c; k = int(np.argmin(Vb)); qlow = Q[k]
    Vstar = float(c @ VAL0)
    rec = {"bank_n": int(len(Vb)), "bank_min_V_stored": float(Vb[k]), "V_star": Vstar,
           "block_norms": {n: float(np.linalg.norm(qlow[s])) for n, s in K.BLOCKS.items()}, "norm_q": float(np.linalg.norm(qlow))}
    t2 = time.time()
    Vfresh = value_at(qlow, c)
    rec["V_fresh_at_qlow"] = Vfresh; rec["V_fresh_minus_Vstar"] = Vfresh - Vstar; rec["seconds_one_eval"] = time.time() - t2
    print(tag, "deep point:", json.dumps(rec), flush=True)
    if tag == "P831b":
        ts = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        vals = [Vfresh if abs(t - 1.0) < 1e-12 else value_at(t * qlow, c) for t in ts]
        A = np.array([[t ** 2, t ** 3, t ** 4] for t in ts]); coef, res, rk, svv = np.linalg.lstsq(A, np.array(vals), rcond=None)
        fitres = float(np.max(np.abs(A @ coef - np.array(vals))))
        A2, A3, A4 = (float(x) for x in coef)
        # ray minimum of A2 t^2 + A3 t^3 + A4 t^4 for t > 0
        tt = np.linspace(0.01, 10, 200000); Vt = A2 * tt ** 2 + A3 * tt ** 3 + A4 * tt ** 4; j = int(np.argmin(Vt))
        rec2 = {"t_values": ts, "V_values": vals, "A2": A2, "A3": A3, "A4": A4, "fit_residual": fitres,
                "A4_over_norm4": A4 / np.linalg.norm(qlow) ** 4, "ray_min_V": float(Vt[j]), "ray_min_t": float(tt[j]),
                "ray_min_minus_Vstar": float(Vt[j]) - Vstar}
        out[f"{tag}_ray"] = rec2
        print(tag, "ray polynomial:", json.dumps(rec2), flush=True)
    out[f"{tag}_deep"] = rec

out["seconds"] = time.time() - t0
json.dump(out, open(HERE / "v_repro.json", "w"), indent=1, default=float)
print("DONE", out["seconds"], flush=True)
