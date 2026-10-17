"""Independent misalignment + isocurvature check (written from scratch).

Integrates theta(t) in cosmic time t with H = 1/(2t) (radiation domination), T(t) from H = 1.66 sqrt(g*) T^2 / M_Pl
(g* iterated), chi(T) = chi0 min(1, (Tc/T)^n), chi0^(1/4) = 75.5 MeV, Tc = 150 MeV, n = 8.16 (and 7).
Stops when T < Tc (m_a constant) and m_a/H > 1500; then n_a a^3 is conserved and Y = n_a/s.
Omega h^2 = 2.74e8 (m_a/GeV) Y.  Also the WKB estimate for comparison and the Planck isocurvature bound.
"""
from __future__ import annotations
import json, sys
import numpy as np
from scipy.integrate import solve_ivp

MPL = 1.2209e19
CHI0 = 0.0755 ** 4
TC = 0.150
# g*_rho and g*_s (Saikawa-Shirai 2018-like coarse table), T in GeV
TT = np.array([0.001, 0.005, 0.01, 0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.18, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 30.0, 100.0])
GR = np.array([10.75, 10.75, 10.75, 10.8, 11.0, 11.8, 13.0, 15.0, 20.0, 29.0, 35.0, 44.0, 50.0, 56.0, 60.0, 66.0, 72.0, 76.0, 79.0, 82.0, 84.0, 86.0, 90.0, 96.0])


def gstar(T):
    return float(np.interp(np.log(T), np.log(TT), GR))


def chi(T, n):
    return CHI0 if T <= TC else CHI0 * (TC / T) ** n


def T_of_t(t):
    # H = 1/(2t) = 1.66 sqrt(g) T^2/MPL  -> T = sqrt(MPL/(2 t 1.66 sqrt(g)))
    T = 1.0
    for _ in range(4):
        T = np.sqrt(MPL / (2.0 * t * 1.66 * np.sqrt(gstar(T))))
    return T


def omega(fa, theta_i, n=8.16):
    ma0 = np.sqrt(CHI0) / fa
    # start when m_a(T)/H = 1e-3
    def m_over_H(t):
        T = T_of_t(t)
        return np.sqrt(chi(T, n)) / fa * 2.0 * t
    lo, hi = 1e-30, 1e10
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        if m_over_H(mid) < 1e-3:
            lo = mid
        else:
            hi = mid
    t0 = lo
    # integrate in u = ln t
    def rhs(u, y):
        t = np.exp(u)
        th, dth = y
        T = T_of_t(t)
        m2 = chi(T, n) / fa ** 2
        H = 0.5 / t
        return [t * dth, t * (-3 * H * dth - m2 * np.sin(th))]

    def stop(u, y):
        # adiabatic regime: m_a/H = 1500 (WKB condition |dm/dt|/m = 4.08 H << m holds), at any T
        t = np.exp(u)
        T = T_of_t(t)
        return 1500.0 - np.sqrt(chi(T, n)) / fa * 2 * t
    stop.terminal = True
    sol = solve_ivp(rhs, (np.log(t0), np.log(t0) + 60), [theta_i, 0.0], method="DOP853", rtol=1e-9, atol=1e-12, events=stop, max_step=0.01)
    t = np.exp(sol.t[-1])
    T = T_of_t(t)
    th, dth = sol.y[:, -1]
    m2 = chi(T, n) / fa ** 2
    rho = 0.5 * fa ** 2 * dth ** 2 + fa ** 2 * m2 * (1 - np.cos(th))
    na = rho / np.sqrt(m2)
    s = 2 * np.pi ** 2 / 45 * gstar(T) * T ** 3        # g_s ~ g_rho at these T within a few %
    Y = na / s
    return dict(Omega_h2=2.74e8 * ma0 * Y, T_end=T, Y=Y, ma0_eV=ma0 * 1e9)


def wkb(fa, theta_i, n=8.16):
    # 3H(T_osc) = m_a(T_osc); n_a = (1/2) m_a(T_osc) fa^2 theta_i^2 ; Y = n_a/s(T_osc)
    def f(T):
        return np.sqrt(chi(T, n)) / fa - 3 * 1.66 * np.sqrt(gstar(T)) * T ** 2 / MPL
    lo, hi = 0.05, 50.0
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    Tosc = lo
    ma_osc = np.sqrt(chi(Tosc, n)) / fa
    na = 0.5 * ma_osc * fa ** 2 * theta_i ** 2
    s = 2 * np.pi ** 2 / 45 * gstar(Tosc) * Tosc ** 3
    return dict(T_osc=Tosc, Omega_h2=2.74e8 * (np.sqrt(CHI0) / fa) * na / s)


def theta_dm(fa, n=8.16):
    lo, hi = 0.05, 3.0
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        if omega(fa, mid, n)["Omega_h2"] < 0.12:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    out = {}
    bm = omega(1e12, 1.0)
    out["benchmark_fa1e12_theta1"] = bm
    out["benchmark_wkb"] = wkb(1e12, 1.0)
    print("benchmark f_a=1e12 theta=1:", bm, "WKB:", out["benchmark_wkb"], flush=True)
    out["benchmark_fa1e12_theta1_n7"] = omega(1e12, 1.0, 7.0)
    print("n=7:", out["benchmark_fa1e12_theta1_n7"], flush=True)
    rows = []
    for Ms, ys in ((1e13, 0.305), (1e13, 0.389), (3e12, 0.31), (3e12, 0.39)):
        vS = np.sqrt(2) * Ms / ys
        fa = vS / 17
        ma = 5.70e-6 * 1e12 / fa
        th = theta_dm(fa)
        th7 = theta_dm(fa, 7.0) if Ms == 1e13 and ys == 0.305 else None
        # Planck 2018: beta_iso < 0.038 at k=0.05 (uncorrelated CDI), P_zeta = 2.1e-9; P_S = (H/(pi fa theta))^2 (Omega_a = Omega_DM)
        PS_max = 0.038 / (1 - 0.038) * 2.1e-9
        HI = np.pi * fa * th * np.sqrt(PS_max)
        rows.append(dict(Ms=Ms, ys=ys, vS=vS, fa=fa, ma_ueV=ma * 1e6, theta_i=th, theta_i_n7=th7, HI_max=HI,
                         gagg=(1 / 137.036) / (2 * np.pi * fa) * abs(8 / 3 - 1.92), Vquarter=(3 * HI ** 2 * 2.435e18 ** 2) ** 0.25))
        print(rows[-1], flush=True)
    out["points"] = rows
    with open(sys.argv[1] if len(sys.argv) > 1 else "verify_axion.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=float)
