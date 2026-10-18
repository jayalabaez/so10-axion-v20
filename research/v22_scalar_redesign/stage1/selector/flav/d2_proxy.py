#!/usr/bin/env python3
"""D-D-literature, criterion D2: GUT-scale proxy fit for designs in which SU(2)_R x SU(4) break at M_U (one light SM
doublet with independent up/down 10 / 126bar compositions).

Yukawa structure at M_U (doublet-LEFT, units of v = 174.1 GeV; H real-diagonal basis):
    Yd = H + F + A,  Ye = H - 3F + k_e A,  Yu = r (H + s F + k_u A),  Yn = r (H - 3 s F + k_D A)
    H = c_d10 Y10, F = c_d126 Y126 (renormalisable, X-allowed: F.F.H10, F.F.Delta);
    A = antisymmetric, from the X-allowed d=5 operator F F H10 Phi210 / Lambda in its (16 16)_120 (10 210)_120 channel
        (Phi210 SM-singlet vevs p (1,1,1), a (15,1,1), omega (15,1,3)): A = A_1 + A_15, A_15 = rho A_1 (rho real),
        lepton Clebsch -3 for the (15,2,2)_120 part, omega flips the sign of the (15,2,2) part between up and down
        (eps real):  k_e = (1 - 3 rho)/(1 + rho), k_u = (1 + eps rho)/(1 + rho), k_D = (1 - 3 eps rho)/(1 + rho).
        The up/down ratio of A is r because the same H10 doublets carry it.
    Size bound (EST Clebsch 1): max_ij |A_1|, |A_15| <= c_5 kappa_Phi c_d10, kappa_Phi = |Phi|/M_Pl,red, c_5 <= 1.
Neutrinos: type I, m_nu = -rho_nu Yn F^-1 Yn^T with rho_nu = v^2 c_d126/(C_R sigma) (M_R = C_R sigma Y126, C_R = 2 sqrt6,
    R2-C normalisation); optional type II  m_nu += t F (free complex t) for the variant with a light Delta_L.
Composition normalisation (R2-C corrected): (1 + r^2) c_d10^2 + (1 + |r s|^2) c_d126^2 <= 1; perturbativity
    |Y10_act| = |H|/c_d10 /(2 sqrt2) <= 1.5, |Y126_act| = |F|/c_d126 sqrt3/4 <= 1.5, Majorana f = C_R |Y126| <= sqrt(4 pi).
    Hence sigma_max = v^2 c_d126max / (C_R rho_nu) with c_d126max from the normalisation at the smallest allowed c_d10.
Observables / errors: R2-C error model (PDG-2024 masses at M_Z, 4-loop QCD, 1 % theory floor; PDG CKM; NuFIT 6.0 NO with
    SK), run to M_U with the SM two-loop RGEs of lib_r2c.py (copied from R2-C v2) including the B63 S-sector shift above
    M_S = 1e13 and the light octets of the design (one-loop gauge shifts); relative mass errors and angle errors kept.
Fit: 18 observables, chi2 + penalty residuals (bounds and sigma window), least squares (TRF) from many seeds
    (random unitary W -> H, F from the pinned R2-C construction) + basin hopping.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lib_r2c as L  # noqa: E402

V = L.VEV
C_R = L.C_R
Y10_ACT, Y126_ACT = L.Y10_ACT, L.Y126_ACT
KEYS = L.ALL_KEYS


# ------------------------------------------------------------------------------------------------------------------
# targets at M_U
# ------------------------------------------------------------------------------------------------------------------
def db_vector(mu, light):
    db = np.zeros(3)
    if mu > L.M_S:
        db += L.B63_SM_SHIFT
    for m, d in light:
        if mu > m:
            db += np.array(d)
    return db


def run_up(data, MU, light):
    import model_r2c as MR
    Yu, Yd, Ye, kap = MR.data_matrices(data)
    st = L.SMState(L.gauge_mz(), 0.26, Yu, Yd, Ye, kap)
    pts = sorted(set([L.M_S] + [m for m, _ in light]))
    mu = L.MZ
    for p in pts + [MU]:
        if p <= mu or p > MU:
            continue
        st = L.run_sm(st, mu, p, db=db_vector(math.sqrt(mu * p), light))
        mu = p
    o = L.observables(st.Yu, st.Yd, st.Ye, st.kappa * V ** 2)
    return o, st


def make_targets(MU, light, nu="nufit60_sk", floor=0.01):
    data = L.data_set(nu=nu, floor=floor)
    o, st = run_up(data, MU, light)
    T = np.zeros(18); S = np.zeros(18)
    for i, k in enumerate(KEYS):
        c, s = data[k]
        if k in L.MASS_KEYS:
            T[i] = o[k]; S[i] = s / c * T[i]
        elif k == "delta":
            T[i] = abs(o[k]); S[i] = s
        elif k in ("s12", "s23", "s13"):
            T[i] = o[k]; S[i] = s / c * T[i]
        else:                       # neutrino: low-energy values (angles and dm^2 ratios barely run: EST)
            T[i] = c; S[i] = s
    return T, S, {"g_MU": st.g.tolist(), "MU": MU, "obs_MU": {k: float(o[k]) for k in KEYS}}


# ------------------------------------------------------------------------------------------------------------------
# parametrisation
# ------------------------------------------------------------------------------------------------------------------
NB = 3 + 12 + 6 + 2 + 1 + 2      # H(3, log) F(12) A(6) rho,eps r(log) s(|.|log, arg)


def unpack(x, typeII):
    h = np.exp(x[0:3])
    H = np.diag(h).astype(complex)
    f = x[3:15]
    Fm = np.zeros((3, 3), complex)
    iu = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]
    for k, (i, j) in enumerate(iu):
        Fm[i, j] = Fm[j, i] = (f[2 * k] + 1j * f[2 * k + 1]) * 1e-3
    a = x[15:21] * 1e-4
    A = np.zeros((3, 3), complex)
    for k, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
        A[i, j] = a[2 * k] + 1j * a[2 * k + 1]
        A[j, i] = -A[i, j]
    rho, eps = x[21], x[22]
    r = 10.0 ** x[23]
    s = 10.0 ** x[24] * np.exp(1j * x[25])
    t = None
    if typeII:
        t = 10.0 ** x[26] * np.exp(1j * x[27])
    return H, Fm, A, rho, eps, r, s, t


def model(x, typeII=False, use_A=True):
    H, Fm, A, rho, eps, r, s, t = unpack(x, typeII)
    if not use_A:
        A = A * 0
    den = 1 + rho
    ke, ku, kD = (1 - 3 * rho) / den, (1 + eps * rho) / den, (1 - 3 * eps * rho) / den
    Yd = H + Fm + A
    Ye = H - 3 * Fm + ke * A
    Yu = r * (H + s * Fm + ku * A)
    Yn = r * (H - 3 * s * Fm + kD * A)
    return dict(H=H, F=Fm, A=A, rho=rho, eps=eps, r=r, s=s, t=t, Yd=Yd, Ye=Ye, Yu=Yu, Yn=Yn)


def observables_and_scale(M, T, S, typeII=False):
    Yu, Yd, Ye, Yn, Fm = M["Yu"], M["Yd"], M["Ye"], M["Yn"], M["F"]
    try:
        m1 = -Yn @ np.linalg.solve(Fm, Yn.T)
    except np.linalg.LinAlgError:
        return None
    if typeII:
        m1 = m1 + M["t"] * np.linalg.norm(m1) / max(np.linalg.norm(Fm), 1e-300) * Fm
    sc = np.abs(m1).max()
    if not np.isfinite(sc) or sc <= 0:
        return None
    m1n = m1 / sc
    o = L.observables(Yu, Yd, Ye, m1n)        # m_nu in arbitrary units
    mn = np.array(o["m_nu_eV"]) * 1e-9        # (units of the normalised matrix)
    a21 = mn[1] ** 2 - mn[0] ** 2; a31 = mn[2] ** 2 - mn[0] ** 2
    i21, i31 = KEYS.index("dm21"), KEYS.index("dm31")
    # dm^2 in eV^2 = lam * a (lam fitted analytically); here o['dm21'] = a*1e18
    num = a21 * T[i21] / S[i21] ** 2 + a31 * T[i31] / S[i31] ** 2
    den = a21 ** 2 / S[i21] ** 2 + a31 ** 2 / S[i31] ** 2
    lam = num / den if den > 0 else 1e-300
    lam = max(lam, 1e-300)
    obs = np.array([o[k] for k in KEYS], float)
    obs[KEYS.index("dm21")] = lam * a21
    obs[KEYS.index("dm31")] = lam * a31
    # physical scale: m_nu[eV] = sqrt(lam) * eigen(m1n) -> rho_nu[GeV] = sqrt(lam) * 1e-9 / sc
    rho_nu = math.sqrt(lam) * 1e-9 / sc
    return obs, rho_nu, o, lam


def residuals(obs, T, S):
    R = np.empty(18)
    for i, k in enumerate(KEYS):
        if k in L.MASS_KEYS:
            R[i] = math.log(max(obs[i], 1e-300) / T[i]) * T[i] / S[i]
        elif k == "delta":
            R[i] = ((abs(obs[i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        else:
            R[i] = (obs[i] - T[i]) / S[i]
    return R


def derived(M, rho_nu, opts):
    """Joint feasibility of the composition normalisation, perturbativity, the d=5 bound and the sigma window."""
    kappa_phi, c5max, sig_lo, sig_hi = opts["kappa_phi"], opts["c5_max"], opts["sigma_lo"], opts["sigma_hi"]
    r, s = M["r"], M["s"]
    Hmax = np.abs(M["H"]).max(); Fmax = np.abs(M["F"]).max()
    rho = M["rho"]
    A1 = np.abs(M["A"]).max() / max(abs(1 + rho), 1e-12)
    Amax = max(A1, abs(rho) * A1) if opts["use_A"] else 0.0
    rs2 = abs(r * s) ** 2
    cd10_min = Hmax * Y10_ACT / 1.5
    cd126_min = max(Fmax * Y126_ACT / 1.5, Fmax * C_R / math.sqrt(4 * math.pi))
    kfac = C_R * rho_nu / V ** 2 if rho_nu > 0 else float("inf")      # c_d126 = kfac * sigma
    c126_lo = max(cd126_min, sig_lo * kfac)
    c126_hi = sig_hi * kfac
    rem = 1 - (1 + rs2) * c126_lo ** 2
    c10_allow = math.sqrt(rem / (1 + r ** 2)) if rem > 0 else 0.0
    c5_needed = Amax / (kappa_phi * c10_allow) if (c10_allow > 0 and Amax > 0) else (0.0 if Amax == 0 else float("inf"))
    c10_req = max(cd10_min, Amax / (kappa_phi * c5max) if Amax > 0 else 0.0)
    rem2 = 1 - (1 + r ** 2) * c10_req ** 2
    c126_max = math.sqrt(rem2 / (1 + rs2)) if rem2 > 0 else 0.0
    sig_max = c126_max / kfac if kfac > 0 else 0.0
    sig_min = cd126_min / kfac if kfac > 0 else float("inf")
    return dict(cd10_min=cd10_min, cd126_min=cd126_min, c126_lo=c126_lo, c126_hi=c126_hi, c10_allow=c10_allow,
                c10_req=c10_req, c126_max=c126_max, sigma_min=sig_min, sigma_max=sig_max, Amax=Amax,
                c5_needed=c5_needed)


def full_residual(x, T, S, opts):
    M = model(x, opts["typeII"], opts["use_A"])
    out = observables_and_scale(M, T, S, opts["typeII"])
    if out is None:
        return np.full(18 + 4, 1e3)
    obs, rho_nu, o, lam = out
    R = residuals(obs, T, S)
    D = derived(M, rho_nu, opts)
    pen = []
    pen.append(max(0.0, math.log(max(D["c5_needed"], 1e-300) / opts["c5_max"])) / 0.05 if D["Amax"] > 0 else 0.0)
    pen.append(max(0.0, math.log(max(D["c126_lo"], 1e-300) / max(D["c126_hi"], 1e-300))) / 0.05)   # sigma window
    pen.append(max(0.0, math.log(max(D["cd10_min"], 1e-300) / max(D["c10_allow"], 1e-300))) / 0.05)  # normalisation
    pen.append(0.0)
    return np.concatenate([np.where(np.isfinite(R), R, 1e3), np.array(pen)])


def seed(rng, T, opts):
    sd = T[3:6] / V; se = T[6:9] / V
    Z = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    Q, Rq = np.linalg.qr(Z)
    W = Q * (np.diag(Rq) / abs(np.diag(Rq)))
    # bias towards small angles (charged-lepton/down alignment as in the fitted basins)
    if rng.random() < 0.7:
        ang = rng.normal(scale=0.3, size=3)
        W = L.umix(math.sin(ang[0]), math.sin(ang[1]), math.sin(ang[2]) * 0.3, rng.uniform(-math.pi, math.pi))
        W = W * np.exp(1j * rng.uniform(-math.pi, math.pi, 3))[None, :]
    Yd = np.diag(sd).astype(complex)
    Ye = W @ np.diag(se) @ W.T
    Hm = (3 * Yd + Ye) / 4; Fm = (Yd - Ye) / 4
    # Takagi-diagonalise H and rotate F
    m, U = L.takagi(Hm)
    Fr = U.T @ Fm @ U
    x = np.zeros(NB + (2 if opts["typeII"] else 0))
    x[0:3] = np.log(np.maximum(m, 1e-9))
    iu = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]
    for k, (i, j) in enumerate(iu):
        x[3 + 2 * k] = Fr[i, j].real * 1e3; x[4 + 2 * k] = Fr[i, j].imag * 1e3
    x[15:21] = rng.normal(scale=0.3, size=6) if opts["use_A"] else 0.0
    x[21] = rng.normal(scale=0.7); x[22] = rng.choice([-1.0, 1.0]) * rng.uniform(0.2, 2)
    x[23] = math.log10(rng.uniform(40, 90))
    x[24] = math.log10(rng.uniform(0.1, 1.0)); x[25] = rng.normal(scale=0.3)
    if opts["typeII"]:
        x[26] = rng.uniform(-1, 1); x[27] = rng.uniform(-math.pi, math.pi)
    return x


def fit(T, S, opts, nseed=60, seed0=1, hops=6, verbose=True):
    rng = np.random.default_rng(seed0)
    best = None
    t0 = time.time()
    for k in range(nseed):
        x0 = seed(rng, T, opts)
        try:
            res = least_squares(full_residual, x0, args=(T, S, opts), method="trf", max_nfev=4000, x_scale="jac")
        except Exception:
            continue
        xb, cb = res.x, float(np.sum(res.fun ** 2))
        for h in range(hops):
            xp = xb + rng.normal(scale=0.05, size=xb.size) * (1 + np.abs(xb))
            try:
                r2 = least_squares(full_residual, xp, args=(T, S, opts), method="trf", max_nfev=2000, x_scale="jac")
            except Exception:
                continue
            c2 = float(np.sum(r2.fun ** 2))
            if c2 < cb:
                xb, cb = r2.x, c2
        if best is None or cb < best[1]:
            best = (xb, cb)
            if verbose:
                print(f"   seed {k}: total {cb:.3f}  ({time.time() - t0:.0f}s)", flush=True)
    return best


def report(x, T, S, opts):
    M = model(x, opts["typeII"], opts["use_A"])
    obs, rho_nu, o, lam = observables_and_scale(M, T, S, opts["typeII"])
    R = residuals(obs, T, S)
    D = derived(M, rho_nu, opts)
    pen = full_residual(x, T, S, opts)[18:]
    mn = np.array(o["m_nu_eV"]) * 1e-9 * math.sqrt(lam)
    return {"chi2_obs": float(np.sum(R ** 2)), "penalty2": float(np.sum(pen ** 2)),
            "pulls": {k: float(v) for k, v in zip(KEYS, R)}, "n_pulls_gt3": int(np.sum(np.abs(R) > 3)),
            "r": M["r"], "s": [M["s"].real, M["s"].imag], "rho": M["rho"], "eps": M["eps"],
            "H_diag": np.real(np.diag(M["H"])).tolist(), "F_abs_max": float(np.abs(M["F"]).max()),
            "A_abs_max": float(np.abs(M["A"]).max()), "derived": D, "rho_nu_GeV": rho_nu,
            "m_nu_eV": mn.tolist(), "sin2_th23": float(obs[KEYS.index("sin2_th23")]),
            "ms_over_md_MU": float(obs[4] / obs[3]), "target_ms_over_md_MU": float(T[4] / T[3])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--MU", type=float, default=1.28e16)
    ap.add_argument("--light", default="BOP")          # BOP: (8,1,0)@1e3 + (8,3,0)@1.7e9 ; none
    ap.add_argument("--useA", type=int, default=1)
    ap.add_argument("--typeII", type=int, default=0)
    ap.add_argument("--kappa", type=float, default=0.01)
    ap.add_argument("--c5max", type=float, default=1.0)
    ap.add_argument("--siglo", type=float, default=1e9)
    ap.add_argument("--sighi", type=float, default=1e17)
    ap.add_argument("--nseed", type=int, default=60)
    ap.add_argument("--hops", type=int, default=6)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--floor", type=float, default=0.01)
    a = ap.parse_args()
    light = {"BOP": [(1e3, (0.0, 0.0, 0.5)), (1.7e9, (0.0, 8 / 3, 1.5))], "none": []}[a.light]
    T, S, info = make_targets(a.MU, light, floor=a.floor)
    opts = dict(typeII=bool(a.typeII), use_A=bool(a.useA), kappa_phi=a.kappa, c5_max=a.c5max, sigma_lo=a.siglo,
                sigma_hi=a.sighi)
    print("label", a.label, "opts", opts, "MU", a.MU, "light", a.light, flush=True)
    print("targets at M_U:", {k: float(v) for k, v in zip(KEYS, T)}, flush=True)
    best = fit(T, S, opts, nseed=a.nseed, seed0=a.seed0, hops=a.hops)
    rep = report(best[0], T, S, opts)
    rep.update({"label": a.label, "opts": opts, "MU": a.MU, "light": a.light, "total": best[1], "x": best[0].tolist(),
                "targets": {k: float(v) for k, v in zip(KEYS, T)}, "errors": {k: float(v) for k, v in zip(KEYS, S)},
                "info": info})
    print(json.dumps({k: v for k, v in rep.items() if k not in ("x", "targets", "errors", "info")}, indent=1, default=str))
    (HERE / f"d2_{a.label}.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
