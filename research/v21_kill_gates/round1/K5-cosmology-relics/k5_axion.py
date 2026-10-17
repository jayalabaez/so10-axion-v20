"""K5 part (2): axion dark matter of v21-F17-G3221 (pre-inflationary PQ breaking).

f_a = v_S/17 (exact gauge-invariant phase, k5_rodd_sector.py), v_S = sqrt2 M_s / y_s.
m_a = 5.70 ueV (1e12 GeV / f_a)   [LIT: 1511.02867]
Misalignment: theta'' + 3 H theta' + m_a(T)^2 sin theta = 0 with m_a(T)^2 = chi(T)/f_a^2,
chi(T) = chi_0 for T < T_c, chi_0 (T_c/T)^n above, chi_0^{1/4} = 75.5 MeV, T_c = 150 MeV, n = 8.16 (lattice) [LIT-abstract],
radiation domination with a g_*(T) table.  Ω_a h^2 = 2.74e8 (m_a/GeV) (n_a/s)_final.
Isocurvature: P_S = (Ω_a/Ω_DM)^2 (H_I/(pi f_a theta_i))^2 ; beta_iso = P_S/(P_S+P_zeta) < 0.038 [LIT: Planck 2018, k=0.05]
 -> H_I < pi f_a theta_i sqrt(0.038/0.962 * 2.1e-9) = 2.86e-5 f_a theta_i (Ω_a = Ω_DM).
"""
from __future__ import annotations
import json
import numpy as np
from scipy.integrate import solve_ivp

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\k5_axion.json"
MPL = 1.2209e19       # non-reduced Planck mass for H = 1.66 sqrt(g) T^2/M_Pl
CHI0 = (0.0755) ** 4  # GeV^4
TC = 0.150
# g_* table (T in GeV): approximate standard values (QCD-transition region is the main uncertainty)
GT = np.array([1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0, 300.0, 1e3, 1e4])
GS = np.array([3.36, 10.75, 10.75, 10.9, 12.0, 17.5, 35.0, 50.0, 58.0, 66.0, 73.0, 78.0, 86.0, 92.0, 96.0, 105.0, 106.75, 106.75])

def gstar(T):
    return float(np.interp(np.log10(T), np.log10(GT), GS))

def chi(T, n=8.16):
    return CHI0 if T < TC else CHI0 * (TC / T) ** n

def H_of_T(T):
    return 1.66 * np.sqrt(gstar(T)) * T ** 2 / MPL

def omega_misalignment(fa, theta_i, n=8.16):
    """Return Omega_a h^2 for initial angle theta_i (radians), f_a in GeV."""
    ma0 = np.sqrt(CHI0) / fa
    # start where m_a(T)/H = 1e-3 : find T_start by bisection on log T
    def ratio(T):
        return np.sqrt(chi(T, n)) / fa / H_of_T(T)
    lo, hi = 1e-2, 1e3
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if ratio(mid) < 1e-3:
            hi = mid
        else:
            lo = mid
    T0 = hi
    # time variable: t = 1/(2H) in radiation domination (ignoring d g/dT); integrate in u = ln(t)
    # H = 1/(2t);  T(t) from H(T) = 1/(2t) by inversion (bisection) -- cache by solving ODE in T instead:
    # use dT/dt = -H T (constant g approx) => integrate in x = ln(T0/T): dt = dx/H
    def rhs(x, y):
        th, dth = y          # dth = d theta/dt
        T = T0 * np.exp(-x)
        H = H_of_T(T)
        m2 = chi(T, n) / fa ** 2
        # d/dx = (1/H) d/dt
        return [dth / H, (-3 * H * dth - m2 * np.sin(th)) / H]
    # stop when m_a/H > 2e3 (adiabatic), or T < 10 MeV
    def stop(x, y):
        T = T0 * np.exp(-x)
        return 2e3 - np.sqrt(chi(T, n)) / fa / H_of_T(T)
    stop.terminal = True
    sol = solve_ivp(rhs, (0.0, np.log(T0 / 0.01)), [theta_i, 0.0], method="DOP853", rtol=1e-9, atol=1e-12, events=stop, max_step=0.01)
    x_end = sol.t[-1]
    T_end = T0 * np.exp(-x_end)
    th, dth = sol.y[:, -1]
    m2 = chi(T_end, n) / fa ** 2
    rho = 0.5 * fa ** 2 * dth ** 2 + m2 * fa ** 2 * (1 - np.cos(th))
    # average over the last oscillations to reduce phase noise: use energy / m (adiabatic number)
    n_a = rho / np.sqrt(m2)
    s = 2 * np.pi ** 2 / 45 * gstar(T_end) * T_end ** 3
    Y = n_a / s
    # T_osc (3H = m_a) for information
    lo, hi = 1e-2, 1e3
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if np.sqrt(chi(mid, n)) / fa < 3 * H_of_T(mid):
            hi = mid
        else:
            lo = mid
    return dict(Omega_h2=2.74e8 * ma0 * Y, T_osc=hi, T_end=T_end, Y=Y, ma0_eV=ma0 * 1e9)

def theta_for_dm(fa, n=8.16, target=0.12):
    lo, hi = 0.01, 3.1
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if omega_misalignment(fa, mid, n)["Omega_h2"] < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

if __name__ == "__main__":
    out = {"points": []}
    # benchmark check: f_a = 1e12, theta = 1
    bm = omega_misalignment(1e12, 1.0)
    out["benchmark_fa1e12_theta1"] = bm
    print("benchmark f_a=1e12, theta_i=1:", bm)
    # power-law fit of Omega(theta=1) vs f_a (for the report)
    fas = [1e11, 3e11, 1e12, 3e12, 1e13]
    oms = [omega_misalignment(f, 1.0)["Omega_h2"] for f in fas]
    slope = np.polyfit(np.log(fas), np.log(oms), 1)[0]
    out["Omega_theta1_vs_fa"] = dict(zip([f"{f:.0e}" for f in fas], oms))
    out["power_law_index"] = float(slope)
    print("Omega(theta=1) vs f_a:", dict(zip(fas, oms)), "index", slope)
    # configuration points: M_s = 1e13, y_s in [0.305, 0.389] (three-loop point); M_s = 3e12 (two-loop end)
    for Ms, ys, label in ((1e13, 0.305, "three-loop point, y_s=0.305"), (1e13, 0.35, "three-loop point, y_s=0.35"), (1e13, 0.389, "three-loop point, y_s=0.389"), (1e13, 0.40, "y_s=0.40 (ADMX-excluded per FINAL)"), (3e12, 0.31, "two-loop low end, y_s=0.31"), (3e12, 0.39, "two-loop low end, y_s=0.39")):
        vS = np.sqrt(2) * Ms / ys
        fa = vS / 17.0
        ma = 5.70e-6 * 1e12 / fa
        th = theta_for_dm(fa)
        th7 = theta_for_dm(fa, n=7.0)
        HI = 2.86e-5 * fa * th
        rec = dict(label=label, M_s=Ms, y_s=ys, v_S=vS, f_a=fa, m_a_ueV=ma * 1e6,
                   g_agg_GeV_inv=(1 / 137.036) / (2 * np.pi * fa) * abs(8 / 3 - 1.92),
                   theta_i_for_Omega_DM=th, theta_i_n7=th7,
                   Omega_check=omega_misalignment(fa, th)["Omega_h2"],
                   H_I_max_GeV=HI, H_I_max_conservative_half=HI / 2,
                   r_tensor_at_HI_max=2 * HI ** 2 / (np.pi ** 2 * 2.435e18 ** 2) / 2.1e-9,
                   V_quarter_GeV=(3 * HI ** 2 * 2.435e18 ** 2) ** 0.25,
                   T_RH_max_instant=(90 / (np.pi ** 2 * 106.75)) ** 0.25 * np.sqrt(HI * 2.435e18))
        out["points"].append(rec)
        print(json.dumps(rec))
    # ADMX bands (LIT): DFSZ excluded 2.66-2.81 (1804.05750) and 2.81-3.31 ueV (1910.08638); 3.3-4.2 KSVZ only (2110.06096)
    out["ADMX_DFSZ_excluded_ueV"] = [[2.66, 2.81], [2.81, 3.31]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
