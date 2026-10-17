"""K3 common helpers: build the G3221 vacuum state in the repo's 486-real chart (read-only imports)."""
from __future__ import annotations

import os
import sys
import json
import math
import time
from pathlib import Path

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
SCRATCH = Path(__file__).resolve().parent
if REPO not in sys.path:
    sys.path.insert(0, REPO)
# the repo modules read committed artifacts relative to their own file, no chdir needed

import numpy as np  # noqa: E402

import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402
import live_g2_canonical_486_field_chart_v20 as chart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402
import g3_candidate_physical_target_audit_v20 as target  # noqa: E402
import g3_sm_pati_salam_candidate_v20 as candidate  # noqa: E402
import gauged_u1x_g2_derivative_audit_v20 as g2_audit  # noqa: E402
import g3_sigma_hypercharge_audit_v20 as hypercharge  # noqa: E402
import exact_gauged_u1x_physical_quotient_v20 as quotient  # noqa: E402

TOTAL = chart.TOTAL_DIM
BLOCKS = {
    "Phi210": chart.PHI_SLICE,
    "H10": chart.H_SLICE,
    "Sigma126bar": chart.SIGMA_SLICE,
    "S": chart.S_SLICE,
    "Phi17": chart.X_SLICE,
}


def singlet_forms():
    """Unit-chart-norm p, a, omega four-forms (direct.singlet_basis, already normalised)."""
    return direct.singlet_basis()


def phi_form(p: float, a: float, omega: float):
    basis = singlet_forms()
    return direct.add_forms(
        direct.scale_form(basis["p"], p),
        direct.scale_form(basis["a"], a),
        direct.scale_form(basis["omega"], omega),
    )


def g3221_state(p: float, a: float, omega: float, r: float, s: complex, x: complex, h=None) -> potential.FieldState:
    """(Phi, H, Sigma, S, Phi17) = (p P + a A + omega W, h, r sigma_std, s, x); kinetic-normalised complex values."""
    sigma = chart.sigma_from_coordinates(float(r) * candidate.sigma_std_unit_coordinates())
    hvec = np.zeros(chart.H_COMPLEX_DIM, dtype=complex) if h is None else np.asarray(h, dtype=complex)
    return potential.FieldState(phi=phi_form(p, a, omega), h=hvec, sigma=sigma, s=complex(s), x=complex(x)).validated()


def state_from_q(q: np.ndarray) -> potential.FieldState:
    return chart.unpack(np.asarray(q, dtype=float))


def parameter_rows(state: potential.FieldState):
    """All 51 exact-X parameter rows (value, gradient, Hessian) at state; ~1 min."""
    return target.parameter_rows(state)


def symmetry_tangents(state: potential.FieldState):
    full, ranks = candidate.symmetry_matrix(state)
    return full, ranks


def sm_operators():
    return candidate.sm_label_operators()


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, complex):
        return {"re": value.real, "im": value.imag}
    return value
