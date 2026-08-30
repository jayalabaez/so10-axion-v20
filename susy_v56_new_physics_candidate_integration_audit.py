#!/usr/bin/env python3
"""Integrate the V56 topology escapes into one fail-closed decision record.

This module does not claim an empirical discovery.  It binds the exact V55 kill
test and four V56 architecture audits, rejects two internally constructed 4D
selectors, retains a published 4D missing-partner mechanism as a UV-stressed
backup, and selects a 6D orbifold plus Z4R action as the next executable
frontier candidate.  No result is promoted across inequivalent actions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V56_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V56_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v56_new_physics_candidate_integration_audit.py"

INPUTS = {
    "v55_master": ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.json",
    "architecture": ROOT / "SUSY_V56_ARCHITECTURE_ESCAPE_RESEARCH_AUDIT.json",
    "two_site": ROOT / "SUSY_V56_TWO_SITE_LINK_PARITY_SELECTOR_AUDIT.json",
    "m_dressed": ROOT / "SUSY_V56_R1_M_DRESSED_B_TOPOLOGY_HESSIAN_AUDIT.json",
    "orbifold_z4r": ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json",
}

EXPECTED_CORES = {
    "v55_master": "52d0044e8d227be29b2cab63c565c1f4335aae9a72c9d51f3c9044fe7289a1f7",
    "architecture": "3f3f662cdb8ba0e1081dc77fa2d579fef7c5421b97ca7b16fdce0760f796af0a",
    "two_site": "334778d7082f133c14c800c97b20a82a01394366e8903b46669e6a7d54b186c0",
    "m_dressed": "700122eddf3e303c760030c6346402489bc0bc6c9814f7ac6f17519019e16684",
    "orbifold_z4r": "09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55",
}

STATUS = (
    "V56_NEW_PHYSICS_CANDIDATE__FIXED_R1_REJECTED__M_DRESSED_REJECTED_AT_"
    "DEGREE4__TWO_SITE_REJECTED_AT_DEGREE6__4D_MISSING_PARTNER_RETAINED_AS_"
    "UV_STRESSED_BACKUP__6D_T2Z2_SU5_BRANE_Z4R_SELECTED_FRONTIER__TWO_WEAK_"
    "ZERO_MODES_ZERO_COLOR__DIRECT_R0_MASS_PROTECTED__BOUNDARY_KK_ANOMALY_"
    "THRESHOLD_PROTON_FLAVOUR_OPEN__ZERO_GATE_PROMOTIONS__COMPLETE_THEORY_FALSE"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing V56 input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def item_by_id(rows: list[dict[str, Any]], wanted: str) -> dict[str, Any]:
    return next(row for row in rows if row["id"] == wanted)


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN for V56: the local SU(5)xU(1)X family anomaly cancels and the "
            "irreducible 6D gauge coefficient vanishes, but gravitational, reducible, "
            "localized, discrete-R, global, and physical GS sectors are unfinished."
        ),
        "G2": (
            "OPEN: the projector, R selection, matter terms, anomaly fragments, thresholds, "
            "proton matching, flavour fit, and SUSY breaking are not yet one closed action; "
            "a globally defined discrete-gauge Z4R for the full 6D compactification has not "
            "been constructed."
        ),
        "G3": (
            "OPEN: the free orbifold projector is exact, but the interacting bulk-plus-brane "
            "vacuum and regulated infinite-KK quadratic operator are not solved."
        ),
        "G4": (
            "OPEN with a real advance: exactly two weak and zero colored free zero modes are "
            "proved, and neutral R0 VEV dressing cannot make HH'; allowed H-Hc and normal-"
            "derivative boundary operators remain unclassified."
        ),
        "G5": "OPEN: no dark sector, relic calculation, or cosmological history is supplied.",
        "G6": (
            "OPEN: compactification radii, cutoff, brane kinetic terms, complete KK thresholds, "
            "and precision unification are not matched."
        ),
        "G7": (
            "OPEN: direct matter dimension-five and perturbative RPV terms are forbidden and "
            "a finite KK witness has zero H-H inverse block, but infinite-KK C5, C6, dressing, "
            "flavour rotations, and proton lifetimes are not computed."
        ),
        "G8": (
            "OPEN: local up, down, charged-lepton, and RH-neutrino operators exist, but the "
            "minimal SU(5) relations, mediator sector, seesaw scales, and current global fit "
            "remain unresolved."
        ),
    }
    return [
        {
            "gate": f"G{i}",
            "V56_candidate_closed": False,
            "status": "OPEN",
            "decision": decisions[f"G{i}"],
        }
        for i in range(1, 9)
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_bound(name, path) for name, path in INPUTS.items()}
    v55 = inputs["v55_master"]
    architecture = inputs["architecture"]
    two_site = inputs["two_site"]
    m_dressed = inputs["m_dressed"]
    orbifold = inputs["orbifold_z4r"]

    missing = item_by_id(architecture["blueprints"], "BP1_4D_SO10_126_MISSING_PARTNER")
    locality = item_by_id(architecture["blueprints"], "BP2_6D_SO10_T2_OVER_Z2_LOCALITY")
    m_fatal = m_dressed["higher_dimensional_fatal_filler_audit"]
    two_fatal = two_site["factorized_epsilon_and_adjoint_stress_test"][
        "first_explicit_vacuum_nonzero_counterexample"
    ]
    modes = orbifold["orbifold_mode_certificate"]
    dressing = orbifold["neutral_VEV_dressing_certificate"]
    anomalies = orbifold["anomaly_audit"]
    proton = orbifold["proton_audit"]
    gates = gate_ledger()

    routes = [
        {
            "id": "R0_FIXED_R1",
            "theory": "4D N=1 SO(10) fixed R1 source/filter topology",
            "decision": "REJECTED",
            "first_decisive_failure_degree": 3,
            "decisive_operator": "h A H2 and L h H2",
            "effect": "generic completed weak rank 16; zero weak-Higgs modes",
            "gate_promotions": [],
        },
        {
            "id": "R1_M_DRESSED_B",
            "theory": "4D N=1 SO(10) zero-new-field M-dressed-B topology",
            "decision": "REJECTED",
            "first_decisive_failure_degree": m_fatal["first_fatal_total_degree"],
            "decisive_operator": "K h^T A H2/Lambda and L K h^T H2/Lambda",
            "effect": "each produces weak rank 16 and removes the protected pair",
            "gate_promotions": [],
        },
        {
            "id": "R2_TWO_SITE_LINK_PARITY",
            "theory": "4D Spin(10)L x Spin(10)R two-site link EFT",
            "decision": "REJECTED",
            "first_decisive_failure_degree": two_fatal["total_degree"],
            "decisive_operator": two_fatal["operator"],
            "effect": two_fatal["effect"],
            "gate_promotions": [],
        },
        {
            "id": "R3_4D_MISSING_PARTNER",
            "theory": missing["theory_category"],
            "decision": "BACKUP_MECHANISM_ONLY",
            "first_decisive_failure_degree": None,
            "decisive_operator": None,
            "effect": (
                "structural witness has triplet rank 6/6 and doublet rank 4/5, but the "
                "Clebsch-resolved Hessian, vacuum, operator completion, and matching are open"
            ),
            "one_loop_b": missing["uv_pressure_certificate"]["one_loop_b"],
            "one_loop_pole_over_M_SO10": missing["uv_pressure_certificate"][
                "one_loop_pole_over_M_SO10"
            ],
            "gate_promotions": [],
        },
        {
            "id": "R4_6D_ORBIFOLD_Z4R",
            "theory": locality["theory_category"],
            "decision": "SELECTED_EXECUTABLE_FRONTIER_CANDIDATE",
            "first_decisive_failure_degree": None,
            "decisive_operator": None,
            "effect": "exact free projector: two weak zero modes and zero colored zero modes",
            "gate_promotions": [],
        },
    ]

    integration_checks = {
        "all_input_cores_are_canonical_and_expected": all(
            inputs[name]["core_sha256"] == expected
            for name, expected in EXPECTED_CORES.items()
        ),
        "fixed_R1_remains_rejected_with_zero_V55_gate_promotions": (
            v55["final_decision"]["R1_fixed_topology_rejected"]
            and v55["final_decision"]["full_gates_closed_for_V55_candidate"] == 0
        ),
        "M_dressed_route_is_rejected_at_degree4": (
            m_fatal["all_order_topology_verdict"] == "REJECTED"
            and m_fatal["first_fatal_total_degree"] == 4
            and len(m_fatal["named_exact_invariants"]) >= 2
        ),
        "two_site_route_is_rejected_at_degree6": (
            two_fatal["total_degree"] == 6
            and two_fatal["vacuum_nonzero"]
            and two_fatal["Tr_A0_B0"] == -6
        ),
        "missing_partner_backup_has_rectangular_rank_witness": (
            missing["rank_certificate"]["triplet_rank"] == 6
            and missing["rank_certificate"]["doublet_rank"] == 4
            and missing["rank_certificate"]["doublet_right_nullity"] == 1
        ),
        "orbifold_projector_has_exactly_two_weak_and_zero_colored_modes": (
            modes["weak_doublet_zero_mode_count"] == 2
            and modes["color_triplet_zero_mode_count"] == 0
            and modes["conjugate_Hc_zero_mode_count"] == 0
        ),
        "neutral_R0_VEV_charge_lemma_forbids_HHp_mass_and_finite_census_confirms_it": (
            dressing["all_dressed_H_Hp_terms_forbidden"]
            and dressing["all_declared_VEV_charges"] == [0, 0, 0]
            and dressing["maximum_total_insertion_degree"] == 12
            and dressing["number_of_exponent_vectors_checked"] == 455
        ),
        "selected_brane_family_and_rank_breaking_gauge_anomalies_cancel": (
            anomalies["O_GG_local_chiral_gauge_anomalies"]["per_family_sums"]
            == {
                "SU5_cubic": 0,
                "SU5_squared_U1X": "0",
                "U1X_cubed": 0,
                "gravity_squared_U1X": 0,
            }
            and anomalies["O_GG_local_chiral_gauge_anomalies"]
            ["X_plus10_Xbar_minus10_pair"]["vectorlike_and_gauge_anomaly_free"]
        ),
        "only_irreducible_6D_gauge_anomaly_is_currently_closed": (
            anomalies["six_dimensional_bulk"]["irreducible_gauge_anomaly_cancels"]
            and anomalies["six_dimensional_bulk"]["reducible_anomaly_status"].startswith(
                "OPEN"
            )
            and anomalies["six_dimensional_bulk"]["full_supergravity_status"].startswith(
                "OPEN"
            )
        ),
        "finite_proton_witness_is_conditional_not_a_lifetime_proof": (
            proton["KK_colored_higgsino_exchange"]["certificate_passes"]
            and "not been evaluated"
            in proton["KK_colored_higgsino_exchange"]["not_a_full_proof"]
        ),
        "boundary_and_infinite_KK_loophole_is_fail_closed": (
            not orbifold["decision"]["all_boundary_operators_closed"]
            and "normal-derivative"
            in " ".join(orbifold["decisive_open_falsifiers"])
        ),
        "selected_candidate_is_not_claimed_complete_or_empirical": (
            not orbifold["decision"]["complete_theory"]
            and not orbifold["decision"]["one_action_completion"]
        ),
        "no_V56_gate_is_promoted": not any(
            row["V56_candidate_closed"] for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy-v56-new-physics-candidate-integration-audit-v1",
        "status": STATUS,
        "input_core_hashes": {name: value["core_sha256"] for name, value in inputs.items()},
        "expected_input_core_hashes": EXPECTED_CORES,
        "same_action_rule": (
            "A G1-G8 gate may close only when every premise is established in one canonical "
            "action.  Rejected R1/two-site calculations and the 4D missing-partner backup "
            "cannot be imported into the selected 6D orbifold action."
        ),
        "meaning_of_new_physics": {
            "created": True,
            "kind": "new falsifiable theoretical candidate architecture",
            "not_claimed": [
                "empirical discovery",
                "experimentally confirmed physics",
                "UV-complete quantum gravity",
                "complete G1-G8 theory",
            ],
            "architecture_change": (
                "Replace the fatal finite 4D additive Higgs selector by component-dependent "
                "orbifold boundary conditions, then protect the surviving pair with a "
                "conventional 4D N=1 Z4R selection rule on the SU(5)xU(1)X brane."
            ),
        },
        "route_ledger": routes,
        "selected_frontier_action": {
            "id": "V56_6D_T2_Z2_SU5_BRANE_Z4R",
            "bulk": "6D N=1 SO(10) gauge theory on T2/Z2",
            "bulk_Higgs_hypermultiplets": [
                {"name": "H10", "intrinsic_translations": [1, -1]},
                {"name": "H10_prime", "intrinsic_translations": [-1, 1]},
            ],
            "selected_fixed_point": "O_GG with local SU(5) x U(1)X",
            "brane_chiral_content": [
                "3 x (10_-1 + bar5_3 + 1_-5)",
                "X_+10 + Xbar_-10",
                "S_0",
            ],
            "Z4R_charges": {
                "theta": 1,
                "H_and_Hprime": 0,
                "Hc_and_Hprimec": 2,
                "matter": 1,
                "X_and_Xbar": 0,
                "S": 2,
                "superpotential": 2,
            },
            "allowed_core_terms": [
                "10_-1 10_-1 H5",
                "10_-1 bar5_3 Hprime_bar5",
                "1_-5 1_-5 X_+10",
                "S(X Xbar - vX^2)",
                "S H Hprime",
                "S Hc Hprimec",
            ],
            "supersymmetric_mu_result": (
                "F_X=S Xbar=0 and F_Xbar=S X=0 with nonzero X,Xbar imply <S>=0; "
                "the supersymmetric Higgs mass vanishes.  Soft R breaking may give "
                "<S> of order the soft scale and mu=lambda<S>."
            ),
            "exact_certificates": {
                "weak_doublet_zero_modes": modes["weak_doublet_zero_mode_count"],
                "color_triplet_zero_modes": modes["color_triplet_zero_mode_count"],
                "Hc_zero_modes": modes["conjugate_Hc_zero_mode_count"],
                "zero_mode_names": modes["zero_modes"],
                "neutral_VEV_dressing_degree": dressing[
                    "maximum_total_insertion_degree"
                ],
                "neutral_VEV_exponent_vectors": dressing[
                    "number_of_exponent_vectors_checked"
                ],
                "all_declared_GUT_VEV_R_charges_zero": (
                    dressing["all_declared_VEV_charges"] == [0, 0, 0]
                ),
                "all_order_R0_charge_lemma": orbifold["decision"]["exact_statement"],
                "direct_matter_dimension5": proton[
                    "direct_superpotential_dimension5"
                ],
                "perturbative_RPV_dimension4": proton[
                    "perturbative_RPV_dimension4"
                ],
                "finite_KK_HH_inverse_block_zero": proton[
                    "KK_colored_higgsino_exchange"
                ]["certificate_passes"],
            },
            "scope_boundary": (
                "The zero-mode statement is exact for the free projector and the R0-VEV "
                "mass statement is exact for non-derivative brane superpotential bilinears. "
                "Neither statement includes the full boundary differential-operator basis. "
                "The protection is conditional on a globally consistent discrete-gauge Z4R "
                "acting on the 6D supercharges, gauge multiplet, superspace measure, translation "
                "twists, and all four fixed points; that realization is not yet constructed."
            ),
        },
        "backup_action": {
            "id": "BP1_4D_SO10_126_MISSING_PARTNER",
            "status": "MECHANISM_SURVIVOR_NOT_COMPLETED_ACTION",
            "triplet_rank": missing["rank_certificate"]["triplet_rank"],
            "triplet_dimension": missing["rank_certificate"]["triplet_shape"][0],
            "doublet_rank": missing["rank_certificate"]["doublet_rank"],
            "doublet_dimension": missing["rank_certificate"]["doublet_shape"][0],
            "one_loop_b": missing["uv_pressure_certificate"]["one_loop_b"],
            "pole_over_M_SO10": missing["uv_pressure_certificate"]
            ["one_loop_pole_over_M_SO10"],
            "reason_not_selected": (
                "The structural rank mechanism is credible, but the large 126+126bar+210+120 "
                "inventory becomes strongly coupled only about 1.75 times above the declared "
                "SO(10) scale and no Clebsch-resolved one-action completion was built."
            ),
        },
        "decisive_open_obligations": [
            {
                "id": "O1_BOUNDARY_OPERATOR_COMPLETION",
                "requirement": (
                    "Classify every supersymmetric H-Hc and normal-derivative operator at "
                    "all four fixed points and compute the regulated infinite KK determinant."
                ),
                "falsifier": "a lifted weak pair, colored zero mode, or hard Hc-Hc block",
            },
            {
                "id": "O2_ANOMALY_AND_GS_COMPLETION",
                "requirement": (
                    "Supply the full 6D supergravity/tensor/hidden ledger, factorized anomaly "
                    "polynomial, localized inflow, and quantized discrete-R GS cancellation. "
                    "Construct the global Z4R action on supercharges, gauge fields, measure, "
                    "translation twists, and every fixed point."
                ),
                "falsifier": "any uncancelled bulk, local, global, or discrete anomaly",
            },
            {
                "id": "O3_THRESHOLD_AND_CUTOFF_MATCHING",
                "requirement": (
                    "Fix R5, R6, M*, brane kinetic terms and U(1)X boundary masses, then "
                    "match the full KK thresholds and two-loop low-energy couplings."
                ),
                "falsifier": "loss of perturbative control or precision unification",
            },
            {
                "id": "O4_PROTON_AND_FLAVOUR_MATCHING",
                "requirement": (
                    "Derive infinite-KK C5/C6 tensors, SUSY dressing and lifetimes; construct "
                    "a mediator-complete Yukawa/seesaw sector and fit current flavour data."
                ),
                "falsifier": "excluded proton lifetime or failed fermion/neutrino fit",
            },
            {
                "id": "O5_SOFT_VACUUM_AND_COSMOLOGY",
                "requirement": (
                    "Specify supersymmetry breaking, stabilize moduli and radii, prove the "
                    "global vacuum, obtain EWSB, and test collider and cosmological bounds."
                ),
                "falsifier": "unstable vacuum, wrong spectrum, or failed cosmology",
            },
        ],
        "gate_ledger": gates,
        "final_decision": {
            "candidate_architecture_created": True,
            "selected_executable_frontier_candidate": "V56_6D_T2_Z2_SU5_BRANE_Z4R",
            "selected_complete_candidate": None,
            "same_action_completion": False,
            "complete_theory": False,
            "empirical_new_physics_discovery": False,
            "V56_candidate_closed_gates": [],
            "full_gates_closed_for_V56_candidate": 0,
            "historical_G1_namespace_may_not_be_imported": True,
            "honest_outcome": (
                "V56 creates a concrete, executable new-theory candidate that escapes the "
                "proved 4D selector obstruction by changing the spacetime architecture.  Its "
                "free zero-mode projector and a bounded brane Z4R protection sector pass exact "
                "tests.  It is not yet a complete or empirically validated theory, and no G1-G8 "
                "gate is closed until the boundary, anomaly, KK, threshold, proton, flavour, "
                "soft-vacuum, and cosmology obligations are solved in this same action."
            ),
        },
        "verification_run": {
            "date": "2026-08-29",
            "python_compile": {"V56_audit_scripts": 5, "passed": True},
            "focused_V56_pytest": {
                "passed": 63,
                "failed": 0,
                "scope": "all five V56 component and integration test modules",
            },
            "historical_pytest": {
                "passed": 829,
                "failed": 0,
                "scope": "all test_susy_v40 through test_susy_v56 modules",
                "evidence_kind": (
                    "recorded direct pytest execution; this count is not recursively "
                    "recomputed by the integration test module"
                ),
                "command": (
                    "python -m pytest -q <all test_susy_vN*.py modules with N >= 40>"
                ),
            },
            "supported_artifact_freshness_checks_passed": True,
        },
        "primary_sources": [
            {
                "title": "SO(10) Unified Theories in Six Dimensions",
                "url": "https://arxiv.org/abs/hep-ph/0108071",
                "use": "orbifold parities, doublet-triplet splitting, and 6D anomaly target",
            },
            {
                "title": "A unique Z4R symmetry for the MSSM",
                "url": "https://arxiv.org/abs/1009.0905",
                "use": "SO(10)-compatible low-energy Z4R and soft-scale mu motivation",
            },
            {
                "title": "Missing Partner Mechanism in SO(10) Grand Unification",
                "url": "https://arxiv.org/abs/hep-ph/0612315",
                "use": "4D backup rank architecture and UV-pressure comparison",
            },
            {
                "title": "Localized anomalies in orbifold gauge theories",
                "url": "https://arxiv.org/abs/hep-th/0612212",
                "use": "localized fixed-point anomaly obligations",
            },
        ],
        "integrity_checks": integration_checks,
        "n_failed_integrity_checks": sum(
            not value for value in integration_checks.values()
        ),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V56 integration status or core drift")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("V56 integration integrity failure")
    decision = report["final_decision"]
    if not decision["candidate_architecture_created"]:
        raise RuntimeError("V56 candidate creation was lost")
    if decision["complete_theory"] or decision["same_action_completion"]:
        raise RuntimeError("V56 completion was overclaimed")
    if decision["empirical_new_physics_discovery"]:
        raise RuntimeError("V56 empirical discovery was overclaimed")
    if decision["V56_candidate_closed_gates"]:
        raise RuntimeError("V56 gate was overpromoted")


def render_markdown(report: Mapping[str, Any]) -> str:
    selected = report["selected_frontier_action"]
    exact = selected["exact_certificates"]
    backup = report["backup_action"]
    route_lines = "\n".join(
        f"- `{row['id']}` — **{row['decision']}**: {row['effect']}"
        for row in report["route_ledger"]
    )
    obligation_lines = "\n".join(
        f"- `{row['id']}`: {row['requirement']} Falsifier: {row['falsifier']}."
        for row in report["decisive_open_obligations"]
    )
    gate_lines = "\n".join(
        f"- `{row['gate']}` — `{row['status']}`: {row['decision']}"
        for row in report["gate_ledger"]
    )
    return f"""# V56 new-physics candidate integration audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Outcome

{report['final_decision']['honest_outcome']}

This is new physics in the limited and legitimate sense of a **new falsifiable
theoretical candidate architecture**. It is not an empirical discovery, a
UV-complete theory, or a completed G1-G8 solution. The V56 candidate closes
`0/8` gates.

## Architecture decision

{route_lines}

The selected action is `{selected['id']}`: {selected['bulk']}, with two bulk 10
hypermultiplets carrying intrinsic translations `(+,−)` and `(−,+)`. Matter and
rank breaking live on the `SU(5) x U(1)X` fixed point, where a conventional
`Z4R` assignment replaces the failed 4D additive selector.

The 4D missing-partner route remains a separate backup. Its structural matrices
have triplet rank `{backup['triplet_rank']}/{backup['triplet_dimension']}` and
doublet rank `{backup['doublet_rank']}/{backup['doublet_dimension']}`, but its
one-loop coefficient is `{backup['one_loop_b']}` and its estimated pole is only
`{backup['pole_over_M_SO10']:.6g}` times the declared SO(10) scale. It is not
merged into the selected action.

## Exact advances inside the selected candidate

- The free orbifold projector gives exactly `{exact['weak_doublet_zero_modes']}`
  weak-doublet zero modes, `{exact['color_triplet_zero_modes']}` colored zero
  modes, and `{exact['Hc_zero_modes']}` conjugate-hypermultiplet zero modes.
- The surviving pair is `{', '.join(exact['zero_mode_names'])}`.
- Because every declared GUT-scale VEV has `R=0`, the all-order charge lemma
  forbids every neutral-VEV dressing of the `R0-R0` Higgs mass. A finite census
  through insertion degree `{exact['neutral_VEV_dressing_degree']}` confirms it
  on `{exact['neutral_VEV_exponent_vectors']}` enumerated exponent vectors.
- The local up/down Yukawas, `X NN`, rank-breaking, and soft-scale mu mechanism
  are mutually compatible at the declared charge-bookkeeping level.
- Each localized family and the `X+Xbar` pair are gauge-anomaly free. The bulk
  vector plus two same-chirality 10 hypers cancels the irreducible 6D gauge
  anomaly only; this is not a complete anomaly cancellation.
- Direct matter dimension five is `{exact['direct_matter_dimension5']}` and
  perturbative RPV dimension four is `{exact['perturbative_RPV_dimension4']}`.
  A finite KK witness has a zero matter-coupled H-H inverse block, but this is
  not an infinite-KK lifetime calculation.

## Why the other internal redesigns fail

The M-dressed-B repair reproduces the desired local Hessian but is killed at
degree four by `K h A H2/Lambda` and `L K h H2/Lambda`. The two-site link-parity
repair protects connected paths but fails at degree six because
`(h Omega H2) Tr(A B Omegabar^T)` is gauge invariant, parity even, and nonzero
on the vacuum (`Tr(A0 B0)=-6`). These are rejection certificates, not tunable
warnings.

## Decisive next tests

{obligation_lines}

The immediate kill test is `O1`: classify the complete boundary differential
operator basis and compute the regulated infinite KK determinant. A failure
there rejects V56; a pass would justify proceeding to the anomaly and matching
program. Even a pass is conditional until `O2` constructs a globally defined
discrete-gauge `Z4R` on the entire 6D orbifold action.

## G1-G8 ledger

{gate_lines}

The historical G1 lemma remains isolated in its earlier ordinary-Spin
namespace and is not imported into this 6D action.

## Verification

The five V56 audit modules pass `{report['verification_run']['focused_V56_pytest']['passed']}`
focused tests. The complete V40-V56 regression passes
`{report['verification_run']['historical_pytest']['passed']}` tests with zero
failures in the recorded direct run; the master tests do not recursively rerun
that entire suite. Generated JSON and Markdown freshness are tested.

## Primary sources

- [SO(10) Unified Theories in Six Dimensions](https://arxiv.org/abs/hep-ph/0108071)
- [A unique Z4R symmetry for the MSSM](https://arxiv.org/abs/1009.0905)
- [Missing Partner Mechanism in SO(10) Grand Unification](https://arxiv.org/abs/hep-ph/0612315)
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0612212)
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_outputs(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V56 generated artifacts are missing")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V56 JSON artifact is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V56 Markdown artifact is stale")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="check generated artifacts")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        check_outputs(report)
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
