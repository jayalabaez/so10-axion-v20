"""Exact top-down refits (LRG fixed point + exact TRF polish) of the best distinct proxy minima of a campaign file.
usage: refit_driver.py campaign.json K [polish_nfev] [floor_override]"""
import sys, json, math, time
import numpy as np
import lib_r2c as L, model_r2c as M, td_refit as T, lrg

L.USE_RK4 = True
src = sys.argv[1]
K = int(sys.argv[2])
polish = int(sys.argv[3]) if len(sys.argv) > 3 else 300
J = json.load(open(src))
vR = J["vR"]; typeII = J["type"] == "II"
floor = J["floor"] if len(sys.argv) <= 4 else float(sys.argv[4])
d = L.data_set(J["nu"], floor)
MU = None if J["env"].get("MU_status", "").startswith("g3=gL") or J["env"].get("MU_status") is None else J["env"]["MU"]
if J["env"].get("MU_status") == "given":
    MU = J["env"]["MU"]
setup = M.make_setup(vR, d, MU=MU, content=J.get("content", "C2"))
tg = setup["targets"]
lay_p = M.Layout(typeII=typeII)
out = {"src": src, "vR": vR, "type": J["type"], "floor": floor, "nu": J["nu"], "MU": setup["env"]["MU"], "refits": []}
tag = src.replace("campaign_", "refit_").replace(".json", "") + (f"_floor{floor}" if len(sys.argv) > 4 else "")
log = open(tag + ".log", "w")
for j, m in enumerate(J["distinct_minima"][:K]):
    t0 = time.time()
    x = np.array(m["x"])
    _, _, aux = M.proxy_eval(x[None], lay_p, tg, want_obs=True)
    rho = float(aux["rho_eff"][0])
    lc0 = T.lc_guess(rho, vR)
    xf = T.to_free(x, lay_p)
    # lc scan
    best = None
    for dl in np.linspace(-0.8, 0.8, 17):
        z = np.concatenate([xf, [lc0 + dl]])
        r, _ = lrg.exact_resid(setup, tg, M.Layout(typeII=typeII, free=True), d, z)
        c = float(np.sum(r**2))
        if best is None or c < best[0]:
            best = (c, z)
    try:
        zf, cf, hist = lrg.lrg_fit(setup, tg, best[1], typeII=typeII, data=d, iters=15, polish_nfev=polish)
        td = T.TD(setup, tg, typeII, d); td.tau = (1.0, 1.0)
        rec = T.report_point(td, zf)
    except Exception as e:
        rec = {"error": repr(e)}; cf = float("nan"); hist = []
    rec.update({"proxy_chi2": m["chi2"], "proxy_r": m["r"], "proxy_s_abs": m["s_abs"], "exact_chi2_at_start": best[0],
                "history": hist, "lc0": lc0, "time_s": time.time() - t0})
    out["refits"].append(rec)
    log.write(f"[{j}] proxy {m['chi2']:.3f} -> exact start {best[0]:.2f} -> refit {cf:.3f}  hist {[round(h,2) for h in hist]}  t={time.time()-t0:.0f}s\n")
    if "pulls" in rec:
        log.write("     pulls " + json.dumps({k: round(v, 2) for k, v in rec["pulls"].items()}) + "\n")
        log.write("     " + json.dumps({k: rec[k] for k in ("r", "s_abs", "s_arg", "c_d126", "Y10_act_max", "Y126_act_max", "M_R_GeV", "m_lightest_eV", "m_betabeta_eV", "delta_pmns_deg")}) + "\n")
    log.flush()
    json.dump(out, open(tag + ".json", "w"), indent=1)
log.close()
