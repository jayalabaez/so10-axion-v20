#!/usr/bin/env python3
"""v21-F17-G3221 content for every segment, thresholds, chain solver and SO(10) x U(1)_X Landau scale."""
from __future__ import annotations

import math
from fractions import Fraction as F
from typing import Any

import numpy as np
from scipy.optimize import fsolve

from k1_lib import (A1_MZ, A2_MZ, A3_MZ, C_G_SO10, M_PL_RED, MZ, PI, SO10, SU2, SU3, Y_T_MZ, Segment, bl,
                    mv_coefficients, pgj_b, pgj_invariants, run_segment, s_factor, threshold_b, ysm, yt_run_sm)

# ---------------------------------------------------------------------------------------------------------------
# Group orders.  SM: (U(1)_Y, SU(2)_L, SU(3)_C) [repo order]; G3221: (SU(3), SU(2)_L, SU(2)_R, U(1)_{B-L}).
# ---------------------------------------------------------------------------------------------------------------
SM_C2 = (F(0), F(2), F(3))
G3221_C2 = (F(3), F(2), F(2), F(0))


def smrep(y, su2, su3):
    return (ysm(y), SU2[su2], SU3[su3])


def g3221(su3, su2l, su2r, bminusl):
    return (SU3[su3], SU2[su2l], SU2[su2r], bl(bminusl))


# One SO(10) 16 in SM and G3221 language (a 16bar has the same (dim, T, C2) data).
SIXTEEN_SM = (("Q", "weyl", smrep(F(1, 6), "2", "3")), ("uc", "weyl", smrep(F(-2, 3), "1", "3b")),
              ("dc", "weyl", smrep(F(1, 3), "1", "3b")), ("L", "weyl", smrep(F(-1, 2), "2", "1")),
              ("ec", "weyl", smrep(F(1), "1", "1")), ("nuc", "weyl", smrep(F(0), "1", "1")))
TEN_SM = (("D", "weyl", smrep(F(-1, 3), "1", "3")), ("Dc", "weyl", smrep(F(1, 3), "1", "3b")),
          ("Hu", "weyl", smrep(F(1, 2), "2", "1")), ("Hd", "weyl", smrep(F(-1, 2), "2", "1")))
SIXTEEN_G = (("QL", "weyl", g3221("3", "2", "1", F(1, 3))), ("QR", "weyl", g3221("3b", "1", "2", F(-1, 3))),
             ("LL", "weyl", g3221("1", "2", "1", F(-1))), ("LR", "weyl", g3221("1", "1", "2", F(1))))
TEN_G = (("D", "weyl", g3221("3", "1", "1", F(-2, 3))), ("Dc", "weyl", g3221("3b", "1", "1", F(2, 3))),
         ("Bd", "weyl", g3221("1", "2", "2", F(0))))


def sm_fields(n_sixteen_extra: int = 0, n_ten: int = 0, n_doublets: int = 1) -> list:
    """SM phase: 3 families + n_doublets Higgs doublets + S-sector (n_sixteen_extra Weyl 16-type, n_ten Weyl 10s)."""
    out = [(n, k, r, 3 + n_sixteen_extra) for n, k, r in SIXTEEN_SM]
    out += [(n, k, r, n_ten) for n, k, r in TEN_SM]
    out.append(("H", "cplx", smrep(F(1, 2), "2", "1"), n_doublets))
    return out


def light_scalars_g3221(content: str) -> list:
    """Tuned light scalar multiplets at v_R (T2 / T3) plus Delta_R, in G3221 language."""
    out = [("bidoublet (1,2,2)_0", "cplx", g3221("1", "2", "2", 0), 1),
           ("Delta_R (1,1,3)_2", "cplx", g3221("1", "1", "3", 2), 1),
           ("(8,2,2)_0 [126b]", "cplx", g3221("8", "2", "2", 0), 1),
           ("(8,3,1)_0 [210]", "real", g3221("8", "3", "1", 0), 1),
           ("(1,3,1)_0 [210]", "real", g3221("1", "3", "1", 0), 1)]
    if content == "T3":
        out += [("(1,2,2)_0 second [126b]", "cplx", g3221("1", "2", "2", 0), 1),
                ("(8,1,1)_0 [210]", "real", g3221("8", "1", "1", 0), 1)]
    elif content != "T2":
        raise ValueError(content)
    return out


def g3221_fields(content: str, with_s_sector: bool = True) -> list:
    out = [(n, k, r, 3 + (6 if with_s_sector else 0)) for n, k, r in SIXTEEN_G]
    if with_s_sector:
        out += [(n, k, r, 2) for n, k, r in TEN_G]
    out += light_scalars_g3221(content)
    return out


# Heavy scalars at M_U in G3221 language (Goldstones removed; the light ones removed per content).
HEAVY_210 = [  # (name, kind, reps)   real 210: self-conjugate pieces real, conjugate pairs one complex
    ("210:(8,1,1)_0", "real", g3221("8", "1", "1", 0)),
    ("210:(3,3,1)_4/3", "cplx", g3221("3", "3", "1", F(4, 3))),
    ("210:(8,1,3)_0", "real", g3221("8", "1", "3", 0)),
    ("210:(3,1,3)_4/3", "cplx", g3221("3", "1", "3", F(4, 3))),
    ("210:(1,1,3)_0", "real", g3221("1", "1", "3", 0)),
    ("210:(6,2,2)_2/3", "cplx", g3221("6", "2", "2", F(2, 3))),
    ("210:(3,2,2)_-2/3 phys", "cplx", g3221("3", "2", "2", F(-2, 3))),
    ("210:(1,2,2)_-2", "cplx", g3221("1", "2", "2", F(-2))),
    ("210:(8,3,1)_0", "real", g3221("8", "3", "1", 0)),  # light in T2/T3 -> removed below
    ("210:(1,3,1)_0", "real", g3221("1", "3", "1", 0)),  # light -> removed
]
HEAVY_126B = [
    ("126b:(3,1,1)_-2/3", "cplx", g3221("3", "1", "1", F(-2, 3))),
    ("126b:(3b,1,1)_2/3", "cplx", g3221("3b", "1", "1", F(2, 3))),
    ("126b:(6,3,1)_2/3", "cplx", g3221("6", "3", "1", F(2, 3))),
    ("126b:(3,3,1)_-2/3", "cplx", g3221("3", "3", "1", F(-2, 3))),
    ("126b:(1,3,1)_-2 Delta_L", "cplx", g3221("1", "3", "1", F(-2))),
    ("126b:(6b,1,3)_-2/3", "cplx", g3221("6b", "1", "3", F(-2, 3))),
    ("126b:(3b,1,3)_2/3", "cplx", g3221("3b", "1", "3", F(2, 3))),
    ("126b:(3,2,2)_4/3", "cplx", g3221("3", "2", "2", F(4, 3))),
    ("126b:(3b,2,2)_-4/3", "cplx", g3221("3b", "2", "2", F(-4, 3))),
    ("126b:(1,2,2)_0", "cplx", g3221("1", "2", "2", 0)),  # one bidoublet combination light (T2) / both (T3)
    ("126b:(8,2,2)_0", "cplx", g3221("8", "2", "2", 0)),  # light
    ("126b:(1,1,3)_2 Delta_R", "cplx", g3221("1", "1", "3", 2)),  # light
]
HEAVY_10 = [
    ("10:(3,1,1)_-2/3", "cplx", g3221("3", "1", "1", F(-2, 3))),
    ("10:(3b,1,1)_2/3", "cplx", g3221("3b", "1", "1", F(2, 3))),
    ("10:(1,2,2)_0", "cplx", g3221("1", "2", "2", 0)),
]
HEAVY_VECTORS = [
    ("V:(3,2,2)_-2/3 + cc", "vector", g3221("3", "2", "2", F(-2, 3)), 2),
    ("V:(3,1,1)_4/3 + cc", "vector", g3221("3", "1", "1", F(4, 3)), 2),
]
LIGHT_NAMES_REMOVED = {"T2": {"210:(8,3,1)_0", "210:(1,3,1)_0", "126b:(8,2,2)_0", "126b:(1,1,3)_2 Delta_R",
                              "126b:(1,2,2)_0"},
                       "T3": {"210:(8,3,1)_0", "210:(1,3,1)_0", "126b:(8,2,2)_0", "126b:(1,1,3)_2 Delta_R",
                              "126b:(1,2,2)_0", "210:(8,1,1)_0", "10:(1,2,2)_0"}}
# In T2 the light bidoublet is a 10/126b mixture: we remove the 126b (1,2,2) and keep the 10's (1,2,2) as the heavy
# orthogonal combination (the b_i are identical, only the name differs).  In T3 both are light.


def heavy_scalars_at_MU(content: str) -> list:
    removed = LIGHT_NAMES_REMOVED[content]
    return [(n, k, r, 1) for n, k, r in HEAVY_210 + HEAVY_126B + HEAVY_10 if n not in removed]


def light_thresholds_at_vR(content: str) -> list:
    """States integrated out at v_R, in SM language (name, kind, reps, mult)."""
    out = [("W_R+-", "vector", smrep(F(1), "1", "1"), 2),
           ("Delta_R++", "cplx", smrep(F(2), "1", "1"), 1),
           ("second doublet", "cplx", smrep(F(1, 2), "2", "1"), 1),
           ("(8,2)_1/2", "cplx", smrep(F(1, 2), "2", "8"), 1),
           ("(8,2)_-1/2", "cplx", smrep(F(-1, 2), "2", "8"), 1),
           ("(8,3)_0", "real", smrep(F(0), "3", "8"), 1),
           ("(1,3)_0", "real", smrep(F(0), "3", "1"), 1)]
    if content == "T3":
        out += [("second bidoublet doublets", "cplx", smrep(F(1, 2), "2", "1"), 2),
                ("(8,1)_0", "real", smrep(F(0), "1", "8"), 1)]
    return out


# SO(10) phase content.
SO10_BASE = [("16", "weyl", 3), ("16", "weyl", 3), ("16b", "weyl", 3), ("10", "weyl", 2),
             ("210", "real", 1), ("126b", "cplx", 1), ("10", "cplx", 1)]
SO10_PHI_PAIR = [("16", "weyl", 1), ("16b", "weyl", 1)]
SO10_V20_NO_PQR = [("16", "weyl", 3), ("16", "weyl", 5), ("16b", "weyl", 5), ("210", "real", 1),
                   ("126b", "cplx", 1), ("10", "cplx", 1)]
SO10_V20_WITH_PQR = SO10_V20_NO_PQR + [("16", "weyl", 3), ("16b", "weyl", 3)]

# U(1)_X charges of the v21 content (Weyl fermions / complex scalars; the real 210 has X = 0).
X_WEYL = [("16", 1, 3), ("16", 0, 1), ("16b", 4, 1), ("16", -3, 1), ("16b", 7, 1), ("16", -6, 1), ("16b", 10, 1),
          ("10", -1, 1), ("10", 5, 1), ("1", -3, 2), ("1", -1, 2)]
X_WEYL_PHI = [("16", -9, 1), ("16b", -8, 1)]
X_CPLX = [("126b", -2, 1), ("10", -2, 1), ("1", 4, 1), ("1", 17, 1)]


def so10_coeffs(content: list) -> tuple[F, F, F]:
    return pgj_b(pgj_invariants(content, SO10, C_G_SO10))


def so10_yukawa_Y(y_s: float, y_phi: float | None, Y10_tr2: float, Y126_tr2: float, lam126: float) -> float:
    """Y_SO10 = 14 y_s^2 (S-sector: 2 T(R) per Dirac pair) + 4 y_phi^2 + 10 Tr(Y10^2) + 2 lam126 Tr(Y126^2).

    10 = (C2(16)/45) x 80: the 16.16.10 coupling normalised to y_t = Y10 has Sum_{A,j,k}|Y|^2 = 80 Y10^2 (gamma-matrix
    computation k1_so10_yukawa_norm: nu^c row = 5 in y_t units, times 16).  lam126 = 126/16 (M_R = Y126 v_R normalisation)
    gives 2 lam126 = 63/4 = 15.75."""
    y = 14.0 * y_s**2 + 10.0 * Y10_tr2 + 2.0 * lam126 * Y126_tr2
    if y_phi is not None:
        y += 4.0 * y_phi**2
    return y


def u1x_coeffs(with_phi: bool) -> tuple[F, F, F]:
    """(b_X, b_{10,X}, b_{X,10}): one-loop U(1)_X and the two-loop cross terms (g_X normalised to the integer X)."""
    bx, b10x, bx10 = F(0), F(0), F(0)
    weyl = X_WEYL + (X_WEYL_PHI if with_phi else [])
    for rep, x, m in weyl:
        d, t, c = SO10[rep]
        bx += F(2, 3) * m * d * x * x
        b10x += 2 * m * t * x * x  # S_10 = T(R); C2_X = X^2
        bx10 += 2 * m * (d * x * x) * c  # S_X = X^2 dim(R); C2_10(R)
    for rep, x, m in X_CPLX:
        d, t, c = SO10[rep]
        bx += F(1, 3) * m * d * x * x
        b10x += 4 * m * t * x * x
        bx10 += 4 * m * (d * x * x) * c
    return bx, b10x, bx10


# ---------------------------------------------------------------------------------------------------------------
# Chain parameters.
# ---------------------------------------------------------------------------------------------------------------
class Params:
    def __init__(self, **kw):
        self.content = "T2"
        self.loops = 2            # 1, 2 or 3 (3 = three-loop SO(10) gauge+matter; product-group 3L optional below)
        self.M_s = 1.0e13
        self.y_s = 0.35
        self.M_phi = 1.0e17       # Phi-sector pair mass (>= M_U)
        self.y_phi = 1.0
        self.light_ratios: dict[str, float] = {}   # name -> M/v_R for light thresholds (default 1)
        self.gut_ratios: dict[str, float] = {}     # name -> M/M_U for heavy scalars at M_U (default 1)
        self.v311_ratio = 1.0     # (3,1,1)_4/3 vector mass / M_U
        self.planck_c = 0.0
        self.planck_eps = (0.0, 0.0, 0.0, 0.0)     # K_i vev/M_Pl per unit c for (SU3, SU2L, SU2R, BL)
        self.yukawa = True
        self.Y126_tr2 = 0.5       # Tr(Y126 Y126^dag) at M_U (EST; scanned)
        self.lam126 = 126.0 / 16.0  # from k1_so10_yukawa_norm (lambda_126 = row/ref = 126/16); 0 -> omit
        self.alpha_x_inv_mpl = None  # None: U(1)_X feedback off; else alpha_X^-1(M_Pl,red) bound
        self.sm_3loop = False     # include pure-gauge three-loop in the SM/G3221 phases (single-group PGJ per factor, EST)
        self.n_doublets_sm = 1
        for k, v in kw.items():
            if not hasattr(self, k):
                raise KeyError(k)
            setattr(self, k, v)


def _mv(group_c2, fields, loops, yuk=None, b3=None):
    b, bij = mv_coefficients(group_c2, fields)
    return Segment(b, bij, b3=b3, yuk=yuk, loops=loops)


def _single_group_b3_per_factor(group_c2, fields) -> list[F]:
    """Pure (alpha_i)^4 three-loop coefficient of each factor from the single-group PGJ formula (cross terms omitted)."""
    out = []
    for i, cg in enumerate(group_c2):
        content = []
        for name, kind, reps, mult in fields:
            # treat the other factors as multiplicity
            d, t, c = reps[i]
            m = F(mult)
            for k, r in enumerate(reps):
                if k != i:
                    m *= r[0]
            if t == 0:
                continue
            content.append(((d, t, c), kind, m))
        reps_map = {rep: rep for rep, _k, _m in content}
        inv = pgj_invariants([(rep, k, m) for rep, k, m in content], reps_map, cg)
        out.append(pgj_b(inv)[2])
    return out


class Chain:
    """Builds the segments once per Params and evaluates the unification residuals."""

    def __init__(self, p: Params):
        self.p = p
        lo = 2 if p.loops >= 2 else 1
        self.loops_low = lo
        # SM segments
        self.f_sm0 = sm_fields(0, 0, p.n_doublets_sm)
        self.f_sm1 = sm_fields(6, 2, p.n_doublets_sm)
        self.f_g = g3221_fields(p.content, True)
        self.f_g_noS = g3221_fields(p.content, False)
        b3_sm0 = b3_sm1 = b3_g = b3_gn = None
        if p.sm_3loop and p.loops >= 3:
            b3_sm0 = _single_group_b3_per_factor(SM_C2, self.f_sm0)
            b3_sm1 = _single_group_b3_per_factor(SM_C2, self.f_sm1)
            b3_g = _single_group_b3_per_factor(G3221_C2, self.f_g)
            b3_gn = _single_group_b3_per_factor(G3221_C2, self.f_g_noS)
        lo_eff = 3 if (p.sm_3loop and p.loops >= 3) else lo
        self.seg_sm0 = _mv(SM_C2, self.f_sm0, lo_eff, yuk=self._yuk_sm0 if p.yukawa else None, b3=b3_sm0)
        self.seg_sm1 = _mv(SM_C2, self.f_sm1, lo_eff, yuk=self._yuk_sm1 if p.yukawa else None, b3=b3_sm1)
        self.seg_g = _mv(G3221_C2, self.f_g, lo_eff, yuk=self._yuk_g if p.yukawa else None, b3=b3_g)
        self.seg_g_noS = _mv(G3221_C2, self.f_g_noS, lo_eff, yuk=self._yuk_g_noS if p.yukawa else None, b3=b3_gn)
        # SO(10)
        self.b_so10_lo = so10_coeffs(SO10_BASE)
        self.b_so10_hi = so10_coeffs(SO10_BASE + SO10_PHI_PAIR)
        self.heavy = heavy_scalars_at_MU(p.content)
        self.light = light_thresholds_at_vR(p.content)
        self.yt_vR = None

    # Yukawa terms (two-loop gauge-Yukawa): Y_i arrays.
    def _yuk_sm0(self, t, ainv):
        yt2 = self._yt2(t)
        return np.array([1.7, 1.5, 2.0]) * yt2

    def _yuk_sm1(self, t, ainv):
        yt2 = self._yt2(t)
        return np.array([1.7, 1.5, 2.0]) * yt2 + 14.0 * self.p.y_s**2

    def _yuk_g(self, t, ainv):
        yt2 = self._yt2(t)
        return np.array([4.0, 4.0, 4.0, 4.0]) * yt2 + 14.0 * self.p.y_s**2

    def _yuk_g_noS(self, t, ainv):
        yt2 = self._yt2(t)
        return np.array([4.0, 4.0, 4.0, 4.0]) * yt2

    def _yt2(self, t):
        # crude: y_t(mu) ~ y_t(MZ) run at one loop in the SM once (cached), frozen above v_R at its v_R value
        if self.yt_vR is None:
            return Y_T_MZ**2
        tv = math.log(self.yt_vR[0])
        if t >= tv:
            return self.yt_vR[1] ** 2
        # linear interpolation in t between MZ and v_R
        f = (t - math.log(MZ)) / (tv - math.log(MZ))
        return (Y_T_MZ + f * (self.yt_vR[1] - Y_T_MZ)) ** 2

    # ---- thresholds -------------------------------------------------------------------------------------------
    def D_light(self) -> np.ndarray:
        """D_i = +(1/2pi) sum_k b_i^k ln(M_k/v_R) for the SM factors (added to the SM alpha^-1 to get the tree G3221 combos)."""
        d = np.zeros(3)
        for name, kind, reps, mult in self.light:
            r = self.p.light_ratios.get(name, 1.0)
            if r == 1.0:
                continue
            for i in range(3):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(r) / (2 * PI)
        return d

    def D_gut(self) -> np.ndarray:
        """D_i = +(1/2pi) sum_k b_i^k ln(M_k/M_U) for the G3221 factors: E_i = alpha_i^-1(M_U) + D_i = alpha_U^-1(1+eps_i)."""
        d = np.zeros(4)
        for name, kind, reps, mult in self.heavy:
            r = self.p.gut_ratios.get(name, 1.0)
            if r == 1.0:
                continue
            for i in range(4):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(r) / (2 * PI)
        if self.p.v311_ratio != 1.0:
            name, kind, reps, mult = HEAVY_VECTORS[1]
            for i in range(4):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(self.p.v311_ratio) / (2 * PI)
        return d

    # ---- running ----------------------------------------------------------------------------------------------
    def run_to_MU(self, ln_vR: float, ln_MU: float, a2R_inv_vR: float) -> dict:
        p = self.p
        t0, tv, tu = math.log(MZ), ln_vR, ln_MU
        ts = math.log(p.M_s)
        a = np.array([A1_MZ, A2_MZ, A3_MZ])
        if ts < tv:
            a, _, _ = run_segment(self.seg_sm0, a, t0, ts)
            a, _, _ = run_segment(self.seg_sm1, a, ts, tv)
        else:
            a, _, _ = run_segment(self.seg_sm0, a, t0, tv)
        a_sm_vR = a.copy()
        D = self.D_light()
        a1, a2, a3 = a + D
        a3C, a2L = a3, a2
        aBL = 2.5 * (a1 - 0.6 * a2R_inv_vR)
        g = np.array([a3C, a2L, a2R_inv_vR, aBL])
        if ts < tv:
            g, _, _ = run_segment(self.seg_g, g, tv, tu)
        else:
            if ts < tu:
                g, _, _ = run_segment(self.seg_g_noS, g, tv, ts)
                g, _, _ = run_segment(self.seg_g, g, ts, tu)
            else:
                g, _, _ = run_segment(self.seg_g_noS, g, tv, tu)
        E = g + self.D_gut()
        eps = np.array(p.planck_eps) * p.planck_c
        aU = E / (1.0 + eps)
        return {"a_sm_vR": a_sm_vR, "g_vR": np.array([a3C, a2L, a2R_inv_vR, aBL]), "g_MU": g, "E": E, "aU_i": aU,
                "resid": np.array([aU[0] - aU[1], aU[2] - aU[1], aU[3] - aU[1]]), "alpha_U_inv": float(aU[1])}

    def solve(self, guess=(math.log(3e13), math.log(2.5e16), 46.0)) -> dict:
        def fun(x):
            try:
                r = self.run_to_MU(x[0], x[1], x[2])["resid"]
                if not np.all(np.isfinite(r)):
                    raise FloatingPointError
                return r
            except Exception:
                return np.array([1.0e3, 1.0e3, 1.0e3]) * (1.0 + np.abs(x[0] - 30.0))

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            x, info, ier, msg = fsolve(fun, np.array(guess, dtype=float), full_output=True, xtol=1e-11)
        try:
            res = self.run_to_MU(*x)
            ok = ier == 1 and np.max(np.abs(res["resid"])) < 1e-6 and np.all(np.isfinite(res["resid"]))
        except Exception:
            res, ok = None, False
        if not ok:
            # retry from a second guess
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                x2, info, ier, msg = fsolve(fun, np.array([math.log(1e13), math.log(5e16), 44.0]), full_output=True,
                                            xtol=1e-11)
            try:
                res2 = self.run_to_MU(*x2)
                if ier == 1 and np.max(np.abs(res2["resid"])) < 1e-6 and np.all(np.isfinite(res2["resid"])):
                    x, res, ok = x2, res2, True
            except Exception:
                pass
        if res is None:
            return {"ok": False, "v_R": float("nan"), "M_U": float("nan"), "a2R_inv_vR": float("nan"),
                    "alpha_U_inv": float("nan"), "resid_max": float("nan"), "g_vR": [], "g_MU": [], "a_sm_vR": [], "aU_i": []}
        out = {"ok": bool(ok), "v_R": math.exp(x[0]), "M_U": math.exp(x[1]), "a2R_inv_vR": float(x[2]),
               "alpha_U_inv": res["alpha_U_inv"], "resid_max": float(np.max(np.abs(res["resid"]))),
               "g_vR": res["g_vR"].tolist(), "g_MU": res["g_MU"].tolist(), "a_sm_vR": res["a_sm_vR"].tolist(),
               "aU_i": res["aU_i"].tolist()}
        return out

    # ---- SO(10) x U(1)_X phase ---------------------------------------------------------------------------------
    def landau(self, M_U: float, alpha_U_inv: float, loops: int | None = None, b3_factor: float = 1.0,
               t_end: float = math.log(1e24)) -> dict:
        p = self.p
        loops = p.loops if loops is None else loops
        tu, tphi = math.log(M_U), math.log(max(p.M_phi, M_U))
        Y_lo = so10_yukawa_Y(p.y_s, None, self._yt2(tu), p.Y126_tr2, p.lam126) if p.yukawa else 0.0
        Y_hi = so10_yukawa_Y(p.y_s, p.y_phi, self._yt2(tu), p.Y126_tr2, p.lam126) if p.yukawa else 0.0
        bx_lo, b10x_lo, bx10_lo = u1x_coeffs(False)
        bx_hi, b10x_hi, bx10_hi = u1x_coeffs(True)
        use_x = p.alpha_x_inv_mpl is not None

        def make(bb, Y, bx, b10x, bx10):
            b1, b2, b3 = bb
            if use_x:
                b = [b1, bx]
                bij = [[b2, b10x], [bx10, F(0)]]  # U(1)_X two-loop self term omitted (irrelevant at this order)
                b3v = [b3 * b3_factor, F(0)]
                yuk = (lambda t, ainv: np.array([Y, 0.0])) if Y else None
            else:
                b, bij, b3v = [b1], [[b2]], [b3 * b3_factor]
                yuk = (lambda t, ainv: np.array([Y])) if Y else None
            return Segment(b, bij, b3=b3v, yuk=yuk, loops=loops)

        seg_lo = make(self.b_so10_lo, Y_lo, bx_lo, b10x_lo, bx10_lo)
        seg_hi = make(self.b_so10_hi, Y_hi, bx_hi, b10x_hi, bx10_hi)
        if use_x:
            # alpha_X^-1 at M_U from the one-loop bound alpha_X^-1(M_Pl,red) = alpha_x_inv_mpl (U(1)_X with full content)
            ax_mu = p.alpha_x_inv_mpl + float(bx_hi) / (2 * PI) * (math.log(M_PL_RED) - tu)
            y0 = np.array([alpha_U_inv, ax_mu])
        else:
            y0 = np.array([alpha_U_inv])
        y, t, hit = run_segment(seg_lo, y0, tu, tphi, landau_event=True)
        a_phi = float(y[0])
        if not hit:
            y, t, hit = run_segment(seg_hi, y, tphi, t_end, landau_event=True)
        lam = math.exp(t) if hit else float("inf")
        # alpha^-1 at M_Pl,red (if reached)
        a_mpl = None
        tpl = math.log(M_PL_RED)
        yy = y0.copy()
        if tphi >= tpl:
            yy, _, h = run_segment(seg_lo, yy, tu, tpl, landau_event=True)
        else:
            yy, _, h = run_segment(seg_lo, yy, tu, tphi, landau_event=True)
            if not h:
                yy, _, h = run_segment(seg_hi, yy, tphi, tpl, landau_event=True)
        a_mpl = float(yy[0]) if not h else None
        return {"Lambda": lam, "Lambda_over_MPl": lam / M_PL_RED, "alpha_inv_MPl": a_mpl, "alpha_inv_Mphi": a_phi,
                "b_lo": [str(x) for x in self.b_so10_lo], "b_hi": [str(x) for x in self.b_so10_hi],
                "Y_lo": Y_lo, "Y_hi": Y_hi, "loops": loops}


def set_yt(chain: Chain, v_R: float) -> None:
    """Run y_t from M_Z to v_R at one loop (SM) and cache for the two-loop Yukawa terms."""
    a0 = np.array([A1_MZ, A2_MZ, A3_MZ])
    yt = yt_run_sm(Y_T_MZ, a0, math.log(MZ), math.log(v_R), chain.seg_sm0)
    chain.yt_vR = (v_R, yt)


def proton_lifetime_years(M_X: float, alpha_inv: float) -> float:
    """Repo normalisation (proton_decay_falsification_gate_v20.gauge_lifetime_years): p -> e+ pi0, d = 6 gauge."""
    f_pi, m_p, alpha_h, a_r, f_q = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    hbar, year = 6.582119569e-25, 365.25 * 24 * 3600
    alpha = 1.0 / alpha_inv
    tau = (4.0 / PI) * (f_pi**2 / m_p) * (M_X**4 / alpha**2) / (alpha_h**2 * a_r**2 * f_q)
    return tau * hbar / year
