"""SKEPTIC (R2-A): own full-486-chart descent of V_c at a coupling point (global-minimum screening, NUMERICAL).

Damped Newton / trust region on V_c(q) = sum_i c_i O_i(q) with exact (value, gradient, Hessian) rows from the repo's
parameter_rows (read-only).  All output goes to this skeptic folder.
usage: python -B sk_descend.py <solution npz (skeptic-relative or parent-relative)> <tag> <start> <out> [max_rows] [stop_below]
  start: random:<seed>:<scale> | hsray:<seed>:<scale> | bank:<npz>:<index> | qmin:<descent npz>
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import k3_common as K  # noqa: E402

solf, tag, start, out = sys.argv[1:5]
max_rows = int(sys.argv[5]) if len(sys.argv) > 5 else 8
stop_below = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5
sp = HERE / solf if (HERE / solf).exists() else PARENT / solf
sol = np.load(sp); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
chart = K.chart
Z = np.load(PARENT / f"{tag}_rows.npz"); q0 = Z["q"]; Vstar = float(c @ Z["values"])
log = open(HERE / f"{out}.log", "w", encoding="utf-8")


def say(m):
    print(m, flush=True); log.write(m + "\n"); log.flush()


def rows_at(q):
    rows = K.parameter_rows(chart.unpack(q))
    J = np.array([rows[p].value for p in ids])
    g = sum(c[i] * np.asarray(rows[p].gradient, float) for i, p in enumerate(ids))
    H = sum(c[i] * np.asarray(rows[p].hessian, float) for i, p in enumerate(ids)); H = 0.5 * (H + H.T)
    return float(c @ J), g, H, J


if start.startswith(("random", "hsray")):
    kind, seed, scale = start.split(":"); rng = np.random.default_rng(int(seed)); scale = float(scale)
    norms = {"Phi210": 1.0, "H10": 0.6, "Sigma126bar": 0.6, "S": 1.0, "Phi17": float(np.linalg.norm(q0[chart.X_SLICE]))}
    if kind == "hsray": norms = {"Phi210": 0.625, "H10": 1.82, "Sigma126bar": 4.06, "S": 0.37, "Phi17": float(np.linalg.norm(q0[chart.X_SLICE]))}
    q = np.zeros(chart.TOTAL_DIM)
    for name, sl in K.BLOCKS.items():
        v = rng.normal(size=sl.stop - sl.start); q[sl] = v / np.linalg.norm(v) * norms[name] * scale
    q = chart.pack(chart.unpack(q).validated())
elif start.startswith("bank:"):
    _, f, i = start.split(":"); q = np.load(PARENT / f)["Q"][int(i)]
elif start.startswith("qmin:"):
    q = np.load(PARENT / start[5:])["qmin"]
else:
    raise SystemExit("start")
say(f"[{out}] sol {solf} tag {tag} start {start}; V* = {Vstar:.9f}")
t0 = time.time(); Delta = 1.0
V, g, H, J = rows_at(q); n = 1; best = (V, q.copy())
while True:
    w, U = np.linalg.eigh(H); gn = float(np.linalg.norm(g))
    say(f"rows {n}: V-V* = {V - Vstar:+.6e} |g| = {gn:.3e} eig_min = {w[0]:.3e} blocks {[round(float(np.linalg.norm(q[sl])), 3) for sl in K.BLOCKS.values()]} ({time.time()-t0:.0f}s)")
    if V - Vstar < -stop_below or n >= max_rows or gn < 1e-9: break
    gU = U.T @ g; sig = max(0.0, -w[0]) + 1e-6
    step = lambda s_: -(U @ (gU / (w + s_)))
    d = step(sig)
    if np.linalg.norm(d) > Delta:
        lo, hi = sig, sig + 1e4
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if np.linalg.norm(step(mid)) > Delta: lo = mid
            else: hi = mid
        d = step(hi)
    pred = float(g @ d + 0.5 * d @ H @ d)
    qt = chart.pack(chart.unpack(q + d).validated()); Vt, gt, Ht, Jt = rows_at(qt); n += 1
    if Vt < V:
        rho = (Vt - V) / pred if pred < 0 else 1.0
        q, V, g, H, J = qt, Vt, gt, Ht, Jt
        if rho > 0.5 and np.linalg.norm(d) > 0.9 * Delta: Delta = min(8.0, 2 * Delta)
        if V < best[0]: best = (V, q.copy())
    else:
        Delta *= 0.3
        if Delta < 1e-8: break
res = {"sol": solf, "tag": tag, "start": start, "V_star": Vstar, "V_best-V*": best[0] - Vstar, "lower": bool(best[0] < Vstar - 1e-9 * abs(Vstar)),
       "blocks_at_best": {nm: float(np.linalg.norm(best[1][sl])) for nm, sl in K.BLOCKS.items()}, "rows": n, "seconds": time.time() - t0}
say(json.dumps(res, default=float))
json.dump(res, open(HERE / f"{out}.json", "w"), indent=1, default=float); np.savez(HERE / f"{out}.npz", qmin=best[1])
