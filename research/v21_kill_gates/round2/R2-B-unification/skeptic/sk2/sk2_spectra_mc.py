#!/usr/bin/env python3
"""(1) R2-A stage-A C2-family spectra (m^2/|Phi|^2 as assigned in R2-B's r2b_r2a_c2check.json, read-only input)
fed through the INDEPENDENT sk2_lib chain with g_U iteration; (2) own threshold Monte Carlo for C2 / C1p / C1 / C0."""
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sk2_lib as L

MAPN = {
    "210:(3,1,3)_4/3": "210(3,1,3)", "126b:(6b,1,3)_-2/3": "126(6b,1,3)", "126b:(3b,1,3)_2/3": "126(3b,1,3)",
    "210:(8,1,3)_0": "210(8,1,3)", "210:(1,1,3)_0": "210(1,1,3)", "210:(6,2,2)_2/3": "210(6,2,2)",
    "210:(3,2,2)_-2/3 phys": "210(3,2,2)", "210:(1,2,2)_-2": "210(1,2,2)-2", "126b:(3,2,2)_4/3": "126(3,2,2)",
    "126b:(3b,2,2)_-4/3": "126(3b,2,2)", "126b:(8,2,2)_0": "126(8,2,2)", "210:(8,1,1)_0": "210(8,1,1)",
    "210:(3,3,1)_4/3": "210(3,3,1)", "210:(8,3,1)_0": "210(8,3,1)", "210:(1,3,1)_0": "210(1,3,1)",
    "126b:(3,1,1)_-2/3": "126(3,1,1)", "126b:(3b,1,1)_2/3": "126(3b,1,1)", "126b:(6,3,1)_2/3": "126(6,3,1)",
    "126b:(3,3,1)_-2/3": "126(3,3,1)", "126b:(1,3,1)_-2 Delta_L": "126(1,3,1)", "10:(3,1,1)_-2/3": "10(3,1,1)",
    "10:(3b,1,1)_2/3": "10(3b,1,1)",
}
MX_OVER_GPHI = math.sqrt(0.5 ** 1 * 0.5 + 1.0 / 6.0)   # sqrt(p^2/2 + a^2), (p,a) = (1/sqrt2, -1/sqrt6) = 0.6455

out = {"spectra": {}, "mc": {}}
src = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "r2b_r2a_c2check.json")))
for pt, d in src.items():
    m2 = {MAPN[k]: v for k, v in d["assigned_m2_over_Phi2"].items()}
    assert set(m2) == {n for n in L.SCAL if n not in L.CONT["C2"]}, pt
    for scale in (1.0, 0.5, 2.0):
        for sv in (1.0, -1.0):
            if scale != 1.0 and sv != 1.0:
                continue
            aU = 34.0
            guess = (math.log(3e10), math.log(7e15), 40.0)
            for it in range(30):
                gU = math.sqrt(4 * math.pi / aU)
                rat = {n: scale * math.sqrt(v) / (MX_OVER_GPHI * gU) for n, v in m2.items()}
                m = L.Model("C2", sv=sv, gut_r=rat)
                r = m.solve(guess)
                guess = (math.log(r["v_R"]), math.log(r["M_U"]), r["a2R"])
                if abs(r["aU"] - aU) < 1e-9:
                    break
                aU = r["aU"]
            row = dict(r, tau_repo=L.tau_repo(r["M_U"], r["aU"]), tau_lat=L.tau_lattice(r["M_U"], r["aU"]),
                       tau_bchpt144=L.tau_bchpt(r["M_U"], r["aU"]), L2=L.landau_2l(r["M_U"], r["aU"]),
                       rmin=min(rat.values()), rmax=max(rat.values()), iters=it)
            key = f"{pt}|x{scale}|sv{sv:+.0f}"
            out["spectra"][key] = row
            print(f"{key:32s} vR={r['v_R']:.3e} MU={r['M_U']:.3e} aU={r['aU']:.3f} tau_repo={row['tau_repo']:.3e} "
                  f"tau_lat={row['tau_lat']:.3e} tau_bchpt144={row['tau_bchpt144']:.3e} L2={row['L2']:.2f} "
                  f"r=[{row['rmin']:.3f},{row['rmax']:.3f}] ok={r['ok']}", flush=True)

# ---- own threshold MC (declared R2-B scan: light x1/3..x3 per SM state incl. W_R; GUT scalars x1/2..x2) ----
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
guesses = {"C2": (math.log(2e10), math.log(6e15), 40.0), "C1p": (math.log(1e11), math.log(3e15), 40.0),
           "C1": (math.log(8e12), math.log(2e15), 40.0), "C0": (math.log(6e12), math.log(3e15), 40.0)}
for c in ["C2", "C1p", "C1", "C0"]:
    rng = random.Random(20261017 + hash(c) % 1000)
    lights = [s[0] for s in L.light_states(L.CONT[c])]
    heavies = [s[0] for s in L.heavy_states(L.CONT[c])]
    res = []
    t0 = time.time()
    for k in range(N if c in ("C2", "C1p") else N // 2):
        lr = {n: math.exp(rng.uniform(math.log(1 / 3), math.log(3))) for n in lights}
        gr = {n: math.exp(rng.uniform(math.log(0.5), math.log(2))) for n in heavies}
        m = L.Model(c, light_r=lr, gut_r=gr)
        r = m.solve(guesses[c])
        if not r["ok"]:
            for gss in [(math.log(1e10), math.log(1e16), 45.0), (math.log(1e12), math.log(5e15), 45.0),
                        (math.log(1e9), math.log(2e16), 45.0)]:
                r = m.solve(gss)
                if r["ok"]:
                    break
        if not r["ok"]:
            res.append(None)
            continue
        tr, tl = L.tau_repo(r["M_U"], r["aU"]), L.tau_lattice(r["M_U"], r["aU"])
        l2 = L.landau_2l(r["M_U"], r["aU"])
        res.append((r["v_R"], r["M_U"], r["aU"], tr, tl, l2))
    ok = [x for x in res if x]
    n = len(ok)
    f_repo = sum(1 for x in ok if x[3] > 2.4e34 and x[5] > 1) / n
    f_lat = sum(1 for x in ok if x[4] > 2.4e34 and x[5] > 1) / n
    f_lat453 = sum(1 for x in ok if x[3] / 4.527 > 2.4e34 and x[5] > 1) / n
    f_seesaw = sum(1 for x in ok if x[3] > 2.4e34 and x[5] > 1 and x[0] >= 1e11) / n
    taus = sorted(x[3] for x in ok)
    summ = {"n": len(res), "n_ok": n, "f_repo": f_repo, "f_lat_own(4.41)": f_lat, "f_lat_r2b(4.53)": f_lat453,
            "f_repo_and_vR>=1e11": f_seesaw, "tau_repo_min_med_max": [taus[0], taus[n // 2], taus[-1]],
            "vR_min_max": [min(x[0] for x in ok), max(x[0] for x in ok)], "L2_min": min(x[5] for x in ok),
            "sec": time.time() - t0}
    out["mc"][c] = {"summary": summ, "samples": res}
    print(c, json.dumps(summ), flush=True)
json.dump(out, open(os.path.join(HERE, "sk2_spectra_mc.json"), "w"), indent=1)
