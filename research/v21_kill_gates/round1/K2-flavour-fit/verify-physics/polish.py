"""Polish proxy solutions with the six d/e masses released (18 residuals, 18 params + analytic rho), basin hopping.
usage: polish.py content in.json [nrec] [nhop]"""
import sys, os, json, math, time, numpy as np, k2v
content, fin = sys.argv[1], sys.argv[2]
nrec = int(sys.argv[3]) if len(sys.argv) > 3 else 5; nhop = int(sys.argv[4]) if len(sys.argv) > 4 else 40
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
T, info, _ = k2v.build_targets(vR, MU, content)
Mf = k2v.Model(T, info["rnu"], free_masses=True)
rng = np.random.default_rng(0)
w = json.load(open(fin)); recs = w["records"][:nrec]
out = []; t0 = time.time()
for rec in recs:
    x = np.concatenate([np.array(rec["x"]), np.zeros(6)]) if len(rec["x"]) == 12 else np.array(rec["x"])
    best = (x, Mf.chi2(x))
    for k in range(nhop):
        p = best[0] if k == 0 else best[0] + rng.normal(0, 0.03, Mf.n)
        try:
            xk, ck, _ = k2v.lm_fit(Mf, p, max_nfev=3000)
        except Exception:
            continue
        if ck < best[1] - 1e-9:
            best = (xk, ck)
    r = k2v.result_record(Mf, best[0], vR, rec.get("label", "") + "_free")
    print(f"{rec.get('label','')}: pinned chi2_18={rec['chi2_18']:.3f} -> free {r['chi2_18']:.3f} max|pull|={r['max_abs_pull']:.2f} t={time.time()-t0:.0f}s", flush=True)
    print("   pulls:", {k: round(v, 2) for k, v in r["pulls"].items()}, flush=True)
    print("   comp:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in r["comp"].items()}, flush=True)
    out.append(r)
out.sort(key=lambda z: z["chi2_18"])
json.dump({"content": content, "vR": vR, "MU": MU, "records": out, "info": info}, open(fin.replace(".json", "_free.json"), "w"), indent=1)
