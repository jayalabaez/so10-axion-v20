"""Independent re-derivation of the K5 relic thresholds (verifier; log-time formulation, not the e-fold code).

Variables as functions of u = ln t: (ln rho_phi, ln rho_R, ln a, Y := n_X a^3 / n_norm).
  d ln rho_phi/du = t(-3H - Gamma),  d ln rho_R/du = t(-4H + Gamma rho_phi/rho_R),  d ln a/du = tH,
  dY/du = -t <sv> (n_X^2 - n_eq^2) a^3 / n_norm
Gamma = sqrt(pi^2 g_*/90) T_RH^2 / M_P (reduced M_P = 2.435e18), g_* = 106.75, n_eq relativistic MB with g_X = 40,
<sigma v> = k pi alpha^2 / M^2 (k = 1, alpha = 0.03).  Omega h^2 = 2.74e8 (M/GeV) n_X/s at the end (T = T_RH/40).
"""
import json, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import kve

MP = 2.435e18
GS = 106.75
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\v_relic_independent.json"


def n_eq(M, T, g=40.0):
    x = M / T
    if x > 600:
        return 0.0
    return g * M * M * T * kve(2, x) * np.exp(-x) / (2 * np.pi ** 2)


def T_of(rr):
    return (30.0 * rr / (np.pi ** 2 * GS)) ** 0.25


def omega(M, TRH, HI, k=1.0, alpha=0.03, g=40.0):
    Gam = np.sqrt(np.pi ** 2 * GS / 90.0) * TRH ** 2 / MP
    sv = k * np.pi * alpha ** 2 / M ** 2
    rp0 = 3 * HI ** 2 * MP ** 2
    Tm_est = 0.45 * (TRH ** 2 * HI * MP) ** 0.25
    if M / Tm_est > 250.0:
        return dict(M=M, TRH=TRH, HI=HI, Tmax=None, Tmax_analytic=Tm_est, Y=0.0, Omega_h2=0.0, ok=True, note="M/Tmax>250: zero")
    nn = n_eq(M, Tm_est, g)
    t0 = 0.01 / HI
    rr0 = max(0.4 * Gam * rp0 * t0, 1e-30 * rp0)
    Tmax = [0.0]

    def rhs(u, y):
        t = np.exp(u)
        lrp, lrr, lna, Y = y
        rp, rr = np.exp(lrp), np.exp(lrr)
        H = np.sqrt((rp + rr) / 3.0) / MP
        T = T_of(rr)
        if T > Tmax[0]:
            Tmax[0] = T
        a3 = np.exp(3 * lna)
        nX = Y * nn / a3
        ne = n_eq(M, T, g)
        return [t * (-3 * H - Gam), t * (-4 * H + Gam * rp / rr), t * H, -t * sv * (nX * nX - ne * ne) * a3 / nn]

    def done(u, y):
        rp, rr = np.exp(y[0]), np.exp(y[1])
        return (T_of(rr) - TRH / 40.0) if rp < 1e-8 * rr else 1.0
    done.terminal = True
    done.direction = -1
    u0, u1 = np.log(t0), np.log(1e5 / Gam)
    sol = solve_ivp(rhs, (u0, u1), [np.log(rp0), np.log(rr0), 0.0, 0.0], method="Radau", rtol=1e-8,
                    atol=[1e-10, 1e-10, 1e-10, 1e-60], events=done, max_step=0.05)
    lrp, lrr, lna, Y = sol.y[:, -1]
    T = T_of(np.exp(lrr))
    s = 2 * np.pi ** 2 / 45 * GS * T ** 3
    nX = max(Y, 0.0) * nn / np.exp(3 * lna)
    Yx = nX / s
    return dict(M=M, TRH=TRH, HI=HI, Tmax=Tmax[0], Tmax_analytic=Tm_est, T_end=T, Y=Yx, Omega_h2=2.74e8 * M * Yx,
                ok=bool(sol.success), status=int(sol.status))


def threshold(M, HI, target=0.12, lo=1e8, hi=None):
    hi = hi or min(1e13, np.sqrt(HI * MP / np.sqrt(np.pi ** 2 * GS / 90.0)))
    flo, fhi = omega(M, lo, HI)["Omega_h2"], omega(M, hi, HI)["Omega_h2"]
    if flo > target:
        return None, "above at lo"
    if fhi <= target:
        return hi, "below at hi (cap)"
    while hi / lo > 1.02:
        mid = np.sqrt(lo * hi)
        if omega(M, mid, HI)["Omega_h2"] <= target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi)), "ok"


if __name__ == "__main__":
    t0 = time.time()
    res = {"points": [], "thresholds": []}
    for (M, TRH, HI) in ((1e13, 1e11, 3e7), (1e13, 1.08e11, 3e7), (3e12, 1e10, 3e7), (3e12, 1.38e10, 3e7), (1e13, 3e11, 1e5), (3e12, 1e11, 1e5), (1e13, 3e11, 1e7)):
        r = omega(M, TRH, HI)
        res["points"].append(r)
        print(json.dumps(r), flush=True)
    for (M, HI) in ((1e13, 3e7), (3e12, 3e7), (1e13, 1e6), (3e12, 1e6), (1e13, 1e9), (1e13, 1e5)):
        th, note = threshold(M, HI)
        res["thresholds"].append(dict(M=M, HI=HI, TRH_max=th, note=note))
        print(f"threshold M={M:.0e} HI={HI:.0e}: TRH_max={th} ({note})", flush=True)
    res["runtime_s"] = time.time() - t0
    json.dump(res, open(OUT, "w"), indent=1)
    print("done", res["runtime_s"])
