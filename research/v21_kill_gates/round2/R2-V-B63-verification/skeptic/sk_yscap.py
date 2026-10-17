"""Skeptic: rough, independent y_s perturbativity cap for B63 (NUM, deliberately simple, grouped components).

Groups at M_s = 1e13 with universal y: y16 (48 components = three S-mass 16-pairs), y10 (10 components, T pair),
yN (4 Dirac-equivalent SO(10)-singlet components: N1N1b, N2N2b, N3N3b, NMm).  One-loop:
  16pi^2 dy_g/dt = y_g (gamma_S + y_g^2 - G_g(t)),   gamma_S = 48 y16^2 + 10 y10^2 + 4 yN^2
G_16 = 6 * sum_a g_a^2 <C_a>(16): below M_U average G3221 Casimir sum 15/8 (SU3 1, SU2L 3/8, SU2R 3/8, BL 1/8),
above M_U C2(16) = 45/8.  G_10: below 3/2, above 9/2.  Singlets: 0 (g_X off) or 3 g_X^2 (X1^2+X2^2) (optional).
Gauge: alpha^-1 linear in ln mu from A0 at M_s to 25.9 at M_U = 2.13e16 (G3221 treated with one common coupling);
above M_U: (a) one-loop b = 8, (b) the R2-V-type two-loop curve reaching alpha^-1(MPl) = 5.16 (fitted by
integrating d alpha/dt = (b1 alpha^2 + b2 alpha^3/(4pi)) / (2pi) with b1 = 8, b2 = 7267/2).
Cap = largest y0 with all y <= sqrt(4 pi) up to MPl,red = 2.435e18.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
MS, MU, MPL = 1e13, 2.13e16, 2.435e18
AU = 25.9
X1 = {"N": [(63, 59), (58, 54), (57, 61), (2, 2)]}


def alpha_inv_above(t_rel, mode):
    """t_rel = ln(mu/MU)."""
    if mode == "1loop":
        return AU - 8 / (2 * math.pi) * t_rel
    return None


def two_loop_curve():
    b1, b2 = 8.0, 7267 / 2

    def f(t, y):
        a = y[0]
        return [(b1 * a * a + b2 * a ** 3 / (4 * math.pi)) / (2 * math.pi)]
    T = math.log(MPL / MU)
    sol = solve_ivp(f, [0, T], [1 / AU], dense_output=True, rtol=1e-10, atol=1e-14)
    return sol


TL = two_loop_curve()


def g2(t, A0, above):
    """t = ln(mu/MS)."""
    tU = math.log(MU / MS)
    if t <= tU:
        ainv = A0 + (AU - A0) * t / tU
        return 4 * math.pi / ainv, False
    tr = t - tU
    if above == "1loop":
        ainv = AU - 8 / (2 * math.pi) * tr
        return 4 * math.pi / ainv, True
    a = TL.sol(tr)[0]
    return 4 * math.pi * a, True


def run(y0, A0, above, singlet_scale=1.0):
    T = math.log(MPL / MS)
    lim = math.sqrt(4 * math.pi)

    def f(t, y):
        y16, y10, yN = y
        gg, hi = g2(t, A0, above)
        gS = 48 * y16 ** 2 + 10 * y10 ** 2 + 4 * yN ** 2
        G16 = 6 * gg * (45 / 8 if hi else 15 / 8)
        G10 = 6 * gg * (9 / 2 if hi else 3 / 2)
        k = 1 / (16 * math.pi ** 2)
        return [k * y16 * (gS + y16 ** 2 - G16), k * y10 * (gS + y10 ** 2 - G10), k * yN * (gS + yN ** 2)]

    def ev(t, y):
        return lim - max(y)
    ev.terminal = True
    sol = solve_ivp(f, [0, T], [y0, y0, y0 * singlet_scale], events=ev, rtol=1e-9, atol=1e-12, max_step=0.05)
    return sol.status == 0 and max(sol.y[:, -1]) <= lim, sol.y[:, -1]


def cap(A0, above, singlet_scale=1.0):
    lo, hi = 0.2, 0.6
    for _ in range(50):
        m = 0.5 * (lo + hi)
        ok, _ = run(m, A0, above, singlet_scale)
        lo, hi = (m, hi) if ok else (lo, m)
    return lo


def main():
    out = {"two_loop_alpha_inv_at_MPl": 1 / TL.sol(math.log(MPL / MU))[0]}
    for A0 in (30.0, 40.0):
        for above in ("1loop", "2loop"):
            out["A0=%g %s" % (A0, above)] = cap(A0, above)
    # no gauge reference
    print(json.dumps(out, indent=1))
    (HERE / "sk_yscap.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
