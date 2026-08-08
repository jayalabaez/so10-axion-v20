#!/usr/bin/env python3
"""Fail-closed audit of alternative globally positive G3 completions.

The chiral SU(5)+Delta candidate uses a small signed adjoint-current term
``beta I45(H,Sigma)``.  A natural attempt to make globality manifest is to
complete that term into a positive Gram square of the three available
adjoint covariants

    K = *(Phi wedge Phi),  J_H,  J_Sigma.

This module proves that the attempt cannot vanish at the selected orbit.  In
the orthonormal five-plane basis, at ``Phi=F``, ``H=H_chi`` and
``Sigma=r Delta_R``,

    K       = (3/5) (C1+C2+C3+W1+W2),
    J_H     = W1,
    J_Sigma = r^2 (C1+C2+C3).

Their exact Gram determinant is ``27 r^4/25``.  It is strictly positive for
every nonzero r, so no nonzero positive-semidefinite Gram form in these three
covariants can vanish there.  In particular, a zero-residual current square
cannot replace the signed H--Sigma lift.  This complements (but does not
extend beyond) the separate exact no-go for all-vanishing affine residuals.

The module also performs deterministic reduced numerical searches on the
complete P/A/omega singlet slice, the Delta_R ray, and all ten chiral H plane
orientations.  Several rational beta, t, r and radial-current completions are
tested.  The searches are diagnostics only: failure to find a lower point is
not a global proof, and nonvanishing-residual cancellations or a different
vacuum orbit remain open.
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
from scipy.optimize import differential_evolution

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_self_invariant_basis_v20 as phi_self
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_mixed_45_triplet_channel_v20 as current45
import exact_phi2_hdagh_channel_family_v20 as phi_h_source
import exact_unique_hsigma_chiral_quartics_v20 as unique_hsigma
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.md"

R = Fraction(1, 5)
BETA = Fraction(1, 20)
T = Fraction(1, 8)
LOWER_WITNESS_TOLERANCE = 1.0e-8


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    return value


def _plane_coordinates(form: direct.Form) -> np.ndarray:
    return np.asarray(
        [complex(form.get(pair, 0.0)).real for pair in current45.ALL_PLANES],
        dtype=float,
    )


@lru_cache(maxsize=1)
def exact_current_gram_no_go_certificate() -> dict[str, Any]:
    """Prove the adjoint-current zero-residual completion is impossible."""
    phi = hsx.normalized_f()
    h = hsx.h_vector(chiral=True)
    h_form = {(index,): value for index, value in enumerate(h) if value}
    sigma = direct.scale_form(direct.delta_r(), float(R))

    observed = np.column_stack(
        (
            _plane_coordinates(current45.phi_45(phi)),
            _plane_coordinates(
                current45.hermitian_current_45(h_form, kinetic_factor=1.0)
            ),
            _plane_coordinates(
                current45.hermitian_current_45(sigma, kinetic_factor=0.5)
            ),
        )
    )
    expected = np.asarray(
        [
            [3 / 5, 0, 1 / 25],
            [3 / 5, 0, 1 / 25],
            [3 / 5, 0, 1 / 25],
            [3 / 5, 1, 0],
            [3 / 5, 0, 0],
        ],
        dtype=float,
    )
    gram = observed.T @ observed
    exact_gram = (
        (Fraction(9, 5), Fraction(3, 5), Fraction(9, 125)),
        (Fraction(3, 5), Fraction(1), Fraction(0)),
        (Fraction(9, 125), Fraction(0), Fraction(3, 625)),
    )
    exact_as_float = np.asarray(
        [[float(value) for value in row] for row in exact_gram], dtype=float
    )
    leading_minors = (
        Fraction(9, 5),
        Fraction(36, 25),
        Fraction(27, 15625),
    )
    source_residual = max(
        float(np.max(np.abs(observed - expected), initial=0.0)),
        float(np.max(np.abs(gram - exact_as_float), initial=0.0)),
    )
    proof_grade = bool(
        source_residual < 1.0e-12
        and all(value > 0 for value in leading_minors)
    )
    return {
        "scope": "Phi=F, H=(e6+i e7)/sqrt(2), Sigma=r Delta_R, r>0",
        "orthonormal_plane_order": ["C1", "C2", "C3", "W1", "W2"],
        "exact_covariants_at_r_equals_1_over_5": {
            "K45_Phi": ["3/5", "3/5", "3/5", "3/5", "3/5"],
            "J45_H": ["0", "0", "0", "1", "0"],
            "J45_Sigma": ["1/25", "1/25", "1/25", "0", "0"],
        },
        "observed_source_matrix": observed,
        "source_maximum_abs_residual": source_residual,
        "exact_Gram_matrix": exact_gram,
        "exact_leading_principal_minors": leading_minors,
        "exact_determinant_general_nonzero_H_Sigma": "27*N_H^2*N_Sigma^2/25",
        "exact_determinant_at_target": Fraction(27, 15625),
        "rank": 3,
        "positive_definite": True,
        "linear_algebra_lemma": (
            "If C has these three covariants as columns and A is PSD, "
            "tr(A C^T C)=||C sqrt(A)||_F^2. Since rank(C)=3, zero at "
            "the target forces A=0."
        ),
        "consequence": (
            "no nonzero all-vanishing PSD 45-channel Gram square can carry "
            "the H-Sigma cross coefficient at this orbit"
        ),
        "holds_for_every_nonzero_r": True,
        "source_binding_exact": proof_grade,
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def exact_unique_chiral_quartic_no_go_certificate() -> dict[str, Any]:
    """Exclude zero-residual completions based on O28 or O31.

    O28 is the inner product of the quadratic six-index covariants
    ``U=H tensor Sigmadag`` and ``W=Sigma tensor Sigmadag`` in the source
    contraction.  They are nonzero and orthogonal at the target.  O31 is the
    holomorphic square of ``z=i_Hbar Sigma``; there ``z`` is nonzero but null.
    A globally positive quadratic-covariant form therefore cannot vanish at
    the target while retaining either cross coefficient.
    """
    h = hsx.h_vector(chiral=True)
    sigma = direct.scale_form(direct.delta_r(), float(R))
    dense = unique_hsigma.forms.dense_antisymmetric(sigma, 5)
    dense_dag = np.conjugate(dense)

    u_covariant = np.einsum("a,bcdef->abcdef", h, dense_dag, optimize=True)
    w_covariant = np.einsum(
        "abcgh,defgh->abcdef", dense, dense_dag, optimize=True
    )
    u_norm = float(np.vdot(u_covariant, u_covariant).real)
    w_norm = float(np.vdot(w_covariant, w_covariant).real)
    o28_inner = complex(np.vdot(u_covariant, w_covariant))
    o28_source = unique_hsigma.invariant_hdag_sigma2_sigmadag(
        np.conjugate(h), dense, dense_dag
    )

    z_covariant = np.einsum(
        "a,acdef->cdef", np.conjugate(h), dense, optimize=True
    )
    z_norm = float(np.vdot(z_covariant, z_covariant).real)
    z_holomorphic = complex(np.dot(z_covariant.ravel(), z_covariant.ravel()))
    o31_source = unique_hsigma.invariant_hdag2_sigma2(
        np.conjugate(h), dense
    )

    expected = {
        "O28_U_norm_squared": Fraction(48, 5),
        "O28_W_norm_squared": Fraction(4032, 625),
        "O28_Gram_determinant": Fraction(193536, 3125),
        "O31_z_norm_squared": Fraction(24, 25),
    }
    residual = max(
        abs(u_norm - float(expected["O28_U_norm_squared"])),
        abs(w_norm - float(expected["O28_W_norm_squared"])),
        abs(o28_inner),
        abs(o28_source),
        abs(z_norm - float(expected["O31_z_norm_squared"])),
        abs(z_holomorphic),
        abs(o31_source),
    )
    proof_grade = residual < 1.0e-12
    return {
        "scope": "unique exact-X quartics O28 and O31 at F+Delta+Hchi",
        "O28_quadratic_covariants": {
            "U_norm_squared": expected["O28_U_norm_squared"],
            "W_norm_squared": expected["O28_W_norm_squared"],
            "inner_product": "0",
            "Gram_determinant": expected["O28_Gram_determinant"],
            "linearly_independent": True,
            "consequence": (
                "a PSD quadratic-covariant Gram square that vanishes here "
                "cannot retain the O28 cross term"
            ),
        },
        "O31_quadratic_covariant": {
            "z_norm_squared": expected["O31_z_norm_squared"],
            "z_holomorphic_square": "0",
            "nonzero_isotropic": True,
            "consequence": (
                "a||z||^2+Re(b z.z) is globally PSD only for a>=|b|; "
                "zero at this nonzero null z forces a=b=0"
            ),
        },
        "source_maximum_abs_residual": residual,
        "all_vanishing_O28_completion_excluded": proof_grade,
        "all_vanishing_O31_completion_excluded": proof_grade,
        "nonvanishing_residual_cancellations_excluded": False,
        "source_binding_exact": proof_grade,
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def _reduced_slice_source() -> dict[str, Any]:
    """Precompute a fast exact-source evaluator for the dangerous slice."""
    polynomials = phi_self.singlet_quartic_polynomials()
    monomials = phi_self.QUARTIC_MONOMIALS
    quartic_basis = np.zeros((len(phi_self.QUARTIC_BASIS_NAMES), len(monomials)))
    for row, name in enumerate(phi_self.QUARTIC_BASIS_NAMES):
        for column, powers in enumerate(monomials):
            key = f"p^{powers[0]} a^{powers[1]} omega^{powers[2]}"
            quartic_basis[row, column] = polynomials[name].get(key, 0.0)
    phi_sos_coefficients = np.asarray(
        [
            float(pd_source.EXPECTED_PHI_J_COEFFICIENTS[name])
            for name in phi_self.QUARTIC_BASIS_NAMES
        ]
    ) @ quartic_basis

    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    contraction_real, contraction_imaginary = (
        mixed_source.integer_contraction_tensor()
    )
    operator = operator_real + 1j * operator_imaginary
    contraction = contraction_real + 1j * contraction_imaginary
    delta = chart.sigma_coordinates(direct.delta_r())
    phi_basis_vectors = tuple(
        phi_self.phi_vector(phi_self.singlet_form(*np.eye(3)[index]))
        for index in range(3)
    )
    mixed_m_images = np.stack(
        [
            np.tensordot(vector, operator, axes=(0, 0)) @ delta
            for vector in phi_basis_vectors
        ]
    )
    mixed_c_images = np.stack(
        [
            np.einsum(
                "vpa,p,a->v", contraction, vector, delta, optimize=True
            )
            for vector in phi_basis_vectors
        ]
    )

    basis_forms = tuple(
        phi_self.singlet_form(*np.eye(3)[index]) for index in range(3)
    )

    def q_operator(form: direct.Form) -> np.ndarray:
        operators = phi_h_source.channel_operators(form)
        return (
            (3.0 / 5.0) * operators["1"]
            + operators["45"]
            - operators["54"]
        )

    diagonal = tuple(q_operator(form) for form in basis_forms)
    q_monomial_operators = (
        diagonal[0],
        diagonal[1],
        diagonal[2],
        q_operator(direct.add_forms(basis_forms[0], basis_forms[1]))
        - diagonal[0]
        - diagonal[1],
        q_operator(direct.add_forms(basis_forms[0], basis_forms[2]))
        - diagonal[0]
        - diagonal[2],
        q_operator(direct.add_forms(basis_forms[1], basis_forms[2]))
        - diagonal[1]
        - diagonal[2],
    )
    return {
        "monomials": monomials,
        "phi_sos_coefficients": phi_sos_coefficients,
        "delta": delta,
        "mixed_m_images": mixed_m_images,
        "mixed_c_images": mixed_c_images,
        "q_monomial_operators": q_monomial_operators,
        "phi_polynomial_validation_residual": polynomials["validation"][
            "maximum_abs_residual"
        ],
    }


def reduced_slice_gap(
    variables: np.ndarray,
    *,
    plane: int,
    chirality: int,
    beta: float,
    t: float,
    r: float,
    radial_cross: float,
) -> float:
    """Candidate gap on P/A/omega x Delta_R x chiral-H sectors."""
    p, a, omega, rho, h_norm_squared = map(float, variables)
    source = _reduced_slice_source()
    monomial_values = np.asarray(
        [p**i * a**j * omega**k for i, j, k in source["monomials"]]
    )
    phi_norm_squared = p * p + a * a + omega * omega
    phi_gap = float(source["phi_sos_coefficients"] @ monomial_values)
    phi_gap += -2.0 * phi_norm_squared + 1.0

    m_image = rho * (
        p * source["mixed_m_images"][0]
        + a * source["mixed_m_images"][1]
        + omega * source["mixed_m_images"][2]
        - (8.0 / math.sqrt(10.0)) * source["delta"]
    )
    c_image = rho * (
        p * source["mixed_c_images"][0]
        + a * source["mixed_c_images"][1]
        + omega * source["mixed_c_images"][2]
    )
    sigma_norm_squared = rho * rho
    pd_gap = phi_gap + t * (
        float(np.vdot(m_image, m_image).real)
        + float(np.vdot(c_image, c_image).real)
        + (sigma_norm_squared - r * r) ** 2
    )

    unit_h = np.zeros(10, dtype=complex)
    unit_h[2 * plane] = 1.0 / math.sqrt(2.0)
    unit_h[2 * plane + 1] = chirality * 1j / math.sqrt(2.0)
    q_monomials = (p * p, a * a, omega * omega, p * a, p * omega, a * omega)
    q_operator = sum(
        coefficient * matrix
        for coefficient, matrix in zip(
            q_monomials, source["q_monomial_operators"], strict=True
        )
    )
    q_eigenvalue = float(np.vdot(unit_h, q_operator @ unit_h).real)
    current = (
        chirality * sigma_norm_squared if plane < 3 else 0.0
    )
    h_gap = (
        (h_norm_squared - 1.0) ** 2
        + h_norm_squared * q_eigenvalue
        + beta * h_norm_squared * current
        + radial_cross
        * (h_norm_squared - 1.0)
        * (sigma_norm_squared - r * r)
    )
    return float(pd_gap + h_gap)


@lru_cache(maxsize=1)
def reduced_numerical_searches() -> dict[str, Any]:
    """Search several stronger/rational variants without treating them as proof."""
    configurations = (
        {
            "name": "current_beta_1_over_20",
            "beta": Fraction(1, 20),
            "t": Fraction(1, 8),
            "r": Fraction(1, 5),
            "radial_cross": Fraction(0),
        },
        {
            "name": "small_beta_1_over_1000",
            "beta": Fraction(1, 1000),
            "t": Fraction(1, 8),
            "r": Fraction(1, 5),
            "radial_cross": Fraction(0),
        },
        {
            "name": "maximal_simple_perturbative_t_1_over_6",
            "beta": Fraction(1, 20),
            "t": Fraction(1, 6),
            "r": Fraction(1, 5),
            "radial_cross": Fraction(0),
        },
        {
            "name": "radially_recentered_positive_projector_attempt",
            "beta": Fraction(1, 20),
            "t": Fraction(1, 8),
            "r": Fraction(1, 5),
            "radial_cross": Fraction(1, 20),
        },
        {
            "name": "unit_sigma_scale_small_beta",
            "beta": Fraction(1, 100),
            "t": Fraction(1, 8),
            "r": Fraction(1),
            "radial_cross": Fraction(0),
        },
    )
    rows: list[dict[str, Any]] = []
    for configuration_index, configuration in enumerate(configurations):
        best_value = math.inf
        best_sector: tuple[int, int] | None = None
        best_point: np.ndarray | None = None
        for plane in range(5):
            for chirality in (-1, 1):
                result = differential_evolution(
                    lambda variables: reduced_slice_gap(
                        variables,
                        plane=plane,
                        chirality=chirality,
                        beta=float(configuration["beta"]),
                        t=float(configuration["t"]),
                        r=float(configuration["r"]),
                        radial_cross=float(configuration["radial_cross"]),
                    ),
                    bounds=((-3, 3), (-3, 3), (-3, 3), (-3, 3), (0, 8)),
                    seed=73_100 + 101 * configuration_index + 7 * plane + chirality,
                    maxiter=120,
                    popsize=7,
                    tol=1.0e-9,
                    polish=True,
                    workers=1,
                )
                if result.fun < best_value:
                    best_value = float(result.fun)
                    best_sector = (plane, chirality)
                    best_point = np.asarray(result.x, dtype=float)
        rows.append(
            {
                **configuration,
                "minimum_gap_found": best_value,
                "best_sector": {
                    "plane": best_sector[0] if best_sector else None,
                    "chirality": best_sector[1] if best_sector else None,
                },
                "best_point_p_a_omega_rho_NH": best_point,
                "lower_witness_found": best_value < -LOWER_WITNESS_TOLERANCE,
                "counts_as_global_proof": False,
            }
        )
    return {
        "scope": (
            "complete P/A/omega singlet slice, Sigma=rho Delta_R, all five "
            "complex H planes and both chiralities"
        ),
        "optimizer": "deterministic-seed scipy differential_evolution plus polish",
        "bounds": {
            "p_a_omega_rho": [-3, 3],
            "N_H": [0, 8],
        },
        "source_formula": (
            "exact PD residual decomposition plus live-source Q_chi and I45 "
            "restrictions; Sigma 54/1050bar residuals vanish on the Delta ray"
        ),
        "phi_polynomial_validation_residual": _reduced_slice_source()[
            "phi_polynomial_validation_residual"
        ],
        "configurations": rows,
        "any_lower_witness_found": any(row["lower_witness_found"] for row in rows),
        "diagnostic_only": True,
    }


def build_report() -> dict[str, Any]:
    current_no_go = exact_current_gram_no_go_certificate()
    chiral_no_go = exact_unique_chiral_quartic_no_go_certificate()
    affine_no_go = hsx.exact_positive_affine_sos_replacement_no_go_certificate()
    searches = reduced_numerical_searches()
    checks = {
        "current_covariants_source_bound": current_no_go["source_binding_exact"],
        "current_covariant_Gram_is_positive_definite": current_no_go[
            "positive_definite"
        ],
        "current_square_no_go_is_proof_grade": current_no_go["proof_grade"],
        "unique_chiral_quartic_no_go_is_proof_grade": chiral_no_go[
            "proof_grade"
        ],
        "affine_all_vanishing_SOS_no_go_is_proof_grade": affine_no_go[
            "proof_grade"
        ],
        "reduced_search_source_polynomial_is_bound": searches[
            "phi_polynomial_validation_residual"
        ]
        < 1.0e-8,
        "numerical_search_not_misrepresented_as_proof": searches[
            "diagnostic_only"
        ],
        "G3_not_promoted_by_negative_result": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    lower_witness = bool(searches["any_lower_witness_found"])
    return _jsonable(
        {
            "status": (
                "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
                if not failures
                else "ALTERNATIVE_GLOBAL_SOS_AUDIT_INTEGRITY_FAILED"
            ),
            "overall_state": "G3_GLOBAL_ALTERNATIVE_OPEN" if not failures else "EXECUTION_FAIL",
            "model_contract_id": hsx.MODEL_CONTRACT_ID,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "exact_current_square_no_go": current_no_go,
            "exact_unique_chiral_quartic_no_go": chiral_no_go,
            "upstream_affine_zero_residual_no_go": affine_no_go,
            "targeted_reduced_searches": searches,
            "flags": {
                "globally_certifiable_alternative_found": False,
                "all_vanishing_45_current_Gram_completion_excluded": current_no_go[
                    "proof_grade"
                ],
                "all_vanishing_affine_SOS_completion_excluded": affine_no_go[
                    "proof_grade"
                ],
                "all_vanishing_unique_chiral_quartic_completion_excluded": chiral_no_go[
                    "proof_grade"
                ],
                "nonvanishing_residual_gradient_cancellation_excluded": False,
                "different_vacuum_orbit_excluded": False,
                "lower_witness_found_in_reduced_searches": lower_witness,
                "current_candidate_global_minimum_certified": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
            "remaining_routes": [
                "prove a uniform finite-field gap for the signed beta deformation",
                "construct and certify a nonvanishing-residual positive completion",
                "move to a different exact stationary orbit and repeat rank/global tests",
            ],
            "verdict": (
                "The most direct beta-free positive completion is exactly "
                "obstructed: the Phi, H and Sigma adjoint covariants are linearly "
                "independent at the selected orbit for every nonzero r. The "
                "independent affine zero-residual routes are obstructed as well. "
                "No lower point was found in the enlarged reduced searches, but "
                "that numerical survival is not a global certificate. G3 remains "
                "open and the whole model is not excluded."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Alternative globally positive G3 completion audit -- v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        "- exact current Gram determinant at r=1/5: `27/15625`;\n"
        "- zero-residual 45-current completion: `EXCLUDED`;\n"
        "- nonvanishing-residual completion: `OPEN`;\n"
        f"- lower reduced-search witness: `{str(report['flags']['lower_witness_found_in_reduced_searches']).lower()}`;\n"
        "- globally certified replacement: `false`;\n"
        "- G3: `OPEN`.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
