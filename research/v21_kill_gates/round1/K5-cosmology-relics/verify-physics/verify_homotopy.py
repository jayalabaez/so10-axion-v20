"""Exact bookkeeping for the G3221 -> SM step (monopoles) and the R-parity / Yukawa census, independent of the researcher.

(1) pi_2(G3221/H) = ker(pi_1(H) -> pi_1(G3221)).  The U(1)_Y generator loop: exp(i phi Y), Y = T3R + (B-L)/2.
    It closes (acts trivially on all fields present) at phi = 2 pi m_Y.  Its U(1)_{B-L} projection exp(i (phi/2)(B-L))
    closes at (phi/2) = 2 pi m_BL.  Degree = m_Y/(2 m_BL).  Also check that the SU(2)_R part exp(i phi T3R) is a
    closed loop in SU(2)_R at phi = 2 pi m_Y (needs m_Y T3R integer) and is contractible (SU(2) simply connected).
(2) R = z^2 (-1)^F with z^2 = -1 on spinors: list R-odd fields and check every X-allowed Yukawa is R-even.
(3) Full census of X-allowed renormalizable Yukawas by brute force over SO(10) product rules.
"""
from fractions import Fraction as Fr
from itertools import combinations_with_replacement
from math import lcm

fields = {  # (SU2R dim, B-L) for every G3221 multiplet carrying T3R/B-L in the model (fermions and scalars)
    "Q(3,2,1)": (1, Fr(1, 3)), "Qc(3b,1,2)": (2, Fr(-1, 3)), "L(1,2,1)": (1, Fr(-1)), "Lc(1,1,2)": (2, Fr(1)),
    "10:(1,2,2)": (2, Fr(0)), "10:(3,1,1)": (1, Fr(-2, 3)), "10:(3b,1,1)": (1, Fr(2, 3)),
    "126b:(1,1,3)": (3, Fr(2)), "126b:(3b,1,3)": (3, Fr(2, 3)), "126b:(6b,1,3)": (3, Fr(-2, 3)), "126b:(15,2,2)": (2, Fr(0)),
    "126b:(10,3,1)": (1, Fr(-2)), "210:(6,2,2)": (2, Fr(-2, 3)), "210:(15,1,3)": (3, Fr(0)), "45:(6,2,2)": (2, Fr(2, 3)),
}
Ys, BLs, T3Rs = set(), set(), set()
for name, (dR, bl) in fields.items():
    for i in range(dR):
        t3 = Fr(dR - 1, 2) - i
        Ys.add(t3 + bl / 2); T3Rs.add(t3)
    BLs.add(bl)
m_Y = lcm(*[y.denominator for y in Ys if y != 0])
m_BL = lcm(*[b.denominator for b in BLs if b != 0])
m_T3R = lcm(*[t.denominator for t in T3Rs if t != 0])
print("Y values:", sorted(Ys), "-> minimal U(1)_Y loop closes at phi = 2 pi x", m_Y)
print("B-L values:", sorted(BLs), "-> minimal U(1)_{B-L} loop closes at psi = 2 pi x", m_BL)
print("T3R values:", sorted(T3Rs), "-> exp(i phi T3R) closes at phi = 2 pi x", m_T3R, "(divides m_Y:", m_Y % m_T3R == 0, ")")
deg = Fr(m_Y, 2 * m_BL)
print("degree of the Y-loop on the B-L circle:", deg, "-> pi_2(G3221/SM) = ker(Z -> Z) =", "0 (no monopoles)" if deg != 0 else "Z")
# z^2 = (-1)^{3(B-L)} : check +1 on all scalar components present (vevs), -1 on 16's
for name, (dR, bl) in fields.items():
    print(f"  z^2 on {name}: {(-1) ** int(3 * bl)}")

# ---- Yukawa census ----
CONJ = {"1": "1", "10": "10", "16": "16bar", "16bar": "16", "126": "126bar", "126bar": "126", "210": "210", "45": "45", "54": "54", "120": "120", "144": "144bar", "144bar": "144"}
PROD = {("1", "1"): ["1"], ("1", "10"): ["10"], ("1", "16"): ["16"], ("1", "16bar"): ["16bar"], ("10", "10"): ["1", "45", "54"],
        ("10", "16"): ["16bar", "144bar"], ("10", "16bar"): ["16", "144"], ("16", "16"): ["10", "120", "126"],
        ("16bar", "16bar"): ["10", "120", "126bar"], ("16", "16bar"): ["1", "45", "210"]}
def prod(a, b):
    return PROD[(a, b)] if (a, b) in PROD else PROD[(b, a)]
F = {"F": ("16", 1), "T1": ("10", -1), "T2": ("10", 5), "A": ("16", 0), "Ab": ("16bar", 4), "B": ("16", -3), "Bb": ("16bar", 7),
     "C": ("16", -6), "Cb": ("16bar", 10), "N3": ("1", -3), "N1": ("1", -1), "P": ("16", -9), "Pb": ("16bar", -8)}
S = {"Phi210": ("210", 0, True), "Delta": ("126bar", -2, False), "H": ("10", -2, False), "S": ("1", 4, False), "Phi17": ("1", 17, False)}
forms = []
for n, (r, x, real) in S.items():
    forms.append((n, r, x))
    if not real:
        forms.append((n + "*", CONJ[r], -x))
found = []
for (f1, f2) in combinations_with_replacement(F, 2):
    r1, x1 = F[f1]; r2, x2 = F[f2]
    for (sn, sr, sx) in forms:
        if x1 + x2 + sx == 0 and CONJ[sr] in prod(r1, r2):
            found.append(f"{f1}.{f2}.{sn}")
Rpar = {f: (-1 if F[f][0] in ("1", "10") else +1) for f in F}
print("X-allowed renormalizable Yukawa structures (", len(found), "):", found)
print("R-odd fermions:", [f for f in F if Rpar[f] == -1])
print("all Yukawas R-even:", all(Rpar[s.split(".")[0]] * Rpar[s.split(".")[1]] == 1 for s in found))
# QCD anomaly of the S-rotation (S charge 1): solve PQ charges by hand (see report); N = 3*(1/4)*2 + 1*1 + 3*(1*2) = 17/2
N = Fr(3, 4) * 2 + 1 + 3 * 2
print("N (S charge 1) =", N, "; 2N =", 2 * N, "= 17 -> theta_QCD shift per unit S-phase = 17 = vartheta shift -> N_DW = 1")
