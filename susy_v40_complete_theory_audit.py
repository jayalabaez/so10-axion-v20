#!/usr/bin/env python3
"""Integrated fail-closed V40 theory audit.

This is an integration ledger, not a device for upgrading a new charge table
or a numerical proxy into a complete theory.  It combines the independently
checked V40 selector, UV, and non-UV contracts and promotes no gate until its
microscopic inputs and observables have actually been derived.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V40_COMPLETE_THEORY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V40_COMPLETE_THEORY_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v40_complete_theory_audit.py"

INPUTS = {
    "v39": ROOT / "SUSY_V39_COMPLETE_THEORY_AUDIT.json",
    "uv": ROOT / "SUSY_V40_G1_UV_ROUTE_CONTRACT.json",
    "nonuv": ROOT / "SUSY_V40_NONUV_COMPLETION_CONTRACT.json",
    "z9": ROOT / "SUSY_V40_ALL_RING_SELECTOR.json",
    "z9_stress": ROOT / "SUSY_V40_Z9_U1F_STRESS_AUDIT.json",
    "z13r": ROOT / "SUSY_V40_Z13R_SELECTOR_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v40_complete_theory_audit.py",
    "test_susy_v40_complete_theory_audit.py",
    "susy_v40_all_ring_selector.py",
    "susy_v40_z9_u1f_stress_audit.py",
    "susy_v40_z13r_selector_audit.py",
    "susy_v40_g1_uv_route_contract.py",
    "susy_v40_nonuv_completion_contract.py",
)
STATUS = (
    "V40_REBUILD_INTEGRATED__EXACT_SELECTOR_AND_NO_GO_ADVANCES__"
    "ZERO_OF_EIGHT_FULL_GATES_CLOSED"
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
            raise RuntimeError(f"required V40 input missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"required V40 input is not an object: {path.name}")
        if canonical_sha(payload) != payload.get("core_sha256"):
            raise RuntimeError(f"required V40 input checksum failed: {path.name}")
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
    z9 = inputs["z9"]
    z9_stress = inputs["z9_stress"]
    z13r = inputs["z13r"]
    nonuv = inputs["nonuv"]
    uv = inputs["uv"]
    ring = z9["same_orientation_baryon_ring_proof"]
    cross = z9["conditional_V38_parent_cross_anomaly_audit"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "advance": (
                "The V40 PS times U(1)_F selector sector has an explicit local anomaly-free "
                "parent and an unbroken Z9 remnant.  A separate Z13R route has necessary "
                "universal Green-Schwarz arithmetic.  The conventional V39 Z66 parent and "
                "trivial mirror-wall gap remain excluded."
            ),
            "blocker": (
                "No common microscopic completion of Z5610 times Z9 times Z4R is supplied. "
                "The attempted reuse of V38 continuous parent lifts has nonzero cross rows "
                f"{cross['rows']}; a quantized product anomaly/bordism completion and visible "
                "threshold matching are still required."
            ),
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": "V40 makes the new selector and its anomaly-canceling threshold content explicit.",
            "blocker": "No accepted soft/Kahler vacuum, component matrices, pole spectrum, or covariance exists.",
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": "A candidate U(1)_F Higgsing source and its necessary neutral-VEV branch are stated.",
            "blocker": "The full Kähler, gauge-kinetic, soft, finite-temperature, branch, and tunnelling problem remains unsolved.",
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "The new heavy selector fields identify additional mediation and singlet-lifting obligations.",
            "blocker": "No hidden W/K/f, messenger vacuum, mu/Bmu derivation, or radiative EWSB calculation is supplied.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": (
                "The V39 isolated Yukawa route is quantitatively excluded at the stated point: "
                f"lambda_D={nonuv['V39_pure_yukawa_G5_scale_no_go']['V39_fitted_lambda_D']}, "
                f"Lambda={nonuv['V39_pure_yukawa_G5_scale_no_go']['V39_lambda_pole_GeV']:.3g} GeV < fPQ. "
                "A perturbative U(1)_D vector route is only a conditional feasibility witness."
            ),
            "blocker": "No selector-compatible dark source, component spectrum, coupled Boltzmann/PQ history, or likelihood is derived.",
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": "V40 specifies the rule that all beta functions and thresholds must be regenerated for the changed field content.",
            "blocker": "No physical boundaries, threshold matching, complete coupled RG system, or propagated covariance is derived.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": (
                "The exact same-orientation Q4/Qc4 subring is protected from all declared PS, PQ, "
                "and U(1)_F VEV dressings: local driver-dressed residues are "
                f"{[row['Z9'] for row in ring['local_driver_dressed_Q4_Qc4_sources']]}, "
                "and the V39 degree-nine Qc4 witness is also Z9-forbidden.  The alternative "
                "Z13R route retains type-I and blocks the same pure source ring on its high-scale "
                "PS/PQ branch."
            ),
            "blocker": (
                "The type-I Majorana seesaw cannot coexist with this ordinary unbroken additive protection; "
                "the route is Dirac-neutrino only.  Mixed-orientation structures such as X Q Q Qc Qc are "
                "selector-neutral, and their components, Wilsons, SUSY dressing, running, and hadronic "
                "matching remain uncomputed.  The Z13R route is also not a literal all-VEV block: "
                f"{z13r['ring']['EW_VEV_counterexamples'][0]['operator']} and "
                f"{z13r['ring']['EW_VEV_counterexamples'][1]['operator']} are R13-allowed after EWSB."
            ),
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": "V40 identifies a Dirac-neutrino operator direction and proves why the retained type-I block conflicts with the exact additive remnant.",
            "blocker": "The messenger/flavour sector, fermion spectrum, PMNS/CKM fit, thresholds, and withheld-observable likelihood are absent.",
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = load_inputs()
    rows = gate_ledger(inputs)
    z9 = inputs["z9"]
    z9_stress = inputs["z9_stress"]
    z13r = inputs["z13r"]
    uv = inputs["uv"]
    nonuv = inputs["nonuv"]
    integrity = {
        "all_input_cores_verify": True,
        "v39_started_with_zero_full_gates": inputs["v39"]["established_full_predictive_closed_count"] == 0,
        "new_U1F_PS_local_anomalies_cancel": z9["integrity_checks"]["all_local_U1F_anomalies_cancel"],
        "new_Z9_finite_arithmetic_passes": z9["integrity_checks"]["finite_Z9_arithmetic_passes"],
        "new_Z9_declared_VEVs_remain_unbroken": z9["integrity_checks"]["declared_VEVs_preserve_Z9"],
        "same_orientation_Q4_Qc4_declared_VEV_dressings_are_forbidden": z9["integrity_checks"]["all_declared_VEV_dressings_of_same_orientation_Q4_Qc4_forbidden"],
        "V39_Qc4_degree9_counterexample_is_blocked_by_Z9": z9_stress["pure_Q4_Qc4_holomorphic_ring"]["canonical_PSVev_counterexample_retested"]["integer_solution_exists"] is False,
        "type_I_seesaw_no_go_for_Z9_route_verified": z9_stress["decision"]["retained_V39_type_I_Majorana_seesaw_survives"] is False,
        "Z13R_high_scale_type_I_route_verified_but_EW_counterexamples_present": (
            z13r["decision"]["high_scale_pure_Q4_Qc4_block"] is True
            and z13r["decision"]["type_I_source_present"] is True
            and z13r["decision"]["all_VEV_ring_block"] is False
        ),
        "old_parent_cross_completion_not_silently_assumed": not z9["conditional_V38_parent_cross_anomaly_audit"]["all_rows_vanish"],
        "G1_still_fail_closed": uv["gate_decision"]["G1_closed"] is False,
        "V39_pure_yukawa_G5_no_go_preserved": nonuv["V39_pure_yukawa_G5_scale_no_go"]["V39_pole_below_fPQ"] is True,
        "no_full_gate_promoted": all(not row["closed"] for row in rows),
    }
    report: dict[str, Any] = {
        "schema": "susy-v40-complete-theory-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "active_theory_classification": (
            "a collection of reproducible V40 EFT architecture candidates and no-go theorems, "
            "not a complete predictive theory"
        ),
        "integrity_checks": integrity,
        "gate_ledger": rows,
        "new_physics_routes": {
            "selector_route_A": {
                "name": "locally anomaly-free PS times U(1)_F Higgsed to unbroken Z9",
                "strength": "exactly blocks the pure same-orientation Q4/Qc4 source ring and the V39 degree-nine Qc4 dressing on the declared neutral-VEV branch",
                "cost": "requires a Dirac-neutrino rebuild and leaves mixed operator classes plus product-symmetry UV data open",
            },
            "selector_route_B": {
                "name": "Z13R high-scale Pati-Salam/PQ selector rebuild",
                "strength": "retains the type-I source and blocks pure Q4/Qc4 sources before electroweak breaking",
                "cost": "requires a new source/vacuum and a quantized GS/product completion; H has R13 charge five, so explicit EWSB dressings defeat literal all-VEV protection",
            },
            "UV_route_C": {
                "name": "4D gauge-derived selector rebuild or 5D inflow with a microscopic anomalous boundary theory",
                "strength": "two logically coherent classes remain after the V39 no-gos",
                "cost": "neither is instantiated by a single microscopic model in this workspace",
            },
            "dark_route_D": {
                "name": "Higgsed vector U(1)_D dark annihilation sector",
                "strength": "a perturbative one-loop feasibility witness avoids the isolated lambda_D pole",
                "cost": "the source, selector compatibility, vacuum, and cosmology are all still required",
            },
        },
        "hard_boundaries": [
            "Changing a charge table cannot derive the missing product anomaly, Kähler/soft functions, UV thresholds, or flavour data.",
            "The V40 Z9 route proves a restricted all-order selector statement, not a proton lifetime.",
            "A Majorana/type-I source after neutral VEV insertions makes Qc4 neutral in every ordinary additive remnant under the stated assumptions.",
            "The Z13R high-scale route retains type-I but electroweak Higgs VEVs explicitly allow its pure-source dressings.",
            "The original V39 pure-Yukawa thermal point has a sub-PQ Landau pole and cannot be retained unchanged.",
        ],
        "decisive_next_physics": [
            "choose one microscopic product-symmetry/UV route and supply its quantized anomaly, spectrum, and threshold data",
            "construct and solve a complete V40 W/K/f and U(1)_F-breaking vacuum, including all new heavy fields",
            "complete mixed-operator classification and component matching before any proton-stability claim",
            "derive a selector-compatible dark and flavour sector, then calculate physical poles, RG matching, cosmology, and a joint likelihood",
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
    return f"""# V40 complete-theory integration audit

Status: {report['status']}

V40 found a real new symmetry architecture but not a finished theory.  The
strongest exact result is an anomaly-free PS times U(1)_F parent which leaves
unbroken Z9 and forbids every declared-VEV dressing of the same-orientation
Q4/Qc4 source ring.  It also exposes the precise tradeoff: the original
neutral-VEV type-I Majorana seesaw is incompatible with that additive
protection, so this route needs a Dirac-neutrino rebuild.

| Gate | Status | Advance |
|---|---|---|
{rows}

No gate is promoted.  The missing objects are physical input, not algebra
waiting to be manipulated: a common product-symmetry UV completion, a solved
soft/Kahler vacuum and spectrum, full operator matching, cosmology, and a
UV-derived flavour likelihood.

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
        raise RuntimeError("V40 integrated JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V40 integrated Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V40_COMPLETE_THEORY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
