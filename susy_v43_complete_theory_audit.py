#!/usr/bin/env python3
"""Integrated, fail-closed V43 theory audit.

V43 tests the last direct escapes left by V42: a charged-spurion source
separation, self-paired Z66-preserving thresholds, and a Z4 matter selector
for the first G7 witness.  Each produces a useful exact subresult and a
separate obstruction.  The audit keeps those facts distinct from a complete
physical theory and promotes no G1--G8 gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V43_COMPLETE_THEORY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V43_COMPLETE_THEORY_AUDIT.md"

INPUTS = {
    "v42": ROOT / "SUSY_V42_COMPLETE_THEORY_AUDIT.json",
    "spurion": ROOT / "SUSY_V43_CHARGED_SPURION_SOURCE_AUDIT.json",
    "pfaffian": ROOT / "SUSY_V43_PFAFFIAN_PRODUCT_ESCAPE_AUDIT.json",
    "g7": ROOT / "SUSY_V43_G7_Z4M_SELECTOR_REPAIR_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v43_complete_theory_audit.py",
    "test_susy_v43_complete_theory_audit.py",
    "susy_v42_complete_theory_audit.py",
    "susy_v43_charged_spurion_source_audit.py",
    "susy_v43_pfaffian_product_escape_audit.py",
    "susy_v43_g7_z4m_selector_repair.py",
)
STATUS = (
    "V43_INTEGRATED__DIRECT_SPURION_SELF_PAIRED_AND_Z4M_ESCAPES_CLASSIFIED__"
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
            raise RuntimeError(f"required V43 input missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"required V43 input is not an object: {path.name}")
        if canonical_sha(payload) != payload.get("core_sha256"):
            raise RuntimeError(f"required V43 input checksum failed: {path.name}")
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
    v42 = inputs["v42"]
    spurion = inputs["spurion"]
    pfaffian = inputs["pfaffian"]
    g7 = inputs["g7"]
    spurion_d = spurion["minimal_D_and_residual_audit"]
    pfaffian_theorem = pfaffian["ordinary_Z66_self_paired_Pfaffian_threshold_theorem"]
    z4 = g7["candidate"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "advance": (
                "A Z66-preserving self-Majorana branch with Sigma(+/-66), T, and chi(33) explicitly "
                "cancels the host X-gravity row.  This proves the V42 even-X Dirac parity obstruction "
                "does not extend to self-paired blocks."
            ),
            "blocker": (
                "For the stated ordinary PS-unbroken pre-P/Pbar threshold class, symmetric real blocks shift "
                f"X-PS^2 only in {pfaffian_theorem['symmetric_real_Majorana_block']['mixed_PS_increment_lattice']} and skew/Pfaffian "
                f"blocks in {pfaffian_theorem['skew_pseudoreal_Pfaffian_block']['mixed_PS_increment_lattice']}, while the host needs "
                "+8 on every PS row.  Thus no fully local product parent is established; PS-breaking, light, "
                "strong-dynamics, GS/inflow/topological, discrete-R, global-form, and threshold alternatives "
                "need separate complete constructions."
            ),
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": (
                "The charged-spurion source has a formal renormalizable F-flat source-times-F-flat-host branch "
                "and no potentially PS-invariant source-host portal through degree three."
            ),
            "blocker": (
                "Its minimal gauged zero-FI realization has no D-flat nonzero source branch, and the new U(1)_S "
                "rows are anomalous.  The conditional FI solution is additional UV/physical input, not a solved "
                "Kähler/soft vacuum, spectrum, or covariance calculation."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": (
                "Replacing the naked STheta tadpole by a charged spurion evades the V42 portal theorem at "
                "renormalizable F-term level and retains a formal U(1)_F-to-Z9 branch."
            ),
            "blocker": (
                "The minimal D-term is strictly negative on that nonzero F branch.  A neutral compensator allows "
                "X Omega Omegabar and Zp Omega Omegabar, re-sourcing host F terms; an FI term or a non-minimal "
                "anomaly-complete redesign is still required."
            ),
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "V43 identifies the new U(1)_S/FI/compensator and self-paired threshold obligations that any mediation completion must address.",
            "blocker": "No hidden W/K/f, mediation mechanism, mu/Bmu derivation, radiative EWSB calculation, or collider likelihood is supplied.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": v42["gate_ledger"][4]["advance"],
            "blocker": "No selector-compatible dark source, physical spectrum, coupled Boltzmann/PQ evolution, or likelihood is derived.",
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": "The explicitly enumerated spurion, compensator, self-paired, and Z4M threshold sectors make a future coupled RG inventory more concrete.",
            "blocker": "No physical boundary conditions, kinetic mixing, threshold matching, complete beta system, or uncertainty propagation is derived.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": (
                f"The smallest ordinary non-R arithmetic repair is {z4['name']}; it blocks the V42 degree-ten "
                "witness while preserving all named V40/V41 terms and the required Dirac operator."
            ),
            "blocker": (
                "The Z4M candidate fails its necessary ordinary discrete gravitational screen and has nonzero "
                "continuous U(1)_M/U(1)_F cross rows.  Under the stated unbroken, no-GS, decoupling-only class, "
                "the only allowed orders are 2, 3, and 6, all of which leave the six-Qc witness neutral.  Two "
                "orientation-neutral bounded-frontier rows also remain unclassified."
            ),
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": v42["gate_ledger"][7]["advance"],
            "blocker": (
                "The spurion/source sector has no completed D-flat/anomaly-free parent, and no three-family texture, "
                "charged-fermion/PMNS/CKM fit, pole spectrum, flavour likelihood, or withheld-observable prediction exists."
            ),
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = load_inputs()
    v42 = inputs["v42"]
    spurion = inputs["spurion"]
    pfaffian = inputs["pfaffian"]
    g7 = inputs["g7"]
    rows = gate_ledger(inputs)
    integrity = {
        "all_input_cores_verify": True,
        "V42_started_with_zero_full_gates": v42["established_full_predictive_closed_count"] == 0,
        "spurion_evasion_of_V42_at_renormalizable_F_level_verified": spurion["decision"]["V42_neutral_parameter_no_go_is_evaded_at_renormalizable_F_term_level"],
        "spurion_formal_F_flat_branch_verified": spurion["decision"]["formal_F_flat_source_times_F_flat_host_branch_exists"],
        "minimal_zero_FI_spurion_D_flat_branch_is_no_go": not spurion["decision"]["zero_FI_minimal_gauged_D_flat_branch_exists"],
        "new_U1S_parent_not_silently_claimed": not spurion["decision"]["new_U1S_gauge_parent_completed"],
        "self_majorana_gravity_escape_verified": pfaffian["checks"]["self_majorana_block_really_evicts_the_V42_gravity_parity_inference"],
        "self_paired_Pfaffian_PS_threshold_class_is_no_go": pfaffian["checks"]["ordinary_self_paired_and_Pfaffian_class_cannot_repair_X_PS_rows"],
        "Z4M_blocks_V42_witness_at_charge_level": g7["decision"]["V42_witness_blocked_by_Z4M"],
        "Z4M_preserves_required_V40_V41_terms": g7["decision"]["all_V40_and_V41_required_terms_preserved"],
        "Z4M_is_not_misrepresented_as_anomaly_complete": not g7["decision"]["candidate_is_anomaly_complete_discrete_gauge_symmetry"],
        "ordinary_no_GS_G7_repair_class_is_no_go": g7["decision"]["no_decoupling_only_ordinary_gauge_repair_exists_under_stated_assumptions"],
        "no_full_gate_promoted": all(not row["closed"] for row in rows),
    }
    report: dict[str, Any] = {
        "schema": "susy-v43-complete-theory-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "active_theory_classification": (
            "a reproducible V43 Pati-Salam EFT research program in which the direct charged-spurion, "
            "self-paired-threshold, and ordinary Z4 matter-selector escape routes have been materially "
            "advanced and fail-closed; not a complete predictive theory"
        ),
        "integrity_checks": integrity,
        "gate_ledger": rows,
        "genuine_V43_advances": {
            "spurion_source": (
                "A charged spurion can protect the source from renormalizable X/Zp portals and yields a formal "
                "coupled F-flat branch, showing precisely which V42 premise must be abandoned."
            ),
            "self_paired_thresholds": (
                "Self-Majorana thresholds are a real exception to the V42 gravity-parity proof, but their "
                "Pati-Salam mixed-anomaly lattice produces a stronger obstruction in the audited class."
            ),
            "G7_selector": (
                "A minimal Z4M charge selector blocks the explicit degree-ten witness and preserves all named "
                "terms, isolating discrete gravitational/product anomaly completion as the remaining cost."
            ),
        },
        "hard_boundaries": [
            "The spurion F-term construction lacks a zero-FI D-flat branch and an anomaly-free U(1)_S parent; a formal FI solution is not a UV completion.",
            "The self-paired threshold theorem is scoped to ordinary PS-unbroken pre-P/Pbar polynomial blocks; it does not rule out every imaginable strong/topological/PS-breaking route.",
            "The Z4M candidate is charge-consistent but not a discrete gauge symmetry under the stated ordinary no-GS decoupling assumptions.",
            "No common global gauge form, Kähler/soft global vacuum, physical spectrum, RG, cosmology, flavour fit, or observable likelihood exists.",
        ],
        "decisive_next_physics": [
            "If pursuing the spurion route, supply an anomaly-free U(1)_S (or another explicit UV origin), a nontrivial D-flat source/compensator sector, and a full coupled Kähler/soft vacuum proof.",
            "If pursuing a product parent, construct a complete PS-breaking or topological/strong-dynamics alternative and compute its full anomaly polynomial and threshold matching rather than extrapolating the audited no-gos.",
            "If pursuing G7 protection, specify a quantized GS/inflow/global discrete completion or a nondecoupling anomaly spectrum for a selector that blocks every remaining invariant-ring class, then perform component matching.",
            "Only after one coherent architecture survives these checks should the G4--G8 spectrum, cosmology, flavour, and prediction program be restarted.",
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
    advances = "\n".join(f"- **{name.replace('_', ' ')}:** {value}" for name, value in report["genuine_V43_advances"].items())
    boundaries = "\n".join(f"- {item}" for item in report["hard_boundaries"])
    next_steps = "\n".join(f"1. {item}" for item in report["decisive_next_physics"])
    return f"""# V43 complete-theory integration audit

Status: {report['status']}

V43 follows every direct escape route left by V42 far enough to distinguish a
real algebraic construction from an actual physics completion.  The spurion,
self-paired threshold, and Z4M selector directions all contain useful exact
subresults, but each still fails a different essential completion condition.

| Gate | Status | V43 advance |
|---|---|---|
{rows}

## Genuine V43 advances

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
        raise RuntimeError("V43 integrated JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V43 integrated Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V43_COMPLETE_THEORY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
