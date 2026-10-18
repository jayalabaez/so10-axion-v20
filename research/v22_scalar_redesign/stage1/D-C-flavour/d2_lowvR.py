"""D2 for the V2 (A2-EFT: G3211 at M_U via 45_H, B-L at v_R in the type-I window) structure and for low-v_R reference:
same single-light-doublet Yukawa structure as the one-step model (SU(2)_R broken at M_U -> generic r, s), M_R =
v_R (C_R F/c_d126 + tau K) with the O5 coefficient K = eps S.  GUT-scale proxy with chain-a targets (EST: the G3211
segment v_R -> M_U is approximated by SM-like running; R2-C found O(40-80) proxy-vs-exact shifts for G3221).
Required max|S| = Q(TAU_eff) * (TAU/TAU_eff) from the decoupled inversion (d2_decoupled.minimise_Q), sigma = 0."""
import json, sys
import numpy as np
import d2_targets as TG
import d2_decoupled as Dc

D = json.load(open("fits/decoupled_a.json", encoding="utf-8"))
tg = TG.gut_targets("a", floor=D["floor"])
out = {}
for key in ("300.0", "30.0"):
    row = D["stage1"][key][0]
    m = Dc.charged_mats(np.array(row["x"]), tg)
    for vR in (3e12, 1e13, 3e13, 1e14):
        for TAU in (3.0, 9.8):
            q = Dc.minimise_Q(m, tg, vR, tg["data"], TAU, 0.0113, seed=3, nstart=20)
            k = f"rho_max={key},vR={vR:.0e},TAU={TAU}"
            out[k] = {"chi2_13": row["chi2_13"], "rho": row["rho_abs"], **q}
            print(k, f"chi2_13={row['chi2_13']:.2f} required max|S| = {q['Q']:.3f}  c_d126 = {q['c_d126']:.4f}  M_R = {np.array(q['M_R_GeV'])}  "
                  f"cancel = {q['cancellation_ratio']:.3g}  chi2_nu = {q['chi2_nu']:.2f}", flush=True)
json.dump(out, open("fits/d2_lowvR.json", "w", encoding="utf-8"), indent=1)
