#!/usr/bin/env python3
"""V86 multipath G1 frontier master audit.

This master binds V85 and the V86 Hodge/C4F/AHSS route, records every exact
advance and retraction, and enforces the remaining same-action boundary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V85_MASTER_PATH = ROOT / "SUSY_V85_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V86_ROUTE_PATH = ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V86_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V86_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v86_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v85_master": "0d4af6a5ac684e2494860733875e517c3bbabd4be38c486c3399db6be9188536",
    "v86_route": "799af690205811d97df663ab53dab639c79262a6aac60a37da4394b961a691ad",
}

SCHEMA = "susy_v86_multipath_g1_frontier_master_audit_v1"
VERSION = "V86"
DATE = "2026-09-01"
STATUS = (
    "V86_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V85_MASTER_AND_V86_ROUTE_CORES_BOUND__"
    "V85_HODGE_PREDICTION_RETRACTED__CONDITIONAL_HODGE_8_268_EULER_MINUS520__"
    "CREPANT_FIVE_BLOWUP_TEMPLATE_EXACT_GLOBAL_COMPACT_CERTIFICATION_OPEN__"
    "FOUR_SECTION_WITH_J2_CENTER_TARGET_RETRACTED__BISECTION_WITH_ORDER4_LIFT_REQUIRED__"
    "C4F_SU2_ANOMALY_GENUINE__GAPPED_AND_ONE_AXION_EXACT_C4_REPAIRS_EXCLUDED__"
    "ORDER2_PRODUCT_INFLOW_TARGET_CONDITIONAL__FULL_DIAGONAL_DAIFREED_OPEN__"
    "SCOPED_AHSS_D3_D4_ZERO_REDUCED_Z4_QHAT_DELTA_ZERO__FULL_HGAMMA_OPEN__"
    "NO_ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def route_matrix(v85: Mapping[str, Any], v86: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = copy.deepcopy(v85["route_matrix"])
    rows.append({
        "ordinal": len(rows) + 1,
        "route_id": "B86",
        "name": "Hodge correction, bisection target, C4F anomaly no-go and scoped AHSS closure",
        "same_action_microscopic_completion": False,
        "accepted": False,
        "selected_open_candidates": copy.deepcopy(v86["candidate_adjudication"]["selected_ids"]),
    })
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    raw = [
        ("A1", "V85 master and V86 route canonical lineage", "PASS_EXACT"),
        ("A2", "V85 Hodge prediction 8,265,-514", "RETRACTED_FALSE"),
        ("A3", "Grassi-Morrison branch and monodromy arithmetic", "PASS_EXACT_B1_8_B2_0_GPRIME3_R_MINUS20"),
        ("A4", "conditional Euler and Hodge invariants", "PASS_EXACT_IF_SMOOTH_PROJECTIVE_CREPANT_8_268_MINUS520"),
        ("A5", "independent six-dimensional gravitational ledgers", "PASS_EXACT_BOTH_273"),
        ("A6", "published Spin11 five-blowup discrepancies", "PASS_EXACT_ALL_ZERO"),
        ("A7", "global Cox saturation, smooth centers and flatness", "OPEN_UNCOMPUTED"),
        ("A8", "compact projective crepant resolution certificate", "OPEN_UNCONSTRUCTED"),
        ("A9", "old four-section with j squared equals center target", "RETRACTED_CHARGE_NORMALIZATION_MISMATCH"),
        ("A10", "corrected bisection with order-four lifted generator", "OPEN_UNCONSTRUCTED"),
        ("A11", "abstract continuous U1F quotient and j squared equals center", "PASS_EXACT_GROUP_ALGEBRA"),
        ("A12", "resolved Shioda/fibral intersection realization", "OPEN_UNCONSTRUCTED"),
        ("A13", "global B0 diagonal VEV stabilizer", "OPEN_UNPROVED"),
        ("A14", "positive-lift C4F anomaly tensor", "PASS_EXACT_12_18_468_688_70_136_24_16_72"),
        ("A15", "SU2 squared C4F mixed residue", "REJECTED_NONZERO_2_MOD4"),
        ("A16", "ordinary full-rank C4-preserving massive matter repair", "REJECTED_EXACT_NO_GO"),
        ("A17", "one-axion integer GS repair retaining exact C4", "REJECTED_EXACT_DIVISIBILITY_NO_GO"),
        ("A18", "order-two five-dimensional product-background inflow target", "PASS_EXACT_CONDITIONAL"),
        ("A19", "full diagonal quotient fixed-wall Dai-Freed trivialization", "OPEN_UNCONSTRUCTED"),
        ("A20", "explicit doublet anomaly repair", "PASS_EXACT_Z2_ENDPOINT_ONLY"),
        ("A21", "incomplete-GUT/fixed-stratum origin for doublet repair", "OPEN_UNCONSTRUCTED"),
        ("A22", "Hashimoto ku3(BZ4)", "PASS_EXACT_Z8_PLUS_Z2"),
        ("A23", "scoped AHSS d3", "PASS_EXACT_ZERO"),
        ("A24", "scoped AHSS d4", "PASS_EXACT_ZERO"),
        ("A25", "scoped reduced bordism and hidden extension", "PASS_EXACT_NON_SPLIT_Z4"),
        ("A26", "V82 qhat displacement in scoped smooth target", "PASS_EXACT_DELTA_ZERO"),
        ("A27", "total scoped group including basepoint", "PASS_EXACT_Z4_PLUS_Z4"),
        ("A28", "full HGamma target with internal C4F, BC2, strata and defects", "OPEN_UNFORMULATED"),
        ("A29", "common BV/regulator/Pfaffian and differential WCS glue", "OPEN_UNCONSTRUCTED"),
        ("A30", "F+S junction and entangled Q4-relative source", "OPEN_UNCONSTRUCTED"),
        ("A31", "same-action microscopic completion", "REJECTED_NOT_FOUND"),
        ("A32", "vacuum, soft spectrum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in raw]


def build_report() -> dict[str, Any]:
    v85 = load_bound(V85_MASTER_PATH, EXPECTED_CORES["v85_master"])
    v86 = load_bound(V86_ROUTE_PATH, EXPECTED_CORES["v86_route"])
    routes = route_matrix(v85, v86)
    route_decision = v86["terminal_decision"]
    geometry = v86["V85_Hodge_retraction_and_Grassi_Morrison_correction"]
    frontier = v86["resolution_and_multisection_frontier"]
    ahss = v86["AHSS_d3_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {"V85_master": v85["core_sha256"], "V86_route": v86["core_sha256"]},
        "lineage": {
            "parent_master": "V85",
            "new_route": "B86",
            "parent_route_count": len(v85["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v85["route_matrix"]),
            "supersession_scope": v86["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": copy.deepcopy(v86["gate_ledger"]),
        "consolidated_theory_card": {
            "current_action_status": route_decision["current_action_status"],
            "research_program_status": route_decision["research_program_status"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "conditional_geometry_tuple": [8, 268, -520],
            "corrected_geometric_target": frontier["charge_lattice_target_correction"]["corrected_obligation"],
            "strongest_exact_topology_result": "scoped reduced Omega7=Z4, d3=d4=0, non-split extension and qhat delta=0",
            "strongest_quantum_obstruction": "SU2 squared C4F residue 2 mod4 cannot be repaired by ordinary gapped matter or one integer axion while retaining exact C4",
            "strongest_conditional_repair": "order-two five-dimensional inflow on liftable product backgrounds",
            "exact_gains": [
                "V85's Hodge prediction is retracted and replaced by the conditional Grassi-Morrison tuple (8,268,-520)",
                "a published five-blowup projective crepant template specializes to the local Spin11 model",
                "charge normalization replaces the inconsistent four-section target by a bisection with order-four lift",
                "the full positive-lift C4F anomaly tensor and genuine SU2 residue are exact",
                "ordinary gapped matter and one-axion exact-C4 repairs are excluded",
                "the scoped AHSS d3 and d4 vanish, the hidden extension is Z4 and V82 delta is zero",
            ],
            "explicit_non_promotions": [
                "the blowup template is not a global compact saturation/flatness certificate",
                "the corrected bisection and resolved center intersection are not constructed",
                "the product-background inflow is not a full diagonal Dai-Freed trivialization",
                "the scoped Spin-Z8 result does not include the separate internal C4F or full HGamma data",
                "the Z2 doublet endpoint is not an exact-C4 parent",
            ],
            "next_required_action": copy.deepcopy(v86["next_required_action"]),
        },
        "strict_master_decision": {
            "V85_Hodge_prediction_retracted": route_decision["V85_Hodge_prediction_retracted"],
            "conditional_Hodge_numbers_and_Euler": route_decision["conditional_Hodge_numbers_and_Euler"],
            "published_crepant_blowup_template_specialized": route_decision["published_crepant_blowup_template_specialized"],
            "projective_crepant_resolution_constructed": route_decision["projective_crepant_resolution_constructed"],
            "V85_four_section_with_j_squared_z_target_retracted": route_decision["V85_four_section_with_j_squared_z_target_retracted"],
            "corrected_bisection_target_constructed": route_decision["corrected_bisection_target_constructed"],
            "C4F_SU2_squared_residue_mod4": route_decision["C4F_SU2_squared_residue_mod4"],
            "C4_preserving_gapped_matter_repair_excluded": route_decision["C4_preserving_gapped_matter_repair_excluded"],
            "C4_preserving_one_axion_repair_excluded": route_decision["C4_preserving_one_axion_repair_excluded"],
            "product_background_inflow_target_constructed": route_decision["product_background_inflow_target_constructed"],
            "full_diagonal_anomaly_trivialization_constructed": route_decision["full_diagonal_anomaly_trivialization_constructed"],
            "scoped_AHSS_d3": ahss["d3_value"],
            "scoped_AHSS_d4": ahss["d4"]["value"],
            "scoped_reduced_bordism": "Z4",
            "scoped_total_bordism": ahss["lambda_seven_equivalence"]["total_group"],
            "scoped_hidden_extension": ahss["hidden_extension"],
            "scoped_qhat_delta": ahss["qhat_delta"]["delta_value"],
            "full_HGamma_C4F_target_computed": route_decision["full_HGamma_C4F_target_computed"],
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": route_decision["accepted_full_parent_action_exists"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "closed_gates": copy.deepcopy(route_decision["closed_gates"]),
            "theory_complete": route_decision["theory_complete"],
        },
        "fail_closed_logic": {
            "conditional_Hodge_theorem_is_not_resolution_construction": True,
            "crepant_local_template_is_not_global_compact_certificate": True,
            "abstract_j_squared_center_is_not_resolved_bisection": True,
            "product_background_inflow_is_not_full_diagonal_trivialization": True,
            "scoped_Spin_Z8_bordism_is_not_full_HGamma_C4F_bordism": True,
            "Z2_endpoint_is_not_exact_C4": True,
            "accept_if_partial_scaffolds_only": False,
        },
        "open_obligations": copy.deepcopy(v86["open_obligations"]),
        "primary_sources": copy.deepcopy(v86["primary_sources"]),
        "source_manifest": copy.deepcopy(v86["source_manifest"]),
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
    if report["input_core_hashes"] != {"V85_master": EXPECTED_CORES["v85_master"], "V86_route": EXPECTED_CORES["v86_route"]}:
        raise RuntimeError("lineage mismatch")
    v85 = load_bound(V85_MASTER_PATH, EXPECTED_CORES["v85_master"])
    if canonical_sha(report["route_matrix"][:-1]) != canonical_sha(v85["route_matrix"]):
        raise RuntimeError("inherited V85 route matrix changed")
    last = report["route_matrix"][-1]
    if last["route_id"] != "B86" or last["accepted"] or last["same_action_microscopic_completion"]:
        raise RuntimeError("B86 route falsely accepted or malformed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(range(1, len(report["route_matrix"]) + 1)):
        raise RuntimeError("route ordinals changed")
    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    exact = {
        "A2": "RETRACTED_FALSE",
        "A4": "PASS_EXACT_IF_SMOOTH_PROJECTIVE_CREPANT_8_268_MINUS520",
        "A8": "OPEN_UNCONSTRUCTED",
        "A9": "RETRACTED_CHARGE_NORMALIZATION_MISMATCH",
        "A15": "REJECTED_NONZERO_2_MOD4",
        "A16": "REJECTED_EXACT_NO_GO",
        "A17": "REJECTED_EXACT_DIVISIBILITY_NO_GO",
        "A23": "PASS_EXACT_ZERO",
        "A24": "PASS_EXACT_ZERO",
        "A25": "PASS_EXACT_NON_SPLIT_Z4",
        "A26": "PASS_EXACT_DELTA_ZERO",
        "A28": "OPEN_UNFORMULATED",
        "A31": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in exact.items()):
        raise RuntimeError("acceptance criterion changed")
    decision = report["strict_master_decision"]
    if decision["conditional_Hodge_numbers_and_Euler"] != [8, 268, -520]:
        raise RuntimeError("Hodge correction mismatch")
    if decision["projective_crepant_resolution_constructed"] or decision["corrected_bisection_target_constructed"]:
        raise RuntimeError("geometry falsely promoted")
    if decision["C4F_SU2_squared_residue_mod4"] != 2:
        raise RuntimeError("C4F anomaly residue mismatch")
    if not decision["C4_preserving_gapped_matter_repair_excluded"] or not decision["C4_preserving_one_axion_repair_excluded"]:
        raise RuntimeError("C4 repair no-go changed")
    if decision["full_diagonal_anomaly_trivialization_constructed"]:
        raise RuntimeError("conditional inflow falsely promoted")
    if decision["scoped_AHSS_d3"] != "ZERO" or decision["scoped_AHSS_d4"] != [0, 0]:
        raise RuntimeError("scoped AHSS differential mismatch")
    if (decision["scoped_reduced_bordism"], decision["scoped_total_bordism"], decision["scoped_qhat_delta"]) != ("Z4", "Z4 direct_sum Z4", "ZERO"):
        raise RuntimeError("scoped bordism or qhat delta mismatch")
    if decision["full_HGamma_C4F_target_computed"]:
        raise RuntimeError("scoped bordism falsely promoted")
    if decision["same_action_microscopic_completion_found"] or decision["accepted_full_parent_action_exists"] or decision["accepted_extension_count"]:
        raise RuntimeError("same-action parent falsely promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("theory falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)} or not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate identity or state changed")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    criteria = "".join(f"- {row['id']}: {row['status']} — {row['requirement']}\n" for row in report["acceptance_criteria"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    return f"""# V86 multipath G1 frontier master audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Master decision

V85's Hodge prediction is retracted. The corrected tuple is conditionally `{decision['conditional_Hodge_numbers_and_Euler']}`. A five-blowup crepant template exists, but the compact resolution is not certified. Charge normalization also retracts the four-section-with-`j^2=z` target in favor of a bisection with an order-four lifted generator.

The C4F `SU2^2` residue is `{decision['C4F_SU2_squared_residue_mod4']} mod 4`. Ordinary gapped matter and a one-axion repair cannot cancel it while retaining exact C4. The order-two product-background inflow is a target, not a full diagonal Dai--Freed construction.

Within the explicitly scoped smooth Spin-Z8/BSpin11 theory, `d3=0`, `d4={decision['scoped_AHSS_d4']}`, reduced bordism is `{decision['scoped_reduced_bordism']}`, total bordism is `{decision['scoped_total_bordism']}`, and the V82 qhat displacement is `{decision['scoped_qhat_delta']}`. The independent C4F/full-HGamma problem remains open.

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
