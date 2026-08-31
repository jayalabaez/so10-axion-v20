#!/usr/bin/env python3
"""V78 fail-closed master card for the torsion-character redesign.

The master binds the frozen V77 master and the new V78 route.  V78 is the
first route in this sequence to construct one global space-group torsion class
that repairs all ordinary isotropy divisibility failures, and it identifies a
unique canonical-vacuum tadpole-free refinement.  It also supplies the missing
common-stratum bosonic bridge and classifies the changed Spin(11) parents.

These exact structural passes do not close G1: no full supersymmetric parent
anomaly line has been trivialized on the H78 cap/bordism category.  The current
action remains rejected and all eight gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V77_MASTER_PATH = ROOT / "SUSY_V77_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V78_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V78_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v78_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v77_master": "abe7657d134a389f79e601434ff3a6ba4eb21f9041d0199ad604c907007e8517",
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
}

SCHEMA = "susy_v78_multipath_g1_frontier_master_audit_v1"
VERSION = "V78"
DATE = "2026-08-31"
STATUS = (
    "V78_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V77_MASTER_AND_V78_ROUTE_CORES_"
    "BOUND__ORDINARY_ISOTROPY_DIVISIBILITY_OBSTRUCTION_REPAIRED_EXACT__"
    "UNIQUE_CANONICAL_VACUUM_TADPOLE_FREE_H78_REFINEMENT_SELECTED__SMOOTH_"
    "I8_UNCHANGED__LEVEL_ONE_BOSONIC_BRIDGE_EXACT__INTEGRATED_PARENT_FAMILY_"
    "AND_EVEN_HALF32_SPACE_GROUP_REPRESENTATION_EXACT__WCS_DAI_FREED_CAP_"
    "BRST_CURVED_SUPERSYMMETRY_AND_CHANGED_PARENT_PROJECTORS_OPEN__CURRENT_"
    "ACTION_REJECTED__G1_TO_G8_OPEN"
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
    embedded = value.get("core_sha256")
    recomputed = canonical_sha(value)
    if embedded != recomputed:
        raise RuntimeError(
            f"noncanonical parent core for {path.name}: {embedded} != {recomputed}"
        )
    if embedded != expected:
        raise RuntimeError(
            f"bound core mismatch for {path.name}: {embedded} != {expected}"
        )
    return value


def route_matrix(v77: Mapping[str, Any], v78: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v77["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B78",
            "name": "space-group torsion characteristic, common-stratum bridge and changed-parent redesign",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v78["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V77 master and V78 route canonical lineage", "PASS_EXACT"),
        ("A2", "global Z4 x Z2 space-group torsion ring and restriction maps", "PASS_EXACT"),
        ("A3", "ordinary V77 GS isotropy divisibility obstruction", "PASS_REPAIRED"),
        ("A4", "globally divisible torsion correction classification", "PASS_FOUR_ROWS"),
        ("A5", "unique canonical-vacuum zero-internal-Y correction", "PASS_EXACT"),
        ("A6", "H78 Spin-c characteristic integrality", "PASS_ON_DEFINED_CATEGORY"),
        ("A7", "flat correction preserves smooth de Rham I8", "PASS_EXACT"),
        ("A8", "curved SU2R promotion of flat r2", "REJECTED_INCOMPLETE_FACTORIZATION"),
        ("A9", "level-one bosonic common-stratum bridge", "PASS_EXACT"),
        ("A10", "curved off-shell supersymmetric bridge", "OPEN_UNCONSTRUCTED"),
        ("A11", "all integrated one-tensor Spin11 parents", "PASS_CLASSIFIED"),
        ("A12", "even half-32 full space-group flavor representation", "PASS_EXACT"),
        ("A13", "changed-parent family/rank projectors and local indices", "OPEN_UNCOMPUTED"),
        ("A14", "F71 singlet spectator field-count minimality", "PASS_7_AND_8"),
        ("A15", "F71 full multiplet, invariant mass and relic completion", "REJECTED"),
        ("A16", "bare-parent eta phase selects V78 torsion refinement", "OPEN_UNCOMPUTED"),
        ("A17", "shifted WuCS quadratic refinement and seven-bordism holonomy", "OPEN_UNCONSTRUCTED"),
        ("A18", "caps, junctions and BV/BRST field descent", "OPEN_UNCONSTRUCTED"),
        ("A19", "bare x WuCS x bridge x cap anomaly-line identity", "SELECTED_OPEN"),
        ("A20", "same-action microscopic completion", "OPEN_FAILED"),
        ("A21", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [
        {"id": key, "requirement": requirement, "status": status}
        for key, requirement, status in rows
    ]


def build_report() -> dict[str, Any]:
    v77 = load_bound(V77_MASTER_PATH, EXPECTED_CORES["v77_master"])
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    routes = route_matrix(v77, v78)
    criteria = acceptance_criteria()
    decision = v78["terminal_decision"]
    torsion = v78["space_group_torsion_audit"]
    combined = v78["combined_H78_characteristic_audit"]
    parents = v78["integrated_parent_family_audit"]
    bridge = v78["common_stratum_bridge_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V77_master": v77["core_sha256"],
            "V77_route_via_V78_lineage": v78["lineage"]["V77_route_core"],
            "V78_route": v78["core_sha256"],
        },
        "lineage": {
            "parent_master": "V77",
            "new_route": "B78",
            "parent_route_count": len(v77["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v77["route_matrix"]),
            "supersession_scope": v78["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": criteria,
        "gate_ledger": v78["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "accepted_extension_count": 0,
            "selected_open_candidates": v78["candidate_adjudication"]["selected_ids"],
            "strongest_action_scaffold": (
                "frozen h=0 Spin11 parent + H78 tadpole-free differential GS "
                "candidate + level-one common-stratum bridge + future cap/curved-SUSY completion"
            ),
            "exact_gains": [
                "H^4(B(Z4 x Z2);Z)=Z4{r^2}+Z2{rs}+Z2{s^2} and all three stabilizer restrictions",
                f"four globally divisible corrections; unique zero-internal-Y choice {torsion['selected_tadpole_free_repair']['delta']}",
                "manifest H78 integral class Y1=qT+r^2+s^2-p1(E), Y2=qTE+r^2+s^2",
                f"canonical flat-product reduction {combined['canonical_flat_product']['selected_Y_reduces_to']}",
                "flat torsion correction has zero de Rham curvature and preserves the V69 smooth factorization",
                f"integer level {bridge['selected_level']} differential bridge with boundary curvature {bridge['selected_boundary_anomaly_polynomial']}",
                "complete h=0,...,9 integrated Spin11 parent family and exact odd-h exclusion",
                "orthogonal two-flavor block representing the full space group for every even half-32 multiplicity",
                "all-odd-normal-lift Z16 theorem: F71 requires at least seven z00 and eight z11 singlet fields",
            ],
            "retired_shortcuts": [
                "declaring the V77 divisibility obstruction terminal without using the existing space-group characters",
                "using three unrelated fixed-point counterterms instead of one global quotient-stack class",
                "promoting flat r^2 to curved p1(SU2R) without refactorizing the full R anomaly polynomial",
                "claiming that even half-32 multiplicity still lacks any space-group representation",
                "assuming larger odd normal charges can reduce the F71 spectator count",
                "calling the exact bosonic bridge a completed curved supersymmetric sector",
            ],
            "remaining_global_blockers": v78["action_redesign"]["obstructions_not_removed"],
        },
        "strict_master_decision": {
            "ordinary_V77_isotropy_divisibility_repaired": decision["ordinary_V77_GS_isotropy_obstruction_repaired"],
            "selected_delta_twice_Y": torsion["selected_tadpole_free_repair"]["delta"],
            "selected_delta_unique_tadpole_free": torsion["selected_tadpole_free_repair"]["unique_among_global_divisible_delta_pairs"],
            "selected_H78_class_integral": decision["selected_class_integral_on_defined_H78_backgrounds"],
            "selected_H78_class_preserves_smooth_I8": decision["selected_class_same_smooth_de_Rham_factorization"],
            "canonical_flat_vacuum_internal_Y": combined["canonical_flat_product"]["pure_internal_Y"],
            "bare_eta_selects_discrete_refinement": decision["torsion_refinement_matched_to_bare_parent_eta_phase"],
            "level_one_bosonic_bridge_constructed": decision["level_one_bosonic_bridge_constructed"],
            "supersymmetric_curved_bridge_constructed": decision["supersymmetric_curved_bridge_constructed"],
            "integrated_parent_row_count": len(parents["rows"]),
            "parity_allowed_changed_parent_rows": parents["even_h_open_rows"],
            "even_half32_space_group_representation_constructed": decision["even_half32_space_group_field_representation_constructed"],
            "changed_parent_three_family_projector_constructed": decision["changed_parent_three_family_projector_constructed"],
            "shifted_WCS_Dai_Freed_cap_identity_proved": decision["shifted_WCS_Dai_Freed_cap_identity_proved"],
            "same_action_microscopic_completion_found": decision["accepted_full_parent_action_exists"],
            "selected_candidate_accepted": decision["selected_candidate_accepted"],
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "closed_gates": decision["closed_gates"],
            "complete_theory": decision["theory_complete"],
            "honest_outcome": decision["honest_outcome"],
        },
        "next_required_action": {
            "id": "F79_H78_ANOMALY_LINE_HOLONOMY_AND_CAP_COMPLETION",
            "objective": (
                "compute the h=0 equivariant Dai--Freed eta phase, test the V78 "
                "tadpole-free discrete refinement, construct shifted U-WuCS and cap "
                "states, and prove or falsify their gluing identity with the level-one bridge"
            ),
            "fallback_if_falsified": (
                "use the explicit even-half32 flavor representation to compute the full "
                "h=4 changed-parent projector and fixed-point anomaly ledger"
            ),
            "accepted": False,
        },
        "regression_scope": {
            "inherited_V77_scope_sha256": canonical_sha(v77["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v78_torsion_character_parent_redesign_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v78["source_manifest"],
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    card = report["consolidated_theory_card"]
    decision = report["strict_master_decision"]
    gains = "".join(f"- {item}\n" for item in card["exact_gains"])
    retired = "".join(f"- {item}\n" for item in card["retired_shortcuts"])
    blockers = "".join(f"- {item}\n" for item in card["remaining_global_blockers"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V78 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action is **{card['current_action_status']}**, while the research
program is `{card['research_program_status']}`.  V78 exactly repairs V77's
ordinary isotropy divisibility obstruction with one global space-group class.
The selected correction to twice the characteristic vector is
`{decision['selected_delta_twice_Y']}` and is the unique globally divisible
choice that permits zero internal `Y` on the canonical flat vacuum.

This is not G1 closure.  The bare eta invariant has not selected the discrete
refinement, the shifted Wu--Chern--Simons/cap holonomy identity is unproved,
and the exact bosonic `-nu A B` bridge has no curved off-shell supersymmetric
completion.  The changed half-spinor parents have an exact space-group flavor
representation but no family/rank projector or fixed-point index ledger.

## Exact gains

{gains}
## Retired shortcuts

{retired}
## Remaining global blockers

{blockers}
## Next required action

`{report['next_required_action']['id']}`: {report['next_required_action']['objective']}

## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V78 master core is not canonical")
    if report["input_core_hashes"]["V77_master"] != EXPECTED_CORES["v77_master"]:
        raise RuntimeError("V77 master lineage mismatch")
    if report["input_core_hashes"]["V78_route"] != EXPECTED_CORES["v78_route"]:
        raise RuntimeError("V78 route lineage mismatch")
    decision = report["strict_master_decision"]
    if not decision["ordinary_V77_isotropy_divisibility_repaired"]:
        raise RuntimeError("V78 exact arithmetic pass was lost")
    if decision["selected_delta_twice_Y"] != ["r^2", "2r^2+s^2"]:
        raise RuntimeError("wrong selected torsion correction")
    if not decision["selected_delta_unique_tadpole_free"]:
        raise RuntimeError("selected correction is not uniquely tadpole-free")
    if decision["canonical_flat_vacuum_internal_Y"] != ["0", "0"]:
        raise RuntimeError("canonical flat-vacuum tadpole returned")
    if decision["bare_eta_selects_discrete_refinement"]:
        raise RuntimeError("uncomputed eta selection was promoted")
    if decision["supersymmetric_curved_bridge_constructed"]:
        raise RuntimeError("bosonic bridge was overpromoted")
    if decision["changed_parent_three_family_projector_constructed"]:
        raise RuntimeError("uncomputed changed-parent projector was promoted")
    if decision["shifted_WCS_Dai_Freed_cap_identity_proved"]:
        raise RuntimeError("unproved anomaly-line identity was promoted")
    if decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("same-action completion was overclaimed")
    if decision["selected_candidate_accepted"]:
        raise RuntimeError("selected structural candidate was accepted")
    if decision["closed_gates"] or decision["complete_theory"]:
        raise RuntimeError("a G gate or theory was closed")
    if not all(value.startswith("OPEN") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
