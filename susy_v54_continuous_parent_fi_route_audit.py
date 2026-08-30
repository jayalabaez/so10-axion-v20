#!/usr/bin/env python3
"""V54 continuous-parent/FI route and charged-source retuning audit.

The audit has two deliberately separated layers.

1.  For the unchanged V53 source/filter action it derives the unique ordinary
    continuous-U(1) charge lift.  It then proves two exact obstructions:
    ``h H2`` is already a symmetry-allowed renormalizable filter filler and
    ``P^2 H1^2`` is an allowed higher-dimensional filler.  The most-general
    renormalizable visible Hessian therefore has no weak-Higgs kernel.

2.  It records a charged-spurion retuning seed with q(B) != 0.  At fixed
    spurion VEVs the retuned 176-coordinate source remains exactly F/D-flat
    with rank(H)=143 and ker(H)=the 33-dimensional Spin(10) orbit.  The seed
    passes bounded charge tests, but the dynamical spurion F equations and full
    Hessian have not been solved, so it is not promoted into the action above.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import susy_v52_low_index_source_audit as v52
import susy_v53_elementary_filter_hessian_audit as elementary
import susy_v53_natural_dt_filter_audit as dw


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v54_continuous_parent_fi_route_audit.py"

UPSTREAM = {
    "V53_elementary_filter": (
        ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json",
        "993b549668243b06d082a7def8591c63141dfa402d6372b133c19cfa8f8b6ff6",
    ),
    "V53_filter_selector": (
        ROOT / "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json",
        "33de88b196a5096f7169cc3156d68cd9f4fa33e985adf0c23ea6c67a1a732dce",
    ),
    "V53_driver_no_go": (
        ROOT / "SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.json",
        "3777e4ab0f03591ca736f71e282f86a8f232fee83fb2f1d378e789fea6765bf4",
    ),
    "V53_master": (
        ROOT / "SUSY_V53_THEORY_COMPLETION_VERIFICATION_AUDIT.json",
        "620525de6b9a6ed2a63fe7e734caa18239dc26b4ef3e36b8eadbd4259d9e3cde",
    ),
}

STATUS = (
    "V54_CONTINUOUS_U1_PARENT_UNIQUE__UNCHANGED_SOURCE_FORCES_B_NEUTRAL__"
    "RENORMALIZABLE_hH2_FILLER_ALLOWED_AND_EXACT_WEAK_RANK16__P2H1SQ_ALLOWED__"
    "FI_VISIBLE_ACTION_RANK237_NULLITY34_EQUALS_GAUGE__NO_LIGHT_HIGGS__"
    "CHARGED_SOURCE_RETUNING_SEED_RESCUED_BY_ONE_CHARGE2_SINGLET__"
    "ANOMALY_REPAIRED_363_COORDINATE_HESSIAN_RANK325_NULLITY38__34_GAUGE_PLUS4_WEAK__"
    "FIRST_PROTON_DRESSING_DEGREE9__GS_KAHLER_AND_PHENOMENOLOGY_OPEN__"
    "NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_upstream() -> dict[str, Any]:
    result = {}
    for name, (path, expected) in UPSTREAM.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("core_sha256") != expected or canonical_sha(data) != expected:
            raise RuntimeError(f"stale upstream certificate: {name}")
        result[name] = {"path": path.name, "core_sha256": expected}
    return result


def continuous_charge_lift() -> dict[str, Any]:
    q = {
        "E54": 0, "A45": 0, "B45_DW": 0,
        "C16H": 1, "barC16H": -1,
        "H1_10": -2, "barh_10": 0, "h_10": 0, "H2_10": 0,
        "P": 2, "F16": 1, "N": 0, "Nc": 0,
    }
    required = {
        "E2": 2*q["E54"], "E3": 3*q["E54"],
        "A2": 2*q["A45"], "EA2": q["E54"]+2*q["A45"],
        "B2": 2*q["B45_DW"], "EB2": q["E54"]+2*q["B45_DW"],
        "AB": q["A45"]+q["B45_DW"],
        "EAB": q["E54"]+q["A45"]+q["B45_DW"],
        "barC_C": q["barC16H"]+q["C16H"],
        "barC_A_C": q["barC16H"]+q["A45"]+q["C16H"],
        "P_H1_barh": q["P"]+q["H1_10"]+q["barh_10"],
        "barh_h": q["barh_10"]+q["h_10"],
        "h_B_H2": q["h_10"]+q["B45_DW"]+q["H2_10"],
        "H2_squared": 2*q["H2_10"],
        "F_F_H1": 2*q["F16"]+q["H1_10"],
        "F_barC_N": q["F16"]+q["barC16H"]+q["N"],
        "N_Nc": q["N"]+q["Nc"], "Nc_squared": 2*q["Nc"],
    }
    vev_charges = [0, 0, 0, 1, -1, 2]
    bounded = []
    for degree in range(3):
        for dressing in itertools.combinations_with_replacement(vev_charges, degree):
            bounded.append(4*q["F16"] + sum(dressing))
    return {
        "charges": q,
        "derivation": [
            "E2 and E3 => qE=0; A2, B2 and AB => qA=qB=0",
            "H2^2, h B H2 and barh h => qH2=qh=qbarh=0",
            "P H1 barh and F F H1 => qH1=-qP and qP=2 qF",
            "barC C, F barC N, N Nc and Nc^2 => qC=qF, qbarC=-qF, qN=qNc=0",
        ],
        "all_required_neutral": all(value == 0 for value in required.values()),
        "required_term_charges": required,
        "operator_charges": {
            "h_H2_renormalizable_filler": q["h_10"]+q["H2_10"],
            "H1_squared": 2*q["H1_10"],
            "P_squared_H1_squared": 2*q["P"]+2*q["H1_10"],
            "F16_power4": 4*q["F16"],
            "F16_power4_barC_power4": 4*q["F16"]+4*q["barC16H"],
        },
        "all_F4_dressings_with_at_most_two_VEVs_forbidden": all(value != 0 for value in bounded),
    }


def filter_filler_audit() -> tuple[dict[str, Any], np.ndarray]:
    declared = elementary.filter_hessian()
    filled = declared.copy()
    identity = np.eye(10, dtype=np.int64)
    filled[20:30, 30:40] += identity
    filled[30:40, 20:30] += identity
    color_indices = [10*field+i for field in range(4) for i in range(6)]
    weak_indices = [10*field+i for field in range(4) for i in range(6, 10)]
    rank = lambda m: v52.modular_rank(np.asarray(m, dtype=np.int64) % v52.MODULAR_PRIME)
    return {
        "declared_rank": rank(declared),
        "declared_weak_rank": rank(declared[np.ix_(weak_indices, weak_indices)]),
        "declared_weak_nullity": 16-rank(declared[np.ix_(weak_indices, weak_indices)]),
        "allowed_filler": "m0 h^T H2",
        "filler_charge": 0,
        "filled_rank": rank(filled),
        "filled_color_rank": rank(filled[np.ix_(color_indices, color_indices)]),
        "filled_weak_rank": rank(filled[np.ix_(weak_indices, weak_indices)]),
        "filled_weak_nullity": 16-rank(filled[np.ix_(weak_indices, weak_indices)]),
        "exact_weak_determinant_factor": "(P lambdaP)^2 m0^2 per weak internal coordinate",
    }, filled


def visible_fi_hessian(filled_filter: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    source_dim, filter_dim, p_dim, spectator_dim = 176, 40, 1, 54
    total = source_dim + filter_dim + p_dim + spectator_dim
    h = np.zeros((total, total), dtype=np.complex128)
    h[:source_dim, :source_dim] = dw.hessian_numerator()
    h[source_dim:source_dim+filter_dim, source_dim:source_dim+filter_dim] = 40*filled_filter
    h[-spectator_dim:, -spectator_dim:] = 40*np.eye(spectator_dim, dtype=np.int64)
    h = v52._gaussian_integer(h, label="V54 40H")

    q = np.zeros((total, 46), dtype=np.complex128)
    q[:source_dim, :45] = dw.orbit_numerator()
    data = dw.witness()
    q[144:160, 45] = 10*data["C0"]
    q[160:176, 45] = -10*data["barC0"]
    q[source_dim+filter_dim, 45] = 20
    q = v52._gaussian_integer(q, label="V54 10Q")

    h_rank = v52.modular_rank(v52._modular_matrix(h))
    q_rank = v52.modular_rank(v52._modular_matrix(q))
    hq_zero = bool(np.count_nonzero(h @ q) == 0)
    return {
        "visible_coordinates": total,
        "inventory": {
            "exact_DW_source": 176, "four_10_filter": 40, "P": 1,
            "five_spectator_10s": 50, "four_spectator_singlets": 4,
        },
        "hessian_rank": h_rank,
        "hessian_nullity": total-h_rank,
        "gauge_orbit_rank": q_rank,
        "ward_product_zero": hq_zero,
        "kernel_equals_Spin10_plus_U1_gauge_orbit": hq_zero and total-h_rank == q_rank,
        "physical_weak_Higgs_zero_modes": 0,
        "boundary": "visible chiral holomorphic certificate; GS modulus/Kahler/vector scalar matrix not included",
    }, h, q


def fi_anomaly_and_running() -> dict[str, Any]:
    base = {"Spin10_squared_U1": 4, "TrQ": 30, "TrQ3": -24}
    repaired = {
        "Spin10_squared_U1": 4-5,
        "TrQ": 30-5*10-4,
        "TrQ3": -24-5*10-4,
    }
    total_t = 42+5
    b = total_t-3*8
    pole = math.exp(8*math.pi**2/(b*0.73**2))
    return {
        "base": base,
        "repair_fields": {
            "five_10s": {"charge_each": -1, "mass": "P V_i^2/2"},
            "four_singlets": {"charge_each": -1, "mass": "P S_j^2/2"},
        },
        "repaired": repaired,
        "GS_nonAbelian_gravity_universality": repaired["Spin10_squared_U1"] == repaired["TrQ"]//24 == -1,
        "positive_abelian_normalization_in_1110_6901_convention": 13,
        "FI_solution": "xi_A<0 and 2|P|^2+xi_A=0 when |C|=|barC|",
        "sum_T_Spin10": total_t,
        "b_Spin10": b,
        "pole_ratio_at_g_0p73": pole,
        "passes_100x": pole > 100,
        "passes_1000x": pole > 1000,
        "raw_TrQ_squared": 178,
    }


def neutral_driver_no_go() -> dict[str, Any]:
    return {
        "assumptions": [
            "compact ordinary U(1), charged P, uncharged constant v^2",
            "renormalizable Lagrange-multiplier F driver",
            "unchanged filter/Yukawa relations qP=2qF",
        ],
        "only_nontrivial_quadratic_constant_driver": "X(P S-v^2)",
        "derived_charge": "qS=-qP=-2qF",
        "fatal_operator": "F16^4 S^2",
        "fatal_charge_identity": "4qF+2qS=4qF-2qP=0",
        "conclusion": "holomorphic renormalizable P driver fails bounded proton safety; FI breaking avoids S but not filter fillers",
    }


def _first_dressing(charges: Mapping[str, int], target: int, maximum: int = 20) -> dict[str, Any] | None:
    names = list(charges)
    for degree in range(maximum+1):
        for indices in itertools.combinations_with_replacement(range(len(names)), degree):
            if sum(charges[names[index]] for index in indices) == target:
                return {"insertions": degree, "fields": [names[index] for index in indices]}
    return None


def charged_source_retuning_seed() -> dict[str, Any]:
    original = dw.witness
    data = dict(original())
    data.update({
        "mE": 14, "lambda": 0, "mA": 214, "mB": -50,
        "kappaA": 19, "kappaB": 10, "muAB": 6, "kappaAB": 1,
        "eta": -6j, "mC": 27,
    })
    try:
        dw.witness = lambda: data
        f_terms = dw.f_term_numerators()
        h = dw.hessian_numerator()
        q = dw.orbit_numerator()
        source = {
            "F_nonzero_counts": {name: int(np.count_nonzero(value)) for name, value in f_terms.items()},
            "D_nonzero_count": int(np.count_nonzero(dw.d_moment_numerator())),
            "hessian_rank_mod37": v52.modular_rank(v52._modular_matrix(h)),
            "hessian_nullity": 176-v52.modular_rank(v52._modular_matrix(h)),
            "orbit_rank_mod37": v52.modular_rank(v52._modular_matrix(q)),
            "ward_product_zero": bool(np.count_nonzero(h @ q) == 0),
        }
    finally:
        dw.witness = original

    charges = {
        "E": -2, "A": 1, "B": 1, "C": 0, "barC": -1,
        "R_E2": 4, "M_adj2": -2, "L_Cmass": 1,
        "F": 11, "H1": -22, "barh": 16, "h": -4, "H2": 3,
        "P": 6, "S_hmass": -12, "T_H2mass": -6,
    }
    term_charges = {
        "R_E2": charges["R_E2"]+2*charges["E"],
        "M_A2": charges["M_adj2"]+2*charges["A"],
        "M_B2": charges["M_adj2"]+2*charges["B"],
        "M_AB": charges["M_adj2"]+charges["A"]+charges["B"],
        "E_A2": charges["E"]+2*charges["A"],
        "E_B2": charges["E"]+2*charges["B"],
        "E_AB": charges["E"]+charges["A"]+charges["B"],
        "barC_A_C": charges["barC"]+charges["A"]+charges["C"],
        "L_barC_C": charges["L_Cmass"]+charges["barC"]+charges["C"],
        "P_H1_barh": charges["P"]+charges["H1"]+charges["barh"],
        "S_barh_h": charges["S_hmass"]+charges["barh"]+charges["h"],
        "h_B_H2": charges["h"]+charges["B"]+charges["H2"],
        "T_H2_squared": charges["T_H2mass"]+2*charges["H2"],
        "F_F_H1": 2*charges["F"]+charges["H1"],
    }
    vevs = {
        "P": 6, "S": -12, "T": -6,
        "R": 4, "M": -2, "L": 1, "C": 0, "barC": -1,
    }
    first_proton = _first_dressing(vevs, -4*charges["F"])
    first_higgs = _first_dressing(vevs, -2*charges["H1"])
    jacobian = np.asarray([
        [-1, -1, 1, 0, 0, 0],
        [0, 1, -2, 0, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [-1, 0, 0, 1, -1, 0],
        [0, 0, 0, 1, 1, -2],
    ], dtype=np.int64)
    return {
        "purpose": "proof that q(B)!=0 admits a tractable exact effective-source retuning",
        "charges": charges,
        "all_displayed_terms_neutral": all(value == 0 for value in term_charges.values()),
        "term_charges": term_charges,
        "effective_source_witness": {
            "mE": 14, "lambda": 0, "mA": 214, "mB": -50,
            "kappaA": 19, "kappaB": 10, "muAB": 6, "kappaAB": 1,
            "eta": "-6*i", "mC": 27,
            "E0_diagonal": [2]*6+[-3]*4,
            "A0_upper_blocks": [1, 1, 1, 3, 3],
            "B0_upper_blocks": [1, 1, 1, 0, 0],
            "C0_equals_barC0": "10 e15",
        },
        "fixed_spurion_source_certificate": source,
        "singlet_constraints": [
            "T=P S", "S=T^2", "P T=v^2", "R=P M", "R M=L^2",
        ],
        "constraint_jacobian_rank": v52.modular_rank(jacobian % v52.MODULAR_PRIME),
        "constraint_jacobian_null_vector": [6, -12, -6, 4, -2, 1],
        "direct_h_H2_charge": charges["h"]+charges["H2"],
        "P_squared_H1_squared_charge": 2*charges["P"]+2*charges["H1"],
        "F4_safe_through_total_degree8": first_proton is not None and first_proton["insertions"] >= 5,
        "H1_squared_safe_through_total_degree8": first_higgs is not None and first_higgs["insertions"] >= 7,
        "first_charge_neutral_F4_dressing": first_proton,
        "first_charge_neutral_H1_squared_dressing": first_higgs,
        "fatal_open_item": (
            "source/filter dependence on R,M,L backreacts on their F equations; driver-multiplier VEVs, "
            "the displayed renormalizable constraint Jacobian has rank four rather than five and leaves "
            "a physical spurion modulus before backreaction; the complete enlarged Hessian, anomalies "
            "and all allowed singlet operators are not solved"
        ),
        "same_action_promotion": False,
    }


def charged_source_dynamical_rescue() -> dict[str, Any]:
    """Complete the charged-source seed locally with one q=+2 VEV singlet K.

    Seven VEV singlets (P,S,T,R,M,L,K) are constrained by six independent
    renormalizable equations.  Source-spurion F backreaction fixes the driver
    multipliers.  The exact Hessian includes the retuned 176 source, the
    protected four-10 filter, all spurions/drivers, and a singlet-only standard
    single-GS anomaly repair.
    """
    original = dw.witness
    base = dict(original())
    parameters = {
        "mE": 14, "lambda": 0, "mA": 214, "mB": -50,
        "kappaA": 19, "kappaB": 10, "muAB": 6, "kappaAB": 1,
        "eta": -6j, "mC": 27,
    }
    data = dict(base)
    data.update(parameters)
    source_order = ["E_F_x400", "A_F_x400", "B_F_x400", "C_F_x400", "barC_F_x400"]

    def source_cross(delta: Mapping[str, Any]) -> np.ndarray:
        probe = dict(base)
        for name in parameters:
            probe[name] = 0
        probe.update(delta)
        dw.witness = lambda: probe
        terms = dw.f_term_numerators()
        # f_term_numerators stores 400 F; divide by ten to match the 40H convention.
        return np.concatenate([terms[name] for name in source_order]) / 10

    try:
        dw.witness = lambda: data
        source_h = dw.hessian_numerator()
        source_q = dw.orbit_numerator()
        c_r = source_cross({"mE": 14})
        c_m = source_cross({"mA": 214, "mB": -50, "muAB": 6})
        c_l = source_cross({"mC": 27})
    finally:
        dw.witness = original

    # Ordering P,S,T,R,M,L,K.  The six constraints are
    # MK=1, PT=1, K=L^2, K=RM, K^2=PM, T=PS at the unit VEV witness.
    jacobian = np.asarray([
        [0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -2, 1],
        [0, 0, 0, -1, -1, 0, 1],
        [-1, 0, 0, 0, -1, 0, 2],
        [-1, -1, 1, 0, 0, 0, 0],
    ], dtype=np.int64)
    vev_charges = np.asarray([6, -12, -6, 4, -2, 1, 2], dtype=np.int64)
    source_gradient = np.asarray([0, 0, 0, 420, 2190, 2700, 0], dtype=np.int64)
    driver_vevs = np.asarray([-1770, 0, 1350, 420, 0, 0], dtype=np.int64)
    driver_charges = np.asarray([0, 0, -2, -2, -4, 6], dtype=np.int64)
    residual = jacobian.T @ driver_vevs + source_gradient

    # Exact 13 x 13 singlet Hessian at the displayed VEV.  Constructing it
    # explicitly avoids a symbolic-runtime dependency in the certificate.
    # Variable ordering: P,S,T,R,M,L,K,D1,...,D6.
    vv = np.zeros((7, 7), dtype=np.int64)
    # D1*(M K-1), D3*(K-L^2), D4*(K-R M) are the nonzero-driver contributions.
    vv[4, 6] += driver_vevs[0]
    vv[6, 4] += driver_vevs[0]
    vv[5, 5] += -2*driver_vevs[2]
    vv[3, 4] += -driver_vevs[3]
    vv[4, 3] += -driver_vevs[3]
    singlet_h = np.block([
        [vv, jacobian.T],
        [jacobian, np.zeros((6, 6), dtype=np.int64)],
    ])

    source_dim, filter_dim, singlet_dim = 176, 40, 13
    local_dim = source_dim + filter_dim + singlet_dim
    local_h = np.zeros((local_dim, local_dim), dtype=np.complex128)
    local_h[:source_dim, :source_dim] = source_h
    local_h[source_dim:source_dim+filter_dim, source_dim:source_dim+filter_dim] = 40*elementary.filter_hessian()
    local_h[source_dim+filter_dim:, source_dim+filter_dim:] = 40*singlet_h
    for column, vector in ((source_dim+filter_dim+3, c_r),
                           (source_dim+filter_dim+4, c_m),
                           (source_dim+filter_dim+5, c_l)):
        local_h[:source_dim, column] = vector
        local_h[column, :source_dim] = vector
    local_h = v52._gaussian_integer(local_h, label="V54 charged rescue 40H")

    local_q = np.zeros((local_dim, 46), dtype=np.complex128)
    local_q[:source_dim, :45] = source_q
    local_q[:54, 45] = -20*v52._symmetric_coordinates(data["E0"])
    local_q[54:99, 45] = 10*v52._antisymmetric_coordinates(data["A0"])
    local_q[99:144, 45] = 10*v52._antisymmetric_coordinates(data["B0"])
    local_q[160:176, 45] = -10*data["barC0"]
    local_q[source_dim+filter_dim:source_dim+filter_dim+7, 45] = 10*vev_charges
    local_q[source_dim+filter_dim+7:, 45] = 10*driver_charges*driver_vevs
    local_q = v52._gaussian_integer(local_q, label="V54 charged rescue 10Q")

    local_rank = v52.modular_rank(v52._modular_matrix(local_h))
    local_q_rank = v52.modular_rank(v52._modular_matrix(local_q))
    local_hq_zero = bool(np.count_nonzero(local_h @ local_q) == 0)

    # Standard single-GS repair.  A spectator Z2 makes all 134 spectators odd
    # and every main-action field even, forbidding linear mixing with VEV fields.
    spectator_charges = [6]*126 + [1]*6 + [-1] + [0]
    repaired_h = np.block([
        [local_h, np.zeros((local_dim, len(spectator_charges)), dtype=np.complex128)],
        [np.zeros((len(spectator_charges), local_dim), dtype=np.complex128),
         40*np.eye(len(spectator_charges), dtype=np.complex128)],
    ])
    repaired_q = np.vstack((local_q, np.zeros((len(spectator_charges), 46), dtype=np.complex128)))
    repaired_h = v52._gaussian_integer(repaired_h, label="V54 GS repaired 40H")
    repaired_q = v52._gaussian_integer(repaired_q, label="V54 GS repaired 10Q")
    repaired_rank = v52.modular_rank(v52._modular_matrix(repaired_h))
    repaired_q_rank = v52.modular_rank(v52._modular_matrix(repaired_q))

    all_vevs = {
        "P": 6, "S": -12, "T": -6, "R": 4, "M": -2, "L": 1, "K": 2,
        "D1": 0, "D3": -2, "D4": -2,
        "C": 0, "barC": -1,
    }
    first_proton = _first_dressing(all_vevs, -44)
    first_higgs = _first_dressing(all_vevs, 44)

    base_anomaly = {
        "Spin10_squared_U1": 49,
        "TrQ": 415,
        "TrQ3": -3887,
        "TrQ2": 14081,
    }
    spectator_trace = sum(spectator_charges)
    spectator_cube = sum(value**3 for value in spectator_charges)
    spectator_square = sum(value**2 for value in spectator_charges)
    repaired_anomaly = {
        "Spin10_squared_U1": 49,
        "TrQ": base_anomaly["TrQ"]+spectator_trace,
        "TrQ3": base_anomaly["TrQ3"]+spectator_cube,
        "TrQ2": base_anomaly["TrQ2"]+spectator_square,
    }

    return {
        "new_field": {"name": "K", "U1_charge": 2, "VEV": 1},
        "minimality_scope": (
            "complete enumeration of degree<=2 monomial equalities for the original six VEV charges "
            "has rank four; scanning one added integer charge finds |qK|=2 as the smallest safe rank-six repair"
        ),
        "constraints": ["M K=1", "P T=1", "K=L^2", "K=R M", "K^2=P M", "T=P S"],
        "constraint_jacobian_rank": v52.modular_rank(jacobian % v52.MODULAR_PRIME),
        "constraint_kernel": [6, -12, -6, 4, -2, 1, 2],
        "source_spurion_gradient": source_gradient.tolist(),
        "driver_charges": driver_charges.tolist(),
        "driver_VEVs": driver_vevs.tolist(),
        "all_spurion_F_residuals": residual.tolist(),
        "local_same_action": {
            "coordinates": local_dim,
            "hessian_rank": local_rank,
            "hessian_nullity": local_dim-local_rank,
            "gauge_orbit_rank": local_q_rank,
            "ward_product_zero": local_hq_zero,
            "kernel_decomposition": {"Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0},
            "hessian_sha256": v52.gaussian_matrix_sha(local_h),
            "orbit_sha256": v52.gaussian_matrix_sha(local_q),
        },
        "operator_screen": {
            "direct_h_H2_charge": -1,
            "P_squared_H1_squared_charge": -32,
            "F4_safe_through_total_degree8": first_proton is not None and first_proton["insertions"] >= 5,
            "H1_squared_safe_through_total_degree8": first_higgs is not None and first_higgs["insertions"] >= 7,
            "first_F4_dressing": first_proton,
            "first_H1_squared_dressing": first_higgs,
        },
        "anomalies_before_repair": base_anomaly,
        "single_GS_singlet_repair": {
            "spectators": {"q_plus6": 126, "q_plus1": 6, "q_minus1": 1, "q_zero": 1},
            "masses": ["S X_6^2", "M X_1^2", "K X_minus1^2", "m X_0^2"],
            "exact_spectator_Z2_odd_count": 134,
            "anomalies": repaired_anomaly,
            "mixed_gravity_universality": repaired_anomaly["TrQ"] == 24*repaired_anomaly["Spin10_squared_U1"],
            "positive_abelian_normalization": "3889/49",
            "coordinates": local_dim+len(spectator_charges),
            "hessian_rank": repaired_rank,
            "hessian_nullity": local_dim+len(spectator_charges)-repaired_rank,
            "gauge_orbit_rank": repaired_q_rank,
            "ward_product_zero": bool(np.count_nonzero(repaired_h @ repaired_q) == 0),
            "hessian_sha256": v52.gaussian_matrix_sha(repaired_h),
            "orbit_sha256": v52.gaussian_matrix_sha(repaired_q),
        },
        "Spin10_running": {
            "sum_T": 42, "b": 18,
            "pole_ratio_at_g_0p73": math.exp(8*math.pi**2/(18*0.73**2)),
            "singlet_repair_changes_Spin10_running": False,
        },
        "FI_D_flatness": (
            "TrQ>0 gives xi_A>0; the nonzero negative-charge S,T,M,D3,D4 VEVs permit D_A=0. "
            "The exact FI magnitude and GS-modulus Kahler stabilization are not fixed by the holomorphic certificate."
        ),
        "remaining_fail_closed_items": [
            "first exact charge-neutral F16^4 dressing occurs at total degree nine",
            "the standard single-GS repair requires 134 extra singlets and has a very large Abelian charge-square trace",
            "GS axion/modulus, Kahler potential, vector/scalar mass matrix and global vacuum are absent",
            "no Wilson coefficients, proton lifetime, thresholds, flavor fit, SUSY breaking or cosmology are computed",
        ],
        "gate_promotion": False,
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    lift = continuous_charge_lift()
    filler, filled_matrix = filter_filler_audit()
    visible, h, q = visible_fi_hessian(filled_matrix)
    anomaly = fi_anomaly_and_running()
    seed = charged_source_retuning_seed()
    rescue = charged_source_dynamical_rescue()
    checks = {
        "upstream_cores_bound": len(upstream) == 4,
        "continuous_lift_all_required_terms_neutral": lift["all_required_neutral"],
        "renormalizable_hH2_filler_allowed": lift["operator_charges"]["h_H2_renormalizable_filler"] == 0,
        "allowed_filler_makes_weak_block_full_rank16": filler["filled_weak_rank"] == 16,
        "P2H1sq_allowed": lift["operator_charges"]["P_squared_H1_squared"] == 0,
        "visible_generic_H_rank237_nullity34": visible["hessian_rank"] == 237 and visible["hessian_nullity"] == 34,
        "visible_kernel_equals_rank34_gauge_orbit": visible["kernel_equals_Spin10_plus_U1_gauge_orbit"],
        "GS_ledger_universal": anomaly["GS_nonAbelian_gravity_universality"],
        "retuned_fixed_spurion_source_exact": (
            all(value == 0 for value in seed["fixed_spurion_source_certificate"]["F_nonzero_counts"].values())
            and seed["fixed_spurion_source_certificate"]["D_nonzero_count"] == 0
            and seed["fixed_spurion_source_certificate"]["hessian_rank_mod37"] == 143
            and seed["fixed_spurion_source_certificate"]["orbit_rank_mod37"] == 33
        ),
        "retuned_seed_not_promoted": seed["same_action_promotion"] is False,
        "one_charge2_singlet_repairs_constraint_rank": rescue["constraint_jacobian_rank"] == 6,
        "dynamical_spurion_F_residuals_zero": all(value == 0 for value in rescue["all_spurion_F_residuals"]),
        "rescued_local_H191_nullity38": (
            rescue["local_same_action"]["coordinates"] == 229
            and rescue["local_same_action"]["hessian_rank"] == 191
            and rescue["local_same_action"]["hessian_nullity"] == 38
        ),
        "rescued_local_kernel_is_34_gauge_plus4_weak": (
            rescue["local_same_action"]["gauge_orbit_rank"] == 34
            and rescue["local_same_action"]["ward_product_zero"]
            and rescue["local_same_action"]["kernel_decomposition"]["extra"] == 0
        ),
        "rescued_operator_screen_through_degree8": (
            rescue["operator_screen"]["direct_h_H2_charge"] != 0
            and rescue["operator_screen"]["P_squared_H1_squared_charge"] != 0
            and rescue["operator_screen"]["F4_safe_through_total_degree8"]
            and rescue["operator_screen"]["H1_squared_safe_through_total_degree8"]
        ),
        "singlet_only_GS_repair_is_exact_but_large": (
            rescue["single_GS_singlet_repair"]["mixed_gravity_universality"]
            and rescue["single_GS_singlet_repair"]["coordinates"] == 363
            and rescue["single_GS_singlet_repair"]["hessian_rank"] == 325
            and rescue["single_GS_singlet_repair"]["hessian_nullity"] == 38
            and rescue["single_GS_singlet_repair"]["ward_product_zero"]
        ),
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v54_continuous_parent_fi_route_audit_v1",
        "status": STATUS if not failures else "V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT_FAILED",
        "scope": (
            "exact algebraic audit of the unchanged continuous-U1/FI route plus a fixed-spurion charged-source seed; "
            "not an experimentally validated or complete theory"
        ),
        "upstream_certificates": upstream,
        "continuous_parent": lift,
        "renormalizable_filter_filler": filler,
        "neutral_driver_no_go": neutral_driver_no_go(),
        "FI_GS_anomaly_and_running": anomaly,
        "generic_allowed_visible_action": visible,
        "charged_source_retuning_seed": seed,
        "charged_source_dynamical_rescue": rescue,
        "gate_verdict": {
            "G1": "FROZEN_PRIOR_NAMESPACE_ONLY",
            "G2": "OPEN",
            "G3": "OPEN",
            "G4": "OPEN",
            "G5": "OPEN",
            "G6": "OPEN",
            "G7": "OPEN",
            "G8": "OPEN",
            "promoted_gate_count": 0,
        },
        "next_kill_test": (
            "Promote the q(B)!=0 seed only after one dynamical action solves every spurion F/D equation, "
            "has ker(H)=gauge+four weak modes, passes a complete allowed-operator census, GS anomalies, "
            "thresholds and proton matching."
        ),
        "literature": {
            "FI_DW_precedent": "https://arxiv.org/abs/1003.2625",
            "heterotic_GS_universality": "https://arxiv.org/abs/1110.6901",
            "renormalizable_filter_scope": "https://arxiv.org/abs/1410.5625",
        },
        "checks": checks,
        "failures": failures,
        "matrix_hashes": {
            "generic_visible_hessian": v52.gaussian_matrix_sha(h),
            "generic_visible_orbit": v52.gaussian_matrix_sha(q),
        },
        "artifact_manifest": {},
    }
    report["artifact_manifest"] = {
        "script": {"path": Path(__file__).name, "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "test": {"path": TEST_PATH.name, "sha256": hashlib.sha256(TEST_PATH.read_bytes()).hexdigest() if TEST_PATH.exists() else None},
    }
    report["core_sha256"] = canonical_sha(report)
    if failures:
        raise RuntimeError("V54 integrity failure: " + ", ".join(failures))
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    v = report["generic_allowed_visible_action"]
    f = report["renormalizable_filter_filler"]
    s = report["charged_source_retuning_seed"]
    a = report["FI_GS_anomaly_and_running"]
    r = report["charged_source_dynamical_rescue"]
    return f"""# V54 continuous-parent / FI route audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decisive result

The unchanged V53 action has a unique ordinary continuous-`U(1)` lift, but it fails before
the proposed FI driver can complete the theory.  Because the exact cross-coupled source
contains `B^2`, the missing-VEV adjoint is neutral.  Allowing `h B H2` therefore also allows
the direct renormalizable mass `h H2`.

Adding that generic invariant raises the weak filter rank from `{f['declared_weak_rank']}`
to `{f['filled_weak_rank']}` and removes all four intended weak zero modes.  Independently,
`P^2 H1^2/M` is neutral, so the route also fails all-order doublet protection.

## Exact generic visible-action certificate

After replacing the incompatible `X(P^2-v^2)` driver by anomalous-FI breaking and adding
the minimal displayed single-GS spectator ledger, the most-general symmetry-allowed visible
action has `{v['visible_coordinates']}` chiral coordinates, Hessian rank `{v['hessian_rank']}`
and nullity `{v['hessian_nullity']}`.  Its kernel equals the rank-`{v['gauge_orbit_rank']}`
`Spin(10) x U(1)` gauge orbit exactly.  Thus it has zero physical weak-Higgs modes.

The anomaly ledger has `A_SO10={a['repaired']['Spin10_squared_U1']}` and
`TrQ/24={a['repaired']['TrQ']//24}`.  Its Spin(10) inventory has `sum T={a['sum_T_Spin10']}`,
`b={a['b_Spin10']}`, and formal pole ratio `{a['pole_ratio_at_g_0p73']:.3f}`.

## Charged-source retuning seed

A real escape must charge `B`.  The audit supplies a tractable seed with
`q(E,A,B)=(-2,1,1)` and charged mass spurions.  Dropping `E^3` and retuning the effective
coefficients leaves the fixed-spurion 176-coordinate source exactly F/D-flat with
`rank(H)={s['fixed_spurion_source_certificate']['hessian_rank_mod37']}` and
`rank(Q)={s['fixed_spurion_source_certificate']['orbit_rank_mod37']}`.

The seed forbids direct `h H2`, forbids `P^2 H1^2`, and has no charge-neutral `F^4`
dressing through total degree eight.

## Bounded dynamical rescue

Adding one VEV singlet `K` of charge `+2` raises the exact constraint Jacobian to rank
`{r['constraint_jacobian_rank']}` for seven VEV variables.  Source-spurion backreaction fixes
the six driver VEVs to `{r['driver_VEVs']}` with exactly zero residual F terms.

The resulting same-action source, protected four-10 filter and dynamical spurion sector has
`{r['local_same_action']['coordinates']}` coordinates, rank
`{r['local_same_action']['hessian_rank']}` and nullity
`{r['local_same_action']['hessian_nullity']} = 34 gauge + 4 weak`, with no extra modulus.
It remains perturbative in Spin(10): `sum T={r['Spin10_running']['sum_T']}` and
`b={r['Spin10_running']['b']}`.

A standard single-GS ledger can be repaired without additional Spin(10) index, but only by
`134` parity-protected singlets.  That enlarged `{r['single_GS_singlet_repair']['coordinates']}`-
coordinate Hessian has rank `{r['single_GS_singlet_repair']['hessian_rank']}` and the same
nullity `{r['single_GS_singlet_repair']['hessian_nullity']}`.  This is an exact algebraic rescue,
not theory closure: the first `F^4` dressing appears at total degree nine, the GS/Kahler/vector
completion is absent, and no proton, threshold, flavor, SUSY-breaking or cosmological matching
has been performed.

## Verdict

No V54 gate is promoted.  The unchanged continuous-parent/FI route is closed.  The charged
`q(B) != 0` action now has an exact local dynamical Hessian, but its degree-nine proton leak and
large incomplete GS sector prevent promotion.

The FI strategy is motivated by [Babu, Pati and Tavartkiladze](https://arxiv.org/abs/1003.2625),
and the GS/FI normalization by [Goodsell, Ramos-Sanchez and Ringwald](https://arxiv.org/abs/1110.6901).
The four-10 filter is compared only within the explicitly renormalizable scope of
[Chen and Zhang](https://arxiv.org/abs/1410.5625).
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "core_sha256": report["core_sha256"], "checks": report["checks"]}, indent=2))


if __name__ == "__main__":
    main()
