#!/usr/bin/env python3
"""V72 fail-closed multipath master for the Spin(11) G1 frontier.

The V71 master is preserved byte-canonically.  V72 proves that its charge-five
singlets are honest characters of the true spinorial U(5) stabilizer, then
rejects their conventional massive, decaying completion by exact mass/anomaly
and all-order non-derivative local chiral-portal theorems.  F72 replaces charged
defect fermions by an opposite Wess--Zumino transfer whose coefficients are
integral after restriction to U(5)-tilde.  That transfer remains
unaccepted until one supersymmetric equivariant differential cocycle, global
quotient, eta/Dai--Freed phase, and microscopic action are constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V72"
DATE = "2026-08-30"
SCHEMA = "susy_v72_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V72_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V72_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v72_multipath_g1_frontier_master_audit.py"
ROUTE_MD_PATH = ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.md"

INPUTS = {
    "v71_master": ROOT / "SUSY_V71_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v72_route": ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.json",
}
EXPECTED_CORES = {
    "v71_master": "526573519b449adbbbf9c28e321ced5ab33e27f3e5e2b676f9f92df579e6fcc8",
    "v72_route": "46edf8f0943316356f0d5f8f918cc9953f00a10471a65e9c95e92f85904ccec3",
}
V71_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B71": "2b96f66577b93e703096719b3e930bb63ae3e36ad970a34c9609cbc56482dbe9",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 30
EXPECTED_REGRESSION_TESTS = 416
EXPECTED_REGRESSION_MANIFEST_SHA256 = "405ed6ac09bafca7f13e2e7089656eebdc5b3ebb9f165b37740e09e2be73ec89"

STATUS = (
    "V72_MULTIPATH_G1_FRONTIER_MASTER__V71_MASTER_AND_V72_ROUTE_CORES_BOUND__"
    "A60_C_AND_COMPLETE_B71_LINEAGE_PRESERVED__ONLY_F71_CONVENTIONAL_CHARGED_"
    "FERMION_COMPLETION_SUPERSEDED__TRUE_U5TILDE_FIXED_GROUP_AND_CHARGE_FIVE_"
    "CHARACTERS_EXACT__F71_MASS_ANOMALY_AND_ALL_ORDER_NONDERIVATIVE_CHIRAL_"
    "PORTAL_NO_GO_EXACT__"
    "F71_STABLE_CHARGED_RELIC_REJECTED__F72_OPPOSITE_WZ_COEFFICIENTS_PLUS1_"
    "MINUS1_INTEGRAL_AFTER_U5TILDE_RESTRICTION__NO_NEW_CHARGED_EXOTICS__GLOBAL_SUPERSYMMETRIC_"
    "EQUIVARIANT_DIFFERENTIAL_COCYCLE_OPEN__F72_NOT_ACCEPTED__NO_CROSS_ROUTE_"
    "SPLICE__G1_TO_G8_OPEN"
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


def frozen_v71_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V71_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V71 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 72):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v72_spin11_global_form_mass_portal_wz_audit.py"
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
        "selection": "all V59-V71 tests plus the V72 route test; the V72 master test is excluded",
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "manifest_sha256": object_sha(rows),
        "expected_manifest_sha256": EXPECTED_REGRESSION_MANIFEST_SHA256,
        "files": rows,
    }


def inherited_f71(b71: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(next(row for row in b71["candidate_matrix"] if row["id"] == "F71"))


def adjudicated_f71(b71: Mapping[str, Any], v72: Mapping[str, Any]) -> dict[str, Any]:
    old = inherited_f71(b71)
    return {
        "id": "F71",
        "kind": "HONEST_CHARGE_FIVE_LOCAL_REP__CONVENTIONAL_MASSIVE_DECAYING_COMPLETION_REJECTED",
        "status": "REJECTED_AS_CONVENTIONAL_CHARGED_FERMION_COMPLETION",
        "selected": False,
        "accepted": False,
        "same_action_complete": False,
        "inherited_F71_candidate_sha256": object_sha(old),
        "inherited_F71_candidate": old,
        "exact_V72_adjudication": copy.deepcopy(v72["candidate_adjudication"]),
        "mass_and_portal_theorems": copy.deepcopy(v72["charge_five_mass_and_portal_audit"]),
        "phenomenology": copy.deepcopy(v72["discrete_R_running_and_relic_audit"]),
        "local_representation_is_honest": True,
        "total_spin_R_multiplet_and_orbibundle_constructed": False,
        "additional_new_bridge_physics_excluded_by_the_no_go": False,
        "scope_clause": (
            "The rejection applies to the conventional F71 completion with the corrected "
            "module and portals to the existing V70/MSSM fields.  It does not prove that "
            "every possible enlarged theory is impossible."
        ),
    }


def f72_candidate(v72: Mapping[str, Any]) -> dict[str, Any]:
    route = copy.deepcopy(v72["F72_opposite_level_WZ_transfer_candidate"])
    route.update(
        {
            "id": "F72",
            "kind": "OPPOSITE_WZ_TRANSFER_WITH_INTEGRAL_U5TILDE_RESTRICTED_COEFFICIENTS__FULL_QUOTIENT_AND_GLOBAL_SUPERSYMMETRIC_COCYCLE_OPEN",
            "selected": True,
            "accepted": False,
            "same_action_complete": False,
            "supersedes_candidates": ["F71"],
            "true_fixed_group_contract": copy.deepcopy(v72["true_fixed_group_and_global_gluing"]),
            "required_new_data": copy.deepcopy(v72["open_obligations"]),
        }
    )
    return route


def candidate_matrix(b71: Mapping[str, Any], v72: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = [
        copy.deepcopy(row) for row in b71["candidate_matrix"] if row["id"] != "F71"
    ]
    inherited.extend([adjudicated_f71(b71, v72), f72_candidate(v72)])
    return inherited


def b72_row(v71: Mapping[str, Any], v72: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v71_row(v71, "B71")
    return {
        "route_id": "B72",
        "name": "Spin(11) true-global-form, mass/portal no-go, and opposite-WZ frontier",
        "supersedes_V71_route_id": "B71",
        "supersession_scope": "F71 conventional charged-fermion completion only",
        "bound_parent_master_core": EXPECTED_CORES["v71_master"],
        "bound_V72_route_core": EXPECTED_CORES["v72_route"],
        "inherited_B71_row_sha256": object_sha(old_b),
        "inherited_B71_row": old_b,
        "superseded_candidate_ids": ["F71"],
        "superseded_candidate_adjudication": {
            "F71": "REJECTED_CONVENTIONAL_COMPLETION_BY_MASS_ANOMALY_PORTAL_AND_CHARGED_RELIC_NO_GO"
        },
        "V72_selected_candidate": f72_candidate(v72),
        "candidate_matrix": candidate_matrix(old_b, v72),
        "current_bound_action_status": "REJECTED",
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates() -> list[dict[str, Any]]:
    decisions = {
        "G1": "OPEN: F72 aligns both local mixed-anomaly vectors and has integral coefficients after U5tilde restriction, but full-quotient level quantization, a supersymmetric equivariant differential cocycle, regulator, and Dai-Freed phase are not constructed.",
        "G2": "OPEN: no coefficient-level SUSY-breaking sector, soft spectrum, pole masses, or mediator-complete flavor fit is derived.",
        "G3": "OPEN: the neutral P0 identification, global neutral-hyper bundle, compactification vacuum, and positive Hessian are absent.",
        "G4": "OPEN: the gauge-fixed KK determinant, hierarchy, and threshold computation are absent.",
        "G5": "OPEN: V71's forced neutral sector plus the F72 axino/saxion/tensor spectrum have no derived masses and couplings.",
        "G6": "OPEN: F71's stable charged relic rejects that completion; F72 removes the charged exotic but reheating, moduli, defects, and yields remain uncomputed.",
        "G7": "OPEN: the combined Spin(2)-U5tilde-SU2R-flavor quotient, all continuous lifts, full invariant operator ring, and proton lifetime remain unproved.",
        "G8": "OPEN: numerical level cancellation is necessary but not sufficient; torsion refinement, l/lprime gluing, eta phases, regulator, and global Dai-Freed trivialization are absent.",
    }
    return [
        {"gate": gate, "status": "OPEN", "V72_master_closed": False, "decision": decisions[gate]}
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def acceptance_criteria() -> list[dict[str, Any]]:
    rows = [
        ("A7", "global Spin-SU2R-Spin11/flavor lift and Dai-Freed phases", "OPEN"),
        ("A8", "complete Higgs/family/neutral/tensor spectrum", "OPEN"),
        ("A9", "pointwise and globally glued anomaly cancellation", "OPEN: the U5tilde-restricted coefficient check passes; full quotient and differential cocycle absent"),
        ("A10", "globally gauged Z4R and full operator ring", "OPEN"),
        ("A11", "positive stabilized tensor/compactification vacuum", "OPEN"),
        ("A12", "regulator, KK determinant and thresholds", "OPEN"),
        ("A13", "soft spectrum, unification, flavor and cosmology", "OPEN"),
    ]
    return [{"id": rid, "requirement": req, "status": status} for rid, req, status in rows]


def theory_card(b72: Mapping[str, Any], v72: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V72 fail-closed Spin(11) opposite-WZ frontier card",
        "current_bound_action_status": "REJECTED",
        "superseded_candidate": "F71 conventional charged-fermion completion",
        "selected_candidate": "F72 opposite WZ transfer with integral U5tilde-restricted coefficients, globally conditional",
        "exact_advances": [
            "the true connected fixed group is U5tilde=(SU5 x U1X)/Z5 with descent rule k+2x=0 mod 5",
            "charge-five singlets are primitive honest local U5tilde representations",
            "the spin-cover translation lift has the exact central cocycle w^2=c and q w q^-1=c w^-1",
            "the corrected z00 and z11 charge-five modules have no symmetry-preserving anomaly-retaining mass completion",
            "every non-derivative local chiral-superfield portal with one charge-five field and existing V70/MSSM matter is forbidden at all orders",
            "F71 therefore contains a stable Y=+/-1 charged relic within the present local action; nonlocal and new bridge sectors are not excluded",
            "F72 has U5tilde-restricted WZ coefficients +1 at z00 and -1 at z11 in l=c1(chi5)=5 fX normalization",
            "F72 aligns both local vectors to (-1/4,-10) and adds no electrically charged field or SM beta-function shift",
        ],
        "open_obligations": copy.deepcopy(v72["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b72["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "F72 passes an exact necessary U5tilde-restricted coefficient-integrality "
            "check, not full diagonal-quotient level quantization.  Opposite integer "
            "restricted coefficients and a zero necessary sum do not construct the global "
            "supersymmetric equivariant differential cocycle or prove its torsion and eta phases."
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
    v71 = load_bound("v71_master")
    v72 = load_bound("v72_route")
    a = frozen_v71_row(v71, "A60")
    c = frozen_v71_row(v71, "C")
    b = b72_row(v71, v72)
    scope = regression_scope()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_V71_master_core": v71["core_sha256"],
            "V72_route_core": v72["core_sha256"],
            "A60_row_sha256": object_sha(a),
            "B71_row_sha256": object_sha(b["inherited_B71_row"]),
            "C_row_sha256": object_sha(c),
            "only_F71_conventional_completion_superseded": True,
        },
        "route_matrix": [a, b, c],
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": master_gates(),
        "consolidated_theory_card": theory_card(b, v72),
        "cross_route_composition_rule": {
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
            "rule": "a gate closes only when one hash-bound action satisfies every obligation in that gate",
        },
        "regression_scope": scope,
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "F71_conventional_completion_accepted": False,
            "F72_new_action_accepted": False,
            "F72_selected_for_next_frontier": True,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "reason": (
                "V72 makes the charge-five local group statement exact but rejects its "
                "conventional massive, decaying completion.  F72 removes the charged exotics "
                "and supplies opposite WZ coefficients that pass the exact necessary "
                "U5tilde-restriction integrality check, yet full-quotient quantization and the supersymmetric "
                "equivariant differential cocycle and global quantum action do not exist in "
                "the artifact.  It therefore cannot close G1 or any downstream gate."
            ),
        },
        "source_manifest": source_manifest(scope),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    manifest = source_manifest(scope)
    expected_manifest_names = {
        Path(__file__).name,
        TEST_PATH.name,
        *(path.name for path in INPUTS.values()),
        ROUTE_MD_PATH.name,
        *(row["path"] for row in scope["files"]),
    }
    checks = {
        "input_cores": (
            v71["core_sha256"] == EXPECTED_CORES["v71_master"]
            and v72["core_sha256"] == EXPECTED_CORES["v72_route"]
        ),
        "A60_frozen": object_sha(a) == V71_ROW_SHA["A60"],
        "B71_frozen": object_sha(b["inherited_B71_row"]) == V71_ROW_SHA["B71"],
        "C_frozen": object_sha(c) == V71_ROW_SHA["C"],
        "regression_files": scope["file_count"] == EXPECTED_REGRESSION_FILES,
        "regression_tests": scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "regression_manifest": scope["manifest_sha256"] == EXPECTED_REGRESSION_MANIFEST_SHA256,
        "source_manifest_complete": (
            {row["path"] for row in manifest} == expected_manifest_names
            and all(row["exists"] and row["sha256"] for row in manifest)
        ),
        "F71_conventional_completion_rejected": not next(
            row for row in b["candidate_matrix"] if row["id"] == "F71"
        )["accepted"],
        "F72_unaccepted": not b["V72_selected_candidate"]["accepted"],
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
        raise RuntimeError("V72 master validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B72")
    f72 = b["V72_selected_candidate"]
    gate_rows = "\n".join(
        f"- **{row['gate']} — {row['status']}:** {row['decision']}" for row in report["gate_ledger"]
    )
    return f"""# V72 multipath G1 frontier master

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Master decision

The complete V71 master is hash-bound and preserved.  `A60` and `C` remain
top-level rows; the entire `B71` row is embedded unchanged inside `B72`.  Only
the conventional charged-fermion completion of `F71` is superseded.

V72 resolves the local representation question: the fixed group is
`U5tilde=(SU(5) x U(1)X)/Z5`, with descent rule `k+2x=0 mod 5`, so
`1_(+/-5)` are honest primitive characters.  This does not rescue F71.  An
invariant quadratic mass pairs opposite anomaly charges and erases the needed
mixed-anomaly shift; the corrected local rings also forbid every non-derivative
local chiral-superfield portal with one charge-five field and the existing
V70/MSSM fields at all orders.  Within
that local action the lightest `Y=+/-1` state is stable, so F71's conventional
completion is rejected.  This scope excludes neither nonlocal interactions nor
arbitrary enlarged bridge sectors.

`F72` is the selected next candidate, not an accepted action.  It uses no new
charged defect fermions.  In the primitive line normalization
`l=c1(chi5)=5 fX`, its two localized WZ variations have U5tilde-restricted
integer coefficients
`{f72['U5tilde_restricted_local_coefficient_integrality']['restricted_coefficients']['z00']}` and
`{f72['U5tilde_restricted_local_coefficient_integrality']['restricted_coefficients']['z11']}`.
Both corners then have the aligned vector `(-1/4,-10)`, the necessary
coefficient sum is zero, and the one-loop SM beta shift is exactly zero.

Those are necessary U5tilde-restricted facts, not full diagonal-quotient level
quantization.  They do not construct the supersymmetric
axion/linear/tensor multiplet, identify the neutral `P0`, glue `l` to `lprime`,
or define the torsion refinement, regulator, and fixed-stratum eta/Dai–Freed
phase.  The global quotient and translation-cocycle completion are also open.

## Gate ledger

{gate_rows}

## Strict outcome

{report['strict_master_decision']['reason']}

No accepted extension exists, no cross-route evidence is spliced, and G1–G8
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
            raise RuntimeError("V72 master generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V72 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V72 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
