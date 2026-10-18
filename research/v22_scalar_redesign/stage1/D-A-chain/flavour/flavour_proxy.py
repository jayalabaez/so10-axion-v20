#!/usr/bin/env python3
"""D-A-chain / D2: cheap GUT-scale proxy flavour fit for SO(10) -> SM direct (one light SM doublet, a general mixture of
H10_u, H10_d^*, Sigma_u, Sigma_d^* [126bar (15,2,2)] and the 210 doublet).

Model at M_U (doublet-left convention of lib_r2c, matrices in GeV):
   M_d = H + F + G,   M_e = H - 3F + c_e G,   M_u = r (H + s F + c_u G),   M_D = r (H - 3 s F + c_D G),
   M_R = F * R   (R = c_R v_BL / (v alpha_Sigma_d c_126): one real scale; m_nu = - M_D M_R^-1 M_D^T, type I only)
 H = diag(h1,h2,h3) real (basis choice), F complex symmetric, r > 0, s complex (r, s free: the four doublet weights are
 independent at the SM-direct vacuum - checked structurally in vac/ at the LP points), G complex ANTISYMMETRIC.
 G = the X-allowed d=5 operator F F H10 Phi210 / Lambda (120-channel); with real Phi210 vevs (p, a, omega) and real
 Clebsches, c_e, c_u, c_D are REAL (minimal d=5 content: no F F Delta Phi210 terms).  Size bound:
   |G_ij| <= g_max (GeV);  g_max = c x |Phi|/Lambda x v x kappa ~ c x 1.7 GeV at M_U = 1e16 (|Phi| ~ 2.5 M_U, kappa ~ 1,
   Lambda = M_Pl,red) -> default g_max = 0.5 GeV <-> c <~ 0.3.
 Variant 'ren': G = 0 (renormalisable 10 + 126bar; reproduces the R2-C structure as a cross-check).
GUT-scale data: PDG-2024 inputs at M_Z (R2-C inputs_mz.json) run with the SM two-loop RGE (lib_r2c.run_sm, copied
unedited; kappa not used) and the one-loop gauge shift of the light states of the chosen D4 content + B63 above M_s.
Error model (stated): mass errors = relative M_Z errors (PDG/FLAG) (+) a theory floor f (default 1%, also 5%), CKM errors
as at M_Z, PMNS/dm^2 = NuFIT 6.0 (with SK) at low energy (running of the PMNS sector neglected, EST < few %).
chi2 = sum of 18 pulls (9 masses, 4 CKM, 2 dm^2, 3 angles).  NUM (local optimiser, multi-start; a minimum found is an
upper bound on the true chi2_min)."""
from __future__ import annotations
import math, json, sys, time
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L

MZ = L.MZ; V = L.VEV
CONTENTS = {
    # (light states (one-loop b-shift vector, mass)), M_U from unif_sm.py nominal two-loop solutions
    "U8362": ([(np.array([0.0, 8 / 3, 3 / 2]), 1.36e12), (np.array([1 / 15, 1.0, 5 / 3]), 2.04e5)], 1.71e17),
    "U6381": ([(np.array([2 / 5, 4.0, 5 / 2]), 1.49e11), (np.array([0.0, 0.0, 0.5]), 6.93e5)], 8.05e15),
    "SM": ([], 1.0e16),
    # D-A-chain nominal D4 point (unif_family_U8362.json): m(8,3,0) = 2.51e11, m(6,2,-1/6) = 1.99e9, M_U = 1.871e16
    "N8362": ([(np.array([0.0, 8 / 3, 3 / 2]), 2.51e11), (np.array([1 / 15, 1.0, 5 / 3]), 1.99e9)], 1.871e16),
}


def gut_targets(content="U6381", M_s=1e13, floor=0.01, nu="nufit60_sk"):
    light, MU = CONTENTS[content]
    d = L.data_set(nu=nu, floor=0.0)
    # initial Yukawas at MZ (doublet-left): Yd diagonal, Yu = CKM^T diag
    ck = L.INP["ckm_MZ"]
    Vc = L.umix(ck["s12"][0], ck["s23"][0], ck["s13"][0], ck["delta"][0])
    mu_ = np.array([d["m_u"][0], d["m_c"][0], d["m_t"][0]]); md_ = np.array([d["m_d"][0], d["m_s"][0], d["m_b"][0]])
    me_ = np.array([d["m_e"][0], d["m_mu"][0], d["m_tau"][0]])
    Yu = (Vc.T @ np.diag(mu_)) / V; Yd = np.diag(md_).astype(complex) / V; Ye = np.diag(me_).astype(complex) / V
    st = L.SMState(L.gauge_mz(), 0.26, Yu.astype(complex), Yd, Ye, np.zeros((3, 3), complex))
    thr = sorted(set([M_s] + [m for _, m in light if MZ < m < MU]))
    pts = [MZ] + thr + [MU]

    def db(mu):
        s = np.zeros(3)
        if mu > M_s:
            s += 28.0 / 3
        for b, m in light:
            if mu > m:
                s += b
        return s
    for a, b in zip(pts[:-1], pts[1:]):
        st = L.run_sm(st, a, b, db=db(math.sqrt(a * b)), rtol=1e-8)
    o = L.observables(st.Yu, st.Yd, st.Ye, np.diag([1e-12, 2e-12, 5e-11]).astype(complex))
    tg = {}
    for k in L.MASS_KEYS:
        c0, s0 = d[k]
        rel = math.sqrt((s0 / c0) ** 2 + floor ** 2)
        tg[k] = (o[k], o[k] * rel)
    for k in L.CKM_KEYS:
        tg[k] = (abs(o[k]) if k == "delta" else o[k], d[k][1])
    for k in L.NU_KEYS:
        tg[k] = d[k]
    return tg, {"M_U": MU, "g_MU": st.g.tolist(), "yt_MU": float(o["m_t"] / V), "ms_md_MU": o["m_s"] / o["m_d"],
                "mb_mtau_MU": o["m_b"] / o["m_tau"], "content": content}


NP_REN = 3 + 3 + 9 + 1 + 2 + 1       # d(3), e(3), W generator (9), log r, s(2), log R   ("pinned" parametrisation)
NP_D5 = NP_REN + 6 + 3               # + G (3 complex), c_e, c_u, c_D (real)
IR = 15                              # index of log r; log R at IR + 3 = 18
from scipy.linalg import expm


def _herm9(v):
    Hm = np.zeros((3, 3), complex)
    Hm[0, 0], Hm[1, 1], Hm[2, 2] = v[0], v[1], v[2]
    Hm[0, 1] = v[3] + 1j * v[4]; Hm[0, 2] = v[5] + 1j * v[6]; Hm[1, 2] = v[7] + 1j * v[8]
    Hm[1, 0], Hm[2, 0], Hm[2, 1] = np.conj(Hm[0, 1]), np.conj(Hm[0, 2]), np.conj(Hm[1, 2])
    return Hm


def unpack(x, mode):
    """S_d = H + F = diag(d) (basis choice), H - 3F = W^T diag(e) W (Takagi, W = exp(i h)); H, F solved exactly:
    H = (3 S_d + S_e)/4, F = (S_d - S_e)/4.  With G = 0 the d- and e-masses are |d|, |e| exactly ('pinned')."""
    d = x[0:3]; e = x[3:6]; W = expm(1j * _herm9(x[6:15]))
    Sd = np.diag(d).astype(complex); Se = W.T @ np.diag(e) @ W
    H = (3 * Sd + Se) / 4; F = (Sd - Se) / 4
    r = math.exp(min(max(x[15], -30.0), 30.0)); s = x[16] + 1j * x[17]; lR = min(max(x[18], -80.0), 80.0); k = 19
    G = np.zeros((3, 3), complex); ce = cu = cD = 0.0
    if mode == "d5":
        g = x[k:k + 6]; G[0, 1], G[0, 2], G[1, 2] = g[0] + 1j * g[1], g[2] + 1j * g[3], g[4] + 1j * g[5]
        G = G - G.T; ce, cu, cD = x[k + 6:k + 9]
    return H, F, r, s, lR, G, ce, cu, cD


def model(x, mode):
    H, F, r, s, lR, G, ce, cu, cD = unpack(x, mode)
    Md = H + F + G; Me = H - 3 * F + ce * G; Mu = r * (H + s * F + cu * G); MD = r * (H - 3 * s * F + cD * G)
    try:
        Finv = np.linalg.inv(F)
    except np.linalg.LinAlgError:
        return None
    if not np.all(np.isfinite(Finv)):
        return None
    mnu = -(MD @ Finv @ MD.T) * math.exp(-lR)          # GeV
    return Mu, Md, Me, mnu, (H, F, r, s, lR, G, ce, cu, cD)


def residuals(x, mode, tg, gmax):
    m = model(x, mode)
    if m is None:
        return np.full(19, 1e3)
    Mu, Md, Me, mnu, par = m
    o = L.observables(Mu / V, Md / V, Me / V, mnu)
    res = []
    for k in L.ALL_KEYS:
        c, s = tg[k]
        if k in L.MASS_KEYS:
            res.append(math.log(max(o[k], 1e-300) / c) * c / s)
        elif k == "delta":
            res.append(((abs(o[k]) - c + math.pi) % (2 * math.pi) - math.pi) / s)
        else:
            res.append((o[k] - c) / s)
    # soft size bound on G (penalty only beyond gmax)
    G = par[5]
    over = max(0.0, float(np.max(np.abs(G))) - gmax) if mode == "d5" else 0.0
    res.append(over / (0.05 * gmax))
    return np.array(res)


def start(rng, mode, tg):
    x = np.zeros(NP_D5 if mode == "d5" else NP_REN)
    x[0:3] = [tg["m_d"][0], tg["m_s"][0], tg["m_b"][0]]
    x[3:6] = [tg["m_e"][0], tg["m_mu"][0], tg["m_tau"][0]]
    x[6:15] = rng.normal(0, 1.0, 9) * rng.choice([0.1, 0.5, 1.5])
    x[15] = math.log(tg["m_t"][0] / tg["m_b"][0]) + rng.normal(0, 1.0)
    x[16:18] = rng.normal(0, 1.0, 2)
    x[18] = math.log(10 ** rng.uniform(11, 16))
    if mode == "d5":
        x[19:25] = rng.normal(0, 1, 6) * 0.02
        x[25:28] = rng.normal(0, 1.5, 3)
    return x


def fit(tg, mode, nstart=200, seed=1, gmax=0.5, tlimit=1500, lRmin=None):
    """mode 'ren' / 'd5'; lRmin: lower bound on ln R (M_R = R F), i.e. on v_BL (SM-direct: v_BL ~ M_U)."""
    rng = np.random.default_rng(seed); best = None; t0 = time.time(); hist = []
    for i in range(nstart):
        x0 = start(rng, mode, tg)
        lb = np.full(len(x0), -np.inf); ub = np.full(len(x0), np.inf)
        if lRmin is not None:
            lb[18] = lRmin; x0[18] = max(x0[18], lRmin + abs(rng.normal(0, 1)))
        try:
            r = least_squares(residuals, x0, args=(mode, tg, gmax), method="trf", max_nfev=4000, x_scale="jac", bounds=(lb, ub))
        except Exception:
            continue
        chi2 = float(np.sum(r.fun ** 2))
        hist.append(chi2)
        if best is None or chi2 < best[0]:
            best = (chi2, r.x.copy())
        if time.time() - t0 > tlimit:
            break
    return best, hist


def report(x, mode, tg, gmax):
    Mu, Md, Me, mnu, par = model(x, mode)
    o = L.observables(Mu / V, Md / V, Me / V, mnu)
    res = residuals(x, mode, tg, gmax)
    pulls = {k: float(v) for k, v in zip(L.ALL_KEYS, res[:18])}
    H, F, r, s, lR, G, ce, cu, cD = par
    R = math.exp(lR)
    Hd = H
    return {"chi2": float(np.sum(res[:18] ** 2)), "penalty": float(res[18] ** 2), "pulls": pulls,
            "obs": {k: (float(o[k]) if not isinstance(o[k], (list, np.ndarray)) else None) for k in L.ALL_KEYS},
            "m_nu_eV": o["m_nu_eV"], "r": r, "s": [s.real, s.imag], "R_scale_MR_over_F": R,
            "MR_eigs_GeV": sorted(np.abs(np.linalg.eigvals(F * R)).tolist()),
            "F_eigs_GeV": sorted(np.abs(np.linalg.svd(F, compute_uv=False)).tolist()),
            "H_svals_GeV": sorted(np.linalg.svd(H, compute_uv=False).tolist()), "G_max_GeV": float(np.max(np.abs(G))), "c_e_u_D": [ce, cu, cD],
            "ms_md_model_MU": float(o["m_s"] / o["m_d"])}


if __name__ == "__main__":
    content = sys.argv[1] if len(sys.argv) > 1 else "U6381"
    floor = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
    nstart = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    gmax = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    tg, info = gut_targets(content, floor=floor)
    print("GUT targets:", json.dumps({k: [float(v[0]), float(v[1])] for k, v in tg.items()}), json.dumps(info), flush=True)
    out = {"content": content, "floor": floor, "gmax": gmax, "targets": {k: list(map(float, v)) for k, v in tg.items()}, "info": info}
    lRmin = math.log(float(sys.argv[5])) if len(sys.argv) > 5 else None
    modes = [("ren", None), ("d5", None)] + ([("d5", lRmin)] if lRmin is not None else [])
    for mode, lrm in modes:
        best, hist = fit(tg, mode, nstart=nstart, gmax=gmax, lRmin=lrm)
        rep = report(best[1], mode, tg, gmax)
        mode = mode if lrm is None else mode + "_Rmin"
        out[mode] = {"best": rep, "x": best[1].tolist(), "chi2_hist_sorted": sorted(hist)[:20], "n_starts": len(hist)}
        print(f"[{content} floor={floor} mode={mode}] chi2_min = {rep['chi2']:.3f} (penalty {rep['penalty']:.2e}) "
              f"starts={len(hist)}; pulls>2: { {k: round(v, 2) for k, v in rep['pulls'].items() if abs(v) > 2} }; "
              f"ms/md={rep['ms_md_model_MU']:.2f}; G_max={rep['G_max_GeV']:.3g} GeV; MR={['%.2e' % m for m in rep['MR_eigs_GeV']]}", flush=True)
    json.dump(out, open(f"flavour_proxy_{content}_f{floor:g}_g{gmax:g}.json", "w"), indent=1, default=float)
