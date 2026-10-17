import json, sys, time, math, numpy as np, fit
content, type2, scheme, nstart, seed, out = sys.argv[1], sys.argv[2] == "II", sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
inp = json.load(open("inputs_mz.json"))
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
R = fit.Runner(inp, vR, MU, content)
T = fit.build_targets(inp, 0.01) if scheme == "floor1" else fit.build_targets(inp, 0.0, lepton_floor=0.001)
P = fit.Proxy(R, T, type2=type2)
rng = np.random.default_rng(seed)
results = []
t0 = time.time()
for i in range(nstart):
    p0 = P.random_start(rng)
    try:
        r = fit.fit_proxy(P, p0)
    except Exception as e:
        print("start", i, "failed", repr(e)); continue
    results.append(r)
    best = min(x["chi2"] + x["penalty"] for x in results)
    print(f"start {i} chi2={r['chi2']:.3f} pen={r['penalty']:.2g} y10={r['ymax10_act']:.2f} y126={r['ymax126_act']:.2f} cd126={r['cd126']:.3g} best={best:.3f} t={time.time()-t0:.0f}s", flush=True)
results.sort(key=lambda x: x["chi2"] + x["penalty"])
json.dump({"content": content, "type2": type2, "scheme": scheme, "vR": vR, "MU": MU, "gauge": {k: (list(np.round(v, 5)) if isinstance(v, list) else float(v)) for k, v in R.gauge.items()},
           "targets_MU": {k: [float(a), float(b)] for k, (a, b) in P.TU.items()}, "rnu": P.bu["rnu"], "results": results}, open(out, "w"), indent=1)
print("done", len(results), "best", results[0]["chi2"], results[0]["penalty"])
