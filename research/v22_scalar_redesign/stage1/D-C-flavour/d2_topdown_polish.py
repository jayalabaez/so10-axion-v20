"""D2: top-down ('exact' one-step chain) polish of a verified point.  Only the O5 coefficient matrix K (12 real
parameters, |K_ij| <= cap eps) is varied: with sigma = 0 the charged sector does not depend on K, so this re-fits the
neutrino sector through the full SM running M_U -> M_Z with sequential nu^c decoupling (removes the proxy eta and
threshold approximations).  Reports chi2 at M_Z (18 observables, same error model) and max|S|.
usage: python -B d2_topdown_polish.py <verify.json> <decoupled.json> <out.json> [cap]
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
from scipy.optimize import least_squares

import lib_flav as L
import d2_targets as TG
import d2_eft_fit as E


def main():
    vf, dec, out = sys.argv[1], sys.argv[2], sys.argv[3]
    capmax = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    V = json.load(open(vf, encoding="utf-8"))
    D = json.load(open(dec, encoding="utf-8"))
    chain, vR, TAU, eps = V["chain"], V["vR"], V["TAU_eff"], V["eps"]
    tg = TG.gut_targets(chain, floor=D["floor"])
    x = np.array(V["summary"]["x"])
    cap0 = V["required_max|S|"] * 1.0001
    E.TAU = TAU * 1.0000001; E.SIG = 1.0
    light = TG.CHAINS[chain]["light"]
    db = TG.db_func_factory(light)
    th = tuple(sorted([mm for mm in list(light.values()) + [L.M_S]], reverse=True))
    data = tg["data"]
    # re-express K in an absolute parametrisation: K_ij = eps * capmax * sigm(u) e^{i phi}
    Kabs = np.array(V["summary"]["K_abs"])
    xK = x.copy()

    def build(z):
        xx = xK.copy()
        xx[16:28] = z
        return xx

    # convert stored sigmoid params from cap0 to capmax normalisation
    z0 = x[16:28].copy()
    for n in range(6):
        q = 1 / (1 + math.exp(-x[16 + 2 * n])) * cap0 / capmax
        q = min(max(q, 1e-9), 1 - 1e-9)
        z0[2 * n] = math.log(q / (1 - q))

    def topdown(z, want=False):
        xx = build(z)
        M = E.model(xx, tg, vR, "o5", capmax * eps)
        st = L.SMState(tg["g_MU"], tg["lam_MU"], M["Yu"], M["Yd"], M["Ye"], np.zeros((3, 3), complex), M["Yn"], M["MR"])
        try:
            st2 = L.run_sm_with_seesaw(st, tg["MU"], L.MZ, db_func=db, rtol=1e-7, thresholds_extra=th)
        except Exception:
            return np.full(18, 1e3) if not want else (np.full(18, 1e3), None, None)
        o = L.observables(st2.Yu, st2.Yd, st2.Ye, st2.kappa * L.VEV ** 2)
        pl = L.pulls(o, data)
        R = np.array([pl[k] for k in L.ALL_KEYS])
        R = np.where(np.isfinite(R), R, 1e3)
        return R if not want else (R, o, M)

    R0 = topdown(z0)
    s = least_squares(topdown, z0, method="trf", max_nfev=400, xtol=1e-10, ftol=1e-10, diff_step=1e-6)
    R, o, M = topdown(s.x, want=True)
    xx = build(s.x)
    Kfin = E.model(xx, tg, vR, "o5", capmax * eps)["K"]
    mR = np.sort(np.linalg.svd(M["MR"], compute_uv=False))
    res = {"chain": chain, "vR": vR, "TAU_eff": TAU, "eps": eps, "cap": capmax,
           "chi2_MZ_before": float(R0 @ R0), "chi2_MZ_after": float(R @ R), "max|S|": float(np.abs(Kfin).max() / eps),
           "pulls_MZ": dict(zip(L.ALL_KEYS, [float(v) for v in R])), "n_pull_gt3": int(np.sum(np.abs(R) > 3)),
           "M_R_GeV": mR.tolist(), "m_nu_eV": o["m_nu_eV"], "sum_mnu_eV": float(sum(o["m_nu_eV"])),
           "delta_pmns_deg": math.degrees(o["delta_pmns"]) % 360,
           "mbb_eV": L.mbb_and_majorana(o["U_pmns"], o["m_nu_eV"]),
           "K_abs_over_eps": (np.abs(Kfin) / eps).tolist(), "x": xx.tolist()}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(f"top-down polish {chain} vR={vR:.0e} TAU={TAU} cap={capmax}: chi2_MZ {res['chi2_MZ_before']:.2f} -> {res['chi2_MZ_after']:.3f}, "
          f"max|S| = {res['max|S|']:.3f}, n>3 = {res['n_pull_gt3']}, M_R = {np.array(mR)}, sum m_nu = {res['sum_mnu_eV']:.4f} eV")
    print("  pulls:", {k: round(v, 2) for k, v in res["pulls_MZ"].items()})


if __name__ == "__main__":
    main()
