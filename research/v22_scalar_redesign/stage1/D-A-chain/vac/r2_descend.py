"""R2-A full-486-chart descent of V_c (global-minimum screening, NUMERICAL) - K3's k3_descend.py generalised.

Trust-region Newton with one exact rows call (value, gradient, Hessian of all 51 parameter rows) per trial point:
the trial q + d (d = TR-Newton step, |d| <= Delta) is evaluated with rows; accepted if V decreases (its rows are then
reused for the next step), otherwise Delta shrinks.  Along the segment the restriction of V is an exact quartic,
fixed by (V, g.d, d.H.d) at both ends; it is used to report the exact line minimum.  Every evaluated point is banked
with its 51 per-parameter values J (feedback: competitor points / BFB rays for r2_lp5 --extra_comp).
usage: python -B r2_descend.py <tag> <solution npz> <start> <out tag> [max_rows] [stop_below]
 start: random:<seed>:<scale> | hsray:<seed>:<scale> | npz:<file>[:<index>] | zstar
 stop_below: stop once V - V* < -stop_below (a deeper point is established), default: never
"""
from __future__ import annotations
import sys, json, time, numpy as np
import k3_common as K

tag, solpath, start, otag = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
max_rows = int(sys.argv[5]) if len(sys.argv) > 5 else 8
stop_below = float(sys.argv[6]) if len(sys.argv) > 6 else None
sol = np.load(K.SCRATCH / solpath); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
chart = K.chart
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); qstar = Z["q"]; assert [str(x) for x in Z["ids"]] == ids
Vstar = float(c @ Z["values"])
BANK_Q, BANK_J = [], []
TR = None
try:
    import json as _j
    TR = _j.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8"))["degrees"]
except Exception:
    pass
deg4 = np.array([TR[p.split("::")[1]] == 4 for p in ids]) if TR else None


def save_bank():
    np.savez_compressed(K.SCRATCH / f"descend_{otag}_bank.npz", Q=np.array(BANK_Q), J=np.array(BANK_J), ids=np.array(ids))


def rows_at(q):
    rows = K.parameter_rows(chart.unpack(q))
    J = np.array([rows[pid].value for pid in ids]); BANK_Q.append(np.array(q)); BANK_J.append(J); save_bank()
    g = sum(c[i] * np.asarray(rows[pid].gradient, float) for i, pid in enumerate(ids))
    H = sum(c[i] * np.asarray(rows[pid].hessian, float) for i, pid in enumerate(ids)); H = 0.5 * (H + H.T)
    return float(c @ J), g, H, J


if start.startswith("random") or start.startswith("hsray"):
    kind, seed, scale = start.split(":"); rng = np.random.default_rng(int(seed)); scale = float(scale)
    norms = {"Phi210": 1.0, "H10": 0.6, "Sigma126bar": 0.6, "S": 1.0, "Phi17": float(np.linalg.norm(qstar[chart.X_SLICE]))}
    if kind == "hsray":   # K3's deep H-Sigma region: |Phi| 0.625, |H| 1.82, |Sigma| 4.06, |S| 0.37, |Phi17| 5.64
        norms = {"Phi210": 0.625, "H10": 1.82, "Sigma126bar": 4.06, "S": 0.37, "Phi17": 5.64}
    q = np.zeros(chart.TOTAL_DIM)
    for name, sl in K.BLOCKS.items():
        n = sl.stop - sl.start; v = rng.normal(size=n); v /= np.linalg.norm(v); q[sl] = v * norms[name] * scale
    q = chart.pack(chart.unpack(q).validated())
elif start.startswith("npz:"):
    parts = start[4:].split(":"); arr = np.load(K.find(parts[0]))
    q = arr["Q"][int(parts[1])] if len(parts) > 1 else arr["q"]
elif start == "zstar":
    q = qstar.copy()
else:
    raise SystemExit("start")

log = open(K.SCRATCH / f"descend_{otag}.log", "w", encoding="utf-8")
def say(m): print(m, flush=True); log.write(m + "\n"); log.flush()
say(f"[{otag}] tag {tag} sol {solpath} start {start}: |q| blocks {[round(float(np.linalg.norm(q[sl])), 4) for sl in K.BLOCKS.values()]}; V* = {Vstar:.9f}")
t0 = time.time(); Delta = 1.0; hist = []
V, g, H, J = rows_at(q); n_rows = 1
while True:
    gn = float(np.linalg.norm(g)); w, U = np.linalg.eigh(H)
    v4 = float(c[deg4] @ J[deg4]) / float(np.linalg.norm(q)) ** 4 if deg4 is not None else None
    hist.append({"rows": n_rows, "V": V, "V-V*": V - Vstar, "grad": gn, "min_eig": float(w[0]), "n_neg": int(np.sum(w < -1e-9)),
                 "block_norms": [float(np.linalg.norm(q[sl])) for sl in K.BLOCKS.values()], "V4/|q|^4": v4})
    say(f"rows {n_rows:2d}: V-V* = {V - Vstar:+.6e}  |g| = {gn:.3e}  eig[min] = {w[0]:.3e}  neg = {hist[-1]['n_neg']}  blocks {np.round(hist[-1]['block_norms'], 3).tolist()}  V4/|q|^4 = {v4:.4g}  Delta {Delta:.3g} ({time.time()-t0:.0f}s)")
    if gn < 1e-8 or n_rows >= max_rows: break
    if stop_below is not None and V - Vstar < -stop_below: say("   deeper point established; stop"); break
    gU = U.T @ g; sigma = max(0.0, -w[0]) + 1e-6
    step_of = lambda sig: -(U @ (gU / (w + sig)))
    d = step_of(sigma)
    if np.linalg.norm(d) > Delta:
        lo, hi = sigma, sigma + 1e4
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if np.linalg.norm(step_of(mid)) > Delta: lo = mid
            else: hi = mid
        d = step_of(hi)
    pred = float(g @ d + 0.5 * d @ H @ d)
    qt = chart.pack(chart.unpack(q + d).validated())
    Vt, gt, Ht, Jt = rows_at(qt); n_rows += 1
    # exact quartic along the segment from (V, g.d, dHd) at 0 and (Vt, gt.d, d Ht d) at 1 (least squares, 6 data / 5 coefficients)
    A = np.array([[0, 0, 0, 0, 1], [0, 0, 0, 1, 0], [0, 0, 2, 0, 0], [1, 1, 1, 1, 1], [4, 3, 2, 1, 0], [12, 6, 2, 0, 0]], float)
    rhs = np.array([V, g @ d, d @ H @ d, Vt, gt @ d, d @ Ht @ d]); coef = np.linalg.lstsq(A, rhs, rcond=None)[0]
    crit = [float(r.real) for r in np.roots(np.polyder(coef)) if abs(r.imag) < 1e-9]
    line_min = min([np.polyval(coef, a) for a in crit + [0.0, 1.0]])
    if Vt < V:
        rho = (Vt - V) / pred if pred < 0 else 1.0
        say(f"   accept |d| = {np.linalg.norm(d):.3e}  dV = {Vt - V:+.4e} (pred {pred:+.4e}, rho {rho:.2f}); exact line min V-V* = {line_min - Vstar:+.4e}")
        q, V, g, H, J = qt, Vt, gt, Ht, Jt
        if rho > 0.5 and np.linalg.norm(d) > 0.9 * Delta: Delta = min(8.0, 2 * Delta)
    else:
        Delta *= 0.3; say(f"   reject |d| = {np.linalg.norm(d):.3e}  dV = {Vt - V:+.4e} (pred {pred:+.4e}); Delta -> {Delta:.3e}")
        if Delta < 1e-8: break
Js = np.array(BANK_J); Vs = Js @ c; jmin = int(np.argmin(Vs)); qmin = BANK_Q[jmin]
final = {"tag": tag, "sol": solpath, "start": start, "V_star": Vstar, "history": hist, "V_last-V*": hist[-1]["V-V*"],
         "V_min_seen-V*": float(Vs[jmin] - Vstar), "lower_than_star": bool(Vs[jmin] < Vstar - 1e-9 * max(1, abs(Vstar))),
         "min_point_block_norms": {name: float(np.linalg.norm(qmin[sl])) for name, sl in K.BLOCKS.items()},
         "min_point_V4/|q|^4": float(c[deg4] @ Js[jmin][deg4]) / float(np.linalg.norm(qmin)) ** 4 if deg4 is not None else None,
         "converged_local_min": bool(hist[-1]["grad"] < 1e-6 and hist[-1]["n_neg"] == 0), "seconds": time.time() - t0, "n_rows": n_rows}
say(json.dumps({k: v for k, v in final.items() if k != "history"}, default=float))
json.dump(final, open(K.SCRATCH / f"descend_{otag}.json", "w"), indent=1, default=float); np.savez(K.SCRATCH / f"descend_{otag}.npz", q=q, qmin=qmin)
