"""DE global search with staged error inflation and optional warm start, then LM polish and basin hopping.
usage: de_run2.py I|II seed popsize maxiter inflate content scheme [warm.json] [vR MU]
"""
import json, time, math, sys, numpy as np, fit
from scipy.optimize import differential_evolution
mode, seed, popsize, maxiter, inflate = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
content = sys.argv[6] if len(sys.argv) > 6 else "T2"; scheme = sys.argv[7] if len(sys.argv) > 7 else "floor1"
warm = sys.argv[8] if len(sys.argv) > 8 and sys.argv[8] != "-" else None
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
if len(sys.argv) > 10:
    vR, MU = float(sys.argv[9]), float(sys.argv[10])
inp = json.load(open("inputs_mz.json")); R = fit.Runner(inp, vR, MU, content)
T = fit.build_targets(inp, 0.01) if scheme == "floor1" else fit.build_targets(inp, 0.0, lepton_floor=0.001)
type2 = mode == "II"
P = fit.Proxy2(R, T, type2=type2)
FS = 3e-3
def unpack(q):
    p = np.zeros(P.n); p[0:12] = q[0:12] * FS
    p[12] = 10 ** q[12]; p[13] = q[13]; p[14] = 10 ** q[14]; p[15] = q[15]; p[16] = q[16]
    if type2:
        p[17] = q[17]; p[18] = q[18]
    return p
def pack(p):
    q = np.zeros(P.n); q[0:12] = p[0:12] / FS
    q[12] = math.log10(p[12]); q[13] = p[13]; q[14] = math.log10(p[14]); q[15] = p[15]; q[16] = p[16]
    if type2:
        q[17] = p[17]; q[18] = p[18]
    return q
nobs = 18
def obj(q):
    r = P.residuals(unpack(q))[0]
    return float(np.sum(r[:nobs]**2) / inflate**2 + np.sum(r[nobs:]**2))
bounds = [(-3, 3)] * 12 + [(1.0, 2.6), (-math.pi, math.pi), (-2.0, 1.5), (-math.pi, math.pi), (-4.0, -1.5)]
if type2:
    bounds += [(-12.5, -8.5), (-math.pi, math.pi)]
rng = np.random.default_rng(seed)
init = "latinhypercube"
if warm:
    w = json.load(open(warm)); q0 = pack(np.array(w["x"]))
    pop = np.array([np.clip(q0 * (1 + 0.05 * rng.normal(size=len(q0))) + 0.02 * rng.normal(size=len(q0)), [b[0] for b in bounds], [b[1] for b in bounds]) for _ in range(popsize * len(bounds))])
    pop[0] = q0; init = pop
t0 = time.time()
de = differential_evolution(obj, bounds, seed=seed, popsize=popsize, maxiter=maxiter, tol=1e-12, mutation=(0.5, 1.0), recombination=0.9, init=init, polish=False)
print("DE chi2(inflated)", de.fun, "nfev", de.nfev, "t", round(time.time() - t0), flush=True)
best = None
p1 = unpack(de.x)
for k in range(25):
    pk = p1 if k == 0 else np.array(best["x"]) * (1 + 0.03 * rng.normal(size=P.n)) + 0.01 * rng.normal(size=P.n)
    try:
        r = fit.fit_proxy(P, pk, max_nfev=4000, method="lm")
    except Exception as e:
        continue
    if best is None or r["chi2"] + r["penalty"] < best["chi2"] + best["penalty"]:
        best = r
print("LM polish+hop chi2", best["chi2"], "pen", best["penalty"], "y10", best["ymax10_act"], "y126", best["ymax126_act"], "cd126", best["cd126"], flush=True)
print("pulls", {k: round(v, 2) for k, v in best["pulls"].items()})
best.update({"de_chi2_inflated": float(de.fun), "nfev_de": int(de.nfev), "popsize": popsize, "maxiter": maxiter, "inflate": inflate,
             "content": content, "scheme": scheme, "type2": type2, "vR": vR, "MU": MU, "seed": seed, "warm": warm})
json.dump(best, open(f"de2_{mode}_{content}_{scheme}_{seed}.json", "w"), indent=1)
