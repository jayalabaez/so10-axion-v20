#!/usr/bin/env python3
"""SKEPTIC D2: independent re-evaluation of the designer's L2 best-fit points (flav/d2c_L2_A_c0.1.json, c0.3, L3p_A).
Only the parametrisation (x -> H, F, A, r, s, rho, eps) is taken from the designer's model definition (it IS the
model); diagonalisation (SVD), CKM/PMNS angle extraction (PDG, Jarlskog for delta), Takagi-free neutrino masses
(singular values of m_nu), the Delta m^2 scale fit and the chi2 are re-implemented here.  Both left-handed
conventions (M M^dagger and M^dagger M) are evaluated: the d=5 term is antisymmetric, so they differ at fixed x."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FLAV = HERE.parent / "flav"
V = 174.1
MK = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"]
CK = ["s12", "s23", "s13", "delta"]
NK = ["sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]
KEYS = MK + CK + NK


def pdg_angles(U):
    s13 = abs(U[0, 2])
    c13 = math.sqrt(max(1 - s13 ** 2, 0))
    s12 = abs(U[0, 1]) / c13
    s23 = abs(U[1, 2]) / c13
    c12, c23 = math.sqrt(1 - s12 ** 2), math.sqrt(1 - s23 ** 2)
    Jcp = np.imag(U[0, 1] * U[1, 2] * np.conj(U[0, 2]) * np.conj(U[1, 1]))
    den = c12 * c23 * c13 ** 2 * s12 * s23 * s13
    sd = max(-1.0, min(1.0, Jcp / den))
    # cos delta from |U_31|^2 = s12^2 s23^2 + c12^2 c23^2 s13^2 - 2 s12 s23 c12 c23 s13 cos d
    cd = (s12 ** 2 * s23 ** 2 + c12 ** 2 * c23 ** 2 * s13 ** 2 - abs(U[2, 0]) ** 2) / (2 * s12 * s23 * c12 * c23 * s13)
    cd = max(-1.0, min(1.0, cd))
    return s12, s23, s13, math.atan2(sd, cd)


def left(M, conv):
    MM = M @ M.conj().T if conv == "MMdag" else M.conj().T @ M
    w, E = np.linalg.eigh(MM)
    return np.sqrt(np.clip(w, 0, None)), E


def umix(x):
    th12, th13, th23, d, a1, a2, b1, b2, b3 = x[:9]
    s12, c12, s13, c13, s23, c23 = math.sin(th12), math.cos(th12), math.sin(th13), math.cos(th13), math.sin(th23), math.cos(th23)
    e = np.exp(1j * d)
    U = np.array([[c12 * c13, s12 * c13, s13 * np.conj(e)],
                  [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                  [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])
    return np.diag(np.exp(1j * np.array([a1, a2, 0.0]))) @ U @ np.diag(np.exp(1j * np.array([b1, b2, b3])))


def evaluate(label, conv):
    d = json.load(open(FLAV / f"d2c_{label}.json"))
    o = d["opts"]
    rec = d["with_d5"]
    x = np.array(rec["x"])
    T = np.array([d["targets"][k] for k in KEYS])
    S = np.array([d["errors"][k] for k in KEYS])
    sd = T[3:6] / V * np.exp(x[12:15])
    se = T[6:9] / V * np.exp(x[15:18])
    W = umix(x)
    Sd = np.diag(sd).astype(complex)
    Se = W @ np.diag(se) @ W.T
    H, F = (3 * Sd + Se) / 4, (Sd - Se) / 4
    r, s = 10 ** x[9], 10 ** x[10] * np.exp(1j * x[11])
    A = np.zeros((3, 3), complex)
    a = x[18:24] * 1e-4
    for k, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
        A[i, j] = a[2 * k] + 1j * a[2 * k + 1]
        A[j, i] = -A[i, j]
    rho, eps = x[24], x[25]
    if o.get("eps_fixed") is not None:
        eps = float(o["eps_fixed"])
    eta1 = float(o.get("eta1", 1.0))
    ke, ku, kD = (1 - 3 * rho) / (1 + rho), (eta1 + eps * rho) / (1 + rho), (eta1 - 3 * eps * rho) / (1 + rho)
    Yd, Ye = Sd + A, Se + ke * A
    Yu, Yn = r * (H + s * F + ku * A), r * (H - 3 * s * F + kD * A)
    mnu = -Yn @ np.linalg.inv(F) @ Yn.T
    assert np.allclose(mnu, mnu.T)
    mu, Eu = left(Yu, conv)
    md, Ed = left(Yd, conv)
    me, Ee = left(Ye, conv)
    VCKM = Eu.conj().T @ Ed
    # neutrino: m_nu symmetric, left-handed rotation from m m^dagger (Takagi up to phases)
    wn, N = np.linalg.eigh(mnu @ mnu.conj().T if conv == "MMdag" else mnu.conj().T @ mnu)
    mn = np.sqrt(np.clip(wn, 0, None))
    UP = Ee.conj().T @ N if conv == "MMdag" else Ee.T @ N.conj()
    obs = {}
    for k, v in zip(MK, list(mu * V) + list(md * V) + list(me * V)):
        obs[k] = float(v)
    obs["s12"], obs["s23"], obs["s13"], obs["delta"] = pdg_angles(VCKM)
    p12, p23, p13, _ = pdg_angles(UP)
    obs["sin2_th12"], obs["sin2_th23"], obs["sin2_th13"] = p12 ** 2, p23 ** 2, p13 ** 2
    a21, a31 = mn[1] ** 2 - mn[0] ** 2, mn[2] ** 2 - mn[0] ** 2
    i21, i31 = KEYS.index("dm21"), KEYS.index("dm31")
    lam = (a21 * T[i21] / S[i21] ** 2 + a31 * T[i31] / S[i31] ** 2) / (a21 ** 2 / S[i21] ** 2 + a31 ** 2 / S[i31] ** 2)
    obs["dm21"], obs["dm31"] = lam * a21, lam * a31
    pulls = {}
    for i, k in enumerate(KEYS):
        if k in MK:
            pulls[k] = math.log(obs[k] / T[i]) * T[i] / S[i]
        elif k == "delta":
            pulls[k] = ((abs(obs[k]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        else:
            pulls[k] = (obs[k] - T[i]) / S[i]
    chi2 = sum(v * v for v in pulls.values())
    return {"label": label, "conv": conv, "chi2": chi2, "chi2_designer": rec["chi2_obs"],
            "pulls": {k: round(v, 4) for k, v in pulls.items()}, "ms_md": obs["m_s"] / obs["m_d"],
            "A_over_md_down": float(np.abs(A).max() / (T[3] / V)), "A_over_ms_down": float(np.abs(A).max() / (T[4] / V)),
            "r": r, "|s|": abs(s), "arg_s": float(np.angle(s)), "rho": rho, "eps": eps}


def main():
    out = []
    for lab in ("L2_A_c0.1", "L2_A_c0.3", "L2_A_c0.03", "L3p_A"):
        if not (FLAV / f"d2c_{lab}.json").exists():
            continue
        for conv in ("MMdag", "MdagM"):
            try:
                r = evaluate(lab, conv)
            except Exception as e:  # noqa: BLE001
                r = {"label": lab, "conv": conv, "error": repr(e)}
            out.append(r)
            print(json.dumps({k: v for k, v in r.items() if k != "pulls"}), flush=True)
            if "pulls" in r and r["chi2"] > 1:
                big = {k: v for k, v in r["pulls"].items() if abs(v) > 1}
                print("   pulls>1:", big, flush=True)
    (HERE / "sk_d2_eval.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
