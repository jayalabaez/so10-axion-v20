#!/usr/bin/env python3
"""SKEPTIC D3 check 3 (NUM, own descent loop): fresh descents of V_c at the designer's final design point L6
(coupling vector of L6_S2_U8362e_R.npz) in the full 486-real chart.

Step: regularised Newton (shift sigma = max(0, -lambda_min) + 1e-6, trust radius Delta) using the repo's exact
parameter_rows (value, gradient, Hessian); EVERY accepted point is re-valued on the independent J path
(evaluate_directions + coefficient_jacobian) and acceptance uses the J-path value.
Starts (own choices, not the designer's seeds):
  cont      : continue from the designer's non-converged DC_hs31 endpoint (-0.025 after one step)
  ray:<seed>: random direction with block norms |Phi| 0.8, |H10| 2.5, |Sigma| 3.6, |S| 1.5, Phi17 at its vev norm
  hdir:<amp>: q* + amp * u_doublet  (pure light-doublet direction, then free relaxation)
usage: python -B sk_descend.py <start> <tag> [max_rows]
"""
import sys, json, time
import numpy as np
import sk_loader as LD
sys.path.insert(0, LD.REPO)
import g3_candidate_physical_target_audit_v20 as target  # noqa: E402

start, tag = sys.argv[1], sys.argv[2]
max_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 8
sol = np.load(LD.VAC / "L6_S2_U8362e_R.npz"); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
Z = np.load(LD.VAC / "S2_rows.npz"); qstar = Z["q"]
Vstar = float(c @ LD.J_at(qstar, ids))
chart = LD.chart
if start == "cont":
    q = np.load(LD.VAC / "descend_DC_hs31.npz")["qmin"]
elif start.startswith("ray:"):
    rng = np.random.default_rng(int(start.split(":")[1]))
    norms = {"Phi210": 0.8, "H10": 2.5, "Sigma126bar": 3.6, "S": 1.5, "Phi17": float(np.linalg.norm(qstar[chart.X_SLICE]))}
    q = np.zeros(chart.TOTAL_DIM)
    for name, sl in LD.BLOCKS.items():
        v = rng.normal(size=sl.stop - sl.start); q[sl] = v / np.linalg.norm(v) * norms[name]
    q = chart.pack(chart.unpack(q).validated())
elif start.startswith("hdir:"):
    amp = float(start.split(":")[1])
    M = np.einsum("p,pij->ij", c, Z["hess"]); M = 0.5 * (M + M.T); w, U = np.linalg.eigh(M)
    li = np.where((w > 1e-9) & (w < 3e-5))[0]; k = li[np.argmin(w[li])]
    q = qstar + amp * U[:, k]
else:
    raise SystemExit("start?")
log = open(LD.HERE / f"sk_descend_{tag}.log", "w", encoding="utf-8")


def say(m):
    print(m, flush=True); log.write(m + "\n"); log.flush()


def rows_at(q):
    r = target.parameter_rows(chart.unpack(q).validated())
    g = sum(c[i] * np.asarray(r[p].gradient, float) for i, p in enumerate(ids))
    H = sum(c[i] * np.asarray(r[p].hessian, float) for i, p in enumerate(ids)); H = 0.5 * (H + H.T)
    Vr = float(c @ np.array([r[p].value for p in ids]))
    return Vr, g, H


say(f"[{tag}] start {start}; V*(J path) = {Vstar:.9f}; blocks {LD.block_norms(q)}")
t0 = time.time(); Delta = 1.0; hist = []
V, g, H = rows_at(q); VJ = float(c @ LD.J_at(q, ids)); n = 1
best = (VJ, q.copy())
while True:
    w, U = np.linalg.eigh(H); gn = float(np.linalg.norm(g))
    hist.append({"rows": n, "V-V*(J)": VJ - Vstar, "V-V*(rows)": V - Vstar, "grad": gn, "n_neg": int(np.sum(w < -1e-9)),
                 "min_eig": float(w[0]), "blocks": LD.block_norms(q)})
    say(f"rows {n}: V-V* = {VJ - Vstar:+.6e} (rows {V - Vstar:+.6e}) |g| = {gn:.3e} neg = {hist[-1]['n_neg']} "
        f"blocks {[round(x, 3) for x in hist[-1]['blocks'].values()]} Delta {Delta:.3g} [{time.time() - t0:.0f}s]")
    if gn < 1e-7 or n >= max_rows:
        break
    gU = U.T @ g; sig = max(0.0, -w[0]) + 1e-6
    step = lambda s: -(U @ (gU / (w + s)))
    d = step(sig)
    if np.linalg.norm(d) > Delta:
        lo, hi = sig, sig + 1e5
        for _ in range(120):
            mid = 0.5 * (lo + hi)
            if np.linalg.norm(step(mid)) > Delta:
                lo = mid
            else:
                hi = mid
        d = step(hi)
    qt = chart.pack(chart.unpack(q + d).validated())
    Vt, gt, Ht = rows_at(qt); VJt = float(c @ LD.J_at(qt, ids)); n += 1
    if VJt < VJ:
        say(f"   accept |d| = {np.linalg.norm(d):.3e} dV = {VJt - VJ:+.4e} (rows-J mismatch {Vt - VJt:+.2e})")
        q, V, g, H, VJ = qt, Vt, gt, Ht, VJt
        if VJ < best[0]:
            best = (VJ, q.copy())
        Delta = min(8.0, 2 * Delta)
    else:
        Delta *= 0.3; say(f"   reject |d| = {np.linalg.norm(d):.3e} dV = {VJt - VJ:+.4e}; Delta -> {Delta:.3g}")
        if Delta < 1e-6:
            break
res = {"tag": tag, "start": start, "V*": Vstar, "best_V-V*(J)": best[0] - Vstar, "lower_than_V*": bool(best[0] < Vstar - 1e-9 * abs(Vstar)),
       "best_blocks": LD.block_norms(best[1]), "history": hist, "seconds": time.time() - t0}
say(json.dumps({k: v for k, v in res.items() if k != "history"}, default=float))
json.dump(res, open(LD.HERE / f"sk_descend_{tag}.json", "w"), indent=1, default=float)
np.savez_compressed(LD.HERE / f"sk_descend_{tag}.npz", qbest=best[1])
