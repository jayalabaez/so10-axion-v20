"""Append unaccepted B104 (exact Q2 core reduction) as route 32 without rewriting history."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V104_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V104_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v104_multipath_g1_frontier_master_audit.py"
V103_MASTER_PATH = ROOT / "SUSY_V103_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V104_ROUTE_PATH = ROOT / "SUSY_V104_Q2_CORE_REDUCTION_AUDIT.json"
EXPECTED_CORES = {
    "v103_master": "6150ab0d71c2a70c95491325cd1bb094827fd48ea165b1a80d838a71c79b9827",
    "v104_route": "b22468dd4bd4ab3c77839ba8fa561deee01a539f23fc64e176c4660a169cc41c",
}
NEXT_ID = "F105_Q2_RESIDUAL_CLOSURE_Q1_AND_TARGET_SYSTEMS_WITH_COVARIANT_ACTION_REPAIR"
STATUS = "V104_MASTER__EXACT_Q2_CORE_REDUCTION_APPENDED__LEADING_PAIR_RESULTANT_NONZERO__Q2_CONFINED_NOT_SOLVED__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def theory_card(previous, helper, rows):
    card = copy.deepcopy(previous["consolidated_theory_card"])
    concl = helper["q2_conclusion"]
    card["accepted_extension_count"] = sum(bool(row["accepted"]) for row in rows)
    card["historical_V103_card_sha256"] = canonical_sha(previous["consolidated_theory_card"])
    card["q2_core_reduction"] = {
        "leading_coefficient_identity": helper["leading_coefficient_identity"]["statement"],
        "discriminant_h_independent": helper["discriminant"]["is_independent_of_h"],
        "R4core_t_and_M_powers_removed": helper["leading_cores"]["R4core_t_and_M_powers_removed"],
        "C43core_t_and_M_powers_removed": helper["leading_cores"]["C43core_t_and_M_powers_removed"],
        "leading_pair_h_resultant_nonzero": helper["fixed_modular_witnesses"]["leading_pair_resultant_is_nonzero_polynomial"],
        "Q2_confined_to_proper_subvariety": True,
        "Q2_solved": concl["Q2_solved"],
        "Q2_excluded": concl["Q2_excluded"],
    }
    # The globally integral quartic frontier is unchanged except that Q2 is now confined.
    card["all_original_quartic_sections_excluded"] = False
    card["all_original_rational_sections_excluded"] = False
    card["actual_target_sections_constructed"] = False
    card["experimental_confirmation"] = False
    return card


def content():
    previous = load_bound(V103_MASTER_PATH, EXPECTED_CORES["v103_master"])
    route = load_bound(V104_ROUTE_PATH, EXPECTED_CORES["v104_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 31 or [row["ordinal"] for row in rows] != list(range(1, 32)):
        raise RuntimeError("all 31 historical route records are required")
    if route["input_core_hashes"]["v103_master"] != EXPECTED_CORES["v103_master"]:
        raise RuntimeError("the V104 route does not bind this V103 master")
    if route["parent_obligation"] != previous["next_required_action"]["id"]:
        raise RuntimeError("the V104 route does not answer the V103 F104 obligation")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("the F105 successor obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    helper = route["q2_core_reduction"]
    if helper.get("core_sha256") != canonical_sha(helper):
        raise RuntimeError("noncanonical bound Q2 helper")
    gates = copy.deepcopy(route["gate_ledger"])
    if set(gates) != {"G" + str(index) for index in range(1, 9)} or not all(value.startswith("OPEN") for value in gates.values()):
        raise RuntimeError("V104 may not promote a branch gate")
    decision = copy.deepcopy(route["terminal_decision"])
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V104 has no accepted complete parent")
    for report, base in ((previous, "susy_v103_multipath_g1_frontier_master_audit"), (route, "susy_v104_q2_core_reduction_audit")):
        for name, key in ((base + ".py", "generator_sha256"), ("test_" + base + ".py", "test_sha256")):
            if file_sha(ROOT / name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound integration source/test changed: " + name)
    for name, value in route["artifact_hashes"].items():
        if name.endswith(".py") and file_sha(ROOT / name) != value:
            raise RuntimeError("bound V104 helper source/test changed: " + name)

    rows.append({
        "ordinal": 32, "route_id": "B104",
        "name": "exact original quartic Q2 core reduction and leading-pair resultant confinement",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the Q2 leading residual is the exact quadratic A2 q^2+A1 q+A0 with A2 = -1296 t^6 M, nonzero on Q2",
            "the q-discriminant Delta = A1^2-4 A2 A0 is independent of h, so the square condition decouples from h",
            "each remaining residual reduces to linear-in-q; the M^2-cleared leading cores R4core, C43core have a nonzero h-resultant (witnesses 28,97,91 mod 101)",
            "Q2 is confined to a proper subvariety, neither solved nor excluded; Q1, the target tails, rational sections, rank and all gates are unchanged",
        ],
    })
    if any(row["accepted"] for row in rows):
        raise RuntimeError("all extension routes remain unaccepted")

    criteria = copy.deepcopy(previous["acceptance_criteria"])
    for row in criteria:
        if row["id"] == "A3":
            row["status"] = "DOUBLE_PIVOT_BOUNDARY_EXCLUDED__Q2_CONFINED_TO_PROPER_SUBVARIETY__Q1_OPEN"
    return {
        "schema": "susy_v104_multipath_g1_frontier_master_v1", "version": "V104", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V103", "new_route": "B104", "parent_route_count": 31,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True, "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": criteria,
        "consolidated_theory_card": theory_card(previous, helper, rows),
        "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
        "supersession_ledger": {
            "V103_history_preserved": True,
            "only_geometry_Q2_branch_advanced": True,
            "Q2_reduced_not_solved_not_excluded": True,
            "physics_covariant_action_repair_still_open": True,
        },
        "strict_master_decision": decision, "gate_ledger": gates,
        "next_required_action": copy.deepcopy(route["next_required_action"]),
        "primary_sources": copy.deepcopy(route["primary_sources"]),
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)},
    }


def build_report():
    out = content()
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_report(out):
    if out.get("core_sha256") != canonical_sha(out):
        raise RuntimeError("V104 master core is noncanonical")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V104 master lineage, derivation or scope changed")


def render_markdown(out):
    if out["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("an accepted extension may not be concealed")
    card = out["consolidated_theory_card"]["q2_core_reduction"]
    paragraphs = [
        "# SUSY V104 multipath frontier master", "Status: " + out["status"], "Core SHA256: " + out["core_sha256"],
        "All 31 historical route records are preserved exactly, and B104 is appended as unaccepted route 32. All G1-G8 in the separate SUSY/C8 branch remain OPEN. Canonical V21 scope is unchanged; this is a bounded research step, not a completed theory.",
        "## The exact Q2 core reduction",
        "On the surviving original quartic chart Q2 (t nonzero, L=0, M nonzero) the L=0 leading residual is the exact quadratic A2 q^2 + A1 q + A0, with A2 = -1296 t^6 M and M = -alpha t^2 + 4 p t + 64 nonzero on Q2. The q-discriminant Delta = A1^2 - 4 A2 A0 is independent of h, so a rational q requires Delta to be a square in C(X) as a condition on t, p and the parameters alone.",
        "After reconstructing r and reducing q^2 through the quadratic, every remaining residual becomes linear in q. The pairwise q-eliminations are necessary on Q2 and, once the spurious M-power from A2 is divided out, give integer-coefficient cores R4core = R4/(t^6 M^2) and C43core = C43/(t^3 M^2). Their h-resultant is a nonzero polynomial, taking the values 28, 97 and 91 modulo 101 at the fixed slices (2,1), (3,1) and (2,3) with M nonzero. Hence Q2 cannot contain an open two-parameter family; it is confined to a proper subvariety, neither solved nor excluded.",
        "## Scope",
        "The Q1 chart, the height-37 and height-148 target systems, general rational sections and the exact Mordell-Weil rank are untouched. Original rank 0..11, torsion 1, the coefficient payload and every gate are unchanged. The physics covariant-action repair required by F104 remains open. Tests verify arithmetic, lineage and scope, not experimental confirmation.",
        "## Acceptance and next obligation",
        "There are zero accepted extensions.",
    ]
    criteria = "\n".join("- " + row["id"] + ": " + row["status"] for row in out["acceptance_criteria"])
    tail = [out["next_required_action"]["id"], out["next_required_action"]["primary"], out["next_required_action"]["parallel"],
            "[Detailed V104 Q2 derivation](SUSY_V104_Q2_CORE_REDUCTION_AUDIT.md)", "## Primary sources"]
    sources = "\n".join("- [" + row["use"] + "](" + row["url"] + ")" for row in out["primary_sources"])
    return "\n\n".join(paragraphs) + "\n\n" + criteria + "\n\n" + "\n\n".join(tail) + "\n\n" + sources + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    out = build_report()
    validate_report(out)
    if args.write:
        OUT_JSON.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(out), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V104", "core_sha256": out["core_sha256"], "route_count": len(out["route_matrix"]),
                      "accepted_extensions": 0, "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
