#!/usr/bin/env python3
"""Audit the strict G1 frontier of the selected V56 orbifold candidate.

V57 adds an exact, quantized six-dimensional Spin(10) supergravity/Green--
Schwarz bulk parent and an exact pointwise continuous-anomaly ledger.  It also
tests the proposed Z4R at the level required by the post-V40 G1 contract.  The
bulk and continuous fixed-point sectors pass, but the discrete-gauge origin,
localized discrete inflow, and the orbifold realization of the neutral parent
spectrum do not.  The report therefore keeps G1 open and selects a heterotic
spin-lift/mixed-symmetry embedding as a redesign target, not as an imported
closure certificate.

Nothing in this module is an empirical discovery.  Every pass is scoped to the
declared action or subsector and every cross-action import is forbidden.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V57_G1_MICROSCOPIC_COMPLETION_FRONTIER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V57_G1_MICROSCOPIC_COMPLETION_FRONTIER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v57_g1_microscopic_completion_frontier_audit.py"

INPUTS = {
    "v56_master": ROOT / "SUSY_V56_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.json",
    "v56_orbifold": ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json",
}

EXPECTED_CORES = {
    "v56_master": "500bb1429e6202c57f574143e01a2edb3e70d94087ae2ac347462c6729e92124",
    "v56_orbifold": "09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55",
}

STATUS = (
    "V57_G1_MICROSCOPIC_COMPLETION_FRONTIER__SPIN10_T1_U_LATTICE_BULK_GS_"
    "CLOSED__ALL_CONTINUOUS_FIXED_POINT_GAUGE_ANOMALIES_ZERO__TRADITIONAL_"
    "GLOBAL_CHECKS_PASS__Z4R_CLASSICAL_AUTOMORPHISM_ONLY__DISCRETE_GAUGE_"
    "ORIGIN_LOCAL_DISCRETE_INFLOW_AND_NEUTRAL_ORBIFOLD_SECTOR_OPEN__G1_NOT_"
    "CLOSED__HETEROTIC_SPIN_LIFT_REDESIGN_SELECTED__ZERO_GATE_PROMOTIONS__"
    "COMPLETE_THEORY_FALSE"
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
        raise RuntimeError(f"missing V57 input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def dot_u(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> Fraction:
    return x[0] * y[1] + x[1] * y[0]


def dot_i11(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> Fraction:
    return x[0] * y[0] - x[1] * y[1]


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def group_theory_ledger() -> dict[str, Any]:
    vector = {"representation": "10", "dimension": 10, "A": 1, "B": 1, "C": 0}
    adjoint = {"representation": "45", "dimension": 45, "A": 8, "B": 2, "C": 3}
    n10 = 2
    lambda_so = 2
    irreducible = adjoint["B"] - n10 * vector["B"]
    a_dot_b = Fraction(lambda_so, 6) * (adjoint["A"] - n10 * vector["A"])
    b_squared = -Fraction(lambda_so**2, 3) * (
        adjoint["C"] - n10 * vector["C"]
    )
    return {
        "trace_convention": "tr = tr_10",
        "lambda_Spin10": lambda_so,
        "representations": [vector, adjoint],
        "trace_identities": {
            "tr45_F2": "8 tr10_F2",
            "tr45_F4": "2 tr10_F4 + 3 (tr10_F2)^2",
        },
        "number_of_same_chirality_10_hypers": n10,
        "irreducible_trF4_coefficient": irreducible,
        "a_dot_b": int(a_dot_b),
        "b_squared": int(b_squared),
        "irreducible_gauge_anomaly_cancels": irreducible == 0,
    }


def spin10_bulk_completion() -> dict[str, Any]:
    group = group_theory_ledger()
    tensors = 1
    vectors = 45
    charged_hyper_dimensions = 2 * 10
    neutral_hyper_dimensions = 269
    hypers = charged_hyper_dimensions + neutral_hyper_dimensions
    gravitational_lhs = hypers - vectors + 29 * tensors

    a = (Fraction(-2), Fraction(-2))
    b = (Fraction(-2), Fraction(1))
    j = (Fraction(2), Fraction(1, 4))
    x1 = {"trR2": -1, "trF2": -2}
    x2 = {"trR2": -1, "trF2": 1}

    return {
        "id": "V57_SPIN10_T1_U_GREEN_SCHWARZ_PARENT_LAYER",
        "scope": "integrated 6D bulk before the T2/Z2 parity quotient",
        "global_gauge_group": "Spin(10)",
        "why_not_literal_SO10": (
            "The localized family spinors are 16 representations and therefore require "
            "Spin(10); they are not representations of Spin(10)/Z2."
        ),
        "supergravity_spectrum": {
            "gravity_multiplets": 1,
            "tensor_multiplets_T": tensors,
            "Spin10_vector_multiplets_dimension_V": vectors,
            "charged_hypermultiplets": "2 x 10",
            "charged_hyper_dimensions": charged_hyper_dimensions,
            "neutral_hyper_dimensions": neutral_hyper_dimensions,
            "total_hyper_dimensions_H": hypers,
            "gravitational_equation": "H - V + 29 T = 273",
            "gravitational_lhs": gravitational_lhs,
            "irreducible_gravitational_anomaly_cancels": gravitational_lhs == 273,
        },
        "string_charge_lattice": {
            "name": "even unimodular hyperbolic plane U",
            "Omega": [[0, 1], [1, 0]],
            "determinant": -1,
            "signature": [1, 1],
            "a": [int(a[0]), int(a[1])],
            "b_Spin10": [int(b[0]), int(b[1])],
            "a_squared": int(dot_u(a, a)),
            "a_dot_b": int(dot_u(a, b)),
            "b_squared": int(dot_u(b, b)),
            "a_is_characteristic_proof": (
                "For x=(m,n), x^2=2mn and a.x=-2(m+n), so a.x=x^2 mod 2."
            ),
            "unimodular": True,
            "a_is_characteristic": True,
            "Spin10_global_form_quantization": (
                "PASS in the declared coroot/cocharacter normalization: the D5 coroot "
                "lattice is even and (1/2)bK is Lambda-valued."
            ),
        },
        "positive_kinetic_chamber": {
            "j": ["2", "1/4"],
            "j_squared": str(dot_u(j, j)),
            "j_dot_b": str(dot_u(j, b)),
            "minus_j_dot_a": str(-dot_u(j, a)),
            "positive": dot_u(j, b) > 0 and -dot_u(j, a) > 0,
        },
        "green_schwarz_factorization": {
            "convention": (
                "I8=(1/2) Omega_ab X4^a X4^b with "
                "X4^a=(a^a/2) trR^2+b^a (2/lambda) trF^2 and lambda=2"
            ),
            "X4_components": [x1, x2],
            "factorized_I8": "(trR2 + 2 trF2)(trR2 - trF2)",
            "expanded_I8": "(trR2)^2 + trR2 trF2 - 2 (trF2)^2",
            "reducible_bulk_anomaly_factorizes": True,
            "quantized_GS_action": "dH^a=X4^a; S_GS=-integral Omega_ab B^a wedge X4^b",
        },
        "connected_global_anomaly": {
            "bordism_group": "Omega_7^Spin(BSpin(10)) = 0",
            "torsion_obstruction": False,
            "scope": (
                "ordinary connected Spin(10), characteristic a, unimodular Lambda, and "
                "standard self-dual-string completeness assumptions"
            ),
        },
        "bulk_sector_closed": all(
            [
                group["irreducible_gauge_anomaly_cancels"],
                gravitational_lhs == 273,
                dot_u(a, a) == 8,
                dot_u(a, b) == 2,
                dot_u(b, b) == -4,
                dot_u(j, b) > 0,
            ]
        ),
        "not_yet_an_orbifold_completion": [
            "parities and fixed-point distribution of all 269 neutral hypermultiplet dimensions",
            "localized tensor/axion boundary conditions and inflow",
            "self-dual-string worldsheet anomaly cancellation",
            "mixed discrete-R/local-Lorentz anomaly cancellation",
        ],
    }


def literal_so10_cross_check() -> dict[str, Any]:
    a = (Fraction(3), Fraction(1))
    b = (Fraction(0), Fraction(-2))
    j = (Fraction(5, 3), Fraction(4, 3))
    return {
        "id": "LITERAL_SO10_GLOBAL_FORM_CROSS_CHECK",
        "global_group": "SO(10)=Spin(10)/Z2",
        "primitive_U_solution": "FAILS because the SO(10) cocharacter lattice forces b in 2 Lambda",
        "repair_lattice": {
            "name": "odd unimodular I_(1,1)",
            "Omega": [[1, 0], [0, -1]],
            "determinant": -1,
            "a": [3, 1],
            "b": [0, -2],
            "a_squared": int(dot_i11(a, a)),
            "a_dot_b": int(dot_i11(a, b)),
            "b_squared": int(dot_i11(b, b)),
            "b_is_even_lattice_vector": True,
            "a_is_characteristic": True,
            "j": ["5/3", "4/3"],
            "j_squared": str(dot_i11(j, j)),
            "j_dot_b": str(dot_i11(j, b)),
        },
        "mathematically_consistent_bulk_alternative": True,
        "compatible_with_localized_16_families": False,
        "selected_for_V57": False,
    }


def continuous_fixed_point_ledger() -> list[dict[str, Any]]:
    return [
        {
            "fixed_point": "O_SO10",
            "global_local_group": "Spin(10)",
            "bulk_10_pair": "each 10 is real; perturbative 4D cubic anomaly zero",
            "bulk_45_vector": "real adjoint; zero",
            "localized_matter": "none",
            "perturbative_continuous_anomaly": "ZERO",
            "traditional_global_check": "pi4(Spin(10))=0",
            "passes": True,
        },
        {
            "fixed_point": "O_GG",
            "global_local_group": "(SU(5) x U(1)_X)/Z5",
            "bulk_10_pair": {
                "H10": [2, 2, 80, 20],
                "H10_prime": [-2, -2, -80, -20],
                "coefficient_order": ["SU5^3", "SU5^2-U1X", "U1X^3", "grav^2-U1X"],
                "sum": [0, 0, 0, 0],
            },
            "bulk_45_vector": "24_0+1_0+10_4+10bar_-4 cancels pairwise",
            "localized_matter": {
                "three_families": "3 x (10_-1 + 5bar_3 + 1_-5)",
                "one_family_coefficients": [0, 0, 0, 0],
                "rank_breaking": "X_10 + Xbar_-10 vectorlike; S_0 neutral",
            },
            "perturbative_continuous_anomaly": "ZERO",
            "traditional_global_check": "pi4(SU(5))=0; finite Z5 quotient adds no Witten test here",
            "passes": True,
        },
        {
            "fixed_point": "O_fl",
            "global_local_group": "(SU(5)' x U(1)'_X)/Z5",
            "bulk_10_pair": {
                "H10": [2, 2, 80, 20],
                "H10_prime": [-2, -2, -80, -20],
                "sum": [0, 0, 0, 0],
            },
            "bulk_45_vector": "tilded 10_4+10bar_-4 cancels pairwise",
            "localized_matter": "none",
            "perturbative_continuous_anomaly": "ZERO",
            "traditional_global_check": "pi4(SU(5))=0",
            "passes": True,
        },
        {
            "fixed_point": "O_PS",
            "global_local_group": "(SU(4)_C x SU(2)_L x SU(2)_R)/Z2",
            "bulk_10_pair": "10=(6,1,1)+(1,2,2): real/pseudoreal; perturbative anomaly zero",
            "bulk_45_vector": "45=(15,1,1)+(1,3,1)+(1,1,3)+(6,2,2): zero",
            "localized_matter": "none",
            "perturbative_continuous_anomaly": "ZERO",
            "traditional_global_check": (
                "each (1,2,2) gives two doublets and (6,2,2) gives twelve; "
                "both SU(2) Witten counts are even"
            ),
            "passes": True,
        },
    ]


def discrete_r_audit() -> dict[str, Any]:
    a3 = 3
    a2 = 1
    five_a1 = -3
    eta = 2
    a_grav = -21 + (8 + 3 + 1 + 1) - 4 - 2 + 1
    rho = 1
    required_gravity_residue = 24 * rho
    return {
        "declared_group_warning": (
            "With matter superfields of charge one, matter fermions have charge zero and "
            "r^2=(-1)^F times matter parity. The faithful group is generically Spin x Z4, "
            "not automatically Spin^Z4."
        ),
        "classical_action_automorphism": {
            "charges_mod4": {
                "theta": 1,
                "V_Phi_H_Hprime_X_Xbar": 0,
                "Hc_Hprimec_S": 2,
                "matter_superfields": 1,
                "superpotential": 2,
            },
            "bulk_gauge_kinetic_q": 2,
            "bulk_hyper_kinetic_superpotential_q": 2,
            "D_terms_neutral": True,
            "commutes_with_declared_pure_gauge_translation_twists": True,
            "classical_global_automorphism_passes": True,
        },
        "four_dimensional_necessary_residues": {
            "eta": eta,
            "rho": rho,
            "A3_R": a3,
            "A2_R": a2,
            "5A1_R": five_a1,
            "residues_mod_eta": [a3 % eta, a2 % eta, five_a1 % eta],
            "nonabelian_and_GUT_normalized_hypercharge_universal": (
                len({a3 % eta, a2 % eta, five_a1 % eta}) == 1
            ),
            "visible_plus_X_Xbar_S_gravitational_coefficient": a_grav,
            "required_24rho": required_gravity_residue,
            "gravitational_congruence_passes": (a_grav - required_gravity_residue) % eta == 0,
            "repair": (
                "retain an explicit GS dilaton/axion multiplet whose axino supplies the "
                "missing odd contribution, then quantize its shift and all couplings"
            ),
        },
        "hard_failures_or_open_obligations": [
            {
                "id": "D1_GAUGED_ORIGIN",
                "status": "OPEN",
                "reason": "a rigid SU(2)_R/hypermultiplet automorphism is not a discrete gauge construction",
            },
            {
                "id": "D2_POINTWISE_DISCRETE_ANOMALIES",
                "status": "OPEN",
                "reason": (
                    "no parity-weighted G_f^2-Z4R, U(1)^2-Z4R, grav^2-Z4R, or "
                    "local-Lorentz ledger at all four singularities"
                ),
            },
            {
                "id": "D3_QUANTIZED_LOCAL_INFLOW",
                "status": "OPEN",
                "reason": "no axion shifts, tensor parities, localized GS matrix, or integer levels",
            },
            {
                "id": "D4_TORSION_DAI_FREED",
                "status": "OPEN",
                "reason": "no eta-invariant/bordism computation for the actual Spin x Z4 symmetry",
            },
            {
                "id": "D5_ALL_FIXED_POINT_COUNTERTERMS",
                "status": "OPEN",
                "reason": "normal derivatives of odd fields and the full local counterterm ring remain unaudited",
            },
        ],
        "globally_gauged_Z4R_proved": False,
    }


def redesign_ledger() -> list[dict[str, Any]]:
    return [
        {
            "id": "R1_MINIMAL_SPIN10_T1_U_GS_PARENT",
            "decision": "ACCEPTED_EXACT_BULK_SUBSECTOR",
            "gain": "closes irreducible, reducible, gravitational, lattice, and connected global 6D bulk anomalies",
            "does_not_close": "orbifold-localized and discrete-R sectors",
            "same_action_G1_promotion": False,
        },
        {
            "id": "R2_LITERAL_SO10_I11_PARENT",
            "decision": "REJECTED_FOR_V56",
            "gain": "mathematically repairs the stronger SO(10) cocharacter quantization condition",
            "fatal_mismatch": "literal SO(10) cannot carry the localized 16 families",
            "same_action_G1_promotion": False,
        },
        {
            "id": "R3_BOTTOM_UP_GAUGED_U1R_TO_Z4R",
            "decision": "NOT_SELECTED",
            "reason": "requires a substantially new gauged 6D R-supergravity spectrum, vacuum, flux, and anomaly lattice",
            "same_action_G1_promotion": False,
        },
        {
            "id": "R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R",
            "decision": "SELECTED_UV_REDESIGN_TARGET_NOT_YET_CONSTRUCTED",
            "mechanism": (
                "derive Z4R from the spin lift of a T2/Z2 orbifold plane mixed with "
                "space-group and gauge symmetries; retain the universal dilaton GS multiplet"
            ),
            "published_existence_witness": (
                "heterotic orbifold vacua can realize matter charge 1, Higgs charge 0, "
                "one Higgs pair, and universal dilaton Green--Schwarz cancellation"
            ),
            "why_not_imported": (
                "the published witness is a different string action; the semi-realistic "
                "example also has an extra Z2 and rank-two down/lepton Yukawas"
            ),
            "required_same_action_binding": [
                "explicit worldsheet shift and Wilson lines",
                "complete massless and massive-index spectrum",
                "singlet-VEV solution and exact residual symmetry group",
                "local anomaly/GS maps to all V56 fixed-point groups",
                "proof that the V56 Higgs projector and brane-family sector survive",
            ],
            "same_action_G1_promotion": False,
        },
    ]


def strict_g1_matrix(
    bulk: dict[str, Any], points: list[dict[str, Any]], discrete: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        {
            "criterion": "compact_global_gauge_group_and_quotients",
            "status": "PASS",
            "evidence": "Spin(10) with (SU5xU1)/Z5 and PS/Z2 fixed-point global forms",
        },
        {
            "criterion": "integral_unimodular_string_charge_lattice",
            "status": "PASS_FOR_INTEGRATED_BULK",
            "evidence": "U lattice with characteristic a=(-2,-2), b=(-2,1)",
        },
        {
            "criterion": "complete_6D_chiral_supergravity_spectrum",
            "status": "PASS_FOR_INTEGRATED_BULK_ONLY",
            "evidence": "gravity + T=1 + Spin10 vector + 2x10 + 269 neutral hyper dimensions",
        },
        {
            "criterion": "all_integrated_6D_perturbative_anomalies",
            "status": "PASS",
            "evidence": "irreducible terms vanish and I8 factorizes on the quantized U lattice",
        },
        {
            "criterion": "connected_6D_global_gauge_gravity_anomaly",
            "status": "PASS_UNDER_DECLARED_ASSUMPTIONS",
            "evidence": "Omega_7^Spin(BSpin10)=0 plus unimodular lattice and characteristic a",
        },
        {
            "criterion": "continuous_fixed_point_gauge_and_traditional_global_anomalies",
            "status": "PASS",
            "evidence": f"{sum(row['passes'] for row in points)}/4 fixed points pass exactly",
        },
        {
            "criterion": "orbifold_projection_of_complete_parent_spectrum",
            "status": "OPEN",
            "evidence": "269 neutral hyper parities and localized tensor boundary conditions are unspecified",
        },
        {
            "criterion": "globally_gauged_Z4R_and_gravitational_residue",
            "status": "FAIL_OPEN",
            "evidence": (
                "classical automorphism only; low-energy A_grav=-13 fails the required "
                "congruence without an explicit GS axino/dilatino"
            ),
        },
        {
            "criterion": "pointwise_discrete_R_local_Lorentz_and_quantized_inflow",
            "status": "OPEN",
            "evidence": "no four-fixed-point coefficient matrix or localized axion/tensor inflow action",
        },
        {
            "criterion": "torsion_global_anomaly_for_actual_Spin_x_Z4_group",
            "status": "OPEN",
            "evidence": "Dai-Freed/bordism invariant not computed",
        },
        {
            "criterion": "same_action_G1_closure",
            "status": "OPEN",
            "evidence": "every strict row must pass in one versioned action; three rows remain open and one fails/open",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: V57 exactly closes the integrated Spin(10) 6D bulk GS sector and all "
            "continuous fixed-point gauge anomalies, but a globally gauged Z4R, its "
            "pointwise discrete/local-Lorentz anomaly inflow, and the orbifold projection "
            "of the 269 neutral hyper dimensions are not constructed in the same action."
        ),
        "G2": "OPEN: the new bulk parent and proposed string spin-lift are not one complete W/K/gauge/soft action.",
        "G3": "OPEN: no interacting orbifold vacuum or regulated infinite-KK Hessian is solved.",
        "G4": "OPEN: the V56 free projector remains exact, but the all-boundary-operator problem is unchanged.",
        "G5": "OPEN: no completed dark sector or cosmological history.",
        "G6": "OPEN: no compactification/threshold/precision-unification match.",
        "G7": "OPEN: no infinite-KK proton tensor, dressing, or lifetime prediction.",
        "G8": "OPEN: no mediator-complete flavour/seesaw fit.",
    }
    return [
        {
            "gate": f"G{i}",
            "status": "OPEN",
            "V57_candidate_closed": False,
            "decision": decisions[f"G{i}"],
        }
        for i in range(1, 9)
    ]


def primary_sources() -> list[dict[str, str]]:
    return [
        {
            "title": "Anomaly Constraints and String/F-theory Geometry in 6D Quantum Gravity",
            "url": "https://arxiv.org/abs/1008.1062",
            "use": "6D anomaly equations, group constants, and kinetic chamber",
        },
        {
            "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
            "url": "https://arxiv.org/abs/1711.04777",
            "use": "integral string-charge and global-form quantization",
        },
        {
            "title": "Remarks on the Green-Schwarz terms of six-dimensional supergravity theories",
            "url": "https://arxiv.org/abs/1808.01334",
            "use": "unimodular lattice, characteristic a, and global GS conditions",
        },
        {
            "title": "Some comments on 6D global gauge anomalies",
            "url": "https://arxiv.org/abs/2012.11622",
            "use": "Spin/SO bordism computation",
        },
        {
            "title": "SO(10) Unified Theories in Six Dimensions",
            "url": "https://arxiv.org/abs/hep-ph/0108071",
            "use": "two-10 orbifold spectrum and parity architecture",
        },
        {
            "title": "Anomaly cancellation in six dimensions",
            "url": "https://arxiv.org/abs/hep-ph/0209144",
            "use": "parity-weighted localized anomaly formula",
        },
        {
            "title": "Localized anomalies in orbifold gauge theories",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "use": "localized gauge and internal-Lorentz anomaly obligations",
        },
        {
            "title": "A unique Z4R symmetry for the MSSM",
            "url": "https://arxiv.org/abs/1009.0905",
            "use": "discrete residues, GS axino repair, and string spin-lift existence witness",
        },
        {
            "title": "On the Anomaly of the Electromagnetic Duality of the Maxwell Theory",
            "url": "https://arxiv.org/abs/1808.02881",
            "use": "ordinary Z4 versus Spin-Z4 global-symmetry distinction",
        },
        {
            "title": "Supersymmetric Standard Model from the Heterotic String (II)",
            "url": "https://arxiv.org/abs/hep-th/0606187",
            "use": "explicit modular-invariant local-SO10 heterotic redesign precedent",
        },
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_bound(name, path) for name, path in INPUTS.items()}
    v56_master = inputs["v56_master"]
    v56_orbifold = inputs["v56_orbifold"]
    bulk = spin10_bulk_completion()
    literal = literal_so10_cross_check()
    points = continuous_fixed_point_ledger()
    discrete = discrete_r_audit()
    redesign = redesign_ledger()
    matrix = strict_g1_matrix(bulk, points, discrete)
    gates = gate_ledger()

    checks = {
        "bound_V56_cores_are_canonical_and_expected": all(
            inputs[name]["core_sha256"] == expected
            for name, expected in EXPECTED_CORES.items()
        ),
        "upstream_selected_action_is_the_V56_orbifold": (
            v56_master["selected_frontier_action"]["id"]
            == "V56_6D_T2_Z2_SU5_BRANE_Z4R"
        ),
        "upstream_G1_was_open": next(
            row for row in v56_master["gate_ledger"] if row["gate"] == "G1"
        )["status"]
        == "OPEN",
        "two_10s_cancel_irreducible_Spin10_gauge_anomaly": group_theory_ledger()[
            "irreducible_gauge_anomaly_cancels"
        ],
        "minimal_T1_gravitational_count_is_273": bulk["supergravity_spectrum"][
            "gravitational_lhs"
        ]
        == 273,
        "U_lattice_is_integral_unimodular_and_characteristic": (
            bulk["string_charge_lattice"]["determinant"] == -1
            and bulk["string_charge_lattice"]["a_is_characteristic"]
            and bulk["string_charge_lattice"]["a_squared"] == 8
            and bulk["string_charge_lattice"]["a_dot_b"] == 2
            and bulk["string_charge_lattice"]["b_squared"] == -4
        ),
        "bulk_reducible_anomaly_factorizes": bulk["green_schwarz_factorization"][
            "reducible_bulk_anomaly_factorizes"
        ],
        "positive_gauge_kinetic_chamber_exists": bulk["positive_kinetic_chamber"][
            "positive"
        ],
        "all_four_continuous_fixed_point_anomalies_vanish": all(
            row["passes"] for row in points
        ),
        "low_energy_Z4R_gauge_residues_are_universal_mod2": discrete[
            "four_dimensional_necessary_residues"
        ]["nonabelian_and_GUT_normalized_hypercharge_universal"],
        "low_energy_Z4R_gravitational_mismatch_is_exposed": not discrete[
            "four_dimensional_necessary_residues"
        ]["gravitational_congruence_passes"],
        "Z4R_is_not_overclaimed_as_globally_gauged": not discrete[
            "globally_gauged_Z4R_proved"
        ],
        "literal_SO10_repair_is_not_imported_into_spinor_model": (
            literal["mathematically_consistent_bulk_alternative"]
            and not literal["compatible_with_localized_16_families"]
            and not literal["selected_for_V57"]
        ),
        "heterotic_redesign_is_selected_but_not_imported": (
            next(row for row in redesign if row["id"] == "R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R")[
                "decision"
            ]
            == "SELECTED_UV_REDESIGN_TARGET_NOT_YET_CONSTRUCTED"
            and not next(
                row for row in redesign if row["id"] == "R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R"
            )["same_action_G1_promotion"]
        ),
        "strict_G1_matrix_contains_open_or_failed_rows": any(
            row["status"] in {"OPEN", "FAIL_OPEN"} for row in matrix
        ),
        "no_G1_to_G8_gate_is_promoted": all(
            row["status"] == "OPEN" and not row["V57_candidate_closed"] for row in gates
        ),
        "upstream_free_projector_is_preserved_not_reproved": (
            v56_orbifold["orbifold_mode_certificate"]["weak_doublet_zero_mode_count"] == 2
            and v56_orbifold["orbifold_mode_certificate"]["color_triplet_zero_mode_count"] == 0
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v57_g1_microscopic_completion_frontier_audit/v1",
        "status": STATUS,
        "question": (
            "Can the selected V56 T2/Z2 Spin(10) orbifold be promoted through the "
            "strict post-V40 G1 microscopic-consistency gate, creating new physics if needed?"
        ),
        "strict_scope": (
            "One action must supply its compact global group, integral charge/axion lattice, "
            "complete chiral spectrum, and cancellation of every perturbative, localized, "
            "global, and discrete anomaly by an explicitly quantized mechanism."
        ),
        "input_core_hashes": {name: value["core_sha256"] for name, value in inputs.items()},
        "expected_input_core_hashes": EXPECTED_CORES,
        "exact_6D_bulk_completion": bulk,
        "literal_SO10_cross_check": literal,
        "continuous_fixed_point_anomaly_ledger": points,
        "discrete_Z4R_microscopic_audit": discrete,
        "strict_G1_matrix": matrix,
        "redesign_ledger": redesign,
        "gate_ledger": gates,
        "new_physics_created": {
            "yes": True,
            "kind": "quantized Spin(10), T=1, U-lattice Green-Schwarz parent layer",
            "exact_gain": (
                "the integrated 6D irreducible, reducible, gravitational, charge-lattice, "
                "kinetic-chamber, and connected global anomaly sector is now closed"
            ),
            "not_a_complete_new_theory": True,
            "empirical_discovery": False,
        },
        "terminal_decision": {
            "V57_G1_closed": False,
            "V57_closed_gates": [],
            "full_gates_closed_for_V57_candidate": 0,
            "integrated_6D_bulk_G1_subsector_closed": True,
            "continuous_fixed_point_gauge_anomaly_subsector_closed": True,
            "globally_gauged_Z4R_closed": False,
            "same_action_completion": False,
            "complete_theory": False,
            "selected_complete_candidate": None,
            "selected_next_redesign": "R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R",
            "historical_or_cross_action_G1_closure_may_not_be_imported": True,
            "honest_outcome": (
                "V57 makes the maximum exact same-line advance presently supported: the "
                "bulk Green--Schwarz parent and every continuous fixed-point gauge anomaly "
                "are closed. G1 itself remains open because the proposed Z4R is only a "
                "classical automorphism, its necessary gravitational residue fails without "
                "an explicit GS multiplet, and no quantized pointwise discrete/local-Lorentz "
                "inflow or complete neutral orbifold spectrum exists. A heterotic spin-lift "
                "embedding is a viable redesign, but importing a published different string "
                "vacuum would violate the one-action rule."
            ),
        },
        "primary_sources": primary_sources(),
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not passed for passed in checks.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    failures: list[str] = []
    if report.get("core_sha256") != canonical_sha(report):
        failures.append("canonical core hash mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failures.append("one or more integrity checks failed")
    decision = report.get("terminal_decision", {})
    if decision.get("V57_G1_closed"):
        failures.append("strict G1 was overclaimed")
    if decision.get("complete_theory"):
        failures.append("complete theory was overclaimed")
    if decision.get("V57_closed_gates"):
        failures.append("a gate was promoted")
    if report.get("discrete_Z4R_microscopic_audit", {}).get("globally_gauged_Z4R_proved"):
        failures.append("unproved gauged Z4R was promoted")
    if any(
        row.get("same_action_G1_promotion")
        for row in report.get("redesign_ledger", [])
    ):
        failures.append("cross-action redesign was imported")
    if failures:
        raise RuntimeError("V57 G1 frontier audit failed: " + "; ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    bulk = report["exact_6D_bulk_completion"]
    lattice = bulk["string_charge_lattice"]
    spectrum = bulk["supergravity_spectrum"]
    discrete = report["discrete_Z4R_microscopic_audit"]
    residues = discrete["four_dimensional_necessary_residues"]
    point_rows = "\n".join(
        f"| {row['fixed_point']} | {row['global_local_group']} | "
        f"{row['perturbative_continuous_anomaly']} | {row['traditional_global_check']} |"
        for row in report["continuous_fixed_point_anomaly_ledger"]
    )
    matrix_rows = "\n".join(
        f"| {row['criterion']} | {row['status']} | {row['evidence']} |"
        for row in report["strict_G1_matrix"]
    )
    redesign_rows = "\n".join(
        f"| {row['id']} | {row['decision']} | "
        f"{row.get('gain', row.get('mechanism', row.get('reason', '')))} |"
        for row in report["redesign_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['use']}"
        for row in report["primary_sources"]
    )
    decision = report["terminal_decision"]
    return f"""# V57 G1 microscopic-completion frontier audit

Status: `{report['status']}`

## Result

**G1 remains OPEN. No G1--G8 gate is promoted.**

V57 nevertheless closes two substantial subsectors exactly:

1. the integrated six-dimensional `Spin(10)` bulk anomaly and quantized
   Green--Schwarz sector; and
2. every perturbative continuous gauge anomaly, plus the traditional Witten
   checks, at all four orbifold fixed points.

The remaining obstruction is not another ordinary anomaly sum. The declared
`Z4R` is a consistent classical automorphism, but no faithful microscopic
discrete-gauge realization, pointwise discrete/local-Lorentz anomaly ledger,
or quantized localized inflow action has been constructed. The required 269
neutral hypermultiplet dimensions also have no declared orbifold parities.

## Exact 6D bulk completion

With `tr=tr_10`, two same-chirality `10` hypermultiplets and the `45` vector give

```text
B_adj - 2 B_10 = 2 - 2 = 0
a.b = (2/6)(8 - 2) = 2
b^2 = -(4/3)(3 - 0) = -4
```

The minimal tensor choice is `T={spectrum['tensor_multiplets_T']}`. The complete
integrated chiral count is

```text
H = 20 charged + 269 neutral = {spectrum['total_hyper_dimensions_H']}
H - V + 29 T = {spectrum['gravitational_lhs']} = 273
```

Choose the even unimodular hyperbolic plane

```text
Omega = [[0,1],[1,0]]       det(Omega) = {lattice['determinant']}
a = {lattice['a']}                    a^2 = {lattice['a_squared']}
b = {lattice['b_Spin10']}                     a.b = {lattice['a_dot_b']}, b^2 = {lattice['b_squared']}
j = (2,1/4)                 j^2 = 1, j.b = 3/2
```

`a` is characteristic because for every `x=(m,n)`, `x^2=2mn` and
`a.x=-2(m+n)` are equal modulo two. The factorized polynomial is

```text
I8 = (tr R^2 + 2 tr F^2)(tr R^2 - tr F^2)
   = (tr R^2)^2 + tr R^2 tr F^2 - 2 (tr F^2)^2.
```

This passes the declared `Spin(10)` global-form quantization and
`Omega_7^Spin(BSpin(10))=0`. Literal `SO(10)` needs an even `b` on the odd
unimodular `I_(1,1)` repair lattice, but it cannot carry the localized `16`
families and is therefore not the V57 global group.

## Continuous fixed-point ledger

| Fixed point | Compact local group | Continuous anomaly | Traditional global check |
|---|---|---:|---|
{point_rows}

At `O_GG`, the two bulk tens contribute opposite coefficient vectors
`(2,2,80,20)` and `(-2,-2,-80,-20)` for
`(SU5^3, SU5^2-X, X^3, grav^2-X)`. Each localized
`10_-1 + 5bar_3 + 1_-5` family is separately anomaly-free, and
`X_10 + Xbar_-10` is vectorlike.

## Why the discrete sector blocks G1

The low-energy necessary gauge residues are

```text
(A3^R, A2^R, 5 A1^R) = ({residues['A3_R']}, {residues['A2_R']}, {residues['5A1_R']})
                         = (1,1,1) mod eta=2.
```

This is the universal Green--Schwarz pattern, not zero anomaly. For the stated
visible plus `X`, `Xbar`, `S`, and `U(1)_X` ledger,

```text
A_grav^R = {residues['visible_plus_X_Xbar_S_gravitational_coefficient']} = 1 mod 2,
24 rho   = {residues['required_24rho']} = 0 mod 2.
```

An explicit dilaton/axion GS multiplet can repair the odd mismatch through its
axino, but V56 did not contain that microscopic field and did not quantize its
shift or local couplings. Also, with matter superfield charge one,
`r^2=(-1)^F` times matter parity; the symmetry is generically ordinary
`Spin x Z4`, not automatically `Spin^Z4`.

## Strict G1 matrix

| Criterion | Status | Evidence |
|---|---|---|
{matrix_rows}

## Redesign decision

| Route | Decision | Exact role |
|---|---|---|
{redesign_rows}

The selected redesign target is a heterotic spin-lift/mixed-symmetry origin for
`Z4R`, including the universal dilaton GS multiplet. Published string vacua
show that this mechanism can exist, but they are not the V56 action. The cited
semi-realistic witness also retains an extra `Z2` and rank-two down/lepton
Yukawas. It is therefore a target to construct, not a closure certificate that
can be imported.

## Terminal decision

{decision['honest_outcome']}

- New physics created: **yes**, an exact quantized 6D bulk parent layer.
- Integrated 6D bulk G1 subsector closed: **yes**.
- Continuous fixed-point gauge anomaly subsector closed: **yes**.
- Full same-action G1 closed: **no**.
- Complete theory: **no**.
- Empirical discovery: **no**.

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown artifacts")
    parser.add_argument("--check", action="store_true", help="verify current artifacts")
    args = parser.parse_args()

    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V57 artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V57 JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V57 Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
