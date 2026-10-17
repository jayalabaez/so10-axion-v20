"""Verifier: broad multi-start LM search of the researcher's proxy chi2 (Proxy2, 17 params, type I, T2 RG factors),
to test the claim that chi2 = 215.7 is an optimiser limit rather than a physics bound.
usage: multistart.py seed nstarts out.json
Strategy per start: structured random start -> charged-only LM -> joint LM with nu_weight ramp (0.1, 0.3, 1.0) -> LM polish.
Also: from each joint result below the running best*3, 6 perturbation hops.
"""
import json, math, sys, time, numpy as np, fit
seed, nstarts, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
inp = json.load(open("inputs_mz.json"))
R = fit.Runner(inp, 2.6e13, 2.13e16, "T2"); T = fit.build_targets(inp, 0.01)
P = fit.Proxy2(R, T, type2=False)
rng = np.random.default_rng(seed)
t0 = time.time()
best = None; allc = []
def better(a, b):
    return b is None or a["chi2"] + a["penalty"] < b["chi2"] + b["penalty"]
for i in range(nstarts):
    p0 = P.random_start(rng)
    try:
        r = fit.fit_proxy(P, p0, max_nfev=800, charged_only=True, method="lm")
        p1 = np.array(r["x"])
        # joint with ramp
        for w in (0.1, 0.3, 1.0):
            P.nu_weight = w
            rj = fit.fit_proxy(P, p1, max_nfev=1500, method="lm")
            p1 = np.array(rj["x"])
        P.nu_weight = 1.0
        rj = fit.fit_proxy(P, p1, max_nfev=1500, method="lm")
    except Exception as e:
        P.nu_weight = 1.0
        continue
    c = rj["chi2"] + rj["penalty"]; allc.append(c)
    if better(rj, best):
        best = rj
    # hops from promising results
    if best is not None and c < 3 * (best["chi2"] + best["penalty"]) + 50:
        for k in range(6):
            pk = np.array(rj["x"]) * (1 + 0.05 * rng.normal(size=P.n)) + 0.01 * rng.normal(size=P.n)
            try:
                rh = fit.fit_proxy(P, pk, max_nfev=1500, method="lm")
            except Exception:
                continue
            allc.append(rh["chi2"] + rh["penalty"])
            if better(rh, best):
                best = rh
    if i % 10 == 0 or c < 300:
        print(f"start {i} chi2={rj['chi2']:.2f} pen={rj['penalty']:.2g} | best={best['chi2']:.2f} pen={best['penalty']:.2g} "
              f"y126={best['ymax126_act']:.3f} cd126={best['cd126']:.3g} |s|={best['s'][0]:.3f} t={time.time()-t0:.0f}s", flush=True)
        json.dump({"seed": seed, "nstarts_done": i + 1, "best": best, "chi2_sorted": sorted(allc)[:40], "t": time.time() - t0},
                  open(out, "w"), indent=1)
json.dump({"seed": seed, "nstarts_done": nstarts, "best": best, "chi2_sorted": sorted(allc)[:40], "t": time.time() - t0},
          open(out, "w"), indent=1)
print("done best", best["chi2"], "pen", best["penalty"], "pulls", {k: round(v, 2) for k, v in best["pulls"].items()}, flush=True)
