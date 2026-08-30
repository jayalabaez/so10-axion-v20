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
G2_MATHEMATICAL_JSON = ROOT / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
G2_MATHEMATICAL_SOURCE = ROOT / "exact_gauged_u1x_g2_mathematical_closure_v20.py"
G2_MATHEMATICAL_CORE_SHA256 = (
    "eb11744d0dbc9ceb883e8a6063177d8e3e370b1dcdc2c4e3eba97541b53d8fc4"
)
G2_MATHEMATICAL_RAW_SHA256 = (
    "de105a206685a236dcddc4cb70d98d756d87b9641e02150c41493897e01f7ff0"
)
G2_MATHEMATICAL_SOURCE_RAW_SHA256 = (
    "5f56a55a7c9597918c530ad6c77252ed161a206ad0dffbf25651e32f4f590a8b"
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
    "3b06ae240c7fce18723f0ce77966e894e688dee65f56859239ff5cf552b1323c"
)
EFT_G6_RAW_SHA256 = (
    "8bd98401ed6e2540ae7968a5b6a51a8e49abd98943252dec159c873d73a13f6c"
)
EFT_G7_NONIDENTIFIABILITY_JSON = (
    ROOT / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
)
EFT_G7_NONIDENTIFIABILITY_SOURCE = (
    ROOT / "exact_eft_g7_threshold_nonidentifiability_v20.py"
)
EFT_G7_NONIDENTIFIABILITY_CORE_SHA256 = (
    "93a8ea1abeb3cec2521cb043057b29646bd9c368f8e8bcc7e2d819f42a7dc741"
)
EFT_G7_NONIDENTIFIABILITY_RAW_SHA256 = (
    "778f96c8760a43be5214b215e08a6308d6198b84ebff9edd7729e75203b13cae"
)
EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256 = (
    "16e4a011e759df3a31664bcac2711b5270598551f1e2791c8f629f9bb6483406"
)
G6_SM_PROVENANCE_JSON = ledger.G6_SM_PROVENANCE_JSON
G6_SM_PROVENANCE_SOURCE = ledger.G6_SM_PROVENANCE_SOURCE
G6_G7_PARAMETERIZED_MATCHING_JSON = ledger.G6_G7_PARAMETERIZED_MATCHING_JSON
G6_G7_PARAMETERIZED_MATCHING_SOURCE = ledger.G6_G7_PARAMETERIZED_MATCHING_SOURCE
AUTHORITATIVE_GAUGE_BETAS_JSON = ledger.AUTHORITATIVE_GAUGE_BETAS_JSON
AUTHORITATIVE_GAUGE_BETAS_SOURCE = ledger.AUTHORITATIVE_GAUGE_BETAS_SOURCE
PYRATE3_GAUGE_REPLAY_JSON = ledger.PYRATE3_GAUGE_REPLAY_JSON
PYRATE3_GAUGE_REPLAY_SOURCE = ledger.PYRATE3_GAUGE_REPLAY_SOURCE
PYRATE3_GAUGE_REPLAY_MODEL = ledger.PYRATE3_GAUGE_REPLAY_MODEL
PYRATE3_GAUGE_REPLAY_DATA = ledger.PYRATE3_GAUGE_REPLAY_DATA
PHYSICAL_G7_COMPONENT_THRESHOLD_JSON = ledger.PHYSICAL_G7_COMPONENT_THRESHOLD_JSON
PHYSICAL_G7_COMPONENT_THRESHOLD_MD = ledger.PHYSICAL_G7_COMPONENT_THRESHOLD_MD
PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE = (
    ledger.PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE
)
PHYSICAL_G7_COMPONENT_THRESHOLD_TEST = ledger.PHYSICAL_G7_COMPONENT_THRESHOLD_TEST
NORMALIZED_YUKAWA_CGCS_JSON = ledger.NORMALIZED_YUKAWA_CGCS_JSON
NORMALIZED_YUKAWA_CGCS_MD = ledger.NORMALIZED_YUKAWA_CGCS_MD
NORMALIZED_YUKAWA_CGCS_SOURCE = ledger.NORMALIZED_YUKAWA_CGCS_SOURCE
NORMALIZED_YUKAWA_CGCS_TEST = ledger.NORMALIZED_YUKAWA_CGCS_TEST
PHYSICAL_SM_VACUUM_JSON = ledger.PHYSICAL_SM_VACUUM_JSON
PHYSICAL_SM_VACUUM_MD = ledger.PHYSICAL_SM_VACUUM_MD
PHYSICAL_SM_VACUUM_SOURCE = ledger.PHYSICAL_SM_VACUUM_SOURCE
PHYSICAL_SM_VACUUM_TEST = ledger.PHYSICAL_SM_VACUUM_TEST
PHYSICAL_SM_SOURCE_EQUALITY_JSON = ledger.PHYSICAL_SM_SOURCE_EQUALITY_JSON
PHYSICAL_SM_SOURCE_EQUALITY_MD = ledger.PHYSICAL_SM_SOURCE_EQUALITY_MD
PHYSICAL_SM_SOURCE_EQUALITY_SOURCE = ledger.PHYSICAL_SM_SOURCE_EQUALITY_SOURCE
PHYSICAL_SM_SOURCE_EQUALITY_TEST = ledger.PHYSICAL_SM_SOURCE_EQUALITY_TEST
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON = (
    ledger.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD = (
    ledger.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE = (
    ledger.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST = (
    ledger.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON = ledger.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD = ledger.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE = ledger.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST = ledger.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST
PHYSICAL_SM_LAST_SIX_HESSIANS_JSON = ledger.PHYSICAL_SM_LAST_SIX_HESSIANS_JSON
PHYSICAL_SM_LAST_SIX_HESSIANS_MD = ledger.PHYSICAL_SM_LAST_SIX_HESSIANS_MD
PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE = ledger.PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE
PHYSICAL_SM_LAST_SIX_HESSIANS_TEST = ledger.PHYSICAL_SM_LAST_SIX_HESSIANS_TEST
PHYSICAL_SM_37_ROW_AGGREGATE_JSON = ledger.PHYSICAL_SM_37_ROW_AGGREGATE_JSON
PHYSICAL_SM_37_ROW_AGGREGATE_MD = ledger.PHYSICAL_SM_37_ROW_AGGREGATE_MD
PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE = ledger.PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE
PHYSICAL_SM_37_ROW_AGGREGATE_TEST = ledger.PHYSICAL_SM_37_ROW_AGGREGATE_TEST
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON = ledger.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD = ledger.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE = ledger.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST = ledger.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON = ledger.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD = ledger.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE = ledger.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST = ledger.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST
PHYSICAL_SM_HEAVY_VECTOR_JSON = ledger.PHYSICAL_SM_HEAVY_VECTOR_JSON
PHYSICAL_SM_HEAVY_VECTOR_MD = ledger.PHYSICAL_SM_HEAVY_VECTOR_MD
PHYSICAL_SM_HEAVY_VECTOR_SOURCE = ledger.PHYSICAL_SM_HEAVY_VECTOR_SOURCE
PHYSICAL_SM_HEAVY_VECTOR_TEST = ledger.PHYSICAL_SM_HEAVY_VECTOR_TEST
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON = (
    ledger.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD = ledger.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE = (
    ledger.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST = (
    ledger.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST
)
PHYSICAL_SM_VECTOR_RXI_JSON = ledger.PHYSICAL_SM_VECTOR_RXI_JSON
PHYSICAL_SM_VECTOR_RXI_MD = ledger.PHYSICAL_SM_VECTOR_RXI_MD
PHYSICAL_SM_VECTOR_RXI_SOURCE = ledger.PHYSICAL_SM_VECTOR_RXI_SOURCE
PHYSICAL_SM_VECTOR_RXI_TEST = ledger.PHYSICAL_SM_VECTOR_RXI_TEST
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON = (
    ledger.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD = (
    ledger.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE = (
    ledger.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST = (
    ledger.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST
)
PHYSICAL_SM_G6_G7_FRONTIER_JSON = ledger.PHYSICAL_SM_G6_G7_FRONTIER_JSON
PHYSICAL_SM_G6_G7_FRONTIER_MD = ledger.PHYSICAL_SM_G6_G7_FRONTIER_MD
PHYSICAL_SM_G6_G7_FRONTIER_SOURCE = ledger.PHYSICAL_SM_G6_G7_FRONTIER_SOURCE
PHYSICAL_SM_G6_G7_FRONTIER_TEST = ledger.PHYSICAL_SM_G6_G7_FRONTIER_TEST
PHYSICAL_SM_G8_FRONTIER_JSON = ledger.PHYSICAL_SM_G8_FRONTIER_JSON
PHYSICAL_SM_G8_FRONTIER_MD = ledger.PHYSICAL_SM_G8_FRONTIER_MD
PHYSICAL_SM_G8_FRONTIER_SOURCE = ledger.PHYSICAL_SM_G8_FRONTIER_SOURCE
PHYSICAL_SM_G8_FRONTIER_TEST = ledger.PHYSICAL_SM_G8_FRONTIER_TEST

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
            "installation and retain its v3 source-tree/runtime/log attestation"
        ),
        "acceptance": (
            "a fresh exact-X audit reports contract_consistent=True, native "
            "Gauge/Global/matter/LagrangianInput syntax, and v3 external evidence "
            "bound to the trusted SARAH tree, exact model, validation driver, "
            "resolved runtime, probe log, and process log"
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
            "SOURCE_BOUND_FULL_MATHEMATICAL_G2_POTENTIAL_COMPLETE__"
            "MODEL_CONTRACT_BLOCKED"
        ),
        "issue": 176,
        "deliverable": (
            "promote the source-bound complete 44/51/486 mathematical component "
            "potential after the executable contract closes"
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
            "t=1 for every real Phi210. For that historical fixed-H/Sigma "
            "frontier, global Sigma, general/full H, and its then-unassembled "
            "Hessian remained open. The current physical-SM branch instead has "
            "an exact source-derived 37-row Hessian; its complete global equality "
            "orbit and physical G3 remain open"
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
        "status": "BLOCKED__LOCAL_SOURCE_HESSIAN_CLOSED__GLOBAL_EQUALITY_SCALE_MASS_MIXING_POLE_THRESHOLD_AND_RELEASE_G6_OPEN",
        "issue": 106,
        "deliverable": (
            "retain the formal SU(3)_C x U(1)_89 factorization and the exact "
            "standard-SM stabilizer of the new reconstructed target together with "
            "its exact parameterized heavy-vector mass matrix, rank/kernel, sector "
            "resolution and conditional reconstructed tree scalar spectrum. Retain "
            "the exact source-derived all-37 Hessian theorem with stationarity, "
            "kernel/rank 38/448 and PSD strict modulo symmetry; classify the complete "
            "global equality orbit, fix absolute scales and couplings, construct full "
            "scalar and fermion mass/mixing matrices, solve pole self-energies, and "
            "complete all thresholds"
        ),
        "acceptance": (
            "standard SM generators annihilate every staged VEV and commute with "
            "the relevant mass pencils; all eigenmasses, irreps, mixings and "
            "uncertainties are complete"
        ),
    },
    {
        "id": "W5-G7-TWO-LOOP",
        "wave": 5,
        "gates": ["G7"],
        "status": "BLOCKED__PHYSICAL_G6_INPUT_AND_FULL_TWO_LOOP_MATCHING_OPEN",
        "issue": 126,
        "deliverable": (
            "retain the source-bound physical PS/SM matter branching, "
            "parameterized one-loop matter threshold kernel and independently "
            "checked non-Yukawa gauge flow together with the normalized SO(10) "
            "10/126bar/singlet representation CGCs; use the corrected physical G6 "
            "pole spectrum, then fix flavor tensors/boundaries and the explicit "
            "SARAH identical-Weyl contraction conversion. Retain the exact combined "
            "heavy-vector/FP-ghost/Goldstone MS-bar kernel and finite constant, but "
            "also retain the exact zero-background arbitrary-positive-R_xi vacuum "
            "determinant cancellation; derive background-covariant general-field "
            "sector determinants/heat-kernel replay, tree-to-pole conversion with "
            "a tadpole/VEV scheme, and a stationary pre-EW "
            "matching stage; then complete scalar/fermion thresholds, "
            "Yukawa/scalar/EFT running, absolute "
            "scale/Wilson matching and staged component thresholds"
        ),
        "acceptance": (
            "the full coupled RGE and physical matching systems agree in two "
            "independent implementations within declared tolerances"
        ),
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
    direct_exact_x_v3 = ledger._exact_x_v3_fail_closed_contract(
        gate_report.get("model_contract_reports", {}).get("exact_X", {}),
        source_raw_sha256=ledger._raw_file_sha256(ledger.EXACT_X_V3_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(ledger.EXACT_X_V3_TEST),
        json_raw_sha256=ledger._raw_file_sha256(ledger.EXACT_X_V3_JSON),
        markdown_raw_sha256=ledger._raw_file_sha256(ledger.EXACT_X_V3_MD),
        input_manifest_raw_sha256=ledger._raw_file_sha256(
            ledger.EXACT_X_V3_INPUT_MANIFEST
        ),
        trusted_sarah_manifest_raw_sha256=ledger._raw_file_sha256(
            ledger.EXACT_X_V3_TRUSTED_SARAH_MANIFEST
        ),
        external_validation_file_present=ledger.exact_x.EXTERNAL_VALIDATION.is_file(),
    )
    embedded_exact_x_v3 = gate_report.get("exact_X_v3_fail_closed_contract", {})
    exact_x_v3_bound = bool(
        (
            direct_exact_x_v3 == embedded_exact_x_v3
            and direct_exact_x_v3["source_bound"] is True
            and direct_exact_x_v3[
                "trusted_SARAH_4_15_3_source_tree_manifest_closed"
            ]
            is True
            and direct_exact_x_v3["external_v3_execution_attestation_present"]
            is False
            and direct_exact_x_v3["contract_consistent"] is False
            and direct_exact_x_v3["authoritative_G1_closed"] is False
            and gates["G1"]["status"] == ledger.STATUS_BLOCKED
        )
        or (
            gate_report.get("contract_consistent") is True
            and ledger._root_contract_evidence_complete(
                gate_report.get("model_contract_reports", {}).get("exact_X", {})
            )
            is True
            and direct_exact_x_v3 == embedded_exact_x_v3
            and embedded_exact_x_v3.get("source_bound") is True
            and embedded_exact_x_v3.get(
                "external_v3_execution_attestation_present"
            )
            is True
            and embedded_exact_x_v3.get("resolved_Wolfram_runtime_bound") is True
            and embedded_exact_x_v3.get("contract_consistent") is True
            and embedded_exact_x_v3.get("authoritative_G1_closed") is True
            and gates["G1"]["status"] == ledger.STATUS_CLOSED
        )
    )
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
    g2_mathematical = ledger._load_json_artifact(G2_MATHEMATICAL_JSON)
    g2_mathematical_raw_sha256 = ledger._raw_file_sha256(G2_MATHEMATICAL_JSON)
    g2_mathematical_source_raw_sha256 = ledger._raw_file_sha256(
        G2_MATHEMATICAL_SOURCE
    )
    direct_g2_mathematical = ledger._renormalizable_g2_mathematical_closure(
        g2_mathematical,
        raw_sha256=g2_mathematical_raw_sha256,
        source_raw_sha256=g2_mathematical_source_raw_sha256,
    )
    ledger_g2_mathematical = gate_report.get(
        "renormalizable_G2_mathematical_closure", {}
    )
    mathematical_g2_closed = bool(
        G2_MATHEMATICAL_CORE_SHA256
        == ledger.RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
        and G2_MATHEMATICAL_RAW_SHA256
        == ledger.RENORMALIZABLE_G2_MATHEMATICAL_RAW_SHA256
        and G2_MATHEMATICAL_SOURCE_RAW_SHA256
        == ledger.RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256
        and direct_g2_mathematical["source_bound"] is True
        and direct_g2_mathematical == ledger_g2_mathematical
        and direct_g2_mathematical[
            "mathematical_G2_closed_for_renormalizable_model"
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
    g6_provenance_report = ledger._load_json_artifact(G6_SM_PROVENANCE_JSON)
    direct_g6_provenance = ledger._g6_sm_provenance_audit(
        g6_provenance_report,
        raw_sha256=ledger._raw_file_sha256(G6_SM_PROVENANCE_JSON),
        source_raw_sha256=ledger._raw_file_sha256(G6_SM_PROVENANCE_SOURCE),
    )
    matching_report = ledger._load_json_artifact(G6_G7_PARAMETERIZED_MATCHING_JSON)
    direct_parameterized_matching = ledger._parameterized_g6_g7_matching(
        matching_report,
        raw_sha256=ledger._raw_file_sha256(G6_G7_PARAMETERIZED_MATCHING_JSON),
        source_raw_sha256=ledger._raw_file_sha256(
            G6_G7_PARAMETERIZED_MATCHING_SOURCE
        ),
    )
    direct_parallel_eft_g6 = ledger._parallel_eft_g6_spectrum(
        eft_g6,
        raw_sha256=eft_g6_raw_sha256,
        gate_source_raw_sha256=ledger._raw_file_sha256(EFT_G6_SOURCE),
        provenance_audit=direct_g6_provenance,
        parameterized_matching=direct_parameterized_matching,
    )
    ledger_parallel_eft_g6 = gate_report.get("parallel_EFT_G6_spectrum", {})
    formal_eft_g6_bound = bool(
        EFT_G6_CORE_SHA256 == ledger.FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256
        and EFT_G6_RAW_SHA256 == ledger.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256
        and direct_parallel_eft_g6["source_bound"] is True
        and ledger_parallel_eft_g6 == direct_parallel_eft_g6
        and direct_parallel_eft_g6[
            "formal_SU3_x_U1_89_tree_factorization_closed"
        ]
        is True
        and direct_parallel_eft_g6["mathematical_G6_closed_for_EFT_model"]
        is False
        and direct_g6_provenance
        == gate_report.get("G6_SM_provenance_audit", {})
        and direct_parameterized_matching
        == gate_report.get("G6_G7_parameterized_matching", {})
    )
    gauge_beta_report = ledger._load_json_artifact(AUTHORITATIVE_GAUGE_BETAS_JSON)
    direct_gauge_betas = ledger._authoritative_gauge_beta_subtheorem(
        gauge_beta_report,
        raw_sha256=ledger._raw_file_sha256(AUTHORITATIVE_GAUGE_BETAS_JSON),
        source_raw_sha256=ledger._raw_file_sha256(AUTHORITATIVE_GAUGE_BETAS_SOURCE),
    )
    gauge_beta_subtheorem_bound = bool(
        direct_gauge_betas
        == gate_report.get("authoritative_gauge_beta_subtheorem", {})
        and direct_gauge_betas["source_bound"] is True
        and direct_gauge_betas[
            "exact_nonyukawa_two_loop_gauge_polynomial_closed"
        ]
        is True
        and direct_gauge_betas["mathematical_G7_closed"] is False
    )
    pyrate_replay_report = ledger._load_json_artifact(PYRATE3_GAUGE_REPLAY_JSON)
    direct_pyrate_replay = ledger._pyrate3_gauge_replay_subtheorem(
        pyrate_replay_report,
        raw_sha256=ledger._raw_file_sha256(PYRATE3_GAUGE_REPLAY_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PYRATE3_GAUGE_REPLAY_SOURCE),
        model_raw_sha256=ledger._raw_file_sha256(PYRATE3_GAUGE_REPLAY_MODEL),
        data_raw_sha256=ledger._raw_file_sha256(PYRATE3_GAUGE_REPLAY_DATA),
    )
    pyrate_replay_bound = bool(
        direct_pyrate_replay
        == gate_report.get("independent_PyRATE3_gauge_replay", {})
        and direct_pyrate_replay["source_bound"] is True
        and direct_pyrate_replay[
            "second_implementation_for_scoped_gauge_subtheorem"
        ]
        is True
        and direct_pyrate_replay["mathematical_G7_closed"] is False
    )
    eft_g7_nonidentifiability = ledger._load_json_artifact(
        EFT_G7_NONIDENTIFIABILITY_JSON
    )
    eft_g7_nonidentifiability_raw_sha256 = ledger._raw_file_sha256(
        EFT_G7_NONIDENTIFIABILITY_JSON
    )
    eft_g7_nonidentifiability_source_raw_sha256 = ledger._raw_file_sha256(
        EFT_G7_NONIDENTIFIABILITY_SOURCE
    )
    direct_eft_g7_nonidentifiability = (
        ledger._parallel_eft_g7_nonidentifiability(
            eft_g7_nonidentifiability,
            raw_sha256=eft_g7_nonidentifiability_raw_sha256,
            source_raw_sha256=eft_g7_nonidentifiability_source_raw_sha256,
        )
    )
    ledger_eft_g7_nonidentifiability = gate_report.get(
        "parallel_EFT_G7_nonidentifiability", {}
    )
    eft_g7_nonidentifiability_bound = bool(
        EFT_G7_NONIDENTIFIABILITY_CORE_SHA256
        == ledger.EFT_G7_NONIDENTIFIABILITY_CORE_SHA256
        and EFT_G7_NONIDENTIFIABILITY_RAW_SHA256
        == ledger.EFT_G7_NONIDENTIFIABILITY_RAW_SHA256
        and EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256
        == ledger.EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256
        and direct_eft_g7_nonidentifiability["source_bound"] is True
        and direct_eft_g7_nonidentifiability
        == ledger_eft_g7_nonidentifiability
        and direct_eft_g7_nonidentifiability[
            "formal_U1_89_abstract_restriction_noninjectivity_proved"
        ]
        is True
        and direct_eft_g7_nonidentifiability[
            "exact_physical_EFT_G7_input_nonidentifiability_proved"
        ]
        is False
        and direct_eft_g7_nonidentifiability[
            "historical_electroweak_lift_interpretation_valid"
        ]
        is False
        and direct_eft_g7_nonidentifiability[
            "downstream_integration_completed"
        ]
        is True
    )
    physical_g7_report = ledger._load_json_artifact(
        PHYSICAL_G7_COMPONENT_THRESHOLD_JSON
    )
    direct_physical_g7 = ledger._physical_g7_component_threshold_contract(
        physical_g7_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_G7_COMPONENT_THRESHOLD_JSON),
        source_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE
        ),
        test_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_TEST
        ),
        markdown_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_MD
        ),
    )
    physical_g7_bound = bool(
        direct_physical_g7
        == gate_report.get("physical_G7_component_threshold_contract", {})
        and direct_physical_g7["source_bound"] is True
        and direct_physical_g7["physical_PS_SM_matter_branching_closed"] is True
        and direct_physical_g7[
            "parameterized_one_loop_matter_threshold_kernel_closed"
        ]
        is True
        and direct_physical_g7["physical_G7_closed"] is False
        and direct_physical_g7["mathematical_G7_closed"] is False
        and direct_physical_g7["release_G7_verified"] is False
        and direct_physical_g7["authoritative_renormalizable_G7_closed"] is False
    )
    yukawa_cgcs_report = ledger._load_json_artifact(NORMALIZED_YUKAWA_CGCS_JSON)
    direct_yukawa_cgcs = ledger._normalized_so10_yukawa_cgc_contract(
        yukawa_cgcs_report,
        raw_sha256=ledger._raw_file_sha256(NORMALIZED_YUKAWA_CGCS_JSON),
        source_raw_sha256=ledger._raw_file_sha256(NORMALIZED_YUKAWA_CGCS_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(NORMALIZED_YUKAWA_CGCS_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(NORMALIZED_YUKAWA_CGCS_MD),
    )
    yukawa_cgcs_bound = bool(
        direct_yukawa_cgcs
        == gate_report.get("normalized_SO10_Yukawa_CGC_contract", {})
        and direct_yukawa_cgcs["source_bound"] is True
        and direct_yukawa_cgcs["all_declared_representation_CGCs_closed"] is True
        and direct_yukawa_cgcs["full_one_two_loop_Yukawa_betas_closed"] is False
        and direct_yukawa_cgcs["physical_threshold_matching_and_running_closed"]
        is False
        and direct_yukawa_cgcs["physical_G7_closed"] is False
        and direct_yukawa_cgcs["mathematical_G7_closed"] is False
        and direct_yukawa_cgcs["release_G7_verified"] is False
    )
    physical_sm_report = ledger._load_json_artifact(PHYSICAL_SM_VACUUM_JSON)
    direct_physical_sm = ledger._physical_sm_vacuum_truth_overlay(
        physical_sm_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VACUUM_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VACUUM_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VACUUM_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VACUUM_MD),
    )
    physical_sm_bound = bool(
        direct_physical_sm
        == gate_report.get("physical_SM_vacuum_truth_overlay", {})
        and direct_physical_sm["source_bound"] is True
        and direct_physical_sm["physical_SM_target_exactly_constructed"] is True
        and direct_physical_sm["standard_SU3C_x_U1em_stabilizer_proved"] is True
        and direct_physical_sm["old_selected_EFT_stabilizer_label_superseded"]
        is True
        and direct_physical_sm["physical_SM_G3_closed"] is False
        and direct_physical_sm["physical_SM_G4_closed"] is False
        and direct_physical_sm["physical_SM_G5_closed"] is False
        and direct_physical_sm["physical_SM_G6_closed"] is False
        and direct_physical_sm["physical_SM_G7_closed"] is False
    )
    source_equality_report = ledger._load_json_artifact(
        PHYSICAL_SM_SOURCE_EQUALITY_JSON
    )
    direct_source_equality = (
        ledger._physical_sm_source_algebra_equality_frontier_contract(
            source_equality_report,
            raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_SOURCE_EQUALITY_JSON
            ),
            source_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_SOURCE_EQUALITY_SOURCE
            ),
            test_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_SOURCE_EQUALITY_TEST
            ),
            markdown_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_SOURCE_EQUALITY_MD
            ),
        )
    )
    source_equality_bound = bool(
        direct_source_equality
        == gate_report.get(
            "physical_SM_source_algebra_equality_frontier", {}
        )
        and direct_source_equality["source_bound"] is True
        and direct_source_equality[
            "radial_stationary_equality_classified_exactly"
        ]
        is True
        and direct_source_equality["radial_gcd"] == "t - 1"
        and direct_source_equality[
            "direct_source_algebra_stationary_Hessian_available"
        ]
        is False
        and direct_source_equality[
            "complete_nonradial_equality_orbit_proved"
        ]
        is False
        and direct_source_equality["physical_SM_G3_closed"] is False
        and direct_source_equality["physical_SM_G4_closed"] is False
        and direct_source_equality["physical_SM_G5_closed"] is False
    )
    five_amplitude_report = ledger._load_json_artifact(
        PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
    )
    direct_five_amplitude = ledger._physical_sm_five_amplitude_equality_contract(
        five_amplitude_report,
        raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
        ),
        source_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE
        ),
        test_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST
        ),
        markdown_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD
        ),
    )
    five_amplitude_bound = bool(
        direct_five_amplitude
        == gate_report.get("physical_SM_five_amplitude_equality_contract", {})
        and direct_five_amplitude["source_bound"] is True
        and direct_five_amplitude[
            "five_real_amplitude_slice_stationary_equality_classified"
        ]
        is True
        and direct_five_amplitude["exact_real_discrete_sign_variant_count"]
        == 16
        and direct_five_amplitude[
            "full_486_field_stationary_equality_classified"
        ]
        is False
        and direct_five_amplitude[
            "continuous_symmetry_orbit_equivalence_of_16_variants_proved"
        ]
        is False
        and direct_five_amplitude[
            "direct_source_algebra_full_486_Hessian_available"
        ]
        is False
        and direct_five_amplitude["physical_SM_G3_closed"] is False
        and direct_five_amplitude["physical_SM_G4_closed"] is False
        and direct_five_amplitude["physical_SM_G5_closed"] is False
    )
    hard_projector_report = ledger._load_json_artifact(
        PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON
    )
    direct_hard_projectors = ledger._physical_sm_hard_projector_hessians_contract(
        hard_projector_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD),
    )
    hard_projectors_bound = bool(
        direct_hard_projectors
        == gate_report.get("physical_SM_hard_projector_Hessians_contract", {})
        and direct_hard_projectors["source_bound"] is True
        and direct_hard_projectors["exact_source_Hessian_row_count"] == 10
        and direct_hard_projectors["remaining_active_row_count"] == 27
        and direct_hard_projectors["all_37_active_source_Hessians_closed"] is False
        and direct_hard_projectors["physical_SM_G3_closed"] is False
        and direct_hard_projectors["physical_SM_G4_closed"] is False
        and direct_hard_projectors["physical_SM_G5_closed"] is False
    )
    last_six_report = ledger._load_json_artifact(PHYSICAL_SM_LAST_SIX_HESSIANS_JSON)
    direct_last_six = ledger._physical_sm_last_six_hessians_contract(
        last_six_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_MD),
    )
    last_six_bound = bool(
        direct_last_six
        == gate_report.get("physical_SM_last_six_Hessians_contract", {})
        and direct_last_six["source_bound"] is True
        and direct_last_six["exact_last_six_source_Hessians_closed"] is True
        and direct_last_six["all_37_active_source_Hessians_available"] is True
        and direct_last_six[
            "exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"
        ]
        is False
        and all(
            direct_last_six[f"physical_SM_{gate}_closed"] is False
            for gate in ("G3", "G4", "G5")
        )
    )
    aggregate_report = ledger._load_json_artifact(PHYSICAL_SM_37_ROW_AGGREGATE_JSON)
    direct_aggregate = ledger._physical_sm_37_row_aggregate_contract(
        aggregate_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_MD),
    )
    aggregate_bound = bool(
        direct_aggregate
        == gate_report.get("physical_SM_37_row_aggregate_contract", {})
        and direct_aggregate["source_bound"] is True
        and direct_aggregate["all_37_active_Hessians_source_derived"] is True
        and direct_aggregate[
            "exact_source_aggregate_value_minus_one_and_stationary"
        ]
        is True
        and direct_aggregate["exact_source_aggregate_kernel_dimension"] == 38
        and direct_aggregate["exact_source_aggregate_rank"] == 448
        and direct_aggregate[
            "exact_source_aggregate_PSD_and_strict_mod_symmetry"
        ]
        is True
        and direct_aggregate[
            "source_bound_local_stationary_Hessian_problem_complete"
        ]
        is True
        and direct_aggregate["full_486_global_equality_orbit_closed"] is False
        and all(
            direct_aggregate[f"physical_SM_{gate}_closed"] is False
            for gate in ("G3", "G4", "G5")
        )
    )
    local_orbit_report = ledger._load_json_artifact(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON)
    direct_local_orbit = ledger._physical_sm_local_equality_orbit_contract(
        local_orbit_report,
        portable_lf_sha256=ledger._file_sha256(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON),
        source_portable_lf_sha256=ledger._file_sha256(
            PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE
        ),
        test_portable_lf_sha256=ledger._file_sha256(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST),
        markdown_portable_lf_sha256=ledger._file_sha256(
            PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD
        ),
    )
    local_orbit_bound = bool(
        direct_local_orbit
        == gate_report.get("physical_SM_local_equality_orbit_contract", {})
        and direct_local_orbit["source_bound"] is True
        and direct_local_orbit["full_486_local_stationary_orbit_classified"] is True
        and direct_local_orbit[
            "full_486_local_stationary_equality_orbit_classified"
        ]
        is True
        and direct_local_orbit[
            "all_16_sign_variants_one_continuous_K_orbit"
        ]
        is True
        and direct_local_orbit["target_orbit_strict_local_minimum_mod_K"] is True
        and direct_local_orbit["quantitative_neighborhood_radius_proved"] is False
        and direct_local_orbit[
            "complete_486_global_equality_orbit_classified"
        ]
        is False
        and all(
            direct_local_orbit[f"physical_SM_{gate}_closed"] is False
            for gate in ("G3", "G4", "G5")
        )
    )
    branch_mismatch_report = ledger._load_json_artifact(
        PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON
    )
    direct_branch_mismatch = ledger._physical_sm_g4_g5_branch_mismatch_contract(
        branch_mismatch_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON),
        source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD),
    )
    branch_mismatch_bound = bool(
        direct_branch_mismatch
        == gate_report.get("physical_SM_G4_G5_branch_mismatch_contract", {})
        and direct_branch_mismatch["source_bound"] is True
        and direct_branch_mismatch["exact_branch_mismatch_proved"] is True
        and direct_branch_mismatch["unit_rescaling_case_count"] == 101
        and direct_branch_mismatch["global_no_go_for_other_physical_EW_branches"] is False
        and all(
            direct_branch_mismatch[f"physical_SM_G{gate}_closed"] is False
            for gate in range(4, 9)
        )
    )
    heavy_vector_report = ledger._load_json_artifact(
        PHYSICAL_SM_HEAVY_VECTOR_JSON
    )
    direct_heavy_vectors = ledger._physical_sm_heavy_vector_mass_contract(
        heavy_vector_report,
        raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HEAVY_VECTOR_JSON),
        source_raw_sha256=ledger._raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_SOURCE
        ),
        test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HEAVY_VECTOR_TEST),
        markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_HEAVY_VECTOR_MD),
    )
    heavy_vectors_bound = bool(
        direct_heavy_vectors
        == gate_report.get("physical_SM_heavy_vector_mass_contract", {})
        and direct_heavy_vectors["source_bound"] is True
        and direct_heavy_vectors[
            "exact_parameterized_tree_vector_mass_matrix_closed"
        ]
        is True
        and direct_heavy_vectors[
            "exact_vector_rank_kernel_and_Goldstone_image_closed"
        ]
        is True
        and direct_heavy_vectors[
            "parameterized_vector_threshold_log_inputs_closed"
        ]
        is True
        and direct_heavy_vectors["physical_G6_closed"] is False
        and direct_heavy_vectors["physical_G7_closed"] is False
    )
    heavy_vector_msbar_report = ledger._load_json_artifact(
        PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON
    )
    direct_heavy_vector_msbar = (
        ledger._physical_sm_heavy_vector_msbar_matching_contract(
            heavy_vector_msbar_report,
            raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON
            ),
            source_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE
            ),
            test_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST
            ),
            markdown_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD
            ),
        )
    )
    heavy_vector_msbar_bound = bool(
        direct_heavy_vector_msbar
        == gate_report.get(
            "physical_SM_heavy_vector_MSbar_matching_contract", {}
        )
        and direct_heavy_vector_msbar["source_bound"] is True
        and direct_heavy_vector_msbar[
            "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
        ]
        is True
        and direct_heavy_vector_msbar["finite_MSbar_vector_constant_closed"]
        is True
        and direct_heavy_vector_msbar[
            "arbitrary_Rxi_sector_resolved_matching_closed"
        ]
        is False
        and direct_heavy_vector_msbar["pole_mass_conversion_closed"] is False
        and direct_heavy_vector_msbar["SM_symmetric_pre_EW_matching_closed"]
        is False
        and direct_heavy_vector_msbar["physical_G6_closed"] is False
        and direct_heavy_vector_msbar["physical_G7_closed"] is False
    )
    vector_rxi_report = ledger._load_json_artifact(PHYSICAL_SM_VECTOR_RXI_JSON)
    direct_vector_rxi = (
        ledger._physical_sm_vector_rxi_vacuum_cancellation_contract(
            vector_rxi_report,
            raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VECTOR_RXI_JSON),
            source_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_VECTOR_RXI_SOURCE
            ),
            test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_VECTOR_RXI_TEST),
            markdown_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_VECTOR_RXI_MD
            ),
        )
    )
    vector_rxi_bound = bool(
        direct_vector_rxi
        == gate_report.get(
            "physical_SM_vector_Rxi_vacuum_cancellation_contract", {}
        )
        and direct_vector_rxi["source_bound"] is True
        and direct_vector_rxi[
            "zero_background_Rxi_vacuum_determinant_cancellation_closed"
        ]
        is True
        and direct_vector_rxi["all_37_broken_directions_closed"] is True
        and direct_vector_rxi[
            "background_covariant_heat_kernel_matching_closed"
        ]
        is False
        and direct_vector_rxi[
            "sector_resolved_general_background_determinants_closed"
        ]
        is False
        and direct_vector_rxi["physical_G6_closed"] is False
        and direct_vector_rxi["physical_G7_closed"] is False
    )
    conditional_scalar_report = ledger._load_json_artifact(
        CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON
    )
    direct_conditional_scalar = (
        ledger._conditional_physical_sm_eft_hessian_spectrum_contract(
            conditional_scalar_report,
            raw_sha256=ledger._raw_file_sha256(
                CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON
            ),
            source_raw_sha256=ledger._raw_file_sha256(
                CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE
            ),
            test_raw_sha256=ledger._raw_file_sha256(
                CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST
            ),
            markdown_raw_sha256=ledger._raw_file_sha256(
                CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD
            ),
        )
    )
    conditional_scalar_bound = bool(
        direct_conditional_scalar
        == gate_report.get(
            "conditional_physical_SM_EFT_Hessian_spectrum_contract", {}
        )
        and direct_conditional_scalar["source_bound"] is True
        and direct_conditional_scalar[
            "conditional_reconstructed_tree_scalar_spectrum_closed"
        ]
        is True
        and direct_conditional_scalar[
            "source_algebra_derived_tree_scalar_spectrum_closed"
        ]
        is False
        and direct_conditional_scalar["physical_scalar_pole_spectrum_closed"]
        is False
        and direct_conditional_scalar["physical_G6_closed"] is False
    )
    closure_frontier_report = ledger._load_json_artifact(
        PHYSICAL_SM_G6_G7_FRONTIER_JSON
    )
    direct_closure_frontier = (
        ledger._physical_sm_g6_g7_closure_frontier_contract(
            closure_frontier_report,
            raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_G6_G7_FRONTIER_JSON
            ),
            source_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_G6_G7_FRONTIER_SOURCE
            ),
            test_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_G6_G7_FRONTIER_TEST
            ),
            markdown_raw_sha256=ledger._raw_file_sha256(
                PHYSICAL_SM_G6_G7_FRONTIER_MD
            ),
        )
    )
    closure_frontier_bound = bool(
        direct_closure_frontier
        == gate_report.get("physical_SM_G6_G7_closure_frontier_contract", {})
        and direct_closure_frontier["source_bound"] is True
        and direct_closure_frontier["continuous_nonidentifiability_proved"]
        is True
        and direct_closure_frontier[
            "minimal_closure_path_machine_readable"
        ]
        is True
        and direct_closure_frontier["unique_pole_spectrum"] is False
        and direct_closure_frontier["unique_threshold_vector"] is False
        and direct_closure_frontier["unique_full_RGE_trajectory"] is False
        and direct_closure_frontier["physical_G6_closed"] is False
        and direct_closure_frontier["physical_G7_closed"] is False
    )
    g8_frontier_report = ledger._load_json_artifact(PHYSICAL_SM_G8_FRONTIER_JSON)
    direct_g8_frontier = (
        ledger._physical_sm_g8_identifiability_frontier_contract(
            g8_frontier_report,
            raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G8_FRONTIER_JSON),
            source_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G8_FRONTIER_SOURCE),
            test_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G8_FRONTIER_TEST),
            markdown_raw_sha256=ledger._raw_file_sha256(PHYSICAL_SM_G8_FRONTIER_MD),
        )
    )
    g8_frontier_bound = bool(
        direct_g8_frontier
        == gate_report.get("physical_SM_G8_identifiability_frontier_contract", {})
        and direct_g8_frontier["source_bound"] is True
        and direct_g8_frontier["canonical_G8_contract_audited"] is True
        and direct_g8_frontier[
            "continuous_absolute_scale_nonidentifiability_proved"
        ]
        is True
        and direct_g8_frontier[
            "flavor_and_interference_nonidentifiability_audited"
        ]
        is True
        and direct_g8_frontier[
            "repository_frozen_PDG_2025_single_channel_constraint_verified"
        ]
        is True
        and direct_g8_frontier["minimal_exhibited_joint_free_real_dimension"]
        == 1
        and direct_g8_frontier["unique_proton_lifetime_or_distribution"] is False
        and direct_g8_frontier["physical_G8_closed"] is False
        and direct_g8_frontier["release_G8_verified"] is False
        and direct_g8_frontier["authoritative_G8_closed"] is False
    )
    direct_recalculated_g7_inputs = (
        ledger._physical_g7_recalculated_input_resolution(
            direct_physical_g7,
            direct_yukawa_cgcs,
            direct_heavy_vectors,
            direct_heavy_vector_msbar,
            direct_vector_rxi,
            direct_conditional_scalar,
            direct_closure_frontier,
        )
    )
    recalculated_g7_inputs_bound = bool(
        direct_recalculated_g7_inputs
        == gate_report.get("physical_G7_recalculated_input_resolution", {})
        and direct_recalculated_g7_inputs["source_bound"] is True
        and direct_recalculated_g7_inputs[
            "all_resolved_scoped_inputs_closed"
        ]
        is True
        and all(
            direct_recalculated_g7_inputs["superseded_stale_blockers"].values()
        )
        and all(
            value is False
            for value in direct_recalculated_g7_inputs["precise_open_inputs"].values()
        )
        and direct_recalculated_g7_inputs["physical_G6_closed"] is False
        and direct_recalculated_g7_inputs["physical_G7_closed"] is False
        and direct_recalculated_g7_inputs["release_G7_verified"] is False
    )
    g1_full_component_tensors_closed = bool(
        gauged["G1"].get("full_G1_closed", False)
    )
    g2_full_mathematical_potential_closed = bool(
        gauged["G2"].get(
            "full_renormalizable_G2_mathematical_potential_closed", False
        )
    )
    expected_statuses = ledger._expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_full_mathematical_potential_closed,
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
        "exact_X_v3_contract_state_is_fail_closed_and_consistent": exact_x_v3_bound,
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
        "renormalizable_G2_mathematical_raw_core_source_bound": (
            mathematical_g2_closed
            and direct_g2_mathematical["raw_sha256"] == G2_MATHEMATICAL_RAW_SHA256
            and direct_g2_mathematical["core_sha256"] == G2_MATHEMATICAL_CORE_SHA256
            and direct_g2_mathematical["source_raw_sha256"]
            == G2_MATHEMATICAL_SOURCE_RAW_SHA256
            and direct_g2_mathematical["authoritative_G2_promoted_closed"]
            is False
            and direct_g2_mathematical["release_G2_verified"] is False
            and direct_g2_mathematical["G3_closed_by_this_theorem"] is False
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
        "parallel_EFT_G6_formal_spectrum_bound_but_physical_G6_open": (
            formal_eft_g6_bound
            and direct_parallel_eft_g6["raw_sha256"] == EFT_G6_RAW_SHA256
            and direct_parallel_eft_g6["core_sha256"] == EFT_G6_CORE_SHA256
            and direct_parallel_eft_g6[
                "formal_SU3_x_U1_89_tree_factorization_closed"
            ]
            is True
            and direct_parallel_eft_g6["mathematical_G6_closed_for_EFT_model"]
            is False
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
        "G6_provenance_and_parameterized_matching_fail_closed": (
            direct_g6_provenance["source_bound"] is True
            and direct_g6_provenance["physical_mathematical_G6_closed"] is False
            and direct_parameterized_matching["source_bound"] is True
            and direct_parameterized_matching[
                "formal_SU3_x_U1_89_threshold_determinants_complete"
            ]
            is True
            and direct_parameterized_matching["physical_mathematical_G6_closed"]
            is False
            and direct_parameterized_matching["mathematical_G7_closed"] is False
        ),
        "authoritative_gauge_beta_subtheorem_bound_but_full_G7_open": (
            gauge_beta_subtheorem_bound
            and direct_gauge_betas["full_two_loop_gauge_beta_closed"] is False
            and direct_gauge_betas["component_threshold_matching_closed"] is False
            and direct_gauge_betas["physical_G6_input_accepted_for_G7"] is False
            and direct_gauge_betas["release_G7_verified"] is False
        ),
        "independent_PyRATE3_replay_bound_but_full_G7_open": (
            pyrate_replay_bound
            and direct_pyrate_replay["full_two_loop_gauge_beta_closed"] is False
            and direct_pyrate_replay["physical_G6_threshold_matching_closed"]
            is False
            and direct_pyrate_replay["release_G7_verified"] is False
        ),
        "formal_U1_89_restriction_audit_raw_core_source_bound": (
            eft_g7_nonidentifiability_bound
            and direct_eft_g7_nonidentifiability[
                "formal_U1_89_restriction_map_noninjective"
            ]
            is True
            and direct_eft_g7_nonidentifiability[
                "exact_physical_EFT_G7_input_nonidentifiability_proved"
            ]
            is False
            and direct_eft_g7_nonidentifiability["absolute_scale_unidentified"]
            is True
            and direct_eft_g7_nonidentifiability[
                "mathematical_EFT_G7_closed"
            ]
            is False
            and direct_eft_g7_nonidentifiability[
                "EFT_release_G7_verified"
            ]
            is False
            and direct_eft_g7_nonidentifiability[
                "authoritative_renormalizable_G7_closed"
            ]
            is False
            and direct_eft_g7_nonidentifiability["positive_G7_certified"]
            is False
            and direct_eft_g7_nonidentifiability[
                "negative_G7_no_go_certified"
            ]
            is False
            and statuses["G7"] == ledger.STATUS_BLOCKED
            and statuses["G8"] == ledger.STATUS_BLOCKED
        ),
        "physical_SM_G8_identifiability_frontier_bound_and_G8_open": (
            g8_frontier_bound
            and direct_g8_frontier["whole_model_excluded_by_conditional_points"]
            is False
            and direct_g8_frontier["all_acceptance_criteria_pass"] is False
            and statuses["G8"] == ledger.STATUS_BLOCKED
        ),
        "physical_G7_component_threshold_contract_bound_but_full_G7_open": (
            physical_g7_bound
            and direct_physical_g7["authoritative_inventory_closed"] is True
            and direct_physical_g7["continuous_gauge_anomalies_closed"] is True
            and direct_physical_g7[
                "exact_two_loop_nonyukawa_gauge_flow_closed"
            ]
            is True
            and direct_physical_g7[
                "physical_component_pole_mass_matrices_closed"
            ]
            is False
            and direct_physical_g7["heavy_vector_matching_closed"] is False
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "normalized_Yukawa_CGC_contract_bound_but_flavor_RGE_G7_open": (
            yukawa_cgcs_bound
            and direct_yukawa_cgcs["normalized_10_CGCs_closed"] is True
            and direct_yukawa_cgcs["normalized_126bar_CGCs_closed"] is True
            and direct_yukawa_cgcs["canonical_304_Weyl_sparse_embedding_closed"]
            is True
            and direct_yukawa_cgcs["flavor_boundary_values_closed"] is False
            and direct_yukawa_cgcs["SARAH_Dot_conversion_closed"] is False
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "physical_SM_truth_overlay_bound_and_physical_G3_G7_open": (
            physical_sm_bound
            and direct_physical_sm[
                "reconstructed_stationary_transverse_PSD_witness_available"
            ]
            is True
            and direct_physical_sm[
                "direct_source_algebra_stationary_PSD_witness_available"
            ]
            is False
            and direct_physical_sm["source_bound_global_equality_orbit_proved"]
            is False
            and direct_physical_sm["old_selected_EFT_target_actual_stabilizer"]
            == "SU(3)_C x U(1)_89"
        ),
        "physical_SM_radial_equality_frontier_bound_but_G3_G4_G5_open": (
            source_equality_bound
            and direct_source_equality["observed_source_Hessian_row_lcm"]
            == 126000
            and direct_source_equality[
                "reconstructed_aggregate_Hessian_lcm"
            ]
            == 6300103327590
            and direct_source_equality["old_formal_U1_89_EFT_scope_promoted"]
            is False
        ),
        "physical_SM_five_amplitude_equality_bound_but_full_G3_G4_G5_open": (
            five_amplitude_bound
            and direct_five_amplitude[
                "exact_radial_theorem_strictly_extended"
            ]
            is True
            and direct_five_amplitude[
                "target_strict_minimum_on_five_amplitude_slice"
            ]
            is True
            and direct_five_amplitude["physical_SM_G3_closed"] is False
            and direct_five_amplitude["physical_SM_G4_closed"] is False
            and direct_five_amplitude["physical_SM_G5_closed"] is False
        ),
        "physical_SM_hard_projector_bundle_exactly_closes_its_10_row_scope": (
            hard_projectors_bound
            and direct_hard_projectors["all_10_O27_O44_source_Hessians_closed"] is True
            and direct_hard_projectors["full_witness_stationarity_rank_PSD_closed"] is False
            and direct_hard_projectors["full_486_global_equality_orbit_closed"] is False
        ),
        "physical_SM_last_six_bundle_makes_all_37_rows_available_for_the_aggregate": (
            last_six_bound
            and direct_last_six["full_486_global_equality_orbit_closed"] is False
        ),
        "physical_SM_37_row_local_Hessian_theorem_bound_but_global_equality_G3_G5_open": (
            aggregate_bound
        ),
        "physical_SM_full_486_local_equality_orbit_bound_but_radius_global_G3_G5_open": (
            local_orbit_bound
        ),
        "physical_SM_G4_G5_branch_mismatch_bound_but_not_global_no_go": (
            branch_mismatch_bound
            and direct_branch_mismatch["current_five_amplitude_target_is_canonical_physical_EW_branch"] is False
            and direct_branch_mismatch["global_no_go_for_other_physical_EW_branches"] is False
        ),
        "physical_SM_heavy_vector_contract_bound_but_G6_G7_open": (
            heavy_vectors_bound
            and direct_heavy_vectors[
                "exact_SU3C_x_U1em_vector_sector_resolution_closed"
            ]
            is True
            and direct_heavy_vectors["absolute_physical_vector_masses_closed"]
            is False
            and direct_heavy_vectors["pole_vector_masses_closed"] is False
            and direct_heavy_vectors[
                "vector_Goldstone_ghost_matching_closed"
            ]
            is False
            and statuses["G6"] == ledger.STATUS_BLOCKED
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "physical_SM_heavy_vector_MSbar_kernel_bound_but_G6_G7_open": (
            heavy_vector_msbar_bound
            and direct_heavy_vector_msbar[
                "Goldstone_double_count_guard_active"
            ]
            is True
            and direct_heavy_vector_msbar[
                "complete_scalar_fermion_threshold_matching_closed"
            ]
            is False
            and statuses["G6"] == ledger.STATUS_BLOCKED
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "physical_SM_zero_background_Rxi_vacuum_cancellation_bound_only": (
            vector_rxi_bound
            and direct_vector_rxi[
                "Goldstone_FPghost_double_count_guard_closed"
            ]
            is True
            and direct_vector_rxi["pole_vector_masses_closed"] is False
            and statuses["G6"] == ledger.STATUS_BLOCKED
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "conditional_physical_SM_scalar_spectrum_bound_but_G6_open": (
            conditional_scalar_bound
            and direct_conditional_scalar[
                "conditional_tree_Hessian_factorization_closed"
            ]
            is True
            and direct_conditional_scalar[
                "conditional_tree_sector_assignment_closed"
            ]
            is True
            and direct_conditional_scalar["release_G6_verified"] is False
            and statuses["G6"] == ledger.STATUS_BLOCKED
        ),
        "physical_SM_G6_G7_nonidentifiability_frontier_bound": (
            closure_frontier_bound
            and len(direct_closure_frontier["minimal_closure_path"]) == 7
            and direct_closure_frontier["release_G6_verified"] is False
            and direct_closure_frontier["release_G7_verified"] is False
            and statuses["G6"] == ledger.STATUS_BLOCKED
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "recalculated_G7_inputs_supersede_stale_broad_blockers_only": (
            recalculated_g7_inputs_bound
            and direct_recalculated_g7_inputs["mathematical_G7_closed"] is False
            and statuses["G7"] == ledger.STATUS_BLOCKED
        ),
        "parallel_EFT_G4_G5_G6_G7_leave_authoritative_frontier_unchanged": (
            statuses == expected_statuses
            and (
                contract_consistent
                or all(
                    statuses[name] == ledger.STATUS_BLOCKED
                    for name in ("G3", "G4", "G5", "G6", "G7", "G8")
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
            and gauged["G2"][
                "full_renormalizable_G2_mathematical_potential_closed"
            ]
            is True
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
            and gates["G2"]["full_gate_calculation_complete"] is True
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
        "Phi210. For that historical fixed-H/Sigma frontier, global Sigma, "
        "general/full H, and its then-unassembled Hessian remained open. The "
        "current physical-SM branch instead has an exact source-derived 37-row "
        "Hessian; its complete global equality orbit and physical G3 remain "
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
        "branch is an exact global SOS minimum with rank/nullity 429/33. The "
        "provenance audit later identifies its abelian stabilizer as U(1)_89, "
        "not physical electromagnetism. A chiral-H extension is exactly stationary "
        "and BFB for that frozen representative. Its source-bound 486-real Hessian is exactly "
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
        "and A(Phi)>3/200 at t=1 for every real Phi210. For that historical "
        "fixed-H/Sigma frontier, global Sigma, general/full H, and its "
        "then-unassembled Hessian remained open. The current physical-SM branch "
        "instead has an exact source-derived 37-row Hessian; its complete global "
        "equality orbit and physical G3 remain open. The historical "
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
        " Its frozen 486-degree tree mass factorization remains exact only as a "
        "formal SU(3)_C x U(1)_89 result, with 38 zero roots and 448 positive "
        "roots. The exact provenance audit proves that U(1)_89 is not physical "
        "electromagnetism and that standard SM projectors do not commute with the "
        "mass pencil. A corrected SU(3)_C x U(1)_em target/stabilizer, a conditional "
        "reconstructed 486-state scalar tree spectrum, and an exact parameterized "
        "heavy-vector tree matrix with physical provenance, rank/kernel, sectors, "
        "and threshold-log inputs are now closed scoped results. The exact "
        "source-derived all-37 physical-branch Hessian, stationarity, 38-dimensional "
        "symmetry kernel, rank 448 and PSD certificate are closed. The complete "
        "global equality-orbit proof, absolute scales/couplings, full scalar and "
        "fermion mass/mixing matrices with pole self-energies, and complete "
        "thresholds remain open; physical/mathematical, release and authoritative "
        "G6 are false."
        if formal_eft_g6_bound
        else " The corrected formal G6 spectrum view is missing or invalid."
    )
    verdict += (
        " Formal G89 scalar determinants, the corrected non-Yukawa gauge "
        "polynomials, physical PS/SM matter branching, the parameterized one-loop "
        "matter threshold kernel, normalized 10/126bar/singlet representation CGCs, "
        "the canonical sparse 304-Weyl embedding, and parameterized physical-SM "
        "vector tree inputs are exact scoped subtheorems. The combined heavy-vector/"
        "FP-ghost/Goldstone MS-bar kernel and finite vector constant are exact, and "
        "all 37 eaten directions are guarded against scalar double counting. The "
        "zero-background vacuum determinant cancellation is exact for arbitrary "
        "positive R_xi in all 37 directions. Continuous vector-scale, scalar-b, "
        "and flavor families prove that the remaining absolute spectrum, threshold "
        "vector and full RGE flow are not identified. SARAH "
        "implicit/identical-Weyl contraction conversion, flavor tensors/boundaries, "
        "the full coupled Yukawa/scalar/dimensionful/EFT system, background-"
        "covariant general-field determinants/heat-kernel replay, tree-to-pole "
        "conversion with a "
        "declared tadpole/VEV scheme, a stationary pre-EW stage, complete scalar/"
        "fermion thresholds, and physical scale/running boundaries remain open; "
        "mathematical, release and authoritative G7 are "
        "false, and G8 remains dependency-blocked."
        if direct_parameterized_matching["source_bound"]
        and gauge_beta_subtheorem_bound
        and physical_g7_bound
        and heavy_vector_msbar_bound
        and vector_rxi_bound
        and closure_frontier_bound
        and g8_frontier_bound
        else " The corrected G7 subtheorem bundle is missing or invalid."
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
        "exact_X_v3_fail_closed_resolution": direct_exact_x_v3,
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
        "renormalizable_G2_mathematical_resolution": {
            "theorem": G2_MATHEMATICAL_JSON.name,
            "source": G2_MATHEMATICAL_SOURCE.name,
            "source_bound": direct_g2_mathematical["source_bound"],
            "raw_sha256": g2_mathematical_raw_sha256,
            "expected_raw_sha256": G2_MATHEMATICAL_RAW_SHA256,
            "core_sha256": g2_mathematical.get("core_sha256"),
            "expected_core_sha256": G2_MATHEMATICAL_CORE_SHA256,
            "source_raw_sha256": g2_mathematical_source_raw_sha256,
            "expected_source_raw_sha256": G2_MATHEMATICAL_SOURCE_RAW_SHA256,
            "mathematical_G2_closed": mathematical_g2_closed,
            "authoritative_G2_promoted_closed": False,
            "release_G2_verified": False,
            "G3_closed_by_this_theorem": False,
            "downstream_integration_completed": direct_g2_mathematical[
                "downstream_integration_completed"
            ],
            "integration_blockers": direct_g2_mathematical[
                "integration_blockers"
            ],
            "release_blockers": direct_g2_mathematical["release_blockers"],
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
            "formal_SU3_x_U1_89_tree_factorization_closed": formal_eft_g6_bound,
            "physical_stabilizer_audit_source_bound": direct_g6_provenance[
                "source_bound"
            ],
            "corrected_residual_group": direct_parallel_eft_g6[
                "corrected_residual_group"
            ],
            "mathematical_G6_closed": False,
            "physical_mathematical_G6_closed": False,
            "original_renormalizable_G6_closed": False,
            "release_G6_verified": False,
            "authoritative_G6_gate_mutated": False,
            "integration_completed": direct_parallel_eft_g6[
                "parallel_integration_completed"
            ],
            "spectrum_summary": direct_parallel_eft_g6["spectrum_summary"],
            "release_blockers": direct_parallel_eft_g6["release_blockers"],
        },
        "G6_SM_provenance_resolution": direct_g6_provenance,
        "G6_G7_parameterized_matching_resolution": direct_parameterized_matching,
        "authoritative_gauge_beta_resolution": direct_gauge_betas,
        "independent_PyRATE3_gauge_replay_resolution": direct_pyrate_replay,
        "parallel_EFT_G7_nonidentifiability_resolution": {
            "theorem": EFT_G7_NONIDENTIFIABILITY_JSON.name,
            "source": EFT_G7_NONIDENTIFIABILITY_SOURCE.name,
            "source_bound": direct_eft_g7_nonidentifiability["source_bound"],
            "raw_sha256": eft_g7_nonidentifiability_raw_sha256,
            "expected_raw_sha256": EFT_G7_NONIDENTIFIABILITY_RAW_SHA256,
            "core_sha256": eft_g7_nonidentifiability.get("core_sha256"),
            "expected_core_sha256": EFT_G7_NONIDENTIFIABILITY_CORE_SHA256,
            "source_raw_sha256": eft_g7_nonidentifiability_source_raw_sha256,
            "expected_source_raw_sha256": (
                EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256
            ),
            "formal_U1_89_abstract_restriction_noninjectivity_proved": (
                eft_g7_nonidentifiability_bound
            ),
            "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
            "historical_electroweak_lift_interpretation_valid": False,
            "formal_U1_89_restriction_map_noninjective": direct_eft_g7_nonidentifiability[
                "formal_U1_89_restriction_map_noninjective"
            ],
            "absolute_scale_unidentified": direct_eft_g7_nonidentifiability[
                "absolute_scale_unidentified"
            ],
            "mathematical_G7_closed": False,
            "positive_G7_certified": False,
            "negative_G7_no_go_certified": False,
            "release_G7_verified": False,
            "authoritative_renormalizable_G7_closed": False,
            "integration_completed": direct_eft_g7_nonidentifiability[
                "downstream_integration_completed"
            ],
            "release_blockers": direct_eft_g7_nonidentifiability[
                "release_blockers"
            ],
            "positive_closure_requirements": direct_eft_g7_nonidentifiability[
                "positive_closure_requirements"
            ],
        },
        "physical_G7_component_threshold_resolution": direct_physical_g7,
        "normalized_SO10_Yukawa_CGC_resolution": direct_yukawa_cgcs,
        "physical_SM_vacuum_truth_resolution": direct_physical_sm,
        "physical_SM_source_algebra_equality_frontier_resolution": (
            direct_source_equality
        ),
        "physical_SM_five_amplitude_equality_resolution": (
            direct_five_amplitude
        ),
        "physical_SM_hard_projector_Hessians_resolution": direct_hard_projectors,
        "physical_SM_last_six_Hessians_resolution": direct_last_six,
        "physical_SM_37_row_aggregate_resolution": direct_aggregate,
        "physical_SM_local_equality_orbit_resolution": direct_local_orbit,
        "physical_SM_G4_G5_branch_mismatch_resolution": direct_branch_mismatch,
        "physical_SM_heavy_vector_mass_resolution": direct_heavy_vectors,
        "physical_SM_heavy_vector_MSbar_matching_resolution": (
            direct_heavy_vector_msbar
        ),
        "physical_SM_vector_Rxi_vacuum_cancellation_resolution": (
            direct_vector_rxi
        ),
        "conditional_physical_SM_EFT_Hessian_spectrum_resolution": (
            direct_conditional_scalar
        ),
        "physical_SM_G6_G7_closure_frontier_resolution": (
            direct_closure_frontier
        ),
        "physical_SM_G8_identifiability_frontier_resolution": (
            direct_g8_frontier
        ),
        "physical_G7_recalculated_input_resolution": (
            direct_recalculated_g7_inputs
        ),
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
        (
            "- Exact-X trusted SARAH 4.15.3 tree / external v3 execution "
            "attestation / authoritative G1: "
            f"`{report['exact_X_v3_fail_closed_resolution']['trusted_SARAH_4_15_3_source_tree_manifest_closed']}`/"
            f"`{report['exact_X_v3_fail_closed_resolution']['external_v3_execution_attestation_present']}`/"
            f"`{report['exact_X_v3_fail_closed_resolution']['authoritative_G1_closed']}`"
        ),
        "## Critical path",
        "",
        "`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`",
        "",
        "## Parallel dimension-six EFT classifications and obstruction",
        "",
        (
            "- Mathematical G3/G4/G5/G6: "
            f"`{report['parallel_EFT_G3_resolution']['mathematical_G3_closed']}`/"
            f"`{report['parallel_EFT_G4_resolution']['mathematical_G4_closed']}`/"
            f"`{report['parallel_EFT_G5_resolution']['mathematical_G5_closed']}`/"
            f"`{report['parallel_EFT_G6_resolution']['mathematical_G6_closed']}`"
        ),
        (
            "- Formal SU(3)_C x U(1)_89 G6 factorization: "
            f"`{report['parallel_EFT_G6_resolution']['formal_SU3_x_U1_89_tree_factorization_closed']}`"
        ),
        (
            "- Physical-stabilizer mismatch audit bound: "
            f"`{report['parallel_EFT_G6_resolution']['physical_stabilizer_audit_source_bound']}`"
        ),
        "- Release G3/G4/G5/G6: `False`/`False`/`False`/`False`",
        (
            "- Formal U(1)_89 abstract restriction noninjectivity: "
            f"`{report['parallel_EFT_G7_nonidentifiability_resolution']['formal_U1_89_abstract_restriction_noninjectivity_proved']}`"
        ),
        (
            "- Physical PS/SM matter branching and parameterized one-loop "
            "matter-threshold kernel: "
            f"`{report['physical_G7_component_threshold_resolution']['source_bound']}`"
        ),
        (
            "- Normalized SO(10) `10`/`126bar`/singlet representation CGCs: "
            f"`{report['normalized_SO10_Yukawa_CGC_resolution']['source_bound']}`"
        ),
        "- Flavor values, SARAH normalization conversion, Yukawa RGEs, and physical matching remain open.",
        (
            "- Physical-SM target/stabilizer truth overlay: "
            f"`{report['physical_SM_vacuum_truth_resolution']['source_bound']}`"
        ),
        (
            "- Exact five-real-amplitude equality classification (16 discrete "
            "sign variants; full 486-field/continuous-orbit proof open): "
            f"`{report['physical_SM_five_amplitude_equality_resolution']['source_bound']}`"
        ),
        (
            "- Exact hard projector Hessians (the staged 10/37-row input; the "
            "succeeding 37-row aggregate closes stationarity/rank/PSD): "
            f"`{report['physical_SM_hard_projector_Hessians_resolution']['source_bound']}`"
        ),
        (
            "- Exact last-six Hessians (all 37 active source Hessians made "
            "available; the succeeding aggregate closes stationarity/kernel/rank/PSD): "
            f"`{report['physical_SM_last_six_Hessians_resolution']['source_bound']}`"
        ),
        (
            "- Exact source-derived 37-row local Hessian theorem (stationary, "
            "38-mode kernel, rank 448, PSD; global equality open): "
            f"`{report['physical_SM_37_row_aggregate_resolution']['source_bound']}`"
        ),
        (
            "- Exact full-486 local stationary/equality orbit plus one continuous "
            "K-orbit for all 16 sign variants (radius/global equality open): "
            f"`{report['physical_SM_local_equality_orbit_resolution']['source_bound']}`"
        ),
        (
            "- Exact five-amplitude/physical-EW branch mismatch (not a global "
            "no-go; canonical G4-G8 open): "
            f"`{report['physical_SM_G4_G5_branch_mismatch_resolution']['source_bound']}`"
        ),
        (
            "- Exact parameterized physical-SM heavy-vector tree masses, "
            "rank/kernel, sectors and threshold logs: "
            f"`{report['physical_SM_heavy_vector_mass_resolution']['source_bound']}`"
        ),
        (
            "- Combined heavy-vector/FP-ghost/Goldstone MS-bar kernel and finite "
            "constant: "
            f"`{report['physical_SM_heavy_vector_MSbar_matching_resolution']['source_bound']}`"
        ),
        (
            "- Arbitrary-positive-R_xi zero-background vacuum determinant "
            "cancellation for all 37 broken directions: "
            f"`{report['physical_SM_vector_Rxi_vacuum_cancellation_resolution']['source_bound']}`"
        ),
        (
            "- Conditional reconstructed physical-SM tree scalar spectrum: "
            f"`{report['conditional_physical_SM_EFT_Hessian_spectrum_resolution']['source_bound']}`"
        ),
        (
            "- Exact G6/G7 continuous non-identifiability frontier and ordered "
            "closure path: "
            f"`{report['physical_SM_G6_G7_closure_frontier_resolution']['source_bound']}`"
        ),
        (
            "- Exact G8 identifiability frontier, 101-case scale audit, and "
            "PDG-2025 single-channel constraint verification: "
            f"`{report['physical_SM_G8_identifiability_frontier_resolution']['source_bound']}`"
        ),
        (
            "- Recalculated G7 scoped-input overlay (stale embedding/vector "
            "blockers superseded): "
            f"`{report['physical_G7_recalculated_input_resolution']['source_bound']}`"
        ),
        "- Background-covariant general-field determinants/heat-kernel replay, tree-to-pole/tadpole-VEV conversion, a stationary pre-EW stage, complete scalar/fermion thresholds, physical scale/running boundaries, flavor tensors, SARAH identical-Weyl conversion and full Yukawa betas remain open.",
        "- Historical selected EFT stabilizer: `SU(3)_C x U(1)_89` (superseded as a physical-SM label).",
        "- Physical-SM G3/G4/G5/G6/G7/G8: `False`/`False`/`False`/`False`/`False`/`False`.",
        "- Mathematical/release/authoritative G7: `False`/`False`/`False`.",
        "- Authoritative renormalizable G3-G8 are not promoted.",
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
