import json, sys, time, math, numpy as np, fit
content, type2, scheme, nseed, seed, out = sys.argv[1], sys.argv[2] == "II", sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
inp = json.load(open("inputs_mz.json"))
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
R = fit.Runner(inp, vR, MU, content)
T = fit.build_targets(inp, 0.01) if scheme == "floor1" else fit.build_targets(inp, 0.0, lepton_floor=0.001)
P = fit.Proxy2(R, T, type2=type2)
rng = np.random.default_rng(seed)
t0 = time.time(); charged = []; joint = []
def log(*a):
    print(*a, flush=True)
for i in range(nseed):
    p0 = P.random_start(rng)
    try:
        r = fit.fit_proxy(P, p0, max_nfev=1500, charged_only=True, method="lm")
    except Exception as e:
        log("seed", i, "charged failed", repr(e)); continue
    if r["chi2"] > 1.0 or r["penalty"] > 1.0:
        continue
    charged.append(r)
    # joint continuation from this charged solution
    for cd in ([-3.0, -2.0, -1.0] if not type2 else [-2.5, -1.5]):
        p1 = np.array(r["x"]); p1[16] = cd
        if type2:
            p1[17] = rng.uniform(-12, -9); p1[18] = rng.uniform(0, 2 * math.pi)
        try:
            for w in (0.03, 0.3, 1.0):
                P.nu_weight = w
                rj = fit.fit_proxy(P, p1, max_nfev=2000)
                p1 = np.array(rj["x"])
            P.nu_weight = 1.0
        except Exception as e:
            P.nu_weight = 1.0; log("joint failed", repr(e)); continue
        rj["seed"] = i; rj["cd_start"] = cd
        joint.append(rj)
        best = min(x["chi2"] + x["penalty"] for x in joint)
        log(f"seed {i} cd0={cd} joint chi2={rj['chi2']:.3f} pen={rj['penalty']:.2g} y10={rj['ymax10_act']:.2f} y126={rj['ymax126_act']:.2f} cd126={rj['cd126']:.3g} | best={best:.3f} ncharged={len(charged)} t={time.time()-t0:.0f}s")
joint.sort(key=lambda x: x["chi2"] + x["penalty"])
# basin hopping around the top 5
hop = []
for b in joint[:5]:
    for k in range(12):
        p1 = np.array(b["x"]) * (1 + 0.1 * rng.normal(size=len(b["x"]))) + 0.05 * rng.normal(size=len(b["x"]))
        try:
            rj = fit.fit_proxy(P, p1, max_nfev=2000)
        except Exception:
            continue
        rj["hop_from"] = b["chi2"]; hop.append(rj)
        log(f"hop from {b['chi2']:.3f}: chi2={rj['chi2']:.3f} pen={rj['penalty']:.2g} y126={rj['ymax126_act']:.2f}")
allres = sorted(joint + hop, key=lambda x: x["chi2"] + x["penalty"])
json.dump({"content": content, "type2": type2, "scheme": scheme, "vR": vR, "MU": MU, "n_charged_solutions": len(charged), "nseed": nseed,
           "targets_MU": {k: [float(a), float(b)] for k, (a, b) in P.TU.items()}, "rnu": P.bu["rnu"], "results": allres[:60],
           "chi2_list": [x["chi2"] + x["penalty"] for x in allres]}, open(out, "w"), indent=1)
log("done", len(allres), "best", allres[0]["chi2"] if allres else None)
