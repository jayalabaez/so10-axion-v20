#!/usr/bin/env python3
"""Exact bounded Pati--Salam vacuum in the complete real-210 self potential.

The complete real-210 basis permits a rigorous sum-of-projectors potential.
Let I_kappa=||P_kappa(Phi tensor Phi)||^2 for the eight distinct pair-Casimir
eigenspaces of Sym^2(210).  They are nonnegative and

    sum_kappa I_kappa = (Phi dagger Phi)^2 = J0.

Choose spectral weights

    beta = 1 on 1,54,(770+1050+1050bar),4125,8910,
    beta = 2 on 45,210,5940.

Then

    Q(Phi) = sum beta_kappa I_kappa
           = J0 + I_45 + I_210 + I_5940 >= J0.

For the normalized Pati--Salam singlet P=e6789, the three extra projectors
vanish exactly, so Q(P)=1.  Therefore, for any v>0,

    V(Phi) = -2 v^2 I2(Phi) + Q(Phi)
           >= (I2(Phi)-v^2)^2 - v^4.

Phi=v P saturates the global lower bound.  P is invariant under
SO(6)xSO(4) ~= SU(4)_C x SU(2)_L x SU(2)_R, so this is an exact first-stage
Pati--Salam vacuum.

The full 210x210 Cartesian Hessian is calculated analytically from the pair
Casimir moments.  At v=1/2 its spectrum is

    0       x 24   (broken SO(10)/[SO(6)xSO(4)] generators),
    2/9     x 90,
    3/8     x 80,
    3/5     x 15,
    2       x 1.

For general v all nonzero eigenvalues are multiplied by 4 v^2.  Thus the
210-only physical Hessian is positive after quotienting the 24 Goldstones.
This does not prove the complete multi-field v20 vacuum or threshold spectrum.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_self_invariant_basis_v20 as self210
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_210_PATI_SALAM_GLOBAL_VACUUM_V20.json"
OUT_MD = ROOT / "EXACT_210_PATI_SALAM_GLOBAL_VACUUM_V20.md"

SPECTRAL_WEIGHTS: dict[str, Fraction] = {
    "1": Fraction(1),
    "45": Fraction(2),
    "54": Fraction(1),
    "210": Fraction(2),
    "770_plus_1050_plus_1050bar": Fraction(1),
    "4125": Fraction(1),
    "5940": Fraction(2),
    "8910": Fraction(1),
}
EXTRA_POSITIVE_CHANNELS = ("45", "210", "5940")
EXPECTED_J_COUPLINGS = {
    "J0": Fraction(-21, 200),
    "J2": Fraction(2467, 28800),
    "J3": Fraction(-77, 3200),
    "J4": Fraction(119, 115200),
}


def quartic_couplings() -> dict[str, Fraction]:
    spectral = self210.spectral_quartics_in_basis()
    values = [Fraction(0) for _ in range(4)]
    for name, weight in SPECTRAL_WEIGHTS.items():
        rows = spectral[name]
        for index in range(4):
            values[index] += weight * rows[index]
    return dict(zip(self210.QUARTIC_BASIS_NAMES, values))


def quartic_value(phi: direct.Form) -> float:
    invariants = self210.quartic_invariants(phi)
    couplings = quartic_couplings()
    return float(
        sum(float(couplings[name]) * invariants[name] for name in couplings)
    )


def potential(phi: direct.Form, *, v: float) -> float:
    return float(
        -2.0 * float(v) ** 2 * self210.quadratic_invariant(phi)
        + quartic_value(phi)
    )


@lru_cache(maxsize=1)
def pair_casimir_sparse() -> sparse.csr_matrix:
    dimension = 210 * 210
    return sum(
        (
            sparse.kron(generator, generator, format="csr")
            for generator in projectors.generator_matrices()
        ),
        sparse.csr_matrix((dimension, dimension), dtype=float),
    )


def quartic_differentials(
    vector: np.ndarray,
) -> dict[str, dict[str, np.ndarray | float]]:
    """Values, gradients and Hessians for J0,J2,J3,J4."""
    phi = np.asarray(vector, dtype=float)
    if phi.shape != (210,):
        raise ValueError("expected 210 real components")
    degrees = (0, 2, 3, 4)
    pair = np.outer(phi, phi)
    operator = pair_casimir_sparse()

    pair_powers: dict[int, np.ndarray] = {0: pair.copy()}
    current_pair = pair.copy()
    for degree in range(1, 5):
        current_pair = (
            operator @ current_pair.reshape(-1)
        ).reshape(210, 210)
        if degree in degrees:
            pair_powers[degree] = current_pair.copy()

    identity = np.eye(210)
    variations = (
        np.einsum("ik,j->ijk", identity, phi)
        + np.einsum("i,jk->ijk", phi, identity)
    ).reshape(210 * 210, 210)
    variation_powers: dict[int, np.ndarray] = {0: variations.copy()}
    current_variations = variations
    for degree in range(1, 5):
        current_variations = operator @ current_variations
        if degree in degrees:
            variation_powers[degree] = current_variations.copy()

    result: dict[str, dict[str, np.ndarray | float]] = {}
    for name, degree in zip(self210.QUARTIC_BASIS_NAMES, degrees):
        background_pair = pair_powers[degree]
        variation_tensor = variation_powers[degree].reshape(210, 210, 210)
        response = np.einsum("ijk,j->ik", variation_tensor, phi)
        hessian = 4.0 * (background_pair + response)
        hessian = 0.5 * (hessian + hessian.T)
        result[name] = {
            "value": float(np.sum(pair * background_pair)),
            "gradient": 4.0 * background_pair @ phi,
            "hessian": hessian,
        }
    return result


def potential_gradient_hessian(
    vector: np.ndarray, *, v: float
) -> tuple[float, np.ndarray, np.ndarray]:
    phi = np.asarray(vector, dtype=float)
    rows = quartic_differentials(phi)
    couplings = quartic_couplings()
    mass_sq = -4.0 * float(v) ** 2
    value = 0.5 * mass_sq * float(phi @ phi)
    gradient = mass_sq * phi
    hessian = mass_sq * np.eye(210)
    for name in self210.QUARTIC_BASIS_NAMES:
        coefficient = float(couplings[name])
        value += coefficient * float(rows[name]["value"])
        gradient += coefficient * np.asarray(rows[name]["gradient"])
        hessian += coefficient * np.asarray(rows[name]["hessian"])
    return float(value), gradient, 0.5 * (hessian + hessian.T)


def pati_salam_direction() -> tuple[direct.Form, np.ndarray]:
    form = self210.singlet_form(1.0, 0.0, 0.0)
    return form, self210.phi_vector(form)


def exact_p_spectral_values() -> dict[str, Fraction]:
    _, vector = pati_salam_direction()
    integer_vector = np.rint(vector).astype(np.int64)
    if np.max(np.abs(vector - integer_vector)) > 1.0e-12:
        raise AssertionError("P direction is not an integral four-form basis state")
    moments = self210.integer_pair_moments(integer_vector)
    values: dict[str, Fraction] = {}
    for name, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items():
        polynomial = projectors.projector_polynomial(eigenvalue)
        values[name] = sum(
            polynomial[degree] * moments[degree]
            for degree in range(8)
        )
    return values


def generator_stabilizer_audit(vector: np.ndarray) -> dict[str, Any]:
    unbroken: list[str] = []
    broken: list[str] = []
    tangents: list[np.ndarray] = []
    pattern_mismatches: list[str] = []
    for label, generator in zip(
        projectors.GENERATOR_LABELS,
        projectors.generator_matrices(),
    ):
        tangent = np.asarray(generator @ vector).reshape(-1)
        name = f"M{label[0]}{label[1]}"
        is_unbroken = float(np.linalg.norm(tangent)) < 1.0e-12
        expected_unbroken = (
            (label[0] < 6 and label[1] < 6)
            or (label[0] >= 6 and label[1] >= 6)
        )
        if is_unbroken:
            unbroken.append(name)
        else:
            broken.append(name)
            tangents.append(tangent)
        if is_unbroken != expected_unbroken:
            pattern_mismatches.append(name)
    tangent_matrix = np.column_stack(tangents)
    singular_values = np.linalg.svd(tangent_matrix, compute_uv=False)
    rank = int(np.sum(singular_values > 1.0e-10))
    return {
        "unbroken_generator_count": len(unbroken),
        "broken_generator_count": len(broken),
        "broken_orbit_rank": rank,
        "unbroken_generators": unbroken,
        "broken_generators": broken,
        "pattern_mismatches": pattern_mismatches,
        "minimum_nonzero_tangent_singular_value": float(
            singular_values[rank - 1]
        ),
        "group_identification": "SO(6)xSO(4) ~= SU(4)_C x SU(2)_L x SU(2)_R",
    }


def eigenvalue_clusters(
    eigenvalues: np.ndarray, tolerance: float = 1.0e-9
) -> list[dict[str, float | int]]:
    clusters: list[dict[str, float | int]] = []
    for value in np.asarray(eigenvalues, dtype=float):
        for cluster in clusters:
            if abs(value - float(cluster["eigenvalue"])) < tolerance:
                cluster["multiplicity"] = int(cluster["multiplicity"]) + 1
                break
        else:
            clusters.append({
                "eigenvalue": float(value),
                "multiplicity": 1,
            })
    return clusters


def build_report() -> dict[str, Any]:
    couplings = quartic_couplings()
    spectral_p = exact_p_spectral_values()
    p_form, p_vector = pati_salam_direction()
    p_quartic = quartic_value(p_form)
    spectral_sum = sum(spectral_p.values())
    extra_at_p = {
        name: spectral_p[name] for name in EXTRA_POSITIVE_CHANNELS
    }

    benchmark_v = 0.5
    vacuum_vector = benchmark_v * p_vector
    vacuum_form = direct.scale_form(p_form, benchmark_v)
    value, gradient, hessian = potential_gradient_hessian(
        vacuum_vector, v=benchmark_v
    )
    eigenvalues = np.linalg.eigvalsh(hessian)
    clusters = eigenvalue_clusters(eigenvalues)
    stabilizer = generator_stabilizer_audit(vacuum_vector)
    broken_tangents = np.column_stack([
        np.asarray(generator @ vacuum_vector).reshape(-1)
        for generator in projectors.generator_matrices()
        if np.linalg.norm(generator @ vacuum_vector) >= 1.0e-12
    ])
    goldstone_residual = float(np.max(np.abs(hessian @ broken_tangents)))
    zero_count = int(np.sum(np.abs(eigenvalues) < 1.0e-9))
    negative_count = int(np.sum(eigenvalues < -1.0e-9))
    physical = eigenvalues[eigenvalues > 1.0e-9]

    expected_clusters = (
        (0.0, 24),
        (2.0 / 9.0, 90),
        (3.0 / 8.0, 80),
        (3.0 / 5.0, 15),
        (2.0, 1),
    )
    cluster_residual = 0.0
    cluster_multiplicity_ok = len(clusters) == len(expected_clusters)
    if cluster_multiplicity_ok:
        for observed, (expected_value, expected_multiplicity) in zip(
            clusters, expected_clusters
        ):
            cluster_residual = max(
                cluster_residual,
                abs(float(observed["eigenvalue"]) - expected_value),
            )
            cluster_multiplicity_ok &= (
                int(observed["multiplicity"]) == expected_multiplicity
            )

    # The exact global lower bound is V >= -v^4.
    global_lower_bound = -benchmark_v**4
    checks = {
        "quartic_couplings_match_exact_fractions": couplings == EXPECTED_J_COUPLINGS,
        "spectral_projectors_sum_to_unit_norm_at_P": spectral_sum == Fraction(1),
        "extra_positive_channels_vanish_at_P": all(
            value == 0 for value in extra_at_p.values()
        ),
        "P_quartic_saturates_J0_bound": abs(p_quartic - 1.0) < 1.0e-12,
        "global_bound_saturated": abs(value - global_lower_bound) < 1.0e-12,
        "vacuum_gradient_zero": float(np.max(np.abs(gradient))) < 1.0e-10,
        "unbroken_generators_are_SO6_plus_SO4": stabilizer[
            "unbroken_generator_count"
        ]
        == 21
        and not stabilizer["pattern_mismatches"],
        "broken_orbit_has_24_generators": stabilizer[
            "broken_generator_count"
        ]
        == 24
        and stabilizer["broken_orbit_rank"] == 24,
        "exactly_24_Goldstones": zero_count == 24,
        "Goldstones_align_with_broken_generators": goldstone_residual < 1.0e-10,
        "no_tachyonic_210_modes": negative_count == 0,
        "all_physical_210_modes_positive": len(physical) == 186
        and float(physical[0]) > 0.0,
        "exact_Hessian_clusters": cluster_multiplicity_ok
        and cluster_residual < 1.0e-10,
        "multi_field_vacuum_not_claimed": True,
        "full_model_thresholds_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_210_PATI_SALAM_GLOBAL_VACUUM_AND_HESSIAN"
            if not failures
            else "EXACT_210_PATI_SALAM_VACUUM_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "potential_convention": {
            "formula": "V=-2 v^2 I2 + Q",
            "Q": "J0+I45+I210+I5940",
            "global_identity": "V >= (I2-v^2)^2-v^4",
            "spectral_weights": {
                name: str(value) for name, value in SPECTRAL_WEIGHTS.items()
            },
            "J_basis_couplings": {
                name: str(value) for name, value in couplings.items()
            },
        },
        "exact_global_proof": {
            "all_spectral_invariants_nonnegative": True,
            "sum_spectral_invariants_equals_J0": True,
            "P_spectral_values": {
                name: str(value) for name, value in spectral_p.items()
            },
            "extra_positive_channels_at_P": {
                name: str(value) for name, value in extra_at_p.items()
            },
            "global_minimum_radius": "I2=v^2",
            "global_minimum_value": "-v^4",
            "uniqueness_of_global_orbit": False,
        },
        "symmetry_breaking": stabilizer,
        "full_210_Hessian": {
            "benchmark_v": benchmark_v,
            "vacuum": "Phi=v P",
            "potential_value": value,
            "gradient_max_abs": float(np.max(np.abs(gradient))),
            "eigenvalue_clusters": clusters,
            "general_v_clusters": [
                {"eigenvalue": "0", "multiplicity": 24},
                {"eigenvalue": "(8/9) v^2", "multiplicity": 90},
                {"eigenvalue": "(3/2) v^2", "multiplicity": 80},
                {"eigenvalue": "(12/5) v^2", "multiplicity": 15},
                {"eigenvalue": "8 v^2", "multiplicity": 1},
            ],
            "zero_mode_count": zero_count,
            "negative_mode_count": negative_count,
            "minimum_physical_eigenvalue": float(physical[0]),
            "maximum_physical_eigenvalue": float(physical[-1]),
            "goldstone_alignment_max_abs_residual": goldstone_residual,
            "cluster_max_abs_residual": cluster_residual,
        },
        "newly_closed_subproblem": {
            "bounded_210_self_quartic_benchmark": not failures,
            "global_Pati_Salam_vacuum_exists": not failures,
            "full_210_Hessian_at_Pati_Salam_vacuum": not failures,
            "210_sector_threshold_multiplets": not failures,
        },
        "remaining_blockers": {
            "uniqueness_among_all_global_210_orbits": True,
            "complete_multi_field_scalar_potential": True,
            "simultaneous_126_and_10_vacuum": True,
            "positive_multi_field_physical_Hessian": True,
            "full_physical_threshold_spectrum": True,
            "component_level_two_loop_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "210_quartic_bounded_below": not failures,
            "global_Pati_Salam_210_vacuum": not failures,
            "physical_210_Hessian_complete_at_benchmark": not failures,
            "complete_multi_field_potential": False,
            "unique_full_vacuum": False,
            "physical_full_model_Hessian_complete": False,
            "full_physical_threshold_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "A globally bounded real-210 potential has an exact Pati--Salam "
            "global minimum Phi=vP. The full 210 Hessian contains precisely 24 "
            "Goldstones and 186 positive modes with an analytic spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact 210 Pati–Salam global vacuum — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Global bound: `V >= (I2-v^2)^2-v^4`.",
            "- Vacuum: `Phi=vP`, preserving `SO(6)xSO(4)`.",
            "- Goldstones: `24`.",
            "- Positive physical 210 modes: `186`.",
            "- The complete multi-field vacuum remains open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
