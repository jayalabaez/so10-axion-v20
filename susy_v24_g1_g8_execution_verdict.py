#!/usr/bin/env python3
"""Terminal, fail-closed G1--G8 verdict for the V24 Pati--Salam campaign.

V24 creates a new, executable research model: the derived
PSZ4RZ11SUSYV24 selector/source on the Kawamura--Raby Pati--Salam base.
This ledger pins the exact V23 baseline and all three V24 producer bundles,
rechecks their canonical cores, and records the sharp boundary between the
landed source/rank/vacuum/RG witnesses and a complete predictive theory.
Every full G1--G8 gate remains false.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V24_G1_G8_EXECUTION_VERDICT.json"
OUT_MD = ROOT / "SUSY_V24_G1_G8_EXECUTION_VERDICT.md"
SCHEMA = "susy_v24_g1_g8_execution_verdict_v1"


# Raw pins bind this terminal decision to the exact reviewed bytes.  The JSON
# core ledger below independently verifies canonical semantic integrity.
SOURCE_PINS = {
    "susy_v23_g1_g8_execution_verdict.py":
        "1b3d46b6cc17436066fa33e4a7e6702e5ece536a6375b9f9507bae37c15dc009",
    "SUSY_V23_G1_G8_EXECUTION_VERDICT.json":
        "495ae179eff96c40cf787c9fe154437ba0941c06679af581a44a0db1983387a7",
    "SUSY_V23_G1_G8_EXECUTION_VERDICT.md":
        "f9326bd8bdee7046a813c266fa2beecfad557ffc5cc9ac30fe027681785bae21",
    "susy_v24_architecture_decision.py":
        "1016de11dbee9dce9d912a0e49fa90053b273ce0564b04f05a42f5ea1f2d179a",
    "SUSY_V24_ARCHITECTURE_DECISION.json":
        "9489128ef689ed21db60c06e4964f7f97de4990e6c81e1c89b1e3bf54b5ca9f6",
    "SUSY_V24_ARCHITECTURE_DECISION.md":
        "0249587b53c06853f0a8b2e055f3944bc557fefbcf61b3927db94b4ce3db581b",
    "susy_v24_ps_source_contract.py":
        "4993924ebf64a8eb05f83290174adaffe277342234d1ae43e78d992b3efbf4da",
    "SUSY_V24_PS_SOURCE_CONTRACT.json":
        "c2457e188877a2729e092acf6ddbf76626b884a4c1cb652c282da215f268ce51",
    "SUSY_V24_PS_SOURCE_CONTRACT.md":
        "8ab2697b3efdbec45d48db53074743faefa1a7740989397e295a41f75855c8f5",
    "susy_v24_ps_vacuum_rg_frontier.py":
        "c5af70ab22756d79eb72a4d5a3c2c23f86a1f1378cb8e09c1e67076609d44125",
    "SUSY_V24_PS_VACUUM_RG_FRONTIER.json":
        "4f47ca9b18902a744c138ddceeec461036e41c6803bb7d60a68a276e09499c0d",
    "SUSY_V24_PS_VACUUM_RG_FRONTIER.md":
        "593a8ce804651746a99e584b991f773ac771053b7c77242bd6444078c93c5ec8",
    "models/PSZ4RZ11SUSYV24/PSZ4RZ11SUSYV24.m":
        "09326668d02b32b4a66c3b79cba34fb6a709430a360dce6d2d5d2ab039cad2bf",
    "models/PSZ4RZ11SUSYV24/parameters.m":
        "1a15d9c29e324a33fc2363fc6fa2e9f871bee2ec3253b98961d25442c32e9992",
    "models/PSZ4RZ11SUSYV24/particles.m":
        "6c7be1d5ee866cfd8b6696c48edfec5f385f9da13decd045baa21e4881369b47",
    "tools/validate-susy-v24-ps.wls":
        "751d44288efebd29daccb8601201b2a8c45eb713dfd06fa23d5d8b39db92deb9",
    "susy_v24_non_gs_anomaly_completion_nogo.py":
        "55054c9bb70629c1ed099dd22c7d54ada510610dced5496ef11ee00db2875bc3",
    "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.json":
        "c28214d0e3be810e26beeff040e3379a42a0d306dd2fe56f87e52de4b4d26941",
    "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.md":
        "57ecbd0460af8830b6616419e8c20b9f8dd35b5a8ce116f8f9b6a96caf3e7fdb",
    "test_susy_v24_non_gs_anomaly_completion_nogo.py":
        "5dd5bf5d58960656dfcdbd99481406b6e11983599b8d8e14fa94bd9972ffd9db",
}


UPSTREAMS = {
    "v23_terminal_baseline": {
        "path": "SUSY_V23_G1_G8_EXECUTION_VERDICT.json",
        "core_sha256": "ab16d07e95c8ca24873523ecb6e145e84fd46fb3b39f2a6a98b0c3349c3396ca",
        "metadata": {
            "schema": "susy_v23_g1_g8_execution_verdict_v1",
            "namespace": "terminal.susy_so10.v23.G1_G8.execution_verdict",
            "status": (
                "V23_G1_G8_EXECUTION_COMPLETE__PRIMARY_RESEARCH_FRONTIER_"
                "LANDED__NO_COMPLETE_THEORY__ZERO_OF_EIGHT_FULL_GATES"
            ),
        },
    },
    "v24_architecture": {
        "path": "SUSY_V24_ARCHITECTURE_DECISION.json",
        "core_sha256": "f091f1a452b815bb32c780a5062704532818d0517254960ed799fecfe3fcb71b",
        "metadata": {
            "schema": "susy_v24_architecture_decision_v1",
            "namespace": "research.susy_gut.v24.architecture_decision",
            "status": (
                "V24_ARCHITECTURE_DECISION_FROZEN__DERIVED_PSZ4RZ11_SELECTED_"
                "ON_KAWAMURA_RABY_PS_BASE__NO_FULL_G1_G8_COMPLETION"
            ),
        },
    },
    "v24_source": {
        "path": "SUSY_V24_PS_SOURCE_CONTRACT.json",
        "core_sha256": "d408aa7d7d3096ac917f5bd6f4f37576aace4cd78709bf4810b8e036dc2d93a8",
        "metadata": {
            "schema": "susy_v24_ps_z11_source_contract_v2",
            "status": (
                "V24_PS_Z11_NONZERO_W_SOURCE_LANDED__G1_G2_PARTIAL__"
                "GS_MODULUS_UV_AND_FULL_COMPONENT_HESSIAN_OPEN"
            ),
        },
    },
    "v24_vacuum_rg": {
        "path": "SUSY_V24_PS_VACUUM_RG_FRONTIER.json",
        "core_sha256": "9f47db6cb3bb97b10b4554b8b3f51f146c09820bd202d7b6dcb429891fece780",
        "metadata": {
            "namespace": "active.susy_pati_salam_z4r_z11_rp2.v24.vacuum_rg_frontier",
            "status": (
                "V24_PS_Z11_RP2_VACUUM_RG_FRONTIER_LANDED__P_ONLY_AXION_"
                "ARITHMETIC__GS_INCLUSIVE_WALL_OPEN__FULL_G1_G8_OPEN"
            ),
        },
    },
    "v24_non_GS_completion_nogo": {
        "path": "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.json",
        "core_sha256": "ee04ddfb4b879efb8e756f54e174b9e33ec35e39ea9a0a58a6741d1249e78932",
        "metadata": {
            "schema_version": 1,
            "status": (
                "V24_MINIMAL_NON_GS_ANOMALY_COMPLETION_NOGO_FROZEN__"
                "GS_OR_NEW_SHAPING_PHYSICS_REMAINS_REQUIRED"
            ),
        },
    },
}


MODEL_PATH = "models/PSZ4RZ11SUSYV24/PSZ4RZ11SUSYV24.m"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded)


def source_manifest(root: Path) -> list[dict[str, Any]]:
    rows = []
    for relative, expected in SOURCE_PINS.items():
        path = root / relative
        observed = sha256(path.read_bytes()) if path.is_file() else None
        rows.append({
            "path": relative,
            "mode": "raw",
            "expected_sha256": expected,
            "sha256": observed,
            "matches": observed == expected,
        })
    return rows


def load_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def json_core_valid(payload: Mapping[str, Any]) -> bool:
    return (
        isinstance(payload.get("core_sha256"), str)
        and canonical_sha(payload) == payload["core_sha256"]
    )


def gate_ledger() -> list[dict[str, Any]]:
    rows = {
        "G1": {
            "state": "EXECUTABLE_RENORMALIZABLE_SOURCE_LANDED__FULL_UV_OPERATOR_CONTRACT_OPEN",
            "evidence_landed": [
                "genuine SARAH 4.15.3 Start[] and post-Start processing of a nonzero W",
                "exact 80-class degree<=3 gauge census with 18 selector-allowed classes",
                "all 18 processed field structures match the declared structural multiset",
                "the component superpotential has 18 couplings and the required representative coupling families",
                "unique renormalizable PS tensor channels and a renormalizable seesaw messenger channel",
            ],
            "open_requirements": [
                "all-order holomorphic, Kahler, soft, and higher-field operator contract",
                "dynamical Green--Schwarz axion/modulus, stabilization, and UV realization",
                "hidden-sector audit preserving the residual Z2 matter parity",
            ],
        },
        "G2": {
            "state": "EXACT_SOURCE_HESSIAN_RANK_LANDED__PHYSICAL_POLE_SPECTRUM_OPEN",
            "evidence_landed": [
                "exact generic PS-breaking superpotential Hessian rank 14/23",
                "the nine-dimensional kernel equals the nine PS/SM gauge-Goldstone directions",
                "full-rank colored block and rank-one-by-four vectorlike family mass rows",
            ],
            "open_requirements": [
                "gauge-fixed full scalar/fermion component Hessians including soft and PQ sectors",
                "complete SM decomposition, pole eigenvalues, and correlated thresholds",
            ],
        },
        "G3": {
            "state": "ZERO_ENERGY_GLOBAL_SUSY_BRANCH_LANDED__FULL_STABILIZED_VACUUM_OPEN",
            "evidence_landed": [
                "explicit equal-conjugate-VEV PS branch with every F term and D term zero",
                "zero energy is globally minimal for the nonnegative global-SUSY F+D potential",
            ],
            "open_requirements": [
                "complete soft/Kahler/PQ potential",
                "competing-branch exclusion and positive full physical Hessian",
                "radiative electroweak and PQ vacuum selection",
            ],
        },
        "G4": {
            "state": "REPRESENTATION_AND_R_PROTECTION_LANDED__WEAK_HIERARCHY_OPEN",
            "evidence_landed": [
                "H=(1,2,2) contains one Hu,Hd pair and no colored partner",
                "the supersymmetric H mass vanishes at X=0 and w0 H^2 permits mu at the soft scale",
                "the P VEV leaves the Z2 matter-parity subgroup",
            ],
            "open_requirements": [
                "explicit mediation and soft spectrum",
                "radiative EWSB and a stable weak hierarchy",
                "physical heavy thresholds",
            ],
        },
        "G5": {
            "state": "SEESAW_AND_P_ONLY_AXION_DIAGNOSTICS_LANDED__GS_PHYSICAL_COSMOLOGY_OPEN",
            "evidence_landed": [
                "rank-capable type-I seesaw channel with a perturbative scale witness",
                "leading pure-P source term P^11/Lambda^8 and conditional P-only gcd(11,4)=1 arithmetic",
                "conditional P-only 36.705 GHz row and narrow quality/timing arithmetic interval",
            ],
            "open_requirements": [
                "actual dynamical GS axion/modulus, stabilization, and UV realization",
                "GS-inclusive discrete-gauge vacuum quotient and physical wall network/collapse",
                "radiative PQ generation and axion/axino/saxion/neutralino relic likelihood",
                "predicted neutrino mixing rather than an input mass witness",
            ],
        },
        "G6": {
            "state": "EXACT_GAUGE_ONLY_PLANCK_WINDOWS_LANDED__PHYSICAL_RGE_CHAIN_OPEN",
            "evidence_landed": [
                "exact PS one-loop b=(1,5,9) and gauge-only two-loop B matrix",
                "universal complete-family Delta b=(4,4,4)",
                "finite coupled gauge-only endpoints at 1e18 GeV and reduced Planck scale",
            ],
            "open_requirements": [
                "physical superpartner, PQ, and PS threshold matching",
                "coupled gauge-Yukawa-soft running and higher-loop uncertainty",
                "precision unification and scheme replay",
            ],
        },
        "G7": {
            "state": "PARAMETRIC_PROTON_SUPPRESSION_LANDED__PHYSICAL_LIFETIME_OPEN",
            "evidence_landed": [
                "exact residual matter parity forbids odd-matter RPV at every P/w0 spurion order",
                "odd RPV is exactly forbidden for all P/w0 dressings, while the leading allowed Q4/Qc4 coefficient is w0/Lambda^2 approximately 1e-31 GeV^-1",
            ],
            "open_requirements": [
                "complete pole spectrum and mass-basis baryon-violating Wilson matching",
                "operator running, dressing, hadronic inputs, and lifetime distributions",
            ],
        },
        "G8": {
            "state": "KINEMATIC_NEUTRINO_WITNESS_LANDED__GLOBAL_FLAVOUR_LIKELIHOOD_OPEN",
            "evidence_landed": [
                "a perturbative Dirac-Yukawa witness can reproduce the input neutrino mass scales",
            ],
            "open_requirements": [
                "charged-fermion, CKM, and PMNS fit with covariance",
                "joint proton, neutrino, axion, relic, collider, and cosmology likelihood",
                "versioned experimental, lattice, and cosmological input ledger",
            ],
        },
    }
    return [
        {
            "gate": gate,
            "qualified_id": f"research.susy_pati_salam.v24.{gate}.full_closure",
            "closed": False,
            "full_gate_claim": False,
            **rows[gate],
        }
        for gate in (f"G{index}" for index in range(1, 9))
    ]


def source_failure_report(
    manifest: list[dict[str, Any]], failures: list[str],
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "terminal.susy_pati_salam.v24.G1_G8.execution_verdict",
        "status": "V24_G1_G8_TERMINAL_LEDGER_SOURCE_FAILURE",
        "overall_state": "FAIL_CLOSED",
        "source_manifest": manifest,
        "upstream_core_pins": {
            name: definition["core_sha256"]
            for name, definition in UPSTREAMS.items()
        },
        "research_model": {
            "name": "PSZ4RZ11SUSYV24",
            "new_research_model_created": False,
            "runtime_attested": False,
        },
        "gates": [
            {
                "gate": f"G{index}",
                "closed": False,
                "full_gate_claim": False,
                "state": "SOURCE_FAILURE",
            }
            for index in range(1, 9)
        ],
        "closure_counts": {"closed": 0, "open": 8},
        "terminal_verdict": {
            "new_research_model_created": False,
            "complete_predictive_theory": False,
            "complete_G1_G8_solution_exists_in_this_repository": False,
            "safe_to_claim_a_new_fundamental_law": False,
        },
        "checks": {"all_pinned_sources_match": False},
        "n_checks": 1,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def build_report(root: Path = ROOT) -> dict[str, Any]:
    manifest = source_manifest(root)
    pin_failures = [
        f"source_pin:{row['path']}" for row in manifest if not row["matches"]
    ]
    if pin_failures:
        return source_failure_report(manifest, pin_failures)

    upstream = {
        name: load_json(root, definition["path"])
        for name, definition in UPSTREAMS.items()
    }
    v23 = upstream["v23_terminal_baseline"]
    architecture = upstream["v24_architecture"]
    source = upstream["v24_source"]
    vacuum = upstream["v24_vacuum_rg"]
    non_gs = upstream["v24_non_GS_completion_nogo"]
    model_text = (root / MODEL_PATH).read_text(encoding="utf-8")

    core_pin_ledger = {
        name: {
            "path": definition["path"],
            "expected_core_sha256": definition["core_sha256"],
            "observed_core_sha256": upstream[name].get("core_sha256"),
            "canonical_core_valid": json_core_valid(upstream[name]),
            "matches": (
                upstream[name].get("core_sha256") == definition["core_sha256"]
                and json_core_valid(upstream[name])
            ),
        }
        for name, definition in UPSTREAMS.items()
    }

    expected_metadata = all(
        upstream[name].get(key) == expected
        for name, definition in UPSTREAMS.items()
        for key, expected in definition["metadata"].items()
    )

    census = source["exhaustive_degree_le_3_gauge_invariant_selector_census"]
    declared = source["symmetry_complete_renormalizable_operator_ledger"]
    attestation = source["sarah_Start_attestation"]
    attestation_checks = attestation["checks"]
    source_rank = source["vacuum_and_generic_rank_ledger"]
    hessian = source_rank["generic_PS_breaking_sector_chiral_W_Hessian"]
    anomaly = source["discrete_anomaly_GS_ledger"]
    source_gates = source["gate_boundary"]
    vacuum_rank = vacuum["vacuum_and_mass_ranks"]
    running = vacuum["running_witness"]
    pheno = vacuum["phenomenology_frontier"]
    axion = pheno["selected_Z11_axion_candidate"]
    selected_z11 = vacuum["derived_Z11_rP2_GS_eligible_candidate"]
    gates = gate_ledger()

    runtime_summary = {
        "model": "PSZ4RZ11SUSYV24",
        "model_path": MODEL_PATH,
        "engine": attestation["engine"],
        "tool": attestation["tool"],
        "executed": attestation["executed"],
        "exit_code": attestation["exit_code"],
        "nonzero_component_superpotential": (
            attestation_checks["processed_component_superpotential_nonzero"]
        ),
        "processed_structural_term_count": (
            attestation["processed_superpotential_term_count"]
        ),
        "processed_field_structure_multiset_exact": (
            attestation_checks["processed_W_full_structural_multiset_exact"]
        ),
        "full_process_free_of_Dot_dotsh": (
            attestation_checks["full_process_log_free_of_Dot_dotsh"]
        ),
        "start_log_free_of_source_errors_and_Dot_dotsh": (
            attestation_checks["Start_log_free_of_model_source_errors_and_Dot_dotsh"]
        ),
        "all_required_checks_pass": attestation["all_required_checks_pass"],
        "claim_boundary": (
            "This is a genuine nonzero-W source/runtime attestation, not a pole-spectrum, "
            "soft-vacuum, or phenomenological likelihood calculation."
        ),
    }

    exact_landed = {
        "architecture": {
            "research_route": architecture["decision"]["selected_route"],
            "gauge_group": architecture["selected_architecture"]["gauge_group"],
            "shaping_symmetry": architecture["selected_architecture"]["shaping_symmetry"],
            "derived_not_published": True,
            "research_base_selected": architecture["decision"]["go_as_V24_research_base"],
            "complete_theory_selected": architecture["decision"]["go_as_complete_predictive_theory"],
        },
        "source_and_selector": {
            "gauge_invariant_degree_le_3_classes": len(census),
            "selector_allowed_classes": sum(
                row["allowed_in_superpotential"] for row in census
            ),
            "declared_structural_classes": len(declared),
            "processed_structural_classes": attestation["processed_superpotential_term_count"],
            "P_VEV_preserves_Z2_matter_parity": source["selector_contract"]["P_VEV_preserves_Z2_matter_parity"],
            "topological_equal_level_GS_counterterm_contract_landed": anomaly["topological_GS_counterterm_and_levels_landed"],
            "actual_dynamical_GS_modulus_stabilization_landed": anomaly["dynamical_GS_modulus_stabilization_landed"],
            "actual_discrete_GS_UV_realization_landed": anomaly["UV_realization_of_discrete_GS_landed"],
        },
        "rank_and_vacuum": {
            "PS_breaking_W_Hessian_dimension": hessian["matrix_dimension"],
            "PS_breaking_W_Hessian_rank": hessian["computed_exact_rank"],
            "PS_breaking_W_Hessian_nullity": hessian["computed_nullity"],
            "PS_to_SM_broken_generators": source_rank["PS_to_SM_broken_generators"],
            "F_terms_all_zero": all(
                value == 0 for value in vacuum_rank["F_terms"].values()
                if isinstance(value, (int, float))
            ),
            "D_terms_all_zero": vacuum_rank["D_terms"]["all_zero"],
            "global_SUSY_energy_over_vPS4": vacuum_rank["global_SUSY_energy_over_vPS4"],
            "full_soft_Kahler_hessian_closed": vacuum_rank["full_F_D_soft_Kahler_hessian_closed"],
        },
        "Higgs_and_mu": {
            "representation": "H=(1,2,2)",
            "low_energy_doublet_pairs_before_w0": source_rank["low_energy_Higgs_doublet_pairs_before_w0"],
            "supersymmetric_mass_at_X0": source_rank["H_bidoublet_supersymmetric_mass_at_X0"],
            "w0_H2_generates_soft_scale_mu": source_rank["w0_H2_generates_soft_scale_mu"],
            "radiative_EWSB_closed": False,
        },
        "axion_and_neutrino": {
            "leading_pure_P_superpotential_power": axion["harmonics"]["leading_superpotential_P_power"],
            "conditional_P_only_gcd": axion["harmonics"]["conditional_P_only_EFT_gcd"],
            "conditional_P_only_37GHz_frequency_GHz": axion["conditional_P_only_EFT_37GHz_benchmark"]["photon_frequency_GHz"],
            "P_only_interval_nonempty": axion["conditional_P_only_EFT_interval_GeV"]["nonempty_P_only_arithmetic"],
            "physical_GS_inclusive_wall_window_claim": axion["conditional_P_only_EFT_interval_GeV"]["physical_GS_inclusive_wall_window_claim"],
            "GS_inclusive_vacuum_lattice_computed": axion["harmonics"]["GS_inclusive_vacuum_lattice_computed"],
            "seesaw_MR_GeV": pheno["neutrino"]["MR_GeV"],
            "neutrino_scale_is_witness_not_prediction": True,
        },
        "gauge_running": {
            "PS_one_loop_b": vacuum["RG_above_PS"]["b"],
            "PS_two_loop_B": vacuum["RG_above_PS"]["B"],
            "complete_family_Delta_b": running["complete_vectorlike_Delta_b"],
            "selected_Z11_alpha_inverse_at_1e18_GeV": selected_z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_1e18GeV"],
            "selected_Z11_alpha_inverse_at_reduced_Planck": selected_z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_reduced_Planck"],
            "published_Z5_control_alpha_inverse_at_1e18_GeV": running["coupled_two_loop_gauge_only"]["alpha_inverse_at_cutoff"],
            "published_Z5_control_alpha_inverse_at_reduced_Planck": running["coupled_two_loop_gauge_only_reduced_Planck"]["alpha_inverse_at_reduced_Planck"],
            "scope": running["scope"],
        },
        "proton_and_flavour": {
            "selected_Z11_leading_Q4_coefficient_GeV_inverse": source["exhaustive_leading_PQ_breaking_and_proton_ledger"]["proton_decay"]["coefficient_estimate_GeV_inverse"],
            "selected_Z11_leading_Q4_dressing": source["exhaustive_leading_PQ_breaking_and_proton_ledger"]["proton_decay"]["leading_W_dressing"],
            "selected_Z11_odd_RPV_forbidden_all_spurion_orders": source["checks"]["matter_parity_and_RPV_are_exact_to_all_spurion_orders"],
            "published_Z5_control_dimension4_baryon_coefficient_order": pheno["proton_and_relic_boundaries"]["source_dimension4_baryon_coefficient_order"],
            "published_Z5_control_minimal_RPV_lambdaL_order": pheno["proton_and_relic_boundaries"]["source_minimal_RPV_lambdaL_order"],
            "physical_Wilson_matching_and_pole_lifetime_landed": pheno["proton_and_relic_boundaries"]["physical_Wilson_matching_and_pole_lifetime_landed"],
            "flavour_and_cosmology_are_predictions": False,
        },
        "minimal_non_GS_completion_scan": {
            "scope": non_gs["scope"],
            "P_mass_weighted_index_congruence": non_gs["exact_P_mass_congruence"]["combined_congruence"],
            "minimum_positive_weighted_index": non_gs["exact_P_mass_congruence"]["minimum_positive_K_each_PS_factor"],
            "one_loop_necessary_perturbativity_condition_pass": non_gs["P_mass_threshold_no_go"]["one_loop_necessary_perturbativity_condition_pass"],
            "projected_SU2R_inverse_after_minimal_completion": non_gs["P_mass_threshold_no_go"]["projected_one_loop_SU2R_inverse_after_minimal_completion"],
            "absolute_N_DW_after_P_mass_completion": non_gs["PQ_domain_wall_obstruction"]["absolute_N_DW_after_completion"],
            "gcd_P11_and_completed_NDW": non_gs["PQ_domain_wall_obstruction"]["gcd_explicit_harmonic_and_NDW"],
            "P11_lifts_all_completed_QCD_vacua": non_gs["PQ_domain_wall_obstruction"]["P11_lifts_all_QCD_vacua"],
            "zero_PQ_spurion_scan_scope": non_gs["zero_PQ_spurion_scan"]["scope"],
            "zero_PQ_spurion_scan_has_quality_RG_overlap": not non_gs["zero_PQ_spurion_scan"]["all_rows_have_no_overlap"],
            "minimal_non_GS_completion_viable_in_scanned_scope": non_gs["verdict"]["minimal_non_GS_completion_viable"],
            "Green_Schwarz_dependency_eliminated": non_gs["verdict"]["Green_Schwarz_dependency_eliminated"],
            "scope_boundary": (
                "This is an exact no-go for the stated minimal weakly-coupled P-mass "
                "and finite zero-PQ-spurion classes, not for every possible UV completion."
            ),
        },
    }

    hard_boundaries = {
        "actual_GS_axion_modulus_stabilization_and_UV_realization": "ABSENT",
        "topological_GS_counterterm_contract": "LANDED_BUT_NOT_A_DYNAMICAL_UV_COMPLETION",
        "P_only_gcd_and_numerical_window": "CONDITIONAL_ARITHMETIC_NOT_A_PHYSICAL_WALL_PROOF",
        "vacuum": "GLOBAL_SUSY_ZERO_BRANCH_ONLY__FULL_SOFT_KAHLER_COMPETING_BRANCH_PROOF_ABSENT",
        "RGE": "GAUGE_ONLY_SCREEN__PHYSICAL_GAUGE_YUKAWA_SOFT_THRESHOLDS_ABSENT",
        "proton": "PARAMETRIC_SOURCE_SUPPRESSION__POLE_LIFETIME_ABSENT",
        "flavour": "MASS_SCALE_WITNESS__GLOBAL_LIKELIHOOD_ABSENT",
        "minimal_non_GS_completion_scan": (
            "P_MASS_CLASS_FAILS_RG_AND_ALIGNS_P11_WITH_NDW11__FINITE_ZERO_PQ_"
            "SPURION_CLASS_HAS_NO_QUALITY_RG_OVERLAP__GS_OR_NEW_SHAPING_REQUIRED"
        ),
    }

    model_markers_exact = all(marker in model_text for marker in (
        'Model`Name = "PSZ4RZ11SUSYV24";',
        "Global[[1]] = {Z[11], Z11Selector};",
        "SuperPotential = (-kappaPS*vPS2*X",
        "NameOfStates = {GaugeES};",
    )) and "SuperPotential = 0;" not in model_text

    checks = {
        "all_pinned_sources_match": all(row["matches"] for row in manifest),
        "all_upstream_canonical_cores_are_valid_and_pinned": all(
            row["matches"] for row in core_pin_ledger.values()
        ),
        "all_upstream_schema_namespace_status_metadata_match": expected_metadata,
        "V23_baseline_is_preserved_at_zero_of_eight_full_gates": (
            v23["closure_counts"] == {"closed": 0, "open": 8}
            and v23["terminal_verdict"]["complete_G1_G8_solution_exists_in_this_repository"] is False
        ),
        "V24_architecture_is_selected_only_as_a_research_base": (
            architecture["decision"]["go_as_V24_research_base"] is True
            and architecture["decision"]["go_as_complete_predictive_theory"] is False
            and architecture["source_and_claim_boundary"]["a_complete_G1_G8_theory_is_claimed"] is False
            and architecture["source_and_claim_boundary"]["PSZ4RZ11_is_described_as_published"] is False
        ),
        "model_file_is_nonzero_W_PSZ4RZ11_source": model_markers_exact,
        "renormalizable_selector_census_is_exactly_18_of_80": (
            len(census) == 80
            and sum(row["allowed_in_superpotential"] for row in census) == 18
            and len(declared) == 18
            and source["checks"]["declared_W_equals_exhaustive_allowed_census"] is True
        ),
        "live_SARAH_processed_nonzero_W_and_exact_18_term_multiset": (
            attestation["executed"] is True
            and attestation["exit_code"] == 0
            and attestation["all_required_checks_pass"] is True
            and attestation["processed_superpotential_term_count"] == 18
            and attestation_checks["processed_component_superpotential_nonzero"] is True
            and attestation_checks["processed_W_exactly_18_terms"] is True
            and attestation_checks["processed_W_full_structural_multiset_exact"] is True
        ),
        "live_SARAH_process_is_free_of_Dot_dotsh_and_source_errors": (
            attestation_checks["Start_log_free_of_model_source_errors_and_Dot_dotsh"] is True
            and attestation_checks["full_process_log_free_of_Dot_dotsh"] is True
        ),
        "source_G1_G2_claims_are_explicitly_partial": (
            source_gates["G1"]["state"] == "PARTIAL"
            and source_gates["G2"]["state"] == "PARTIAL"
            and source_gates["full_G1_or_G2_claim"] is False
        ),
        "exact_PS_breaking_source_Hessian_rank_is_14_of_23_with_nine_Goldstones": (
            hessian["matrix_dimension"] == [23, 23]
            and hessian["computed_exact_rank"] == 14
            and hessian["computed_nullity"] == 9
            and source_rank["PS_to_SM_broken_generators"] == 9
            and source_rank["breaking_sector_physical_chiral_nullity_after_super_Higgs"] == 0
        ),
        "zero_energy_global_SUSY_F_D_branch_is_not_promoted_to_full_vacuum": (
            exact_landed["rank_and_vacuum"]["F_terms_all_zero"] is True
            and vacuum_rank["D_terms"]["all_zero"] is True
            and vacuum_rank["global_SUSY_energy_over_vPS4"] == 0
            and vacuum_rank["full_F_D_soft_Kahler_hessian_closed"] is False
        ),
        "H_representation_and_mu_protection_are_scoped": (
            source_rank["low_energy_Higgs_doublet_pairs_before_w0"] == 1
            and source_rank["H_bidoublet_supersymmetric_mass_at_X0"] == 0
            and source_rank["w0_H2_generates_soft_scale_mu"] is True
            and source["selector_contract"]["P_VEV_preserves_Z2_matter_parity"] is True
        ),
        "GS_topological_contract_does_not_overclaim_dynamical_UV_completion": (
            anomaly["topological_GS_counterterm_and_levels_landed"] is True
            and anomaly["equal_level_GS_universality_demonstrated"] is True
            and anomaly["dynamical_GS_modulus_stabilization_landed"] is False
            and anomaly["UV_realization_of_discrete_GS_landed"] is False
            and source["checks"]["GS_modulus_and_UV_are_not_overclaimed"] is True
        ),
        "P_only_gcd_window_is_not_promoted_to_physical_wall_solution": (
            axion["harmonics"]["conditional_P_only_EFT_gcd"] == 1
            and axion["harmonics"]["GS_inclusive_vacuum_lattice_computed"] is False
            and axion["harmonics"]["GS_inclusive_wall_collapse_demonstrated"] is False
            and axion["conditional_P_only_EFT_interval_GeV"]["nonempty_P_only_arithmetic"] is True
            and axion["conditional_P_only_EFT_interval_GeV"]["physical_GS_inclusive_wall_window_claim"] is False
            and axion["promotion_boundary"]["actual_domain_wall_solution"] is False
        ),
        "seesaw_witness_is_perturbative_but_not_a_flavour_prediction": (
            pheno["neutrino"]["perturbative_scale_witness"] is True
            and "inputs, not predictions" in pheno["neutrino"]["interpretation"]
        ),
        "gauge_only_Planck_endpoints_are_finite_but_not_physical_RGE_closure": (
            vacuum["RG_above_PS"]["b"] == [1, 5, 9]
            and vacuum["RG_above_PS"]["B"] == [[108, 15, 21], [75, 53, 3], [105, 3, 81]]
            and running["complete_vectorlike_Delta_b"] == [4, 4, 4]
            and running["coupled_two_loop_gauge_only"]["finite_to_cutoff"] is True
            and running["coupled_two_loop_gauge_only_reduced_Planck"]["finite_to_reduced_Planck"] is True
            and selected_z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_1e18GeV"] == [15.760581115599363, 12.87767203164891, 9.686379301220363]
            and selected_z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_reduced_Planck"] == [15.501027745017138, 12.06369301733598, 8.231081080183568]
            and "gauge-only" in running["scope"]
        ),
        "proton_result_is_parametric_not_a_pole_lifetime": (
            source["checks"]["matter_parity_and_RPV_are_exact_to_all_spurion_orders"] is True
            and source["exhaustive_leading_PQ_breaking_and_proton_ledger"]["proton_decay"]["coefficient_estimate_GeV_inverse"] == 1e-31
            and "w0*(Q^4 or Qc^4)/Lambda^2" == source["exhaustive_leading_PQ_breaking_and_proton_ledger"]["proton_decay"]["leading_W_dressing"]
            and pheno["proton_and_relic_boundaries"]["physical_Wilson_matching_and_pole_lifetime_landed"] is False
        ),
        "flavour_and_joint_likelihood_remain_open": (
            vacuum["G1_G8"][7]["gate"] == "G8"
            and vacuum["G1_G8"][7]["closed"] is False
            and "inputs, not predictions" in pheno["neutrino"]["interpretation"]
            and pheno["proton_and_relic_boundaries"]["axino_saxion_neutralino_relic_likelihood_landed"] is False
        ),
        "minimal_non_GS_P_mass_completion_has_K7_RG_and_NDW11_obstructions": (
            non_gs["exact_P_mass_congruence"]["combined_congruence"] == "K_G=7 (mod 22)"
            and non_gs["exact_P_mass_congruence"]["minimum_positive_K_each_PS_factor"] == 7
            and non_gs["P_mass_threshold_no_go"]["one_loop_necessary_perturbativity_condition_pass"] is False
            and non_gs["P_mass_threshold_no_go"]["projected_one_loop_SU2R_inverse_after_minimal_completion"] < 0
            and non_gs["PQ_domain_wall_obstruction"]["absolute_N_DW_after_completion"] == 11
            and non_gs["PQ_domain_wall_obstruction"]["gcd_explicit_harmonic_and_NDW"] == 11
            and non_gs["PQ_domain_wall_obstruction"]["P11_lifts_all_QCD_vacua"] is False
        ),
        "finite_zero_PQ_spurion_scan_has_no_quality_RG_overlap": (
            non_gs["zero_PQ_spurion_scan"]["all_rows_have_no_overlap"] is True
            and "rS=0 includes its required existing-P k=1 real-10 repair" in non_gs["zero_PQ_spurion_scan"]["scope"]
            and non_gs["checks"]["zero_PQ_spurion_mixed_anomaly_congruences_include_R_repair"] is True
            and non_gs["verdict"]["minimal_non_GS_completion_viable"] is False
            and non_gs["verdict"]["Green_Schwarz_dependency_eliminated"] is False
            and non_gs["closure_counts"] == {"closed": 0, "open": 8}
        ),
        "all_eight_full_G1_G8_gates_are_false_and_open": (
            len(gates) == 8
            and [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
            and all(
                row["closed"] is False and row["full_gate_claim"] is False
                for row in gates
            )
            and vacuum["closure_counts"] == {"closed": 0, "open": 8}
        ),
    }
    failures = [name for name, passed in checks.items() if passed is not True]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "terminal.susy_pati_salam.v24.G1_G8.execution_verdict",
        "status": (
            "V24_G1_G8_EXECUTION_COMPLETE__NEW_EXECUTABLE_RESEARCH_MODEL_"
            "LANDED__NO_COMPLETE_PREDICTIVE_THEORY__ZERO_OF_EIGHT_FULL_GATES"
            if not failures else "V24_G1_G8_TERMINAL_LEDGER_AUDIT_FAILED"
        ),
        "overall_state": (
            "NEW_RESEARCH_MODEL_AT_FAIL_CLOSED_PREDICTIVE_FRONTIER"
            if not failures else "FAIL_CLOSED_EXECUTION_ERROR"
        ),
        "campaign_scope": (
            "Frozen V23 terminal baseline plus V24 architecture, executable source, "
            "exact source-rank, global-SUSY vacuum, gauge-only running, and scoped "
            "axion/neutrino/proton diagnostics"
        ),
        "source_manifest": manifest,
        "upstream_core_pins": core_pin_ledger,
        "research_model": {
            "name": "PSZ4RZ11SUSYV24",
            "short_name": "PSZ4RZ11",
            "gauge_group": "SU(4)C x SU(2)L x SU(2)R",
            "selector": "Z4R x Z11",
            "provenance": (
                "Derived V24 selector/source on the published Kawamura--Raby "
                "Pati--Salam scaffold; PSZ4RZ11 itself is not a published model."
            ),
            "new_research_model_created": not failures,
            "runtime_attested": not failures,
            "complete_predictive_theory": False,
        },
        "runtime_attestation": runtime_summary,
        "exact_landed_results": exact_landed,
        "hard_claim_boundaries": hard_boundaries,
        "gates": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "terminal_verdict": {
            "new_research_model_created": not failures,
            "complete_predictive_theory": False,
            "complete_G1_G8_solution_exists_in_this_repository": False,
            "safe_to_claim_a_new_fundamental_law": False,
            "reproducible_research_progress_created": not failures,
            "all_full_G1_G8_gates_closed": False,
            "reason": (
                "V24 materially advances the project with an executable nonzero-W "
                "Pati--Salam source, an exact 18/80 selector census, rank 14/23 source "
                "Hessian, an F=D=0 branch, protected Higgs representation, and finite "
                "gauge-only Planck screens. It is not a complete predictive theory: the "
                "dynamical GS sector and UV realization, full soft/Kahler vacuum and pole "
                "spectrum, physical thresholds/RGEs, GS-inclusive wall physics, proton "
                "lifetime, flavour fit, and joint likelihood remain absent. The tested "
                "minimal non-GS alternatives also fail: natural P-generated masses force "
                "K=7 mod 22, exceed the one-loop RG budget, and shift NDW to 11 so P11 "
                "aligns; the finite zero-PQ-spurion scan has no quality/RG overlap."
            ),
            "stop_complete_theory_claim": True,
            "continue_as_research_model": True,
        },
        "next_research_promotion_requirements": [
            "construct and stabilize the dynamical GS axion/modulus and its UV/hidden sector while preserving residual matter parity, or replace the selector with independently anomaly-complete shaping physics",
            "solve the full F+D+soft+Kahler/PQ vacuum and gauge-fixed component/pole spectrum",
            "perform physical threshold matching and coupled gauge-Yukawa-soft running",
            "compute the GS-inclusive vacuum lattice, wall network/collapse, and relic history",
            "calculate proton Wilson coefficients/lifetimes and fit charged flavour, CKM, PMNS, axion, neutrino, collider, and cosmology data",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    if report["overall_state"] == "FAIL_CLOSED":
        return "\n".join([
            "# SUSY V24 G1--G8 execution verdict", "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            "- Result: fail-closed because pinned source artifacts are missing or changed.",
            "- Full gates closed: `0/8`.", "",
        ])

    runtime = report["runtime_attestation"]
    landed = report["exact_landed_results"]
    running = landed["gauge_running"]
    return "\n".join([
        "# SUSY V24 G1--G8 execution verdict", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- New executable research model: **yes -- `PSZ4RZ11SUSYV24`**.",
        "- Complete predictive theory: **no**.",
        "- Full G1--G8 gates closed: **0/8**.", "",
        "## What is genuinely new", "",
        f"The derived `Z4R x Z11` Pati--Salam source has a nonzero superpotential and a real `{runtime['tool']}` initialization/process attestation. The exact degree-<=3 gauge census contains `80` structural classes, `18` are selector allowed, and the `18` processed field structures match exactly. The component superpotential has `18` couplings and the required representative coupling families. The full process is free of `Dot::dotsh` and the validator's source-error classes.", "",
        "The source-exact PS-breaking superpotential Hessian has rank `14/23`; its nullity `9` equals the nine PS/SM Goldstone directions. An equal-conjugate-VEV branch makes every F and D term zero, hence has zero global-SUSY energy. `H=(1,2,2)` leaves one doublet pair without a colored partner, its SUSY mass vanishes at `X=0`, and `w0 H^2` can generate soft-scale mu.", "",
        "The exact gauge ledgers give `b=(1,5,9)` and `B=((108,15,21),(75,53,3),(105,3,81))`. The gauge-only inverse-coupling endpoint is "
        f"`{running['selected_Z11_alpha_inverse_at_1e18_GeV']}` at `1e18 GeV` and `{running['selected_Z11_alpha_inverse_at_reduced_Planck']}` at reduced Planck scale. These are the selected-Z11 perturbativity screens, not precision physical RG closure; the separately recorded lower endpoints are explicitly the published-Z5 control.", "",
        "## Hard boundary", "",
        "The equal-level topological GS counterterm is a source contract only. An actual dynamical GS axion/modulus, its stabilization and UV/hidden-sector realization are absent. Consequently `gcd(11,4)=1`, the `P^11` quality estimate, the narrow P-only interval, and the `36.705 GHz` row are conditional arithmetic -- not a GS-inclusive physical wall-vacuum or collapse proof.", "",
        "The seesaw result is a viable perturbative mass-scale witness, not a flavour prediction. Proton safety is parametric at source level, not a Wilson-matched pole lifetime. The complete soft/Kahler vacuum, pole spectrum, thresholds, coupled gauge-Yukawa-soft RGEs, wall/relic history, charged flavour/PMNS fit, and joint likelihood remain open.", "",
        "A separate exact certificate tests the stated minimal non-GS alternatives. Natural P-generated spectator masses require `K=7 mod 22`; the minimum `K=7` threshold exhausts the one-loop SU(2)R budget and changes `|N_DW|` to `11`, aligning the explicit `P^11` harmonic instead of lifting all vacua. The finite zero-PQ-spurion charge scan has no axion-quality/RG overlap. This establishes that GS or materially new shaping physics is still required within the scanned scope; it is not a no-go for every conceivable UV completion.", "",
        "Therefore V24 is a concrete and reproducible new research model, but it is not a completed G1--G8 solution or a new established fundamental law.", "",
    ])


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write frozen JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="fail if frozen outputs have drifted")
    args = parser.parse_args()

    report = build_report()
    if report["n_failed"]:
        print(report["status"])
        print(report["core_sha256"])
        print(json.dumps(report["failures"], sort_keys=True))
        return 1
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            raise FileNotFoundError("frozen V24 terminal verdict outputs are missing")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V24 terminal verdict JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V24 terminal verdict Markdown drifted")

    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
