#!/usr/bin/env python3
"""V61 master audit after the Spin(11) exact Z4R selector escape.

This is a new master, not an edit of V60.  It supersedes only the V59 route-B
classification row: the sharp non-R selector no-go remains true and bound, but
it is no longer the operative route-B frontier, because the V61 route audit
proves the no-go does not extend to R-type Abelian selectors and that exactly
one physical R class survives every exact requirement: Z4R with all matter
sixteens at charge one.

That selector passes the Green-Schwarz universality test that rejected the
corrected heterotic candidate in V60.  It does not close strict G1: the single
GS axion multiplet, the localized fixed-point R-anomaly ledger, the Dai-Freed
phase, the exact KK determinant and a UV regulator are still absent.  Routes
A60 and C are carried forward unchanged.  No route-local gain is spliced into
another action, and all G1--G8 gates stay open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V61_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V61_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v61_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v60_master": ROOT / "SUSY_V60_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v61_z4r_escape": ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.json",
    "v60_live_heterotic": ROOT
    / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "v59_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

CORE_KEYS = {
    "v60_master": "core_sha256",
    "v61_z4r_escape": "core_sha256",
    "v60_live_heterotic": "canonical_core_sha256",
    "v59_gauged_u1r": "core_sha256",
}

EXPECTED_CORES = {
    "v60_master": "35395532eaf625886b704ed25b7fa8525482ec1d53b94ccc96e7858d6425898e",
    "v61_z4r_escape": "6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a",
    "v60_live_heterotic": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "v59_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V61_MULTIPATH_G1_FRONTIER_MASTER__V60_MASTER_AND_Z4R_ESCAPE_CORE_BOUND__"
    "V59_ROUTE_B_CLASSIFICATION_SUPERSEDED__SPIN11_NON_R_OBSTRUCTION_RESOLVED_"
    "AT_R_TYPE_ARITHMETIC_AND_GLOBAL_ANOMALY_LEVEL__UNIQUE_Z4R_CLASS_UP_TO_"
    "GAUGE_CENTER__W_AND_KAHLER_DIM5_PROTON_BANS_EXACT__UNIVERSALITY_PASSES_"
    "WHERE_HETEROTIC_CANDIDATE_FAILED__GS_AXION_LOCALIZED_R_ANOMALY_DAI_FREED_"
    "KK_UV_OPEN__ROUTES_A60_AND_C_CARRIED_FORWARD__NO_CROSS_ROUTE_SPLICING__"
    "G1_TO_G8_OPEN"
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
        raise RuntimeError(f"missing V61 master input: {path.name}")
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


def z4r_escape_row(value: Mapping[str, Any]) -> dict[str, Any]:
    scan = value["exhaustive_r_selector_scan"]
    equivalence = value["gauge_center_equivalence"]
    anomalies = value["anomaly_universality_certificate"]
    proton = value["proton_mu_ledger"]
    contrast = value["non_R_contrast"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "B61",
        "name": "Spin(11) gauge-Higgs route with the exact Z4R selector escape",
        "bound_core_sha256": value["core_sha256"],
        "classification": value["classification"],
        "supersedes_V59_route_id": "B",
        "tested_object": (
            "all R-type Abelian selectors Z_M^R with 2<=M<=24 and all family "
            "charge triples, under the architecture-forced q_Sigma=0, bulk "
            "hyper charges (1,1) and VEV-neutral rank charges"
        ),
        "escape_certificate": {
            "v59_non_R_scan_had_zero_selectors": contrast[
                "v59_non_R_counterexamples"
            ]
            == 0,
            "v59_first_loophole_was_exact_R": contrast["v61_realizes_that_loophole"],
            "odd_cycle_argument_inverts_for_R_type": value[
                "odd_cycle_escape_theorem"
            ]["every_forced_diagonal_16_pow4_forbidden"],
            "assignments_scanned": scan["assignments_scanned"],
            "arithmetic_selectors_exist_beyond_M4": scan[
                "arithmetic_selectors_exist_beyond_M4"
            ],
            "GS_universality_selects_only_M4": all(
                row["plus_GS_universality"] == 0
                for row in scan["per_modulus"]
                if row["M"] != 4
            ),
            "raw_solutions": [row["charges"] for row in scan["solutions"]],
            "physical_class_count": equivalence["physical_class_count"],
            "canonical_class": equivalence["canonical_class"],
        },
        "anomaly_certificate": {
            "A3": anomalies["A3"],
            "A2": anomalies["A2"],
            "eta": anomalies["eta"],
            "universal_mod_eta": anomalies["universal_mod_eta"],
            "GS_axion_required": anomalies["GS_axion_required"],
            "GS_axion_exhibited": anomalies["GS_axion_exhibited_in_5D_action"],
            "heterotic_contrast_bound": anomalies["heterotic_contrast"][
                "V60_route_A60_residue_vector_mod2"
            ],
        },
        "proton_upgrade": {
            "W_dim5_forbidden_all_orders": proton["W_dim5_all_orders_ban"][
                "forbidden"
            ],
            "Kahler_dim5_forbidden": proton["Kahler_dim5_ban"]["forbidden"],
            "dimension_six_and_numerics_open": True,
        },
        "remaining_obligations": terminal["next_obligations"],
        "same_action_microscopic_completion": terminal["V61_G1_closed"],
        "G1_closed": terminal["V61_G1_closed"],
        "closed_gates": terminal["V61_closed_gates"],
    }


def carried_route(
    v60_master: Mapping[str, Any],
    route_id: str,
    direct: Mapping[str, Any],
    direct_core_key: str,
) -> dict[str, Any]:
    row = route_by_id(v60_master, route_id)
    if row["bound_core_sha256"] != direct[direct_core_key]:
        raise RuntimeError(f"V60 route {route_id} row/direct core mismatch")
    row["carried_forward_unchanged_from_V60_master_core"] = v60_master["core_sha256"]
    row["direct_core_rebound_in_V61"] = True
    return row


def gate_ledger(v60_master: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v60_master["gate_ledger"]}
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        if gate == "G1":
            decision = (
                "OPEN: the Spin(11) non-R selector obstruction is resolved at the "
                "R-type arithmetic and global-anomaly level by a unique Z4R class "
                "that passes the universality test which rejected the corrected "
                "heterotic candidate; the required GS axion multiplet, localized "
                "fixed-point R-anomaly ledger, Dai-Freed phase, exact KK "
                "determinant and UV regulator remain absent, and routes A60 and C "
                "retain their independent obstructions."
            )
        else:
            decision = (
                f"OPEN: V61 adds no same-action proof of {gate}; the prior "
                f"fail-closed frontier remains: {prior[gate]['decision']}"
            )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V61_master_closed": False,
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
    v60_master = load_bound("v60_master")
    escape = load_bound("v61_z4r_escape")
    live = load_bound("v60_live_heterotic")
    gauged = load_bound("v59_gauged_u1r")

    old_b = route_by_id(v60_master, "B")
    new_b = z4r_escape_row(escape)
    route_a = carried_route(v60_master, "A60", live, "canonical_core_sha256")
    route_c = carried_route(v60_master, "C", gauged, "core_sha256")
    routes = [route_a, new_b, route_c]
    gates = gate_ledger(v60_master)

    supersession = {
        "superseded_route": {
            "master_core": v60_master["core_sha256"],
            "route_id": "B",
            "route_core": old_b["bound_core_sha256"],
            "classification": old_b["classification"],
        },
        "replacement_route": {
            "route_id": "B61",
            "route_core": escape["core_sha256"],
            "classification": new_b["classification"],
        },
        "what_is_resolved": (
            "the V59 non-R no-go is answered on its own first loophole: R-type "
            "selectors evade the determinant-cycle obstruction, and exactly one "
            "physical class, Z4R with matter charge one, survives the full-rank "
            "Yukawa, dimension-five proton, and GS-universality requirements"
        ),
        "what_is_not_resolved": (
            "the single GS axion multiplet, localized fixed-point R anomalies, "
            "the Dai-Freed phase, the exact KK determinant/flavor fit, the soft "
            "spectrum and a UV regulator; strict G1 stays open"
        ),
        "v59_non_R_theorem_still_true_and_bound": (
            "the escape does not falsify the V59 theorem; the theorem's own "
            "scope excluded R symmetries, and its core remains bound inside the "
            "V61 route lineage"
        ),
        "route_A60_core_unchanged": route_a["bound_core_sha256"],
        "route_C_core_unchanged": route_c["bound_core_sha256"],
        "V60_master_modified": False,
    }

    no_same_action = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V59_route_B_is_replaced_not_mutated": (
            supersession["superseded_route"]["route_id"] == "B"
            and supersession["replacement_route"]["route_id"] == "B61"
            and supersession["superseded_route"]["route_core"]
            != supersession["replacement_route"]["route_core"]
            and not supersession["V60_master_modified"]
        ),
        "escape_certificate_is_bound": (
            new_b["escape_certificate"]["v59_first_loophole_was_exact_R"]
            and new_b["escape_certificate"]["odd_cycle_argument_inverts_for_R_type"]
            and new_b["escape_certificate"]["assignments_scanned"] == 89999
            and new_b["escape_certificate"]["GS_universality_selects_only_M4"]
            and new_b["escape_certificate"]["physical_class_count"] == 1
            and new_b["escape_certificate"]["canonical_class"]
            == {"M": 4, "matter_charges": [1, 1, 1]}
        ),
        "anomaly_universality_passes_where_heterotic_failed": (
            new_b["anomaly_certificate"]["A3"] == "3"
            and new_b["anomaly_certificate"]["A2"] == "1"
            and new_b["anomaly_certificate"]["universal_mod_eta"]
            and new_b["anomaly_certificate"]["heterotic_contrast_bound"]
            == ["1", "1", "1", "0", "0"]
        ),
        "GS_axion_requirement_not_overclaimed": (
            new_b["anomaly_certificate"]["GS_axion_required"]
            and not new_b["anomaly_certificate"]["GS_axion_exhibited"]
        ),
        "proton_dim5_bans_bound_and_scoped": (
            new_b["proton_upgrade"]["W_dim5_forbidden_all_orders"]
            and new_b["proton_upgrade"]["Kahler_dim5_forbidden"]
            and new_b["proton_upgrade"]["dimension_six_and_numerics_open"]
        ),
        "five_remaining_obligations_bound": len(new_b["remaining_obligations"]) == 5,
        "route_A60_is_directly_rebound_unchanged": (
            route_a["bound_core_sha256"] == EXPECTED_CORES["v60_live_heterotic"]
            and route_a["direct_core_rebound_in_V61"]
        ),
        "route_C_is_directly_rebound_unchanged": (
            route_c["bound_core_sha256"] == EXPECTED_CORES["v59_gauged_u1r"]
            and route_c["direct_core_rebound_in_V61"]
        ),
        "no_route_has_same_action_microscopic_completion": no_same_action,
        "cross_route_splicing_is_forbidden": True,
        "all_G1_to_G8_gates_remain_open": all(
            row["status"] == "OPEN"
            and not row["V61_master_closed"]
            and not row["cross_route_aggregation_used"]
            for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v61_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "After the exact Z4R selector escape on the Spin(11) route, does any "
            "route close strict G1 in one action?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_master_core": v60_master["core_sha256"],
            "V59_master_core_via_parent": v60_master["lineage"][
                "parent_master_core"
            ],
            "supersession": supersession,
        },
        "upstream_status": {
            "V60_master": v60_master["status"],
            "V61_z4r_escape": escape["status"],
            "V60_live_heterotic": live["status"],
            "V59_gauged_U1R": gauged["status"],
        },
        "route_matrix": routes,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action. A Spin(11) "
                "Z4R selector, conditional heterotic charges and a gauged-U1R "
                "lattice cannot be conjoined across inequivalent actions."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_specific_obstructions_remain_scoped": True,
        },
        "comparison_conclusion": {
            "heterotic": v60_master["comparison_conclusion"]["heterotic"],
            "Spin11": (
                "The selector question is resolved in the R-type direction: the "
                "unique Z4R class protects the proton at all orders in W, passes "
                "GS universality where the heterotic candidate failed, and is "
                "forced by both the superalgebra Cartan and the mediator mixing. "
                "The route is now blocked only by quantum-completion data: the GS "
                "axion, localized R anomalies, Dai-Freed, the KK determinant and "
                "a UV regulator."
            ),
            "gauged_U1R": v60_master["comparison_conclusion"]["gauged_U1R"],
            "frontier": (
                "Route B is the most advanced: its next obligation, the localized "
                "R-anomaly and GS-axion ledger, is sharply defined.  Routes A60 "
                "and C retain their separately certified obstructions."
            ),
        },
        "strict_master_decision": {
            "selector_escape_proved": True,
            "unique_selector_class": "Z4R with matter charge one",
            "same_action_microscopic_completion_found": False,
            "V61_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The Spin(11) route escapes its V59 selector no-go through the "
                "unique GS-universal Z4R class, which passes the exact test that "
                "rejected the corrected heterotic candidate.  This is an "
                "arithmetic and global-anomaly result; the quantum completion of "
                "the selector and of the route is not exhibited.  No same-action "
                "route closes G1, and G1--G8 remain open."
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
        raise AssertionError("V61 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V61 multipath integrity failures: {failed}")
    decision = report["strict_master_decision"]
    if decision["same_action_microscopic_completion_found"]:
        raise AssertionError("V61 master promoted an absent completion")
    if decision["V61_G1_closed"] or decision["closed_gates"]:
        raise AssertionError("V61 master promoted a gate")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("V61 master spliced inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V61 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    a = rows["A60"]
    b = rows["B61"]
    c = rows["C"]
    supersession = report["lineage"]["supersession"]
    escape = b["escape_certificate"]
    anomaly = b["anomaly_certificate"]
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    obligations = "\n".join(f"- {item}" for item in b["remaining_obligations"])
    return f"""# V61 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**The Spin(11) route escapes its V59 non-R selector no-go: the unique
GS-universal Z4R class survives every exact arithmetic and global-anomaly
requirement, passing the test that rejected the corrected heterotic candidate.
The quantum completion is not exhibited. G1--G8 remain OPEN.**

This distinct V61 master supersedes only the V59 route-B classification row.
It binds the V60 master and directly rebinds the unchanged A60 and C cores.
No route-local gain is spliced into another action.

## Exact supersession

```text
V59 route B: {supersession['superseded_route']['route_core']}
V61 route B: {supersession['replacement_route']['route_core']}
V60 master:  {supersession['superseded_route']['master_core']}
```

The V59 non-R theorem stays true and bound; its own scope excluded R
symmetries, and V61 audits exactly that loophole. The V60 master and route
files were not modified.

## The escape in numbers

- V59: `1295` full-rank non-R supports, `0` viable selectors.
- V61: `{escape['assignments_scanned']}` R-type assignments scanned over `2<=M<=24`.
- Arithmetic selectors exist at many moduli; GS universality eliminates all but `M=4`: `{escape['GS_universality_selects_only_M4']}`.
- Raw solutions `{escape['raw_solutions']}` collapse to `{escape['physical_class_count']}` class under the Spin(10) gauge center: `{escape['canonical_class']}`.

```text
A3 = {anomaly['A3']}, A2 = {anomaly['A2']}, eta = {anomaly['eta']}, universal = {anomaly['universal_mod_eta']}
V60 heterotic residues {anomaly['heterotic_contrast_bound']} were non-universal; the Z4R residues are universal.
```

The proton ledger upgrades exactly: every dimension-five operator is forbidden
to all orders in W and at dimension five in K; the dimension-six KK channel
and all numerics stay open. The required single GS axion is **not** exhibited:
`GS_axion_required={anomaly['GS_axion_required']}`, `GS_axion_exhibited={anomaly['GS_axion_exhibited']}`.

Remaining route-B obligations:

{obligations}

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
            raise RuntimeError("generated V61 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V61 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V61 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
