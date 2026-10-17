"""K5 part (1c): which component of the stable 10_F is the lightest after SO(10) -> G3221 -> SM?

Tree level: T1.T2.S* gives one common Dirac mass M_10 = y_10 <S> to all ten components (10 x 10 contains no 210 or
126, so Phi210 and Delta cannot split the multiplet at the renormalizable level).  The splitting is radiative:
between M_U and M_10 the Yukawa y_10 of each G3221 component runs with its own gauge anomalous dimension,
   d ln y_c / d ln mu = -(3/16 pi^2) * 2 * sum_i g_i^2 C_i(c)   (common Yukawa/S-wavefunction pieces drop out)
colour triplet (3,1,1)_{-2/3}:  C_3 = 4/3, C_BL = (3/8)(2/3)^2 = 1/6  (GUT-normalised B-L)
bidoublet (1,2,2)_0:            C_L = C_R = 3/4
(at g_3 = g_L = g_R = g_BL both sums are 3/2: the SO(10)-symmetric limit is degenerate, as it must be.)
One-loop G3221 gauge running between M_10 ~ 1e13 and M_U ~ 2.5e16 with the T2 content (+ Delta_R + F17 S-sector):
   b = gauge + 3 families + T2 scalars + Delta_R + F17 (complete multiplets: common shift only).
Two Delta_R variants (minimal (1,1,3)_2; full (10bar,1,3)) and T3 are run to test the sign.
Also: decay rate of the heavier (coloured) components into the bidoublet via M_U leptoquark gauge bosons,
and the Planck-suppressed operator 10_F 10_F Phi210^2 S*/M_P^2 as a splitting uncertainty.
"""
from __future__ import annotations
import json
import numpy as np

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\k5_splitting.json"

# one-loop b_i = (b_3, b_L, b_R, b_BL) contributions
gauge = np.array([-11.0, -22 / 3, -22 / 3, 0.0])
families = np.array([4.0, 4.0, 4.0, 4.0])            # 3 x 16 (Weyl): 2/3 * T summed = 4 each (complete multiplets)
F17_S_sector = np.array([28 / 3] * 4)                 # 2 x 10 + 3 x (16+16bar) Weyl: 2/3*(1+1) + 2/3*6*2 = 28/3
# scalars: complex -> 1/3 T * mult ; real -> 1/6
def scalar(rep3, dL, dR, bl, real):
    f = 1 / 6 if real else 1 / 3
    T3 = {1: 0.0, 3: 0.5, 6: 2.5, 8: 3.0}[rep3]
    dim3 = {1: 1, 3: 3, 6: 6, 8: 8}[rep3]
    TL = {1: 0.0, 2: 0.5, 3: 2.0}[dL]
    TR = {1: 0.0, 2: 0.5, 3: 2.0}[dR]
    return f * np.array([T3 * dL * dR, TL * dim3 * dR, TR * dim3 * dL, (3 / 8) * bl ** 2 * dim3 * dL * dR])
T2 = scalar(1, 2, 2, 0, False) + scalar(8, 2, 2, 0, False) + scalar(8, 3, 1, 0, True) + scalar(1, 3, 1, 0, True)
T3 = T2 + scalar(1, 2, 2, 0, False) + scalar(8, 1, 1, 0, True)
DeltaR_min = scalar(1, 1, 3, 2, False)
DeltaR_full = DeltaR_min + scalar(3, 1, 3, 2 / 3, False) + scalar(6, 1, 3, 2 / 3, False)   # (10bar,1,3): 1_2 + 3bar_{2/3} + 6bar_{-2/3} (|B-L| used)

def splitting(b, M10, MU, alphaU_inv):
    """Return (M_triplet - M_bidoublet)/M at scale M10 from one-loop running."""
    t = np.log(MU / M10)
    # alpha_i^{-1}(mu) = alpha_U^{-1} + b_i/(2 pi) ln(MU/mu)
    xs = np.linspace(0, t, 2001)
    ainv = alphaU_inv + np.outer(xs, b) / (2 * np.pi)       # shape (n, 4)
    a = 1 / ainv
    g2 = 4 * np.pi * a
    C_trip = (4 / 3) * g2[:, 0] + (1 / 6) * g2[:, 3]
    C_bid = (3 / 4) * g2[:, 1] + (3 / 4) * g2[:, 2]
    # d ln y / d ln mu = -(6/16pi^2) sum g^2 C  -> ln y(M10) - ln y(MU) = +(6/16pi^2) int_0^t sum g^2 C dx
    dln = (6 / (16 * np.pi ** 2)) * np.trapezoid(C_trip - C_bid, xs)
    return dln, dict(alpha_inv_at_M10=dict(zip(["3", "L", "R", "BL"], (1 / a[-1]).round(3).tolist())))

results = {}
for label, b in (("T2+DeltaR_min", gauge + families + F17_S_sector + T2 + DeltaR_min),
                 ("T2+DeltaR_full", gauge + families + F17_S_sector + T2 + DeltaR_full),
                 ("T3+DeltaR_min", gauge + families + F17_S_sector + T3 + DeltaR_min),
                 ("T3+DeltaR_full", gauge + families + F17_S_sector + T3 + DeltaR_full)):
    rows = []
    for M10, MU, aUinv in ((1e13, 2.5e16, 36.0), (3e12, 2.5e16, 36.0), (1e13, 2.1e16, 30.0), (1e13, 3.1e16, 42.0)):
        dln, info = splitting(b, M10, MU, aUinv)
        rows.append(dict(M10=M10, MU=MU, alphaU_inv=aUinv, dM_over_M_triplet_minus_bidoublet=dln, dM_GeV=dln * M10, **info))
    results[label] = dict(b=b.round(4).tolist(), rows=rows)
    print(label, "b =", b.round(3), [f"dM/M={r['dM_over_M_triplet_minus_bidoublet']:+.2e}" for r in rows])

# decay of the coloured components into the bidoublet through an M_U leptoquark gauge boson (muon-decay-like)
def tau_triplet(dM, MU, alphaU=1 / 36, N_channels=6):
    GX = 4 * np.pi * alphaU / MU ** 2
    Gamma = N_channels * GX ** 2 * dM ** 5 / (192 * np.pi ** 3)
    return 6.582e-25 / Gamma
decays = []
for M10 in (1e13, 3e12):
    dln = results["T2+DeltaR_min"]["rows"][0 if M10 == 1e13 else 1]["dM_over_M_triplet_minus_bidoublet"]
    dM = dln * M10
    decays.append(dict(M10=M10, dM=dM, tau_s_MU2p5e16=tau_triplet(dM, 2.5e16), tau_s_MU3p1e16=tau_triplet(dM, 3.1e16)))
results["coloured_component_decay"] = decays
# Planck operator 10_F 10_F Phi210^2 S*/M_P^2 : dM ~ c v_S M_U^2/M_P^2
planck = {f"MU={MU:.1e}": 4e13 * MU ** 2 / 2.435e18 ** 2 for MU in (2.1e16, 2.5e16, 3.1e16)}
results["planck_operator_dM_per_unit_c_GeV"] = planck
results["EW_splitting_in_bidoublet"] = "charged members heavier by ~alpha_2 m_Z/2 ~ 0.3 GeV (Higgsino-like, EST); neutral member lightest"
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1)
print(json.dumps(decays), planck)
