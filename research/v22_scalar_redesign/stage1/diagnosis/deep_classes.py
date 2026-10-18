"""Classify the R2-A descent endpoints by the operator class that supplies the depth (reads deep_budget inputs again)."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
R2A = Path(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research\research\v21_kill_gates\round2\R2-A-vacuum-two-bidoublets")
SCR = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21R2\R2-A-vacuum-two-bidoublets")
summ = json.load(open(R2A / "descent_summary.json", encoding="utf-8"))
CLS = {"O31": "O31 H+2 S^2", "O28": "O28 H+ S^2 S+", "O35": "O35 |H|^2|S|^2", "O15": "H-S cubic/Phi portals", "O38": "H-S cubic/Phi portals",
       "O45": "H-S cubic/Phi portals", "O27": "O27 126 self", "O05": "Sigma mass/norm", "O25": "Sigma mass/norm", "O26": "Sigma mass/norm",
       "O44": "Phi2 Sigma2", "O14": "Phi Sigma Sigma+ cubic", "O06": "H mass", "O33": "H-singlet portals", "O34": "H-singlet portals",
       "O12": "H-singlet portals", "O46": "Phi2 H+H", "O36": "H self quartic", "O07": "Phi210 self", "O17": "Phi210 self", "O48": "Phi210 self",
       "O42": "Phi210-singlet", "O43": "Phi210-singlet"}
out = []; agg = defaultdict(float); n = 0
for rnd, R in summ.items():
    sol = np.load(SCR / R["sol"]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    Z = np.load(SCR / f"{R['tag']}_rows.npz"); J0 = Z["values"]; q0 = Z["q"]
    if rnd in ("R1", "R2", "X1"):
        print(f"--- {rnd}: sol {R['sol']}  c[O06 m10^2]={c[ids.index('lambda::O06_B01_Hdag_H_norm')]:+.3f}  c[O05 m126^2]={c[ids.index('lambda::O05_B01_126bar_norm')]:+.3f}"
              f"  c[O31]=({c[ids.index('re::O31_B01_unique_Hdag2_Sigma2')]:+.4f},{c[ids.index('im::O31_B01_unique_Hdag2_Sigma2')]:+.4f})"
              f"  c[O28]=({c[ids.index('re::O28_B01_unique_Hdag_Sigma2_Sigmadag')]:+.4f},{c[ids.index('im::O28_B01_unique_Hdag_Sigma2_Sigmadag')]:+.4f})"
              f"  c[O27_B02]={c[ids.index('lambda::O27_B02_126bar_self_projectors')]:+.4f} c[O35_B02]={c[ids.index('lambda::O35_B02_H_Sigma_hermitian')]:+.4f}")
    for run in R["runs"]:
        B = np.load(SCR / f"descend_{run['name']}_bank.npz"); J = B["J"]; k = int(np.argmin(J @ c)); d = c * (J[k] - J0); tot = d.sum()
        cl = defaultdict(float)
        for i, pid in enumerate(ids):
            base = pid.split("::")[1].split("_B")[0]
            cl[CLS.get(base, "singlets (S,Phi17)")] += d[i]
        n += 1
        for kk, v in cl.items(): agg[kk] += v / abs(tot)
        hs = cl["O31 H+2 S^2"] + cl["O28 H+ S^2 S+"] + cl["O35 |H|^2|S|^2"] + cl["H-S cubic/Phi portals"]
        hm = cl["H mass"] + cl["Phi2 H+H"] + cl["H-singlet portals"]
        kind = "HS-mixed" if hs < 0.6 * tot else ("H-mass" if hm < 0.6 * tot else ("Sigma-self" if cl["O27 126 self"] < 0.6 * tot else "mixed"))
        bn = run["block_norms_at_min"]
        out.append({"run": run["name"], "dV": round(float(tot), 3), "class": kind, "HSmixed": round(float(hs), 2), "Hmass": round(float(hm), 2),
                    "O27": round(float(cl["O27 126 self"]), 2), "singlets": round(float(cl["singlets (S,Phi17)"]), 2),
                    "Phi210": round(float(cl["Phi210 self"] + cl["Phi210-singlet"]), 2),
                    "blocks": {k2: round(v2, 2) for k2, v2 in bn.items()}})
    print(f"    q* blocks ({R['tag']}): " + str({k2: round(float(np.linalg.norm(q0[s])), 3) for k2, s in
          zip(["Phi210", "H10", "Sigma126bar", "S", "Phi17"], [slice(0, 210), slice(210, 230), slice(230, 482), slice(482, 484), slice(484, 486)])}))
cnt = defaultdict(int)
for o in out:
    cnt[o["class"]] += 1
    print(f"{o['run']:12s} dV={o['dV']:+8.2f} {o['class']:10s} HSmix={o['HSmixed']:+7.2f} Hmass={o['Hmass']:+7.2f} O27={o['O27']:+7.2f} sing={o['singlets']:+6.2f} Phi={o['Phi210']:+6.2f} {o['blocks']}")
print("classes:", dict(cnt))
print("mean normalised class contribution:", {k: round(v / n, 3) for k, v in sorted(agg.items(), key=lambda kv: kv[1])})
json.dump({"endpoints": out, "classes": dict(cnt), "mean_norm": {k: v / n for k, v in agg.items()}}, open("deep_classes.json", "w"), indent=1)
