"""Shared verification of a coupling vector c at the Am45 G3221 point (no LP): full Hessian counts, exact tree
lambda_eff along the neutral up-type H10 direction (b_i, V4_i from cubic_rows.npz), singlet-channel a0, BFB bank,
competitor bank gap, and the exact SM-singlet-subspace polynomial screens (smsinglet 6-d and deltar 7-d)."""
from __future__ import annotations
import json, math, itertools, numpy as np
from scipy.optimize import minimize
import k3_common as K

import os
TAG = os.environ.get("R2_TAG", "Am45")
Z = np.load(K.SCRATCH / f"{TAG}_rows.npz"); HESS = Z["hess"]; VAL0 = Z["values"]; GRADS = Z["grads"]; q0 = Z["q"]
ids = [str(x) for x in Z["ids"]]; n_par = len(ids)
point = json.load(open(K.SCRATCH / f"{TAG}_rows_meta.json"))["point"]
CUB = np.load(K.SCRATCH / os.environ.get("R2_CUBIC", "cubic_rows.npz")); b_up = CUB["b_up"]; V4_up = CUB["V4_up"]; b_dn = CUB["b_dn"] if "b_dn" in CUB.files else CUB["b_up"]; V4_dn = CUB["V4_dn"] if "V4_dn" in CUB.files else CUB["V4_up"]
TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8")); DEG = TR["degrees"]
deg4 = np.array([DEG[p.split("::")[1]] == 4 for p in ids])
chart = K.chart; basis = K.direct.singlet_basis()
EPS_HI = 3.0e-6


def pk(**kw):
    d = dict(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=0j); d.update(kw); return chart.pack(K.potential.FieldState(**d))


sig_std = K.candidate.sigma_std_unit_coordinates()
drc = chart.sigma_coordinates(K.direct.delta_r()); drc /= np.linalg.norm(drc)
SUBDIRS = [pk(phi=basis["p"]), pk(phi=basis["a"]), pk(phi=basis["omega"]), pk(sigma=chart.sigma_from_coordinates(sig_std)),
           pk(sigma=chart.sigma_from_coordinates(drc)), pk(s=1 + 0j), pk(x=1 + 0j)]
zstar = np.array([point["p"], point["a"], point["omega"], point["r"], 0.0, point["s"], point["x"]])


def J_from_values(vals, dids):
    dindex = {d: j for j, d in enumerate(dids)}; J = np.zeros((vals.shape[0], n_par))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = dindex[did]
        J[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return J


def state_of_z(z):
    phi = K.phi_form(z[0], z[1], z[2]); sigma = chart.sigma_from_coordinates(z[3] * sig_std + z[4] * drc)
    return K.potential.FieldState(phi=phi, h=np.zeros(10, complex), sigma=sigma, s=complex(z[5]), x=complex(z[6])).validated()


def in_g3221_orbit(z):
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-3 and abs(abs(z[1]) - abs(zstar[1])) < 2e-3 and abs(z[2]) < 2e-3
            and abs(z[6] - zstar[6]) < 2e-2 and math.hypot(z[3], z[4]) < 0.02)


class SubspaceFit:
    def __init__(self, npz, mode, seed=11, n_sample=40000):
        pts = np.load(K.SCRATCH / npz); self.mode = mode; rng = np.random.default_rng(seed)
        self.Q = pts["Q"]; self.J = J_from_values(pts["values"], [str(x) for x in pts["ids"]])
        self.coords = np.array([[float(q @ d) / float(d @ d) for d in SUBDIRS] for q in self.Q])
        self.degs = [1, 1, 1, 2, 2, 2] if mode == "smsinglet" else [1, 1, 1, 2, 2, 2, 2]
        self.monos = np.array([pw for pw in itertools.product(range(5), repeat=len(self.degs)) if sum(p * d for p, d in zip(pw, self.degs)) <= 4])
        self.X = self.mono_matrix(self.coords); self.Pinv = np.linalg.pinv(self.X)
        zs = np.column_stack([rng.uniform(-1.5, 1.5, (n_sample, 3)), rng.uniform(0, 1.5, (n_sample, 2)), rng.uniform(0, 1.5, (n_sample, 1)), rng.uniform(0, 6, (n_sample, 1))])
        self.sample = zs; self.Xs = self.mono_matrix(zs)

    def var(self, z):
        z = np.atleast_2d(z)
        if self.mode == "smsinglet": return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
        return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 4] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])

    def mono_matrix(self, zs):
        v = self.var(zs); return np.prod(v[:, None, :] ** self.monos[None, :, :], axis=2)

    def fit(self, c):
        Vv = self.J @ c; coef = self.Pinv @ Vv; return coef, float(np.max(np.abs(self.X @ coef - Vv)))

    def V(self, coef, z):
        return float(self.mono_matrix(np.asarray(z)[None, :])[0] @ coef)

    def search(self, c, n_polish=30):
        coef, resid = self.fit(c); vs = self.Xs @ coef; order = np.argsort(vs)[:n_polish]; found = []
        for j in order:
            r = minimize(lambda z: self.V(coef, z), self.sample[j], method="BFGS", options={"gtol": 1e-9, "maxiter": 500}); found.append((float(r.fun), np.array(r.x)))
        r = minimize(lambda z: self.V(coef, z), zstar, method="BFGS", options={"gtol": 1e-9, "maxiter": 500}); found.append((float(r.fun), np.array(r.x)))
        found.sort(key=lambda t: t[0]); Vst = self.V(coef, zstar)
        if self.mode == "smsinglet":
            for _, zm in found: zm[4] = 0.0   # r2 is not a coordinate of the 6-d fit
        others = [(Vm, zm.tolist()) for Vm, zm in found if not in_g3221_orbit(zm)]
        return {"mode": self.mode, "fit_residual": resid, "V_star": Vst, "V_min_all": found[0][0], "argmin_all": found[0][1].tolist(),
                "lowest_non_orbit": others[:3], "n_lower_non_orbit": int(sum(1 for Vm, _ in others if Vm < Vst - 1e-9 * max(1, abs(Vst)))),
                "runaway": bool(np.max(np.abs(found[0][1])) > 30)}


_fits = None
def fits():
    global _fits
    if _fits is None: _fits = [SubspaceFit("smsinglet_pts.npz", "smsinglet"), SubspaceFit("deltar_pts.npz", "deltar")]
    return _fits


_banks = None
def banks():
    global _banks
    if _banks is None:
        comp, bfb = [], []
        for f in fits():
            for row, z in zip(f.J, f.coords):
                if not in_g3221_orbit(z): comp.append(row)
            nr = np.linalg.norm(f.Q, axis=1); bfb.append((f.J * deg4[None, :]) / nr[:, None] ** 4)
        for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):
            rp = np.load(K.SCRATCH / fn); Jr = J_from_values(rp["values"], [str(x) for x in rp["ids"]]); nr = np.linalg.norm(rp["Q"], axis=1)
            bfb.append((Jr * deg4[None, :]) / nr[:, None] ** 4)
        bfb.append((V4_up * deg4 / 24.0)[None, :])
        import os
        for fn in [x for x in os.environ.get('K3_EXTRA_BANKS', '').split(',') if x]:
            eb = np.load(K.SCRATCH / fn); Je = np.asarray(eb['J'], float) if 'J' in eb.files else J_from_values(eb['values'], [str(x) for x in eb['ids']]); ne = np.linalg.norm(eb['Q'], axis=1)
            for row, qq in zip(Je, eb['Q']):
                if np.linalg.norm(qq - q0) > 1e-6: comp.append(row)
            bfb.append((Je * deg4[None, :]) / ne[:, None] ** 4)
        _banks = (np.array(comp), np.vstack(bfb))
    return _banks


def full_hessian(c):
    H = np.einsum("p,pij->ij", c, HESS); return 0.5 * (H + H.T)


def lambda_eff_exact(c, which="up"):
    b_i, V4_i = (b_up, V4_up) if which == "up" else (b_dn, V4_dn)
    H = full_hessian(c); w, V = np.linalg.eigh(H); b = c @ b_i; V4 = float(c @ V4_i)
    gold = np.abs(w) < 1e-9; heavy = w >= 10 * EPS_HI; light = (~gold) & (~heavy)
    bh = V[:, heavy].T @ b; bl = V[:, light].T @ b; bg = V[:, gold].T @ b
    Rh = float(np.sum(bh ** 2 / w[heavy])); Rl_terms = bl ** 2 / w[light]; Rl = float(np.sum(Rl_terms))
    # heavy response split by field-block weight of the responding mode
    return {"lambda_direct": V4 / 6, "R_heavy": Rh, "lambda_eff_heavy": V4 / 6 - Rh / 2, "R_light": Rl, "lambda_eff_all": V4 / 6 - (Rh + Rl) / 2,
            "max_b_goldstone": float(np.max(np.abs(bg))) if bg.size else 0.0,
            "light_terms_sorted": sorted([(float(x), float(m)) for x, m in zip(Rl_terms, w[light])], reverse=True)[:6],
            "heavy_terms_top": sorted([(float(x), float(m)) for x, m in zip(bh ** 2 / w[heavy], w[heavy])], reverse=True)[:6]}


def a0_singlet(c):
    blocks = list(K.BLOCKS); n = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in blocks}; beta = np.zeros((5, 5))
    for jb, Bn in enumerate(blocks):
        tr = TR["blocks"][Bn]["traces"]
        for i, pid in enumerate(ids):
            if DEG[pid.split("::")[1]] != 4: continue
            for ia, An in enumerate(blocks): beta[ia, jb] += c[i] * tr[pid][An]
    M = np.zeros((5, 5))
    for ia, An in enumerate(blocks):
        for jb, Bn in enumerate(blocks): M[ia, jb] = beta[ia, jb] if ia == jb else math.sqrt(n[Bn] / n[An]) * beta[ia, jb]
    return (np.linalg.eigvalsh(0.5 * (M + M.T)) / (16 * math.pi)).tolist()


def verify(c, screen=True):
    H = full_hessian(c); w = np.linalg.eigvalsh(H)
    out = {"grad_residual": float(np.max(np.abs(GRADS.T @ c))), "V_star": float(VAL0 @ c),
           "full_hessian": {"n_zero(<1e-9)": int(np.sum(np.abs(w) < 1e-9)), "n_negative(<-1e-9)": int(np.sum(w < -1e-9)),
                            "n_light(<10 eps_hi)": int(np.sum((w >= 1e-9) & (w < 10 * EPS_HI))), "n_heavy": int(np.sum(w >= 10 * EPS_HI)),
                            "min_eigenvalue": float(w[0]), "min_heavy": float(np.min(w[w >= 10 * EPS_HI])), "light_levels": sorted(set(np.round(w[(w >= 1e-9) & (w < 10 * EPS_HI)], 10).tolist()))},
           "lambda_up": lambda_eff_exact(c, "up"), "lambda_dn": lambda_eff_exact(c, "dn"), "a0_singlet": a0_singlet(c)}
    comp, bfb = banks()
    out["bfb_bank_min_V4"] = float(np.min(bfb @ c)); out["competitor_bank_min_gap"] = float(np.min(comp @ c - VAL0 @ c))
    out["box_max"] = {"quartic": float(np.max(np.abs(c[deg4]))), "cubic": float(np.max(np.abs([c[i] for i, p in enumerate(ids) if DEG[p.split('::')[1]] == 3]))),
                      "mass": float(np.max(np.abs([c[i] for i, p in enumerate(ids) if DEG[p.split('::')[1]] == 2])))}
    if screen: out["subspace_screen"] = [f.search(c) for f in fits()]
    return out
