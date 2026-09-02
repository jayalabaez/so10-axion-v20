#!/usr/bin/env python3
"""V87 multipath G1 frontier master audit.

Bind the canonical V86 master to the V87 compact/bisection/B-neutral route,
record exactly which V86 obstructions are superseded on the selected branch,
and preserve every unresolved same-action obligation fail-closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V86_MASTER_PATH = ROOT / "SUSY_V86_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V87_ROUTE_PATH = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V87_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V87_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v87_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v86_master": "9fa1d73f2ba1a5f69906bf05ffb5db8db48b05cf466c871b727035f17c7d4aba",
    "v87_route": "2cc908183f77848f292ced26a8cd5dd6bf923fb7ef11140d9d20ac35d0c07e9e",
}

SCHEMA = "susy_v87_multipath_g1_frontier_master_audit_v1"
VERSION = "V87"
DATE = "2026-09-01"
STATUS = (
    "V87_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V86_MASTER_AND_V87_ROUTE_CORES_BOUND__"
    "GLOBAL_PROJECTIVE_CREPANT_AMBIENT_AND_COMPACT_FLATNESS_EXACT__FORMAL_EULER_MINUS520__"
    "COMPACT_STRICT_TRANSFORM_SMOOTHNESS_OPEN__PERIOD2_BISECTION_AND_NON_SPLIT_I2STAR_JACOBIAN_EXACT__"
    "RESOLVED_BISECTION_CENTER_RELATION_OPEN__B_NEUTRAL_FIXED_PHASE_CANDIDATE_AND_RANK1_EXACT__FULL_SPACE_GROUP_PROJECTORS_OPEN__"
    "ALL_DISPLAYED_ORDINARY_C4_RESIDUES_ZERO__ZERO_MODE_K2_NOT_REQUIRED__UV_COUNTERTERM_OPEN__"
    "SMOOTH_GF_AW4_CHARACTER_EXACT_WITH_ZERO_ZERO_MODE_COEFFICIENT__FULL_STRATIFIED_DAIFREED_OPEN__"
    "RESIDUAL_C2_NOT_FAITHFUL_C4__NO_ACCEPTED_EXTENSION__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if value["core_sha256"] != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def route_matrix(v86_master: Mapping[str, Any], v87: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = copy.deepcopy(v86_master["route_matrix"])
    rows.append({
        "ordinal": len(rows) + 1,
        "route_id": "B87",
        "name": "compact ambient/flatness, period-two bisection, B-neutral fixed-phase candidate and smooth GF character",
        "same_action_microscopic_completion": False,
        "accepted": False,
        "selected_exact_scaffolds": copy.deepcopy(v87["candidate_adjudication"]["selected_exact_scaffolds"]),
    })
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    raw = [
        ("A1", "V86 master and V87 route canonical lineage", "PASS_EXACT"),
        ("A2", "global smooth projective ambient five-blowup sequence", "PASS_EXACT"),
        ("A3", "crepant discrepancies", "PASS_EXACT_ALL_ZERO"),
        ("A4", "compact hypersurface flatness", "PASS_EXACT"),
        ("A5", "independent formal Chern pushforward", "PASS_EXACT_EULER_MINUS520"),
        ("A6", "actual compact strict-transform Cox Jacobian saturation", "OPEN_UNCOMPUTED"),
        ("A7", "unconditional compact Hodge numbers", "OPEN_CONDITIONAL_8_268_REQUIRES_SMOOTHNESS_MW0_AND_NO_EXTRA_DIVISORS"),
        ("A8", "explicit genus-one period and index", "PASS_EXACT_2_2"),
        ("A9", "Jacobian non-split I2-star Spin11 model and eight branch points", "PASS_EXACT"),
        ("A10", "global crepant resolution of the bisection total space", "OPEN_UNCONSTRUCTED"),
        ("A11", "resolved bisection component intersections and j-squared-center relation", "OPEN_UNCOMPUTED"),
        ("A12", "B-neutral qF(A,B,C) assignment", "PASS_EXACT_2_0_2"),
        ("A13", "B-neutral four-stratum phase candidate", "PASS_EXACT_PHASE_TABLE_ONLY"),
        ("A13B", "full Gammahat lift/kernel restores all V70 charged-hyper projectors", "OPEN_UNCONSTRUCTED"),
        ("A14", "rank-one doublet matrix and light HuA/HdC pair", "PASS_EXACT"),
        ("A15", "B-neutral ordinary C4 anomaly tensor", "PASS_EXACT_12_16_432_672_64_112_0_0_48"),
        ("A16", "all displayed B-neutral ordinary C4 residues", "PASS_EXACT_ZERO"),
        ("A17", "V86 qF(B)=2 nonzero residue", "SUPERSEDED_BRANCH_CORRECT_NOT_SELECTED"),
        ("A18", "V86 order-two k2 term in the displayed B-neutral zero-mode shadow", "NOT_REQUIRED_BY_ZERO_MODE_SHADOW"),
        ("A18B", "UV k2 counterterm after massive/fixed-wall eta contributions", "OPEN_UNDETERMINED"),
        ("A19", "charge-four GS/Stueckelberg divisibility and factorization screen", "PASS_EXACT_INTEGER_LEVELS"),
        ("A20", "supersymmetric differential GS cocycle and common regulator", "OPEN_UNCONSTRUCTED"),
        ("A21", "ordinary smooth GF bundle constraint and a*w4 character", "PASS_EXACT"),
        ("A22", "full Omega5 and fermionic Dai-Freed character", "OPEN_UNCOMPUTED"),
        ("A23", "B0/X/Xbar abstract vacuum stabilizer", "PASS_EXACT_RESIDUAL_C2"),
        ("A24", "faithful low-energy C4 selector", "REJECTED_ABSENT_ON_SELECTED_VACUUM"),
        ("A25", "global diagonal bisection-C4/Sp3 bundle", "OPEN_UNCONSTRUCTED"),
        ("A26", "full stratified HGamma target and fixed-wall isotropy data", "OPEN_UNFORMULATED"),
        ("A27", "fixed-wall eta/Dai-Freed trivialization with one regulator", "OPEN_UNCOMPUTED"),
        ("A28", "all-order operator closure and even B0 driver", "OPEN_UNPROVED"),
        ("A29", "same-action microscopic completion", "REJECTED_NOT_FOUND"),
        ("A30", "soft spectrum, thresholds, cosmology and likelihood", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in raw]


def build_report() -> dict[str, Any]:
    v86 = load_bound(V86_MASTER_PATH, EXPECTED_CORES["v86_master"])
    v87 = load_bound(V87_ROUTE_PATH, EXPECTED_CORES["v87_route"])
    routes = route_matrix(v86, v87)
    geometry = v87["compact_resolution_globalization"]
    bisection = v87["period_two_bisection_candidate"]
    redesign = v87["B_neutral_orbifold_redesign"]
    stabilizer = v87["vacuum_stabilizer_audit"]["B_neutral_vacuum"]
    inflow = v87["diagonal_quotient_bundle_and_inflow"]
    decision = v87["terminal_decision"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {"V86_master": v86["core_sha256"], "V87_route": v87["core_sha256"]},
        "lineage": {
            "parent_master": "V86",
            "new_route": "B87",
            "parent_route_count": len(v86["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v86["route_matrix"]),
            "supersession_scope": v87["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": copy.deepcopy(v87["gate_ledger"]),
        "consolidated_theory_card": {
            "selected_branch_status": "ALGEBRAIC_CANDIDATE_FULL_SPACE_GROUP_NOT_CONSTRUCTED",
            "research_program_status": "OPEN_WITH_EXACT_V87_ADVANCES",
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "conditional_geometry_tuple": [8, 268, -520],
            "selected_hyper_charges": [2, 0, 2],
            "selected_light_Higgs_pair": ["H_uA", "H_dC"],
            "selected_vacuum_nongauge_component": "C2",
            "faithful_low_energy_C4_selector": False,
            "strongest_exact_geometry_result": "global projective crepant ambient blowups, compact flatness, formal Euler -520 and an explicit period/index-two bisection with non-split I2-star Jacobian",
            "strongest_exact_action_result": "the B-neutral charge ledger gives a matching four-stratum phase candidate, the required rank-one mass matrix and zero displayed ordinary C4 residues; the full Gammahat lift remains open",
            "strongest_exact_topology_result": "ordinary smooth GF bundles obey w2(V)=a^2 and support the nonzero order-two a*w4 character",
            "branch_correction": "the V86 qF(B)=2 anomaly remains correct for its rejected branch; the qF(B)=0 zero-mode shadow has coefficient zero, but the UV k2 coefficient awaits massive/fixed-wall eta data",
            "exact_gains": copy.deepcopy(v87["same_action_synthesis"]["exact_gains"]),
            "explicit_non_promotions": copy.deepcopy(v87["same_action_synthesis"]["hard_boundaries"]),
            "next_required_action": copy.deepcopy(v87["next_required_action"]),
        },
        "strict_master_decision": {
            "global_projective_crepant_ambient_constructed": decision["global_projective_crepant_ambient_constructed"],
            "compact_flatness_proved": decision["compact_flatness_proved"],
            "formal_Euler_characteristic": decision["formal_Euler_characteristic"],
            "compact_strict_transform_smooth_certified": decision["compact_strict_transform_smooth_certified"],
            "conditional_Hodge_numbers": geometry["formal_Chern_pushforward"]["conditional_Hodge"],
            "unconditional_Hodge_numbers": decision["unconditional_Hodge_numbers"],
            "period_two_bisection_and_Spin11_Jacobian_constructed": decision["period_two_bisection_and_Spin11_Jacobian_constructed"],
            "bisection_period_index": [bisection["period_index_proof"]["period"], bisection["period_index_proof"]["index"]],
            "resolved_bisection_j_squared_center_proved": decision["resolved_bisection_j_squared_center_proved"],
            "B_neutral_fixed_stratum_phase_candidate_passes": decision["B_neutral_fixed_stratum_phase_candidate_passes"],
            "B_neutral_full_space_group_projectors_restored": decision["B_neutral_full_space_group_projectors_restored"],
            "B_neutral_rank1_action_exact": decision["B_neutral_rank1_action_exact"],
            "selected_charge_pattern": [redesign["charge_redesign"][f"{name}_hyper_qF"] for name in ("A", "B", "C")],
            "selected_anomaly_tensor": copy.deepcopy(redesign["ordinary_zero_mode_anomaly"]["integer_tensor"]),
            "B_neutral_ordinary_C4_anomaly_residues_zero": decision["B_neutral_ordinary_C4_anomaly_residues_zero"],
            "zero_mode_shadow_requires_V86_k2": inflow["B_neutral_branch_relation"]["zero_mode_shadow_requires_V86_k2"],
            "UV_k2_counterterm_coefficient_determined": inflow["B_neutral_branch_relation"]["UV_k2_counterterm_coefficient_determined"],
            "charge4_GS_integer_factorization_screen_passes": decision["charge4_GS_integer_factorization_screen_passes"],
            "differential_GS_common_regulator_constructed": redesign["charge4_GS_Stueckelberg_screen"]["supersymmetric_differential_cocycle_and_common_regulator_constructed"],
            "ordinary_smooth_GF_bundle_and_aw4_character_constructed": decision["ordinary_smooth_GF_bundle_and_aw4_character_constructed"],
            "selected_aw4_coefficient": inflow["B_neutral_branch_relation"]["omega5_coefficient_required_by_displayed_zero_mode_shadow"],
            "residual_nongauge_component": stabilizer["surviving_nongauge_component"],
            "faithful_C4_low_energy_selector_survives": stabilizer["faithful_C4_low_energy_selector_survives"],
            "global_diagonal_bisection_Sp3_bundle_constructed": decision["global_diagonal_bisection_Sp3_bundle_constructed"],
            "full_stratified_HGamma_target_selected": decision["full_stratified_HGamma_target_selected"],
            "full_fixed_wall_Dai_Freed_trivialization_constructed": decision["full_fixed_wall_Dai_Freed_trivialization_constructed"],
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": decision["accepted_full_parent_action_exists"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "closed_gates": copy.deepcopy(decision["closed_gates"]),
            "theory_complete": decision["theory_complete"],
        },
        "supersession_ledger": {
            "V86_positive_lift_qF_B_equals_2_tensor_remains_correct": True,
            "V86_positive_lift_branch_selected": False,
            "V87_B_neutral_branch_selected_for_continuation": True,
            "V86_nonzero_SU2_residue_applies_to_selected_branch": False,
            "V86_k2_product_inflow_required_by_zero_mode_shadow": False,
            "UV_k2_coefficient_determined": False,
            "retaining_k2_without_matching_massive_or_defect_character_fails_zero_mode_probe": True,
            "bare_bisection_proves_copy_dependent_grading": False,
        },
        "fail_closed_logic": {
            "smooth_projective_ambient_is_not_smooth_hypersurface": True,
            "formal_Euler_is_not_unconditional_Hodge_certificate": True,
            "singular_period_two_bisection_is_not_resolved_center_relation": True,
            "ordinary_anomaly_residues_are_not_full_fixed_wall_Dai_Freed": True,
            "phase_level_projector_match_is_not_full_Gammahat_lift": True,
            "integer_GS_levels_are_not_differential_cocycle": True,
            "abstract_Sp3_diagonal_is_not_global_geometric_bundle": True,
            "residual_C2_is_not_faithful_C4_selector": True,
            "partial_scaffolds_are_not_same_action_completion": True,
            "accept_if_partial_scaffolds_only": False,
        },
        "open_obligations": copy.deepcopy(v87["open_obligations"]),
        "primary_sources": copy.deepcopy(v87["primary_sources"]),
        "source_manifest": copy.deepcopy(v87["source_manifest"]),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    if report["input_core_hashes"] != {"V86_master": EXPECTED_CORES["v86_master"], "V87_route": EXPECTED_CORES["v87_route"]}:
        raise RuntimeError("lineage mismatch")
    v86 = load_bound(V86_MASTER_PATH, EXPECTED_CORES["v86_master"])
    if canonical_sha(report["route_matrix"][:-1]) != canonical_sha(v86["route_matrix"]):
        raise RuntimeError("inherited V86 route matrix changed")
    last = report["route_matrix"][-1]
    if last["route_id"] != "B87" or last["accepted"] or last["same_action_microscopic_completion"]:
        raise RuntimeError("B87 route falsely accepted or malformed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(range(1, len(report["route_matrix"]) + 1)):
        raise RuntimeError("route ordinals changed")
    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    exact = {
        "A4": "PASS_EXACT", "A5": "PASS_EXACT_EULER_MINUS520", "A6": "OPEN_UNCOMPUTED",
        "A8": "PASS_EXACT_2_2", "A12": "PASS_EXACT_2_0_2", "A13": "PASS_EXACT_PHASE_TABLE_ONLY",
        "A13B": "OPEN_UNCONSTRUCTED", "A16": "PASS_EXACT_ZERO",
        "A17": "SUPERSEDED_BRANCH_CORRECT_NOT_SELECTED", "A18": "NOT_REQUIRED_BY_ZERO_MODE_SHADOW",
        "A18B": "OPEN_UNDETERMINED",
        "A20": "OPEN_UNCONSTRUCTED", "A23": "PASS_EXACT_RESIDUAL_C2",
        "A24": "REJECTED_ABSENT_ON_SELECTED_VACUUM", "A26": "OPEN_UNFORMULATED",
        "A29": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in exact.items()):
        raise RuntimeError("acceptance criterion changed")
    decision = report["strict_master_decision"]
    if not decision["global_projective_crepant_ambient_constructed"] or not decision["compact_flatness_proved"]:
        raise RuntimeError("exact compact ambient or flatness result lost")
    if decision["formal_Euler_characteristic"] != -520 or decision["conditional_Hodge_numbers"] != [8, 268]:
        raise RuntimeError("formal compact invariants changed")
    if decision["compact_strict_transform_smooth_certified"] or decision["unconditional_Hodge_numbers"]:
        raise RuntimeError("compact smoothness falsely promoted")
    if not decision["period_two_bisection_and_Spin11_Jacobian_constructed"] or decision["bisection_period_index"] != [2, 2]:
        raise RuntimeError("period-two geometry changed")
    if decision["resolved_bisection_j_squared_center_proved"]:
        raise RuntimeError("resolved bisection relation falsely promoted")
    if decision["selected_charge_pattern"] != [2, 0, 2] or not decision["B_neutral_fixed_stratum_phase_candidate_passes"]:
        raise RuntimeError("B-neutral action changed")
    if decision["B_neutral_full_space_group_projectors_restored"] or not decision["B_neutral_rank1_action_exact"]:
        raise RuntimeError("B-neutral projector/rank boundary changed")
    expected_tensor = {"A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672, "TrF": 64, "TrF_cubed": 112, "F_squared_Y6": 0, "F_squared_X": 0, "FY6X": 48}
    if decision["selected_anomaly_tensor"] != expected_tensor or not decision["B_neutral_ordinary_C4_anomaly_residues_zero"]:
        raise RuntimeError("B-neutral anomaly result changed")
    if decision["zero_mode_shadow_requires_V86_k2"] or decision["selected_aw4_coefficient"] != 0:
        raise RuntimeError("zero-mode inflow coefficient changed")
    if decision["UV_k2_counterterm_coefficient_determined"]:
        raise RuntimeError("zero-mode shadow falsely promoted to UV k2 result")
    if decision["differential_GS_common_regulator_constructed"]:
        raise RuntimeError("GS screen falsely promoted")
    if decision["residual_nongauge_component"] != "C2" or decision["faithful_C4_low_energy_selector_survives"]:
        raise RuntimeError("vacuum stabilizer changed")
    forbidden = [
        "B_neutral_full_space_group_projectors_restored", "global_diagonal_bisection_Sp3_bundle_constructed", "full_stratified_HGamma_target_selected",
        "full_fixed_wall_Dai_Freed_trivialization_constructed", "same_action_microscopic_completion_found",
        "accepted_full_parent_action_exists", "theory_complete",
    ]
    if any(decision[key] for key in forbidden) or decision["accepted_extension_count"] or decision["closed_gates"]:
        raise RuntimeError("same-action boundary falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)} or not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate identity or state changed")
    supersession = report["supersession_ledger"]
    if supersession["V86_positive_lift_branch_selected"] or supersession["V86_k2_product_inflow_required_by_zero_mode_shadow"]:
        raise RuntimeError("superseded V86 branch was reactivated")
    if supersession["UV_k2_coefficient_determined"]:
        raise RuntimeError("UV k2 coefficient falsely determined")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    criteria = "".join(f"- {row['id']}: {row['status']} — {row['requirement']}\n" for row in report["acceptance_criteria"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    return f"""# V87 multipath G1 frontier master audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Master decision

V87 is a substantive repair, but not a completed theory. The compact model now has globally defined projective crepant ambient blowups, exact flatness and formal Euler `{decision['formal_Euler_characteristic']}`. Hodge `{decision['conditional_Hodge_numbers']}` remains conditional until one explicit compact member passes the Cox Jacobian saturation.

The explicit genus-one fibration has period/index `{decision['bisection_period_index']}` and a non-split `I2*` Jacobian. Its crepant resolution, component intersections and geometric `j^2=z` relation are not yet proved.

The candidate branch has `qF(A,B,C)={decision['selected_charge_pattern']}`. It matches the four displayed fixed-stratum phases and gives the rank-one Higgs mass matrix, but the full `Gammahat` lift and quotient kernel are not constructed, so the charged-hyper projectors are not certified restored. Its displayed ordinary anomaly tensor is `{decision['selected_anomaly_tensor']}` with zero mod-four residues. The zero-mode shadow does not require the old V86 `k=2` inflow; the UV coefficient remains undetermined until the massive/fixed-wall eta character is computed.

The vacuum retains only `{decision['residual_nongauge_component']}`, acting trivially on the light families/Higgs pair, not a faithful low-energy C4 selector. Full stratified Dai--Freed data and a global bisection/Sp3 diagonal bundle remain absent.

No route is accepted, no gate is closed, and the theory is not complete.

## Acceptance ledger

{criteria}
## Gates

{gates}
## Open obligations

{obligations}"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated JSON is stale")
        if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated Markdown is stale")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
