#!/usr/bin/env python3
"""O36 lambda_H Higgs-quartic member of the SOS-certified SM Pati-Salam witness family (v20): exact, tree level,
status-neutral.

The decoupled-singlet family (g3_sm_pati_salam_decoupled_singlet_family_v20) keeps the H self-quartics of the
committed 27-parameter map at O36_B01 = O36_B02 = 2, so its light-doublet tree quartic is lambda_eff = 2 -
kappa^2/(4 rS^2), close to 2.  This module certifies the member

    O36_B01 = O36_B02 = lambda_H > 0      (every other entry of the family map unchanged; 27 parameters),

whose H/S block of the SOS identity is

    T6' = lambda_H N_H^2 + (2|kappa| rS + eps) N_H + 2 kappa Re(conj(H.H) conj(S)) + lambda_S (|S|^2 - rS^2)^2,

with lambda_S = O23 = 1 in the map.  Labels: EXACT (sympy or Fraction arithmetic), NUM (float64 recomputed here),
RESEARCH_RECORD (not re-derived; sha256 provenance).

EXACT results:

* H self-identity: I_1 + I_54 = N_H^2 as a polynomial identity in the 20 real coordinates of 10 complex H_i (sympy;
  the repository checked it only in float), and N_H^2 - |H.H|^2 = sum_{i<j} |conj(H_i) H_j - conj(H_j) H_i|^2
  (Cauchy-Schwarz |H.H| <= N_H as a sum of squares).  So a I_1 + b I_54 is a multiple of N_H^2 iff a = b, and the
  member's H quartic is lambda_H N_H^2.
* SOS identity (sympy, symbolic in lambda_H, lambda_S, rS, k = |kappa|, eps): after Cauchy-Schwarz,
  lambda_H N^2 + 2 k N (rS - s) + lambda_S (s^2 - rS^2)^2 + eps N
      = lambda_H (N - k t/lambda_H)^2 + t^2 (lambda_S u^2 - k^2/lambda_H) + eps N,   t = s - rS, u = s + rS,
  residual 0; it reduces to the committed identity at lambda_H = 2, lambda_S = 1.  For t >= 0 the bracket is
  >= 4 lambda_S rS^2 - k^2/lambda_H > 0 when kappa^2 < 4 lambda_H lambda_S rS^2 (equivalently lambda_eff > 0); for
  t < 0 every term is >= 0; the zero set is t = 0, N_H = 0.  At the boundary kappa^2 = 4 lambda_H lambda_S rS^2
  the bracket is lambda_S t (s + 3 rS) >= 0, so the bound and the equality set still hold.  Operator by operator:
  T6' = T6 + T9 + (lambda_H - 2)(I_1 + I_54), and the member map equals the family SOS map plus eps except
  O36 = lambda_H (three kappa signs), so V - V0 = T1 + ... + T5 + T6' + T7 + T8.
* Sharpness at eps = 0: along the Cauchy-Schwarz-saturated curve N_H = |kappa| t/lambda_H (H = h e_6 real,
  S = rS + t real) V - V0 = t^2 [lambda_S (2 rS + t)^2 - kappa^2/lambda_H], with exact rational violating points
  beyond the margin.  For eps > 0 the margin is sufficient but not sharp: minimising the reduced form over N_H >= 0
  gives 4 lambda_H R_min = (2c t^2 - 2 delta t + eps)(2c t u + 2|kappa| t - eps), c = sqrt(lambda_H lambda_S),
  delta = |kappa| - 2 c rS, so the exact H/S-block domain is |kappa| <= 2 c rS + sqrt(2 c eps) (exact identities, an
  exact non-violating row beyond the eps = 0 margin at eps = 1/1000 and an exact violating row beyond the extended
  domain; the certificate itself stays the completed square with kappa^2 < 4 lambda_H lambda_S rS^2).
* V0 = -1 - r0^4/8 - rS^4 - x0^4/32 is unchanged; the equality set is unchanged: {V = V0} = Z(T1..T5, T7, T8) and
  Z(T6'), Z(T6') = {H = 0, |S| = rS}, and T1-T5, T7, T8 are kappa-free (kappa enters only T6; exact check on the
  family's eight-term expansion), so the set equals {V_family(kappa') = V0} = G.q0 for any kappa'^2 < 8 rS^2 (e.g.
  kappa' = 0) -- this also covers lambda_H > 2 with 8 rS^2 <= kappa^2 < 4 lambda_H rS^2, where the family itself is
  not certified; bound fail-closed to the committed equality-set and decoupled-singlet family artifacts.
* The exact 486 x 486 Hessian over Q at (r0, rS, x0, kappa) = (1/5, 1, 1, -1/100) for lambda_H in {2, 1/100, 1/1000}
  and at the committed witness point (1/5, 1/5, 1, -1/20) for lambda_H = 1/10: numerator, denominator and gradient
  bit-identical to the lambda_H = 2 member (O36 is quartic in H), inertia 447/39/0 (kernel T35 + 4 doublet
  directions, gap r0^2/96 x 14) and 451/35/0 at eps = r0^2/100.  The Hessian cannot see lambda_H, so the global
  statement rests on the SOS identity, not on the Hessian (a witness-point member with lambda_H = 1/100 violates
  the margin although its Hessian is identical).  The hessian module's ``overrides`` keyword (documented for
  mutation tests) is used read-only to set the two O36 entries.
* Tree light-doublet quartic (S-radial exchange, series): lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2); with an
  O34 portal l34 it would be lambda_H - (|kappa| - l34 rS)^2/(4 lambda_S rS^2) (series identity only; no O34 member
  is certified).  For kappa = -r0^2/(4 rS): lambda_eff - lambda_H = -r0^4/(64 lambda_S rS^4) = -1.5625e-14 at
  rS = 1000 r0.
* Bounded from below: V4 >= lambda_H |q|^4/(165 lambda_H + 4) (Cauchy-Schwarz as in the candidate with
  alpha_NH = lambda_H): 1/167 at 2 (the committed G5 constant), 1/565 at 1/100, 1/4165 at 1/1000.

NUM (float64, outside the exact check count): the live compiler rows of both O36 directions vanish at q0 with their
gradient and Hessian; the compiler's O36_B01/B02 directions equal I_1 and I_54 at random H; the compiler reproduces
the exact violating value along the sharpness curve.

RESEARCH_RECORD (sha256 provenance, not re-derived): the rescue study's float projection of lambda_eff, the DA'
size of lambda_H - lambda_eff, and the tree matching of lambda_SM(v_R) at the research benchmarks BM-DA1/BM-E, which
needs lambda_H(M_GUT) ~ 0.036-0.104 inside the certified domain (CONDITIONAL: the running used an anti-SOS Delta_R
region point with G6 assumed fixed; the a1/lh2 sensitivity rows are outside the certified member (an H-Sigma portal
and O36_B01 != O36_B02), and one further row needs lambda_H < 0).

Scope: tree level only.  The one-loop quartic matching at v_R (research estimate +-0.004) is not computed, no
benchmark is chosen, the committed witness (lambda_H = 2) remains the G3/G4 closing instance, G5 stays bound to the
committed lambda_H = 2 vector, and no gate status changes (this module is not read by the ledger).
"""
from __future__ import annotations

import argparse
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

import exact_h10_self_quartic_family_v20 as h_self_source
import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_decoupled_singlet_family_v20 as family
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
MODULE = "g3_sm_pati_salam_higgs_quartic_member_v20"
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_V20.md"

STATUS_CERTIFIED = "SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_EXACT__TREE_LEVEL__STATUS_NEUTRAL"
STATUS_INCOMPLETE = "SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_INCOMPLETE__STATUS_NEUTRAL"
OVERALL_STATE_CERTIFIED = "EXACT_O36_LAMBDA_H_MEMBER__TREE_LIGHT_DOUBLET_QUARTIC_FREE__NO_BENCHMARK__NO_GATE_CHANGE"
OVERALL_STATE_OPEN = "HIGGS_QUARTIC_MEMBER_NOT_CERTIFIED__NO_GATE_CHANGE"
MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
EXPECTED_N_CHECKS = 48  # default point sets only (enforced by build_report and report_passes)
CHECK_COUNT_FAILURE = "check_count_equals_EXPECTED_N_CHECKS_with_default_point_sets"
EXPECTED_N_FLOAT_CHECKS = 3
FAMILY_EXPECTED_N_CHECKS = 77

R0, X0 = candidate.R0, candidate.X0
P = hessian.SingletPoint
O36_B01, O36_B02 = hessian.O36_IDS
O04, O06, O12 = candidate.O04_ID, candidate.O06_ID, candidate.O12_ID
O23 = hessian.O23_ID
H_S_IDS = (O36_B01, O36_B02, O06, O12, O04, O23)
LAMBDA_S = Fraction(1)  # O23 of the committed map: lambda_S (|S|^2 - rS^2)^2 with lambda_S = 1
KEEPS_POINT = P(R0, Fraction(1), X0, Fraction(-1, 100))  # the family's kappa = -r0^2/(4 rS) point at rS = 1
WITNESS_POINT = hessian.WITNESS_POINT  # (1/5, 1/5, 1, -1/20)
MEMBER_POINTS = (
    ("rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2", KEEPS_POINT, Fraction(2)),
    ("rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100", KEEPS_POINT, Fraction(1, 100)),
    ("rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000", KEEPS_POINT, Fraction(1, 1000)),
    ("rS_eq_r0_witness__lambda_H_1_over_10", WITNESS_POINT, Fraction(1, 10)),
)
# (margin 4 lambda_H lambda_S rS^2 - kappa^2, lambda_eff) pinned for the default points.
EXPECTED_POINT_VALUES = {
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2": (Fraction(79999, 10**4), Fraction(79999, 40000)),
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100": (Fraction(399, 10**4), Fraction(399, 40000)),
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000": (Fraction(39, 10**4), Fraction(39, 40000)),
    "rS_eq_r0_witness__lambda_H_1_over_10": (Fraction(27, 2000), Fraction(27, 320)),
}
POINT_CHECK_SUFFIXES = (
    "member_map_27_parameters_in_contract_changes_only_O36_vs_family_map",
    "margin_positive_and_lambda_eff_closed_form",
    "hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants",
    "benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14",
    "raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4",
)
# (lambda_H, |kappa|, t, V - V0) at rS = 1, lambda_S = 1 beyond the margin kappa^2 = 4 lambda_H rS^2.
SHARPNESS_RS = Fraction(1)
SHARPNESS_WITNESSES = (
    (Fraction(1, 100), Fraction(21, 100), Fraction(1, 1000), Fraction(-405999, 10**12)),
    (Fraction(1, 1000), Fraction(7, 100), Fraction(1, 10**4), Fraction(-89959999, 10**16)),
    (Fraction(2), Fraction(3), Fraction(3, 100), Fraction(-34119, 10**8)),
)
# eps > 0 rows at rS = 1, lambda_S = 1, lambda_H = 1/100 (c = sqrt(lambda_H lambda_S) = 1/10), |kappa| = 21/100 (beyond
# the eps = 0 margin: 4 lambda_H lambda_S rS^2 - kappa^2 = -41/10000): (eps, violates).  delta = 1/100, delta^2 = 1/10^4.
EPS_SHARPNESS_C = Fraction(1, 10)
EPS_SHARPNESS_ROWS = (
    (Fraction(1, 100), Fraction(21, 100), Fraction(1, 1000), False),  # 2 c eps = 1/5000 > delta^2: V >= V0 holds
    (Fraction(1, 100), Fraction(21, 100), Fraction(1, 10**5), True),  # 2 c eps = 1/500000 < delta^2: violation
)
BFB_EXPECTED = {Fraction(2): Fraction(1, 167), Fraction(1, 100): Fraction(1, 565), Fraction(1, 1000): Fraction(1, 4165)}
ANCHOR_RS_OVER_R0 = 1000
ANCHOR_LAMBDA_SHIFT = Fraction(-1, 64 * 10**12)
VARIANTS = ("benchmark", "raised_O06", "tiny_eps")
LABELS = ("EXACT", "NUM", "LIT", "RESEARCH_RECORD", "EST")
NEVER_TRUE_FLAGS = (
    "benchmark_chosen",
    "gate_status_changed",
    "G3_witness_replaced",
    "wired_into_gate_ledger",
    "one_loop_matching_computed",
    "lambda_SM_matched_by_certificate",
    "report_closes_g3_by_itself",
    "report_closes_g5_by_itself",
    "G5_bound_vector_changed",
)
FLOAT_TOLERANCE = 1.0e-12
FLOAT_SEED = 20260927
FLOAT_SAMPLES = 3
FLOAT_CHECK_NAMES = (
    "float_F1_live_O36_rows_value_gradient_hessian_zero_at_q0",
    "float_F2_compiler_O36_directions_equal_I1_I54_and_lambda_H_NH2",
    "float_F3_compiler_matches_exact_violating_value",
)
FLOAT_VIOLATING = (Fraction(1, 100), Fraction(21, 100), Fraction(1, 1000))  # (lambda_H, |kappa|, t) at rS = 1

PHYSICS_STATUS = {
    "certifies": "the tree-level O36 lambda_H member of the SOS-certified decoupled-singlet family only: the family map "
    "with O36_B01 = O36_B02 = lambda_H (committed 2), certified for kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = "
    "O23 = 1); its light-doublet tree quartic lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) is a free positive "
    "parameter",
    "does_not_choose_a_benchmark": "this report does NOT choose a benchmark: its (r0, rS, x0, kappa, lambda_H) points "
    "are certificate points, not benchmarks",
    "does_not_change_G3_G4_G5": "the committed witness (lambda_H = 2, rS = r0, kappa = -r0/4) remains the G3 and G4 "
    "closing instance and G5 stays bound to the committed lambda_H = 2 coefficient vector; no gate status, ledger "
    "entry or roadmap text changes",
    "tree_level_only": "lambda_eff is the tree-level light-doublet quartic; the one-loop quartic matching at v_R "
    "(research estimate +-0.004) is not computed, and the running of lambda_H is research-recorded only",
    "higgs_matching_is_research": "research record (CONDITIONAL): tree matching of lambda_SM(v_R) at the research "
    "benchmarks BM-DA1/BM-E needs lambda_H(M_GUT) ~ 0.036-0.104, inside the certified domain; that running used an "
    "anti-SOS Delta_R region point (G6 assumed fixed); the a1/lh2 sensitivity rows are outside the certified member "
    "(an H-Sigma portal and O36_B01 != O36_B02), and one further row needs lambda_H < 0; the G7 evidence on these "
    "benchmarks is recorded separately (g7_decoupled_singlet_benchmark_evidence_v20)",
}
STATUS_NEUTRALITY = (
    "status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20, g4_sm_closure_binding_v20 or any "
    "roadmap/readiness module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed, the committed lambda_H "
    "= 2 witness remains the G3 and G4 closing instance, and G5 stays bound to the committed coefficient vector"
)

# ---------------------------------------------------------------------------
# Research record (scratch outputs of the rescue study; values embedded, never read at runtime).
# ---------------------------------------------------------------------------

RESEARCH_PROVENANCE_NOTE = (
    "scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for "
    "audit only; the source files are not in the repository and were hashed at generation time (the session scratch "
    "area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified "
    "at runtime"
)
RESEARCH_FILES = {
    "E-G7-completion/e1_quartic_member.json": (
        "E-G7-completion/e1_quartic_member.py",
        "2e3e64a139b4d8df2f50c4cc94ffd932dfecd2761b0966acca41837ac025de4d",
    ),
    "E-G7-completion/verify-physics/v4_e1_check.json": (
        "E-G7-completion/verify-physics/v4_e1_check.py",
        "b879932351e08ac8b71ce3fefc7f2395a8eac4b70ff15df895d0b717201865b5",
    ),
    "E-G7-completion/verify-feasibility/v_sos.json": (
        "E-G7-completion/verify-feasibility/v_sos.py",
        "4974fd881893c27053afe7d0aa39321e836d29e72a21988b828fd7cbc3986447",
    ),
    "E-G7-completion/e3_quartic_rg.json": (
        "E-G7-completion/e3_quartic_rg.py",
        "b49b21f4191af7a0c95979e6ade7050f8cf9b90f1be8b9c9694330de4b96df2c",
    ),
    "E-G7-completion/e3b_quartic_sens.json": (
        "E-G7-completion/e3b_quartic_sens.py",
        "20617026db9b1ed7db541ec192ecce65275a1cb76b6153f5d78ce076e1f38d98",
    ),
}
RESEARCH_SCRIPT_SHA256 = {
    "E-G7-completion/e1_quartic_member.py": "d78f5baaf8322b4d8a36b553d008895b0f0d46aecdbc0e3cbb87cfab1929e5c2",
    "E-G7-completion/verify-physics/v4_e1_check.py": "d18cb79b3dbad80a63c4f5e0b5d1705c0927c6f92b7472341ab54085957a8ea0",
    "E-G7-completion/verify-feasibility/v_sos.py": "42ddff2d9c5bf990f47dabcc190fb4a0c23f6fb629b3f599fd617de51f52b9e6",
    "E-G7-completion/e3_quartic_rg.py": "8ca253eb116457dcb9dcc220001cb5ccc34419dc040cbef26fc4fcaddd31d80c",
    "E-G7-completion/e3b_quartic_sens.py": "7dd46bf816f85b68946427769319c98a6a5c26ca0a6ceeee73335ff15608758c",
}
RESEARCH_ROOT = "wfRESCUE (session scratchpad of the rescue study; paths below are relative to it; not in the repository)"
_REC = "RESEARCH_RECORD"


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


_E1 = "E-G7-completion/e1_quartic_member.json"
_V4 = "E-G7-completion/verify-physics/v4_e1_check.json"
_VSOS = "E-G7-completion/verify-feasibility/v_sos.json"
_E3 = "E-G7-completion/e3_quartic_rg.json"
_E3B = "E-G7-completion/e3b_quartic_sens.json"
E3_VARIANTS = ("W", "Tn", "T", "T0")
RESEARCH_RECORD: dict[str, dict[str, Any]] = {
    "e1_lambda_eff_exact_strings": _record(
        _REC,
        {"2": "79999/40000", "1/10": "3999/40000", "1/100": "399/40000", "1/1000": "39/40000", "1/10000": "3/40000"},
        "research exact lambda_eff = lambda_H - kappa^2/(4 rS^2) at (r0, rS, x0, kappa) = (1/5, 1, 1, -1/100) per "
        "lambda_H (re-derived exactly by this module)",
        _E1,
        "float.<lam_H>.lambda_eff_exact",
    ),
    "e1_lambda_eff_numerical_projection": _record(
        _REC,
        {
            "2": 1.9999750129179767,
            "1/10": 0.09997500460224319,
            "1/100": 0.00997501143478911,
            "1/1000": 0.0009750119759501886,
            "1/10000": 7.500554532191949e-05,
        },
        "float64 tree quartic of the light doublet by projection (V minimised over every other field at fixed doublet "
        "amplitude, fit V - V0 = c2 a^2 + c4 a^4 + c6 a^6, lambda = 4 c4) at (1/5, 1, 1, -1/100)",
        _E1,
        "float.<lam_H>.lambda_eff_numerical_projection",
    ),
    "e1_float_hessian_and_plane_scan": _record(
        _REC,
        {
            "hessian_max_diff_vs_lamH2": 0.0,
            "projected_n_negative": 0,
            "projected_n_zero": 4,
            "min_massive": 0.0004166666666023227,
            "S_H_plane_scan_min_gap": 0.002437890624999106,
            "lambda_H_values": ["2", "1/10", "1/100", "1/1000", "1/10000"],
        },
        "float64 live-compiler Hessian at q0 identical for every lambda_H (max difference 0), projected inertia 0 "
        "negative / 4 zero, lightest massive r0^2/96, and the (|S|, light doublet) plane scan minimum gap (all rows equal)",
        _E1,
        "float.<lam_H>.{hessian_max_diff_vs_lamH2, n_negative, n_zero, min_massive, S_H_plane_scan_min_gap}",
    ),
    "v4_kappa_correction_DA_prime": _record(
        _REC,
        {
            "BM-DA1": {"v_R_GeV": 1.2665e9, "v_S_GeV": 5.97e12, "lambda_H_minus_lambda_eff": 3.1647796547834696e-17},
            "BM-E": {"v_R_GeV": 5.7455e9, "v_S_GeV": 8.565e12, "lambda_H_minus_lambda_eff": 3.16389362011907e-15},
        },
        "lambda_H - lambda_eff = (v_R/v_S)^4/64 for kappa = -r0^2/(4 rS) in the research DA' convention (r0 <-> v_R, "
        "rS <-> v_S); independent verifier sympy check of the O36 H/S block",
        _V4,
        "kappa_correction_<BM>",
    ),
    "v_sos_sampling": _record(
        _REC,
        {"identity_residual": "0", "min_T6_normalised_over_samples": 6.48241811319652e-11, "samples": 200000},
        "independent verifier: sympy residual of the completed square and the minimum of the unreduced T6'/(1 + N^2 + "
        "|S|^4) over 2e5 random samples under a strict margin (sample count from the script, range(200000))",
        _VSOS,
        "identity_residual, min_T6_normalised_over_samples",
    ),
    "e3_lambda_H_required_BM_DA1": _record(
        _REC,
        {
            "v_R_GeV": 1266500000.0,
            "rho": 1000.0,
            "M_GUT_GeV": 1.5205e17,
            "lambda_SM_vR": 0.008012531557171942,
            "sigma_lambda_SM_vR": 0.0024409314596018196,
            "lambda_H_MGUT_required": {
                "W": 0.03587035516649833,
                "Tn": 0.07551527473789853,
                "T": 0.0835734776344113,
                "T0": 0.10377646692804587,
            },
            "threshold_band_minus_plus_0p004": {
                "W": [0.03117634502735243, 0.040733863802469045],
                "Tn": [0.07162825141381585, 0.07952126827486611],
                "T": [0.07989667174939727, 0.08735801200531641],
                "T0": [0.10072062718822597, 0.10691045968617448],
            },
            "inside_SOS_region_every_row": True,
        },
        "CONDITIONAL tree matching of lambda_SM(v_R) (PDG 2024, three-loop curve) through the one-loop PS-EFT running "
        "v_R..M_GUT: the required lambda_H(M_GUT) per Yukawa variant (W witness box, Tn top + Dirac nu, T top only, "
        "T0 no Yukawa) and with a +-0.004 one-loop threshold shift; the running uses D's anti-SOS Delta_R region point "
        "(rho = 1e3), i.e. assumes G6 fixed",
        _E3,
        "BM-DA1.variants.<V>.solutions.{central, central-0.004thr, central+0.004thr}.lam_H_MGUT_required",
    ),
    "e3_lambda_H_required_BM_E": _record(
        _REC,
        {
            "v_R_GeV": 5745500000.0,
            "rho": 316.22776601683796,
            "M_GUT_GeV": 1.0085e17,
            "lambda_SM_vR": 0.0044854129774534466,
            "sigma_lambda_SM_vR": 0.002565604386585357,
            "lambda_H_MGUT_required": {
                "W": 0.037762992965824346,
                "Tn": 0.07282846875416402,
                "T": 0.08004210589198844,
                "T0": 0.09840071936667158,
            },
            "threshold_band_minus_plus_0p004": {
                "W": [0.03307889525698535, 0.04259464961062117],
                "Tn": [0.06897721927060876, 0.07678368064288553],
                "T": [0.0763966428666798, 0.08378211491515931],
                "T0": [0.09534862700848327, 0.1015228304456413],
            },
            "inside_SOS_region_every_row": True,
        },
        "as e3_lambda_H_required_BM_DA1 at BM-E (rho = 10^2.5, D remnants); CONDITIONAL in the same way",
        _E3,
        "BM-E(rho=10^2.5, D remnants).variants.<V>.solutions.{central, central-0.004thr, central+0.004thr}.lam_H_MGUT_required",
    ),
    "e3b_sensitivity_lambda_H": _record(
        _REC,
        {
            "BM-DA1": {
                "T_baseline": 0.08357347748830186,
                "T_lam5x0.7": 0.10114336811206666,
                "T_lam5x1.3": 0.07429045082446034,
                "T_a1G=+0.02": 0.06551405762615649,
                "T_a1G=-0.02": 0.10730616550779959,
                "T_lh2G=+0.02": 0.06007554876745092,
                "T_lh2G=-0.02": 0.1103288069531027,
                "T_Delta_GUT_lo": 0.15705084064952124,
                "T_Delta_GUT_hi": 0.036707398525043906,
                "W_baseline": 0.035870356526868256,
                "W_lam5x0.7": 0.052754129953264166,
                "W_lam5x1.3": 0.026965471474800894,
                "W_a1G=+0.02": 0.01907523255527687,
                "W_a1G=-0.02": 0.05778901897688072,
                "W_lh2G=+0.02": 0.013001574173386024,
                "W_lh2G=-0.02": 0.06131754591852318,
                "W_Delta_GUT_lo": 0.10398442027507207,
                "W_Delta_GUT_hi": -0.009011563143015213,
            },
            "BM-E": {
                "T_baseline": 0.08004210609113097,
                "T_lam5x0.7": 0.09875756111801204,
                "T_lam5x1.3": 0.07013105379651838,
                "T_a1G=+0.02": 0.05737961638407827,
                "T_a1G=-0.02": 0.11156827133840559,
                "T_lh2G=+0.02": 0.057376859884218936,
                "T_lh2G=-0.02": 0.10547614509028466,
                "T_Delta_GUT_lo": 0.04904775579429955,
                "T_Delta_GUT_hi": 0.04156752069968334,
                "W_baseline": 0.03776299016688553,
                "W_lam5x0.7": 0.05624645175196802,
                "W_lam5x1.3": 0.027994239621913056,
                "W_a1G=+0.02": 0.01612635396270662,
                "W_a1G=-0.02": 0.06756150329603593,
                "W_lh2G=+0.02": 0.015367750372851808,
                "W_lh2G=-0.02": 0.062411304279985834,
                "W_Delta_GUT_lo": 0.007208890007870474,
                "W_Delta_GUT_hi": 5.812597394019914e-05,
            },
        },
        "sensitivity of the required lambda_H(M_GUT) to the Delta_R sector (lam_(35,5) x0.7/x1.3, D's lam_GUT corners) "
        "for Yukawa variants T and W, and to two GUT-threshold deformations that are NOT boundary conditions of the "
        "certified member: a1 = +-0.02 (an H-Sigma portal (D^+D)(h^+h) at M_GUT, not in the 27-parameter member map) "
        "and lh2 = +-0.02 (O36_B01 != O36_B02, not lambda_H N_H^2)",
        _E3B,
        "<BM>.rows.<row>.lam_H",
    ),
}
# Rows whose required lambda_H lies outside the certified domain (lambda_H <= (v_R/v_S)^4/64): disclosed.
DISCLOSED_OUTSIDE_DOMAIN = {"BM-DA1": ["W_Delta_GUT_hi"], "BM-E": []}
# Rows that are not boundary conditions of the certified member at all: a1 is an H-Sigma (126bar) portal at M_GUT,
# (D^+D)(h^+h), not in the 27-parameter member map; lh2 means O36_B01 != O36_B02, which is not lambda_H N_H^2.
_OUTSIDE_MEMBER_ROWS = sorted(f"{y}_{p}={s}0.02" for y in ("T", "W") for p in ("a1G", "lh2G") for s in ("+", "-"))
DISCLOSED_OUTSIDE_MEMBER = {"BM-DA1": list(_OUTSIDE_MEMBER_ROWS), "BM-E": list(_OUTSIDE_MEMBER_ROWS)}
E1_PROJECTION_RELATIVE_TOLERANCE = 1.0e-4
V4_RELATIVE_TOLERANCE = 1.0e-12

# ---------------------------------------------------------------------------
# Serialisation and small helpers.
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    return candidate._jsonable(value)


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _point_dict(point: Sequence[Any]) -> dict[str, str]:
    p = hessian.as_singlet_point(point)
    return {"r0": str(p.r0), "rS": str(p.rs), "x0": str(p.x0), "kappa": str(p.kappa)}


def load_report(path: Path) -> dict[str, Any]:
    """A committed JSON report, {} if missing or unreadable (fail-closed)."""
    return family.load_report(path)


def member_coefficients(
    point: Sequence[Any], lambda_h: Any, eps: Any = 0, *, o36_b02_offset: Any = 0
) -> dict[str, Any]:
    """The O36 member at (r0, rS, x0, kappa): the decoupled-singlet family map with O36_B01 = O36_B02 = lambda_H.

    ``o36_b02_offset`` (default 0) exists for the fail-closed mutation test O36_B01 != O36_B02 only."""
    p = hessian.as_singlet_point(point)
    output = dict(candidate.candidate_coefficients(p.r0, p.x0, p.kappa, o06_offset=eps, rs=p.rs))
    output[O36_B01] = Fraction(lambda_h)
    output[O36_B02] = Fraction(lambda_h) + Fraction(o36_b02_offset)
    return {key: value for key, value in output.items() if value != 0}


def symbolic_member_coefficients(r: Any, x: Any, kappa: Any, rs: Any, eps: Any, lambda_h: Any) -> dict[str, Any]:
    output = dict(candidate.candidate_coefficients(r, x, kappa, o06_offset=eps, rs=rs))
    output[O36_B01] = lambda_h
    output[O36_B02] = lambda_h
    return {key: value for key, value in output.items() if value != 0}


def _o36_overrides(lambda_h: Fraction, o36_b02_offset: Fraction = Fraction(0)) -> dict[str, Fraction]:
    return {O36_B01: Fraction(lambda_h), O36_B02: Fraction(lambda_h) + Fraction(o36_b02_offset)}


def clear_point_caches() -> None:
    """Clear the exact-Hessian point caches (not the unit matrices, which do not depend on the coefficients)."""
    hessian._exact_hessian_point_cached.cache_clear()
    hessian._exact_certificate_point_cached.cache_clear()


# ---------------------------------------------------------------------------
# (1) The H self-quartics (EXACT, sympy in 20 real variables).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def h_polynomials() -> dict[str, Any]:
    """N_H, H.H, I_1 = |H.H|^2/10, I_54 = sum_ij |H_i H_j - delta_ij H.H/10|^2 and the 45 current norm as sympy Polys
    in H_i = x_i + i y_i (i = 0..9); real and imaginary parts are expanded explicitly (no modulus identities)."""
    xs = sympy.symbols("x0:10", real=True)
    ys = sympy.symbols("y0:10", real=True)
    gens = tuple(xs) + tuple(ys)
    re_ = [sympy.Poly(symbol, *gens) for symbol in xs]
    im_ = [sympy.Poly(symbol, *gens) for symbol in ys]
    zero = sympy.Poly(0, *gens)
    tenth = sympy.Rational(1, 10)
    dot_re = sum((re_[i] * re_[i] - im_[i] * im_[i] for i in range(10)), zero)
    dot_im = sum((2 * re_[i] * im_[i] for i in range(10)), zero)
    n_h = sum((re_[i] * re_[i] + im_[i] * im_[i] for i in range(10)), zero)
    abs_dot_squared = dot_re * dot_re + dot_im * dot_im
    i_1 = abs_dot_squared * tenth
    i_54 = zero
    for i in range(10):
        for j in range(10):
            part_re = re_[i] * re_[j] - im_[i] * im_[j]
            part_im = re_[i] * im_[j] + re_[j] * im_[i]
            if i == j:
                part_re = part_re - dot_re * tenth
                part_im = part_im - dot_im * tenth
            i_54 = i_54 + part_re * part_re + part_im * part_im
    current = zero
    for i in range(10):
        for j in range(i + 1, 10):
            # conj(H_i) H_j - conj(H_j) H_i, real and imaginary parts
            c_re = (re_[i] * re_[j] + im_[i] * im_[j]) - (re_[j] * re_[i] + im_[j] * im_[i])
            c_im = (re_[i] * im_[j] - im_[i] * re_[j]) - (re_[j] * im_[i] - im_[j] * re_[i])
            current = current + c_re * c_re + c_im * c_im
    return {
        "xs": xs,
        "ys": ys,
        "gens": gens,
        "N_H": n_h,
        "abs_HdotH_squared": abs_dot_squared,
        "I_1": i_1,
        "I_54": i_54,
        "current_45": current,
    }


def _poly_value(poly: Any, assignment: Mapping[Any, Any]) -> Any:
    return sympy.nsimplify(poly.as_expr().subs({symbol: assignment.get(symbol, 0) for symbol in poly.gens}))


def h_self_section(
    member_points: Sequence[tuple[str, Any, Fraction]], o36_b02_offset: Fraction
) -> tuple[dict[str, Any], dict[str, bool]]:
    data = h_polynomials()
    n_h, i_1, i_54 = data["N_H"], data["I_1"], data["I_54"]
    identity = i_1 + i_54 - n_h * n_h
    cauchy = data["current_45"] - (n_h * n_h - data["abs_HdotH_squared"])
    degrees = {name: sorted({sum(monomial) for monomial in data[name].monoms()}) for name in ("I_1", "I_54")}
    homogeneous = all(value == [4] for value in degrees.values()) and not i_1.is_zero and not i_54.is_zero
    # a I_1 + b I_54 = c N_H^2 identically forces a = b = c: evaluate at a real unit vector and at the null vector.
    xs, ys = data["xs"], data["ys"]
    real_unit = {xs[0]: 1}
    null_vector = {xs[0]: 1, ys[1]: 1}  # H = e_0 + i e_1, H.H = 0
    a, b, c = sympy.symbols("a b c")
    equations = [
        a * _poly_value(i_1, point) + b * _poly_value(i_54, point) - c * _poly_value(n_h * n_h, point)
        for point in (real_unit, null_vector)
    ]
    solution = sympy.solve(equations, [a, c], dict=True)
    iff_ok = bool(len(solution) == 1 and sympy.simplify(solution[0][a] - b) == 0 and sympy.simplify(solution[0][c] - b) == 0)
    entries = {}
    for label, point, lambda_h in member_points:
        values = member_coefficients(point, lambda_h, o36_b02_offset=o36_b02_offset)
        entries[label] = {
            "O36_B01": values.get(O36_B01, Fraction(0)),
            "O36_B02": values.get(O36_B02, Fraction(0)),
            "equal_to_lambda_H": values.get(O36_B01) == values.get(O36_B02) == lambda_h,
        }
    checks = {
        "h_self_I1_plus_I54_equals_NH_squared_sympy_20_real_variables": bool(identity.is_zero),
        "h_self_NH2_minus_abs_HdotH2_equals_45_current_sum_of_squares_sympy": bool(cauchy.is_zero),
        "h_self_I1_I54_homogeneous_quartics_value_gradient_hessian_vanish_at_H0": bool(homogeneous),
        "h_self_quartic_multiple_of_NH2_iff_O36_B01_eq_O36_B02_and_member_entries_equal_lambda_H": bool(
            iff_ok and entries and all(row["equal_to_lambda_H"] for row in entries.values())
        ),
    }
    section = {
        "label": "EXACT",
        "variables": "H_i = x_i + i y_i, i = 0..9 (20 real sympy symbols); real and imaginary parts expanded explicitly",
        "definitions": {
            "I_1": "|H.H|^2/10 (O36_B01, exact_h10_self_quartic_family_v20)",
            "I_54": "sum_ij |H_i H_j - delta_ij (H.H)/10|^2 (O36_B02)",
            "N_H": "H^dag H",
        },
        "I1_plus_I54_minus_NH2": str(identity.as_expr()),
        "I1_terms": len(i_1.terms()),
        "I54_terms": len(i_54.terms()),
        "cauchy_schwarz_identity": "N_H^2 - |H.H|^2 = sum_{i<j} |conj(H_i) H_j - conj(H_j) H_i|^2 (so |H.H| <= N_H)",
        "cauchy_schwarz_residual": str(cauchy.as_expr()),
        "monomial_degrees": degrees,
        "hessian_at_H0": "every monomial of I_1 and I_54 has degree 4, so their value, gradient and Hessian vanish at "
        "H = 0 (the O36 binding units of g3_sm_pati_salam_exact_hessian_v20 have empty pieces for this reason)",
        "iff_statement": "a I_1 + b I_54 = b N_H^2 + (a - b) I_1; at H = e_0 (I_1 = 1/10, N_H^2 = 1) and at the null "
        "vector H = e_0 + i e_1 (I_1 = 0, N_H^2 = 4) the identity a I_1 + b I_54 = c N_H^2 forces a = c = b",
        "iff_solution": {str(key): str(value) for key, value in solution[0].items()} if len(solution) == 1 else None,
        "member_entries": entries,
        "consequence": "the member's H quartic lambda_H (I_1 + I_54) is lambda_H N_H^2 exactly",
    }
    return section, checks


# ---------------------------------------------------------------------------
# (2) The SOS identity with T6' (EXACT, sympy symbolic in lambda_H, lambda_S, rS, k = |kappa|, eps).
# ---------------------------------------------------------------------------


def _hs_symbols() -> tuple[Any, ...]:
    return (
        sympy.Symbol("N_H", nonnegative=True),
        sympy.Symbol("s", nonnegative=True),  # |S|
        sympy.Symbol("rS", positive=True),
        sympy.Symbol("lambda_H", positive=True),
        sympy.Symbol("lambda_S", positive=True),
        sympy.Symbol("k", nonnegative=True),  # |kappa|
        sympy.Symbol("eps", nonnegative=True),
    )


def hs_reduced_form(n: Any, s: Any, rs: Any, l_h: Any, l_s: Any, k: Any, eps: Any) -> Any:
    """T6' after Cauchy-Schwarz (2 kappa Re(conj(H.H) conj(S)) >= -2|kappa| N_H |S|)."""
    return l_h * n**2 + 2 * k * n * (rs - s) + l_s * (s**2 - rs**2) ** 2 + eps * n


def hs_completed_square(n: Any, s: Any, rs: Any, l_h: Any, l_s: Any, k: Any, eps: Any) -> Any:
    """The completed square of the reduced form in N_H (t = |S| - rS, u = |S| + rS)."""
    t, u = s - rs, s + rs
    return l_h * (n - k * t / l_h) ** 2 + t**2 * (l_s * u**2 - k**2 / l_h) + eps * n


def _t6_operator_forms(sign: str, lam: Any, s: Any, e: Any) -> dict[str, Any]:
    """T6 (family, as in g3_sm_pati_salam_equality_set_v20), T9 = eps N_H and T6' in the operator dictionary."""
    op = equality._operator_dictionary()
    k = family._kappa_symbol(sign)
    abs_k = sympy.Abs(k)
    t6 = 2 * op[O36_B01] + 2 * op[O36_B02] + 2 * abs_k * s * op[O06] + k * op[O12] + op[O23] - 2 * s**2 * op[O04] + s**4
    t9 = e * op[O06]
    l_s = sympy.Rational(LAMBDA_S.numerator, LAMBDA_S.denominator)
    t6_prime = lam * (op[O36_B01] + op[O36_B02]) + (2 * abs_k * s + e) * op[O06] + k * op[O12] + l_s * (
        op[O23] - 2 * s**2 * op[O04] + s**4
    )
    return {"op": op, "kappa": k, "T6": t6, "T9": t9, "T6_prime": t6_prime}


def sos_section(
    member_points: Sequence[tuple[str, Any, Fraction]], self_weights: Mapping[str, Fraction]
) -> tuple[dict[str, Any], dict[str, bool]]:
    n, s, rs, l_h, l_s, k, eps = _hs_symbols()
    t, u = s - rs, s + rs
    reduced = hs_reduced_form(n, s, rs, l_h, l_s, k, eps)
    completed = hs_completed_square(n, s, rs, l_h, l_s, k, eps)
    residual = sympy.simplify(sympy.expand(reduced - completed))
    committed_completed = 2 * (n - k * t / 2) ** 2 + t**2 * (4 * rs**2 - k**2 / 2 + t * (t + 4 * rs))
    committed_reduced = 2 * n**2 + 2 * k * rs * n - 2 * k * n * s + (s**2 - rs**2) ** 2
    at_two = {l_h: 2, l_s: 1, eps: 0}
    reduction = {
        "completed_square_at_lambda_H_2_minus_committed": str(sympy.expand(completed.subs(at_two) - committed_completed)),
        "reduced_form_at_lambda_H_2_minus_committed": str(sympy.expand(reduced.subs(at_two) - committed_reduced)),
        "committed_identity_residual_candidate": candidate._hs_square_completion_residual(),
    }
    bracket = l_s * u**2 - k**2 / l_h
    margin_form = 4 * l_s * rs**2 - k**2 / l_h
    sign_identities = {
        "bracket_minus_margin_minus_lambda_S_t_(t+4rS)": str(sympy.expand(bracket - margin_form - l_s * t * (t + 4 * rs))),
        "reduced_minus_nonpositive_t_form": str(
            sympy.expand(reduced - (l_h * n**2 + 2 * k * n * (-t) + l_s * t**2 * u**2 + eps * n))
        ),
        "lambda_H_margin_form_minus_(4 lambda_H lambda_S rS^2 - k^2)": str(
            sympy.expand(l_h * margin_form - (4 * l_h * l_s * rs**2 - k**2))
        ),
    }
    boundary = sympy.factor(sympy.expand(bracket.subs(k, 2 * sympy.sqrt(l_h * l_s) * rs)))
    boundary_residual = sympy.expand(boundary - l_s * t * (s + 3 * rs))
    lambda_eff_closed = l_h - k**2 / (4 * l_s * rs**2)
    margin_equivalence = sympy.expand(4 * l_s * rs**2 * lambda_eff_closed - (4 * l_h * l_s * rs**2 - k**2))

    # Operator level: the family's eight-term expansion (reused), the member map vs the family SOS map, and T6'.
    r, x = sympy.symbols("r0 x0", positive=True)
    s_sym = sympy.Symbol("rS", positive=True)
    e_sym = sympy.Symbol("eps", nonnegative=True)
    lam = sympy.Symbol("lambda_H", positive=True)
    expansion = equality._eight_term_expansion(dict(self_weights), rs=s_sym, eps=e_sym)
    rows = expansion["by_kappa_sign"]
    # kappa enters the family's SOS terms only through T6: every other term is the same for the three kappa signs and
    # contains no kappa symbol (no operator of the dictionary is named with "kappa").
    term_texts = {sign: rows[sign]["terms_in_operators"] for sign in ("negative", "positive", "zero")}
    non_t6 = {sign: {name: text for name, text in texts.items() if not name.startswith("T6")} for sign, texts in term_texts.items()}
    t6_texts = {sign: [text for name, text in texts.items() if name.startswith("T6")] for sign, texts in term_texts.items()}
    op_names_free_of_kappa = all("kappa" not in str(symbol) for symbol in equality._operator_dictionary().values())
    kappa_free = bool(
        op_names_free_of_kappa
        and non_t6["negative"] == non_t6["positive"] == non_t6["zero"]
        and len(non_t6["negative"]) == 8  # T1-T5, T7, T8 and T9 = eps N_H
        and all("kappa" not in text for texts in non_t6.values() for text in texts.values())
        and all(len(t6_texts[sign]) == 1 and "kappa" in t6_texts[sign][0] for sign in ("negative", "positive"))
        and len(t6_texts["zero"]) == 1 and "kappa" not in t6_texts["zero"][0]
    )
    family_rows_ok = {
        sign: bool(
            rows[sign]["matches_operator_by_operator_and_constant_is_minus_V0"]
            and rows[sign]["operators_compared"] == family.SOS_OPERATOR_COUNTS[sign]
            and rows[sign]["constant_plus_V0"] == "0"
        )
        for sign in ("negative", "positive", "zero")
    }
    map_differences = {}
    map_ok = {}
    t6_rows = {}
    t6_ok = {}
    for sign in ("negative", "positive", "zero"):
        kappa = family._kappa_symbol(sign)
        member = symbolic_member_coefficients(r, x, kappa, s_sym, e_sym, lam)
        expected = dict(candidate.expanded_sos_coefficient_map(r, x, kappa, rs=s_sym))
        expected[O06] = expected.get(O06, 0) + e_sym
        difference = family._map_difference(member, expected)
        map_differences[sign] = {key: str(value) for key, value in difference.items()}
        map_ok[sign] = bool(
            set(difference) == {O36_B01, O36_B02}
            and all(sympy.simplify(value - (lam - 2)) == 0 for value in difference.values())
        )
        forms = _t6_operator_forms(sign, lam, s_sym, e_sym)
        op = forms["op"]
        shift = sympy.expand(forms["T6_prime"] - forms["T6"] - forms["T9"] - (lam - 2) * (op[O36_B01] + op[O36_B02]))
        coefficients = {
            key: sympy.simplify(sympy.expand(forms["T6_prime"]).coeff(op[key]) - candidate._as_sympy(member.get(key, 0)))
            for key in H_S_IDS
        }
        constant = sympy.expand(forms["T6_prime"].subs({symbol: 0 for symbol in op.values()}))
        others = sympy.expand(forms["T6_prime"]).free_symbols & (set(op.values()) - {op[key] for key in H_S_IDS})
        t6_rows[sign] = {
            "T6_prime": str(forms["T6_prime"]),
            "T6_prime_minus_T6_minus_T9_minus_(lambda_H-2)(I1+I54)": str(shift),
            "H_S_coefficient_residuals_vs_member_map": {key: str(value) for key, value in coefficients.items()},
            "constant": str(constant),
            "operators_outside_H_S_block": sorted(str(symbol) for symbol in others),
        }
        t6_ok[sign] = bool(
            shift == 0
            and all(value == 0 for value in coefficients.values())
            and sympy.expand(constant - s_sym**4) == 0
            and not others
        )
    checks = {
        "sos_hs_completed_square_identity_symbolic_residual_zero": residual == 0,
        "sos_hs_completed_square_reduces_to_committed_identity_at_lambda_H_2_lambda_S_1": bool(
            all(value == "0" for value in reduction.values())
        ),
        "sos_hs_sign_argument_identities_exact": all(value == "0" for value in sign_identities.values()),
        "sos_hs_boundary_bracket_equals_lambda_S_t_times_s_plus_3rS": boundary_residual == 0,
        "sos_hs_margin_equivalent_to_lambda_eff_positive_symbolic": margin_equivalence == 0,
        "sos_family_eight_term_expansion_passes_three_kappa_signs": bool(expansion["passes"] and all(family_rows_ok.values())),
        "sos_member_map_equals_family_sos_map_plus_eps_except_O36_equal_lambda_H_three_signs": all(map_ok.values()),
        "sos_T6_prime_equals_T6_plus_T9_plus_lambda_H_minus_2_times_I1_plus_I54_three_signs": all(t6_ok.values()),
        "sos_non_T6_terms_kappa_free_three_signs": kappa_free,
    }
    section = {
        "label": "EXACT",
        "symbols": "N_H >= 0, s = |S| >= 0, rS > 0, lambda_H > 0, lambda_S > 0, k = |kappa| >= 0, eps >= 0 (sympy); "
        "kappa < 0, > 0 and = 0 for the operator-level rows",
        "T6_prime": "lambda_H N_H^2 + (2|kappa| rS + eps) N_H + 2 kappa Re(conj(H.H) conj(S)) + lambda_S (|S|^2 - rS^2)^2 "
        "(lambda_S = O23 = 1 in the map; O04 = -2 lambda_S rS^2)",
        "cauchy_schwarz": "2 kappa Re(conj(H.H) conj(S)) >= -2|kappa| |H.H| |S| >= -2|kappa| N_H |S| (|H.H| <= N_H: "
        "h_self.cauchy_schwarz_identity), so T6' >= R(N_H, |S|)",
        "reduced_form": "R = lambda_H N^2 + 2 k N (rS - s) + lambda_S (s^2 - rS^2)^2 + eps N",
        "completed_square": "R = lambda_H (N - k t/lambda_H)^2 + t^2 (lambda_S u^2 - k^2/lambda_H) + eps N, t = s - rS, "
        "u = s + rS",
        "completed_square_residual": str(residual),
        "reduction_to_committed": reduction,
        "sign_argument": "t >= 0: u >= 2 rS, so the bracket is >= 4 lambda_S rS^2 - k^2/lambda_H + lambda_S t (t + 4 rS) "
        "> 0 when k^2 < 4 lambda_H lambda_S rS^2, hence R > 0 unless t = 0 and N = 0; t < 0: R = lambda_H N^2 + 2 k N "
        "|t| + lambda_S t^2 u^2 + eps N with every term >= 0 and lambda_S t^2 u^2 > 0 (u > 0).  Zero set: t = 0, N_H = 0, "
        "i.e. H = 0 and |S| = rS",
        "sign_identities": sign_identities,
        "domain": "kappa^2 < 4 lambda_H lambda_S rS^2, equivalently lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) > 0",
        "margin_equivalence_residual": str(margin_equivalence),
        "boundary_bracket_at_k2_eq_4_lambda_H_lambda_S_rS2": str(boundary),
        "boundary_note": "at kappa^2 = 4 lambda_H lambda_S rS^2 (lambda_eff = 0) the bracket is lambda_S t (s + 3 rS) >= 0 "
        "for t >= 0 and the t < 0 argument is unchanged, so V >= V0 and the equality set still hold on the boundary; "
        "the certified domain is the open kappa^2 < 4 lambda_H lambda_S rS^2 (the committed convention)",
        "operator_level": {
            "family_eight_term_expansion_passes": expansion["passes"],
            "family_rows_ok": family_rows_ok,
            "operators_compared_by_sign": {sign: rows[sign]["operators_compared"] for sign in rows},
            "non_T6_terms_kappa_free": {
                "terms": sorted(non_t6["negative"]),
                "identical_for_the_three_kappa_signs": non_t6["negative"] == non_t6["positive"] == non_t6["zero"],
                "meaning": "kappa enters the SOS map only through O06 and O12, i.e. T6; T1-T5, T7, T8 and T9 are "
                "kappa-free, which the equality-set argument uses for lambda_H > 2",
            },
            "member_map_minus_family_sos_map_plus_eps": map_differences,
            "T6_prime_rows": t6_rows,
            "statement": "V_member - V0 = T1 + ... + T5 + T6' + T7 + T8 with T6' = T6 + T9 + (lambda_H - 2)(I_1 + I_54) = "
            "T6 + T9 + (lambda_H - 2) N_H^2 (the family's eight-term identity plus the H self-identity)",
        },
    }
    return section, checks


# ---------------------------------------------------------------------------
# (3) Sharpness (EXACT).
# ---------------------------------------------------------------------------


def t6_prime_on_curve(
    rs: Fraction, kappa: Fraction, t: Fraction, n_h: Fraction, lambda_h: Fraction, l_s: Fraction = LAMBDA_S, eps: Fraction = Fraction(0)
) -> Fraction:
    """V - V0 = T6' at H = h e_6 (h real, h^2 = n_h), S = rS + t real, kappa < 0 (T9 = eps N_H included): exact."""
    s_abs = rs + t
    return (
        lambda_h * n_h * n_h + 2 * abs(kappa) * rs * n_h + 2 * kappa * n_h * s_abs + l_s * (s_abs * s_abs - rs * rs) ** 2
        + eps * n_h
    )


def eps_domain_section() -> tuple[dict[str, Any], bool]:
    """eps > 0: exact minimisation of the reduced H/S form over N_H >= 0 and the exact domain |kappa| <= 2c rS +
    sqrt(2 c eps), c = sqrt(lambda_H lambda_S) (sympy identities plus exact rows at c = 1/10)."""
    n, s, rs, l_h, l_s, k, eps = _hs_symbols()
    c = sympy.Symbol("c", positive=True)
    t = sympy.Symbol("t", positive=True)
    u = t + 2 * rs
    delta = k - 2 * c * rs
    reduced = hs_reduced_form(n, rs + t, rs, l_h, c**2 / l_h, k, eps)
    n_star = (2 * k * t - eps) / (2 * l_h)
    r_min = c**2 / l_h * t**2 * u**2 - (2 * k * t - eps) ** 2 / (4 * l_h)
    g = 2 * c * t**2 - 2 * delta * t + eps
    identities = {
        "reduced_at_N_star_minus_R_min": sympy.simplify(sympy.expand(reduced.subs(n, n_star) - r_min)),
        "reduced_minus_R_min_minus_lambda_H_(N-N_star)^2": sympy.simplify(
            sympy.expand(reduced - r_min - l_h * (n - n_star) ** 2)
        ),
        "4_lambda_H_R_min_minus_g_times_(2c t u + 2k t - eps)": sympy.simplify(
            sympy.expand(4 * l_h * r_min - g * (2 * c * t * u + 2 * k * t - eps))
        ),
        "discriminant_of_g_in_t_minus_4(delta^2 - 2 c eps)": sympy.simplify(
            sympy.expand(sympy.discriminant(g, t) - 4 * (delta**2 - 2 * c * eps))
        ),
    }
    rows = []
    rows_ok = True
    for lambda_h, k_abs, e, violates in EPS_SHARPNESS_ROWS:
        cc = EPS_SHARPNESS_C
        d = k_abs - 2 * cc * SHARPNESS_RS
        disc = 4 * (d * d - 2 * cc * e)
        row: dict[str, Any] = {
            "rS": SHARPNESS_RS, "lambda_H": lambda_h, "lambda_S": LAMBDA_S, "abs_kappa": k_abs, "eps": e,
            "c_squared_equals_lambda_H_lambda_S": cc * cc == lambda_h * LAMBDA_S,
            "margin_4_lambda_H_lambda_S_rS2_minus_kappa2": 4 * lambda_h * LAMBDA_S * SHARPNESS_RS**2 - k_abs * k_abs,
            "delta": d, "discriminant_of_g": disc, "expected_violation": violates,
        }
        ok = bool(row["c_squared_equals_lambda_H_lambda_S"] and row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"] < 0 and d > 0)
        if violates:
            t_star = d / (2 * cc)
            n_h = (2 * k_abs * t_star - e) / (2 * lambda_h)
            value = t6_prime_on_curve(SHARPNESS_RS, -k_abs, t_star, n_h, lambda_h, eps=e)
            closed = (cc * cc / lambda_h) * t_star**2 * (t_star + 2 * SHARPNESS_RS) ** 2 - (2 * k_abs * t_star - e) ** 2 / (4 * lambda_h)
            row.update({"t_star": t_star, "h_squared": n_h, "V_minus_V0_equals_T6_prime": value, "R_min_closed_form": closed})
            ok = ok and disc > 0 and n_h > 0 and value < 0 and value == closed
        else:
            ok = ok and disc < 0  # g > 0 for every t, so R >= 0: V >= V0 holds beyond the eps = 0 margin
        row["consistent"] = ok
        rows.append(row)
        rows_ok = rows_ok and ok
    passed = bool(all(value == 0 for value in identities.values()) and rows_ok)
    section = {
        "label": "EXACT",
        "statement": "for eps > 0 the certified margin kappa^2 < 4 lambda_H lambda_S rS^2 is sufficient but not sharp: "
        "with c = sqrt(lambda_H lambda_S) and delta = |kappa| - 2 c rS the reduced form is lambda_H (N - N*)^2 + R_min, "
        "N* = (2|kappa| t - eps)/(2 lambda_H), 4 lambda_H R_min = (2c t^2 - 2 delta t + eps)(2c t u + 2|kappa| t - eps); "
        "so V >= V0 holds exactly iff |kappa| <= 2 c rS + sqrt(2 c eps) (discriminant 4(delta^2 - 2 c eps)), with the "
        "equality set unchanged strictly inside; beyond it the curve H = h e_6, S = rS + t* with t* = delta/(2c) "
        "violates.  This extension is exact but is not a completed-square SOS certificate, and no member point uses it",
        "identities": {key: str(value) for key, value in identities.items()},
        "rows": rows,
    }
    return section, passed


def exact_violating_point(point: Sequence[Any], lambda_h: Fraction, l_s: Fraction = LAMBDA_S) -> dict[str, Any] | None:
    """For kappa^2 > 4 lambda_H lambda_S rS^2: an exact rational point on the curve with V - V0 < 0 (else None)."""
    p = hessian.as_singlet_point(point)
    k = abs(p.kappa)
    if k * k <= 4 * lambda_h * l_s * p.rs * p.rs:
        return None
    for power in range(1, 80):
        t = p.rs / 2**power
        formula = t * t * (l_s * (2 * p.rs + t) ** 2 - k * k / lambda_h)
        if formula < 0:
            n_h = k * t / lambda_h
            direct = t6_prime_on_curve(p.rs, -k, t, n_h, lambda_h, l_s)
            return {
                "t": t,
                "S_value": p.rs + t,
                "h_squared": n_h,
                "V_minus_V0": direct,
                "curve_formula": formula,
                "negative_and_equal": bool(direct < 0 and direct == formula),
                "direction": "H = h e_6 (real doublet; H = i h e_6 for kappa > 0), S = rS + t, other fields at q0",
            }
    return None


def sharpness_section(witnesses: Sequence[tuple[Fraction, Fraction, Fraction, Fraction]]) -> tuple[dict[str, Any], dict[str, bool]]:
    n, s, rs, l_h, l_s, k, eps = _hs_symbols()
    t = sympy.Symbol("t", positive=True)
    reduced = hs_reduced_form(n, s, rs, l_h, l_s, k, eps)
    on_curve = reduced.subs({n: k * t / l_h, s: rs + t, eps: 0})
    curve = sympy.expand(on_curve - t**2 * (l_s * (2 * rs + t) ** 2 - k**2 / l_h))
    q_h = np.asarray(hessian.h_wedge_data()["Q_H"])
    wedge_zero = bool(hessian.h_wedge_data()["Q_H_is_diag_1x6_0x4"] and not np.any(q_h[6, :]) and not np.any(q_h[:, 6]))
    rows = []
    for lambda_h, k_abs, step, expected in witnesses:
        n_h = k_abs * step / lambda_h
        direct = t6_prime_on_curve(SHARPNESS_RS, -k_abs, step, n_h, lambda_h)
        formula = step * step * (LAMBDA_S * (2 * SHARPNESS_RS + step) ** 2 - k_abs * k_abs / lambda_h)
        rows.append(
            {
                "rS": SHARPNESS_RS,
                "lambda_H": lambda_h,
                "abs_kappa": k_abs,
                "t": step,
                "margin_4_lambda_H_lambda_S_rS2_minus_kappa2": 4 * lambda_h * LAMBDA_S * SHARPNESS_RS**2 - k_abs * k_abs,
                "h_squared": n_h,
                "V_minus_V0_equals_T6_prime": direct,
                "curve_formula": formula,
                "expected": expected,
                "negative": direct < 0,
            }
        )
    witnesses_ok = bool(
        rows
        and all(
            row["V_minus_V0_equals_T6_prime"] == row["curve_formula"] == row["expected"]
            and row["negative"]
            and row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"] < 0
            for row in rows
        )
    )
    eps_domain, eps_ok = eps_domain_section()
    checks = {
        "sharpness_curve_identity_exact": curve == 0,
        "sharpness_violating_points_exact_beyond_margin": witnesses_ok,
        "sharpness_other_sos_terms_vanish_on_curve_Q_H_row_and_column_6_zero": wedge_zero,
        "sharpness_only_at_eps_0_exact_eps_positive_domain": eps_ok,
    }
    section = {
        "label": "EXACT",
        "curve": "H = h e_6 real (weak-doublet direction), S = rS + t real, kappa < 0, N_H = h^2 = |kappa| t/lambda_H: "
        "V - V0 = t^2 [lambda_S (2 rS + t)^2 - kappa^2/lambda_H] (for kappa > 0 the same with H = i h e_6)",
        "curve_identity_residual": str(curve),
        "other_sos_terms_vanish": "T1-T5 and T8 involve only (Phi, Sigma, Phi17) at their vacuum values; T7 = ||H wedge "
        "p||^2 = h^2 Q_H[6,6] = 0 (Q_H = diag(1^6, 0^4), integer); so V - V0 = T6' exactly on the curve (T9 = eps N_H "
        "is part of T6'), and at eps = 0 V >= V0 fails for every kappa^2 > 4 lambda_H lambda_S rS^2 (0 < t < "
        "|kappa|/sqrt(lambda_H lambda_S) - 2 rS); for eps > 0 see eps_positive_domain",
        "Q_H_row_and_column_6_zero": wedge_zero,
        "violating_witnesses": rows,
        "eps_positive_domain": eps_domain,
    }
    return section, checks


# ---------------------------------------------------------------------------
# (4) + (6) Member points: map, margin, lambda_eff and the exact 486 x 486 Hessian.
# ---------------------------------------------------------------------------


def _certificate_ok(summary: Mapping[str, Any], variant: str, point: hessian.SingletPoint) -> bool:
    if variant == "benchmark":
        return bool(
            summary["gradient_exactly_zero"]
            and summary["exactly_symmetric"]
            and summary["coverage_ok"]
            and summary["inertia_positive_zero_negative"] == "447/39/0"
            and summary["kernel_equals_expected_span"]
            and summary["strictly_positive_on_kernel_complement"]
            and summary["smallest_nonzero_eigenvalue"] == hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * point.r0 * point.r0
            and summary["is_smallest"]
            and summary["multiplicity"] == 14
        )
    return bool(
        summary["gradient_exactly_zero"]
        and summary["exactly_symmetric"]
        and summary["coverage_ok"]
        and summary["inertia_positive_zero_negative"] == "451/35/0"
        and summary["kernel_equals_expected_span"]
        and summary["strictly_positive_on_symmetry_quotient"]
        and summary["strictly_positive_on_kernel_complement"]
        and summary["smallest_nonzero_eigenvalue"] == hessian.variant_offset(variant, point)
        and summary["is_smallest"]
        and summary["multiplicity"] == candidate.LIGHT_DOUBLET_REAL_DIMENSION
    )


def _is_witness_point(point: hessian.SingletPoint) -> bool:
    return point == hessian.as_singlet_point(WITNESS_POINT)


def member_point_section(
    label: str, point: Sequence[Any], lambda_h: Fraction, o36_b02_offset: Fraction, contract_ids: set[str]
) -> tuple[dict[str, Any], dict[str, bool], dict[str, Any]]:
    p = hessian.as_singlet_point(point)
    lambda_h = Fraction(lambda_h)
    values = member_coefficients(p, lambda_h, o36_b02_offset=o36_b02_offset)
    family_values = family.family_coefficients(p)
    changed = sorted(key for key in set(values) | set(family_values) if values.get(key, Fraction(0)) != family_values.get(key, Fraction(0)))
    map_ok = bool(
        len(values) == candidate.EXPECTED_NONZERO
        and set(values) <= contract_ids
        and not (set(family.S_PORTAL_IDS) & set(values))
        and set(changed) <= {O36_B01, O36_B02}
        and values.get(O36_B01) == lambda_h
        and (lambda_h == 2 or O36_B01 in changed)
    )
    margin = 4 * lambda_h * LAMBDA_S * p.rs * p.rs - p.kappa * p.kappa
    shift = candidate.exact_light_doublet_quartic(p.r0, p.kappa, rs=p.rs)["S_exchange_shift"]  # kappa^2/(4 rS^2), lambda_S = 1
    lambda_eff = lambda_h - p.kappa * p.kappa / (4 * LAMBDA_S * p.rs * p.rs)
    expected = EXPECTED_POINT_VALUES.get(label)
    margin_ok = bool(
        margin > 0
        and lambda_eff > 0
        and lambda_eff == lambda_h - shift
        and lambda_eff == margin / (4 * LAMBDA_S * p.rs * p.rs)
        and (expected is None or (margin, lambda_eff) == expected)
    )
    upper = hessian.eps_perturbative_upper(p.kappa, p.rs)
    maximum = max(abs(value) for value in values.values())
    violating = exact_violating_point(p, lambda_h)

    overrides = _o36_overrides(lambda_h, o36_b02_offset)
    identity = {}
    applied = True
    for variant in VARIANTS:
        member = hessian.exact_hessian(variant, overrides, point=p)
        reference = hessian.exact_hessian(variant, point=p)  # the lambda_H = 2 family member
        (num, den), (ref_num, ref_den) = member["hessian"], reference["hessian"]
        (grad, grad_den), (ref_grad, ref_grad_den) = member["gradient"], reference["gradient"]
        coverage = member["coverage"]
        applied = applied and member["coefficients"].get(O36_B01) == overrides[O36_B01]
        identity[variant] = {
            "hessian_numerator_identical": bool(np.array_equal(num, ref_num)),
            "hessian_denominator_identical": int(den) == int(ref_den),
            "gradient_identical": bool(np.array_equal(grad, ref_grad) and int(grad_den) == int(ref_grad_den)),
            "gradient_exactly_zero": not any(int(value) for value in np.asarray(grad).flat),
            "coverage_ok": bool(
                coverage["coefficients_proportional_to_unit_weights"]
                and coverage["every_nonzero_parameter_covered"]
                and coverage["no_parameter_in_two_units"]
                and not coverage["units_parameters_not_in_benchmark"]
            ),
            "denominator": int(den),
        }
    identity_ok = bool(applied and all(all(value for key, value in row.items() if key != "denominator") for row in identity.values()))
    certificates = {variant: hessian.exact_certificate(variant, overrides, point=p) for variant in VARIANTS}
    summaries = {variant: family._certificate_summary(certificates[variant], hessian.variant_offset(variant, p)) for variant in VARIANTS}
    checks = {
        "member_map_27_parameters_in_contract_changes_only_O36_vs_family_map": map_ok,
        "margin_positive_and_lambda_eff_closed_form": margin_ok,
        "hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants": identity_ok,
        "benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14": _certificate_ok(summaries["benchmark"], "benchmark", p),
        "raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4": _certificate_ok(summaries["raised_O06"], "raised_O06", p),
    }
    record = {
        "point": _point_dict(p),
        "lambda_H": lambda_h,
        "is_committed_witness_point": _is_witness_point(p),
        "changed_vs_family_map": {key: {"family": family_values.get(key, Fraction(0)), "member": values.get(key, Fraction(0))} for key in changed},
        "nonzero_count": len(values),
        "V0": candidate.lower_bound_v0(p.r0, p.x0, rs=p.rs),
        "margin_4_lambda_H_lambda_S_rS2_minus_kappa2": margin,
        "lambda_eff": lambda_eff,
        "candidate_S_exchange_shift_kappa2_over_4rS2": shift,
        "lambda_eff_minus_lambda_H": lambda_eff - lambda_h,
        "exact_violating_point": violating,
        "perturbative_box": {
            "bound": hessian.PERTURBATIVE_BOUND,
            "max_abs_coefficient": maximum,
            "eps_window_upper_exclusive": upper,
            "eps_window_nonempty": upper > 0,
            "perturbative_member": bool(maximum < hessian.PERTURBATIVE_BOUND and upper > 0),
        },
        "hessian_identity_vs_lambda_H_2": identity,
        "certificates": summaries,
        "hessian_note": "O36 is quartic in H: its binding units have empty pieces, so the exact H_u, gradient and "
        "certificates equal those of the lambda_H = 2 member bit for bit; the global statement rests on the SOS "
        "identity (the Hessian cannot detect a margin violation)",
    }
    return record, checks, certificates


# ---------------------------------------------------------------------------
# (5) V0, equality set and the committed artifacts (EXACT bindings).
# ---------------------------------------------------------------------------


def equality_section(
    member_points: Sequence[tuple[str, Any, Fraction]],
    equality_report: Mapping[str, Any] | None,
    family_report: Mapping[str, Any] | None,
    t6_constants_ok: bool,
) -> tuple[dict[str, Any], dict[str, bool]]:
    report = hessian.load_equality_report() if equality_report is None else equality_report
    premises = hessian.equality_premises(report)
    fam = load_report(family.OUT_JSON) if family_report is None else family_report
    fam_checks = fam.get("checks") if isinstance(fam.get("checks"), Mapping) else {}
    fam_flags = fam.get("flags") if isinstance(fam.get("flags"), Mapping) else {}
    fam_float = fam.get("float_evidence") if isinstance(fam.get("float_evidence"), Mapping) else {}
    fam_float_checks = fam_float.get("checks") if isinstance(fam_float.get("checks"), Mapping) else {}
    f1 = fam_float.get("F1_live_compiler_at_rS_1_kappa_minus_1_over_100") if isinstance(fam_float, Mapping) else None
    f1_point = f1.get("point") if isinstance(f1, Mapping) else None
    family_binding = {
        "status_certified": fam.get("status") == family.STATUS_CERTIFIED,
        "n_checks_77": fam.get("n_checks") == FAMILY_EXPECTED_N_CHECKS == family.EXPECTED_N_CHECKS and len(fam_checks) == FAMILY_EXPECTED_N_CHECKS,
        "n_failed_0": fam.get("n_failed") == 0 and fam.get("failures") == [],
        "all_checks_true": bool(fam_checks) and all(value is True for value in fam_checks.values()),
        "family_theorem_claimed": fam_flags.get("family_theorem_claimed") is True,
        "float_evidence_consistent": fam_flags.get("float_evidence_consistent") is True,
        "F1_live_compiler_equals_exact_at_keeps_point": bool(
            fam_float_checks.get(family.FLOAT_CHECK_NAMES[0]) is True and f1_point == _point_dict(KEEPS_POINT)
        ),
        "tangent_ranks_and_p3_checks_true": bool(fam_checks)
        and all(value is True for key, value in fam_checks.items() if key.startswith(("tangent_ranks_", "p3_family_"))),
    }
    witness_ids = set(candidate.candidate_coefficients(R0, X0))
    operator_ids = {row["parameter"] for row in equality.operator_data()["operators"]}
    rows = hessian._get(report, "P3_H_S_Phi17_phases", "operators", "operators", default=[])
    committed_ids = {row.get("parameter") for row in rows if isinstance(row, Mapping)} if isinstance(rows, list) else set()
    point_ids = {label: set(member_coefficients(point, lambda_h)) == witness_ids for label, point, lambda_h in member_points}
    r, x = sympy.symbols("r0 x0", positive=True)
    s = sympy.Symbol("rS", positive=True)
    lam = sympy.Symbol("lambda_H", positive=True)
    v0 = candidate.lower_bound_v0(r, x, rs=s)
    v0_ok = bool(
        t6_constants_ok
        and sympy.diff(v0, lam) == 0
        and sympy.simplify(v0 + 1 + r**4 / 8 + s**4 + x**4 / 32) == 0
    )
    checks = {
        "member_V0_equals_family_V0_lambda_H_free_symbolic": v0_ok,
        "equality_set_premises_from_committed_report": bool(premises) and all(premises.values()),
        "committed_family_report_certified_77_checks_0_failed_float_consistent": all(family_binding.values()),
        "member_operator_ids_equal_witness_and_committed_P3_operator_ids": bool(
            witness_ids == operator_ids == committed_ids and point_ids and all(point_ids.values())
        ),
    }
    section = {
        "label": "EXACT (committed-artifact bindings fail closed)",
        "V0": "-1 - r0^4/8 - rS^4 - x0^4/32 (the constant of the SOS expansion; T6' has the constant lambda_S rS^4 = rS^4 "
        "of T6, and O36 contributes no constant)",
        "claim": "{V = V0} = G.(p, r0 sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ, for kappa^2 < 4 lambda_H "
        "lambda_S rS^2",
        "argument": "{V = V0} is the intersection of the zero sets of the SOS terms (each >= 0): {V_member = V0} = "
        "Z(T1..T5, T7, T8) and Z(T6'), with Z(T6') = {H = 0, |S| = rS} = Z(T6) (sos_identity.sign_argument; T9 = eps N_H "
        "is part of T6').  T1-T5, T7 and T8 are kappa-free (kappa enters the SOS map only through O06 and O12, i.e. T6: "
        "sos_non_T6_terms_kappa_free_three_signs), so the set equals {V_family(kappa') = V0} = G.q0 for any kappa' with "
        "kappa'^2 < 8 rS^2 (e.g. kappa' = 0) by the committed decoupled-singlet family certificate (rS) and the committed "
        "equality-set theorem (P1/P2 contain no H or S and carry over verbatim; charges, phases, operator neutrality and "
        "the tangent ranks are lambda_H-free).  This covers lambda_H > 2 with 8 rS^2 <= kappa^2 < 4 lambda_H lambda_S "
        "rS^2, where the family at the same kappa is not certified",
        "committed_equality_report_premises": premises,
        "committed_family_report_binding": family_binding,
        "member_operator_ids_equal_witness_ids": point_ids,
    }
    return section, checks


def committed_witness_binding(
    member_certificates: Mapping[str, Mapping[str, Any]] | None, hessian_report: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool]:
    """The witness-point member certificates (lambda_H = 1/10) against the committed exact-Hessian report."""
    if member_certificates is None:
        return {"compared": False, "reason": "no committed-witness point among the member points"}, False
    binding, ok = family.committed_hessian_binding(hessian_report, member_certificates)
    return {"compared": True, **binding}, ok


# ---------------------------------------------------------------------------
# (7) lambda_eff (EXACT series) and (8) boundedness from below (EXACT).
# ---------------------------------------------------------------------------


def lambda_eff_section(point_records: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, bool]]:
    k, rs, l_s, l_h = sympy.symbols("k rS lambda_S lambda_H", positive=True)  # k = |kappa|
    eta, tau = sympy.symbols("eta tau", real=True)
    l34 = sympy.Symbol("l34", real=True)
    # Light line: H = eta e (N_H = eta^2, H.H = eta^2), S = rS + tau eta^2 real; O06 = 2 k rS - l34 rS^2 (massless).
    o06 = 2 * k * rs - l34 * rs**2
    line = l_h * eta**4 + (o06 - 2 * k * (rs + tau * eta**2) + l34 * (rs + tau * eta**2) ** 2) * eta**2 + l_s * (
        (rs + tau * eta**2) ** 2 - rs**2
    ) ** 2
    expanded = sympy.expand(line)
    c2 = expanded.coeff(eta, 2)
    c4 = expanded.coeff(eta, 4)
    tau_star = sympy.solve(sympy.diff(c4, tau), tau)[0]
    series = sympy.simplify(c4.subs(tau, tau_star))
    closed_o34 = l_h - (k - l34 * rs) ** 2 / (4 * l_s * rs**2)
    closed = l_h - k**2 / (4 * l_s * rs**2)
    committed = sympy.simplify(closed.subs({l_h: 2, l_s: 1}) - (2 - k**2 / (4 * rs**2)))
    series_ok = bool(
        sympy.simplify(c2) == 0
        and sympy.simplify(series - closed_o34) == 0
        and sympy.simplify(series.subs(l34, 0) - closed) == 0
        and committed == 0
        and sympy.simplify(sympy.diff(c4, tau, 2)).is_positive
    )
    r0 = sympy.Symbol("r0", positive=True)
    shift = sympy.simplify((closed - l_h).subs(k, r0**2 / (4 * rs)))
    anchor = Fraction(-1, 64 * ANCHOR_RS_OVER_R0**4)
    shift_ok = bool(
        sympy.simplify(shift + r0**4 / (64 * l_s * rs**4)) == 0
        and anchor == ANCHOR_LAMBDA_SHIFT
        and sympy.Rational(anchor.numerator, anchor.denominator) == shift.subs({l_s: 1, rs: ANCHOR_RS_OVER_R0 * r0})
    )
    rows = {
        label: {
            "lambda_H": record["lambda_H"],
            "lambda_eff": record["lambda_eff"],
            "lambda_H_minus_candidate_shift": record["lambda_H"] - record["candidate_S_exchange_shift_kappa2_over_4rS2"],
        }
        for label, record in point_records.items()
    }
    points_ok = bool(rows) and all(row["lambda_eff"] == row["lambda_H_minus_candidate_shift"] for row in rows.values())
    checks = {
        "lambda_eff_series_closed_form_with_and_without_O34_symbolic": series_ok,
        "lambda_eff_equals_lambda_H_minus_candidate_S_exchange_shift_at_every_point": points_ok,
        "lambda_eff_minus_lambda_H_is_minus_r0_4_over_64_lambda_S_rS_4_at_kappa_minus_r0sq_over_4rS": shift_ok,
    }
    section = {
        "label": "EXACT",
        "normalisation": "V = lambda (h^dag h)^2 on the light doublet, h^dag h = N_H (the candidate's convention: "
        "lambda_eff = 2 - kappa^2/(4 r0^2) = 127/64 for the committed witness)",
        "derivation": "along the light line H = eta e (real doublet), S = rS + tau eta^2 relaxes: V - V0 = c4(tau) eta^4 + "
        "O(eta^6) with no eta^2 term; minimising c4 over tau gives the tree light-doublet quartic (S-radial exchange; the "
        "only |h|^2-heavy trilinear is kappa's, ||H wedge Phi||^2 vanishes on doublets, and O36 changes nothing else)",
        "eta2_coefficient": str(sympy.simplify(c2)),
        "eta4_coefficient": str(sympy.simplify(c4)),
        "tau_star": str(sympy.simplify(tau_star)),
        "lambda_eff_series": str(series),
        "lambda_eff": "lambda_H - kappa^2/(4 lambda_S rS^2)",
        "lambda_eff_with_O34": "lambda_H - (|kappa| - l34 rS)^2/(4 lambda_S rS^2) (series identity only; an O34 member is "
        "an S portal and is NOT certified here)",
        "at_kappa_minus_r0sq_over_4rS": str(shift),
        "anchor_rS_1000_r0": {"lambda_eff_minus_lambda_H": ANCHOR_LAMBDA_SHIFT, "float": float(ANCHOR_LAMBDA_SHIFT)},
        "points": rows,
        "positivity": "lambda_eff > 0 is the certified domain (sos_identity.margin_equivalence), so lambda_eff takes any "
        "positive value: at kappa = -r0^2/(4 rS), lambda_eff = lambda_H - r0^4/(64 rS^4) for every lambda_H > r0^4/(64 rS^4)",
    }
    return section, checks


def bfb_section() -> tuple[dict[str, Any], dict[str, bool]]:
    base = candidate.exact_quartic_bound()
    lam = sympy.Symbol("lambda_H", positive=True)
    alpha = {key: candidate._as_sympy(value) for key, value in base["coefficients_alpha"].items()}
    beta = {key: candidate._as_sympy(value) for key, value in base["chart_norm_weights_beta"].items()}
    alpha["N_H"] = lam
    constant = sympy.simplify(1 / sum(beta[key] ** 2 / alpha[key] for key in alpha))
    closed = lam / (165 * lam + 4)
    values = {value: constant.subs(lam, candidate._as_sympy(value)) for value in BFB_EXPECTED}
    ok = bool(
        sympy.simplify(constant - closed) == 0
        and all(values[value] == candidate._as_sympy(expected) for value, expected in BFB_EXPECTED.items())
        and base["constant"] == candidate.QUARTIC_LOWER_BOUND == BFB_EXPECTED[Fraction(2)]
        and base["matches_recorded_constant"]
        and constant.is_positive
    )
    checks = {"bfb_quartic_constant_lambda_H_over_165_lambda_H_plus_4_symbolic_points_and_committed_1_over_167": ok}
    section = {
        "label": "EXACT",
        "quartic_part": "V4 = Q(Phi) + (1/8)(||M_Phi Sigma||^2 + ||C_Phi Sigma||^2 + W'(Sigma)) + lambda_H N_H^2 + ||H wedge "
        "Phi||^2 + |S|^4 + |Phi17|^4/32 (the kappa term is cubic)",
        "bound": "V4(q) >= |q|^4 / sum(beta^2/alpha) with alpha_NH = lambda_H (the candidate's Cauchy-Schwarz argument)",
        "constant": str(constant),
        "values": {str(key): str(value) for key, value in values.items()},
        "committed_G5_constant": base["constant"],
        "G5_binding": "G5 stays bound to the committed lambda_H = 2 coefficient vector (constant 1/167); this report "
        "records the member's constant only (status-neutral)",
    }
    return section, checks


# ---------------------------------------------------------------------------
# (9) Research record (RESEARCH_RECORD, sha256 provenance).
# ---------------------------------------------------------------------------

_SCHEMA = ("label", "value", "meaning", "source_script", "source_json", "key", "source_json_sha256", "reproducible_from_repository")


def research_record_section(research_record: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, bool]]:
    record = RESEARCH_RECORD if research_record is None else research_record
    problems = []
    entries_ok = isinstance(record, Mapping) and bool(record)
    if entries_ok:
        for name, entry in record.items():
            if not isinstance(entry, Mapping) or set(entry) != set(_SCHEMA):
                problems.append(f"{name}: schema")
                continue
            if entry["label"] != _REC:
                problems.append(f"{name}: label")
            if entry["source_json"] not in RESEARCH_FILES or RESEARCH_FILES[entry["source_json"]] != (
                entry["source_script"],
                entry["source_json_sha256"],
            ):
                problems.append(f"{name}: provenance")
            if not re.fullmatch(r"[0-9a-f]{64}", str(entry["source_json_sha256"])):
                problems.append(f"{name}: sha256")
            if entry["reproducible_from_repository"] is not False:
                problems.append(f"{name}: reproducible_from_repository")
            if not all(isinstance(entry[key], str) and entry[key] for key in ("meaning", "source_script", "key")):
                problems.append(f"{name}: provenance text")

    def value_of(name: str) -> Any:
        entry = record.get(name) if isinstance(record, Mapping) else None
        return entry.get("value") if isinstance(entry, Mapping) else None

    consistency: dict[str, Any] = {}
    ok = True
    try:
        # (a) the research exact lambda_eff strings at (1/5, 1, 1, -1/100) equal lambda_H - kappa^2/(4 rS^2).
        strings = value_of("e1_lambda_eff_exact_strings")
        kappa = KEEPS_POINT.kappa
        exact = {key: Fraction(key) - kappa * kappa / (4 * LAMBDA_S * KEEPS_POINT.rs**2) for key in strings}
        consistency["e1_exact_strings_equal_module"] = all(Fraction(strings[key]) == exact[key] for key in strings)
        ok = ok and consistency["e1_exact_strings_equal_module"] and len(strings) == 5
        # (b) the research float projection agrees with the exact lambda_eff.
        projection = value_of("e1_lambda_eff_numerical_projection")
        deviation = max(abs(float(projection[key]) / float(exact[key]) - 1.0) for key in projection)
        consistency["e1_projection_max_relative_deviation"] = deviation
        ok = ok and set(projection) == set(strings) and deviation <= E1_PROJECTION_RELATIVE_TOLERANCE
        # (c) the DA' size of lambda_H - lambda_eff = (v_R/v_S)^4/64.
        v4 = value_of("v4_kappa_correction_DA_prime")
        thresholds = {}
        for name, row in v4.items():
            recomputed = (float(row["v_R_GeV"]) / float(row["v_S_GeV"])) ** 4 / 64.0
            thresholds[name] = recomputed
            consistency[f"v4_{name}_relative_deviation"] = abs(recomputed / float(row["lambda_H_minus_lambda_eff"]) - 1.0)
            ok = ok and consistency[f"v4_{name}_relative_deviation"] <= V4_RELATIVE_TOLERANCE
        # (d) every recorded required lambda_H(M_GUT) lies inside the certified domain lambda_H > (v_R/v_S)^4/64.
        inside = {}
        for name, key in (("BM-DA1", "e3_lambda_H_required_BM_DA1"), ("BM-E", "e3_lambda_H_required_BM_E")):
            row = value_of(key)
            required = [float(value) for value in row["lambda_H_MGUT_required"].values()]
            required += [float(value) for pair in row["threshold_band_minus_plus_0p004"].values() for value in pair]
            inside[name] = bool(
                set(row["lambda_H_MGUT_required"]) == set(E3_VARIANTS)
                and all(value > thresholds[name] for value in required)
                and row["inside_SOS_region_every_row"] is True
            )
        consistency["e3_required_lambda_H_inside_certified_domain"] = inside
        ok = ok and all(inside.values())
        # (e) the sensitivity rows outside the domain are exactly the disclosed ones.
        sensitivity = value_of("e3b_sensitivity_lambda_H")
        outside = {name: sorted(row for row, value in rows.items() if float(value) <= thresholds[name]) for name, rows in sensitivity.items()}
        ranges = {
            name: {
                variant: [min(float(v) for r, v in rows.items() if r.startswith(variant + "_")), max(float(v) for r, v in rows.items() if r.startswith(variant + "_"))]
                for variant in ("T", "W")
            }
            for name, rows in sensitivity.items()
        }
        consistency["e3b_rows_outside_domain"] = outside
        consistency["e3b_lambda_H_ranges"] = ranges
        ok = ok and outside == DISCLOSED_OUTSIDE_DOMAIN
        # (e') the a1 (H-Sigma portal) and lh2 (O36_B01 != O36_B02) rows are outside the certified member map.
        outside_member = {name: sorted(row for row in rows if "a1G=" in row or "lh2G=" in row) for name, rows in sensitivity.items()}
        consistency["e3b_rows_outside_member_map"] = outside_member
        ok = ok and outside_member == DISCLOSED_OUTSIDE_MEMBER
        # (f) the verifier's completed-square residual is the module's.
        ok = ok and value_of("v_sos_sampling")["identity_residual"] == "0"
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError):
        ok = False
    checks = {
        "research_record_entries_labelled_with_provenance": bool(entries_ok and not problems),
        "research_record_consistent_with_exact_values_and_disclosed_outliers": bool(ok),
    }
    section = {
        "kind": _REC,
        "provenance_note": RESEARCH_PROVENANCE_NOTE,
        "research_root": RESEARCH_ROOT,
        "entries": record,
        "consistency": consistency,
        "problems": problems,
        "disclosed_rows_outside_domain": DISCLOSED_OUTSIDE_DOMAIN,
        "disclosed_rows_outside_member_map": DISCLOSED_OUTSIDE_MEMBER,
        "conditional": "the e3/e3b running used D's anti-SOS Delta_R region point with G6 assumed fixed and a one-loop "
        "PS-EFT; lambda_SM(v_R) is matched at tree level only; BM-DA1/BM-E are research benchmarks, not chosen here",
    }
    return section, checks


# ---------------------------------------------------------------------------
# FLOAT64 corroboration (outside the exact check count).
# ---------------------------------------------------------------------------


def float_evidence_section() -> dict[str, Any]:
    started = time.time()
    output: dict[str, Any] = {"run": True, "label": "NUM (FLOAT64 corroboration outside the exact check count)"}
    checks: dict[str, bool] = {}
    ids = {O36_B01.split("::", 1)[1], O36_B02.split("::", 1)[1]}
    # F1: the live compiler rows of both O36 directions at q0 (the keeps point).
    t0 = time.time()
    state = candidate.candidate_state(KEEPS_POINT.r0, KEEPS_POINT.x0, rs=KEEPS_POINT.rs)
    rows = target.parameter_rows(state, include=lambda direction: direction.direction_id in ids)
    f1 = {"point": _point_dict(KEEPS_POINT), "rows": {}}
    for key in (O36_B01, O36_B02):
        row = rows.get(key)
        f1["rows"][key] = (
            {
                "abs_value": abs(float(row.value)),
                "max_abs_gradient": float(np.max(np.abs(np.asarray(row.gradient, dtype=float)))),
                "max_abs_hessian": float(np.max(np.abs(np.asarray(row.hessian, dtype=float)))),
            }
            if row is not None
            else None
        )
    f1["seconds"] = time.time() - t0
    checks[FLOAT_CHECK_NAMES[0]] = all(
        row is not None and max(row.values()) <= FLOAT_TOLERANCE for row in f1["rows"].values()
    )
    output["F1_live_O36_rows_at_q0"] = f1
    # F2: the compiler's O36 directions at random H equal I_1 and I_54, and lambda_H (I_1 + I_54) = lambda_H N_H^2.
    t0 = time.time()
    rng = np.random.default_rng(FLOAT_SEED)
    samples = []
    worst = 0.0
    for _ in range(FLOAT_SAMPLES):
        h = rng.normal(size=chart.H_COMPLEX_DIM) + 1j * rng.normal(size=chart.H_COMPLEX_DIM)
        q = chart.pack(candidate.candidate_state(KEEPS_POINT.r0, KEEPS_POINT.x0, h=h, rs=KEEPS_POINT.rs))
        directions = potential.evaluate_directions(chart.unpack(q))
        invariants = h_self_source.invariants(h)
        v1 = potential.potential_value(directions, {O36_B01: 1.0})
        v54 = potential.potential_value(directions, {O36_B02: 1.0})
        n_squared = invariants["HdagH"] ** 2
        member = {str(value): potential.potential_value(directions, {O36_B01: float(value), O36_B02: float(value)}) for _, _, value in MEMBER_POINTS}
        relative = {
            "I_1": abs(v1 - invariants["I_1"]) / max(1.0, abs(invariants["I_1"])),
            "I_54": abs(v54 - invariants["I_54"]) / max(1.0, abs(invariants["I_54"])),
            "lambda_H_NH2": max(abs(value - float(Fraction(key)) * n_squared) / max(1.0, abs(float(Fraction(key)) * n_squared)) for key, value in member.items()),
        }
        worst = max(worst, *relative.values())
        samples.append({"N_H": invariants["HdagH"], "I_1": invariants["I_1"], "I_54": invariants["I_54"], "relative_differences": relative})
    f2 = {"seed": FLOAT_SEED, "samples": samples, "max_relative_difference": worst, "seconds": time.time() - t0}
    checks[FLOAT_CHECK_NAMES[1]] = bool(samples and worst <= FLOAT_TOLERANCE)
    output["F2_compiler_O36_directions"] = f2
    # F3: the compiler along the violating curve at lambda_H = 1/100, |kappa| = 21/100, t = 1/1000 (rS = 1).
    t0 = time.time()
    lambda_h, k_abs, step = FLOAT_VIOLATING
    point = P(R0, SHARPNESS_RS, X0, -k_abs)
    coefficients = candidate.float_coefficients(member_coefficients(point, lambda_h))
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = math.sqrt(float(k_abs * step / lambda_h))
    q = chart.pack(candidate.candidate_state(R0, X0, h=h, rs=SHARPNESS_RS + step))
    compiler = candidate.compiler_value(q, coefficients) - float(candidate.lower_bound_v0(R0, X0, rs=SHARPNESS_RS))
    exact = t6_prime_on_curve(SHARPNESS_RS, -k_abs, step, k_abs * step / lambda_h, lambda_h)
    f3 = {
        "point": _point_dict(point),
        "lambda_H": lambda_h,
        "t": step,
        "compiler_V_minus_V0": compiler,
        "exact": exact,
        "difference": compiler - float(exact),
        "seconds": time.time() - t0,
    }
    checks[FLOAT_CHECK_NAMES[2]] = bool(abs(f3["difference"]) <= FLOAT_TOLERANCE and compiler < 0)
    output["F3_violating_direction"] = f3
    failures = [name for name, passed in checks.items() if not passed]
    output.update({"checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures})
    output["seconds"] = time.time() - started
    return output


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def _label_of(name: str) -> str:
    if name.startswith("research_record_"):
        return _REC
    return "EXACT"


def build_report(
    *,
    numerical: bool = True,
    points: Sequence[tuple[str, Any, Any]] | None = None,
    witnesses: Sequence[tuple[Fraction, Fraction, Fraction, Fraction]] | None = None,
    o36_b02_offset: Any = 0,
    equality_report: Mapping[str, Any] | None = None,
    family_report: Mapping[str, Any] | None = None,
    hessian_report: Mapping[str, Any] | None = None,
    research_record: Mapping[str, Any] | None = None,
    self_weights: Mapping[str, Fraction] | None = None,
    expected_n_checks: int | None = None,
) -> dict[str, Any]:
    """Build the status-neutral O36 member certificate.  Every keyword except ``numerical`` exists for fail-closed
    mutation tests: member points, sharpness witnesses, an O36_B02 offset, the committed reports, the research record,
    the SOS self weights and the expected check count.  With the default point sets the check count must equal
    EXPECTED_N_CHECKS (or ``expected_n_checks`` when given); otherwise the report fails closed with CHECK_COUNT_FAILURE."""
    started = time.time()
    default_sets = points is None and witnesses is None
    count_target = expected_n_checks if expected_n_checks is not None else (EXPECTED_N_CHECKS if default_sets else None)
    member_points = [
        (label, hessian.as_singlet_point(point), Fraction(lambda_h)) for label, point, lambda_h in (MEMBER_POINTS if points is None else points)
    ]
    witness_list = list(SHARPNESS_WITNESSES if witnesses is None else witnesses)
    offset = Fraction(o36_b02_offset)
    weights = dict(candidate.SWAPPED_SELF_WEIGHTS if self_weights is None else self_weights)
    checks: dict[str, bool] = {}

    h_self, h_checks = h_self_section(member_points, offset)
    checks.update(h_checks)
    sos, sos_checks = sos_section(member_points, weights)
    checks.update(sos_checks)
    sharp, sharp_checks = sharpness_section(witness_list)
    checks.update(sharp_checks)

    selection = g2_audit.contract_selection()
    contract_ids = set(selection["parameter_ids"]) if selection["parameter_count"] == 51 else set()
    point_records: dict[str, Any] = {}
    witness_certificates = None
    for label, point, lambda_h in member_points:
        record, point_checks, certificates = member_point_section(label, point, lambda_h, offset, contract_ids)
        point_records[label] = record
        for suffix in POINT_CHECK_SUFFIXES:
            checks[f"point_{label}__{suffix}"] = bool(point_checks[suffix])
        if _is_witness_point(point) and witness_certificates is None:
            witness_certificates = certificates
    witness_binding, witness_ok = committed_witness_binding(witness_certificates, hessian_report)
    checks["witness_point_member_certificates_equal_committed_exact_hessian_report"] = bool(witness_ok)
    t6_constants_ok = checks["sos_T6_prime_equals_T6_plus_T9_plus_lambda_H_minus_2_times_I1_plus_I54_three_signs"]
    equality_part, equality_checks = equality_section(member_points, equality_report, family_report, t6_constants_ok)
    checks.update(equality_checks)
    lam_eff, lam_checks = lambda_eff_section(point_records)
    checks.update(lam_checks)
    bfb, bfb_checks = bfb_section()
    checks.update(bfb_checks)
    research, research_checks = research_record_section(research_record)
    checks.update(research_checks)

    failures = [name for name, passed in checks.items() if not passed]
    if count_target is not None and len(checks) != count_target:
        failures.append(CHECK_COUNT_FAILURE)
    exact_ok = not failures
    float_evidence = (
        float_evidence_section()
        if numerical
        else {"run": False, "label": "NUM (FLOAT64 corroboration outside the exact check count)", "reason": "--no-numerics"}
    )
    float_ok = bool(numerical and float_evidence.get("n_failed") == 0 and float_evidence.get("n_checks") == EXPECTED_N_FLOAT_CHECKS)
    certified = bool(exact_ok and (not numerical or float_ok))
    flags = {
        "member_theorem_claimed": exact_ok,
        "float_evidence_run": bool(numerical),
        "float_evidence_consistent": float_ok,
        "lambda_eff_free_positive_parameter": bool(exact_ok),
        "hessian_bit_identical_to_lambda_H_2_member": bool(
            exact_ok and all(checks.get(f"point_{label}__{POINT_CHECK_SUFFIXES[2]}") for label, _, _ in member_points)
        ),
        "margin_sharp_at_eps_0": bool(
            exact_ok and checks.get("sharpness_curve_identity_exact") and checks.get("sharpness_violating_points_exact_beyond_margin")
        ),
        "margin_sufficient_not_sharp_for_eps_positive": bool(exact_ok and checks.get("sharpness_only_at_eps_0_exact_eps_positive_domain")),
        "research_record_disclosed": bool(checks.get("research_record_entries_labelled_with_provenance")),
    }
    flags.update({name: False for name in NEVER_TRUE_FLAGS})
    report = {
        "module": MODULE,
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_CERTIFIED if certified else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_CERTIFIED if certified else OVERALL_STATE_OPEN,
        "theorem_claimed": exact_ok,
        "theorem": THEOREM if exact_ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "physics_status": dict(PHYSICS_STATUS),
        "G3_witness_unchanged": True,
        "n_checks": len(checks),
        "expected_n_checks": count_target,
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "check_labels": {name: _label_of(name) for name in checks},
        "flags": flags,
        "h_self": h_self,
        "sos_identity": sos,
        "sharpness": sharp,
        "member_points": point_records,
        "committed_witness_binding": witness_binding,
        "equality_set": equality_part,
        "lambda_eff": lam_eff,
        "bfb": bfb,
        "research_record": research,
        "float_evidence": float_evidence,
        "float_verdict": "",
        "scope": {
            "claimed": [
                "EXACT: I_1 + I_54 = N_H^2 and N_H^2 - |H.H|^2 = sum of squares (sympy, 20 real variables); the H quartic "
                "is lambda_H N_H^2 iff O36_B01 = O36_B02",
                "EXACT: the O36 member's SOS identity for every kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1) "
                "and eps >= 0 (sympy residual 0; reduces to the committed identity at lambda_H = 2), valid on the "
                "boundary, and sharp at eps = 0 (exact violating points beyond it); for eps > 0 the exact H/S-block "
                "domain is |kappa| <= 2 sqrt(lambda_H lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the margin "
                "is sufficient but not sharp there",
                "EXACT: V0 and the equality set unchanged for every lambda_H > 0 in the domain (T1-T5, T7, T8 are "
                "kappa-free; bound to the committed equality-set and family artifacts)",
                "EXACT: the 486 x 486 Hessian over Q bit-identical to the lambda_H = 2 member at (1/5, 1, 1, -1/100) for "
                "lambda_H in {2, 1/100, 1/1000} and at the witness point for lambda_H = 1/10 (447/39/0, 451/35/0), and "
                "the witness-point certificates equal to the committed exact-Hessian report",
                "EXACT: lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) (series), a free positive parameter; "
                "lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS)",
                "EXACT: V4 >= lambda_H |q|^4/(165 lambda_H + 4)",
                "NUM: the live compiler's O36 rows vanish at q0, its O36 directions equal I_1 and I_54, and it reproduces "
                "the exact violating value",
            ],
            "not_claimed": [
                "no benchmark is chosen: the (r0, rS, x0, kappa, lambda_H) points are certificate points",
                "tree level only: the one-loop quartic matching at v_R (research estimate +-0.004) is not computed, "
                "and the RG running of lambda_H is research-recorded only (CONDITIONAL)",
                "lambda_SM(v_R) is not matched by this certificate; the required lambda_H(M_GUT) values are research "
                "records at research benchmarks (BM-DA1, BM-E) with an anti-SOS Delta_R point (G6 assumed fixed); the "
                "a1/lh2 sensitivity rows are outside the certified member (an H-Sigma portal and O36_B01 != O36_B02), "
                "and one further row needs lambda_H < 0 (outside the certified domain)",
                "no S-portal member (O34 or others) is certified; the O34 lambda_eff formula is a series identity only",
                "the committed witness (lambda_H = 2) stays the G3/G4 closing instance and G5 stays bound to the "
                "committed lambda_H = 2 vector; no gate status changes and nothing is wired into the ledger",
                "the G6 tree spectrum, G7 running and G8 flavour are unchanged by O36 at tree level (O36 is quartic in H "
                "and invisible at q0) and are not re-derived here",
                "no manuscript change",
            ],
            "relies_on_committed": [
                "G3_SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_V20.json (certified, 77 checks, 0 failed; the rS family, its "
                "eight-term SOS identity, tangent ranks and P3 at rS)",
                "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; P1/P2 contain no H or S)",
                "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to the witness-point member certificates)",
            ],
            "status_neutrality": STATUS_NEUTRALITY,
        },
        "provenance": {
            "repository_modules_imported_read_only": [
                "g3_sm_pati_salam_candidate_v20",
                "g3_sm_pati_salam_decoupled_singlet_family_v20",
                "g3_sm_pati_salam_exact_hessian_v20 (exact_hessian/exact_certificate with the documented overrides "
                "keyword, used read-only for the two O36 entries)",
                "g3_sm_pati_salam_equality_set_v20",
                "exact_h10_self_quartic_family_v20",
                "g3_candidate_physical_target_audit_v20 (live compiler rows, float only)",
            ],
            "research_note": RESEARCH_PROVENANCE_NOTE,
            "research_files": {name: {"script": script, "sha256": sha} for name, (script, sha) in RESEARCH_FILES.items()},
            "research_script_sha256": dict(RESEARCH_SCRIPT_SHA256),
        },
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["float_verdict"] = _float_verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


THEOREM = (
    "For every r0, rS, x0 > 0, lambda_H > 0, real kappa with kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1) and "
    "eps >= 0, the O36 member (the decoupled-singlet map with O36_B01 = O36_B02 = lambda_H instead of 2; 27 parameters "
    "inside the 51-parameter contract) satisfies V >= V0 = -1 - r0^4/8 - rS^4 - x0^4/32 with {V = V0} = G.(p, r0 "
    "sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ (given the committed family certificate and the committed "
    "equality-set theorem's lambda_H-free parts).  The H quartic is lambda_H N_H^2 exactly (I_1 + I_54 = N_H^2), and "
    "after Cauchy-Schwarz the H/S block is lambda_H (N_H - |kappa| t/lambda_H)^2 + t^2 (lambda_S u^2 - kappa^2/lambda_H) "
    "+ eps N_H, t = |S| - rS, u = |S| + rS (sympy residual 0).  The domain is sharp at eps = 0: V >= V0 fails for "
    "every kappa^2 > 4 lambda_H lambda_S rS^2 when eps = 0 (exact violating points), while on the boundary the bound "
    "and the equality set still hold; for eps > 0 the exact domain of the H/S block is |kappa| <= 2 sqrt(lambda_H "
    "lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the certified margin is sufficient there but not sharp.  "
    "The equality set holds for every lambda_H > 0 in the domain because T1-T5, T7, T8 are kappa-free.  The tree "
    "light-doublet quartic is lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) > 0, a free positive "
    "parameter (lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS)), and V4 >= lambda_H |q|^4/(165 "
    "lambda_H + 4).  Exact over Q at (1/5, 1, 1, -1/100) with lambda_H in {2, 1/100, 1/1000} and at the witness point "
    "(1/5, 1/5, 1, -1/20) with lambda_H = 1/10: grad V(q0) = 0 and the 486 x 486 Hessian is bit-identical to the lambda_H "
    "= 2 member (447/39/0 at eps = 0, kernel = 35 orbit tangents + 4 doublet directions, gap r0^2/96 x 14; 451/35/0 at "
    "eps = r0^2/100).  Tree level only."
)


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the O36 lambda_H member certificate is NOT claimed (failed: " + ", ".join(report["failures"])
            + ").  No gate is affected: this report is status-neutral."
        )
    points = report["member_points"]
    return (
        f"Exact ({report['n_checks']} checks): setting the H self-quartics O36_B01 = O36_B02 = lambda_H (committed 2) in "
        "the decoupled-singlet map keeps the SOS certificate for every kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = "
        "O23 = 1): I_1 + I_54 = N_H^2 (sympy, 10 complex variables) and, after Cauchy-Schwarz, the H/S block is "
        "lambda_H (N_H - |kappa| t/lambda_H)^2 + t^2 (lambda_S u^2 - kappa^2/lambda_H) + eps N_H (sympy residual 0); "
        "the margin is sharp at eps = 0 (exact violating points beyond it; for eps > 0 the exact domain is |kappa| <= "
        "2 sqrt(lambda_H lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the margin is sufficient but not sharp) "
        "and the bound still holds on the boundary.  V0, the "
        f"equality set and the exact 486 x 486 Hessian at q0 are unchanged (bit-identical at {len(points)} member "
        "points; 447/39/0 and 451/35/0).  The tree light-doublet quartic lambda_eff = lambda_H - kappa^2/(4 lambda_S "
        "rS^2) is a free positive parameter (lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS), "
        "-1.5625e-14 at rS = 1000 r0), and V4 >= lambda_H |q|^4/(165 lambda_H + 4).  Tree level only: the one-loop "
        "matching at v_R (research estimate +-0.004) is not computed, lambda_SM(v_R) is matched only in the research "
        "record (CONDITIONAL), no benchmark is chosen, the committed lambda_H = 2 witness remains the G3/G4 closing "
        "instance, G5 stays bound to it, and no gate changes."
    )


def _float_verdict(report: Mapping[str, Any]) -> str:
    evidence = report["float_evidence"]
    if not evidence.get("run"):
        return "FLOAT64 corroboration not run (--no-numerics); the exact verdict does not depend on it."
    if evidence.get("n_failed"):
        return "FLOAT64 corroboration FAILED (" + ", ".join(evidence["failures"]) + "); the report is not certified."
    return (
        f"FLOAT64 corroboration (NUM), outside the exact check count: {evidence['n_checks']}/{evidence['n_checks']} "
        "passed (live O36 rows vanish at q0, compiler O36 directions = I_1 and I_54, compiler violating value)."
    )


def report_passes(report: Mapping[str, Any]) -> bool:
    """Certified, nothing failed, and the pinned check count (main writes only when this holds)."""
    return bool(
        report.get("n_failed") == 0
        and report.get("status") == STATUS_CERTIFIED
        and report.get("n_checks") == EXPECTED_N_CHECKS
        and len(report.get("checks", {})) == EXPECTED_N_CHECKS
    )


def _cell(value: Any) -> str:
    return "`" + str(value).replace("|", "\\|") + "`"


def _ordered(mapping: Mapping[str, Any], preferred: Sequence[str] | Mapping[str, Any]) -> list[str]:
    """Keys of ``mapping`` in the ``preferred`` order first, then the rest sorted."""
    first = [key for key in preferred if key in mapping]
    return first + sorted(key for key in mapping if key not in first)


def _markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# G3 SM Pati-Salam O36 lambda_H Higgs-quartic member -- v20",
        "",
        f"**Status:** `{report['status']}` (`{report['overall_state']}`)",
        "",
        f"**Theorem claimed:** `{report['theorem_claimed']}`",
        "",
        "Labels: EXACT (sympy or Fraction arithmetic), NUM (float64 recomputed here), RESEARCH_RECORD (not re-derived; "
        "sha256 provenance).",
        "",
        "## Theorem (EXACT)",
        "",
        report["theorem"],
        "",
        "## Physics status (read first)",
        "",
    ]
    status = report["physics_status"]
    lines += [f"- **{key}**: {status[key]}" for key in _ordered(status, PHYSICS_STATUS)]
    lines += ["", "## Verdict", "", report["verdict"], "", report["float_verdict"], ""]
    lines += [f"Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed.", ""]
    lines += [
        "## Member points (EXACT)",
        "",
        "| label | (r0, rS, x0, kappa) | lambda_H | margin 4 lambda_H rS^2 - kappa^2 | lambda_eff | V0 | eps window upper | "
        "perturbative member | Hessian = lambda_H 2 member | tuned / raised inertia | gap tuned (mult) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label in _ordered(report["member_points"], [name for name, _, _ in MEMBER_POINTS]):
        row = report["member_points"][label]
        point = row["point"]
        identical = all(
            value for variant in row["hessian_identity_vs_lambda_H_2"].values() for key, value in variant.items() if key != "denominator"
        )
        bench, raised = row["certificates"]["benchmark"], row["certificates"]["raised_O06"]
        lines.append(
            f"| {label} | `({point['r0']}, {point['rS']}, {point['x0']}, {point['kappa']})` | `{row['lambda_H']}` | "
            f"`{row['margin_4_lambda_H_lambda_S_rS2_minus_kappa2']}` | `{row['lambda_eff']}` | `{row['V0']}` | "
            f"`{row['perturbative_box']['eps_window_upper_exclusive']}` | `{row['perturbative_box']['perturbative_member']}` | "
            f"`{identical}` | `{bench['inertia_positive_zero_negative']} / {raised['inertia_positive_zero_negative']}` | "
            f"`{bench['smallest_nonzero_eigenvalue']}` (`{bench['multiplicity']}`) |"
        )
    sos = report["sos_identity"]
    lines += [
        "",
        "## SOS identity (EXACT, sympy)",
        "",
        f"- T6' = {sos['T6_prime']}",
        f"- Cauchy-Schwarz: {sos['cauchy_schwarz']}",
        f"- {sos['completed_square']} (residual `{sos['completed_square_residual']}`)",
        f"- reduction to the committed identity at lambda_H = 2: {_cell(sos['reduction_to_committed'])}",
        f"- sign argument: {sos['sign_argument']}",
        f"- domain: {sos['domain']}",
        f"- boundary bracket: `{sos['boundary_bracket_at_k2_eq_4_lambda_H_lambda_S_rS2']}`; {sos['boundary_note']}",
        f"- operator level: {sos['operator_level']['statement']}",
        "",
        "## H self-identities (EXACT, sympy)",
        "",
        f"- I_1 + I_54 - N_H^2 = `{report['h_self']['I1_plus_I54_minus_NH2']}`",
        f"- {report['h_self']['cauchy_schwarz_identity']}: residual `{report['h_self']['cauchy_schwarz_residual']}`",
        f"- {report['h_self']['iff_statement']}",
        f"- {report['h_self']['hessian_at_H0']}",
        "",
        "## Sharpness (EXACT)",
        "",
        report["sharpness"]["curve"] + f" (residual `{report['sharpness']['curve_identity_residual']}`).",
        "",
        "| rS | lambda_H | abs kappa | t | margin | V - V0 |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["sharpness"]["violating_witnesses"]:
        lines.append(
            f"| `{row['rS']}` | `{row['lambda_H']}` | `{row['abs_kappa']}` | `{row['t']}` | "
            f"`{row['margin_4_lambda_H_lambda_S_rS2_minus_kappa2']}` | `{row['V_minus_V0_equals_T6_prime']}` |"
        )
    lam = report["lambda_eff"]
    bfb = report["bfb"]
    lines += [
        "",
        "## Light-doublet tree quartic (EXACT, series)",
        "",
        f"- lambda_eff = {lam['lambda_eff']} (series: `{lam['lambda_eff_series']}`)",
        f"- with O34: {lam['lambda_eff_with_O34']}",
        f"- at kappa = -r0^2/(4 rS): lambda_eff - lambda_H = `{lam['at_kappa_minus_r0sq_over_4rS']}`; at rS = 1000 r0: "
        f"`{lam['anchor_rS_1000_r0']['lambda_eff_minus_lambda_H']}` = `{lam['anchor_rS_1000_r0']['float']}`",
        "",
        "## Boundedness from below (EXACT)",
        "",
        f"- {bfb['bound']}: constant `{bfb['constant']}`, values {_cell(bfb['values'])}",
        f"- {bfb['G5_binding']}",
        "",
        "## Equality set (EXACT bindings)",
        "",
        report["equality_set"]["argument"],
        "",
        "## Research record (RESEARCH_RECORD, not re-derived)",
        "",
        report["research_record"]["provenance_note"] + ".",
        "",
        "| entry | source | sha256 | meaning |",
        "|---|---|---|---|",
    ]
    for name, entry in report["research_record"]["entries"].items():
        meaning = entry["meaning"].replace("|", "\\|")
        lines.append(f"| `{name}` | `{entry['source_json']}` | `{entry['source_json_sha256'][:16]}...` | {meaning} |")
    consistency = report["research_record"]["consistency"]
    lines += [
        "",
        f"Consistency: {_cell(consistency)}",
        "",
        f"Conditional: {report['research_record']['conditional']}.",
        "",
        "## FLOAT64 evidence (NUM, outside the exact check count)",
        "",
    ]
    evidence = report["float_evidence"]
    if evidence.get("run"):
        lines += [
            "| item | value |",
            "|---|---|",
            f"| F1 live O36 rows at q0 (abs value, max abs gradient, max abs Hessian) | {_cell(evidence['F1_live_O36_rows_at_q0']['rows'])} |",
            f"| F2 compiler O36 vs I_1, I_54, lambda_H N_H^2: max relative difference | `{evidence['F2_compiler_O36_directions']['max_relative_difference']}` |",
            f"| F3 compiler V - V0 on the violating curve (exact) | `{evidence['F3_violating_direction']['compiler_V_minus_V0']}` (`{evidence['F3_violating_direction']['exact']}`) |",
            "",
            "| FLOAT64 check | passed |",
            "|---|---|",
        ]
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
