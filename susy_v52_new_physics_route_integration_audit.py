#!/usr/bin/env python3
"""Integrate and rank the V52 new-physics routes without cross-action promotion.

V52 contains several exact but deliberately scoped advances: a locally isolated
low-index Spin(10) source, a nonlinear two-site alignment action, and a minimal
renormalizable seesaw/selector/DT repair module.  This audit compares those
results with literature-backed flipped and missing-VEV alternatives, selects the
strongest elementary foundation, and keeps every gate fail-closed until one
complete action is constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V52_NEW_PHYSICS_ROUTE_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V52_NEW_PHYSICS_ROUTE_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v52_new_physics_route_integration_audit.py"

INPUTS = {
    "v51_master": ROOT / "SUSY_V51_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.json",
    "low_index_source": ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.json",
    "lean_alignment": ROOT / "SUSY_V52_LEAN_NONLINEAR_ALIGNMENT_AUDIT.json",
    "low_index_hybrid": ROOT / "SUSY_V52_LOW_INDEX_HYBRID_ALIGNMENT_AUDIT.json",
    "minimal_repair": ROOT / "SUSY_V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT.json",
}

STATUS = (
    "V52_NEW_PHYSICS_ROUTE_SELECTION__EXACT_LOW_INDEX_54_45_16_BAR16_SOURCE_"
    "SELECTED_FOR_NEXT_BUILD__EXACT_RECOMPUTED_TWO_SITE_HYBRID_LIFTS_ALL24_"
    "RELATIVE_CHIRALS_AND_HAS_FULL176_HESSIAN_KERNEL_EQUAL_GAUGE_ORBIT__"
    "HYBRID_IS_EFT_ONLY__V51_NEAR_THRESHOLD_LANDAU_KILL_EVADED__EXACT_"
    "RANK3_DOUBLE_SEESAW_AND_EXTERNAL_Z2_WITNESS__DT_WITNESS_IS_TUNED__"
    "UV_SELECTOR_NATURAL_DT_FLAVOUR_MATCHING_AND_GLOBAL_VACUUM_OPEN__"
    "NO_G2_OR_FULL_GATE_PROMOTION"
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


def load_hashed_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"input is not an object: {path.name}")
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"stale canonical core: {path.name}")
    return value


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def flipped_route(g: float) -> dict[str, Any]:
    b10 = 1.0
    bx = 67.0 / 24.0
    family_anomalies = {
        "gravity_squared_U1X": 16 * 1 + 10 * (-2) + 1 * 4,
        "U1X_cubed": 16 * 1**3 + 10 * (-2) ** 3 + 1 * 4**3,
        "Spin10_squared_U1X": 2 * 1 + 1 * (-2),
    }
    return {
        "id": "R3_flipped_Spin10xU1X",
        "rank": 3,
        "evidence_level": "primary-literature-backed; no repository full-chiral-Hessian certificate",
        "field_content": "45_0 + 2(16_+1 + bar16_-1), with 3(16_+1+10_-2+1_+4)",
        "renormalizable_Higgs_superpotential": (
            "W=(mu/2)Tr(45^2)+rho_ij bar16_i 16_j+"
            "tau_ij bar16_i 45 16_j"
        ),
        "generic_little_group": "SM for two non-aligned spinor pairs",
        "Higgs_coordinates": 45 + 4 * 16,
        "gauge_dimension": 46,
        "broken_generators": 46 - 12,
        "required_full_Hessian_rank_before_DT_selection": 109 - 34,
        "family_anomaly_sums": family_anomalies,
        "published_one_loop_coefficients": {"b10": b10, "bXhat": bx},
        "Landau_pole_over_matching_scale_at_g0p73": {
            "Spin10": math.exp(8 * math.pi**2 / (b10 * g**2)),
            "U1Xhat": math.exp(8 * math.pi**2 / (bx * g**2)),
        },
        "strength": "best perturbative margin and no link/A5 sector",
        "fatal_open_items": [
            "full 109-coordinate chiral Hessian and Goldstone equality",
            "natural doublet-triplet splitting (the minimal setup resorts to tuning)",
            "an anomaly-safe discrete matter selector through dimension five",
            "Planck-suppressed down/lepton/neutrino flavour completion",
            "global gauge quotient, E6 threshold spectrum and proton decay",
        ],
        "decision": "credible alternative; not selected over the executable exact R1 witness",
    }


def missing_vev_route(g: float) -> dict[str, Any]:
    ratios = {
        str(b): math.exp(8 * math.pi**2 / (b * g**2)) for b in (23, 24)
    }
    return {
        "id": "R5_extended_missing_VEV_DT",
        "rank": 5,
        "evidence_level": "primary-literature repair direction; not integrated into V52 Hessian",
        "field_content": "54 + 2(45) + 3(16+bar16) + 1 or 2(10) + singlets",
        "advance": "explicit renormalizable doublet and triplet mass matrices with one light MSSM pair",
        "one_loop_b_range": [23, 24],
        "Landau_pole_over_matching_scale_at_g0p73": ratios,
        "decision": (
            "passes a 100x perturbative-window screen but fails a 1000x screen; "
            "requires a new whole-action Hessian, selector, flavour and proton audit"
        ),
    }


def updated_gate_ledger(
    v51: Mapping[str, Any],
    low: Mapping[str, Any],
    hybrid: Mapping[str, Any],
    repair: Mapping[str, Any],
) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v51["gate_ledger"])
    pole = low["perturbativity"]["landau_pole_over_matching_scale_if_b_positive"]
    for row in ledger:
        if row["gate"] == "G1":
            row["advance"] = (
                "Frozen V47 ordinary-Spin quotient/anomaly results remain a reusable lemma; "
                "this is not a same-action V52 reclosure."
            )
            row["blocker"] = (
                "For an independently gauged V50-style U(1)F, the R1 spinor pair leaves an "
                "extra diagonal U(1) unless another charged sector is added; the complete "
                "V52 selector/UV quotient is not frozen."
            )
        elif row["gate"] == "G2":
            row["advance"] = (
                "V52 proves an exact low-index source vacuum/Hessian and a separately frozen, "
                "fully recomputed two-site hybrid whose rank-24 alignment lifts every relative "
                "chiral and whose 176-coordinate Hessian kernel equals its gauge orbit."
            )
            row["blocker"] = (
                "The hybrid link is a nonlinear sigma-model EFT without an elementary UV "
                "completion; neither V52 action is matched to frozen V50, and no complete "
                "C1-C7 Wilson action exists."
            )
        elif row["gate"] == "G3":
            row["advance"] = (
                "The complete 131-coordinate GUT-breaking source has F=D=0, rank(Q)=33, "
                "rank(H)=98, HQ=0 and ker(H)=im(Q) at one exact rational witness."
            )
            row["blocker"] = (
                "The electroweak/DT, SUSY-breaking and soft sectors, tunnelling/global vacuum "
                "selection and the whole-action scalar Hessian are absent."
            )
        elif row["gate"] == "G4":
            row["advance"] = (
                "The minimal R1 repair has an exact renormalizable 10H tree matrix with "
                "triplet rank 6 and weak nullity 4, i.e. one Hu,Hd pair."
            )
            row["blocker"] = (
                "The result requires the codimension-one tuning mH=3*kH; no symmetry enforces "
                "it, and mu/Bmu, SUSY breaking, radiative EWSB and the full scalar vacuum are absent."
            )
        elif row["gate"] == "G5":
            row["advance"] = (
                "V52 introduces no dark/PQ claim; the four seesaw singlets have zero scalar VEV "
                "at the displayed witness and are not silently counted as a relic solution."
            )
            row["blocker"] = (
                "No dark-sector or PQ Lagrangian, reheating history, relic calculation, BBN/CMB "
                "test or cosmological likelihood is specified."
            )
        elif row["gate"] == "G6":
            row["advance"] = (
                f"The selected single-site source has sum T=24; with three families and one "
                f"10H, b=7 and the one-loop pole ratio at g=0.73 is {pole:.6g}."
            )
            row["blocker"] = (
                "The hybrid's 627.6 pole ratio is only a nonlinear-tangent proxy above its NDA "
                "cutoff; a frozen elementary spectrum, two-loop running, one-loop thresholds, "
                "unification and proton-decay amplitudes have not been computed."
            )
        elif row["gate"] == "G7":
            row["advance"] = (
                "V52 identifies a source action with a controlled local quotient on which a new "
                "operator/Wilson calculation can be based."
            )
            row["blocker"] = (
                "V51 factor tensors cannot be inherited across the action change; the V52 "
                "invariant census, mediator matching, running and B/L rates are absent."
            )
        elif row["gate"] == "G8":
            row["advance"] = (
                "The minimal extension gives an exact renormalizable 10x10 double-seesaw witness: "
                "heavy rank 7, full rank 10, induced-RH rank 3 and light-neutrino rank 3. An "
                "external Z2 survives all declared VEVs and passes the displayed mod-2 ledgers."
            )
            row["blocker"] = (
                "The Z2 has no continuous-parent/full UV discrete-gauge construction; the complete "
                "operator census, charged-family fit, uncertainty propagation and withheld prediction "
                "are absent."
            )
    return ledger


def candidate_clause_ledger() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "status": "source_subsector_pass_only",
            "statement": "The most general declared renormalizable 54+45+16+bar16 source is explicit; the full matter/DT/portal action census is not.",
        },
        {
            "id": "C2",
            "status": "new_action_locality_only",
            "statement": "The selected source is an ordinary local 4D action, but it is not the frozen V50 boundary regulator/action.",
        },
        {
            "id": "C3",
            "status": "source_subsector_exact",
            "statement": "The source variational domain, gauge orbit, Ward identity and physical Hessian kernel are exact.",
        },
        {
            "id": "C4",
            "status": "source_subsector_exact",
            "statement": "With canonical source Kahler metric, H-dagger-H is positive on all 98 physical source directions; the whole-theory metric is absent.",
        },
        {
            "id": "C5",
            "status": "open",
            "statement": "No V52 one-loop matching, counterterm map or matching-scale cancellation has been computed.",
        },
        {
            "id": "C6",
            "status": "partial_selector_ledger",
            "statement": "An external Z2 survives the declared VEVs and passes the displayed mod-2 ledgers, but its UV embedding, complete operator census and natural DT protection are absent.",
        },
        {
            "id": "C7",
            "status": "open",
            "statement": "No V52 component Clebsch basis or contracted physical Wilson array exists.",
        },
    ]


def build_report() -> dict[str, Any]:
    loaded = {name: load_hashed_json(path) for name, path in INPUTS.items()}
    v51 = loaded["v51_master"]
    low = loaded["low_index_source"]
    lean = loaded["lean_alignment"]
    hybrid = loaded["low_index_hybrid"]
    repair = loaded["minimal_repair"]
    geometry = low["exact_local_geometry"]
    running = low["perturbativity"]
    incidence = lean["PS_SU5_projector_incidence"]
    alignment = lean["alignment_and_spectrum"]["full_two_site_Rxi_and_alignment"]
    lean_running = lean["field_and_perturbativity_stress_test"]
    g = float(running["g_at_matching_witness"])
    b_max_100 = 8 * math.pi**2 / (g**2 * math.log(100.0))
    b_max_1000 = 8 * math.pi**2 / (g**2 * math.log(1000.0))
    hybrid_partition = hybrid["endpoint_partition"]["dimensions"]
    hybrid_exact = hybrid["exact_alignment_and_full_Hessian"]
    hybrid_rxi = hybrid_exact["adapted_Rxi_count"]
    hybrid_full = hybrid_exact["full_holomorphic_system"]
    hybrid_running = hybrid["field_and_perturbativity_proxy"]
    repair_seesaw = repair["renormalizable_double_seesaw"]
    repair_selector = repair["surviving_selector"]
    repair_dt = repair["doublet_triplet"]
    repair_running = repair["perturbativity"]
    gates = updated_gate_ledger(v51, low, hybrid, repair)
    clauses = candidate_clause_ledger()

    routes = [
        {
            "id": "R1_exact_conventional_low_index",
            "rank": 1,
            "evidence_level": "repository-executable exact certificate",
            "field_content": low["candidate"]["representations"],
            "coordinates": low["candidate"]["complex_coordinates"],
            "exact_results": {
                "F_and_D_flat": (
                    low["exact_witness"]["F_terms_all_zero"]
                    and low["exact_witness"]["D_terms_all_zero"]
                ),
                "orbit_rank": geometry["orbit_rank_mod37"],
                "Hessian_rank": geometry["hessian_rank_mod37"],
                "Hessian_nullity": geometry["hessian_nullity_mod37"],
                "HQ_zero": geometry["ward_product_exactly_zero"],
                "kernel_equals_gauge_orbit": geometry["kernel_equals_broken_gauge_orbit"],
            },
            "scope": (
                "The 131-coordinate certificate covers the Spin(10) GUT-breaking source only; "
                "its 12-dimensional stabilizer is SM inside Spin(10). It does not include an "
                "independently gauged U(1)F or the phenomenological repair fields."
            ),
            "minimal_renormalizable_repair": {
                "added_fields": "one H10 plus four Spin(10) singlets N",
                "double_seesaw_ranks": repair_seesaw["ranks"],
                "external_Z2_survives_declared_VEVs": repair_selector[
                    "all_nonzero_VEV_fields_even"
                ],
                "external_Z2_scope": repair_selector["scope_caveat"],
                "DT_triplet_rank": repair_dt["color_triplet_coordinate_block"]["rank"],
                "DT_weak_nullity": repair_dt["weak_doublet_coordinate_block"]["nullity"],
                "DT_condition_codimension": repair_dt["condition_codimension"],
                "natural_DT": repair_dt["natural_missing_partner_or_DW"],
            },
            "running": {
                "source_sum_T": running["source_sum_T"],
                "b_with_three_families_and_10H": running[
                    "one_loop_b_with_three_16_families_and_one_10H"
                ],
                "pole_ratio": running["landau_pole_over_matching_scale_if_b_positive"],
            },
            "strength": (
                "strongest elementary renormalizable single-site foundation; it evades the "
                "V51 link-sector obstruction by deleting that sector rather than repairing it"
            ),
            "fatal_open_items": [
                "the exact rank-98 Hessian covers only the 131-coordinate GUT-breaking source, not the repair or whole phenomenological action",
                low["anomaly_ledger"]["integration_caveat"],
                "the external Z2 has no continuous-parent/full UV discrete-gauge construction and does not by itself forbid even-matter dimension-five classes such as 16F^4",
                "the displayed DT rank witness requires an unprotected codimension-one coefficient relation",
                "the complete invariant/operator census, thresholds, flavour fit and proton-decay calculation are absent",
            ],
            "decision": "selected as the V52 foundation for the next complete-action build",
        },
        {
            "id": "R2_low_index_two_site_hybrid",
            "rank": 2,
            "evidence_level": "repository-executable full coupled-Hessian EFT certificate",
            "field_content": "45-dimensional group-valued link chart + exact 131-coordinate R1 source",
            "coordinates": hybrid_full["coordinates"],
            "exact_results": {
                "endpoint_partition": hybrid_partition,
                "alignment_rank": hybrid_rxi["A_rank"],
                "gauge_rank": hybrid_rxi["D_rank"],
                "combined_Goldstone_rank": hybrid_rxi["combined_Goldstone_rank"],
                "combined_Goldstone_nullity": hybrid_rxi["combined_Goldstone_nullity"],
                "alignment_orthogonal_to_gauge": hybrid_rxi["A_D_exact_zero"],
                "Q_rank": hybrid_full["Q_rank_mod37"],
                "Hessian_rank": hybrid_full["H_rank_mod37"],
                "Hessian_nullity": hybrid_full["H_nullity_mod37"],
                "HQ_zero": hybrid_full["HQ_exact_zero"],
                "kernel_equals_gauge_orbit": hybrid_full[
                    "kernel_equals_broken_gauge_orbit"
                ],
            },
            "running_proxy": {
                "NDA_cutoff_over_vector_mass": hybrid_running[
                    "nonlinear_sigma_NDA_cutoff_over_vector_mass"
                ],
                "colocated_visible_sum_T": hybrid_running[
                    "including_colocated_visible_families_and_10H"
                ]["sum_T"],
                "b_AF_3C2_minus_sumT": hybrid_running[
                    "including_colocated_visible_families_and_10H"
                ]["b_asymptotic_freedom__3C2_minus_sumT"],
                "b_Landau_sumT_minus_3C2": hybrid_running[
                    "including_colocated_visible_families_and_10H"
                ]["b_Landau__sumT_minus_3C2"],
                "pole_ratio": hybrid_running[
                    "including_colocated_visible_families_and_10H"
                ]["pole_over_matching_scale"],
            },
            "strength": (
                "explicitly recomputes the action after combining the low-index source and a "
                "single nonlinear link; all 24 relative modes and all local physical Hessian "
                "zero modes are removed"
            ),
            "fatal_open_items": list(hybrid["limitations"]),
            "decision": "selected boundary-EFT branch, but not an elementary UV completion",
        },
        flipped_route(g),
        {
            "id": "R4_original_two_site_nonlinear_alignment",
            "rank": 4,
            "evidence_level": "repository-executable tangent-space EFT certificate",
            "exact_results": {
                "endpoint_partition": incidence["simultaneous_incidence_dimensions"],
                "alignment_rank": alignment["alignment_Hessian_rank"],
                "gauge_rank": alignment["D_rank"],
                "combined_rank": alignment["combined_Goldstone_mass_rank"],
                "combined_nullity": alignment["combined_Goldstone_mass_nullity"],
                "alignment_orthogonal_to_gauge": alignment["A_D_exact_zero"],
            },
            "strength": (
                "lifts the 12-dimensional V51-analog incidence sector in this distinct "
                "two-site action"
            ),
            "fatal_open_items": [
                "nonlinear/nonrenormalizable sigma-model action",
                "no elementary UV completion or global Kahler proof",
                "retaining the linear V51 source leaves a pole ratio of 3.51005",
            ],
            "decision": "retain as an exact EFT lemma, not as a UV completion",
        },
        missing_vev_route(g),
    ]
    route_by_id = {row["id"]: row for row in routes}

    integrity = {
        "all_input_core_hashes_valid": True,
        "low_index_witness_is_exactly_supersymmetric": route_by_id[
            "R1_exact_conventional_low_index"
        ]["exact_results"]["F_and_D_flat"],
        "low_index_Hessian_kernel_is_exactly_gauge": (
            geometry["orbit_rank_mod37"] == 33
            and geometry["hessian_rank_mod37"] == 98
            and geometry["hessian_nullity_mod37"] == 33
            and geometry["ward_product_exactly_zero"]
            and geometry["kernel_equals_broken_gauge_orbit"]
        ),
        "low_index_source_passes_100_and_1000_scale_windows": (
            running["one_loop_b_with_three_16_families_and_one_10H"] <= b_max_1000
            and running["landau_pole_over_matching_scale_if_b_positive"] > 1.0e9
        ),
        "lean_alignment_lifts_exactly_the_12_dimensional_V51_analog_sector": (
            incidence["simultaneous_incidence_dimensions"]
            == {
                "PS_intersection_SU5__SM": 12,
                "PS_only": 9,
                "SU5_only": 12,
                "neither": 12,
            }
            and alignment["A_rank"] == 12
            and alignment["D_rank"] == 54
            and alignment["A_D_exact_zero"]
            and alignment["combined_Goldstone_mass_rank"] == 66
            and alignment["combined_Goldstone_mass_nullity"] == 0
        ),
        "hybrid_alignment_lifts_exactly_24_relative_chirals": (
            hybrid_partition
            == {
                "PS_intersection_source_SM": 12,
                "PS_only": 9,
                "source_SM_only": 0,
                "neither": 24,
            }
            and hybrid_rxi["A_rank"] == 24
            and hybrid_rxi["D_rank"] == 54
            and hybrid_rxi["A_D_exact_zero"]
            and hybrid_rxi["combined_Goldstone_rank"] == 78
            and hybrid_rxi["combined_Goldstone_nullity"] == 0
        ),
        "hybrid_full_Hessian_kernel_is_exactly_gauge": (
            hybrid_full["coordinates"] == 176
            and hybrid_full["Q_rank_mod37"] == 54
            and hybrid_full["H_rank_mod37"] == 122
            and hybrid_full["H_nullity_mod37"] == 54
            and hybrid_full["HQ_exact_zero"]
            and hybrid_full["kernel_equals_broken_gauge_orbit"]
        ),
        "hybrid_proxy_pole_is_above_its_NDA_cutoff": (
            hybrid_running["including_colocated_visible_families_and_10H"][
                "pole_over_matching_scale"
            ]
            > hybrid_running["nonlinear_sigma_NDA_cutoff_over_vector_mass"]
            and "EFT_ONLY" in hybrid["gate_effect"]["candidate_UV_viability"]
        ),
        "minimal_repair_has_rank_three_renormalizable_double_seesaw": (
            repair["upstream"]["core_sha256"] == low["core_sha256"]
            and repair["n_failed"] == 0
            and repair_seesaw["ranks"]["heavy"] == 7
            and repair_seesaw["ranks"]["full"] == 10
            and repair_seesaw["ranks"]["induced_RH"] == 3
            and repair_seesaw["ranks"]["light"] == 3
            and repair_seesaw["full_neutral_matrix_nonsingular"]
        ),
        "minimal_repair_Z2_survives_declared_VEVs": (
            repair_selector["all_nonzero_VEV_fields_even"]
            and repair_selector["required_operators_even"]
            and repair_selector["listed_dangerous_operators_odd"]
            and all(
                repair_selector["standard_discrete_anomaly_ledgers"][name] == 0
                for name in (
                    "odd_Weyl_dimension_mod2",
                    "SO10_Dynkin_index_sum_mod2",
                    "cubic_Z2_charge_sum_mod2",
                )
            )
        ),
        "DT_rank_witness_is_exact_and_explicitly_tuned": (
            repair_dt["color_triplet_coordinate_block"]["rank"] == 6
            and repair_dt["weak_doublet_coordinate_block"]["nullity"] == 4
            and repair_dt["condition_codimension"] == 1
            and not repair_dt["selector_enforces_coefficient_relation"]
            and not repair_dt["natural_missing_partner_or_DW"]
        ),
        "minimal_repair_stays_inside_perturbative_screen": (
            repair_running["total_chiral_T"] == 31
            and repair_running["one_loop_b"] == 7
            and repair_running["formal_landau_pole_over_matching_scale"] > 1.0e9
        ),
        "nonlinear_alignment_not_mislabeled_as_UV_completion": (
            "FAIL_AS_COMPLETION" in lean["gate_effect"]["candidate_UV_viability"]
            and lean_running["linear_V51_source_retained"][
                "Landau_pole_over_matching_scale"
            ] < 3.52
        ),
        "flipped_family_local_anomalies_cancel": all(
            value == 0
            for value in route_by_id["R3_flipped_Spin10xU1X"][
                "family_anomaly_sums"
            ].values()
        ),
        "no_cross_action_clause_promotion": (
            not low["gate_effect"]["clause_promotions"]
            and not lean["gate_effect"]["gates_promoted"]
            and not hybrid["gate_effect"]["gates_promoted"]
            and not repair["gate_effect"]["clause_promotions"]
            and all(row["status"] != "pass" for row in clauses)
        ),
        "only_frozen_G1_is_closed": (
            [row["gate"] for row in gates if row["closed"]] == ["G1"]
        ),
    }
    failures = [name for name, passed in integrity.items() if not passed]
    if failures:
        raise RuntimeError("V52 integration integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v52-new-physics-route-integration-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "serious_new_candidate_exists": True,
            "empirical_new_physics_discovery": False,
            "complete_theory": False,
            "selected_route": "R1_exact_conventional_low_index",
            "G2_closed": False,
            "full_gates_closed": 1,
            "closed_gates": ["G1"],
            "gate_scope": (
                "G1 is closed only in the frozen reusable ordinary-Spin namespace inherited "
                "from V47; no complete V52 candidate gate is closed."
            ),
            "V52_candidate_closed_gates": [],
            "statement": (
                "V52 replaces speculation with an exact low-index Spin(10)-sector source candidate "
                "and separately proves that nonlinear alignment lifts the 12-dimensional "
                "V51-analog incidence sector in a new two-site action. The selected single-site "
                "redesign evades the V51 link and near-threshold running failures by deleting that "
                "sector, not by repairing the V51 action. A recomputed low-index hybrid has an "
                "exact 176-coordinate source+link Hessian, but remains a nonlinear EFT. A minimal "
                "renormalizable extension supplies an exact rank-three double seesaw and external "
                "Z2 ledger; its DT result is tuned and its UV/operator completion is open."
            ),
        },
        "selection_logic": {
            "primary_selection_rule": (
                "prefer the exact elementary renormalizable single-site source as the foundation "
                "over a nonlinear EFT, while retaining all independently verified branch lemmas"
            ),
            "why_R1": (
                "R1 has a complete source F/D/orbit/Hessian certificate, stays in ordinary "
                "Spin(10), has no link sector, and retains a 1.56e9 one-loop window."
            ),
            "hybrid_branch_decision": (
                "R2 is not a pasted inference: its PS-versus-source-SM incidence, alignment and "
                "entire 176-coordinate Hessian were recomputed for one new action. It is kept "
                "as the boundary-EFT branch because its nonlinear link lacks a UV completion."
            ),
        },
        "route_ranking": routes,
        "minimal_repair_module": {
            "status": repair["status"],
            "core_sha256": repair["core_sha256"],
            "scope": (
                "A tested extension of the selected R1 foundation, not part of the 131-coordinate "
                "source Hessian and not yet a frozen whole action."
            ),
            "additions": repair["minimal_additions"],
            "double_seesaw": {
                "dimensions": repair_seesaw["dimensions"],
                "ranks": repair_seesaw["ranks"],
                "rank_three_Majorana_generation": repair_seesaw[
                    "rank_three_Majorana_generation"
                ],
                "source_vacuum_unchanged": repair_seesaw["source_vacuum_unchanged"],
                "scope_caveat": (
                    "This is a phenomenological neutral-mass-matrix existence witness and "
                    "presumes a nonzero electroweak Dirac matrix; it is not included in the "
                    "131-coordinate GUT-source Hessian."
                ),
            },
            "external_Z2": {
                "all_nonzero_VEV_fields_even": repair_selector[
                    "all_nonzero_VEV_fields_even"
                ],
                "required_operators_even": repair_selector["required_operators_even"],
                "listed_dangerous_operators_odd": repair_selector[
                    "listed_dangerous_operators_odd"
                ],
                "mod2_ledgers": repair_selector["standard_discrete_anomaly_ledgers"],
                "scope_caveat": (
                    repair_selector["scope_caveat"]
                    + "; ordinary matter parity still allows even-matter dangerous classes such "
                    "as dimension-five 16F^4, so this is not a proton-safe full selector census"
                ),
            },
            "doublet_triplet": {
                "triplet_rank": repair_dt["color_triplet_coordinate_block"]["rank"],
                "weak_nullity": repair_dt["weak_doublet_coordinate_block"]["nullity"],
                "interpretation": repair_dt["weak_doublet_coordinate_block"][
                    "interpretation"
                ],
                "massless_condition": repair_dt["massless_condition"],
                "condition_codimension": repair_dt["condition_codimension"],
                "natural": repair_dt["natural_missing_partner_or_DW"],
                "decision": repair_dt["claim"],
            },
            "running": repair_running,
            "decision": (
                "Exact seesaw and declared external-Z2 existence witnesses; exact but tuned DT "
                "rank witness. Natural DT, UV selector, full d<=5 operator/proton census and the "
                "enlarged whole-action Hessian remain absent."
            ),
        },
        "perturbative_acceptance": {
            "g": g,
            "minimum_scale_ratio": 100,
            "maximum_positive_b_for_100x": b_max_100,
            "maximum_positive_b_for_1000x": b_max_1000,
            "selected_R1_b": running[
                "one_loop_b_with_three_16_families_and_one_10H"
            ],
        },
        "V52_candidate_clause_ledger": clauses,
        "gate_ledger_scope": (
            "Frozen cumulative frontier: closed flags denote reusable prior-namespace results, "
            "not same-action closure for the selected V52 candidate."
        ),
        "same_action_decision": {
            "V51_core_sha256": v51["core_sha256"],
            "V52_low_index_source_core_sha256": low["core_sha256"],
            "V52_lean_alignment_core_sha256": lean["core_sha256"],
            "V52_low_index_hybrid_core_sha256": hybrid["core_sha256"],
            "V52_minimal_repair_core_sha256": repair["core_sha256"],
            "equivalence_proved": False,
            "statement": (
                "No V50/V51 clause or Wilson tensor is inherited by any V52 action. "
                "The exact V52 results are reusable lemmas only until one complete action is frozen."
            ),
        },
        "sharp_next_obligations": [
            {
                "id": "N1",
                "task": "Freeze one complete R1-plus-repair field/action/selector census, construct a UV discrete-gauge embedding, and enumerate every allowed operator through dimension five.",
                "kill_condition": "Reject if the external Z2 cannot be UV completed or supplemented to forbid the even-matter proton-decay classes while preserving the required seesaw/Yukawa terms.",
            },
            {
                "id": "N2",
                "task": "Replace the tuned mH=3*kH relation by a symmetry/vacuum-enforced natural DT mechanism, then recompute the enlarged holomorphic Hessian.",
                "kill_condition": "Require exactly one light Higgs-doublet pair, no light colored triplet/exotic, no unprotected coefficient cancellation and no physical GUT-scale modulus.",
            },
            {
                "id": "N3",
                "task": "Redo the invariant/Clebsch census and derive the V52 action-to-EFT Wilson array; do not reuse the V51 array by name.",
                "kill_condition": "Reject any route without one action hash shared by the vacuum, regulator/matching and coefficient array.",
            },
            {
                "id": "N4",
                "task": "Run two-loop unification, one-loop thresholds, dressed proton decay and a rank-three flavour/neutrino fit.",
                "kill_condition": "Reject if perturbative control, experimental proton limits or the withheld flavour prediction fails.",
            },
        ],
        "gate_ledger": gates,
        "primary_sources": [
            {
                "title": "Buccella and Savoy: Intermediate Symmetries in SUSY SO(10)",
                "url": "https://arxiv.org/abs/hep-ph/0202278",
            },
            {
                "title": "Bertolini, Di Luzio and Malinsky: Minimal Flipped SO(10) x U(1) SUSY Higgs Model",
                "url": "https://arxiv.org/abs/1011.1821",
            },
            {
                "title": "Chacko and Mohapatra: New Doublet-Triplet Splitting Mechanism",
                "url": "https://arxiv.org/abs/hep-ph/9810315",
            },
            {
                "title": "Mohapatra and Valle: Neutrino Mass and Baryon-Number Nonconservation in Superstring Models",
                "url": "https://doi.org/10.1103/PhysRevD.34.1642",
            },
            {
                "title": "Banks and Dine: Note on Discrete Gauge Anomalies",
                "url": "https://arxiv.org/abs/hep-th/9109045",
            },
            {
                "title": "Nath and Syed: SO(10) Spinor and Tensor Couplings",
                "url": "https://arxiv.org/abs/hep-th/0109116",
            },
            {
                "title": "Haba, Mimura and Yamada: Proton Decay in Lean SUSY SO(10)",
                "url": "https://arxiv.org/abs/1904.11697",
            },
        ],
        "input_core_hashes": {
            name: value["core_sha256"] for name, value in loaded.items()
        },
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    routes = report["route_ranking"]
    r1, r2, r3, r4, r5 = routes
    repair = report["minimal_repair_module"]
    gates = "\n".join(
        f"- `{row['gate']}` — `{'closed' if row['closed'] else 'open'}`: "
        f"{row['advance']} Remaining: {row['blocker']}"
        for row in report["gate_ledger"]
    )
    clauses = "\n".join(
        f"- `{row['id']}` — `{row['status']}`: {row['statement']}"
        for row in report["V52_candidate_clause_ledger"]
    )
    obligations = "\n".join(
        f"{index}. **{row['id']}** — {row['task']} Kill test: {row['kill_condition']}"
        for index, row in enumerate(report["sharp_next_obligations"], 1)
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']})" for row in report["primary_sources"]
    )
    return f"""# V52 new-physics route integration audit

Status: `{report['status']}`

## Outcome

V52 produces a **real candidate advance**, not a complete theory.  The selected
single-site `54+45+16+bar16` source has an exact supersymmetric witness whose
Spin(10)-sector stabilizer is the SM, with no additional local infinitesimal
source modulus at that witness.  It evades V51's link and near-threshold running
failures by deleting the link sector; this is not a repair of the V51 action.
Separately, a nonlinear two-site theorem lifts a 12-dimensional V51-analog
incidence sector, and the recomputed low-index hybrid lifts all 24 of its own
relative modes with an exact 176-coordinate source+link Hessian.  That hybrid
remains an EFT without an elementary UV completion.

The minimal R1 extension also provides exact existence witnesses for a rank-three
renormalizable double seesaw, a VEV-stable external Z2 ledger, and a triplet-heavy/
one-Higgs-pair tree matrix.  The last result is an unprotected codimension-one
tuning, while the Z2 lacks a UV embedding and permits dangerous even-matter
classes unless further selection rules are supplied.

**No result is combined across action lineages. G2 remains open. The frozen
cumulative ledger retains only prior ordinary-Spin G1; the V52 candidate itself
closes 0/8 complete gates.**

## Selected route: exact conventional low-index source

- Coordinates: `{r1['coordinates']}`.
- Exact ranks: `rank(Q)={r1['exact_results']['orbit_rank']}` and
  `rank(H)={r1['exact_results']['Hessian_rank']}` with
  `nullity(H)={r1['exact_results']['Hessian_nullity']}`.
- Exact Ward/kernel result: `HQ=0` and `ker(H)=im(Q)`.
- Running: source `sum T={r1['running']['source_sum_T']}`; with three families
  and one 10H, `b={r1['running']['b_with_three_families_and_10H']}` and
  `Lambda_pole/M={r1['running']['pole_ratio']:.6g}` at `g=0.73`.

This is the strongest foundation because its full GUT-breaking source geometry
is certified in an elementary renormalizable single-site theory.  Its minimal
extension establishes seesaw, external-Z2 and tuned DT rank existence, but does
not establish a UV-safe proton selector, natural DT splitting, a full flavour
fit, thresholds or proton decay.  If an independent V50-style U(1)F is restored,
an additional charged sector is needed to remove the leftover diagonal U(1).

## Recomputed low-index boundary-EFT hybrid

The low-index source stabilizer lies inside the PS host, so its exact endpoint
partition is `12/9/0/24`.  The hybrid alignment has rank
`{r2['exact_results']['alignment_rank']}`, the gauge incidence rank is
`{r2['exact_results']['gauge_rank']}`, and their 78-coordinate Goldstone block
has rank `{r2['exact_results']['combined_Goldstone_rank']}` with zero nullity.
For the actual 45 link plus 131 source coordinates,
`rank(Q)={r2['exact_results']['Q_rank']}` and
`rank(H)={r2['exact_results']['Hessian_rank']}` with
`ker(H)=im(Q)`.  This is a genuine recomputation for one action, not a pasted
cross-action inference.  It is a source+link result, not a whole-phenomenological-
action Hessian.  Its pole proxy (`{r2['running_proxy']['pole_ratio']:.6g}`)
lies above the nonlinear cutoff (`{r2['running_proxy']['NDA_cutoff_over_vector_mass']:.6g}`),
but the link still has no elementary UV beta function.

## Minimal renormalizable R1 repair module

- Added fields: one `10H` and four Spin(10)-singlet `N` fields.
- Double seesaw: heavy rank `{repair['double_seesaw']['ranks']['heavy']}`, full
  neutral rank `{repair['double_seesaw']['ranks']['full']}`, induced-RH rank
  `{repair['double_seesaw']['ranks']['induced_RH']}`, and light rank
  `{repair['double_seesaw']['ranks']['light']}`.
- External Z2: every declared nonzero-VEV field is even, required displayed
  operators are allowed, and the reported gravity/SO(10)/cubic mod-2 ledgers
  vanish.  This is a conservative local ledger, not a continuous-parent or full
  discrete-gauge construction, and it does not forbid even-matter `16F^4`.
- DT matrix: color-triplet rank `{repair['doublet_triplet']['triplet_rank']}` and
  weak nullity `{repair['doublet_triplet']['weak_nullity']}`, corresponding to one
  `Hu,Hd` pair.  The condition `{repair['doublet_triplet']['massless_condition']}`
  is codimension `{repair['doublet_triplet']['condition_codimension']}` and is not
  symmetry protected.
- Running: `sum T={repair['running']['total_chiral_T']}`, `b={repair['running']['one_loop_b']}`,
  and formal one-loop pole ratio `{repair['running']['formal_landau_pole_over_matching_scale']:.6g}`
  at `g=0.73`, before any future naturalizer, messenger or UV-selector fields.

## Original nonlinear alignment lemma

The PS/SU(5) endpoint partition is `12/9/12/12`.  The gauge incidence has rank
`{r4['exact_results']['gauge_rank']}` and the alignment supplies the orthogonal
rank `{r4['exact_results']['alignment_rank']}`.  Their combined 66-coordinate
mass block has rank `{r4['exact_results']['combined_rank']}` and nullity
`{r4['exact_results']['combined_nullity']}`.  Thus all and only the 12-dimensional
pre-alignment V51-analog sector of this new action is lifted.  The term is nonlinear and
nonrenormalizable, and retaining the V51 linear source leaves a pole only 3.51
matching scales away.

## Other serious routes

- **Flipped Spin(10) x U(1)X:** generic spinor misalignment can leave the SM. The
  primary analysis reports `b10=1` and `bXhat=67/24`; this audit's one-loop
  extrapolation assuming both normalized couplings equal `0.73` gives pole ratios
  `{r3['Landau_pole_over_matching_scale_at_g0p73']['Spin10']:.3g}` and
  `{r3['Landau_pole_over_matching_scale_at_g0p73']['U1Xhat']:.3g}`. It
  changes the gauge group and matter embedding; its 109-coordinate chiral
  Hessian, selector and natural DT mechanism are not complete.
- **Extended missing-VEV repair:** a known simple-representation construction
  supplies renormalizable DT matrices, but raises `b` to 23–24.  Its pole window
  is about 480–628, so it passes a 100x screen but not a 1000x screen and has not
  been joined to the exact V52 Hessian.

## Honest C1-C7 ledger

{clauses}

## Sharp continuation / rejection tests

{obligations}

## G1-G8 frozen cumulative ledger

{report['gate_ledger_scope']}

{gates}

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("canonical hash drifted")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    if report["scientific_verdict"]["G2_closed"]:
        raise RuntimeError("G2 was overpromoted")
    if report["scientific_verdict"]["complete_theory"]:
        raise RuntimeError("candidate was mislabeled as complete")
    if [row["gate"] for row in report["gate_ledger"] if row["closed"]] != ["G1"]:
        raise RuntimeError("gate ledger drifted")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V52 master JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V52 master Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V52_NEW_PHYSICS_ROUTE_INTEGRATION_AUDIT_CHECK_PASS")
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
