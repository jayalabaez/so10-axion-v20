"""Full top-down check of a proxy solution: Yukawas at M_U -> G3221 one loop -> v_R (type-I seesaw, all nu^c out at v_R)
-> SM two loop + kappa -> M_Z, chi2 against the M_Z data (researcher's inputs_mz.json; 1% mass floor), then an LM refit of
the proxy parameters on the full top-down residuals.  Conventions as in k2v.py (researcher's rge.py called with transposed
Yukawas so that the cross terms act on the doublet index).
usage: td.py content in.json [out.json] [free]
"""
import sys, os, json, math, time
import numpy as np
from scipy.optimize import least_squares
import k2v
from k2v import rge, VEV, MZ, inp, MASS_KEYS, CKM_KEYS, NU_KEYS, ALL_KEYS, observables, H

def targets_MZ(floor=0.01):
    T = {}
    for k in MASS_KEYS:
        c, s = inp["masses_GeV_MZ"][k]; T[k] = (c, math.sqrt(s**2 + (floor * c)**2))
    for k in CKM_KEYS:
        T[k] = tuple(inp["ckm_MZ"][k])
    for k in NU_KEYS:
        T[k] = tuple(inp["pmns"][k])
    return T

class TopDown:
    def __init__(self, content, model, info):
        self.M = model; self.content = content
        self.vR, self.MU = info["vR"], info["MU"]
        self.b = np.array(info["b_g3221"])
        _, self.g_vR, self.g_MU = k2v.gauge_g3221(self.vR, self.MU, content, info["g_sm_vR"])
        # SM quartic at vR: take the value from the bottom-up run (two-loop gauge/Yukawa, one-loop lambda)
        self.lam_vR = info.get("lam_vR", 0.0)
        self.TZ = targets_MZ()

    def run(self, p):
        """returns observables at MZ for proxy parameters p (rho fixed from the proxy's analytic value)"""
        res, o, rho = self.M.residuals(p)
        if o is None:
            return None
        Yu, Yd, Ye, Yn, Hm, F, r, s = self.M.matrices(p)
        MR = F / rho
        y = rge.pack_g3221(self.g_MU, Yu.T, Yd.T, Ye.T, Yn.T)
        y = rge.run_g3221(y, self.MU, self.vR, self.b, 1e-7)
        _, YuT, YdT, YeT, YnT = rge.unpack_g3221(y)
        Yu, Yd, Ye, Yn = YuT.T, YdT.T, YeT.T, YnT.T
        MD = Yn * VEV
        mnu = -MD @ np.linalg.solve(MR, MD.T)
        kap = mnu / VEV**2
        g1, g2, g3 = self.g_vR[1] * 0 + 0, 0, 0  # placeholder (set below)
        gsm = self.gsm_vR
        ysm = rge.pack_sm(gsm, self.lam_vR, Yu.T, Yd.T, Ye.T, kap)
        ysm = rge.run_sm(ysm, self.vR, MZ, True, 1e-7)
        _, _, YuT, YdT, YeT, kap = rge.unpack_sm(ysm, True)
        return observables(YuT.T, YdT.T, YeT.T, kap * VEV**2)

    def pulls(self, p):
        o = self.run(p)
        if o is None:
            return None, None
        pl = {}
        for k in ALL_KEYS:
            c, s = self.TZ[k]
            if k in MASS_KEYS:
                pl[k] = math.log(max(o[k], 1e-300) / c) * c / s
            elif k == "delta":
                pl[k] = ((abs(o[k]) - c + math.pi) % (2 * math.pi) - math.pi) / s
            else:
                pl[k] = (o[k] - c) / s
        return pl, o

    def residuals(self, p):
        pl, o = self.pulls(p)
        if pl is None:
            return np.full(18, 1e3)
        return np.array([pl[k] for k in ALL_KEYS])

if __name__ == "__main__":
    content = sys.argv[1]; fin = sys.argv[2]
    fout = sys.argv[3] if len(sys.argv) > 3 else fin.replace(".json", "_td.json")
    free = len(sys.argv) > 4 and sys.argv[4] == "free"
    vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
    T, info, _ = k2v.build_targets(vR, MU, content)
    # gauge couplings at vR from the bottom-up two-loop SM run (reuse build_targets internals)
    a_em = 1 / inp["gauge_MZ"]["alpha_em_inv"]; s2 = inp["gauge_MZ"]["sin2_thw_MSbar"]; a_s = inp["gauge_MZ"]["alpha_s"]
    g1 = math.sqrt(4 * math.pi * a_em / (1 - s2) * 5 / 3); g2 = math.sqrt(4 * math.pi * a_em / s2); g3 = math.sqrt(4 * math.pi * a_s)
    yt = inp["masses_GeV_MZ"]["m_t"][0] / VEV
    y0 = rge.pack_sm([g1, g2, g3], 0.26, np.diag([0, 0, yt]).astype(complex), np.zeros((3, 3), complex), np.zeros((3, 3), complex))
    yR = rge.run_sm(y0, MZ, vR, False)
    gsm_vR, lam_vR, *_ = rge.unpack_sm(yR, False)
    info["lam_vR"] = float(lam_vR)
    M = k2v.Model(T, info["rnu"], free_masses=free)
    TD = TopDown(content, M, info); TD.gsm_vR = list(map(float, gsm_vR))
    w = json.load(open(fin))
    recs = w["records"] if "records" in w else [w]
    out = []
    t0 = time.time()
    for rec in recs[:int(os.environ.get("K2_TD_N", "3"))]:
        x = np.array(rec["x"])
        if free and len(x) == 12:
            x = np.concatenate([x, np.zeros(6)])
        r0 = TD.residuals(x); c0 = float(np.sum(r0**2))
        print(f"{rec.get('label','')}: proxy chi2_18={rec.get('chi2_18', float('nan')):.3f} -> top-down before refit {c0:.3f}", flush=True)
        try:
            r = least_squares(TD.residuals, x, method="lm", max_nfev=int(os.environ.get("K2_TD_NFEV", "1500")), xtol=1e-10, ftol=1e-10, gtol=1e-10, x_scale="jac")
            x1, c1 = r.x, float(np.sum(r.fun**2))
        except Exception as e:
            print("refit failed", repr(e)); x1, c1 = x, c0
        pl, o = TD.pulls(x1)
        comp = k2v.composition(M, x1, vR)
        print(f"   refit chi2={c1:.3f} max|pull|={max(abs(v) for v in pl.values()):.2f} t={time.time()-t0:.0f}s", flush=True)
        print("   pulls:", {k: round(v, 2) for k, v in pl.items()}, flush=True)
        print("   comp:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in comp.items()}, flush=True)
        out.append({"label": rec.get("label", ""), "x": list(map(float, x1)), "chi2_td_before": c0, "chi2_td": c1,
                    "pulls": {k: float(v) for k, v in pl.items()}, "obs_MZ": {k: (float(v) if not isinstance(v, list) else v) for k, v in o.items()},
                    "comp": comp, "free_masses": free})
    out.sort(key=lambda z: z["chi2_td"])
    json.dump({"content": content, "vR": vR, "MU": MU, "results": out}, open(fout, "w"), indent=1)
    print("best top-down chi2:", out[0]["chi2_td"] if out else None)
