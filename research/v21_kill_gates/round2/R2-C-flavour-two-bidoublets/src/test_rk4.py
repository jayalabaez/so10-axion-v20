"""RK4 vs DOP853 accuracy and top-down refit test from a quick proxy minimum at v_R = 3e13."""
import math, time, json
import numpy as np
import lib_r2c as L, model_r2c as M, search_r2c as S, td_refit as T

d = L.data_set("nufit60_sk", 0.01)
setup = M.make_setup(3e13, d)
tg = setup["targets"]
lay = M.Layout()
P = S.Problem(lay, tg)
rng = np.random.default_rng(7)
best = None
for i in range(4):
    for c, x, _ in S.run_de(P, rng, 1):
        if best is None or c < best[0]:
            best = (c, x)
print("proxy best", best[0], flush=True)
_, _, aux = M.proxy_eval(best[1][None], lay, tg, want_obs=True)
lc0 = T.lc_guess(float(aux["rho_eff"][0]), 3e13)
xf = T.to_free(best[1], lay)
layf = M.Layout(free=True)
for flag, h in [(False, None), (True, 0.5)]:
    L.USE_RK4 = flag
    if h:
        L.RK4_H = h
    t0 = time.time()
    o = M.top_down(xf, layf, setup, tg, lc0, rtol=1e-10)
    dt = time.time() - t0
    print(f"RK4={flag} h={h}: t={dt:.3f}s m_u={o['m_u']:.6e} m_e={o['m_e']:.8e} m_t={o['m_t']:.6f} s13={o['s13']:.7f} "
          f"s2th23={o['sin2_th23']:.6f} dm31={o['dm31']:.6e}", flush=True)
L.USE_RK4 = True; L.RK4_H = 0.5
t0 = time.time()
res = T.refit(setup, tg, best[1], verbose=True)
rec = T.report_point(res["td"], res["z"])
print("top-down refit chi2", rec["chi2"], "max pull", rec["max_abs_pull"], f"t={time.time()-t0:.0f}s")
print({k: round(v, 2) for k, v in rec["pulls"].items()})
print({k: rec[k] for k in ("r", "s_abs", "s_arg", "c_d126", "comp", "Y10_act_max", "Y126_act_max", "M_R_GeV", "m_lightest_eV", "m_betabeta_eV", "delta_pmns_deg")})
