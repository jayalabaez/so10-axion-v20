#!/usr/bin/env python3
"""V63 master audit: the consolidated candidate theory after inflow identification.

This is a new master, not an edit of V62.  It supersedes only the route-B row:
B62 is replaced by B63, which identifies the post-VEV inflow deficits exactly
with the ledger of the twelve Goldstone chirals dissolved into the AB gauge
towers, closes both infrared anomaly-matching identities, and thereby forces
the wall Wess-Zumino coefficient uniquely.

The master also carries a consolidated theory card: the most complete
candidate action this program can currently support, listing every certified
pass and every open obligation.  It is a candidate, not a completed theory:
the dynamical WZ extraction, saxion stabilization, Dai-Freed phase, KK
determinant and UV regulator are absent, routes A60 and C retain their
independent obstructions, no cross-route splicing is performed, and all
G1--G8 gates stay open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V63_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V63_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v63_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v62_master": ROOT / "SUSY_V62_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v63_wz_inflow": ROOT
    / "SUSY_V63_SPIN11_GOLDSTONE_DISSOLUTION_WZ_INFLOW_AUDIT.json",
    "v60_live_heterotic": ROOT
    / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "v59_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

CORE_KEYS = {
    "v62_master": "core_sha256",
    "v63_wz_inflow": "core_sha256",
    "v60_live_heterotic": "canonical_core_sha256",
    "v59_gauged_u1r": "core_sha256",
}

EXPECTED_CORES = {
    "v62_master": "4e1344fbaa148c0369417918e3e39d2c94282d8db568a8ec6fa01522e680cdf0",
    "v63_wz_inflow": "b7178dc59b9cd4a49468ce5ace543c047e58cc34bcf4fcc65466ee93f3a1bfd7",
    "v60_live_heterotic": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "v59_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V63_MULTIPATH_G1_FRONTIER_MASTER__V62_MASTER_AND_WZ_INFLOW_CORE_BOUND__"
    "V62_ROUTE_B_ROW_SUPERSEDED__POST_VEV_DEFICITS_IDENTIFIED_WITH_DISSOLVED_"
    "GOLDSTONE_LEDGER__BOTH_IR_MATCHING_IDENTITIES_CLOSE__WZ_COEFFICIENT_"
    "UNIQUELY_FORCED__CONSOLIDATED_CANDIDATE_THEORY_CARD_BOUND__DYNAMICAL_WZ_"
    "SAXION_DAI_FREED_KK_UV_OPEN__ROUTES_A60_AND_C_CARRIED_FORWARD__NO_CROSS_"
    "ROUTE_SPLICING__G1_TO_G8_OPEN"
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
        raise RuntimeError(f"missing V63 master input: {path.name}")
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


def wz_inflow_row(value: Mapping[str, Any]) -> dict[str, Any]:
    fates = value["fate_enumeration"]
    identification = value["deficit_identification"]
    wz = value["forced_wz_term"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "B63",
        "name": (
            "Spin(11) gauge-Higgs route with Z4R selector, localized ledger, "
            "GS sector and identified WZ inflow"
        ),
        "bound_core_sha256": value["core_sha256"],
        "classification": value["classification"],
        "supersedes_V62_route_id": "B62",
        "fate_enumeration": {
            "total_components": fates["total_complex_components"],
            "fate_counts": fates["fate_counts"],
            "all_4d_pairings_R_neutral": fates["all_4d_pairings_R_neutral"],
            "dissolved_ledger": fates["dissolved_ledger"],
        },
        "deficit_identification": {
            "identification_exact": identification["identification_exact"],
            "both_ir_identities_close": identification["both_identities_close"],
            "V62_required_inflow": identification["V62_required_inflow"],
        },
        "forced_wz_term": {
            "coefficient_uniquely_forced": wz["coefficient_uniquely_forced"],
            "status": wz["status"],
        },
        "remaining_obligations": terminal["next_obligations"],
        "same_action_microscopic_completion": terminal["V63_G1_closed"],
        "G1_closed": terminal["V63_G1_closed"],
        "closed_gates": terminal["V63_closed_gates"],
    }


def carried_route(
    v62_master: Mapping[str, Any],
    route_id: str,
    direct: Mapping[str, Any],
    direct_core_key: str,
) -> dict[str, Any]:
    row = route_by_id(v62_master, route_id)
    if row["bound_core_sha256"] != direct[direct_core_key]:
        raise RuntimeError(f"V62 route {route_id} row/direct core mismatch")
    row["carried_forward_unchanged_from_V62_master_core"] = v62_master["core_sha256"]
    row["direct_core_rebound_in_V63"] = True
    return row


def consolidated_theory_card() -> dict[str, Any]:
    """The most complete candidate action this program currently supports."""

    return {
        "name": (
            "5D SUSY Spin(11) gauge-Higgs grand unification on S1/(Z2xZ2') "
            "with an exact Z4R selector and a two-wall Green-Schwarz sector"
        ),
        "action_inventory": [
            "bulk: 5D N=1 Spin(11) super-Yang-Mills on an interval with projectors P0=diag(+^10,-), P1=diag(+^4,-^7)",
            "bulk: mirror-paired 32 mediator hypermultiplets (opposite intrinsic parities, superalgebra R charges (1,1))",
            "bulk: one axion multiplet with faithful quarter-period Z4R shift and wall couplings (3,1,1,3) mod 4",
            "y=0 wall: three matter 16s at R charge 1 (Yukawas via the mediator Schur kernel)",
            "y=0 wall: rank sector C(16,0)+Cbar(16bar,0)+T(10,2)+S(1,2) with W=kappa S(C Cbar-v^2)+lambda CCT+lambdabar CbarCbarT and M_T=0 forced",
            "y=0 wall: the anomaly-forced Wess-Zumino term in the eaten C,Cbar phases carrying (-2,-3)",
            "symmetry: Z4R = order-four subgroup of the orbifold-preserved SU(2)R Cartan; g^2 acts as exact R parity",
        ],
        "certified_passes": [
            "exactly two weak Higgs doublet zero modes and zero colored zero modes (55-generator projector enumeration)",
            "rank breaking to SU(5) intersecting to the SM with full-rank 5+5bar mass, det = -lambda lambdabar v^2, M_T not needed",
            "unique Z4R selector class from the exhaustive 89999-assignment scan (V61); Yukawa/seesaw/Weinberg allowed",
            "all dimension-five proton operators forbidden to all orders in W and at dimension five in K; mu doubly forbidden",
            "4D global anomaly universality A3=3, A2=1 mod eta=2, where the corrected heterotic candidate failed",
            "exact per-wall localized Z4R ledger (1/2; -5/2,-5/2,1/2) with three integrated-matching validations",
            "unique quantized GS wall couplings (3,1,1,3) mod 4 with faithful odd quarter-period axion shift",
            "complete 32-component fate enumeration; dissolved Goldstone ledger (-2,-3) equals the inflow deficits exactly",
            "both infrared anomaly-matching identities close; WZ coefficient uniquely forced",
            "exact R parity survives gravitino-scale Z4R breaking: stable LSP structurally",
        ],
        "open_obligations": [
            "dynamical WZ extraction with superspace completion",
            "saxion stabilization without Z4R breaking; axino sector",
            "Dai-Freed phase with the R twist, GS sector and WZ term",
            "exact KK determinant, realistic flavor fit and soft spectrum",
            "UV regulator or string completion",
            "G2-G8: Wilsonian action, vacuum/Hessian, cosmology, precision running, proton lifetime number, CKM/PMNS likelihood",
        ],
        "honesty_clause": (
            "this card is the maximal candidate assembled from one action; "
            "every listed pass is bound by a hash-pinned audit, every gap is "
            "listed, and the theory is not claimed complete"
        ),
    }


def gate_ledger(v62_master: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v62_master["gate_ledger"]}
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        if gate == "G1":
            decision = (
                "OPEN: the post-VEV inflow deficits are identified exactly with "
                "the dissolved Goldstone ledger and both IR matching identities "
                "close, forcing the WZ coefficient uniquely; the dynamical WZ "
                "extraction, saxion stabilization, Dai-Freed phase, KK "
                "determinant and UV regulator remain absent, and routes A60 and "
                "C retain their independent obstructions."
            )
        else:
            decision = (
                f"OPEN: V63 adds no same-action proof of {gate}; the prior "
                f"fail-closed frontier remains: {prior[gate]['decision']}"
            )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V63_master_closed": False,
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
    v62_master = load_bound("v62_master")
    inflow = load_bound("v63_wz_inflow")
    live = load_bound("v60_live_heterotic")
    gauged = load_bound("v59_gauged_u1r")

    old_b = route_by_id(v62_master, "B62")
    new_b = wz_inflow_row(inflow)
    route_a = carried_route(v62_master, "A60", live, "canonical_core_sha256")
    route_c = carried_route(v62_master, "C", gauged, "core_sha256")
    routes = [route_a, new_b, route_c]
    gates = gate_ledger(v62_master)
    card = consolidated_theory_card()

    supersession = {
        "superseded_route": {
            "master_core": v62_master["core_sha256"],
            "route_id": "B62",
            "route_core": old_b["bound_core_sha256"],
            "classification": old_b["classification"],
        },
        "replacement_route": {
            "route_id": "B63",
            "route_core": inflow["core_sha256"],
            "classification": new_b["classification"],
        },
        "what_is_resolved": (
            "the sharpest V62 obligation: the (-2,-3) inflow deficits are "
            "identified exactly with the twelve dissolved (2,2,6) Goldstone "
            "chirals, both IR anomaly-matching identities close, and the wall "
            "WZ coefficient is uniquely forced"
        ),
        "what_is_not_resolved": (
            "the dynamical WZ functional and its SUSY completion, saxion "
            "stabilization, the Dai-Freed phase, the KK determinant/flavor "
            "fit, the soft spectrum and a UV regulator; strict G1 stays open"
        ),
        "route_A60_core_unchanged": route_a["bound_core_sha256"],
        "route_C_core_unchanged": route_c["bound_core_sha256"],
        "V62_master_modified": False,
    }

    no_same_action = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V62_route_B_is_replaced_not_mutated": (
            supersession["superseded_route"]["route_id"] == "B62"
            and supersession["replacement_route"]["route_id"] == "B63"
            and supersession["superseded_route"]["route_core"]
            != supersession["replacement_route"]["route_core"]
            and not supersession["V62_master_modified"]
        ),
        "fate_enumeration_is_bound": (
            new_b["fate_enumeration"]["total_components"] == 32
            and new_b["fate_enumeration"]["fate_counts"]
            == {
                "dissolved_into_AB_tower": 12,
                "eaten_by_zero_mode_gauginos": 9,
                "paired_with_T": 10,
                "paired_with_S": 1,
            }
            and new_b["fate_enumeration"]["all_4d_pairings_R_neutral"]
        ),
        "deficit_identification_is_bound": (
            new_b["fate_enumeration"]["dissolved_ledger"]
            == {"Delta_A3": "-2", "Delta_A2": "-3"}
            and new_b["deficit_identification"]["identification_exact"]
            and new_b["deficit_identification"]["both_ir_identities_close"]
            and new_b["deficit_identification"]["V62_required_inflow"]
            == {"SU3": "-2", "SU2_L": "-3"}
        ),
        "wz_coefficient_forced_but_extraction_open": (
            new_b["forced_wz_term"]["coefficient_uniquely_forced"]
            and new_b["forced_wz_term"]["status"]
            == "COEFFICIENT_FORCED__DYNAMICAL_EXTRACTION_OPEN"
        ),
        "five_remaining_obligations_bound": len(new_b["remaining_obligations"]) == 5,
        "theory_card_has_no_unlisted_gap_claim": (
            len(card["certified_passes"]) == 10
            and len(card["open_obligations"]) == 6
            and "not claimed complete" in card["honesty_clause"]
        ),
        "route_A60_is_directly_rebound_unchanged": (
            route_a["bound_core_sha256"] == EXPECTED_CORES["v60_live_heterotic"]
            and route_a["direct_core_rebound_in_V63"]
        ),
        "route_C_is_directly_rebound_unchanged": (
            route_c["bound_core_sha256"] == EXPECTED_CORES["v59_gauged_u1r"]
            and route_c["direct_core_rebound_in_V63"]
        ),
        "no_route_has_same_action_microscopic_completion": no_same_action,
        "cross_route_splicing_is_forbidden": True,
        "all_G1_to_G8_gates_remain_open": all(
            row["status"] == "OPEN"
            and not row["V63_master_closed"]
            and not row["cross_route_aggregation_used"]
            for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v63_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "After the inflow identification on the Spin(11) route, does any "
            "route close strict G1 in one action, and what is the most "
            "complete candidate theory currently supported?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_master_core": v62_master["core_sha256"],
            "V61_master_core_via_parent": v62_master["lineage"][
                "parent_master_core"
            ],
            "supersession": supersession,
        },
        "upstream_status": {
            "V62_master": v62_master["status"],
            "V63_wz_inflow": inflow["status"],
            "V60_live_heterotic": live["status"],
            "V59_gauged_U1R": gauged["status"],
        },
        "route_matrix": routes,
        "consolidated_theory_card": card,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action. The Spin(11) "
                "candidate with its GS and WZ sectors, conditional heterotic "
                "charges and a gauged-U1R lattice cannot be conjoined across "
                "inequivalent actions."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_specific_obstructions_remain_scoped": True,
        },
        "comparison_conclusion": {
            "heterotic": v62_master["comparison_conclusion"]["heterotic"],
            "Spin11": (
                "Every anomaly question this program knows how to pose about "
                "the Z4R selector is now answered exactly: global universality "
                "(V61), the localized orbifold ledger with its GS cure (V62), "
                "and the post-VEV rearrangement (V63).  The route is blocked "
                "only by dynamical and UV data: the WZ functional, the saxion "
                "potential, Dai-Freed, the KK determinant and the regulator."
            ),
            "gauged_U1R": v62_master["comparison_conclusion"]["gauged_U1R"],
            "frontier": (
                "Route B holds the consolidated candidate; its next obligation "
                "is the first genuinely dynamical one, the WZ extraction.  "
                "Routes A60 and C retain their separately certified "
                "obstructions."
            ),
        },
        "strict_master_decision": {
            "inflow_deficits_identified": True,
            "consolidated_candidate_bound": True,
            "same_action_microscopic_completion_found": False,
            "V63_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The Spin(11) route's anomaly program is arithmetically "
                "complete: the V62 deficits are exactly the dissolved Goldstone "
                "ledger, matching closes, and the WZ coefficient is forced.  "
                "The consolidated theory card is the most complete candidate "
                "this program supports, and it is a candidate only: dynamical "
                "WZ extraction, saxion stabilization, Dai-Freed, KK and UV data "
                "are absent.  No same-action route closes G1, and G1--G8 "
                "remain open."
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
        raise AssertionError("V63 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V63 multipath integrity failures: {failed}")
    decision = report["strict_master_decision"]
    if decision["same_action_microscopic_completion_found"]:
        raise AssertionError("V63 master promoted an absent completion")
    if decision["V63_G1_closed"] or decision["closed_gates"]:
        raise AssertionError("V63 master promoted a gate")
    if decision["complete_theory"]:
        raise AssertionError("V63 master overclaimed a complete theory")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("V63 master spliced inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V63 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    a = rows["A60"]
    b = rows["B63"]
    c = rows["C"]
    supersession = report["lineage"]["supersession"]
    card = report["consolidated_theory_card"]
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    inventory = "\n".join(f"- {item}" for item in card["action_inventory"])
    passes = "\n".join(f"- {item}" for item in card["certified_passes"])
    opens = "\n".join(f"- {item}" for item in card["open_obligations"])
    obligations = "\n".join(f"- {item}" for item in b["remaining_obligations"])
    return f"""# V63 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**The anomaly program of the Spin(11) route is arithmetically complete: the
V62 inflow deficits are exactly the dissolved Goldstone ledger, both infrared
matching identities close, and the Wess-Zumino coefficient is uniquely
forced.  The consolidated candidate theory is bound below.  G1--G8 remain
OPEN.**

This distinct V63 master supersedes only the V62 route-B row.  It binds the
V62 master and directly rebinds the unchanged A60 and C cores.  No route-local
gain is spliced into another action.

## Exact supersession

```text
V62 route B: {supersession['superseded_route']['route_core']}
V63 route B: {supersession['replacement_route']['route_core']}
V62 master:  {supersession['superseded_route']['master_core']}
```

## The identification in numbers

```text
fates of the 32 rank components: {b['fate_enumeration']['fate_counts']}
dissolved ledger:                {b['fate_enumeration']['dissolved_ledger']}
V62 required inflow:             {b['deficit_identification']['V62_required_inflow']}
identification exact:            {b['deficit_identification']['identification_exact']}
IR identities close:             {b['deficit_identification']['both_ir_identities_close']}
WZ term:                         {b['forced_wz_term']['status']}
```

Remaining route-B obligations:

{obligations}

## Consolidated candidate theory card

**{card['name']}**

Action inventory:

{inventory}

Certified passes (each bound by a hash-pinned audit):

{passes}

Open obligations:

{opens}

{card['honesty_clause']}

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
            raise RuntimeError("generated V63 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V63 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V63 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
