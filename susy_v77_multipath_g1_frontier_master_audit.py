#!/usr/bin/env python3
"""V77 fail-closed master card for the parent anomaly-line frontier.

The master binds the frozen V76 master and the V77 route audit.  It records
that a scalar parent determinant is the wrong object, that the ordinary smooth
Green--Schwarz characteristic class has no integral restriction to any current
orbifold isotropy stratum, and that the standard induced raw-character branch
contains additional SU(2)_R-dependent curvature.  The selected frontier is a
combined-H anomaly-line/Wu--Chern--Simons/cap trivialization, not an accepted
completion.  No G gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V76_MASTER_PATH = ROOT / "SUSY_V76_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V77_ROUTE_PATH = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V77_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V77_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v77_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v76_master": "202b5c000d2a540179419980f3daac4896fe340670787933cebd8d27943c5247",
    "v77_route": "fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb",
}

SCHEMA = "susy_v77_multipath_g1_frontier_master_audit_v1"
VERSION = "V77"
DATE = "2026-08-31"
STATUS = (
    "V77_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V76_MASTER_AND_V77_ROUTE_CORES_"
    "BOUND__SCALAR_PARENT_DETERMINANT_REJECTED_AS_CATEGORY_ERROR__TEN_NEUTRAL_"
    "ZERO_MODES_EXACT__NAIVE_SMOOTH_GS_CLASS_ORDINARY_ORBIFOLD_RESTRICTION_REJECTED_EXACT__"
    "UNCHANGED_TENSOR_LATTICE_TWIST_FORCED_IDENTITY__V70_AND_F71_ACTION_"
    "SCENARIOS_SEPARATED__CONDITIONAL_SU2R_FIXED_INDEX_DENSITIES_NONZERO__"
    "COMBINED_H_ANOMALY_LINE_TRIVIALIZATION_SELECTED_"
    "OPEN__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def route_summary(v76: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(v76["route_matrix"], start=1):
        rows.append(
            {
                "ordinal": index,
                "route_id": row.get("route_id", row.get("id", f"legacy_{index}")),
                "name": row.get("name", row.get("kind", "inherited route")),
                "same_action_microscopic_completion": bool(
                    row.get("same_action_microscopic_completion", False)
                ),
                "accepted": bool(row.get("accepted", False)),
            }
        )
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B77",
            "name": "equivariant parent anomaly-line and ordinary GS-cocycle audit",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidate": (
                "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
            ),
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V76 master and V77 route canonical lineage", "PASS_EXACT"),
        ("A2", "square-torus space-group abelianization and eight flat characters", "PASS_EXACT_DIAGNOSTIC"),
        ("A3", "V71 standard equal-corner parent residue", "PASS_REPRODUCED"),
        ("A4", "unprimed internal KK product at zero external momentum", "REJECTED_TEN_ZERO_MODES"),
        ("A5", "scalar determinant as absolute parent quantum object", "REJECTED_CATEGORY_ERROR"),
        ("A6", "raw field-by-field BRST/BV and global-H input contract", "OPEN_MISSING"),
        ("A7", "unchanged tensor-lattice twist fixing a and b", "REJECTED_IDENTITY_ONLY"),
        ("A8", "ordinary smooth GS class on all orbifold isotropy strata", "REJECTED_DIVISIBILITY"),
        ("A9", "standard-branch Z2 SU2R equivariant index density", "PASS_CONDITIONAL_LOCAL"),
        ("A10", "standard-branch Z4 restricted bulk index cross-check", "PASS_CONDITIONAL_LOCAL"),
        ("A11", "combined Spin-SU2R-Sp266-Spin11 H_Gamma orbibundle", "OPEN_UNCONSTRUCTED"),
        ("A12", "generalized integral differential cocycle checkY_H", "OPEN_UNCONSTRUCTED"),
        ("A13", "self-dual quadratic refinement and equivariant polarization", "OPEN_UNCONSTRUCTED"),
        ("A14", "caps, APS projectors and BRST-compatible boundary domains", "OPEN_UNCONSTRUCTED"),
        ("A15", "combined anomaly-line identity on all seven-bordism classes", "SELECTED_OPEN"),
        ("A16", "same-action microscopic completion", "OPEN_FAILED"),
        ("A17", "spectrum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [
        {"id": criterion_id, "requirement": requirement, "status": status}
        for criterion_id, requirement, status in rows
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": (
            "OPEN: the naive smooth Spin x Spin11 GS/WuCS class has no integral restriction "
            "to the current Z4 or Z2 isotropy data, conditional SU2R curvature "
            "remains nonzero, and no combined-H anomaly-line trivialization exists."
        ),
        "G2": (
            "OPEN: there is no accepted Wilsonian action, supersymmetry-breaking "
            "sector or regulator-defined physical pole spectrum."
        ),
        "G3": (
            "OPEN: the global H_Gamma orbibundle, quotient caps, BPS/APS projectors, "
            "junction conditions and positive Hessian are absent."
        ),
        "G4": (
            "OPEN: the gauge-fixed BV/BRST KK operator, zero-mode measure, regulator, "
            "hierarchy and thresholds are absent."
        ),
        "G5": (
            "OPEN: at least ten neutral chiral zero modes remain and no accepted "
            "full-rank supersymmetric stabilization sector is present."
        ),
        "G6": "OPEN: reheating, defects, relic abundances and BBN are uncomputed.",
        "G7": (
            "OPEN: flavor, decay, proton and collider predictions are not derived "
            "from an accepted microscopic action."
        ),
        "G8": (
            "OPEN: the Dai--Freed, self-dual/WuCS and cap/defect anomaly lines have "
            "not been canonically trivialized on the full seven-dimensional bordism domain."
        ),
    }


def build_report() -> dict[str, Any]:
    v76 = load_bound(V76_MASTER_PATH, EXPECTED_CORES["v76_master"])
    v77 = load_bound(V77_ROUTE_PATH, EXPECTED_CORES["v77_route"])
    routes = route_summary(v76)
    criteria = acceptance_criteria()
    gates = gate_ledger()
    decision = v77["terminal_decision"]
    tensor = v77["tensor_lattice_and_isotropy_cocycle_audit"]
    su2r = v77["conditional_order2_SU2R_index_density"]
    action = v77["parent_action_scenario_audit"]
    target = v77["anomaly_line_trivialization_target"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V76_master": v76["core_sha256"],
            "V76_route_via_V77_lineage": v77["lineage"]["V76_route_core"],
            "V77_route": v77["core_sha256"],
        },
        "lineage": {
            "parent_master": "V76",
            "new_route": "B77",
            "parent_route_matrix_sha256": canonical_sha(v76["route_matrix"]),
            "parent_route_count": len(v76["route_matrix"]),
            "supersession_scope": (
                "refines F76's scalar determinant request to the combined anomaly-line "
                "problem and rejects the ordinary smooth GS orbifold restriction; it "
                "does not exclude a newly constructed combined-H refinement, explicit "
                "cap/defect sector, changed isotropy lift or changed UV parent"
            ),
        },
        "route_matrix": routes,
        "acceptance_criteria": criteria,
        "gate_ledger": gates,
        "consolidated_theory_card": {
            "current_action_status": "REJECTED",
            "research_program_status": (
                "VIABLE_ONLY_IF_COMBINED_H_COCYCLE_CAP_DEFECT_OR_CHANGED_PARENT_IS_CONSTRUCTED"
            ),
            "selected_open_candidate": (
                "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
            ),
            "accepted_extension_count": 0,
            "exact_gains": [
                "space-group abelianization Z4 x Z2 and all eight flat character probes",
                "exact reconstruction of the bound complete-F71 equal-corner residue from its three bulk/neutral blocks",
                "separation of unmodified V70, provisional V71-neutral and complete-but-unaccepted F71 action scenarios",
                "V71-provisional qL lifts on inherited V70 fields: z00 (-28,-20)/192 versus z11 (-24,-24)/192, with mixed vectors (-1/4,-60) versus (-1/4,40)",
                "ten forced neutral chiral compactification zero modes and the resulting zero-momentum KK-product correction",
                "tensor-lattice rigidity det(a,b)=-6, forcing the unchanged lift to the identity",
                "ordinary GS restriction no-go: 2Y=(3,2) at both Z4 corners and (1,1) at the Z2 orbit",
                "conditional standard-branch Z2 SU2R polynomial rho(4rho^2+21nu^2-25p1)/96",
                "conditional Z4 restricted bulk cross-check with rho=0 exactly recovering the V71 bulk/neutral profile",
                "precise combined anomaly-line/WuCS/cap identity required for completion",
            ],
            "retired_shortcuts": [
                "promoting a local equivariant polynomial to a scalar determinant",
                "using the zero unprimed determinant as a physical one-loop answer",
                "repairing the missing integral GS class by regulator choice",
                "using a nontrivial unchanged-action tensor-lattice twist",
                "interpreting V71's normal-only Z2 zero as a full SU2R-background zero",
            ],
            "open_new_physics": [
                "a global combined-H characteristic/torsion refinement checkY_H with canonical gluing",
                "an explicit invertible cap/defect sector compatible with the full BRST/BV complex",
                "a consistent string/flux source and tadpole sector with recomputed anomaly ledger",
                "a changed isotropy lift or different UV parent followed by complete recomputation",
            ],
        },
        "strict_master_decision": {
            "reason": decision["honest_outcome"],
            "naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction": decision[
                "naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction"
            ],
            "tensor_lattice_basis_determinant": tensor[
                "determinant_of_a_b_basis_over_Q"
            ],
            "nontrivial_unchanged_tensor_lattice_twist_exists": decision[
                "nontrivial_unchanged_tensor_lattice_twist_exists"
            ],
            "minimum_neutral_chiral_compactification_zero_modes": v77[
                "zero_mode_and_anomaly_line_audit"
            ]["minimum_neutral_chiral_zero_modes"],
            "equal_corner_profile_is_an_accepted_current_action": decision[
                "equal_corner_profile_is_an_accepted_current_action"
            ],
            "V71_provisional_lifts_on_V70_fields_normal_profiles": {
                "z00": action["scenarios"][
                    "V71_neutral_witness_without_F71_local_compensators"
                ]["z00_over_192"],
                "z11": action["scenarios"][
                    "V71_neutral_witness_without_F71_local_compensators"
                ]["z11_over_192"],
            },
            "conditional_Z2_SU2R_coefficients_over_96": su2r["total"][
                "coefficients_over_96_rho3_rho_nu2_rho_p1"
            ],
            "conditional_Z2_projection_scope": su2r["projection_scope"],
            "conditional_Z4_coefficients_over_192": su2r[
                "Z4_restricted_bulk_crosscheck"
            ]["coefficients_over_192"],
            "conditional_Z4_projection_scope": su2r[
                "Z4_restricted_bulk_crosscheck"
            ]["scope"],
            "conditional_SU2R_results_globalized": False,
            "combined_anomaly_line_identity": target[
                "closed_seven_manifold_target"
            ],
            "combined_anomaly_line_categorical_target": target[
                "categorical_trivialization_target"
            ],
            "combined_anomaly_line_trivialized": decision[
                "combined_anomaly_line_trivialized"
            ],
            "same_action_microscopic_completion_found": decision[
                "same_action_microscopic_completion_found"
            ],
            "selected_candidate": decision["selected_candidate"],
            "selected_candidate_accepted": decision["selected_candidate_accepted"],
            "current_Spin11_action_status": "REJECTED",
            "closed_gates": [],
            "complete_theory": False,
        },
        "regression_scope": {
            "inherited_V76_scope_sha256": canonical_sha(v76["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v77_equivariant_parent_anomaly_line_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v77["source_manifest"],
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
    gains = "".join(f"- {row}\n" for row in card["exact_gains"])
    retired = "".join(f"- {row}\n" for row in card["retired_shortcuts"])
    open_new = "".join(f"- {row}\n" for row in card["open_new_physics"])
    gates = "".join(
        f"- **{gate}** — {status}\n" for gate, status in report["gate_ledger"].items()
    )
    return f"""# V77 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action is **{card['current_action_status']}**.  The research program
is `{card['research_program_status']}`.  V77 does not close G1.  It proves that
the naive smooth Spin x Spin11 Green--Schwarz characteristic class has no integral
restriction to any current orbifold isotropy stratum, while the unchanged
tensor lattice admits no compensating nontrivial twist.  The standard induced
raw-character branch also carries conditional nonzero SU(2)R curvature.
The equal-corner profile belongs only to the complete but unaccepted F71 local
ledger.  Applying V71's provisional qL assignments to inherited V70 localized
fields and the provisional V71 neutral witness gives z00 `(-28,-20)/192` and
z11 `(-24,-24)/192`; V70 itself did not define those continuous normal lifts,
and this hybrid must not be identified with an accepted current action.

The selected candidate is `{card['selected_open_candidate']}`.  Completion
requires a combined-H differential cocycle and a canonical bare-fermion x
self-dual/WuCS x cap/defect anomaly-line identity on the entire seven-dimensional
bordism domain.  None has been constructed.
The displayed SU(2)R densities set gauge/flavor curvature to zero; the Z4 result
also excludes inherited V70 and new F71 localized fields, so neither is a full
action polynomial.

## Exact gains

{gains}
## Retired shortcuts

{retired}
## Physics still capable of changing the verdict

{open_new}
## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V77 master core hash is not canonical")
    if report["input_core_hashes"]["V76_master"] != EXPECTED_CORES["v76_master"]:
        raise RuntimeError("V76 master lineage mismatch")
    if report["input_core_hashes"]["V77_route"] != EXPECTED_CORES["v77_route"]:
        raise RuntimeError("V77 route lineage mismatch")
    if not all(status.startswith("OPEN") for status in report["gate_ledger"].values()):
        raise RuntimeError("a G gate was promoted")
    decision = report["strict_master_decision"]
    if decision["naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction"]:
        raise RuntimeError("ordinary GS orbifold cocycle was overclaimed")
    if decision["tensor_lattice_basis_determinant"] != -6:
        raise RuntimeError("tensor-lattice rigidity was lost")
    if decision["equal_corner_profile_is_an_accepted_current_action"]:
        raise RuntimeError("the unaccepted F71 equal-corner profile was promoted")
    if decision["V71_provisional_lifts_on_V70_fields_normal_profiles"] != {
        "z00": [-28, -20],
        "z11": [-24, -24],
    }:
        raise RuntimeError("V70/F71 parent-action scenarios were merged")
    if decision["conditional_SU2R_results_globalized"]:
        raise RuntimeError("conditional local SU2R result was overpromoted")
    if decision["combined_anomaly_line_trivialized"]:
        raise RuntimeError("combined anomaly-line identity was overclaimed")
    if decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("same-action completion was overclaimed")
    if decision["selected_candidate_accepted"]:
        raise RuntimeError("selected open candidate was overpromoted")
    if decision["closed_gates"]:
        raise RuntimeError("a G gate was closed")
    if decision["complete_theory"]:
        raise RuntimeError("theory completeness was overclaimed")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if OUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    report = (
        write_artifacts()
        if args.write
        else check_artifacts()
        if args.check
        else build_report()
    )
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
