#!/usr/bin/env python3
"""Integrated, fail-closed V41 theory audit.

V41 is deliberately an evidence ledger.  It connects the V40 ``U(1)_F ->
Z9`` selector to an explicit canonical source branch and a Dirac-neutrino
messenger, classifies a previously ambiguous mixed four-matter operator, and
tests two independent UV/anomaly directions.  None of those results supplies
the physical inputs required for a full G1--G8 closure, so this module refuses
to promote a gate merely because a useful EFT subproblem has been solved.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V41_COMPLETE_THEORY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V41_COMPLETE_THEORY_AUDIT.md"

INPUTS = {
    "v40": ROOT / "SUSY_V40_COMPLETE_THEORY_AUDIT.json",
    "mixed": ROOT / "SUSY_V41_MIXED_FOUR_MATTER_AUDIT.json",
    "dirac": ROOT / "SUSY_V41_DIRAC_MESSENGER_AUDIT.json",
    "rsym": ROOT / "SUSY_V41_FULL_VEV_RSYM_NO_GO_AUDIT.json",
    "product": ROOT / "SUSY_V41_U1F_PRODUCT_CROSS_COMPLETION.json",
    "source": ROOT / "SUSY_V41_Z9_U1F_SOURCE_SECTOR_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v41_complete_theory_audit.py",
    "test_susy_v41_complete_theory_audit.py",
    "susy_v40_complete_theory_audit.py",
    "susy_v41_mixed_four_matter_audit.py",
    "susy_v41_dirac_messenger_audit.py",
    "susy_v41_r5r_full_vev_selector_audit.py",
    "susy_v41_u1f_product_cross_completion.py",
    "susy_v41_z9_u1f_source_sector_audit.py",
)
STATUS = (
    "V41_INTEGRATED__SOURCE_MESSENGER_AND_OPERATOR_CLASSIFICATION_ADVANCES__"
    "TWO_UV_NO_GOS__ZERO_OF_EIGHT_FULL_GATES_CLOSED"
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
            raise RuntimeError(f"required V41 input missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"required V41 input is not an object: {path.name}")
        if canonical_sha(payload) != payload.get("core_sha256"):
            raise RuntimeError(f"required V41 input checksum failed: {path.name}")
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
    v40 = inputs["v40"]
    mixed = inputs["mixed"]
    dirac = inputs["dirac"]
    rsym = inputs["rsym"]
    product = inputs["product"]
    source = inputs["source"]
    threshold = product["continuous_cross_triangle_audit"]
    source_branch = source["canonical_F_D_flat_branch"]
    mixed_rows = mixed["four_matter_tensor_classification"]
    r_rows = rsym["R5_core_anomaly"]["core_doubled_rows_D"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "advance": (
                "The U(1)_F x U(1)_X x U(1)_H cross block has an explicit four-singlet "
                "P/Pbar-threshold EFT cancellation: the five genuine F-X/H triangle rows go "
                f"from {threshold['baseline_V40_rows']} to {threshold['net_rows']}.  Independently, "
                "an all-visible-VEV Z5R source witness retains the type-I operator while forbidding "
                "the stated same-orientation sources at every visible-VEV order."
            ),
            "blocker": (
                "The threshold uses P/Pbar with primitive X charges and therefore breaks the old "
                "U(1)_X/Z66 direction; it leaves the other X/H, gravity, discrete-R, global/bordism, "
                "and threshold-matching data unresolved.  The all-visible-VEV R witness has nonuniversal "
                f"equal-level doubled anomaly rows {r_rows}, and the all-order theorem rules out every "
                "protective minimal type-I one-axion equal-level Z_N^R branch.  No common microscopic "
                "product completion is supplied."
            ),
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": (
                "A canonical F/D-flat U(1)_F source branch is explicit: ThetaPlus ThetaMinus=mu_F^2, "
                "all anomalons and messengers vanish, and all listed source/anomalon pairs have "
                "full-rank mass witnesses."
            ),
            "blocker": (
                "No coupled PS/PQ/U(1)_F Kähler/soft vacuum, component mass matrices, physical pole "
                "spectrum, or covariance calculation exists."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": (
                "The isolated canonical source branch leaves exact Z9 because its only nonzero "
                f"U(1)_F VEV charges are {source_branch['unbroken_gauge_subgroup']['VEV_charges']}."
            ),
            "blocker": (
                "STheta, X, and Zp have identical declared product signatures, so allowed host-driver "
                "cross couplings invalidate a symmetry-only sequestering claim.  General Kähler/soft "
                "data can also condense Z9-charged fields; global minima, thermal history, and tunnelling "
                "are not derived."
            ),
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "The new source, anomaly, and Dirac-messenger fields make the enlarged mediation burden explicit.",
            "blocker": "No hidden W/K/f, mediation mechanism, mu/Bmu derivation, radiative EWSB calculation, or collider likelihood is supplied.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": v40["gate_ledger"][4]["advance"],
            "blocker": (
                "The V41 selector/source additions do not supply a selector-compatible dark sector, "
                "physical spectrum, coupled Boltzmann/PQ evolution, or likelihood."
            ),
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": (
                "V41 identifies the threshold inventory that must enter a fresh RG calculation: U(1)_F "
                "Higgs/stabilizer fields, anomalons, the Dirac messenger, and the conditional P/Pbar "
                "cross-anomaly packet."
            ),
            "blocker": "No physical boundary conditions, threshold matching, complete coupled beta system, or uncertainty propagation is derived.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": (
                "The apparent selector-neutral mixed example X Q Q Qc Qc is now correctly classified "
                "as a two-delta SU(4) invariant, not a conventional Delta-B=Delta-L=1 epsilon source. "
                "All matter-only net +/-4 SU(4) epsilon classes through degree twelve are Z9-forbidden; "
                f"the enumeration contains {mixed_rows['all_matter_only_net_plus_or_minus_four_classes_through_degree_12']['row_count']} rows."
            ),
            "blocker": (
                "This is not a proton lifetime.  Pati-Salam-breaking VEV insertions, Kähler/soft and "
                "nonholomorphic operators, heavy thresholds, component matching, SUSY dressing, RG, flavour, "
                "and hadronic matrix elements remain uncomputed.  The Z9 all-declared-VEV statement remains "
                "conditional on the noncondensing branch and a full product UV completion."
            ),
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": (
                "A renormalizable Pati-Salam and U(1)_F/Z9-compatible vectorlike messenger explicitly "
                f"matches to {dirac['tree_level_matching']['matched_superpotential']}."
            ),
            "blocker": (
                "No three-family texture, charged-fermion/PMNS/CKM fit, threshold/pole spectrum, flavour "
                "likelihood, or withheld-observable prediction is present."
            ),
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = load_inputs()
    v40 = inputs["v40"]
    mixed = inputs["mixed"]
    dirac = inputs["dirac"]
    rsym = inputs["rsym"]
    product = inputs["product"]
    source = inputs["source"]
    rows = gate_ledger(inputs)
    integrity = {
        "all_input_cores_verify": True,
        "V40_started_with_zero_full_gates": v40["established_full_predictive_closed_count"] == 0,
        "canonical_U1F_to_Z9_source_branch_exists": source["decision"]["isolated_renormalizable_source_branch_exists"],
        "source_branch_preserves_exact_Z9": source["decision"]["exact_Z9_is_preserved_on_that_branch"],
        "source_branch_masses_all_listed_U1F_fields": source["decision"]["all_listed_anomalon_and_U1F_breaking_fields_massable_on_a_rank_witness"],
        "source_host_mixing_boundary_is_explicit": not source["host_embedding_boundary"]["embedding_is_complete"],
        "Dirac_messenger_matches_tree_level_operator": dirac["integrity_checks"]["tree_level_matching_explicit"],
        "Dirac_messenger_preserves_incremental_local_anomalies": dirac["integrity_checks"]["messenger_anomaly_increment_vanishes"],
        "mixed_QQ_QcQc_is_not_a_conventional_epsilon_source": mixed["integrity_checks"]["mixed_two_plus_two_is_Z9_neutral_but_not_epsilon"],
        "net_four_epsilon_matter_classes_through_degree_twelve_are_Z9_forbidden": mixed["integrity_checks"]["all_net_plus_or_minus_four_matter_only_classes_through_12_are_Z9_forbidden"],
        "P_Pbar_packet_cancels_five_genuine_F_X_H_triangle_rows": product["checks"]["all_genuine_F_X_H_triangle_rows_cancel"],
        "theta_only_residual_preserving_product_repair_is_no_go": product["checks"]["theta_only_residual_preserving_obstruction_is_nonvacuous"],
        "simple_one_axion_GS_subcase_is_obstructed": product["simple_quantized_GS_subcase"]["integer_solution"]["k_XH"] is None,
        "all_visible_VEV_R_witness_blocks_same_orientation_sources": rsym["decision"]["all_declared_visible_VEV_same_orientation_source_block"],
        "all_order_single_GS_type_I_R_completion_is_no_go": not rsym["decision"]["equal_level_single_GS_discrete_R_completion_found"],
        "no_full_gate_promoted": all(not row["closed"] for row in rows),
    }
    report: dict[str, Any] = {
        "schema": "susy-v41-complete-theory-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "active_theory_classification": (
            "a reproducible V41 Pati-Salam EFT research program with a canonical U(1)_F-to-Z9 source "
            "branch, a Dirac-messenger matching construction, exact restricted selector theorems, and "
            "two fail-closed UV/anomaly no-gos; not a complete predictive theory"
        ),
        "integrity_checks": integrity,
        "gate_ledger": rows,
        "genuine_V41_advances": {
            "source_sector": (
                "A renormalizable canonical U(1)_F source sector realizes a SUSY F/D-flat branch, "
                "unbroken Z9, and full-rank anomalon mass witnesses."
            ),
            "Dirac_neutrino_route": (
                "A vectorlike Pati-Salam messenger generates Q H Sc NDirac at tree level without breaking "
                "the U(1)_F/Z9 selector or changing local anomalies."
            ),
            "operator_classification": (
                "The neutral 2x4 plus 2xbar4 class is B/L conserving delta-tensor structure; the actual "
                "net-four epsilon classes are selector forbidden in the audited matter-only ring."
            ),
            "UV_boundaries": (
                "A P/Pbar EFT packet cancels the five F-X/H cross triangles but exits the old residual-X "
                "direction; theta-only residual-preserving thresholds and simple one-axion GS cannot repair "
                "that block.  An independent all-visible-VEV type-I single-GS discrete-R architecture is "
                "ruled out at every protective order."
            ),
        },
        "hard_boundaries": [
            "A canonical F/D-flat branch is not a coupled Kähler/soft global vacuum or a physical spectrum.",
            "Allowed X/Zp/STheta cross couplings mean the new source cannot be declared sequestered from the host theory by the listed symmetries alone.",
            "The P/Pbar cross-anomaly packet is an EFT threshold and not a product UV completion because it breaks the old U(1)_X/Z66 direction and leaves other anomaly rows open.",
            "The all-visible-VEV type-I R-symmetry no-go removes a broad minimal repair class; formal multi-axion arithmetic is not a quantized UV completion.",
            "Restricted source-ring and matter-only operator results are not a proton lifetime without full matching and matrix elements.",
            "The V39 pure-Yukawa dark point remains excluded by its sub-PQ Landau pole.",
        ],
        "decisive_next_physics": [
            "Specify one common microscopic product completion: full gauge/global form, integral charge lattice, spectrum, all triangle/discrete/gravitational/bordism anomalies, and threshold matching.",
            "Build the coupled PS/PQ/U(1)_F W/K/f and soft sector, explicitly resolve X/Zp/STheta mixing, and prove a viable global vacuum with all Z9-charged fields noncondensing.",
            "Extend the G7 audit through PS-breaking and nonholomorphic operators, then calculate component Wilson coefficients, dressing, RG evolution, and hadronic proton-decay observables.",
            "Construct a three-family Dirac flavour sector and derive charged-fermion plus PMNS/CKM fits, pole spectrum, cosmology, and genuine out-of-sample likelihood tests.",
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
    advances = "\n".join(f"- **{name.replace('_', ' ')}:** {value}" for name, value in report["genuine_V41_advances"].items())
    boundaries = "\n".join(f"- {item}" for item in report["hard_boundaries"])
    next_steps = "\n".join(f"1. {item}" for item in report["decisive_next_physics"])
    return f"""# V41 complete-theory integration audit

Status: {report['status']}

V41 turns the strongest V40 selector direction into a more concrete research
EFT: it now has a canonical source branch, mass witnesses, a tree-level Dirac
messenger, and a corrected four-matter classification.  It also narrows the
UV options with two exact no-go results.  Those are real advances, but the
inputs needed to promote any G1--G8 gate remain absent.

| Gate | Status | V41 advance |
|---|---|---|
{rows}

## Genuine V41 advances

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
        raise RuntimeError("V41 integrated JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V41 integrated Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V41_COMPLETE_THEORY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
