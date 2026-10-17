"""One-loop unification estimate (EST/NUM, one loop only, no thresholds) for the v21 G3221 chain with K1's exact
one-loop b-coefficients, comparing the declared T2/T3 light content with K3's refined content
(bidoublet + (8,3,1)_0 + Delta_R(1,1,3)_2), i.e. T2 minus the complex (8,2,2)_0 and the real (1,3,1)_0.
Conventions as K1: GUT-normalised U(1)_Y and U(1)_{B-L}; matching alpha_1^-1 = (3/5) alpha_2R^-1 + (2/5) alpha_BL^-1.
Segments: SM [M_Z, M_s], SM + F17 S-sector [M_s, v_R] (b shift 28/3 universal), G3221 [v_R, M_U].
"""
import math, json
from fractions import Fraction as F

MZ = 91.1876
alpha_inv = 127.951; s2w = 0.23121; alpha_s = 0.1180   # PDG 2024 MS-bar values at M_Z
a1 = 0.6 * (1 - s2w) * alpha_inv; a2 = s2w * alpha_inv; a3 = 1 / alpha_s
b_SM = (F(41, 10), F(-19, 6), F(-7))
b_SMS = (F(403, 30), F(37, 6), F(7, 3))   # K1: SM + S-sector (3x(16+16bar) + 2x10 Weyl), shift 28/3
# G3221 (SU3, SU2L, SU2R, B-L) with the S-sector, K1 exact values
T2 = (F(47, 6), F(12), F(29, 3), F(89, 6))
T3 = (F(25, 3), F(37, 3), F(10), F(89, 6))
# refined: remove complex (8,2,2)_0 [dB3 = 4, dB2L = dB2R = 8/3] and real (1,3,1)_0 [dB2L = 1/3]
REF = (T2[0] - 4, T2[1] - F(8, 3) - F(1, 3), T2[2] - F(8, 3), T2[3])
# variants of the refined content, for orientation
REF_plus_131 = (REF[0], REF[1] + F(1, 3), REF[2], REF[3])          # bidoublet + (8,3,1) + (1,3,1)
BID_ONLY = (T2[0] - 4 - F(8, 3) + F(8, 3) - F(8, 3) + F(8, 3), 0, 0, 0)  # placeholder, not used


def solve(bG, Ms=1e13, label=""):
    bG = [float(x) for x in bG]
    b1eff = (3 * bG[2] + 2 * bG[3]) / 5
    bg = [b1eff, bG[1], bG[0]]  # order (1, 2L, 3)
    low = [a1, a2, a3]
    bsm = [float(x) for x in b_SM]; bsms = [float(x) for x in b_SMS]
    lnMs = math.log(Ms / MZ)
    # alpha_i^-1(v_R) = A_i - (bsms_i/2pi) tR', with tR' = ln(v_R/M_s), A_i = low_i - bsm_i lnMs/2pi
    A = [low[i] - bsm[i] * lnMs / (2 * math.pi) for i in range(3)]
    # unknowns tR', L, aU: A_i - bsms_i tR'/2pi - bg_i L/2pi - aU = 0
    import numpy as np
    M = np.array([[-bsms[i] / (2 * math.pi), -bg[i] / (2 * math.pi), -1.0] for i in range(3)])
    rhs = -np.array(A)
    tRp, L, aU = np.linalg.solve(M, rhs)
    vR = Ms * math.exp(tRp); MU = vR * math.exp(L)
    # couplings at v_R and the split alpha_2R, alpha_BL
    a_vR = [A[i] - bsms[i] * tRp / (2 * math.pi) for i in range(3)]
    a2R_vR = aU + bG[2] * L / (2 * math.pi); aBL_vR = aU + bG[3] * L / (2 * math.pi)
    out = {"label": label, "b_G3221": bG, "M_s": Ms, "v_R": vR, "M_U": MU, "alpha_U_inv": aU,
           "alpha_inv_at_vR(1,2L,3)": a_vR, "alpha_2R_inv(vR)": a2R_vR, "alpha_BL_inv(vR)": aBL_vR,
           "consistent(vR>Ms, MU>vR)": bool(vR > Ms and MU > vR)}
    print(json.dumps(out), flush=True)
    return out


res = {}
for Ms in (3e12, 1e13):
    for name, b in (("T2", T2), ("T3", T3), ("refined bidoublet+(8,3,1)+Delta_R", REF), ("refined+(1,3,1)", REF_plus_131)):
        res[f"{name}@Ms={Ms:.0e}"] = solve(b, Ms, name)
json.dump(res, open(__file__.replace(".py", ".json"), "w"), indent=1)
