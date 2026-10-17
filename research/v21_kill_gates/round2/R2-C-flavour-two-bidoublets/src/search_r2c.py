"""Global optimisers on the batched GUT-scale proxy: multi-start LM, differential evolution, CMA-ES, basin hopping.
Every optimiser ends with the same LM polish, so the final chi2 values are comparable."""
import math, time, json, sys
import numpy as np
from scipy.optimize import least_squares, differential_evolution
import lib_r2c as L
import model_r2c as M

PI = math.pi


def bounds(lay):
    lo = [0, 0, 0, -PI, -PI, -PI, -PI, -PI, -PI, 0.0, -3.0, -PI]
    hi = [PI / 2, PI / 2, PI / 2, PI, PI, PI, PI, PI, PI, 3.0, 2.0, PI]
    if lay.typeII:
        lo += [-5.0, -PI]; hi += [2.0, PI]
    if lay.free:
        lo += [-0.15] * 6; hi += [0.15] * 6
    return np.array(lo, float), np.array(hi, float)


PERIODIC_CORE = [3, 4, 5, 6, 7, 8, 11]


def periodic_mask(lay):
    m = np.zeros(lay.n, bool)
    m[PERIODIC_CORE] = True
    if lay.typeII:
        m[13] = True
    return m


def wrap(x, lay):
    x = np.array(x, float)
    pm = periodic_mask(lay)
    x[pm] = (x[pm] + PI) % (2 * PI) - PI
    return x


class Problem:
    def __init__(self, lay, tg, penalty=None):
        self.lay = lay; self.tg = tg; self.nev = 0
        self.lo, self.hi = bounds(lay)
        self.penalty = penalty           # optional callable(X) -> (N,) extra chi2
        self.w = np.ones(18)             # residual weights (continuation: neutrino weight ramp)
        self.tcap = None                 # type II: cap on log10|t| (penalty residual 1e2 * excess)
        self.mask = None                 # optional boolean mask of residuals to drop (e.g. theta23-free fit)

    def set_nu_weight(self, wnu):
        self.w = np.ones(18); self.w[13:18] = wnu

    def chi2(self, X):
        X = np.atleast_2d(X)
        self.nev += X.shape[0]
        R = self._R(X)
        c = np.sum(R**2, axis=1)
        if self.penalty is not None:
            c = c + self.penalty(X)
        return c

    def _R(self, X):
        R, _ = M.proxy_eval(X, self.lay, self.tg)
        R = R * self.w
        if self.mask is not None:
            R = R * (~self.mask)
        if self.tcap is not None:
            ex = np.clip(X[:, 12] - self.tcap, 0, None)
            R = np.concatenate([R, 1e2 * ex[:, None]], 1)
        return R

    def resid(self, x):
        self.nev += 1
        return self._R(x[None])[0]

    def jac(self, x, h=1e-6):
        n = len(x)
        X = np.tile(x, (n + 1, 1))
        X[1:] += np.eye(n) * h
        R = self._R(X)
        self.nev += n + 1
        return ((R[1:] - R[0]) / h).T


def lm_polish(P, x0, max_nfev=1500, tol=1e-11):
    x0 = np.array(x0, float)
    try:
        r = least_squares(P.resid, x0, jac=lambda x: P.jac(x), method="lm", max_nfev=max_nfev, xtol=tol, ftol=tol,
                          gtol=tol, x_scale="jac")
        x = r.x
    except Exception:
        x = x0
    x = wrap(x, P.lay)
    c = float(P.chi2(x[None])[0])
    return x, c


def lm_continuation(P, x0, ramp=(0.0, 0.03, 0.1, 0.3, 1.0)):
    """Charged-sector fit first, then ramp the neutrino weight to 1 (as in the round-1 skeptic multistart)."""
    x = np.array(x0, float)
    for wn in ramp:
        P.set_nu_weight(wn)
        x, c = lm_polish(P, x, max_nfev=800 if wn < 1 else 2000)
    P.set_nu_weight(1.0)
    c = float(P.chi2(x[None])[0])
    return x, c


def random_start(P, rng):
    """Uniform in the box, except W angles drawn from the U(3) Haar measure (s12^2, c13^4, s23^2 uniform)."""
    x = rng.uniform(P.lo, P.hi)
    x[0] = math.asin(math.sqrt(rng.uniform()))
    x[1] = math.acos(rng.uniform()**0.25)
    x[2] = math.asin(math.sqrt(rng.uniform()))
    return x


def run_ms_lm(P, rng, nstart, continuation=True):
    res = []
    for i in range(nstart):
        x0 = random_start(P, rng)
        x, c = lm_continuation(P, x0) if continuation else lm_polish(P, x0)
        res.append((c, x))
    return res


def run_de(P, rng, nstart, popsize=20, maxiter=1000):
    res = []
    bnds = list(zip(P.lo, P.hi))
    f = lambda X: P.chi2(X.T)
    for i in range(nstart):
        seed = int(rng.integers(0, 2**31 - 1))
        de = differential_evolution(f, bnds, vectorized=True, updating="deferred", popsize=popsize, maxiter=maxiter,
                                    tol=0, atol=0, seed=seed, polish=False, init="sobol", mutation=(0.5, 1.0),
                                    recombination=0.9)
        x, c = lm_polish(P, de.x)
        res.append((c, x, float(de.fun)))
    return res


def cma_es(P, rng, max_evals=40000, sigma0=0.4, lam_mult=3, m0=None):
    """Plain (mu/mu_w, lambda)-CMA-ES in box-normalised coordinates; periodic coords wrapped, others mirrored."""
    n = P.lay.n
    lo, hi = P.lo, P.hi
    width = hi - lo
    pm = periodic_mask(P.lay)
    lam = lam_mult * (4 + int(3 * math.log(n)))
    mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum()
    mueff = 1 / np.sum(w**2)
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3)**2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2)**2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    m = rng.uniform(0, 1, n) if m0 is None else np.array(m0, float); sigma = sigma0
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); B = np.eye(n); D = np.ones(n)
    best = (np.inf, None); ev = 0; it = 0
    while ev < max_evals:
        it += 1
        Z = rng.standard_normal((lam, n))
        Y = Z @ (B * D).T
        Xn = m + sigma * Y
        Xc = Xn.copy()
        # boundary handling in normalised coords
        Xc[:, pm] = Xc[:, pm] % 1.0
        nb = ~pm
        Xm = Xc[:, nb]
        Xm = np.abs(Xm); Xm = np.where(Xm > 1, 2 - Xm, Xm); Xm = np.clip(Xm, 0, 1)
        Xc[:, nb] = Xm
        f = P.chi2(lo + Xc * width); ev += lam
        # penalise mirrored distance slightly to keep the mean inside
        f = f + 1e-3 * np.sum((Xn[:, nb] - Xc[:, nb])**2, axis=1)
        idx = np.argsort(f)
        if f[idx[0]] < best[0]:
            best = (float(f[idx[0]]), lo + Xc[idx[0]] * width)
        Ysel = Y[idx[:mu]]
        m_old = m
        m = m + sigma * (w @ Ysel)
        zmean = w @ Z[idx[:mu]]
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (B @ zmean)
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs)**(2 * it)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (w @ Ysel)
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C) + cmu * (Ysel.T * w) @ Ysel
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        if it % 5 == 0:
            C = np.triu(C) + np.triu(C, 1).T
            Dv, B = np.linalg.eigh(C)
            D = np.sqrt(np.clip(Dv, 1e-20, None))
        if sigma * D.max() < 1e-7:
            break
    return best


def run_cma(P, rng, nstart, max_evals=200000, ipop=3):
    """IPOP-style: `ipop` restarts with doubled population (lambda = 36, 72, 144 for n = 12) inside each start's budget;
    each restart from a fresh random mean."""
    res = []
    for i in range(nstart):
        best = (np.inf, None); mult = 3
        for k in range(ipop):
            b = cma_es(P, rng, max_evals=max_evals // ipop, lam_mult=mult)
            if b[0] < best[0]:
                best = b
            mult *= 2
        x, c = lm_polish(P, best[1])
        res.append((c, x, best[0]))
    return res


def run_bh(P, rng, nstart, nhop=25, T0=200.0, T1=2.0):
    """Monte-Carlo basin hopping with LM local minimisation and an annealed temperature T0 -> T1."""
    res = []
    steps = np.full(P.lay.n, 0.35); steps[9] = 0.15; steps[10] = 0.3
    if P.lay.free:
        steps[P.lay.n_core:] = 0.03
    for i in range(nstart):
        x, c = lm_polish(P, random_start(P, rng))
        cur = (c, x); best = (c, x)
        for k in range(nhop):
            T = T0 * (T1 / T0)**(k / max(nhop - 1, 1))
            xn = cur[1] + rng.normal(0, 1, P.lay.n) * steps
            xn = np.clip(xn, P.lo - 0.5 * (P.hi - P.lo) * (~periodic_mask(P.lay)), P.hi + 0.5 * (P.hi - P.lo) * (~periodic_mask(P.lay)))
            xk, ck = lm_polish(P, xn, max_nfev=1000)
            if ck < cur[0] or rng.uniform() < math.exp(-min((ck - cur[0]) / T, 700)):
                cur = (ck, xk)
            if ck < best[0]:
                best = (ck, xk)
        res.append((best[0], best[1]))
    return res


def summarize(res):
    c = np.array([r[0] for r in res])
    return {"n": len(res), "min": float(c.min()), "median": float(np.median(c)), "q10": float(np.quantile(c, 0.1)),
            "n_within_1_of_min": int(np.sum(c < c.min() + 1.0)), "n_within_10pct": int(np.sum(c < 1.1 * c.min()))}
