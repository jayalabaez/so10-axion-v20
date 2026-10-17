"""Independent GLOBAL search in the exact chain (my code): CMA-ES from random starting means (W-parametrisation),
then TRF polish of each run's best.  usage: global_cma.py TAG KAPPA_LAM vR NRUNS LAMBDA GENS [floor] [seed]"""
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
# central GUT eigenvalues of Yd, Ye from the researcher's 3e12 point (only used to centre the d/e search box: these
# are just the data run up to M_U, varied +-0.15 dex per run)
pts = json.load(open(os.path.join(HERE, "their_points.json")))
p0 = [q for q in pts if q["tag"] == "vscan_fine" and abs(q["vR"] - 3e12) < 1][0]
X0 = O.gut_to_w(*S.unpack(np.array(p0["P"])[None]))[0]
de_c = X0[9:15].copy()
rng = np.random.default_rng(seed)
scale = np.array([0.6] * 4 + [1.0] * 5 + [0.04] * 6 + [0.12, 0.25, 0.8, 0.3])
out = []
outf = os.path.join(HERE, f"global_{tag}.json")
t0 = time.time()
for run in range(nruns):
    xc = np.zeros(19)
    xc[0:3] = rng.uniform(0, math.pi / 2, 3); xc[3] = rng.uniform(-math.pi, math.pi)
    xc[4:9] = rng.uniform(-math.pi, math.pi, 5)
    xc[9:15] = de_c + rng.normal(0, 0.08, 6)
    xc[15] = rng.uniform(1.2, 2.1); xc[16] = rng.uniform(-1.6, 0.1); xc[17] = rng.uniform(-math.pi, math.pi)
    xc[18] = rng.uniform(-3.2, -1.6)

    def fun(U):
        X = xc + U * scale
        return fit.chi2(X)
    (fb, ub), mfin = O.cmaes(fun, np.zeros(19), 1.0, lam=lam, gens=gens, rng=rng)
    xb = xc + ub * scale
    xp, cp = fit.polish(xb, nfev=150)
    out.append(dict(run=run, cma=fb, polished=cp, x=xp.tolist(), r=float(10**xp[15]), s_abs=float(10**xp[16]),
                    s_arg=float(xp[17]), lc=float(xp[18]), t=time.time() - t0))
    o = fit.last[0][0] if False else None
    print(f"run {run}: cma {fb:.2f} -> polish {cp:.2f}  r={10**xp[15]:.1f} |s|={10**xp[16]:.3f} arg={xp[17]:.2f} "
          f"lc={xp[18]:.2f}  t={time.time()-t0:.0f}s nev={m.nev}", flush=True)
    json.dump(out, open(outf, "w"), indent=1)
best = min(out, key=lambda e: e["polished"])
print("BEST", best["polished"], flush=True)
