#!/usr/bin/env python3
"""Integrate the V47 anomaly, source and four-spinor KK certificates.

V47 is the first version in this line to close a full gate: G1, microscopic
gauge/global-anomaly consistency.  The source-vacuum and KK results are real
advances but remain subproblem closures, so G2--G8 stay open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V47_G1_CLOSURE_FRONTIER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V47_G1_CLOSURE_FRONTIER_AUDIT.md"

INPUTS = {
    "v46_master": ROOT / "SUSY_V46_MICROSCOPIC_KILL_TEST_AUDIT.json",
    "relative_eta_bordism": ROOT / "SUSY_V47_RELATIVE_ETA_BORDISM_AUDIT.json",
    "source_completion": ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
    "four_spinor_KK": ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.json",
}

SOURCE_FILES = (
    Path(__file__).name,
    "test_susy_v47_g1_closure_frontier_audit.py",
    *(path.name for path in INPUTS.values()),
)

STATUS = (
    "V47_G1_MICROSCOPIC_GAUGE_AND_GLOBAL_ANOMALY_CONSISTENCY_CLOSED__"
    "COUPLED_NEUTRAL_210_SOURCE_BRANCH_FULL_PHYSICAL_RANK__FOUR_SPINOR_"
    "MIXED_KK_ZERO_MODE_THEOREM_PROVED__REGULATOR_VACUUM_THRESHOLDS_AND_"
    "PHENOMENOLOGY_OPEN__ONE_OF_EIGHT_FULL_GATES_CLOSED"
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


def updated_candidate(
    v46: Mapping[str, Any],
    global_eta: Mapping[str, Any],
    source: Mapping[str, Any],
    kk: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = copy.deepcopy(v46["authoritative_candidate"])
    candidate["name"] = "V47 anomaly-closed coupled-source four-spinor interval"
    wall = candidate["Spin10_source_wall_yL"]
    wall["coupled_neutral_source_form"] = source["coupled_210_source"][
        "most_general_relevant_form_after_shifting_STheta"
    ]
    wall["exact_coupled_branch"] = source["coupled_210_source"]["exact_branch"]
    wall["coupled_physical_counting"] = source["coupled_210_source"]["counting"]
    wall["operator_policy"] = (
        "Include the gauge-allowed neutral STheta cross couplings and both Sigma-spinor "
        "operators; do not sequester them by assertion."
    )
    candidate["exact_global_structure"] = {
        "PS_group": global_eta["group_and_bundle_geometry"]["P"],
        "spacetime_structure": global_eta["group_and_bundle_geometry"]["spacetime_structure"],
        "Omega5_PSxU1F": global_eta["AHSS_BPxU1F"]["Omega5Spin"],
        "Omega6_interval_relative": global_eta["standard_interval_relative_pair"][
            "Omega6Spin_relative"
        ],
        "G1_closed": True,
    }
    candidate["four_spinor_boundary_extension"] = {
        "basis": kk["renormalized_source_boundary_matrix"]["basis"],
        "matrix": kk["renormalized_source_boundary_matrix"]["B_component"],
        "characteristic": kk["general_transfer_theorem"]["characteristic_matrix"],
        "zero_criterion": kk["exact_zero_mode_theorem"]["criterion"],
        "exact_zero_modes_for_finite_nonzero_Theta_blocks": kk[
            "V46_Theta_Sigma_zero_count"
        ]["both_Theta_nonzero"]["total_chiral_component_zero_modes"],
        "scope": "finite Hermitian renormalized B; bare-brane matching and induced operators remain open",
    }
    candidate["alternative_source_route"] = {
        "name": "45+54+126+bar126",
        "exact_SU5_branch": source["alternative_45_plus_54"]["SU5_branch"],
        "status": source["decision"]["45_plus_54_status"],
    }
    return candidate


def exact_results(
    global_eta: Mapping[str, Any],
    source: Mapping[str, Any],
    kk: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "id": "E15",
            "result": "ordinary-Spin quotient bordism",
            "statement": "Every total-degree-five AHSS term dies for BP and B(PxU1F), including non-liftable bundles.",
            "value": {
                "Omega5_BP": global_eta["AHSS_BP"]["Omega5Spin"],
                "Omega5_BPxU1F": global_eta["AHSS_BPxU1F"]["Omega5Spin"],
            },
        },
        {
            "id": "E16",
            "result": "relative interval anomaly",
            "statement": "The degree-six map is integrally surjective and the standard interval relative group is zero.",
            "value": global_eta["standard_interval_relative_pair"],
        },
        {
            "id": "E17",
            "result": "G1 promoted",
            "statement": "Local polynomials, quantized parity levels, quotient torsion, the relative obstruction and the residual Z6 pullback all cancel.",
            "value": global_eta["decision"]["G1_closure_reason"],
        },
        {
            "id": "E18",
            "result": "coupled neutral source branch",
            "statement": "The unavoidable neutral cross couplings preserve an exact F/D-flat branch with 443 generic massive physical chirals and no physical zero.",
            "value": source["coupled_210_source"]["counting"],
        },
        {
            "id": "E19",
            "result": "source Hessian cofactor theorem",
            "statement": "On the gauge quotient, det(Mphys)=-a^2 det(H), independent of the cross vector and singlet diagonal entry.",
            "value": source["coupled_210_source"]["physical_hessian_lemma"]["certificate"],
        },
        {
            "id": "E20",
            "result": "four-spinor mixed KK theorem",
            "statement": "The zero-mode kernel is exactly ker(B_EE); both finite nonzero Theta blocks remove all exact zero modes for arbitrary finite Sigma mixing.",
            "value": {
                "characteristic": kk["general_transfer_theorem"]["characteristic_matrix"],
                "factorization": kk["exact_zero_mode_theorem"]["block_factorization"],
                "zero_count": kk["V46_Theta_Sigma_zero_count"]["both_Theta_nonzero"],
            },
        },
        {
            "id": "E21",
            "result": "finite strong-mixing warning",
            "statement": "Large finite Sigma mixing need not create a zero but can create a parametrically light pole, so thresholds require the full characteristic.",
            "value": kk["numerical_certificate"]["flat_singlet_lightest_absolute_signed_mass"],
        },
        {
            "id": "E22",
            "result": "source-route comparison",
            "statement": "45+54 has a lower source index and an exact SU5 branch, but 210 remains selected because only it has a replayed full physical Hessian.",
            "value": source["decision"],
        },
    ]


def stage_ledger() -> list[dict[str, Any]]:
    return [
        {
            "stage": "S0",
            "status": "OPEN_WITH_COUPLED_SOURCE_BRANCH_AND_RANK_CERTIFIED",
            "passed": "all relevant neutral renormalizable source terms included; exact coupled branch; 443 massive physical chirals",
            "missing": "resolved boundary regulator, complete Kahler action, radion stabilization and dynamical branch selection",
        },
        {
            "stage": "S1",
            "status": "CLOSED",
            "passed": "local polynomials, free parity lattice, exact quotient Omega5, relative Omega6 and residual Z6 pullback",
            "missing": "none for gauge/global-anomaly consistency in the declared ordinary-Spin boundary-condition model",
        },
        {
            "stage": "S2",
            "status": "OPEN_WITH_FOUR_SPINOR_ZERO_THEOREM_CERTIFIED",
            "passed": "exact C(m), D(z), ker(B_EE) theorem and no-zero/no-SUSY-tachyon result for finite Hermitian B",
            "missing": "bare-to-renormalized brane map, induced kinetic/derivative terms, numerical roots and thresholds",
        },
        {
            "stage": "S3",
            "status": "OPEN_WITH_OPERATOR_FRONTIER_RETAINED",
            "passed": "faithful Z3F and matter parity survive; prior degree-20 orientation frontier retained",
            "missing": "210-completed operator ring, full-tower Wilson matching and decay-rate limits",
        },
        {
            "stage": "S4",
            "status": "OPEN",
            "passed": "no phenomenological claim imported from a microscopic subcheck",
            "missing": "unification, RG spectrum, flavor, neutrinos, light Higgs, SUSY breaking, dark sector and cosmology",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "closed": True,
            "advance": "Exact ordinary-Spin AHSS and relative-pair calculations remove the non-liftable, mixed-U1F and residual-Z6 anomaly obstructions.",
            "blocker": "none within the declared model; gauging the orbifold reflection would define a different equivariant/Pin problem",
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": "All relevant renormalizable neutral cross terms and both Sigma-spinor portals are now included algebraically and in the idealized boundary matrix.",
            "blocker": "The resolved-brane map, induced boundary operators, higher-dimensional selector/naturalness structure and Wilson matching are absent.",
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": "An exact coupled F/D-flat neutral-210 branch has 443 generic massive physical chirals and an executable full-rank Hessian theorem.",
            "blocker": "The Kahler/radion/soft potential, global vacuum selection and controlled 5D branch are not solved.",
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": "No inconsistent soft sector was imported.",
            "blocker": "Radion stabilization, SUSY breaking, mu/Bmu, EWSB and the complete scalar vacuum are absent.",
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": "The excluded V39 dark benchmark remains removed.",
            "blocker": "No dark-sector Lagrangian, relic calculation or cosmological history is specified.",
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": "The exact four-spinor characteristic, zero-mode theorem and Hermitian no-tachyon result include both Theta and Sigma mixings.",
            "blocker": "Regulator matching, boundary kinetics, numerical thresholds, 5D unification, RG running and the pole spectrum are missing.",
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": "The anomaly-free faithful Z3F and matter parity coexist with the retained high-degree orientation frontier.",
            "blocker": "The 210-completed operator ring, shifted-tower Wilson coefficients and proton/multinucleon rates are absent.",
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": "The PS-wall Yukawa architecture remains compatible with the retained route.",
            "blocker": "There is no neutrino completion, three-family fit, uncertainty propagation or withheld prediction.",
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_json(path) for name, path in INPUTS.items()}
    v46 = inputs["v46_master"]
    global_eta = inputs["relative_eta_bordism"]
    source = inputs["source_completion"]
    kk = inputs["four_spinor_KK"]
    candidate = updated_candidate(v46, global_eta, source, kk)
    stages = stage_ledger()
    gates = gate_ledger()
    exact = exact_results(global_eta, source, kk)
    manifest = source_manifest()

    closed_gates = [row["gate"] for row in gates if row["closed"]]
    checks = {
        "all_input_core_hashes_verify": True,
        "V46_had_zero_closed_gates": v46["scientific_verdict"]["full_gates_closed"] == 0,
        "ordinary_PS_Omega5_zero": global_eta["AHSS_BP"]["Omega5Spin"] == "0",
        "PSxU1F_Omega5_zero": global_eta["AHSS_BPxU1F"]["Omega5Spin"] == "0",
        "relative_interval_Omega6_zero": global_eta["standard_interval_relative_pair"]["Omega6Spin_relative"] == "0",
        "relative_map_integrally_surjective": global_eta["standard_interval_relative_pair"]["surjectivity_witness"]["map_Omega6_is_surjective"],
        "G1_subaudit_closed": global_eta["decision"]["G1_closed"],
        "absolute_APS_not_overclaimed": not global_eta["APS_eta_conclusion"]["absolute_exponentiated_eta_value_computed"],
        "coupled_source_has_443_massive_physical": source["coupled_210_source"]["counting"]["generic_massive_uneaten_chiral_components"] == 443,
        "coupled_source_has_no_physical_zero": source["coupled_210_source"]["counting"]["generic_physical_massless_chiral_components"] == 0,
        "source_hessian_exact_witnesses_pass": source["coupled_210_source"]["physical_hessian_lemma"]["certificate"]["all_witnesses_pass"],
        "45_54_not_overpromoted": not source["alternative_45_plus_54"]["rank_status"]["independent_full_physical_hessian_replayed_here"],
        "four_spinor_zero_count_is_zero": kk["V46_Theta_Sigma_zero_count"]["both_Theta_nonzero"]["total_chiral_component_zero_modes"] == 0,
        "KK_self_adjoint_stability_certified": kk["self_adjointness_and_stability"]["tachyonic_or_complex_roots"] == 0,
        "KK_regulator_not_overclaimed": not kk["decision"]["S2_closed"],
        "only_G1_closed": closed_gates == ["G1"],
        "one_of_eight_full_gates_closed": len(gates) == 8 and len(closed_gates) == 1,
        "S1_is_only_closed_stage": [row["stage"] for row in stages if row["status"] == "CLOSED"] == ["S1"],
        "all_required_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V47 master integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v47-g1-closure-frontier-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "real_new_physics_obtained": True,
            "complete_theory_established": False,
            "empirically_validated": False,
            "full_gates_closed": 1,
            "full_gates_total": 8,
            "closed_gates": closed_gates,
            "summary": (
                "V47 closes G1: the exact ordinary-Spin Pati-Salam quotient AHSS has no "
                "degree-five torsion, the Spin10/P relative degree-six group vanishes, and "
                "the already-certified local/free and residual-Z6 anomaly data are compatible. "
                "It also proves a coupled full-rank source branch and the exact four-spinor "
                "mixed KK zero theorem.  The brane regulator, stabilized vacuum, thresholds "
                "and physical reconstruction remain open, so the theory is not complete."
            ),
            "tests_mean": "deterministic verification of the encoded mathematics, not empirical validation or a UV-completion proof",
        },
        "authoritative_candidate": candidate,
        "route_decision": {
            "continue": "neutral-210-repaired full-Spin10 source wall with all relevant renormalizable cross couplings included",
            "G1_status": "closed",
            "G2_to_G8_status": "open",
            "45_plus_54": "priority lower-index alternative pending complete physical-Hessian replay",
        },
        "V46_exact_results_retained": v46["V46_exact_results"],
        "V47_exact_results": exact,
        "stage_ledger": stages,
        "gate_ledger": gates,
        "remaining_terminal_calculations": [
            "Resolve the source wall and derive the matrix-valued bare-to-renormalized B_R map, including induced kinetic, derivative and wrong-chirality operators.",
            "Choose a controlled 5D parameter point and compute every root of the complete four-spinor/gauge/source characteristic, thresholds, NDA cutoff and unification fit.",
            "Specify the Kahler, radion and SUSY-breaking sectors and prove global vacuum selection, EWSB and absence of dangerous scalar directions.",
            "Recompute the 210-completed invariant/operator ring, full-tower Wilson coefficients and proton or multinucleon decay likelihoods.",
            "Build and fit the light-Higgs, flavor, neutrino, dark-sector and cosmological completion with uncertainty propagation and withheld predictions.",
        ],
        "research_stopping_rule": (
            "Continue this one G1-consistent neutral-210 route.  Kill it if every resolved-brane "
            "realization has a zero, negative-norm mode or uncontrolled cutoff; if no stabilized "
            "vacuum and light Higgs exist; or if decay, flavor, neutrino, collider and cosmological "
            "data exclude the full controlled parameter region."
        ),
        "primary_sources": [
            {"topic": "Pati-Salam quotient cohomology and bordism", "url": "https://arxiv.org/abs/1910.14668"},
            {"topic": "ordinary Spin AHSS and Pati-Salam global anomalies", "url": "https://arxiv.org/abs/1910.11277"},
            {"topic": "eta-invariant anomaly inflow", "url": "https://arxiv.org/abs/1909.08775"},
            {"topic": "minimal renormalizable 210+126+bar126 source", "url": "https://arxiv.org/abs/hep-ph/0306242"},
            {"topic": "general 45,54,126,210 couplings and mass matrices", "url": "https://arxiv.org/abs/1707.00580"},
            {"topic": "5D supersymmetric hypermultiplet equations", "url": "https://arxiv.org/abs/hep-th/0106256"},
            {"topic": "thin-brane regulator and order-of-limits warning", "url": "https://arxiv.org/abs/1408.1852"},
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
    exact_rows = "\n".join(
        f"| {row['id']} | {row['result']} | {row['statement']} |"
        for row in report["V47_exact_results"]
    )
    stage_rows = "\n".join(
        f"| {row['stage']} | {row['status']} | {row['passed']} | {row['missing']} |"
        for row in report["stage_ledger"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {'closed' if row['closed'] else 'open'} | {row['advance']} | {row['blocker']} |"
        for row in report["gate_ledger"]
    )
    remaining = "\n".join(
        f"{index}. {item}" for index, item in enumerate(report["remaining_terminal_calculations"], 1)
    )
    return f"""# V47 G1 closure and exact frontier

Status: {report['status']}

## Scientific verdict

{verdict['summary']}

**Full gates closed: {verdict['full_gates_closed']} / {verdict['full_gates_total']} — G1 only.**

This is a mathematical consistency advance, not empirical validation and not a
complete theory.

## Why G1 closes

For `P=(SU4 x SU2L x SU2R)/Z2_diag` with an independent spacetime Spin
structure, the exact low-degree AHSS gives

`Omega5^Spin(BP)=Omega5^Spin(B(P x U1F))=0`.

The non-liftable candidate `x Sq1(x)` and the mixed `x c1(U1F)` direction are
killed by explicit `d2` differentials.  The free degree-six map from the
Pati--Salam endpoint to `Spin(10) x U1F` hits all three bulk generators
primitively, so the standard interval relative group is also zero.  Together
with the exact wall-local anomaly cancellation, quantized parity levels and
residual-Z6 pullback, the gauge/global-anomaly obstruction vanishes.

The absolute APS determinant phase is not assigned a number.  It depends on a
regulator and local counterterm convention, but its gauge-invariant value is
not an anomaly and does not reopen G1.

## Coupled source branch

After shifting the neutral singlet coordinate, all relevant neutral
renormalizable cross couplings can be retained.  At `STheta=0`, the V46 SU5
branch remains exact and `F_STheta` fixes `ThetaPlus ThetaMinus`.  On the gauge
quotient the physical Hessian has block form

`[[H,0,c],[0,0,a],[cT,a,d]]`,

with determinant `-a^2 det(H)`.  The coupled sector has 465 chiral components,
22 eaten directions and 443 generic massive physical components, with no
physical zero.  This closes the source-superpotential existence subproblem,
not full G3: Kahler/radion stabilization and branch selection remain absent.

## Four-spinor mixed KK theorem

The exact characteristic is

`K(m)=(-mS+BF)E+(G+mBS)(1-E)`, `C(m)=det K(m)`,

and `D(z)=C(sqrt(z))C(-sqrt(z))`.  At zero mass,

`det K(0)=det G_O det(B_EE) det F_E`.

Therefore `n_zero=n_even-rank(B_EE)`.  Both finite nonzero Theta blocks make
`B_EE` full rank in all 16 component directions; the allowed Sigma entries are
even--odd on the SU5 singlet and cannot restore a zero.  A Hermitian extension
has real signed eigenvalues and no supersymmetric tachyon.  Large finite Sigma
mixing can nevertheless produce a parametrically light pole, so the regulator
and complete threshold spectrum remain part of G6.

## V47 exact results

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

## Next terminal calculations

{remaining}

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
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V47 master JSON is missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V47 master Markdown is missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V47_G1_CLOSURE_FRONTIER_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
