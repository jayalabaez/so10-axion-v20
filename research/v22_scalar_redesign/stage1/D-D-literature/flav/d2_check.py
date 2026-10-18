#!/usr/bin/env python3
"""Independent scalar re-evaluation of a D2 best-fit point (d2c_<label>.json): rebuild the GUT-scale matrices from x
with explicit formulas (no batching), recompute every observable with lib_r2c.observables, the chi2, and the physical
sizes: d=5 coefficient c5 = max(|A_1|,|A_15|)/(kappa c_d10), the allowed (c_d10, c_d126, sigma) window, Yukawa
perturbativity, M_R spectrum at a chosen sigma, light neutrino masses, m_s/m_d.  Usage: d2_check.py <label> [sigma]"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lib_r2c as L  # noqa: E402

V = L.VEV


def umix_full(x):
    th12, th13, th23, d, a1, a2, b1, b2, b3 = x[:9]
    U = L.umix(math.sin(th12), math.sin(th23), math.sin(th13), d)
    # lib umix takes sines; reproduce umix_b (angles) exactly
    s12, c12, s13, c13, s23, c23 = math.sin(th12), math.cos(th12), math.sin(th13), math.cos(th13), math.sin(th23), math.cos(th23)
    e = np.exp(1j * d)
    U = np.array([[c12 * c13, s12 * c13, s13 * np.conj(e)],
                  [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                  [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])
    P1 = np.diag(np.exp(1j * np.array([a1, a2, 0.0])))
    P2 = np.diag(np.exp(1j * np.array([b1, b2, b3])))
    return P1 @ U @ P2


def main():
    label = sys.argv[1]
    sig = float(sys.argv[2]) if len(sys.argv) > 2 else None
    d = json.load(open(HERE / f"d2c_{label}.json"))
    o = d["opts"]
    T = np.array([d["targets"][k] for k in L.ALL_KEYS]); S = np.array([d["errors"][k] for k in L.ALL_KEYS])
    rec = d.get("with_d5") or d["renorm_best"]
    x = np.array(rec["x"]) if "x" in rec else None
    if x is None:
        print("no x stored"); return
    sd0, se0 = T[3:6] / V, T[6:9] / V
    W = umix_full(x)
    sd = sd0 * np.exp(x[12:15]); se = se0 * np.exp(x[15:18])
    Sd = np.diag(sd).astype(complex); Se = W @ np.diag(se) @ W.T
    H = (3 * Sd + Se) / 4; F = (Sd - Se) / 4
    r = 10 ** x[9]; s = 10 ** x[10] * np.exp(1j * x[11])
    A = np.zeros((3, 3), complex); rho = eps = 0.0
    useA = bool(o.get("useA", 1)) and len(x) >= 26
    if useA:
        a = x[18:24] * 1e-4
        for k, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
            A[i, j] = a[2 * k] + 1j * a[2 * k + 1]; A[j, i] = -A[i, j]
        rho, eps = x[24], x[25]
        if o.get("eps_fixed") is not None:
            eps = float(o["eps_fixed"])
    eta1 = float(o.get("eta1", 1.0))
    den = 1 + rho
    ke, ku, kD = (1 - 3 * rho) / den, (eta1 + eps * rho) / den, (eta1 - 3 * eps * rho) / den
    Yd = Sd + A; Ye = Se + ke * A; Yu = r * (H + s * F + ku * A); Yn = r * (H - 3 * s * F + kD * A)
    m1 = -Yn @ np.linalg.solve(F, Yn.T)
    tII = None
    if o.get("typeII"):
        i0 = 18 + (8 if useA else 0)
        tII = 10 ** x[i0] * np.exp(1j * x[i0 + 1])
        m1 = m1 + tII * np.linalg.norm(m1) / np.linalg.norm(F) * F
    ob = L.observables(Yu, Yd, Ye, m1 / np.abs(m1).max())
    mn = np.array(ob["m_nu_eV"]) * 1e-9
    a21, a31 = mn[1] ** 2 - mn[0] ** 2, mn[2] ** 2 - mn[0] ** 2
    i21, i31 = L.ALL_KEYS.index("dm21"), L.ALL_KEYS.index("dm31")
    lam = (a21 * T[i21] / S[i21] ** 2 + a31 * T[i31] / S[i31] ** 2) / (a21 ** 2 / S[i21] ** 2 + a31 ** 2 / S[i31] ** 2)
    obs = np.array([ob[k] for k in L.ALL_KEYS], float)
    obs[i21] = lam * a21; obs[i31] = lam * a31
    pulls = {}
    for i, k in enumerate(L.ALL_KEYS):
        if k in L.MASS_KEYS:
            pulls[k] = math.log(obs[i] / T[i]) * T[i] / S[i]
        elif k == "delta":
            pulls[k] = ((abs(obs[i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        else:
            pulls[k] = (obs[i] - T[i]) / S[i]
    chi2 = sum(v * v for v in pulls.values())
    rho_nu = math.sqrt(lam) * 1e-9 / np.abs(m1).max()
    # physical windows
    rs2 = abs(r * s) ** 2
    cd10_min = np.abs(H).max() * L.Y10_ACT / 1.5
    cd126_min = max(np.abs(F).max() * L.Y126_ACT / 1.5, np.abs(F).max() * L.C_R / math.sqrt(4 * math.pi))
    kfac = L.C_R * rho_nu / V ** 2
    A1 = np.abs(A).max() / max(abs(1 + rho), 1e-12); Amax = max(A1, abs(rho) * A1)
    out = {"label": label, "chi2_recomputed": chi2, "chi2_stored": rec.get("chi2_obs"), "pulls": {k: round(v, 3) for k, v in pulls.items()},
           "r": r, "s": [s.real, s.imag], "rho": rho, "eps": eps, "eta1": eta1,
           "kappa_e,u,D": [ke, ku, kD],
           "masses_MU_GeV": {k: float(obs[i]) for i, k in enumerate(L.ALL_KEYS) if k in L.MASS_KEYS},
           "ms_over_md": float(obs[4] / obs[3]), "A_max_v_units": float(np.abs(A).max()),
           "A_in_down_sector_GeV": float(np.abs(A).max() * V),
           "A_in_up_sector_GeV": float(np.abs(ku * A).max() * r * V),
           "F_max_GeV": float(np.abs(F).max() * V), "H_max_GeV": float(np.abs(H).max() * V),
           "rho_nu_GeV": rho_nu, "m_nu_eV": (mn * math.sqrt(lam)).tolist(), "typeII_t": None if tII is None else [tII.real, tII.imag]}
    windows = []
    for sg in ([sig] if sig else []) + [o["sigma_lo"], 1e13, 3e13, o["sigma_hi"]]:
        c126 = sg * kfac
        if c126 < cd126_min:
            windows.append({"sigma": sg, "ok": False, "why": "Y126 perturbativity (c_d126 too small)"}); continue
        rem = 1 - (1 + rs2) * c126 ** 2
        if rem <= 0:
            windows.append({"sigma": sg, "ok": False, "why": "composition normalisation"}); continue
        c10max = math.sqrt(rem / (1 + r ** 2))
        if c10max < cd10_min:
            windows.append({"sigma": sg, "ok": False, "why": "Y10 perturbativity"}); continue
        c5 = Amax / (o["kappa_phi"] * c10max) if Amax > 0 else 0.0
        Y126 = F / c126
        MR = L.C_R * sg * Y126
        mR = np.sort(np.linalg.svd(MR, compute_uv=False))
        windows.append({"sigma": sg, "ok": True, "c_d126": c126, "c_d10_max": c10max, "c5_needed(kappa)": c5,
                        "max|Y126_act|": float(np.abs(Y126).max() * L.Y126_ACT),
                        "max|Y10_act|(c10max)": float(np.abs(H).max() / c10max * L.Y10_ACT), "M_R_GeV": mR.tolist()})
    out["sigma_windows"] = windows
    out["sigma_range_allowed"] = [cd126_min / kfac, math.sqrt(max(0.0, 1 - (1 + r ** 2) * cd10_min ** 2) / (1 + rs2)) / kfac]
    print(json.dumps(out, indent=1, default=str))
    (HERE / f"d2check_{label}.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
