#!/usr/bin/env python3
"""Integrate the three V46 microscopic kill tests into one fail-closed verdict.

V46 does not declare a complete theory.  It eliminates two tempting source-wall
routes, selects the standard neutral-210 repair, solves an idealized full KK
boundary problem, and performs all currently available anomaly screens.  The
actual quotient-relative eta invariant and the enlarged coupled KK operator
remain mandatory before any G gate can close.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V46_MICROSCOPIC_KILL_TEST_AUDIT.json"
MD_PATH = ROOT / "SUSY_V46_MICROSCOPIC_KILL_TEST_AUDIT.md"

INPUTS = {
    "v45_master": ROOT / "SUSY_V45_NEW_PHYSICS_MASTER_AUDIT.json",
    "source_higgs": ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
    "spinor_kk": ROOT / "SUSY_V46_SPINOR_KK_DETERMINANT_AUDIT.json",
    "global_eta": ROOT / "SUSY_V46_GLOBAL_PARITY_ETA_AUDIT.json",
}

SOURCE_FILES = (
    "susy_v46_microscopic_kill_test_audit.py",
    "test_susy_v46_microscopic_kill_test_audit.py",
    "susy_v46_source_higgs_rank_audit.py",
    "test_susy_v46_source_higgs_rank_audit.py",
    "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.md",
    "susy_v46_spinor_kk_determinant_audit.py",
    "test_susy_v46_spinor_kk_determinant_audit.py",
    "SUSY_V46_SPINOR_KK_DETERMINANT_AUDIT.md",
    "susy_v46_global_parity_eta_audit.py",
    "test_susy_v46_global_parity_eta_audit.py",
    "SUSY_V46_GLOBAL_PARITY_ETA_AUDIT.md",
    *tuple(path.name for path in INPUTS.values()),
)

STATUS = (
    "V46_MICROSCOPIC_KILL_TESTS_RESOLVED__126_PAIR_PLUS_SINGLETS_KILLED__"
    "NEUTRAL_210_REPAIR_SELECTED__IDEALIZED_FULL_KK_ZERO_MODE_THEOREM_PROVED__"
    "NO_SCREENED_GLOBAL_ANOMALY_OBSTRUCTION__RELATIVE_ETA_AND_COUPLED_KK_OPEN__"
    "ZERO_FULL_GATES_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"required V46 input missing: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"required V46 input is not an object: {path.name}")
    if canonical_sha(payload) != payload.get("core_sha256"):
        raise RuntimeError(f"required V46 input has an invalid core hash: {path.name}")
    return payload


def source_manifest() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in SOURCE_FILES:
        path = ROOT / name
        rows.append(
            {
                "path": name,
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
        )
    return rows


def updated_candidate(v45: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(v45["authoritative_candidate"])
    candidate["name"] = "V46 neutral-210-repaired four-bulk-spinor interval"
    wall = candidate["Spin10_source_wall_yL"]
    wall["boundary_chirals"] = [
        "STheta_0",
        "ThetaPlus_+3",
        "ThetaMinus_-3",
        "Phi_210,0",
        "Sigma_126,0",
        "barSigma_bar126,0",
    ]
    wall.pop("missing_term", None)
    wall["selected_superpotential"] = source["recommended_source_superpotential"]
    wall["GUT_tensor_superpotential"] = source["neutral_210_repair"]["tensor_superpotential"]
    wall["SU5_branch"] = source["neutral_210_repair"]["F_D_branch"]
    wall["rank_scope"] = (
        "The isolated source-Higgs sector has full physical rank on a generic SU(5) branch. "
        "Gauge-allowed Theta/GUT cross couplings, Sigma-spinor terms, boundary kinetics and "
        "the relative eta problem are not removed by this statement."
    )
    candidate["route_decision"] = {
        "retained": "full Spin(10) source wall with neutral 210+126+bar126",
        "rejected": [
            "126+bar126 plus gauge singlets only",
            "five-dimensional PS/GG orbifold wall with charge-ten singlet breaking",
        ],
    }
    candidate["mandatory_allowed_operator_extension"] = [
        "barSigma HLF HRA",
        "Sigma HLA HRF",
        "generic neutral source cross couplings such as STheta Phi^2 and STheta Sigma.barSigma",
    ]
    return candidate


def exact_v46_results(
    source: Mapping[str, Any],
    kk: Mapping[str, Any],
    global_eta: Mapping[str, Any],
) -> list[dict[str, Any]]:
    no_go = source["singlet_only_126_pair"]
    repair = source["neutral_210_repair"]
    gg = source["PS_GG_orbifold_shortcut"]
    zero = kk["zero_mode_and_tachyon_theorems"]
    half = global_eta["five_dimensional_parity_half_levels"]
    residual = global_eta["residual_Z3F_and_matter_parity"]
    return [
        {
            "id": "E8",
            "result": "singlet-only source no-go",
            "statement": "A neutral 126+bar126 pair with any renormalizable singlet sector leaves at least 230 physical massless transverse chirals.",
            "value": no_go["dimensions"]["physical_massless_transverse_chirals_at_least"],
        },
        {
            "id": "E9",
            "result": "neutral-210 repair",
            "statement": "The explicit SU(5) branch has 21 Goldstones and a generic full-rank 441-component uneaten spectrum.",
            "value": repair["counting"],
        },
        {
            "id": "E10",
            "result": "5D PS/GG shortcut rejected",
            "statement": "Opposite adjoint-chiral parities create 12 massless Phi modes; the four-spinor wall scan also has zero anomaly-free intrinsic-sign assignments.",
            "value": {
                "adjoint_chiral_zero_modes": gg["five_dimensional_vector_obstruction"]["Phi_plus_plus_zero_modes_from_V_minus_minus"],
                "anomaly_free_sign_assignments": gg["source_wall_ordinary_anomaly_scan"]["number_locally_anomaly_free"],
            },
        },
        {
            "id": "E11",
            "result": "exact idealized KK characteristics",
            "statement": "For finite nonzero self-adjoint boundary parameter b, both selected zero modes are lifted and no unselected zero or supersymmetric tachyon occurs.",
            "value": {
                "selected": kk["exact_characteristics"]["selected_plus_plus"]["D"],
                "unselected": kk["exact_characteristics"]["unselected_minus_plus"]["D"],
                "finite_nonzero_b": zero["finite_nonzero_b"],
                "tachyon_result": zero["tachyon_result"],
            },
        },
        {
            "id": "E12",
            "result": "strong-boundary spectral flow",
            "statement": "The b to infinity endpoint is nonuniform: an unselected mode becomes parametrically light and is exactly massless only at the distinct infinite extension.",
            "value": kk["projected_4D_vs_full_KK"]["strong_boundary_spectral_flow"],
        },
        {
            "id": "E13",
            "result": "5D parity half-level screen",
            "statement": "Every displayed shift lies in the closed-spin U(1) free lattice and the common-orientation total vanishes.",
            "value": {
                "all_integral": half["every_individual_displayed_shift_has_zero_fractional_part"],
                "closed_spin_lattice": half["every_individual_shift_lies_in_closed_spin_U1_free_lattice"],
                "totals": half["common_sigma_totals"],
            },
        },
        {
            "id": "E14",
            "result": "finite and traditional global screens",
            "statement": "Spin(10) homotopy, PS Witten, source Spin(10), residual Z3, matter parity and combined Z6 screens pass; the actual quotient-relative eta class is not certified.",
            "value": {
                "pure_finite_result": residual["pure_finite_Dai_Freed_result"],
                "actual_interval_certified": residual["combined_with_actual_PS_quotient_and_interval_certified"],
            },
        },
    ]


def stage_ledger() -> list[dict[str, Any]]:
    return [
        {
            "stage": "S0",
            "status": "OPEN_WITH_SOURCE_HIGGS_RANK_REPAIR_CERTIFIED",
            "passed": "compact V45 skeleton plus a neutral-210 SU5 branch with only 21 Goldstones and 441 massive uneaten chirals",
            "missing": "one complete all-allowed boundary action, its selector/naturalness rationale, and the compact quotient-relative definition",
        },
        {
            "stage": "S1",
            "status": "OPEN_WITH_LOCAL_AND_FAST_GLOBAL_SCREENS_CERTIFIED",
            "passed": "ordinary wall polynomials, closed-spin half-level lattice, homotopy, Witten and pure residual Z3/Z2/Z6 tests",
            "missing": "relative or stratified bordism plus regulated APS eta on the actual two-wall quotient",
        },
        {
            "stage": "S2",
            "status": "OPEN_WITH_IDEALIZED_FULL_TOWER_THEOREM_CERTIFIED",
            "passed": "entire D++ and D-+ characteristics; no zero or tachyon for finite nonzero b in the declared two-hyper problem",
            "missing": "resolved-brane map B_R(mu), Sigma-spinor mixing, all boundary kinetic terms and the complete coupled transfer matrix",
        },
        {
            "stage": "S3",
            "status": "OPEN_WITH_V45_OPERATOR_FRONTIER_RETAINED",
            "passed": "degree-20 local orientation frontier, pure-light charge-flow lower bound and universal discrete-R no-go",
            "missing": "complete operator ring in the 210 repair, shifted-tower Wilson matching and physical decay limits",
        },
        {
            "stage": "S4",
            "status": "OPEN",
            "passed": "no phenomenological sector promoted by a microscopic consistency subcheck",
            "missing": "thresholds, unification, flavour, neutrinos, light Higgs, SUSY breaking, dark sector and cosmology",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {"gate": "G1", "closed": False, "advance": "No fractional parity-level, homotopy, Witten or pure Z3/Z2/Z6 obstruction was found.", "blocker": "The actual PS/Z2 diagonal quotient and two-wall relative eta/bordism class remain uncomputed."},
        {"gate": "G2", "closed": False, "advance": "The full-Spin10 source route is fixed and the nonlocality repair is retained.", "blocker": "Allowed Sigma-spinor and neutral source cross couplings lack a complete selector and Wilson matching."},
        {"gate": "G3", "closed": False, "advance": "A neutral 210 gives an explicit D-flat SU5 branch with a full-rank physical source-Higgs Hessian.", "blocker": "The coupled Theta/GUT/Kahler/radion vacuum and branch selection are not solved."},
        {"gate": "G4", "closed": False, "advance": "No inconsistent soft sector was imported.", "blocker": "Radion stabilization, SUSY breaking, mu/Bmu, EWSB and the full scalar vacuum are absent."},
        {"gate": "G5", "closed": False, "advance": "The V45 core remains free of the excluded V39 dark benchmark.", "blocker": "No dark sector, relic calculation or cosmological history is specified."},
        {"gate": "G6", "closed": False, "advance": "Exact full-tower characteristics and regulated determinant ratios exist for the idealized two-hyper system.", "blocker": "The enlarged coupled determinant, regulator matching, thresholds, unification, RG and pole spectrum are missing."},
        {"gate": "G7", "closed": False, "advance": "The faithful Z3 and matter parity pass pure finite anomaly tests while the high-degree orientation frontier survives.", "blocker": "The 210-completed operator ring, shifted-KK Wilson coefficients and proton/multinucleon rates are absent."},
        {"gate": "G8", "closed": False, "advance": "The generic PS-wall Yukawa block remains compatible with the retained architecture.", "blocker": "There is no neutrino completion, three-family fit, uncertainty propagation or withheld prediction."},
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_json(path) for name, path in INPUTS.items()}
    v45 = inputs["v45_master"]
    source = inputs["source_higgs"]
    kk = inputs["spinor_kk"]
    global_eta = inputs["global_eta"]
    candidate = updated_candidate(v45, source)
    stages = stage_ledger()
    gates = gate_ledger()
    manifest = source_manifest()
    v46_exact = exact_v46_results(source, kk, global_eta)

    checks = {
        "all_input_core_hashes_verify": True,
        "V45_had_zero_closed_gates": v45["scientific_verdict"]["full_gates_closed"] == 0,
        "singlet_only_126_pair_is_killed": source["singlet_only_126_pair"]["no_go"],
        "singlet_only_massless_count_is_230": source["singlet_only_126_pair"]["dimensions"]["physical_massless_transverse_chirals_at_least"] == 230,
        "neutral_210_repair_selected": source["decision"]["standard_repair_selected"] == "add one neutral 210 boundary chiral",
        "neutral_210_repair_has_only_21_goldstones": source["neutral_210_repair"]["counting"]["eaten_chiral_components"] == 21,
        "neutral_210_repair_has_441_massive_uneaten": source["neutral_210_repair"]["counting"]["generic_massive_uneaten_chiral_components"] == 441,
        "PS_GG_5D_shortcut_rejected": not source["decision"]["PS_GG_shortcut_valid_in_5D"],
        "PS_GG_has_12_adjoint_chiral_zero_modes": source["PS_GG_orbifold_shortcut"]["five_dimensional_vector_obstruction"]["Phi_plus_plus_zero_modes_from_V_minus_minus"] == 12,
        "idealized_finite_b_KK_has_no_zero_modes": kk["V45_consequence"]["exact_massless_KK_modes_if_bL_bR_finite_nonzero"] == 0,
        "idealized_KK_has_no_tachyon": kk["zero_mode_and_tachyon_theorems"]["tachyon_result"].startswith("none"),
        "strong_b_limit_is_not_claimed_safe": any("b=infinity" in row for row in kk["zero_mode_and_tachyon_theorems"]["massless_exceptions"]),
        "Sigma_spinor_terms_remain_obligatory": len(kk["V45_consequence"]["omitted_allowed_source_terms"]) == 2,
        "no_fractional_half_level_obstruction": not global_eta["decision"]["unavoidable_fractional_5D_half_level_obstruction_found"],
        "closed_spin_U1_lattice_screen_passes": global_eta["five_dimensional_parity_half_levels"]["every_individual_shift_lies_in_closed_spin_U1_free_lattice"],
        "pure_combined_Z6_screen_passes": global_eta["decision"]["pure_combined_Z6_Dai_Freed_class_zero"],
        "relative_eta_not_overclaimed": not global_eta["decision"]["actual_quotient_relative_eta_certified"],
        "all_stages_fail_closed": all(row["status"] != "CLOSED" for row in stages),
        "all_eight_gates_open": len(gates) == 8 and all(not row["closed"] for row in gates),
        "all_required_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V46 master integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v46-microscopic-kill-test-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "real_new_physics_obtained": True,
            "complete_theory_established": False,
            "empirically_validated": False,
            "full_gates_closed": 0,
            "full_gates_total": 8,
            "summary": (
                "V46 decisively kills the under-rank 126-pair-plus-singlets source and the "
                "five-dimensional PS/GG shortcut, then selects one neutral 210 as the smallest "
                "standard single-irrep rank repair.  It also proves an exact no-zero/no-tachyon "
                "theorem for the declared finite-boundary two-hyper KK problem and clears every "
                "currently implemented anomaly screen.  The actual quotient-relative eta phase, "
                "all allowed source mixings and the physical reconstruction remain open, so no "
                "full G gate closes."
            ),
            "tests_mean": "deterministic verification of the encoded mathematics, not empirical validation or proof of UV completion",
        },
        "authoritative_candidate": candidate,
        "route_decision": {
            "continue": "neutral-210-repaired full-Spin10 source wall",
            "kill": [
                {
                    "route": "126+bar126 plus singlets",
                    "reason": "at least 230 physical massless chiral components at renormalizable order",
                },
                {
                    "route": "5D PS/GG source wall plus charge-ten singlets",
                    "reason": "12 adjoint-chiral zero modes, fragmented intended spinor zero modes and 0/16 locally anomaly-free intrinsic-sign assignments",
                },
            ],
        },
        "V45_exact_results_retained": v45["exact_results"],
        "V46_exact_results": v46_exact,
        "stage_ledger": stages,
        "gate_ledger": gates,
        "remaining_terminal_calculations": [
            "Compute the relative or stratified spin-bordism group for the exact bulk group and its two centre-quotiented boundary reductions, then evaluate the regulated APS eta phase on generators.",
            "Specify a resolved source-wall regulator and derive the renormalized boundary map B_R(mu), including induced kinetic operators.",
            "Build one enlarged transfer matrix containing both Theta masses and the allowed barSigma HLF HRA and Sigma HLA HRF mixings; prove its complete spectrum and eta phase.",
            "Write the complete allowed source superpotential and Kahler action, solve the coupled Theta/210/126/radion vacuum and quantify the strong-coupling or threshold window.",
            "Recompute the full operator ring, KK Wilson coefficients, unification, RG spectrum, proton limits, flavour, neutrinos, SUSY breaking, dark matter and cosmology in this one retained model.",
        ],
        "research_stopping_rule": (
            "Continue only the neutral-210 full-Spin10-wall candidate.  Kill it if the quotient-relative "
            "eta phase cannot be canceled by a quantized local counterterm, if the enlarged KK operator "
            "has an unavoidable zero/tachyon, if the source sector has no controlled perturbative window, "
            "or if physical likelihood and decay bounds fail throughout the controlled parameter space."
        ),
        "primary_sources": [
            {"topic": "minimal renormalizable 210+126+bar126 vacuum", "url": "https://arxiv.org/abs/hep-ph/0306242"},
            {"topic": "complete minimal SO10 heavy spectrum", "url": "https://arxiv.org/abs/hep-ph/0501025"},
            {"topic": "5D PS/GG adjoint-chiral obstruction", "url": "https://arxiv.org/abs/hep-ph/0108071"},
            {"topic": "5D supersymmetric hypermultiplet boundary equations", "url": "https://arxiv.org/abs/hep-th/0106256"},
            {"topic": "brane-delta regulator and order-of-limits warning", "url": "https://arxiv.org/abs/1408.1852"},
            {"topic": "eta-invariant anomaly framework", "url": "https://arxiv.org/abs/1909.08775"},
            {"topic": "exact Spin times finite-cyclic anomaly conditions", "url": "https://arxiv.org/abs/1808.02881"},
            {"topic": "Spin10 Dai-Freed screen", "url": "https://arxiv.org/abs/1808.00009"},
            {"topic": "centre-quotient global anomaly warning", "url": "https://arxiv.org/abs/2012.11693"},
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
        for row in report["V46_exact_results"]
    )
    stage_rows = "\n".join(
        f"| {row['stage']} | {row['status']} | {row['passed']} | {row['missing']} |"
        for row in report["stage_ledger"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | open | {row['advance']} | {row['blocker']} |"
        for row in report["gate_ledger"]
    )
    remaining = "\n".join(
        f"{index}. {item}" for index, item in enumerate(report["remaining_terminal_calculations"], 1)
    )
    killed = "\n".join(
        f"- {row['route']}: {row['reason']}" for row in report["route_decision"]["kill"]
    )
    return f"""# V46 microscopic kill-test audit

Status: {report['status']}

## Outcome

{verdict['summary']}

This is a real microscopic advance, not a complete theory and not an
experimental validation.  Full predictive gates closed: 0/8.

## One route survives

Continue the V45 four-bulk-spinor interval with the full Spin(10) source wall,
but add one neutral 210 to the neutral 126+bar126 pair.  The retained
renormalizable GUT superpotential is

W_GUT = m Phi^2 + lambda Phi^3 + M Sigma barSigma + eta Phi Sigma barSigma,

with the tensor normalizations frozen in the machine-readable artifact.  Its
SU(5) branch has 462 source-Higgs chiral components: 21 are the required
Goldstones and the remaining 441 are generically massive.

The following routes are killed:

{killed}

The second rejection matters because its charge-ten singlet Higgs subsystem is
healthy in isolation.  It is the five-dimensional gauge multiplet and wall
anomaly structure that fails.

## Exact V46 results

| ID | Result | Certified statement |
|---|---|---|
{exact_rows}

For one idealized conjugate hyper pair the entire characteristic functions are

D++(z) = z S1(z) S2(z) - b^2 F1(z) F2(z),

D-+(z) = G1(z) G2(z) - z b^2 S1(z) S2(z).

At z=0 they equal -b^2 exp[-(M1+M2)L] and exp[+(M1+M2)L].  Thus every finite
nonzero renormalized boundary parameter removes the selected zero modes and
cannot create an unselected zero.  The sign of both functions at negative z
also excludes a tachyon in this supersymmetric self-adjoint problem.  The bare
delta coefficient is not itself b until a regulator prescription is fixed.

## Why the theory is still incomplete

Gauge symmetry permits barSigma HLF HRA and Sigma HLA HRF.  Their direct
selected-zero-mode entries vanish on the SU(5)-singlet VEV, but they mix those
states with source-even KK modes.  They must be included in the enlarged
transfer matrix or forbidden by an exact selector.  Neutral cross couplings
such as STheta Phi^2 and STheta Sigma barSigma also show that source
sequestering is not automatic.

The anomaly screens found no immediate obstruction: all displayed 5D
half-levels occupy the closed-spin U(1) lattice and cancel in common
orientation; the Spin(10) homotopy, Pati-Salam Witten, source Spin(10), Z3F,
matter-parity and combined Z6 tests pass.  This does not calculate the actual
relative APS eta invariant for the PS/Z2-diagonal wall and the full-Spin(10)
wall on arbitrary non-liftable bundles.

## Research stages

| Stage | Status | Exact progress | Missing closure object |
|---|---|---|---|
{stage_rows}

## G1-G8 ledger

| Gate | Status | V46 advance | Why it remains open |
|---|---|---|---|
{gate_rows}

## Mandatory next calculations

{remaining}

Stopping rule: {report['research_stopping_rule']}

Repository tests certify artifact integrity and the displayed derivations only.
They do not certify nature, a UV completion or a fitted likelihood.

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
        raise RuntimeError("V46 master JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V46 master Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V46_MICROSCOPIC_KILL_TEST_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
