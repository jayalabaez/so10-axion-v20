"""Verifier: independent one-loop y_s cap.  Beta function derived independently (verifier notes):
  for y_i S* psi_i chi_i with S a complex singlet: 16 pi^2 dy_k/dt = y_k [ sum_i d_i y_i^2 + y_k^2 - 3 sum g^2 (C2(psi)+C2(chi)) ]
  (no one-loop vertex correction: the exchanged complex scalar would need <S* S*>; checked against SM top 9/2).
  sum d_i = 3*16 + 10 + 2 = 60 (universal y).
Gauge treatments: (a) none; (b) full SO(10) coupling from M_s upward (over-estimates the gauge damping below M_U:
  gives an UPPER bound on the cap); (c) the component with the least gauge charge (nu^c-like): zero below v_R,
  SU(2)_R x U(1)_B-L between v_R and M_U with the researcher's G3221 one-loop b's, SO(10) above M_U.
SO(10) one-loop b1 = -11/3*8 + 2/3*T_f + 1/3*T_cplx + 1/6*T_real:  fermions: 11 x 16 (T=2) + 2 x 10 (T=1) = 24;
  scalars: 210 real (56/6), 126bar complex (35/3), 10 complex (1/3): b1 = -88/3 + 16 + 28/3 + 35/3 + 1/3 = 8.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
PI = math.pi
MPL = 2.435e18
MU = 2.13e16
VR = 2.6e13
AU_INV = 25.9
SUMD = 60.0

b1 = Fr(-11, 3) * 8 + Fr(2, 3) * (11 * 2 + 2 * 1) + Fr(1, 6) * 56 + Fr(1, 3) * 35 + Fr(1, 3) * 1
assert b1 == 8, b1
# G3221 (SU3, SU2L, SU2R, B-L GUT-normalised) one-loop b's from the researcher (T2 + F17): (65/6, 12, 47/3, 49/3)
B3221 = (65 / 6, 12.0, 47 / 3, 49 / 3)


def alpha_inv_so10(mu):
    return AU_INV - float(b1) / (2 * PI) * math.log(mu / MU)


def alpha_inv_3221(mu):
    return [AU_INV - b / (2 * PI) * math.log(mu / MU) for b in B3221]


def gauge_term(mu, variant):
    if variant == "none":
        return 0.0
    if variant == "so10_everywhere":
        return 3 * 2 * (45 / 8) * 4 * PI / alpha_inv_so10(mu)
    # least gauged: nu^c-like component (1,1,2)_{B-L=1} of the 16: C2(SU2R) = 3/4, T_BL^2 = 3/8 * 1
    if mu < VR:
        return 0.0
    if mu < MU:
        a = alpha_inv_3221(mu)
        g2r2 = 4 * PI / a[2]
        gbl2 = 4 * PI / a[3]
        return 3 * 2 * (0.75 * g2r2 + 0.375 * gbl2)
    return 3 * 2 * (45 / 8) * 4 * PI / alpha_inv_so10(mu)


def run(y0, ms, variant):
    def rhs(t, v):
        y = v[0]
        return [y * ((SUMD + 1) * y * y - gauge_term(math.exp(t), variant)) / (16 * PI ** 2)]

    def ev(t, v):
        return v[0] - 4.0
    ev.terminal = True
    sol = solve_ivp(rhs, [math.log(ms), math.log(MPL)], [y0], rtol=1e-9, atol=1e-12, max_step=0.05, events=ev)
    hit = len(sol.t_events[0]) > 0
    return hit, float(np.max(sol.y[0])), float(sol.y[0, -1])


def cap(ms, variant, ylim=math.sqrt(4 * PI)):
    lo, hi = 0.05, 2.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        hit, ymax, _ = run(mid, ms, variant)
        if (not hit) and ymax <= ylim:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    out = {}
    for ms in (3.0e12, 1.0e13):
        analytic = math.sqrt(16 * PI ** 2 / (2 * (SUMD + 1) * math.log(MPL / ms)))
        row = {"analytic_pure_Yukawa_pole_at_MPl": analytic}
        for variant in ("none", "least_gauged", "so10_everywhere"):
            row[variant] = cap(ms, variant)
        out["M_s=%.0e" % ms] = row
        print(ms, json.dumps(row, indent=1))
    (HERE / "v4_ys_cap.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
