#!/usr/bin/env python3
"""Source-pinned G1--G8 execution verdict for the accepted V22R model.

This is the terminal ledger for the user-approved V22R execution.  It records
what was actually landed and distinguishes exact scoped results from full
physics-gate closure.  The terminal result is intentionally negative at
whole-theory scope: the degree-four EFT is reproducible, but no full G1--G8
gate is closed and the repository must not claim a predictive completed model.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22R_G1_G8_EXECUTION_VERDICT.json"
OUT_MD = ROOT / "SUSY_V22R_G1_G8_EXECUTION_VERDICT.md"
SCHEMA = "susy_v22r_g1_g8_execution_verdict_v1"

SOURCE_PINS = {
    "susy_v22r_broken_selector_spurion_frontier.py":
        "7d10d21d46e755e3c05f9981a8096cfeb41dd30cb73f8af5c0cdb99ba90138f9",
    "susy_v22r_operator_catalogue.py":
        "1c7ff5325229d3aaf9bac3ec56eb99e009b77bbf40b78ce9220d15f903b108ba",
    "susy_so10x17_v22r_contract.py":
        "f4a45d49c68393d765e445ac5acc2c50a7d47ba4d979d0a97c6e47d75dbea92c",
    "susy_v22r_g2_missing_partner_deformation_audit.py":
        "169c8cd3165a35b692f0560875f570dde6df0994554e7344b3d369952fa2da4a",
    "susy_v22r_g3_generic_vacuum_frontier.py":
        "5c520470b3ff10749727112cc346238d7f0b490c6005379edae1bfa1aec9cd9a",
    "susy_v22r_spectator_mass_frontier.py":
        "fd161599fece1a38e33003374f8d826262a2a11413cbf44abf0f7550211ff5f7",
    "models/SO10X17SUSYV22R/SO10X17SUSYV22R.m":
        "c792d94c01008a03e5ef8811652764094efdfa3276b4986aa5dc295e7015a77e",
    "SUSY_V22R_OPERATOR_CATALOGUE.json":
        "dbd3f87df836184673c6bf972c5c3d4a7f278ba19d7be20798db3cb7014d7b1f",
    "SUSY_SO10X17_V22R_CONTRACT.json":
        "9804311b0aa2ffb021205238a55438e990472b5ecaa4ef60a11de7256981b259",
    "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json":
        "c6cfb2dc6065d4bdb64d89d77389c9278c11a396e65dfd9f8b91ace2170ca9cd",
    "SUSY_V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT.json":
        "2f9c78dfd3e853c07c8ec2fa3db013522ee523e86ac4fa694bdcb1e56d560c1b",
    "SUSY_V22R_G3_GENERIC_VACUUM_FRONTIER.json":
        "2baefd7f6de9d3e9cb2a43cb8df9c52c6133321a4968bb717c09c34902898ce7",
    "SUSY_V22R_SPECTATOR_MASS_FRONTIER.json":
        "d3eb39c834d2329988e31618dd816ea7d24bc47a0495eb0ba8d25f494502bf59",
    "SUSY_V22_EXACT_EW_ENDPOINT.json":
        "98f9a54bded44d39f1a4abe0d33d02e8dc0de203ad51f27ae7ceefae5c75df0f",
    "SUSY_V22_PERTURBATIVE_WINDOW.json":
        "b4a634ed2b89d0967038131d8caee69e04d7502f02fc4482f765bb037c5ddf13",
    "SUSY_V22_G5_PHASE_COUNT.json":
        "bc2d8cba4f07c8a929a089d3ff2c633914c3bb6ef1dca262c55b3cab0513f7c7",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def core_sha(value: dict[str, Any]) -> str:
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


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


def json_core_valid(payload: dict[str, Any]) -> bool:
    return isinstance(payload.get("core_sha256"), str) and core_sha(payload) == payload["core_sha256"]


def failure_report(manifest: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "active.susy_so10x17.v22r.G1_G8.execution_verdict",
        "status": "V22R_G1_G8_LEDGER_SOURCE_FAILURE",
        "overall_state": "FAIL_CLOSED",
        "active_model": "SUSY SO(10) x U(1)_X V22R degree-four EFT",
        "source_manifest": manifest,
        "closure_counts": {"closed": 0, "open": 8},
        "gates": [
            {"gate": f"G{index}", "closed": False, "state": "SOURCE_FAILURE"}
            for index in range(1, 9)
        ],
        "checks": {"all_pinned_sources_match": False},
        "n_checks": 1,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = core_sha(report)
    return report


def build_report(root: Path = ROOT) -> dict[str, Any]:
    manifest = source_manifest(root)
    pin_failures = [f"source_pin:{row['path']}" for row in manifest if not row["matches"]]
    if pin_failures:
        return failure_report(manifest, pin_failures)

    catalogue = load_json(root, "SUSY_V22R_OPERATOR_CATALOGUE.json")
    contract = load_json(root, "SUSY_SO10X17_V22R_CONTRACT.json")
    spurion = load_json(root, "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json")
    g2 = load_json(root, "SUSY_V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT.json")
    g3 = load_json(root, "SUSY_V22R_G3_GENERIC_VACUUM_FRONTIER.json")
    spectator = load_json(root, "SUSY_V22R_SPECTATOR_MASS_FRONTIER.json")
    ew = load_json(root, "SUSY_V22_EXACT_EW_ENDPOINT.json")
    rge = load_json(root, "SUSY_V22_PERTURBATIVE_WINDOW.json")
    phase = load_json(root, "SUSY_V22_G5_PHASE_COUNT.json")
    payloads = {
        "catalogue": catalogue, "contract": contract, "spurion": spurion,
        "g2": g2, "g3": g3, "spectator": spectator, "ew": ew,
        "rge": rge, "phase": phase,
    }

    gates = [
        {
            "gate": "G1",
            "qualified_id": "active.susy_so10x17.v22r.G1.complete_susy_operator_contract",
            "state": "DEGREE4_BASE_SECTOR_SOURCE_CLOSED__FULL_G1_OPEN",
            "closed": False,
            "closed_subproblems": [
                "separate 33-field V22R source model",
                "Z28R x Z2S selector with recorded conventional single-factor anomaly ledgers",
                "complete 108-sector holomorphic base catalogue through degree four",
                "exact count of 265 SO(10)-and-flavour invariant components",
                "first audited broken-Z2S XMP-spurion leakage layer: 67 degree-five sectors and 160 components",
                "standard-embedding gauge-compensated diagonal Z28R stabilizer arithmetic",
            ],
            "open_requirements": [
                "construct and normalize all 265 invariant tensors (currently zero realizations landed)",
                "replace the metadata-only SuperPotential=0 scaffold by an executable component superpotential",
                "close the infinite broken-Z2S Wilsonian spurion tower",
                "close the Kahler and soft-operator rings",
                "complete the mixed-discrete and UV anomaly audit",
                "re-fit the enlarged matter/flavour sector",
            ],
        },
        {
            "gate": "G2",
            "qualified_id": "active.susy_so10x17.v22r.G2.full_component_projection",
            "state": "DEFORMATION_BASIS_AND_ABSTRACT_RANK_CLOSED__PHYSICAL_G2_OPEN",
            "closed": False,
            "closed_subproblems": [
                "ten direct degree-four missing-partner deformations and twenty invariant copies classified",
                "fourteen additional direct deformations and twenty-eight copies classified in the first audited XMP-spurion layer",
                "no light-light sector through the first audited XMP-spurion layer",
                "abstract generic doublet rank/nullity 10/1 and triplet rank/nullity 13/0",
            ],
            "open_requirements": [
                "normalized SO(10)-to-SM Clebsches for all 26 degree-four direct channels",
                "source-exact doublet and triplet component matrices",
                "rank evaluation on an exact full V22R vacuum",
                "all-order light-light zero-block proof",
            ],
        },
        {
            "gate": "G3",
            "qualified_id": "active.susy_so10x17.v22r.G3.global_F_D_soft_vacuum",
            "state": "REGULAR_INVARIANT_COORDINATE_BRANCH_EXISTS__FULL_G3_OPEN",
            "closed": False,
            "closed_subproblems": [
                "dense nonzero degree-four coefficient witness with exact F=0",
                "driver Jacobian rank five with nonzero minor -60",
                "nonempty regular branch with a formal one-complex-modulus quotient inside the restricted eight-coordinate slice",
                "all 28 diagonal Z28R elements compensated on the declared standard VEV pattern",
            ],
            "open_requirements": [
                "source-normalized component F terms and every SO(10) and U(1)X D generator",
                "global branch classification and exclusion of deeper vacua",
                "declared soft/Kahler potential and positive complete Hessian",
                "degree-five and higher spurion-corrected vacuum",
                "proof that every missing-partner 126 field has zero VEV",
            ],
        },
        {
            "gate": "G4",
            "qualified_id": "active.susy_so10x17.v22r.G4.protected_174GeV_hierarchy",
            "state": "SCOPED_ZERO_BLOCK_AND_EW_ENDPOINT_SURVIVE__DEPENDENCY_BLOCKED",
            "closed": False,
            "closed_subproblems": [
                "light-light holomorphic mass block absent through the audited first 67-sector XMP-spurion layer",
                "abstract one-doublet/no-triplet architecture",
                "exact 174 GeV tree electroweak endpoint",
            ],
            "open_requirements": [
                "physical G2 component ranks",
                "full G3 vacuum and Hessian",
                "soft/RGE/threshold bridge to the electroweak endpoint",
                "all-order hierarchy protection in holomorphic, Kahler and soft sectors",
                "UV completion before the one-loop SO(10) Landau pole",
            ],
        },
        {
            "gate": "G5",
            "qualified_id": "active.susy_so10x17.v22r.G5.calg_axion_and_full_spectrum",
            "state": "RESTRICTED_SLICE_ONE_MODULUS__THREE_MASSLESS_SPECTATORS__FULL_G5_OPEN",
            "closed": False,
            "closed_subproblems": [
                "formal one-complex-modulus quotient within the restricted eight-coordinate slice, plus three spectator flat directions",
                "legacy declared-VEV phase count gives one gauge-quotiented phase",
            ],
            "open_requirements": [
                "lift Z0, Z1 and Z2, which are absent from the degree-four catalogue and the audited first XMP-spurion layer and give three zero fermion-mass rows there",
                "determine the full gauge-quotiented vacuum dimension, which is at least four before spectator lifting",
                "identify the formal modulus with the physical axion multiplet",
                "construct the complete chiral-gaugino matrix and scalar spectrum",
                "prove phase alignment and positivity on the full soft vacuum",
                "close G4 first",
            ],
        },
        {
            "gate": "G6",
            "qualified_id": "active.susy_so10x17.v22r.G6.full_susy_RGE_matching_chain",
            "state": "ONE_LOOP_GAUGE_WINDOW_ONLY__FULL_G6_OPEN",
            "closed": False,
            "closed_subproblems": [
                "unchanged-field-content one-loop SO(10) coefficient b=272",
                "finite benchmark window through 1.5 M_GUT",
            ],
            "open_requirements": [
                "beta functions for the 265-component superpotential and soft sector",
                "stage-resolved thresholds and independent replay",
                "UV completion strictly below 2 M_GUT in the benchmark",
            ],
        },
        {
            "gate": "G7",
            "qualified_id": "active.susy_so10x17.v22r.G7.physical_pole_threshold_spectrum",
            "state": "DEPENDENCY_BLOCKED",
            "closed": False,
            "closed_subproblems": [],
            "open_requirements": [
                "source-exact scalar/vector/fermion/gaugino mass matrices",
                "declared renormalization and tadpole scheme",
                "self-energy pole solutions and complete threshold inventory",
            ],
        },
        {
            "gate": "G8",
            "qualified_id": "active.susy_so10x17.v22r.G8.proton_lifetime_distribution",
            "state": "DEPENDENCY_BLOCKED",
            "closed": False,
            "closed_subproblems": [],
            "open_requirements": [
                "physical gauge and color-triplet mediators from G7",
                "mass-basis Wilson matching and running from G6",
                "new V22R flavour fit/covariance and interference phases",
                "versioned lattice and experimental input ledger",
            ],
        },
    ]

    checks = {
        "all_pinned_sources_match": all(row["matches"] for row in manifest),
        "all_JSON_core_hashes_are_valid": all(json_core_valid(value) for value in payloads.values()),
        "all_scoped_evidence_artifacts_execute_without_failure": all(
            value["n_failed"] == 0 for value in payloads.values()
        ),
        "V22R_is_landed_as_a_separate_active_degree_four_EFT":
            contract["claim_boundary"]["active_V22R_source_model_landed"]
            and contract["overall_state"] == "ACTIVE_DEGREE4_EFT_SOURCE_LANDED",
        "catalogue_is_exactly_108_equal_29_plus_79":
            catalogue["counts"]["selected_base_sectors"] == 108
            and catalogue["counts"]["retained_v22_base_sectors"] == 29
            and catalogue["counts"]["forced_completion_base_sectors"] == 79,
        "265_components_are_counted_but_zero_tensor_realizations_are_landed":
            contract["operator_catalogue"]["counted_so10_flavour_components"] == 265
            and contract["operator_catalogue"]["component_tensor_realizations_landed"] == 0,
        "finite_catalogue_all_order_failure_is_explicit":
            not contract["all_order_boundary"]["finite_108_sector_catalogue_all_order_closed"]
            and spurion["first_audited_XMP_spurion_leakage_layer"]["sectors"] == 67
            and spurion["first_audited_XMP_spurion_leakage_layer"]["so10_flavour_components"] == 160
            and spurion["first_audited_XMP_spurion_leakage_layer"]["source_degree"] == 5
            and not spurion["first_audited_XMP_spurion_leakage_layer"]["complete_degree_five_census"],
        "G2_deformations_and_abstract_ranks_are_exact_but_physical_G2_is_open":
            g2["accepted_basis"]["direct_missing_partner_deformation_sectors"] == 10
            and g2["accepted_basis"]["direct_deformation_SO10_singlet_contraction_channels"] == 20
            and g2["rank_implications"]["doublet"]["abstract_generic_rank"] == 10
            and g2["rank_implications"]["triplet"]["abstract_generic_rank"] == 13
            and not g2["claim_boundary"]["V22R_G2_closed"],
        "G3_regular_branch_exists_but_full_G3_is_open":
            g3["exact_dense_coefficient_witness"]["Jacobian_rank"] == 5
            and g3["claim_boundary"]["restricted_eight_coordinate_slice_has_one_formal_complex_modulus_after_two_direction_gauge_quotient"]
            and g3["claim_boundary"]["full_declared_degree_four_EFT_quotient_dimension_is_at_least_four"]
            and not g3["claim_boundary"]["full_declared_degree_four_EFT_has_exactly_one_complex_modulus"]
            and not g3["claim_boundary"]["V22R_G3_closed"],
        "three_massless_spectator_chiral_multiplets_block_full_G5_in_scope":
            spectator["mass_matrix_consequence"]["minimum_massless_chiral_multiplets_in_scope"] == 3
            and not spectator["claim_boundary"]["V22R_G5_closed"],
        "exact_174_GeV_endpoint_remains_scoped_only":
            ew["checks"]["complex_VEV_radius_is_exactly_174_GeV"]
            and not ew["claim_boundary"]["canonical_G4_closed"],
        "one_loop_SO10_window_requires_UV_completion_before_2MGUT":
            rge["SO10"]["b_one_loop"] == 272
            and rge["declared_validity"]["mandatory_UV_completion_scale"].startswith("strictly below 2 M_GUT"),
        "legacy_phase_count_is_not_promoted_over_the_new_spectrum_obstruction":
            phase["exact_counts"]["physical_GUT_phase_dimension"] == 1
            and not phase["claim_boundary"]["canonical_G5_closed"],
        "all_eight_full_gates_remain_open": all(not gate["closed"] for gate in gates),
        "complete_predictive_theory_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "active.susy_so10x17.v22r.G1_G8.execution_verdict",
        "status": (
            "V22R_G1_G8_EXECUTION_COMPLETE__DEGREE4_EFT_LANDED__NO_FULL_GATE_CLOSED"
            if not failures else "V22R_G1_G8_EXECUTION_AUDIT_FAILED"
        ),
        "overall_state": "END_AT_EXACT_OPEN_BOUNDARY" if not failures else "EXECUTION_FAIL",
        "active_model": "SUSY SO(10) x U(1)_X V22R degree-four EFT",
        "model_lineage": {
            "V22": "frozen sparse baseline and no-go provenance",
            "V22R": "user-approved active degree-four EFT completion",
            "V21": "superseded non-supersymmetric hierarchy no-go only",
        },
        "source_manifest": manifest,
        "execution_summary": {
            "new_fields": 0,
            "source_model_landed": True,
            "base_sectors_landed": 108,
            "counted_invariant_components": 265,
            "normalized_tensor_realizations_landed": 0,
            "first_audited_XMP_spurion_leakage_degree_five_sectors": 67,
            "G2_direct_degree_four_deformations": 10,
            "G3_regular_dense_singlet_branch_exhibited": True,
            "massless_spectator_chiral_multiplets_through_first_audited_XMP_spurion_layer": 3,
        },
        "gates": gates,
        "closure_counts": {
            "closed": sum(gate["closed"] for gate in gates),
            "open": sum(not gate["closed"] for gate in gates),
        },
        "terminal_verdict": {
            "degree_four_EFT_is_mathematically_reproducible": not failures,
            "complete_G1_G8_solution_exists_in_this_repository": False,
            "safe_to_claim_a_complete_predictive_theory": False,
            "stop_current_execution": True,
            "reason": (
                "The accepted sector-level repair is real as a finite EFT truncation, but the component "
                "superpotential, all-order operator contract, physical missing-partner matrices, global soft "
                "vacuum, spectator masses, RG chain, pole spectrum and proton lifetime are not determined."
            ),
        },
        "critical_unresolved_inputs": [
            "265 normalized SO(10) invariant tensors and component Clebsches",
            "a UV rule or power counting for the infinite broken-Z2S spurion tower",
            "a complete Kahler, soft-breaking and/or supergravity contract that also lifts Z0/Z1/Z2",
            "a global F+D+soft vacuum and positive physical Hessian",
            "a UV completion below the benchmark SO(10) Landau pole",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = core_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    if report["status"] == "V22R_G1_G8_LEDGER_SOURCE_FAILURE":
        return "\n".join([
            "# SUSY V22R G1--G8 execution verdict", "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`", "",
            "A pinned source changed or disappeared. The ledger fails closed and no gate is promoted.", "",
        ])
    execution = report["execution_summary"]
    return "\n".join([
        "# SUSY V22R G1--G8 execution verdict", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Full gates closed/open: `{report['closure_counts']['closed']}/{report['closure_counts']['open']}`",
        f"- Active degree-four catalogue: `{execution['base_sectors_landed']}` sectors / "
        f"`{execution['counted_invariant_components']}` counted components.",
        f"- Normalized component tensors landed: `{execution['normalized_tensor_realizations_landed']}`.",
        f"- First audited XMP-spurion leakage layer: "
        f"`{execution['first_audited_XMP_spurion_leakage_degree_five_sectors']}` degree-five sectors.",
        f"- Exact massless spectators in the audited scope: "
        f"`{execution['massless_spectator_chiral_multiplets_through_first_audited_XMP_spurion_layer']}`.", "",
        "The user-approved V22R repair was executed as far as the source data support. The separate model,",
        "108-sector catalogue, anomaly/selector contract, G2 deformation audit, and a dense regular G3",
        "singlet-branch witness are landed and reproducible.", "",
        "The whole theory is not solved. All eight full gates remain open: no normalized component",
        "superpotential exists, Z2S breaking opens an infinite Wilsonian tower, physical doublet/triplet",
        "Clebsches and the global soft vacuum are missing, and three anomaly spectators are massless through",
        "the first leakage layer. G6--G8 consequently have no physical spectrum or proton-lifetime output.", "",
        "This is the honest end point: a real degree-four EFT construction, not a complete predictive G1--G8 theory.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V22R G1--G8 verdict JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R G1--G8 verdict Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
