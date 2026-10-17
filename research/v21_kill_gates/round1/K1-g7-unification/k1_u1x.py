#!/usr/bin/env python3
"""U(1)_X one-loop perturbativity bound (exact coefficients from k1_model.u1x_coeffs) and its maximal feedback."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k1_model import u1x_coeffs
M_PL = 2.435e18
out = {}
for tag, with_phi in (("below_Mphi(no Phi pair)", False), ("full_content", True)):
    bx, b10x, bx10 = u1x_coeffs(with_phi)
    out[tag] = {"b_X": str(bx), "b_X_float": float(bx), "b_10X": str(b10x), "b_X10": str(bx10)}
bx = float(u1x_coeffs(True)[0])
for mu0 in (1e17, 2e16):
    L = math.log(M_PL / mu0)
    ax_inv_min = 1.0 + bx / (2 * math.pi) * L   # alpha_X^-1(mu0) needed for alpha_X(M_Pl,red) <= 1
    gx_max = math.sqrt(4 * math.pi / ax_inv_min)
    out[f"bound_from_{mu0:.0e}"] = {"ln(MPl/mu0)": L, "alpha_X_inv_min_at_mu0": ax_inv_min, "g_X_max_at_mu0": gx_max,
                                   "alpha_X_max_at_mu0": 1 / ax_inv_min}
# if g_X were SO(10)-like (alpha_X^-1 = 26 at 1e17): one-loop pole position
ax = 26.0
out["pole_if_alphaX_inv_26_at_1e17"] = 1e17 * math.exp(ax * 2 * math.pi / bx)
# maximal two-loop feedback on d alpha_10^-1/dt at mu = 1e17 .. M_Pl with alpha_X at the bound (relative to the one-loop SO(10) term b1/(2pi) with b1 = 8)
b10x = float(u1x_coeffs(True)[1])
feed = b10x * (1 / 2178.0) / (8 * math.pi**2)
out["max_feedback_dalpha10inv_dt_vs_oneloop"] = {"feedback_term": feed, "one_loop_term_b1=8": 8 / (2 * math.pi), "ratio": feed / (8 / (2 * math.pi))}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "k1_u1x.json"), "w"), indent=1)
