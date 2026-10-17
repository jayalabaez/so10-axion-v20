"""Gate K0 (5): one-loop running of the S-sector Yukawa y_s and the singlet quartic lambda_S with the
F17 content; maximal y_s(M_s) that stays perturbative up to M_Pl,red = 2.435e18 GeV, and the minimal y_s
the axion-quality window needs (declared operator Phi17^4 S*^17 / M_Pl^17; also the Z17-EFT and NDA conventions).

RG conventions (one loop, chiral Yukawa y S psi chi with S complex, psi in R, chi in Rbar; Machacek-Vaughn /
Cheng-Eichten-Li; checked against the SM top-Yukawa beta 9/2 y_t^3 - 8 g3^2 y_t - 9/4 g2^2 y_t - 17/20 g1^2 y_t):
  16 pi^2 dy_k/dt = y_k [ sum_i d_i |y_i|^2  (gamma_S: every Dirac pair i coupled to S, multiplicity d_i)
                         + |y_k|^2            (gamma_psi + gamma_chi, one partner each)
                         - 3 sum_G g_G^2 (C2_G(psi) + C2_G(chi)) ]
  V = (lambda_S/2)|S|^4 == lambda |S|^4:  16 pi^2 dlambda/dt = 20 lambda^2 + 4 lambda sum d_i y_i^2 - 2 sum d_i y_i^4
                         [+ U(1)_X: -12 q^2 g_X^2 lambda + 6 q^4 g_X^4, q = 4, active only above <Phi17>]
  F17 S-sector: 3 x (16+16bar) (d = 16 each), 10+10 (d = 10), 2 singlet pairs (d = 1): sum d_i = 60 with a
  universal y_s; "58 Dirac components" + 2 singlets.
Gauge environment (NUM, inputs from the rescue study C4 numbers, not re-derived here: v_R = 2.6e13, M_U = 2.13e16,
alpha_U^-1 = 25.9 for T2; K1 owns the unification): SM one loop M_Z -> M_s (PDG 2024 inputs), SM + F17 complete
multiplets M_s -> v_R, G3221 with T2 + F17 content v_R -> M_U run DOWN from alpha_U at M_U (so the couplings
are consistent with the quoted unification point), SO(10) one+two loop above M_U (b1 = 8, exact MV b2), U(1)_X
one loop above <Phi17> = 1e17 with alpha_X fixed by alpha_X(M_Pl,red) = 1 (largest allowed; b_X = 4288 in the
integer-X normalisation).  The cap is reported for (a) no gauge terms (strict upper bound on y), (b) the least-gauged
component of the vectorlike 16 (nu^c-like), (c) the dimension-averaged Casimir of a 16.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
PI = math.pi
MPL = 2.435e18
MZ = 91.1876
CHI = 0.0755 ** 4  # GeV^4, chi^(1/4) = 75.5 MeV (Grilli di Cortona et al. 1511.02867; Borsanyi et al. 1606.07494)
MA_COEF = 5.70e-6  # eV, m_a = 5.70 ueV (1e12 GeV / f_a)  [1511.02867]
VPHI = 1.0e17      # <Phi17>
V_R = 2.6e13
M_U = 2.13e16
ALPHA_U_INV = 25.9
SUM_D = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
BX_ARG = sys.argv[2] if len(sys.argv) > 2 else "12865/3"
TAG = sys.argv[3] if len(sys.argv) > 3 else "k0b"
L16 = 16.0 * PI ** 2

# ---- gauge coefficients (exact Fractions) ------------------------------------------------------------------
# SM one loop (GUT-normalised U(1)_Y), three families + one Higgs doublet: (41/10, -19/6, -7).
B_SM = (Fr(41, 10), Fr(-19, 6), Fr(-7))
# F17 complete SO(10) multiplets below v_R: 3 x (16+16bar) + 10 + 10 Weyl: each 16: Delta b_i = (2/3) T = 4/3;
# each 10: 2/3.  Total 6 x 4/3 + 2 x 2/3 = 28/3 for every SM factor.
B_F17_LOW = Fr(28, 3)


def g3221_coefficients():
    """One-loop b for (SU(3), SU(2)_L, SU(2)_R, U(1)_{B-L} GUT-normalised: T_BL = sqrt(3/8)(B-L)).
    Content: 3 x 16_F + 6 x 16-type (Vec pairs) + 2 x 10_F (Weyl); scalars: Delta_R (10bar,1,3)_{B-L: see
    decomposition}, complex bidoublet (1,2,2)_0, complex (8,2,2)_0, real (8,3,1)_0, real (1,3,1)_0."""
    half, third = Fr(1, 2), Fr(1, 3)
    # (SU3 index, SU2L index, SU2R index, (B-L)^2 sum)*mult per Weyl multiplet; T_BL^2 = 3/8 (B-L)^2
    # 16 = (3,2,1)_{1/3} + (3bar,1,2)_{-1/3} + (1,2,1)_{-1} + (1,1,2)_{1}
    def sixteen():
        s3 = half * 2 + half * 2            # (3,2,1): T3 = 1/2 x dim2 ; (3bar,1,2)
        s2l = half * 3 + half * 1
        s2r = half * 3 + half * 1
        bl = Fr(3, 8) * (6 * Fr(1, 9) + 6 * Fr(1, 9) + 2 * 1 + 2 * 1)
        return s3, s2l, s2r, bl
    # 10 = (3,1,1)_{2/3} + (3bar,1,1)_{-2/3} + (1,2,2)_0
    def ten():
        s3 = half + half
        s2l = half * 2
        s2r = half * 2
        bl = Fr(3, 8) * (6 * Fr(4, 9))
        return s3, s2l, s2r, bl
    b = [Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)]
    nf16 = 3 + 6
    for _ in range(nf16):
        for i, v in enumerate(sixteen()):
            b[i] += Fr(2, 3) * v
    for _ in range(2):
        for i, v in enumerate(ten()):
            b[i] += Fr(2, 3) * v
    # scalars (complex: 1/3 T; real: 1/6 T)
    # Delta_R (10bar,1,3): SU(4) 10bar -> (6bar)_{-2/3} + (3)_{2/3} + (1)_{2}: SU3 index (5/2 + 1/2) x 3 = 9;
    # SU2R index 10 x 2 = 20; B-L: 18 x 4/9 + 9 x 4/9 + 3 x 4 = 24 -> 3/8 x 24 = 9
    b[0] += third * 9
    b[2] += third * 20
    b[3] += third * 9
    # bidoublet (1,2,2)_0 complex: SU2L 1, SU2R 1
    b[1] += third * 1
    b[2] += third * 1
    # (8,2,2)_0 complex: SU3 3 x 4 = 12; SU2L 8 x 2 x 1/2 = 8; SU2R 8
    b[0] += third * 12
    b[1] += third * 8
    b[2] += third * 8
    # (8,3,1)_0 real: SU3 3 x 3 = 9; SU2L 8 x 2 = 16
    b[0] += Fr(1, 6) * 9
    b[1] += Fr(1, 6) * 16
    # (1,3,1)_0 real: SU2L 2
    b[1] += Fr(1, 6) * 2
    return tuple(b)


def so10_coefficients():
    """SO(10) one- and two-loop gauge coefficients (MV, Weyl fermions; complex scalar = 2 real)."""
    CG = Fr(8)
    reps = {"10": (10, Fr(1), Fr(9, 2)), "16": (16, Fr(2), Fr(45, 8)), "126": (126, Fr(35), Fr(25, 2)),
            "210": (210, Fr(56), Fr(12))}
    ferm = [("16", 3 + 6 + 2), ("10", 2)]      # Weyl multiplets: 3 F + 6 Vec + 2 PhiV ; TenA, TenB
    scal = [("210", "real", 1), ("126", "cplx", 1), ("10", "cplx", 1)]
    b1 = Fr(-11, 3) * CG
    b2 = Fr(-34, 3) * CG * CG
    for name, mult in ferm:
        _d, T, C2 = reps[name]
        b1 += Fr(2, 3) * T * mult
        b2 += (Fr(10, 3) * CG + 2 * C2) * T * mult
    for name, kind, mult in scal:
        _d, T, C2 = reps[name]
        eta = Fr(1, 3) if kind == "cplx" else Fr(1, 6)
        b1 += eta * T * mult
        b2 += ((Fr(2, 3) * CG + 4 * C2) * T * mult) * (Fr(1) if kind == "cplx" else Fr(1, 2))
    # U(1)_X one loop, integer X normalisation: (2/3) sum_Weyl dim X^2 + (1/3) sum_cplx dim X^2
    bx = Fr(BX_ARG)
    return b1, b2, bx


B_G3221 = g3221_coefficients()
B1_SO10, B2_SO10, B_X = so10_coefficients()


def alpha_inv_sm(mu, m_s):
    """GUT-normalised (alpha_1^-1, alpha_2^-1, alpha_3^-1) at mu <= v_R (one loop)."""
    a = np.array([59.02, 29.58, 8.47])  # PDG 2024 at M_Z: alpha^-1 = 127.95, sin^2 = 0.23122, alpha_s = 0.1180
    t = math.log(mu / MZ)
    for i in range(3):
        a[i] -= float(B_SM[i]) / (2 * PI) * t
        if mu > m_s:
            a[i] -= float(B_F17_LOW) / (2 * PI) * math.log(mu / m_s)
    return a


def alpha_inv_g3221(mu):
    """(SU3, SU2L, SU2R, BL) at v_R <= mu <= M_U, run down from the common alpha_U at M_U (one loop)."""
    t = math.log(mu / M_U)
    return np.array([ALPHA_U_INV - float(b) / (2 * PI) * t for b in B_G3221])


def alpha_inv_so10(mu, two_loop=True):
    """SO(10) alpha^-1 above M_U: d alpha^-1/dt = -b1/(2 pi) - b2 alpha/(8 pi^2)."""
    b1, b2 = float(B1_SO10), float(B2_SO10)
    def rhs(t, y):
        a = 1.0 / y[0]
        return [-b1 / (2 * PI) - (b2 * a / (8 * PI ** 2) if two_loop else 0.0)]
    sol = solve_ivp(rhs, [math.log(M_U), math.log(mu)], [ALPHA_U_INV], rtol=1e-9, atol=1e-12, max_step=0.05)
    return sol.y[0, -1]


def alpha_inv_x(mu, alpha_x_inv_mpl=1.0):
    """U(1)_X above <Phi17>: alpha_X^-1(mu) = alpha_X^-1(M_Pl) + b_X/(2 pi) ln(M_Pl/mu)."""
    return alpha_x_inv_mpl + float(B_X) / (2 * PI) * math.log(MPL / mu)


def casimir_term(mu, m_s, variant):
    """3 sum_G g_G^2 (C2(psi) + C2(chi)) for the 16 pair, per variant: 'none', 'min', 'avg'."""
    if variant == "none":
        return 0.0
    if mu < V_R:
        a = alpha_inv_sm(mu, m_s)
        g2 = 4 * PI / a  # (g1^2, g2^2, g3^2), g1 GUT-normalised: (3/5) Y^2 -> g1^2 * (3/5) Y^2
        comps = [  # (dim, C_SU3, C_SU2, 3/5 Y^2)
            (6, 4 / 3, 3 / 4, 0.6 / 36), (3, 4 / 3, 0, 0.6 * 4 / 9), (3, 4 / 3, 0, 0.6 / 9),
            (2, 0, 3 / 4, 0.6 / 4), (1, 0, 0, 0.6), (1, 0, 0, 0)]
        vals = [c3 * g2[2] + c2 * g2[1] + cy * g2[0] for _d, c3, c2, cy in comps]
        if variant == "min":
            return 3 * 2 * min(vals)
        return 3 * 2 * sum(d * v for (d, *_), v in zip(comps, vals)) / 16
    if mu < M_U:
        a = alpha_inv_g3221(mu)
        g2 = 4 * PI / a  # (g3^2, g2L^2, g2R^2, gBL^2)
        comps = [  # (dim, C3, C2L, C2R, 3/8 (B-L)^2)
            (6, 4 / 3, 3 / 4, 0, 3 / 8 / 9), (6, 4 / 3, 0, 3 / 4, 3 / 8 / 9),
            (2, 0, 3 / 4, 0, 3 / 8), (2, 0, 0, 3 / 4, 3 / 8)]
        vals = [c3 * g2[0] + cl * g2[1] + cr * g2[2] + cb * g2[3] for _d, c3, cl, cr, cb in comps]
        if variant == "min":
            return 3 * 2 * min(vals)
        return 3 * 2 * sum(d * v for (d, *_), v in zip(comps, vals)) / 16
    g2 = 4 * PI / alpha_inv_so10(mu)
    term = 3 * 2 * (45 / 8) * g2
    if mu > VPHI:
        gx2 = 4 * PI / alpha_inv_x(mu)
        term += 3 * (0 ** 2 + 4 ** 2) * gx2 if variant == "min" else 3 * ((0 + 16) + (9 + 49) + (36 + 100)) / 3 * gx2
    return term


_SO10_DENSE = None
_CAS_TABLES = {}


def alpha_inv_so10_fast(mu):
    """Dense two-loop SO(10) solution above M_U (built once)."""
    global _SO10_DENSE
    if _SO10_DENSE is None:
        b1, b2 = float(B1_SO10), float(B2_SO10)
        sol = solve_ivp(lambda t, y: [-b1 / (2 * PI) - b2 / (8 * PI ** 2) / y[0]], [math.log(M_U), math.log(MPL) + 0.01],
                        [ALPHA_U_INV], rtol=1e-9, atol=1e-12, max_step=0.02, dense_output=True)
        _SO10_DENSE = sol.sol
    return float(_SO10_DENSE(math.log(mu))[0])


def cas_table(m_s, variant):
    """Casimir term on a grid in t (built once per (m_s, variant)); uses the fast SO(10) solution."""
    key = (m_s, variant)
    if key not in _CAS_TABLES:
        global alpha_inv_so10
        orig = alpha_inv_so10
        alpha_inv_so10 = lambda mu, two_loop=True: alpha_inv_so10_fast(mu)  # noqa: E731
        try:
            tg = np.linspace(math.log(m_s), math.log(MPL), 1600)
            vals = np.array([casimir_term(math.exp(t), m_s, variant) for t in tg])
        finally:
            alpha_inv_so10 = orig
        _CAS_TABLES[key] = (tg, vals)
    return _CAS_TABLES[key]


def run_yukawa(y0, m_s, variant, lam0=None, t_end=math.log(MPL)):
    """Integrate y_s (and lambda) from M_s to t_end.  Returns dict with final values / Landau scale."""
    tg, vals = cas_table(m_s, variant)

    def cas(t):
        return float(np.interp(t, tg, vals))

    def rhs(t, v):
        y, lam = v
        mu = math.exp(t)
        dy = y * ((SUM_D + 1.0) * y * y - cas(t)) / L16
        dl = (20 * lam * lam + 4 * lam * SUM_D * y * y - 2 * SUM_D * y ** 4) / L16
        if mu > VPHI and variant != "none":
            gx2 = 4 * PI / alpha_inv_x(mu)
            dl += (-12 * 16 * gx2 * lam + 6 * 256 * gx2 * gx2) / L16
        return [dy, dl]

    def landau(t, v):
        return v[0] - 10.0
    landau.terminal = True
    sol = solve_ivp(rhs, [math.log(m_s), t_end], [y0, 0.0 if lam0 is None else lam0], rtol=1e-8, atol=1e-12,
                    max_step=0.05, events=landau)
    hit = len(sol.t_events[0]) > 0
    return {"y_end": float(sol.y[0, -1]), "lambda_end": float(sol.y[1, -1]), "landau_below_MPl": hit,
            "landau_scale": float(math.exp(sol.t_events[0][0])) if hit else None, "t": sol.t, "y": sol.y[0], "lam": sol.y[1]}


def y_cap(m_s, variant, y_limit):
    """Largest y(M_s) with y(mu) <= y_limit for all M_s <= mu <= M_Pl,red (bisection)."""
    lo, hi = 0.05, 3.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        r = run_yukawa(mid, m_s, variant)
        ok = (not r["landau_below_MPl"]) and float(np.max(r["y"])) <= y_limit
        if ok:
            lo = mid
        else:
            hi = mid
    return lo


def lambda_window(m_s, y0, variant):
    """Minimal lambda_S(M_s) = 2 lambda keeping lambda > 0 to M_Pl,red, and maximal keeping lambda < 4 pi."""
    def ok_pos(l0):
        r = run_yukawa(y0, m_s, variant, lam0=l0)
        return float(np.min(r["lam"])) > 0 and not r["landau_below_MPl"]
    lo, hi = 0.0, 2.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if ok_pos(mid):
            hi = mid
        else:
            lo = mid
    lam_min = hi
    def ok_pert(l0):
        r = run_yukawa(y0, m_s, variant, lam0=l0)
        return float(np.max(r["lam"])) < 4 * PI and not r["landau_below_MPl"]
    lo, hi = lam_min, 10.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if ok_pert(mid):
            lo = mid
        else:
            hi = mid
    return 2 * lam_min, 2 * lo  # in lambda_S convention (V = lambda_S/2 |S|^4)


def quality(m_s, y_s, p_nda=None):
    sigma = m_s / y_s  # <S>
    d_declared = 2 * (VPHI / MPL) ** 4 * (sigma / MPL) ** 17 * MPL ** 4 / CHI
    d_eft = 2 * (sigma / MPL) ** 17 * MPL ** 4 / CHI
    d_nda12 = 2 * sigma ** 4 * (sigma / MPL) ** 12 / CHI
    d_nda = 2 * sigma ** 4 * (sigma / MPL) ** p_nda / CHI if p_nda is not None else None
    v_s = math.sqrt(2) * sigma
    v_phi = math.sqrt(2) * VPHI
    f_a = v_s * v_phi / math.sqrt(16 * v_s ** 2 + 289 * v_phi ** 2)
    m_a = MA_COEF * 1e12 / f_a
    return {"<S>": sigma, "dtheta_declared_Phi17^4S*17/MPl^17": d_declared, "dtheta_Z17_EFT_S17/MPl^13": d_eft,
            "dtheta_NDA_v20_P12": d_nda12, "dtheta_NDA_F17_P": d_nda, "f_a_GeV": f_a, "m_a_ueV": m_a * 1e6}


def y_min_quality(m_s, convention, p_nda=None):
    """Smallest y_s(M_s) with dtheta < 1e-10 (dtheta decreases with y since <S> = M_s/y)."""
    if convention == "declared":
        sigma_max = MPL * (1e-10 * CHI / (2 * VPHI ** 4)) ** (1 / 17)
    elif convention == "eft":
        sigma_max = MPL ** (13 / 17) * (1e-10 * CHI / 2) ** (1 / 17)
    else:
        sigma_max = MPL ** (p_nda / (4 + p_nda)) * (1e-10 * CHI / 2) ** (1 / (4 + p_nda))
    return m_s / sigma_max, sigma_max


def main() -> int:
    p_nda = None
    try:
        q = json.loads((HERE / "k0_quality_relics.json").read_text(encoding="utf-8"))
        p_nda = q["NDA_multi_operator_Z17_EFT"]["P_min_sum_(d_i-4)"]
        p_nda = float(p_nda) if p_nda is not None else None
    except Exception:  # noqa: BLE001
        pass
    out = {
        "coefficients": {
            "b_SM_one_loop": [str(b) for b in B_SM], "delta_b_F17_below_vR_each_factor": str(B_F17_LOW),
            "b_G3221_(SU3,SU2L,SU2R,BL)_T2+F17": [str(b) for b in B_G3221],
            "b1_SO10": str(B1_SO10), "b2_SO10_MV": str(B2_SO10), "b2_SO10_float": float(B2_SO10),
            "b_X_one_loop_integer_X": str(B_X),
            "alpha_X_inv_at_Phi17_for_alpha_X(MPl)=1": alpha_inv_x(VPHI),
            "alpha_X_inv_at_MU_for_alpha_X(MPl)=1": alpha_inv_x(M_U),
            "alpha_SO10_inv_at_MPl_1loop": alpha_inv_so10(MPL, two_loop=False),
            "alpha_SO10_inv_at_MPl_2loop": alpha_inv_so10(MPL, two_loop=True),
        },
        "inputs": {"v_R": V_R, "M_U": M_U, "alpha_U_inv": ALPHA_U_INV, "<Phi17>": VPHI, "M_Pl_red": MPL, "sum_d": SUM_D},
        "caps": {}, "lambda_S": {}, "quality": {}, "window": {},
    }
    for m_s in (3.0e12, 1.0e13):
        key = "M_s=%.1e" % m_s
        caps = {}
        for variant in ("none", "min", "avg"):
            caps[variant] = {
                "y_max_(y<=sqrt(4pi)_to_MPl)": y_cap(m_s, variant, math.sqrt(4 * PI)),
                "y_max_(y<=2_to_MPl)": y_cap(m_s, variant, 2.0),
                "y_max_(y<=1_to_MPl)": y_cap(m_s, variant, 1.0),
                "y_max_(non_increasing: y(MPl)<=y(M_s))": y_cap_noninc(m_s, variant),
            }
            for y0 in (0.30, 0.35, 0.39):
                r = run_yukawa(y0, m_s, variant)
                caps[variant]["y(MPl) from y(M_s)=%.2f" % y0] = r["y_end"]
        out["caps"][key] = caps
        lw = {}
        for y0 in (0.30, 0.35, 0.39):
            lmin, lmax = lambda_window(m_s, y0, "avg")
            lw["y_s=%.2f" % y0] = {"lambda_S_min_positive_to_MPl": lmin, "lambda_S_max_pert_to_MPl": lmax}
        out["lambda_S"][key] = lw
        qd = {}
        for y0 in (0.30, 0.305, 0.33, 0.35, 0.389, 0.45):
            qd["y_s=%.3f" % y0] = quality(m_s, y0, p_nda)
        ymin_decl, smax_decl = y_min_quality(m_s, "declared")
        ymin_eft, smax_eft = y_min_quality(m_s, "eft")
        ymin_nda12, smax_nda12 = y_min_quality(m_s, "nda", 12)
        qd["y_s_min_declared"] = ymin_decl
        qd["<S>_max_declared"] = smax_decl
        qd["y_s_min_Z17_EFT"] = ymin_eft
        qd["<S>_max_Z17_EFT"] = smax_eft
        qd["y_s_min_NDA_v20_P12"] = ymin_nda12
        if p_nda is not None:
            ymin_nda, smax_nda = y_min_quality(m_s, "nda", p_nda)
            qd["y_s_min_NDA_F17_P=%g" % p_nda] = ymin_nda
            qd["<S>_max_NDA_F17"] = smax_nda
        out["quality"][key] = qd
        cap_min = caps["min"]["y_max_(y<=sqrt(4pi)_to_MPl)"]
        cap_none = caps["none"]["y_max_(y<=sqrt(4pi)_to_MPl)"]
        out["window"][key] = {
            "declared_quality_y_min": ymin_decl,
            "perturbativity_y_max_no_gauge": cap_none,
            "perturbativity_y_max_least_gauged": cap_min,
            "perturbativity_y_max_avg_gauged": caps["avg"]["y_max_(y<=sqrt(4pi)_to_MPl)"],
            "ADMX_DFSZ_excluded_m_a_band_ueV": [2.66, 3.31],
            "y_s_giving_m_a=2.66ueV": y_for_ma(m_s, 2.66e-6),
            "y_s_giving_m_a=3.31ueV": y_for_ma(m_s, 3.31e-6),
            "consistent_window_declared_quality_x_perturbativity_(least_gauged)": [ymin_decl, cap_min] if cap_min > ymin_decl else None,
            "Z17_EFT_quality_y_min": ymin_eft,
            "consistent_window_Z17_EFT_x_perturbativity_(least_gauged)": [ymin_eft, cap_min] if cap_min > ymin_eft else None,
        }
    (HERE / ("ys_cap_%s.json" % TAG)).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["coefficients"], indent=1))
    for key in out["caps"]:
        print("==", key)
        print(json.dumps(out["caps"][key], indent=1))
        print(json.dumps(out["lambda_S"][key], indent=1))
        print(json.dumps({k: v for k, v in out["quality"][key].items() if not k.startswith("y_s=")}, indent=1))
        print(json.dumps(out["window"][key], indent=1))
    return 0


def y_cap_noninc(m_s, variant):
    lo, hi = 0.05, 3.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        r = run_yukawa(mid, m_s, variant)
        if (not r["landau_below_MPl"]) and r["y_end"] <= mid:
            lo = mid
        else:
            hi = mid
    return lo


def y_for_ma(m_s, m_a_ev):
    """y_s such that m_a = m_a_ev (f_a = v_S v_Phi/F; invert numerically)."""
    lo, hi = 0.05, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if quality(m_s, mid)["m_a_ueV"] * 1e-6 < m_a_ev:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    sys.exit(main())
