#!/usr/bin/env python3
"""SKEPTIC D3 check 2 (NUM, own matching code): tree-level lambda_eff of the light SM doublet at the designer's final
flavour-capable point L6_S2_U8362e_R.

* Full Hessian M = sum_p c_p hess_p at q* (stored S2_rows.npz, exact compiler rows).
* Light doublet direction u: any unit vector in the 4-dim real eigenspace with the tuned eigenvalue (~2.2e-7); for a
  single complex doublet every direction in that space is SU(2)_L x U(1)_Y-equivalent to the neutral real one (EXACT).
  The (1,2)_{1/2} identification is checked by the doublet's SM Casimirs (C2L = 3/4, Y^2 = 1/4, C3 = 0).
* V is a quartic polynomial, so with rows at q* +- eta u:  dH = (H+ - H-)/(2 eta) and d2H = (H+ + H- - 2 H0)/eta^2 are
  EXACT; b = dH u (the h h phi_k trilinears), V4 = u d2H u.
* lambda_eff = V4/6 - (1/2) sum_k (b.e_k)^2 / m_k^2 over heavy modes (m_k^2 >= 3e-5), light modes listed separately.
Also re-checks the local spectrum at q* (Goldstones / negative / light / heavy) independently of the LP log.
usage: python -B sk_lambda.py [eta]
"""
import sys, json, time
import numpy as np
import sk_loader as LD
sys.path.insert(0, LD.REPO)
import g3_candidate_physical_target_audit_v20 as target  # noqa: E402

eta = float(sys.argv[1]) if len(sys.argv) > 1 else 0.07
sol = np.load(LD.VAC / "L6_S2_U8362e_R.npz"); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
Z = np.load(LD.VAC / "S2_rows.npz"); q0 = Z["q"]; assert [str(x) for x in Z["ids"]] == ids
H0p = Z["hess"]
M = np.einsum("p,pij->ij", c, H0p); M = 0.5 * (M + M.T)
w, U = np.linalg.eigh(M)
out = {"spectrum": {"n_zero(|w|<1e-9)": int(np.sum(np.abs(w) < 1e-9)), "n_neg(<-1e-9)": int(np.sum(w < -1e-9)),
                    "n_light(1e-9..3e-5)": int(np.sum((w > 1e-9) & (w < 3e-5))), "n_heavy(>=3e-5)": int(np.sum(w >= 3e-5)),
                    "min_eig": float(w[0]), "min_heavy": float(w[w >= 3e-5][0])}}
grad = np.einsum("p,pi->i", c, Z["grads"])
out["grad_norm_at_q*"] = float(np.linalg.norm(grad))
# doublet eigenspace: eigenvalues within 1% of the smallest positive light eigenvalue cluster near 2.2e-7
light_idx = np.where((w > 1e-9) & (w < 3e-5))[0]
lw = w[light_idx]
cl = light_idx[np.abs(lw - lw.min()) < 1e-2 * lw.min()]
out["doublet_cluster"] = {"size": int(len(cl)), "eig": w[cl].tolist()}
C2L = Z["C2L"]; Y2 = Z["Y2"]; C3 = Z["C3"]
u = U[:, cl[0]]
out["u_casimirs"] = {"C2L": float(u @ C2L @ u), "Y2": float(u @ Y2 @ u), "C3": float(u @ C3 @ u)}
out["u_block_weights"] = {k: float(np.linalg.norm(u[sl]) ** 2) for k, sl in LD.BLOCKS.items()}
print(json.dumps(out, indent=1), flush=True)
t0 = time.time()
Hp_rows = target.parameter_rows(LD.chart.unpack(q0 + eta * u)); Hm_rows = target.parameter_rows(LD.chart.unpack(q0 - eta * u))
Hp = np.einsum("p,pij->ij", c, np.array([np.asarray(Hp_rows[i].hessian, float) for i in ids])); Hp = 0.5 * (Hp + Hp.T)
Hm = np.einsum("p,pij->ij", c, np.array([np.asarray(Hm_rows[i].hessian, float) for i in ids])); Hm = 0.5 * (Hm + Hm.T)
Vp = float(c @ np.array([Hp_rows[i].value for i in ids])); Vm = float(c @ np.array([Hm_rows[i].value for i in ids]))
dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * M) / eta ** 2
b = dH @ u; V4 = float(u @ d2H @ u)
heavy = w >= 3e-5; light = (w > 1e-9) & (w < 3e-5)
bh = U[:, heavy].T @ b; bl = U[:, light].T @ b
Rh = bh ** 2 / w[heavy]; Rl = bl ** 2 / w[light]
V0 = float(c @ Z["values"])
lam = {"eta": eta, "V4/6": V4 / 6, "sum_heavy_b2/m2": float(Rh.sum()), "lambda_eff_heavy": V4 / 6 - 0.5 * float(Rh.sum()),
       "sum_light_b2/m2": float(Rl.sum()), "V(q*+-eta u)-V*": [Vp - V0, Vm - V0],
       "largest_heavy_terms": sorted([(float(x), float(m)) for x, m in zip(Rh, w[heavy])], reverse=True)[:8],
       "largest_light_terms": sorted([(float(x), float(m)) for x, m in zip(Rl, w[light])], reverse=True)[:6],
       "|b|": float(np.linalg.norm(b)), "seconds": time.time() - t0}
out["lambda_tree"] = lam
print(json.dumps(lam, indent=1), flush=True)
json.dump(out, open(LD.HERE / "sk_lambda.json", "w"), indent=1, default=float)
