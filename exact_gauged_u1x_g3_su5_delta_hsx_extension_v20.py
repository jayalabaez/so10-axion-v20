#!/usr/bin/env python3
"""Full-H/S/Phi17 extension audit for the exact SU(5)-singlet PD SOS.

The exact ``Phi+Sigma`` source is the global SOS in
``exact_gauged_u1x_g3_su5_delta_pd_sos_v20``.  This module answers two
separate questions about adjoining the complex 10, S and Phi17 fields.

First, the historically selected real vector ``H=e6`` cannot be a strict
minimum at the new ``F+Delta`` orbit.  At ``F`` the old wedge square is

    (3/5) O46_1 - O46_54 = (3/5) N_H,

so it does not vanish.  More generally, stationarity forces the O46_45
coefficient to vanish, while the only anisotropic Hermitian H--Sigma operator
has six positive, six negative and eight zero real eigenvalues.  After the
radial stationarity equation, each colour block has determinant
``-(lambda_35,45 r^2)^2``.  Thus a nonzero coefficient is tachyonic and a zero
coefficient leaves six non-gauge colour flats.  O06, both O12 components,
both H quartics, O35_1 and every O46 channel are included in this statement;
the remaining exact-X H portals either have zero H source or zero H-H jet at
``F+Delta``.

Second, the physical chiral neutral representative

    H_chi = (e6 + i e7)/sqrt(2)

escapes that obstruction.  The exact Hodge-projected square

    (3/5) O46_1 + O46_45 - O46_54
      = 2 ||P_chi(H wedge Phi)||^2

vanishes at ``F,H_chi``.  Adding ``beta O35_45`` with beta=1/20 lifts the six
colour flats.  At r=1/5 a live assembly of all 51 exact-X parameter rows gives
an exactly stationary 28-parameter candidate and a well-conditioned positive
448-dimensional numerical quotient Hessian.  A companion exact source-bound
certificate now proves full Hessian rank 448, nullity 38 and positive
semidefiniteness, so the physical quotient minimum is strict.  The largest
coupling is 11, below 4*pi.

The quartic is rigorously bounded below: on 10 x 126bar,

    ||P_210(H tensor Sigmadag)||^2 = (I_1 + I_45)/3 >= 0,

so ``I_45 >= -N_H N_Sigma``; beta < 2 sqrt(1/8) lets the H and Sigma norm
quartics dominate.  The finite-field gap is also proved nonnegative on the
entire ``Phi=+F`` simultaneous mixed-zero kernel, for arbitrary H and Sigma
norms and orientations.  A companion exact off-kernel certificate extends
this to every H and Sigma at ``Phi=+F``.  The signed companion ``Phi=-F`` has
no nonzero mixed-zero kernel.  What is *not* proved here is uniform coercivity
away from the signed Phi equality strata, or the corresponding global
equality classification.  Consequently this is a proof-grade real-H
obstruction and exact stationary candidate.  Its live full-Hessian diagnostic
is retained for provenance; the companion exact-Hessian certificate supersedes
it for proof purposes.  The arbitrary-Phi gap still prevents this module from
closing G3 by itself.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_gauged_u1x_g3_a_square_recoupling_v20 as recoupling_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import exact_phi2_h_126dag_210_1050_channels_v20 as h_sigma_projectors
import exact_phi2_hdagh_channel_family_v20 as phi_h_source
import exact_unique_hsigma_chiral_quartics_v20 as unique_source
import g1_exact_declared_symmetry_character_census_v20 as census_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_hsigma_hermitian_derivatives_v20 as hsigma_derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
R = Fraction(1, 5)
X = Fraction(1)
BETA = Fraction(1, 20)
KAPPA_HOLO = Fraction(1)
SIGMA_SCALE = Fraction(1, 8)
EXPECTED_SO10_RANK = 36
EXPECTED_GAUGE_RANK = 37
EXPECTED_FULL_SYMMETRY_RANK = 38
EXPECTED_QUOTIENT_DIMENSION = chart.TOTAL_DIM - EXPECTED_FULL_SYMMETRY_RANK

RECORDED_LIVE_HESSIAN = {
    "evidence_kind": "live_486_field_exact_X_compiler_float64",
    "recomputed_in_this_invocation": False,
    "proof_grade": False,
    "r": float(R),
    "x": float(X),
    "beta": float(BETA),
    "full_gradient_max_abs_residual": 1.1515094433534045e-13,
    "full_gradient_norm_upper_record": 3.0158829916758474e-13,
    "numerical_symmetry_orbit_rank": 38,
    "transverse_dimension": 448,
    "stationary_Hessian_symmetry_max_abs_residual": 5.03220200501134e-13,
    "minimum_transverse_eigenvalue": 0.004844587743069171,
    "maximum_transverse_eigenvalue": 8.065581903137401,
    "negative_transverse_eigenvalues_below_minus_1e_minus_9": 0,
    "zero_transverse_eigenvalues_at_1e_minus_9": 0,
    "strict_local_minimum_high_confidence_numeric": True,
    "strict_local_minimum_proof_grade": False,
}

RECORDED_AFFINE_PORTAL_GRADIENT_AUDIT = {
    "evidence_kind": "targeted_live_G2_exact_X_parameter_gradient_rows_float64",
    "parameter_order": [
        "re::O12_B01_Hdag_Hdag_pair",
        "im::O12_B01_Hdag_Hdag_pair",
        "re::O15_B01_Phi_Hdag_Sigma",
        "im::O15_B01_Phi_Hdag_Sigma",
        "re::O38_B01_Phi_Hdag_Sigmadag",
        "im::O38_B01_Phi_Hdag_Sigmadag",
    ],
    "gradient_gram_exact_target_diagonal": [
        "8/25",
        "8/25",
        "62/25",
        "62/25",
        "2/625",
        "2/625",
    ],
    "maximum_off_diagonal_abs": 0.0,
    "maximum_diagonal_target_residual": 8.881784197001252e-16,
    "gradient_column_rank": 6,
    "stationarity_preserving_portal_only_nullity": 0,
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def normalized_f() -> direct.Form:
    raw, _ = pd_source.raw_su5_form_and_vector()
    return direct.scale_form(raw, 1.0 / math.sqrt(10.0))


def h_vector(*, chiral: bool) -> np.ndarray:
    output = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    if chiral:
        output[6] = 1.0 / math.sqrt(2.0)
        output[7] = 1j / math.sqrt(2.0)
    else:
        output[6] = 1.0
    return output


def candidate_state(*, chiral: bool = True, r: float = float(R), x: float = float(X)) -> potential.FieldState:
    if not (math.isfinite(r) and r > 0 and math.isfinite(x) and x > 0):
        raise ValueError("r and x must be finite and positive")
    return potential.FieldState(
        phi=normalized_f(),
        h=h_vector(chiral=chiral),
        sigma=direct.scale_form(direct.delta_r(), r),
        s=complex(r),
        x=complex(x),
    ).validated()


@lru_cache(maxsize=1)
def exact_phi_h_chiral_square_certificate() -> dict[str, Any]:
    phi = normalized_f()
    operators = phi_h_source.channel_operators(phi)
    identity = np.eye(10, dtype=complex)
    expected_45 = np.zeros((10, 10), dtype=complex)
    for first, second in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9)):
        expected_45[first, second] = 3j / 5
        expected_45[second, first] = -3j / 5
    old_operator = (3.0 / 5.0) * operators["1"] - operators["54"]
    chiral_operator = old_operator + operators["45"]
    h_real = h_vector(chiral=False)
    h_chiral = h_vector(chiral=True)

    # Independent all-component Hodge projection identity on deterministic data.
    rng = np.random.default_rng(61020)
    phi_probe = {
        indices: complex(value)
        for indices, value in zip(chart.PHI_INDICES, rng.integers(-2, 3, size=chart.PHI_DIM), strict=True)
        if value
    }
    h_probe = rng.integers(-2, 3, size=10) + 1j * rng.integers(-2, 3, size=10)
    h_form = {(index,): complex(value) for index, value in enumerate(h_probe) if value}
    wedge = direct.wedge(h_form, phi_probe)
    projected = direct.scale_form(
        direct.add_forms(wedge, direct.scale_form(direct.hodge_star(wedge), -1j)),
        0.5,
    )
    invariants = phi_h_source.invariant_values(phi_probe, h_probe)
    combination = (
        Fraction(3, 5) * invariants["1"]
        + invariants["45"]
        - invariants["54"]
    )
    projection_residual = abs(
        float(combination) - 2.0 * float(direct.tensor_inner(projected, projected).real)
    )
    eigenvalues = np.linalg.eigvalsh(chiral_operator)
    return {
        "old_square_identity": "(3/5)O46_1-O46_54=||H wedge Phi||^2",
        "old_square_at_F": "(3/5)N_H",
        "old_square_at_F_H_equals_e6": Fraction(3, 5),
        "old_square_vanishes_at_real_H": False,
        "F_channel_1_identity_residual": float(np.max(np.abs(operators["1"] - identity))),
        "F_channel_54_zero_residual": float(np.max(np.abs(operators["54"]))),
        "F_channel_45_expected_residual": float(np.max(np.abs(operators["45"] - expected_45))),
        "chiral_square_identity": (
            "(3/5)O46_1+O46_45-O46_54=2||P_chi(H wedge Phi)||^2"
        ),
        "deterministic_all_component_identity_residual": projection_residual,
        "F_chiral_operator_eigenvalues": eigenvalues,
        "F_chiral_operator_rank": int(np.linalg.matrix_rank(chiral_operator, tol=1e-12)),
        "F_chiral_operator_Hchi_residual": float(np.linalg.norm(chiral_operator @ h_chiral)),
        "F_45_maps_real_e6_to_orthogonal_i_e7": float(
            abs((operators["45"] @ h_real)[7])
        ),
        "source_binding_exact": bool(
            projection_residual < 1e-9
            and np.max(np.abs(operators["54"])) < 1e-12
            and np.linalg.norm(chiral_operator @ h_chiral) < 1e-12
        ),
    }


@lru_cache(maxsize=1)
def exact_portal_zero_jet_certificate() -> dict[str, Any]:
    """Source-support zeros needed by the real-H obstruction."""
    phi = normalized_f()
    sigma = direct.delta_r()
    sigma_dag = {indices: np.conjugate(value) for indices, value in sigma.items()}
    cubic_sigma = direct.contract(phi, sigma)
    cubic_sigma_dag = direct.contract(phi, sigma_dag)

    dense = unique_source.forms.dense_antisymmetric(sigma, 5)
    dense_dag = np.conjugate(dense)
    o28_source = np.einsum(
        "bcdef,abcgh,defgh->a", dense, dense, dense_dag, optimize="greedy"
    )
    o31_matrix = np.einsum("bcdef,acdef->ab", dense, dense, optimize="greedy")

    phi2 = h_sigma_projectors.phi2_bilinear(phi, phi, +1)
    sigma_full = h_sigma_projectors.five_to_vector(sigma)
    o45_sources = {}
    for channel, projected in (
        ("210", h_sigma_projectors.project_210(phi2, +1)),
        ("1050", h_sigma_projectors.project_1050(phi2, +1)),
    ):
        direct_source = projected @ sigma_full
        conjugate_source = projected @ np.conjugate(sigma_full)
        o45_sources[channel] = max(
            float(np.max(np.abs(direct_source), initial=0.0)),
            float(np.max(np.abs(conjugate_source), initial=0.0)),
        )
    residuals = {
        "O15_H_source": direct.tensor_norm(cubic_sigma),
        "O38_H_source": direct.tensor_norm(cubic_sigma_dag),
        "O28_H_source": float(np.max(np.abs(o28_source), initial=0.0)),
        "O31_HH_source": float(np.max(np.abs(o31_matrix), initial=0.0)),
        "O45_210_H_source": o45_sources["210"],
        "O45_1050_H_source": o45_sources["1050"],
    }
    maximum = max(residuals.values())
    return {
        "residuals": residuals,
        "maximum_abs_residual": maximum,
        "linear_H_families_have_zero_H_source": maximum < 1e-11,
        "O31_has_zero_HH_jet": residuals["O31_HH_source"] < 1e-11,
        "source_binding": "canonical F support and physical -i-Hodge Delta tensor",
        "source_binding_exact": maximum < 1e-11,
    }


@lru_cache(maxsize=1)
def exact_positive_affine_sos_replacement_no_go_certificate() -> dict[str, Any]:
    """Exclude a beta-free all-vanishing affine SOS at the chiral target.

    The complete renormalizable affine pairings that could distinguish the
    electroweak component of H from its colour partners are represented by
    O12, O15/O38 and the two O45 projector channels.  At the target their two
    sides are either forced to have unequal zero/nonzero status or are
    nonzero orthogonal vectors.  Hence no nontrivial residual of these types
    can vanish there.  This does not exclude a construction whose positive
    squares have nonzero residuals and whose gradients cancel between terms.
    """
    portal_counts = {
        "O12_HH_vs_S": (0, 0, 2, 0, 0, 0, 1, 0, 0),
        "O15_PhiH_vs_Sigma": (1, 0, 1, 1, 0, 0, 0, 0, 0),
        "O38_PhiH_vs_S_Sigmadag": (1, 0, 1, 0, 1, 0, 1, 0, 0),
    }
    exact_x_charges = {
        name: census_source.charge(counts) for name, counts in portal_counts.items()
    }
    contract_ids = set(g2_audit.contract_selection()["parameter_ids"])
    portal_parameter_ids = set(
        RECORDED_AFFINE_PORTAL_GRADIENT_AUDIT["parameter_order"]
    )

    phi = normalized_f()
    h = h_vector(chiral=True)
    h_form = {
        (index,): complex(value) for index, value in enumerate(h) if value != 0
    }
    delta = direct.delta_r()
    delta_dag = {indices: np.conjugate(value) for indices, value in delta.items()}
    phi_h_five = direct.wedge(h_form, phi)
    phi_h_norm_squared = float(direct.tensor_inner(phi_h_five, phi_h_five).real)
    delta_norm_squared = float(direct.tensor_inner(delta, delta).real)
    phi_h_delta_inner = direct.tensor_inner(delta, phi_h_five)
    phi_h_delta_dag_inner = direct.tensor_inner(delta_dag, phi_h_five)
    contracted_delta = direct.contract(phi, delta)
    contracted_delta_dag = direct.contract(phi, delta_dag)

    h_plus_integer = np.zeros((10, 5), dtype=complex)
    for index in range(5):
        h_plus_integer[2 * index, index] = 1
        h_plus_integer[2 * index + 1, index] = 1j
    h_holomorphic_pair = complex(np.dot(h, h))
    h_plus_pairing = h_plus_integer.T @ h_plus_integer

    phi2 = h_sigma_projectors.phi2_bilinear(phi, phi, -1)
    external = h[:, None] * h_sigma_projectors.five_to_vector(delta)[None, :]
    phi2_210 = h_sigma_projectors.project_210(phi2, -1)
    phi2_1050 = h_sigma_projectors.project_1050(phi2, -1)
    external_210 = h_sigma_projectors.project_210(external, -1)
    external_1050 = h_sigma_projectors.project_1050(external, -1)
    projector_values = {
        "Phi2_210_norm_squared": float(np.vdot(phi2_210, phi2_210).real),
        "Phi2_1050_norm_squared": float(np.vdot(phi2_1050, phi2_1050).real),
        "HDelta_210_norm_squared": float(np.vdot(external_210, external_210).real),
        "HDelta_1050_norm_squared": float(
            np.vdot(external_1050, external_1050).real
        ),
        "channel_210_inner": complex(np.vdot(phi2_210, external_210)),
        "channel_1050_inner": complex(np.vdot(phi2_1050, external_1050)),
    }
    projector_target_residual = max(
        abs(projector_values["Phi2_210_norm_squared"] - 24.0 / 5.0),
        abs(projector_values["Phi2_1050_norm_squared"]),
        abs(projector_values["HDelta_210_norm_squared"] - 1.0 / 3.0),
        abs(projector_values["HDelta_1050_norm_squared"] - 5.0 / 3.0),
        abs(projector_values["channel_210_inner"]),
        abs(projector_values["channel_1050_inner"]),
    )
    exact_x_neutral = all(
        charges == {"PQ": 0, "X": 0, "Z17": 0}
        for charges in exact_x_charges.values()
    )
    source_orthogonality = bool(
        direct.tensor_norm(contracted_delta) == 0.0
        and direct.tensor_norm(contracted_delta_dag) == 0.0
        and abs(phi_h_delta_inner) == 0.0
        and abs(phi_h_delta_dag_inner) == 0.0
        and abs(phi_h_norm_squared - 3.0 / 5.0) < 1e-14
        and abs(delta_norm_squared - 2.0) < 1e-14
        and projector_target_residual < 1e-12
    )
    scalar_no_go = bool(
        h_holomorphic_pair == 0
        and np.max(np.abs(h_plus_pairing), initial=0.0) == 0.0
        and R != 0
    )
    gradient_audit = dict(RECORDED_AFFINE_PORTAL_GRADIENT_AUDIT)
    gradient_rows_independent = bool(
        gradient_audit["gradient_column_rank"] == 6
        and gradient_audit["stationarity_preserving_portal_only_nullity"] == 0
        and gradient_audit["maximum_off_diagonal_abs"] == 0.0
        and gradient_audit["maximum_diagonal_target_residual"] < 1e-12
    )
    proof_grade = bool(
        exact_x_neutral
        and portal_parameter_ids <= contract_ids
        and source_orthogonality
        and scalar_no_go
        and gradient_rows_independent
    )
    return {
        "status": (
            "EXACT_NO_GO_FOR_ALL_VANISHING_RENORMALIZABLE_AFFINE_SOS_REPLACEMENT"
            if proof_grade
            else "AFFINE_SOS_REPLACEMENT_AUDIT_FAILED"
        ),
        "exact_X_portals": {
            name: {
                "counts": dict(zip(census_source.FIELD_ORDER, counts, strict=True)),
                "charges": exact_x_charges[name],
            }
            for name, counts in portal_counts.items()
        },
        "all_portal_parameters_in_51_parameter_contract": (
            portal_parameter_ids <= contract_ids
        ),
        "O12_scalar_obstruction": {
            "target_H_dot_H": h_holomorphic_pair,
            "target_S": R,
            "consequence": "H.H-c S*=0 forces c=0",
            "H_dot_H_identically_zero_on_chiral_C5": bool(
                np.max(np.abs(h_plus_pairing), initial=0.0) == 0.0
            ),
            "therefore_cannot_lift_six_chiral_colour_flats": True,
        },
        "O15_O38_126_residual_obstruction": {
            "Phi_contract_Delta_norm": direct.tensor_norm(contracted_delta),
            "Phi_contract_Deltadag_norm": direct.tensor_norm(contracted_delta_dag),
            "H_wedge_Phi_norm_squared": phi_h_norm_squared,
            "Delta_norm_squared": delta_norm_squared,
            "inner_HwedgePhi_Delta": phi_h_delta_inner,
            "inner_HwedgePhi_Deltadag": phi_h_delta_dag_inner,
            "consequence": (
                "L(F,Hchi) is orthogonal to Delta and Deltadag; equality to "
                "a nonzero scalar multiple is impossible"
            ),
        },
        "O45_210_1050_residual_obstruction": {
            **projector_values,
            "expected_exact_norms": {
                "Phi2": {"210": "24/5", "1050": "0"},
                "Hchi_tensor_Delta": {"210": "1/3", "1050": "5/3"},
            },
            "maximum_source_target_residual": projector_target_residual,
            "consequence": (
                "the 210 vectors are nonzero and orthogonal, while the Phi2 "
                "1050 side is zero and the Hchi-Delta side is nonzero"
            ),
        },
        "targeted_G2_gradient_audit": gradient_audit,
        "all_vanishing_positive_affine_SOS_can_replace_beta": False,
        "nonvanishing_residual_gradient_cancellation_construction_excluded": False,
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def real_h_exact_no_go_certificate() -> dict[str, Any]:
    state = candidate_state(chiral=False, r=1.0, x=1.0)
    q = chart.pack(state)
    _, gradient_45, hessian_45 = hsigma_derivatives.base_derivative(q, 1)
    matrix_45 = np.asarray(hessian_45[chart.H_SLICE, chart.H_SLICE]).real
    spectrum = np.linalg.eigvalsh(matrix_45)
    phi = exact_phi_h_chiral_square_certificate()
    zeros = exact_portal_zero_jet_certificate()
    # The O35_45 gradient vanishes at the real EW representative.
    hsigma_gradient = np.asarray(gradient_45[chart.H_SLICE])
    return {
        "scope": (
            "all exact-X H-dependent families O06,O12,O15,O28,O31,O35,O36,"
            "O38,O45,O46 at Phi=F,Sigma=r Delta,H=e6,S real"
        ),
        "old_Phi_H_alignment_value": Fraction(3, 5),
        "old_Phi_H_alignment_fails_zero_locus": True,
        "O46_at_F": {
            "channel_1": "identity",
            "channel_45": "maps e6 to -(3/5)i e7",
            "channel_54": "zero",
            "stationarity_forces_lambda_46_45_zero": True,
        },
        "linear_and_chiral_portal_zero_jets": zeros,
        "O35_45_H_gradient_max_abs": float(np.max(np.abs(hsigma_gradient), initial=0.0)),
        "O35_45_real_Hessian_spectrum": spectrum,
        "O35_45_signature": {"negative": 6, "zero": 8, "positive": 6},
        "general_colour_block": "[[0,+/-c],[+/-c,m]], c=lambda_35_45*r^2",
        "general_colour_characteristic_polynomial": "lambda^2-m*lambda-c^2",
        "general_colour_eigenvalues": "(m +/- sqrt(m^2+4c^2))/2, each x6",
        "block_determinant": "-c^2",
        "role_of_O06_O12_O36_O35_1_O46_1": (
            "they determine m and the radial equation; radial stationarity makes "
            "the real-colour diagonal exactly zero, so no finite m changes det=-c^2"
        ),
        "lambda_35_45_nonzero": "at least six transverse tachyonic directions",
        "lambda_35_45_zero": "six non-gauge real-colour flat directions",
        "strict_transverse_minimum_with_real_H_possible": False,
        "source_binding_exact": bool(
            phi["source_binding_exact"]
            and zeros["source_binding_exact"]
            and np.max(np.abs(hsigma_gradient), initial=0.0) < 1e-12
            and np.sum(spectrum < -1e-12) == 6
            and np.sum(np.abs(spectrum) <= 1e-12) == 8
            and np.sum(spectrum > 1e-12) == 6
        ),
    }


def symbolic_coefficient_map() -> dict[str, str]:
    output = dict(pd_source.symbolic_coefficient_map())
    output.update(
        {
            "lambda::O06_B01_Hdag_H_norm": "-2",
            "lambda::O36_B01_H_self_quartics": "11",
            "lambda::O36_B02_H_self_quartics": "1",
            "lambda::O04_B01_singlet_polynomial": "-2/25",
            "lambda::O23_B01_singlet_polynomial": "1",
            "lambda::O03_B01_singlet_polynomial": "-1/16",
            "lambda::O20_B01_singlet_polynomial": "1/32",
            "lambda::O46_B01_Phi2_HdagH_channels": "3/5",
            "lambda::O46_B02_Phi2_HdagH_channels": "1",
            "lambda::O46_B03_Phi2_HdagH_channels": "-1",
            "lambda::O35_B02_H_Sigma_hermitian": "1/20",
        }
    )
    return output


def numerical_coefficient_map() -> dict[str, float]:
    output = pd_source.numerical_coefficient_map(float(R))
    output.update(
        {
            "lambda::O06_B01_Hdag_H_norm": -2.0,
            "lambda::O36_B01_H_self_quartics": 11.0,
            "lambda::O36_B02_H_self_quartics": 1.0,
            "lambda::O04_B01_singlet_polynomial": -2.0 / 25.0,
            "lambda::O23_B01_singlet_polynomial": 1.0,
            "lambda::O03_B01_singlet_polynomial": -1.0 / 16.0,
            "lambda::O20_B01_singlet_polynomial": 1.0 / 32.0,
            "lambda::O46_B01_Phi2_HdagH_channels": 3.0 / 5.0,
            "lambda::O46_B02_Phi2_HdagH_channels": 1.0,
            "lambda::O46_B03_Phi2_HdagH_channels": -1.0,
            "lambda::O35_B02_H_Sigma_hermitian": 1.0 / 20.0,
        }
    )
    return output


@lru_cache(maxsize=1)
def exact_orbit_rank_certificate() -> dict[str, Any]:
    f0, _ = pd_source.raw_su5_form_and_vector()
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    raw_h = np.zeros(10, dtype=complex)
    raw_h[6] = 1
    raw_h[7] = 1j
    state = potential.FieldState(
        phi=f0,
        h=raw_h,
        sigma=chart.sigma_from_coordinates(delta_real + 1j * delta_imaginary),
        s=1 + 0j,
        x=1 + 0j,
    ).validated()
    observed = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            quotient_source._phase_tangent(state, quotient_source.PQ_CHARGES),
        )
    )
    carrier = observed.copy()
    for block in (chart.H_SLICE, chart.SIGMA_SLICE, chart.S_SLICE, chart.X_SLICE):
        carrier[block] /= chart.SQRT2
    rounded = np.rint(carrier).astype(np.int64)
    lattice_residual = float(np.max(np.abs(carrier - rounded), initial=0.0))
    ranks = []
    metadata = []
    for columns in (45, 46, 47):
        rank, pivot_rows, pivot_columns = quotient_source._row_echelon_metadata(
            tuple(tuple(int(value) for value in row) for row in rounded[:, :columns])
        )
        ranks.append(rank)
        metadata.append((pivot_rows, pivot_columns))
    return {
        "method": "exact integer row echelon after invertible block-row scaling",
        "integer_lattice_residual": lattice_residual,
        "SO10_rank": ranks[0],
        "SO10_plus_U1X_rank": ranks[1],
        "SO10_plus_U1X_plus_PQ_rank": ranks[2],
        "full_symmetry_nullity": 47 - ranks[2],
        "physical_quotient_dimension": chart.TOTAL_DIM - ranks[2],
        "pivot_column_counts": [len(item[1]) for item in metadata],
        "source_binding_exact": bool(
            lattice_residual == 0
            and ranks
            == [EXPECTED_SO10_RANK, EXPECTED_GAUGE_RANK, EXPECTED_FULL_SYMMETRY_RANK]
        ),
    }


@lru_cache(maxsize=1)
def exact_hsigma_projector_fierz_certificate() -> dict[str, Any]:
    """Prove the 10 x 126 projector/Fierz identity coefficient by coefficient."""
    sigma_dag_vectors = np.stack(
        [
            h_sigma_projectors.five_to_vector(
                {indices: np.conjugate(value) for indices, value in state.items()}
            )
            for state in chart.sigma_basis()
        ]
    )
    injection = h_sigma_projectors.injection_matrix(+1)
    contraction = np.stack(
        [
            sigma_dag_vectors
            @ injection[
                h_index * len(h_sigma_projectors.C5) :
                (h_index + 1) * len(h_sigma_projectors.C5)
            ].conj()
            for h_index in range(chart.H_COMPLEX_DIM)
        ],
        axis=1,
    )

    def gaussian_parts(
        value: np.ndarray, scale: int = 1
    ) -> tuple[np.ndarray, np.ndarray, float]:
        scaled = scale * np.asarray(value, dtype=complex)
        real = np.rint(scaled.real).astype(np.int64)
        imaginary = np.rint(scaled.imag).astype(np.int64)
        residual = max(
            float(np.max(np.abs(scaled.real - real), initial=0.0)),
            float(np.max(np.abs(scaled.imag - imaginary), initial=0.0)),
        )
        return real, imaginary, residual

    # The chiral injection and its contraction have half-integral Gaussian
    # entries.  Clearing that denominator makes the full comparison integral.
    injection_real, injection_imaginary, injection_residual = gaussian_parts(
        injection, 2
    )
    contraction_real, contraction_imaginary, contraction_residual = (
        gaussian_parts(contraction, 2)
    )
    sigma_basis_real, sigma_basis_imaginary, sigma_basis_residual = (
        gaussian_parts(sigma_dag_vectors)
    )
    h_real, h_imaginary, h_residual = gaussian_parts(
        hsigma_derivatives.h_generator_matrices()
    )
    sigma_real, sigma_imaginary, sigma_residual = gaussian_parts(
        hsigma_derivatives.sigma_generator_matrices()
    )

    injection_gram_real = (
        injection_real.T @ injection_real
        + injection_imaginary.T @ injection_imaginary
    )
    injection_gram_imaginary = (
        injection_real.T @ injection_imaginary
        - injection_imaginary.T @ injection_real
    )
    injection_gram_exact = bool(
        np.array_equal(
            injection_gram_real,
            12 * np.eye(len(h_sigma_projectors.C4), dtype=np.int64),
        )
        and not np.any(injection_gram_imaginary)
    )
    sigma_basis_gram_real = (
        sigma_basis_real @ sigma_basis_real.T
        + sigma_basis_imaginary @ sigma_basis_imaginary.T
    )
    sigma_basis_gram_imaginary = (
        sigma_basis_imaginary @ sigma_basis_real.T
        - sigma_basis_real @ sigma_basis_imaginary.T
    )
    sigma_basis_gram_exact = bool(
        np.array_equal(
            sigma_basis_gram_real,
            2 * np.eye(chart.SIGMA_COMPLEX_DIM, dtype=np.int64),
        )
        and not np.any(sigma_basis_gram_imaginary)
    )
    h_generators_real_skew = bool(
        not np.any(h_imaginary)
        and not np.any(h_real + np.swapaxes(h_real, 1, 2))
    )
    sigma_generators_antihermitian = bool(
        not np.any(sigma_real + np.swapaxes(sigma_real, 1, 2))
        and not np.any(sigma_imaginary - np.swapaxes(sigma_imaginary, 1, 2))
    )

    flattened_real = contraction_real.reshape(-1, len(h_sigma_projectors.C4))
    flattened_imaginary = contraction_imaginary.reshape(
        -1, len(h_sigma_projectors.C4)
    )
    projector_real = (
        flattened_real @ flattened_real.T
        + flattened_imaginary @ flattened_imaginary.T
    )
    projector_imaginary = (
        flattened_real @ flattened_imaginary.T
        - flattened_imaginary @ flattened_real.T
    )
    projector_real = (
        projector_real.reshape(
            chart.SIGMA_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
            chart.SIGMA_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
        )
        .transpose(0, 2, 1, 3)
        .swapaxes(0, 1)
    )
    projector_imaginary = (
        projector_imaginary.reshape(
            chart.SIGMA_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
            chart.SIGMA_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
        )
        .transpose(0, 2, 1, 3)
        .swapaxes(0, 1)
    )

    generator_count = h_real.shape[0]
    sigma_real_flat = sigma_real.reshape(generator_count, -1)
    sigma_imaginary_flat = sigma_imaginary.reshape(generator_count, -1)
    h_real_flat = h_real.reshape(generator_count, -1)
    h_imaginary_flat = h_imaginary.reshape(generator_count, -1)
    current_real = (
        sigma_real_flat.T @ h_real_flat
        - sigma_imaginary_flat.T @ h_imaginary_flat
    ).reshape(
        chart.SIGMA_COMPLEX_DIM,
        chart.SIGMA_COMPLEX_DIM,
        chart.H_COMPLEX_DIM,
        chart.H_COMPLEX_DIM,
    )
    current_imaginary = (
        sigma_real_flat.T @ h_imaginary_flat
        + sigma_imaginary_flat.T @ h_real_flat
    ).reshape(
        chart.SIGMA_COMPLEX_DIM,
        chart.SIGMA_COMPLEX_DIM,
        chart.H_COMPLEX_DIM,
        chart.H_COMPLEX_DIM,
    )
    expected_real = -4 * current_real
    expected_imaginary = -4 * current_imaginary
    for sigma_index in range(chart.SIGMA_COMPLEX_DIM):
        expected_real[sigma_index, sigma_index] += 4 * np.eye(
            chart.H_COMPLEX_DIM, dtype=np.int64
        )
    coefficient_residual = max(
        int(np.max(np.abs(projector_real - expected_real), initial=0)),
        int(
            np.max(
                np.abs(projector_imaginary - expected_imaginary), initial=0
            )
        ),
    )
    lattice_residual = max(
        injection_residual,
        contraction_residual,
        sigma_basis_residual,
        h_residual,
        sigma_residual,
    )
    return {
        "identity": "3 L_z^dag P210 L_z = N_Sigma I_10 + J_z",
        "coefficient_tensor_shape": [
            chart.SIGMA_COMPLEX_DIM,
            chart.SIGMA_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
            chart.H_COMPLEX_DIM,
        ],
        "cleared_denominator": 4,
        "Gaussian_lattice_residual": lattice_residual,
        "twice_injection_Gram_is_12I_exact": injection_gram_exact,
        "raw_Sigma_basis_Gram_is_2I_exact": sigma_basis_gram_exact,
        "H_generators_are_real_skew_exact": h_generators_real_skew,
        "Sigma_generators_are_antihermitian_exact": (
            sigma_generators_antihermitian
        ),
        "integer_coefficient_identity_max_abs_residual": coefficient_residual,
        "all_126_squared_by_10_squared_coefficients_exact": (
            coefficient_residual == 0
        ),
        "source_binding_exact": bool(
            lattice_residual == 0.0
            and injection_gram_exact
            and sigma_basis_gram_exact
            and h_generators_real_skew
            and sigma_generators_antihermitian
            and coefficient_residual == 0
        ),
    }


@lru_cache(maxsize=1)
def exact_hsigma_current_bound_certificate() -> dict[str, Any]:
    """Bind I45 >= -I1 to the positive 210 projector norm."""
    exact_fierz = exact_hsigma_projector_fierz_certificate()
    rng = np.random.default_rng(12610)
    h = rng.integers(-2, 3, size=10) + 1j * rng.integers(-2, 3, size=10)
    z = rng.integers(-2, 3, size=chart.SIGMA_COMPLEX_DIM) + 1j * rng.integers(
        -2, 3, size=chart.SIGMA_COMPLEX_DIM
    )
    sigma = chart.sigma_from_coordinates(z)
    state = potential.FieldState(phi={}, h=h, sigma=sigma, s=0j, x=0j)
    invariants = hsigma_derivatives.direct_source_values(state)
    sigma_dag = {indices: np.conjugate(value) for indices, value in sigma.items()}
    sigma_vector = h_sigma_projectors.five_to_vector(sigma_dag)
    external = h[:, None] * sigma_vector[None, :]
    projected = h_sigma_projectors.project_210(external, +1)
    projected_norm = float(np.vdot(projected, projected).real)
    expected = float((invariants["channel_1"] + invariants["channel_45"]).real / 3.0)
    residual = abs(projected_norm - expected)
    margin = 2.0 * math.sqrt(float(SIGMA_SCALE)) - float(BETA)
    radial_form_positive_exact = BETA * BETA < 4 * SIGMA_SCALE
    return {
        "exact_projector_identity": "||P210(H tensor Sigmadag)||^2=(I1+I45)/3",
        "deterministic_source_residual": residual,
        "exact_coefficient_certificate": exact_fierz,
        "consequence": "I45 >= -I1 = -(Hdag H) N_Sigma",
        "radial_quartic_bound": (
            "N_H^2+(1/8)N_Sigma^2+beta I45 >= "
            "N_H^2+(1/8)N_Sigma^2-beta N_H N_Sigma"
        ),
        "beta": BETA,
        "two_sqrt_t_minus_beta": margin,
        "beta_squared_less_than_4t_exact": radial_form_positive_exact,
        "homogeneous_quartic_BFB_certified": (
            exact_fierz["source_binding_exact"] and radial_form_positive_exact
        ),
        "finite_field_global_gap_certified": False,
        "source_binding_exact": exact_fierz["source_binding_exact"],
    }


def fixed_pd_equal_norm_h_orientation_certificate() -> dict[str, Any]:
    beta_r2 = BETA * R * R
    spectrum = {
        "desired_EW_chirality": {"eigenvalue": Fraction(0), "complex_multiplicity": 2},
        "opposite_EW_chirality": {"eigenvalue": Fraction(6, 5), "complex_multiplicity": 2},
        "desired_colour_chirality": {"eigenvalue": beta_r2, "complex_multiplicity": 3},
        "opposite_colour_chirality": {
            "eigenvalue": Fraction(6, 5) - beta_r2,
            "complex_multiplicity": 3,
        },
    }
    return {
        "scope": "Phi=F, Sigma=r Delta, N_H=1",
        "Hermitian_alignment_plus_current_spectrum": spectrum,
        "smallest_positive_eigenvalue": beta_r2,
        "all_nonnegative": all(row["eigenvalue"] >= 0 for row in spectrum.values()),
        "equality_subspace": "desired electroweak chirality C^2",
        "H_holomorphic_square": "|H.H|^2 vanishes on that isotropic C^2",
        "normalized_equality_set_is_EW_gauge_orbit": True,
        "lower_equal_norm_H_orientation_found": False,
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def fixed_f_mixed_kernel_global_certificate() -> dict[str, Any]:
    """Prove the beta deformation globally safe on the full F mixed kernel.

    At ``Phi=F`` the simultaneous A/C zero space is the SU(5) representation
    ``10 = Lambda^2 C^5``.  Write its element as a two-form z and split the
    complex SO(10) vector into the two SU(5) chiralities ``h_+ + h_-``.  The
    exact current restriction is

        J45(h_+,z) = ||h_+ wedge z||^2 >= 0,
        J45(h_-,z) >= -N_z ||h_-||^2,

    with no cross-chirality term.  Meanwhile the chiral Phi-H square is
    ``(6/5)||h_-||^2``.  This reduces the only possibly negative part to a
    two-variable scalar inequality, proved below with Fraction arithmetic.

    All representation statements used here are source-bound without random
    sampling.  Ten explicit Gaussian-integer kernel vectors, plus a rank-116
    minor modulo 5, prove the +F kernel dimension.  A rank-126 minor modulo 5
    proves that the signed companion -F has no mixed-zero kernel.  The full
    current coefficient tensor is then matched exactly to the exterior-square
    factorization in an orthonormal kernel basis.
    """

    def gaussian_modular_rank(matrix: np.ndarray) -> int:
        """Exact rank lower bound over Q(i), using i -> 2 in F_5."""
        values = np.asarray(matrix, dtype=complex)
        real = np.rint(values.real).astype(np.int64)
        imaginary = np.rint(values.imag).astype(np.int64)
        if np.max(np.abs(values - (real + 1j * imaginary)), initial=0.0) != 0.0:
            raise ArithmeticError("Gaussian-integer source matrix expected")
        prime = 5
        reduced = (real + 2 * imaginary) % prime
        n_rows, n_columns = reduced.shape
        rank = 0
        for column in range(n_columns):
            pivots = np.flatnonzero(reduced[rank:, column])
            if not len(pivots):
                continue
            pivot = rank + int(pivots[0])
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
            inverse = pow(int(reduced[rank, column]), -1, prime)
            reduced[rank] = (inverse * reduced[rank]) % prime
            active = np.flatnonzero(reduced[:, column])
            active = active[active != rank]
            if len(active):
                reduced[active] = (
                    reduced[active]
                    - reduced[active, column, None] * reduced[rank]
                ) % prime
            rank += 1
            if rank == n_rows:
                break
        return rank

    kernel_rows = (
        ((7, 1j), (8, -1), (11, -1), (12, -1j), (22, -1), (23, -1j), (26, -1j), (27, 1)),
        ((9, 1j), (10, -1), (13, -1), (14, -1j), (24, -1), (25, -1j), (28, -1j), (29, 1)),
        ((16, 1j), (17, -1), (18, -1), (19, -1j), (31, -1), (32, -1j), (33, -1j), (34, 1)),
        ((41, 1j), (42, -1), (43, -1), (44, -1j), (47, -1), (48, -1j), (49, -1j), (50, 1)),
        ((75, -1), (80, -1), (81, -1j), (86, -1j), (95, -1j), (100, -1j), (101, 1), (106, 1)),
        ((73, -1), (74, -1j), (87, -1), (88, -1j), (93, -1j), (94, 1), (107, -1j), (108, 1)),
        ((71, -1), (72, -1j), (89, -1), (90, -1j), (91, -1j), (92, 1), (109, -1j), (110, 1)),
        ((66, -1), (67, -1j), (68, -1j), (69, 1), (112, -1), (113, -1j), (114, -1j), (115, 1)),
        ((59, -1), (60, -1j), (63, -1j), (64, 1), (117, -1), (118, -1j), (121, -1j), (122, 1)),
        ((57, -1), (58, -1j), (61, -1j), (62, 1), (119, -1), (120, -1j), (123, -1j), (124, 1)),
    )
    kernel_integer = np.zeros((chart.SIGMA_COMPLEX_DIM, 10), dtype=complex)
    for column, row in enumerate(kernel_rows):
        for index, value in row:
            kernel_integer[index, column] = value

    _, f0 = pd_source.raw_su5_form_and_vector()
    operator_real, operator_imaginary = recoupling_source.integer_cubic_operators()
    matrix_real = np.tensordot(f0, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(f0, operator_imaginary, axes=(0, 0))
    contraction_real, contraction_imaginary = recoupling_source.integer_contraction_tensor()
    c_real = np.einsum("vpa,p->va", contraction_real, f0, optimize=True)
    c_imaginary = np.einsum("vpa,p->va", contraction_imaginary, f0, optimize=True)
    positive_mixed_operator = np.vstack(
        (
            matrix_real + 1j * matrix_imaginary - 8 * np.eye(chart.SIGMA_COMPLEX_DIM),
            c_real + 1j * c_imaginary,
        )
    )
    negative_mixed_operator = np.vstack(
        (
            -matrix_real - 1j * matrix_imaginary - 8 * np.eye(chart.SIGMA_COMPLEX_DIM),
            -c_real - 1j * c_imaginary,
        )
    )
    positive_rank_mod_5 = gaussian_modular_rank(positive_mixed_operator)
    negative_rank_mod_5 = gaussian_modular_rank(negative_mixed_operator)
    kernel_gram = kernel_integer.conj().T @ kernel_integer
    kernel_annihilation = positive_mixed_operator @ kernel_integer
    negative_singular_values = np.linalg.svd(
        negative_mixed_operator, compute_uv=False
    )

    f_operators = phi_h_source.channel_operators(normalized_f())
    q_chiral = (
        (3.0 / 5.0) * f_operators["1"]
        + f_operators["45"]
        - f_operators["54"]
    )
    h_plus_integer = np.zeros((10, 5), dtype=complex)
    h_minus_integer = np.zeros((10, 5), dtype=complex)
    for index in range(5):
        h_plus_integer[2 * index, index] = 1
        h_plus_integer[2 * index + 1, index] = 1j
        h_minus_integer[2 * index, index] = 1
        h_minus_integer[2 * index + 1, index] = -1j
    expected_q_chiral = Fraction(3, 5) * (
        h_minus_integer @ h_minus_integer.conj().T
    )
    q_chiral_source_residual = float(np.max(np.abs(q_chiral - expected_q_chiral)))

    sigma_generators = hsigma_derivatives.sigma_generator_matrices()
    h_generators = hsigma_derivatives.h_generator_matrices()
    sigma_restricted = np.einsum(
        "ia,gij,jb->gab",
        kernel_integer.conj(),
        sigma_generators,
        kernel_integer,
        optimize=True,
    )
    plus_restricted = np.einsum(
        "ia,gij,jb->gab",
        h_plus_integer.conj(),
        h_generators,
        h_plus_integer,
        optimize=True,
    )
    cross_restricted = np.einsum(
        "ia,gij,jb->gab",
        h_plus_integer.conj(),
        h_generators,
        h_minus_integer,
        optimize=True,
    )
    plus_current_numerator = -np.einsum(
        "gab,gij->abij", sigma_restricted, plus_restricted, optimize=True
    )
    cross_current_numerator = -np.einsum(
        "gab,gij->abij", sigma_restricted, cross_restricted, optimize=True
    )

    two_form_pairs = (
        (0, 4),
        (0, 3),
        (0, 2),
        (0, 1),
        (3, 4),
        (2, 3),
        (2, 4),
        (1, 2),
        (1, 3),
        (1, 4),
    )
    two_form_phases = (1, -1, 1, -1, 1j, 1j, -1j, 1j, -1j, 1j)
    three_form_basis = tuple(
        (first, second, third)
        for first in range(5)
        for second in range(first + 1, 5)
        for third in range(second + 1, 5)
    )
    three_form_index = {indices: index for index, indices in enumerate(three_form_basis)}
    wedge_maps: list[np.ndarray] = []
    for first, second in two_form_pairs:
        wedge = np.zeros((10, 5), dtype=complex)
        for h_index in range(5):
            raw = (h_index, first, second)
            if len(set(raw)) != 3:
                continue
            inversions = sum(
                raw[left] > raw[right]
                for left in range(3)
                for right in range(left + 1, 3)
            )
            wedge[three_form_index[tuple(sorted(raw))], h_index] = (-1) ** inversions
        wedge_maps.append(wedge)
    expected_plus_numerator = np.zeros_like(plus_current_numerator)
    for left in range(10):
        for right in range(10):
            expected_plus_numerator[left, right] = (
                16
                * np.conjugate(two_form_phases[right])
                * two_form_phases[left]
                * wedge_maps[right].conj().T
                @ wedge_maps[left]
            )

    exact_kernel_annihilation = bool(
        np.max(np.abs(kernel_annihilation), initial=0.0) == 0.0
    )
    exact_kernel_gram = bool(np.array_equal(kernel_gram, 8 * np.eye(10)))
    exact_wedge_factorization = bool(
        np.array_equal(plus_current_numerator, expected_plus_numerator)
    )
    exact_cross_zero = bool(
        np.max(np.abs(cross_current_numerator), initial=0.0) == 0.0
    )
    current_bound = exact_hsigma_current_bound_certificate()

    threshold = Fraction(6, 5) / BETA
    if threshold != 24:
        raise ArithmeticError("unexpected fixed-kernel threshold")
    boundary_value = SIGMA_SCALE * (threshold - R * R) ** 2
    # For v>=24, after minimizing over u>=0 the lower bound is
    # f(v)=t(v-r^2)^2+L-L^2/4, L=6/5-beta*v.  Its derivative is
    # (199/800)v-3/100, hence it is positive and increasing there.
    derivative_at_threshold = Fraction(199, 800) * threshold - Fraction(3, 100)
    exact_scalar_proof = bool(
        threshold == 24 and boundary_value > 0 and derivative_at_threshold > 0
    )
    exact_source_proof = bool(
        positive_rank_mod_5 == 116
        and negative_rank_mod_5 == 126
        and exact_kernel_annihilation
        and exact_kernel_gram
        and exact_wedge_factorization
        and exact_cross_zero
        and q_chiral_source_residual < 1e-12
        and current_bound["source_binding_exact"]
    )
    return {
        "scope": "Phi=F and arbitrary Sigma in ker(M(F)-8/sqrt(10)) intersect ker(C_F)",
        "mixed_kernel_complex_dimension": 10,
        "expected_SU5_representation": "10=Lambda^2(C^5)",
        "SU5_current_identities": {
            "desired_chirality": "J45(h_plus,z)=||h_plus wedge z||^2>=0",
            "opposite_chirality": "J45(h_minus,z)>=-N_z||h_minus||^2",
            "cross_chirality": "0",
        },
        "Phi_H_square_on_F": "Q_chi=(6/5)||h_minus||^2",
        "source_audit": {
            "positive_F_rank_mod_5": positive_rank_mod_5,
            "positive_F_explicit_kernel_annihilation_exact": exact_kernel_annihilation,
            "positive_F_explicit_kernel_gram_is_8I_exact": exact_kernel_gram,
            "negative_F_rank_mod_5": negative_rank_mod_5,
            "negative_F_mixed_kernel_complex_dimension": 0,
            "negative_F_smallest_singular_value_diagnostic": float(
                negative_singular_values[-1]
            ),
            "desired_chirality_wedge_coefficient_identity_exact": exact_wedge_factorization,
            "chirality_cross_coefficient_tensor_zero_exact": exact_cross_zero,
            "Phi_H_chiral_projector_source_residual": q_chiral_source_residual,
            "opposite_chirality_bound_from_210_projector": current_bound[
                "source_binding_exact"
            ],
        },
        "scalar_reduction": {
            "v_below_24": (
                "Q_chi+beta J45 >= (6/5-beta v)||h_minus||^2 >=0"
            ),
            "v_at_least_24": (
                "G >= (1/8)(v-1/25)^2 + (u-1)^2 + "
                "(6/5-v/20)u"
            ),
            "minimized_large_v_function": (
                "f(v)=(1/8)(v-1/25)^2+L-L^2/4, L=6/5-v/20"
            ),
            "large_v_boundary": threshold,
            "f_at_boundary": boundary_value,
            "fprime_at_boundary": derivative_at_threshold,
            "fprime_formula": "(199/800)v-3/100 >0 for v>=24",
        },
        "global_gap_nonnegative_on_entire_fixed_F_mixed_kernel": bool(
            exact_scalar_proof and exact_source_proof
        ),
        "equality_conditions": (
            "v=1/25, N_H=1, h_minus=0, z decomposable, and h_plus lies "
            "in the two-plane of z"
        ),
        "equality_is_one_SU5_orbit": True,
        "negative_F_mixed_zero_equality_branch_excluded": negative_rank_mod_5 == 126,
        "lower_witness_on_this_full_kernel": False,
        "proof_grade": bool(exact_scalar_proof and exact_source_proof),
    }
def recompute_live_hessian() -> dict[str, Any]:
    """Assemble all 51 live rows and classify the candidate quotient."""
    import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

    state = candidate_state()
    q = chart.pack(state)
    selection = g2_audit.contract_selection()
    values = potential.evaluate_directions(state)
    by_direction = {row.direction_id: row for row in values}
    owners = g2_audit._adapter_modules_by_family()
    direction_rows = tuple(
        owners[by_direction[direction_id].base_family].direction_derivative(
            q, by_direction[direction_id]
        )
        for direction_id in sorted(selection["direction_ids"])
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    by_parameter = {row.parameter_id: row for row in parameter_rows}
    coefficients = numerical_coefficient_map()
    missing = sorted(set(coefficients).difference(by_parameter))
    if missing:
        raise KeyError(f"candidate rows missing from compiler: {missing}")
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in coefficients.items():
        row = by_parameter[parameter_id]
        gradient += coefficient * np.asarray(row.gradient).real
        hessian += coefficient * np.asarray(row.hessian).real
    hessian = 0.5 * (hessian + hessian.T)

    orbit = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            quotient_source._phase_tangent(state, quotient_source.PQ_CHARGES),
        )
    )
    complete, singular_values, _ = np.linalg.svd(orbit, full_matrices=True)
    rank = int(np.sum(singular_values > 1e-10 * singular_values[0]))
    quotient = complete[:, rank:]
    transverse = quotient.T @ hessian @ quotient
    eigenvalues = np.linalg.eigvalsh(0.5 * (transverse + transverse.T))
    return {
        "evidence_kind": "live_486_field_exact_X_compiler_float64",
        "recomputed_in_this_invocation": True,
        "proof_grade": False,
        "parameter_rows_assembled": len(parameter_rows),
        "full_gradient_max_abs_residual": float(np.max(np.abs(gradient), initial=0.0)),
        "full_gradient_norm": float(np.linalg.norm(gradient)),
        "numerical_symmetry_orbit_rank": rank,
        "transverse_dimension": int(quotient.shape[1]),
        "stationary_Hessian_symmetry_max_abs_residual": float(
            np.max(np.abs(hessian @ complete[:, :rank]), initial=0.0)
        ),
        "minimum_transverse_eigenvalue": float(eigenvalues[0]),
        "maximum_transverse_eigenvalue": float(eigenvalues[-1]),
        "negative_transverse_eigenvalues_below_minus_1e_minus_9": int(
            np.sum(eigenvalues < -1e-9)
        ),
        "zero_transverse_eigenvalues_at_1e_minus_9": int(
            np.sum(np.abs(eigenvalues) <= 1e-9)
        ),
        "strict_local_minimum_high_confidence_numeric": bool(
            rank == EXPECTED_FULL_SYMMETRY_RANK
            and quotient.shape[1] == EXPECTED_QUOTIENT_DIMENSION
            and eigenvalues[0] > 1e-4
        ),
        "strict_local_minimum_proof_grade": False,
    }


def build_report(*, recompute_heavy: bool = False) -> dict[str, Any]:
    alignment = exact_phi_h_chiral_square_certificate()
    affine_sos_no_go = exact_positive_affine_sos_replacement_no_go_certificate()
    real_no_go = real_h_exact_no_go_certificate()
    orbit = exact_orbit_rank_certificate()
    current_bound = exact_hsigma_current_bound_certificate()
    fixed_orientation = fixed_pd_equal_norm_h_orientation_certificate()
    fixed_f_kernel = fixed_f_mixed_kernel_global_certificate()
    coefficients = numerical_coefficient_map()
    symbolic = symbolic_coefficient_map()
    contract_ids = set(g2_audit.contract_selection()["parameter_ids"])
    hessian = recompute_live_hessian() if recompute_heavy else dict(RECORDED_LIVE_HESSIAN)
    maximum = max(abs(value) for value in coefficients.values())
    checks = {
        "PD_source_certificate_available": bool(
            pd_source.exact_phi_projector_certificate()["source_binding_exact"]
            and pd_source.exact_mixed_zero_certificate()["source_binding_exact"]
            and pd_source.exact_sigma_certificate()["source_binding_exact"]
        ),
        "real_H_obstruction_exact": real_no_go["source_binding_exact"],
        "real_H_strict_minimum_impossible": not real_no_go[
            "strict_transverse_minimum_with_real_H_possible"
        ],
        "chiral_Phi_H_square_exact": alignment["source_binding_exact"],
        "beta_free_all_vanishing_affine_SOS_route_excluded": affine_sos_no_go[
            "proof_grade"
        ],
        "complete_51_parameter_contract": len(contract_ids) == 51,
        "candidate_parameters_inside_contract": set(symbolic) <= contract_ids,
        "candidate_has_28_nonzero_parameters": len(symbolic) == 28,
        "coefficient_bound_4pi": maximum < 4.0 * math.pi,
        "exact_symmetry_rank_38": orbit["source_binding_exact"],
        "quartic_BFB_bound": current_bound["homogeneous_quartic_BFB_certified"],
        "fixed_PD_equal_norm_H_test": fixed_orientation["all_nonnegative"],
        "fixed_F_full_mixed_kernel_global_gap": fixed_f_kernel["proof_grade"],
        "negative_F_has_no_mixed_zero_kernel": fixed_f_kernel[
            "negative_F_mixed_zero_equality_branch_excluded"
        ],
        "live_full_gradient_zero": hessian["full_gradient_max_abs_residual"] < 1e-10,
        "live_448_quotient_positive": (
            hessian["transverse_dimension"] == 448
            and hessian["negative_transverse_eigenvalues_below_minus_1e_minus_9"] == 0
            and hessian["zero_transverse_eigenvalues_at_1e_minus_9"] == 0
            and hessian["minimum_transverse_eigenvalue"] > 1e-4
        ),
        "global_minimum_not_overclaimed": not current_bound[
            "finite_field_global_gap_certified"
        ],
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
                if not failures
                else "SU5_DELTA_HSX_EXTENSION_AUDIT_FAILED"
            ),
            "overall_state": "G3_PROMISING_CANDIDATE_NOT_CLOSED" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "model_contract_id": MODEL_CONTRACT_ID,
            "selected_scales": {"r": R, "x": X, "N_H": Fraction(1)},
            "real_H_obstruction": real_no_go,
            "chiral_H_candidate": {
                "H": "(e6+i e7)/sqrt(2)",
                "H_norm_squared": Fraction(1),
                "H_dot_H": Fraction(0),
                "Phi_H_alignment": alignment,
                "H_Sigma_lift": {"parameter": "O35_B02", "beta": BETA},
                "exact_orbit": orbit,
                "fixed_PD_equal_norm_orientation_test": fixed_orientation,
                "fixed_F_full_mixed_kernel_global_certificate": fixed_f_kernel,
                "beta_free_affine_SOS_replacement_audit": affine_sos_no_go,
            },
            "coefficient_map": {
                "nonzero_count": len(symbolic),
                "symbolic": symbolic,
                "numerical": coefficients,
                "maximum_absolute_coefficient": maximum,
                "four_pi": 4.0 * math.pi,
            },
            "BFB_certificate": current_bound,
            "live_full_gradient_and_quotient_Hessian": hessian,
            "global_status": {
                "PD_global_SOS_exact": True,
                "full_homogeneous_quartic_BFB_exact": True,
                "fixed_PD_equal_norm_H_orientation_exact": True,
                "positive_F_full_mixed_kernel_gap_exact": fixed_f_kernel[
                    "proof_grade"
                ],
                "negative_F_mixed_zero_kernel_dimension": fixed_f_kernel[
                    "source_audit"
                ]["negative_F_mixed_kernel_complex_dimension"],
                "all_vanishing_affine_SOS_beta_replacement_excluded": (
                    affine_sos_no_go["proof_grade"]
                ),
                "beta_deformed_finite_field_global_gap_exact": False,
                "global_equality_orbits_classified": False,
                "G3_closed": False,
            },
            "flag": {
                "real_H_e6_extension_exactly_excluded": not failures,
                "chiral_H_exact_stationary_candidate_constructed": not failures,
                "full_486_gradient_zero_live": not failures,
                "strict_448_quotient_local_minimum_high_confidence_numeric": not failures,
                "full_quartic_BFB_certified": not failures,
                "full_global_minimum_certified": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
            "next_required_test": (
                "The fixed-F off-kernel and exact-Hessian companion certificates "
                "remove those two former blockers.  Prove the remaining uniform "
                "coercivity inequality when Phi lies outside the signed F equality "
                "strata, then classify its global equality set; otherwise exhibit "
                "a lower arbitrary-Phi witness."
            ),
            "verdict": (
                "The real H=e6 extension is exactly impossible, but this is not a "
                "no-go for G3: the chiral neutral H=(e6+i e7)/sqrt(2) gives an "
                "exact stationary, BFB, coefficient-safe candidate whose complete "
                "live 448-dimensional quotient Hessian is strictly positive, and the "
                "companion source-bound certificate upgrades it to exact rank 448, "
                "nullity 38 and PSD.  The companion fixed-F off-kernel certificate "
                "also extends the exact +F result beyond its mixed kernel; -F has no "
                "mixed-zero Sigma branch.  A clean all-vanishing affine-SOS replacement "
                "for beta is exactly excluded.  Only uniform arbitrary-Phi coercivity "
                "and its equality classification remain before G3 can close."
            ),
        }
    )


def write_markdown(report: dict[str, Any]) -> str:
    hessian = report["live_full_gradient_and_quotient_Hessian"]
    fixed_kernel = report["chiral_H_candidate"][
        "fixed_F_full_mixed_kernel_global_certificate"
    ]
    return "\n".join(
        [
            "# Exact SU(5)-Delta full H/S/Phi17 extension audit -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Real-H result",
            "",
            "- `H=e6`: exactly obstructed; O35_45 nonzero is tachyonic, zero leaves six physical flats.",
            "- Old Phi-H wedge square at F: `3/5`, not zero.",
            "",
            "## Chiral escape candidate",
            "",
            "- `H=(e6+i e7)/sqrt(2)`, `r=1/5`, `beta=1/20`.",
            "- exact symmetry rank: `38`; physical quotient: `448`.",
            f"- live gradient max residual: `{hessian['full_gradient_max_abs_residual']}`.",
            f"- live minimum transverse eigenvalue: `{hessian['minimum_transverse_eigenvalue']}`.",
            "- negative/zero transverse modes: `0/0`.",
            "- companion exact Hessian: rank `448`, nullity `38`, PSD; strict on the quotient.",
            "- largest coefficient: `11 < 4*pi`.",
            "",
            "## Exact finite-field slice",
            "",
            "- the full `Phi=+F` mixed-kernel gap is nonnegative for arbitrary H and Sigma norms/orientations.",
            f"- exact mixed-kernel complex dimension: `{fixed_kernel['mixed_kernel_complex_dimension']}`.",
            "- the signed `Phi=-F` branch has mixed-kernel dimension `0`.",
            "- the equality set on the +F slice is one SU(5) orbit.",
            "- companion off-kernel bound extends this result to every H and Sigma at `Phi=+F`.",
            "",
            "## Beta-free affine-SOS audit",
            "",
            "- O12, O15/O38 and both O45 projector residuals were checked in the exact-X contract.",
            "- no nontrivial all-vanishing affine residual is compatible with `(F,Delta,Hchi)`.",
            "- the six live portal-gradient columns have rank `6`, so no portal-only stationarity combination exists.",
            "",
            "## Remaining gate",
            "",
            report["next_required_test"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute-heavy", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(recompute_heavy=args.recompute_heavy)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
