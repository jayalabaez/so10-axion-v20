"""Skeptic independent GLOBAL search: my own GUT-scale proxy (data run bottom-up with my SM RGEs to v_R, then
gauge-only G3221 factors to M_U), scipy differential_evolution over (W, r, s, mass offsets) from many seeds, then the
distinct proxy minima are mapped into the EXACT chain (same W-parametrisation), lc-scanned and TRF-polished.
usage: skproxy.py TAG vR NSEEDS NMAP [floor]"""
import sys, os, json, math, time
import numpy as np
from scipy.optimize import differential_evolution
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skchain as S, skopt as O

tag = sys.argv[1]; vR = float(sys.argv[2]); nseeds = int(sys.argv[3]); nmap = int(sys.argv[4])
floor = float(sys.argv[5]) if len(sys.argv) > 5 else 0.01
S.KAPPA_LAM = 2.0
c = "C2" if vR < 5e10 else ("R813" if vR <= 2e12 else "R622"); MU = S.MU_NOMINAL[c]
d = S.dataset(floor)
env = S.Env(vR, c, MU, d)
# --- bottom-up targets
st = S.sm_bottom_up(d, vR)
YuR, YdR, YeR = st[2], st[3], st[4]
o_vR, _ = S.observables(np.swapaxes(YuR, 1, 2), np.swapaxes(YdR, 1, 2), np.swapaxes(YeR, 1, 2), np.eye(3)[None] * (1 + 0j))
o_vR = o_vR[0]
ts = np.linspace(math.log(vR), math.log(MU), 401)
Iq = Il = 0.0
for a, b in zip(ts[:-1], ts[1:]):
    g3s, gLs, gRs, gqs = env.g2_at(0.5 * (a + b))
    Iq += (8 * g3s + 9 / 4 * (gLs + gRs) + gqs / 6) * (b - a)
    Il += (9 / 4 * (gLs + gRs) + 1.5 * gqs) * (b - a)
eq, el = math.exp(-S.K1 * Iq), math.exp(-S.K1 * Il)
T = o_vR.copy()
T[0:6] *= eq; T[6:9] *= el
sig = np.array([d[k][1] / d[k][0] for k in S.MASS_KEYS])           # relative mass errors
d0 = T[3:6] / S.VEV; e0 = T[6:9] / S.VEV
nu = [d["sin2_th12"], d["sin2_th23"], d["sin2_th13"]]
ratio_t = d["dm21"][0] / d["dm31"][0]
ratio_s = ratio_t * math.hypot(d["dm21"][1] / d["dm21"][0], d["dm31"][1] / d["dm31"][0])


def proxy(Xs):
    """Xs (N,18): W(9), log10 r, log10|s|, arg s, 6 log-offsets (units of 1 sigma) for d, e."""
    N = Xs.shape[0]
    W = O.Wmat(Xs[:, 0:9])
    off = Xs[:, 12:18]
    dv = d0[None] * np.exp(off[:, 0:3] * sig[3:6]); ev = e0[None] * np.exp(off[:, 3:6] * sig[6:9])
    Yd = np.zeros((N, 3, 3), complex); Yd[:, [0, 1, 2], [0, 1, 2]] = dv
    Ye = (W * ev[:, None, :]) @ np.swapaxes(W, 1, 2)
    H = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
    r = 10.0**Xs[:, 9]; s = 10.0**Xs[:, 10] * np.exp(1j * Xs[:, 11])
    Yu = r[:, None, None] * (H + s[:, None, None] * F)
    Yn = r[:, None, None] * (H - 3 * s[:, None, None] * F)
    w, Eu = np.linalg.eigh(Yu @ S.herm(Yu))
    mu = np.sqrt(np.clip(w, 1e-300, None)) * S.VEV
    V = np.swapaxes(Eu, 1, 2)                      # E_u^T E_d^*, E_d = 1
    a12, a23, a13, dl = S.angles(V)
    with np.errstate(all="ignore"):
        mn = -Yn @ np.linalg.solve(F, np.swapaxes(Yn, 1, 2))
    sc = np.abs(mn).reshape(N, -1).max(1); sc = np.where(np.isfinite(sc) & (sc > 0), sc, 1.0)
    mn = mn / sc[:, None, None]; mn = np.where(np.isfinite(mn), mn, 0)
    wn, Nn = np.linalg.eigh(S.herm(mn) @ mn)
    U = np.swapaxes(W, 1, 2) @ Nn
    n12, n23, n13, _ = S.angles(U)
    R = np.zeros((N, 17))
    R[:, 0:3] = np.log(mu / T[0:3]) / sig[0:3]
    R[:, 3] = (a12 - T[9]) / d["s12"][1]; R[:, 4] = (a23 - T[10]) / (d["s23"][1] / d["s23"][0] * T[10])
    R[:, 5] = (a13 - T[11]) / (d["s13"][1] / d["s13"][0] * T[11])
    R[:, 6] = ((np.abs(dl) - abs(T[12]) + math.pi) % (2 * math.pi) - math.pi) / d["delta"][1]
    R[:, 7] = (n12**2 - nu[0][0]) / nu[0][1]; R[:, 8] = (n23**2 - nu[1][0]) / nu[1][1]; R[:, 9] = (n13**2 - nu[2][0]) / nu[2][1]
    rat = (wn[:, 1] - wn[:, 0]) / np.where(wn[:, 2] - wn[:, 0] > 0, wn[:, 2] - wn[:, 0], 1e-300)
    R[:, 10] = (rat - ratio_t) / ratio_s
    R[:, 11:17] = off
    R = np.where(np.isfinite(R), R, 1e4)
    return R


def f_vec(x):
    if x.ndim == 1:
        R = proxy(x[None]); return float(np.sum(R * R))
    R = proxy(x.T)
    return np.sum(R * R, 1)


b12 = [(0, math.pi / 2)] * 3 + [(-math.pi, math.pi)] * 6 + [(1.0, 2.3), (-2.0, 0.5), (-math.pi, math.pi)]


def f12(x):
    if x.ndim == 1:
        return float(np.sum(proxy(np.concatenate([x, np.zeros(6)])[None])**2))
    return np.sum(proxy(np.concatenate([x.T, np.zeros((x.shape[1], 6))], 1))**2, 1)


from scipy.optimize import least_squares
t0 = time.time()
prox = []
for sd in range(nseeds):
    res = differential_evolution(f12, b12, vectorized=True, popsize=30, maxiter=3000, tol=1e-10, seed=3000 + sd,
                                 polish=True, updating="deferred", mutation=(0.5, 1.0), recombination=0.9)
    x18 = np.concatenate([res.x, np.zeros(6)])
    sol = least_squares(lambda x: proxy(x[None])[0], x18, method="trf", max_nfev=5000, xtol=1e-14, ftol=1e-14, x_scale="jac")
    prox.append((float(2 * sol.cost), sol.x.copy()))
    print(f"  proxy seed {sd}: pinned {res.fun:.3f} -> free {2*sol.cost:.3f}  r={10**sol.x[9]:.1f} |s|={10**sol.x[10]:.3f} "
          f"arg={sol.x[11]:.2f} t={time.time()-t0:.0f}s", flush=True)
prox.sort(key=lambda t: t[0])
# distinct minima by (r, s)
dist = []
for cval, x in prox:
    key = (10**x[9], 10**x[10] * np.exp(1j * x[11]))
    if all(abs(key[0] - k[0]) / key[0] > 0.02 or abs(key[1] - k[1]) > 0.02 for _, _, k in dist):
        dist.append((cval, x, key))
print("distinct proxy minima:", [(round(cv, 2), round(k[0], 1), round(abs(k[1]), 3), round(float(np.angle(k[1])), 2)) for cv, _, k in dist],
      flush=True)
# map into the exact chain
m = S.Model(env, d, h_g=0.5, h_hi=0.1, h_lo=0.5)
fit = O.Fit(m, "W")
out = dict(vR=vR, content=c, MU=MU, proxy=[(cv, x.tolist()) for cv, x in prox], exact=[])
rng = np.random.default_rng(5)
for cv, x, key in dist[:nmap]:
    X = np.zeros(19)
    X[0:9] = x[0:9]
    X[9:12] = np.log10(d0 * np.exp(x[12:15] * sig[3:6])); X[12:15] = np.log10(e0 * np.exp(x[15:18] * sig[6:9]))
    X[15:18] = x[9:12]
    Z = np.tile(X, (81, 1)); Z[:, 18] = np.linspace(-4.5, -1.0, 81)
    cs = fit.chi2(Z); j = int(np.argmin(cs))
    xe, ce = fit.polish(Z[j], nfev=250)
    cur = (ce, xe)
    steps = np.full(19, 0.1); steps[9:15] = 0.02; steps[15] = 0.02; steps[16] = 0.04; steps[17] = 0.1; steps[18] = 0.05
    for k in range(4):
        xk, ck = fit.polish(cur[1] + rng.normal(0, 1, 19) * steps, 120)
        if ck < cur[0]:
            cur = (ck, xk)
    R = fit.resid(cur[1][None])[0]
    th = float(fit.last[0][0, 14])
    out["exact"].append(dict(proxy_chi2=cv, lc_scan=float(cs[j]), exact_chi2=cur[0], x=cur[1].tolist(), th23=th,
                             r=float(10**cur[1][15]), s=[float(10**cur[1][16]), float(cur[1][17])],
                             pulls={k: float(R[i]) for i, k in enumerate(S.KEYS)}))
    print(f"  map proxy {cv:.2f} (r={key[0]:.1f}, |s|={abs(key[1]):.3f}): lc-scan {cs[j]:.1f} -> exact {cur[0]:.2f} th23={th:.3f} "
          f"t={time.time()-t0:.0f}s", flush=True)
    json.dump(out, open(os.path.join(HERE, f"proxy_{tag}.json"), "w"), indent=1)
json.dump(out, open(os.path.join(HERE, f"proxy_{tag}.json"), "w"), indent=1)
print("BEST exact", min(e["exact_chi2"] for e in out["exact"]), flush=True)
