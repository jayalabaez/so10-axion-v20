#!/usr/bin/env python3
"""Strict V50 C5 second-profile rematching and obstruction audit.

The frozen V50 same-action collar proved that its local A=A^T, Xi=Xi^T and
C blocks span sp(2n), including the exact O7/O8 integration-by-parts normal
form.  This audit asks the narrower C5 question: can two independent regulator
profiles be brought to the same renormalized transfer through O(1/Lambda) by
counterterms already in that local action?

The answer is yes for the complete quadratic tree transfer.  Fixing the
renormalized zero-energy transfer and its first spectral jet determines a
leading Hamiltonian layer H0 and a weak layer x H1, x=m/Lambda.  Both lie in
sp(2n) and decompose into the retained A/Xi/C blocks.  A deterministic Wilson
response then agrees between profiles up to O(Lambda^-2).

This does not close strict C5.  The existing criterion also requires a named
subtraction prescription, the full retained-order divergent counterterm
mixing, and regulator/scale independence.  The one-loop 1PI divergences,
finite deconstruction thresholds, anomalous-dimension matrix and beta-function
cancellation are not available.  The report identifies these missing data
rather than demoting them to an unspecified remainder.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.linalg import expm, logm

import susy_v48_source_operator_wilson_audit as v48
import susy_v50_full_same_action_collar_audit as v50


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_C5_STRICT_REMATCH_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_C5_STRICT_REMATCH_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_c5_strict_rematch_audit.py"

STATUS = (
    "V50_C5_STRICT_TREE_QUADRATIC_PROFILE_REMATCH_COMPLETE__"
    "FULL_SP_COUNTERTERMS_REALIZED_IN_LOCAL_A_XI_C_ACTION__"
    "FIXED_TRANSFER_JET_RENORMALIZATION_REMOVES_HOMOGENEOUS_QUADRATIC_PROFILE_AMBIGUITY_"
    "THROUGH_O_LAMBDA_MINUS1__"
    "LOOP_DIVERGENCE_MIXING_THRESHOLD_SUBTRACTION_AND_SCALE_CANCELLATION_UNCOMPUTED__"
    "C5_REMAINS_PARTIAL__G2_OPEN"
)

UPSTREAM = (
    ROOT / "SUSY_V50_FULL_SAME_ACTION_COLLAR_AUDIT.json",
    ROOT / "SUSY_V50_LOCAL_CONSTRAINED_TRANSPORT_REGULATOR_AUDIT.json",
    ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spectral_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(np.asarray(matrix), compute_uv=False)[0])


def maximum_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(matrix))))


def alternate_profile_callback(data: Mapping[str, Any]) -> v50.BlockCallback:
    """Independent smooth profiles with the same individual zeroth moments.

    Relative ordering differs from the frozen V50 profile.  In particular,
    A, Xi, C and the O7/O8 difference use distinct smooth shapes.  Their
    normalized integrals match the corresponding frozen coefficients, but
    noncommuting ordered moments do not.
    """

    epsilon = float(data["epsilon"])

    def callback(t: float, mass: complex) -> Mapping[str, np.ndarray]:
        angle4 = 4.0 * math.pi * t
        profile_a = 6.0 * t * (1.0 - t)  # integral one
        profile_xi = 30.0 * t**2 * (1.0 - t) ** 2  # integral one
        profile_c = 1.0 + 0.17 * math.cos(angle4)  # integral one
        odd_a = math.sin(angle4)  # integral zero
        odd_xi = (2.0 * t - 1.0) * profile_xi  # integral zero
        odd_c = math.sin(angle4)  # integral zero

        derivative_even = 3.0 * t * (1.0 - t)  # integral one half
        derivative_even_prime = 3.0 * (1.0 - 2.0 * t)
        derivative_odd = math.sin(angle4)
        derivative_odd_prime = 4.0 * math.pi * math.cos(angle4)

        r7 = derivative_even * data["R7a"] + derivative_odd * data["R7b"]
        r8 = derivative_even * data["R8a"] + derivative_odd * data["R8b"]
        r7_prime = (
            derivative_even_prime * data["R7a"]
            + derivative_odd_prime * data["R7b"]
        )
        r8_prime = (
            derivative_even_prime * data["R8a"]
            + derivative_odd_prime * data["R8b"]
        )
        return {
            "A": profile_a * data["A0"] + 0.31 * odd_a * data["A1"],
            "Xi": profile_xi * data["Xi0"] + 0.27 * odd_xi * data["Xi1"],
            "C": profile_c * data["C0"] + 0.23 * odd_c * data["C1"],
            "R7": r7,
            "R8": r8,
            "R7_prime": r7_prime,
            "R8_prime": r8_prime,
            "spectral_metric": epsilon * data["norm_metric"],
        }

    return callback


def hamiltonian_projection(matrix: np.ndarray, channels: int) -> np.ndarray:
    """Roundoff-stable projection onto sp(2n)."""

    value = np.asarray(matrix, dtype=np.complex128)
    j0 = v50.j_form(channels)
    return (value + j0 @ value.T @ j0) / 2.0


def hamiltonian_residual(matrix: np.ndarray, channels: int) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    j0 = v50.j_form(channels)
    return maximum_abs(value.T @ j0 + j0 @ value)


def hamiltonian_blocks(matrix: np.ndarray, channels: int) -> dict[str, Any]:
    """Decompose H in sp(2n) into the retained A/Xi/C coordinates."""

    value = np.asarray(matrix, dtype=np.complex128)
    c0 = value[:channels, :channels]
    xi0 = value[:channels, channels:]
    a0 = -value[channels:, :channels]
    reconstruction = v50.sp_generator(a0, xi0, c0)
    return {
        "A": a0,
        "Xi": xi0,
        "C": c0,
        "A_symmetric_residual": v50.transpose_symmetry_residual(a0),
        "Xi_symmetric_residual": v50.transpose_symmetry_residual(xi0),
        "reconstruction_residual": maximum_abs(reconstruction - value),
        "A_norm": spectral_norm(a0),
        "Xi_norm": spectral_norm(xi0),
        "C_norm": spectral_norm(c0),
    }


def matrix_summary(blocks: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in blocks.items()
        if not isinstance(value, np.ndarray)
    }


def transfer_at_x(
    callback: v50.BlockCallback,
    x: float,
    epsilon: float,
    channels: int,
    steps: int,
) -> np.ndarray:
    """Collar transfer at x=m epsilon=m/Lambda."""

    return v50.path_ordered_collar_transfer(
        x / epsilon, callback, channels, steps=steps
    )


def counterterm_layers(
    reference: v50.BlockCallback,
    alternate: v50.BlockCallback,
    epsilon: float,
    channels: int,
    steps: int,
) -> dict[str, Any]:
    """Determine the fixed-RC outer-layer counterterms H0 and H1.

    Renormalization conditions are T_R(0)=T_star(0) and
    (dT_R/dx)T_R^-1|0=Y_star.  The principal logarithm fixes the local chart.
    """

    def transfer(callback: v50.BlockCallback, x: float) -> np.ndarray:
        return transfer_at_x(callback, x, epsilon, channels, steps)

    reference0 = transfer(reference, 0.0)
    alternate0 = transfer(alternate, 0.0)
    correction0 = reference0 @ np.linalg.inv(alternate0)
    raw_h0 = logm(correction0)
    h0 = hamiltonian_projection(raw_h0, channels)
    finite_step = 5.0e-5

    def exact_correction(x: float) -> np.ndarray:
        return transfer(reference, x) @ np.linalg.inv(transfer(alternate, x))

    correction_prime = (
        exact_correction(finite_step) - exact_correction(-finite_step)
    ) / (2.0 * finite_step)
    raw_h1 = correction_prime @ np.linalg.inv(correction0)
    h1 = hamiltonian_projection(raw_h1, channels)
    z_counterterm = -v50.j_form(channels) @ h1

    return {
        "reference0": reference0,
        "alternate0": alternate0,
        "correction0": correction0,
        "H0": h0,
        "H1": h1,
        "Z_counterterm": z_counterterm,
        "raw_zero_profile_difference_norm": spectral_norm(reference0 - alternate0),
        "correction0_distance_from_identity": spectral_norm(
            correction0 - np.eye(2 * channels)
        ),
        "principal_log_imaginary_residual": maximum_abs(np.imag(raw_h0)),
        "H0_Hamiltonian_residual": hamiltonian_residual(h0, channels),
        "H1_Hamiltonian_residual": hamiltonian_residual(h1, channels),
        "exp_H0_exact_correction_residual": spectral_norm(expm(h0) - correction0),
        "spectral_Z_symmetric_residual": v50.transpose_symmetry_residual(
            z_counterterm
        ),
        "H0_blocks": hamiltonian_blocks(h0, channels),
        "H1_blocks": hamiltonian_blocks(h1, channels),
    }


@functools.lru_cache(maxsize=1)
def rematch_certificate() -> dict[str, Any]:
    channels = 4
    data = v50.deterministic_collar_data(channels)
    epsilon = float(data["epsilon"])
    reference = v50.deterministic_collar_blocks(data)
    alternate = alternate_profile_callback(data)
    steps = 72
    layers = counterterm_layers(
        reference, alternate, epsilon, channels, steps
    )
    h0 = layers["H0"]
    h1 = layers["H1"]

    x_values = (0.04, 0.02, 0.01, 0.005, 0.0025)
    transfer_errors: list[float] = []
    exact_counterterm_symplectic: list[float] = []
    for x in x_values:
        target = transfer_at_x(reference, x, epsilon, channels, steps)
        uncorrected = transfer_at_x(alternate, x, epsilon, channels, steps)
        exact = target @ np.linalg.inv(uncorrected)
        corrected = expm(x * h1) @ expm(h0) @ uncorrected
        transfer_errors.append(spectral_norm(corrected - target))
        exact_counterterm_symplectic.append(
            v50.symplectic_residual(exact, channels)
        )

    transfer_ratios = [
        later / earlier
        for earlier, later in zip(transfer_errors, transfer_errors[1:])
    ]
    normalized_transfer_errors = [
        error / x**2 for error, x in zip(transfer_errors, x_values)
    ]

    # Check the actual reduced Wilson response after composing the unchanged
    # bulk and endpoint pencils.  The physical mass stays fixed as epsilon is
    # reduced, so x=m epsilon.
    physical_mass = 0.37
    epsilons = (0.08, 0.04, 0.02, 0.01)
    bulk_masses = (0.0, 0.07, -0.04, 0.025)
    even = (True, False, False, True)
    bulk = v50.bulk_transfer(physical_mass, bulk_masses, 0.93, even)
    host = v50.endpoint_data(channels, 601)
    source = v50.endpoint_data(channels, 611)
    raw_wilson_errors: list[float] = []
    rematched_wilson_errors: list[float] = []

    for width in epsilons:
        profile_data = v50.deterministic_collar_data(channels)
        profile_data["epsilon"] = width
        ref_callback = v50.deterministic_collar_blocks(profile_data)
        alt_callback = alternate_profile_callback(profile_data)
        ref_collar = v50.path_ordered_collar_transfer(
            physical_mass, ref_callback, channels, steps=steps
        )
        alt_collar = v50.path_ordered_collar_transfer(
            physical_mass, alt_callback, channels, steps=steps
        )
        correction = expm(physical_mass * width * h1) @ expm(h0)

        gamma_ref, n_ref = v50.reduced_characteristic(
            ref_collar @ bulk, physical_mass, host, source
        )
        gamma_alt, n_alt = v50.reduced_characteristic(
            alt_collar @ bulk, physical_mass, host, source
        )
        gamma_matched, n_matched = v50.reduced_characteristic(
            correction @ alt_collar @ bulk, physical_mass, host, source
        )
        response_ref = np.linalg.solve(gamma_ref, n_ref)
        response_alt = np.linalg.solve(gamma_alt, n_alt)
        response_matched = np.linalg.solve(gamma_matched, n_matched)
        raw_wilson_errors.append(spectral_norm(response_alt - response_ref))
        rematched_wilson_errors.append(
            spectral_norm(response_matched - response_ref)
        )

    wilson_ratios = [
        later / earlier
        for earlier, later in zip(
            rematched_wilson_errors, rematched_wilson_errors[1:]
        )
    ]
    wilson_normalized = [
        error / width**2
        for error, width in zip(rematched_wilson_errors, epsilons)
    ]

    z_total = np.asarray(data["norm_metric"]) + np.real_if_close(
        layers["Z_counterterm"]
    ).real
    return {
        "channels": channels,
        "path_order_steps": steps,
        "renormalized_variable": "x=m epsilon=m/Lambda",
        "profile_moment_contract": {
            "A_Xi_C_zeroth_moments": "equal by analytic normalization",
            "R7_R8_even_moment": "one half in both profiles",
            "odd_moments": "zero in both profiles",
            "ordered_mixed_moments": "different because the strong generators do not commute",
        },
        "unmatched_profile_obstruction": {
            "zero_energy_transfer_difference_norm": layers[
                "raw_zero_profile_difference_norm"
            ],
            "correction0_distance_from_identity": layers[
                "correction0_distance_from_identity"
            ],
            "raw_Wilson_response_errors": raw_wilson_errors,
            "raw_Wilson_error_last_over_first": raw_wilson_errors[-1]
            / raw_wilson_errors[0],
        },
        "local_counterterm_realization": {
            "definition": (
                "C_exact(x)=T_reference(x)T_profile(x)^-1; "
                "C_CT(x)=exp(x H1)exp(H0)"
            ),
            "H0": "principal-log Hamiltonian of C_exact(0)",
            "H1": "left logarithmic derivative C_exact'(0)C_exact(0)^-1",
            "principal_log_imaginary_residual": layers[
                "principal_log_imaginary_residual"
            ],
            "H0_Hamiltonian_residual": layers["H0_Hamiltonian_residual"],
            "H1_Hamiltonian_residual": layers["H1_Hamiltonian_residual"],
            "exp_H0_exact_correction_residual": layers[
                "exp_H0_exact_correction_residual"
            ],
            "exact_counterterm_max_symplectic_residual": max(
                exact_counterterm_symplectic
            ),
            "H0_retained_block_decomposition": matrix_summary(
                layers["H0_blocks"]
            ),
            "H1_retained_block_decomposition": matrix_summary(
                layers["H1_blocks"]
            ),
            "spectral_Z_counterterm_symmetric_residual": layers[
                "spectral_Z_symmetric_residual"
            ],
            "total_Kahler_metric_min_eigenvalue": v50.minimum_eigenvalue(
                z_total
            ),
            "locality": (
                "H0 is one strong local A/Xi/C layer. H1 is one weak local "
                "spectral layer, equivalently a symmetric Z shift; the retained "
                "O7/O8 blocks provide the same Darboux-complete chart."
            ),
        },
        "transfer_rematch": {
            "x_values": list(x_values),
            "errors": transfer_errors,
            "successive_halving_ratios": transfer_ratios,
            "errors_divided_by_x_squared": normalized_transfer_errors,
        },
        "Wilson_rematch": {
            "physical_mass": physical_mass,
            "epsilons": list(epsilons),
            "raw_profile_errors": raw_wilson_errors,
            "rematched_errors": rematched_wilson_errors,
            "successive_halving_ratios": wilson_ratios,
            "errors_divided_by_epsilon_squared": wilson_normalized,
        },
    }


def strict_c5_contract() -> dict[str, Any]:
    return {
        "criterion_frozen_from_V48": (
            "Name the regulator and subtraction prescription, list every counterterm "
            "at the retained order, give renormalization conditions at mu_star and show "
            "regulator/scale independence up to the declared remainder."
        ),
        "regulator": (
            "V50 finite local constrained-transport deconstruction, with the V50 "
            "same-action A/Xi/C/O7/O8 collar"
        ),
        "provisional_subtraction_scheme": (
            "supersymmetric dimensional reduction with DRbar poles at mu_star=Lambda, "
            "plus the finite transfer-jet conditions below; this is named but its "
            "one-loop counterterms have not been calculated"
        ),
        "tree_quadratic_renormalization_conditions": {
            "RC0": (
                "Hold the entire renormalized symplectic transfer T_R(0)=T_star(0) "
                "fixed in the principal-log outer-layer chart."
            ),
            "RC1": (
                "Hold the left spectral jet Y_R=(dT_R/dx)T_R^-1|x=0 fixed, "
                "with x=m/Lambda."
            ),
            "endpoint": (
                "Hold the enlarged Hermitian endpoint M,Z,C,H,W pencils and their "
                "auxiliary determinant factors fixed at mu_star."
            ),
            "effect": (
                "H0 and H1 are then profile-dependent bare shifts but no homogeneous-"
                "quadratic or fixed-endpoint-current Wilson ambiguity remains through "
                "O(Lambda^-1)."
            ),
        },
        "counterterm_basis_at_tree_quadratic_order": [
            "all symmetric A(X) HH strong blocks",
            "all symmetric Xi(X) HcHc strong blocks",
            "all arbitrary C(X) odd-profile HcH blocks",
            "independent R7/R8 O7/O8 normal-derivative blocks with their exact endpoint shifts",
            "the complete positive Kahler/spectral Z operator and positive auxiliary endpoint enlargements",
        ],
        "uncomputed_strict_requirements": [
            "the one-loop divergent 1PI boundary functional in the finite local deconstruction regulator",
            "the anomalous-dimension/operator-mixing matrix for every V49 retained invariant direction",
            "finite thresholds of the transport pairs, gauge-link sector, and any linear-link radial completion",
            "bare-to-DRbar maps for A,Xi,C,R7,R8,Kahler,FI,gauge,source-quartic and portal coefficients",
            "a beta-function proof that the full physical Wilson array is mu_star independent through O(Lambda^-1)",
            "an affine/distributed-current and source-functional profile rematch for every retained portal and derivative-current direction",
            "normalized component tensors needed to project the loop divergences into every retained SO(10)->PS direction",
        ],
        "logical_result": (
            "The second-profile homogeneous-quadratic and fixed-endpoint-current test passes. Strict C5 remains partial "
            "because subtraction and scale independence are conjunctive requirements, "
            "not because an unmapped tree-level symplectic transfer coefficient remains."
        ),
    }


def build_report() -> dict[str, Any]:
    certificate = rematch_certificate()
    contract = strict_c5_contract()
    local = certificate["local_counterterm_realization"]
    transfer = certificate["transfer_rematch"]
    wilson = certificate["Wilson_rematch"]
    obstruction = certificate["unmatched_profile_obstruction"]

    checks = {
        "independent_profiles_have_nonzero_unmatched_transfer": obstruction[
            "zero_energy_transfer_difference_norm"
        ] > 1.0e-4,
        "unmatched_Wilson_profile_dependence_survives_thin_limit": obstruction[
            "raw_Wilson_error_last_over_first"
        ] > 0.8,
        "H0_is_retained_Hamiltonian_block": local["H0_Hamiltonian_residual"] < 1.0e-11
        and local["H0_retained_block_decomposition"]["reconstruction_residual"] < 1.0e-11,
        "H1_is_retained_Hamiltonian_block": local["H1_Hamiltonian_residual"] < 1.0e-11
        and local["H1_retained_block_decomposition"]["reconstruction_residual"] < 1.0e-11,
        "leading_counterterm_is_exact_and_local": local[
            "exp_H0_exact_correction_residual"
        ] < 1.0e-11,
        "exact_transfer_counterterm_is_symplectic": local[
            "exact_counterterm_max_symplectic_residual"
        ] < 1.0e-10,
        "spectral_counterterm_is_symmetric_and_total_metric_positive": local[
            "spectral_Z_counterterm_symmetric_residual"
        ] < 1.0e-10
        and local["total_Kahler_metric_min_eigenvalue"] > 0.0,
        "transfer_rematch_error_is_second_order": max(
            abs(ratio - 0.25) for ratio in transfer["successive_halving_ratios"]
        ) < 0.01,
        "Wilson_rematch_error_is_second_order": max(
            abs(ratio - 0.25) for ratio in wilson["successive_halving_ratios"]
        ) < 0.01,
        "strict_C5_not_overclaimed": len(contract["uncomputed_strict_requirements"]) == 7,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V50 strict C5 audit failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v50-c5-strict-rematch-audit-v1",
        "status": STATUS,
        "strict_C5_contract": contract,
        "second_profile_rematch_certificate": certificate,
        "C5_decision": {
            "status": "PARTIAL_NOT_CLOSED",
            "tree_quadratic_profile_rematch": "PASS_THROUGH_O_LAMBDA_MINUS1",
            "affine_current_and_source_functional_rematch": "FAIL_MISSING_CALCULATION",
            "loop_subtraction_and_scale_independence": "FAIL_MISSING_CALCULATION",
            "unmapped_homogeneous_quadratic_and_fixed_endpoint_current_ambiguity": False,
            "remaining_unmapped_data": (
                "one-loop divergent mixing, finite local-regulator thresholds, "
                "bare-to-renormalized maps, affine distributed-current/source-functional "
                "rematching, beta functions and component projections"
            ),
        },
        "G2_decision": {
            "closed": False,
            "verdict": "G2_REMAINS_OPEN",
            "reason": (
                "The frozen strict C5 conjunction is false even though the second-profile "
                "homogeneous tree transfer test now passes. Affine distributed-current "
                "rematching, loop subtraction and scale independence remain unproved; "
                "C7 also remains incomplete."
            ),
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "source_manifest": [
            {"path": path.name, "sha256": sha256_file(path)} for path in UPSTREAM
        ]
        + [
            {
                "path": TEST_PATH.name,
                "sha256": sha256_file(TEST_PATH) if TEST_PATH.is_file() else None,
            }
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    certificate = report["second_profile_rematch_certificate"]
    local = certificate["local_counterterm_realization"]
    transfer = certificate["transfer_rematch"]
    wilson = certificate["Wilson_rematch"]
    obstruction = certificate["unmatched_profile_obstruction"]
    missing = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(
            report["strict_C5_contract"]["uncomputed_strict_requirements"], 1
        )
    )
    return f"""# V50 strict C5 second-profile rematch audit

Status: `{report['status']}`

## Verdict

The independent-profile test now **passes for the complete quadratic tree
collar through `O(Lambda^-1)`**.  The regulator-profile difference is an exact
symplectic transfer.  Its leading correction and first spectral jet are
Hamiltonian and decompose into the already retained local `A`, `Xi`, and `C`
blocks.  Holding the full renormalized transfer and its first spectral jet
fixed removes the homogeneous quadratic and fixed-endpoint-current ambiguity;
no new operator is needed for that tested sector.  Distributed collar
currents and source-functional jets are not silently included in this claim.

**Strict C5 nevertheless remains partial and G2 remains open.**  The frozen
C5 criterion also demands the retained-order subtraction calculation and
scale independence.  No one-loop divergent mixing matrix, finite local-chain
threshold subtraction, beta functions, or component projection of those
divergences has been computed.  That conjunct cannot be replaced by the
tree-level profile rematch.

## Exact tree rematch

Let `x=m epsilon=m/Lambda` and let `T_star(x)` and `T_p(x)` be the two
independently integrated same-action collar transfers.  Although every
individual profile has the same zeroth moment, their noncommuting ordered
moments differ.  Before rematching,

```text
||T_star(0)-T_p(0)|| = {obstruction['zero_energy_transfer_difference_norm']:.8g},
last/first raw Wilson mismatch = {obstruction['raw_Wilson_error_last_over_first']:.8g}.
```

Define

```text
C_exact(x) = T_star(x) T_p(x)^-1,
H0 = principal_log C_exact(0),
H1 = C_exact'(0) C_exact(0)^-1,
C_CT(x) = exp(x H1) exp(H0).
```

Because both transfers are symplectic, `H0,H1 in sp(2n)`.  In the deterministic
four-channel calculation their Hamiltonian residuals are
`{local['H0_Hamiltonian_residual']:.3e}` and
`{local['H1_Hamiltonian_residual']:.3e}`.  Their reconstruction from
`[[C,Xi],[-A,-C^T]]` has residuals
`{local['H0_retained_block_decomposition']['reconstruction_residual']:.3e}`
and `{local['H1_retained_block_decomposition']['reconstruction_residual']:.3e}`.
Thus the correction is inside the declared local action, not an abstract
unmapped boundary matrix.

The leading layer reproduces `C_exact(0)` to
`{local['exp_H0_exact_correction_residual']:.3e}`.  The weak layer corresponds
to the symmetric spectral counterterm `Z_CT=-J0 H1`; the total representative
Kahler metric remains positive with minimum eigenvalue
`{local['total_Kahler_metric_min_eigenvalue']:.6g}`.

For successive halvings of `x`, the corrected transfer errors are
`{transfer['errors']}` and their ratios are
`{transfer['successive_halving_ratios']}`.  They scale as `x^2`.

After composing the unchanged bulk transfer and enlarged endpoint pencils,
the physical Wilson-response errors at widths `{wilson['epsilons']}` are
`{wilson['rematched_errors']}` with ratios
`{wilson['successive_halving_ratios']}`.  They scale as `epsilon^2`, whereas
the unrematched errors approach a nonzero thin-wall value.

## Fixed tree renormalization conditions

At `mu_star=Lambda`, use the principal-log outer-layer chart and hold fixed:

1. the entire renormalized transfer `T_R(0)=T_star(0)`;
2. the left spectral jet `(dT_R/dx)T_R^-1|_0`;
3. the enlarged Hermitian endpoint pencils and their undivided auxiliary
   determinant factors.

These conditions determine profile-dependent **bare** `H0,H1` shifts while
keeping the tested renormalized response fixed.  Therefore the old inference
that an unmapped homogeneous-quadratic coefficient necessarily survives is
rejected; the affine distributed-current sector remains an explicit missing
calculation.

## Why strict C5 still fails

The unchanged C5 criterion is: name the regulator and subtraction
prescription, list every retained-order counterterm, give renormalization
conditions, and prove regulator/scale independence to the declared remainder.
The finite local deconstruction regulator is named, and the tree quadratic
conditions above are complete.  The following required data remain absent:

{missing}

Consequently `C5=PARTIAL_NOT_CLOSED`.  The precise obstruction is now the
missing loop/threshold mixing and scale-cancellation calculation—not an
unrealizable tree-level symplectic counterterm.

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError(f"stale artifact: {JSON_PATH.name}")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError(f"stale artifact: {MD_PATH.name}")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_artifacts()
        print("V50_C5_STRICT_REMATCH_AUDIT_CHECK_PASS")
    else:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])


if __name__ == "__main__":
    main()
