#!/usr/bin/env python3
"""V73 fail-closed multipath master for the Spin(11) G1 frontier.

V73 preserves the complete V72 master and resolves the full-quotient question
that V72 explicitly left open.  The U5tilde-restricted level-one calculation
remains exact, but its pure extension has period 25/4 on an allowed diagonal
cocharacter and is rejected as an ordinary counterterm.  Correlated integral
classes exist, yet they force unmatched R or normal-cubic spectators, and the
two corners leave nu*A*B on their common U(2)xU(3) group.  The plain
opposite-slope tensor is therefore rejected.  The selected, unaccepted
frontier is the existing tensor plus a bridge/inflow sector whose perturbative
curvature is the missing free class.  A spin/eta realization counts as that
bridge, not as an alternative torsion escape.  No gate is closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V73"
DATE = "2026-08-30"
SCHEMA = "susy_v73_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V73_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V73_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v73_multipath_g1_frontier_master_audit.py"
ROUTE_MD_PATH = ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.md"

INPUTS = {
    "v72_master": ROOT / "SUSY_V72_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v73_route": ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.json",
}
EXPECTED_CORES = {
    "v72_master": "eb77fff51a96155a1f162889ae4e073db8837a87bfe4cc804e498dac1eda5530",
    "v73_route": "1ef4890b81885f5a16196865dd8772d9d3b70a20958829481c2397fd9b044c44",
}
V72_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B72": "2ddac54a5762fc6d383cfc026cde34a281631c91a33e2018561d3b8cf9ef9f73",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 32
EXPECTED_REGRESSION_TESTS = 457
EXPECTED_REGRESSION_MANIFEST_SHA256 = (
    "a228af33806b8219568d0670200d94ac3115956cbb4ba2f0138cd95089be28ea"
)

STATUS = (
    "V73_MULTIPATH_G1_FRONTIER_MASTER__V72_MASTER_AND_V73_ROUTE_CORES_BOUND__"
    "A60_C_AND_COMPLETE_B72_LINEAGE_PRESERVED__V72_U5TILDE_RESTRICTED_RESULT_"
    "RETAINED__F72_PURE_FULL_QUOTIENT_EXTENSION_REJECTED_PERIOD_25_OVER_4__"
    "MINIMUM_PURE_MULTIPLIER_FOUR__CORRELATED_PR_AND_PN_CLASSES_INTEGRAL_BUT_"
    "SPECTATORS_UNMATCHED__BULK_SU2R_COEFFICIENT_OPEN__COMMON_C_NO_GO_EXACT__COMMON_"
    "RESIDUE_NU_AB__PLAIN_TENSOR_REJECTED__TENSOR_BRIDGE_INFLOW_FRONTIER_"
    "SELECTED_UNACCEPTED__NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


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
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def frozen_v72_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V72_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V72 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 73):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v73_spin11_full_quotient_supersymmetric_wz_audit.py"
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
        "selection": (
            "all V59-V72 tests plus the V73 route test; the V73 master test is excluded"
        ),
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "manifest_sha256": object_sha(rows),
        "expected_manifest_sha256": EXPECTED_REGRESSION_MANIFEST_SHA256,
        "files": rows,
    }


def adjudicated_f72(b72: Mapping[str, Any], v73: Mapping[str, Any]) -> dict[str, Any]:
    old = copy.deepcopy(
        next(row for row in b72["candidate_matrix"] if row["id"] == "F72")
    )
    quant = v73["ordinary_WZ_quantization_and_correlated_repair"]
    glue = v73["z00_z11_common_subgroup_gluing"]
    return {
        "id": "F72",
        "kind": (
            "U5TILDE_RESTRICTED_RESULT_RETAINED__PURE_FULL_QUOTIENT_ORDINARY_"
            "EXTENSION_REJECTED"
        ),
        "status": "REJECTED_AS_PURE_FULL_QUOTIENT_ORDINARY_WZ_EXTENSION",
        "selected": False,
        "accepted": False,
        "same_action_complete": False,
        "inherited_F72_candidate_sha256": object_sha(old),
        "inherited_F72_candidate": old,
        "retained_exact_scoped_result": {
            "U5tilde_restricted_coefficients": {"z00": 1, "z11": -1},
            "local_vectors_align": True,
            "new_charged_fields": 0,
        },
        "V73_full_quotient_adjudication": {
            "diagonal_period": quant["diagonal_cocharacter_test"]["P_period"],
            "minimal_pure_multiplier": quant["diagonal_cocharacter_test"][
                "minimal_pure_multiplier"
            ],
            "common_residue": glue[
                "opposite_profile_common_restriction_inherited_normalization"
            ],
            "ordinary_single_transfer_glues": glue["ordinary_single_transfer_glues"],
        },
        "spin_eta_or_bridge_refinement_excluded": False,
        "scope_clause": (
            "V72 made only a necessary U5tilde-restricted claim.  V73 rejects the "
            "pure ordinary full-quotient extension, not that scoped calculation and "
            "not every possible bridge/inflow completion.  A spin/eta completion "
            "must carry the missing perturbative curvature and is then such a bridge."
        ),
    }


def f73_candidates(v73: Mapping[str, Any]) -> list[dict[str, Any]]:
    obligations = copy.deepcopy(v73["open_obligations"])
    rows = []
    for raw in v73["F73_candidate_matrix"]:
        if raw["id"] == "F72_PURE":
            continue
        row = copy.deepcopy(raw)
        row["same_action_complete"] = False
        row["required_new_data"] = obligations
        rows.append(row)
    return rows


def candidate_matrix(b72: Mapping[str, Any], v73: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = [
        copy.deepcopy(row) for row in b72["candidate_matrix"] if row["id"] != "F72"
    ]
    inherited.append(adjudicated_f72(b72, v73))
    inherited.extend(f73_candidates(v73))
    return inherited


def b73_row(v72: Mapping[str, Any], v73: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v72_row(v72, "B72")
    candidates = candidate_matrix(old_b, v73)
    selected = copy.deepcopy(
        next(row for row in candidates if row.get("selected"))
    )
    return {
        "route_id": "B73",
        "name": "Spin(11) full-quotient supersymmetric WZ and tensor-bridge frontier",
        "supersedes_V72_route_id": "B72",
        "supersession_scope": "F72 pure ordinary full-quotient WZ extension only",
        "bound_parent_master_core": EXPECTED_CORES["v72_master"],
        "bound_V73_route_core": EXPECTED_CORES["v73_route"],
        "inherited_B72_row_sha256": object_sha(old_b),
        "inherited_B72_row": old_b,
        "superseded_candidate_ids": ["F72_PURE_FULL_QUOTIENT_EXTENSION"],
        "V73_selected_candidate": selected,
        "candidate_matrix": candidates,
        "current_bound_action_status": "REJECTED",
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: the pure F72 extension and plain tensor transfer are rejected; "
            "no bridge/inflow same-action completion with curvature -nu*A*B has "
            "been constructed in the bound action."
        ),
        "G2": (
            "OPEN: no coefficient-level SUSY-breaking sector, complete soft spectrum, "
            "pole masses, or mediator-complete flavor fit is derived."
        ),
        "G3": (
            "OPEN: P0 is not an ordinary neutral hyper or affine axion; its vector-type "
            "source, projected partners, compactification vacuum, and Hessian are absent."
        ),
        "G4": "OPEN: the gauge-fixed KK determinant, hierarchy, and thresholds are absent.",
        "G5": (
            "OPEN: tensor/bridge, axino/saxion, forced neutral, and moduli spectra have "
            "no derived masses, mixings, or stabilized couplings."
        ),
        "G6": (
            "OPEN: the pre-existing tensor itself adds no charged relic, but the "
            "bridge field content and its charged states are open; reheating, tensor/"
            "axion production, moduli, defects, and cosmological yields are uncomputed."
        ),
        "G7": (
            "OPEN: the exact local quotient lattice is known, but the global orbibundle, "
            "continuous lifts, full invariant operator ring, and proton lifetime are not."
        ),
        "G8": (
            "OPEN: the common nu*A*B and antisymmetric R spectators are uncancelled; "
            "torsion, regulator, eta phases, and Dai--Freed trivialization are absent."
        ),
    }
    return [
        {"gate": gate, "status": "OPEN", "V73_master_closed": False, "decision": decisions[gate]}
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def acceptance_criteria() -> list[dict[str, Any]]:
    rows = [
        ("A7", "global Spin-SU2R-Spin11/flavor lift and Dai-Freed phases", "OPEN"),
        ("A8", "complete Higgs/family/neutral/tensor spectrum", "OPEN"),
        (
            "A9",
            "pointwise and globally glued anomaly cancellation",
            "OPEN: pure level fails; correlated spectators and common residue uncancelled",
        ),
        ("A10", "globally gauged Z4R and full operator ring", "OPEN"),
        ("A11", "positive stabilized tensor/compactification vacuum", "OPEN"),
        ("A12", "regulator, KK determinant and thresholds", "OPEN"),
        ("A13", "soft spectrum, unification, flavor and cosmology", "OPEN"),
    ]
    return [{"id": rid, "requirement": req, "status": status} for rid, req, status in rows]


def theory_card(b73: Mapping[str, Any], v73: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V73 fail-closed Spin(11) tensor-bridge/inflow frontier card",
        "current_bound_action_status": "REJECTED",
        "superseded_candidate": "F72 pure ordinary full-quotient WZ extension",
        "selected_candidate": "F73 existing tensor plus required bridge/inflow of curvature -nu A B",
        "exact_advances": [
            "the full descent rules are k+2x=0 mod5 and n+x+r=0 mod2, with x+f=0 mod2 when flavor is installed",
            "the pure level-one class nu ell^2 has period 25/4 and minimum pure integral multiplier four",
            "nu(ell^2+c2R) and nu(ell^2-nu^2/4) are exact correlated integral classes",
            "the provisional 11/16 bulk mixed normal-R attempt is unbound and not certified",
            "the correlated R spectators are antisymmetric and cannot be cancelled by any one symmetric bulk coefficient C",
            "the two corners leave nu A B on common U2xU3",
            "within the displayed degree-four ansatz, the unique SU5 correction that glues is the bulk p1(V10)/4 direction and cannot repair the orthogonal anomaly",
            "a schematic affine N1 axion descent requires the GCS/Bardeen completion and an axino; its curved normal-R supergravity embedding is open",
            "P0 is the partner type, not the affine axion, and fails the ordinary neutral-hyper center pattern",
        ],
        "open_obligations": copy.deepcopy(v73["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b73["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "V73 rejects two concrete extensions, not every possible quantum repair. "
            "The selected tensor-bridge/inflow row is a design target until one "
            "quantized equivariant differential cocycle and microscopic action are "
            "constructed.  A spin/eta realization must supply curvature -nu A B."
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
    v72 = load_bound("v72_master")
    v73 = load_bound("v73_route")
    a = frozen_v72_row(v72, "A60")
    c = frozen_v72_row(v72, "C")
    b = b73_row(v72, v73)
    scope = regression_scope()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_V72_master_core": v72["core_sha256"],
            "V73_route_core": v73["core_sha256"],
            "A60_row_sha256": object_sha(a),
            "B72_row_sha256": object_sha(b["inherited_B72_row"]),
            "C_row_sha256": object_sha(c),
            "only_F72_pure_full_quotient_extension_superseded": True,
        },
        "route_matrix": [a, b, c],
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": master_gates(),
        "consolidated_theory_card": theory_card(b, v73),
        "cross_route_composition_rule": {
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
            "rule": "a gate closes only when one hash-bound action satisfies every obligation in that gate",
        },
        "regression_scope": scope,
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "F72_pure_full_quotient_extension_accepted": False,
            "F73_plain_tensor_accepted": False,
            "F73_tensor_bridge_inflow_selected": True,
            "F73_tensor_bridge_inflow_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "reason": (
                "V73 preserves V72's scoped local result but rejects its pure ordinary "
                "full-quotient extension by the 25/4 period.  Correlated classes repair "
                "local integrality only by adding unmatched spectator anomalies.  The "
                "plain tensor transfer is independently rejected by the common nu*A*B "
                "residue.  A tensor plus bridge/inflow of curvature -nu*A*B is the "
                "selected design frontier, not an accepted action; a spin/eta "
                "realization would be that bridge rather than a torsion alternative."
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
    selected = b["V73_selected_candidate"]
    checks = {
        "input_cores": (
            v72["core_sha256"] == EXPECTED_CORES["v72_master"]
            and v73["core_sha256"] == EXPECTED_CORES["v73_route"]
        ),
        "A60_frozen": object_sha(a) == V72_ROW_SHA["A60"],
        "B72_frozen": object_sha(b["inherited_B72_row"]) == V72_ROW_SHA["B72"],
        "C_frozen": object_sha(c) == V72_ROW_SHA["C"],
        "regression_files": scope["file_count"] == EXPECTED_REGRESSION_FILES,
        "regression_tests": scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "regression_manifest": scope["manifest_sha256"] == EXPECTED_REGRESSION_MANIFEST_SHA256,
        "source_manifest_complete": (
            {row["path"] for row in manifest} == expected_manifest_names
            and all(row["exists"] and row["sha256"] for row in manifest)
        ),
        "F72_pure_rejected": not next(
            row for row in b["candidate_matrix"] if row["id"] == "F72"
        )["accepted"],
        "selected_tensor_bridge": selected["id"] == "F73_TENSOR_BRIDGE",
        "selected_unaccepted": selected["selected"] and not selected["accepted"],
        "no_accepted_candidate": not any(row["accepted"] for row in b["candidate_matrix"]),
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
        raise RuntimeError("V73 master validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B73")
    gate_rows = "\n".join(
        f"- **{row['gate']} -- {row['status']}:** {row['decision']}"
        for row in report["gate_ledger"]
    )
    return f"""# V73 multipath G1 frontier master

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Master decision

The complete V72 master is hash-bound and preserved.  `A60` and `C` remain
top-level rows, while the entire `B72` row is embedded unchanged inside `B73`.
Only the proposed pure ordinary full-quotient extension of F72 is superseded;
V72's explicitly scoped U5tilde-restricted calculation remains exact.

The pure class `nu ell^2` evaluates to `25/4` on the allowed diagonal
cocharacter, and its smallest pure integral multiple is four.  At the two
corners, `ell^2-ellprime^2=A B`, leaving `nu A B` on common U2xU3.  Within the
displayed degree-four SU5-characteristic ansatz, the unique correction that
glues is the bulk `p1(V10)/4` direction and therefore cannot repair the
orthogonal anomaly.

Two correlated level-one classes are integral, but neither completes the
action.  `nu(ell^2+c2R)` forces an antisymmetric R spectator.  The provisional
`11/16` bulk coefficient is not certified because the raw SU2R equivariant
characters remain unbound.  Independently of its value, no one symmetric bulk
coefficient `C` cancels the required `(+1,-1)`.  The normal-line alternative
`nu(ell^2-nu^2/4)` instead adds an unsupported antisymmetric normal-cubic
profile and destroys V71's local factorization.

The plain opposite-slope tensor is rejected.  The selected candidate
`{b['V73_selected_candidate']['id']}` is the existing tensor plus a genuinely
new bridge/inflow sector with curvature `-nu A B`.  A spin/eta realization
with that perturbative curvature is itself the bridge; a torsion-only
refinement cannot cancel the free residue.  The pre-existing tensor adds no
localized axino, but the bridge field content is unknown; this is a design
target rather than a microscopic action.

## Gate ledger

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
            raise RuntimeError("V73 master generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V73 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V73 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
