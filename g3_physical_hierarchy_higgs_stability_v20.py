#!/usr/bin/env python3
"""Two-loop Higgs-vacuum stability at the physical G3 hierarchy.

Commit 5f25846's version of ``g3_tuned_target_portal_threshold_v20`` matched
the H-S portal threshold

    lambda_SM = lambda_H - lambda_HS^2 / (4 lambda_S)

at M_GUT with one-loop SM running from mu0 = 173.10 (lambda_eff(M_GUT) =
-0.0335).  The current portal module uses this module's two-loop value
(-0.0151) and finds the matched point is a saddle.  A negative light-doublet
quartic at the matching point means the tuned point is not a tree-level local
minimum.  In the repository's physical hierarchy
(``gauged_u1x_g2_derivative_audit_v20.physical_hierarchy_state``) S and Sigma
sit at M_I = 6.31e11 GeV, so the threshold belongs at M_I.  This module redoes
the problem as a two-stage running problem:

* below M_I: the Standard Model, two loops (complete 1L+2L gauge / yt / lambda
  betas, gY not GUT-normalised), from the Buttazzo et al. 2013 NNLO MSbar inputs
  at mu = M_t;
* at M_I: tree-level matching lambda_H = lambda_SM + lambda_HS^2/(4 lambda_S);
* above M_I: SM + complex gauge singlet S with
  V > lambda_H (H^dag H)^2 + lambda_S |S|^4 + lambda_HS (H^dag H)|S|^2, with
  the one-loop portal terms derived here (and checked against the general
  scalar-tensor formula, Elias-Miro et al. 1203.0237 eq. (RG) and SMASH
  1610.01639 App. A after lambda_HS = 2 lambda_Hsigma):
      16pi^2 beta_lambdaH  = SM(lambda -> lambda_H) + lambda_HS^2
      16pi^2 beta_lambdaS  = 20 lambda_S^2 + 2 lambda_HS^2
      16pi^2 beta_lambdaHS = lambda_HS (12 lambda_H + 8 lambda_S + 4 lambda_HS
                                        + 6 yt^2 - 9/2 g2^2 - 3/2 gY^2)
  plus the two-loop SM terms, run to M_GUT.

The SM coefficient tables are copied (not imported) from the workflow
consensus solver ``sm_rge2.py``: two independent one/two-loop transcriptions
(Luo-Wang-Xiao gY form and Buttazzo App. B verbatim) must agree exactly, and
the three-loop + four-loop-QCD terms reproduce the published Buttazzo
lambda(M_Pl) = -0.0143.

Results at the Buttazzo central inputs (M_t = 173.34, M_h = 125.15,
alpha_s = 0.1184), two loops:

* Lambda_I (MSbar lambda = 0) = 4.76e9 GeV, below M_I by a factor ~130;
  lambda_SM(M_I) = -0.00854, lambda_SM(M_GUT) = -0.0151, lambda_min = -0.0155.
* Threshold at M_I: absolute stability of the EW vacuum is impossible at
  central inputs, for every (lambda_S, lambda_HS).  It needs lambda_SM > 0 up
  to the threshold.  Tree level agrees: with the S vev switched on, the EW/S
  point is a local (and global) tree minimum iff lambda_SM(threshold) >= 0.  In
  the RG-improved potential the EW vacuum is metastable, and the bounce estimate S ~ 8 pi^2/(3|lambda_SM(M_I)|) ~ 3.1e3
  is far above the ~500 needed.  Positive lambda_HS windows keep lambda_H > 0
  (a copositive (H, S) quartic) up to M_GUT, but copositivity is not the
  tree-level local-minimum condition (the single-stage point is copositive
  too).  At the tuned point that condition is lambda_eff = lambda_H -
  lambda_HS^2/(4 lambda_S) >= 0 (g3_tuned_target_portal_threshold_v20), and
  tree-level matching gives lambda_eff(M_I) = lambda_SM(M_I) = -0.0085 < 0 for
  every (lambda_S, lambda_HS): the M_I threshold does not remove the tree-level
  saddle.  At the GUT coefficients lambda_eff is negative at 4 of 5 window
  middles (+0.0003 at lambda_S(M_I) = 0.5).  Metastability is the RG-improved
  statement.
* Absolute stability with the threshold at M_I needs M_t < 171.96 GeV (2L),
  172.07 GeV (3L) with the MSbar-lambda criterion.  With PDG 2024 M_h and alpha_s
  the 3L bound is 171.95 GeV, 2.0 sigma below the measured 172.57 +- 0.29 GeV.
  With the Landau-gauge effective-potential zero (~6.5x higher) it is ~172.36 GeV,
  0.7 sigma below.  At both the Buttazzo and PDG 2024 central inputs the instability
  lies below M_I under either definition.
* GUT-scale coefficients: the certified (O36, O23, O34) = (1, 1, 0) gives m_h ~ 173
  GeV at two loops (lambda_HS = 0 is RG-invariant, S decouples).  Every window
  point needs O34 != 0.  Keeping O36 = O23 = 1 needs O34 = lambda_HS(M_GUT) ~ 2.07
  > 2, so lambda_eff(M_GUT) = -0.073 and that point is a tree-level saddle; the
  RG-improved EW vacuum is metastable, not absolutely stable.
* The threshold scale is really the radial-mode mass m_rho = 2 sqrt(lambda_S) M_I;
  absolute stability at central inputs is possible if lambda_S <~ 1.4e-5 (a
  SMASH-like tiny self-coupling), far from the certified O23 = 1 (RG-improved:
  lambda_eff(m_rho) > 0 there, but lambda_eff at the GUT coefficients is
  negative at every scanned window point).
* Single-stage GUT matching (the portal module) needs lambda_eff(M_GUT) =
  -0.0151 at two loops (-0.0335 at one loop): as with the M_I threshold, the
  tuned point is then not a tree-level local minimum and the EW vacuum is at
  best metastable.

Scope: only S is kept as an intermediate state.  Any colour-triplet partner
(the F-branch formula extrapolated to M_I gives sqrt(beta) M_I ~ 1.4e11 GeV,
but no such state has been constructed), light Sigma_126bar components, the
axion-sector vector-like fermion Yukawas that drive lambda_S, threshold loop
corrections and two-loop portal terms (a sensitivity estimate is included) are
omitted.  Nothing is closed or excluded: g3_closed, whole_model_validated and
whole_model_excluded stay False.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar, root

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_PHYSICAL_HIERARCHY_HIGGS_STABILITY_V20.json"
OUT_MD = ROOT / "G3_PHYSICAL_HIERARCHY_HIGGS_STABILITY_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
DIGITS = 12

# =============================================================================
# scales [GeV]
# =============================================================================
# Repository anchors (scalar_vacuum_proton_decay_v20._unification_anchor(), as
# used by gauged_u1x_g2_derivative_audit_v20._physical_hierarchy_metadata).
M_I_GEV = 6.313855230528793e11
M_GUT_GEV = 9.917564798898606e15
M_PL_GEV = 1.2209e19  # non-reduced Planck mass
SUPERSEDED_5F25846_M_GUT_GEV = 1.0e16  # reference M_GUT of the superseded one-loop portal module
V_EW_GEV = 246.22
ANCHOR_RTOL = 1.0e-12

# =============================================================================
# Standard Model inputs
# =============================================================================
# Buttazzo, Degrassi, Giardino, Giudice, Sala, Salvio, Strumia, arXiv:1307.3536
# v3/v4 (JHEP 1312 (2013) 089), NNLO MSbar couplings at mu = M_t.  These central
# values belong to M_t = 173.34, M_h = 125.15, alpha_s(M_Z) = 0.1184 and
# M_W = 80.384 GeV (v2 of the paper used M_t = 173.10 with different numbers).
MT_REF = 173.34
MH_REF = 125.15
ALPHA_S_REF = 0.1184
MW_REF = 80.384
BUTTAZZO_INPUTS = {"gY": 0.35830, "g2": 0.64779, "g3": 1.1666, "yt": 0.93690, "lam": 0.12604}
BUTTAZZO_THEORY_ERRORS = {"lam": 0.00030, "yt": 0.00050}
BUTTAZZO_PUBLISHED = {
    "lambda_M_Pl": -0.0143,
    "g1_M_Pl": 0.6154,
    "g2_M_Pl": 0.5055,
    "g3_M_Pl": 0.4873,
    "yt_M_Pl": 0.3825,
    "dlambda_M_Pl_dMt_per_GeV": -0.0066,
}
# Buttazzo et al. sec. 5: Lambda_lambda (MSbar lambda = 0) ~ 2 Lambda_V and the
# Landau-gauge effective-potential zero Lambda_I ~ 13 Lambda_V, so Lambda_I ~ 6.5 Lambda_lambda.
LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO = 13.0 / 2.0
# Regression anchor: these constants reproduce the superseded commit-5f25846
# one-loop portal values (same inputs started at mu0 = 173.10, matched at
# M_GUT = 1e16 GeV); the current portal module uses the two-loop value.
SUPERSEDED_5F25846_MU0 = 173.10
SUPERSEDED_5F25846_LAMBDA_GUT_ONE_LOOP = -0.033538209985
SUPERSEDED_5F25846_LAMBDA_HS_REQUIRED = 2.033261626043
SUPERSEDED_5F25846_ATOL = 1.0e-9
# Comparison values (PDG 2024): direct-measurement top mass, Higgs mass, alpha_s.
PDG2024 = {"Mt_GeV": 172.57, "Mt_err_GeV": 0.29, "Mh_GeV": 125.20, "alpha_s": 0.1180}
TOP_MASS_SCAN_GEV = (-1.0, 0.0, 1.0)

# =============================================================================
# model constants
# =============================================================================
H_QUARTIC_ID = "lambda::O36_B02_H_self_quartics"
S_QUARTIC_ID = "lambda::O23_B01_singlet_polynomial"
PORTAL_ID = "lambda::O34_B01_Hdag_H_norm"
CERTIFIED_GUT_COUPLINGS = {"lambda_H": 1.0, "lambda_S": 1.0, "lambda_HS": 0.0}
TRIPLET_BETA = 1.0 / 20.0  # candidate beta; F-branch sqrt(beta) M_I extrapolation (no triplet state built)

LOOP = 1.0 / (16.0 * math.pi**2)
K1, K2, K3, K4 = LOOP, LOOP**2, LOOP**3, LOOP**4
FOUR_PI = 4.0 * math.pi
ZETA3 = 1.2020569031595942

# vacuum-decay estimate
AGE_OF_UNIVERSE_GYR = 13.8
HBAR_GEV_S = 6.582119569e-25
AGE_OF_UNIVERSE_INV_GEV = AGE_OF_UNIVERSE_GYR * 1.0e9 * 365.25 * 86400.0 / HBAR_GEV_S
LITERATURE_ACTION_THRESHOLD = 400.0

# numerics
SM_RTOL, SM_ATOL = 1.0e-12, 1.0e-15
STAGE_RTOL, STAGE_ATOL = 1.0e-11, 1.0e-14
PROFILE_GRID = 20001
STAGE_GRID = 801
EDGE_XTOL = 1.0e-10

# portal scans
LAMBDA_S_WINDOW_SCAN = (0.01, 0.05, 0.1, 0.2, 0.5)
LAMBDA_HS_GRID = (-0.1, 0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6)
LAMBDA_S_RADIAL_SCAN = (1.0e-6, 1.0e-5, 1.0e-4, 1.0e-2)
REPORT_SCALES = (
    ("1e4", 1.0e4),
    ("1e6", 1.0e6),
    ("1e8", 1.0e8),
    ("1e10", 1.0e10),
    ("1e11", 1.0e11),
    ("M_I", M_I_GEV),
    ("1e13", 1.0e13),
    ("1e15", 1.0e15),
    ("M_GUT", M_GUT_GEV),
    ("1e16", 1.0e16),
    ("M_Pl", M_PL_GEV),
)

COUPLINGS = ("gY", "g2", "g3", "yt", "lam")


def buttazzo_inputs(
    Mt: float = MT_REF, Mh: float = MH_REF, alpha_s: float = ALPHA_S_REF, MW: float = MW_REF
) -> dict[str, float]:
    """Published linear dependences of the MSbar couplings at mu = M_t (1307.3536 v3/v4)."""
    dt, das, dw = Mt - MT_REF, (alpha_s - ALPHA_S_REF) / 0.0007, (MW - MW_REF) / 0.014
    return {
        "gY": 0.35830 + 0.00011 * dt - 0.00020 * dw,
        "g2": 0.64779 + 0.00004 * dt + 0.00011 * dw,
        "g3": 1.1666 + 0.00314 * das - 0.00046 * dt,
        "yt": 0.93690 + 0.00556 * dt - 0.00042 * das,
        "lam": 0.12604 + 0.00206 * (Mh - MH_REF) - 0.00004 * dt,
    }


# =============================================================================
# coefficient tables (copied from the workflow consensus solver sm_rge2.py)
# Exponent tuple e = (eY, e2, e3, et, el) stands for
# (gY^2)^eY (g2^2)^e2 (g3^2)^e3 (yt^2)^et lambda^el; K = 1/(16 pi^2):
#     dg_i/dln mu = g_i sum_n K^n P_i^(n),  dyt/dln mu = yt sum_n K^n P_t^(n),
#     dlambda/dln mu = sum_n K^n P_l^(n).
# =============================================================================
_POS = {"gY": 0, "g1": 0, "g2": 1, "g3": 2, "yt": 3}


def _mono(text: str) -> tuple[int, ...]:
    exponents = [0, 0, 0, 0, 0]
    for token in text.split():
        name, _, power = token.partition("^")
        power = int(power) if power else 1
        if name == "lam":
            exponents[4] += power
        else:
            if power % 2:
                raise ValueError(f"odd power in {token!r}")
            exponents[_POS[name]] += power // 2
    return tuple(exponents)


def _poly(terms, native: bool = False, lam_eq: bool = False) -> dict[tuple[int, ...], Any]:
    """native=True: Buttazzo form (GUT-normalised g1, d/dln mu^2): g1^2 -> 5/3 gY^2 and
    x2 for the lambda equation; gauge and Yukawa brackets need no factor."""
    out: dict[tuple[int, ...], Any] = {}
    for coefficient, text in terms:
        names = {token.partition("^")[0] for token in text.split()}
        if native and "gY" in names:
            raise ValueError("native (Buttazzo) monomials must use g1")
        if not native and "g1" in names:
            raise ValueError("gY-form monomials must use gY")
        exponents = _mono(text)
        if native:
            if isinstance(coefficient, (int, F)):
                coefficient = coefficient * F(5, 3) ** exponents[0]
            else:
                coefficient = coefficient * (5.0 / 3.0) ** exponents[0]
            if lam_eq:
                coefficient = coefficient * 2
        out[exponents] = out.get(exponents, 0) + coefficient
    return {key: value for key, value in out.items() if value != 0}


def _fmt(exponents) -> str:
    parts = [f"{n}^{2 * k}" for n, k in zip(("gY", "g2", "g3", "yt"), exponents[:4]) if k]
    if exponents[4]:
        parts.append("lam" if exponents[4] == 1 else f"lam^{exponents[4]}")
    return " ".join(parts) or "1"


# (A) one and two loops, gY / d ln mu form (Machacek-Vaughn with Luo-Wang-Xiao).
A: dict[tuple[str, int], dict] = {}
A["gY", 1] = _poly([(F(41, 6), "gY^2")])
A["g2", 1] = _poly([(F(-19, 6), "g2^2")])
A["g3", 1] = _poly([(F(-7), "g3^2")])
A["yt", 1] = _poly([(F(9, 2), "yt^2"), (F(-8), "g3^2"), (F(-9, 4), "g2^2"), (F(-17, 12), "gY^2")])
A["lam", 1] = _poly([(F(24), "lam^2"), (F(12), "lam yt^2"), (F(-6), "yt^4"), (F(-9), "lam g2^2"),
                     (F(-3), "lam gY^2"), (F(9, 8), "g2^4"), (F(3, 4), "g2^2 gY^2"), (F(3, 8), "gY^4")])
A["gY", 2] = _poly([(F(199, 18), "gY^4"), (F(9, 2), "gY^2 g2^2"), (F(44, 3), "gY^2 g3^2"),
                    (F(-17, 6), "gY^2 yt^2")])
A["g2", 2] = _poly([(F(3, 2), "g2^2 gY^2"), (F(35, 6), "g2^4"), (F(12), "g2^2 g3^2"),
                    (F(-3, 2), "g2^2 yt^2")])
A["g3", 2] = _poly([(F(11, 6), "g3^2 gY^2"), (F(9, 2), "g3^2 g2^2"), (F(-26), "g3^4"),
                    (F(-2), "g3^2 yt^2")])
A["yt", 2] = _poly([
    (F(-12), "yt^4"), (F(131, 16), "yt^2 gY^2"), (F(225, 16), "yt^2 g2^2"), (F(36), "yt^2 g3^2"),
    (F(-12), "yt^2 lam"), (F(6), "lam^2"), (F(1187, 216), "gY^4"), (F(-3, 4), "gY^2 g2^2"),
    (F(19, 9), "gY^2 g3^2"), (F(-23, 4), "g2^4"), (F(9), "g2^2 g3^2"), (F(-108), "g3^4")])
A["lam", 2] = _poly([
    (F(-312), "lam^3"), (F(-144), "lam^2 yt^2"), (F(108), "lam^2 g2^2"), (F(36), "lam^2 gY^2"),
    (F(-3), "lam yt^4"), (F(80), "lam yt^2 g3^2"), (F(45, 2), "lam yt^2 g2^2"),
    (F(85, 6), "lam yt^2 gY^2"), (F(-73, 8), "lam g2^4"), (F(39, 4), "lam g2^2 gY^2"),
    (F(629, 24), "lam gY^4"), (F(30), "yt^6"), (F(-32), "yt^4 g3^2"), (F(-8, 3), "yt^4 gY^2"),
    (F(-9, 4), "yt^2 g2^4"), (F(21, 2), "yt^2 g2^2 gY^2"), (F(-19, 4), "yt^2 gY^4"),
    (F(305, 16), "g2^6"), (F(-289, 48), "g2^4 gY^2"), (F(-559, 48), "g2^2 gY^4"),
    (F(-379, 48), "gY^6")])

# (B) Buttazzo et al. 1307.3536 v3/v4 App. B verbatim (b, tau Yukawas dropped).
B: dict[tuple[str, int], dict] = {}
B["gY", 1] = _poly([(F(41, 10), "g1^2")], native=True)
B["g2", 1] = _poly([(F(-19, 6), "g2^2")], native=True)
B["g3", 1] = _poly([(F(-7), "g3^2")], native=True)
B["yt", 1] = _poly([(F(9, 2), "yt^2"), (F(-8), "g3^2"), (F(-9, 4), "g2^2"), (F(-17, 20), "g1^2")],
                   native=True)
B["lam", 1] = _poly([(F(12), "lam^2"), (F(6), "lam yt^2"), (F(-9, 2), "lam g2^2"),
                     (F(-9, 10), "lam g1^2"), (F(-3), "yt^4"), (F(9, 16), "g2^4"),
                     (F(27, 400), "g1^4"), (F(9, 40), "g2^2 g1^2")], native=True, lam_eq=True)
B["gY", 2] = _poly([(F(44, 5), "g1^2 g3^2"), (F(27, 10), "g1^2 g2^2"), (F(199, 50), "g1^4"),
                    (F(-17, 10), "g1^2 yt^2")], native=True)
B["g2", 2] = _poly([(F(12), "g2^2 g3^2"), (F(35, 6), "g2^4"), (F(9, 10), "g2^2 g1^2"),
                    (F(-3, 2), "g2^2 yt^2")], native=True)
B["g3", 2] = _poly([(F(-26), "g3^4"), (F(9, 2), "g3^2 g2^2"), (F(11, 10), "g3^2 g1^2"),
                    (F(-2), "g3^2 yt^2")], native=True)
B["yt", 2] = _poly([
    (F(-12), "yt^4"), (F(-12), "yt^2 lam"), (F(36), "yt^2 g3^2"), (F(225, 16), "yt^2 g2^2"),
    (F(393, 80), "yt^2 g1^2"), (F(6), "lam^2"), (F(-108), "g3^4"), (F(-23, 4), "g2^4"),
    (F(1187, 600), "g1^4"), (F(9), "g3^2 g2^2"), (F(19, 15), "g3^2 g1^2"), (F(-9, 20), "g2^2 g1^2")],
    native=True)
B["lam", 2] = _poly([
    (F(-156), "lam^3"), (F(-72), "lam^2 yt^2"), (F(54), "lam^2 g2^2"), (F(54, 5), "lam^2 g1^2"),
    (F(-3, 2), "lam yt^4"), (F(40), "lam yt^2 g3^2"), (F(45, 4), "lam yt^2 g2^2"),
    (F(17, 4), "lam yt^2 g1^2"), (F(-73, 16), "lam g2^4"), (F(1887, 400), "lam g1^4"),
    (F(117, 40), "lam g2^2 g1^2"), (F(15), "yt^6"), (F(-16), "yt^4 g3^2"), (F(-4, 5), "yt^4 g1^2"),
    (F(-9, 8), "yt^2 g2^4"), (F(-171, 200), "yt^2 g1^4"), (F(63, 20), "yt^2 g2^2 g1^2"),
    (F(305, 32), "g2^6"), (F(-3411, 4000), "g1^6"), (F(-289, 160), "g2^4 g1^2"),
    (F(-1677, 800), "g2^2 g1^4")], native=True, lam_eq=True)

# Three loops: the numbers printed in Buttazzo App. B (zeta_3 evaluated).
_B3 = {
    "gY": [(F(189, 16), "g1^2 yt^4"), (F(-29, 5), "g1^2 yt^2 g3^2"), (F(-471, 32), "g1^2 yt^2 g2^2"),
           (F(-2827, 800), "g1^4 yt^2"), (F(-9, 5), "g1^2 lam^2"), (F(9, 10), "g1^2 lam g2^2"),
           (F(27, 50), "g1^4 lam"), (F(297, 5), "g1^2 g3^4"), (F(789, 64), "g1^2 g2^4"),
           (F(-388613, 24000), "g1^6"), (F(-3, 5), "g1^2 g3^2 g2^2"), (F(-137, 75), "g1^4 g3^2"),
           (F(123, 160), "g1^4 g2^2")],
    "g2": [(F(147, 16), "g2^2 yt^4"), (F(-7), "g2^2 yt^2 g3^2"), (F(-729, 32), "g2^4 yt^2"),
           (F(-593, 160), "g2^2 yt^2 g1^2"), (F(-3), "g2^2 lam^2"), (F(3, 2), "g2^4 lam"),
           (F(3, 10), "g2^2 lam g1^2"), (F(81), "g2^2 g3^4"), (F(324953, 1728), "g2^6"),
           (F(-5597, 1600), "g2^2 g1^4"), (F(39), "g2^4 g3^2"), (F(-1, 5), "g2^2 g3^2 g1^2"),
           (F(873, 160), "g2^4 g1^2")],
    "g3": [(F(15), "g3^2 yt^4"), (F(-40), "g3^4 yt^2"), (F(-93, 8), "g3^2 yt^2 g2^2"),
           (F(-101, 40), "g3^2 yt^2 g1^2"), (F(65, 2), "g3^6"), (F(109, 8), "g3^2 g2^4"),
           (F(-523, 120), "g3^2 g1^4"), (F(21), "g3^4 g2^2"), (F(77, 15), "g3^4 g1^2"),
           (F(-3, 40), "g3^2 g2^2 g1^2")],
    "yt": [(58.6028, "yt^6"), (198.0, "yt^4 lam"), (-157.0, "yt^4 g3^2"), (-1593 / 16, "yt^4 g2^2"),
           (-2437 / 80, "yt^4 g1^2"), (15 / 4, "lam^2 yt^2"), (16.0, "lam yt^2 g3^2"),
           (-135 / 2, "lam yt^2 g2^2"), (-127 / 10, "lam yt^2 g1^2"), (363.764, "yt^2 g3^4"),
           (16.990, "yt^2 g2^4"), (-24.422, "yt^2 g1^4"), (48.370, "yt^2 g3^2 g2^2"),
           (18.074, "yt^2 g3^2 g1^2"), (34.829, "yt^2 g2^2 g1^2"), (-36.0, "lam^3"),
           (45.0, "lam^2 g2^2"), (9.0, "lam^2 g1^2"), (-171 / 16, "lam g2^4"),
           (-1089 / 400, "lam g1^4"), (117 / 40, "lam g2^2 g1^2"), (-619.35, "g3^6"),
           (169.829, "g2^6"), (16.099, "g1^6"), (73.654, "g3^4 g2^2"), (-15.096, "g3^4 g1^2"),
           (-21.072, "g3^2 g2^4"), (-22.319, "g3^2 g1^4"), (-321 / 20, "g3^2 g2^2 g1^2"),
           (-4.743, "g2^4 g1^2"), (-4.442, "g2^2 g1^4")],
    "lam": [(6011.35, "lam^4"), (873.0, "lam^3 yt^2"), (-387.452, "lam^3 g2^2"),
            (-77.490, "lam^3 g1^2"), (1768.26, "lam^2 yt^4"), (160.77, "lam^2 yt^2 g3^2"),
            (-359.539, "lam^2 yt^2 g2^2"), (-63.869, "lam^2 yt^2 g1^2"), (-790.28, "lam^2 g2^4"),
            (-185.532, "lam^2 g1^4"), (-316.64, "lam^2 g2^2 g1^2"), (-223.382, "lam yt^6"),
            (-662.866, "lam yt^4 g3^2"), (-5.470, "lam yt^4 g2^2"), (-21.015, "lam yt^4 g1^2"),
            (356.968, "lam yt^2 g3^4"), (-319.664, "lam yt^2 g2^4"), (-74.8599, "lam yt^2 g1^4"),
            (15.1443, "lam yt^2 g3^2 g2^2"), (17.454, "lam yt^2 g3^2 g1^2"),
            (5.615, "lam yt^2 g2^2 g1^2"), (-57.144, "lam g2^4 g3^2"), (865.483, "lam g2^6"),
            (79.638, "lam g2^4 g1^2"), (-8.381, "lam g1^4 g3^2"), (61.753, "lam g1^4 g2^2"),
            (28.168, "lam g1^6"), (-243.149, "yt^8"), (250.494, "yt^6 g3^2"),
            (74.138, "yt^6 g2^2"), (33.930, "yt^6 g1^2"), (-50.201, "yt^4 g3^4"),
            (15.884, "yt^4 g2^4"), (15.948, "yt^4 g1^4"), (13.349, "yt^4 g3^2 g2^2"),
            (17.570, "yt^4 g3^2 g1^2"), (-70.356, "yt^4 g2^2 g1^2"), (16.464, "yt^2 g3^2 g2^4"),
            (1.016, "yt^2 g3^2 g1^4"), (11.386, "yt^2 g3^2 g2^2 g1^2"), (62.500, "yt^2 g2^6"),
            (13.041, "yt^2 g2^4 g1^2"), (10.627, "yt^2 g1^4 g2^2"), (11.117, "yt^2 g1^6"),
            (7.536, "g3^2 g2^6"), (0.663, "g3^2 g1^6"), (1.507, "g3^2 g2^4 g1^2"),
            (1.105, "g3^2 g2^2 g1^4"), (-114.091, "g2^8"), (-1.508, "g1^8"),
            (-37.889, "g2^6 g1^2"), (6.500, "g2^4 g1^4"), (-1.543, "g2^2 g1^6")],
}
for _key, _terms in _B3.items():
    B[_key, 3] = _poly(_terms, native=True, lam_eq=(_key == "lam"))


def qcd_beta3(nf: int) -> float:
    """Four-loop QCD coefficient (van Ritbergen-Vermaseren-Larin 1997)."""
    z = ZETA3
    return ((149753 / 6 + 3564 * z) - (1078361 / 162 + 6508 / 27 * z) * nf
            + (50065 / 162 + 6472 / 81 * z) * nf ** 2 + 1093 / 729 * nf ** 3)


# dg3/dln mu = -b3 K^4 g3^9 (n-loop pure QCD is always -b_{n-1} K^n g^(2n+1)).
QCD4 = {(0, 0, 4, 0, 0): -qcd_beta3(6)}


def two_transcriptions_disagreements() -> list[str]:
    bad = []
    for loop in (1, 2):
        for name in COUPLINGS:
            keys = sorted(set(A[name, loop]) | set(B[name, loop]))
            for key in keys:
                if A[name, loop].get(key, 0) != B[name, loop].get(key, 0):
                    bad.append(f"beta_{name} {loop}L {_fmt(key)}")
    return bad


COEFFS = {**{(k, L): A[k, L] for k in COUPLINGS for L in (1, 2)},
          **{(k, 3): B[k, 3] for k in COUPLINGS}}
_TABLES = {key: tuple((float(c), e) for e, c in poly.items()) for key, poly in COEFFS.items()}
_QCD4_TABLE = tuple((float(c), e) for e, c in QCD4.items())


def _table_value(table, X: Sequence[float]) -> tuple[float, float]:
    """(value, sum of |terms|) of a coefficient table at X = (gY^2, g2^2, g3^2, yt^2, lam)."""
    powers = [(1.0, x, x * x, x * x * x, x * x * x * x) for x in X]
    total = magnitude = 0.0
    for coefficient, e in table:
        term = (coefficient * powers[0][e[0]] * powers[1][e[1]] * powers[2][e[2]]
                * powers[3][e[3]] * powers[4][e[4]])
        total += term
        magnitude += abs(term)
    return total, magnitude


def _resolve(loops: int, qcd4) -> tuple[int, bool]:
    if loops not in (1, 2, 3):
        raise ValueError("loops must be 1, 2 or 3")
    return loops, (loops >= 3) if qcd4 is None else bool(qcd4)


# =============================================================================
# SM beta functions: hand-written 1L + 2L (fast), tables for 3L + 4L QCD.
# The hand-written form is checked against the exact tables in the report.
# =============================================================================
def _sm_beta_values(gY: float, g2: float, g3: float, yt: float, lam: float,
                    loops: int, qcd4: bool) -> list[float]:
    a, b, c, t, l = gY * gY, g2 * g2, g3 * g3, yt * yt, lam
    sY = K1 * (41.0 / 6.0 * a)
    s2 = K1 * (-19.0 / 6.0 * b)
    s3 = K1 * (-7.0 * c)
    st = K1 * (4.5 * t - 8.0 * c - 2.25 * b - 17.0 / 12.0 * a)
    sl = K1 * (24.0 * l * l + 12.0 * l * t - 6.0 * t * t - 9.0 * l * b - 3.0 * l * a
               + 9.0 / 8.0 * b * b + 0.75 * a * b + 0.375 * a * a)
    if loops >= 2:
        sY += K2 * a * (199.0 / 18.0 * a + 4.5 * b + 44.0 / 3.0 * c - 17.0 / 6.0 * t)
        s2 += K2 * b * (1.5 * a + 35.0 / 6.0 * b + 12.0 * c - 1.5 * t)
        s3 += K2 * c * (11.0 / 6.0 * a + 4.5 * b - 26.0 * c - 2.0 * t)
        st += K2 * (-12.0 * t * t + t * (131.0 / 16.0 * a + 225.0 / 16.0 * b + 36.0 * c - 12.0 * l)
                    + 6.0 * l * l + 1187.0 / 216.0 * a * a - 0.75 * a * b + 19.0 / 9.0 * a * c
                    - 23.0 / 4.0 * b * b + 9.0 * b * c - 108.0 * c * c)
        sl += K2 * (
            -312.0 * l * l * l
            + l * l * (-144.0 * t + 108.0 * b + 36.0 * a)
            + l * (-3.0 * t * t + 80.0 * c * t + 22.5 * b * t + 85.0 / 6.0 * a * t
                   - 73.0 / 8.0 * b * b + 39.0 / 4.0 * a * b + 629.0 / 24.0 * a * a)
            + 30.0 * t * t * t - 32.0 * c * t * t - 8.0 / 3.0 * a * t * t
            - 2.25 * b * b * t + 10.5 * a * b * t - 4.75 * a * a * t
            + 305.0 / 16.0 * b * b * b - 289.0 / 48.0 * b * b * a - 559.0 / 48.0 * b * a * a
            - 379.0 / 48.0 * a * a * a
        )
    if loops >= 3:
        X = (a, b, c, t, l)
        sY += K3 * _table_value(_TABLES["gY", 3], X)[0]
        s2 += K3 * _table_value(_TABLES["g2", 3], X)[0]
        s3 += K3 * _table_value(_TABLES["g3", 3], X)[0]
        st += K3 * _table_value(_TABLES["yt", 3], X)[0]
        sl += K3 * _table_value(_TABLES["lam", 3], X)[0]
    if qcd4:
        s3 += K4 * _table_value(_QCD4_TABLE, (a, b, c, t, l))[0]
    return [gY * sY, g2 * s2, g3 * s3, yt * st, sl]


def sm_beta(y: Sequence[float], loops: int = 2, qcd4=None) -> list[float]:
    """d/dln mu of (gY, g2, g3, yt, lambda)."""
    loops, qcd4 = _resolve(loops, qcd4)
    return _sm_beta_values(*(float(v) for v in y), loops, qcd4)


def sm_beta_from_tables(y: Sequence[float], loops: int = 2, qcd4=None) -> tuple[list[float], list[float]]:
    """Same as sm_beta but evaluated term by term from the exact tables; also returns magnitudes."""
    loops, qcd4 = _resolve(loops, qcd4)
    gY, g2, g3, yt, lam = (float(v) for v in y)
    X = (gY * gY, g2 * g2, g3 * g3, yt * yt, lam)
    values, magnitudes = [], []
    for name in COUPLINGS:
        total = magnitude = 0.0
        for loop in range(1, loops + 1):
            value, size = _table_value(_TABLES[name, loop], X)
            total += LOOP**loop * value
            magnitude += LOOP**loop * size
        if qcd4 and name == "g3":
            value, size = _table_value(_QCD4_TABLE, X)
            total += K4 * value
            magnitude += K4 * size
        values.append(total)
        magnitudes.append(magnitude)
    prefactor = (gY, g2, g3, yt, 1.0)
    return ([p * v for p, v in zip(prefactor, values)],
            [abs(p) * m for p, m in zip(prefactor, magnitudes)])


def _sm_rhs(loops: int, qcd4: bool) -> Callable:
    def rhs(_t, y):
        return _sm_beta_values(*y.tolist(), loops, qcd4)
    return rhs


# =============================================================================
# SM running
# =============================================================================
def _as_vector(couplings: Mapping[str, float] | Sequence[float]) -> np.ndarray:
    if isinstance(couplings, Mapping):
        values = dict(couplings)
        if "lam" not in values and "lambda" in values:
            values["lam"] = values["lambda"]
        return np.array([float(values[k]) for k in COUPLINGS])
    vector = np.asarray(couplings, dtype=float).ravel()
    if vector.size != 5:
        raise ValueError("expected 5 couplings (gY, g2, g3, yt, lam)")
    return vector


def _solve(rhs, y0, mu0, mu1, rtol, atol, dense=False, events=None):
    solution = solve_ivp(rhs, (math.log(mu0), math.log(mu1)), list(map(float, y0)),
                         method="DOP853", rtol=rtol, atol=atol, dense_output=dense, events=events)
    if solution.status == -1:
        raise ArithmeticError(f"RGE integration failed: {solution.message}")
    return solution


def run_sm(couplings, mu0: float, mu1: float, loops: int = 2, qcd4=None) -> dict[str, float]:
    """Run (gY, g2, g3, yt, lam) from mu0 to mu1 in either direction."""
    loops, qcd4 = _resolve(loops, qcd4)
    y0 = _as_vector(couplings)
    if mu1 == mu0:
        return dict(zip(COUPLINGS, map(float, y0)))
    solution = _solve(_sm_rhs(loops, qcd4), y0, mu0, mu1, SM_RTOL, SM_ATOL)
    return dict(zip(COUPLINGS, map(float, solution.y[:, -1])))


class SMProfile:
    """Dense two-sided solution of the SM RGEs on [mu0, mu_hi]."""

    def __init__(self, couplings, mu0: float, loops: int, qcd4=None, mu_hi: float = M_PL_GEV):
        self.loops, self.qcd4 = _resolve(loops, qcd4)
        self.mu0, self.mu_hi = float(mu0), float(mu_hi)
        self.y0 = _as_vector(couplings)
        self.solution = _solve(_sm_rhs(self.loops, self.qcd4), self.y0, mu0, mu_hi,
                               SM_RTOL, SM_ATOL, dense=True)
        self._t = np.linspace(math.log(mu0), math.log(mu_hi), PROFILE_GRID)
        self._lam = self.solution.sol(self._t)[4]

    def couplings(self, mu: float) -> dict[str, float]:
        if abs(mu - self.mu0) <= 1.0e-12 * self.mu0:
            return dict(zip(COUPLINGS, map(float, self.y0)))
        return dict(zip(COUPLINGS, map(float, self.solution.sol(math.log(mu)))))

    def lam(self, mu: float) -> float:
        return self.couplings(mu)["lam"]

    def instability_scale(self) -> float | None:
        """First scale above mu0 where the MSbar lambda crosses zero (Buttazzo's
        Lambda_lambda, not the Landau-gauge effective-potential zero)."""
        index = np.nonzero((self._lam[:-1] > 0) & (self._lam[1:] <= 0))[0]
        if not index.size:
            return None
        i = int(index[0])
        return math.exp(brentq(lambda t: float(self.solution.sol(t)[4]), self._t[i], self._t[i + 1],
                               xtol=1.0e-13, rtol=1.0e-15))

    def minimum(self, mu_lo: float | None = None, mu_hi: float | None = None) -> tuple[float, float]:
        t_lo = math.log(mu_lo) if mu_lo else self._t[0]
        t_hi = math.log(mu_hi) if mu_hi else self._t[-1]
        mask = (self._t >= t_lo) & (self._t <= t_hi)
        ts = np.concatenate(([t_lo], self._t[mask], [t_hi]))
        lams = self.solution.sol(ts)[4]
        i = int(np.argmin(lams))
        if 0 < i < ts.size - 1:
            result = minimize_scalar(lambda t: float(self.solution.sol(t)[4]),
                                     bounds=(ts[i - 1], ts[i + 1]), method="bounded",
                                     options={"xatol": 1.0e-10})
            return float(result.fun), math.exp(result.x)
        t_end = t_lo if i == 0 else t_hi
        return float(self.solution.sol(t_end)[4]), math.exp(t_end)


@lru_cache(maxsize=None)
def _profile_cached(y0: tuple[float, ...], mu0: float, loops: int, qcd4: bool) -> SMProfile:
    return SMProfile(y0, mu0, loops, qcd4)


def sm_profile(couplings=None, mu0: float = MT_REF, loops: int = 2, qcd4=None) -> SMProfile:
    couplings = BUTTAZZO_INPUTS if couplings is None else couplings
    loops, qcd4 = _resolve(loops, qcd4)
    return _profile_cached(tuple(float(v) for v in _as_vector(couplings)), float(mu0), loops, qcd4)


def sm_summary(profile: SMProfile) -> dict[str, Any]:
    instability = profile.instability_scale()
    lam_min, mu_min = profile.minimum()
    return {
        "mu0_GeV": profile.mu0,
        "loops": profile.loops,
        "four_loop_qcd": profile.qcd4,
        "lambda_at": {name: profile.lam(mu) for name, mu in REPORT_SCALES},
        "instability_scale_GeV": instability,
        "log10_instability_scale": math.log10(instability) if instability else None,
        "lambda_min": lam_min,
        "mu_at_lambda_min_GeV": mu_min,
        "couplings_at_M_I": profile.couplings(M_I_GEV),
        "couplings_at_M_GUT": profile.couplings(M_GUT_GEV),
    }


def lambda_mt_for_target(target: float, mu: float, loops: int = 2,
                         lo: float = 0.02, hi: float = 0.45) -> float:
    """lambda(M_t) that runs to lambda(mu) = target with the other inputs fixed (2L)."""
    loops, qcd4 = _resolve(loops, None)
    rhs = _sm_rhs(loops, qcd4)

    def blowup(_t, y):
        return 50.0 - y[4]
    blowup.terminal = True

    def residual(lam0: float) -> float:
        y0 = dict(BUTTAZZO_INPUTS, lam=lam0)
        solution = _solve(rhs, _as_vector(y0), MT_REF, mu, SM_RTOL, SM_ATOL, events=[blowup])
        if solution.status == 1:
            return 50.0 - target
        return float(solution.y[4, -1]) - target

    return brentq(residual, lo, hi, xtol=1.0e-14, rtol=1.0e-14)


def higgs_mass_estimates(lam_mt: float) -> dict[str, float | None]:
    """Tree-level m_h = sqrt(2 lambda) v (portal-module convention) and the same
    rescaled to the Buttazzo central point (M_h = 125.15 GeV at lambda = 0.12604),
    which keeps the relative NNLO threshold correction fixed (an estimate)."""
    if lam_mt <= 0:
        return {"m_h_tree_GeV": None, "M_h_scaled_to_buttazzo_GeV": None}
    return {
        "m_h_tree_GeV": math.sqrt(2.0 * lam_mt) * V_EW_GEV,
        "M_h_scaled_to_buttazzo_GeV": MH_REF * math.sqrt(lam_mt / BUTTAZZO_INPUTS["lam"]),
    }


# =============================================================================
# SM + complex singlet above the threshold
# =============================================================================
def portal_one_loop(lH: float, lS: float, lHS: float, yt: float, g2: float, gY: float) -> tuple[float, float, float]:
    """(16pi^2) x portal parts: (delta beta_lambdaH, beta_lambdaS, beta_lambdaHS).
    V > lambda_H (H^dag H)^2 + lambda_S |S|^4 + lambda_HS (H^dag H)|S|^2."""
    a, b, t = gY * gY, g2 * g2, yt * yt
    return (
        lHS * lHS,
        20.0 * lS * lS + 2.0 * lHS * lHS,
        lHS * (12.0 * lH + 8.0 * lS + 4.0 * lHS + 6.0 * t - 4.5 * b - 1.5 * a),
    )


def portal_two_loop_partial(lH: float, lS: float, lHS: float, yt: float) -> tuple[float, float]:
    """(16pi^2)^2 x the singlet-only two-loop pieces of beta_lambdaH and beta_yt/yt from
    SMASH 1610.01639 App. A (their -40 lambda_H x^2 - 32 x^3 and 2 x^2 with
    x = lambda_Hsigma = lambda_HS/2).  Used only as a sensitivity estimate."""
    return (-10.0 * lH * lHS * lHS - 4.0 * lHS**3, 0.5 * lHS * lHS)


def _stage_rhs(loops: int, portal_two_loop: bool) -> Callable:
    def rhs(_t, y):
        gY, g2, g3, yt, lH, lS, lHS = y.tolist()
        d = _sm_beta_values(gY, g2, g3, yt, lH, loops, False)
        dH, dS, dHS = portal_one_loop(lH, lS, lHS, yt, g2, gY)
        d[4] += K1 * dH
        if portal_two_loop:
            dH2, dyt2 = portal_two_loop_partial(lH, lS, lHS, yt)
            d[4] += K2 * dH2
            d[3] += K2 * yt * dyt2
        d.append(K1 * dS)
        d.append(K1 * dHS)
        return d
    return rhs


def match_threshold(lam_sm: float, lam_s: float, lam_hs: float) -> float:
    """Tree-level matching lambda_H = lambda_SM + lambda_HS^2/(4 lambda_S)."""
    return lam_sm + lam_hs * lam_hs / (4.0 * lam_s)


def invert_threshold(lam_h: float, lam_s: float, lam_hs: float) -> float:
    return lam_h - lam_hs * lam_hs / (4.0 * lam_s)


def tree_lambda_eff(values: Mapping[str, float]) -> float:
    """Tree-level light-doublet quartic at the tuned point, lambda_H - lambda_HS^2/(4 lambda_S)
    (g3_tuned_target_portal_threshold_v20); at mu_match it equals lambda_SM by the matching."""
    return invert_threshold(values["lambda_H"], values["lambda_S"], values["lambda_HS"])


def tree_local_minimum(values: Mapping[str, float]) -> bool:
    """(H, S)-block tree-level local-minimum condition at the tuned point: lambda_S > 0 and
    lambda_eff >= 0.  Copositivity is weaker (it allows lambda_HS > 2 sqrt(lambda_H lambda_S))."""
    return values["lambda_S"] > 0.0 and tree_lambda_eff(values) >= 0.0


def _copositivity_margin(lH: np.ndarray, lS: np.ndarray, lHS: np.ndarray) -> np.ndarray:
    """min(lambda_H, lambda_S, lambda_HS + 2 sqrt(lambda_H lambda_S)); > 0 iff the quartic
    form lambda_H x^2 + lambda_HS x y + lambda_S y^2 is strictly copositive."""
    cross = lHS + 2.0 * np.sqrt(np.clip(lH, 0.0, None) * np.clip(lS, 0.0, None))
    return np.minimum(np.minimum(lH, lS), cross)


def run_two_stage(sm_at_match: Mapping[str, float], mu_match: float, lam_s: float, lam_hs: float,
                  mu_end: float = M_GUT_GEV, loops: int = 2, portal_two_loop: bool = False,
                  lam_h: float | None = None) -> dict[str, Any]:
    """Run SM + S from mu_match to mu_end starting from the matched couplings."""
    lam_h = match_threshold(sm_at_match["lam"], lam_s, lam_hs) if lam_h is None else lam_h
    y0 = [sm_at_match["gY"], sm_at_match["g2"], sm_at_match["g3"], sm_at_match["yt"],
          lam_h, lam_s, lam_hs]
    start_max = max(abs(lam_h), abs(lam_s), abs(lam_hs))
    if start_max >= FOUR_PI:
        # already nonperturbative at the matching scale; the margin continues
        # t_stop - t_end (event at t0) smoothly to more negative values
        return {
            "mu_match_GeV": mu_match,
            "lambda_H_at_match": lam_h,
            "lambda_S_at_match": lam_s,
            "lambda_HS_at_match": lam_hs,
            "reached_end": False,
            "mu_stop_GeV": mu_match,
            "at_end": dict(zip(("gY", "g2", "g3", "yt", "lambda_H", "lambda_S", "lambda_HS"),
                               map(float, y0))),
            "min_lambda_H": lam_h,
            "mu_at_min_lambda_H_GeV": mu_match,
            "min_lambda_S": lam_s,
            "min_copositivity_margin": float(_copositivity_margin(
                np.array([lam_h]), np.array([lam_s]), np.array([lam_hs]))[0]),
            "max_abs_quartic": start_max,
            "perturbativity_margin": math.log(mu_match / mu_end) - math.log(start_max / FOUR_PI),
            "largest_quartic_at_stop": ("lambda_H", "lambda_S", "lambda_HS")[
                int(np.argmax(np.abs(y0[4:7])))],
            "copositive_to_end": False,
            "perturbative_to_end": False,
            "solution": None,
        }

    def nonperturbative(_t, y):
        return FOUR_PI - max(abs(y[4]), abs(y[5]), abs(y[6]))
    nonperturbative.terminal = True
    nonperturbative.direction = -1

    solution = _solve(_stage_rhs(loops, portal_two_loop), y0, mu_match, mu_end,
                      STAGE_RTOL, STAGE_ATOL, dense=True, events=[nonperturbative])
    t_stop = float(solution.t[-1])
    reached = solution.status == 0
    ts = np.linspace(math.log(mu_match), t_stop, STAGE_GRID)
    Y = solution.sol(ts)
    lH, lS, lHS = Y[4], Y[5], Y[6]
    margin = _copositivity_margin(lH, lS, lHS)
    i = int(np.argmin(lH))
    lam_h_min, mu_h_min = float(lH[i]), math.exp(ts[i])
    if 0 < i < ts.size - 1:
        refined = minimize_scalar(lambda t: float(solution.sol(t)[4]), bounds=(ts[i - 1], ts[i + 1]),
                                  method="bounded", options={"xatol": 1.0e-10})
        lam_h_min, mu_h_min = float(refined.fun), math.exp(refined.x)
    end = solution.y[:, -1]
    max_abs = float(np.max(np.abs(Y[4:7])))
    if reached:
        perturbativity_margin = math.log(FOUR_PI / max(max_abs, 1.0e-300))
    else:
        perturbativity_margin = t_stop - math.log(mu_end)
    binding = ("lambda_H", "lambda_S", "lambda_HS")[int(np.argmax(np.abs(end[4:7])))]
    return {
        "mu_match_GeV": mu_match,
        "lambda_H_at_match": lam_h,
        "lambda_S_at_match": lam_s,
        "lambda_HS_at_match": lam_hs,
        "reached_end": reached,
        "mu_stop_GeV": math.exp(t_stop),
        "at_end": dict(zip(("gY", "g2", "g3", "yt", "lambda_H", "lambda_S", "lambda_HS"),
                           map(float, end))),
        "min_lambda_H": lam_h_min,
        "mu_at_min_lambda_H_GeV": mu_h_min,
        "min_lambda_S": float(np.min(lS)),
        "min_copositivity_margin": float(np.min(margin)),
        "max_abs_quartic": max_abs,
        "perturbativity_margin": perturbativity_margin,
        "largest_quartic_at_stop": binding,
        "copositive_to_end": bool(reached and np.min(margin) > 0.0),
        "perturbative_to_end": bool(reached and max_abs < FOUR_PI),
        "solution": solution,
    }


def _public(stage: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in stage.items() if key != "solution"}


# =============================================================================
# vacuum decay estimate
# =============================================================================
def critical_action(mu: float) -> float:
    """S above which a bounce of size ~1/mu decays slower than once per past light
    cone: p ~ (mu T_U)^4 exp(-S) < 1."""
    return 4.0 * math.log(mu * AGE_OF_UNIVERSE_INV_GEV)


def tunnelling_estimate(profile: SMProfile, mu_lo: float | None, mu_hi: float) -> dict[str, Any]:
    """Tree-level Fubini bounce S = 8 pi^2/(3 |lambda(mu)|) scanned over [mu_lo, mu_hi].
    An order-of-magnitude estimate: no quantum/gravity corrections, no prefactor."""
    if mu_lo is None or mu_lo >= mu_hi:
        return {"negative_lambda_window": False, "lifetime_exceeds_age_of_universe": True}
    ts = np.linspace(math.log(mu_lo), math.log(mu_hi), STAGE_GRID)
    lams = profile.solution.sol(ts)[4]
    negative = lams < 0
    if not np.any(negative):
        return {"negative_lambda_window": False, "lifetime_exceeds_age_of_universe": True}
    actions = np.full_like(lams, np.inf)
    actions[negative] = 8.0 * math.pi**2 / (3.0 * np.abs(lams[negative]))
    crit = np.array([critical_action(math.exp(t)) for t in ts])
    log10p = (crit - actions) / math.log(10.0)
    lam_min, mu_min = profile.minimum(mu_lo, mu_hi)
    s_min = 8.0 * math.pi**2 / (3.0 * abs(lam_min))
    return {
        "negative_lambda_window": True,
        "window_GeV": [mu_lo, mu_hi],
        "lambda_min_in_window": lam_min,
        "mu_at_lambda_min_GeV": mu_min,
        "bounce_action_at_lambda_min": s_min,
        "critical_action_at_lambda_min": critical_action(mu_min),
        "literature_action_threshold": LITERATURE_ACTION_THRESHOLD,
        "action_exceeds_literature_threshold": s_min > LITERATURE_ACTION_THRESHOLD,
        "max_log10_decay_probability_in_past_light_cone": float(np.max(log10p)),
        "lifetime_exceeds_age_of_universe": bool(np.max(log10p) < 0.0),
        "formula": "S = 8 pi^2/(3|lambda(mu)|); p ~ (mu T_U)^4 exp(-S); T_U = 13.8 Gyr",
        "is_estimate": True,
    }


# =============================================================================
# (a) SM running and top-mass sensitivity
# =============================================================================
def sm_running_audit() -> dict[str, Any]:
    runs = {
        "1L": sm_summary(sm_profile(loops=1)),
        "1L_superseded_5f25846_mu0_173.10": sm_summary(sm_profile(mu0=SUPERSEDED_5F25846_MU0, loops=1)),
        "2L": sm_summary(sm_profile(loops=2)),
        "3L+4QCD": sm_summary(sm_profile(loops=3)),
    }
    mt_rows: dict[str, Any] = {}
    for label, loops in (("2L", 2), ("3L+4QCD", 3)):
        rows = {}
        for shift in TOP_MASS_SCAN_GEV:
            mt = MT_REF + shift
            profile = sm_profile(buttazzo_inputs(Mt=mt), mt, loops)
            instability = profile.instability_scale()
            lam_min, mu_min = profile.minimum()
            rows[f"{shift:+.0f}"] = {
                "Mt_GeV": mt,
                "instability_scale_GeV": instability,
                "log10_instability_scale": math.log10(instability) if instability else None,
                "lambda_M_I": profile.lam(M_I_GEV),
                "lambda_M_GUT": profile.lam(M_GUT_GEV),
                "lambda_M_Pl": profile.lam(M_PL_GEV),
                "lambda_min": lam_min,
                "mu_at_lambda_min_GeV": mu_min,
            }
        rows["dlambda_M_Pl_dMt_per_GeV"] = (rows["+1"]["lambda_M_Pl"] - rows["-1"]["lambda_M_Pl"]) / 2.0
        rows["dlog10_instability_scale_dMt_per_GeV"] = (
            rows["+1"]["log10_instability_scale"] - rows["-1"]["log10_instability_scale"]
        ) / 2.0
        mt_rows[label] = rows
    planck = sm_profile(loops=3).couplings(M_PL_GEV)
    return {
        "scheme": "MSbar, top Yukawa only, no thresholds above M_t; mu0 = M_t",
        "inputs": {
            "couplings_at_mu0": BUTTAZZO_INPUTS,
            "mu0_GeV": MT_REF,
            "M_t_GeV": MT_REF,
            "M_h_GeV": MH_REF,
            "alpha_s_MZ": ALPHA_S_REF,
            "M_W_GeV": MW_REF,
            "source": "Buttazzo et al. arXiv:1307.3536 v3/v4 (JHEP 1312 (2013) 089), NNLO MSbar at mu = M_t",
            "attribution_note": (
                "These central values belong to M_t = 173.34 GeV, not 173.10 GeV (v2 of the paper). "
                "The superseded one-loop portal module of commit 5f25846 started them at 173.10; "
                "the shift in lambda(M_I) is 2e-6."
            ),
            "linear_dependences": {
                "lambda": "0.12604 + 0.00206 (M_h - 125.15) - 0.00004 (M_t - 173.34)",
                "yt": "0.93690 + 0.00556 (M_t - 173.34) - 0.00042 (alpha_s - 0.1184)/0.0007",
                "g3": "1.1666 + 0.00314 (alpha_s - 0.1184)/0.0007 - 0.00046 (M_t - 173.34)",
                "g2": "0.64779 + 0.00004 (M_t - 173.34) + 0.00011 (M_W - 80.384)/0.014",
                "gY": "0.35830 + 0.00011 (M_t - 173.34) - 0.00020 (M_W - 80.384)/0.014",
                "theory_errors": BUTTAZZO_THEORY_ERRORS,
            },
        },
        "runs": runs,
        "top_mass_sensitivity": mt_rows,
        "three_loop_planck_couplings": {
            "g1": math.sqrt(5.0 / 3.0) * planck["gY"],
            "g2": planck["g2"],
            "g3": planck["g3"],
            "yt": planck["yt"],
            "lambda": planck["lam"],
            "published": BUTTAZZO_PUBLISHED,
        },
        "instability_scale_definition": (
            "first zero of the MSbar lambda(mu) (Buttazzo's Lambda_lambda ~ 2 Lambda_V); the "
            "Landau-gauge effective-potential zero Lambda_I ~ 13 Lambda_V is ~6.5x higher"
        ),
    }


# =============================================================================
# (d) top-mass bound and metastability
# =============================================================================
def critical_top_mass(mu: float = M_I_GEV, loops: int = 2, Mh: float = MH_REF,
                      alpha_s: float = ALPHA_S_REF, shift: Mapping[str, float] | None = None,
                      bracket: tuple[float, float] = (166.0, 175.0)) -> float:
    """M_t at which the MSbar lambda_SM(mu) = 0 (i.e. Lambda_I = mu)."""
    shift = dict(shift or {})

    def residual(mt: float) -> float:
        couplings = buttazzo_inputs(Mt=mt, Mh=Mh, alpha_s=alpha_s)
        for key, value in shift.items():
            couplings[key] += value
        return run_sm(couplings, mt, mu, loops=loops)["lam"]

    return brentq(residual, *bracket, xtol=1.0e-9, rtol=1.0e-12)


def pdg2024_central_run() -> dict[str, Any]:
    """SM running at the PDG 2024 central M_t, M_h, alpha_s through the Buttazzo fits."""
    mt = PDG2024["Mt_GeV"]
    couplings = buttazzo_inputs(Mt=mt, Mh=PDG2024["Mh_GeV"], alpha_s=PDG2024["alpha_s"])
    rows = {}
    for label, loops in (("2L", 2), ("3L+4QCD", 3)):
        profile = sm_profile(couplings, mt, loops)
        instability = profile.instability_scale()
        rows[label] = {
            "msbar_instability_scale_GeV": instability,
            "landau_veff_zero_estimate_GeV": LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO * instability,
            "lambda_M_I": profile.lam(M_I_GEV),
            "lambda_M_GUT": profile.lam(M_GUT_GEV),
            "instability_below_M_I_msbar": instability < M_I_GEV,
            "instability_below_M_I_landau_veff_estimate": LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO * instability < M_I_GEV,
            "decay_estimate": tunnelling_estimate(profile, instability, M_I_GEV),
        }
    return {"inputs": {"Mt_GeV": mt, "Mh_GeV": PDG2024["Mh_GeV"], "alpha_s": PDG2024["alpha_s"],
                       "couplings_at_mt": couplings}, "runs": rows}


def top_mass_bound_audit() -> dict[str, Any]:
    reference = {"2L": critical_top_mass(loops=2), "3L+4QCD": critical_top_mass(loops=3)}
    pdg_like = {
        "2L": critical_top_mass(loops=2, Mh=PDG2024["Mh_GeV"], alpha_s=PDG2024["alpha_s"]),
        "3L+4QCD": critical_top_mass(loops=3, Mh=PDG2024["Mh_GeV"], alpha_s=PDG2024["alpha_s"]),
    }
    mu_veff = M_I_GEV / LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO
    veff = {
        "2L": critical_top_mass(mu=mu_veff, loops=2),
        "3L+4QCD": critical_top_mass(mu=mu_veff, loops=3),
        "2L_PDG2024_Mh_alpha_s": critical_top_mass(
            mu=mu_veff, loops=2, Mh=PDG2024["Mh_GeV"], alpha_s=PDG2024["alpha_s"]),
        "3L+4QCD_PDG2024_Mh_alpha_s": critical_top_mass(
            mu=mu_veff, loops=3, Mh=PDG2024["Mh_GeV"], alpha_s=PDG2024["alpha_s"]),
    }
    shifts = {}
    for key, error in BUTTAZZO_THEORY_ERRORS.items():
        up = critical_top_mass(loops=2, shift={key: +error})
        down = critical_top_mass(loops=2, shift={key: -error})
        shifts[key] = abs(up - down) / 2.0
    theory = math.sqrt(sum(value * value for value in shifts.values()))
    total_error = math.hypot(PDG2024["Mt_err_GeV"], theory)
    at_bound = sm_profile(buttazzo_inputs(Mt=reference["2L"]), reference["2L"], 2)
    gut_zero = {
        "2L": critical_top_mass(mu=M_GUT_GEV, loops=2),
        "3L+4QCD": critical_top_mass(mu=M_GUT_GEV, loops=3),
    }
    return {
        "definition": "largest M_t with lambda_SM(mu) > 0 for all mu < M_I, i.e. Lambda_I >= M_I",
        "Mt_max_absolute_stability_threshold_at_M_I_GeV": reference,
        "Mt_max_with_PDG2024_Mh_and_alpha_s_GeV": pdg_like,
        "Mt_max_landau_veff_zero_definition_estimate_GeV": veff,
        "landau_veff_definition_note": (
            "Same bound with the Landau-gauge effective-potential zero, estimated as "
            f"{LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO} x the MSbar zero (Buttazzo et al.: Lambda_lambda ~ 2 Lambda_V, "
            "Lambda_I ~ 13 Lambda_V), i.e. lambda_SM(M_I/6.5) = 0. The spread between the two definitions "
            "is a theory systematic of the RG-improved criterion."
        ),
        "theory_error_GeV_from_matching": {"per_input": shifts, "combined": theory},
        "instability_scale_at_bound_GeV": at_bound.instability_scale(),
        "measured_top_mass": {
            "Mt_GeV": PDG2024["Mt_GeV"],
            "error_GeV": PDG2024["Mt_err_GeV"],
            "source": "PDG 2024 average of direct measurements (MC-mass interpretation ambiguity ~0.5 GeV not included)",
        },
        "measured_minus_bound_in_sigma_3L_PDG_like": (PDG2024["Mt_GeV"] - pdg_like["3L+4QCD"]) / total_error,
        "measured_minus_bound_in_sigma_2L_PDG_like": (PDG2024["Mt_GeV"] - pdg_like["2L"]) / total_error,
        "measured_minus_bound_in_sigma_3L_PDG_like_landau_veff_estimate": (
            PDG2024["Mt_GeV"] - veff["3L+4QCD_PDG2024_Mh_alpha_s"]) / total_error,
        "Mt_max_for_lambda_SM_M_GUT_nonnegative_GeV": gut_zero,
        "pdg2024_central": pdg2024_central_run(),
    }


# =============================================================================
# (b, c) two-stage portal analysis
# =============================================================================
def classify(profile: SMProfile, stage: dict[str, Any]) -> dict[str, Any]:
    mu_match = stage["mu_match_GeV"]
    instability = profile.instability_scale()
    sm_segment_stable = instability is None or instability > mu_match
    decay = tunnelling_estimate(profile, instability, mu_match)
    if not stage["perturbative_to_end"]:
        label = "NONPERTURBATIVE_BELOW_M_GUT"
    elif not stage["copositive_to_end"]:
        label = "QUARTIC_NOT_COPOSITIVE_ABOVE_THRESHOLD"
    elif sm_segment_stable:
        label = "ABSOLUTELY_STABLE_TO_M_GUT"
    elif decay["lifetime_exceeds_age_of_universe"]:
        label = "METASTABLE_LONG_LIVED_ESTIMATE"
    else:
        label = "UNSTABLE_ESTIMATE"
    return {
        "class": label,
        "sm_segment_stable": sm_segment_stable,
        "copositive_above_threshold": stage["copositive_to_end"],
        "perturbative_to_M_GUT": stage["perturbative_to_end"],
        "lifetime_exceeds_age_estimate": decay["lifetime_exceeds_age_of_universe"],
    }


def portal_window(profile: SMProfile, lam_s: float, mu_match: float,
                  portal_two_loop: bool = False) -> dict[str, Any]:
    """lambda_HS(mu_match) range with lambda_H > 0 (copositive) and |lambda| < 4 pi to M_GUT."""
    sm = profile.couplings(mu_match)

    def run(lam_hs: float) -> dict[str, Any]:
        return run_two_stage(sm, mu_match, lam_s, lam_hs, portal_two_loop=portal_two_loop)

    def lower(lam_hs: float) -> float:
        return run(lam_hs)["min_lambda_H"]

    def upper(lam_hs: float) -> float:
        return run(lam_hs)["perturbativity_margin"]

    start = 2.0 * math.sqrt(lam_s * max(-sm["lam"], 0.0))
    if lower(start) >= 0.0:
        edge_lo = start
    else:
        hi = max(2.0 * start, 1.0e-3)
        for _ in range(60):
            if lower(hi) > 0.0 or upper(hi) < 0.0:
                break
            hi *= 1.5
        if lower(hi) <= 0.0:
            return {"lambda_S": lam_s, "window_exists": False, "mu_match_GeV": mu_match}
        edge_lo = brentq(lower, start, hi, xtol=EDGE_XTOL, rtol=1.0e-12)
    if upper(edge_lo) <= 0.0:
        return {"lambda_S": lam_s, "window_exists": False, "mu_match_GeV": mu_match}
    hi = 2.0 * edge_lo
    for _ in range(80):
        if upper(hi) < 0.0:
            break
        hi *= 1.5
    edge_hi = brentq(upper, edge_lo, hi, xtol=EDGE_XTOL, rtol=1.0e-12)
    middle = math.sqrt(edge_lo * edge_hi)
    lo_run, mid_run, hi_run = run(edge_lo * (1.0 + 1.0e-6)), run(middle), run(edge_hi * (1.0 - 1.0e-6))
    gut = {label: {k: stage["at_end"][k] for k in ("lambda_H", "lambda_S", "lambda_HS")}
           for label, stage in (("lower", lo_run), ("middle", mid_run), ("upper", hi_run))}
    return {
        "lambda_S": lam_s,
        "mu_match_GeV": mu_match,
        "window_exists": True,
        "lambda_HS_min": edge_lo,
        "lambda_HS_max": edge_hi,
        "delta_min": edge_lo**2 / (4.0 * lam_s),
        "delta_max": edge_hi**2 / (4.0 * lam_s),
        "lambda_H_at_match_min": match_threshold(sm["lam"], lam_s, edge_lo),
        "gut_values_at_lower_edge": gut["lower"],
        "gut_values_at_geometric_middle": gut["middle"],
        "gut_values_just_below_upper_edge": gut["upper"],
        # tree level: lambda_eff(mu_match) = lambda_SM(mu_match) for every lambda_HS in the window
        "tree_level_lambda_eff_at_match": sm["lam"],
        "tree_level_lambda_eff_at_gut_values": {label: tree_lambda_eff(v) for label, v in gut.items()},
        "tree_level_local_minimum_at_gut_values": {label: tree_local_minimum(v) for label, v in gut.items()},
        "upper_edge_binding_coupling": run(edge_hi * (1.0 + 1.0e-4))["largest_quartic_at_stop"],
        "interior_points_copositive_and_perturbative": bool(
            mid_run["copositive_to_end"] and mid_run["perturbative_to_end"]
            and lo_run["copositive_to_end"] and hi_run["perturbative_to_end"]
        ),
        "middle_classification": classify(profile, mid_run)["class"],
    }


def benchmark_compatible_portal(profile: SMProfile) -> dict[str, Any]:
    """Keep the certified O36 = O23 = 1 at M_GUT; solve for (lambda_S, lambda_HS)(M_I) and
    hence O34 = lambda_HS(M_GUT) that reproduces the SM lambda at M_I."""
    sm = profile.couplings(M_I_GEV)

    def residual(x: np.ndarray) -> list[float]:
        stage = run_two_stage(sm, M_I_GEV, float(x[0]), float(x[1]))
        if not stage["reached_end"]:
            return [10.0, 10.0]
        end = stage["at_end"]
        return [end["lambda_H"] - CERTIFIED_GUT_COUPLINGS["lambda_H"],
                end["lambda_S"] - CERTIFIED_GUT_COUPLINGS["lambda_S"]]

    solution = root(residual, x0=[0.45, 0.86], method="hybr", options={"xtol": 1.0e-13})
    lam_s, lam_hs = map(float, solution.x)
    stage = run_two_stage(sm, M_I_GEV, lam_s, lam_hs)
    gut = {k: stage["at_end"][k] for k in ("lambda_H", "lambda_S", "lambda_HS")}
    at_mi = {"lambda_H": stage["lambda_H_at_match"], "lambda_S": lam_s, "lambda_HS": lam_hs}
    return {
        "converged": bool(solution.success and max(map(abs, residual(solution.x))) < 1.0e-9),
        "max_residual": float(max(map(abs, residual(solution.x)))),
        "lambda_S_M_I": lam_s,
        "lambda_HS_M_I": lam_hs,
        "lambda_H_M_I": stage["lambda_H_at_match"],
        "delta_M_I": lam_hs**2 / (4.0 * lam_s),
        "radial_mode_mass_over_M_I": 2.0 * math.sqrt(lam_s),
        "gut_values": gut,
        "required_O34_at_M_GUT": stage["at_end"]["lambda_HS"],
        "tree_level_lambda_eff_at_M_I": tree_lambda_eff(at_mi),
        "tree_level_local_minimum_at_M_I": tree_local_minimum(at_mi),
        "tree_level_lambda_eff_at_gut_values": tree_lambda_eff(gut),
        "tree_level_local_minimum_at_gut_values": tree_local_minimum(gut),
        "stage": _public(stage),
        "classification": classify(profile, stage),
    }


def certified_benchmark_prediction() -> dict[str, Any]:
    """(lambda_H, lambda_S, lambda_HS)(M_GUT) = (1, 1, 0): lambda_HS = 0 is RG-invariant, S
    decouples, and lambda_H runs as the SM lambda from M_GUT."""
    lam_mt = lambda_mt_for_target(CERTIFIED_GUT_COUPLINGS["lambda_H"], M_GUT_GEV)
    profile = sm_profile(dict(BUTTAZZO_INPUTS, lam=lam_mt))
    return {
        "lambda_at_mt": lam_mt,
        **higgs_mass_estimates(lam_mt),
        "lambda_H_M_I": profile.lam(M_I_GEV),
        "lambda_H_M_GUT": profile.lam(M_GUT_GEV),
        "reproduces_observed_higgs_mass": abs(lam_mt - BUTTAZZO_INPUTS["lam"]) < 0.005,
    }


def portal_analysis() -> dict[str, Any]:
    profile = sm_profile(loops=2)
    sm_mi = profile.couplings(M_I_GEV)
    instability = profile.instability_scale()
    grid = []
    for lam_s in LAMBDA_S_WINDOW_SCAN:
        for lam_hs in LAMBDA_HS_GRID:
            stage = run_two_stage(sm_mi, M_I_GEV, lam_s, lam_hs)
            gut = {k: stage["at_end"][k] for k in ("lambda_H", "lambda_S", "lambda_HS")}
            row = {
                "lambda_S_M_I": lam_s,
                "lambda_HS_M_I": lam_hs,
                "lambda_H_M_I": stage["lambda_H_at_match"],
                "threshold_round_trip_residual": abs(
                    invert_threshold(stage["lambda_H_at_match"], lam_s, lam_hs) - sm_mi["lam"]
                ),
                "min_lambda_H_to_M_GUT": stage["min_lambda_H"],
                "min_copositivity_margin": stage["min_copositivity_margin"],
                "max_abs_quartic": stage["max_abs_quartic"],
                "reached_M_GUT": stage["reached_end"],
                "mu_stop_GeV": stage["mu_stop_GeV"],
                "gut_values": gut,
                # None when the run stops (|lambda| = 4 pi) below M_GUT
                "tree_level_lambda_eff_at_gut_values": tree_lambda_eff(gut) if stage["reached_end"] else None,
                "tree_level_local_minimum_at_gut_values": tree_local_minimum(gut) if stage["reached_end"] else None,
            }
            row.update(classify(profile, stage))
            grid.append(row)
    windows = [portal_window(profile, lam_s, M_I_GEV) for lam_s in LAMBDA_S_WINDOW_SCAN]
    sensitivity = []
    for window in windows:
        if not window["window_exists"]:
            continue
        two = portal_window(profile, window["lambda_S"], M_I_GEV, portal_two_loop=True)
        sensitivity.append({
            "lambda_S": window["lambda_S"],
            "lambda_HS_min_one_loop_portal": window["lambda_HS_min"],
            "lambda_HS_min_with_partial_two_loop_portal": two.get("lambda_HS_min"),
            "relative_shift": (two["lambda_HS_min"] - window["lambda_HS_min"]) / window["lambda_HS_min"]
            if two.get("window_exists") else None,
        })
    negative = [row for row in grid if row["lambda_HS_M_I"] < 0]
    fix = benchmark_compatible_portal(profile)
    benchmark = certified_benchmark_prediction()
    requirements = {
        "certified_benchmark_110": (
            "lambda_HS = 0 is RG-invariant, so S decouples and lambda_H(M_GUT) = 1 predicts "
            f"m_h(tree) = {benchmark['m_h_tree_GeV']:.1f} GeV: excluded by the Higgs mass"
        ),
        "nonzero_O34_required": (
            "with O34 = 0 the Higgs mass forces lambda_H(M_GUT) = lambda_SM(M_GUT) < 0, which is not copositive"
        ),
        "lambda_S_M_I_scan": [
            {
                "lambda_S_M_I": window["lambda_S"],
                "O36_lambda_H_M_GUT_range": [window["gut_values_at_lower_edge"]["lambda_H"],
                                             window["gut_values_just_below_upper_edge"]["lambda_H"]],
                "O23_lambda_S_M_GUT_range": [window["gut_values_at_lower_edge"]["lambda_S"],
                                             window["gut_values_just_below_upper_edge"]["lambda_S"]],
                "O34_lambda_HS_M_GUT_range": [window["gut_values_at_lower_edge"]["lambda_HS"],
                                              window["gut_values_just_below_upper_edge"]["lambda_HS"]],
                "geometric_middle": window["gut_values_at_geometric_middle"],
            }
            for window in windows if window["window_exists"]
        ],
        "O36_eq_O23_eq_1_needs_O34": fix["required_O34_at_M_GUT"],
        "comparison": (
            "Every window point needs O34 != 0. O36 = 1 needs a large portal: O34 ~ 2.07 at O23 = 1, "
            "close to the upper (perturbativity) edge and above 2 sqrt(O36 O23) = 2, so that point is a "
            "tree-level saddle. The window middles have O36 ~ 0.1."
        ),
    }
    radial = []
    for lam_s in LAMBDA_S_RADIAL_SCAN:
        m_rho = 2.0 * math.sqrt(lam_s) * M_I_GEV
        window = portal_window(profile, lam_s, m_rho)
        radial.append({
            "lambda_S": lam_s,
            "radial_mode_mass_GeV": m_rho,
            "radial_mode_below_instability_scale": instability is not None and m_rho < instability,
            "lambda_SM_at_radial_mode_mass": profile.lam(m_rho),
            "window": window,
            "decay_estimate_if_threshold_above_Lambda_I": tunnelling_estimate(profile, instability, m_rho),
        })
    return {
        "matching": {
            "scale_GeV": M_I_GEV,
            "formula": "lambda_H(M_I) = lambda_SM(M_I) + lambda_HS^2/(4 lambda_S)",
            "sm_couplings_at_M_I_2L": sm_mi,
            "instability_scale_2L_GeV": instability,
            "M_I_over_instability_scale": M_I_GEV / instability if instability else None,
            "tree_level_lambda_eff_at_M_I_every_solution": sm_mi["lam"],
            "tree_level_lambda_eff_note": (
                "the matching makes lambda_H - lambda_HS^2/(4 lambda_S) at M_I equal lambda_SM(M_I) for every "
                "(lambda_S, lambda_HS), so the M_I-matched tuned point is a tree-level saddle whenever "
                "lambda_SM(M_I) < 0"
            ),
        },
        "beta_functions": {
            "normalization": "V > lambda_H (H^dag H)^2 + lambda_S |S|^4 + lambda_HS (H^dag H)|S|^2, S complex",
            "16pi2_beta_lambda_H": "SM 1L+2L (lambda -> lambda_H) + lambda_HS^2",
            "16pi2_beta_lambda_S": "20 lambda_S^2 + 2 lambda_HS^2",
            "16pi2_beta_lambda_HS": "lambda_HS (12 lambda_H + 8 lambda_S + 4 lambda_HS + 6 yt^2 - 9/2 g2^2 - 3/2 gY^2)",
            "literature_map": (
                "Elias-Miro et al. 1203.0237 eq. (RG) and SMASH 1610.01639 App. A write "
                "2 lambda_Hsigma (H^dag H)|S|^2: lambda_HS = 2 lambda_Hsigma, delta = lambda_Hsigma^2/lambda_sigma "
                "= lambda_HS^2/(4 lambda_S)"
            ),
            "two_loop_portal_terms": "omitted in the baseline; singlet-only SMASH pieces used for a sensitivity estimate",
        },
        "stability_conditions": {
            "below_threshold": "lambda_SM(mu) > 0 for M_t < mu < mu_match",
            "above_threshold": "lambda_H > 0, lambda_S > 0, lambda_HS > -2 sqrt(lambda_H lambda_S) up to M_GUT",
            "perturbativity": "|lambda_H|, |lambda_S|, |lambda_HS| < 4 pi up to M_GUT",
            "tree_level_global_minimum_at_threshold": (
                "with <S> != 0 and lambda_HS > 0, V = lambda_H x^2 + lambda_HS x y + lambda_S y^2 "
                "(x = |H|^2, y = |S|^2 - w >= -w) has its global minimum at the EW/S vacuum iff "
                "4 lambda_H lambda_S >= lambda_HS^2, i.e. lambda_SM(mu_match) >= 0; otherwise S = 0, "
                "|H|^2 = lambda_HS w/(2 lambda_H) has V = w^2 lambda_S lambda_SM/lambda_H < 0"
            ),
            "tree_level_local_minimum_at_tuned_point": (
                "lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S) >= 0 with lambda_S > 0 "
                "(g3_tuned_target_portal_threshold_v20). Copositivity is weaker: the single-stage point "
                "(1, 1, 2.015) is copositive with lambda_eff < 0. The copositivity and perturbativity "
                "conditions above are RG-improved statements"
            ),
            "reference": "Elias-Miro et al. 1203.0237 sec. 2 (mechanism needs M_S < Lambda_I); SMASH 1610.01639 sec. 6",
        },
        "classification_grid": grid,
        "windows_lambda_H_positive_to_M_GUT": windows,
        "two_loop_portal_sensitivity": sensitivity,
        "negative_portal_always_fails_at_M_I": all(
            not row["copositive_above_threshold"] for row in negative
        ),
        "certified_benchmark_110": benchmark,
        "benchmark_O36_O23_kept_solve_O34": fix,
        "gut_coefficient_requirements": requirements,
        "radial_mode_threshold": {
            "radial_mode_mass": "m_rho = sqrt(2 lambda_S) w = 2 sqrt(lambda_S) M_I for |<S>| = M_I (S = (x+iy)/sqrt(2))",
            "lambda_S_max_for_m_rho_below_Lambda_I_2L": (instability / (2.0 * M_I_GEV)) ** 2 if instability else None,
            "scan": radial,
        },
    }


# =============================================================================
# (e) single-stage GUT matching (portal module; the 1L mu0 = 173.10 row
#     reproduces the superseded commit-5f25846 value)
# =============================================================================
def gut_single_stage_audit() -> dict[str, Any]:
    required = {
        "1L_mu0_173.10": sm_profile(mu0=SUPERSEDED_5F25846_MU0, loops=1).lam(M_GUT_GEV),
        "1L": sm_profile(loops=1).lam(M_GUT_GEV),
        "2L": sm_profile(loops=2).lam(M_GUT_GEV),
        "3L+4QCD": sm_profile(loops=3).lam(M_GUT_GEV),
    }
    required_at_1e16 = {
        "1L_mu0_173.10": sm_profile(mu0=SUPERSEDED_5F25846_MU0, loops=1).lam(SUPERSEDED_5F25846_M_GUT_GEV),
        "2L": sm_profile(loops=2).lam(SUPERSEDED_5F25846_M_GUT_GEV),
    }
    lam_mt_zero = lambda_mt_for_target(0.0, M_GUT_GEV)
    profile = sm_profile(loops=2)
    instability = profile.instability_scale()
    def needed(value: float) -> float:
        return 2.0 * math.sqrt(CERTIFIED_GUT_COUPLINGS["lambda_S"] * (CERTIFIED_GUT_COUPLINGS["lambda_H"] - value))

    portal_needed = {key: needed(value) for key, value in required.items()}
    portal_needed_1e16 = {key: needed(value) for key, value in required_at_1e16.items()}
    lam_h1, lam_s1 = CERTIFIED_GUT_COUPLINGS["lambda_H"], CERTIFIED_GUT_COUPLINGS["lambda_S"]
    copositive = {
        key: bool(_copositivity_margin(np.array([lam_h1]), np.array([lam_s1]), np.array([value]))[0] > 0.0)
        for key, value in portal_needed.items()
    }
    return {
        "statement": (
            "At the tuned GUT point the light doublet is exactly massless, so V = lambda_eff |h|^4 "
            "along it; a tree-level local minimum needs lambda_eff(M_GUT) > 0. SM running to M_GUT "
            "with m_h = 125.15 GeV requires lambda_eff(M_GUT) < 0 at every loop order."
        ),
        "lambda_eff_required_at_M_GUT": required,
        "lambda_eff_required_at_1e16_GeV": required_at_1e16,
        "tuned_point_is_tree_level_local_minimum": {key: value > 0 for key, value in required.items()},
        "lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1": portal_needed,
        "lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1_at_1e16_GeV": portal_needed_1e16,
        # copositive (lambda_HS > 0) yet lambda_eff < 0: copositivity is not the tree-level condition
        "single_stage_point_copositive_at_lambda_H_eq_lambda_S_eq_1": copositive,
        "lambda_eff_zero_prediction": {"lambda_at_mt": lam_mt_zero, **higgs_mass_estimates(lam_mt_zero)},
        "decay_estimate_window_Lambda_I_to_M_GUT_2L": tunnelling_estimate(profile, instability, M_GUT_GEV),
    }


# =============================================================================
# internal consistency checks
# =============================================================================
def _random_points(count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    low = np.array([0.30, 0.45, 0.45, 0.35, -0.05])
    high = np.array([0.50, 0.70, 1.25, 1.00, 0.30])
    return low + (high - low) * rng.random((count, 5))


def fast_beta_table_deviation() -> float:
    worst = 0.0
    for point in _random_points(200, 20260924):
        for loops in (1, 2, 3):
            fast = sm_beta(point, loops=loops)
            table, magnitude = sm_beta_from_tables(point, loops=loops)
            for f, t, m in zip(fast, table, magnitude):
                worst = max(worst, abs(f - t) / max(m, 1.0e-300))
    return worst


def pure_qcd_deviation() -> float:
    nf = 6
    b = [11 - 2 * nf / 3, 102 - 38 * nf / 3, 2857 / 2 - 5033 * nf / 18 + 325 * nf**2 / 54, qcd_beta3(nf)]
    worst = 0.0
    for g in (0.6, 1.2):
        got = sm_beta([0.0, 0.0, g, 0.0, 0.0], loops=3, qcd4=True)[2]
        want = -sum(coefficient * LOOP ** (n + 1) * g ** (2 * n + 3) for n, coefficient in enumerate(b))
        worst = max(worst, abs(got - want) / abs(want))
    return worst


def _quartic_tensor(lH: float, lS: float, lHS: float) -> np.ndarray:
    """lambda_abcd = d^4 V for 6 real fields (4 in H, 2 in S) via the polarization identity."""
    def potential(phi: np.ndarray) -> float:
        h2 = float(phi[:4] @ phi[:4])
        s2 = float(phi[4:] @ phi[4:])
        return lH / 4.0 * h2 * h2 + lS / 4.0 * s2 * s2 + lHS / 4.0 * h2 * s2

    n = 6
    eye = np.eye(n)
    tensor = np.zeros((n, n, n, n))
    signs = list(itertools.product((1.0, -1.0), repeat=4))
    for a, b, c, d in itertools.combinations_with_replacement(range(n), 4):
        value = sum(
            s[0] * s[1] * s[2] * s[3] * potential(s[0] * eye[a] + s[1] * eye[b] + s[2] * eye[c] + s[3] * eye[d])
            for s in signs
        ) / 16.0
        for p in set(itertools.permutations((a, b, c, d))):
            tensor[p] = value
    return tensor


def portal_tensor_deviation() -> float:
    """Scalar-only one-loop betas from 16pi^2 beta_abcd = sum_3 channels lambda_abef lambda_efcd."""
    worst = 0.0
    for lH, lS, lHS in ((0.13, 0.4, 0.7), (0.02, 0.05, -0.03), (1.0, 1.0, 2.0)):
        lam = _quartic_tensor(lH, lS, lHS)
        beta = (np.einsum("abef,efcd->abcd", lam, lam) + np.einsum("acef,efbd->abcd", lam, lam)
                + np.einsum("adef,efbc->abcd", lam, lam))
        tensor = (beta[0, 0, 0, 0] / 6.0, beta[4, 4, 4, 4] / 6.0, beta[0, 0, 4, 4])
        dH, dS, dHS = portal_one_loop(lH, lS, lHS, 0.0, 0.0, 0.0)
        closed = (24.0 * lH * lH + dH, dS, dHS)
        cross_check = (lam[0, 0, 0, 0] - 6.0 * lH, lam[4, 4, 4, 4] - 6.0 * lS, lam[0, 0, 4, 4] - lHS)
        worst = max(worst, max(abs(x - y) for x, y in zip(tensor, closed)), max(map(abs, cross_check)))
    return worst


def portal_literature_deviation() -> float:
    """Elias-Miro et al. 1203.0237 eq. (RG) / SMASH 1610.01639 App. A, in their convention
    V > 2 x (H^dag H)|S|^2 (x = lambda_Hsigma), mapped with lambda_HS = 2 x."""
    worst = 0.0
    for point in _random_points(50, 1203_0237):
        gY, g2, _, yt, lH = point
        lS, x = 0.1 + 0.5 * abs(lH), 0.3 * lH - 0.02
        em_lh = ((12 * yt**2 - 3 * gY**2 - 9 * g2**2) * lH - 6 * yt**4
                 + 3.0 / 8.0 * (2 * g2**4 + (gY**2 + g2**2) ** 2) + 24 * lH**2 + 4 * x**2)
        em_x = 0.5 * (12 * yt**2 - 3 * gY**2 - 9 * g2**2) * x + 4 * x * (3 * lH + 2 * lS) + 8 * x**2
        em_ls = 8 * x**2 + 20 * lS**2
        lHS = 2.0 * x
        dH, dS, dHS = portal_one_loop(lH, lS, lHS, yt, g2, gY)
        sm_lh = sm_beta([gY, g2, 1.0, yt, lH], loops=1)[4] / K1
        worst = max(worst, abs(sm_lh + dH - em_lh), abs(dS - em_ls), abs(dHS - 2.0 * em_x))
    return worst


def portal_anomalous_dimension_ok() -> bool:
    """The gauge/Yukawa part of beta_lambdaHS is 2 gamma_H: half of the SM linear-in-lambda
    one-loop terms (4 gamma_H lambda), read off the exact table."""
    linear = {e: c for e, c in COEFFS["lam", 1].items() if e[4] == 1 and sum(e[:4]) == 1}
    if sorted(linear) != [(0, 0, 0, 1, 1), (0, 1, 0, 0, 1), (1, 0, 0, 0, 1)]:
        return False
    unit = {(0, 0, 0, 1, 1): (1.0, 0.0, 0.0), (0, 1, 0, 0, 1): (0.0, 1.0, 0.0), (1, 0, 0, 0, 1): (0.0, 0.0, 1.0)}
    for exponents, coefficient in linear.items():
        yt, g2, gY = unit[exponents]
        # lambda_HS = 1, other quartics 0: beta = 4 (lambda_HS^2 term) + 2 gamma_H coefficient
        _, _, value = portal_one_loop(0.0, 0.0, 1.0, yt, g2, gY)
        if abs((value - 4.0) - float(coefficient) / 2.0) > 1.0e-15:
            return False
    return True


def tree_vacuum_criterion_ok() -> bool:
    """Numerically minimize V = lambda_H x^2 + lambda_HS x y + lambda_S y^2 on x >= 0,
    y >= -1 and confirm: global minimum < 0 iff lambda_H - lambda_HS^2/(4 lambda_S) < 0."""
    xs = np.linspace(0.0, 10.0, 2001)
    ys = np.linspace(-1.0, 3.0, 401)
    X, Y = np.meshgrid(xs, ys)
    for lam_sm, lam_s, lam_hs in ((-0.0085, 0.1, 0.3), (0.004, 0.1, 0.3), (-0.02, 0.5, 1.0), (0.01, 0.5, 1.0)):
        lam_h = match_threshold(lam_sm, lam_s, lam_hs)
        values = lam_h * X * X + lam_hs * X * Y + lam_s * Y * Y
        numeric = float(np.min(values))
        # S = 0 boundary value; the true minimum is at or below it
        boundary = lam_s - lam_hs**2 / (4.0 * lam_h)
        if (numeric < -1.0e-12) != (lam_sm < 0):
            return False
        if lam_sm < 0 and not (boundary < 0 and numeric < boundary + 1.0e-4):
            return False
    return True


def anchor_check() -> dict[str, Any]:
    try:
        import scalar_vacuum_proton_decay_v20 as scalar_pd  # lightweight repository anchor
        anchor = scalar_pd._unification_anchor()
    except Exception as exc:  # fail closed
        return {"available": False, "error": f"{type(exc).__name__}: {exc}", "matches": False}
    matches = bool(anchor.get("available")) and (
        abs(float(anchor["M_I_GeV"]) - M_I_GEV) <= ANCHOR_RTOL * M_I_GEV
        and abs(float(anchor["M_GUT_GeV"]) - M_GUT_GEV) <= ANCHOR_RTOL * M_GUT_GEV
    )
    return {
        "available": bool(anchor.get("available")),
        "M_I_GeV": float(anchor["M_I_GeV"]),
        "M_GUT_GeV": float(anchor["M_GUT_GeV"]),
        "matches": matches,
        "source": "scalar_vacuum_proton_decay_v20._unification_anchor()",
    }


def two_stage_round_trip_deviation() -> float:
    profile = sm_profile(loops=2)
    sm = profile.couplings(M_I_GEV)
    lam_s, lam_hs = 0.1, 0.3
    stage = run_two_stage(sm, M_I_GEV, lam_s, lam_hs)
    end = stage["at_end"]
    back = solve_ivp(_stage_rhs(2, False), (math.log(M_GUT_GEV), math.log(M_I_GEV)),
                     [end[k] for k in ("gY", "g2", "g3", "yt", "lambda_H", "lambda_S", "lambda_HS")],
                     method="DOP853", rtol=SM_RTOL, atol=SM_ATOL).y[:, -1]
    lam_sm = invert_threshold(back[4], back[5], back[6])
    low = run_sm(list(back[:4]) + [lam_sm], M_I_GEV, MT_REF)
    return max(abs(low[k] - BUTTAZZO_INPUTS[k]) for k in COUPLINGS)


def zero_portal_deviation() -> float:
    profile = sm_profile(loops=2)
    stage = run_two_stage(profile.couplings(M_I_GEV), M_I_GEV, 0.2, 0.0)
    ts = np.linspace(math.log(M_I_GEV), math.log(M_GUT_GEV), 41)
    return float(np.max(np.abs(stage["solution"].sol(ts)[4] - profile.solution.sol(ts)[4])))


def one_loop_gauge_deviation() -> float:
    running = run_sm(BUTTAZZO_INPUTS, MT_REF, 1.0e16, loops=1)
    log = math.log(1.0e16 / MT_REF)
    return max(
        abs(running[k] - (1.0 / BUTTAZZO_INPUTS[k] ** 2 - 2.0 * b * K1 * log) ** -0.5)
        for k, b in (("gY", 41.0 / 6.0), ("g2", -19.0 / 6.0), ("g3", -7.0))
    )


def sm_round_trip_deviation() -> float:
    up = run_sm(BUTTAZZO_INPUTS, MT_REF, M_PL_GEV, loops=2)
    back = run_sm(up, M_PL_GEV, MT_REF, loops=2)
    return max(abs(back[k] - BUTTAZZO_INPUTS[k]) for k in COUPLINGS)


# =============================================================================
# report
# =============================================================================
def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, F):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return round(value, DIGITS) + 0.0
    return value


def build_report() -> dict[str, Any]:
    running = sm_running_audit()
    bound = top_mass_bound_audit()
    portal = portal_analysis()
    gut = gut_single_stage_audit()
    anchor = anchor_check()
    profile = sm_profile(loops=2)
    instability = profile.instability_scale()
    decay_mi = tunnelling_estimate(profile, instability, M_I_GEV)
    runs = running["runs"]
    planck = running["three_loop_planck_couplings"]
    grid = portal["classification_grid"]
    windows = portal["windows_lambda_H_positive_to_M_GUT"]
    fix = portal["benchmark_O36_O23_kept_solve_O34"]
    radial = portal["radial_mode_threshold"]
    lam_gut = {key: runs[key]["lambda_at"]["M_GUT"] for key in ("1L", "2L", "3L+4QCD")}
    at_bound = bound["instability_scale_at_bound_GeV"]

    checks = {
        "anchor_scales_match_repository_unification_anchor": anchor["matches"],
        "two_loop_coefficients_two_transcriptions_agree_exactly": not two_transcriptions_disagreements(),
        "fast_betas_match_exact_coefficient_tables": fast_beta_table_deviation() < 1.0e-13,
        "pure_qcd_limit_matches_b0_to_b3": pure_qcd_deviation() < 1.0e-13,
        "one_loop_gauge_running_matches_analytic_solution": one_loop_gauge_deviation() < 1.0e-11,
        "sm_round_trip_mt_to_mpl_and_back": sm_round_trip_deviation() < 1.0e-9,
        "one_loop_reproduces_superseded_5f25846_minus_0_0335": abs(
            runs["1L_superseded_5f25846_mu0_173.10"]["lambda_at"]["1e16"] - SUPERSEDED_5F25846_LAMBDA_GUT_ONE_LOOP
        ) < SUPERSEDED_5F25846_ATOL,
        "one_loop_portal_requirement_reproduces_superseded_5f25846_2_033": abs(
            gut["lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1_at_1e16_GeV"]["1L_mu0_173.10"]
            - SUPERSEDED_5F25846_LAMBDA_HS_REQUIRED
        ) < SUPERSEDED_5F25846_ATOL,
        "two_loop_minus_one_loop_is_positive_and_smaller_than_one_loop": (
            0.0 < lam_gut["2L"] - lam_gut["1L"] < abs(lam_gut["1L"])
        ),
        "three_loop_correction_smaller_than_two_loop_correction": (
            abs(lam_gut["3L+4QCD"] - lam_gut["2L"]) < abs(lam_gut["2L"] - lam_gut["1L"])
        ),
        "three_loop_reproduces_buttazzo_planck_values": (
            abs(planck["lambda"] - BUTTAZZO_PUBLISHED["lambda_M_Pl"]) < 1.5e-4
            and abs(planck["g1"] - BUTTAZZO_PUBLISHED["g1_M_Pl"]) < 1.5e-4
            and abs(planck["g2"] - BUTTAZZO_PUBLISHED["g2_M_Pl"]) < 1.5e-4
            and abs(planck["g3"] - BUTTAZZO_PUBLISHED["g3_M_Pl"]) < 1.5e-4
            and abs(planck["yt"] - BUTTAZZO_PUBLISHED["yt_M_Pl"]) < 1.5e-4
        ),
        "three_loop_top_slope_matches_published": abs(
            running["top_mass_sensitivity"]["3L+4QCD"]["dlambda_M_Pl_dMt_per_GeV"]
            - BUTTAZZO_PUBLISHED["dlambda_M_Pl_dMt_per_GeV"]
        ) < 5.0e-4,
        "instability_scale_is_zero_of_lambda": abs(profile.lam(instability)) < 1.0e-12,
        "portal_betas_match_general_scalar_tensor_formula": portal_tensor_deviation() < 1.0e-9,
        "portal_betas_match_elias_miro_and_smash_after_convention_map": portal_literature_deviation() < 1.0e-12,
        "portal_anomalous_dimension_is_half_sm_linear_lambda_terms": portal_anomalous_dimension_ok(),
        "threshold_matching_round_trip_on_grid": max(row["threshold_round_trip_residual"] for row in grid) < 1.0e-15,
        "benchmark_tree_lambda_eff_at_M_I_equals_lambda_SM_M_I": abs(
            fix["tree_level_lambda_eff_at_M_I"] - portal["matching"]["tree_level_lambda_eff_at_M_I_every_solution"]
        ) < 1.0e-12,
        "two_stage_round_trip_recovers_mt_inputs": two_stage_round_trip_deviation() < 1.0e-8,
        "zero_portal_two_stage_equals_sm_running": zero_portal_deviation() < 1.0e-9,
        "tree_level_vacuum_criterion_matches_numeric_minimum": tree_vacuum_criterion_ok(),
        "critical_top_mass_puts_instability_scale_at_M_I": (
            at_bound is not None and abs(math.log(at_bound / M_I_GEV)) < 1.0e-5
        ),
        "every_window_found_and_interior_points_valid": all(
            window["window_exists"] and window["interior_points_copositive_and_perturbative"]
            and window["lambda_HS_min"] < window["lambda_HS_max"]
            for window in windows
        ),
        "benchmark_compatible_portal_solution_converged": fix["converged"],
        "no_gate_closed_or_model_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures

    central_absolute = any(row["class"] == "ABSOLUTELY_STABLE_TO_M_GUT" for row in grid)
    radial_absolute = any(
        entry["window"].get("window_exists") and entry["radial_mode_below_instability_scale"]
        and entry["window"].get("middle_classification") == "ABSOLUTELY_STABLE_TO_M_GUT"
        for entry in radial["scan"]
    )
    lam_eff_mi = portal["matching"]["tree_level_lambda_eff_at_M_I_every_solution"]
    middles = [window["tree_level_lambda_eff_at_gut_values"]["middle"] for window in windows if window["window_exists"]]
    radial_windows = [entry["window"] for entry in radial["scan"] if entry["window"].get("window_exists")]
    radial_gut_negative = [
        window for window in radial_windows
        if all(value < 0 for value in window["tree_level_lambda_eff_at_gut_values"].values())
    ]
    metastable_rows = [row for row in grid if row["class"] == "METASTABLE_LONG_LIVED_ESTIMATE"]
    metastable_tree_min = [row for row in metastable_rows if row["tree_level_local_minimum_at_gut_values"]]
    outcomes = {
        "sm_instability_scale_below_M_I_at_central_inputs": ok and instability < M_I_GEV,
        "absolute_stability_possible_at_central_inputs": ok and central_absolute,
        "requires_metastability_at_central_inputs": ok and not central_absolute,
        "ew_vacuum_lifetime_exceeds_age_of_universe_estimate": ok and decay_mi["lifetime_exceeds_age_of_universe"],
        "lambda_H_positive_window_exists_above_M_I_for_every_scanned_lambda_S": ok and all(
            window["window_exists"] for window in windows
        ),
        "negative_portal_cannot_help_when_lambda_SM_M_I_negative": ok and portal["negative_portal_always_fails_at_M_I"],
        "certified_benchmark_110_reproduces_higgs_mass": ok
        and portal["certified_benchmark_110"]["reproduces_observed_higgs_mass"],
        "benchmark_O36_O23_kept_O34_solution_exists_and_perturbative": ok and fix["converged"]
        and fix["classification"]["perturbative_to_M_GUT"],
        "absolute_stability_possible_at_central_inputs_if_radial_mode_below_Lambda_I": ok and radial_absolute,
        "absolute_stability_top_mass_bound_below_measured_top_mass": ok
        and bound["Mt_max_with_PDG2024_Mh_and_alpha_s_GeV"]["3L+4QCD"] < PDG2024["Mt_GeV"]
        and bound["Mt_max_landau_veff_zero_definition_estimate_GeV"]["3L+4QCD_PDG2024_Mh_alpha_s"] < PDG2024["Mt_GeV"],
        "absolute_stability_excluded_beyond_2_sigma_under_both_definitions": ok
        and min(bound["measured_minus_bound_in_sigma_3L_PDG_like"],
                bound["measured_minus_bound_in_sigma_3L_PDG_like_landau_veff_estimate"]) > 2.0,
        "requires_metastability_at_pdg2024_central_inputs_both_definitions": ok and all(
            row["instability_below_M_I_msbar"] and row["instability_below_M_I_landau_veff_estimate"]
            for row in bound["pdg2024_central"]["runs"].values()
        ),
        "conclusion_independent_of_instability_scale_definition_at_buttazzo_central": ok
        and LANDAU_VEFF_ZERO_OVER_MSBAR_ZERO * instability < M_I_GEV,
        "gut_single_stage_matching_requires_negative_lambda_eff_two_loop": ok
        and gut["lambda_eff_required_at_M_GUT"]["2L"] < 0,
        "tuned_gut_point_not_tree_level_local_minimum_in_single_stage_matching": ok
        and not any(gut["tuned_point_is_tree_level_local_minimum"].values()),
        "M_I_matched_tuned_point_is_tree_level_saddle_at_M_I_for_every_solution": ok and lam_eff_mi < 0,
        "benchmark_O36_O23_kept_is_tree_level_saddle": ok and fix["converged"]
        and fix["tree_level_lambda_eff_at_gut_values"] < 0 and fix["tree_level_lambda_eff_at_M_I"] < 0,
        "n_window_middles_with_tree_lambda_eff_at_gut_negative": sum(value < 0 for value in middles),
        "n_window_middles": len(middles),
        # lower edge, geometric middle and upper edge of each radial-mode window
        "n_radial_windows_with_tree_lambda_eff_at_gut_negative_at_every_point": len(radial_gut_negative),
        "n_radial_windows": len(radial_windows),
        "n_metastable_grid_rows": len(metastable_rows),
        "n_metastable_grid_rows_with_tree_lambda_eff_at_gut_nonnegative": len(metastable_tree_min),
    }
    headline = {
        "Lambda_I_2L_GeV": instability,
        "Lambda_I_3L_GeV": runs["3L+4QCD"]["instability_scale_GeV"],
        "lambda_SM_M_I_2L": runs["2L"]["lambda_at"]["M_I"],
        "lambda_SM_M_GUT_2L": runs["2L"]["lambda_at"]["M_GUT"],
        "lambda_SM_M_Pl_2L": runs["2L"]["lambda_at"]["M_Pl"],
        "lambda_min_2L": runs["2L"]["lambda_min"],
        "lambda_SM_M_I_1L": runs["1L"]["lambda_at"]["M_I"],
        "lambda_SM_M_GUT_1L": runs["1L"]["lambda_at"]["M_GUT"],
        "lambda_SM_M_Pl_3L": runs["3L+4QCD"]["lambda_at"]["M_Pl"],
        "Mt_max_absolute_stability_2L_GeV": bound["Mt_max_absolute_stability_threshold_at_M_I_GeV"]["2L"],
        "Mt_max_absolute_stability_3L_GeV": bound["Mt_max_absolute_stability_threshold_at_M_I_GeV"]["3L+4QCD"],
        "Mt_max_absolute_stability_3L_PDG2024_Mh_alpha_s_GeV": bound["Mt_max_with_PDG2024_Mh_and_alpha_s_GeV"]["3L+4QCD"],
        "Mt_max_absolute_stability_3L_PDG2024_landau_veff_estimate_GeV": bound[
            "Mt_max_landau_veff_zero_definition_estimate_GeV"]["3L+4QCD_PDG2024_Mh_alpha_s"],
        "measured_Mt_above_bound_sigma_msbar": bound["measured_minus_bound_in_sigma_3L_PDG_like"],
        "measured_Mt_above_bound_sigma_landau_veff_estimate": bound[
            "measured_minus_bound_in_sigma_3L_PDG_like_landau_veff_estimate"],
        "bounce_action_window_Lambda_I_to_M_I": decay_mi.get("bounce_action_at_lambda_min"),
        "lambda_S_max_radial_mode_below_Lambda_I": radial["lambda_S_max_for_m_rho_below_Lambda_I_2L"],
        "required_O34_with_O36_eq_O23_eq_1": fix["required_O34_at_M_GUT"],
        "tree_level_lambda_eff_M_I": lam_eff_mi,
        "tree_level_lambda_eff_M_GUT_O36_eq_O23_eq_1": fix["tree_level_lambda_eff_at_gut_values"],
        "tree_level_lambda_eff_M_GUT_window_middles": middles,
    }
    verdict = (
        "Within an SM + complex-singlet EFT (not the repository's 2HDM + Pati-Salam anchor chain, and not "
        "realized by any current repository vacuum, whose Delta_R is not the SM singlet): "
        f"two-loop SM running from the Buttazzo et al. inputs puts the MSbar instability scale at "
        f"{instability:.3g} GeV, a factor {M_I_GEV / instability:.0f} below M_I, with "
        f"lambda_SM(M_I) = {headline['lambda_SM_M_I_2L']:.5f} and lambda_SM(M_GUT) = "
        f"{headline['lambda_SM_M_GUT_2L']:.5f} (one loop: {headline['lambda_SM_M_GUT_1L']:.4f}). With the H-S "
        "portal threshold at M_I, positive-portal windows keep lambda_H > 0 up to M_GUT for every scanned "
        "lambda_S. Copositivity is not the tree-level local-minimum condition (the single-stage point is "
        "copositive too). At the tuned point of the tree potential the condition is lambda_eff = lambda_H - "
        "lambda_HS^2/(4 lambda_S) >= 0 (g3_tuned_target_portal_threshold_v20). With the S threshold at M_I, "
        f"lambda_eff(M_I) = lambda_SM(M_I) = {lam_eff_mi:.4f} < 0, so the M_I threshold does not remove the "
        "tree-level saddle; at the GUT coefficients lambda_eff is "
        f"{headline['tree_level_lambda_eff_M_GUT_O36_eq_O23_eq_1']:.3f} for the O36 = O23 = 1 benchmark and "
        f"negative at {outcomes['n_window_middles_with_tree_lambda_eff_at_gut_negative']} of "
        f"{outcomes['n_window_middles']} window middles. Metastability is the RG-improved statement. "
        "In the RG-improved potential the EW vacuum is still not the global minimum at central inputs, "
        "because the SM segment [Lambda_I, M_I] has lambda_SM < 0; the bounce estimate S ~ "
        f"{headline['bounce_action_window_Lambda_I_to_M_I']:.0f} far exceeds the ~500 needed, so it is "
        "metastable and long-lived (estimate). At tree level with the S vev the EW/S point is a local (and "
        "then global) minimum iff lambda_SM(threshold) >= 0, so at central inputs it is the tree-level saddle "
        "stated above. Absolute stability with the threshold at M_I needs "
        f"M_t < {headline['Mt_max_absolute_stability_2L_GeV']:.2f} GeV (2L) / "
        f"{headline['Mt_max_absolute_stability_3L_GeV']:.2f} GeV (3L) with the MSbar criterion. With "
        f"PDG 2024 M_h and alpha_s this becomes {headline['Mt_max_absolute_stability_3L_PDG2024_Mh_alpha_s_GeV']:.2f} GeV, "
        f"{headline['measured_Mt_above_bound_sigma_msbar']:.1f} sigma below the measured "
        f"{PDG2024['Mt_GeV']} +- {PDG2024['Mt_err_GeV']} GeV; with the Landau-gauge effective-potential zero it is ~"
        f"{headline['Mt_max_absolute_stability_3L_PDG2024_landau_veff_estimate_GeV']:.2f} GeV "
        f"({headline['measured_Mt_above_bound_sigma_landau_veff_estimate']:.1f} sigma). The alternative is a "
        "radial mode below Lambda_I, i.e. "
        f"lambda_S <~ {headline['lambda_S_max_radial_mode_below_Lambda_I']:.2g}, far from the certified O23 = 1 "
        "(RG-improved: lambda_eff(m_rho) > 0 there, but lambda_eff at the GUT coefficients is negative at every "
        "scanned window point). "
        "Keeping O36 = O23 = 1 needs O34 = lambda_HS(M_GUT) = "
        f"{headline['required_O34_with_O36_eq_O23_eq_1']:.3f} (RG-improved metastable; a tree-level saddle, since "
        "O34 > 2 at O36 = O23 = 1). Single-stage GUT matching needs "
        f"lambda_eff(M_GUT) = {gut['lambda_eff_required_at_M_GUT']['2L']:.4f} at two loops (negative at every loop "
        "order), so that tuned point is not a tree-level local minimum either. The RG-improved M_I-threshold "
        "conclusions are marginal: they depend on M_t (1-2 sigma), on the MSbar versus "
        "effective-potential instability criterion, and on the omitted states listed in the scope. This is an "
        "RG-improved EFT statement, not an exact lower witness of the 486-field tree potential: G3 stays open "
        "and the model is neither validated nor excluded."
    )
    if not ok:
        status = "G3_PHYSICAL_HIERARCHY_HIGGS_STABILITY_AUDIT_FAILED"
    elif outcomes["requires_metastability_at_central_inputs"]:
        status = (
            "G3_SM_SINGLET_EFT_HIGGS_STABILITY__TUNED_POINT_TREE_SADDLE_FOR_GUT_OR_M_I_MATCHING__"
            "EW_VACUUM_METASTABLE_AT_BUTTAZZO_CENTRAL_INPUTS__G3_OPEN"
        )
    else:
        # an absolutely stable grid row needs lambda_SM > 0 up to M_I, so no M_I tree saddle is claimed
        status = (
            "G3_SM_SINGLET_EFT_HIGGS_STABILITY__TUNED_POINT_TREE_SADDLE_FOR_GUT_ONLY_MATCHING__"
            "EW_VACUUM_STABLE_WINDOW_WITH_M_I_THRESHOLD__G3_OPEN"
        )
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": status,
        "overall_state": "PHYSICAL_TARGET_CONSTRAINT" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scientific_outcomes": outcomes,
        "headline": headline,
        "scales_GeV": {
            "M_I": M_I_GEV,
            "M_GUT": M_GUT_GEV,
            "M_Pl": M_PL_GEV,
            "anchor": anchor,
            "colour_triplet_partner_sqrt_beta_M_I": math.sqrt(TRIPLET_BETA) * M_I_GEV,
        },
        "certified_gut_couplings": {
            "parameters": {"lambda_H": H_QUARTIC_ID, "lambda_S": S_QUARTIC_ID, "lambda_HS": PORTAL_ID},
            "values": CERTIFIED_GUT_COUPLINGS,
        },
        "sm_running": running,
        "top_mass_bound": bound,
        "metastability_threshold_at_M_I_2L": decay_mi,
        "portal": portal,
        "gut_single_stage_matching": gut,
        "flags": {
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "tree_level_matching_only": True,
            "two_loop_sm_running": True,
            "one_loop_portal_running": True,
            "decay_rate_is_estimate": True,
            "conclusions_conditional_on_sm_singlet_eft": True,
            "repository_vacuum_realizing_this_eft_exists": False,
        },
        "scope": [
            "Only the complex singlet S is kept between M_I and M_GUT. Other states near M_I are omitted: any "
            "colour-triplet partner (the F-branch formula extrapolated to M_I gives sqrt(beta) M_I ~ 1.4e11 GeV, "
            "but no such state has been constructed) and light Sigma_126bar components.",
            "The axion-sector vector-like fermion Yukawas (y S Q Qbar), which drive lambda_S through "
            "-6 y^4 and 12 y^2 lambda_S, are omitted, as are right-handed-neutrino Yukawas.",
            "Threshold matching is tree level at mu = M_I (or at m_rho in the radial-mode scan). One-loop "
            "threshold corrections and the log of m_rho/M_I are omitted.",
            "Portal running is one loop; the singlet-only two-loop pieces from SMASH App. A enter only as a "
            "sensitivity estimate. SM running below M_I is two loop (three loop + four-loop QCD as a cross-check).",
            "Stability is judged on the RG-improved tree potential, with lambda evaluated at mu ~ field value. "
            "The MSbar zero Lambda_I is not the Landau-gauge effective-potential zero, which is ~6.5x higher "
            "(Buttazzo et al.). Both sit below M_I at the Buttazzo and PDG 2024 central inputs. The top-mass "
            "bound moves by ~0.4 GeV between the two definitions, and it is quoted for both.",
            "The vacuum-decay numbers use the tree-level Fubini bounce, with no quantum, gravitational or "
            "thermal corrections. They are estimates.",
            "Tree-level local minimality at the tuned point (lambda_eff >= 0) is evaluated on the (H, S) block "
            "only, at M_I and at the running GUT values; it is a necessary condition, not a 486-field Hessian test.",
            "Identifying the GUT-scale light-field quartics with the tree-level coefficients O36_B02, O23 and "
            "O34 assumes no heavy-exchange shifts at M_GUT for S and HS; only the H shift was shown to vanish.",
            "This is not an exact lower witness of the 486-field tree potential; the G3 gate stays open.",
            "EFT mismatch: the repository's M_I/M_GUT anchor (two_loop_thresholds_v20 chain) runs a 2HDM below M_I "
            "and Pati-Salam above it, while this module runs the one-doublet SM below M_I and SM + singlet above. "
            "In a 2HDM the stability conditions differ (lambda3, lambda4 raise beta_lambda1,2), so the "
            "no-absolute-stability conclusions hold only if the low-energy EFT is exactly the SM.",
            "No current repository vacuum realizes this EFT: the certified Delta_R (direct.delta_r) is the "
            "T3R = 0, Y = -1 component of the 126bar triplet, not the SM singlet (g3_sigma_hypercharge_audit_v20).",
            "Above M_N ~ f M_I, SO(10) Dirac neutrino Yukawas y_nu ~ y_t add -2 y_nu^4 to beta_lambda_H; the dynamical "
            "Delta_R and its portals give further thresholds (a matrix over the S and Delta_R radial modes) and "
            "make lambda_HS = 0 non-RG-invariant at one loop.",
            "For lambda_S << lambda_HS the relevant scale is the valley end h_c ~ sqrt2 (lambda_S/delta)^(1/4) M_I rather "
            "than m_rho; the radial-mode scan treats the threshold at m_rho and is optimistic there.",
            "The Fubini bounce at 1/R ~ M_I has a central field above the threshold; the action is used as a "
            "conservative lower bound (V >= lambda_SM(M_I) |H|^4 at tree level). Inflationary and thermal "
            "Higgs fluctuations are not addressed.",
            "With PDG 2024 inputs, the effective-potential criterion and matching at m_rho, absolute stability is "
            "allowed for small lambda_S; the 'metastable at central inputs' status refers to the Buttazzo 2013 "
            "central values and the MSbar criterion.",
        ],
        "verdict": verdict,
    }


def _fmt_num(value: Any, spec: str = ".4g") -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return str(value)
    return format(value, spec)


def _markdown(report: dict[str, Any]) -> str:
    running = report["sm_running"]
    bound = report["top_mass_bound"]
    portal = report["portal"]
    gut = report["gut_single_stage_matching"]
    decay = report["metastability_threshold_at_M_I_2L"]
    lines = [
        "# Higgs-vacuum stability in an SM + singlet EFT at the repository scales -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## SM running (Buttazzo et al. 1307.3536 v3/v4 inputs, mu0 = M_t = 173.34 GeV)",
        "",
        "| run | Lambda_I [GeV] | lambda(M_I) | lambda(M_GUT) | lambda(M_Pl) | lambda_min |",
        "|---|---|---|---|---|---|",
    ]
    for key in ("1L_superseded_5f25846_mu0_173.10", "1L", "2L", "3L+4QCD"):
        run = running["runs"][key]
        lines.append(
            f"| {key} | {_fmt_num(run['instability_scale_GeV'], '.4g')} | {run['lambda_at']['M_I']:+.6f} | "
            f"{run['lambda_at']['M_GUT']:+.6f} | {run['lambda_at']['M_Pl']:+.6f} | {run['lambda_min']:+.6f} |"
        )
    lines += ["", "| M_t [GeV] | loops | Lambda_I [GeV] | lambda(M_I) | lambda(M_GUT) | lambda(M_Pl) |",
              "|---|---|---|---|---|---|"]
    for key, rows in running["top_mass_sensitivity"].items():
        for shift in ("-1", "+0", "+1"):
            row = rows[shift]
            lines.append(
                f"| {row['Mt_GeV']:.2f} | {key} | {_fmt_num(row['instability_scale_GeV'], '.3e')} | "
                f"{row['lambda_M_I']:+.6f} | {row['lambda_M_GUT']:+.6f} | {row['lambda_M_Pl']:+.6f} |"
            )
    mt = bound["Mt_max_absolute_stability_threshold_at_M_I_GeV"]
    pdg = bound["Mt_max_with_PDG2024_Mh_and_alpha_s_GeV"]
    veff = bound["Mt_max_landau_veff_zero_definition_estimate_GeV"]
    central = bound["pdg2024_central"]["runs"]["3L+4QCD"]
    lines += [
        "",
        "## Top-mass bound and metastability (threshold at M_I)",
        "",
        f"- Absolute stability needs Lambda_I >= M_I: M_t < `{mt['2L']:.3f}` GeV (2L), `{mt['3L+4QCD']:.3f}` GeV "
        f"(3L+4QCD); with M_h = 125.20, alpha_s = 0.1180: `{pdg['2L']:.3f}` / `{pdg['3L+4QCD']:.3f}` GeV "
        f"(matching theory error +-{bound['theory_error_GeV_from_matching']['combined']:.2f} GeV).",
        f"- With the Landau-gauge effective-potential zero (~6.5 x the MSbar zero) instead: "
        f"`{veff['3L+4QCD']:.3f}` GeV (3L), `{veff['3L+4QCD_PDG2024_Mh_alpha_s']:.3f}` GeV (3L, PDG 2024 M_h, alpha_s); "
        "an estimate.",
        f"- Measured M_t = {PDG2024['Mt_GeV']} +- {PDG2024['Mt_err_GeV']} GeV: "
        f"{bound['measured_minus_bound_in_sigma_3L_PDG_like']:.1f} sigma above the 3L MSbar bound, "
        f"{bound['measured_minus_bound_in_sigma_3L_PDG_like_landau_veff_estimate']:.1f} sigma above the "
        "effective-potential estimate.",
        f"- PDG 2024 central inputs (3L): MSbar zero `{central['msbar_instability_scale_GeV']:.3g}` GeV, "
        f"effective-potential zero ~`{central['landau_veff_zero_estimate_GeV']:.3g}` GeV, both below M_I; "
        f"lambda_SM(M_I) = `{central['lambda_M_I']:.5f}`.",
        f"- Window [Lambda_I, M_I]: lambda_min = `{decay['lambda_min_in_window']:.5f}`, bounce action "
        f"S ~ `{decay['bounce_action_at_lambda_min']:.0f}` vs ~{decay['critical_action_at_lambda_min']:.0f} needed; "
        f"max log10 p ~ `{decay['max_log10_decay_probability_in_past_light_cone']:.0f}` (estimate).",
        "",
        "## Portal windows at M_I (lambda_H > 0 and |lambda| < 4 pi up to M_GUT)",
        "",
        "| lambda_S(M_I) | lambda_HS min | lambda_HS max | delta min | (lambda_H, lambda_S, lambda_HS)(M_GUT) at middle "
        "| tree lambda_eff(M_GUT) at middle | class |",
        "|---|---|---|---|---|---|---|",
    ]
    for window in portal["windows_lambda_H_positive_to_M_GUT"]:
        mid = window["gut_values_at_geometric_middle"]
        lines.append(
            f"| {window['lambda_S']:g} | {window['lambda_HS_min']:.5f} | {window['lambda_HS_max']:.4f} | "
            f"{window['delta_min']:.5f} | ({mid['lambda_H']:.4f}, {mid['lambda_S']:.4f}, {mid['lambda_HS']:.4f}) | "
            f"{window['tree_level_lambda_eff_at_gut_values']['middle']:+.4f} | {window['middle_classification']} |"
        )
    fix = portal["benchmark_O36_O23_kept_solve_O34"]
    bench = portal["certified_benchmark_110"]
    radial = portal["radial_mode_threshold"]
    outcomes = report["scientific_outcomes"]
    lines += [
        "",
        f"- Tree level: lambda_eff(M_I) = lambda_SM(M_I) = "
        f"`{portal['matching']['tree_level_lambda_eff_at_M_I_every_solution']:.5f}` for every M_I solution, so the "
        "M_I-matched tuned point is a tree-level saddle; the classes above are RG-improved. Metastable grid rows "
        f"with lambda_eff(M_GUT) >= 0: {outcomes['n_metastable_grid_rows_with_tree_lambda_eff_at_gut_nonnegative']} "
        f"of {outcomes['n_metastable_grid_rows']}.",
        f"- Certified benchmark (1, 1, 0) at M_GUT: lambda(M_t) = `{bench['lambda_at_mt']:.4f}`, "
        f"m_h(tree) = `{bench['m_h_tree_GeV']:.1f}` GeV (two loops).",
        f"- Keeping O36 = O23 = 1: lambda_S(M_I) = `{fix['lambda_S_M_I']:.4f}`, lambda_HS(M_I) = "
        f"`{fix['lambda_HS_M_I']:.4f}`, O34 = lambda_HS(M_GUT) = `{fix['required_O34_at_M_GUT']:.4f}`; "
        f"class `{fix['classification']['class']}` (RG-improved); tree-level lambda_eff(M_GUT) = "
        f"`{fix['tree_level_lambda_eff_at_gut_values']:.4f}`, a saddle.",
        f"- Radial-mode threshold m_rho = 2 sqrt(lambda_S) M_I is below Lambda_I iff lambda_S < "
        f"`{radial['lambda_S_max_for_m_rho_below_Lambda_I_2L']:.3g}`:",
    ]
    for entry in radial["scan"]:
        window = entry["window"]
        span = (f"lambda_HS in [{window['lambda_HS_min']:.3g}, {window['lambda_HS_max']:.3g}]"
                if window.get("window_exists") else "no window")
        tree = (f"; tree lambda_eff(m_rho) = {window['tree_level_lambda_eff_at_match']:+.4f}, lambda_eff(M_GUT) at "
                f"middle = {window['tree_level_lambda_eff_at_gut_values']['middle']:+.4f} (class RG-improved)"
                if window.get("window_exists") else "")
        lines.append(
            f"  - lambda_S = {entry['lambda_S']:g}: m_rho = {entry['radial_mode_mass_GeV']:.3g} GeV, "
            f"below Lambda_I: {entry['radial_mode_below_instability_scale']}; {span}; "
            f"class {window.get('middle_classification', '-')}{tree}"
        )
    required = gut["lambda_eff_required_at_M_GUT"]
    zero = gut["lambda_eff_zero_prediction"]
    lines += [
        "",
        "## Single-stage matching at M_GUT (portal module; the 1L mu0 = 173.10 row reproduces the superseded "
        "commit-5f25846 value)",
        "",
        f"- lambda_eff(M_GUT) required: 1L (mu0 173.10) `{required['1L_mu0_173.10']:.4f}`, 2L `{required['2L']:.4f}`, "
        f"3L `{required['3L+4QCD']:.4f}`: negative, so the tuned point is not a tree-level local minimum.",
        f"- lambda_eff(M_GUT) = 0 would give m_h(tree) = `{zero['m_h_tree_GeV']:.1f}` GeV "
        f"(scaled `{zero['M_h_scaled_to_buttazzo_GeV']:.1f}` GeV) at two loops; lambda_SM(M_GUT) >= 0 needs M_t < "
        f"`{bound['Mt_max_for_lambda_SM_M_GUT_nonnegative_GeV']['2L']:.2f}` GeV (2L).",
        "",
        f"Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed. "
        "G3: `OPEN`; whole model: neither validated nor excluded.",
        "",
        "## Scope",
        "",
    ]
    lines += [f"- {item}" for item in report["scope"]]
    lines.append("")
    return "\n".join(lines)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
