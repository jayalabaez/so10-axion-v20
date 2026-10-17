"""chi2 WITHOUT the 1% mass theory floor, by floor continuation 1% -> 0.3% -> 0.1% -> 0.03% -> 0 from the best exact
points of a run_vr result (direct floor-0 TRF polishing from a floor-1% point can jump into the unphysical region,
because the charged-lepton errors are then 1e-5..1e-6 relative).
usage: floor0.py RESULT.json"""
import sys, json, time
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L, model_r2c as M, bexact as B, td_refit as T

L.USE_RK4 = True; L.RK4_H = 0.5
J = json.load(open(sys.argv[1]))
typeII = J["type"] == "II"
setup = None
res = []
for r in J["exact_results"][:4]:
    z = np.array(r["z"]); hist = []
    for fl in (0.01, 0.003, 0.001, 0.0003, 0.0):
        d = L.data_set(J["nu"], fl)
        if J.get("th23", "none") != "none":
            X, sg = [float(v) for v in J["th23"].split(",")]; d["sin2_th23"] = (X, sg)
        setup = M.make_setup(J["vR"], d, content=J["content"], MU=J["MU"]); tg = setup["targets"]
        Ex = B.Exact(setup, tg, typeII, d)

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

        def jac(x, h=1e-7):
            n = len(x); Xs = np.tile(x, (n + 1, 1)); Xs[1:] += np.eye(n) * h
            rr = R(Xs); return ((rr[1:] - rr[0]) / h).T
        c0 = float(np.sum(R(z[None])[0] ** 2))
        try:
            sol = least_squares(lambda x: R(x[None])[0], z, jac=jac, method="trf", max_nfev=300, xtol=1e-13, ftol=1e-13,
                                gtol=1e-13, x_scale="jac")
            c1 = float(np.sum(R(sol.x[None])[0] ** 2))
            if c1 < c0:
                z = sol.x
            else:
                c1 = c0
        except Exception:
            c1 = c0
        hist.append((fl, c0, c1))
    L.USE_RK4 = False
    td = T.TD(setup, setup["targets"], typeII, d); td.tau = (1.0, 1.0)
    try:
        rep = T.report_point(td, z)
    except Exception as e:
        rep = {"error": repr(e)}
    L.USE_RK4 = True
    res.append({"src": r["src"], "chi2_floor1": r["chi2"], "continuation": hist, "chi2_floor0": hist[-1][2], "report": rep})
    print(f"{r['src']}: " + " -> ".join(f"[{fl}] {a:.2f}->{b:.2f}" for fl, a, b in hist), flush=True)
best = min(res, key=lambda x: x["chi2_floor0"])
json.dump({"src_file": sys.argv[1], "results": res, "best_floor0": best["chi2_floor0"], "best_report": best["report"]},
          open(sys.argv[1].replace(".json", "_floor0.json"), "w"), indent=1, default=str)
print(json.dumps({"best_floor0": best["chi2_floor0"], "pulls": best["report"].get("pulls")}))
