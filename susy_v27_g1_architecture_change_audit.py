#!/usr/bin/env python3
"""V27 architecture-changing audit of the full SUSY Pati--Salam G1 gate.

The user explicitly authorized new physics.  This certificate therefore tests
the V26 dynamical GS EFT, an anomaly-free selector replacement, and explicit
string-derived Pati--Salam constructions against one unchanged acceptance
matrix.  It also emits the machine-readable input schema that a future UV
candidate must satisfy.

The key logical rule is row-wise conjunction: partial results from different
theories cannot be spliced into a UV completion unless an explicit matching
derives one from the other.  No candidate currently satisfies every row, so
the result remains fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.md"
SCHEMA_PATH = ROOT / "SUSY_V27_G1_UV_COMPLETION_INPUT_SCHEMA.json"

STATUS = (
    "V27_G1_ARCHITECTURE_CHANGE_AUDIT_COMPLETE__NO_SINGLE_UV_CANDIDATE_"
    "PASSES__V26_DYNAMICAL_GS_EFT_RETAINED__FULL_G1_OPEN"
)

SOURCE_PINS = {
    "susy_v26_g1_dynamical_gs_completion_attempt.py":
        "6527ee543dd224a10140943ee94d0a23c967bd88384be1a9ae1a11c35bb4da1d",
    "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.json":
        "3914d0754f8c2d1c70d2952507216a098f7a815c99ee64be1cb51b2dc67306b1",
    "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.md":
        "b421954ae496d8173d1b8424a05437747dd531a19818bf9465e94c83f40406ea",
    "susy_v25_g1_g3_completion_frontier.py":
        "51833f307b05d13ae828cab3dec5922795e80b7d56187c554367692a079db638",
    "SUSY_V25_G1_G3_COMPLETION_FRONTIER.json":
        "08c25dbd3b978dc28746f87c8ff0cb89aae3fab5346dad61c8230da63717f027",
    "susy_v24_non_gs_anomaly_completion_nogo.py":
        "55054c9bb70629c1ed099dd22c7d54ada510610dced5496ef11ee00db2875bc3",
    "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.json":
        "c28214d0e3be810e26beeff040e3379a42a0d306dd2fe56f87e52de4b4d26941",
}

UPSTREAM_CORES = {
    "V25_G1_G3_frontier": "5aa1d0bffd39fa3a520105291d95906882842fd185e85cae72b519b03528e307",
    "V26_dynamical_GS_attempt": "7dd049d43e1ce6cb6e9ca3385ecb2895521443a80f5af1363260d4ea637ba59d",
    "V24_minimal_non_GS_nogo": "ee04ddfb4b879efb8e756f54e174b9e33ec35e39ea9a0a58a6741d1249e78932",
}

REQUIREMENTS = (
    (
        "R1_microscopic_UV_source",
        "one explicit UV construction, not a bottom-up EFT declaration",
    ),
    (
        "R2_selector_levels_and_all_anomalies",
        "derive the selector, axion/level matrix, mixed, gravity, and pure-discrete anomaly cancellation",
    ),
    (
        "R3_all_order_operator_and_coefficient_contract",
        "derive normalized holomorphic, Kahler, gauge-kinetic, soft, and higher-field operators and coefficients",
    ),
    (
        "R4_all_moduli_stabilized_and_branch_quotient",
        "stabilize every modulus/axion with the physical quotient and a positive physical Hessian",
    ),
    (
        "R5_hidden_threshold_and_residual_Z2_audit",
        "derive the hidden spectrum, thresholds, condensate branches/VEVs, and preserve visible matter parity",
    ),
    (
        "R6_executable_matching_to_visible_source",
        "match the UV fields and couplings to an executable nonzero component source",
    ),
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    rows = []
    for relative, expected in SOURCE_PINS.items():
        path = ROOT / relative
        actual = sha256_file(path) if path.exists() else None
        rows.append(
            {
                "path": relative,
                "mode": "raw",
                "expected_sha256": expected,
                "sha256": actual,
                "matches": actual == expected,
            }
        )
    return rows


def requirement_rows(statuses: dict[str, tuple[bool, str]]) -> dict[str, Any]:
    return {
        requirement_id: {
            "passes": statuses[requirement_id][0],
            "evidence": statuses[requirement_id][1],
        }
        for requirement_id, _description in REQUIREMENTS
    }


def candidate(
    candidate_id: str,
    name: str,
    route_class: str,
    source: dict[str, Any],
    statuses: dict[str, tuple[bool, str]],
    qualified_progress: list[str],
) -> dict[str, Any]:
    rows = requirement_rows(statuses)
    return {
        "candidate_id": candidate_id,
        "name": name,
        "route_class": route_class,
        "primary_source": source,
        "requirements": rows,
        "passed_requirement_count": sum(int(row["passes"]) for row in rows.values()),
        "full_G1_pass": all(row["passes"] for row in rows.values()),
        "qualified_progress": qualified_progress,
    }


def candidate_ledger() -> list[dict[str, Any]]:
    return [
        candidate(
            "V26_BOTTOM_UP_GS_RACETRACK",
            "V26 anomaly-matched triple-racetrack EFT",
            "bottom_up_4D_supergravity_EFT",
            {
                "url": "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.md",
                "retrieved_or_frozen": "local raw-pinned artifact",
            },
            {
                "R1_microscopic_UV_source": (
                    False,
                    "T, integer levels, and condensate prefactors are declared EFT inputs",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "mixed and gravitational congruences close, but the pure-discrete/cubic counterterm audit and microscopic level origin do not",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "a constructive tensor grammar exists, but the normalized independent basis and UV Wilson/Kahler/soft matching do not",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "one GS modulus is locally stabilized on one selected branch; the complete modulus set and 30-branch quotient are absent",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "residual Z2 is preserved, but thresholds and the full hidden composite branch dynamics are inputs",
                ),
                "R6_executable_matching_to_visible_source": (
                    True,
                    "the raw-pinned V24 SARAH source initializes and processes all 18 terms",
                ),
            },
            [
                "dynamical GS EFT subgate closed",
                "exact supersymmetric Minkowski modulus point",
                "residual matter parity preserved at the declared EFT branch",
            ],
        ),
        candidate(
            "RIGID_DBRANE_PS_2026",
            "Three-family supersymmetric Pati--Salam flux models from rigid D-branes",
            "explicit_Type_IIB_IIA_string_compactification",
            {
                "url": "https://arxiv.org/pdf/2512.21141",
                "version": "arXiv:2512.21141v2, 12 May 2026",
                "evidence_locations": {
                    "microscopic_consistency_and_spectra": "pages 51--52, lines 5024--5033 in the parsed PDF",
                    "Kahler_moduli_open": "page 52, lines 5019--5021",
                    "Yukawa_soft_and_twisted_rules_open": "page 52, lines 5035--5044",
                },
            },
            {
                "R1_microscopic_UV_source": (
                    True,
                    "explicit rigid-brane flux compactifications satisfy N=1, RR tadpole, and K-theory conditions",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "the compactifications do not derive the V24 Z4R x Z11 selector or the V26 level matrix",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "the authors list Yukawas, soft terms, and twisted-sector Yukawa interpretation as future work",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "Kahler moduli remain unfixed at the constructed tree-level stage; nonperturbative stabilization is proposed generically",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "hidden strong decoupling is discussed, but no mapping to the V24 residual Z2 and complete threshold/branch ledger is supplied",
                ),
                "R6_executable_matching_to_visible_source": (
                    False,
                    "the rigid-brane spectrum and couplings are not matched to PSZ4RZ11SUSYV24",
                ),
            },
            [
                "strongest microscopic candidate found",
                "complete perturbative massless spectra",
                "open-string moduli and complex-structure/axio-dilaton stabilization",
            ],
        ),
        candidate(
            "TYPE_IIA_PS_FLUX_2006",
            "Type IIA Pati--Salam flux vacua",
            "explicit_Type_IIA_flux_models",
            {
                "url": "https://arxiv.org/abs/hep-th/0601064",
                "evidence_locations": {
                    "candidate_moduli_language": "lines 38--50 and 264--278 in the parsed paper",
                    "deferred_physics": "lines 50 and 278",
                },
            },
            {
                "R1_microscopic_UV_source": (
                    True,
                    "explicit intersecting-brane flux constructions and spectra are supplied",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "generalized GS cancellation is present, but the required finite selector/level/anomaly ledger is not the V24 contract",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "complete interactions and higher operators are not derived",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "the paper says all moduli may be stabilized and defers the detailed stabilization analysis",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "generic exotics remain and their mass generation is deferred",
                ),
                "R6_executable_matching_to_visible_source": (
                    False,
                    "different spectra and no component-source matching are supplied",
                ),
            },
            ["explicit three-family string spectra", "flux and D-brane consistency framework"],
        ),
        candidate(
            "HETEROTIC_PS_GGSO_2010",
            "Classification of heterotic Pati--Salam models",
            "exact_worldsheet_GGSO_classification",
            {
                "url": "https://arxiv.org/abs/1007.2268",
                "evidence_locations": {
                    "algebraic_spectrum_classification": "lines 0--4 and 562--571 in the parsed paper",
                },
            },
            {
                "R1_microscopic_UV_source": (
                    True,
                    "free-fermionic heterotic worldsheet constructions with algebraic GGSO spectrum rules",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "no selected vacuum is shown to reproduce the V24 selector and GS ledger",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "the classification supplies spectra, not the required complete operator/Kahler/soft matching",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "no full stabilized modulus vacuum matching V24 is supplied",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "no matching hidden threshold and residual-parity audit is supplied",
                ),
                "R6_executable_matching_to_visible_source": (
                    False,
                    "no GGSO vacuum is matched to the 13-field V24 component source",
                ),
            },
            ["exact algebraic worldsheet spectrum machinery", "existence of three-generation exophobic PS vacua"],
        ),
        candidate(
            "D6_PS_HIDDEN_RACETRACK_2004",
            "Supersymmetric Pati--Salam models from intersecting D6-branes",
            "explicit_D6_branes_with_hidden_confining_sectors",
            {
                "url": "https://arxiv.org/abs/hep-th/0403061",
                "evidence_locations": {
                    "models_and_hidden_sectors": "lines 0--5 and 31--35 in the parsed paper",
                    "extra_exotics": "abstract line 5",
                },
            },
            {
                "R1_microscopic_UV_source": (
                    True,
                    "explicit orientifold D6-brane constructions are supplied",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "the D-brane U(1) GS system is not the V24 finite-selector anomaly ledger",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "no complete all-order visible operator/Kahler/soft contract is supplied",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "the paper claims only some moduli stabilization from hidden condensation",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "additional exotic matter remains and no V24 matter-parity mapping is derived",
                ),
                "R6_executable_matching_to_visible_source": (
                    False,
                    "different brane spectra and no V24 component matching",
                ),
            },
            ["at least two hidden confining sectors", "explicit brane configurations and PS breaking"],
        ),
        candidate(
            "ANOMALY_FREE_SELECTOR_REPLACEMENT",
            "materially new anomaly-free shaping/gauge selector",
            "new_bottom_up_architecture",
            {
                "url": "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.md",
                "retrieved_or_frozen": "local raw-pinned certificate",
            },
            {
                "R1_microscopic_UV_source": (
                    False,
                    "no explicit microscopic replacement source has been supplied",
                ),
                "R2_selector_levels_and_all_anomalies": (
                    False,
                    "the minimal weakly-coupled spectator class is exactly excluded and no complete replacement selector exists",
                ),
                "R3_all_order_operator_and_coefficient_contract": (
                    False,
                    "changing the selector resets the complete operator contract",
                ),
                "R4_all_moduli_stabilized_and_branch_quotient": (
                    False,
                    "no replacement vacuum exists",
                ),
                "R5_hidden_threshold_and_residual_Z2_audit": (
                    False,
                    "the new hidden spectrum and parity history are undefined",
                ),
                "R6_executable_matching_to_visible_source": (
                    False,
                    "no nonzero executable model for the replacement architecture exists",
                ),
            },
            ["the exact V24 minimal-spectator no-go sharply defines which architecture changes are genuinely new"],
        ),
    ]


def uv_input_schema() -> dict[str, Any]:
    hash_pattern = "^[0-9a-f]{64}$"
    evidence_array = {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["path_or_url", "sha256_or_version", "claim"],
            "properties": {
                "path_or_url": {"type": "string", "minLength": 1},
                "sha256_or_version": {"type": "string", "minLength": 1},
                "claim": {"type": "string", "minLength": 1},
            },
        },
    }
    closed_object = lambda required, properties: {
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://local.invalid/susy-v27-g1-uv-completion-input-schema.json",
        "title": "SUSY V27 full-G1 UV completion candidate",
        "description": "Structural submission contract; passing this schema is necessary but not sufficient for physics acceptance.",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "candidate_id",
            "microscopic_source",
            "selector_and_anomalies",
            "operator_contract",
            "moduli_and_vacuum",
            "hidden_and_parity",
            "executable_matching",
            "evidence_manifest",
            "all_acceptance_checks_pass",
        ],
        "properties": {
            "candidate_id": {"type": "string", "minLength": 1},
            "microscopic_source": closed_object(
                ["construction", "spectrum_manifest_sha256", "consistency_checks_pass"],
                {
                    "construction": {"type": "string", "minLength": 1},
                    "spectrum_manifest_sha256": {"type": "string", "pattern": hash_pattern},
                    "consistency_checks_pass": {"const": True},
                },
            ),
            "selector_and_anomalies": closed_object(
                ["generator_action_sha256", "level_matrix_sha256", "all_anomalies_canceled"],
                {
                    "generator_action_sha256": {"type": "string", "pattern": hash_pattern},
                    "level_matrix_sha256": {"type": "string", "pattern": hash_pattern},
                    "all_anomalies_canceled": {"const": True},
                },
            ),
            "operator_contract": closed_object(
                ["normalized_basis_sha256", "wilson_matching_sha256", "kahler_gauge_soft_matching_sha256", "all_orders_closed"],
                {
                    "normalized_basis_sha256": {"type": "string", "pattern": hash_pattern},
                    "wilson_matching_sha256": {"type": "string", "pattern": hash_pattern},
                    "kahler_gauge_soft_matching_sha256": {"type": "string", "pattern": hash_pattern},
                    "all_orders_closed": {"const": True},
                },
            ),
            "moduli_and_vacuum": closed_object(
                ["field_manifest_sha256", "branch_quotient_sha256", "hessian_sha256", "all_moduli_stabilized"],
                {
                    "field_manifest_sha256": {"type": "string", "pattern": hash_pattern},
                    "branch_quotient_sha256": {"type": "string", "pattern": hash_pattern},
                    "hessian_sha256": {"type": "string", "pattern": hash_pattern},
                    "all_moduli_stabilized": {"const": True},
                },
            ),
            "hidden_and_parity": closed_object(
                ["spectrum_threshold_sha256", "vev_branch_sha256", "residual_Z2_preserved"],
                {
                    "spectrum_threshold_sha256": {"type": "string", "pattern": hash_pattern},
                    "vev_branch_sha256": {"type": "string", "pattern": hash_pattern},
                    "residual_Z2_preserved": {"const": True},
                },
            ),
            "executable_matching": closed_object(
                ["model_source_sha256", "uv_to_component_map_sha256", "live_engine_pass"],
                {
                    "model_source_sha256": {"type": "string", "pattern": hash_pattern},
                    "uv_to_component_map_sha256": {"type": "string", "pattern": hash_pattern},
                    "live_engine_pass": {"const": True},
                },
            ),
            "evidence_manifest": evidence_array,
            "all_acceptance_checks_pass": {"const": True},
        },
    }


def build_report() -> dict[str, Any]:
    manifest = source_manifest()
    candidates = candidate_ledger()
    requirement_ids = [row[0] for row in REQUIREMENTS]
    candidate_ids = [row["candidate_id"] for row in candidates]
    v26 = json.loads(
        (ROOT / "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.json").read_text(encoding="utf-8")
    )
    v25 = json.loads(
        (ROOT / "SUSY_V25_G1_G3_COMPLETION_FRONTIER.json").read_text(encoding="utf-8")
    )
    nong = json.loads(
        (ROOT / "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.json").read_text(encoding="utf-8")
    )
    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in manifest),
        "V26_core_matches": v26["core_sha256"] == UPSTREAM_CORES["V26_dynamical_GS_attempt"],
        "V25_core_matches": v25["core_sha256"] == UPSTREAM_CORES["V25_G1_G3_frontier"],
        "V24_non_GS_core_matches": nong["core_sha256"] == UPSTREAM_CORES["V24_minimal_non_GS_nogo"],
        "six_acceptance_requirements_are_unique": len(requirement_ids) == len(set(requirement_ids)) == 6,
        "all_candidates_have_every_requirement": all(
            set(row["requirements"]) == set(requirement_ids) for row in candidates
        ),
        "candidate_ids_are_unique": len(candidate_ids) == len(set(candidate_ids)),
        "no_single_candidate_passes_full_G1": not any(row["full_G1_pass"] for row in candidates),
        "full_pass_is_rowwise_conjunction": all(
            row["full_G1_pass"] == all(cell["passes"] for cell in row["requirements"].values())
            for row in candidates
        ),
        "V26_is_executable_but_not_microscopic": (
            candidates[0]["requirements"]["R6_executable_matching_to_visible_source"]["passes"]
            and not candidates[0]["requirements"]["R1_microscopic_UV_source"]["passes"]
        ),
        "newest_rigid_Dbrane_candidate_is_microscopic_but_not_operator_complete": (
            candidates[1]["requirements"]["R1_microscopic_UV_source"]["passes"]
            and not candidates[1]["requirements"]["R3_all_order_operator_and_coefficient_contract"]["passes"]
        ),
        "minimal_non_GS_route_remains_excluded": nong["verdict"]["minimal_non_GS_completion_viable"] is False,
        "V25_arbitrary_driver_function_remains_open": v25["terminal_conclusion"]["G1_full_closed"] is False,
        "schema_requires_all_six_physics_blocks": all(
            name in uv_input_schema()["required"]
            for name in (
                "microscopic_source",
                "selector_and_anomalies",
                "operator_contract",
                "moduli_and_vacuum",
                "hidden_and_parity",
                "executable_matching",
            )
        ),
        "no_full_G1_claim_is_supported": not any(
            row["full_G1_pass"] for row in candidates
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v27-g1-architecture-change-audit-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v27.g1_architecture_change_audit",
        "audit_date": "2026-08-24",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "acceptance_requirements": [
            {"requirement_id": requirement_id, "description": description}
            for requirement_id, description in REQUIREMENTS
        ],
        "candidate_ledger": candidates,
        "conjunction_rule": {
            "statement": (
                "full G1 requires every acceptance requirement in one UV theory or an explicit "
                "derivation/matching between theories; column-wise union of unrelated candidates is invalid"
            ),
            "Frankenstein_union_allowed": False,
            "reason": (
                "no source derives the V26 levels, racetrack, selector, and operator coefficients from any "
                "of the listed compactifications"
            ),
        },
        "new_physics_decision": {
            "new_physics_was_allowed_and_tested": True,
            "replace_V24_source_now": False,
            "retain_V26_as_qualified_dynamical_GS_EFT_frontier": True,
            "strongest_microscopic_research_route": "RIGID_DBRANE_PS_2026",
            "why_not_promoted": (
                "its exact UV spectrum is not V24, its Kahler moduli are not explicitly stabilized, "
                "and its Yukawa, soft, and twisted-sector coupling rules remain open"
            ),
            "full_G1_closed": False,
            "full_gate_claim": False,
        },
        "G1_gate": {
            "gate": "G1",
            "qualified_id": "research.susy_pati_salam.v27.G1.full_closure",
            "closed": False,
            "full_gate_claim": False,
            "state": "REPRESENTATIVE_ARCHITECTURE_ROUTES_AUDITED__NO_TESTED_UV_COMPLETION_PASSES",
            "remaining_blocker": (
                "one explicit UV theory must simultaneously derive the selector/anomalies, all-order "
                "operators and coefficients, stabilized moduli/branches, hidden parity thresholds, "
                "and the executable visible matching"
            ),
        },
        "closure_counts": {
            "full_G1_closed": 0,
            "full_G1_open": 1,
            "candidate_routes_tested": len(candidates),
            "candidate_routes_passing": sum(int(row["full_G1_pass"]) for row in candidates),
        },
        "generated_submission_schema": SCHEMA_PATH.name,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    candidates = report["candidate_ledger"]
    lines = [
        "# SUSY V27 G1 architecture-change audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full G1 closed: **no**.",
        f"- New-physics routes tested: **{len(candidates)}**; complete routes: **0**.",
        "",
        "## Outcome",
        "",
        "New physics was allowed without preserving the V24 architecture. Six independent full-G1 requirements were applied to every candidate. No single theory supplies all six, and partial results from unrelated theories cannot be combined without an explicit UV-to-EFT derivation.",
        "",
        "V26 remains the strongest executable continuation: it has a dynamical anomaly-matched GS racetrack, an exact local supersymmetric Minkowski modulus point, and preserved residual matter parity. It is still a bottom-up supergravity EFT whose levels, condensate thresholds, complete branch quotient, and all-order coefficients are inputs.",
        "",
        "## Route-by-route result",
        "",
    ]
    for row in candidates:
        failed = ", ".join(
            requirement_id.split("_", 1)[0]
            for requirement_id, cell in row["requirements"].items()
            if not cell["passes"]
        )
        lines.append(
            f"- `{row['candidate_id']}`: {row['passed_requirement_count']}/6 requirements pass; failed: {failed}."
        )
    lines.extend(
        [
        "",
        "## Strongest microscopic alternative",
        "",
        "The 2026 rigid D-brane Pati--Salam models are genuine string constructions with full perturbative spectra and string consistency checks. They still do not close this gate. Their Kähler moduli remain unfixed at the constructed stage, and the paper explicitly leaves Yukawa couplings, soft terms, and twisted-sector Yukawa rules for future work. Their spectrum and selection rules also do not match `PSZ4RZ11SUSYV24`.",
        "",
        "Primary source: [Three-family supersymmetric Pati--Salam flux models from rigid D-branes](https://arxiv.org/pdf/2512.21141). The relevant limitations are stated in its conclusion on pages 51--52.",
        "",
        "Older string routes do not fill the gap: the 2006 Type-IIA construction says detailed moduli stabilization and exotic masses are deferred; the heterotic GGSO work classifies exact spectra but does not supply the stabilized operator-matched vacuum; and the 2004 D6 models contain extra exotics and only partial moduli stabilization.",
        "",
        "## Exact stopping rule",
        "",
        "Full G1 can be promoted only when one candidate passes all of: microscopic source; complete selector/level/anomaly derivation; normalized all-order operator and coefficient matching; stabilization of every modulus and physical branch quotient; hidden-threshold and residual-`Z2` audit; and executable component matching.",
        "",
        f"The generated `{report['generated_submission_schema']}` makes those required inputs machine-readable. It prevents another EFT ansatz or literature scaffold from being mislabeled as a completed UV theory.",
        "",
        "## Decision",
        "",
        "Do not replace V24 with an unmatched string model and do not mark G1 closed. The scientifically valid enhancement is the V26 dynamical GS EFT plus this V27 UV acceptance audit. Actual closure now requires new external microscopic data, not another unconstrained local operator or invented coefficient.",
        "",
        "Other primary sources: [Type IIA Pati--Salam flux vacua](https://arxiv.org/abs/hep-th/0601064), [heterotic Pati--Salam classification](https://arxiv.org/abs/1007.2268), and [intersecting D6-brane Pati--Salam models](https://arxiv.org/abs/hep-th/0403061).",
        "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    SCHEMA_PATH.write_text(
        json.dumps(uv_input_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def check_outputs(report: dict[str, Any]) -> bool:
    return all(
        [
            JSON_PATH.exists(),
            MD_PATH.exists(),
            SCHEMA_PATH.exists(),
            JSON_PATH.read_text(encoding="utf-8")
            == json.dumps(report, indent=2, sort_keys=True) + "\n",
            MD_PATH.read_text(encoding="utf-8") == render_markdown(report),
            SCHEMA_PATH.read_text(encoding="utf-8")
            == json.dumps(uv_input_schema(), indent=2, sort_keys=True) + "\n",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check and (report["n_failed"] or not check_outputs(report)):
        print(
            json.dumps(
                {
                    "failures": report["failures"],
                    "frozen_outputs_match": check_outputs(report),
                }
            )
        )
        return 1
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
