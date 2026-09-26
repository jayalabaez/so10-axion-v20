#!/usr/bin/env python3
"""Exact gauge quotient, axion and physical Hessian at the accepted G3 witness (G4 certificate, v20).

G3 is CLOSED on the SM Pati-Salam track.  Its witness (decision D2) is the light-doublet member

    V_PS,eps = V_PS + eps N_H   (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50),  r0 = 1/5, x0 = 1, kappa = -r0/4,
    q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0),

and g3_sm_pati_salam_exact_hessian_v20 proves exactly (eps family, L2) that for every eps > 0 the Hessian at q0 is
PSD with kernel exactly the 35-dimensional SO(10) x U(1)_X x U(1)_PQ orbit tangent space T35.  The ledger's G4
gate ("Gauge quotient, axion directions, and physical Hessian") asks for the exact gauge quotient at this witness
and for a classification of every remaining zero and negative mode.  This module certifies, exactly over Q:

  (1) Gauge quotient.  In the canonical chart the tangent matrix is D M: M is the equality module's integer
      486 x 47 matrix (45 so(10) generators L_ab, U(1)_X, PQ) at the raw vacuum and D = diag(1, sqrt2 r0/4,
      sqrt2 r0, sqrt2 x0) on (Phi, Sigma, S, Phi17) is invertible (u-coordinates: D_u = diag(1, r0/4, r0, x0)).
      Both halves of a rank certificate: nonzero integer minors of sizes 33, 34 and 35 (determinants 1, 4, -68;
      rescaled by the exact row-scale product) and, for each of the column sets so(10), so(10)+X and
      so(10)+X+PQ, 12 independent integer null vectors, all without an X or PQ coefficient, spanning exactly the
      standard SM algebra su(3)+su(2)_L+u(1)_Y of g3_sigma_hypercharge_audit_v20.  So the SO(10) orbit has rank 33,
      SO(10) x U(1)_X rank 34 (gauge quotient 486 - 34 = 452, axion included) and SO(10) x U(1)_X x PQ rank 35
      (massive/transverse quotient 451).  PQ is the contract's accidental global symmetry: not gauged, not eaten.
  (2) Physical Hessian on the gauge quotient.  The chart is canonically normalised (K_2 = q^T q / 2, checked);
      in the radical-free coordinates u (q = D_c u, D_c = diag(1^210, sqrt2^276), as in the Hessian module) the
      kinetic metric is D_c^2 = diag(1^210, 2^276), so every inner product is rational.  With G34 the gauge-tangent
      span, W = G34^perp (dim 452) and a = t_PQ - proj_G34 t_PQ (chart metric), exactly: a != 0, a is orthogonal
      to all 46 gauge tangents, a lies in T35, and T35 cap W = span(a).  Since K = ker Hess_q V_eps(q0) = T35 with
      Hess_q PSD, T35 = G34 (+) span(a) and W = span(a) (+) K^perp orthogonally, K^perp = range(Hess_q) being
      invariant.  Hence the Hessian restricted to W is PSD with exactly one zero mode, the physical axion a, and 451
      strictly positive modes whose values are exactly the 451 positive eigenvalues of Hess_q V_eps(q0); no mode is
      negative.  The inputs (PSD, kernel = T35) are read from the committed Hessian report (every eps > 0, L2) and
      re-certified here from fresh exact Hessians at eps = r0^2/100 and eps = r0^2/10^6 (inertia 451/35/0,
      H_u T_u = 0 and H_u a = 0 exactly).
  (3) Axion.  |a|^2 = 9248/7241 in chart units (M_GUT^2) with the PQ charges (Sigma -2, H -2, S 4, Phi17 0), equal
      to 2 r0^2 x0^2 68^2 / (16 r0^2 + 289 x0^2); squared-norm composition: S phase 7225/7241, Phi17 phase
      16/7241, Sigma phase 0 (the Sigma phase is eaten by the so(10) Cartan combination), Phi210 0, H10 0.
      Modulo SO(10) x U(1)_X the axion angle has period 2 pi/68 (68 = |det| of the S/Phi17 charge minor over
      gcd(q_X(S), q_X(Phi17)); explicit element U(1)_X(26 pi/17) exp(pi L_01) for theta = pi/34), so a = F_PQ theta
      has period 2 pi v_a with v_a = F_PQ/68, v_a^2 = 2/7241.
  (4) Zero and negative modes.  At every eps in the window: no negative mode, and exactly 35 zero modes = 34 eaten
      Goldstones (33 SO(10)/SM + 1 U(1)_X) + 1 physical axion.
  (5) eps -> 0.  The tuned point adds exactly the 4 real zero modes Re H_6..9 (inertia 447/39/0; 447/5/0 on W):
      span(Re H_6..9) is SM-invariant, a colour singlet, has SU(2)_L Casimir 3/4 and Y^2 = 1/4 with Y a complex
      structure, i.e. one SM doublet (1,2)_{1/2} realified; at eps = 0 it is lifted at quartic order by
      lambda_eff = 127/64 > 0 (candidate), and for eps > 0 its mass^2 is exactly eps (the lightest level, with
      multiplicity 4, for 0 < eps < r0^2/96).
  (6) Vector bosons.  The tangent Gram matrix Gamma_AB = <T_A q0, T_B q0> of the 46 gauge generators (M_V^2 =
      g^2 Gamma up to coupling normalisation) has exact rank 34; exact adjoint Casimirs of the audit's SM
      generators split so(10) into SM sectors, Gamma is scalar on each broken one ((3,2)_-5/6: 1; (3,2)_1/6:
      27/25; (3,1)_2/3 and (1,1)_1: 2/25) and the neutral (1,1)_0 (+) X block gives
      125 lambda^2 - (50 + 72450 t^2) lambda + 28964 t^2 (t = g_X/g).

The rows of D M are bound to the live compiler tangents (chart.gauge_orbit_matrix plus the phase tangents) at
the candidate state in float64, and the restricted spectrum is corroborated in float64; both are diagnostics.

Scope: the benchmark point r0 = 1/5, x0 = 1 only (every eps in the window, parametrically); the compiler =
exact-operator identity of the Hessian is float64 end to end (inherited).  Not covered: the physical hierarchy
point, loop corrections (including the axion's anomaly mass and the v_a -> f_a = v_a/N_DW conversion), PQ-violating
non-renormalizable operators (e.g. the dimension-21 Phi17^4 conj(S)^17, which lift the axion explicitly: its zero
mode is exact for the renormalizable PQ-neutral benchmark potential only), and the G6 positivity/EWSB caveats
(H = 0, no electroweak breaking).  This report does not wire G4: the ledger keeps G4 OPEN,
and under decision D3 closing G4 would approve the internal candidate, which is the user's decision.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_gauged_u1x_physical_quotient_v20 as superseded
import g3_sigma_hypercharge_audit_v20 as sigma_audit
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json"
OUT_MD = ROOT / "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.md"
CONTRACT_JSON = ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.json"

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_CERTIFIED = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED"
STATUS_INCOMPLETE = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_NOT_CERTIFIED__G4_OPEN"
OVERALL_STATE_CERTIFIED = "EXACT_G4_PHYSICAL_QUOTIENT_AT_G3_WITNESS__GATE_NOT_WIRED"
OVERALL_STATE_OPEN = "G4_PHYSICAL_QUOTIENT_OPEN"

R0 = hessian.R0
X0 = hessian.X0
KAPPA = hessian.KAPPA
TOTAL_DIM = chart.TOTAL_DIM
SO10_GENERATOR_COUNT = 45
GAUGE_GENERATOR_COUNT = 46
FULL_GENERATOR_COUNT = 47
EXPECTED_SO10_RANK = 33
EXPECTED_GAUGE_RANK = 34
EXPECTED_FULL_RANK = 35
EXPECTED_STABILIZER_DIMENSION = 12
EXPECTED_GAUGE_QUOTIENT = TOTAL_DIM - EXPECTED_GAUGE_RANK  # 452
EXPECTED_TRANSVERSE_QUOTIENT = TOTAL_DIM - EXPECTED_FULL_RANK  # 451
EXPECTED_TUNED_RANK = hessian.EXPECTED_RANK  # 447
EXPECTED_TUNED_NULLITY = hessian.EXPECTED_NULLITY  # 39
EXPECTED_MINOR_DETERMINANTS = {"SO10": 1, "SO10_x_U1X": 4, "SO10_x_U1X_x_PQ": -68}
EXPECTED_PHASE_MINOR = [[4, 4], [17, 0]]
EXPECTED_PHASE_DETERMINANT = -68
EXPECTED_AXION_NORM_SQUARED = Fraction(9248, 7241)
EXPECTED_AXION_PERIOD_DENOMINATOR = 68  # theta_PQ ~ theta_PQ + 2 pi/68 modulo SO(10) x U(1)_X
EXPECTED_V_A_SQUARED = Fraction(2, 7241)  # v_a = F_PQ/68
EXPECTED_AXION_FRACTIONS = {
    "Phi210": Fraction(0),
    "H10": Fraction(0),
    "Sigma126bar": Fraction(0),
    "S": Fraction(7225, 7241),
    "Phi17": Fraction(16, 7241),
}
LIGHT_DOUBLET_REAL_DIMENSION = hessian.LIGHT_DOUBLET_REAL_DIMENSION  # 4
DOUBLET_REAL_X = tuple(hessian.DOUBLET_REAL_X)  # Re H_6 .. Re H_9
LAMBDA_EFF = Fraction(127, 64)
EPS_WINDOW_UPPER = hessian.EPS_PERTURBATIVE_UPPER  # 599/50
DOUBLET_LIGHTEST_BELOW = hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0  # r0^2/96 = 1/2400
SECOND_LEVEL_MULTIPLICITY = 14
EPS_MEMBERS = {"raised_O06": hessian.O06_RAISE, "tiny_eps": hessian.O06_TINY}
FRESH_VARIANTS = ("benchmark", "raised_O06", "tiny_eps")
SUPERSEDED_VALUES = {
    "point": "p + Delta_R (superseded; Delta_R has Y = -1, not an SM vacuum)",
    "gauge_rank": superseded.EXPECTED_GAUGE_RANK,
    "full_rank": superseded.EXPECTED_FULL_RANK,
    "gauge_quotient": superseded.EXPECTED_GAUGE_QUOTIENT_DIMENSION,
    "transverse_quotient": superseded.EXPECTED_QUOTIENT_DIMENSION,
}
BLOCK_SLICES = {
    "Phi210": chart.PHI_SLICE,
    "H10": chart.H_SLICE,
    "Sigma126bar": chart.SIGMA_SLICE,
    "S": chart.S_SLICE,
    "Phi17": chart.X_SLICE,
}
BLOCK_CONVENTIONS = {
    "Phi210": "independent ordered components Phi_abcd",
    "H10": "H_i=(x_i+i y_i)/sqrt(2), interleaved x_i,y_i",
    "Sigma126bar": "Sigma=sum_i (x_i+i y_i)/sqrt(2) e_i, interleaved",
    "S": "S=(x+i y)/sqrt(2)",
    "Phi17": "Phi17=(x+i y)/sqrt(2)",
}
X_CHARGES = {name: int(value) for name, value in superseded.U1X_CHARGES.items()}
PQ_CHARGES = {name: int(value) for name, value in superseded.PQ_CHARGES.items()}
GENERATOR_LABELS = superseded.generator_labels(include_phases=True)
FLOAT_TOLERANCE = 1.0e-12
FLOAT_ZERO_EIGENVALUE = 1.0e-10
RANDOM_SEED = 20260925
DIGITS = 12

# The ledger's G4 open scope (g1_g8_gate_ledger_v20, gates.G4.open_scope) and the roadmap's W3-G4 acceptance,
# pinned verbatim; the test compares them with the committed ledger and roadmap artifacts.
G4_OPEN_SCOPE = (
    "carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and recompute its "
    "ranks there: SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 "
    "(massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point",
    "classify all remaining Hessian zero and negative modes at that witness, including the axion/PQ direction and "
    "the eps -> 0 tuned light doublet (4 real modes)",
    "routed from G3 by decision D5 (zero_modes_and_ranks_at_witness): Zero-mode classification at the witness "
    "belongs to G4: the recomputed ranks 34/35 (SO(10) x U(1)_X rank 34, gauge quotient 452 with the axion "
    "included; SO(10) x U(1)_X x U(1)_PQ rank 35, massive/transverse quotient 451, i.e. quotients 452/451), the "
    "axion/PQ direction and the eps -> 0 tuned light doublet (4 real modes); it is resolved only when G4 is CLOSED.",
)
W3_G4_ACCEPTANCE = (
    "exact gauge/global-symmetry ranks remain compiler-bound and the completed G3 Hessian has no unexplained zero "
    "or negative modes"
)
G4_REQUIRED_STATEMENT = (
    "At the G3 witness q0 of V_PS,eps (0 < eps < 599/50; r0 = 1/5, x0 = 1, kappa = -r0/4) the SO(10)xU(1)_X orbit "
    "has rank 34 and the SO(10)xU(1)_XxPQ orbit rank 35 (gauge quotient 452, massive/transverse quotient 451); the "
    "Hessian has no negative mode and exactly 35 zero modes, 34 eaten Goldstones (33 SO(10)/SM + 1 U(1)_X) and 1 "
    "physical axion; restricted to the 452-dimensional gauge quotient (canonical chart metric) it is PSD with the "
    "axion as its only zero mode and 451 strictly positive modes; as eps -> 0 the only extra zero modes are the 4 "
    "real modes of one SM doublet (1,2)_{1/2}, of mass^2 eps and lifted at quartic order by lambda_eff = 127/64 > 0."
)
THEOREM = (
    "Exact over Q at the G3 witness (V_PS,eps, 0 < eps < 599/50, r0 = 1/5, x0 = 1, kappa = -r0/4, q0 = (p, 0, "
    "r0 sigma_std, r0, x0)): the orbit tangent ranks are SO(10) 33, SO(10)xU(1)_X 34 and SO(10)xU(1)_XxPQ 35 "
    "(nonzero integer minors 1, 4, -68 and 12 independent integer null vectors spanning the standard SM algebra, "
    "without X or PQ coefficient), so the gauge quotient has dimension 452 and the massive/transverse quotient 451; "
    "PQ is global, neither gauged nor eaten.  In the canonical chart metric the PQ tangent's component orthogonal to "
    "the gauge tangents, a, spans T35 cap G34^perp; with ker Hess = T35 (PSD) for every eps > 0 the Hessian "
    "restricted to the 452-dimensional gauge quotient is PSD with a single zero mode, the physical axion "
    "(|a|^2 = 9248/7241; S phase 7225/7241, Phi17 phase 16/7241, Sigma phase 0), and 451 positive modes equal to the "
    "positive spectrum of the Hessian; the 35 zero modes of the full Hessian are 34 eaten Goldstones (33 + 1) and the "
    "axion, with no negative mode.  At eps = 0 the only extra zero modes are Re H_6..9, one SM doublet (1,2)_{1/2}, "
    "lifted at quartic order by lambda_eff = 127/64; for eps > 0 their mass^2 is eps."
)

VECTOR_SECTORS = (
    # label, (colour Casimir, SU(2)_L Casimir, Y^2), real dimension, expected Gamma eigenvalue (None: neutral block)
    ("(8,1)_0", (Fraction(3), Fraction(0), Fraction(0)), 8, Fraction(0)),
    ("(1,3)_0", (Fraction(0), Fraction(2), Fraction(0)), 3, Fraction(0)),
    ("(3,2)_-5/6 + conj", (Fraction(4, 3), Fraction(3, 4), Fraction(25, 36)), 12, Fraction(1)),
    ("(3,2)_1/6 + conj", (Fraction(4, 3), Fraction(3, 4), Fraction(1, 36)), 12, Fraction(27, 25)),
    ("(3,1)_2/3 + conj", (Fraction(4, 3), Fraction(0), Fraction(4, 9)), 6, Fraction(2, 25)),
    ("(1,1)_1 + conj", (Fraction(0), Fraction(0), Fraction(1)), 2, Fraction(2, 25)),
    ("(1,1)_0", (Fraction(0), Fraction(0), Fraction(0)), 2, None),
)
NEUTRAL_POLYNOMIAL = "125*lambda**2 - (50 + 72450*t**2)*lambda + 28964*t**2"
FLOAT_EVIDENCE_SECTIONS = ("live_compiler_binding", "float64_corroboration")

Vector = dict[int, Fraction]


# ---------------------------------------------------------------------------
# Serialisation and fail-closed loaders.
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    return hessian._jsonable(value)


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _get(value: Any, *keys: str, default: Any = None) -> Any:
    return hessian._get(value, *keys, default=default)


def load_report(path: Path) -> dict[str, Any]:
    """Committed JSON report, {} if missing or unreadable (fail closed)."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _is_zero_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == 0


def _passes(report: Mapping[str, Any]) -> bool:
    return _is_zero_int(report.get("n_failed")) and report.get("failures") == []


# ---------------------------------------------------------------------------
# Premises read from the committed reports (every entry must hold).
# ---------------------------------------------------------------------------


def hessian_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    eps = _get(report, "eps_family", default={})
    members = _get(eps, "consistency_certificates", default={})
    doublet = _get(eps, "doublet", default={})
    every = _get(eps, "L2_hessian", "for_every_eps_positive", default={})
    bench = _get(report, "exact_certificate", default={})
    window = _get(eps, "final_acceptance_test", "eps_window", default={})

    def member(name: str, eps_value: Fraction) -> bool:
        row = _get(members, name, default={})
        return bool(
            isinstance(row, Mapping)
            and row.get("eps") == str(eps_value)
            and row.get("inertia_positive_zero_negative") == "451/35/0"
            and row.get("kernel_equals_symmetry_tangents") is True
            and row.get("strictly_positive_on_symmetry_quotient") is True
            and row.get("smallest_nonzero_eigenvalue") == str(eps_value)
            and row.get("smallest_nonzero_eigenvalue_multiplicity") == LIGHT_DOUBLET_REAL_DIMENSION
        )

    return {
        "status_certified": report.get("status") == hessian.STATUS_CERTIFIED,
        "no_failed_checks": _passes(report),
        "theorem_claimed": report.get("theorem_claimed") is True,
        "same_model_contract": report.get("model_contract_id") == MODEL_CONTRACT_ID,
        "eps_family_theorem_claimed": eps.get("theorem_claimed") is True and _passes(eps),
        "eps_family_kernel_is_orbit_for_every_eps_positive": bool(
            _get(report, "flags", "eps_family_kernel_equals_symmetry_orbit") is True
            and _get(report, "flags", "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive") is True
        ),
        "L2_every_eps_positive_PSD_rank_451_nullity_35": bool(
            isinstance(every, Mapping)
            and every.get("PSD") is True
            and every.get("rank") == EXPECTED_TRANSVERSE_QUOTIENT
            and every.get("nullity") == EXPECTED_FULL_RANK
            and every.get("strictly_positive_on_symmetry_quotient_dimension") == EXPECTED_TRANSVERSE_QUOTIENT
        ),
        "members_r0sq_over_100_and_10e6_inertia_451_35_0": member("raised_O06", EPS_MEMBERS["raised_O06"])
        and member("tiny_eps", EPS_MEMBERS["tiny_eps"]),
        "doublet_mass_squared_equals_eps": _get(report, "flags", "doublet_mass_squared_equals_eps") is True,
        "doublet_lightest_for_eps_below_r0sq_over_96": doublet.get("eps_range_for_lightest_multiplicity_4")
        == "0 < eps < r0^2/96 = %s" % DOUBLET_LIGHTEST_BELOW,
        "doublet_directions_are_Re_H6_to_H9": doublet.get("doublet_chart_indices") == list(DOUBLET_REAL_X)
        and _get(report, "light_doublet_directions", "chart_indices") == list(DOUBLET_REAL_X),
        "H_block_chart_curvatures_0_r0sq_1_1_plus_r0sq": doublet.get("H_block_chart_curvatures")
        == {"0": 4, "1/25": 4, "1": 6, "26/25": 6},
        "rest_block_nullity_35_next_level_r0sq_over_96_multiplicity_14": doublet.get(
            "rest_block_from_benchmark_certificate"
        )
        == {
            "nullity": EXPECTED_FULL_RANK,
            "eigenvalues_below_r0_squared_over_96": EXPECTED_FULL_RANK,
            "eigenvalue_r0_squared_over_96_multiplicity": SECOND_LEVEL_MULTIPLICITY,
        },
        "tuned_benchmark_447_39_kernel_orbit_plus_doublet": bool(
            bench.get("exact_PSD") is True
            and bench.get("exact_rank") == EXPECTED_TUNED_RANK
            and bench.get("exact_nullity") == EXPECTED_TUNED_NULLITY
            and bench.get("kernel_equals_expected_span") is True
            and _get(bench, "inertia", "negative") == 0
        ),
        "eps_window_0_to_599_over_50_passes": bool(
            _get(eps, "final_acceptance_test", "currently_passes") is True
            and isinstance(window, Mapping)
            and window.get("lower_exclusive") == "0"
            and window.get("upper_exclusive") == str(EPS_WINDOW_UPPER)
        ),
        "symmetry_ranks_33_34_35": _get(report, "symmetry_tangents", "exact_ranks")
        == {"so10": 33, "so10_plus_X": 34, "so10_plus_X_plus_PQ": 35, "scaled_T_u": 35},
        "float64_compiler_binding_passes": _get(report, "flags", "source_binding_exact") is True,
        "does_not_close_G3_by_itself": _get(report, "flags", "report_closes_g3_by_itself") is False
        and report.get("G3_closed") is False,
    }


def equality_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    tangent = _get(report, "P3_H_S_Phi17_phases", "tangent_rank", default={})
    charges = _get(report, "P3_H_S_Phi17_phases", "charges", default={})
    pq_status = charges.get("PQ_status") if isinstance(charges, Mapping) else None
    return {
        "status_proved": report.get("status") == equality.STATUS_PROVED,
        "no_failed_checks": _passes(report),
        "theorem_claimed": report.get("theorem_claimed") is True,
        "same_model_contract": report.get("model_contract_id") == MODEL_CONTRACT_ID,
        "equality_set_unique_modulo_G_including_PQ": bool(
            _get(report, "flags", "equality_set_unique_modulo_symmetry_certified") is True
            and _get(report, "flags", "uniqueness_is_modulo_G_including_accidental_U1_PQ") is True
            and _get(report, "flags", "unique_modulo_SO10_x_U1X_alone") is False
        ),
        "tangent_ranks_33_34_35_kernel_12_without_phase": bool(
            isinstance(tangent, Mapping)
            and tangent.get("rank_so10") == EXPECTED_SO10_RANK
            and tangent.get("rank_so10_plus_X") == EXPECTED_GAUGE_RANK
            and tangent.get("rank_so10_plus_X_plus_PQ") == EXPECTED_FULL_RANK
            and tangent.get("kernel_dimension") == EXPECTED_STABILIZER_DIMENSION
            and tangent.get("kernel_has_no_X_or_PQ_component") is True
        ),
        "X_and_PQ_charges_as_declared": isinstance(charges, Mapping)
        and charges.get("X_charges") == X_CHARGES
        and charges.get("PQ_charges") == PQ_CHARGES,
        "S_Phi17_charge_determinant_minus_68": isinstance(charges, Mapping)
        and charges.get("determinant") == EXPECTED_PHASE_DETERMINANT,
        "PQ_declared_accidental_global": isinstance(pq_status, str) and "accidental global symmetry" in pq_status,
    }


def candidate_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    quartic = _get(report, "light_doublet_quartic", default={})
    stabilizer = _get(report, "sm_embedding", "full_state_stabilizer_so10_plus_u1x", default={})
    return {
        "no_failed_checks": _passes(report),
        "same_model_contract": report.get("model_contract_id") == MODEL_CONTRACT_ID,
        "lambda_eff_127_over_64": quartic.get("lambda_eff") == str(LAMBDA_EFF),
        "lambda_eff_normalisation_canonical_h": quartic.get("normalization")
        == "V = lambda (h^dag h)^2, canonically normalised h (g3_tuned_target_effective_higgs_quartic_v20)",
        "candidate_is_sm_vacuum": _get(report, "flags", "candidate_is_sm_vacuum") is True
        and _get(report, "flags", "target_unbroken_algebra_is_standard_model") is True,
        "full_state_stabilizer_dim_12_without_U1X_admixture": stabilizer
        == {"so10_only_dimension": 12, "stabilizer_dimension": 12, "u1x_admixture_dimension": 0, "u1x_broken": True},
        "no_electroweak_breaking_disclosed": _get(report, "flags", "electroweak_symmetry_breaking_realized") is False,
    }


def sigma_audit_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    pair = _get(report, "pair_stabilizers", "p|sm_singlet_Y0", default={})
    spectrum = _get(pair, "centre_spectrum_on_vector_10", default={})
    return {
        "no_failed_checks": _passes(report),
        "same_model_contract": report.get("model_contract_id") == sigma_audit.MODEL_CONTRACT_ID == MODEL_CONTRACT_ID,
        "p_sm_singlet_pair_is_standard_SM": bool(
            pair.get("is_sm_type") is True
            and pair.get("contains_standard_sm_algebra") is True
            and pair.get("stabilizer_dimension") == EXPECTED_STABILIZER_DIMENSION
            and pair.get("centre_proportional_to") == ["Y_standard"]
        ),
        "weak_block_hypercharge_half_colour_third": bool(
            isinstance(spectrum, Mapping)
            and spectrum.get("weak_block_6_9") == {"1/2": 4}
            and spectrum.get("colour_block_0_5") == {"1/3": 6}
        ),
        "hypercharge_convention_standard": _get(report, "conventions", "Y") == "T3R + (B-L)/2"
        and _get(report, "conventions", "hermitian_generator")
        == "J_ab = -i L_ab, L_ab e_b = e_a, L_ab e_a = -e_b (direct.generator_action)",
    }


def contract_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    contract = _get(report, "authoritative_contract", default={})
    return {
        "no_failed_checks": _passes(report),
        "same_model_contract": report.get("model_contract_id") == MODEL_CONTRACT_ID,
        "gauge_group_SO10_x_U1X": _get(contract, "gauge") == ["SO(10)", "U(1)_X"],
        "PQ_is_accidental_global_not_gauged": _get(contract, "accidental_global") == ["U(1)_PQ"],
    }


# ---------------------------------------------------------------------------
# The exact tangent matrix at the witness.
# ---------------------------------------------------------------------------


def phase_column(charges: Mapping[str, int]) -> np.ndarray:
    """Integer tangent of a U(1) with the given charges at the raw vacuum (H = 0 carries no tangent)."""
    s_real, s_imaginary = equality._sigma_std_integer()
    column = np.zeros(TOTAL_DIM, dtype=np.int64)
    block = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
    block[0::2] = -int(charges["Sigma126bar"]) * s_imaginary
    block[1::2] = int(charges["Sigma126bar"]) * s_real
    column[chart.SIGMA_SLICE] = block
    column[chart.S_SLICE] = [0, int(charges["S"])]
    column[chart.X_SLICE] = [0, int(charges["Phi17"])]
    return column


@lru_cache(maxsize=1)
def witness_integer_tangent_matrix() -> np.ndarray:
    """The equality module's 486 x 47 integer tangents (built by the Hessian module with the same helpers)."""
    matrix = np.asarray(hessian.integer_tangent_matrix(), dtype=np.int64)
    matrix.setflags(write=False)
    return matrix


def tangent_matrix(
    *,
    matrix: np.ndarray | None = None,
    x_charges: Mapping[str, int] | None = None,
    pq_charges: Mapping[str, int] | None = None,
) -> np.ndarray:
    """The tangent matrix used by the certificate; the keywords exist for fail-closed mutation tests."""
    output = np.array(witness_integer_tangent_matrix() if matrix is None else matrix, dtype=np.int64)
    if x_charges is not None:
        output[:, SO10_GENERATOR_COUNT] = phase_column(x_charges)
    if pq_charges is not None:
        output[:, GAUGE_GENERATOR_COUNT] = phase_column(pq_charges)
    return output


def _integer_rows(matrix: np.ndarray, columns: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(value) for value in row[:columns]) for row in np.asarray(matrix).tolist())


def _rank(rows: Sequence[Sequence[Any]]) -> int:
    rows = tuple(tuple(row) for row in rows)
    return superseded._row_echelon_metadata(rows)[0] if rows else 0


def _span_rank(vectors: Sequence[Mapping[int, Fraction]]) -> int:
    """Exact rank of sparse vectors, eliminating over their coordinate rows (fast: few columns)."""
    support = sorted({index for vector in vectors for index in vector})
    return _rank([tuple(vector.get(index, 0) for vector in vectors) for index in support])


def _chart_scale_string(power: int, value: Fraction) -> str:
    rational = value * 2 ** (power // 2)
    return str(rational) if power % 2 == 0 else "sqrt(2)*(%s)" % rational


def rank_certificate(matrix: np.ndarray, columns: int) -> dict[str, Any]:
    """Nonzero integer minor plus independent exact right null vectors for the first ``columns`` generators."""
    rows = _integer_rows(matrix, columns)
    labels = GENERATOR_LABELS[:columns]
    rank, pivot_rows, pivot_columns = superseded._row_echelon_metadata(rows)
    minor = [[rows[row][column] for column in pivot_columns] for row in pivot_rows]
    determinant = superseded._bareiss_determinant(minor) if minor else 0
    null = superseded._right_nullspace(rows, pivot_rows)
    null_rank = _rank(null)
    residuals_zero = all(superseded._matrix_vector_product_is_zero(rows, vector) for vector in null)
    scale = hessian.tangent_row_scale()
    scale_product = math.prod((scale[row] for row in pivot_rows), start=Fraction(1))
    complex_rows = sum(1 for row in pivot_rows if row >= chart.PHI_DIM)
    names = chart.coordinate_names()
    phase_free = all(all(value == 0 for value in vector[SO10_GENERATOR_COUNT:]) for vector in null)
    return {
        "columns": ["so(10) L_ab (45)"] + list(labels[SO10_GENERATOR_COUNT:]),
        "rank": rank,
        "right_nullity": columns - rank,
        "minor": {
            "shape": [len(pivot_rows), len(pivot_columns)],
            "row_indices": list(pivot_rows),
            "row_coordinate_names": [names[row] for row in pivot_rows],
            "column_generator_labels": [labels[column] for column in pivot_columns],
            "determinant_integer_M": determinant,
            "determinant_nonzero": determinant != 0,
            "u_row_scale_product": scale_product,
            "determinant_D_u_M": scale_product * determinant,
            "complex_block_rows": complex_rows,
            "determinant_D_chart_M": _chart_scale_string(complex_rows, scale_product * determinant),
        },
        "right_null_vectors": superseded._null_vector_report(null, labels),
        "null_vector_count": len(null),
        "null_vector_rank": null_rank,
        "null_residuals_exactly_zero": residuals_zero,
        "null_vectors_without_X_or_PQ_coefficient": phase_free,
        "_null": null,
        "_rows": rows,
    }


def gauge_quotient_section(matrix: np.ndarray, contract: Mapping[str, bool]) -> dict[str, Any]:
    certificates = {
        "SO10": rank_certificate(matrix, SO10_GENERATOR_COUNT),
        "SO10_x_U1X": rank_certificate(matrix, GAUGE_GENERATOR_COUNT),
        "SO10_x_U1X_x_PQ": rank_certificate(matrix, FULL_GENERATOR_COUNT),
    }
    expected_ranks = {"SO10": EXPECTED_SO10_RANK, "SO10_x_U1X": EXPECTED_GAUGE_RANK, "SO10_x_U1X_x_PQ": EXPECTED_FULL_RANK}
    so10 = certificates["SO10"]
    sm_basis = tuple(tuple(int(value) for value in vector) for vector in sigma_audit.standard_sm_integer_basis())
    sm_annihilates = all(superseded._matrix_vector_product_is_zero(so10["_rows"], vector) for vector in sm_basis)
    sm_rank = _rank(sm_basis)
    union_rank = _rank(sm_basis + tuple(so10["_null"]))
    stabilizer_is_sm = bool(
        sm_annihilates and sm_rank == EXPECTED_STABILIZER_DIMENSION and union_rank == EXPECTED_STABILIZER_DIMENSION
    )
    full_rows = certificates["SO10_x_U1X_x_PQ"]["_rows"]
    s_y = chart.S_SLICE.start + 1
    x_y = chart.X_SLICE.start + 1
    phase_minor = [
        [full_rows[s_y][SO10_GENERATOR_COUNT], full_rows[s_y][GAUGE_GENERATOR_COUNT]],
        [full_rows[x_y][SO10_GENERATOR_COUNT], full_rows[x_y][GAUGE_GENERATOR_COUNT]],
    ]
    phase_determinant = phase_minor[0][0] * phase_minor[1][1] - phase_minor[0][1] * phase_minor[1][0]
    pristine = witness_integer_tangent_matrix()
    phase_columns_bound = bool(
        np.array_equal(pristine[:, SO10_GENERATOR_COUNT], phase_column(X_CHARGES))
        and np.array_equal(pristine[:, GAUGE_GENERATOR_COUNT], phase_column(PQ_CHARGES))
    )
    scale = hessian.tangent_row_scale()
    row_scale_nonzero = all(value != 0 for index, value in enumerate(scale) if not chart.H_SLICE.start <= index < chart.H_SLICE.stop)
    h_rows_vanish = not np.any(np.asarray(matrix)[chart.H_SLICE])
    ranks = {name: certificates[name]["rank"] for name in certificates}
    gauge_rank = ranks["SO10_x_U1X"]
    full_rank = ranks["SO10_x_U1X_x_PQ"]
    checks = {
        "tangent_matrix_is_486x47_integer": np.asarray(matrix).shape == (TOTAL_DIM, FULL_GENERATOR_COUNT)
        and np.issubdtype(np.asarray(matrix).dtype, np.integer),
        "tangent_matrix_equals_equality_module_construction": bool(np.array_equal(matrix, pristine)),
        "phase_columns_rebuilt_from_declared_X_and_PQ_charges": phase_columns_bound,
        "row_scaling_D_invertible_at_witness_r0_x0_positive": bool(row_scale_nonzero and R0 > 0 and X0 > 0),
        "tangents_vanish_on_H_block": bool(h_rows_vanish),
    }
    for name, certificate in certificates.items():
        size = expected_ranks[name]
        checks[f"{name}_rank_{size}_nonzero_{size}x{size}_integer_minor"] = bool(
            certificate["rank"] == size and certificate["minor"]["determinant_nonzero"]
        )
        checks[f"{name}_minor_determinant_{EXPECTED_MINOR_DETERMINANTS[name]}"] = (
            certificate["minor"]["determinant_integer_M"] == EXPECTED_MINOR_DETERMINANTS[name]
        )
        checks[f"{name}_12_independent_exact_null_vectors"] = bool(
            certificate["null_vector_count"] == EXPECTED_STABILIZER_DIMENSION
            and certificate["null_vector_rank"] == EXPECTED_STABILIZER_DIMENSION
            and certificate["null_residuals_exactly_zero"]
        )
    checks["null_vectors_have_no_X_or_PQ_coefficient"] = bool(
        certificates["SO10_x_U1X"]["null_vectors_without_X_or_PQ_coefficient"]
        and certificates["SO10_x_U1X_x_PQ"]["null_vectors_without_X_or_PQ_coefficient"]
    )
    checks["so10_stabilizer_equals_standard_SM_algebra"] = stabilizer_is_sm
    checks["U1X_PQ_phase_minor_on_S_y_Phi17_y_is_minus_68"] = bool(
        phase_minor == EXPECTED_PHASE_MINOR and phase_determinant == EXPECTED_PHASE_DETERMINANT
    )
    checks["gauge_quotient_dimension_452"] = TOTAL_DIM - gauge_rank == EXPECTED_GAUGE_QUOTIENT
    checks["massive_transverse_quotient_dimension_451"] = TOTAL_DIM - full_rank == EXPECTED_TRANSVERSE_QUOTIENT
    checks["PQ_global_not_gauged_and_not_in_gauge_span"] = bool(
        all(contract.values()) and full_rank == gauge_rank + 1 and gauge_rank == ranks["SO10"] + 1
    )
    for certificate in certificates.values():
        certificate.pop("_null")
        certificate.pop("_rows")
    return {
        "matrix": "D M: M = 486 x 47 integer tangents at (p, 0, sigma_std raw, 1, 1) (equality module), columns 45 "
        "so(10) L_ab, U(1)_X, PQ",
        "row_scaling": {
            "u_coordinates": "D_u = diag(1 on Phi, r0/4 on Sigma, r0 on S, x0 on Phi17) = diag(1, 1/20, 1/5, 1)",
            "chart": "D = sqrt(2) D_u on the complex blocks: diag(1, sqrt2 r0/4, sqrt2 r0, sqrt2 x0)",
            "invertible": row_scale_nonzero,
            "consequence": "rank(D M) = rank(M); a minor of D M is the integer minor times the row-scale product",
        },
        "certificates": certificates,
        "ranks": ranks,
        "stabilizer": {
            "dimension": EXPECTED_STABILIZER_DIMENSION if stabilizer_is_sm else so10["right_nullity"],
            "standard_SM_basis_source": "g3_sigma_hypercharge_audit_v20.standard_sm_integer_basis (su(3)_c + su(2)_L + Y)",
            "SM_basis_annihilates_vacuum_exactly": sm_annihilates,
            "SM_basis_rank": sm_rank,
            "rank_of_SM_basis_plus_null_vectors": union_rank,
            "equals_standard_SM_algebra": stabilizer_is_sm,
        },
        "U1X_PQ_independence": {
            "rows": ["S.y", "Phi17.y"],
            "columns": ["U1X", "PQ"],
            "minor": phase_minor,
            "determinant": phase_determinant,
        },
        "gauge_quotient_dimension_including_axion": TOTAL_DIM - gauge_rank,
        "massive_transverse_quotient_dimension": TOTAL_DIM - full_rank,
        "eaten_goldstones": {"total": gauge_rank, "SO10_over_SM": ranks["SO10"], "U1X": gauge_rank - ranks["SO10"]},
        "PQ": {
            "declared": "accidental global U(1)_PQ (GAUGED_U1X_SCALAR_CONTRACT_V20.json authoritative_contract)",
            "gauged": False,
            "eaten": False,
            "rank_increase_over_gauge_orbit": full_rank - gauge_rank,
            "contract_premises": dict(contract),
        },
        "superseded_point_values": dict(SUPERSEDED_VALUES),
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Exact metric geometry in the u-coordinates (q = D_c u, metric D_c^2 = diag(1^210, 2^276)).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def metric_diagonal() -> tuple[int, ...]:
    return tuple(hessian.congruence_scale_squared())


def u_columns(matrix: np.ndarray) -> list[Vector]:
    """T_u = D_u M column by column, sparse with Fraction entries."""
    scale = hessian.tangent_row_scale()
    matrix = np.asarray(matrix, dtype=np.int64)
    columns: list[Vector] = []
    for column in range(matrix.shape[1]):
        columns.append({int(row): int(matrix[row, column]) * scale[row] for row in np.flatnonzero(matrix[:, column]).tolist()})
    return columns


def metric_inner(left: Mapping[int, Fraction], right: Mapping[int, Fraction]) -> Fraction:
    metric = metric_diagonal()
    if len(left) > len(right):
        left, right = right, left
    return sum((metric[index] * value * right[index] for index, value in left.items() if index in right), Fraction(0))


def _dense(vector: Mapping[int, Fraction]) -> list[Fraction]:
    output = [Fraction(0)] * TOTAL_DIM
    for index, value in vector.items():
        output[index] = Fraction(value)
    return output


def vacuum_u() -> Vector:
    """q0 in u-coordinates: Phi = p, Sigma = (r0/4) sigma_std raw (Re, Im), S = (r0, 0), Phi17 = (x0, 0)."""
    vector: Vector = {equality.P_CHART_INDEX: Fraction(1)}
    s_real, s_imaginary = equality._sigma_std_integer()
    for index, (real, imaginary) in enumerate(zip(s_real.tolist(), s_imaginary.tolist(), strict=True)):
        if real:
            vector[chart.SIGMA_SLICE.start + 2 * index] = Fraction(int(real)) * R0 / 4
        if imaginary:
            vector[chart.SIGMA_SLICE.start + 2 * index + 1] = Fraction(int(imaginary)) * R0 / 4
    vector[chart.S_SLICE.start] = Fraction(R0)
    vector[chart.X_SLICE.start] = Fraction(X0)
    return vector


def chart_normalisation_section(matrix: np.ndarray) -> dict[str, Any]:
    """Exact: the chart conventions and the metric D_c^2; the vacuum is orthogonal to its orbit tangents."""
    conventions = {block.name: block.coordinate_convention for block in chart.BLOCKS}
    metric = metric_diagonal()
    metric_by_block = {name: sorted({metric[index] for index in range(block.start, block.stop)}) for name, block in BLOCK_SLICES.items()}
    q0 = vacuum_u()
    orthogonal = all(metric_inner(q0, column) == 0 for column in u_columns(matrix))
    norm_squared = metric_inner(q0, q0)
    return {
        "chart_statement": "live_g2_canonical_486_field_chart_v20: K_2 = 1/2 q^T q (identity kinetic metric); every "
        "complex coefficient c = (x + i y)/sqrt(2)",
        "block_conventions": conventions,
        "u_coordinates": "u_Phi = q_Phi, u_c = q_c/sqrt(2) = (Re c, Im c); K_2 = 1/2 u^T D_c^2 u",
        "metric_D_c_squared_by_block": metric_by_block,
        "vacuum_norm_squared_chart": norm_squared,
        "vacuum_norm_squared_expected": 1 + 4 * R0 * R0 + 2 * X0 * X0,
        "checks": {
            "chart_blocks_use_canonical_conventions": conventions == BLOCK_CONVENTIONS,
            "metric_is_1_on_Phi_and_2_on_complex_blocks": metric_by_block
            == {"Phi210": [1], "H10": [2], "Sigma126bar": [2], "S": [2], "Phi17": [2]},
            "vacuum_orthogonal_to_all_47_orbit_tangents_exact": orthogonal,
            "vacuum_norm_squared_1_plus_4r0sq_plus_2x0sq": norm_squared == 1 + 4 * R0 * R0 + 2 * X0 * X0,
        },
    }


def _integer_vector(vector: Mapping[int, Fraction]) -> tuple[np.ndarray, int]:
    """(object integer vector, common denominator) with vector = integer / denominator."""
    denominator = math.lcm(*(Fraction(value).denominator for value in vector.values())) if vector else 1
    output = np.zeros(TOTAL_DIM, dtype=object)
    output[...] = 0
    for index, value in vector.items():
        output[index] = int(Fraction(value) * denominator)
    return output, denominator


def axion_period_certificate(
    matrix: np.ndarray, x_charges: Mapping[str, int], pq_charges: Mapping[str, int], norm_squared: Fraction
) -> dict[str, Any]:
    """Exact period of the axion angle modulo SO(10) x U(1)_X, and v_a = F_PQ / (that period's denominator).

    Lower bound: S and Phi17 are SO(10) singlets, so PQ(theta) q0 = g q0 with g in SO(10) x U(1)_X forces
    q_PQ(F) theta - q_X(F) beta in 2 pi Z for F = S, Phi17, i.e. theta in 2 pi gcd(q_X(S), q_X(Phi17))/|det| Z
    (det the S/Phi17 charge minor).  Upper bound: an explicit element (beta, psi) with U(1)_X(beta) exp(psi L)
    reproducing PQ(2 pi gcd/|det|) q0, where L is an so(10) generator whose integer tangent is the pure Sigma phase
    (it fixes p) and H vanishes at q0 (the U(1)_X tangent vanishes on H while q_X(H) != 0).
    """
    matrix = np.asarray(matrix)
    x_s, x_17 = int(x_charges["S"]), int(x_charges["Phi17"])
    p_s, p_17 = int(pq_charges["S"]), int(pq_charges["Phi17"])
    determinant = p_s * x_17 - p_17 * x_s
    x_gcd = math.gcd(x_s, x_17)
    denominator = abs(determinant) // x_gcd if determinant and x_gcd else 0
    sigma_only = phase_column({"Sigma126bar": 1, "S": 0, "Phi17": 0})
    sigma_generators = [
        (GENERATOR_LABELS[column], sign)
        for column in range(SO10_GENERATOR_COUNT)
        for sign in (1, -1)
        if np.array_equal(matrix[:, column], sign * sigma_only)
    ]
    singlets = not np.any(matrix[chart.S_SLICE, :SO10_GENERATOR_COUNT]) and not np.any(
        matrix[chart.X_SLICE, :SO10_GENERATOR_COUNT]
    )
    h_vanishes = int(x_charges["H10"]) != 0 and not np.any(matrix[chart.H_SLICE, SO10_GENERATOR_COUNT])
    theta = Fraction(x_gcd, abs(determinant)) if denominator else None
    element: dict[str, Any] | None = None
    if theta is not None and sigma_generators:
        for step in range(abs(determinant)):
            beta = Fraction(step, abs(determinant))
            if (p_s * theta - x_s * beta).denominator == 1 and (p_17 * theta - x_17 * beta).denominator == 1:
                label, sign = sigma_generators[0]
                absorb = (int(pq_charges["Sigma126bar"]) * theta - int(x_charges["Sigma126bar"]) * beta) % 1
                element = {"theta_PQ": theta, "beta_U1X": beta, "so10_generator": label, "psi_so10": (sign * absorb) % 1}
                break
    v_a_squared = norm_squared * x_gcd**2 / determinant**2 if determinant else None
    closed_denominator = x_s**2 * R0 * R0 + x_17**2 * X0 * X0
    v_a_closed = 2 * R0 * R0 * X0 * X0 * x_gcd**2 / closed_denominator if closed_denominator else None
    certified = bool(
        denominator == EXPECTED_AXION_PERIOD_DENOMINATOR
        and element is not None
        and singlets
        and h_vanishes
        and v_a_squared == EXPECTED_V_A_SQUARED
        and v_a_squared == v_a_closed
    )
    return {
        "S_Phi17_charge_minor_det": determinant,
        "gcd_qX_S_qX_Phi17": x_gcd,
        "period_denominator": denominator,
        "lower_bound": "S, Phi17 are SO(10) singlets: PQ(theta) q0 = g q0 needs q_PQ(F) theta - q_X(F) beta in 2 pi Z "
        "(F = S, Phi17), so theta in (2 pi gcd/|det|) Z; equivalently every SO(10) x U(1)_X-invariant monomial in S, "
        "Phi17 and their conjugates (a power of Phi17^4 conj(S)^17 or of its conjugate) has PQ charge in 68 Z",
        "SO10_acts_trivially_on_S_and_Phi17": singlets,
        "H_vanishes_at_q0": h_vanishes,
        "Sigma_phase_so10_generators": [label for label, _ in sigma_generators],
        "explicit_gauge_element_units_of_2pi": element,
        "explicit_element_meaning": "PQ(theta) q0 = U(1)_X(beta) exp(psi L) q0 (angles in units of 2 pi); L fixes p "
        "and rotates the Sigma phase (its integer tangent is the pure Sigma phase)",
        "v_a_squared": v_a_squared,
        "v_a_squared_closed_form": "2 r0^2 x0^2 gcd^2/(q_X(S)^2 r0^2 + q_X(Phi17)^2 x0^2) = 2 r0^2 x0^2/(16 r0^2 + "
        "289 x0^2)",
        "v_a_squared_closed_form_value": v_a_closed,
        "certified": certified,
    }


def axion_section(matrix: np.ndarray, gauge_pivot_columns: Sequence[int], x_charges: Mapping[str, int], pq_charges: Mapping[str, int]) -> dict[str, Any]:
    columns = u_columns(matrix)
    gauge_columns = columns[:GAUGE_GENERATOR_COUNT]
    t_pq = columns[GAUGE_GENERATOR_COUNT]
    basis = [gauge_columns[index] for index in gauge_pivot_columns]
    gram = [[metric_inner(left, right) for right in basis] for left in basis]
    gram_determinant = equality.exact_det(gram) if gram else Fraction(0)
    coefficients: list[Fraction] = []
    if gram and gram_determinant != 0:
        coefficients = equality.exact_solve(gram, [metric_inner(vector, t_pq) for vector in basis])
    axion: Vector = dict(t_pq)
    for coefficient, vector in zip(coefficients, basis):
        if coefficient:
            for index, value in vector.items():
                axion[index] = axion.get(index, Fraction(0)) - coefficient * value
    axion = {index: value for index, value in axion.items() if value != 0}
    norm_squared = metric_inner(axion, axion)
    orthogonal = all(metric_inner(axion, column) == 0 for column in gauge_columns)
    rank_all = _span_rank(columns)
    rank_with_axion = _span_rank(columns + [axion])
    rank_gauge_with_axion = _span_rank(gauge_columns + [axion])
    rank_gauge = _span_rank(gauge_columns)
    pairing = [[metric_inner(left, right) for right in columns] for left in gauge_columns]
    pairing_rank = _rank(pairing)
    intersection_dimension = rank_all - pairing_rank
    fractions: dict[str, Fraction | None] = {}
    metric = metric_diagonal()
    for name, block in BLOCK_SLICES.items():
        part = sum((metric[index] * value * value for index, value in axion.items() if block.start <= index < block.stop), Fraction(0))
        fractions[name] = part / norm_squared if norm_squared else None
    s_x, s_y = chart.S_SLICE.start, chart.S_SLICE.start + 1
    x_x, x_y = chart.X_SLICE.start, chart.X_SLICE.start + 1
    pure_phase = bool(axion.get(s_x, 0) == 0 and axion.get(x_x, 0) == 0 and not any(
        block.start <= index < block.stop for index in axion for block in (chart.PHI_SLICE, chart.H_SLICE, chart.SIGMA_SLICE)
    ))
    charge_minor = int(pq_charges["S"]) * int(x_charges["Phi17"]) - int(pq_charges["Phi17"]) * int(x_charges["S"])
    closed_denominator = int(x_charges["S"]) ** 2 * R0 * R0 + int(x_charges["Phi17"]) ** 2 * X0 * X0
    closed_form = 2 * R0 * R0 * X0 * X0 * charge_minor**2 / closed_denominator if closed_denominator else None
    pq_norm_squared = metric_inner(t_pq, t_pq)
    period = axion_period_certificate(matrix, x_charges, pq_charges, norm_squared)
    labels = [GENERATOR_LABELS[index] for index in gauge_pivot_columns]
    chart_components = {}
    names = chart.coordinate_names()
    for index, value in sorted(axion.items()):
        chart_components[names[index]] = str(value) if index < chart.PHI_DIM else "sqrt(2)*(%s)" % value
    checks = {
        "gauge_gram_on_34_pivot_tangents_nonsingular": bool(len(basis) == EXPECTED_GAUGE_RANK and gram_determinant != 0),
        "axion_orthogonal_to_all_46_gauge_tangents_exact": orthogonal,
        "axion_nonzero": norm_squared != 0,
        "axion_lies_in_orbit_tangent_span_T35": bool(rank_all == EXPECTED_FULL_RANK and rank_with_axion == rank_all),
        "axion_not_in_gauge_span": bool(rank_gauge == EXPECTED_GAUGE_RANK and rank_gauge_with_axion == rank_gauge + 1),
        "T35_cap_gauge_complement_is_one_dimensional": bool(pairing_rank == EXPECTED_GAUGE_RANK and intersection_dimension == 1),
        "axion_norm_squared_9248_over_7241": norm_squared == EXPECTED_AXION_NORM_SQUARED,
        "axion_norm_squared_matches_closed_form": closed_form is not None and norm_squared == closed_form,
        "axion_composition_S_7225_Phi17_16_over_7241_Sigma_Phi_H_0": fractions == EXPECTED_AXION_FRACTIONS,
        "axion_is_pure_S_and_Phi17_phase": pure_phase,
        "axion_period_modulo_gauge_2pi_over_68": bool(
            period["certified"] and period["period_denominator"] == EXPECTED_AXION_PERIOD_DENOMINATOR
        ),
    }
    return {
        "construction": "a = t_PQ - sum_k c_k g_k, (g_k) the 34 pivot gauge tangents, c solving the Gram system "
        "<g_j, g_k> c_k = <g_j, t_PQ> in the metric D_c^2 (u-coordinates; the chart metric); unique since a is the "
        "orthogonal projection of t_PQ onto G34^perp",
        "gauge_basis_labels": labels,
        "gauge_gram_determinant": gram_determinant,
        "projection_coefficients": {labels[index]: value for index, value in enumerate(coefficients) if value},
        "axion_u_components": {names[index]: value for index, value in sorted(axion.items())},
        "axion_chart_components": chart_components,
        "axion_norm_squared": norm_squared,
        "axion_norm_squared_closed_form": "2 r0^2 x0^2 (q_PQ(S) q_X(Phi17) - q_PQ(Phi17) q_X(S))^2 / (q_X(S)^2 r0^2 "
        "+ q_X(Phi17)^2 x0^2) = 2 r0^2 x0^2 68^2 / (16 r0^2 + 289 x0^2)",
        "axion_norm_squared_closed_form_value": closed_form,
        "PQ_tangent_norm_squared": pq_norm_squared,
        "PQ_tangent_norm_squared_inside_gauge_span": pq_norm_squared - norm_squared,
        "squared_norm_fractions": fractions,
        "composition": {
            "Sigma_phase": fractions["Sigma126bar"],
            "S_phase": fractions["S"],
            "Phi17_phase": fractions["Phi17"],
            "Phi210": fractions["Phi210"],
            "H10": fractions["H10"],
        },
        "decay_constant": {
            "F_PQ_squared": norm_squared,
            "units": "M_GUT^2 (chart units; the chart unit |Phi| = 1 is M_GUT)",
            "convention": "theta_PQ -> exp(i theta Q_PQ) q0 with Q_PQ(Sigma126bar, H10, S, Phi17) = (-2, -2, 4, 0); "
            "the physical axion is the canonical-metric component of d/dtheta orthogonal to the gauge orbit, with "
            "kinetic term (1/2) F_PQ^2 (d theta)^2, F_PQ^2 = |a|^2.  theta = pi acts trivially on the scalar fields, "
            "but modulo the gauge group the axion angle has period 2 pi/68: S and Phi17 are SO(10) singlets, so "
            "PQ(theta) q0 = g q0 with g in SO(10) x U(1)_X needs 4 (theta - beta) and 17 beta in 2 pi Z, i.e. theta in "
            "(2 pi/68) Z, with 68 = |q_PQ(S) q_X(Phi17) - q_PQ(Phi17) q_X(S)|/gcd(q_X(S), q_X(Phi17)) the PQ charge of "
            "the gauge-invariant Phi17^4 conj(S)^17; conversely U(1)_X at beta = 26 pi/17 followed by exp(pi L_01) "
            "(L_01 fixes p and rotates the Sigma phase; H = 0) reproduces theta = pi/34.  So a = F_PQ theta has period "
            "2 pi v_a with v_a = F_PQ/68, v_a^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2) = 2/7241 M_GUT^2.  The axion zero "
            "mode is exact for the renormalizable PQ-neutral benchmark potential only: PQ-violating non-renormalizable "
            "operators such as Phi17^4 conj(S)^17 (PQ charge -68, a potential in cos(a/v_a + delta)) lift it "
            "explicitly and are not included.  The conversion to f_a = v_a/N_DW needs the QCD anomaly (domain-wall) "
            "coefficient and the fermion PQ charges, which are not computed here",
            "axion_angle_period_modulo_gauge": "2 pi/%d" % period["period_denominator"]
            if period["period_denominator"]
            else None,
            "period_certificate": period,
            "v_a_squared": period["v_a_squared"],
            "v_a_squared_units": "M_GUT^2 (a/v_a has period 2 pi)",
            "F_PQ_squared_float": float(norm_squared),
            "v_a_squared_float": float(period["v_a_squared"]) if period["v_a_squared"] is not None else None,
        },
        "rank_data": {
            "rank_T47": rank_all,
            "rank_T47_plus_axion": rank_with_axion,
            "rank_gauge_46": rank_gauge,
            "rank_gauge_46_plus_axion": rank_gauge_with_axion,
            "rank_of_gauge_pairing_with_T47": pairing_rank,
            "dim_T35_cap_gauge_complement": intersection_dimension,
        },
        "_axion": axion,
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Fresh exact Hessians at the witness members (and the tuned point).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def fresh_hessian_certificates() -> dict[str, dict[str, Any]]:
    return {variant: hessian.exact_certificate(variant) for variant in FRESH_VARIANTS}


@lru_cache(maxsize=1)
def raised_second_level_inertia() -> dict[str, int]:
    numerator, denominator = hessian.exact_hessian("raised_O06")["hessian"]
    inertia = hessian.component_inertia(numerator, denominator, shift=DOUBLET_LIGHTEST_BELOW)
    return {key: inertia[key] for key in ("negative", "zero", "positive")}


def doublet_matrix(indices: Sequence[int]) -> np.ndarray:
    output = np.zeros((TOTAL_DIM, len(indices)), dtype=np.int64)
    for column, index in enumerate(indices):
        output[int(index), column] = 1
    return output


def fresh_hessian_section(matrix: np.ndarray, axion: Mapping[int, Fraction], doublet_indices: Sequence[int]) -> dict[str, Any]:
    certificates = fresh_hessian_certificates()
    scaled = hessian._scaled_tangents(matrix)
    axion_integer, _ = _integer_vector(axion)
    axion_column = axion_integer.reshape(TOTAL_DIM, 1)
    d4 = doublet_matrix(doublet_indices)
    rows: dict[str, dict[str, Any]] = {}
    for variant in FRESH_VARIANTS:
        numerator, denominator = hessian.exact_hessian(variant)["hessian"]
        cert = certificates[variant]
        eps = EPS_MEMBERS.get(variant, Fraction(0))
        tangent_zero = hessian._all_zero(hessian._exact_matmul(numerator, scaled))
        axion_zero = hessian._all_zero(hessian._exact_matmul(numerator, axion_column)) if axion else False
        doublet_product = hessian._exact_matmul(numerator, d4)
        doublet_eigen = hessian._fraction_matrix_equal(doublet_product, denominator, d4, 2 * eps)
        rows[variant] = {
            "eps": eps,
            "O06": cert["O06"],
            "inertia_positive_zero_negative": "%d/%d/%d" % (
                cert["inertia"]["positive"],
                cert["inertia"]["zero"],
                cert["inertia"]["negative"],
            ),
            "exact_PSD": cert["exact_PSD"],
            "exact_rank": cert["exact_rank"],
            "exact_nullity": cert["exact_nullity"],
            "gradient_exactly_zero": cert["gradient_exactly_zero"],
            "kernel_equals_expected_span": cert["kernel_equals_expected_span"],
            "H_u_annihilates_all_47_tangents": tangent_zero,
            "H_u_annihilates_axion": axion_zero,
            "H_u_doublet_equals_2_eps_doublet": doublet_eigen,
            "smallest_nonzero_eigenvalue": cert["spectral_gap"]["lambda"],
            "smallest_nonzero_is_certified": cert["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"],
            "smallest_nonzero_multiplicity": cert["spectral_gap"]["multiplicity"],
        }
    second = raised_second_level_inertia()
    member_ok = {
        variant: bool(
            rows[variant]["inertia_positive_zero_negative"] == "451/35/0"
            and rows[variant]["exact_PSD"]
            and rows[variant]["kernel_equals_expected_span"]
            and rows[variant]["gradient_exactly_zero"]
            and rows[variant]["H_u_annihilates_all_47_tangents"]
            and rows[variant]["H_u_annihilates_axion"]
            and rows[variant]["smallest_nonzero_eigenvalue"] == EPS_MEMBERS[variant]
            and rows[variant]["smallest_nonzero_is_certified"]
            and rows[variant]["smallest_nonzero_multiplicity"] == LIGHT_DOUBLET_REAL_DIMENSION
        )
        for variant in EPS_MEMBERS
    }
    bench = rows["benchmark"]
    checks = {
        "fresh_eps_r0sq_over_100_inertia_451_35_0_kernel_T35_annihilates_axion": member_ok["raised_O06"],
        "fresh_eps_r0sq_over_10e6_inertia_451_35_0_kernel_T35_annihilates_axion": member_ok["tiny_eps"],
        "fresh_tuned_eps_0_inertia_447_39_0_kernel_T35_plus_doublet": bool(
            bench["inertia_positive_zero_negative"] == "447/39/0"
            and bench["exact_PSD"]
            and bench["kernel_equals_expected_span"]
            and bench["H_u_annihilates_all_47_tangents"]
            and bench["H_u_annihilates_axion"]
            and bench["H_u_doublet_equals_2_eps_doublet"]
        ),
        "fresh_doublet_exact_eigenvectors_mass_squared_eps_at_both_members": all(
            rows[variant]["H_u_doublet_equals_2_eps_doublet"] for variant in EPS_MEMBERS
        ),
        "fresh_second_level_r0sq_over_96_multiplicity_14_at_r0sq_over_100": second
        == {"negative": EXPECTED_FULL_RANK + LIGHT_DOUBLET_REAL_DIMENSION, "zero": SECOND_LEVEL_MULTIPLICITY,
            "positive": TOTAL_DIM - EXPECTED_FULL_RANK - LIGHT_DOUBLET_REAL_DIMENSION - SECOND_LEVEL_MULTIPLICITY},
    }
    return {
        "source": "g3_sm_pati_salam_exact_hessian_v20.exact_certificate / exact_hessian (recomputed here, exact over Q)",
        "variants": rows,
        "second_level_pencil_at_r0sq_over_100": {
            "shift": DOUBLET_LIGHTEST_BELOW,
            "inertia_of_H_u_minus_shift_D_c_squared": second,
            "meaning": "35 zero + 4 doublet (eps) below r0^2/96, the level r0^2/96 with multiplicity 14, 433 above",
        },
        "checks": checks,
    }


def restricted_hessian_section(
    gauge: Mapping[str, Any],
    axion: Mapping[str, Any],
    fresh: Mapping[str, Any],
    premises: Mapping[str, bool],
    matrix: np.ndarray,
    doublet_indices: Sequence[int],
) -> dict[str, Any]:
    """The Hessian restricted to W = G34^perp: an exact lemma whose inputs are certified above."""
    gauge_rank = gauge["ranks"]["SO10_x_U1X"]
    w_dimension = TOTAL_DIM - gauge_rank
    kernel_dimension = axion["rank_data"]["rank_T47"]
    w_cap_kernel = axion["rank_data"]["dim_T35_cap_gauge_complement"]
    # The tuned point: ker = span(T47 + D4); D4 lies in the H block, where every gauge tangent vanishes.
    columns = u_columns(matrix)
    d4 = [{int(index): Fraction(1)} for index in doublet_indices]
    tuned_rank = _span_rank(columns + d4)
    tuned_pairing_rank = _rank([[metric_inner(left, right) for right in columns + d4] for left in columns[:GAUGE_GENERATOR_COUNT]])
    tuned_w_cap_kernel = tuned_rank - tuned_pairing_rank
    doublet_orthogonal = all(metric_inner(vector, column) == 0 for vector in d4 for column in columns)
    inputs_eps = bool(
        premises["eps_family_kernel_is_orbit_for_every_eps_positive"]
        and premises["L2_every_eps_positive_PSD_rank_451_nullity_35"]
        and fresh["checks"]["fresh_eps_r0sq_over_100_inertia_451_35_0_kernel_T35_annihilates_axion"]
        and fresh["checks"]["fresh_eps_r0sq_over_10e6_inertia_451_35_0_kernel_T35_annihilates_axion"]
    )
    geometry = bool(
        kernel_dimension == EXPECTED_FULL_RANK
        and w_cap_kernel == 1
        and all(axion["checks"][name] for name in (
            "axion_orthogonal_to_all_46_gauge_tangents_exact",
            "axion_nonzero",
            "axion_lies_in_orbit_tangent_span_T35",
            "T35_cap_gauge_complement_is_one_dimensional",
        ))
    )
    inputs_tuned = bool(
        premises["tuned_benchmark_447_39_kernel_orbit_plus_doublet"]
        and fresh["checks"]["fresh_tuned_eps_0_inertia_447_39_0_kernel_T35_plus_doublet"]
    )
    positive = w_dimension - w_cap_kernel
    tuned_positive = w_dimension - tuned_w_cap_kernel
    checks = {
        "gauge_complement_W_has_dimension_452": w_dimension == EXPECTED_GAUGE_QUOTIENT,
        "restricted_hessian_inputs_PSD_and_kernel_T35_for_every_eps_positive": inputs_eps,
        "restricted_hessian_psd_one_zero_mode_axion_451_positive": bool(
            inputs_eps and geometry and positive == EXPECTED_TRANSVERSE_QUOTIENT
        ),
        "restricted_spectrum_is_zero_plus_positive_hessian_spectrum": bool(inputs_eps and geometry),
        "tuned_limit_W_inertia_447_5_0_axion_plus_doublet": bool(
            inputs_tuned
            and doublet_orthogonal
            and tuned_rank == EXPECTED_TUNED_NULLITY
            and tuned_pairing_rank == EXPECTED_GAUGE_RANK
            and tuned_w_cap_kernel == 1 + LIGHT_DOUBLET_REAL_DIMENSION
            and tuned_positive == EXPECTED_TUNED_RANK
        ),
    }
    lowest_ok = bool(
        premises["doublet_lightest_for_eps_below_r0sq_over_96"]
        and premises["rest_block_nullity_35_next_level_r0sq_over_96_multiplicity_14"]
        and premises["H_block_chart_curvatures_0_r0sq_1_1_plus_r0sq"]
    )
    # The inertia and zero-mode statements are the lemma's conclusions: stated only when its checks pass.
    eps_certified = checks["restricted_hessian_psd_one_zero_mode_axion_451_positive"]
    tuned_certified = checks["tuned_limit_W_inertia_447_5_0_axion_plus_doublet"]
    return {
        "W": "G34^perp, the orthogonal complement of the 46 gauge tangents in the canonical chart metric "
        "(u-coordinates: {u : <g, u>_(D_c^2) = 0 for every gauge tangent g})",
        "lemma": (
            "Let K = ker Hess_q V_eps(q0) with Hess_q PSD and K = T35 (every eps > 0).  Then T35 = G34 (+) span(a) "
            "orthogonally (a is orthogonal to G34, lies in T35, and dim T35 = dim G34 + 1), so K^perp = G34^perp cap "
            "a^perp and W = G34^perp = span(a) (+) K^perp.  Hess_q is symmetric with kernel K, so K^perp = range(Hess_q) "
            "is invariant and Hess_q is positive definite on it.  Hence P_W Hess_q P_W on W is 0 on a and equals Hess_q "
            "on K^perp: PSD, with inertia (dim W - 1, 1, 0) and positive spectrum equal to the positive spectrum of "
            "Hess_q (Sylvester: identical statements hold for H_u with the metric D_c^2)."
        ),
        "dimensions": {
            "W": w_dimension,
            "kernel_T35": kernel_dimension,
            "W_cap_kernel_eps_positive": w_cap_kernel,
            "kernel_T35_plus_D4_tuned": tuned_rank,
            "W_cap_kernel_tuned": tuned_w_cap_kernel,
        },
        "eps_positive": {
            "certified": eps_certified,
            "inertia_on_W_positive_zero_negative": "%d/%d/%d" % (positive, w_cap_kernel, 0) if eps_certified else None,
            "zero_mode": "the physical axion a" if eps_certified else None,
            "positive_spectrum": "the %d positive eigenvalues of Hess_q V_eps(q0), counted with multiplicity" % positive
            if eps_certified
            else None,
            "lowest_levels_for_eps_below_r0sq_over_96": {
                "eps": LIGHT_DOUBLET_REAL_DIMENSION,
                str(DOUBLET_LIGHTEST_BELOW): SECOND_LEVEL_MULTIPLICITY,
                "above_" + str(DOUBLET_LIGHTEST_BELOW): EXPECTED_TRANSVERSE_QUOTIENT
                - LIGHT_DOUBLET_REAL_DIMENSION
                - SECOND_LEVEL_MULTIPLICITY,
                "bound_from": "the Hessian report's doublet section (H block decoupled, curvatures shifted by eps) and "
                "rest block (no eigenvalue in (0, r0^2/96), r0^2/96 with multiplicity 14), re-certified at eps = r0^2/100",
                "holds": bool(
                    lowest_ok
                    and eps_certified
                    and fresh["checks"]["fresh_second_level_r0sq_over_96_multiplicity_14_at_r0sq_over_100"]
                ),
            },
        },
        "tuned_eps_0": {
            "certified": tuned_certified,
            "inertia_on_W_positive_zero_negative": "%d/%d/%d" % (tuned_positive, tuned_w_cap_kernel, 0)
            if tuned_certified
            else None,
            "zero_modes": "the axion a and the 4 real doublet directions Re H_6..9 (in W: the gauge tangents vanish "
            "on the H block)"
            if tuned_certified
            else None,
            "doublet_orthogonal_to_all_tangents_exact": doublet_orthogonal,
        },
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# The light doublet: exact SM label.
# ---------------------------------------------------------------------------


def _fraction_matrix(matrix: np.ndarray, scale: Fraction = Fraction(1)) -> list[list[Fraction]]:
    return [[scale * int(value) for value in row] for row in np.asarray(matrix).tolist()]


def _matrix_is_scalar(matrix: Sequence[Sequence[Fraction]], value: Fraction) -> bool:
    return all(entry == (value if row == column else 0) for row, line in enumerate(matrix) for column, entry in enumerate(line))


def _sum_fraction_matrices(matrices: Sequence[Sequence[Sequence[Fraction]]], size: int) -> list[list[Fraction]]:
    output = [[Fraction(0)] * size for _ in range(size)]
    for matrix in matrices:
        for row in range(size):
            for column in range(size):
                output[row][column] += matrix[row][column]
    return output


def doublet_section(doublet_indices: Sequence[int], fresh: Mapping[str, Any], hessian_ok: Mapping[str, bool], candidate_ok: Mapping[str, bool], sigma_ok: Mapping[str, bool]) -> dict[str, Any]:
    local = [int(index) - chart.H_SLICE.start for index in doublet_indices]
    in_h_block = all(0 <= position < chart.H_REAL_DIM for position in local)
    real_parts = [position // 2 for position in local if position % 2 == 0]
    is_re_h_6_to_9 = bool(in_h_block and len(local) == LIGHT_DOUBLET_REAL_DIMENSION and real_parts == [6, 7, 8, 9])
    colour = sigma_audit.su3_colour_integer_basis()
    weak = sigma_audit.SU2L_INTEGER
    hypercharge = sigma_audit.Y_STANDARD_INTEGER
    others = [position for position in range(chart.H_REAL_DIM) if position not in local]

    def u_action(vector: Sequence[int]) -> np.ndarray:
        # H -> L H with real L acts on the interleaved (Re, Im) u-block as kron(L, I_2).
        return np.kron(sigma_audit._matrix(vector), np.eye(2, dtype=np.int64))

    def restrict(vector: Sequence[int]) -> np.ndarray:
        return u_action(vector)[np.ix_(local, local)] if in_h_block else np.zeros((len(local), len(local)), dtype=np.int64)

    generators = tuple(colour) + tuple(weak) + (hypercharge,)
    invariant = bool(in_h_block) and all(not np.any(u_action(vector)[np.ix_(others, local)]) for vector in generators)
    size = len(local)
    colour_singlet = invariant and all(not np.any(restrict(vector)) for vector in colour)
    weak_squares = [
        _fraction_matrix(restrict(vector) @ restrict(vector), Fraction(-1, 4)) for vector in weak
    ]
    casimir_weak = _sum_fraction_matrices(weak_squares, size)
    y_matrix = restrict(hypercharge)
    y_squared = _fraction_matrix(y_matrix @ y_matrix, Fraction(-1, 36))
    complex_structure = _fraction_matrix(y_matrix, Fraction(1, 3))
    j_squared = _fraction_matrix(y_matrix @ y_matrix, Fraction(1, 9))
    commutes = all(np.array_equal(y_matrix @ restrict(vector), restrict(vector) @ y_matrix) for vector in weak)
    t3 = restrict(sigma_audit.T3L_INTEGER)
    t3_squared = _fraction_matrix(t3 @ t3, Fraction(-1, 4))
    label_ok = bool(
        invariant
        and colour_singlet
        and _matrix_is_scalar(casimir_weak, Fraction(3, 4))
        and _matrix_is_scalar(y_squared, Fraction(1, 4))
        and _matrix_is_scalar(j_squared, Fraction(-1))
        and commutes
    )
    bench = fresh["variants"]["benchmark"]
    checks = {
        "doublet_directions_are_Re_H6_to_H9": bool(is_re_h_6_to_9 and list(doublet_indices) == list(DOUBLET_REAL_X)),
        "doublet_span_invariant_under_SM_algebra_exact": invariant,
        "doublet_colour_singlet_exact": colour_singlet,
        "doublet_SU2L_casimir_3_over_4_exact": invariant and _matrix_is_scalar(casimir_weak, Fraction(3, 4)),
        "doublet_hypercharge_squared_1_over_4_exact": invariant and _matrix_is_scalar(y_squared, Fraction(1, 4)),
        "doublet_Y_is_complex_structure_commuting_with_SU2L": bool(
            invariant and _matrix_is_scalar(j_squared, Fraction(-1)) and commutes
        ),
        "doublet_is_zero_mode_of_tuned_hessian_exact": bool(bench["H_u_doublet_equals_2_eps_doublet"]),
        "doublet_mass_squared_eps_committed_and_fresh": bool(
            hessian_ok["doublet_mass_squared_equals_eps"]
            and fresh["checks"]["fresh_doublet_exact_eigenvectors_mass_squared_eps_at_both_members"]
        ),
        "doublet_quartic_lift_127_over_64_committed_and_fresh": bool(
            candidate_ok["lambda_eff_127_over_64"]
            and candidate.exact_light_doublet_quartic(R0)["lambda_eff"] == LAMBDA_EFF
            and LAMBDA_EFF > 0
        ),
        "doublet_label_consistent_with_sigma_audit_weak_block": bool(
            sigma_ok["weak_block_hypercharge_half_colour_third"] and label_ok
        ),
    }
    return {
        "directions": {
            "chart_indices": list(doublet_indices),
            "names": [chart.coordinate_names()[int(index)] for index in doublet_indices],
            "meaning": "Re H_6 .. Re H_9 (the tuned electroweak doublet; Im H_6..9 have curvature r0^2 at eps = 0)",
        },
        "generators": "g3_sigma_hypercharge_audit_v20: su3_colour_integer_basis, SU2L_INTEGER (T_k = (-i/2) L'_k), "
        "Y_STANDARD_INTEGER (Y = (1/6)(-i) L_Y); on u_H the action is kron(L, I_2), so span(Re H_6..9) carries L[6:10, 6:10]",
        "exact_values": {
            "colour_generators_vanish": colour_singlet,
            "SU2L_casimir": casimir_weak[0][0] if size and _matrix_is_scalar(casimir_weak, casimir_weak[0][0]) else None,
            "Y_squared": y_squared[0][0] if size and _matrix_is_scalar(y_squared, y_squared[0][0]) else None,
            "T3L_squared": t3_squared[0][0] if size and _matrix_is_scalar(t3_squared, t3_squared[0][0]) else None,
            "complex_structure": "J = L_Y/3 restricted, J^2 = -1, [J, su(2)_L] = 0",
            "complex_structure_matrix": complex_structure,
        },
        "SM_label": "(1,2)_{1/2}: one complex SM doublet realified (equivalently its conjugate (1,2)_{-1/2}); |Y| = 1/2"
        if label_ok
        else None,
        "mass_squared": {
            "value": "eps (exact, every eps >= 0; units M_GUT^2)",
            "lightest_level_multiplicity_4_for": "0 < eps < r0^2/96 = %s" % DOUBLET_LIGHTEST_BELOW,
            "source": "committed Hessian report eps_family.doublet, re-certified here: H_u D4 = 2 eps D4 exactly at "
            "eps = r0^2/100 and r0^2/10^6 (D_c^2 = 2 on the H block)",
        },
        "tuned_limit": {
            "eps": 0,
            "zero_modes": LIGHT_DOUBLET_REAL_DIMENSION,
            "quartic_lift_lambda_eff": LAMBDA_EFF,
            "lambda_eff_formula": "2 - kappa^2/(4 r0^2) = 127/64 at kappa = -r0/4 (g3_sm_pati_salam_candidate_v20)",
            "normalisation": "V = V0 + lambda_eff (h^dag h)^2 + ... along the canonically normalised doublet h",
            "meaning": "the 4 zero modes of the tuned point are not flat: they are lifted at quartic order",
        },
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Vector bosons: the tangent Gram matrix of the gauge generators by SM sector.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _adjoint(vector: tuple[int, ...]) -> np.ndarray:
    """ad(Z) on so(10) in the L_ab basis: column A = coordinates of [Z, L_A]."""
    z = sigma_audit._matrix(vector)
    columns = [sigma_audit._matrix_to_vector(z @ elementary - elementary @ z) for elementary in sigma_audit._elementary_matrices()]
    return np.asarray(columns, dtype=np.int64).T


@lru_cache(maxsize=1)
def adjoint_casimirs() -> dict[str, Any]:
    """Exact colour, SU(2)_L and Y^2 Casimirs on the adjoint 45 (normalised on the vector 10)."""
    colour = [tuple(int(value) for value in vector) for vector in sigma_audit.su3_colour_integer_basis()]
    weak = [tuple(int(value) for value in vector) for vector in sigma_audit.SU2L_INTEGER]
    hypercharge = tuple(int(value) for value in sigma_audit.Y_STANDARD_INTEGER)
    matrices = [sigma_audit._matrix(vector) for vector in colour]
    form = [[Fraction(-int(np.trace(left @ right)), 2) for right in matrices] for left in matrices]
    inverse = equality.exact_inverse(form)

    def casimir(rep: Sequence[np.ndarray], size: int) -> list[list[Fraction]]:
        total = [[Fraction(0)] * size for _ in range(size)]
        for i, left in enumerate(rep):
            for j, right in enumerate(rep):
                weight = inverse[i][j]
                if not weight:
                    continue
                product = left @ right
                for row, column in zip(*np.nonzero(product)):
                    total[int(row)][int(column)] -= weight * int(product[row, column])
        return total

    vector_colour = casimir(matrices, 10)
    fundamental = vector_colour[0][0]
    colour_block_scalar = all(
        vector_colour[row][column] == (fundamental if row == column and row < 6 else 0) for row in range(10) for column in range(10)
    )
    normalise = Fraction(4, 3) / fundamental if fundamental else Fraction(0)
    adjoints = [_adjoint(vector) for vector in colour]
    colour_adjoint = [[normalise * value for value in row] for row in casimir(adjoints, 45)]
    weak_adjoint = _sum_fraction_matrices(
        [_fraction_matrix(_adjoint(vector) @ _adjoint(vector), Fraction(-1, 4)) for vector in weak], 45
    )
    y_adjoint = _fraction_matrix(_adjoint(hypercharge) @ _adjoint(hypercharge), Fraction(-1, 36))
    return {
        "colour": colour_adjoint,
        "weak": weak_adjoint,
        "y_squared": y_adjoint,
        "fundamental_raw": fundamental,
        "colour_block_scalar_on_vector": colour_block_scalar,
    }


def _polynomial_terms(expression: Any, *symbols: Any) -> dict[str, str]:
    """Deterministic {"(i, j)": coefficient} form of a polynomial with rational coefficients."""
    polynomial = sympy.Poly(expression, *symbols)
    return {str(tuple(int(power) for power in monomial)): str(coefficient) for monomial, coefficient in sorted(polynomial.terms())}


def _quadratic_roots(a: int, b: int, c: int) -> list[str]:
    """Exact roots of a x^2 + b x + c (a > 0, positive discriminant) as 'p -/+ (s)*sqrt(d)', smaller first."""
    discriminant = b * b - 4 * a * c
    square, free = 1, 1
    for prime, power in sorted(sympy.factorint(discriminant).items()):
        square *= prime ** (power // 2)
        free *= prime ** (power % 2)
    centre = Fraction(-b, 2 * a)
    spread = Fraction(square, 2 * a)
    return ["%s - (%s)*sqrt(%d)" % (centre, spread, free), "%s + (%s)*sqrt(%d)" % (centre, spread, free)]


def vector_boson_section(matrix: np.ndarray) -> dict[str, Any]:
    columns = u_columns(matrix)[:GAUGE_GENERATOR_COUNT]
    gram = [[metric_inner(left, right) for right in columns] for left in columns]
    gram_rank = _rank(gram)
    casimirs = adjoint_casimirs()
    identity = [[Fraction(int(row == column)) for column in range(45)] for row in range(45)]
    sectors = []
    covered = 0
    sector_bases: dict[str, list[list[Fraction]]] = {}
    x_index = SO10_GENERATOR_COUNT
    x_couples_only_to_neutral = True
    scalar_everywhere = True
    for label, (c_colour, c_weak, y_squared), dimension, expected in VECTOR_SECTORS:
        rows = []
        for operator, value in ((casimirs["colour"], c_colour), (casimirs["weak"], c_weak), (casimirs["y_squared"], y_squared)):
            rows += [[operator[i][j] - value * identity[i][j] for j in range(45)] for i in range(45)]
        basis = equality.exact_nullspace(rows, 45)
        sector_bases[label] = basis
        covered += len(basis)
        eigenvalue = None
        scalar = False
        if expected is not None and basis:
            images = [[sum((gram[i][j] * vector[j] for j in range(45) if vector[j]), Fraction(0)) for i in range(45)] for vector in basis]
            pivot = next(j for j in range(45) if basis[0][j])
            eigenvalue = images[0][pivot] / basis[0][pivot]
            scalar = all(image[i] == eigenvalue * vector[i] for image, vector in zip(images, basis) for i in range(45))
            scalar_everywhere &= scalar
            x_couples_only_to_neutral &= all(
                sum((gram[x_index][j] * vector[j] for j in range(45) if vector[j]), Fraction(0)) == 0 for vector in basis
            )
        sectors.append(
            {
                "sector": label,
                "casimirs_colour_weak_Y_squared": [c_colour, c_weak, y_squared],
                "real_dimension": len(basis),
                "expected_real_dimension": dimension,
                "gamma_eigenvalue": eigenvalue,
                "expected_gamma_eigenvalue": expected,
                "gamma_scalar_on_sector": scalar if expected is not None else None,
                "unbroken": expected == 0,
            }
        )
    neutral = sector_bases.get("(1,1)_0", [])
    t, lam = sympy.symbols("t lambda")
    neutral_polynomial = None
    neutral_roots_unit = None
    if len(neutral) == 2:
        basis46 = [list(vector) + [Fraction(0)] for vector in neutral] + [[Fraction(0)] * 45 + [Fraction(1)]]
        scale = [sympy.Integer(1)] * 45 + [t]
        a_matrix = sympy.zeros(3, 3)
        n_matrix = sympy.zeros(3, 3)
        for p, left in enumerate(basis46):
            for q, right in enumerate(basis46):
                a_matrix[p, q] = sum(
                    (sympy.Rational(left[i].numerator, left[i].denominator) * scale[i] * sympy.Rational(gram[i][j].numerator, gram[i][j].denominator)
                     * scale[j] * sympy.Rational(right[j].numerator, right[j].denominator)
                     for i in range(46) if left[i] for j in range(46) if right[j] and gram[i][j]),
                    sympy.Integer(0),
                )
                n_matrix[p, q] = sum(
                    (sympy.Rational(left[i].numerator, left[i].denominator) * sympy.Rational(right[i].numerator, right[i].denominator) for i in range(46) if left[i] and right[i]),
                    sympy.Integer(0),
                )
        # det(lambda N - A)/det(N): the monic characteristic polynomial of the block in an orthonormal basis.
        characteristic = sympy.expand(sympy.cancel((lam * n_matrix - a_matrix).det() / n_matrix.det()))
        quadratic = sympy.expand(125 * lam**2 - (50 + 72450 * t**2) * lam + 28964 * t**2)
        neutral_ok = sympy.expand(125 * characteristic - lam * quadratic) == 0
        neutral_polynomial = _polynomial_terms(characteristic, lam, t)
        neutral_roots_unit = _quadratic_roots(125, -72500, 28964)
    else:
        neutral_ok = False
    dimensions_ok = all(row["real_dimension"] == row["expected_real_dimension"] for row in sectors) and covered == 45
    eigenvalues_ok = all(row["gamma_eigenvalue"] == row["expected_gamma_eigenvalue"] for row in sectors if row["expected_gamma_eigenvalue"] is not None)
    massless = sum(row["real_dimension"] for row in sectors if row["unbroken"]) + (1 if neutral_ok else 0)
    checks = {
        "vector_gram_rank_34": gram_rank == EXPECTED_GAUGE_RANK,
        "colour_casimir_normalised_on_vector_colour_block": casimirs["colour_block_scalar_on_vector"],
        "SM_sectors_decompose_so10_with_expected_dimensions": dimensions_ok,
        "gamma_scalar_on_every_charged_sector_with_expected_value": bool(scalar_everywhere and eigenvalues_ok),
        "X_couples_only_to_the_neutral_sector": x_couples_only_to_neutral,
        "neutral_block_polynomial_exact": bool(neutral_ok),
        "massless_vectors_are_the_12_SM_gauge_bosons": massless == EXPECTED_STABILIZER_DIMENSION,
    }
    characteristic_unit = (
        "lambda^12 (lambda - 1)^12 (lambda - 27/25)^12 (lambda - 2/25)^8 (125 lambda^2 - 72500 lambda + 28964)/125"
    )
    return {
        "definition": "Gamma_AB = <T_A q0, T_B q0> (canonical chart metric) for the 45 so(10) generators L_ab and "
        "U(1)_X; with D_mu = d_mu + g A^A L_A + g_X B Q_X and canonical -(1/4) F^2 terms, M_V^2 = g^2 Gamma on so(10), "
        "g g_X on the mixed and g_X^2 on the X entries (units M_GUT^2); t = g_X/g",
        "gram_rank": gram_rank,
        "sectors": sectors,
        "neutral_block": {
            "basis": "the (1,1)_0 sector of so(10) (Y and the SU(5)-commuting Cartan J) plus X",
            "characteristic_polynomial": "lambda (" + NEUTRAL_POLYNOMIAL + ")/125" if neutral_ok else None,
            "characteristic_polynomial_terms_lambda_t_exponents": neutral_polynomial,
            "roots_at_t_1": neutral_roots_unit,
            "massless_combination": "the hypercharge boson (Y)",
        },
        "characteristic_polynomial_at_unit_couplings": characteristic_unit if all(checks.values()) else None,
        "physical_reading": "(3,2)_-5/6 + conj (SU(5) X/Y bosons): Phi only, Gamma = 1; (3,2)_1/6 + conj: Phi + "
        "Sigma, 1 + 2 r0^2 = 27/25; (3,1)_2/3 + conj and (1,1)_1 + conj: Sigma only, 2 r0^2 = 2/25; neutral Z'/X "
        "mixing from the Sigma, S and Phi17 phases",
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# float64 bindings and corroboration (diagnostics).
# ---------------------------------------------------------------------------


def live_compiler_binding(matrix: np.ndarray) -> dict[str, Any]:
    """D M against the live chart tangents at the candidate state (float64)."""
    state = candidate.candidate_state(R0, X0)
    live = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            superseded._phase_tangent(state, X_CHARGES),
            superseded._phase_tangent(state, PQ_CHARGES),
        )
    )
    scale = hessian.congruence_scale() * np.asarray([float(value) for value in hessian.tangent_row_scale()])
    expected = scale[:, None] * np.asarray(matrix, dtype=float)
    residual = float(np.max(np.abs(live - expected), initial=0.0))
    return {
        "live_sources": [
            "live_g2_canonical_486_field_chart_v20.gauge_orbit_matrix",
            "exact_gauged_u1x_physical_quotient_v20._phase_tangent (U1X and PQ charges)",
            "g3_sm_pati_salam_candidate_v20.candidate_state(r0 = 1/5, x0 = 1)",
        ],
        "row_scaling": "chart = sqrt(2)^[complex] D_u M",
        "live_shape": list(live.shape),
        "maximum_absolute_residual": residual,
        "tolerance": FLOAT_TOLERANCE,
        "compiler_binding_passes": bool(live.shape == (TOTAL_DIM, FULL_GENERATOR_COUNT) and residual <= FLOAT_TOLERANCE),
    }


def float64_corroboration(matrix: np.ndarray, axion: Mapping[int, Fraction]) -> dict[str, Any]:
    """Kinetic normalisation residuals and the restricted spectrum at eps = r0^2/100 (float64 diagnostics)."""
    state = candidate.candidate_state(R0, X0)
    q0 = chart.pack(state)
    scale = hessian.congruence_scale()
    axion_q = np.asarray([float(value) for value in _dense(axion)]) * scale
    rng = np.random.default_rng(RANDOM_SEED)
    random_q = rng.normal(size=TOTAL_DIM)
    residuals = {}
    for name, vector in (("vacuum", q0), ("vacuum_plus_axion", q0 + axion_q), ("random", random_q)):
        value = chart.kinetic_quadratic(chart.unpack(vector))
        residuals[name] = abs(value - chart.coordinate_kinetic_quadratic(vector)) / max(1.0, abs(value))
    basis = chart.sigma_basis()
    gram = np.asarray([[direct.sigma_kinetic_inner(left, right) for right in basis] for left in basis], dtype=complex)
    sigma_residual = float(np.max(np.abs(gram - np.eye(chart.SIGMA_COMPLEX_DIM))))
    tangents_q = scale[:, None] * (np.asarray([float(value) for value in hessian.tangent_row_scale()])[:, None] * np.asarray(matrix, dtype=float))
    gauge_q = tangents_q[:, :GAUGE_GENERATOR_COUNT]
    left, singular, _ = np.linalg.svd(gauge_q, full_matrices=True)
    rank = int(np.sum(singular > 1.0e-9 * singular[0]))
    complement = left[:, rank:]
    numerator, denominator = hessian.exact_hessian("raised_O06")["hessian"]
    hessian_q = hessian.u_to_chart_hessian(hessian.exact_to_float(numerator, denominator))
    eigenvalues = np.linalg.eigvalsh(complement.T @ hessian_q @ complement)
    positive = eigenvalues[eigenvalues > FLOAT_ZERO_EIGENVALUE]
    eps = float(EPS_MEMBERS["raised_O06"])
    second = float(DOUBLET_LIGHTEST_BELOW)
    return {
        "kinetic_relative_residuals": residuals,
        "sigma_basis_orthonormality_residual": sigma_residual,
        "chart_kinetic_metric_identity": bool(max(residuals.values()) < 1.0e-12 and sigma_residual < 1.0e-12),
        "restricted_spectrum_eps_r0sq_over_100": {
            "gauge_rank_float": rank,
            "W_dimension_float": int(complement.shape[1]),
            "negative_below_minus_1e_minus_10": int(np.sum(eigenvalues < -FLOAT_ZERO_EIGENVALUE)),
            "zero_within_1e_minus_10": int(np.sum(np.abs(eigenvalues) <= FLOAT_ZERO_EIGENVALUE)),
            "positive_above_1e_minus_10": int(positive.size),
            "smallest_positive": float(positive[0]) if positive.size else float("nan"),
            "multiplicity_of_eps": int(np.sum(np.abs(eigenvalues - eps) <= 1.0e-10)),
            "multiplicity_of_r0sq_over_96": int(np.sum(np.abs(eigenvalues - second) <= 1.0e-10)),
        },
        "consistent": bool(
            rank == EXPECTED_GAUGE_RANK
            and complement.shape[1] == EXPECTED_GAUGE_QUOTIENT
            and int(np.sum(eigenvalues < -FLOAT_ZERO_EIGENVALUE)) == 0
            and int(np.sum(np.abs(eigenvalues) <= FLOAT_ZERO_EIGENVALUE)) == 1
            and int(positive.size) == EXPECTED_TRANSVERSE_QUOTIENT
            and int(np.sum(np.abs(eigenvalues - eps) <= 1.0e-10)) == LIGHT_DOUBLET_REAL_DIMENSION
            and int(np.sum(np.abs(eigenvalues - second) <= 1.0e-10)) == SECOND_LEVEL_MULTIPLICITY
        ),
    }


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def _inertia_triple(value: Any) -> tuple[int, int, int] | None:
    """(positive, zero, negative) from a 'p/z/n' inertia string, None if it is not one."""
    parts = value.split("/") if isinstance(value, str) else []
    return tuple(int(part) for part in parts) if len(parts) == 3 and all(part.isdigit() for part in parts) else None


def zero_mode_classification(
    gauge: Mapping[str, Any], restricted: Mapping[str, Any], fresh: Mapping[str, Any], *, certified: bool
) -> dict[str, Any]:
    """The classification of every zero and negative mode, stated only when ``certified`` (every gauge-quotient and
    mode check passes); otherwise each claim is None.  The inertias are the fresh exact ones (eps = r0^2/100, which
    with the Hessian report's L2 holds for every eps > 0; and the tuned eps = 0 point)."""
    ranks = gauge["ranks"]
    member = fresh["variants"]["raised_O06"]["inertia_positive_zero_negative"]
    tuned = fresh["variants"]["benchmark"]["inertia_positive_zero_negative"]
    member_triple = _inertia_triple(member)
    tuned_triple = _inertia_triple(tuned)
    certified = bool(certified and member_triple is not None and tuned_triple is not None)

    def claim(value: Any) -> Any:
        return value if certified else None

    eaten = ranks["SO10_x_U1X"]
    axion_count = ranks["SO10_x_U1X_x_PQ"] - eaten
    return {
        "certified": certified,
        "eps_positive": {
            "hessian_inertia_positive_zero_negative": claim(member),
            "negative_modes": claim(member_triple[2] if member_triple else None),
            "zero_modes": claim(member_triple[1] if member_triple else None),
            "eaten_goldstones": claim(
                {
                    "total": eaten,
                    "SO10_over_SM": ranks["SO10"],
                    "U1X": eaten - ranks["SO10"],
                    "span": "G34, the span of the 46 gauge tangents",
                }
            ),
            "physical_axion": claim(axion_count),
            "decomposition": claim("ker Hess = T35 = G34 (+) span(a) orthogonally (canonical chart metric)"),
            "gauge_quotient_W": claim(restricted["eps_positive"]["inertia_on_W_positive_zero_negative"]),
            "massive_transverse_quotient": claim(
                "%d strictly positive (kernel = orbit, Hessian report L2)" % member_triple[0] if member_triple else None
            ),
        },
        "tuned_eps_0": {
            "hessian_inertia_positive_zero_negative": claim(tuned),
            "zero_modes": claim(tuned_triple[1] if tuned_triple else None),
            "decomposition": claim(
                "%d eaten + %d axion + %d real doublet modes Re H_6..9" % (eaten, axion_count, LIGHT_DOUBLET_REAL_DIMENSION)
            ),
            "gauge_quotient_W": claim(restricted["tuned_eps_0"]["inertia_on_W_positive_zero_negative"]),
        },
        "unexplained_zero_or_negative_modes": claim(0),
    }


def g4_scope_coverage(ok_sections: Mapping[str, bool]) -> list[dict[str, Any]]:
    return [
        {
            "item": G4_OPEN_SCOPE[0],
            "certified_by": ["gauge_quotient", "live_compiler_binding"],
            "content_certified": ok_sections["gauge_quotient"],
        },
        {
            "item": G4_OPEN_SCOPE[1],
            "certified_by": ["restricted_hessian", "axion", "fresh_exact_hessians", "light_doublet", "zero_mode_classification"],
            "content_certified": ok_sections["modes"],
        },
        {
            "item": G4_OPEN_SCOPE[2],
            "certified_by": ["gauge_quotient", "axion", "light_doublet", "zero_mode_classification"],
            "content_certified": ok_sections["gauge_quotient"] and ok_sections["modes"],
            "resolved": False,
            "resolution": "the caveat is resolved only when G4 is CLOSED; this report does not wire G4 (under decision "
            "D3 a CLOSED G4 approves the internal candidate, so wiring G4 is the user's decision)",
        },
    ]


def build_report(
    *,
    hessian_report: Mapping[str, Any] | None = None,
    equality_report: Mapping[str, Any] | None = None,
    candidate_report: Mapping[str, Any] | None = None,
    sigma_audit_report: Mapping[str, Any] | None = None,
    contract_report: Mapping[str, Any] | None = None,
    tangent_override: np.ndarray | None = None,
    pq_charges: Mapping[str, int] | None = None,
    doublet_indices: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Build the fail-closed G4 certificate.  Every keyword exists for mutation tests only: the committed
    reports, the integer tangent matrix, the PQ charges and the doublet directions replace the module's own."""
    started = time.time()
    reports = {
        "hessian": load_report(hessian.OUT_JSON) if hessian_report is None else hessian_report,
        "equality": load_report(equality.OUT_JSON) if equality_report is None else equality_report,
        "candidate": load_report(candidate.OUT_JSON) if candidate_report is None else candidate_report,
        "sigma_audit": load_report(sigma_audit.OUT_JSON) if sigma_audit_report is None else sigma_audit_report,
        "contract": load_report(CONTRACT_JSON) if contract_report is None else contract_report,
    }
    premises = {
        "hessian": hessian_premises(reports["hessian"]),
        "equality": equality_premises(reports["equality"]),
        "candidate": candidate_premises(reports["candidate"]),
        "sigma_audit": sigma_audit_premises(reports["sigma_audit"]),
        "contract": contract_premises(reports["contract"]),
    }
    charges_pq = dict(PQ_CHARGES) if pq_charges is None else {key: int(value) for key, value in pq_charges.items()}
    matrix = tangent_matrix(matrix=tangent_override, pq_charges=None if pq_charges is None else charges_pq)
    doublet = tuple(DOUBLET_REAL_X) if doublet_indices is None else tuple(int(index) for index in doublet_indices)

    gauge = gauge_quotient_section(matrix, premises["contract"])
    gauge_pivots = [GENERATOR_LABELS.index(label) for label in gauge["certificates"]["SO10_x_U1X"]["minor"]["column_generator_labels"]]
    normalisation = chart_normalisation_section(matrix)
    axion = axion_section(matrix, gauge_pivots, X_CHARGES, charges_pq)
    axion_vector = axion.pop("_axion")
    fresh = fresh_hessian_section(matrix, axion_vector, doublet)
    restricted = restricted_hessian_section(gauge, axion, fresh, premises["hessian"], matrix, doublet)
    light = doublet_section(doublet, fresh, premises["hessian"], premises["candidate"], premises["sigma_audit"])
    vectors = vector_boson_section(matrix)
    binding = live_compiler_binding(matrix)
    corroboration = float64_corroboration(matrix, axion_vector)

    checks: dict[str, bool] = {}
    for name, rows in premises.items():
        checks[f"premise_{name}_report"] = bool(rows) and all(rows.values())
    for prefix, section in (
        ("gauge", gauge),
        ("chart", normalisation),
        ("axion", axion),
        ("fresh", fresh),
        ("restricted", restricted),
        ("doublet", light),
        ("vectors", vectors),
    ):
        checks.update({f"{prefix}__{key}": bool(value) for key, value in section["checks"].items()})
    checks["binding__live_compiler_tangents_equal_D_M_float64"] = binding["compiler_binding_passes"]
    checks["binding__float64_restricted_spectrum_and_kinetic_metric_consistent"] = bool(
        corroboration["consistent"] and corroboration["chart_kinetic_metric_identity"]
    )
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures

    gauge_ok = all(value for key, value in checks.items() if key.startswith(("gauge__", "premise_contract", "premise_equality", "binding__live")))
    modes_ok = all(
        value
        for key, value in checks.items()
        if key.startswith(("axion__", "fresh__", "restricted__", "doublet__", "chart__", "premise_hessian", "premise_candidate", "premise_sigma"))
    )
    classification = zero_mode_classification(gauge, restricted, fresh, certified=bool(gauge_ok and modes_ok))
    flags = {
        "certificate_passes": ok,
        "gauge_ranks_33_34_35_exact": ok,
        "gauge_quotient_452_and_transverse_quotient_451_exact": ok,
        "PQ_global_not_gauged_not_eaten": ok,
        "physical_axion_identified_exact": ok,
        "restricted_hessian_psd_single_zero_mode_axion": ok,
        "no_negative_modes": ok,
        "zero_modes_35_equal_34_eaten_plus_axion": ok,
        "tuned_limit_doublet_is_SM_doublet_lifted_at_quartic_order": ok,
        "vector_boson_gram_by_SM_sector_exact": ok,
        "compiler_binding_float64_only": True,
        "G4_closed": False,
        "G4_wired_into_gate_ledger": False,
        "report_closes_g4_by_itself": False,
        "gate_status_changed": False,
        "internal_candidate_approved": False,
    }
    report = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_CERTIFIED if ok else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_CERTIFIED if ok else OVERALL_STATE_OPEN,
        "theorem_claimed": ok,
        "theorem": THEOREM if ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "witness": {
            "potential": "V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps), the other 26 benchmark couplings unchanged",
            "r0": R0,
            "x0": X0,
            "kappa": KAPPA,
            "eps_window": {"lower_exclusive": "0", "upper_exclusive": str(EPS_WINDOW_UPPER)},
            "vacuum": "q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0), independent of eps",
            "fresh_exact_members": {name: value for name, value in EPS_MEMBERS.items()},
        },
        "premises": premises,
        "chart_normalisation": normalisation,
        "gauge_quotient": gauge,
        "axion": axion,
        "fresh_exact_hessians": fresh,
        "restricted_hessian": restricted,
        "zero_mode_classification": classification,
        "light_doublet": light,
        "vector_bosons": vectors,
        "live_compiler_binding": binding,
        "float64_corroboration": corroboration,
        "g4_open_scope_coverage": g4_scope_coverage({"gauge_quotient": gauge_ok, "modes": modes_ok}),
        "roadmap_W3_G4_acceptance": {
            "text": W3_G4_ACCEPTANCE,
            "ranks_compiler_bound": bool(checks["binding__live_compiler_tangents_equal_D_M_float64"] and gauge_ok),
            "no_unexplained_zero_or_negative_modes": bool(modes_ok),
            "binding_note": "compiler-bound in float64 (entrywise D M vs the live chart tangents); the exact ranks "
            "are integer certificates",
        },
        "final_acceptance_test": {
            "gate": "G4",
            "required_statement": G4_REQUIRED_STATEMENT,
            "currently_passes": ok,
            "status": STATUS_CERTIFIED if ok else STATUS_INCOMPLETE,
            "witness": "V_PS,eps at r0 = 1/5, x0 = 1, kappa = -r0/4, 0 < eps < 599/50 (the G3 witness, decision D2)",
            "evidence": [
                "gauge_quotient: integer minors 1/4/-68 and 12 independent integer null vectors (standard SM algebra, "
                "no X/PQ coefficient) for SO(10), SO(10)xU(1)_X, SO(10)xU(1)_XxPQ",
                "axion: exact orthogonal projection of the PQ tangent in the canonical metric, T35 cap G34^perp = span(a)",
                "restricted_hessian: PSD with kernel T35 for every eps > 0 (Hessian report L2; fresh exact 451/35/0 at "
                "eps = r0^2/100, r0^2/10^6) gives inertia 451/1/0 on the 452-dimensional gauge quotient",
                "light_doublet: exact SM label (1,2)_{1/2}, mass^2 eps, quartic lift 127/64 at eps = 0",
            ],
            "wired_into_gate_ledger": False,
            "closes_g4_by_itself": False,
            "wiring_decision": "left to the user: under decision D3 a CLOSED G4 approves the internal candidate, so "
            "this report does not wire G4 and the ledger keeps G4 OPEN",
        },
        "scope": {
            "proved_exactly": [
                "the orbit tangent ranks 33/34/35 at q0 (both halves of the rank certificate, for all r0, x0 > 0 since "
                "D is invertible), the gauge quotient 452 and the massive/transverse quotient 451",
                "the physical axion a = t_PQ - proj_G34 t_PQ, |a|^2 = 9248/7241 and its squared-norm composition, and "
                "the axion-angle period 2 pi/68 modulo SO(10) x U(1)_X (v_a = F_PQ/68, v_a^2 = 2/7241), at r0 = 1/5, "
                "x0 = 1",
                "the Hessian of V_PS,eps restricted to the gauge quotient: PSD, one zero mode (a), 451 positive modes "
                "equal to the positive spectrum of the Hessian, for every eps in the window (inputs: the Hessian "
                "report's L2 plus fresh exact certificates at eps = r0^2/100 and r0^2/10^6)",
                "the zero-mode classification 35 = 34 eaten (33 + 1) + 1 axion, no negative mode; at eps = 0 the 4 "
                "extra modes Re H_6..9 form one SM doublet (1,2)_{1/2}",
                "the vector-boson tangent Gram matrix: rank 34 and its eigenvalues by SM sector",
            ],
            "bound_from_committed_reports": [
                "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (eps family L1/L2, doublet section, tuned 447/39)",
                "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (tangent ranks, charges, PQ status)",
                "G3_SM_PATI_SALAM_CANDIDATE_V20.json (lambda_eff = 127/64, SM vacuum)",
                "G3_SIGMA_HYPERCHARGE_AUDIT_V20.json (standard SM pair (p, z1..z5), weak-block |Y| = 1/2)",
                "GAUGED_U1X_SCALAR_CONTRACT_V20.json (gauge SO(10) x U(1)_X, accidental global U(1)_PQ)",
            ],
            "float64_evidence_only": [
                "the compiler = exact-operator identity of the Hessian end to end (inherited from the exact Hessian "
                "report: per-unit and assembled float64 bindings)",
                "the entrywise binding of D M to the live chart tangents",
                "the chart kinetic normalisation residuals and the float64 restricted spectrum",
            ],
            "not_covered": [
                "the physical hierarchy point (r0 = M_I/M_GUT, canonical Phi17 scale x0 ~ 10.08): only r0 = 1/5, x0 = 1 "
                "is certified",
                "loop corrections (Coleman-Weinberg, running), the axion's QCD anomaly mass and the conversion of v_a "
                "to the conventional f_a = v_a/N_DW (fermion PQ charges and the domain-wall number are not computed)",
                "PQ-violating non-renormalizable operators (e.g. the dimension-21 axion-quality term "
                "Phi17^4 conj(S)^17 / M_Pl^17, SO(10) x U(1)_X-invariant with PQ charge -68), which lift the axion "
                "explicitly; the axion zero mode is exact for the renormalizable PQ-neutral benchmark potential only",
                "the G6 positivity/EWSB caveats: H = 0 on the witness, no electroweak breaking, sub-M_I coloured "
                "126bar states; the complete positive spectrum with SM provenance is a G6 task",
                "gauge coupling values: the vector-boson matrix is given up to g and g_X",
                "wiring G4 into the gate ledger (under decision D3 a CLOSED G4 approves the internal candidate, so "
                "wiring is the user's decision)",
            ],
        },
        "G4_closed": False,
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the G4 physical-quotient certificate is NOT claimed (failed: " + ", ".join(report["failures"])
            + ").  G4 stays OPEN."
        )
    axion = report["axion"]
    return (
        "Exact over Q at the G3 witness V_PS,eps (0 < eps < 599/50, r0 = 1/5, x0 = 1, kappa = -r0/4): the orbit "
        "tangent ranks are 33 (SO(10)), 34 (SO(10) x U(1)_X) and 35 (+ PQ), with nonzero integer minors 1, 4, -68 and "
        "12 independent integer null vectors spanning the standard SM algebra; the gauge quotient has dimension 452 "
        "(axion included) and the massive/transverse quotient 451.  PQ is global.  The physical axion is the PQ "
        f"tangent's component orthogonal to the gauge tangents, |a|^2 = {axion['axion_norm_squared']} (S phase "
        f"{axion['composition']['S_phase']}, Phi17 phase {axion['composition']['Phi17_phase']}, Sigma phase "
        f"{axion['composition']['Sigma_phase']}).  On the 452-dimensional gauge quotient the Hessian is PSD with the "
        "axion as its only zero mode and 451 positive modes (the positive spectrum of the Hessian, lowest eps with "
        "multiplicity 4 for eps < r0^2/96); the 35 zero modes of the full Hessian are 34 eaten Goldstones (33 + 1) "
        "and the axion, and no mode is negative.  At eps = 0 the 4 extra zero modes are one SM doublet (1,2)_{1/2}, "
        "lifted at quartic order by lambda_eff = 127/64.  The vector-boson Gram matrix has rank 34.  Compiler "
        "binding is float64.  G4 is NOT wired: the ledger keeps G4 OPEN (under decision D3 a CLOSED G4 approves the "
        "internal candidate, so wiring G4 is the user's decision)."
    )


def report_passes(report: Mapping[str, Any]) -> bool:
    return bool(
        report.get("n_failed") == 0
        and report.get("status") == STATUS_CERTIFIED
        and _get(report, "final_acceptance_test", "currently_passes") is True
    )


def _markdown(report: Mapping[str, Any]) -> str:
    gauge = report["gauge_quotient"]
    axion = report["axion"]
    restricted = report["restricted_hessian"]
    light = report["light_doublet"]
    vectors = report["vector_bosons"]
    fresh = report["fresh_exact_hessians"]
    levels = restricted["eps_positive"]["lowest_levels_for_eps_below_r0sq_over_96"]
    second = str(DOUBLET_LIGHTEST_BELOW)
    element = axion["decay_constant"]["period_certificate"]["explicit_gauge_element_units_of_2pi"]
    element_text = ", ".join(f"{key} `{value}`" for key, value in sorted(element.items())) if element else "`None`"
    lines = [
        "# G4 at the G3 witness: gauge quotient, axion and physical Hessian -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Theorem claimed:** `{report['theorem_claimed']}` ({report['n_checks'] - report['n_failed']}/"
        f"{report['n_checks']} checks)",
        "",
        report["theorem"],
        "",
        report["verdict"],
        "",
        "## Gauge quotient (exact rank certificate)",
        "",
        "| generators | rank | minor | det M-minor | det D_u M-minor | null vectors (rank) | no X/PQ coefficient |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, cert in gauge["certificates"].items():
        lines.append(
            f"| {name} | `{cert['rank']}` | `{cert['minor']['shape'][0]}x{cert['minor']['shape'][1]}` | "
            f"`{cert['minor']['determinant_integer_M']}` | `{cert['minor']['determinant_D_u_M']}` | "
            f"`{cert['null_vector_count']}` (`{cert['null_vector_rank']}`) | "
            f"`{cert['null_vectors_without_X_or_PQ_coefficient']}` |"
        )
    lines += [
        "",
        f"- stabilizer = standard SM algebra: `{gauge['stabilizer']['equals_standard_SM_algebra']}`;",
        f"- U(1)_X/PQ minor on (S.y, Phi17.y): `{gauge['U1X_PQ_independence']['minor']}`, det "
        f"`{gauge['U1X_PQ_independence']['determinant']}`;",
        f"- gauge quotient (axion included): `{gauge['gauge_quotient_dimension_including_axion']}`; "
        f"massive/transverse quotient: `{gauge['massive_transverse_quotient_dimension']}` (superseded point: "
        f"`{gauge['superseded_point_values']['gauge_quotient']}`/`{gauge['superseded_point_values']['transverse_quotient']}`);",
        f"- eaten Goldstones: `{gauge['eaten_goldstones']['total']}` = `{gauge['eaten_goldstones']['SO10_over_SM']}` "
        f"SO(10)/SM + `{gauge['eaten_goldstones']['U1X']}` U(1)_X; PQ gauged: `{gauge['PQ']['gauged']}`, eaten: "
        f"`{gauge['PQ']['eaten']}`;",
        f"- live compiler binding (float64, max residual): `{report['live_compiler_binding']['maximum_absolute_residual']}`.",
        "",
        "## Physical axion",
        "",
        f"- |a|^2 = `{axion['axion_norm_squared']}` M_GUT^2 (closed form `{axion['axion_norm_squared_closed_form_value']}`); "
        f"|t_PQ|^2 = `{axion['PQ_tangent_norm_squared']}`;",
        "- squared-norm composition: " + ", ".join(f"{key} `{value}`" for key, value in axion["composition"].items()) + ";",
        "- chart components: " + ", ".join(f"{key} = `{value}`" for key, value in axion["axion_chart_components"].items()) + ";",
        f"- projection coefficients: " + ", ".join(f"{key} `{value}`" for key, value in axion["projection_coefficients"].items()) + ";",
        f"- axion-angle period modulo SO(10) x U(1)_X: `{axion['decay_constant']['axion_angle_period_modulo_gauge']}` "
        f"(explicit gauge element, angles in units of 2 pi: {element_text}); "
        f"v_a^2 = `{axion['decay_constant']['v_a_squared']}` M_GUT^2 (v_a = F_PQ/68);",
        f"- convention: {axion['decay_constant']['convention']}.",
        "",
        "## Hessian on the gauge quotient",
        "",
        "- dimensions: " + ", ".join(f"{key} `{value}`" for key, value in restricted["dimensions"].items()) + ";",
        f"- eps > 0: inertia on W `{restricted['eps_positive']['inertia_on_W_positive_zero_negative']}`, zero mode: "
        f"{restricted['eps_positive']['zero_mode']}; for 0 < eps < r0^2/96 the positive levels are eps "
        f"(x`{levels['eps']}`), {second} (x`{levels[second]}`) and `{levels['above_' + second]}` above "
        f"(holds: `{levels['holds']}`);",
        f"- eps = 0: inertia on W `{restricted['tuned_eps_0']['inertia_on_W_positive_zero_negative']}` ({restricted['tuned_eps_0']['zero_modes']});",
        f"- lemma: {restricted['lemma']}",
        "",
        "| fresh exact member | eps | inertia (+/0/-) | kernel as expected | H_u a = 0 | H_u D4 = 2 eps D4 | smallest nonzero (mult.) |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, row in fresh["variants"].items():
        lines.append(
            f"| {name} | `{row['eps']}` | `{row['inertia_positive_zero_negative']}` | `{row['kernel_equals_expected_span']}` | "
            f"`{row['H_u_annihilates_axion']}` | `{row['H_u_doublet_equals_2_eps_doublet']}` | "
            f"`{row['smallest_nonzero_eigenvalue']}` (`{row['smallest_nonzero_multiplicity']}`) |"
        )
    classification = report["zero_mode_classification"]
    eps_modes = classification["eps_positive"]
    eaten = eps_modes["eaten_goldstones"] or {}
    lines += [
        "",
        "## Zero and negative modes",
        "",
        f"- certified: `{classification['certified']}`; unexplained zero or negative modes: "
        f"`{classification['unexplained_zero_or_negative_modes']}`;",
        f"- eps > 0: `{eps_modes['hessian_inertia_positive_zero_negative']}`; "
        f"{eps_modes['decomposition']}; eaten {eaten.get('total')} ({eaten.get('SO10_over_SM')} + {eaten.get('U1X')}), "
        f"axion {eps_modes['physical_axion']}, negative {eps_modes['negative_modes']};",
        f"- eps = 0: `{classification['tuned_eps_0']['hessian_inertia_positive_zero_negative']}`; "
        f"{classification['tuned_eps_0']['decomposition']}.",
        "",
        "## Light doublet (eps -> 0)",
        "",
        "- directions: " + ", ".join(f"`{name}`" for name in light["directions"]["names"]) + " (Re H_6..9);",
        f"- SM label: `{light['SM_label']}` (SU(2)_L Casimir `{light['exact_values']['SU2L_casimir']}`, Y^2 "
        f"`{light['exact_values']['Y_squared']}`, colour singlet `{light['exact_values']['colour_generators_vanish']}`);",
        f"- mass^2: {light['mass_squared']['value']}; lightest with multiplicity 4 for {light['mass_squared']['lightest_level_multiplicity_4_for']};",
        f"- quartic lift at eps = 0: lambda_eff = `{light['tuned_limit']['quartic_lift_lambda_eff']}` ({light['tuned_limit']['lambda_eff_formula']}).",
        "",
        "## Vector bosons (tangent Gram matrix, up to couplings)",
        "",
        f"- rank `{vectors['gram_rank']}`; characteristic polynomial at unit couplings: "
        f"`{vectors['characteristic_polynomial_at_unit_couplings']}`;",
        f"- neutral block (1,1)_0 (+) X (t = g_X/g): `{vectors['neutral_block']['characteristic_polynomial']}`; "
        "roots at t = 1: " + ", ".join(f"`{root}`" for root in vectors["neutral_block"]["roots_at_t_1"] or []) + ";",
        "",
        "| sector | real dim | Gamma eigenvalue |",
        "|---|---|---|",
    ]
    for row in vectors["sectors"]:
        value = row["gamma_eigenvalue"] if row["gamma_eigenvalue"] is not None else "neutral block"
        lines.append(f"| {row['sector']} | `{row['real_dimension']}` | `{value}` |")
    final = report["final_acceptance_test"]
    lines += [
        "",
        "## Final acceptance test (G4, not wired)",
        "",
        f"**Required statement:** {final['required_statement']}",
        "",
        f"**Currently passes:** `{final['currently_passes']}`; wired into the gate ledger: "
        f"`{final['wired_into_gate_ledger']}`; closes G4 by itself: `{final['closes_g4_by_itself']}`.",
        "",
        "Wiring: " + final["wiring_decision"] + ".",
        "",
        "## G4 open-scope coverage",
        "",
    ]
    for row in report["g4_open_scope_coverage"]:
        lines.append(f"- `{row['content_certified']}`: {row['item']}")
    lines += ["", "## Checks", "", "| check | passed |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
    lines += ["", "## Scope", ""]
    for key in ("proved_exactly", "bound_from_committed_reports", "float64_evidence_only", "not_covered"):
        rows = report["scope"][key]
        lines.append(f"**{key}**")
        lines.append("")
        lines += [f"- {row}" for row in rows]
        lines.append("")
    lines.append(f"Runtime: {report['runtime_seconds']:.0f} s.")
    return "\n".join(lines) + "\n"


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n"


def write_report(report: Mapping[str, Any], *, out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> None:
    Path(out_json).write_text(render_json(report), encoding="utf-8")
    Path(out_md).write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if report_passes(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
