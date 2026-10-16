#!/usr/bin/env python3
"""G7 evidence on the decoupled-singlet benchmark BM-DA1: robust two-loop pass only (v20; status-neutral, G7 BLOCKED).

Rescue-study record (wfRESCUE, 2026-09-27; user decision U1: accept the no-go and record the results).  The decoupled
singlet benchmark BM-DA1 (g3_sm_pati_salam_decoupled_singlet_family_v20 with rS >> r0; rho = M_s/v_R = 1e3, G6 tree
remnant masses) has a research two-loop unification root v_R = 1.27e9 GeV, M_X = mu_G = 7.79e16 GeV,
alpha_U^-1 = 23.92 (code U1; the second code U2 gives v_R = 1.22e9 GeV, M_X = 8.36e16 GeV, alpha_U^-1 = 23.78), and
P,Q,R (+ bars) enter the SO(10) phase at x0 p = 1.53e18 GeV.  This module records whether
the SO(10) phase then stays perturbative up to the reduced Planck mass M_Pl,red = 2.435e18 GeV (alpha_10 = 1 above
M_Pl,red: the reduced-Planck Landau criterion) and whether the axion quality survives.  Every Landau number is
labelled by loop order (1L, 2L, 3L_gauge_only).  Checks by kind:

  (A) coefficients (EXACT; Fractions and sympy).  The SO(10) representation data (10, 16, 16bar, 45, 54, 120, 126,
      126bar, 210) from the Weyl dimension formula and C2 = (L, L + 2 rho), normalised to C2(10) = 9/2 and
      T = C2 dim/45; the Pickering-Gracey-Jones single-group b1, b2, b3 (hep-ph/0104247 eqs. (28)-(33), transcribed
      from arXiv v1; errata Phys. Lett. B512 (2001) 230 and B535 (2002) 377; gauge + matter terms, Yukawa and quartic
      terms omitted) with the pins (28/3, 22283/6, 132706057/864) without P,Q,R and (52/3, 25013/6, 109873879/864)
      with them; validated against the QCD three-loop coefficient with general Casimirs (symbolic; fixes every
      fermion term) and against Mihaila-Salomon-Steinhauser arXiv:1201.5868 eq. (5) as polynomials in n_G for
      U(1)_Y, SU(2)_L and SU(3)_C (which fixes 4 linear combinations of the 8 scalar coefficients, computed here); both SO(10) b3
      values are reproduced exactly by PyR@TE 3 (research-recorded); b1, b2 cross-checked with the repository's
      Machacek-Vaughn routine
      (two_loop_thresholds_v20.mv_gauge_coefficients, reused read-only) and every chain segment of the research code
      U1 (SM + remnants, Pati-Salam witness, spectators) re-derived as exact Fractions.
  (B) running (NUM).  alpha_10^-1 run from the research-recorded roots with two integrators (I1: fixed-step RK4 in
      t = ln mu plus bisection; I2: scipy DOP853 with a terminal event), which agree to <= 1e-6 on every alpha = 1
      scale.  The SO(10)-phase running is gauge + matter only at every order (1L, 2L and 3L_gauge_only: the two-loop
      Yukawa terms are omitted as well; they would raise the alpha = 1 scale).  BM-DA1 on the U1 root: 1L 1.25e21,
      2L 3.72e18 (pass), 3L_gauge_only 2.34e18 (fails, -3.8%); on the second-code U2 root (x0 p = 1.64e18 GeV from
      the same x0/p): 2L 3.88e18, 3L_gauge_only 2.438e18 (passes marginally, +0.14%).  The BM-DA1 three-loop outcome
      therefore lies within the two-code root uncertainty (and below the neglected two-loop GUT thresholds: the
      three-loop segment sits on a two-loop root with one-loop thresholds).  With P,Q,R at M_Pl,red instead of x0 p
      the U1 three-loop scale is 2.456e18 (+0.8%, disclosed: U(1)_X breaking at the cutoff).  BM-E (rho = 10^2.5,
      RG-improved remnants): 2L 3.58e18 pass, 3L 2.27e18 fails (U2 root: 3L 2.36e18, fails).
  (C) landau_cost (NUM).  Every analysed SO(10)-phase addition at mu_G (root held fixed: a lower bound on the
      damage) fails at three loops; a 120_H, a second 126bar and vectorlike pairs fail already at two loops.
  (D) quality (NUM; the RG-improved row is CONDITIONAL).  With the G6 tree remnant masses BM-DA1 passes both
      axion-quality bounds; with the RG-improved remnant masses (x3.1, 3.1, 1.3, 1.6, 1.6, 1.05; anti-SOS region
      points, committed GUT scalar spectrum) the rho = 1e3 root moves to v_R = 8.56e9 GeV, <S> = 2.85e13 GeV
      (y_s = 0.30) and fails both (NDA 0.27, Z17 3.2e-6 > 1e-10).  That failure is not robust to the GUT thresholds:
      the research scheme variant with the GUT scalar masses x2 (v_R = 1.96e9 GeV) passes three loops and both bounds
      (NDA 1.6e-11, Z17 4.3e-17), while U2 and the other six scheme variants keep the Z17 failure.  NDA convention:
      Lambda = max(M_s, <S>) = <S> = M_s/y_s, more conservative by y_s^-16 than eq. (qualitybound) of the manuscript
      (Lambda = M_s); both are recorded.
  (E) windows (NUM, CONDITIONAL).  The recorded rho scan: with the RG-improved remnants the three-loop criterion and
      the Z17 bound hold together for log10 rho in {2.55, 2.60, 2.65, 2.75}; with the NDA bound (Lambda = <S>) only
      at the knife edge 2.55, with the eq. (qualitybound) NDA bound (Lambda = M_s) at {2.55, 2.60, 2.65, 2.75}
      (convention-dependent).  Conditional: those remnant masses come from anti-SOS region points (G6 is not closed),
      the GUT thresholds are uncontrolled and the Yukawa/quartic terms are missing.
  (F) uncertainty (NUM).  Lambda_2L/Lambda_3L ~ 1.59; the 3L/2L term ratio at M_Pl,red on the two-loop trajectory
      is computed per root (its range is stated; the research quote 0.23-0.32 is research-recorded only); b3 scaled
      by 0.5, 0.75, 1.25.
  (G) planck_kinetic (EST plus one NUM derivative).  A Planck gauge-kinetic term c Phi210 F F/M shifts
      alpha_i^-1 by about c (M_X/M_Pl,red) alpha_U^-1 = 0.77 c at BM-DA1 (group factors omitted); with
      d ln Lambda/d alpha_U^-1 = 0.22 that moves the alpha = 1 scale by about 15-20% per unit c, more than the
      three-loop margins (-3.8% U1, +0.14% U2).  Not computed: the three-loop verdict is convention- and
      threshold-limited.
  (H) research_record (RESEARCH_RECORD / RESEARCH_RECORD_INPUT / LIT, not re-derived; sha256 provenance).  The
      research roots (codes U1 and U2), the research Landau and quality outputs, the literature transcriptions.

Verdict: G7 is not closed on BM-DA1: the reduced-Planck Landau criterion is passed robustly only at two loops (the
three-loop outcome lies within the two-code root uncertainty), and the RG-improved remnant masses fail axion quality
(conditional on the committed GUT scalar spectrum).  G7 stays BLOCKED (G6 dependency); no gate status changes, nothing
is wired into the gate ledger, no benchmark is adopted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from collections.abc import Callable, Mapping, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy
from scipy.integrate import solve_ivp

import two_loop_thresholds_v20 as two_loop

ROOT = Path(__file__).resolve().parent
MODULE = "g7_decoupled_singlet_benchmark_evidence_v20"
OUT_JSON = ROOT / "G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_V20.json"
OUT_MD = ROOT / "G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_V20.md"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"  # = g3_sm_pati_salam_candidate_v20.MODEL_CONTRACT_ID (not imported here)
GATE = "G7"
G7_STATUS = "BLOCKED"
STATUS_RECORDED = (
    "G7_DECOUPLED_SINGLET_BENCHMARK_BM_DA1__TWO_LOOP_PASS__THREE_LOOP_WITHIN_TWO_CODE_ROOT_UNCERTAINTY"
    "__RG_IMPROVED_QUALITY_FAIL_CONDITIONAL__G7_BLOCKED"
)
STATUS_INCOMPLETE = "G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_INCOMPLETE__G7_BLOCKED"
OVERALL_STATE_RECORDED = (
    "BM_DA1_TWO_LOOP_PASS__THREE_LOOP_GAUGE_ONLY_FAIL_U1_ROOT_MARGINAL_PASS_U2_ROOT__RG_IMPROVED_QUALITY_FAIL_CONDITIONAL"
    "__G7_BLOCKED"
)
OVERALL_STATE_OPEN = "G7_BENCHMARK_EVIDENCE_NOT_ESTABLISHED__G7_BLOCKED"
EXPECTED_N_CHECKS = 46
CHECK_COUNT_FAILURE = "check_count_equals_EXPECTED_N_CHECKS"
EXPECTED_SECTION_COUNTS = {
    "coefficients": 12,
    "running": 9,
    "landau_cost": 4,
    "quality": 5,
    "windows": 5,
    "uncertainty": 3,
    "planck_kinetic": 2,
    "research_record": 4,
    "verdict": 1,
    "scope": 1,
}
F = Fraction

# ---------------------------------------------------------------------------------------------------------------------
# Conventions and numerical settings.
# ---------------------------------------------------------------------------------------------------------------------

PI = math.pi
M_PL_RED = 2.435e18  # reduced Planck mass (GeV); the Landau criterion is alpha_10 = 1 above this scale
LOG_T_END = math.log(1.0e23)  # upper end of every SO(10)-phase integration (t = ln(mu/GeV))
LOOP_LABELS = ("1L", "2L", "3L_gauge_only")
PQR_PLACEMENTS = ("PQR_at_x0p", "PQR_at_max_x0p_MPlred")
RK4_STEP = 0.001  # I1: fixed RK4 step in t (spec: h <= 0.002)
RK4_BISECTIONS = 80
DOP853_TOL = 1.0e-12  # I2: rtol = atol
INTEGRATOR_AGREEMENT_REL = 1.0e-6
RECORD_AGREEMENT_REL = 1.0e-6
PIN_REL = 1.0e-6
FLOAT_TOLERANCES = {"rel": 1.0e-6, "abs": 1.0e-12}  # regression tolerances of float leaves (tests)
CONVENTION = (
    "t = ln(mu/GeV); dg/dt = b1 g^3/(16 pi^2) + b2 g^5/(16 pi^2)^2 + b3 g^7/(16 pi^2)^3, i.e. d alpha^-1/dt = "
    "-b1/(2 pi) - b2 alpha/(8 pi^2) - b3 alpha^2/(32 pi^3); Weyl fermions, real scalars (a complex scalar = 2 real), "
    "T(10) = 1, C_G = C2(45) = 8; SO(10) phase from mu_G = M_X with 3 x 16 + 5 x (16 + 16bar) + 210 (real) + "
    "126bar + 10 (complex), P,Q,R (+ bars) = 3 x (16 + 16bar) above x0 p; 1L: b2 = b3 = 0; 2L: b3 = 0; "
    "3L_gauge_only: gauge + matter three-loop term; the SO(10)-phase running is gauge + matter only at EVERY order "
    "(the two-loop Yukawa terms of 16.16.10_H, 16.16.126bar_H and y_s S 16_s 16bar_s and the three-loop Yukawa and "
    "quartic terms are omitted; the Yukawa terms enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 "
    "scale, so their omission is not conservative for a fail statement); U(1)_X feedback neglected"
)

# Axion-quality conventions (research e6_summary.py; manuscript eq. scalarquality with c17 = 1).
CHI = 0.0755**4  # topological susceptibility (GeV^4), chi^(1/4) = 75.5 MeV
Z17_PREFACTOR = 6.47e-37
Z17_REFERENCE_VS = 6.31e11
Z17_EXPONENT = 17
NDA_EXPONENT = 16
QUALITY_BOUND = 1.0e-10
Y_S_VALUES = (0.30, 0.34)
Y_S_PRIMARY = 0.30
QUALITY_CONVENTION = (
    "<S> = rho v_R / y_s (canonical), v_S = sqrt2 <S>, M_s = rho v_R = y_s <S>; NDA-conservative dtheta = 2 "
    "Lambda^16/(chi M_Pl,red^12) with Lambda = max(M_s, <S>) = <S> (every mass and scalar insertion <= Lambda), more "
    "conservative by y_s^-16 (2.3e8 at y_s = 0.30) than the manuscript's eq. (qualitybound), which uses Lambda = M_s; "
    "the eq. (qualitybound) value dtheta_NDA_Ms = 2 M_s^16/(chi M_Pl,red^12) is recorded alongside; "
    "Z17-EFT dtheta = 6.47e-37 (v_S/6.31e11)^17 (manuscript eq. scalarquality, c17 = 1); chi = (0.0755 GeV)^4; "
    "requirement dtheta < 1e-10; the hard-coded e2 flags NDA_quality_ok(vR<=2.2e9) / Z17_quality_ok(vR<=4.6e9) "
    "are thresholds for rho = 1e3 only and are NOT used"
)

# ---------------------------------------------------------------------------------------------------------------------
# (A) Exact coefficient data.
# ---------------------------------------------------------------------------------------------------------------------

# Pickering-Gracey-Jones, hep-ph/0104247 eqs. (28)-(33): beta_g = -g (a1 + 2 b1 + 3 c1) in loop order with
# (16 pi^2) a1/g^2 = 11/3 C_G - 2/3 T(R) - 1/6 T(S), etc.  T(R), T(S): sums of Dynkin indices over two-component
# fermions and real scalars; CR2 = sum T C2, CR3 = sum T C2^2 (fermions); CS2, CS3 likewise (real scalars).
PGJ_COEFFICIENTS: dict[str, Fraction] = {
    "a1.CG": F(11, 3), "a1.TR": F(-2, 3), "a1.TS": F(-1, 6),
    "b1.CG^2": F(17, 3), "b1.CG*TR": F(-5, 3), "b1.CG*TS": F(-1, 6), "b1.CS2": F(-1), "b1.CR2": F(-1),
    "c1.CG^3": F(2857, 162), "c1.CG^2*TR": F(-1415, 162), "c1.CG*TR^2": F(79, 162), "c1.CG^2*TS": F(-545, 648),
    "c1.CG*TR*TS": F(29, 162), "c1.CG*TS^2": F(-1, 324), "c1.CG*CS2": F(-1129, 216), "c1.TR*CS2": F(25, 54),
    "c1.TS*CS2": F(49, 216), "c1.CG*CR2": F(-205, 54), "c1.TR*CR2": F(11, 27), "c1.TS*CR2": F(23, 108),
    "c1.CR3": F(1, 3), "c1.CS3": F(-29, 12),
}

# SO(10) highest weights in the orthonormal basis of D5 (positive roots e_i +- e_j, rho = (4, 3, 2, 1, 0)).
SO10_RHO = (4, 3, 2, 1, 0)
_H = F(1, 2)
SO10_HIGHEST_WEIGHTS = {
    "10": (1, 0, 0, 0, 0),
    "16": (_H, _H, _H, _H, _H),
    "16bar": (_H, _H, _H, _H, -_H),
    "45": (1, 1, 0, 0, 0),
    "54": (2, 0, 0, 0, 0),
    "120": (1, 1, 1, 0, 0),
    "126": (1, 1, 1, 1, 1),
    "126bar": (1, 1, 1, 1, -1),
    "210": (1, 1, 1, 1, 0),
}
EXPECTED_SO10_REPS = {  # (dim, T, C2) with T(10) = 1 and C2(10) = 9/2
    "10": (10, "1", "9/2"),
    "16": (16, "2", "45/8"),
    "16bar": (16, "2", "45/8"),
    "45": (45, "8", "8"),
    "54": (54, "12", "10"),
    "120": (120, "28", "21/2"),
    "126": (126, "35", "25/2"),
    "126bar": (126, "35", "25/2"),
    "210": (210, "56", "12"),
}
SO10_DIM_G = 45

# SO(10)-phase content (research U1/A2 convention; spectators already below mu_G).
SO10_BASE_CONTENT = (
    ("16", "weyl", 3),  # the three families F
    ("16", "weyl", 5),  # spectators 5 x 16
    ("16bar", "weyl", 5),  # spectators 5 x 16bar
    ("210", "real", 1),
    ("126bar", "cplx", 1),
    ("10", "cplx", 1),
)
SO10_PQR_CONTENT = (("16", "weyl", 3), ("16bar", "weyl", 3))  # P, Q, R and their conjugates above x0 p
SO10_NO_SPECTATOR_CONTENT = (("16", "weyl", 3), ("210", "real", 1), ("126bar", "cplx", 1), ("10", "cplx", 1))
EXPECTED_SO10_B = {
    "no_PQR": ("28/3", "22283/6", "132706057/864"),
    "with_PQR": ("52/3", "25013/6", "109873879/864"),
}

# QCD three-loop coefficient with general Casimirs (Tarasov-Vladimirov-Zharkov 1980; Larin-Vermaseren 1993), LIT:
# mu^2 da/dmu^2 = -beta0 a^2 - beta1 a^3 - beta2 a^4 with a = g^2/(16 pi^2) and n_f Dirac flavours.
QCD_BETA_LITERATURE = {
    "beta0": "11/3 C_A - 4/3 T_F n_f",
    "beta1": "34/3 C_A^2 - 4 C_F T_F n_f - 20/3 C_A T_F n_f",
    "beta2": "2857/54 C_A^3 + 2 C_F^2 T_F n_f - 205/9 C_F C_A T_F n_f - 1415/27 C_A^2 T_F n_f + 44/9 C_F T_F^2 n_f^2 "
    "+ 158/27 C_A T_F^2 n_f^2",
}
QCD_NUMERIC_RECORD = {"5": "-9769/54", "6": "65/2"}  # b3 of SU(3) with n_f = 5, 6 (e4 record: equal to -beta2)

# Mihaila-Salomon-Steinhauser arXiv:1201.5868 eq. (5) (LIT): the pure (alpha_i/pi)^(n+1) coefficients of
# mu^2 d(alpha_i/pi)/dmu^2 as polynomials in n_G (coefficient lists in n_G^0, n_G^1, n_G^2); multiplied by
# (4, 16, 64) they are b1, b2, b3 in the convention above.  U(1)_Y GUT-normalised, one Higgs doublet.
MSS_EQ5 = {
    "U1_Y": (("1/40", "1/3"), ("9/800", "19/240"), ("489/512000", "-29/2400", "-209/8640")),
    "SU2_L": (("-43/24", "1/3"), ("-259/96", "49/48"), ("-667111/110592", "1603/432", "-415/1728")),
    "SU3_C": (("-11/4", "1/3"), ("-51/8", "19/12"), ("-2857/128", "5033/576", "-325/864")),
}
MSS_LOOP_FACTORS = (4, 16, 64)
EXPECTED_SM_B_AT_NG3 = {
    "U1_Y": ("41/10", "199/50", "-388613/24000"),
    "SU2_L": ("-19/6", "35/6", "324953/1728"),
    "SU3_C": ("-7", "-26", "65/2"),
}

# Local SU(3) tables for the remnant segments ((dim, T, C2)); SU(2), SU(4) and U(1)_Y from two_loop_thresholds_v20.
SU3_LOCAL = {
    "1": (1, F(0), F(0)),
    "3": (3, F(1, 2), F(4, 3)),
    "6": (6, F(5, 2), F(10, 3)),
    "8": (8, F(3), F(3)),
}
# The six complex (10bar,1,3) remnants below v_R in the research code U1's labels ((SU3, SU2)_Y).
REMNANTS = (
    ("(6,1)_4/3", F(4, 3), "6"),
    ("(6,1)_1/3", F(1, 3), "6"),
    ("(6,1)_-2/3", F(-2, 3), "6"),
    ("(3,1)_-1/3", F(-1, 3), "3"),
    ("(3,1)_-4/3", F(-4, 3), "3"),
    ("(1,1)_-2", F(-2), "1"),
)

# (C) Landau-cost options at BM-DA1: extra SO(10) multiplets at mu_G (research C/c6_landau_cost.py content).
LANDAU_OPTIONS = (
    ("baseline", "baseline (contract, BM-DA1)", ()),
    ("+real 45", "(a1) + real 45_H", (("45", "real", 1),)),
    ("+real 45 +1VL", "(a2) + real 45_H + 1 x (16+16bar)_V", (("45", "real", 1), ("16", "weyl", 1), ("16bar", "weyl", 1))),
    ("+complex 45", "(a') + complex 45_H (X != 0)", (("45", "cplx", 1),)),
    ("+second 126bar", "(b) + second complex 126bar_H", (("126bar", "cplx", 1),)),
    ("+10_F", "(c) + 10_F (one Weyl 10)", (("10", "weyl", 1),)),
    ("+2VL", "(c) + 2 x (16+16bar)_V only", (("16", "weyl", 2), ("16bar", "weyl", 2))),
    ("+120_H", "Route B: + complex 120_H (X=-2)", (("120", "cplx", 1),)),
    ("+120_H +real 45", "Route B + real 45 (for comparison)", (("120", "cplx", 1), ("45", "real", 1))),
)
EXPECTED_OPTION_B = {  # (b below P,Q,R; b above P,Q,R), each (b1, b2, b3)
    "baseline": (("28/3", "22283/6", "132706057/864"), ("52/3", "25013/6", "109873879/864")),
    "+real 45": (("32/3", "23179/6", "128249017/864"), ("56/3", "25909/6", "103840807/864")),
    "+real 45 +1VL": (("40/3", "24089/6", "120626611/864"), ("64/3", "26819/6", "94677409/864")),
    "+complex 45": (("12", "8025/2", "4562891/32"), ("20", "8935/2", "10801535/96")),
    "+second 126bar": (("21", "11301/2", "3765131/32"), ("29", "12211/2", "6722231/96")),
    "+10_F": (("10", "7499/2", "14556977/96"), ("18", "8409/2", "3992949/32")),
    "+2VL": (("44/3", "24103/6", "117998269/864"), ("68/3", "26833/6", "92084107/864")),
    "+120_H": (("56/3", "30235/6", "100917097/864"), ("80/3", "32965/6", "65036695/864")),
    "+120_H +real 45": (("20", "10377/2", "10182673/96"), ("28", "11287/2", "2006949/32")),
}
FLAVOUR_ROLE = {
    "baseline": "the contract content (no flavour repair)",
    "+real 45": "B-L-breaking 45_H: the 45 scalar portal (splits d from e off the certified orientation)",
    "+real 45 +1VL": "45_H plus one vectorlike 16 + 16bar",
    "+complex 45": "complex 45_H (X != 0)",
    "+second 126bar": "a second 126bar_H",
    "+10_F": "one Weyl 10 (vectorlike 10 matter)",
    "+2VL": "two vectorlike 16 + 16bar pairs",
    "+120_H": "a 120_H (among the analysed candidates the only d/e splitter on the certified orientation, through a "
    "(15,2,2)_120 admixture of O((v_R/M15)^2))",
    "+120_H +real 45": "a 120_H plus a real 45_H",
}
EXPECTED_TWO_LOOP_FAIL_OPTIONS = ("+real 45 +1VL", "+second 126bar", "+2VL", "+120_H", "+120_H +real 45")
EXPECTED_TWO_LOOP_PASS_OPTIONS = ("baseline", "+real 45", "+complex 45", "+10_F")

# Committed G6 tree remnant levels m^2/(r0 M_GUT)^2 (G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json, research U1 labels).
G6_TREE_LEVELS = {
    "(6,1)_4/3": F(1, 96),
    "(1,1)_2": F(1, 96),
    "(3,1)_1/3": F(17, 288),
    "(6,1)_1/3": F(37, 576),
    "(3,1)_4/3": F(37, 576),
    "(6,1)_2/3": F(353, 3360),
}
G6_MASS_REL_TOL = 1.0e-5  # U1 uses the finite-r0 G6 spectrum (O(r0^2) away from the r0 -> 0 levels)
RG_IMPROVED_MULTIPLIERS = {  # research e2_unif.py MULT_D (D-D region, skeptic summary)
    "(6,1)_4/3": 3.1, "(1,1)_2": 3.1, "(3,1)_1/3": 1.3, "(6,1)_1/3": 1.6, "(3,1)_4/3": 1.6, "(6,1)_2/3": 1.05,
}

# Benchmarks: (variant, log10 rho) of the research roots.
BENCHMARKS = {
    "BM-DA1": ("G6", "3.00"),
    "BM-E": ("D", "2.50"),
    "D_rho1e3": ("D", "3.00"),
}
BENCHMARK_MEANING = {
    "BM-DA1": "rho = 1e3, G6 exact tree remnant masses (the decoupled-singlet benchmark)",
    "BM-E": "rho = 10^2.5, RG-improved remnant masses (the route-E reference point)",
    "D_rho1e3": "rho = 1e3, RG-improved remnant masses (BM-DA1 with the one-loop remnant masses)",
}
EXPECTED_BENCHMARK_SCALES = {  # alpha_10 = 1 scale (GeV), I2, pinned to PIN_REL
    "BM-DA1": {
        "PQR_at_x0p": {"1L": 1.248578312e21, "2L": 3.723514786e18, "3L_gauge_only": 2.343519513e18},
        "PQR_at_max_x0p_MPlred": {"1L": 1.545765812e21, "2L": 4.142308484e18, "3L_gauge_only": 2.455600511e18},
    },
    "BM-E": {
        "PQR_at_x0p": {"1L": 1.560393803e21, "2L": 3.584004188e18, "3L_gauge_only": 2.266650459e18},
        "PQR_at_max_x0p_MPlred": {"1L": 2.334838186e21, "2L": 4.429202069e18, "3L_gauge_only": 2.578713127e18},
    },
    "D_rho1e3": {
        "PQR_at_x0p": {"1L": 5.798548610e21, "2L": 7.450058095e18, "3L_gauge_only": 4.690743299e18},
        "PQR_at_max_x0p_MPlred": {"1L": 9.431745592e21, "2L": 9.965879472e18, "3L_gauge_only": 5.988227012e18},
    },
}
EXPECTED_LANDAU_COST = {  # (2L, 3L_gauge_only) alpha = 1 scale at BM-DA1 (GeV), P,Q,R at x0 p
    "baseline": (3.723514786e18, 2.343519513e18),
    "+real 45": (3.032024814e18, 1.992318422e18),
    "+real 45 +1VL": (2.261963922e18, 1.554366051e18),
    "+complex 45": (2.517999422e18, 1.713368392e18),
    "+second 126bar": (8.124031146e17, 6.667255278e17),
    "+10_F": (3.419776015e18, 2.189716677e18),
    "+2VL": (2.045197428e18, 1.415609544e18),
    "+120_H": (1.083312526e18, 8.495541729e17),
    "+120_H +real 45": (9.646811334e17, 7.840333284e17),
}

# (E) Expected windows (log10 rho sets) at y_s = 0.30 and 0.34 (same sets); 3L means P,Q,R at x0 p.
EXPECTED_WINDOWS = {
    "D": {
        "2L": ("2.30", "2.35", "2.40", "2.45", "2.50", "2.55", "2.60", "2.65", "2.75", "3.00", "3.25"),
        "3L_gauge_only": ("2.55", "2.60", "2.65", "2.75", "3.00", "3.25"),
        "NDA": ("2.00", "2.25", "2.30", "2.35", "2.40", "2.45", "2.50", "2.55"),
        "Z17": ("2.00", "2.25", "2.30", "2.35", "2.40", "2.45", "2.50", "2.55", "2.60", "2.65", "2.75"),
        "3L_and_Z17": ("2.55", "2.60", "2.65", "2.75"),
        "3L_and_NDA": ("2.55",),
        "NDA_Ms": ("2.00", "2.25", "2.30", "2.35", "2.40", "2.45", "2.50", "2.55", "2.60", "2.65", "2.75"),
        "3L_and_NDA_Ms": ("2.55", "2.60", "2.65", "2.75"),
    },
    "D_best": {
        "2L": ("2.25", "2.50", "2.75", "3.00"),
        "3L_gauge_only": ("2.50", "2.75", "3.00"),
        "NDA": ("2.25",),
        "Z17": ("2.25", "2.50"),
        "3L_and_Z17": ("2.50",),
        "3L_and_NDA": (),
        "NDA_Ms": ("2.25", "2.50", "2.75"),
        "3L_and_NDA_Ms": ("2.50", "2.75"),
    },
}
EXPECTED_WINDOW_ROWS = 24
KNIFE_EDGE = ("D", "2.55")

# (F), (G) pins.
EXPECTED_SCALE_RATIO_2L_OVER_3L = {"BM-DA1": 1.58886, "BM-E": 1.58119, "D_rho1e3": 1.58825}
EXPECTED_TERM_RATIO = {"BM-DA1": 0.31986, "BM-E": 0.33662, "D_rho1e3": 0.18564}
RATIO_PIN_ABS = 1.0e-4
B3_SENSITIVITY_FACTORS = (0.5, 0.75, 1.25)
EXPECTED_DLNLAMBDA_DAU = {"2L": 0.21987, "3L_gauge_only": 0.22709}
DLNLAMBDA_STEP = 0.5

# ---------------------------------------------------------------------------------------------------------------------
# (H) Research record (not re-derived; values embedded, scratch never read at runtime).
# ---------------------------------------------------------------------------------------------------------------------

RESEARCH_PROVENANCE_NOTE = (
    "scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit "
    "only; the source files are not in the repository and were hashed at generation time (the session scratch area "
    "that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at "
    "runtime"
)
RESEARCH_PATH_NOTE = (
    "paths are relative to the session scratchpad; wfRESCUE/* is the 2026-09-27 rescue study, wfGNG/U1/* the D-C "
    "workstream U1 code (2026-09-26) that the rescue study drove read-only, wfREC/verify-M2/* the record PR's "
    "independent verifier (MSS 2012 text, PyR@TE 3 runs)"
)
_E = "wfRESCUE/E-G7-completion/"
_E2 = _E + "e2_unif.py (U1 two-loop code wfGNG/U1/rge.py driven through wfDA/A2)"
RESEARCH_FILES: dict[str, tuple[str, str]] = {
    _E + "e2_unif_G6_ys0.0_3.0.json": (_E2, "15265343e05ef9cfdac5ed552cb3042bb8ee6d926345553b7f120991862da2d3"),
    _E + "e2_unif_D_ys0.0_3.0.json": (_E2, "d30403a2631e7edce75c7ebf9dc4df8b950ea520d2a16b852f3bae7eeb8e6e9b"),
    _E + "e2_unif_D_ys0.0_1.5_1.75_2.0_2.25_2.5_2.75_3.25.json": (
        _E2, "63a9a490c7a0217d7ea58fcef1bf2d5f3e08850c27a797c02906de8563d15146"),
    _E + "e2_unif_D_ys0.0_2.3_2.35_2.4_2.45_2.55_2.6_2.65.json": (
        _E2, "ea935ae57b44a38581812ef71171c5b729e3ce9787ea9d8b1049abd26ee5d746"),
    _E + "e2_unif_D_sq_ys0.0_2.0_2.5_3.0.json": (_E2, "2a40ba7d06d16b090354ac34bd313186523e6a61181a94c2e11a8cddb393ecbb"),
    _E + "e2_unif_D_x2_ys0.0_2.0_2.5_3.0.json": (_E2, "6035d598d04005df92fed8ccabf1194e4d8af8d825bb9481d72f631676332b3c"),
    _E + "verify-feasibility/e2_unif_D_best_ys0.0_2.25_2.5_2.75_3.0.json": (
        _E + "verify-feasibility/v_e2_unif.py", "b7c55aca8bb7bf800f13f42604dd9309da6ddb64f42ca9bad956227160ac2790"),
    _E + "e4_so10_3loop.json": (_E + "e4_so10_3loop.py", "19a85330788e9f75948f7facd9e321cc3215e4a97546904315a3aa2badb13391"),
    _E + "e5_crosscheck.json": (
        _E + "e5_crosscheck.py (U2 code wfGNG/U2, PyR@TE coefficients)",
        "7244bc65daa5c754d8e7c96c2ab99bc094f4a296d308a46082e53c44519f7459"),
    _E + "e6_summary.json": (_E + "e6_summary.py", "ea19c9031175b03a6616008f9a1febc60122b123d03c41410c958b92ffb35f7a"),
    _E + "verify-physics/v1_threeloop.json": (
        _E + "verify-physics/v1_threeloop.py (independent verifier)",
        "38cd9b2f9033eaad8d86268b23a987ecc4e852c1c25292b691ad35d44a16bf9b"),
    _E + "verify-physics/mss.txt": (
        "LIT: Mihaila, Salomon, Steinhauser, arXiv:1201.5868 (text of the PDF read by the verifier)",
        "5430459c261b5572dc8df5fb2ea05067c7872a8c3af362aca783470d0307ca43"),
    _E + "verify-physics/pgj.txt": (
        "LIT: Pickering, Gracey, Jones, hep-ph/0104247 (text of the PDF read by the verifier)",
        "e3de10df9895c6659adc11ed90c98de06d163decc9a18f88c1649937fc384c39"),
    _E + "VERIFY_feasibility.md": (
        "route E feasibility verifier report", "770aa7ca8197e606842061ffbc7745d7d7459e1a1a4f2c6385b57e4e4e9b5d33"),
    "wfRESCUE/C-other-extensions/c6_landau_cost.json": (
        "wfRESCUE/C-other-extensions/c6_landau_cost.py",
        "78cc4eb01879dae36a6aeeee96339ec1772c7409621ba237479fa4464afbb1a4"),
    "wfRESCUE/critic/c1_f17_light1522_scan.json": (
        "wfRESCUE/critic/c1_f17_light1522_scan.py (Route-B engine)",
        "4481ba5df0ee232dec1a04c39439fcfda59a423312d9b84239bb52488b139d3d"),
    "wfRESCUE/critic/c5_witness_chain_3loop.json": (
        "wfRESCUE/critic/c5_witness_chain_3loop.py", "8cd545b154edb641291f44b91bad55d826ddd3e1a17bd395d2f65861ff00a712"),
    "wfRESCUE/final/j1_adjudication_checks.json": (
        "wfRESCUE/final/j1_adjudication_checks.py", "cd4b85a0983688ccf262eb46ca7fa6966234f9a811963a9a420759ae9cb6a21c"),
    "wfGNG/U1/betas.json": (
        "wfGNG/U1/print_betas.py (U1: independent Machacek-Vaughn implementation)",
        "79328ca11341b5638178a84c09982ba0db3ea87f77feb7a51b5fc59a245274b6"),
    "wfGNG/U1/rge.py": ("U1 two-loop RG code (segment content and thresholds)",
                        "04bb4ad527c05477e0936c6aa103105ecd8214c9ec0c463d135c71b4d203103c"),
    "wfREC/verify-M2/mss2012.txt": (
        "LIT: Mihaila, Salomon, Steinhauser, arXiv:1208.3357v2 (text of the PDF read by the verifier)",
        "2b0df369fd026bfcb6b829148b9e132d757ba4da3a877268838fe79a980f79c4"),
    "wfREC/verify-M2/pyrate_out/VSO10noPQR/PythonOutput/RGEs.py": (
        "PyR@TE 3 -l [3,0,0] on wfREC/verify-M2/VSO10noPQR.model (sha256 "
        "78d00a119f98c9246d740e467e22bc25a26f6c32a26e8f9ef591753f39451aa9)",
        "9763855e8753873fce1fb2762bfdf0f5834cc1333d4a355d81342450310c1e62"),
    "wfREC/verify-M2/pyrate_out/VSO10PQR/PythonOutput/RGEs.py": (
        "PyR@TE 3 -l [3,0,0] on wfREC/verify-M2/VSO10PQR.model (sha256 "
        "3574fe9b807303ec803248a2ddbe37ae235ccc9a64a89e51742fde8c9f68b25c)",
        "7a316a60eba04148a57ce3e4aa51b032a278067a80ee31589c6aa2c288819be3"),
}
RESEARCH_LABELS = ("RESEARCH_RECORD", "RESEARCH_RECORD_INPUT", "LIT")


def research_files_digest(files: Mapping[str, Sequence[str]]) -> str:
    """sha256 over the sorted (path, script, sha256) triples: pins the whole provenance table."""
    text = "\n".join(f"{name}\t{files[name][0]}\t{files[name][1]}" for name in sorted(files))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


RESEARCH_FILES_DIGEST = "5c85f8dc90593af23ee364a7fd926f31c7408c0f41c0598b4b1269f5645ec988"


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
_LIT = "LIT"
_ROOT_FIELDS = ("variant", "log10_rho", "v_R_GeV", "alpha_U_inv", "mu_G_GeV", "x0p_GeV")
_ROOT_FILES = {
    "roots_e2_D_sq": (_E + "e2_unif_D_sq_ys0.0_2.0_2.5_3.0.json", (
        ("D_sq", "2.50", 1907354463.5879536, 22.115542516295307, 7.688834617053275e16, 1.4545020482923067e18),
        ("D_sq", "3.00", 3535253051.494902, 27.204186396317485, 5.28022855349453e16, 1.1078363506809742e18),
    )),
    "roots_e2_D_x2": (_E + "e2_unif_D_x2_ys0.0_2.0_2.5_3.0.json", (
        ("D_x2", "2.00", 23411372366.74563, 27.138197951193163, 3.3546757870930868e16, 7.029850288307057e17),
        ("D_x2", "2.50", 32666568149.80416, 31.118090582561955, 2.6871193707019932e16, 6.029738099631443e17),
        ("D_x2", "3.00", 40610842525.46279, 34.639705207028975, 2.2955570030799772e16, 5.43475779834305e17),
    )),
    "roots_e2_D_scan_a": (_E + "e2_unif_D_ys0.0_1.5_1.75_2.0_2.25_2.5_2.75_3.25.json", (
        ("D", "2.00", 187434282.63811576, 9.427072161715847, 3.3377503901014086e17, 4.122372323967593e18),
        ("D", "2.00", 2560177360.6462255, 19.867027851940552, 8.0683606445846e16, 1.4466276818656164e18),
        ("D", "2.25", 4211436891.506577, 23.161348169697604, 6.025932190426988e16, 1.1665710019408133e18),
        ("D", "2.50", 5745468809.640461, 25.716864836749135, 4.9850482431518744e16, 1.0169120550820891e18),
        ("D", "2.75", 7195746524.362495, 27.934982966709647, 4.32214543873622e16, 9.189218984694612e17),
        ("D", "3.25", 9833460216.002699, 31.82708189981223, 3.5058304923760268e16, 7.955992113677635e17),
    )),
    "roots_e2_D_scan_b": (_E + "e2_unif_D_ys0.0_2.3_2.35_2.4_2.45_2.55_2.6_2.65.json", (
        ("D", "2.30", 4525399284.894231, 23.71103948594786, 5.770684019758163e16, 1.1303361324210998e18),
        ("D", "2.35", 4835593834.56997, 24.23861871178785, 5.543219881596317e16, 1.0977945198812412e18),
        ("D", "2.40", 5142254192.1854, 24.74721909181928, 5.338768387264883e16, 1.0683395364735009e18),
        ("D", "2.45", 5445520289.8489685, 25.239307022605804, 5.153668126376457e16, 1.0415021739015738e18),
        ("D", "2.55", 6042133118.51992, 26.181513859863973, 4.830616580213064e16, 9.942714384163252e17),
        ("D", "2.60", 6335516707.529448, 26.634599984105733, 4.68851450898962e16, 9.733373135435058e17),
        ("D", "2.65", 6625602468.762978, 27.077254826499484, 4.557214669344594e16, 9.539087265014538e17),
    )),
    "roots_e2_D_rho1e3": (_E + "e2_unif_D_ys0.0_3.0.json", (
        ("D", "3.00", 8560428044.594446, 29.950197955900347, 3.8551068310509176e16, 8.486747579803726e17),
    )),
    "roots_e2_G6_rho1e3": (_E + "e2_unif_G6_ys0.0_3.0.json", (
        ("G6", "3.00", 1266547317.6994867, 23.915307659746492, 7.793732345676163e16, 1.5331635730399654e18),
    )),
    "roots_e2_D_best": (_E + "verify-feasibility/e2_unif_D_best_ys0.0_2.25_2.5_2.75_3.0.json", (
        ("D_best", "2.25", 6351116492.731352, 24.554301968776322, 4.9945934058715656e16, 9.955634744386006e17),
        ("D_best", "2.50", 8221861690.580313, 26.903824768734392, 4.251777310738453e16, 8.871203501619665e17),
        ("D_best", "2.75", 9987392095.718596, 29.002065424806833, 3.748507614222224e16, 8.120408560727181e17),
        ("D_best", "3.00", 11641133764.432993, 30.93709593313107, 3.3811540722182276e16, 7.565014281041528e17),
    )),
}
VARIANT_MEANING = {
    "G6": "G6 exact tree remnant masses (BM-DA1)",
    "D": "RG-improved remnant masses x(3.1, 3.1, 1.3, 1.6, 1.6, 1.05) (D-D region, skeptic summary)",
    "D_sq": "the multipliers read as m^2 ratios (square roots)",
    "D_x2": "the multipliers squared (pessimistic)",
    "D_best": "D's best controlled rho = 1e3 point pole masses (x3.53, 3.74, 1.48, 1.81, 1.82, 1.21)",
}


def _root_rows(tag: str) -> list[dict[str, Any]]:
    source, rows = _ROOT_FILES[tag]
    return [dict(zip(_ROOT_FIELDS, row)) | {"source": source} for row in rows]


VARIANT_ORDER = ("G6", "D", "D_best", "D_sq", "D_x2")


def default_window_roots() -> list[dict[str, Any]]:
    """The 24 perturbative research roots (U1 code), deduplicated by (variant, log10 rho, v_R), in table order."""
    rows: list[dict[str, Any]] = []
    for tag in _ROOT_FILES:
        rows += _root_rows(tag)
    return sorted(rows, key=lambda row: (VARIANT_ORDER.index(row["variant"]), row["log10_rho"], row["v_R_GeV"]))


# e6_summary.json rows: (variant, log10 rho, y_s, v_R, <S>, dtheta_NDA, dtheta_Z17, L1_2L_pqr_x0p, L1_3L_pqr_MPl).
E6_ROWS = (
    ("D", "2.00", "0.30", 187434282.63811576, 62478094212.70526, 7.636581325586912e-44, 1.9793941796951422e-51, 1.5707129431138555e18, 9.141539553622163e17),
    ("D", "2.00", "0.30", 2560177360.6462255, 853392453548.742, 1.121076818902522e-25, 3.9690786494429285e-32, 1.5707129431138555e18, 9.141539553622163e17),
    ("D", "2.25", "0.30", 4211436891.506577, 2496370503614.8237, 3.2225471593438818e-18, 3.337443007967786e-24, 2.4313506311451597e18, 1.5530353146351862e18),
    ("D", "2.30", "0.30", 4525399284.894231, 3009786217778.857, 6.424287810427254e-17, 8.021695504006834e-23, 2.633315642106104e18, 1.7204213027304276e18),
    ("D", "2.35", "0.30", 4835593834.56997, 3608515378327.51, 1.1708777949089104e-15, 1.752853678995524e-21, 2.848367313966135e18, 1.904657182644155e18),
    ("D", "2.40", "0.30", 5142254192.1854, 4305586177574.587, 1.9759283004953825e-14, 3.529465993586874e-20, 3.0776880398609393e18, 2.10756700043342e18),
    ("D", "2.45", "0.30", 5445520289.8489685, 5115853812254.867, 3.118491867531665e-13, 6.618632625750992e-19, 3.322483716608342e18, 2.331151263720462e18),
    ("D", "2.50", "0.30", 5745468809.640461, 6056255887973.414, 4.640043675694875e-12, 1.165820852923879e-17, 3.5840041878552684e18, 2.5787131269552604e18),
    ("D", "2.55", "0.30", 6042133118.51992, 7146099099941.616, 6.551777733072225e-11, 1.942377883425923e-16, 3.8635582901413796e18, 2.831872099759703e18),
    ("D", "2.60", "0.30", 6335516707.529448, 8407382101429.858, 8.827285551594116e-10, 3.0788851974207427e-15, 4.1625259589333187e18, 3.0971511845074406e18),
    ("D", "2.65", "0.30", 6625602468.762978, 9865159703037.785, 1.1400411477797218e-08, 4.6658436433361197e-14, 4.482368724291266e18, 3.3786876539976596e18),
    ("D", "2.75", "0.30", 7195746524.362495, 13488218787479.514, 1.7003104832379841e-06, 9.514552535476662e-12, 5.190991251356957e18, 4.0000901470244076e18),
    ("D", "3.00", "0.30", 8560428044.594446, 28534760148648.156, 0.27367947303886964, 3.239828231454218e-06, 7.450058095353779e18, 5.988227011708973e18),
    ("D", "3.25", "0.30", 9833460216.002699, 58288799438514.99, 25154.53931882347, 0.6082848675053429, 1.0634037192182352e19, 8.823598145373262e18),
    ("D", "2.00", "0.34", 187434282.63811576, 55127730187.68111, 1.0308046855126193e-44, 2.3575017805912994e-52, 1.5707129431138555e18, 9.141539553622163e17),
    ("D", "2.00", "0.34", 2560177360.6462255, 752993341366.5369, 1.513257292071705e-26, 4.7272595218046725e-33, 1.5707129431138555e18, 9.141539553622163e17),
    ("D", "2.25", "0.34", 4211436891.506577, 2202679856130.7266, 4.349874072586735e-19, 3.974967651525494e-25, 2.4313506311451597e18, 1.5530353146351862e18),
    ("D", "2.30", "0.34", 4525399284.894231, 2655693721569.5796, 8.671663004336667e-18, 9.554014873869148e-24, 2.633315642106104e18, 1.7204213027304276e18),
    ("D", "2.35", "0.34", 4835593834.56997, 3183984157347.8027, 1.580479884514332e-16, 2.0876870871593769e-22, 2.848367313966135e18, 1.904657182644155e18),
    ("D", "2.40", "0.34", 5142254192.1854, 3799046627271.694, 2.6671570216416017e-15, 4.203671229193481e-21, 3.0776880398609393e18, 2.10756700043342e18),
    ("D", "2.45", "0.34", 5445520289.8489685, 4513988657871.94, 4.2094176592004995e-14, 7.88293628441948e-20, 3.322483716608342e18, 2.331151263720462e18),
    ("D", "2.50", "0.34", 5745468809.640461, 5343755195270.659, 6.263246023274531e-13, 1.3885181460126427e-18, 3.5840041878552684e18, 2.5787131269552604e18),
    ("D", "2.55", "0.34", 6042133118.51992, 6305381558772.014, 8.843752063583304e-12, 2.3134145617539673e-17, 3.8635582901413796e18, 2.831872099759703e18),
    ("D", "2.60", "0.34", 6335516707.529448, 7418278324791.051, 1.1915288948018554e-10, 3.667019641471076e-16, 4.1625259589333187e18, 3.0971511845074406e18),
    ("D", "2.65", "0.34", 6625602468.762978, 8704552679150.986, 1.5388558134921782e-09, 5.557121875956845e-15, 4.482368724291266e18, 3.3786876539976596e18),
    ("D", "2.75", "0.34", 7195746524.362495, 11901369518364.275, 2.295121256779435e-07, 1.1332040264648223e-12, 5.190991251356957e18, 4.0000901470244076e18),
    ("D", "3.00", "0.34", 8560428044.594446, 25177729542924.84, 0.03694193397664229, 3.858706316717378e-07, 7.450058095353779e18, 5.988227011708973e18),
    ("D", "3.25", "0.34", 9833460216.002699, 51431293622219.11, 3395.4220987441477, 0.07244805875257541, 1.0634037192182352e19, 8.823598145373262e18),
    ("D_sq", "2.50", "0.30", 1907354463.5879536, 2010528136742.2095, 1.0097574995469251e-19, 8.422340143920851e-26, 2.4585564202482033e18, 1.5118797907032643e18),
    ("D_sq", "3.00", "0.30", 3535253051.494902, 11784176838316.342, 1.9590369163164123e-07, 9.577395128017356e-13, 5.348752759858506e18, 3.9502225074297457e18),
    ("D_sq", "2.50", "0.34", 1907354463.5879536, 1773995414772.5376, 1.362995714164651e-20, 1.0031191406805614e-26, 2.4585564202482033e18, 1.5118797907032643e18),
    ("D_sq", "3.00", "0.34", 3535253051.494902, 10397803092632.064, 2.644356612382371e-08, 1.1406887167468988e-13, 5.348752759858506e18, 3.9502225074297457e18),
    ("D_x2", "2.00", "0.30", 23411372366.74563, 7803790788915.21, 2.6800598291493725e-10, 8.67672116685388e-16, 3.3465577280794296e18, 2.607373215475437e18),
    ("D_x2", "2.50", "0.30", 32666568149.80416, 34433586231497.87, 5.533127865527428, 7.904210490983163e-05, 6.868497543207255e18, 6.011769178938456e18),
    ("D_x2", "3.00", "0.30", 40610842525.46279, 135369475084875.97, 18013019557.271626, 1011609.2680074004, 1.3867226888017805e19, 1.2907865810498497e19),
    ("D_x2", "2.00", "0.34", 23411372366.74563, 6885697754925.185, 3.617611220985722e-11, 1.0334164771416427e-16, 3.3465577280794296e18, 2.607373215475437e18),
    ("D_x2", "2.50", "0.34", 32666568149.80416, 30382576086615.766, 0.7468753210570648, 9.414087652582273e-06, 6.868497543207255e18, 6.011769178938456e18),
    ("D_x2", "3.00", "0.34", 40610842525.46279, 119443654486655.25, 2431442050.862856, 120484.87739604298, 1.3867226888017805e19, 1.2907865810498497e19),
    ("G6", "3.00", "0.30", 1266547317.6994867, 4221824392331.623, 1.4429697905847307e-14, 2.527335733893531e-20, 3.723514785641488e18, 2.455600510957088e18),
    ("G6", "3.00", "0.34", 1266547317.6994867, 3725139169704.3726, 1.947756407967783e-15, 3.0101121615522092e-21, 3.723514785641488e18, 2.455600510957088e18),
)
E6_FIELDS = ("variant", "log10_rho", "y_s", "v_R_GeV", "S_vev_GeV", "dtheta_NDA", "dtheta_Z17", "L1_2L_pqr_x0p", "L1_3L_pqr_MPlred")
# e6 keys its Landau columns by (variant, log10 rho) only: the two D log10 rho = 2.00 roots carry the columns of the
# second root (v_R = 2.56e9).  Those two rows are excluded from the Landau-column comparison (disclosed).
E6_DUPLICATED_LANDAU_KEYS = (("D", "2.00"),)

V1_LANDAU = {  # verify-physics/v1_threeloop.json landau (LSODA, rtol 1e-11)
    "BM-DA1": {
        "PQR_x0p_1L": 1.2485783121400758e21, "PQR_x0p_2L": 3.7235147827744573e18, "PQR_x0p_3L": 2.3435195109615954e18,
        "PQR_x0p_3Lx0.5": 2.898712806666489e18, "PQR_x0p_3Lx0.75": 2.5976623370158607e18,
        "PQR_x0p_3Lx1.25": 2.1251341074260214e18,
        "PQR_MPlred_1L": 1.5457658121852444e21, "PQR_MPlred_2L": 4.142308480354427e18,
        "PQR_MPlred_3L": 2.4556005082356915e18,
        "ratio_3L_over_2L_at_MPlred": 0.319862757394462,
    },
    "D_rho1e3": {
        "PQR_x0p_1L": 5.798548609674974e21, "PQR_x0p_2L": 7.450058087919734e18, "PQR_x0p_3L": 4.690743293996769e18,
        "PQR_x0p_3Lx0.5": 5.793696223830015e18, "PQR_x0p_3Lx0.75": 5.193799920862071e18,
        "PQR_x0p_3Lx1.25": 4.2621125112056837e18,
        "PQR_MPlred_1L": 9.431745592332393e21, "PQR_MPlred_2L": 9.96587946090459e18,
        "PQR_MPlred_3L": 5.988227004739035e18,
        "ratio_3L_over_2L_at_MPlred": 0.18564456781220293,
    },
    "BM-E": {
        "PQR_x0p_1L": 1.560393803221979e21, "PQR_x0p_2L": 3.5840041848998513e18, "PQR_x0p_3L": 2.2666504569941233e18,
        "PQR_x0p_3Lx0.5": 2.794707417508143e18, "PQR_x0p_3Lx0.75": 2.5078591039359217e18,
        "PQR_x0p_3Lx1.25": 2.0604766478151299e18,
        "PQR_MPlred_1L": 2.334838186428255e21, "PQR_MPlred_2L": 4.429202065432076e18,
        "PQR_MPlred_3L": 2.5787131239924173e18,
        "ratio_3L_over_2L_at_MPlred": 0.33662127543157067,
    },
    "D_rho10^2.45": {"PQR_x0p_2L": 3.322483713889801e18, "PQR_x0p_3L": 2.1000323559397284e18,
                     "PQR_MPlred_3L": 2.331151261025014e18},
    "D_rho10^2.55": {"PQR_x0p_2L": 3.8635582868431857e18, "PQR_x0p_3L": 2.444038067384688e18,
                     "PQR_MPlred_3L": 2.831872096609818e18},
}
V1_WINDOW_KEYS = {"D_rho10^2.45": ("D", "2.45"), "D_rho10^2.55": ("D", "2.55")}
V1_BENCHMARK_KEYS = {"BM-DA1": "BM-DA1", "BM-E": "BM-E", "D_rho1e3": "D_rho1e3"}
E4_BENCHMARKS = {  # e4_so10_3loop.json benchmarks: (U1 two-loop, e4 two-loop, e4 three-loop), P,Q,R at x0 p
    ("G6", "3.00"): (3.723514785641488e18, 3.723514785641488e18, 2.343519513010022e18),
    ("D", "2.25"): (2.4313506311451597e18, 2.4313506311451597e18, 1.5220547735770148e18),
    ("D", "2.30"): (2.633315642106104e18, 2.633315642106104e18, 1.6554390825928366e18),
    ("D", "2.35"): (2.848367313966135e18, 2.848367313966135e18, 1.7954166227967537e18),
    ("D", "2.40"): (3.0776880398609393e18, 3.0776880398609393e18, 1.9432688295298148e18),
    ("D", "2.45"): (3.322483716608342e18, 3.322483716608342e18, 2.100032357827926e18),
    ("D", "2.50"): (3.5840041878552684e18, 3.5840041878552684e18, 2.2666504590672259e18),
    ("D", "2.55"): (3.863558290141352e18, 3.8635582901413796e18, 2.444038069631736e18),
    ("D", "2.60"): (4.1625259589333187e18, 4.1625259589333187e18, 2.6331156178086093e18),
    ("D", "2.65"): (4.482368724291298e18, 4.482368724291266e18, 2.8348293084580767e18),
    ("D", "2.75"): (5.190991251356957e18, 5.190991251356957e18, 3.280157983459972e18),
    ("D", "3.00"): (7.450058095353726e18, 7.450058095353779e18, 4.690743298893041e18),
    ("D", "3.25"): (1.0634037192182352e19, 1.0634037192182352e19, 6.665317481878994e18),
}
C6_LANDAU = {  # c6_landau_cost.json: (b1 above P,Q,R, b2 above P,Q,R, 2L alpha = 1 scale, 1L alpha = 1 scale)
    "baseline": ("52/3", "25013/6", 3.723514785641461e18, 1.2485783121400758e21),
    "+real 45": ("56/3", "25909/6", 3.032024813808539e18, 6.252910234716526e20),
    "+real 45 +1VL": ("64/3", "26819/6", 2.2619639221939272e18, 2.0325447013278004e20),
    "+complex 45": ("20", "8935/2", 2.517999421715391e18, 3.4339429862594406e20),
    "+second 126bar": ("29", "12211/2", 8.124031146123272e17, 2.540280990235396e19),
    "+10_F": ("18", "8409/2", 3.419776015454903e18, 8.723429534814121e20),
    "+2VL": ("68/3", "26833/6", 2.0451974284721897e18, 1.2796217071854274e20),
    "+120_H": ("80/3", "32965/6", 1.0833125258255683e18, 4.214840863878052e19),
    "+120_H +real 45": ("28", "11287/2", 9.646811334057153e17, 3.123464865258055e19),
}
C5_WITNESS_CHAIN = {  # critic c5 (v20, rho = 1e3): Route-B engine (U1 + A2 + landau120 patches)
    "without_120H": {"engine_2L_x0p": 3.723514785641488e18, "Lam_1L_x0p": 1.2485783123079814e21,
                     "Lam_2L_x0p": 3.7235147859029637e18, "Lam_3L_x0p": 2.34351951311601e18},
    "with_120H": {"engine_2L_x0p": 1.083312525825576e18, "Lam_1L_x0p": 4.214840864246476e19,
                  "Lam_2L_x0p": 1.083312525825576e18, "Lam_3L_x0p": 8.495541729483657e17},
}
C1_ROUTE_B_ROOT = {"v_R_GeV": 1266547317.6994867, "alpha_U_inv": 23.915307659746492, "M_X_GeV": 7.793732345676163e16,
                   "Lam_PQR_x0p": 3.723514785641488e18}
U2_ROOTS = {  # e5_crosscheck.json U2 (second code: PyR@TE coefficients, full one-loop thresholds, RK4)
    "BM-DA1": {"M_I_GeV": 1223911937.8488863, "M_X_GeV": 8.358521049654704e16, "alpha_U_inv": 23.78391793631131,
               "M_GUT_chart_GeV": 1.62622714179438e17},
    "BM-E": {"M_I_GeV": 5573614906.020839, "M_X_GeV": 5.3347549445514744e16, "alpha_U_inv": 25.600847851685387,
             "M_GUT_chart_GeV": 1.076841327430653e17},
    "D_rho1e3": {"M_I_GeV": 8358999666.253184, "M_X_GeV": 4.111000526121682e16, "alpha_U_inv": 29.859419311207706,
                 "M_GUT_chart_GeV": 8.961862512898546e16},
}
U2_LOG10_RHO = {"BM-DA1": "3.00", "BM-E": "2.50", "D_rho1e3": "3.00"}
EXPECTED_U2_SCALES = {  # alpha_10 = 1 scale (GeV), I2, P,Q,R at x0 p with x0/p of the U1 BM-DA1 root
    "BM-DA1": {"1L": 1.2751555957797584e21, "2L": 3.8771446394817336e18, "3L_gauge_only": 2.438437519260898e18},
    "BM-E": {"1L": 1.5994175010047622e21, "2L": 3.7349901976468557e18, "3L_gauge_only": 2.361885616635942e18},
    "D_rho1e3": {"1L": 5.979089861493778e21, "2L": 7.774690584284981e18, "3L_gauge_only": 4.896099474631718e18},
}
U2_CHART_REL = 1.0e-9
MARGINAL_BAND = 0.01  # |alpha = 1 scale / M_Pl,red - 1| below this is "marginal"
# e5_crosscheck.json U1_variants at the D remnants, rho = 1e3: scheme variants of the RG-improved root (code U1).
E5_U1_VARIANTS_RHO1E3 = {
    "base": (8560428044.594446, 3.8551068310509176e16, 29.950197955900347),
    "muR=2vR": (9652075007.854258, 3.7245162066308104e16, 30.30777692085777),
    "muG=2MX": (6037623832.902306, 4.543207053868633e16, 27.607164059645164),
    "cV=0": (8062196180.576289, 3.7171877683298024e16, 29.704820497602352),
    "pdg_inputs": (8069685333.216217, 4.0118243881162824e16, 29.748680800549256),
    "ys=0.3_2loop": (8564075508.963989, 3.854119636818767e16, 29.96806541589703),
    "gut_mass_x0.5": (31230353988.21647, 2.3699783304202676e16, 31.635477408222062),
    "gut_mass_x2": (1960997360.294188, 6.900271904278583e16, 27.59292676538894),
}
E5_VARIANT_PASSING_QUALITY = "gut_mass_x2"
E5_NDA_MS_ONLY_PASSING = ("U1:muG=2MX",)  # passes NDA with Lambda = M_s only; still fails Z17
PYRATE3_SO10_B3 = {"no_PQR": "132706057/864", "with_PQR": "109873879/864"}  # PyR@TE 3, -l [3,0,0] (Poole-Thomsen)
TWO_CODE_BOUNDS = {"v_R": 0.034, "M_X": 0.073}  # BM-DA1, relative to the U1 value
REMNANT_MASSES_OVER_VR = {
    "G6": {"(6,1)_4/3": 0.10206186761478958, "(1,1)_2": 0.10206186761478958, "(3,1)_1/3": 0.2429564214861968,
           "(6,1)_1/3": 0.25344830303475263, "(3,1)_4/3": 0.25344830303475263, "(6,1)_2/3": 0.3241288580512096},
    "D": {"(6,1)_4/3": 0.3163917896058477, "(1,1)_2": 0.3163917896058477, "(3,1)_1/3": 0.3158433479320559,
          "(6,1)_1/3": 0.40551728485560423, "(3,1)_4/3": 0.40551728485560423, "(6,1)_2/3": 0.3403353009537701},
}
J1F_PLANCK_KINETIC = {  # final/j1: delta alpha^-1 per unit c = (M_U/M_Pl,red) alpha_U^-1
    "MU=2.07e+16": {"M_U_GeV": 2.07e16, "alpha_U_inv": 27.0, "delta_aInv_per_unit_c": 0.2295277207392197},
    "MU=3.00e+16": {"M_U_GeV": 3.0e16, "alpha_U_inv": 25.0, "delta_aInv_per_unit_c": 0.3080082135523614},
    "MU=7.80e+16": {"M_U_GeV": 7.8e16, "alpha_U_inv": 23.9, "delta_aInv_per_unit_c": 0.7655852156057494},
}
U1_BETAS = {  # wfGNG/U1/betas.json (independent implementation): (b, b_ij) as exact strings
    "SM_1HDM": (("41/10", "-19/6", "-7"), (("199/50", "27/10", "44/5"), ("9/10", "35/6", "12"), ("11/10", "9/2", "-26"))),
    "SM_1HDM+all_remnants": (("53/6", "-19/6", "-25/6"), (("10477/150", "27/10", "2084/15"), ("9/10", "35/6", "12"), ("521/30", "9/2", "289/3"))),
    "SM_1HDM+all_remnants+5pairs": (("133/6", "61/6", "55/6"), (("12377/150", "87/10", "2524/15"), ("29/10", "1015/6", "52"), ("631/30", "39/2", "1049/3"))),
    "PS_witness": (("-23/3", "-3", "11/3"), (("643/6", "9/2", "153/2"), ("45/2", "8", "3"), ("765/2", "3", "584/3"))),
    "PS_witness+5pairs": (("17/3", "31/3", "17"), (("2693/6", "39/2", "183/2"), ("195/2", "514/3", "3"), ("915/2", "3", "358"))),
    "PS_spectators_only_delta": (("40/3", "40/3", "40/3"), (("1025/3", "15", "15"), ("75", "490/3", "0"), ("75", "0", "490/3"))),
    "PS_anchor_with_(15,2,2)": (("-7/3", "2", "26/3"), (("2435/6", "105/2", "249/2"), ("525/2", "73", "48"), ("1245/2", "48", "779/3"))),
    "SO10_no_spect": (("-4",), (("5911/2",),)),
    "SO10_5pairs": (("28/3",), (("22283/6",),)),
    "SO10_5pairs+PQR": (("52/3",), (("25013/6",),)),
}
U1_REMNANT_DELTA_B = {
    "(6,1)_4/3": ("32/15", "0", "5/6"),
    "(6,1)_1/3": ("2/15", "0", "5/6"),
    "(6,1)_-2/3": ("8/15", "0", "5/6"),
    "(3,1)_-1/3": ("1/15", "0", "1/6"),
    "(3,1)_-4/3": ("16/15", "0", "1/6"),
    "(1,1)_-2": ("4/5", "0", "0"),
}


def _default_research_record() -> dict[str, dict[str, Any]]:
    record = {
        "window_roots": {
            tag: _record(
                _IN,
                [dict(zip(_ROOT_FIELDS, row)) for row in rows],
                "perturbative two-loop unification roots of code U1 (one-loop MS-bar thresholds at v_R and M_X, "
                "spectators at M_s = rho v_R, P,Q,R at x0 p); inputs of every recomputed SO(10)-phase run",
                source,
                "points[].roots[] with perturbative_root = true: {vR, alpha_U_inv, mu_G, x0p}",
            )
            for tag, (source, rows) in _ROOT_FILES.items()
        },
        "remnant_masses_over_vR": _record(
            _IN,
            REMNANT_MASSES_OVER_VR,
            "remnant pole masses m/v_R of the G6 (tree) and D (RG-improved) variants",
            _E + "e2_unif_D_ys0.0_3.0.json",
            "remnant_masses_over_vR (G6 values: e2_unif_G6_ys0.0_3.0.json)",
        ),
        "u2_roots": _record(
            _REC,
            U2_ROOTS,
            "second-code (U2) roots at the same benchmarks: BM-DA1 v_R and M_X agree with U1 within 3.4% and 7.3%; the "
            "SO(10) phase is also run from them here (running.u2_roots), with x0 p from the U1 x0/p",
            _E + "e5_crosscheck.json",
            "U2.{G6_log10rho3.0, D_log10rho2.5, D_log10rho3.0}.roots[0].{M_I, M_X, alpha_inv_U, M_GUT_chart}",
        ),
        "e5_u1_scheme_variants_rho1e3": _record(
            _IN,
            {name: {"v_R_GeV": row[0], "M_X_GeV": row[1], "alpha_U_inv": row[2]} for name, row in E5_U1_VARIANTS_RHO1E3.items()},
            "code U1 scheme variants of the RG-improved rho = 1e3 root (mu_R = 2 v_R, mu_G = 2 M_X, cV = 0, PDG inputs, "
            "y_s = 0.3 in the two-loop running, GUT scalar masses x0.5 and x2); inputs of quality.scheme_variants_rho1e3",
            _E + "e5_crosscheck.json",
            "U1_variants.log10rho3.0_<variant>[0].{vR, M_X, alpha_U_inv}",
        ),
        "pyrate3_so10_b3": {
            "no_PQR": _record(
                _REC, PYRATE3_SO10_B3["no_PQR"],
                "PyR@TE 3 three-loop gauge coefficient of the SO(10) phase without P,Q,R (3 x 16 + 5 x (16 + 16bar) + "
                "real 210 + complex 126bar + complex 10; Poole-Thomsen three-loop results): equal to the PGJ value",
                "wfREC/verify-M2/pyrate_out/VSO10noPQR/PythonOutput/RGEs.py", "beta_g10, nLoop = 3 coefficient of g10**7",
            ),
            "with_PQR": _record(
                _REC, PYRATE3_SO10_B3["with_PQR"],
                "PyR@TE 3 three-loop gauge coefficient of the SO(10) phase with P,Q,R (+ bars): equal to the PGJ value",
                "wfREC/verify-M2/pyrate_out/VSO10PQR/PythonOutput/RGEs.py", "beta_g10, nLoop = 3 coefficient of g10**7",
            ),
        },
        "mss2012_pgj_agreement": _record(
            _LIT,
            {"agreement_with_PGJ_eq_33": "complete, after symmetrising two Yukawa terms and correcting one misprint "
                                         "(eqs. (28)-(30) of arXiv:1208.3357)",
             "affected_terms": "Yukawa terms only (omitted in this module)"},
            "Mihaila-Salomon-Steinhauser arXiv:1208.3357 section IV compare their three-loop gauge beta functions with "
            "PGJ eq. (33)",
            "wfREC/verify-M2/mss2012.txt",
            "section IV, eqs. (28)-(30)",
        ),
        "c1_route_b_engine_root": _record(
            _REC,
            C1_ROUTE_B_ROOT,
            "the critic's Route-B engine reproduces the U1 root bit for bit (a reproduction, not an independent code)",
            "wfRESCUE/critic/c1_f17_light1522_scan.json",
            "rows[design = v20, rho = 1000, with120 = false].roots[0]",
        ),
        "c5_witness_chain_3loop": _record(
            _REC,
            C5_WITNESS_CHAIN,
            "critic three-loop recomputation on the v20 witness chain at BM-DA1, with and without a 120_H at mu_G",
            "wfRESCUE/critic/c5_witness_chain_3loop.json",
            "[design = v20, rho = 1000]",
        ),
        "c6_landau_cost": _record(
            _REC,
            {name: {"b1_above_PQR": row[0], "b2_above_PQR": row[1], "alpha_eq_1_2L_GeV": row[2], "alpha_eq_1_1L_GeV": row[3]}
             for name, row in C6_LANDAU.items()},
            "two-loop Landau cost of each SO(10)-phase addition at BM-DA1 (root held fixed)",
            "wfRESCUE/C-other-extensions/c6_landau_cost.json",
            "<option>.{b1_above_PQR, b2_above_PQR, alpha_eq_1_scale_GeV, one_loop_alpha_eq_1_scale_GeV}",
        ),
        "v1_threeloop_landau": _record(
            _REC,
            V1_LANDAU,
            "independent verifier: alpha = 1 scales at 1L/2L/3L (b3 x 0.5, 0.75, 1.25) with P,Q,R at x0 p or M_Pl,red",
            _E + "verify-physics/v1_threeloop.json",
            "landau.<benchmark>.<PQR placement>_<loops>.alpha1",
        ),
        "v1_threeloop_coefficients": _record(
            _REC,
            {"no_PQR": list(EXPECTED_SO10_B["no_PQR"]), "with_PQR": list(EXPECTED_SO10_B["with_PQR"]),
             "SM_U1Y": list(EXPECTED_SM_B_AT_NG3["U1_Y"]), "SM_SU2L": list(EXPECTED_SM_B_AT_NG3["SU2_L"]),
             "SM_SU3C_3L": EXPECTED_SM_B_AT_NG3["SU3_C"][2]},
            "verifier's independent PGJ transcription: SO(10) b1, b2, b3 and the SM checks against MSS",
            _E + "verify-physics/v1_threeloop.json",
            "so10_coeffs, sm_checks",
        ),
        "e4_so10_3loop": _record(
            _REC,
            {"coefficients": {k: list(v) for k, v in EXPECTED_SO10_B.items()}, "qcd_b3": dict(QCD_NUMERIC_RECORD),
             "benchmarks_U1_2L_e4_2L_e4_3L": {f"{variant}_{lr}": list(values) for (variant, lr), values in E4_BENCHMARKS.items()}},
            "route E's three-loop implementation (b coefficients, QCD checks, alpha = 1 scales with P,Q,R at x0 p)",
            _E + "e4_so10_3loop.json",
            "coefficients_pqr_*, qcd_check_nf*, benchmarks.<key>.{L1_2loop_U1, 2L, 3L}.alpha1_scale",
        ),
        "e6_summary_rows": _record(
            _REC,
            [dict(zip(E6_FIELDS, row)) for row in E6_ROWS],
            "route E benchmark table: <S>, NDA and Z17 quality, and U1/e4 alpha = 1 scales (2L with P,Q,R at x0 p; "
            "3L with P,Q,R at M_Pl,red); its Landau columns are keyed by (variant, log10 rho) only",
            _E + "e6_summary.json",
            "[].{remnants, log10_rho, ys, vR, S_vev, dtheta_NDA, dtheta_Z17, L1_2L_pqr_x0p, L1_3L_pqr_MPl}",
        ),
        "j1f_planck_kinetic": _record(
            _REC,
            J1F_PLANCK_KINETIC,
            "final adjudication J1f: delta alpha_i^-1 per unit c of c Phi210 F F/M; the FINAL '0.23c' is the "
            "M_U = 2.07e16 (G3221 lead) row, not BM-DA1",
            "wfRESCUE/final/j1_adjudication_checks.json",
            "J1f_planck_kinetic",
        ),
        "u1_betas": _record(
            _REC,
            {"segments": {k: {"b": list(b), "bij": [list(r) for r in bij]} for k, (b, bij) in U1_BETAS.items()},
             "remnant_delta_b": {k: list(v) for k, v in U1_REMNANT_DELTA_B.items()}},
            "exact MV coefficients of every chain segment of code U1 (independent implementation)",
            "wfGNG/U1/betas.json",
            "<segment>.{b, bij}, remnant_delta_b",
        ),
        "u1_chain_content": _record(
            _REC,
            {"remnants": [name for name, _y, _r in REMNANTS], "spectators": "5 x (16 + 16bar) at M_s = rho v_R",
             "PS_witness": "3 x [(4,2,1) + (4bar,1,2)] + complex (1,2,2) + complex (10bar,1,3)"},
            "segment content of code U1 (SM + remnants below v_R, PS witness above, spectators above M_s)",
            "wfGNG/U1/rge.py",
            "sm_segment, ps_segment, remnant_fields, spectators_sm, spectators_ps",
        ),
        "verify_feasibility_quotes": _record(
            _REC,
            {
                "three_to_two_loop_term_ratio_quote": "about 0.23-0.32 at M_Pl,red",
                "e2_quality_flags_hard_coded_for_rho_1e3": True,
                "d_best_multipliers": [3.53, 3.74, 1.48, 1.81, 1.82, 1.21],
                "nda_window_d_best": "about [2.39, 2.45]",
                "z17_window_d_best": "about [2.5, 2.68]",
                "x0p_near_planckian": "pushing P,Q,R to >= M_Pl,red puts U(1)_X breaking at the cutoff",
            },
            "route E feasibility verifier (quotes; the module states its own computed values)",
            _E + "VERIFY_feasibility.md",
            "Corrections A-C, section 4",
        ),
        "mss_eq5": _record(
            _LIT,
            {group: [list(poly) for poly in polys] for group, polys in MSS_EQ5.items()},
            "Mihaila-Salomon-Steinhauser eq. (5): pure (alpha_i/pi)^(n+1) coefficients as polynomials in n_G "
            "(x 4, 16, 64 = b1, b2, b3)",
            _E + "verify-physics/mss.txt",
            "eq. (5)",
        ),
        "pgj_eqs_28_33": _record(
            _LIT,
            {name: str(value) for name, value in PGJ_COEFFICIENTS.items()},
            "Pickering-Gracey-Jones three-loop gauge beta function of a general single-group theory (gauge + "
            "matter terms), Phys. Lett. B510 (2001) 347, transcribed from arXiv hep-ph/0104247v1; errata Phys. Lett. "
            "B512 (2001) 230 and B535 (2002) 377 (the corrections reported by MSS arXiv:1208.3357 concern Yukawa terms, "
            "which are omitted here); the QCD check fixes every fermion term, while the MSS n_G-polynomial check fixes "
            "4 linear combinations of the 8 scalar coefficients (coefficients.mss_eq5.scalar_coefficient_constraints); both SO(10) b3 "
            "values are reproduced by PyR@TE 3 (pyrate3_so10_b3)",
            _E + "verify-physics/pgj.txt",
            "eqs. (28)-(33)",
        ),
    }
    return record


RESEARCH_RECORD = _default_research_record()

NEVER_TRUE_FLAGS = (
    "G7_closed",
    "gate_status_changed",
    "wired_into_gate_ledger",
    "report_closes_G7_by_itself",
    "benchmark_adopted",
    "three_loop_includes_yukawa_quartic",
    "planck_kinetic_term_computed",
    "G6_closed_assumed_true",
)
PHYSICS_FLAGS = (
    "bm_da1_two_loop_pass_both_roots",
    "bm_da1_three_loop_fail_on_U1_root",
    "bm_da1_three_loop_marginal_pass_on_U2_root",
    "bm_da1_rg_improved_quality_fail_conditional",
    "bm_e_three_loop_fail_both_roots",
    "integrators_agree",
)
DERIVED_FLAGS = ("evidence_recorded", *PHYSICS_FLAGS)

SCOPE = {
    "claimed": [
        "EXACT: SO(10) representation data from the Weyl dimension formula; the PGJ single-group b1, b2, b3 of the "
        "SO(10) phase with and without P,Q,R (gauge + matter terms); PGJ = QCD with general Casimirs and = MSS eq. (5) "
        "as polynomials in n_G for U(1)_Y, SU(2)_L, SU(3)_C; b1, b2 = the repository's Machacek-Vaughn routine; every "
        "chain segment of code U1 re-derived as exact Fractions",
        "NUM: alpha_10 = 1 scales at 1L, 2L and 3L_gauge_only from the research-recorded roots of codes U1 and U2 with "
        "two integrators (<= 1e-6 agreement); BM-DA1 passes the reduced-Planck Landau criterion at two loops on both "
        "roots; at three loops (gauge-only) it fails on the U1 root (-3.8%) and passes marginally on the U2 root "
        "(+0.14%), so its three-loop outcome lies within the two-code root uncertainty; BM-E passes at two loops and "
        "fails at three loops on both roots",
        "NUM: every analysed SO(10)-phase addition at mu_G fails at three loops at BM-DA1 (root held fixed: a lower "
        "bound on the damage); a 120_H, a second 126bar and vectorlike pairs fail already at two loops",
        "NUM: axion quality (NDA with Lambda = <S> and with Lambda = M_s, Z17-EFT) at every recorded root; BM-DA1 with "
        "the G6 masses passes",
        "NUM, CONDITIONAL: the rho = 1e3 root with the RG-improved remnant masses (anti-SOS region points, committed GUT "
        "scalar spectrum) fails both bounds; the GUT scalar masses x2 scheme variant removes the failure, U2 and the "
        "other six scheme variants keep the Z17 failure",
        "NUM, CONDITIONAL: the rho windows of the recorded scan",
    ],
    "not_claimed": [
        "the two-loop unification roots are research-recorded (codes U1 and U2; one-loop MS-bar thresholds at v_R "
        "and M_X), not re-derived here",
        "the SO(10)-phase running is gauge + matter only at every order: the two-loop Yukawa terms (16.16.10_H, "
        "16.16.126bar_H, y_s S 16_s 16bar_s) and the three-loop Yukawa and quartic terms are omitted; the Yukawa terms "
        "enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 scale, so their omission is not "
        "conservative for a fail statement",
        "the 3L_gauge_only SO(10) segment sits on a two-loop root with one-loop thresholds: the unknown two-loop GUT "
        "thresholds are of the same formal order as the three-loop term, so the BM-DA1 three-loop margins (-3.8% on the "
        "U1 root, +0.14% on the U2 root) are below the neglected effects",
        "U(1)_X feedback on the SO(10) running is neglected; the SO(10) phase is a single coupling",
        "the GUT-scale thresholds are uncontrolled: BM-DA1 uses the committed spectrum, whose normalisation is "
        "non-perturbative (a0 ~ 21.6, g3_sm_pati_salam_witness_unitarity_v20); on the perturbative x1/50 member every "
        "scalar tree mass (the six remnants below v_R and the GUT scalars) scales by 1/sqrt50 and the root, Landau and "
        "quality numbers are not recomputed here; the GUT scalar masses x0.5 and x2 scheme variants alone move the "
        "rho = 1e3 root from v_R = 3.1e10 to 1.96e9 GeV (a factor 16; the rescue synthesis quotes up to x30)",
        "the Planck gauge-kinetic term c Phi210 F F/M is not computed (EST only); it moves the alpha = 1 scale by "
        "more than the three-loop margins (-3.8% on the U1 root, +0.14% on the U2 root), so the three-loop verdict is "
        "convention- and threshold-limited",
        "the RG-improved remnant masses come from anti-SOS region points: G6 is not closed and is not assumed closed",
        "no benchmark is adopted; the windows are conditional evidence, not a G7 closure",
        "no gate status changes; nothing is wired into the gate ledger; G7 stays BLOCKED",
    ],
}

# ---------------------------------------------------------------------------------------------------------------------
# Small helpers.
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
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value)))


def _rel(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs(a / b - 1.0)


def _close(a: float | None, b: float | None, rel: float) -> bool:
    d = _rel(a, b)
    return d is not None and d <= rel


def _strs(values: Sequence[Any]) -> list[str]:
    return [str(value) for value in values]


def _sym(value: Any) -> Any:
    if isinstance(value, Fraction):
        return sympy.Rational(value.numerator, value.denominator)
    if isinstance(value, int):
        return sympy.Integer(value)
    return value


_MONOMIAL_TOKEN = re.compile(r"^(CG|TR|TS|CR2|CS2|CR3|CS3)(?:\^(\d+))?$")


def _monomial(expression: str, invariants: Mapping[str, Any]) -> Any:
    value: Any = 1
    for token in expression.split("*"):
        match = _MONOMIAL_TOKEN.match(token)
        if match is None:
            raise ValueError(f"bad PGJ monomial {expression!r}")
        value = value * invariants[match.group(1)] ** int(match.group(2) or 1)
    return value


def pgj_b(invariants: Mapping[str, Any], table: Mapping[str, Fraction] | None = None) -> tuple[Any, Any, Any]:
    """(b1, b2, b3) of dg/dt = b1 g^3/(16pi^2) + b2 g^5/(16pi^2)^2 + b3 g^7/(16pi^2)^3 (PGJ eqs. (28)-(33))."""
    table = PGJ_COEFFICIENTS if table is None else table
    symbolic = any(isinstance(value, sympy.Basic) for value in invariants.values())
    inv = {name: (_sym(value) if symbolic else value) for name, value in invariants.items()}
    sums: dict[str, Any] = {"a1": 0, "b1": 0, "c1": 0}
    for key, coefficient in table.items():
        order, expression = key.split(".", 1)
        c = _sym(coefficient) if symbolic else coefficient
        sums[order] = sums[order] + c * _monomial(expression, inv)
    b = (-sums["a1"], -2 * sums["b1"], -3 * sums["c1"])
    if symbolic:
        return tuple(sympy.expand(x) for x in b)
    return tuple(F(x) for x in b)


def so10_rep_data() -> dict[str, dict[str, Any]]:
    """dim, T and C2 of SO(10) irreps from the Weyl dimension formula and C2 = (L, L + 2 rho), C2(10) = 9/2."""
    positive = []
    for i in range(5):
        for j in range(i + 1, 5):
            for sign in (1, -1):
                root = [0] * 5
                root[i], root[j] = 1, sign
                positive.append(root)
    raw: dict[str, tuple[int, Fraction]] = {}
    for name, weight in SO10_HIGHEST_WEIGHTS.items():
        lam = [F(x) for x in weight]
        numerator = denominator = F(1)
        for root in positive:
            numerator *= sum((lam[k] + SO10_RHO[k]) * root[k] for k in range(5))
            denominator *= sum(SO10_RHO[k] * root[k] for k in range(5))
        dim = numerator / denominator
        if dim.denominator != 1:
            raise ArithmeticError(f"non-integer dimension for {name}")
        raw[name] = (int(dim), sum(lam[k] * (lam[k] + 2 * SO10_RHO[k]) for k in range(5)))
    norm = F(9, 2) / raw["10"][1]
    data = {}
    for name, (dim, c2raw) in raw.items():
        c2 = c2raw * norm
        data[name] = {"dim": dim, "C2": c2, "T": c2 * dim / SO10_DIM_G}
    return data


def content_invariants(content: Sequence[tuple[str, str, Any]], reps: Mapping[str, Mapping[str, Any]], cg: Any = F(8)) -> dict[str, Any]:
    inv = {"CG": cg, "TR": F(0), "TS": F(0), "CR2": F(0), "CS2": F(0), "CR3": F(0), "CS3": F(0)}
    for rep, kind, mult in content:
        t, c = reps[rep]["T"], reps[rep]["C2"]
        m = F(mult)
        if kind == "weyl":
            inv["TR"] += m * t
            inv["CR2"] += m * t * c
            inv["CR3"] += m * t * c * c
        elif kind in ("real", "cplx"):
            n = m * (2 if kind == "cplx" else 1)
            inv["TS"] += n * t
            inv["CS2"] += n * t * c
            inv["CS3"] += n * t * c * c
        else:
            raise ValueError(f"unknown field kind {kind!r}")
    return inv


def mv_single_group(content: Sequence[tuple[str, str, Any]], reps: Mapping[str, Mapping[str, Any]]) -> tuple[Fraction, Fraction]:
    """b1, b2 of the SO(10) phase through two_loop_thresholds_v20.mv_gauge_coefficients (real = complex x 1/2)."""
    fields = []
    for rep, kind, mult in content:
        data = (reps[rep]["dim"], reps[rep]["T"], reps[rep]["C2"])
        if kind == "weyl":
            fields.append((f"{rep} Weyl", "weyl", (data,), F(mult)))
        elif kind == "cplx":
            fields.append((f"{rep} complex", "cplx", (data,), F(mult)))
        else:
            fields.append((f"{rep} real", "cplx", (data,), F(mult) / 2))
    b, bij = two_loop.mv_gauge_coefficients((F(8),), tuple(fields))
    return b[0], bij[0][0]


# ---------------------------------------------------------------------------------------------------------------------
# (B) Integrators.
# ---------------------------------------------------------------------------------------------------------------------


def _segments(mu_g: float, m_pqr: float, b_lo: Sequence[Fraction], b_hi: Sequence[Fraction]) -> tuple[tuple[float, float, tuple[Fraction, ...]], ...]:
    t_g, t_p = math.log(mu_g), math.log(m_pqr)
    if t_p > t_g:
        return ((t_g, t_p, tuple(b_lo)), (t_p, LOG_T_END, tuple(b_hi)))
    return ((t_g, LOG_T_END, tuple(b_hi)),)


def _rates(b: Sequence[Fraction], f2: float, f3: float) -> tuple[float, float, float]:
    b1, b2, b3 = (float(x) for x in b)
    return -b1 / (2.0 * PI), -f2 * b2 / (8.0 * PI**2), -f3 * b3 / (32.0 * PI**3)


def alpha_one_rk4(alpha_inv: float, segments: Sequence[tuple[float, float, Sequence[Fraction]]], f2: float, f3: float,
                  h_max: float = RK4_STEP) -> float | None:
    """I1: fixed-step RK4 in t with the alpha = 1 crossing located by bisection on the last step."""
    y = float(alpha_inv)
    for t_a, t_b, b in segments:
        c1, c2, c3 = _rates(b, f2, f3)

        def f(value: float) -> float:
            a = 1.0 / value
            return c1 + a * (c2 + c3 * a)

        n = max(1, math.ceil((t_b - t_a) / h_max))
        h = (t_b - t_a) / n
        for k in range(n):
            t = t_a + k * h
            k1 = f(y)
            k2 = f(y + 0.5 * h * k1)
            k3 = f(y + 0.5 * h * k2)
            k4 = f(y + h * k3)
            y_new = y + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            if y_new <= 1.0:
                lo, hi = 0.0, h
                for _ in range(RK4_BISECTIONS):
                    mid = 0.5 * (lo + hi)
                    m1 = f(y)
                    m2 = f(y + 0.5 * mid * m1)
                    m3 = f(y + 0.5 * mid * m2)
                    m4 = f(y + mid * m3)
                    if y + mid / 6.0 * (m1 + 2.0 * m2 + 2.0 * m3 + m4) <= 1.0:
                        hi = mid
                    else:
                        lo = mid
                return math.exp(t + 0.5 * (lo + hi))
            y = y_new
    return None


def _dop853(y0: float, t_a: float, t_b: float, rates: tuple[float, float, float], event: bool) -> Any:
    c1, c2, c3 = rates

    def rhs(_t: float, yy: Any) -> list[float]:
        a = 1.0 / yy[0]
        return [c1 + a * (c2 + c3 * a)]

    def crossing(_t: float, yy: Any) -> float:
        return yy[0] - 1.0

    crossing.terminal = True  # type: ignore[attr-defined]
    crossing.direction = -1  # type: ignore[attr-defined]
    return solve_ivp(rhs, (t_a, t_b), [y0], method="DOP853", rtol=DOP853_TOL, atol=DOP853_TOL,
                     events=crossing if event else None)


def alpha_one_dop853(alpha_inv: float, segments: Sequence[tuple[float, float, Sequence[Fraction]]], f2: float, f3: float) -> float | None:
    """I2: scipy DOP853 (rtol = atol = 1e-12) with a terminal alpha = 1 event."""
    y = float(alpha_inv)
    for t_a, t_b, b in segments:
        solution = _dop853(y, t_a, t_b, _rates(b, f2, f3), True)
        if len(solution.t_events[0]):
            return math.exp(float(solution.t_events[0][0]))
        y = float(solution.y[0, -1])
    return None


def alpha_inv_at(alpha_inv: float, segments: Sequence[tuple[float, float, Sequence[Fraction]]], f2: float, f3: float,
                 mu: float) -> float | None:
    """alpha^-1(mu) along the trajectory (I2); None when alpha = 1 is reached below mu."""
    y = float(alpha_inv)
    t_target = math.log(mu)
    for t_a, t_b, b in segments:
        if t_a >= t_target:
            break
        end = min(t_b, t_target)
        solution = _dop853(y, t_a, end, _rates(b, f2, f3), True)
        if len(solution.t_events[0]):
            return None
        y = float(solution.y[0, -1])
    return y


class Runner:
    """Runs both integrators and keeps every (I1, I2) pair for the agreement check."""

    def __init__(self, *, three_loop_factor: float = 1.0, rk4_step: float = RK4_STEP) -> None:
        self.three_loop_factor = float(three_loop_factor)
        self.rk4_step = float(rk4_step)
        self.pairs: list[tuple[str, float | None, float | None]] = []

    def factors(self, label: str) -> tuple[float, float]:
        return {"1L": (0.0, 0.0), "2L": (1.0, 0.0), "3L_gauge_only": (1.0, self.three_loop_factor)}[label]

    def scale(self, context: str, alpha_inv: float, segments: Any, f2: float, f3: float) -> dict[str, Any]:
        i1 = alpha_one_rk4(alpha_inv, segments, f2, f3, self.rk4_step)
        i2 = alpha_one_dop853(alpha_inv, segments, f2, f3)
        self.pairs.append((context, i1, i2))
        return {"I1": i1, "I2": i2, "rel_I1_I2": _rel(i1, i2)}

    def loops(self, context: str, root: Mapping[str, Any], m_pqr: float, b_lo: Any, b_hi: Any,
              labels: Sequence[str] = LOOP_LABELS) -> dict[str, dict[str, Any]]:
        segments = _segments(root["mu_G_GeV"], m_pqr, b_lo, b_hi)
        return {label: self.scale(f"{context}:{label}", root["alpha_U_inv"], segments, *self.factors(label)) for label in labels}

    def max_disagreement(self) -> tuple[float | None, int, list[str]]:
        worst = 0.0
        missing = []
        for context, i1, i2 in self.pairs:
            if (i1 is None) != (i2 is None):
                missing.append(context)
                continue
            if i1 is not None:
                worst = max(worst, abs(i1 / i2 - 1.0))
        return worst, len(self.pairs), missing


def _i2(entry: Mapping[str, Any]) -> float | None:
    return entry["I2"]


# ---------------------------------------------------------------------------------------------------------------------
# (A) coefficients.
# ---------------------------------------------------------------------------------------------------------------------


def _used_reps(computed: Mapping[str, Mapping[str, Any]], overrides: Mapping[str, Mapping[str, Any]] | None) -> dict[str, dict[str, Any]]:
    reps = {name: dict(data) for name, data in computed.items()}
    for name, changes in (overrides or {}).items():
        reps[name].update({key: (F(value) if key != "dim" else int(value)) for key, value in changes.items()})
    return reps


def _qcd_check(table: Mapping[str, Fraction]) -> dict[str, Any]:
    ca, cf, tf, nf = sympy.symbols("C_A C_F T_F n_f")
    tr = 2 * tf * nf
    b = pgj_b({"CG": ca, "TR": tr, "TS": sympy.Integer(0), "CR2": tr * cf, "CS2": sympy.Integer(0),
               "CR3": tr * cf**2, "CS3": sympy.Integer(0)}, table)
    beta0 = sympy.Rational(11, 3) * ca - sympy.Rational(4, 3) * tf * nf
    beta1 = sympy.Rational(34, 3) * ca**2 - 4 * cf * tf * nf - sympy.Rational(20, 3) * ca * tf * nf
    beta2 = (sympy.Rational(2857, 54) * ca**3 + 2 * cf**2 * tf * nf - sympy.Rational(205, 9) * cf * ca * tf * nf
             - sympy.Rational(1415, 27) * ca**2 * tf * nf + sympy.Rational(44, 9) * cf * tf**2 * nf**2
             + sympy.Rational(158, 27) * ca * tf**2 * nf**2)
    residuals = [sympy.expand(b[0] + beta0), sympy.expand(b[1] + beta1), sympy.expand(b[2] + beta2)]
    numeric = {}
    for flavours in (5, 6):
        t = F(1, 2)
        trn = 2 * flavours * t
        bn = pgj_b({"CG": F(3), "TR": trn, "TS": F(0), "CR2": trn * F(4, 3), "CS2": F(0), "CR3": trn * F(16, 9),
                    "CS3": F(0)}, table)
        numeric[str(flavours)] = str(bn[2])
    return {
        "residuals_b_plus_beta_1L_2L_3L": [str(r) for r in residuals],
        "numeric_b3": numeric,
        "numeric_b3_record": dict(QCD_NUMERIC_RECORD),
        "literature": dict(QCD_BETA_LITERATURE),
        "passes": all(r == 0 for r in residuals) and numeric == QCD_NUMERIC_RECORD,
    }


def _mss_check(table: Mapping[str, Fraction]) -> dict[str, Any]:
    ng = sympy.Symbol("n_G")
    q2 = lambda y: F(3, 5) * y * y  # noqa: E731
    hyper = ((F(1, 6), 6), (F(-2, 3), 3), (F(1, 3), 3), (F(-1, 2), 2), (F(1), 1))  # Weyl components per family
    t2, c2 = F(1, 2), F(3, 4)
    t3, c3 = F(1, 2), F(4, 3)
    qh = q2(F(1, 2))
    invariants = {
        "U1_Y": {"CG": 0, "TR": ng * sympy.Rational(*_nd(sum(m * q2(y) for y, m in hyper))),
                 "TS": 4 * qh, "CR2": ng * sympy.Rational(*_nd(sum(m * q2(y) ** 2 for y, m in hyper))),
                 "CS2": 4 * qh**2, "CR3": ng * sympy.Rational(*_nd(sum(m * q2(y) ** 3 for y, m in hyper))),
                 "CS3": 4 * qh**3},
        "SU2_L": {"CG": 2, "TR": 4 * ng * _sym(t2), "TS": 2 * t2, "CR2": 4 * ng * _sym(t2 * c2), "CS2": 2 * t2 * c2,
                  "CR3": 4 * ng * _sym(t2 * c2 * c2), "CS3": 2 * t2 * c2 * c2},
        "SU3_C": {"CG": 3, "TR": 4 * ng * _sym(t3), "TS": 0, "CR2": 4 * ng * _sym(t3 * c3), "CS2": 0,
                  "CR3": 4 * ng * _sym(t3 * c3 * c3), "CS3": 0},
    }
    out: dict[str, Any] = {"residuals": {}, "values_at_nG_3": {}}
    ok = True
    for group, inv in invariants.items():
        b = pgj_b({k: _sym(v) if not isinstance(v, sympy.Basic) else v for k, v in inv.items()}, table)
        residuals = []
        for loop, poly in enumerate(MSS_EQ5[group]):
            target = MSS_LOOP_FACTORS[loop] * sum(sympy.Rational(*_nd(F(c))) * ng**k for k, c in enumerate(poly))
            residuals.append(sympy.expand(b[loop] - target))
        out["residuals"][group] = [str(r) for r in residuals]
        out["values_at_nG_3"][group] = [str(sympy.Rational(x.subs(ng, 3))) for x in b]
        ok = ok and all(r == 0 for r in residuals)
    out["polynomials_agree"] = ok
    out["values_at_nG_3_pinned"] = out["values_at_nG_3"] == {g: list(v) for g, v in EXPECTED_SM_B_AT_NG3.items()}
    out["scalar_coefficient_constraints"] = _mss_scalar_constraints(invariants, table)
    return out


def _mss_scalar_constraints(invariants: Mapping[str, Mapping[str, Any]], table: Mapping[str, Fraction]) -> dict[str, Any]:
    """How many linear combinations of the eight PGJ scalar three-loop coefficients the MSS n_G check fixes (exact)."""
    ng = sympy.Symbol("n_G")
    scalar_keys = [key for key in table if key.startswith("c1.") and ("TS" in key or "CS" in key)]
    unknowns = {key: sympy.Symbol(f"u{index}") for index, key in enumerate(scalar_keys)}
    equations = []
    for group, inv in invariants.items():
        if group not in ("U1_Y", "SU2_L"):  # SU(3)_C carries no scalar in the SM
            continue
        inv_sym = {k: _sym(v) if not isinstance(v, sympy.Basic) else v for k, v in inv.items()}
        c1 = 0
        for key, coefficient in table.items():
            order, expression = key.split(".", 1)
            if order == "c1":
                c1 = c1 + (unknowns[key] if key in unknowns else _sym(coefficient)) * _monomial(expression, inv_sym)
        target = MSS_LOOP_FACTORS[2] * sum(sympy.Rational(*_nd(F(c))) * ng**k for k, c in enumerate(MSS_EQ5[group][2]))
        poly = sympy.Poly(sympy.expand(-3 * c1 - target), ng)
        equations += [coefficient for coefficient in poly.all_coeffs() if coefficient != 0]
    matrix = sympy.Matrix([[sympy.diff(eq, symbol) for symbol in unknowns.values()] for eq in equations])
    return {
        "n_scalar_coefficients": len(scalar_keys),
        "scalar_coefficients": scalar_keys,
        "n_equations": len(equations),
        "rank_fixed_by_MSS": int(matrix.rank()) if equations else 0,
        "meaning": "the MSS polynomial check fixes only this many linear combinations of the scalar coefficients; the "
                   "SO(10) b3 is scalar-dominated (210, 126bar), so its values are cross-checked with PyR@TE 3",
    }


def _nd(value: Fraction) -> tuple[int, int]:
    value = F(value)
    return value.numerator, value.denominator


def _sm_remnant_fields() -> tuple[tuple[str, str, tuple, int], ...]:
    return tuple(
        (name, "cplx", (two_loop.u1_rep(y), two_loop.SU2_REPS["1"], SU3_LOCAL[su3]), 1) for name, y, su3 in REMNANTS
    )


def _sm_spectator_fields(pairs: int) -> tuple[tuple[str, str, tuple, int], ...]:
    n = 2 * pairs
    return tuple((f"{name} spectators x{n}", "weyl", reps, n) for name, kind, reps, _m in two_loop.sm_fields(0) if kind == "weyl")


def _ps_witness_fields() -> tuple[tuple[str, str, tuple, int], ...]:
    return tuple(field for field in two_loop.FIELDS_PS_ANCHOR if not field[0].startswith("(15,2,2)"))


def _mv_strings(b: Sequence[Fraction], bij: Sequence[Sequence[Fraction]]) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    return tuple(str(x) for x in b), tuple(tuple(str(x) for x in row) for row in bij)


def chain_segments(reps: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Every U1 chain segment as exact MV (b, b_ij) strings, from two_loop_thresholds_v20 field tables."""
    mv = two_loop.mv_gauge_coefficients
    sm_c2, ps_c2 = two_loop.SM_GROUP_C2, two_loop.PS_GROUP_C2
    sm = two_loop.FIELDS_SM_1HDM
    remnants = _sm_remnant_fields()
    ps_witness = _ps_witness_fields()
    segments = {
        "SM_1HDM": _mv_strings(*mv(sm_c2, sm)),
        "SM_1HDM+all_remnants": _mv_strings(*mv(sm_c2, sm + remnants)),
        "SM_1HDM+all_remnants+5pairs": _mv_strings(*mv(sm_c2, sm + remnants + _sm_spectator_fields(5))),
        "PS_witness": _mv_strings(*mv(ps_c2, ps_witness)),
        "PS_witness+5pairs": _mv_strings(*mv(ps_c2, ps_witness + two_loop.ps_spectator_fields(5))),
        "PS_anchor_with_(15,2,2)": _mv_strings(*mv(ps_c2, two_loop.FIELDS_PS_ANCHOR)),
    }
    plain, plus = mv(ps_c2, ps_witness), mv(ps_c2, ps_witness + two_loop.ps_spectator_fields(5))
    segments["PS_spectators_only_delta"] = _mv_strings(
        [plus[0][i] - plain[0][i] for i in range(3)], [[plus[1][i][j] - plain[1][i][j] for j in range(3)] for i in range(3)]
    )
    for name, content in (("SO10_no_spect", SO10_NO_SPECTATOR_CONTENT), ("SO10_5pairs", SO10_BASE_CONTENT),
                          ("SO10_5pairs+PQR", SO10_BASE_CONTENT + SO10_PQR_CONTENT)):
        b1, b2 = mv_single_group(content, reps)
        segments[name] = ((str(b1),), ((str(b2),),))
    remnant_delta = {}
    for field in remnants:
        rows = two_loop.mv_field_contributions(sm_c2, (field,))
        remnant_delta[field[0]] = tuple(str(x) for x in rows[1][1])
    return {"segments": segments, "remnant_delta_b": remnant_delta}


def _su3_tables_consistent() -> bool:
    return all(t * 8 == c2 * dim for dim, t, c2 in SU3_LOCAL.values())


def coefficients_section(*, pgj_table: Mapping[str, Fraction] | None = None,
                         rep_overrides: Mapping[str, Mapping[str, Any]] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    table = dict(PGJ_COEFFICIENTS if pgj_table is None else pgj_table)
    computed = so10_rep_data()
    reps = _used_reps(computed, rep_overrides)
    rep_strings = {name: (data["dim"], str(data["T"]), str(data["C2"])) for name, data in reps.items()}
    computed_strings = {name: (data["dim"], str(data["T"]), str(data["C2"])) for name, data in computed.items()}
    qcd = _qcd_check(table)
    mss = _mss_check(table)
    b_no = pgj_b(content_invariants(SO10_BASE_CONTENT, reps), table)
    b_with = pgj_b(content_invariants(SO10_BASE_CONTENT + SO10_PQR_CONTENT, reps), table)
    mv_no = mv_single_group(SO10_BASE_CONTENT, reps)
    mv_with = mv_single_group(SO10_BASE_CONTENT + SO10_PQR_CONTENT, reps)
    option_b: dict[str, Any] = {}
    mv_options_agree = True
    for key, _name, extra in LANDAU_OPTIONS:
        lo = pgj_b(content_invariants(SO10_BASE_CONTENT + extra, reps), table)
        hi = pgj_b(content_invariants(SO10_BASE_CONTENT + SO10_PQR_CONTENT + extra, reps), table)
        option_b[key] = (tuple(str(x) for x in lo), tuple(str(x) for x in hi))
        mv_options_agree = mv_options_agree and mv_single_group(SO10_BASE_CONTENT + extra, reps) == lo[:2] and (
            mv_single_group(SO10_BASE_CONTENT + SO10_PQR_CONTENT + extra, reps) == hi[:2]
        )
    provenance = two_loop.coefficient_provenance()
    chain = chain_segments(reps)
    c6_hi = {key: tuple(C6_LANDAU[key][:2]) for key in C6_LANDAU}
    checks = {
        "so10_rep_data_from_weyl_formula": computed_strings == EXPECTED_SO10_REPS and rep_strings == computed_strings,
        "so10_index_casimir_relation": all(
            data["T"] * SO10_DIM_G == data["C2"] * data["dim"] for data in reps.values()
        ) and reps["10"]["T"] == 1 and reps["45"]["C2"] == 8 and reps["45"]["dim"] == SO10_DIM_G
        and all(reps[a]["T"] == reps[b]["T"] and reps[a]["C2"] == reps[b]["C2"] for a, b in (("16", "16bar"), ("126", "126bar"))),
        "pgj_reproduces_qcd_general_casimirs": bool(qcd["passes"]),
        "pgj_matches_mss_as_nG_polynomials": bool(mss["polynomials_agree"]),
        "pgj_mss_values_at_nG_3": bool(mss["values_at_nG_3_pinned"]),
        "so10_phase_coefficients_pinned": (tuple(str(x) for x in b_no) == EXPECTED_SO10_B["no_PQR"]
                                           and tuple(str(x) for x in b_with) == EXPECTED_SO10_B["with_PQR"]
                                           and str(b_no[2]) == PYRATE3_SO10_B3["no_PQR"]
                                           and str(b_with[2]) == PYRATE3_SO10_B3["with_PQR"]),
        "mv_two_loop_reproduces_pgj_b1_b2": mv_no == b_no[:2] and mv_with == b_with[:2] and mv_options_agree,
        "two_loop_module_provenance": bool(provenance["SM_1HDM_matches_literature"] and provenance["recomputed_from_field_content"]),
        "chain_segments_match_u1_record": all(chain["segments"][k] == U1_BETAS[k] for k in U1_BETAS if not k.startswith("SO10"))
        and _su3_tables_consistent(),
        "remnant_delta_b_match_u1_record": chain["remnant_delta_b"] == U1_REMNANT_DELTA_B,
        "so10_segments_match_u1_record": all(chain["segments"][k] == U1_BETAS[k] for k in U1_BETAS if k.startswith("SO10")),
        "landau_option_coefficients_exact": option_b == EXPECTED_OPTION_B
        and all(option_b[key][1][:2] == c6_hi[key] for key in c6_hi),
    }
    section = {
        "label": "EXACT",
        "convention": CONVENTION,
        "pgj_formula": {"source": "Pickering, Gracey, Jones, hep-ph/0104247 eqs. (28)-(33) (LIT)",
                        "coefficients": {k: str(v) for k, v in table.items()},
                        "omitted": "Yukawa and quartic contributions to the three-loop gauge beta function"},
        "so10_reps": {name: {"dim": d, "T": t, "C2": c} for name, (d, t, c) in rep_strings.items()},
        "so10_reps_from_weyl_formula": {name: {"dim": d, "T": t, "C2": c} for name, (d, t, c) in computed_strings.items()},
        "so10_phase_b": {"no_PQR": _strs(b_no), "with_PQR": _strs(b_with),
                         "pyrate3_b3_RESEARCH_RECORD": dict(PYRATE3_SO10_B3),
                         "content_no_PQR": [list(x) for x in SO10_BASE_CONTENT],
                         "content_PQR_added": [list(x) for x in SO10_PQR_CONTENT]},
        "mv_cross_check": {"no_PQR": _strs(mv_no), "with_PQR": _strs(mv_with),
                           "routine": "two_loop_thresholds_v20.mv_gauge_coefficients((8,), fields), 210 real = complex x 1/2"},
        "qcd_general_casimirs": qcd,
        "mss_eq5": mss,
        "two_loop_module_provenance": {"SM_1HDM_matches_literature": provenance["SM_1HDM_matches_literature"],
                                       "recomputed_from_field_content": provenance["recomputed_from_field_content"]},
        "chain_segments": {k: {"b": list(v[0]), "bij": [list(r) for r in v[1]]} for k, v in chain["segments"].items()},
        "remnant_delta_b": {k: list(v) for k, v in chain["remnant_delta_b"].items()},
        "landau_options_b": {k: {"below_PQR": list(v[0]), "above_PQR": list(v[1])} for k, v in option_b.items()},
        "checks": checks,
    }
    context = {"reps": reps, "b_no": b_no, "b_with": b_with, "option_b": {k: (tuple(F(x) for x in v[0]), tuple(F(x) for x in v[1])) for k, v in option_b.items()}}
    return section, context


# ---------------------------------------------------------------------------------------------------------------------
# Roots.
# ---------------------------------------------------------------------------------------------------------------------


def _find_roots(roots: Sequence[Mapping[str, Any]], variant: str, lr: str) -> list[Mapping[str, Any]]:
    return [row for row in roots if row["variant"] == variant and row["log10_rho"] == lr]


def _benchmark_root(roots: Sequence[Mapping[str, Any]], name: str) -> Mapping[str, Any]:
    variant, lr = BENCHMARKS[name]
    rows = _find_roots(roots, variant, lr)
    if len(rows) != 1:
        raise ValueError(f"benchmark {name} needs exactly one root, found {len(rows)}")
    return rows[0]


# ---------------------------------------------------------------------------------------------------------------------
# (B) running.
# ---------------------------------------------------------------------------------------------------------------------


def _pqr_scale(root: Mapping[str, Any], placement: str) -> float:
    return root["x0p_GeV"] if placement == "PQR_at_x0p" else max(root["x0p_GeV"], M_PL_RED)


def chart_scale(alpha_inv: float, m_x: float) -> float:
    """p = sqrt2 M_X/g_U (the GUT chart scale of the research codes), g_U = sqrt(4 pi/alpha_U^-1)."""
    return math.sqrt(2.0) * m_x / math.sqrt(4.0 * PI / alpha_inv)


def x0_over_p(root: Mapping[str, Any]) -> float:
    return root["x0p_GeV"] / chart_scale(root["alpha_U_inv"], root["mu_G_GeV"])


def derived_root(name: str, v_r: float, m_x: float, alpha_inv: float, ratio: float, log10_rho: str) -> dict[str, Any]:
    """A research root of another code or scheme with P,Q,R at x0 p, x0/p taken from the U1 BM-DA1 root."""
    p = chart_scale(alpha_inv, m_x)
    return {"variant": name, "log10_rho": log10_rho, "v_R_GeV": v_r, "alpha_U_inv": alpha_inv, "mu_G_GeV": m_x,
            "x0p_GeV": ratio * p, "p_GeV": p}


def u2_section(runner: Runner, roots: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any) -> dict[str, Any]:
    ratio = x0_over_p(_benchmark_root(roots, "BM-DA1"))
    ratios = [x0_over_p(row) for row in roots]
    runs: dict[str, Any] = {}
    for name, u2 in U2_ROOTS.items():
        root = derived_root("U2", u2["M_I_GeV"], u2["M_X_GeV"], u2["alpha_U_inv"], ratio, U2_LOG10_RHO[name])
        loops = runner.loops(f"U2:{name}:PQR_at_x0p", root, root["x0p_GeV"], b_no, b_with)
        values = {label: _i2(loops[label]) for label in LOOP_LABELS}
        runs[name] = {
            "root_RESEARCH_RECORD_INPUT": root,
            "p_rel_dev_vs_recorded_M_GUT_chart": _rel(root["p_GeV"], u2["M_GUT_chart_GeV"]),
            "alpha_one_GeV": values,
            "integrators": loops,
            "margin_vs_MPlred": {label: (None if value is None else value / M_PL_RED - 1.0) for label, value in values.items()},
            "passes_reduced_Planck_criterion": {label: bool(value is not None and value > M_PL_RED) for label, value in values.items()},
        }
    return {
        "x0_over_p_BM_DA1_U1": ratio,
        "x0_over_p_range_over_U1_roots": [min(ratios), max(ratios)],
        "meaning": "the SO(10) phase run from the second-code (U2) roots with the same x0/p as the U1 BM-DA1 root "
                   "(P,Q,R at x0 p); p = sqrt2 M_X/g_U equals U2's recorded chart scale",
        "runs": runs,
    }


def running_section(runner: Runner, roots: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any) -> dict[str, Any]:
    benchmarks: dict[str, Any] = {}
    scales: dict[str, dict[str, dict[str, float | None]]] = {}
    for name in BENCHMARKS:
        root = _benchmark_root(roots, name)
        per: dict[str, Any] = {}
        scales[name] = {}
        for placement in PQR_PLACEMENTS:
            loops = runner.loops(f"{name}:{placement}", root, _pqr_scale(root, placement), b_no, b_with)
            per[placement] = loops
            scales[name][placement] = {label: _i2(loops[label]) for label in LOOP_LABELS}
        benchmarks[name] = {
            "meaning": BENCHMARK_MEANING[name],
            "root_RESEARCH_RECORD_INPUT": dict(root),
            "alpha_one_GeV": scales[name],
            "integrators": per,
            "margin_vs_MPlred": {
                placement: {label: (None if value is None else value / M_PL_RED - 1.0) for label, value in values.items()}
                for placement, values in scales[name].items()
            },
            "passes_reduced_Planck_criterion": {
                placement: {label: bool(value is not None and value > M_PL_RED) for label, value in values.items()}
                for placement, values in scales[name].items()
            },
        }

    def dev(name: str, placement: str, label: str, record: float) -> float | None:
        return _rel(scales[name][placement][label], record)

    v1 = V1_LANDAU
    da1 = scales["BM-DA1"]
    bme = scales["BM-E"]
    drho = scales["D_rho1e3"]
    record_devs = {
        "BM-DA1": {
            "c6_2L": dev("BM-DA1", "PQR_at_x0p", "2L", C6_LANDAU["baseline"][2]),
            "c6_1L": dev("BM-DA1", "PQR_at_x0p", "1L", C6_LANDAU["baseline"][3]),
            "e2_U1_2L": dev("BM-DA1", "PQR_at_x0p", "2L", E4_BENCHMARKS[("G6", "3.00")][0]),
            "e4_3L": dev("BM-DA1", "PQR_at_x0p", "3L_gauge_only", E4_BENCHMARKS[("G6", "3.00")][2]),
            "v1_1L": dev("BM-DA1", "PQR_at_x0p", "1L", v1["BM-DA1"]["PQR_x0p_1L"]),
            "v1_2L": dev("BM-DA1", "PQR_at_x0p", "2L", v1["BM-DA1"]["PQR_x0p_2L"]),
            "v1_3L": dev("BM-DA1", "PQR_at_x0p", "3L_gauge_only", v1["BM-DA1"]["PQR_x0p_3L"]),
            "v1_MPlred_2L": dev("BM-DA1", "PQR_at_max_x0p_MPlred", "2L", v1["BM-DA1"]["PQR_MPlred_2L"]),
            "v1_MPlred_3L": dev("BM-DA1", "PQR_at_max_x0p_MPlred", "3L_gauge_only", v1["BM-DA1"]["PQR_MPlred_3L"]),
            "c5_3L": dev("BM-DA1", "PQR_at_x0p", "3L_gauge_only", C5_WITNESS_CHAIN["without_120H"]["Lam_3L_x0p"]),
        },
        "BM-E": {
            "e4_2L": dev("BM-E", "PQR_at_x0p", "2L", E4_BENCHMARKS[("D", "2.50")][1]),
            "e4_3L": dev("BM-E", "PQR_at_x0p", "3L_gauge_only", E4_BENCHMARKS[("D", "2.50")][2]),
            "v1_1L": dev("BM-E", "PQR_at_x0p", "1L", v1["BM-E"]["PQR_x0p_1L"]),
            "v1_2L": dev("BM-E", "PQR_at_x0p", "2L", v1["BM-E"]["PQR_x0p_2L"]),
            "v1_3L": dev("BM-E", "PQR_at_x0p", "3L_gauge_only", v1["BM-E"]["PQR_x0p_3L"]),
            "v1_MPlred_3L": dev("BM-E", "PQR_at_max_x0p_MPlred", "3L_gauge_only", v1["BM-E"]["PQR_MPlred_3L"]),
        },
        "D_rho1e3": {
            "e4_2L": dev("D_rho1e3", "PQR_at_x0p", "2L", E4_BENCHMARKS[("D", "3.00")][1]),
            "e4_3L": dev("D_rho1e3", "PQR_at_x0p", "3L_gauge_only", E4_BENCHMARKS[("D", "3.00")][2]),
            "v1_1L": dev("D_rho1e3", "PQR_at_x0p", "1L", v1["D_rho1e3"]["PQR_x0p_1L"]),
            "v1_2L": dev("D_rho1e3", "PQR_at_x0p", "2L", v1["D_rho1e3"]["PQR_x0p_2L"]),
            "v1_3L": dev("D_rho1e3", "PQR_at_x0p", "3L_gauge_only", v1["D_rho1e3"]["PQR_x0p_3L"]),
            "v1_MPlred_3L": dev("D_rho1e3", "PQR_at_max_x0p_MPlred", "3L_gauge_only", v1["D_rho1e3"]["PQR_MPlred_3L"]),
        },
    }

    def within(devs: Mapping[str, float | None]) -> bool:
        return all(value is not None and value <= RECORD_AGREEMENT_REL for value in devs.values())

    def pinned(name: str) -> bool:
        return all(
            _close(scales[name][placement][label], EXPECTED_BENCHMARK_SCALES[name][placement][label], PIN_REL)
            for placement in PQR_PLACEMENTS for label in LOOP_LABELS
        )

    def above(value: float | None) -> bool:
        return value is not None and value > M_PL_RED

    pqr_planck = da1["PQR_at_max_x0p_MPlred"]["3L_gauge_only"]
    u2 = u2_section(runner, roots, b_no, b_with)
    u2_runs = u2["runs"]
    u2_da1 = u2_runs["BM-DA1"]["alpha_one_GeV"]
    checks = {
        "bm_da1_scales_pinned": pinned("BM-DA1"),
        "bm_da1_matches_research_records": within(record_devs["BM-DA1"]),
        "bm_da1_two_loop_pass_three_loop_fail_on_U1_root": above(da1["PQR_at_x0p"]["2L"])
        and da1["PQR_at_x0p"]["3L_gauge_only"] is not None and not above(da1["PQR_at_x0p"]["3L_gauge_only"]),
        "u2_roots_pinned_bm_da1_two_loop_pass_three_loop_marginal_pass": all(
            _close(u2_runs[name]["alpha_one_GeV"][label], EXPECTED_U2_SCALES[name][label], PIN_REL)
            for name in EXPECTED_U2_SCALES for label in LOOP_LABELS
        ) and all(
            run["p_rel_dev_vs_recorded_M_GUT_chart"] is not None and run["p_rel_dev_vs_recorded_M_GUT_chart"] <= U2_CHART_REL
            for run in u2_runs.values()
        ) and above(u2_da1["2L"]) and above(u2_da1["3L_gauge_only"])
        and u2_da1["3L_gauge_only"] < (1.0 + MARGINAL_BAND) * M_PL_RED
        and not above(u2_runs["BM-E"]["alpha_one_GeV"]["3L_gauge_only"]),
        "bm_da1_pqr_at_planck_three_loop_marginal": above(pqr_planck) and pqr_planck < 1.01 * M_PL_RED,
        "bm_e_two_loop_pass_three_loop_fail": pinned("BM-E") and above(bme["PQR_at_x0p"]["2L"])
        and bme["PQR_at_x0p"]["3L_gauge_only"] is not None and not above(bme["PQR_at_x0p"]["3L_gauge_only"]),
        "bm_e_matches_research_records": within(record_devs["BM-E"]),
        "d_remnant_rho1e3_landau_pass_and_matches_records": pinned("D_rho1e3") and within(record_devs["D_rho1e3"])
        and above(drho["PQR_at_x0p"]["3L_gauge_only"]),
    }
    return {
        "label": "NUM",
        "loop_labels": list(LOOP_LABELS),
        "M_Pl_red_GeV": M_PL_RED,
        "integrators": {
            "I1": f"fixed-step RK4 in t = ln(mu/GeV), h = {RK4_STEP} (<= 0.002), threshold at the P,Q,R scale, alpha = 1 "
                  f"located by {RK4_BISECTIONS} bisections of the last step",
            "I2": f"scipy solve_ivp DOP853, rtol = atol = {DOP853_TOL:g}, terminal event alpha^-1 = 1",
            "primary": "I2",
        },
        "benchmarks": benchmarks,
        "u2_roots": u2,
        "research_record_deviations": record_devs,
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (C) landau_cost.
# ---------------------------------------------------------------------------------------------------------------------


def landau_cost_section(runner: Runner, roots: Sequence[Mapping[str, Any]], option_b: Mapping[str, Any]) -> dict[str, Any]:
    root = _benchmark_root(roots, "BM-DA1")
    options: dict[str, Any] = {}
    for key, name, extra in LANDAU_OPTIONS:
        lo, hi = option_b[key]
        loops = runner.loops(f"landau:{key}", root, root["x0p_GeV"], lo, hi)
        values = {label: _i2(loops[label]) for label in LOOP_LABELS}
        options[key] = {
            "research_name": name,
            "role": FLAVOUR_ROLE[key],
            "extra_content_at_mu_G": [list(x) for x in extra],
            "b_below_PQR": _strs(lo),
            "b_above_PQR": _strs(hi),
            "alpha_one_GeV": values,
            "integrators": loops,
            "passes_reduced_Planck_criterion": {label: bool(v is not None and v > M_PL_RED) for label, v in values.items()},
            "c6_record": {"2L": C6_LANDAU[key][2], "1L": C6_LANDAU[key][3]},
            "rel_dev_c6": {"2L": _rel(values["2L"], C6_LANDAU[key][2]), "1L": _rel(values["1L"], C6_LANDAU[key][3])},
        }
    c5 = {
        "without_120H_3L": _rel(options["baseline"]["alpha_one_GeV"]["3L_gauge_only"], C5_WITNESS_CHAIN["without_120H"]["Lam_3L_x0p"]),
        "with_120H_2L": _rel(options["+120_H"]["alpha_one_GeV"]["2L"], C5_WITNESS_CHAIN["with_120H"]["Lam_2L_x0p"]),
        "with_120H_3L": _rel(options["+120_H"]["alpha_one_GeV"]["3L_gauge_only"], C5_WITNESS_CHAIN["with_120H"]["Lam_3L_x0p"]),
        "with_120H_1L": _rel(options["+120_H"]["alpha_one_GeV"]["1L"], C5_WITNESS_CHAIN["with_120H"]["Lam_1L_x0p"]),
    }
    passes_2l = {key: options[key]["passes_reduced_Planck_criterion"]["2L"] for key in options}
    checks = {
        "scales_match_research_records": all(
            dev is not None and dev <= RECORD_AGREEMENT_REL for entry in options.values() for dev in entry["rel_dev_c6"].values()
        ) and all(dev is not None and dev <= RECORD_AGREEMENT_REL for dev in c5.values()),
        "scales_pinned": all(
            _close(options[key]["alpha_one_GeV"]["2L"], EXPECTED_LANDAU_COST[key][0], PIN_REL)
            and _close(options[key]["alpha_one_GeV"]["3L_gauge_only"], EXPECTED_LANDAU_COST[key][1], PIN_REL)
            for key in EXPECTED_LANDAU_COST
        ),
        "every_option_fails_three_loop": all(
            entry["alpha_one_GeV"]["3L_gauge_only"] is not None and not entry["passes_reduced_Planck_criterion"]["3L_gauge_only"]
            for entry in options.values()
        ),
        "two_loop_pass_fail_split": all(passes_2l[key] is False for key in EXPECTED_TWO_LOOP_FAIL_OPTIONS)
        and all(passes_2l[key] is True for key in EXPECTED_TWO_LOOP_PASS_OPTIONS)
        and set(EXPECTED_TWO_LOOP_FAIL_OPTIONS) | set(EXPECTED_TWO_LOOP_PASS_OPTIONS) == set(passes_2l),
    }
    return {
        "label": "NUM",
        "root": "BM-DA1 root held fixed (new multiplets at mu_G, their light components not added below mu_G): a lower bound on the damage",
        "options": options,
        "critic_c5_deviations": c5,
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (D) quality and (E) windows.
# ---------------------------------------------------------------------------------------------------------------------


def quality(s_vev: float, *, m_s: float | None = None, z17_exponent: int = Z17_EXPONENT) -> dict[str, Any]:
    """NDA with Lambda = <S> (this module's convention), NDA with Lambda = M_s (eq. qualitybound) and Z17-EFT."""
    v_s = math.sqrt(2.0) * s_vev
    nda = 2.0 * s_vev**NDA_EXPONENT / (CHI * M_PL_RED**12)
    z17 = Z17_PREFACTOR * (v_s / Z17_REFERENCE_VS) ** z17_exponent
    out: dict[str, Any] = {"S_vev_GeV": s_vev, "v_S_GeV": v_s, "dtheta_NDA": nda, "dtheta_Z17": z17}
    if m_s is not None:
        out["M_s_GeV"] = m_s
        out["dtheta_NDA_Ms"] = 2.0 * m_s**NDA_EXPONENT / (CHI * M_PL_RED**12)
    return out


def _quality_flags(q: dict[str, Any]) -> dict[str, Any]:
    q["NDA_ok"] = q["dtheta_NDA"] < QUALITY_BOUND
    q["Z17_ok"] = q["dtheta_Z17"] < QUALITY_BOUND
    if "dtheta_NDA_Ms" in q:
        q["NDA_Ms_ok"] = q["dtheta_NDA_Ms"] < QUALITY_BOUND
    return q


def _row_key(row: Mapping[str, Any]) -> tuple[str, str, float]:
    return (row["variant"], row["log10_rho"], round(row["v_R_GeV"], -3))


def window_rows(runner: Runner, roots: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any, *, z17_exponent: int) -> list[dict[str, Any]]:
    rows = []
    for root in roots:
        rho = 10.0 ** float(root["log10_rho"])
        tag = f"window:{root['variant']}:{root['log10_rho']}:{root['v_R_GeV']:.6e}"
        at_x0p = runner.loops(tag + ":x0p", root, root["x0p_GeV"], b_no, b_with, ("2L", "3L_gauge_only"))
        at_max = runner.loops(tag + ":max", root, _pqr_scale(root, "PQR_at_max_x0p_MPlred"), b_no, b_with, ("3L_gauge_only",))
        scales = {
            "2L_PQR_at_x0p": _i2(at_x0p["2L"]),
            "3L_gauge_only_PQR_at_x0p": _i2(at_x0p["3L_gauge_only"]),
            "3L_gauge_only_PQR_at_max_x0p_MPlred": _i2(at_max["3L_gauge_only"]),
        }
        segments = _segments(root["mu_G_GeV"], root["x0p_GeV"], b_no, b_with)
        a_inv = alpha_inv_at(root["alpha_U_inv"], segments, 1.0, 0.0, M_PL_RED)
        b_active = b_with if root["x0p_GeV"] <= M_PL_RED else b_no
        ratio = None
        if a_inv is not None:
            a = 1.0 / a_inv
            b2, b3 = float(b_active[1]), float(b_active[2])
            ratio = (b3 * a * a / (32.0 * PI**3)) / (b2 * a / (8.0 * PI**2))
        qual = {}
        for ys in Y_S_VALUES:
            m_s = rho * root["v_R_GeV"]
            qual[f"{ys:.2f}"] = _quality_flags(quality(m_s / ys, m_s=m_s, z17_exponent=z17_exponent))
        rows.append({
            **{key: root[key] for key in _ROOT_FIELDS},
            "source": root.get("source"),
            "alpha_one_GeV": scales,
            "rel_I1_I2": {"2L": at_x0p["2L"]["rel_I1_I2"], "3L_x0p": at_x0p["3L_gauge_only"]["rel_I1_I2"],
                          "3L_max": at_max["3L_gauge_only"]["rel_I1_I2"]},
            "passes": {label: bool(v is not None and v > M_PL_RED) for label, v in scales.items()},
            "alpha_inv_at_MPlred_2L": a_inv,
            "term_ratio_3L_over_2L_at_MPlred": ratio,
            "quality": qual,
        })
    return rows


def _window_sets(rows: Sequence[Mapping[str, Any]], variant: str, ys: str) -> dict[str, list[str]]:
    selected = [row for row in rows if row["variant"] == variant]

    def lrs(predicate: Callable[[Mapping[str, Any]], bool]) -> list[str]:
        return sorted({row["log10_rho"] for row in selected if predicate(row)})

    two = lambda r: r["passes"]["2L_PQR_at_x0p"]  # noqa: E731
    three = lambda r: r["passes"]["3L_gauge_only_PQR_at_x0p"]  # noqa: E731
    nda = lambda r: r["quality"][ys]["NDA_ok"]  # noqa: E731
    z17 = lambda r: r["quality"][ys]["Z17_ok"]  # noqa: E731
    nda_ms = lambda r: r["quality"][ys]["NDA_Ms_ok"]  # noqa: E731
    return {
        "2L": lrs(two),
        "3L_gauge_only": lrs(three),
        "NDA": lrs(nda),
        "Z17": lrs(z17),
        "3L_and_Z17": lrs(lambda r: three(r) and z17(r)),
        "3L_and_NDA": lrs(lambda r: three(r) and nda(r)),
        "NDA_Ms": lrs(nda_ms),
        "3L_and_NDA_Ms": lrs(lambda r: three(r) and nda_ms(r)),
    }


def scheme_variant_rows(runner: Runner, roots: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any, *,
                        z17_exponent: int) -> dict[str, Any]:
    """The RG-improved rho = 1e3 root in the U1 scheme variants (e5) and in code U2: Landau scales and quality."""
    ratio = x0_over_p(_benchmark_root(roots, "BM-DA1"))
    inputs = {f"U1:{name}": row for name, row in E5_U1_VARIANTS_RHO1E3.items()}
    u2 = U2_ROOTS["D_rho1e3"]
    inputs["U2"] = (u2["M_I_GeV"], u2["M_X_GeV"], u2["alpha_U_inv"])
    out = {}
    for name, (v_r, m_x, alpha_inv) in inputs.items():
        root = derived_root(name, v_r, m_x, alpha_inv, ratio, "3.00")
        loops = runner.loops(f"scheme:{name}", root, root["x0p_GeV"], b_no, b_with, ("2L", "3L_gauge_only"))
        values = {label: _i2(loops[label]) for label in ("2L", "3L_gauge_only")}
        m_s = 1000.0 * v_r
        out[name] = {
            "root_RESEARCH_RECORD_INPUT": root,
            "alpha_one_GeV_PQR_at_x0p": values,
            "margin_vs_MPlred": {label: (None if value is None else value / M_PL_RED - 1.0) for label, value in values.items()},
            "quality": {f"{ys:.2f}": _quality_flags(quality(m_s / ys, m_s=m_s, z17_exponent=z17_exponent)) for ys in Y_S_VALUES},
        }
    return out


def quality_section(rows: Sequence[Mapping[str, Any]], *, z17_exponent: int,
                    variants: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, Any]:
    by_key = {(row["variant"], row["log10_rho"], round(row["v_R_GeV"], -3)): row for row in rows}
    deviations = []
    for record in E6_ROWS:
        entry = dict(zip(E6_FIELDS, record))
        row = by_key.get((entry["variant"], entry["log10_rho"], round(entry["v_R_GeV"], -3)))
        if row is None:
            deviations.append(None)
            continue
        q = row["quality"][entry["y_s"]]
        deviations += [_rel(q["S_vev_GeV"], entry["S_vev_GeV"]), _rel(q["dtheta_NDA"], entry["dtheta_NDA"]),
                       _rel(q["dtheta_Z17"], entry["dtheta_Z17"])]
    g6 = by_key[_row_key(_find_one(rows, "G6", "3.00"))]
    d3 = by_key[_row_key(_find_one(rows, "D", "3.00"))]
    bme = by_key[_row_key(_find_one(rows, "D", "2.50"))]
    e2_flag_nda_bme = bme["v_R_GeV"] <= 2.2e9
    e2_flag_z17_bme = bme["v_R_GeV"] <= 4.6e9
    checks = {
        "bm_da1_g6_masses_pass_both_bounds": all(g6["quality"][ys]["NDA_ok"] and g6["quality"][ys]["Z17_ok"] for ys in g6["quality"]),
        "rg_improved_remnants_fail_both_bounds": all(
            not d3["quality"][ys]["NDA_ok"] and not d3["quality"][ys]["Z17_ok"] for ys in d3["quality"]
        ) and _close(d3["v_R_GeV"], 8.5604e9, 1.0e-4) and _close(d3["quality"]["0.30"]["S_vev_GeV"], 2.8535e13, 1.0e-4),
        "matches_e6_record": all(dev is not None and dev <= 1.0e-9 for dev in deviations),
        "e2_hard_coded_flags_disagree_at_bm_e": (not e2_flag_nda_bme and bme["quality"]["0.30"]["NDA_ok"])
        and (not e2_flag_z17_bme and bme["quality"]["0.30"]["Z17_ok"]),
        "rg_improved_failure_scheme_dependence_pinned": bool(variants) and _scheme_dependence_ok(variants),
    }
    return {
        "label": "NUM",
        "convention": QUALITY_CONVENTION,
        "bound": QUALITY_BOUND,
        "z17_exponent": z17_exponent,
        "bm_da1_g6_masses": {"v_R_GeV": g6["v_R_GeV"], "log10_rho": g6["log10_rho"], "quality": g6["quality"]},
        "rg_improved_rho1e3": {"label": "NUM, CONDITIONAL",
                               "conditional_on": [
                                   "the RG-improved remnant masses come from anti-SOS region points (G6 is not closed)",
                                   "the committed GUT scalar spectrum (non-perturbative normalisation; GUT thresholds "
                                   "uncontrolled): the GUT scalar masses x2 scheme variant removes the failure",
                               ],
                               "v_R_GeV": d3["v_R_GeV"], "log10_rho": d3["log10_rho"], "quality": d3["quality"],
                               "multipliers": dict(RG_IMPROVED_MULTIPLIERS)},
        "scheme_variants_rho1e3": {
            "label": "NUM (inputs RESEARCH_RECORD_INPUT: e5 U1 scheme variants and the U2 root)",
            "rows": dict(variants or {}),
            "passing_variant": E5_VARIANT_PASSING_QUALITY,
            "meaning": "doubling the GUT scalar masses removes the RG-improved quality failure (three loops and both "
                       "bounds pass); U2 and every other scheme variant keep the Z17 failure (and the NDA failure with "
                       "Lambda = <S>; with Lambda = M_s the mu_G = 2 M_X variant passes NDA but still fails Z17)",
        },
        "bm_e": {"v_R_GeV": bme["v_R_GeV"], "quality": bme["quality"],
                 "e2_hard_coded_flags": {"NDA_quality_ok(vR<=2.2e9)": e2_flag_nda_bme, "Z17_quality_ok(vR<=4.6e9)": e2_flag_z17_bme},
                 "meaning": "the e2 JSON flags are thresholds for rho = 1e3; at BM-E they say False where both bounds pass"},
        "e6_max_rel_deviation": max((d for d in deviations if d is not None), default=None),
        "checks": checks,
    }


def _scheme_dependence_ok(variants: Mapping[str, Mapping[str, Any]]) -> bool:
    passing = variants.get(f"U1:{E5_VARIANT_PASSING_QUALITY}")
    others = [row for name, row in variants.items() if name != f"U1:{E5_VARIANT_PASSING_QUALITY}"]
    if passing is None or len(others) != len(E5_U1_VARIANTS_RHO1E3):  # seven other U1 variants plus U2
        return False
    passing_ok = all(q["NDA_ok"] and q["NDA_Ms_ok"] and q["Z17_ok"] for q in passing["quality"].values()) and (
        passing["alpha_one_GeV_PQR_at_x0p"]["3L_gauge_only"] or 0.0) > M_PL_RED
    others_fail = all(not q["Z17_ok"] and not q["NDA_ok"] for row in others for q in row["quality"].values())
    nda_ms_passes = sorted(name for name, row in variants.items() if name != f"U1:{E5_VARIANT_PASSING_QUALITY}"
                           and all(q["NDA_Ms_ok"] for q in row["quality"].values()))
    return bool(passing_ok and others_fail and nda_ms_passes == list(E5_NDA_MS_ONLY_PASSING))


def _find_one(rows: Sequence[Mapping[str, Any]], variant: str, lr: str) -> Mapping[str, Any]:
    found = [row for row in rows if row["variant"] == variant and row["log10_rho"] == lr]
    if len(found) != 1:
        raise ValueError(f"expected one row for {variant} {lr}, found {len(found)}")
    return found[0]


def windows_section(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    sets = {variant: {ys: _window_sets(rows, variant, ys) for ys in (f"{y:.2f}" for y in Y_S_VALUES)}
            for variant in VARIANT_ORDER if any(row["variant"] == variant for row in rows)}
    e6_devs = []
    for record in E6_ROWS:
        entry = dict(zip(E6_FIELDS, record))
        if (entry["variant"], entry["log10_rho"]) in E6_DUPLICATED_LANDAU_KEYS:
            continue
        row = _find_one(rows, entry["variant"], entry["log10_rho"])
        e6_devs += [_rel(row["alpha_one_GeV"]["2L_PQR_at_x0p"], entry["L1_2L_pqr_x0p"]),
                    _rel(row["alpha_one_GeV"]["3L_gauge_only_PQR_at_max_x0p_MPlred"], entry["L1_3L_pqr_MPlred"])]
    e4_devs = []
    for (variant, lr), (u1_2l, _e4_2l, e4_3l) in E4_BENCHMARKS.items():
        row = _find_one(rows, variant, lr)
        e4_devs += [_rel(row["alpha_one_GeV"]["2L_PQR_at_x0p"], u1_2l), _rel(row["alpha_one_GeV"]["3L_gauge_only_PQR_at_x0p"], e4_3l)]
    for key, (variant, lr) in V1_WINDOW_KEYS.items():
        row = _find_one(rows, variant, lr)
        e4_devs += [_rel(row["alpha_one_GeV"]["2L_PQR_at_x0p"], V1_LANDAU[key]["PQR_x0p_2L"]),
                    _rel(row["alpha_one_GeV"]["3L_gauge_only_PQR_at_x0p"], V1_LANDAU[key]["PQR_x0p_3L"]),
                    _rel(row["alpha_one_GeV"]["3L_gauge_only_PQR_at_max_x0p_MPlred"], V1_LANDAU[key]["PQR_MPlred_3L"])]
    knife = _find_one(rows, *KNIFE_EDGE)
    knife_3l = knife["alpha_one_GeV"]["3L_gauge_only_PQR_at_x0p"]
    knife_nda = knife["quality"]["0.30"]["dtheta_NDA"]
    duplicated = _find_roots(rows, "D", "2.00")

    def expected(variant: str) -> dict[str, list[str]]:
        return {k: list(v) for k, v in EXPECTED_WINDOWS[variant].items()}

    checks = {
        "rows_complete_and_match_records": len(rows) == EXPECTED_WINDOW_ROWS
        and all(dev is not None and dev <= RECORD_AGREEMENT_REL for dev in e6_devs + e4_devs),
        "d_variant_windows_pinned": sets["D"]["0.30"] == expected("D"),
        "d_best_windows_pinned": sets["D_best"]["0.30"] == expected("D_best"),
        "knife_edge_point": knife_3l is not None and 0.0 < knife_3l / M_PL_RED - 1.0 < 0.01 and 1.0e-11 < knife_nda < QUALITY_BOUND
        and knife["quality"]["0.30"]["Z17_ok"],
        "y_s_034_windows_same": sets["D"]["0.34"] == expected("D") and sets["D_best"]["0.34"] == expected("D_best"),
    }
    return {
        "label": "NUM, CONDITIONAL",
        "conditional_on": [
            "the RG-improved remnant masses come from anti-SOS region points (G6 is not closed)",
            "the GUT-scale thresholds are uncontrolled (witness a0 ~ 21.6 normalisation)",
            "the Yukawa terms (two and three loops) and the three-loop quartic terms are missing",
        ],
        "variant_meaning": dict(VARIANT_MEANING),
        "window_definition": "log10 rho values whose root passes; 3L = 3L_gauge_only with P,Q,R at x0 p; quality at y_s; "
                             "NDA uses Lambda = <S> (this module), NDA_Ms uses Lambda = M_s (manuscript eq. qualitybound): "
                             "the NDA windows are convention-dependent",
        "rows": list(rows),
        "windows": sets,
        "knife_edge": {"variant": KNIFE_EDGE[0], "log10_rho": KNIFE_EDGE[1], "3L_gauge_only_PQR_at_x0p_GeV": knife_3l,
                       "margin_vs_MPlred": None if knife_3l is None else knife_3l / M_PL_RED - 1.0,
                       "dtheta_NDA_ys0.30": knife_nda, "dtheta_Z17_ys0.30": knife["quality"]["0.30"]["dtheta_Z17"]},
        "e6_duplicated_landau_columns": {
            "keys": [list(k) for k in E6_DUPLICATED_LANDAU_KEYS],
            "recomputed_2L_PQR_at_x0p_GeV": [row["alpha_one_GeV"]["2L_PQR_at_x0p"] for row in duplicated],
            "meaning": "e6 keys its Landau columns by (variant, log10 rho): both D log10 rho = 2.00 roots carry the "
                       "second root's values; they are excluded from the record comparison",
        },
        "record_max_rel_deviation": max((d for d in e6_devs + e4_devs if d is not None), default=None),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (F) uncertainty and (G) planck_kinetic.
# ---------------------------------------------------------------------------------------------------------------------


def uncertainty_section(runner: Runner, roots: Sequence[Mapping[str, Any]], running: Mapping[str, Any],
                        rows: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any) -> dict[str, Any]:
    scale_ratio = {}
    term_ratio = {}
    for name in BENCHMARKS:
        values = running["benchmarks"][name]["alpha_one_GeV"]["PQR_at_x0p"]
        two, three = values["2L"], values["3L_gauge_only"]
        scale_ratio[name] = None if (two is None or three is None) else two / three
        variant, lr = BENCHMARKS[name]
        term_ratio[name] = _find_one(rows, variant, lr)["term_ratio_3L_over_2L_at_MPlred"]
    all_ratios = [row["term_ratio_3L_over_2L_at_MPlred"] for row in rows if row["term_ratio_3L_over_2L_at_MPlred"] is not None]
    root = _benchmark_root(roots, "BM-DA1")
    sensitivity = {}
    for factor in B3_SENSITIVITY_FACTORS:
        segments = _segments(root["mu_G_GeV"], root["x0p_GeV"], b_no, b_with)
        entry = runner.scale(f"b3x{factor}", root["alpha_U_inv"], segments, 1.0, factor * runner.three_loop_factor)
        sensitivity[f"x{factor}"] = {**entry, "v1_record": V1_LANDAU["BM-DA1"][f"PQR_x0p_3Lx{factor}"],
                                     "rel_dev_v1": _rel(entry["I2"], V1_LANDAU["BM-DA1"][f"PQR_x0p_3Lx{factor}"])}
    v1_ratio_devs = {name: _rel(term_ratio[name], V1_LANDAU[V1_BENCHMARK_KEYS[name]]["ratio_3L_over_2L_at_MPlred"])
                     for name in BENCHMARKS}
    checks = {
        "two_to_three_loop_scale_ratios": all(
            scale_ratio[name] is not None and abs(scale_ratio[name] - EXPECTED_SCALE_RATIO_2L_OVER_3L[name]) <= RATIO_PIN_ABS
            for name in BENCHMARKS
        ),
        "three_to_two_loop_term_ratios": all(
            term_ratio[name] is not None and abs(term_ratio[name] - EXPECTED_TERM_RATIO[name]) <= RATIO_PIN_ABS
            and v1_ratio_devs[name] is not None and v1_ratio_devs[name] <= RECORD_AGREEMENT_REL
            for name in BENCHMARKS
        ) and len(all_ratios) > 0,
        "b3_sensitivity_matches_record": all(
            entry["rel_dev_v1"] is not None and entry["rel_dev_v1"] <= RECORD_AGREEMENT_REL for entry in sensitivity.values()
        ),
    }
    return {
        "label": "NUM",
        "scale_ratio_2L_over_3L": scale_ratio,
        "term_ratio_3L_over_2L_at_MPlred": {
            "definition": "(b3 alpha^2/(32 pi^3))/(b2 alpha/(8 pi^2)) with b above P,Q,R, alpha on the two-loop trajectory "
                          "at M_Pl,red (roots whose two-loop alpha reaches 1 below M_Pl,red have no value)",
            "benchmarks": term_ratio,
            "v1_record_rel_dev": v1_ratio_devs,
            "range_over_window_rows": [min(all_ratios), max(all_ratios)] if all_ratios else None,
            "n_rows_with_value": len(all_ratios),
            "research_quote_RESEARCH_RECORD_only": "about 0.23-0.32 (VERIFY_feasibility.md); not a computed range",
        },
        "b3_sensitivity_BM_DA1": sensitivity,
        "checks": checks,
    }


def planck_kinetic_section(runner: Runner, roots: Sequence[Mapping[str, Any]], b_no: Any, b_with: Any) -> dict[str, Any]:
    root = _benchmark_root(roots, "BM-DA1")
    derivative = {}
    for label in ("2L", "3L_gauge_only"):
        f2, f3 = runner.factors(label)
        values = []
        for shift in (DLNLAMBDA_STEP, -DLNLAMBDA_STEP):
            segments = _segments(root["mu_G_GeV"], root["x0p_GeV"], b_no, b_with)
            values.append(runner.scale(f"dlnL:{label}:{shift}", root["alpha_U_inv"] + shift, segments, f2, f3)["I2"])
        derivative[label] = None if None in values else (math.log(values[0]) - math.log(values[1])) / (2.0 * DLNLAMBDA_STEP)
    per_unit_c = {}
    for name in BENCHMARKS:
        r = _benchmark_root(roots, name)
        per_unit_c[name] = r["mu_G_GeV"] / M_PL_RED * r["alpha_U_inv"]
    j1f_devs = {key: _rel(entry["M_U_GeV"] / M_PL_RED * entry["alpha_U_inv"], entry["delta_aInv_per_unit_c"])
                for key, entry in J1F_PLANCK_KINETIC.items()}
    shift = None
    if derivative["3L_gauge_only"] is not None and derivative["2L"] is not None:
        shift = {label: math.exp(per_unit_c["BM-DA1"] * derivative[label]) - 1.0 for label in ("2L", "3L_gauge_only")}
    checks = {
        "dlnLambda_daU_inv": all(
            derivative[label] is not None and abs(derivative[label] - EXPECTED_DLNLAMBDA_DAU[label]) <= RATIO_PIN_ABS
            for label in derivative
        ),
        "estimate_arithmetic_matches_j1f_record": all(dev is not None and dev <= 1.0e-12 for dev in j1f_devs.values())
        and abs(per_unit_c["BM-DA1"] - J1F_PLANCK_KINETIC["MU=7.80e+16"]["delta_aInv_per_unit_c"]) < 1.0e-2,
    }
    return {
        "label": "EST (with one NUM derivative)",
        "operator": "c Phi210 F F / M_Pl,red",
        "delta_alpha_inv_per_unit_c_EST": per_unit_c,
        "formula_EST": "delta alpha_i^-1 ~ c (M_X/M_Pl,red) alpha_U^-1 (group factors O(1) omitted)",
        "j1f_record": {key: dict(entry) for key, entry in J1F_PLANCK_KINETIC.items()},
        "j1f_rel_dev": j1f_devs,
        "final_0.23c_is_for": "M_U = 2.07e16 GeV (the G3221 lead), not BM-DA1",
        "dlnLambda_dalphaU_inv_NUM": derivative,
        "fractional_scale_shift_per_unit_c_EST": shift,
        "meaning": "per unit c the alpha = 1 scale moves by about 15-20% [EST], more than the three-loop margins "
                   "at BM-DA1 (-3.8% on the U1 root, +0.14% on the U2 root): the three-loop verdict is convention- and "
                   "threshold-limited",
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (H) research_record.
# ---------------------------------------------------------------------------------------------------------------------


def _flatten_entries(record: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    out = {}
    for name, entry in record.items():
        if isinstance(entry, Mapping) and "label" not in entry:
            for sub, value in entry.items():
                out[f"{name}.{sub}"] = value
        else:
            out[name] = entry
    return out


def research_record_section(record: Mapping[str, Any], files: Mapping[str, Sequence[str]], roots: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    entries = _flatten_entries(record)
    hex64 = re.compile(r"^[0-9a-f]{64}$")
    labelled = bool(entries) and all(
        isinstance(entry, Mapping)
        and entry.get("label") in RESEARCH_LABELS
        and entry.get("source_json") in files
        and entry.get("source_json_sha256") == files[entry["source_json"]][1]
        and hex64.match(str(entry.get("source_json_sha256"))) is not None
        and entry.get("reproducible_from_repository") is False
        for entry in entries.values()
    )
    digest = research_files_digest(files)
    da1 = _benchmark_root(roots, "BM-DA1")
    u2 = U2_ROOTS["BM-DA1"]
    two_code = {"v_R": abs(u2["M_I_GeV"] / da1["v_R_GeV"] - 1.0), "M_X": abs(u2["M_X_GeV"] / da1["mu_G_GeV"] - 1.0),
                "alpha_U_inv": abs(u2["alpha_U_inv"] - da1["alpha_U_inv"])}
    reproduction = (C1_ROUTE_B_ROOT["v_R_GeV"] == da1["v_R_GeV"] and C1_ROUTE_B_ROOT["alpha_U_inv"] == da1["alpha_U_inv"]
                    and C1_ROUTE_B_ROOT["M_X_GeV"] == da1["mu_G_GeV"]
                    and C5_WITNESS_CHAIN["without_120H"]["engine_2L_x0p"] == E4_BENCHMARKS[("G6", "3.00")][0]
                    and C1_ROUTE_B_ROOT["Lam_PQR_x0p"] == E4_BENCHMARKS[("G6", "3.00")][0])
    g6_mass_devs = {name: abs(REMNANT_MASSES_OVER_VR["G6"][name] / math.sqrt(float(level)) - 1.0)
                    for name, level in G6_TREE_LEVELS.items()}
    g6_masses_ok = all(dev <= G6_MASS_REL_TOL for dev in g6_mass_devs.values())
    multipliers_ok = all(
        abs(REMNANT_MASSES_OVER_VR["D"][name] / REMNANT_MASSES_OVER_VR["G6"][name] - factor) <= 1.0e-12
        for name, factor in RG_IMPROVED_MULTIPLIERS.items()
    )
    checks = {
        "entries_labelled_with_provenance": labelled,
        "files_digest_pinned": digest == RESEARCH_FILES_DIGEST,
        "two_code_roots_and_reproduction": two_code["v_R"] <= TWO_CODE_BOUNDS["v_R"] and two_code["M_X"] <= TWO_CODE_BOUNDS["M_X"]
        and reproduction,
        "remnant_masses_consistent": g6_masses_ok and multipliers_ok,
    }
    return {
        "label": "RESEARCH_RECORD",
        "provenance_note": RESEARCH_PROVENANCE_NOTE,
        "path_note": RESEARCH_PATH_NOTE,
        "files_digest": digest,
        "entries": {name: dict(entry) for name, entry in entries.items()},
        "two_code_root_agreement_BM_DA1": {**two_code, "bounds": dict(TWO_CODE_BOUNDS),
                                           "meaning": "U2 relative to U1 (v_R, M_X) and |delta alpha_U^-1|"},
        "critic_engine_reproduces_U1_bit_for_bit": reproduction,
        "g6_remnant_masses_vs_sqrt_committed_tree_levels": {
            "rel_dev": g6_mass_devs,
            "tolerance": G6_MASS_REL_TOL,
            "meaning": "U1 takes the exact G6 tree spectrum at finite r0 = M_I/M_GUT; the committed levels are the "
                       "r0 -> 0 limits, so they agree up to O(r0^2) corrections",
        },
        "rg_improved_multipliers_consistent": multipliers_ok,
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Assembly.
# ---------------------------------------------------------------------------------------------------------------------

SECTION_PREFIXES = (
    ("coefficients", "coefficients"),
    ("running", "running"),
    ("landau_cost", "landau_cost"),
    ("quality", "quality"),
    ("windows", "windows"),
    ("uncertainty", "uncertainty"),
    ("planck_kinetic", "planck_kinetic"),
    ("research_record", "research_record"),
)


def _physics_flags(running: Mapping[str, Any], quality_sec: Mapping[str, Any], agree: bool) -> dict[str, bool]:
    da1 = running["benchmarks"]["BM-DA1"]["alpha_one_GeV"]["PQR_at_x0p"]
    bme = running["benchmarks"]["BM-E"]["alpha_one_GeV"]["PQR_at_x0p"]
    u2_da1 = running["u2_roots"]["runs"]["BM-DA1"]["alpha_one_GeV"]
    u2_bme = running["u2_roots"]["runs"]["BM-E"]["alpha_one_GeV"]
    d3 = quality_sec["rg_improved_rho1e3"]["quality"][f"{Y_S_PRIMARY:.2f}"]

    def above(value: float | None) -> bool:
        return value is not None and value > M_PL_RED

    def below(value: float | None) -> bool:
        return value is not None and value < M_PL_RED

    return {
        "bm_da1_two_loop_pass_both_roots": bool(above(da1["2L"]) and above(u2_da1["2L"])),
        "bm_da1_three_loop_fail_on_U1_root": bool(below(da1["3L_gauge_only"])),
        "bm_da1_three_loop_marginal_pass_on_U2_root": bool(
            above(u2_da1["3L_gauge_only"]) and u2_da1["3L_gauge_only"] < (1.0 + MARGINAL_BAND) * M_PL_RED
        ),
        "bm_da1_rg_improved_quality_fail_conditional": bool(not d3["NDA_ok"] and not d3["Z17_ok"]),
        "bm_e_three_loop_fail_both_roots": bool(below(bme["3L_gauge_only"]) and below(u2_bme["3L_gauge_only"])),
        "integrators_agree": bool(agree),
    }


def assemble_report(sections: Mapping[str, Mapping[str, Any]], runner: Runner, *, record: Mapping[str, Any],
                    files: Mapping[str, Sequence[str]], started: float) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    for prefix, key in SECTION_PREFIXES:
        for name, value in sections[key]["checks"].items():
            checks[f"{prefix}.{name}"] = bool(value)
    worst, n_pairs, missing = runner.max_disagreement()
    agree = worst is not None and worst <= INTEGRATOR_AGREEMENT_REL and not missing
    checks["running.integrators_agree"] = bool(agree)
    physics = _physics_flags(sections["running"], sections["quality"], agree)
    checks["verdict.physics_flags_from_numbers"] = all(physics.values())
    flags: dict[str, bool] = {"evidence_recorded": False, **physics}
    for name in NEVER_TRUE_FLAGS:
        flags[name] = False
    checks["scope.g7_blocked_and_status_neutral"] = bool(
        G7_STATUS == "BLOCKED" and all(flags[name] is False for name in NEVER_TRUE_FLAGS)
    )
    failures = [name for name, value in checks.items() if not value]
    if len(checks) != EXPECTED_N_CHECKS:
        failures.append(CHECK_COUNT_FAILURE)
    passed = not failures
    flags["evidence_recorded"] = passed
    running = dict(sections["running"])
    running["integrator_agreement"] = {"max_rel_I1_I2": worst, "n_pairs": n_pairs, "missing_on_one_side": missing,
                                       "tolerance": INTEGRATOR_AGREEMENT_REL}
    report = {
        "module": MODULE,
        "model_contract_id": MODEL_CONTRACT_ID,
        "gate": GATE,
        "G7_status": G7_STATUS,
        "status": STATUS_RECORDED if passed else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_RECORDED if passed else OVERALL_STATE_OPEN,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "labels": {
            "EXACT": "Fraction or sympy identity",
            "NUM": "float, recomputed in this module",
            "LIT": "a paper that was read (transcription recorded with sha256)",
            "RESEARCH_RECORD": "not re-derived; sha256 provenance of the scratch output",
            "RESEARCH_RECORD_INPUT": "a research value used as an input of a recomputation",
            "EST": "order-of-magnitude arithmetic, never load-bearing for a check",
            "CONDITIONAL": "holds only under the stated conditions",
        },
        "coefficients": sections["coefficients"],
        "running": running,
        "landau_cost": sections["landau_cost"],
        "quality": sections["quality"],
        "windows": sections["windows"],
        "uncertainty": sections["uncertainty"],
        "planck_kinetic": sections["planck_kinetic"],
        "research_record": sections["research_record"],
        "provenance": {
            "research_note": RESEARCH_PROVENANCE_NOTE,
            "path_note": RESEARCH_PATH_NOTE,
            "research_files": {name: {"script": script, "sha256": sha} for name, (script, sha) in files.items()},
            "research_files_digest": research_files_digest(files),
            "repository_inputs": [
                "two_loop_thresholds_v20 (mv_gauge_coefficients, mv_field_contributions, u1_rep, SU2/SU4 tables, "
                "FIELDS_SM_1HDM, FIELDS_PS_ANCHOR, ps_spectator_fields, coefficient_provenance; read-only)",
            ],
            "never_reads_scratch_at_runtime": True,
        },
        "scope": SCOPE,
        "disclosures": _disclosures(sections),
        "verdict": "",
        "runtime_seconds": 0.0,
    }
    if report["G7_status"] != "BLOCKED" or any(flags[name] for name in NEVER_TRUE_FLAGS):
        raise AssertionError("the G7 benchmark evidence module is status-neutral: G7 stays BLOCKED")
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def _disclosures(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    da1 = sections["running"]["benchmarks"]["BM-DA1"]["alpha_one_GeV"]
    u2_da1 = sections["running"]["u2_roots"]["runs"]["BM-DA1"]["alpha_one_GeV"]
    u1_margin = (da1["PQR_at_x0p"]["3L_gauge_only"] or 0.0) / M_PL_RED - 1.0
    u2_margin = (u2_da1["3L_gauge_only"] or 0.0) / M_PL_RED - 1.0
    passing = sections["quality"]["scheme_variants_rho1e3"]["rows"].get(f"U1:{E5_VARIANT_PASSING_QUALITY}")
    planck = da1["PQR_at_max_x0p_MPlred"]["3L_gauge_only"]
    planck_e = sections["running"]["benchmarks"]["BM-E"]["alpha_one_GeV"]["PQR_at_max_x0p_MPlred"]["3L_gauge_only"]
    root = sections["running"]["benchmarks"]["BM-DA1"]["root_RESEARCH_RECORD_INPUT"]
    root_e = sections["running"]["benchmarks"]["BM-E"]["root_RESEARCH_RECORD_INPUT"]
    return {
        "pqr_placement": {
            "3L_gauge_only_PQR_at_max_x0p_MPlred_GeV": planck,
            "margin_vs_MPlred": None if planck is None else planck / M_PL_RED - 1.0,
            "x0p_over_MPlred": root["x0p_GeV"] / M_PL_RED,
            "BM_E_3L_gauge_only_PQR_at_max_x0p_MPlred_GeV": planck_e,
            "BM_E_margin_vs_MPlred": None if planck_e is None else planck_e / M_PL_RED - 1.0,
            "BM_E_x0p_over_MPlred": root_e["x0p_GeV"] / M_PL_RED,
            "meaning": "with P,Q,R at M_Pl,red instead of x0 p BM-DA1 passes three loops marginally (+0.8%) and BM-E "
                       "passes (+5.9%), but that places U(1)_X breaking at the cutoff, where the EFT and the certified "
                       "renormalisable vacuum lose meaning; the recorded verdict uses P,Q,R at x0 p",
        },
        "windows_conditional": {
            "meaning": "the rho windows that pass three loops and a quality bound use the RG-improved remnant masses "
                       "of anti-SOS region points (G6 not closed), uncontrolled GUT thresholds and gauge-only three "
                       "loops: conditional evidence only, not a benchmark",
        },
        "planck_kinetic": {
            "meaning": sections["planck_kinetic"]["meaning"],
            "per_unit_c_BM_DA1": sections["planck_kinetic"]["delta_alpha_inv_per_unit_c_EST"]["BM-DA1"],
        },
        "term_ratio_quote": {
            "meaning": "the research quote '3L/2L ~ 0.23-0.32' is research-recorded only; the module states its own "
                       "per-root values and range (uncertainty.term_ratio_3L_over_2L_at_MPlred)",
        },
        "two_code_root_uncertainty": {
            "U1_3L_gauge_only_GeV": da1["PQR_at_x0p"]["3L_gauge_only"],
            "U1_margin_vs_MPlred": u1_margin,
            "U2_3L_gauge_only_GeV": u2_da1["3L_gauge_only"],
            "U2_margin_vs_MPlred": u2_margin,
            "meaning": "run through this module's integrators, the U1 BM-DA1 root fails three loops by "
                       f"{100 * u1_margin:.1f}% and the second-code U2 root passes by +{100 * u2_margin:.2f}%: the gap "
                       "between the two codes' three-loop scales exceeds the U1 miss, so the BM-DA1 three-loop outcome "
                       "lies within the two-code root uncertainty (a two-loop pass is the robust statement)",
        },
        "three_loop_on_two_loop_root": {
            "meaning": "the 3L_gauge_only SO(10) segment is run from a two-loop root with one-loop MS-bar thresholds; the "
                       "unknown two-loop GUT thresholds are of the same formal order as the three-loop term, so the "
                       "three-loop margins are below the neglected effects",
        },
        "so10_phase_yukawa_terms_omitted": {
            "meaning": "the SO(10)-phase running is gauge + matter only at every order: the two-loop Yukawa terms "
                       "(16.16.10_H, 16.16.126bar_H, y_s S 16_s 16bar_s) are omitted as well as the three-loop Yukawa and "
                       "quartic terms; they enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 "
                       "scale, so the omission is not conservative for the fail statements",
        },
        "nda_convention": {
            "meaning": "the NDA bound uses Lambda = max(M_s, <S>) = <S> = M_s/y_s, more conservative by y_s^-16 (2.3e8 "
                       "at y_s = 0.30) than the manuscript's eq. (qualitybound) with Lambda = M_s; the windows are "
                       "recorded under both (3L and NDA: {2.55} with Lambda = <S>, {2.55, 2.60, 2.65, 2.75} with Lambda "
                       "= M_s for the D variant); the rho = 1e3 RG-improved failure holds under both (NDA with "
                       "Lambda = M_s 1.2e-9 > 1e-10; Z17 3.2e-6)",
        },
        "rg_improved_quality_scheme_dependence": {
            "meaning": sections["quality"]["scheme_variants_rho1e3"]["meaning"],
            "passing_variant_v_R_GeV": passing["root_RESEARCH_RECORD_INPUT"]["v_R_GeV"] if passing else None,
            "passing_variant_quality_ys0.30": passing["quality"]["0.30"] if passing else None,
            "passing_variant_3L_margin_vs_MPlred": passing["margin_vs_MPlred"]["3L_gauge_only"] if passing else None,
        },
        "normalisation_nonperturbative": {
            "meaning": "BM-DA1 uses the committed spectrum, whose normalisation is non-perturbative (singlet-channel "
                       "a0 ~ 21.6, g3_sm_pati_salam_witness_unitarity_v20); on the perturbative x1/50 member every scalar "
                       "tree mass (the remnants below v_R and the GUT scalars) scales by 1/sqrt50 and the root, Landau "
                       "and quality numbers are not recomputed; the GUT scalar masses alone move the rho = 1e3 root "
                       "by a factor 16 across the x0.5/x2 scheme variants (the rescue synthesis quotes up to x30)",
        },
        "e6_duplicated_landau_columns": {"meaning": sections["windows"]["e6_duplicated_landau_columns"]["meaning"]},
        "e2_hard_coded_quality_flags": {"meaning": sections["quality"]["bm_e"]["meaning"]},
        "critic_engine_not_independent": {
            "meaning": "the critic's Route-B engine reproduces the U1 root and scales bit for bit: a reproduction, not an "
                       "independent code; the independent checks are U2 (roots) and v1 (scales)",
        },
    }


def build_report(
    *,
    pgj_table: Mapping[str, Fraction] | None = None,
    rep_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    roots: Sequence[Mapping[str, Any]] | None = None,
    three_loop_factor: float = 1.0,
    rk4_step: float = RK4_STEP,
    z17_exponent: int = Z17_EXPONENT,
    research_files: Mapping[str, Sequence[str]] | None = None,
    research_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the report (defaults = the committed inputs; every other value is a test mutation)."""
    started = time.time()
    files = RESEARCH_FILES if research_files is None else research_files
    record = RESEARCH_RECORD if research_record is None else research_record
    root_rows = default_window_roots() if roots is None else [dict(row) for row in roots]
    runner = Runner(three_loop_factor=three_loop_factor, rk4_step=rk4_step)
    coefficients, context = coefficients_section(pgj_table=pgj_table, rep_overrides=rep_overrides)
    b_no, b_with = context["b_no"], context["b_with"]
    running = running_section(runner, root_rows, b_no, b_with)
    landau = landau_cost_section(runner, root_rows, context["option_b"])
    rows = window_rows(runner, root_rows, b_no, b_with, z17_exponent=z17_exponent)
    variants = scheme_variant_rows(runner, root_rows, b_no, b_with, z17_exponent=z17_exponent)
    quality_sec = quality_section(rows, z17_exponent=z17_exponent, variants=variants)
    windows = windows_section(rows)
    uncertainty = uncertainty_section(runner, root_rows, running, rows, b_no, b_with)
    planck = planck_kinetic_section(runner, root_rows, b_no, b_with)
    research = research_record_section(record, files, root_rows)
    sections = {
        "coefficients": coefficients,
        "running": running,
        "landau_cost": landau,
        "quality": quality_sec,
        "windows": windows,
        "uncertainty": uncertainty,
        "planck_kinetic": planck,
        "research_record": research,
    }
    return assemble_report(sections, runner, record=record, files=files, started=started)


def report_passes(report: Mapping[str, Any]) -> bool:
    """Recorded, nothing failed, the pinned check count, G7 BLOCKED and every never-true flag False."""
    try:
        return bool(
            report["status"] == STATUS_RECORDED
            and report["n_failed"] == 0
            and report["n_checks"] == EXPECTED_N_CHECKS
            and len(report["checks"]) == EXPECTED_N_CHECKS
            and all(report["checks"].values())
            and report["G7_status"] == "BLOCKED"
            and report["flags"]["evidence_recorded"] is True
            and all(report["flags"][name] is False for name in NEVER_TRUE_FLAGS)
        )
    except (KeyError, TypeError):
        return False


def _sci(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return f"{mantissa}e{int(exponent)}"


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the G7 benchmark evidence is NOT recorded (failed: " + ", ".join(report["failures"])
            + "). G7 stays BLOCKED; no gate status changes; nothing is claimed."
        )
    da1 = report["running"]["benchmarks"]["BM-DA1"]["alpha_one_GeV"]["PQR_at_x0p"]
    u2 = report["running"]["u2_roots"]["runs"]["BM-DA1"]["alpha_one_GeV"]
    d3 = report["quality"]["rg_improved_rho1e3"]
    passing = report["quality"]["scheme_variants_rho1e3"]["rows"][f"U1:{E5_VARIANT_PASSING_QUALITY}"]
    ys = f"{Y_S_PRIMARY:.2f}"
    u1_margin = 100.0 * (da1["3L_gauge_only"] / M_PL_RED - 1.0)
    u2_margin = 100.0 * (u2["3L_gauge_only"] / M_PL_RED - 1.0)
    return (
        "G7 is not closed on BM-DA1. It passes the reduced-Planck Landau criterion at two loops (alpha = 1 at "
        f"{_sci(da1['2L'])} GeV on the U1 root, {_sci(u2['2L'])} GeV on the second-code U2 root). At three loops "
        f"(gauge-only; P,Q,R at x0 p) it fails on the U1 root ({_sci(da1['3L_gauge_only'])} GeV < {_sci(M_PL_RED, 3)} GeV, "
        f"{u1_margin:.1f}%) and passes marginally on the U2 root ({_sci(u2['3L_gauge_only'], 3)} GeV, +{u2_margin:.2f}%), "
        "so the BM-DA1 three-loop outcome lies within the two-code root uncertainty (and below the neglected two-loop "
        "GUT thresholds and Yukawa terms). With the RG-improved remnant masses (CONDITIONAL: anti-SOS region points, "
        f"committed GUT scalar spectrum) the rho = 1e3 root moves to v_R = {_sci(d3['v_R_GeV'])} GeV, <S> = "
        f"{_sci(d3['quality'][ys]['S_vev_GeV'])} GeV at y_s = {ys} and fails both axion-quality bounds; doubling the GUT "
        f"scalar masses removes that failure (research scheme variant: v_R = {_sci(passing['root_RESEARCH_RECORD_INPUT']['v_R_GeV'])} "
        f"GeV, NDA {_sci(passing['quality'][ys]['dtheta_NDA'], 1)}, Z17 {_sci(passing['quality'][ys]['dtheta_Z17'], 1)}), "
        "while U2 and the other scheme variants keep it. BM-E passes at two loops only (P,Q,R at x0 p; on both roots). "
        "Every flavour-capable SO(10)-phase addition fails the criterion at three loops at BM-DA1 (a 120_H, a second "
        "126bar and vectorlike pairs already at two loops), as does the contract content itself on the U1 root. The "
        "SO(10)-phase running is gauge + matter only at every order and the rho windows that pass are conditional "
        "(anti-SOS remnant masses; G6 not closed; the NDA window is convention-dependent); a Planck gauge-kinetic term "
        "would move the alpha = 1 scale by more than the three-loop margins (EST). G7 stays BLOCKED."
    )


# ---------------------------------------------------------------------------------------------------------------------
# Markdown and CLI.
# ---------------------------------------------------------------------------------------------------------------------


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def _row(values: Sequence[Any]) -> str:
    return "| " + " | ".join(_fmt(value) for value in values) + " |"


def _ordered(mapping: Mapping[str, Any], preferred: Sequence[str] | Mapping[str, Any]) -> list[str]:
    """Keys of ``mapping`` in the ``preferred`` order first, then the rest sorted (the MD is order-stable)."""
    first = [key for key in preferred if key in mapping]
    return first + sorted(key for key in mapping if key not in first)


def _markdown(report: Mapping[str, Any]) -> str:
    coeff = report["coefficients"]
    running = report["running"]
    landau = report["landau_cost"]
    qual = report["quality"]
    windows = report["windows"]
    unc = report["uncertainty"]
    planck = report["planck_kinetic"]
    research = report["research_record"]
    lines = [
        "# G7 evidence on the decoupled-singlet benchmark BM-DA1 (v20)",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        f"**G7 status:** `{report['G7_status']}` (evidence only; this module never changes a gate status)",
        f"**Checks:** {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed",
        "",
        report["verdict"],
        "",
        "Labels: " + "; ".join(f"`{k}` {v}" for k, v in report["labels"].items()) + ".",
        "",
        "## Flags",
        "",
    ]
    lines += [f"- `{name}`: `{report['flags'][name]}`" for name in _ordered(report["flags"], (*DERIVED_FLAGS, *NEVER_TRUE_FLAGS))]
    lines += ["", "## (A) coefficients (EXACT)", "", coeff["convention"], ""]
    lines.append(_row(["rep", "dim", "T", "C2"]))
    lines.append("|" + " --- |" * 4)
    for name in _ordered(coeff["so10_reps"], SO10_HIGHEST_WEIGHTS):
        data = coeff["so10_reps"][name]
        lines.append(_row([name, data["dim"], data["T"], data["C2"]]))
    lines += [
        "",
        f"SO(10) phase (PGJ): without P,Q,R b = ({', '.join(coeff['so10_phase_b']['no_PQR'])}); with P,Q,R b = "
        f"({', '.join(coeff['so10_phase_b']['with_PQR'])}). MV cross-check (two_loop_thresholds_v20): "
        f"({', '.join(coeff['mv_cross_check']['no_PQR'])}) and ({', '.join(coeff['mv_cross_check']['with_PQR'])}).",
        "",
        "QCD with general Casimirs (b + beta at 1, 2, 3 loops): "
        + ", ".join(coeff["qcd_general_casimirs"]["residuals_b_plus_beta_1L_2L_3L"])
        + f"; n_f = 5, 6: b3 = {coeff['qcd_general_casimirs']['numeric_b3']['5']}, {coeff['qcd_general_casimirs']['numeric_b3']['6']}.",
        "",
        "MSS arXiv:1201.5868 eq. (5) as polynomials in n_G (residuals) and the SM values at n_G = 3:",
        "",
    ]
    lines.append(_row(["group", "residuals 1L, 2L, 3L", "b1, b2, b3 at n_G = 3"]))
    lines.append("|" + " --- |" * 3)
    for group in MSS_EQ5:
        lines.append(_row([group, ", ".join(coeff["mss_eq5"]["residuals"][group]), ", ".join(coeff["mss_eq5"]["values_at_nG_3"][group])]))
    lines += ["", "Chain segments (U1 record = exact re-derivation):", ""]
    lines.append(_row(["segment", "b", "b_ij"]))
    lines.append("|" + " --- |" * 3)
    for name in _ordered(coeff["chain_segments"], U1_BETAS):
        data = coeff["chain_segments"][name]
        lines.append(_row([name, ", ".join(data["b"]), "; ".join(", ".join(row) for row in data["bij"])]))
    lines += ["", "## (B) running (NUM)", "", f"I1: {running['integrators']['I1']}. I2: {running['integrators']['I2']}. "
              f"Max |I1/I2 - 1| = {_fmt(running['integrator_agreement']['max_rel_I1_I2'], 3)} over "
              f"{running['integrator_agreement']['n_pairs']} scales.", ""]
    lines.append(_row(["benchmark", "P,Q,R", "1L (GeV)", "2L (GeV)", "3L_gauge_only (GeV)", "2L pass", "3L pass"]))
    lines.append("|" + " --- |" * 7)
    for name in _ordered(running["benchmarks"], BENCHMARKS):
        entry = running["benchmarks"][name]
        for placement in PQR_PLACEMENTS:
            values = entry["alpha_one_GeV"][placement]
            passes = entry["passes_reduced_Planck_criterion"][placement]
            lines.append(_row([name, placement, values["1L"], values["2L"], values["3L_gauge_only"], passes["2L"], passes["3L_gauge_only"]]))
    u2 = running["u2_roots"]
    lines += ["", f"Second-code (U2) roots, P,Q,R at x0 p with x0/p = {_fmt(u2['x0_over_p_BM_DA1_U1'])} (U1 BM-DA1): "
              + u2["meaning"] + ".", ""]
    lines.append(_row(["benchmark", "v_R (GeV)", "M_X (GeV)", "alpha_U^-1", "x0 p (GeV)", "1L (GeV)", "2L (GeV)",
                       "3L_gauge_only (GeV)", "3L margin"]))
    lines.append("|" + " --- |" * 9)
    for name in _ordered(u2["runs"], BENCHMARKS):
        entry = u2["runs"][name]
        root = entry["root_RESEARCH_RECORD_INPUT"]
        values = entry["alpha_one_GeV"]
        lines.append(_row([name, root["v_R_GeV"], root["mu_G_GeV"], root["alpha_U_inv"], root["x0p_GeV"], values["1L"],
                           values["2L"], values["3L_gauge_only"], entry["margin_vs_MPlred"]["3L_gauge_only"]]))
    lines += ["", "Benchmark roots (RESEARCH_RECORD_INPUT, code U1):", ""]
    lines.append(_row(["benchmark", "variant", "log10 rho", "v_R (GeV)", "M_X = mu_G (GeV)", "alpha_U^-1", "x0 p (GeV)"]))
    lines.append("|" + " --- |" * 7)
    for name in _ordered(running["benchmarks"], BENCHMARKS):
        root = running["benchmarks"][name]["root_RESEARCH_RECORD_INPUT"]
        lines.append(_row([name, root["variant"], root["log10_rho"], root["v_R_GeV"], root["mu_G_GeV"], root["alpha_U_inv"], root["x0p_GeV"]]))
    lines += ["", "## (C) landau_cost (NUM; BM-DA1 root held fixed, P,Q,R at x0 p)", ""]
    lines.append(_row(["option", "b below P,Q,R (1L, 2L, 3L)", "2L (GeV)", "3L_gauge_only (GeV)", "2L pass", "3L pass", "role"]))
    lines.append("|" + " --- |" * 7)
    for key in _ordered(landau["options"], [option[0] for option in LANDAU_OPTIONS]):
        entry = landau["options"][key]
        lines.append(_row([key, ", ".join(entry["b_below_PQR"]), entry["alpha_one_GeV"]["2L"], entry["alpha_one_GeV"]["3L_gauge_only"],
                           entry["passes_reduced_Planck_criterion"]["2L"], entry["passes_reduced_Planck_criterion"]["3L_gauge_only"], entry["role"]]))
    lines += ["", "## (D) quality (NUM)", "", qual["convention"], ""]
    lines.append(_row(["point", "y_s", "v_R (GeV)", "<S> (GeV)", "dtheta NDA", "dtheta Z17", "NDA ok", "Z17 ok"]))
    lines.append("|" + " --- |" * 8)
    for label, key in (("BM-DA1 (G6 masses)", "bm_da1_g6_masses"), ("rho = 1e3, RG-improved", "rg_improved_rho1e3"), ("BM-E", "bm_e")):
        entry = qual[key]
        for ys, q in entry["quality"].items():
            lines.append(_row([label, ys, entry["v_R_GeV"], q["S_vev_GeV"], q["dtheta_NDA"], q["dtheta_Z17"], q["NDA_ok"], q["Z17_ok"]]))
    variants = qual["scheme_variants_rho1e3"]
    lines += ["", "RG-improved rho = 1e3 root (" + qual["rg_improved_rho1e3"]["label"] + "): conditional on "
              + "; ".join(qual["rg_improved_rho1e3"]["conditional_on"]) + ".", "",
              "Scheme variants of that root (" + variants["label"] + "): " + variants["meaning"] + ".", ""]
    lines.append(_row(["variant", "v_R (GeV)", "3L margin", "<S> (0.30)", "NDA (<S>)", "NDA (M_s)", "Z17", "NDA ok",
                       "Z17 ok"]))
    lines.append("|" + " --- |" * 9)
    for name in sorted(variants["rows"]):
        entry = variants["rows"][name]
        q = entry["quality"]["0.30"]
        lines.append(_row([name, entry["root_RESEARCH_RECORD_INPUT"]["v_R_GeV"], entry["margin_vs_MPlred"]["3L_gauge_only"],
                           q["S_vev_GeV"], q["dtheta_NDA"], q["dtheta_NDA_Ms"], q["dtheta_Z17"], q["NDA_ok"], q["Z17_ok"]]))
    lines += ["", "## (E) windows (NUM, CONDITIONAL)", "", "Conditional on: " + "; ".join(windows["conditional_on"]) + ".", ""]
    lines.append(_row(["variant", "log10 rho", "v_R (GeV)", "alpha_U^-1", "2L (x0 p)", "3L (x0 p)", "3L (P,Q,R at max(x0 p, M_Pl,red))",
                       "NDA (0.30)", "Z17 (0.30)", "3L/2L term ratio"]))
    lines.append("|" + " --- |" * 10)
    for row in windows["rows"]:
        scales = row["alpha_one_GeV"]
        q = row["quality"]["0.30"]
        lines.append(_row([row["variant"], row["log10_rho"], row["v_R_GeV"], row["alpha_U_inv"], scales["2L_PQR_at_x0p"],
                           scales["3L_gauge_only_PQR_at_x0p"], scales["3L_gauge_only_PQR_at_max_x0p_MPlred"], q["dtheta_NDA"],
                           q["dtheta_Z17"], row["term_ratio_3L_over_2L_at_MPlred"]]))
    lines += ["", "Windows (log10 rho sets):", ""]
    lines.append(_row(["variant", "y_s", "2L", "3L", "NDA (<S>)", "Z17", "3L and Z17", "3L and NDA (<S>)", "NDA (M_s)",
                       "3L and NDA (M_s)"]))
    lines.append("|" + " --- |" * 10)
    for variant in _ordered(windows["windows"], VARIANT_ORDER):
        per = windows["windows"][variant]
        for ys, sets in sorted(per.items()):
            lines.append(_row([variant, ys, *(", ".join(sets[k]) or "none" for k in (
                "2L", "3L_gauge_only", "NDA", "Z17", "3L_and_Z17", "3L_and_NDA", "NDA_Ms", "3L_and_NDA_Ms"))]))
    knife = windows["knife_edge"]
    lines += ["", f"Knife edge {knife['variant']} log10 rho = {knife['log10_rho']}: 3L = {_fmt(knife['3L_gauge_only_PQR_at_x0p_GeV'])} GeV "
              f"(margin {_fmt(knife['margin_vs_MPlred'], 3)}), NDA = {_fmt(knife['dtheta_NDA_ys0.30'], 3)}.", "",
              "## (F) uncertainty (NUM)", ""]
    lines.append(_row(["benchmark", "Lambda_2L/Lambda_3L", "3L/2L term ratio at M_Pl,red"]))
    lines.append("|" + " --- |" * 3)
    for name in BENCHMARKS:
        lines.append(_row([name, unc["scale_ratio_2L_over_3L"][name], unc["term_ratio_3L_over_2L_at_MPlred"]["benchmarks"][name]]))
    rng = unc["term_ratio_3L_over_2L_at_MPlred"]["range_over_window_rows"]
    lines += ["", f"Term-ratio range over the {unc['term_ratio_3L_over_2L_at_MPlred']['n_rows_with_value']} window rows whose "
              f"two-loop alpha stays below 1 up to M_Pl,red (NUM): {_fmt(rng[0] if rng else None, 4)} to "
              f"{_fmt(rng[1] if rng else None, 4)}; values near or above 1 occur where the two-loop alpha approaches 1 at "
              f"M_Pl,red. Research quote (RESEARCH_RECORD only): "
              f"{unc['term_ratio_3L_over_2L_at_MPlred']['research_quote_RESEARCH_RECORD_only']}.", "",
              "b3 sensitivity at BM-DA1 (3L alpha = 1 scale): "
              + ", ".join(f"{k}: {_fmt(v['I2'])}" for k, v in unc["b3_sensitivity_BM_DA1"].items()) + ".", "",
              "## (G) planck_kinetic (EST)", "",
              f"{planck['formula_EST']}; per unit c: " + ", ".join(f"{k} {_fmt(planck['delta_alpha_inv_per_unit_c_EST'][k], 4)}" for k in _ordered(planck["delta_alpha_inv_per_unit_c_EST"], BENCHMARKS))
              + f". d ln Lambda/d alpha_U^-1 (NUM): " + ", ".join(f"{k} {_fmt(v, 4)}" for k, v in planck["dlnLambda_dalphaU_inv_NUM"].items())
              + f". {planck['meaning']}. The FINAL '0.23c' is for {planck['final_0.23c_is_for']}.", "",
              "## (H) research_record (not re-derived)", "", research["provenance_note"] + ". " + research["path_note"] + ".", ""]
    lines.append(_row(["entry", "label", "source", "sha256"]))
    lines.append("|" + " --- |" * 4)
    for name, entry in research["entries"].items():
        lines.append(_row([name, entry["label"], entry["source_json"], entry["source_json_sha256"][:16] + "..."]))
    lines += ["", "## Scope", ""]
    for key, items in report["scope"].items():
        lines += [f"**{key}**", ""] + [f"- {item}" for item in items] + [""]
    lines += ["## Disclosures", ""]
    for key, value in report["disclosures"].items():
        lines.append(f"- `{key}`: {value.get('meaning', '')}")
    lines += ["", "## Checks", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} `{name}`" for name, value in report["checks"].items()]
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json.loads(json.dumps(_jsonable(report), sort_keys=True))), encoding="utf-8")


def main(argv: list[str] | None = None, *, report_builder: Callable[[], dict[str, Any]] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts (only when every check passes)")
    args = parser.parse_args(argv)
    report = (report_builder or build_report)()
    passes = report_passes(report)
    if args.write and passes:
        write_report(report)
    elif args.write:
        print("REFUSED: the report does not pass (failed: " + ", ".join(report.get("failures", [])) + "); nothing written")
    summary = {key: report.get(key) for key in ("status", "overall_state", "G7_status", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if passes else 1


if __name__ == "__main__":
    raise SystemExit(main())
