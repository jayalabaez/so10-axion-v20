"""Second-pass independent Boltzmann check of the R-odd relic thresholds (verifier, physics lens).

Different formulation from the researcher's code: dimensionless comoving variables
    Phi = rho_phi a^3 / rho_0,   R = rho_R a^4 / rho_0,   X = n_X a^3 / (rho_0 / M)      (rho_0 = 3 M_P^2 H_I^2, a_I = 1)
integrated in N = ln a with an explicit Jacobian-free stiff solver (LSODA), and the equilibrium density written
with the Fermi-Dirac-vs-Maxwell-Boltzmann ratio irrelevant at M/T >~ 20.  Also an analytic estimate of the yield
(saddle point at T_max, with the exact GKR dilution factor) as a sanity check of the exponent 2M/T_max.
Outputs: Omega h^2 at the researcher's claimed thresholds and my own bisection thresholds.
"""
from __future__ import annotations
import json, sys, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import kve

MP = 2.435e18
GS = 106.75
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-physics\v2_relic_boltzmann.json"


def n_eq(M, T, gX):
    x = M / T
    if x > 600:
        return 0.0
    return gX * M * M * T / (2 * np.pi ** 2) * kve(2, x) * np.exp(-x)


def solve(M, TRH, HI, k=1.0, alpha=0.03, gX=40.0, gs=GS):
    rho0 = 3 * MP ** 2 * HI ** 2
    Gam = np.sqrt(np.pi ** 2 * gs / 90) * TRH ** 2 / MP
    sv = k * np.pi * alpha ** 2 / M ** 2
    # scale for X: X = n a^3 / nscale
    Tguess = 0.45 * (TRH ** 2 * HI * MP) ** 0.25
    nscale = max(n_eq(M, 2.0 * max(Tguess, TRH), gX), 1e-300)
    Tmax_seen = [0.0]

    def rhs(N, y):
        lPhi, lR, X = y
        a = np.exp(N)
        Phi, R = np.exp(lPhi), np.exp(lR)
        rho_phi = Phi * rho0 / a ** 3
        rho_R = R * rho0 / a ** 4
        H = np.sqrt((rho_phi + rho_R) / 3) / MP
        T = (30 * rho_R / (np.pi ** 2 * gs)) ** 0.25
        if T > Tmax_seen[0]:
            Tmax_seen[0] = T
        ne = n_eq(M, T, gX)
        n = X * nscale / a ** 3
        dlPhi = -Gam / H
        dlR = (Gam / H) * (rho_phi / rho_R)
        dX = -(sv / H) * (n * n - ne * ne) * a ** 3 / nscale
        return [dlPhi, dlR, dX]

    y0 = [0.0, np.log(1e-14), 0.0]

    def ev(N, y):
        a = np.exp(N)
        rho_R = np.exp(y[1]) * rho0 / a ** 4
        T = (30 * rho_R / (np.pi ** 2 * gs)) ** 0.25
        rho_phi = np.exp(y[0]) * rho0 / a ** 3
        return (T - TRH / 40.0) if rho_phi / rho_R < 1e-12 else 1.0
    ev.terminal = True
    ev.direction = -1
    sol = solve_ivp(rhs, (0.0, 300.0), y0, method="LSODA", rtol=1e-8, atol=[1e-12, 1e-12, 1e-80], events=ev, max_step=0.05)
    N = sol.t[-1]
    a = np.exp(N)
    rho_R = np.exp(sol.y[1, -1]) * rho0 / a ** 4
    T = (30 * rho_R / (np.pi ** 2 * gs)) ** 0.25
    s = 2 * np.pi ** 2 / 45 * gs * T ** 3
    n = max(sol.y[2, -1], 0.0) * nscale / a ** 3
    Y = n / s
    return dict(M=M, TRH=TRH, HI=HI, k=k, Tmax=Tmax_seen[0], Tmax_formula=0.4487 * (TRH ** 2 * HI * MP) ** 0.25,
                T_end=T, Y=Y, Omega_h2=2.74e8 * M * Y, nX_nB=Y / 8.66e-11, ok=bool(sol.success))


def analytic_yield(M, TRH, HI, k=1.0, alpha=0.03, gX=40.0, gs=GS):
    """Saddle-point estimate: production rate per comoving volume peaks near T_max; Y_final = (n a^3)_prod / (s a^3)_RH.
    Exact reheating kinematics for rho_R(a) (matter-dominated inflaton, constant Gamma), numerical quadrature in a."""
    rho0 = 3 * MP ** 2 * HI ** 2
    Gam = np.sqrt(np.pi ** 2 * gs / 90) * TRH ** 2 / MP
    sv = k * np.pi * alpha ** 2 / M ** 2
    # rho_R(a) = (6/5) Gam M_P^2 H_I [ a^-3/2 - a^-4 ]  (valid while rho_phi dominates and Gamma t << 1)
    la = np.linspace(np.log(1.0001), np.log(1e6), 20000)
    a = np.exp(la)
    rhoR = 1.2 * Gam * MP ** 2 * HI * (a ** -1.5 - a ** -4.0)
    rhophi = rho0 * a ** -3.0 * np.exp(-Gam * (2.0 / (3 * HI)) * (a ** 1.5 - 1))
    T = (30 * rhoR / (np.pi ** 2 * gs)) ** 0.25
    H = np.sqrt((rhophi + rhoR) / 3) / MP
    ne = np.array([n_eq(M, t, gX) for t in T])
    integrand = sv * ne ** 2 * a ** 3 / H          # d(n a^3)/dN
    na3 = np.trapezoid(integrand, la)
    # entropy at reheating: a_RH where H = Gamma -> a_RH = (HI/Gam)^(2/3); s a^3 at the end of reheating (rho_R -> 3 M_P^2 Gam^2 roughly)
    a_RH = (HI / Gam) ** (2.0 / 3.0)
    T_RH_eff = (30 * 3 * MP ** 2 * Gam ** 2 / (np.pi ** 2 * gs)) ** 0.25   # = TRH by construction (times (3)^(1/4)... keep as is)
    s_a3 = 2 * np.pi ** 2 / 45 * gs * TRH ** 3 * a_RH ** 3
    Y = na3 / s_a3
    return dict(M=M, TRH=TRH, HI=HI, Y_analytic=Y, Omega_h2_analytic=2.74e8 * M * Y, Tmax=float(T.max()), T_RH_eff=T_RH_eff)


def bisect(M, HI, target=0.12, k=1.0, lo=3e8, hi=3e12):
    hi = min(hi, np.sqrt(HI * MP / np.sqrt(np.pi ** 2 * GS / 90)))
    f = lambda T: solve(M, T, HI, k=k)["Omega_h2"]
    if f(lo) > target:
        return None
    if f(hi) <= target:
        return hi
    while hi / lo > 1.015:
        mid = np.sqrt(lo * hi)
        if f(mid) <= target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


if __name__ == "__main__":
    t0 = time.time()
    out = {"claimed_points": [], "analytic": [], "my_thresholds": []}
    # researcher's claimed thresholds (Omega_DM line) -> Omega h^2 should be ~0.12
    claimed = [(1e13, 1.08e11, 3e7), (1e13, 1.62e11, 1e7), (1e13, 4.05e11, 1e6), (3e12, 1.38e10, 3e7), (3e12, 4.70e10, 1e6),
               (6e12, 6.68e10, 1e7), (6e12, 4.46e10, 3e7), (1e13, 4.36e10, 3e7)]
    for (M, TRH, HI) in claimed:
        r = solve(M, TRH, HI)
        out["claimed_points"].append(r)
        print(f"claimed M={M:.0e} TRH={TRH:.3e} HI={HI:.0e}: Tmax={r['Tmax']:.3e} (formula {r['Tmax_formula']:.3e}) Oh2={r['Omega_h2']:.3e} nX/nB={r['nX_nB']:.2e} ok={r['ok']}", flush=True)
        an = analytic_yield(M, TRH, HI)
        out["analytic"].append(an)
        print(f"   analytic saddle: Oh2={an['Omega_h2_analytic']:.3e} (Tmax {an['Tmax']:.3e})", flush=True)
    # my own thresholds
    for (M, HI) in ((1e13, 3e7), (3e12, 3e7), (1e13, 1e6), (6e12, 1e7)):
        th = bisect(M, HI)
        out["my_thresholds"].append(dict(M=M, HI=HI, TRH_max_OmegaDM=th, M_over_Tmax=(M / (0.4487 * (th ** 2 * HI * MP) ** 0.25) if th else None)))
        print(f"my threshold M={M:.0e} HI={HI:.0e}: TRH_max={th:.4e}  M/Tmax={out['my_thresholds'][-1]['M_over_Tmax']:.2f}", flush=True)
    # k sensitivity at the reference point
    for k in (1e-4, 1e-2, 10.0):
        th = bisect(1e13, 3e7, k=k)
        out["my_thresholds"].append(dict(M=1e13, HI=3e7, k=k, TRH_max_OmegaDM=th))
        print(f"k={k}: TRH_max={th:.4e}", flush=True)
    out["runtime_s"] = time.time() - t0
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, default=float)
    print("done", out["runtime_s"])
