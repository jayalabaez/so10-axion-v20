"""One-loop running of charged-fermion Yukawas, CKM and the neutrino mass matrix.

Low-energy theory below M_I: type-II 2HDM (the manuscript uses 2HDM gauge
coefficients (21/5,-3,-7) below M_I).  An SM mode is kept for validation
against Huang & Zhou, PRD 103, 016010 (2021), Tables 2-3.

Inputs at mu = M_Z: MS-bar effective masses m_f = y_f v_F/sqrt2 (full SM),
Huang & Zhou Table 2/3, v_F = 246 GeV.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.integrate import solve_ivp

K = 16.0 * math.pi ** 2
MZ = 91.1876
VEV = 246.0 / math.sqrt(2.0)                        # Huang-Zhou effective-mass normalisation

# Huang & Zhou (2021), full SM, mu = M_Z  [GeV]
MASS_MZ = {"u": 1.23e-3, "c": 0.620, "t": 168.26,
           "d": 2.67e-3, "s": 53.16e-3, "b": 2.839,
           "e": 0.48307e-3, "mu": 0.101766, "tau": 1.72856}
REL_ERR_MZ = {"u": 0.21/1.23, "c": 0.017/0.620, "t": 0.75/168.26,
              "d": 0.19/2.67, "s": 4.61/53.16, "b": 0.026/2.839,
              "e": 0.00045/0.48307, "mu": 0.000023/0.101766, "tau": 0.00028/1.72856}
# Huang & Zhou (2021) Table 5, full SM at M_Z
G_MZ = {"gp": 0.357254, "g2": 0.65100, "g3": 1.2104}
# Huang & Zhou (2021) Tables 2,3,5 at mu = 1e12 GeV (validation targets)
HZ_1E12 = {"t": 85.07, "b": 1.194, "c": 0.283, "s": 24.76e-3, "d": 1.24e-3,
           "u": 0.56e-3, "tau": 1.73194, "mu": 0.101936, "e": 0.48388e-3,
           "g3": 0.6017, "g2": 0.55325, "gp": 0.414821}

# PDG 2024 CKM (Wolfenstein fit) -- magnitudes and Jarlskog at low energy
CKM_LOW = {"s12": (0.22501, 0.00068), "s23": (0.04182, 0.00085),
           "s13": (0.00369, 0.00011), "J": (3.08e-5, 0.15e-5)}


def _rhs(t, y, mode, lam2):
    yu, yd, ye = y[0:3], y[3:6], y[6:9]
    g1, g2, g3 = y[9], y[10], y[11]
    su, sd, se = yu**2, yd**2, ye**2
    if mode == "2hdm":
        b = (21.0/5.0, -3.0, -7.0)
        cross = 0.5
        Tu = 3*su.sum(); Td = 3*sd.sum() + se.sum(); Te = Td
    else:  # SM
        b = (41.0/10.0, -19.0/6.0, -7.0)
        cross = -1.5
        T = 3*su.sum() + 3*sd.sum() + se.sum(); Tu = Td = Te = T
    Gu = 8*g3**2 + 2.25*g2**2 + 0.85*g1**2
    Gd = 8*g3**2 + 2.25*g2**2 + 0.25*g1**2
    Ge = 2.25*g2**2 + 2.25*g1**2
    qcd2 = -108.0*g3**4/K              # two-loop QCD, n_f = 6 (dominant 2-loop term)
    dyu = yu*(1.5*su + cross*sd + Tu - Gu + qcd2)/K
    dyd = yd*(1.5*sd + cross*su + Td - Gd + qcd2)/K
    dye = ye*(1.5*se + Te - Ge)/K
    dg = np.array([b[0]*g1**3, b[1]*g2**3, b[2]*g3**3 - 26.0*g3**5/K])/K
    # accumulators: CKM log-running of s13,s23 ; neutrino integrals
    ckm_coef = 0.5 if mode == "2hdm" else 1.5
    d_ln_s = -ckm_coef*(su[2] + sd[2])/K
    if mode == "2hdm":
        alpha = -3*g2**2 + lam2 + 6*su.sum()
        ce = 0.5
    else:
        T = 3*su.sum() + 3*sd.sum() + se.sum()
        alpha = -3*g2**2 + lam2 + 2*T
        ce = -1.5
    d_Ia = alpha/K
    d_Ie = se/K
    return np.concatenate([dyu, dyd, dye, dg, [d_ln_s, d_Ia], d_Ie, [ce*0.0]])


def run(mu_high, tan_beta=None, mode="2hdm", lam2=0.5):
    """Integrate M_Z -> mu_high. Returns masses at mu_high (in tree-vev units),
    CKM magnitudes at mu_high, and neutrino running data for M_Z <- mu_high."""
    if mode == "2hdm":
        sb = math.sin(math.atan(tan_beta)); cb = math.cos(math.atan(tan_beta))
        vu, vd = VEV*sb, VEV*cb
    else:
        vu = vd = VEV
    m = MASS_MZ
    y0 = np.array([m["u"]/vu, m["c"]/vu, m["t"]/vu,
                   m["d"]/vd, m["s"]/vd, m["b"]/vd,
                   m["e"]/vd, m["mu"]/vd, m["tau"]/vd,
                   math.sqrt(5.0/3.0)*G_MZ["gp"], G_MZ["g2"], G_MZ["g3"],
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sol = solve_ivp(_rhs, (math.log(MZ), math.log(mu_high)), y0, args=(mode, lam2),
                    method="DOP853", rtol=1e-10, atol=1e-13)
    Y = sol.y[:, -1]
    yu, yd, ye = Y[0:3], Y[3:6], Y[6:9]
    ln_s, Ia, Ie = Y[12], Y[13], Y[14:17]
    ce = 0.5 if mode == "2hdm" else -1.5
    return {
        "masses": {"u": yu[0]*vu, "c": yu[1]*vu, "t": yu[2]*vu,
                   "d": yd[0]*vd, "s": yd[1]*vd, "b": yd[2]*vd,
                   "e": ye[0]*vd, "mu": ye[1]*vd, "tau": ye[2]*vd},
        "yukawas_max": float(max(yu.max(), yd.max(), ye.max())),
        "gauge": {"g1": Y[9], "g2": Y[10], "g3": Y[11],
                  "gp": Y[9]/math.sqrt(5.0/3.0)},
        "ckm_high": {"s12": CKM_LOW["s12"][0],
                     "s23": CKM_LOW["s23"][0]*math.exp(ln_s),
                     "s13": CKM_LOW["s13"][0]*math.exp(ln_s),
                     "J": CKM_LOW["J"][0]*math.exp(2*ln_s)},
        # m_nu_ij(M_Z) = exp(-Ia) * exp(-ce*(Ie_i+Ie_j)) * m_nu_ij(mu_high)
        "nu_scale": math.exp(-Ia),
        "nu_flavour": np.exp(-ce*Ie),
        "vu": vu, "vd": vd,
    }


if __name__ == "__main__":
    r = run(1e12, mode="sm", lam2=0.5)
    print("SM one-loop  M_Z -> 1e12 GeV   vs  Huang & Zhou (2021) multi-loop table")
    print(f"{'':>5} {'this code':>12} {'H&Z 2021':>12} {'rel diff':>9}")
    for k in ("t", "b", "c", "s", "d", "u", "tau", "mu", "e"):
        a, b = r["masses"][k], HZ_1E12[k]
        print(f"{k:>5} {a:12.5g} {b:12.5g} {100*(a-b)/b:8.2f}%")
    for k in ("g3", "g2", "gp"):
        a, b = r["gauge"][k], HZ_1E12[k]
        print(f"{k:>5} {a:12.5g} {b:12.5g} {100*(a-b)/b:8.2f}%")
