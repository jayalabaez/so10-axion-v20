"""D4: dependence of the one-step solutions on the B63 S-sector mass M_s (y_s = 0.336) -> M_s range with Lambda_2L > M_Pl,red."""
import json, math
import unif1s as Q
import d4_unif as D4
out = {}
for ch, C in D4.CHAINS.items():
    for Ms in (3e12, 4e12, 5e12, 6e12, 7e12, 8.5e12, 1e13, 1.21e13):
        m = Q.OneStep(dict(C["light"]), M_s=Ms)
        s = m.solve(C["free"], C["guess"])
        e = D4.evaluate(ch, m, s)
        out[f"{ch},Ms={Ms:.2e}"] = e
        print(ch, f"Ms={Ms:.2e}", f"MU={e['M_U']:.3e} aU={e['aU']:.2f} tau_latAR={e['tau_lat_chainAR']:.2e} L2={e['Lambda2L_over_MPl']:.3f}", flush=True)
json.dump(out, open("d4_ms_scan.json", "w", encoding="utf-8"), indent=1, default=str)
