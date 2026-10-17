"""Independent misalignment + isocurvature check (verifier), fast version.

theta'' + 3H theta' + m_a(T)^2 sin(theta) = 0 integrated in u = ln t with H = 1/(2t) (radiation domination) and
T(H) from a tabulated inversion of H = 1.66 sqrt(g_*(T)) T^2 / M_Pl (M_Pl = 1.2209e19), g_* a smooth tanh crossover
(independent of the researcher's table).  chi(T) = chi_0 min(1, (T_c/T)^n), chi_0^{1/4} = 75.5 MeV, T_c = 150 MeV,
n = 8.16 (and 7.0).  Omega_a h^2 = 2.74e8 (m_a/GeV) (n_a/s)(T_end).
"""
import json
import numpy as np
from scipy.integrate import solve_ivp

MPL = 1.2209e19
CHI0 = 0.0755 ** 4
TC = 0.150
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\v_axion_independent.json"


def gstar(T):
    T = np.asarray(T, dtype=float)
    g = 10.75 + (61.75 - 10.75) * 0.5 * (1 + np.tanh(np.log(T / 0.17) / 0.35))
    g += 13.0 * 0.5 * (1 + np.tanh(np.log(T / 1.5) / 0.5))
    g += 11.0 * 0.5 * (1 + np.tanh(np.log(T / 8.0) / 0.5))
    return g


def H_T(T):
    return 1.66 * np.sqrt(gstar(T)) * T * T / MPL


# tabulate ln T vs ln H on a fine grid (H monotonic in T)
_T = np.geomspace(1e-3, 1e3, 20001)
_lnH = np.log(H_T(_T))
_lnT = np.log(_T)


def T_of_H(H):
    return np.exp(np.interp(np.log(H), _lnH, _lnT))


def chi(T, n):
    return CHI0 if T < TC else CHI0 * (TC / T) ** n


def omega_a(fa, th0, n=8.16):
    ma = lambda T: np.sqrt(chi(T, n)) / fa
    lo, hi = 1e-2, 1e3
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        if ma(mid) / H_T(mid) < 1e-3:
            hi = mid
        else:
            lo = mid
    T0 = hi
    t0 = 1.0 / (2 * H_T(T0))

    def rhs(u, y):
        t = np.exp(u)
        th, dth = y
        H = 1.0 / (2 * t)
        T = T_of_H(H)
        m2 = chi(T, n) / fa ** 2
        return [t * dth, t * (-3 * H * dth - m2 * np.sin(th))]

    def ev(u, y):
        t = np.exp(u)
        H = 1.0 / (2 * t)
        return 3000.0 - ma(T_of_H(H)) / H
    ev.terminal = True
    sol = solve_ivp(rhs, (np.log(t0), np.log(t0) + 40), [th0, 0.0], method="DOP853", rtol=1e-9, atol=1e-13, events=ev, max_step=0.005)
    t = np.exp(sol.t[-1])
    H = 1.0 / (2 * t)
    T = float(T_of_H(H))
    th, dth = sol.y[:, -1]
    m2 = chi(T, n) / fa ** 2
    rho = 0.5 * fa ** 2 * dth ** 2 + m2 * fa ** 2 * (1 - np.cos(th))
    na = rho / np.sqrt(m2)
    s = 2 * np.pi ** 2 / 45 * float(gstar(T)) * T ** 3
    return 2.74e8 * (np.sqrt(CHI0) / fa) * na / s, T


def theta_dm(fa, n=8.16):
    lo, hi = 0.05, 3.0
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        if omega_a(fa, mid, n)[0] < 0.12:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    out = {}
    om, Tend = omega_a(1e12, 1.0)
    out["benchmark_fa1e12_theta1"] = dict(Omega_h2=om, T_end=Tend)
    print("benchmark f_a=1e12 theta=1:", om, "T_end", Tend, flush=True)
    out["points"] = []
    for Ms, ys in ((1e13, 0.305), (1e13, 0.389), (3e12, 0.31), (3e12, 0.39)):
        vS = np.sqrt(2) * Ms / ys
        vPhi = np.sqrt(2) * 1e17
        fa_exact = vS * vPhi / np.sqrt((4 * vS) ** 2 + (17 * vPhi) ** 2)
        fa = vS / 17
        th = theta_dm(fa)
        th7 = theta_dm(fa, 7.0)
        HI = np.pi * fa * th * np.sqrt(0.038 / 0.962 * 2.1e-9)
        rec = dict(M_s=Ms, y_s=ys, v_S=vS, f_a=fa, f_a_exact_vPhi1e17=fa_exact, m_a_ueV=5.70 * 1e12 / fa,
                   theta_i=th, theta_i_n7=th7, H_I_max=HI, check_Omega=omega_a(fa, th)[0])
        out["points"].append(rec)
        print(json.dumps(rec), flush=True)
    json.dump(out, open(OUT, "w"), indent=1)
