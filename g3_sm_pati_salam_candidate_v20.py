#!/usr/bin/env python3
"""Standard-Model Pati-Salam G3 candidate of the exact-X potential (v20).

The historical G3 candidates put the 126bar vev along
``direct_phi_h_sigmabar_tensor_v20.delta_r()`` = z1^z2^z3^(e67+e89), the
T3R = 0, Y = -1 member of the (10bar,1,3) triplet, so their vacua are not
Standard-Model vacua (g3_sigma_hypercharge_audit_v20).  This module records a
27-parameter member of the declared 51-parameter exact-X potential whose
vacuum is along the Y = 0 SM singlet sigma_std = z1^z2^z3^z4^z5
(z_k = e_{2k-2} + i e_{2k-1}; unit kinetic norm, raw chart norm^2 16):

    (Phi, Sigma, H, S, Phi17) = (p, r0 sigma_std, 0, r0, x0).

The coefficient map is the historical p-branch map of
``gauged_u1x_g3_sos_candidate_v20`` at h = 0 with four changes: the 126bar
self-projector weights of 2772bar and 4125 are swapped (O27_B03 17/128 -> 1/8,
O27_B04 1/8 -> 17/128), O05 = (1/8)(4 - 2 r0^2), and the SARAH kappa_H term
H.H S (census orbit O12) with O06 = 2|kappa| r0 (default kappa = -r0/4, which
leaves exactly one tree-level massless electroweak doublet).

What is proved here, and how:

* SM embedding (exact integers).  g3_sigma_hypercharge_audit_v20 gives the
  stabilizer of (p, sigma_std) in so(10): dimension 12, one-dimensional centre
  proportional to the standard hypercharge (|q| = 1/3 on six, 1/2 on four real
  directions of the 10), derived algebra su(3)+su(2)_L, containing the
  standard SM basis.  Phi = p alone leaves Pati-Salam, so the chain is
  SO(10) -> PS at M_GUT -> SM at r0 M_GUT = M_I (chart units: |Phi| = 1 is
  called M_GUT and r0 M_GUT is called M_I, without gauge-coupling factors).
* Exact lower bound attained (global minimum).  The repository's exact SOS27
  identity (exact_gauged_u1x_g3_sos_bfb_stationarity_v20) is adapted: with the
  swapped weights (2, 2, 1, 17/16) >= 1 the self-projector sum is >= N^2 and
  N^2 - 2 r0^2 N >= -r0^4; the H/S sector 2 N_H^2 + 2|k| r0 N_H + 2k Re(H.H S)
  + (|S|^2 - r0^2)^2 is >= 0 whenever k^2 < 8 r0^2 (equivalently lambda_eff >
  0; Cauchy-Schwarz plus a square in N_H, sharp: k^2 <= 8 r0^2 is necessary).
  Hence V >= V0 = -1 - r0^4/8 - r0^4 - x0^4/32 on the whole 486-real field
  space.  Exact integer arithmetic shows sigma_std lies
  entirely in the 2772bar channel of Sym^2(126bar), (M_p - 2) sigma_std = 0 and
  C_p sigma_std = 0, so every square vanishes at the vacuum and V(vac) = V0.
  The vacuum is therefore a global minimum; exact stationarity and exact
  Hessian positive semidefiniteness follow for every r0 > 0.
* Compiler checks (float64).  At r0 in {1/5, 1/100, 1/1000, M_I/M_GUT} (all
  with x0 = 1) the live compiler gives |grad| ~ 1e-14, symmetry rank 35
  (SO(10)/SM + U(1)_X + PQ), no negative mode, a kernel equal to the 35
  symmetry tangents PLUS the 4 real modes of the tuned light doublet (the
  kernel is exactly the symmetry tangents only if O06 is raised), and smallest
  massive eigenvalue r0^2/96.  At the coupling ratio O46_1 : O46_54 = 3/5 : -1
  the Phi-H quartics combine into ||H wedge Phi||^2, which gives the 10_H
  colour triplets M_GUT^2 and the doublets no Phi-induced mass.  That ratio is
  a tuning (nothing enforces it), and so is O06 = 2|kappa| r0: doublet-triplet
  splitting is tuned, not automatic.
* Numerical global search.  A fast evaluator of the SOS form (value and
  analytic gradient) is validated against the live compiler at random states;
  random-start L-BFGS over the full 486 chart and structured competitors never
  go below V0.  Endpoints are classified on_orbit / inconclusive / off_orbit
  with orbit tolerances scaled to the soft-mode curvature r0^2/96 (an endpoint
  at gap g may sit a relative distance sqrt(96 g)/r0^2 off the orbit), so the
  classification does not depend on run-to-run float noise.

Physics caveats recorded in the report (not hidden behind the SM label):
* "Colour triplets at M_GUT" holds for the 10_H triplets only.  Six
  gauge-charged complex remnants of the 126bar (10bar,1,3) -- (6,1)_4/3 and
  (1,1)_2 at M_I/sqrt(96), (3,1)_1/3, (3,1)_4/3, (6,1)_1/3 and (6,1)_2/3 at
  0.24-0.33 M_I -- and its real radial mode (M_I/sqrt(2)) lie BELOW M_I, and
  the 126bar (15,2,2) sits at ~0.7 M_GUT.
* The breaking route SO(10) -> PS -> SM matches the manuscript's Pati-Salam RG
  anchor, but its field content does not: the anchor's beta coefficients assume
  a light (15,2,2) above M_I and a 2HDM below M_I, whereas this candidate has a
  1HDM plus the sub-M_I remnants.  Re-solving the anchor's one-loop chain with
  the candidate's content moves M_I and M_GUT substantially, so the GeV masses
  quoted at r0 = M_I/M_GUT (anchor scales, chart unit |Phi| = 1 <-> M_GUT, x0 = 1
  rather than the canonical Phi17 = 1e17 GeV) are illustrative only.
* The tuned light doublet has tree-level quartic lambda_eff = 2 - kappa^2/(4 r0^2)
  = 127/64 at the benchmark, so conditional SM running from M_I gives m_h ~ 195
  GeV.  The certificate holds whenever kappa^2 < 8 r0^2 (equivalently
  lambda_eff > 0), and lambda_eff -> 0+ brings m_h within a few GeV of the
  measured value; global minimality forces lambda_eff >= 0, whereas SM running
  at M_t = 173.34 GeV needs a slightly negative lambda(M_I).

The equality set {V = V0} is classified exactly in
g3_sm_pati_salam_equality_set_v20: it is G.(p, r0 sigma_std, 0, r0, x0), unique
modulo G = SO(10) x U(1)_X x U(1)_PQ (U(1)_PQ is the contract's accidental
symmetry; modulo SO(10) x U(1)_X alone it is a circle of orbits).  This module
reads that committed artifact (it cannot import the module, which imports this
one) and claims uniqueness only when the artifact reports the proved status
with no failed check.

Open: the Hessian kernel count is float64; electroweak breaking and a realistic
Yukawa sector are absent (the H-linear portals O15, O38, O45, O28 vanish); the
two doublet tunings, the sub-M_I coloured scalars, the RG content and the Higgs
quartic are open.  G3 is not closed and nothing is excluded.
"""
from __future__ import annotations

import argparse
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
from scipy import sparse
from scipy.optimize import minimize

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_gauged_u1x_g3_global_counterexample_v20 as counterexample_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as ext
import exact_gauged_u1x_physical_quotient_v20 as quotient
import exact_h10_self_quartic_family_v20 as h_self_source
import exact_hsigma_45_background_hessian_v20 as hsigma
import g3_candidate_physical_target_audit_v20 as target
import g3_physical_hierarchy_higgs_stability_v20 as stability
import g3_sigma_hypercharge_audit_v20 as hypercharge
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import gauged_u1x_g3_sos_candidate_v20 as historical
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import two_loop_thresholds_v20 as rg_anchor

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_CANDIDATE_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_CANDIDATE_V20.md"
# Committed artifact of g3_sm_pati_salam_equality_set_v20.  Read from disk, never imported: that module imports
# this one.
EQUALITY_SET_JSON = ROOT / "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json"
EQUALITY_SET_SOURCE = "g3_sm_pati_salam_equality_set_v20"
EQUALITY_SET_PROVED_STATUS = "SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
R0 = Fraction(1, 5)
X0 = Fraction(1)
SIGMA_SCALE = Fraction(1, 8)
RADIAL_COEFFICIENT = Fraction(2)
HISTORICAL_RADIAL_COEFFICIENT = Fraction(25, 12)
SELF_CHANNELS = ("54", "1050bar", "2772bar", "4125")
HISTORICAL_SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(17, 16),
    "4125": Fraction(1),
}
SWAPPED_SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(1),
    "4125": Fraction(17, 16),
}
SELF_IDS = {
    channel: f"lambda::O27_B0{index}_126bar_self_projectors"
    for index, channel in enumerate(SELF_CHANNELS, start=1)
}
O05_ID = "lambda::O05_B01_126bar_norm"
O06_ID = "lambda::O06_B01_Hdag_H_norm"
O12_ID = "re::O12_B01_Hdag_Hdag_pair"
O04_ID = "lambda::O04_B01_singlet_polynomial"
O46_1_ID = "lambda::O46_B01_Phi2_HdagH_channels"
O46_54_ID = "lambda::O46_B03_Phi2_HdagH_channels"
H_LINEAR_PORTAL_IDS = (
    "re::O15_B01_Phi_Hdag_Sigma",
    "re::O38_B01_Phi_Hdag_Sigmadag",
    "re::O45_B01_Phi2_Hdag_Sigma_210_1050",
    "re::O45_B02_Phi2_Hdag_Sigma_210_1050",
    "re::O28_B01_unique_Hdag_Sigma2_Sigmadag",
)
EXPECTED_NONZERO = 27
EXPECTED_STABILIZER_DIMENSION = 12
EXPECTED_SYMMETRY_RANK = 35
LIGHT_DOUBLET_REAL_DIMENSION = 4
LIGHTEST_MASSIVE_OVER_R0_SQUARED = Fraction(1, 96)
QUARTIC_LOWER_BOUND = Fraction(1, 167)
SIGMA_STD_RAW_NORM_SQUARED = 16
STATIONARITY_ATOL = 1.0e-12
# Light states: projected-Hessian eigenvalues below 5 r0^2 (the decoupled Phi17 radial mode, x0^2/8, excluded).
LIGHT_CUTOFF_OVER_R0_SQUARED = 5.0
# Numerical zero for Hessian eigenvalues (absolute, M_GUT^2): ~200x above the <~5e-16 float noise of the tuned
# doublet at every benchmark and ~400x below the lightest massive state r0^2/96 = 4.2e-11 at r0 = M_I/M_GUT.
# Masses below it are reported as exactly 0 (sqrt would lift ~1e-18 noise to a spurious ~1e-8 r0 M_GUT).
NUMERICAL_ZERO_EIGENVALUE = 1.0e-13
# Light-state order: m^2/r0^2 values closer than this are one mass level (the same resolution light_spectrum uses to
# merge eigenvalues).  (6,1)_4/3 and (1,1)_2 are exactly degenerate at r0^2/96, and float noise in m^2/r0^2 reaches
# ~1e-5 at r0 = M_I/M_GUT (~6e-14 M_GUT^2 over r0^2 ~ 4e-9), so a level is ordered by its SM labels, never by noise.
LIGHT_LEVEL_TOLERANCE_OVER_R0_SQUARED = 1.0e-3
EXPECTED_LIGHT_REAL_DIMENSION = 60
# Numerical endpoint classification (float64 evidence only).  NUM_FULL_GAP_REACHED and NUM_FULL_ORBIT_RESIDUAL
# repeat g3_sm_pati_salam_equality_set_v20's values (that module imports this one).  Near the vacuum orbit,
# V - V0 >= (1/2)(r0^2/96)|d|^2 for an off-orbit chart displacement d (the softest massive modes are the 126bar
# remnants at r0^2/96; the tuned massless doublet enters only quartically, N_H <~ 0.71 sqrt(gap)), so an endpoint
# at gap g can sit a relative distance eps(g) = sqrt(96 g)/r0^2 off the orbit (|Sigma|_chart = sqrt(2) r0).  eps
# grows as r0 shrinks, so orbit residuals are compared with NUM_FULL_ORBIT_RESIDUAL + 10 eps(g) (along the soft
# modes the largest normalised residual, the stabilizer's kernel singular value / r0, is ~2.7 eps), and an
# endpoint is classified only when g <= NUM_FULL_GAP_REACHED and eps(g) <= 1e-2 (the float stabilizer count with
# its 0.1 r0 threshold breaks down near eps ~ 4e-2); otherwise it is inconclusive, never a failure.
NUM_FULL_GAP_REACHED = 1.0e-11
NUM_FULL_ORBIT_RESIDUAL = 1.0e-3
ENDPOINT_GAP_FLOOR = 1.0e-14  # float resolution of V - V0 (|V| ~ 1)
ENDPOINT_TOLERANCE_PER_SOFT_DISPLACEMENT = 10.0
ENDPOINT_MAX_SOFT_DISPLACEMENT = 1.0e-2
BELOW_V0_TOLERANCE = 1.0e-10
ORBIT_CLASSES = ("on_orbit", "inconclusive", "off_orbit")
M_H_OBSERVED_GEV = 125.20
DIGITS = 12
UNITS = "Hessian eigenvalues of the canonical 486-real chart, units of M_GUT^2 (|Phi| = 1)"
SQRT2 = math.sqrt(2.0)

DOUBLET_REAL_X = tuple(chart.H_SLICE.start + 2 * index for index in range(6, 10))
BLOCKS = {
    "Phi210": chart.PHI_SLICE,
    "H10": chart.H_SLICE,
    "Sigma126bar": chart.SIGMA_SLICE,
    "S": chart.S_SLICE,
    "Phi17": chart.X_SLICE,
}


# ---------------------------------------------------------------------------
# Serialisation.
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# The coefficient map.
# ---------------------------------------------------------------------------

_H, _R, _X = sympy.symbols("h r x", positive=True)


@lru_cache(maxsize=1)
def historical_expressions() -> dict[str, sympy.Expr]:
    """The historical 27-parameter p-branch map as exact sympy expressions."""
    return {
        parameter_id: sympy.sympify(text.replace("^", "**"), locals={"h": _H, "r": _R, "x": _X})
        for parameter_id, text in historical.symbolic_nonzero_coefficients().items()
    }


def _to_fraction(value: Any) -> Fraction:
    rational = sympy.nsimplify(value)
    if not rational.is_Rational:
        raise ArithmeticError(f"expected an exact rational, got {value!r}")
    return Fraction(int(rational.p), int(rational.q))


def _as_sympy(value: Any) -> Any:
    if isinstance(value, Fraction):
        return sympy.Rational(value.numerator, value.denominator)
    return value


def historical_coefficients(r0: Any = R0, x0: Any = X0, h: Any = 0) -> dict[str, Any]:
    """Historical map evaluated exactly at (h, r, x); zero entries dropped."""
    return dict(_historical_coefficients_cached(r0, x0, h))


@lru_cache(maxsize=64)
def _historical_coefficients_cached(r0: Any, x0: Any, h: Any) -> tuple[tuple[str, Any], ...]:
    substitution = {_H: _as_sympy(h), _R: _as_sympy(r0), _X: _as_sympy(x0)}
    exact = isinstance(r0, Fraction) and isinstance(x0, Fraction)
    output: list[tuple[str, Any]] = []
    for parameter_id, expression in historical_expressions().items():
        value = sympy.expand(expression.subs(substitution))
        if value == 0:
            continue
        output.append((parameter_id, _to_fraction(value) if exact else value))
    return tuple(output)


def candidate_coefficients(
    r0: Any = R0,
    x0: Any = X0,
    kappa: Any | None = None,
    *,
    o06_offset: Any = 0,
) -> dict[str, Any]:
    """The SM Pati-Salam candidate: historical h=0 map plus the stated changes.

    Accepts Fractions (exact benchmark values) or sympy symbols (identity check).
    """
    kappa = -r0 / 4 if kappa is None else kappa
    output = historical_coefficients(r0, x0, 0)
    t = SIGMA_SCALE
    output[SELF_IDS["2772bar"]] = t * SWAPPED_SELF_WEIGHTS["2772bar"]
    output[SELF_IDS["4125"]] = t * SWAPPED_SELF_WEIGHTS["4125"]
    output[O05_ID] = t * (4 - RADIAL_COEFFICIENT * r0 * r0)
    output[O06_ID] = 2 * abs(kappa) * r0 + o06_offset
    output[O12_ID] = kappa
    return {key: value for key, value in output.items() if value != 0}


def float_coefficients(coefficients: Mapping[str, Any]) -> dict[str, float]:
    return {key: float(value) for key, value in coefficients.items()}


def coefficient_changes(r0: Fraction = R0, x0: Fraction = X0) -> list[dict[str, Any]]:
    before = historical_coefficients(r0, x0, 0)
    after = candidate_coefficients(r0, x0)
    rows = []
    for key in sorted(set(before) | set(after)):
        old = before.get(key, Fraction(0))
        new = after.get(key, Fraction(0))
        if old != new:
            rows.append({"parameter": key, "historical_h0": old, "candidate": new})
    return rows


def expanded_sos_coefficient_map(r0: Any = R0, x0: Any = X0, kappa: Any | None = None) -> dict[str, Any]:
    """Expand the adapted SOS decomposition into authoritative parameters.

    V = V_Phi + (1/8)[||(M-2)Sigma||^2 + ||C Sigma||^2 + W'(Sigma) - 2 r0^2 N_Sigma]
        + [2 N_H^2 + 2|k| r0 N_H + 2k Re(H.H S) + (|S|^2 - r0^2)^2]
        + ||H wedge Phi||^2 + (1/32)(|Phi17|^2 - x0^2)^2   (constants dropped).
    """
    kappa = -r0 / 4 if kappa is None else kappa
    t = SIGMA_SCALE
    output: dict[str, Any] = {"lambda::O07_B01_Phi_norm": Fraction(-2)}
    for index, name in enumerate(("J0", "J2", "J3", "J4"), start=1):
        output[f"lambda::O48_B0{index}_Phi_self_quartics"] = phi_source.EXPECTED_J_COUPLINGS[name]
    mixed = tuple(
        a + c
        for a, c in zip(a_square_source.EXPECTED_WEIGHTS, sos_source.C_SQUARE_WEIGHTS, strict=True)
    )
    for index, weight in enumerate(mixed, start=1):
        output[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] = t * weight
    output["lambda::O14_B01_Phi_Sigma_Sigmadag_cubic"] = -4 * t
    output[O05_ID] = 4 * t - t * RADIAL_COEFFICIENT * r0 * r0
    for channel in SELF_CHANNELS:
        output[SELF_IDS[channel]] = t * SWAPPED_SELF_WEIGHTS[channel]
    # 2 N_H^2 = 2 (I_1 + I_54): Sym^2(10) = 1 + 54.
    output["lambda::O36_B01_H_self_quartics"] = Fraction(2)
    output["lambda::O36_B02_H_self_quartics"] = Fraction(2)
    output[O06_ID] = 2 * abs(kappa) * r0
    output[O12_ID] = kappa
    output[O04_ID] = -2 * r0 * r0
    output["lambda::O23_B01_singlet_polynomial"] = Fraction(1)
    # (3/5) I_1 - I_54 = Hdag(||Phi||^2 I - C(Phi))H = ||H wedge Phi||^2.
    output[O46_1_ID] = Fraction(3, 5)
    output[O46_54_ID] = Fraction(-1)
    output["lambda::O03_B01_singlet_polynomial"] = -x0 * x0 / 16
    output["lambda::O20_B01_singlet_polynomial"] = Fraction(1, 32)
    return {key: value for key, value in output.items() if value != 0}


def _laurent_at(polynomial: Mapping[tuple[int, int, int], Fraction], h: Fraction, r: Fraction, x: Fraction) -> Fraction:
    total = Fraction(0)
    for (a, b, c), coefficient in polynomial.items():
        if a and h == 0:
            continue
        total += coefficient * h**a * r**b * x**c
    return total


def lower_bound_v0(r0: Any = R0, x0: Any = X0) -> Any:
    """V0 = -1 - (1/8) r0^4 - r0^4 - x0^4/32 (no constant term in the compiler)."""
    return -1 - SIGMA_SCALE * r0**4 - r0**4 - x0**4 / 32


@lru_cache(maxsize=1)
def hierarchy_anchor() -> dict[str, Any]:
    metadata = g2_audit._physical_hierarchy_metadata(g2_audit.physical_hierarchy_state())
    m_gut = float(metadata["M_GUT_GeV"])
    m_i = float(metadata["M_I_GeV"])
    ratio = m_i / m_gut
    return {
        "M_GUT_GeV": m_gut,
        "M_I_GeV": m_i,
        "ratio_float": ratio,
        "r0_physical": Fraction(ratio).limit_denominator(10**12),
        "source": "gauged_u1x_g2_derivative_audit_v20._physical_hierarchy_metadata(physical_hierarchy_state())",
    }


def benchmark_r0_values() -> dict[str, Fraction]:
    return {
        "1/5": Fraction(1, 5),
        "1/100": Fraction(1, 100),
        "1/1000": Fraction(1, 1000),
        "M_I/M_GUT": hierarchy_anchor()["r0_physical"],
    }


def candidate_section() -> dict[str, Any]:
    selection = g2_audit.contract_selection()
    parameter_ids = set(selection["parameter_ids"])
    exact = candidate_coefficients()
    floats = float_coefficients(exact)
    declared = sos_source.declared_candidate_coefficient_map()
    historical_via_laurent = {
        key: value
        for key, polynomial in declared.items()
        if (value := _laurent_at(polynomial, Fraction(0), R0, X0)) != 0
    }
    historical_float = historical.evaluated_nonzero_coefficients({"h": 0.0, "r": float(R0), "x": float(X0)})
    historical_exact = historical_coefficients(R0, X0, 0)
    per_benchmark = {}
    for label, r0 in benchmark_r0_values().items():
        coefficients = candidate_coefficients(r0, X0)
        per_benchmark[label] = {
            "r0": r0,
            "kappa": -r0 / 4,
            "O05": coefficients[O05_ID],
            "O06": coefficients[O06_ID],
            "O04": coefficients[O04_ID],
            "nonzero_count": len(coefficients),
            "V0": lower_bound_v0(r0, X0),
            "V0_float": float(lower_bound_v0(r0, X0)),
        }
    return {
        "defaults": {"r0": R0, "x0": X0, "kappa": "-r0/4", "O06": "2|kappa| r0"},
        "derivation": (
            "gauged_u1x_g3_sos_candidate_v20.symbolic_nonzero_coefficients() evaluated exactly at h=0 "
            "(O06 and re::O12 vanish there), then O27_B03 (2772bar) 17/128 -> 1/8, O27_B04 (4125) 1/8 -> 17/128, "
            "O05 -> (1/8)(4 - 2 r0^2), O06 -> 2|kappa| r0, re::O12 -> kappa"
        ),
        "exact_nonzero_coefficients": dict(sorted(exact.items())),
        "nonzero_count": len(exact),
        "maximum_absolute_coefficient": max(abs(value) for value in exact.values()),
        "all_parameters_in_exact_X_contract": set(exact) <= parameter_ids,
        "exact_X_parameter_count": selection["parameter_count"],
        "changes_from_historical_h0": coefficient_changes(),
        "historical_h0_nonzero_count": len(historical_exact),
        "historical_parse_matches_exact_sos_laurent_map": historical_exact == historical_via_laurent,
        "historical_parse_matches_float_evaluation": set(historical_exact) == {k for k, v in historical_float.items() if v != 0.0}
        and all(abs(float(value) - historical_float[key]) <= 1.0e-15 for key, value in historical_exact.items()),
        "H_linear_portals_zero": all(portal not in exact for portal in H_LINEAR_PORTAL_IDS),
        "float_map_inside_4pi_box": max(abs(value) for value in floats.values()) < 4.0 * math.pi,
        "benchmarks": per_benchmark,
    }


# ---------------------------------------------------------------------------
# The vacuum state.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def sigma_std_exact_form() -> dict[tuple[int, ...], tuple[int, int]]:
    record = hypercharge.exact_sigma_directions()["sm_singlet_Y0"]
    if not record["primitive_equals_raw"] or not record["raw_is_minus_i_eigenform"]:
        raise ArithmeticError("z1^z2^z3^z4^z5 is not an exact -i Hodge eigenform")
    return record["form"]


@lru_cache(maxsize=1)
def sigma_std_raw_coordinates() -> tuple[np.ndarray, np.ndarray]:
    coordinates = g2_audit._exact_sigma_coordinates(sigma_std_exact_form())
    real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    imaginary = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    for index, (re, im) in coordinates.items():
        real[int(index)] = int(re)
        imaginary[int(index)] = int(im)
    if int(real @ real + imaginary @ imaginary) != SIGMA_STD_RAW_NORM_SQUARED:
        raise ArithmeticError("sigma_std raw chart norm is not 16")
    return real, imaginary


def sigma_std_unit_coordinates() -> np.ndarray:
    real, imaginary = sigma_std_raw_coordinates()
    return (real + 1j * imaginary) / 4.0


def candidate_state(r0: Any = R0, x0: Any = X0, *, h: np.ndarray | None = None) -> potential.FieldState:
    return potential.FieldState(
        phi=direct.singlet_basis()["p"],
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex) if h is None else np.asarray(h, dtype=complex),
        sigma=chart.sigma_from_coordinates(float(r0) * sigma_std_unit_coordinates()),
        s=complex(float(r0)),
        x=complex(float(x0)),
    ).validated()


def _pair_stabilizer_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "stabilizer_dimension",
        "centre_dimension",
        "derived_algebra_dimension",
        "label",
        "is_sm_type",
        "contains_standard_sm_algebra",
        "contains_flipped_sm_algebra",
        "centre_proportional_to",
        "centre_spectrum_on_vector_10",
    )
    return {key: record.get(key) for key in keys}


def sm_embedding_section() -> dict[str, Any]:
    phis = hypercharge.exact_phi_directions()
    sigma = sigma_std_exact_form()
    spec = {
        "source": "g3_sm_pati_salam_candidate_v20.candidate_state()",
        "description": "(p, r0 sigma_std, 0, r0, x0), r0 = 1/5, x0 = 1",
        "state": candidate_state,
        "phi": phis["p"],
        "h": {},
        "sigma": sigma,
    }
    vacuum = hypercharge._named_vacuum(spec)
    phi_only = hypercharge.stabilizer([hypercharge._phi_field("p")])
    sigma_only = hypercharge.stabilizer([hypercharge._sigma_field(sigma)])
    charges = hypercharge.sigma_charge_table()["sm_singlet_Y0"]
    delta_pair = hypercharge.stabilizer(
        [hypercharge._phi_field("p"), hypercharge._sigma_field(hypercharge._sigma_form("direct_delta_r"))]
    )
    reflection = hypercharge.reflection_certificate()
    # sigma_std = -conj(hsigma.delta_r_form()) up to normalisation.
    plus_i = hsigma.delta_r_form()
    conjugate = {key: -np.conjugate(value) for key, value in plus_i.items()}
    unit = chart.sigma_from_coordinates(sigma_std_unit_coordinates())
    overlap = complex(direct.sigma_kinetic_inner(conjugate, unit)) / (
        direct.sigma_kinetic_norm(conjugate) * direct.sigma_kinetic_norm(unit)
    )
    pair = vacuum["heavy_pair_stabilizer"]
    gauge = vacuum["full_state_stabilizer_so10_plus_u1x"]
    unbroken_is_sm = bool(
        pair["is_sm_type"]
        and pair["contains_standard_sm_algebra"]
        and pair["stabilizer_dimension"] == EXPECTED_STABILIZER_DIMENSION
        and pair["centre_proportional_to"] == ["Y_standard"]
    )
    return {
        "source": "g3_sigma_hypercharge_audit_v20 (exact Gaussian-integer forms, integer so(10) matrices)",
        "binding": vacuum["binding"],
        "sigma_std_formula": "z1^z2^z3^z4^z5",
        "sigma_std_exact_charges": {
            key: charges[key]
            for key in ("B_minus_L", "T3L", "T3R", "Y", "Q_em", "C2_SU2L", "C2_SU2R", "SU3_colour_singlet", "annihilated_by_standard_SM_algebra")
        },
        "sigma_std_equals_minus_conj_hsigma_delta_r_form": {
            "overlap": {"re": overlap.real, "im": overlap.imag},
            "alignment_defect": max(0.0, 1.0 - abs(overlap)),
        },
        "heavy_pair_stabilizer": _pair_stabilizer_summary(pair),
        "full_state_stabilizer_so10_plus_u1x": gauge,
        "phi_p_alone": _pair_stabilizer_summary(phi_only),
        "sigma_std_alone": _pair_stabilizer_summary(sigma_only),
        "old_orientation_p_delta_r": _pair_stabilizer_summary(delta_pair),
        "reflection_R_maps_sigma_std_to_flipped_and_fixes_p": bool(
            reflection["R_maps_sm_singlet_Y0_to_flipped"] and reflection["R_fixes_p"]
        ),
        "candidate_is_sm_vacuum": bool(vacuum["is_sm_vacuum"]),
        "target_unbroken_algebra_is_standard_model": unbroken_is_sm,
        "breaking_chain": [
            {
                "stage": "SO(10) -> SU(4)_C x SU(2)_L x SU(2)_R",
                "vev": "Phi = p (Pati-Salam singlet e6789)",
                "scale": "M_GUT",
                "exact_stabilizer_dimension": phi_only["stabilizer_dimension"],
            },
            {
                "stage": "Pati-Salam -> SU(3)_c x SU(2)_L x U(1)_Y",
                "vev": "Sigma = r0 sigma_std (Y = 0 member of (10bar,1,3))",
                "scale": "r0 M_GUT = M_I",
                "exact_stabilizer_dimension": pair["stabilizer_dimension"],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Exact certificates.
# ---------------------------------------------------------------------------


def _integer_projected_pairs(real: np.ndarray, imaginary: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray, int]]:
    """den * P_q(raw (x) raw) as exact integer matrices (generalises the Delta_R source)."""
    pair_real = np.outer(real, real) - np.outer(imaginary, imaginary)
    pair_imaginary = np.outer(real, imaginary) + np.outer(imaginary, real)
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(sos_source._sigma_pair_casimir(*powers[-1]))
    output: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}
    for channel in sigma_source.CHANNELS:
        polynomial = sigma_source._poly(channel)
        denominator = math.lcm(*(value.denominator for value in polynomial))
        projected_real = sum(
            (int(coefficient * denominator) * powers[index][0] for index, coefficient in enumerate(polynomial)),
            np.zeros_like(pair_real),
        )
        projected_imaginary = sum(
            (int(coefficient * denominator) * powers[index][1] for index, coefficient in enumerate(polynomial)),
            np.zeros_like(pair_imaginary),
        )
        output[channel] = (projected_real, projected_imaginary, denominator)
    return output


@lru_cache(maxsize=1)
def exact_sigma_std_certificate() -> dict[str, Any]:
    real, imaginary = sigma_std_raw_coordinates()
    norm_squared = int(real @ real + imaginary @ imaginary)
    projected = _integer_projected_pairs(real, imaginary)
    fractions = {
        channel: Fraction(
            sum(int(v) ** 2 for v in projected[channel][0].flat) + sum(int(v) ** 2 for v in projected[channel][1].flat),
            projected[channel][2] ** 2 * norm_squared**2,
        )
        for channel in SELF_CHANNELS
    }
    max_entry = max(int(np.max(np.abs(part))) for value in projected.values() for part in value[:2])

    p_form, p_float = sos_source.phi_source.pati_salam_direction()
    p_vector = np.rint(p_float).astype(np.int64)
    operator_real, operator_imaginary = a_square_source.integer_cubic_operators()
    m_real = np.tensordot(p_vector, operator_real.astype(np.int64), axes=(0, 0))
    m_imaginary = np.tensordot(p_vector, operator_imaginary.astype(np.int64), axes=(0, 0))
    image_real = m_real @ real - m_imaginary @ imaginary
    image_imaginary = m_real @ imaginary + m_imaginary @ real
    contraction_real, contraction_imaginary = a_square_source.integer_contraction_tensor()
    c_real = np.einsum("vpa,p,a->v", contraction_real.astype(np.int64), p_vector, real) - np.einsum(
        "vpa,p,a->v", contraction_imaginary.astype(np.int64), p_vector, imaginary
    )
    c_imaginary = np.einsum("vpa,p,a->v", contraction_real.astype(np.int64), p_vector, imaginary) + np.einsum(
        "vpa,p,a->v", contraction_imaginary.astype(np.int64), p_vector, real
    )
    delta = sos_source.exact_delta_self_certificate()["delta_projector_fractions"]

    def weighted(weights: Mapping[str, Fraction], values: Mapping[str, Fraction]) -> Fraction:
        return sum((weights[channel] * values[channel] for channel in SELF_CHANNELS), Fraction(0))

    return {
        "raw_form": "z1^z2^z3^z4^z5 (exact Gaussian-integer chart coordinates, 16 entries)",
        "raw_nonzero_coordinates": int(np.count_nonzero(real) + np.count_nonzero(imaginary)),
        "raw_norm_squared": norm_squared,
        "exactly_in_chart_minus_i_space": hypercharge._is_minus_i_eigenform(sigma_std_exact_form()),
        "projector_fractions": fractions,
        "projector_fractions_sum": sum(fractions.values(), Fraction(0)),
        "maximum_integer_projection_entry": max_entry,
        "weighted_self_quartic_over_N2": {
            "sigma_std_swapped": weighted(SWAPPED_SELF_WEIGHTS, fractions),
            "sigma_std_historical": weighted(HISTORICAL_SELF_WEIGHTS, fractions),
            "delta_r_swapped": weighted(SWAPPED_SELF_WEIGHTS, delta),
            "delta_r_historical": weighted(HISTORICAL_SELF_WEIGHTS, delta),
        },
        "delta_r_projector_fractions": delta,
        "M_p_sigma_minus_2_sigma_max_abs": max(
            int(np.max(np.abs(image_real - 2 * real))), int(np.max(np.abs(image_imaginary - 2 * imaginary)))
        ),
        "C_p_sigma_max_abs": max(int(np.max(np.abs(c_real))), int(np.max(np.abs(c_imaginary)))),
        "interpretation": (
            "sigma_std (x) sigma_std lies entirely in 2772bar (the highest-weight channel: sigma_std is the "
            "SO(10) highest-weight vector of 126bar), so W'(Sigma) = N^2 exactly with the swapped weights; "
            "p acts on it with M_p = 2 and C_p = 0 exactly."
        ),
    }


@lru_cache(maxsize=None)
def _hs_square_completion_residual() -> str:
    """Exact residual of the H/S square completion (after Cauchy-Schwarz), sympy."""
    n, s, a, r = sympy.symbols("N_H s k_abs r0", nonnegative=True)
    t = s - r
    reduced = 2 * n**2 + 2 * a * r * n - 2 * a * n * s + (s**2 - r**2) ** 2
    completed = 2 * (n - a * t / 2) ** 2 + t**2 * (4 * r**2 - a**2 / 2 + t * (t + 4 * r))
    return str(sympy.expand(reduced - completed))


def exact_hs_certificate(r0: Fraction = R0, kappa: Fraction | None = None) -> dict[str, Any]:
    kappa = -r0 / 4 if kappa is None else kappa
    margin = 4 * r0 * r0 - kappa * kappa / 2
    residual = _hs_square_completion_residual()
    sample = np.random.default_rng(10).normal(size=(2, 10))
    completeness = h_self_source.invariants(sample[0] + 1j * sample[1])["projector_completeness_residual"]
    return {
        "I1_plus_I54_minus_NH2_float_residual_at_random_H": completeness,
        "sector": "V_HS = 2 N_H^2 + 2|k| r0 N_H + 2 k Re(conj(H.H) conj(S)) + |S|^4 - 2 r0^2 |S|^2",
        "O12_convention": "re::O12 multiplies 2 Re[(Hdag.Hdag) Sdag] (census orbit O12 = SARAH kappaH H10.H10.S)",
        "H_self_identity": "O36: 2 I_1 + 2 I_54 = 2 N_H^2 (Sym^2(10) = 1 + 54, exact_h10_self_quartic_family_v20)",
        "cauchy_schwarz": "|2k Re(conj(H.H) conj(S))| <= 2|k| |H.H| |S| <= 2|k| N_H |S|",
        "square_completion": (
            "Let t = |S| - r0. Then V_HS + r0^4 >= 2 N_H^2 + 2|k| N_H (r0 - |S|) + t^2 (|S| + r0)^2. For t <= 0 "
            "every term is >= 0, and the sum is > 0 unless t = 0 and N_H = 0. For t > 0, completing the square in "
            "N_H gives >= 2 (N_H - |k| t/2)^2 + t^2 [(|S| + r0)^2 - k^2/2], and (|S| + r0)^2 > 4 r0^2. So "
            "V_HS >= -r0^4, with equality only at H = 0, |S| = r0, whenever k^2 < 8 r0^2, i.e. lambda_eff = "
            "2 - k^2/(4 r0^2) > 0. The Cauchy-Schwarz step is tight (H real up to phase, S phase aligned), so "
            "k^2 <= 8 r0^2 is also necessary."
        ),
        "square_completion_identity": (
            "2 N_H^2 + 2|k| N_H (r0 - |S|) + (|S|^2 - r0^2)^2 = 2 (N_H - |k| t/2)^2 + t^2 [4 r0^2 - k^2/2 + t (t + 4 r0)]"
        ),
        "square_completion_identity_residual_sympy": residual,
        "square_completion_identity_exact": residual == "0",
        "kappa": kappa,
        "condition": "k^2 < 8 r0^2 (equivalently lambda_eff = 2 - k^2/(4 r0^2) > 0)",
        "margin_4r0_squared_minus_kappa_squared_over_2": margin,
        "condition_holds_strictly": margin > 0,
        "lower_bound": -(r0**4),
        "equality_set": "H = 0 and |S| = r0 (strict inequality elsewhere)",
    }


def exact_quartic_bound() -> dict[str, Any]:
    alpha = {"|Phi|^2": Fraction(1), "N_H": Fraction(2), "N_Sigma": SIGMA_SCALE, "|S|^2": Fraction(1), "|Phi17|^2": Fraction(1, 32)}
    beta = {"|Phi|^2": Fraction(1), "N_H": Fraction(2), "N_Sigma": Fraction(2), "|S|^2": Fraction(2), "|Phi17|^2": Fraction(2)}
    constant = 1 / sum((beta[key] ** 2 / alpha[key] for key in alpha), Fraction(0))
    return {
        "quartic_part": (
            "V4 = Q(Phi) + (1/8)(||M_Phi Sigma||^2 + ||C_Phi Sigma||^2 + W'(Sigma)) + 2 N_H^2 + ||H wedge Phi||^2 "
            "+ |S|^4 + |Phi17|^4/32  (the kappa term is cubic, O06/O05/O04/O03/O07 quadratic)"
        ),
        "termwise_lower_bounds": "Q >= |Phi|^4, W' >= N_Sigma^2, all other terms >= 0",
        "coefficients_alpha": alpha,
        "chart_norm_weights_beta": beta,
        "chart_norm": "|q|^2 = |Phi|^2 + 2 N_H + 2 N_Sigma + 2|S|^2 + 2|Phi17|^2",
        "bound": "V4(q) >= |q|^4 / sum(beta^2/alpha) (Cauchy-Schwarz)",
        "constant": constant,
        "matches_recorded_constant": constant == QUARTIC_LOWER_BOUND,
    }


def _symbolic_identity_check() -> dict[str, Any]:
    r, x = sympy.symbols("r0 x0", positive=True)
    k = sympy.Symbol("kappa", negative=True)
    candidate = candidate_coefficients(r, x, k)
    expanded = expanded_sos_coefficient_map(r, x, k)
    keys = sorted(set(candidate) | set(expanded))
    residuals = {key: sympy.simplify(_as_sympy(candidate.get(key, 0)) - _as_sympy(expanded.get(key, 0))) for key in keys}
    return {
        "variables": "r0 > 0, x0 > 0, kappa < 0 (sympy)",
        "parameters_compared": len(keys),
        "all_residuals_zero": all(value == 0 for value in residuals.values()),
        "O06_symbolic": str(candidate[O06_ID]),
        "O05_symbolic": str(sympy.expand(candidate[O05_ID])),
    }


def load_equality_set_report(path: Path = EQUALITY_SET_JSON) -> dict[str, Any]:
    """Committed g3_sm_pati_salam_equality_set_v20 report, {} if missing or unreadable (fail-closed)."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def equality_set_certified(equality_report: Mapping[str, Any]) -> bool:
    """True only for the proved status with zero failed checks (full report or its summary)."""
    n_failed = equality_report.get("n_failed")
    return bool(
        equality_report.get("status") == EQUALITY_SET_PROVED_STATUS
        and isinstance(n_failed, int)
        and not isinstance(n_failed, bool)
        and n_failed == 0
    )


def equality_set_section(equality_report: Mapping[str, Any]) -> dict[str, Any]:
    """The equality set {V = V0}; uniqueness is claimed only from a proved, fully passing equality-set report."""
    certified = equality_set_certified(equality_report)
    return {
        "conditions": [
            "V_Phi(Phi) = -1 (|Phi| = 1 and I45 = I210 = I5940 = 0)",
            "N_Sigma = r0^2 and Sigma (x) Sigma in 2772bar (pure: SO(10) orbit of sigma_std up to phase)",
            "(M_Phi - 2) Sigma = 0 and C_Phi Sigma = 0",
            "H = 0, |S| = r0, |Phi17| = x0",
        ],
        "unique_modulo_symmetry": (
            "exact: {V = V0} = G.(p, r0 sigma_std, 0, r0, x0) with G = SO(10) x U(1)_X x U(1)_PQ, for every r0 > 0, "
            "x0 > 0, kappa^2 < 8 r0^2 (proved in g3_sm_pati_salam_equality_set_v20).  U(1)_PQ is the contract's "
            "accidental global symmetry: modulo SO(10) x U(1)_X alone the equality set is a circle of orbits (the "
            "axion direction)"
            if certified
            else "open (numerical evidence in numerical_global_search)"
        ),
        "unique_modulo_symmetry_certified": certified,
        "equality_set_certificate": {
            "source": f"{EQUALITY_SET_SOURCE} (committed {EQUALITY_SET_JSON.name})",
            "status": equality_report.get("status"),
            "n_failed": equality_report.get("n_failed"),
        },
    }


def exact_certificate_section(equality_report: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if equality_report is None:
        equality_report = load_equality_set_report()
    phi = sos_source.exact_phi_certificate()
    mixed = sos_source.exact_mixed_certificate()
    self_source = sos_source.exact_delta_self_certificate()
    wedge = sos_source.exact_wedge_certificate()
    sigma = exact_sigma_std_certificate()
    a_report = mixed["A_square_report"]
    identity_points = {}
    for label, r0 in benchmark_r0_values().items():
        for x0 in (X0, Fraction(7, 3)):
            for kappa in (-r0 / 4, -r0 / 3, r0 / 5):
                key = f"r0={label},x0={x0},kappa={kappa / r0}*r0"
                identity_points[key] = candidate_coefficients(r0, x0, kappa) == expanded_sos_coefficient_map(r0, x0, kappa)
    symbolic = _symbolic_identity_check()
    hs = {label: exact_hs_certificate(r0) for label, r0 in benchmark_r0_values().items()}
    quartic = exact_quartic_bound()
    weights_dominate = all(value >= 1 for value in SWAPPED_SELF_WEIGHTS.values())
    completeness = self_source["projector_polynomial_sum"] == (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    vacuum_squares = {
        "V_Phi(p) + 1": "0 (exact_210: |p| = 1, extra channels vanish)",
        "(M_p - 2) Sigma": sigma["M_p_sigma_minus_2_sigma_max_abs"],
        "C_p Sigma": sigma["C_p_sigma_max_abs"],
        "W'(Sigma) - N_Sigma^2": sigma["weighted_self_quartic_over_N2"]["sigma_std_swapped"] - 1,
        "N_Sigma - r0^2": 0,
        "H": 0,
        "|S| - r0": 0,
        "|Phi17| - x0": 0,
    }
    checks = {
        "coefficient_map_equals_adapted_SOS_expansion_symbolically": symbolic["all_residuals_zero"],
        "coefficient_map_equals_adapted_SOS_expansion_at_all_rational_points": all(identity_points.values()),
        "exact_210_global_bound_and_P_saturation": bool(
            phi["couplings_match_candidate"]
            and phi["spectral_weights_all_at_least_one"]
            and phi["P_has_unit_norm"]
            and phi["positive_extra_channels_zero_at_P"]
        ),
        "A_square_recoupling_exact": bool(a_report["n_failed"] == 0 and a_report["flags"]["A_square_recoupling_exactly_source_bound"]),
        "C_square_recoupling_exact": bool(
            mixed["invariant_space_dimension"] == 6
            and mixed["witness_determinant"] != 0
            and mixed["C_square_unique_weights"] == tuple(map(Fraction, sos_source.C_SQUARE_WEIGHTS))
            and all(value == 0 for value in mixed["C_square_identity_residuals"])
        ),
        "cubic_operator_exactly_hermitian": bool(mixed["cubic_operator_exactly_hermitian"]),
        "self_projectors_complete_and_generators_antihermitian": bool(
            completeness and self_source["generators_exactly_antihermitian"]
        ),
        "swapped_self_weights_all_at_least_one": weights_dominate,
        "Phi_H_term_is_exact_wedge_square": bool(
            wedge["all_polarized_coefficient_residual"] == 0 and wedge["P_operator_equals_diag_1x6_0x4"]
        ),
        "H_self_quartic_basis_is_I1_I54": tuple(h_self_source_labels()) == ("I_1", "I_54"),
        "HS_sector_bounded_at_every_benchmark": all(
            row["condition_holds_strictly"] and row["square_completion_identity_exact"] for row in hs.values()
        ),
        "sigma_std_exactly_in_minus_i_space": bool(sigma["exactly_in_chart_minus_i_space"]),
        "sigma_std_is_pure_2772bar": sigma["projector_fractions"]
        == {"54": Fraction(0), "1050bar": Fraction(0), "2772bar": Fraction(1), "4125": Fraction(0)},
        "M_p_sigma_std_equals_2_sigma_std": sigma["M_p_sigma_minus_2_sigma_max_abs"] == 0,
        "C_p_sigma_std_vanishes": sigma["C_p_sigma_max_abs"] == 0,
        "quartic_part_strictly_positive": quartic["matches_recorded_constant"],
    }
    proof = all(checks.values())
    return {
        "adapted_identity": (
            "V = [-2|Phi|^2 + Q(Phi)] + (1/8)[||(M_Phi - 2)Sigma||^2 + ||C_Phi Sigma||^2 + W'(Sigma) - 2 r0^2 N_Sigma] "
            "+ [2 N_H^2 + 2|k| r0 N_H + 2k Re(conj(H.H) conj(S)) + (|S|^2 - r0^2)^2 - r0^4] + ||H wedge Phi||^2 "
            "+ (1/32)(|Phi17|^2 - x0^2)^2 - x0^4/32,  W' = 2 I54 + 2 I1050bar + I2772bar + (17/16) I4125"
        ),
        "difference_from_historical_SOS27": (
            "self weights (2,2,17/16,1) -> (2,2,1,17/16); radial coefficient 25/12 -> 2; H/S sector at h = 0 with "
            "kappa_H instead of the (h, alpha = h^2/r) alignment squares"
        ),
        "symbolic_identity": symbolic,
        "rational_point_identity": identity_points,
        "lower_bound": {
            "Phi": "V_Phi >= (I2 - 1)^2 - 1 >= -1",
            "Sigma": "(1/8)(W' - 2 r0^2 N) >= (1/8)(N^2 - 2 r0^2 N) >= -(1/8) r0^4",
            "H_S": "V_HS >= -r0^4 (exact_hs_certificate)",
            "Phi17": "(1/32)(|Phi17|^2 - x0^2)^2 - x0^4/32 >= -x0^4/32",
            "V0": "-1 - r0^4/8 - r0^4 - x0^4/32",
            "V0_at_default": lower_bound_v0(),
        },
        "vacuum_square_values": vacuum_squares,
        "V_at_vacuum_equals_V0": proof,
        "conclusions": {
            "global_minimum": "V >= V0 everywhere and V(p, r0 sigma_std, 0, r0, x0) = V0",
            "stationarity": "a global minimiser of a smooth function is a critical point: grad V = 0 exactly",
            "hessian": "second-order necessary condition at a global minimiser: Hessian PSD exactly",
            "validity": (
                "every r0 > 0, x0 > 0, kappa^2 < 8 r0^2 (lambda_eff > 0); the light-doublet tuning O06 = 2|kappa| r0 "
                "included"
            ),
        },
        "equality_set": equality_set_section(equality_report),
        "exact_sigma_std": sigma,
        "exact_HS_sector": hs,
        "exact_quartic_bound": quartic,
        "reused_source_certificates": {
            "exact_210": "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_phi_certificate",
            "A_and_C_squares": "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_mixed_certificate",
            "self_projector_completeness": "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_delta_self_certificate",
            "wedge_square": "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_wedge_certificate",
        },
        "why_the_swap": (
            "With the historical weights W/N^2 is 17/16 at sigma_std and 25/24 at delta_R, so the p-branch "
            "prefers the non-SM delta_R; with the swapped weights it is 1 at sigma_std (the bound W' >= N^2 is "
            "attained) and 49/48 at delta_R."
        ),
        "checks": checks,
        "bfb_certified": proof,
        "global_minimum_certified": proof,
        "exactly_stationary": proof,
        "hessian_psd_exact": proof,
    }


def h_self_source_labels() -> tuple[str, ...]:
    import live_g2_exact_h10_self_quartic_derivatives_v20 as h_self_derivatives

    return tuple(h_self_derivatives.BASIS_LABELS)


def exact_slice_section(r0: Fraction = R0, x0: Fraction = X0) -> dict[str, Any]:
    """Exact slice polynomial along (c p, r sigma_std, 0, s, x) from the SOS identities."""
    c, r, s, x = sympy.symbols("c r s x", real=True)
    R, X = _as_sympy(r0), _as_sympy(x0)
    t = sympy.Rational(1, 8)
    polynomial = sympy.expand(
        (c**2 - 1) ** 2
        - 1
        + t * (4 * (c - 1) ** 2 * r**2 + r**4 - 2 * R**2 * r**2)
        + (s**2 - R**2) ** 2
        - R**4
        + (x**2 - X**2) ** 2 / 32
        - X**4 / 32
    )
    variables = (c, r, s, x)
    point = {c: 1, r: R, s: R, x: X}
    gradient = [sympy.simplify(sympy.diff(polynomial, v).subs(point)) for v in variables]
    hessian = sympy.Matrix(4, 4, lambda i, j: sympy.diff(polynomial, variables[i], variables[j]).subs(point))
    return {
        "slice": "(Phi, Sigma, H, S, Phi17) = (c p, r sigma_std, 0, s, x), all real",
        "derivation": "Q(c p) = c^4, (c M_p - 2) r sigma = 2(c - 1) r sigma, C_p sigma = 0, W'(r sigma) = r^4",
        "r0": r0,
        "x0": x0,
        "polynomial": str(polynomial),
        "value_at_vacuum": polynomial.subs(point),
        "equals_V0": sympy.simplify(polynomial.subs(point) - _as_sympy(lower_bound_v0(r0, x0))) == 0,
        "gradient_at_vacuum": gradient,
        "gradient_vanishes_exactly": all(value == 0 for value in gradient),
        "slice_hessian_at_vacuum": [[hessian[i, j] for j in range(4)] for i in range(4)],
        "slice_hessian_eigenvalues": sorted(hessian.eigenvals().keys(), key=lambda value: float(value)),
    }


def slice_value(c: float, r: float, s: float, x: float, r0: Fraction = R0, x0: Fraction = X0) -> Fraction:
    cf, rf, sf, xf = (Fraction(value) for value in (c, r, s, x))
    R, X = Fraction(r0), Fraction(x0)
    return (
        (cf * cf - 1) ** 2
        - 1
        + SIGMA_SCALE * (4 * (cf - 1) ** 2 * rf * rf + rf**4 - 2 * R * R * rf * rf)
        + (sf * sf - R * R) ** 2
        - R**4
        + (xf * xf - X * X) ** 2 / 32
        - X**4 / 32
    )


def slice_state(c: float, r: float, s: float, x: float) -> potential.FieldState:
    return potential.FieldState(
        phi=direct.scale_form(direct.singlet_basis()["p"], float(c)),
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=chart.sigma_from_coordinates(float(r) * sigma_std_unit_coordinates()),
        s=complex(float(s)),
        x=complex(float(x)),
    ).validated()


# ---------------------------------------------------------------------------
# SM generators on the 486 chart (exact integer bases, float matrices).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _phi_generators() -> tuple[sparse.csr_matrix, ...]:
    return tuple(a_square_source.integer_generators())


def chart_generator(vector: Sequence[Any]) -> np.ndarray:
    """486x486 real matrix of sum_ab v_ab L_ab in the canonical chart (L_ab e_b = e_a)."""
    coefficients = np.asarray([float(value) for value in vector], dtype=float)
    output = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    phi = sparse.csr_matrix((chart.PHI_DIM, chart.PHI_DIM), dtype=float)
    vector10 = np.zeros((10, 10), dtype=float)
    sigma = np.zeros((chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM), dtype=complex)
    generators = sigma_source._generators()
    for index, (first, second) in enumerate(itertools.combinations(range(10), 2)):
        value = coefficients[index]
        if value == 0.0:
            continue
        phi = phi + value * _phi_generators()[index].astype(float)
        vector10[first, second] += value
        vector10[second, first] -= value
        sigma += value * generators[index]
    output[chart.PHI_SLICE, chart.PHI_SLICE] = phi.toarray()
    output[chart.H_SLICE, chart.H_SLICE] = g2_audit._complex_generator_real_chart(vector10.astype(complex))
    output[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = g2_audit._complex_generator_real_chart(sigma)
    return output


@lru_cache(maxsize=1)
def sm_label_operators() -> dict[str, np.ndarray]:
    """Colour and SU(2)_L Casimirs and Y^2 on the chart, from exact integer bases."""
    su3 = hypercharge.su3_colour_integer_basis()
    matrices = [hypercharge._matrix(vector) for vector in su3]
    gram = sympy.Matrix(8, 8, lambda i, j: -int(np.trace(matrices[i] @ matrices[j])))
    # Orthonormalise X'_k = sum_a L[k, a] X_a with L^T L = gram^{-1} (exact Cholesky of the inverse).
    inverse = gram.inv()
    lower = inverse.cholesky(hermitian=False)
    combos = np.asarray(lower.evalf(30).tolist(), dtype=float)  # inverse = L L^T, X'_k = sum_a L[a,k] X_a
    su3_chart = [chart_generator(vector) for vector in su3]
    colour = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM))
    for k in range(8):
        generator = sum(combos[a, k] * su3_chart[a] for a in range(8))
        colour -= generator @ generator
    weak = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM))
    for vector in hypercharge.SU2L_INTEGER:
        generator = 0.5 * chart_generator(vector)
        weak -= generator @ generator
    hyper = chart_generator(hypercharge.Y_STANDARD_INTEGER) / 6.0
    return {
        "C3": colour,
        "C2L": weak,
        "Y2": -(hyper @ hyper),
        "gram_su3": [[int(gram[i, j]) for j in range(8)] for i in range(8)],
        "sm_generators": [chart_generator(vector) for vector in hypercharge.standard_sm_integer_basis()],
    }


_COLOUR_NAMES = {Fraction(0): "1", Fraction(4, 3): "3", Fraction(3): "8", Fraction(10, 3): "6"}
_WEAK_NAMES = {Fraction(0): "1", Fraction(3, 4): "2", Fraction(2): "3"}


def _nearest(value: float, table: Mapping[Fraction, str]) -> str:
    key = min(table, key=lambda item: abs(float(item) - value))
    return table[key] if abs(float(key) - value) < 1.0e-6 else f"C={value:.6g}"


def _abs_hypercharge(y2: float) -> str:
    fraction = Fraction(max(y2, 0.0)).limit_denominator(144)
    if abs(float(fraction) - y2) > 1.0e-6:
        return f"sqrt({y2:.6g})"
    root = Fraction(math.isqrt(fraction.numerator), math.isqrt(fraction.denominator))
    return str(root) if root * root == fraction else f"sqrt({fraction})"


def label_subspace(basis: np.ndarray) -> dict[str, int]:
    """SM content (real multiplicities) of an SM-invariant subspace."""
    if basis.shape[1] == 0:
        return {}
    ops = sm_label_operators()
    generic = ops["C3"] + math.pi * ops["C2L"] + 7.0 * math.e * ops["Y2"]
    reduced = basis.T @ generic @ basis
    _, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    rotated = basis @ vectors
    counts: dict[str, int] = {}
    for column in range(rotated.shape[1]):
        v = rotated[:, column]
        name = (
            f"({_nearest(float(v @ ops['C3'] @ v), _COLOUR_NAMES)},"
            f"{_nearest(float(v @ ops['C2L'] @ v), _WEAK_NAMES)})_|Y|={_abs_hypercharge(float(v @ ops['Y2'] @ v))}"
        )
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items()))


def block_weights(basis: np.ndarray) -> dict[str, float]:
    total = max(float(np.sum(basis**2)), 1.0e-300)
    return {
        name: float(np.sum(basis[block] ** 2)) / total
        for name, block in BLOCKS.items()
        if float(np.sum(basis[block] ** 2)) / total > 1.0e-9
    }


# ---------------------------------------------------------------------------
# Compiler verification.
# ---------------------------------------------------------------------------


def needed_direction_ids(coefficients: Mapping[str, Any]) -> set[str]:
    return {key.split("::", 1)[1] for key in coefficients}


def symmetry_matrix(state: potential.FieldState) -> tuple[np.ndarray, dict[str, int]]:
    orbit = chart.gauge_orbit_matrix(state)
    u1x = g2_audit.u1x_tangent(state)
    pq = quotient._phase_tangent(state, quotient.PQ_CHARGES)
    full = np.column_stack((orbit, u1x, pq))

    def rank(matrix: np.ndarray) -> int:
        values = np.linalg.svd(matrix, compute_uv=False)
        return int(np.sum(values > 1.0e-9 * values[0])) if values.size and values[0] > 0 else 0

    return full, {
        "so10_orbit_rank": rank(orbit),
        "so10_plus_u1x_rank": rank(np.column_stack((orbit, u1x))),
        "so10_plus_u1x_plus_pq_rank": rank(full),
    }


def _split(matrix: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    u, _, _ = np.linalg.svd(matrix, full_matrices=True)
    return u[:, :rank], u[:, rank:]


def _grouped_real(values: np.ndarray) -> list[dict[str, Any]]:
    """Group real-chart eigenvalues (multiplicities count real dimensions)."""
    groups: list[dict[str, Any]] = []
    for value in np.sort(np.asarray(values, dtype=float)):
        if groups and abs(value - groups[-1]["mass_squared"]) <= 1.0e-9:
            groups[-1]["real_multiplicity"] += 1
        else:
            groups.append({"mass_squared": float(value), "real_multiplicity": 1})
    return groups


def _clusters(values: np.ndarray, relative: float = 1.0e-7, absolute: float = 1.0e-12) -> list[tuple[int, int]]:
    output = []
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and abs(values[stop] - values[start]) <= absolute + relative * max(1.0, abs(values[start])):
            stop += 1
        output.append((start, stop))
        start = stop
    return output


def compiler_point_audit(r0: Fraction, x0: Fraction = X0, *, spectrum: bool = False) -> dict[str, Any]:
    started = time.time()
    kappa = -r0 / 4
    exact = candidate_coefficients(r0, x0, kappa)
    coefficients = float_coefficients(exact)
    state = candidate_state(r0, x0)
    needed = needed_direction_ids(coefficients)
    rows = target.parameter_rows(state, include=lambda direction: direction.direction_id in needed)
    value, gradient, hessian = target.assemble(rows, coefficients)
    v0 = lower_bound_v0(r0, x0)
    symmetry, ranks = symmetry_matrix(state)
    rank = ranks["so10_plus_u1x_plus_pq_rank"]
    tangent, complement = _split(symmetry, rank)
    projected = complement.T @ hessian @ complement
    eigenvalues, vectors = np.linalg.eigh(0.5 * (projected + projected.T))
    scale = float(r0) ** 2 * float(LIGHTEST_MASSIVE_OVER_R0_SQUARED)
    tolerance = 1.0e-3 * scale
    zero = np.abs(eigenvalues) <= tolerance
    massive = eigenvalues[eigenvalues > tolerance]
    zero_modes = complement @ vectors[:, zero]
    doublet_weight = float(np.sum(zero_modes[list(DOUBLET_REAL_X), :] ** 2)) / max(zero_modes.shape[1], 1)

    variant = dict(coefficients)
    variant[O06_ID] += float(r0) ** 2 / 100.0
    _, _, variant_hessian = target.assemble(rows, variant)
    variant_projected = complement.T @ variant_hessian @ complement
    variant_eigenvalues = np.linalg.eigvalsh(0.5 * (variant_projected + variant_projected.T))

    min_massive = float(massive[0]) if massive.size else float("nan")
    full = complement @ vectors
    output: dict[str, Any] = {
        "r0": r0,
        "r0_float": float(r0),
        "kappa": kappa,
        "O06": exact[O06_ID],
        "state": "(p, r0 sigma_std, 0, r0, x0)",
        "V_compiler": value,
        "V0_float": float(v0),
        "V_minus_V0": value - float(v0),
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "gradient_block_max_abs": {name: float(np.max(np.abs(gradient[block]))) for name, block in BLOCKS.items()},
        "symmetry_ranks": ranks,
        "hessian_symmetry_residual": float(np.max(np.abs(hessian @ tangent))),
        "projected_hessian": {
            "dimension": int(projected.shape[0]),
            "zero_tolerance": tolerance,
            "n_negative": int(np.sum(eigenvalues < -tolerance)),
            "n_zero": int(np.sum(zero)),
            "min_eigenvalue": float(eigenvalues[0]),
            "max_abs_zero_mode_eigenvalue": float(np.max(np.abs(eigenvalues[zero]))) if np.any(zero) else 0.0,
            "max_eigenvalue": float(eigenvalues[-1]),
            "zero_modes_weight_in_light_doublet_real_directions": doublet_weight,
            "min_massive_eigenvalue": min_massive,
            "min_massive_over_r0_squared": min_massive / float(r0) ** 2,
            "expected_min_massive_over_r0_squared": LIGHTEST_MASSIVE_OVER_R0_SQUARED,
            "min_massive_absolute_deviation": abs(min_massive - scale),
        },
        "all_massive_variant": {
            "O06_offset": r0 * r0 / 100,
            "n_negative": int(np.sum(variant_eigenvalues < -tolerance)),
            "n_zero": int(np.sum(np.abs(variant_eigenvalues) <= tolerance)),
            "min_eigenvalue": float(variant_eigenvalues[0]),
            "min_eigenvalue_over_r0_squared": float(variant_eigenvalues[0]) / float(r0) ** 2,
        },
    }
    output["kernel_is_symmetry_plus_light_doublet"] = bool(
        rank == EXPECTED_SYMMETRY_RANK
        and output["projected_hessian"]["n_negative"] == 0
        and output["projected_hessian"]["n_zero"] == LIGHT_DOUBLET_REAL_DIMENSION
        and doublet_weight > 1.0 - 1.0e-6
        and output["all_massive_variant"]["n_zero"] == 0
        and output["all_massive_variant"]["n_negative"] == 0
    )
    output["light_spectrum"] = light_spectrum(r0, hessian, full, eigenvalues)
    output["Phi17_block"] = phi17_block_audit(hessian, x0)
    if spectrum:
        output["labelled_spectrum"] = labelled_spectrum(r0, tangent, complement, eigenvalues, vectors)
        output["h10"] = h10_audit(rows, exact, hessian, r0, kappa)
        output["sm_generators_annihilate_vacuum"] = float(
            max(np.max(np.abs(generator @ chart.pack(state))) for generator in sm_label_operators()["sm_generators"])
        )
        output["light_doublet_quartic"] = compiler_light_doublet_quartic(
            state, coefficients, needed, full, eigenvalues, tangent, tolerance
        )
    output["seconds"] = time.time() - started
    return output


def _light_level_value(state: Mapping[str, Any]) -> float:
    """m^2/r0^2, with the numerically massless tuned doublet floored to exactly 0 (as in mass_over_r0_M_GUT)."""
    return 0.0 if float(state["mass_squared"]) < NUMERICAL_ZERO_EIGENVALUE else float(state["mass_squared_over_r0_squared"])


def _sm_label_key(state: Mapping[str, Any]) -> str:
    return ", ".join(f"{label}: {count}" for label, count in sorted(state["sm_content_real"].items()))


def order_light_states(states: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Run-independent order: mass levels ascending, SM label string within a level.

    Values of m^2/r0^2 within LIGHT_LEVEL_TOLERANCE_OVER_R0_SQUARED of a level's lowest value belong to that level
    (the real level spacings are >= 5e-3, the float noise <~ 1e-5).  The tuned doublet is floored to 0, alone in
    the lowest level, so it stays states[0].
    """
    ranked = sorted(states, key=lambda state: (_light_level_value(state), _sm_label_key(state)))
    ordered: list[Mapping[str, Any]] = []
    level: list[Mapping[str, Any]] = []
    level_start = 0.0
    for state in ranked:
        value = _light_level_value(state)
        if level and value - level_start > LIGHT_LEVEL_TOLERANCE_OVER_R0_SQUARED:
            ordered += sorted(level, key=lambda row: (_sm_label_key(row), _light_level_value(row)))
            level = []
        if not level:
            level_start = value
        level.append(state)
    ordered += sorted(level, key=lambda row: (_sm_label_key(row), _light_level_value(row)))
    return ordered


def light_spectrum(r0: Fraction, hessian: np.ndarray, full: np.ndarray, eigenvalues: np.ndarray) -> dict[str, Any]:
    """Light states (m^2 < 5 r0^2; the decoupled Phi17 radial mode excluded), labelled robustly.

    At tiny r0 the light clusters are only ~1e-11 M_GUT^2 apart, comparable to the ~6e-14 float noise
    of the assembled Hessian times the eigenvector sensitivity, so eigenvectors are not labelled
    directly.  The light subspace (separated from everything else by >= 0.125 M_GUT^2) is first split
    into SM-isotypic components with the exact-integer Casimirs, and the Hessian is diagonalised
    inside each component.
    """
    r2 = float(r0) ** 2
    phi17_weight = np.sum(full[chart.X_SLICE, :] ** 2, axis=0)
    light = (eigenvalues < LIGHT_CUTOFF_OVER_R0_SQUARED * r2) & (phi17_weight < 0.5)
    basis = full[:, light]
    ops = sm_label_operators()
    generic = ops["C3"] + math.pi * ops["C2L"] + 7.0 * math.e * ops["Y2"]
    reduced = basis.T @ generic @ basis
    casimir, rotation = np.linalg.eigh(0.5 * (reduced + reduced.T))
    states = []
    for start, stop in _clusters(casimir, relative=0.0, absolute=1.0e-6):
        component = basis @ rotation[:, start:stop]
        block = component.T @ hessian @ component
        values, inner = np.linalg.eigh(0.5 * (block + block.T))
        for first, last in _clusters(values, relative=0.0, absolute=1.0e-3 * r2):
            modes = component @ inner[:, first:last]
            value = float(np.mean(values[first:last]))
            states.append(
                {
                    "mass_squared": value,
                    "mass_squared_over_r0_squared": value / r2,
                    "mass_over_r0_M_GUT": 0.0 if value < NUMERICAL_ZERO_EIGENVALUE else math.sqrt(value) / float(r0),
                    "real_multiplicity": last - first,
                    "eigenvalue_spread": float(values[last - 1] - values[first]),
                    "sm_content_real": label_subspace(modes),
                    "field_weights": block_weights(modes),
                }
            )
    states = order_light_states(states)
    heavy = ~light & (phi17_weight < 0.5)
    lowest_heavy = int(np.argmin(np.where(heavy, eigenvalues, np.inf)))
    return {
        "window": "projected-Hessian eigenvalues below 5 r0^2, Phi17 radial mode (x0^2/8, decoupled) excluded",
        "method": "SM-isotypic split of the light subspace by exact-integer Casimirs, then Hessian eigenvalues per component",
        "order": (
            f"mass levels ascending (m^2/r0^2 within {LIGHT_LEVEL_TOLERANCE_OVER_R0_SQUARED:g} of a level's lowest value "
            "is one level; the tuned doublet floored to 0 first), then SM label string within a level"
        ),
        "real_dimension": int(np.sum(light)),
        "states": states,
        "lowest_heavy_non_Phi17": {
            "mass_squared": float(eigenvalues[lowest_heavy]),
            "field_weights": block_weights(full[:, [lowest_heavy]]),
        },
    }


def phi17_block_audit(hessian: np.ndarray, x0: Fraction) -> dict[str, Any]:
    """The Phi17 block: (1/32)(|Phi17|^2 - x0^2)^2 only, so radial m^2 = x0^2/8 and no coupling to the rest."""
    others = np.r_[0 : chart.X_SLICE.start, chart.X_SLICE.stop : chart.TOTAL_DIM]
    values = np.linalg.eigvalsh(hessian[chart.X_SLICE, chart.X_SLICE])
    return {
        "block_eigenvalues": [float(value) for value in values],
        "radial_mass_squared": float(values[-1]),
        "exact_radial_mass_squared_x0_squared_over_8": x0 * x0 / 8,
        "radial_deviation_from_exact": abs(float(values[-1]) - float(x0 * x0 / 8)),
        "coupling_to_other_fields_max_abs": float(np.max(np.abs(hessian[chart.X_SLICE][:, others]))),
        "scaling": "r0-independent: GUT scale for x0 >= 1, never an r0^2-scaled intermediate state",
    }


def compiler_light_doublet_quartic(
    state: potential.FieldState,
    coefficients: Mapping[str, float],
    needed: set[str],
    full: np.ndarray,
    eigenvalues: np.ndarray,
    tangent: np.ndarray,
    tolerance: float,
) -> dict[str, Any]:
    """Tree-level quartic of the tuned light doublet from the live compiler (V = lambda (h^dag h)^2).

    Along a unit chart direction u of the doublet, c = grad V(q0+u) + grad V(q0-u) - 2 grad V(q0) and
    Q = u.(Hess V(q0+u) + Hess V(q0-u) - 2 Hess V(q0)).u are exact polynomial differences (only
    H-involving rows change), and lambda_eff = (Q - 3 c.M^+.c)/6 with M the massive projected Hessian
    (the convention of g3_tuned_target_effective_higgs_quartic_v20).
    """
    involves_h = target.involves_fields(target.H_FIELDS)

    def include(direction: Any) -> bool:
        return direction.direction_id in needed and involves_h(direction)

    q0 = chart.pack(state)
    base = target.parameter_rows(state, include=include)
    h_coefficients = {key: value for key, value in coefficients.items() if key in base}
    _, g0, h0 = target.assemble(base, h_coefficients)
    massive = eigenvalues > tolerance
    heavy_vectors = full[:, massive]
    heavy_values = eigenvalues[massive]
    zero_vectors = full[:, np.abs(eigenvalues) <= tolerance]
    single = np.zeros(chart.TOTAL_DIM)
    single[DOUBLET_REAL_X[0]] = 1.0
    equal = np.zeros(chart.TOTAL_DIM)
    equal[list(DOUBLET_REAL_X)] = 0.5
    rows_out = {}
    for name, u in (("Re_h6", single), ("Re_h6789_equal_weights", equal)):
        plus = target.parameter_rows(chart.unpack(q0 + u), include=include)
        minus = target.parameter_rows(chart.unpack(q0 - u), include=include)
        _, gp, hp = target.assemble(plus, h_coefficients)
        _, gm, hm = target.assemble(minus, h_coefficients)
        coupling = gp + gm - 2.0 * g0
        quartic = float(u @ (hp + hm - 2.0 * h0) @ u)
        heavy_components = heavy_vectors.T @ coupling
        shift = 3.0 * float(np.sum(heavy_components**2 / heavy_values))
        rows_out[name] = {
            "lambda_direct": quartic / 6.0,
            "heavy_exchange_shift": shift / 6.0,
            "lambda_eff": (quartic - shift) / 6.0,
            "coupling_vector_norm": float(np.linalg.norm(coupling)),
            "coupling_on_Re_S": float(coupling[chart.S_SLICE.start]),
            "coupling_outside_Re_S_max_abs": float(
                np.max(np.abs(np.delete(coupling, chart.S_SLICE.start)))
            ),
            "coupling_zero_mode_projection_norm": float(np.linalg.norm(zero_vectors.T @ coupling)),
            "coupling_symmetry_tangent_projection_norm": float(np.linalg.norm(tangent.T @ coupling)),
        }
    return {
        "normalization": "V = lambda (h^dag h)^2, canonically normalised h; lambda = Q/6 along a unit chart direction",
        "H_rows": sorted(base),
        "directions": rows_out,
        "lambda_direct": float(np.mean([row["lambda_direct"] for row in rows_out.values()])),
        "lambda_eff": float(np.mean([row["lambda_eff"] for row in rows_out.values()])),
    }


def labelled_spectrum(
    r0: Fraction, tangent: np.ndarray, complement: np.ndarray, eigenvalues: np.ndarray, vectors: np.ndarray
) -> dict[str, Any]:
    rows = []
    for start, stop in _clusters(eigenvalues):
        basis = complement @ vectors[:, start:stop]
        value = float(np.mean(eigenvalues[start:stop]))
        rows.append(
            {
                "mass_squared": value,
                "mass_squared_over_r0_squared": value / float(r0) ** 2,
                "real_multiplicity": stop - start,
                "sm_content_real": label_subspace(basis),
                "field_weights": block_weights(basis),
            }
        )
    return {
        "units": UNITS,
        "labels": "(SU(3)_c, SU(2)_L)_|Y| from exact integer generators; multiplicities in real dimensions",
        "symmetry_tangents": {"real_dimension": tangent.shape[1], "sm_content_real": label_subspace(tangent)},
        "clusters": rows,
        "n_clusters": len(rows),
    }


def h10_audit(
    rows: Mapping[str, Any], exact: Mapping[str, Fraction], hessian: np.ndarray, r0: Fraction, kappa: Fraction
) -> dict[str, Any]:
    block = hessian[chart.H_SLICE, chart.H_SLICE]
    xs, ys = slice(0, None, 2), slice(1, None, 2)
    hermitian = 0.5 * (block[xs, xs] + block[ys, ys]) + 0.5j * (block[ys, xs] - block[xs, ys])
    holomorphic = 0.5 * (block[xs, xs] - block[ys, ys]) - 0.5j * (block[xs, ys] + block[ys, xs])
    others = np.concatenate(
        [np.arange(0, chart.H_SLICE.start), np.arange(chart.H_SLICE.stop, chart.TOTAL_DIM)]
    )
    real_parts = {}
    for label, indices in (
        ("colour_x", [2 * k for k in range(6)]),
        ("colour_y", [2 * k + 1 for k in range(6)]),
        ("weak_x", [2 * k for k in range(6, 10)]),
        ("weak_y", [2 * k + 1 for k in range(6, 10)]),
    ):
        real_parts[label] = np.linalg.eigvalsh(block[np.ix_(indices, indices)]).tolist()
    b_term = 4 * abs(kappa) * r0
    expected = {
        "colour_x": [Fraction(1)] * 6,
        "colour_y": [1 + b_term] * 6,
        "weak_x": [Fraction(0)] * 4,
        "weak_y": [b_term] * 4,
    }
    deviation = max(
        abs(value - float(reference))
        for label in expected
        for value, reference in zip(sorted(real_parts[label]), expected[label], strict=True)
    )
    contributions: dict[str, Any] = {}
    floats = float_coefficients(exact)
    for parameter_id, coefficient in sorted(floats.items()):
        _, _, term = target.assemble(rows, {parameter_id: coefficient})
        term_block = term[chart.H_SLICE, chart.H_SLICE]
        if np.max(np.abs(term_block)) > 1.0e-13:
            contributions[parameter_id] = {
                "colour_real_eigenvalues": _grouped_real(
                    np.linalg.eigvalsh(term_block[np.ix_(range(12), range(12))])
                ),
                "weak_real_eigenvalues": _grouped_real(
                    np.linalg.eigvalsh(term_block[np.ix_(range(12, 20), range(12, 20))])
                ),
            }
    _, _, wedge_hessian = target.assemble(rows, {O46_1_ID: 0.6, O46_54_ID: -1.0})
    wedge_matrix, wedge_holomorphic = target.hermitian_h_mass_matrix(wedge_hessian)
    # Per unit coefficient at |Phi| = 1: O46_B01 = |Phi|^2 N_H gives (colour, weak) = (1, 1); O46_B03 = I_54
    # = (3/5)|Phi|^2 N_H - ||H wedge Phi||^2 (exact wedge identity, P = diag(1_6, 0_4)) gives (-2/5, 3/5).
    exact_per_unit = {
        O46_1_ID: {"colour": Fraction(1), "weak": Fraction(1)},
        O46_54_ID: {"colour": Fraction(-2, 5), "weak": Fraction(3, 5)},
    }
    per_unit: dict[str, Any] = {}
    per_unit_deviation = 0.0
    for parameter_id, expected_unit in exact_per_unit.items():
        _, _, unit_hessian = target.assemble(rows, {parameter_id: 1.0})
        unit_block = unit_hessian[chart.H_SLICE, chart.H_SLICE]
        colour = np.linalg.eigvalsh(unit_block[np.ix_(range(12), range(12))])
        weak = np.linalg.eigvalsh(unit_block[np.ix_(range(12, 20), range(12, 20))])
        per_unit[parameter_id] = {
            "colour": float(np.mean(colour)),
            "colour_spread": float(np.ptp(colour)),
            "weak": float(np.mean(weak)),
            "weak_spread": float(np.ptp(weak)),
        }
        per_unit_deviation = max(
            per_unit_deviation,
            float(np.max(np.abs(colour - float(expected_unit["colour"])))),
            float(np.max(np.abs(weak - float(expected_unit["weak"])))),
        )
    o46_1, o46_54 = exact[O46_1_ID], exact[O46_54_ID]
    doublet_phi_mass = o46_1 * exact_per_unit[O46_1_ID]["weak"] + o46_54 * exact_per_unit[O46_54_ID]["weak"]
    triplet_phi_mass = o46_1 * exact_per_unit[O46_1_ID]["colour"] + o46_54 * exact_per_unit[O46_54_ID]["colour"]
    # SU(5) content of the doublet mass eigenstates: weight in span{z4, z5} (z_k = e_{2k-2} + i e_{2k-1}).
    weak_block = block[np.ix_(range(12, 20), range(12, 20))]
    weak_values, weak_vectors = np.linalg.eigh(weak_block)

    def z_weight(columns: np.ndarray) -> float:
        total = 0.0
        for column in columns.T:
            h_weak = (column[0::2] + 1j * column[1::2]) / SQRT2
            along_z = np.array([h_weak[0] - 1j * h_weak[1], h_weak[2] - 1j * h_weak[3]]) / SQRT2
            total += float(np.vdot(along_z, along_z).real) / float(np.vdot(h_weak, h_weak).real)
        return total / columns.shape[1]

    light_mask = weak_values < 0.5 * b_term
    doublet_composition = {
        "light_doublet_weight_in_span_z4_z5": z_weight(weak_vectors[:, light_mask]),
        "heavy_doublet_weight_in_span_z4_z5": z_weight(weak_vectors[:, ~light_mask]),
        "interpretation": (
            "span{z4, z5} and its conjugate are the doublet parts of the 5 and 5bar of the SU(5) fixed by "
            "sigma_std; weight 1/2 means the light doublet is an equal mixture of the 5 and 5bar doublets "
            "(tan beta = 1 structure: with 10_H-only Yukawas, m_t = m_b at the matching scale)"
        ),
    }
    return {
        "units": UNITS,
        "real_block_eigenvalues": {label: _grouped_real(np.asarray(values)) for label, values in real_parts.items()},
        "exact_expectation": {
            "colour_triplets": "1 (x) and 1 + 4|kappa| r0 (y): from ||H wedge p||^2 = |H_colour|^2 plus the kappa B-term",
            "weak_doublets": "0 (x, tuned light doublet) and 4|kappa| r0 (y)",
            "4|kappa|r0": b_term,
        },
        "max_deviation_from_exact_expectation": deviation,
        "H_block_decoupled_from_other_fields": float(np.max(np.abs(hessian[chart.H_SLICE][:, others]))),
        "hermitian_part": target.sm_branch_spectrum(hermitian),
        "holomorphic_part_B": target.sm_branch_spectrum(holomorphic),
        "wedge_combination_(3/5)O46_1-O46_54": {
            "hermitian_matrix_minus_diag_1x6_0x4": float(np.max(np.abs(wedge_matrix - np.diag([1.0] * 6 + [0.0] * 4)))),
            "holomorphic_residual": wedge_holomorphic,
        },
        "doublet_triplet_splitting": {
            "colour_triplet_mass_squared_min": float(min(real_parts["colour_x"] + real_parts["colour_y"])),
            "light_doublet_mass_squared": float(min(real_parts["weak_x"])),
            "heavy_doublet_mass_squared": float(max(real_parts["weak_y"])),
            "scope": "10_H only; the 126bar has light coloured states below M_I (light_spectrum)",
            "mechanism": (
                "At the tuned ratio O46_1 : O46_54 = 3/5 : -1 the Phi-H quartics combine into ||H wedge Phi||^2 = "
                "H^dag diag(1_6, 0_4) H, which gives the 10_H colour triplets M_GUT^2 and the doublets no Phi-induced "
                "mass; the remaining doublet mass O06 - 2|kappa| r0 is tuned to zero. Neither relation is enforced by "
                "a symmetry: adding eps > 0 to O46_1 adds eps |Phi|^2 N_H >= 0, keeps V >= V0 with the same global "
                "minimum, and gives the doublets eps M_GUT^2. Doublet-triplet splitting is therefore tuned, not automatic."
            ),
            "phi_induced_mass_per_unit_coefficient_exact": exact_per_unit,
            "phi_induced_mass_per_unit_coefficient_compiler": per_unit,
            "per_unit_max_deviation_from_exact": per_unit_deviation,
            "doublet_phi_induced_mass_squared": {
                "formula": "(O46_1 + (3/5) O46_54) |Phi|^2",
                "value_at_candidate": doublet_phi_mass,
            },
            "triplet_phi_induced_mass_squared": {
                "formula": "(O46_1 - (2/5) O46_54) |Phi|^2",
                "value_at_candidate": triplet_phi_mass,
            },
            "tuned_relations": [
                "O46_1 = -(3/5) O46_54 (doublet Phi-induced mass zero; precision ~ (m_h/M_GUT)^2)",
                "O06 = 2|kappa| r0 (doublet B-term cancelled; precision ~ (m_h/M_I)^2)",
                "O05 = (1/8)(4 - 2 r0^2) against the Phi-induced O14/O44 masses on the (10bar,1,3) "
                "(1/2 - 1 + 1/2 - r0^2/4 at |Phi| = 1): the intermediate scale itself is a cancellation of O(1) "
                "couplings to precision ~ (M_I/M_GUT)^2 ~ 4e-9",
            ],
            "natural": False,
            "doublet_composition": doublet_composition,
        },
        "h_mass_contributions_by_parameter": contributions,
    }


def compiler_section(*, heavy: bool) -> dict[str, Any]:
    values = benchmark_r0_values()
    labels = list(values) if heavy else ["1/5"]
    return {label: compiler_point_audit(values[label], spectrum=(label == "1/5")) for label in labels}


# ---------------------------------------------------------------------------
# Hierarchy, RG-anchor consistency and the light-doublet quartic.
# ---------------------------------------------------------------------------

_LABEL_PATTERN = re.compile(r"\((\d+),(\d+)\)_\|Y\|=(\d+(?:/\d+)?)")
SU3_REPS = {"1": (1, Fraction(0)), "3": (3, Fraction(1, 2)), "6": (6, Fraction(5, 2)), "8": (8, Fraction(3))}
SU2_REPS = {"1": (1, Fraction(0)), "2": (2, Fraction(1, 2)), "3": (3, Fraction(2))}
SU4_REPS = {
    "1": (1, Fraction(0)),
    "4": (4, Fraction(1, 2)),
    "4bar": (4, Fraction(1, 2)),
    "10bar": (10, Fraction(3)),
    "15": (15, Fraction(4)),
}
WEYL, COMPLEX_SCALAR = Fraction(2, 3), Fraction(1, 3)
PS_FAMILIES = ((("4", "2", "1"), 3), (("4bar", "1", "2"), 3))
SM_FAMILIES = (
    ("3", "2", Fraction(1, 6)),
    ("3", "1", Fraction(-2, 3)),
    ("3", "1", Fraction(1, 3)),
    ("1", "2", Fraction(-1, 2)),
    ("1", "1", Fraction(1)),
)
ANCHOR_PS_SCALARS = ((("1", "2", "2"), 1), (("10bar", "1", "3"), 1), (("15", "2", "2"), 1))
CANDIDATE_PS_SCALARS = ((("1", "2", "2"), 1), (("10bar", "1", "3"), 1))


def ps_one_loop_b(complex_scalars: Sequence[tuple[tuple[str, str, str], int]]) -> tuple[Fraction, ...]:
    """(SU(4), SU(2)_L, SU(2)_R) one-loop b: gauge + 3 families + the listed complex scalars."""
    b = [Fraction(-11, 3) * 4, Fraction(-11, 3) * 2, Fraction(-11, 3) * 2]

    def add(reps: tuple[str, str, str], count: int, weight: Fraction) -> None:
        data = (SU4_REPS[reps[0]], SU2_REPS[reps[1]], SU2_REPS[reps[2]])
        for i in range(3):
            others = math.prod(data[j][0] for j in range(3) if j != i)
            b[i] += weight * count * data[i][1] * others

    for reps, count in PS_FAMILIES:
        add(reps, count, WEYL)
    for reps, count in complex_scalars:
        add(reps, count, COMPLEX_SCALAR)
    return tuple(b)


def sm_scalar_delta_b(colour: str, weak: str, hypercharge_abs: Fraction, count: Fraction) -> tuple[Fraction, ...]:
    """(U(1)_Y GUT-normalised, SU(2)_L, SU(3)_c) one-loop b of `count` complex scalars."""
    d3, t3 = SU3_REPS[colour]
    d2, t2 = SU2_REPS[weak]
    return (
        COMPLEX_SCALAR * count * Fraction(3, 5) * hypercharge_abs**2 * d3 * d2,
        COMPLEX_SCALAR * count * t2 * d3,
        COMPLEX_SCALAR * count * t3 * d2,
    )


def sm_one_loop_b(n_doublets: int) -> tuple[Fraction, ...]:
    b = [Fraction(0), Fraction(-22, 3), Fraction(-11)]
    for colour, weak, hypercharge_value in SM_FAMILIES:
        d3, t3 = SU3_REPS[colour]
        d2, t2 = SU2_REPS[weak]
        b[0] += WEYL * 3 * Fraction(3, 5) * hypercharge_value**2 * d3 * d2
        b[1] += WEYL * 3 * t2 * d3
        b[2] += WEYL * 3 * t3 * d2
    doublets = sm_scalar_delta_b("1", "2", Fraction(1, 2), Fraction(n_doublets))
    return tuple(value + extra for value, extra in zip(b, doublets, strict=True))


def _one_loop_chain(
    log_mi: float, b_low: Sequence[Any], b_ps: Sequence[Any], thresholds: Sequence[tuple[float, Sequence[Any]]]
) -> tuple[float, float, float]:
    """two_loop_thresholds_v20.chain at one loop, plus extra content between ratio * M_I and M_I."""
    mi = 10.0**log_mi
    ell = math.log(mi / rg_anchor.MZ) / (2.0 * math.pi)
    inverse = [rg_anchor.A1 - float(b_low[0]) * ell, rg_anchor.A2 - float(b_low[1]) * ell, rg_anchor.A3 - float(b_low[2]) * ell]
    for ratio, delta in thresholds:
        extra = math.log(1.0 / ratio) / (2.0 * math.pi)
        inverse = [value - float(delta[k]) * extra for k, value in enumerate(inverse)]
    i1, i2, i3 = inverse
    i4, i_l = i3, i2
    i_r = (5.0 * i1 - 2.0 * i4) / 3.0
    ln_mu = 2.0 * math.pi * (i4 - i_l) / (float(b_ps[0]) - float(b_ps[1]))
    i4u = i4 - float(b_ps[0]) * ln_mu / (2.0 * math.pi)
    iru = i_r - float(b_ps[2]) * ln_mu / (2.0 * math.pi)
    return i4u - iru, mi * math.exp(ln_mu), i4u


def solve_one_loop(
    b_low: Sequence[Any], b_ps: Sequence[Any], thresholds: Sequence[tuple[float, Sequence[Any]]] = ()
) -> dict[str, Any]:
    try:
        log_mi = rg_anchor.bracketed_root(lambda x: _one_loop_chain(x, b_low, b_ps, thresholds)[0], 4.0, 15.9, xtol=1.0e-12)
    except ValueError as error:
        return {"solved": False, "reason": str(error)}
    residual, m_gut, alpha_inverse = _one_loop_chain(log_mi, b_low, b_ps, thresholds)
    m_i = 10.0**log_mi
    return {
        "solved": True,
        "M_I_GeV": m_i,
        "M_GUT_GeV": m_gut,
        "alpha_inv_GUT": alpha_inverse,
        "M_I_over_M_GUT": m_i / m_gut,
        "matching_residual": residual,
    }


def _parse_sm_label(label: str) -> tuple[str, str, Fraction]:
    match = _LABEL_PATTERN.fullmatch(label)
    if match is None:
        raise ValueError(f"unparsed SM label {label!r}")
    return match.group(1), match.group(2), Fraction(match.group(3))


def sub_m_i_thresholds(physical_states: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Gauge-charged light states strictly below M_I at the physical benchmark, with their one-loop Delta b."""
    rows = []
    for state in physical_states:
        ratio = float(state["mass_over_r0_M_GUT"])
        for label, real_multiplicity in state["sm_content_real"].items():
            colour, weak, hypercharge_abs = _parse_sm_label(label)
            if colour == "1" and weak == "1" and hypercharge_abs == 0:
                continue  # gauge singlet
            if float(state["mass_squared"]) < NUMERICAL_ZERO_EIGENVALUE:
                if (label, real_multiplicity) != ("(1,2)_|Y|=1/2", LIGHT_DOUBLET_REAL_DIMENSION):
                    raise ValueError(f"unexpected massless state {label}: {real_multiplicity}")
                continue  # the tuned light doublet: the SM Higgs, already in the low-energy b
            if ratio >= 1.0 - 1.0e-6:
                continue  # at or above M_I: part of the PS-stage content
            count = Fraction(int(real_multiplicity), 2 * SU3_REPS[colour][0] * SU2_REPS[weak][0])
            rows.append(
                {
                    "label": label,
                    "real_multiplicity": int(real_multiplicity),
                    "complex_multiplets": count,
                    "mass_over_M_I": ratio,
                    "delta_b_Y_L_c": sm_scalar_delta_b(colour, weak, hypercharge_abs, count),
                }
            )
    return rows


def rg_anchor_section(physical_states: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Does the candidate reproduce the field content behind the manuscript's Pati-Salam RG anchor?"""
    anchor_ps = ps_one_loop_b(ANCHOR_PS_SCALARS)
    anchor_low = sm_one_loop_b(2)
    candidate_ps = ps_one_loop_b(CANDIDATE_PS_SCALARS)
    candidate_low = sm_one_loop_b(1)
    repository = rg_anchor.solve_unification(False)
    local = solve_one_loop(anchor_low, anchor_ps)
    reproduced = bool(
        local["solved"]
        and all(
            math.isclose(local[key], repository[key], rel_tol=1.0e-9)
            for key in ("M_I_GeV", "M_GUT_GeV", "alpha_inv_GUT")
        )
    )
    betas_reproduced = bool(
        all(math.isclose(float(a), float(b), rel_tol=0, abs_tol=1.0e-15) for a, b in zip(anchor_ps, rg_anchor.B_PS, strict=True))
        and all(math.isclose(float(a), float(b), rel_tol=0, abs_tol=1.0e-15) for a, b in zip(anchor_low, rg_anchor.B_LOW, strict=True))
    )
    solutions: dict[str, Any] = {
        "anchor_repository_two_loop_thresholds_v20": {key: repository[key] for key in ("M_I_GeV", "M_GUT_GeV", "alpha_inv_GUT")},
        "anchor_content_local_chain": local,
        "candidate_PS_content_with_2HDM_below_M_I": solve_one_loop(anchor_low, candidate_ps),
        "candidate_PS_content_with_1HDM_below_M_I": solve_one_loop(candidate_low, candidate_ps),
    }
    thresholds: list[dict[str, Any]] | str = "requires the M_I/M_GUT compiler benchmark (not run in --light mode)"
    if physical_states is not None:
        thresholds = sub_m_i_thresholds(physical_states)
        solutions["candidate_content_with_1HDM_and_sub_M_I_remnants"] = solve_one_loop(
            candidate_low,
            candidate_ps,
            [(row["mass_over_M_I"], row["delta_b_Y_L_c"]) for row in thresholds],
        )
    content_reproduced = bool(
        tuple(candidate_ps) == tuple(anchor_ps)
        and tuple(candidate_low) == tuple(anchor_low)
        and isinstance(thresholds, list)
        and not thresholds
    )
    return {
        "anchor_source": "two_loop_thresholds_v20 one-loop chain (manuscript 'Benchmark and inputs'; so10_axion_v17_engine S3)",
        "anchor_field_content": {
            "below_M_I": "SM gauge + 3 families + 2 Higgs doublets (2HDM)",
            "M_I_to_M_GUT": "PS gauge + 3 families + complex (1,2,2) + complex (10bar,1,3) + complex (15,2,2)",
        },
        "anchor_betas_repository": {"B_LOW": list(rg_anchor.B_LOW), "B_PS": list(rg_anchor.B_PS)},
        "anchor_betas_from_field_content": {"B_LOW": anchor_low, "B_PS": anchor_ps},
        "anchor_betas_reproduced_from_field_content": betas_reproduced,
        "candidate_field_content": {
            "below_M_I": (
                "SM gauge + 3 families + ONE light doublet (1HDM; the partner is at exactly M_I) + six gauge-charged "
                "complex (10bar,1,3) remnants between 0.10 M_I and 0.33 M_I (sub_M_I_thresholds) and the neutral "
                "Sigma radial mode at M_I/sqrt(2)"
            ),
            "M_I_to_M_GUT": (
                "PS gauge + 3 families + complex (1,2,2) (10_H doublets) + complex (10bar,1,3); the 126bar (15,2,2) "
                "sits at m^2 = 0.45-0.50 M_GUT^2 at r0 = 1/5 and 0.5 M_GUT^2 as r0 -> 0 (~0.7 M_GUT), forced by "
                "(1/8)||(M_Phi - 2)Sigma||^2 with M_p = 0 on it"
            ),
        },
        "candidate_betas": {"B_LOW_1HDM": candidate_low, "B_PS": candidate_ps},
        "beta_differences_candidate_minus_anchor": {
            "B_LOW": tuple(c - a for c, a in zip(candidate_low, anchor_low, strict=True)),
            "B_PS": tuple(c - a for c, a in zip(candidate_ps, anchor_ps, strict=True)),
        },
        "sub_M_I_thresholds": thresholds,
        "one_loop_solutions": solutions,
        "anchor_reproduced_by_local_chain": reproduced,
        "field_content_reproduced": content_reproduced,
        "breaking_route_matches_anchor": "SO(10) -> PS (Phi = p, no D parity) -> SM (Y = 0 member of (10bar,1,3)): yes",
        "caveats": (
            "Indicative: one loop, tree-level threshold masses at their physical-benchmark ratios m/M_I (r0-independent "
            "at leading order), no matching corrections or two-loop shifts, and the chart unit |Phi| = 1 identified "
            "with M_GUT and r0 with M_I/M_GUT without gauge-coupling factors."
        ),
        "conclusion": (
            "Only the breaking route matches the anchor. Its beta coefficients assume a light (15,2,2) above M_I and a "
            "2HDM below M_I; this candidate provides neither and adds sub-M_I coloured scalars, so the anchor's M_I and "
            "M_GUT (and r0 = M_I/M_GUT) are borrowed, not reproduced."
        ),
    }


def hierarchy_section(physical_states: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Illustrative GeV masses at r0 = M_I/M_GUT using the anchor's scales (which this content does not reproduce)."""
    anchor = hierarchy_anchor()
    r0 = anchor["r0_physical"]
    m_gut = anchor["M_GUT_GeV"]
    m_i = anchor["M_I_GeV"]
    kappa = -r0 / 4
    b_term = float(4 * abs(kappa) * r0)
    metadata = g2_audit._physical_hierarchy_metadata(g2_audit.physical_hierarchy_state())
    phi17_scale = float(metadata["Phi17_scale_GeV"])
    x0_canonical = phi17_scale / m_gut
    masses: dict[str, Any] = {
        "H10_colour_triplets": [m_gut, m_gut * math.sqrt(1.0 + b_term)],
        "H10_light_doublet": 0.0,
        "H10_heavy_doublet_partner": m_gut * math.sqrt(b_term),
        "S_radial": 2.0 * m_i,
        "Phi17_radial_at_benchmark_x0_1": m_gut * float(X0) / math.sqrt(8.0),
        "Phi17_radial_at_canonical_x0": m_gut * x0_canonical / math.sqrt(8.0),
        "lightest_massive_non_H_state": m_gut * float(r0) * math.sqrt(float(LIGHTEST_MASSIVE_OVER_R0_SQUARED)),
        "Sigma_126bar_15_2_2": m_gut * math.sqrt(0.5),
        "formulae": (
            "H10: M_T = M_GUT (x), M_GUT sqrt(1 + r0^2) (y); M_D' = r0 M_GUT = M_I. S radial 2 r0 M_GUT. Phi17 radial "
            "x0 M_GUT/sqrt(8), r0-independent. Lightest massive state M_I/sqrt(96). Sigma (15,2,2) ~ M_GUT/sqrt(2) "
            "(m^2 -> 1/2 as r0 -> 0)."
        ),
    }
    coloured_below: list[dict[str, Any]] | str = "requires the M_I/M_GUT compiler benchmark (not run in --light mode)"
    if physical_states is not None:
        light_rows = []
        coloured_below = []
        for state in physical_states:
            ratio = float(state["mass_over_r0_M_GUT"])
            row = {
                "sm_content_real": dict(state["sm_content_real"]),
                "field_weights": dict(state["field_weights"]),
                "mass_squared_over_r0_squared": float(state["mass_squared_over_r0_squared"]),
                "mass_over_M_I": ratio,
                "mass_GeV": ratio * m_i,
            }
            light_rows.append(row)
            coloured = any(_parse_sm_label(label)[0] != "1" for label in state["sm_content_real"])
            if coloured and ratio < 1.0:
                coloured_below.append(row)
        masses["light_states_at_physical_r0"] = light_rows
    return {
        "status": (
            "ILLUSTRATIVE: M_GUT and M_I are the anchor's (gauged_u1x_g2_derivative_audit_v20), and this candidate's "
            "field content does not reproduce the anchor (rg_anchor_consistency); the GeV numbers are not predictions"
        ),
        "anchor": {key: anchor[key] for key in ("M_GUT_GeV", "M_I_GeV", "ratio_float", "source")},
        "r0_physical": r0,
        "r0_physical_float": float(r0),
        "unit_identification": (
            "chart unit |Phi| = 1 identified with the RG M_GUT and r0 = |Sigma|/|Phi| with M_I/M_GUT (a vev ratio), "
            "without gauge-coupling or group-theory factors"
        ),
        "breaking_route": (
            "SO(10) -> Pati-Salam at M_GUT (Phi = p) -> SM at M_I (Sigma = r0 sigma_std): the anchor's route (chain "
            "topology only; the anchor's field content is not reproduced)"
        ),
        "benchmark_x0": X0,
        "canonical_Phi17_scale_GeV": phi17_scale,
        "canonical_x0": x0_canonical,
        "benchmark_uses_canonical_phi17_scale": False,
        "phi17_note": (
            "Every compiler benchmark, including 'M_I/M_GUT', keeps x0 = 1 (Phi17 at M_GUT), not the canonical "
            "physical_hierarchy_state value Phi17 = 1e17 GeV (x0 ~ 10.08). The exact identity contains Phi17 only in "
            "(1/32)(|Phi17|^2 - x0^2)^2 and the compiler Phi17 block is decoupled (Phi17_block), so x0 changes only "
            "the Phi17 radial mass x0^2/8 M_GUT^2 and V0; the exact certificate holds for every x0 > 0."
        ),
        "tree_masses_GeV_at_physical_r0": masses,
        "coloured_states_below_M_I": coloured_below,
        "doublet_tuning_precision": {
            "m_h_GeV": M_H_OBSERVED_GEV,
            "O46_ratio_(m_h/M_GUT)^2": (M_H_OBSERVED_GEV / m_gut) ** 2,
            "O06_(m_h/M_I)^2": (M_H_OBSERVED_GEV / m_i) ** 2,
        },
    }


def exact_light_doublet_quartic(r0: Fraction, kappa: Fraction | None = None) -> dict[str, Fraction]:
    kappa = -r0 / 4 if kappa is None else kappa
    shift = kappa * kappa / (4 * r0 * r0)
    return {"lambda_direct": Fraction(2), "S_exchange_shift": shift, "lambda_eff": 2 - shift}


def lambda_at_top_from(lambda_matching: float, matching_scale: float) -> float:
    """lambda(M_t) from lambda(mu): SM couplings run up, lambda replaced, then run down (two loops)."""
    high = stability.run_sm(stability.BUTTAZZO_INPUTS, stability.MT_REF, matching_scale, loops=2)
    high["lam"] = lambda_matching
    return float(stability.run_sm(high, matching_scale, stability.MT_REF, loops=2)["lam"])


def light_doublet_quartic_section() -> dict[str, Any]:
    lambda_eff = exact_light_doublet_quartic(R0)["lambda_eff"]
    m_i = hierarchy_anchor()["M_I_GeV"]
    predictions = {}
    for label, value in (("lambda_eff_127_over_64", float(lambda_eff)), ("lambda_zero", 0.0)):
        top = lambda_at_top_from(value, m_i)
        predictions[label] = {"lambda_M_I": value, "lambda_at_mt": top, **stability.higgs_mass_estimates(top)}
    required = float(stability.sm_profile(loops=2).lam(m_i))
    return {
        "normalization": "V = lambda (h^dag h)^2, canonically normalised h (g3_tuned_target_effective_higgs_quartic_v20)",
        "derivation": [
            "direct: 2 N_H^2 (O36_B01 = O36_B02 = 2, Sym^2(10) = 1 + 54) with h^dag h = N_H on the doublet gives 2; "
            "||H wedge Phi||^2 vanishes on doublets (P = diag(1_6, 0_4)); the map has no H-Sigma or H-Phi17 terms",
            "exchange: the only |h|^2-heavy trilinear is 2 kappa Re(conj(H.H) conj(S)) = sqrt(2) kappa |h|^2 sigma_S "
            "(sigma_S = Re S chart coordinate) with m_S^2 = 4 r0^2, giving -kappa^2/(4 r0^2)",
            "lambda_eff = 2 - kappa^2/(4 r0^2) = 127/64 at kappa = -r0/4, independent of r0",
        ],
        "exact_by_benchmark": {label: exact_light_doublet_quartic(r0) for label, r0 in benchmark_r0_values().items()},
        "lambda_eff": lambda_eff,
        "global_minimality_forces_lambda_eff_nonnegative": (
            "V >= V0 with the doublet exactly massless implies V_eff(h) = V0 + lambda_eff (h^dag h)^2 + ... >= V0, so "
            "lambda_eff >= 0 at tree level for every member of this family"
        ),
        "conditional_sm_running": {
            "scheme": (
                "two-loop SM RGEs of g3_physical_hierarchy_higgs_stability_v20 (Buttazzo et al. 2013 inputs at "
                "M_t = 173.34 GeV), tree-level matching lambda(M_I) = lambda_eff at the anchor M_I"
            ),
            "matching_scale_GeV": m_i,
            "predictions": predictions,
            "lambda_M_I_required_for_sm_two_loop": required,
            "applicability": (
                "Conditional: assumes pure SM running below M_I and the anchor's M_I. The candidate has sub-M_I "
                "coloured scalars, a tan beta = 1 light doublet, and a field content that does not reproduce the "
                "anchor's M_I."
            ),
        },
        "higgs_mass_compatible": bool(abs(float(lambda_eff) - required) < 1.0e-2),
        "conclusion": (
            f"lambda_eff = 127/64 gives m_h ~ {predictions['lambda_eff_127_over_64']['m_h_tree_GeV']:.0f} GeV under "
            f"conditional SM running, while the measured Higgs mass needs lambda(M_I) = {required:.4f} < 0 at M_t = "
            f"{stability.MT_REF} GeV, which global minimality forbids at tree level for this family (the sign of the "
            "required lambda(M_I) is M_t-dependent at ~2 sigma; lambda(M_I) = 0 gives m_h ~ "
            f"{predictions['lambda_zero']['m_h_tree_GeV']:.0f} GeV at tree level, within a few GeV of the measured value)."
        ),
    }


# ---------------------------------------------------------------------------
# Fast evaluator of the SOS form (value and analytic gradient).
# ---------------------------------------------------------------------------

THREE_INDICES = tuple(itertools.combinations(range(10), 3))
THREE_INDEX = {indices: index for index, indices in enumerate(THREE_INDICES)}


@lru_cache(maxsize=1)
def _fast_tensors() -> dict[str, Any]:
    m_real, m_imaginary = a_square_source.integer_cubic_operators()
    c_real, c_imaginary = a_square_source.integer_contraction_tensor()
    generators = sigma_source._generators()
    interior = np.zeros((10, len(THREE_INDICES), chart.PHI_DIM))
    for column, indices in enumerate(chart.PHI_INDICES):
        for vector_index in range(10):
            for target_indices, value in direct.interior({indices: 1.0 + 0.0j}, vector_index).items():
                interior[vector_index, THREE_INDEX[target_indices], column] = complex(value).real
    M = m_real.astype(float) + 1j * m_imaginary.astype(float)
    return {
        "M": M,
        "M_flat": M.reshape(chart.PHI_DIM, -1),
        "C": c_real.astype(float) + 1j * c_imaginary.astype(float),
        "G": [sparse.csr_matrix(g) for g in generators],
        "K210": phi_source.pair_casimir_sparse(),
        "interior": interior,
        "polys": {channel: [float(c) for c in sigma_source._poly(channel)] for channel in SELF_CHANNELS},
    }


class SosFormPotential:
    """V on the 486 chart written as the adapted SOS; ``quartic_only`` keeps V4."""

    def __init__(
        self,
        r0: float,
        x0: float,
        kappa: float,
        o06: float,
        *,
        weights: Mapping[str, Fraction] = SWAPPED_SELF_WEIGHTS,
        quartic_only: bool = False,
    ) -> None:
        self.r0, self.x0, self.kappa, self.o06 = float(r0), float(x0), float(kappa), float(o06)
        self.t = float(SIGMA_SCALE)
        self.weights = {channel: float(value) for channel, value in weights.items()}
        self.quartic_only = quartic_only
        self.tensors = _fast_tensors()
        self.j = {name: float(value) for name, value in phi_source.EXPECTED_J_COUPLINGS.items()}

    def _k126(self, pair: np.ndarray) -> np.ndarray:
        output = np.zeros_like(pair)
        for g in self.tensors["G"]:
            output += g @ (g @ pair.T).T
        return output

    def _fields(self, q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, complex, complex]:
        h = (q[chart.H_SLICE][0::2] + 1j * q[chart.H_SLICE][1::2]) / SQRT2
        z = (q[chart.SIGMA_SLICE][0::2] + 1j * q[chart.SIGMA_SLICE][1::2]) / SQRT2
        s = complex(q[chart.S_SLICE][0], q[chart.S_SLICE][1]) / SQRT2
        x = complex(q[chart.X_SLICE][0], q[chart.X_SLICE][1]) / SQRT2
        return np.array(q[chart.PHI_SLICE]), h, z, s, x

    def value_grad(self, q: np.ndarray) -> tuple[float, np.ndarray]:
        q = np.asarray(q, dtype=float)
        phi, h, z, s, x = self._fields(q)
        quartic = self.quartic_only
        T = self.tensors
        g_phi = np.zeros(chart.PHI_DIM)
        g_h = np.zeros(10, dtype=complex)
        g_z = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=complex)
        g_s = 0j
        g_x = 0j
        value = 0.0
        # Phi self potential: -2|Phi|^2 + sum_k c_k <pair, K^k pair>.
        pair = np.outer(phi, phi).reshape(-1)
        powers = {0: pair}
        current = pair
        for degree in range(1, 5):
            current = T["K210"] @ current
            powers[degree] = current
        if not quartic:
            value += -2.0 * float(phi @ phi)
            g_phi += -4.0 * phi
        for name, degree in (("J0", 0), ("J2", 2), ("J3", 3), ("J4", 4)):
            value += self.j[name] * float(pair @ powers[degree])
            g_phi += self.j[name] * 4.0 * (powers[degree].reshape(chart.PHI_DIM, chart.PHI_DIM) @ phi)
        # Sigma self projectors.
        zz = np.outer(z, z)
        pair_powers = [zz]
        for _ in range(3):
            pair_powers.append(self._k126(pair_powers[-1]))
        norm_sigma = float(np.vdot(z, z).real)
        for channel, weight in self.weights.items():
            projected = sum(c * pair_powers[i] for i, c in enumerate(T["polys"][channel]))
            value += self.t * weight * float(np.vdot(projected, projected).real)
            g_z += self.t * weight * 2.0 * (projected @ np.conj(z))
        shift = 0.0 if quartic else 2.0
        if not quartic:
            value += -2.0 * self.t * self.r0**2 * norm_sigma
            g_z += -2.0 * self.t * self.r0**2 * z
        # (1/8) ||(M_Phi - 2) Sigma||^2 and (1/8) ||C_Phi Sigma||^2.
        m_phi = np.tensordot(phi, T["M"], axes=(0, 0))
        w = m_phi @ z - shift * z
        value += self.t * float(np.vdot(w, w).real)
        g_z += self.t * (m_phi @ w - shift * w)
        g_phi += self.t * 2.0 * np.real(T["M_flat"] @ np.outer(np.conj(w), z).ravel())
        c_z = np.tensordot(T["C"], z, axes=(2, 0))
        u = c_z @ phi
        value += self.t * float(np.vdot(u, u).real)
        c_phi = np.tensordot(T["C"], phi, axes=(1, 0))
        g_z += self.t * (c_phi.conj().T @ u)
        g_phi += self.t * 2.0 * np.real(c_z.T @ np.conj(u))
        # H, S and Phi17.
        norm_h = float(np.vdot(h, h).real)
        value += 2.0 * norm_h**2
        g_h += 4.0 * norm_h * h
        if not quartic:
            value += self.o06 * norm_h
            g_h += self.o06 * h
            hh = complex(np.dot(h, h))
            value += 2.0 * self.kappa * float(np.real(np.conj(hh) * np.conj(s)))
            g_h += 2.0 * self.kappa * np.conj(s) * np.conj(h)
            g_s += self.kappa * np.conj(hh)
        y = np.tensordot(T["interior"], phi, axes=(2, 0))
        v = h @ y
        phi_norm = float(phi @ phi)
        value += phi_norm * norm_h - float(np.vdot(v, v).real)
        g_phi += 2.0 * phi * norm_h - 2.0 * np.real(np.einsum("t,i,itp->p", np.conj(v), h, T["interior"], optimize=True))
        g_h += phi_norm * h - (y @ y.T) @ h
        ss, xx = abs(s) ** 2, abs(x) ** 2
        value += ss**2 + xx**2 / 32.0
        g_s += 2.0 * ss * s
        g_x += 2.0 * xx * x / 32.0
        if not quartic:
            value += -2.0 * self.r0**2 * ss - (self.x0**2 / 16.0) * xx
            g_s += -2.0 * self.r0**2 * s
            g_x += -(self.x0**2 / 16.0) * x
        gradient = np.zeros(chart.TOTAL_DIM)
        gradient[chart.PHI_SLICE] = g_phi
        gradient[chart.H_SLICE] = chart._pack_complex_interleaved(g_h)
        gradient[chart.SIGMA_SLICE] = chart._pack_complex_interleaved(g_z)
        gradient[chart.S_SLICE] = chart._pack_complex_interleaved(np.asarray([g_s]))
        gradient[chart.X_SLICE] = chart._pack_complex_interleaved(np.asarray([g_x]))
        return value, gradient

    def value(self, q: np.ndarray) -> float:
        return self.value_grad(q)[0]

    def invariants(self, q: np.ndarray) -> dict[str, float]:
        phi, h, z, s, x = self._fields(np.asarray(q, dtype=float))
        T = self.tensors
        pair = np.outer(phi, phi).reshape(-1)
        powers = {0: pair}
        current = pair
        for degree in range(1, 5):
            current = T["K210"] @ current
            powers[degree] = current
        quartic_phi = sum(self.j[name] * float(pair @ powers[d]) for name, d in (("J0", 0), ("J2", 2), ("J3", 3), ("J4", 4)))
        zz = np.outer(z, z)
        pair_powers = [zz]
        for _ in range(3):
            pair_powers.append(self._k126(pair_powers[-1]))
        norm_sigma = float(np.vdot(z, z).real)
        fractions = {}
        for channel in SELF_CHANNELS:
            projected = sum(c * pair_powers[i] for i, c in enumerate(T["polys"][channel]))
            fractions[channel] = float(np.vdot(projected, projected).real) / max(norm_sigma**2, 1.0e-300)
        m_phi = np.tensordot(phi, T["M"], axes=(0, 0))
        return {
            "Phi_norm_squared": float(phi @ phi),
            "V_Phi_plus_1": -2.0 * float(phi @ phi) + quartic_phi + 1.0,
            "N_Sigma": norm_sigma,
            "Sigma_2772bar_fraction": fractions["2772bar"],
            "Sigma_purity_defect": 1.0 - fractions["2772bar"],
            "A_shift_norm": float(np.linalg.norm(m_phi @ z - 2.0 * z)),
            "C_norm": float(np.linalg.norm(np.tensordot(T["C"], z, axes=(2, 0)) @ phi)),
            "N_H": float(np.vdot(h, h).real),
            "S_abs": abs(s),
            "Phi17_abs": abs(x),
        }


def fast_potential(r0: Fraction = R0, x0: Fraction = X0, *, quartic_only: bool = False) -> SosFormPotential:
    kappa = -r0 / 4
    return SosFormPotential(float(r0), float(x0), float(kappa), float(2 * abs(kappa) * r0), quartic_only=quartic_only)


def compiler_value(q: np.ndarray, coefficients: Mapping[str, float]) -> float:
    return potential.potential_value(potential.evaluate_directions(chart.unpack(q)), coefficients)


# ---------------------------------------------------------------------------
# Numerical global search.
# ---------------------------------------------------------------------------


def _random_block(rng: np.random.Generator, block: slice, scale: float) -> np.ndarray:
    values = rng.normal(size=block.stop - block.start)
    return values / np.linalg.norm(values) * scale


def random_start(kind: str, rng: np.random.Generator, r0: float, x0: float) -> np.ndarray:
    q = np.zeros(chart.TOTAL_DIM)
    p_vector = chart.pack(candidate_state(R0, X0))[chart.PHI_SLICE]
    if kind == "generic":
        q[chart.PHI_SLICE] = _random_block(rng, chart.PHI_SLICE, rng.uniform(0.3, 1.5))
        scales = {chart.H_SLICE: 0.5, chart.SIGMA_SLICE: max(3.0 * r0, 0.3), chart.S_SLICE: 3.0 * r0, chart.X_SLICE: 1.5 * x0}
    elif kind == "phi_near_p":
        noise = _random_block(rng, chart.PHI_SLICE, 0.4)
        q[chart.PHI_SLICE] = p_vector + noise
        scales = {chart.H_SLICE: 0.05, chart.SIGMA_SLICE: 2.0 * SQRT2 * r0, chart.S_SLICE: 2.0 * r0, chart.X_SLICE: 1.5 * x0}
    elif kind == "large_field":
        q[chart.PHI_SLICE] = _random_block(rng, chart.PHI_SLICE, rng.uniform(1.0, 3.0))
        scales = {chart.H_SLICE: 1.5, chart.SIGMA_SLICE: 2.0, chart.S_SLICE: 1.5, chart.X_SLICE: 3.0 * x0}
    elif kind == "sigma_dominated":
        q[chart.PHI_SLICE] = _random_block(rng, chart.PHI_SLICE, 0.1)
        scales = {chart.H_SLICE: 0.1, chart.SIGMA_SLICE: 1.0, chart.S_SLICE: r0, chart.X_SLICE: x0}
    else:
        raise ValueError(kind)
    for block, scale in scales.items():
        q[block] = _random_block(rng, block, scale * rng.uniform(0.3, 1.3))
    return q


def local_minimize(fast: SosFormPotential, q0: np.ndarray, *, maxiter: int = 20000) -> tuple[np.ndarray, Any]:
    result = minimize(
        fast.value_grad,
        np.asarray(q0, dtype=float),
        jac=True,
        method="L-BFGS-B",
        options={"maxiter": maxiter, "maxfun": 2 * maxiter, "gtol": 1.0e-11, "ftol": 1.0e-16, "maxcor": 30},
    )
    return result.x, result


def numerical_stabilizer(q: np.ndarray, r0: float) -> dict[str, Any]:
    """Float stabilizer of the (Phi, Sigma) part of an endpoint (with a reported singular-value gap)."""
    state = chart.unpack(q)
    heavy = potential.FieldState(
        phi=state.phi, h=np.zeros(10, dtype=complex), sigma=state.sigma, s=state.s, x=state.x
    ).validated()
    orbit = chart.gauge_orbit_matrix(heavy)
    rows = np.concatenate([np.arange(chart.PHI_DIM), np.arange(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop)])
    _, singular, vt = np.linalg.svd(orbit[rows], full_matrices=True)
    # At the exact vacuum the smallest broken-generator tangent is sqrt(2) r0; float minimisation
    # endpoints sit up to ~1e-4 off the orbit along the soft (r0^2/96) modes.  Generators whose
    # tangent is below 0.1 r0 are counted as unbroken.
    threshold = 0.1 * float(r0)
    rank = int(np.sum(singular > threshold))
    kernel = vt[rank:].T
    output: dict[str, Any] = {
        "stabilizer_dimension": int(kernel.shape[1]),
        "threshold_0.1_r0": threshold,
        "largest_kernel_singular_value": float(singular[rank]) if rank < singular.size else 0.0,
        "smallest_orbit_singular_value": float(singular[rank - 1]),
    }
    if kernel.shape[1] == 0:
        output["hypercharge_type_centre"] = False
        return output
    matrices = [
        sum(kernel[i, j] * hypercharge._elementary_matrices()[i] for i in range(45)) for j in range(kernel.shape[1])
    ]
    k = len(matrices)
    blocks = []
    for j in range(k):
        blocks.append(np.column_stack([(matrices[i] @ matrices[j] - matrices[j] @ matrices[i]).ravel() for i in range(k)]))
    _, sv, vt2 = np.linalg.svd(np.vstack(blocks))
    centre_rank = int(np.sum(sv > 1.0e-2 * max(sv[0], 1.0e-300)))
    centre = vt2[centre_rank:].T
    output["centre_dimension"] = int(centre.shape[1])
    if centre.shape[1] == 1:
        generator = sum(centre[i, 0] * matrices[i] for i in range(k))
        charges = np.sort(np.abs(np.linalg.eigvals(generator).imag))
        charges = charges / (2.0 * charges.max())
        output["centre_abs_charges_on_10_normalized"] = [round(float(c), 3) for c in charges]
        output["hypercharge_type_centre"] = bool(
            np.allclose(charges, [1 / 3] * 6 + [1 / 2] * 4, atol=1.0e-2)
        )
    else:
        output["hypercharge_type_centre"] = False
    return output


def soft_displacement(gap: float, r0: float) -> float:
    """eps(g) = sqrt(96 max(g, floor))/r0^2: relative off-orbit Sigma displacement a gap g allows along r0^2/96 modes."""
    return math.sqrt(max(float(gap), ENDPOINT_GAP_FLOOR) / float(LIGHTEST_MASSIVE_OVER_R0_SQUARED)) / r0**2


def endpoint_orbit_test(
    gap: float, invariants: Mapping[str, float], stabilizer: Mapping[str, Any], r0: float, x0: float
) -> dict[str, Any]:
    """Convergence-aware classification of a float minimisation endpoint (see NUM_FULL_GAP_REACHED).

    on_orbit: converged (reached) and every normalised residual within the soft-mode tolerance, with a 12-dim
    stabilizer of hypercharge type; inconclusive: not converged enough to classify; off_orbit: converged but
    outside the tolerance, which would contradict the exact equality-set classification.
    """
    eps = soft_displacement(gap, r0)
    # gap <= NUM_FULL_GAP_REACHED and eps(gap) <= ENDPOINT_MAX_SOFT_DISPLACEMENT.
    reached_threshold = min(
        NUM_FULL_GAP_REACHED, (ENDPOINT_MAX_SOFT_DISPLACEMENT * r0**2) ** 2 * float(LIGHTEST_MASSIVE_OVER_R0_SQUARED)
    )
    reached = bool(gap <= reached_threshold)
    tolerance = NUM_FULL_ORBIT_RESIDUAL + ENDPOINT_TOLERANCE_PER_SOFT_DISPLACEMENT * eps
    residuals = {
        "Phi_norm_squared_minus_1": abs(invariants["Phi_norm_squared"] - 1.0),
        "V_Phi_plus_1": abs(invariants["V_Phi_plus_1"]),
        "N_Sigma_minus_r0_squared_over_r0_squared": abs(invariants["N_Sigma"] - r0**2) / r0**2,
        "sqrt_Sigma_purity_defect": math.sqrt(max(invariants["Sigma_purity_defect"], 0.0)),
        "A_shift_norm_over_r0": invariants["A_shift_norm"] / r0,
        "C_norm_over_r0": invariants["C_norm"] / r0,
        "abs_S_minus_r0_over_r0": abs(invariants["S_abs"] - r0) / r0,
        "abs_Phi17_minus_x0_over_x0": abs(invariants["Phi17_abs"] - x0) / x0,
        "N_H_over_r0_squared": invariants["N_H"] / r0**2,
        "kernel_singular_value_over_r0": stabilizer["largest_kernel_singular_value"] / r0,
    }
    within = all(value <= tolerance for value in residuals.values())
    sm_stabilizer = bool(
        stabilizer["stabilizer_dimension"] == EXPECTED_STABILIZER_DIMENSION and stabilizer["hypercharge_type_centre"]
    )
    if not reached:
        classification = "inconclusive"
    elif within and sm_stabilizer:
        classification = "on_orbit"
    else:
        classification = "off_orbit"
    return {
        "gap": gap,
        "reached_threshold": reached_threshold,
        "reached": reached,
        "soft_relative_displacement": eps,
        "tolerance": tolerance,
        "normalized_residuals": residuals,
        "max_residual_over_tolerance": max(residuals.values()) / tolerance,
        "residuals_within_tolerance": within,
        "stabilizer_sm_type": sm_stabilizer,
        "classification": classification,
    }


def classify_endpoint(fast: SosFormPotential, q: np.ndarray, r0: float, x0: float, *, gap: float) -> dict[str, Any]:
    invariants = fast.invariants(q)
    stabilizer = numerical_stabilizer(q, r0)
    test = endpoint_orbit_test(gap, invariants, stabilizer, r0, x0)
    classification = test.pop("classification")
    return {
        "invariants": invariants,
        "heavy_pair_stabilizer": stabilizer,
        "orbit_test": test,
        "orbit_classification": classification,
    }


def classification_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Counts per class; the flag excludes inconclusive endpoints but needs at least one converged endpoint."""
    counts = {name: sum(1 for row in rows if row["orbit_classification"] == name) for name in ORBIT_CLASSES}
    return {
        "endpoint_classification_counts": counts,
        "all_converged_endpoints_on_sm_vacuum_orbit": bool(counts["off_orbit"] == 0 and counts["on_orbit"] > 0),
    }


def _ray_optimum(fast: SosFormPotential, phi_unit: np.ndarray, sigma_unit: np.ndarray | None, r0: float, x0: float) -> tuple[np.ndarray, dict[str, float]]:
    base = np.zeros(chart.TOTAL_DIM)
    base[chart.S_SLICE] = [SQRT2 * r0, 0.0]
    base[chart.X_SLICE] = [SQRT2 * x0, 0.0]
    sigma_chart = np.zeros(chart.SIGMA_REAL_DIM) if sigma_unit is None else chart._pack_complex_interleaved(sigma_unit)

    def build(params: np.ndarray) -> np.ndarray:
        q = base.copy()
        q[chart.PHI_SLICE] = params[0] * phi_unit
        q[chart.SIGMA_SLICE] = params[1] * sigma_chart
        return q

    def objective(params: np.ndarray) -> tuple[float, np.ndarray]:
        value, gradient = fast.value_grad(build(params))
        return value, np.array([gradient[chart.PHI_SLICE] @ phi_unit, gradient[chart.SIGMA_SLICE] @ sigma_chart])

    starts = [np.array([1.0, r0]), np.array([-1.0, r0]), np.array([0.8, 2.0 * r0]), np.array([1.2, 0.5 * r0])]
    best = None
    for start in starts:
        if sigma_unit is None:
            start = start.copy()
            start[1] = 0.0
        result = minimize(
            objective,
            start,
            jac=True,
            method="L-BFGS-B",
            bounds=[(-5.0, 5.0), (0.0, 0.0) if sigma_unit is None else (0.0, 5.0)],
            options={"gtol": 1.0e-13, "ftol": 1.0e-16, "maxiter": 2000},
        )
        if best is None or result.fun < best.fun:
            best = result
    return build(best.x), {"Phi_scale": float(best.x[0]), "Sigma_norm": float(best.x[1])}


def _unit_sigma(form: Mapping[tuple[int, ...], complex]) -> np.ndarray:
    coordinates = chart.sigma_coordinates(dict(form))
    return coordinates / np.linalg.norm(coordinates)


def structured_competitors(fast: SosFormPotential, coefficients: Mapping[str, float], r0: Fraction, x0: Fraction, rng: np.random.Generator) -> dict[str, Any]:
    r, x = float(r0), float(x0)
    v0 = float(lower_bound_v0(r0, x0))
    singlets = direct.singlet_basis()

    def phi_unit(form: Mapping[tuple[int, ...], complex]) -> np.ndarray:
        values = np.asarray([complex(form.get(indices, 0.0)).real for indices in chart.PHI_INDICES])
        return values / np.linalg.norm(values)

    sigmas = {
        "sigma_std": sigma_std_unit_coordinates(),
        "flipped": _unit_sigma(hypercharge._float_form(hypercharge._sigma_form("flipped_P_minus_i"))),
        "delta_R": _unit_sigma(direct.delta_r()),
    }
    z_real, z_imaginary = counterexample_source._witness_arrays()
    witness = np.asarray(z_real, dtype=float) + 1j * np.asarray(z_imaginary, dtype=float)
    sigmas["historical_global_witness"] = witness / np.linalg.norm(witness)
    phis = {
        "p": phi_unit(singlets["p"]),
        "F": phi_unit(ext.normalized_f()),
        "a": phi_unit(singlets["a"]),
        "omega": phi_unit(singlets["omega"]),
    }
    exact_gaps = {
        "p|Sigma=0": SIGMA_SCALE * r0**4,
        "p|delta_R": SIGMA_SCALE * r0**4 / 49,
        "p|flipped": Fraction(0),
        "p|sigma_std": Fraction(0),
    }
    specs = [
        ("p|Sigma=0", "p", None),
        ("p|delta_R", "p", "delta_R"),
        ("p|flipped", "p", "flipped"),
        ("p|historical_global_witness", "p", "historical_global_witness"),
        ("F|sigma_std", "F", "sigma_std"),
        ("F|flipped", "F", "flipped"),
        ("F|delta_R", "F", "delta_R"),
        ("F|Sigma=0", "F", None),
        ("a|sigma_std", "a", "sigma_std"),
        ("omega|sigma_std", "omega", "sigma_std"),
    ]
    rows: dict[str, Any] = {}
    for name, phi_name, sigma_name in specs:
        q, params = _ray_optimum(fast, phis[phi_name], None if sigma_name is None else sigmas[sigma_name], r, x)
        fast_value = fast.value(q)
        compiler = compiler_value(q, coefficients)
        perturbed = q + 1.0e-3 * rng.normal(size=chart.TOTAL_DIM)
        end, result = local_minimize(fast, perturbed)
        end_value, end_gradient = fast.value_grad(end)
        row = {
            "restricted_optimum": params,
            "fast_gap": fast_value - v0,
            "compiler_gap": compiler - v0,
            "fast_minus_compiler": fast_value - compiler,
            "exact_gap": exact_gaps.get(name),
            "local_minimization_from_perturbed_optimum": {
                "final_gap": end_value - v0,
                "final_gradient_max_abs": float(np.max(np.abs(end_gradient))),
                "iterations": int(result.nit),
                **classify_endpoint(fast, end, r, x, gap=end_value - v0),
            },
        }
        if name in exact_gaps:
            row["exact_gap_float"] = float(exact_gaps[name])
            row["compiler_minus_exact_gap"] = compiler - v0 - float(exact_gaps[name])
        rows[name] = row
    return rows


def quartic_scan(fast4: SosFormPotential, coefficients: Mapping[str, float], rng: np.random.Generator, *, n_random: int, n_minimize: int, n_compiler: int) -> dict[str, Any]:
    values = []
    for _ in range(n_random):
        q = rng.normal(size=chart.TOTAL_DIM)
        q /= np.linalg.norm(q)
        values.append(fast4.value(q))

    def normalized(q: np.ndarray) -> tuple[float, np.ndarray]:
        value, gradient = fast4.value_grad(q)
        n2 = float(q @ q)
        return value / n2**2, gradient / n2**2 - 4.0 * value * q / n2**3

    minima = []
    for _ in range(n_minimize):
        q0 = rng.normal(size=chart.TOTAL_DIM)
        result = minimize(normalized, q0 / np.linalg.norm(q0), jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1.0e-12, "ftol": 1.0e-16})
        minima.append(float(result.fun))
    compiler_rows = []
    for _ in range(n_compiler):
        q = rng.normal(size=chart.TOTAL_DIM)
        q /= np.linalg.norm(q)
        ts = np.array([1.0, 2.0, 3.0, 4.0])
        vs = np.array([compiler_value(t * q, coefficients) for t in ts])
        design = np.column_stack([ts**2, ts**3, ts**4])
        solution, *_ = np.linalg.lstsq(design[:3], vs[:3], rcond=None)
        residual = float(vs[3] - design[3] @ solution)
        compiler_rows.append(
            {
                "compiler_quartic_coefficient": float(solution[2]),
                "fast_quartic_value": fast4.value(q),
                "fit_check_residual_at_t4": residual,
            }
        )
    bound = float(QUARTIC_LOWER_BOUND)
    return {
        "exact_lower_bound_on_unit_sphere": QUARTIC_LOWER_BOUND,
        "random_unit_directions": n_random,
        "random_min_V4": float(min(values)),
        "random_max_V4": float(max(values)),
        "sphere_minimizations": n_minimize,
        "sphere_minima_V4": minima,
        "lowest_V4_found": float(min(minima + values)),
        "lowest_at_or_above_exact_bound": bool(min(minima + values) >= bound * (1.0 - 1.0e-9)),
        "compiler_directions": compiler_rows,
    }


def validate_fast_evaluator(fast: SosFormPotential, coefficients: Mapping[str, float], rng: np.random.Generator, *, n_random: int, gradient_check: bool, r0: Fraction = R0, x0: Fraction = X0) -> dict[str, Any]:
    vacuum = chart.pack(candidate_state(r0, x0))
    v0 = float(lower_bound_v0(r0, x0))
    fast_vacuum, fast_gradient = fast.value_grad(vacuum)
    compiler_vacuum = compiler_value(vacuum, coefficients)
    random_rows = []
    for _ in range(n_random):
        q = rng.normal(size=chart.TOTAL_DIM) * 0.3
        fast_value = fast.value(q)
        compiler = compiler_value(q, coefficients)
        direction = rng.normal(size=chart.TOTAL_DIM)
        direction /= np.linalg.norm(direction)
        step = 1.0e-5
        analytic = float(fast.value_grad(q)[1] @ direction)
        finite = (fast.value(q + step * direction) - fast.value(q - step * direction)) / (2.0 * step)
        random_rows.append(
            {
                "fast_value": fast_value,
                "compiler_value": compiler,
                "relative_difference": abs(fast_value - compiler) / max(abs(compiler), 1.0),
                "directional_derivative_analytic_minus_central_difference": analytic - finite,
            }
        )
    output = {
        "evaluator": "SosFormPotential: adapted SOS form with integer M, C tensors, sparse Casimirs, analytic gradient",
        "vacuum_fast_minus_V0": fast_vacuum - v0,
        "vacuum_compiler_minus_V0": compiler_vacuum - v0,
        "vacuum_fast_gradient_max_abs": float(np.max(np.abs(fast_gradient))),
        "random_states": random_rows,
        "max_relative_value_difference": max(row["relative_difference"] for row in random_rows) if random_rows else 0.0,
    }
    if gradient_check:
        q = rng.normal(size=chart.TOTAL_DIM) * 0.3
        state = chart.unpack(q)
        needed = needed_direction_ids(coefficients)
        rows = target.parameter_rows(state, include=lambda direction: direction.direction_id in needed)
        value, gradient, _ = target.assemble(rows, coefficients)
        fast_value, fast_gradient = fast.value_grad(q)
        output["compiler_gradient_check"] = {
            "value_relative_difference": abs(fast_value - value) / max(abs(value), 1.0),
            "gradient_max_abs_difference": float(np.max(np.abs(fast_gradient - gradient))),
            "gradient_max_abs": float(np.max(np.abs(gradient))),
        }
    return output


@lru_cache(maxsize=1)
def _p_operators() -> tuple[np.ndarray, np.ndarray]:
    _, p_float = phi_source.pati_salam_direction()
    p_vector = np.rint(p_float).astype(np.int64)
    m_real, m_imaginary = a_square_source.integer_cubic_operators()
    c_real, c_imaginary = a_square_source.integer_contraction_tensor()
    m_p = np.tensordot(p_vector, m_real.astype(float) + 1j * m_imaginary.astype(float), axes=(0, 0))
    c_p = np.tensordot(c_real.astype(float) + 1j * c_imaginary.astype(float), p_vector.astype(float), axes=(1, 0))
    return m_p, c_p


def equality_set_evidence(rng: np.random.Generator, *, n_pure: int = 4, n_phi: int = 6) -> dict[str, Any]:
    """Numerical evidence on {V = V0}: the Sigma subspace allowed at Phi = p, pure spinors in it, V_Phi minima."""
    m_p, c_p = _p_operators()
    stacked = np.vstack([m_p - 2.0 * np.eye(chart.SIGMA_COMPLEX_DIM), c_p])
    _, singular, vt = np.linalg.svd(stacked)
    null_mask = np.concatenate([singular, np.zeros(chart.SIGMA_COMPLEX_DIM - singular.size)]) < 1.0e-9 * singular[0]
    basis = vt.conj().T[:, null_mask]
    spectrum = np.linalg.eigvalsh(0.5 * (m_p + m_p.conj().T))
    eigen_groups = [
        {"eigenvalue": row["mass_squared"], "complex_multiplicity": row["complex_multiplicity"]}
        for row in target._grouped(spectrum)
    ]
    unit = sigma_std_unit_coordinates()
    tensors = _fast_tensors()
    fast = SosFormPotential(0.0, 0.0, 0.0, 0.0)

    def impurity(real_c: np.ndarray) -> tuple[float, np.ndarray]:
        c = real_c[0::2] + 1j * real_c[1::2]
        z = basis @ c
        norm = float(np.vdot(z, z).real)
        zz = np.outer(z, z)
        powers = [zz]
        for _ in range(3):
            powers.append(fast._k126(powers[-1]))
        value = 0.0
        g_z = np.zeros_like(z)
        for channel in ("54", "1050bar", "4125"):
            projected = sum(coef * powers[i] for i, coef in enumerate(tensors["polys"][channel]))
            value += float(np.vdot(projected, projected).real)
            g_z += 2.0 * (projected @ np.conj(z))
        ratio = value / norm**2
        g_z = g_z / norm**2 - 2.0 * ratio * z / norm
        g_c = basis.conj().T @ g_z
        gradient = np.empty_like(real_c)
        gradient[0::2] = 2.0 * g_c.real
        gradient[1::2] = 2.0 * g_c.imag
        return ratio, gradient

    pure_rows = []
    p_vector = chart.pack(candidate_state(R0, X0))[chart.PHI_SLICE]
    for _ in range(n_pure):
        start = rng.normal(size=2 * basis.shape[1])
        result = minimize(impurity, start, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1.0e-13, "ftol": 1.0e-16})
        c = result.x[0::2] + 1j * result.x[1::2]
        z = basis @ c
        z *= float(R0) / np.linalg.norm(z)
        q = np.zeros(chart.TOTAL_DIM)
        q[chart.PHI_SLICE] = p_vector
        q[chart.SIGMA_SLICE] = chart._pack_complex_interleaved(z)
        q[chart.S_SLICE] = [SQRT2 * float(R0), 0.0]
        q[chart.X_SLICE] = [SQRT2 * float(X0), 0.0]
        pure_rows.append(
            {
                "start_impurity": impurity(start)[0],
                "final_impurity": float(result.fun),
                "gap_at_r0_one_fifth": fast_potential().value(q) - float(lower_bound_v0()),
                "heavy_pair_stabilizer": numerical_stabilizer(q, float(R0)),
            }
        )

    phi_rows = []
    K = tensors["K210"]
    j = {name: float(value) for name, value in phi_source.EXPECTED_J_COUPLINGS.items()}

    def v_phi(phi: np.ndarray) -> tuple[float, np.ndarray]:
        pair = np.outer(phi, phi).reshape(-1)
        powers = {0: pair}
        current = pair
        for degree in range(1, 5):
            current = K @ current
            powers[degree] = current
        value = -2.0 * float(phi @ phi)
        gradient = -4.0 * phi
        for name, degree in (("J0", 0), ("J2", 2), ("J3", 3), ("J4", 4)):
            value += j[name] * float(pair @ powers[degree])
            gradient += j[name] * 4.0 * (powers[degree].reshape(chart.PHI_DIM, chart.PHI_DIM) @ phi)
        return value, gradient

    generators = _phi_generators()
    for _ in range(n_phi):
        start = rng.normal(size=chart.PHI_DIM)
        start /= np.linalg.norm(start)
        result = minimize(v_phi, start, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1.0e-12, "ftol": 1.0e-16})
        tangents = np.column_stack([np.asarray(g @ result.x).ravel() for g in generators])
        values = np.linalg.svd(tangents, compute_uv=False)
        stabilizer = int(np.sum(values <= 1.0e-5 * values[0]))
        phi_rows.append(
            {
                "final_V_Phi_plus_1": float(result.fun) + 1.0,
                "Phi_norm": float(np.linalg.norm(result.x)),
                "stabilizer_dimension": stabilizer,
            }
        )
    return {
        "sigma_subspace_at_p": {
            "definition": "ker(M_p - 2) intersect ker(C_p) in the 126bar (float SVD of exact integer matrices)",
            "complex_dimension": int(basis.shape[1]),
            "largest_null_singular_value": float(singular[null_mask[: singular.size]].max()) if np.any(null_mask[: singular.size]) else 0.0,
            "smallest_nonnull_singular_value": float(singular[~null_mask[: singular.size]].min()),
            "M_p_eigenvalues": eigen_groups,
            "sigma_std_residual_outside_subspace": float(np.linalg.norm(unit - basis @ (basis.conj().T @ unit))),
            "delta_r_residual_outside_subspace": float(
                np.linalg.norm(_unit_sigma(direct.delta_r()) - basis @ (basis.conj().T @ _unit_sigma(direct.delta_r())))
            ),
        },
        "pure_spinor_minimizations_in_subspace": pure_rows,
        "all_pure_minima_sm_type": all(
            row["final_impurity"] < 1.0e-10
            and row["heavy_pair_stabilizer"]["stabilizer_dimension"] == EXPECTED_STABILIZER_DIMENSION
            and row["heavy_pair_stabilizer"]["hypercharge_type_centre"]
            for row in pure_rows
        ),
        "V_Phi_minimizations": phi_rows,
        "all_V_Phi_minima_at_minus_1_with_pati_salam_stabilizer": all(
            abs(row["final_V_Phi_plus_1"]) < 1.0e-10 and row["stabilizer_dimension"] == 21 for row in phi_rows
        ),
        "interpretation": (
            "At Phi = p the equality conditions (M_p - 2)Sigma = 0, C_p Sigma = 0 cut the 126bar down to this "
            "subspace; the (10,3,1) also contains pure spinors but has M_p = -2 (L<->R parity plus conjugation). "
            "Evidence only: the V_Phi equality set and the pure spinors of the subspace are sampled, not classified."
        ),
    }


def numerical_global_search(*, seed: int = 20260924) -> dict[str, Any]:
    started = time.time()
    rng = np.random.default_rng(seed)
    output: dict[str, Any] = {"seed": seed, "note": "numerical evidence; the exact proof is exact_certificate"}
    runs: dict[str, Any] = {}
    for r0, kinds in (
        (R0, ("generic", "generic", "generic", "phi_near_p", "phi_near_p", "phi_near_p", "large_field", "large_field", "sigma_dominated", "sigma_dominated")),
        (Fraction(1, 20), ("generic", "phi_near_p", "sigma_dominated")),
    ):
        fast = fast_potential(r0, X0)
        coefficients = float_coefficients(candidate_coefficients(r0, X0))
        v0 = float(lower_bound_v0(r0, X0))
        label = f"r0={r0}"
        if r0 == R0:
            output["fast_evaluator_validation"] = validate_fast_evaluator(fast, coefficients, rng, n_random=3, gradient_check=True)
        rows = []
        for index, kind in enumerate(kinds):
            q0 = random_start(kind, rng, float(r0), float(X0))
            start_value = fast.value(q0)
            end, result = local_minimize(fast, q0)
            end_value, end_gradient = fast.value_grad(end)
            rows.append(
                {
                    "start": index,
                    "kind": kind,
                    "start_gap": start_value - v0,
                    "final_gap": end_value - v0,
                    "final_compiler_gap": compiler_value(end, coefficients) - v0,
                    "final_gradient_max_abs": float(np.max(np.abs(end_gradient))),
                    "iterations": int(result.nit),
                    **classify_endpoint(fast, end, float(r0), float(X0), gap=end_value - v0),
                }
            )
        runs[label] = {
            "V0": lower_bound_v0(r0, X0),
            "starts": rows,
            "lowest_final_gap": min(row["final_gap"] for row in rows),
            "lowest_final_compiler_gap": min(row["final_compiler_gap"] for row in rows),
            **classification_summary(rows),
            "no_endpoint_below_V0": all(
                row["final_gap"] > -BELOW_V0_TOLERANCE and row["final_compiler_gap"] > -BELOW_V0_TOLERANCE for row in rows
            ),
        }
    output["random_start_local_minimization"] = runs
    fast = fast_potential(R0, X0)
    coefficients = float_coefficients(candidate_coefficients(R0, X0))
    output["structured_competitors_r0_1_5"] = structured_competitors(fast, coefficients, R0, X0, rng)
    competitor_endpoints = [
        row["local_minimization_from_perturbed_optimum"] for row in output["structured_competitors_r0_1_5"].values()
    ]
    endpoints = [row for run in runs.values() for row in run["starts"]] + competitor_endpoints
    output["endpoint_classification"] = {
        "method": (
            f"a float endpoint at gap g = V - V0 is classified only if g <= min(NUM_FULL_GAP_REACHED, "
            f"({ENDPOINT_MAX_SOFT_DISPLACEMENT:g} r0^2)^2/96) (converged: relative soft-mode displacement eps(g) = "
            f"sqrt(96 g)/r0^2 <= {ENDPOINT_MAX_SOFT_DISPLACEMENT:g}); it is on_orbit if every normalised orbit "
            f"residual is <= NUM_FULL_ORBIT_RESIDUAL + {ENDPOINT_TOLERANCE_PER_SOFT_DISPLACEMENT:g} eps(g) and the "
            "(Phi, Sigma) stabilizer is 12-dimensional of hypercharge type, off_orbit otherwise (a contradiction); "
            "less converged endpoints are inconclusive"
        ),
        "NUM_FULL_GAP_REACHED": NUM_FULL_GAP_REACHED,
        "NUM_FULL_ORBIT_RESIDUAL": NUM_FULL_ORBIT_RESIDUAL,
        "tolerance_per_soft_displacement": ENDPOINT_TOLERANCE_PER_SOFT_DISPLACEMENT,
        "max_soft_displacement": ENDPOINT_MAX_SOFT_DISPLACEMENT,
        "scope": "random-start endpoints (r0 = 1/5, 1/20) and structured-competitor local minimisations (r0 = 1/5)",
        **classification_summary(endpoints),
        "no_endpoint_below_V0": all(run["no_endpoint_below_V0"] for run in runs.values())
        and all(row["final_gap"] > -BELOW_V0_TOLERANCE for row in competitor_endpoints),
    }
    output["equality_set_evidence"] = equality_set_evidence(rng)
    output["quartic_directions"] = quartic_scan(
        fast_potential(R0, X0, quartic_only=True), coefficients, rng, n_random=512, n_minimize=6, n_compiler=3
    )
    slice_points = [(1.0, 0.2, 0.2, 1.0), (0.9, 0.25, 0.3, 1.2), (1.1, 0.1, 0.25, 0.8)]
    output["exact_slice_vs_compiler"] = [
        {
            "point_c_r_s_x": point,
            "exact": slice_value(*point),
            "compiler_minus_exact": compiler_value(chart.pack(slice_state(*point)), coefficients) - float(slice_value(*point)),
        }
        for point in slice_points
    ]
    gaps = [row["fast_gap"] for row in output["structured_competitors_r0_1_5"].values()]
    gaps += [row["compiler_gap"] for row in output["structured_competitors_r0_1_5"].values()]
    gaps += [
        row["local_minimization_from_perturbed_optimum"]["final_gap"]
        for row in output["structured_competitors_r0_1_5"].values()
    ]
    for run in runs.values():
        gaps += [row["final_gap"] for row in run["starts"]] + [row["final_compiler_gap"] for row in run["starts"]]
    output["lowest_gap_found_any_method"] = float(min(gaps))
    output["nothing_found_below_V0"] = bool(min(gaps) > -BELOW_V0_TOLERANCE)
    output["seconds"] = time.time() - started
    return output


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def report_flags(
    ok: bool,
    *,
    embedding: Mapping[str, Any],
    certificate: Mapping[str, Any],
    checks: Mapping[str, bool],
    points: Sequence[Mapping[str, Any]],
    splitting: Mapping[str, Any],
    coloured_light: Sequence[str],
    rg: Mapping[str, Any],
    hierarchy: Mapping[str, Any],
    quartic: Mapping[str, Any],
    equality_set: Mapping[str, Any],
) -> dict[str, bool]:
    """Report flags; every positive claim is gated by ``ok`` (fail-closed).

    ``equality_set`` is the committed equality-set report (or its status/n_failed summary); {} means absent.
    """
    return {
        "candidate_is_sm_vacuum": bool(ok and embedding["candidate_is_sm_vacuum"]),
        "target_unbroken_algebra_is_standard_model": bool(ok and embedding["target_unbroken_algebra_is_standard_model"]),
        "exactly_stationary": bool(ok and certificate["exactly_stationary"]),
        "hessian_psd_exact": bool(ok and certificate["hessian_psd_exact"]),
        # Literal reading: kernel == symmetry tangents.  False for the reported (tuned) candidate.
        "hessian_psd_kernel_is_symmetry": bool(
            ok
            and all(
                row["projected_hessian"]["n_zero"] == 0 and row["projected_hessian"]["n_negative"] == 0
                for row in points
            )
        ),
        "hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet": bool(
            ok and checks["hessian_psd_with_kernel_symmetry_plus_light_doublet"]
        ),
        "hessian_kernel_is_symmetry_when_O06_raised": bool(
            ok
            and all(
                row["all_massive_variant"]["n_zero"] == 0 and row["all_massive_variant"]["n_negative"] == 0
                for row in points
            )
        ),
        "hessian_kernel_count_is_float64": True,
        "bfb_certified": bool(ok and certificate["bfb_certified"]),
        "global_minimum_certified": bool(ok and certificate["global_minimum_certified"]),
        "equality_set_unique_modulo_symmetry_certified": bool(ok and equality_set_certified(equality_set)),
        "doublet_triplet_splitting_natural": bool(ok and splitting["natural"]),
        "coloured_scalars_only_at_M_GUT": bool(ok and not coloured_light),
        "breaking_route_matches_rg_anchor": bool(
            ok and embedding["phi_p_alone"]["stabilizer_dimension"] == 21 and embedding["target_unbroken_algebra_is_standard_model"]
        ),
        "rg_anchor_field_content_reproduced": bool(ok and rg["field_content_reproduced"]),
        "physical_benchmark_uses_canonical_phi17_scale": bool(ok and hierarchy["benchmark_uses_canonical_phi17_scale"]),
        "higgs_mass_compatible": bool(ok and quartic["higgs_mass_compatible"]),
        "electroweak_symmetry_breaking_realized": False,
        "realistic_yukawa_sector": False,
        "g3_closed": False,
        "whole_model_validated": False,
        "whole_model_excluded": False,
    }


def build_report(
    *,
    heavy: bool = True,
    search: Mapping[str, Any] | None = None,
    equality_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if equality_report is None:
        equality_report = load_equality_set_report()
    equality_proved = equality_set_certified(equality_report)
    candidate = candidate_section()
    embedding = sm_embedding_section()
    certificate = exact_certificate_section(equality_report)
    exact_slice = exact_slice_section()
    compiler = compiler_section(heavy=heavy)
    physical_states = (
        json_roundtrip(compiler["M_I/M_GUT"]["light_spectrum"]["states"]) if "M_I/M_GUT" in compiler else None
    )
    hierarchy = hierarchy_section(physical_states)
    rg = rg_anchor_section(physical_states)
    quartic = light_doublet_quartic_section()
    numerical = (numerical_global_search() if heavy else None) if search is None else dict(search)
    default = compiler["1/5"]
    spectrum = default["labelled_spectrum"]
    h10 = default["h10"]
    points = list(compiler.values())
    splitting = h10["doublet_triplet_splitting"]

    def light_content(row: Mapping[str, Any]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for state in row["light_spectrum"]["states"]:
            for label, count in state["sm_content_real"].items():
                counts[label] = counts.get(label, 0) + int(count)
        return dict(sorted(counts.items()))

    def light_ratios(row: Mapping[str, Any]) -> dict[str, list[float]]:
        ratios: dict[str, list[float]] = {}
        for state in row["light_spectrum"]["states"]:
            for label in state["sm_content_real"]:
                ratios.setdefault(label, []).append(float(state["mass_squared_over_r0_squared"]))
        return {label: sorted(values) for label, values in ratios.items()}

    reference_ratios = light_ratios(default)
    coloured_light = [
        label
        for row in points
        for state in row["light_spectrum"]["states"]
        for label in state["sm_content_real"]
        if _parse_sm_label(label)[0] != "1"
    ]

    checks = {
        "coefficient_map_has_27_nonzero_entries_in_contract": candidate["nonzero_count"] == EXPECTED_NONZERO
        and candidate["all_parameters_in_exact_X_contract"],
        "coefficient_map_derived_from_historical_map": candidate["historical_parse_matches_exact_sos_laurent_map"]
        and candidate["historical_parse_matches_float_evaluation"]
        and len(candidate["changes_from_historical_h0"]) == 5,
        "H_linear_portals_are_zero": candidate["H_linear_portals_zero"],
        "exact_state_binding": bool(embedding["binding"]["bound"]),
        "unbroken_algebra_is_exactly_standard_model": embedding["target_unbroken_algebra_is_standard_model"],
        "phi_p_alone_leaves_pati_salam": embedding["phi_p_alone"]["stabilizer_dimension"] == 21,
        "U1X_broken_in_full_state": embedding["full_state_stabilizer_so10_plus_u1x"]["u1x_broken"],
        "old_delta_r_orientation_is_not_sm": not embedding["old_orientation_p_delta_r"]["is_sm_type"],
        "exact_SOS_lower_bound_attained": certificate["global_minimum_certified"],
        "exact_slice_gradient_vanishes": exact_slice["gradient_vanishes_exactly"] and exact_slice["equals_V0"],
        "compiler_gradient_vanishes_at_every_benchmark": all(
            row["gradient_max_abs"] < STATIONARITY_ATOL for row in points
        ),
        "compiler_value_equals_V0_at_every_benchmark": all(abs(row["V_minus_V0"]) < 1.0e-12 for row in points),
        "symmetry_rank_35_at_every_benchmark": all(
            row["symmetry_ranks"]
            == {"so10_orbit_rank": 33, "so10_plus_u1x_rank": 34, "so10_plus_u1x_plus_pq_rank": 35}
            for row in points
        ),
        "hessian_annihilates_symmetry_tangents": all(row["hessian_symmetry_residual"] < 1.0e-10 for row in points),
        "hessian_psd_with_kernel_symmetry_plus_light_doublet": all(
            row["kernel_is_symmetry_plus_light_doublet"] for row in points
        ),
        "lightest_massive_mode_is_r0_squared_over_96": all(
            row["projected_hessian"]["min_massive_absolute_deviation"] < 1.0e-12 for row in points
        ),
        "sm_generators_annihilate_the_vacuum": default["sm_generators_annihilate_vacuum"] < 1.0e-12,
        "goldstone_content_is_so10_over_sm_plus_two_phases": spectrum["symmetry_tangents"]["sm_content_real"]
        == {
            "(1,1)_|Y|=0": 3,
            "(1,1)_|Y|=1": 2,
            "(3,1)_|Y|=2/3": 6,
            "(3,2)_|Y|=1/6": 12,
            "(3,2)_|Y|=5/6": 12,
        },
        "h10_spectrum_matches_exact_expectation": h10["max_deviation_from_exact_expectation"] < 1.0e-12
        and h10["H_block_decoupled_from_other_fields"] < 1.0e-12,
        "tuned_wedge_combination_gives_triplets_M_GUT_and_doublets_no_phi_mass": h10["wedge_combination_(3/5)O46_1-O46_54"][
            "hermitian_matrix_minus_diag_1x6_0x4"
        ]
        < 1.0e-12
        and splitting["per_unit_max_deviation_from_exact"] < 1.0e-12
        and splitting["doublet_phi_induced_mass_squared"]["value_at_candidate"] == 0
        and splitting["triplet_phi_induced_mass_squared"]["value_at_candidate"] == 1,
        "light_doublet_is_equal_5_5bar_mixture": abs(
            splitting["doublet_composition"]["light_doublet_weight_in_span_z4_z5"] - 0.5
        )
        < 1.0e-12,
        "light_spectrum_has_60_real_states_with_same_sm_content_at_every_benchmark": all(
            row["light_spectrum"]["real_dimension"] == EXPECTED_LIGHT_REAL_DIMENSION
            and light_content(row) == light_content(default)
            for row in points
        ),
        "light_spectrum_mass_ratios_stable_across_benchmarks": all(
            len(light_ratios(row)[label]) == len(values)
            and all(
                abs(a - b) <= 1.0e-2 * max(abs(b), 1.0e-3)
                for a, b in zip(light_ratios(row)[label], values, strict=True)
            )
            for row in points
            for label, values in reference_ratios.items()
        ),
        "Phi17_block_decoupled_with_radial_x0_squared_over_8": all(
            row["Phi17_block"]["coupling_to_other_fields_max_abs"] < 1.0e-12
            and row["Phi17_block"]["radial_deviation_from_exact"] < 1.0e-12
            for row in points
        ),
        "light_doublet_quartic_compiler_matches_exact_127_64": all(
            abs(direction["lambda_eff"] - float(quartic["lambda_eff"])) < 1.0e-9
            and abs(direction["lambda_direct"] - 2.0) < 1.0e-9
            and direction["coupling_outside_Re_S_max_abs"] < 1.0e-12
            for direction in default["light_doublet_quartic"]["directions"].values()
        ),
        "rg_anchor_betas_reproduced_from_field_content": rg["anchor_betas_reproduced_from_field_content"],
        "rg_anchor_reproduced_by_local_one_loop_chain": rg["anchor_reproduced_by_local_chain"],
    }
    if numerical is not None:
        validation = numerical["fast_evaluator_validation"]
        checks.update(
            {
                "fast_sos_evaluator_matches_compiler": validation["max_relative_value_difference"] < 1.0e-11
                and validation["compiler_gradient_check"]["gradient_max_abs_difference"] < 1.0e-8,
                "numerical_search_finds_nothing_below_V0": numerical["nothing_found_below_V0"],
                "random_quartic_directions_respect_exact_bound": numerical["quartic_directions"][
                    "lowest_at_or_above_exact_bound"
                ],
                "exact_slice_matches_compiler": all(
                    abs(row["compiler_minus_exact"]) < 1.0e-12 for row in numerical["exact_slice_vs_compiler"]
                ),
            }
        )
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    m_h_conditional = quartic["conditional_sm_running"]["predictions"]["lambda_eff_127_over_64"]["m_h_tree_GeV"]
    lambda_zero = quartic["conditional_sm_running"]["predictions"]["lambda_zero"]
    lambda_required = quartic["conditional_sm_running"]["lambda_M_I_required_for_sm_two_loop"]
    flags = report_flags(
        ok,
        embedding=embedding,
        certificate=certificate,
        checks=checks,
        points=points,
        splitting=splitting,
        coloured_light=coloured_light,
        rg=rg,
        hierarchy=hierarchy,
        quartic=quartic,
        equality_set=equality_report,
    )
    equality_summary = certificate["equality_set"]["equality_set_certificate"]
    report = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": (
            "SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN"
            if ok
            else "G3_SM_PATI_SALAM_CANDIDATE_AUDIT_FAILED"
        ),
        "overall_state": "CANDIDATE_CERTIFIED_G3_OPEN" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "flag_notes": {
            "hessian_psd_kernel_is_symmetry": (
                "False by its literal meaning: at every benchmark the PSD Hessian's kernel is the 35 symmetry tangents "
                "(SO(10)/SM + U(1)_X + PQ) PLUS the 4 real modes of the deliberately tuned light doublet (O06 = "
                "2|kappa| r0); see hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet. Raising O06 by r0^2/100 "
                "leaves exactly the 35 symmetry tangents (hessian_kernel_is_symmetry_when_O06_raised). Kernel counts "
                "are float64."
            ),
            "target_unbroken_algebra_is_standard_model": (
                "exact integer stabilizer of (p, sigma_std); gated by the audit passing (fail-closed), like every other "
                "positive flag"
            ),
            "global_minimum_certified": (
                "exact: adapted SOS27 lower bound attained at the vacuum (repository source-bound recouplings plus "
                "new exact sigma_std pieces); "
                + (
                    "uniqueness modulo SO(10) x U(1)_X x U(1)_PQ is certified separately (see "
                    "equality_set_unique_modulo_symmetry_certified)"
                    if equality_proved
                    else "uniqueness of the minimum modulo symmetry is not certified"
                )
            ),
            "equality_set_unique_modulo_symmetry_certified": (
                (
                    f"exact, bound to the committed {EQUALITY_SET_JSON.name} (status {equality_summary['status']}, "
                    f"n_failed {equality_summary['n_failed']}; {EQUALITY_SET_SOURCE} imports this module, so it is "
                    "read, not imported): {V = V0} = G.(p, r0 sigma_std, 0, r0, x0), G = SO(10) x U(1)_X x U(1)_PQ, "
                    "for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2. Uniqueness uses the accidental U(1)_PQ: modulo "
                    "SO(10) x U(1)_X alone the equality set is a circle of orbits (the axion direction). The classical "
                    "theorems it cites are not machine-checked there, nor are the elementary steps listed in its "
                    "scope.elementary_not_machine_checked"
                )
                if equality_proved
                else (
                    f"False: the committed {EQUALITY_SET_JSON.name} is missing or does not report "
                    f"{EQUALITY_SET_PROVED_STATUS} with n_failed = 0 (status {equality_summary['status']}, n_failed "
                    f"{equality_summary['n_failed']}); only numerical evidence (numerical_global_search)"
                )
            ),
            "exactly_stationary": "follows from global minimality; the exact slice gradient also vanishes identically",
            "doublet_triplet_splitting_natural": (
                "False: the 10_H splitting needs O46_1 = -(3/5) O46_54 (to ~ (m_h/M_GUT)^2) and O06 = 2|kappa| r0 (to "
                "~ (m_h/M_I)^2); no symmetry enforces either"
            ),
            "coloured_scalars_only_at_M_GUT": (
                "False: only the 10_H triplets are at M_GUT; 126bar (10bar,1,3) remnants (6,1)_4/3, (3,1)_1/3, "
                "(3,1)_4/3, (6,1)_1/3, (6,1)_2/3 lie below M_I"
            ),
            "breaking_route_matches_rg_anchor": "chain topology SO(10) -> PS -> SM only; not the anchor's field content",
            "rg_anchor_field_content_reproduced": (
                "False: anchor betas assume a light (15,2,2) above M_I and a 2HDM below; the candidate has neither and "
                "has sub-M_I coloured scalars (rg_anchor_consistency)"
            ),
            "physical_benchmark_uses_canonical_phi17_scale": "False: x0 = 1 at every benchmark (canonical x0 ~ 10.08)",
            "higgs_mass_compatible": (
                "False at the benchmark (a benchmark-only flag): tree-level lambda_eff = 127/64 at kappa = -r0/4 "
                f"(m_h ~ {m_h_conditional:.0f} GeV under conditional SM running). The certified family kappa^2 < 8 r0^2 "
                "spans lambda_eff in (0, 2], and lambda_eff -> 0+ gives m_h within a few GeV of the measured value "
                f"(lambda(M_I) = 0: m_h ~ {lambda_zero['m_h_tree_GeV']:.1f} GeV tree, "
                f"{lambda_zero['M_h_scaled_to_buttazzo_GeV']:.1f} GeV Buttazzo-scaled, vs {M_H_OBSERVED_GEV:.2f} GeV). "
                "The remaining tension is lambda_eff >= 0 (tree-level global minimality) versus the SM-required "
                f"lambda(M_I) = {lambda_required:.4f} at M_t = 173.34 GeV, whose sign is M_t-dependent at about 2 sigma"
            ),
        },
        "units": UNITS,
        "candidate": candidate,
        "sm_embedding": embedding,
        "exact_certificate": certificate,
        "exact_slice": exact_slice,
        "compiler": compiler,
        "hierarchy": hierarchy,
        "rg_anchor_consistency": rg,
        "light_doublet_quartic": quartic,
        "numerical_global_search": numerical,
        "scope": {
            "proved_exactly": [
                "unbroken algebra of (p, sigma_std) is the standard SM (integer arithmetic)",
                "V >= V0 on the full 486-real chart and V(vacuum) = V0 (adapted SOS27; repository source-bound identities plus new exact sigma_std pieces)",
                "hence exact stationarity and exact Hessian PSD for every r0 > 0 with kappa^2 < 8 r0^2 (lambda_eff > 0)",
                "strict positivity of the quartic part: V4(q) >= |q|^4/167",
                "tree-level light-doublet quartic lambda_eff = 2 - kappa^2/(4 r0^2) = 127/64 (from the exact identity; compiler cross-check at r0 = 1/5)",
            ]
            + (
                [
                    "equality set {V = V0} = G.(p, r0 sigma_std, 0, r0, x0), unique modulo G = SO(10) x U(1)_X x U(1)_PQ "
                    "(g3_sm_pati_salam_equality_set_v20, read from its committed artifact; U(1)_PQ is accidental, and "
                    "modulo SO(10) x U(1)_X alone the equality set is a circle of orbits)"
                ]
                if equality_proved
                else []
            ),
            "float64_only": [
                "Hessian kernel = 35 symmetry tangents + 4 light-doublet modes; lightest massive eigenvalue r0^2/96",
                "labelled spectrum, light spectrum and 10_H spectrum",
                "numerical global search (fast SOS evaluator validated against the live compiler)",
            ],
            "illustrative_only": [
                "GeV masses at r0 = M_I/M_GUT (anchor scales; the candidate's content does not reproduce the anchor)",
                "one-loop re-solve of the anchor chain with the candidate's content (tree-level thresholds, chart-unit identification)",
                "conditional two-loop SM running of the light-doublet quartic from the anchor M_I",
            ],
            "open": ([] if equality_proved else ["uniqueness of the equality set {V = V0} modulo symmetry (numerical evidence only)"])
            + [
                "exact (non-float) Hessian kernel/rank certificate",
                "electroweak symmetry breaking: H = 0 here, one doublet is tuned massless at tree level",
                "doublet-triplet splitting is tuned, not automatic: O46_1 = -(3/5) O46_54 (precision ~ (m_h/M_GUT)^2 ~ 2e-28) and O06 = 2|kappa| r0 (precision ~ (m_h/M_I)^2 ~ 4e-20); their radiative stability is not addressed",
                "light 126bar coloured states below M_I: (3,1)_1/3 at ~0.24 M_I (proton-decay mediator quantum numbers, coupled to 16.16 by the 126bar Yukawa that Majorana nu_R masses need), (6,1)_4/3 and (1,1)_2 at M_I/sqrt(96), (3,1)_4/3 + (6,1)_1/3 at ~0.25 M_I, (6,1)_2/3 at ~0.32 M_I; their proton-decay and RG/unification consequences are not analysed",
                "RG consistency: the anchor's M_I, M_GUT assume a light (15,2,2) above M_I and a 2HDM below; this candidate has the (15,2,2) at ~0.7 M_GUT and a 1HDM, and re-solving the one-loop chain with its content moves M_I and M_GUT (rg_anchor_consistency)",
                f"Higgs mass: the benchmark's tree-level lambda_eff = 127/64 at M_I is too large (m_h ~ {m_h_conditional:.0f} GeV under conditional SM running); the certified family kappa^2 < 8 r0^2 reaches lambda_eff -> 0+, near the measured Higgs mass (m_h ~ {lambda_zero['m_h_tree_GeV']:.0f} GeV at lambda(M_I) = 0), but tree-level global minimality forbids the slightly negative SM value lambda(M_I) = {lambda_required:.4f} at M_t = 173.34 GeV (sign M_t-dependent at ~2 sigma)",
                "intermediate scale: O05 = (1/8)(4 - 2 r0^2) cancels the Phi-induced O14/O44 (10bar,1,3) mass to precision ~ (M_I/M_GUT)^2 ~ 4e-9 at the anchor; its radiative stability is not addressed",
                "light doublet is an equal 5/5bar mixture (tan beta = 1 structure): with 10_H-only Yukawas m_t = m_b at matching",
                "realistic Yukawa sector: the H-linear portals O15, O38, O45, O28 vanish",
                "radiative stability of the M_I/M_GUT hierarchy",
            ],
        },
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return "The SM Pati-Salam candidate audit failed: " + ", ".join(report["failures"])
    m_h = report["light_doublet_quartic"]["conditional_sm_running"]["predictions"]["lambda_eff_127_over_64"]["m_h_tree_GeV"]
    if report["exact_certificate"]["equality_set"]["unique_modulo_symmetry_certified"]:
        uniqueness = (
            "The equality set {V = V0} is exactly the orbit of the vacuum under SO(10) x U(1)_X x U(1)_PQ "
            "(g3_sm_pati_salam_equality_set_v20), so the minimum is unique modulo symmetry once the accidental "
            "U(1)_PQ is included (modulo SO(10) x U(1)_X alone it is a circle of orbits). Electroweak breaking and a "
            "realistic Yukawa sector remain open"
        )
    else:
        uniqueness = (
            "Uniqueness of the minimum modulo symmetry, electroweak breaking and a realistic Yukawa sector remain open"
        )
    return (
        "The 27-parameter member of the declared exact-X potential obtained from the historical p-branch map by "
        "swapping the 2772bar/4125 self-projector weights, setting O05 = (1/8)(4 - 2 r0^2) and adding kappa_H = -r0/4 "
        "with O06 = 2|kappa| r0 has the vacuum (p, r0 sigma_std, 0, r0, x0), sigma_std = z1^z2^z3^z4^z5, whose "
        "unbroken algebra is exactly SU(3)_c x SU(2)_L x U(1)_Y (SO(10) -> Pati-Salam at M_GUT -> SM at r0 M_GUT). "
        "An adapted exact SOS identity gives V >= -1 - r0^4/8 - r0^4 - x0^4/32 on the whole field space and the "
        "vacuum attains it, so it is an exact global minimum of this benchmark potential, exactly stationary with "
        "PSD Hessian, for every r0 > 0 (checked on the live compiler at r0 = 1/5, 1/100, 1/1000 and M_I/M_GUT with "
        "x0 = 1: symmetry rank 35, kernel = symmetry tangents plus the 4 modes of one tuned light doublet, lightest "
        "massive mode r0^2/96). Physics caveats: one 10_H doublet is light (exactly massless at tree level) only "
        "because O46_1 = -(3/5) O46_54 and O06 = 2|kappa| r0 are tuned, while the 10_H colour triplets are at M_GUT "
        "for generic O46 couplings (doublet-triplet splitting is tuned, not automatic); the intermediate scale is "
        "itself a cancellation of O(1) couplings to ~(M_I/M_GUT)^2; 126bar colour "
        "triplets and sextets and a doubly charged singlet lie below M_I; only the breaking route matches the "
        "manuscript's Pati-Salam RG anchor, not its field content (no light (15,2,2), 1HDM instead of 2HDM), so the "
        "GeV masses at r0 = M_I/M_GUT are illustrative; and the light doublet's tree-level quartic is 127/64 at the "
        f"benchmark (m_h ~ {m_h:.0f} GeV under conditional SM running), too large; the certified family kappa^2 < "
        "8 r0^2 reaches lambda_eff -> 0+, near the measured Higgs mass, but tree-level global minimality forbids the "
        f"slightly negative SM value at M_t = 173.34 GeV. {uniqueness}; G3 is not closed and the model is neither "
        "validated nor excluded."
    )


def _fmt(value: Any, digits: int = 6) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def _cell(text: str) -> str:
    """Escape pipes inside a markdown table cell (SM labels and competitor names contain '|')."""
    return str(text).replace("|", "\\|")


def _markdown(report: Mapping[str, Any]) -> str:
    compiler = report["compiler"]
    certificate = report["exact_certificate"]
    embedding = report["sm_embedding"]
    lines = [
        "# G3 SM Pati-Salam candidate -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Candidate",
        "",
        "Vacuum `(Phi, Sigma, H, S, Phi17) = (p, r0 sigma_std, 0, r0, x0)`, `sigma_std = z1^z2^z3^z4^z5` (Y = 0).",
        "",
        "| parameter | historical (h=0) | candidate |",
        "|---|---|---|",
    ]
    for row in report["candidate"]["changes_from_historical_h0"]:
        lines.append(f"| `{row['parameter']}` | {row['historical_h0']} | {row['candidate']} |")
    lines += [
        "",
        f"- nonzero parameters: `{report['candidate']['nonzero_count']}` of 51; H-linear portals zero: `{report['candidate']['H_linear_portals_zero']}`",
        f"- unbroken algebra: {embedding['heavy_pair_stabilizer']['label']} (dim {embedding['heavy_pair_stabilizer']['stabilizer_dimension']}, centre ~ {embedding['heavy_pair_stabilizer']['centre_proportional_to']}); Phi = p alone: dim {embedding['phi_p_alone']['stabilizer_dimension']} (Pati-Salam)",
        "",
        "## Exact certificate",
        "",
        f"- identity: {certificate['adapted_identity']}",
        f"- sigma_std projector fractions: `{certificate['exact_sigma_std']['projector_fractions']}`; (M_p - 2) sigma = 0: `{certificate['checks']['M_p_sigma_std_equals_2_sigma_std']}`; C_p sigma = 0: `{certificate['checks']['C_p_sigma_std_vanishes']}`",
        f"- lower bound V0 = {certificate['lower_bound']['V0']} (= `{certificate['lower_bound']['V0_at_default']}` at r0 = 1/5, x0 = 1), attained at the vacuum",
        f"- BFB: `{certificate['bfb_certified']}`; global minimum: `{certificate['global_minimum_certified']}`; exact stationarity: `{certificate['exactly_stationary']}`; quartic part >= |q|^4/167",
        f"- equality set, unique modulo symmetry: {certificate['equality_set']['unique_modulo_symmetry']} "
        f"(equality-set artifact status `{certificate['equality_set']['equality_set_certificate']['status']}`, "
        f"n_failed `{certificate['equality_set']['equality_set_certificate']['n_failed']}`)",
        "",
        "## Compiler (float64)",
        "",
        "| r0 | max abs grad | V - V0 | sym. rank | n_neg | n_zero | min massive / r0^2 | abs. dev. from r0^2/96 | all-massive n_zero |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for label in sorted(compiler, key=lambda key: -float(compiler[key]["r0_float"])):
        row = compiler[label]
        lines.append(
            f"| {label} | {_fmt(row['gradient_max_abs'], 3)} | {_fmt(row['V_minus_V0'], 3)} | "
            f"{row['symmetry_ranks']['so10_plus_u1x_plus_pq_rank']} | {row['projected_hessian']['n_negative']} | "
            f"{row['projected_hessian']['n_zero']} | {_fmt(row['projected_hessian']['min_massive_over_r0_squared'], 10)} | "
            f"{_fmt(row['projected_hessian']['min_massive_absolute_deviation'], 3)} | "
            f"{row['all_massive_variant']['n_zero']} |"
        )
    lines += [
        "",
        "n_zero counts the 4 real modes of the tuned light doublet: the Hessian kernel is the 35 symmetry tangents "
        "plus that doublet, and exactly the symmetry tangents only when O06 is raised (last column). All benchmarks "
        "use x0 = 1.",
    ]
    spectrum = compiler["1/5"]["labelled_spectrum"]
    lines += [
        "",
        "### Spectrum at r0 = 1/5 (lightest clusters)",
        "",
        "The m^2/r0^2 column is a scaling only for the r0-dependent states (m^2 < 5 r0^2 below). The Phi17 radial mode "
        "(0.125 = x0^2/8) and every state from m^2 ~ 0.45 up are GUT-scale and do not scale with r0.",
        "",
        "| m^2 | m^2/r0^2 | real dim | SM content | fields |",
        "|---|---|---|---|---|",
    ]
    for row in spectrum["clusters"][:24]:
        content = ", ".join(f"{key}: {value}" for key, value in row["sm_content_real"].items())
        fields = ", ".join(f"{key} {value:.2f}" for key, value in row["field_weights"].items())
        lines.append(
            f"| {_fmt(row['mass_squared'], 8)} | {_fmt(row['mass_squared_over_r0_squared'], 8)} | {row['real_multiplicity']} | {_cell(content)} | {fields} |"
        )
    hierarchy = report["hierarchy"]
    physical = hierarchy["tree_masses_GeV_at_physical_r0"].get("light_states_at_physical_r0")
    if physical:
        lines += [
            "",
            "### Light states at r0 = M_I/M_GUT (illustrative GeV)",
            "",
            "Labelled by SM-isotypic component (exact-integer Casimirs), then diagonalised. GeV values use the anchor's "
            "M_I, which this content does not reproduce (see RG-anchor consistency).",
            "",
            "| SM content | m^2/r0^2 | m/M_I | m [GeV] | fields |",
            "|---|---|---|---|---|",
        ]
        for row in physical:
            content = ", ".join(f"{key}: {value}" for key, value in row["sm_content_real"].items())
            fields = ", ".join(f"{key} {value:.2f}" for key, value in row["field_weights"].items())
            lines.append(
                f"| {_cell(content)} | {_fmt(row['mass_squared_over_r0_squared'], 6)} | {_fmt(row['mass_over_M_I'], 4)} | "
                f"{_fmt(row['mass_GeV'], 4)} | {fields} |"
            )
    h10 = compiler["1/5"]["h10"]
    splitting = h10["doublet_triplet_splitting"]
    lines += [
        "",
        "### 10_H at r0 = 1/5",
        "",
        f"- real-block eigenvalues: `{ {key: [g['mass_squared'] for g in value] for key, value in h10['real_block_eigenvalues'].items()} }`",
        f"- doublet-triplet splitting (10_H only; tuned): {splitting['mechanism']}",
        f"- Phi-induced doublet m^2 = {splitting['doublet_phi_induced_mass_squared']['formula']} = "
        f"`{splitting['doublet_phi_induced_mass_squared']['value_at_candidate']}`; triplet m^2 = "
        f"{splitting['triplet_phi_induced_mass_squared']['formula']} = `{splitting['triplet_phi_induced_mass_squared']['value_at_candidate']}`",
        f"- tuned relations: {'; '.join(splitting['tuned_relations'])}",
        f"- light doublet weight in the 5 (span z4, z5): `{_fmt(splitting['doublet_composition']['light_doublet_weight_in_span_z4_z5'], 6)}` "
        "(equal 5/5bar mixture, tan beta = 1 structure)",
    ]
    rg = report["rg_anchor_consistency"]
    solutions = rg["one_loop_solutions"]
    lines += [
        "",
        "## Illustrative hierarchy and RG-anchor consistency",
        "",
        f"- {hierarchy['status']}",
        f"- units: {hierarchy['unit_identification']}",
        f"- Phi17: {hierarchy['phi17_note']}",
        f"- anchor content: below M_I {rg['anchor_field_content']['below_M_I']}; M_I to M_GUT {rg['anchor_field_content']['M_I_to_M_GUT']}",
        f"- candidate content: below M_I {rg['candidate_field_content']['below_M_I']}; M_I to M_GUT {rg['candidate_field_content']['M_I_to_M_GUT']}",
        f"- betas (U(1)_Y, SU(2)_L, SU(3)_c) below M_I: anchor `{rg['anchor_betas_from_field_content']['B_LOW']}`, "
        f"candidate `{rg['candidate_betas']['B_LOW_1HDM']}`; (SU(4), SU(2)_L, SU(2)_R) above M_I: anchor "
        f"`{rg['anchor_betas_from_field_content']['B_PS']}`, candidate `{rg['candidate_betas']['B_PS']}`",
        "",
        "| one-loop chain | M_I [GeV] | M_GUT [GeV] | alpha_GUT^-1 | M_I/M_GUT |",
        "|---|---|---|---|---|",
    ]
    for name, row in solutions.items():
        if row.get("solved", True) and "M_I_GeV" in row:
            ratio = row.get("M_I_over_M_GUT", row["M_I_GeV"] / row["M_GUT_GeV"])
            lines.append(
                f"| {name} | {_fmt(row['M_I_GeV'], 4)} | {_fmt(row['M_GUT_GeV'], 4)} | {_fmt(row['alpha_inv_GUT'], 4)} | {_fmt(ratio, 4)} |"
            )
        else:
            lines.append(f"| {name} | not solved | | | |")
    lines += ["", f"- {rg['caveats']}", f"- {rg['conclusion']}"]
    quartic = report["light_doublet_quartic"]
    running = quartic["conditional_sm_running"]
    compiler_quartic = compiler["1/5"]["light_doublet_quartic"]
    lines += [
        "",
        "## Light-doublet quartic (tree level)",
        "",
        f"- exact: lambda_eff = 2 - kappa^2/(4 r0^2) = `{quartic['lambda_eff']}`; compiler at r0 = 1/5: lambda_direct "
        f"`{_fmt(compiler_quartic['lambda_direct'], 10)}`, lambda_eff `{_fmt(compiler_quartic['lambda_eff'], 10)}`",
        f"- {quartic['global_minimality_forces_lambda_eff_nonnegative']}",
        f"- conditional two-loop SM running from M_I = `{_fmt(running['matching_scale_GeV'], 4)}` GeV: lambda(M_I) = 127/64 -> "
        f"m_h `{_fmt(running['predictions']['lambda_eff_127_over_64']['m_h_tree_GeV'], 4)}` GeV; SM needs lambda(M_I) = "
        f"`{_fmt(running['lambda_M_I_required_for_sm_two_loop'], 4)}`. {running['applicability']}",
    ]
    numerical = report.get("numerical_global_search")
    if numerical:
        lines += [
            "",
            "## Numerical global search",
            "",
            f"- fast SOS evaluator vs compiler: max relative value difference `{_fmt(numerical['fast_evaluator_validation']['max_relative_value_difference'], 3)}`",
            f"- lowest gap V - V0 found by any method: `{_fmt(numerical['lowest_gap_found_any_method'], 3)}`",
            "",
            "| competitor (r0 = 1/5) | compiler gap | exact gap | local min. from it: final gap | orbit classification |",
            "|---|---|---|---|---|",
        ]
        for name, row in numerical["structured_competitors_r0_1_5"].items():
            end = row["local_minimization_from_perturbed_optimum"]
            lines.append(
                f"| {_cell(name)} | {_fmt(row['compiler_gap'], 6)} | {row['exact_gap'] if row['exact_gap'] is not None else '-'} | "
                f"{_fmt(end['final_gap'], 3)} | {end['orbit_classification']} |"
            )
        lines.append("")
        for label, run in numerical["random_start_local_minimization"].items():
            counts = ", ".join(f"{name} {count}" for name, count in run["endpoint_classification_counts"].items())
            lines.append(
                f"- random starts ({label}): {len(run['starts'])}; lowest final gap `{_fmt(run['lowest_final_gap'], 3)}`; "
                f"endpoints {counts}; all converged endpoints on the SM vacuum orbit: "
                f"`{run['all_converged_endpoints_on_sm_vacuum_orbit']}`; none below V0: `{run['no_endpoint_below_V0']}`"
            )
        classification = numerical["endpoint_classification"]
        counts = ", ".join(f"{name} {count}" for name, count in classification["endpoint_classification_counts"].items())
        lines.append(
            f"- endpoint classification (all {sum(classification['endpoint_classification_counts'].values())} "
            f"endpoints): {counts}; all converged on the SM vacuum orbit: "
            f"`{classification['all_converged_endpoints_on_sm_vacuum_orbit']}`. {classification['method']}"
        )
        quartic = numerical["quartic_directions"]
        lines.append(
            f"- quartic part on the unit sphere: lowest `{_fmt(quartic['lowest_V4_found'], 6)}` >= exact bound 1/167: `{quartic['lowest_at_or_above_exact_bound']}`"
        )
        evidence = numerical["equality_set_evidence"]
        lines += [
            f"- equality set at Phi = p: ker(M_p - 2) n ker(C_p) has complex dimension "
            f"`{evidence['sigma_subspace_at_p']['complex_dimension']}` (contains sigma_std and delta_R); pure-spinor "
            f"minima in it all SM-type: `{evidence['all_pure_minima_sm_type']}`",
            f"- V_Phi minimizations all at -1 with a 21-dimensional (Pati-Salam) stabilizer: "
            f"`{evidence['all_V_Phi_minima_at_minus_1_with_pati_salam_stabilizer']}`",
        ]
    lines += ["", "## Flags", ""]
    lines += [f"- {key}: `{value}`" for key, value in report["flags"].items()]
    lines += ["", "Flag notes:", ""]
    lines += [f"- {key}: {value}" for key, value in report["flag_notes"].items()]
    lines += ["", "## Open", ""]
    lines += [f"- {item}" for item in report["scope"]["open"]]
    lines.append("")
    return "\n".join(lines)


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--light", action="store_true", help="skip the multi-r0 scan and the numerical search")
    args = parser.parse_args(argv)
    report = build_report(heavy=not args.light)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable({key: report[key] for key in ("status", "n_failed", "failures", "checks", "flags")}), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
