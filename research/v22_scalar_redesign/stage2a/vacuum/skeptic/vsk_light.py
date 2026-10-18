#!/usr/bin/env python3
"""Light-sector stability at the formal-round points (a NECESSARY condition of the G3 global-minimum standard with
the PHYSICAL light masses, which the tester's descents cannot see because they use placeholder light masses
m^2 ~ 1e-7 .. 3e-6 and a 'lower' threshold of 2.5e-6).

With every light multiplet massless (physical: (8,1) at TeV, (8,3) at ~2e9, (6bar,2) ~1e11, doublet at EW), the
tree-level effective potential of the light fields phi in L (light subspace minus the light singlets, which sit at
v_R / <S> and are integrated out) is
    V_L(phi) = C(phi) + lambda(phi),   C = (1/6) T*(phi,phi,phi)   (light cubic),
    lambda(phi) = V4(phi) - (1/8) tau(phi)^T K tau(phi),   tau(phi) = T*(phi,phi,.),  K = (H*)^+ on heavy + light singlets.
q* can only be the global minimum (as m_light -> 0) if C = 0 on L (tunings) and lambda >= 0 on L.  For the EW
direction 4 lambda(u_EW) is the tester's lambda_eff_all (cross-check).
Engine: vc.FastV (the tester's exact polynomial; validated against my independent evaluator in vsk_validate.json and
re-checked here at q*).  Labels: NUM (float64; T* from exact symmetric Hessian-vector differences of a quartic).
usage: python -B vsk_light.py <solution npz> [<solution npz> ...]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from scipy.optimize import minimize

import vsk_eval as E

sys.path.insert(0, str(E.HERE.parent))
import vc  # noqa: E402

C = vc.C
P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
ops = C.label_operators()


def casimirs(Vs):
    """colour / weak Casimir and Y expectation on a real subspace (columns orthonormal)."""
    out = {}
    for k in ("C3_op", "C2_op", "Y_op"):
        if k in ops:
            M = ops[k]
            out[k] = np.real(Vs.T @ M @ Vs)
    return out


res = {}
for sol in sys.argv[1:]:
    t0 = time.time()
    c = E.load_c(sol)
    cv = np.array([c[p] for p in vc.IDS])
    F = vc.FastV(cv)
    F4 = vc.FastV(cv * (vc.DEG == 4))
    V0, g0 = F.value_grad(qs)
    Vmine = E.V(qs, c)
    H = F.hessian(qs)
    w, U = np.linalg.eigh(H)
    zero = np.abs(w) < 1e-9
    neg = w < -1e-9
    light = (w >= 1e-9) & (w < 3e-5)
    heavy = w >= 3e-5
    Ul = U[:, light]
    wl = w[light]
    # identify light singlets (Y = 0 colour singlet weak singlet) via the label operators
    lab = {}
    if ops:
        for k in ("C3_op", "C2_op", "Y_op"):
            if k in ops:
                pass
    # cluster light modes by eigenvalue and by Casimirs (colour C3, weak C2)
    names = list(ops.keys())
    cas = {}
    for k in names:
        M = np.asarray(ops[k])
        if M.shape == (vc.N, vc.N):
            cas[k] = M
    # colour Casimir on the light space: Hermitian charges Q = -i G -> Casimir = -sum G^2 (real symmetric)
    info_modes = []
    Cc = cas.get("C3", cas.get("C3_op"))
    Cw = cas.get("C2L", cas.get("C2_op"))
    singlet_mask = np.zeros(Ul.shape[1], bool)
    if Cc is not None and Cw is not None:
        # simultaneous diagonalisation on the light space
        Mc = Ul.T @ (Cc + 0.1 * np.pi * Cw) @ Ul
        Mc = 0.5 * (Mc + Mc.T)
        ec, Rc = np.linalg.eigh(Mc)
        Ul2 = Ul @ Rc
        cc = np.einsum("ia,ij,ja->a", Ul2, Cc, Ul2)
        cw = np.einsum("ia,ij,ja->a", Ul2, Cw, Ul2)
        Ul = Ul2
        singlet_mask = (np.abs(cc) < 1e-6) & (np.abs(cw) < 1e-6)
        info_modes = sorted(set((round(float(a), 4), round(float(b), 4)) for a, b in zip(cc, cw)))
    else:
        # fallback: the light singlets are the two lightest-but-not-doublet modes with eigenvalue outside the
        # doublet/octet plateaus (by eigenvalue clustering)
        info_modes = ["no Casimir operators found: " + ",".join(names)]
    L = Ul[:, ~singlet_mask]
    Lsing = Ul[:, singlet_mask]
    nL = L.shape[1]
    # response kernel: heavy modes + light singlets
    Kmodes = np.hstack([U[:, heavy], Lsing])
    Kvals = np.concatenate([w[heavy], np.array([float(x @ H @ x) for x in Lsing.T])]) if Lsing.size else w[heavy]
    # T*(e_i, e_j, .) for the light basis via exact symmetric HVP differences
    eps = 1e-3
    TL = np.zeros((nL, nL, vc.N))
    for i in range(nL):
        ei = L[:, i]
        Hp = None
        for j in range(i, nL):
            ej = L[:, j]
            d = (F.hvp(qs + eps * ei, ej) - F.hvp(qs - eps * ei, ej)) / (2 * eps)
            TL[i, j] = d
            TL[j, i] = d
    # light cubic form C(u) = (1/6) sum u_i u_j u_k T(e_i,e_j,e_k)
    T3 = np.einsum("ijn,nk->ijk", TL, L)
    T3 = (T3 + T3.transpose(1, 2, 0) + T3.transpose(2, 0, 1) + T3.transpose(0, 2, 1) + T3.transpose(2, 1, 0)
          + T3.transpose(1, 0, 2)) / 6.0
    TK = np.einsum("ijn,nm->ijm", TL, Kmodes)          # projections on the response modes
    invK = 1.0 / Kvals

    def lam(x):
        n2 = float(x @ x)
        u = L @ x
        V4, g4 = F4.value_grad(u)
        g4x = L.T @ g4
        tau = np.einsum("i,j,ijm->m", x, x, TK)
        R = float(np.sum(tau * tau * invK))
        dtau = 2 * np.einsum("j,ijm->im", x, TK)
        gR = 2 * dtau @ (tau * invK)
        f = (V4 - R / 8.0) / n2 ** 2
        gf = (g4x - gR / 8.0) / n2 ** 2 - 4.0 * (V4 - R / 8.0) * x / n2 ** 3
        return f, gf

    def cub(x):
        n2 = float(x @ x)
        Cx = float(np.einsum("ijk,i,j,k->", T3, x, x, x)) / 6.0
        g = 0.5 * np.einsum("ijk,j,k->i", T3, x, x)
        return -abs(Cx) / n2 ** 1.5, -np.sign(Cx) * g / n2 ** 1.5 + 3 * abs(Cx) * x / n2 ** 2.5

    rng = np.random.default_rng(5)
    best = (np.inf, None)
    lam_samples = []
    for s in range(60):
        x0 = rng.normal(size=nL)
        r = minimize(lam, x0, jac=True, method="L-BFGS-B", options={"maxiter": 3000, "gtol": 1e-12, "ftol": 1e-15})
        lam_samples.append(float(r.fun))
        if r.fun < best[0]:
            best = (float(r.fun), r.x / np.linalg.norm(r.x))
    bc = (0.0, None)
    for s in range(30):
        x0 = rng.normal(size=nL)
        r = minimize(cub, x0, jac=True, method="L-BFGS-B", options={"maxiter": 2000, "gtol": 1e-14})
        if r.fun < bc[0]:
            bc = (float(r.fun), r.x / np.linalg.norm(r.x))
    xb = best[1]
    ub = L @ xb
    comp_b = {}
    if Cc is not None:
        comp_b = {"colour_casimir": float(ub @ Cc @ ub), "weak_casimir": float(ub @ Cw @ ub)}
    # EW-direction cross check: the light (1,2) modes (weak Casimir 3/4, colour 0) - min of lambda on that subspace
    ew_check = None
    if Cc is not None:
        cc_L = np.einsum("ia,ij,ja->a", L, Cc, L)
        cw_L = np.einsum("ia,ij,ja->a", L, Cw, L)
        dmask = (np.abs(cc_L) < 1e-6) & (np.abs(cw_L - 0.75) < 1e-6)
        if dmask.any():
            vals = []
            for s in range(20):
                x0 = np.zeros(nL)
                x0[dmask] = rng.normal(size=int(dmask.sum()))
                fx = lambda xx: lam(np.where(dmask, xx, 0.0))
                r = minimize(lambda xx: (lam(np.where(dmask, xx, 0.0))[0], np.where(dmask, lam(np.where(dmask, xx, 0.0))[1], 0.0)),
                             x0, jac=True, method="L-BFGS-B", options={"maxiter": 2000, "gtol": 1e-12})
                vals.append(float(r.fun))
            ew_check = {"n_doublet_modes": int(dmask.sum()), "min_lambda_on_doublet_space": min(vals),
                        "4x": 4 * min(vals)}
    # multiplet content of the most cubic light direction
    cubic_weights = {}
    if Cc is not None and bc[1] is not None:
        cc_L = np.einsum("ia,ij,ja->a", L, Cc, L)
        cw_L = np.einsum("ia,ij,ja->a", L, Cw, L)
        for a_, b_, x_ in zip(cc_L, cw_L, bc[1]):
            key = f"({a_:.3f},{b_:.3f})"
            cubic_weights[key] = cubic_weights.get(key, 0.0) + float(x_ * x_)
    # how deep would the light-direction minimum be at the tester's placeholder masses, and at physical masses
    m2_place = float(np.max(wl))
    out = {"sol": sol, "V_star_FastV": V0, "V_star_mine": Vmine, "|grad|": float(np.linalg.norm(g0)),
           "n_zero": int(zero.sum()), "n_neg": int(neg.sum()), "n_light": int(light.sum()), "n_heavy": int(heavy.sum()),
           "min_heavy": float(w[heavy][0]), "light_eigs": sorted(set(np.round(wl, 12).tolist())),
           "n_light_singlets_integrated_out": int(Lsing.shape[1]), "nL": nL, "light_labels_(C3,C2)": info_modes,
           "lambda_min_on_L": best[0], "lambda_min_4x": 4 * best[0], "lambda_min_dir_casimirs": comp_b,
           "lambda_samples_lowest10": sorted(lam_samples)[:10],
           "max_light_cubic_|C(u)|_unit": -bc[0],
           "cubic_dir_weights_by_(C3,C2L)": cubic_weights,
           "ew_crosscheck": ew_check,
           "depth_at_placeholder_mass_EST": (-(m2_place ** 2) / (16 * abs(best[0]))) if best[0] < 0 else None,
           "seconds": time.time() - t0}
    print(json.dumps({k: v for k, v in out.items() if k != "lambda_samples_lowest10"}, indent=1, default=float), flush=True)
    res[sol] = out
    np.savez_compressed(E.BIGS / f"light_{sol[:-4]}.npz", L=L, xb=xb, xc=bc[1], TK=TK, Kvals=Kvals, w=w)
    json.dump(res, open(E.HERE / f"vsk_light_{'_'.join(s[:-4] for s in sys.argv[1:])}.json", "w"), indent=1, default=float)
