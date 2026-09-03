"""F104 route audit: bind the exact Q2 core reduction to the V103 frontier.

This route accepts the V103 obligation F104 on its parallel geometry branch and
records the bounded Q2 advance.  It binds the immutable V103 route and master
cores, wraps the v104 Q2 core-reduction helper, keeps every G1-G8 gate OPEN,
accepts no parent, and emits the successor obligation F105.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common
import v104_q2_core_reduction_audit as q2

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V104_Q2_CORE_REDUCTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT / (STEM + extension) for extension in (".json", ".md"))
TEST_PATH = ROOT / "test_susy_v104_q2_core_reduction_audit.py"
V103_ROUTE_PATH = ROOT / "SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT.json"
V103_MASTER_PATH = ROOT / "SUSY_V103_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
EXPECTED_CORES = {
    "v103_route": "cb5074dae5e38ea34c167d869050abd1926053c6bda229edf919b7d7f2e16e53",
    "v103_master": "6150ab0d71c2a70c95491325cd1bb094827fd48ea165b1a80d838a71c79b9827",
}
PARENT_OBLIGATION = "F104_COVARIANT_ACTION_PARITY_INFLOW_AND_REMAINING_SECTION_SYSTEMS"
NEXT_ID = "F105_Q2_RESIDUAL_CLOSURE_Q1_AND_TARGET_SYSTEMS_WITH_COVARIANT_ACTION_REPAIR"
STATUS = "V104_Q2_CORE_REDUCTION__LEADING_PAIR_RESULTANT_NONZERO__Q2_CONFINED_TO_PROPER_SUBVARIETY__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def crosscheck(route, master, helper):
    if master["input_core_hashes"]["v103_route"] != EXPECTED_CORES["v103_route"]:
        raise RuntimeError("the immutable V103 master-to-route edge changed")
    if route["next_required_action"]["id"] != PARENT_OBLIGATION:
        raise RuntimeError("the parent F104 obligation changed")
    if helper["input_core_hashes"]["v103_route"] != EXPECTED_CORES["v103_route"]:
        raise RuntimeError("the helper does not bind the same V103 route core")
    quartic = route["original_quartic_sections"]
    if helper["bound_reduced_equations_sha256"] != quartic["quartic_reduced_equations_sha256"]:
        raise RuntimeError("the helper reduced-quartic member differs from V103")
    if helper["bound_coefficient_payload_sha256"] != quartic["coefficient_payload_sha256"]:
        raise RuntimeError("the helper coefficient member differs from V103")
    if helper["preserved_frontier"] != quartic["preserved_frontier"]:
        raise RuntimeError("the original rank/torsion/cubic frontier changed")
    if [row["id"] for row in quartic["remaining_quartic_charts"]["live_charts"]] != ["Q1", "Q2"]:
        raise RuntimeError("the two live V103 quartic charts changed")
    concl = helper["q2_conclusion"]
    if concl["Q2_solved"] or concl["Q2_excluded"]:
        raise RuntimeError("Q2 may be neither solved nor excluded at this step")
    if not helper["discriminant"]["is_independent_of_h"]:
        raise RuntimeError("the h-independent discriminant fact was lost")
    if not helper["fixed_modular_witnesses"]["leading_pair_resultant_is_nonzero_polynomial"]:
        raise RuntimeError("the Q2 leading-core resultant witness was lost")
    return {
        "helper_binds_identical_V103_route_and_member": True,
        "Q2_leading_cores_reduced_exactly": helper["leading_coefficient_identity"]["verified_exactly"] and helper["l_zero_quadratic"]["verified_exactly"],
        "Q2_confined_not_solved_not_excluded": True,
        "Q1_and_target_systems_untouched": True,
        "original_rank_torsion_and_cubic_frontier_preserved": True,
        "no_gate_promotion": True,
    }


def content():
    route = load_bound(V103_ROUTE_PATH, EXPECTED_CORES["v103_route"])
    master = load_bound(V103_MASTER_PATH, EXPECTED_CORES["v103_master"])
    for base in ("susy_v103_normal_parity_quartic_target_audit", "susy_v103_multipath_g1_frontier_master_audit"):
        report = route if "normal_parity" in base else master
        for name, key in ((base + ".py", "generator_sha256"), ("test_" + base + ".py", "test_sha256")):
            if file_sha(ROOT / name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound V103 integration source/test changed: " + name)
    helper = q2.build_certificate()
    if helper.get("core_sha256") != canonical_sha(helper):
        raise RuntimeError("noncanonical V104 Q2 helper")
    for name in ("v104_q2_core_reduction_audit.py", "test_v104_q2_core_reduction_audit.py"):
        if not (ROOT / name).is_file():
            raise RuntimeError("missing V104 helper artifact: " + name)

    gates = copy.deepcopy(route["gate_ledger"])
    gates["G8"] = (
        "OPEN: the original cubic exclusion and the quartic L=M=0 boundary remain excluded; "
        "Q2 (t!=0,L=0,M!=0) is now reduced exactly to the common zero locus of the M^2-cleared "
        "leading cores, whose h-resultant is a nonzero polynomial (fixed witnesses 28,97,91 mod 101), "
        "so Q2 is confined to a proper subvariety but is neither solved nor excluded; Q1, the "
        "height-37/148 target tails, general rational sections and the exact rank remain unsolved."
    )
    if set(gates) != {"G" + str(index) for index in range(1, 9)} or not all(value.startswith("OPEN") for value in gates.values()):
        raise RuntimeError("V104 may not promote a branch gate")

    hashes = {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH),
              "v104_q2_core_reduction_audit.py": file_sha(ROOT / "v104_q2_core_reduction_audit.py"),
              "test_v104_q2_core_reduction_audit.py": file_sha(ROOT / "test_v104_q2_core_reduction_audit.py")}
    sources = {}
    for row in helper["primary_sources"]:
        sources.setdefault(row["url"], copy.deepcopy(row))
    return {
        "schema": "susy_v104_q2_core_reduction_route_v1", "version": "V104", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "scope": "Separate SUSY/C8 completion branch. Canonical V21 physical evidence and all historical routes are unchanged; exact mathematical audits are not experimental confirmation.",
        "parent_obligation": PARENT_OBLIGATION,
        "q2_core_reduction": helper,
        "cross_sector_scope_checks": crosscheck(route, master, helper),
        "terminal_decision": {
            "bounded_F104_geometry_step_completed": True,
            "Q2_reduced_to_proper_subvariety": True,
            "Q2_solved": False, "Q2_excluded": False,
            "Q1_or_target_systems_solved": False,
            "covariant_action_repair_constructed": False,
            "same_action_microscopic_parent_accepted": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": gates,
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Impose the remaining Q2 residuals N2,N1,N0 with their cross conditions C42,C32,C4i and the Delta-square condition on the confined subvariety; decide Q2 over C(X) with a certificate, or open the Q1 chart by the same method. No rank or point promotion without a certificate.",
            "parallel": "Construct the covariant action repair required by F104: a globally defined normal/internal tensor or diagonal G-structure carrying normal charge 1 with all old representations and a recomputed vacuum; do not install a neutral constant or a formal inverse eta character by declaration. Continue the height-37/148 target tails with all primitivity and global-tail obligations. Complete nonlinear QK/F/D, Higgs-zero matching, full quantum action, soft spectrum, unification and cosmology on the same data.",
        },
        "artifact_hashes": hashes, "primary_sources": list(sources.values()),
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V104 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V104 route arithmetic, lineage or scope changed")


def render_markdown(report):
    helper = report["q2_core_reduction"]
    witnesses = ", ".join(str(row["h_resultant_mod101"]) for row in helper["fixed_modular_witnesses"]["points"])
    paragraphs = [
        "# SUSY V104: exact Q2 core reduction on the original quartic",
        "Status: " + report["status"], "Core SHA256: " + report["core_sha256"],
        "This is a bounded research step on the separate SUSY/C8 branch, not a completed theory. All G1-G8 remain OPEN, canonical V21 scope is unchanged, and no route parent is accepted.",
        "## The Q2 leading coefficient factors exactly",
        "On the surviving chart Q2 (t nonzero, L=0, M nonzero) the L=0 leading residual is the exact quadratic A2 q^2 + A1 q + A0. Its leading coefficient factors as A2 = -1296 t^6 M with M = -alpha t^2 + 4 p t + 64, so A2 is manifestly nonzero on Q2 and the quadratic is genuine.",
        "The q-discriminant Delta = A1^2 - 4 A2 A0 is independent of h. A rational q on Q2 therefore requires Delta to be a square in C(X), a condition on t, p and the fixed parameters alone, decoupled from h.",
        "## Exact q-elimination and the M-squared cores",
        "After substituting the reconstructed r and reducing q^2 through the quadratic, every remaining residual N4..N0 becomes exactly linear in q, N_i -> ell_i q + m_i. The pairwise eliminations R_i = A2 m_i^2 - A1 ell_i m_i + A0 ell_i^2 and C_ij = ell_i m_j - ell_j m_i are necessary on Q2. The q-reduction multiplies through by powers of A2 = -1296 t^6 M; that M-power is nonzero on Q2 and is divided out exactly, leaving integer-coefficient cores R4core = R4/(t^6 M^2) and C43core = C43/(t^3 M^2).",
        "## The leading pair confines Q2 to a proper subvariety",
        "Both R4core and C43core vanish on any Q2 point. Their h-resultant is a nonzero polynomial in (t,p): at the bound coefficient payload it takes the nonzero values " + witnesses + " modulo 101 at the fixed slices (2,1), (3,1), (2,3), all with M nonzero. Hence Q2 cannot contain an open two-parameter family; its solutions lie on the proper subvariety Res_h(R4core,C43core)=0, together with the retained ell4=ell3=0 degeneracy. Q2 is neither solved nor excluded, and no rational-function degree bound in X is assumed.",
        "## Scope and next obligation",
        "The Q1 chart, the height-37 and height-148 target systems, general rational sections and the exact Mordell-Weil rank are untouched. Original rank 0..11, torsion 1, the coefficient payload and every gate are unchanged. Tests verify arithmetic, lineage and scope, not experimental confirmation.",
        report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    return "\n\n".join(paragraphs) + "\n" + "\n".join("- [" + row["use"] + "](" + row["url"] + ")" for row in report["primary_sources"]) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V104", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
