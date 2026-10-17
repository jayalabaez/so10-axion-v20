import json, sys, time, math, numpy as np, fit
s1file, ntop, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
kappa_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0   # robustness: rescale KAPPA_R (vev convention)
ymax = float(sys.argv[5]) if len(sys.argv) > 5 else 1.5
vR_override = float(sys.argv[6]) if len(sys.argv) > 6 else None
fit.KAPPA_R *= kappa_scale; fit.YMAX = ymax
s1 = json.load(open(s1file))
inp = json.load(open("inputs_mz.json"))
vR = vR_override or s1["vR"]
R = fit.Runner(inp, vR, s1["MU"], s1["content"])
T = fit.build_targets(inp, 0.01) if s1["scheme"] == "floor1" else fit.build_targets(inp, 0.0, lepton_floor=0.001)
P = fit.Proxy2(R, T, type2=s1["type2"])
res = []
t0 = time.time()
for i, r0 in enumerate(s1["results"][:ntop]):
    p0 = np.array(r0["x"])
    try:
        r = fit.fit_proxy(P, p0, full=True, max_nfev=3000)
    except Exception as e:
        print("refine", i, "failed", repr(e), flush=True); continue
    r["stage1_chi2"] = r0["chi2"]; r["stage1_penalty"] = r0["penalty"]
    res.append(r)
    print(f"refine {i}: stage1 {r0['chi2']:.2f}+{r0['penalty']:.2g} -> full chi2={r['chi2']:.3f} pen={r['penalty']:.2g} y10={r['ymax10_act']:.2f} y126={r['ymax126_act']:.2f} cd126={r['cd126']:.3g} nfev={r['nfev']} t={time.time()-t0:.0f}s", flush=True)
    print("   pulls:", {k: round(v, 2) for k, v in r["pulls"].items()}, flush=True)
res.sort(key=lambda x: x["chi2"] + x["penalty"])
json.dump({"source": s1file, "kappa_scale": kappa_scale, "ymax": ymax, "vR": vR, "MU": s1["MU"], "content": s1["content"], "type2": s1["type2"], "scheme": s1["scheme"], "results": res}, open(out, "w"), indent=1)
print("done best full chi2", res[0]["chi2"], res[0]["penalty"])
