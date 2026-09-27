#!/usr/bin/env python3
"""G6 remnant RG no-go on the SOS-certified witness family (v20; evidence only: G6 stays OPEN).

User decision of 2026-09-26 ("G6: OPEN + no-go module").  The exact G6 tree certificate
(g6_sm_pati_salam_tree_spectrum_v20: 35 zero, 451 positive and 0 negative Hessian levels for all r0, x0, eps > 0) is a
statement about the tree-level Hessian at mu = M_GUT.  The light 126bar remnants are the Delta_R = (10bar,1,3)
multiplets of the Pati-Salam EFT below M_GUT; their physical spectrum needs the quartics run down to mu ~ v_R.  This
module records that G6 is NOT CLOSABLE ON THE SOS WITNESS FAMILY at one loop.  Checks are separated by kind:

  (A) group_theory (EXACT; integers and Fractions).  An integer model of Delta_R inside V = 4bar (x) 4bar (x) 3
      (symmetric in the two 4bar slots; gl(4) basis E_ij acting as -E_ji, Cartesian so(3) for SU(2)_R): the five
      Pati-Salam irreps of Sym^2(Delta_R) by Lagrange projectors in the pair Casimirs (dimensions 20, 35, 135, 100, 175),
      the SM-singlet vacuum D0 (9 broken generators), exact SM labels, the tree mass matrix A (m^2/v^2 = A lambda, rows
      of the six remnant multiplets summing to 0), the exact Fierz vectors of the exchange channels, the 210 channel
      content, and the one-loop beta functions as exact rationals (effective-potential route, Landau gauge; the same
      code path reproduces the SM Higgs beta function as an exact identity).
  (B) chart_binding (EXACT).  The restriction c_qk of the four SO(10) 126bar self-quartics I_q to Delta_R, computed in
      the repository's own 126bar chart with the integer projector routine that certifies sigma_std
      (g3_sm_pati_salam_candidate_v20._integer_projected_pairs), on an exact Krylov basis of Delta_R generated from
      sigma_std; the witness Phi-Sigma portal squares annihilate Delta_R exactly (no 210 exchange at the witness).
  (C) matching (EXACT; sympy).  Tree matching at mu = M_GUT: lambda(w, beta) = (1/8) sum_q w_q c_q - sum_c beta_c f_c
      gives lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3) >= 0 on the SOS cone
      W_SOS = {w_q >= w_2772} x {beta >= 0}; the witness reproduces the committed G6 tree levels exactly.
  (D) running (FLOAT, recomputed deterministically; fixed-step RK4, scipy linprog/HiGHS for the LP margins).  The PS
      two-loop gauge profiles are rebuilt from recorded boundary values; the witness quartics run tachyonic (lambda5 = 0
      between M_GUT and v_R) and non-perturbative above v_R; the best research region points need lambda4 - lambda5 < 0
      at M_GUT, i.e. anti-SOS weights; no point of a 2560-point SOS-safe grid runs perturbatively to v_R with a tree
      vacuum.  The margins with the research one-loop M_GUT threshold are pinned for both coupling pairings
      (record-only; declared not robust).  The float pins are regression tolerances against the module's own
      discretisation; its accuracy is estimated against a joint gauge + quartic RK4 without interpolation.
  (E) one_loop_masses (FLOAT, recomputed).  One-loop FJ R_xi pole masses (ported from the research polemass.py /
      eft_pole.py) at the three best region points for xi in {0, 0.5, 1, 3, 10} with their xi independence, the
      vev-fixed Landau masses VF_L and the FJ vev shifts, and Landau-gauge p = 0 vev-fixed Coleman-Weinberg curvature
      masses (cross-checked against the independent skeptic record).
  (F) research_record (RESEARCH_RECORD, not re-derived).  The region scan itself (1.5M sampled points per profile in
      a finite IR box), region volume, tuning, the renormalisation-scale variation of the pole masses and the
      400-point matching LP are recorded with script names and sha256 of the research JSONs (scratch outputs of
      2026-09-26, not in the repository; hashes for audit only).
  (G) scope.

Honest scope:
  * a no-go for the SOS-certified witness FAMILY only (the committed degree-2 SOS certificate with 126bar self weights
    in W_SOS = {w_54, w_1050bar, w_4125 >= w_2772 > 0}; the witness w = (2, 2, 1, 17/16) is strictly inside, the
    pre-swap historical weights (2, 2, 17/16, 1) are outside), at one loop, with the stated approximations: tree
    matching of the Delta_R EFT at mu = M_GUT plus any tree 210 exchange (beta_c >= 0), one-loop quartic running with
    two-loop PS gauge profiles;
  * only the tree-matching statement is robust.  The one-loop M_GUT threshold is research-recorded, computed at the
    witness only and ASSUMED WEIGHT INDEPENDENT (NOT VERIFIED); it shifts lambda4 - lambda5 by about -0.57 (gX = g),
    which removes the lambda4 >= lambda5 obstruction; the remaining separation is marginal (0.042 at rho = 1e3; it
    closes at 1.2 to 1.73 times the recorded threshold) and depends on the coupling at which the threshold is taken;
  * the one-loop-positive region is a sampled, box-bounded research scan: its lambda4 - lambda5 < 0 at M_GUT is a
    sampling statement, not a proof over all couplings;
  * it does NOT show that G6 is impossible in the contract: an anti-SOS G3 witness (outside degree-2 SOS
    certification) might exist.  Closing G6 would need controlled (weight-dependent) M_GUT thresholds and two-loop
    quartic running and, unless those thresholds open an SOS-safe route, an anti-SOS G3 witness;
  * it does NOT change G3/G4: their closures are tree-level statements and remain true; G5 is unchanged;
  * the G6 tree certificate stays exact but is scoped to tree level at mu = M_GUT; below M_GUT the certified witness is
    tachyonic at the physical hierarchy.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import time
from collections.abc import Callable, Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy
from scipy import sparse
from scipy.optimize import linprog

import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import g3_sm_pati_salam_candidate_v20 as candidate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G6_SM_PATI_SALAM_REMNANT_RG_NOGO_V20.json"
OUT_MD = ROOT / "G6_SM_PATI_SALAM_REMNANT_RG_NOGO_V20.md"
G6_TREE_JSON = ROOT / "G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json"
G6_TREE_STATUS = "G6_SM_PATI_SALAM_TREE_SPECTRUM_EXACT__TREE_LEVEL_ONLY__NOT_WIRED"  # read-only binding
MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_RECORDED = "G6_SM_PATI_SALAM_REMNANT_RG__NOT_CLOSABLE_ON_SOS_WITNESS_FAMILY__G6_OPEN"
STATUS_INCOMPLETE = "G6_SM_PATI_SALAM_REMNANT_RG_NOGO_NOT_ESTABLISHED__G6_OPEN"
OVERALL_STATE_RECORDED = "SOS_WITNESS_FAMILY_TREE_MATCHING_DISJOINT_FROM_ONE_LOOP_REMNANT_REGION__G6_OPEN"
OVERALL_STATE_OPEN = "G6_REMNANT_RG_NOGO_NOT_ESTABLISHED"
TREE_CERTIFICATE_SCOPE = "tree level at mu = M_GUT"
EXPECTED_N_CHECKS = 58
DIGITS = 12
EXPECTED_SECTION_COUNTS = {
    "group_theory": 17,
    "chart": 9,
    "matching": 9,
    "running": 13,
    "one_loop": 6,
    "research_record": 3,
    "scope": 1,
}

# ---------------------------------------------------------------------------------------------------------------------
# Conventions and pinned exact values (sections A-C).
# ---------------------------------------------------------------------------------------------------------------------

QUARTIC_BASIS = ("(20',1)", "(35,1)", "(45,3)", "(20',5)", "(35,5)")
QUARTIC_CASIMIRS = {"(20',1)": (6, 0), "(35,1)": (12, 0), "(45,3)": (8, 2), "(20',5)": (6, 6), "(35,5)": (12, 6)}
QUARTIC_DIMENSIONS = (20, 35, 135, 100, 175)
C4_VALUES = (6, 8, 12)
CR_VALUES = (0, 2, 6)
# Chart pair operators K4 = sum_{so(6)} t (x) t and KR = sum_J J (x) J (t = sqrt2 i T, J = 2 i T_R):
# K4 = 9 - C_pair, KR = 8 - 2 C_pair on Sym^2(Delta_R).
K4_EIGEN = {6: 3, 8: 1, 12: -3}
KR_EIGEN = {0: 8, 2: 4, 6: -4}
STATE_ORDER = ("(6,1)_4/3", "(1,1)_2", "(3,1)_1/3", "(6,1)_1/3", "(3,1)_4/3", "(6,1)_2/3", "(1,1)_0 radial")
G6_LABELS = (
    "(6,1)_|Y|=4/3",
    "(1,1)_|Y|=2",
    "(3,1)_|Y|=1/3",
    "(6,1)_|Y|=1/3",
    "(3,1)_|Y|=4/3",
    "(6,1)_|Y|=2/3",
    "(1,1)_|Y|=0",
)
# (symmetric 4 x 4 unit tensor on the 4bar index pair, T3R eigenvalue of the SU(2)_R triplet vector)
STATE_DIRECTIONS = {
    "(6,1)_4/3": ((0, 0), -1),
    "(1,1)_2": ((3, 3), 1),
    "(3,1)_1/3": ((0, 3), 0),
    "(6,1)_1/3": ((0, 0), 0),
    "(3,1)_4/3": ((0, 3), 1),
    "(6,1)_2/3": ((0, 0), 1),
    "(1,1)_0 radial": ((3, 3), -1),
}
GOLDSTONE_DIRECTIONS = {"(1,1)_1": ((3, 3), 0), "(3,1)_2/3": ((0, 3), -1)}
# Cartesian T3R = i L_3 eigenvectors as Gaussian integers (re, im): v_{+1} = (1, i, 0), v_{-1} = (1, -i, 0), v_0 = e_3.
T3R_VECTORS = {1: ((1, 0), (0, 1), (0, 0)), -1: ((1, 0), (0, -1), (0, 0)), 0: ((0, 0), (0, 0), (1, 0))}
EXPECTED_STATE_Y = ("-4/3", "2", "1/3", "-1/3", "4/3", "2/3", "0")
EXPECTED_STATE_C3 = ("10/3", "0", "4/3", "10/3", "4/3", "10/3", "0")
EXPECTED_STATE_REAL_DIMS = (12, 2, 6, 12, 6, 12, 1)
EXPECTED_TREE_MATRIX = (
    ("0", "0", "0", "4/3", "-4/3"),
    ("0", "4/3", "0", "0", "-4/3"),
    ("0", "0", "1", "0", "-1"),
    ("0", "0", "1", "2/3", "-5/3"),
    ("0", "2/3", "1", "0", "-5/3"),
    ("4/9", "2/9", "1", "2/9", "-17/9"),
    ("0", "0", "0", "0", "4"),
)
FIERZ_CHANNELS = ("(1,1,1)", "(15,1,1)", "(1,1,3)", "(15,1,3)")
EXCHANGE_CHANNELS = ("(1,1,1)", "(15,1,1)", "(15,1,3)")
EXPECTED_FIERZ = {
    "(1,1,1)": ("1", "1", "1", "1", "1"),
    "(15,1,1)": ("-3/2", "3/2", "-1/2", "-3/2", "3/2"),
    "(1,1,3)": ("-2", "-2", "-1", "1", "1"),
    "(15,1,3)": ("3", "-3", "1/2", "-3/2", "3/2"),
}
# Pati-Salam content of the 210 (SU(4)_c, SU(2)_L, SU(2)_R); Delta_R^dag Delta_R = (10 x 10bar, 1, 3 x 3).
PS_CONTENT_210 = (
    ("1", "1", "1"),
    ("15", "1", "1"),
    ("6", "2", "2"),
    ("15", "3", "1"),
    ("15", "1", "3"),
    ("10", "2", "2"),
    ("10bar", "2", "2"),
)
PS_DIMENSIONS = {"1": 1, "2": 2, "3": 3, "5": 5, "6": 6, "10": 10, "10bar": 10, "15": 15, "84": 84}
DELTA_BILINEAR_SU4 = ("1", "15", "84")  # 10 x 10bar
DELTA_BILINEAR_SU2R = ("1", "3", "5")  # 3 x 3
EXPECTED_Q = {
    (0, 0): ("124/27", "32/27", "-32/81", "16/27", "32/27"),
    (0, 1): ("112/27", "32/27", "-224/81", "112/27", "32/27"),
    (0, 2): ("-16/3", "-32/3", "16/3", "8/3", "16/3"),
    (0, 3): ("160/27", "320/27", "160/81", "16/27", "32/27"),
    (0, 4): ("560/27", "160/27", "560/81", "56/27", "16/27"),
    (1, 1): ("28/27", "200/27", "-140/81", "28/27", "92/27"),
    (1, 2): ("-56/3", "-40/3", "28/3", "28/3", "20/3"),
    (1, 3): ("560/27", "160/27", "560/81", "56/27", "16/27"),
    (1, 4): ("280/27", "920/27", "700/81", "28/27", "92/27"),
    (2, 2): ("18", "18", "4", "18", "18"),
    (2, 3): ("40/3", "80/3", "80/3", "16/3", "32/3"),
    (2, 4): ("140/3", "100/3", "140/3", "56/3", "40/3"),
    (3, 3): ("40/27", "80/27", "160/81", "292/27", "368/27"),
    (3, 4): ("280/27", "80/27", "1120/81", "1288/27", "368/27"),
    (4, 4): ("70/27", "230/27", "700/81", "322/27", "1166/27"),
}
GAUGE_MONOMIALS = ("g4^4", "gR^4", "g4^2gR^2")
EXPECTED_G = {
    "g4^4": ("9/2", "45/2", "-3/2", "9/2", "45/2"),
    "gR^4": ("18", "18", "3", "9", "9"),
    "g4^2gR^2": ("36", "-36", "6", "-18", "18"),
}
O60_POINT_SUM = 136  # 2 (N + 8), N = 60 real components
WITNESS_LAMBDA = ("989/4480", "17/128", "53/288", "17/128", "1/8")
WITNESS_LEVELS = ("1/96", "1/96", "17/288", "37/576", "37/576", "353/3360", "1/2")
WITNESS_GAUGE_SQUARED = ("9/25", "1/4")  # g4 = 3/5, gR = 1/2 (the research D2 / skeptic reference point)
EXPECTED_WITNESS_BETA16 = (
    "540798191/211680000",
    "111806803/338688000",
    "-10773671491/10160640000",
    "-1491898817/1693440000",
    "3310549871/677376000",
)
SELF_CHANNELS = tuple(candidate.SELF_CHANNELS)  # ("54", "1050bar", "2772bar", "4125")
EXPECTED_CQK = {
    "54": ("9/35", "0", "0", "0", "0"),
    "1050bar": ("1/2", "0", "4/9", "0", "0"),
    "2772bar": ("1/10", "0", "1/9", "0", "1"),
    "4125": ("1/7", "1", "4/9", "1", "0"),
}
EXPECTED_SWAPPED_WEIGHTS = {"54": "2", "1050bar": "2", "2772bar": "1", "4125": "17/16"}
EXPECTED_HISTORICAL_WEIGHTS = {"54": "2", "1050bar": "2", "2772bar": "17/16", "4125": "1"}
SOS_CONE_ROWS = ("54", "1050bar", "4125")  # w_2772 - w_q <= 0
LCG_SEED_GROUP = 20260926
LCG_SEED_CHART = 1000
GF_PRIME = 998244353
EXACT_FLOAT_BOUND = float(2**52)  # float64 carries integer arithmetic exactly while every partial sum is below this
INT64_BOUND = 2**62

# ---------------------------------------------------------------------------------------------------------------------
# Research-recorded inputs and pinned float values (sections D-F).
# ---------------------------------------------------------------------------------------------------------------------

PROFILE_TAGS = ("rho1e3", "rho1e4", "no_spec")
PROFILE_INPUTS = {
    "rho1e3": {
        "M_I": 1223911937.8488863,
        "M_GUT": 1.62622714179438e17,
        "rho": 1000.0,
        "y_MI": (26.551935405254966, 37.74036133618748, 61.656650195569895, 0.5816952070500827),
    },
    "rho1e4": {
        "M_I": 2775021134.413371,
        "M_GUT": 1.1245259351866925e17,
        "rho": 10000.0,
        "y_MI": (27.485590445812672, 38.14705635482525, 60.15500599061282, 0.5724139554383538),
    },
    "no_spec": {
        "M_I": 4870634643.848149,
        "M_GUT": 8.389303509454094e16,
        "y_MI": (28.12670975121436, 38.42663234074447, 59.12245346745631, 0.566250341320957),
    },
}
PROFILE_SUMMARIES = {
    "rho1e3": {
        "g_vR": (0.6879499454920116, 0.5770346665282832, 0.45145552159918684),
        "g_MGUT": (0.7737703882513763, 0.7897089501474092, 0.7867064557520829),
        "alpha_inv_U": 23.78391793631131,
    },
    "rho1e4": {
        "g_vR": (0.6761645480438538, 0.5739504709048532, 0.4570556109315572),
        "g_MGUT": (0.6585586357623028, 0.6704775835878615, 0.6683722868032554),
        "alpha_inv_U": 32.31569257759096,
    },
    "no_spec": {
        "g_vR": (0.668413890051069, 0.5718587484398723, 0.4610294918909248),
        "g_MGUT": (0.5141880720726201, 0.5214441691598797, 0.5202320748408694),
        "alpha_inv_U": 49.32425167130797,
    },
}
# PyR@TE two-loop PS coefficients (research U2, models.U2PS and delta_PS_spectators), exact rationals.
PS_GAUGE_COEFFICIENTS = {
    "order": ("SU4c", "SU2L", "SU2R"),
    "b": ("-23/3", "-3", "11/3"),
    "b_ij": (("643/6", "9/2", "153/2"), ("45/2", "8", "3"), ("765/2", "3", "584/3")),
    "c_Y": ("4", "4", "4"),
    "spectator_b": ("40/3", "40/3", "40/3"),
    "spectator_b_ij": (("1025/3", "15", "15"), ("75", "490/3", "0"), ("75", "0", "490/3")),
}
REGION_POINTS = {
    "rho1e3": (-0.045758787127761935, 0.10217708894106708, 0.1194735896276812, 0.08559785904921019, 0.022422096880318484),
    "rho1e4": (-0.11172701398279583, 0.17805599665690988, 0.13984409218858637, 0.10004735565833173, 0.02802765488133831),
    "no_spec": (0.05423553050978447, 0.125585318667933, 0.13367156929872168, 0.10124744506010513, 0.027610522474726784),
}
GUT_THRESHOLDS = {
    "alphainv23.78_gX1.0": (-0.19297447938490625, -0.09814759198486722, -0.01359127369076701, 0.017103294497563242, 0.587801966369927),
    "alphainv23.78_gX0.0": (0.03489753770405653, -0.16918689808917078, 0.015006728053717368, -0.05393564856381076, 0.21785356112663473),
    "alphainv40.0_gX1.0": (-0.030021232916049655, -0.1479853400276115, 0.009456570082212306, -0.030778634135968517, 0.33886428078046904),
    "alphainv40.0_gX0.0": (0.040763686676398965, -0.1711422860678133, 0.017613900769211686, -0.05393564845488634, 0.22176432188427492),
}
THRESHOLD_PAIRING = {"rho1e3": "alphainv23.78", "rho1e4": "alphainv40.0", "no_spec": "alphainv40.0"}
# Standard alpha^-1 = 4 pi / g^2 at which d12 computed each threshold (d12_matching.py: gstd = sqrt(4 pi / alpha_inv)).
THRESHOLD_ALPHA_INV = {"alphainv23.78": 23.78, "alphainv40.0": 40.0}
THRESHOLD_PAIRINGS = tuple(THRESHOLD_ALPHA_INV)
GX_VALUES = ("gX1.0", "gX0.0")
RESEARCH_SLACK = 0.03  # the research D21 matching slack
PROFILE_M_X = {"rho1e3": 8.358521049654704e16, "rho1e4": 4.958526930551065e16, "no_spec": 2.994232971214522e16}
# The float pins below are REGRESSION tolerances against this module's own discretisation (np.interp of the tabulated
# gauge profile, as in the research and skeptic codes); running.accuracy_estimate measures the method error.
TOLERANCE_SEMANTICS = (
    "regression tolerances against this module's own discretisation (RK4 on np.interp of the tabulated gauge profile, "
    "the research and skeptic method, so the research comparisons are like for like), not accuracy statements; the "
    "method error is measured in running.accuracy_estimate against a joint gauge + quartic RK4 without interpolation "
    "(about 2e-6 absolute in lambda(M_GUT), 1e-6 in lambda4 - lambda5 and 1e-5 relative in the lambda5 crossing)"
)
FLOAT_TOLERANCES = {
    "profile_rel": 1.0e-9,
    "crossing_rel": 1.0e-5,
    "blowup_rel": 2.0e-2,
    "lambda_gut_abs": 1.0e-6,
    "gap_abs": 1.0e-6,
    "tree_levels_abs": 1.0e-9,
    "tree_slack_abs": 1.0e-6,
    "half_gap_abs": 1.0e-7,
    "threshold_slack_abs": 1.0e-5,
    "threshold_scale_abs": 2.0e-3,
    "bfb_only_slack_abs": 1.0e-9,
    "beta_rel": 1.0e-12,
    "cw_mass_abs": 1.0e-6,
    "pole_xi_spread_abs": 1.0e-12,
    "pole_research_abs": 1.0e-9,
    "research_lambda_gut_abs": 1.0e-6,
    "research_crossing_rel": 3.0e-2,
}
# Accuracy budget of the primary running against the joint reference (an order of magnitude above the measured
# method error and far below every margin used, >= 0.1 in lambda4 - lambda5).
ACCURACY_BUDGET = {
    "lambda_gut_abs": 1.0e-5,
    "gap_abs": 1.0e-5,
    "crossing_rel": 5.0e-5,
    "reference_convergence_abs": 1.0e-9,
    "reference_convergence_rel": 1.0e-9,
}
JOINT_REFERENCE_STEPS = (0.02, 0.01)
EXPECTED_CROSSING_GEV = {"rho1e3": 4.68087527e16, "rho1e4": 1.17115647e16, "no_spec": 1.21018326e15}
EXPECTED_BLOWUP_GEV = {
    "rho1e3": {"4pi": 4.02e13, "1e3": 3.01e13},
    "rho1e4": {"4pi": 1.36e12, "1e3": 1.03e12},
    "no_spec": {"4pi": 5.64e10, "1e3": 4.36e10},
}
EXPECTED_LAMBDA_GUT = {
    "rho1e3": (0.559600253, 0.242978937, 0.242113810, 0.156283237, 0.572370727),
    "rho1e4": (0.499487524, 0.282478070, 0.274845499, 0.208034189, 0.520156065),
    "no_spec": (0.461447654, 0.285492692, 0.279987734, 0.226344633, 0.471166497),
}
EXPECTED_GAP_GUT = {"rho1e3": -0.4160875, "rho1e4": -0.3121219, "no_spec": -0.2448219}
EXPECTED_TREE_LEVELS_VR = {  # A lambda(v_R) at the recorded region points (d22 best_core.tree agrees for rho1e3)
    "rho1e3": (0.0842343495585, 0.106339989414, 0.0970514927474, 0.139168667527, 0.150221487455, 0.0985112674615, 0.0896883875213),
    "rho1e4": (0.0960262677027, 0.200037789034, 0.111816437307, 0.159829571159, 0.211835331824, 0.0990472606015, 0.112110619525),
    "no_spec": (0.0981825634472, 0.130633061591, 0.106061046824, 0.155152328548, 0.171377577619, 0.156030321235, 0.110442089899),
}
EXPECTED_TREE_SLACK = {"rho1e3": 0.208044, "rho1e4": 0.156061, "no_spec": 0.122411}
# D08 (record-only): min LP slack with the research threshold subtracted, for BOTH coupling pairings.
EXPECTED_THRESHOLD_SLACK = {
    "rho1e3": {"alphainv23.78": {"gX1.0": 0.041547, "gX0.0": 0.091365}, "alphainv40.0": {"gX1.0": 0.075708, "gX0.0": 0.091365}},
    "rho1e4": {"alphainv23.78": {"gX1.0": 0.020135, "gX0.0": 0.069954}, "alphainv40.0": {"gX1.0": 0.054297, "gX0.0": 0.069954}},
    "no_spec": {"alphainv23.78": {"gX1.0": 0.003820, "gX0.0": 0.053639}, "alphainv40.0": {"gX1.0": 0.037981, "gX0.0": 0.053639}},
}
EXPECTED_THRESHOLD_SCALE = {"slack_le_research": 1.2037, "slack_zero": 1.7328, "gX0_min_slack": 0.043198}
THRESHOLD_SCALE_MAX_GX0 = 8.0
D11_GRID = {
    "w_2772bar": ("1/2", "1", "2", "4", "8"),
    "w_q_minus_w_2772bar": ("0", "1", "4", "12"),
    "beta": ("0", "1/10"),
    "rk4_steps": 800,
    "blow_up_cap": 1.0e3,
}
EXPECTED_D11_NOT_BLOWN_UP = {"rho1e3": 0, "rho1e4": 0, "no_spec": 4}
RUN_STEPS = 2000
BISECTIONS = 60
PROFILE_STEP = 0.05
PROFILE_TOP_MARGIN = 0.1
CW_STEP = 2.0e-3
FOUR_PI = 4.0 * math.pi
# One-loop FJ R_xi pole masses (section E).
POLE_XIS = (0.0, 0.5, 1.0, 3.0, 10.0)
POLE_FD_STEP = 0.5  # exact: the quartic Hessian is quadratic in the field
POLE_IR_REGULATOR = 1.0e-9  # massless (unbroken) vectors get M^2 = reg x scale, as in the research code
POLE_DV_MAX = 0.2  # the research controlled-core bound on the FJ vev shifts |dv/v|

RESEARCH_PROVENANCE_NOTE = (
    "scratch research outputs of 2026-09-26 (study D-D, wfDA/D and wfDA/review); not in the repository; hashes "
    "recorded for audit only and not verifiable from the repository"
)
RESEARCH_FILES = {
    "d20_summary.json": ("d20_summary.py", "df5087df4e5bc27999bb2f310d48e2314533879326a9d64f60d13476207fe607"),
    "d19_witness_sos.json": ("d19_witness_sos.py", "5c9f15c0b013be5e53844d00d10798d046e196fd087c16f19432f97f334c7022"),
    "d12_matching.json": ("d12_matching.py", "f35ae578794cb7feb42ba34f11e5a366610eb0caa06bc30361b61a30607b6c37"),
    "d21_threshold_matching.json": ("d21_threshold_matching.py", "2a8305720493b145c881a847caec919d3899958253caa4db4c879e1e3cfbdb20"),
    "d13_region_rho1e3.json": ("d13_region_prod.py", "baf89f1118c1c75538b2522310ef5b619914e4f13cc5d51e05f7b06c1b103e3d"),
    "d13_region_rho1e4.json": ("d13_region_prod.py", "7a24d52cbb540a09aae0836b41e3b1f2d892d106ee01aeeb578cce33098beba6"),
    "d13_region_no_spec.json": ("d13_region_prod.py", "3e6c32f9e0ce8c5b5367c7a3d81ad526430db88e4c55614db8332967896d1796"),
    "d18_tuning_rho1e3.json": ("d18_tuning.py", "361388aa9f5eccc2cf79e7573a1e83ad3bd755caa51a499ddb696c86163b05d0"),
    "d22_controlled_rho1e3.json": ("d22_controlled.py", "0f36280f9ecd528ecf3e3b9609f049ba9788389a22bec7b83c8ff4e6bdc37d7d"),
    "d22_controlled_rho1e4.json": ("d22_controlled.py", "29025a73ddc8a891fcb91a1e929963f4dcab43948a74f4ebf8dfa88935907af6"),
    "d22_controlled_no_spec.json": ("d22_controlled.py", "6e89e32edbbde23bfd9ae512ec77835535af7a5920b989f3000f34d77310935a"),
    "d9_validate_pole.json": ("d9_validate_pole.py", "b5855269ff5cfec12f8716696e88ed73a89dd5d720bcf2245a04b31f2f35b868"),
    "d5_unitarity.json": ("d5_unitarity.py", "d816b2dbf4fee195c89daef5ba55135a26dae5fa7b01c055c2d9950157eea8be"),
    "d15_majorana.json": ("d15_majorana.py", "aebcfef3fbfee7dc2873512cb07e078caf8902cfec136871a2c5cfd52c261d95"),
    "d16_portals_f.json": ("d16_portals_f.py", "2d376a514ff698b81a37056ccc54b36fb74c0639b144f3adcfcee728c0db5727"),
    "d23_box_extension_rho1e3.json": ("d23_box_extension.py", "0708eb0407f21c8b309e928c03934e8fb7c8cfbb2c2a85d067f9bb8a2c8d2735"),
    "d23_box_extension_no_spec.json": ("d23_box_extension.py", "353cf488c6ee9bc477695bd3966ee8d8c54d56d6d6773ebd6f087cc74838a1dc"),
    "profiles.json": ("d6_profiles.py", "d253ca54be7e905d65920e0b98f973089a4a9fd37d3a387b4094cbc66063d4ec"),
    "profiles.pkl": ("d6_profiles.py", "db86478396d7fee4ff25b52c8d43545c333301ff7bb6222f8bf4e68c193ec136"),
    "u2_coefficients.json": ("wfGNG/U2 (PyR@TE)", "03f361ed4a91c506891211eb6bc66c753d7c50180095f63c43ce4fcdee8d60a3"),
    "r_d_indep.json": ("r_d_indep.py (skeptic)", "663c8b15e85328a14512782e00856e3f1706c03a1e5abaf4e49dfd9edd7a9d79"),
    "r_d_running.json": ("r_d_running.py (skeptic)", "983b579879c7184bcdab66c7d831603504499b95310d90cd252d0599de227a2e"),
    "wfDA_review.md": ("skeptic review, part D", "8e1ac0bd123f4850e2eb7fb37da6e5f51e34a33345bdde45543a3c818029148a"),
}
# Research FJ R_xi pole masses (m^2 / v_R^2 at Q = v_R) of the best controlled points (d20_summary.json
# [tag].best_controlled.{pole_by_xi, tree, VF_L}): the reference of the recomputed section E.
BEST_CONTROLLED_POLE_REFERENCE = {
    "rho1e3": {
        "pole_by_xi": {
            "0.0": (0.12947755778136857, 0.14599318377097517, 0.1283984801005008, 0.21038251933311758, 0.21252720399683434, 0.15251228830706784, 0.18129197626503635),
            "0.5": (0.12947755778137407, 0.1459931837709787, 0.12839848010050298, 0.21038251933312238, 0.21252720399683656, 0.1525122883070707, 0.18129197626503635),
            "1.0": (0.12947755778136968, 0.14599318377097553, 0.12839848010049987, 0.21038251933311722, 0.21252720399683453, 0.1525122883070715, 0.18129197626503632),
            "3.0": (0.1294775577813686, 0.1459931837709755, 0.1283984801005013, 0.21038251933312174, 0.2125272039968365, 0.15251228830707056, 0.1812919762650347),
            "10.0": (0.1294775577813701, 0.14599318377097298, 0.12839848010050192, 0.21038251933311994, 0.21252720399684247, 0.15251228830707336, 0.18129197626521987),
        },
        "tree": (0.08423434955852208, 0.10633998941433152, 0.09705149274736252, 0.13916866752662355, 0.1502214874545283, 0.09851126746146888, 0.0896883875212739),
        "VF_L": (0.09975619618138643, 0.10847203836549076, 0.09415470039684706, 0.16127805882947277, 0.15952285159043933, 0.11775343972285086, 0.14964620454827093),
    },
    "rho1e4": {
        "pole_by_xi": {
            "0.0": (0.14738211083904496, 0.27959290498039735, 0.1498884874480522, 0.2408388136002295, 0.3021703413964068, 0.1533850702734966, 0.20014623017263805),
            "0.5": (0.14738211083904829, 0.2795929049804042, 0.14988848744805203, 0.24083881360022413, 0.3021703413963988, 0.15338507027349707, 0.200146230172638),
            "1.0": (0.14738211083904829, 0.2795929049804131, 0.14988848744805258, 0.24083881360023277, 0.302170341396404, 0.1533850702734991, 0.20014623017263805),
            "3.0": (0.14738211083904723, 0.27959290498041256, 0.1498884874480534, 0.24083881360023424, 0.30217034139640053, 0.15338507027349846, 0.20014623017263705),
            "10.0": (0.14738211083904873, 0.2795929049804039, 0.14988848744805497, 0.24083881360023182, 0.3021703413963968, 0.15338507027350004, 0.20014623017263466),
        },
        "tree": (0.09602626770265768, 0.2000377890340955, 0.11181643730724786, 0.15982957115857668, 0.21183533182429579, 0.09904726060153583, 0.1121106195253532),
        "VF_L": (0.11356746911353668, 0.2091516983233288, 0.1105135033210472, 0.1845565086104716, 0.22757475394085638, 0.1185066176244265, 0.1606676528669615),
    },
    "no_spec": {
        "pole_by_xi": {
            "0.0": (0.15200134544409027, 0.18465986376461052, 0.14410733449679974, 0.23635702722599228, 0.24728227104640937, 0.2403289438851111, 0.196101031141994),
            "0.5": (0.15200134544409205, 0.1846598637646119, 0.1441073344968, 0.23635702722599805, 0.2472822710464108, 0.2403289438851231, 0.19610103114199395),
            "1.0": (0.15200134544409186, 0.1846598637646156, 0.14410733449679747, 0.23635702722598823, 0.24728227104640874, 0.24032894388511322, 0.19610103114199395),
            "3.0": (0.1520013454440877, 0.1846598637646119, 0.14410733449679977, 0.23635702722599555, 0.24728227104640904, 0.24032894388511244, 0.19610103114199443),
            "10.0": (0.15200134544409086, 0.1846598637646202, 0.14410733449680038, 0.23635702722599547, 0.24728227104640993, 0.24032894388512455, 0.19610103114191707),
        },
        "tree": (0.0981825634471709, 0.13063306159094165, 0.1060610468239947, 0.15515232854758015, 0.17137757761946562, 0.15603032123481658, 0.11044208989890708),
        "VF_L": (0.11574797289412041, 0.1364243229218873, 0.1049448752112527, 0.17906788166545773, 0.18400204133949977, 0.18271560434482725, 0.15532089575209965),
    },
}
REGION_SCAN_BOX = {"lo": (-0.8, -0.1, -0.1, -0.1, 0.0), "hi": (0.8, 0.8, 0.35, 0.45, 0.08)}
REGION_SCAN_PREFILTER = {"rho1e3": 978514, "rho1e4": 979077, "no_spec": 978576}


def _record(label: str, value: Any, meaning: str, source_json: str, key: str) -> dict[str, Any]:
    script, sha = RESEARCH_FILES[source_json]
    return {
        "label": label,
        "value": value,
        "meaning": meaning,
        "source_script": script,
        "source_json": source_json,
        "key": key,
        "source_json_sha256": sha,
        "reproducible_from_repository": False,
    }


_IN = "RESEARCH_RECORD_INPUT"
_REC = "RESEARCH_RECORD"
RESEARCH_RECORD: dict[str, dict[str, Any]] = {
    # ---- inputs of the recomputed float sections
    "profile_scales": _record(
        _IN,
        {tag: {key: value for key, value in PROFILE_INPUTS[tag].items() if key != "y_MI"} for tag in PROFILE_TAGS},
        "M_I = v_R, M_GUT and the spectator ratio rho = M_s/v_R of the three PS profiles (no_spec: no spectators)",
        "profiles.json",
        "<tag>.{M_I, M_GUT, rho}",
    ),
    "profile_boundary_values": _record(
        _IN,
        {tag: list(PROFILE_INPUTS[tag]["y_MI"]) for tag in PROFILE_TAGS},
        "(alpha_4^-1, alpha_L^-1, alpha_R^-1, y_PS) at t = ln M_I: the only boundary data of the rebuilt profiles",
        "profiles.pkl",
        "<tag>.y[0]",
    ),
    "profile_summaries": _record(
        _IN,
        {tag: {key: (list(value) if isinstance(value, tuple) else value) for key, value in PROFILE_SUMMARIES[tag].items()} for tag in PROFILE_TAGS},
        "research gauge couplings (g4, gL, gR) at v_R and at M_GUT and alpha_U^-1 (reference values of D01)",
        "d19_witness_sos.json",
        "<tag>.profile.{g_vR, g_MGUT, alpha_inv_U}",
    ),
    "profile_M_X": _record(
        _IN,
        dict(PROFILE_M_X),
        "gauge-unification scale M_X of each profile (where alpha_U^-1 is read off); used only for the M_GUT/M_X "
        "disclosure of the threshold coupling pairing",
        "profiles.json",
        "<tag>.M_X",
    ),
    "ps_gauge_coefficients": _record(
        _IN,
        {key: (list(value) if not isinstance(value, tuple) or not isinstance(value[0], tuple) else [list(row) for row in value]) for key, value in PS_GAUGE_COEFFICIENTS.items() if key != "order"},
        "two-loop PS gauge coefficients b, b_ij, c_Y and the universal spectator shifts (exact rationals)",
        "u2_coefficients.json",
        "models.U2PS, delta_PS_spectators",
    ),
    "region_points": _record(
        _IN,
        {tag: list(REGION_POINTS[tag]) for tag in PROFILE_TAGS},
        "best controlled points of the RG-improved one-loop remnant region, lambda at v_R (tree-positive, FJ and VF_L "
        "pole-positive, path-unitary, Delta-only EFT)",
        "d20_summary.json",
        "[tag].best_controlled.lam_vR",
    ),
    "gut_thresholds": _record(
        _IN,
        {key: list(value) for key, value in GUT_THRESHOLDS.items()},
        "one-loop M_GUT threshold dlambda of the Delta_R quartics, computed at the witness only (gX = g or 0)",
        "d12_matching.json",
        "threshold.<key>.dlam_threshold",
    ),
    # ---- heavy research statistics (not re-derived)
    **{
        f"region_scan_box_{tag}": _record(
            _REC,
            {
                "box_lo": list(REGION_SCAN_BOX["lo"]),
                "box_hi": list(REGION_SCAN_BOX["hi"]),
                "N_box": 1500000,
                "n_prefilter": REGION_SCAN_PREFILTER[tag],
                "prefilter_min_remnant_level": -0.1,
                "matching_slack_d_th": 0.02,
            },
            "the region scan is a sampled, box-bounded set: N_box uniform lambda(v_R) points in the IR box [box_lo, "
            "box_hi], a tree prefilter (all six remnant tree levels > -0.1 v_R^2) and the matching-LP slack d_th; its "
            "statistics (gap quantiles, 0 of 400 reachable) are sample statistics, not a proof over all couplings",
            f"d13_region_{tag}.json",
            "{box, N_box, n_prefilter, d_th}",
        )
        for tag in PROFILE_TAGS
    },
    "box_extension_rho1e3": _record(
        _REC,
        {
            "ext_box_lo": [-2.0, -0.1, -0.1, -0.1, 0.0],
            "ext_box_hi": [2.0, 1.6, 0.6, 0.7, 0.12],
            "N": 1500000,
            "n_tree_pos_path_unitary": 605,
            "share_inside_prod_box": 0.9966342653842164,
        },
        "box-truncation check (tree-positive path-unitary points as the region proxy): 99.7% of the |det J|-weighted UV "
        "volume of an extended box lies inside the production box at rho = 1e3; the sign of lambda4 - lambda5 at M_GUT "
        "of the points outside it was not recorded",
        "d23_box_extension_rho1e3.json",
        "{ext_box, N, n_tree_pos_path_unitary, share_inside_prod_box}",
    ),
    "box_extension_no_spec": _record(
        _REC,
        {
            "ext_box_lo": [-2.0, -0.1, -0.1, -0.1, 0.0],
            "ext_box_hi": [2.0, 1.6, 0.6, 0.7, 0.12],
            "N": 1500000,
            "n_tree_pos_path_unitary": 1359,
            "share_inside_prod_box": 0.9753385592649834,
        },
        "box-truncation check (tree-positive path-unitary points as the region proxy): 97.5% of the |det J|-weighted UV "
        "volume of an extended box lies inside the production box without spectators; the sign of lambda4 - lambda5 at "
        "M_GUT of the points outside it was not recorded",
        "d23_box_extension_no_spec.json",
        "{ext_box, N, n_tree_pos_path_unitary, share_inside_prod_box}",
    ),
    "best_controlled_pole_reference": _record(
        _REC,
        {
            tag: {
                "pole_by_xi": {xi: list(values) for xi, values in BEST_CONTROLLED_POLE_REFERENCE[tag]["pole_by_xi"].items()},
                "tree": list(BEST_CONTROLLED_POLE_REFERENCE[tag]["tree"]),
                "VF_L": list(BEST_CONTROLLED_POLE_REFERENCE[tag]["VF_L"]),
            }
            for tag in PROFILE_TAGS
        },
        "research FJ R_xi one-loop pole masses (m^2/v_R^2, Q = v_R) of the three best controlled points for xi in "
        "{0, 0.5, 1, 3, 10}, their tree levels and the vev-fixed Landau masses VF_L (reference of the recomputed "
        "one_loop pole checks)",
        "d20_summary.json",
        "[tag].best_controlled.{pole_by_xi, tree, VF_L}",
    ),
    "region_counts": _record(
        _REC,
        {
            "rho1e3": {"N_box": 1500000, "n_path_unitary": 83960, "region_pole": 8954, "region_FJ_and_VF_L": 8477, "region_pole_u_le_half": 0},
            "rho1e4": {"N_box": 1500000, "n_path_unitary": 124920, "region_pole": 17818, "region_FJ_and_VF_L": 17104, "region_pole_u_le_half": 155},
            "no_spec": {"N_box": 1500000, "n_path_unitary": 135409, "region_pole": 20254, "region_FJ_and_VF_L": 19510, "region_pole_u_le_half": 1225},
        },
        "box scan of lambda(v_R): path-unitary points, one-loop FJ pole-positive region, FJ and VF_L, and |a0| <= 1/4 (u <= 1/2)",
        "d20_summary.json",
        "[tag].{N_box, n_path_unitary, region_FJ, region_FJ_VF, region_u_le_half}",
    ),
    "region_fraction_of_V_pos": _record(
        _REC,
        {"rho1e3": 4.149543049430024e-08, "rho1e4": 1.0527264429465262e-06, "no_spec": 5.82387791665372e-06},
        "region volume as a fraction of the perturbative positive coupling volume (about 4e-8 at rho = 1e3)",
        "d20_summary.json",
        "[tag].tuning.region_fraction_of_V_pos",
    ),
    "UV_volume_region": _record(
        _REC,
        {"rho1e3": 1.158826289242125e-08},
        "region volume mapped to M_GUT (rho = 1e3)",
        "d18_tuning_rho1e3.json",
        "UV_volume_region",
    ),
    "BG_max_quantiles": _record(
        _REC,
        {
            "rho1e3": [116.63615877652238, 161.3279159373818, 1050.0694415956004],
            "rho1e4": [59.60390792754232, 85.9899427698044, 491.88936082608984],
            "no_spec": [38.75381921506904, 56.70399133094628, 304.58602862798443],
        },
        "Barbieri-Giudice sensitivity max_k |d ln m^2/d ln lambda_k(M_GUT)| over the region (q10, q50, q90)",
        "d20_summary.json",
        "[tag].BG_q",
    ),
    "region_u_quantiles": _record(
        _REC,
        {
            "rho1e3": [0.6142024767803779, 0.736414750885803, 0.8675189159926681, 0.9733352211530565],
            "rho1e4": [0.44749856296172813, 0.5881189638632168, 0.774769447920323, 0.9503045784475155],
            "no_spec": [0.37314836890302655, 0.5308096364029189, 0.7408695088178328, 0.9433351728298783],
        },
        "path-unitarity measure u = 2 max |a0| over the region (min, q10, q50, q90); min |a0| = u/2 = 0.307 at rho = 1e3",
        "d20_summary.json",
        "[tag].u_q",
    ),
    "region_gap_quantiles_rho1e3": _record(
        _REC,
        [-0.43680623690201764, -0.41452176304030797, -0.3985047290317483],
        "lambda4 - lambda5 at M_GUT over the rho = 1e3 region (min, median, max): the maximum is < 0",
        "d13_region_rho1e3.json",
        "region_lam4_minus_lam5_GUT_quantiles",
    ),
    "region_gap_quantiles_rho1e4": _record(
        _REC,
        [-0.34220296474587464, -0.3066612705923047, -0.27816342020857926],
        "lambda4 - lambda5 at M_GUT over the rho = 1e4 region (min, median, max): the maximum is < 0",
        "d13_region_rho1e4.json",
        "region_lam4_minus_lam5_GUT_quantiles",
    ),
    "region_gap_quantiles_no_spec": _record(
        _REC,
        [-0.28895258467114904, -0.24147243609601352, -0.19965773593385644],
        "lambda4 - lambda5 at M_GUT over the no-spectator region (min, median, max): the maximum is < 0",
        "d13_region_no_spec.json",
        "region_lam4_minus_lam5_GUT_quantiles",
    ),
    "matching_tree_LP": _record(
        _REC,
        {tag: {"n_tested": 400, "SOS_safe_feasible": 0, "BFB_only_feasible": 400} for tag in PROFILE_TAGS},
        "tree matching LP at M_GUT with slack 0.02 on 400 region points per profile: SOS-safe weights reach none, BFB-only "
        "(anti-SOS) weights reach all",
        "d20_summary.json",
        "[tag].matching",
    ),
    "matching_min_max_selfcoupling_w_over_8": _record(
        _REC,
        {"rho1e3": [1.6648465210304728, 1.8537787920005537, 2.2013939298075456]},
        "smallest max_q w_q/8 of the anti-SOS weights that match the region exactly (min, median, max)",
        "d18_tuning_rho1e3.json",
        "matching_d0.0.min_max_selfcoupling_w_over_8_quantiles",
    ),
    "threshold_LP": _record(
        _REC,
        {"gX0.0": {"n": 300, "feasible": 0}, "gX1.0": {"n": 300, "feasible": 0}},
        "SOS-safe matching with the witness M_GUT threshold subtracted, 300 rho = 1e3 region points, slack 0.03",
        "d21_threshold_matching.json",
        "rho1e3.LP_sos_minus_threshold_gX*",
    ),
    "sos_grid_with_threshold": _record(
        _REC,
        {
            "rho1e3": {"n": 18144, "path_unitary_lam5pos_gX0.0": 0, "path_unitary_lam5pos_gX1.0": 22, "pole_positive_gX1.0": 0},
            "rho1e4": {"n": 18144, "path_unitary_lam5pos_gX0.0": 0, "path_unitary_lam5pos_gX1.0": 7, "pole_positive_gX1.0": 0},
            "no_spec": {"n": 18144, "path_unitary_lam5pos_gX0.0": 0, "path_unitary_lam5pos_gX1.0": 429, "pole_positive_gX1.0": 0},
        },
        "SOS weight grid plus the witness threshold run to v_R: path-unitary with lambda5(v_R) > 0, and one-loop "
        "pole-positive (0 in every case)",
        "d21_threshold_matching.json",
        "<tag>.sos_grid_plus_threshold_gX*",
    ),
    "sos_grid_tree": _record(
        _REC,
        {tag: {"n": 30240, "path_unitary": 0, "alive_lam5_vR_pos": 0} for tag in PROFILE_TAGS},
        "30240 SOS weights with beta in {0, 0.05, 0.15}^3 run from tree matching to v_R",
        "d19_witness_sos.json",
        "<tag>.sos_grid",
    ),
    "witness_crossing_grid_limited": _record(
        _REC,
        {"rho1e3": 4.5864360850818776e16, "rho1e4": 1.146804430985203e16, "no_spec": 1185456208820689.2},
        "research lambda5 zero crossing of the witness located on a 400-point grid (about 2% below D02)",
        "d19_witness_sos.json",
        "<tag>.witness.lam5_zero_crossing_GeV",
    ),
    "pole_mass_xi_spread": _record(
        _REC,
        {"rho1e3": 1.8515744493186048e-13, "rho1e4": 1.5765166949677223e-14, "no_spec": 7.735478924075778e-14},
        "spread of the FJ one-loop pole masses over xi in {0, 0.5, 1, 3, 10} at the best points (gauge independent to "
        "<= 2e-13)",
        "d20_summary.json",
        "[tag].best_controlled.xi_spread",
    ),
    "fj_vs_vf_vev_shift": _record(
        _REC,
        {
            "rho1e3": {"dv_feyn": 0.1870998438035675, "dv_landau": 0.1764206749132327},
            "rho1e4": {"dv_feyn": 0.18669317057105997, "dv_landau": 0.17606974911394854},
            "no_spec": {"dv_feyn": 0.19520687751456328, "dv_landau": 0.18462225509867802},
        },
        "one-loop vev shift dv/v between the FJ and vev-fixed tadpole schemes (overall mass factor ~1.36 = 1 + 2 dv)",
        "d20_summary.json",
        "[tag].best_controlled.{dv_feyn, dv_landau}",
    ),
    "scale_variation": _record(
        _REC,
        {
            "Q_vR_over_sqrt2": {"region_at_vR": 1906, "region_at_Q": 0, "median_rel_dpole_region": 10.922356537809934},
            "Q_sqrt2_vR": {"region_at_vR": 1906, "region_at_Q": 1728, "median_rel_dpole_region": 0.4924976301275528},
            "Q_2_vR": {"region_at_vR": 1906, "region_at_Q": 1363, "median_rel_dpole_region": 0.735233399326998},
        },
        "rho = 1e3 renormalisation-scale variation of the one-loop pole masses (Q = v_R/sqrt2 removes every region point)",
        "d20_summary.json",
        "rho1e3.scale_variation",
    ),
    "n_core_all_scales_rho1e3": _record(
        _REC, 0, "controlled core points positive at all three scale choices (rho = 1e3)", "d22_controlled_rho1e3.json", "n_core_all_scales"
    ),
    "n_core_all_scales_rho1e4": _record(
        _REC, 87, "controlled core points positive at all three scale choices (rho = 1e4)", "d22_controlled_rho1e4.json", "n_core_all_scales"
    ),
    "n_core_all_scales_no_spec": _record(
        _REC, 240, "controlled core points positive at all three scale choices (no spectators)", "d22_controlled_no_spec.json", "n_core_all_scales"
    ),
    "best_core_lam_GUT_rho1e3": _record(
        _REC,
        [0.5596001449488849, 0.24297882322770695, 0.24211370628742573, 0.15628313581737308, 0.5723705906272927],
        "research lambda(M_GUT) of the best rho = 1e3 region point (compared with D04)",
        "d22_controlled_rho1e3.json",
        "best_core.lam_GUT",
    ),
    "sphere_min": _record(
        _REC,
        {
            "rho1e3": {"n": 60, "sigma_global_min": 43, "n_quartic_negative_somewhere": 11},
            "rho1e4": {"n": 60, "sigma_global_min": 42, "n_quartic_negative_somewhere": 11},
            "no_spec": {"n": 60, "sigma_global_min": 39, "n_quartic_negative_somewhere": 12},
        },
        "of 60 region points, those where sigma is the global minimum of the tree quartic at v_R, and those where the "
        "quartic is negative somewhere",
        "d20_summary.json",
        "[tag].sphere",
    ),
    "threshold_quality": _record(
        _REC,
        {
            "alphainv23.78_gX1.0": {"r0_stability_max": 1.8280993227648423e-05, "fit_resid": 2.2464219125994944e-06},
            "alphainv23.78_gX0.0": {"r0_stability_max": 1.8619999828217715e-05, "fit_resid": 2.7238178131328006e-06},
            "alphainv40.0_gX1.0": {"r0_stability_max": 1.8784330820365014e-05, "fit_resid": 2.78695068689494e-06},
            "alphainv40.0_gX0.0": {"r0_stability_max": 1.8537250686234685e-05, "fit_resid": 2.722045340936008e-06},
        },
        "quality of the witness M_GUT threshold extraction (computed at the witness only)",
        "d12_matching.json",
        "threshold.<key>.{r0_stability_max, fit_resid}",
    ),
    "portals_and_majorana": _record(
        _REC,
        {
            "baseline": 697,
            "a1=0.3": 40,
            "a1=0.6": 0,
            "a2=0.3": 669,
            "a2=0.6": 608,
            "a2=1.0": 431,
            "lamSD=0.3": 0,
            "lamSD=0.6": 0,
            "f=0.3,ngen=1": 651,
            "f=0.6,ngen=1": 559,
            "f=1.0,ngen=1": 610,
            "f=1.5,ngen=1": 0,
            "f=0.3,ngen=3": 579,
            "f=0.6,ngen=3": 362,
            "f=1.0,ngen=3": 486,
            "f=1.5,ngen=3": 0,
        },
        "rho = 1e3 tree-positive path-unitary points with the h/S portals (a1, a2, lamSD) and the Majorana Yukawa f on: "
        "never above the Delta-only baseline",
        "d16_portals_f.json",
        "rho1e3.<case>.n_path_unitary_tree_pos",
    ),
    "skeptic_running": _record(
        _REC,
        {
            "rho1e3": {
                "lam_MGUT": [0.559600187595696, 0.24297887178196848, 0.24211374711694336, 0.1562831763363225, 0.5723706504422938],
                "witness_lam5_zero_crossing_GeV": 4.6808750808182424e16,
                "lam4_minus_lam5_MGUT": -0.41608747410597136,
            },
            "rho1e4": {
                "lam_MGUT": [0.49948744026413405, 0.28247804789082587, 0.27484546479638894, 0.20803416565203084, 0.5201560072920164],
                "witness_lam5_zero_crossing_GeV": 1.171156460936046e16,
                "lam4_minus_lam5_MGUT": -0.3121218416399856,
            },
            "no_spec": {
                "lam_MGUT": [0.461447583523581, 0.2854926260193017, 0.279987676619798, 0.22634457823119172, 0.4711664098169027],
                "witness_lam5_zero_crossing_GeV": 1210183100234497.2,
                "lam4_minus_lam5_MGUT": -0.244821831585711,
            },
        },
        "the skeptic's independent running (DOP853) of the region points and of the witness",
        "r_d_running.json",
        "<tag>.{lam_MGUT_mine, witness_lam5_zero_crossing_GeV, lam4_minus_lam5_MGUT}",
    ),
    "skeptic_cw_masses": _record(
        _REC,
        {
            "rho1e3": [0.08413746585236913, 0.0983525938288791, 0.08395908297362252, 0.13913103441708705, 0.1416913093773803, 0.1017251408907738, 0.14822305853319445],
            "rho1e4": [0.09661777161354622, 0.19152878085107697, 0.09930888773560993, 0.160465621443867, 0.20399872501023633, 0.10304436152341831, 0.15882375472989416],
            "no_spec": [0.0987399010099738, 0.1241959765293266, 0.09430211665368585, 0.1561508812936955, 0.1651068462508241, 0.16059850690264893, 0.15346086672915935],
        },
        "the skeptic's Landau-gauge p = 0 vev-fixed CW curvature masses at the best points (reference of E02)",
        "r_d_indep.json",
        "I4.<tag>.rows[].CW_p0_vevfixed_mine",
    ),
    "skeptic_witness_betas": _record(
        _REC,
        [0.016178403965819523, 0.0020904928760440665, -0.006714643145275857, -0.005578916067776429, 0.030949283654564473],
        "one-loop betas at the witness couplings with g4 = 0.6, gR = 0.5 (research D2 = skeptic; reference of D12)",
        "r_d_indep.json",
        "beta_mine_witness_g4_0.6_gR_0.5",
    ),
    # ---- items NOT verified or NOT done here (must stay False)
    "threshold_w_independence_verified": _record(
        _REC, False, "not verified: the one-loop M_GUT threshold was computed at the witness only", "wfDA_review.md", "D: flaws and caveats"
    ),
    "two_loop_quartic_running": _record(
        _REC, False, "not verified: the quartic running is one loop (two-loop PS gauge profiles only)", "wfDA_review.md", "D: uncertain"
    ),
    "pole_mass_scale_variation_recomputed_in_module": _record(
        _REC,
        False,
        "not verified in this module: the renormalisation-scale variation of the pole masses (Q = v_R/sqrt2, sqrt2 v_R, "
        "2 v_R with joint lambda, mu^2 running) is research-recorded; the FJ pole masses at Q = v_R are recomputed",
        "d20_summary.json",
        "rho1e3.scale_variation",
    ),
    "region_gap_outside_production_box_recorded": _record(
        _REC,
        False,
        "not verified: the sign of lambda4 - lambda5 at M_GUT for region points outside the production IR box (0.3% "
        "of the UV volume at rho = 1e3, 2.5% without spectators) was not recorded",
        "d23_box_extension_rho1e3.json",
        "share_inside_prod_box",
    ),
}
UNVERIFIED_RECORD_KEYS = (
    "threshold_w_independence_verified",
    "two_loop_quartic_running",
    "pole_mass_scale_variation_recomputed_in_module",
    "region_gap_outside_production_box_recorded",
)
RESEARCH_LABELS = (_IN, _REC)

DERIVED_FLAG_CHECKS = {
    "sos_family_tree_matching_forces_lam4_ge_lam5_exact": (
        "group_theory.fierz_vectors_exact",
        "group_theory.exchange_channels_of_210_never_lower_gap",
        "chart.c_qk_exact",
        "matching.tree_map_symbolic",
        "matching.gap_identity_exact",
        "matching.sos_family_forces_gap_nonnegative",
    ),
    "tree_matching_map_exact": (
        "group_theory.fierz_vectors_exact",
        "chart.c_qk_exact",
        "matching.tree_map_symbolic",
        "matching.gap_identity_exact",
    ),
    "witness_tree_levels_reproduce_g6_exact": (
        "matching.witness_tree_levels_exact",
        "matching.witness_tree_levels_match_committed_g6_certificate",
    ),
    "one_loop_beta_coefficients_exact_rational": (
        "group_theory.beta_route_reproduces_sm_higgs",
        "group_theory.beta_scalar_tensor_exact",
        "group_theory.beta_scalar_tensor_o60_point_136",
        "group_theory.beta_gauge_tensor_exact",
        "group_theory.witness_betas_exact",
    ),
    "witness_210_exchange_vanishes_exact": ("chart.witness_portal_squares_annihilate_delta_R",),
    "witness_radiatively_unstable_at_physical_hierarchy": (
        "running.witness_lambda5_zero_crossing",
        "running.witness_flow_nonperturbative_before_v_R",
    ),
    "best_region_points_outside_sos_image_at_tree_matching": (
        "running.region_points_run_up",
        "running.region_points_violate_sos_gap_at_M_GUT",
        "running.tree_matching_min_slack_is_half_gap",
    ),
    "pole_masses_recomputed_in_module": (
        "one_loop.fj_pole_masses_positive_all_xi",
        "one_loop.fj_pole_masses_xi_independent",
        "one_loop.fj_pole_masses_match_research_record",
    ),
    "best_region_points_one_loop_pole_positive_recomputed": (
        "one_loop.fj_pole_masses_positive_all_xi",
        "one_loop.fj_pole_masses_xi_independent",
        "one_loop.fj_pole_masses_match_research_record",
        "one_loop.vev_fixed_landau_masses_positive_and_dv_controlled",
    ),
    "landau_cw_curvature_masses_positive_at_best_points": (
        "one_loop.cw_masses_positive_at_region_points",
        "one_loop.cw_masses_match_independent_record",
    ),
}
DERIVED_FLAGS = ("not_closable_on_sos_witness_family", *DERIVED_FLAG_CHECKS, "evidence_only")
NEVER_TRUE_FLAGS = (
    "G6_closed",
    "report_closes_g6_by_itself",
    "G6_gate_wired",
    "g6_impossible_in_contract_claimed",
    "anti_sos_g3_witness_excluded",
    "changes_g3_g4_closure",
    "one_loop_gut_threshold_w_independence_verified",
    "disjointness_robust_to_one_loop_threshold",
    "two_loop_quartic_running_included",
    "pole_mass_scale_variation_recomputed_in_module",
    "region_volume_and_tuning_recomputed_in_module",
    "region_scan_exhaustive_beyond_sampled_box",
    "tree_certificate_valid_below_M_GUT",
)

_DEFAULT = object()
F = Fraction


# ---------------------------------------------------------------------------------------------------------------------
# Small exact helpers.
# ---------------------------------------------------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sympy.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            return value
        return float(f"{value:.{DIGITS}g}") + 0.0
    return value


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _fractions(values: Sequence[Any]) -> list[Fraction]:
    return [Fraction(value) for value in values]


def _lcg(seed: int):
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2**31
        yield (state >> 16) % 5 - 2


def _perm_sign(permutation: Sequence[int]) -> int:
    inversions = sum(1 for i in range(len(permutation)) for j in range(i + 1, len(permutation)) if permutation[i] > permutation[j])
    return -1 if inversions % 2 else 1


def _max_abs(array: np.ndarray) -> float:
    return float(np.max(np.abs(array))) if array.size else 0.0


def _row_l1(matrix: np.ndarray) -> float:
    return float(np.max(np.sum(np.abs(matrix), axis=-1))) if matrix.size else 0.0


def _exact_matmul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Exact integer product left @ right.

    Every partial sum of an entry is bounded by (row l1 norm of left) * max|right|: below 2^52 the float64 BLAS product
    is exact; below 2^62 int64 is used; otherwise Python integers."""
    bound = _row_l1(np.asarray(left, dtype=np.float64)) * _max_abs(np.asarray(right, dtype=np.float64))
    if bound < EXACT_FLOAT_BOUND:
        return np.rint(np.asarray(left, dtype=np.float64) @ np.asarray(right, dtype=np.float64)).astype(np.int64)
    if bound < INT64_BOUND:
        return np.asarray(left, dtype=np.int64) @ np.asarray(right, dtype=np.int64)
    return np.asarray(left, dtype=object) @ np.asarray(right, dtype=object)


def _exact_dot(left: np.ndarray, right: np.ndarray) -> int:
    a = np.asarray(left).ravel()
    b = np.asarray(right).ravel()
    if float(np.sum(np.abs(a.astype(np.float64)))) * _max_abs(b.astype(np.float64)) < INT64_BOUND:
        return int(np.dot(a.astype(np.int64), b.astype(np.int64)))
    return int(np.dot(a.astype(object), b.astype(object)))


def _to_int64(array: np.ndarray) -> np.ndarray:
    array = np.asarray(array)
    if array.dtype.kind in "iu":
        return array.astype(np.int64, copy=False)
    if _max_abs(array) >= EXACT_FLOAT_BOUND:
        raise ArithmeticError("value outside the exact float64 range")
    return np.rint(array).astype(np.int64)


def _lagrange(values: Sequence[int], target: int) -> list[Fraction]:
    """Coefficients (low -> high) of prod_{c != target} (x - c)/(target - c)."""
    polynomial = [Fraction(1)]
    for value in values:
        if value == target:
            continue
        denominator = Fraction(target - value)
        shifted = [Fraction(0)] * (len(polynomial) + 1)
        for degree, coefficient in enumerate(polynomial):
            shifted[degree + 1] += coefficient / denominator
            shifted[degree] += -value * coefficient / denominator
        polynomial = shifted
    return polynomial


def _solve_fraction(matrix: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]) -> list[Fraction] | None:
    """Exact solve of a square system (Gauss-Jordan over Q); None if singular."""
    n = len(matrix)
    rows = [[Fraction(value) for value in row] + [Fraction(rhs[index])] for index, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if rows[row][column] != 0), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        head = rows[column][column]
        rows[column] = [value / head for value in rows[column]]
        for row in range(n):
            if row != column and rows[row][column] != 0:
                factor = rows[row][column]
                rows[row] = [value - factor * other for value, other in zip(rows[row], rows[column])]
    return [row[n] for row in rows]


def _rank_fraction(rows: Sequence[Sequence[Any]]) -> int:
    matrix = [[Fraction(value) for value in row] for row in rows]
    rank = 0
    n_columns = len(matrix[0]) if matrix else 0
    for column in range(n_columns):
        pivot = next((row for row in range(rank, len(matrix)) if matrix[row][column] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        head = matrix[rank][column]
        for row in range(len(matrix)):
            if row != rank and matrix[row][column] != 0:
                factor = matrix[row][column] / head
                matrix[row] = [value - factor * other for value, other in zip(matrix[row], matrix[rank])]
        rank += 1
    return rank


def _rank_mod_p(matrix: np.ndarray, prime: int = GF_PRIME) -> int:
    work = np.array(matrix, dtype=np.int64) % prime
    n_rows, n_columns = work.shape
    rank = 0
    for column in range(n_columns):
        nonzero = np.flatnonzero(work[rank:, column])
        if nonzero.size == 0:
            continue
        pivot = rank + int(nonzero[0])
        work[[rank, pivot]] = work[[pivot, rank]]
        inverse = pow(int(work[rank, column]), prime - 2, prime)
        work[rank] = (work[rank] * inverse) % prime
        factors = work[:, column].copy()
        factors[rank] = 0
        work = (work - (factors[:, None] * work[rank][None, :]) % prime) % prime
        rank += 1
        if rank == n_rows:
            break
    return rank


def _fraction_matrix_product(left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))] for i in range(len(left))]


def _fraction_inverse(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]] | None:
    n = len(matrix)
    columns = []
    for index in range(n):
        column = _solve_fraction(matrix, [Fraction(int(row == index)) for row in range(n)])
        if column is None:
            return None
        columns.append(column)
    return [[columns[j][i] for j in range(n)] for i in range(n)]


# ---------------------------------------------------------------------------------------------------------------------
# (A) Integer model of Delta_R = (10bar,1,3) inside V = 4bar (x) 4bar (x) 3.
# ---------------------------------------------------------------------------------------------------------------------

N_V = 48
N_SYM = 30
N_REAL = 60


def _v_index(a: int, b: int, m: int) -> int:
    return (4 * a + b) * 3 + m


@lru_cache(maxsize=1)
def _model() -> dict[str, Any]:
    identity4 = np.eye(4, dtype=np.int64)
    identity3 = np.eye(3, dtype=np.int64)
    gl: dict[tuple[int, int], np.ndarray] = {}
    for i in range(4):
        for j in range(4):
            unit = np.zeros((4, 4), dtype=np.int64)
            unit[i, j] = 1
            bar = -unit.T  # 4bar: E_ij -> -E_ji
            gl[(i, j)] = np.kron(np.kron(bar, identity4), identity3) + np.kron(np.kron(identity4, bar), identity3)
    epsilon = np.zeros((3, 3, 3), dtype=np.int64)
    for permutation in itertools.permutations(range(3)):
        epsilon[permutation] = _perm_sign(permutation)
    so3 = tuple(-epsilon[m] for m in range(3))  # (L_m)_ab = -eps_mab
    rl = tuple(np.kron(np.kron(identity4, identity4), generator) for generator in so3)
    sym_pairs = tuple((a, b) for a in range(4) for b in range(a, 4))
    basis = []
    norms = []
    labels = []
    for a, b in sym_pairs:
        for m in range(3):
            vector = np.zeros(N_V, dtype=np.int64)
            vector[_v_index(a, b, m)] += 1
            if a != b:
                vector[_v_index(b, a, m)] += 1
            basis.append(vector)
            norms.append(1 if a == b else 2)
            labels.append((a, b, m))
    basis_matrix = np.array(basis, dtype=np.int64)  # 30 x 48
    # Real basis U_a = b and i b (60), metric g_ab = 2 Re<U_a, U_b> = diag(2 n).
    u_real = np.zeros((N_V, N_REAL), dtype=np.int64)
    u_imag = np.zeros((N_V, N_REAL), dtype=np.int64)
    for index in range(N_SYM):
        u_real[:, 2 * index] = basis_matrix[index]
        u_imag[:, 2 * index + 1] = basis_matrix[index]
    metric = tuple(2 * norms[index // 2] for index in range(N_REAL))
    # Hermitian su(4) basis on the fundamental: E_ij + E_ji, -i (E_ij - E_ji) (i < j), E_ii - E_{i+1,i+1}.
    su4 = []
    for i in range(4):
        for j in range(i + 1, 4):
            symmetric = np.zeros((4, 4), dtype=np.int64)
            symmetric[i, j] = symmetric[j, i] = 1
            su4.append((symmetric, np.zeros((4, 4), dtype=np.int64), f"S{i}{j}"))
            antisymmetric = np.zeros((4, 4), dtype=np.int64)
            antisymmetric[i, j] = -1
            antisymmetric[j, i] = 1
            su4.append((np.zeros((4, 4), dtype=np.int64), antisymmetric, f"A{i}{j}"))
    for i in range(3):
        diagonal = np.zeros((4, 4), dtype=np.int64)
        diagonal[i, i] = 1
        diagonal[i + 1, i + 1] = -1
        su4.append((diagonal, np.zeros((4, 4), dtype=np.int64), f"D{i}"))
    su4_on_v = []
    for real, imag, _name in su4:
        bar_real, bar_imag = -real.T, -imag.T  # 4bar: X -> -X^T
        su4_on_v.append(
            (
                np.kron(np.kron(bar_real, identity4), identity3) + np.kron(np.kron(identity4, bar_real), identity3),
                np.kron(np.kron(bar_imag, identity4), identity3) + np.kron(np.kron(identity4, bar_imag), identity3),
            )
        )
    kappa4 = []
    for real_a, imag_a, _ in su4:
        row = []
        for real_b, imag_b, _ in su4:
            trace_real = int(np.trace(real_a @ real_b - imag_a @ imag_b))
            trace_imag = int(np.trace(real_a @ imag_b + imag_a @ real_b))
            if trace_imag != 0:
                raise ArithmeticError("su(4) Killing form is not real")
            row.append(Fraction(2 * trace_real))
        kappa4.append(row)
    kappa4_inverse = _fraction_inverse(kappa4)
    # su(2)_R Hermitian T_m = i L_m on the triplet (the adjoint images of sigma/2: orthonormal, kappa = 1).
    su2r_on_v = tuple((np.zeros((N_V, N_V), dtype=np.int64), generator) for generator in rl)
    return {
        "gl": gl,
        "gl_l1": max(_row_l1(matrix.astype(np.float64)) for matrix in gl.values()),
        "gl_sparse": {key: sparse.csr_matrix(value) for key, value in gl.items()},
        "so3": so3,
        "rl": rl,
        "rl_sparse": tuple(sparse.csr_matrix(value) for value in rl),
        "rl_l1": max(_row_l1(matrix.astype(np.float64)) for matrix in rl),
        "sym_pairs": sym_pairs,
        "basis": basis_matrix,
        "norms": tuple(norms),
        "labels": tuple(labels),
        "u_real": u_real,
        "u_imag": u_imag,
        "metric": metric,
        "su4": tuple(su4),
        "su4_on_v": tuple(su4_on_v),
        "kappa4": kappa4,
        "kappa4_inverse": kappa4_inverse,
        "su2r_on_v": su2r_on_v,
    }


# Pair stacks are held in the layout L[r, n, c] = X_n[r, c] (int64), so that M X_n for every n is one sparse product.
# Every pair tensor of this module is symmetric (D (x) D, D (x) U + U (x) D, the basis pairs e_ab) and R(M) preserves
# symmetry, so R(M) X = M X + X M^T = M X + (M X)^T; the symmetry is asserted exactly on entry (_to_layout).
PAIR_INPUT_BOUND = 2**40  # int64 guard: (64 l1^2 + 4) * 2^40 << 2^62 for every generator used here (l1 <= 2)


def _to_layout(stack: np.ndarray) -> np.ndarray:
    stack = np.asarray(stack, dtype=np.int64)
    if not np.array_equal(stack, stack.transpose(0, 2, 1)):
        raise ArithmeticError("pair tensors must be symmetric")
    return np.ascontiguousarray(stack.transpose(1, 0, 2))


def _from_layout(layout: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(layout.transpose(1, 0, 2))


def _pair_apply(matrix: Any, layout: np.ndarray) -> np.ndarray:
    """R(M) X = M X + (M X)^T on a symmetric pair stack in layout form (exact int64; M a sparse integer matrix)."""
    d, n, _ = layout.shape
    product = np.asarray(matrix @ layout.reshape(d, n * d)).reshape(d, n, d)
    return product + product.transpose(2, 1, 0)


def _guard_pairs(layout: np.ndarray) -> None:
    if _max_abs(layout) >= PAIR_INPUT_BOUND:
        raise ArithmeticError("int64 guard exceeded in a pair operator")


def _c4_twice(layout: np.ndarray) -> np.ndarray:
    """2 C4_std X = sum_ij R(E_ij) R(E_ji) X - (1/4) R(N)^2 X with R(N) = -4 on the four 4bar slots of a pair."""
    model = _model()
    _guard_pairs(layout)
    output = -4 * layout
    for i in range(4):
        for j in range(4):
            output += _pair_apply(model["gl_sparse"][(i, j)], _pair_apply(model["gl_sparse"][(j, i)], layout))
    return output


def _cr(layout: np.ndarray) -> np.ndarray:
    """CR X = -sum_m R(L_m)^2 X."""
    model = _model()
    _guard_pairs(layout)
    output = np.zeros_like(layout)
    for generator in model["rl_sparse"]:
        output -= _pair_apply(generator, _pair_apply(generator, layout))
    return output


@lru_cache(maxsize=1)
def _projector_terms() -> tuple[tuple[int, dict[tuple[int, int], int]], ...]:
    """den_k P_k = den_k L4_{c4}(C4) LR_{cr}(CR) as integer combinations of (2 C4)^a CR^b."""
    output = []
    for name in QUARTIC_BASIS:
        c4, cr = QUARTIC_CASIMIRS[name]
        in_c4 = _lagrange(C4_VALUES, c4)
        in_twice_c4 = [in_c4[a] / Fraction(2) ** a for a in range(len(in_c4))]
        in_cr = _lagrange(CR_VALUES, cr)
        coefficients = {(a, b): in_twice_c4[a] * in_cr[b] for a in range(3) for b in range(3) if in_twice_c4[a] * in_cr[b] != 0}
        denominator = math.lcm(*(value.denominator for value in coefficients.values()))
        output.append((denominator, {key: int(value * denominator) for key, value in coefficients.items()}))
    return tuple(output)


def _monomials(layout: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    """(2 C4)^a CR^b X for a, b <= 2 (layout form)."""
    powers = [layout]
    for _ in range(2):
        powers.append(_c4_twice(powers[-1]))
    output = {}
    for a in range(3):
        current = powers[a]
        output[(a, 0)] = current
        for b in (1, 2):
            current = _cr(current)
            output[(a, b)] = current
    return output


def _project(monomials: Mapping[tuple[int, int], np.ndarray], terms: tuple[int, Mapping[tuple[int, int], int]]) -> tuple[int, np.ndarray]:
    denominator, coefficients = terms
    bound = sum(abs(value) for value in coefficients.values()) * max(_max_abs(monomials[key]) for key in coefficients)
    if bound >= INT64_BOUND:
        raise ArithmeticError("int64 guard exceeded in a projector")
    result = sum(value * monomials[key] for key, value in coefficients.items())
    return denominator, result


def _delta_projections(stack: np.ndarray) -> list[tuple[int, np.ndarray]]:
    """(den_k, den_k P_k X) for every X of a symmetric pair stack (exact int64)."""
    monomials = _monomials(_to_layout(stack))
    return [(denominator, _from_layout(array)) for denominator, array in (_project(monomials, terms) for terms in _projector_terms())]


def _pair_square(real: np.ndarray, imag: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.outer(real, real) - np.outer(imag, imag), np.outer(real, imag) + np.outer(imag, real)


def _pair_symmetrised(dr: np.ndarray, di: np.ndarray, er: np.ndarray, ei: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    real = np.outer(dr, er) - np.outer(di, ei)
    imag = np.outer(dr, ei) + np.outer(di, er)
    return real + real.T, imag + imag.T


def _hermitian_real(ar: np.ndarray, ai: np.ndarray, br: np.ndarray, bi: np.ndarray) -> int:
    """Re <A, B> = Re sum conj(A) B (exact)."""
    return _exact_dot(ar, br) + _exact_dot(ai, bi)


def quartic_values(real: np.ndarray, imag: np.ndarray, project: Callable[[np.ndarray], list[tuple[int, np.ndarray]]] | None = None) -> list[Fraction]:
    """V_k(D) = <X, P_k X>, X = D (x) D (exact)."""
    project = _delta_projections if project is None else project
    xr, xi = _pair_square(np.asarray(real, dtype=np.int64), np.asarray(imag, dtype=np.int64))
    projected = project(np.stack([xr, xi]).astype(np.int64))
    values = []
    for denominator, array in projected:
        array = _to_int64(array)
        values.append(Fraction(_hermitian_real(xr, xi, array[0], array[1]), denominator))
    return values


def quartic_hessians(
    real: np.ndarray,
    imag: np.ndarray,
    u_real: np.ndarray,
    u_imag: np.ndarray,
    project: Callable[[np.ndarray], list[tuple[int, np.ndarray]]],
) -> list[tuple[np.ndarray, int]]:
    """Exact Hessians H_k[a, b] = 2 Re<X_a, P_k X_b> + 2 Re<X_ab, P_k X0> of V_k(phi) = <X, P_k X> along the real
    directions U_a = u_real[:, a] + i u_imag[:, a] (X0 = phi (x) phi, X_a = phi (x) U_a + U_a (x) phi, X_ab = U_a (x) U_b +
    U_b (x) U_a); returned as (den_k H_k integer matrix, den_k)."""
    dr = np.asarray(real, dtype=np.int64)
    di = np.asarray(imag, dtype=np.int64)
    n_real = u_real.shape[1]
    x0r, x0i = _pair_square(dr, di)
    ar = np.einsum("p,qa->apq", dr, u_real) - np.einsum("p,qa->apq", di, u_imag)
    ai = np.einsum("p,qa->apq", dr, u_imag) + np.einsum("p,qa->apq", di, u_real)
    xar = ar + ar.transpose(0, 2, 1)
    xai = ai + ai.transpose(0, 2, 1)
    projected_a = project(np.concatenate([xar, xai]).astype(np.int64))
    projected_0 = project(np.stack([x0r, x0i]).astype(np.int64))
    xa_flat = np.concatenate([xar.reshape(n_real, -1), xai.reshape(n_real, -1)], axis=1)
    output = []
    for (denominator, pa), (denominator_0, p0) in zip(projected_a, projected_0):
        if denominator != denominator_0:
            raise ArithmeticError("projector denominators differ")
        pa = _to_int64(pa)
        p0 = _to_int64(p0)
        pa_flat = np.concatenate([pa[:n_real].reshape(n_real, -1), pa[n_real:].reshape(n_real, -1)], axis=1)
        first = 2 * _exact_matmul(xa_flat, pa_flat.T)
        sym_real = p0[0] + p0[0].T
        sym_imag = p0[1] + p0[1].T
        p_mat = _exact_matmul(u_real.T, sym_real) + _exact_matmul(u_imag.T, sym_imag)
        q_mat = _exact_matmul(u_real.T, sym_imag) - _exact_matmul(u_imag.T, sym_real)
        second = 2 * (_exact_matmul(p_mat, u_real) + _exact_matmul(q_mat, u_imag))
        hessian = first + second
        if not np.array_equal(hessian, hessian.T):
            raise ArithmeticError("exact Hessian is not symmetric")
        output.append((hessian, denominator))
    return output


def metric_trace(first: tuple[np.ndarray, int], second: tuple[np.ndarray, int], metric: Sequence[int]) -> Fraction:
    """Tr(g^-1 H_i g^-1 H_j) for the diagonal kinetic metric g (canonical normalisation)."""
    (a, den_a), (b, den_b) = first, second
    common = math.lcm(*metric)
    weights = np.array([common // value for value in metric], dtype=object)
    weighted = np.asarray(a, dtype=object) * np.outer(weights, weights)
    total = int(np.sum(weighted * np.asarray(b, dtype=object).T))
    return Fraction(total, common * common * den_a * den_b)


def _apply_complex(generator: tuple[np.ndarray, np.ndarray], real: np.ndarray, imag: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    g_real, g_imag = generator
    return g_real @ real - g_imag @ imag, g_real @ imag + g_imag @ real


def gauge_quartic_traces(real: np.ndarray, imag: np.ndarray, factors: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], Fraction]:
    """Tr (M_V^2)^2 split by coupling monomials g_f^2 g_f'^2, with M_V^2 = 2 g_a g_b Re(phi^+ T_a T_b phi) in an
    orthonormal basis (Tr (M'^2) = Tr(A_ff' K_f' A_f'f K_f), K = kappa^-1); the (f, f') cross terms are summed."""
    images = {}
    for factor in factors:
        images[factor["name"]] = [_apply_complex(generator, real, imag) for generator in factor["generators"]]
    output: dict[tuple[str, str], Fraction] = {}
    names = [factor["name"] for factor in factors]
    by_name = {factor["name"]: factor for factor in factors}

    def gram(first: str, second: str) -> list[list[Fraction]]:
        scale = by_name[first]["scale"] * by_name[second]["scale"]
        return [
            [2 * scale * (_exact_dot(x[0], y[0]) + _exact_dot(x[1], y[1])) for y in images[second]]
            for x in images[first]
        ]

    for index, first in enumerate(names):
        for second in names[index:]:
            block = gram(first, second)
            block_t = [list(row) for row in zip(*block)]
            product = _fraction_matrix_product(
                _fraction_matrix_product(block, by_name[second]["kappa_inverse"]),
                _fraction_matrix_product(block_t, by_name[first]["kappa_inverse"]),
            )
            trace = sum((product[i][i] for i in range(len(product))), Fraction(0))
            output[(first, second)] = trace if first == second else 2 * trace
    return output


def gauge_casimir(factor: Mapping[str, Any], basis_real: np.ndarray, basis_imag: np.ndarray) -> Fraction | None:
    """sum_ab kappa^-1_ab T_a T_b on the field (columns of the basis); the scalar if it is a multiple of 1, else None."""
    kinv = factor["kappa_inverse"]
    generators = factor["generators"]
    common = math.lcm(*(value.denominator for row in kinv for value in row))
    total_real = np.zeros(basis_real.shape, dtype=object)
    total_imag = np.zeros(basis_imag.shape, dtype=object)
    images = [_apply_complex(generator, basis_real, basis_imag) for generator in generators]
    for a, generator in enumerate(generators):
        for b in range(len(generators)):
            if kinv[a][b] == 0:
                continue
            twice = _apply_complex(generator, *images[b])
            weight = int(kinv[a][b] * common)
            total_real = total_real + weight * twice[0].astype(object)
            total_imag = total_imag + weight * twice[1].astype(object)
    scale = factor["scale"] ** 2
    value = None
    for column in range(basis_real.shape[1]):
        vector = np.concatenate([basis_real[:, column], basis_imag[:, column]]).astype(object)
        image = np.concatenate([total_real[:, column], total_imag[:, column]])
        pivot = next(index for index, entry in enumerate(vector) if entry != 0)
        ratio = Fraction(int(image[pivot]), int(vector[pivot]) * common)
        if any(Fraction(int(image[index]), common) != ratio * int(vector[index]) for index in range(len(vector))):
            return None
        if value is None:
            value = ratio
        elif value != ratio:
            return None
    return None if value is None else value * scale


def _delta_gauge_factors() -> list[dict[str, Any]]:
    model = _model()
    return [
        {"name": "g4", "generators": list(model["su4_on_v"]), "scale": Fraction(1), "kappa_inverse": model["kappa4_inverse"]},
        {
            "name": "gR",
            "generators": list(model["su2r_on_v"]),
            "scale": Fraction(1),
            "kappa_inverse": [[Fraction(int(i == j)) for j in range(3)] for i in range(3)],
        },
    ]


def _expectation(generator: tuple[np.ndarray, np.ndarray], real: np.ndarray, imag: np.ndarray) -> int:
    """D^+ R D for a Hermitian complex-integer R (exactly real)."""
    yr, yi = _apply_complex(generator, real, imag)
    re_part = _exact_dot(real, yr) + _exact_dot(imag, yi)
    im_part = _exact_dot(real, yi) - _exact_dot(imag, yr)
    if im_part != 0:
        raise ArithmeticError("expectation value of a Hermitian generator is not real")
    return re_part


def _complex_product(first: tuple[np.ndarray, np.ndarray], second: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    return first[0] @ second[0] - first[1] @ second[1], first[0] @ second[1] + first[1] @ second[0]


def fierz_values(real: np.ndarray, imag: np.ndarray) -> dict[str, Fraction]:
    """Q_c(D) = sum_a (D^+ X_a D)^2 over an orthonormal basis of each PS channel (rational Killing Gram)."""
    model = _model()
    kinv = model["kappa4_inverse"]
    norm = _exact_dot(real, real) + _exact_dot(imag, imag)
    su4_values = [_expectation(generator, real, imag) for generator in model["su4_on_v"]]
    q15 = sum((kinv[a][b] * su4_values[a] * su4_values[b] for a in range(15) for b in range(15)), Fraction(0))
    su2_values = [_expectation(generator, real, imag) for generator in model["su2r_on_v"]]
    q13 = Fraction(sum(value * value for value in su2_values))
    q1513 = Fraction(0)
    for su2 in model["su2r_on_v"]:
        mixed = [_expectation(_complex_product(generator, su2), real, imag) for generator in model["su4_on_v"]]
        q1513 += sum((kinv[a][b] * mixed[a] * mixed[b] for a in range(15) for b in range(15)), Fraction(0))
    return {"(1,1,1)": Fraction(norm * norm), "(15,1,1)": q15, "(1,1,3)": q13, "(15,1,3)": q1513}


def _sym_vector(pair: tuple[int, int], t3r: int) -> tuple[np.ndarray, np.ndarray]:
    """S_ab v_t as a Gaussian-integer vector of V (symmetric in the two 4bar slots)."""
    a, b = pair
    real = np.zeros(N_V, dtype=np.int64)
    imag = np.zeros(N_V, dtype=np.int64)
    for m, (vr, vi) in enumerate(T3R_VECTORS[t3r]):
        for x, y in {(a, b), (b, a)}:
            real[_v_index(x, y, m)] += vr
            imag[_v_index(x, y, m)] += vi
    return real, imag


def _delta_points() -> list[tuple[np.ndarray, np.ndarray]]:
    model = _model()
    generator = _lcg(LCG_SEED_GROUP)
    points = []
    for _ in range(7):
        real = np.zeros(N_V, dtype=np.int64)
        imag = np.zeros(N_V, dtype=np.int64)
        for index in range(N_SYM):
            coefficient_real = next(generator)
            coefficient_imag = next(generator)
            real = real + coefficient_real * model["basis"][index]
            imag = imag + coefficient_imag * model["basis"][index]
        points.append((real, imag))
    return points


def _hypercharge_times_six(real: np.ndarray, imag: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """6 Y D = 6 T3R D + 3 (B-L) D with B-L(4bar) = diag(-1/3, -1/3, -1/3, +1) per slot and T3R = i L_3 (integers)."""
    model = _model()
    bl3 = (-1, -1, -1, 3)  # 3 (B-L) on one 4bar slot
    diagonal = np.zeros(N_V, dtype=np.int64)
    for a in range(4):
        for b in range(4):
            for m in range(3):
                diagonal[_v_index(a, b, m)] = bl3[a] + bl3[b]
    t3_real, t3_imag = _apply_complex(model["su2r_on_v"][2], real, imag)  # T3R D
    return 6 * t3_real + diagonal * real, 6 * t3_imag + diagonal * imag


def _su3_casimir_times_six(real: np.ndarray, imag: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """6 C3 D = 3 sum_{i,j<=2} rho(E_ij) rho(E_ji) D - rho(N3)^2 D on the single field."""
    model = _model()
    gl = model["gl"]
    out_real = np.zeros(N_V, dtype=np.int64)
    out_imag = np.zeros(N_V, dtype=np.int64)
    for i in range(3):
        for j in range(3):
            out_real += 3 * (gl[(i, j)] @ (gl[(j, i)] @ real))
            out_imag += 3 * (gl[(i, j)] @ (gl[(j, i)] @ imag))
    n3 = gl[(0, 0)] + gl[(1, 1)] + gl[(2, 2)]
    out_real -= n3 @ (n3 @ real)
    out_imag -= n3 @ (n3 @ imag)
    return out_real, out_imag


def _eigenvalue(image: tuple[np.ndarray, np.ndarray], vector: tuple[np.ndarray, np.ndarray], scale: int) -> Fraction | None:
    """lambda with image = scale * lambda * vector, or None."""
    flat_vector = np.concatenate(vector)
    flat_image = np.concatenate(image)
    pivot = int(np.flatnonzero(flat_vector)[0])
    value = Fraction(int(flat_image[pivot]), int(flat_vector[pivot]) * scale)
    for index in range(flat_vector.size):
        if Fraction(int(flat_image[index]), scale) != value * int(flat_vector[index]):
            return None
    return value


@lru_cache(maxsize=1)
def _sym2_core() -> dict[str, Any]:
    """The 465 orthogonal basis pairs e_ab = b_a (x) b_b + b_b (x) b_a of Sym^2(Delta_R): minimal polynomials of the pair
    Casimirs, exact Gram matrices G_k[f, e] = den_k <e_f, P_k e_e> (batched, exact int64)."""
    model = _model()
    basis = model["basis"]
    pairs = tuple((a, b) for a in range(N_SYM) for b in range(a, N_SYM))
    flat = np.zeros((len(pairs), N_V * N_V), dtype=np.int64)
    for index, (a, b) in enumerate(pairs):
        tensor = np.outer(basis[a], basis[b]) + np.outer(basis[b], basis[a])
        flat[index] = tensor.ravel()
    norms2 = tuple(int(value) for value in np.sum(flat * flat, axis=1))
    terms = _projector_terms()
    grams = [np.zeros((len(pairs), len(pairs)), dtype=np.int64) for _ in terms]
    minimal_c4 = True
    minimal_cr = True
    chunk = 155
    for start in range(0, len(pairs), chunk):
        stop = min(start + chunk, len(pairs))
        x = _to_layout(flat[start:stop].reshape(-1, N_V, N_V))
        c4_powers = [x]
        for _ in range(3):
            c4_powers.append(_c4_twice(c4_powers[-1]))
        cr_powers = [x]
        for _ in range(3):
            cr_powers.append(_cr(cr_powers[-1]))
        residual_c4 = c4_powers[3] - 52 * c4_powers[2] + 864 * c4_powers[1] - 4608 * c4_powers[0]
        residual_cr = cr_powers[3] - 8 * cr_powers[2] + 12 * cr_powers[1]
        minimal_c4 = minimal_c4 and not np.any(residual_c4)
        minimal_cr = minimal_cr and not np.any(residual_cr)
        monomials = {(0, 0): x, (0, 1): cr_powers[1], (0, 2): cr_powers[2]}
        for a in (1, 2):
            monomials[(a, 0)] = c4_powers[a]
            monomials[(a, 1)] = _cr(c4_powers[a])
            monomials[(a, 2)] = _cr(monomials[(a, 1)])
        for k, term in enumerate(terms):
            _den, projected = _project(monomials, term)
            projected_flat = _from_layout(projected).reshape(stop - start, -1)
            grams[k][:, start:stop] = _exact_matmul(flat, projected_flat.T)
    dimensions = []
    for k, (denominator, _coefficients) in enumerate(terms):
        dimensions.append(sum((Fraction(int(grams[k][e, e]), denominator * norms2[e]) for e in range(len(pairs))), Fraction(0)))
    common = math.lcm(*(term[0] for term in terms))
    completeness = sum(grams[k].astype(object) * (common // terms[k][0]) for k in range(len(terms)))
    identity = np.diag(np.array([common * value for value in norms2], dtype=object))
    return {
        "pairs": pairs,
        "norms2": norms2,
        "grams": tuple(grams),
        "denominators": tuple(term[0] for term in terms),
        "minimal_polynomial_c4": bool(minimal_c4),
        "minimal_polynomial_cr": bool(minimal_cr),
        "dimensions": tuple(dimensions),
        "grams_symmetric": all(np.array_equal(gram, gram.T) for gram in grams),
        "projectors_sum_to_identity": bool(np.array_equal(completeness, identity)),
    }


def _sm_higgs_identity() -> dict[str, Any]:
    """The Delta_R beta route on V = lambda (H^+ H)^2 (complex doublet, SU(2)_L x U(1)_Y with Y = 1/2)."""
    u_real = np.array([[1, 0, 0, 0], [0, 0, 1, 0]], dtype=np.int64)
    u_imag = np.array([[0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.int64)
    metric = (2, 2, 2, 2)

    def identity_projector(x: np.ndarray) -> list[tuple[int, np.ndarray]]:
        return [(1, x)]

    sigma = [
        (np.array([[0, 1], [1, 0]], dtype=np.int64), np.zeros((2, 2), dtype=np.int64)),
        (np.zeros((2, 2), dtype=np.int64), np.array([[0, -1], [1, 0]], dtype=np.int64)),
        (np.array([[1, 0], [0, -1]], dtype=np.int64), np.zeros((2, 2), dtype=np.int64)),
    ]
    kappa = [
        [Fraction(2 * int(np.trace(a[0] @ b[0] - a[1] @ b[1])), 4) for b in sigma] for a in sigma
    ]  # 2 Tr((sigma_a/2)(sigma_b/2))
    factors = [
        {"name": "g", "generators": sigma, "scale": Fraction(1, 2), "kappa_inverse": _fraction_inverse(kappa)},
        {
            "name": "gY",
            "generators": [(np.eye(2, dtype=np.int64), np.zeros((2, 2), dtype=np.int64))],
            "scale": Fraction(1, 2),
            "kappa_inverse": [[Fraction(1)]],
        },
    ]
    points = [(np.array([1, 0]), np.array([0, 0])), (np.array([2, 1]), np.array([1, -2]))]
    q_values = []
    gauge_values = []
    for real, imag in points:
        value = quartic_values(real, imag, identity_projector)[0]
        hessian = quartic_hessians(real, imag, u_real, u_imag, identity_projector)[0]
        q_values.append(Fraction(1, 2) * metric_trace(hessian, hessian, metric) / value)
        traces = gauge_quartic_traces(real, imag, factors)
        gauge_values.append({key: Fraction(3, 2) * trace / value for key, trace in traces.items()})
    basis_real = np.eye(2, dtype=np.int64)
    basis_imag = np.zeros((2, 2), dtype=np.int64)
    casimirs = {factor["name"]: gauge_casimir(factor, basis_real, basis_imag) for factor in factors}
    consistent = q_values[0] == q_values[1] and gauge_values[0] == gauge_values[1] and None not in casimirs.values()
    lam, g, gy = sympy.symbols("lambda g gY")
    symbols = {"g": g, "gY": gy}
    beta = _sympy_rational(q_values[0]) * lam**2
    if None not in casimirs.values():
        anomalous = sum((_sympy_rational(casimirs[name]) * symbols[name] ** 2 for name in ("g", "gY")), sympy.Integer(0))
        beta -= 12 * lam * anomalous
    for (first, second), value in gauge_values[0].items():
        beta += _sympy_rational(value) * symbols[first] ** 2 * symbols[second] ** 2
    target = 24 * lam**2 - 3 * lam * (3 * g**2 + gy**2) + sympy.Rational(3, 8) * (2 * g**4 + (g**2 + gy**2) ** 2)
    identity = bool(consistent and sympy.expand(beta - target) == 0)
    return {
        "scalar_coefficient": q_values[0],
        "casimirs": casimirs,
        "gauge_coefficients": {f"{first}^2{second}^2": value for (first, second), value in gauge_values[0].items()},
        "beta_16pi2": sympy.expand(beta),
        "target_16pi2": sympy.expand(target),
        "identity_exact": identity,
    }


@lru_cache(maxsize=1)
def _group_core() -> dict[str, Any]:
    started = time.time()
    model = _model()
    gl = model["gl"]
    # A01: gl(4) and so(3) relations of the integer generators.
    commutators_ok = True
    for (i, j), first in gl.items():
        for (k, l), second in gl.items():
            expected = (gl[(i, l)] if j == k else 0) - (gl[(k, j)] if l == i else 0)
            if not np.array_equal(first @ second - second @ first, expected + np.zeros_like(first)):
                commutators_ok = False
    so3 = model["so3"]
    epsilon = {(a, b, c): _perm_sign((a, b, c)) for a, b, c in itertools.permutations(range(3))}
    for a in range(3):
        for b in range(3):
            expected = sum((epsilon.get((a, b, c), 0) * so3[c] for c in range(3)), np.zeros((3, 3), dtype=np.int64))
            if not np.array_equal(so3[a] @ so3[b] - so3[b] @ so3[a], expected):
                commutators_ok = False
    for first in gl.values():
        for second in model["rl"]:
            if np.any(first @ second - second @ first):
                commutators_ok = False
    integer_generators = all(matrix.dtype == np.int64 for matrix in gl.values()) and all(matrix.dtype == np.int64 for matrix in model["rl"])
    # A02: single-field Casimirs on the 30 symmetric basis vectors (gl route and Killing route).
    c_gl = sum((gl[(i, j)] @ gl[(j, i)] for i in range(4) for j in range(4)), np.zeros((N_V, N_V), dtype=np.int64))
    casimir_ok = True
    for vector in model["basis"]:
        if not np.array_equal(c_gl @ vector - vector, 9 * vector):  # 2 C4 = C_gl - (1/4) rho(N)^2, rho(N) = -2
            casimir_ok = False
        cr_vector = -sum((generator @ (generator @ vector) for generator in model["rl"]), np.zeros(N_V, dtype=np.int64))
        if not np.array_equal(cr_vector, 2 * vector):
            casimir_ok = False
    factors = _delta_gauge_factors()
    basis_real = model["basis"].T.copy()
    basis_imag = np.zeros_like(basis_real)
    killing = {factor["name"]: gauge_casimir(factor, basis_real, basis_imag) for factor in factors}
    # A05 and the V matrix at the 7 deterministic points.
    points = _delta_points()
    values = [quartic_values(real, imag) for real, imag in points]
    norms = [_exact_dot(real, real) + _exact_dot(imag, imag) for real, imag in points]
    d0 = _sym_vector(*STATE_DIRECTIONS["(1,1)_0 radial"])
    d0_norm = _exact_dot(d0[0], d0[0]) + _exact_dot(d0[1], d0[1])
    d0_values = quartic_values(*d0)
    # A06: vacuum stabiliser.
    su3_indices = [index for index, (_r, _i, name) in enumerate(model["su4"]) if name in {"S01", "A01", "S02", "A02", "S12", "A12", "D0", "D1"}]
    su3_annihilates = all(
        not np.any(_apply_complex(model["su4_on_v"][index], *d0)[0]) and not np.any(_apply_complex(model["su4_on_v"][index], *d0)[1])
        for index in su3_indices
    )
    y_image = _hypercharge_times_six(*d0)
    hypercharge_annihilates = not np.any(y_image[0]) and not np.any(y_image[1])
    broken_rows = []
    for generator in list(model["su4_on_v"]) + list(model["su2r_on_v"]):
        real, imag = _apply_complex(generator, *d0)
        broken_rows.append([int(value) for value in np.concatenate([real, imag])])
    broken_rank = _rank_fraction(broken_rows)
    # A07/A08: SM labels of the states and of the 30 weight vectors.
    state_labels = {}
    for name in STATE_ORDER:
        vector = _sym_vector(*STATE_DIRECTIONS[name])
        symmetric = all(
            vector[part][_v_index(a, b, m)] == vector[part][_v_index(b, a, m)] for part in (0, 1) for a in range(4) for b in range(4) for m in range(3)
        )
        state_labels[name] = {
            "symmetric": symmetric,
            "Y": _eigenvalue(_hypercharge_times_six(*vector), vector, 6),
            "C3": _eigenvalue(_su3_casimir_times_six(*vector), vector, 6),
        }
    classes: dict[tuple[Fraction, Fraction], int] = {}
    weight_vectors_ok = True
    for pair in model["sym_pairs"]:
        for t3r in (1, -1, 0):
            vector = _sym_vector(pair, t3r)
            y_value = _eigenvalue(_hypercharge_times_six(*vector), vector, 6)
            c3_value = _eigenvalue(_su3_casimir_times_six(*vector), vector, 6)
            if y_value is None or c3_value is None:
                weight_vectors_ok = False
                continue
            classes[(c3_value, y_value)] = classes.get((c3_value, y_value), 0) + 2
    goldstone_classes = {}
    for name, (pair, t3r) in GOLDSTONE_DIRECTIONS.items():
        vector = _sym_vector(pair, t3r)
        goldstone_classes[name] = (
            _eigenvalue(_su3_casimir_times_six(*vector), vector, 6),
            _eigenvalue(_hypercharge_times_six(*vector), vector, 6),
        )
    # A09: tree mass matrix.
    x0 = _pair_square(*d0)
    projections_0 = _delta_projections(np.stack(x0).astype(np.int64))
    tree_rows = []
    for name in STATE_ORDER:
        er, ei = _sym_vector(*STATE_DIRECTIONS[name])
        e_norm = _exact_dot(er, er) + _exact_dot(ei, ei)
        x1 = _pair_symmetrised(d0[0], d0[1], er, ei)
        x2 = _pair_square(er, ei)
        projections_1 = _delta_projections(np.stack(x1).astype(np.int64))
        row = []
        for k in range(5):
            den_1, p1 = projections_1[k]
            den_0, p0 = projections_0[k]
            p1 = _to_int64(p1)
            p0 = _to_int64(p0)
            first = Fraction(_hermitian_real(x1[0], x1[1], p1[0], p1[1]), den_1)
            second = 2 * Fraction(_hermitian_real(x2[0], x2[1], p0[0], p0[1]), den_0)
            mu2 = 2 * d0_norm if QUARTIC_BASIS[k] == "(35,5)" else 0
            row.append(((first + second) / e_norm - mu2) / d0_norm)
        tree_rows.append(row)
    # A11: Fierz values; A13-A17: Hessians and gauge traces at the 7 points.
    fierz_at_points = [fierz_values(real, imag) for real, imag in points]
    scalar_traces = []
    gauge_traces = []
    for real, imag in points:
        hessians = quartic_hessians(real, imag, model["u_real"], model["u_imag"], _delta_projections)
        traces = {}
        for i in range(5):
            for j in range(i, 5):
                factor = Fraction(1, 2) if i == j else Fraction(1)
                traces[(i, j)] = factor * metric_trace(hessians[i], hessians[j], model["metric"])
        scalar_traces.append(traces)
        raw = gauge_quartic_traces(real, imag, factors)
        gauge_traces.append(
            {
                "g4^4": Fraction(3, 2) * raw[("g4", "g4")],
                "gR^4": Fraction(3, 2) * raw[("gR", "gR")],
                "g4^2gR^2": Fraction(3, 2) * raw[("g4", "gR")],
            }
        )
    return {
        "commutators_ok": commutators_ok,
        "integer_generators": integer_generators,
        "casimir_gl_route_ok": casimir_ok,
        "casimir_killing_route": killing,
        "points": points,
        "values": values,
        "norms": norms,
        "d0": d0,
        "d0_norm": d0_norm,
        "d0_values": d0_values,
        "su3_annihilates": su3_annihilates,
        "hypercharge_annihilates": hypercharge_annihilates,
        "broken_rank": broken_rank,
        "state_labels": state_labels,
        "weight_classes": classes,
        "weight_vectors_ok": weight_vectors_ok,
        "goldstone_classes": goldstone_classes,
        "tree_rows": tree_rows,
        "fierz_at_points": fierz_at_points,
        "scalar_traces": scalar_traces,
        "gauge_traces": gauge_traces,
        "sym2": _sym2_core(),
        "sm_higgs": _sm_higgs_identity(),
        "seconds": time.time() - started,
    }


def _decompose(values: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]) -> tuple[list[Fraction] | None, list[Fraction] | None]:
    """Solve sum_k c_k V_k = rhs on the first five points; residuals on the two check points."""
    solution = _solve_fraction([list(row) for row in values[:5]], list(rhs[:5]))
    if solution is None:
        return None, None
    residuals = [sum((solution[k] * values[p][k] for k in range(5)), Fraction(0)) - rhs[p] for p in range(5, len(values))]
    return solution, residuals


def group_theory_section(*, fierz_override: Mapping[str, Sequence[Any]] | None = None, beta_override: Mapping[tuple[int, int], Sequence[Any]] | None = None) -> dict[str, Any]:
    core = _group_core()
    model = _model()
    values = core["values"]
    checks: dict[str, bool] = {}
    checks["integer_generators_close_su4_su2R"] = bool(core["commutators_ok"] and core["integer_generators"])
    killing = core["casimir_killing_route"]
    checks["delta_R_casimirs_9_2_and_2"] = bool(
        core["casimir_gl_route_ok"] and killing.get("g4") == Fraction(9, 2) and killing.get("gR") == Fraction(2)
    )
    sym2 = core["sym2"]
    checks["sym2_minimal_polynomials"] = bool(sym2["minimal_polynomial_c4"] and sym2["minimal_polynomial_cr"])
    checks["sym2_irrep_dimensions"] = bool(
        list(sym2["dimensions"]) == [Fraction(value) for value in QUARTIC_DIMENSIONS]
        and sum(sym2["dimensions"]) == len(sym2["pairs"]) == 465
        and sym2["grams_symmetric"]
        and sym2["projectors_sum_to_identity"]
    )
    completeness = all(sum(row) == norm * norm for row, norm in zip(values, core["norms"]))
    checks["quartic_basis_completeness"] = bool(
        completeness and core["d0_norm"] == 2 and core["d0_values"] == [0, 0, 0, 0, core["d0_norm"] ** 2]
    )
    checks["vacuum_is_sm_singlet_with_9_broken_generators"] = bool(
        core["su3_annihilates"] and core["hypercharge_annihilates"] and core["broken_rank"] == 9
    )
    labels = core["state_labels"]
    checks["sm_state_labels_exact"] = bool(
        all(labels[name]["symmetric"] for name in STATE_ORDER)
        and [labels[name]["Y"] for name in STATE_ORDER] == _fractions(EXPECTED_STATE_Y)
        and [labels[name]["C3"] for name in STATE_ORDER] == _fractions(EXPECTED_STATE_C3)
    )
    classes = core["weight_classes"]
    state_classes = [(labels[name]["C3"], labels[name]["Y"]) for name in STATE_ORDER]
    goldstone = core["goldstone_classes"]
    goldstone_real = sum(classes.get(value, 0) for value in goldstone.values()) + 1  # + the phase of D0
    state_real = [classes.get(value, 0) for value in state_classes]
    state_real[-1] -= 1  # the (1,1)_0 class holds the radial mode and the Goldstone phase
    witness_lambda = _fractions(WITNESS_LAMBDA)
    tree = core["tree_rows"]
    witness_levels = [sum((tree[s][k] * witness_lambda[k] for k in range(5)), Fraction(0)) for s in range(7)]
    level_groups: dict[Fraction, int] = {}
    for level, dim in zip(witness_levels, state_real):
        level_groups[level] = level_groups.get(level, 0) + dim
    checks["real_dimension_bookkeeping_60"] = bool(
        core["weight_vectors_ok"]
        and sum(classes.values()) == N_REAL
        and goldstone_real == 9 == core["broken_rank"]
        and tuple(state_real) == EXPECTED_STATE_REAL_DIMS
        and goldstone_real + sum(state_real) == N_REAL
        and sorted(level_groups.values()) == sorted([14, 6, 18, 12, 1])
    )
    expected_tree = [_fractions(row) for row in EXPECTED_TREE_MATRIX]
    checks["tree_mass_matrix_exact"] = tree == expected_tree
    checks["remnant_rows_sum_to_zero_radial_row_4"] = bool(
        all(sum(row) == 0 for row in tree[:6]) and tree[6] == _fractions(("0", "0", "0", "0", "4"))
    )
    # A11 Fierz.
    fierz: dict[str, list[Fraction] | None] = {}
    fierz_residuals: dict[str, list[Fraction] | None] = {}
    for channel in FIERZ_CHANNELS:
        solution, residuals = _decompose(values, [point[channel] for point in core["fierz_at_points"]])
        if fierz_override is not None and channel in fierz_override:
            solution = _fractions(fierz_override[channel])
            residuals = [
                sum((solution[k] * values[p][k] for k in range(5)), Fraction(0)) - core["fierz_at_points"][p][channel] for p in range(5, 7)
            ]
        fierz[channel] = solution
        fierz_residuals[channel] = residuals
    checks["fierz_vectors_exact"] = bool(
        all(fierz[channel] == _fractions(EXPECTED_FIERZ[channel]) for channel in FIERZ_CHANNELS)
        and all(residual is not None and all(value == 0 for value in residual) for residual in fierz_residuals.values())
    )
    # A12 210 channels.
    dims_210 = sum(PS_DIMENSIONS[a] * PS_DIMENSIONS[b] * PS_DIMENSIONS[c] for a, b, c in PS_CONTENT_210)
    bilinear = {(a, "1", c) for a in DELTA_BILINEAR_SU4 for c in DELTA_BILINEAR_SU2R}
    bilinear_dim = sum(PS_DIMENSIONS[a] * PS_DIMENSIONS[c] for a, _b, c in bilinear)
    coupling = [f"({a},{b},{c})" for a, b, c in PS_CONTENT_210 if (a, b, c) in bilinear]
    gap_shift = {}
    for channel in FIERZ_CHANNELS:
        vector = fierz.get(channel)
        gap_shift[channel] = None if vector is None else vector[3] - vector[4]
    checks["exchange_channels_of_210_never_lower_gap"] = bool(
        dims_210 == 210
        and bilinear_dim == 900
        and tuple(coupling) == EXCHANGE_CHANNELS
        and all(gap_shift[channel] is not None and gap_shift[channel] <= 0 for channel in EXCHANGE_CHANNELS)
        and gap_shift["(1,1,3)"] == 0
    )
    # A13 SM identity.
    sm = core["sm_higgs"]
    checks["beta_route_reproduces_sm_higgs"] = bool(sm["identity_exact"])
    # A14-A16 beta tensors.
    q_tensor: dict[tuple[int, int], list[Fraction] | None] = {}
    q_residuals: dict[tuple[int, int], list[Fraction] | None] = {}
    for key in EXPECTED_Q:
        solution, residuals = _decompose(values, [traces[key] for traces in core["scalar_traces"]])
        if beta_override is not None and key in beta_override:
            solution = _fractions(beta_override[key])
            residuals = [sum((solution[k] * values[p][k] for k in range(5)), Fraction(0)) - core["scalar_traces"][p][key] for p in range(5, 7)]
        q_tensor[key] = solution
        q_residuals[key] = residuals
    checks["beta_scalar_tensor_exact"] = bool(
        all(q_tensor[key] == _fractions(EXPECTED_Q[key]) for key in EXPECTED_Q)
        and all(residual is not None and all(value == 0 for value in residual) for residual in q_residuals.values())
    )
    o60 = [sum((q_tensor[key][k] for key in EXPECTED_Q), Fraction(0)) if all(q_tensor[key] is not None for key in EXPECTED_Q) else None for k in range(5)]
    checks["beta_scalar_tensor_o60_point_136"] = all(value == O60_POINT_SUM for value in o60)
    g_tensor: dict[str, list[Fraction] | None] = {}
    g_residuals: dict[str, list[Fraction] | None] = {}
    for monomial in GAUGE_MONOMIALS:
        solution, residuals = _decompose(values, [traces[monomial] for traces in core["gauge_traces"]])
        g_tensor[monomial] = solution
        g_residuals[monomial] = residuals
    checks["beta_gauge_tensor_exact"] = bool(
        all(g_tensor[monomial] == _fractions(EXPECTED_G[monomial]) for monomial in GAUGE_MONOMIALS)
        and all(residual is not None and all(value == 0 for value in residual) for residual in g_residuals.values())
    )
    # A17 witness betas.
    g4_squared, gr_squared = _fractions(WITNESS_GAUGE_SQUARED)
    c2d = {"g4^2": killing.get("g4"), "gR^2": killing.get("gR")}
    witness_beta16: list[Fraction] | None = None
    if all(value is not None for value in q_tensor.values()) and all(value is not None for value in g_tensor.values()) and None not in c2d.values():
        c2 = c2d["g4^2"] * g4_squared + c2d["gR^2"] * gr_squared
        monomials = {"g4^4": g4_squared**2, "gR^4": gr_squared**2, "g4^2gR^2": g4_squared * gr_squared}
        witness_beta16 = []
        for k in range(5):
            total = sum((q_tensor[(i, j)][k] * witness_lambda[i] * witness_lambda[j] for (i, j) in EXPECTED_Q), Fraction(0))
            total += sum((g_tensor[name][k] * monomials[name] for name in GAUGE_MONOMIALS), Fraction(0))
            total -= 12 * c2 * witness_lambda[k]
            witness_beta16.append(total)
    checks["witness_betas_exact"] = witness_beta16 == _fractions(EXPECTED_WITNESS_BETA16)
    return {
        "kind": "EXACT",
        "model": {
            "space": "V = 4bar (x) 4bar (x) 3 (48 complex); Delta_R = symmetric part in the two 4bar slots (30 complex = 60 real)",
            "generators": "gl(4): rho(E_ij) = -E_ji per 4bar slot; su(2)_R: Cartesian (L_m)_ab = -eps_mab, T_m = i L_m",
            "points": {"lcg_seed": LCG_SEED_GROUP, "n_points": 7, "n_solve": 5, "n_check": 2, "coefficients": "{-2..2} + i {-2..2}"},
        },
        "casimirs": {
            "C4_std_on_Delta_R": killing.get("g4"),
            "C_su2R_on_Delta_R": killing.get("gR"),
            "gl_route_2C4_equals_9_and_CR_equals_2": core["casimir_gl_route_ok"],
            "C2D_coefficients": c2d,
        },
        "sym2": {
            "basis": list(QUARTIC_BASIS),
            "casimirs": {name: list(QUARTIC_CASIMIRS[name]) for name in QUARTIC_BASIS},
            "dimensions": list(sym2["dimensions"]),
            "n_basis_pairs": len(sym2["pairs"]),
            "minimal_polynomial_2C4": "(2C4 - 12)(2C4 - 16)(2C4 - 24) = 0",
            "minimal_polynomial_CR": "CR (CR - 2)(CR - 6) = 0",
            "projectors_sum_to_identity": sym2["projectors_sum_to_identity"],
            "grams_symmetric": sym2["grams_symmetric"],
        },
        "vacuum": {
            "D0": "S_33 (x) v_{-1} (the (1,1)_0 direction)",
            "D0_norm_squared": core["d0_norm"],
            "V_at_D0": core["d0_values"],
            "su3_and_Y_annihilate_D0": bool(core["su3_annihilates"] and core["hypercharge_annihilates"]),
            "broken_generator_rank": core["broken_rank"],
        },
        "states": [
            {
                "state": name,
                "g6_label": label,
                "S": list(STATE_DIRECTIONS[name][0]),
                "T3R": STATE_DIRECTIONS[name][1],
                "Y": labels[name]["Y"],
                "C3": labels[name]["C3"],
                "real_dimension": dim,
            }
            for name, label, dim in zip(STATE_ORDER, G6_LABELS, state_real)
        ],
        "real_dimension_bookkeeping": {
            "classes_C3_Y_real_dimension": {f"C3={c3},Y={y}": dim for (c3, y), dim in sorted(classes.items())},
            "goldstone_real_dimension": goldstone_real,
            "state_real_dimensions": state_real,
            "witness_level_groups": {str(level): dim for level, dim in sorted(level_groups.items())},
        },
        "tree_mass_matrix": {
            "formula": "A_sk = ([<X1, P_k X1> + 2 Re<X0, P_k X2>]/|E|^2 - 2 delta_{k,(35,5)} |D0|^2)/|D0|^2, mu^2 = 2 lambda5 v^2",
            "rows": STATE_ORDER,
            "A": tree,
            "row_sums": [sum(row) for row in tree],
        },
        "fierz_vectors": {"f": fierz, "check_point_residuals": fierz_residuals, "gap_shift_f4_minus_f5": gap_shift},
        "exchange_channels_210": {
            "ps_content_210": [f"({a},{b},{c})" for a, b, c in PS_CONTENT_210],
            "dimension_210": dims_210,
            "delta_dagger_delta_channels": sorted(f"({a},{b},{c})" for a, b, c in bilinear),
            "channels_coupling_to_delta_dagger_delta": coupling,
            "tree_exchange_shift_of_lam4_minus_lam5": "-beta_c (f_c4 - f_c5) = +3 beta_c for (15,1,1), (15,1,3); 0 for (1,1,1)",
        },
        "sm_higgs_beta_identity": sm,
        "beta_scalar_tensor": {"Q": {f"{i},{j}": value for (i, j), value in q_tensor.items()}, "check_point_residuals": {f"{i},{j}": value for (i, j), value in q_residuals.items()}, "o60_point_sums": o60},
        "beta_gauge_tensor": {"G": g_tensor, "check_point_residuals": g_residuals},
        "beta_formula": "16 pi^2 d lambda_k/dt = sum_{i<=j} Q[(i,j)][k] lambda_i lambda_j - 12 C2D lambda_k + G[k].(g4^4, gR^4, g4^2 gR^2), C2D = (9/2) g4^2 + 2 gR^2",
        "witness_betas": {
            "lambda": witness_lambda,
            "g4_squared": g4_squared,
            "gR_squared": gr_squared,
            "beta_16pi2": witness_beta16,
            "beta_float": [float(value) / (16.0 * math.pi**2) for value in witness_beta16] if witness_beta16 else None,
        },
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (B) The repository's 126bar chart: c_qk, Krylov basis of Delta_R, witness portal squares.
# ---------------------------------------------------------------------------------------------------------------------


def _chart_pair(generators: Sequence[tuple[Any, Any, float]], xr: np.ndarray, xi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """K(X) = sum_g g X g^T = sum_g g (g X)^T for a symmetric X and Gaussian-integer g = gr + i gi (exact int64 sparse
    products; guard: sum_g l1(g)^2 max|X| < 2^62 with l1 the max row sum of |gr| + |gi|)."""
    maximum = max(_max_abs(xr), _max_abs(xi))
    if sum(l1 * l1 for _gr, _gi, l1 in generators) * maximum >= INT64_BOUND:
        raise ArithmeticError("int64 guard exceeded in a chart pair operator")
    out_real = np.zeros(xr.shape, dtype=np.int64)
    out_imag = np.zeros(xi.shape, dtype=np.int64)
    for g_real, g_imag, _l1 in generators:
        left_real = np.asarray(g_real @ xr - g_imag @ xi)
        left_imag = np.asarray(g_real @ xi + g_imag @ xr)
        out_real += np.asarray(g_real @ left_real.T - g_imag @ left_imag.T)
        out_imag += np.asarray(g_real @ left_imag.T + g_imag @ left_real.T)
    return out_real, out_imag


def _chart_apply(generator: tuple[Any, Any, float], real: np.ndarray, imag: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    g_real, g_imag, _ = generator
    return np.asarray(g_real @ real - g_imag @ imag), np.asarray(g_real @ imag + g_imag @ real)


@lru_cache(maxsize=1)
def _chart_generators() -> dict[str, Any]:
    real, imag = sos_source.integer_sigma_generators()
    pairs = list(itertools.combinations(range(10), 2))
    index = {pair: position for position, pair in enumerate(pairs)}

    def generator(pair: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
        return real[index[pair]].astype(np.int64), imag[index[pair]].astype(np.int64)

    def combine(first: tuple[int, int], second: tuple[int, int], sign: int) -> tuple[np.ndarray, np.ndarray]:
        a, b = generator(first), generator(second)
        return a[0] + sign * b[0], a[1] + sign * b[1]

    def as_sparse(pair: tuple[np.ndarray, np.ndarray]) -> tuple[Any, Any, float]:
        return sparse.csr_matrix(pair[0]), sparse.csr_matrix(pair[1]), _row_l1(np.abs(pair[0]) + np.abs(pair[1]))

    so6 = [as_sparse(generator(pair)) for pair in pairs if pair[1] <= 5]
    j_right = [combine((6, 7), (8, 9), 1), combine((6, 8), (7, 9), -1), combine((6, 9), (7, 8), 1)]
    j_left = [combine((6, 7), (8, 9), -1), combine((6, 8), (7, 9), 1), combine((6, 9), (7, 8), -1)]
    return {
        "so6": so6,
        "j_right": [as_sparse(pair) for pair in j_right],
        "j_left": [as_sparse(pair) for pair in j_left],
        "n_generators": int(real.shape[0]),
        "dimension": int(real.shape[1]),
    }


def _chart_monomials(xr: np.ndarray, xi: np.ndarray) -> dict[str, Any]:
    xr = np.asarray(xr, dtype=np.int64)
    xi = np.asarray(xi, dtype=np.int64)
    if not (np.array_equal(xr, xr.T) and np.array_equal(xi, xi.T)):
        raise ArithmeticError("chart pair tensors must be symmetric")
    gens = _chart_generators()
    k4_powers = [(xr, xi)]
    for _ in range(3):
        k4_powers.append(_chart_pair(gens["so6"], *k4_powers[-1]))
    kr_powers = [(xr, xi)]
    for _ in range(3):
        kr_powers.append(_chart_pair(gens["j_right"], *kr_powers[-1]))
    monomials = {(0, 0): (xr, xi), (0, 1): kr_powers[1], (0, 2): kr_powers[2]}
    for a in (1, 2):
        monomials[(a, 0)] = k4_powers[a]
        monomials[(a, 1)] = _chart_pair(gens["j_right"], *k4_powers[a])
        monomials[(a, 2)] = _chart_pair(gens["j_right"], *monomials[(a, 1)])
    return {"k4_powers": k4_powers, "kr_powers": kr_powers, "monomials": monomials}


@lru_cache(maxsize=1)
def _chart_projector_terms() -> tuple[tuple[int, dict[tuple[int, int], int]], ...]:
    output = []
    k4_values = tuple(K4_EIGEN[value] for value in C4_VALUES)
    kr_values = tuple(KR_EIGEN[value] for value in CR_VALUES)
    for name in QUARTIC_BASIS:
        c4, cr = QUARTIC_CASIMIRS[name]
        in_k4 = _lagrange(k4_values, K4_EIGEN[c4])
        in_kr = _lagrange(kr_values, KR_EIGEN[cr])
        coefficients = {(a, b): in_k4[a] * in_kr[b] for a in range(3) for b in range(3) if in_k4[a] * in_kr[b] != 0}
        denominator = math.lcm(*(value.denominator for value in coefficients.values()))
        output.append((denominator, {key: int(value * denominator) for key, value in coefficients.items()}))
    return tuple(output)


def _chart_quartic_values(xr: np.ndarray, xi: np.ndarray, monomials: Mapping[tuple[int, int], tuple[np.ndarray, np.ndarray]]) -> list[Fraction]:
    values = []
    xr_int = _to_int64(xr)
    xi_int = _to_int64(xi)
    for denominator, coefficients in _chart_projector_terms():
        bound = sum(abs(value) for value in coefficients.values()) * max(max(_max_abs(monomials[key][0]), _max_abs(monomials[key][1])) for key in coefficients)
        if bound >= INT64_BOUND:
            raise ArithmeticError("int64 guard exceeded in a chart projector")
        projected_real = _to_int64(sum(value * monomials[key][0] for key, value in coefficients.items()))
        projected_imag = _to_int64(sum(value * monomials[key][1] for key, value in coefficients.items()))
        values.append(Fraction(_hermitian_real(xr_int, xi_int, projected_real, projected_imag), denominator))
    return values


def _self_quartics(real: np.ndarray, imag: np.ndarray) -> dict[str, Fraction]:
    projected = candidate._integer_projected_pairs(real, imag)
    output = {}
    for channel in SELF_CHANNELS:
        projected_real, projected_imag, denominator = projected[channel]
        numerator = sum(int(value) ** 2 for value in projected_real.flat) + sum(int(value) ** 2 for value in projected_imag.flat)
        output[channel] = Fraction(numerator, denominator * denominator)
    return output


@lru_cache(maxsize=1)
def _chart_core() -> dict[str, Any]:
    started = time.time()
    gens = _chart_generators()
    sigma_real, sigma_imag = candidate.sigma_std_raw_coordinates()
    sigma = (sigma_real.astype(np.int64), sigma_imag.astype(np.int64))
    sigma_norm = _exact_dot(sigma[0], sigma[0]) + _exact_dot(sigma[1], sigma[1])
    ps_generators = gens["so6"] + gens["j_right"]
    # Exact Krylov spanning set of Delta_R (the float rank only selects; the vectors are exact).
    basis = [sigma]
    float_rows = [sigma[0] + 1j * sigma[1]]
    frontier = [sigma]
    while len(basis) < N_SYM and frontier:
        next_frontier = []
        for vector in frontier:
            for generator in ps_generators:
                image = _chart_apply(generator, vector[0], vector[1])
                as_complex = image[0] + 1j * image[1]
                if not np.any(image[0]) and not np.any(image[1]):
                    continue
                if np.linalg.matrix_rank(np.array(float_rows + [as_complex]), tol=1.0e-8) > len(float_rows):
                    basis.append(image)
                    float_rows.append(as_complex)
                    next_frontier.append(image)
                    if len(basis) == N_SYM:
                        break
            if len(basis) == N_SYM:
                break
        frontier = next_frontier
    realified = np.array(
        [np.concatenate([vector[0], vector[1]]) for vector in basis] + [np.concatenate([-vector[1], vector[0]]) for vector in basis],
        dtype=np.int64,
    )
    krylov_rank = _rank_mod_p(realified)
    # Deterministic chart points D_j = sum_i (c_ij + i d_ij) B_i, c, d in {-1, 0, 1}.
    points = []
    for j in range(7):
        stream = _lcg(LCG_SEED_CHART + j)
        real = np.zeros(sigma[0].shape, dtype=np.int64)
        imag = np.zeros(sigma[0].shape, dtype=np.int64)
        for vector in basis:
            c = next(stream) % 3 - 1
            d = next(stream) % 3 - 1
            real = real + c * vector[0] - d * vector[1]
            imag = imag + c * vector[1] + d * vector[0]
        points.append((real, imag))
    # sigma (x) sigma calibration and pair-operator minimal polynomials.
    sigma_pair = _pair_square(*sigma)
    sigma_pair_int = (sigma_pair[0].astype(np.int64), sigma_pair[1].astype(np.int64))
    sigma_monomials = _chart_monomials(*sigma_pair_int)
    k4_sigma = sigma_monomials["k4_powers"][1]
    kr_sigma = sigma_monomials["kr_powers"][1]
    calibrated = bool(
        np.array_equal(k4_sigma[0], -3 * sigma_pair_int[0])
        and np.array_equal(k4_sigma[1], -3 * sigma_pair_int[1])
        and np.array_equal(kr_sigma[0], -4 * sigma_pair_int[0])
        and np.array_equal(kr_sigma[1], -4 * sigma_pair_int[1])
    )
    j_left_kills = all(not np.any(part) for generator in gens["j_left"] for part in _chart_apply(generator, *sigma))
    j_right_acts = any(np.any(part) for generator in gens["j_right"] for part in _chart_apply(generator, *sigma))
    sigma_values = _chart_quartic_values(*sigma_pair_int, sigma_monomials["monomials"])
    sigma_self = _self_quartics(*sigma)

    def minimal_ok(monomials: Mapping[str, Any]) -> bool:
        k4 = monomials["k4_powers"]
        kr = monomials["kr_powers"]
        ok = True
        for part in (0, 1):
            residual_k4 = k4[3][part] - k4[2][part] - 9 * k4[1][part] + 9 * k4[0][part]
            residual_kr = kr[3][part] - 8 * kr[2][part] - 16 * kr[1][part] + 128 * kr[0][part]
            ok = ok and not np.any(residual_k4) and not np.any(residual_kr)
        return ok

    minimal_at_points = [minimal_ok(sigma_monomials)]
    point_values = []
    point_self = []
    point_norms = []
    for real, imag in points:
        pair = _pair_square(real, imag)
        pair_int = (pair[0].astype(np.int64), pair[1].astype(np.int64))
        monomials = _chart_monomials(*pair_int)
        minimal_at_points.append(minimal_ok(monomials))
        point_values.append(_chart_quartic_values(*pair_int, monomials["monomials"]))
        point_self.append(_self_quartics(real, imag))
        point_norms.append(_exact_dot(real, real) + _exact_dot(imag, imag))
    # Witness portal squares on the Krylov vectors (M_p, C_p as in candidate.exact_sigma_std_certificate).
    _p_form, p_float = sos_source.phi_source.pati_salam_direction()
    p_vector = np.rint(p_float).astype(np.int64)
    p_integral = bool(np.max(np.abs(p_float - p_vector)) == 0.0)
    operator_real, operator_imag = candidate.a_square_source.integer_cubic_operators()
    m_real = np.tensordot(p_vector, operator_real.astype(np.int64), axes=(0, 0))
    m_imag = np.tensordot(p_vector, operator_imag.astype(np.int64), axes=(0, 0))
    contraction_real, contraction_imag = candidate.a_square_source.integer_contraction_tensor()
    contraction_real = contraction_real.astype(np.int64)
    contraction_imag = contraction_imag.astype(np.int64)
    c_real_matrix = np.einsum("vpa,p->va", contraction_real, p_vector)
    c_imag_matrix = np.einsum("vpa,p->va", contraction_imag, p_vector)
    portal_max = 0
    for vector in [sigma] + basis:
        image_real = m_real @ vector[0] - m_imag @ vector[1]
        image_imag = m_real @ vector[1] + m_imag @ vector[0]
        c_real = c_real_matrix @ vector[0] - c_imag_matrix @ vector[1]
        c_imag = c_real_matrix @ vector[1] + c_imag_matrix @ vector[0]
        portal_max = max(
            portal_max,
            int(np.max(np.abs(image_real - 2 * vector[0]))),
            int(np.max(np.abs(image_imag - 2 * vector[1]))),
            int(np.max(np.abs(c_real))),
            int(np.max(np.abs(c_imag))),
        )
    return {
        "generator_counts": {"so10": gens["n_generators"], "so6": len(gens["so6"]), "su2R_J": len(gens["j_right"]), "chart_dimension": gens["dimension"]},
        "sigma_norm": sigma_norm,
        "krylov_size": len(basis),
        "krylov_max_entry": max(max(int(np.max(np.abs(vector[0]))), int(np.max(np.abs(vector[1])))) for vector in basis),
        "krylov_rank_mod_p": krylov_rank,
        "realified_shape": list(realified.shape),
        "point_max_coordinate": max(max(int(np.max(np.abs(real))), int(np.max(np.abs(imag)))) for real, imag in points),
        "calibrated": calibrated,
        "j_left_kills_sigma": j_left_kills,
        "j_right_acts_on_sigma": j_right_acts,
        "minimal_at_points": minimal_at_points,
        "sigma_values": sigma_values,
        "sigma_self": sigma_self,
        "point_values": point_values,
        "point_self": point_self,
        "point_norms": point_norms,
        "p_integral": p_integral,
        "portal_max_abs": portal_max,
        "seconds": time.time() - started,
    }


def chart_section(*, cqk_override: Mapping[str, Sequence[Any]] | None = None) -> dict[str, Any]:
    core = _chart_core()
    checks: dict[str, bool] = {}
    checks["krylov_basis_spans_delta_R_exactly"] = bool(core["krylov_size"] == N_SYM and core["krylov_rank_mod_p"] == N_REAL)
    checks["ps_pair_operators_calibrated_on_sigma_std"] = bool(core["calibrated"] and core["j_left_kills_sigma"] and core["j_right_acts_on_sigma"])
    checks["ps_pair_minimal_polynomials_at_points"] = bool(all(core["minimal_at_points"]))
    completeness = all(
        sum(values) == norm * norm and sum(selfs.values()) == norm * norm
        for values, selfs, norm in zip(core["point_values"], core["point_self"], core["point_norms"])
    )
    checks["completeness_at_points"] = bool(completeness)
    cqk: dict[str, list[Fraction] | None] = {}
    residuals: dict[str, list[Fraction] | None] = {}
    for channel in SELF_CHANNELS:
        solution, residual = _decompose(core["point_values"], [selfs[channel] for selfs in core["point_self"]])
        if cqk_override is not None and channel in cqk_override:
            solution = _fractions(cqk_override[channel])
            residual = [
                sum((solution[k] * core["point_values"][p][k] for k in range(5)), Fraction(0)) - core["point_self"][p][channel] for p in range(5, 7)
            ]
        cqk[channel] = solution
        residuals[channel] = residual
    checks["c_qk_exact"] = bool(
        all(cqk[channel] == _fractions(EXPECTED_CQK[channel]) for channel in SELF_CHANNELS)
        and all(residual is not None and all(value == 0 for value in residual) for residual in residuals.values())
    )
    column_sums = (
        [sum((cqk[channel][k] for channel in SELF_CHANNELS), Fraction(0)) for k in range(5)]
        if all(cqk[channel] is not None for channel in SELF_CHANNELS)
        else None
    )
    checks["c_qk_columns_sum_to_one"] = column_sums == [1, 1, 1, 1, 1]
    sigma_fourth = core["sigma_norm"] ** 2
    checks["sigma_std_pure_35_5_and_pure_2772bar"] = bool(
        core["sigma_norm"] == candidate.SIGMA_STD_RAW_NORM_SQUARED
        and core["sigma_values"] == [0, 0, 0, 0, sigma_fourth]
        and core["sigma_self"] == {"54": 0, "1050bar": 0, "2772bar": sigma_fourth, "4125": 0}
    )
    checks["witness_portal_squares_annihilate_delta_R"] = bool(
        core["p_integral"] and core["portal_max_abs"] == 0 and checks["krylov_basis_spans_delta_R_exactly"]
    )
    swapped = {channel: str(value) for channel, value in candidate.SWAPPED_SELF_WEIGHTS.items()}
    historical = {channel: str(value) for channel, value in candidate.HISTORICAL_SELF_WEIGHTS.items()}
    checks["witness_weights_bound_to_committed_candidate"] = bool(
        swapped == EXPECTED_SWAPPED_WEIGHTS
        and historical == EXPECTED_HISTORICAL_WEIGHTS
        and candidate.SIGMA_SCALE == Fraction(1, 8)
        and tuple(candidate.SELF_CHANNELS) == ("54", "1050bar", "2772bar", "4125")
    )
    return {
        "kind": "EXACT",
        "chart": "repository 126bar chart (sos_source.integer_sigma_generators, 45 Gaussian-integer anti-Hermitian 126 x 126)",
        "generators": core["generator_counts"],
        "su2R_combinations": {
            "J_R": "(t67 + t89, t68 - t79, t69 + t78) (acts on sigma_std)",
            "J_L": "(t67 - t89, t68 + t79, t69 - t78) (annihilates sigma_std)",
        },
        "pair_operator_eigenvalues": {"K4_by_C4": {str(key): value for key, value in K4_EIGEN.items()}, "KR_by_CR": {str(key): value for key, value in KR_EIGEN.items()}},
        "krylov_basis": {
            "size": core["krylov_size"],
            "max_entry": core["krylov_max_entry"],
            "realified_shape": core["realified_shape"],
            "rank_mod_p": core["krylov_rank_mod_p"],
            "prime": GF_PRIME,
            "rank_argument": "rank over Q >= rank mod p = 60 = number of realified columns",
        },
        "points": {"lcg_seed": f"{LCG_SEED_CHART} + j", "n_points": 7, "n_solve": 5, "n_check": 2, "max_coordinate": core["point_max_coordinate"]},
        "c_qk": cqk,
        "c_qk_check_point_residuals": residuals,
        "c_qk_column_sums": column_sums,
        "sigma_std": {
            "raw_norm_squared": core["sigma_norm"],
            "V_k": core["sigma_values"],
            "I_q": core["sigma_self"],
        },
        "witness_portal": {
            "operators": "M_p, C_p from sos_source.phi_source.pati_salam_direction(), a_square_source.integer_cubic_operators() and integer_contraction_tensor()",
            "max_abs_residual_on_krylov_basis": core["portal_max_abs"],
            "p_integral": core["p_integral"],
            "consequence": "(M_p - 2) and C_p vanish on Delta_R: the witness portal squares have no phi Delta Delta^dag trilinear, beta_c(witness) = 0 exactly",
        },
        "weights": {
            "swapped_witness": swapped,
            "historical": historical,
            "sigma_scale": candidate.SIGMA_SCALE,
            "self_channels": list(candidate.SELF_CHANNELS),
        },
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (C) Tree matching at mu = M_GUT (exact, sympy).
# ---------------------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _matching_symbols() -> tuple[sympy.Symbol, ...]:
    return sympy.symbols("w_54 w_1050bar w_2772bar w_4125 beta_111 beta_15_1_1 beta_15_1_3")


def _pinned_tree_map() -> list[sympy.Expr]:
    w54, w1050, w2772, w4125, b111, b1511, b1513 = _matching_symbols()
    r = sympy.Rational
    return [
        (r(9, 35) * w54 + r(1, 2) * w1050 + r(1, 10) * w2772 + r(1, 7) * w4125) / 8 - b111 + r(3, 2) * b1511 - 3 * b1513,
        w4125 / 8 - b111 - r(3, 2) * b1511 + 3 * b1513,
        (r(4, 9) * w1050 + r(1, 9) * w2772 + r(4, 9) * w4125) / 8 - b111 + r(1, 2) * b1511 - r(1, 2) * b1513,
        w4125 / 8 - b111 + r(3, 2) * b1511 + r(3, 2) * b1513,
        w2772 / 8 - b111 - r(3, 2) * b1511 - r(3, 2) * b1513,
    ]


def tree_map(weights: Mapping[str, Any], betas: Mapping[str, Any], cqk: Mapping[str, Sequence[Any]], fierz: Mapping[str, Sequence[Any]]) -> list[Any]:
    """lambda_k = (1/8) sum_q w_q c_qk - sum_c beta_c f_ck (works for Fractions, floats and sympy symbols)."""
    output = []
    for k in range(5):
        value = sum((weights[channel] * cqk[channel][k] for channel in SELF_CHANNELS), 0) / 8
        value -= sum((betas[channel] * fierz[channel][k] for channel in EXCHANGE_CHANNELS), 0)
        output.append(value)
    return output


def _sympy_rational(value: Fraction) -> sympy.Rational:
    return sympy.Rational(value.numerator, value.denominator)


def load_g6_tree_report(path: Path = G6_TREE_JSON) -> dict[str, Any] | None:
    try:
        report = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return report if isinstance(report, dict) else None


def g6_tree_level_pairs(report: Any) -> set[tuple[str, str, int]] | None:
    """(label, mu, real dim) of every light r0 -> 0 branch mu != 0 of the committed G6 certificate (fail closed)."""
    try:
        if not isinstance(report, dict) or report.get("status") != G6_TREE_STATUS:
            return None
        n_failed = report.get("n_failed")
        if not isinstance(n_failed, int) or isinstance(n_failed, bool) or n_failed != 0:
            return None
        pairs = set()
        for factor in report["parametric_spectrum"]["factors"]:
            limits = factor.get("r0_to_0")
            if not isinstance(limits, dict):
                continue
            mus = (limits.get("light_branches") or {}).get("mu_limits_rational")
            if not isinstance(mus, list) or len(mus) != 1 or mus[0] == "0":
                continue
            mu = Fraction(mus[0])
            for label, dim in factor["sm_content_per_root_real"].items():
                pairs.add((str(label), str(mu), int(dim)))
        return pairs
    except (KeyError, TypeError, ValueError, AttributeError, ZeroDivisionError):
        return None


def matching_section(
    group: Mapping[str, Any],
    chart: Mapping[str, Any],
    *,
    witness_weights: Mapping[str, Any] | None = None,
    g6_tree_report: Any = _DEFAULT,
) -> dict[str, Any]:
    weights = {channel: Fraction(value) for channel, value in (candidate.SWAPPED_SELF_WEIGHTS if witness_weights is None else witness_weights).items()}
    report = load_g6_tree_report() if g6_tree_report is _DEFAULT else g6_tree_report
    cqk = chart["c_qk"]
    fierz = group["fierz_vectors"]["f"]
    tree = group["tree_mass_matrix"]["A"]
    checks: dict[str, bool] = {}
    inputs_ok = all(cqk.get(channel) is not None for channel in SELF_CHANNELS) and all(fierz.get(channel) is not None for channel in FIERZ_CHANNELS)
    symbols = _matching_symbols()
    w54, w1050, w2772, w4125, b111, b1511, b1513 = symbols
    symbolic_weights = {"54": w54, "1050bar": w1050, "2772bar": w2772, "4125": w4125}
    symbolic_betas = {"(1,1,1)": b111, "(15,1,1)": b1511, "(15,1,3)": b1513}
    if inputs_ok:
        cqk_sym = {channel: [_sympy_rational(value) for value in cqk[channel]] for channel in SELF_CHANNELS}
        fierz_sym = {channel: [_sympy_rational(value) for value in fierz[channel]] for channel in FIERZ_CHANNELS}
        symbolic = [sympy.expand(value) for value in tree_map(symbolic_weights, symbolic_betas, cqk_sym, fierz_sym)]
    else:
        symbolic = None
    pinned = _pinned_tree_map()
    checks["tree_map_symbolic"] = bool(symbolic is not None and all(sympy.expand(a - b) == 0 for a, b in zip(symbolic, pinned)))
    gap_identity_form = (w4125 - w2772) / 8 + 3 * b1511 + 3 * b1513
    gap = sympy.expand(symbolic[3] - symbolic[4]) if symbolic is not None else None
    checks["gap_identity_exact"] = bool(gap is not None and sympy.expand(gap - gap_identity_form) == 0)
    # C03: Farkas certificate of gap >= 0 on W_SOS x R^3_{>=0} (multipliers read off the linear form).
    certificate = None
    if gap is not None:
        coefficient = {channel: Fraction(str(sympy.expand(gap).coeff(symbolic_weights[channel]))) for channel in SELF_CHANNELS}
        beta_coefficient = {channel: Fraction(str(sympy.expand(gap).coeff(symbolic_betas[channel]))) for channel in EXCHANGE_CHANNELS}
        constant = sympy.expand(gap).subs({symbol: 0 for symbol in symbols})
        cone = {channel: coefficient[channel] for channel in SOS_CONE_ROWS}
        w2772_multiplier = coefficient["2772bar"] + sum(cone.values(), Fraction(0))
        certificate = {
            "cone_row_multipliers_w_q_minus_w_2772": cone,
            "w_2772_multiplier": w2772_multiplier,
            "beta_multipliers": beta_coefficient,
            "constant": str(constant),
            "binding_row": [channel for channel, value in cone.items() if value > 0],
        }
        rebuilt = sum((_sympy_rational(cone[channel]) * (symbolic_weights[channel] - w2772) for channel in SOS_CONE_ROWS), sympy.Integer(0))
        rebuilt += _sympy_rational(w2772_multiplier) * w2772
        rebuilt += sum((_sympy_rational(beta_coefficient[channel]) * symbolic_betas[channel] for channel in EXCHANGE_CHANNELS), sympy.Integer(0))
        certificate["exact"] = bool(sympy.expand(rebuilt - gap) == 0 and constant == 0)
        certificate["nonnegative"] = bool(
            all(value >= 0 for value in cone.values()) and w2772_multiplier >= 0 and all(value >= 0 for value in beta_coefficient.values())
        )
    checks["sos_family_forces_gap_nonnegative"] = bool(
        certificate is not None and certificate["exact"] and certificate["nonnegative"] and certificate["binding_row"] == ["4125"]
    )
    at_zero = [sympy.expand(value.subs({b111: 0, b1511: 0, b1513: 0})) for value in symbolic] if symbolic is not None else None
    checks["lambda2_equals_lambda4_without_exchange"] = bool(
        at_zero is not None and sympy.expand(at_zero[1] - w4125 / 8) == 0 and sympy.expand(at_zero[3] - w4125 / 8) == 0 and sympy.expand(at_zero[4] - w2772 / 8) == 0
    )
    zero_betas = {channel: Fraction(0) for channel in EXCHANGE_CHANNELS}
    witness_lambda = tree_map(weights, zero_betas, cqk, fierz) if inputs_ok else None
    witness_gap = witness_lambda[3] - witness_lambda[4] if witness_lambda is not None else None
    strictly_inside = all(value > 0 for value in weights.values()) and all(weights[channel] > weights["2772bar"] for channel in SOS_CONE_ROWS)
    beta_zero = bool(chart["checks"]["witness_portal_squares_annihilate_delta_R"])
    checks["witness_couplings_exact"] = bool(
        witness_lambda == _fractions(WITNESS_LAMBDA) and witness_gap == Fraction(1, 128) and strictly_inside and beta_zero
    )
    levels = [sum((tree[s][k] * witness_lambda[k] for k in range(5)), Fraction(0)) for s in range(7)] if witness_lambda is not None else None
    checks["witness_tree_levels_exact"] = levels == _fractions(WITNESS_LEVELS)
    g6_pairs = g6_tree_level_pairs(report)
    expected_pairs = None
    if levels is not None:
        state_dims = [row["real_dimension"] for row in group["states"]]
        expected_pairs = {(label, str(level), int(dim)) for label, level, dim in zip(G6_LABELS, levels, state_dims)}
        expected_pairs.add(("(1,1)_|Y|=0", "4", 1))
    checks["witness_tree_levels_match_committed_g6_certificate"] = bool(g6_pairs is not None and expected_pairs is not None and g6_pairs == expected_pairs)
    historical = {channel: Fraction(value) for channel, value in candidate.HISTORICAL_SELF_WEIGHTS.items()}
    historical_lambda = tree_map(historical, zero_betas, cqk, fierz) if inputs_ok else None
    historical_gap = historical_lambda[3] - historical_lambda[4] if historical_lambda is not None else None
    checks["historical_unswapped_weights_violate_gap"] = historical_gap == Fraction(-1, 128)
    checks["tree_vacuum_requires_positive_gap"] = bool(
        tree[0] == [0, 0, 0, Fraction(4, 3), Fraction(-4, 3)] and tree[6] == [0, 0, 0, 0, 4]
    )
    return {
        "kind": "EXACT",
        "tree_map": {
            "formula": "lambda_k(w, beta) = (1/8) sum_q w_q c_qk - sum_c beta_c f_ck, beta_c >= 0 (tree 210 exchange)",
            "components": [str(value) for value in symbolic] if symbolic is not None else None,
            "gap_lam4_minus_lam5": str(gap) if gap is not None else None,
            "gap_identity": "lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3)",
            "lambda_at_zero_exchange": [str(value) for value in at_zero] if at_zero is not None else None,
        },
        "sos_cone": {
            "W_SOS": "w in Q^4_{>0}: w_54 >= w_2772, w_1050bar >= w_2772, w_4125 >= w_2772",
            "farkas_certificate": certificate,
        },
        "witness": {
            "weights": weights,
            "beta": zero_betas,
            "lambda": witness_lambda,
            "lam4_minus_lam5": witness_gap,
            "strictly_inside_W_SOS": strictly_inside,
            "tree_levels": dict(zip(STATE_ORDER, levels)) if levels is not None else None,
        },
        "g6_cross_check": {
            "report": G6_TREE_JSON.name,
            "required_status": G6_TREE_STATUS,
            "pairs_from_certificate": sorted(list(pair) for pair in g6_pairs) if g6_pairs is not None else None,
            "expected_pairs": sorted(list(pair) for pair in expected_pairs) if expected_pairs is not None else None,
            "extra_level": "(1,1)_|Y|=0 at 4 r0^2 is the S radial mode, not a Delta_R state",
        },
        "historical_weights": {"weights": historical, "lambda": historical_lambda, "lam4_minus_lam5": historical_gap},
        "tree_vacuum_rows": {"(6,1)_4/3": tree[0], "radial": tree[6], "meaning": "a tree vacuum needs lambda4 > lambda5 and lambda5 > 0"},
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (D) Running (float, recomputed).
# ---------------------------------------------------------------------------------------------------------------------


def _float_fraction(value: Any) -> float:
    return float(Fraction(value))


def _rk4(function: Callable[[float, np.ndarray], np.ndarray], t: float, y: np.ndarray, h: float) -> np.ndarray:
    k1 = function(t, y)
    k2 = function(t + h / 2, y + h / 2 * k1)
    k3 = function(t + h / 2, y + h / 2 * k2)
    k4 = function(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def _gauge_rhs(b: np.ndarray, bij: np.ndarray, cy: np.ndarray) -> Callable[[float, np.ndarray], np.ndarray]:
    pi = math.pi

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        a = y[:3]
        g2 = 4 * pi / a
        yp = y[3]
        da = -b / (2 * pi) - bij @ (1.0 / a) / (8 * pi**2) + (cy * yp * yp) / (32 * pi**3)
        dy = yp / (16 * pi**2) * (6.0 * yp * yp - 45.0 / 4.0 * g2[0] - 9.0 / 4.0 * g2[1] - 9.0 / 4.0 * g2[2])
        return np.array([*da, dy])

    return rhs


@lru_cache(maxsize=16)
def _gauge_profile(m_i: float, m_gut: float, rho: float | None, y_mi: tuple[float, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Two-loop PS gauge (+ y_PS) profile from t_I = ln M_I: RK4 step 0.05, a step boundary at t_s = ln(rho M_I),
    spectator coefficients above t_s, last step ending at ln M_GUT + 0.1.  Returns (t grid, (g4, gL, gR))."""
    coefficients = PS_GAUGE_COEFFICIENTS
    b = np.array([_float_fraction(value) for value in coefficients["b"]])
    bij = np.array([[_float_fraction(value) for value in row] for row in coefficients["b_ij"]])
    cy = np.array([_float_fraction(value) for value in coefficients["c_Y"]])
    sb = np.array([_float_fraction(value) for value in coefficients["spectator_b"]])
    sbij = np.array([[_float_fraction(value) for value in row] for row in coefficients["spectator_b_ij"]])
    below = _gauge_rhs(b, bij, cy)
    above = _gauge_rhs(b + sb, bij + sbij, cy)
    t_i = math.log(m_i)
    t_s = math.log(rho * m_i) if rho is not None else 1.0e9
    t_top = math.log(m_gut) + PROFILE_TOP_MARGIN
    t = t_i
    y = np.array(y_mi, dtype=float)
    grid = [t]
    values = [y.copy()]
    while t < t_top - 1.0e-12:
        t_next = min(t_top, t + PROFILE_STEP)
        if t < t_s <= t_next:
            t_next = t_s
        function = below if t < t_s - 1.0e-12 else above
        y = _rk4(function, t, y, t_next - t)
        t = t_next
        grid.append(t)
        values.append(y.copy())
    grid_array = np.array(grid)
    couplings = np.sqrt(4 * math.pi / np.array(values)[:, :3])
    return grid_array, couplings


def _profile_key(inputs: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        float(inputs["M_I"]),
        float(inputs["M_GUT"]),
        None if inputs.get("rho") is None else float(inputs["rho"]),
        tuple(float(value) for value in inputs["y_MI"]),
    )


def _profile_for(inputs: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    return _gauge_profile(*_profile_key(inputs))


def _beta_key(q_tensor: Mapping[str, Sequence[Fraction]], g_tensor: Mapping[str, Sequence[Fraction]], c2d: Mapping[str, Fraction]) -> tuple[Any, ...]:
    """Hashable float version of the exact beta data: (Q[k, i, j] symmetrised, G[k, m], (C2D_4, C2D_R))."""
    q = np.zeros((5, 5, 5))
    for key, values in q_tensor.items():
        i, j = (int(part) for part in key.split(","))
        for k in range(5):
            value = float(values[k])
            if i == j:
                q[k, i, i] = value
            else:
                q[k, i, j] = value / 2
                q[k, j, i] = value / 2
    g = tuple(tuple(float(g_tensor[name][k]) for name in GAUGE_MONOMIALS) for k in range(5))
    return tuple(q.ravel().tolist()), g, (float(c2d["g4^2"]), float(c2d["gR^2"]))


def _flow_for(profile_key: tuple[Any, ...], beta_key: tuple[Any, ...]) -> "_Flow":
    q = np.array(beta_key[0]).reshape(5, 5, 5)
    g = np.array(beta_key[1])
    return _Flow(_gauge_profile(*profile_key), q, g, beta_key[2])


@lru_cache(maxsize=128)
def _cached_run(profile_key: tuple[Any, ...], beta_key: tuple[Any, ...], lam0: tuple[float, ...], t_a: float, t_b: float) -> dict[str, Any]:
    result = _flow_for(profile_key, beta_key).run(lam0, t_a, t_b)
    lam_end = result["lambda_end"]
    return {
        "lambda_end": None if lam_end is None else tuple(float(value) for value in lam_end),
        "crossing": result["crossing"],
        "events": dict(result["events"]),
        "completed": result["completed"],
    }


@lru_cache(maxsize=32)
def _cached_grid_scan(profile_key: tuple[Any, ...], beta_key: tuple[Any, ...], map_key: tuple[Any, ...], tree_key: tuple[Any, ...]) -> dict[str, Any]:
    """D11: the SOS-safe weight grid, tree-matched at M_GUT and run to v_R (batched RK4, blow-up cap)."""
    cqk_rows, fierz_rows = map_key
    weights = []
    betas = []
    for w2772 in D11_GRID["w_2772bar"]:
        for d54, d1050, d4125 in itertools.product(D11_GRID["w_q_minus_w_2772bar"], repeat=3):
            for beta in itertools.product(D11_GRID["beta"], repeat=3):
                base = _float_fraction(w2772)
                weights.append([base + _float_fraction(d54), base + _float_fraction(d1050), base, base + _float_fraction(d4125)])
                betas.append([_float_fraction(value) for value in beta])
    lam_grid = np.array(weights) @ np.array(cqk_rows) / 8.0 - np.array(betas) @ np.array(fierz_rows)
    m_i, m_gut = profile_key[0], profile_key[1]
    final, alive = _flow_for(profile_key, beta_key).run_batch(lam_grid, math.log(m_gut), math.log(m_i), int(D11_GRID["rk4_steps"]), float(D11_GRID["blow_up_cap"]))
    levels = final @ np.array(tree_key).T
    positive = alive & np.all(levels > 0, axis=1)
    return {
        "n_points": int(lam_grid.shape[0]),
        "not_blown_up": int(np.sum(alive)),
        "tree_vacuum_at_v_R": int(np.sum(positive)),
        "min_lambda5_vR_not_blown_up": float(np.min(final[alive, 4])) if np.any(alive) else None,
        "max_lambda5_vR_not_blown_up": float(np.max(final[alive, 4])) if np.any(alive) else None,
    }


def _gauge_rhs_pair() -> tuple[Callable[[float, np.ndarray], np.ndarray], Callable[[float, np.ndarray], np.ndarray]]:
    """(below, above) the spectator threshold: the two-loop PS gauge + y_PS right-hand sides."""
    coefficients = PS_GAUGE_COEFFICIENTS
    b = np.array([_float_fraction(value) for value in coefficients["b"]])
    bij = np.array([[_float_fraction(value) for value in row] for row in coefficients["b_ij"]])
    cy = np.array([_float_fraction(value) for value in coefficients["c_Y"]])
    sb = np.array([_float_fraction(value) for value in coefficients["spectator_b"]])
    sbij = np.array([[_float_fraction(value) for value in row] for row in coefficients["spectator_b_ij"]])
    return _gauge_rhs(b, bij, cy), _gauge_rhs(b + sb, bij + sbij, cy)


@lru_cache(maxsize=32)
def _joint_reference(
    profile_key: tuple[Any, ...], beta_key: tuple[Any, ...], region: tuple[float, ...], witness: tuple[float, ...], step: float
) -> dict[str, Any]:
    """Accuracy reference: the gauge couplings (alpha^-1, y_PS) and the quartics integrated JOINTLY by RK4 (no
    interpolation of a tabulated profile), uniform steps <= step on each side of the spectator threshold.  The region
    point runs up from ln M_I to ln M_GUT; the witness runs down from ln M_GUT with the gauge state reached there, and
    its lambda5 zero crossing is located by BISECTIONS bisections of single joint RK4 sub-steps."""
    m_i, m_gut, rho, y_mi = profile_key
    below, above = _gauge_rhs_pair()
    q = np.array(beta_key[0]).reshape(5, 5, 5)
    g_tensor = np.array(beta_key[1])
    c2d = beta_key[2]
    kp = 1.0 / (16.0 * math.pi**2)
    t_i, t_g = math.log(m_i), math.log(m_gut)
    t_s = math.log(rho * m_i) if rho is not None else 1.0e9

    def joint(gauge_rhs: Callable[[float, np.ndarray], np.ndarray]) -> Callable[[float, np.ndarray], np.ndarray]:
        def rhs(t: float, state: np.ndarray) -> np.ndarray:
            y = state[:4]
            lam = state[4:]
            g2 = 4 * math.pi / y[:3]
            g42, gr2 = g2[0], g2[2]
            c2 = c2d[0] * g42 + c2d[1] * gr2
            quadratic = np.einsum("kij,i,j->k", q, lam, lam)
            d_lam = kp * (quadratic - 12 * c2 * lam + g_tensor @ np.array([g42 * g42, gr2 * gr2, g42 * gr2]))
            return np.concatenate([gauge_rhs(t, y), d_lam])

        return rhs

    split = t_i < t_s < t_g
    up_nodes = [t_i, t_s, t_g] if split else [t_i, t_g]
    state = np.concatenate([np.array(y_mi, dtype=float), np.array(region, dtype=float)])
    t = t_i
    completed = True
    for start, stop in zip(up_nodes[:-1], up_nodes[1:]):
        function = joint(below if start < t_s - 1.0e-12 else above)
        n = max(1, math.ceil((stop - start) / step))
        h = (stop - start) / n
        for _ in range(n):
            state = _rk4(function, t, state, h)
            t += h
            if not np.all(np.isfinite(state)) or float(np.max(np.abs(state[4:]))) > 1.0e3:
                completed = False
                break
        if not completed:
            break
    lam_gut = tuple(float(value) for value in state[4:]) if completed else None
    crossing = None
    if completed:
        down_nodes = [t_g, t_s, t_i] if split else [t_g, t_i]
        current = np.concatenate([state[:4], np.array(witness, dtype=float)])
        t = t_g
        for start, stop in zip(down_nodes[:-1], down_nodes[1:]):
            function = joint(below if stop < t_s - 1.0e-12 else above)
            n = max(1, math.ceil((start - stop) / step))
            h = (stop - start) / n
            for _ in range(n):
                new = _rk4(function, t, current, h)
                if new[8] <= 0 < current[8]:
                    low, high, state_low = t, t + h, current
                    for _ in range(BISECTIONS):
                        middle = 0.5 * (low + high)
                        trial = _rk4(function, low, state_low, middle - low)
                        if trial[8] > 0:
                            low, state_low = middle, trial
                        else:
                            high = middle
                    crossing = math.exp(0.5 * (low + high))
                    break
                current = new
                t += h
            if crossing is not None:
                break
    return {"lambda_GUT": lam_gut, "crossing": crossing, "step": step}


def _accuracy_estimate(
    profile_inputs: Mapping[str, Mapping[str, Any]],
    beta_key: tuple[Any, ...],
    witness: tuple[float, ...],
    region_points: Mapping[str, Sequence[float]],
    per_profile: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Primary (interpolated-profile) running against the joint reference at two step sizes."""
    budget = ACCURACY_BUDGET
    output: dict[str, Any] = {}
    ok = True
    for tag in PROFILE_TAGS:
        key = _profile_key(profile_inputs[tag])
        region = tuple(float(value) for value in region_points[tag])
        coarse, fine = (_joint_reference(key, beta_key, region, witness, step) for step in JOINT_REFERENCE_STEPS)
        primary_lam = per_profile[tag]["region_point_lambda_GUT"]
        primary_crossing = per_profile[tag]["witness_lambda5_zero_crossing_GeV"]
        entry: dict[str, Any] = {"reference_lambda_GUT": fine["lambda_GUT"], "reference_crossing_GeV": fine["crossing"]}
        if None in (coarse["lambda_GUT"], fine["lambda_GUT"], coarse["crossing"], fine["crossing"], primary_lam, primary_crossing):
            ok = False
            output[tag] = entry
            continue
        reference_gap = fine["lambda_GUT"][3] - fine["lambda_GUT"][4]
        entry.update(
            {
                "reference_gap_lam4_minus_lam5_GUT": reference_gap,
                "reference_self_convergence_lambda_abs": max(abs(a - b) for a, b in zip(coarse["lambda_GUT"], fine["lambda_GUT"])),
                "reference_self_convergence_crossing_rel": abs(coarse["crossing"] / fine["crossing"] - 1.0),
                "primary_minus_reference_lambda_GUT_max_abs": max(abs(a - b) for a, b in zip(primary_lam, fine["lambda_GUT"])),
                "primary_minus_reference_gap_abs": abs((primary_lam[3] - primary_lam[4]) - reference_gap),
                "primary_over_reference_crossing_minus_1": primary_crossing / fine["crossing"] - 1.0,
            }
        )
        ok = ok and bool(
            entry["reference_self_convergence_lambda_abs"] <= budget["reference_convergence_abs"]
            and entry["reference_self_convergence_crossing_rel"] <= budget["reference_convergence_rel"]
            and entry["primary_minus_reference_lambda_GUT_max_abs"] <= budget["lambda_gut_abs"]
            and entry["primary_minus_reference_gap_abs"] <= budget["gap_abs"]
            and abs(entry["primary_over_reference_crossing_minus_1"]) <= budget["crossing_rel"]
            and reference_gap < 0
            and per_profile[tag]["v_R_GeV"] < fine["crossing"] < per_profile[tag]["M_GUT_GeV"]
        )
        output[tag] = entry
    return {
        "method": (
            f"joint RK4 of (alpha_4^-1, alpha_L^-1, alpha_R^-1, y_PS, lambda_1..5) without interpolation, uniform steps "
            f"<= {JOINT_REFERENCE_STEPS[0]} and <= {JOINT_REFERENCE_STEPS[1]} on each side of ln(rho M_I); the finer "
            "one is the reference"
        ),
        "budget": dict(budget),
        "per_profile": output,
        "within_budget": bool(ok),
        "meaning": (
            "the primary running interpolates the tabulated profile linearly (np.interp, as in the research and skeptic "
            "codes); its error against the joint reference is about 2e-6 in lambda(M_GUT), 1e-6 in lambda4 - lambda5 "
            "and 1e-5 relative in the crossing, far below every margin used (>= 0.1 in the gap)"
        ),
    }


class _Flow:
    """One-loop Delta_R quartic running on a tabulated gauge profile (float, RK4)."""

    def __init__(self, profile: tuple[np.ndarray, np.ndarray], q: np.ndarray, g: np.ndarray, c2d: tuple[float, float]) -> None:
        self.grid, self.couplings = profile
        self.q = q
        self.g = g
        self.c2d = c2d
        self.kp = 1.0 / (16.0 * math.pi**2)

    def gauge(self, t: float) -> tuple[float, float]:
        return float(np.interp(t, self.grid, self.couplings[:, 0])), float(np.interp(t, self.grid, self.couplings[:, 2]))

    def beta(self, lam: np.ndarray, g4: float, gr: float) -> np.ndarray:
        g42, gr2 = g4 * g4, gr * gr
        c2 = self.c2d[0] * g42 + self.c2d[1] * gr2
        quadratic = np.einsum("kij,...i,...j->...k", self.q, lam, lam)
        return self.kp * (quadratic - 12 * c2 * lam + self.g @ np.array([g42 * g42, gr2 * gr2, g42 * gr2]))

    def step(self, lam: np.ndarray, a: float, b: float) -> np.ndarray:
        h = b - a
        g_a, g_m, g_b = self.gauge(a), self.gauge(0.5 * (a + b)), self.gauge(b)
        k1 = self.beta(lam, *g_a)
        k2 = self.beta(lam + h / 2 * k1, *g_m)
        k3 = self.beta(lam + h / 2 * k2, *g_m)
        k4 = self.beta(lam + h * k3, *g_b)
        return lam + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    def run(self, lam0: Sequence[float], t_a: float, t_b: float, n_steps: int = RUN_STEPS) -> dict[str, Any]:
        """Run from t_a to t_b (either direction); record the lambda5 zero crossing (60 bisections inside the step, each
        a single RK4 sub-step from the bracket start) and the first step ends with max|lambda| > 4 pi and > 1e3."""
        lam = np.array(lam0, dtype=float)
        grid = np.linspace(t_a, t_b, n_steps + 1)
        crossing = None
        events: dict[str, float | None] = {"4pi": None, "1e3": None}
        for index in range(n_steps):
            a, b = grid[index], grid[index + 1]
            new = self.step(lam, a, b)
            if crossing is None and new[4] <= 0 < lam[4]:
                low, high, lam_low = a, b, lam
                for _ in range(BISECTIONS):
                    middle = 0.5 * (low + high)
                    trial = self.step(lam_low, low, middle)
                    if trial[4] > 0:
                        low, lam_low = middle, trial
                    else:
                        high = middle
                crossing = math.exp(0.5 * (low + high))
            lam = new
            if not np.all(np.isfinite(lam)):
                events["1e3"] = events["1e3"] or math.exp(b)
                events["4pi"] = events["4pi"] or math.exp(b)
                return {"lambda_end": None, "crossing": crossing, "events": events, "completed": False}
            largest = float(np.max(np.abs(lam)))
            if events["4pi"] is None and largest > FOUR_PI:
                events["4pi"] = math.exp(b)
            if largest > 1.0e3:
                events["1e3"] = math.exp(b)
                return {"lambda_end": lam, "crossing": crossing, "events": events, "completed": False}
        return {"lambda_end": lam, "crossing": crossing, "events": events, "completed": True}

    def run_batch(self, lam0: np.ndarray, t_a: float, t_b: float, n_steps: int, cap: float) -> tuple[np.ndarray, np.ndarray]:
        lam = np.array(lam0, dtype=float)
        alive = np.ones(lam.shape[0], dtype=bool)
        grid = np.linspace(t_a, t_b, n_steps + 1)
        for index in range(n_steps):
            rows = np.flatnonzero(alive)
            if rows.size == 0:
                break
            with np.errstate(over="ignore", invalid="ignore"):
                new = self.step(lam[rows], grid[index], grid[index + 1])
            bad = ~np.all(np.isfinite(new), axis=1) | (np.max(np.abs(np.nan_to_num(new, nan=np.inf)), axis=1) > cap)
            lam[rows[~bad]] = new[~bad]
            alive[rows[bad]] = False
        return lam, alive


def matching_lp(
    target: Sequence[float],
    cqk: Mapping[str, Sequence[Fraction]],
    fierz: Mapping[str, Sequence[Fraction]],
    cone_rows: Sequence[str],
    *,
    direction: Sequence[float] | None = None,
    mode: str = "slack",
    slack_bound: float | None = None,
    scale_max: float | None = None,
) -> float | None:
    """LP over (w_54, w_1050bar, w_2772bar, w_4125, beta_111, beta_1511, beta_1513, delta_1..5, s[, sigma]):
    (1/8) c^T w - f^T beta + delta (+ sigma direction) = target, |delta_k| <= s, w_2772 - w_q <= 0 for the cone rows,
    w, beta >= 0.  mode "slack": min s (sigma in [0, scale_max] if a direction is given); mode "scale": min sigma with
    s <= slack_bound.  Returns the optimum or None if infeasible."""
    c = np.array([[float(value) for value in cqk[channel]] for channel in SELF_CHANNELS])
    f = np.array([[float(value) for value in fierz[channel]] for channel in EXCHANGE_CHANNELS])
    with_scale = direction is not None
    n = 4 + 3 + 5 + 1 + (1 if with_scale else 0)
    s_index = 12
    a_eq = np.zeros((5, n))
    a_eq[:, 0:4] = c.T / 8.0
    a_eq[:, 4:7] = -f.T
    a_eq[:, 7:12] = np.eye(5)
    if with_scale:
        a_eq[:, 13] = np.asarray(direction, dtype=float)
    rows = []
    for k in range(5):
        row = np.zeros(n)
        row[7 + k] = 1.0
        row[s_index] = -1.0
        rows.append(row)
        row = np.zeros(n)
        row[7 + k] = -1.0
        row[s_index] = -1.0
        rows.append(row)
    for channel in cone_rows:
        row = np.zeros(n)
        row[SELF_CHANNELS.index("2772bar")] = 1.0
        row[SELF_CHANNELS.index(channel)] = -1.0
        rows.append(row)
    bounds = [(0, None)] * 7 + [(None, None)] * 5
    objective = np.zeros(n)
    if mode == "slack":
        bounds.append((0, None))
        objective[s_index] = 1.0
        if with_scale:
            bounds.append((0, scale_max))
    elif mode == "scale":
        if not with_scale:
            raise ValueError("scale mode needs a direction")
        bounds.append((0, slack_bound))
        bounds.append((0, None))
        objective[13] = 1.0
    else:
        raise ValueError(mode)
    result = linprog(objective, A_ub=np.array(rows), b_ub=np.zeros(len(rows)), A_eq=a_eq, b_eq=np.asarray(target, dtype=float), bounds=bounds, method="highs")
    if result.status != 0:
        return None
    return float(result.fun)


def gap_excludes_sos_tree_image(lam_gut: Sequence[float]) -> bool:
    """D05 predicate: lambda4 - lambda5 < 0 at M_GUT puts lambda outside the SOS tree-matching image (C03)."""
    return bool(float(lam_gut[3]) - float(lam_gut[4]) < 0)


def _close(value: float | None, expected: float, *, rel: float | None = None, abs_tol: float | None = None) -> bool:
    if value is None or not math.isfinite(value):
        return False
    if rel is not None:
        return abs(value - expected) <= rel * abs(expected)
    return abs(value - expected) <= abs_tol


def running_section(
    group: Mapping[str, Any],
    chart: Mapping[str, Any],
    matching: Mapping[str, Any],
    *,
    profile_inputs: Mapping[str, Mapping[str, Any]] | None = None,
    region_points: Mapping[str, Sequence[float]] | None = None,
    thresholds: Mapping[str, Sequence[float]] | None = None,
    sos_cone_rows: Sequence[str] | None = None,
    research_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.time()
    profile_inputs = PROFILE_INPUTS if profile_inputs is None else profile_inputs
    region_points = REGION_POINTS if region_points is None else region_points
    thresholds = GUT_THRESHOLDS if thresholds is None else thresholds
    cone_rows = SOS_CONE_ROWS if sos_cone_rows is None else tuple(sos_cone_rows)
    record = RESEARCH_RECORD if research_record is None else research_record
    tol = FLOAT_TOLERANCES
    checks: dict[str, bool] = {}
    q_tensor = group["beta_scalar_tensor"]["Q"]
    g_tensor = group["beta_gauge_tensor"]["G"]
    c2d = group["casimirs"]["C2D_coefficients"]
    tree = group["tree_mass_matrix"]["A"]
    cqk = chart["c_qk"]
    fierz = group["fierz_vectors"]["f"]
    witness_lambda = matching["witness"]["lambda"]
    exact_ok = (
        all(value is not None for value in q_tensor.values())
        and all(value is not None for value in g_tensor.values())
        and None not in c2d.values()
        and all(cqk.get(channel) is not None for channel in SELF_CHANNELS)
        and all(fierz.get(channel) is not None for channel in FIERZ_CHANNELS)
        and witness_lambda is not None
    )
    if not exact_ok:
        raise ArithmeticError("the exact sections did not produce the beta tensors, c_qk, f_c and the witness couplings")
    beta_key = _beta_key(q_tensor, g_tensor, c2d)
    a_float = np.array([[float(value) for value in row] for row in tree])
    witness = tuple(float(value) for value in witness_lambda)
    summaries = (record.get("profile_summaries") or {}).get("value") or {}
    per_profile: dict[str, dict[str, Any]] = {}
    for tag in PROFILE_TAGS:
        inputs = profile_inputs[tag]
        profile_key = _profile_key(inputs)
        grid, couplings = _gauge_profile(*profile_key)
        t_i, t_g = math.log(float(inputs["M_I"])), math.log(float(inputs["M_GUT"]))
        g_vr = [float(np.sqrt(4 * math.pi / float(value))) for value in inputs["y_MI"][:3]]
        g_gut = [float(np.interp(t_g, grid, couplings[:, index])) for index in range(3)]
        witness_run = _cached_run(profile_key, beta_key, witness, t_g, t_i)
        crossing = witness_run["crossing"]
        region = tuple(float(value) for value in region_points[tag])
        region_run = _cached_run(profile_key, beta_key, region, t_i, t_g)
        lam_gut = region_run["lambda_end"]
        per_profile[tag] = {
            "t_I": t_i,
            "t_GUT": t_g,
            "v_R_GeV": float(inputs["M_I"]),
            "M_GUT_GeV": float(inputs["M_GUT"]),
            "grid_points": int(grid.size),
            "g_vR_recomputed": g_vr,
            "g_MGUT_recomputed": g_gut,
            "alpha_inv_MGUT_recomputed": [4 * math.pi / (value * value) for value in g_gut],
            "M_GUT_over_M_X": float(inputs["M_GUT"]) / PROFILE_M_X[tag],
            "witness_lambda5_zero_crossing_GeV": crossing,
            "witness_events_GeV": dict(witness_run["events"]),
            "witness_reaches_v_R": bool(witness_run["completed"]),
            "region_point_lambda_vR": list(region),
            "region_point_lambda_GUT": None if lam_gut is None else [float(value) for value in lam_gut],
            "region_point_run_completed": bool(region_run["completed"]),
        }
    # D01 profiles.
    profile_ok = True
    for tag in PROFILE_TAGS:
        recorded = summaries.get(tag) if isinstance(summaries, Mapping) else None
        if not isinstance(recorded, Mapping):
            profile_ok = False
            continue
        for key, recomputed in (("g_vR", per_profile[tag]["g_vR_recomputed"]), ("g_MGUT", per_profile[tag]["g_MGUT_recomputed"])):
            expected = recorded.get(key)
            if not isinstance(expected, (list, tuple)) or len(expected) != 3:
                profile_ok = False
                continue
            profile_ok = profile_ok and all(_close(value, float(reference), rel=tol["profile_rel"]) for value, reference in zip(recomputed, expected))
    checks["gauge_profiles_reproduce_recorded_inputs"] = bool(profile_ok)
    # D02 crossing.
    checks["witness_lambda5_zero_crossing"] = all(
        _close(per_profile[tag]["witness_lambda5_zero_crossing_GeV"], EXPECTED_CROSSING_GEV[tag], rel=tol["crossing_rel"])
        and per_profile[tag]["v_R_GeV"] < per_profile[tag]["witness_lambda5_zero_crossing_GeV"] < per_profile[tag]["M_GUT_GeV"]
        for tag in PROFILE_TAGS
    )
    # D03 blow-up above v_R.
    checks["witness_flow_nonperturbative_before_v_R"] = all(
        per_profile[tag]["witness_events_GeV"]["4pi"] is not None
        and per_profile[tag]["witness_events_GeV"]["1e3"] is not None
        and per_profile[tag]["witness_events_GeV"]["4pi"] > per_profile[tag]["v_R_GeV"]
        and per_profile[tag]["witness_events_GeV"]["1e3"] > per_profile[tag]["v_R_GeV"]
        and _close(per_profile[tag]["witness_events_GeV"]["4pi"], EXPECTED_BLOWUP_GEV[tag]["4pi"], rel=tol["blowup_rel"])
        and _close(per_profile[tag]["witness_events_GeV"]["1e3"], EXPECTED_BLOWUP_GEV[tag]["1e3"], rel=tol["blowup_rel"])
        for tag in PROFILE_TAGS
    )
    # D04 / D05 region points at M_GUT.
    run_up_ok = True
    gaps = {}
    for tag in PROFILE_TAGS:
        lam_gut = per_profile[tag]["region_point_lambda_GUT"]
        if lam_gut is None or not per_profile[tag]["region_point_run_completed"]:
            run_up_ok = False
            gaps[tag] = None
            continue
        run_up_ok = run_up_ok and all(_close(value, expected, abs_tol=tol["lambda_gut_abs"]) for value, expected in zip(lam_gut, EXPECTED_LAMBDA_GUT[tag]))
        gaps[tag] = lam_gut[3] - lam_gut[4]
    checks["region_points_run_up"] = bool(run_up_ok)
    checks["region_points_violate_sos_gap_at_M_GUT"] = all(
        gaps[tag] is not None
        and _close(gaps[tag], EXPECTED_GAP_GUT[tag], abs_tol=tol["gap_abs"])
        and gap_excludes_sos_tree_image(per_profile[tag]["region_point_lambda_GUT"])
        for tag in PROFILE_TAGS
    )
    # D06 tree levels at v_R.
    levels_vr = {tag: [float(value) for value in a_float @ np.array(region_points[tag], dtype=float)] for tag in PROFILE_TAGS}
    checks["region_points_tree_positive_at_v_R"] = all(
        all(value > 0 for value in levels_vr[tag])
        and all(_close(value, expected, abs_tol=tol["tree_levels_abs"]) for value, expected in zip(levels_vr[tag], EXPECTED_TREE_LEVELS_VR[tag]))
        for tag in PROFILE_TAGS
    )
    # D07 tree-matching LP margins.
    tree_slack = {}
    for tag in PROFILE_TAGS:
        lam_gut = per_profile[tag]["region_point_lambda_GUT"]
        tree_slack[tag] = None if lam_gut is None else matching_lp(lam_gut, cqk, fierz, cone_rows)
    checks["tree_matching_min_slack_is_half_gap"] = all(
        tree_slack[tag] is not None
        and gaps[tag] is not None
        and _close(tree_slack[tag], EXPECTED_TREE_SLACK[tag], abs_tol=tol["tree_slack_abs"])
        and abs(tree_slack[tag] - (-gaps[tag]) / 2) <= tol["half_gap_abs"]
        for tag in PROFILE_TAGS
    )
    # D08 threshold-matching margins for both coupling pairings: RECORD-ONLY pins (no pass criterion on the margin;
    # the threshold path is declared not robust, see disclosures.threshold_fragility).
    threshold_slack_all: dict[str, dict[str, dict[str, float | None]]] = {}
    target_gap: dict[str, dict[str, dict[str, float | None]]] = {}
    for tag in PROFILE_TAGS:
        lam_gut = per_profile[tag]["region_point_lambda_GUT"]
        threshold_slack_all[tag] = {}
        target_gap[tag] = {}
        for pairing in THRESHOLD_PAIRINGS:
            threshold_slack_all[tag][pairing] = {}
            target_gap[tag][pairing] = {}
            for gx in GX_VALUES:
                key = f"{pairing}_{gx}"
                if lam_gut is None or key not in thresholds:
                    threshold_slack_all[tag][pairing][gx] = None
                    target_gap[tag][pairing][gx] = None
                    continue
                target = np.array(lam_gut) - np.array(thresholds[key], dtype=float)
                threshold_slack_all[tag][pairing][gx] = matching_lp(target, cqk, fierz, cone_rows)
                target_gap[tag][pairing][gx] = float(target[3] - target[4])
    threshold_slack = {tag: dict(threshold_slack_all[tag][THRESHOLD_PAIRING[tag]]) for tag in PROFILE_TAGS}
    checks["threshold_matching_min_slack_pinned"] = all(
        threshold_slack_all[tag][pairing][gx] is not None
        and _close(threshold_slack_all[tag][pairing][gx], EXPECTED_THRESHOLD_SLACK[tag][pairing][gx], abs_tol=tol["threshold_slack_abs"])
        for tag in PROFILE_TAGS
        for pairing in THRESHOLD_PAIRINGS
        for gx in GX_VALUES
    )
    threshold_gap_shift = {
        key: {"dlam4_minus_dlam5": float(value[3]) - float(value[4]), "in_units_of_witness_tree_gap_1_128": 128.0 * (float(value[3]) - float(value[4]))}
        for key, value in thresholds.items()
    }
    # D09 threshold scale at which the best rho = 1e3 point becomes SOS-reachable (disclosure).
    lam_primary = per_profile["rho1e3"]["region_point_lambda_GUT"]
    scale_research = scale_zero = min_slack_gx0 = None
    key_gx1 = f"{THRESHOLD_PAIRING['rho1e3']}_gX1.0"
    key_gx0 = f"{THRESHOLD_PAIRING['rho1e3']}_gX0.0"
    if lam_primary is not None and key_gx1 in thresholds and key_gx0 in thresholds:
        scale_research = matching_lp(lam_primary, cqk, fierz, cone_rows, direction=thresholds[key_gx1], mode="scale", slack_bound=RESEARCH_SLACK)
        scale_zero = matching_lp(lam_primary, cqk, fierz, cone_rows, direction=thresholds[key_gx1], mode="scale", slack_bound=0.0)
        min_slack_gx0 = matching_lp(lam_primary, cqk, fierz, cone_rows, direction=thresholds[key_gx0], mode="slack", scale_max=THRESHOLD_SCALE_MAX_GX0)
    checks["threshold_scale_to_reach_sos_family"] = bool(
        _close(scale_research, EXPECTED_THRESHOLD_SCALE["slack_le_research"], abs_tol=tol["threshold_scale_abs"])
        and _close(scale_zero, EXPECTED_THRESHOLD_SCALE["slack_zero"], abs_tol=tol["threshold_scale_abs"])
        and _close(min_slack_gx0, EXPECTED_THRESHOLD_SCALE["gX0_min_slack"], abs_tol=tol["threshold_slack_abs"])
    )
    # D10 BFB-only matching.
    bfb_slack = {tag: (None if per_profile[tag]["region_point_lambda_GUT"] is None else matching_lp(per_profile[tag]["region_point_lambda_GUT"], cqk, fierz, ())) for tag in PROFILE_TAGS}
    checks["bfb_only_matching_exact_at_region_points"] = all(bfb_slack[tag] is not None and bfb_slack[tag] <= tol["bfb_only_slack_abs"] for tag in PROFILE_TAGS)
    # D11 SOS-safe grid: no tree vacuum at v_R.
    map_key = (
        tuple(tuple(float(value) for value in cqk[channel]) for channel in SELF_CHANNELS),
        tuple(tuple(float(value) for value in fierz[channel]) for channel in EXCHANGE_CHANNELS),
    )
    tree_key = tuple(tuple(float(value) for value in row) for row in tree)
    sos_grid = {tag: dict(_cached_grid_scan(_profile_key(profile_inputs[tag]), beta_key, map_key, tree_key)) for tag in PROFILE_TAGS}
    checks["sos_safe_grid_has_no_perturbative_tree_vacuum_at_v_R"] = bool(
        all(sos_grid[tag]["tree_vacuum_at_v_R"] == 0 for tag in PROFILE_TAGS)
        and all(sos_grid[tag]["n_points"] == 2560 for tag in PROFILE_TAGS)
        and all(sos_grid[tag]["not_blown_up"] == EXPECTED_D11_NOT_BLOWN_UP[tag] for tag in PROFILE_TAGS)
        and all(sos_grid[tag]["max_lambda5_vR_not_blown_up"] is None or sos_grid[tag]["max_lambda5_vR_not_blown_up"] < 0 for tag in PROFILE_TAGS)
    )
    grid_meaning = (
        "no SOS grid point runs perturbatively to v_R with a tree vacuum: "
        + "; ".join(
            f"{tag}: {sos_grid[tag]['n_points'] - sos_grid[tag]['not_blown_up']} of {sos_grid[tag]['n_points']} exceed "
            f"|lambda| = {D11_GRID['blow_up_cap']:g} above v_R"
            + (
                f", the {sos_grid[tag]['not_blown_up']} others reach v_R with lambda5(v_R) <= "
                f"{sos_grid[tag]['max_lambda5_vR_not_blown_up']:.3g} (min {sos_grid[tag]['min_lambda5_vR_not_blown_up']:.4g})"
                if sos_grid[tag]["not_blown_up"]
                else ""
            )
            for tag in PROFILE_TAGS
        )
        + "; this is a statement about perturbative flows from SOS-safe tree matching, not a vacuum analysis at "
        "non-perturbative couplings"
    )
    # D12 witness betas (float) against the research value.
    beta_float = group["witness_betas"]["beta_float"]
    reference = (record.get("skeptic_witness_betas") or {}).get("value")
    checks["witness_betas_float_match_research"] = bool(
        beta_float is not None
        and isinstance(reference, (list, tuple))
        and len(reference) == 5
        and all(_close(value, float(expected), rel=tol["beta_rel"]) for value, expected in zip(beta_float, reference))
    )
    # D13 method accuracy against the joint (non-interpolated) reference.
    accuracy = _accuracy_estimate(profile_inputs, beta_key, witness, region_points, per_profile)
    checks["discretisation_accuracy_within_budget"] = bool(accuracy["within_budget"])
    return {
        "kind": "FLOAT",
        "tolerances": dict(FLOAT_TOLERANCES),
        "tolerance_semantics": TOLERANCE_SEMANTICS,
        "method": {
            "gauge_profiles": "two-loop PS gauge + y_PS, RK4 step 0.05 from ln M_I (step boundary at ln(rho M_I), spectators above), last step to ln M_GUT + 0.1; g by np.interp",
            "quartic_running": f"one-loop exact-rational betas (group_theory), RK4 with {RUN_STEPS} uniform steps between ln M_GUT and ln M_I",
            "crossing": f"first step with lambda5 from > 0 to <= 0, then {BISECTIONS} bisections, each a single RK4 sub-step from the bracket start",
            "lp": "scipy.optimize.linprog(method='highs'); variables w (4), beta (3), delta (5), s[, scale]",
            "threshold_matching": "D08 pins the min LP slack with the research witness threshold subtracted for both coupling pairings (alpha^-1 = 23.78 and 40) and both gX; record-only, no pass criterion on the margin (the threshold path is declared not robust)",
            "threshold_scale": "D09 minimises the threshold scale directly as an LP variable (the min slack is convex in the scale), which replaces a bisection and gives the smallest scale exactly up to the LP tolerance",
            "accuracy": "D13 compares the primary running with a joint gauge + quartic RK4 without interpolation (running.accuracy_estimate)",
            "inputs": "profile boundary values, region points and M_GUT thresholds are RESEARCH_RECORD_INPUT (see research_record)",
        },
        "inputs": {
            "profiles": {tag: dict(profile_inputs[tag]) for tag in PROFILE_TAGS},
            "region_points": {tag: list(region_points[tag]) for tag in PROFILE_TAGS},
            "gut_thresholds": {key: list(value) for key, value in thresholds.items()},
            "threshold_pairing": dict(THRESHOLD_PAIRING),
            "threshold_alpha_inv": dict(THRESHOLD_ALPHA_INV),
            "profile_M_X": dict(PROFILE_M_X),
            "sos_cone_rows": list(cone_rows),
        },
        "profiles": per_profile,
        "gap_lam4_minus_lam5_GUT": gaps,
        "tree_levels_at_v_R": levels_vr,
        "tree_matching_min_slack": tree_slack,
        "threshold_matching_min_slack": threshold_slack,
        "threshold_matching_min_slack_all_pairings": threshold_slack_all,
        "threshold_gap_shift": threshold_gap_shift,
        "target_gap_after_threshold": target_gap,
        "threshold_scale": {
            "primary_profile": "rho1e3",
            "threshold": key_gx1,
            "scale_for_slack_le_research_0.03": scale_research,
            "scale_for_exact_reach": scale_zero,
            "gX0_min_slack_over_scale_0_to_8": min_slack_gx0,
            "meaning": "DISCLOSURE: the one-loop-threshold version of the disjointness is marginal",
        },
        "bfb_only_min_slack": bfb_slack,
        "sos_safe_grid": {
            "grid": {key: (list(value) if isinstance(value, tuple) else value) for key, value in D11_GRID.items()},
            "per_profile": sos_grid,
            "meaning": grid_meaning,
        },
        "witness_betas_float": beta_float,
        "accuracy_estimate": accuracy,
        "checks": checks,
        "seconds_internal": time.time() - started,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (E) One-loop Coleman-Weinberg curvature masses (float, recomputed).
# ---------------------------------------------------------------------------------------------------------------------


def _realform(matrix: np.ndarray) -> np.ndarray:
    output = np.zeros((2 * matrix.shape[0], 2 * matrix.shape[1]))
    output[0::2, 0::2] = matrix.real
    output[0::2, 1::2] = -matrix.imag
    output[1::2, 0::2] = matrix.imag
    output[1::2, 1::2] = matrix.real
    return output


@lru_cache(maxsize=1)
def _float_cw_model() -> dict[str, Any]:
    """Float version of the integer model on orthonormal real coordinates (x = sqrt2 (Re, Im) of the b-hat coefficients):
    the quartic projectors are the exact Gram data of _sym2_core on the orthonormal Sym^2 basis."""
    model = _model()
    sym = _sym2_core()
    norms = np.array(model["norms"], dtype=float)
    bhat = model["basis"].T.astype(float) / np.sqrt(norms)  # 48 x 30
    norms2 = np.array(sym["norms2"], dtype=float)
    scale = 1.0 / np.sqrt(norms2)
    projectors = [gram.astype(float) / denominator * scale[:, None] * scale[None, :] for gram, denominator in zip(sym["grams"], sym["denominators"])]
    embedding = np.zeros((N_SYM * N_SYM, len(sym["pairs"])))
    for index, (a, b) in enumerate(sym["pairs"]):
        if a == b:
            embedding[a * N_SYM + a, index] = 1.0
        else:
            embedding[a * N_SYM + b, index] = embedding[b * N_SYM + a, index] = 1.0 / math.sqrt(2.0)
    w = np.zeros((N_SYM, N_REAL), dtype=complex)
    for index in range(N_SYM):
        w[index, 2 * index] = 1.0 / math.sqrt(2.0)
        w[index, 2 * index + 1] = 1.0j / math.sqrt(2.0)

    def to_x(real: np.ndarray, imag: np.ndarray) -> np.ndarray:
        coefficients = bhat.T @ (real.astype(float) + 1j * imag.astype(float))
        x = np.zeros(N_REAL)
        x[0::2] = math.sqrt(2.0) * coefficients.real
        x[1::2] = math.sqrt(2.0) * coefficients.imag
        return x

    d0 = _sym_vector(*STATE_DIRECTIONS["(1,1)_0 radial"])
    x0 = to_x(*d0)
    x0 = x0 / np.linalg.norm(w @ x0)  # |D0| = 1
    directions = {}
    for name in STATE_ORDER:
        x = to_x(*_sym_vector(*STATE_DIRECTIONS[name]))
        directions[name] = x / np.linalg.norm(x)
    kinv = np.array([[float(value) for value in row] for row in model["kappa4_inverse"]])
    lower = np.linalg.cholesky(kinv)  # kinv = L L^T: T'_alpha = sum_a L[a, alpha] T_a is orthonormal
    su4_restricted = [bhat.T @ (real + 1j * imag) @ bhat for real, imag in model["su4_on_v"]]
    orthonormal = [sum(lower[a, alpha] * su4_restricted[a] for a in range(15)) for alpha in range(15)]
    su2 = [bhat.T @ (1j * generator.astype(float)) @ bhat for generator in model["rl"]]
    return {
        "projectors": projectors,
        "embedding": embedding,
        "w": w,
        "x0": x0,
        "directions": directions,
        "real_su4": [_realform(1j * matrix) for matrix in orthonormal],
        "real_su2": [_realform(1j * matrix) for matrix in su2],
    }


def _float_hessians(x: np.ndarray) -> np.ndarray:
    cw = _float_cw_model()
    w = cw["w"]
    embedding = cw["embedding"]
    d = w @ x
    pair = np.kron(d, d)
    jacobian = np.kron(w, d[:, None]) + np.kron(d[:, None], w)
    pair_e = embedding.T @ pair
    jacobian_e = embedding.T @ jacobian
    output = []
    for projector in cw["projectors"]:
        projected_jacobian = projector @ jacobian_e
        y = (embedding @ (projector @ pair_e)).reshape(N_SYM, N_SYM)
        z = w.T @ y.conj() @ w
        hessian = 2.0 * np.real(jacobian_e.conj().T @ projected_jacobian) + 2.0 * np.real(z + z.T)
        output.append(0.5 * (hessian + hessian.T))
    return np.array(output)


def _vector_mass_matrix(x: np.ndarray, g4: float, gr: float) -> np.ndarray:
    cw = _float_cw_model()
    rows = [g4 * (matrix @ x) for matrix in cw["real_su4"]] + [gr * (matrix @ x) for matrix in cw["real_su2"]]
    k = np.array(rows)
    return k @ k.T


def _cw_potential(x: np.ndarray, lam: np.ndarray, mu2: float, g4: float, gr: float) -> float:
    scalar = np.einsum("k,kij->ij", lam, _float_hessians(x)) - mu2 * np.eye(N_REAL)
    scalar_masses = np.linalg.eigvalsh(0.5 * (scalar + scalar.T))
    vector_masses = np.clip(np.linalg.eigvalsh(_vector_mass_matrix(x, g4, gr)), 0, None)

    def f(m2: np.ndarray, c: float) -> np.ndarray:
        m2 = np.where(np.abs(m2) < 1.0e-300, 1.0e-300, m2)
        return m2**2 * (np.log(np.abs(m2)) - c)

    return float((np.sum(f(scalar_masses, 1.5)) + 3 * np.sum(f(vector_masses, 5.0 / 6.0))) / (64 * math.pi**2))


@lru_cache(maxsize=16)
def cw_masses(lam: tuple[float, ...], g4: float, gr: float, h: float = CW_STEP) -> dict[str, dict[str, float]]:
    """Landau-gauge, p = 0, vev-fixed CW curvature masses (Q^2 = 1 = |D0|^2): m^2 = e.H_tree.e + d^2V1/de^2 -
    (dV1/dphi_radial)/|phi| (central differences, step h)."""
    cw = _float_cw_model()
    lam_array = np.array(lam, dtype=float)
    mu2 = 2.0 * lam_array[4]
    x0 = cw["x0"]
    phi = float(np.linalg.norm(x0))
    tree = np.einsum("k,kij->ij", lam_array, _float_hessians(x0)) - mu2 * np.eye(N_REAL)
    v00 = _cw_potential(x0, lam_array, mu2, g4, gr)
    radial = cw["directions"]["(1,1)_0 radial"]
    v_plus = {}
    v_minus = {}
    for name, direction in cw["directions"].items():
        v_plus[name] = _cw_potential(x0 + h * direction, lam_array, mu2, g4, gr)
        v_minus[name] = _cw_potential(x0 - h * direction, lam_array, mu2, g4, gr)
    radial_name = "(1,1)_0 radial"
    tadpole = (v_plus[radial_name] - v_minus[radial_name]) / (2 * h) / phi
    if not np.allclose(radial, x0 / phi):
        raise ArithmeticError("radial direction is not the vev direction")
    output = {}
    for name, direction in cw["directions"].items():
        second = (v_plus[name] - 2 * v00 + v_minus[name]) / h**2
        tree_mass = float(direction @ tree @ direction)
        output[name] = {"tree": tree_mass, "cw": tree_mass + second - tadpole}
    return output


# One-loop FJ R_xi scalar pole masses: a numpy port of the research polemass.py / eft_pole.py (study D-D; MS-bar,
# ordinary R_xi, Fleischer-Jegerlehner tadpoles; Martin loop functions A, B, K; m_pole^2 = m^2 + Re Pi(m^2)).
K16 = 1.0 / (16.0 * math.pi**2)


def _loop_a(x: Any, q2: float = 1.0) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    ax = np.abs(x)
    with np.errstate(divide="ignore", invalid="ignore"):
        value = x * (np.log(np.where(ax > 0, ax, 1.0) / q2) - 1.0)
    return np.where(ax > 0, value, 0.0)


def _loop_i(r: Any) -> np.ndarray:
    """Re[(1 - r) Log(1 - r) + r Log(-r)] - 1 for complex r (limits at r -> 0, 1 taken)."""
    r = np.asarray(r, dtype=complex)
    one = 1.0 - r
    with np.errstate(divide="ignore", invalid="ignore"):
        first = np.where(np.abs(one) > 1e-300, one * np.log(np.where(np.abs(one) > 1e-300, one, 1.0)), 0.0)
        second = np.where(np.abs(r) > 1e-300, r * np.log(np.where(np.abs(r) > 1e-300, -r, 1.0)), 0.0)
    return np.real(first + second) - 1.0


def _loop_b(x: Any, y: Any, s: Any, q2: float = 1.0) -> np.ndarray:
    """Re B0(s; x, y), finite MS-bar part (x, y >= 0 squared masses; |x|, |y| used for tiny negative inputs)."""
    x, y, s = np.broadcast_arrays(np.abs(np.asarray(x, dtype=float)), np.abs(np.asarray(y, dtype=float)), np.asarray(s, dtype=float))
    scale = np.maximum(np.maximum(x, y), np.abs(s))
    scale = np.where(scale > 0, scale, 1.0)
    small_s = np.abs(s) <= 1e-12 * scale
    out = np.empty(x.shape)
    if np.any(small_s):
        xx, yy = x[small_s], y[small_s]
        difference = xx - yy
        near = np.abs(difference) <= 1e-9 * np.maximum(np.maximum(xx, yy), 1e-300)
        with np.errstate(divide="ignore", invalid="ignore"):
            lx = np.where(xx > 0, np.log(np.where(xx > 0, xx, 1.0) / q2), 0.0)
            ly = np.where(yy > 0, np.log(np.where(yy > 0, yy, 1.0) / q2), 0.0)
            general = -((xx * lx - yy * ly) / np.where(near, 1.0, difference) - 1.0)
        middle = 0.5 * (xx + yy)
        with np.errstate(divide="ignore"):
            degenerate = -np.log(np.where(middle > 0, middle, 1e-300) / q2)
        out[small_s] = np.where(near, degenerate, general)
    rest = ~small_s
    if np.any(rest):
        xx, yy, ss = x[rest], y[rest], s[rest]
        b = (xx - yy - ss).astype(complex)
        c = yy.astype(complex)
        a = ss.astype(complex)
        discriminant = np.sqrt(b * b - 4 * a * c)
        sign = np.where(np.real(np.conj(b) * discriminant) >= 0, 1.0, -1.0)
        q = -0.5 * (b + sign * discriminant)
        with np.errstate(divide="ignore", invalid="ignore"):
            r1 = q / a
            r2 = np.where(np.abs(q) > 0, c / np.where(np.abs(q) > 0, q, 1.0), -b / a)
        out[rest] = -np.log(np.abs(ss) / q2) - _loop_i(r1) - _loop_i(r2)
    return out


def _loop_k(x: Any, y: Any, s: Any, q2: float = 1.0) -> np.ndarray:
    return 0.25 * (-(x + 3 * y - s) * _loop_a(y, q2) - (3 * x + y - s) * _loop_a(x, q2) + (x + y - s) ** 2 * _loop_b(x, y, s, q2))


def _loop_sv(s: float, m: np.ndarray, mv: np.ndarray, xi: float, q2: float = 1.0) -> np.ndarray:
    base = (2 * s + 2 * m - mv) * _loop_b(mv, m, s, q2) - 2 * _loop_a(mv, q2) + _loop_a(m, q2)
    if xi == 1.0:
        return base
    correction = (
        (s - m) ** 2 * (_loop_b(mv, m, s, q2) - _loop_b(xi * mv, m, s, q2)) - (mv - s + m) * _loop_a(mv, q2) + (xi * mv - s + m) * _loop_a(xi * mv, q2)
    ) / mv
    return base - correction


def _loop_vv(s: float, a: np.ndarray, b: np.ndarray, xi: float, q2: float = 1.0) -> np.ndarray:
    base = 4 * _loop_b(a, b, s, q2) - 2.0
    if xi == 1.0:
        return base
    mixed = -(_loop_b(a, b, s, q2) - xi * _loop_b(a, xi * b, s, q2)) - (_loop_b(a, b, s, q2) - xi * _loop_b(xi * a, b, s, q2))
    k_terms = (_loop_k(a, b, s, q2) - _loop_k(xi * a, b, s, q2) - _loop_k(a, xi * b, s, q2) + _loop_k(xi * a, xi * b, s, q2)) / (a * b)
    return base + mixed + k_terms


@lru_cache(maxsize=16)
def fj_pole_masses(lam: tuple[float, ...], g4: float, gr: float, q2: float = 1.0) -> dict[float, dict[str, Any]]:
    """One-loop FJ R_xi pole masses m^2/v^2 of the seven light states (|D0| = v = 1, Q^2 = q2 v^2) for xi in POLE_XIS.

    Self-energy (units 1/16 pi^2): scalar seagull and bubble, vector seagull, SV and VV bubbles, ghosts and the FJ
    tadpole along the radial direction, at p^2 = the tree mass; massless (unbroken) vectors get M^2 = reg x scale.  The
    per-coupling Hessians and their derivatives along each state direction are exact central differences (the quartic
    Hessian is quadratic in the field).  Also returns the FJ vev shift dv = -T_radial/(m_radial^2 |x0|) per xi."""
    cw = _float_cw_model()
    lam_array = np.array(lam, dtype=float)
    x0 = cw["x0"]
    directions = cw["directions"]
    radial = "(1,1)_0 radial"
    hessians_0 = _float_hessians(x0)
    h0_quartic = np.einsum("k,kij->ij", lam_array, hessians_0)
    h0 = h0_quartic - 2.0 * lam_array[4] * np.eye(N_REAL)
    h0 = 0.5 * (h0 + h0.T)
    d_h: dict[str, np.ndarray] = {}
    dd_h: dict[str, np.ndarray] = {}
    for name in STATE_ORDER:
        e = directions[name]
        plus = np.einsum("k,kij->ij", lam_array, _float_hessians(x0 + POLE_FD_STEP * e))
        minus = np.einsum("k,kij->ij", lam_array, _float_hessians(x0 - POLE_FD_STEP * e))
        d_h[name] = (plus - minus) / (2 * POLE_FD_STEP)
        dd_h[name] = (plus - 2 * h0_quartic + minus) / POLE_FD_STEP**2
    thetas = np.array([g4 * matrix for matrix in cw["real_su4"]] + [gr * matrix for matrix in cw["real_su2"]])
    k_matrix = np.einsum("aij,j->ia", thetas, x0)
    vector_mass = k_matrix.T @ k_matrix
    vector_eigen, rotation = np.linalg.eigh(0.5 * (vector_mass + vector_mass.T))
    scale = max(float(np.max(np.abs(vector_eigen))), float(np.max(np.abs(np.linalg.eigvalsh(h0)))), 1e-300)
    massless = vector_eigen < 1e-10 * scale
    mv = np.where(massless, POLE_IR_REGULATOR * scale, vector_eigen)
    rotated = np.einsum("ba,bij->aij", rotation, thetas)
    goldstone_rows = np.einsum("aij,j->ai", rotated, x0)
    gg = goldstone_rows.T @ goldstone_rows
    x0_norm = float(np.linalg.norm(x0))
    e_radial = directions[radial]
    m_radial2 = float(e_radial @ h0 @ e_radial)
    output: dict[float, dict[str, Any]] = {}
    for xi in POLE_XIS:
        scalar = 0.5 * (h0 + xi * gg + (h0 + xi * gg).T)
        w, u = np.linalg.eigh(scalar)
        xi_vector = xi * _loop_a(xi * mv, q2) if xi > 0 else 0.0
        # FJ tadpole along the radial direction.
        lam_rkk = np.einsum("ik,ij,jk->k", u, d_h[radial], u)
        tadpole = 0.5 * float(lam_rkk @ _loop_a(w, q2))
        projection = np.einsum("aij,aj->ai", rotated, goldstone_rows) @ e_radial
        tadpole += float(np.sum(-projection * (3 * _loop_a(mv, q2) + 2 * mv + xi_vector)))
        if xi > 0:
            tadpole += float(np.sum(xi * projection * _loop_a(xi * mv, q2)))
        poles = []
        trees = []
        for name in STATE_ORDER:
            e = directions[name]
            s = float(e @ h0 @ e)
            pieces = 0.5 * float(np.einsum("ik,ij,jk->k", u, dd_h[name], u) @ _loop_a(w, q2))
            lam_ekl = u.T @ d_h[name] @ u
            pieces -= 0.5 * float(np.sum(lam_ekl**2 * _loop_b(w[:, None], w[None, :], s, q2)))
            theta_e = np.einsum("aij,j->ai", rotated, e)
            pieces += 0.5 * float(np.sum(2 * np.sum(theta_e**2, axis=1) * (3 * _loop_a(mv, q2) + 2 * mv + xi_vector)))
            c_ak = -(theta_e @ u)
            pieces += float(np.sum(c_ak**2 * _loop_sv(s, w[None, :], mv[:, None], xi, q2)))
            g_theta_e = goldstone_rows @ theta_e.T
            vv_coupling = g_theta_e + g_theta_e.T
            pieces -= 0.5 * float(np.sum(vv_coupling**2 * _loop_vv(s, mv[:, None], mv[None, :], xi, q2)))
            if xi > 0:
                pieces += xi * xi * float(np.sum(g_theta_e * g_theta_e.T * _loop_b(xi * mv[:, None], xi * mv[None, :], s, q2)))
            pieces -= float(e @ d_h[radial] @ e) * tadpole / m_radial2
            poles.append(s + K16 * pieces)
            trees.append(s)
        output[xi] = {"pole": poles, "tree": trees, "dv": -K16 * tadpole / m_radial2 / x0_norm}
    return output


def one_loop_section(running: Mapping[str, Any], *, research_record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = RESEARCH_RECORD if research_record is None else research_record
    reference = (record.get("skeptic_cw_masses") or {}).get("value") or {}
    pole_reference = (record.get("best_controlled_pole_reference") or {}).get("value") or {}
    dv_reference = (record.get("fj_vs_vf_vev_shift") or {}).get("value") or {}
    tol = FLOAT_TOLERANCES
    masses = {}
    poles: dict[str, dict[str, Any]] = {}
    for tag in PROFILE_TAGS:
        lam = tuple(float(value) for value in running["inputs"]["region_points"][tag])
        g_vr = running["profiles"][tag]["g_vR_recomputed"]
        result = cw_masses(lam, float(g_vr[0]), float(g_vr[2]))
        masses[tag] = {"tree": [result[name]["tree"] for name in STATE_ORDER], "cw": [result[name]["cw"] for name in STATE_ORDER], "g4_gR": [g_vr[0], g_vr[2]]}
        fj = fj_pole_masses(lam, float(g_vr[0]), float(g_vr[2]))
        by_xi = np.array([fj[xi]["pole"] for xi in POLE_XIS])
        tree = list(fj[1.0]["tree"])
        dv_feyn, dv_landau = fj[1.0]["dv"], fj[0.0]["dv"]
        poles[tag] = {
            "pole_by_xi": {str(xi): list(fj[xi]["pole"]) for xi in POLE_XIS},
            "tree": tree,
            "xi_spread": float(np.max(by_xi.max(axis=0) - by_xi.min(axis=0))),
            "min_pole": float(np.min(by_xi)),
            "dv_feyn": dv_feyn,
            "dv_landau": dv_landau,
            "VF_L": [pole - 2.0 * level * dv_landau for pole, level in zip(fj[1.0]["pole"], tree)],
        }
    all_values = [value for tag in PROFILE_TAGS for value in masses[tag]["cw"]]
    all_poles = [value for tag in PROFILE_TAGS for values in poles[tag]["pole_by_xi"].values() for value in values]

    def pole_reference_ok() -> bool:
        try:
            return all(
                all(
                    len(pole_reference[tag]["pole_by_xi"][str(xi)]) == 7
                    and all(abs(a - float(b)) <= tol["pole_research_abs"] for a, b in zip(poles[tag]["pole_by_xi"][str(xi)], pole_reference[tag]["pole_by_xi"][str(xi)]))
                    for xi in POLE_XIS
                )
                and len(pole_reference[tag]["tree"]) == 7
                and all(abs(a - float(b)) <= tol["pole_research_abs"] for a, b in zip(poles[tag]["tree"], pole_reference[tag]["tree"]))
                for tag in PROFILE_TAGS
            )
        except (KeyError, TypeError, ValueError):
            return False

    def vev_fixed_ok() -> bool:
        try:
            return all(
                all(value > 0 for value in poles[tag]["VF_L"])
                and abs(poles[tag]["dv_feyn"]) <= POLE_DV_MAX
                and abs(poles[tag]["dv_landau"]) <= POLE_DV_MAX
                and len(pole_reference[tag]["VF_L"]) == 7
                and all(abs(a - float(b)) <= tol["pole_research_abs"] for a, b in zip(poles[tag]["VF_L"], pole_reference[tag]["VF_L"]))
                and abs(poles[tag]["dv_feyn"] - float(dv_reference[tag]["dv_feyn"])) <= tol["pole_research_abs"]
                and abs(poles[tag]["dv_landau"] - float(dv_reference[tag]["dv_landau"])) <= tol["pole_research_abs"]
                for tag in PROFILE_TAGS
            )
        except (KeyError, TypeError, ValueError):
            return False

    checks = {
        "cw_masses_positive_at_region_points": bool(len(all_values) == 21 and all(value > 0 for value in all_values)),
        "cw_masses_match_independent_record": bool(
            isinstance(reference, Mapping)
            and all(
                isinstance(reference.get(tag), (list, tuple))
                and len(reference[tag]) == 7
                and all(_close(value, float(expected), abs_tol=FLOAT_TOLERANCES["cw_mass_abs"]) for value, expected in zip(masses[tag]["cw"], reference[tag]))
                for tag in PROFILE_TAGS
            )
        ),
        "fj_pole_masses_positive_all_xi": bool(len(all_poles) == 7 * len(POLE_XIS) * len(PROFILE_TAGS) and all(value > 0 for value in all_poles)),
        "fj_pole_masses_xi_independent": all(poles[tag]["xi_spread"] <= tol["pole_xi_spread_abs"] for tag in PROFILE_TAGS),
        "fj_pole_masses_match_research_record": bool(pole_reference_ok()),
        "vev_fixed_landau_masses_positive_and_dv_controlled": bool(vev_fixed_ok()),
    }
    deviation = None
    if checks["cw_masses_match_independent_record"]:
        deviation = max(abs(value - float(expected)) for tag in PROFILE_TAGS for value, expected in zip(masses[tag]["cw"], reference[tag]))
    pole_deviation = None
    if checks["fj_pole_masses_match_research_record"]:
        pole_deviation = max(
            abs(a - float(b))
            for tag in PROFILE_TAGS
            for xi in POLE_XIS
            for a, b in zip(poles[tag]["pole_by_xi"][str(xi)], pole_reference[tag]["pole_by_xi"][str(xi)])
        )
    return {
        "kind": "FLOAT",
        "tolerances": {
            "cw_mass_abs": tol["cw_mass_abs"],
            "pole_xi_spread_abs": tol["pole_xi_spread_abs"],
            "pole_research_abs": tol["pole_research_abs"],
            "dv_max": POLE_DV_MAX,
        },
        "label": (
            "one-loop FJ R_xi pole masses at the three best region points (recomputed, xi in {0, 0.5, 1, 3, 10}), the "
            "vev-fixed Landau masses VF_L and Landau-gauge p = 0 CW curvature masses; the renormalisation-scale "
            "variation of the pole masses stays RESEARCH_RECORD"
        ),
        "method": "Landau gauge, p = 0, vev-fixed Coleman-Weinberg (MS-bar, Q^2 = |D0|^2 = 1), V1 = [sum_s f(m_s^2, 3/2) + 3 sum_v f(m_v^2, 5/6)]/(64 pi^2), f = m^4 (ln|m^2| - c), m^2 = e.H.e + d^2V1/de^2 - (dV1/dphi_r)/|phi|, h = 2e-3",
        "pole_method": (
            "port of the research polemass.py / eft_pole.py: MS-bar at Q^2 = v_R^2 (|D0| = 1), ordinary R_xi, "
            "Fleischer-Jegerlehner tadpoles (tree vev of the MS-bar potential), m_pole^2 = m^2 + Re Pi(p^2 = m^2) with "
            "scalar seagull and bubble, vector seagull, SV and VV bubbles, ghosts and the FJ tadpole (Martin A, B, K); "
            f"massless vectors get M^2 = {POLE_IR_REGULATOR:g} x scale; per-coupling Hessian derivatives by exact "
            f"central differences (h = {POLE_FD_STEP:g}); VF_L = FJ(xi = 1) - 2 tree dv_Landau, dv = -T_radial/(m_radial^2 |x0|)"
        ),
        "states": list(STATE_ORDER),
        "masses_over_v_R_squared": masses,
        "minimum": min(all_values) if all_values else None,
        "max_abs_deviation_from_independent_record": deviation,
        "fj_pole_masses_over_v_R_squared": poles,
        "fj_pole_minimum": min(all_poles) if all_poles else None,
        "fj_pole_max_abs_deviation_from_research_record": pole_deviation,
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (F) Research record integrity and consistency; (G) scope.
# ---------------------------------------------------------------------------------------------------------------------

_RATIONAL_RE = re.compile(r"^-?\d+(/\d+)?$")


def _numeric_leaves(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        return bool(_RATIONAL_RE.match(value))
    if isinstance(value, Mapping):
        return bool(value) and all(_numeric_leaves(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_numeric_leaves(item) for item in value)
    return False


def research_record_section(running: Mapping[str, Any], *, research_record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = RESEARCH_RECORD if research_record is None else research_record
    schema = ("label", "value", "meaning", "source_script", "source_json", "key", "source_json_sha256", "reproducible_from_repository")
    entries_ok = isinstance(record, Mapping) and bool(record)
    problems = []
    if entries_ok:
        for name, entry in record.items():
            if not isinstance(entry, Mapping) or set(entry) != set(schema):
                problems.append(f"{name}: schema")
                continue
            if entry["label"] not in RESEARCH_LABELS:
                problems.append(f"{name}: label")
            sha = entry["source_json_sha256"]
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
                problems.append(f"{name}: sha256")
            if entry["reproducible_from_repository"] is not False:
                problems.append(f"{name}: reproducible_from_repository")
            if not all(isinstance(entry[key], str) and entry[key] for key in ("meaning", "source_script", "source_json", "key")):
                problems.append(f"{name}: provenance text")
            if name in UNVERIFIED_RECORD_KEYS:
                if not (isinstance(entry["value"], bool) and entry["label"] == _REC and "not verified" in entry["meaning"]):
                    problems.append(f"{name}: unverified entry")
            elif not _numeric_leaves(entry["value"]):
                problems.append(f"{name}: value")
    checks = {"entries_labelled_with_provenance": bool(entries_ok and not problems)}

    def value_of(name: str) -> Any:
        entry = record.get(name) if isinstance(record, Mapping) else None
        return entry.get("value") if isinstance(entry, Mapping) else None

    consistency: dict[str, Any] = {}
    ok = True
    try:
        profiles = running["profiles"]
        best = value_of("best_core_lam_GUT_rho1e3")
        recomputed = profiles["rho1e3"]["region_point_lambda_GUT"]
        consistency["d22_best_core_lam_GUT_max_abs_deviation"] = max(abs(float(a) - float(b)) for a, b in zip(best, recomputed))
        ok = ok and len(best) == 5 and consistency["d22_best_core_lam_GUT_max_abs_deviation"] <= FLOAT_TOLERANCES["research_lambda_gut_abs"]
        skeptic = value_of("skeptic_running")
        deviation = max(abs(float(a) - float(b)) for tag in PROFILE_TAGS for a, b in zip(skeptic[tag]["lam_MGUT"], profiles[tag]["region_point_lambda_GUT"]))
        consistency["skeptic_lam_GUT_max_abs_deviation"] = deviation
        ok = ok and deviation <= FLOAT_TOLERANCES["research_lambda_gut_abs"]
        crossing_skeptic = max(
            abs(float(skeptic[tag]["witness_lam5_zero_crossing_GeV"]) / profiles[tag]["witness_lambda5_zero_crossing_GeV"] - 1.0) for tag in PROFILE_TAGS
        )
        consistency["skeptic_crossing_max_rel_deviation"] = crossing_skeptic
        ok = ok and crossing_skeptic <= FLOAT_TOLERANCES["crossing_rel"]
        gap_max = {tag: float(value_of(f"region_gap_quantiles_{tag}")[-1]) for tag in PROFILE_TAGS}
        consistency["recorded_region_gap_max"] = gap_max
        ok = ok and all(value < 0 for value in gap_max.values())
        matching_record = value_of("matching_tree_LP")
        ok = ok and all(int(matching_record[tag]["SOS_safe_feasible"]) == 0 for tag in PROFILE_TAGS)
        threshold_record = value_of("threshold_LP")
        ok = ok and all(int(threshold_record[gx]["feasible"]) == 0 for gx in GX_VALUES)
        grid_crossing = value_of("witness_crossing_grid_limited")
        crossing_deviation = {tag: float(grid_crossing[tag]) / profiles[tag]["witness_lambda5_zero_crossing_GeV"] - 1.0 for tag in PROFILE_TAGS}
        consistency["grid_limited_crossing_rel_deviation"] = crossing_deviation
        ok = ok and all(abs(value) <= FLOAT_TOLERANCES["research_crossing_rel"] for value in crossing_deviation.values())
        summaries = value_of("profile_summaries")
        profile_deviation = max(
            abs(float(reference) / value - 1.0)
            for tag in PROFILE_TAGS
            for key, recomputed_key in (("g_vR", "g_vR_recomputed"), ("g_MGUT", "g_MGUT_recomputed"))
            for reference, value in zip(summaries[tag][key], profiles[tag][recomputed_key])
        )
        consistency["profile_summaries_max_rel_deviation"] = profile_deviation
        ok = ok and profile_deviation <= FLOAT_TOLERANCES["profile_rel"]
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        ok = False
    checks["consistent_with_recomputation"] = bool(ok)
    unverified = {name: value_of(name) for name in UNVERIFIED_RECORD_KEYS}
    checks["unverified_items_not_claimed"] = all(value is False for value in unverified.values())
    return {
        "kind": "RESEARCH_RECORD",
        "provenance_note": RESEARCH_PROVENANCE_NOTE,
        "entries": record,
        "unverified_items": unverified,
        "consistency": consistency,
        "problems": problems,
        "checks": checks,
    }


SCOPE = {
    "proved_exactly": [
        "group_theory (A): integer model of Delta_R = (10bar,1,3); Sym^2 irreps; SM-singlet vacuum; SM labels; tree mass matrix; Fierz vectors; 210 channels; one-loop beta tensors as exact rationals (SM Higgs identity on the same code path)",
        "chart_binding (B): c_qk of the 126bar self-quartics restricted to Delta_R in the repository chart; witness portal squares vanish on Delta_R",
        "matching (C): tree map at mu = M_GUT, gap identity lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3) >= 0 on W_SOS (Farkas certificate), witness levels = the committed G6 tree levels",
    ],
    "float_recomputed": [
        "running (D): PS gauge profiles, witness lambda5 zero crossings and runaway above v_R, the three best region points run to M_GUT, tree LP margins, threshold LP margins for both coupling pairings (record-only), BFB-only reach, a 2560-point SOS-safe grid, and the method accuracy against a joint gauge + quartic RK4 without interpolation",
        "one_loop_masses (E): FJ R_xi one-loop pole masses at the three best region points for xi in {0, 0.5, 1, 3, 10} (xi independence), the vev-fixed Landau masses VF_L with the FJ vev shifts, and Landau-gauge p = 0 vev-fixed CW curvature masses",
    ],
    "research_recorded": [
        "the one-loop region itself: 1.5M sampled lambda(v_R) points per profile in a finite IR box with a tree prefilter (d13), and its box-extension check (d23)",
        "region volume and tuning (fraction of V_pos, UV volume, Barbieri-Giudice quantiles), path-unitarity quantiles",
        "the 400-point tree matching LP per profile and the 300-point threshold LP (d13/d20, d21)",
        "the renormalisation-scale variation of the pole masses",
        "the one-loop M_GUT thresholds (computed at the witness only, at alpha^-1 = 23.78 and 40)",
    ],
    "not_proved_or_out_of_scope": [
        "anti-SOS G3 witnesses (outside degree-2 SOS certification): not excluded",
        "the one-loop region as a whole: it is a sampled, box-bounded set (1.5M points per profile); its gap < 0 at M_GUT is a sampling statement, not a proof over all couplings",
        "robustness beyond tree matching: with the recorded witness M_GUT threshold the lambda4 >= lambda5 obstruction is removed and the separation is marginal (0.042 at rho = 1e3, closing at 1.2 to 1.73 times that threshold; smaller at rho = 1e4 and without spectators with the alpha^-1 = 23.78 threshold); only the tree-matching statement is robust",
        "two-loop quartic beta functions",
        "the M_GUT one-loop threshold as a function of the weights w (assumed weight independent, not verified) and of the coupling at which it is taken",
        "the renormalisation-scale variation of the pole masses (research-recorded, not recomputed)",
        "region volume and tuning statistics (research-recorded, prior dependent)",
        "electroweak symmetry breaking",
        "heavy-Sigma exchange O(r0^2) corrections (r0 ~ 1e-8)",
        "the h/S portals and the Majorana Yukawa f (research: they only shrink the region)",
        "y_s / spectator Yukawas (Delta-only EFT)",
        "the rho = 1e3 profile premise of study D (A2's strict window prefers rho >= 10^3.8, where the region is larger)",
    ],
    "status_statement": "G6 stays OPEN; this module is evidence only and never changes a gate status",
}


def scope_section(flags: Mapping[str, Any], g6_status: str, tree_scope: str) -> dict[str, Any]:
    return {
        "checks": {
            "g6_open_and_evidence_only": bool(
                g6_status == "OPEN"
                and flags.get("G6_closed") is False
                and all(flags.get(name) is False for name in NEVER_TRUE_FLAGS)
                and tree_scope == TREE_CERTIFICATE_SCOPE
            )
        }
    }


# ---------------------------------------------------------------------------------------------------------------------
# Report assembly.
# ---------------------------------------------------------------------------------------------------------------------

SECTION_PREFIXES = (
    ("group_theory", "group_theory"),
    ("chart", "chart_binding"),
    ("matching", "matching"),
    ("running", "running"),
    ("one_loop", "one_loop_masses"),
    ("research_record", "research_record"),
)


def _collect_checks(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    output = {}
    for prefix, key in SECTION_PREFIXES:
        for name, value in sections[key]["checks"].items():
            output[f"{prefix}.{name}"] = bool(value)
    return output


def _disclosures(running: Mapping[str, Any], one_loop: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    def value_of(name: str) -> Any:
        entry = record.get(name) if isinstance(record, Mapping) else None
        return entry.get("value") if isinstance(entry, Mapping) else None

    scale = running["threshold_scale"]
    primary_key = f"{THRESHOLD_PAIRING['rho1e3']}_gX1.0"
    shift = (running["threshold_gap_shift"].get(primary_key) or {}).get("dlam4_minus_dlam5")
    all_slack = running["threshold_matching_min_slack_all_pairings"]
    target = running["target_gap_after_threshold"]
    profiles = running["profiles"]

    def fmt(value: Any, spec: str) -> str:
        return "n/a" if value is None else format(value, spec)

    alpha_ranges = {
        tag: (min(profiles[tag]["alpha_inv_MGUT_recomputed"]), max(profiles[tag]["alpha_inv_MGUT_recomputed"])) for tag in PROFILE_TAGS
    }
    ratios = [profiles[tag]["M_GUT_over_M_X"] for tag in PROFILE_TAGS]
    fragility_meaning = (
        f"the only computed one-loop M_GUT threshold (at the witness; alpha^-1 = 23.78, gX = g) shifts lambda4 - lambda5 by "
        f"{fmt(shift, '.3f')}, {fmt(None if shift is None else abs(shift) * 128.0, '.0f')} times the witness tree gap 1/128 "
        f"and larger than the rho = 1e3 region gap {fmt(running['gap_lam4_minus_lam5_GUT']['rho1e3'], '.3f')}: it removes the "
        f"lambda4 >= lambda5 obstruction (the rho = 1e3 target gap becomes {fmt(target['rho1e3']['alphainv23.78']['gX1.0'], '+.3f')}) "
        f"and leaves a sup-norm LP margin of {fmt(all_slack['rho1e3']['alphainv23.78']['gX1.0'], '.3f')} in other components, "
        f"which closes at {fmt(scale['scale_for_slack_le_research_0.03'], '.2f')} (slack <= 0.03) to "
        f"{fmt(scale['scale_for_exact_reach'], '.2f')} (exact reach) times that threshold. The thresholds were computed at "
        f"alpha^-1 = 23.78 and 40, while 4 pi/g^2 at the matching scale M_GUT ({min(ratios):.1f} to {max(ratios):.1f} times M_X) is "
        + ", ".join(f"{alpha_ranges[tag][0]:.1f}-{alpha_ranges[tag][1]:.1f} ({tag})" for tag in PROFILE_TAGS)
        + f"; with the alpha^-1 = 23.78 threshold the rho = 1e4 margin is {fmt(all_slack['rho1e4']['alphainv23.78']['gX1.0'], '.4f')} "
        f"and the no-spectator margin {fmt(all_slack['no_spec']['alphainv23.78']['gX1.0'], '.4f')} (gX = g), below the research "
        "slack 0.03, and at rho = 1e3 the threshold was taken at a weaker coupling than at M_GUT: only the tree-level version "
        "of the disjointness is robust"
    )
    recomputed_poles = one_loop.get("fj_pole_masses_over_v_R_squared") or {}
    xi_spreads = {
        "research_record": value_of("pole_mass_xi_spread"),
        "recomputed": {tag: (recomputed_poles.get(tag) or {}).get("xi_spread") for tag in PROFILE_TAGS},
    }
    return {
        "threshold_fragility": {
            "tree_level_min_slack": running["tree_matching_min_slack"],
            "with_recorded_threshold_min_slack": running["threshold_matching_min_slack"],
            "with_threshold_min_slack_all_pairings": all_slack,
            "threshold_pairing_used": dict(THRESHOLD_PAIRING),
            "threshold_alpha_inv": dict(THRESHOLD_ALPHA_INV),
            "alpha_inv_at_M_GUT": {tag: profiles[tag]["alpha_inv_MGUT_recomputed"] for tag in PROFILE_TAGS},
            "M_GUT_over_M_X": {tag: profiles[tag]["M_GUT_over_M_X"] for tag in PROFILE_TAGS},
            "threshold_gap_shift": running["threshold_gap_shift"],
            "target_gap_after_threshold": target,
            "rho1e3_scale_for_slack_le_0.03": scale["scale_for_slack_le_research_0.03"],
            "rho1e3_scale_for_exact_reach": scale["scale_for_exact_reach"],
            "meaning": fragility_meaning,
        },
        "region_sampling": {
            "scan_boxes": {tag: value_of(f"region_scan_box_{tag}") for tag in PROFILE_TAGS},
            "box_extension": {"rho1e3": value_of("box_extension_rho1e3"), "no_spec": value_of("box_extension_no_spec")},
            "meaning": (
                "the one-loop region is a sampled, box-bounded set: 1.5M uniform lambda(v_R) points per profile in "
                "[-0.8, 0.8] x [-0.1, 0.8] x [-0.1, 0.35] x [-0.1, 0.45] x [0, 0.08] after a tree prefilter (remnant "
                "levels > -0.1 v_R^2); its maximum lambda4 - lambda5 < 0 at M_GUT and '0 of 400 reachable' are sample "
                "statistics, not a proof over all couplings; an extended box puts 99.7% (rho = 1e3) and 97.5% (no "
                "spectators) of the UV volume inside the production box, and the gap sign of the rest was not recorded"
            ),
        },
        "pole_scheme_dependence": {
            "fj_vs_vf_vev_shift": value_of("fj_vs_vf_vev_shift"),
            "overall_factor_fj_over_vf": "about 1.36 (1 + 2 dv/v)",
            "scale_variation_rho1e3": value_of("scale_variation"),
            "meaning": "median relative pole-mass change 0.49 at Q = sqrt2 v_R and 0.74 at Q = 2 v_R; Q = v_R/sqrt2 removes every region point (research-recorded)",
        },
        "xi_spread_actual": {
            "values": xi_spreads,
            "meaning": "the FJ pole masses at the three best points are xi independent over xi in {0, 0.5, 1, 3, 10} to at most 1.85e-13 in the research record (rho = 1e3; 1.6e-14 and 7.7e-14 at rho = 1e4 and without spectators) and to <= 1e-12 when recomputed here (one_loop_masses.fj_pole_masses_over_v_R_squared)",
        },
        "scale_statement_rho_specific": {
            "n_core_all_scales": {tag: value_of(f"n_core_all_scales_{tag}") for tag in PROFILE_TAGS},
            "meaning": "no point positive at all three scale choices holds at rho = 1e3 only",
        },
        "sigma_not_global_min_in_region": {
            "sphere_min": value_of("sphere_min"),
            "meaning": "at rho = 1e3 sigma is the global minimum of the tree quartic at v_R in 43 of 60 region points (not in 17)",
        },
    }


def _derive_flags(checks: Mapping[str, bool]) -> dict[str, bool]:
    passed = bool(checks) and all(checks.values()) and len(checks) == EXPECTED_N_CHECKS
    flags: dict[str, bool] = {"not_closable_on_sos_witness_family": passed}
    for name, required in DERIVED_FLAG_CHECKS.items():
        flags[name] = bool(passed and all(checks.get(check) is True for check in required))
    flags["evidence_only"] = True
    for name in NEVER_TRUE_FLAGS:
        flags[name] = False
    return flags


def assemble_report(sections: Mapping[str, Mapping[str, Any]], *, record: Mapping[str, Any], started: float) -> dict[str, Any]:
    checks = _collect_checks(sections)
    flags = _derive_flags(checks)
    scope = scope_section(flags, "OPEN", TREE_CERTIFICATE_SCOPE)
    checks["scope.g6_open_and_evidence_only"] = scope["checks"]["g6_open_and_evidence_only"]
    flags = _derive_flags(checks)
    failures = sorted(name for name, value in checks.items() if not value)
    n_failed = len(failures)
    passed = n_failed == 0 and len(checks) == EXPECTED_N_CHECKS
    matching = sections["matching"]
    report = {
        "module": "g6_sm_pati_salam_remnant_rg_nogo_v20",
        "model_contract_id": MODEL_CONTRACT_ID,
        "gate": "G6",
        "G6_status": "OPEN",
        "status": STATUS_RECORDED if passed else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_RECORDED if passed else OVERALL_STATE_OPEN,
        "n_checks": len(checks),
        "n_failed": n_failed,
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "tree_certificate_scope": TREE_CERTIFICATE_SCOPE,
        "witness": {
            "weights": matching["witness"]["weights"],
            "lambda_at_M_GUT": matching["witness"]["lambda"],
            "beta_210_exchange": matching["witness"]["beta"],
            "lam4_minus_lam5": matching["witness"]["lam4_minus_lam5"],
            "strictly_inside_W_SOS": matching["witness"]["strictly_inside_W_SOS"],
            "tree_levels_r0_squared_units": matching["witness"]["tree_levels"],
        },
        "conventions": {
            "delta_R": "complex D in V = 4bar (x) 4bar (x) 3 symmetric in the two 4bar slots; kinetic |dD|^2; real coordinates D = (x_re + i x_im)/sqrt2",
            "gl4": "integer basis E_ij, rho(E_ij) = -E_ji on 4bar; B-L(4bar) = diag(-1/3, -1/3, -1/3, +1); T3R = i L_3; Y = T3R + (B-L)/2",
            "normalisation": "Tr_fund(T_a T_b) = delta_ab/2; 2 C4 X = sum_ij R(E_ij) R(E_ji) X - 4 X on pairs; CR X = -sum_m R(L_m)^2 X",
            "quartic_basis": "k = (20',1), (35,1), (45,3), (20',5), (35,5) with (C4, CR) = (6,0), (12,0), (8,2), (6,6), (12,6); V_k(D) = <X, P_k X>, X = D (x) D, sum_k V_k = |D|^4",
            "potential": "V = -mu^2 |D|^2 + sum_k lambda_k V_k(D); D0 = v S_33 v_{-1}; mu^2 = 2 lambda5 v^2; levels m^2/v^2 = G6 levels in units r0^2 M_GUT^2 (v = r0)",
            "states": "S_ab (x) v_t with v_{+1} = (1, i, 0), v_{-1} = (1, -i, 0), v_0 = e_3; order " + ", ".join(STATE_ORDER),
            "betas": "Landau gauge, MS-bar, effective-potential route, t = ln(mu/GeV); sum_k beta_k V_k = k'[(1/2) Tr M_S^4 + (3/2) Tr M_V^4] - 3 k' C2D phi.dV4",
            "matching": "lambda(w, beta) = (1/8) sum_q w_q c_q - sum_c beta_c f_c at mu = M_GUT (w_q/8 = O27_B0q, SIGMA_SCALE = 1/8)",
        },
        "group_theory": sections["group_theory"],
        "chart_binding": sections["chart_binding"],
        "matching": sections["matching"],
        "running": sections["running"],
        "one_loop_masses": sections["one_loop_masses"],
        "research_record": sections["research_record"],
        "provenance": {
            "research_note": RESEARCH_PROVENANCE_NOTE,
            "research_files": {name: {"script": script, "sha256": sha} for name, (script, sha) in RESEARCH_FILES.items()},
            "repository_inputs": [
                "g3_sm_pati_salam_candidate_v20 (sigma_std_raw_coordinates, _integer_projected_pairs, SWAPPED/HISTORICAL_SELF_WEIGHTS, SIGMA_SCALE, a_square_source)",
                "exact_gauged_u1x_g3_sos_bfb_stationarity_v20 (integer_sigma_generators, phi_source.pati_salam_direction)",
                G6_TREE_JSON.name + " (read-only cross-check of the witness levels)",
            ],
        },
        "scope": SCOPE,
        "disclosures": _disclosures(sections["running"], sections["one_loop_masses"], record),
        "verdict": "",
        "runtime_seconds": 0.0,
    }
    if report["G6_status"] != "OPEN" or any(flags[name] for name in NEVER_TRUE_FLAGS):
        raise AssertionError("the remnant RG module is status-neutral: G6 stays OPEN")
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def build_report(
    *,
    witness_weights: Mapping[str, Any] | None = None,
    cqk_override: Mapping[str, Sequence[Any]] | None = None,
    fierz_override: Mapping[str, Sequence[Any]] | None = None,
    beta_override: Mapping[tuple[int, int], Sequence[Any]] | None = None,
    profile_inputs: Mapping[str, Mapping[str, Any]] | None = None,
    region_points: Mapping[str, Sequence[float]] | None = None,
    thresholds: Mapping[str, Sequence[float]] | None = None,
    sos_cone_rows: Sequence[str] | None = None,
    g6_tree_report: Any = _DEFAULT,
    research_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the report (None / default = the committed inputs; every other value is a test mutation).

    g6_tree_report defaults to the committed G6 tree JSON; an explicit None stands for a missing report (fail closed)."""
    started = time.time()
    record = RESEARCH_RECORD if research_record is None else research_record
    group = group_theory_section(fierz_override=fierz_override, beta_override=beta_override)
    chart = chart_section(cqk_override=cqk_override)
    matching = matching_section(group, chart, witness_weights=witness_weights, g6_tree_report=g6_tree_report)
    running = running_section(
        group,
        chart,
        matching,
        profile_inputs=profile_inputs,
        region_points=region_points,
        thresholds=thresholds,
        sos_cone_rows=sos_cone_rows,
        research_record=record,
    )
    running.pop("seconds_internal", None)
    one_loop = one_loop_section(running, research_record=record)
    research = research_record_section(running, research_record=record)
    sections = {
        "group_theory": group,
        "chart_binding": chart,
        "matching": matching,
        "running": running,
        "one_loop_masses": one_loop,
        "research_record": research,
    }
    return assemble_report(sections, record=record, started=started)


def report_passes(report: Mapping[str, Any]) -> bool:
    """The no-go is recorded (every check passed) and nothing beyond evidence is claimed (G6 stays OPEN)."""
    try:
        return bool(
            report["status"] == STATUS_RECORDED
            and report["n_failed"] == 0
            and report["n_checks"] == EXPECTED_N_CHECKS
            and all(report["checks"].values())
            and report["G6_status"] == "OPEN"
            and report["flags"]["not_closable_on_sos_witness_family"] is True
            and all(report["flags"][name] is False for name in NEVER_TRUE_FLAGS)
            and report["tree_certificate_scope"] == TREE_CERTIFICATE_SCOPE
        )
    except (KeyError, TypeError):
        return False


def _sci(value: float) -> str:
    mantissa, exponent = f"{value:.2e}".split("e")
    return f"{mantissa}e{int(exponent)}"


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the G6 remnant RG no-go on the SOS witness family is NOT recorded (failed: "
            + ", ".join(report["failures"])
            + "). G6 stays OPEN; the G6 tree certificate is scoped to tree level at mu = M_GUT; nothing else is claimed."
        )
    running = report["running"]
    gap = running["gap_lam4_minus_lam5_GUT"]["rho1e3"]
    crossing = running["profiles"]["rho1e3"]["witness_lambda5_zero_crossing_GeV"]
    threshold = running["threshold_matching_min_slack"]["rho1e3"]["gX1.0"]
    scale_research = running["threshold_scale"]["scale_for_slack_le_research_0.03"]
    scale = running["threshold_scale"]["scale_for_exact_reach"]
    shift = running["threshold_gap_shift"][f"{THRESHOLD_PAIRING['rho1e3']}_gX1.0"]["dlam4_minus_dlam5"]
    spread_bound = FLOAT_TOLERANCES["pole_xi_spread_abs"]  # the checked bound (the spread itself is rounding noise)
    return (
        "G6 is not closable on the SOS-certified witness family at one loop with tree-level matching, with the stated "
        "approximations. Exact tree-level matching of the Delta_R = (10bar,1,3) EFT at mu = M_GUT gives lambda4 - "
        "lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3) >= 0 on every SOS-safe weight vector (and "
        "exactly 1/128 at the witness, whose tree levels 1/96, 17/288, 37/576, 353/3360 and 1/2 reproduce the G6 "
        "certificate), while the RG-improved one-loop-positive remnant region needs lambda4 - lambda5 < 0 at M_GUT "
        f"({gap:.3f} at rho = 1e3 for its best point, whose FJ pole masses are recomputed here and xi independent to "
        f"<= {spread_bound:.0e}; the region itself is a sampled, box-bounded research scan, so its lambda4 - lambda5 < 0 is a "
        "sampling statement, not a proof over all couplings). The certified witness runs tachyonic: lambda5 crosses "
        f"zero at {_sci(crossing)} GeV (rho = 1e3). Only the tree-matching statement is robust: the only computed "
        "one-loop M_GUT threshold (at the witness, assumed weight independent, not verified) shifts lambda4 - lambda5 by "
        f"{shift:.2f} (gX = g), which removes the lambda4 >= lambda5 obstruction; the remaining separation is "
        f"{threshold:.3f} at rho = 1e3 and closes at {scale_research:.2f} to {scale:.2f} times that threshold (and is "
        "smaller at rho = 1e4 and without spectators with the alpha^-1 = 23.78 threshold). G6 stays OPEN; the G6 tree certificate is scoped to tree level at "
        "mu = M_GUT; G3 and G4 are unchanged; G6 is not shown impossible in the contract (an anti-SOS G3 witness might "
        "exist); closing G6 would need controlled weight-dependent M_GUT thresholds and two-loop quartic running and, "
        "unless those thresholds open an SOS-safe route, an anti-SOS G3 witness."
    )


# ---------------------------------------------------------------------------------------------------------------------
# Markdown and CLI.
# ---------------------------------------------------------------------------------------------------------------------


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def _row(values: Sequence[Any]) -> str:
    return "| " + " | ".join(_fmt(value) for value in values) + " |"


def _markdown(report: Mapping[str, Any]) -> str:
    group = report["group_theory"]
    chart = report["chart_binding"]
    matching = report["matching"]
    running = report["running"]
    one_loop = report["one_loop_masses"]
    research = report["research_record"]
    lines = [
        "# G6 remnant RG no-go on the SOS witness family (v20)",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        f"**G6 status:** `{report['G6_status']}` (evidence only; this module never changes a gate status)",
        f"**Tree certificate scope:** {report['tree_certificate_scope']}",
        f"**Checks:** {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed",
        "",
        report["verdict"],
        "",
        "## Flags",
        "",
    ]
    lines += [f"- `{name}`: `{value}`" for name, value in report["flags"].items()]
    lines += ["", "## (A) group_theory (EXACT)", "", "Tree mass matrix A (m^2/v^2 = A lambda):", ""]
    lines.append(_row(["state", *QUARTIC_BASIS]))
    lines.append("|" + " --- |" * 6)
    for name, row in zip(group["tree_mass_matrix"]["rows"], group["tree_mass_matrix"]["A"]):
        lines.append(_row([name, *row]))
    lines += ["", "Sym^2(Delta_R) dimensions: " + ", ".join(f"{name} {dim}" for name, dim in zip(QUARTIC_BASIS, group["sym2"]["dimensions"])), ""]
    lines += ["Fierz vectors f_c (Q_c = sum_k f_ck V_k):", ""]
    lines.append(_row(["channel", *QUARTIC_BASIS]))
    lines.append("|" + " --- |" * 6)
    for channel, vector in group["fierz_vectors"]["f"].items():
        lines.append(_row([channel, *(vector or ["-"] * 5)]))
    lines += ["", "One-loop scalar tensor Q[(i,j)][k] (exact):", ""]
    lines.append(_row(["(i,j)", *QUARTIC_BASIS]))
    lines.append("|" + " --- |" * 6)
    for key, vector in group["beta_scalar_tensor"]["Q"].items():
        lines.append(_row([key, *(vector or ["-"] * 5)]))
    lines += ["", "Gauge tensor G[k]:", ""]
    lines.append(_row(["monomial", *QUARTIC_BASIS]))
    lines.append("|" + " --- |" * 6)
    for key, vector in group["beta_gauge_tensor"]["G"].items():
        lines.append(_row([key, *(vector or ["-"] * 5)]))
    witness_betas = group["witness_betas"]
    lines += [
        "",
        f"Witness 16 pi^2 beta (g4^2 = {witness_betas['g4_squared']}, gR^2 = {witness_betas['gR_squared']}): "
        + ", ".join(str(value) for value in (witness_betas["beta_16pi2"] or [])),
        "",
        "## (B) chart_binding (EXACT)",
        "",
        "c_qk (I_q restricted to Delta_R = sum_k c_qk V_k):",
        "",
    ]
    lines.append(_row(["q", *QUARTIC_BASIS]))
    lines.append("|" + " --- |" * 6)
    for channel, vector in chart["c_qk"].items():
        lines.append(_row([channel, *(vector or ["-"] * 5)]))
    lines += [
        "",
        f"Krylov basis: {chart['krylov_basis']['size']} vectors, realified rank {chart['krylov_basis']['rank_mod_p']} (mod p); witness portal residual on Delta_R: {chart['witness_portal']['max_abs_residual_on_krylov_basis']}.",
        "",
        "## (C) matching (EXACT)",
        "",
        f"- gap identity: {matching['tree_map']['gap_identity']}",
        f"- witness lambda(M_GUT) = " + ", ".join(str(value) for value in (matching["witness"]["lambda"] or [])) + f"; lambda4 - lambda5 = {matching['witness']['lam4_minus_lam5']}",
        "- witness tree levels (r0^2 units): " + ", ".join(f"{name} {level}" for name, level in (matching["witness"]["tree_levels"] or {}).items()),
        f"- historical (unswapped) weights: lambda4 - lambda5 = {matching['historical_weights']['lam4_minus_lam5']}",
        "",
        "## (D) running (FLOAT, recomputed)",
        "",
    ]
    lines.append(_row(["profile", "lambda5 = 0 (GeV)", "max abs lambda > 4 pi (GeV)", "max abs lambda > 1e3 (GeV)", "lambda4 - lambda5 at M_GUT", "tree LP slack", "slack with threshold gX1", "gX0", "SOS grid tree vacua"]))
    lines.append("|" + " --- |" * 9)
    for tag in PROFILE_TAGS:
        profile = running["profiles"][tag]
        lines.append(
            _row(
                [
                    tag,
                    profile["witness_lambda5_zero_crossing_GeV"],
                    profile["witness_events_GeV"]["4pi"],
                    profile["witness_events_GeV"]["1e3"],
                    running["gap_lam4_minus_lam5_GUT"][tag],
                    running["tree_matching_min_slack"][tag],
                    running["threshold_matching_min_slack"][tag]["gX1.0"],
                    running["threshold_matching_min_slack"][tag]["gX0.0"],
                    running["sos_safe_grid"]["per_profile"][tag]["tree_vacuum_at_v_R"],
                ]
            )
        )
    scale = running["threshold_scale"]
    lines += [
        "",
        f"Threshold fragility (rho = 1e3, gX = g): slack <= 0.03 at {_fmt(scale['scale_for_slack_le_research_0.03'])} x threshold, exact reach at {_fmt(scale['scale_for_exact_reach'])} x threshold; gX = 0 minimum slack over scale [0, 8]: {_fmt(scale['gX0_min_slack_over_scale_0_to_8'])}.",
        "",
        "Min LP slack with the research witness threshold, both coupling pairings (record-only; the pairing used is marked *):",
        "",
    ]
    lines.append(_row(["profile", "4 pi/g^2 at M_GUT", "M_GUT/M_X", "alpha^-1 = 23.78, gX1", "gX0", "alpha^-1 = 40, gX1", "gX0"]))
    lines.append("|" + " --- |" * 7)
    for tag in PROFILE_TAGS:
        slack = running["threshold_matching_min_slack_all_pairings"][tag]
        alpha = running["profiles"][tag]["alpha_inv_MGUT_recomputed"]
        cells = []
        for pairing in THRESHOLD_PAIRINGS:
            for gx in GX_VALUES:
                marker = "*" if running["inputs"]["threshold_pairing"][tag] == pairing else ""
                cells.append(f"{_fmt(slack[pairing][gx])}{marker}")
        lines.append(_row([tag, f"{min(alpha):.1f}-{max(alpha):.1f}", running["profiles"][tag]["M_GUT_over_M_X"], *cells]))
    shift = running["threshold_gap_shift"]
    lines += [
        "",
        "Threshold shift of lambda4 - lambda5: " + ", ".join(f"{key} {_fmt(value['dlam4_minus_dlam5'])}" for key, value in shift.items()) + ".",
        "",
        f"SOS-safe grid: {running['sos_safe_grid']['meaning']}.",
        "",
        f"Tolerances: {running['tolerance_semantics']}.",
        "",
    ]
    accuracy = running["accuracy_estimate"]
    lines.append(_row(["profile", "max abs dlambda(M_GUT)", "abs d(lambda4 - lambda5)", "crossing ratio - 1", "reference self-convergence"]))
    lines.append("|" + " --- |" * 5)
    for tag in PROFILE_TAGS:
        entry = accuracy["per_profile"][tag]
        lines.append(
            _row(
                [
                    tag,
                    entry.get("primary_minus_reference_lambda_GUT_max_abs"),
                    entry.get("primary_minus_reference_gap_abs"),
                    entry.get("primary_over_reference_crossing_minus_1"),
                    entry.get("reference_self_convergence_lambda_abs"),
                ]
            )
        )
    lines += [
        "",
        f"Accuracy ({accuracy['method']}): within budget `{accuracy['within_budget']}`.",
        "",
        "## (E) one_loop_masses (FLOAT)",
        "",
        "FJ R_xi one-loop pole masses m^2/v_R^2 at xi = 1 (recomputed; xi spread over {0, 0.5, 1, 3, 10}, min VF_L, FJ vev shifts):",
        "",
    ]
    lines.append(_row(["profile", *STATE_ORDER, "xi spread", "min VF_L", "dv Feynman", "dv Landau"]))
    lines.append("|" + " --- |" * 12)
    for tag in PROFILE_TAGS:
        pole = one_loop["fj_pole_masses_over_v_R_squared"][tag]
        lines.append(_row([tag, *pole["pole_by_xi"]["1.0"], pole["xi_spread"], min(pole["VF_L"]), pole["dv_feyn"], pole["dv_landau"]]))
    lines += ["", "Landau-gauge p = 0 vev-fixed CW curvature masses:", ""]
    lines.append(_row(["profile", *STATE_ORDER]))
    lines.append("|" + " --- |" * 8)
    for tag in PROFILE_TAGS:
        lines.append(_row([tag, *one_loop["masses_over_v_R_squared"][tag]["cw"]]))
    lines += ["", one_loop["label"], "", "## (F) research_record (not re-derived)", "", research["provenance_note"], ""]
    lines.append(_row(["entry", "label", "source", "key", "sha256"]))
    lines.append("|" + " --- |" * 5)
    for name, entry in research["entries"].items():
        lines.append(_row([name, entry["label"], f"{entry['source_json']} ({entry['source_script']})", entry["key"], entry["source_json_sha256"][:16] + "..."]))
    lines += ["", "## Scope", ""]
    for key, items in report["scope"].items():
        if isinstance(items, list):
            lines.append(f"**{key}**")
            lines.append("")
            lines += [f"- {item}" for item in items]
            lines.append("")
        else:
            lines += [f"**{key}:** {items}", ""]
    lines += ["## Disclosures", ""]
    for key, value in report["disclosures"].items():
        meaning = value.get("meaning") if isinstance(value, dict) else None
        lines.append(f"- `{key}`" + (f": {meaning}" if meaning else ""))
    lines += ["", "## Checks", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} `{name}`" for name, value in report["checks"].items()]
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "G6_status", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
