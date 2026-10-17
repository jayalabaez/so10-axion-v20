"""Per-parameter third/fourth derivatives along the neutral pure-H10 doublet directions at the Am45 point.
V is quartic, so with rows at q0 +- eta u:  dH_i = (H_i+ - H_i-)/(2 eta) exactly,  d2H_i = (H_i+ + H_i- - 2 H_i0)/eta^2 exactly.
  b_i = dH_i u   (486-vector per parameter: d^3 D_i/du du dphi),   V4_i = u^T d2H_i u  (d^4 D_i/du^4).
Directions: kernel of Q_em on the H10 slice (neutral components), split by i*T3R eigenvalue (+1/2 / -1/2) -> u_up, u_dn
(real unit chart vectors; one phase representative each).  Saves cubic_rows.npz.
"""
from __future__ import annotations
import time, json, numpy as np
import k3_common as K
chart = K.chart
Z = np.load(K.SCRATCH / "Am45_rows.npz"); q0 = Z["q"]; ids = [str(x) for x in Z["ids"]]; H0 = Z["hess"]
Qem = K.candidate.chart_generator(K.hypercharge.Q_EM_STANDARD_INTEGER) / 3.0
T3R = 0.5 * K.candidate.chart_generator(K.hypercharge.T3R_INTEGER)
T3L = None
sl = chart.H_SLICE; idx = np.arange(sl.start, sl.stop)
Qh = Qem[np.ix_(idx, idx)]; u_, s_, vt = np.linalg.svd(Qh); ker = vt[s_ < 1e-10].T   # 20 x 4
print("neutral H10 real dimension:", ker.shape[1])
op = ker.T @ (1j * T3R[np.ix_(idx, idx)]) @ ker; op = 0.5 * (op + op.conj().T); w, v = np.linalg.eigh(op)
print("i*T3R eigenvalues on neutral H10:", np.round(w, 4))
dirs = {}
for name, target in (("dn", -0.5), ("up", +0.5)):
    cols = [j for j in range(len(w)) if abs(w[j] - target) < 1e-6]
    vec = ker @ v[:, cols[0]]            # complex 20-vector; take a real representative (phase choice)
    re = np.real(vec); 
    if np.linalg.norm(re) < 1e-6: re = np.imag(vec)
    u = np.zeros(chart.TOTAL_DIM); u[idx] = re / np.linalg.norm(re); dirs[name] = u
    print(name, "T3R =", target, "|u|=", np.linalg.norm(u), "Q check", float(np.linalg.norm(Qem @ u)), "T3R check", float(u @ (T3R @ T3R) @ u))
eta = 0.1; out = {}; t0 = time.time()
for name, u in dirs.items():
    rows_p = K.parameter_rows(chart.unpack(q0 + eta * u)); rows_m = K.parameter_rows(chart.unpack(q0 - eta * u))
    Hp = np.array([np.asarray(rows_p[i].hessian, float) for i in ids]); Hm = np.array([np.asarray(rows_m[i].hessian, float) for i in ids])
    Hp = 0.5 * (Hp + np.transpose(Hp, (0, 2, 1))); Hm = 0.5 * (Hm + np.transpose(Hm, (0, 2, 1)))
    dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
    b = np.einsum("pij,j->pi", dH, u); V4 = np.einsum("i,pij,j->p", u, d2H, u)
    vp = np.array([rows_p[i].value for i in ids]); vm = np.array([rows_m[i].value for i in ids])
    out[f"b_{name}"] = b; out[f"V4_{name}"] = V4; out[f"u_{name}"] = u; out[f"vp_{name}"] = vp; out[f"vm_{name}"] = vm
    # odd part check: values are even in eta for a stationary point with u orthogonal to the gradient?  (not nec.)  store only
    print(f"{name}: done {time.time()-t0:.0f}s; max|b| per param {np.max(np.abs(b)):.3e}; V4 range [{V4.min():.3f},{V4.max():.3f}]", flush=True)
np.savez_compressed(K.SCRATCH / "cubic_rows.npz", ids=np.array(ids), eta=eta, values0=Z["values"], **out)
json.dump({"ids": ids, "eta": eta, **{f"V4_{n}": out[f"V4_{n}"].tolist() for n in dirs}, **{f"max_abs_b_{n}": np.max(np.abs(out[f"b_{n}"]), axis=1).tolist() for n in dirs}},
          open(K.SCRATCH / "cubic_rows.json", "w"), indent=1)
print("saved cubic_rows.npz")
