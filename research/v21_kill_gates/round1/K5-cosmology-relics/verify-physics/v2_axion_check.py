"""Second-pass axion check: f_a, m_a, misalignment theta_i for Omega_a = Omega_DM, isocurvature H_I,max.

Independent of both earlier codes: (i) solve the misalignment ODE in conformal-like variable u = ln(T0/T) with the
smooth lattice-inspired susceptibility chi(T) = chi_0 / (1 + (T/T_c)^n)   (no kink at T_c), n = 8.16 and 7.0,
and a g_*(T) table; (ii) compare with the standard adiabatic-invariant estimate (n_a/s frozen at 3H = m_a(T)).
(iii) Isocurvature: beta_iso < 0.038 -> H_I < pi f_a theta_i sqrt(beta/(1-beta) A_s).
"""
from __future__ import annotations
import json
import numpy as np
from scipy.integrate import solve_ivp

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-physics\v2_axion_check.json"
MPL_RED = 2.435e18
CHI0 = 0.0755 ** 4
TC = 0.150
GT = np.array([1e-3, 1e-2, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0, 1e3])
GS = np.array([10.75, 10.75, 11.0, 12.5, 20.0, 38.0, 52.0, 60.0, 68.0, 74.0, 80.0, 86.0, 97.0, 106.75])


def gstar(T):
    return float(np.interp(np.log10(T), np.log10(GT), GS))


def chi(T, n):
    return CHI0 / (1.0 + (T / TC) ** n)


def H(T):
    return np.sqrt(np.pi ** 2 * gstar(T) / 90) * T ** 2 / MPL_RED


def omega(fa, th0, n=8.16):
    m0 = np.sqrt(CHI0) / fa
    # start at T0 where m_a(T)/H = 1e-3
    T0 = 50.0
    while np.sqrt(chi(T0, n)) / fa / H(T0) > 1e-3:
        T0 *= 1.2
    # variables: theta, dtheta/dt ; independent u = ln(T0/T), dt = du / H (radiation, g_* slowly varying)
    def rhs(u, y):
        T = T0 * np.exp(-u)
        h = H(T)
        m2 = chi(T, n) / fa ** 2
        return [y[1] / h, (-3 * h * y[1] - m2 * np.sin(y[0])) / h]

    def done(u, y):
        T = T0 * np.exp(-u)
        return 3e3 - np.sqrt(chi(T, n)) / fa / H(T)
    done.terminal = True
    sol = solve_ivp(rhs, (0.0, np.log(T0 / 0.005)), [th0, 0.0], method="DOP853", rtol=1e-10, atol=1e-13, events=done, max_step=0.005)
    T = T0 * np.exp(-sol.t[-1])
    th, dth = sol.y[:, -1]
    m2 = chi(T, n) / fa ** 2
    rho = 0.5 * fa ** 2 * dth ** 2 + m2 * fa ** 2 * (1 - np.cos(th))
    n_a = rho / np.sqrt(m2)
    s = 2 * np.pi ** 2 / 45 * gstar(T) * T ** 3
    return 2.74e8 * m0 * n_a / s


def omega_adiabatic(fa, th0, n=8.16):
    # T_osc: 3 H = m_a(T)
    lo, hi = 0.05, 50.0
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        if np.sqrt(chi(mid, n)) / fa < 3 * H(mid):
            hi = mid
        else:
            lo = mid
    Tosc = hi
    m_osc = np.sqrt(chi(Tosc, n)) / fa
    F = (np.log(np.e / (1 - th0 ** 2 / np.pi ** 2))) ** 1.175   # anharmonic factor (Visinelli-Gondolo form)
    n_a = 0.5 * m_osc * fa ** 2 * th0 ** 2 * F
    s = 2 * np.pi ** 2 / 45 * gstar(Tosc) * Tosc ** 3
    return 2.74e8 * (np.sqrt(CHI0) / fa) * n_a / s, Tosc


def theta_dm(fa, n=8.16):
    lo, hi = 0.05, 3.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if omega(fa, mid, n) < 0.12:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    res = {}
    bm = omega(1e12, 1.0)
    bm7 = omega(1e12, 1.0, 7.0)
    ad, Tosc = omega_adiabatic(1e12, 1.0)
    res["benchmark_fa1e12_theta1"] = dict(numerical_n816=bm, numerical_n7=bm7, adiabatic_estimate=ad, Tosc=Tosc)
    print("benchmark f_a=1e12 theta=1: numerical n=8.16:", bm, " n=7:", bm7, " adiabatic:", ad, "T_osc", Tosc)
    pts = []
    for Ms, ys in ((1e13, 0.305), (1e13, 0.35), (1e13, 0.389), (3e12, 0.31), (3e12, 0.39)):
        vS = np.sqrt(2) * Ms / ys
        fa = vS / 17
        ma = 5.70e-6 * 1e12 / fa
        th = theta_dm(fa)
        th7 = theta_dm(fa, 7.0)
        beta = 0.038
        HI = np.pi * fa * th * np.sqrt(beta / (1 - beta) * 2.1e-9)
        HI7 = np.pi * fa * th7 * np.sqrt(beta / (1 - beta) * 2.1e-9)
        pts.append(dict(M_s=Ms, y_s=ys, f_a=fa, m_a_ueV=ma * 1e6, theta_i_n816=th, theta_i_n7=th7, H_I_max=HI, H_I_max_n7=HI7,
                        H_I_max_beta0035=HI * np.sqrt(0.035 / 0.965 / (0.038 / 0.962))))
        print(json.dumps(pts[-1]))
    res["points"] = pts
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=float)
