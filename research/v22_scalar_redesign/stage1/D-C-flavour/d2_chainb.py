"""D2 for the realisable light content (chain b: (6,2,-1/6) + (8,3,0), M_U = 2.16e16, eps = |Phi|/M_Pl,red = 0.024) at the
v_R implied by the LP points (r = 0.5-1 -> v_R ~ 1e16-6e16): fresh stage-1 charged fits with chain-b targets, then the
required O5 size max|S| = Q from the decoupled inversion (sigma = 0) for |tau| = 3, 5, 9.8."""
import json
import numpy as np
import d2_targets as TG
import d2_decoupled as Dc
tg = TG.gut_targets("b", floor=0.01)
out = {}
for rho_max in (300.0, 30.0):
    x, c = Dc.fit_charged(tg, rho_max, 7)
    m = Dc.charged_mats(x, tg)
    out[str(rho_max)] = {"chi2_13": c, "rho": abs(m["rho"]), "r": m["r"], "x": x.tolist(), "stage2": {}}
    print(f"chain b rho_max={rho_max}: chi2_13 = {c:.3f} |rho| = {abs(m['rho']):.2f} r = {m['r']:.2f}", flush=True)
    for vR in (1e16, 3e16, 6e16):
        for TAU in (3.0, 5.0, 9.8):
            q = Dc.minimise_Q(m, tg, vR, tg["data"], TAU, 0.024, seed=2, nstart=15)
            out[str(rho_max)]["stage2"][f"vR={vR:.0e},TAU={TAU}"] = q
            print(f"   vR={vR:.0e} TAU={TAU}: required max|S| = {q['Q']:.3f}  c_d126 = {q['c_d126']:.4f}  M_R = {np.array(q['M_R_GeV'])}  chi2_nu = {q['chi2_nu']:.2f}", flush=True)
json.dump(out, open("fits/d2_chainb.json", "w", encoding="utf-8"), indent=1)
