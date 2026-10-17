"""Verifier structural checks for K2.
(1) X-charge enumeration of every renormalisable fermion bilinear x scalar coupling in v21-F17 (EXACT arithmetic),
    with the SO(10) selection rules 16x16 -> 10,120,126bar ; 16x16bar -> 1,45,210 ; 16x10_F needs 16bar_H (none);
    10_F x 10_F -> 1,45,54 ; 16x1 needs 16bar_H (none); 1x1 -> 1.
(2) Single-light-bidoublet (T2) consequence: M_u = (kappa_u/kappa_d) M_d exactly below M_U up to O(v_R^2/M_U^2)
    heavy-bidoublet admixture; the pulls this implies at M_Z (CKM = 1, m_u/m_d = m_c/m_s = m_t/m_b).
(3) dof recount for the researcher's Proxy2 parametrisation.
"""
import json, math, itertools, numpy as np

# ---------------- (1) X-charge enumeration ----------------
scalars = {"Phi210": (210, 0), "Delta126bar": (126, -2), "H10": (10, -2), "S": (1, 4), "Phi17": (1, 17)}
# add conjugates (10 is real: H10* is still a 10; 126bar* = 126; 210 real; singlets conj)
sc = {}
for k, (rep, X) in scalars.items():
    sc[k] = (rep, X)
    sc[k + "*"] = ({126: -126, 10: 10, 210: 210, 1: 1}[rep], -X)   # -126 denotes the 126 (conjugate of 126bar)
fermions = {"F": (16, 1), "16a": (16, 0), "16bar_a": (-16, 4), "16b": (16, -3), "16bar_b": (-16, 7), "16c": (16, -6), "16bar_c": (-16, 10),
            "16d": (16, -9), "16bar_d": (-16, -8), "10F_a": (10, -1), "10F_b": (10, 5), "1_a": (1, -3), "1_b": (1, -1), "1_a2": (1, -3), "1_b2": (1, -1)}
def so10_allowed(r1, r2, rs):
    pair = tuple(sorted((r1, r2)))
    if pair == (16, 16):
        return rs in (10, 120, -126)       # 16x16 = 10 + 120 + 126 -> couples to 10, 120, 126bar ; -126 here means the 126 scalar... careful below
    if pair == (-16, -16):
        return rs in (10, 120, 126)        # 16bar x 16bar = 10 + 120 + 126bar -> couples to 10, 120, 126
    if pair == (-16, 16):
        return rs in (1, 45, 210)
    if pair == (10, 10):
        return rs in (1, 45, 54)
    if pair == (10, 16) or pair == (-16, 10):
        return rs in (16, -16)             # needs a 16/16bar scalar
    if pair == (1, 16) or pair == (-16, 1):
        return rs in (16, -16)
    if pair == (1, 10):
        return rs == 10
    if pair == (1, 1):
        return rs == 1
    raise ValueError(pair)
# representation labels: scalars: 126 means '126bar' field (as declared), -126 its conjugate (a 126).  Fix the 16x16 rule:
# 16 x 16 contains the 126 (not 126bar), so the scalar must be a 126bar  -> label 126 ; 16bar x 16bar needs a 126 -> label -126.
def so10_allowed_fixed(r1, r2, rs):
    pair = tuple(sorted((r1, r2)))
    if pair == (16, 16):
        return rs in (10, 120, 126)
    if pair == (-16, -16):
        return rs in (10, 120, -126)
    return so10_allowed(r1, r2, rs)
allowed = []
names = list(fermions)
for i, j in itertools.combinations_with_replacement(range(len(names)), 2):
    f1, f2 = names[i], names[j]
    (r1, X1), (r2, X2) = fermions[f1], fermions[f2]
    for s, (rs, Xs) in sc.items():
        if X1 + X2 + Xs == 0 and so10_allowed_fixed(r1, r2, rs):
            allowed.append((f1, f2, s))
print("X- and SO(10)-allowed renormalisable fermion couplings:")
for a in allowed:
    print("  ", a)
light_mix = [a for a in allowed if ("F" in a[:2]) and not (a[0] == "F" and a[1] == "F")]
print("couplings that mix the light F with F17 states:", light_mix)

# ---------------- (2) single-bidoublet consequence ----------------
inp = json.load(open("inputs_mz.json"))
m = {k: v[0] for k, v in inp["masses_GeV_MZ"].items()}
ck = inp["ckm_MZ"]
# If M_u = c M_d (c complex scalar) then V_CKM = 1 and m_u/m_d = m_c/m_s = m_t/m_b = |c|.
pull_s12 = (0 - ck["s12"][0]) / ck["s12"][1]; pull_s23 = (0 - ck["s23"][0]) / ck["s23"][1]; pull_s13 = (0 - ck["s13"][0]) / ck["s13"][1]
print(f"T2 (M_u = c M_d): CKM = 1 => pulls s12 {pull_s12:.0f} sigma, s23 {pull_s23:.0f} sigma, s13 {pull_s13:.0f} sigma")
print(f"   mass ratios at M_Z: m_u/m_d = {m['m_u']/m['m_d']:.3f}, m_c/m_s = {m['m_c']/m['m_s']:.2f}, m_t/m_b = {m['m_t']/m['m_b']:.1f} (must be equal under T2)")
vR, MU = 2.6e13, 2.13e16
print(f"   heavy-bidoublet admixture bound (v_R/M_U)^2 = {(vR/MU)**2:.2e}; needed up/down misalignment O(theta_C) = 0.22")
print("   corrected composition at the researcher's best point: s = v_u126 v_d10/(v_u10 v_d126) = 0.481 e^{0.114 i} (needs |1-s| = O(1))")

# ---------------- (3) dof recount ----------------
print("dof: Proxy2 free params 17 (F 12, r 2, s 2, cd126 1) + 3 up masses fixed to data (Du) - 1 redundant phase of r = 19 physical;"
      " observables 18 -> dof = -1 (type I), -3 (type I+II); researcher states 1 / -1")
