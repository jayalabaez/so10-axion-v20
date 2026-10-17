"""Profile of the proxy chi2 against sin^2(theta23): refit (LM + short hopping) with sin^2 th23 pinned to a set of values
(hard constraint via a very small error), starting from the best known point(s).  Reports chi2 of the other 17 observables.
usage: profile23.py content in.json [in2.json ...]
"""
import sys, os, json, math, time
import numpy as np
import k2v
content = sys.argv[1]; files = sys.argv[2:]
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
T, info, _ = k2v.build_targets(vR, MU, content)
rng = np.random.default_rng(3)
seeds = []
for f in files:
    w = json.load(open(f))
    for rec in w.get("records", [w])[:3]:
        seeds.append(np.array(rec["x"])[:12])
out = []
t0 = time.time()
for s23 in [None, 0.30, 0.34, 0.38, 0.42, 0.46, 0.50, 0.56]:
    Tp = dict(T)
    if s23 is not None:
        Tp["sin2_th23"] = (s23, 0.001)
    M = k2v.Model(Tp, info["rnu"])
    best = None
    for x0 in seeds:
        cur = None
        for k in range(25):
            p = x0 if k == 0 else cur[0] + rng.normal(0, 0.05, 12)
            try:
                x, c2, _ = k2v.lm_fit(M, p, max_nfev=1500)
            except Exception:
                continue
            if cur is None or c2 < cur[1]:
                cur = (x, c2)
        if cur is not None and (best is None or cur[1] < best[1]):
            best = cur
    if best is None:
        continue
    # chi2 with the TRUE errors, split into theta23 and the rest
    Mt = k2v.Model(T, info["rnu"])
    pl, o, rho = Mt.pulls_full(best[0])
    c_rest = sum(v * v for k, v in pl.items() if k != "sin2_th23")
    print(f"sin2th23 pinned={s23}: model sin2th23={o['sin2_th23']:.4f}  chi2(other 17)={c_rest:.2f}  total(true errors)={c_rest + pl['sin2_th23']**2:.2f}  "
          f"max|pull| other={max(abs(v) for k, v in pl.items() if k != 'sin2_th23'):.2f}  t={time.time()-t0:.0f}s", flush=True)
    print("    pulls:", {k: round(v, 2) for k, v in pl.items()}, flush=True)
    out.append({"pin": s23, "x": list(map(float, best[0])), "sin2_th23_model": o["sin2_th23"], "chi2_other17": c_rest,
                "chi2_total_true": c_rest + pl["sin2_th23"]**2, "pulls": {k: float(v) for k, v in pl.items()}})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"profile23_{content}.json"), "w"), indent=1)
