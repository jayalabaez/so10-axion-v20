"""D2 verification of the decoupled solutions:
 (1) forward evaluation of the full one-step O5-EFT model (d2_eft_fit.residuals, 18 observables at M_U) at the point
     built from a stage-1 charged solution + the stage-2 neutrino inversion (K = (M_R/v_R - C_R F/c_d126)/tau,
     tau = TAU_eff e^{i phi}); reports chi2_18, max|S| = max|K|/eps and the K pattern;
 (2) 'exact' top-down check: run the GUT-scale Yukawas and M_R of that point down to M_Z with the SM two-loop RGEs of
     the one-step chain (lib_flav, kappa coefficient fixed), sequential tree-level nu^c decoupling, the light colour
     states' and the B63 S-sector's gauge-b shifts, and compare with the M_Z data (same error model): chi2_MZ.
usage: python -B d2_verify.py <decoupled.json> <chain> <rho_max key> <vR> <TAU_eff> <eps> <out.json>
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

import lib_flav as L
import d2_targets as TG
import d2_eft_fit as E
import d2_decoupled as Dc

C_R = E.C_R


def main():
    dec, chain, key, vR, TAU, eps, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
    D = json.load(open(dec, encoding="utf-8"))
    tg = TG.gut_targets(chain, floor=D["floor"])
    row = D["stage1"][key][0]
    x1 = np.array(row["x"])
    m = Dc.charged_mats(x1, tg)
    nu = Dc.minimise_Q(m, tg, vR, tg["data"], TAU, eps, seed=7, nstart=30)
    cd = nu["c_d126"]
    y = np.array([math.log10(nu["m1_eV"]), nu["a21"], nu["a31"], nu["delta_pmns"]] + list(nu["nu_pulls"]))
    MR, chi2nu = Dc.required_MR(m, tg, y, tg["data"])
    best = None
    for ph in np.linspace(-math.pi, math.pi, 25):
        tau = TAU * np.exp(1j * ph)
        K = (MR / vR - C_R * m["F"] / cd) / tau
        s = float(np.abs(K).max() / eps)
        if best is None or s < best[0]:
            best = (s, ph, K)
    smax, ph, K = best
    # forward model with these values: build the 35-vector (|K_ij| <= cap*eps with cap = smax*1.0001)
    E.TAU = TAU * 1.0000001; E.SIG = 1.0
    cap = max(smax * 1.0001, 1e-6)
    x = np.zeros(E.NPAR)
    x[0:12] = x1[0:12]; x[29:35] = x1[12:18]
    cmax = math.sqrt(E.CMAX2 / (1 + abs(m["rho"]) ** 2))
    p = cd / cmax
    x[28] = math.log(p / (1 - p)) if p < 1 else 30.0
    x[12] = -40.0
    x[14] = math.log(0.9999999 / (1 - 0.9999999)); x[15] = ph
    for n, (i, j) in enumerate(E.SYM):
        v = K[i, j]; q = min(abs(v) / (cap * eps), 1 - 1e-12)
        x[16 + 2 * n] = math.log(q / (1 - q)); x[17 + 2 * n] = math.atan2(v.imag, v.real)
    R = E.residuals(x, tg, vR, "o5", cap * eps)
    summ = E.summarize(x, tg, vR, "o5", cap * eps)
    # (2) top-down: GUT-scale matrices of the forward model -> M_Z
    M = E.model(x, tg, vR, "o5", cap * eps)
    st = L.SMState(tg["g_MU"], tg["lam_MU"], M["Yu"], M["Yd"], M["Ye"], np.zeros((3, 3), complex), M["Yn"], M["MR"])
    light = TG.CHAINS[chain]["light"]
    db = TG.db_func_factory(light)
    th = sorted([mm for mm in list(light.values()) + [L.M_S]], reverse=True)
    st2 = L.run_sm_with_seesaw(st, tg["MU"], L.MZ, db_func=db, rtol=1e-8, thresholds_extra=tuple(th))
    o = L.observables(st2.Yu, st2.Yd, st2.Ye, st2.kappa * L.VEV ** 2)
    data = tg["data"]
    pl = L.pulls(o, data)
    chi2_mz = float(sum(v * v for v in pl.values()))
    res = {"chain": chain, "rho_max_key": key, "vR": vR, "TAU_eff": TAU, "eps": eps, "chi2_13_stage1": row["chi2_13"],
           "chi2_nu_inversion": chi2nu, "required_max|S|": smax, "tau_phase": ph, "c_d126": cd,
           "chi2_18_forward_MU": float(R @ R), "pulls_MU": dict(zip(L.ALL_KEYS, [float(v) for v in R])),
           "summary": summ, "chi2_MZ_topdown": chi2_mz, "pulls_MZ_topdown": {k: float(v) for k, v in pl.items()},
           "obs_MZ": {k: (float(v) if not isinstance(v, (list, np.ndarray)) else None) for k, v in o.items() if k != "U_pmns"},
           "m_nu_eV_MZ": o["m_nu_eV"], "K_abs_over_eps": (np.abs(K) / eps).tolist()}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(f"{chain} {key} vR={vR:.0e} TAU={TAU} eps={eps}: required max|S| = {smax:.3f}; chi2_18(M_U, forward) = {R @ R:.3f}; "
          f"chi2(M_Z, top-down) = {chi2_mz:.3f}; c_d126 = {cd:.4f}; M_R = {np.array(summ['M_R_GeV'])}")
    print("  M_U pulls:", {k: round(v, 2) for k, v in res["pulls_MU"].items()})
    print("  M_Z pulls:", {k: round(v, 2) for k, v in res["pulls_MZ_topdown"].items()})
    print("  m_nu (eV, M_Z):", o["m_nu_eV"], " sum =", sum(o["m_nu_eV"]))


if __name__ == "__main__":
    main()
