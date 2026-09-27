#!/usr/bin/env python3
"""Decoupled-singlet family of the G3 SM Pati-Salam witness: exact, status-neutral certificate (v20).

Decision D-A decouples the singlet scale |S| = rS from the 126bar scale r0 inside the declared 51-parameter
exact-X contract.  The committed 27-parameter SM Pati-Salam map (g3_sm_pati_salam_candidate_v20) then changes in
exactly two entries,

    O04: -2 r0^2 -> -2 rS^2,        O06: 2|kappa| r0 + eps -> 2|kappa| rS + eps,

with re::O12 = kappa, kappa^2 < 8 rS^2 (sharp, see below) and every S portal (O22, O26, O34, O38, O43, im::O12)
still 0.  The vacuum is q0 = (p, 0, r0 sigma_std, rS, x0), V0 = -1 - r0^4/8 - rS^4 - x0^4/32 and lambda_eff =
2 - kappa^2/(4 rS^2).  rS = r0, kappa = -r0/4 is the committed witness.

What is certified here, exactly (77 checks):

* the coefficient map (symbolic in r0, rS, x0, kappa, eps): only O04 and O06 change, 27 parameters inside the
  contract, no S portal, V0 and lambda_eff in closed form;
* the eight-term SOS identity with T6 at rS and T9 = eps N_H, operator by operator for kappa < 0, > 0 and = 0,
  and the sharpness of kappa^2 < 8 rS^2: V >= V0 fails for every kappa^2 > 8 rS^2 (exact identity along
  H = h e_6, S = rS + t, h^2 = |kappa| t/2, with exact rational violating points), while at kappa^2 = 8 rS^2 the
  bound and the equality set still hold (lambda_eff = 0; exact completed square); the certified domain is the open
  kappa^2 < 8 rS^2;
* P3 of the equality-set theorem at rS (g3_sm_pati_salam_equality_set_v20.p3_section with (r0, kappa, rS) points)
  and the committed equality-set premises for the rS-free parts P1/P2;
* the exact 486 x 486 Hessian over Q (g3_sm_pati_salam_exact_hessian_v20 with its ``point`` keyword) at
  (r0, rS, x0, kappa) = (1/5, 1/5, 1, -1/20), (1/5, 1, 1, -1/100), (1/5, 1, 1, -1/4), (1/5, 5, 1, -5/4):
  zero gradient, inertia 447/39/0 at eps = 0 (kernel T35 + 4 doublet directions) and 451/35/0 at eps = r0^2/100,
  r0^2/10^6 (kernel T35), gaps r0^2/96 (x14) and eps (x4), H and S blocks in closed form, and the rS = r0 point
  bit-identical to the committed witness Hessian.  The rS = 5 point is a stress point outside the |c| < 12
  perturbative box (|O04| = 50, O06 = 25/2; its eps window 12 - 2|kappa| rS = -1/2 is empty): an exact member of
  the vacuum family, not a perturbative one;
* the orbit tangent ranks 33/34/35 with the SM stabilizer at rS in {1/10, 1/5, 1, 2}, and the G4 axion and vector
  sections at rS in {1/10, 1/5, 1, 2, 5}: F_PQ^2 = 9248 rS^2 x0^2/(16 rS^2 + 289 x0^2), S share
  289 x0^2/(16 rS^2 + 289 x0^2), Phi17 share 16 rS^2/(...), no Sigma share (route B: exact Gram projection; route A:
  symbolic for all rS);
* the model-file anomaly (models/SO10Z17AxionV20.m, with its declared SO(10) representations checked: nine
  16/16bar fermion fields, scalars 210, 126bar, 10, 1, 1): N_X = 0, N_PQ = -34, E/N = 8/3, N_DW = 1 modulo gauge (axion period
  2 pi/68), with the (13, -3) string caveat.

The check count is pinned: with the default point sets a report whose check count differs from EXPECTED_N_CHECKS
fails closed and is not written.

FLOAT64 corroboration (8 checks outside the exact count, --write only): the live compiler Hessian at
(1/5, 1, 1, -1/100) against the exact one, a compiler point audit at the hierarchy anchor with rS = 1000 r0
(r0 = M_I/M_GUT ~ 6.4e-5, so rS ~ 0.064; tolerances 1e-12 max(1, |V0|) and 1e-12 max(1, 4 rS^3), i.e. 1e-12 at this
anchor), the violating direction, and fast-evaluator endpoints on the orbit.

Status neutrality: this report certifies the vacuum family only.  It chooses no benchmark, closes nothing and
changes no gate: the committed rS = r0 witness remains the closing instance of G3 and G4.  The physics viability of
decoupling (y_s <= ~0.35, the reduced-Planck Landau criterion, a v_R/f_a/m_a benchmark) is open research pending
the user's decisions, and m_a = 153.5 ueV is not a prediction of the family.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import time
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy

import exact_gauged_u1x_physical_quotient_v20 as quotient
import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g4_sm_pati_salam_physical_quotient_v20 as g4
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
MODULE = "g3_sm_pati_salam_decoupled_singlet_family_v20"
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_V20.md"
MODEL_FILE = ROOT / "models" / "SO10Z17AxionV20.m"

STATUS_CERTIFIED = "SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_EXACT__STATUS_NEUTRAL"
STATUS_INCOMPLETE = "SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_INCOMPLETE__STATUS_NEUTRAL"
OVERALL_STATE_CERTIFIED = "EXACT_VACUUM_FAMILY_WITH_R_S_INDEPENDENT_OF_R0__NO_BENCHMARK__NO_GATE_CHANGE"
OVERALL_STATE_OPEN = "DECOUPLED_SINGLET_FAMILY_NOT_CERTIFIED__NO_GATE_CHANGE"
MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
EXPECTED_N_CHECKS = 77  # default point sets only (enforced by build_report and report_passes)
CHECK_COUNT_FAILURE = "check_count_equals_EXPECTED_N_CHECKS_with_default_point_sets"
EXPECTED_N_FLOAT_CHECKS = 8

R0, X0 = Fraction(1, 5), Fraction(1)
P = hessian.SingletPoint
HESSIAN_POINTS = (
    ("rS_eq_r0_witness", P(R0, R0, X0, Fraction(-1, 20))),
    ("rS_1_kappa_minus_r0sq_over_4rS", P(R0, Fraction(1), X0, Fraction(-1, 100))),
    ("rS_1_kappa_minus_rS_over_4", P(R0, Fraction(1), X0, Fraction(-1, 4))),
    ("rS_5_kappa_minus_rS_over_4_stress", P(R0, Fraction(5), X0, Fraction(-5, 4))),
)
KEEPS_H_BLOCK_LABEL = "rS_1_kappa_minus_r0sq_over_4rS"
RANK_RS = (Fraction(1, 10), Fraction(1, 5), Fraction(1), Fraction(2))
G4_RS = RANK_RS + (Fraction(5),)
# (r0, kappa, rS): the Hessian points, kappa = -r0^2/(4 rS) at every rank rS, and one point just inside the boundary.
HS_POINTS = (
    [(p.r0, p.kappa, p.rs) for _, p in HESSIAN_POINTS]
    + [(R0, -R0 * R0 / (4 * rs), rs) for rs in RANK_RS]
    + [(R0, Fraction(-707, 250), Fraction(1))]
)
# (rS, kappa, t) beyond the boundary kappa^2 = 8 rS^2: V_HS + rS^4 = t^2 [(2 rS + t)^2 - kappa^2/2] < 0.
SHARPNESS_WITNESSES = (
    (Fraction(1), Fraction(-3), Fraction(3, 100)),
    (Fraction(1), Fraction(-2829, 1000), Fraction(1, 10**4)),
)
SHARPNESS_VALUES = (Fraction(-34119, 10**8), Fraction(-122049, 10**16))
S_PORTAL_IDS = (
    "lambda::O22_B01_singlet_polynomial",
    "lambda::O26_B01_126bar_norm",
    "lambda::O34_B01_Hdag_H_norm",
    "re::O38_B01_Phi_Hdag_Sigmadag",
    "im::O38_B01_Phi_Hdag_Sigmadag",
    "lambda::O43_B01_Phi_norm",
    "im::O12_B01_Hdag_Hdag_pair",
)
MODEL_SCALAR_NAMES = {"Phi210": "Phi210", "Delta126bar": "Sigma126bar", "H10": "H10", "S": "S", "Phi17": "Phi17"}
# Declared SO(10) representations (the model file's dimension column; negative = conjugate).  The anomaly indices
# below (T_SU3 = 2, Tr Q^2 = 16/3) are those of a 16 or 16bar, so every fermion must be one.
MODEL_SCALAR_REPS = {"Phi210": 210, "Delta126bar": -126, "H10": 10, "S": 1, "Phi17": 1}
MODEL_FERMION_ABS_REP = 16
# The SM content of one 16 (Q = T3 + Y): name, colour dimension, SU(2)_L dimension, hypercharge.
SIXTEEN_SM_CONTENT = (
    ("Q", 3, 2, Fraction(1, 6)),
    ("u^c", 3, 1, Fraction(-2, 3)),
    ("d^c", 3, 1, Fraction(1, 3)),
    ("L", 1, 2, Fraction(-1, 2)),
    ("e^c", 1, 1, Fraction(1)),
    ("nu^c", 1, 1, Fraction(0)),
)
NEVER_TRUE_FLAGS = (
    "benchmark_chosen",
    "gate_status_changed",
    "report_closes_g3_by_itself",
    "report_closes_g4_by_itself",
    "G3_witness_replaced",
    "wired_into_gate_ledger",
    "decoupling_physically_viable_established",
    "m_a_153_5_ueV_predicted",
)
VARIANTS = ("benchmark", "raised_O06", "tiny_eps")
LIFTED = ("raised_O06", "tiny_eps")
O04, O06, O12 = candidate.O04_ID, candidate.O06_ID, candidate.O12_ID
BLOCK_NAMES = (
    ("Phi", chart.PHI_SLICE),
    ("H", chart.H_SLICE),
    ("Sigma", chart.SIGMA_SLICE),
    ("S", chart.S_SLICE),
    ("Phi17", chart.X_SLICE),
)
EXPECTED_CHARGED_VECTOR_GAMMA = {
    "(8,1)_0": Fraction(0),
    "(1,3)_0": Fraction(0),
    "(3,2)_-5/6 + conj": Fraction(1),
    "(3,2)_1/6 + conj": Fraction(27, 25),
    "(3,1)_2/3 + conj": Fraction(2, 25),
    "(1,1)_1 + conj": Fraction(2, 25),
}
RS_INDEPENDENT_AXION_CHECKS = (
    "gauge_gram_on_34_pivot_tangents_nonsingular",
    "axion_orthogonal_to_all_46_gauge_tangents_exact",
    "axion_nonzero",
    "axion_lies_in_orbit_tangent_span_T35",
    "axion_not_in_gauge_span",
    "T35_cap_gauge_complement_is_one_dimensional",
    "axion_is_pure_S_and_Phi17_phase",
    "axion_norm_squared_matches_closed_form",
)
RS_INDEPENDENT_VECTOR_CHECKS = (
    "vector_gram_rank_34",
    "colour_casimir_normalised_on_vector_colour_block",
    "SM_sectors_decompose_so10_with_expected_dimensions",
    "gamma_scalar_on_every_charged_sector_with_expected_value",
    "X_couples_only_to_the_neutral_sector",
)
FLOAT_TOLERANCE = 1.0e-12
# F2 at the hierarchy anchor rS = 1000 r0 (r0 = M_I/M_GUT ~ 6.4e-5, so rS ~ 0.064): |V0| ~ 1.03 and the S-block
# gradient terms ~ 4 rS^3 ~ 1e-3, so the tolerances FLOAT_TOLERANCE * max(1, scale) equal 1e-12 there; the scale
# factors keep the check meaningful (not sub-ulp) if the anchor ratio ever gives rS > 1 (recorded in the F2 record).
FLOAT_SEED = 20260926
FLOAT_CHECK_NAMES = (
    "float_F1_live_compiler_hessian_and_gradient_match_exact_within_1e_minus_12",
    "float_F1_live_lattice_and_V_minus_V0",
    "float_F2_anchor_gradient_and_V_minus_V0",
    "float_F2_anchor_ranks_33_34_35_and_projected_inertia_0_4",
    "float_F2_anchor_lightest_massive_r0sq_over_96_and_eps_variant",
    "float_F3_violating_direction_matches_exact",
    "float_F4_fast_evaluator_matches_compiler",
    "float_F4_converged_endpoints_on_orbit",
)

PHYSICS_STATUS = {
    "certifies": "the tree-level vacuum family only: the committed 27-parameter SM Pati-Salam map with |S| = rS "
    "independent of r0 (O04 = -2 rS^2, O06 = 2|kappa| rS + eps)",
    "does_not_choose_a_benchmark": "this report does NOT choose a benchmark: its (r0, rS, kappa) points are "
    "certificate points, not benchmarks",
    "does_not_change_G3_or_G4": "this report does NOT change G3 or G4 closure: the committed rS = r0 witness (r0 = "
    "1/5, x0 = 1, kappa = -r0/4, 0 < eps < 599/50) remains the closing instance; no gate status, ledger entry or "
    "roadmap text changes",
    "open_research": "the physics viability of decoupling (y_s <= ~0.35 from two-loop running, the reduced-Planck "
    "Landau/perturbativity criterion, and a v_R / f_a / m_a benchmark such as BM-DA1) is open research pending "
    "user decisions DA', (d) and the kappa placement",
    "axion_mass": "m_a = 153.5 ueV is not a prediction of the family: f_a = v_S v_Phi/sqrt((4 v_S)^2 + (17 v_Phi)^2) "
    "(v_F = sqrt2 <F>, N_DW = 1 modulo gauge) depends on rS, which the family leaves free",
    "kappa_placement": "kappa = -r0^2/(4 rS) keeps O06 = r0^2/2 and the H block of the witness (heavy Im-10_H "
    "doublet at M_I) with |kappa| rS = r0^2/4; kappa = -rS/4 puts that doublet at <S>; neither placement is chosen "
    "here",
}

THEOREM = (
    "For every r0, rS, x0 > 0, real kappa with kappa^2 < 8 rS^2 and eps >= 0, the decoupled-singlet member V (the "
    "committed 27-parameter SM Pati-Salam map with O04 = -2 rS^2 and O06 = 2|kappa| rS + eps) satisfies V >= V0 = -1 "
    "- r0^4/8 - rS^4 - x0^4/32 and {V = V0} = G.(p, r0 sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ (given "
    "the committed equality-set theorem's rS-free parts).  The domain is sharp: V >= V0 fails for every kappa^2 > 8 "
    "rS^2 (exact violating points), while at kappa^2 = 8 rS^2 the bound and the equality set still hold (lambda_eff "
    "= 0); the certified domain is the open kappa^2 < 8 rS^2.  Exact over Q at (r0, rS, x0, kappa) = "
    "(1/5,1/5,1,-1/20), (1/5,1,1,-1/100), (1/5,1,1,-1/4) and the stress point (1/5,5,1,-5/4) (outside the |c| < 12 "
    "perturbative box, eps window 12 - 2|kappa| rS empty; an exact family member only): grad V(q0) = 0, the 486 x 486 "
    "Hessian has inertia 447/39/0 at eps = 0 (kernel = 35 orbit tangents + 4 real doublet directions) and 451/35/0 "
    "at eps = r0^2/100 and r0^2/10^6 (kernel = the orbit tangents), identical to the committed witness at rS = r0.  "
    "The orbit ranks are 33/34/35 at rS in {1/10, 1/5, 1, 2}; F_PQ^2 = 9248 rS^2 x0^2/(16 rS^2 + 289 x0^2) with S "
    "share 289 x0^2/(16 rS^2 + 289 x0^2), Phi17 share 16 rS^2/(16 rS^2 + 289 x0^2) and no Sigma share.  The model "
    "file gives N_X = 0, N_PQ = -34, E/N = 8/3 and N_DW = 1 modulo gauge (axion period 2 pi/68)."
)
ANOMALY_CAVEATS = (
    "N_DW = 1 holds modulo gauge only: the one-wall object is the (l, n) = (13, -3) string sector with Phi17 winding "
    "and S-winding 2 pi/17 (axion_so10_theory_v20.tex); if Phi17 breaks before inflation the S-only strings carry 17 "
    "walls, and the post-inflation branch is conditional on the (13, -3) string's existence and production",
    "the anomaly and N_DW do not depend on rS; f_a = v_a/N_DW = F_PQ/68 does",
)
STATUS_NEUTRALITY = (
    "status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20, g4_sm_closure_binding_v20 or "
    "any roadmap/readiness module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed, and the committed "
    "rS = r0 witness remains the G3 and G4 closing instance"
)


# ---------------------------------------------------------------------------
# Serialisation and small helpers.
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    return candidate._jsonable(value)


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _tag(value: Fraction) -> str:
    return str(Fraction(value)).replace("/", "_over_")


def _point_dict(point: Sequence[Any]) -> dict[str, str]:
    p = hessian.as_singlet_point(point)
    return {"r0": str(p.r0), "rS": str(p.rs), "x0": str(p.x0), "kappa": str(p.kappa)}


def _kappa_symbol(sign: str) -> Any:
    if sign == "negative":
        return sympy.Symbol("kappa", negative=True)
    if sign == "positive":
        return sympy.Symbol("kappa", positive=True)
    return sympy.Integer(0)


def _symbols() -> tuple[Any, Any, Any, Any]:
    r, x = sympy.symbols("r0 x0", positive=True)
    return r, x, sympy.Symbol("rS", positive=True), sympy.Symbol("eps", nonnegative=True)


def _map_difference(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    """Nonzero simplified differences left - right over the union of keys (sympy or Fraction values)."""
    output = {}
    for key in sorted(set(left) | set(right)):
        difference = sympy.simplify(candidate._as_sympy(left.get(key, 0)) - candidate._as_sympy(right.get(key, 0)))
        if difference != 0:
            output[key] = difference
    return output


def family_coefficients(point: Sequence[Any], eps: Any = 0) -> dict[str, Any]:
    """The decoupled-singlet member at (r0, rS, x0, kappa): the committed map with rs = rS (and O06 += eps)."""
    p = hessian.as_singlet_point(point)
    return candidate.candidate_coefficients(p.r0, p.x0, p.kappa, o06_offset=eps, rs=p.rs)


def _block_of(index: int) -> str:
    return next(name for name, block in BLOCK_NAMES if block.start <= index < block.stop)


def _difference_support(left: tuple[np.ndarray, int], right: tuple[np.ndarray, int]) -> list[list[str]]:
    """Block pairs where left - right (each (numerator, denominator)) is nonzero, exactly."""
    (left_num, left_den), (right_num, right_den) = left, right
    common = math.lcm(int(left_den), int(right_den))
    difference = np.asarray(left_num, dtype=object) * (common // int(left_den)) - np.asarray(right_num, dtype=object) * (
        common // int(right_den)
    )
    rows, columns = np.nonzero(difference != 0)
    return sorted({(_block_of(int(row)), _block_of(int(column))) for row, column in zip(rows.tolist(), columns.tolist())})


def _clear_point_caches() -> None:
    hessian._exact_hessian_point_cached.cache_clear()
    hessian._exact_certificate_point_cached.cache_clear()
    hessian.exact_unit_matrices.cache_clear()


def load_report(path: Path) -> dict[str, Any]:
    """A committed JSON report, {} if missing or unreadable (fail-closed)."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


# ---------------------------------------------------------------------------
# The coefficient map (checks 1-5).
# ---------------------------------------------------------------------------


def family_section(points: Sequence[tuple[str, Any]]) -> tuple[dict[str, Any], dict[str, bool]]:
    r, x, s, e = _symbols()
    reduction = {}
    for sign in ("negative", "positive"):
        k = _kappa_symbol(sign)
        difference = _map_difference(candidate.candidate_coefficients(r, x, k, rs=r), candidate.candidate_coefficients(r, x, k))
        reduction[sign] = {key: str(value) for key, value in difference.items()}
    benchmarks = {
        label: candidate.candidate_coefficients(r0, X0, rs=r0) == candidate.candidate_coefficients(r0, X0)
        for label, r0 in candidate.benchmark_r0_values().items()
    }
    k = _kappa_symbol("negative")
    family = candidate.candidate_coefficients(r, x, k, o06_offset=e, rs=s)
    witness = candidate.candidate_coefficients(r, x, k, o06_offset=e)
    changed = _map_difference(family, witness)
    changed_ok = bool(
        set(changed) == {O04, O06}
        and sympy.simplify(candidate._as_sympy(family[O04]) + 2 * s**2) == 0
        and sympy.simplify(candidate._as_sympy(family[O06]) - (-2 * k * s + e)) == 0
        and set(family) == set(witness)
        and len(family) == candidate.EXPECTED_NONZERO
    )
    selection = g2_audit.contract_selection()
    contract_ids = set(selection["parameter_ids"])
    witness_map = candidate.candidate_coefficients(R0, X0)
    records = {}
    inside = set(family) <= contract_ids
    portal_free = not (set(S_PORTAL_IDS) & set(family))
    for label, point in points:
        p = hessian.as_singlet_point(point)
        values = family_coefficients(p)
        inside = inside and len(values) == candidate.EXPECTED_NONZERO and set(values) <= contract_ids
        portal_free = portal_free and not (set(S_PORTAL_IDS) & set(values))
        upper = hessian.eps_perturbative_upper(p.kappa, p.rs)
        maximum = max(abs(value) for value in values.values())
        records[label] = {
            "point": _point_dict(p),
            "changed_vs_witness": {
                key: {"witness": witness_map.get(key, Fraction(0)), "point": values.get(key, Fraction(0))}
                for key in sorted(set(values) | set(witness_map))
                if values.get(key, Fraction(0)) != witness_map.get(key, Fraction(0))
            },
            "nonzero_count": len(values),
            "O04": values.get(O04, Fraction(0)),
            "O06": values.get(O06, Fraction(0)),
            "O12": values.get(O12, Fraction(0)),
            "V0": candidate.lower_bound_v0(p.r0, p.x0, rs=p.rs),
            "lambda_eff": candidate.exact_light_doublet_quartic(p.r0, p.kappa, rs=p.rs)["lambda_eff"],
            "kappa_squared_over_8_rS_squared": p.kappa * p.kappa / (8 * p.rs * p.rs),
            "abs_kappa_times_rS": abs(p.kappa) * p.rs,
            "kappa_is_minus_r0sq_over_4rS": p.kappa == -p.r0 * p.r0 / (4 * p.rs),
            "perturbative_box": {
                "bound": hessian.PERTURBATIVE_BOUND,
                "max_abs_coefficient": maximum,
                "eps_window_upper_exclusive": upper,
                "eps_window_nonempty": upper > 0,
                "perturbative_member": bool(maximum < hessian.PERTURBATIVE_BOUND and upper > 0),
            },
        }
    portals_declared = set(S_PORTAL_IDS) <= contract_ids
    v0_residual = sympy.simplify(candidate.lower_bound_v0(r, x, rs=s) + 1 + r**4 / 8 + s**4 + x**4 / 32)
    lambda_residual = sympy.simplify(
        candidate.exact_light_doublet_quartic(r, k, rs=s)["lambda_eff"] - (2 - k**2 / (4 * s**2))
    )
    checks = {
        "family_map_equals_witness_map_at_rS_equal_r0_symbolic_and_benchmarks": bool(
            not any(reduction.values()) and benchmarks and all(benchmarks.values())
        ),
        "family_map_changes_only_O04_and_O06_symbolic": changed_ok,
        "family_map_27_parameters_inside_51_parameter_contract": bool(
            inside and selection["parameter_count"] == 51 and len(family) == candidate.EXPECTED_NONZERO
        ),
        "family_map_has_no_S_portal_parameters": bool(portals_declared and portal_free),
        "family_V0_and_lambda_eff_closed_forms_symbolic": bool(v0_residual == 0 and lambda_residual == 0),
    }
    section = {
        "statement": "the committed 27-parameter map with |S| = rS: O04 = -2 rS^2, O06 = 2|kappa| rS + eps, every "
        "other entry unchanged (candidate_coefficients(r0, x0, kappa, o06_offset=eps, rs=rS))",
        "symbolic_changed_entries_vs_witness_map": {key: str(value) for key, value in changed.items()},
        "symbolic_O04": str(family[O04]),
        "symbolic_O06": str(family[O06]),
        "reduction_at_rS_equal_r0_symbolic_residuals": reduction,
        "reduction_at_rS_equal_r0_benchmarks": benchmarks,
        "contract_parameter_count": selection["parameter_count"],
        "S_portal_parameters": list(S_PORTAL_IDS),
        "S_portal_parameters_declared_in_contract": portals_declared,
        "V0": "-1 - r0^4/8 - rS^4 - x0^4/32",
        "V0_symbolic_residual": str(v0_residual),
        "lambda_eff": "2 - kappa^2/(4 rS^2)",
        "lambda_eff_symbolic_residual": str(lambda_residual),
        "heavy_doublet_placement": "O06 = 2|kappa| rS and the Im H_6..9 curvature 4|kappa| rS; kappa = -r0^2/(4 rS) "
        "gives |kappa| rS = r0^2/4 for every rS (O06 = r0^2/2, the witness H block); kappa = -rS/4 gives "
        "|kappa| rS = rS^2/4",
        "eps_window": "0 < eps < 12 - 2|kappa| rS (nonempty iff |kappa| rS < 6); a perturbative member also needs "
        "every coefficient in the 12 box (|O04| = 2 rS^2 < 12 iff rS < sqrt(6))",
        "points": records,
    }
    return section, checks


# ---------------------------------------------------------------------------
# The SOS identity at rS (checks 6-10).
# ---------------------------------------------------------------------------

SOS_OPERATOR_COUNTS = {"negative": 27, "positive": 27, "zero": 26}


def sos_section(
    points: Sequence[tuple[str, Any]], self_weights: Mapping[str, Fraction]
) -> tuple[dict[str, Any], dict[str, bool]]:
    r, x, s, e = _symbols()
    expansion = equality._eight_term_expansion(dict(self_weights), rs=s, eps=e)
    rows = expansion["by_kappa_sign"]
    plus_eps = {}
    for sign in ("negative", "positive", "zero"):
        k = _kappa_symbol(sign)
        mapped = candidate.candidate_coefficients(r, x, k, o06_offset=e, rs=s)
        expanded = dict(candidate.expanded_sos_coefficient_map(r, x, k, rs=s))
        expanded[O06] = expanded.get(O06, 0) + e
        plus_eps[sign] = {key: str(value) for key, value in _map_difference(mapped, expanded).items()}
    at_points = {
        label: candidate.expanded_sos_coefficient_map(p.r0, p.x0, p.kappa, rs=p.rs) == family_coefficients(p)
        for label, p in ((label, hessian.as_singlet_point(point)) for label, point in points)
    }
    checks = {}
    for sign in ("negative", "positive", "zero"):
        row = rows[sign]
        checks[f"sos_eight_terms_expand_to_family_map_kappa_{sign}"] = bool(
            row["matches_operator_by_operator_and_constant_is_minus_V0"]
            and row["operators_compared"] == SOS_OPERATOR_COUNTS[sign]
            and row["constant_plus_V0"] == "0"
        )
    checks["candidate_map_with_rS_eps_equals_expanded_sos_map_plus_eps_three_signs"] = not any(plus_eps.values())
    checks["sos_expanded_map_equals_family_map_at_every_point_exact"] = bool(at_points) and all(at_points.values())
    section = {
        "statement": "V - V0 = T1 + ... + T8 + T9 with T6 = V_HS(rS) + rS^4 = 2 N_H^2 + 2|kappa| rS N_H + 2 kappa "
        "Re(conj(H.H) conj(S)) + (|S|^2 - rS^2)^2 and T9 = eps N_H; every term >= 0 for kappa^2 < 8 rS^2, eps >= 0",
        "symbols": "r0, x0, rS > 0, eps >= 0; kappa < 0, kappa > 0 (sympy symbols) and kappa = 0",
        "self_weights_54_1050bar_2772bar_4125": dict(self_weights),
        "eight_term_operator_expansion": expansion,
        "operators_compared_by_sign": {sign: rows[sign]["operators_compared"] for sign in rows},
        "candidate_map_minus_expanded_map_plus_eps_residuals": plus_eps,
        "expanded_map_equals_family_map_at_points": at_points,
    }
    return section, checks


# ---------------------------------------------------------------------------
# The H/S sector: P3 at rS and sharpness (checks 11-23).
# ---------------------------------------------------------------------------


def _t6_on_curve(rs: Fraction, kappa: Fraction, t: Fraction, n_h: Fraction) -> Fraction:
    """V_HS + rS^4 at H = h e_6 (h real, h^2 = n_h), S = rS + t real: exact."""
    s_abs = rs + t
    return 2 * n_h * n_h + 2 * abs(kappa) * rs * n_h + 2 * kappa * n_h * s_abs + (s_abs * s_abs - rs * rs) ** 2


def hs_section(
    points: Sequence[tuple[str, Any]], hs_points: Sequence[tuple[Any, ...]]
) -> tuple[dict[str, Any], dict[str, bool]]:
    p3, p3_checks = equality.p3_section(hs_points)
    s = sympy.Symbol("rS", positive=True)
    a = sympy.Symbol("k_abs", positive=True)
    t = sympy.Symbol("t", positive=True)
    n = sympy.Symbol("N_H", nonnegative=True)
    reduced = 2 * n**2 + 2 * a * s * n - 2 * a * n * (s + t) + ((s + t) ** 2 - s**2) ** 2
    curve = sympy.expand(reduced.subs(n, a * t / 2) - t**2 * ((2 * s + t) ** 2 - a**2 / 2))
    boundary = sympy.factor(sympy.expand(t**2 * ((2 * s + t) ** 2 - 8 * s**2 / 2)))
    boundary_ok = sympy.expand(boundary - t**3 * (t + 4 * s)) == 0
    # The boundary kappa^2 = 8 rS^2 globally (all N_H >= 0, u = |S| - rS >= -rS): after Cauchy-Schwarz
    # T6 >= 2 N_H^2 - 2|kappa| N_H u + u^2 (u + 2 rS)^2 = 2 (N_H - |kappa| u/2)^2 + u^2 [(u + 2 rS)^2 - kappa^2/2], and
    # the bracket at |kappa| = 2 sqrt2 rS is u (u + 4 rS).
    u = sympy.Symbol("u", real=True)
    lower = 2 * n**2 + 2 * a * s * n - 2 * a * n * (s + u) + ((s + u) ** 2 - s**2) ** 2
    completed = 2 * (n - a * u / 2) ** 2 + u**2 * ((u + 2 * s) ** 2 - a**2 / 2)
    nonpositive_u_form = 2 * n**2 + 2 * a * n * (-u) + u**2 * (u + 2 * s) ** 2
    global_residuals = {
        "completed_square": sympy.expand(lower - completed),
        "nonpositive_u_form": sympy.expand(lower - nonpositive_u_form),
    }
    boundary_bracket = sympy.factor(sympy.expand(((u + 2 * s) ** 2 - a**2 / 2).subs(a, 2 * sympy.sqrt(2) * s)))
    boundary_bracket_ok = sympy.expand(boundary_bracket - u * (u + 4 * s)) == 0
    boundary_global_ok = bool(boundary_ok and boundary_bracket_ok and all(value == 0 for value in global_residuals.values()))
    q_h = np.asarray(hessian.h_wedge_data()["Q_H"])
    doublet_wedge_zero = bool(not np.any(q_h[6, :]) and not np.any(q_h[:, 6]))
    witnesses = []
    for (rs, kappa, step), expected in zip(SHARPNESS_WITNESSES, SHARPNESS_VALUES, strict=True):
        n_h = abs(kappa) * step / 2
        formula = step * step * ((2 * rs + step) ** 2 - kappa * kappa / 2)
        direct = _t6_on_curve(rs, kappa, step, n_h)
        witnesses.append(
            {
                "rS": rs,
                "kappa": kappa,
                "t": step,
                "kappa_squared_minus_8_rS_squared": kappa * kappa - 8 * rs * rs,
                "field_point": {
                    "Phi": "p",
                    "Sigma": "r0 sigma_std",
                    "H": "h e_6 (real, weak-doublet component Re H_6), h^2 = |kappa| t/2",
                    "S": "rS + t (real)",
                    "Phi17": "x0",
                },
                "h_squared": n_h,
                "S_value": rs + step,
                "V_minus_V0_equals_T6": direct,
                "curve_formula_t2_times_bracket": formula,
                "expected": expected,
                "negative": direct < 0,
            }
        )
    witnesses_ok = bool(
        doublet_wedge_zero
        and all(
            row["V_minus_V0_equals_T6"] == row["curve_formula_t2_times_bracket"] == row["expected"]
            and row["negative"]
            and row["kappa_squared_minus_8_rS_squared"] > 0
            for row in witnesses
        )
    )
    lambda_rows = {}
    for label, point in points:
        p = hessian.as_singlet_point(point)
        value = candidate.exact_light_doublet_quartic(p.r0, p.kappa, rs=p.rs)["lambda_eff"]
        lambda_rows[label] = {"lambda_eff": value, "closed_form_2_minus_kappa2_over_4rS2": 2 - p.kappa**2 / (4 * p.rs**2)}
    checks = {
        "kappa_bound_sharp_curve_identity_exact": curve == 0,
        "kappa_bound_violated_beyond_boundary_at_exact_rational_witnesses": witnesses_ok,
        "kappa_boundary_bound_and_equality_set_hold_curve_and_completed_square_exact": boundary_global_ok,
        "lambda_eff_equals_2_minus_kappa_sq_over_4rS_sq_at_every_point": bool(lambda_rows)
        and all(row["lambda_eff"] == row["closed_form_2_minus_kappa2_over_4rS2"] for row in lambda_rows.values()),
    }
    for name, value in p3_checks.items():
        checks["p3_family_" + name] = bool(value)
    section = {
        "p3": p3,
        "p3_checks": p3_checks,
        "p3_note": "equality.p3_section with (r0, kappa, rS) points states P3 at rS (statement, domain, proof text "
        "and the H/S bracket algebra in the scale symbol rS); the charges, phases, operator neutrality and the integer "
        "tangent ranks are scale-free",
        "sharpness": {
            "curve": "H = h e_6 real (a weak-doublet direction: ||H wedge p||^2 = h^2 Q_H[6,6] = 0), S = rS + t real, "
            "kappa < 0, h^2 = |kappa| t/2: V_HS + rS^4 = t^2 [(2 rS + t)^2 - kappa^2/2]",
            "kappa_positive": "for kappa > 0 the same curve with H = i h e_6 (H.H = -h^2, the same N_H and Q_H value) "
            "gives the same identity, so V >= V0 fails for every kappa^2 > 8 rS^2 of either sign (0 < t < |kappa|/sqrt2 "
            "- 2 rS)",
            "curve_identity_residual": str(curve),
            "other_sos_terms_vanish": "T1-T5 and T8 involve only (Phi, Sigma, Phi17), which sit at the vacuum values; "
            "T7 = ||H wedge p||^2 = h^2 Q_H[6,6] = 0 (Q_H = diag(1^6, 0^4), integer); T9 = eps N_H is absent at eps = 0; "
            "so V - V0 = T6 exactly on the curve",
            "Q_H_doublet_row_and_column_6_zero": doublet_wedge_zero,
            "violating_witnesses": witnesses,
            "boundary_kappa_squared_eq_8_rS_squared": str(boundary),
            "boundary_global_lower_bound": "u = |S| - rS: T6 >= 2 N_H^2 - 2|kappa| N_H u + u^2 (u + 2 rS)^2 = "
            "2 (N_H - |kappa| u/2)^2 + u^2 [(u + 2 rS)^2 - kappa^2/2] (Cauchy-Schwarz |H.H| <= N_H)",
            "boundary_global_residuals": {key: str(value) for key, value in global_residuals.items()},
            "boundary_bracket_at_kappa_squared_eq_8_rS_squared": str(boundary_bracket),
            "boundary_note": "at kappa^2 = 8 rS^2 (lambda_eff = 0) the bound and the equality set still hold: for u > 0 "
            "T6 >= 2 (N_H - |kappa| u/2)^2 + u^3 (u + 4 rS) > 0; for -rS <= u < 0 every term of 2 N_H^2 + 2|kappa| N_H "
            "|u| + u^2 (u + 2 rS)^2 is >= 0 and u^2 (u + 2 rS)^2 > 0; at u = 0 T6 >= 2 N_H^2, which is 0 iff H = 0 (the "
            "elementary sign argument of P3).  So V >= V0 with {V = V0} unchanged on the boundary, and the bound is "
            "sharp in the sense that it fails for every kappa^2 > 8 rS^2.  The certified domain is the open kappa^2 < 8 "
            "rS^2 (the committed convention; lambda_eff > 0 and the exact Hessians are certified only there)",
        },
        "lambda_eff": lambda_rows,
    }
    return section, checks


# ---------------------------------------------------------------------------
# Equality set (checks 24-25).
# ---------------------------------------------------------------------------


def equality_section(
    points: Sequence[tuple[str, Any]], equality_report: Mapping[str, Any] | None
) -> tuple[dict[str, Any], dict[str, bool]]:
    report = hessian.load_equality_report() if equality_report is None else equality_report
    premises = hessian.equality_premises(report)
    witness_ids = set(candidate.candidate_coefficients(R0, X0))
    operator_ids = {row["parameter"] for row in equality.operator_data()["operators"]}
    rows = hessian._get(report, "P3_H_S_Phi17_phases", "operators", "operators", default=[])
    committed_ids = {row.get("parameter") for row in rows if isinstance(row, Mapping)} if isinstance(rows, list) else set()
    r, x, s, e = _symbols()
    symbolic_ids = set(candidate.candidate_coefficients(r, x, _kappa_symbol("negative"), o06_offset=e, rs=s))
    point_ids = {label: set(family_coefficients(point)) == witness_ids for label, point in points}
    checks = {
        "equality_set_premises_from_committed_report": bool(premises) and all(premises.values()),
        "family_operator_ids_equal_witness_operator_ids": bool(
            witness_ids == operator_ids == committed_ids == symbolic_ids and all(point_ids.values())
        ),
    }
    section = {
        "claim": "{V = V0} = G.(p, r0 sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ, for kappa^2 < 8 rS^2",
        "committed_equality_report_premises": premises,
        "family_operator_ids_equal_witness_ids": point_ids,
        "relies_on": {
            "P0": "replaced by this report's sos_identity (eight terms with T6 at rS and T9 = eps N_H)",
            "P1_Phi": "contains no S: carried over verbatim from the committed proved equality-set report (the "
            "exact 210 uniqueness; decision D6 inputs)",
            "P2_Sigma": "contains no S: carried over verbatim from the committed proved equality-set report",
            "P3": "the H/S bracket at rS (hs_sector.p3 with (r0, kappa, rS) points); the X/PQ charges, the explicit "
            "phase element and the operator neutrality are scale-free and the operator ids are the witness ids",
            "tangent_ranks": "D = diag(1, sqrt2 r0/4, sqrt2 rS, sqrt2 x0) is invertible for rS > 0, so the integer "
            "ranks 33/34/35 and the 12-dimensional SM stabilizer carry over (tangent_ranks re-checks them exactly)",
            "eps_lemma_L1": "N_H >= 0 with equality iff H = 0 is scale-free, so {V_eps = V0} = {V = V0} for eps >= 0",
        },
    }
    return section, checks


# ---------------------------------------------------------------------------
# Exact 486 x 486 Hessians at the family points (checks 26-53).
# ---------------------------------------------------------------------------

POINT_CHECK_SUFFIXES = (
    "tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4",
    "eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient",
    "gaps_r0sq_over_96_mult_14_and_eps_mult_4",
    "linear_in_eps_and_doublet_eigenvalue_eps",
    "H_and_S_blocks_closed_form_and_decoupled",
    "difference_from_witness_only_on_H_and_S_blocks",
)


def _inertia_text(certificate: Mapping[str, Any]) -> str:
    inertia = certificate["inertia"]
    return f"{inertia['positive']}/{inertia['zero']}/{inertia['negative']}"


def _coverage_ok(certificate: Mapping[str, Any]) -> bool:
    coverage = certificate["coverage"]
    return bool(
        coverage["coefficients_proportional_to_unit_weights"]
        and coverage["every_nonzero_parameter_covered"]
        and coverage["no_parameter_in_two_units"]
        and not coverage["units_parameters_not_in_benchmark"]
    )


def _certificate_summary(certificate: Mapping[str, Any], eps: Fraction) -> dict[str, Any]:
    gap = certificate["spectral_gap"]
    return {
        "O06": certificate["O06"],
        "eps": eps,
        "inertia_positive_zero_negative": _inertia_text(certificate),
        "rank": certificate["exact_rank"],
        "nullity": certificate["exact_nullity"],
        "kernel_equals_expected_span": certificate["kernel_equals_expected_span"],
        "gradient_exactly_zero": certificate["gradient_exactly_zero"],
        "exactly_symmetric": certificate["exactly_symmetric"],
        "strictly_positive_on_symmetry_quotient": certificate["strictly_positive_on_symmetry_quotient"],
        "strictly_positive_on_kernel_complement": certificate["strictly_positive_on_kernel_complement"],
        "smallest_nonzero_eigenvalue": gap["lambda"],
        "is_smallest": gap["lambda_is_smallest_nonzero_eigenvalue"],
        "multiplicity": gap["multiplicity"],
        "denominator": certificate["denominator"],
        "nonzero_entries": certificate["nonzero_entries"],
        "coverage_ok": _coverage_ok(certificate),
    }


def _h_and_s_blocks(numerator: np.ndarray, denominator: int, point: hessian.SingletPoint, eps: Fraction) -> dict[str, Any]:
    hb, sb = chart.H_SLICE, chart.S_SLICE
    numerator = np.asarray(numerator, dtype=object)
    curvatures = [Fraction(int(numerator[i, i]), int(denominator)) / 2 for i in range(hb.start, hb.stop)]
    heavy = 4 * abs(point.kappa) * point.rs
    expected = []
    for component in range(chart.H_COMPLEX_DIM):
        expected.append((1 if component < 6 else 0) + eps)
        expected.append((1 + heavy if component < 6 else heavy) + eps)
    h_block = numerator[hb, hb]
    h_offdiagonal_zero = not np.any((h_block - np.diag(np.diag(h_block))) != 0)
    h_rows = numerator[hb, :]
    outside_h = np.concatenate([h_rows[:, : hb.start], h_rows[:, hb.stop :]], axis=1)
    s_block = [[Fraction(int(numerator[i, j]), int(denominator)) for j in range(sb.start, sb.stop)] for i in range(sb.start, sb.stop)]
    s_rows = numerator[sb, :]
    outside_s = np.concatenate([s_rows[:, : sb.start], s_rows[:, sb.stop :]], axis=1)
    counts: dict[Fraction, int] = {}
    for value in curvatures:
        counts[value] = counts.get(value, 0) + 1
    return {
        "H_chart_curvatures_by_value": {str(value): counts[value] for value in sorted(counts)},
        "H_curvatures_equal_closed_form": curvatures == expected,
        "H_offdiagonal_zero": bool(h_offdiagonal_zero),
        "H_rows_vanish_outside_H": bool(not np.any(outside_h != 0)),
        "S_u_block": s_block,
        "S_u_block_equals_8rS2_0_0_0": s_block == [[8 * point.rs * point.rs, Fraction(0)], [Fraction(0), Fraction(0)]],
        "S_rows_vanish_outside_S": bool(not np.any(outside_s != 0)),
        "S_radial_chart_mass_squared": s_block[0][0] / 2,
    }


def hessian_point_section(
    label: str,
    point: hessian.SingletPoint,
    witness: Mapping[str, Mapping[str, Any]],
    axion: tuple[np.ndarray, int],
) -> tuple[dict[str, Any], dict[str, bool]]:
    p = hessian.as_singlet_point(point)
    mats = {variant: hessian.exact_hessian(variant, point=p) for variant in VARIANTS}
    certs = {variant: hessian.exact_certificate(variant, point=p) for variant in VARIANTS}
    offsets = {variant: hessian.variant_offset(variant, p) for variant in VARIANTS}
    doublet = hessian.doublet_matrix()
    two_p_h = (hessian._two_p_h(), 1)
    summaries = {variant: _certificate_summary(certs[variant], offsets[variant]) for variant in VARIANTS}
    linear = {
        variant: hessian._difference_is(mats[variant]["hessian"], mats["benchmark"]["hessian"], offsets[variant], two_p_h)
        for variant in LIFTED
    }
    doublet_eigen = {}
    blocks = {}
    support = {}
    for variant in VARIANTS:
        numerator, denominator = mats[variant]["hessian"]
        doublet_eigen[variant] = hessian._fraction_matrix_equal(
            hessian._exact_matmul(numerator, doublet), denominator, doublet, 2 * offsets[variant]
        )
        blocks[variant] = _h_and_s_blocks(numerator, denominator, p, offsets[variant])
        support[variant] = _difference_support(mats[variant]["hessian"], witness[variant]["hessian"])
    raised_numerator = np.asarray(mats["raised_O06"]["hessian"][0], dtype=object)
    axion_vector, _ = axion
    axion_in_kernel = hessian._all_zero(hessian._exact_matmul(raised_numerator, np.asarray(axion_vector, dtype=object).reshape(-1, 1)))
    lightest = hessian.LIGHTEST_MASSIVE_OVER_R0_SQUARED * p.r0 * p.r0
    precondition = bool(4 * abs(p.kappa) * p.rs > lightest and 4 * p.rs * p.rs > lightest)
    witness_h_block_equal = all(
        _h_block_fractions(mats[variant]["hessian"]) == _h_block_fractions(witness[variant]["hessian"]) for variant in VARIANTS
    )
    bench, raised, tiny = (summaries[variant] for variant in VARIANTS)
    checks = {
        "tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4": bool(
            bench["gradient_exactly_zero"]
            and bench["exactly_symmetric"]
            and bench["coverage_ok"]
            and bench["inertia_positive_zero_negative"] == "447/39/0"
            and bench["kernel_equals_expected_span"]
        ),
        "eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient": all(
            row["gradient_exactly_zero"]
            and row["exactly_symmetric"]
            and row["coverage_ok"]
            and row["inertia_positive_zero_negative"] == "451/35/0"
            and row["kernel_equals_expected_span"]
            and row["strictly_positive_on_symmetry_quotient"]
            and row["strictly_positive_on_kernel_complement"]
            for row in (raised, tiny)
        ),
        "gaps_r0sq_over_96_mult_14_and_eps_mult_4": bool(
            precondition
            and bench["smallest_nonzero_eigenvalue"] == lightest
            and bench["is_smallest"]
            and bench["multiplicity"] == 14
            and all(
                row["smallest_nonzero_eigenvalue"] == offsets[variant]
                and row["is_smallest"]
                and row["multiplicity"] == candidate.LIGHT_DOUBLET_REAL_DIMENSION
                for variant, row in (("raised_O06", raised), ("tiny_eps", tiny))
            )
        ),
        "linear_in_eps_and_doublet_eigenvalue_eps": bool(all(linear.values()) and all(doublet_eigen.values())),
        "H_and_S_blocks_closed_form_and_decoupled": all(
            row["H_curvatures_equal_closed_form"]
            and row["H_offdiagonal_zero"]
            and row["H_rows_vanish_outside_H"]
            and row["S_u_block_equals_8rS2_0_0_0"]
            and row["S_rows_vanish_outside_S"]
            for row in blocks.values()
        ),
        "difference_from_witness_only_on_H_and_S_blocks": all(
            set(map(tuple, rows)) <= {("H", "H"), ("S", "S")} for rows in support.values()
        ),
    }
    record = {
        "point": _point_dict(p),
        "certificates": summaries,
        "linearity_in_eps_exact": linear,
        "doublet_eigenvalue_eps_exact": doublet_eigen,
        "H_and_S_blocks": blocks,
        "difference_support_vs_witness": {variant: [list(pair) for pair in rows] for variant, rows in support.items()},
        "H_block_equal_to_witness_all_variants": witness_h_block_equal,
        "axion_in_kernel_of_raised_hessian": axion_in_kernel,
        "lowest_level_precondition_4_abs_kappa_rS_and_4_rS2_above_r0sq_over_96": precondition,
        "checks": checks,
    }
    return record, checks


def _h_block_fractions(matrix: tuple[np.ndarray, int]) -> list[list[Fraction]]:
    numerator, denominator = matrix
    hb = chart.H_SLICE
    block = np.asarray(numerator, dtype=object)[hb, hb]
    return [[Fraction(int(value), int(denominator)) for value in row] for row in block.tolist()]


def rs_eq_r0_regression() -> tuple[dict[str, Any], bool]:
    rows = {}
    for variant in VARIANTS:
        via_point = hessian.exact_hessian(variant, point=hessian.WITNESS_POINT)
        default = hessian.exact_hessian(variant)
        rows[variant] = {
            "hessian_numerators_equal": bool(np.array_equal(via_point["hessian"][0], default["hessian"][0])),
            "hessian_denominators_equal": int(via_point["hessian"][1]) == int(default["hessian"][1]),
            "gradients_equal": bool(
                np.array_equal(via_point["gradient"][0], default["gradient"][0])
                and int(via_point["gradient"][1]) == int(default["gradient"][1])
            ),
            "certificates_equal": hessian.json_roundtrip(hessian.exact_certificate(variant, point=hessian.WITNESS_POINT))
            == hessian.json_roundtrip(hessian.exact_certificate(variant)),
        }
    tangents_equal = bool(
        np.array_equal(
            hessian.tangent_data(hessian.WITNESS_POINT)["T_u_times_common"], hessian.tangent_data()["T_u_times_common"]
        )
    )
    ok = tangents_equal and all(all(row.values()) for row in rows.values())
    return {"witness_point": _point_dict(hessian.WITNESS_POINT), "variants": rows, "tangents_equal": tangents_equal}, ok


def committed_hessian_binding(
    hessian_report: Mapping[str, Any] | None, witness_certificates: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, Any], bool]:
    report = load_report(hessian.OUT_JSON) if hessian_report is None else hessian_report
    fresh = {variant: hessian.json_roundtrip(certificate) for variant, certificate in witness_certificates.items()}
    keys = ("inertia", "exact_rank", "exact_nullity", "denominator", "nonzero_entries")
    comparisons = {}
    for name, variant in (("exact_certificate", "benchmark"), ("exact_certificate_raised_O06", "raised_O06")):
        committed = report.get(name, {}) if isinstance(report.get(name), dict) else {}
        row = {key: committed.get(key) == fresh[variant].get(key) for key in keys}
        gap = committed.get("spectral_gap", {}) if isinstance(committed.get("spectral_gap"), dict) else {}
        row["spectral_gap_lambda"] = gap.get("lambda") == fresh[variant]["spectral_gap"]["lambda"]
        row["spectral_gap_multiplicity"] = gap.get("multiplicity") == fresh[variant]["spectral_gap"]["multiplicity"]
        comparisons[name] = row
    tiny = hessian._get(report, "eps_family", "consistency_certificates", "tiny_eps", default={})
    tiny = tiny if isinstance(tiny, dict) else {}
    comparisons["eps_family.consistency_certificates.tiny_eps"] = {
        "inertia_451_35_0": tiny.get("inertia_positive_zero_negative") == "451/35/0"
        and _inertia_text(fresh["tiny_eps"]) == "451/35/0",
        "denominator": tiny.get("denominator") == fresh["tiny_eps"]["denominator"],
    }
    ok = bool(
        report.get("status") == hessian.STATUS_CERTIFIED
        and report.get("n_failed") == 0
        and all(all(row.values()) for row in comparisons.values())
    )
    return {
        "source": hessian.OUT_JSON.name,
        "status_certified": report.get("status") == hessian.STATUS_CERTIFIED,
        "n_failed": report.get("n_failed"),
        "comparisons_with_rS_eq_r0_certificates": comparisons,
    }, ok


# ---------------------------------------------------------------------------
# Tangent ranks and the G4 sections at rS (checks 54-69).
# ---------------------------------------------------------------------------

MINOR_NAMES = ("SO10", "SO10_x_U1X", "SO10_x_U1X_x_PQ")


def tangent_rank_section(
    rs_values: Sequence[Fraction], gauge_sections: Mapping[Fraction, Mapping[str, Any]]
) -> tuple[dict[str, Any], dict[str, bool]]:
    rows = {}
    checks = {}
    for rs in rs_values:
        point = P(R0, rs, X0, -R0 * R0 / (4 * rs))
        data = hessian.tangent_data(point)
        scaled = data["T_u_times_common"]
        ranks = [hessian._rank_exact(scaled[:, :45]), hessian._rank_exact(scaled[:, :46]), hessian._rank_exact(scaled)]
        gauge = gauge_sections[rs]
        integer_minors = {name: gauge["certificates"][name]["minor"]["determinant_integer_M"] for name in MINOR_NAMES}
        du_minors = {name: gauge["certificates"][name]["minor"]["determinant_D_u_M"] for name in MINOR_NAMES}
        rows[f"rS={rs}"] = {
            "point": _point_dict(point),
            "row_scale": data["row_scale"],
            "scaled_ranks_so10_X_PQ": ranks,
            "integer_minor_determinants": integer_minors,
            "D_u_minor_determinants": du_minors,
            "stabilizer_dimension": gauge["stabilizer"]["dimension"],
            "stabilizer_equals_standard_SM_algebra": gauge["stabilizer"]["equals_standard_SM_algebra"],
            "gauge_quotient_checks_all_true": all(gauge["checks"].values()),
        }
        checks[f"tangent_ranks_33_34_35_minors_and_SM_stabilizer_at_rS_{_tag(rs)}"] = bool(
            ranks == [33, 34, 35]
            and integer_minors == g4.EXPECTED_MINOR_DETERMINANTS
            and all(value != 0 for value in du_minors.values())
            and gauge["stabilizer"]["equals_standard_SM_algebra"]
            and gauge["stabilizer"]["dimension"] == candidate.EXPECTED_STABILIZER_DIMENSION
            and all(gauge["checks"].values())
        )
    section = {
        "statement": "rS enters only the S rows of the invertible D_u; these ranks are a regression of an rS-free "
        "statement (integer ranks of M), re-checked exactly on D_u M",
        "by_rS": rows,
    }
    return section, checks


def _expected_neutral_terms(rs: Fraction) -> dict[str, str]:
    t, lam = sympy.symbols("t lambda")
    r0 = sympy.Rational(R0.numerator, R0.denominator)
    x0 = sympy.Rational(X0.numerator, X0.denominator)
    s = sympy.Rational(Fraction(rs).numerator, Fraction(rs).denominator)
    polynomial = lam * (
        lam**2 - (10 * r0**2 + (578 * x0**2 + 32 * s**2 + 8 * r0**2) * t**2) * lam + r0**2 * (5780 * x0**2 + 320 * s**2) * t**2
    )
    return g4._polynomial_terms(sympy.expand(polynomial), lam, t)


def g4_rs_section(
    rs: Fraction, matrix: np.ndarray, gauge: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, bool], tuple[np.ndarray, int]]:
    pivots = [g4.GENERATOR_LABELS.index(label) for label in gauge["certificates"]["SO10_x_U1X"]["minor"]["column_generator_labels"]]
    axion = g4.axion_section(matrix, pivots, g4.X_CHARGES, g4.PQ_CHARGES, rs=rs)
    axion_vector = axion.pop("_axion")
    denominator = 16 * rs * rs + 289 * X0 * X0
    f2_expected = 9248 * rs * rs * X0 * X0 / denominator
    fractions_expected = {
        "Phi210": Fraction(0),
        "H10": Fraction(0),
        "Sigma126bar": Fraction(0),
        "S": 289 * X0 * X0 / denominator,
        "Phi17": 16 * rs * rs / denominator,
    }
    period = axion["decay_constant"]["period_certificate"]
    v_a_squared = axion["decay_constant"]["v_a_squared"]
    axion_ok = bool(
        axion["axion_norm_squared"] == f2_expected
        and axion["squared_norm_fractions"] == fractions_expected
        and v_a_squared == f2_expected / 68**2 == 2 * rs * rs * X0 * X0 / denominator
        and period["period_denominator"] == g4.EXPECTED_AXION_PERIOD_DENOMINATOR
        and period["explicit_gauge_element_units_of_2pi"] is not None
        and axion["PQ_tangent_norm_squared"] == 8 * R0 * R0 + 32 * rs * rs
        and all(axion["checks"][name] for name in RS_INDEPENDENT_AXION_CHECKS)
    )
    vectors = g4.vector_boson_section(matrix, rs=rs)
    terms = vectors["neutral_block"]["characteristic_polynomial_terms_lambda_t_exponents"]
    expected_terms = _expected_neutral_terms(rs)
    gamma = {row["sector"]: row["gamma_eigenvalue"] for row in vectors["sectors"] if row["expected_gamma_eigenvalue"] is not None}
    unbroken = sum(row["real_dimension"] for row in vectors["sectors"] if row["unbroken"])
    # lambda divides the neutral characteristic polynomial exactly once: no lambda^0 term, some lambda^1 term.
    neutral_zero_root = bool(terms) and not any(key.startswith("(0,") for key in terms) and any(
        key.startswith("(1,") for key in terms
    )
    massless = unbroken + (1 if neutral_zero_root else 0)
    chart_section = g4.chart_normalisation_section(matrix, rs=rs)
    chart_expected = 1 + 2 * R0 * R0 + 2 * rs * rs + 2 * X0 * X0
    vectors_ok = bool(
        terms == expected_terms
        and gamma == EXPECTED_CHARGED_VECTOR_GAMMA
        and vectors["gram_rank"] == g4.EXPECTED_GAUGE_RANK
        and massless == candidate.EXPECTED_STABILIZER_DIMENSION
        and all(vectors["checks"][name] for name in RS_INDEPENDENT_VECTOR_CHECKS)
        and chart_section["vacuum_norm_squared_chart"] == chart_expected
        and all(chart_section["checks"].values())
    )
    record = {
        "axion_norm_squared_F_PQ2": axion["axion_norm_squared"],
        "axion_norm_squared_closed_form": f2_expected,
        "squared_norm_fractions": axion["squared_norm_fractions"],
        "v_a_squared": v_a_squared,
        "axion_period_modulo_gauge": axion["decay_constant"]["axion_angle_period_modulo_gauge"],
        "axion_period_denominator": period["period_denominator"],
        "period_element_units_of_2pi": period["explicit_gauge_element_units_of_2pi"],
        "PQ_tangent_norm_squared": axion["PQ_tangent_norm_squared"],
        "axion_u_components": axion["axion_u_components"],
        "rS_independent_axion_checks": {name: axion["checks"][name] for name in RS_INDEPENDENT_AXION_CHECKS},
        "witness_pinned_axion_checks_(ignored_off_witness)": {
            name: axion["checks"][name]
            for name in ("axion_norm_squared_9248_over_7241", "axion_composition_S_7225_Phi17_16_over_7241_Sigma_Phi_H_0", "axion_period_modulo_gauge_2pi_over_68")
        },
        "D_u_minor_determinants": {name: gauge["certificates"][name]["minor"]["determinant_D_u_M"] for name in MINOR_NAMES},
        "vector_gram_rank": vectors["gram_rank"],
        "charged_vector_gamma": gamma,
        "neutral_block_terms_lambda_t_exponents": terms,
        "neutral_block_expected_terms": expected_terms,
        "massless_vectors": massless,
        "rS_independent_vector_checks": {name: vectors["checks"][name] for name in RS_INDEPENDENT_VECTOR_CHECKS},
        "chart_vacuum_norm_squared": chart_section["vacuum_norm_squared_chart"],
        "chart_vacuum_norm_squared_expected": chart_expected,
        "chart_checks": chart_section["checks"],
    }
    checks = {
        f"g4_axion_closed_forms_and_period_at_rS_{_tag(rs)}": axion_ok,
        f"g4_vectors_and_chart_norm_at_rS_{_tag(rs)}": vectors_ok,
    }
    return record, checks, g4._integer_vector(axion_vector)


def route_a_symbolic(matrix: np.ndarray) -> tuple[dict[str, Any], bool, Any]:
    """F_PQ^2 for all rS from the structure of the integer tangent matrix (exact premises) plus a 2 x 2 projection."""
    matrix = np.asarray(matrix)
    s_rows, x_rows, h_rows, sigma_rows = chart.S_SLICE, chart.X_SLICE, chart.H_SLICE, chart.SIGMA_SLICE
    so10 = g4.SO10_GENERATOR_COUNT
    column_l01 = g4.GENERATOR_LABELS.index("SO10:T[0,1]")
    sigma_column = matrix[:, column_l01]
    sigma_only = bool(not np.any(np.delete(sigma_column, np.arange(sigma_rows.start, sigma_rows.stop))))

    def multiple_of_sigma_column(column: np.ndarray) -> int | None:
        block, base = column[sigma_rows], sigma_column[sigma_rows]
        index = int(np.flatnonzero(base)[0]) if np.any(base) else None
        if index is None or block[index] % base[index]:
            return None
        factor = int(block[index] // base[index])
        return factor if np.array_equal(block, factor * base) else None

    x_factor = multiple_of_sigma_column(matrix[:, so10])
    pq_factor = multiple_of_sigma_column(matrix[:, so10 + 1])
    metric = hessian.congruence_scale_squared()
    premises = {
        "so10_columns_vanish_on_S_and_Phi17": bool(not np.any(matrix[s_rows, :so10]) and not np.any(matrix[x_rows, :so10])),
        "all_columns_vanish_on_H": bool(not np.any(matrix[h_rows])),
        "SO10_T01_column_supported_on_Sigma_only": sigma_only,
        "X_and_PQ_Sigma_blocks_are_integer_multiples_of_SO10_T01": x_factor is not None and pq_factor is not None,
        "S_and_Phi17_carry_only_the_imaginary_phase_tangent": bool(
            matrix[s_rows.start, so10] == 0 and matrix[s_rows.start, so10 + 1] == 0 and matrix[x_rows.start, so10] == 0
            and matrix[x_rows.start, so10 + 1] == 0
        ),
        "S_and_Phi17_metric_is_2": all(metric[index] == 2 for index in (*range(s_rows.start, s_rows.stop), *range(x_rows.start, x_rows.stop))),
    }
    q_x = {name: int(g4.X_CHARGES[name]) for name in ("S", "Phi17")}
    q_pq = {name: int(g4.PQ_CHARGES[name]) for name in ("S", "Phi17")}
    charges_bound = bool(
        matrix[s_rows.start + 1, so10] == q_x["S"]
        and matrix[x_rows.start + 1, so10] == q_x["Phi17"]
        and matrix[s_rows.start + 1, so10 + 1] == q_pq["S"]
        and matrix[x_rows.start + 1, so10 + 1] == q_pq["Phi17"]
    )
    premises["integer_S_Phi17_phase_entries_equal_X_and_PQ_charges"] = charges_bound
    s, x0 = sympy.symbols("rS x0", positive=True)
    p_vec = sympy.Matrix([q_pq["S"] * s, q_pq["Phi17"] * x0])
    x_vec = sympy.Matrix([q_x["S"] * s, q_x["Phi17"] * x0])
    inner = lambda left, right: 2 * (left.T * right)[0, 0]  # noqa: E731 - metric 2 on S and Phi17
    axion = p_vec - inner(p_vec, x_vec) / inner(x_vec, x_vec) * x_vec
    norm = sympy.factor(sympy.simplify(inner(axion, axion)))
    share_s = sympy.factor(sympy.simplify(2 * axion[0] ** 2 / inner(axion, axion)))
    share_x = sympy.factor(sympy.simplify(2 * axion[1] ** 2 / inner(axion, axion)))
    expected_norm = 9248 * s**2 * x0**2 / (16 * s**2 + 289 * x0**2)
    v_s, v_phi = sympy.sqrt(2) * s, sympy.sqrt(2) * x0
    gev_form = v_s**2 * v_phi**2 / ((4 * v_s) ** 2 + (17 * v_phi) ** 2)
    identities = {
        "F_PQ2_equals_9248_rS2_x0_2_over_16rS2_plus_289x0_2": sympy.simplify(norm - expected_norm) == 0,
        "S_share_equals_289x0_2_over_denominator": sympy.simplify(share_s - 289 * x0**2 / (16 * s**2 + 289 * x0**2)) == 0,
        "Phi17_share_equals_16rS2_over_denominator": sympy.simplify(share_x - 16 * s**2 / (16 * s**2 + 289 * x0**2)) == 0,
        "v_a2_equals_vS2_vPhi2_over_4vS_2_plus_17vPhi_2": sympy.simplify(norm / 68**2 - gev_form) == 0,
    }
    ok = bool(all(premises.values()) and all(identities.values()))
    section = {
        "argument": "t_PQ - b L01 and T_X - a L01 are supported on (Im S, Im Phi17) only; the so(10) tangents vanish "
        "there, so a = s_PQ - (<s_PQ, s_X>/<s_X, s_X>) s_X is the orthogonal projection of t_PQ onto G34^perp with "
        "s_PQ = (q_PQ(S) rS, q_PQ(Phi17) x0), s_X = (q_X(S) rS, q_X(Phi17) x0) in the metric 2",
        "premises_exact_on_integer_matrix": premises,
        "X_and_PQ_Sigma_multiples_of_SO10_T01": {"X": x_factor, "PQ": pq_factor},
        "F_PQ_squared": str(norm),
        "S_share": str(share_s),
        "Phi17_share": str(share_x),
        "Sigma_share": "0",
        "r0_free": not any(symbol.name == "r0" for symbol in norm.free_symbols),
        "GeV_form": "v_a = F_PQ/68 = v_S v_Phi/sqrt((4 v_S)^2 + (17 v_Phi)^2), v_S = sqrt2 rS, v_Phi = sqrt2 x0 (chart "
        "units M_GUT)",
        "identities": identities,
    }
    return section, ok, norm


def g4_committed_comparison(
    g4_report: Mapping[str, Any] | None, record: Mapping[str, Any] | None, gauge: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool]:
    report = load_report(g4.OUT_JSON) if g4_report is None else g4_report
    if record is None or gauge is None:
        return {"compared": False}, False
    fresh = json_roundtrip(
        {
            "axion_norm_squared": record["axion_norm_squared_F_PQ2"],
            "squared_norm_fractions": record["squared_norm_fractions"],
            "v_a_squared": record["v_a_squared"],
            "D_u_minors": {name: gauge["certificates"][name]["minor"]["determinant_D_u_M"] for name in MINOR_NAMES},
            "neutral_terms": record["neutral_block_terms_lambda_t_exponents"],
            "chart_norm": record["chart_vacuum_norm_squared"],
        }
    )
    comparisons = {
        "axion.axion_norm_squared": hessian._get(report, "axion", "axion_norm_squared") == fresh["axion_norm_squared"],
        "axion.squared_norm_fractions": hessian._get(report, "axion", "squared_norm_fractions") == fresh["squared_norm_fractions"],
        "axion.decay_constant.v_a_squared": hessian._get(report, "axion", "decay_constant", "v_a_squared") == fresh["v_a_squared"],
        "gauge_quotient.certificates.*.minor.determinant_D_u_M": all(
            hessian._get(report, "gauge_quotient", "certificates", name, "minor", "determinant_D_u_M") == fresh["D_u_minors"][name]
            for name in MINOR_NAMES
        ),
        "vector_bosons.neutral_block.characteristic_polynomial_terms_lambda_t_exponents": hessian._get(
            report, "vector_bosons", "neutral_block", "characteristic_polynomial_terms_lambda_t_exponents"
        )
        == fresh["neutral_terms"],
        "chart_normalisation.vacuum_norm_squared_chart": hessian._get(report, "chart_normalisation", "vacuum_norm_squared_chart")
        == fresh["chart_norm"],
    }
    return {"source": g4.OUT_JSON.name, "compared": True, "comparisons": comparisons}, all(comparisons.values())


# ---------------------------------------------------------------------------
# Model-file anomaly (checks 70-77).
# ---------------------------------------------------------------------------

_FIELD_PATTERN = r"{kind}\[\[\d+\]\]\s*=\s*\{{(\w+),\s*(\d+),\s*(\w+),\s*(-?\d+),\s*(-?\d+),"


def parse_model(path: Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    fields = {}
    for kind in ("FermionFields", "ScalarFields"):
        fields[kind] = {
            match.group(1): {"generations": int(match.group(2)), "so10_rep": int(match.group(4)), "X": int(match.group(5))}
            for match in re.finditer(_FIELD_PATTERN.format(kind=kind), text)
        }
    terms = []
    if "LagHC = -(" in text:
        body = text.split("LagHC = -(", 1)[1].split(");", 1)[0]
        for line in body.splitlines():
            line = line.strip().lstrip("+").strip()
            if not line:
                continue
            coupling, product = line.split(None, 1)
            factors = []
            for factor in product.split("."):
                factor = factor.strip()
                conjugate = re.fullmatch(r"conj\[(\w+)\]", factor)
                factors.append((conjugate.group(1), -1) if conjugate else (factor, 1))
            terms.append({"coupling": coupling, "factors": factors})
    return {"fermions": fields["FermionFields"], "scalars": fields["ScalarFields"], "LagHC": terms}


def sm_content_indices() -> dict[str, Any]:
    """T_SU3 and Tr Q^2 of one 16 from its SM content (Q = T3 + Y); the 16bar has the same values."""
    t_su3 = Fraction(0)
    trace_q2 = Fraction(0)
    dimension = 0
    for _name, colour, weak, hypercharge in SIXTEEN_SM_CONTENT:
        dimension += colour * weak
        if colour == 3:
            t_su3 += Fraction(1, 2) * weak
        charges = [hypercharge + Fraction(1, 2), hypercharge - Fraction(1, 2)] if weak == 2 else [hypercharge]
        trace_q2 += colour * sum(charge * charge for charge in charges)
    return {"dimension": dimension, "T_SU3": t_su3, "TrQ2": trace_q2}


def _operator_charge(counts: Mapping[str, int], table: Mapping[str, int]) -> int:
    base = {"P": "Phi210", "H": "H10", "D": "Sigma126bar", "S": "S", "X": "Phi17"}
    total = 0
    for letter, name in base.items():
        charge = int(table.get(name, 0))
        total += charge * (int(counts.get(letter, 0)) - int(counts.get(letter + "b", 0)))
    return total


def anomaly_section(
    model_path: Path, pq_charges: Mapping[str, int] | None, period_record: Mapping[str, Any] | None
) -> tuple[dict[str, Any], dict[str, bool]]:
    model = parse_model(model_path)
    fermions, scalars, terms = model["fermions"], model["scalars"], model["LagHC"]
    declared = set(fermions) | set(scalars)
    # The declared representations: the anomaly indices used below are those of a 16/16bar, so a fermion declared in
    # any other representation (or a scalar in an unexpected one) fails closed here.
    fermion_reps = {name: row["so10_rep"] for name, row in fermions.items()}
    scalar_reps = {name: row["so10_rep"] for name, row in scalars.items()}
    reps_ok = bool(
        fermion_reps
        and all(abs(rep) == MODEL_FERMION_ABS_REP for rep in fermion_reps.values())
        and scalar_reps == MODEL_SCALAR_REPS
    )
    parse_ok = bool(
        len(fermions) == 9
        and len(scalars) == 5
        and len(terms) == 11
        and all(field in declared for term in terms for field, _ in term["factors"])
        and set(scalars) == set(MODEL_SCALAR_NAMES)
        and reps_ok
    )
    repo_x = {name: int(value) for name, value in quotient.U1X_CHARGES.items()}
    repo_pq = {name: int(value) for name, value in quotient.PQ_CHARGES.items()}
    pq_table = dict(repo_pq if pq_charges is None else {name: int(value) for name, value in pq_charges.items()})
    x_scalar = {model_name: scalars[model_name]["X"] for model_name in scalars}
    pq_scalar = {model_name: (0 if repo_name == "Phi210" else int(pq_table.get(repo_name, 0))) for model_name, repo_name in MODEL_SCALAR_NAMES.items()}
    scalar_ok = bool(
        all(x_scalar.get(model_name) == (0 if repo_name == "Phi210" else repo_x.get(repo_name)) for model_name, repo_name in MODEL_SCALAR_NAMES.items())
        and pq_table == repo_pq
        and equality.charge_data()["census_charges_consistent"]
    )
    alpha, beta = sympy.symbols("alpha beta")
    unknowns = {name: sympy.Symbol("q_" + name) for name in fermions}
    order = [name for name in fermions if name != "SpecB"] + (["SpecB"] if "SpecB" in fermions else [])
    variables = [unknowns[name] for name in order] + [alpha, beta]
    charge = {name: alpha * x_scalar[name] + beta * pq_scalar.get(name, 0) for name in scalars}
    charge.update(unknowns)
    equations = [sum((sign * charge[field] for field, sign in term["factors"]), sympy.Integer(0)) for term in terms]
    coefficient_matrix = sympy.Matrix([[sympy.diff(equation, variable) for variable in variables] for equation in equations])
    dimension = len(variables) - coefficient_matrix.rank()
    solutions = list(sympy.linsolve(equations, variables))
    general = dict(zip(variables, solutions[0], strict=True)) if len(solutions) == 1 else {}
    free = sorted({symbol for value in general.values() for symbol in sympy.sympify(value).free_symbols}, key=str)
    spectators = [symbol for symbol in free if symbol not in (alpha, beta)]
    indices = sm_content_indices()
    t_su3, trace_q2 = indices["T_SU3"], indices["TrQ2"]

    def n_of(q: Mapping[str, int]) -> Fraction:
        """N = sum_fields generations * T_SU3 * q (integer charges, exact)."""
        return sum((fermions[name]["generations"] * t_su3 * Fraction(int(q[name])) for name in fermions), Fraction(0))

    def e_of(q: Mapping[str, int]) -> Fraction:
        return sum((fermions[name]["generations"] * trace_q2 * Fraction(int(q[name])) for name in fermions), Fraction(0))

    general_fermion = {name: sympy.simplify(general.get(unknowns[name], unknowns[name])) for name in fermions} if general else {}
    n_general = (
        sympy.expand(
            sum(
                (fermions[name]["generations"] * candidate._as_sympy(t_su3) * value for name, value in general_fermion.items()),
                sympy.Integer(0),
            )
        )
        if general
        else None
    )
    # X: alpha = 1, beta = 0, the spectator fixed by SpecB's model charge.
    x_reproduced = False
    x_charges: dict[str, Any] = {}
    if general and len(spectators) == 1 and "SpecB" in fermions:
        at_x = {name: value.subs({alpha: 1, beta: 0}) for name, value in general_fermion.items()}
        spectator_value = sympy.solve(sympy.Eq(at_x["SpecB"], fermions["SpecB"]["X"]), spectators[0])
        if len(spectator_value) == 1:
            values = {name: sympy.nsimplify(value.subs(spectators[0], spectator_value[0])) for name, value in at_x.items()}
            if all(value.is_Integer for value in values.values()):
                x_charges = {name: int(value) for name, value in values.items()}
                x_reproduced = all(x_charges[name] == fermions[name]["X"] for name in fermions)
    model_terms_x_neutral = all(
        sum(sign * (fermions[field]["X"] if field in fermions else scalars[field]["X"]) for field, sign in term["factors"]) == 0
        for term in terms
    )
    model_x = {name: fermions[name]["X"] for name in fermions}
    n_x = n_of(model_x)
    # PQ: alpha = 0, beta = 1, spectator split fixed to the tex choice SpecB = -6 (N does not depend on it).
    pq_charges_fermions: dict[str, Any] = {}
    if general and len(spectators) == 1:
        at_pq = {name: value.subs({alpha: 0, beta: 1}) for name, value in general_fermion.items()}
        split = sympy.solve(sympy.Eq(at_pq.get("SpecB", 0), -6), spectators[0]) if "SpecB" in at_pq else []
        if len(split) == 1:
            values = {name: sympy.nsimplify(value.subs(spectators[0], split[0])) for name, value in at_pq.items()}
            if all(value.is_Integer for value in values.values()):
                pq_charges_fermions = {name: int(value) for name, value in values.items()}
    n_pq = n_of(pq_charges_fermions) if pq_charges_fermions else None
    e_pq = e_of(pq_charges_fermions) if pq_charges_fermions else None
    vs_charges = {name: (1 if name == "SpecS" else -1 if name == "SpecB" else 0) for name in fermions}
    n_vs = n_of(vs_charges)
    n_general_ok = bool(
        n_general is not None
        and sympy.expand(n_general + 34 * beta) == 0
        and not any(symbol in n_general.free_symbols for symbol in spectators)
    )
    heavy_pairs = (
        {pair: pq_charges_fermions[pair[0]] + pq_charges_fermions[pair[1]] for pair in (("P", "Pbar"), ("Q", "Qbar"), ("R", "Rbar"))}
        if pq_charges_fermions
        else {}
    )
    period_denominator = period_record.get("period_denominator") if period_record else None
    element = period_record.get("explicit_gauge_element_units_of_2pi") if period_record else None
    n_dw = abs(2 * n_pq) / period_denominator if (n_pq is not None and period_denominator) else None
    cover = abs(2 * n_pq) / pq_scalar["S"] if (n_pq is not None and pq_scalar.get("S")) else None
    theta_shift = 2 * n_pq / period_denominator if (n_pq is not None and period_denominator) else None
    counts = equality.direction_counts()
    portals = {}
    for label, direction in (("kappaH H10.H10.S (census O12, conjugate Hdag.Hdag.Sdag)", "O12_B01_Hdag_Hdag_pair"), ("O38 Phi Hdag Sigmadag Sdag", "O38_B01_Phi_Hdag_Sigmadag")):
        found = counts.get(direction)
        row = dict(zip(potential.FIELD_ORDER, found, strict=True)) if found is not None else {}
        portals[label] = {
            "field_counts": {key: value for key, value in row.items() if value},
            "X_charge": _operator_charge(row, repo_x),
            "PQ_charge": _operator_charge(row, pq_table),
        }
    kappa_terms = [term for term in terms if term["coupling"] == "kappaH"]
    kappa_model_ok = len(kappa_terms) == 1 and sum(
        sign * (x_scalar[field] if field in x_scalar else 99) for field, sign in kappa_terms[0]["factors"]
    ) == 0 and sum(sign * (pq_scalar[field] if field in pq_scalar else 99) for field, sign in kappa_terms[0]["factors"]) == 0
    checks = {
        "anomaly_model_file_parsed_9_fermion_16s_5_scalars_with_declared_reps_11_LagHC_terms": parse_ok,
        "anomaly_scalar_charges_match_repository_X_and_PQ_tables": scalar_ok,
        "anomaly_global_U1_space_is_3_dimensional_X_PQ_Vs": bool(
            dimension == 3 and general and set(free) == {alpha, beta, *spectators} and len(spectators) == 1
        ),
        "anomaly_model_X_charges_solve_every_LagHC_term_and_N_X_0": bool(x_reproduced and model_terms_x_neutral and n_x == 0),
        "anomaly_N_PQ_minus_34_independent_of_spectator_split": bool(n_general_ok and n_pq == -34 and n_vs == 0 and heavy_pairs and not any(heavy_pairs.values())),
        "anomaly_E_over_N_8_over_3_from_SM_content_of_16": bool(
            indices["dimension"] == 16
            and t_su3 == 2
            and trace_q2 == Fraction(16, 3)
            and e_pq == Fraction(-272, 3)
            and n_pq
            and e_pq / n_pq == Fraction(8, 3)
        ),
        "anomaly_N_DW_1_modulo_gauge_period_2pi_over_68": bool(
            period_denominator == 68 and element is not None and n_dw == 1 and theta_shift == -1 and cover == 17 and n_x == 0
        ),
        "anomaly_contract_kappaH_and_O38_X_and_PQ_neutral": bool(
            portals and all(row["X_charge"] == 0 and row["PQ_charge"] == 0 and row["field_counts"] for row in portals.values())
            and kappa_model_ok
        ),
    }
    section = {
        "model_file": Path(model_path).resolve().relative_to(ROOT).as_posix()
        if Path(model_path).resolve().is_relative_to(ROOT)
        else Path(model_path).name,
        "fermions": fermions,
        "scalars": scalars,
        "declared_representations": {
            "fermions_all_16_or_16bar": bool(fermion_reps)
            and all(abs(rep) == MODEL_FERMION_ABS_REP for rep in fermion_reps.values()),
            "scalars": scalar_reps,
            "scalars_expected": dict(MODEL_SCALAR_REPS),
            "scalars_match": scalar_reps == MODEL_SCALAR_REPS,
            "note": "T_SU3 = 2 and Tr Q^2 = 16/3 are the indices of a 16 (and of a 16bar); they apply only because "
            "every fermion is declared as a 16 or 16bar",
        },
        "LagHC_terms": [term["coupling"] + ": " + ".".join(("conj[%s]" % field) if sign < 0 else field for field, sign in term["factors"]) for term in terms],
        "scalar_charges_X_model_PQ_repository": {name: {"X": x_scalar.get(name), "PQ": pq_scalar.get(name)} for name in MODEL_SCALAR_NAMES},
        "PQ_table_equals_repository": pq_table == repo_pq,
        "general_global_U1": {
            "unknowns": [str(variable) for variable in variables],
            "solution_space_dimension": dimension,
            "free_parameters": [str(symbol) for symbol in free],
            "fermion_charges": {name: str(value) for name, value in general_fermion.items()},
            "N_SU3_general": str(n_general) if n_general is not None else None,
        },
        "SM_content_of_16": {"content": [list(row) for row in SIXTEEN_SM_CONTENT], **indices},
        "X": {"charges": x_charges, "reproduces_model_file": x_reproduced, "every_LagHC_term_X_neutral": model_terms_x_neutral, "N": n_x},
        "PQ": {
            "charges_with_spectator_split_SpecS_2_SpecB_minus_6": pq_charges_fermions,
            "spectator_split": "free (SpecS + SpecB = -4 per generation under PQ); N does not depend on it",
            "N": n_pq,
            "2N": 2 * n_pq if n_pq is not None else None,
            "E": e_pq,
            "E_over_N": e_pq / n_pq if (n_pq and e_pq is not None) else None,
            "heavy_vectorlike_pairs_PQ_sums": {f"{a}+{b}": value for (a, b), value in heavy_pairs.items()},
        },
        "V_s": {"charges": vs_charges, "N": n_vs},
        "domain_wall": {
            "period_denominator_from_G4_period_certificate_at_rS_1": period_denominator,
            "explicit_gauge_element_units_of_2pi": element,
            "theta_QCD_shift_over_one_period_units_of_2pi": theta_shift,
            "N_DW_modulo_gauge": n_dw,
            "N_DW_cover_relative_to_S_phase": cover,
            "gauge_part_anomaly_free": n_x == 0,
            "f_a": "f_a = v_a/N_DW = v_a = F_PQ/68",
        },
        "contract_portals": portals,
        "caveats": list(ANOMALY_CAVEATS),
    }
    return section, checks


# ---------------------------------------------------------------------------
# FLOAT64 corroboration (outside the exact check count).
# ---------------------------------------------------------------------------


def _live_rows(state: Any, coefficients: Mapping[str, float]) -> dict[str, Any]:
    needed = candidate.needed_direction_ids(coefficients)
    return target.parameter_rows(state, include=lambda direction: direction.direction_id in needed)


def float_evidence_section() -> dict[str, Any]:
    started = time.time()
    output: dict[str, Any] = {"run": True, "label": "FLOAT64 corroboration outside the exact check count"}
    checks: dict[str, bool] = {}
    # F1: the live compiler at (1/5, 1, 1, -1/100) against the exact Hessian.
    t0 = time.time()
    point = P(R0, Fraction(1), X0, Fraction(-1, 100))
    tuned = candidate.float_coefficients(family_coefficients(point))
    raised = candidate.float_coefficients(family_coefficients(point, hessian.variant_offset("raised_O06", point)))
    rows = _live_rows(candidate.candidate_state(R0, X0, rs=point.rs), tuned)
    f1 = {"point": _point_dict(point)}
    v0 = float(candidate.lower_bound_v0(R0, X0, rs=point.rs))
    for variant, coefficients in (("benchmark", tuned), ("raised_O06", raised)):
        value, gradient, hessian_q = target.assemble(rows, coefficients)
        exact = hessian.exact_hessian(variant, point=point)
        comparison = hessian.compare_live(hessian_q, gradient, exact["hessian"], exact["gradient"])
        f1[variant] = {
            "V_minus_V0": value - v0,
            "max_abs_hessian_difference": comparison["max_abs_exact_minus_live_chart_hessian"],
            "max_abs_gradient_difference": comparison["max_abs_exact_minus_live_gradient"],
            "within_tolerance": comparison["within_tolerance"],
            "lattice_passes": comparison["lattice"]["passes"],
            "half_lattice_margin": comparison["lattice"]["half_lattice_margin"],
        }
    _clear_point_caches()
    f1["seconds"] = time.time() - t0
    checks[FLOAT_CHECK_NAMES[0]] = all(f1[variant]["within_tolerance"] for variant in ("benchmark", "raised_O06"))
    checks[FLOAT_CHECK_NAMES[1]] = all(
        f1[variant]["lattice_passes"] and abs(f1[variant]["V_minus_V0"]) <= FLOAT_TOLERANCE for variant in ("benchmark", "raised_O06")
    )
    output["F1_live_compiler_at_rS_1_kappa_minus_1_over_100"] = f1
    # F2: compiler point audit at the hierarchy anchor with rS = 1000 r0.
    t0 = time.time()
    r0 = candidate.hierarchy_anchor()["r0_physical"]
    anchor = P(r0, 1000 * r0, X0, -r0 * r0 / (4 * 1000 * r0))
    anchor_tuned = candidate.float_coefficients(family_coefficients(anchor))
    anchor_raised = candidate.float_coefficients(family_coefficients(anchor, r0 * r0 / 100))
    state = candidate.candidate_state(anchor.r0, anchor.x0, rs=anchor.rs)
    anchor_rows = _live_rows(state, anchor_tuned)
    value, gradient, hessian_q = target.assemble(anchor_rows, anchor_tuned)
    _, _, hessian_raised = target.assemble(anchor_rows, anchor_raised)
    symmetry, ranks = candidate.symmetry_matrix(state)
    _, complement = candidate._split(symmetry, ranks["so10_plus_u1x_plus_pq_rank"])
    lightest = float(anchor.r0) ** 2 / 96
    tolerance = 1.0e-3 * lightest
    eigenvalues = np.linalg.eigvalsh(0.5 * (complement.T @ hessian_q @ complement + (complement.T @ hessian_q @ complement).T))
    raised_eigenvalues = np.linalg.eigvalsh(
        0.5 * (complement.T @ hessian_raised @ complement + (complement.T @ hessian_raised @ complement).T)
    )
    massive = eigenvalues[eigenvalues > tolerance]
    anchor_v0 = float(candidate.lower_bound_v0(anchor.r0, anchor.x0, rs=anchor.rs))
    # Scale-aware tolerances (|V0| ~ 1 + rS^4, S-block gradient terms ~ 4 rS^3); both are 1e-12 at this anchor.
    v_tolerance = FLOAT_TOLERANCE * max(1.0, abs(anchor_v0))
    gradient_tolerance = FLOAT_TOLERANCE * max(1.0, 4.0 * float(anchor.rs) ** 3)
    f2 = {
        "point": _point_dict(anchor),
        "rS_over_r0": 1000,
        "V_minus_V0": value - anchor_v0,
        "V0": anchor_v0,
        "V_tolerance": v_tolerance,
        "max_abs_gradient": float(np.max(np.abs(gradient))),
        "gradient_tolerance": gradient_tolerance,
        "tolerance_rule": "|V - V0| <= 1e-12 max(1, |V0|) and max|grad| <= 1e-12 max(1, 4 rS^3) (the S-block gradient "
        "terms are ~ 4 rS^3)",
        "symmetry_ranks": ranks,
        "projected_negative": int(np.sum(eigenvalues < -tolerance)),
        "projected_zero": int(np.sum(np.abs(eigenvalues) <= tolerance)),
        "lightest_massive_over_r0sq_over_96": float(massive[0]) / lightest if massive.size else None,
        "raised_variant_negative": int(np.sum(raised_eigenvalues < -tolerance)),
        "raised_variant_zero": int(np.sum(np.abs(raised_eigenvalues) <= tolerance)),
        "note": "float64 cannot classify minimisation endpoints at the hierarchy anchor (r0 = M_I/M_GUT ~ 6.4e-5, rS = "
        "1000 r0 ~ 0.064: the endpoint convergence threshold (1e-2 r0^2)^2/96 ~ 2e-23 falls below the float floor "
        "of V - V0 ~ 1e-14 at |V0| ~ 1.03), so rS/r0 = 1000 is covered by this point audit",
    }
    f2["seconds"] = time.time() - t0
    checks[FLOAT_CHECK_NAMES[2]] = bool(f2["max_abs_gradient"] <= gradient_tolerance and abs(f2["V_minus_V0"]) <= v_tolerance)
    checks[FLOAT_CHECK_NAMES[3]] = bool(
        [ranks.get("so10_orbit_rank"), ranks.get("so10_plus_u1x_rank"), ranks.get("so10_plus_u1x_plus_pq_rank")] == [33, 34, 35]
        and f2["projected_negative"] == 0
        and f2["projected_zero"] == candidate.LIGHT_DOUBLET_REAL_DIMENSION
    )
    checks[FLOAT_CHECK_NAMES[4]] = bool(
        f2["lightest_massive_over_r0sq_over_96"] is not None
        and abs(f2["lightest_massive_over_r0sq_over_96"] - 1.0) <= 1.0e-2
        and f2["raised_variant_negative"] == 0
        and f2["raised_variant_zero"] == 0
    )
    output["F2_anchor_rS_1000_r0"] = f2
    # F3: the violating direction at (1/5, 1, 1, kappa = -3).
    t0 = time.time()
    rs, kappa, step = SHARPNESS_WITNESSES[0]
    violating = candidate.float_coefficients(family_coefficients(P(R0, rs, X0, kappa)))
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = math.sqrt(float(abs(kappa) * step / 2))
    q = chart.pack(candidate.candidate_state(R0, X0, h=h, rs=rs + step))
    compiler = candidate.compiler_value(q, violating) - float(candidate.lower_bound_v0(R0, X0, rs=rs))
    f3 = {
        "rS": rs,
        "kappa": kappa,
        "t": step,
        "compiler_V_minus_V0": compiler,
        "exact": SHARPNESS_VALUES[0],
        "difference": compiler - float(SHARPNESS_VALUES[0]),
        "seconds": time.time() - t0,
    }
    checks[FLOAT_CHECK_NAMES[5]] = bool(abs(f3["difference"]) <= FLOAT_TOLERANCE)
    output["F3_violating_direction"] = f3
    # F4: the rS-aware fast evaluator and two endpoints at (1/5, 1, 1, -1/100).
    t0 = time.time()
    exact_map = family_coefficients(point)
    fast = candidate.SosFormPotential(R0, X0, point.kappa, exact_map[O06], rs=point.rs)
    rng = np.random.default_rng(FLOAT_SEED)
    relative = []
    for _ in range(3):
        sample = rng.normal(size=chart.TOTAL_DIM) * rng.uniform(0.05, 1.0)
        reference = candidate.compiler_value(sample, tuned)
        relative.append(abs(reference - fast.value(sample)) / max(1.0, abs(reference)))
    endpoints = []
    for kind in ("generic", "phi_near_p"):
        start = candidate.random_start(kind, rng, float(R0), float(X0), rs=float(point.rs))
        final, result = candidate.local_minimize(fast, start)
        gap = fast.value(final) - v0
        endpoint = candidate.classify_endpoint(fast, final, float(R0), float(X0), gap=gap, rs=float(point.rs))
        endpoints.append(
            {
                "kind": kind,
                "gap": gap,
                "classification": endpoint["orbit_classification"],
                "S_abs_over_rS": endpoint["invariants"]["S_abs"] / float(point.rs),
                "iterations": int(result.nit),
            }
        )
    classes = [row["classification"] for row in endpoints]
    f4 = {
        "point": _point_dict(point),
        "max_relative_fast_minus_compiler": max(relative),
        "endpoints": endpoints,
        "on_orbit": classes.count("on_orbit"),
        "inconclusive": classes.count("inconclusive"),
        "off_orbit": classes.count("off_orbit"),
        "seconds": time.time() - t0,
    }
    checks[FLOAT_CHECK_NAMES[6]] = bool(f4["max_relative_fast_minus_compiler"] <= FLOAT_TOLERANCE)
    checks[FLOAT_CHECK_NAMES[7]] = bool(f4["off_orbit"] == 0 and f4["on_orbit"] >= 1)
    output["F4_fast_evaluator_and_endpoints"] = f4
    failures = [name for name, passed in checks.items() if not passed]
    output.update({"checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures})
    output["seconds"] = time.time() - started
    return output


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def build_report(
    *,
    numerical: bool = True,
    points: Sequence[tuple[str, Any]] | None = None,
    rank_rs: Sequence[Any] | None = None,
    g4_rs: Sequence[Any] | None = None,
    hs_points: Sequence[tuple[Any, ...]] | None = None,
    equality_report: Mapping[str, Any] | None = None,
    hessian_report: Mapping[str, Any] | None = None,
    g4_report: Mapping[str, Any] | None = None,
    model_path: Path | None = None,
    pq_charges: Mapping[str, int] | None = None,
    self_weights: Mapping[str, Fraction] | None = None,
    expected_n_checks: int | None = None,
) -> dict[str, Any]:
    """Build the status-neutral family certificate.  Every keyword except ``numerical`` exists for mutation tests:
    reduced or modified point sets, committed reports, the model file, the PQ table, the SOS self weights and the
    expected check count.  With the default point sets the check count must equal EXPECTED_N_CHECKS (or
    ``expected_n_checks`` when given); otherwise the report fails closed with CHECK_COUNT_FAILURE."""
    started = time.time()
    default_sets = points is None and rank_rs is None and g4_rs is None and hs_points is None
    count_target = expected_n_checks if expected_n_checks is not None else (EXPECTED_N_CHECKS if default_sets else None)
    point_list = [(label, hessian.as_singlet_point(point)) for label, point in (HESSIAN_POINTS if points is None else points)]
    rank_values = [Fraction(value) for value in (RANK_RS if rank_rs is None else rank_rs)]
    g4_values = [Fraction(value) for value in (G4_RS if g4_rs is None else g4_rs)]
    hs_list = list(HS_POINTS if hs_points is None else hs_points)
    weights = dict(candidate.SWAPPED_SELF_WEIGHTS if self_weights is None else self_weights)
    checks: dict[str, bool] = {}

    family, family_checks = family_section(point_list)
    checks.update(family_checks)
    sos, sos_checks = sos_section(point_list, weights)
    checks.update(sos_checks)
    hs, hs_checks = hs_section(point_list, hs_list)
    checks.update({key: hs_checks[key] for key in hs_checks if not key.startswith("p3_family_")})
    checks.update({key: hs_checks[key] for key in hs_checks if key.startswith("p3_family_")})
    equality_part, equality_checks = equality_section(point_list, equality_report)
    checks.update(equality_checks)

    # G4 geometry at every rS needed (computed once per rS inside this call; nothing rS-dependent is cached).
    matrix = g4.tangent_matrix()
    contract = g4.contract_premises(g4.load_report(g4.CONTRACT_JSON))
    needed_rs = sorted(set(rank_values) | set(g4_values) | {p.rs for _, p in point_list} | {R0})
    gauge_sections = {rs: g4.gauge_quotient_section(matrix, contract, rs=rs) for rs in needed_rs}
    g4_records: dict[Fraction, dict[str, Any]] = {}
    g4_checks: dict[str, bool] = {}
    axions: dict[Fraction, tuple[np.ndarray, int]] = {}
    for rs in needed_rs:
        record, rs_checks, axion_vector = g4_rs_section(rs, matrix, gauge_sections[rs])
        g4_records[rs] = record
        axions[rs] = axion_vector
        if rs in g4_values:
            g4_checks.update(rs_checks)

    # Exact Hessians: the witness (default path), the rS = r0 regression, then each family point.
    witness = {variant: hessian.exact_hessian(variant) for variant in VARIANTS}
    witness_certificates = {variant: hessian.exact_certificate(variant) for variant in VARIANTS}
    regression, regression_ok = rs_eq_r0_regression()
    point_records = {}
    for label, point in point_list:
        record, point_checks = hessian_point_section(label, point, witness, axions[point.rs])
        point_records[label] = record
        for suffix in POINT_CHECK_SUFFIXES:
            checks[f"point_{label}__{suffix}"] = bool(point_checks[suffix])
        _clear_point_caches()
    keeps = point_records.get(KEEPS_H_BLOCK_LABEL)
    witness_o06 = candidate.candidate_coefficients(R0, X0)[O06]
    keeps_ok = bool(
        keeps is not None
        and family["points"].get(KEEPS_H_BLOCK_LABEL, {}).get("O06") == witness_o06
        and keeps["H_block_equal_to_witness_all_variants"]
        and all(rows == [["S", "S"]] for rows in keeps["difference_support_vs_witness"].values())
    )
    binding, binding_ok = committed_hessian_binding(hessian_report, witness_certificates)
    checks["rS_eq_r0_hessians_and_certificates_identical_to_witness_module"] = regression_ok
    checks["kappa_minus_r0sq_over_4rS_point_keeps_witness_O06_and_H_block"] = keeps_ok
    checks["committed_exact_hessian_report_certified_and_equal_to_rS_eq_r0_certificates"] = binding_ok
    checks["axion_in_kernel_of_eps_member_hessian_at_every_point"] = bool(point_records) and all(
        record["axion_in_kernel_of_raised_hessian"] for record in point_records.values()
    )

    ranks, rank_checks = tangent_rank_section(rank_values, gauge_sections)
    checks.update(rank_checks)
    checks.update({key: value for key, value in g4_checks.items() if key.startswith("g4_axion_")})
    checks.update({key: value for key, value in g4_checks.items() if key.startswith("g4_vectors_")})
    route_a, route_a_ok, route_a_norm = route_a_symbolic(matrix)
    route_b_agree = {}
    for rs in g4_values:
        at_rs = route_a_norm.subs(
            {sympy.Symbol("rS", positive=True): candidate._as_sympy(rs), sympy.Symbol("x0", positive=True): candidate._as_sympy(X0)}
        )
        route_b_agree[f"rS={rs}"] = bool(sympy.simplify(at_rs - candidate._as_sympy(g4_records[rs]["axion_norm_squared_F_PQ2"])) == 0)
    route_a["route_B_agreement_by_rS"] = route_b_agree
    checks["g4_axion_route_A_symbolic_closed_form_all_rS"] = bool(route_a_ok and route_b_agree and all(route_b_agree.values()))
    committed_g4, committed_g4_ok = g4_committed_comparison(g4_report, g4_records.get(R0), gauge_sections.get(R0))
    checks["g4_rS_eq_r0_values_equal_committed_G4_report"] = committed_g4_ok

    period_rs = Fraction(1) if Fraction(1) in g4_records else needed_rs[-1]
    period_record = {
        "rS": period_rs,
        "period_denominator": g4_records[period_rs]["axion_period_denominator"],
        "explicit_gauge_element_units_of_2pi": g4_records[period_rs]["period_element_units_of_2pi"],
    }
    anomaly, anomaly_checks = anomaly_section(MODEL_FILE if model_path is None else Path(model_path), pq_charges, period_record)
    checks.update(anomaly_checks)

    failures = [name for name, passed in checks.items() if not passed]
    if count_target is not None and len(checks) != count_target:
        failures.append(CHECK_COUNT_FAILURE)
    exact_ok = not failures
    float_evidence = float_evidence_section() if numerical else {"run": False, "label": "FLOAT64 corroboration outside the exact check count", "reason": "--no-numerics"}
    float_ok = bool(numerical and float_evidence.get("n_failed") == 0 and float_evidence.get("n_checks") == EXPECTED_N_FLOAT_CHECKS)
    certified = bool(exact_ok and (not numerical or float_ok))
    flags = {
        "family_theorem_claimed": exact_ok,
        "float_evidence_run": bool(numerical),
        "float_evidence_consistent": float_ok,
        "rS_eq_r0_reproduces_committed_witness": bool(exact_ok and regression_ok and binding_ok and committed_g4_ok),
        "kappa_minus_r0sq_over_4rS_keeps_witness_H_block": bool(exact_ok and keeps_ok),
        "kappa_bound_sharp": bool(
            exact_ok
            and checks.get("kappa_bound_sharp_curve_identity_exact")
            and checks.get("kappa_bound_violated_beyond_boundary_at_exact_rational_witnesses")
        ),
        "anomaly_N_DW_1_modulo_gauge": bool(exact_ok and checks.get("anomaly_N_DW_1_modulo_gauge_period_2pi_over_68")),
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
        "flags": flags,
        "family": family,
        "sos_identity": sos,
        "hs_sector": hs,
        "equality_set": equality_part,
        "exact_hessian_points": point_records,
        "rS_eq_r0_regression": regression,
        "committed_hessian_binding": binding,
        "tangent_ranks": ranks,
        "g4_axion_and_vectors": {
            **{f"rS={rs}": g4_records[rs] for rs in g4_values},
            "route_A_symbolic": route_a,
            "rS_eq_r0_vs_committed_G4": committed_g4,
        },
        "anomaly": anomaly,
        "float_evidence": float_evidence,
        "float_verdict": "",
        "scope": {
            "proved_exactly": [
                "the family coefficient map (symbolic): only O04 = -2 rS^2 and O06 = 2|kappa| rS + eps change; 27 "
                "parameters inside the 51-parameter contract; no S portal; V0 and lambda_eff closed forms",
                "the eight-term SOS identity with T6 at rS and T9 = eps N_H for kappa < 0, > 0 and = 0, and the "
                "sharpness of kappa^2 < 8 rS^2 (exact curve identity and rational violating points beyond it) and the "
                "boundary kappa^2 = 8 rS^2 (exact completed square: the bound and the equality set still hold there, "
                "lambda_eff = 0; elementary sign argument as in P3)",
                "P3 at rS (bracket algebra, charges, phases, operator neutrality, integer tangent ranks) at the HS "
                "points",
                "exact 486 x 486 Hessians over Q at the four family points (tuned 447/39/0, eps members 451/35/0, "
                "gaps, H/S blocks), the rS = r0 point identical to the committed witness; the rS = 5 point is a "
                "stress point outside the |c| < 12 perturbative box (empty eps window), an exact member only",
                "tangent ranks 33/34/35 and the SM stabilizer at rS in {1/10, 1/5, 1, 2}; the G4 axion (F_PQ^2, "
                "composition, period 2 pi/68) and vector/chart sections at rS in {1/10, 1/5, 1, 2, 5}; route A for "
                "all rS",
                "the model-file anomaly (declared representations checked): N_X = 0, N_PQ = -34, E/N = 8/3, N_DW = 1 "
                "modulo gauge",
            ],
            "relies_on_committed": [
                "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; P1/P2 contain no S and carry over verbatim)",
                "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to this report's rS = r0 certificates)",
                "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json (equal to this report's rS = r0 G4 values)",
                "GAUGED_U1X_SCALAR_CONTRACT_V20.json (gauge SO(10) x U(1)_X, accidental global PQ)",
                "models/SO10Z17AxionV20.m (fermion content, X charges, Yukawa/portal terms)",
            ],
            "float64_evidence_only": [
                "the live compiler Hessian and gradient at (1/5, 1, 1, -1/100) against the exact one (F1)",
                "the compiler point audit at the hierarchy anchor with rS = 1000 r0 (F2)",
                "the compiler value along the violating direction (F3)",
                "the rS-aware fast evaluator and minimisation endpoints at (1/5, 1, 1, -1/100) (F4)",
            ],
            "not_proved_or_out_of_scope": [
                "a member with a nonzero S portal (O22, O26, O34, O38, O43): not certified; the S portals stay 0",
                "the G6 tree spectrum and G8 flavour no-go re-pins at a decoupled point (roadmap PR 3)",
                "two-loop running with y_s, the reduced-Planck Landau criterion, and v_R / f_a / m_a numbers (roadmap "
                "PR 4, research)",
                "the committed exact Hessian report's flags.other_r0_x0_kappa_certified stays False: the family "
                "certificates live only in this report",
                "no manuscript change",
            ],
            "status_neutrality": STATUS_NEUTRALITY,
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
            "FAIL-CLOSED: the decoupled-singlet family certificate is NOT claimed (failed: " + ", ".join(report["failures"])
            + ").  No gate is affected: this report is status-neutral."
        )
    points = report["exact_hessian_points"]
    return (
        f"Exact over Q ({report['n_checks']} checks): the committed SM Pati-Salam map with |S| = rS independent of r0 "
        "changes only O04 = -2 rS^2 and O06 = 2|kappa| rS + eps; the eight-term SOS identity holds for every kappa^2 < "
        "8 rS^2 and eps >= 0, so V >= V0 = -1 - r0^4/8 - rS^4 - x0^4/32 with {V = V0} = G.(p, r0 sigma_std, 0, rS, x0) "
        "(sharp: V >= V0 fails for every kappa^2 > 8 rS^2; at kappa^2 = 8 rS^2 it still holds with lambda_eff = 0); "
        f"the exact 486 x 486 Hessian at {len(points)} points is 447/39/0 at eps = 0 and 451/35/0 at eps > 0 (kernel "
        "T35; the rS = 5 point is a stress point outside the |c| < 12 perturbative box with an empty eps window), "
        "identical to the committed witness at rS = r0; the orbit ranks stay 33/34/35; F_PQ^2 = 9248 rS^2 "
        "x0^2/(16 rS^2 + 289 x0^2) with no Sigma share; the model file gives N = -34, E/N = 8/3 and N_DW = 1 modulo "
        "gauge.  Status-neutral: no benchmark is chosen, G3 and G4 stay closed on the committed rS = r0 witness, and "
        "the physics viability of decoupling (y_s, the Landau criterion, v_R/f_a/m_a) is open research; m_a = 153.5 "
        "ueV is not a prediction of the family."
    )


def _float_verdict(report: Mapping[str, Any]) -> str:
    evidence = report["float_evidence"]
    if not evidence.get("run"):
        return "FLOAT64 corroboration not run (--no-numerics); the exact verdict does not depend on it."
    if evidence.get("n_failed"):
        return "FLOAT64 corroboration FAILED (" + ", ".join(evidence["failures"]) + "); the report is not certified."
    return (
        f"FLOAT64 corroboration, outside the exact check count: {evidence['n_checks']}/{evidence['n_checks']} passed "
        "(live compiler at (1/5, 1, 1, -1/100), anchor point audit at rS = 1000 r0, violating direction, endpoints)."
    )


def report_passes(report: Mapping[str, Any]) -> bool:
    """Certified, nothing failed, and the pinned check count (main writes only when this holds)."""
    return bool(
        report.get("n_failed") == 0
        and report.get("status") == STATUS_CERTIFIED
        and report.get("n_checks") == EXPECTED_N_CHECKS
        and len(report.get("checks", {})) == EXPECTED_N_CHECKS
    )


def _ordered(mapping: Mapping[str, Any], preferred: Sequence[str] | Mapping[str, Any]) -> list[str]:
    """Keys of ``mapping`` in the ``preferred`` order first, then the rest sorted."""
    first = [key for key in preferred if key in mapping]
    return first + sorted(key for key in mapping if key not in first)


def _cell(value: Any) -> str:
    return "`" + str(value).replace("|", "\\|") + "`"


def _markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# G3 SM Pati-Salam decoupled singlet family -- v20",
        "",
        f"**Status:** `{report['status']}` (`{report['overall_state']}`)",
        "",
        f"**Theorem claimed:** `{report['theorem_claimed']}`",
        "",
        "## Theorem",
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
        "## Family points",
        "",
        "| label | (r0, rS, x0, kappa) | O04 | O06 | O12 | V0 | lambda_eff | eps window upper | perturbative member | "
        "tuned / raised / tiny inertia | gap tuned (mult) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    point_order = [label for label, _ in HESSIAN_POINTS]
    for label in _ordered(report["family"]["points"], point_order):
        row = report["family"]["points"][label]
        point = row["point"]
        hess = report["exact_hessian_points"].get(label, {}).get("certificates", {})
        inertia = " / ".join(hess.get(variant, {}).get("inertia_positive_zero_negative", "-") for variant in VARIANTS)
        bench = hess.get("benchmark", {})
        box = row["perturbative_box"]
        lines.append(
            f"| {label} | `({point['r0']}, {point['rS']}, {point['x0']}, {point['kappa']})` | `{row['O04']}` | `{row['O06']}` | "
            f"`{row['O12']}` | `{row['V0']}` | `{row['lambda_eff']}` | `{box['eps_window_upper_exclusive']}` | "
            f"`{box['perturbative_member']}` | `{inertia}` | `{bench.get('smallest_nonzero_eigenvalue')}` "
            f"(`{bench.get('multiplicity')}`) |"
        )
    lines += [
        "",
        "## H and S blocks (eps = 0)",
        "",
        "| label | H chart curvatures (value: count) | S u-block | S radial mass^2 | difference vs witness |",
        "|---|---|---|---|---|",
    ]
    for label in _ordered(report["exact_hessian_points"], point_order):
        record = report["exact_hessian_points"][label]
        blocks = record["H_and_S_blocks"]["benchmark"]
        support = sorted({"/".join(pair) for rows in record["difference_support_vs_witness"].values() for pair in rows})
        lines.append(
            f"| {label} | {_cell(blocks['H_chart_curvatures_by_value'])} | {_cell(blocks['S_u_block'])} | "
            f"`{blocks['S_radial_chart_mass_squared']}` | `{', '.join(support) or 'none'}` |"
        )
    lines += [
        "",
        "## G4 axion, vectors and chart norm by rS",
        "",
        "| rS | F_PQ^2 | S share | Phi17 share | v_a^2 | D_u minors (SO10, +X, +PQ) | chart norm^2 |",
        "|---|---|---|---|---|---|---|",
    ]
    g4_part = report["g4_axion_and_vectors"]
    for key in sorted((key for key in g4_part if key.startswith("rS=")), key=lambda text: Fraction(text[3:])):
        row = g4_part[key]
        minors = ", ".join(str(row["D_u_minor_determinants"][name]) for name in MINOR_NAMES)
        lines.append(
            f"| `{key[3:]}` | `{row['axion_norm_squared_F_PQ2']}` | `{row['squared_norm_fractions']['S']}` | "
            f"`{row['squared_norm_fractions']['Phi17']}` | `{row['v_a_squared']}` | `{minors}` | `{row['chart_vacuum_norm_squared']}` |"
        )
    route_a = g4_part["route_A_symbolic"]
    lines += [
        "",
        f"Route A (symbolic, all rS): F_PQ^2 = `{route_a['F_PQ_squared']}`, S share `{route_a['S_share']}`, Phi17 share "
        f"`{route_a['Phi17_share']}`; {route_a['GeV_form']}.",
        "",
        "## Model-file anomaly",
        "",
        "| quantity | value |",
        "|---|---|",
    ]
    anomaly = report["anomaly"]
    rows = [
        ("N_X", anomaly["X"]["N"]),
        ("N_PQ", anomaly["PQ"]["N"]),
        ("2N", anomaly["PQ"]["2N"]),
        ("E_PQ", anomaly["PQ"]["E"]),
        ("E/N", anomaly["PQ"]["E_over_N"]),
        ("N_Vs", anomaly["V_s"]["N"]),
        ("global U(1) dimension", anomaly["general_global_U1"]["solution_space_dimension"]),
        ("general N_SU3", anomaly["general_global_U1"]["N_SU3_general"]),
        ("axion period modulo gauge", "2 pi/%s" % anomaly["domain_wall"]["period_denominator_from_G4_period_certificate_at_rS_1"]),
        ("N_DW modulo gauge", anomaly["domain_wall"]["N_DW_modulo_gauge"]),
        ("N_DW cover (S phase)", anomaly["domain_wall"]["N_DW_cover_relative_to_S_phase"]),
    ]
    lines += [f"| {name} | `{value}` |" for name, value in rows]
    lines += ["", "Caveats:", ""] + [f"- {text}" for text in anomaly["caveats"]]
    evidence = report["float_evidence"]
    lines += ["", "## FLOAT64 evidence (outside the exact check count)", ""]
    if evidence.get("run"):
        f1 = evidence["F1_live_compiler_at_rS_1_kappa_minus_1_over_100"]
        f2 = evidence["F2_anchor_rS_1000_r0"]
        f3 = evidence["F3_violating_direction"]
        f4 = evidence["F4_fast_evaluator_and_endpoints"]
        lines += [
            "| item | FLOAT64 value |",
            "|---|---|",
            f"| F1 max abs Hessian difference (tuned / raised) | `{f1['benchmark']['max_abs_hessian_difference']}` / "
            f"`{f1['raised_O06']['max_abs_hessian_difference']}` |",
            f"| F1 V - V0 (tuned) | `{f1['benchmark']['V_minus_V0']}` |",
            f"| F2 anchor rS = 1000 r0: max abs gradient (tolerance), V - V0 (tolerance) | `{f2['max_abs_gradient']}` "
            f"(`{f2['gradient_tolerance']}`), `{f2['V_minus_V0']}` (`{f2['V_tolerance']}`) |",
            f"| F2 projected negative / zero; lightest / (r0^2/96) | `{f2['projected_negative']}` / `{f2['projected_zero']}`; "
            f"`{f2['lightest_massive_over_r0sq_over_96']}` |",
            f"| F3 compiler minus exact | `{f3['difference']}` |",
            f"| F4 fast evaluator relative difference | `{f4['max_relative_fast_minus_compiler']}` |",
            f"| F4 endpoints on / inconclusive / off orbit | `{f4['on_orbit']}` / `{f4['inconclusive']}` / `{f4['off_orbit']}` |",
            "",
        ]
        lines += ["| FLOAT64 check | passed |", "|---|---|"]
        lines += [f"| `{name}` | `{value}` |" for name, value in evidence["checks"].items()]
    else:
        lines.append("not run (--no-numerics)")
    lines += ["", "## Checks", "", "| check | passed |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
    lines += ["", "## Scope", ""]
    for key in ("proved_exactly", "relies_on_committed", "float64_evidence_only", "not_proved_or_out_of_scope"):
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
