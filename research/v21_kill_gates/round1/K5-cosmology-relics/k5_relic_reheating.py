"""K5 part (1b): thermal relic abundance of the exactly stable R-odd 10_F (Dirac, M_10 = y_10 <S>) produced
from the plasma during and after reheating, as a function of (M, T_RH, H_I).

Boltzmann system in e-folds N = ln a (perturbative reheating, inflaton oscillating as matter):
   d ln rho_phi/dN = -3 - Gamma/H
   d ln rho_R  /dN = -4 + (Gamma/H) rho_phi/rho_R
   d (n_X a^3)/dN  = -(<sigma v>/H) (n_X^2 - n_eq^2) a^3
H^2 = (rho_phi + rho_R)/(3 M_P^2), T = (30 rho_R / pi^2 g_*)^{1/4}, Gamma = sqrt(pi^2 g_*/90) T_RH^2 / M_P.
n_eq = g_X M^2 T K_2(M/T)/(2 pi^2) with g_X = 40 (10 Dirac states: all 10_F components; every component ends up as
the lightest R-odd state, which has mass ~ M up to the 0.3-0.5% G3221 splitting), <sigma v> = k pi alpha^2 / M^2
(gauge pair production; k and alpha are scanned for robustness).
Initial state: rho_phi = 3 H_I^2 M_P^2, rho_R ~ 0, n_X = 0 (gravitational production is exponentially suppressed
for M >> H_I).  Output: Y_X = n_X/s, Omega_X h^2 = 2.74e8 (M/GeV) Y_X, n_X/n_B = Y_X/8.66e-11.
Thresholds in T_RH (bisection in log T_RH) for  Omega h^2 = 0.12 (overclosure / WIMPzilla line),
Omega h^2 = 1.2e-4 (cosmologically irrelevant, 1e-3 of DM) and n_X/n_B = 1e-10 (loose heavy-isotope bound).
"""
from __future__ import annotations
import json, sys, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import kve

MP = 2.435e18
GSTAR = 106.75
YB = 8.66e-11
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\k5_relic_reheating.json"


def neq(M, T, gX):
    x = M / T
    if x > 700.0:
        return 0.0
    return gX / (2 * np.pi ** 2) * M ** 2 * T * kve(2, x) * np.exp(-x)


def run(M, TRH, HI, k=1.0, alpha=0.03, gX=40.0):
    Gamma = np.sqrt(np.pi ** 2 * GSTAR / 90) * TRH ** 2 / MP
    sigv = k * np.pi * alpha ** 2 / M ** 2
    rho_phi0 = 3 * HI ** 2 * MP ** 2
    Tmax_est = max(0.6 * (TRH ** 2 * HI * MP) ** 0.25, TRH)
    n_ref = neq(M, 3.0 * Tmax_est, gX)          # generous reference density (3 x T_max,est)
    Tmax = [0.0]
    if n_ref <= 0.0:
        # M/T > 2100 everywhere: nothing is produced (e^{-700} underflow); report zero
        return dict(M=M, TRH=TRH, HI=HI, k=k, alpha=alpha, Tmax=Tmax_est, T_end=TRH / 30, N_end=None, Y=0.0,
                    Omega_h2=0.0, nX_over_nB=0.0, status=0, success=True, note="n_eq underflow: Y=0")

    def rhs(N, y):
        lrp, lrr, v = y
        rp, rr = np.exp(lrp), np.exp(lrr)
        H = np.sqrt((rp + rr) / 3.0) / MP
        T = (30 * rr / (np.pi ** 2 * GSTAR)) ** 0.25
        Tmax[0] = max(Tmax[0], T)
        a3 = np.exp(3 * N)
        nX = v * n_ref / a3
        ne = neq(M, T, gX)
        dlrp = -3.0 - Gamma / H
        dlrr = -4.0 + (Gamma / H) * rp / rr
        dv = -(sigv / H) * (nX * nX - ne * ne) * a3 / n_ref
        return [dlrp, dlrr, dv]

    y0 = [np.log(rho_phi0), np.log(rho_phi0 * 1e-12), 0.0]

    def stop(N, y):
        rp, rr = np.exp(y[0]), np.exp(y[1])
        T = (30 * rr / (np.pi ** 2 * GSTAR)) ** 0.25
        return (T - TRH / 30.0) if rp / rr < 1e-10 else 1.0
    stop.terminal = True
    stop.direction = -1
    sol = solve_ivp(rhs, (0.0, 200.0), y0, method="Radau", rtol=1e-7, atol=[1e-10, 1e-10, 1e-60], events=stop, max_step=0.2)
    N_end = sol.t[-1]
    lrp, lrr, v = sol.y[:, -1]
    rr = np.exp(lrr)
    T = (30 * rr / (np.pi ** 2 * GSTAR)) ** 0.25
    s = 2 * np.pi ** 2 / 45 * GSTAR * T ** 3
    nX = max(v, 0.0) * n_ref / np.exp(3 * N_end)
    Y = nX / s
    return dict(M=M, TRH=TRH, HI=HI, k=k, alpha=alpha, Tmax=Tmax[0], T_end=T, N_end=N_end, Y=Y,
                Omega_h2=2.74e8 * M * Y, nX_over_nB=Y / YB, status=sol.status, success=sol.success)


def freeze_in_radiation_only(M, TRH, k=1.0, alpha=0.03, gX=40.0):
    """Instant-reheating cross-check: Y = int_0^{TRH} <sv> n_eq^2 /(s H T) dT (no X-annihilation feedback)."""
    sigv = k * np.pi * alpha ** 2 / M ** 2
    Ts = np.geomspace(TRH / 200, TRH, 4000)
    integrand = []
    for T in Ts:
        ne = neq(M, T, gX)
        s = 2 * np.pi ** 2 / 45 * GSTAR * T ** 3
        H = np.sqrt(np.pi ** 2 * GSTAR / 90) * T ** 2 / MP
        integrand.append(sigv * ne ** 2 / (s * H * T))
    return float(np.trapezoid(integrand, Ts))


def threshold(M, HI, target_key, target, k=1.0, alpha=0.03, lo=1e8, hi=1e14):
    """Largest T_RH with quantity <= target, by bisection in log T_RH (quantity is monotonic in T_RH)."""
    hi = min(hi, np.sqrt(HI * MP / np.sqrt(np.pi ** 2 * GSTAR / 90)))   # H(T_RH) <= H_I
    f = lambda TRH: run(M, TRH, HI, k, alpha)[target_key]
    flo, fhi = f(lo), f(hi)
    if flo > target:
        return None, "already above target at lo"
    if fhi <= target:
        return hi, "below target even at hi"
    for _ in range(40):
        mid = np.sqrt(lo * hi)
        if f(mid) <= target:
            lo = mid
        else:
            hi = mid
        if hi / lo < 1.02:
            break
    return float(np.sqrt(lo * hi)), "ok"


if __name__ == "__main__":
    t0 = time.time()
    results = {"grid": [], "thresholds": [], "cross_check": []}
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for (M, TRH, HI) in ((1e13, 3e11, 3e7), (1e13, 1e11, 1e13), (3e12, 3e11, 1e11), (1e13, 1e10, 1e13)):
            r = run(M, TRH, HI)
            print(r, flush=True)
        for (M, TRH) in ((1e13, 3e11), (1e13, 1e11)):
            Y = freeze_in_radiation_only(M, TRH)
            print("instant", M, TRH, Y, 2.74e8 * M * Y)
        sys.exit(0)
    # 1. coarse grid
    for M in (3e12, 1e13):
        for HI in (1e5, 1e7, 3e7, 1e9, 1e11, 1e13):
            for TRH in (1e9, 1e10, 3e10, 1e11, 3e11, 1e12, 3e12, 1e13):
                r = run(M, TRH, HI)
                results["grid"].append(r)
                print(f"M={M:.0e} HI={HI:.0e} TRH={TRH:.0e} Tmax={r['Tmax']:.2e} Y={r['Y']:.3e} Oh2={r['Omega_h2']:.3e} nX/nB={r['nX_over_nB']:.3e} ok={r['success']}", flush=True)
    # 2. thresholds
    for M in (3e12, 1e13):
        for HI in (1e5, 1e6, 1e7, 3e7, 1e9, 1e11, 1e13):
            for key, target, label in (("Omega_h2", 0.12, "Omega_X = Omega_DM"), ("Omega_h2", 1.2e-4, "Omega_X = 1e-3 Omega_DM"), ("nX_over_nB", 1e-10, "n_X/n_B = 1e-10")):
                th, note = threshold(M, HI, key, target)
                results["thresholds"].append(dict(M=M, HI=HI, criterion=label, TRH_max=th, TRH_max_over_M=(th / M if th else None), note=note))
                print(f"threshold M={M:.0e} HI={HI:.0e} {label}: TRH_max={th} ({note})", flush=True)
    # 3. robustness in k (cross-section) and alpha at the reference point
    for k in (0.1, 1.0, 10.0):
        for M in (3e12, 1e13):
            th, note = threshold(M, 3e7, "Omega_h2", 0.12, k=k)
            results["thresholds"].append(dict(M=M, HI=3e7, criterion=f"Omega_X = Omega_DM, k={k}", TRH_max=th, TRH_max_over_M=(th / M if th else None), note=note))
            print(f"robustness k={k} M={M:.0e}: TRH_max={th}", flush=True)
    # 4. instant-reheating cross-check
    for M in (3e12, 1e13):
        for TRH in (1e11, 3e11, 1e12):
            Y = freeze_in_radiation_only(M, TRH)
            results["cross_check"].append(dict(M=M, TRH=TRH, Y_freeze_in_instant=Y, Omega_h2=2.74e8 * M * Y))
            print(f"instant-reheating freeze-in M={M:.0e} TRH={TRH:.0e}: Y={Y:.3e} Oh2={2.74e8*M*Y:.3e}", flush=True)
    results["runtime_s"] = time.time() - t0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    print("done", results["runtime_s"])
