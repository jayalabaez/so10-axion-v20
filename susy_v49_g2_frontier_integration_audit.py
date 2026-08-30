#!/usr/bin/env python3
"""Integrate the V49 retained-action, regulator, and Wilson-pencils audits.

V49 repairs the source operator census and catches the non-uniform Hc scaling
inside the strong Lambda/epsilon collar.  It also supplies a much larger
restricted-action Wilson witness.  This master applies the frozen C1--C7 G2
contract without promoting a restricted transfer to a complete microscopic
boundary theory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V49_G2_FRONTIER_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V49_G2_FRONTIER_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v49_g2_frontier_integration_audit.py"

INPUTS = {
    "v48_master": ROOT / "SUSY_V48_G2_FRONTIER_INTEGRATION_AUDIT.json",
    "fixed_profile": ROOT / "SUSY_V49_FIXED_PROFILE_SOURCE_REGULATOR_AUDIT.json",
    "retained_action": ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
    "generalized_pencil": ROOT / "SUSY_V49_GENERALIZED_BOUNDARY_PENCIL_AUDIT.json",
}

STATUS = (
    "V49_G2_RETAINED_ACTION_C1_AND_FIXED_ORDER_POLICY_C6_CLOSED__"
    "STRICTLY_4D_SOURCE_REMOVES_SPURIOUS_SOURCE_TOWER__"
    "STRONG_COLLAR_HC_COUNTERTERMS_PROVED_UNSUPPRESSED__"
    "GENERALIZED_RESTRICTED_KERNEL_AND_64_TRACE_PS_MAP_EXECUTABLE__"
    "LOCAL_REGULATOR_COMPLETE_DOMAIN_PROFILE_REMATCH_AND_PHYSICAL_COMPONENT_KERNEL_MISSING__"
    "G2_FAIL_CLOSED__ONE_OF_EIGHT_FULL_GATES_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_hashed_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"input is not an object: {path.name}")
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"stale core hash: {path.name}")
    return value


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in paths
    ]


def closure_assessment() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "name": "fixed_order_action_completeness",
            "status": "pass",
            "landed": (
                "The declared tree O(Lambda^-1) sector now has one coefficient for every "
                "abstract invariant direction: 23 exact pure-source quartics in 12 sectors, "
                "mu_H, direct and conjugate H/Hc portals, mixed Kahler blocks, FI/gauge "
                "coordinates, and an IBP/EOM normal form for one normal derivative."
            ),
            "blocker": "none for C1 at the abstract invariant-tensor level; Cartesian Clebsches belong to C7",
        },
        {
            "id": "C2",
            "name": "explicit_regulator",
            "status": "conditional",
            "landed": (
                "Strictly 4D source multiplets remove the spurious source KK tower, and fixed "
                "profiles plus shortest normal Wilson lines define an explicit gauge-covariant "
                "finite-resolution tree prescription."
            ),
            "blocker": (
                "The Wilson-line source coupling is bilocal over epsilon.  It is not a point-local "
                "microscopic 5D wall unless finite-range bilocality is admitted as the regulator "
                "class or localized by deconstruction/constrained transport fields."
            ),
        },
        {
            "id": "C3",
            "name": "variational_domain_and_self_adjointness",
            "status": "partial",
            "landed": (
                "The general holomorphic A,Xi,C collar generator is Hamiltonian and its transfer "
                "is symplectic; passive endpoint pencils have a positive-metric self-adjoint enlargement."
            ),
            "blocker": (
                "All retained strong-collar, Kahler, O7/O8, brane-bulk, and auxiliary blocks have "
                "not been varied together into one complete domain."
            ),
        },
        {
            "id": "C4",
            "name": "positive_full_kinetic_form",
            "status": "partial",
            "landed": (
                "Positive direct/auxiliary endpoint metrics and the monotone Hermitian pencil "
                "identity are executable; the restricted witnesses have finite positive norms."
            ),
            "blocker": (
                "Positivity of the same complete strong-collar action after every mixed Kahler, "
                "normal-derivative, and source-dependent block is assembled remains unproved."
            ),
        },
        {
            "id": "C5",
            "name": "counterterm_and_matching_scheme",
            "status": "partial",
            "landed": (
                "The matching scale, finite even/odd profiles, coefficient coordinates, and "
                "renormalization inputs are declared."
            ),
            "blocker": (
                "No independent second-profile rematch or loop/subtraction calculation shows "
                "profile and scale independence through O(Lambda^-1)."
            ),
        },
        {
            "id": "C6",
            "name": "selector_and_naturalness_policy",
            "status": "pass",
            "landed": (
                "Every retained invariant direction has an independent matching coefficient; "
                "the Hc and odd-profile zeros are identified as finite-part choices rather than "
                "symmetry claims, and higher sectors have an explicit remainder assignment."
            ),
            "blocker": "none for the declared fixed-order policy",
        },
        {
            "id": "C7",
            "name": "action_to_full_tower_Wilson_matching",
            "status": "partial",
            "landed": (
                "A generalized Hermitian endpoint pencil, exact restricted Schur kernel, 64-trace "
                "PS map, and pole/residue/locality/decoupling witnesses are executable."
            ),
            "blocker": (
                "The kernel uses the zero-Hc-counterterm V48 transfer.  The full A,Xi,C path-ordered "
                "collar, normalized SO(10)->PS tensors, derivative-current Clebsches, and complete "
                "physical Wilson coefficient array have not been matched together."
            ),
        },
    ]


def exact_results(
    fixed: Mapping[str, Any], action: Mapping[str, Any], pencil: Mapping[str, Any]
) -> list[dict[str, Any]]:
    strong = action["strong_wall_scaling_correction"]
    quartics = action["exact_pure_source_quartic_basis"]
    ps = pencil["full_64_PS_component_certificate"]
    return [
        {
            "id": "E30",
            "result": "source-spectrum repair",
            "statement": (
                "The source fields depend only on (x,theta), so their transverse mode count is "
                "exactly zero and the V47 4D source Hessian is retained."
            ),
            "value": fixed["strictly_4D_source_action"],
        },
        {
            "id": "E31",
            "result": "non-uniform strong-wall Hc scaling",
            "statement": (
                "At m=0, Hc(s)=-(s/epsilon)A H0.  Even-profile Hc Xi Hc and odd-profile "
                "H C Hc therefore remain O(1), so they are leading regulator coordinates."
            ),
            "value": strong,
        },
        {
            "id": "E32",
            "result": "exact pure-source quartic census",
            "statement": "Twelve neutral monomial sectors contain 23 independent complex invariant directions.",
            "value": {
                "sector_count": quartics["sector_count"],
                "direction_count": quartics["direction_count"],
            },
        },
        {
            "id": "E33",
            "result": "retained boundary-action normal form",
            "statement": (
                "The fixed-order action includes mu_H, all direct/conjugate collar portals, "
                "leading Hc-Hc and odd-profile coordinates, mixed Kahler sectors, and the "
                "two-coordinate O7/O8/profile IBP quotient per channel."
            ),
            "value": action["adversarial_verdict"],
        },
        {
            "id": "E34",
            "result": "general strong-collar symplectic transfer",
            "statement": (
                "For symmetric A and Xi the full holomorphic collar generator is Hamiltonian; "
                "the representative path-ordered transfer preserves the symplectic form."
            ),
            "value": action["general_full_collar_transfer"],
        },
        {
            "id": "E35",
            "result": "restricted generalized Wilson witness",
            "statement": (
                "The executable restricted kernel has a 64-coordinate PS trace map and passes "
                "its Hermiticity, pole, residue, Euclidean locality, and decoupling checks."
            ),
            "value": {
                "coordinate_count": ps["coordinate_count"],
                "nonzero_vertex_entries": ps["independent_nonzero_vertex_entries"],
                "pencil_verdict": pencil["G2_decision"]["verdict"],
            },
        },
        {
            "id": "E36",
            "result": "V49 fail-closed decision",
            "statement": (
                "C1 and C6 pass, while C2 is conditional and C3/C4/C5/C7 remain partial. "
                "The seven-clause conjunction is false; G2 is not promoted."
            ),
            "value": {"full_gate_count": 1, "G2_closed": False},
        },
    ]


def unresolved_defects() -> list[dict[str, str]]:
    return [
        {
            "id": "D8",
            "defect": "finite_range_bilocal_regulator",
            "statement": (
                "The shortest normal Wilson line makes the smearing gauge covariant but bilocal. "
                "Localize it by finite deconstruction/constrained transport, or explicitly adopt "
                "cutoff-range bilocality in the G2 regulator contract."
            ),
        },
        {
            "id": "D9",
            "defect": "complete_strong_collar_transfer_missing",
            "statement": (
                "All allowed Hc-Hc and odd-profile H-Hc matrices are O(1) in the strong wall and "
                "must enter one path-ordered transfer; the current Wilson witness uses their zero point."
            ),
        },
        {
            "id": "D10",
            "defect": "complete_domain_and_positive_norm_missing",
            "statement": (
                "The full retained collar, endpoint Kahler, derivative, auxiliary, and counterterm "
                "blocks have not been varied and certified positive together."
            ),
        },
        {
            "id": "D11",
            "defect": "profile_rematching_missing",
            "statement": (
                "An independent profile calculation has not shown counterterm-rematched agreement "
                "through O(Lambda^-1)."
            ),
        },
        {
            "id": "D12",
            "defect": "physical_component_kernel_missing",
            "statement": (
                "Normalized SO(10)-to-PS Cartesian tensors and derivative-current Clebsches are "
                "still abstract, so the complete physical Wilson coefficient array is absent."
            ),
        },
    ]


def updated_gate_ledger(v48: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v48["gate_ledger"])
    for row in ledger:
        if row["gate"] == "G2":
            row.update(
                {
                    "closed": False,
                    "advance": (
                        "V49 completes the retained action at the abstract invariant-tensor level, "
                        "proves 23 pure-source quartic directions and the O(1) strong-collar Hc "
                        "correction, and supplies a 64-trace restricted Wilson witness."
                    ),
                    "blocker": (
                        "The regulator is cutoff-range bilocal, the full A/Xi/C strong-collar "
                        "action has not been assembled into one positive self-adjoint kernel, "
                        "profile rematching is absent, and physical component tensors remain abstract."
                    ),
                }
            )
    return ledger


def updated_stage_ledger(v48: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v48["stage_ledger"])
    for row in ledger:
        if row["stage"] == "S0":
            row["passed"] = (
                "exact coupled neutral-210 branch, 443 generic massive physical source chirals, "
                "and a strictly 4D source prescription with no source KK tower"
            )
            row["missing"] = (
                "complete same-action source/collar Kahler and counterterm norm, radion dynamics, "
                "and global branch selection"
            )
        elif row["stage"] == "S2":
            row["status"] = "OPEN_WITH_GENERAL_STRONG_COLLAR_GENERATOR"
            row["passed"] = (
                "restricted exact V48 transfer, the corrected O(1) Hc scaling, and a Hamiltonian "
                "general A/Xi/C collar generator"
            )
            row["missing"] = (
                "complete path-ordered same-action transfer/domain/norm, local regulator decision, "
                "full pole tower and thresholds"
            )
        elif row["stage"] == "S3":
            row["status"] = "OPEN_WITH_COMPLETE_ABSTRACT_ACTION_AND_RESTRICTED_64_TRACE_KERNEL"
            row["passed"] = (
                "23 exact source quartics, complete abstract retained action, IBP/EOM normal form, "
                "and restricted 64-trace PS Schur kernel"
            )
            row["missing"] = (
                "same-action strong-collar Wilson kernel, normalized component Clebsches, B/L ring, "
                "physical Wilson coefficients and rates"
            )
    return ledger


def build_report() -> dict[str, Any]:
    loaded = {name: load_hashed_json(path) for name, path in INPUTS.items()}
    v48 = loaded["v48_master"]
    fixed = loaded["fixed_profile"]
    action = loaded["retained_action"]
    pencil = loaded["generalized_pencil"]
    clauses = closure_assessment()
    passed = [row["id"] for row in clauses if row["status"] == "pass"]
    gates = updated_gate_ledger(v48)

    integrity = {
        "all_input_core_hashes_valid": True,
        "V48_started_with_only_G1_closed": sum(bool(row["closed"]) for row in v48["gate_ledger"]) == 1,
        "strictly_4D_sources_have_no_KK_tower": (
            fixed["numerical_certificate"]["source_field_count_with_y_dependence"] == 0
            and not fixed["numerical_certificate"]["source_KK_tower_present"]
        ),
        "regulator_artifact_rejects_microscopic_closure": not fixed["decision"][
            "regulator_microscopic_candidate_condition_closed"
        ],
        "strong_collar_Hc_terms_are_unsuppressed": action["integrity_checks"][
            "strong_wall_HcHc_is_unsuppressed"
        ]
        and action["integrity_checks"]["strong_wall_odd_HcH_is_unsuppressed"],
        "quartic_census_is_12_sectors_23_directions": (
            action["exact_pure_source_quartic_basis"]["sector_count"] == 12
            and action["exact_pure_source_quartic_basis"]["direction_count"] == 23
        ),
        "full_collar_generator_certificate_is_symplectic": action["integrity_checks"][
            "general_collar_transfer_is_symplectic"
        ],
        "restricted_pencil_integrity_passes": (
            pencil["n_failed_integrity_checks"] == 0
            and all(pencil["integrity_checks"].values())
        ),
        "restricted_pencil_rejects_G2_closure": not pencil["G2_decision"]["closed"],
        "exactly_C1_and_C6_pass": passed == ["C1", "C6"],
        "G2_conjunction_is_false": len(passed) != len(clauses),
        "only_G1_is_closed_after_V49": (
            sum(bool(row["closed"]) for row in gates) == 1
            and next(row for row in gates if row["gate"] == "G1")["closed"]
        ),
    }
    failures = [name for name, value in integrity.items() if not value]
    if failures:
        raise RuntimeError("V49 master integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v49-g2-frontier-integration-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "G2_closed": False,
            "full_gates_closed": 1,
            "closed_gates": ["G1"],
            "statement": (
                "V49 closes the retained-action census and fixed-order coefficient policy, "
                "but not the full G2 conjunction.  The exact strong-wall correction makes the "
                "missing Hc/counterterm transfer more important, not less."
            ),
            "claim_scope": (
                "mathematical EFT progress only; not a complete theory, UV completion, "
                "phenomenological fit, or empirical validation"
            ),
        },
        "frozen_G2_contract": v48["frozen_G2_contract"],
        "G2_closure_assessment": clauses,
        "number_of_clauses": len(clauses),
        "fully_passed_clauses": passed,
        "V49_exact_results": exact_results(fixed, action, pencil),
        "unresolved_defects": unresolved_defects(),
        "smallest_next_closure_patch": [
            "Localize the source coupling with finite deconstruction or constrained covariantly constant transport fields, unless cutoff-range bilocality is explicitly accepted.",
            "Insert the complete A,Xi,C and O7/O8 tensor families into one path-ordered strong-collar transfer and vary the full retained action.",
            "Assemble and prove positivity of the complete bulk+collar+endpoint generalized norm.",
            "Rematch a second smooth profile and show counterterm-adjusted agreement through O(Lambda^-1).",
            "Publish normalized SO10-to-PS tensors and the resulting complete physical Wilson coefficient array.",
        ],
        "gate_ledger": gates,
        "stage_ledger": updated_stage_ledger(v48),
        "route_decision": (
            "Continue the neutral-210 route only as an open EFT research program.  Do not promote "
            "G2 until one local or explicitly admitted regulator carries the complete retained "
            "action, positive domain, profile rematch, and component Wilson kernel together."
        ),
        "input_core_hashes": {
            name: value["core_sha256"] for name, value in loaded.items()
        },
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            {
                "title": "Marti--Pomarol: 5D supersymmetry in N=1 superfields",
                "url": "https://arxiv.org/abs/hep-th/0106256",
            },
            {
                "title": "Hebecker: gauge-covariant brane operators",
                "url": "https://arxiv.org/abs/hep-ph/0112230",
            },
            {
                "title": "von Gersdorff et al.: interval boundary action principle",
                "url": "https://arxiv.org/abs/hep-th/0411133",
            },
            {
                "title": "del Aguila et al.: thin-defect EFT and classical renormalization",
                "url": "https://arxiv.org/abs/hep-ph/0601222",
            },
            {
                "title": "Barcelo--Mitra--Moreau: finite-width brane/KK limit ordering",
                "url": "https://arxiv.org/abs/1408.1852",
            },
            {
                "title": "Nath--Syed: SO(10) spinor contraction channels",
                "url": "https://arxiv.org/abs/hep-th/0109116",
            },
        ],
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    clauses = "\n".join(
        f"| {row['id']} | {row['name']} | {row['status']} | {row['landed']} | {row['blocker']} |"
        for row in report["G2_closure_assessment"]
    )
    exact = "\n".join(
        f"- **{row['id']} — {row['result']}:** {row['statement']}"
        for row in report["V49_exact_results"]
    )
    defects = "\n".join(
        f"- **{row['id']} — {row['defect']}:** {row['statement']}"
        for row in report["unresolved_defects"]
    )
    patch = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["smallest_next_closure_patch"], 1)
    )
    gates = "\n".join(
        f"| {row['gate']} | {'closed' if row['closed'] else 'open'} | {row['advance']} | {row['blocker']} |"
        for row in report["gate_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']})" for row in report["primary_sources"]
    )
    return f"""# V49 G2 frontier integration audit

Status: `{report['status']}`

## Scientific verdict

V49 makes two closure-grade advances: the fixed-order retained action is now
complete at the abstract invariant-tensor level (`C1`), and every retained
coefficient has an explicit matching/naturalness policy (`C6`).  It also
removes the spurious source KK tower and expands the Wilson witness to 64 PS
trace coordinates.

**G2 nevertheless remains open.  Full gates closed: 1 / 8 — G1 only.**

The decisive correction is that the exact strong collar has

```text
H(s)=H0,
Hc(s)=-(s/epsilon) A H0.
```

Consequently `Hc Xi Hc` and odd-profile `H C Hc` terms are `O(1)`, not
`O(epsilon^2)` or `O(epsilon)`.  The V48 transfer is exact only at their
zero-finite-part matching point.  A complete G2 calculation must recompute the
path-ordered transfer with all of them present.

This is mathematical EFT progress, not a complete theory, UV completion,
phenomenological fit, or empirical validation.

## What V49 genuinely solved

{exact}

## Frozen C1--C7 decision

`G2_closed iff C1 through C7 all pass for the same retained action`.

| Clause | Requirement | Status | Landed | Remaining blocker |
|---|---|---|---|---|
{clauses}

Only `C1` and `C6` pass completely.  The conjunction is false.

## Exact remaining defects

{defects}

## Smallest next closure patch

{patch}

## G1--G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
{gates}

## Route decision

{report['route_decision']}

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    if report["n_failed_integrity_checks"] != 0 or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    if report["fully_passed_clauses"] != ["C1", "C6"]:
        raise RuntimeError("G2 clause decision drifted")
    if report["scientific_verdict"]["G2_closed"]:
        raise RuntimeError("G2 was overpromoted")
    if sum(bool(row["closed"]) for row in report["gate_ledger"]) != 1:
        raise RuntimeError("gate ledger drifted")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V49 master JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V49 master Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V49_G2_FRONTIER_INTEGRATION_AUDIT_CHECK_PASS")
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
