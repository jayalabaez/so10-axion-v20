#!/usr/bin/env python3
"""Integrated, fail-closed V42 theory audit.

V42 tests the three bottlenecks exposed by the V41 ledger.  It deliberately
records both the new exact constructions and the new counterexamples: a local
continuous product parent can be made anomaly-free only along a branch that
destroys the old X-derived selector; a neutral-parameter additive symmetry
cannot sequester the new source from the host; and a high-degree PS-VEV
six-matter B/L witness remains selector-allowed.  The report therefore
promotes no G1--G8 gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V42_COMPLETE_THEORY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V42_COMPLETE_THEORY_AUDIT.md"

INPUTS = {
    "v41": ROOT / "SUSY_V41_COMPLETE_THEORY_AUDIT.json",
    "source_host": ROOT / "SUSY_V42_SOURCE_HOST_ADDITIVE_NO_GO_AUDIT.json",
    "product": ROOT / "SUSY_V42_PRODUCT_PARENT_LOCAL_COMPLETION.json",
    "g7": ROOT / "SUSY_V42_G7_PS_VEV_EPSILON_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v42_complete_theory_audit.py",
    "test_susy_v42_complete_theory_audit.py",
    "susy_v41_complete_theory_audit.py",
    "susy_v42_source_host_additive_no_go_audit.py",
    "susy_v42_product_parent_local_completion.py",
    "susy_v42_g7_ps_vev_epsilon_audit.py",
)
STATUS = (
    "V42_INTEGRATED__LOCAL_PRODUCT_PARENT_AND_EXACT_NO_GOS__"
    "SOURCE_HOST_AND_G7_COUNTEREXAMPLES__ZERO_OF_EIGHT_FULL_GATES_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        if not path.is_file():
            raise RuntimeError(f"required V42 input missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"required V42 input is not an object: {path.name}")
        if canonical_sha(payload) != payload.get("core_sha256"):
            raise RuntimeError(f"required V42 input checksum failed: {path.name}")
        result[name] = payload
    return result


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def gate_ledger(inputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    v41 = inputs["v41"]
    source_host = inputs["source_host"]
    product = inputs["product"]
    g7 = inputs["g7"]
    product_rows = product["full_local_continuous_anomaly_audit"]
    source_branch = source_host["coupled_F_branch_boundary"]
    g7_witness = g7["selector_allowed_six_matter_witness"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "advance": (
                "An explicit chiral packet cancels every local U(1)_F x U(1)_X x U(1)_H cubic, "
                f"mixed-PS, and gravitational row ({product_rows['U1_cubic_and_all_cross_triangles']}) "
                "with full-rank spectator mass witnesses, while retaining F-to-Z9."
            ),
            "blocker": (
                "The necessary Xi(+/-1) VEVs make the X remnant trivial and explicitly break the old "
                "Z66/Z5610 selector.  Z4R/discrete/global/bordism data, the full host vacuum, thresholds, "
                "and a microscopic UV completion remain absent.  The even-X threshold obstruction is only "
                "proved for Dirac-paired blocks; Majorana/Pfaffian, light-state, or topological escapes are "
                "not excluded."
            ),
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": "V41's isolated source mass and F/D-flat witnesses remain useful local EFT data.",
            "blocker": (
                "V42 proves that the isolated source times the unperturbed host is generically not F-flat: "
                f"{source_branch['generic_result']['reason']}  No coupled PS/PQ/U(1)_F Kähler/soft vacuum, "
                "component matrices, pole spectrum, or covariance exists."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": "The exact neutral-parameter additive source-host separation no-go identifies the required redesign boundary.",
            "blocker": (
                "With naked STheta, X, Zp and STheta ThetaPlus ThetaMinus terms, X ThetaPlus ThetaMinus "
                "and Zp ThetaPlus ThetaMinus are unavoidable.  A coupled vacuum, charged-spurion redesign, "
                "or non-additive/geometrical sequestering must be explicitly constructed; global minima, "
                "thermal selection, and tunnelling remain unknown."
            ),
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "The conditional product-parent and source packets make their complete mediation and soft-sector inventory explicit.",
            "blocker": "No hidden W/K/f, mediation mechanism, mu/Bmu derivation, radiative EWSB calculation, or collider likelihood is supplied.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": v41["gate_ledger"][4]["advance"],
            "blocker": "No selector-compatible dark source, physical spectrum, coupled Boltzmann/PQ evolution, or likelihood is derived.",
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": "The fully enumerated V42 local-parent packet provides a concrete enlarged threshold list for a future RG calculation.",
            "blocker": "No physical boundary conditions, kinetic mixing treatment, threshold matching, complete beta system, or uncertainty propagation is derived.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": (
                "The conventional Q4/Qc4 epsilon families remain all-order Z9-blocked in the declared VEV ring, "
                "and the one-PS-VEV Q3 Sbc H / Qc3 Sc precursors are all-order residual-R-parity blocked."
            ),
            "blocker": (
                "A fully listed-selector-clean degree-ten witness exists: "
                f"{g7_witness['operator']}, with DeltaB={g7_witness['Delta_B']} and DeltaL={g7_witness['Delta_L']}. "
                "It has a nonzero PS component and prevents a full G7 proof.  Its Wilson coefficient, flavour "
                "tensor, spectrum, dressing, RG, and physical decay amplitudes are uncomputed, so it is not a "
                "proton-lifetime claim."
            ),
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": v41["gate_ledger"][7]["advance"],
            "blocker": (
                "The Dirac messenger remains a local matching construction only: a coupled source/host vacuum, "
                "three-family texture, charged-fermion/PMNS/CKM fit, pole spectrum, flavour likelihood, and "
                "withheld-observable prediction are absent."
            ),
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = load_inputs()
    v41 = inputs["v41"]
    source_host = inputs["source_host"]
    product = inputs["product"]
    g7 = inputs["g7"]
    rows = gate_ledger(inputs)
    integrity = {
        "all_input_cores_verify": True,
        "V41_started_with_zero_full_gates": v41["established_full_predictive_closed_count"] == 0,
        "neutral_parameter_additive_source_host_no_go_verified": source_host["integrity_checks"]["symbolic_no_go_has_two_universal_bridges"],
        "generic_isolated_source_host_product_branch_is_not_F_flat": not source_host["decision"]["generic_isolated_source_times_unperturbed_host_branch_is_F_flat"],
        "local_product_all_ten_U1_cubic_rows_vanish": product["checks"]["all_ten_symmetric_U1_cubic_cross_rows_vanish"],
        "local_product_all_nine_U1_PS_squared_rows_vanish": product["checks"]["all_nine_U1_PS_squared_rows_vanish"],
        "local_product_all_three_U1_gravity_rows_vanish": product["checks"]["all_three_U1_gravity_rows_vanish"],
        "local_product_spectator_mass_witnesses_are_full_rank": product["checks"]["all_new_spectator_blocks_have_full_rank_witness"],
        "local_product_preserves_Z9": product["checks"]["Z9_selector_survives_all_declared_product_VEVs"],
        "local_product_does_not_silently_preserve_old_Z5610": product["checks"]["old_Z5610_is_not_silently_claimed_preserved"],
        "G7_low_degree_same_orientation_protection_survives": g7["decision"]["low_degree_same_orientation_protection_is_exact_in_stated_ring"],
        "G7_selector_clean_six_matter_witness_exists": g7["decision"]["fully_listed_selector_clean_six_matter_B_L_witness_exists"],
        "G7_is_not_promoted": not g7["decision"]["full_G7_closed"],
        "no_full_gate_promoted": all(not row["closed"] for row in rows),
    }
    report: dict[str, Any] = {
        "schema": "susy-v42-complete-theory-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "active_theory_classification": (
            "a reproducible V42 Pati-Salam EFT research program with a local anomaly-free continuous "
            "product witness, a concrete source-host incompatibility theorem, and exact restricted G7 "
            "protections plus a selector-allowed B/L counterexample; not a complete predictive theory"
        ),
        "integrity_checks": integrity,
        "gate_ledger": rows,
        "genuine_V42_advances": {
            "local_product_parent": (
                "All local continuous product rows can be cancelled by an explicit massable packet, showing "
                "that the triangle algebra itself is not the only barrier."
            ),
            "source_host_theorem": (
                "The source-host portal problem is now an all-additive-factor theorem for neutral naked "
                "parameters, not an omitted term that can be removed by an extra charge label."
            ),
            "G7_frontier": (
                "The low-degree PS-VEV frontier is classified exactly and the first clean selector-allowed "
                "single-epsilon/delta six-matter witness occurs at full field degree ten in the bounded scan."
            ),
        },
        "hard_boundaries": [
            "The local product parent destroys the old X-derived Z66/Z5610 selector, so it cannot be substituted for a common selector-preserving UV completion.",
            "The source-host no-go does not rule out a genuinely coupled vacuum or a charged-spurion/new-physics redesign; it rules out only a neutral-parameter additive separation.",
            "The even-X threshold theorem excludes fully massive Dirac-paired blocks only; Majorana/Pfaffian, light-state, and specified topological responses remain distinct possibilities requiring full construction.",
            "The degree-ten six-matter B/L witness is an allowed EFT operator, not a calculated nucleon-decay rate.",
            "No soft/Kähler global vacuum, spectrum, RG, cosmology, flavour fit, or prediction likelihood has been derived.",
        ],
        "decisive_next_physics": [
            "Choose an actual UV architecture rather than combine mutually incompatible selector remnants: specify its full global gauge group, charge lattice, anomaly/bordism data, and low-energy matching.",
            "Either solve the fully coupled source/host F/D/Kähler/soft system with all allowed portals or formulate and re-audit a charged-spurion/non-additive source redesign.",
            "Perform complete PS invariant-ring and component matching for the degree-ten B/L witness; calculate whether it yields any observable nucleon or multi-lepton process.",
            "Only after those foundations, build the three-family Dirac flavour, dark sector, RG, and joint-likelihood calculations required by G4--G8.",
        ],
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = "\n".join(
        f"| {row['gate']} | {'closed' if row['closed'] else 'open'} | {row['advance']} |"
        for row in report["gate_ledger"]
    )
    advances = "\n".join(f"- **{name.replace('_', ' ')}:** {value}" for name, value in report["genuine_V42_advances"].items())
    boundaries = "\n".join(f"- {item}" for item in report["hard_boundaries"])
    next_steps = "\n".join(f"1. {item}" for item in report["decisive_next_physics"])
    return f"""# V42 complete-theory integration audit

Status: {report['status']}

V42 creates a sharper boundary map, not a finished theory.  The local
continuous product anomaly ledger can be made exactly zero, but its required
odd-X branch destroys the old selector.  The source-host portal is proved to
be unavoidable under the current neutral-parameter additive architecture, and
the G7 low-degree protection has a concrete high-degree B/L counterexample.

| Gate | Status | V42 advance |
|---|---|---|
{rows}

## Genuine V42 advances

{advances}

## Fail-closed boundaries

{boundaries}

## Decisive next physics

{next_steps}

Core SHA-256: {report['core_sha256']}
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V42 integrated JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V42 integrated Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V42_COMPLETE_THEORY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
