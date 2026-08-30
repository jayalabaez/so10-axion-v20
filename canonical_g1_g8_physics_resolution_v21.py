#!/usr/bin/env python3
"""Fail-closed physics adjudication of the canonical gauged-X G1--G8 chain.

This module does not manufacture closure evidence for an open gate.  It binds
the accepted canonical contract to the exact G4/G5 obstruction and the exact
G6--G8 non-identifiability witnesses, then separates three different outcomes:

* CLOSED: the canonical acceptance criteria have verified evidence;
* REJECTED_CURRENT_CONTRACT: the frozen V21 model fails a required criterion;
* UNDERDETERMINED: continuous inputs remain free, so no unique prediction is
  defined by the frozen theory data.

The result is a resolution of the present model's physics status, not a claim
that all eight positive canonical gates are closed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.json"
OUT_MD = ROOT / "CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.md"

SCHEMA = "canonical_g1_g8_physics_resolution_v21"
CONTRACT_NAMESPACE = "canonical.gauged_u1x.phenomenology.v21"

# Raw byte pins deliberately make the adjudication fail closed if any upstream
# evidence is regenerated or edited.  A changed source must be reviewed and
# explicitly repinned here.
SOURCE_PINS = {
    "CANONICAL_G1_G8_GAUGED_U1X_V21.json":
        "b5c8977b97f6f14a12a66ec20c8ba278ff1f8406b22d823b3eac7d4028fa4d1d",
    "CANONICAL_G4_G5_CURRENT_CONTRACT_OBSTRUCTION_V21.json":
        "9d426e4e11bbec61a446cb54d9fb8b398a0a4fa050878bfce373b4b1459e4888",
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json":
        "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a",
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json":
        "bb58ef10bef730cefa8da4cee342711e1033134a5e9468febed5cc0f8a93acac",
    "SUSY_SO10X17_V22_CONTRACT.json":
        "4bd5f2f829fbaf7d88b1a535a0eba295222cd07418ad8dd4d3c84e0365c41cc1",
    "SUSY_V22_G4_PROTECTION_FRONTIER.json":
        "97bab837e20da1d5b8766a6b2e9e7bb57f7051b49c5f20772e6d75d80c4adb44",
    "SUSY_V22_G5_PHASE_COUNT.json":
        "bc2d8cba4f07c8a929a089d3ff2c633914c3bb6ef1dca262c55b3cab0513f7c7",
    "SUSY_V22_EXACT_EW_ENDPOINT.json":
        "98f9a54bded44d39f1a4abe0d33d02e8dc0de203ad51f27ae7ceefae5c75df0f",
    "SUSY_V22_ALL_ORDER_R_PROTECTION.json":
        "18fe2443b741597aa241df8ff6f3d8461ad2db697c0a101759941f8204d7849e",
    "SUSY_V22_Z4R_ANOMALY.json":
        "3a9852341b7299777024bc8fa8b0b10df2dde19345b641d630e8cf2ec5bd6f24",
    "SUSY_V22_PERTURBATIVE_WINDOW.json":
        "b4a634ed2b89d0967038131d8caee69e04d7502f02fc4482f765bb037c5ddf13",
    "SUSY_V22_MISSING_PARTNER_RANK.json":
        "52519f26c02807595341d1ba5a7c065c61f51a8b96e6e28061c3cc8b8c06ca94",
    "SUSY_V22_F_FLAT_GUT_SLICE.json":
        "8f001bfa9ecd235b1a2c078489206126951a486880cccd381f8e99ee713a15eb",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _core_sha256(value: dict[str, Any]) -> str:
    core = dict(value)
    core.pop("core_sha256", None)
    return _sha256_bytes(_json_bytes(core))


def _load_sources(root: Path) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    payloads: dict[str, Any] = {}
    manifest: list[dict[str, str]] = []
    failures: list[str] = []
    for name, expected_sha in SOURCE_PINS.items():
        path = root / name
        if not path.is_file() or path.is_symlink():
            failures.append(f"missing_or_unsafe_source:{name}")
            continue
        raw = path.read_bytes()
        actual_sha = _sha256_bytes(raw)
        manifest.append(
            {
                "path": name,
                "mode": "raw",
                "sha256": actual_sha,
                "expected_sha256": expected_sha,
            }
        )
        if actual_sha != expected_sha:
            failures.append(f"source_sha256_mismatch:{name}")
            continue
        try:
            payloads[name] = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            failures.append(f"invalid_json:{name}")
    return payloads, manifest, failures


def _check(condition: bool, label: str, checks: dict[str, bool], failures: list[str]) -> None:
    value = condition is True
    checks[label] = value
    if not value:
        failures.append(label)


def build_report(root: Path = ROOT) -> dict[str, Any]:
    payloads, source_manifest, failures = _load_sources(root)
    checks: dict[str, bool] = {}

    required = set(SOURCE_PINS)
    _check(set(payloads) == required, "all_source_pins_match", checks, failures)
    if set(payloads) != required:
        report = {
            "schema": SCHEMA,
            "contract_namespace": CONTRACT_NAMESPACE,
            "status": "SOURCE_BINDING_FAILURE",
            "overall_resolution": "UNRESOLVED",
            "canonical_positive_gates_closed": False,
            "whole_model_validated": False,
            "source_manifest": source_manifest,
            "checks": checks,
            "n_checks": len(checks),
            "failures": failures,
            "n_failed": len(failures),
            "gates": [],
        }
        report["core_sha256"] = _core_sha256(report)
        return report

    canonical = payloads["CANONICAL_G1_G8_GAUGED_U1X_V21.json"]
    obstruction = payloads[
        "CANONICAL_G4_G5_CURRENT_CONTRACT_OBSTRUCTION_V21.json"
    ]
    g67 = payloads["EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json"]
    g8 = payloads["EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"]

    _check(canonical.get("n_failed") == 0, "canonical_contract_self_checks_pass", checks, failures)
    _check(
        canonical.get("contract_namespace") == CONTRACT_NAMESPACE,
        "canonical_namespace_matches",
        checks,
        failures,
    )
    canonical_gates = canonical.get("gates", [])
    canonical_closure = [row.get("closed") is True for row in canonical_gates]
    _check(
        canonical_closure == [True, True, True, False, False, False, False, False],
        "canonical_closure_vector_is_11100000",
        checks,
        failures,
    )

    hierarchy = obstruction["exact_hierarchy_continuity"]
    current_ratio = Fraction(hierarchy["current_G3_H_over_Phi_squared"])
    required_ratio = Fraction(hierarchy["required_physical_H_over_Phi_squared"])
    mismatch = current_ratio / required_ratio
    _check(obstruction.get("n_failed") == 0, "G4_G5_obstruction_checks_pass", checks, failures)
    _check(current_ratio == 2, "G4_current_ratio_is_exactly_two", checks, failures)
    _check(
        required_ratio == Fraction(1682, 2732169209454242979737518576201),
        "G4_required_physical_ratio_is_exact",
        checks,
        failures,
    )
    _check(
        mismatch == Fraction(2732169209454242979737518576201, 841),
        "G4_ratio_mismatch_factor_is_exact",
        checks,
        failures,
    )
    _check(
        hierarchy["common_rescaling_cannot_repair"] is True,
        "G4_common_rescaling_cannot_repair",
        checks,
        failures,
    )
    _check(
        obstruction["linear_internal_symmetry_theorem"]["source_bound_conclusion"]
        == "no declared linear internal symmetry forbids the H mass or neutral heavy portals",
        "G4_declared_symmetries_do_not_protect_H",
        checks,
        failures,
    )
    lock = obstruction["lambda_lock_and_phase"]
    _check(
        lock["G3_lambda_lock_coefficient_is_exactly_zero"] is True,
        "G5_live_lambda_lock_is_zero_on_G3",
        checks,
        failures,
    )
    _check(
        obstruction["canonical_gate_evaluation"]["G4"]["closed"] is False
        and obstruction["canonical_gate_evaluation"]["G5"]["closed"] is False,
        "G4_G5_positive_closure_is_false",
        checks,
        failures,
    )

    _check(g67.get("n_failed") == 0, "G6_G7_frontier_checks_pass", checks, failures)
    witnesses67 = g67["exact_nonidentifiability_witnesses"]
    _check(
        witnesses67["vector_common_scale"]["threshold_changes"] is True
        and witnesses67["vector_common_scale"]["absolute_vector_scale_identified"] is False,
        "G6_G7_vector_scale_family_is_nonidentifiable",
        checks,
        failures,
    )
    _check(
        witnesses67["scalar_EFT_b_scale"]["scale_changes"] is True
        and witnesses67["scalar_EFT_b_scale"]["dimensionful_scalar_scale_identified"] is False,
        "G7_scalar_scale_family_is_nonidentifiable",
        checks,
        failures,
    )
    _check(
        witnesses67["flavor_boundaries"]["flavor_boundary_values_identified"] is False
        and witnesses67["flavor_boundaries"]["raw_complex_entries_before_flavour_quotients"] == 50,
        "G6_G7_flavor_family_is_nonidentifiable",
        checks,
        failures,
    )

    _check(g8.get("n_failed") == 0, "G8_frontier_checks_pass", checks, failures)
    witnesses8 = g8["exact_nonidentifiability_witnesses"]
    _check(
        witnesses8["absolute_vector_scale"]["mass_ratio"] == "2"
        and witnesses8["absolute_vector_scale"]["partial_lifetime_ratio_at_fixed_dimensionless_data"] == "16",
        "G8_lifetime_scales_as_lambda_four",
        checks,
        failures,
    )
    _check(
        witnesses8["finite_limit_crossing"]["model_classification_identified_without_absolute_scale"] is False,
        "G8_finite_limit_classification_is_not_identified",
        checks,
        failures,
    )
    _check(
        all(row["passed"] is False for row in g8["acceptance_matrix"].values()),
        "G8_all_five_acceptance_criteria_fail",
        checks,
        failures,
    )

    susy_contract = payloads["SUSY_SO10X17_V22_CONTRACT.json"]
    susy_g4 = payloads["SUSY_V22_G4_PROTECTION_FRONTIER.json"]
    susy_g5 = payloads["SUSY_V22_G5_PHASE_COUNT.json"]
    susy_window = payloads["SUSY_V22_PERTURBATIVE_WINDOW.json"]
    _check(
        susy_contract.get("n_failed") == 0
        and susy_contract["claim_boundary"]["canonical_G4_closed"] is False
        and susy_contract["claim_boundary"]["canonical_G5_closed"] is False,
        "SUSY_V22_is_not_promoted_to_canonical_G4_G5",
        checks,
        failures,
    )
    _check(
        susy_g4.get("n_failed") == 0 and susy_g5.get("n_failed") == 0,
        "SUSY_V22_scoped_frontiers_pass",
        checks,
        failures,
    )
    _check(
        susy_window["checks"]["coupling_is_finite_through_1p5_MGUT"] is True
        and susy_window["checks"]["one_loop_Landau_pole_occurs_before_2_MGUT"] is True,
        "SUSY_V22_requires_nearby_UV_completion",
        checks,
        failures,
    )

    gates = [
        {
            "gate": "G1",
            "canonical_closed": True,
            "resolution_state": "CLOSED",
            "physics_outcome": "complete derivative-free scalar operator ring through dimension six accepted",
        },
        {
            "gate": "G2",
            "canonical_closed": True,
            "resolution_state": "CLOSED",
            "physics_outcome": "full normalized component projection accepted",
        },
        {
            "gate": "G3",
            "canonical_closed": True,
            "resolution_state": "CLOSED",
            "physics_outcome": "physical-EW global vacuum, 37 broken gauge directions and complete Hessian accepted",
        },
        {
            "gate": "G4",
            "canonical_closed": False,
            "resolution_state": "REJECTED_CURRENT_CONTRACT",
            "physics_outcome": (
                "the accepted V21 branch has the wrong exact H/Phi hierarchy and no declared "
                "linear internal symmetry forbids the destabilizing Higgs mass/portal operators"
            ),
            "exact_witness": {
                "current_H_over_Phi_squared": str(current_ratio),
                "required_H_over_Phi_squared": str(required_ratio),
                "mismatch_factor": str(mismatch),
            },
        },
        {
            "gate": "G5",
            "canonical_closed": False,
            "resolution_state": "REJECTED_CURRENT_CONTRACT_AND_DEPENDENCY_BLOCKED",
            "physics_outcome": (
                "G4 is rejected and the accepted G3 point sets the live lambda-lock coefficient "
                "exactly to zero, so the required cal-G lift is absent"
            ),
        },
        {
            "gate": "G6",
            "canonical_closed": False,
            "resolution_state": "UNDERDETERMINED_AND_DEPENDENCY_BLOCKED",
            "physics_outcome": (
                "the full non-supersymmetric two-loop chain is not defined by the frozen data; "
                "absolute vector scale and 50 complex flavor entries remain free"
            ),
        },
        {
            "gate": "G7",
            "canonical_closed": False,
            "resolution_state": "UNDERDETERMINED_AND_DEPENDENCY_BLOCKED",
            "physics_outcome": (
                "continuous vector-scale, scalar-b and flavor families change the pole/threshold "
                "outputs while preserving the closed normalized subtheorems"
            ),
        },
        {
            "gate": "G8",
            "canonical_closed": False,
            "resolution_state": "NONPREDICTIVE_AND_DEPENDENCY_BLOCKED",
            "physics_outcome": (
                "no unique proton lifetime or propagated distribution exists; M_X -> lambda M_X "
                "changes a nonzero gauge-mediated lifetime by lambda^4"
            ),
        },
    ]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "contract_namespace": CONTRACT_NAMESPACE,
        "status": "G1_G8_PHYSICS_ADJUDICATED__V21_REJECTED_AT_G4__G5_G8_NONPREDICTIVE",
        "overall_resolution": "CURRENT_NONSUSY_V21_MODEL_REJECTED",
        "canonical_positive_gates_closed": False,
        "whole_model_validated": False,
        "highest_consecutive_closed_gate": "G3",
        "canonical_closure_counts": {"closed": 3, "open": 5},
        "adjudication_counts": {
            "closed": 3,
            "rejected_current_contract": 2,
            "underdetermined_or_nonpredictive": 3,
        },
        "gates": gates,
        "model_decision": {
            "continue_V21_to_proton_prediction": False,
            "reason": "G4 is exactly incompatible with the accepted V21 G3 branch",
            "honest_next_route": (
                "continue with the active SUSY V22 replacement, completing its independent G1-G3 "
                "before promoting its existing G4-G5 protection subtheorems"
            ),
        },
        "active_SUSY_V22_route": {
            "canonical_substitute": False,
            "scoped_progress": [
                "one protected doublet pair and no triplet zero mode in the rank architecture",
                "an exact 174 GeV electroweak endpoint",
                "an all-order holomorphic R-selection rule with mixed Z4R anomaly cancellation",
                "one physical phase after the GUT and electroweak gauge quotients",
                "an exact local F/D-flat singlet slice",
            ],
            "blocking_facts": [
                "the V22 operator ring and full component projections are open",
                "the global F+D+soft vacuum and canonical G1-G3 have not been recomputed",
                "component Clebsches, pole spectrum and tensor RGE/threshold bridge are open",
                "the one-loop Landau pole lies below 2 M_GUT, so a nearby UV completion is required",
            ],
        },
        "claim_boundary": {
            "all_eight_positive_gates_closed": False,
            "a_decisive_negative_resolution_is_not_positive_gate_closure": True,
            "no_unique_proton_lifetime_reported": True,
            "no_SUSY_result_is_used_to_close_a_nonsupersymmetric_V21_gate": True,
        },
        "source_manifest": source_manifest,
        "producer": {
            "path": Path(__file__).name,
            "raw_sha256": _sha256_bytes(Path(__file__).read_bytes()),
        },
        "checks": checks,
        "n_checks": len(checks),
        "failures": failures,
        "n_failed": len(failures),
    }
    report["core_sha256"] = _core_sha256(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "# Canonical G1--G8 physics resolution v21\n\n"
            f"**Status:** `{report['status']}`\n\n"
            "The source-bound adjudication failed closed. See the JSON artifact for failures.\n"
        )

    lines = [
        "# Canonical G1--G8 physics resolution v21",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "The eight gates are now scientifically adjudicated for the frozen non-supersymmetric V21 contract. "
        "G1--G3 close positively. G4 is exactly incompatible with the accepted G3 vacuum, G5 fails its live "
        "lock requirement and depends on G4, and G6--G8 remain underdetermined/nonpredictive. This is a decisive "
        "negative model resolution, not eight positive gate closures.",
        "",
        "## Gate outcomes",
        "",
    ]
    for row in report["gates"]:
        lines.extend(
            [
                f"### {row['gate']} -- {row['resolution_state']}",
                "",
                row["physics_outcome"] + ".",
                "",
            ]
        )
        witness = row.get("exact_witness")
        if witness:
            lines.extend(
                [
                    f"- Current exact `||H||^2/||Phi||^2`: `{witness['current_H_over_Phi_squared']}`",
                    f"- Required physical ratio: `{witness['required_H_over_Phi_squared']}`",
                    f"- Exact mismatch factor: `{witness['mismatch_factor']}`",
                    "",
                ]
            )

    lines.extend(
        [
            "## Model decision",
            "",
            "Do not continue the V21 chain to a unique proton-lifetime claim. The honest route is to supersede "
            "the model with an explicit hierarchy-protection mechanism and recompute G1--G3 before reattempting "
            "G4--G8.",
            "",
            "SUSY V22 is the active replacement model, not inherited V21 canonical evidence: its protected "
            "doublet architecture, exact 174 GeV endpoint, R-selection rule and one-phase quotient are scoped "
            "subtheorems. Its operator ring, full component projection, global F+D+soft vacuum, pole spectrum and "
            "RGE/threshold bridge remain open, and its one-loop Landau pole below `2 M_GUT` requires a nearby UV "
            "completion.",
            "",
            f"Checks: `{report['n_checks']}`; failures: `{report['n_failed']}`.",
            "",
            f"Core SHA-256: `{report['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: dict[str, Any], root: Path = ROOT) -> None:
    (root / OUT_JSON.name).write_bytes(_json_bytes(report))
    (root / OUT_MD.name).write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and print the compact result without writing artifacts",
    )
    args = parser.parse_args()
    report = build_report()
    if not args.check:
        write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_resolution": report["overall_resolution"],
                "n_failed": report["n_failed"],
                "core_sha256": report["core_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
