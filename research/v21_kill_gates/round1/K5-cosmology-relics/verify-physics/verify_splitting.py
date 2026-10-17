"""Independent check of the 10_F component ordering (which R-odd state is lightest).

1. Exact (Fraction) one-loop b_i for G3221 with the T2 content + minimal Delta_R + F17 S-sector + 3 families.
2. One-loop running M_U -> M_10 (own RK4 in t = ln mu), Yukawa anomalous dimension
      d ln y_c / d ln mu = -(3/16 pi^2) sum_i g_i^2 [C_i(psi1_c) + C_i(psi2_c)]
   with the component Casimirs (T(fund) = 1/2, B-L GUT-normalised sqrt(3/8)(B-L)).
3. The M_U gauge-threshold term the researcher omitted: between M_U and the individual coset gauge-boson masses the
   components run with different coset Casimirs:  SU(4)/SU(3)xU(1) coset (3,1,1)+(3bar,1,1): C = 1 on the triplet,
   0 on the bidoublet;  (6,2,2) coset: C = 2 on the triplet, 3 on the bidoublet (C_2^{SO(10)}(10) = 9/2 total,
   subgroup part 3/2 for both).  So  d(ln M_trip/M_bid) = (6/16 pi^2) g_U^2 ln(M_{(6,2,2)}/M_{(3,1,1)}).
   Reports the ratio M_{(3,1,1)}/M_{(6,2,2)} at which the running effect is cancelled.
"""
from __future__ import annotations
import json, sys
from fractions import Fraction as Fr
import numpy as np

# Dynkin indices: SU(N) fund 1/2, adjoint N; SU(2) triplet 2; SU(3) octet 3, sextet 5/2
T3 = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
T2 = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}
D3 = {1: 1, 3: 3, 6: 6, 8: 8}


def contrib(kind, c, dL, dR, bl):
    """b_i contribution of one multiplet (c = SU(3) dim, dL, dR = SU(2) dims, bl = B-L).  kind: 'weyl', 'cplx', 'real'."""
    f = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    mult = D3[c] * dL * dR
    return np.array([f * T3[c] * dL * dR, f * T2[dL] * D3[c] * dR, f * T2[dR] * D3[c] * dL, f * Fr(3, 8) * bl * bl * mult], dtype=object)


gauge = np.array([Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)], dtype=object)
fam = 3 * (contrib("weyl", 3, 2, 1, Fr(1, 3)) + contrib("weyl", 3, 1, 2, Fr(-1, 3)) + contrib("weyl", 1, 2, 1, Fr(-1)) + contrib("weyl", 1, 1, 2, Fr(1)))
ten = contrib("weyl", 1, 2, 2, Fr(0)) + contrib("weyl", 3, 1, 1, Fr(-2, 3)) + contrib("weyl", 3, 1, 1, Fr(2, 3))
sixteen = contrib("weyl", 3, 2, 1, Fr(1, 3)) + contrib("weyl", 3, 1, 2, Fr(-1, 3)) + contrib("weyl", 1, 2, 1, Fr(-1)) + contrib("weyl", 1, 1, 2, Fr(1))
f17 = 2 * ten + 6 * sixteen
T2s = contrib("cplx", 1, 2, 2, 0) + contrib("cplx", 8, 2, 2, 0) + contrib("real", 8, 3, 1, 0) + contrib("real", 1, 3, 1, 0)
DRmin = contrib("cplx", 1, 1, 3, Fr(2))
DRfull = DRmin + contrib("cplx", 3, 1, 3, Fr(2, 3)) + contrib("cplx", 6, 1, 3, Fr(-2, 3))
b_min = gauge + fam + f17 + T2s + DRmin
b_full = gauge + fam + f17 + T2s + DRfull
print("b (T2 + DeltaR min):", [str(x) for x in b_min], [float(x) for x in b_min])
print("b (T2 + DeltaR full):", [str(x) for x in b_full], [float(x) for x in b_full])
print("families:", [str(x) for x in fam], " F17:", [str(x) for x in f17], " T2:", [str(x) for x in T2s], " DRmin:", [str(x) for x in DRmin])

# component Casimirs (sum over the two Weyl fermions of the Dirac pair)
C_trip = np.array([2 * Fr(4, 3), 0, 0, 2 * Fr(3, 8) * Fr(4, 9)], dtype=float)   # (3,1,1)_{-2/3} + (3bar,1,1)_{+2/3}
C_bid = np.array([0, 2 * Fr(3, 4), 2 * Fr(3, 4), 0], dtype=float)                  # (1,2,2)_0 x 2
print("sum C triplet:", C_trip.sum(), " bidoublet:", C_bid.sum(), "(equal at the SO(10) point: OK)")


def run(b, M10, MU, aUinv, nsteps=4000):
    b = np.array([float(x) for x in b])
    t = np.log(MU / M10)
    h = t / nsteps
    # alpha_i^{-1}(mu) = aUinv + b_i/(2pi) * ln(MU/mu); integrate dln(y_trip/y_bid) going down
    def integrand(x):   # x = ln(MU/mu)
        ainv = aUinv + b * x / (2 * np.pi)
        g2 = 4 * np.pi / ainv
        return (3 / (16 * np.pi ** 2)) * (g2 @ (C_trip - C_bid))
    xs = np.linspace(0, t, nsteps + 1)
    vals = np.array([integrand(x) for x in xs])
    dln = np.trapz(vals, xs)   # ln(y_trip/y_bid) at M10, positive = triplet heavier
    ainv_end = aUinv + b * t / (2 * np.pi)
    return dln, ainv_end


rows = []
for label, b in (("T2+DRmin", b_min), ("T2+DRfull", b_full)):
    for (M10, MU, aUinv) in ((1e13, 2.5e16, 36.0), (3e12, 2.5e16, 36.0), (1e13, 2.1e16, 30.0), (1e13, 3.1e16, 42.0)):
        dln, ainv = run(b, M10, MU, aUinv)
        gU2 = 4 * np.pi / aUinv
        # threshold term: dln_th = (6/16pi^2) gU^2 ln(M622/M311); cancellation when ln(M311/M622) = dln / ((6/16pi^2) gU^2)
        coef = (6 / (16 * np.pi ** 2)) * gU2
        crit = np.exp(dln / coef)
        rows.append(dict(content=label, M10=M10, MU=MU, aUinv=aUinv, dlnM_trip_minus_bid_running=dln, alpha_inv_at_M10=ainv.round(3).tolist(),
                         threshold_coeff_per_unit_log=coef, critical_ratio_M311_over_M622=crit))
        print(f"{label} M10={M10:.0e} MU={MU:.1e} aU^-1={aUinv}: dln(running)={dln:+.3e}; threshold coef={coef:.4f}/unit ln; ordering flips if M(3,1,1)/M(6,2,2) > {crit:.2f}")
with open(sys.argv[1] if len(sys.argv) > 1 else "verify_splitting.json", "w", encoding="utf-8") as fh:
    json.dump(dict(b_min=[str(x) for x in b_min], b_full=[str(x) for x in b_full], rows=rows), fh, indent=1, default=float)
