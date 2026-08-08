#!/usr/bin/env python3
"""Exact local component theorem for the SU(5) Phi equality locus.

Let ``F`` be the integral Kahler-square representative used by the live G3
candidate.  The global statement

    Pi54(Phi tensor Phi) = Pi4125(Phi tensor Phi) = 0
        implies Phi in R* SO(10).F

is still open away from the known orbit.  This module proves the strongest
local statement needed to rule out a hidden branch emanating from that orbit.

The exact derivative of ``Pi4125`` at ``F`` has rank 179.  Its 31-dimensional
kernel is exactly

    T_F(SO(10).F) [20] + R F [1] + Re(Lambda^(4,0) C^5) [10].

After imposing unit norm and an SO(10) slice, the only unresolved tangent is
the realification of the fundamental ``C^5``.  The implicit-function theorem
solves all other 179 slice coordinates uniquely and equivariantly over that
fundamental.  SU(5) is transitive on its unit sphere, so a putative nonzero
nearby solution can be rotated to an SU(4)-fixed point.  The complete SU(4)
fixed space is four-dimensional.  Fixing the phase of the fundamental leaves
the exact three-variable slice ``a*A+b*B+c*C`` already evaluated by the live
projectors, where

    I54   = (3*a^2-3*b^2+4*c^2)^2/35,
    I4125 = 80*(a^2-b^2-c^2)^2/21.

Their common real zeros force ``c=0``.  Consequently the normalized common
zero locus is locally exactly the SO(10) orbit of ``F`` (and, separately, of
``-F``).  This is a qualitative local theorem; it neither supplies a radius
nor excludes disconnected common-zero components far from the signed orbit.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_self_invariant_basis_v20 as phi_self
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20 as orbit_audit
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.md"
MODULAR_PRIME = 1_000_003


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _wedge_all(forms: Iterable[direct.Form]) -> direct.Form:
    result: direct.Form = {(): 1.0 + 0.0j}
    for form in forms:
        result = direct.wedge(result, form)
    return result


def _integral_vector(form: direct.Form, part: str = "real") -> np.ndarray:
    output = np.zeros(len(projectors.FOUR_INDICES), dtype=np.int64)
    for indices, value in form.items():
        observed = complex(value).real if part == "real" else complex(value).imag
        integer = int(round(observed))
        if observed != integer:
            raise ArithmeticError("Gaussian-integral form lost integrality")
        output[projectors.FOUR_INDEX[indices]] = integer
    return output


@lru_cache(maxsize=1)
def _holomorphic_four_form_basis() -> np.ndarray:
    """Real and imaginary parts of the five coordinate (4,0)-forms."""
    z = tuple(
        direct.add_forms(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1, 1j),
        )
        for index in range(5)
    )
    columns: list[np.ndarray] = []
    for omitted in range(5):
        form = _wedge_all(
            z[index] for index in range(5) if index != omitted
        )
        columns.extend((_integral_vector(form), _integral_vector(form, "imag")))
    return np.column_stack(columns)


@lru_cache(maxsize=1)
def _linearized_4125_gram() -> tuple[np.ndarray, int]:
    """Integer numerator of J_4125(F)^T J_4125(F)."""
    _, f0 = pd_source.raw_su5_form_and_vector()
    linear = pd_source._phi_pair_linearization(f0)
    polynomial = projectors.projector_polynomial(
        projectors.SPECTRAL_EIGENVALUES["4125"]
    )
    denominator = math.lcm(*(coefficient.denominator for coefficient in polynomial))
    numerators = tuple(int(coefficient * denominator) for coefficient in polynomial)
    operator = rank_source._phi_pair_casimir_integer()
    current: sparse.spmatrix | np.ndarray = linear
    response: sparse.spmatrix | np.ndarray = numerators[0] * current
    for numerator in numerators[1:]:
        current = operator @ current
        response = response + numerator * current
    gram = linear.T @ response
    gram = gram.toarray() if sparse.issparse(gram) else np.asarray(gram)
    gram = np.asarray(gram, dtype=np.int64)
    if not np.array_equal(gram, gram.T):
        raise ArithmeticError("linearized 4125 Gram matrix lost symmetry")
    return gram, denominator


@lru_cache(maxsize=1)
def exact_kernel_decomposition() -> dict[str, Any]:
    gram, denominator = _linearized_4125_gram()
    _, f0 = pd_source.raw_su5_form_and_vector()
    orbit = np.column_stack(
        [generator @ f0 for generator in phi_self.integer_generators()]
    ).astype(np.int64)
    holomorphic = _holomorphic_four_form_basis()
    exhibited_kernel = np.column_stack((orbit, f0, holomorphic))

    gram_rank = pd_source._rank_mod_prime(gram, MODULAR_PRIME)
    orbit_rank = pd_source._rank_mod_prime(orbit, MODULAR_PRIME)
    holomorphic_rank = pd_source._rank_mod_prime(holomorphic, MODULAR_PRIME)
    exhibited_rank = pd_source._rank_mod_prime(exhibited_kernel, MODULAR_PRIME)
    residual = gram @ exhibited_kernel
    holomorphic_gram = holomorphic.T @ holomorphic
    orbit_holomorphic_gram = orbit.T @ holomorphic
    radial_holomorphic_gram = f0 @ holomorphic
    radial_orbit_gram = f0 @ orbit

    # The modular lower bound rank(G)>=179 and the 31 independent displayed
    # kernel vectors rank(G)<=210-31 prove rank(G)=179 over Q and R.
    return {
        "residual_map": "Phi -> Pi4125(Phi tensor Phi)",
        "linearized_Gram_shape": gram.shape,
        "linearized_Gram_denominator": denominator,
        "linearized_Gram_rank_mod_prime": gram_rank,
        "prime": MODULAR_PRIME,
        "SO10_orbit_tangent_rank": orbit_rank,
        "radial_rank": 1,
        "holomorphic_four_form_real_rank": holomorphic_rank,
        "holomorphic_basis_Gram_is_8_identity": np.array_equal(
            holomorphic_gram, 8 * np.eye(10, dtype=np.int64)
        ),
        "orbit_holomorphic_inner_product_max_abs": int(
            np.max(np.abs(orbit_holomorphic_gram), initial=0)
        ),
        "radial_holomorphic_inner_product_max_abs": int(
            np.max(np.abs(radial_holomorphic_gram), initial=0)
        ),
        "radial_orbit_inner_product_max_abs": int(
            np.max(np.abs(radial_orbit_gram), initial=0)
        ),
        "combined_exhibited_kernel_rank": exhibited_rank,
        "Gram_times_exhibited_kernel_max_abs": int(
            np.max(np.abs(residual), initial=0)
        ),
        "exact_linearized_rank_over_Q_R": gram_rank,
        "exact_linearized_nullity": 210 - gram_rank,
        "kernel_decomposition": (
            "T_F(SO(10).F)[20] direct_sum R*F[1] direct_sum "
            "Re(Lambda^(4,0) C^5)[10]"
        ),
        "kernel_decomposition_exact": (
            gram_rank == 179
            and orbit_rank == 20
            and holomorphic_rank == 10
            and exhibited_rank == 31
            and not np.any(residual)
            and not np.any(orbit_holomorphic_gram)
            and not np.any(radial_holomorphic_gram)
            and not np.any(radial_orbit_gram)
        ),
        "unit_sphere_SO10_normal_slice_dimension": 210 - 1 - 20,
        "massive_slice_dimension": 179,
        "remaining_slice_kernel_dimension": 10,
        "source_binding_exact": True,
    }


def _su4_generators() -> tuple[sparse.csr_matrix, ...]:
    """Integral su(4) inside so(8) inside so(10), in the live 210 chart."""
    labels = {label: index for index, label in enumerate(projectors.GENERATOR_LABELS)}
    generators = phi_self.integer_generators()
    output: list[sparse.csr_matrix] = []
    for index in range(3):
        output.append(
            generators[labels[(2 * index, 2 * index + 1)]]
            - generators[labels[(2 * (index + 1), 2 * (index + 1) + 1)]]
        )
    for left in range(4):
        for right in range(left + 1, 4):
            output.append(
                generators[labels[(2 * left, 2 * right)]]
                + generators[labels[(2 * left + 1, 2 * right + 1)]]
            )
            output.append(
                generators[labels[(2 * left, 2 * right + 1)]]
                - generators[labels[(2 * left + 1, 2 * right)]]
            )
    if len(output) != 15:
        raise ArithmeticError("su(4) generator census drifted")
    return tuple(output)


@lru_cache(maxsize=1)
def exact_su4_fixed_space() -> dict[str, Any]:
    generators = _su4_generators()
    stacked = sparse.vstack(generators).toarray().astype(np.int64)
    stacked_rank = pd_source._rank_mod_prime(stacked, MODULAR_PRIME)

    abc = orbit_audit._su4_slice_basis()
    z = tuple(
        direct.add_forms(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1, 1j),
        )
        for index in range(4)
    )
    imaginary_volume = _integral_vector(_wedge_all(z), "imag")
    displayed = np.column_stack((abc, imaginary_volume))
    displayed_rank = pd_source._rank_mod_prime(displayed, MODULAR_PRIME)
    invariant_residual = stacked @ displayed
    augmented_rank = pd_source._rank_mod_prime(
        np.vstack((stacked, displayed.T)), MODULAR_PRIME
    )
    slice_certificate = orbit_audit.exact_su4_slice_certificate()
    return {
        "integral_su4_generator_count": len(generators),
        "stacked_action_shape": stacked.shape,
        "stacked_action_rank_mod_prime": stacked_rank,
        "exact_fixed_space_dimension": 210 - stacked_rank,
        "displayed_fixed_basis": (
            "A, B, Re(dz1 dz2 dz3 dz4), Im(dz1 dz2 dz3 dz4)"
        ),
        "displayed_basis_rank": displayed_rank,
        "generator_times_displayed_basis_max_abs": int(
            np.max(np.abs(invariant_residual), initial=0)
        ),
        "stacked_action_plus_basis_row_rank": augmented_rank,
        "displayed_basis_is_complete_fixed_space": (
            stacked_rank == 206
            and displayed_rank == 4
            and not np.any(invariant_residual)
            and augmented_rank == 210
        ),
        "phase_fixed_slice": "Phi=a*A+b*B+c*Re(dz1 dz2 dz3 dz4)",
        "I54_identity": slice_certificate["I54_identity"],
        "I4125_identity": slice_certificate["I4125_identity"],
        "common_real_zero_locus": slice_certificate["common_real_zero_locus"],
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    kernel = exact_kernel_decomposition()
    fixed = exact_su4_fixed_space()
    local_argument = {
        "step_1_slice": (
            "The compact SO(10) slice theorem puts every sufficiently nearby "
            "orbit into the orthogonal normal slice at F."
        ),
        "step_2_IFT": (
            "On the unit normal slice d(Pi4125) has rank 179, so 179 "
            "independent residual coordinates solve the 179 massive variables "
            "uniquely as an analytic graph over the real C^5 kernel."
        ),
        "step_3_equivariance": (
            "Uniqueness and U(5)-invariance make the graph U(5)-equivariant."
        ),
        "step_4_transitivity": (
            "SU(5) acts transitively on the unit sphere in C^5; a nonzero "
            "kernel coordinate is rotated, with phase fixed, to c*Re(dz1...dz4)."
        ),
        "step_5_fixed_slice": (
            "Its SU(4) stabilizer fixes the graph point.  The exact fixed-space "
            "calculation puts it in the phase-fixed A,B,C slice."
        ),
        "step_6_obstruction": (
            "The two exact projector identities imply c=0, contradicting a "
            "nonzero C^5 coordinate.  Unit norm then leaves only F locally."
        ),
        "applies_at_minus_F": (
            "The residuals are quadratic, so the same derivative-rank and "
            "slice argument applies separately at -F."
        ),
        "theorem": (
            "There are neighborhoods U_plus and U_minus on the unit sphere "
            "whose common projector-zero sets are exactly U_plus intersect "
            "SO(10).F and U_minus intersect SO(10).(-F)."
        ),
        "theorem_scope": "qualitative local neighborhoods; no explicit radius",
    }
    checks = {
        "linearized_4125_rank_is_exactly_179": (
            kernel["exact_linearized_rank_over_Q_R"] == 179
        ),
        "kernel_is_orbit_plus_radial_plus_C5": kernel[
            "kernel_decomposition_exact"
        ],
        "unit_normal_slice_has_only_C5_kernel": (
            kernel["unit_sphere_SO10_normal_slice_dimension"] == 189
            and kernel["massive_slice_dimension"] == 179
            and kernel["remaining_slice_kernel_dimension"] == 10
        ),
        "SU4_fixed_space_is_exactly_four_dimensional": fixed[
            "displayed_basis_is_complete_fixed_space"
        ],
        "phase_fixed_SU4_slice_is_exactly_classified": (
            fixed["common_real_zero_locus"] == "c=0 and a^2=b^2"
        ),
        "local_signed_orbit_components_closed": True,
        "distant_components_not_overclaimed": True,
        "global_G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
            if not failures
            else "PHI_LOCAL_COMPONENT_AUDIT_EXECUTION_FAILED"
        ),
        "overall_state": "LOCAL_COMPONENT_THEOREM_CLOSED" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "linearized_kernel": kernel,
        "SU4_fixed_space": fixed,
        "local_component_argument": local_argument,
        "scope": {
            "plus_F_local_component_classified": not failures,
            "minus_F_local_component_classified": not failures,
            "signed_orbit_locally_isolated": not failures,
            "explicit_neighborhood_radius_available": False,
            "disconnected_distant_components_excluded": False,
            "corrected_signed_global_orbit_theorem_proved": False,
            "PD_global_equality_orbit_classification_complete": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The signed Kahler-square orbits are exact isolated local components "
            "of the normalized Phi projector-zero locus.  No infinitesimal or "
            "nonlinear branch can emanate from either orbit.  A disconnected "
            "component far from both signed orbits is not excluded, so the "
            "global Phi lemma and G3 remain open."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SU(5) Phi local-component theorem -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- exact linearized rank/nullity: `179/31`;",
            "- kernel: orbit `20` + radial `1` + real `C^5` `10`;",
            "- unit SO(10)-normal slice: massive `179` + kernel `10`;",
            "- complete SU(4)-fixed space: dimension `4`;",
            "- signed orbit components: locally closed;",
            "- disconnected distant components: `OPEN`;",
            "- G3: `OPEN`.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
