#!/usr/bin/env python3
"""V62 master audit after the localized Z4R ledger and GS-sector construction.

This is a new master, not an edit of V61.  It supersedes only the route-B row:
B61 (selector escape with the GS axion not exhibited) is replaced by B62,
which computes the exact fixed-point-localized Z4R anomaly ledger, proves the
matter-free nonuniversality of the Spin(4)xSpin(7) wall, and exhibits the
unique quantized Green-Schwarz axion sector as declared new action content.

The route still does not close strict G1: the post-VEV inflow deficits (-2 for
SU(3), -3 for SU(2)) are displayed but not carried by a computed mechanism,
and the saxion stabilization, Dai-Freed phase, KK determinant and UV regulator
remain absent.  Routes A60 and C are carried forward unchanged.  No
cross-route splicing.  All G1--G8 gates stay open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V62_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V62_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v62_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v61_master": ROOT / "SUSY_V61_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v62_localized_gs": ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.json",
    "v60_live_heterotic": ROOT
    / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "v59_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

CORE_KEYS = {
    "v61_master": "core_sha256",
    "v62_localized_gs": "core_sha256",
    "v60_live_heterotic": "canonical_core_sha256",
    "v59_gauged_u1r": "core_sha256",
}

EXPECTED_CORES = {
    "v61_master": "a230fda5699b3bd81552317b94733a9f537b0e9ae2a6c35f644830511fa7a810",
    "v62_localized_gs": "f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e",
    "v60_live_heterotic": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "v59_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V62_MULTIPATH_G1_FRONTIER_MASTER__V61_MASTER_AND_LOCALIZED_GS_CORE_"
    "BOUND__V61_ROUTE_B_ROW_SUPERSEDED__EXACT_PER_WALL_Z4R_LEDGER_WITH_THREE_"
    "MATCHING_CHECKS__SPIN4_SPIN7_WALL_NONUNIVERSALITY_MINUS_THREE_IS_PURE_"
    "GROUP_THEORY__UNIQUE_QUANTIZED_GS_COUPLINGS_3_1_1_3_WITH_FAITHFUL_ODD_"
    "QUARTER_PERIOD_SHIFT__POST_VEV_INFLOW_DEFICITS_MINUS_2_MINUS_3_OPEN__"
    "SAXION_STABILIZATION_DAI_FREED_KK_UV_OPEN__ROUTES_A60_AND_C_CARRIED_"
    "FORWARD__NO_CROSS_ROUTE_SPLICING__G1_TO_G8_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any], core_key: str = "core_sha256") -> str:
    body = copy.deepcopy(dict(value))
    body.pop(core_key, None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing V62 master input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    key = CORE_KEYS[name]
    stored = value.get(key)
    actual = canonical_sha(value, key)
    if stored != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def localized_gs_row(value: Mapping[str, Any]) -> dict[str, Any]:
    ledgers = value["wall_ledgers"]
    matching = value["integrated_matching"]
    nonuniversal = value["nonuniversality_theorem"]
    congruences = value["gs_congruence_system"]
    inflow = value["post_vev_inflow_deficit"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "B62",
        "name": (
            "Spin(11) gauge-Higgs route with the exact Z4R selector, localized "
            "ledger and quantized GS sector"
        ),
        "bound_core_sha256": value["core_sha256"],
        "classification": value["classification"],
        "supersedes_V61_route_id": "B61",
        "localized_ledger": {
            "A_y0_Spin10": ledgers["A_y0_Spin10"],
            "A_yL": ledgers["A_yL"],
            "matter_and_mirror_mediators_drop_out": True,
            "integrated_matching_checks": len(matching["checks"]),
            "all_matching_checks_pass": matching["all_match"],
        },
        "nonuniversality": {
            "difference_A": nonuniversal["difference_A"],
            "matter_free": True,
            "heterotic_parallel_noted": "heterotic"
            in nonuniversal["heterotic_parallel"],
        },
        "gs_sector": {
            "even_shift_impossible": congruences["even_shift_impossible"],
            "universal_yL_coupling_impossible": congruences[
                "universal_yL_coupling_impossible"
            ],
            "selected_couplings_mod_4": congruences["selected_sector_s1"],
            "all_four_wall_phases_cancel": congruences[
                "verification_all_phases_cancel"
            ],
        },
        "post_vev_inflow": {
            "required_inflow": inflow["required_inflow"],
            "status": inflow["status"],
        },
        "remaining_obligations": terminal["next_obligations"],
        "same_action_microscopic_completion": terminal["V62_G1_closed"],
        "G1_closed": terminal["V62_G1_closed"],
        "closed_gates": terminal["V62_closed_gates"],
    }


def carried_route(
    v61_master: Mapping[str, Any],
    route_id: str,
    direct: Mapping[str, Any],
    direct_core_key: str,
) -> dict[str, Any]:
    row = route_by_id(v61_master, route_id)
    if row["bound_core_sha256"] != direct[direct_core_key]:
        raise RuntimeError(f"V61 route {route_id} row/direct core mismatch")
    row["carried_forward_unchanged_from_V61_master_core"] = v61_master["core_sha256"]
    row["direct_core_rebound_in_V62"] = True
    return row


def gate_ledger(v61_master: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v61_master["gate_ledger"]}
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        if gate == "G1":
            decision = (
                "OPEN: the localized Z4R ledger is exact with three matching "
                "validations and the unique quantized GS sector (couplings "
                "3,1,1,3 mod 4, faithful quarter-period shift) cancels every "
                "wall phase, but the post-VEV inflow deficits (-2, -3), saxion "
                "stabilization, Dai-Freed phase, KK determinant and UV "
                "regulator remain absent; routes A60 and C retain their "
                "independent obstructions."
            )
        else:
            decision = (
                f"OPEN: V62 adds no same-action proof of {gate}; the prior "
                f"fail-closed frontier remains: {prior[gate]['decision']}"
            )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V62_master_closed": False,
                "decision": decision,
                "cross_route_aggregation_used": False,
            }
        )
    return rows


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v61_master = load_bound("v61_master")
    localized = load_bound("v62_localized_gs")
    live = load_bound("v60_live_heterotic")
    gauged = load_bound("v59_gauged_u1r")

    old_b = route_by_id(v61_master, "B61")
    new_b = localized_gs_row(localized)
    route_a = carried_route(v61_master, "A60", live, "canonical_core_sha256")
    route_c = carried_route(v61_master, "C", gauged, "core_sha256")
    routes = [route_a, new_b, route_c]
    gates = gate_ledger(v61_master)

    supersession = {
        "superseded_route": {
            "master_core": v61_master["core_sha256"],
            "route_id": "B61",
            "route_core": old_b["bound_core_sha256"],
            "classification": old_b["classification"],
        },
        "replacement_route": {
            "route_id": "B62",
            "route_core": localized["core_sha256"],
            "classification": new_b["classification"],
        },
        "what_is_resolved": (
            "the first V61 quantum obligation: the fixed-point-localized Z4R "
            "ledger is computed exactly and the required GS axion is exhibited "
            "with unique quantized couplings as declared new action content"
        ),
        "what_is_not_resolved": (
            "the post-VEV inflow matching with its displayed (-2,-3) deficits, "
            "saxion stabilization, the Dai-Freed phase, the KK determinant/"
            "flavor fit, the soft spectrum and a UV regulator; strict G1 stays "
            "open"
        ),
        "route_A60_core_unchanged": route_a["bound_core_sha256"],
        "route_C_core_unchanged": route_c["bound_core_sha256"],
        "V61_master_modified": False,
    }

    no_same_action = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V61_route_B_is_replaced_not_mutated": (
            supersession["superseded_route"]["route_id"] == "B61"
            and supersession["replacement_route"]["route_id"] == "B62"
            and supersession["superseded_route"]["route_core"]
            != supersession["replacement_route"]["route_core"]
            and not supersession["V61_master_modified"]
        ),
        "localized_ledger_is_bound": (
            new_b["localized_ledger"]["A_y0_Spin10"] == "1/2"
            and new_b["localized_ledger"]["A_yL"]
            == {"SU2_L": "-5/2", "SU2_R": "-5/2", "SO7": "1/2"}
            and new_b["localized_ledger"]["integrated_matching_checks"] == 3
            and new_b["localized_ledger"]["all_matching_checks_pass"]
        ),
        "nonuniversality_minus_three_is_bound": (
            new_b["nonuniversality"]["difference_A"] == "-3"
            and new_b["nonuniversality"]["matter_free"]
        ),
        "gs_sector_is_bound_and_quantized": (
            new_b["gs_sector"]["even_shift_impossible"]
            and new_b["gs_sector"]["universal_yL_coupling_impossible"]
            and new_b["gs_sector"]["selected_couplings_mod_4"]
            == {"Spin10@y0": 3, "SU2_L@yL": 1, "SU2_R@yL": 1, "SO7@yL": 3}
            and new_b["gs_sector"]["all_four_wall_phases_cancel"]
        ),
        "inflow_deficits_remain_open_not_assumed": (
            new_b["post_vev_inflow"]["required_inflow"]
            == {"SU3": "-2", "SU2_L": "-3"}
            and new_b["post_vev_inflow"]["status"] == "OPEN"
        ),
        "five_remaining_obligations_bound": len(new_b["remaining_obligations"]) == 5,
        "route_A60_is_directly_rebound_unchanged": (
            route_a["bound_core_sha256"] == EXPECTED_CORES["v60_live_heterotic"]
            and route_a["direct_core_rebound_in_V62"]
        ),
        "route_C_is_directly_rebound_unchanged": (
            route_c["bound_core_sha256"] == EXPECTED_CORES["v59_gauged_u1r"]
            and route_c["direct_core_rebound_in_V62"]
        ),
        "no_route_has_same_action_microscopic_completion": no_same_action,
        "cross_route_splicing_is_forbidden": True,
        "all_G1_to_G8_gates_remain_open": all(
            row["status"] == "OPEN"
            and not row["V62_master_closed"]
            and not row["cross_route_aggregation_used"]
            for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v62_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "After the exact localized Z4R ledger and the quantized GS sector "
            "on the Spin(11) route, does any route close strict G1 in one action?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_master_core": v61_master["core_sha256"],
            "V60_master_core_via_parent": v61_master["lineage"][
                "parent_master_core"
            ],
            "supersession": supersession,
        },
        "upstream_status": {
            "V61_master": v61_master["status"],
            "V62_localized_gs": localized["status"],
            "V60_live_heterotic": live["status"],
            "V59_gauged_U1R": gauged["status"],
        },
        "route_matrix": routes,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action. A Spin(11) "
                "Z4R selector with its GS sector, conditional heterotic "
                "charges and a gauged-U1R lattice cannot be conjoined across "
                "inequivalent actions."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_specific_obstructions_remain_scoped": True,
        },
        "comparison_conclusion": {
            "heterotic": v61_master["comparison_conclusion"]["heterotic"],
            "Spin11": (
                "The quantum frontier advanced one full step: the localized "
                "ledger that V61 could only name is now an exact, triply "
                "validated computation, and the GS axion it demanded exists "
                "with unique quantized couplings.  The route is now blocked by "
                "the post-VEV inflow deficits (-2,-3), the saxion potential, "
                "Dai-Freed, the KK determinant and the UV completion."
            ),
            "gauged_U1R": v61_master["comparison_conclusion"]["gauged_U1R"],
            "frontier": (
                "Route B remains the most advanced; its next obligation, the "
                "post-VEV inflow computation, is now a pair of exact target "
                "numbers rather than an unspecified deficit.  Routes A60 and C "
                "retain their separately certified obstructions."
            ),
        },
        "strict_master_decision": {
            "localized_ledger_computed": True,
            "gs_sector_exhibited": True,
            "same_action_microscopic_completion_found": False,
            "V62_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The Spin(11) route now has an exact localized Z4R ledger, a "
                "matter-free nonuniversality theorem at the Spin(4)xSpin(7) "
                "wall, and a unique quantized GS sector that cancels every "
                "computed wall phase.  The new sector is declared candidate "
                "action content, not a discovery.  The post-VEV inflow, saxion "
                "stabilization, Dai-Freed, KK and UV data are still absent, so "
                "no same-action route closes G1, and G1--G8 remain open."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_literature_claim": True,
            "route_primary_sources_remain_in_their_bound_artifacts": True,
        },
        "source_manifest": source_manifest(),
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise AssertionError("V62 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V62 multipath integrity failures: {failed}")
    decision = report["strict_master_decision"]
    if decision["same_action_microscopic_completion_found"]:
        raise AssertionError("V62 master promoted an absent completion")
    if decision["V62_G1_closed"] or decision["closed_gates"]:
        raise AssertionError("V62 master promoted a gate")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("V62 master spliced inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V62 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    a = rows["A60"]
    b = rows["B62"]
    c = rows["C"]
    supersession = report["lineage"]["supersession"]
    ledger = b["localized_ledger"]
    gs = b["gs_sector"]
    inflow = b["post_vev_inflow"]
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    obligations = "\n".join(f"- {item}" for item in b["remaining_obligations"])
    return f"""# V62 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**The Spin(11) route's localized Z4R anomaly ledger is now an exact, triply
validated computation, and the Green-Schwarz axion it demanded exists with
unique quantized couplings.  The post-VEV inflow deficits are exact open
numbers.  G1--G8 remain OPEN.**

This distinct V62 master supersedes only the V61 route-B row.  It binds the
V61 master and directly rebinds the unchanged A60 and C cores.  No route-local
gain is spliced into another action.

## Exact supersession

```text
V61 route B: {supersession['superseded_route']['route_core']}
V62 route B: {supersession['replacement_route']['route_core']}
V61 master:  {supersession['superseded_route']['master_core']}
```

## The ledger and the sector

```text
A(Spin10)|y=0 = {ledger['A_y0_Spin10']}
A|y=L         = {ledger['A_yL']}
matching      = {ledger['integrated_matching_checks']} independent checks, all pass
nonuniversality at y=L = {b['nonuniversality']['difference_A']} (matter-free group theory)
GS couplings  = {gs['selected_couplings_mod_4']} (unique mod 4, faithful quarter-period shift)
wall phases   = all four cancel: {gs['all_four_wall_phases_cancel']}
```

With the unique V61 charges the matter sixteens and all mirror mediators drop
out of the localized ledger.  An even axion shift and a universal y=L coupling
are both impossible; the per-factor quantized sector is the unique cure, and
it is declared new route-B62 action content.

Remaining route-B obligations:

{obligations}

The sharpest of these is now numeric: the post-VEV inflow must carry exactly
`SU3: {inflow['required_inflow']['SU3']}` and `SU2_L: {inflow['required_inflow']['SU2_L']}`; its status is `{inflow['status']}`.

## Carried routes

Route A60 remains `{a['classification']}`: the live regeneration rejected the
Kappl candidate in the tested corrected Abelian basis without proving a
universal heterotic no-go.

Route C remains `{c['classification']}`: its integrated lattice and 270-singlet
parity solution pass, but the existing bulk GS direction fails at GG,
flipped-GG, and Pati--Salam fixed points.

## No cross-route splicing

{report['cross_route_composition_rule']['logical_rule']}

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Fail-closed decision

{report['strict_master_decision']['honest_outcome']}

Primary-source provenance remains in the canonically bound route artifacts;
this master adds no new literature claim.

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()

    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V62 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V62 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V62 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
