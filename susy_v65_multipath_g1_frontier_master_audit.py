#!/usr/bin/env python3
"""V65 master audit: conditional viability after the orphan lifting classification.

This is a new master, not an edit of V64.  It supersedes only the route-B row:
B64 (action rejected pending a lifting sector) is replaced by B65, which
closes six GUT-scale lifting channels exactly, constructs the gravitino-scale
Giudice-Masiero lift shared with mu, proves the baryon-safe decay-portal
theorem, and verifies that the V62 GS couplings cancel the orphan-included IR
ledger with no Wess-Zumino term.

The consolidated theory card is corrected accordingly: the V63 forced-WZ line
is gone, the orphan sector is explicit, and the card remains a candidate.
G1 is not closed and cannot be closed by declaration: the soft spectrum,
unification numerics, cosmology, Dai-Freed phase, KK determinant and UV
regulator are absent.  Routes A60 and C are carried forward unchanged.  No
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
JSON_PATH = ROOT / "SUSY_V65_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V65_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v65_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v64_master": ROOT / "SUSY_V64_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v65_orphan_lift": ROOT
    / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json",
    "v60_live_heterotic": ROOT
    / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "v59_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

CORE_KEYS = {
    "v64_master": "core_sha256",
    "v65_orphan_lift": "core_sha256",
    "v60_live_heterotic": "canonical_core_sha256",
    "v59_gauged_u1r": "core_sha256",
}

EXPECTED_CORES = {
    "v64_master": "2840d49f02b4eafd75ca856657ea938e0543e35e7e5c8dab5760f9a908b63e16",
    "v65_orphan_lift": "b87696403fb46c4a6b044be8abe58dd5f82b63a83a58fff262a6f00bdd6914ae",
    "v60_live_heterotic": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "v59_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V65_MULTIPATH_G1_FRONTIER_MASTER__V64_MASTER_AND_ORPHAN_LIFT_CORE_BOUND__"
    "V64_ROUTE_B_ROW_SUPERSEDED__SIX_GUT_SCALE_LIFT_CHANNELS_CLOSED_EXACTLY__"
    "GRAVITINO_SCALE_GM_LIFT_SHARED_WITH_MU__BARYON_SAFE_PORTALS_FORCED_BY_X_"
    "ARITHMETIC__GS_IR_CLOSURE_WITH_ORPHANS_EXACT_NO_WZ__ACTION_UPGRADED_"
    "FROM_REJECTED_TO_CONDITIONALLY_VIABLE__THEORY_CARD_CORRECTED_NO_WZ_"
    "LINE__UNIFICATION_COSMOLOGY_SOFT_DAI_FREED_KK_UV_OPEN__ROUTES_A60_AND_C_"
    "CARRIED_FORWARD__NO_CROSS_ROUTE_SPLICING__G1_TO_G8_OPEN"
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
        raise RuntimeError(f"missing V65 master input: {path.name}")
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


def orphan_lift_row(value: Mapping[str, Any]) -> dict[str, Any]:
    classification = value["gut_scale_channel_classification"]
    lift = value["gravitino_scale_lift"]
    portals = value["decay_portal_theorem"]
    closure = value["gs_ir_closure"]
    shift = value["unification_shift"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "B65",
        "name": (
            "Spin(11) gauge-Higgs route with Z4R selector, GS sector, "
            "surviving orphan pair lifted at the gravitino scale"
        ),
        "bound_core_sha256": value["core_sha256"],
        "classification": value["classification"],
        "supersedes_V64_route_id": "B64",
        "gut_scale_channels": {
            "count": len(classification["branches"]),
            "all_closed": classification["all_branches_closed"],
            "ids": [row["id"] for row in classification["branches"]],
        },
        "gravitino_lift": {
            "orphan_pair_charge": lift["orphan_pair_charge"],
            "same_gm_class_as_mu": lift["same_gm_class_as_mu"],
            "r_parity_survives": lift["r_parity"]["orphan_fermion_g2_phase"] == -1,
        },
        "decay_portals": {
            "orphan": portals["orphan_solutions"],
            "anti_orphan": portals["orphanbar_solutions"],
            "unique_and_baryon_safe": portals[
                "portal_uniqueness_channel_independent"
            ],
        },
        "gs_ir_closure": {
            "ledger": closure["orphan_included_IR_ledger"],
            "closes_exactly": closure["closes_exactly"],
            "wz_term": "NONE",
        },
        "unification_shift": shift["Delta_b"],
        "action_status": terminal["action_status"],
        "remaining_obligations": terminal["next_obligations"],
        "same_action_microscopic_completion": terminal["V65_G1_closed"],
        "G1_closed": terminal["V65_G1_closed"],
        "closed_gates": terminal["V65_closed_gates"],
    }


def carried_route(
    v64_master: Mapping[str, Any],
    route_id: str,
    direct: Mapping[str, Any],
    direct_core_key: str,
) -> dict[str, Any]:
    row = route_by_id(v64_master, route_id)
    if row["bound_core_sha256"] != direct[direct_core_key]:
        raise RuntimeError(f"V64 route {route_id} row/direct core mismatch")
    row["carried_forward_unchanged_from_V64_master_core"] = v64_master["core_sha256"]
    row["direct_core_rebound_in_V65"] = True
    return row


def consolidated_theory_card() -> dict[str, Any]:
    """The corrected candidate card after the V64 retraction and V65 lift."""

    return {
        "name": (
            "5D SUSY Spin(11) gauge-Higgs grand unification on S1/(Z2xZ2') "
            "with an exact Z4R selector, a two-wall Green-Schwarz sector, and "
            "a gravitino-scale orphan pair"
        ),
        "action_inventory": [
            "bulk: 5D N=1 Spin(11) super-Yang-Mills on an interval with projectors P0=diag(+^10,-), P1=diag(+^4,-^7)",
            "bulk: mirror-paired 32 mediator hypermultiplets (superalgebra R charges (1,1))",
            "bulk: one axion multiplet with faithful quarter-period Z4R shift and wall couplings (3,1,1,3) mod 4",
            "y=0 wall: three matter 16s at R charge 1 (Yukawas via the mediator Schur kernel)",
            "y=0 wall: rank sector C(16,0)+Cbar(16bar,0)+T(10,2)+S(1,2) with M_T=0 forced and <S>=0 exact",
            "symmetry: Z4R = order-four subgroup of the orbifold-preserved SU(2)R Cartan; g^2 acts as exact R parity",
            "IR remnant: the vectorlike orphan pair (3,2,+1/6)+(3bar,2,-1/6) at m_3/2 with baryon-safe portals",
        ],
        "explicitly_absent": [
            "no Wess-Zumino inflow term: the V63 claim is retracted and the corrected ledger needs none",
            "no GUT-scale orphan mass: excluded in all six classified channels",
        ],
        "certified_passes": [
            "exactly two weak Higgs doublet zero modes from the 55-generator projector enumeration",
            "rank breaking with full-rank 5+5bar mass, det = -lambda lambdabar v^2, M_T not needed",
            "unique Z4R selector class from the exhaustive 89999-assignment scan (V61)",
            "all dimension-five proton operators forbidden to all orders in W and at dimension five in K; mu doubly forbidden",
            "exact per-wall localized Z4R ledger with three integrated-matching validations (V62)",
            "unique quantized GS wall couplings (3,1,1,3) mod 4 with faithful odd quarter-period shift (V62)",
            "exact N x (N+1) null-mode theorem: twelve Q-type orphan components survive (V64)",
            "orphan-included IR ledger (1,-2) equals the wall sum and is cancelled by the V62 couplings with no WZ term (V64+V65)",
            "six GUT-scale lifting channels closed exactly; the orphan bilinear is charge-zero GM class with mu (V65)",
            "unique baryon-safe decay portals (3,3) and (-5,-1) forced by X neutrality (V65)",
            "exact R parity survives <W> != 0: stable LSP, decaying orphans",
        ],
        "open_obligations": [
            "unification numerics with Delta b = (2,3,1/5) at m_3/2",
            "orphan lifetimes, relic behavior, collider limits",
            "SUSY-breaking sector fixing mu, B-mu and the orphan mass together",
            "saxion stabilization; Dai-Freed phase with the corrected spectrum",
            "exact KK determinant, realistic flavor fit, UV regulator",
            "G2-G8: Wilsonian action, vacuum/Hessian, cosmology, precision running, proton lifetime number, CKM/PMNS likelihood",
        ],
        "honesty_clause": (
            "this card is the maximal candidate assembled from one action; "
            "every listed pass is bound by a hash-pinned audit, every gap is "
            "listed, the V63 retraction is incorporated, and the theory is "
            "not claimed complete"
        ),
    }


def gate_ledger(v64_master: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v64_master["gate_ledger"]}
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        if gate == "G1":
            decision = (
                "OPEN: the V64 rejection is upgraded to conditional viability. "
                "Six GUT-scale lifting channels are closed exactly; the orphan "
                "pair is lifted at m_3/2 by the same GM mechanism as mu, "
                "decays through baryon-safe portals, and the V62 GS couplings "
                "cancel the corrected IR ledger with no WZ term.  The soft "
                "spectrum, unification numerics, cosmology, Dai-Freed, KK "
                "determinant and UV regulator remain absent; routes A60 and C "
                "retain their independent obstructions."
            )
        else:
            decision = (
                f"OPEN: V65 adds no same-action proof of {gate}; the prior "
                f"fail-closed frontier remains: {prior[gate]['decision']}"
            )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V65_master_closed": False,
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
    v64_master = load_bound("v64_master")
    lift = load_bound("v65_orphan_lift")
    live = load_bound("v60_live_heterotic")
    gauged = load_bound("v59_gauged_u1r")

    old_b = route_by_id(v64_master, "B64")
    new_b = orphan_lift_row(lift)
    route_a = carried_route(v64_master, "A60", live, "canonical_core_sha256")
    route_c = carried_route(v64_master, "C", gauged, "core_sha256")
    routes = [route_a, new_b, route_c]
    gates = gate_ledger(v64_master)
    card = consolidated_theory_card()

    supersession = {
        "superseded_route": {
            "master_core": v64_master["core_sha256"],
            "route_id": "B64",
            "route_core": old_b["bound_core_sha256"],
            "classification": old_b["classification"],
        },
        "replacement_route": {
            "route_id": "B65",
            "route_core": lift["core_sha256"],
            "classification": new_b["classification"],
        },
        "what_is_resolved": (
            "the V64 repair question: no GUT-scale lift exists in any "
            "classified channel, but the charge-zero orphan bilinear is lifted "
            "at the gravitino scale by the same mechanism as mu, with unique "
            "baryon-safe portals and an exact GS-IR closure without WZ"
        ),
        "what_is_not_resolved": (
            "unification numerics with the exact Delta b, orphan cosmology and "
            "collider limits, the SUSY-breaking sector, saxion stabilization, "
            "Dai-Freed, the KK determinant/flavor fit and a UV regulator; "
            "strict G1 stays open"
        ),
        "route_A60_core_unchanged": route_a["bound_core_sha256"],
        "route_C_core_unchanged": route_c["bound_core_sha256"],
        "V64_master_modified": False,
    }

    no_same_action = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V64_route_B_is_replaced_not_mutated": (
            supersession["superseded_route"]["route_id"] == "B64"
            and supersession["replacement_route"]["route_id"] == "B65"
            and supersession["superseded_route"]["route_core"]
            != supersession["replacement_route"]["route_core"]
            and not supersession["V64_master_modified"]
        ),
        "six_channels_closed_and_bound": (
            new_b["gut_scale_channels"]["count"] == 6
            and new_b["gut_scale_channels"]["all_closed"]
            and new_b["gut_scale_channels"]["ids"]
            == ["B1", "B2", "B3", "B4", "B5", "B6"]
        ),
        "gm_lift_and_r_parity_bound": (
            new_b["gravitino_lift"]["orphan_pair_charge"] == 0
            and new_b["gravitino_lift"]["same_gm_class_as_mu"]
            and new_b["gravitino_lift"]["r_parity_survives"]
        ),
        "portals_unique_and_baryon_safe": (
            new_b["decay_portals"]["orphan"] == [[3, 3]]
            and sorted(new_b["decay_portals"]["anti_orphan"])
            == [[-5, -1], [-1, -5]]
            and new_b["decay_portals"]["unique_and_baryon_safe"]
        ),
        "gs_ir_closure_bound_no_wz": (
            new_b["gs_ir_closure"]["ledger"] == {"A3": 1, "A2": -2}
            and new_b["gs_ir_closure"]["closes_exactly"]
            and new_b["gs_ir_closure"]["wz_term"] == "NONE"
        ),
        "unification_shift_bound": new_b["unification_shift"]
        == {"b3": "2", "b2": "3", "b1_GUT_normalized": "1/5"},
        "action_upgraded_not_completed": (
            "conditionally viable" in new_b["action_status"]
            and not new_b["G1_closed"]
        ),
        "theory_card_corrected": (
            len(card["explicitly_absent"]) == 2
            and any("Wess-Zumino" in item for item in card["explicitly_absent"])
            and len(card["certified_passes"]) == 11
            and len(card["open_obligations"]) == 6
            and "not claimed complete" in card["honesty_clause"]
        ),
        "route_A60_is_directly_rebound_unchanged": (
            route_a["bound_core_sha256"] == EXPECTED_CORES["v60_live_heterotic"]
            and route_a["direct_core_rebound_in_V65"]
        ),
        "route_C_is_directly_rebound_unchanged": (
            route_c["bound_core_sha256"] == EXPECTED_CORES["v59_gauged_u1r"]
            and route_c["direct_core_rebound_in_V65"]
        ),
        "no_route_has_same_action_microscopic_completion": no_same_action,
        "cross_route_splicing_is_forbidden": True,
        "all_G1_to_G8_gates_remain_open": all(
            row["status"] == "OPEN"
            and not row["V65_master_closed"]
            and not row["cross_route_aggregation_used"]
            for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v65_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "After the orphan lifting classification, does any route close "
            "strict G1 in one action, and what is the corrected candidate "
            "theory?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_master_core": v64_master["core_sha256"],
            "V63_master_core_via_parent": v64_master["lineage"][
                "parent_V63_master_core"
            ],
            "supersession": supersession,
        },
        "upstream_status": {
            "V64_master": v64_master["status"],
            "V65_orphan_lift": lift["status"],
            "V60_live_heterotic": live["status"],
            "V59_gauged_U1R": gauged["status"],
        },
        "route_matrix": routes,
        "consolidated_theory_card": card,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action. The "
                "Spin(11) candidate with its GS sector and orphan lift, "
                "conditional heterotic charges and a gauged-U1R lattice "
                "cannot be conjoined across inequivalent actions."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_specific_obstructions_remain_scoped": True,
        },
        "comparison_conclusion": {
            "heterotic": v64_master["comparison_conclusion"]["heterotic"],
            "Spin11": (
                "The V64 crisis is resolved honestly: the orphans cannot be "
                "lifted at the GUT scale in any classified channel, but they "
                "are exactly the charge-zero class that the mu mechanism "
                "already lifts at m_3/2, with baryon-safe portals and an "
                "exact GS-IR closure.  The route now stands or falls on "
                "numerics: unification with Delta b = (2,3,1/5), orphan "
                "cosmology, and the soft spectrum."
            ),
            "gauged_U1R": v64_master["comparison_conclusion"]["gauged_U1R"],
            "frontier": (
                "Route B remains the live candidate; its next obligation is "
                "the first fully numerical one in the program: the two-loop "
                "unification test with the exact orphan Delta b."
            ),
        },
        "strict_master_decision": {
            "gut_scale_lift_excluded": True,
            "gravitino_scale_lift_constructed": True,
            "same_action_microscopic_completion_found": False,
            "V65_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The G1 gate is not closed, and the program does not close "
                "gates by declaration.  What V65 establishes exactly: no "
                "GUT-scale orphan mass exists in the six classified channels; "
                "the orphan pair is lifted at the gravitino scale by the same "
                "spontaneous R breaking that generates mu; its decay portals "
                "are unique and baryon-safe; and the corrected IR ledger is "
                "cancelled by the V62 GS sector with no WZ term.  The action "
                "is conditionally viable with sharp numerical tests ahead, "
                "and G1--G8 remain open."
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
        raise AssertionError("V65 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V65 multipath integrity failures: {failed}")
    decision = report["strict_master_decision"]
    if decision["same_action_microscopic_completion_found"]:
        raise AssertionError("V65 master promoted an absent completion")
    if decision["V65_G1_closed"] or decision["closed_gates"]:
        raise AssertionError("V65 master promoted a gate")
    if decision["complete_theory"]:
        raise AssertionError("V65 master overclaimed a complete theory")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("V65 master spliced inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V65 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    a = rows["A60"]
    b = rows["B65"]
    c = rows["C"]
    supersession = report["lineage"]["supersession"]
    card = report["consolidated_theory_card"]
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    inventory = "\n".join(f"- {item}" for item in card["action_inventory"])
    absent = "\n".join(f"- {item}" for item in card["explicitly_absent"])
    passes = "\n".join(f"- {item}" for item in card["certified_passes"])
    opens = "\n".join(f"- {item}" for item in card["open_obligations"])
    obligations = "\n".join(f"- {item}" for item in b["remaining_obligations"])
    return f"""# V65 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**The V64 rejection is resolved honestly: no GUT-scale orphan mass exists in
any classified channel, but the orphan pair is exactly the charge-zero class
that the mu mechanism lifts at the gravitino scale, with unique baryon-safe
decay portals and an exact GS-IR closure without any Wess-Zumino term.  The
action is upgraded to conditionally viable.  G1 is not closed and cannot be
closed by declaration.  G1--G8 remain OPEN.**

This distinct V65 master supersedes only the V64 route-B row.  It binds the
V64 master and directly rebinds the unchanged A60 and C cores.  No route-local
gain is spliced into another action.

## Exact supersession

```text
V64 route B: {supersession['superseded_route']['route_core']}
V65 route B: {supersession['replacement_route']['route_core']}
V64 master:  {supersession['superseded_route']['master_core']}
```

## The resolution in numbers

```text
GUT-scale channels closed:  {b['gut_scale_channels']['ids']}
orphan bilinear charge:     {b['gravitino_lift']['orphan_pair_charge']}  (same GM class as mu)
decay portals:              orphan {b['decay_portals']['orphan']}, anti-orphan {b['decay_portals']['anti_orphan']}
orphan-included IR ledger:  {b['gs_ir_closure']['ledger']}  cancelled exactly, WZ term: {b['gs_ir_closure']['wz_term']}
unification shift:          Delta b = {b['unification_shift']}
action status:              {b['action_status']}
```

Remaining route-B obligations:

{obligations}

## Corrected candidate theory card

**{card['name']}**

Action inventory:

{inventory}

Explicitly absent (corrected after V64):

{absent}

Certified passes (each bound by a hash-pinned audit):

{passes}

Open obligations:

{opens}

{card['honesty_clause']}

## Carried routes

Route A60 remains `{a['classification']}`.

Route C remains `{c['classification']}`.

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
            raise RuntimeError("generated V65 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V65 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V65 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
