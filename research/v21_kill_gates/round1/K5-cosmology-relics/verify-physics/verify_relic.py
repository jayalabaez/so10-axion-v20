"""Independent re-computation of the R-odd relic produced from the plasma during perturbative reheating.

Written from scratch (not copied from the researcher's k5_relic_reheating.py).  Comoving variables:
   P = rho_phi a^3,  R = rho_R a^4,  Nx = n_X a^3        (all evolved in N = ln a, log form for P and R)
   dP/dN = -(Gamma/H) P
   dR/dN = +(Gamma/H) rho_phi a^4 = (Gamma/H) P a
   dNx/dN = -(<sv>/H) (n_X^2 - n_eq^2) a^3
H^2 = (rho_phi + rho_R)/(3 M_P^2), reduced M_P = 2.435e18, g_* = 106.75, Gamma = sqrt(pi^2 g_*/90) T_RH^2/M_P.
n_eq = g_X M^2 T K_2(M/T)/(2 pi^2), g_X = 40, <sv> = k pi alpha^2/M^2, alpha = 0.03.
Outputs Omega h^2 = 2.74e8 (M/GeV) Y and n_X/n_B = Y/8.66e-11, and the T_max reached.
"""
from __future__ import annotations
import json, sys, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import kve

MP = 2.435e18
GS = 106.75
YB = 8.66e-11
OUT = sys.argv[1] if len(sys.argv) > 1 else "verify_relic.json"


def neq(M, T, gX=40.0):
    x = M / T
    if x > 690:
        return 0.0
    return gX * M * M * T * kve(2, x) * np.exp(-x) / (2 * np.pi ** 2)


def T_of_rhoR(rr):
    return (30.0 * rr / (np.pi ** 2 * GS)) ** 0.25


def evolve(M, TRH, HI, k=1.0, alpha=0.03, gX=40.0, freeze_in_only=False):
    Gamma = np.sqrt(np.pi ** 2 * GS / 90.0) * TRH ** 2 / MP
    sv = k * np.pi * alpha ** 2 / M ** 2
    rho0 = 3.0 * HI ** 2 * MP ** 2
    # scale for Nx: use n_eq at an estimated 2 x T_max (a > 0 number unless underflow)
    Tmax_est = 0.5 * (TRH ** 2 * HI * MP) ** 0.25
    nscale = neq(M, 2.5 * Tmax_est, gX)
    if nscale <= 0.0:
        return dict(M=M, TRH=TRH, HI=HI, Y=0.0, Omega_h2=0.0, nX_over_nB=0.0, Tmax=Tmax_est, note="underflow: zero")
    Tmax = [0.0]

    def rhs(N, y):
        lP, lR, nx = y
        a = np.exp(N)
        rp = np.exp(lP) / a ** 3
        rr = np.exp(lR) / a ** 4
        H = np.sqrt((rp + rr) / 3.0) / MP
        T = T_of_rhoR(rr)
        if T > Tmax[0]:
            Tmax[0] = T
        nX = nx * nscale / a ** 3
        ne = neq(M, T, gX)
        ann = 0.0 if freeze_in_only else nX * nX
        return [-(Gamma / H), (Gamma / H) * np.exp(lP) * a / np.exp(lR), -(sv / H) * (ann - ne * ne) * a ** 3 / nscale]

    # initial: a = 1, rho_phi = rho0, rho_R small (sourced immediately)
    y0 = [np.log(rho0), np.log(rho0 * 1e-14), 0.0]

    def done(N, y):
        a = np.exp(N)
        rp = np.exp(y[0]) / a ** 3
        rr = np.exp(y[1]) / a ** 4
        return (rp / rr - 1e-12)      # stop once the inflaton is gone (T then is ~ T_RH/few)
    done.terminal = True
    done.direction = -1
    sol = solve_ivp(rhs, (0.0, 300.0), y0, method="Radau", rtol=1e-8, atol=[1e-12, 1e-12, 1e-80], events=done, max_step=0.1)
    N = sol.t[-1]
    a = np.exp(N)
    rr = np.exp(sol.y[1, -1]) / a ** 4
    T = T_of_rhoR(rr)
    s = 2 * np.pi ** 2 / 45 * GS * T ** 3
    nX = max(sol.y[2, -1], 0.0) * nscale / a ** 3
    Y = nX / s
    return dict(M=M, TRH=TRH, HI=HI, k=k, Y=Y, Omega_h2=2.74e8 * M * Y, nX_over_nB=Y / YB, Tmax=Tmax[0],
                Tmax_formula_0p465=0.465 * (TRH ** 2 * HI * MP) ** 0.25, T_end=T, N_end=N, ok=bool(sol.success))


def bisect(M, HI, key, target, k=1.0, lo=1e8, hi=None):
    cap = np.sqrt(HI * MP / np.sqrt(np.pi ** 2 * GS / 90.0))    # H(T_RH) = H_I
    hi = cap if hi is None else min(hi, cap)
    if evolve(M, hi, HI, k)[key] <= target:
        return hi, "capped (below target at H(TRH)=HI)"
    if evolve(M, lo, HI, k)[key] > target:
        return None, "above target at lo"
    while hi / lo > 1.015:
        mid = np.sqrt(lo * hi)
        if evolve(M, mid, HI, k)[key] <= target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi)), "ok"


if __name__ == "__main__":
    t0 = time.time()
    out = {"points": [], "thresholds": []}
    # 1. spot checks against the researcher's grid
    for (M, TRH, HI) in ((1e13, 1e11, 3e7), (1e13, 3e11, 3e7), (3e12, 1e10, 3e7), (3e12, 3e10, 3e7), (1e13, 1e12, 1e7), (3e12, 1e11, 1e5)):
        r = evolve(M, TRH, HI)
        r2 = evolve(M, TRH, HI, freeze_in_only=True)
        r["Omega_h2_freeze_in_only"] = r2["Omega_h2"]
        out["points"].append(r)
        print(f"M={M:.0e} TRH={TRH:.0e} HI={HI:.0e}: Tmax={r['Tmax']:.3e} (formula {r['Tmax_formula_0p465']:.3e}) Oh2={r['Omega_h2']:.3e} (FI-only {r2['Omega_h2']:.3e}) nX/nB={r['nX_over_nB']:.3e} ok={r['ok']}", flush=True)
    # 2. thresholds
    for (M, HI) in ((1e13, 3e7), (3e12, 3e7), (1e13, 1e6), (1e13, 1e7), (3e12, 1e6), (1e13, 1e9)):
        for key, target in (("Omega_h2", 0.12), ("Omega_h2", 1.2e-4), ("nX_over_nB", 1e-10), ("nX_over_nB", 1e-20), ("nX_over_nB", 1e-25)):
            th, note = bisect(M, HI, key, target)
            out["thresholds"].append(dict(M=M, HI=HI, key=key, target=target, TRH_max=th, note=note, M_over_Tmax=(M / (0.465 * (th ** 2 * HI * MP) ** 0.25) if th else None)))
            print(f"threshold M={M:.0e} HI={HI:.0e} {key}<={target:.0e}: TRH_max={th} {note}", flush=True)
    # 3. k robustness at (1e13, 3e7)
    for k in (0.01, 0.1, 10.0):
        th, note = bisect(1e13, 3e7, "Omega_h2", 0.12, k=k)
        out["thresholds"].append(dict(M=1e13, HI=3e7, key="Omega_h2", target=0.12, k=k, TRH_max=th, note=note))
        print(f"k={k}: TRH_max={th}", flush=True)
    out["runtime_s"] = time.time() - t0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("done", out["runtime_s"])
