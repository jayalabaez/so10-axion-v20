#!/usr/bin/env python3
"""Perturbative-unitarity normalisation of the G3 SM Pati-Salam witness: exact, status-neutral record (v20).

The committed G3 witness (g3_sm_pati_salam_candidate_v20, 27 parameters, r0 = 1/5, x0 = 1, kappa = -r0/4) is
certified exactly (SOS identity, equality set, exact 486 x 486 Hessian), but its coupling normalisation is not
perturbative.  This module computes the tree-level s-wave amplitude a0 of the coupled SO(10) x U(1)_X x U(1)_PQ
singlet two-particle channel exactly, and records a rescaled member of the certified family with |a0| <= 1/2.

(A) Method [EXACT lemma].  At s -> infinity only the quartic contact terms contribute (trilinear exchange falls
    off as 1/s).  In the canonical chart (K = q^T q/2) the five blocks Phi (n = 210 reals), H (20), Sigma (252),
    S (2) and Phi17 (2) are irreducible real representations of G = SO(10) x U(1)_X x U(1)_PQ (Phi of real type,
    the others of complex type), so the only invariant quadratic form on a block is |x_A|^2.  Hence, with
    x ~ N(0, 1) per real component,

        E[V4_A] = (1/8) Lap^2 V4_A       = (n_A/4) alpha_A,    alpha_A    = Tr Hess_q V4_A(e), any unit e in A,
        E[V_AB] = (1/4) Lap_A Lap_B V_AB = (n_B/2) beta_{A|B}, beta_{A|B} = Tr_A Hess_q V_AB at unit x_B,

    and the singlet-channel matrix (the normalisation of the research study, D/s03) is M_AA = -alpha_A,
    M_AB = -sqrt(n_B/n_A) beta_{A|B}.  Its eigenvalues are those of the rational matrix -4 N^-1 E (a similarity
    transform), and a0 = eig/(16 pi).  Calibration: V = lambda (H^dag H)^2 on a complex doublet gives
    a0 = 3 lambda/(8 pi).  alpha and beta are read from the per-unit exact Hessians at q0 of
    g3_sm_pati_salam_exact_hessian_v20 (u -> q traces: Phi x1, complex blocks x1/2; divided by the chart norms
    |p|^2 = 1, |q_Sigma|^2 = 2 r0^2, |q_S|^2 = 2 r0^2, |q_Phi17|^2 = 2 x0^2).  alpha_H = 22 lambda_H is computed
    with sympy (the O36 units are empty at H = 0).  Every unit's degree is certified by the Euler relation
    H_u u0 = (d - 1) grad_u where the gradient is nonzero; the zero-gradient units (H-bilinear at H = 0, and the
    O27 channels 54, 1050bar, 4125, orthogonal to sigma_std x sigma_std) by field content, block support and the
    exact scaling of their Hessian under r0 -> 2 r0.  Cubic and quadratic units are excluded.

(B) Committed witness [EXACT].  alpha_Phi = 1084, alpha_H = 44, alpha_Sigma = 16645/448, alpha_S = 4,
    alpha_Phi17 = 1/8, beta_{Phi|Sigma} = 205/4, beta_{Sigma|Phi} = 123/2 (252 x 205/4 = 210 x 123/2 = 12915),
    beta_{H|Phi} = 12, every other pair 0.  a0_max = 21.654 (NUM), enclosed exactly in (21, 22) and, from an
    isolating interval of the characteristic cubic, in (21.64, 21.66): the benchmark normalisation is
    non-perturbative (the 210 singlet entry alone is 1084/(16 pi) = 21.565).

(C) Rescaling lemma [EXACT].  Scaling each of the seven SOS terms of the committed identity by its own factor
    s_k > 0 keeps the SOS identity, V0(s) = sum_k s_k m_k, the equality set and the Hessian kernel and inertia (a
    sum of PSD terms at q0).  Scaling a proper subset of a term's parameters need not keep it: O48 alone or O27
    alone moves the Phi or Sigma radius (exact nonzero gradient at q0), whereas the O36-only lambda_H change of
    g3_sm_pati_salam_higgs_quartic_member_v20 does keep it under its kappa margin.

(D) Perturbative member [EXACT].  All 27 couplings x 1/50: H_u(s) = s H_u(1) exactly, inertia 447/39/0 (451/35/0
    for the O06-raised variant, whose offset r0^2/100 is added unscaled), smallest nonzero eigenvalue r0^2/4800
    (the certificate's own gap flag assumes r0^2/96 and is re-checked here), V0 -> V0/50, and a0_max = 0.4331 <=
    1/2 (rational bound 8 pi > 1332/53).  s_max lies in (1/44, 1/43).  Rescaling only the 210 block (T_Phi) by
    1/50 gives a0_max = 1.98 (fails): the H and Sigma self channels and the Phi-H and Phi-Sigma mixings also
    exceed the bound, which corrects the rescue synthesis line "rescale the 210 block by 0.02".

(E) What changes.  Every tree mass^2 scales by s (masses by sqrt(s) = 0.1414); the vevs and the gauge-boson
    masses do not; lambda_eff -> 127/3200.  The D12 GUT thresholds and the G6/G7 research numbers assume the
    committed normalisation and are not recomputed.

Status neutrality.  Only the singlet channel is computed.  The committed witness stays the G3 closing instance,
no benchmark is chosen, no gate or ledger entry changes, and nothing here is read by any gate module.  The
exact-Hessian module's ``overrides`` keyword (documented for mutation tests) is used read-only to evaluate the
rescaled members.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import time
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy

import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
MODULE = "g3_sm_pati_salam_witness_unitarity_v20"
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_WITNESS_UNITARITY_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_WITNESS_UNITARITY_V20.md"

STATUS_CERTIFIED = (
    "SM_PATI_SALAM_WITNESS_UNITARITY__COMMITTED_NONPERTURBATIVE__RESCALED_MEMBER_SINGLET_CHANNEL_PERTURBATIVE_EXACT"
    "__STATUS_NEUTRAL"
)
STATUS_INCOMPLETE = "SM_PATI_SALAM_WITNESS_UNITARITY_INCOMPLETE__STATUS_NEUTRAL"
OVERALL_STATE_CERTIFIED = "COMMITTED_WITNESS_SINGLET_A0_21_65__OVERALL_ONE_FIFTIETH_MEMBER_A0_0_433__NO_GATE_CHANGE"
OVERALL_STATE_OPEN = "WITNESS_UNITARITY_RECORD_NOT_CERTIFIED__NO_GATE_CHANGE"
MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
EXPECTED_N_CHECKS = 57  # enforced by build_report and report_passes
CHECK_COUNT_FAILURE = "check_count_equals_EXPECTED_N_CHECKS"
EXPECTED_N_FLOAT_CHECKS = 2

R0, X0, KAPPA = hessian.R0, hessian.X0, hessian.KAPPA
T = candidate.SIGMA_SCALE  # 1/8
TOTAL_DIM = chart.TOTAL_DIM
BLOCKS = ("Phi", "H", "Sigma", "S", "Phi17")
BLOCK_SLICES = {"Phi": chart.PHI_SLICE, "H": chart.H_SLICE, "Sigma": chart.SIGMA_SLICE, "S": chart.S_SLICE, "Phi17": chart.X_SLICE}
BLOCK_DIMS = {"Phi": 210, "H": 20, "Sigma": 252, "S": 2, "Phi17": 2}
# Hess_q = D^-1 H_u D^-1 with D^2 = diag(1 on Phi, 2 on the complex blocks): q-trace = u-trace / D^2.
D_SQUARED = {"Phi": 1, "H": 2, "Sigma": 2, "S": 2, "Phi17": 2}

# pi bounds (exact rationals): 333/106 < pi < 22/7.
PI_LOWER = Fraction(333, 106)
PI_UPPER = Fraction(22, 7)
HALF_BOUND_BELOW = 8 * PI_LOWER  # 1332/53 < 8 pi: max|eig| < 1332/53 certifies a0 < 1/2
HALF_BOUND_ABOVE = 8 * PI_UPPER  # 176/7 > 8 pi: max|eig| > 176/7 certifies a0 > 1/2

# The seven SOS terms of the committed identity (g3_sm_pati_salam_candidate_v20.exact_certificate_section):
# V = [-2|Phi|^2 + Q(Phi)] + (1/8)||(M_Phi - 2)Sigma||^2 + (1/8)||C_Phi Sigma||^2 + (1/8)[W'(Sigma) - 2 r0^2 N_Sigma]
#     + [2 N_H^2 + 2|k| r0 N_H + 2k Re(conj(H.H) conj(S)) + (|S|^2 - r0^2)^2] + ||H wedge Phi||^2
#     + (1/32)(|Phi17|^2 - x0^2)^2  (constants dropped).
TERM_NAMES = ("T_Phi", "A_square", "C_square", "W", "T_HS", "T_HPhi", "T_X")
TERM_TEXT = {
    "T_Phi": "-2|Phi|^2 + Q(Phi) (O07, O48 x4); minimum -1",
    "A_square": "(1/8)||(M_Phi - 2)Sigma||^2 (O44 a-weights (40,72,28,-8,-12,12)/8, O14 = -1/2, O05 part 1/2); minimum 0",
    "C_square": "(1/8)||C_Phi Sigma||^2 (O44 c-weights (1,...,1)/8); minimum 0",
    "W": "(1/8)[W'(Sigma) - 2 r0^2 N_Sigma] (O27 weights w_q/8, O05 part -r0^2/4); minimum -r0^4/8",
    "T_HS": "2 N_H^2 + 2|k| r0 N_H + 2k Re(conj(H.H) conj(S)) + |S|^4 - 2 r0^2 |S|^2 (O36 x2, O06, re::O12, O04, O23); "
    "minimum -r0^4",
    "T_HPhi": "||H wedge Phi||^2 (O46_B01 = 3/5, O46_B03 = -1); minimum 0",
    "T_X": "(1/32)|Phi17|^4 - (x0^2/16)|Phi17|^2 (O03, O20); minimum -x0^4/32",
}
O44_IDS = hessian.O44_IDS
O48_IDS = hessian.O48_IDS
O36_IDS = hessian.O36_IDS
O07_ID, O14_ID, O05_ID, O06_ID, O12_ID = hessian.O07_ID, hessian.O14_ID, hessian.O05_ID, hessian.O06_ID, hessian.O12_ID
O04_ID, O23_ID, O03_ID, O20_ID = hessian.O04_ID, hessian.O23_ID, hessian.O03_ID, hessian.O20_ID
O46_1_ID, O46_54_ID = candidate.O46_1_ID, candidate.O46_54_ID
SELF_IDS = candidate.SELF_IDS
O27_IDS = tuple(SELF_IDS[channel] for channel in candidate.SELF_CHANNELS)
J_NAMES = ("J0", "J2", "J3", "J4")

MEMBER_SCALE = Fraction(1, 50)
S_MAX_BRACKET = (Fraction(1, 44), Fraction(1, 43))
FAILING_OVERALL_SCALE = Fraction(1, 40)
PHI_ONLY_SCALES = {"T_Phi": Fraction(1, 50)}
# A blockwise lemma test point (NOT a benchmark): whole SOS terms scaled by different factors (A and C together,
# because the exact Hessian module binds O44 as one A+C unit).
BLOCKWISE_TEST_SCALES = {
    "T_Phi": Fraction(1, 50),
    "A_square": Fraction(1, 50),
    "C_square": Fraction(1, 50),
    "W": Fraction(1, 2),
    "T_HS": Fraction(1, 4),
    "T_HPhi": Fraction(1, 10),
    "T_X": Fraction(1),
}
SUBSET_SCALE = Fraction(1, 50)

# Unit classification: degree, kind and blocks of every exact binding unit (hessian.binding_units).
# kind: "quadratic" / "cubic" (excluded at s -> infinity), "self" (quartic in one block), "self_analytic" (quartic
# in H, empty at H = 0; alpha from sympy), "mixed" (quadratic in each of two blocks).
UNIT_TABLE: dict[str, tuple[int, str, tuple[str, ...]]] = {
    "O07 |Phi|^2": (2, "quadratic", ("Phi",)),
    "O48 J0": (4, "self", ("Phi",)),
    "O48 J2": (4, "self", ("Phi",)),
    "O48 J3": (4, "self", ("Phi",)),
    "O48 J4": (4, "self", ("Phi",)),
    "O44 ||M_Phi Sigma||^2 + ||C_Phi Sigma||^2": (4, "mixed", ("Phi", "Sigma")),
    "O14 Sigma^dag M_Phi Sigma": (3, "cubic", ("Phi", "Sigma")),
    "O05 N_Sigma": (2, "quadratic", ("Sigma",)),
    "O27 I_54": (4, "self", ("Sigma",)),
    "O27 I_1050bar": (4, "self", ("Sigma",)),
    "O27 I_2772bar": (4, "self", ("Sigma",)),
    "O27 I_4125": (4, "self", ("Sigma",)),
    "O06 N_H": (2, "quadratic", ("H",)),
    "re::O12 2 Re[conj(H.H) conj(S)]": (3, "cubic", ("H", "S")),
    "O36 I_1(H) (quartic in H)": (4, "self_analytic", ("H",)),
    "O36 I_54(H) (quartic in H)": (4, "self_analytic", ("H",)),
    "O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H": (4, "mixed", ("H", "Phi")),
    "O04 |S|^2": (2, "quadratic", ("S",)),
    "O23 |S|^4": (4, "self", ("S",)),
    "O03 |Phi17|^2": (2, "quadratic", ("Phi17",)),
    "O20 |Phi17|^4": (4, "self", ("Phi17",)),
}
# Units with zero gradient at q0: field content (degree = total count), the compiler parameter-id token and the block
# carrying their Hessian at q0.  The H-bilinear units vanish to second order at H = 0; the O27 channels 54, 1050bar and
# 4125 have zero gradient because sigma_std x sigma_std lies entirely in 2772bar.  Their degree is certified by the
# exact scaling of the unit Hessian under (Sigma, S) -> 2 (Sigma, S), i.e. r0 -> 2 r0 (VEV_SCALING).
ZERO_GRADIENT_FIELD_CONTENT = {
    "O27 I_54": ({"Sigma": 2, "Sigmadag": 2}, "126bar_self_projectors", "Sigma"),
    "O27 I_1050bar": ({"Sigma": 2, "Sigmadag": 2}, "126bar_self_projectors", "Sigma"),
    "O27 I_2772bar": ({"Sigma": 2, "Sigmadag": 2}, "126bar_self_projectors", "Sigma"),
    "O27 I_4125": ({"Sigma": 2, "Sigmadag": 2}, "126bar_self_projectors", "Sigma"),
    "O06 N_H": ({"H": 1, "Hdag": 1}, "Hdag_H_norm", "H"),
    "re::O12 2 Re[conj(H.H) conj(S)]": ({"Hdag": 2, "Sdag": 1}, "Hdag_Hdag_pair", "H"),
    "O36 I_1(H) (quartic in H)": ({"H": 2, "Hdag": 2}, "H_self_quartics", "H"),
    "O36 I_54(H) (quartic in H)": ({"H": 2, "Hdag": 2}, "H_self_quartics", "H"),
    "O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H": ({"Phi": 2, "H": 1, "Hdag": 1}, "Phi2_HdagH", "H"),
}
VEV_SCALING = Fraction(2)  # r0 -> 2 r0 (Sigma and S vevs doubled; p and x0 fixed)
SCALED_FIELDS = ("Sigma", "Sigmadag", "S", "Sdag")
O36_CHANNEL_BY_UNIT = {"O36 I_1(H) (quartic in H)": "I_1", "O36 I_54(H) (quartic in H)": "I_54"}
MEASURED_PAIRS = ("Phi|Sigma", "Sigma|Phi", "H|Phi")

# Pinned exact values (committed witness).
EXPECTED_ALPHA = {"Phi": Fraction(1084), "H": Fraction(44), "Sigma": Fraction(16645, 448), "S": Fraction(4), "Phi17": Fraction(1, 8)}
EXPECTED_BETA = {"Phi|Sigma": Fraction(205, 4), "Sigma|Phi": Fraction(123, 2), "H|Phi": Fraction(12)}
EXPECTED_PHI_SIGMA_CONSISTENCY = Fraction(12915)
EXPECTED_RATIONAL_BLOCK = (
    (Fraction(-1084), Fraction(-12), Fraction(-123, 2)),
    (Fraction(-126), Fraction(-44), Fraction(0)),
    (Fraction(-205, 4), Fraction(0), Fraction(-16645, 448)),
)
EXPECTED_CUBIC = "lam**3 + 521989*lam**2/448 + 594593*lam/7 + 88325365/56"
EXPECTED_V0 = Fraction(-20661, 20000)
EXPECTED_TERM_GROUP_MINIMA = {
    "T_Phi": Fraction(-1),
    "A_square+C_square": Fraction(0),
    "W": -T * R0**4,
    "T_HS": -(R0**4),
    "T_HPhi": Fraction(0),
    "T_X": -(X0**4) / 32,
}
EXPECTED_ALPHA_H_PER_CHANNEL = {"I_1": Fraction(2, 5), "I_54": Fraction(108, 5), "N_H^2": Fraction(22)}
EXPECTED_MEMBER_LAMBDA_EFF = Fraction(127, 3200)
EXPECTED_GAP_MULTIPLICITY = 14
ISOLATING_INTERVAL_WIDTH = Fraction(1, 10**9)
FLOAT_SEED = 20260927
FLOAT_TOLERANCE = 1.0e-12
NUM_EIGENVALUE_REL_TOLERANCE = 1.0e-9
RESEARCH_REL_TOLERANCE = 1.0e-12
RESEARCH_SIGMAS = 3

NEVER_TRUE_FLAGS = (
    "gate_status_changed",
    "G3_witness_replaced",
    "wired_into_gate_ledger",
    "non_singlet_channels_computed",
    "thresholds_recomputed",
    "benchmark_chosen",
    "report_closes_g3_by_itself",
    "report_closes_g6_by_itself",
)

# ---------------------------------------------------------------------------
# Research record (not re-derived; the values are embedded, never read from scratch at runtime).
# ---------------------------------------------------------------------------

RESEARCH_PROVENANCE_NOTE = (
    "scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for "
    "audit only; the source files are not in the repository and were hashed at generation time (the session scratch "
    "area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified "
    "at runtime"
)
S03_JSON = "wfRESCUE/D-G6-certification/s03_unitarity.json"
S03_PY = "wfRESCUE/D-G6-certification/s03_unitarity.py"
VERIFY_MD = "wfRESCUE/D-G6-certification/VERIFY_physics.md"
SYNTHESIS_MD = "wfRESCUE/SYNTHESIS.md"
FINAL_MD = "wfRESCUE/FINAL.md"
RESEARCH_FILES = {
    S03_JSON: (S03_PY, "3e0d46fdf37a49482ba0dcc7204cddac822a35709088d9e0047643c6d49e31ed"),
    S03_PY: ("research script producing s03_unitarity.json", "1abb418aef9e32a5dc099c4db518af71a54073504adec02dfb3cfa81ecb0196a"),
    VERIFY_MD: ("D-G6-certification physics verifier review", "7a979d737afaa8d75a2a0538f31e3ef45dd18b1b4982e1a78c1cd8ed49503242"),
    SYNTHESIS_MD: ("rescue-study synthesis (route scorecard, PR-1..PR-5)", "a805b3272a2a2ec109181f3feb2a44b4c2e0f6d6029cd420ec28545045acf01b"),
    FINAL_MD: ("rescue-study final adjudication", "90f29e8ea8bc7a2b204cf65b515e8155ca0e03651572dbb65659537be1dd194d"),
}
RESEARCH_FILES_DIGEST = "e08d4824ea7aa8938f6731f4332e7007d7357bf30b318cce39ffff13f72b5558"
RESEARCH_LABELS = ("RESEARCH_RECORD",)


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


_REC = "RESEARCH_RECORD"
# D/s03_unitarity.json, section "witness": Monte Carlo (n = 2000 Gaussian samples) of the same singlet-channel matrix
# with the candidate's SosFormPotential(quartic_only=True) evaluator; blocks (Phi, H, Sigma, S, Phi17).
MC_M = (
    (-1083.823557780308, -38.85149581601002, -56.132098811535705, 5.525246939983952e-13, 3.514386861102625e-13),
    (-38.85149581601002, -43.66240813216283, -0.0, 1.8256334036598845e-15, 6.337054410780945e-15),
    (-56.132098811535705, -0.0, -37.14924881778186, -2.2273750132705633e-14, -4.379086532529049e-14),
    (5.525246939983952e-13, 1.8256334036598845e-15, -2.2273750132705633e-14, -3.8740142491992176, 5.551115123125783e-17),
    (3.514386861102625e-13, 6.337054410780945e-15, -4.379086532529049e-14, 5.551115123125783e-17, -0.11447411134569763),
)
MC_M_ERR = (
    (4.636612043220145, 15.224911980504242, 4.4403835603406945, 47.52014033491435, 47.51140000112703),
    (15.224911980504242, 0.6466266552262339, 0.6339208278616786, 2.0732325907443276, 2.045624216490511),
    (4.4403835603406945, 0.6339208278616786, 0.14956058043621404, 1.686710524448506, 1.6790554618344713),
    (47.52014033491435, 2.0732325907443276, 1.686710524448506, 0.17760055322972945, 0.18037666595655275),
    (47.51140000112703, 2.045624216490511, 1.6790554618344713, 0.18037666595655275, 0.005416995334914935),
)
RESEARCH_RECORD = {
    "mc_singlet_matrix": _record(
        _REC, [list(row) for row in MC_M],
        "Monte Carlo singlet-channel matrix M (blocks Phi, H, Sigma, S, Phi17) of the committed witness", S03_JSON, "witness.M_singlet",
    ),
    "mc_singlet_matrix_error": _record(
        _REC, [list(row) for row in MC_M_ERR], "one-sigma Monte Carlo errors of M", S03_JSON, "witness.M_err",
    ),
    "mc_eigenvalues": _record(
        _REC, [-1088.2661300172745, -42.72277806671984, -33.64630664625787, -3.8740142491992176, -0.11447411134569774],
        "eigenvalues of the Monte Carlo matrix", S03_JSON, "witness.eigs",
    ),
    "mc_a0_max": _record(_REC, 21.650366748967063, "max |eig|/(16 pi) of the Monte Carlo matrix", S03_JSON, "witness.a0_max"),
    "mc_samples": _record(_REC, 2000, "Gaussian samples per block combination", S03_JSON, "witness.n_mc"),
    "sigma_self_a0_exact": _record(
        _REC, 0.7391556997111044, "Sigma self channel a0 = sum_q dim_q w_q/(252 x 16 pi) at w = (2, 2, 1, 17/16)", S03_JSON,
        "witness.a0_sigma_exact",
    ),
    "sigma_self_M_SS_exact": _record(_REC, -37.154017857142854, "Sigma self entry M_SS", S03_JSON, "witness.M_SS_exact"),
    "verify_sigma_channel_formula": _record(
        _REC, "a0_Sigma = sum_q d_q w_q / (252 * 16 pi); the witness value is 0.739",
        "the physics verifier's derivation of the Sigma singlet entry (quoted)", VERIFY_MD, "SO(10) Sigma-singlet channel",
    ),
    "synthesis_witness_a0": _record(
        _REC, "The committed witness has a0 ~ 21.6 in the 210 singlet channel, so the benchmark itself is non-perturbative.",
        "rescue-study statement (quoted with ASCII '~' for the approximate sign)", SYNTHESIS_MD, "section 1, route D verifier corrections",
    ),
    "synthesis_pr4_rescale_line": _record(
        _REC, "Rescale the 210 block by 0.02 or less.",
        "PR-4 plan line, corrected here: rescaling the 210 block (T_Phi) alone by 1/50 leaves a0_max = 1.98",
        SYNTHESIS_MD, "section 4, PR-4",
    ),
    "final_g6_row": _record(
        _REC, "perturbative unitarity is unknown (the witness normalization had a0 ~ 21.6)",
        "final adjudication, redesign-track G6 row (quoted with ASCII '~')", FINAL_MD, "section 3 table, G6",
    ),
}


def research_files_digest(files: Mapping[str, tuple[str, str]] | None = None) -> str:
    table = RESEARCH_FILES if files is None else files
    payload = json.dumps({name: list(entry) for name, entry in table.items()}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Serialisation.
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    return candidate._jsonable(value)


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _fraction(value: Any) -> Fraction:
    rational = sympy.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


# ---------------------------------------------------------------------------
# (A) Method lemmas (sympy).
# ---------------------------------------------------------------------------


def _laplacian(expression: Any, variables: Sequence[Any]) -> Any:
    return sum((sympy.diff(expression, variable, 2) for variable in variables), sympy.Integer(0))


def _isserlis(exponents: Sequence[int]) -> Fraction:
    """E[prod x_i^a_i] for independent standard normals: prod (a_i - 1)!!, zero if an exponent is odd."""
    value = 1
    for exponent in exponents:
        if exponent % 2:
            return Fraction(0)
        value *= math.prod(range(exponent - 1, 0, -2))
    return Fraction(value)


@lru_cache(maxsize=1)
def gaussian_moment_section() -> dict[str, Any]:
    """E[P4] = (1/8) Lap^2 P4 on every quartic monomial in 3 variables; E[P_AB] = (1/4) Lap_A Lap_B P_AB on every
    monomial quadratic in (a0, a1) and in (b0, b1).  Exact (sympy and Isserlis)."""
    xs = sympy.symbols("x0:3", real=True)
    self_rows = []
    for exponents in itertools.product(range(5), repeat=3):
        if sum(exponents) != 4:
            continue
        monomial = sympy.Mul(*(variable**power for variable, power in zip(xs, exponents)))
        laplace = _fraction(_laplacian(_laplacian(monomial, xs), xs) / 8)
        self_rows.append(laplace == _isserlis(exponents))
    a = sympy.symbols("a0:2", real=True)
    b = sympy.symbols("b0:2", real=True)
    mixed_rows = []
    for ea in itertools.product(range(3), repeat=2):
        for eb in itertools.product(range(3), repeat=2):
            if sum(ea) != 2 or sum(eb) != 2:
                continue
            monomial = sympy.Mul(*(v**p for v, p in zip(a + b, ea + eb)))
            laplace = _fraction(_laplacian(_laplacian(monomial, a), b) / 4)
            mixed_rows.append(laplace == _isserlis(ea + eb))
    return {
        "self_identity": "E[P4] = (1/8) Lap^2 P4 for x ~ N(0, I)",
        "mixed_identity": "E[P_AB] = (1/4) Lap_A Lap_B P_AB for P quadratic in x_A and in x_B",
        "self_monomials_checked": len(self_rows),
        "mixed_monomials_checked": len(mixed_rows),
        "self_all_equal": bool(self_rows) and all(self_rows),
        "mixed_all_equal": bool(mixed_rows) and all(mixed_rows),
    }


@lru_cache(maxsize=1)
def lqt_calibration() -> dict[str, Any]:
    """V = lambda (H^dag H)^2 on a complex doublet (4 canonical reals): M = -(4/n) E[V] = -6 lambda, a0 = 3 lambda/(8 pi)."""
    lam = sympy.Symbol("lambda", positive=True)
    q = sympy.symbols("q0:4", real=True)
    n_h = sum((v**2 for v in q), sympy.Integer(0)) / 2
    potential = lam * n_h**2
    expectation = sympy.expand(_laplacian(_laplacian(potential, q), q) / 8)
    entry = sympy.simplify(-sympy.Rational(4, 4) * expectation)
    a0 = sympy.simplify(-entry / (16 * sympy.pi))
    return {
        "potential": "lambda (H^dag H)^2, H a complex doublet, H^dag H = |q|^2/2 (4 canonical reals)",
        "expectation": str(expectation),
        "M_entry": str(entry),
        "a0": str(a0),
        "a0_equals_3_lambda_over_8_pi": bool(sympy.simplify(a0 - 3 * lam / (8 * sympy.pi)) == 0),
        "reference": "the standard Lee-Quigg-Thacker value 3 lambda/(8 pi) (calibration; the paper is not re-read here)",
    }


@lru_cache(maxsize=1)
def h_self_section() -> dict[str, Any]:
    """alpha of I_1 = |H.H|^2/10, I_54 = sum_ij |H_i H_j - delta_ij H.H/10|^2 and N_H^2 in the 20-real chart
    H_i = (x_i + i y_i)/sqrt(2) (sympy, QQ polynomials); the identity I_1 + I_54 = N_H^2; and the trace of the Hessian
    at two unit vectors (block invariance of Lap V4_H)."""
    xs = sympy.symbols("hx0:10", real=True)
    ys = sympy.symbols("hy0:10", real=True)
    generators = [variable for pair in zip(xs, ys) for variable in pair]
    half = sympy.Rational(1, 2)

    def poly(expression: Any) -> sympy.Poly:
        return sympy.Poly(expression, *generators, domain="QQ")

    def pair(i: int, j: int) -> tuple[Any, Any]:
        return half * (xs[i] * xs[j] - ys[i] * ys[j]), half * (xs[i] * ys[j] + ys[i] * xs[j])

    hh_re = sum((pair(i, i)[0] for i in range(10)), sympy.Integer(0))
    hh_im = sum((pair(i, i)[1] for i in range(10)), sympy.Integer(0))
    i_1 = (poly(hh_re) ** 2 + poly(hh_im) ** 2) * sympy.Rational(1, 10)
    i_54 = poly(0)
    for i in range(10):
        for j in range(10):
            real, imaginary = pair(i, j)
            if i == j:
                real = real - hh_re / 10
                imaginary = imaginary - hh_im / 10
            i_54 += poly(real) ** 2 + poly(imaginary) ** 2
    n_h = poly(half * sum((x * x + y * y for x, y in zip(xs, ys)), sympy.Integer(0)))
    identity_zero = (i_1 + i_54 - n_h**2).is_zero

    def lap(p: sympy.Poly) -> sympy.Poly:
        output = poly(0)
        for generator in generators:
            output += p.diff(generator).diff(generator)
        return output

    vectors = (
        {xs[0]: sympy.Integer(1)},
        {xs[0]: sympy.Rational(3, 5), ys[3]: sympy.Rational(4, 5)},
    )
    output: dict[str, Any] = {}
    invariant = True
    for name, polynomial in (("I_1", i_1), ("I_54", i_54), ("N_H^2", n_h**2)):
        first = lap(polynomial)
        alpha = _fraction(lap(first).as_expr() / (2 * len(generators)))
        traces = []
        for vector in vectors:
            point = {generator: vector.get(generator, sympy.Integer(0)) for generator in generators}
            traces.append(_fraction(first.as_expr().subs(point)))
        invariant = invariant and all(value == alpha for value in traces)
        output[name] = {"alpha": alpha, "hessian_trace_at_test_unit_vectors": traces}
    return {
        "chart": "H_i = (x_i + i y_i)/sqrt(2), 20 canonical reals",
        "definitions": "I_1 = |H.H|^2/10, I_54 = sum_ij |H_i H_j - delta_ij H.H/10|^2 (exact_h10_self_quartic_family_v20)",
        "identity_I1_plus_I54_equals_NH_squared": bool(identity_zero),
        "per_channel": output,
        "alpha_by_channel": {name: output[name]["alpha"] for name in output},
        "trace_equals_alpha_at_test_unit_vectors": bool(invariant),
        "test_unit_vectors": ["x_0", "(3/5) x_0 + (4/5) y_3"],
        "alpha_H_formula": "alpha_H = alpha(I_1) O36_B01 + alpha(I_54) O36_B02 = 22 lambda_H at O36_B01 = O36_B02 = lambda_H",
    }


# ---------------------------------------------------------------------------
# (A) Unit classification at q0 (exact).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def block_of_index() -> tuple[str, ...]:
    output = [""] * TOTAL_DIM
    for name, block in BLOCK_SLICES.items():
        for index in range(block.start, block.stop):
            output[index] = name
    return tuple(output)


def vacuum_u(r0: Fraction = R0, x0: Fraction = X0, *, rs: Fraction | None = None) -> tuple[np.ndarray, int]:
    """u0 = (p, 0, (r0/4) sigma_std raw, (rS, 0), (x0, 0)) as an integer object vector over a common denominator L."""
    tensors = hessian.source_tensors()
    rho = Fraction(r0) / 4
    s = Fraction(r0 if rs is None else rs)
    x = Fraction(x0)
    common = math.lcm(rho.denominator, s.denominator, x.denominator)
    output = np.zeros(TOTAL_DIM, dtype=object)
    output[...] = 0
    output[BLOCK_SLICES["Phi"]] = np.asarray(tensors["p"]).astype(object) * common
    output[BLOCK_SLICES["Sigma"]] = hessian._realvec(*tensors["s"]).astype(object) * int(rho * common)
    output[BLOCK_SLICES["S"]] = np.asarray([int(s * common), 0], dtype=object)
    output[BLOCK_SLICES["Phi17"]] = np.asarray([int(x * common), 0], dtype=object)
    return output, common


def chart_norms_at_q0(u0: np.ndarray, common: int) -> dict[str, Fraction]:
    """|q_B|^2 = sum_B D^2 u^2 (exact)."""
    return {
        name: Fraction(sum(int(value) ** 2 for value in u0[block]) * D_SQUARED[name], common * common)
        for name, block in BLOCK_SLICES.items()
    }


def unit_analysis(
    units: Sequence[Mapping[str, Any]],
    table: Mapping[str, tuple[int, str, tuple[str, ...]]],
    u0: np.ndarray,
    common: int,
    scaled_units: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Per unit: q-traces by block, block support, Euler degree test (nonzero gradient) or, for a zero gradient, the
    field-content classification with the exact vev-scaling test H(2 r0) = 2^e H(r0), e = (number of Sigma/S fields)
    - (Sigma/S derivatives of the Hessian block), and the exact value at q0."""
    blocks = block_of_index()
    scaled_by_name = {unit["name"]: unit for unit in scaled_units}
    output = {}
    for unit in units:
        name = unit["name"]
        num_h, den_h = unit["hessian"]
        num_g, den_g = unit["gradient"]
        entry = table.get(name)
        degree = entry[0] if entry else None
        rows, columns = np.nonzero(num_h != 0)
        support = sorted({(blocks[row], blocks[column]) for row, column in zip(rows.tolist(), columns.tolist())})
        traces = {
            block: Fraction(sum(int(num_h[i, i]) for i in range(sl.start, sl.stop)), int(den_h) * D_SQUARED[block])
            for block, sl in BLOCK_SLICES.items()
        }
        gradient_nonzero = any(int(value) for value in num_g.flat)
        record: dict[str, Any] = {
            "table": list(entry) if entry else None,
            "gradient_nonzero": gradient_nonzero,
            "support_blocks": [list(pair) for pair in support],
            "q_traces": {block: value for block, value in traces.items() if value},
        }
        if gradient_nonzero:
            ok = False
            value = None
            if degree:
                left = num_h.dot(u0) * int(den_g)
                right = num_g * ((degree - 1) * int(den_h) * common)
                ok = bool(np.array_equal(left, right))
                value = Fraction(int(u0.dot(num_g)), common * int(den_g) * degree)
            record.update({"classification": "Euler: H_u u0 = (d - 1) grad_u", "degree_certified": ok, "value_at_q0": value})
        else:
            content, token, block = ZERO_GRADIENT_FIELD_CONTENT.get(name, (None, None, None))
            scaled = scaled_by_name.get(name)
            scaling_ok = False
            exponent = None
            if content is not None and scaled is not None:
                derivatives = 2 if block in ("Sigma", "S") else 0
                exponent = sum(content.get(field, 0) for field in SCALED_FIELDS) - derivatives
                num_s, den_s = scaled["hessian"]
                factor = VEV_SCALING**exponent
                scaling_ok = bool(
                    exponent >= 0
                    and np.array_equal(num_s * (int(den_h) * factor.denominator), num_h * (int(den_s) * factor.numerator))
                )
            ok = bool(
                content is not None
                and degree == sum(content.values())
                and all(token in parameter for parameter in unit["weights"])
                and all(pair == (block, block) for pair in support)
                and scaling_ok
            )
            record.update(
                {
                    "classification": (
                        "zero gradient at q0: field content, block support and exact vev scaling H(2 r0) = 2^e H(r0)"
                    ),
                    "field_content": content,
                    "hessian_block": block,
                    "vev_scaling_exponent": exponent,
                    "degree_certified": ok,
                    "value_at_q0": Fraction(0),
                }
            )
        output[name] = record
    return output


def classification_checks(units: Sequence[Mapping[str, Any]], table: Mapping[str, tuple[int, str, tuple[str, ...]]], analysis: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    names = [unit["name"] for unit in units]
    euler_ok = all(row["degree_certified"] for row in analysis.values() if row["gradient_nonzero"])
    zero_ok = all(row["degree_certified"] for row in analysis.values() if not row["gradient_nonzero"])
    supports_ok = True
    no_singlet_portal = True
    for name, (degree, kind, blocks) in table.items():
        row = analysis.get(name)
        if row is None or degree != 4:
            continue
        support = {tuple(pair) for pair in row["support_blocks"]}
        if kind == "self":
            supports_ok = supports_ok and support <= {(blocks[0], blocks[0])} and bool(row["q_traces"].get(blocks[0]))
        elif kind == "self_analytic":
            supports_ok = supports_ok and not support
        elif kind == "mixed":
            allowed = {(a, b) for a in blocks for b in blocks}
            supports_ok = supports_ok and support <= allowed
            no_singlet_portal = no_singlet_portal and not ({"S", "Phi17"} & set(blocks))
        else:
            supports_ok = False
    return {
        "unit_list_equals_classification_table": len(names) == len(set(names)) and set(names) == set(table),
        "euler_degree_matches_table_for_every_unit_with_nonzero_gradient": euler_ok,
        "zero_gradient_units_classified_by_field_content_and_exact_vev_scaling": zero_ok,
        "quartic_unit_supports_within_declared_blocks_and_no_S_or_Phi17_portal": bool(supports_ok and no_singlet_portal),
    }


# ---------------------------------------------------------------------------
# (A)/(B) The singlet-channel matrix from a coefficient map.
# ---------------------------------------------------------------------------


def singlet_channel(
    coefficients: Mapping[str, Fraction],
    units: Sequence[Mapping[str, Any]],
    table: Mapping[str, tuple[int, str, tuple[str, ...]]],
    analysis: Mapping[str, Mapping[str, Any]],
    alpha_h_channels: Mapping[str, Fraction],
    norms: Mapping[str, Fraction],
    *,
    dims: Mapping[str, int] | None = None,
    alpha_overrides: Mapping[str, Fraction] | None = None,
) -> dict[str, Any]:
    dims = dict(BLOCK_DIMS if dims is None else dims)
    coverage = hessian.unit_coefficients(units, coefficients)
    scalars = coverage["unit_coefficients"]
    alpha = {block: Fraction(0) for block in BLOCKS}
    measured: dict[str, Fraction] = {}
    partner_trace_zero = True
    for unit in units:
        name = unit["name"]
        entry = table.get(name)
        scalar = scalars.get(name, Fraction(0))
        if entry is None or entry[0] != 4 or scalar == 0:
            continue
        _, kind, blocks = entry
        traces = analysis[name]["q_traces"]
        if kind == "self":
            alpha[blocks[0]] += scalar * traces.get(blocks[0], Fraction(0)) / norms[blocks[0]]
        elif kind == "self_analytic":
            alpha[blocks[0]] += scalar * alpha_h_channels[O36_CHANNEL_BY_UNIT[name]]
        elif kind == "mixed":
            first, second = blocks
            if norms[second]:
                key = f"{first}|{second}"
                measured[key] = measured.get(key, Fraction(0)) + scalar * traces.get(first, Fraction(0)) / norms[second]
            if norms[first]:
                key = f"{second}|{first}"
                measured[key] = measured.get(key, Fraction(0)) + scalar * traces.get(second, Fraction(0)) / norms[first]
            elif traces.get(second, Fraction(0)) != 0:
                partner_trace_zero = False
    for block, value in (alpha_overrides or {}).items():
        alpha[block] = Fraction(value)
    index = {block: position for position, block in enumerate(BLOCKS)}
    e_matrix = [[Fraction(0)] * len(BLOCKS) for _ in BLOCKS]
    for block in BLOCKS:
        e_matrix[index[block]][index[block]] = dims[block] * alpha[block] / 4
    beta: dict[str, Fraction] = {}
    consistency: dict[str, list[Fraction]] = {}
    done = set()
    for key in sorted(measured):
        first, second = key.split("|")
        pair = frozenset((first, second))
        if pair in done:
            continue
        done.add(pair)
        forward = measured.get(f"{first}|{second}")
        backward = measured.get(f"{second}|{first}")
        if forward is not None and backward is not None:
            consistency[f"{first},{second}"] = [dims[second] * forward, dims[first] * backward]
        value = dims[second] * forward / 4 if forward is not None else dims[first] * backward / 4
        e_matrix[index[first]][index[second]] = e_matrix[index[second]][index[first]] = value
        beta[f"{first}|{second}"] = 4 * value / dims[second]
        beta[f"{second}|{first}"] = 4 * value / dims[first]
    rational = [[-4 * e_matrix[i][j] / dims[BLOCKS[i]] for j in range(len(BLOCKS))] for i in range(len(BLOCKS))]
    return {
        "dims": dims,
        "alpha": alpha,
        "beta_measured": measured,
        "beta": beta,
        "consistency": consistency,
        "E": e_matrix,
        "minus_4_Ninv_E": rational,
        "zero_vev_partner_traces_vanish": partner_trace_zero,
        "coverage_ok": bool(
            coverage["coefficients_proportional_to_unit_weights"]
            and coverage["every_nonzero_parameter_covered"]
            and coverage["no_parameter_in_two_units"]
        ),
    }


def symmetric_matrix_float(channel: Mapping[str, Any]) -> np.ndarray:
    dims = channel["dims"]
    e_matrix = channel["E"]
    size = len(BLOCKS)
    return np.array(
        [[-4.0 * float(e_matrix[i][j]) / math.sqrt(dims[BLOCKS[i]] * dims[BLOCKS[j]]) for j in range(size)] for i in range(size)]
    )


def _shifted(e_matrix: Sequence[Sequence[Fraction]], dims: Mapping[str, int], bound: Fraction, sign: int) -> list[list[Fraction]]:
    size = len(BLOCKS)
    return [
        [(bound / 4) * dims[BLOCKS[i]] * (1 if i == j else 0) + sign * e_matrix[i][j] for j in range(size)] for i in range(size)
    ]


def spectral_radius_below(e_matrix: Sequence[Sequence[Fraction]], dims: Mapping[str, int], bound: Fraction) -> bool:
    """max |eig M| < bound  <=>  (bound/4) N +- E are positive definite (exact inertia; M = -4 N^-1/2 E N^-1/2)."""
    for sign in (1, -1):
        inertia = hessian.exact_inertia(_shifted(e_matrix, dims, bound, sign))
        if inertia["positive"] != len(BLOCKS):
            return False
    return True


def spectral_radius_above(e_matrix: Sequence[Sequence[Fraction]], dims: Mapping[str, int], bound: Fraction) -> bool:
    """max |eig M| > bound  <=>  (bound/4) N + E or (bound/4) N - E is not positive semidefinite (exact inertia)."""
    return any(hessian.exact_inertia(_shifted(e_matrix, dims, bound, sign))["negative"] > 0 for sign in (1, -1))


def _scaled(e_matrix: Sequence[Sequence[Fraction]], factor: Fraction) -> list[list[Fraction]]:
    return [[factor * value for value in row] for row in e_matrix]


def _a0_float(channel: Mapping[str, Any]) -> tuple[float, list[float]]:
    eigenvalues = np.linalg.eigvalsh(symmetric_matrix_float(channel))
    return float(np.max(np.abs(eigenvalues)) / (16.0 * math.pi)), [float(value) for value in eigenvalues]


# ---------------------------------------------------------------------------
# (B) The committed witness.
# ---------------------------------------------------------------------------


def witness_section(channel: Mapping[str, Any], coefficients: Mapping[str, Fraction], units: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, bool], dict[str, Any]]:
    dims = channel["dims"]
    alpha = channel["alpha"]
    beta = channel["beta"]
    measured = channel["beta_measured"]
    checks: dict[str, bool] = {}
    checks["singlet_alphas_equal_pinned_exact_values"] = alpha == EXPECTED_ALPHA
    checks["singlet_betas_equal_pinned_exact_values"] = bool(
        set(measured) == set(MEASURED_PAIRS) and all(beta.get(key) == value for key, value in EXPECTED_BETA.items())
    )
    consistency = channel["consistency"].get("Phi,Sigma")
    checks["phi_sigma_consistency_n_Sigma_beta_equals_n_Phi_beta_equals_12915"] = bool(
        consistency is not None and consistency[0] == consistency[1] == EXPECTED_PHI_SIGMA_CONSISTENCY
    )
    # Independent exact cross-checks of two entries.
    q_h = hessian.h_wedge_data()["Q_H"]
    wedge_scalar = hessian.unit_coefficients(units, coefficients)["unit_coefficients"]["O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H"]
    beta_h_phi_closed = wedge_scalar * 2 * int(np.trace(q_h))
    weights = candidate.SWAPPED_SELF_WEIGHTS
    channel_dims = {name: int(re.match(r"\d+", name).group(0)) for name in candidate.SELF_CHANNELS}
    alpha_sigma_closed = 8 * T * sum((weights[name] * channel_dims[name] for name in candidate.SELF_CHANNELS), Fraction(0)) / chart.SIGMA_REAL_DIM
    checks["beta_H_Phi_equals_two_trace_Q_H_of_the_wedge_square"] = bool(beta.get("H|Phi") == beta_h_phi_closed == Fraction(12))
    checks["alpha_Sigma_equals_dimension_weighted_channel_sum"] = bool(
        sum(channel_dims.values()) == chart.SIGMA_COMPLEX_DIM * (chart.SIGMA_COMPLEX_DIM + 1) // 2
        and alpha["Sigma"] == alpha_sigma_closed
    )
    e_matrix = channel["E"]
    zero_pairs = all(
        e_matrix[i][j] == 0
        for i in range(len(BLOCKS))
        for j in range(len(BLOCKS))
        if i != j and {BLOCKS[i], BLOCKS[j]} not in ({"Phi", "Sigma"}, {"Phi", "H"})
    )
    checks["every_other_pair_zero_S_and_Phi17_decouple"] = bool(zero_pairs and channel["zero_vev_partner_traces_vanish"])
    rational = channel["minus_4_Ninv_E"]
    block3 = tuple(tuple(rational[i][j] for j in range(3)) for i in range(3))
    checks["rational_matrix_Phi_H_Sigma_block_equals_pinned"] = block3 == EXPECTED_RATIONAL_BLOCK
    lam = sympy.Symbol("lam")
    full = sympy.Matrix([[sympy.Rational(value.numerator, value.denominator) for value in row] for row in rational])
    cubic = sympy.Matrix(3, 3, lambda i, j: full[i, j]).charpoly(lam).as_expr()
    factorised = sympy.expand(
        full.charpoly(lam).as_expr() - (lam - full[3, 3]) * (lam - full[4, 4]) * cubic
    ) == 0 and all(full[i, j] == 0 for i in range(5) for j in range(5) if i != j and (i >= 3 or j >= 3))
    checks["characteristic_polynomial_factorises_with_pinned_cubic"] = bool(factorised and str(cubic) == EXPECTED_CUBIC)
    lower_21 = 16 * 21 * PI_UPPER
    upper_22 = 16 * 22 * PI_LOWER
    checks["a0_max_between_21_and_22_exact"] = bool(
        spectral_radius_above(e_matrix, dims, lower_21) and spectral_radius_below(e_matrix, dims, upper_22)
    )
    intervals = sympy.Poly(cubic, lam).intervals(eps=sympy.Rational(ISOLATING_INTERVAL_WIDTH.numerator, ISOLATING_INTERVAL_WIDTH.denominator))
    roots = sorted(((Fraction(int(a.p), int(a.q)), Fraction(int(b.p), int(b.q))) for (a, b), _ in intervals), key=lambda pair: pair[0])
    lowest = roots[0] if roots else (Fraction(0), Fraction(0))
    others = [-full[3, 3], -full[4, 4]]
    radius_interval = (-lowest[1], -lowest[0])
    a0_interval = (radius_interval[0] / (16 * PI_UPPER), radius_interval[1] / (16 * PI_LOWER))
    checks["largest_root_isolated_exactly_and_a0_enclosed"] = bool(
        len(roots) == 3
        and all(b - a <= ISOLATING_INTERVAL_WIDTH for a, b in roots)
        and radius_interval[0] > max(_fraction(value) for value in others)
        and all(b < 0 for _, b in roots)
        and Fraction(2164, 100) < a0_interval[0] < a0_interval[1] < Fraction(2166, 100)
    )
    per_block = {block: alpha[block] for block in BLOCKS}
    checks["committed_Phi_H_Sigma_self_entries_exceed_half_S_Phi17_below_exact"] = bool(
        all(per_block[block] > HALF_BOUND_ABOVE for block in ("Phi", "H", "Sigma"))
        and all(per_block[block] < HALF_BOUND_BELOW for block in ("S", "Phi17"))
    )
    index = {block: position for position, block in enumerate(BLOCKS)}
    mixing_squared = {
        f"{a}-{b}": 16 * e_matrix[index[a]][index[b]] ** 2 / (dims[a] * dims[b]) for a, b in (("Phi", "Sigma"), ("Phi", "H"))
    }
    checks["committed_Phi_Sigma_and_Phi_H_mixings_exceed_the_bound_exact"] = all(
        value > HALF_BOUND_ABOVE**2 for value in mixing_squared.values()
    )
    a0_max, eigenvalues = _a0_float(channel)
    numeric_roots = sorted(float(value) for value in sympy.Poly(cubic, lam).nroots(n=30)) + [float(value) for value in (full[3, 3], full[4, 4])]
    num_ok = bool(
        len(eigenvalues) == 5
        and all(
            abs(a - b) <= NUM_EIGENVALUE_REL_TOLERANCE * max(1.0, abs(b)) for a, b in zip(sorted(eigenvalues), sorted(numeric_roots))
        )
        and float(radius_interval[0]) <= -min(eigenvalues) * (1 + NUM_EIGENVALUE_REL_TOLERANCE)
        and -min(eigenvalues) <= float(radius_interval[1]) * (1 + NUM_EIGENVALUE_REL_TOLERANCE)
    )
    checks["num_eigenvalues_consistent_with_exact_characteristic_polynomial"] = num_ok
    record = {
        "label": "EXACT (matrix, characteristic polynomial, enclosures); NUM (float eigenvalues, a0 values)",
        "alpha": alpha,
        "beta_measured_at_q0": measured,
        "beta": beta,
        "phi_sigma_consistency": {"n_Sigma_beta_Phi_Sigma": consistency[0] if consistency else None, "n_Phi_beta_Sigma_Phi": consistency[1] if consistency else None},
        "beta_H_Phi_closed_form": "2 Tr Q_H(p), Q_H = diag(1^6, 0^4) (hessian.h_wedge_data): %s" % beta_h_phi_closed,
        "alpha_Sigma_closed_form": "8 t sum_q w_q dim_q / 252 with dims (54, 1050, 2772, 4125), w = (2, 2, 1, 17/16): %s" % alpha_sigma_closed,
        "E": channel["E"],
        "minus_4_Ninv_E": rational,
        "characteristic_polynomial": {
            "full": str(sympy.factor(full.charpoly(lam).as_expr())),
            "cubic_Phi_H_Sigma": str(cubic),
            "decoupled_roots": {"S": -others[0], "Phi17": -others[1]},
        },
        "largest_root_isolating_interval": [lowest[0], lowest[1]],
        "max_abs_eigenvalue_interval": list(radius_interval),
        "a0_max_exact_enclosure": list(a0_interval),
        "a0_max_exact_enclosure_float": [float(a0_interval[0]), float(a0_interval[1])],
        "a0_max_between": (
            "21 < a0_max < 22: (16 x 21 x 22/7) N/4 +- E is not positive semidefinite for one sign and "
            "(16 x 22 x 333/106) N/4 +- E is positive definite for both signs (exact inertia)"
        ),
        "mixing_entries_squared": mixing_squared,
        "per_block_self_a0": {block: float(alpha[block]) / (16.0 * math.pi) for block in BLOCKS},
        "per_block_labels": {"Phi": "210 singlet channel", "H": "10_H singlet", "Sigma": "126bar singlet", "S": "S", "Phi17": "Phi17"},
        "M_symmetric_float": symmetric_matrix_float(channel).tolist(),
        "eigenvalues_float": eigenvalues,
        "a0_max_float": a0_max,
        "nonperturbative": "every self entry of Phi, H and Sigma and both nonzero mixings exceed |a0| = 1/2 by themselves",
    }
    return record, checks, {"cubic": cubic, "a0_interval": a0_interval}


# ---------------------------------------------------------------------------
# (C) Rescaling lemma.
# ---------------------------------------------------------------------------


def sos_terms(r0: Any = R0, x0: Any = X0, kappa: Any = KAPPA, *, rs: Any | None = None) -> dict[str, dict[str, Any]]:
    """The seven SOS terms as parameter groups of candidate.expanded_sos_coefficient_map (exact or sympy)."""
    scale = r0 if rs is None else rs
    t = T
    return {
        "T_Phi": {O07_ID: Fraction(-2), **{O48_IDS[i]: phi_source.EXPECTED_J_COUPLINGS[name] for i, name in enumerate(J_NAMES)}},
        "A_square": {
            **{O44_IDS[j]: t * weight for j, weight in enumerate(a_square_source.EXPECTED_WEIGHTS)},
            O14_ID: -4 * t,
            O05_ID: 4 * t,
        },
        "C_square": {O44_IDS[j]: t * weight for j, weight in enumerate(sos_source.C_SQUARE_WEIGHTS)},
        "W": {
            **{SELF_IDS[channel]: t * candidate.SWAPPED_SELF_WEIGHTS[channel] for channel in candidate.SELF_CHANNELS},
            O05_ID: -t * candidate.RADIAL_COEFFICIENT * r0 * r0,
        },
        "T_HS": {
            O36_IDS[0]: Fraction(2),
            O36_IDS[1]: Fraction(2),
            O06_ID: 2 * abs(kappa) * scale,
            O12_ID: kappa,
            O04_ID: -2 * scale * scale,
            O23_ID: Fraction(1),
        },
        "T_HPhi": {O46_1_ID: Fraction(3, 5), O46_54_ID: Fraction(-1)},
        "T_X": {O03_ID: -x0 * x0 / 16, O20_ID: Fraction(1, 32)},
    }


def term_minima(r0: Any = R0, x0: Any = X0, *, rs: Any | None = None) -> dict[str, Any]:
    scale = r0 if rs is None else rs
    return {
        "T_Phi": -1,
        "A_square": 0,
        "C_square": 0,
        "W": -T * r0**4,
        "T_HS": -(scale**4),
        "T_HPhi": 0,
        "T_X": -(x0**4) / 32,
    }


def member_map(terms: Mapping[str, Mapping[str, Any]], scales: Mapping[str, Fraction]) -> dict[str, Fraction]:
    output: dict[str, Fraction] = {}
    for name, term in terms.items():
        factor = Fraction(scales.get(name, Fraction(1)))
        for parameter, value in term.items():
            output[parameter] = output.get(parameter, Fraction(0)) + factor * Fraction(value)
    return {key: value for key, value in output.items() if value != 0}


def term_groups(terms: Mapping[str, Mapping[str, Any]], units: Sequence[Mapping[str, Any]]) -> list[tuple[str, ...]]:
    """Finest grouping of terms such that every unit is proportional to its weights within each group (union-find):
    a unit whose parameters two terms share with non-proportional weights merges them (O44: A_square + C_square)."""
    parent = {name: name for name in terms}

    def root(name: str) -> str:
        while parent[name] != name:
            name = parent[name]
        return name

    for unit in units:
        touching = [name for name in terms if any(parameter in terms[name] for parameter in unit["weights"])]
        if len(touching) < 2:
            continue
        proportional = all(
            len({Fraction(terms[name].get(parameter, 0)) / weight for parameter, weight in unit["weights"].items()}) == 1
            for name in touching
        )
        if not proportional:
            base = root(touching[0])
            for name in touching[1:]:
                parent[root(name)] = base
    groups: dict[str, list[str]] = {}
    for name in terms:
        groups.setdefault(root(name), []).append(name)
    return [tuple(members) for members in groups.values()]


def _assemble(units: Sequence[Mapping[str, Any]], coefficients: Mapping[str, Fraction], analysis: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    coverage = hessian.unit_coefficients(units, coefficients)
    scalars = coverage["unit_coefficients"]
    hessian_terms = []
    gradient_terms = []
    value = Fraction(0)
    for unit in units:
        scalar = scalars[unit["name"]]
        if scalar == 0:
            continue
        numerator, denominator = unit["hessian"]
        hessian_terms.append((scalar / denominator, numerator))
        numerator, denominator = unit["gradient"]
        gradient_terms.append((scalar / denominator, numerator))
        unit_value = analysis[unit["name"]]["value_at_q0"]
        value += scalar * (unit_value if unit_value is not None else Fraction(0))
    return {
        "hessian": hessian.combine(hessian_terms, (TOTAL_DIM, TOTAL_DIM)),
        "gradient": hessian.combine(gradient_terms, (TOTAL_DIM,)),
        "value": value,
        "proportional": bool(coverage["coefficients_proportional_to_unit_weights"]),
    }


def lemma_section(
    terms: Mapping[str, Mapping[str, Any]],
    units: Sequence[Mapping[str, Any]],
    analysis: Mapping[str, Mapping[str, Any]],
    u0: np.ndarray,
) -> tuple[dict[str, Any], dict[str, bool]]:
    checks: dict[str, bool] = {}
    # (1) partition, symbolic in r0, x0, kappa < 0.
    r, x = sympy.symbols("r0 x0", positive=True)
    k = sympy.Symbol("kappa", negative=True)
    symbolic_terms = sos_terms(r, x, k)
    summed: dict[str, Any] = {}
    for term in symbolic_terms.values():
        for parameter, value in term.items():
            summed[parameter] = summed.get(parameter, 0) + value
    expanded = candidate.expanded_sos_coefficient_map(r, x, k)
    committed = candidate.candidate_coefficients(r, x, k)
    keys = sorted(set(summed) | set(expanded) | set(committed))
    residuals = {
        key: (
            sympy.simplify(candidate._as_sympy(summed.get(key, 0)) - candidate._as_sympy(expanded.get(key, 0))),
            sympy.simplify(candidate._as_sympy(summed.get(key, 0)) - candidate._as_sympy(committed.get(key, 0))),
        )
        for key in keys
    }
    checks["sos_term_partition_sums_to_committed_map_symbolically"] = bool(
        list(symbolic_terms) == list(TERM_NAMES) and all(a == 0 and b == 0 for a, b in residuals.values()) and len(keys) == candidate.EXPECTED_NONZERO
    )
    witness_map = member_map(terms, {})
    checks["sos_term_partition_equals_benchmark_coefficients_at_witness"] = witness_map == hessian.benchmark_coefficients()
    # (2) linear identity with symbolic scalings.
    scale_symbols = {name: sympy.Symbol(f"s_{name}", positive=True) for name in TERM_NAMES}
    operators = {key: sympy.Symbol("O[" + key + "]") for key in keys}
    scaled_map: dict[str, Any] = {}
    for name, term in symbolic_terms.items():
        for parameter, value in term.items():
            scaled_map[parameter] = scaled_map.get(parameter, 0) + scale_symbols[name] * candidate._as_sympy(value)
    potential = sum((scaled_map[key] * operators[key] for key in scaled_map), sympy.Integer(0))
    by_terms = sum(
        (scale_symbols[name] * sum((candidate._as_sympy(value) * operators[p] for p, value in term.items()), sympy.Integer(0)) for name, term in symbolic_terms.items()),
        sympy.Integer(0),
    )
    identity_residual = sympy.expand(potential - by_terms)
    minima = term_minima(r, x)
    v0_scaled = sum((scale_symbols[name] * minima[name] for name in TERM_NAMES), sympy.Integer(0))
    at_one = {symbol: 1 for symbol in scale_symbols.values()}
    v0_residual = sympy.simplify(v0_scaled.subs(at_one) - candidate.lower_bound_v0(r, x))
    map_at_one = all(sympy.simplify(scaled_map[key].subs(at_one) - candidate._as_sympy(committed.get(key, 0))) == 0 for key in scaled_map)
    checks["scaled_map_and_V0_linear_identity_sympy_residual_zero"] = bool(identity_residual == 0 and v0_residual == 0 and map_at_one)
    # (3) kappa margin under the T_HS scaling.
    s = sympy.Symbol("s", positive=True)
    hs = symbolic_terms["T_HS"]
    margin = 4 * (s * hs[O36_IDS[0]]) * (s * hs[O23_ID]) * r**2 - (s * k) ** 2
    committed_margin = 4 * r**2 - k**2 / 2
    margin_ok = sympy.expand(margin - s**2 * (8 * r**2 - k**2)) == 0 and sympy.expand(margin.subs(s, 1) - 2 * committed_margin) == 0
    checks["kappa_margin_scale_invariant_under_T_HS_scaling_sympy"] = bool(margin_ok)
    # (4) per-group stationarity, PSD and values at q0 (exact, at the witness).
    groups = term_groups(terms, units)
    group_rows = {}
    stationary = True
    psd = True
    values_ok = True
    proportional = True
    for members in groups:
        group_name = "+".join(members)
        coefficients = member_map({name: terms[name] for name in members}, {})
        assembled = _assemble(units, coefficients, analysis)
        numerator, denominator = assembled["hessian"]
        gradient_zero = not any(int(value) for value in assembled["gradient"][0].flat)
        inertia = hessian.component_inertia(numerator, denominator)
        expected = EXPECTED_TERM_GROUP_MINIMA.get(group_name)
        stationary = stationary and gradient_zero
        psd = psd and inertia["negative"] == 0
        values_ok = values_ok and expected is not None and assembled["value"] == expected
        proportional = proportional and assembled["proportional"]
        group_rows[group_name] = {
            "terms": list(members),
            "parameters": sorted(coefficients),
            "gradient_exactly_zero_at_q0": gradient_zero,
            "hessian_inertia_positive_negative_zero": [inertia["positive"], inertia["negative"], inertia["zero"]],
            "value_at_q0": assembled["value"],
            "expected_minimum": expected,
        }
    c_square_zero = hessian.phi_sigma_data()["C_p_sigma_std_max_abs"] == 0
    checks["every_unit_computable_term_group_stationary_at_q0_exact"] = bool(stationary and proportional)
    checks["every_unit_computable_term_group_hessian_psd_at_q0_exact"] = bool(psd and proportional)
    checks["term_group_values_at_q0_equal_committed_minima"] = bool(values_ok and c_square_zero)
    # (5) proper-subset scalings break stationarity.
    tensors = hessian.source_tensors()
    base = hessian.benchmark_coefficients()
    o48_only = {key: (SUBSET_SCALE * value if key in O48_IDS else value) for key, value in base.items()}
    o48 = _assemble(units, o48_only, analysis)
    grad_num, grad_den = o48["gradient"]
    expected_phi = np.zeros(TOTAL_DIM, dtype=object)
    expected_phi[...] = 0
    expected_phi[BLOCK_SLICES["Phi"]] = np.asarray(tensors["p"]).astype(object) * 4
    shift = SUBSET_SCALE - 1
    o48_ok = bool(
        np.array_equal(grad_num * shift.denominator, expected_phi * (shift.numerator * int(grad_den)))
        and any(int(value) for value in grad_num.flat)
    )
    o27_only = {key: (SUBSET_SCALE * value if key in O27_IDS else value) for key, value in base.items()}
    o27 = _assemble(units, o27_only, analysis)
    grad27, _ = o27["gradient"]
    blocks = block_of_index()
    o27_support = {blocks[i] for i in range(TOTAL_DIM) if int(grad27[i])}
    radial = int(u0.dot(grad27))
    o27_ok = bool(o27_support == {"Sigma"} and radial != 0)
    checks["proper_subset_scaling_O48_only_moves_Phi_radius_exact"] = o48_ok
    checks["proper_subset_scaling_O27_only_moves_Sigma_radius_exact"] = o27_ok
    record = {
        "label": "EXACT",
        "terms": {name: {"text": TERM_TEXT.get(name, "custom"), "parameters": {p: v for p, v in terms[name].items()}} for name in terms},
        "statement": (
            "For s_k > 0, V(s) = sum_k s_k T_k (parameter map c(s) = sum_k s_k c_k) satisfies V(s) - V0(s) = sum_k s_k "
            "(T_k - m_k) >= 0 with V0(s) = sum_k s_k m_k; {V(s) = V0(s)} = cap_k {T_k = m_k} = G.q0 (unchanged: every "
            "T_k attains m_k at q0); Hess V(s)(q0) = sum_k s_k Hess T_k(q0) with every Hess T_k(q0) PSD, so its kernel "
            "is cap_k ker Hess T_k(q0), independent of s: inertia 447/39/0 for every positive scaling"
        ),
        "symbolic_partition_residuals_zero": all(a == 0 and b == 0 for a, b in residuals.values()),
        "parameters_compared": len(keys),
        "linear_identity_residual": str(identity_residual),
        "V0_scaled": str(v0_scaled),
        "V0_at_s_equal_1_residual": str(v0_residual),
        "kappa_margin": {
            "scaled": "4 lambda_H(s) lambda_S(s) r0^2 - kappa(s)^2 = s^2 (8 r0^2 - kappa^2)",
            "committed": "4 r0^2 - kappa^2/2 (candidate.exact_hs_certificate) = (8 r0^2 - kappa^2)/2",
            "scale_invariant": bool(margin_ok),
        },
        "unit_computable_groups": group_rows,
        "C_square_value_at_q0": "t ||C_p Sigma0||^2 = 0 (C_p sigma_std = 0 exactly, hessian.phi_sigma_data)",
        "why_A_and_C_are_grouped": (
            "the exact Hessian module binds O44 as one unit with weights a_j + c_j; the lemma holds for independent "
            "s_A and s_C by the same argument (both are squares vanishing at q0), but only s_A = s_C members are "
            "evaluated exactly here"
        ),
        "proper_subset_counterexamples": {
            "O48_only_x1/50": "grad_Phi(q0) = (s - 1) grad Q(p) = (s - 1) 4 p != 0: |Phi| moves (exact)",
            "O27_only_x1/50": f"grad V(q0) supported on Sigma with u0 . grad = {Fraction(radial, int(o27['gradient'][1]))} != 0: the Sigma radius moves (exact)",
        },
    }
    return record, checks


# ---------------------------------------------------------------------------
# (D) Members.
# ---------------------------------------------------------------------------


def _hessian_equals_scaled(left: tuple[np.ndarray, int], right: tuple[np.ndarray, int], factor: Fraction) -> bool:
    """left == factor * right entrywise (exact)."""
    num_l, den_l = left
    num_r, den_r = right
    return bool(np.array_equal(num_l * (factor.denominator * int(den_r)), num_r * (factor.numerator * int(den_l))))


def _certificate_summary(certificate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "inertia_positive_zero_negative": "%d/%d/%d"
        % (certificate["inertia"]["positive"], certificate["exact_nullity"], certificate["inertia"]["negative"]),
        "exact_rank": certificate["exact_rank"],
        "exact_nullity": certificate["exact_nullity"],
        "kernel_equals_expected_span": certificate["kernel_equals_expected_span"],
        "kernel_spanning_set": certificate["kernel_spanning_set"],
        "strictly_positive_on_kernel_complement": certificate["strictly_positive_on_kernel_complement"],
        "gradient_exactly_zero": certificate["gradient_exactly_zero"],
        "exact_PSD": certificate["exact_PSD"],
        "coverage_ok": bool(
            certificate["coverage"]["coefficients_proportional_to_unit_weights"] and certificate["coverage"]["every_nonzero_parameter_covered"]
        ),
        "denominator": certificate["denominator"],
        "O06": certificate["O06"],
        "O06_offset": certificate["O06_offset"],
        "certificate_gap_target": certificate["spectral_gap"]["lambda"],
        "certificate_gap_flag": certificate["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"],
    }


def _certificate_ok(summary: Mapping[str, Any], rank: int, nullity: int) -> bool:
    return bool(
        summary["exact_rank"] == rank
        and summary["exact_nullity"] == nullity
        and summary["kernel_equals_expected_span"]
        and summary["strictly_positive_on_kernel_complement"]
        and summary["gradient_exactly_zero"]
        and summary["exact_PSD"]
        and summary["coverage_ok"]
    )


def member_section(
    terms: Mapping[str, Mapping[str, Any]],
    scales: Mapping[str, Fraction],
    witness_channel: Mapping[str, Any],
    channel_of: Any,
    units: Sequence[Mapping[str, Any]],
    analysis: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, bool]]:
    checks: dict[str, bool] = {}
    full_scales = {name: Fraction(scales.get(name, Fraction(1))) for name in terms}
    unknown = sorted(set(scales) - set(terms))
    positive = all(value > 0 for value in full_scales.values()) and not unknown
    distinct = set(full_scales.values())
    common = next(iter(distinct)) if len(distinct) == 1 else None
    member = member_map(terms, full_scales)
    checks["member_is_whole_term_scaling_with_positive_factors"] = bool(positive and common is not None)
    witness_exact = hessian.exact_hessian("benchmark")
    member_exact = hessian.exact_hessian("benchmark", member)
    checks["member_hessian_equals_s_times_witness_hessian_exact"] = bool(
        common is not None and _hessian_equals_scaled(member_exact["hessian"], witness_exact["hessian"], common)
    )
    checks["member_gradient_exactly_zero"] = not any(int(value) for value in member_exact["gradient"][0].flat)
    certificate_b = hessian.exact_certificate("benchmark", member)
    certificate_r = hessian.exact_certificate("raised_O06", member)
    summary_b = _certificate_summary(certificate_b)
    summary_r = _certificate_summary(certificate_r)
    checks["member_benchmark_inertia_447_39_0_kernel_T35_plus_doublets"] = _certificate_ok(summary_b, hessian.EXPECTED_RANK, hessian.EXPECTED_NULLITY)
    checks["member_raised_O06_inertia_451_35_0_kernel_T35"] = _certificate_ok(
        summary_r, hessian.RAISED_EXPECTED_RANK, hessian.RAISED_EXPECTED_NULLITY
    )
    gap_target = (common if common is not None else Fraction(0)) * hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0
    gap_b = hessian.component_inertia(*hessian.exact_hessian("benchmark", member)["hessian"], shift=gap_target)
    gap_r = hessian.component_inertia(*hessian.exact_hessian("raised_O06", member)["hessian"], shift=gap_target)
    eps_inertia = hessian.component_inertia(*hessian.exact_hessian("raised_O06", member)["hessian"], shift=hessian.O06_RAISE)
    checks["member_smallest_nonzero_eigenvalue_s_r0sq_over_96_multiplicity_14_both_variants"] = bool(
        common is not None
        and gap_b["negative"] == hessian.EXPECTED_NULLITY
        and gap_b["zero"] == EXPECTED_GAP_MULTIPLICITY
        and gap_r["negative"] == hessian.RAISED_EXPECTED_NULLITY
        and gap_r["zero"] == EXPECTED_GAP_MULTIPLICITY
    )
    member_v0 = _assemble(units, member, analysis)["value"]
    minima = term_minima()
    v0_from_terms = sum((full_scales[name] * Fraction(minima.get(name, 0)) for name in terms if name in minima), Fraction(0))
    checks["member_V0_equals_s_V0_and_sum_of_scaled_minima"] = bool(
        common is not None and member_v0 == common * EXPECTED_V0 and member_v0 == v0_from_terms
    )
    channel = channel_of(member)
    e_member = channel["E"]
    checks["member_singlet_matrix_equals_s_times_witness"] = bool(
        common is not None and e_member == _scaled(witness_channel["E"], common)
    )
    checks["member_a0_below_half_exact"] = spectral_radius_below(e_member, channel["dims"], HALF_BOUND_BELOW)
    lambda_h = member.get(O36_IDS[0], Fraction(0))
    lambda_s = member.get(O23_ID, Fraction(0))
    kappa_m = member.get(O12_ID, Fraction(0))
    lambda_eff = lambda_h - kappa_m**2 / (4 * lambda_s * R0 * R0) if lambda_s else None
    witness_eff = candidate.exact_light_doublet_quartic(R0)["lambda_eff"]
    checks["member_lambda_eff_equals_127_over_3200"] = bool(
        lambda_eff == EXPECTED_MEMBER_LAMBDA_EFF and member.get(O36_IDS[1]) == lambda_h and common is not None and lambda_eff == common * witness_eff
    )
    diagonal_ok = all(channel["alpha"][block] < HALF_BOUND_BELOW for block in BLOCKS)
    checks["member_per_block_necessary_conditions_hold_exact"] = bool(diagonal_ok)
    a0_float, eigenvalues = _a0_float(channel)
    record = {
        "label": "EXACT (certificates, identities, a0 bound); NUM (a0 float)",
        "term_scales": full_scales,
        "common_scale": common,
        "coefficients": member,
        "hessian": {
            "numerators_identical_to_witness": bool(np.array_equal(member_exact["hessian"][0], witness_exact["hessian"][0])),
            "denominator": member_exact["hessian"][1],
            "witness_denominator": witness_exact["hessian"][1],
            "statement": "H_u(member) = s H_u(witness) entrywise (exact), so every Hessian eigenvalue scales by s",
        },
        "certificate_benchmark": summary_b,
        "certificate_raised_O06": summary_r,
        "raised_O06_note": (
            "the raised variant adds eps = r0^2/100 to O06 after scaling (unscaled offset): its doublet at r0^2/100 "
            "lies above the scaled remnants at s r0^2/96 = r0^2/4800, which are the lightest massive states"
        ),
        "certificate_gap_flag_note": (
            "hessian.exact_certificate tests the gap target r0^2/96 (raised: eps), valid only for the committed "
            "normalisation; it is re-checked here at s r0^2/96"
        ),
        "gap_recheck": {
            "lambda": gap_target,
            "lambda_over_r0_squared": gap_target / (R0 * R0),
            "benchmark_negative_zero_positive": [gap_b["negative"], gap_b["zero"], gap_b["positive"]],
            "raised_O06_negative_zero_positive": [gap_r["negative"], gap_r["zero"], gap_r["positive"]],
            "raised_O06_at_eps_r0sq_over_100_negative_zero_positive": [eps_inertia["negative"], eps_inertia["zero"], eps_inertia["positive"]],
        },
        "V0": member_v0,
        "lambda_eff": lambda_eff,
        "alpha": channel["alpha"],
        "beta": channel["beta"],
        "E": e_member,
        "a0_max_float": a0_float,
        "eigenvalues_float": eigenvalues,
        "a0_bound": "max|eig| < 1332/53 < 8 pi (exact inertia of (1332/53) N/4 +- E), so a0_max < 1/2",
    }
    return record, checks


def blockwise_section(
    terms: Mapping[str, Mapping[str, Any]], channel_of: Any
) -> tuple[dict[str, Any], dict[str, bool]]:
    member = member_map(terms, BLOCKWISE_TEST_SCALES)
    certificate = _certificate_summary(hessian.exact_certificate("benchmark", member))
    channel = channel_of(member)
    a0_float, eigenvalues = _a0_float(channel)
    checks = {
        "blockwise_test_member_inertia_447_39_0_kernel_T35_plus_doublets": _certificate_ok(
            certificate, hessian.EXPECTED_RANK, hessian.EXPECTED_NULLITY
        ),
        "blockwise_test_member_a0_below_half_exact": spectral_radius_below(channel["E"], channel["dims"], HALF_BOUND_BELOW),
    }
    record = {
        "label": "EXACT (lemma test point, NOT a benchmark); NUM (a0 float)",
        "term_scales": dict(BLOCKWISE_TEST_SCALES),
        "certificate_benchmark": certificate,
        "alpha": channel["alpha"],
        "beta": channel["beta"],
        "a0_max_float": a0_float,
        "eigenvalues_float": eigenvalues,
        "note": (
            "different positive factors per SOS term (A and C together) keep the exact inertia 447/39/0 and the kernel "
            "T35 + 4 doublet directions, as the lemma states; this point also has a0_max < 1/2 while scaling the "
            "Sigma self term only by 1/2 and the H/S term by 1/4"
        ),
    }
    return record, checks


def negative_results_section(
    terms: Mapping[str, Mapping[str, Any]], witness_channel: Mapping[str, Any], channel_of: Any
) -> tuple[dict[str, Any], dict[str, bool]]:
    dims = witness_channel["dims"]
    e_witness = witness_channel["E"]
    low, high = S_MAX_BRACKET
    checks = {
        "s_max_between_1_over_44_and_1_over_43_exact": bool(
            spectral_radius_below(_scaled(e_witness, low), dims, HALF_BOUND_BELOW)
            and spectral_radius_above(_scaled(e_witness, high), dims, HALF_BOUND_ABOVE)
        ),
        "overall_1_over_40_not_perturbative_exact": spectral_radius_above(_scaled(e_witness, FAILING_OVERALL_SCALE), dims, HALF_BOUND_ABOVE),
    }
    phi_only = channel_of(member_map(terms, PHI_ONLY_SCALES))
    checks["T_Phi_only_1_over_50_not_perturbative_exact"] = spectral_radius_above(phi_only["E"], phi_only["dims"], HALF_BOUND_ABOVE)
    a0_witness, _ = _a0_float(witness_channel)
    phi_a0, phi_eigenvalues = _a0_float(phi_only)
    record = {
        "label": "EXACT (inertia of (c/4) N +- E); NUM (a0 floats)",
        "s_max": {
            "bracket": [low, high],
            "a0_at_bracket_float": [a0_witness * float(low), a0_witness * float(high)],
            "statement": "a0_max(s) = s a0_max(1); at s = 1/44 max|eig| < 1332/53 < 8 pi, at s = 1/43 max|eig| > 176/7 > 8 pi",
        },
        "overall_1_over_40": {"a0_max_float": a0_witness * float(FAILING_OVERALL_SCALE), "perturbative": False},
        "T_Phi_only_1_over_50": {
            "a0_max_float": phi_a0,
            "eigenvalues_float": phi_eigenvalues,
            "perturbative": False,
            "reason": (
                "the 210 self entry drops to 1084/50 but the H (44) and Sigma (16645/448) self entries and the "
                "Phi-Sigma (sqrt(6/5) 205/4) and Phi-H (sqrt(2/21) 126) mixings are untouched and each exceeds 8 pi"
            ),
            "corrects": "rescue synthesis PR-4 line 'Rescale the 210 block by 0.02 or less' (research record)",
        },
        "per_block_necessary_conditions": {
            "statement": "max|eig M| >= max_A |M_AA| (Rayleigh), so a0 <= 1/2 needs s_A alpha_A <= 8 pi for every block",
            "T_Phi": "s_TPhi <= 8 pi/1084 = 2 pi/271 (< 44/1897 with pi < 22/7)",
            "T_HS": "22 lambda_H s_HS <= 8 pi, i.e. lambda_H <= 4 pi/11 at s_HS = 1",
            "W": "s_W <= 8 pi/(16645/448) = 3584 pi/16645",
        },
    }
    return record, checks


# ---------------------------------------------------------------------------
# Committed artifacts (fail closed).
# ---------------------------------------------------------------------------


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def committed_section(equality_report: Mapping[str, Any] | None, hessian_report: Mapping[str, Any] | None) -> tuple[dict[str, Any], dict[str, bool]]:
    equality_report = _load(equality.OUT_JSON) if equality_report is None else equality_report
    hessian_report = _load(hessian.OUT_JSON) if hessian_report is None else hessian_report
    equality_ok = bool(
        equality_report.get("status") == candidate.EQUALITY_SET_PROVED_STATUS
        and equality_report.get("n_failed") == 0
        and equality_report.get("theorem_claimed") is True
    )
    fresh = {variant: hessian.exact_certificate(variant) for variant in ("benchmark", "raised_O06")}
    keys = ("exact_rank", "exact_nullity", "denominator", "nonzero_entries", "maximum_abs_numerator", "kernel_equals_expected_span", "gradient_exactly_zero")
    comparison = {}
    agree = True
    for variant, key in (("benchmark", "exact_certificate"), ("raised_O06", "exact_certificate_raised_O06")):
        committed = hessian_report.get(key, {}) if isinstance(hessian_report.get(key), Mapping) else {}
        row = {name: [committed.get(name), json_roundtrip(fresh[variant][name])] for name in keys}
        comparison[variant] = row
        agree = agree and all(left == right for left, right in row.values())
    hessian_ok = bool(
        hessian_report.get("status") == candidate.EXACT_HESSIAN_CERTIFIED_STATUS
        and hessian_report.get("n_failed") == 0
        and isinstance(hessian_report.get("flags"), Mapping)
        and hessian_report["flags"].get("source_binding_exact") is True
        and agree
    )
    record = {
        "equality_set_artifact": {"status": equality_report.get("status"), "n_failed": equality_report.get("n_failed")},
        "exact_hessian_artifact": {"status": hessian_report.get("status"), "n_failed": hessian_report.get("n_failed")},
        "fresh_witness_certificates_vs_committed": comparison,
    }
    checks = {
        "committed_equality_set_artifact_proved": equality_ok,
        "committed_exact_hessian_artifact_certified_and_equal_to_fresh_witness_certificates": hessian_ok,
    }
    return record, checks


# ---------------------------------------------------------------------------
# Research record checks.
# ---------------------------------------------------------------------------


def research_section(
    witness_channel: Mapping[str, Any],
    *,
    research_record: Mapping[str, Any] | None = None,
    research_files: Mapping[str, tuple[str, str]] | None = None,
) -> tuple[dict[str, Any], dict[str, bool]]:
    record = RESEARCH_RECORD if research_record is None else research_record
    files = RESEARCH_FILES if research_files is None else research_files
    schema = ("label", "value", "meaning", "source_script", "source_json", "key", "source_json_sha256", "reproducible_from_repository")
    problems = []
    for name, entry in record.items():
        if not isinstance(entry, Mapping) or set(entry) != set(schema):
            problems.append(f"{name}: schema")
            continue
        if entry["label"] not in RESEARCH_LABELS:
            problems.append(f"{name}: label")
        sha = entry["source_json_sha256"]
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            problems.append(f"{name}: sha256 format")
        source = files.get(entry["source_json"])
        if source is None or source[1] != sha or source[0] != entry["source_script"]:
            problems.append(f"{name}: sha256 or source differs from RESEARCH_FILES")
        if entry["reproducible_from_repository"] is not False:
            problems.append(f"{name}: reproducible_from_repository")
    digest = research_files_digest(files)
    provenance_ok = bool(record and not problems and digest == RESEARCH_FILES_DIGEST)

    def value(name: str) -> Any:
        entry = record.get(name)
        return entry.get("value") if isinstance(entry, Mapping) else None

    exact = symmetric_matrix_float(witness_channel)
    deviations = []
    within = True
    try:
        mc = value("mc_singlet_matrix")
        err = value("mc_singlet_matrix_error")
        for i in range(len(BLOCKS)):
            for j in range(len(BLOCKS)):
                deviation = abs(exact[i, j] - float(mc[i][j]))
                sigma = float(err[i][j])
                deviations.append(deviation / sigma if sigma > 0 else math.inf)
                within = within and deviation <= RESEARCH_SIGMAS * sigma
        a0_exact, _ = _a0_float(witness_channel)
        a0_sigma = float(err[0][0]) / (16.0 * math.pi)
        a0_ok = abs(a0_exact - float(value("mc_a0_max"))) <= RESEARCH_SIGMAS * a0_sigma
        alpha_sigma = float(witness_channel["alpha"]["Sigma"])
        sigma_ok = bool(
            abs(alpha_sigma / (16.0 * math.pi) - float(value("sigma_self_a0_exact"))) <= RESEARCH_REL_TOLERANCE * float(value("sigma_self_a0_exact"))
            and abs(-alpha_sigma - float(value("sigma_self_M_SS_exact"))) <= RESEARCH_REL_TOLERANCE * alpha_sigma
        )
    except (TypeError, ValueError, KeyError, IndexError):
        within, a0_ok, sigma_ok = False, False, False
    checks = {
        "research_entries_labelled_with_provenance_and_pinned_digest": provenance_ok,
        "research_MC_matrix_within_3_sigma_of_exact": bool(within),
        "research_MC_a0_max_within_3_sigma_of_exact": bool(a0_ok),
        "research_sigma_self_entry_equals_exact_16645_over_448": bool(sigma_ok),
    }
    section = {
        "kind": "RESEARCH_RECORD",
        "provenance_note": RESEARCH_PROVENANCE_NOTE,
        "research_files": {name: {"producer": entry[0], "sha256": entry[1]} for name, entry in files.items()},
        "research_files_digest": digest,
        "entries": record,
        "problems": problems,
        "consistency": {
            "max_abs_deviation_in_sigma_units": max(deviations) if deviations else None,
            "sigmas_allowed": RESEARCH_SIGMAS,
        },
        "checks": checks,
    }
    return section, checks


# ---------------------------------------------------------------------------
# FLOAT64 corroboration (live compiler; outside the exact check count).
# ---------------------------------------------------------------------------

FLOAT_CHECK_NAMES = (
    "float_F1_compiler_O36_value_equals_lambda_H_N_H_squared_at_random_unit_H",
    "float_F2_compiler_Q_at_p_equals_1_and_T_Phi_at_p_equals_minus_1",
)


def float_evidence_section() -> dict[str, Any]:
    rng = np.random.default_rng(FLOAT_SEED)
    lambda_h = float(candidate.candidate_coefficients()[O36_IDS[0]])
    o36 = {parameter: lambda_h for parameter in O36_IDS}
    values = []
    for _ in range(3):
        vector = rng.normal(size=chart.H_REAL_DIM)
        vector /= np.linalg.norm(vector)
        state = np.zeros(TOTAL_DIM)
        state[BLOCK_SLICES["H"]] = vector
        values.append(candidate.compiler_value(state, o36))
    target_h = lambda_h / 4.0  # lambda_H N_H^2 with N_H = |q_H|^2/2 = 1/2
    deviation_h = max(abs(value - target_h) for value in values)
    base = hessian.benchmark_coefficients()
    state = np.zeros(TOTAL_DIM)
    state[BLOCK_SLICES["Phi"]] = np.asarray(hessian.source_tensors()["p"], dtype=float)
    q_value = candidate.compiler_value(state, {parameter: float(base[parameter]) for parameter in O48_IDS})
    t_phi = candidate.compiler_value(state, {parameter: float(base[parameter]) for parameter in (O07_ID, *O48_IDS)})
    checks = {
        FLOAT_CHECK_NAMES[0]: deviation_h <= FLOAT_TOLERANCE,
        FLOAT_CHECK_NAMES[1]: abs(q_value - 1.0) <= FLOAT_TOLERANCE and abs(t_phi + 1.0) <= FLOAT_TOLERANCE,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "run": True,
        "label": "FLOAT64 corroboration outside the exact check count (live compiler)",
        "F1_O36_values": values,
        "F1_target_lambda_H_over_4": target_h,
        "F1_max_abs_deviation": deviation_h,
        "F2_Q_at_p": q_value,
        "F2_T_Phi_at_p": t_phi,
        "tolerance": FLOAT_TOLERANCE,
        "seed": FLOAT_SEED,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# The report.
# ---------------------------------------------------------------------------

CHECK_LABELS_NUM = ("num_eigenvalues_consistent_with_exact_characteristic_polynomial",)
CHECK_LABEL_RESEARCH_PREFIX = "research_"

THEOREM = (
    "Tree level, s -> infinity, coupled SO(10) x U(1)_X x U(1)_PQ singlet two-particle channel of the five scalar "
    "blocks: at the committed G3 witness the singlet-channel matrix is exactly -4 N^-1 E with alpha = (1084, 44, "
    "16645/448, 4, 1/8), beta_{Phi|Sigma} = 205/4, beta_{Sigma|Phi} = 123/2, beta_{H|Phi} = 12 and no other pair, so "
    "21 < a0_max < 22 (a0_max = 21.654): the committed normalisation is non-perturbative.  Scaling every SOS term "
    "of the committed identity by its own positive factor keeps the SOS identity, the vacuum, the equality set and "
    "the Hessian inertia; the overall x1/50 member has H_u = H_u(witness)/50, inertia 447/39/0 (451/35/0 raised), "
    "smallest nonzero eigenvalue r0^2/4800, V0/50 and a0_max = 0.4331 < 1/2 in the computed channel; s_max lies in "
    "(1/44, 1/43); rescaling the 210 block alone by 1/50 leaves a0_max = 1.98."
)
STATUS_NEUTRALITY = (
    "status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20 or any roadmap/readiness "
    "module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed; the committed witness remains the G3 "
    "closing instance and the internal candidate is unchanged"
)


def build_report(
    *,
    numerical: bool = True,
    terms: Mapping[str, Mapping[str, Any]] | None = None,
    member_scales: Mapping[str, Fraction] | None = None,
    unit_table: Mapping[str, tuple[int, str, tuple[str, ...]]] | None = None,
    block_dims: Mapping[str, int] | None = None,
    alpha_overrides: Mapping[str, Fraction] | None = None,
    research_record: Mapping[str, Any] | None = None,
    research_files: Mapping[str, tuple[str, str]] | None = None,
    equality_report: Mapping[str, Any] | None = None,
    hessian_report: Mapping[str, Any] | None = None,
    expected_n_checks: int | None = None,
) -> dict[str, Any]:
    """Build the status-neutral unitarity record.  Every keyword except ``numerical`` exists for fail-closed
    mutation tests (a term partition, member scales, the unit classification table, block dimensions, alpha
    overrides, the research record/files, committed reports and the expected check count)."""
    started = time.time()
    count_target = EXPECTED_N_CHECKS if expected_n_checks is None else expected_n_checks
    table = dict(UNIT_TABLE)
    table.update(unit_table or {})
    dims = dict(BLOCK_DIMS)
    dims.update(block_dims or {})
    term_map = sos_terms() if terms is None else {name: dict(term) for name, term in terms.items()}
    scales = {name: MEMBER_SCALE for name in term_map} if member_scales is None else dict(member_scales)
    checks: dict[str, bool] = {}

    # (A) method.
    moments = gaussian_moment_section()
    calibration = lqt_calibration()
    h_self = h_self_section()
    alpha_h_channels = h_self["alpha_by_channel"]
    checks["gaussian_fourth_moment_identity_exact"] = moments["self_all_equal"]
    checks["gaussian_biquadratic_moment_identity_exact"] = moments["mixed_all_equal"]
    checks["lee_quigg_thacker_calibration_a0_3_lambda_over_8_pi"] = calibration["a0_equals_3_lambda_over_8_pi"]
    checks["h_self_identity_I1_plus_I54_equals_NH_squared_sympy"] = h_self["identity_I1_plus_I54_equals_NH_squared"]
    checks["alpha_H_22_per_unit_lambda_H_and_trace_independent_of_unit_vector"] = bool(
        h_self["trace_equals_alpha_at_test_unit_vectors"]
        and alpha_h_channels["I_1"] + alpha_h_channels["I_54"] == alpha_h_channels["N_H^2"] == 22
        and alpha_h_channels == EXPECTED_ALPHA_H_PER_CHANNEL
    )
    units = hessian.exact_unit_matrices(R0, X0)
    u0, common = vacuum_u()
    norms = chart_norms_at_q0(u0, common)
    squared = hessian.congruence_scale_squared()
    checks["block_dimensions_and_congruence_factors_match_chart"] = bool(
        all(dims[name] == block.stop - block.start for name, block in BLOCK_SLICES.items())
        and all(squared[i] == D_SQUARED[name] for name, block in BLOCK_SLICES.items() for i in range(block.start, block.stop))
    )
    checks["chart_norms_at_q0_equal_1_2r0sq_2r0sq_2x0sq"] = norms == {
        "Phi": Fraction(1), "H": Fraction(0), "Sigma": 2 * R0 * R0, "S": 2 * R0 * R0, "Phi17": 2 * X0 * X0
    }
    scaled_units = hessian.exact_unit_matrices(VEV_SCALING * R0, X0)
    analysis = unit_analysis(units, table, u0, common, scaled_units)
    checks.update(classification_checks(units, table, analysis))
    witness_coefficients = hessian.benchmark_coefficients()
    coverage = hessian.unit_coefficients(units, witness_coefficients)
    checks["unit_coverage_of_committed_map_exact"] = bool(
        coverage["coefficients_proportional_to_unit_weights"] and coverage["every_nonzero_parameter_covered"] and coverage["no_parameter_in_two_units"]
    )
    v0_units = sum(
        (coverage["unit_coefficients"][name] * (row["value_at_q0"] if row["value_at_q0"] is not None else Fraction(0)) for name, row in analysis.items()),
        Fraction(0),
    )
    checks["euler_values_at_q0_sum_to_V0"] = bool(v0_units == candidate.lower_bound_v0() == EXPECTED_V0)

    def channel_of(coefficients: Mapping[str, Fraction]) -> dict[str, Any]:
        return singlet_channel(coefficients, units, table, analysis, alpha_h_channels, norms, dims=dims, alpha_overrides=alpha_overrides)

    # (B) committed witness.
    witness_channel = channel_of(witness_coefficients)
    witness, witness_checks, _ = witness_section(witness_channel, witness_coefficients, units)
    checks.update(witness_checks)

    # (C) rescaling lemma.
    lemma, lemma_checks = lemma_section(term_map, units, analysis, u0)
    checks.update(lemma_checks)
    blockwise, blockwise_checks = blockwise_section(term_map, channel_of)
    checks.update(blockwise_checks)
    committed, committed_checks = committed_section(equality_report, hessian_report)
    checks.update(committed_checks)

    # (D) perturbative member and negative results.
    member, member_checks = member_section(term_map, scales, witness_channel, channel_of, units, analysis)
    checks.update(member_checks)
    negative, negative_checks = negative_results_section(term_map, witness_channel, channel_of)
    checks.update(negative_checks)

    # Research record.
    research, research_checks = research_section(witness_channel, research_record=research_record, research_files=research_files)
    checks.update(research_checks)

    failures = [name for name, passed in checks.items() if not passed]
    if count_target is not None and len(checks) != count_target:
        failures.append(CHECK_COUNT_FAILURE)
    exact_ok = not failures
    float_evidence = (
        float_evidence_section()
        if numerical
        else {"run": False, "label": "FLOAT64 corroboration outside the exact check count", "reason": "--no-numerics"}
    )
    float_ok = bool(numerical and float_evidence.get("n_failed") == 0 and float_evidence.get("n_checks") == EXPECTED_N_FLOAT_CHECKS)
    certified = bool(exact_ok and (not numerical or float_ok))
    labels = {
        name: ("NUM" if name in CHECK_LABELS_NUM else "RESEARCH_RECORD consistency" if name.startswith(CHECK_LABEL_RESEARCH_PREFIX) else "EXACT")
        for name in checks
    }
    flags = {
        "record_claimed": exact_ok,
        "committed_witness_singlet_channel_nonperturbative": bool(exact_ok and checks.get("a0_max_between_21_and_22_exact")),
        "overall_one_fiftieth_member_perturbative_in_computed_channel": bool(exact_ok and checks.get("member_a0_below_half_exact")),
        "rescaling_lemma_whole_sos_terms_exact": bool(exact_ok and checks.get("every_unit_computable_term_group_hessian_psd_at_q0_exact")),
        "phi_block_only_rescaling_insufficient": bool(exact_ok and checks.get("T_Phi_only_1_over_50_not_perturbative_exact")),
        "s_max_bracketed_1_over_44_to_1_over_43": bool(exact_ok and checks.get("s_max_between_1_over_44_and_1_over_43_exact")),
        "float_evidence_run": bool(numerical),
        "float_evidence_consistent": float_ok,
    }
    flags.update({name: False for name in NEVER_TRUE_FLAGS})
    a0_member = member["a0_max_float"]
    report = {
        "module": MODULE,
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_CERTIFIED if certified else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_CERTIFIED if certified else OVERALL_STATE_OPEN,
        "record_claimed": exact_ok,
        "theorem": THEOREM if exact_ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "G3_witness_unchanged": True,
        "n_checks": len(checks),
        "expected_n_checks": count_target,
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "check_labels": labels,
        "flags": flags,
        "method": {
            "label": "EXACT lemma",
            "regime": "tree level, s -> infinity: quartic contact terms only (trilinear exchange falls off as 1/s)",
            "chart": "canonical chart K = q^T q/2 (live_g2_canonical_486_field_chart_v20)",
            "blocks": {name: {"n_real": dims[name], "q_trace_factor": Fraction(1, D_SQUARED[name]), "vev_chart_norm_squared": norms[name]} for name in BLOCKS},
            "irreducibility_premise": (
                "Phi (210, real type), H (10 (x) C with U(1)_X), Sigma (126bar), S and Phi17 (charged singlets) are "
                "irreducible real representations of SO(10) x U(1)_X x U(1)_PQ, so Lap of an invariant quartic "
                "restricted to a block is c |x_A|^2 (standard representation theory; checked for H with sympy and "
                "for Sigma against the dimension-weighted channel sum)"
            ),
            "formulas": {
                "self": "E[V4_A] = (1/8) Lap^2 V4_A = (n_A/4) alpha_A, alpha_A = Tr Hess_q V4_A(e)",
                "mixed": "E[V_AB] = (1/4) Lap_A Lap_B V_AB = (n_B/2) beta_{A|B}, beta_{A|B} = Tr_A Hess_q V_AB(x_B unit)",
                "matrix": "M_AA = -alpha_A, M_AB = -sqrt(n_B/n_A) beta_{A|B}; eig M = eig(-4 N^-1 E); a0 = eig/(16 pi)",
                "unitarity": "|a0| <= 1/2",
                "pi_bounds": "333/106 < pi < 22/7: max|eig| < 1332/53 certifies a0 < 1/2, max|eig| > 176/7 certifies a0 > 1/2",
            },
            "gaussian_moments": moments,
            "lee_quigg_thacker_calibration": calibration,
            "H_self_quartic": h_self,
            "unit_classification": analysis,
            "V0_from_Euler_values": v0_units,
        },
        "witness": witness,
        "rescaling_lemma": lemma,
        "blockwise_test_member": blockwise,
        "committed_artifacts": committed,
        "perturbative_member": member,
        "negative_results": negative,
        "what_changes": {
            "mass_squared": "every tree mass^2 (Hessian eigenvalue) scales by s = 1/50 (exact: H_u(s) = s H_u(1))",
            "masses_factor_float": math.sqrt(float(MEMBER_SCALE)),
            "vevs": "unchanged: the same vacuum q0 = (p, 0, r0 sigma_std, r0, x0) (exact zero gradient)",
            "gauge_boson_masses": "unchanged (vevs and gauge couplings only)",
            "lambda_eff": {"witness": candidate.exact_light_doublet_quartic(R0)["lambda_eff"], "member": member["lambda_eff"]},
            "eps_windows": {
                "witness_perturbative_box": hessian.EPS_PERTURBATIVE_UPPER,
                "member_perturbative_box": hessian.PERTURBATIVE_BOUND - 2 * MEMBER_SCALE * abs(KAPPA) * R0,
                "witness_doublet_is_lightest_for_eps_below": hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0,
                "member_doublet_is_lightest_for_eps_below": MEMBER_SCALE * hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0,
                "note": (
                    "eps enters quadratically (no effect on the s -> infinity amplitude); the |c| < 12 box of the "
                    "committed eps family moves to 12 - 2 s |kappa| r0, and the eps doublet is the lightest massive "
                    "state only below s r0^2/96"
                ),
            },
            "not_recomputed": (
                "the D12 GUT thresholds, the G6 remnant RG no-go numbers and the G7 research running assume the "
                "committed normalisation and are not recomputed at the rescaled member"
            ),
        },
        "research_record": research,
        "float_evidence": float_evidence,
        "float_verdict": "",
        "scope": {
            "claimed": [
                "the exact tree-level s -> infinity singlet-channel matrix of the committed witness (five scalar "
                "blocks) and 21 < a0_max < 22 (a0_max = 21.654): the committed normalisation is non-perturbative",
                "the rescaling lemma: whole SOS terms scaled by positive factors keep the SOS identity, the vacuum, the "
                "equality set and the Hessian inertia (exact per-term stationarity/PSD at q0; blockwise test point)",
                "proper-subset scalings (O48 alone, O27 alone) break stationarity at q0 (exact)",
                "the overall x1/50 member: H_u = H_u(witness)/50, 447/39/0 and 451/35/0, gap r0^2/4800, V0/50, "
                "lambda_eff = 127/3200 and a0_max = %.4f < 1/2 in the computed channel (exact rational bound)" % a0_member,
                "s_max in (1/44, 1/43); x1/40 and the T_Phi-only x1/50 rescaling are not perturbative (exact)",
            ],
            "not_claimed": [
                "non-singlet two-particle channels are not computed: |a0| <= 1/2 is shown in the singlet channel "
                "only (a necessary condition, not full perturbative unitarity)",
                "finite-energy partial waves (trilinear exchange) and loop-level perturbativity or running are not "
                "computed",
                "the D12 GUT thresholds, the G6 remnant RG no-go and the G7 running are not recomputed at the rescaled "
                "member; they assume the committed normalisation",
                "no benchmark is chosen: the committed witness remains the G3 closing instance and this adds one "
                "perturbative family member; the blockwise point is a lemma test point",
                "no gate status, ledger entry, internal candidate or manuscript text changes",
            ],
            "relies_on_committed": [
                "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; the equality set of every whole-term member is "
                "the same intersection of term zero sets)",
                "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to the fresh witness certificates)",
                "g3_sm_pati_salam_exact_hessian_v20 binding units (bound to the live compiler in that module)",
                "g3_sm_pati_salam_candidate_v20 SOS identity (term partition = expanded_sos_coefficient_map)",
            ],
            "status_neutrality": STATUS_NEUTRALITY,
        },
        "provenance": {
            "reuses": [
                "g3_sm_pati_salam_exact_hessian_v20: exact_unit_matrices, unit_coefficients, combine, exact_hessian, "
                "exact_certificate (overrides keyword used read-only for the rescaled members), component_inertia, "
                "exact_inertia, h_wedge_data, phi_sigma_data, source_tensors",
                "g3_sm_pati_salam_candidate_v20: candidate_coefficients, expanded_sos_coefficient_map, lower_bound_v0, "
                "exact_light_doublet_quartic, compiler_value (FLOAT64 corroboration only)",
            ],
            "research_note": RESEARCH_PROVENANCE_NOTE,
            "research_files": {name: {"producer": entry[0], "sha256": entry[1]} for name, entry in RESEARCH_FILES.items()},
        },
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["float_verdict"] = _float_verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the witness unitarity record is NOT claimed (failed: " + ", ".join(report["failures"])
            + ").  No gate is affected: this report is status-neutral."
        )
    witness = report["witness"]
    member = report["perturbative_member"]
    negative = report["negative_results"]
    return (
        f"Exact ({report['n_checks']} checks): at the committed G3 witness the tree-level singlet-channel matrix has "
        f"a0_max = {witness['a0_max_float']:.3f} (exactly between 21 and 22; the 210 singlet entry alone is "
        f"{witness['per_block_self_a0']['Phi']:.3f}), so the benchmark normalisation is non-perturbative.  Scaling "
        "whole SOS terms by positive factors keeps the certificate exactly; the overall x1/50 member keeps the vacuum, "
        "the SOS identity, the equality set and the inertia 447/39/0 (451/35/0 raised), with gap r0^2/4800, and has "
        f"a0_max = {member['a0_max_float']:.4f} < 1/2 in the computed channel.  s_max lies in (1/44, 1/43); "
        f"rescaling only the 210 block by 1/50 leaves a0_max = {negative['T_Phi_only_1_over_50']['a0_max_float']:.2f}.  "
        "Status-neutral: no gate changes, the committed witness remains the G3 closing instance, non-singlet channels "
        "are not computed and the D12 thresholds are not recomputed."
    )


def _float_verdict(report: Mapping[str, Any]) -> str:
    evidence = report["float_evidence"]
    if not evidence.get("run"):
        return "FLOAT64 corroboration not run (--no-numerics); the exact verdict does not depend on it."
    if evidence.get("n_failed"):
        return "FLOAT64 corroboration FAILED (" + ", ".join(evidence["failures"]) + "); the report is not certified."
    return (
        f"FLOAT64 corroboration, outside the exact check count: {evidence['n_checks']}/{evidence['n_checks']} passed "
        "(live compiler: O36 = lambda_H N_H^2 at random unit H; Q(p) = 1 and T_Phi(p) = -1)."
    )


def report_passes(report: Mapping[str, Any]) -> bool:
    """Certified, nothing failed, the pinned check count and every never-true flag False."""
    flags = report.get("flags", {})
    return bool(
        report.get("n_failed") == 0
        and report.get("status") == STATUS_CERTIFIED
        and report.get("n_checks") == EXPECTED_N_CHECKS
        and len(report.get("checks", {})) == EXPECTED_N_CHECKS
        and all(report.get("checks", {}).values())
        and all(flags.get(name) is False for name in NEVER_TRUE_FLAGS)
    )


# ---------------------------------------------------------------------------
# Markdown.
# ---------------------------------------------------------------------------


def _cell(value: Any) -> str:
    return "`" + str(value).replace("|", "\\|") + "`"


def _fmt(value: Any, digits: int = 6) -> str:
    return f"{value:.{digits}g}" if isinstance(value, float) else str(value)


def _markdown(report: Mapping[str, Any]) -> str:
    witness = report["witness"]
    member = report["perturbative_member"]
    negative = report["negative_results"]
    blockwise = report["blockwise_test_member"]
    lines = [
        "# G3 SM Pati-Salam witness: perturbative-unitarity normalisation -- v20",
        "",
        f"**Status:** `{report['status']}` (`{report['overall_state']}`)",
        "",
        f"**Record claimed:** `{report['record_claimed']}`",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        report["float_verdict"],
        "",
        f"Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed.",
        "",
        "## Statement",
        "",
        report["theorem"],
        "",
        "## Method (EXACT lemma)",
        "",
    ]
    lines += [f"- **{key}**: {value}" for key, value in report["method"]["formulas"].items()]
    lines += [f"- **regime**: {report['method']['regime']}", f"- **irreducibility premise**: {report['method']['irreducibility_premise']}", ""]
    lines += ["| block | n (reals) | q-trace factor | vev chart norm^2 |", "|---|---|---|---|"]
    for name in BLOCKS:
        row = report["method"]["blocks"][name]
        lines.append(f"| {name} | `{row['n_real']}` | `{row['q_trace_factor']}` | `{row['vev_chart_norm_squared']}` |")
    lines += [
        "",
        "## Committed witness (EXACT)",
        "",
        "| block | alpha_A | self a0 = alpha/(16 pi) (NUM) | channel |",
        "|---|---|---|---|",
    ]
    for name in BLOCKS:
        lines.append(
            f"| {name} | `{witness['alpha'][name]}` | `{_fmt(witness['per_block_self_a0'][name])}` | {witness['per_block_labels'][name]} |"
        )
    lines += ["", "| pair | beta |", "|---|---|"]
    lines += [f"| {_cell(key)} | `{value}` |" for key, value in witness["beta"].items()]
    lines += [
        "",
        f"- -4 N^-1 E (rows Phi, H, Sigma, S, Phi17): {_cell(witness['minus_4_Ninv_E'])}",
        f"- characteristic polynomial: {_cell(witness['characteristic_polynomial']['full'])}",
        f"- largest |eig| in {_cell(witness['max_abs_eigenvalue_interval'])}; a0_max in "
        f"`[{_fmt(witness['a0_max_exact_enclosure_float'][0], 8)}, {_fmt(witness['a0_max_exact_enclosure_float'][1], 8)}]` (exact rational enclosure)",
        f"- eigenvalues (NUM): `{', '.join(_fmt(v, 8) for v in witness['eigenvalues_float'])}`; a0_max = `{_fmt(witness['a0_max_float'], 8)}`",
        f"- {witness['a0_max_between']}",
        "",
        "## Rescaling lemma (EXACT)",
        "",
        report["rescaling_lemma"]["statement"],
        "",
        "| group | terms | gradient 0 at q0 | Hessian inertia +/-/0 | value at q0 | expected minimum |",
        "|---|---|---|---|---|---|",
    ]
    for name, row in report["rescaling_lemma"]["unit_computable_groups"].items():
        lines.append(
            f"| {name} | {', '.join(row['terms'])} | `{row['gradient_exactly_zero_at_q0']}` | "
            f"`{'/'.join(str(v) for v in row['hessian_inertia_positive_negative_zero'])}` | `{row['value_at_q0']}` | `{row['expected_minimum']}` |"
        )
    lines += ["", "Proper-subset counterexamples:", ""]
    lines += [f"- {key}: {value}" for key, value in report["rescaling_lemma"]["proper_subset_counterexamples"].items()]
    lines += [
        "",
        "## Members",
        "",
        "| member | term scales | inertia (benchmark) | a0_max (NUM) | a0 <= 1/2 (exact) |",
        "|---|---|---|---|---|",
        f"| overall x1/50 | all `1/50` | `{member['certificate_benchmark']['inertia_positive_zero_negative']}` "
        f"(raised `{member['certificate_raised_O06']['inertia_positive_zero_negative']}`) | `{_fmt(member['a0_max_float'], 6)}` | "
        f"`{report['checks'].get('member_a0_below_half_exact')}` |",
        f"| blockwise test point (not a benchmark) | {_cell(blockwise['term_scales'])} | "
        f"`{blockwise['certificate_benchmark']['inertia_positive_zero_negative']}` | `{_fmt(blockwise['a0_max_float'], 6)}` | "
        f"`{report['checks'].get('blockwise_test_member_a0_below_half_exact')}` |",
        f"| T_Phi only x1/50 | `T_Phi: 1/50` | (whole term: certificate kept) | `{_fmt(negative['T_Phi_only_1_over_50']['a0_max_float'], 6)}` | `False` |",
        f"| overall x1/40 | all `1/40` | | `{_fmt(negative['overall_1_over_40']['a0_max_float'], 6)}` | `False` |",
        "",
        f"- H_u(member) = H_u(witness)/50: numerators identical `{member['hessian']['numerators_identical_to_witness']}`, "
        f"denominators `{member['hessian']['witness_denominator']}` -> `{member['hessian']['denominator']}`",
        f"- gap re-check at `{member['gap_recheck']['lambda']}` = r0^2 x `{member['gap_recheck']['lambda_over_r0_squared']}`: "
        f"benchmark (neg/zero/pos) `{member['gap_recheck']['benchmark_negative_zero_positive']}`, raised "
        f"`{member['gap_recheck']['raised_O06_negative_zero_positive']}`",
        f"- {member['raised_O06_note']}",
        f"- {member['certificate_gap_flag_note']}",
        f"- V0 = `{member['V0']}`, lambda_eff = `{member['lambda_eff']}`",
        f"- s_max in {_cell(negative['s_max']['bracket'])} ({negative['s_max']['statement']})",
        f"- T_Phi only: {negative['T_Phi_only_1_over_50']['reason']}; corrects the {negative['T_Phi_only_1_over_50']['corrects']}",
        "",
        "Per-block necessary conditions:",
        "",
    ]
    lines += [f"- {key}: {value}" for key, value in negative["per_block_necessary_conditions"].items()]
    changes = report["what_changes"]
    lines += [
        "",
        "## What changes at the x1/50 member",
        "",
        f"- {changes['mass_squared']}; masses x `{_fmt(changes['masses_factor_float'], 6)}`",
        f"- vevs: {changes['vevs']}; gauge-boson masses: {changes['gauge_boson_masses']}",
        f"- lambda_eff: `{changes['lambda_eff']['witness']}` -> `{changes['lambda_eff']['member']}`",
        f"- eps windows: {_cell({k: v for k, v in changes['eps_windows'].items() if k != 'note'})}; {changes['eps_windows']['note']}",
        f"- {changes['not_recomputed']}",
        "",
        "## Research record (not re-derived)",
        "",
        report["research_record"]["provenance_note"],
        "",
        "| entry | source | key | sha256 |",
        "|---|---|---|---|",
    ]
    for name, entry in report["research_record"]["entries"].items():
        lines.append(f"| {name} | {entry['source_json']} | {entry['key']} | `{entry['source_json_sha256'][:16]}...` |")
    lines += [
        "",
        f"Largest deviation of the exact matrix from the Monte Carlo record: "
        f"`{_fmt(report['research_record']['consistency']['max_abs_deviation_in_sigma_units'], 4)}` sigma.",
        "",
    ]
    evidence = report["float_evidence"]
    lines += ["## FLOAT64 evidence (outside the exact check count)", ""]
    if evidence.get("run"):
        lines += [
            f"- F1 O36 compiler values at random unit H: `{', '.join(_fmt(v, 15) for v in evidence['F1_O36_values'])}` "
            f"(target `{evidence['F1_target_lambda_H_over_4']}`, max deviation `{_fmt(evidence['F1_max_abs_deviation'], 3)}`)",
            f"- F2 Q(p) = `{_fmt(evidence['F2_Q_at_p'], 15)}`, T_Phi(p) = `{_fmt(evidence['F2_T_Phi_at_p'], 15)}`",
            "",
        ]
        lines += ["| FLOAT64 check | passed |", "|---|---|"]
        lines += [f"| `{name}` | `{value}` |" for name, value in evidence["checks"].items()]
    else:
        lines.append("not run (--no-numerics)")
    lines += ["", "## Checks", "", "| check | label | passed |", "|---|---|---|"]
    lines += [f"| `{name}` | {report['check_labels'][name]} | `{value}` |" for name, value in report["checks"].items()]
    lines += ["", "## Scope", ""]
    for key in ("claimed", "not_claimed", "relies_on_committed"):
        lines += [f"**{key}**", ""] + [f"- {row}" for row in report["scope"][key]] + [""]
    lines += ["**status_neutrality**", "", report["scope"]["status_neutrality"], ""]
    lines.append(f"Runtime: {report['runtime_seconds']:.0f} s.")
    return "\n".join(lines) + "\n"


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n"


def write_report(report: Mapping[str, Any], *, out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> None:
    Path(out_json).write_text(render_json(report), encoding="utf-8")
    Path(out_md).write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts (only if certified)")
    parser.add_argument("--no-numerics", action="store_true", help="skip the FLOAT64 corroboration")
    args = parser.parse_args(argv)
    report = build_report(numerical=not args.no_numerics)
    passes = report_passes(report)
    if args.write and passes:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    summary["float_evidence"] = {key: report["float_evidence"].get(key) for key in ("run", "n_checks", "n_failed", "failures")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if passes else 1


if __name__ == "__main__":
    raise SystemExit(main())
