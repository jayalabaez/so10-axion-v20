#!/usr/bin/env python3
"""Terminal, fail-closed G1--G8 verdict for the V23 redesign campaign.

This ledger does not invent a completion.  It pins and independently checks
the frozen V22R terminal verdict and the three V23 route audits, then records
the exact route decision: the unchanged Chacko and Barr--Raby architectures
are rejected at their stated scopes, while the flipped missing-partner route
is retained only as the primary research frontier.  No full G1--G8 gate is
closed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V23_G1_G8_EXECUTION_VERDICT.json"
OUT_MD = ROOT / "SUSY_V23_G1_G8_EXECUTION_VERDICT.md"
SCHEMA = "susy_v23_g1_g8_execution_verdict_v1"


# Raw pins make the terminal decision depend on the exact reviewed artifacts,
# not merely on selected fields copied from them.  The upstream JSON core pins
# below add an independent canonical-integrity check.
SOURCE_PINS = {
    "susy_v22r_g1_g8_execution_verdict.py":
        "43f6160d8c3ca2bf5b50961c23b993f559ba99da88260d74aa3d2817cd3243a9",
    "SUSY_V22R_G1_G8_EXECUTION_VERDICT.json":
        "a16b740043096a40beae194f3cd585b5ff3de7ceade46ee94e6acb46f963bc86",
    "SUSY_V22R_G1_G8_EXECUTION_VERDICT.md":
        "3ae30ad402329b339aaf8739d3f578a66b95cf1ec420ba1f76cd51c04a7b317a",
    "models/SO10X17SUSYV22R/SO10X17SUSYV22R.m":
        "c792d94c01008a03e5ef8811652764094efdfa3276b4986aa5dc295e7015a77e",
    "susy_v23_chacko_route_rejection.py":
        "707cc06b0789b83f3b050acc8ed83b42dfd33398d487a300bcff5dbf4f35d65a",
    "SUSY_V23_CHACKO_ROUTE_REJECTION.json":
        "102edf31aa6cfb36385a8ac49a58ffc1beefd4cb863a3bc0ca89a05abaaa331e",
    "SUSY_V23_CHACKO_ROUTE_REJECTION.md":
        "c126a5bfdeae5929777b8a8468f1e15b433bd7218d9d0d32eb35f708977737bc",
    "susy_v23_barr_raby_completion_frontier.py":
        "f083b7e4d3571786633a9ae15f85e71ecee435fcab73d7df20173dc40d30c43c",
    "SUSY_V23_BARR_RABY_COMPLETION_FRONTIER.json":
        "74c72bd0105a2fffc9bdfb08b5be134a6dfa74216afd2f257461b9aba52966e6",
    "SUSY_V23_BARR_RABY_COMPLETION_FRONTIER.md":
        "4b176273f490af27d6b7452c9be5a68496176506e2d038cd70aa7d7c4725ce90",
    "models/SO10U1V23BarrRaby/SO10U1V23BarrRaby.m":
        "418ab8e5174e4c715bc677d2961e1b4913413d128b31f37d574701b5911ff1a3",
    "susy_v23_flipped_missing_partner_frontier.py":
        "ad8a41bd09ae100e32a1e5a91a7e71fc3c5c7cd8d2e718a83be86cf66631db00",
    "SUSY_V23_FLIPPED_MISSING_PARTNER_FRONTIER.json":
        "6d067a3c78dc1053b94356ce23dadeb60685144e27387af8b27dd45320afc902",
    "SUSY_V23_FLIPPED_MISSING_PARTNER_FRONTIER.md":
        "cf70a85c4e4eae12592d51b92b6c81730e8544108614ccee198a9d0fc1cc0118",
    "models/SO10U1V23FlippedMissingPartner/SO10U1V23FlippedMissingPartner.m":
        "17898fd619c4f60edb1bcc6b37eae26ccd95cbdcc06f57cbb63482ef456c16ef",
}


UPSTREAMS = {
    "v22r_degree4_eft": {
        "path": "SUSY_V22R_G1_G8_EXECUTION_VERDICT.json",
        "schema": "susy_v22r_g1_g8_execution_verdict_v1",
        "namespace": "active.susy_so10x17.v22r.G1_G8.execution_verdict",
        "status": "V22R_G1_G8_EXECUTION_COMPLETE__DEGREE4_EFT_LANDED__NO_FULL_GATE_CLOSED",
        "core_sha256": "c1bc4ec70dd1cfe91b3716e485dec58dc3a80adedadcfbc47acf52363b09a994",
    },
    "chacko_unchanged_route": {
        "path": "SUSY_V23_CHACKO_ROUTE_REJECTION.json",
        "schema": "susy_v23_chacko_route_rejection_v1",
        "namespace": "rejected.susy_so10.v23.chacko_route",
        "status": "V23_CHACKO_ROUTE_EXACTLY_REJECTED__SELECTOR_AND_TWO_LOOP_UV_OBSTRUCTIONS",
        "core_sha256": "d0a0f9cbe0ea764327de88be009aa7892e1c41f248feba7dc942581104537a34",
    },
    "barr_raby_route": {
        "path": "SUSY_V23_BARR_RABY_COMPLETION_FRONTIER.json",
        "schema": "susy_v23_barr_raby_completion_frontier_v1",
        "namespace": "candidate.susy_so10_u1.v23.barr_raby_completion_frontier",
        "status": "V23_BARR_RABY_ARCHITECTURE_REJECTED__FORCED_H1_MASS__RG_SAFE_NEGATIVE_CONTROL",
        "core_sha256": "ae63a2e7f15acef92b3bc170e02e281d3ac449803d5ee4945fc0dbe9b67511fc",
    },
    "flipped_missing_partner_route": {
        "path": "SUSY_V23_FLIPPED_MISSING_PARTNER_FRONTIER.json",
        "schema": "susy_v23_flipped_missing_partner_frontier_v1",
        "namespace": "candidate.susy_so10_u1.v23.flipped_missing_partner_frontier",
        "status": "V23_FLIPPED_MISSING_PARTNER_FRONTIER_LANDED__FULL_G1_G8_OPEN",
        "core_sha256": "01f8d13d950045f3eaa6de2d950f973dbbb48ebe5711a880b09b602e42c6fd43",
    },
}


MODEL_PATHS = {
    "v22r_degree4_eft": "models/SO10X17SUSYV22R/SO10X17SUSYV22R.m",
    "barr_raby_route": "models/SO10U1V23BarrRaby/SO10U1V23BarrRaby.m",
    "flipped_missing_partner_route": (
        "models/SO10U1V23FlippedMissingPartner/"
        "SO10U1V23FlippedMissingPartner.m"
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded)


def source_manifest(root: Path) -> list[dict[str, Any]]:
    rows = []
    for relative, expected in SOURCE_PINS.items():
        path = root / relative
        observed = sha256(path.read_bytes()) if path.is_file() else None
        rows.append({
            "path": relative,
            "mode": "raw",
            "expected_sha256": expected,
            "sha256": observed,
            "matches": observed == expected,
        })
    return rows


def load_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def json_core_valid(payload: Mapping[str, Any]) -> bool:
    return (
        isinstance(payload.get("core_sha256"), str)
        and canonical_sha(payload) == payload["core_sha256"]
    )


def gate_ledger() -> list[dict[str, Any]]:
    rows = {
        "G1": {
            "state": "SOURCE_SCAFFOLDS_LANDED__FULL_OPERATOR_CONTRACT_OPEN",
            "evidence_landed": [
                "V22R finite degree-four sector catalogue",
                "exact Chacko and Barr--Raby selector obstructions",
                "published flipped Table-I charge and field ledger",
            ],
            "open_requirements": [
                "normalized SO(10) invariant tensors and component Clebsches",
                "complete all-order holomorphic, Kahler, soft, and anomaly-safe selector contract",
                "an executable nonzero-superpotential SARAH model",
            ],
        },
        "G2": {
            "state": "GENERIC_STRUCTURAL_RANKS_LANDED__PHYSICAL_COMPONENT_RANKS_OPEN",
            "evidence_landed": [
                "flipped published zero patterns have generic triplet rank 7 and doublet rank 3",
                "Barr--Raby conditional DW rank is retained only as a negative control",
            ],
            "open_requirements": [
                "normalized full component mass matrices on a solved vacuum",
                "physical threshold eigenvalues with correlated coefficients",
            ],
        },
        "G3": {
            "state": "PUBLISHED_VEV_SCALINGS_LANDED__GLOBAL_VACUUM_OPEN",
            "evidence_landed": [
                "flipped published VEV pattern and Froggatt--Nielsen scalings",
                "V22R restricted regular invariant-coordinate branch",
            ],
            "open_requirements": [
                "source-exact global F+D+soft vacuum",
                "competing-branch exclusion and positive full Hessian",
                "Green--Schwarz and hidden-sector completion for anomalous U(1)A",
            ],
        },
        "G4": {
            "state": "MISSING_PARTNER_PATTERN_LANDED__HIERARCHY_PROTECTION_OPEN",
            "evidence_landed": [
                "flipped one-light-doublet/no-light-triplet generic zero pattern",
                "Barr--Raby additive-Abelian Higgs-mass obstruction",
            ],
            "open_requirements": [
                "mu and soft-scale generation without filling the light block",
                "all-order hierarchy protection and physical heavy thresholds",
            ],
        },
        "G5": {
            "state": "SINGLE_10_KSVZ_REJECTED__AXION_NEUTRINO_SPECTRUM_OPEN",
            "evidence_landed": [
                "the formal N_DW=1 single-10 KSVZ proposal is rejected because flipped hypercharge gives fractional states and nonuniversal Standard-Model beta shifts",
                "Barr--Raby neutrino scale identity is retained as an unprotected negative control",
            ],
            "open_requirements": [
                "a viable vectorlike KSVZ set complete under SO(10)xU(1)V-prime",
                "anomaly-safe PQ-quality symmetry compatible with anomalous U(1)A",
                "protected physical neutrino texture and complete chiral/gaugino spectrum",
                "cosmological initial-condition and relic calculation",
            ],
        },
        "G6": {
            "state": "FORMAL_GAUGE_ONLY_LEDGERS_LANDED__PHYSICAL_RGE_CHAIN_OPEN",
            "evidence_landed": [
                "Chacko stated spectrum fails the Planck-120 perturbative benchmark",
                "Barr--Raby gauge-only running is retained only as a negative-control benchmark",
                "flipped common-threshold gA=0 two-coupling running is explicitly formal",
            ],
            "open_requirements": [
                "stage-resolved SU(5)xU(1)X matching between vPhi and vC",
                "gauged anomalous-U(1)A and V-prime/U(1)A kinetic mixing, including the recorded B10,A term",
                "anomalous-U(1)A normalization above the level-one pole",
                "coupled gauge-Yukawa-soft running with physical stage thresholds",
                "scheme and independent numerical replay",
            ],
        },
        "G7": {
            "state": "DEPENDENCY_BLOCKED",
            "evidence_landed": [],
            "open_requirements": [
                "complete tree and pole spectrum",
                "threshold matching and mass-basis baryon-violating Wilson coefficients",
                "proton-decay calculation with hadronic inputs",
            ],
        },
        "G8": {
            "state": "DEPENDENCY_BLOCKED",
            "evidence_landed": [
                "published flipped qualitative flavour textures only",
            ],
            "open_requirements": [
                "global fermion/flavour fit with covariance",
                "proton, axion, neutrino, cosmology, and collider likelihoods",
                "versioned experimental and lattice input ledger",
            ],
        },
    }
    return [
        {
            "gate": gate,
            "qualified_id": f"research.susy_so10.v23.{gate}.full_closure",
            "closed": False,
            "full_gate_claim": False,
            **rows[gate],
        }
        for gate in (f"G{index}" for index in range(1, 9))
    ]


def source_failure_report(
    manifest: list[dict[str, Any]], failures: list[str],
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "terminal.susy_so10.v23.G1_G8.execution_verdict",
        "status": "V23_G1_G8_TERMINAL_LEDGER_SOURCE_FAILURE",
        "overall_state": "FAIL_CLOSED",
        "source_manifest": manifest,
        "upstream_core_pins": {
            name: row["core_sha256"] for name, row in UPSTREAMS.items()
        },
        "route_decision": {
            "complete_theory_selected": None,
            "primary_research_frontier": None,
            "decision_valid": False,
        },
        "model_artifact_classification": {},
        "gates": [
            {
                "gate": f"G{index}",
                "closed": False,
                "full_gate_claim": False,
                "state": "SOURCE_FAILURE",
            }
            for index in range(1, 9)
        ],
        "closure_counts": {"closed": 0, "open": 8},
        "terminal_verdict": {
            "complete_G1_G8_solution_exists_in_this_repository": False,
            "safe_to_claim_a_complete_predictive_theory": False,
            "stop_current_completion_claim": True,
        },
        "checks": {"all_pinned_sources_match": False},
        "n_checks": 1,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def build_report(root: Path = ROOT) -> dict[str, Any]:
    manifest = source_manifest(root)
    pin_failures = [
        f"source_pin:{row['path']}" for row in manifest if not row["matches"]
    ]
    if pin_failures:
        return source_failure_report(manifest, pin_failures)

    upstream = {
        name: load_json(root, definition["path"])
        for name, definition in UPSTREAMS.items()
    }
    v22r = upstream["v22r_degree4_eft"]
    chacko = upstream["chacko_unchanged_route"]
    barr = upstream["barr_raby_route"]
    flipped = upstream["flipped_missing_partner_route"]
    models = {
        name: (root / relative).read_text(encoding="utf-8")
        for name, relative in MODEL_PATHS.items()
    }

    core_pin_ledger = {
        name: {
            "path": definition["path"],
            "expected_core_sha256": definition["core_sha256"],
            "observed_core_sha256": upstream[name].get("core_sha256"),
            "canonical_core_valid": json_core_valid(upstream[name]),
            "matches": (
                upstream[name].get("core_sha256") == definition["core_sha256"]
                and json_core_valid(upstream[name])
            ),
        }
        for name, definition in UPSTREAMS.items()
    }

    route_decision = {
        "complete_theory_selected": None,
        "primary_research_frontier": "flipped_missing_partner_route",
        "decision_valid": True,
        "routes": [
            {
                "route": "v22r_degree4_eft",
                "disposition": "PRESERVED_FROZEN_FINITE_EFT__NOT_A_COMPLETE_THEORY",
                "accepted_as_complete_theory": False,
                "architecture_exactly_rejected": False,
                "retained_value": "reproducible degree-four sector-level EFT boundary",
                "reason": v22r["terminal_verdict"]["reason"],
            },
            {
                "route": "chacko_unchanged_route",
                "disposition": "EXACTLY_REJECTED_AT_STATED_UNCHANGED_ROUTE_SCOPE",
                "accepted_as_complete_theory": False,
                "architecture_exactly_rejected": True,
                "retained_value": "selector and gauge-running no-go certificate",
                "reason": chacko["route_verdict"]["reason"],
            },
            {
                "route": "barr_raby_route",
                "disposition": "EXACTLY_REJECTED_AS_ALL_ORDER_COMPLETION",
                "accepted_as_complete_theory": False,
                "architecture_exactly_rejected": True,
                "retained_value": "formal gauge-only RG negative control and conditional DW ledger",
                "reason": (
                    "The displayed symmetries allow XHplus*H1^2; its required VEV "
                    "fills the H1 doublet mass, and the exact residual additive-Abelian "
                    "identity prevents the stated architecture from forbidding it. The same "
                    "charge system also permits type-I messenger terms, all cross-driver "
                    "scale mixings, and a degree-five PQ-breaking operator."
                ),
            },
            {
                "route": "flipped_missing_partner_route",
                "disposition": "PRIMARY_RESEARCH_FRONTIER__NOT_PROMOTED_TO_COMPLETE_THEORY",
                "accepted_as_complete_theory": False,
                "architecture_exactly_rejected": False,
                "retained_value": (
                    "published generic missing-partner rank witness and comparatively mild "
                    "formal SO(10)xU(1)V-prime coefficient ledger"
                ),
                "reason": flipped["route_verdict"]["reason"],
            },
        ],
    }

    model_classification = {
        "v22r_degree4_eft": {
            "path": MODEL_PATHS["v22r_degree4_eft"],
            "SuperPotential": 0,
            "artifact_kind": "metadata-only Wolfram-syntax source scaffold",
            "wolfram_syntax_zero_W_stub": True,
            "SARAH_initialization_attested": False,
            "executable_SARAH_model_landed": False,
            "classification_basis": "pinned source plus frozen V22R G1 open requirement",
        },
        "chacko_unchanged_route": {
            "path": None,
            "artifact_kind": "analytic rejection certificate; no V23 model file",
            "wolfram_syntax_zero_W_stub": False,
            "SARAH_initialization_attested": False,
            "executable_SARAH_model_landed": False,
        },
        "barr_raby_route": {
            "path": MODEL_PATHS["barr_raby_route"],
            "SuperPotential": barr["model_source"]["SuperPotential"],
            "artifact_kind": barr["model_source"]["artifact_kind"],
            "wolfram_syntax_zero_W_stub": True,
            "Wolfram_syntax_parse_observed": barr["model_source"]["Wolfram_syntax_parse_observed"],
            "SARAH_initialization_attested": barr["model_source"]["SARAH_initialization_attested"],
            "executable_SARAH_model_landed": barr["model_source"]["executable_SARAH_model_landed"],
            "missing_auxiliary_model_files": barr["model_source"]["missing_auxiliary_model_files"],
        },
        "flipped_missing_partner_route": {
            "path": MODEL_PATHS["flipped_missing_partner_route"],
            "SuperPotential": flipped["model_source"]["SuperPotential"],
            "artifact_kind": flipped["model_source"]["artifact_kind"],
            "wolfram_syntax_zero_W_stub": True,
            "Wolfram_syntax_parse_observed": flipped["model_source"]["Wolfram_syntax_parse_observed"],
            "SARAH_initialization_attested": flipped["model_source"]["SARAH_initialization_attested"],
            "executable_SARAH_model_landed": flipped["model_source"]["executable_SARAH_model_landed"],
            "missing_auxiliary_model_files": flipped["model_source"]["missing_auxiliary_model_files"],
        },
    }

    gates = gate_ledger()
    expected_metadata = all(
        upstream[name].get(key) == definition[key]
        for name, definition in UPSTREAMS.items()
        for key in ("schema", "namespace", "status")
    )
    upstream_failure_free = all(
        row.get("n_failed") == 0 and row.get("failures") == []
        for row in upstream.values()
    )
    model_markers_exact = all(
        models[name].count("SuperPotential = 0;") == 1
        and models[name].count("NameOfStates = {GaugeES};") == 1
        for name in MODEL_PATHS
    )
    barr_rejected = (
        barr["overall_state"] == "REJECTED_AS_ALL_ORDER_COMPLETION"
        and barr["fatal_mass_operator"]["fields"] == ["XHplus", "H1", "H1"]
        and barr["fatal_mass_operator"]["forbidden_at_displayed_operator_level"] is False
        and barr["all_order_additive_Abelian_boundary"]
            ["all_order_additive_Abelian_DT_protection_exists"] is False
    )
    flipped_frontier = (
        flipped["route_verdict"]["safe_as_reproducible_research_frontier"] is True
        and flipped["route_verdict"]["accepted_as_complete_theory"] is False
        and flipped["route_verdict"]["safe_as_executable_SARAH_model"] is False
    )
    ranks = flipped["published_missing_partner_rank_ledger"]
    checks = {
        "all_pinned_sources_match": all(row["matches"] for row in manifest),
        "all_upstream_canonical_cores_are_valid_and_pinned": all(
            row["matches"] for row in core_pin_ledger.values()
        ),
        "all_upstream_schema_namespace_status_metadata_match": expected_metadata,
        "all_upstream_audits_are_failure_free": upstream_failure_free,
        "V22R_finite_EFT_is_preserved_but_not_promoted": (
            v22r["terminal_verdict"]["degree_four_EFT_is_mathematically_reproducible"] is True
            and v22r["terminal_verdict"]["complete_G1_G8_solution_exists_in_this_repository"] is False
            and v22r["closure_counts"] == {"closed": 0, "open": 8}
        ),
        "Chacko_unchanged_route_is_exactly_rejected": (
            chacko["overall_state"] == "ROUTE_REJECTED"
            and chacko["route_verdict"]["rejected_as_complete_G1_G8_route"] is True
            and chacko["route_verdict"]["accepted_as_V23_completion"] is False
        ),
        "Barr_Raby_all_order_architecture_is_exactly_rejected": barr_rejected,
        "flipped_route_is_primary_research_frontier_only": flipped_frontier,
        "flipped_published_structural_ranks_are_7_and_3": (
            ranks["triplet"]["generic_rank"] == 7
            and ranks["triplet"]["nullity"] == 0
            and ranks["doublet"]["generic_rank"] == 3
            and ranks["doublet"]["nullity"] == 1
        ),
        "flipped_anomalous_U1A_Planck_and_GS_completion_remain_open": (
            flipped["anomalous_U1A_frontier"]["Planck120_perturbativity_demonstrated"] is False
            and flipped["anomalous_U1A_frontier"]
                ["Green_Schwarz_normalization_and_hidden_spectrum_landed"] is False
        ),
        "landed_model_files_are_exact_zero_W_GaugeES_scaffolds": model_markers_exact,
        "V23_model_scaffolds_are_not_called_executable_SARAH_models": (
            model_classification["barr_raby_route"]["executable_SARAH_model_landed"] is False
            and model_classification["flipped_missing_partner_route"]
                ["executable_SARAH_model_landed"] is False
            and model_classification["barr_raby_route"]["SARAH_initialization_attested"] is False
            and model_classification["flipped_missing_partner_route"]
                ["SARAH_initialization_attested"] is False
        ),
        "exact_route_decision_has_no_complete_theory": (
            route_decision["complete_theory_selected"] is None
            and route_decision["primary_research_frontier"]
                == "flipped_missing_partner_route"
            and all(not row["accepted_as_complete_theory"] for row in route_decision["routes"])
            and route_decision["routes"][1]["architecture_exactly_rejected"] is True
            and route_decision["routes"][2]["architecture_exactly_rejected"] is True
            and route_decision["routes"][3]["architecture_exactly_rejected"] is False
        ),
        "flipped_formal_running_is_not_promoted_to_physical_RGE_closure": (
            flipped["coupled_two_loop_gauge_only_base"]
                ["formal_common_threshold_and_gA_zero_truncation"] is True
            and flipped["coupled_two_loop_gauge_only_base"]
                ["physical_stage_resolved_RGE_closed"] is False
            and flipped["coupled_two_loop_gauge_only_base"]
                ["omits_intermediate_SU5xU1X_breaking_and_matching"] is True
            and flipped["published_physics_caveats"]["vPhi_over_vC"] > 9
            and flipped["anomalous_U1A_frontier"]
                ["raw_Vprime_U1A_kinetic_mixing_trace"] == 48
            and flipped["anomalous_U1A_frontier"]["omitted_two_loop_B10_A_at_kA1"] == 1040
        ),
        "flipped_single_10_KSVZ_extension_is_exactly_rejected": (
            flipped["optional_KSVZ_extension"]["route_status"]
                == "REJECTED_SINGLE_SO10_10_KSVZ_COMPLETION"
            and flipped["optional_KSVZ_extension"]["viable_KSVZ_extension_landed"] is False
            and flipped["optional_KSVZ_extension"]["universal_below_GUT_threshold_exists"] is False
            and flipped["optional_KSVZ_extension"]["flipped_hypercharge_decomposition"]
                ["contains_fractionally_charged_states"] is True
            and flipped["optional_KSVZ_extension"]["flipped_hypercharge_decomposition"]
                ["delta_b_SM_canonical"] == {"b1": "1/10", "b2": 1, "b3": 1}
        ),
        "all_eight_full_G1_G8_gates_are_false_and_open": (
            len(gates) == 8
            and [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
            and all(
                row["closed"] is False and row["full_gate_claim"] is False
                for row in gates
            )
        ),
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    route_decision["decision_valid"] = not failures

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "terminal.susy_so10.v23.G1_G8.execution_verdict",
        "status": (
            "V23_G1_G8_EXECUTION_COMPLETE__PRIMARY_RESEARCH_FRONTIER_LANDED__"
            "NO_COMPLETE_THEORY__ZERO_OF_EIGHT_FULL_GATES"
            if not failures else "V23_G1_G8_TERMINAL_LEDGER_AUDIT_FAILED"
        ),
        "overall_state": (
            "END_AT_FAIL_CLOSED_RESEARCH_FRONTIER"
            if not failures else "FAIL_CLOSED_EXECUTION_ERROR"
        ),
        "campaign_scope": (
            "V22R frozen finite EFT plus V23 Chacko, Barr--Raby, and flipped "
            "missing-partner route evaluation"
        ),
        "source_manifest": manifest,
        "upstream_core_pins": core_pin_ledger,
        "route_decision": route_decision,
        "model_artifact_classification": model_classification,
        "gates": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "terminal_verdict": {
            "complete_G1_G8_solution_exists_in_this_repository": False,
            "safe_to_claim_a_complete_predictive_theory": False,
            "new_complete_physics_model_created": False,
            "reproducible_research_progress_created": not failures,
            "primary_research_frontier": "flipped_missing_partner_route",
            "reason": (
                "The campaign produced exact rejection certificates and a reproducible "
                "flipped missing-partner lead, but normalized tensors, an all-order selector, "
                "a global vacuum, stage-resolved physical thresholds and RGEs, a viable KSVZ "
                "sector, pole spectrum, proton decay, and fitted observables remain open."
            ),
            "stop_current_completion_claim": True,
        },
        "next_research_promotion_requirements": [
            "replace SuperPotential=0 by normalized nonzero component tensors and attest SARAH initialization",
            "land an anomaly/Green--Schwarz completion and all-order operator census for the flipped selector",
            "solve the full F+D+soft vacuum and physical doublet/triplet/exotic spectrum",
            "run coupled gauge-Yukawa-soft RGEs through physical thresholds",
            "fit flavour and calculate pole masses, proton decay, axion, neutrino, and cosmology likelihoods",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    if report["overall_state"] == "FAIL_CLOSED":
        return "\n".join([
            "# SUSY V23 G1--G8 execution verdict", "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            "- Result: fail-closed because one or more pinned source artifacts are missing or changed.",
            "- Full gates closed: `0/8`.", "",
        ])

    routes = {row["route"]: row for row in report["route_decision"]["routes"]}
    models = report["model_artifact_classification"]
    return "\n".join([
        "# SUSY V23 G1--G8 execution verdict", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Complete theory selected: **none**.",
        "- Primary research frontier: **flipped missing partner**.",
        "- Full gates closed: **0/8**.", "",
        "## Exact route decision", "",
        f"- **V22R:** `{routes['v22r_degree4_eft']['disposition']}`. It remains a reproducible finite degree-four EFT, not a full theory.",
        f"- **Chacko--Mohapatra:** `{routes['chacko_unchanged_route']['disposition']}`. The unchanged selector and stated gauge trajectory are rejected.",
        f"- **Barr--Raby:** `{routes['barr_raby_route']['disposition']}`. The required `XHplus` VEV activates the symmetry-allowed `XHplus*H1^2` mass; the exact residual-Abelian identity blocks the advertised all-order protection. Its messenger, cross-driver, and degree-five PQ leaks independently prevent promotion.",
        f"- **Flipped SO(10)xU(1):** `{routes['flipped_missing_partner_route']['disposition']}`. The published generic rank witness and exact base coefficient ledger justify continued research, not completion.", "",
        "## What the model files are", "",
        f"The V22R, Barr--Raby, and flipped `.m` artifacts are pinned source scaffolds with `SuperPotential=0`; they are not executable completed SARAH models. Barr--Raby reports `SARAH_initialization_attested={str(models['barr_raby_route']['SARAH_initialization_attested']).lower()}`, and flipped reports `SARAH_initialization_attested={str(models['flipped_missing_partner_route']['SARAH_initialization_attested']).lower()}`. A Wolfram-syntax parse is not a SARAH initialization or a physics-spectrum calculation.", "",
        "## Why all gates remain open", "",
        "The flipped lead has a published generic triplet rank `7/7` and doublet rank `3/4`, but normalized SO(10) component tensors, correlated thresholds, and the global F+D+soft vacuum are absent. Its displayed two-coupling RK endpoint is only a common-threshold `gA=0` truncation: it omits the `vPhi/vC=9.69` intermediate SU(5)xU(1)X stage, light FN thresholds, gauged anomalous U(1)A, and V-prime/U(1)A kinetic mixing (`Tr(V-prime A)=48`, `B10,A=1040`). U(1)A also has no landed Green--Schwarz normalization/hidden spectrum and fails the stated level-one Planck-running benchmark. The single neutral SO(10) 10 KSVZ proposal is rejected because flipped hypercharge produces fractional states and `Delta b=(1/10,1,1)`, not a universal threshold. Full Yukawa/soft running, pole masses, proton decay, flavour, neutrino, axion, and cosmology likelihoods are not computed.", "",
        "Therefore the honest terminal result is useful negative and frontier evidence, but no new complete predictive physics theory. The current completion claim stops at this exact open boundary.", "",
    ])


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write frozen JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="fail if frozen outputs have drifted")
    args = parser.parse_args()

    report = build_report()
    if report["n_failed"]:
        print(report["status"])
        print(report["core_sha256"])
        print(json.dumps(report["failures"], sort_keys=True))
        return 1
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            raise FileNotFoundError("frozen V23 terminal verdict outputs are missing")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V23 terminal verdict JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V23 terminal verdict Markdown drifted")

    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
