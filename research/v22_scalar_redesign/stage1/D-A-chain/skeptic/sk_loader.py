"""SKEPTIC loader (own code): read-only imports of the repo's v20 chart / potential modules, and the designer's
D-A-chain data files (read only).  Nothing is written outside this skeptic folder."""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
HERE = Path(__file__).resolve().parent
VAC = HERE.parent / "vac"
BANKDIR = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21R2\R2-A-vacuum-two-bidoublets")
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402
import live_g2_canonical_486_field_chart_v20 as chart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402
import g3_sm_pati_salam_candidate_v20 as candidate  # noqa: E402

BLOCKS = {"Phi210": chart.PHI_SLICE, "H10": chart.H_SLICE, "Sigma126bar": chart.SIGMA_SLICE, "S": chart.S_SLICE,
          "Phi17": chart.X_SLICE}


def phi_form(p, a, omega):
    b = direct.singlet_basis()
    return direct.add_forms(direct.scale_form(b["p"], p), direct.scale_form(b["a"], a), direct.scale_form(b["omega"], omega))


def build_state(p, a, omega, r, s, x):
    sigma = chart.sigma_from_coordinates(float(r) * candidate.sigma_std_unit_coordinates())
    return potential.FieldState(phi=phi_form(p, a, omega), h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex), sigma=sigma,
                                s=complex(s), x=complex(x)).validated()


def J_at(q, ids):
    """51 operator values via evaluate_directions + coefficient_jacobian (NOT the parameter_rows path of the LP/descent)."""
    st = chart.unpack(np.asarray(q, float)).validated()
    jac = potential.coefficient_jacobian(potential.evaluate_directions(st))
    return np.array([float(np.real(jac[p])) for p in ids])


def block_norms(q):
    return {k: float(np.linalg.norm(np.asarray(q)[sl])) for k, sl in BLOCKS.items()}
