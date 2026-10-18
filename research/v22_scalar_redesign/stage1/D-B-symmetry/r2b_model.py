#!/usr/bin/env python3
"""Gate R2-B model: realisable G3221 light contents with the v21-B63 fermion sector.

Generalises K1's k1_model.py (round 1) to an arbitrary set of light G3221 scalar multiplets taken from the complete
G3221 decomposition of 210 (real) + 126bar (complex) + 10 (complex), with
  * exact Machacek-Vaughn one/two-loop coefficients for every segment (k1_lib.mv_coefficients, Fractions),
  * the S-sector (B63: 3 x (16 + 16bar) + 2 x 10 Weyl, T_S = 14) at M_s = y_s <S> and the Phi pair 16(-35)+16bar(18)
    (T_Phi = 4) at M_Phi,
  * one-loop MS-bar matching at v_R and M_U including (switchable, sign-selectable) the heavy-vector constant
    alpha_low^-1 = alpha_high^-1 - S_V,i/(12 pi) (S_V = (5,6,6,8) at M_U, 6/5 for U(1)_Y at v_R),
  * the (3,1,1)_{4/3} vector at its Am45 mass ratio M(3,1,1)/M(3,2,2) = sqrt(0.8) = 0.894 (K3 chart: 0.5774/0.6455),
  * the Planck gauge-kinetic operator with the exact Clebsches K = (-2a, 2 s p, -2 s p, 4a) at the Am45 orientation
    ((p, a) = (0.70711, -0.40825) |Phi| in K1's normalisation, |Phi| = M_U/(0.6455 g_U)),
  * SO(10) x U(1)_X running above M_U with the exact B63 U(1)_X coefficients (b_X = 101203 for the full content),
    the two-loop cross terms b_{10,X}, b_{X,10}, the U(1)_X two-loop self term b_XX, PGJ three-loop SO(10) term.
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from typing import Any

import numpy as np
from scipy.optimize import brentq, fsolve

from r2b_lib import (A1_MZ, A2_MZ, A3_MZ, C_G_SO10, M_PL_RED, MZ, PI, SO10, SU2, SU3, Y_T_MZ, Segment, bl,
                     mv_coefficients, pgj_b, pgj_invariants, run_segment, s_factor, threshold_b, ysm, yt_run_sm)

SM_C2 = (F(0), F(2), F(3))            # (U(1)_Y, SU(2)_L, SU(3)_C)
G3221_C2 = (F(3), F(2), F(2), F(0))   # (SU(3), SU(2)_L, SU(2)_R, U(1)_{B-L})

# Am45 orientation (K3 chart): (p, a_K3, omega) = (0.70711, -0.70711, 0); K1 normalisation a_K1 = a_K3/sqrt3.
P_AM45 = 1.0 / math.sqrt(2.0)
A_AM45 = -1.0 / math.sqrt(6.0)
MX_OVER_G_PHI = math.sqrt(P_AM45 ** 2 / 2.0 + A_AM45 ** 2)          # 0.6455 = M(3,2,2)/(g |Phi|)
M311_OVER_G_PHI = math.sqrt(2.0 * A_AM45 ** 2)                      # 0.5774 = M(3,1,1)/(g |Phi|)
R311_AM45 = M311_OVER_G_PHI / MX_OVER_G_PHI                          # 0.8944


def smrep(y, su2, su3):
    return (ysm(y), SU2[su2], SU3[su3])


def g3221(su3, su2l, su2r, bminusl):
    return (SU3[su3], SU2[su2l], SU2[su2r], bl(bminusl))


# ---------------------------------------------------------------------------------------------------------------
# Complete G3221 scalar table of 210 (real) + 126bar + 10 (complex), Goldstones removed (K1 table, completeness
# re-checked: 178 + 2 singlets + 30 Goldstones = 210 real; 126 and 10 complex).  Entry: name -> (kind, su3, 2L, 2R, B-L)
# ---------------------------------------------------------------------------------------------------------------
SCALAR_TABLE: dict[str, tuple[str, str, str, str, F]] = {
    "210:(8,1,1)_0": ("real", "8", "1", "1", F(0)),
    "210:(3,3,1)_4/3": ("cplx", "3", "3", "1", F(4, 3)),
    "210:(8,1,3)_0": ("real", "8", "1", "3", F(0)),
    "210:(3,1,3)_4/3": ("cplx", "3", "1", "3", F(4, 3)),
    "210:(1,1,3)_0": ("real", "1", "1", "3", F(0)),
    "210:(6,2,2)_2/3": ("cplx", "6", "2", "2", F(2, 3)),
    "210:(3,2,2)_-2/3 phys": ("cplx", "3", "2", "2", F(-2, 3)),
    "210:(1,2,2)_-2": ("cplx", "1", "2", "2", F(-2)),
    "210:(8,3,1)_0": ("real", "8", "3", "1", F(0)),
    "210:(1,3,1)_0": ("real", "1", "3", "1", F(0)),
    "126b:(3,1,1)_-2/3": ("cplx", "3", "1", "1", F(-2, 3)),
    "126b:(3b,1,1)_2/3": ("cplx", "3b", "1", "1", F(2, 3)),
    "126b:(6,3,1)_2/3": ("cplx", "6", "3", "1", F(2, 3)),
    "126b:(3,3,1)_-2/3": ("cplx", "3", "3", "1", F(-2, 3)),
    "126b:(1,3,1)_-2 Delta_L": ("cplx", "1", "3", "1", F(-2)),
    "126b:(6b,1,3)_-2/3": ("cplx", "6b", "1", "3", F(-2, 3)),
    "126b:(3b,1,3)_2/3": ("cplx", "3b", "1", "3", F(2, 3)),
    "126b:(3,2,2)_4/3": ("cplx", "3", "2", "2", F(4, 3)),
    "126b:(3b,2,2)_-4/3": ("cplx", "3b", "2", "2", F(-4, 3)),
    "126b:(1,2,2)_0": ("cplx", "1", "2", "2", F(0)),
    "126b:(8,2,2)_0": ("cplx", "8", "2", "2", F(0)),
    "126b:(1,1,3)_2 Delta_R": ("cplx", "1", "1", "3", F(2)),
    "10:(3,1,1)_-2/3": ("cplx", "3", "1", "1", F(-2, 3)),
    "10:(3b,1,1)_2/3": ("cplx", "3b", "1", "1", F(2, 3)),
    "10:(1,2,2)_0": ("cplx", "1", "2", "2", F(0)),
}
HEAVY_VECTORS = [("V:(3,2,2)_-2/3 + cc", "vector", g3221("3", "2", "2", F(-2, 3)), 2),
                 ("V:(3,1,1)_4/3 + cc", "vector", g3221("3", "1", "1", F(4, 3)), 2)]
BID = ("126b:(1,2,2)_0", "10:(1,2,2)_0")
DR = "126b:(1,1,3)_2 Delta_R"

CONTENTS: dict[str, tuple[str, ...]] = {
    # round-2 contents (light at v_R, besides the 3 families and the B63 S-sector)
    "C0": (BID[0], DR, "210:(8,3,1)_0"),                    # K3-realisable, one bidoublet (flavour-dead)
    "C1": (BID[0], BID[1], DR, "210:(8,3,1)_0"),            # two bidoublets + (8,3,1)_0
    "C2": (BID[0], BID[1], DR),                             # two bidoublets
    "C1p": (BID[0], BID[1], DR, "210:(1,3,1)_0"),           # two bidoublets + (1,3,1)_0
    # round-1 references (validation against K1 and its skeptics)
    "T2": (BID[0], DR, "126b:(8,2,2)_0", "210:(8,3,1)_0", "210:(1,3,1)_0"),
    "T3": (BID[0], BID[1], DR, "126b:(8,2,2)_0", "210:(8,3,1)_0", "210:(1,3,1)_0", "210:(8,1,1)_0"),
    "bid_DR": (BID[0], DR),
    # rescue candidates found by r2b_rescue.py (need R2-A realisability)
    "C1+813": (BID[0], BID[1], DR, "210:(8,3,1)_0", "210:(8,1,3)_0"),
    "C1+622": (BID[0], BID[1], DR, "210:(8,3,1)_0", "210:(6,2,2)_2/3"),
    "C1+822": (BID[0], BID[1], DR, "210:(8,3,1)_0", "126b:(8,2,2)_0"),
}


def content_with(base: str, extra: tuple[str, ...]) -> tuple[str, ...]:
    out = list(CONTENTS[base])
    for e in extra:
        if e in out:
            raise ValueError(f"{e} already light in {base}")
        if e not in SCALAR_TABLE:
            raise KeyError(e)
        out.append(e)
    return tuple(out)


def g3221_entry(name: str):
    kind, c3, l, r, q = SCALAR_TABLE[name]
    return (name, kind, g3221(c3, l, r, q), 1)


def sm_pieces(name: str) -> list[tuple[str, str, tuple, int]]:
    """SM decomposition (Y = T3R + (B-L)/2) of one G3221 multiplet; real multiplets -> real pieces (b sums correctly)."""
    kind, c3, l, r, q = SCALAR_TABLE[name]
    nr = int(r)
    out = []
    for k in range(nr):
        t3r = F(nr - 1, 2) - k
        y = t3r + q / 2
        out.append((f"{name}|Y={y}", kind, smrep(y, l, c3), 1))
    return out


# One SO(10) 16 / 10 in SM and G3221 language (a 16bar has the same (dim, T, C2) data).
SIXTEEN_SM = (("Q", "weyl", smrep(F(1, 6), "2", "3")), ("uc", "weyl", smrep(F(-2, 3), "1", "3b")),
              ("dc", "weyl", smrep(F(1, 3), "1", "3b")), ("L", "weyl", smrep(F(-1, 2), "2", "1")),
              ("ec", "weyl", smrep(F(1), "1", "1")), ("nuc", "weyl", smrep(F(0), "1", "1")))
TEN_SM = (("D", "weyl", smrep(F(-1, 3), "1", "3")), ("Dc", "weyl", smrep(F(1, 3), "1", "3b")),
          ("Hu", "weyl", smrep(F(1, 2), "2", "1")), ("Hd", "weyl", smrep(F(-1, 2), "2", "1")))
SIXTEEN_G = (("QL", "weyl", g3221("3", "2", "1", F(1, 3))), ("QR", "weyl", g3221("3b", "1", "2", F(-1, 3))),
             ("LL", "weyl", g3221("1", "2", "1", F(-1))), ("LR", "weyl", g3221("1", "1", "2", F(1))))
TEN_G = (("D", "weyl", g3221("3", "1", "1", F(-2, 3))), ("Dc", "weyl", g3221("3b", "1", "1", F(2, 3))),
         ("Bd", "weyl", g3221("1", "2", "2", F(0))))
N16_S, N10_S = 6, 2   # B63 S-sector: 3 x (16 + 16bar) and 2 x 10 (Weyl), T_S = 6*2 + 2*1 = 14


def sm_fields(with_s: bool, n_doublets: int = 1) -> list:
    out = [(n, k, r, 3 + (N16_S if with_s else 0)) for n, k, r in SIXTEEN_SM]
    if with_s:
        out += [(n, k, r, N10_S) for n, k, r in TEN_SM]
    out.append(("H", "cplx", smrep(F(1, 2), "2", "1"), n_doublets))
    return out


def g3221_fields(light: tuple[str, ...], with_s: bool) -> list:
    out = [(n, k, r, 3 + (N16_S if with_s else 0)) for n, k, r in SIXTEEN_G]
    if with_s:
        out += [(n, k, r, N10_S) for n, k, r in TEN_G]
    out += [g3221_entry(n) for n in light]
    return out


def light_thresholds_at_vR(light: tuple[str, ...]) -> list:
    """States integrated out at v_R (SM language): W_R+- plus every SM piece of the light G3221 multiplets, minus the
    SM Higgs doublet (one (1,2)_{1/2} of the first bidoublet) and minus the Delta_R^+ Goldstone (Y = 1 piece)."""
    out = [("W_R+-", "vector", smrep(F(1), "1", "1"), 2)]
    higgs_removed = False
    for name in light:
        for piece in sm_pieces(name):
            pname, kind, reps, mult = piece
            if name == DR and pname.endswith("|Y=1"):
                continue  # eaten by W_R^+
            if (not higgs_removed) and name in BID and pname.endswith("|Y=1/2"):
                higgs_removed = True
                continue  # the light SM Higgs
            out.append(piece)
    if any(n in BID for n in light) and not higgs_removed:
        raise RuntimeError("Higgs not removed")
    return out


def heavy_scalars_at_MU(light: tuple[str, ...]) -> list:
    return [g3221_entry(n) for n in SCALAR_TABLE if n not in light]


# SO(10) phase content (B63 = K1 content multiplet by multiplet).
SO10_BASE = [("16", "weyl", 3), ("16", "weyl", 3), ("16b", "weyl", 3), ("10", "weyl", 2),
             ("210", "real", 1), ("126b", "cplx", 1), ("10", "cplx", 1)]
SO10_PHI_PAIR = [("16", "weyl", 1), ("16b", "weyl", 1)]

# U(1)_X charges of v21-B63 (K0b candB63.json): (rep, X, multiplicity)
X_WEYL_B63 = [("16", 1, 3), ("16", -35, 1), ("16b", 39, 1), ("16", -28, 1), ("16b", 32, 1), ("16", 34, 1),
              ("16b", -30, 1), ("10", 2, 2), ("1", -63, 1), ("1", 59, 1), ("1", -58, 1), ("1", 54, 1),
              ("1", -57, 1), ("1", 61, 1), ("1", -2, 2)]
X_WEYL_B63_PHI = [("16", -35, 1), ("16b", 18, 1)]
X_CPLX = [("126b", -2, 1), ("10", -2, 1), ("1", 4, 1), ("1", 17, 1)]
X_MAX = 63


def so10_coeffs(content: list) -> tuple[F, F, F]:
    return pgj_b(pgj_invariants(content, SO10, C_G_SO10))


def u1x_coeffs(with_phi: bool) -> dict[str, F]:
    """b_X, b_{10,X} (SO(10) row, X column), b_{X,10}, b_XX for integer-normalised X (exact Fractions)."""
    bx = b10x = bx10 = bxx = F(0)
    weyl = X_WEYL_B63 + (X_WEYL_B63_PHI if with_phi else [])
    for rep, x, m in weyl:
        d, t, c = SO10[rep]
        bx += F(2, 3) * m * d * x * x
        b10x += 2 * m * t * x * x
        bx10 += 2 * m * (d * x * x) * c
        bxx += 2 * m * d * x ** 4
    for rep, x, m in X_CPLX:
        d, t, c = SO10[rep]
        bx += F(1, 3) * m * d * x * x
        b10x += 4 * m * t * x * x
        bx10 += 4 * m * (d * x * x) * c
        bxx += 4 * m * d * x ** 4
    return {"b_X": bx, "b_10X": b10x, "b_X10": bx10, "b_XX": bxx}


def so10_yukawa_Y(y_s: float, y_phi: float | None, Y10_tr2: float, Y126_tr2: float, lam126: float) -> float:
    y = 14.0 * y_s ** 2 + 10.0 * Y10_tr2 + 2.0 * lam126 * Y126_tr2
    if y_phi is not None:
        y += 4.0 * y_phi ** 2
    return y


def _single_group_b3_per_factor(group_c2, fields) -> list[F]:
    """Pure (alpha_i)^4 three-loop coefficient of each factor (single-group PGJ, other factors as multiplicity)."""
    out = []
    for i, cg in enumerate(group_c2):
        content = []
        for name, kind, reps, mult in fields:
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


def sv_constants() -> tuple[np.ndarray, float]:
    """S_V per G3221 factor of the heavy vectors at M_U (EXACT: (5, 6, 6, 8)), and S_V(U(1)_Y) of W_R at v_R (6/5)."""
    sv = []
    for i in range(4):
        s = F(0)
        for _n, _k, reps, mult in HEAVY_VECTORS:
            s += s_factor(reps, i) * mult
        sv.append(s)
    svY = s_factor(smrep(F(1), "1", "1"), 0) * 2
    return np.array([float(x) for x in sv]), float(svY), [str(x) for x in sv], str(svY)


SV_MU, SV_Y_VR, SV_MU_STR, SV_Y_STR = sv_constants()


class Params:
    def __init__(self, **kw):
        self.light: tuple[str, ...] = CONTENTS["C0"]
        self.loops = 2
        self.M_s = 1.0e13
        self.y_s = 0.336            # centre of the B63 window [0.304, 0.368] at M_s = 1e13
        self.M_phi = 1.0e17
        self.y_phi = 1.0
        self.light_ratios: dict[str, float] = {}
        self.gut_ratios: dict[str, float] = {}
        self.v311_ratio = R311_AM45
        self.planck_c = 0.0
        self.planck_s = +1
        self.sv_sign = +1           # +1: MS-bar constant alpha_low^-1 = alpha_high^-1 - S_V/(12 pi); 0: off; -1: opposite
        self.yukawa = True
        self.Y126_tr2 = 0.5
        self.lam126 = 126.0 / 16.0
        self.alpha_x_inv_mpl = None  # None: no U(1)_X feedback; float: alpha_X^-1(M_Pl,red) target (shooting)
        self.sm_3loop = False
        self.n_doublets_sm = 1
        for k, v in kw.items():
            if not hasattr(self, k):
                raise KeyError(k)
            setattr(self, k, v)


def _mv(group_c2, fields, loops, yuk=None, b3=None):
    b, bij = mv_coefficients(group_c2, fields)
    return Segment(b, bij, b3=b3, yuk=yuk, loops=loops)


class Chain:
    def __init__(self, p: Params):
        self.p = p
        lo = 2 if p.loops >= 2 else 1
        use3 = p.sm_3loop and p.loops >= 3
        lo_eff = 3 if use3 else lo
        self.f_sm0 = sm_fields(False, p.n_doublets_sm)
        self.f_sm1 = sm_fields(True, p.n_doublets_sm)
        self.f_g = g3221_fields(p.light, True)
        self.f_g_noS = g3221_fields(p.light, False)
        b3 = (lambda c2, f: _single_group_b3_per_factor(c2, f)) if use3 else (lambda c2, f: None)
        self.seg_sm0 = _mv(SM_C2, self.f_sm0, lo_eff, yuk=self._yuk_sm0 if p.yukawa else None, b3=b3(SM_C2, self.f_sm0))
        self.seg_sm1 = _mv(SM_C2, self.f_sm1, lo_eff, yuk=self._yuk_sm1 if p.yukawa else None, b3=b3(SM_C2, self.f_sm1))
        self.seg_g = _mv(G3221_C2, self.f_g, lo_eff, yuk=self._yuk_g if p.yukawa else None, b3=b3(G3221_C2, self.f_g))
        self.seg_g_noS = _mv(G3221_C2, self.f_g_noS, lo_eff, yuk=self._yuk_g_noS if p.yukawa else None,
                             b3=b3(G3221_C2, self.f_g_noS))
        self.b_g = [str(x) for x in mv_coefficients(G3221_C2, self.f_g)[0]]
        self.b_g_noS = [str(x) for x in mv_coefficients(G3221_C2, self.f_g_noS)[0]]
        self.b_so10_lo = so10_coeffs(SO10_BASE)
        self.b_so10_hi = so10_coeffs(SO10_BASE + SO10_PHI_PAIR)
        self.heavy = heavy_scalars_at_MU(p.light)
        self.light_thr = light_thresholds_at_vR(p.light)
        self.yt_vR = None

    # ---- two-loop Yukawa terms (K1 conventions) ----
    def _yt2(self, t):
        if self.yt_vR is None:
            return Y_T_MZ ** 2
        tv = math.log(self.yt_vR[0])
        if t >= tv:
            return self.yt_vR[1] ** 2
        f = (t - math.log(MZ)) / (tv - math.log(MZ))
        return (Y_T_MZ + f * (self.yt_vR[1] - Y_T_MZ)) ** 2

    def _yuk_sm0(self, t, ainv):
        return np.array([1.7, 1.5, 2.0]) * self._yt2(t)

    def _yuk_sm1(self, t, ainv):
        return np.array([1.7, 1.5, 2.0]) * self._yt2(t) + 14.0 * self.p.y_s ** 2

    def _yuk_g(self, t, ainv):
        return np.array([4.0, 4.0, 4.0, 4.0]) * self._yt2(t) + 14.0 * self.p.y_s ** 2

    def _yuk_g_noS(self, t, ainv):
        return np.array([4.0, 4.0, 4.0, 4.0]) * self._yt2(t)

    # ---- thresholds ----
    def D_light(self) -> np.ndarray:
        d = np.zeros(3)
        for name, kind, reps, mult in self.light_thr:
            r = self.p.light_ratios.get(name, self.p.light_ratios.get("*", 1.0))
            if r == 1.0:
                continue
            for i in range(3):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(r) / (2 * PI)
        d[0] += self.p.sv_sign * SV_Y_VR / (12 * PI)
        return d

    def D_gut(self) -> np.ndarray:
        d = np.zeros(4)
        for name, kind, reps, mult in self.heavy:
            r = self.p.gut_ratios.get(name, self.p.gut_ratios.get("*", 1.0))
            if r == 1.0:
                continue
            for i in range(4):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(r) / (2 * PI)
        if self.p.v311_ratio != 1.0:
            name, kind, reps, mult = HEAVY_VECTORS[1]
            for i in range(4):
                d[i] += float(threshold_b(kind, reps, i, mult)) * math.log(self.p.v311_ratio) / (2 * PI)
        d += self.p.sv_sign * SV_MU / (12 * PI)
        return d

    def planck_eps(self, M_U: float, aU_inv: float) -> np.ndarray:
        if self.p.planck_c == 0.0:
            return np.zeros(4)
        g = math.sqrt(4 * PI / aU_inv)
        phi = M_U / (g * MX_OVER_G_PHI)
        s = self.p.planck_s
        K = np.array([-2 * A_AM45, 2 * s * P_AM45, -2 * s * P_AM45, 4 * A_AM45]) * phi
        return self.p.planck_c * K / M_PL_RED

    # ---- running ----
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
        a1, a2, a3 = a + self.D_light()
        aBL = 2.5 * (a1 - 0.6 * a2R_inv_vR)
        g = np.array([a3, a2, a2R_inv_vR, aBL])
        g_vR = g.copy()
        if ts < tv:
            g, _, _ = run_segment(self.seg_g, g, tv, tu)
        elif ts < tu:
            g, _, _ = run_segment(self.seg_g_noS, g, tv, ts)
            g, _, _ = run_segment(self.seg_g, g, ts, tu)
        else:
            g, _, _ = run_segment(self.seg_g_noS, g, tv, tu)
        E = g + self.D_gut()
        aU0 = E[1]
        eps = self.planck_eps(math.exp(tu), max(aU0, 1.0))
        aU = E / (1.0 + eps)
        return {"a_sm_vR": a_sm_vR, "g_vR": g_vR, "g_MU": g, "E": E, "aU_i": aU, "eps": eps,
                "resid": np.array([aU[0] - aU[1], aU[2] - aU[1], aU[3] - aU[1]]), "alpha_U_inv": float(aU[1])}

    def solve(self, guesses=None) -> dict:
        if guesses is None:
            guesses = [(math.log(3e13), math.log(2.5e16), 46.0), (math.log(1e10), math.log(1.5e16), 50.0),
                       (math.log(5e12), math.log(3e15), 48.0), (math.log(1e8), math.log(3e17), 52.0),
                       (math.log(3e11), math.log(1e16), 49.0)]

        def fun(x):
            try:
                r = self.run_to_MU(x[0], x[1], x[2])["resid"]
                if not np.all(np.isfinite(r)):
                    raise FloatingPointError
                return r
            except Exception:
                return np.array([1.0e3, 1.0e3, 1.0e3]) * (1.0 + abs(x[0] - 30.0))

        import warnings
        best = None
        for gs in guesses:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                x, info, ier, msg = fsolve(fun, np.array(gs, dtype=float), full_output=True, xtol=1e-11)
            try:
                res = self.run_to_MU(*x)
                rmax = float(np.max(np.abs(res["resid"])))
                ok = (ier == 1 or rmax < 1e-8) and rmax < 1e-6 and np.all(np.isfinite(res["resid"]))
            except Exception:
                continue
            phys = ok and (math.log(MZ) + 1 < x[0] < x[1]) and res["alpha_U_inv"] > 1.0
            cand = (phys, -rmax, x, res, ok)
            if phys:
                best = cand
                break
            if best is None or (cand[0], cand[1]) > (best[0], best[1]):
                best = cand
        if best is None:
            return {"ok": False}
        phys, mrmax, x, res, ok = best
        return {"ok": bool(phys), "v_R": math.exp(x[0]), "M_U": math.exp(x[1]), "a2R_inv_vR": float(x[2]),
                "alpha_U_inv": res["alpha_U_inv"], "resid_max": -mrmax, "g_vR": res["g_vR"].tolist(),
                "g_MU": res["g_MU"].tolist(), "aU_i": res["aU_i"].tolist(), "eps": res["eps"].tolist()}

    # ---- SO(10) x U(1)_X phase ----
    def landau(self, M_U: float, alpha_U_inv: float, loops: int | None = None, b3_factor: float = 1.0,
               t_end: float = math.log(1e24)) -> dict:
        p = self.p
        loops = p.loops if loops is None else loops
        tu, tphi = math.log(M_U), math.log(max(p.M_phi, M_U))
        tpl = math.log(M_PL_RED)
        Y_lo = so10_yukawa_Y(p.y_s, None, self._yt2(tu), p.Y126_tr2, p.lam126) if p.yukawa else 0.0
        Y_hi = so10_yukawa_Y(p.y_s, p.y_phi, self._yt2(tu), p.Y126_tr2, p.lam126) if p.yukawa else 0.0
        xlo, xhi = u1x_coeffs(False), u1x_coeffs(True)
        use_x = p.alpha_x_inv_mpl is not None

        def make(bb, Y, xc):
            b1, b2, b3 = bb
            if use_x:
                b = [b1, xc["b_X"]]
                bij = [[b2, xc["b_10X"]], [xc["b_X10"], xc["b_XX"]]]
                b3v = [b3 * F(b3_factor).limit_denominator(1000), F(0)]
                yuk = (lambda t, ainv: np.array([Y, 0.0])) if Y else None
            else:
                b, bij, b3v = [b1], [[b2]], [b3 * F(b3_factor).limit_denominator(1000)]
                yuk = (lambda t, ainv: np.array([Y])) if Y else None
            return Segment(b, bij, b3=b3v, yuk=yuk, loops=loops)

        seg_lo, seg_hi = make(self.b_so10_lo, Y_lo, xlo), make(self.b_so10_hi, Y_hi, xhi)

        def run_full(y0, t_stop, event=True, idx=None):
            y, t, hit = run_segment(seg_lo, y0, tu, min(tphi, t_stop), landau_event=event, event_index=idx)
            if (not hit) and t_stop > tphi:
                y, t, hit = run_segment(seg_hi, y, tphi, t_stop, landau_event=event, event_index=idx)
            return y, t, hit

        ax_mu = None
        if use_x:
            target = p.alpha_x_inv_mpl

            def f(ax0):
                y, t, hit = run_full(np.array([alpha_U_inv, ax0]), tpl, event=True)
                if hit and t < tpl - 1e-9:
                    if y[1] <= y[0]:
                        return -1.0e6 * (1.0 + (tpl - t))   # U(1)_X reached alpha = 1 below M_Pl: start weaker
                    raise RuntimeError("SO10 first")
                return float(y[1]) - target
            lo_, hi_ = target + 1.0, target + 1.0e7
            try:
                ax_mu = brentq(f, lo_, hi_, xtol=1e-6, maxiter=200)
            except Exception:
                # SO(10) reaches alpha = 1 below M_Pl: fix alpha_X^-1(M_U) from the U(1)_X-only one-loop + b_XX run
                segx = Segment([xhi["b_X"]], [[xhi["b_XX"]]], loops=2)

                def fx(ax0):
                    y, t, hit = run_segment(segx, np.array([ax0]), tu, tpl, landau_event=True)
                    return (-1.0e6 if hit else float(y[0]) - target)
                try:
                    ax_mu = brentq(fx, lo_, hi_, xtol=1e-6, maxiter=200)
                except Exception:
                    ax_mu = target + float(xhi["b_X"]) / (2 * PI) * (tpl - tu)
            y0 = np.array([alpha_U_inv, ax_mu])
        else:
            y0 = np.array([alpha_U_inv])
        y, t, hit = run_full(y0, t_end, event=True)
        lam = math.exp(t) if hit else float("inf")
        which = None
        if hit:
            which = "SO10" if (not use_x or y[0] <= y[1]) else "U1X"
        try:
            yy, _, h = run_full(y0.copy(), tpl, event=True, idx=0)
        except RuntimeError:
            yy, _, h = run_full(y0.copy(), tpl, event=True, idx=None)  # U(1)_X pole before M_Pl: stop there
        a_mpl = float(yy[0]) if not h else None
        ax_mpl = (float(yy[1]) if (use_x and not h) else None)
        return {"Lambda": lam, "Lambda_over_MPl": lam / M_PL_RED, "first_to_alpha1": which,
                "alpha_inv_MPl": a_mpl, "alphaX_inv_MPl": ax_mpl, "alphaX_inv_MU": ax_mu,
                "Y_lo": Y_lo, "Y_hi": Y_hi, "loops": loops}


def set_yt(chain: Chain, v_R: float) -> None:
    a0 = np.array([A1_MZ, A2_MZ, A3_MZ])
    yt = yt_run_sm(Y_T_MZ, a0, math.log(MZ), math.log(max(v_R, 200.0)), chain.seg_sm0)
    chain.yt_vR = (v_R, yt)


def proton_lifetime_years(M_X: float, alpha_inv: float, alpha_h: float = 0.012) -> float:
    """Repository normalisation (proton_decay_falsification_gate_v20.gauge_lifetime_years): p -> e+ pi0, gauge d = 6;
    alpha_H = alpha_bar_H (1 + D + F) absorbed (LIT-abstract), F_q = 2 (1 + |V_ud|^2)^2 = 7.6 for SO(10)."""
    f_pi, m_p, a_r, f_q = 0.139, 0.9382720813, 2.726, 7.6
    hbar, year = 6.582119569e-25, 365.25 * 24 * 3600
    alpha = 1.0 / alpha_inv
    tau = (4.0 / PI) * (f_pi ** 2 / m_p) * (M_X ** 4 / alpha ** 2) / (alpha_h ** 2 * a_r ** 2 * f_q)
    return tau * hbar / year


def proton_lifetime_direct_years(M_X: float, alpha_inv: float, W0: float = 0.131, A: float = 2.726,
                                 Vud: float = 0.9737) -> float:
    """Second normalisation (EST, derived in this gate): direct lattice form factor W0 = <pi0|(ud)_R u_L|p>
    (Aoki et al. 1705.01338, |W0| ~ 0.131 GeV^2 at 2 GeV; value quoted from memory, not re-read), lattice-basis
    Wilson coefficients from the SO(10) X,Y,X',Y' exchange after Weyl Fierz: C^{LR} = 2 k^2 (1 + |V_ud|^2),
    C^{RL} = 4 k^2, k^2 = g_U^2/(2 M_X^2);  Gamma = (m_p/32 pi)(1 - m_pi^2/m_p^2)^2 A^2 W0^2 (|C^{LR}|^2 + |C^{RL}|^2)
    = (pi m_p/2)(1 - x)^2 A^2 W0^2 alpha_U^2 [(1 + |V_ud|^2)^2 + 4] / M_X^4."""
    m_p, m_pi = 0.9382720813, 0.1349768
    hbar, year = 6.582119569e-25, 365.25 * 24 * 3600
    alpha = 1.0 / alpha_inv
    fq = (1 + Vud ** 2) ** 2 + 4
    gam = (PI * m_p / 2) * (1 - (m_pi / m_p) ** 2) ** 2 * A ** 2 * W0 ** 2 * alpha ** 2 * fq / M_X ** 4
    return hbar / gam / year


def full_point(p: Params, landau_loops=(2, 3), x_opts=(None,)) -> dict:
    """Solve the chain (two-pass: y_t at v_R), then Landau scales and tau_p."""
    ch = Chain(p)
    r = ch.solve()
    if r.get("ok"):
        set_yt(ch, r["v_R"])
        guess = [(math.log(r["v_R"]), math.log(r["M_U"]), r["a2R_inv_vR"])]
        r2 = ch.solve(guesses=guess + [(math.log(3e13), math.log(2.5e16), 46.0)])
        if r2.get("ok"):
            r = r2
    out = dict(r)
    out["b_G3221"] = ch.b_g
    if not r.get("ok"):
        return out
    out["tau_p_yr"] = proton_lifetime_years(r["M_U"], r["alpha_U_inv"])
    out["tau_p_yr_alphaH0.0144"] = proton_lifetime_years(r["M_U"], r["alpha_U_inv"], alpha_h=0.0144)
    out["M311"] = r["M_U"] * p.v311_ratio
    for L in landau_loops:
        for xo in x_opts:
            save = p.alpha_x_inv_mpl
            p.alpha_x_inv_mpl = xo
            lm = ch.landau(r["M_U"], r["alpha_U_inv"], loops=L)
            p.alpha_x_inv_mpl = save
            key = f"L{L}" + ("" if xo is None else f"_ax{xo:g}")
            out[key] = lm["Lambda_over_MPl"]
            out[key + "_first"] = lm["first_to_alpha1"]
            out[key + "_a10inv_MPl"] = lm["alpha_inv_MPl"]
            if xo is not None:
                out[key + "_axMU"] = lm["alphaX_inv_MU"]
    return out
