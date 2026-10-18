#!/usr/bin/env python3
"""Post-analysis of a coupling point of v22-L2 at its G3211 -> SM vacuum (531 chart).

* exact stationarity, Goldstone count, full spectrum and its SM multiplet decomposition (chart531.decompose_hessian;
  exact at the SM-symmetric vacuum, leakage reported), the G3211 projection for orientation (leakage ~ r),
* optional --repo: the 51 v20 rows recomputed with the repository compiler (authoritative backend) and compared with the
  fast poly backend (values, gradients, Hessians), spectrum recomputed from the repo rows,
* EW doublet composition (|r|, s, f_Sigma, beta), tree lambda_eff (heavy / all), one-loop Coleman-Weinberg estimate of
  the threshold to lambda (R2-A r2a_cw_lambda method: second-order degenerate PT of m_s^2(h), Landau gauge, scalars +
  gauge bosons, rho terms and fermions dropped) [EST],
* light-octet cubic couplings (d-symbol / f eps invariants) and mixed light cubics,
* a0 (singlet channel), coupling box ratios.
usage: python -B vpost.py <pt_tag> <solution npz> <out> [--repo] [--eta 0.05]
"""
from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np

import vc

C = vc.C
ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("sol")
ap.add_argument("out")
ap.add_argument("--repo", action="store_true")
ap.add_argument("--eta", type=float, default=0.05)
ap.add_argument("--eps_hi", type=float, default=3e-6)
ap.add_argument("--g", type=float, default=0.58)
ap.add_argument("--cubics", default="", help="semicolon list of light components, label[#n_light] e.g. '(8,3)_{Y=0},(6bar,2)_{Y=+1/6}'")
args = ap.parse_args()
T0 = time.time()
log = vc.Logger(vc.BIG / f"{args.out}.log")
P = np.load(vc.BIG / f"pt_{args.tag}.npz")
PJ = json.load(open(vc.BIG / f"pt_{args.tag}.json"))
S = np.load(args.sol if (":" in args.sol) else vc.BIG / args.sol)
c = S["c"]
q0 = P["q"]
pt = PJ["point"]
out = {"tag": args.tag, "solution": args.sol, "point": pt, "c": vc.cdict(c)}

vals, grads, hess = vc.rows_at(q0, hessian=True, backend="poly")
H = np.einsum("k,kij->ij", c, hess, optimize=True)
H = 0.5 * (H + H.T)
g = c @ grads
out["V_star"] = float(c @ vals)
out["grad_norm"] = float(np.linalg.norm(g))
T, ranks = C.symmetry_matrix(q0)
out["symmetry_ranks"] = ranks
w, V = np.linalg.eigh(H)
out["n_zero"] = int(np.sum(np.abs(w) < 1e-9))
out["n_negative"] = int(np.sum(w < -1e-9))
out["n_light"] = int(np.sum((w >= 1e-9) & (w < 10 * args.eps_hi)))
out["n_heavy"] = int(np.sum(w >= 10 * args.eps_hi))
out["min_heavy"] = float(np.min(w[w >= 10 * args.eps_hi]))
out["eigenvalues_lowest_60"] = w[:60].tolist()
log(f"V* = {out['V_star']:.10g}; |grad| {out['grad_norm']:.2e}; ranks {ranks}; zero {out['n_zero']} neg {out['n_negative']} "
    f"light {out['n_light']} heavy {out['n_heavy']} (min heavy {out['min_heavy']:.4g})")
dec = C.decompose_hessian(H, "SM", tangents=T)
spec = []
for comp in dec["components"]:
    spec.append({"label": comp["label"], "real_dim": comp["real_dim"], "copies": comp["m"],
                 "goldstone_real_dim": comp["goldstone_real_dim"], "spectrum_m2": comp["spectrum"],
                 "leakage": comp["leakage"]})
out["SM_multiplets"] = spec
out["SM_max_leakage"] = dec["max_leakage"]
decG = C.decompose_hessian(H, "G3211", tangents=T)
out["G3211_projection_max_leakage"] = decG["max_leakage"]
out["G3211_multiplets"] = [{"label": comp["label"], "real_dim": comp["real_dim"], "goldstone_real_dim": comp["goldstone_real_dim"],
                            "block_eigenvalues_min": float(min(comp["block_eigenvalues"])),
                            "block_eigenvalues_max": float(max(comp["block_eigenvalues"]))} for comp in decG["components"]]
log(f"SM decomposition: max leakage {dec['max_leakage']:.2e}; Goldstones {sum(x['goldstone_real_dim'] or 0 for x in spec)}")
for x in spec:
    lows = [f"{s_['mass_squared']:.4g}x{s_['real_multiplicity']}" for s_ in x["spectrum_m2"][:4]]
    log(f"   {x['label']:18s} dim {x['real_dim']:3d} gold {x['goldstone_real_dim']}  m^2: {', '.join(lows)}")

# ---------------- repo confirmation
if args.repo:
    t1 = time.time()
    rv, rg, rh = vc.rows_at(q0, hessian=True, backend="repo")
    dv = float(np.max(np.abs(rv - vals)) / max(1.0, np.max(np.abs(vals))))
    dg = float(np.max(np.abs(rg - grads)) / max(1.0, np.max(np.abs(grads))))
    dh = float(np.max(np.abs(rh - hess)) / max(1.0, np.max(np.abs(hess))))
    Hr = np.einsum("k,kij->ij", c, rh, optimize=True)
    Hr = 0.5 * (Hr + Hr.T)
    wr = np.linalg.eigvalsh(Hr)
    out["repo_check"] = {"max_rel_diff_values": dv, "max_rel_diff_gradients": dg, "max_rel_diff_hessians": dh,
                         "grad_norm_repo": float(np.linalg.norm(c @ rg)), "V_star_repo": float(c @ rv),
                         "n_zero": int(np.sum(np.abs(wr) < 1e-9)), "n_negative": int(np.sum(wr < -1e-9)),
                         "n_light": int(np.sum((wr >= 1e-9) & (wr < 10 * args.eps_hi))),
                         "min_heavy": float(np.min(wr[wr >= 10 * args.eps_hi])),
                         "max_abs_eig_diff": float(np.max(np.abs(wr - w))), "seconds": time.time() - t1}
    log(f"repo check: {out['repo_check']}")

# ---------------- EW doublet, lambda_eff, CW
if "a_ew" in S.files and S["a_ew"].size:
    a = S["a_ew"]
    u = np.real(P["neutral"] @ a)
    u /= np.linalg.norm(u)
    F = vc.FastV(c)
    eta = args.eta
    Hp = F.hessian(q0 + eta * u)
    Hm = F.hessian(q0 - eta * u)
    dH = (Hp - Hm) / (2 * eta)
    d2H = (Hp + Hm - 2 * H) / eta ** 2
    b = dH @ u                                    # T(u, u, .)
    J4u = vc.J_values(u[None, :])[0] * (vc.DEG == 4)
    lam_dir = 4.0 * float(c @ J4u)
    lam_ew = float(u @ H @ u)
    gold = np.abs(w) < 1e-9
    ew = np.abs(w - lam_ew) < 0.3 * abs(lam_ew) + 1e-12
    heavy = (w >= 10 * args.eps_hi) & ~ew
    light = ~gold & ~heavy & ~ew
    bh = V[:, heavy].T @ b
    bl = V[:, light].T @ b
    Rh = float(np.sum(bh ** 2 / w[heavy]))
    Rl = float(np.sum(bl ** 2 / w[light])) if light.any() else 0.0
    out["ew"] = {"doublet_m2": lam_ew, "lambda_direct": lam_dir, "R_heavy": Rh, "lambda_eff_heavy": lam_dir - Rh / 2,
                 "R_light": Rl, "lambda_eff_all": lam_dir - (Rh + Rl) / 2,
                 "light_terms": sorted([(float(x * x / m_), float(m_)) for x, m_ in zip(bl, w[light])], reverse=True)[:6],
                 "max_b_goldstone": float(np.max(np.abs(V[:, gold].T @ b))) if gold.any() else 0.0}
    # composition
    st = C.chart.unpack(np.asarray(u[:486], float))
    hvec = np.asarray(st.h, complex)
    log(f"EW: m2 {lam_ew:.3e}; lambda direct {lam_dir:.4g}, eff_heavy {lam_dir - Rh / 2:.4g}, eff_all {lam_dir - (Rh + Rl) / 2:.4g}")

    # CW (R2-A method)
    dHe = V.T @ dH @ V
    d2He = V.T @ d2H @ V
    is_skip = gold | ew

    def clusters_of(vals_, rel=1e-6, absolute=1e-12):
        order = np.argsort(vals_)
        cl = []
        cur = [order[0]]
        for j in order[1:]:
            if abs(vals_[j] - vals_[cur[-1]]) <= max(absolute, rel * abs(vals_[cur[-1]])):
                cur.append(j)
            else:
                cl.append(cur)
                cur = [j]
        cl.append(cur)
        return cl

    def kappas(ww, M1, M2, skip):
        res = []
        for cl in clusters_of(ww):
            if all(skip[j] for j in cl):
                continue
            idx = np.array(cl)
            rest = np.array([t for t in range(len(ww)) if t not in set(cl)])
            Kc = M2[np.ix_(idx, idx)].copy()
            if rest.size:
                den = ww[idx[0]] - ww[rest]
                Kc += 2 * (M1[np.ix_(idx, rest)] / den[None, :]) @ M1[np.ix_(rest, idx)]
            for k_ in np.linalg.eigvalsh(0.5 * (Kc + Kc.T)):
                res.append((float(ww[idx[0]]), float(k_)))
        return res

    scal = kappas(w, dHe, d2He, is_skip)
    T1, _ = C.symmetry_matrix(u)
    G0 = T[:, :46]
    G1 = T1[:, :46]
    gg = args.g
    M0 = 0.5 * gg * gg * (G0.T @ G0)
    M1g = 0.5 * gg * gg * (G0.T @ G1 + G1.T @ G0)
    M2g = gg * gg * (G1.T @ G1)
    wv, Vv = np.linalg.eigh(M0)
    gauge = kappas(wv, Vv.T @ M1g @ Vv, Vv.T @ M2g @ Vv, np.abs(wv) < 1e-12)

    def dlam(pairs, mu2, nfac=1.0):
        tot = 0.0
        for m2, kap in pairs:
            if m2 <= 0:
                continue
            tot += nfac * 3 * (2 * math.log(m2 / mu2)) * kap * kap / (64 * math.pi ** 2)
        return tot / 6

    hs = [(m2, k_) for m2, k_ in scal if m2 >= 10 * args.eps_hi]
    ls = [(m2, k_) for m2, k_ in scal if m2 < 10 * args.eps_hi]
    hg = [(m2, k_) for m2, k_ in gauge if m2 >= 1e-4]
    lg = [(m2, k_) for m2, k_ in gauge if m2 < 1e-4]
    r2 = pt["r"] ** 2
    out["cw_one_loop_EST"] = {"heavy_scalars(mu=|Phi|)": dlam(hs, 1.0), "heavy_scalars(mu=0.3|Phi|)": dlam(hs, 0.09),
                              "light_scalars(mu=v_R)": dlam(ls, r2), "heavy_gauge(mu=|Phi|)": dlam(hg, 1.0, 3.0),
                              "light_gauge(mu=v_R)": dlam(lg, r2, 3.0),
                              "heavy_kappa_rms": float(np.sqrt(np.mean([k_ ** 2 for _, k_ in hs]))) if hs else None,
                              "sum_kappa2_over_64pi2_heavy": float(sum(k_ ** 2 for _, k_ in hs) / (64 * math.pi ** 2)),
                              "note": "Landau gauge; exact Goldstones and the light doublet excluded; rho terms, fermions dropped"}
    cw = out["cw_one_loop_EST"]
    out["ew"]["lambda_one_loop_EST(mu=|Phi|)"] = out["ew"]["lambda_eff_all"] + cw["heavy_scalars(mu=|Phi|)"] + \
        cw["heavy_gauge(mu=|Phi|)"] + cw["light_scalars(mu=v_R)"] + cw["light_gauge(mu=v_R)"]
    log(f"CW (EST): {json.dumps(cw)}")

# ---------------- light-state cubic couplings (self cubics of the light octets, mixed light cubics)
def light_space(label, nl=None):
    comp = [x for x in C.real_components("SM") if x["label"] == label][0]
    R = comp["W"]
    if nl is None:
        return R
    Hc = R.T @ H @ R
    ww, VV = np.linalg.eigh(0.5 * (Hc + Hc.T))
    return R @ VV[:, :nl]


def cubic_slices(L, F_):
    """T(e_a, ., .) for the columns e_a of L (exact: central difference of Hessians of a quartic polynomial)."""
    h = 0.05
    return [(F_.hessian(q0 + h * L[:, a_]) - F_.hessian(q0 - h * L[:, a_])) / (2 * h) for a_ in range(L.shape[1])]


if args.cubics:
    Fc = vc.FastV(c)
    cub = {}
    labs = [x.strip() for x in args.cubics.split(";") if x.strip()]
    spaces = {}
    for lab in labs:
        nm, _, nl = lab.partition("#")
        spaces[lab] = light_space(nm, int(nl) if nl else None)
    slices = {lab: cubic_slices(L, Fc) for lab, L in spaces.items()}
    for lab in labs:      # self cubic: Frobenius norm of T restricted to L x L x L
        L = spaces[lab]
        Tl = np.array([L.T @ Ts @ L for Ts in slices[lab]])
        cub[f"self {lab}"] = {"frobenius": float(np.linalg.norm(Tl)), "max_abs_entry": float(np.max(np.abs(Tl)))}
    for i, la in enumerate(labs):
        for lb in labs[i + 1:]:
            La_, Lb_ = spaces[la], spaces[lb]
            T1 = np.array([Lb_.T @ Ts @ Lb_ for Ts in slices[la]])     # T(a, b, b')
            T2 = np.array([La_.T @ Ts @ La_ for Ts in slices[lb]])     # T(b, a, a')
            cub[f"mixed {la} x {lb}^2"] = {"frobenius": float(np.linalg.norm(T1)), "max_abs_entry": float(np.max(np.abs(T1)))}
            cub[f"mixed {lb} x {la}^2"] = {"frobenius": float(np.linalg.norm(T2)), "max_abs_entry": float(np.max(np.abs(T2)))}
    out["light_cubics"] = cub
    log(f"light cubics: {json.dumps(cub)}")

# ---------------- a0 and boxes
UT = np.load(vc.BIG / "unit_traces.npz")
out["a0"] = (np.linalg.eigvalsh(np.einsum("k,kij->ij", c, UT["Mi"])) / (16 * math.pi)).tolist()
bx = vc.boxes()
out["box_ratio_max"] = float(np.max(np.abs(c) / bx))
out["box_ratio_top"] = sorted([(vc.IDS[i], float(abs(c[i]) / bx[i])) for i in range(vc.NPAR)], key=lambda t: -t[1])[:10]
out["seconds"] = time.time() - T0
json.dump(vc.jsonable(out), open(vc.BIG / f"{args.out}.json", "w"), indent=1)
log(f"done {time.time()-T0:.0f}s")
