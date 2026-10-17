#!/usr/bin/env python3
"""Report tables from the R2-B json outputs (adds the direct-lattice proton lifetime tau_dir = tau_repo/4.530)."""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SK, HK = 2.4e34, 7.8e34
RATIO = 4.530  # tau_repo / tau_direct (r2b_model.proton_lifetime_direct_years; alpha- and M-independent)


def g(x, f="%.3g"):
    return "-" if x is None else (f % x if isinstance(x, (int, float)) else str(x))


def mc_tables(fn):
    d = json.load(open(fn))
    out = []
    for cont, res in d.items():
        if not isinstance(res, dict) or "coherent" not in res:
            continue
        for scen in ("light", "gut", "both", "both_Ms3e12", "gut_half"):
            if scen not in res:
                continue
            rows = [r for r in res[scen]["rows"] if r.get("ok")]
            n = len(res[scen]["rows"])
            taus = sorted(r["tau_p"] for r in rows)
            fsk = sum(t > SK for t in taus) / n
            fsk_dir = sum(t / RATIO > SK for t in taus) / n
            fhk = sum(t > HK for t in taus) / n
            l2 = [r.get("L2") or 0 for r in rows]
            l3 = [r.get("L3") or 0 for r in rows]
            vr = sorted(r["v_R"] for r in rows)
            mu = sorted(r["M_U"] for r in rows)
            fall = sum(1 for r in rows if r["tau_p"] > SK and (r.get("L2") or 0) > 1 and 1e11 <= r["v_R"] <= 1e14) / n
            fall_dir = sum(1 for r in rows if r["tau_p"] / RATIO > SK and (r.get("L2") or 0) > 1 and 1e11 <= r["v_R"] <= 1e14) / n
            out.append(f"{cont:5s} {scen:12s} n={n:3d} tau[min/med/max]={g(taus[0])}/{g(taus[len(taus)//2])}/{g(taus[-1])} "
                       f"f(tau>SK)={fsk:.3f} f_dir={fsk_dir:.3f} f(>HK)={fhk:.2f} M_U={g(mu[0])}-{g(mu[-1])} "
                       f"v_R={g(vr[0])}-{g(vr[-1])} L2min={min(l2):.2f} L3[min/med]={min(l3):.2f}/{sorted(l3)[len(l3)//2]:.2f} "
                       f"f(L3>1)={sum(x > 1 for x in l3)/n:.2f} f(all)={fall:.3f} f(all,dir)={fall_dir:.3f}")
        for k, r in res["coherent"].items():
            out.append(f"{cont:5s} coherent {k:22s} v_R={g(r.get('v_R'))} M_U={g(r.get('M_U'))} aU={g(r.get('alpha_U_inv'),'%.2f')} "
                       f"tau={g(r.get('tau_p'))} tau_dir={g((r.get('tau_p') or 0)/RATIO)} L2={g(r.get('L2'))} L3={g(r.get('L3'))}")
    return out


if __name__ == "__main__":
    for fn in sorted(glob.glob(os.path.join(HERE, "r2b_scan_mc_*.json"))):
        print("==", os.path.basename(fn))
        for line in mc_tables(fn):
            print(line)
