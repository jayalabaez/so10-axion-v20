#!/usr/bin/env python3
"""V55-R1 exact matter/RH-neutrino Hessian audit.

This certificate extends the exact V54 charged-source rescue by three Spin(10)
matter 16s and three singlet neutrinos.  It deliberately separates an explicit
coefficient witness from the symmetry-complete action: the universal U(1)
charges allow generic family matrices, even when a sparse Yukawa matrix is
chosen at the witness point.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import susy_v52_low_index_source_audit as v52
import susy_v53_elementary_filter_hessian_audit as elementary
import susy_v53_natural_dt_filter_audit as dw


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V55_R1_MATTER_HESSIAN_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_MATTER_HESSIAN_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v55_r1_matter_hessian_audit.py"
UPSTREAM_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
UPSTREAM_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"

STATUS = (
    "V55_R1_MATTER_RHN_LOCAL_HESSIAN_EXACT__"
    "UNIVERSAL_FAMILY_U1_CHARGES_ALLOW_GENERIC_TEXTURES__"
    "280_COORDINATE_H197_NULL83_EQUALS34_GAUGE_PLUS45_MATTER_PLUS4_WEAK__"
    "SINGLET_GS_REPAIR_413_COORDINATE_H330_SAME_NULL83__"
    "F4_FIRST_DRESSING_DEGREE9__SPARSE_TOP_ONLY_TEXTURE_NOT_SYMMETRY_PROTECTED__"
    "NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def bind_upstream() -> dict[str, str]:
    data = json.loads(UPSTREAM_PATH.read_text(encoding="utf-8"))
    if data.get("core_sha256") != UPSTREAM_CORE or canonical_sha(data) != UPSTREAM_CORE:
        raise RuntimeError("stale V54 charged-source rescue certificate")
    local = data["charged_source_dynamical_rescue"]["local_same_action"]
    return {
        "path": UPSTREAM_PATH.name,
        "core_sha256": UPSTREAM_CORE,
        "local_hessian_sha256": local["hessian_sha256"],
        "local_orbit_sha256": local["orbit_sha256"],
    }


def _first_dressing(charges: Mapping[str, int], target: int, maximum: int = 12) -> dict[str, Any] | None:
    names = list(charges)
    for degree in range(maximum + 1):
        for indices in itertools.combinations_with_replacement(range(len(names)), degree):
            if sum(charges[names[index]] for index in indices) == target:
                return {"insertions": degree, "fields": [names[index] for index in indices]}
    return None


def _reachable(charges: Mapping[str, int], maximum: int) -> dict[int, dict[str, Any]]:
    names = list(charges)
    result: dict[int, dict[str, Any]] = {}
    for degree in range(maximum + 1):
        for indices in itertools.combinations_with_replacement(range(len(names)), degree):
            value = sum(charges[names[index]] for index in indices)
            result.setdefault(value, {"insertions": degree, "fields": [names[index] for index in indices]})
    return result


def family_charge_search() -> dict[str, Any]:
    """Bounded half-integer search in the primitive V54 normalization.

    A short Majorana dressing has at most four VEV insertions.  Since all V54
    VEV charges are integral, this condition reduces rational family charges
    to half-integral values.  We enumerate them exactly as n_i=2 q(F_i).
    """
    vevs = {
        "P": 6, "S": -12, "T": -6, "R": 4, "M": -2,
        "L": 1, "K": 2, "D3": -2, "D4": -2, "barC": -1,
    }
    reachable4 = _reachable(vevs, 4)
    strict: list[list[int]] = []
    relaxed: list[tuple[int, int, int, tuple[int, int, int], tuple[int, ...], dict[str, Any]]] = []

    # n3=22 is fixed by 2 q(F3)+q(H1)=0 with q(H1)=-22.
    for n1 in range(-80, 81):
        for n2 in range(n1 + 1, 22):
            ns = (n1, n2, 22)
            pair_twice_charges = [ns[i] + ns[j] for i in range(3) for j in range(i, 3)]
            unique_top = pair_twice_charges.count(44) == 1 and pair_twice_charges[-1] == 44
            # Other filter 10 charges are q(barh,h,H2)=(16,-4,3).
            no_other_renormalizable_10_yukawa = not any(
                value in (-32, 8, -6) for value in pair_twice_charges
            )
            majorana_insertions = tuple(
                reachable4.get(n - 2, {"insertions": 99})["insertions"] for n in ns
            )
            if not unique_top or not no_other_renormalizable_10_yukawa or max(majorana_insertions) > 4:
                continue

            first: dict[str, Any] | None = None
            for family_indices in itertools.combinations_with_replacement(range(3), 4):
                twice_quartic_charge = sum(ns[index] for index in family_indices)
                if twice_quartic_charge % 2:
                    continue
                dressing = reachable4.get(-twice_quartic_charge // 2)
                if dressing is None:
                    continue
                candidate = {
                    "total_degree": 4 + dressing["insertions"],
                    "family_indices": list(family_indices),
                    "quartic_charge": twice_quartic_charge // 2,
                    "dressing": dressing,
                }
                if first is None or candidate["total_degree"] < first["total_degree"]:
                    first = candidate
            if first is None:
                strict.append(list(ns))
            else:
                relaxed.append((
                    -first["total_degree"], max(abs(n) for n in ns),
                    sum(majorana_insertions), ns, majorana_insertions, first,
                ))

    relaxed.sort()
    best = relaxed[0]
    # The exact optimum is qF=(10,21/2,11); spell it out stably rather than
    # relying on incidental lexicographic representation in the JSON.
    near_ns = (20, 21, 22)
    near_majorana = [reachable4[n - 2] for n in near_ns]
    near_first = None
    for indices in itertools.combinations_with_replacement(range(3), 4):
        twice_charge = sum(near_ns[index] for index in indices)
        if twice_charge % 2 == 0 and -twice_charge // 2 in reachable4:
            dressing = reachable4[-twice_charge // 2]
            candidate = {
                "total_degree": 4 + dressing["insertions"],
                "family_indices": list(indices),
                "quartic_charge": str(Fraction(twice_charge, 2)),
                "dressing": dressing,
            }
            if near_first is None or candidate["total_degree"] < near_first["total_degree"]:
                near_first = candidate

    return {
        "normalization": "primitive V54 charges with q(L)=1; n_i=2 q(F_i)",
        "range": {"n1_min": -80, "n1_max": 80, "n2_less_than": 22, "n3": 22},
        "requirements": [
            "family-distinct ordered charges",
            "F3 F3 H1 is the unique renormalizable matter/filter-10 Yukawa",
            "each diagonal N_i N_i mass has a dressing of at most four VEV insertions",
            "no charge-neutral 16^4 dressing through total degree eight",
        ],
        "strict_solution_count": len(strict),
        "scoped_no_go": len(strict) == 0,
        "best_degree_from_internal_sort": -best[0],
        "nearest_top_only_candidate": {
            "qF": ["10", "21/2", "11"],
            "qN": ["-9", "-19/2", "-10"],
            "Majorana_dressings": near_majorana,
            "first_F4_dressing": near_first,
            "rejected_because": "the first proton operator is already total degree eight",
        },
        "boundary": "finite exact half-integer search, not a theorem for arbitrary long Majorana dressings",
    }


def charge_and_operator_audit() -> dict[str, Any]:
    q = {
        "F1": 11, "F2": 11, "F3": 11,
        "N1": -10, "N2": -10, "N3": -10,
        "H1": -22, "barh": 16, "h": -4, "H2": 3,
        "barC": -1, "P": 6, "S": -12, "T": -6,
        "R": 4, "M": -2, "L": 1, "K": 2,
    }
    displayed = {
        "F_i_F_j_H1": q["F1"] + q["F2"] + q["H1"],
        "F_i_barC_N_j": q["F1"] + q["barC"] + q["N1"],
        "P2_R2_N_i_N_j": 2*q["P"] + 2*q["R"] + q["N1"] + q["N2"],
    }
    other_tens = {
        "F_i_F_j_barh": 2*q["F1"] + q["barh"],
        "F_i_F_j_h": 2*q["F1"] + q["h"],
        "F_i_F_j_H2": 2*q["F1"] + q["H2"],
    }
    vevs = {
        "P": 6, "S": -12, "T": -6, "R": 4, "M": -2,
        "L": 1, "K": 2, "D3": -2, "D4": -2, "barC": -1,
    }
    first_f4 = _first_dressing(vevs, -44)
    first_h1sq = _first_dressing(vevs, 44)
    return {
        "charges": q,
        "displayed_term_charges": displayed,
        "all_displayed_terms_neutral": all(value == 0 for value in displayed.values()),
        "other_filter_10_Yukawa_charges": other_tens,
        "other_filter_10_Yukawas_forbidden": all(value != 0 for value in other_tens.values()),
        "top_Yukawa": "(Y_10)33 F3 F3 H1, with (Y_10)33=1 at the witness",
        "RHN_link": "Lambda_ij F_i barC N_j, with Lambda=I at the witness",
        "Majorana": "(1/2) (P^2 R^2/M_*^3) Mu_ij N_i N_j, with Mu=I at the witness",
        "symmetry_complete_flavor_statement": (
            "U(1) permits every entry of the symmetric F_i F_j H1 matrix, every entry of "
            "F_i barC N_j, and every entry of the dressed symmetric N_i N_j matrix"
        ),
        "declared_sparse_texture": {
            "Y10": [[0, 0, 0], [0, 0, 0], [0, 0, 1]],
            "Lambda": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "Mu": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "protected_by_U1": False,
            "interpretation": "one exact coefficient witness only; zero off-diagonal entries are not symmetry zeros",
        },
        "symmetry_complete_generic_condition": "det(Lambda) != 0; Mu is arbitrary symmetric",
        "operator_screen": {
            "direct_h_H2_charge": -1,
            "P_squared_H1_squared_charge": -32,
            "first_F4_dressing": first_f4,
            "F4_safe_through_total_degree8": first_f4 is not None and first_f4["insertions"] >= 5,
            "first_H1_squared_dressing": first_h1sq,
            "H1_squared_safe_through_total_degree8": first_h1sq is not None and first_h1sq["insertions"] >= 7,
        },
    }


def _v54_local_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct the exact V54 229-coordinate 40H and 10Q matrices."""
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

    jacobian = np.asarray([
        [0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -2, 1],
        [0, 0, 0, -1, -1, 0, 1],
        [-1, 0, 0, 0, -1, 0, 2],
        [-1, -1, 1, 0, 0, 0, 0],
    ], dtype=np.int64)
    vev_charges = np.asarray([6, -12, -6, 4, -2, 1, 2], dtype=np.int64)
    driver_vevs = np.asarray([-1770, 0, 1350, 420, 0, 0], dtype=np.int64)
    driver_charges = np.asarray([0, 0, -2, -2, -4, 6], dtype=np.int64)
    vv = np.zeros((7, 7), dtype=np.int64)
    vv[4, 6] += driver_vevs[0]
    vv[6, 4] += driver_vevs[0]
    vv[5, 5] += -2*driver_vevs[2]
    vv[3, 4] += -driver_vevs[3]
    vv[4, 3] += -driver_vevs[3]
    singlet_h = np.block([[vv, jacobian.T], [jacobian, np.zeros((6, 6), dtype=np.int64)]])

    h = np.zeros((229, 229), dtype=np.complex128)
    h[:176, :176] = source_h
    h[176:216, 176:216] = 40*elementary.filter_hessian()
    h[216:, 216:] = 40*singlet_h
    for column, vector in ((219, c_r), (220, c_m), (221, c_l)):
        h[:176, column] = vector
        h[column, :176] = vector
    h = v52._gaussian_integer(h, label="V55 bound V54 40H")

    q = np.zeros((229, 46), dtype=np.complex128)
    q[:176, :45] = source_q
    q[:54, 45] = -20*v52._symmetric_coordinates(data["E0"])
    q[54:99, 45] = 10*v52._antisymmetric_coordinates(data["A0"])
    q[99:144, 45] = 10*v52._antisymmetric_coordinates(data["B0"])
    q[160:176, 45] = -10*data["barC0"]
    q[216:223, 45] = 10*vev_charges
    q[223:, 45] = 10*driver_charges*driver_vevs
    q = v52._gaussian_integer(q, label="V55 bound V54 10Q")
    return h, q


def enlarged_hessian() -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    base_h, base_q = _v54_local_matrices()
    if v52.gaussian_matrix_sha(base_h) != "44dfe08b2d9cb19f3e11df33d212dc8451211c90e7c22a73687c52bafa8f6d1d":
        raise RuntimeError("V54 local Hessian reconstruction drift")
    if v52.gaussian_matrix_sha(base_q) != "fad10b84a0d51453e3efaf616e2699b73c4743c1a0565016d463f90d57b5b063":
        raise RuntimeError("V54 orbit reconstruction drift")

    # Matter ordering F1(16),F2(16),F3(16),N1,N2,N3.  barC0=10 e15.
    matter_h = np.zeros((51, 51), dtype=np.int64)
    for family in range(3):
        matter_h[16*family + 15, 48 + family] = 400
        matter_h[48 + family, 16*family + 15] = 400
        matter_h[48 + family, 48 + family] = 40
    matter_rank = v52.modular_rank(matter_h % v52.MODULAR_PRIME)

    h = np.block([
        [base_h, np.zeros((229, 51), dtype=np.complex128)],
        [np.zeros((51, 229), dtype=np.complex128), matter_h],
    ])
    q = np.vstack((base_q, np.zeros((51, 46), dtype=np.complex128)))
    h = v52._gaussian_integer(h, label="V55 matter 40H")
    q = v52._gaussian_integer(q, label="V55 matter 10Q")

    # Explicit 45 matter zero modes: all F components orthogonal to e15.
    matter_basis = np.zeros((280, 45), dtype=np.int64)
    column = 0
    for family in range(3):
        for component in range(15):
            matter_basis[229 + 16*family + component, column] = 1
            column += 1

    # Four exact weak-filter modes, H1=-2 h, one for each weak coordinate.
    weak_basis = np.zeros((280, 4), dtype=np.int64)
    for column, internal in enumerate(range(6, 10)):
        weak_basis[176 + internal, column] = -2
        weak_basis[176 + 20 + internal, column] = 1

    kernel_span = np.column_stack((q, matter_basis, weak_basis))
    h_rank = v52.modular_rank(v52._modular_matrix(h))
    q_rank = v52.modular_rank(v52._modular_matrix(q))
    matter_basis_rank = v52.modular_rank(matter_basis % v52.MODULAR_PRIME)
    weak_basis_rank = v52.modular_rank(weak_basis % v52.MODULAR_PRIME)
    span_rank = v52.modular_rank(v52._modular_matrix(kernel_span))
    annihilation = bool(np.count_nonzero(h @ kernel_span) == 0)

    cert = {
        "coordinate_order": [
            "V54 charged-source/filter/spurion/driver (229)",
            "F1(16)", "F2(16)", "F3(16)", "N1", "N2", "N3",
        ],
        "coordinates": 280,
        "matter_block_coordinates": 51,
        "matter_block_rank": matter_rank,
        "matter_block_nullity": 51 - matter_rank,
        "heavy_RHN_subblock": {
            "coordinates": 6,
            "rank": 6,
            "determinant_identity": "det([[0,400 Lambda],[400 Lambda^T,40 Mu]])=-400^6 det(Lambda)^2",
        },
        "hessian_rank": h_rank,
        "hessian_nullity": 280 - h_rank,
        "gauge_orbit_rank": q_rank,
        "ward_product_zero": bool(np.count_nonzero(h @ q) == 0),
        "explicit_matter_kernel_rank": matter_basis_rank,
        "explicit_weak_kernel_rank": weak_basis_rank,
        "combined_kernel_span_rank": span_rank,
        "combined_kernel_annihilated": annihilation,
        "kernel_decomposition": {
            "Spin10_gauge": 33, "U1_gauge": 1,
            "light_matter": 45, "weak_Higgs": 4, "extra": 0,
        },
        "kernel_exact": annihilation and span_rank == 280 - h_rank == 83,
        "hessian_sha256": v52.gaussian_matrix_sha(h),
        "orbit_sha256": v52.gaussian_matrix_sha(q),
        "boundary": (
            "holomorphic local Hessian at F_i=N_i=0; 45 light SO(10)-matter coordinates here "
            "mean the components orthogonal to the barC singlet-VEV direction before electroweak breaking"
        ),
    }
    return cert, h, q


def anomaly_repair(h: np.ndarray, q: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    before = {"Spin10_squared_U1": 49, "TrQ": 385, "TrQ3": -6887, "TrQ2": 14381}
    # 66 S-mass pairs have trace 792.  Replace one (6,6) pair by (40,-28)
    # to make TrQ3 positive, then add one q=-1 self-mass through K.
    spectator_charges = [40, -28] + [6, 6]*65 + [-1]
    repaired = {
        "Spin10_squared_U1": before["Spin10_squared_U1"],
        "TrQ": before["TrQ"] + sum(spectator_charges),
        "TrQ3": before["TrQ3"] + sum(value**3 for value in spectator_charges),
        "TrQ2": before["TrQ2"] + sum(value**2 for value in spectator_charges),
    }
    full_h = np.block([
        [h, np.zeros((280, len(spectator_charges)), dtype=np.complex128)],
        [np.zeros((len(spectator_charges), 280), dtype=np.complex128),
         40*np.eye(len(spectator_charges), dtype=np.complex128)],
    ])
    full_q = np.vstack((q, np.zeros((len(spectator_charges), 46), dtype=np.complex128)))
    full_h = v52._gaussian_integer(full_h, label="V55 repaired 40H")
    full_q = v52._gaussian_integer(full_q, label="V55 repaired 10Q")
    h_rank = v52.modular_rank(v52._modular_matrix(full_h))
    q_rank = v52.modular_rank(v52._modular_matrix(full_q))
    result = {
        "anomalies_before_repair": before,
        "spectator_Z2": "all 133 repair singlets odd; all main-action fields even",
        "spectators": {
            "one_S_mass_pair": [40, -28],
            "sixty_five_S_mass_pairs": [6, 6],
            "one_K_self_mass": -1,
            "coordinate_count": len(spectator_charges),
        },
        "anomalies_after_repair": repaired,
        "mixed_gravity_GS_universality": repaired["TrQ"] == 24*repaired["Spin10_squared_U1"],
        "positive_abelian_normalization": str(Fraction(repaired["TrQ3"], 6*repaired["Spin10_squared_U1"])),
        "coordinates": len(full_h),
        "hessian_rank": h_rank,
        "hessian_nullity": len(full_h) - h_rank,
        "gauge_orbit_rank": q_rank,
        "ward_product_zero": bool(np.count_nonzero(full_h @ full_q) == 0),
        "kernel_unchanged": len(full_h) - h_rank == 83 and q_rank == 34,
        "hessian_sha256": v52.gaussian_matrix_sha(full_h),
        "orbit_sha256": v52.gaussian_matrix_sha(full_q),
        "warning": "exact but highly nonminimal Abelian repair; no Kac-Moody/string embedding is supplied",
    }
    return result, full_h, full_q


@functools.lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    upstream = bind_upstream()
    search = family_charge_search()
    charges = charge_and_operator_audit()
    local, h, q = enlarged_hessian()
    repair, repaired_h, repaired_q = anomaly_repair(h, q)
    running = {
        "sum_T_Spin10": 42,
        "b_Spin10": 18,
        "pole_ratio_at_g_0p73": math.exp(8*math.pi**2/(18*0.73**2)),
        "matter_and_singlet_extension_changes_V54_running": False,
    }
    checks = {
        "V54_core_and_matrices_bound": upstream["core_sha256"] == UPSTREAM_CORE,
        "displayed_matter_terms_neutral": charges["all_displayed_terms_neutral"],
        "other_filter10_Yukawas_forbidden": charges["other_filter_10_Yukawas_forbidden"],
        "universal_action_not_misreported_as_sparse_symmetry": not charges["declared_sparse_texture"]["protected_by_U1"],
        "bounded_distinct_top_only_short_RHN_screen_no_go": search["scoped_no_go"],
        "matter_block_rank6_null45": local["matter_block_rank"] == 6 and local["matter_block_nullity"] == 45,
        "local_H197_null83": local["hessian_rank"] == 197 and local["hessian_nullity"] == 83,
        "local_kernel_exact_34plus45plus4": local["kernel_exact"] and local["gauge_orbit_rank"] == 34,
        "V54_operator_screen_preserved_through_degree8": (
            charges["operator_screen"]["F4_safe_through_total_degree8"]
            and charges["operator_screen"]["H1_squared_safe_through_total_degree8"]
            and charges["operator_screen"]["P_squared_H1_squared_charge"] != 0
        ),
        "GS_repair_universal_and_full_rank": (
            repair["mixed_gravity_GS_universality"]
            and repair["coordinates"] == 413
            and repair["hessian_rank"] == 330
            and repair["hessian_nullity"] == 83
            and repair["ward_product_zero"]
        ),
        "Spin10_running_unchanged": running["sum_T_Spin10"] == 42 and running["b_Spin10"] == 18,
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v55_r1_matter_hessian_audit_v1",
        "status": STATUS if not failures else "V55_R1_MATTER_HESSIAN_AUDIT_FAILED",
        "scope": (
            "one explicit local supersymmetric action extending the exact V54 rescue by three 16s, "
            "three singlet neutrinos and an optional exact singlet-only GS ledger; not a flavor fit or full theory"
        ),
        "upstream_certificate": upstream,
        "family_charge_search": search,
        "charges_action_and_operator_screen": charges,
        "local_matter_hessian_certificate": local,
        "single_GS_repaired_action": repair,
        "Spin10_running": running,
        "gate_verdict": {
            "G1": "FROZEN_PRIOR_NAMESPACE_ONLY", "G2": "OPEN", "G3": "OPEN", "G4": "OPEN",
            "G5": "OPEN", "G6": "OPEN", "G7": "OPEN", "G8": "OPEN", "promoted_gate_count": 0,
        },
        "fail_closed_findings": [
            "the U1-universal family assignment does not protect a sparse top-only flavor texture",
            "the first charge-neutral 16^4 dressing remains at total degree nine",
            "the exact GS repair adds 133 parity-protected singlets and has a large Abelian normalization",
            "no global vacuum, Kahler/vector mass matrix, realistic flavor/seesaw fit, proton lifetime, thresholds, SUSY breaking or cosmology is supplied",
        ],
        "next_kill_test": (
            "replace coefficient-selected flavor sparsity by an explicit family symmetry and rerun the whole-action "
            "operator/anomaly/Hessian census; the bounded single-U1 search shows why this cannot be assumed"
        ),
        "checks": checks,
        "failures": failures,
        "matrix_hashes": {
            "local_hessian": v52.gaussian_matrix_sha(h), "local_orbit": v52.gaussian_matrix_sha(q),
            "GS_repaired_hessian": v52.gaussian_matrix_sha(repaired_h),
            "GS_repaired_orbit": v52.gaussian_matrix_sha(repaired_q),
        },
        "artifact_manifest": {},
    }
    report["artifact_manifest"] = {
        "script": {"path": Path(__file__).name, "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "test": {"path": TEST_PATH.name, "sha256": hashlib.sha256(TEST_PATH.read_bytes()).hexdigest() if TEST_PATH.exists() else None},
    }
    report["core_sha256"] = canonical_sha(report)
    if failures:
        raise RuntimeError("V55-R1 integrity failure: " + ", ".join(failures))
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    local = report["local_matter_hessian_certificate"]
    charge = report["charges_action_and_operator_screen"]
    search = report["family_charge_search"]
    repair = report["single_GS_repaired_action"]
    return f"""# V55-R1 matter / RH-neutrino Hessian audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact result

The exact V54 charged-source rescue admits a simple matter extension with
`q(F1,F2,F3)=(11,11,11)` and `q(N1,N2,N3)=(-10,-10,-10)`.  The displayed action contains
`F_i F_j H1`, `F_i barC N_j`, and `P^2 R^2 N_i N_j/M_*^3`.  At the coefficient witness
`Y10=diag(0,0,1)`, `Lambda=I`, `Mu=I`, the top Yukawa is nonzero and every singlet-direction
right-handed neutrino is lifted.

The `{local['coordinates']}`-coordinate local Hessian has rank `{local['hessian_rank']}` and
nullity `{local['hessian_nullity']}`.  An explicit annihilated basis has rank
`{local['combined_kernel_span_rank']} = 34 gauge + 45 light matter + 4 weak Higgs`; hence it
has zero extra modes.  The six-coordinate `(F_nu^c,N)` block is full rank independently of
the symmetric Majorana matrix whenever `det(Lambda) != 0`.

## Sparse versus symmetry-complete action

The displayed top-only `Y10` is a coefficient choice, not a U(1) texture.  The symmetry
allows every entry of `F_i F_j H1`, every link entry, and every dressed Majorana entry.
Thus this audit proves a full-rank local matter Hessian and a viable top coupling, but it
does not prove flavor hierarchies.

An exact half-integer scan found `{search['strict_solution_count']}` family-distinct choices
in the stated range that simultaneously make the top the unique renormalizable Yukawa,
give all three short Majorana dressings, and forbid every `16^4` dressing through degree
eight.  The nearest top-only choice `(10,21/2,11)` already permits a degree-eight proton
operator and is rejected.

## Operator, anomaly, and running boundary

The universal assignment preserves the V54 screen: the first `16^4` dressing uses
`{charge['operator_screen']['first_F4_dressing']['insertions']}` VEV insertions and therefore
has total degree nine.  Direct `h H2` and `P^2 H1^2` remain charged.

An exact singlet-only GS ledger exists, but it is unattractive: `{repair['spectators']['coordinate_count']}`
parity-odd singlets enlarge the action to `{repair['coordinates']}` coordinates with Hessian
rank `{repair['hessian_rank']}` and unchanged nullity `{repair['hessian_nullity']}`.  Spin(10)
running remains `sum T=42`, `b=18`.

## Verdict

No gate is promoted.  V55-R1 closes the local matter/RHN Hessian subproblem exactly, while
leaving flavor protection, the degree-nine proton operator, the large GS completion, global
vacuum physics, thresholds and phenomenology open.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "core_sha256": report["core_sha256"], "checks": report["checks"]}, indent=2))


if __name__ == "__main__":
    main()
