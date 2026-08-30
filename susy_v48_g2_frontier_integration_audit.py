#!/usr/bin/env python3
"""Integrate the V48 G2 regulator, operator and adversarial audits.

The V48 calculations make a substantial microscopic advance, but this master
audit deliberately applies a same-action closure test: the regulated action,
its positive self-adjoint domain, and its Wilson kernel must contain the same
retained operators.  The present artifacts do not yet satisfy that test, so G2
remains open while G1 remains the only closed full gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V48_G2_FRONTIER_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V48_G2_FRONTIER_INTEGRATION_AUDIT.md"

INPUTS = {
    "v47_master": ROOT / "SUSY_V47_G1_CLOSURE_FRONTIER_AUDIT.json",
    "resolved_wall": ROOT / "SUSY_V48_RESOLVED_SOURCE_WALL_AUDIT.json",
    "operator_wilson": ROOT / "SUSY_V48_SOURCE_OPERATOR_WILSON_AUDIT.json",
    "adversarial_contract": ROOT / "SUSY_V48_G2_ADVERSARIAL_CLOSURE_AUDIT.json",
}

SOURCE_FILES = (
    Path(__file__).name,
    "test_susy_v48_g2_frontier_integration_audit.py",
    *(path.name for path in INPUTS.values()),
)

STATUS = (
    "V48_G2_MAJOR_REGULATOR_AND_WILSON_ADVANCE__EXACT_POSITIVE_HYPERMULTIPLET_"
    "COLLAR_MAP_AND_POLE_SAFE_CHARACTERISTIC__SCOPED_SOURCE_PORTAL_AND_PS_"
    "SCHUR_KERNEL_REPLAYED__FULL_RETAINED_ACTION_DOMAIN_AND_COMPONENT_MATCHING_"
    "INCOMPLETE__G2_FAIL_CLOSED__ONE_OF_EIGHT_FULL_GATES_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if canonical_sha(payload) != payload.get("core_sha256"):
        raise RuntimeError(f"bad input core hash: {path.name}")
    return payload


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def closure_assessment() -> list[dict[str, Any]]:
    return [
        {
            "id": "C1",
            "name": "fixed_order_action_completeness",
            "status": "fail",
            "landed": (
                "The complete renormalizable neutral source superpotential, four leading "
                "source-spinor portals, twelve next two-bulk-trace contractions, the corrected "
                "nineteen PS Yukawa structures, FI data and boundary gauge terms are catalogued."
            ),
            "blocker": (
                "The allowed PS mu_H H H term, pure-source quartics at the same 1/Lambda order, "
                "source-collar Hc/mixed portals and the normal-derivative/EOM-reduced basis are not "
                "all included in one retained-order action."
            ),
        },
        {
            "id": "C2",
            "name": "explicit_regulator",
            "status": "pass",
            "landed": (
                "A finite square H/Hc collar of width epsilon is an explicit regulator and gives "
                "the exact undivided transfer matrices C,D and the map B_epsilon=D^-1 C."
            ),
            "blocker": "none for the fixed-background H/Hc regulator subproblem",
        },
        {
            "id": "C3",
            "name": "variational_domain_and_self_adjointness",
            "status": "partial",
            "landed": (
                "The canonical H/Hc collar with Hermitian Nambu source matrix is J-unitary and "
                "self-adjoint on its parity/continuity domain."
            ),
            "blocker": (
                "The declared wall kinetic, normal-derivative and source-field terms have not been "
                "varied together to derive one complete self-adjoint generalized domain."
            ),
        },
        {
            "id": "C4",
            "name": "positive_full_kinetic_form",
            "status": "partial",
            "landed": "The H/Hc slab induces Z_b=epsilon(I+A^2/3)>0 and the declared wall metrics can be chosen positive.",
            "blocker": (
                "The full source, Zhat, Kähler-mixing and derivative Schur complements are not "
                "assembled.  The proposed source-collar y-stiffness changes Kähler normalization "
                "but does not prove a gapped transverse source spectrum."
            ),
        },
        {
            "id": "C5",
            "name": "counterterm_and_matching_scheme",
            "status": "partial",
            "landed": "The square-collar matching scale, minimal quadratic renormalization conditions and NDA domain are explicit.",
            "blocker": (
                "There is no complete retained-order counterterm catalogue or profile-rematching "
                "calculation for the source, PS kinetic and normal-derivative sectors."
            ),
        },
        {
            "id": "C6",
            "name": "selector_and_naturalness_policy",
            "status": "partial",
            "landed": (
                "V48 correctly rejects an all-order finite selector, treats allowed coefficients "
                "as matching data and declares a sub-cutoff NDA expansion."
            ),
            "blocker": (
                "Because the retained-order basis is incomplete, the claim that every allowed "
                "coefficient at that order is admitted is not yet true."
            ),
        },
        {
            "id": "C7",
            "name": "action_to_full_tower_Wilson_matching",
            "status": "partial",
            "landed": (
                "The undivided matrices K_reg=CR+DQ and N_reg=CP+DT give the exact restricted "
                "tree kernel G_00=(K_reg+N_reg V_0)^-1 N_reg; poles, a residue, locality and "
                "off-shell decoupling replay numerically."
            ),
            "blocker": (
                "The kernel omits the declared wall Kähler/derivative operators and is represented "
                "by an eight-coordinate witness rather than a complete component-Clebsch current map "
                "for the same retained action."
            ),
        },
    ]


def unresolved_defects() -> list[dict[str, str]]:
    return [
        {
            "id": "D1",
            "defect": "missing_PS_Higgs_mass",
            "statement": (
                "After the exact Z4R selector was withdrawn, the local PS invariant "
                "mu_H epsilon_L epsilon_R H H is allowed and must be declared even though the "
                "small-mu mechanism belongs to G4."
            ),
        },
        {
            "id": "D2",
            "defect": "same_order_pure_source_quartics",
            "statement": (
                "Pure-source chiral quartics are O(1/Lambda), the same Wilsonian order as the "
                "retained degree-four portals.  G3 owns their vacuum solution, but G2 must still "
                "parameterize their invariant coefficient space."
            ),
        },
        {
            "id": "D3",
            "defect": "source_collar_wrong_chirality_basis",
            "statement": (
                "A finite collar makes Hc nonzero.  The four conjugate HcHc source portals and "
                "source-dependent HcH/mixed-Kähler terms require inclusion or a proved symmetric-"
                "profile/Dirichlet power-counting reduction."
            ),
        },
        {
            "id": "D4",
            "defect": "PS_normal_derivative_basis",
            "statement": (
                "Gauge-covariant normal-derivative operators, including Q_i nabla5(HLFc) and "
                "Qc_i nabla5(HRAc), are not explicitly reduced by IBP/EOM/field redefinitions or "
                "propagated into the boundary pencil."
            ),
        },
        {
            "id": "D5",
            "defect": "source_profile_spectrum_unproved",
            "statement": (
                "The rho epsilon^2 |D_y X|^2 D-term is a mode-dependent Kähler metric, not by "
                "itself a supersymmetric transverse mass.  A constrained single profile, finite "
                "deconstruction or proper first-order 5D source multiplets are needed."
            ),
        },
        {
            "id": "D6",
            "defect": "same_action_positivity_and_counterterms",
            "statement": (
                "The source, boundary Kähler, Zhat, derivative and counterterm blocks must be "
                "assembled in one positive generalized norm and rematched in the chosen scheme."
            ),
        },
        {
            "id": "D7",
            "defect": "component_resolved_matching",
            "statement": (
                "The exact Schur structure is established, but all physical PS Clebsches, projectors "
                "and currents for the complete retained operator set have not been published."
            ),
        },
    ]


def exact_results(
    wall: Mapping[str, Any], operator: Mapping[str, Any]
) -> list[dict[str, Any]]:
    numerical = operator["numerical_certificate"]
    return [
        {
            "id": "E23",
            "result": "exact finite-collar map",
            "statement": (
                "For delta=m epsilon and X=delta(A-delta I), D=cosh(sqrt X), "
                "C=(A-delta I)sinhc(sqrt X), and B_epsilon=D^-1 C wherever D is invertible."
            ),
            "value": wall["exact_bare_to_boundary_map"],
        },
        {
            "id": "E24",
            "result": "positive induced kinetic term",
            "statement": "B_epsilon=A-m epsilon(I+A^2/3)+... and Z_b=epsilon(I+A^2/3) is strictly positive.",
            "value": {
                "derivative_expansion": wall["exact_bare_to_boundary_map"]["derivative_expansion"],
                "induced_boundary_kinetic": wall["exact_bare_to_boundary_map"]["induced_boundary_kinetic"],
                "strict_kinetic_bound": wall["self_adjointness_positivity_unitarity"]["strict_kinetic_bound"],
            },
        },
        {
            "id": "E25",
            "result": "pole-safe resolved characteristic",
            "statement": (
                "K_reg=(CF-mDS)E+(mCS+DG)O retains every collar state, tends to V47 in the "
                "thin-wall limit and preserves zero nullity at the certificate point."
            ),
            "value": wall["pole_free_spectrum"],
        },
        {
            "id": "E26",
            "result": "scoped operator census",
            "statement": (
                "The renormalizable source action has 16 raw structures including W0, the next "
                "two-bulk-trace portal sector has 12 SO(10) contractions, and the corrected PS "
                "Yukawa census has 19 coefficients before the missing Higgs mass term is added."
            ),
            "value": {
                "renormalizable_raw": operator["renormalizable_source_wall_basis"]["raw_count_including_constant"],
                "leading_two_bulk_portals": operator["leading_degree_four_two_bulk_trace_basis"]["count"],
                "PS_yukawa_coefficients": operator["PS_wall_current_and_response_basis"]["renormalizable_superpotential"]["family_resolved_count"],
            },
        },
        {
            "id": "E27",
            "result": "restricted exact full-tower Schur kernel",
            "statement": (
                "For the encoded tree action, K_reg=CR+DQ, N_reg=CP+DT and "
                "G_00=(K_reg+N_reg V_0)^-1 N_reg.  The witness sees every Theta/Sigma projector."
            ),
            "value": numerical["actual_PS_to_PS_matching"],
        },
        {
            "id": "E28",
            "result": "regulated pole and locality witness",
            "statement": (
                "Three representative positive signed roots, the first-pole residue, exponential "
                "Euclidean locality and off-shell large-source decoupling replay."
            ),
            "value": {
                "spectral": numerical["regulated_spectral_kernel"],
                "locality": numerical["euclidean_locality"],
                "decoupling": numerical["large_boundary_off_shell_decoupling_at_p2"],
            },
        },
        {
            "id": "E29",
            "result": "G2 fail-closed decision",
            "statement": (
                "Only C2 passes completely.  The exact collar and Schur formula are genuine advances, "
                "but the same-action C1--C7 conjunction is false, so G2 is not promoted."
            ),
            "value": "G2 open; one of eight full gates closed",
        },
    ]


def stage_ledger() -> list[dict[str, str]]:
    return [
        {
            "stage": "S0",
            "status": "OPEN_WITH_COUPLED_SOURCE_RANK_RETAINED",
            "passed": "exact coupled neutral-210 branch and 443 generic massive physical source chirals",
            "missing": "spectrally healthy source-field regulator, complete Kähler/FI functional, radion dynamics and branch selection",
        },
        {
            "stage": "S1",
            "status": "CLOSED",
            "passed": "V47 local, quotient, relative and residual-discrete gauge/global anomaly certificate",
            "missing": "none within the declared ordinary-Spin boundary-condition model",
        },
        {
            "stage": "S2",
            "status": "OPEN_WITH_EXACT_HYPERMULTIPLET_COLLAR",
            "passed": "exact B_epsilon, positive induced H/Hc norm, pole-safe K_reg and representative roots/residue",
            "missing": "one complete action-derived generalized domain, healthy source realization, full pole tower and thresholds",
        },
        {
            "stage": "S3",
            "status": "OPEN_WITH_RESTRICTED_SCHUR_KERNEL",
            "passed": "leading source portals, corrected PS H/Hc Yukawas and exact restricted full-tower kernel",
            "missing": "complete retained-order operator basis, component Clebsches, B/L ring, physical Wilson coefficients and rates",
        },
        {
            "stage": "S4",
            "status": "OPEN",
            "passed": "no empirical claim imported from the exact microscopic subchecks",
            "missing": "unification, RG spectrum, flavor, neutrinos, light Higgs, SUSY breaking, dark sector and cosmology",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "closed": True,
            "advance": "V47 exact ordinary-Spin quotient and relative anomaly calculations remain intact.",
            "blocker": "none within the declared ordinary-Spin model",
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": (
                "An explicit H/Hc square collar gives exact B_epsilon and K_reg; the leading source/portal "
                "census, corrected PS traces and a restricted tree full-tower Schur kernel are executable."
            ),
            "blocker": (
                "The source realization is not spectrally certified, the retained-order action omits allowed "
                "mu_H/source-quartic/Hc/normal-derivative terms, and all declared kinetic terms are not matched "
                "in one component-resolved positive kernel."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": "The exact coupled F/D-flat branch and generic physical-rank theorem remain valid at renormalizable order.",
            "blocker": "Pure-source higher operators, FI/Kähler/radion/soft terms, global vacuum selection and the controlled 5D branch are unsolved.",
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "The missing PS mu_H term is now identified as an allowed input rather than silently forbidden.",
            "blocker": "The mu/Bmu mechanism, SUSY breaking, radion stabilization, EWSB and complete scalar vacuum are absent.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": "No excluded dark benchmark is reintroduced.",
            "blocker": "No dark-sector Lagrangian, relic calculation or cosmological history is specified.",
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": "The regulator map is exact and three representative regulated poles plus one residue replay.",
            "blocker": "A complete controlled parameter point, every pole, thresholds, NDA cutoff, unification and RG running are absent.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": "The source-dependent restricted Schur kernel supplies the correct structural starting point for full-tower matching.",
            "blocker": "The 210-completed B/L ring, component Wilson coefficients, dressing/running and proton or multinucleon rates are absent.",
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": "The PS census now includes complementary Hc Higgs cubics and the allowed family/bulk Kähler mixings.",
            "blocker": "There is no complete component Clebsch map, neutrino completion, family fit, uncertainty propagation or withheld prediction.",
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_json(path) for name, path in INPUTS.items()}
    v47 = inputs["v47_master"]
    wall = inputs["resolved_wall"]
    operator = inputs["operator_wilson"]
    criteria = closure_assessment()
    defects = unresolved_defects()
    gates = gate_ledger()
    stages = stage_ledger()
    exact = exact_results(wall, operator)
    manifest = source_manifest()

    closed_gates = [row["gate"] for row in gates if row["closed"]]
    fully_passed = [row["id"] for row in criteria if row["status"] == "pass"]
    checks = {
        "all_input_core_hashes_verify": True,
        "V47_G1_remains_closed": v47["scientific_verdict"]["closed_gates"] == ["G1"],
        "resolved_wall_map_is_exact": wall["decision"]["bare_to_Wilsonian_boundary_map_exact_in_declared_scheme"],
        "resolved_H_collar_positive": wall["decision"]["fundamental_problem_self_adjoint_and_positive"],
        "operator_subaudit_has_no_internal_failures": operator["n_failed_integrity_checks"] == 0,
        "only_C2_fully_passes": fully_passed == ["C2"],
        "same_action_G2_predicate_fails": not all(row["status"] == "pass" for row in criteria),
        "seven_specific_defects_recorded": [row["id"] for row in defects] == [f"D{i}" for i in range(1, 8)],
        "G2_not_promoted": not next(row for row in gates if row["gate"] == "G2")["closed"],
        "only_G1_closed": closed_gates == ["G1"],
        "one_of_eight_full_gates_closed": len(gates) == 8 and len(closed_gates) == 1,
        "S1_only_closed_stage": [row["stage"] for row in stages if row["status"] == "CLOSED"] == ["S1"],
        "complete_theory_not_claimed": not v47["scientific_verdict"]["complete_theory_established"],
        "all_required_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V48 G2 integration integrity failure: " + ", ".join(failures))

    candidate = copy.deepcopy(v47["authoritative_candidate"])
    candidate["name"] = "V48 G1-closed neutral-210 interval with resolved H/Hc collar frontier"
    candidate["resolved_H_hyper_collar"] = {
        "status": "exact fixed-background regulator subproblem closed",
        "map": wall["exact_bare_to_boundary_map"]["map_where_D_invertible"],
        "pole_safe_characteristic": wall["pole_free_spectrum"]["resolved_characteristic"],
        "induced_kinetic": wall["exact_bare_to_boundary_map"]["induced_boundary_kinetic"],
    }
    candidate["source_host_operator_frontier"] = {
        "renormalizable_source_rows": operator["renormalizable_source_wall_basis"]["raw_count_including_constant"],
        "leading_two_bulk_portal_rows": operator["leading_degree_four_two_bulk_trace_basis"]["count"],
        "PS_yukawa_coefficients": operator["PS_wall_current_and_response_basis"]["renormalizable_superpotential"]["family_resolved_count"],
        "restricted_kernel": operator["exact_cross_wall_wilson_matching"]["actual_host_kernel"],
        "status": "major partial result; not the kernel of a complete retained-order action",
    }

    report: dict[str, Any] = {
        "schema": "susy-v48-g2-frontier-integration-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "real_new_physics_obtained": True,
            "G2_closed": False,
            "complete_theory_established": False,
            "empirically_validated": False,
            "full_gates_closed": 1,
            "full_gates_total": 8,
            "closed_gates": closed_gates,
            "summary": (
                "V48 solves the fixed-background H/Hc regulator subproblem and derives an exact restricted "
                "full-tower source-dependent Schur kernel.  It does not close G2 because the retained action, "
                "positive generalized domain and component Wilson kernel are not yet the same complete object. "
                "G1 remains the only closed full gate."
            ),
            "tests_mean": "deterministic checks of the encoded formulas and artifacts, not empirical validation or a UV-completion proof",
        },
        "frozen_G2_contract": {
            "definition": (
                "A fixed-order tree-level Wilsonian source/portal boundary EFT in one declared regulator scheme, "
                "with a complete retained-order local action, an action-derived positive self-adjoint domain, and "
                "a component-resolved full-tower kernel for that same action."
            ),
            "not_required_for_G2": {
                "G3": "solve the vacuum and FI/Kähler/radion/soft branch",
                "G6": "compute the complete pole tower, thresholds, unification and RG flow",
                "G7": "finish the B/L ring, running and decay likelihoods",
                "G8": "perform the flavor/neutrino fit and withheld prediction",
                "UV": "predict the infinite irrelevant tower from a fundamental UV completion",
            },
            "closure_logic": "G2_closed iff C1 through C7 all pass for the same retained action",
        },
        "G2_closure_assessment": criteria,
        "number_of_clauses": len(criteria),
        "fully_passed_clauses": fully_passed,
        "unresolved_defects": defects,
        "authoritative_candidate": candidate,
        "V48_exact_results": exact,
        "stage_ledger": stages,
        "gate_ledger": gates,
        "smallest_next_closure_patch": [
            "Replace the dynamical source collar by a constrained single 4D profile, finite deconstruction, or proper first-order 5D source multiplets and prove that no extra light source tower appears.",
            "Freeze the full retained-order source/PS action, adding mu_H H H, an abstract complete invariant basis for pure-source quartics, the Hc/mixed terms and an explicit normal-derivative IBP/EOM reduction.",
            "Insert every retained Kähler, derivative and counterterm block into generalized K_reg,N_reg; prove self-adjointness and positivity of the complete norm.",
            "Publish the component Clebsch/projector current map and verify that its poles, residues and low-energy coefficients reproduce the complete retained action.",
        ],
        "route_decision": {
            "continue": "the G1-consistent neutral-210 route remains viable",
            "G1_status": "closed",
            "G2_status": "open after major V48 advance",
            "G3_to_G8_status": "open",
            "do_not_claim": "two gates closed, a complete theory, UV completeness, or empirical validation",
        },
        "primary_sources": [
            {"topic": "5D N=1 hypermultiplets in 4D superspace", "url": "https://arxiv.org/abs/hep-th/0106256"},
            {"topic": "gauge-covariant brane and normal-derivative operators", "url": "https://arxiv.org/abs/hep-ph/0112230"},
            {"topic": "interval action principle and boundary conditions", "url": "https://arxiv.org/abs/hep-th/0411133"},
            {"topic": "thin-defect EFT renormalization", "url": "https://arxiv.org/abs/hep-ph/0601222"},
            {"topic": "SO(10) spinor cubic/quartic channels", "url": "https://arxiv.org/abs/hep-th/0109116"},
            {"topic": "finite-width brane and KK order-of-limits", "url": "https://arxiv.org/abs/1408.1852"},
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "input_core_hashes": {name: payload["core_sha256"] for name, payload in inputs.items()},
        "source_manifest": manifest,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    verdict = report["scientific_verdict"]
    criteria_rows = "\n".join(
        f"| {row['id']} | {row['name']} | {row['status']} | {row['landed']} | {row['blocker']} |"
        for row in report["G2_closure_assessment"]
    )
    defect_rows = "\n".join(
        f"| {row['id']} | {row['defect']} | {row['statement']} |"
        for row in report["unresolved_defects"]
    )
    exact_rows = "\n".join(
        f"| {row['id']} | {row['result']} | {row['statement']} |"
        for row in report["V48_exact_results"]
    )
    stage_rows = "\n".join(
        f"| {row['stage']} | {row['status']} | {row['passed']} | {row['missing']} |"
        for row in report["stage_ledger"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {'closed' if row['closed'] else 'open'} | {row['advance']} | {row['blocker']} |"
        for row in report["gate_ledger"]
    )
    next_steps = "\n".join(
        f"{index}. {item}" for index, item in enumerate(report["smallest_next_closure_patch"], 1)
    )
    return f"""# V48 G2 frontier integration audit

Status: `{report['status']}`

## Scientific verdict

{verdict['summary']}

**Full gates closed: {verdict['full_gates_closed']} / {verdict['full_gates_total']} — G1 only.  G2 remains open.**

This is a real regulator and matching advance, not a complete theory, UV
completion or empirical validation.

## What V48 genuinely solved

For a Hermitian Nambu source matrix `A`, a finite square collar gives

`delta=m epsilon`, `X=delta(A-delta I)`,

`D=cosh(sqrt X)`, `C=(A-delta I) sinhc(sqrt X)`,

and, where `D` is invertible,

`B_epsilon(m)=D^-1 C`.

The exact derivative expansion begins

`B_epsilon=A-m epsilon(I+A^2/3)+...`,

so the induced H/Hc boundary kinetic matrix
`Z_b=epsilon(I+A^2/3)` is strictly positive.  The undivided characteristic

`K_reg=(CF-mDS)E+(mCS+DG)O`

retains collar poles and tends to the V47 characteristic in the thin-wall
limit.

For both host boundary data, the corrected tree response is

`K_reg=CR+DQ`, `N_reg=CP+DT`,

`G_00=(K_reg+N_reg V_0)^-1 N_reg`.

This is the right Schur structure.  The executable representative contains all
four H/Hc Higgs bilinears, sees all four Theta/Sigma projectors, replays three
regulated poles and one residue, and has exponential Euclidean locality.

## Frozen G2 contract

{report['frozen_G2_contract']['definition']}

`{report['frozen_G2_contract']['closure_logic']}`.

It does not demand an all-order UV prediction, and it does not absorb the
vacuum, numerical-threshold, B/L-rate or flavor-fit work owned by G3, G6, G7
and G8.

## C1--C7 decision

| Clause | Requirement | Status | Landed | Remaining blocker |
|---|---|---|---|---|
{criteria_rows}

Only `{', '.join(report['fully_passed_clauses'])}` passes completely.  The
conjunction is therefore false and G2 cannot be promoted.

## Exact defects preventing closure

| ID | Defect | Why it matters |
|---|---|---|
{defect_rows}

The source-collar problem is especially important.  A positive
`d4theta epsilon^2 |D_y X|^2` term is a Kähler normalization, not a proof that
nonconstant source profiles are gapped.  The source must instead be a
constrained single profile, a finite deconstruction, or a proper first-order
5D multiplet before its spectrum and norm can support G2.

## V48 exact results

| ID | Result | Exact statement |
|---|---|---|
{exact_rows}

## Research stages

| Stage | Status | Passed | Missing |
|---|---|---|---|
{stage_rows}

## G1--G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
{gate_rows}

## Smallest next G2 closure patch

{next_steps}

The neutral-210 route remains viable.  It should be continued, but the result
must stay at **1/8 closed gates** until the repaired source regulator and the
same-action component kernel pass together.

## Primary sources

- [Marti--Pomarol: 5D supersymmetry in N=1 superfields](https://arxiv.org/abs/hep-th/0106256)
- [Hebecker: gauge-covariant brane operators](https://arxiv.org/abs/hep-ph/0112230)
- [von Gersdorff et al.: interval boundary action principle](https://arxiv.org/abs/hep-th/0411133)
- [del Aguila--Perez-Victoria--Santiago: thin-defect EFT](https://arxiv.org/abs/hep-ph/0601222)
- [Nath--Syed: SO(10) spinor contraction channels](https://arxiv.org/abs/hep-th/0109116)
- [Barcelo--Mitra--Moreau: finite-width brane/KK limit ordering](https://arxiv.org/abs/1408.1852)

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V48 G2 integration JSON is missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V48 G2 integration Markdown is missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V48_G2_FRONTIER_INTEGRATION_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
