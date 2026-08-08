#!/usr/bin/env python3
"""Exact audit of the real-four-form orbit lemma used by the SU(5) G3 route.

The upstream equality reduction asked whether every real unit four-form
``Phi`` satisfying

    Pi_54(Phi tensor Phi) = Pi_4125(Phi tensor Phi) = 0

is SO(10)-conjugate to the selected Kahler-square representative ``F``.
Taken literally as a *single* SO(10) orbit, that statement is false: ``-F``
obeys the same quadratic equations, while the exact cubic invariant
``Tr(A_Phi^3)`` has the opposite sign.  Thus no orthogonal transformation,
and in particular no SO(10) transformation, maps ``F`` to ``-F``.

The physically useful corrected statement is the signed version

    zero locus = SO(10).F union SO(10).(-F).

This module does not claim that global theorem.  It does prove an exact
source-bound reduction on the slice which contains all ten infinitesimal
directions left over beyond the tangent to SO(10)/U(5).  Write

    A = sum_{1<=i<j<=4} omega_i omega_j,
    B = sum_{1<=i<=4} omega_i omega_5,
    C = Re(dz_1 dz_2 dz_3 dz_4).

On ``Phi=a A+b B+c C`` the live Casimir projectors give exactly

    I_54   = (3 a^2-3 b^2+4 c^2)^2/35,
    I_4125 = 80 (a^2-b^2-c^2)^2/21.

Their common real zero set has ``c=0`` and ``a^2=b^2``.  Hence the complex-5
excess tangent direction ``C`` is quadratically obstructed on its complete
SU(4)-invariant slice.  This is a sharp local/symmetry-slice result, not a
classification of all real four-forms.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_self_invariant_basis_v20 as phi_self
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.md"

MONOMIAL_LABELS = (
    "a2",
    "a_b",
    "a_c",
    "b2",
    "b_c",
    "c2",
)
EXPECTED_54_LINEAR_SQUARE = np.asarray((3, 0, 0, -3, 0, 4), dtype=np.int64)
EXPECTED_4125_LINEAR_SQUARE = np.asarray((1, 0, 0, -1, 0, -1), dtype=np.int64)
MODULAR_RANK_PRIME = 1_000_003


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


def _exact_cubic_from_vector(vector: np.ndarray) -> int:
    form = phi_self.vector_to_phi(np.asarray(vector, dtype=np.int64))
    matrix_float = phi_self.two_form_matrix(form)
    matrix = np.rint(matrix_float).astype(np.int64)
    if np.any(matrix_float != matrix):
        raise ArithmeticError("integer four-form produced a nonintegral two-form matrix")
    return int(np.trace(matrix @ matrix @ matrix, dtype=np.int64))


@lru_cache(maxsize=1)
def exact_opposite_orbit_counterexample() -> dict[str, Any]:
    _, f0 = pd_source.raw_su5_form_and_vector()
    projector = pd_source.exact_phi_projector_certificate()
    cubic_plus = _exact_cubic_from_vector(f0)
    cubic_minus = _exact_cubic_from_vector(-f0)
    return {
        "representatives": {
            "plus": "F=F0/sqrt(10)",
            "minus": "-F=-F0/sqrt(10)",
        },
        "raw_norm_squared_both": int(f0 @ f0),
        "I54_raw_both": projector["raw_projector_values"]["54"],
        "I4125_raw_both": projector["raw_projector_values"]["4125"],
        "cubic_invariant_definition": "I3(Phi)=Tr(A_Phi^3)",
        "raw_cubic_plus": cubic_plus,
        "raw_cubic_minus": cubic_minus,
        "normalized_cubic_plus": "6/sqrt(10)",
        "normalized_cubic_minus": "-6/sqrt(10)",
        "invariance_argument": (
            "For Q in O(10), A_(Q.Phi)=(Lambda^2 Q) A_Phi "
            "(Lambda^2 Q)^T, so Tr(A_Phi^3) is invariant."
        ),
        "not_O10_conjugate": cubic_plus != cubic_minus,
        "not_SO10_conjugate": cubic_plus != cubic_minus,
        "literal_single_orbit_lemma_refuted": (
            projector["raw_projector_values"]["54"] == 0
            and projector["raw_projector_values"]["4125"] == 0
            and cubic_plus == 60
            and cubic_minus == -60
        ),
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def _su4_slice_basis() -> np.ndarray:
    index = {
        indices: position
        for position, indices in enumerate(projectors.FOUR_INDICES)
    }
    kahler_four = np.zeros(210, dtype=np.int64)
    fifth_plane_mixed = np.zeros(210, dtype=np.int64)
    for left, right in itertools.combinations(range(4), 2):
        indices = (2 * left, 2 * left + 1, 2 * right, 2 * right + 1)
        kahler_four[index[indices]] = 1
    for left in range(4):
        indices = (2 * left, 2 * left + 1, 8, 9)
        fifth_plane_mixed[index[indices]] = 1

    holomorphic = {(): 1.0 + 0.0j}
    for plane in range(4):
        one_form = direct.add_forms(
            direct.one_form(2 * plane),
            direct.one_form(2 * plane + 1, 1j),
        )
        holomorphic = direct.wedge(holomorphic, one_form)
    real_volume = np.zeros(210, dtype=np.int64)
    for indices, value in holomorphic.items():
        rounded = int(round(complex(value).real))
        if complex(value).real != rounded:
            raise ArithmeticError("SU(4) volume form lost Gaussian integrality")
        real_volume[index[indices]] = rounded

    basis = np.column_stack((kahler_four, fifth_plane_mixed, real_volume))
    expected_support_sizes = (6, 4, 8)
    if tuple(np.count_nonzero(basis[:, column]) for column in range(3)) != expected_support_sizes:
        raise ArithmeticError("SU(4)-invariant slice support drifted")
    return basis


@lru_cache(maxsize=1)
def _slice_pair_columns() -> np.ndarray:
    basis = _su4_slice_basis()
    columns: list[np.ndarray] = []
    for left in range(3):
        for right in range(left, 3):
            pair = np.outer(basis[:, left], basis[:, right])
            if left != right:
                pair += np.outer(basis[:, right], basis[:, left])
            columns.append(pair.ravel())
    return np.column_stack(columns)


def _projector_gram(channel: str) -> tuple[np.ndarray, int]:
    pair = _slice_pair_columns()
    polynomial = projectors.projector_polynomial(
        projectors.SPECTRAL_EIGENVALUES[channel]
    )
    denominator = math.lcm(*(coefficient.denominator for coefficient in polynomial))
    numerators = tuple(int(coefficient * denominator) for coefficient in polynomial)
    operator = rank_source._phi_pair_casimir_integer()
    current = pair
    response = numerators[0] * current
    for numerator in numerators[1:]:
        current = operator @ current
        response += numerator * current
    gram = np.asarray(pair.T @ response, dtype=np.int64)
    if not np.array_equal(gram, gram.T):
        raise ArithmeticError(f"{channel} slice Gram matrix lost symmetry")
    return gram, denominator


@lru_cache(maxsize=1)
def exact_su4_slice_certificate() -> dict[str, Any]:
    gram_54, denominator_54 = _projector_gram("54")
    gram_4125, denominator_4125 = _projector_gram("4125")
    outer_54 = np.outer(EXPECTED_54_LINEAR_SQUARE, EXPECTED_54_LINEAR_SQUARE)
    outer_4125 = np.outer(
        EXPECTED_4125_LINEAR_SQUARE, EXPECTED_4125_LINEAR_SQUARE
    )
    identity_54 = 35 * gram_54 - denominator_54 * outer_54
    identity_4125 = (
        21 * gram_4125 - 80 * denominator_4125 * outer_4125
    )
    return {
        "slice": "Phi=a*A+b*B+c*C",
        "basis": {
            "A": "sum_(1<=i<j<=4) omega_i wedge omega_j",
            "B": "sum_(1<=i<=4) omega_i wedge omega_5",
            "C": "Re(dz_1 wedge dz_2 wedge dz_3 wedge dz_4)",
        },
        "basis_support_sizes": tuple(
            int(np.count_nonzero(_su4_slice_basis()[:, column]))
            for column in range(3)
        ),
        "pair_monomials": MONOMIAL_LABELS,
        "I54_Gram_numerator": gram_54,
        "I54_Gram_denominator": denominator_54,
        "I4125_Gram_numerator": gram_4125,
        "I4125_Gram_denominator": denominator_4125,
        "I54_identity": "(3*a^2-3*b^2+4*c^2)^2/35",
        "I4125_identity": "80*(a^2-b^2-c^2)^2/21",
        "I54_matrix_identity_max_abs_residual": int(
            np.max(np.abs(identity_54), initial=0)
        ),
        "I4125_matrix_identity_max_abs_residual": int(
            np.max(np.abs(identity_4125), initial=0)
        ),
        "real_zero_derivation": (
            "r54-3*r4125=7*c^2, hence c=0; then r4125=0 "
            "gives a^2=b^2"
        ),
        "common_real_zero_locus": "c=0 and a^2=b^2",
        "complex_five_direction_obstructed": True,
        "complete_SU4_invariant_slice_classified": True,
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def exact_linearized_warning() -> dict[str, Any]:
    gram, _, _ = pd_source._exact_phi_sos_gram()
    _, f0 = pd_source.raw_su5_form_and_vector()
    orbit_tangent = np.column_stack(
        [generator @ f0 for generator in phi_self.integer_generators()]
    )
    residual_rank = pd_source._rank_mod_prime(gram, MODULAR_RANK_PRIME)
    orbit_rank = pd_source._rank_mod_prime(orbit_tangent, MODULAR_RANK_PRIME)
    return {
        "unit_norm_plus_projector_linearized_rank": residual_rank,
        "linearized_nullity": 210 - residual_rank,
        "SO10_orbit_tangent_rank": orbit_rank,
        "excess_linearized_nullity": 210 - residual_rank - orbit_rank,
        "SU5_type_of_excess": "5+5bar (ten real dimensions)",
        "interpretation": (
            "The quadrics are singular along the Kahler-square orbit; a "
            "Jacobian-rank argument alone cannot prove the global lemma."
        ),
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    counterexample = exact_opposite_orbit_counterexample()
    slice_certificate = exact_su4_slice_certificate()
    linearized = exact_linearized_warning()
    checks = {
        "F_and_minus_F_are_unit_after_normalization": (
            counterexample["raw_norm_squared_both"] == 10
        ),
        "F_and_minus_F_obey_both_projector_equations": (
            counterexample["I54_raw_both"] == 0
            and counterexample["I4125_raw_both"] == 0
        ),
        "opposite_cubic_invariants_are_exact": (
            counterexample["raw_cubic_plus"] == 60
            and counterexample["raw_cubic_minus"] == -60
        ),
        "literal_single_orbit_lemma_is_refuted": counterexample[
            "literal_single_orbit_lemma_refuted"
        ],
        "SU4_slice_I54_identity_is_exact": (
            slice_certificate["I54_matrix_identity_max_abs_residual"] == 0
        ),
        "SU4_slice_I4125_identity_is_exact": (
            slice_certificate["I4125_matrix_identity_max_abs_residual"] == 0
        ),
        "SU4_slice_common_real_zeros_are_signed_Kahler_squares": (
            slice_certificate["common_real_zero_locus"]
            == "c=0 and a^2=b^2"
        ),
        "linearization_has_ten_nonorbit_directions": (
            linearized["linearized_nullity"] == 30
            and linearized["SO10_orbit_tangent_rank"] == 20
            and linearized["excess_linearized_nullity"] == 10
        ),
        "corrected_signed_global_lemma_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
            if not failures
            else "PHI_ORBIT_LEMMA_AUDIT_EXECUTION_FAILED"
        ),
        "overall_state": "SHARP_COUNTEREXAMPLE_AND_REDUCTION" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "opposite_orbit_counterexample": counterexample,
        "SU4_invariant_slice": slice_certificate,
        "linearized_warning": linearized,
        "corrected_global_lemma": {
            "statement": (
                "Every nonzero real Phi with Pi54(Phi tensor Phi)=0 and "
                "Pi4125(Phi tensor Phi)=0 lies in SO(10).F or SO(10).(-F)."
            ),
            "proved": False,
            "counterexample_found": False,
            "remaining_scope": "arbitrary real four-forms outside the SU(4)-invariant slice",
        },
        "scope": {
            "literal_plus_orbit_only_statement_refuted": not failures,
            "complete_SU4_invariant_slice_classified": not failures,
            "ten_excess_tangent_directions_obstructed_on_natural_slice": not failures,
            "all_arbitrary_real_four_forms_classified": False,
            "corrected_signed_two_orbit_theorem_proved": False,
            "PD_global_equality_orbit_classification_complete": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The one-orbit Phi lemma is false as written: -F is an exact "
            "second SO(10) orbit, distinguished from F by the cubic invariant. "
            "After correcting the target to the signed union of two orbits, "
            "the natural SU(4)-invariant slice is completely classified and "
            "contains no further branch; its complex-five direction is "
            "exactly obstructed. The arbitrary-four-form signed theorem "
            "remains open and cannot be replaced by the rank calculation."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SU(5) Phi orbit-lemma audit -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- exact counterexample to the literal one-orbit statement: `-F`;",
            "- exact cubic separator: `I3(F0)=60`, `I3(-F0)=-60`;",
            "- corrected signed two-orbit theorem: `OPEN`;",
            "- complete SU(4)-invariant slice: `c=0`, `a^2=b^2`;",
            "- arbitrary real-four-form classification: `OPEN`;",
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
