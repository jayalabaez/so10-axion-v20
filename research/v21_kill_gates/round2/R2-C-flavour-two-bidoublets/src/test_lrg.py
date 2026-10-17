"""LRG consistency at the reference point and fixed-point refit from a proxy minimum."""
import math, time, json, sys
import numpy as np
import lib_r2c as L, model_r2c as M, search_r2c as S, td_refit as T, lrg

L.USE_RK4 = True
d = L.data_set("nufit60_sk", 0.01)
vR = float(sys.argv[1]) if len(sys.argv) > 1 else 3e13
setup = M.make_setup(vR, d)
tg = setup["targets"]
src = sys.argv[2] if len(sys.argv) > 2 else None
if src:
    J = json.load(open(src))
    xs = [np.array(m["x"]) for m in J["distinct_minima"][:int(sys.argv[3]) if len(sys.argv) > 3 else 3]]
    cs = [m["chi2"] for m in J["distinct_minima"]]
else:
    lay = M.Layout(); P = S.Problem(lay, tg); rng = np.random.default_rng(3)
    res = S.run_cma(P, rng, 2)
    best = min(res, key=lambda r: r[0]); xs = [best[1]]; cs = [best[0]]
lay = M.Layout()
for j, x in enumerate(xs):
    _, _, aux = M.proxy_eval(x[None], lay, tg, want_obs=True)
    lc0 = T.lc_guess(float(aux["rho_eff"][0]), vR)
    xf = T.to_free(x, lay)
    z = np.concatenate([xf, [lc0]])
    lr = lrg.LRG(setup, tg)
    t0 = time.time(); o_ex = lr.build(z); tb = time.time() - t0
    R, obs = lr.eval(z[None], want=True)
    dev = max(abs(obs[0, i] / o_ex[k] - 1) if k in L.MASS_KEYS or k in ("dm21", "dm31") else abs(obs[0, i] - o_ex[k])
              for i, k in enumerate(L.ALL_KEYS) if k != "delta")
    t0 = time.time()
    for _ in range(10):
        lr.eval(np.tile(z, (20, 1)))
    te = (time.time() - t0) / 200
    print(f"[{j}] proxy chi2 {cs[j]:.3f}: LRG-vs-exact max deviation at reference = {dev:.2e}  (build {tb:.2f}s, eval {te*1e6:.0f} us/pt)", flush=True)
    # lc scan
    best = None
    for dl in np.linspace(-0.8, 0.8, 17):
        zz = z.copy(); zz[-1] += dl
        r, _ = lrg.exact_resid(setup, tg, lr.lay, d, zz)
        c = float(np.sum(r**2))
        if best is None or c < best[0]:
            best = (c, zz)
    print(f"    exact chi2 at proxy point after lc scan: {best[0]:.2f}", flush=True)
    t0 = time.time()
    zf, cf, hist = lrg.lrg_fit(setup, tg, best[1], verbose=True, iters=15)
    print(f"    LRG fixed point: exact chi2 {cf:.3f}  hist {[round(h,2) for h in hist]}  t={time.time()-t0:.0f}s", flush=True)
    td = T.TD(setup, tg); td.tau = (1.0, 1.0)
    rec = T.report_point(td, zf)
    print("    pulls:", {k: round(v, 2) for k, v in rec["pulls"].items()})
    print("    ", {k: rec[k] for k in ("r", "s_abs", "s_arg", "c_d126", "Y10_act_max", "Y126_act_max", "M_R_GeV", "m_lightest_eV", "m_betabeta_eV", "delta_pmns_deg")})
