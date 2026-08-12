#!/usr/bin/env python3
"""Contract-aware execution roadmap for the SO(10) axion v20 program."""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import g1_g8_gate_ledger_v20 as ledger
import corrected_rank1_endpoint_v21 as corrected_rank1

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_G8_EXECUTION_ROADMAP_V20.json"
OUT_MD = ROOT / "G1_G8_EXECUTION_ROADMAP_V20.md"
G1_COMPONENT_TENSOR_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
)
G1_COMPONENT_TENSOR_SOURCE = (
    ROOT / "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
)
G1_COMPONENT_TENSOR_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
G1_COMPONENT_TENSOR_RAW_SHA256 = (
    "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
)
G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256 = (
    "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f"
)
EFT_G3_JSON = ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
EFT_G3_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
EFT_G3_RAW_SHA256 = (
    "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0"
)
EFT_G4_JSON = ROOT / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json"
EFT_G4_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)
EFT_G4_RAW_SHA256 = (
    "98664542a4e1bbfba233652737826b974963a31c2e86a15e2d73fda1457d987b"
)
EFT_G5_JSON = ROOT / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json"
EFT_G5_CORE_SHA256 = (
    "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
)
EFT_G5_RAW_SHA256 = (
    "6d6e4fd9932a03e35146afb1bca850666e883aaed5e23b73b81f0f703e4e7db9"
)
EFT_G6_JSON = ROOT / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
EFT_G6_SOURCE = ROOT / "final_g6_eft_mathematical_gate_v20.py"
EFT_G6_CORE_SHA256 = (
    "e34b791478bf9cb00f951819cbfec45a99d51be776889d8a4e13cf1717eee738"
)
EFT_G6_RAW_SHA256 = (
    "85000f555eb3bc4e2e4bc49236a82ce2161987212906d78efd667bb52dd432f8"
)

DEPENDENCIES = ledger.DEPENDENCIES

TASKS: list[dict[str, Any]] = [
    {
        "id": "W0-MODEL-CONTRACT",
        "wave": 0,
        "prerequisite": "MODEL_CONTRACT",
        "gates": [],
        "status": "BLOCKED__EXTERNAL_SARAH_EXECUTION_ATTESTATION_MISSING",
        "issue": None,
        "deliverable": (
            "execute the shipped hash-bound Wolfram driver with a real SARAH "
            "installation and retain its v2 process attestation"
        ),
        "acceptance": (
            "a fresh exact-X audit reports contract_consistent=True, native "
            "Gauge/Global/matter/LagrangianInput syntax, and v2 external evidence "
            "bound to the exact model, manifest, validation driver, and process log"
        ),
    },
    {
        "id": "W1-G1-GAUGED-RECERTIFICATION",
        "wave": 1,
        "gates": ["G1"],
        "status": (
            "SOURCE_BOUND_FULL_MATHEMATICAL_G1_COMPONENT_RING_COMPLETE__"
            "MODEL_CONTRACT_BLOCKED"
        ),
        "issue": 176,
        "deliverable": (
            "promote the source-bound 28-orbit, 44-direction, 51-parameter "
            "mathematical G1 component-tensor theorem after external SARAH attestation"
        ),
        "acceptance": (
            "the separate multiplicity census remains scoped, the component-tensor "
            "theorem remains raw/core/source bound, and authoritative G1 carries a "
            "valid external executable-contract attestation"
        ),
    },
    {
        "id": "W2-G2-GAUGED-PROJECTION",
        "wave": 2,
        "gates": ["G2"],
        "status": (
            "SCOPED_DERIVATIVE_AUDIT_COMPLETE__BLOCKED_ON_MODEL_CONTRACT"
        ),
        "issue": 176,
        "deliverable": (
            "promote the completed 44/51/486 component-potential derivative, "
            "Hessian, and Ward audit after the executable contract promotes mathematical G1"
        ),
        "acceptance": (
            "all SO(10)xU(1)_X Ward identities stay green; all three exact "
            "structural-zero columns, the compiler-bound nonzero 13x13 minor, "
            "and the exact full-row factorization continue to prove "
            "rank/nullity 13/38; SVD remains diagnostic only"
        ),
    },
    {
        "id": "W3-G3-FULL-STATIONARITY",
        "wave": 3,
        "gates": ["G3"],
        "status": "SU5_DELTA_CHIRAL_H_EXACT_LOCAL_MINIMUM__PURE_DELTA_FULL_RESIDUAL_GAP_CLOSED__RANK1_SU4_FIXED_ENDPOINT_ARBITRARY_PHI_EXACT__GLOBAL_SIGMA_GENERAL_H_FULL_HESSIAN_AND_G3_OPEN__BLOCKED_ON_G2_PROMOTION",
        "issue": 178,
        "deliverable": (
            "prove a uniform coercive global gap for arbitrary non-pure-Delta "
            "Sigma orientations of the SU(5)+Delta chiral-H candidate; its exact "
            "448/38 Hessian and complete pure-Delta maximal-negative sector are "
            "complete. The prior four-real-dimensional SU(3) regression is "
            "historical and subsumed. At fixed H=h_- and Sigma=q/4, the "
            "corrected v21 exact theorem covers every real Phi210; its exact "
            "SU(4) stabilizer, aligned 25-carrier "
            "rank-210 real-form maps, and complete 45-element invariant "
            "quadratic basis from a 5952x551 rank-506 constraint system are "
            "ready. The exact augmented census has dimension 22366, 35 "
            "complex isotypic types spanning 824 copies, 22 real/Hermitian "
            "blocks, 19594 real Schur parameters, and 6585 invariant target "
            "rows with an abstract surjective multiplication map. The complete "
            "cubic interface is now explicit: 540 required Sym2(Phi210) carrier "
            "copies generate all 1414 real Schur cross variables, and their "
            "478x1414 integer coefficient map has exact rank 478 and kernel "
            "dimension 936. Its reserved zero vector is only an abstract "
            "interface placeholder, not the physical G3 target. The exact "
            "homogeneous quartic map has shape 6057x18085, rank 6057, and "
            "kernel dimension 12028. The legacy v20 assembled physical target "
            "is rejected. The corrected 6585x19594 standard positive-Gram map, "
            "ordered-spectral target, and exact strict 22-block/824-pivot primal "
            "prove p(t,Phi)>0 off the homogeneous origin and A(Phi)>3/200 at "
            "t=1 for every real Phi210. Global Sigma, general/full H, the full "
            "Hessian, and G3 remain open"
        ),
        "acceptance": (
            "the full 486-field candidate is globally minimal with all equality "
            "orbits classified, or an exact lower witness rejects it"
        ),
    },
    {
        "id": "W3-G4-FULL-GAUGE-QUOTIENT",
        "wave": 3,
        "gates": ["G4"],
        "status": "EXACT_QUOTIENT_GEOMETRY_COMPLETE__HESSIAN_CLASSIFICATION_BLOCKED_ON_G3",
        "issue": 178,
        "deliverable": (
            "retain the exact SO(10)xU(1)_X rank-37 gauge quotient (449, axion "
            "included) and rank-38 massive/transverse quotient (448) while G3 "
            "classifies the Hessian"
        ),
        "acceptance": (
            "exact gauge/global-symmetry ranks remain compiler-bound and the "
            "completed G3 Hessian has no unexplained zero or negative modes"
        ),
    },
    {
        "id": "W3-G5-FULL-BFB",
        "wave": 3,
        "gates": ["G5"],
        "status": (
            "SCOPED_BFB_CERTIFICATE_COMPLETE__BLOCKED_ON_MODEL_CONTRACT_AND_G1_G2"
        ),
        "issue": 86,
        "deliverable": (
            "promote the completed source-bound SOS/BFB certificate after "
            "the external model execution gate"
        ),
        "acceptance": (
            "the exact 27-parameter SOS identity remains source-bound and covers "
            "every asymptotic field direction"
        ),
    },
    {
        "id": "W4-G6-SPECTRUM",
        "wave": 4,
        "gates": ["G6"],
        "status": "BLOCKED_ON_G3_G4_G5",
        "issue": 106,
        "deliverable": "complete positive physical scalar spectrum with SM provenance",
        "acceptance": "all eigenmasses, irreps, mixings, and uncertainties are complete",
    },
    {
        "id": "W5-G7-TWO-LOOP",
        "wave": 5,
        "gates": ["G7"],
        "status": "BLOCKED_ON_G6_AND_EXTERNAL_VALIDATION",
        "issue": 126,
        "deliverable": "complete two-loop running and component threshold matching",
        "acceptance": "two independent implementations agree within declared tolerances",
    },
    {
        "id": "W6-G8-PROTON",
        "wave": 6,
        "gates": ["G8"],
        "status": "BLOCKED_ON_G3_G6_G7",
        "issue": 106,
        "deliverable": "unique mass-basis proton-decay distribution or a scoped falsification",
        "acceptance": "one authoritative vacuum fixes all Wilson, running, phase, and uncertainty inputs",
    },
]

MILESTONES = [
    {
        "pr": 176,
        "merge_commit": "71ab6d970b7730255bb0ac1f10610b95ac881b46",
        "scope": ledger.HISTORICAL_CONTRACT_ID,
        "authoritative_gate_closure": False,
        "result": (
            "historical Option-C subtheorem: 18 families, 64 directions, "
            "91 parameters, and a dense 486x486 Hessian"
        ),
    },
    {
        "pr": 178,
        "scope": ledger.HISTORICAL_CONTRACT_ID,
        "authoritative_gate_closure": False,
        "result": (
            "historical Option-C subtheorem: 449-dimensional quotient saddle "
            "and fail-closed stationary-family search"
        ),
    },
]


def acyclic() -> bool:
    return ledger._acyclic_dependencies()


def _tasks_for_gate_report(gate_report: dict[str, Any]) -> list[dict[str, Any]]:
    """Reflect the authoritative frontier without promoting scoped subtheorems."""
    if not gate_report["contract_consistent"]:
        return [dict(task) for task in TASKS]
    gates = gate_report["gates"]
    promoted_statuses = {
        "W0-MODEL-CONTRACT": ledger.STATUS_CLOSED,
        "W1-G1-GAUGED-RECERTIFICATION": gates["G1"]["status"],
        "W2-G2-GAUGED-PROJECTION": (
            "BLOCKED_ON_G1"
            if gates["G2"]["status"] == ledger.STATUS_BLOCKED
            else gates["G2"]["status"]
        ),
        "W3-G3-FULL-STATIONARITY": (
            "BLOCKED_ON_G2"
            if gates["G3"]["status"] == ledger.STATUS_BLOCKED
            else gates["G3"]["status"]
        ),
        "W3-G4-FULL-GAUGE-QUOTIENT": (
            "BLOCKED_ON_G3"
            if gates["G4"]["status"] == ledger.STATUS_BLOCKED
            else gates["G4"]["status"]
        ),
        "W3-G5-FULL-BFB": (
            "BLOCKED_ON_G1_G2"
            if gates["G5"]["status"] == ledger.STATUS_BLOCKED
            else gates["G5"]["status"]
        ),
    }
    return [
        {**task, "status": promoted_statuses.get(task["id"], task["status"])}
        for task in TASKS
    ]


def _build_report_from_ledger(gate_report: dict[str, Any]) -> dict[str, Any]:
    """Build the roadmap from a current or hypothetically repaired ledger."""
    gates = gate_report["gates"]
    tasks = _tasks_for_gate_report(gate_report)
    task_ids = [task["id"] for task in tasks]
    gates_with_tasks = {gate for task in tasks for gate in task["gates"]}
    historical = gate_report["historical_option_c_subtheorems"]
    gauged = gate_report["gauged_u1x_scalar_subtheorems"]
    g3_frontier = gate_report["gauged_u1x_g3_constructive_frontier"]
    critical_path = [
        "MODEL_CONTRACT",
        "G1",
        "G2",
        "G3/G4/G5",
        "G6",
        "G7",
        "G8",
    ]
    contract_consistent = bool(gate_report["contract_consistent"])
    g1_component_tensor = ledger._load_json_artifact(G1_COMPONENT_TENSOR_JSON)
    g1_component_tensor_raw_sha256 = ledger._raw_file_sha256(
        G1_COMPONENT_TENSOR_JSON
    )
    g1_component_tensor_source_raw_sha256 = ledger._raw_file_sha256(
        G1_COMPONENT_TENSOR_SOURCE
    )
    direct_g1_component_tensor = (
        ledger._renormalizable_g1_component_tensor_closure(
            g1_component_tensor,
            raw_sha256=g1_component_tensor_raw_sha256,
            source_raw_sha256=g1_component_tensor_source_raw_sha256,
        )
    )
    ledger_g1_component_tensor = gate_report.get(
        "renormalizable_G1_component_tensor_closure", {}
    )
    mathematical_g1_component_tensor_closed = bool(
        G1_COMPONENT_TENSOR_CORE_SHA256
        == ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        and G1_COMPONENT_TENSOR_RAW_SHA256
        == ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256
        and G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        == ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        and direct_g1_component_tensor["source_bound"] is True
        and direct_g1_component_tensor == ledger_g1_component_tensor
        and direct_g1_component_tensor[
            "mathematical_G1_closed_for_renormalizable_model"
        ]
        is True
    )
    try:
        eft_g3 = json.loads(EFT_G3_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        eft_g3 = {}
    eft_classification = eft_g3.get("classification", {})
    eft_g3_raw_sha256 = ledger._raw_file_sha256(EFT_G3_JSON)
    direct_parallel_eft_g3 = ledger._parallel_eft_g3_acceptance(
        eft_g3,
        raw_sha256=eft_g3_raw_sha256,
    )
    ledger_parallel_eft_g3 = gate_report.get(
        "parallel_EFT_G3_acceptance", {}
    )
    parallel_eft_g3_closed = bool(
        EFT_G3_CORE_SHA256 == ledger.FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
        and EFT_G3_RAW_SHA256 == ledger.FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256
        and direct_parallel_eft_g3["source_bound"] is True
        and ledger_parallel_eft_g3 == direct_parallel_eft_g3
        and direct_parallel_eft_g3[
            "mathematical_G3_closed_for_EFT_model"
        ]
        is True
    )
    eft_g4 = ledger._load_json_artifact(EFT_G4_JSON)
    eft_g4_raw_sha256 = ledger._raw_file_sha256(EFT_G4_JSON)
    direct_parallel_eft_g4 = ledger._parallel_eft_g4_mathematical(
        eft_g4,
        raw_sha256=eft_g4_raw_sha256,
    )
    ledger_parallel_eft_g4 = gate_report.get(
        "parallel_EFT_G4_mathematical", {}
    )
    parallel_eft_g4_closed = bool(
        EFT_G4_CORE_SHA256 == ledger.FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256
        and EFT_G4_RAW_SHA256 == ledger.FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256
        and direct_parallel_eft_g4["source_bound"] is True
        and ledger_parallel_eft_g4 == direct_parallel_eft_g4
        and direct_parallel_eft_g4[
            "mathematical_G4_closed_for_EFT_model"
        ]
        is True
    )
    eft_g5 = ledger._load_json_artifact(EFT_G5_JSON)
    eft_g5_raw_sha256 = ledger._raw_file_sha256(EFT_G5_JSON)
    direct_parallel_eft_g5 = ledger._parallel_eft_g5_mathematical(
        eft_g5,
        raw_sha256=eft_g5_raw_sha256,
    )
    ledger_parallel_eft_g5 = gate_report.get(
        "parallel_EFT_G5_mathematical", {}
    )
    parallel_eft_g5_closed = bool(
        EFT_G5_CORE_SHA256 == ledger.FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256
        and EFT_G5_RAW_SHA256 == ledger.FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256
        and direct_parallel_eft_g5["source_bound"] is True
        and ledger_parallel_eft_g5 == direct_parallel_eft_g5
        and direct_parallel_eft_g5[
            "mathematical_G5_closed_for_EFT_model"
        ]
        is True
    )
    eft_g6 = ledger._load_json_artifact(EFT_G6_JSON)
    eft_g6_raw_sha256 = ledger._raw_file_sha256(EFT_G6_JSON)
    direct_parallel_eft_g6 = ledger._parallel_eft_g6_spectrum(
        eft_g6,
        raw_sha256=eft_g6_raw_sha256,
        gate_source_raw_sha256=ledger._raw_file_sha256(EFT_G6_SOURCE),
    )
    ledger_parallel_eft_g6 = gate_report.get("parallel_EFT_G6_spectrum", {})
    parallel_eft_g6_closed = bool(
        EFT_G6_CORE_SHA256 == ledger.FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256
        and EFT_G6_RAW_SHA256 == ledger.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256
        and direct_parallel_eft_g6["source_bound"] is True
        and ledger_parallel_eft_g6 == direct_parallel_eft_g6
        and direct_parallel_eft_g6[
            "mathematical_G6_closed_for_EFT_model"
        ]
        is True
    )
    g1_full_component_tensors_closed = bool(
        gauged["G1"].get("full_G1_closed", False)
    )
    g2_scoped_derivatives_complete = bool(
        gauged["G2"].get("scoped_derivative_audit_complete", False)
    )
    expected_statuses = ledger._expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_scoped_derivatives_complete,
    )
    statuses = {name: row["status"] for name, row in gates.items()}
    expected_task_frontier = {task["id"]: task["status"] for task in TASKS}
    if contract_consistent:
        expected_task_frontier.update(
            {
                "W0-MODEL-CONTRACT": ledger.STATUS_CLOSED,
                "W1-G1-GAUGED-RECERTIFICATION": statuses["G1"],
                "W2-G2-GAUGED-PROJECTION": (
                    "BLOCKED_ON_G1"
                    if statuses["G2"] == ledger.STATUS_BLOCKED
                    else statuses["G2"]
                ),
                "W3-G3-FULL-STATIONARITY": (
                    "BLOCKED_ON_G2"
                    if statuses["G3"] == ledger.STATUS_BLOCKED
                    else statuses["G3"]
                ),
                "W3-G4-FULL-GAUGE-QUOTIENT": "BLOCKED_ON_G3",
                "W3-G5-FULL-BFB": (
                    "BLOCKED_ON_G1_G2"
                    if statuses["G5"] == ledger.STATUS_BLOCKED
                    else statuses["G5"]
                ),
            }
        )
    task_statuses = {task["id"]: task["status"] for task in tasks}
    checks = {
        "gate_ledger_audit_executes": gate_report["n_failed"] == 0,
        "renormalizable_G1_component_tensor_raw_core_source_bound": (
            mathematical_g1_component_tensor_closed
            and direct_g1_component_tensor["raw_sha256"]
            == G1_COMPONENT_TENSOR_RAW_SHA256
            and direct_g1_component_tensor["core_sha256"]
            == G1_COMPONENT_TENSOR_CORE_SHA256
            and direct_g1_component_tensor["source_raw_sha256"]
            == G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
            and direct_g1_component_tensor["authoritative_G1_promoted_closed"]
            is False
            and direct_g1_component_tensor["release_G1_verified"] is False
        ),
        "parallel_EFT_G3_acceptance_raw_and_core_bound": (
            parallel_eft_g3_closed
            and direct_parallel_eft_g3["raw_sha256"] == EFT_G3_RAW_SHA256
            and direct_parallel_eft_g3["core_sha256"] == EFT_G3_CORE_SHA256
        ),
        "parallel_EFT_G4_mathematical_raw_and_core_bound": (
            parallel_eft_g4_closed
            and direct_parallel_eft_g4["raw_sha256"] == EFT_G4_RAW_SHA256
            and direct_parallel_eft_g4["core_sha256"] == EFT_G4_CORE_SHA256
            and direct_parallel_eft_g4[
                "release_G4_verified_for_EFT_model"
            ]
            is False
            and direct_parallel_eft_g4[
                "mathematical_G4_closed_for_original_renormalizable_model"
            ]
            is False
        ),
        "parallel_EFT_G5_mathematical_raw_and_core_bound": (
            parallel_eft_g5_closed
            and direct_parallel_eft_g5["raw_sha256"] == EFT_G5_RAW_SHA256
            and direct_parallel_eft_g5["core_sha256"] == EFT_G5_CORE_SHA256
            and direct_parallel_eft_g5[
                "release_G5_verified_for_EFT_model"
            ]
            is False
            and direct_parallel_eft_g5[
                "authoritative_renormalizable_G5_closed"
            ]
            is False
        ),
        "parallel_EFT_G6_spectrum_raw_and_core_bound": (
            parallel_eft_g6_closed
            and direct_parallel_eft_g6["raw_sha256"] == EFT_G6_RAW_SHA256
            and direct_parallel_eft_g6["core_sha256"] == EFT_G6_CORE_SHA256
            and direct_parallel_eft_g6[
                "release_G6_verified_for_EFT_model"
            ]
            is False
            and direct_parallel_eft_g6[
                "authoritative_renormalizable_G6_closed"
            ]
            is False
            and direct_parallel_eft_g6["authoritative_G6_gate_mutated"]
            is False
        ),
        "parallel_EFT_G4_G5_G6_leave_authoritative_frontier_unchanged": (
            statuses == expected_statuses
            and (
                contract_consistent
                or all(
                    statuses[name] == ledger.STATUS_BLOCKED
                    for name in ("G3", "G4", "G5", "G6")
                )
            )
        ),
        "gate_ledger_state_classified": gate_report["overall_state"] == (
            ledger.STATUS_OPEN if contract_consistent else ledger.STATUS_BLOCKED
        ),
        "gate_frontier_matches_contract_state": statuses == expected_statuses,
        "task_frontier_matches_contract_state": all(
            task_statuses[task_id] == expected_status
            for task_id, expected_status in expected_task_frontier.items()
        ),
        "dependency_graph_acyclic": acyclic(),
        "wave_zero_precedes_G1": critical_path[:2] == ["MODEL_CONTRACT", "G1"],
        "wave_zero_task_unique": sum(
            task["id"] == "W0-MODEL-CONTRACT" for task in tasks
        )
        == 1,
        "task_ids_unique": len(task_ids) == len(set(task_ids)),
        "every_gate_has_execution_task": gates_with_tasks == set(gates),
        "every_task_has_acceptance": all(bool(task["acceptance"]) for task in tasks),
        "historical_64_91_449_facts_preserved": (
            historical["G1"]["invariant_directions"] == 64
            and historical["G1"]["real_potential_parameters"] == 91
            and historical["G3"]["massive_physical_quotient_dimension"] == 449
        ),
        "historical_saddle_search_not_promoted": (
            historical["G3"]["anchored_witness_negative_modes"] == 46
            and historical["G3"]["stability_search_iterations"] == 80
            and historical["G3"]["strict_local_minimum_found"] is False
            and gates["G3"]["status"] != ledger.STATUS_CLOSED
        ),
        "gauged_G1_mathematical_component_ring_and_G2_scoped_audit_recorded": (
            gauged["G1"]["invariant_directions"] == 44
            and gauged["G1"]["real_potential_parameters"] == 51
            and gauged["G1"]["multiplicity_census_complete"] is True
            and gauged["G1"]["character_census_remains_multiplicity_only"] is True
            and gauged["G1"]["full_G1_closed"] is True
            and gauged["G2"]["real_field_dimension"] == 486
            and gauged["G2"]["scoped_derivative_audit_complete"] is True
            and gauged["G2"]["authoritative_promotion_blocked_on_full_G1"]
            is False
            and gauged["G2"]["authoritative_promotion_blocked_on_model_contract"]
            == (not contract_consistent)
            and gauged["G2"]["promoted_stationarity_rank"] == 13
            and gauged["G2"]["promoted_stationarity_nullity"] == 38
            and gauged["G2"][
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            ] is True
            and gauged["G2"]["stationarity_rank_13_exactly_certified"] is True
            and gauged["G2"]["stationarity_nullity_38_exactly_certified"] is True
            and gates["G1"]["scoped_calculation_complete"] is True
            and gates["G1"]["full_gate_calculation_complete"] is True
            and gates["G2"]["scoped_calculation_complete"] is True
        ),
        "constructive_G3_frontier_artifacts_are_integrated": (
            g3_frontier["integrity_pass"] is True
            and all(g3_frontier["artifacts_present"].values())
            and g3_frontier["candidate_nonzero_real_parameters"] == 27
            and g3_frontier["candidate_real_parameter_count"] == 51
            and g3_frontier["candidate_J0"] == "-21/200"
            and g3_frontier["exact_A_square_recoupling_source_bound"] is True
            and g3_frontier["exact_SOS_BFB_stationarity_source_bound"] is True
            and g3_frontier["exact_PD_rank"] == 429
            and g3_frontier["exact_PD_nullity"] == 33
            and g3_frontier["exact_full_Hessian_rank"] == 448
            and g3_frontier["fixed_P_branch_exactly_excluded"] is True
            and g3_frontier[
                "lower_replacement_rejected_for_wrong_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_PD_exact_global_frontier"] is True
            and g3_frontier["SU5_Delta_PD_exact_Hessian_rank"] == 429
            and g3_frontier["SU5_Delta_PD_exact_Hessian_nullity"] == 33
            and g3_frontier["SU5_Delta_HSX_honest_frontier"] is True
            and g3_frontier["SU5_Delta_HSX_nonzero_real_parameters"] == 28
            and g3_frontier["SU5_Delta_HSX_exact_symmetry_ranks"]
            == [36, 37, 38]
            and g3_frontier["SU5_Delta_HSX_transverse_dimension"] == 448
            and g3_frontier["SU5_Delta_HSX_full_Hessian_proof_grade"] is False
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_closed"] is True
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_rank"] == 448
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_nullity"] == 38
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_PSD"] is True
            and g3_frontier[
                "SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_HSX_exact_quotient_positive"] is True
            and g3_frontier["SU5_Delta_HSX_full_quartic_BFB_exact"] is True
            and g3_frontier["SU5_Delta_HSX_finite_field_global_gap_open"] is True
            and g3_frontier["SU5_Delta_equality_honestly_reduced"] is True
            and g3_frontier["SU5_Delta_Phi_orbit_audit_honest"] is True
            and g3_frontier[
                "SU5_Delta_literal_single_Phi_orbit_refuted"
            ]
            is True
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_open"] is False
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_closed"] is True
            and g3_frontier["SU5_Delta_SU4_Phi_slice_classified"] is True
            and g3_frontier[
                "SU5_Delta_signed_Phi_local_components_closed"
            ]
            is True
            and g3_frontier["SU5_Delta_distant_Phi_components_excluded"]
            is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"] is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"] == 16
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_open"] is False
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_closed"] is True
            and g3_frontier["SU5_Delta_PD_equality_orbits_classified_exactly"]
            is True
            and g3_frontier[
                "SU5_Delta_global_Phi_orbit_theorem_core_sha256"
            ]
            == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
            and g3_frontier[
                "SU5_Delta_chiral_global_gap_honestly_reduced"
            ]
            is True
            and g3_frontier["SU5_fixed_F_full_offkernel_gap_closed"] is True
            and g3_frontier["SU5_fixed_F_gap_equality_is_selected_flag"] is True
            and g3_frontier["SU5_arbitrary_Phi_offstratum_gap_open"] is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_route_excluded"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_strict_margin"
            ]
            == "7859/140295000"
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_gap_closed"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_minimum"
            ]
            == "1/5000"
            and g3_frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
            is True
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_dimension"] == 4
            and g3_frontier["SU5_max_negative_rank1_SU3_ambient_dimension"] == 16
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_minimum"]
            == "1/5000"
            and g3_frontier["SU5_max_negative_arbitrary_rank1_Phi_open"] is True
            and g3_frontier[
                "SU5_max_negative_arbitrary_Sigma_orientation_open"
            ]
            is True
            and g3_frontier["rank1_SU4_stabilizer_infrastructure_exact"] is True
            and g3_frontier["rank1_SU4_joint_stabilizer_dimension"] == 15
            and g3_frontier[
                "rank1_SU4_Phi210_intertwiner_infrastructure_exact"
            ]
            is True
            and g3_frontier["rank1_SU4_Phi210_carrier_count"] == 25
            and g3_frontier["rank1_SU4_Sym2_invariant_dimension"] == 45
            and g3_frontier["rank1_SU4_aligned_carriers_exact"] is True
            and g3_frontier["rank1_SU4_aligned_direct_sum_rank"] == 210
            and g3_frontier["rank1_SU4_physical_real_maps_exact"] is True
            and g3_frontier["rank1_SU4_Phi210_quadratic_basis_exact"] is True
            and g3_frontier["rank1_SU4_quadratic_constraint_shape"]
            == [5952, 551]
            and g3_frontier["rank1_SU4_quadratic_constraint_rank"] == 506
            and g3_frontier["rank1_SU4_quadratic_constraint_nullity"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_count"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_rank"] == 45
            and g3_frontier[
                "rank1_SU4_quadratic_live_invariance_exact"
            ] is True
            and g3_frontier["rank1_SU4_Schur_SOS_SDP_open"] is True
            and g3_frontier["rank1_SU4_arbitrary_Phi_bound_open"] is True
            and g3_frontier["rank1_SU4_augmented_SOS_census_exact"] is True
            and g3_frontier["rank1_SU4_augmented_homogeneous_dimension"]
            == 22_366
            and g3_frontier[
                "rank1_SU4_augmented_complex_isotypic_type_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_complex_irreducible_copy_count"
            ] == 824
            and g3_frontier["rank1_SU4_augmented_real_isotypic_block_count"]
            == 22
            and g3_frontier["rank1_SU4_augmented_Schur_real_parameter_count"]
            == 19_594
            and g3_frontier["rank1_SU4_augmented_invariant_equation_count"]
            == 6_585
            and g3_frontier["rank1_SU4_augmented_coordinate_Schur_map_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_isotypic_maps_open"] is True
            and g3_frontier["rank1_SU4_augmented_physical_target_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_arbitrary_Phi_bound_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_cubic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_carrier_copy_count"
            ] == 540
            and g3_frontier[
                "rank1_SU4_augmented_cubic_real_variable_count"
            ] == 1_414
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_shape"
            ] == [478, 1_414]
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_nnz"
            ] == 3_145
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_rank"
            ] == 478
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"
            ] == 936
            and g3_frontier[
                "rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_other_graded_maps_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_full_coordinate_map_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_cubic_G3_open"] is True
            and g3_frontier["rank1_SU4_augmented_quartic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_carrier_family_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_quartic_irreducible_copy_count"
            ] == 798
            and g3_frontier[
                "rank1_SU4_augmented_quartic_real_block_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_shape"
            ] == [6_057, 18_085]
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_nnz"
            ] == 115_641
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_rank"
            ] == 6_057
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"
            ] == 12_028
            and g3_frontier[
                "rank1_SU4_augmented_quartic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_quartic_SDP_open"] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_quartic_G3_open"] is True
            and g3_frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ] is True
            and g3_frontier["rank1_SU4_legacy_v20_physical_target_valid"]
            is False
            and g3_frontier["rank1_SU4_legacy_v20_primal_valid"] is False
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_route_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_parameter_count"
            ] == 19_594
            and g3_frontier[
                "rank1_SU4_augmented_real_type_PSD_congruences_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_complex_Hermitian_coordinates_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_fixed_endpoint_theorem_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_publication_manifest_sha256"
            ] == corrected_rank1.EXPECTED_MANIFEST_RAW_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_shape"
            ] == [6_585, 19_594]
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_common_denominator"
            ] == 256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_nnz"
            ] == 138_550
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_sha256"
            ] == corrected_rank1.EXPECTED_MAP_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_common_denominator"
            ] == 576_000
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_nonzero_count"
            ] == 512
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_sha256"
            ] == corrected_rank1.EXPECTED_TARGET_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_exact_coefficient_equalities"
            ] == 6_585
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_Gram_blocks"
            ] == 22
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_LDL_pivots"
            ] == 824
            and g3_frontier[
                "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_p_zero_set_at_t1_empty"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_global_Sigma_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_general_H_proved"] is False
            and g3_frontier["rank1_SU4_corrected_full_H_proved"] is False
            and g3_frontier[
                "rank1_SU4_corrected_full_Hessian_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_G3_closed"] is False
            and g3_frontier[
                "SU5_arbitrary_Phi_nonzero_residual_cancellations_open"
            ]
            is False
            and g3_frontier[
                "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"
            ]
            is True
            and g3_frontier["SU5_arbitrary_Phi_uniform_coercivity_open"] is True
            and g3_frontier["SU5_Delta_chiral_lower_witness_found"] is False
            and g3_frontier["SU5_Delta_chiral_small_beta_route_exists"] is True
            and g3_frontier[
                "SU5_Delta_chiral_beta_1_over_20_global_certified"
            ]
            is False
            and g3_frontier["alternative_global_SOS_audit_honestly_open"]
            is True
            and g3_frontier[
                "all_vanishing_global_SOS_replacements_excluded"
            ]
            is True
            and g3_frontier[
                "nonvanishing_residual_global_SOS_replacements_excluded"
            ]
            is False
        ),
        "constructive_G3_local_minimum_and_global_rejection_integrated": (
            g3_frontier["direct_exact_PD_source_binding"] is True
            and g3_frontier["complete_potential_BFB_exactly_certified"] is True
            and g3_frontier[
                "selected_vacuum_stationarity_exactly_certified"
            ]
            is True
            and g3_frontier["strict_local_minimum_certified"] is True
            and g3_frontier["global_minimum_certified"] is False
            and g3_frontier["selected_global_minimum_disproved"] is True
            and g3_frontier[
                "exact_lower_energy_field_witness_certified"
            ]
            is True
            and g3_frontier["constructive_candidate_rejected_for_G3"] is True
            and g3_frontier["global_uniqueness_certified"] is False
            and g3_frontier["G3_closed"] is False
            and gates["G3"]["status"] != ledger.STATUS_CLOSED
            and gates["G5"]["status"] == expected_statuses["G5"]
        ),
        "whole_model_neither_validated_nor_excluded": (
            gate_report["feasibility"]["whole_model_validated"] is False
            and gate_report["feasibility"]["whole_model_excluded"] is False
        ),
    }
    audit_failures = [name for name, passed in checks.items() if not passed]
    if audit_failures:
        status = "G1_G8_EXECUTION_ROADMAP_AUDIT_FAILED"
        overall_state = "EXECUTION_FAIL"
    elif contract_consistent and statuses["G1"] == ledger.STATUS_CLOSED and statuses[
        "G2"
    ] == ledger.STATUS_CLOSED:
        status = "G1_G8_EXECUTION_ROADMAP_READY__G1_G2_G5_CLOSED__G3_GLOBAL_OPEN"
        overall_state = ledger.STATUS_OPEN
    elif contract_consistent:
        status = (
            "G1_G8_EXECUTION_ROADMAP_READY__MODEL_CONTRACT_CLOSED__"
            "G1_COMPONENT_TENSOR_INTEGRATION_OPEN__G2_BLOCKED_ON_G1"
        )
        overall_state = ledger.STATUS_OPEN
    else:
        status = "G1_G8_EXECUTION_ROADMAP_READY__WAVE0_MODEL_CONTRACT_BLOCKED"
        overall_state = ledger.STATUS_BLOCKED

    verdict = (
        "Wave 0 and the gauged scalar G1/G2 recertification are CLOSED. G3 "
        "has a 27-of-51 perturbative SOS candidate with J0=-21/200. Source-bound "
        "identities prove exact stationarity and complete BFB; direct exact "
        "P+Delta rank/nullity 429/33 plus the extension certificate prove a "
        "strict local minimum on all 448 transverse directions. An exact second "
        "stationary orbit is lower by 25*r^4/19008, so the selected global "
        "vacuum is rejected. The fixed-P branch is exactly excluded and its lower "
        "replacement has the wrong gauge symmetry. The surviving SU(5)+Delta "
        "Phi/Sigma orbit is an exact global SOS minimum with SM stabilizer and "
        "rank/nullity 429/33. Its chiral-H full Hessian is exactly PSD with "
        "rank/nullity 448/38 and kernel precisely the symmetry orbit. The complete "
        "maximally-negative pure-Delta sector is excluded for arbitrary real Phi "
        "and all nonzero residuals with sharp gap 1/5000. The prior "
        "four-real-dimensional SU(3) regression is historical and subsumed. At "
        "fixed H=h_- and Sigma=q/4, the corrected theorem covers every real "
        "Phi210. Its exact SU(4) "
        "stabilizer, aligned rank-210 carrier maps, and explicit 45-element "
        "Phi210 invariant quadratic basis now feed an exact augmented census: "
        "dimension 22366, 35 isotypic types/824 copies, 22 real/Hermitian "
        "blocks, 19594 real Schur parameters, and 6585 invariant rows. The "
        "complete cubic interface has all 1414 real cross variables and an "
        "exact-rank-478, 478x1414 integer map with kernel dimension 936. Its "
        "zero placeholder is not a physical target. The homogeneous quartic "
        "map is exact-rank-6057 with shape 6057x18085 and kernel dimension "
        "12028. The legacy v20 assembled physical target is rejected. The "
        "corrected 6585x19594 standard positive-Gram map, ordered-spectral "
        "target, and exact strict 22-block/824-pivot primal prove p(t,Phi)>0 "
        "off the homogeneous origin and A(Phi)>3/200 at t=1 for every real "
        "Phi210. Global Sigma, general/full H, the full Hessian, and G3 remain "
        "open. G5 is "
        "CLOSED. G4 and "
        "G6-G8 remain dependency-blocked; the "
        "historical 64/91 saddle/search remains scoped to option C."
        if contract_consistent
        and statuses["G1"] == ledger.STATUS_CLOSED
        and statuses["G2"] == ledger.STATUS_CLOSED
        else "Wave 0 MODEL_CONTRACT is the first critical-path task. All G1-G8 "
        "authoritative gates are BLOCKED and none is closed. The exact G1 "
        "multiplicity census remains a distinct scoped theorem at 28 Hermitian "
        "conjugacy orbits, while the separate raw/core/source-bound component-tensor "
        "theorem closes the mathematical ring at 44 directions, 51 parameters, and "
        "18 tensor families. The scoped G2 derivative audit is complete at 44/51/486. Three "
        "structural gradient columns vanish exactly; a compiler-bound nonzero "
        "13x13 minor and exact full-row factorization prove stationarity "
        "rank/nullity 13/38, with SVD retained only as a diagnostic. G2 does not "
        "require recalculation, but G1/G2 cannot be authoritatively promoted before "
        "the external model contract closes. G3 now has a 27-of-51 perturbative SOS "
        "candidate with J0=-21/200. Exact source-bound SOS identities prove "
        "stationarity and complete BFB. Direct exact arithmetic gives P+Delta "
        "rank/nullity 429/33 and proves positivity on all 448 transverse Hessian "
        "directions, so the selected orbit is a strict local minimum. A source-bound "
        "field counterexample is lower by 25*r^4/19008 and rejects it as the "
        "global vacuum. The fixed-P branch is exactly excluded and the lower "
        "replacement has the wrong gauge symmetry. The SU(5)+Delta Phi/Sigma "
        "branch is an exact global SOS minimum with the correct SM stabilizer "
        "and rank/nullity 429/33. A chiral-H extension is exactly stationary, "
        "BFB and symmetry-correct. Its source-bound 486-real Hessian is exactly "
        "PSD with rank/nullity 448/38 and kernel exactly the 38 symmetry tangents. "
        "The complete maximally-negative pure-Delta sector is excluded for arbitrary "
        "real Phi and all nonzero residuals with sharp gap 1/5000. The prior "
        "four-real-dimensional SU3 regression is historical and subsumed. At "
        "fixed H=h_- and Sigma=q/4, the corrected v21 exact theorem covers every "
        "real Phi210. Its exact SU(4) "
        "stabilizer, aligned rank-210 carrier maps, and explicit 45-element "
        "Phi210 invariant quadratic basis now feed the exact 22366-dimensional "
        "augmented census with 35 isotypic types/824 copies, 22 real/Hermitian "
        "blocks, 19594 Schur parameters and 6585 invariant rows. The complete "
        "cubic interface has all 1414 real cross variables and an exact-rank-478, "
        "478x1414 integer map with kernel dimension 936. Its zero placeholder "
        "is not a physical target. The homogeneous quartic map is exact-rank-6057 "
        "with shape 6057x18085 and kernel dimension 12028. The legacy v20 "
        "assembled physical target is rejected. The corrected 6585x19594 "
        "standard positive-Gram map, ordered-spectral target, and exact strict "
        "22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin "
        "and A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma, "
        "general/full H, the full Hessian, and G3 remain open. The historical "
        "64/91 calculation "
        "and 449-dimensional saddle/search remain scoped to option C."
    )
    if contract_consistent and statuses["G1"] == ledger.STATUS_OPEN:
        verdict = (
            "Wave 0 MODEL_CONTRACT is CLOSED, but full G1 remains OPEN. The exact "
            "renormalizable multiplicity census is complete at 28 Hermitian "
            "conjugacy orbits, 44 invariant directions, and 51 real parameters; "
            "the explicit component-tensor/Clebsch integration is still open. "
            "The exact 44/51/486 G2 derivative and Ward audit is complete as a "
            "scoped subtheorem with stationarity rank/nullity 13/38, but its "
            "authoritative task remains BLOCKED_ON_G1. Contract repair alone "
            "therefore closes no G1-G8 gate; G3-G8 remain dependency-blocked."
        )
    verdict += (
        " In parallel, the registered dimension-six current-kernel EFT "
        "contract closes mathematical G3 exactly; its release verification "
        "and the original renormalizable G3 remain open."
        if parallel_eft_g3_closed
        else " The parallel EFT G3 certificate is missing or invalid."
    )
    verdict += (
        " The same EFT closes mathematical G4 with exact Hessian rank/nullity "
        "448/38; EFT release G4 and authoritative renormalizable G4 remain open."
        if parallel_eft_g4_closed
        else " The parallel EFT G4 certificate is missing or invalid."
    )
    verdict += (
        " It also closes mathematical G5 by the frozen full-field SOS lower "
        "bound plus the PSD dimension-six operator; EFT release G5 remains "
        "open and authoritative renormalizable G5 remains contract-blocked."
        if parallel_eft_g5_closed
        else " The parallel EFT G5 certificate is missing or invalid."
    )
    verdict += (
        " Its exact normalized tree-level scalar spectrum closes mathematical "
        "G6: 486 real modes split into 37 gauge tangents, one physical PQ axion, "
        "and 448 strictly positive massive modes with complete residual-group and "
        "mixing provenance. EFT release G6 and authoritative renormalizable G6 "
        "remain false."
        if parallel_eft_g6_closed
        else " The parallel EFT G6 spectrum gate is missing or invalid."
    )
    return {
        "status": status,
        "overall_state": overall_state,
        "model_contract_id": ledger.AUTHORITATIVE_CONTRACT_ID,
        "contract_consistent": gate_report["contract_consistent"],
        "scientific_blockers": gate_report["scientific_blockers"],
        "n_checks": len(checks),
        "n_failed": len(audit_failures),
        "failures": audit_failures,
        "audit_failures": audit_failures,
        "critical_path": critical_path,
        "dependencies": DEPENDENCIES,
        "gates": gates,
        "tasks": tasks,
        "recent_milestones": MILESTONES,
        "model_contract_reports": gate_report["model_contract_reports"],
        "historical_option_c_subtheorems": historical,
        "gauged_u1x_scalar_subtheorems": gauged,
        "gauged_u1x_g3_constructive_frontier": g3_frontier,
        "renormalizable_G1_component_tensor_resolution": {
            "theorem": G1_COMPONENT_TENSOR_JSON.name,
            "source": G1_COMPONENT_TENSOR_SOURCE.name,
            "source_bound": direct_g1_component_tensor["source_bound"],
            "raw_sha256": g1_component_tensor_raw_sha256,
            "expected_raw_sha256": G1_COMPONENT_TENSOR_RAW_SHA256,
            "core_sha256": g1_component_tensor.get("core_sha256"),
            "expected_core_sha256": G1_COMPONENT_TENSOR_CORE_SHA256,
            "source_raw_sha256": g1_component_tensor_source_raw_sha256,
            "expected_source_raw_sha256": G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256,
            "mathematical_G1_closed": mathematical_g1_component_tensor_closed,
            "authoritative_G1_promoted_closed": False,
            "release_G1_verified": False,
            "downstream_integration_completed": direct_g1_component_tensor[
                "downstream_integration_completed"
            ],
            "release_blockers": direct_g1_component_tensor["release_blockers"],
        },
        "parallel_EFT_G3_resolution": {
            "gate": EFT_G3_JSON.name,
            "source_bound": direct_parallel_eft_g3["source_bound"],
            "raw_sha256": eft_g3_raw_sha256,
            "expected_raw_sha256": EFT_G3_RAW_SHA256,
            "core_sha256": eft_g3.get("core_sha256"),
            "expected_core_sha256": EFT_G3_CORE_SHA256,
            "mathematical_G3_closed": parallel_eft_g3_closed,
            "original_renormalizable_G3_closed": False,
            "release_G3_verified": eft_classification.get(
                "release_G3_verified_for_EFT_model"
            ),
            "G4_closed": False,
        },
        "parallel_EFT_G4_resolution": {
            "gate": EFT_G4_JSON.name,
            "source_bound": direct_parallel_eft_g4["source_bound"],
            "raw_sha256": eft_g4_raw_sha256,
            "expected_raw_sha256": EFT_G4_RAW_SHA256,
            "core_sha256": eft_g4.get("core_sha256"),
            "expected_core_sha256": EFT_G4_CORE_SHA256,
            "mathematical_G4_closed": parallel_eft_g4_closed,
            "original_renormalizable_G4_closed": False,
            "release_G4_verified": False,
            "integration_completed": direct_parallel_eft_g4["checks"][
                "parallel_integration_completed"
            ],
            "release_blockers": direct_parallel_eft_g4["release_blockers"],
        },
        "parallel_EFT_G5_resolution": {
            "gate": EFT_G5_JSON.name,
            "source_bound": direct_parallel_eft_g5["source_bound"],
            "raw_sha256": eft_g5_raw_sha256,
            "expected_raw_sha256": EFT_G5_RAW_SHA256,
            "core_sha256": eft_g5.get("core_sha256"),
            "expected_core_sha256": EFT_G5_CORE_SHA256,
            "mathematical_G5_closed": parallel_eft_g5_closed,
            "original_renormalizable_G5_closed": False,
            "release_G5_verified": False,
            "new_SOS_claimed": False,
            "integration_completed": direct_parallel_eft_g5["checks"][
                "parallel_integration_completed"
            ],
            "release_blockers": direct_parallel_eft_g5["release_blockers"],
        },
        "parallel_EFT_G6_resolution": {
            "gate": EFT_G6_JSON.name,
            "source_bound": direct_parallel_eft_g6["source_bound"],
            "raw_sha256": eft_g6_raw_sha256,
            "expected_raw_sha256": EFT_G6_RAW_SHA256,
            "core_sha256": eft_g6.get("core_sha256"),
            "expected_core_sha256": EFT_G6_CORE_SHA256,
            "gate_source_raw_sha256": direct_parallel_eft_g6[
                "gate_source_raw_sha256"
            ],
            "expected_gate_source_raw_sha256": (
                ledger.FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256
            ),
            "spectrum_core_sha256": direct_parallel_eft_g6[
                "spectrum_core_sha256"
            ],
            "expected_spectrum_core_sha256": (
                ledger.FINAL_G6_EFT_SPECTRUM_CORE_SHA256
            ),
            "mathematical_G6_closed": parallel_eft_g6_closed,
            "original_renormalizable_G6_closed": False,
            "release_G6_verified": False,
            "authoritative_G6_gate_mutated": False,
            "integration_completed": direct_parallel_eft_g6[
                "parallel_integration_completed"
            ],
            "spectrum_summary": direct_parallel_eft_g6["spectrum_summary"],
            "release_blockers": direct_parallel_eft_g6["release_blockers"],
        },
        "summary": gate_report["summary"],
        "new_physics_policy": (
            "Historical calculations remain scoped subtheorems. No whole-model "
            "validation, exclusion, or discovery claim is permitted until every "
            "authoritative gauged-U(1)_X gate is complete."
        ),
        "checks": checks,
        "verdict": verdict,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    return _build_report_from_ledger(ledger.build_report())


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SO(10) axion v20 - contract-aware G1-G8 roadmap",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Critical path",
        "",
        "`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`",
        "",
        "## Parallel dimension-six EFT classifications",
        "",
        (
            "- Mathematical G3/G4/G5/G6: "
            f"`{report['parallel_EFT_G3_resolution']['mathematical_G3_closed']}`/"
            f"`{report['parallel_EFT_G4_resolution']['mathematical_G4_closed']}`/"
            f"`{report['parallel_EFT_G5_resolution']['mathematical_G5_closed']}`/"
            f"`{report['parallel_EFT_G6_resolution']['mathematical_G6_closed']}`"
        ),
        "- Release G3/G4/G5/G6: `False`/`False`/`False`/`False`",
        "- Authoritative renormalizable G3/G4/G5/G6 are not promoted.",
        "",
        "## Gate ledger",
        "",
        "| Gate | Status | Immediate work |",
        "|---|---:|---|",
    ]
    for gate, row in report["gates"].items():
        immediate = (
            ", ".join(row["authoritative_closed_scope"])
            if row["status"] == ledger.STATUS_CLOSED
            else row["open_scope"][0]
        )
        lines.append(f"| {gate} | {row['status']} | {immediate} |")
    lines.extend(["", "## Execution tasks", ""])
    for task in report["tasks"]:
        lines.extend(
            [
                f"### {task['id']} - `{task['status']}`",
                "",
                f"- Wave: `{task['wave']}`",
                f"- Deliverable: {task['deliverable']}",
                f"- Acceptance: {task['acceptance']}",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
