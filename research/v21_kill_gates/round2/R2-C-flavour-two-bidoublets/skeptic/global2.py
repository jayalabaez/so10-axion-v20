"""Staged independent global search in the exact chain (my code).
Stage 1: CMA-ES on the 13 charged-fermion observables only (masses + CKM) from random means (W-param).
Stage 2: full 18-observable fit: lc scan + TRF polish + a few hops, from every stage-1 solution with chi2_13 < 60.
usage: global2.py TAG KAPPA_LAM vR NRUNS LAMBDA GENS [floor] [seed]"""
import sys, os, json, math, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skchain as S, skopt as O

tag = sys.argv[1]; S.KAPPA_LAM = float(sys.argv[2]); vR = float(sys.argv[3]); nruns = int(sys.argv[4])
lam = int(sys.argv[5]); gens = int(sys.argv[6]); floor = float(sys.argv[7]) if len(sys.argv) > 7 else 0.01
seed = int(sys.argv[8]) if len(sys.argv) > 8 else 7
c = "C2" if vR < 5e10 else ("R813" if vR <= 2e12 else "R622"); MU = S.MU_NOMINAL[c]
d = S.dataset(floor)
env = S.Env(vR, c, MU, d)
m = S.Model(env, d, **dict(h_g=0.5, h_hi=0.1, h_lo=0.5))
fit = O.Fit(m, "W")
fitc = O.Fit(m, "W"); fitc.mask = np.array([1.0] * 13 + [0.0] * 5)
pts = json.load(open(os.path.join(HERE, "their_points.json")))
p0 = [q for q in pts if q["tag"] == "vscan_fine" and abs(q["vR"] - 3e12) < 1][0]
X0 = O.gut_to_w(*S.unpack(np.array(p0["P"])[None]))[0]
de_c = X0[9:15].copy()
rng = np.random.default_rng(seed)
scale = np.array([0.6] * 4 + [1.0] * 5 + [0.04] * 6 + [0.12, 0.25, 0.8, 0.3])
out = []
outf = os.path.join(HERE, f"global2_{tag}.json")
t0 = time.time()
for run in range(nruns):
    xc = np.zeros(19)
    xc[0:3] = rng.uniform(0, math.pi / 2, 3); xc[3] = rng.uniform(-math.pi, math.pi)
    xc[4:9] = rng.uniform(-math.pi, math.pi, 5)
    xc[9:15] = de_c + rng.normal(0, 0.08, 6)
    xc[15] = rng.uniform(1.2, 2.1); xc[16] = rng.uniform(-1.6, 0.1); xc[17] = rng.uniform(-math.pi, math.pi)
    xc[18] = rng.uniform(-3.2, -1.6)

    def fun(U):
        return fitc.chi2(xc + U * scale)
    (fb, ub), _ = O.cmaes(fun, np.zeros(19), 1.0, lam=lam, gens=gens, rng=rng)
    x1 = xc + ub * scale
    x1p, c13 = fitc.polish(x1, nfev=80)
    rec = dict(run=run, chi2_13_cma=fb, chi2_13=c13, r=float(10**x1p[15]), s_abs=float(10**x1p[16]), s_arg=float(x1p[17]))
    if c13 < 60:
        Z = np.tile(x1p, (61, 1)); Z[:, 18] = np.linspace(-4.0, -1.0, 61)
        cs = fit.chi2(Z); j = int(np.argmin(cs))
        x2, c2 = fit.polish(Z[j], nfev=200)
        cur = (c2, x2)
        steps = np.full(19, 0.1); steps[9:15] = 0.02; steps[15] = 0.02; steps[16] = 0.04; steps[17] = 0.1; steps[18] = 0.05
        for k in range(3):
            xk, ck = fit.polish(cur[1] + rng.normal(0, 1, 19) * steps, 120)
            if ck < cur[0]:
                cur = (ck, xk)
        R = fit.resid(cur[1][None])[0]
        rec.update(chi2_18=cur[0], x=cur[1].tolist(), r18=float(10**cur[1][15]), s18=[float(10**cur[1][16]), float(cur[1][17])],
                   th23=float(fit.last[0][0, 14]), pulls={k: float(R[i]) for i, k in enumerate(S.KEYS)})
    rec["t"] = time.time() - t0
    out.append(rec)
    print(f"run {run}: chi2_13 {fb:.2f}->{c13:.2f} r={rec['r']:.1f} |s|={rec['s_abs']:.3f} arg={rec['s_arg']:.2f} "
          f"chi2_18={rec.get('chi2_18', float('nan')):.2f} th23={rec.get('th23', float('nan')):.3f} t={rec['t']:.0f}s", flush=True)
    json.dump(out, open(outf, "w"), indent=1)
ok = [e for e in out if "chi2_18" in e]
print("BEST", min(e["chi2_18"] for e in ok) if ok else None, flush=True)
