#!/usr/bin/env python3
"""V70 fail-closed multipath master for the Spin(11) six-dimensional frontier.

The historical A60 and C rows are preserved byte-canonically.  B69 is bound
in full and only its unaccepted F69 candidate is superseded: F70 selects the
integer-m301 localized-family charged parent, while the flavor-Wilson
projection is retained as an alternate action.  Exact charged-sector passes
are not promoted to a microscopic action or to gate closure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V70"
DATE = "2026-08-30"
SCHEMA = "susy_v70_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V70_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V70_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v70_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v69_master": ROOT / "SUSY_V69_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v70_route": ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json",
}
EXPECTED_CORES = {
    "v69_master": "ad238c2b92019a50f048c9fb60bb8eea1afd7c35359c57bc9ee2b9ec02690ab6",
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
}
V69_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B69": "9c2ebeaadf2121343927cbcbb1cecf966364658b0b04a52da80b5a05199682e3",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 26
EXPECTED_REGRESSION_TESTS = 348

STATUS = (
    "V70_MULTIPATH_G1_FRONTIER_MASTER__V69_MASTER_AND_V70_ROUTE_CORES_BOUND__"
    "A60_C_AND_EMBEDDED_B69_LINEAGE_PRESERVED__ONLY_F69_SUPERSEDED__F70_"
    "INTEGER_M301_LOCALIZED_PARENT_SELECTED__FLAVOR_WILSON_ALTERNATE__CHARGED_"
    "SPIN_SUSY_LIFT_EXACT__HIGGS_RANK_BRANCH_AND_LOCAL_HESSIAN_EXACT__POINTWISE_"
    "CHARGED_ANOMALY_ZERO__SMOOTH_BULK_QUANTIZATION_PASS__POSITIVE_CHAMBER_"
    "EXISTS__FULL_LOCAL_SUPERGRAVITY_GS_266_NEUTRALS_GLOBAL_QUOTIENT_Z4R_KK_"
    "REGULATOR_ALL_ORDER_VACUUM_PHENOMENOLOGY_OPEN__CURRENT_ACTION_REJECTED__"
    "F70_CANDIDATE_NOT_ACCEPTED__NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing bound input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(next(row for row in master["route_matrix"] if row["route_id"] == route_id))


def frozen_v69_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V69_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V69 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 70):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v70_spin11_localized_parent_spin_flavor_completion_audit.py"
    if route_test.is_file():
        selected[route_test.name] = route_test
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = [
        {"path": name, "test_functions": len(test_re.findall(path.read_text(encoding="utf-8")))}
        for name, path in sorted(selected.items())
    ]
    return {
        "selection": "all V59-V69 tests plus the V70 route test; the V70 master test is excluded",
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "files": rows,
    }


def f70_candidate(v70: Mapping[str, Any]) -> dict[str, Any]:
    branch = v70["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    anomaly = v70["localized_anomaly_and_bulk_global_audit"]
    return {
        "id": "F70",
        "kind": "CANDIDATE_6D_ORDER4_LOCALIZED_FAMILY_INTEGER_M301_ACTION",
        "status": "EXACT_CHARGED_CLASSICAL_AND_LOCAL_POLYNOMIAL_CANDIDATE",
        "selected": True,
        "accepted": False,
        "same_action_complete": False,
        "supersedes_candidate": "F69",
        "phase_assignment": "A:m=3, B:m=0, C:m=1",
        "charged_spin_SUSY_lift": v70["acceptance"]["A7_spin_R_lift_for_localized_charged_parent"],
        "Higgs_spectrum": v70["acceptance"]["A8_Higgs_spectrum"],
        "rank_and_Hessian": {
            "branch_status": branch["status"],
            "driver_nondegeneracy": branch["local_U5_stabilizer"][
                "complete_renormalizable_driver_class"
            ]["nondegeneracy_condition"],
            "driver_Hessian_determinant": branch["local_U5_stabilizer"][
                "complete_renormalizable_driver_class"
            ]["exact_determinant"],
            "doublet_mass_rank": branch["mandatory_and_local_masses"][
                "rank_for_g_nonzero_vB_nonzero"
            ],
        },
        "pointwise_charged_anomaly_zero": anomaly["integer_m301_branch"][
            "pointwise_charged_polynomial_zero"
        ],
        "smooth_bulk_quantization": copy.deepcopy(anomaly["smooth_bulk_quantization"]),
        "positive_tensor_chamber": copy.deepcopy(anomaly["positive_tensor_chamber"]),
        "four_dimensional_anomalies": copy.deepcopy(v70["four_dimensional_zero_mode_anomaly_audit"]),
        "open_boundary": copy.deepcopy(v70["open_obligations"]),
    }


def flavor_wilson_alternate(v70: Mapping[str, Any]) -> dict[str, Any]:
    branch = v70["localized_parent_completion_branches"]["minimal_flavor_Wilson_projection"]
    return {
        "id": "F70_ALT",
        "kind": "ALTERNATE_6D_ORDER4_FLAVOR_WILSON_PROJECTION",
        "status": branch["status"],
        "selected": False,
        "accepted": False,
        "same_action_complete": False,
        "supersedes_candidate": "F69",
        "advance": "an exact active-11 plus two-spectator flavor-Wilson projection with no spectator zero modes",
        "spectator_status": branch["spectator_pair"]["status"],
        "open_boundary": copy.deepcopy(v70["open_obligations"]),
    }


def candidate_matrix(old_b: Mapping[str, Any], v70: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = [copy.deepcopy(row) for row in old_b["candidate_matrix"] if row["id"] != "F69"]
    inherited.extend([f70_candidate(v70), flavor_wilson_alternate(v70)])
    return inherited


def b70_row(v69: Mapping[str, Any], v70: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v69_row(v69, "B69")
    return {
        "route_id": "B70",
        "name": "Spin(11) order-four localized-parent charged completion frontier, fail closed",
        "supersedes_V69_route_id": "B69",
        "supersession_scope": "F69 candidate only",
        "bound_parent_master_core": EXPECTED_CORES["v69_master"],
        "bound_V70_route_core": EXPECTED_CORES["v70_route"],
        "inherited_B69_row_sha256": object_sha(old_b),
        "inherited_B69_row": old_b,
        "current_bound_action_status": "REJECTED",
        "V64_null_mode_stands_for_current_action": True,
        "V70_selected_candidate": f70_candidate(v70),
        "V70_flavor_Wilson_alternate": flavor_wilson_alternate(v70),
        "candidate_matrix": candidate_matrix(old_b, v70),
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates() -> list[dict[str, Any]]:
    decisions = {
        "G1": "OPEN: F70 closes the charged classical Spin/SUSY, spectrum and anomaly sub-obligations, but the local supergravity/GS action and neutral equivariance are absent.",
        "G2": "OPEN: no coefficient-level soft spectrum, pole masses or mediator-complete flavor fit is derived.",
        "G3": "OPEN: a local driver Hessian and positive tensor chamber exist, but the all-order compactification vacuum and stabilization are not proved.",
        "G4": "OPEN: the charged zero-mode Higgs pair is exact, but the gauge-fixed KK determinant, hierarchy and thresholds are absent.",
        "G5": "OPEN: the charged spectrum is controlled, but 266 neutral hypers and the complete compactified spectrum remain unaudited locally.",
        "G6": "OPEN: reheating, defects, relics, moduli and cosmology are not computed.",
        "G7": "OPEN: selected Z4R operators pass classically, but its gauged origin, pointwise anomaly and proton lifetime are not proved.",
        "G8": "OPEN: the equivariant GS/Wu-Chern-Simons action, global quotient, Dai-Freed phases, regulator and thresholds remain absent.",
    }
    return [
        {"gate": gate, "status": "OPEN", "V70_master_closed": False, "decision": decisions[gate]}
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def theory_card(b70: Mapping[str, Any], v70: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V70 fail-closed Spin(11) localized-parent frontier card",
        "current_bound_action_status": "REJECTED",
        "selected_candidate": "F70 integer-m301 localized-family charged parent",
        "alternate_candidate": "F70_ALT flavor-Wilson projection",
        "exact_passes": [
            "genuine charged Spin lift and 4D N=1 Lorentz-SU2R superfield lift",
            "integer-m301 no-triplet Higgs spectrum with rank-one heavy doublet mass",
            "renormalizable local rank/driver branch with full physical Hessian when detJ is nonzero",
            "zero charged-fermion projector anomaly at every fixed locus",
            "integral unimodular smooth-bulk anomaly coefficients",
            "existence of a positive gauge-and-gravity tensor chamber",
            "exact four-dimensional perturbative and SU2 Witten anomaly cancellation",
        ],
        "open_obligations": copy.deepcopy(v70["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b70["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "F70 is an improved new-action candidate.  Charged-sector passes do not supply "
            "the neutral/tensor/gravitational local action, the quantum global definition, "
            "or any phenomenological gate closure."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v69 = load_bound("v69_master")
    v70 = load_bound("v70_route")
    a = frozen_v69_row(v69, "A60")
    old_b = frozen_v69_row(v69, "B69")
    c = frozen_v69_row(v69, "C")
    b = b70_row(v69, v70)
    gates = master_gates()
    scope = regression_scope()
    if scope["file_count"] != EXPECTED_REGRESSION_FILES or scope["test_count"] != EXPECTED_REGRESSION_TESTS:
        raise RuntimeError(
            f"unexpected V59-V70 route regression scope: {scope['file_count']} files, {scope['test_count']} tests"
        )
    report: dict[str, Any] = {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": "Does V70 promote the exact charged localized-parent completion to a full microscopic action or close any gate?",
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_V69_master_core": v69["core_sha256"],
            "V70_route_core": v70["core_sha256"],
            "preserved_rows": {"A60": object_sha(a), "C": object_sha(c)},
            "embedded_B69_row_sha256": object_sha(old_b),
            "historical_artifacts_modified": False,
            "supersession_scope": "only F69 is replaced by selected F70; F70_ALT is retained separately",
        },
        "artifact_integrity": {
            "V69_master_and_V70_route_modified": False,
            "A60_and_C_preserved_exactly": True,
            "B69_bound_in_full_inside_B70": True,
            "current_bound_Spin11_action_status": "REJECTED",
        },
        "regression_scope": scope,
        "route_matrix": [a, b, c],
        "consolidated_theory_card": theory_card(b, v70),
        "acceptance_criteria": copy.deepcopy(v69["acceptance_criteria"]),
        "cross_route_composition_rule": {
            "logical_rule": "A60, the rejected current Spin11 action, F70, F70_ALT and C are distinct actions; subsector passes cannot be spliced.",
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
        },
        "comparison_conclusion": {
            "heterotic_A60": v69["comparison_conclusion"]["heterotic_A60"],
            "Spin11_B70": "Current action REJECTED. F70 is exact in the displayed charged classical/local-polynomial sectors but lacks the full local quantum supergravity action.",
            "gauged_U1R_C": v69["comparison_conclusion"]["gauged_U1R_C"],
            "frontier": "Compute the 266-neutral/tensor/gravity fixed-locus action and equivariant GS descent before any acceptance claim.",
        },
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "V64_null_mode_stands_in_current_action": True,
            "F69_status": "SUPERSEDED_AS_CANDIDATE_BY_F70",
            "F70_selected_branch": "INTEGER_M301_LOCALIZED_PARENT",
            "F70_flavor_Wilson_branch": "ALTERNATE_NOT_SELECTED",
            "charged_spin_SUSY_lift": "PASS_EXACT",
            "Higgs_rank_local_Hessian": "PASS_EXACT_CONDITIONAL_ON_NONZERO_VEVS_AND_DETJ",
            "pointwise_charged_anomaly": "PASS_EXACT_ZERO",
            "smooth_bulk_quantization": "PASS",
            "positive_tensor_chamber": "PASS_EXISTENCE_NOT_STABILIZATION",
            "full_local_supergravity_GS": "OPEN",
            "neutral_266_equivariance": "OPEN",
            "global_quotient_and_Z4R": "OPEN",
            "KK_regulator_all_order_vacuum_phenomenology": "OPEN",
            "F70_new_action_accepted": False,
            "accepted_extension_count": 0,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "V70 completes the charged classical and local-polynomial frontier of one "
                "localized-family candidate, including exact pointwise charged anomaly zero. "
                "It does not construct the neutral/tensor/gravitational local supergravity and "
                "global quantum action, so F70 is not accepted and G1-G8 remain open."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "V70_primary_claims_live_in_bound_route": True,
            "charged_pointwise_zero_is_not_full_local_supergravity": True,
            "positive_chamber_is_not_stabilization": True,
            "smooth_bulk_quantization_is_not_orbifold_GS_completion": True,
            "mechanism_pass_is_not_gate_closure": True,
        },
        "source_manifest": source_manifest(),
    }
    routes = {row["route_id"]: row for row in report["route_matrix"]}
    candidates = {row["id"]: row for row in routes["B70"]["candidate_matrix"]}
    f70 = candidates["F70"]
    old_candidate_rows = [row for row in old_b["candidate_matrix"] if row["id"] != "F69"]
    new_inherited_rows = [row for row in routes["B70"]["candidate_matrix"] if row["id"] not in {"F70", "F70_ALT"}]
    checks = {
        "input_cores_exact": report["input_core_hashes"] == EXPECTED_CORES,
        "route_order_and_supersession": list(routes) == ["A60", "B70", "C"] and routes["B70"]["supersedes_V69_route_id"] == "B69",
        "A60_preserved": object_sha(routes["A60"]) == V69_ROW_SHA["A60"],
        "C_preserved": object_sha(routes["C"]) == V69_ROW_SHA["C"],
        "B69_parent_bound": routes["B70"]["inherited_B69_row_sha256"] == V69_ROW_SHA["B69"] and object_sha(routes["B70"]["inherited_B69_row"]) == V69_ROW_SHA["B69"],
        "only_F69_superseded": old_candidate_rows == new_inherited_rows and "F69" not in candidates,
        "candidate_set_exact": set(candidates) == {"D67", "H66", "T66", "B3_IR", "E68", "F70", "F70_ALT"},
        "F70_selected_not_accepted": f70["selected"] and not f70["accepted"] and not f70["same_action_complete"],
        "flavor_Wilson_alternate": not candidates["F70_ALT"]["selected"] and not candidates["F70_ALT"]["accepted"],
        "charged_spin_SUSY_pass": f70["charged_spin_SUSY_lift"] == "PASS_EXACT_CLASSICAL_SUPERFIELD",
        "Higgs_rank_Hessian_pass": f70["Higgs_spectrum"] == "PASS_EXACT_IN_BOTH_DISPLAYED_BRANCHES" and f70["rank_and_Hessian"]["doublet_mass_rank"] == 1 and f70["rank_and_Hessian"]["driver_nondegeneracy"] == "det J != 0",
        "pointwise_charged_anomaly_zero": f70["pointwise_charged_anomaly_zero"] is True,
        "smooth_bulk_quantization_pass": f70["smooth_bulk_quantization"]["coefficient_quantization"] == "PASS_ON_THE_SMOOTH_BULK" and f70["smooth_bulk_quantization"]["unimodular_integral"],
        "positive_chamber_pass_scoped": f70["positive_tensor_chamber"]["gauge_kinetic_positive_and_j_dot_a_positive"] and not f70["positive_tensor_chamber"]["stabilized_tensor_vacuum"],
        "four_dimensional_anomalies_zero": f70["four_dimensional_anomalies"]["all_perturbative_coefficients_zero"] and f70["four_dimensional_anomalies"]["SU2_Witten"]["even"],
        "required_obligations_open": all(any(term in item for item in v70["open_obligations"]) for term in ("266 neutral", "Green-Schwarz", "global Spin", "Z4R", "all-order", "KK", "soft spectrum")),
        "regression_scope_exact": scope["file_count"] == EXPECTED_REGRESSION_FILES and scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "acceptance_criteria_open": all(row["status"] == "OPEN" for row in report["acceptance_criteria"]),
        "all_gates_open": all(row["status"] == "OPEN" and not row["V70_master_closed"] for row in gates),
        "no_splice_no_acceptance": not report["cross_route_composition_rule"]["cross_route_splicing_allowed"] and not report["cross_route_composition_rule"]["aggregated_gate_closure"] and routes["B70"]["accepted_extension_count"] == 0,
        "fail_closed": report["strict_master_decision"]["current_Spin11_action_status"] == "REJECTED" and not report["strict_master_decision"]["F70_new_action_accepted"] and not report["strict_master_decision"]["same_action_microscopic_completion_found"] and report["strict_master_decision"]["closed_gates"] == [] and not report["strict_master_decision"]["complete_theory"],
    }
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V70 master canonical core mismatch")
    if canonical_bytes(report) != canonical_bytes(build_report()):
        raise RuntimeError("V70 master recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"V70 master integrity checks failed: {failed}")
    if report["strict_master_decision"]["closed_gates"] or report["strict_master_decision"]["F70_new_action_accepted"]:
        raise RuntimeError("V70 master overclaimed acceptance or gate closure")


def render_markdown(report: Mapping[str, Any]) -> str:
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B70")
    f70 = b["V70_selected_candidate"]
    candidate_rows = "\n".join(
        f"| {row['id']} | {row['kind']} | {row['status']} | {row.get('selected', False)} | {row['accepted']} |"
        for row in b["candidate_matrix"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |" for row in report["gate_ledger"]
    )
    obligations = "\n".join(f"- {item}" for item in report["consolidated_theory_card"]["open_obligations"])
    return f"""# V70 multipath G1 frontier master audit

Version: {report['version']}
Date: {report['date']}
Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The current bound Spin(11) action remains **REJECTED**, F70 is **not
accepted**, and G1-G8 remain OPEN.  Only the unaccepted F69 candidate is
superseded.  A60 and C are preserved exactly, and the complete B69 row is
embedded at `{report['lineage']['embedded_B69_row_sha256']}`.

## Exact F70 advances

The selected integer-m301 localized-family branch has an exact charged
Spin/SUSY superfield lift, one light Higgs pair with no triplet zero modes,
a rank-one heavy-doublet matrix, and a full local driver/radial Hessian on
the open branch `{f70['rank_and_Hessian']['driver_nondegeneracy']}`.  Its
charged-fermion anomaly polynomial vanishes pointwise.  Smooth-bulk anomaly
coefficients are integral and unimodular, and a positive tensor chamber
exists; stabilization is not claimed.

The flavor-Wilson construction is retained as an alternate, not combined
with F70.

## Candidate isolation

| ID | Kind | Status | Selected | Accepted |
|---|---|---|---:|---:|
{candidate_rows}

## Still required

{obligations}

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Decision

{report['strict_master_decision']['honest_outcome']}

Regression scope: {report['regression_scope']['test_count']} top-level test
functions in {report['regression_scope']['file_count']} files, before pytest
parametrization.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V70 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V70 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V70 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
