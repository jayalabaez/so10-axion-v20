"""D2 helper: GUT-scale flavour targets for a ONE-STEP SO(10) -> SM chain (no intermediate gauge group).

Bottom-up: PDG-2024 masses / CKM at M_Z (R2-C inputs_mz.json), SM two-loop gauge + Yukawa RGEs (lib_flav.py = copy
of R2-C lib_r2c.py with the Weinberg-operator lambda coefficient fixed: +2 lam for V = (lam/2)(H^+H)^2), one-loop
gauge-b shifts of the light colour states above their masses and of the B63 S-sector (+28/3) above M_s, run to M_U.
Neutrino data (NuFIT 6.0 NO with SK) are compared at M_U for the angles (running of a hierarchical NO spectrum is
negligible, standard) and for Delta m^2 with the Weinberg-operator factor eta^2, eta = kappa(M_Z)/kappa(M_U)
(computed here from the same RGEs).
Error model (stated for D2): every mass keeps its M_Z relative error, plus a 1 % theory floor in quadrature
(main runs; 0 % / 3 % variants); s12, s23, s13 keep their relative errors (s23, s13 rescaled with their running);
delta_CKM absolute; NuFIT 6.0 errors (symmetrised) for sin^2 th_ij and Delta m^2.
"""
from __future__ import annotations

import math
import numpy as np

import lib_flav as L

# light colour states of the one-step chains (one-loop Delta b = (b1 GUT, b2, b3))
DB_STATE = {"(8,1,0)": np.array([0.0, 0.0, 0.5]), "(8,3,0)": np.array([0.0, 8 / 3, 1.5]),
            "(6,2,-1/6)": np.array([1 / 15, 1.0, 5 / 3])}

CHAINS = {
    # option (a): (8,1,0) at 1e4 GeV, (8,3,0) at 2.25e9 GeV, M_U = 1.02e16 (unif1s nominal two-loop)
    "a": {"light": {"(8,1,0)": 1.0e4, "(8,3,0)": 2.248e9}, "MU": 1.017e16},
    # option (b): (6,2,-1/6) at 1e9 GeV, (8,3,0) at 2.95e11 GeV, M_U = 2.16e16
    "b": {"light": {"(6,2,-1/6)": 1.0e9, "(8,3,0)": 2.95e11}, "MU": 2.16e16},
}


def db_func_factory(light, M_s=L.M_S):
    def db(mu):
        d = np.zeros(3)
        for k, m in light.items():
            if mu > m:
                d = d + DB_STATE[k]
        if mu > M_s:
            d = d + L.B63_SM_SHIFT
        return d
    return db


def run_chain(st, mu0, mu1, light, rtol=1e-8):
    """run an SMState from mu0 to mu1 (either direction) piecewise with the db of the chain."""
    db = db_func_factory(light)
    pts = sorted(set([mu0, mu1] + [m for m in list(light.values()) + [L.M_S] if min(mu0, mu1) < m < max(mu0, mu1)]))
    if mu0 > mu1:
        pts = pts[::-1]
    for lo, hi in zip(pts[:-1], pts[1:]):
        st = L.run_sm(st, lo, hi, db=db(math.sqrt(lo * hi)), rtol=rtol)
    return st


def data_matrices(d):
    m = {k: (d[k][0] if isinstance(d[k], (tuple, list)) else d[k]) for k in L.ALL_KEYS}
    V = L.umix(m["s12"], m["s23"], m["s13"], m["delta"])
    Yu = np.diag([m["m_u"], m["m_c"], m["m_t"]]).astype(complex) / L.VEV
    Yd = V.conj() @ np.diag([m["m_d"], m["m_s"], m["m_b"]]).astype(complex) / L.VEV
    Ye = np.diag([m["m_e"], m["m_mu"], m["m_tau"]]).astype(complex) / L.VEV
    return Yu, Yd, Ye


def gut_targets(chain="a", floor=0.01, nu="nufit60_sk", lam0=0.26):
    ch = CHAINS[chain]
    data = L.data_set(nu=nu, floor=floor)
    Yu, Yd, Ye = data_matrices(data)
    kap = np.diag([1e-14, 2e-14, 5e-14]).astype(complex)          # tiny probe kappa (GeV^-1) for eta
    st = L.SMState(L.gauge_mz(), lam0, Yu, Yd, Ye, kap)
    st = run_chain(st, L.MZ, ch["MU"], ch["light"])
    o = L.observables(st.Yu, st.Yd, st.Ye, st.kappa * L.VEV ** 2)
    # eta: kappa(M_Z)/kappa(M_U) per eigen-direction (third one, dominant for dm31); run a probe kappa down
    k_top = np.diag([0, 0, 1e-14]).astype(complex)
    st2 = L.SMState(st.g, st.lam, st.Yu, st.Yd, st.Ye, k_top)
    st2 = run_chain(st2, ch["MU"], L.MZ, ch["light"])
    eta = float(abs(st2.kappa[2, 2]) / 1e-14)
    T = np.zeros(18); S = np.zeros(18)
    for i, k in enumerate(L.ALL_KEYS):
        c, s = data[k]
        if k in L.MASS_KEYS:
            T[i] = o[k]; S[i] = s / c * T[i]
        elif k in ("s12", "s23", "s13"):
            T[i] = o[k]; S[i] = s / c * T[i]
        elif k == "delta":
            T[i] = abs(o[k]); S[i] = s
        else:
            T[i] = c; S[i] = s                    # neutrino data compared at M_U (dm's: model x eta^2)
    sd0 = T[[3, 4, 5]] / L.VEV; se0 = T[[6, 7, 8]] / L.VEV
    return {"chain": chain, "MU": ch["MU"], "light": ch["light"], "T": T, "S": S, "sd0": sd0, "se0": se0, "eta": eta,
            "g_MU": st.g.tolist(), "lam_MU": st.lam, "yt_MU": float(T[2] / L.VEV), "data": data, "floor": floor}


if __name__ == "__main__":
    for c in ("a", "b"):
        tg = gut_targets(c)
        print(c, "MU", tg["MU"], "eta", round(tg["eta"], 4), "g_MU", np.round(tg["g_MU"], 4), "lam_MU", round(tg["lam_MU"], 4))
        for k, t, s in zip(L.ALL_KEYS, tg["T"], tg["S"]):
            print(f"   {k:10s} {t:.5e}  +- {s:.2e}  ({s / t * 100 if t else 0:.2f} %)")
        print("   m_s/m_d(M_U) =", tg["T"][4] / tg["T"][3], " m_b/m_tau(M_U) =", tg["T"][5] / tg["T"][8])
