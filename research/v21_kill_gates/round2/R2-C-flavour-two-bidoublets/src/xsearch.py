"""Search directly in the EXACT (batched) top-down model.
usage: xsearch.py TAG vR I|II nSeeds nDE nCMA [floor] [nu] [MU|auto] [content] [tcap|none] [mask]
 - seeds: the best nSeeds distinct proxy minima of campaign_main_<vR>_<type>.json (or campaign_<srcTag>...) mapped
   to the exact model (quark-sector transfer inversion) and polished by exact TRF;
 - nDE / nCMA independent random-start DE / CMA-ES runs on the exact model, each TRF-polished."""
import sys, os, json, math, time
import numpy as np
from scipy.optimize import least_squares, differential_evolution
import lib_r2c as L, model_r2c as M, search_r2c as S, bexact as B, mapping, td_refit as T

L.USE_RK4 = True; L.RK4_H = 0.5
tag = sys.argv[1]; vR = float(sys.argv[2]); typ = sys.argv[3]
nSeeds, nDE, nCMA = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
floor = float(sys.argv[7]) if len(sys.argv) > 7 else 0.01
nu = sys.argv[8] if len(sys.argv) > 8 else "nufit60_sk"
MU = float(sys.argv[9]) if len(sys.argv) > 9 and sys.argv[9] != "auto" else None
content = sys.argv[10] if len(sys.argv) > 10 else "C2"
tcap = float(sys.argv[11]) if len(sys.argv) > 11 and sys.argv[11] != "none" else None
maskkeys = sys.argv[12].split(",") if len(sys.argv) > 12 else None
srcfile = os.environ.get("R2C_SEEDFILE", f"campaign_main_{vR:.0e}_{typ}.json")
typeII = typ == "II"
d = L.data_set(nu, floor)
setup = M.make_setup(vR, d, MU=MU, content=content)
tg = setup["targets"]
Ex = B.Exact(setup, tg, typeII, d)
if maskkeys:
    Ex.mask = np.array([k in maskkeys for k in L.ALL_KEYS])


class XLay:
    def __init__(self, typeII):
        self.typeII = typeII; self.free = True
        self.n_core = 12 + (2 if typeII else 0); self.n = self.n_core + 6 + 1


class XProblem:
    def __init__(self):
        self.lay = XLay(typeII); self.nev = 0
        lo, hi = S.bounds(M.Layout(typeII=typeII))
        self.lo = np.concatenate([lo, [-0.3] * 6, [-4.5]]); self.hi = np.concatenate([hi, [0.3] * 6, [-1.0]])
        if tcap is not None:
            self.hi[12] = min(self.hi[12], tcap)

    def R(self, X):
        X = np.atleast_2d(X)
        self.nev += len(X)
        R = Ex.resid(X)
        if tcap is not None:
            ex = np.clip(X[:, 12] - tcap, 0, None)
            R = np.concatenate([R, 1e2 * ex[:, None]], 1)
        return R

    def chi2(self, X):
        R = self.R(X)
        return np.sum(R * R, 1)

    def resid(self, x):
        return self.R(x[None])[0]

    def jac(self, x, h=1e-6):
        n = len(x)
        X = np.tile(x, (n + 1, 1)); X[1:] += np.eye(n) * h
        R = self.R(X)
        return ((R[1:] - R[0]) / h).T


P = XProblem()


def polish(x0, nfev=300):
    try:
        r = least_squares(P.resid, np.array(x0, float), jac=lambda x: P.jac(x), method="trf", max_nfev=nfev, xtol=1e-12,
                          ftol=1e-12, gtol=1e-12, x_scale="jac")
        x = r.x
    except Exception:
        x = np.array(x0, float)
    x = S.wrap(np.concatenate([x[:-1], [x[-1]]]), XLay(typeII)) if False else x
    return x, float(P.chi2(x[None])[0])


log = open(f"xsearch_{tag}_{vR:.0e}_{typ}.log", "a")


def note(m):
    log.write(m + "\n"); log.flush()


note(f"== {tag} vR={vR:.1e} {typ} floor={floor} nu={nu} MU={setup['env']['MU']:.3e} content={content} tcap={tcap} mask={maskkeys} seeds<-{srcfile}")
results = []
t00 = time.time()
# 1. mapped proxy seeds
if nSeeds and os.path.exists(srcfile):
    J = json.load(open(srcfile))
    for j, m in enumerate(J["distinct_minima"][:nSeeds]):
        t0 = time.time()
        mp = mapping.proxy_to_exact(setup, tg, np.array(m["x"]), typeII=typeII, iters=12)
        if mp is None:
            note(f"  seed {j}: unphysical mapping"); continue
        z0 = np.concatenate([mp["x"], [mp["lc"]]])
        Z = np.tile(z0, (25, 1)); Z[:, -1] += np.linspace(-0.6, 0.6, 25)
        c = P.chi2(Z); z0 = Z[int(np.argmin(c))]
        x, cx = polish(z0, 400)
        results.append({"src": f"seed{j}", "proxy_chi2": m["chi2"], "chi2": cx, "z": list(map(float, x))})
        note(f"  seed {j}: proxy {m['chi2']:.2f} -> mapped {float(np.min(c)):.1f} -> exact polish {cx:.3f}  t={time.time()-t0:.0f}s")
# 2. random-start DE
rng = np.random.default_rng(abs(hash((tag, vR, typ, 'x'))) % (2**32))
bnds = list(zip(P.lo, P.hi))
for i in range(nDE):
    t0 = time.time()
    de = differential_evolution(lambda X: P.chi2(X.T), bnds, vectorized=True, updating="deferred", popsize=10, maxiter=300,
                                tol=0, atol=0, seed=int(rng.integers(0, 2**31 - 1)), polish=False, init="sobol",
                                mutation=(0.5, 1.0), recombination=0.9)
    x, cx = polish(de.x)
    results.append({"src": f"de{i}", "pre": float(de.fun), "chi2": cx, "z": list(map(float, x))})
    note(f"  DE {i}: {de.fun:.2f} -> polish {cx:.3f}  t={time.time()-t0:.0f}s")
# 3. random-start CMA-ES (IPOP x3)
for i in range(nCMA):
    t0 = time.time()
    best = (np.inf, None); mult = 3
    for k in range(3):
        b = S.cma_es(P, rng, max_evals=25000, lam_mult=mult)
        if b[0] < best[0]:
            best = b
        mult *= 2
    x, cx = polish(best[1])
    results.append({"src": f"cma{i}", "pre": float(best[0]), "chi2": cx, "z": list(map(float, x))})
    note(f"  CMA {i}: {best[0]:.2f} -> polish {cx:.3f}  t={time.time()-t0:.0f}s")
results.sort(key=lambda r: r["chi2"])
# full report of the best few (scalar exact chain, h=0.5)
reps = []
for r in results[:5]:
    z = np.array(r["z"])
    td = T.TD(setup, tg, typeII, d); td.tau = (1.0, 1.0)
    try:
        rec = T.report_point(td, z)
    except Exception as e:
        rec = {"error": repr(e)}
    rec["src"] = r["src"]; rec["chi2_batched"] = r["chi2"]
    reps.append(rec)
out = {"tag": tag, "vR": vR, "type": typ, "floor": floor, "nu": nu, "content": content, "tcap": tcap, "mask": maskkeys,
       "env": setup["env"], "results": results, "best_reports": reps, "n_eval": P.nev, "time_s": time.time() - t00,
       "summary": {"n": len(results), "min": results[0]["chi2"] if results else None,
                   "by_src": {s: min([r["chi2"] for r in results if r["src"].startswith(s)] or [None]) for s in ("seed", "de", "cma")}}}
json.dump(out, open(f"xsearch_{tag}_{vR:.0e}_{typ}.json", "w"), indent=1, default=str)
note(f"DONE best {results[0]['chi2']:.3f} ({results[0]['src']}) t={time.time()-t00:.0f}s")
