"""Content / M_U / data sensitivity: re-polish the best exact points of a run_vr result under another setup.
usage: sens.py RESULT.json OUTTAG content MU [nu] [floor]
(exact batched model with the perturbativity penalty; TRF polish 400 evaluations of the Jacobian-based LS, then
 12 basin hops around the best re-polished point)."""
import sys, json, math, time
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L, model_r2c as M, bexact as B, search_r2c as S, td_refit as T

L.USE_RK4 = True; L.RK4_H = 0.5
J = json.load(open(sys.argv[1])); tag = sys.argv[2]; content = sys.argv[3]; MU = float(sys.argv[4])
nu = sys.argv[5] if len(sys.argv) > 5 else J["nu"]; floor = float(sys.argv[6]) if len(sys.argv) > 6 else J["floor"]
typeII = J["type"] == "II"
d = L.data_set(nu, floor)
setup = M.make_setup(J["vR"], d, content=content, MU=MU); tg = setup["targets"]
Ex = B.Exact(setup, tg, typeII, d)


def R(X):
    X = np.atleast_2d(X)
    try:
        with np.errstate(all="ignore"):
            r = Ex.resid(X)
        if r.shape[0] == len(X):
            return r
    except Exception:
        pass
    if len(X) == 1:
        return np.full((1, 20), 1e8)
    h = len(X) // 2
    return np.concatenate([R(X[:h]), R(X[h:])], 0)


def chi2(X):
    r = R(X); return np.sum(r * r, 1)


def jac(x, h=1e-6):
    n = len(x); X = np.tile(x, (n + 1, 1)); X[1:] += np.eye(n) * h
    r = R(X); return ((r[1:] - r[0]) / h).T


def polish(x0, nfev=400):
    try:
        res = least_squares(lambda x: R(x[None])[0], np.array(x0, float), jac=jac, method="trf", max_nfev=nfev,
                            xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
        x = res.x
    except Exception:
        x = np.array(x0, float)
    return x, float(chi2(x[None])[0])


out = []
t0 = time.time()
for r in J["exact_results"][:3]:
    z0 = np.array(r["z"])
    c0 = float(chi2(z0[None])[0])
    Z = np.tile(z0, (41, 1)); Z[:, -1] = np.linspace(-5, -1, 41)
    cs = chi2(Z); zs = Z[int(np.argmin(cs))] if cs.min() < c0 else z0
    x, c = polish(zs)
    out.append({"src": r["src"], "chi2_orig": r["chi2"], "chi2_new_setup_same_point": c0, "chi2_repolished": c, "z": x.tolist()})
    print(f"{r['src']}: orig {r['chi2']:.3f}  new-setup same point {c0:.3f}  repolished {c:.3f}  t={time.time()-t0:.0f}s", flush=True)
best = min(out, key=lambda o: o["chi2_repolished"])
rng = np.random.default_rng(7)
steps = np.full(len(best["z"]), 0.25); steps[9] = 0.05; steps[10] = 0.1; steps[-7:-1] = 0.03; steps[-1] = 0.2
cur = (best["chi2_repolished"], np.array(best["z"])); bst = cur
for k in range(12):
    xk, ck = polish(cur[1] + rng.normal(0, 1, len(steps)) * steps, 200)
    if ck < cur[0]:
        cur = (ck, xk)
    if ck < bst[0]:
        bst = (ck, xk)
print(f"BH best {bst[0]:.3f}", flush=True)
L.USE_RK4 = False
td = T.TD(setup, tg, typeII, d); td.tau = (1.0, 1.0)
try:
    rep = T.report_point(td, bst[1])
except Exception as e:
    rep = {"error": repr(e)}
res = {"src_file": sys.argv[1], "tag": tag, "vR": J["vR"], "content": content, "MU": MU, "nu": nu, "floor": floor,
       "orig_content": J["content"], "orig_MU": J["MU"], "points": out, "bh_best": bst[0], "report": rep}
json.dump(res, open(f"sens_{tag}_{J['vR']:.0e}_{content}.json", "w"), indent=1, default=str)
print(json.dumps({"tag": tag, "best": bst[0], "pulls": rep.get("pulls")}))
