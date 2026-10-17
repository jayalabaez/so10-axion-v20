"""R2-C v2 driver: global flavour fit at one v_R (proxy global search -> exact top-down global search + polish).

usage: run_vr.py TAG vR content I|II [--n 50] [--nx 6] [--seeds 10] [--floor 0.01] [--nu nufit60_sk] [--MU auto]
                 [--err std|lit] [--th23 none|X,sig] [--noproxy SRCJSON]

Stages
 P (proxy, batched GUT-scale model with bottom-up targets): DE, CMA-ES (IPOP x3), basin hopping, multi-start LM with
   neutrino-weight continuation -- n random starts each -- plus 3 literature/round-1 (r, s) seeds x 3 DE runs.
 X (exact, batched top-down chain M_U -> v_R -> M_Z, perturbativity penalty |Y_act| <= 1.5):
   (a) the best `seeds` distinct proxy minima mapped (quark-transfer inversion) and TRF-polished;
   (b) nx random-start DE and nx random-start CMA-ES runs directly on the exact model, TRF-polished;
   (c) basin hopping (12 hops) around the best two exact points.
 R (report): the best exact points re-evaluated with the independent scalar DOP853 chain (td_refit.report_point);
   floor-0 re-polish of the best 3 points.
"""
import sys, os, json, math, time, argparse
import numpy as np
from scipy.optimize import least_squares, differential_evolution
import lib_r2c as L, model_r2c as M, search_r2c as S, bexact as B, mapping, td_refit as T

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("vR", type=float); ap.add_argument("content"); ap.add_argument("typ")
ap.add_argument("--n", type=int, default=50); ap.add_argument("--nx", type=int, default=6)
ap.add_argument("--seeds", type=int, default=10); ap.add_argument("--floor", type=float, default=0.01)
ap.add_argument("--nu", default="nufit60_sk"); ap.add_argument("--MU", default="auto")
ap.add_argument("--err", default="std"); ap.add_argument("--th23", default="none")
ap.add_argument("--noproxy", default=None); ap.add_argument("--nbh", type=int, default=50)
ap.add_argument("--hops", type=int, default=12)
a = ap.parse_args()
L.USE_RK4 = True; L.RK4_H = 0.5
typeII = a.typ == "II"
MU = L.R2B_NOMINAL[a.content][1] if a.MU == "auto" else float(a.MU)
OUT = f"{a.tag}_{a.vR:.0e}_{a.content}_{a.typ}"
logf = open(OUT + ".log", "a")


def note(m):
    logf.write(m + "\n"); logf.flush()


# ---------------------------------------------------------------- data variants
def make_data():
    d = L.data_set(a.nu, a.floor)
    if a.err == "lit":
        # 'literature-era' error model (EST, recollection of Xing-Zhang-Zhou 2011/12 M_Z errors and PDG-2016-era CKM):
        # central values unchanged, relative errors inflated
        rel = {"m_u": 0.30, "m_d": 0.17, "m_s": 0.21, "m_c": 0.13, "m_b": 0.011, "m_t": 0.007,
               "m_e": 0.01, "m_mu": 0.01, "m_tau": 0.01}
        for k, rr in rel.items():
            c, s = d[k]
            d[k] = (c, c * max(rr, s / c))
        for k, fac in (("s12", 2.0), ("s23", 2.0), ("s13", 2.0), ("delta", 2.0)):
            c, s = d[k]; d[k] = (c, s * fac)
    if a.th23 != "none":
        X, sg = [float(v) for v in a.th23.split(",")]
        d["sin2_th23"] = (X, sg)
    return d


d = make_data()
setup = M.make_setup(a.vR, d, content=a.content, MU=MU)
tg = setup["targets"]
note(f"== {OUT} vR={a.vR:.2e} content={a.content} MU={MU:.3e} type={a.typ} floor={a.floor} nu={a.nu} err={a.err} th23={a.th23}"
     f" eta={tg.info['eta']} a^-1(vR)={np.round(setup['env']['alpha_inv_vR'], 3).tolist()} gBL={setup['env']['gBL_status']}")
t00 = time.time()

# ---------------------------------------------------------------- stage P
SEEDS = {"MummidiPatel2021_r77.4_s0.314-0.028i": (77.4, complex(0.314, -0.028)),
         "OP2019_r66_s0.39": (66.0, complex(0.39, 0.0)),
         "round1_skeptic_r63.7_s0.475": (63.7, 0.4753 * np.exp(0.0197j))}


def distinct(res, lay, tg, tol=0.05, nmax=25):
    out = []
    for c, x in sorted(((r[0], r[1]) for r in res), key=lambda t: t[0]):
        key = (10**x[9], 10**x[10], (x[11] + math.pi) % (2 * math.pi) - math.pi)
        if any(abs(o["chi2"] - c) < tol * max(1.0, 0.002 * c) and abs(o["r"] - key[0]) / key[0] < 0.01
               and abs(o["s_abs"] - key[1]) / max(key[1], 1e-6) < 0.01 for o in out):
            continue
        R, cc, aux = M.proxy_eval(x[None], lay, tg, want_obs=True)
        out.append({"chi2": float(c), "r": float(key[0]), "s_abs": float(key[1]), "s_arg": float(key[2]),
                    "x": list(map(float, x)), "pulls": {k: float(R[0, i]) for i, k in enumerate(L.ALL_KEYS)},
                    "rho_eff": float(aux["rho_eff"][0])})
        if len(out) >= nmax:
            break
    return out


proxy = None
if a.noproxy:
    proxy = json.load(open(a.noproxy))["proxy"]
    note(f"proxy stage skipped; seeds from {a.noproxy}")
else:
    lay = M.Layout(typeII=typeII)
    P = S.Problem(lay, tg)
    rng = np.random.default_rng(abs(hash((a.tag, a.vR, a.typ, a.content))) % (2**32))
    allres = {}; summ = {}
    for name, fn, n in [("de", S.run_de, a.n), ("cma", S.run_cma, a.n), ("bh", S.run_bh, a.nbh), ("ms_lm", S.run_ms_lm, a.n)]:
        t0 = time.time(); P.nev = 0; res = []
        for i in range(n):
            res += fn(P, rng, 1)
            if (i + 1) % 10 == 0 or i == n - 1:
                note(f"   P {name} {i+1}/{n}: best {min(r[0] for r in res):.3f}  t={time.time()-t0:.0f}s")
        allres[name] = res; summ[name] = S.summarize(res); summ[name]["nev"] = P.nev; summ[name]["t"] = time.time() - t0
        note(f"P {name}: " + json.dumps(summ[name]))
    seedres = []
    for sname, (r0, s0) in SEEDS.items():
        lo0, hi0 = P.lo.copy(), P.hi.copy()
        P.lo[9], P.hi[9] = math.log10(r0) - 0.004, math.log10(r0) + 0.004
        P.lo[10], P.hi[10] = math.log10(abs(s0)) - 0.004, math.log10(abs(s0)) + 0.004
        P.lo[11], P.hi[11] = np.angle(s0) - 0.01, np.angle(s0) + 0.01
        rr = S.run_de(P, rng, 3)
        P.lo, P.hi = lo0, hi0
        for c, x, cde in rr:
            x2, c2 = S.lm_polish(P, x)
            seedres.append((c2, x2, sname, cde))
        note(f"P seed {sname}: fixed-(r,s) DE {[round(t[2], 2) for t in rr]} -> free LM {[round(t[0], 2) for t in seedres[-3:]]}")
    allres["lit_seeds"] = [(c, x) for c, x, _, _ in seedres]
    pooled = [(r[0], r[1]) for k in allres for r in allres[k]]
    dist = distinct(pooled, lay, tg)
    proxy = {"summary": summ, "all_final_chi2": {k: sorted(float(r[0]) for r in v) for k, v in allres.items()},
             "seed_detail": [{"seed": nm, "chi2_fixed_rs_DE": float(cf), "chi2_free": float(c)} for c, x, nm, cf in seedres],
             "distinct_minima": dist, "min": dist[0]["chi2"]}
    note(f"P DONE best {dist[0]['chi2']:.3f} t={time.time()-t00:.0f}s")
    json.dump({"proxy": proxy}, open(OUT + "_proxy.json", "w"), indent=1)

# ---------------------------------------------------------------- stage X
Ex = B.Exact(setup, tg, typeII, d)


class XProblem:
    def __init__(self, Ex):
        self.Ex = Ex; self.nev = 0
        lo, hi = S.bounds(M.Layout(typeII=typeII))
        self.lo = np.concatenate([lo, [-0.3] * 6, [-5.0]]); self.hi = np.concatenate([hi, [0.3] * 6, [-1.0]])
        self.n = len(self.lo)
        self.lay = type("XL", (), {"n": self.n, "typeII": typeII, "free": True, "n_core": 12 + 2 * typeII})()

    def R(self, X):
        X = np.atleast_2d(X); self.nev += len(X)
        return self._safe(X)

    def _safe(self, X):
        try:
            with np.errstate(all="ignore"):
                R = self.Ex.resid(X)
            if R.shape[0] == len(X):
                return R
        except Exception:
            pass
        if len(X) == 1:
            return np.full((1, 20), 1e8)
        h = len(X) // 2
        return np.concatenate([self._safe(X[:h]), self._safe(X[h:])], 0)

    def chi2(self, X):
        R = self.R(X); return np.sum(R * R, 1)

    def resid(self, x):
        return self.R(x[None])[0]

    def jac(self, x, h=1e-6):
        n = len(x); X = np.tile(x, (n + 1, 1)); X[1:] += np.eye(n) * h
        R = self.R(X); return ((R[1:] - R[0]) / h).T


XP = XProblem(Ex)


def polish(x0, nfev=400, P=XP):
    try:
        r = least_squares(P.resid, np.array(x0, float), jac=lambda x: P.jac(x), method="trf", max_nfev=nfev,
                          xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
        x = r.x
    except Exception:
        x = np.array(x0, float)
    return x, float(P.chi2(x[None])[0])


xres = []
t0 = time.time()
for j, m in enumerate(proxy["distinct_minima"][:a.seeds]):
    tj = time.time()
    try:
        mp = mapping.proxy_to_exact(setup, tg, np.array(m["x"]), typeII=typeII, iters=12)
    except Exception as e:
        mp = None
    if mp is None:
        # fallback: identity map with lc scan
        x = np.array(m["x"]); zc = np.concatenate([x[:12 + 2 * typeII], np.zeros(6), [-2.0]])
    else:
        zc = np.concatenate([mp["x"], [mp["lc"]]])
    # lc scan over the FULL allowed range (at low v_R the mapped lc lies in the non-perturbative region)
    Z = np.tile(zc, (81, 1)); Z[:, -1] = np.linspace(XP.lo[-1], XP.hi[-1], 81)
    c = XP.chi2(Z); z0 = Z[int(np.argmin(c))]
    x, cx = polish(z0, 400)
    xres.append({"src": f"seed{j}", "proxy_chi2": m["chi2"], "mapped": float(np.min(c)), "chi2": cx, "z": list(map(float, x))})
    note(f"X seed {j}: proxy {m['chi2']:.2f} -> mapped {float(np.min(c)):.1f} -> polish {cx:.3f} t={time.time()-tj:.0f}s")
rng = np.random.default_rng(abs(hash((a.tag, a.vR, a.typ, a.content, "x"))) % (2**32))
bnds = list(zip(XP.lo, XP.hi))
for i in range(a.nx):
    tj = time.time()
    de = differential_evolution(lambda X: XP.chi2(X.T), bnds, vectorized=True, updating="deferred", popsize=10, maxiter=400,
                                tol=0, atol=0, seed=int(rng.integers(0, 2**31 - 1)), polish=False, init="sobol",
                                mutation=(0.5, 1.0), recombination=0.9)
    x, cx = polish(de.x)
    xres.append({"src": f"xde{i}", "pre": float(de.fun), "chi2": cx, "z": list(map(float, x))})
    note(f"X DE {i}: {de.fun:.2f} -> polish {cx:.3f} t={time.time()-tj:.0f}s")
# CMA-ES started at the current best exact point (normalised mean, sigma0 = 0.08): wide local-global refinement
# (random-start exact CMA-ES was tested in the smoke run and is ineffective: 7.6e3 -> 5.1e3)
xres.sort(key=lambda r: r["chi2"])
for i in range(a.nx):
    tj = time.time()
    zb = np.array(xres[min(i, len(xres) - 1)]["z"])
    m0 = np.clip((zb - XP.lo) / (XP.hi - XP.lo), 0.0, 1.0)
    b = S.cma_es(XP, rng, max_evals=20000, sigma0=0.08, lam_mult=3, m0=m0)
    x, cx = polish(b[1])
    xres.append({"src": f"xcma{i}", "pre": float(b[0]), "chi2": cx, "z": list(map(float, x)), "start": xres[min(i, len(xres) - 1)]["src"]})
    note(f"X CMA {i} (from {xres[min(i, len(xres) - 1)]['src']}): {b[0]:.2f} -> polish {cx:.3f} t={time.time()-tj:.0f}s")
# basin hopping around the best two
xres.sort(key=lambda r: r["chi2"])
steps = np.full(XP.n, 0.25); steps[9] = 0.05; steps[10] = 0.1; steps[-7:-1] = 0.03; steps[-1] = 0.2
for base in list(xres[:2]):
    cur = (base["chi2"], np.array(base["z"])); bst = cur; tj = time.time()
    for k in range(a.hops):
        xn = cur[1] + rng.normal(0, 1, XP.n) * steps
        xn = np.clip(xn, XP.lo - 0.5, XP.hi + 0.5)
        xk, ck = polish(xn, 200)
        if ck < cur[0] or rng.uniform() < math.exp(-min((ck - cur[0]) / 5.0, 700)):
            cur = (ck, xk)
        if ck < bst[0]:
            bst = (ck, xk)
    xres.append({"src": "xbh_" + base["src"], "chi2": bst[0], "z": list(map(float, bst[1]))})
    note(f"X BH from {base['src']} ({base['chi2']:.3f}): best {bst[0]:.3f} t={time.time()-tj:.0f}s")
xres.sort(key=lambda r: r["chi2"])
note(f"X DONE best {xres[0]['chi2']:.3f} ({xres[0]['src']}) t={time.time()-t0:.0f}s")

# ---------------------------------------------------------------- stage R
L.USE_RK4 = False      # independent scalar DOP853 chain for the report


def full_report(z, data):
    td = T.TD(setup, tg, typeII, data); td.tau = (1.0, 1.0)
    rec = T.report_point(td, np.array(z))
    Ex2 = B.Exact(setup, tg, typeII, data)
    Rb = Ex2.resid(np.array(z)[None])[0]
    rec["chi2_batched_rk4"] = float(np.sum(Rb**2)); rec["pert_resid"] = Rb[18:].tolist()
    rec["ymax_act_batched"] = Ex2.last_ymax[0].tolist()
    if typeII:
        # v_L: kappa_II(v_R) = tc * Y126(v_R); m_II = kappa v^2 = C_L v_L Y126  ->  v_L = tc v^2 / C_L (C_L = C_R, K2)
        rec["typeII_note"] = "t parameter = log10 |type-II/type-I| norm ratio at v_R (see bexact)"
        rec["log10_t"] = float(z[12])
    return rec


reports = []
L.USE_RK4 = True
for r in xres[:4]:
    L.USE_RK4 = False
    try:
        rec = full_report(r["z"], d)
    except Exception as e:
        rec = {"error": repr(e)}
    L.USE_RK4 = True
    rec["src"] = r["src"]; rec["chi2_search"] = r["chi2"]
    reports.append(rec)
# floor-0 re-polish
d0 = make_data() if a.floor == 0 else None
fl0 = []
if a.floor > 0:
    a_floor = a.floor; a.floor = 0.0; d0 = make_data(); a.floor = a_floor
    Ex0 = B.Exact(setup, tg, typeII, d0); XP0 = XProblem(Ex0)
    for r in xres[:3]:
        z0 = np.array(r["z"])
        c_start = float(XP0.chi2(z0[None])[0])
        x, cx = polish(z0, 400, P=XP0)
        L.USE_RK4 = False
        try:
            rec = full_report(x, d0)
        except Exception as e:
            rec = {"error": repr(e)}
        L.USE_RK4 = True
        fl0.append({"src": r["src"], "chi2_floor0_at_floor1_point": c_start, "chi2_floor0_repolished": cx, "report": rec})
        note(f"R floor0: {r['src']} floor1 {r['chi2']:.3f} -> floor0 at same point {c_start:.3f} -> repolished {cx:.3f}")
out = {"tag": a.tag, "vR": a.vR, "content": a.content, "MU": MU, "type": a.typ, "floor": a.floor, "nu": a.nu, "err": a.err,
       "th23": a.th23, "data": {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}, "env": setup["env"],
       "eta": tg.info["eta"], "proxy": proxy, "exact_results": xres, "exact_min": xres[0]["chi2"],
       "exact_by_src": {s: min([r["chi2"] for r in xres if r["src"].startswith(s)] or [None]) for s in ("seed", "xde", "xcma", "xbh")},
       "reports": reports, "floor0": fl0, "n_exact_eval": XP.nev, "time_s": time.time() - t00}
json.dump(out, open(OUT + ".json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
note(f"ALL DONE {OUT}: proxy min {proxy['min']:.3f}, exact min {xres[0]['chi2']:.3f}; t={time.time()-t00:.0f}s")
