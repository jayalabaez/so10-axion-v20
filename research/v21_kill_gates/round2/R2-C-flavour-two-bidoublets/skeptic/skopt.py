"""Skeptic optimisers: W-parametrisation, batched finite-difference TRF polish, own CMA-ES with restarts."""
import math, time
import numpy as np
from scipy.optimize import least_squares
import skchain as S


def Wmat(x):
    """x (N,9): th12, th13, th23, delta, a1, a2, b1, b2, b3 -> unitary W = diag(e^{ia1}, e^{ia2}, 1) U diag(e^{ib})"""
    th12, th13, th23, dl = x[:, 0], x[:, 1], x[:, 2], x[:, 3]
    s12, c12, s13, c13, s23, c23 = np.sin(th12), np.cos(th12), np.sin(th13), np.cos(th13), np.sin(th23), np.cos(th23)
    e = np.exp(1j * dl)
    N = x.shape[0]
    U = np.empty((N, 3, 3), complex)
    U[:, 0, 0] = c12 * c13; U[:, 0, 1] = s12 * c13; U[:, 0, 2] = s13 / e
    U[:, 1, 0] = -s12 * c23 - c12 * s23 * s13 * e; U[:, 1, 1] = c12 * c23 - s12 * s23 * s13 * e; U[:, 1, 2] = s23 * c13
    U[:, 2, 0] = s12 * s23 - c12 * c23 * s13 * e; U[:, 2, 1] = -c12 * s23 - s12 * c23 * s13 * e; U[:, 2, 2] = c23 * c13
    P1 = np.exp(1j * np.stack([x[:, 4], x[:, 5], np.zeros(N)], 1))
    P2 = np.exp(1j * x[:, 6:9])
    return P1[:, :, None] * U * P2[:, None, :]


def w_to_gut(X):
    """X (N,19): W(9), log10 d(3), log10 e(3), log10 r, log10|s|, arg s, log10 cd126 -> H, F, r, s, cd"""
    X = np.atleast_2d(X)
    N = X.shape[0]
    W = Wmat(X[:, 0:9])
    dv = 10.0**X[:, 9:12]; ev = 10.0**X[:, 12:15]
    Yd = np.zeros((N, 3, 3), complex); Yd[:, [0, 1, 2], [0, 1, 2]] = dv
    Ye = (W * ev[:, None, :]) @ np.swapaxes(W, 1, 2)
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0**X[:, 15]; s = 10.0**X[:, 16] * np.exp(1j * X[:, 17]); cd = 10.0**X[:, 18]
    return H, F, r, s, cd


def gut_to_w(H, F, r, s, cd):
    """inverse map (up to discrete choices): Yd = H+F diagonalised (Takagi), Ye = H-3F in that basis -> Takagi W."""
    Yd = H + F; Ye = H - 3 * F
    md, Ud = S.takagi(Yd)
    Ye2 = np.swapaxes(Ud, 1, 2) @ Ye @ Ud
    me, We = S.takagi(Ye2)            # We^T Ye2 We = diag  ->  Ye2 = We^* diag We^dag ; W = We^*
    W = np.conj(We)
    N = H.shape[0]
    X = np.zeros((N, 19))
    for n in range(N):
        X[n, 0:9] = w_angles(W[n])
    X[:, 9:12] = np.log10(md); X[:, 12:15] = np.log10(me)
    X[:, 15] = np.log10(r); X[:, 16] = np.log10(np.abs(s)); X[:, 17] = np.angle(s); X[:, 18] = np.log10(cd)
    return X


def w_angles(W):
    """Decompose unitary W = diag(e^{ia1}, e^{ia2}, 1) U(th, delta) diag(e^{ib}); returns 9 params (least-squares refine)."""
    A = np.abs(W)
    s13 = min(1.0, A[0, 2]); c13 = math.sqrt(max(0, 1 - s13**2))
    th13 = math.asin(s13)
    th12 = math.atan2(A[0, 1], A[0, 0]); th23 = math.atan2(A[1, 2], A[2, 2])
    best = None
    from scipy.optimize import least_squares as LS

    def res(p):
        Wm = Wmat(p[None])[0]
        D = Wm - W
        return np.concatenate([D.real.ravel(), D.imag.ravel()])
    for dl0 in np.linspace(-3, 3, 7):
        # phases from a guess
        p0 = np.zeros(9); p0[0], p0[1], p0[2], p0[3] = th12, th13, th23, dl0
        b = np.angle(W[2, :]) - np.angle(Wmat(p0[None])[0][2, :])
        p0[6:9] = b
        Wg = Wmat(p0[None])[0]
        p0[4] = np.angle(W[0, 0] / Wg[0, 0]) if abs(Wg[0, 0]) > 1e-9 else 0
        p0[5] = np.angle(W[1, 2] / Wg[1, 2]) if abs(Wg[1, 2]) > 1e-9 else 0
        sol = LS(res, p0, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        if best is None or sol.cost < best.cost:
            best = sol
    return best.x


class Fit:
    def __init__(self, model, param="W"):
        self.m = model; self.param = param

    def gut(self, X):
        if self.param == "W":
            return w_to_gut(X)
        return S.unpack(X)

    nuis = 0            # number of nuisance threshold parameters appended to X (0 or 3)
    nuis_sigma = 0.01

    def resid(self, X):
        X = np.atleast_2d(X)
        thr = None
        if self.nuis:
            thr = X[:, 19:22]; X = X[:, :19]
        H, F, r, s, cd = self.gut(X)
        o, ok, info = S.chain(H, F, r, s, cd, self.m.env, thr=thr, **self.m.kw)
        self.m.nev += X.shape[0]
        R = S.residuals(o, self.m.d)
        BAD = 1e6
        R = np.where(np.isfinite(R), R, BAD); R[~ok] = BAD
        ym10 = np.maximum(info["y10U"], info["y10R"]); ym126 = np.maximum(info["y126U"], info["y126R"])
        fm = np.maximum(info["fU"], info["fR"])
        w = self.m.wpen
        pen = np.stack([w * np.clip(ym10 / self.m.ybound - 1, 0, None), w * np.clip(ym126 / self.m.ybound - 1, 0, None),
                        (w * np.clip(fm / self.m.fbound - 1, 0, None)) if np.isfinite(self.m.fbound) else 0 * fm], 1)
        pen = np.where(np.isfinite(pen), pen, BAD); pen[~ok] = 0
        self.last = (o, ok, info)
        if getattr(self, "mask", None) is not None:
            R = R * self.mask[None, :]
        if self.nuis:
            pen = np.concatenate([pen, thr / self.nuis_sigma], 1)
        return np.concatenate([R, pen], 1)

    def chi2(self, X):
        R = self.resid(X)
        return np.sum(R * R, 1)

    def polish(self, x0, nfev=200, h=1e-6):
        x0 = np.array(x0, float)

        def f(x):
            return self.resid(x[None])[0]

        def jac(x):
            n = len(x)
            Xs = np.tile(x, (n + 1, 1)); Xs[1:] += np.eye(n) * h
            R = self.resid(Xs)
            return ((R[1:] - R[0]) / h).T
        try:
            sol = least_squares(f, x0, jac=jac, method="trf", max_nfev=nfev, xtol=1e-12, ftol=1e-12, gtol=1e-12,
                                x_scale="jac")
            x = sol.x
        except Exception:
            x = x0
        return x, float(self.chi2(x[None])[0])


def cmaes(fun, m0, sig0, lam=40, gens=300, rng=None, lo=None, hi=None, tol=1e-6, verbose=False):
    """Plain (mu/mu_w, lambda)-CMA-ES (Hansen 2016 tutorial defaults) on batched fun(X)->(N,)."""
    rng = rng or np.random.default_rng()
    n = len(m0)
    mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum()
    mueff = 1 / np.sum(w**2)
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3)**2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2)**2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    m = np.array(m0, float); sig = float(sig0)
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); B = np.eye(n); D = np.ones(n)
    best = (np.inf, m.copy()); hist = []
    for g in range(gens):
        Z = rng.standard_normal((lam, n))
        Y = Z @ (B * D).T
        X = m + sig * Y
        if lo is not None:
            X = np.clip(X, lo, hi)
        fx = fun(X)
        fx = np.where(np.isfinite(fx), fx, 1e30)
        idx = np.argsort(fx)
        if fx[idx[0]] < best[0]:
            best = (float(fx[idx[0]]), X[idx[0]].copy())
        hist.append(float(fx[idx[0]]))
        Ysel = (X[idx[:mu]] - m) / sig
        yw = w @ Ysel
        m = m + sig * yw
        Cinvsq = B @ np.diag(1 / D) @ B.T
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (Cinvsq @ yw)
        hs = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs)**(2 * (g + 1))) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hs * math.sqrt(cc * (2 - cc) * mueff) * yw
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hs) * cc * (2 - cc) * C) + cmu * (Ysel.T * w) @ Ysel
        sig = sig * math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        C = np.triu(C) + np.triu(C, 1).T
        Dv, B = np.linalg.eigh(C)
        D = np.sqrt(np.clip(Dv, 1e-20, None))
        if verbose and g % 50 == 0:
            print(f"   cma gen {g} best {best[0]:.3f} sig {sig:.3g}", flush=True)
        if sig * D.max() < tol or (g > 60 and abs(hist[-60] - hist[-1]) < 1e-3 * max(1, abs(hist[-1]))):
            break
    return best, m
