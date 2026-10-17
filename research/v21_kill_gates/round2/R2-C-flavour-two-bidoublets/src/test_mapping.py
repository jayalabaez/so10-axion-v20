import math, time, json, sys
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L, model_r2c as M, td_refit as T, lrg, mapping

L.USE_RK4 = True
d = L.data_set("nufit60_sk", 0.01)
vR = 3e13
setup = M.make_setup(vR, d); tg = setup["targets"]
J = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "campaign_seedtest_3e+13_I.json"))
x = np.array(J["distinct_minima"][0]["x"]); print("proxy chi2", J["distinct_minima"][0]["chi2"])
# W-decomposition self-test
Wt = M.W_batch(np.array([[0.3, 0.1, 0.7, 1.1, 0.4, -0.9, 2.0, -1.3, 0.2, 1, 0, 0]]))[0]
p, e = mapping.w_decompose(Wt); print("W decompose self-test err", e)
t0 = time.time()
mp = mapping.proxy_to_exact(setup, tg, x, verbose=True)
print("mapped: inverse err", mp["inverse_rel_err"], "w_err", mp["w_err"], f"t={time.time()-t0:.1f}s")
lay = M.Layout(free=True)
best = None
for dl in np.linspace(-0.4, 0.4, 17):
    z = np.concatenate([mp["x"], [mp["lc"] + dl]])
    r, o = lrg.exact_resid(setup, tg, lay, d, z)
    c = float(np.sum(r**2))
    if best is None or c < best[0]:
        best = (c, z, r)
print("exact chi2 at mapped point (lc scan):", round(best[0], 2), "dlc", best[1][-1] - mp["lc"])
print("  pulls", {k: round(float(best[2][i]), 2) for i, k in enumerate(L.ALL_KEYS)})
t0 = time.time()
zf, cf, hist = lrg.lrg_fit(setup, tg, best[1], verbose=True, iters=20, polish_nfev=0)
print(f"LRG fixed point: {cf:.3f} hist {[round(h,2) for h in hist]} t={time.time()-t0:.0f}s", flush=True)
t0 = time.time()
sol = least_squares(lambda zz: lrg.exact_resid(setup, tg, lay, d, zz)[0], zf, method="trf", max_nfev=600, xtol=1e-12,
                    ftol=1e-12, gtol=1e-12, x_scale="jac", diff_step=1e-7)
r, o = lrg.exact_resid(setup, tg, lay, d, sol.x)
print(f"exact TRF polish: {float(np.sum(r**2)):.3f}  nfev={sol.nfev} t={time.time()-t0:.0f}s")
td = T.TD(setup, tg); td.tau = (1.0, 1.0)
rec = T.report_point(td, sol.x)
print("pulls", {k: round(v, 2) for k, v in rec["pulls"].items()})
print({k: rec[k] for k in ("r", "s_abs", "s_arg", "c_d126", "comp", "Y10_act_max", "Y126_act_max", "M_R_GeV", "m_lightest_eV", "m_betabeta_eV", "delta_pmns_deg")})
json.dump({"z": list(map(float, sol.x)), "rec": rec}, open("test_mapping_result.json", "w"), indent=1, default=str)
