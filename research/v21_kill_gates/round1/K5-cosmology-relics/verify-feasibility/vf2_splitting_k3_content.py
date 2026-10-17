"""Does the triplet-heavier ordering of the 10_F survive (a) K3's realizable light content (bidoublet + exactly one of
(8,3,1)_0 / (1,3,1)_0, Delta_R = (1,1,3)_2 only; T2/T3 are NOT realizable per K3) and (b) K2's b-coefficients
(9.33, 13.67, 8.33, 9.89), which differ from K5's for nominally the same T2 + F17 content?
Also: size of the H10-Yukawa contribution (light (1,2,2) of H10 at v_R vs its (3,1,1)/(3bar,1,1) at M_U) to the splitting.
"""
from fractions import Fraction as Fr
import json, numpy as np

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\vf2_splitting_k3_content.json"
T3 = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
T2 = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}
D3 = {1: 1, 3: 3, 6: 6, 8: 8}


def b_rep(d3, dL, dR, bl, kind):
    f = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    n = D3[d3] * dL * dR
    return [f * T3[d3] * dL * dR, f * T2[dL] * D3[d3] * dR, f * T2[dR] * D3[d3] * dL, f * Fr(3, 8) * Fr(bl) ** 2 * n]


def add(*rows):
    return [sum(r[i] for r in rows) for i in range(4)]


gauge = [Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)]
one16 = add(b_rep(3, 2, 1, Fr(1, 3), "weyl"), b_rep(3, 1, 2, Fr(-1, 3), "weyl"), b_rep(1, 2, 1, -1, "weyl"), b_rep(1, 1, 2, 1, "weyl"))
one10 = add(b_rep(1, 2, 2, 0, "weyl"), b_rep(3, 1, 1, Fr(-2, 3), "weyl"), b_rep(3, 1, 1, Fr(2, 3), "weyl"))
base = add(gauge, [3 * v for v in one16], *([one10] * 2 + [one16] * 6))
bid = b_rep(1, 2, 2, 0, "cplx")
oct831 = b_rep(8, 3, 1, 0, "real")
trip131 = b_rep(1, 3, 1, 0, "real")
oct822 = b_rep(8, 2, 2, 0, "cplx")
DRmin = b_rep(1, 1, 3, 2, "cplx")
contents = {
    "K3-A: bidoublet + (8,3,1)_0 + DR(1,1,3)_2": add(base, bid, oct831, DRmin),
    "K3-B: bidoublet + (1,3,1)_0 + DR(1,1,3)_2": add(base, bid, trip131, DRmin),
    "K3-min: bidoublet + DR(1,1,3)_2 only": add(base, bid, DRmin),
    "K5 T2 + DRmin (reference)": add(base, bid, oct822, oct831, trip131, DRmin),
    "SM-only below M_U (no light exotics, no S-sector: extreme)": add(gauge, [3 * v for v in one16], bid),
}
C_trip = np.array([4 / 3, 0, 0, 3 / 8 * (2 / 3) ** 2])
C_bid = np.array([0, 3 / 4, 3 / 4, 0])


def dln(bvals, M10=1e13, MU=2.5e16, aUinv=36.0):
    bb = np.array([float(v) for v in bvals])
    t = np.log(MU / M10)
    xs = np.linspace(0, t, 4001)
    ainv = aUinv + np.outer(xs, bb) / (2 * np.pi)
    g2 = 4 * np.pi / ainv
    return (6 / (16 * np.pi ** 2)) * np.trapezoid(g2 @ C_trip - g2 @ C_bid, xs), (1 / ainv[-1])


res = {}
for lab, b in contents.items():
    for (M10, MU, aUinv) in ((1e13, 2.5e16, 36.0), (3e12, 2.1e16, 30.0)):
        d, aM = dln(b, M10, MU, aUinv)
        res[f"{lab} | M10={M10:.0e} MU={MU:.1e}"] = dict(b=[str(v) for v in b], dln_trip_minus_bid=float(d), alpha_at_M10=aM.tolist())
        print(f"{lab:62s} b={[str(v) for v in b]} M10={M10:.0e}: ln(M_trip/M_bid)={d:+.2e}  alpha(M10)={np.round(aM,4)}")
# K2's b-coefficients
d, aM = dln([9.33, 13.67, 8.33, 9.89])
res["K2 b=(9.33,13.67,8.33,9.89)"] = dict(dln_trip_minus_bid=float(d), alpha_at_M10=aM.tolist())
print(f"K2's b (9.33, 13.67, 8.33, 9.89): ln(M_trip/M_bid) = {d:+.2e} alpha(M10) = {np.round(aM,4)}")
# H10-Yukawa piece: the bidoublet of 10_F couples to N through the LIGHT (1,2,2) of H10 (active M_U -> M_10), the triplet
# through the (3,1,1) of H10 at M_U (inactive below M_U).  One-loop: d ln m/d ln mu ⊃ + y_h^2/(32 pi^2) x (multiplicity) for
# the bidoublet only -> ln(M_trip/M_bid) ⊃ + y_h^2/(32 pi^2) x n x ln(M_U/M_10), n = number of (N, H) channels ~ 2 (two N1 flavours)
for yh in (0.1, 0.3, 0.5):
    piece = yh ** 2 / (32 * np.pi ** 2) * 2 * np.log(2.5e16 / 1e13)
    res[f"yukawa_piece_yh={yh}"] = float(piece)
    print(f"H10-Yukawa piece (bidoublet lighter), y_h={yh}: +{piece:.2e} (same sign as gauge running)")
# finite threshold constants cancel between the (3,1,1) and (6,2,2) bosons when all share one mass (Casimir sum rule):
# C_311(trip)=1, C_622(trip)=2, C_622(bid)=3 -> net = -(6/16pi^2) g^2 ln(M_311/M_622); mu-independent.
res["threshold_structure"] = "C_311(trip)=1, C_622(trip)=2, C_622(bid)=3; finite matching constants cancel; net = -(6 g_U^2/16pi^2) ln(M311/M622) = -0.0133 ln(M311/M622)"
json.dump(res, open(OUT, "w"), indent=1)
