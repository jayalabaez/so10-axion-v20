"""Second-pass check of the 10_F triplet/bidoublet ordering at K3's ACTUAL orientations.

K3 (REPORT.txt, method): Phi = p P + a A with P, A unit-chart-norm four-forms, A20/A45/A70 = (p,a) = (cos th, sin th).
So p/a = cot(th) in the SAME unit-vector normalisation as verify_gauge_masses_210.py (a_dir = (e0123+e0145+e2345)/sqrt3).
Gauge-boson masses from that script (verified analytically below):  M^2(3,1,1) = (4/3) a^2,  M^2(6,2,2) = p^2 + (2/3) a^2.

Net one-loop leading-log ordering  dln(M_trip/M_bid) = running(G3221, M_U -> M_10)  -  (6/16pi^2) g_U^2 ln(M311/M622).
Independent recomputation of the running with coupled RGEs integrated numerically (RK4 on alpha_i^-1 and ln y_c),
plus an estimate of the finite one-loop pole-mass pieces at M_10 and the size of unknown finite M_U matching terms.
"""
from __future__ import annotations
import json
import numpy as np
from fractions import Fraction as Fr

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-physics\v2_splitting_orientations.json"

# ---- exact one-loop b_i (SU3, SU2L, SU2R, U1_BL GUT-normalised) ----
T3 = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
T2 = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}
D3 = {1: 1, 3: 3, 6: 6, 8: 8}


def mult(kind, c, dL, dR, bl):
    f = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    n = D3[c] * dL * dR
    return np.array([f * T3[c] * dL * dR, f * T2[dL] * D3[c] * dR, f * T2[dR] * D3[c] * dL, f * Fr(3, 8) * bl * bl * n], dtype=object)


sixteen = mult("weyl", 3, 2, 1, Fr(1, 3)) + mult("weyl", 3, 1, 2, Fr(-1, 3)) + mult("weyl", 1, 2, 1, Fr(-1)) + mult("weyl", 1, 1, 2, Fr(1))
ten = mult("weyl", 1, 2, 2, 0) + mult("weyl", 3, 1, 1, Fr(-2, 3)) + mult("weyl", 3, 1, 1, Fr(2, 3))
gauge = np.array([Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)], dtype=object)
T2s = mult("cplx", 1, 2, 2, 0) + mult("cplx", 8, 2, 2, 0) + mult("real", 8, 3, 1, 0) + mult("real", 1, 3, 1, 0)
DR = mult("cplx", 1, 1, 3, Fr(2))
b = gauge + 3 * sixteen + 2 * ten + 6 * sixteen + T2s + DR
bf = np.array([float(x) for x in b])
print("b_i (T2 + DeltaR(1,1,3) + F17 + 3 fam):", [str(x) for x in b])

# component Casimir sums (two Weyl fermions of the Dirac pair)
C_trip = np.array([2 * 4 / 3, 0.0, 0.0, 2 * (3 / 8) * (4 / 9)])
C_bid = np.array([0.0, 2 * 3 / 4, 2 * 3 / 4, 0.0])
assert abs(C_trip.sum() - C_bid.sum()) < 1e-12


def running_split(M10, MU, aUinv, nsteps=20000):
    """RK4 integration downward in t = ln(mu/MU) (t<0) of alpha_i^-1 and of L = ln(y_trip/y_bid)."""
    t_end = np.log(M10 / MU)
    h = t_end / nsteps
    ainv = np.full(4, aUinv, dtype=float)
    L = 0.0

    def f(ainv_):
        g2 = 4 * np.pi / ainv_
        dainv = -bf / (2 * np.pi)                       # d alpha^-1 / d ln mu
        dL = -(3 / (16 * np.pi ** 2)) * (g2 @ (C_trip - C_bid))   # d ln(y_t/y_b)/d ln mu
        return dainv, dL
    for _ in range(nsteps):
        k1a, k1L = f(ainv)
        k2a, k2L = f(ainv + 0.5 * h * k1a)
        k3a, k3L = f(ainv + 0.5 * h * k2a)
        k4a, k4L = f(ainv + h * k3a)
        ainv = ainv + h / 6 * (k1a + 2 * k2a + 2 * k3a + k4a)
        L = L + h / 6 * (k1L + 2 * k2L + 2 * k3L + k4L)
    return L, ainv


def ratio_311_622(p_over_a):
    r = p_over_a
    return np.sqrt((4 / 3) / (r * r + 2 / 3))


rows = []
orientations = {"A20": np.cos(np.radians(20)) / np.sin(np.radians(20)), "A45": 1.0, "A70": np.cos(np.radians(70)) / np.sin(np.radians(70)),
                "pure a (p=0)": 0.0, "p/a=0.2": 0.2, "p/a=0.3": 0.3}
for (M10, MU, aUinv) in ((1e13, 2.5e16, 36.0), (1e13, 2.1e16, 30.0), (1e13, 3.1e16, 42.0), (3e12, 2.5e16, 36.0)):
    L, ainv = running_split(M10, MU, aUinv)
    gU2 = 4 * np.pi / aUinv
    coef = 6 / (16 * np.pi ** 2) * gU2
    alpha_IR = 1 / ainv
    # finite one-loop pole-mass pieces at M_10 (MSbar->pole, C_F alpha/pi per gauge factor; same sign for both)
    fin_trip = (4 / 3) * alpha_IR[0] / np.pi + (1 / 6) * alpha_IR[3] / np.pi
    fin_bid = (3 / 4) * (alpha_IR[1] + alpha_IR[2]) / np.pi
    for name, r in orientations.items():
        ratio = ratio_311_622(r)
        thr = -coef * np.log(ratio)
        net = L + thr
        rows.append(dict(M10=M10, MU=MU, aUinv=aUinv, orientation=name, p_over_a=r, M311_over_M622=ratio,
                         running=L, MU_threshold_log=thr, net_leading_log=net,
                         finite_pole_mass_estimate=fin_trip - fin_bid, unknown_finite_matching_per_unitC=gU2 / (16 * np.pi ** 2),
                         alpha_inv_IR=ainv.round(2).tolist()))
    print(f"M10={M10:.0e} MU={MU:.1e} aU^-1={aUinv}: running=+{L:.3e}; alpha^-1(M10)={ainv.round(2)}; finite pole-mass diff ~{fin_trip-fin_bid:+.2e}; unknown finite matching ~{gU2/(16*np.pi**2):.2e}/unit C")
    for rr in rows[-len(orientations):]:
        print(f"    {rr['orientation']:12s} p/a={rr['p_over_a']:.3f} M311/M622={rr['M311_over_M622']:.3f} thr={rr['MU_threshold_log']:+.2e} net={rr['net_leading_log']:+.2e}")

# analytic check of the gauge-boson mass formula against the previous verifier's numbers
chk = {r: ratio_311_622(r) for r in (0.0, 0.25, 0.5, 0.75, 1.0)}
print("ratio formula check vs verify_gauge_masses_210 (1.414, 1.352, 1.206, 1.042, 0.894):", {k: round(v, 3) for k, v in chk.items()})
json.dump(dict(b=[str(x) for x in b], rows=rows, ratio_check=chk), open(OUT, "w", encoding="utf-8"), indent=1, default=float)
