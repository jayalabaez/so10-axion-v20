"""sk2: own recomputation of the NUM quality numbers of R2-V (dtheta_tree, <S>_max, y_s floor, no-gauge cap, f_a, m_a,
tolerances) plus a sensitivity scan of the SO(10) coupling at M_Pl,red (two-loop, complete-multiplet b's recomputed
here from the field content) which drives the small-instanton caveat.  Writes sk2_numbers.json."""
from __future__ import annotations

import json
import math
from fractions import Fraction as Fr
from pathlib import Path

from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
MPL = 2.435e18
CHI = 0.0755 ** 4            # chi^(1/4) = 75.5 MeV (LIT-abstract 1511.02867 / 1812.01008)
MA_COEF = 5.70e-6            # m_a = 5.70 ueV x 1e12 GeV / f_a  (same LIT)
PHI = 1.0e17
MS = 1.0e13
PI = math.pi


def dtheta(S, P=PHI, g=1.0, M=MPL):
    # V = g |S|^17 |Phi17|^4 / M^17 (e^{i delta} + c.c.)  ->  dtheta <= 2 g ... / chi
    return 2 * g * (S / M) ** 17 * (P / M) ** 4 * M ** 4 / CHI


def s_max(P=PHI, g=1.0, M=MPL, target=1e-10):
    return M * (target * CHI / (2 * g * (P / M) ** 4 * M ** 4)) ** (1 / 17)


def nogauge_cap(Ms=MS, ncomp=62, ymax=math.sqrt(4 * PI)):
    # 16 pi^2 dy/dt = (ncomp + 1) y^3  (gamma_S = ncomp y^2, legs y^2/2 + y^2/2), universal y
    return 1 / math.sqrt(1 / ymax ** 2 + 2 * (ncomp + 1) * math.log(MPL / Ms) / (16 * PI ** 2))


def so10_b():
    # SO(10) above M_U: fermions 11 x 16 + 2 x 10 (Weyl); scalars 210 real, 126bar complex, 10 complex, singlets
    CG = Fr(8)
    T = {"10": Fr(1), "16": Fr(2), "126": Fr(35), "210": Fr(56)}
    C2 = {"10": Fr(9, 2), "16": Fr(45, 8), "126": Fr(25, 2), "210": Fr(12)}
    b1 = Fr(-11, 3) * CG + Fr(2, 3) * (11 * T["16"] + 2 * T["10"]) + Fr(1, 3) * (T["126"] + T["10"]) + Fr(1, 6) * T["210"]
    # MV two-loop: b2 = -34/3 C_G^2 + sum_Weyl (10/3 C_G + 2 C2) T + sum_complex-scalar (2/3 C_G + 4 C2) T (real: x1/2)
    b2 = Fr(-34, 3) * CG ** 2
    b2 += (Fr(10, 3) * CG + 2 * C2["16"]) * T["16"] * 11 + (Fr(10, 3) * CG + 2 * C2["10"]) * T["10"] * 2
    b2 += (Fr(2, 3) * CG + 4 * C2["126"]) * T["126"] + (Fr(2, 3) * CG + 4 * C2["10"]) * T["10"]
    b2 += (Fr(2, 3) * CG + 4 * C2["210"]) * T["210"] * Fr(1, 2)
    return b1, b2


B1, B2 = so10_b()


def ainv_at(MU, ainvU, mu_end=MPL, two_loop=True):
    def rhs(t, y):
        return [-float(B1) / (2 * PI) - (float(B2) / (8 * PI ** 2) / y[0] if two_loop else 0.0)]

    def hit(t, y):
        return y[0] - 0.05
    hit.terminal = True
    sol = solve_ivp(rhs, [math.log(MU), math.log(mu_end)], [ainvU], rtol=1e-10, atol=1e-12, events=hit)
    if sol.t_events[0].size:
        return None, math.exp(sol.t_events[0][0])
    return float(sol.y[0, -1]), None


def main():
    out = {}
    out["dtheta_tree"] = {f"{S:.3g}": dtheta(S) for S in (2.72e13, 3.0e13, 3.29e13, 3.6e13)}
    smax = s_max()
    out["S_max(1e-10)"] = smax
    out["margin_at_3e13"] = 1e-10 / dtheta(3e13)
    out["y_s_floor = M_s/S_max"] = MS / smax
    out["nogauge_cap(y<=sqrt4pi)"] = nogauge_cap()
    out["nogauge_cap(y<=1)"] = nogauge_cap(ymax=1.0)
    out["f_a range (sqrt2 <S>/17) for y_s in [0.304,0.368]"] = [math.sqrt(2) * MS / 0.368 / 17, math.sqrt(2) * MS / 0.304 / 17]
    fa = out["f_a range (sqrt2 <S>/17) for y_s in [0.304,0.368]"]
    out["m_a_ueV"] = [MA_COEF * 1e12 / fa[1] * 1e6, MA_COEF * 1e12 / fa[0] * 1e6]
    out["S_range for window"] = [MS / 0.368, MS / 0.304]
    out["dtheta at S = M_s/0.304 (upper S end)"] = dtheta(MS / 0.304)
    # tolerances
    out["supp_scale_min_over_MPl (margin^-1/17 at 3e13)"] = (dtheta(3e13) / 1e-10) ** (1 / 17)
    out["g_tol(cap 0.368)"] = 1e-10 / dtheta(MS / 0.368)
    out["g_tol(floor 0.3166)"] = 1e-10 / dtheta(MS / nogauge_cap())
    out["Phi17_tol(cap 0.368)"] = PHI * (1e-10 / dtheta(MS / 0.368)) ** 0.25
    out["Phi17_tol(floor)"] = PHI * (1e-10 / dtheta(MS / nogauge_cap())) ** 0.25
    out["M_s max for window (cap x S_max)"] = {"floor 0.3166": 0.3166 * smax, "0.368": 0.368 * smax, "0.380": 0.380 * smax}
    # one-loop K=17 renormalisation of the tree coefficient (R2-V EST <= 35%): effect on floor
    out["y_s floor if coefficient x1.35"] = MS / s_max(g=1.35)
    out["y_s floor if coefficient x2"] = MS / s_max(g=2.0)
    out["y_s floor if coefficient x4.7"] = MS / s_max(g=4.7)
    # SO(10) running above M_U
    out["SO10_b1"] = str(B1)
    out["SO10_b2"] = str(B2)
    scan = {}
    for MU in (1.0e16, 1.5e16, 2.13e16, 3.0e16):
        for ainvU in (22.0, 24.0, 25.9, 28.0, 32.0, 36.0):
            a2, pole2 = ainv_at(MU, ainvU)
            a1, pole1 = ainv_at(MU, ainvU, two_loop=False)
            scan[f"M_U={MU:.3g}, aU^-1={ainvU}"] = {"ainv(MPl) 2L": a2, "Landau pole 2L": pole2, "ainv(MPl) 1L": a1}
    out["SO10_alpha_inv_at_MPl_scan"] = scan
    # critical alpha_U^-1 for a two-loop Landau pole exactly at M_Pl,red, by M_U
    crit = {}
    for MU in (1.0e16, 1.5e16, 2.13e16, 3.0e16):
        f = lambda a: (ainv_at(MU, a)[0] or 0.0) - 0.06  # noqa: E731
        try:
            crit[f"{MU:.3g}"] = brentq(f, 5.0, 60.0, xtol=1e-4)
        except Exception as e:  # pragma: no cover
            crit[f"{MU:.3g}"] = repr(e)
    out["alpha_U^-1 below which SO(10) hits a 2L Landau pole before M_Pl,red"] = crit
    # alpha_U^-1 needed for alpha^-1(MPl) = 3 (R2-V's SI danger value)
    crit3 = {}
    for MU in (1.0e16, 1.5e16, 2.13e16, 3.0e16):
        f = lambda a: (ainv_at(MU, a)[0] or 0.0) - 3.0  # noqa: E731
        try:
            crit3[f"{MU:.3g}"] = brentq(f, 5.0, 60.0, xtol=1e-4)
        except Exception as e:  # pragma: no cover
            crit3[f"{MU:.3g}"] = repr(e)
    out["alpha_U^-1 giving alpha^-1(MPl)=3"] = crit3
    (HERE / "sk2_numbers.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
