#!/usr/bin/env python3
"""Independent C3/C4 replay of the canonical V50 finite-moose action.

This audit owns no second matrix model. It imports the immutable ACTION_SPEC and
compressed matrices from ``susy_v50_finite_moose_action_spec`` and independently
recomputes the complex-Nambu, variational-domain, quotient-arithmetic, locality
and full-positive-metric certificates. These are abstract finite-matrix facts;
the missing representation maps prevent identification with the full physical
V47/V49 action and force physical C3/C4 to remain partial.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import susy_v50_finite_moose_action_spec as action_spec


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_COMPLEX_NAMBU_REFEREE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_COMPLEX_NAMBU_REFEREE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_complex_nambu_referee_audit.py"
SPEC_PATH = ROOT / "susy_v50_finite_moose_action_spec.py"
STATUS = (
    "V50_CANONICAL_ABSTRACT_FINITE_MATRIX_WITNESS_INDEPENDENTLY_REPLAYED__"
    "EXACT_RATIONAL_UNIFORM_K_BOUND__COMPLEX_HERMITIAN_NAMBU_DOUBLING__"
    "FULL_5303_DIMENSION_POSITIVE_METRIC_AND_5097_DIMENSION_GAUGE_DOMAIN__"
    "ABSTRACT_C3_C4_WITNESS_PASS__PHYSICAL_C3_C4_PARTIAL_NOT_IDENTIFIED__"
    "C5_C7_AND_G2_OPEN"
)

Array = np.ndarray


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def maximum_abs(matrix: Array) -> float:
    value = np.asarray(matrix)
    return float(np.max(np.abs(value))) if value.size else 0.0


def hermitian_residual(matrix: Array) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return maximum_abs(value - value.conjugate().T)


def symmetric_residual(matrix: Array) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return maximum_abs(value - value.T)


def minimum_eigenvalue(matrix: Array) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    if hermitian_residual(value) > 1.0e-10:
        raise ValueError("matrix must be Hermitian")
    return float(np.min(np.linalg.eigvalsh(value)))


def block_diagonal(*blocks: Array) -> Array:
    dimension = sum(block.shape[0] for block in blocks)
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    cursor = 0
    for block in blocks:
        value = np.asarray(block, dtype=np.complex128)
        if value.ndim != 2 or value.shape[0] != value.shape[1]:
            raise ValueError("block-diagonal inputs must be square")
        width = value.shape[0]
        result[cursor : cursor + width, cursor : cursor + width] = value
        cursor += width
    return result


def positive_inverse_square_root(metric: Array) -> Array:
    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(metric, dtype=np.complex128))
    if float(np.min(eigenvalues)) <= 0.0:
        raise ValueError("metric must be positive")
    return eigenvectors @ np.diag(eigenvalues ** -0.5) @ eigenvectors.conjugate().T


def decode_complex_payload(payload: Any) -> Array:
    return np.asarray(
        [[complex(float(item[0]), float(item[1])) for item in row] for row in payload],
        dtype=np.complex128,
    )


def exact_frobenius_square(matrix: Array) -> Fraction:
    total = Fraction(0, 1)
    for item in np.asarray(matrix, dtype=np.complex128).flat:
        total += Fraction.from_float(float(item.real)) ** 2
        total += Fraction.from_float(float(item.imag)) ** 2
    return total


def ceil_sqrt_fraction(value: Fraction, decimal_places: int = 18) -> Fraction:
    """Return a proved decimal upper enclosure of sqrt(value)."""

    if value < 0:
        raise ValueError("square-root input must be nonnegative")
    scale = 10**decimal_places
    numerator = value.numerator * scale * scale
    denominator = value.denominator
    candidate = math.isqrt(numerator // denominator)
    while candidate * candidate * denominator < numerator:
        candidate += 1
    while candidate and (candidate - 1) ** 2 * denominator >= numerator:
        candidate -= 1
    return Fraction(candidate, scale)


def fifth_derivative_blocks(
    matrices: Mapping[str, Any] | None = None,
) -> tuple[Array, Array]:
    frozen = action_spec.compressed_action_matrices() if matrices is None else matrices
    raw = frozen["collar_metadata"]["raw_collar_data"]
    return (
        decode_complex_payload(raw["R7a"]) - decode_complex_payload(raw["R8a"]),
        decode_complex_payload(raw["R7b"]) - decode_complex_payload(raw["R8b"]),
    )


def exact_uniform_K_certificate(
    matrices: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Certify K(t) uniformly with exact rational Frobenius enclosures.

    Canonical metadata rounds real entries to 15 decimal places.  Allowing a
    full 1e-15 per coefficient (twice the ideal decimal rounding error, which
    also covers binary parsing), a difference has entry error <=2e-15 and each
    4x4 Frobenius error is <=8e-15.  Thus 16e-15 covers both blocks used by the
    unrounded action generator.
    """

    delta_even, delta_odd = fifth_derivative_blocks(matrices)
    square_even = exact_frobenius_square(delta_even)
    square_odd = exact_frobenius_square(delta_odd)
    even_upper = ceil_sqrt_fraction(square_even)
    odd_upper = ceil_sqrt_fraction(square_odd)
    serialization_envelope = Fraction(16, 10**15)
    rho_upper = even_upper + odd_upper + serialization_envelope
    lower = Fraction(1, 1) - rho_upper
    spectral_rho = float(np.linalg.norm(delta_even, 2) + np.linalg.norm(delta_odd, 2))
    return {
        "profile": "K(t)=I+sin^2(pi t)(R7a-R8a)+sin(2 pi t)(R7b-R8b)",
        "profile_suprema": {"abs_sin_squared": 1, "abs_sin_double": 1},
        "delta_even_frobenius_square_exact": f"{square_even.numerator}/{square_even.denominator}",
        "delta_odd_frobenius_square_exact": f"{square_odd.numerator}/{square_odd.denominator}",
        "sqrt_upper_decimal_places": 18,
        "serialization_rounding_envelope_exact": f"{serialization_envelope.numerator}/{serialization_envelope.denominator}",
        "rho_upper_exact": f"{rho_upper.numerator}/{rho_upper.denominator}",
        "rho_upper": float(rho_upper),
        "uniform_sigma_min_lower_bound_exact": f"{lower.numerator}/{lower.denominator}",
        "uniform_sigma_min_lower_bound": float(lower),
        "independent_tighter_spectral_norm_bound": 1.0 - spectral_rho,
        "uses_grid_in_proof": False,
        "proof": (
            "For all t and v, ||K(t)v|| >= [1-||Delta_even||_2-"
            "||Delta_odd||_2]||v||. Exact binary-rational Frobenius enclosures "
            "dominate both operator norms, and the serialization envelope covers "
            "the original unrounded generator coefficients."
        ),
        "invertible_for_every_t": lower > 0,
    }


def nambu_pencil(mass: Array, metric: Array) -> tuple[Array, Array]:
    mass_value = np.asarray(mass, dtype=np.complex128)
    metric_value = np.asarray(metric, dtype=np.complex128)
    zero = np.zeros_like(mass_value)
    hamiltonian = np.block([[zero, mass_value.conjugate().T], [mass_value, zero]])
    return hamiltonian, block_diagonal(metric_value.conjugate(), metric_value)


def independent_nambu_certificate(mass: Array, metric: Array) -> dict[str, Any]:
    mass_value = np.asarray(mass, dtype=np.complex128)
    metric_value = np.asarray(metric, dtype=np.complex128)
    hamiltonian, nambu_metric = nambu_pencil(mass_value, metric_value)
    inverse_root = positive_inverse_square_root(nambu_metric)
    canonical = inverse_root @ hamiltonian @ inverse_root
    eigenvalues = np.linalg.eigvalsh(canonical)
    return {
        "chiral_dimension": int(mass_value.shape[0]),
        "Nambu_dimension": int(hamiltonian.shape[0]),
        "M_transpose_symmetry_residual": symmetric_residual(mass_value),
        "M_maximum_imaginary_entry": maximum_abs(np.imag(mass_value)),
        "Z_Hermitian_residual": hermitian_residual(metric_value),
        "Z_minimum_eigenvalue": minimum_eigenvalue(metric_value),
        "H_N_Hermitian_residual": hermitian_residual(hamiltonian),
        "Z_N_Hermitian_residual": hermitian_residual(nambu_metric),
        "Z_N_minimum_eigenvalue": minimum_eigenvalue(nambu_metric),
        "whitened_Hermitian_residual": hermitian_residual(canonical),
        "plus_minus_pairing_residual": float(np.max(np.abs(eigenvalues + eigenvalues[::-1]))),
        "zero_count_at_1e_minus_9": int(np.count_nonzero(np.abs(eigenvalues) < 1.0e-9)),
        "minimum_signed_eigenvalue": float(eigenvalues[0]),
        "maximum_signed_eigenvalue": float(eigenvalues[-1]),
    }


def generalized_hermitian_certificate(stiffness: Array, metric: Array) -> dict[str, Any]:
    stiffness_value = np.asarray(stiffness, dtype=np.complex128)
    metric_value = np.asarray(metric, dtype=np.complex128)
    inverse_root = positive_inverse_square_root(metric_value)
    canonical = inverse_root @ stiffness_value @ inverse_root
    eigenvalues = np.linalg.eigvalsh(canonical)
    positive = eigenvalues[eigenvalues > 1.0e-9]
    return {
        "dimension": int(stiffness_value.shape[0]),
        "stiffness_Hermitian_residual": hermitian_residual(stiffness_value),
        "metric_Hermitian_residual": hermitian_residual(metric_value),
        "metric_minimum_eigenvalue": minimum_eigenvalue(metric_value),
        "whitened_Hermitian_residual": hermitian_residual(canonical),
        "zero_count_at_1e_minus_9": int(np.count_nonzero(np.abs(eigenvalues) < 1.0e-9)),
        "minimum_positive_eigenvalue": float(np.min(positive)) if positive.size else None,
    }


def _rounded_real_gershgorin_bound(matrix: Array) -> Fraction:
    value = np.asarray(matrix, dtype=np.complex128)
    if maximum_abs(np.imag(value)) != 0.0:
        raise ValueError("exact rational Gershgorin helper expects a real matrix")
    candidates: list[Fraction] = []
    for row in range(value.shape[0]):
        diagonal = Fraction(str(float(value[row, row].real)))
        radius = sum(
            abs(Fraction(str(float(value[row, column].real))))
            for column in range(value.shape[1])
            if column != row
        )
        candidates.append(diagonal - radius)
    return min(candidates)


def mixed_kahler_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    norm_metric = decode_complex_payload(
        matrices["collar_metadata"]["raw_collar_data"]["norm_metric"]
    )
    channels = action_spec.N_CHANNELS
    z_h = norm_metric[:channels, :channels]
    mixing = norm_metric[:channels, channels:]
    z_hc = norm_metric[channels:, channels:]
    h_min = minimum_eigenvalue(z_h)
    hc_min = minimum_eigenvalue(z_hc)
    mixing_norm = float(np.linalg.norm(mixing, 2))
    schur_norm_bound = hc_min - mixing_norm**2 / h_min
    exact_schur = z_hc - mixing.conjugate().T @ np.linalg.solve(z_h, mixing)
    rounded_gershgorin = _rounded_real_gershgorin_bound(norm_metric)
    # A conservative 1e-15 error per 8x8 entry gives ||E||_2<=||E||_F<=8e-15.
    unrounded_gershgorin = rounded_gershgorin - Fraction(8, 10**15)
    return {
        "H_block_minimum": h_min,
        "Hc_block_minimum": hc_min,
        "mixed_block_operator_norm": mixing_norm,
        "operator_norm_Schur_lower_bound": schur_norm_bound,
        "exact_Schur_minimum": minimum_eigenvalue(exact_schur),
        "full_metric_minimum": minimum_eigenvalue(norm_metric),
        "rounded_Gershgorin_lower_bound_exact": f"{rounded_gershgorin.numerator}/{rounded_gershgorin.denominator}",
        "unrounded_generator_Gershgorin_lower_bound_exact": f"{unrounded_gershgorin.numerator}/{unrounded_gershgorin.denominator}",
        "unrounded_generator_Gershgorin_lower_bound": float(unrounded_gershgorin),
    }


def full_metric_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    metrics = {
        "collar": np.asarray(matrices["collar_Z"]),
        "source_physical": np.asarray(matrices["source_Z_physical"]),
        "source_gauge_orbit": np.asarray(matrices["source_Z_gauge_orbit"]),
        "gauge_unbroken": np.asarray(matrices["gauge_Z_unbroken"]),
        "gauge_broken": np.asarray(matrices["gauge_Z_broken"]),
        "link": np.asarray(matrices["link_Z"]),
    }
    multiplicities = dict(matrices["sector_multiplicities"])
    spectra = {name: np.linalg.eigvalsh(value) for name, value in metrics.items()}
    sector_dimensions = {
        name: int(len(values) * multiplicities[name]) for name, values in spectra.items()
    }
    full_dimension = sum(sector_dimensions.values())
    positive_count = sum(
        int(np.count_nonzero(values > 0.0)) * multiplicities[name]
        for name, values in spectra.items()
    )
    exact_core_minimum = min(float(np.min(values)) for values in spectra.values())
    representative = block_diagonal(*metrics.values())
    mixed = mixed_kahler_certificate(matrices)
    endpoint = endpoint_auxiliary_certificate(matrices)
    endpoint_gershgorin_minimum = min(
        value
        for side in endpoint["endpoint_unrounded_Gershgorin_lower_bounds"].values()
        for value in side.values()
    )
    if endpoint_gershgorin_minimum <= 0.0:
        raise RuntimeError("endpoint positive additions lack an analytic PSD certificate")
    minimum_weight = min(action_spec.ACTION_SPEC["geometry"]["trapezoid_weights"])
    collar_gershgorin_bound = (
        minimum_weight
        * action_spec.EPSILON
        * mixed["unrounded_generator_Gershgorin_lower_bound"]
    )
    analytic_full_bound = min(
        collar_gershgorin_bound,
        1.0 / (action_spec.N_CELLS + 1),
        1.0 / action_spec.GAUGE_COUPLING**2,
        action_spec.LINK_KAHLER_SCALE**2,
    )
    perturbation_radius = analytic_full_bound / 2.0
    return {
        "sector_dimensions": sector_dimensions,
        "core_minima": {name: float(np.min(values)) for name, values in spectra.items()},
        "full_gauge_fixed_coordinate_dimension": full_dimension,
        "full_positive_eigenvalue_count": positive_count,
        "full_minimum_from_core_spectra": exact_core_minimum,
        "representative_core_dimension": int(representative.shape[0]),
        "representative_minimum_eigenvalue": minimum_eigenvalue(representative),
        "certified_collar_Gershgorin_lower_bound": collar_gershgorin_bound,
        "certified_full_metric_lower_bound": analytic_full_bound,
        "declared_Hermitian_perturbation_ball_radius": perturbation_radius,
        "post_perturbation_lower_bound": analytic_full_bound - perturbation_radius,
        "endpoint_additions_certified_PSD": True,
        "endpoint_unrounded_Gershgorin_minimum": endpoint_gershgorin_minimum,
        "direct_sum_Kronecker_identity": (
            "(Z_collar tensor I16) direct_sum (Z_source_phys tensor I443) "
            "direct_sum (Z_source_gauge tensor I22) direct_sum "
            "(Z_vector_unbroken tensor I24) direct_sum "
            "(Z_vector_broken tensor I22) direct_sum (Z_link tensor I46)"
        ),
        "proof": (
            "The full spectrum is the multiset union of six core spectra with "
            "their frozen multiplicities. Weyl's inequality preserves positivity "
            "throughout the displayed global operator-norm perturbation ball."
        ),
    }


def endpoint_auxiliary_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    mass = np.asarray(matrices["collar_M"])
    metric = np.asarray(matrices["collar_Z"])
    node_width = 2 * action_spec.N_CHANNELS
    node_dimension = (action_spec.N_CELLS + 1) * node_width
    host_aux = slice(node_dimension, node_dimension + 2)
    source_aux = slice(node_dimension + 2, node_dimension + 4)
    interior = slice(node_width, action_spec.N_CELLS * node_width)
    metadata = matrices["collar_metadata"]
    endpoint_minima: dict[str, dict[str, float]] = {}
    endpoint_gershgorin: dict[str, dict[str, float]] = {}
    endpoint_gershgorin_exact: dict[str, dict[str, str]] = {}
    for side in ("host_endpoint", "source_endpoint"):
        endpoint_minima[side] = {
            name: minimum_eigenvalue(decode_complex_payload(metadata[side][name]))
            for name in ("Z", "W")
        }
        endpoint_gershgorin[side] = {}
        endpoint_gershgorin_exact[side] = {}
        for name in ("Z", "W"):
            value = decode_complex_payload(metadata[side][name])
            # n-by-n payload, conservative 1e-15 per entry: ||E||_F<=n e-15.
            certified = _rounded_real_gershgorin_bound(value) - Fraction(
                value.shape[0], 10**15
            )
            endpoint_gershgorin[side][name] = float(certified)
            endpoint_gershgorin_exact[side][name] = (
                f"{certified.numerator}/{certified.denominator}"
            )
    return {
        "collar_dimension": int(mass.shape[0]),
        "node_dimension": node_dimension,
        "retained_auxiliary_dimension": int(mass.shape[0] - node_dimension),
        "auxiliary_metric_minimum": minimum_eigenvalue(metric[node_dimension:, node_dimension:]),
        "host_auxiliary_coupling_norm": float(np.linalg.norm(mass[host_aux, :node_width], 2)),
        "source_auxiliary_coupling_norm": float(
            np.linalg.norm(mass[source_aux, action_spec.N_CELLS * node_width : node_dimension], 2)
        ),
        "auxiliary_to_interior_maximum": max(
            maximum_abs(mass[host_aux, interior]), maximum_abs(mass[source_aux, interior])
        ),
        "endpoint_positive_metric_minima": endpoint_minima,
        "endpoint_unrounded_Gershgorin_lower_bounds": endpoint_gershgorin,
        "endpoint_unrounded_Gershgorin_lower_bounds_exact": endpoint_gershgorin_exact,
        "domain_statement": (
            "Four endpoint auxiliaries remain coordinates of the 44x44 collar "
            "Hessian; endpoint equations are variational rows and rational pencils "
            "arise only after optional Schur elimination."
        ),
    }


def locality_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    node_width = 2 * action_spec.N_CHANNELS
    node_dimension = (action_spec.N_CELLS + 1) * node_width
    collar = np.asarray(matrices["collar_M"])
    violations = 0
    for left in range(action_spec.N_CELLS + 1):
        for right in range(action_spec.N_CELLS + 1):
            if abs(left - right) <= 1:
                continue
            block = collar[
                left * node_width : (left + 1) * node_width,
                right * node_width : (right + 1) * node_width,
            ]
            violations += int(maximum_abs(block) > 1.0e-13)
    auxiliary_to_bulk_interior = maximum_abs(
        collar[node_dimension:, node_width : action_spec.N_CELLS * node_width]
    )
    source = np.asarray(matrices["source_M_physical"])
    nodes = action_spec.N_CELLS + 1
    source_cross_nonzero = int(np.count_nonzero(np.abs(source[:nodes, nodes:]) > 1.0e-13))
    return {
        "collar_non_nearest_neighbour_violations": violations,
        "endpoint_auxiliary_to_bulk_interior_maximum": auxiliary_to_bulk_interior,
        "source_XP_cross_nonzero_count": source_cross_nonzero,
        "source_XP_expected_incidence_nonzero_count": 2 * action_spec.N_CELLS,
        "all_fundamental_terms_site_or_nearest_neighbour": (
            violations == 0
            and auxiliary_to_bulk_interior < 1.0e-13
            and source_cross_nonzero == 2 * action_spec.N_CELLS
        ),
    }


def gauge_domain_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    source_gauge = independent_nambu_certificate(
        matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]
    )
    unbroken = generalized_hermitian_certificate(
        matrices["gauge_L_unbroken"], matrices["gauge_Z_unbroken"]
    )
    broken = generalized_hermitian_certificate(
        matrices["gauge_L_broken"], matrices["gauge_Z_broken"]
    )
    link = generalized_hermitian_certificate(matrices["link_L"], matrices["link_Z"])
    full_fixed = full_metric_certificate(matrices)["full_gauge_fixed_coordinate_dimension"]
    removed_source = action_spec.SOURCE_GAUGE_ORBIT_COMPONENTS
    removed_links = action_spec.N_CELLS * action_spec.GAUGE_DIMENSION
    return {
        "source_gauge_profile_Nambu_zero_count": source_gauge["zero_count_at_1e_minus_9"],
        "unbroken_vector": unbroken,
        "broken_vector": broken,
        "link_Rxi": link,
        "removed_source_gauge_orbit_profiles": removed_source,
        "removed_link_Goldstones": removed_links,
        "full_gauge_fixed_dimension": full_fixed,
        "full_gauge_reduced_dimension": full_fixed - removed_source - removed_links,
        "abstract_unbroken_vector_zero_mode_multiplicity": action_spec.UNBROKEN_GAUGE_DIMENSION,
        "quotient_proof": (
            "For any chosen 22-plus-184-dimensional subspace, its metric-orthogonal "
            "complement inherits strict positivity. The arithmetic dimension is "
            "5097; identifying that subspace with the physical gauge-orbit image "
            "requires the missing explicit orbit map and coupled Goldstone block."
        ),
    }


def combined_operator_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    chiral_pairs = [
        nambu_pencil(matrices["collar_M"], matrices["collar_Z"]),
        nambu_pencil(matrices["source_M_physical"], matrices["source_Z_physical"]),
        nambu_pencil(matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]),
    ]
    operators = [pair[0] for pair in chiral_pairs] + [
        np.asarray(matrices["gauge_L_unbroken"]),
        np.asarray(matrices["gauge_L_broken"]),
        np.asarray(matrices["link_L"]),
    ]
    metrics = [pair[1] for pair in chiral_pairs] + [
        np.asarray(matrices["gauge_Z_unbroken"]),
        np.asarray(matrices["gauge_Z_broken"]),
        np.asarray(matrices["link_Z"]),
    ]
    operator = block_diagonal(*operators)
    metric = block_diagonal(*metrics)
    inverse_root = positive_inverse_square_root(metric)
    whitened = inverse_root @ operator @ inverse_root
    return {
        "representative_pencil_dimension": int(operator.shape[0]),
        "operator_Hermitian_residual": hermitian_residual(operator),
        "metric_Hermitian_residual": hermitian_residual(metric),
        "metric_minimum_eigenvalue": minimum_eigenvalue(metric),
        "whitened_operator_Hermitian_residual": hermitian_residual(whitened),
        "operator_contract": (
            "direct sum of complex chiral Nambu pencils and transverse/Rxi "
            "gauge-link pencils, all derived from the canonical finite action"
        ),
    }


def shared_action_fingerprint_certificate() -> dict[str, Any]:
    action_spec.assert_matrix_fingerprint(action_spec.compressed_action_matrices())
    independent_hash = hashlib.sha256(action_spec.canonical_action_bytes()).hexdigest()
    return {
        "canonical_module_sha256": action_spec.SHARED_ACTION_SHA256,
        "independent_canonical_bytes_sha256": independent_hash,
        "canonical_hash_matches_independent_bytes": (
            action_spec.SHARED_ACTION_SHA256 == independent_hash
        ),
        "canonical_schema": action_spec.ACTION_SPEC["schema"],
        "matrix_fingerprints_recomputed": True,
        "external_certificate_dependency": None,
    }


def build_report() -> dict[str, Any]:
    matrices = action_spec.compressed_action_matrices()
    action_spec.assert_matrix_fingerprint(matrices)
    fingerprint = shared_action_fingerprint_certificate()
    uniform_k = exact_uniform_K_certificate(matrices)
    collar_nambu = independent_nambu_certificate(matrices["collar_M"], matrices["collar_Z"])
    source_physical_nambu = independent_nambu_certificate(
        matrices["source_M_physical"], matrices["source_Z_physical"]
    )
    source_gauge_nambu = independent_nambu_certificate(
        matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]
    )
    metric = full_metric_certificate(matrices)
    mixed = mixed_kahler_certificate(matrices)
    endpoint = endpoint_auxiliary_certificate(matrices)
    locality = locality_certificate(matrices)
    gauge = gauge_domain_certificate(matrices)
    combined = combined_operator_certificate(matrices)

    checks = {
        "canonical_action_hash_matches_independent_bytes": fingerprint[
            "canonical_hash_matches_independent_bytes"
        ],
        "canonical_spec_fail_closes_physical_identification": (
            action_spec.ACTION_SPEC["physical_identification_status"]["status"]
            == "OPEN_NOT_A_V47_V49_SAME_ACTION_CERTIFICATE"
            and len(
                action_spec.ACTION_SPEC["physical_identification_status"]["missing_maps"]
            )
            == 5
        ),
        "all_named_collar_blocks_are_present": all(
            max(matrices["collar_metadata"]["block_spectral_norms"][name]) > 0.0
            for name in ("A", "Xi", "C", "R7", "R8", "Z")
        ),
        "exact_uniform_K_bound_positive_without_grid": (
            uniform_k["invertible_for_every_t"]
            and not uniform_k["uses_grid_in_proof"]
            and uniform_k["uniform_sigma_min_lower_bound"] > 0.9
        ),
        "collar_M_complex_symmetric_and_Nambu_Hermitian": (
            collar_nambu["M_transpose_symmetry_residual"] < 1.0e-12
            and collar_nambu["M_maximum_imaginary_entry"] > 1.0e-6
            and max(
                collar_nambu["H_N_Hermitian_residual"],
                collar_nambu["Z_N_Hermitian_residual"],
                collar_nambu["whitened_Hermitian_residual"],
            ) < 1.0e-10
        ),
        "both_source_Nambu_pencils_Hermitian_and_paired": max(
            source_physical_nambu["M_transpose_symmetry_residual"],
            source_physical_nambu["H_N_Hermitian_residual"],
            source_physical_nambu["plus_minus_pairing_residual"],
            source_gauge_nambu["M_transpose_symmetry_residual"],
            source_gauge_nambu["H_N_Hermitian_residual"],
            source_gauge_nambu["plus_minus_pairing_residual"],
        ) < 1.0e-9,
        "one_combined_action_operator_is_self_adjoint": max(
            combined["operator_Hermitian_residual"],
            combined["metric_Hermitian_residual"],
            combined["whitened_operator_Hermitian_residual"],
        ) < 1.0e-10 and combined["metric_minimum_eigenvalue"] > 0.0,
        "full_5303_metric_strictly_positive": (
            metric["full_gauge_fixed_coordinate_dimension"] == 5303
            and metric["full_positive_eigenvalue_count"] == 5303
            and metric["certified_full_metric_lower_bound"] > 0.0
            and metric["post_perturbation_lower_bound"] > 0.0
        ),
        "mixed_Kahler_Schur_and_Gershgorin_bounds_positive": (
            mixed["operator_norm_Schur_lower_bound"] > 0.0
            and mixed["exact_Schur_minimum"] > 0.0
            and mixed["unrounded_generator_Gershgorin_lower_bound"] > 0.0
        ),
        "endpoint_auxiliaries_retained_in_same_positive_domain": (
            endpoint["collar_dimension"] == 44
            and endpoint["retained_auxiliary_dimension"] == 4
            and endpoint["auxiliary_metric_minimum"] > 0.0
            and endpoint["host_auxiliary_coupling_norm"] > 0.0
            and endpoint["source_auxiliary_coupling_norm"] > 0.0
            and min(
                value
                for side in endpoint["endpoint_unrounded_Gershgorin_lower_bounds"].values()
                for value in side.values()
            ) > 0.0
        ),
        "fundamental_action_is_finite_and_nearest_neighbour": locality[
            "all_fundamental_terms_site_or_nearest_neighbour"
        ],
        "candidate_quotient_arithmetic_and_abstract_zero_modes_exact": (
            gauge["full_gauge_reduced_dimension"] == 5097
            and gauge["source_gauge_profile_Nambu_zero_count"] == 2
            and gauge["unbroken_vector"]["zero_count_at_1e_minus_9"] == 1
            and gauge["broken_vector"]["zero_count_at_1e_minus_9"] == 0
            and gauge["link_Rxi"]["zero_count_at_1e_minus_9"] == 0
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V50 canonical referee replay failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v50-complex-nambu-referee-audit-v2",
        "status": STATUS,
        "shared_action_sha256": action_spec.SHARED_ACTION_SHA256,
        "canonical_action_fingerprint": fingerprint,
        "canonical_action_contract": action_spec.action_manifest(),
        "scientific_scope": (
            "One frozen finite-N abstract numerical quadratic witness with a "
            "positive Kahler metric. Its matrix theorems are proved, but it has not "
            "been pulled back from the physical V47/V49 representation-level action."
        ),
        "exact_uniform_fifth_derivative_certificate": uniform_k,
        "action_derived_operator_and_C3": {
            "finite_variational_domain": (
                "All site X/P, collar H/Hc, four endpoint auxiliaries, transverse "
                "site vectors and separate R_xi link coordinates in the abstract "
                "matrix model; a candidate positive-metric quotient has dimension 5097."
            ),
            "variation_statement": (
                "Every endpoint equation is a row of the canonical finite Hessian; "
                "no mass-dependent Schur complement is used as a boundary domain."
            ),
            "Green_identity": (
                "For the combined Hermitian pencil, u^dagger H v-(H u)^dagger v=0; "
                "endpoint rows cancel finite summation-by-parts terms."
            ),
            "collar_complex_Nambu": collar_nambu,
            "source_443_candidate_complex_Nambu": source_physical_nambu,
            "source_gauge_complex_Nambu": source_gauge_nambu,
            "combined_representative": combined,
            "endpoint_auxiliaries": endpoint,
            "locality": locality,
            "gauge_reduction": gauge,
        },
        "full_positive_metric_and_C4": {
            "direct_sum_Kronecker_certificate": metric,
            "mixed_Kahler_certificate": mixed,
            "positive_cone_scope": (
                "The displayed global Hermitian operator-norm ball applies to "
                "simultaneous source/coefficient perturbations of the complete "
                "kinetic matrix; outside coefficients are not certified."
            ),
        },
        "physical_identification_obstructions": [
            {
                "id": "V47_HESSIAN_PULLBACK",
                "missing_datum": (
                    "An explicit representation-respecting pullback proving that the "
                    "abstract 0.31 I_443 plus 0 I_22 endpoint Hessian and Kahler block "
                    "equal the retained V47 source Hessian."
                ),
                "impact": "The 443/22 source blocks are witnesses, not yet the physical V47 blocks.",
            },
            {
                "id": "GAUGE_ORBIT_PROJECTOR",
                "missing_datum": (
                    "The actual 465x22 infinitesimal orbit map, its rank-22 proof, "
                    "the Z-orthogonal projector, and equality of its image with the "
                    "quadratic Hessian kernel."
                ),
                "impact": "5097 is certified arithmetic, not a certified physical quotient dimension.",
            },
            {
                "id": "COUPLED_RXI_GOLDSTONE_BLOCK",
                "missing_datum": (
                    "The endpoint source Goldstone/link-Goldstone mixing that yields "
                    "the five-mode broken-generator R_xi Goldstone matrix."
                ),
                "impact": "The separate link and endpoint blocks are not a complete physical R_xi realization.",
            },
            {
                "id": "ENDPOINT_AUXILIARY_REPRESENTATIONS",
                "missing_datum": (
                    "Spin(10)xU(1)_F representations, charges, and vectorlike/anomaly "
                    "pairing for all four positive-metric endpoint auxiliary fields."
                ),
                "impact": "Their positive 64-coordinate lift cannot yet be identified with an anomaly-safe physical sector.",
            },
            {
                "id": "V49_INVARIANT_TENSOR_LIFT",
                "missing_datum": (
                    "Normalized SO(10) invariant tensors/copy maps for A, Xi, C, "
                    "R7, R8 and Z, plus a covariant midpoint in one site frame."
                ),
                "impact": "The random four-channel blocks tensored with I_16 are not proved to lie in the physical V49 invariant image.",
            },
        ],
        "clause_decision": {
            "abstract_finite_matrix_C3_witness": "PASS",
            "abstract_finite_matrix_C4_witness": "PASS",
            "C3_physical_same_action_domain_and_self_adjointness": (
                "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
            ),
            "C4_physical_full_kinetic_positivity": (
                "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
            ),
            "C5_counterterm_and_profile_matching": "REMAINS_PARTIAL",
            "C7_component_Wilson_matching": "REMAINS_PARTIAL",
            "G2_closed": False,
            "gates_promoted": [],
        },
        "scope_boundary": [
            "The finite N=4 matrix model is an abstract witness, not yet the declared physical regulator action.",
            "Its positivity theorem covers the frozen point and explicit open ball, not arbitrary Kahler coefficients.",
            "C5 still lacks a full affine/source-functional loop and finite-threshold rematch under fixed renormalization conditions.",
            "C7 still lacks the normalized physical component tensor/Wilson incidence array.",
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "provenance": {
            "canonical_spec_file": SPEC_PATH.name,
            "canonical_spec_file_sha256": sha256_file(SPEC_PATH),
            "test_file": TEST_PATH.name,
            "test_file_sha256": sha256_file(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    if report["shared_action_sha256"] != action_spec.action_fingerprint():
        raise RuntimeError("canonical action hash drifted")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity checks failed")
    decision = report["clause_decision"]
    if decision["abstract_finite_matrix_C3_witness"] != "PASS":
        raise RuntimeError("abstract C3 witness decision drifted")
    if decision["abstract_finite_matrix_C4_witness"] != "PASS":
        raise RuntimeError("abstract C4 witness decision drifted")
    if decision["C3_physical_same_action_domain_and_self_adjointness"] != (
        "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
    ):
        raise RuntimeError("physical C3 must remain fail-closed")
    if decision["C4_physical_full_kinetic_positivity"] != (
        "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
    ):
        raise RuntimeError("physical C4 must remain fail-closed")
    if len(report["physical_identification_obstructions"]) != 5:
        raise RuntimeError("physical identification blockers drifted")
    if decision["G2_closed"] or decision["gates_promoted"]:
        raise RuntimeError("this audit cannot close/promote G2")


def render_markdown(report: Mapping[str, Any]) -> str:
    fingerprint = report["canonical_action_fingerprint"]
    uniform = report["exact_uniform_fifth_derivative_certificate"]
    c3 = report["action_derived_operator_and_C3"]
    collar = c3["collar_complex_Nambu"]
    gauge = c3["gauge_reduction"]
    endpoint = c3["endpoint_auxiliaries"]
    metric = report["full_positive_metric_and_C4"]["direct_sum_Kronecker_certificate"]
    mixed = report["full_positive_metric_and_C4"]["mixed_Kahler_certificate"]
    return f"""# V50 canonical complex-Nambu referee replay

Status: `{report['status']}`

## Strict verdict

The independent replay uses only canonical ACTION_SPEC bytes with hash
`{report['shared_action_sha256']}`. The independently recomputed byte hash
agrees: `{fingerprint['canonical_hash_matches_independent_bytes']}`.

- **Abstract finite-matrix C3/C4 witness:** `PASS`.
- **Physical V47/V49 C3/C4:** `PARTIAL_NOT_PHYSICALLY_IDENTIFIED`.
- **C5/C7:** remain partial; therefore **G2 remains open**.

The numerical Hessian, metric and quotient arithmetic are internally sound,
but five missing representation-level maps prevent promotion to the physical
theory: the V47 Hessian pullback, the 465x22 orbit projector, the coupled
endpoint/link Rxi Goldstone block, endpoint-auxiliary representation/anomaly
assignments, and the normalized V49 invariant-tensor/covariant-midpoint lift.

## Uniform derivative chart—no grid premise

For every real `t`,

```text
K(t)=I+sin^2(pi t) Delta_even+sin(2 pi t) Delta_odd,
sigma_min K(t) >= {uniform['uniform_sigma_min_lower_bound']:.12f} > 0.
```

The bound uses exact binary-rational Frobenius enclosures plus the full
serialization envelope. The tighter spectral-norm cross-check is
`{uniform['independent_tighter_spectral_norm_bound']:.12f}`; neither uses a
grid in the proof.

## Abstract C3 witness

The collar Hessian is 44-dimensional: 40 node coordinates plus all
{endpoint['retained_auxiliary_dimension']} endpoint auxiliaries. Their metric
minimum is `{endpoint['auxiliary_metric_minimum']:.9g}` and both endpoint
couplings are nonzero. Endpoint equations are rows of this same matrix.

For genuinely complex symmetric `M`, the replay constructs

```text
H_N = [[0,M^dagger],[M,0]],   Z_N = diag(Z*,Z).
```

The collar Nambu dimension is {collar['Nambu_dimension']}; its maximum
imaginary mass entry is `{collar['M_maximum_imaginary_entry']:.6g}`. The
Hermiticity residuals of `H_N` and its whitened operator are
`{collar['H_N_Hermitian_residual']:.3e}` and
`{collar['whitened_Hermitian_residual']:.3e}`; signed masses pair to
`{collar['plus_minus_pairing_residual']:.3e}`.

The same test covers the candidate 443- and 22-component `X/P` blocks.
Gauge/link pencils are Hermitian separately. Removing
{gauge['removed_source_gauge_orbit_profiles']} candidate source directions and
{gauge['removed_link_Goldstones']} link coordinates leaves the arithmetic
**{gauge['full_gauge_reduced_dimension']}-coordinate** positive complement.
Without the explicit orbit map and coupled Goldstone block, this is not yet a
physical gauge quotient.

## Abstract C4 witness

The exact direct-sum/Kronecker lift has
**{metric['full_gauge_fixed_coordinate_dimension']} coordinates**:

```text
collar x16:           {metric['sector_dimensions']['collar']}
source candidate x443:{metric['sector_dimensions']['source_physical']}
source orbit x22:     {metric['sector_dimensions']['source_gauge_orbit']}
vectors unbroken x24: {metric['sector_dimensions']['gauge_unbroken']}
vectors broken x22:   {metric['sector_dimensions']['gauge_broken']}
links x46:            {metric['sector_dimensions']['link']}
```

All {metric['full_positive_eigenvalue_count']} lifted eigenvalues are positive.
The exact-core numerical minimum is `{metric['full_minimum_from_core_spectra']:.9g}`;
an independent rational Gershgorin/direct-sum proof gives
`{metric['certified_full_metric_lower_bound']:.9g}`. The retained mixed H/Hc
Kähler block has Schur lower bound `{mixed['operator_norm_Schur_lower_bound']:.9g}`.

Positivity persists for simultaneous Hermitian source/coefficient perturbations
of operator norm at most `{metric['declared_Hermitian_perturbation_ball_radius']:.9g}`,
leaving lower bound `{metric['post_perturbation_lower_bound']:.9g}`.

This is an abstract fixed-cutoff, tree-level quadratic theorem. It does not yet
establish the physical V47/V49 same-action domain or kinetic form, assert a
continuum limit, supply the C5 loop rematch, or construct the C7 component array.

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V50 complex-Nambu artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V50 complex-Nambu JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V50 complex-Nambu Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
