import time, sys, json, math
import numpy as np
import lib_r2c as L, model_r2c as M, search_r2c as S

vR = float(sys.argv[1]) if len(sys.argv) > 1 else 3e13
typeII = len(sys.argv) > 2 and sys.argv[2] == "II"
d = L.data_set("nufit60_sk", 0.01)
setup = M.make_setup(vR, d)
tg = setup["targets"]
lay = M.Layout(typeII=typeII)
P = S.Problem(lay, tg)
rng = np.random.default_rng(1)
for name, fn, kw in [("ms_lm", S.run_ms_lm, dict(nstart=10)), ("de", S.run_de, dict(nstart=2)),
                     ("cma", S.run_cma, dict(nstart=2)), ("bh", S.run_bh, dict(nstart=2, nhop=10))]:
    t0 = time.time(); P.nev = 0
    res = fn(P, rng, **kw)
    cs = sorted(r[0] for r in res)
    print(f"{name}: t={time.time()-t0:.1f}s nev={P.nev} chi2 sorted: {[round(c,1) for c in cs]}", flush=True)
    best = min(res, key=lambda r: r[0])
    R, c, aux = M.proxy_eval(best[1][None], lay, tg, want_obs=True)
    print("   pulls:", {k: round(float(R[0, i]), 2) for i, k in enumerate(L.ALL_KEYS) if abs(R[0, i]) > 0.5},
          " r=%.1f |s|=%.3f args=%.3f" % (10**best[1][9], 10**best[1][10], best[1][11]))
