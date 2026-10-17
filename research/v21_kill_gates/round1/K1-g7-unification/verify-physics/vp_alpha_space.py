#!/usr/bin/env python3
"""Independent SO(10)-phase Landau-scale check in alpha-space (not alpha^-1), adaptive DOP853 with a terminal event,
starting from the (M_U, alpha_U^-1) of the verifier chain.  Also: analytic two-loop Landau scale (closed form) as a
sanity check, the scale where the three-loop term equals half / all of the two-loop term, and alpha(M_Pl,red).

  d alpha/dt = (alpha^2/2pi) [ b1 + b2 alpha/(4pi) - Y/(16 pi^2) + b3 alpha^2/(16 pi^2) ]
(equivalent to d alpha^-1/dt = -b1/2pi - b2 alpha/8pi^2 + Y/32pi^3 - b3 alpha^2/32pi^3).
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_coeffs as vc  # noqa: E402

PI = math.pi
MPL = 2.435e18
b_lo = [float(x) for x in vc.b123_single(8, vc.SO10_CONTENT)]
b_hi = [float(x) for x in vc.b123_single(8, vc.SO10_CONTENT + vc.SO10_PHI)]


def rhs_factory(b, Y, loops):
    b1, b2, b3 = b

    def f(t, y):
        a = y[0]
        br = b1
        if loops >= 2:
            br += b2 * a / (4 * PI) - Y / (16 * PI**2)  # d alpha^-1/dt = ... + Y/(32 pi^3)
        if loops >= 3:
            br += b3 * a * a / (16 * PI**2)
        return [a * a / (2 * PI) * br]
    return f


def landau(M_U, aU_inv, M_phi, Ylo, Yhi, loops, t_end=math.log(1e23)):
    def ev(t, y):
        return 1.0 - y[0]
    ev.terminal = True
    ev.direction = -1
    tu, tphi = math.log(M_U), math.log(max(M_phi, M_U))
    y0 = [1.0 / aU_inv]
    sol = solve_ivp(rhs_factory(b_lo, Ylo, loops), (tu, tphi), y0, method="DOP853", rtol=1e-11, atol=1e-14, events=ev,
                    dense_output=True)
    if sol.t_events[0].size:
        return math.exp(sol.t_events[0][0]), sol
    y1 = sol.y[:, -1]
    sol2 = solve_ivp(rhs_factory(b_hi, Yhi, loops), (tphi, t_end), y1, method="DOP853", rtol=1e-11, atol=1e-14, events=ev,
                     dense_output=True)
    lam = math.exp(sol2.t_events[0][0]) if sol2.t_events[0].size else float("inf")
    return lam, (sol, sol2)


def alpha_at(M, M_U, aU_inv, M_phi, Ylo, Yhi, loops):
    tu, tphi, tm = math.log(M_U), math.log(max(M_phi, M_U)), math.log(M)
    y0 = [1.0 / aU_inv]
    if tm <= tphi:
        s = solve_ivp(rhs_factory(b_lo, Ylo, loops), (tu, tm), y0, method="DOP853", rtol=1e-11, atol=1e-14)
        return s.y[0, -1]
    s = solve_ivp(rhs_factory(b_lo, Ylo, loops), (tu, tphi), y0, method="DOP853", rtol=1e-11, atol=1e-14)
    s2 = solve_ivp(rhs_factory(b_hi, Yhi, loops), (tphi, tm), s.y[:, -1], method="DOP853", rtol=1e-11, atol=1e-14)
    return s2.y[0, -1]


def two_loop_closed_form(M_U, aU_inv, b1, b2):
    """Pure two-loop (no Yukawa, single segment): t(a) = (1/A^2)[u - B ln u], u = A a + B, A = b1/2pi, B = b2/8pi^2."""
    A, B = b1 / (2 * PI), b2 / (8 * PI**2)
    u0, u1 = A * aU_inv + B, A * 1.0 + B
    dt = ((u0 - B * math.log(u0)) - (u1 - B * math.log(u1))) / A**2
    return M_U * math.exp(dt)


if __name__ == "__main__":
    out = {}
    # chain solutions from vp_chain_nominal.json (2L chain, Yukawa on, M_s = 1e13)
    nom = json.load(open(os.path.join(HERE, "vp_chain_nominal.json")))
    y_s, yt2, Y126 = 1e13 / 2.9e13, 0.95**2 * 0.0 + 0.0, 0.5  # y_t(M_U) is taken from the chain below
    for content in ("T2", "T3"):
        r = nom[f"{content}_2L_Ms1e+13_yuk1_Mphi1e+17"]
        M_U, aU = r["M_U"], r["alpha_U_inv"]
        # Yukawa norms as in the chain: Ylo = 14 y_s^2 + 10 y_t^2 + 15.75 Y126^2, Yhi = Ylo + 4 y_phi^2; y_t(M_U) ~ y_t(v_R) frozen
        # (the chain's cached value is not stored; use 0.50 as a representative frozen value and show the sensitivity)
        res = {}
        for yt in (0.45, 0.55):
            Ylo = 14 * y_s**2 + 10 * yt**2 + 15.75 * Y126**2
            Yhi = Ylo + 4.0
            for loops in (2, 3):
                lam, _ = landau(M_U, aU, 1e17, Ylo, Yhi, loops)
                res[f"yt={yt}_L{loops}_ratio"] = lam / MPL
                res[f"yt={yt}_L{loops}_alpha_inv_MPl"] = 1.0 / alpha_at(MPL, M_U, aU, 1e17, Ylo, Yhi, loops)
        # Yukawa off
        for loops in (2, 3):
            lam, _ = landau(M_U, aU, 1e17, 0.0, 0.0, loops)
            res[f"noYuk_L{loops}_ratio"] = lam / MPL
            lam, _ = landau(M_U, aU, 1e10, 0.0, 0.0, loops)
            res[f"noYuk_PhiAtMU_L{loops}_ratio"] = lam / MPL
        res["closed_form_2L_noYuk_PhiAtMU_ratio"] = two_loop_closed_form(M_U, aU, b_hi[0], b_hi[1]) / MPL
        # same-point comparison with the verifier chain's RK4 landau (alpha^-1 space, h = 0.002), Yukawa Y as in the chain
        import vp_chain as vch
        mdl = vch.Model(content=content, loops=3, M_s=1e13, y_s=y_s, M_phi=1e17)
        mdl.yt_cache = (math.log(2.5e13), 0.47)
        for loops in (2, 3):
            lan = mdl.landau(M_U, aU, loops=loops)
            lam, _ = landau(M_U, aU, 1e17, lan["Ylo"], lan["Yhi"], loops)
            res[f"samepoint_L{loops}_rk4_ratio"] = lan["ratio"]
            res[f"samepoint_L{loops}_dop853_alpha_ratio"] = lam / MPL
            res[f"samepoint_L{loops}_Ylo_Yhi"] = [lan["Ylo"], lan["Yhi"]]
        res["closed_form_2L_noYuk_noPhi_ratio"] = two_loop_closed_form(M_U, aU, b_lo[0], b_lo[1]) / MPL
        # perturbativity markers on the 3L trajectory (Yukawa on, yt = 0.5)
        Ylo = 14 * y_s**2 + 10 * 0.25 + 15.75 * 0.25
        Yhi = Ylo + 4.0
        for target in (0.5, 1.0):
            # find scale where (b3 a^2/16pi^2)/(b2 a/4pi) = b3 a/(4 pi b2) = target  -> a = 4 pi b2 target / b3 (above-M_phi coeffs)
            a_t = 4 * PI * b_hi[1] * target / b_hi[2]
            # scale where alpha reaches a_t on the 3L trajectory

            def ev2(t, y, a_t=a_t):
                return a_t - y[0]
            ev2.terminal = True
            tu, tphi = math.log(M_U), math.log(1e17)
            s = solve_ivp(rhs_factory(b_lo, Ylo, 3), (tu, tphi), [1 / aU], method="DOP853", rtol=1e-11, atol=1e-14, events=ev2)
            if s.t_events[0].size:
                sc = math.exp(s.t_events[0][0])
            else:
                s2 = solve_ivp(rhs_factory(b_hi, Yhi, 3), (tphi, math.log(1e20)), s.y[:, -1], method="DOP853", rtol=1e-11,
                               atol=1e-14, events=ev2)
                sc = math.exp(s2.t_events[0][0]) if s2.t_events[0].size else float("inf")
            res[f"scale_where_3L_over_2L={target}"] = sc
            res[f"alpha_inv_where_3L_over_2L={target}"] = 1 / a_t
        out[content] = {"M_U": M_U, "alpha_U_inv": aU, **res}
        print(content, json.dumps(out[content], indent=1))
    out["b_lo"], out["b_hi"] = b_lo, b_hi
    json.dump(out, open(os.path.join(HERE, "vp_alpha_space.json"), "w"), indent=1)
