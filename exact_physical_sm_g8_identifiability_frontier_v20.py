#!/usr/bin/env python3
"""Exact identifiability frontier for the physical proton-decay gate G8.

This theorem composes the corrected physical-SM vector, threshold and Yukawa
CGC artifacts with the repository-frozen proton-decay input.  It does not
promote a conditional benchmark to a model prediction.

Two exact obstructions are sufficient to keep G8 open:

* the heavy-vector theorem permits every ``v>0`` and has
  ``M_X(lambda*v)=lambda*M_X(v)``.  For any nonzero dimension-six gauge
  contribution at fixed dimensionless coupling, flavour and running data,
  ``C(lambda)=C(1)/lambda^2``, ``Gamma(lambda)=Gamma(1)/lambda^4`` and
  ``tau(lambda)=lambda^4*tau(1)``.  Relative to the mass that saturates any
  finite positive experimental lower limit, ``lambda=1/2`` and ``lambda=2``
  give exact margins ``1/16`` and ``16``.  The same rescaling also changes the
  closed vector MS-bar thresholds logarithmically.
* normalized representation CGCs do not fix the ten complex flavour tensors,
  their boundary covariance, the physical colour-triplet pole matrix, or the
  relative gauge/scalar interference phases.  Equal-magnitude amplitudes with
  relative signs ``+`` and ``-`` give exact squared amplitudes ``4`` and ``0``.

Thus current inputs do not define a unique lifetime or an uncertainty
distribution.  This is a constructive proof of non-identifiability, not a
claim that G8 cannot be closed after the missing boundary data and calculations
are supplied.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from numbers import Rational
from pathlib import Path
from typing import Any

import canonical_g1_g8_gauged_u1x_v21 as gap_contract
import proton_decay_falsification_gate_v20 as proton_gate


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md"

STATUS = (
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_CLOSED__"
    "PHYSICAL_RELEASE_AUTHORITATIVE_G8_OPEN"
)
CONTRACT_ID = "exact_physical_sm_g8_identifiability_frontier_v20"

DEPENDENCIES: dict[str, tuple[Path, str, str | None]] = {
    "canonical_gauged_u1x_v21_contract_source": (
        HERE / "canonical_g1_g8_gauged_u1x_v21.py",
        "4158df2bbef369d100ed95cf45a6428b3307cdf4da066f4664981b2c4d61dea0",
        None,
    ),
    "repository_frozen_proton_gate_source": (
        HERE / "proton_decay_falsification_gate_v20.py",
        "f2d875ba665707a929bf912dfc83af547452d04cb8ebb6932e67dffd076dd921",
        None,
    ),
    "physical_SM_G6_G7_frontier": (
        HERE / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json",
        "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a",
        "eedc4bf7c068318f7cf597beaed25ff2eb5893951872475ade02ea8a91386aae",
    ),
    "physical_SM_heavy_vector_masses": (
        HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
        "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0",
        "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894",
    ),
    "physical_SM_heavy_vector_MSbar_matching": (
        HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
        "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee",
        "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575",
    ),
    "normalized_SO10_Yukawa_CGCs": (
        HERE / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
        "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b",
        "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7",
    ),
    "physical_G7_component_threshold_contract": (
        HERE / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
        "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e",
        "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2",
    ),
}

EXPECTED_CORE_SHA256 = (
    "029dfd8b707825742c85b6d223a54ee964c76cf519496c5d5da28a7cad407fd5"
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_text(value: Fraction | int) -> str:
    result = Fraction(value)
    return (
        str(result.numerator)
        if result.denominator == 1
        else f"{result.numerator}/{result.denominator}"
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return _fraction_text(value)
    return value


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _positive_exact(name: str, value: Rational) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, Rational):
        raise TypeError(f"{name} must be an exact rational number")
    result = Fraction(value)
    if result <= 0:
        raise ValueError(f"{name} must be strictly positive")
    return result


def source_guard() -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for name, (path, raw_expected, core_expected) in DEPENDENCIES.items():
        raw_observed = _digest(path)
        if raw_observed != raw_expected:
            raise ArithmeticError(f"G8-frontier dependency drifted: {name}")
        row: dict[str, Any] = {
            "path": str(path.relative_to(HERE)),
            "raw_sha256": raw_observed,
            "binding_mode": "raw",
        }
        if core_expected is not None:
            payload = json.loads(path.read_text(encoding="utf-8"))
            core_observed = payload.get("core_sha256")
            if core_observed != core_expected:
                raise ArithmeticError(f"G8-frontier core drifted: {name}")
            row["core_sha256"] = core_observed
        bindings[name] = row
    return bindings


def _load(name: str) -> dict[str, Any]:
    return json.loads(DEPENDENCIES[name][0].read_text(encoding="utf-8"))


def canonical_g8_definition() -> dict[str, Any]:
    matches = [
        gate
        for gate in gap_contract.GATES
        if gate["qualified_gate_id"] == gap_contract.G8_ID
    ]
    if len(matches) != 1:
        raise ArithmeticError("canonical G8 definition is absent or non-unique")
    gap = matches[0]
    expected_dependencies = [
        gap_contract.G5_ID,
        gap_contract.G6_ID,
        gap_contract.G7_ID,
    ]
    expected_acceptance = gap_contract.GATES[7]["acceptance"]
    if gap["dependencies"] != expected_dependencies:
        raise ArithmeticError("canonical G8 dependencies drifted")
    if gap["acceptance"] != expected_acceptance:
        raise ArithmeticError("canonical G8 acceptance criteria drifted")
    if gap["required_artifact"] != "CANONICAL_G8_UNIQUE_PROTON_LIFETIME_V21.json":
        raise ArithmeticError("canonical G8 artifact name drifted")
    return {
        "gap_id": gap["qualified_gate_id"],
        "definition_sha256": gap_contract.DEFINITION_SHA256,
        "dependencies": gap["dependencies"],
        "required_artifact": gap["required_artifact"],
        "acceptance": gap["acceptance"],
        "required_evidence_schema": gap_contract.EVIDENCE_SCHEMA,
    }


def exact_gauge_scale_witness(scale_ratio: Rational) -> dict[str, Any]:
    """Return exact lifetime and matching changes under ``v -> lambda*v``."""
    ratio = _positive_exact("scale_ratio", scale_ratio)
    masses = _load("physical_SM_heavy_vector_masses")
    matching = _load("physical_SM_heavy_vector_MSbar_matching")
    if masses["normalization"]["parameter_domain"] != "g10>0, gX>0, v>0":
        raise ArithmeticError("heavy-vector parameter domain drifted")
    if masses["scope"]["absolute_physical_masses"] is not False:
        raise ArithmeticError("heavy-vector scale was unexpectedly fixed")
    factors = matching["exact_group_factors"]["combined_threshold_coefficients"]
    su3 = Fraction(factors["SU3"]["log_over_pi"])
    qed = Fraction(factors["QED"]["log_over_pi"])
    if (su3, qed) != (Fraction(35, 4), Fraction(112, 3)):
        raise ArithmeticError("heavy-vector threshold coefficient drifted")
    return {
        "scale_ratio_lambda": ratio,
        "same_dimensionless_vector_mass_ratios": True,
        "mass_ratio": ratio,
        "dimension_six_Wilson_ratio_at_fixed_dimensionless_data": ratio ** -2,
        "partial_width_ratio_at_fixed_dimensionless_data": ratio ** -4,
        "partial_lifetime_ratio_at_fixed_dimensionless_data": ratio ** 4,
        "fixed_matching_scale": True,
        "threshold_shift_over_pi": {
            "SU3": f"(35/4)*log({_fraction_text(ratio)})",
            "QED": f"(112/3)*log({_fraction_text(ratio)})",
        },
        "threshold_log_coefficients": {"SU3": su3, "QED": qed},
        "absolute_vector_scale_identified": False,
    }


def exact_limit_crossing_witness() -> dict[str, Any]:
    below = exact_gauge_scale_witness(Fraction(1, 2))
    above = exact_gauge_scale_witness(Fraction(2))
    return {
        "reference_mass_definition": (
            "M_star is the vector mass for which a nonzero gauge-mediated "
            "partial lifetime equals any chosen finite positive lower limit"
        ),
        "below_limit_completion": {
            "lambda": below["scale_ratio_lambda"],
            "lifetime_margin_over_limit": below[
                "partial_lifetime_ratio_at_fixed_dimensionless_data"
            ],
            "below_limit": below[
                "partial_lifetime_ratio_at_fixed_dimensionless_data"
            ]
            < 1,
        },
        "above_limit_completion": {
            "lambda": above["scale_ratio_lambda"],
            "lifetime_margin_over_limit": above[
                "partial_lifetime_ratio_at_fixed_dimensionless_data"
            ],
            "above_limit": above[
                "partial_lifetime_ratio_at_fixed_dimensionless_data"
            ]
            > 1,
        },
        "same_normalized_vector_spectrum": True,
        "same_representation_and_charge_contract": True,
        "model_classification_identified_without_absolute_scale": False,
    }


def exact_scale_grid_0_through_100() -> dict[str, Any]:
    records = []
    for index in range(101):
        ratio = Fraction(index + 1, 51)
        witness = exact_gauge_scale_witness(ratio)
        records.append(
            {
                "case": index,
                "lambda": ratio,
                "mass_ratio": witness["mass_ratio"],
                "Wilson_ratio": witness[
                    "dimension_six_Wilson_ratio_at_fixed_dimensionless_data"
                ],
                "width_ratio": witness[
                    "partial_width_ratio_at_fixed_dimensionless_data"
                ],
                "lifetime_ratio": witness[
                    "partial_lifetime_ratio_at_fixed_dimensionless_data"
                ],
            }
        )
    return {
        "case_range": [0, 100],
        "case_count": len(records),
        "identity_case": 50,
        "all_scaling_identities_exact": all(
            row["Wilson_ratio"] == row["lambda"] ** -2
            and row["width_ratio"] == row["lambda"] ** -4
            and row["lifetime_ratio"] == row["lambda"] ** 4
            for row in records
        ),
        "records_sha256": _canonical_sha256(records),
        "first_case": records[0],
        "identity_record": records[50],
        "last_case": records[-1],
    }


def repository_frozen_experimental_input() -> dict[str, Any]:
    experiment = proton_gate.SOURCES["experiment"]
    if proton_gate.SUPER_K_EPI0_LIMIT_YEARS != 2.4e34:
        raise ArithmeticError("repository-frozen p->e+pi0 limit drifted")
    reference_alpha_inv = 37.0
    required_mass = proton_gate.required_vector_mass_gev(
        proton_gate.SUPER_K_EPI0_LIMIT_YEARS,
        reference_alpha_inv,
    )
    return {
        "scope": (
            "repository-frozen 2020 single-channel input, independently confirmed "
            "in the official PDG 2025 Conservation Laws review; not a live "
            "all-channel limit ledger"
        ),
        "channel": experiment["channel"],
        "citation": experiment["citation"],
        "arxiv": experiment["arxiv"],
        "official_current_review_verification": {
            "publisher": "Particle Data Group",
            "edition": 2025,
            "review": "Conservation Laws",
            "url": "https://pdg.lbl.gov/2025/reviews/rpp2025-rev-conservation-laws.pdf",
            "pdf_sha256_retrieved_2026_08_12": (
                "a320b62680575d1a37d29de60fe4f259afef2d24d5ab3550c59294bfd187b693"
            ),
            "pdf_page": 14,
            "reference_number": 117,
            "statement_scope": (
                "PDG lists tau(p->e+pi0)>2.4e34 yr and cites the 2020 "
                "Super-Kamiokande result"
            ),
            "numeric_value_agrees_with_repository": True,
        },
        "reported_limit_90CL_years": format(
            proton_gate.SUPER_K_EPI0_LIMIT_YEARS, ".12e"
        ),
        "reported_observation": experiment["observation"],
        "illustrative_alpha_inverse": format(reference_alpha_inv, ".12e"),
        "illustrative_required_vector_mass_GeV": format(required_mass, ".12e"),
        "illustrative_alpha_inverse_is_measured_or_model_fixed": False,
        "all_reported_channels_covered": False,
        "current_PDG_review_numeric_verification_performed": True,
        "complete_live_all_channel_limit_verification_performed": False,
        "usable_as_conditional_constraint": True,
        "usable_as_unique_G8_prediction": False,
    }


def exact_flavor_and_phase_witness() -> dict[str, Any]:
    cgcs = _load("normalized_SO10_Yukawa_CGCs")
    thresholds = _load("physical_G7_component_threshold_contract")
    inventory = thresholds["interaction_beta_inventory"]
    symbols = inventory["declared_Yukawa_and_fermion_mixing_symbols"]
    raw_complex = inventory["raw_complex_family_entries_before_flavour_quotients"]
    if len(symbols) != 10 or raw_complex != 50:
        raise ArithmeticError("flavour inventory drifted")
    if cgcs["scope"]["flavor_tensor_values_or_textures"] is not False:
        raise ArithmeticError("flavour values were unexpectedly fixed")
    plus = (Fraction(1) + Fraction(1)) ** 2
    minus = (Fraction(1) - Fraction(1)) ** 2
    return {
        "declared_flavor_tensor_symbols": symbols,
        "raw_complex_entries_before_flavour_quotients": raw_complex,
        "raw_real_entries_before_flavour_quotients": 2 * raw_complex,
        "representation_CGCs_normalized": cgcs["scope"][
            "normalized_representation_CGCs_for_all_declared_Yukawas"
        ],
        "flavor_tensor_values_or_textures_fixed": cgcs["scope"][
            "flavor_tensor_values_or_textures"
        ],
        "flavor_boundary_covariance_supplied": False,
        "physical_triplet_pole_mass_and_mixing_matrix_supplied": False,
        "equal_magnitude_interference_witness": {
            "gauge_amplitude_magnitude": 1,
            "scalar_amplitude_magnitude": 1,
            "relative_sign_plus_squared_amplitude": plus,
            "relative_sign_minus_squared_amplitude": minus,
            "same_individual_magnitudes": True,
            "different_total_widths": plus != minus,
            "scope": (
                "algebraic demonstration that an unspecified relative phase "
                "cannot define a unique rate; not a fitted physical endpoint"
            ),
        },
        "unique_mass_basis_scalar_Wilson_coefficients": False,
        "vacuum_fixed_gauge_scalar_interference": False,
    }


def acceptance_matrix() -> dict[str, dict[str, Any]]:
    canonical = canonical_g8_definition()
    frontier = _load("physical_SM_G6_G7_frontier")
    scope = frontier["scope"]
    flavor = exact_flavor_and_phase_witness()
    frozen = repository_frozen_experimental_input()
    passed = [
        bool(
            scope["unique_pole_spectrum"]
            and flavor["physical_triplet_pole_mass_and_mixing_matrix_supplied"]
        ),
        bool(scope["unique_full_RGE_trajectory"]),
        bool(
            flavor["flavor_tensor_values_or_textures_fixed"]
            and flavor["flavor_boundary_covariance_supplied"]
        ),
        bool(flavor["vacuum_fixed_gauge_scalar_interference"]),
        bool(frozen["all_reported_channels_covered"]),
    ]
    reasons = [
        "absolute scalar/vector/fermion pole spectrum and physical triplet matrix are open",
        "complete Wilson matching, anomalous dimensions and full RGE trajectory are open",
        "50 complex flavour entries and their fitted covariance/distribution are absent",
        "the physical vacuum does not yet fix gauge-scalar relative phases",
        "only one repository-frozen 2020 channel limit is represented",
    ]
    return {
        f"criterion_{index}": {
            "criterion": criterion,
            "passed": value,
            "reason": reason,
        }
        for index, (criterion, value, reason) in enumerate(
            zip(canonical["acceptance"], passed, reasons, strict=True), start=1
        )
    }


def exact_missing_inputs() -> dict[str, list[str]]:
    return {
        "continuous_boundary_values_or_distributions": [
            "absolute breaking scales and g10/gX with covariance",
            "the complete 51-real scalar tensor and dimensionful renormalized boundary data",
            "ten flavour tensors (50 complex entries before flavour quotients) fitted to low-energy data with covariance",
            "matching scales and correlated nuisance parameters",
            "physical CP/interference phases fixed by the same vacuum and flavour solution",
        ],
        "derivable_but_not_yet_derived": [
            "source-algebra global physical-SM vacuum and stage-resolved Hessians",
            "source-exact scalar/vector/fermion tree matrices at every breaking stage",
            "self-energy pole equations in a declared tadpole/VEV and MS-bar scheme",
            "complete scalar and fermion thresholds including finite terms",
            "full two-loop gauge/Yukawa/scalar/dimensionful flow and required EFT mixing",
            "mass-basis gauge and scalar baryon-violating Wilson coefficients and their running",
            "second independent full RGE/matching replay",
        ],
        "measured_or_lattice_inputs_to_freeze_with_covariance": [
            "low-energy gauge couplings, fermion masses, CKM and neutrino observables",
            "channel-specific lattice-QCD hadronic matrix elements",
            "a versioned all-channel experimental lifetime-limit ledger",
        ],
        "software_environment_not_laboratory": [
            "hash-bound genuine SARAH/Wolfram execution attestation required upstream",
        ],
        "new_laboratory_measurement_required_for_theory_gate": [],
    }


def minimal_exhibited_free_input_vector() -> dict[str, Any]:
    """Record the smallest explicit witness and independent extra freedoms.

    One positive scale coordinate already destroys uniqueness of the absolute
    vector spectrum, the fixed-mu vector threshold and a nonzero gauge-mediated
    lifetime.  The scalar ``b`` and flavour coordinates are independent
    obstructions; they are not needed to make the one-dimensional argument.
    """
    g6g7 = _load("physical_SM_G6_G7_frontier")
    witnesses = g6g7["exact_nonidentifiability_witnesses"]
    flavor = witnesses["flavor_boundaries"]
    if flavor["raw_real_degrees_before_flavour_quotients"] != 100:
        raise ArithmeticError("raw flavour dimension drifted")
    if witnesses["scalar_EFT_b_scale"]["dimensionful_scalar_scale_identified"]:
        raise ArithmeticError("conditional scalar b scale was unexpectedly fixed")
    if witnesses["vector_common_scale"]["absolute_vector_scale_identified"]:
        raise ArithmeticError("absolute vector scale was unexpectedly fixed")
    return {
        "smallest_exhibited_joint_witness": {
            "coordinates": ["lambda_v"],
            "domain": "lambda_v in positive rationals, lambda_v != 1",
            "real_dimension": 1,
            "breaks_G6_uniqueness": "absolute heavy-vector masses rescale",
            "breaks_G7_uniqueness": (
                "closed heavy-vector threshold changes at fixed matching scale"
            ),
            "breaks_G8_uniqueness": (
                "every nonzero dimension-six gauge lifetime rescales as lambda_v^4"
            ),
            "claim_of_global_parameter_minimality": False,
        },
        "independent_additional_witnesses": {
            "kappa_b": {
                "domain": "kappa_b>0",
                "effect": "448 conditional scalar masses rescale as sqrt(kappa_b)",
            },
            "flavor_boundaries": {
                "symbols": flavor["declared_tensor_symbols"],
                "raw_complex_entries_before_quotients": 50,
                "raw_real_degrees_before_quotients": 100,
                "effect": "fermion masses, Y4, scalar Wilsons and interference are not fixed",
            },
        },
        "exhibited_raw_real_dimension_including_v_b_and_all_flavor_entries": 102,
        "scope": (
            "lower-bound witness dimension before flavour quotients and measured-data "
            "fits; not a count of physically independent fitted parameters"
        ),
    }


def exact_checks() -> dict[str, bool]:
    canonical = canonical_g8_definition()
    crossing = exact_limit_crossing_witness()
    grid = exact_scale_grid_0_through_100()
    flavor = exact_flavor_and_phase_witness()
    acceptance = acceptance_matrix()
    free_vector = minimal_exhibited_free_input_vector()
    frontier = _load("physical_SM_G6_G7_frontier")
    return {
        "all_dependency_raw_and_core_hashes_match": bool(source_guard()),
        "canonical_G8_definition_is_unique": canonical["gap_id"]
        == gap_contract.G8_ID,
        "canonical_G8_has_three_dependencies": len(canonical["dependencies"]) == 3,
        "canonical_G8_has_five_acceptance_criteria": len(canonical["acceptance"]) == 5,
        "vector_scale_is_unidentified": frontier["scope"][
            "unique_absolute_tree_spectrum"
        ]
        is False,
        "gauge_lifetime_scales_exactly_as_lambda_four": exact_gauge_scale_witness(
            Fraction(7, 3)
        )["partial_lifetime_ratio_at_fixed_dimensionless_data"]
        == Fraction(2401, 81),
        "below_limit_scale_witness_is_one_sixteenth": crossing[
            "below_limit_completion"
        ]["lifetime_margin_over_limit"]
        == Fraction(1, 16),
        "above_limit_scale_witness_is_sixteen": crossing[
            "above_limit_completion"
        ]["lifetime_margin_over_limit"]
        == 16,
        "same_normalized_spectrum_crosses_finite_limit": crossing[
            "same_normalized_vector_spectrum"
        ]
        and crossing["below_limit_completion"]["below_limit"]
        and crossing["above_limit_completion"]["above_limit"],
        "vector_threshold_coefficients_are_exact": exact_gauge_scale_witness(2)[
            "threshold_log_coefficients"
        ]
        == {"SU3": Fraction(35, 4), "QED": Fraction(112, 3)},
        "scale_audit_covers_cases_zero_through_one_hundred": grid["case_range"]
        == [0, 100]
        and grid["case_count"] == 101,
        "all_101_scaling_identities_are_exact": grid[
            "all_scaling_identities_exact"
        ],
        "fifty_complex_flavor_entries_are_unfixed": flavor[
            "raw_complex_entries_before_flavour_quotients"
        ]
        == 50
        and not flavor["flavor_tensor_values_or_textures_fixed"],
        "unfixed_relative_phase_changes_total_width": flavor[
            "equal_magnitude_interference_witness"
        ]["different_total_widths"],
        "all_five_G8_acceptance_criteria_fail_closed": len(acceptance) == 5
        and all(not row["passed"] for row in acceptance.values()),
        "one_dimensional_scale_witness_already_breaks_G6_G7_G8_uniqueness": (
            free_vector["smallest_exhibited_joint_witness"]["real_dimension"] == 1
            and free_vector["smallest_exhibited_joint_witness"][
                "claim_of_global_parameter_minimality"
            ]
            is False
        ),
        "independent_raw_v_b_flavor_witness_has_102_real_coordinates": (
            free_vector[
                "exhibited_raw_real_dimension_including_v_b_and_all_flavor_entries"
            ]
            == 102
        ),
        "physical_G8_fail_closed": True,
        "release_G8_fail_closed": True,
        "authoritative_G8_fail_closed": True,
    }


def build_report() -> dict[str, Any]:
    checks = exact_checks()
    failures = sorted(name for name, passed in checks.items() if not passed)
    if failures:
        raise ArithmeticError(f"G8-frontier checks failed: {failures}")
    report: dict[str, Any] = {
        "schema": "exact_physical_sm_g8_identifiability_frontier_v1",
        "status": STATUS,
        "contract_id": CONTRACT_ID,
        "source_binding": source_guard(),
        "canonical_G8_definition": canonical_g8_definition(),
        "exact_nonidentifiability_witnesses": {
            "absolute_vector_scale": exact_gauge_scale_witness(Fraction(2)),
            "finite_limit_crossing": exact_limit_crossing_witness(),
            "flavor_and_interference": exact_flavor_and_phase_witness(),
        },
        "scale_audit_0_through_100": exact_scale_grid_0_through_100(),
        "repository_frozen_experimental_input": repository_frozen_experimental_input(),
        "acceptance_matrix": acceptance_matrix(),
        "minimal_exhibited_free_input_vector": minimal_exhibited_free_input_vector(),
        "exact_missing_inputs": exact_missing_inputs(),
        "scope": {
            "canonical_G8_contract_audited": True,
            "continuous_absolute_scale_nonidentifiability_proved": True,
            "flavor_and_interference_nonidentifiability_audited": True,
            "repository_frozen_single_channel_constraint_computed": True,
            "negative_no_go_for_future_G8_closure": False,
            "unique_proton_lifetime_or_distribution": False,
            "physical_G8": False,
            "release_G8": False,
            "authoritative_G8": False,
            "whole_model_excluded_by_conditional_points": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "verdict": (
            "The canonical G8 acceptance contract is now audited against the "
            "corrected physical-SM G6/G7 artifacts.  An exact positive vector-"
            "scale family changes a nonzero gauge-mediated lifetime as lambda^4 "
            "and crosses any finite limit while preserving the normalized "
            "spectrum.  Fifty complex flavour entries, the triplet pole matrix "
            "and relative interference phases are also unfixed.  Therefore the "
            "current repository data do not identify a unique lifetime or "
            "uncertainty distribution; physical, release and authoritative G8 "
            "remain false.  No new laboratory measurement is required merely "
            "to complete the missing theory calculations."
        ),
    }
    core = _canonical_sha256(report)
    report["core_sha256"] = core
    if EXPECTED_CORE_SHA256 and core != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"G8-frontier core drifted: expected {EXPECTED_CORE_SHA256}, observed {core}"
        )
    return _jsonable(report)


def render_markdown(report: dict[str, Any]) -> str:
    crossing = report["exact_nonidentifiability_witnesses"]["finite_limit_crossing"]
    lines = [
        "# Exact physical-SM G8 identifiability frontier v20",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Outcome",
        "",
        report["verdict"],
        "",
        "## Exact finite-limit crossing",
        "",
        "For `M_X -> lambda M_X` at fixed dimensionless data,",
        "`C -> lambda^-2 C`, `Gamma -> lambda^-4 Gamma`, and",
        "`tau -> lambda^4 tau`.",
        "",
        f"- `lambda=1/2`: margin `{crossing['below_limit_completion']['lifetime_margin_over_limit']}`",
        f"- `lambda=2`: margin `{crossing['above_limit_completion']['lifetime_margin_over_limit']}`",
        "",
        "The 101-case exact audit covers cases `0..100`.",
        "",
        "## Canonical acceptance",
        "",
    ]
    for key, row in report["acceptance_matrix"].items():
        lines.append(
            f"- {key}: `{row['passed']}` - {row['criterion']} ({row['reason']})"
        )
    lines.extend(["", "## Missing inputs", ""])
    for category, entries in report["exact_missing_inputs"].items():
        lines.append(f"### {category}")
        lines.append("")
        if entries:
            lines.extend(f"- {entry}" for entry in entries)
        else:
            lines.append("- none")
        lines.append("")
    lines.extend(
        [
            f"Checks: `{report['n_checks']}`; failures: `{report['n_failed']}`.",
            "",
            f"Core SHA256: `{report['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _write_or_check(*, check: bool) -> dict[str, Any]:
    report = build_report()
    json_bytes = _canonical_bytes(report)
    md_bytes = render_markdown(report).encode("utf-8")
    if check:
        if not OUT_JSON.exists() or OUT_JSON.read_bytes() != json_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_JSON.name}")
        if not OUT_MD.exists() or OUT_MD.read_bytes() != md_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_MD.name}")
    else:
        OUT_JSON.write_bytes(json_bytes)
        OUT_MD.write_bytes(md_bytes)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = _write_or_check(check=args.check)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
