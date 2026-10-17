"""R2-V continuation: SO(10) small-instanton contributions to the axion potential (skeptic item 4c), EST.

EXACT structure: in a minimal SO(10) instanton a Weyl fermion in R has 2T(R) zero modes (T(10) = 1, T(16) = 2).  The 't Hooft
vertex therefore carries X = 2 sum T X = 0 (gauge anomaly free) and accidental charges q = 2 sum T q:
  G2: V1 (2 gens) 2*2*2*(-1) = -8, Vb1 +4  -> -4;  f1: +8 - 4 - 4 = 0;  f2: +4 - 4 - 4 + 4 = 0;  f3..f5: 0 (singlets).
Renormalizable vertices conserve q and X, so closing the vertex needs external vevs with G2 = +4 (or -4 for the
anti-instanton) and X = 0: the dimension-21 monomial S^17 Phi17*^4 (conjugate of the tree operator's), at least.  So
small instantons produce the SAME phase structure as the Planck operator; their size relative to it is
  R(mu) = V_SI(mu) / V_tree,  V_SI(mu) ~ C (2 pi/alpha)^16 e^{-2 pi/alpha} mu^4 x Pi_S Pi_P Pi_F,
  Pi_S = (y <S>/mu)^14   (14 S-sector Dirac pairs, T_S = 14),
  Pi_P = min(1, yP <Phi17>/mu)^4   (Phi sector; heavy -> decouples with an aligned arg-det phase),
  Pi_F = [lam38 <Phi210> <S> / (16 pi^2 mu^2)]^3 x Pi_fam  (12 family zero modes closed through Y10, Y126 and the
         O38 H10-Delta mixing; Pi_fam = product of six Yukawa matrix elements, EST 1e-20 .. 1e-10).
alpha^-1(mu): linear in ln mu between 25.9 at M_U = 2.13e16 and 5.16 at M_Pl,red (ys_rg.py two-loop value), EST.
C_SO(10): the one-instanton measure constant (SU(N): 0.466 e^{-1.679N}/((N-1)!(N-2)!), 7.3e-7 for SU(5)); unknown
for SO(10), kept as a symbol (results are quoted per unit C).
Writes small_instantons.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
MPL, MU_U = 2.435e18, 2.13e16
AINV_U, AINV_P = 25.9, 5.158
S, P, PHI210 = 3.0e13, 1.0e17, 2.1e16
CHI = 0.0755 ** 4
V_TREE = 2 * (P / MPL) ** 4 * (S / MPL) ** 17 * MPL ** 4


def ainv(mu):
    t = (math.log(mu) - math.log(MU_U)) / (math.log(MPL) - math.log(MU_U))
    return AINV_U + t * (AINV_P - AINV_U)


def v_si(mu, y=math.sqrt(4 * math.pi), yP=math.sqrt(4 * math.pi), lam38=1.0, pifam=1e-10):
    a = ainv(mu)
    sinst = 2 * math.pi * a
    meas = sinst ** 16 * math.exp(-sinst) * mu ** 4
    pi_s = (y * S / mu) ** 14
    pi_p = min(1.0, yP * P / mu) ** 4
    pi_f = (lam38 * PHI210 * S / (16 * math.pi ** 2 * mu ** 2)) ** 3 * pifam
    return meas * pi_s * pi_p * pi_f


def main():
    out = {"V_tree_GeV4(<S>=3e13)": V_TREE, "chi_GeV4": CHI, "rows": []}
    worst = None
    for k in range(0, 41):
        mu = MU_U * (MPL / MU_U) ** (k / 40)
        v = v_si(mu)
        row = {"mu": mu, "alpha_inv": ainv(mu), "V_SI/C (GeV^4)": v, "R/C = V_SI/(C V_tree)": v / V_TREE,
               "dtheta_SI/C = V_SI/(C chi)": v / CHI}
        out["rows"].append(row)
        if worst is None or v > worst[1]:
            worst = (mu, v)
    out["max_over_mu"] = {"mu": worst[0], "R/C": worst[1] / V_TREE, "dtheta/C": worst[1] / CHI}
    # sensitivity: alpha^-1(MPl) = 3 (closer to a Landau pole) and Pi_fam = 1e-6 (extreme)
    global AINV_P
    keep = AINV_P
    sens = {}
    for ap, pf in ((5.158, 1e-10), (5.158, 1e-6), (3.0, 1e-10), (3.0, 1e-6), (2.0, 1e-6)):
        AINV_P = ap
        best = max(v_si(MU_U * (MPL / MU_U) ** (k / 40), pifam=pf) for k in range(41))
        sens["alphaInv(MPl)=%.2f, Pi_fam=%g" % (ap, pf)] = {"R/C": best / V_TREE, "dtheta/C": best / CHI}
    AINV_P = keep
    out["sensitivity"] = sens
    out["below_M_U"] = ("G3221 / SU(3) instantons: alpha^-1 >~ 35-45 -> e^{-2 pi alpha^-1} <~ 1e-96; for mu below the "
                        "exotic masses the exotics decouple with an aligned arg-det phase; light-quark closures need "
                        "y_u y_d ... ~ 1e-13 and loop factors: dtheta << 1e-40 (EST)")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in out["rows"][::8]:
        print("mu=%.3g a^-1=%.2f  R/C=%.3g  dtheta/C=%.3g" % (r["mu"], r["alpha_inv"], r["R/C = V_SI/(C V_tree)"],
                                                         r["dtheta_SI/C = V_SI/(C chi)"]))
    (HERE / "small_instantons.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
