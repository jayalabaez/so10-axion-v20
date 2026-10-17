"""Exact-model v_R continuation scan: starting from the best exact points of the main runs, re-polish (full lc scan +
TRF + 8 basin hops) at each v_R of a finer grid; content per v_R as in the main assignment (C2 below 5e10, R813 up to
2e12, R622 above), M_U from R2-B.
usage: vscan.py OUTTAG vR1,vR2,... SRC1.json[,SRC2.json...]"""
import sys, json, math, time
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L, model_r2c as M, bexact as B, td_refit as T

L.USE_RK4 = True; L.RK4_H = 0.5
tag = sys.argv[1]; vRs = [float(v) for v in sys.argv[2].split(",")]; srcs = sys.argv[3].split(",")
starts = []
for f in srcs:
    J = json.load(open(f))
    for r in J["exact_results"][:3]:
        starts.append((f, r["src"], np.array(r["z"])))
d = L.data_set("nufit60_sk", 0.01)


def content_for(vR):
    return "C2" if vR < 5e10 else ("R813" if vR <= 2e12 else "R622")


out = []
for vR in vRs:
    c = content_for(vR); MU = L.R2B_NOMINAL[c][1]
    setup = M.make_setup(vR, d, content=c, MU=MU); tg = setup["targets"]
    Ex = B.Exact(setup, tg, False, d)

    def R(X):
        X = np.atleast_2d(X)
        try:
            with np.errstate(all="ignore"):
                rr = Ex.resid(X)
            if rr.shape[0] == len(X):
                return rr
        except Exception:
            pass
        if len(X) == 1:
            return np.full((1, 20), 1e8)
        h = len(X) // 2
        return np.concatenate([R(X[:h]), R(X[h:])], 0)

    def chi2(X):
        rr = R(X); return np.sum(rr * rr, 1)

    def jac(x, h=1e-6):
        n = len(x); Xs = np.tile(x, (n + 1, 1)); Xs[1:] += np.eye(n) * h
        rr = R(Xs); return ((rr[1:] - rr[0]) / h).T

    def polish(x0, nfev=300):
        try:
            sol = least_squares(lambda x: R(x[None])[0], np.array(x0, float), jac=jac, method="trf", max_nfev=nfev,
                                xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
            x = sol.x
        except Exception:
            x = np.array(x0, float)
        return x, float(chi2(x[None])[0])
    t0 = time.time(); res = []
    for f, s, z0 in starts:
        Z = np.tile(z0, (81, 1)); Z[:, -1] = np.linspace(-5, -1, 81)
        cs = chi2(Z); zs = Z[int(np.argmin(cs))]
        x, cx = polish(zs)
        res.append((cx, x, f + ":" + s))
    res.sort(key=lambda t: t[0])
    rng = np.random.default_rng(11)
    steps = np.full(len(res[0][1]), 0.25); steps[9] = 0.05; steps[10] = 0.1; steps[-7:-1] = 0.03; steps[-1] = 0.2
    cur = (res[0][0], res[0][1]); bst = cur
    for k in range(8):
        xk, ck = polish(cur[1] + rng.normal(0, 1, len(steps)) * steps, 200)
        if ck < cur[0]:
            cur = (ck, xk)
        if ck < bst[0]:
            bst = (ck, xk)
    L.USE_RK4 = False
    td = T.TD(setup, tg, False, d); td.tau = (1.0, 1.0)
    try:
        rep = T.report_point(td, bst[1])
    except Exception as e:
        rep = {"error": repr(e)}
    L.USE_RK4 = True
    rec = {"vR": vR, "content": c, "MU": MU, "chi2_min": bst[0], "start_chi2s": [t[0] for t in res], "best_start": res[0][2],
           "report": rep, "t": time.time() - t0}
    out.append(rec)
    pl = rep.get("pulls", {})
    print(f"vR={vR:.1e} {c} chi2={bst[0]:.3f} starts={[round(t[0], 1) for t in res]} th23pull={pl.get('sin2_th23', float('nan')):.2f} "
          f"fh={max(rep.get('fh_vR_sv', [float('nan')])):.3f} Y126act={rep.get('Y126_act_max', float('nan')):.3f} "
          f"M_R3={max(rep.get('M_R_GeV', [float('nan')])):.3g} t={time.time()-t0:.0f}s", flush=True)
    json.dump(out, open(f"vscan_{tag}.json", "w"), indent=1, default=str)
