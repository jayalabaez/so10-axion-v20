#!/usr/bin/env python3
"""V71 fail-closed multipath master for the normal-bundle frontier.

The V70 route evidence is preserved byte-canonically.  Only its two unaccepted
Spin(11) order-four candidates F70 and F70_ALT are superseded: V71 proves that
both have an uncanceled mixed normal-gauge anomaly at the second Z4 corner.
F71 records an exact two-corner perturbative witness in the provisional
spinorial U(5)-preimage charge lattice and
the neutral phase theorem, but remains unaccepted because the exotic mass and
decay sector, global quaternionic H-bundle and neutral stabilization,
equivariant Green--Schwarz/Wu--Chern--Simons cocycle and global phases have not
been constructed; the local symmetric-target isometry witness is explicit.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V71"
DATE = "2026-08-30"
SCHEMA = "susy_v71_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V71_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V71_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v71_multipath_g1_frontier_master_audit.py"
ROUTE_MD_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.md"

INPUTS = {
    "v70_master": ROOT / "SUSY_V70_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v71_route": ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json",
}
EXPECTED_CORES = {
    "v70_master": "3e3f624df10419741c1835a8718e4272f8a01d9624f7be3b18c8eaad96cceb98",
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
}
V70_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B70": "cd634111acd82944c0355d2b76fee2fd6340a6695402fd6316e4e624b86c840b",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 28
EXPECTED_REGRESSION_TESTS = 379
EXPECTED_REGRESSION_MANIFEST_SHA256 = "b627bb29520c06ebcb5629ebad6f33c5c2bca8ed8e1e8f4ce0d4f3da7881132b"

STATUS = (
    "V71_MULTIPATH_G1_FRONTIER_MASTER__V70_MASTER_AND_V71_ROUTE_CORES_BOUND__"
    "A60_C_AND_EMBEDDED_B70_LINEAGE_PRESERVED__ONLY_F70_AND_F70ALT_"
    "SUPERSEDED__UNMODIFIED_V70_CANDIDATES_REJECTED_BY_EXACT_Z11_NORMAL_"
    "GAUGE_ANOMALY__FORMER_FOUR_FERMION_REPAIR_RETRACTED_BY_FACTOR_TWO__F71_"
    "CORRECTED_PROVISIONAL_SPINORIAL_U5_PREIMAGE_MODULES_AT_BOTH_Z4_CORNERS_"
    "AND_DELTA_MINUS10_"
    "NEUTRAL_WITNESS_AND_SYMMETRIC_QK_TARGET_ISOMETRY_SELECTED_AS_"
    "CONDITIONAL_CONTRACT__TEN_NEUTRAL_ZERO_MODES_FORCED__SMOOTH_SPIN11_"
    "WCS_PASS_BUT_EQUIVARIANT_ORBIFOLD_WUCS_"
    "ABSENT__F71_NOT_ACCEPTED__NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing bound input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(next(row for row in master["route_matrix"] if row["route_id"] == route_id))


def frozen_v70_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V70_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V70 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 71):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v71_spin11_normal_bundle_equivariant_gs_audit.py"
    if route_test.is_file():
        selected[route_test.name] = route_test
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = [
        {
            "path": name,
            "sha256": file_sha(path),
            "test_functions": len(test_re.findall(path.read_text(encoding="utf-8"))),
        }
        for name, path in sorted(selected.items())
    ]
    return {
        "selection": "all V59-V70 tests plus the V71 route test; the V71 master test is excluded",
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "manifest_sha256": object_sha(rows),
        "expected_manifest_sha256": EXPECTED_REGRESSION_MANIFEST_SHA256,
        "files": rows,
    }


def f71_candidate(v71: Mapping[str, Any]) -> dict[str, Any]:
    route_candidate = v71["F71_repair_candidate"]
    mixed = v71["mixed_normal_gauge_obstruction"]
    neutral = v71["neutral_266_phase_classification"]
    return {
        "id": "F71",
        "kind": "EXACT_LOCAL_TWO_CORNER_WITNESS_IN_PROVISIONAL_SPINORIAL_U5_PREIMAGE__GLOBAL_COMPLETION_OPEN",
        "status": route_candidate["status"],
        "selected": True,
        "accepted": False,
        "same_action_complete": False,
        "supersedes_candidates": ["F70", "F70_ALT"],
        "exact_rejection_of_superseded_candidates": {
            "F70_vector_each_Z4": mixed["F70_bulk_result_each_Z4_corner"],
            "bulk_GS_direction": mixed["standard_bulk_GS"]["restriction_to_U5"],
            "determinant": mixed["standard_bulk_GS"]["determinant_with_F70_vector"],
            "z11_has_V70_local_repair": False,
        },
        "exact_repair_contract": {
            "retracted_four_fermion_module": copy.deepcopy(mixed["minimal_R_compatible_four_fermion_module"]),
            "corrected_charge_lattice_modules": copy.deepcopy(mixed["corrected_spinorial_U5_preimage_modules"]),
            "selected_hybrid": copy.deepcopy(route_candidate["repair_options"]["selected_hybrid"]),
            "neutral_Delta": neutral["bulk_gravitational_trace_factorization"]["unique_Delta"],
            "neutral_zero_mode_minimum": neutral["two_corner_zero_mode_theorem"]["minimum_neutral_chiral_zero_modes"],
            "neutral_266_witness": copy.deepcopy(neutral["explicit_266_dimensional_witness"]),
            "neutral_symmetric_QK_target": copy.deepcopy(neutral["symmetric_quaternionic_Kahler_realization"]),
            "local_fermion_only_residue_cancellation": neutral["conventional_local_fermion_only_no_go_for_factored_residue"]["solution_exists"],
            "continuous_Stueckelberg": copy.deepcopy(v71["equivariant_GS_WuCS_boundary"]["continuous_Stueckelberg"]),
        },
        "required_new_data": copy.deepcopy(route_candidate["required_new_data"]),
        "not_yet_passes": copy.deepcopy(route_candidate["not_yet_passes"]),
        "equivariant_WuCS_constructed": v71["equivariant_GS_WuCS_boundary"]["equivariant_GS_descent_constructed"],
        "naive_WuCS_torsion_divisibility": copy.deepcopy(v71["equivariant_GS_WuCS_boundary"]["naive_orbifold_torsion_divisibility"]),
    }


def candidate_matrix(old_b: Mapping[str, Any], v71: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = [
        copy.deepcopy(row)
        for row in old_b["candidate_matrix"]
        if row["id"] not in {"F70", "F70_ALT"}
    ]
    inherited.append(f71_candidate(v71))
    return inherited


def b71_row(v70: Mapping[str, Any], v71: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v70_row(v70, "B70")
    return {
        "route_id": "B71",
        "name": "Spin(11) order-four normal-bundle and equivariant-GS frontier, fail closed",
        "supersedes_V70_route_id": "B70",
        "supersession_scope": "F70 and F70_ALT candidates only",
        "bound_parent_master_core": EXPECTED_CORES["v70_master"],
        "bound_V71_route_core": EXPECTED_CORES["v71_route"],
        "inherited_B70_row_sha256": object_sha(old_b),
        "inherited_B70_row": old_b,
        "superseded_candidate_ids": ["F70", "F70_ALT"],
        "superseded_candidate_adjudication": {
            "F70": "REJECTED_UNMODIFIED_BY_Z11_MIXED_NORMAL_GAUGE_ANOMALY",
            "F70_ALT": "REJECTED_UNMODIFIED_BY_Z11_MIXED_NORMAL_GAUGE_ANOMALY",
        },
        "V71_selected_candidate": f71_candidate(v71),
        "candidate_matrix": candidate_matrix(old_b, v71),
        "current_bound_action_status": "REJECTED",
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates() -> list[dict[str, Any]]:
    decisions = {
        "G1": "OPEN: F70/F70_ALT are rejected by a local normal-gauge anomaly; F71 has an exact local witness conditional on the spinorial stabilizer preimage but no complete mass/decay, defect/tensor or global action.",
        "G2": "OPEN: no coefficient-level soft spectrum, pole masses or mediator-complete flavor fit is derived.",
        "G3": "OPEN: a symmetric neutral target/isometry and local repair spectra exist, but their global H-bundle, defect masses and complete compactification vacuum/Hessian are not constructed.",
        "G4": "OPEN: the gauge-fixed KK determinant, hierarchy and threshold computation are absent.",
        "G5": "OPEN: Delta=-10 forces at least ten neutral chiral zero modes, whose masses and couplings are not derived.",
        "G6": "OPEN: reheating, defects, charged-singlet relics, moduli and cosmology are not computed.",
        "G7": "OPEN: the local repair has integral scalar isotropy charges, but its discrete-R anomaly, operator ring, global quotient and proton lifetime remain unproved.",
        "G8": "OPEN: the naive smooth WCS restriction fails exact Z4/Z2 torsion-divisibility tests, while no corrected H-cocycle, fixed-stratum eta phase, regulator or global gluing theorem is supplied.",
    }
    return [
        {"gate": gate, "status": "OPEN", "V71_master_closed": False, "decision": decisions[gate]}
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def acceptance_criteria() -> list[dict[str, Any]]:
    rows = [
        ("A7", "global Spin-SU2R-Spin11/flavor lift and Dai-Freed phases", "OPEN"),
        ("A8", "complete Higgs/family/neutral spectrum", "OPEN: at least ten neutral chirals are forced"),
        ("A9", "pointwise local anomaly cancellation", "OPEN: the perturbative local directions align exactly, but no equivariant GS cocycle/global defect action exists"),
        ("A10", "globally gauged Z4R and full operator ring", "OPEN"),
        ("A11", "positive stabilized tensor/compactification vacuum", "OPEN"),
        ("A12", "regulator, KK determinant and thresholds", "OPEN"),
        ("A13", "soft spectrum, unification, flavor and cosmology", "OPEN"),
    ]
    return [{"id": rid, "requirement": req, "status": status} for rid, req, status in rows]


def theory_card(b71: Mapping[str, Any], v71: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V71 fail-closed Spin(11) normal-bundle frontier card",
        "current_bound_action_status": "REJECTED",
        "superseded_candidates": ["F70", "F70_ALT"],
        "selected_candidate": "F71 exact local repair witness in a provisional spinorial U(5) preimage, globally conditional",
        "exact_advances": [
            "common-normalization mixed U1L-(SU5^2,X^2) vector (-1/4,40) and determinant -50 at both Z4 corners",
            "both V70 charged branches have zero U1L^2-X and the same normal-gravity class",
            "general local factorization equation 100+10 Delta+32 Q3+8 Q1=0",
            "factor-two retraction: the former 1_(+/-10) four-fermion module shifts -100 and cannot supply the required -50",
            "corrected provisional spinorial U(5)-preimage modules align both Z4 corners with Q1=Q3=U1L^2-X=X^3=gravity-X=0",
            "z00 uses seven new chirals beyond X/Xbar/S0; z11 uses eight new chirals whose charged states have Y=+/-1",
            "flat torsion holonomy forces no continuous hypercharge or X Stueckelberg mass",
            "bulk Delta=-10 theorem, sharp ten-neutral-zero-mode bound and explicit 266-dimensional witness",
            "explicit Sp(266,1)/(Sp(266)xSp(1)) target and local full-space-group isometry lift for that witness",
            "ordinary half-integral localized fermions cannot replace the remaining factorized tensor inflow",
            "smooth Spin(11) WCS data pass while the SO(11) fallback fails global-form quantization",
            "the naive smooth WCS characteristic fails fixed-stratum divisibility: 2Y=(3,2) in Z4^2 and (1,1) in Z2^2",
        ],
        "open_obligations": copy.deepcopy(v71["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b71["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "F71 is a reproducible exact local perturbative witness conditional on the "
            "spinorial stabilizer preimage, not a new complete "
            "theory.  Its target-space isometry and local spectra are explicit, but "
            "their masses/decays, global combined H-bundle and equivariant/global tensor action "
            "must coexist in one action before any gate can close."
        ),
    }


def source_manifest(scope: Mapping[str, Any]) -> list[dict[str, Any]]:
    paths = [Path(__file__).resolve(), TEST_PATH, *INPUTS.values(), ROUTE_MD_PATH]
    paths.extend(ROOT / row["path"] for row in scope["files"])
    unique = {path.name: path for path in paths}
    return [
        {"path": name, "exists": path.is_file(), "sha256": file_sha(path)}
        for name, path in sorted(unique.items())
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound("v70_master")
    v71 = load_bound("v71_route")
    a = frozen_v70_row(v70, "A60")
    c = frozen_v70_row(v70, "C")
    b = b71_row(v70, v71)
    scope = regression_scope()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_V70_master_core": v70["core_sha256"],
            "V71_route_core": v71["core_sha256"],
            "A60_row_sha256": object_sha(a),
            "B70_row_sha256": object_sha(b["inherited_B70_row"]),
            "C_row_sha256": object_sha(c),
            "only_F70_and_F70ALT_superseded": True,
        },
        "route_matrix": [a, b, c],
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": master_gates(),
        "consolidated_theory_card": theory_card(b, v71),
        "cross_route_composition_rule": {
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
            "rule": "a gate closes only when one hash-bound action satisfies every obligation in that gate",
        },
        "regression_scope": scope,
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "F70_and_F70ALT_rejected_unmodified": True,
            "F71_new_action_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "reason": (
                "V71 converts the missing normal-bundle ledger into an exact no-go for "
                "the unmodified candidates and an exact local charge-lattice repair "
                "witness.  The witness has no completed exotic mass/decay sector, "
                "defect supergravity or equivariant/global "
                "tensor action, so it cannot be promoted."
            ),
        },
        "source_manifest": source_manifest(scope),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    checks = {
        "input_cores": v70["core_sha256"] == EXPECTED_CORES["v70_master"] and v71["core_sha256"] == EXPECTED_CORES["v71_route"],
        "A60_frozen": object_sha(a) == V70_ROW_SHA["A60"],
        "B70_frozen": object_sha(b["inherited_B70_row"]) == V70_ROW_SHA["B70"],
        "C_frozen": object_sha(c) == V70_ROW_SHA["C"],
        "regression_files": scope["file_count"] == EXPECTED_REGRESSION_FILES,
        "regression_tests": scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "regression_manifest": scope["manifest_sha256"] == EXPECTED_REGRESSION_MANIFEST_SHA256,
        "source_manifest_complete": (
            {row["path"] for row in source_manifest(scope)}
            == {
                Path(__file__).name,
                TEST_PATH.name,
                *(path.name for path in INPUTS.values()),
                ROUTE_MD_PATH.name,
                *(row["path"] for row in scope["files"]),
            }
            and all(row["exists"] and row["sha256"] for row in source_manifest(scope))
        ),
        "F71_unaccepted": not b["V71_selected_candidate"]["accepted"],
        "all_gates_open": all(row["status"] == "OPEN" for row in report["gate_ledger"]),
    }
    report["integrity_checks"] = checks
    report["n_failed_integrity_checks"] = sum(not passed for passed in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    failures = [name for name, passed in report["integrity_checks"].items() if not passed]
    if report["n_failed_integrity_checks"] != len(failures):
        failures.append("failure_count")
    if report.get("core_sha256") != canonical_sha(report):
        failures.append("core_exact")
    if failures:
        raise RuntimeError("V71 master validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B71")
    f71 = b["V71_selected_candidate"]
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |" for row in report["gate_ledger"]
    )
    return f"""# V71 multipath G1 frontier master

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Master decision

The V70 evidence is preserved byte-canonically: `A60` and `C` remain top-level
rows, while `B70` is embedded inside its `B71` replacement.  Only the
unaccepted `F70` and `F70_ALT` candidates are superseded.  Both are now rejected
in unmodified form:
their common-normalization mixed normal-gauge vector at the second Z4 corner is
`(-1/4,40)`, while
ordinary bulk Spin(11) GS inflow is restricted to `(1,40)`; the determinant is
`-50`.

`F71` is selected as the next local witness, not accepted as an action.  The
former `1_(+10)+1_(-10)` repair is retracted: its half-integral pair shifts
`(0,-100)` where alignment requires `(0,-50)`.  The corrected z00 ledger uses
the inherited `X,Xbar,S0` plus seven new chirals; the z11 ledger uses eight new
chirals.  Both employ `1_(+/-5)` representations of the provisional spinorial
`U(5)` preimage and give exactly

```text
(U1L-SU5^2,U1L-X^2)=(0,-50),
Q1=Q3=U1L^2-X=X^3=gravity-X=0.
```

The bulk neutral lift still requires `Delta=-10` and forces at least
{f71['exact_repair_contract']['neutral_zero_mode_minimum']}
neutral chiral zero modes.  The sharp 266-dimensional matrix witness has an
explicit local nonlinear realization on `Sp(266,1)/(Sp(266)xSp(1))`.

The spinorial preimage is suggested by V70's localized 16s; a literal
vector-form `U(5)` would forbid the charge-five singlets, so the global quotient
must still be pinned.  At `z11`, the primed charge-five singlets form two
vectorlike `Y=+/-1` charged-lepton pairs.  Bare superpotential masses are
forbidden.  At z11, normal-neutral Kahler bilinears can generate only
gravitino-scale Giudice-Masiero masses.  At z00, each new charged scalar has
continuous normal charge `+1`, so its bilinear requires a charge `-2`
spurion/section or a proven reduction to the discrete symmetry.  The z00 masses,
all decays, discrete-R anomalies and cosmology are not completed.  Because Q/W are flat torsion holonomies with
zero real internal flux, bulk holonomy alone does not force a continuous
hypercharge or X Stückelberg mass.

These facts are exact local perturbative alignment conditions.  The full
defect mass/decay action, global combined H-bundle, equivariant GS/Wu-CS cocycle,
the full compactification vacuum and eta phases are not constructed.  The smooth
Spin(11) parent remains valid, but neither it nor an invalid SO(11) fallback
supplies the orbifold quantum action.

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Strict outcome

{report['strict_master_decision']['reason']}

No accepted extension exists, no cross-route evidence is spliced, and G1-G8
remain OPEN.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V71 master generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V71 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V71 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
