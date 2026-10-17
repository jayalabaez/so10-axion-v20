"""One-loop (Coleman-Weinberg, Landau gauge) threshold to the light-doublet quartic from the scalar and gauge spectrum,
via the field-dependent masses m_s^2(h) along the neutral up-type H10 direction u.

For V1 = sum_s n_s f(m_s^2(h)), f(m2) = m2^2 (ln m2/mu^2 - 3/2)/(64 pi^2):  d^4 V1/dh^4|_0 = sum_s n_s [3 f''(m_s^2) kappa_s^2 + f'(m_s^2) rho_s]
with kappa_s = d^2 m_s^2/dh^2 (second-order degenerate perturbation theory from the exact dH = d_u Hess, d2H = d_u^2 Hess),
f'' = 2 ln(m2/mu^2)/(64 pi^2); the rho_s (fourth derivative of m_s^2) term is dropped (it is suppressed by m_s^2 for light
states; reported as a neglected piece).  delta lambda = delta V4 / 6.  Gauge bosons: M^2(h) = (g^2/2) (T q)^T (T q) with
q = q0 + h u (exactly quadratic in h), 3 polarisations, g = 0.58.  Excluded: exact Goldstones (gauge IR), the light doublet
itself, massless SM gauge bosons (their effect is the SM running), fermions (not computed).
usage: python -B k3_cw_lambda.py <solution npz> <out tag> [eta]
"""
from __future__ import annotations
import sys, json, math, time, numpy as np
import k3_common as K
import r2_verify as VF

solpath, tag = sys.argv[1], sys.argv[2]; eta = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
sol = np.load(K.SCRATCH / solpath); c = sol["c"]; ids = [str(x) for x in sol["ids"]]; assert ids == VF.ids
chart = K.chart; q0 = VF.q0; u = VF.CUB["u_up"]; g = 0.58
t0 = time.time()
H0 = VF.full_hessian(c)
rows_p = K.parameter_rows(chart.unpack(q0 + eta * u)); rows_m = K.parameter_rows(chart.unpack(q0 - eta * u))
Hp = sum(c[i] * np.asarray(rows_p[pid].hessian, float) for i, pid in enumerate(ids)); Hp = 0.5 * (Hp + Hp.T)
Hm = sum(c[i] * np.asarray(rows_m[pid].hessian, float) for i, pid in enumerate(ids)); Hm = 0.5 * (Hm + Hm.T)
dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
print(f"rows done ({time.time()-t0:.0f}s)")
w, V = np.linalg.eigh(H0)
ops = K.candidate.sm_label_operators(); C2L = ops["C2L"]; C3 = ops["C3"]
is_doublet = np.array([abs(V[:, j] @ C2L @ V[:, j] - 0.75) < 1e-6 and abs(V[:, j] @ C3 @ V[:, j]) < 1e-6 and w[j] < 10 * VF.EPS_HI and w[j] > 1e-9 for j in range(len(w))])
is_gold = np.abs(w) < 1e-9
dHe = V.T @ dH @ V; d2He = V.T @ d2H @ V


def clusters_of(vals, rel=1e-6, absolute=1e-12):
    order = np.argsort(vals); cl = []; cur = [order[0]]
    for j in order[1:]:
        if abs(vals[j] - vals[cur[-1]]) <= max(absolute, rel * abs(vals[cur[-1]])): cur.append(j)
        else: cl.append(cur); cur = [j]
    cl.append(cur); return cl


def kappas(w, M1, M2, skip):
    """second-order degenerate PT: for each cluster, K = M2_cc + 2 sum_{t notin c} M1_ct M1_tc/(w_c - w_t); returns list of (w, kappa)."""
    out = []
    for cl in clusters_of(w):
        if all(skip[j] for j in cl): continue
        idx = np.array(cl); rest = np.array([t for t in range(len(w)) if t not in set(cl)])
        Kc = M2[np.ix_(idx, idx)].copy()
        if rest.size:
            denom = w[idx[0]] - w[rest]
            Kc += 2 * (M1[np.ix_(idx, rest)] / denom[None, :]) @ M1[np.ix_(rest, idx)]
        kk = np.linalg.eigvalsh(0.5 * (Kc + Kc.T))
        for k_ in kk: out.append((float(w[idx[0]]), float(k_)))
    return out


scal = kappas(w, dHe, d2He, is_gold | is_doublet)
# gauge bosons: tangents T_a q (486 x 45) at q0 and along u: G0 = T q0, G1 = T u  ->  M^2(h) = (g^2/2)(G0 + h G1)^T (G0 + h G1)
full0, _ = K.candidate.symmetry_matrix(chart.unpack(q0)); full1, _ = K.candidate.symmetry_matrix(chart.unpack(u))
G0 = full0[:, :45]; G1 = full1[:, :45]   # so(10) columns (the U(1)_X / PQ columns are the global/gauged-X extra; include X as gauged: 46)
G0 = full0[:, :46]; G1 = full1[:, :46]
M0 = 0.5 * g * g * (G0.T @ G0); M1 = 0.5 * g * g * (G0.T @ G1 + G1.T @ G0); M2 = g * g * (G1.T @ G1)
wv, Vv = np.linalg.eigh(M0); M1e = Vv.T @ M1 @ Vv; M2e = Vv.T @ M2 @ Vv
massless = np.abs(wv) < 1e-12
gauge = kappas(wv, M1e, M2e, massless)


def delta_lambda(pairs, mu2, nfac=1.0):
    tot = 0.0; rows = []
    for m2, kap in pairs:
        if m2 <= 0: continue
        dV4 = nfac * 3 * (2 * math.log(m2 / mu2)) * kap * kap / (64 * math.pi ** 2); tot += dV4; rows.append((m2, kap, dV4 / 6))
    return tot / 6, rows


light_scal = [(m2, k_) for m2, k_ in scal if m2 < 10 * VF.EPS_HI]; heavy_scal = [(m2, k_) for m2, k_ in scal if m2 >= 10 * VF.EPS_HI]
light_gauge = [(m2, k_) for m2, k_ in gauge if m2 < 1e-4]; heavy_gauge = [(m2, k_) for m2, k_ in gauge if m2 >= 1e-4]
mu_light2 = VF.point["r"] ** 2  # v_R^2 in |Phi| = 1 units
res = {"solution": solpath, "eta": eta, "g": g, "n_scalar_modes_used": len(scal), "n_gauge_modes_used": len(gauge),
       "tree": VF.lambda_eff_exact(c, "up"),
       "light_scalars(mu=v_R)": delta_lambda(light_scal, mu_light2)[0], "light_scalars_rows": sorted(delta_lambda(light_scal, mu_light2)[1], key=lambda r: -abs(r[2]))[:10],
       "heavy_scalars(mu=|Phi|)": delta_lambda(heavy_scal, 1.0)[0], "heavy_scalars(mu=0.3|Phi|)": delta_lambda(heavy_scal, 0.09)[0],
       "heavy_scalars_kappa_rms": float(np.sqrt(np.mean([k_ ** 2 for _, k_ in heavy_scal]))) if heavy_scal else None,
       "heavy_scalars_sum_kappa2_over_64pi2": float(sum(k_ ** 2 for _, k_ in heavy_scal) / (64 * math.pi ** 2)),
       "light_scalars_sum_kappa2_over_64pi2": float(sum(k_ ** 2 for _, k_ in light_scal) / (64 * math.pi ** 2)),
       "heavy_gauge(mu=|Phi|)": delta_lambda(heavy_gauge, 1.0, nfac=3.0)[0], "light_gauge(mu=v_R)": delta_lambda(light_gauge, mu_light2, nfac=3.0)[0],
       "gauge_masses_light": [m2 for m2, _ in light_gauge][:6], "n_gauge_massless": int(np.sum(massless)),
       "excluded": "exact Goldstones, light doublet (8 modes), massless gauge bosons, fermions; rho (d^4 m^2/dh^4) terms dropped",
       "seconds": time.time() - t0}
json.dump(res, open(K.SCRATCH / f"cwlam_{tag}.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if "rows" not in k and k != "tree"}, indent=None, default=float))
print("tree:", {k: v for k, v in res["tree"].items() if "terms" not in k})
print("top light-scalar rows (m2, kappa, dlambda):", res["light_scalars_rows"][:6])
