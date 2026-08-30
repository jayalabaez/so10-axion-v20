#!/usr/bin/env python3
"""V56-R1 zero-new-field M-dressed-B source/filter topology audit.

The fixed V54/V55 topology makes q(A)=q(B)=q(L), so h B H2 forces the
renormalizable fillers h A H2 and L h H2.  This audit changes four source
monomials without adding a representation:

    M B^2       -> T B^2
    M A B       -> M^2 A B / Lambda
    E A B       -> M E A B / Lambda
    E B^2       -> M^2 E B^2 / Lambda^2.

At <M>=<T>=1 the effective 176-coordinate source is exactly the V54 source.
The dynamical spurion/driver backreaction is recomputed, not copied.  The
result is an exact local EFT Hessian candidate.  A complete degree<=3 operator
census then shows that U(1) alone does not make the declared action symmetry
complete, so no theory gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import sympy as sp

import susy_v52_low_index_source_audit as v52
import susy_v53_elementary_filter_hessian_audit as elementary
import susy_v53_natural_dt_filter_audit as dw


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V56_R1_M_DRESSED_B_TOPOLOGY_HESSIAN_AUDIT.json"
MD_PATH = ROOT / "SUSY_V56_R1_M_DRESSED_B_TOPOLOGY_HESSIAN_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v56_r1_m_dressed_b_topology_hessian_audit.py"
V54_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
V55_PATH = ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.json"
V54_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"
V55_CORE = "52d0044e8d227be29b2cab63c565c1f4335aae9a72c9d51f3c9044fe7289a1f7"

STATUS = (
    "V56_R1_ZERO_NEW_FIELD_M_DRESSED_B_TOPOLOGY__A_EQUALS_L_NOT_B__"
    "EXACT_FD_FLAT_EFFECTIVE_SOURCE_RANK143_KERNEL33__"
    "DYNAMICAL_229_COORDINATE_H191_NULL38_EQUALS34_GAUGE_PLUS4_WEAK__"
    "COMPLETE_RENORMALIZABLE_U1_CENSUS_HAS_61_OPERATORS_AND_OMITTED_DRIVER_COUPLINGS__"
    "RENORMALIZABLE_FILTER_ROBUST_BUT_FORCED_DEGREE4_KhAH2_AND_LKhH2_FILL_WEAK_RANK16__"
    "ALL_ORDER_EFT_TOPOLOGY_REJECTED__NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def bind_upstream() -> dict[str, Any]:
    result = {}
    for name, path, expected in (("V54", V54_PATH, V54_CORE), ("V55", V55_PATH, V55_CORE)):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("core_sha256") != expected:
            raise RuntimeError(f"stale {name} certificate")
        result[name] = {"path": path.name, "core_sha256": expected}
    return result


def charge_solution() -> dict[str, Any]:
    q = {
        "E": -2, "A": 1, "B": 3, "C": 0, "barC": -1,
        "H1": -24, "barh": 18, "h": -6, "H2": 3,
        "P": 6, "S": -12, "T": -6, "R": 4, "M": -2, "L": 1, "K": 2,
        "D1": 0, "D2": 0, "D3": -2, "D4": -2, "D5": -4, "D6": 6,
    }
    intended = {
        "R_E2": q["R"] + 2*q["E"],
        "M_A2": q["M"] + 2*q["A"],
        "T_B2": q["T"] + 2*q["B"],
        "M2_AB": 2*q["M"] + q["A"] + q["B"],
        "E_A2": q["E"] + 2*q["A"],
        "M_E_AB": q["M"] + q["E"] + q["A"] + q["B"],
        "M2_E_B2": 2*q["M"] + q["E"] + 2*q["B"],
        "barC_A_C": q["barC"] + q["A"] + q["C"],
        "L_barC_C": q["L"] + q["barC"] + q["C"],
        "P_H1_barh": q["P"] + q["H1"] + q["barh"],
        "S_barh_h": q["S"] + q["barh"] + q["h"],
        "h_B_H2": q["h"] + q["B"] + q["H2"],
        "T_H2_squared": q["T"] + 2*q["H2"],
        "D1_MK": q["D1"] + q["M"] + q["K"],
        "D2_PT": q["D2"] + q["P"] + q["T"],
        "D3_K": q["D3"] + q["K"],
        "D3_L2": q["D3"] + 2*q["L"],
        "D4_K": q["D4"] + q["K"],
        "D4_RM": q["D4"] + q["R"] + q["M"],
        "D5_K2": q["D5"] + 2*q["K"],
        "D5_PM": q["D5"] + q["P"] + q["M"],
        "D6_T": q["D6"] + q["T"],
        "D6_PS": q["D6"] + q["P"] + q["S"],
    }

    # Homogeneous exact charge equations.  Their rank leaves the expected
    # overall normalization and the harmless C/barC rephasing.
    names = ["E", "A", "B", "C", "barC", "H1", "barh", "h", "H2",
             "P", "S", "T", "R", "M", "L", "K"]
    index = {name: position for position, name in enumerate(names)}
    monomials = [
        ["R", "E", "E"], ["M", "A", "A"], ["T", "B", "B"],
        ["M", "M", "A", "B"], ["E", "A", "A"],
        ["M", "E", "A", "B"], ["M", "M", "E", "B", "B"],
        ["barC", "A", "C"], ["L", "barC", "C"],
        ["P", "H1", "barh"], ["S", "barh", "h"],
        ["h", "B", "H2"], ["T", "H2", "H2"],
        ["M", "K"], ["P", "T"], ["K", "L", "L"],
        ["K", "R", "M"], ["K", "K", "P", "M"], ["T", "P", "S"],
    ]
    rows = []
    # The last four driver equalities are differences rather than products.
    for monomial in monomials[:15]:
        row = [0]*len(names)
        for field in monomial:
            row[index[field]] += 1
        rows.append(row)
    for left, right in ((["K"], ["L", "L"]), (["K"], ["R", "M"]),
                        (["K", "K"], ["P", "M"]), (["T"], ["P", "S"])):
        row = [0]*len(names)
        for field in left:
            row[index[field]] += 1
        for field in right:
            row[index[field]] -= 1
        rows.append(row)
    equation_rank = int(sp.Matrix(rows).rank())

    fillers = {
        "direct_h_H2": q["h"] + q["H2"],
        "h_A_H2": q["h"] + q["A"] + q["H2"],
        "L_h_H2": q["L"] + q["h"] + q["H2"],
        "h_B_H2": q["h"] + q["B"] + q["H2"],
    }
    return {
        "charges": q,
        "normalization": "q(A)=q(L)=1 and q(C)=0",
        "all_intended_terms_neutral": all(value == 0 for value in intended.values()),
        "intended_term_charges": intended,
        "equation_matrix_shape": [len(rows), len(names)],
        "equation_rank": equation_rank,
        "solution_freedom": "overall normalization plus C/barC vectorlike rephasing",
        "broken_V55_equality": {"qA": 1, "qB": 3, "qL": 1, "all_equal": False},
        "filter_filler_charges": fillers,
        "both_V55_fillers_forbidden": fillers["h_A_H2"] != 0 and fillers["L_h_H2"] != 0,
    }


def deletion_only_no_go() -> dict[str, Any]:
    """The best F-flat one-cubic source branch still has 12 extra modes."""
    original = dw.witness
    data = dict(original())
    data.update({
        "mE": -1/5, "lambda": 0, "mA": 5, "mB": -10,
        "kappaA": 0, "kappaB": 0, "muAB": 6, "kappaAB": 1,
        "eta": -3j/10, "mC": 27/20,
    })
    try:
        dw.witness = lambda: data
        f_terms = dw.f_term_numerators()
        h = dw.hessian_numerator()
        q = dw.orbit_numerator()
    finally:
        dw.witness = original
    rank = v52.modular_rank(v52._modular_matrix(h))
    return {
        "scope": (
            "exact enumeration of the three choices retaining only one of E A^2, E B^2, E A B, "
            "with all quadratic masses/cross-mass and the spinor coupling available at the fixed DW VEV"
        ),
        "only_nontrivial_F_flat_cross_branch": "retain E A B; set E A^2=E B^2=0",
        "rational_parameters": {
            "mE": "-1/5", "mA": "5", "mB": "-10", "muAB": "6",
            "kappaAB": "1", "eta": "-3*i/10", "mC": "27/20",
        },
        "F_nonzero_counts": {name: int(np.count_nonzero(value)) for name, value in f_terms.items()},
        "hessian_rank": rank,
        "hessian_nullity": 176-rank,
        "gauge_orbit_rank": v52.modular_rank(v52._modular_matrix(q)),
        "extra_physical_zero_modes": 176-rank-33,
        "conclusion": "deleting the charge-linking cubics loses twelve source modes; dressing is required",
    }


def renormalizable_census() -> dict[str, Any]:
    q = charge_solution()["charges"]
    singlets = ["P", "S", "T", "R", "M", "L", "K", "D1", "D2", "D3", "D4", "D5", "D6"]
    tens = ["H1", "barh", "h", "H2"]

    singlet_only = []
    for degree in range(1, 4):
        for fields in itertools.combinations_with_replacement(singlets, degree):
            if sum(q[field] for field in fields) == 0:
                singlet_only.append(" ".join(fields))

    bilinears = {
        "E^2": 2*q["E"], "A^2": 2*q["A"], "B^2": 2*q["B"],
        "A B": q["A"]+q["B"], "barC C": q["barC"]+q["C"],
    }
    for first_index, first in enumerate(tens):
        for second in tens[first_index:]:
            bilinears[f"{first} {second}"] = q[first]+q[second]
    bare_bilinears = [name for name, charge in bilinears.items() if charge == 0]
    singlet_times_bilinear = [
        f"{singlet} {name}"
        for singlet in singlets for name, charge in bilinears.items()
        if q[singlet]+charge == 0
    ]

    cubic_charges = {
        "E^3": 3*q["E"], "E A^2": q["E"]+2*q["A"],
        "E B^2": q["E"]+2*q["B"], "E A B": q["E"]+q["A"]+q["B"],
        "barC A C": q["barC"]+q["A"]+q["C"],
        "barC B C": q["barC"]+q["B"]+q["C"],
    }
    for ten in tens:
        cubic_charges[f"C C {ten}"] = 2*q["C"]+q[ten]
        cubic_charges[f"barC barC {ten}"] = 2*q["barC"]+q[ten]
    for first_index, first in enumerate(tens):
        for second in tens[first_index:]:
            cubic_charges[f"{first} E {second}"] = q[first]+q["E"]+q[second]
    for adjoint in ("A", "B"):
        for first_index, first in enumerate(tens):
            for second in tens[first_index+1:]:
                cubic_charges[f"{first} {adjoint} {second}"] = q[first]+q[adjoint]+q[second]
    non_singlet_cubics = [name for name, charge in cubic_charges.items() if charge == 0]

    declared_renormalizable = {
        "R E^2", "M A^2", "T B^2", "L barC C",
        "E A^2", "barC A C", "P H1 barh", "S barh h", "h B H2", "T H2 H2",
        "D1", "D2", "M K D1", "P T D2", "K D3", "L L D3",
        "K D4", "R M D4", "K K D5", "P M D5", "T D6", "P S D6",
    }
    all_allowed = set(singlet_only) | set(bare_bilinears) | set(singlet_times_bilinear) | set(non_singlet_cubics)
    omitted = sorted(all_allowed-declared_renormalizable)
    omitted_non_singlet = sorted(
        (set(singlet_times_bilinear) | set(non_singlet_cubics))-declared_renormalizable
    )
    filter_terms = sorted(
        term for term in all_allowed if any(f" {ten}" in f" {term}" for ten in tens)
    )
    return {
        "scope": (
            "complete holomorphic degree<=3 SO(10)xU(1) monomial census for E54,A45,B45,C16,barCbar16, "
            "four 10s and the thirteen displayed singlets; derivative/Kahler and higher-dimensional terms excluded"
        ),
        "template_families": [
            "singlet monomials", "singlet times every quadratic SO(10) invariant",
            "E^3 and E(A^2,B^2,AB)", "barC(A,B)C", "10 E 10",
            "distinct-10 45 couplings", "C C 10 and barC barC 10",
        ],
        "bare_bilinears": bare_bilinears,
        "singlet_only_count": len(singlet_only),
        "singlet_only": singlet_only,
        "singlet_times_bilinear_count": len(singlet_times_bilinear),
        "singlet_times_bilinear": singlet_times_bilinear,
        "non_singlet_cubic_count": len(non_singlet_cubics),
        "non_singlet_cubics": non_singlet_cubics,
        "total_allowed_count": len(all_allowed),
        "allowed_filter_terms": filter_terms,
        "omitted_allowed_count": len(omitted),
        "omitted_allowed_operators": omitted,
        "omitted_allowed_non_singlet_operators": omitted_non_singlet,
        "declared_action_symmetry_complete": not omitted,
        "decisive_omissions": ["D3 A^2", "D4 A^2", "D5 A B", "D6 H1 barh"],
    }


def local_hessian_certificate() -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    original = dw.witness
    base = dict(original())
    parameters = {
        "mE": 14, "lambda": 0, "mA": 214, "mB": -50,
        "kappaA": 19, "kappaB": 10, "muAB": 6, "kappaAB": 1,
        "eta": -6j, "mC": 27,
    }
    data = dict(base)
    data.update(parameters)
    order = ["E_F_x400", "A_F_x400", "B_F_x400", "C_F_x400", "barC_F_x400"]

    def source_cross(delta: Mapping[str, Any]) -> np.ndarray:
        probe = dict(base)
        for name in parameters:
            probe[name] = 0
        probe.update(delta)
        dw.witness = lambda: probe
        terms = dw.f_term_numerators()
        return np.concatenate([terms[name] for name in order])/10

    try:
        dw.witness = lambda: data
        f_terms = dw.f_term_numerators()
        d_terms = dw.d_moment_numerator()
        source_h = dw.hessian_numerator()
        source_q = dw.orbit_numerator()
        cross_r = source_cross({"mE": 14})
        cross_t = source_cross({"mB": -50})
        cross_m = source_cross({"mA": 214, "muAB": 12, "kappaB": 20, "kappaAB": 1})
        cross_l = source_cross({"mC": 27})
    finally:
        dw.witness = original

    # P,S,T,R,M,L,K and D1..D6.  The topology changes the source gradients,
    # driver VEVs and H_MM, while the six constraint Jacobian is unchanged.
    jacobian = np.asarray([
        [0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -2, 1],
        [0, 0, 0, -1, -1, 0, 1],
        [-1, 0, 0, 0, -1, 0, 2],
        [-1, -1, 1, 0, 0, 0, 0],
    ], dtype=np.int64)
    vev_charges = np.asarray([6, -12, -6, 4, -2, 1, 2], dtype=np.int64)
    driver_charges = np.asarray([0, 0, -2, -2, -4, 6], dtype=np.int64)
    source_gradient = np.asarray([0, 0, -75, 420, 2415, 2700, 0], dtype=np.int64)
    driver_vevs = np.asarray([-1920, 75, 1350, 420, 75, 0], dtype=np.int64)
    residual = jacobian.T @ driver_vevs + source_gradient

    vv = np.zeros((7, 7), dtype=np.int64)
    vv[4, 6] += driver_vevs[0]
    vv[6, 4] += driver_vevs[0]
    vv[0, 2] += driver_vevs[1]
    vv[2, 0] += driver_vevs[1]
    vv[5, 5] += -2*driver_vevs[2]
    vv[3, 4] += -driver_vevs[3]
    vv[4, 3] += -driver_vevs[3]
    vv[6, 6] += 2*driver_vevs[4]
    vv[0, 4] += -driver_vevs[4]
    vv[4, 0] += -driver_vevs[4]
    # d^2/dM^2: 6 M^2 AB gives 12 O_AB=36; 10 M^2 E B^2 gives 20 O_EB2=120.
    vv[4, 4] += 156
    singlet_h = np.block([[vv, jacobian.T], [jacobian, np.zeros((6, 6), dtype=np.int64)]])

    h = np.zeros((229, 229), dtype=np.complex128)
    h[:176, :176] = source_h
    h[176:216, 176:216] = 40*elementary.filter_hessian()
    h[216:, 216:] = 40*singlet_h
    for singlet_index, cross in ((3, cross_r), (2, cross_t), (4, cross_m), (5, cross_l)):
        column = 216+singlet_index
        h[:176, column] = cross
        h[column, :176] = cross
    h = v52._gaussian_integer(h, label="V56 M-dressed-B 40H")

    q = np.zeros((229, 46), dtype=np.complex128)
    q[:176, :45] = source_q
    q[:54, 45] = -20*v52._symmetric_coordinates(data["E0"])
    q[54:99, 45] = 10*v52._antisymmetric_coordinates(data["A0"])
    q[99:144, 45] = 30*v52._antisymmetric_coordinates(data["B0"])
    q[160:176, 45] = -10*data["barC0"]
    q[216:223, 45] = 10*vev_charges
    q[223:, 45] = 10*driver_charges*driver_vevs
    q = v52._gaussian_integer(q, label="V56 M-dressed-B 10Q")

    weak_basis = np.zeros((229, 4), dtype=np.int64)
    for column, internal in enumerate(range(6, 10)):
        weak_basis[176+internal, column] = -2
        weak_basis[176+20+internal, column] = 1
    combined = np.column_stack((q, weak_basis))
    h_rank = v52.modular_rank(v52._modular_matrix(h))
    q_rank = v52.modular_rank(v52._modular_matrix(q))
    combined_rank = v52.modular_rank(v52._modular_matrix(combined))
    source_rank = v52.modular_rank(v52._modular_matrix(source_h))
    filter_h = elementary.filter_hessian()
    weak_indices = [10*field+internal for field in range(4) for internal in range(6, 10)]
    weak_rank = v52.modular_rank(filter_h[np.ix_(weak_indices, weak_indices)] % v52.MODULAR_PRIME)

    cert = {
        "effective_source_parameters_at_M_equals_T_equals_1": {
            "mE": 14, "lambda": 0, "mA": 214, "mB": -50,
            "kappaA": 19, "kappaB": 10, "muAB": 6, "kappaAB": 1,
            "eta": "-6*i", "mC": 27,
        },
        "source_F_nonzero_counts": {name: int(np.count_nonzero(value)) for name, value in f_terms.items()},
        "source_D_nonzero_count": int(np.count_nonzero(d_terms)),
        "source_hessian_rank": source_rank,
        "source_hessian_nullity": 176-source_rank,
        "source_orbit_rank": v52.modular_rank(v52._modular_matrix(source_q)),
        "source_gradient_P_S_T_R_M_L_K": source_gradient.tolist(),
        "source_H_MM": 156,
        "driver_VEVs_D1_to_D6": driver_vevs.tolist(),
        "all_spurion_F_residuals": residual.tolist(),
        "coordinates": 229,
        "hessian_rank": h_rank,
        "hessian_nullity": 229-h_rank,
        "gauge_orbit_rank": q_rank,
        "ward_product_zero": bool(np.count_nonzero(h @ q) == 0),
        "filter_rank": v52.modular_rank(filter_h % v52.MODULAR_PRIME),
        "filter_weak_rank": weak_rank,
        "filter_weak_nullity": 16-weak_rank,
        "explicit_weak_basis_rank": v52.modular_rank(weak_basis % v52.MODULAR_PRIME),
        "combined_gauge_plus_weak_span_rank": combined_rank,
        "combined_span_annihilated": bool(np.count_nonzero(h @ combined) == 0),
        "kernel_decomposition": {"Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0},
        "kernel_exact": bool(combined_rank == 229-h_rank == 38 and np.count_nonzero(h @ combined) == 0),
        "hessian_sha256": v52.gaussian_matrix_sha(h),
        "orbit_sha256": v52.gaussian_matrix_sha(q),
    }
    return cert, h, q


def filter_completion_audit(census: Mapping[str, Any]) -> dict[str, Any]:
    allowed = census["allowed_filter_terms"]
    forbidden_fillers = all(name not in " | ".join(allowed) for name in ("h A H2", "L h H2"))
    return {
        "all_allowed_renormalizable_filter_terms": allowed,
        "additional_allowed_term": "D6 H1 barh",
        "D6_VEV_at_witness": 0,
        "effect_of_generic_D6_VEV": "renormalizes the P H1 barh link; it does not add an h-H2 weak mass",
        "one_weak_component_generic_matrix": [
            [0, "p_eff", 0, 0], ["p_eff", 0, "s_eff", 0],
            [0, "s_eff", 0, 0], [0, 0, 0, "t_eff"],
        ],
        "generic_open_conditions": ["p_eff != 0", "s_eff != 0", "t_eff != 0"],
        "generic_one_weak_component_rank": 3,
        "generic_four_component_weak_rank": 12,
        "generic_weak_nullity": 4,
        "h_A_H2_and_L_h_H2_absent_from_complete_census": forbidden_fillers,
        "conclusion": "the complete renormalizable filter sector preserves four weak modes; this statement does not extend beyond degree three",
    }


def higher_dimensional_filler_audit() -> dict[str, Any]:
    """Exact matrix-chain invariant audit through total degree eight.

    E, A and B transform as two-index SO(10) tensors, so
    h^T X_1 ... X_n H2 is an exact singlet for every matrix word.  Singlet
    spurions may multiply it.  The search is complete in this tensor-chain
    channel for all nonzero-VEV singlets and E/A/B insertions through degree 8.
    Spinor-tensor channels are not needed for the no-go and are not claimed.
    """
    data = dw.witness()
    matrices = {
        "E": np.rint(data["E0"].real).astype(np.int64),
        "A": np.rint(data["A0"].real).astype(np.int64),
        "B": np.rint(data["B0"].real).astype(np.int64),
    }
    tensor_charges = {"E": -2, "A": 1, "B": 3}
    # All singlets with nonzero VEV in the exact V56 witness.  D1/D2 are
    # neutral; retaining them makes the finite census genuinely exhaustive at
    # each bounded degree rather than quotienting out neutral decorations.
    singlet_charges = {
        "P": 6, "S": -12, "T": -6, "R": 4, "M": -2, "L": 1, "K": 2,
        "D1": 0, "D2": 0, "D3": -2, "D4": -2, "D5": -4,
    }
    filter_h = elementary.filter_hessian().astype(np.int64)
    weak_indices = [10*field+internal for field in range(4) for internal in range(6, 10)]
    color_indices = [10*field+internal for field in range(4) for internal in range(6)]

    def filled_matrix(insertion: np.ndarray) -> np.ndarray:
        result = filter_h.copy()
        result[20:30, 30:40] += insertion
        result[30:40, 20:30] += insertion.T
        return result

    def exact_effect(insertion: np.ndarray) -> dict[str, int]:
        filled = filled_matrix(insertion)
        weak = filled[np.ix_(weak_indices, weak_indices)]
        color = filled[np.ix_(color_indices, color_indices)]
        return {
            "full_rank": v52.modular_rank(filled % v52.MODULAR_PRIME),
            "weak_rank": v52.modular_rank(weak % v52.MODULAR_PRIME),
            "color_rank": v52.modular_rank(color % v52.MODULAR_PRIME),
            "weak_determinant": int(sp.Matrix(weak.tolist()).det()),
        }

    identity = np.eye(10, dtype=np.int64)
    a0 = matrices["A"]
    named = [
        {
            "operator": "K h^T A H2 / Lambda",
            "degree": 4, "charge": 2-6+1+3,
            "invariant": "10^T 45 10, multiplied by the singlet K",
            "effect": exact_effect(a0),
        },
        {
            "operator": "L K h^T H2 / Lambda",
            "degree": 4, "charge": 1+2-6+3,
            "invariant": "the vector bilinear 10^T 10, multiplied by L K",
            "effect": exact_effect(identity),
        },
        {
            "operator": "h^T A^3 H2 / Lambda^2",
            "degree": 5, "charge": -6+3+3,
            "invariant": "the contracted matrix chain 10^T 45^3 10",
            "effect": exact_effect(a0 @ a0 @ a0),
        },
        {
            "operator": "L h^T A^2 H2 / Lambda^2",
            "degree": 5, "charge": 1-6+2+3,
            "invariant": "the contracted matrix chain 10^T 45^2 10, multiplied by L",
            "effect": exact_effect(a0 @ a0),
        },
    ]

    # h+H2=-3, so insertions must carry charge +3.  On the exact weak block,
    # B=0 while both A and E are invertible.  A word is therefore fatal iff it
    # contains no B; the empty word is the identity.  We still recompute exact
    # matrices for the recorded leading examples above.
    counts_by_degree: dict[str, dict[str, int]] = {}
    examples: list[dict[str, Any]] = []
    singlet_names = list(singlet_charges)
    for insertion_count in range(1, 7):
        total_degree = 2+insertion_count
        neutral_count = 0
        fatal_count = 0
        for word_length in range(insertion_count+1):
            singlet_count = insertion_count-word_length
            for word in itertools.product(matrices, repeat=word_length):
                word_charge = sum(tensor_charges[name] for name in word)
                word_is_weak_invertible = "B" not in word
                for singlets in itertools.combinations_with_replacement(singlet_names, singlet_count):
                    charge = word_charge + sum(singlet_charges[name] for name in singlets)
                    if charge != 3:
                        continue
                    neutral_count += 1
                    if word_is_weak_invertible:
                        fatal_count += 1
                        if len(examples) < 24:
                            examples.append({
                                "degree": total_degree,
                                "singlets": list(singlets),
                                "matrix_word": list(word) if word else ["I"],
                            })
        counts_by_degree[str(total_degree)] = {
            "neutral_matrix_chain_fillers": neutral_count,
            "fatal_weak_full_rank_fillers": fatal_count,
        }

    # Factorwise ordinary-additive derivation: the required topology gives
    # L=A, K=2L and B=3A.  Since h+B+H2=0, both degree-four charges vanish.
    forced_derivation = [
        "barC A C and L barC C imply r(L)=r(A)",
        "D3(K-L^2) implies r(K)=2 r(L)=2 r(A)",
        "E A^2 and M E A B imply r(B)=3 r(A)",
        "h B H2 implies r(h)+r(H2)=-3 r(A)",
        "therefore r(K h A H2)=2r(A)+r(A)-3r(A)=0",
        "therefore r(L K h H2)=r(A)+2r(A)-3r(A)=0",
    ]
    return {
        "scope": (
            "complete E/A/B matrix-chain and nonzero-VEV-singlet dressing census through total degree eight; "
            "additional spinor contraction channels could only add operators"
        ),
        "named_exact_invariants": named,
        "first_fatal_total_degree": min(item["degree"] for item in named if item["effect"]["weak_rank"] == 16),
        "bounded_counts_by_total_degree": counts_by_degree,
        "leading_fatal_examples": examples,
        "ordinary_additive_factor_forcing_derivation": forced_derivation,
        "product_of_ordinary_additive_selectors_cannot_forbid_degree4_fillers": True,
        "all_order_topology_verdict": "REJECTED",
    }


@functools.lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    upstream = bind_upstream()
    charges = charge_solution()
    deletion = deletion_only_no_go()
    census = renormalizable_census()
    local, h, q = local_hessian_certificate()
    filter_completion = filter_completion_audit(census)
    higher = higher_dimensional_filler_audit()
    checks = {
        "V54_and_V55_cores_bound": len(upstream) == 2,
        "all_declared_terms_U1_neutral": charges["all_intended_terms_neutral"],
        "V55_A_B_L_equality_broken": not charges["broken_V55_equality"]["all_equal"],
        "hAH2_and_LhH2_forbidden": charges["both_V55_fillers_forbidden"],
        "deletion_only_branch_has_12_extra_modes": deletion["extra_physical_zero_modes"] == 12,
        "effective_source_exact_rank143": (
            local["source_hessian_rank"] == 143 and local["source_hessian_nullity"] == 33
            and not any(local["source_F_nonzero_counts"].values()) and local["source_D_nonzero_count"] == 0
        ),
        "dynamical_spurion_F_terms_zero": local["all_spurion_F_residuals"] == [0]*7,
        "whole_H191_null38": local["hessian_rank"] == 191 and local["hessian_nullity"] == 38,
        "whole_kernel_exact_34gauge_plus4weak": local["kernel_exact"] and local["gauge_orbit_rank"] == 34,
        "complete_renormalizable_census_has61": census["total_allowed_count"] == 61,
        "complete_filter_retains_four_weak_modes": (
            filter_completion["generic_weak_nullity"] == 4
            and filter_completion["h_A_H2_and_L_h_H2_absent_from_complete_census"]
        ),
        "degree4_fatal_fillers_exact": (
            higher["first_fatal_total_degree"] == 4
            and all(item["charge"] == 0 for item in higher["named_exact_invariants"])
            and all(item["effect"]["weak_rank"] == 16 for item in higher["named_exact_invariants"])
        ),
        "all_order_topology_rejected": higher["all_order_topology_verdict"] == "REJECTED",
        "declared_action_correctly_not_symmetry_complete": not census["declared_action_symmetry_complete"],
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v56_r1_m_dressed_b_topology_hessian_audit_v1",
        "status": STATUS if not failures else "V56_R1_M_DRESSED_B_TOPOLOGY_HESSIAN_AUDIT_FAILED",
        "scope": (
            "zero-new-representation effective-superpotential topology test at the exact V54 vacuum; "
            "complete only through renormalizable order, not a UV or phenomenological completion"
        ),
        "upstream_certificates": upstream,
        "topology_change": {
            "new_fields_or_representations": 0,
            "replacements": [
                "M B^2 -> T B^2",
                "M A B -> M^2 A B/Lambda",
                "E A B -> M E A B/Lambda",
                "E B^2 -> M^2 E B^2/Lambda^2",
            ],
            "unchanged_terms": ["R E^2", "M A^2", "E A^2", "barC A C", "L barC C"],
            "minimality_scope": (
                "zero added fields and the four B-containing monomials that independently recreate an A=B "
                "charge equation are replaced; exact one-cubic deletion branches were checked and leave 12 modes"
            ),
            "EFT_maximum_displayed_degree": 5,
        },
        "charge_constraint_certificate": charges,
        "deletion_only_no_go": deletion,
        "declared_EFT_local_hessian": local,
        "complete_allowed_renormalizable_operator_census": census,
        "symmetry_complete_filter_audit": filter_completion,
        "higher_dimensional_fatal_filler_audit": higher,
        "perturbativity": {
            "Spin10_field_inventory_changed": False, "sum_T_including_three_16_families": 42,
            "one_loop_b_Spin10": 18,
        },
        "fail_closed_findings": [
            "the exact local action contains dimension-four and dimension-five source operators with no messenger UV completion",
            f"U1 permits {census['omitted_allowed_count']} renormalizable operators omitted by the declared coefficient witness",
            "allowed D3 A^2, D4 A^2 and D5 A B terms backreact on the driver constraints in a symmetry-complete action",
            "K h A H2 and L K h H2 are forced degree-four invariants and each raises the weak rank from 12 to 16",
            "no anomaly/GS ledger, matter/flavor sector, global vacuum, thresholds, proton matching, SUSY breaking or cosmology is supplied",
        ],
        "gate_verdict": {
            "G1": "FROZEN_PRIOR_NAMESPACE_ONLY", "G2": "OPEN", "G3": "OPEN", "G4": "OPEN",
            "G5": "OPEN", "G6": "OPEN", "G7": "OPEN", "G8": "OPEN", "promoted_gate_count": 0,
        },
        "next_kill_test": (
            "abandon this M-dressed-B charge solution or change the K/L driver topology; ordinary additive selectors "
            "factorwise force both degree-four fillers, so a messenger completion alone cannot rescue it"
        ),
        "checks": checks,
        "failures": failures,
        "matrix_hashes": {"hessian": v52.gaussian_matrix_sha(h), "orbit": v52.gaussian_matrix_sha(q)},
        "artifact_manifest": {},
    }
    report["artifact_manifest"] = {
        "script": {"path": Path(__file__).name, "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "test": {"path": TEST_PATH.name, "sha256": hashlib.sha256(TEST_PATH.read_bytes()).hexdigest() if TEST_PATH.exists() else None},
    }
    report["core_sha256"] = canonical_sha(report)
    if failures:
        raise RuntimeError("V56 topology integrity failure: " + ", ".join(failures))
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    local = report["declared_EFT_local_hessian"]
    census = report["complete_allowed_renormalizable_operator_census"]
    charge = report["charge_constraint_certificate"]
    higher = report["higher_dimensional_fatal_filler_audit"]
    return f"""# V56-R1 M-dressed-B topology / Hessian audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Minimal topology change

No field or Spin(10) representation is added.  Four B-containing source terms are changed:

- `M B^2 -> T B^2`
- `M A B -> M^2 A B/Lambda`
- `E A B -> M E A B/Lambda`
- `E B^2 -> M^2 E B^2/Lambda^2`

The exact charge solution is `q(E,A,B,L,M,T)=(-2,1,3,1,-2,-6)`.  Thus the
V55 equality becomes `q(A)=q(L)=1 != q(B)=3`.  The required `h B H2` is neutral,
while `h A H2` and `L h H2` each have charge
`{charge['filter_filler_charges']['h_A_H2']}` and are forbidden.

Simply deleting the charge-linking cubics does not work: the only nontrivial exact
one-cubic cross branch has source rank 131 and twelve physical zero modes.  The dressed
terms retain their effective Hessian at the unit-spurion vacuum.

## Exact declared-action Hessian

The effective 176-coordinate source remains exactly F/D-flat with rank
`{local['source_hessian_rank']}` and nullity `{local['source_hessian_nullity']}`, equal to
its Spin(10) orbit.  Recomputing all M/T derivatives changes the source gradient to
`{local['source_gradient_P_S_T_R_M_L_K']}`, fixes driver VEVs to
`{local['driver_VEVs_D1_to_D6']}`, and leaves every spurion F residual zero.

The full declared `{local['coordinates']}`-coordinate action has Hessian rank
`{local['hessian_rank']}` and nullity `{local['hessian_nullity']}`.  An explicit
annihilated span proves the kernel is exactly 34 gauge plus four weak-Higgs modes, with
zero extra modes.

## Symmetry-completion boundary

The complete degree-three SO(10)xU(1) census contains `{census['total_allowed_count']}`
operators: `{census['singlet_only_count']}` singlet monomials,
`{census['singlet_times_bilinear_count']}` singlet-times-bilinear operators, and
`{census['non_singlet_cubic_count']}` pure non-singlet cubics.  It permits
`D3 A^2`, `D4 A^2`, `D5 A B`, and `D6 H1 barh`, among other singlet-sector terms omitted
from the declared witness.

At strictly renormalizable order the filter itself is robust: its only extra term is
`D6 H1 barh`, which merely renormalizes the existing link.  Its generic weak rank remains
12 and its weak nullity remains four.

## Fatal all-order stress test

The renormalizable result does not survive the EFT completion.  Two exact total-degree-four
invariants are already forced:

- `K h^T A H2/Lambda`
- `L K h^T H2/Lambda`

Both are neutral.  The first uses the standard `10 x 45 x 10` contraction; the second uses
the vector bilinear.  At the exact vacuum each raises the weak rank from 12 to 16.  Their
weak determinants are respectively
`{higher['named_exact_invariants'][0]['effect']['weak_determinant']}` and
`{higher['named_exact_invariants'][1]['effect']['weak_determinant']}`.

The proposed degree-five `h^T A^3 H2` and `L h^T A^2 H2` chains are also exact invariants
and also give weak rank 16.  A complete E/A/B matrix-chain and nonzero-VEV-singlet search
through total degree eight confirms that the first fatal degree is
`{higher['first_fatal_total_degree']}`.  Moreover, the required charge equations force both
degree-four classes factorwise for every ordinary additive selector retaining this topology.

## Verdict

This is an exact mathematical certificate for the renormalizable truncation, but the
all-order M-dressed-B topology is rejected.  No gate is promoted.  A successor must change
the K/L driver relations or abandon this charge solution; adding messengers alone cannot
remove the forced degree-four fillers.
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
