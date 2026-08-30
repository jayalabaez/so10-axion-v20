#!/usr/bin/env python3
"""Source-pinned G1--G8 ledger for the active SUSY SO(10)xU(1)_X V22 model.

V22 supersedes the failed V21 hierarchy branch, but it has a different field
space and scalar potential.  V21 gate closures therefore cannot be inherited.
This ledger composes only V22 evidence and distinguishes complete gates from
exactly closed subproblems.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G1_G8_GATE_LEDGER.json"
OUT_MD = ROOT / "SUSY_V22_G1_G8_GATE_LEDGER.md"
SCHEMA = "susy_v22_g1_g8_gate_ledger_v1"
NAMESPACE = "canonical.susy_so10x17.v22"

SOURCE_PINS = {
    "models/SO10X17SUSYV22/SO10X17SUSYV22.m":
        "a253e40e712287d654122b74ac94ceeb05b5fc3dddcf8c2af2c790af99be45d4",
    "tools/validate-susy-so10x17-v22.wls":
        "50b32ff40acbcd90b5b087fd72013578ed5d131235455189a423268fc31d2fce",
    "run_susy_v22_sarah_validation.py":
        "e83c7e716375f1698aa6e1c4bb57662e27d6d666673d48399a13020e7b4d3a36",
    "SUSY_SO10X17_V22_CONTRACT.json":
        "4bd5f2f829fbaf7d88b1a535a0eba295222cd07418ad8dd4d3c84e0365c41cc1",
    "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json":
        "3f7ba0c354ea3daeae51fe337b56b18ad237908a6e9f0dc59759ab3a3d4d77fd",
    "SUSY_V22_G1_SHAPING_SYMMETRY_NOGO.json":
        "36ebcfbe1e059377da32fa3e29c7be4d17690c75fa31b0276a10b3d5df9ca223",
    "SUSY_V22_G1_MINIMAL_REPAIR_SEARCH.json":
        "c1bbdd79f99a533c7351b90193827a34f655db18d34b1b2a2a887475f88db50b",
    "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json":
        "ac9d2ad4eaa091e7b7381e91956c8a97d57d1bcb2adf5af030a6da1632cfdaf9",
    "SUSY_V22_MISSING_PARTNER_RANK.json":
        "52519f26c02807595341d1ba5a7c065c61f51a8b96e6e28061c3cc8b8c06ca94",
    "SUSY_V22_EXACT_EW_ENDPOINT.json":
        "98f9a54bded44d39f1a4abe0d33d02e8dc0de203ad51f27ae7ceefae5c75df0f",
    "SUSY_V22_PERTURBATIVE_WINDOW.json":
        "b4a634ed2b89d0967038131d8caee69e04d7502f02fc4482f765bb037c5ddf13",
    "SUSY_V22_ALL_ORDER_R_PROTECTION.json":
        "18fe2443b741597aa241df8ff6f3d8461ad2db697c0a101759941f8204d7849e",
    "SUSY_V22_Z4R_ANOMALY.json":
        "3a9852341b7299777024bc8fa8b0b10df2dde19345b641d630e8cf2ec5bd6f24",
    "SUSY_V22_F_FLAT_GUT_SLICE.json":
        "8f001bfa9ecd235b1a2c078489206126951a486880cccd381f8e99ee713a15eb",
    "SUSY_V22_G4_PROTECTION_FRONTIER.json":
        "97bab837e20da1d5b8766a6b2e9e7bb57f7051b49c5f20772e6d75d80c4adb44",
    "SUSY_V22_G5_PHASE_COUNT.json":
        "bc2d8cba4f07c8a929a089d3ff2c633914c3bb6ef1dca262c55b3cab0513f7c7",
}

JSON_SOURCES = tuple(name for name in SOURCE_PINS if name.endswith(".json"))
OPTIONAL_SARAH_ATTESTATION = "SUSY_V22_SARAH_VALIDATION.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def core_sha(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha(json_bytes(body))


def load_pinned(root: Path) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    payloads: dict[str, Any] = {}
    manifest: list[dict[str, str]] = []
    failures: list[str] = []
    for relative, expected in SOURCE_PINS.items():
        path = root / relative
        if not path.is_file() or path.is_symlink():
            failures.append(f"missing_or_unsafe:{relative}")
            continue
        raw = path.read_bytes()
        actual = sha(raw)
        manifest.append(
            {
                "path": relative,
                "mode": "raw",
                "sha256": actual,
                "expected_sha256": expected,
            }
        )
        if actual != expected:
            failures.append(f"sha256_mismatch:{relative}")
            continue
        if relative in JSON_SOURCES:
            try:
                payloads[relative] = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                failures.append(f"invalid_json:{relative}")
    return payloads, manifest, failures


def optional_sarah_state(root: Path) -> dict[str, Any]:
    path = root / OPTIONAL_SARAH_ATTESTATION
    if not path.is_file() or path.is_symlink():
        return {
            "state": "NOT_FROZEN",
            "valid": False,
            "path": OPTIONAL_SARAH_ATTESTATION,
            "reason": "no completed V22 Wolfram/SARAH attestation artifact exists",
        }
    raw = path.read_bytes()
    try:
        report = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "state": "INVALID",
            "valid": False,
            "path": OPTIONAL_SARAH_ATTESTATION,
            "sha256": sha(raw),
            "reason": "attestation is not valid JSON",
        }
    expected_checks = {
        "model_parse_succeeded",
        "model_initialization_succeeded",
        "supersymmetric_potential_constructed",
        "sarah_anomaly_check_succeeded",
        "sarah_model_check_completed_without_abort",
    }
    checks = report.get("checks", {})
    valid = (
        report.get("schema") == "susy_so10x17_v22_sarah_validation_v1"
        and set(checks) == expected_checks
        and all(value is True for value in checks.values())
        and report.get("n_failed") == 0
        and report.get("execution", {}).get("process_exit_code") == 0
        and report.get("tool", {}).get("SARAH_version") == "4.15.3"
    )
    return {
        "state": "ACCEPTED" if valid else "INVALID",
        "valid": valid,
        "path": OPTIONAL_SARAH_ATTESTATION,
        "sha256": sha(raw),
        "reason": "accepted scoped executable attestation" if valid else "attestation fields fail closed",
    }


def check(condition: bool, label: str, checks: dict[str, bool], failures: list[str]) -> None:
    passed = condition is True
    checks[label] = passed
    if not passed:
        failures.append(label)


def build_report(root: Path = ROOT) -> dict[str, Any]:
    payloads, manifest, failures = load_pinned(root)
    checks: dict[str, bool] = {}
    check(
        set(payloads) == set(JSON_SOURCES),
        "all_pinned_V22_sources_match",
        checks,
        failures,
    )
    if set(payloads) != set(JSON_SOURCES):
        report = {
            "schema": SCHEMA,
            "namespace": NAMESPACE,
            "status": "V22_GATE_LEDGER_SOURCE_FAILURE",
            "overall_state": "UNRESOLVED",
            "gates": [],
            "source_manifest": manifest,
            "checks": checks,
            "n_checks": len(checks),
            "failures": failures,
            "n_failed": len(failures),
        }
        report["core_sha256"] = core_sha(report)
        return report

    contract = payloads["SUSY_SO10X17_V22_CONTRACT.json"]
    holomorphic_ring = payloads["SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"]
    shaping_nogo = payloads["SUSY_V22_G1_SHAPING_SYMMETRY_NOGO.json"]
    minimal_repair = payloads["SUSY_V22_G1_MINIMAL_REPAIR_SEARCH.json"]
    no_new_field = payloads["SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"]
    missing_partner = payloads["SUSY_V22_MISSING_PARTNER_RANK.json"]
    ew = payloads["SUSY_V22_EXACT_EW_ENDPOINT.json"]
    window = payloads["SUSY_V22_PERTURBATIVE_WINDOW.json"]
    r_protection = payloads["SUSY_V22_ALL_ORDER_R_PROTECTION.json"]
    r_anomaly = payloads["SUSY_V22_Z4R_ANOMALY.json"]
    flat = payloads["SUSY_V22_F_FLAT_GUT_SLICE.json"]
    g4 = payloads["SUSY_V22_G4_PROTECTION_FRONTIER.json"]
    g5 = payloads["SUSY_V22_G5_PHASE_COUNT.json"]
    sarah = optional_sarah_state(root)

    for label, artifact in (
        ("contract", contract),
        ("G1_holomorphic_ring", holomorphic_ring),
        ("G1_shaping_nogo", shaping_nogo),
        ("G1_minimal_repair_search", minimal_repair),
        ("G1_no_new_field_completion", no_new_field),
        ("missing_partner", missing_partner),
        ("EW_endpoint", ew),
        ("perturbative_window", window),
        ("R_protection", r_protection),
        ("R_anomaly", r_anomaly),
        ("F_D_flat_slice", flat),
        ("G4_frontier", g4),
        ("G5_phase", g5),
    ):
        check(
            artifact.get("n_failed") == 0 and artifact.get("failures") == [],
            f"{label}_artifact_passes",
            checks,
            failures,
        )

    check(
        contract["continuity_with_V21"]["V21_G3_can_be_inherited_as_the_V22_vacuum"] is False,
        "V21_gate_evidence_is_not_inherited",
        checks,
        failures,
    )
    check(
        contract["continuous_anomalies"]
        == {"SO10_squared_U1X": 0, "gravity_squared_U1X": 0, "U1X_cubed": 0},
        "V22_continuous_anomalies_cancel",
        checks,
        failures,
    )
    check(
        holomorphic_ring["counts"]["allowed_base_field_sectors"] == 1045
        and holomorphic_ring["counts"]["declared_allowed_sectors"] == 29
        and holomorphic_ring["counts"]["allowed_undeclared_sectors"] == 1016
        and holomorphic_ring["catalogue_verdict"]["complete_under_declared_symmetries"] is False,
        "degree_le_4_holomorphic_census_proves_catalogue_incomplete",
        checks,
        failures,
    )
    check(
        shaping_nogo["counts"]["off_diagonal_allowed_undeclared_sectors"] == 20
        and shaping_nogo["resolution"]["ordinary_Abelian_shaping_charge_patch_exists"] is False,
        "neutral_coefficient_Abelian_shaping_patch_is_exactly_excluded",
        checks,
        failures,
    )
    check(
        minimal_repair["counts"]["minimum_selected_sectors"] == 81
        and minimal_repair["counts"]["unavoidable_extra_sectors"] == 52
        and minimal_repair["repair_verdict"]["classical_degree_le_4_holomorphic_sector_repair_exists"] is True,
        "minimal_degree4_shaping_completion_is_constructively_exhibited",
        checks,
        failures,
    )
    check(
        minimal_repair["vacuum_effect"]["four_scale_field_dimensions"]["complex_quotient_moduli"] == 5
        and minimal_repair["repair_verdict"]["full_V22_repair_achieved"] is False,
        "minimal_completion_has_four_extra_moduli_and_does_not_repair_V22",
        checks,
        failures,
    )
    check(
        no_new_field["counts"]["minimum_selected_sectors"] == 108
        and no_new_field["counts"]["unavoidable_extra_sectors"] == 79
        and no_new_field["counts"]["unavoidable_extra_flavour_components"] == 194,
        "no_new_field_Abelian_R_completion_has_exact_108_sector_minimum",
        checks,
        failures,
    )
    check(
        no_new_field["completion_verdict"]["classical_degree_le_4_sector_completion_exists_without_new_fields"] is True
        and no_new_field["checks"]["all_Z28R_mixed_anomalies_vanish_under_eta_14_convention"] is True
        and no_new_field["shaping_symmetry"]["Z28R_unbroken_VEV_remnant"] == "Z4R",
        "anomaly_free_Z28R_Z2S_selector_exists_and_preserves_Z4R_remnant",
        checks,
        failures,
    )
    check(
        no_new_field["completion_verdict"]["source_land_as_active_V22"] is False
        and no_new_field["physics_effect"]["original_diagonal_F_flat_solution_inherited"] is False,
        "108_sector_candidate_requires_explicit_acceptance_and_full_revalidation",
        checks,
        failures,
    )
    mp = missing_partner["corrected_rank_certificate"]
    check(
        mp["doublet_rank"] == 10
        and mp["doublet_nullity"] == 1
        and mp["triplet_rank"] == 13
        and mp["triplet_nullity"] == 0,
        "missing_partner_rank_architecture_is_10_over_1_and_13_over_0",
        checks,
        failures,
    )
    check(
        missing_partner["claim_boundary"]["source_exact_component_missing_partner_closed"] is False,
        "missing_partner_component_Clebsches_remain_open",
        checks,
        failures,
    )
    check(
        missing_partner["claim_boundary"]["corrected_missing_partner_fields_source_landed"] is True
        and missing_partner["required_model_correction"]["source_declared_continuous_U1_MP"] is False,
        "corrected_missing_partner_fields_are_landed_without_fictitious_U1_MP",
        checks,
        failures,
    )
    check(
        ew["exact_inputs"]["vu_GeV"] == "696/5"
        and ew["exact_inputs"]["vd_GeV"] == "522/5"
        and ew["exact_inputs"]["tan_beta"] == "4/3",
        "EW_endpoint_is_exactly_174_GeV",
        checks,
        failures,
    )
    check(
        flat["exact_dimensions"]["complex_quotient_moduli"] == 1
        and flat["claim_boundary"]["V22_global_vacuum_closed"] is False,
        "local_F_D_flat_slice_has_one_axion_modulus_but_not_globality",
        checks,
        failures,
    )
    check(
        all(g4["positive_frontier"].values())
        and all(value is False for value in g4["open_canonical_requirements"].values()),
        "G4_scoped_frontier_is_closed_but_full_gate_is_open",
        checks,
        failures,
    )
    check(
        g5["exact_counts"]["physical_GUT_phase_dimension"] == 1
        and all(value is False for value in g5["remaining_requirements"].values()),
        "G5_one_phase_subproblem_is_closed_but_full_gate_is_open",
        checks,
        failures,
    )
    check(
        r_protection["claim_boundary"]["canonical_G4_closed"] is False
        and r_anomaly["claim_boundary"]["canonical_G4_closed"] is False,
        "R_selection_and_anomaly_results_do_not_overclose_G4",
        checks,
        failures,
    )
    check(
        window["checks"]["coupling_is_finite_through_1p5_MGUT"] is True
        and window["checks"]["one_loop_Landau_pole_occurs_before_2_MGUT"] is True,
        "V22_has_only_a_short_effective_GUT_window",
        checks,
        failures,
    )

    gates = [
        {
            "gate": "G1",
            "qualified_id": f"{NAMESPACE}.G1.complete_susy_operator_contract",
            "closed": False,
            "state": "CONSTRUCTIVE_108_SECTOR_COMPLETION_FOUND__MODEL_ACCEPTANCE_OPEN",
            "closed_subproblems": [
                "33-superfield source catalogue",
                "continuous anomaly cancellation",
                "U(1)_X to residual Z17 charge relation",
                "declared superpotential charge/R selection ledger",
                "exact degree<=4 holomorphic charge/flavour/SO(10)-character census",
                "neutral-coefficient Abelian shaping-symmetry no-go for the five-driver sector",
                "four-scale-field non-R alternative rejected as lower quality by four extra complex moduli",
                "no-new-field Smith minimum: 108 sectors selected by anomaly-compatible Z28R x Z2S",
                "required VEVs leave the original hierarchy-protecting Z4R subgroup of Z28R",
            ],
            "open_requirements": [
                "explicit model decision to accept 79 extra sectors and 194 extra flavour/contraction components",
                "source-land and normalize the complete 108-sector superpotential tensor basis",
                "recompute the full F+D+soft vacuum for the generic 5x5 driver matrix",
                "all-order closure of broken-Z2S spurion insertions plus the Kahler and soft rings",
                "independent SO(10) tensor-copy multiplicities and normalizations",
                "completed hash-bound V22 Wolfram/SARAH attestation",
            ],
        },
        {
            "gate": "G2",
            "qualified_id": f"{NAMESPACE}.G2.full_component_projection",
            "closed": False,
            "state": "ABSTRACT_RANK_CLOSED__G1_DEPENDENCY_BLOCKED",
            "closed_subproblems": [
                "abstract missing-partner rank witness: doublet 10/1 and triplet 13/0"
            ],
            "open_requirements": [
                "an accepted complete G1 operator basis after source-level selection-rule repair",
                "source-exact SO(10) component Clebsches spanning the rank witness",
                "normalized component projections for every accepted G1 operator",
            ],
        },
        {
            "gate": "G3",
            "qualified_id": f"{NAMESPACE}.G3.global_F_D_soft_vacuum",
            "closed": False,
            "state": "PARTIAL_OPEN",
            "closed_subproblems": [
                "exact local F/D-flat GUT singlet slice",
                "one complex axion multiplet on the local quotient",
            ],
            "open_requirements": [
                "complete global F+D+soft stationary-orbit classification",
                "full scalar Hessian positive modulo gauge and the axion",
                "proof that all R-charge-two missing-partner 126 fields have zero VEV",
            ],
        },
        {
            "gate": "G4",
            "qualified_id": f"{NAMESPACE}.G4.protected_174GeV_hierarchy",
            "closed": False,
            "state": "SCOPED_PROTECTION_CLOSED__DEPENDENCY_BLOCKED",
            "closed_subproblems": [
                "one light doublet pair and no triplet zero mode in the rank architecture",
                "exact 174 GeV tree endpoint with positive physical Higgs curvatures",
                "N=1 quadratic supertrace cancellation",
                "source-landed all-order holomorphic R selection rule",
                "mixed Z4R anomaly cancellation",
            ],
            "open_requirements": list(g4["open_canonical_requirements"]),
        },
        {
            "gate": "G5",
            "qualified_id": f"{NAMESPACE}.G5.calg_and_axion_revalidation",
            "closed": False,
            "state": "ONE_PHASE_QUOTIENT_CLOSED__DEPENDENCY_BLOCKED",
            "closed_subproblems": [
                "exactly one physical GUT phase after the broken gauge quotient",
                "EW CP-odd endpoint has only the required eaten zero and one positive physical mode",
            ],
            "open_requirements": list(g5["remaining_requirements"]),
        },
        {
            "gate": "G6",
            "qualified_id": f"{NAMESPACE}.G6.full_susy_RGE_matching_chain",
            "closed": False,
            "state": "PARTIAL_OPEN__DEPENDENCY_BLOCKED",
            "closed_subproblems": [
                "exact one-loop SO(10) coefficient b=272",
                "finite effective window through 1.5 M_GUT at the benchmark",
            ],
            "open_requirements": [
                "complete tensor gauge/Yukawa/superpotential/soft beta system",
                "stage-resolved threshold matching and independent replay",
                "UV completion below the one-loop Landau pole before 2 M_GUT",
            ],
        },
        {
            "gate": "G7",
            "qualified_id": f"{NAMESPACE}.G7.physical_pole_threshold_spectrum",
            "closed": False,
            "state": "DEPENDENCY_BLOCKED",
            "closed_subproblems": [],
            "open_requirements": [
                "source-exact scalar, vector, fermion and gaugino/higgsino mass matrices",
                "declared soft/tadpole/VEV scheme and self-energy pole solutions",
                "complete finite threshold inventory with ancestry and multiplicities",
            ],
        },
        {
            "gate": "G8",
            "qualified_id": f"{NAMESPACE}.G8.proton_lifetime_distribution",
            "closed": False,
            "state": "DEPENDENCY_BLOCKED",
            "closed_subproblems": [],
            "open_requirements": [
                "physical gauge and color-triplet pole mediators from G7",
                "mass-basis Wilson matching and running from G6",
                "V22 flavor fit/covariance and interference phases",
                "versioned experimental and lattice input ledger",
            ],
        },
    ]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": NAMESPACE,
        "status": "V22_G1_G8_LEDGER_RESOLVED__108_SECTOR_G1_COMPLETION_CANDIDATE_FOUND__ALL_FULL_GATES_OPEN",
        "overall_state": "OPEN_WITH_CONSTRUCTIVE_G1_REPLACEMENT",
        "active_model": "SUSY SO(10) x U(1)_X V22",
        "superseded_model_role": {
            "V21": "hierarchy no-go and regression evidence only",
            "can_close_V22_gate": False,
        },
        "closure_counts": {"closed": 0, "open": 8},
        "gates": gates,
        "sarah_attestation": sarah,
        "critical_path": [
            "accept or reject the no-new-field 108-sector V22R completion",
            "G1 complete operator/tensor contract plus executable attestation",
            "G2 full component Clebsches",
            "G3 global F+D+soft vacuum",
            "G4 protected hierarchy promotion",
            "G5 cal-G/axion full-spectrum promotion",
            "G6 and G7 coupled RGE/pole-threshold closure",
            "G8 proton-lifetime distribution",
        ],
        "next_executable_tasks": [
            "if the 79 unavoidable additions are accepted, define the no-new-field V22R source with the exact Z28R x Z2S selector and all 108 sectors",
            "normalize 265 SO(10)-and-flavour singlet components and rebuild the ten directly modified missing-partner sectors",
            "recompute the generic 5x5-driver F+D+soft vacuum and close broken-Z2S higher-order leakage",
            "only after G1 repair, replace the abstract 11x11/13x13 rank witness by source-exact SO(10) component Clebsch matrices",
            "solve and classify the complete V22 F+D+soft vacuum and Hessian",
            "run the multi-hour full SARAH CheckModel attestation in a dedicated CI budget",
        ],
        "claim_boundary": {
            "V22_is_the_active_physics": True,
            "V21_G1_G3_inherited": False,
            "all_V22_full_gates_closed": False,
            "degree_le_4_holomorphic_census_closed": True,
            "current_declared_superpotential_catalogue_complete": False,
            "neutral_coefficient_Abelian_shaping_no_go_closed": True,
            "sparse_29_sector_Abelian_repair_excluded": True,
            "anomaly_free_degree4_81_sector_candidate_exists": True,
            "candidate_has_five_instead_of_one_complex_moduli": True,
            "no_new_field_108_sector_completion_candidate_exists": True,
            "candidate_adds_79_sectors_and_194_components": True,
            "candidate_VEV_remnant_is_Z4R": True,
            "candidate_explicitly_accepted_as_active_model": False,
            "full_V22_repair_found": False,
            "G2_blocked_by_G1_operator_basis": True,
            "scoped_G4_protection_architecture_closed": True,
            "scoped_G5_one_phase_quotient_closed": True,
            "unique_V22_proton_lifetime_reported": False,
        },
        "source_manifest": manifest,
        "producer": {
            "path": Path(__file__).name,
            "raw_sha256": sha(Path(__file__).read_bytes()),
        },
        "checks": checks,
        "n_checks": len(checks),
        "failures": failures,
        "n_failed": len(failures),
    }
    report["core_sha256"] = core_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "# SUSY V22 G1--G8 gate ledger\n\n"
            f"**Status:** `{report['status']}`\n\n"
            "The source-pinned V22 ledger failed closed. See the JSON artifact.\n"
        )
    lines = [
        "# SUSY SO(10) x U(1)_X V22 G1--G8 gate ledger",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "V22 is the active physics model. V21 is retained only as the hierarchy no-go and a regression reference; "
        "its G1--G3 evidence cannot be inherited because V22 has a different supersymmetric field space and potential.",
        "",
        "No full V22 gate is yet closed. The exact degree-four holomorphic census landed a decisive G1 obstruction: "
        "1,045 sectors are allowed, 29 are declared, and 1,016 are omitted. The five linear drivers yield an exact "
        "no-go for preserving the sparse catalogue with another charge patch. The strongest constructive route adds "
        "no fields: an anomaly-compatible Z28R x Z2S selector picks the exact Smith minimum of 108 sectors and leaves "
        "the useful Z4R VEV remnant. That route necessarily adds 79 sectors and 194 flavour/contraction components.",
        "",
        "This does not erase the other exact V22 progress: the field/charge/anomaly contract, missing-partner rank "
        "architecture, R protection, Z4R anomaly cancellation, local F/D-flat slice, exact 174 GeV endpoint, and "
        "one-phase quotient remain closed scoped subproblems.",
        "",
        "## Gate outcomes",
        "",
    ]
    for gate in report["gates"]:
        lines.extend(
            [
                f"### {gate['gate']} -- {gate['state']}",
                "",
                f"Qualified ID: `{gate['qualified_id']}`",
                "",
            ]
        )
        if gate["closed_subproblems"]:
            lines.append("Closed subproblems:")
            lines.append("")
            lines.extend(f"- {item}" for item in gate["closed_subproblems"])
            lines.append("")
        lines.append("Open requirements:")
        lines.append("")
        lines.extend(f"- {item}" for item in gate["open_requirements"])
        lines.append("")
    lines.extend(
        [
            "## Critical path",
            "",
            " -> ".join(report["critical_path"]),
            "",
            "The sparse 29-sector V22 catalogue cannot be preserved, but a no-new-field 108-sector completion now "
            "exists. Activating it is a material model choice because its generic 5x5 driver matrix invalidates the "
            "frozen vacuum and ten missing-partner sectors change directly. G2 and G3 must be rebuilt if it is accepted.",
            "",
            f"SARAH attestation: `{report['sarah_attestation']['state']}` -- {report['sarah_attestation']['reason']}.",
            "",
            f"Checks: `{report['n_checks']}`; failures: `{report['n_failed']}`.",
            "",
            f"Core SHA-256: `{report['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], root: Path = ROOT) -> None:
    (root / OUT_JSON.name).write_bytes(json_bytes(report))
    (root / OUT_MD.name).write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.check:
        write_outputs(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_state": report["overall_state"],
                "closure_counts": report.get("closure_counts"),
                "n_failed": report["n_failed"],
                "core_sha256": report["core_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
