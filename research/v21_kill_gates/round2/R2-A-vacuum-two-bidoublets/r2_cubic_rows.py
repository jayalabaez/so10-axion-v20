"""R2-A: per-parameter third/fourth derivatives along a chosen neutral EW (Higgs) direction u at a tag's G3221 point.

u = q_vev(a) for slice coordinates a inside the H10 + Sigma(15,2,2) bidoublet span chosen to realise a target fit
composition (|r|, s) [default K2/Ohlsson-Pernow basin |r| = 66, s = 0.43].  V is quartic, so rows at q0 +- eta u give
dH_i, d2H_i exactly:  b_i = dH_i u, V4_i = u.d2H_i.u.  Saves cubic_<tag>_<label>.npz with b_up, V4_up, u_up (+ the a used).
usage: python -B r2_cubic_rows.py <tag> <label> [r_target] [s_re,s_im]
"""
from __future__ import annotations
import sys, time, math, json
import numpy as np
from scipy.optimize import minimize
import k3_common as K
import r2_compose as RC

tag, label = sys.argv[1], sys.argv[2]
tr = float(sys.argv[3]) if len(sys.argv) > 3 else 66.0
ts = complex(*[float(x) for x in (sys.argv[4] if len(sys.argv) > 4 else "0.43,0.0").split(",")])
nt = RC.Neutral(tag)
cols = [j for j, m in enumerate(nt.meta) if m["block"] in ("H10", "Sigma126bar")]
L = np.eye(5, dtype=complex)[:, cols]
rng = np.random.default_rng(11)


def loss(x):
    a = L @ (x[:4] + 1j * x[4:]); cm = nt.comp_of_a(a); r, s = cm["r"], cm["s"]
    if not (np.isfinite(abs(r)) and np.isfinite(s)): return 1e6
    # also keep the Sigma fraction away from 0 and 1 (perturbative Y126 / Y10): soft preference for ~0.5
    return (math.log(abs(r) / tr)) ** 2 + abs(s - ts) ** 2 + 1e-3 * (cm["frac"]["Sigma126bar"] - 0.5) ** 2


best = None
for k in range(40):
    res = minimize(loss, rng.normal(size=8), method="Nelder-Mead", options={"maxiter": 6000, "xatol": 1e-12, "fatol": 1e-16})
    if best is None or res.fun < best.fun: best = res
a = L @ (best.x[:4] + 1j * best.x[4:]); a = a / np.linalg.norm(a)
cm = nt.comp_of_a(a); u = nt.q_of_a(a)
print(f"target |r| = {tr}, s = {ts}: achieved |r| = {abs(cm['r']):.6g}, s = {cm['s']:.6g}, frac {cm['frac']}")
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); q0 = Z["q"]; ids = [str(x) for x in Z["ids"]]; H0 = Z["hess"]
eta = 0.1; t0 = time.time()
rows_p = K.parameter_rows(K.chart.unpack(q0 + eta * u)); rows_m = K.parameter_rows(K.chart.unpack(q0 - eta * u))
Hp = np.array([np.asarray(rows_p[i].hessian, float) for i in ids]); Hm = np.array([np.asarray(rows_m[i].hessian, float) for i in ids])
Hp = 0.5 * (Hp + np.transpose(Hp, (0, 2, 1))); Hm = 0.5 * (Hm + np.transpose(Hm, (0, 2, 1)))
dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
b = np.einsum("pij,j->pi", dH, u); V4 = np.einsum("i,pij,j->p", u, d2H, u)
np.savez_compressed(K.SCRATCH / f"cubic_{tag}_{label}.npz", ids=np.array(ids), eta=eta, b_up=b, V4_up=V4, u_up=u, a=a,
                    r=abs(cm["r"]), s=np.array([cm["s"].real, cm["s"].imag]))
print(f"saved cubic_{tag}_{label}.npz in {time.time()-t0:.0f}s; max|b| {np.max(np.abs(b)):.3e}; V4 range [{V4.min():.3f}, {V4.max():.3f}]")
