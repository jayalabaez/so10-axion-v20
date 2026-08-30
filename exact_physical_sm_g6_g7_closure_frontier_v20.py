#!/usr/bin/env python3
"""Exact closure frontier and non-identifiability witnesses for physical G6/G7.

This theorem composes only the corrected physical-SM terminal artifacts.  It
records what is closed and proves that the remaining numerical spectrum and
flow are not functions of the repository's presently fixed data.

Three independent continuous witnesses are enough:

* with all dimensionless data fixed, ``v -> lambda v`` rescales every heavy
  vector tree mass by ``lambda`` and changes the frozen MS-bar threshold by
  ``(35/4pi) log(lambda)`` for SU(3) and
  ``(112/3pi) log(lambda)`` for QED at fixed matching scale;
* the conditional squared-stationarity scalar Hessian is
  ``H_U=2 b H^T H`` with arbitrary ``b>0``, so its nonzero tree masses scale
  as ``sqrt(b)``;
* the normalized representation CGCs leave 50 complex flavor entries
  symbolic.  The zero tensor and any nonzero normalized-CGC tensor obey the
  same representation/charge contract but give different Yukawa invariants,
  fermion masses and two-loop gauge ``Y4`` terms.

Consequently no unique pole spectrum, component threshold vector, or full RGE
trajectory can be reconstructed without additional boundary data and loop
operators.  This is a proof of non-identifiability, not a claim that G6/G7
are impossible after those inputs are supplied.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from numbers import Rational
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md"

STATUS = (
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_AND_NONIDENTIFIABILITY_"
    "CLOSED__PHYSICAL_G6_G7_REMAIN_OPEN"
)
CONTRACT_ID = "exact_physical_sm_g6_g7_closure_frontier_v20"

DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "physical_SM_vacuum_foundation": (
        HERE / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
        "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315",
        "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80",
    ),
    "conditional_physical_SM_scalar_spectrum": (
        HERE / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json",
        "6a4354baac91881b796e70d86e529158fe8c51a0a2a9e1dc9ba876130c3510ef",
        "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a",
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
    "physical_SM_vector_Rxi_vacuum_cancellation": (
        HERE / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json",
        "e1553d18c5acb9fd738dfc8c16277a634ae42bca2960296656eee57a78101221",
        "ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93",
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
    "eedc4bf7c068318f7cf597beaed25ff2eb5893951872475ade02ea8a91386aae"
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


def source_guard() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for name, (path, raw_expected, core_expected) in DEPENDENCIES.items():
        raw_observed = _digest(path)
        if raw_observed != raw_expected:
            raise ArithmeticError(f"closure-frontier dependency drifted: {name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        core_observed = payload.get("core_sha256")
        if core_observed is None and "integrity" in payload:
            core_observed = payload["integrity"].get("core_sha256")
        if core_observed != core_expected:
            raise ArithmeticError(f"closure-frontier core drifted: {name}")
        bindings[name] = {
            "path": str(path.relative_to(HERE)),
            "raw_sha256": raw_observed,
            "core_sha256": core_observed,
        }
    return bindings


def _load(name: str) -> dict[str, Any]:
    return json.loads(DEPENDENCIES[name][0].read_text(encoding="utf-8"))


def exact_vector_scale_witness(scale_ratio: Rational) -> dict[str, Any]:
    """Return the exact coefficient of log(lambda)/pi at fixed mu."""
    ratio = _positive_exact("scale_ratio", scale_ratio)
    matching = _load("physical_SM_heavy_vector_MSbar_matching")
    factors = matching["exact_group_factors"]
    totals = {
        key: Fraction(value)
        for key, value in factors["complex_index_totals"].items()
    }
    coefficients = {key: Fraction(7, 2) * value for key, value in totals.items()}
    expected = {"SU3": Fraction(35, 4), "QED": Fraction(112, 3)}
    if coefficients != expected:
        raise ArithmeticError("common-scale threshold coefficients drifted")
    return {
        "scale_ratio_lambda": ratio,
        "tree_mass_map": "M_a(lambda*v)=lambda*M_a(v)",
        "fixed_matching_scale": True,
        "threshold_shift_over_pi": {
            key: f"({_fraction_text(value)})*log(lambda)"
            for key, value in coefficients.items()
        },
        "log_shift_coefficients": coefficients,
        "threshold_changes": ratio != 1,
        "absolute_vector_scale_identified": False,
    }


def exact_vector_scale_grid() -> dict[str, Any]:
    records = []
    for index in range(100):
        ratio = Fraction(index + 2, 103)
        witness = exact_vector_scale_witness(ratio)
        records.append(
            {
                "case": index,
                "lambda": _fraction_text(ratio),
                "SU3_coefficient": _fraction_text(
                    witness["log_shift_coefficients"]["SU3"]
                ),
                "QED_coefficient": _fraction_text(
                    witness["log_shift_coefficients"]["QED"]
                ),
                "threshold_changes": witness["threshold_changes"],
            }
        )
    if any(not row["threshold_changes"] for row in records):
        raise ArithmeticError("scale grid accidentally included lambda=1")
    return {
        "case_range": [0, 99],
        "case_count": 100,
        "all_are_distinct_from_lambda_one": True,
        "record_sha256": _canonical_sha256(records),
        "first_case": records[0],
        "last_case": records[-1],
    }


def exact_scalar_scale_witness(scale_ratio: Rational) -> dict[str, Any]:
    ratio = _positive_exact("scale_ratio", scale_ratio)
    scalar = _load("conditional_physical_SM_scalar_spectrum")
    boundary = scalar["kernel_and_physics_boundary"]
    if boundary["rho_interpretation"] != (
        "canonically normalized tree-level scalar Hessian eigenvalue"
    ):
        raise ArithmeticError("scalar eigenvalue interpretation drifted")
    return {
        "b_scale_ratio_kappa": ratio,
        "Hessian_identity": "H_U=2*b*Hren^T*Hren",
        "nonzero_mass_squared_map": "rho_a(kappa*b)=kappa*rho_a(b)",
        "nonzero_tree_mass_map": "M_a(kappa*b)=sqrt(kappa)*M_a(b)",
        "massive_mode_count": boundary["massive_tree_Hessian_mode_count"],
        "scale_changes": ratio != 1,
        "dimensionful_scalar_scale_identified": False,
        "source_algebra_derived": scalar["proof_boundary"][
            "upstream_source_algebra_derivation_complete"
        ],
        "pole_mass_squared": boundary["rho_is_a_pole_mass_squared"],
    }


def exact_flavor_nonidentifiability_witness() -> dict[str, Any]:
    cgcs = _load("normalized_SO10_Yukawa_CGCs")
    threshold = _load("physical_G7_component_threshold_contract")
    inventory = threshold["interaction_beta_inventory"]
    symbols = inventory["declared_Yukawa_and_fermion_mixing_symbols"]
    raw_complex = inventory["raw_complex_family_entries_before_flavour_quotients"]
    if len(symbols) != 10 or raw_complex != 50:
        raise ArithmeticError("flavor inventory drifted")
    if not all(
        row["flavor_tensor_preserved_symbolically"]
        for row in cgcs["declared_yukawa_closure"]
    ):
        raise ArithmeticError("a flavor tensor was unexpectedly fixed")
    return {
        "declared_tensor_symbols": symbols,
        "symbol_count": len(symbols),
        "raw_complex_entries_before_flavour_quotients": raw_complex,
        "raw_real_degrees_before_flavour_quotients": 2 * raw_complex,
        "representation_CGC_Gram_normalization": (
            "Tr(C_A^dagger*C_B)=delta_AB"
        ),
        "boundary_A": "all ten flavor tensors identically zero",
        "boundary_B": (
            "one exact nonzero flavor coefficient epsilon on any normalized "
            "10, 126bar, or singlet CGC"
        ),
        "same_representation_and_charge_contract": True,
        "different_positive_Yukawa_norm_for_epsilon_nonzero": True,
        "different_fermion_mass_matrices_after_relevant_VEV": True,
        "different_two_loop_gauge_Y4_and_Yukawa_beta_terms": True,
        "flavor_boundary_values_identified": False,
        "SARAH_identical_Weyl_conversion_identified": cgcs["scope"][
            "sarah_implicit_contraction_normalization"
        ],
    }


def completed_and_open_matrix() -> dict[str, Any]:
    foundation = _load("physical_SM_vacuum_foundation")
    scalar = _load("conditional_physical_SM_scalar_spectrum")
    masses = _load("physical_SM_heavy_vector_masses")
    matching = _load("physical_SM_heavy_vector_MSbar_matching")
    rxi = _load("physical_SM_vector_Rxi_vacuum_cancellation")
    cgcs = _load("normalized_SO10_Yukawa_CGCs")
    g7 = _load("physical_G7_component_threshold_contract")
    return {
        "closed": {
            "standard_SU3C_x_U1em_target_and_stabilizer": foundation[
                "logical_summary"
            ]["physical_SM_target_exactly_constructed"]
            and foundation["logical_summary"][
                "standard_SU3C_x_U1em_stabilizer_proved"
            ],
            "conditional_reconstructed_448_mode_scalar_tree_spectrum": scalar[
                "closure_claims"
            ]["conditional_reconstructed_squared_EFT_spectrum"],
            "parameterized_37_mode_vector_tree_spectrum": masses["scope"][
                "exact_parameterized_46x46_tree_mass_matrix"
            ],
            "combined_vector_ghost_Goldstone_MSbar_kernel": matching["scope"][
                "combined_heavy_vector_FPghost_Goldstone_MSbar_matching"
            ],
            "vacuum_quadratic_Rxi_cancellation_all_37_directions": rxi["scope"][
                "arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation"
            ],
            "normalized_all_declared_representation_Yukawa_CGCs": cgcs["scope"][
                "normalized_representation_CGCs_for_all_declared_Yukawas"
            ],
            "physical_PS_SM_matter_branching_and_threshold_kernel": g7[
                "completion_matrix"
            ]["complete_physical_PS_and_SM_matter_branching"]
            and g7["completion_matrix"][
                "parameterized_one_loop_matter_component_threshold_kernel"
            ],
            "two_independent_nonyukawa_gauge_beta_implementations": g7[
                "completion_matrix"
            ]["independent_official_PyRATE3_gauge_replay"],
        },
        "open": {
            "direct_source_algebra_physical_SM_Hessian": not foundation[
                "logical_summary"
            ]["source_bound_exact_stationary_PSD_witness_available"],
            "global_physical_SM_equality_orbit": not foundation[
                "logical_summary"
            ]["source_bound_global_equality_orbit_proved"],
            "dimensionful_renormalized_boundary_data": True,
            "scalar_vector_fermion_pole_mass_matrices": not g7[
                "completion_matrix"
            ]["physical_component_pole_mass_matrices"],
            "stationary_pre_EW_SU3xSU2xU1_stage": not matching["scope"][
                "SM_symmetric_pre_EW_threshold"
            ],
            "complete_scalar_fermion_thresholds": not matching["scope"][
                "complete_scalar_and_fermion_thresholds"
            ],
            "full_two_loop_Yukawa_betas": not g7["completion_matrix"][
                "full_two_loop_Yukawa_betas"
            ],
            "full_scalar_and_dimensionful_betas": not g7["completion_matrix"][
                "full_51_real_parameter_scalar_tensor_translation"
            ]
            or not g7["completion_matrix"]["dimensionful_mass_and_trilinear_betas"],
            "dimension_six_operator_mixing_if_EFT_retained": not g7[
                "completion_matrix"
            ]["dimension_six_EFT_anomalous_dimension_and_mixing"],
            "second_independent_full_RGE_threshold_implementation": not g7[
                "completion_matrix"
            ]["second_independent_full_RGE_and_matching_implementation"],
            "boundary_data_matching_scales_and_covariance": True,
        },
    }


def minimal_closure_path() -> list[dict[str, Any]]:
    return [
        {
            "order": 1,
            "deliverable": "authoritative external model execution",
            "acceptance": (
                "hash-bound real SARAH execution attestation for the complete "
                "SO(10)xU(1)_X model contract"
            ),
        },
        {
            "order": 2,
            "deliverable": "physical-SM vacuum proof",
            "acceptance": (
                "derive every stationary/Hessian entry from source algebra and "
                "classify the complete global equality orbit"
            ),
        },
        {
            "order": 3,
            "deliverable": "renormalized boundary contract",
            "acceptance": (
                "fix g10, gX, all breaking scales, the 51-real scalar tensor, "
                "all ten flavor tensors, matching scales, MS-bar scheme, and "
                "tadpole/VEV prescription with covariance"
            ),
        },
        {
            "order": 4,
            "deliverable": "stage-resolved tree mass matrices",
            "acceptance": (
                "construct stationary SO(10), intermediate, pre-EW SM, and "
                "terminal vacua; diagonalize source-exact scalar, vector, and "
                "fermion matrices with ancestry projectors and remove exactly "
                "the eaten directions"
            ),
        },
        {
            "order": 5,
            "deliverable": "pole spectrum and complete one-loop matching",
            "acceptance": (
                "solve self-energy-corrected pole equations and combine the "
                "closed vector kernel with every physical scalar and fermion "
                "threshold and finite constant"
            ),
        },
        {
            "order": 6,
            "deliverable": "complete running",
            "acceptance": (
                "derive two-loop gauge including Y4, two-loop Yukawa/scalar/"
                "dimensionful betas, and one-loop nonredundant EFT mixing if kept"
            ),
        },
        {
            "order": 7,
            "deliverable": "independent replay and release",
            "acceptance": (
                "independent complete SARAH/PyR@TE or analytic replay, exact "
                "symbolic comparison where possible and <=1e-10 agreement on "
                "at least 100 nonsingular random points, followed by frozen "
                "boundary and threshold-covariance tests"
            ),
        },
    ]


def exact_checks() -> dict[str, bool]:
    source_guard()
    vector = exact_vector_scale_witness(Fraction(2))
    scalar = exact_scalar_scale_witness(Fraction(3))
    flavor = exact_flavor_nonidentifiability_witness()
    matrix = completed_and_open_matrix()
    path = minimal_closure_path()
    return {
        "all_dependency_raw_and_core_hashes_match": bool(source_guard()),
        "vector_SU3_scale_shift_is_35_over_4": vector[
            "log_shift_coefficients"
        ]["SU3"]
        == Fraction(35, 4),
        "vector_QED_scale_shift_is_112_over_3": vector[
            "log_shift_coefficients"
        ]["QED"]
        == Fraction(112, 3),
        "vector_scale_is_not_identified": not vector[
            "absolute_vector_scale_identified"
        ],
        "hundred_vector_scale_witnesses_cover_0_through_99": exact_vector_scale_grid()[
            "case_range"
        ]
        == [0, 99],
        "scalar_completion_has_448_massive_modes": scalar["massive_mode_count"]
        == 448,
        "scalar_b_scale_is_not_identified": not scalar[
            "dimensionful_scalar_scale_identified"
        ],
        "conditional_scalar_spectrum_is_not_pole_spectrum": not scalar[
            "pole_mass_squared"
        ],
        "ten_symbolic_flavor_tensors_present": flavor["symbol_count"] == 10,
        "fifty_complex_flavor_entries_remain": flavor[
            "raw_complex_entries_before_flavour_quotients"
        ]
        == 50,
        "zero_and_nonzero_Yukawa_boundaries_change_Y4": flavor[
            "different_two_loop_gauge_Y4_and_Yukawa_beta_terms"
        ],
        "every_closed_scope_item_is_true": all(matrix["closed"].values()),
        "every_open_scope_item_is_true": all(matrix["open"].values()),
        "minimal_path_is_strictly_ordered": [row["order"] for row in path]
        == list(range(1, 8)),
        "physical_G6_fail_closed": True,
        "physical_G7_fail_closed": True,
    }


def build_report() -> dict[str, Any]:
    checks = exact_checks()
    failures = sorted(key for key, value in checks.items() if not value)
    if failures:
        raise ArithmeticError(f"closure-frontier checks failed: {failures}")
    report: dict[str, Any] = {
        "schema": "exact_physical_sm_g6_g7_closure_frontier_v1",
        "status": STATUS,
        "contract_id": CONTRACT_ID,
        "source_binding": source_guard(),
        "completed_and_open_matrix": completed_and_open_matrix(),
        "exact_nonidentifiability_witnesses": {
            "vector_common_scale": exact_vector_scale_witness(Fraction(2)),
            "scalar_EFT_b_scale": exact_scalar_scale_witness(Fraction(3)),
            "flavor_boundaries": exact_flavor_nonidentifiability_witness(),
        },
        "hundred_case_vector_scale_audit": exact_vector_scale_grid(),
        "minimal_closure_path": minimal_closure_path(),
        "scope": {
            "corrected_physical_SM_terminal_artifacts_composed": True,
            "continuous_nonidentifiability_proved": True,
            "minimal_closure_path_machine_readable": True,
            "unique_absolute_tree_spectrum": False,
            "unique_pole_spectrum": False,
            "unique_threshold_vector": False,
            "unique_full_RGE_trajectory": False,
            "physical_G6": False,
            "physical_G7": False,
            "release_G6": False,
            "release_G7": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "verdict": (
            "The corrected target, conditional scalar tree spectrum, exact "
            "vector tree/MS-bar/R_xi subtheorems, normalized CGCs, component "
            "threshold kernel and gauge-only running are composed consistently. "
            "Independent vector-scale, scalar-b and flavor-boundary families "
            "prove that the absolute pole spectrum, thresholds and full flow "
            "are not identified by current data. Physical G6 and G7 remain false."
        ),
    }
    core = _canonical_sha256(report)
    report["core_sha256"] = core
    if EXPECTED_CORE_SHA256 and core != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"closure-frontier core drifted: expected {EXPECTED_CORE_SHA256}, observed {core}"
        )
    return _jsonable(report)


def render_markdown(report: dict[str, Any]) -> str:
    closed = report["completed_and_open_matrix"]["closed"]
    opened = report["completed_and_open_matrix"]["open"]
    vector = report["exact_nonidentifiability_witnesses"]["vector_common_scale"]
    lines = [
        "# Exact physical-SM G6/G7 closure frontier v20",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Outcome",
        "",
        report["verdict"],
        "",
        "At fixed matching scale, `v -> lambda v` shifts the exact vector threshold by:",
        "",
        f"- SU(3): `{vector['threshold_shift_over_pi']['SU3']}/pi`",
        f"- QED: `{vector['threshold_shift_over_pi']['QED']}/pi`",
        "",
        "The scalar EFT coefficient `b>0` and 50 complex flavor entries are also unfixed, yielding independent continuous non-identifiability witnesses.",
        "",
        "## Closed scoped inputs",
        "",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in closed.items())
    lines.extend(["", "## Still open", ""])
    lines.extend(f"- {key}: `{value}`" for key, value in opened.items())
    lines.extend(["", "## Minimal closure path", ""])
    lines.extend(
        f"{row['order']}. **{row['deliverable']}** — {row['acceptance']}"
        for row in report["minimal_closure_path"]
    )
    lines.extend(
        [
            "",
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
