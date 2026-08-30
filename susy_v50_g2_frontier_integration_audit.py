#!/usr/bin/env python3
"""Integrate the V50 local-regulator, same-action, rematch, and tensor audits.

The frozen G2 rule is conjunctive: C1 through C7 must pass for one retained
action in one declared regulator scheme.  This audit records genuine V50
closures while keeping G2 fail-closed on any remaining clause.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import susy_v50_finite_moose_action_spec as finite_action_spec


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_G2_FRONTIER_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_G2_FRONTIER_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_g2_frontier_integration_audit.py"
ACTION_SPEC_PATH = ROOT / "susy_v50_finite_moose_action_spec.py"

INPUTS = {
    "v49_master": ROOT / "SUSY_V49_G2_FRONTIER_INTEGRATION_AUDIT.json",
    "local_regulator": ROOT / "SUSY_V50_LOCAL_CONSTRAINED_TRANSPORT_REGULATOR_AUDIT.json",
    "full_collar": ROOT / "SUSY_V50_FULL_SAME_ACTION_COLLAR_AUDIT.json",
    "finite_moose_bridge": ROOT / "SUSY_V50_FINITE_MOOSE_SAME_ACTION_BRIDGE_AUDIT.json",
    "complex_nambu_referee": ROOT / "SUSY_V50_COMPLEX_NAMBU_REFEREE_AUDIT.json",
    "second_profile": ROOT / "SUSY_V50_SECOND_PROFILE_CLEBSCH_AUDIT.json",
    "strict_c5": ROOT / "SUSY_V50_C5_STRICT_REMATCH_AUDIT.json",
    "clifford_tensors": ROOT / "SUSY_V50_CLIFFORD_TENSOR_EXTENSION_AUDIT.json",
    "phi_sigma_tensors": ROOT / "SUSY_V50_PHI_SIGMA_FORM_TENSOR_AUDIT.json",
    "ps_intertwiner": ROOT / "SUSY_V50_PS_INTERTWINER_BASIS_AUDIT.json",
    "c7_incidence": ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json",
}

STATUS = (
    "V50_G2_LOCAL_DECONSTRUCTION_REGULATOR_C2_CLOSED__"
    "ABSTRACT_FINITE_MOOSE_NAMBU_AND_POSITIVITY_WITNESS_CERTIFIED__"
    "PHYSICAL_V47_V49_IDENTIFICATION_FAIL_CLOSED_C3_C4_PARTIAL__"
    "TREE_QUADRATIC_C5_PROFILE_REMATCH_THROUGH_O_LAMBDA_MINUS1_CERTIFIED__"
    "CARTESIAN_TENSORS_CONJUGATE_MAPS_AND_176_ROW_INCIDENCE_CENSUS_CERTIFIED__"
    "C5_AFFINE_LOOP_THRESHOLD_SCALE_MAPS_AND_C7_RESOLVED_INCIDENCE_INCOMPLETE__"
    "G2_FAIL_CLOSED__ONE_OF_EIGHT_FULL_GATES_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_hashed_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"input is not an object: {path.name}")
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"stale core hash: {path.name}")
    return value


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, ACTION_SPEC_PATH, *INPUTS.values()]
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in paths
    ]


def closure_assessment() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "name": "fixed_order_action_completeness",
            "status": "pass",
            "landed": (
                "V49 remains the complete abstract retained-order census: 23 pure-source "
                "quartics in 12 sectors, mu_H, all H/Hc portals, mixed Kahler blocks, "
                "FI/gauge coordinates, and the one-normal-derivative IBP/EOM quotient."
            ),
            "blocker": "none for C1 at the declared abstract invariant-tensor order",
        },
        {
            "id": "C2",
            "name": "explicit_regulator",
            "status": "pass",
            "landed": (
                "A finite supersymmetric Spin(10)xU(1)_F gauge moose localizes the source "
                "transport.  Its fundamental action is site-local or nearest-neighbour, its "
                "constraint determinant is link-independent, and its positive completion has "
                "one intended source profile plus only cutoff-scale vectorlike pairs."
            ),
            "blocker": (
                "none for the declared finite-cutoff deconstruction regulator; a renormalizable "
                "continuum 5D UV completion is outside the frozen G2 requirement"
            ),
        },
        {
            "id": "C3",
            "name": "variational_domain_and_self_adjointness",
            "status": "partial",
            "landed": (
                "The continuum A/Xi/C/O7/O8 normal form and an independent finite-N complex "
                "Nambu construction are mathematically self-adjoint for their declared abstract "
                "matrices.  The finite witness has one canonical action hash and retains endpoint "
                "auxiliaries instead of imposing an energy-dependent domain."
            ),
            "blocker": (
                "The abstract matrices are not yet identified with the physical V47/V49 action: "
                "the explicit V47 Hessian pullback, 465x22 gauge-orbit map/Z-projector and Ward "
                "identity, coupled endpoint/link Goldstone R_xi block, physical invariant-tensor "
                "lift, and endpoint-auxiliary representation assignment are missing."
            ),
        },
        {
            "id": "C4",
            "name": "positive_full_kinetic_form",
            "status": "partial",
            "landed": (
                "The canonical 5,303-coordinate abstract witness has an exact uniform derivative "
                "bound, positive complex Nambu metric, positive mixed-Kahler Schur bounds, and a "
                "candidate 5,097-coordinate gauge-reduced restriction."
            ),
            "blocker": (
                "Its 443+22 source split, quotient projector, R_xi Goldstone mixing, auxiliary "
                "sector, and A/Xi/C/R7/R8/Z tensor lift are abstract placeholders rather than an "
                "assembled positive metric for the physical retained theory."
            ),
        },
        {
            "id": "C5",
            "name": "counterterm_and_matching_scheme",
            "status": "partial",
            "landed": (
                "A genuinely independent smooth profile exposes the O(1) noncommuting profile "
                "dependence.  The exact transfer counterterm C_T=T_square T_smooth^-1 is "
                "symplectic.  Its zeroth and first spectral jets H0,H1 decompose exactly into "
                "retained local A/Xi/C blocks; fixed transfer and endpoint-current conditions "
                "then rematch the homogeneous tree quadratic sector through O(Lambda^-1), with "
                "residuals scaling as O(Lambda^-2) inside the positive cone."
            ),
            "blocker": (
                "The affine/distributed-current and source-functional profile jets, one-loop 1PI "
                "divergences and operator mixing, finite deconstruction/link thresholds, "
                "bare-to-DRbar coefficient maps, and beta-function cancellation of matching-scale "
                "dependence through O(Lambda^-1) have not been calculated."
            ),
        },
        {
            "id": "C6",
            "name": "selector_and_naturalness_policy",
            "status": "pass",
            "landed": (
                "Every retained invariant direction is admitted with an independent matching "
                "coefficient; finite-part zeros are not misrepresented as symmetry predictions, "
                "and higher orders have an explicit remainder assignment."
            ),
            "blocker": "none for the declared fixed-order Wilsonian policy",
        },
        {
            "id": "C7",
            "name": "action_to_full_tower_Wilson_matching",
            "status": "partial",
            "landed": (
                "The complete abstract same-action kernel now includes the full quadratic collar, "
                "undivided characteristic, poles and residues.  Normalized Cartesian generating "
                "tensors exist for the 1,10,45,120,126 and 210 spinor representation channels "
                "and for Phi-Sigma maps to 10,120 and 126; their conjugate orientations and Hodge "
                "chirality flip are now tested.  Basis covariance is explicit, and all 176 V49 "
                "schema rows have been enumerated without promoting unresolved candidates."
            ),
            "blocker": (
                "The 168 charge-neutral candidate rows omit resolved Haar multiplicities and "
                "normalized tensor/copy IDs; the eight PS string rows omit structured ancestry, "
                "per-term charge, parity projectors and tensor IDs.  The common PS Chevalley/"
                "multiplicity intertwiners and final contracted physical Wilson-coefficient array "
                "are therefore still absent."
            ),
        },
    ]


def exact_results(
    local: Mapping[str, Any],
    collar: Mapping[str, Any],
    bridge: Mapping[str, Any],
    nambu: Mapping[str, Any],
    profile: Mapping[str, Any],
    strict_c5: Mapping[str, Any],
    clifford: Mapping[str, Any],
    phi_sigma: Mapping[str, Any],
    intertwiner: Mapping[str, Any],
    c7_incidence: Mapping[str, Any],
) -> list[dict[str, Any]]:
    nc = local["numerical_certificate"]
    same = collar["representative_same_action_certificate"]
    rematch = profile["second_profile_certificate"]
    strict_rematch = strict_c5["second_profile_rematch_certificate"]
    return [
        {
            "id": "E37",
            "result": "finite local constrained-transport regulator",
            "statement": (
                "The N-link supersymmetric gauge moose replaces the V49 finite-range bilocal "
                "coupling by local site/link interactions.  Exact elimination reconstructs the "
                "ordered Wilson chain without new source poles."
            ),
            "value": {
                "source_components": nc["original_source_component_count"],
                "intended_zero_modes": nc["intended_source_component_zero_modes"],
                "extra_light_profiles": nc[
                    "additional_massless_source_profiles_in_positive_completion"
                ],
                "constraint_determinant": [
                    nc["constraint_jacobian_determinant_real"],
                    nc["constraint_jacobian_determinant_imag"],
                ],
                "finite_N": nc["parameters"]["N"],
                "heavy_vectorlike_pairs": nc["heavy_vectorlike_chiral_pairs"],
            },
        },
        {
            "id": "E38",
            "result": "abstract continuum collar theorem",
            "statement": (
                "The IBP-reduced A/Xi/C/R7/R8/Z action supplies one symplectic transfer, one "
                "variational maximal-isotropic domain, and one nonempty positive kinetic cone for "
                "its abstract collar inputs.  This theorem is not by itself a finite-moose physical "
                "V47/V49 identification certificate."
            ),
            "value": {
                "sp_basis_rank": collar["sp_2n_span_certificate"]["matrix_rank"],
                "sp_expected_dimension": collar["sp_2n_span_certificate"][
                    "expected_dimension_n_2n_plus_1"
                ],
                "minimum_K_singular_value": same["normal_form"][
                    "minimum_K_singular_value_on_21_point_grid"
                ],
                "minimum_collar_metric_eigenvalue": same["positive_norm"][
                    "collar_metric_min_eigenvalue"
                ],
                "J_unitarity_residual": same["transfer"][
                    "real_slice_J_unitary_residual"
                ],
            },
        },
        {
            "id": "E39",
            "result": "hashed finite-matrix witness and physical-identification obstruction",
            "statement": (
                "One canonical finite-N action hash supports an exact complex-Nambu Hermiticity, "
                "uniform derivative and 5,303-coordinate positivity witness.  Independent review "
                "proves that physical C3/C4 remain partial because five representation/gauge maps "
                "are not executable."
            ),
            "value": {
                "shared_action_sha256": bridge["shared_action_sha256"],
                "bridge_decision": bridge["clause_decision"],
                "referee_decision": nambu["clause_decision"],
                "physical_identification_obstructions": nambu[
                    "physical_identification_obstructions"
                ],
                "uniform_derivative": nambu[
                    "exact_uniform_fifth_derivative_certificate"
                ],
                "positive_metric": nambu["full_positive_metric_and_C4"],
            },
        },
        {
            "id": "E40",
            "result": "abstract pole/residue/Wilson witness",
            "statement": (
                "The undivided enlarged determinant and reduced kernel agree away from auxiliary "
                "poles; three roots, a simple first pole, its full residue, Euclidean locality, "
                "and a finite Wilson response are executable in the abstract collar action."
            ),
            "value": same,
        },
        {
            "id": "E41",
            "result": "second-profile obstruction and strict tree rematch",
            "statement": (
                "Noncommuting strong blocks retain an O(1) profile difference, disproving naive "
                "universality.  The exact symplectic correction and its first spectral jet are "
                "realized by retained A/Xi/C layers; corrected homogeneous transfer and fixed "
                "endpoint-current Wilson errors scale as O(Lambda^-2).  Affine and loop/scale "
                "matching remain absent."
            ),
            "value": {
                "thin_limit_difference": rematch["noncommuting_thin_limit_estimate"],
                "counterterm_distance_from_identity": rematch[
                    "counterterm_distance_from_identity"
                ],
                "rematch_residual": rematch["exact_full_matrix_counterterm_residual"],
                "counterterm_symplectic_residual": rematch[
                    "counterterm_symplectic_residual"
                ],
                "strict_tree_quadratic_rematch": strict_rematch,
                "strict_C5_decision": strict_c5["C5_decision"],
            },
        },
        {
            "id": "E42",
            "result": "normalized Clifford component tensors",
            "statement": (
                "Generating arrays for 16x16->120 and 16xbar16->45,210 are Hilbert-Schmidt "
                "normalized and covariant under all 45 SO(10) generators, extending the certified "
                "1,10,126 representation maps.  This is not an operator-incidence certificate."
            ),
            "value": clifford["certified_maps"],
        },
        {
            "id": "E43",
            "result": "normalized Phi-Sigma form tensors",
            "statement": (
                "The Phi210 x Sigma126 maps to 120 and chiral 126 have full target rank, isotropic "
                "Gram matrices, and dense all-generator covariance certificates; a separate audit "
                "now verifies the conjugate orientation and Hodge-chirality flip."
            ),
            "value": phi_sigma["certificates"],
        },
        {
            "id": "E44",
            "result": "basis-ambiguity theorem",
            "statement": (
                "Unitary rotations within repeated PS weight spaces are conventions, not missing "
                "physics: currents, kernels and projectors transform covariantly and leave the "
                "Wilson functional invariant.  The identity is universal; the executable witness "
                "uses representative blocks rather than the actual 120/126/210 weight blocks, and "
                "the explicit convention bridge is still absent."
            ),
            "value": {
                "decision": intertwiner["ambiguity_decision"],
                "certificate": intertwiner["certificate"],
            },
        },
        {
            "id": "E45",
            "result": "conjugate maps and exhaustive schema-row incidence census",
            "statement": (
                "All available conjugate Cartesian maps are involutive and orthonormal.  The "
                "census enumerates 176 retained schema rows and proves why none of the 168 "
                "charge-neutral candidates or eight aggregate PS rows can yet be instantiated as "
                "a complete physical tensor/current incidence row."
            ),
            "value": {
                "counts": c7_incidence["counts"],
                "coverage_decision": c7_incidence["coverage_decision"],
                "smallest_missing_schema_data": c7_incidence[
                    "smallest_missing_schema_data"
                ],
                "conjugate_maps": c7_incidence["conjugate_maps"],
            },
        },
        {
            "id": "E46",
            "result": "V50 fail-closed decision",
            "statement": (
                "C1, C2 and C6 pass.  Physical C3/C4, strict C5 and component-resolved C7 "
                "remain partial, so the seven-clause conjunction is false and G2 is not promoted."
            ),
            "value": {
                "passed_clauses": ["C1", "C2", "C6"],
                "full_gate_count": 1,
                "G2_closed": False,
            },
        },
    ]


def unresolved_defects() -> list[dict[str, str]]:
    return [
        {
            "id": "D13",
            "defect": "physical_same_action_identification_missing",
            "statement": (
                "Bind the abstract finite matrix to the retained theory with the explicit V47 "
                "465x465 Hessian pullback; rank-22 orbit map, Z-projector and Ward identity; coupled "
                "five-Goldstone R_xi block; normalized V49 A/Xi/C/R7/R8/Z tensor lift; and charged, "
                "anomaly-safe endpoint auxiliary assignments."
            ),
        },
        {
            "id": "D14",
            "defect": "coefficient_level_profile_rematch_missing",
            "statement": (
                "Extend the certified homogeneous transfer rematch to all affine/distributed "
                "currents and source-functional jets; compute the one-loop "
                "1PI mixing, finite-N/link thresholds and bare-to-DRbar maps; then prove matching-"
                "scale cancellation through O(Lambda^-1)."
            ),
        },
        {
            "id": "D15",
            "defect": "resolved_component_incidence_and_PS_bridge_missing",
            "statement": (
                "Resolve the Haar multiplicity and normalized tensor/copy IDs of all 168 candidate "
                "rows; structure the eight PS rows with ancestry, charge and parity IDs; freeze the "
                "PS Chevalley/multiplicity intertwiners; then emit the complete contracted physical "
                "Wilson array in one convention."
            ),
        },
    ]


def updated_gate_ledger(v49: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v49["gate_ledger"])
    for row in ledger:
        if row["gate"] == "G2":
            row.update(
                {
                    "closed": False,
                    "advance": (
                        "V50 closes the finite local regulator (C2), constructs a hashed abstract "
                        "finite-moose complex-Nambu/positivity witness, completes conjugate Cartesian "
                        "maps, and exhaustively enumerates all 176 available component-incidence rows."
                    ),
                    "blocker": (
                        "Physical C3/C4 lack five V47/V49 representation/gauge identifications; C5 "
                        "lacks affine, loop, threshold and scale rematching; C7 lacks resolved tensor/"
                        "copy incidence, the Cartesian-to-PS bridge, and the physical Wilson array."
                    ),
                }
            )
    return ledger


def updated_stage_ledger(v49: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v49["stage_ledger"])
    for row in ledger:
        if row["stage"] == "S0":
            row["passed"] = (
                "exact coupled neutral-210 branch, 443 generic massive physical source chirals, "
                "strictly 4D sources, and a finite local transport regulator with one intended "
                "source zero profile and only vectorlike cutoff pairs"
            )
            row["missing"] = "radion dynamics and global branch selection (outside G2)"
        elif row["stage"] == "S2":
            row["status"] = "OPEN_WITH_ABSTRACT_FINITE_NAMBU_WITNESS"
            row["passed"] = (
                "local finite deconstruction regulator; abstract full A/Xi/C/O7/O8 transfer and "
                "hashed finite-matrix complex-Nambu/positive-metric witness"
            )
            row["missing"] = (
                "physical V47 Hessian/orbit/Rxi/tensor/auxiliary identification; affine and loop/"
                "threshold/scale rematch; complete physical pole tower"
            )
        elif row["stage"] == "S3":
            row["status"] = "OPEN_WITH_NORMALIZED_CARTESIAN_TENSOR_PACKAGE"
            row["passed"] = (
                "complete abstract retained action, normalized Cartesian spinor and Phi-Sigma "
                "generating/conjugate tensors, basis covariance, and a 176-row fail-closed census"
            )
            row["missing"] = (
                "resolved Haar/tensor-copy incidence, PS Chevalley/multiplicity bridge, fully "
                "contracted physical Wilson array, B/L ring and rates"
            )
    return ledger


def build_report() -> dict[str, Any]:
    loaded = {name: load_hashed_json(path) for name, path in INPUTS.items()}
    v49 = loaded["v49_master"]
    local = loaded["local_regulator"]
    collar = loaded["full_collar"]
    bridge = loaded["finite_moose_bridge"]
    nambu = loaded["complex_nambu_referee"]
    profile = loaded["second_profile"]
    strict_c5 = loaded["strict_c5"]
    clifford = loaded["clifford_tensors"]
    phi_sigma = loaded["phi_sigma_tensors"]
    intertwiner = loaded["ps_intertwiner"]
    c7_incidence = loaded["c7_incidence"]
    clauses = closure_assessment()
    passed = [row["id"] for row in clauses if row["status"] == "pass"]
    gates = updated_gate_ledger(v49)

    nc = local["numerical_certificate"]
    rematch = profile["second_profile_certificate"]
    integrity = {
        "all_input_core_hashes_valid": True,
        "V49_started_with_only_G1_closed": (
            sum(bool(row["closed"]) for row in v49["gate_ledger"]) == 1
            and next(row for row in v49["gate_ledger"] if row["gate"] == "G1")["closed"]
        ),
        "local_regulator_fundamental_action_is_local": (
            local["decision"]["C2_explicit_regulator_passes"]
            and local["decision"]["fundamental_action_site_or_nearest_neighbour_local"]
            and local["decision"]["fundamental_endpoint_to_interior_Wilson_line_absent"]
        ),
        "local_regulator_has_only_intended_light_source_profiles": (
            nc["original_source_component_count"]
            == nc["intended_source_component_zero_modes"]
            == 465
            and nc["additional_massless_source_profiles_in_positive_completion"] == 0
            and nc["source_replica_propagating_poles_in_exact_auxiliary_limit"] == 0
        ),
        "local_regulator_preserves_G1": local["decision"]["G1_anomaly_closure_preserved"],
        "abstract_collar_integrity_passes": (
            collar["n_failed_integrity_checks"] == 0
            and all(collar["integrity_checks"].values())
        ),
        "shared_abstract_action_fingerprint_matches": (
            bridge["shared_action_sha256"] == nambu["shared_action_sha256"]
            == finite_action_spec.action_fingerprint()
        ),
        "abstract_finite_matrix_C3_C4_witness_passes": (
            bridge["clause_decision"][
                "C3_same_action_variational_domain_and_self_adjointness"
            ].startswith("PARTIAL_ABSTRACT_MATRIX_PASS")
            and bridge["clause_decision"][
                "C4_same_action_full_kinetic_positivity"
            ].startswith("PARTIAL_ABSTRACT_MATRIX_PASS")
            and nambu["clause_decision"]["abstract_finite_matrix_C3_witness"] == "PASS"
            and nambu["clause_decision"]["abstract_finite_matrix_C4_witness"] == "PASS"
            and bridge["n_failed_integrity_checks"] == 0
            and nambu["n_failed_integrity_checks"] == 0
            and all(bridge["integrity_checks"].values())
            and all(nambu["integrity_checks"].values())
        ),
        "physical_C3_C4_are_fail_closed": (
            nambu["clause_decision"][
                "C3_physical_same_action_domain_and_self_adjointness"
            ] == "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
            and nambu["clause_decision"]["C4_physical_full_kinetic_positivity"]
            == "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
            and bridge["physical_identification_obstruction"]["status"]
            == "OPEN_FIVE_EXPLICIT_MAPS_REQUIRED"
        ),
        "five_physical_identification_maps_are_missing": (
            len(bridge["physical_identification_obstruction"]["missing_maps"]) == 5
            and len(nambu["physical_identification_obstructions"]) == 5
            and {
                row["id"] for row in nambu["physical_identification_obstructions"]
            }
            == {
                "V47_HESSIAN_PULLBACK",
                "GAUGE_ORBIT_PROJECTOR",
                "COUPLED_RXI_GOLDSTONE_BLOCK",
                "ENDPOINT_AUXILIARY_REPRESENTATIONS",
                "V49_INVARIANT_TENSOR_LIFT",
            }
        ),
        "A_Xi_C_span_full_sp8": (
            collar["sp_2n_span_certificate"]["spanned"]
            and collar["sp_2n_span_certificate"]["matrix_rank"] == 36
        ),
        "second_profile_has_O1_noncommuting_obstruction": (
            rematch["noncommuting_thin_limit_estimate"] > 0.1
        ),
        "exact_transfer_rematch_passes": (
            rematch["exact_full_matrix_counterterm_residual"] < 1.0e-12
            and rematch["counterterm_symplectic_residual"] < 1.0e-10
        ),
        "tree_quadratic_C5_rematch_is_retained_and_second_order": (
            strict_c5["C5_decision"]["tree_quadratic_profile_rematch"]
            == "PASS_THROUGH_O_LAMBDA_MINUS1"
            and strict_c5["C5_decision"][
                "unmapped_homogeneous_quadratic_and_fixed_endpoint_current_ambiguity"
            ] is False
            and strict_c5["n_failed_integrity_checks"] == 0
            and all(strict_c5["integrity_checks"].values())
        ),
        "C5_is_not_overpromoted": (
            next(row for row in clauses if row["id"] == "C5")["status"] == "partial"
            and strict_c5["C5_decision"]["status"] == "PARTIAL_NOT_CLOSED"
            and not strict_c5["G2_decision"]["closed"]
        ),
        "clifford_tensor_checks_pass": all(clifford["checks"][name] for name in (
            "16x16_to_120_orthonormal",
            "16x16bar_to_45_orthonormal",
            "16x16bar_to_210_orthonormal",
            "16x16_to_120_covariant",
            "16x16bar_to_45_covariant",
            "16x16bar_to_210_covariant",
        )),
        "phi_sigma_tensor_checks_pass": all(
            value for name, value in phi_sigma["checks"].items() if name != "fail_closed"
        ),
        "basis_rotations_are_conventional_but_C7_is_partial": (
            intertwiner["checks"]["external_CG_not_required"]
            and intertwiner["checks"]["wilson_invariant"]
            and intertwiner["checks"]["projector_covariant"]
            and intertwiner["C7_decision"]["verdict"] == "PARTIAL"
        ),
        "C7_conjugate_maps_and_176_row_census_pass_fail_closed": (
            c7_incidence["counts"]["total_rows"] == 176
            and c7_incidence["counts"]["UNINSTANTIATED_ABSTRACT_HAAR_DIRECTION"] == 168
            and c7_incidence["counts"]["UNINSTANTIATED_PS_STRING_ROW"] == 8
            and c7_incidence["coverage_decision"]["C7"] == "PARTIAL"
            and all(c7_incidence["checks"].values())
        ),
        "exactly_three_clauses_pass": passed == ["C1", "C2", "C6"],
        "G2_conjunction_is_false": len(passed) != len(clauses),
        "only_G1_is_closed_after_V50": (
            sum(bool(row["closed"]) for row in gates) == 1
            and next(row for row in gates if row["gate"] == "G1")["closed"]
        ),
    }
    failures = [name for name, value in integrity.items() if not value]
    if failures:
        raise RuntimeError("V50 master integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v50-g2-frontier-integration-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "G2_closed": False,
            "full_gates_closed": 1,
            "closed_gates": ["G1"],
            "passed_G2_clauses": passed,
            "statement": (
                "V50 closes the finite local-regulator clause C2 and raises G2 from two to three "
                "passed clauses.  It also proves strong abstract C3/C4 matrix theorems, but an "
                "adversarial audit rejects their physical V47/V49 identification.  Physical C3, "
                "C4, strict C5 and component-resolved C7 remain partial."
            ),
            "claim_scope": (
                "mathematical fixed-order EFT progress only; not a complete theory, continuum "
                "UV completion, phenomenological fit, or empirical validation"
            ),
        },
        "frozen_G2_contract": v49["frozen_G2_contract"],
        "G2_closure_assessment": clauses,
        "number_of_clauses": len(clauses),
        "fully_passed_clauses": passed,
        "V50_exact_results": exact_results(
            local,
            collar,
            bridge,
            nambu,
            profile,
            strict_c5,
            clifford,
            phi_sigma,
            intertwiner,
            c7_incidence,
        ),
        "unresolved_defects": unresolved_defects(),
        "smallest_next_closure_patch": [
            (
                "Physically bind the finite action by emitting the V47 Hessian pullback; 465x22 "
                "orbit map/Z-projector/Ward identity; coupled R_xi Goldstone block; normalized V49 "
                "tensor lift; and anomaly-safe endpoint-auxiliary representations."
            ),
            (
                "Complete affine/distributed-current and source-functional profile jets; compute "
                "the one-loop 1PI mixing, finite-N/link thresholds and bare-to-DRbar maps; then "
                "prove subtraction-scale cancellation through O(Lambda^-1)."
            ),
            (
                "Resolve Haar multiplicities and normalized tensor/copy IDs for all 168 candidates; "
                "structure the eight PS rows with ancestry, charge and parity; declare the PS "
                "Chevalley/multiplicity intertwiners; then emit the physical Wilson array."
            ),
        ],
        "gate_ledger": gates,
        "stage_ledger": updated_stage_ledger(v49),
        "route_decision": (
            "Continue only with the three explicit defect families D13-D15.  Do not invent "
            "additional fields or promote G2: the abstract matrix witness is reusable, but it must "
            "first be identified with the physical retained action before C3/C4 can close."
        ),
        "input_core_hashes": {name: value["core_sha256"] for name, value in loaded.items()},
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            {
                "title": "Marti--Pomarol: 5D supersymmetry in N=1 superfields",
                "url": "https://arxiv.org/abs/hep-th/0106256",
            },
            {
                "title": "Hebecker: gauge-covariant brane operators",
                "url": "https://arxiv.org/abs/hep-ph/0112230",
            },
            {
                "title": "Arkani-Hamed--Cohen--Georgi: (De)constructing Dimensions",
                "url": "https://arxiv.org/abs/hep-th/0104005",
            },
            {
                "title": "Falkowski--Nilles--Olechowski--Pokorski: supersymmetric deconstruction on orbifolds",
                "url": "https://arxiv.org/abs/hep-th/0212206",
            },
            {
                "title": "von Gersdorff et al.: interval boundary action principle",
                "url": "https://arxiv.org/abs/hep-th/0411133",
            },
            {
                "title": "del Aguila et al.: thin-defect EFT and classical renormalization",
                "url": "https://arxiv.org/abs/hep-ph/0601222",
            },
            {
                "title": "Barcelo--Mitra--Moreau: finite-width brane/KK limit ordering",
                "url": "https://arxiv.org/abs/1408.1852",
            },
            {
                "title": "Nath--Syed: SO(10) spinor contraction channels",
                "url": "https://arxiv.org/abs/hep-th/0109116",
            },
        ],
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    clauses = "\n".join(
        f"| {row['id']} | {row['name']} | {row['status']} | {row['landed']} | {row['blocker']} |"
        for row in report["G2_closure_assessment"]
    )
    exact = "\n".join(
        f"- **{row['id']} - {row['result']}:** {row['statement']}"
        for row in report["V50_exact_results"]
    )
    defects = "\n".join(
        f"- **{row['id']} - {row['defect']}:** {row['statement']}"
        for row in report["unresolved_defects"]
    )
    patch = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["smallest_next_closure_patch"], 1)
    )
    gates = "\n".join(
        f"| {row['gate']} | {'closed' if row['closed'] else 'open'} | {row['advance']} | {row['blocker']} |"
        for row in report["gate_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']})" for row in report["primary_sources"]
    )
    return f"""# V50 G2 frontier integration audit

Status: `{report['status']}`

## Scientific verdict

V50 closes one additional clause: the finite local supersymmetric
deconstruction regulator (`C2`).  Together with V49's `C1` and `C6`,
**three of the seven G2 clauses now pass**.

**G2 remains open.  Full gates closed: 1 / 8 - G1 only.**

Four clauses remain partial.  `C3/C4` have strong abstract finite-matrix
witnesses but lack five physical V47/V49 identification maps.  `C5` needs
affine, loop, threshold and scale rematching.  `C7` needs resolved tensor/copy
incidence, the Cartesian-to-PS bridge and the final physical Wilson array.

This is mathematical fixed-order EFT progress, not a complete theory,
continuum UV completion, phenomenological fit, or empirical validation.

## What V50 genuinely solved

{exact}

## Frozen C1-C7 decision

`G2_closed iff C1 through C7 all pass for the same retained action`.

| Clause | Requirement | Status | Landed | Remaining blocker |
|---|---|---|---|---|
{clauses}

## Exact remaining defects

{defects}

## Smallest next closure patch

{patch}

## G1-G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
{gates}

## Route decision

{report['route_decision']}

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    if report["n_failed_integrity_checks"] != 0 or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    if report["fully_passed_clauses"] != ["C1", "C2", "C6"]:
        raise RuntimeError("G2 clause decision drifted")
    if report["scientific_verdict"]["G2_closed"]:
        raise RuntimeError("G2 was overpromoted")
    if sum(bool(row["closed"]) for row in report["gate_ledger"]) != 1:
        raise RuntimeError("gate ledger drifted")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V50 master JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V50 master Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V50_G2_FRONTIER_INTEGRATION_AUDIT_CHECK_PASS")
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
