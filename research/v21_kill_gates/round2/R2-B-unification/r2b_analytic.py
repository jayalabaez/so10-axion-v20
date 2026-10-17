#!/usr/bin/env python3
"""One-loop analytic structure (EXACT arithmetic on exact b's; physics inputs alpha_i(M_Z)):
   2 pi [alpha_1^-1 - alpha_2^-1](M_Z) = (b1-b2)_SM L1 + A L2,   A = 3/5 b_2R + 2/5 b_BL - b_2L
   2 pi [alpha_2^-1 - alpha_3^-1](M_Z) = (b2-b3)_SM L1 + B L2,   B = b_2L - b_3
with L1 = ln(v_R/M_Z), L2 = ln(M_U/v_R) (tree matching, all thresholds at the matching scales).  Per-multiplet
(Delta A, Delta B) for every G3221 multiplet of 210 + 126bar + 10, and the B63 axion band."""
import json
import math
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M
from r2b_lib import mv_coefficients, threshold_b

A1, A2, A3 = M.A1_MZ, M.A2_MZ, M.A3_MZ
b_sm = mv_coefficients(M.SM_C2, M.sm_fields(False))[0]
d12, d23 = b_sm[0] - b_sm[1], b_sm[1] - b_sm[2]
R1, R2 = 2 * math.pi * (A1 - A2), 2 * math.pi * (A2 - A3)


def AB(b):
    b3, b2l, b2r, bbl = b
    return F(3, 5) * b2r + F(2, 5) * bbl - b2l, b2l - b3


def solve1L(b):
    A, B = AB(b)
    det = d12 * B - d23 * A
    L2 = (d12 * R2 - d23 * R1) / float(det)
    L1 = (R1 - float(A) * L2) / float(d12)
    vR = M.MZ * math.exp(L1)
    MU = vR * math.exp(L2)
    aU = A2 - (float(b_sm[1]) * L1 + float(b[1]) * L2) / (2 * math.pi)
    return vR, MU, aU


out = {"(b1-b2)_SM": str(d12), "(b2-b3)_SM": str(d23), "contents": {}, "per_multiplet": {}}
for c in ("C0", "C1", "C2", "C1p", "T2", "T3", "bid_DR"):
    b = mv_coefficients(M.G3221_C2, M.g3221_fields(M.CONTENTS[c], False))[0]
    A, B = AB(b)
    vR, MU, aU = solve1L(b)
    out["contents"][c] = {"b_noS": [str(x) for x in b], "A": str(A), "B": str(B), "vR_1L": vR, "MU_1L": MU,
                          "aU_1L": aU}
    print(f"{c:6s} A = {str(A):7s} ({float(A):6.3f})  B = {str(B):6s} ({float(B):6.3f})  1L: v_R = {vR:.3g}  M_U = {MU:.3g}  aU^-1 = {aU:.2f}")
for n, (kind, c3, l, r, q) in M.SCALAR_TABLE.items():
    reps = M.g3221(c3, l, r, q)
    db = [threshold_b(kind, reps, i, 1) for i in range(4)]
    dA, dB = AB(db)
    out["per_multiplet"][n] = {"db": [str(x) for x in db], "dA": str(dA), "dB": str(dB)}
    print(f"   {n:28s} dA = {str(dA):7s} dB = {str(dB):6s}")

# B63 axion band: f_a = sqrt2 <S>/17, m_a = 5.70 ueV (1e12 GeV/f_a)  [K1/K0b conventions; Gorghetto-Villadoro LIT-abstract]
band = {}
for Ms in (3e12, 5e12, 7e12, 8.2e12, 1e13, 1.21e13):
    lo = Ms / 3.29e13
    hi = 0.346 if Ms <= 3e12 else (0.368 if Ms >= 1e13 else 0.346 + (0.368 - 0.346) * math.log(Ms / 3e12) / math.log(1e13 / 3e12))
    S_hi, S_lo = Ms / lo, Ms / hi
    ma = lambda S: 5.70 * 1e12 / (math.sqrt(2) * S / 17)
    band[f"{Ms:.3g}"] = {"y_s": [lo, hi], "<S>": [S_lo, S_hi], "m_a_ueV": [ma(S_hi), ma(S_lo)]}
    print(f"M_s = {Ms:.3g}: y_s in [{lo:.3f}, {hi:.3f}], <S> in [{S_lo:.3g}, {S_hi:.3g}], m_a in [{ma(S_hi):.2f}, {ma(S_lo):.2f}] ueV")
out["axion_band"] = band
with open(os.path.join(HERE, "r2b_analytic.json"), "w") as fh:
    json.dump(out, fh, indent=1)
