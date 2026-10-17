"""sk2: EST of how the gauge-resolved y_s perturbativity cap (y <= sqrt(4pi) or <= 1 up to M_Pl,red, all 62 S-coupled
Dirac-equivalent components universal at M_s = 1e13) moves when the round-1 (non-realisable) gauge environment is
replaced by the R2-B realisable-content unification points.  Own simplified one-loop model (not R2-V's code):
  - SM-component Casimirs for all scales below M_U (G3221 details ignored); gauge couplings: SM one loop from M_Z to M_s,
    then alpha_i^-1 interpolated linearly in ln mu from their M_s values to alpha_U^-1 at M_U (one-loop running is linear
    in ln mu inside a fixed content, so this is the content-independent part; the v_R kink is ignored);
  - SO(10) above M_U, two loop with b1 = 8, b2 = 7267/2 (sk2_numbers.py), 16 and 10 components merged by RMS;
  - singlets (N1, N2, N3, NMm) ungauged (U(1)_X off).
16 pi^2 dy_c/dt = y_c (gamma_S + y_c^2 - 6 sum_G g_G^2 C_G(c)),  gamma_S = sum_c d_c y_c^2.
Calibration: the same model in the round-1 environment should land near R2-V's 0.373-0.380.  EST only."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
PI = math.pi
L16 = 16 * PI ** 2
MZ, MS, MPL = 91.1876, 1.0e13, 2.435e18
AINV_MZ = np.array([59.02, 29.58, 8.47])  # (alpha_1 GUT-normalised, alpha_2, alpha_3)
B_SM = np.array([41 / 10, -19 / 6, -7.0])
B1, B2 = 8.0, 7267 / 2
# components: (d, (C_1 = 3/5 Y^2, C_2, C_3))
COMP16 = [(6, (0.6 / 36, 0.75, 4 / 3)), (3, (0.6 * 4 / 9, 0, 4 / 3)), (3, (0.6 / 9, 0, 4 / 3)), (2, (0.6 / 4, 0.75, 0)),
          (1, (0.6, 0, 0)), (1, (0, 0, 0))]
COMP10 = [(6, (0.6 / 9, 0, 4 / 3)), (4, (0.6 / 4, 0.75, 0))]
ENVS = {"round-1 T2+F17": (2.13e16, 25.9), "C0": (3.02e15, 33.26), "C1": (2.18e15, 33.53), "C2": (6.05e15, 34.64),
        "C1'": (3.20e15, 34.91)}


def a_ms():
    return AINV_MZ - B_SM / (2 * PI) * math.log(MS / MZ)


def run(y0, env, ymax):
    MU, aU = env
    ams = a_ms()

    def g2(mu):
        f = min(1.0, math.log(mu / MS) / math.log(MU / MS))
        return 4 * PI / (ams + f * (aU - ams))

    # below M_U: vector = 3 x COMP16 (identical copies -> one set with multiplicity 3) + COMP10 + 4 singlets
    n16, n10 = len(COMP16), len(COMP10)

    def rhs_low(t, v):
        mu = math.exp(t)
        gg = g2(mu)
        y16, y10, yN = v[:n16], v[n16:n16 + n10], v[n16 + n10:]
        gam = 3 * sum(d * y * y for (d, _), y in zip(COMP16, y16)) + sum(d * y * y for (d, _), y in zip(COMP10, y10)) + sum(y * y for y in yN)
        out = []
        for (d, C), y in zip(COMP16, y16):
            out.append(y * (gam + y * y - 6 * float(np.dot(gg, C))) / L16)
        for (d, C), y in zip(COMP10, y10):
            out.append(y * (gam + y * y - 6 * float(np.dot(gg, C))) / L16)
        for y in yN:
            out.append(y * (gam + y * y) / L16)
        return out

    def blow(t, v):
        return max(abs(x) for x in v) - ymax
    blow.terminal = True
    v0 = [y0] * (n16 + n10 + 4)
    s1 = solve_ivp(rhs_low, [math.log(MS), math.log(MU)], v0, rtol=1e-8, atol=1e-11, max_step=0.1, events=blow)
    if s1.t_events[0].size:
        return False
    e = s1.y[:, -1]
    y16 = math.sqrt(sum(d * y * y for (d, _), y in zip(COMP16, e[:n16])) / 16)
    y10 = math.sqrt(sum(d * y * y for (d, _), y in zip(COMP10, e[n16:n16 + n10])) / 10)
    yN = list(e[n16 + n10:])

    def rhs_hi(t, v):
        ainv, a16, a10 = v[0], v[1], v[2]
        yn = v[3:]
        g = 4 * PI / ainv
        gam = 48 * a16 ** 2 + 10 * a10 ** 2 + sum(y * y for y in yn)
        out = [-B1 / (2 * PI) - B2 / (8 * PI ** 2) / ainv,
               a16 * (gam + a16 ** 2 - 6 * g * 45 / 8) / L16,
               a10 * (gam + a10 ** 2 - 6 * g * 9 / 2) / L16]
        out += [y * (gam + y * y) / L16 for y in yn]
        return out

    def blow2(t, v):
        return max(abs(x) for x in v[1:]) - ymax
    blow2.terminal = True

    def pole(t, v):
        return v[0] - 0.05
    pole.terminal = True
    s2 = solve_ivp(rhs_hi, [math.log(MU), math.log(MPL)], [aU, y16, y10] + yN, rtol=1e-8, atol=1e-11, max_step=0.05,
                   events=[blow2, pole])
    if s2.t_events[0].size or s2.t_events[1].size:
        return False
    return True


def cap(env, ymax):
    lo, hi = 0.05, 1.0
    for _ in range(40):
        m = 0.5 * (lo + hi)
        if run(m, env, ymax):
            lo = m
        else:
            hi = m
    return lo


def main():
    out = {}
    for k, env in ENVS.items():
        out[k] = {"cap y<=sqrt(4pi)": cap(env, math.sqrt(4 * PI)), "cap y<=1": cap(env, 1.0)}
        print(k, out[k], flush=True)
    out["quality floor (sk2_numbers)"] = 0.3044
    (HERE / "sk2_yscap_env.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
