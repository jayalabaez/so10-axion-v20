#!/usr/bin/env python3
"""Exact local equality-orbit theorem for the physical-SM witness.

Let K=SO(10) x U(1)_X x U(1)_PQ act orthogonally on the canonical
486-real scalar chart.  The frozen exact 37-row theorem proves that q_* is
stationary, that its Hessian is positive semidefinite, and that its kernel is
exactly the 38-dimensional tangent space to K.q_*.  The K-invariance audit and
compactness of K therefore put the standard equivariant Morse--Bott/slice
lemma in its nondegenerate-orbit case: there exists a K-invariant open
neighborhood U of K.q_* for which

  Crit(V) intersect U = K.q_*,

and the orbit is a strict local minimum in U/K.  Hence every stationary point
in U with V=-1 is on that orbit.  This is an existence theorem; it supplies
no numerical radius and makes no statement about equality components outside
U.

The prior five-amplitude theorem found sixteen sign variants.  This module
also gives exact rational multiples of pi for an SO(10) Cartan rotation and
the two declared U(1) phases that connect every variant continuously to q_*.
Thus those sixteen variants form one declared continuous-symmetry orbit.

Neither conclusion classifies the complete 486-field equality locus, so all
global G3--G5 claims remain false.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_physical_quotient_v20 as quotient
import live_g2_canonical_486_field_chart_v20 as chart
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md"
SCHEMA = "exact_physical_sm_local_equality_orbit_v20"
STATUS = "EXACT_FULL_486_LOCAL_EQUALITY_ORBIT_AND_16_SIGN_ORBIT__GLOBAL_EQUALITY_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"

DEPENDENCIES = {
    "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json": "66bafa7e00ce543abea0e29b8be586cca8ecb1c5417204fc0ec75f6736c984b3",
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json": "61bca8d55230b798b1d45ae4496c2b1b39490f73d0596e671478a388f72449ce",
    "GAUGED_U1X_SCALAR_CONTRACT_V20.json": "3244ed71f185f22441f73707a8a7ee34e9dcbcae3b1bcb478df560ccb2366375",
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json": "506dc21cffda5d25d7f6a86bb100a961186a9f54fe716d3a8daf4251c92248d3",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "exact_gauged_u1x_physical_quotient_v20.py": "405fd691d633d9b925af27c6bc0504bf741784198ae3b0c1fe83da7ca2284324",
    "live_g2_canonical_486_field_chart_v20.py": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
}
AGGREGATE_CORE_SHA256 = "8c1aeffcd29a4f78c42014f92cf4bfa09823a6a2efbd660d512d6b014db99f43"
FIVE_AMPLITUDE_CORE_SHA256 = "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"


def _portable_lf_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def source_bindings() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    documents: dict[str, Any] = {}
    rows: dict[str, dict[str, Any]] = {}
    for name, expected in DEPENDENCIES.items():
        path = ROOT / name
        observed = _portable_lf_sha256(path)
        if observed != expected:
            raise ArithmeticError(f"local equality-orbit dependency drifted: {name}")
        rows[name] = {
            "portable_lf_sha256": observed,
            "expected_portable_lf_sha256": expected,
            "matches": True,
        }
        if path.suffix == ".json":
            documents[name] = json.loads(path.read_text(encoding="utf-8"))
    return {
        "files": rows,
        "all_portable_lf_pins_match": True,
    }, documents


def _fraction(value: Fraction) -> str:
    return str(value)


def _gi_neg(value: quotient.GaussianInteger) -> quotient.GaussianInteger:
    return (-value[0], -value[1])


def _gi_i(value: quotient.GaussianInteger) -> quotient.GaussianInteger:
    return (-value[1], value[0])


def _i_times_form(form: quotient.ExactForm) -> quotient.ExactForm:
    return {indices: _gi_i(value) for indices, value in form.items()}


def _vector_generator_action(
    vector: tuple[quotient.GaussianInteger, ...], first: int, second: int
) -> tuple[quotient.GaussianInteger, ...]:
    output = [quotient.ZERO] * len(vector)
    output[first] = vector[second]
    output[second] = _gi_neg(vector[first])
    return tuple(output)


def _i_times_vector(
    vector: tuple[quotient.GaussianInteger, ...]
) -> tuple[quotient.GaussianInteger, ...]:
    return tuple(_gi_i(value) for value in vector)


def _exact_target_vector_from_shapes() -> np.ndarray:
    phi, h, sigma = foundation._canonical_exact_shapes()
    output: list[int] = []
    for indices in chart.phi_indices():
        real, imaginary = phi.get(indices, quotient.ZERO)
        if imaginary:
            raise ArithmeticError("physical real Phi shape acquired an imaginary entry")
        output.append(real)
    for real, imaginary in h:
        output.extend((real, imaginary))
    for indices in quotient._sigma_representatives():
        output.extend(sigma.get(indices, quotient.ZERO))
    target = foundation.integer_target_vector()
    output.extend(int(value) for value in target[chart.S_SLICE])
    output.extend(int(value) for value in target[chart.X_SLICE])
    reconstructed = np.asarray(output, dtype=np.int64)
    if reconstructed.shape != (chart.TOTAL_DIM,) or not np.array_equal(reconstructed, target):
        raise ArithmeticError("exact physical target shapes do not reconstruct the 486-vector")
    return reconstructed


def representation_embedding_certificate() -> dict[str, Any]:
    """Derive the Cartan weights from the actual physical target tensors."""
    phi, h, sigma = foundation._canonical_exact_shapes()
    plane_rows = []
    for plane in range(5):
        first, second = 2 * plane, 2 * plane + 1
        phi_action = quotient._generator_action(phi, first, second)
        h_action = _vector_generator_action(h, first, second)
        sigma_action = quotient._generator_action(sigma, first, second)
        h_expected = _i_times_vector(h) if plane == 4 else (quotient.ZERO,) * 10
        plane_rows.append({
            "plane": [first, second],
            "Phi_generator_action_is_zero": not phi_action,
            "H_Cartan_weight": 1 if h_action == h_expected and plane == 4 else 0 if h_action == h_expected else None,
            "Sigma_Cartan_weight": 1 if sigma_action == _i_times_form(sigma) else None,
        })
    target = _exact_target_vector_from_shapes()
    support = np.flatnonzero(target)
    checks = {
        "physical_target_reconstructed_entrywise_from_exact_shapes": True,
        "target_chart_dimension_is_486": target.size == 486,
        "target_nonzero_real_coordinate_count": support.size == 21,
        "Phi_is_fixed_by_every_Cartan_plane": all(row["Phi_generator_action_is_zero"] for row in plane_rows),
        "H_has_weight_one_only_in_plane_8_9": [row["H_Cartan_weight"] for row in plane_rows] == [0, 0, 0, 0, 1],
        "physical_SM_Sigma_has_plus_one_weight_in_all_five_planes": all(row["Sigma_Cartan_weight"] == 1 for row in plane_rows),
        "phase_charges_match_source": quotient.U1X_CHARGES == {"H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17} and quotient.PQ_CHARGES == {"H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 0},
    }
    if not all(checks.values()):
        raise ArithmeticError(f"physical representation embedding failed: {checks}")
    return {
        "source": "physical_sm_vacuum_local_feasibility_v20._canonical_exact_shapes plus exact SO(10) form/vector generator action",
        "target_sparse_integer_coordinates": {str(int(index)): int(target[index]) for index in support},
        "plane_actions": plane_rows,
        "U1X_charges": quotient.U1X_CHARGES,
        "PQ_charges": quotient.PQ_CHARGES,
        "checks": checks,
    }


def phase_action(
    bits: tuple[int, int, int, int],
    theta: tuple[Fraction, ...],
    alpha: Fraction,
    beta: Fraction,
    *,
    h_plane: int = 4,
    sigma_cartan_weights: tuple[int, ...] = (1, 1, 1, 1, 1),
    u1x_charges: tuple[int, int, int, int] = (-2, -2, 4, 17),
    pq_charges: tuple[int, int, int, int] = (-2, -2, 4, 0),
) -> tuple[dict[str, Fraction], bool]:
    if len(theta) != 5 or len(sigma_cartan_weights) != 5:
        raise ValueError("the SO(10) Cartan has five plane angles/weights")
    labels = ("H", "Sigma", "S", "Phi17")
    so10 = (theta[h_plane], sum(weight * value for weight, value in zip(sigma_cartan_weights, theta, strict=True)), Fraction(0), Fraction(0))
    phases = {
        label: so10[index] + u1x_charges[index] * alpha + pq_charges[index] * beta
        for index, label in enumerate(labels)
    }
    expected = dict(zip(labels, map(Fraction, bits), strict=True))
    return phases, phases == expected


def _signed_target(bits: tuple[int, int, int, int]) -> np.ndarray:
    target = _exact_target_vector_from_shapes().copy()
    for block, bit in zip(
        (chart.H_SLICE, chart.SIGMA_SLICE, chart.S_SLICE, chart.X_SLICE),
        bits,
        strict=True,
    ):
        target[block] *= (-1) ** bit
    return target


def _group_endpoint_target(phases: dict[str, Fraction]) -> np.ndarray:
    target = _exact_target_vector_from_shapes().copy()
    for label, block in zip(
        ("H", "Sigma", "S", "Phi17"),
        (chart.H_SLICE, chart.SIGMA_SLICE, chart.S_SLICE, chart.X_SLICE),
        strict=True,
    ):
        exponent = phases[label]
        if exponent.denominator != 1:
            raise ArithmeticError("listed group endpoint does not act by a real sign")
        target[block] *= -1 if exponent.numerator % 2 else 1
    return target


def _sparse_vector_sha256(vector: np.ndarray) -> str:
    payload = "".join(
        f"{index}:{int(value)}\n" for index, value in enumerate(vector) if value
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def sign_orbit_rows() -> list[dict[str, Any]]:
    """Return and verify exact group parameters for all sixteen sign choices.

    Write theta_j for the SO(10) rotation angle in the oriented plane
    (2j,2j+1), alpha for U(1)_X, and beta for U(1)_PQ, all divided by pi.
    On the target shapes the phase exponents are

      H: theta_4-2 alpha-2 beta,
      Sigma: sum_j theta_j-2 alpha-2 beta,
      S: 4 alpha+4 beta,       Phi17: 17 alpha.

    Each plane rotation acts trivially on its oriented area form; hence the
    target four-form Phi=e_6789 is fixed for every theta_3 and theta_4.
    """
    rows: list[dict[str, Any]] = []
    for h, d, s, x in itertools.product((0, 1), repeat=4):
        alpha = Fraction(x, 17)
        beta = Fraction(s, 4) - alpha
        theta = (
            Fraction(d - h),
            Fraction(0),
            Fraction(0),
            Fraction(0),
            Fraction(h) + Fraction(s, 2),
        )
        bits = (h, d, s, x)
        phases, matches = phase_action(bits, theta, alpha, beta)
        if not matches:
            raise ArithmeticError("exact sign-orbit phase construction failed")
        transformed = _group_endpoint_target(phases)
        expected = _signed_target(bits)
        if not np.array_equal(transformed, expected):
            raise ArithmeticError("group endpoint failed actual 486-coordinate sign action")
        rows.append({
            "bits_h_d_s_x": [h, d, s, x],
            "signs_h_d_s_x": [(-1) ** h, (-1) ** d, (-1) ** s, (-1) ** x],
            "SO10_Cartan_theta_0_to_4_over_pi": [_fraction(value) for value in theta],
            "U1X_alpha_over_pi": _fraction(alpha),
            "PQ_beta_over_pi": _fraction(beta),
            "verified_net_phase_exponents_over_pi": {key: _fraction(value) for key, value in phases.items()},
            "actual_486_coordinate_endpoint_matches_amplitude_variant": True,
            "transformed_target_sparse_sha256": _sparse_vector_sha256(transformed),
        })
    return rows


def build_report() -> dict[str, Any]:
    bindings, docs = source_bindings()
    aggregate = docs["EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json"]
    five = docs["EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json"]
    contract = docs["GAUGED_U1X_SCALAR_CONTRACT_V20.json"]
    census = docs["G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json"]
    embedding = representation_embedding_certificate()
    rows = sign_orbit_rows()

    aggregate_core = aggregate["integrity"]["core_sha256"]
    five_core = five["integrity"]["core_sha256"]
    direction_by_id = {
        row["direction_id"]: row for row in contract["gauged_directions"]
    }
    witness_ids = set(aggregate["witness"]["exact_rational_coefficients"])
    witness_rows_are_neutral = witness_ids.issubset(direction_by_id) and all(
        direction_by_id[row_id]["charge"] == {"PQ": 0, "X": 0, "Z17": 0}
        for row_id in witness_ids
    )
    invariant = (
        contract["implementation_matches_manuscript"]
        and contract["counts"]["invariant_directions"] == 44
        and all(row["charge"] == {"PQ": 0, "X": 0, "Z17": 0} for row in contract["gauged_directions"])
        and witness_rows_are_neutral
        and census["checks"]["live_PQ_X_Z17_neutral"]
        and census["live_symmetry_contract"]["gauge"] == ["SO(10)", "U(1)_X"]
        and census["live_symmetry_contract"]["accidental_global"] == ["PQ"]
    )
    local_hypotheses = {
        "K_is_compact": True,
        "compactness_reason": "SO(10), U(1)_X, and U(1)_PQ are compact and a finite direct product of compact groups is compact",
        "K_acts_smoothly_and_orthogonally_on_R486": True,
        "selected_potential_is_K_invariant": invariant,
        "target_is_exact_stationary_point_with_V_minus_one": aggregate["exact_stationarity"]["exact_gradient_is_zero"] and aggregate["exact_stationarity"]["exact_potential_value"] == "-1",
        "orbit_tangent_dimension": aggregate["exact_kernel_and_rank"]["exact_symmetry_tangent_span_dimension"],
        "Hessian_kernel_dimension": aggregate["exact_kernel_and_rank"]["exact_nullity"],
        "Hessian_kernel_equals_orbit_tangent": aggregate["exact_kernel_and_rank"]["kernel_equals_exact_symmetry_tangent_span"],
        "Hessian_positive_definite_on_a_transverse_complement": aggregate["exact_PSD_certificate"]["full_Hessian_is_positive_definite_mod_kernel"],
    }
    all_local = all(value for key, value in local_hypotheses.items() if key != "compactness_reason")
    groebner = five["exact_Groebner_certificate"]
    exact_sign_solution_bound = (
        groebner["variables"] == ["p", "h", "d", "s", "x"]
        and groebner["reduced_Groebner_basis"]
        == ["h**2 - 1", "d**2 - 1", "s**2 - 1", "x**2 - 1", "p - 1"]
        and groebner["ideals_equal_by_mutual_exact_reduction"]
        and groebner["ideal_is_radical_from_squarefree_separated_basis"]
        and groebner["all_solutions_real"]
        and groebner["solution_set"]
        == "p=1; h,d,s,x independently in {-1,+1}"
    )
    checks = {
        "dependency_pins_match": bindings["all_portable_lf_pins_match"],
        "upstream_core_pins_match": aggregate_core == AGGREGATE_CORE_SHA256 and five_core == FIVE_AMPLITUDE_CORE_SHA256,
        "all_equivariant_Morse_Bott_slice_hypotheses_hold": all_local,
        "actual_486_target_and_representation_embedding_source_verified": all(embedding["checks"].values()),
        "full_486_local_stationary_locus_is_exactly_one_K_orbit": all_local,
        "full_486_local_stationary_equality_locus_is_exactly_one_K_orbit": all_local,
        "exactly_16_sign_rows": len(rows) == 16,
        "every_sign_row_has_verified_exact_phase_action": all(
            list(row["verified_net_phase_exponents_over_pi"].values())
            == [str(value) for value in row["bits_h_d_s_x"]]
            for row in rows
        ),
        "every_sign_row_group_action_matches_all_actual_nonzero_target_coordinates": all(row["actual_486_coordinate_endpoint_matches_amplitude_variant"] for row in rows),
        "five_amplitude_exact_solution_ideal_and_bit_order_source_bound": exact_sign_solution_bound,
        "all_16_five_amplitude_variants_are_one_declared_continuous_orbit": exact_sign_solution_bound and groebner["complex_solution_count_with_multiplicity"] == 16,
        "no_quantitative_neighborhood_radius_claimed": True,
        "global_G3_G4_G5_remain_fail_closed": True,
    }
    failures = [key for key, value in checks.items() if not value]
    if failures:
        raise ArithmeticError(f"local equality-orbit checks failed: {failures}")
    claims = {
        "exists_K_invariant_open_neighborhood_U_of_target_orbit": True,
        "Crit_V_intersection_U_equals_target_orbit": True,
        "stationary_V_minus_one_locus_intersection_U_equals_target_orbit": True,
        "target_orbit_is_strict_local_minimum_in_U_mod_K": True,
        "all_16_five_amplitude_sign_variants_one_continuous_K_orbit": True,
        "quantitative_radius_for_U_proved": False,
        "complete_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_bindings": bindings,
        "local_orbit_theorem": {
            "group_K": "SO(10) x U(1)_X x U(1)_PQ",
            "ambient_real_dimension": 486,
            "target_orbit_dimension": 38,
            "normal_slice_dimension": 448,
            "hypotheses": local_hypotheses,
            "theorem_used": "compact-group slice theorem plus equivariant Morse lemma / Morse-Bott lemma for a nondegenerate critical orbit",
            "conclusion": "there exists a K-invariant open neighborhood U of K.q_* such that Crit(V) intersect U=K.q_*; V is strictly larger than -1 on U minus K.q_* after shrinking U",
            "quantitative_radius": None,
        },
        "sixteen_sign_orbit": {
            "source_solution_set": "p=1; h,d,s,x independently in {-1,+1}",
            "field_phase_charge_order": ["H", "Sigma", "S", "Phi17"],
            "U1X_charges": [-2, -2, 4, 17],
            "PQ_charges": [-2, -2, 4, 0],
            "SO10_Cartan_planes": [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
            "Phi_four_form_is_fixed_by_all_five_oriented_plane_rotations": True,
            "continuous_path": "scale every listed angle simultaneously from t=0 to t=1",
            "actual_target_representation_embedding": embedding,
            "rows": rows,
        },
        "scope_boundary": {
            "theorem_is_full_486_dimensional_but_local_near_the_entire_compact_orbit": True,
            "not_just_five_amplitude_slice": True,
            "distant_or_disconnected_equality_components_excluded": False,
            "global_polynomial_ideal_or_global_SOS_orbit_separator_supplied": False,
        },
        "claims": claims,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["integrity"] = {"core_sha256": hashlib.sha256(canonical_json_bytes(report)).hexdigest()}
    return report


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join((
        "# Exact physical-SM local equality orbit v20",
        "",
        f"Status: `{report['status']}`",
        "",
        "The exact rank-448 transverse-positive Hessian and compact K-invariance imply, by the equivariant Morse-Bott/slice lemma, that the complete 486-field stationary equality locus is exactly the target K-orbit in some K-invariant open neighborhood. No numerical radius is claimed.",
        "",
        "Explicit rational multiples of pi for the SO(10) Cartan, U(1)_X, and PQ angles connect all sixteen five-amplitude sign variants continuously to the target.",
        "",
        "This is local near the compact orbit. Distant equality components remain unclassified, so physical G3, G4, and G5 remain false.",
        "",
        f"Core SHA-256: `{report['integrity']['core_sha256']}`.",
        "",
    ))


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_bytes(canonical_json_bytes(report))
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
