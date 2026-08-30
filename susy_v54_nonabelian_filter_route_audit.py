#!/usr/bin/env python3
"""V54 non-Abelian SU(2)_F filter and charged-source-spurion audit.

The audit appends a gauged SU(2)_F filter to the exact V53 DW source.  A
charged singlet S distinguishes the full-VEV adjoint A from the missing-VEV
adjoint B.  This produces an exact F/D-flat, isolated source extension and an
exact same-action Hessian with one weak Higgs pair in the *declared* action.

The symmetry completion nevertheless fails: the same charge equations that
allow S A B and epsilon H B H necessarily allow the dimension-four operator
S epsilon H A H / Lambda.  Since A has nonzero weak entries, that operator
fills the intended weak kernel.  This is a scoped, executable redesign/no-go,
not a completed theory and not a gate promotion.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import susy_v52_low_index_source_audit as v52
import susy_v53_natural_dt_filter_audit as v53


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_NONABELIAN_FILTER_ROUTE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_NONABELIAN_FILTER_ROUTE_AUDIT.md"

STATUS = (
    "V54_SU2F_NONABELIAN_FILTER__CHARGED_Z8_SOURCE_SPURION__"
    "EXACT255_DECLARED_ACTION_RANK215_NULL40_GAUGE36_PLUS_WEAK4__"
    "GENERIC_ALLOWED_S_H_A_H_FILLS_WEAK_KERNEL__NO_GATE_PROMOTION"
)

SOURCE_BASE_DIM = 176
SOURCE_EXT_DIM = 178
FILTER_DIM = 50
FLAVOR_DRIVER_DIM = 5
SPECTATOR_VECTOR_DIM = 20
SPECTATOR_SINGLET_DIM = 2
TOTAL_DIM = (
    SOURCE_EXT_DIM + FILTER_DIM + FLAVOR_DRIVER_DIM
    + SPECTATOR_VECTOR_DIM + SPECTATOR_SINGLET_DIM
)
HESSIAN_SCALE = 40


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=lambda item: item.item() if isinstance(item, np.generic) else str(item),
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def exact_rank(matrix: np.ndarray) -> int:
    return v52.modular_rank(v52._modular_matrix(matrix))


def source_spurion_cross_value() -> int:
    """dW/dS before the X_S contribution at the V53 witness."""
    w = v53.witness()
    e0, a0, b0 = w["E0"], w["A0"], w["B0"]
    value = (
        -0.5 * w["muAB"] * np.trace(a0 @ b0)
        -0.5 * w["kappaAB"] * np.trace(e0 @ (a0 @ b0 + b0 @ a0))
    )
    if abs(value.imag) > 1e-10 or abs(value.real - round(value.real)) > 1e-10:
        raise ArithmeticError("source-spurion cross value is not an exact integer")
    return int(round(value.real))


def source_spurion_hessian_numerator() -> np.ndarray:
    """40 H for (V53 source, S, X_S) at S=1, X_S=-15/2."""
    w = v53.witness()
    e0, a0, b0 = w["E0"], w["A0"], w["B0"]
    alpha, beta = w["muAB"], w["kappaAB"]
    mixed: list[complex] = []
    for variation in v52.symmetric_traceless_basis():
        mixed.append(-0.5 * beta * np.trace(variation @ (a0 @ b0 + b0 @ a0)))
    for variation in v52.antisymmetric_basis():
        mixed.append(
            -0.5 * alpha * np.trace(variation @ b0)
            -0.5 * beta * np.trace(e0 @ (variation @ b0 + b0 @ variation))
        )
    for variation in v52.antisymmetric_basis():
        mixed.append(
            -0.5 * alpha * np.trace(a0 @ variation)
            -0.5 * beta * np.trace(e0 @ (a0 @ variation + variation @ a0))
        )
    mixed.extend([0j] * 32)
    mixed_numerator = v52._gaussian_integer(
        HESSIAN_SCALE * np.asarray(mixed), label="40 H_source,S"
    )

    result = np.zeros((SOURCE_EXT_DIM, SOURCE_EXT_DIM), dtype=np.complex128)
    result[:SOURCE_BASE_DIM, :SOURCE_BASE_DIM] = v53.hessian_numerator()
    result[:SOURCE_BASE_DIM, SOURCE_BASE_DIM] = mixed_numerator
    result[SOURCE_BASE_DIM, :SOURCE_BASE_DIM] = mixed_numerator
    # W_X = X_S(S^2-1), S=1, X_S=-15/2.
    result[SOURCE_BASE_DIM, SOURCE_BASE_DIM] = -15 * HESSIAN_SCALE
    result[SOURCE_BASE_DIM, SOURCE_BASE_DIM + 1] = 2 * HESSIAN_SCALE
    result[SOURCE_BASE_DIM + 1, SOURCE_BASE_DIM] = 2 * HESSIAN_SCALE
    return result


def filter_hessian(*, include_fatal_s_h_a_h: bool = False) -> np.ndarray:
    """50-coordinate Hessian ordered H1,H2,U,V,W, each a Spin(10) 10."""
    w = v53.witness()
    b0 = w["B0"]
    if include_fatal_s_h_a_h:
        b0 = b0 + w["A0"]
    eye = np.eye(10, dtype=np.complex128)
    zero = np.zeros((10, 10), dtype=np.complex128)
    blocks = [[zero.copy() for _ in range(5)] for _ in range(5)]
    # epsilon_ab H_a^T B H_b.
    blocks[0][1] = b0
    blocks[1][0] = b0.T
    # P=(1,0) selects H2; Q=(0,1) selects -H1.
    blocks[1][2] = blocks[2][1] = eye
    blocks[0][4] = blocks[4][0] = -eye
    blocks[2][3] = blocks[3][2] = eye
    # S W^T W/2 at S=1.
    blocks[4][4] = eye
    result = np.vstack([np.hstack(row) for row in blocks])
    if not np.array_equal(result, result.T):
        raise ArithmeticError("filter Hessian is not symmetric")
    return result


def flavor_driver_hessian() -> np.ndarray:
    """Hessian for X_F(P1 Q2-P2 Q1-1) at P=e1,Q=e2,X_F=0."""
    result = np.zeros((5, 5), dtype=np.complex128)
    # ordering P1,P2,Q1,Q2,X_F
    result[0, 4] = result[4, 0] = 1
    result[3, 4] = result[4, 3] = 1
    return result


def flavor_orbit() -> np.ndarray:
    """Complexified sl(2) orbit in P,Q,X_F coordinates."""
    # columns E_+, E_-, H for P=e1,Q=e2.
    return np.asarray(
        [
            [0, 0, 1],  # P1
            [0, 1, 0],  # P2
            [1, 0, 0],  # Q1
            [0, 0, -1], # Q2
            [0, 0, 0],  # X_F
        ],
        dtype=np.complex128,
    )


def spectator_hessian() -> np.ndarray:
    """Mass blocks for one 10 pair (q=1,3) and one singlet pair (q=0,4)."""
    eye10 = np.eye(10, dtype=np.complex128)
    vector = np.block([[np.zeros((10, 10)), eye10], [eye10, np.zeros((10, 10))]])
    singlet = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
    return np.block(
        [
            [vector, np.zeros((20, 2))],
            [np.zeros((2, 20)), singlet],
        ]
    )


def combined_hessian(*, include_fatal_s_h_a_h: bool = False) -> np.ndarray:
    result = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.complex128)
    source = source_spurion_hessian_numerator()
    result[:SOURCE_EXT_DIM, :SOURCE_EXT_DIM] = source
    f0 = SOURCE_EXT_DIM
    f1 = f0 + FILTER_DIM
    d1 = f1 + FLAVOR_DRIVER_DIM
    result[f0:f1, f0:f1] = HESSIAN_SCALE * filter_hessian(
        include_fatal_s_h_a_h=include_fatal_s_h_a_h
    )
    result[f1:d1, f1:d1] = HESSIAN_SCALE * flavor_driver_hessian()
    result[d1:, d1:] = HESSIAN_SCALE * spectator_hessian()
    return result


def combined_orbit() -> np.ndarray:
    result = np.zeros((TOTAL_DIM, 48), dtype=np.complex128)
    result[:SOURCE_BASE_DIM, :45] = v53.orbit_numerator()
    driver_start = SOURCE_EXT_DIM + FILTER_DIM
    result[driver_start:driver_start + FLAVOR_DRIVER_DIM, 45:48] = 10 * flavor_orbit()
    return result


def charge_audit() -> dict[str, Any]:
    n = 8
    q = {
        "E54": 0, "A45": 0, "B45_DW": 4, "S_source": 4,
        "C16H": 0, "barC16H": 0, "H_10_SU2_doublet": 2,
        "U10": 6, "V10": 2, "W10": 6, "P_SU2_doublet": 0,
        "Q_SU2_doublet": 0, "X_source": 0, "X_flavor": 0,
        "F16": 3, "spectator10_x": 1, "spectator10_y": 3,
        "spectator1_x": 0, "spectator1_y": 4,
    }
    required = {
        "SAB": q["S_source"] + q["A45"] + q["B45_DW"],
        "SEAB": q["S_source"] + q["E54"] + q["A45"] + q["B45_DW"],
        "HBH": 2 * q["H_10_SU2_doublet"] + q["B45_DW"],
        "PHU": q["P_SU2_doublet"] + q["H_10_SU2_doublet"] + q["U10"],
        "QHW": q["Q_SU2_doublet"] + q["H_10_SU2_doublet"] + q["W10"],
        "UV": q["U10"] + q["V10"],
        "SWW": q["S_source"] + 2 * q["W10"],
        "PQ_driver": q["P_SU2_doublet"] + q["Q_SU2_doublet"],
        "FFV_Yukawa": 2 * q["F16"] + q["V10"],
        "S_spectator10_mass": q["S_source"] + q["spectator10_x"] + q["spectator10_y"],
        "S_spectator1_mass": q["S_source"] + q["spectator1_x"] + q["spectator1_y"],
    }
    forbidden = {
        "H_squared": 2 * q["H_10_SU2_doublet"],
        "H_A_H": 2 * q["H_10_SU2_doublet"] + q["A45"],
        "PH_QH": q["P_SU2_doublet"] + q["Q_SU2_doublet"] + 2 * q["H_10_SU2_doublet"],
        "F16_power4": 4 * q["F16"],
    }
    exposed = {
        "S_H_A_H": q["S_source"] + 2 * q["H_10_SU2_doublet"] + q["A45"],
        "S_PH_QH": q["S_source"] + q["P_SU2_doublet"] + q["Q_SU2_doublet"] + 2 * q["H_10_SU2_doublet"],
        "S_F16_power4": q["S_source"] + 4 * q["F16"],
    }
    return {
        "group": "Z8 x exact Z2_matter",
        "Z8_charges": q,
        "required_term_residues": {k: v % n for k, v in required.items()},
        "direct_forbidden_residues": {k: v % n for k, v in forbidden.items()},
        "first_exposed_residues": {k: v % n for k, v in exposed.items()},
        "universal_spurion_identity": (
            "q(SAB)=q(HBH)=q(B^2)=0 implies q(S H A H)=0: "
            "s+a+b=0, 2h+b=0, 2b=0 => s+2h+a=-2b=0"
        ),
    }


def anomaly_audit() -> dict[str, Any]:
    # Conservative residues mod 8; T(10)=1,T(16)=2,T(45)=8.
    base_gauge = (8 * 4 + 2 * 1 * 2 + (6 + 2 + 6) + 3 * 2 * 3) % 8
    base_gravity = (45 * 4 + 2 * 10 * 2 + 10 * (6 + 2 + 6) + 3 * 16 * 3 + 4) % 8
    base_cubic = (
        45 * 4**3 + 2 * 10 * 2**3 + 10 * (6**3 + 2**3 + 6**3)
        + 3 * 16 * 3**3 + 4**3
    ) % 8
    vector = {
        "Spin10_squared_Z8": (1 + 3) % 8,
        "gravity_squared_Z8": (10 * (1 + 3)) % 8,
        "Z8_cubed": (10 * (1**3 + 3**3)) % 8,
    }
    singlet = {
        "Spin10_squared_Z8": 0,
        "gravity_squared_Z8": (0 + 4) % 8,
        "Z8_cubed": (0**3 + 4**3) % 8,
    }
    base = {
        "Spin10_squared_Z8": base_gauge,
        "gravity_squared_Z8": base_gravity,
        "Z8_cubed": base_cubic,
    }
    total = {k: (base[k] + vector[k] + singlet[k]) % 8 for k in base}
    return {
        "convention": "conservative residues modulo 8",
        "base": base,
        "repair": {
            "one_vector10_pair_charges": [1, 3],
            "one_singlet_pair_charges": [0, 4],
            "all_masses_from_S_charge4": True,
            "vector_contribution": vector,
            "singlet_contribution": singlet,
        },
        "total_mod8": total,
    }


def running_audit() -> dict[str, Any]:
    g = 0.73
    b_eft = 21  # sumT=45, including the anomaly-repair 10 pair.
    b_uv = 37   # add two mediator 45s, sumT=61.
    return {
        "Spin10": {
            "EFT_sumT": 45,
            "EFT_b": b_eft,
            "EFT_pole_ratio": math.exp(8 * math.pi**2 / (b_eft * g**2)),
            "clean_renormalizable_UV_completion": "two 45 mediators generate S E A B / M",
            "UV_sumT": 61,
            "UV_b": b_uv,
            "UV_pole_ratio": math.exp(8 * math.pi**2 / (b_uv * g**2)),
        },
        "SU2_F": {
            "weighted_fundamental_doublets": 12,
            "Witten_parity": 0,
            "sumT": 6,
            "three_C2": 6,
            "one_loop_b": 0,
            "count_explanation": "10 doublets from H=(10,2), plus P and Q",
        },
    }


def build_report() -> dict[str, Any]:
    source_h = source_spurion_hessian_numerator()
    source_q = np.vstack(
        [v53.orbit_numerator(), np.zeros((2, 45), dtype=np.complex128)]
    )
    filt = filter_hessian()
    fatal_filt = filter_hessian(include_fatal_s_h_a_h=True)
    driver = flavor_driver_hessian()
    flavor_q = flavor_orbit()
    h = combined_hessian()
    h_fatal = combined_hessian(include_fatal_s_h_a_h=True)
    q = combined_orbit()

    weak_indices = [10 * field + component for field in range(5) for component in range(6, 10)]
    color_indices = [10 * field + component for field in range(5) for component in range(6)]
    filter_color = filt[np.ix_(color_indices, color_indices)]
    filter_weak = filt[np.ix_(weak_indices, weak_indices)]
    fatal_weak = fatal_filt[np.ix_(weak_indices, weak_indices)]

    source_rank = exact_rank(source_h)
    filter_rank = exact_rank(filt)
    driver_rank = exact_rank(driver)
    h_rank = exact_rank(h)
    h_fatal_rank = exact_rank(h_fatal)
    q_rank = exact_rank(q)

    report: dict[str, Any] = {
        "schema": "susy_v54_nonabelian_filter_route_audit_v1",
        "status": STATUS,
        "candidate": {
            "gauge_group": "Spin(10) x SU(2)_F",
            "flavor_representations": {
                "H": "(10,2)", "U_V_W": "three (10,1)",
                "P_Q": "two (1,2)", "X_F": "(1,1)",
            },
            "source_replacement": (
                "mu A B + k E A B -> alpha S A B + (beta/Lambda) S E A B, "
                "with Z8 charges A=0,B=S=4"
            ),
            "filter_superpotential": (
                "epsilon H B H + (P.H)U + (Q.H)W + U V + (S/2)W^2"
            ),
            "source_driver": "X_S(S^2-1)",
            "flavor_driver": "X_F(epsilon P Q-1)",
        },
        "source_vacuum": {
            "S": 1,
            "X_S": "-15/2",
            "cross_dW_dS_before_driver": source_spurion_cross_value(),
            "F_S": 0,
            "F_XS": 0,
            "upstream_F_nonzero_counts": {
                k: int(np.count_nonzero(v)) for k, v in v53.f_term_numerators().items()
            },
            "D_nonzero_count": int(np.count_nonzero(v53.d_moment_numerator())),
            "coordinates": SOURCE_EXT_DIM,
            "hessian_rank": source_rank,
            "hessian_nullity": SOURCE_EXT_DIM - source_rank,
            "Spin10_orbit_rank": exact_rank(source_q),
            "ward_product_zero": bool(np.count_nonzero(source_h @ source_q) == 0),
            "kernel_equals_Spin10_gauge_orbit": source_rank == 145 and exact_rank(source_q) == 33,
        },
        "SU2F_vacuum": {
            "P": [1, 0], "Q": [0, 1], "X_F": 0,
            "F_terms_zero": True,
            "D_terms_zero_for_equal_norms": True,
            "driver_rank": driver_rank,
            "driver_nullity": FLAVOR_DRIVER_DIM - driver_rank,
            "SU2F_orbit_rank": exact_rank(flavor_q),
            "driver_kernel_equals_complexified_SU2F_orbit": bool(
                driver_rank == 2 and exact_rank(flavor_q) == 3
                and np.count_nonzero(driver @ flavor_q) == 0
            ),
        },
        "filter_ranks": {
            "coordinates": FILTER_DIM,
            "full_rank": filter_rank,
            "full_nullity": FILTER_DIM - filter_rank,
            "color_rank": exact_rank(filter_color),
            "color_nullity": len(color_indices) - exact_rank(filter_color),
            "weak_rank": exact_rank(filter_weak),
            "weak_nullity": len(weak_indices) - exact_rank(filter_weak),
            "generic_fatal_S_H_A_H_filter_rank": exact_rank(fatal_filt),
            "generic_fatal_weak_rank": exact_rank(fatal_weak),
        },
        "same_action_hessian": {
            "declared_coordinates": TOTAL_DIM,
            "declared_rank": h_rank,
            "declared_nullity": TOTAL_DIM - h_rank,
            "rank_decomposition": {
                "source": source_rank, "filter": filter_rank,
                "SU2F_driver": driver_rank, "massive_spectators": 22,
            },
            "combined_gauge_orbit_rank": q_rank,
            "ward_product_zero": bool(np.count_nonzero(h @ q) == 0),
            "declared_kernel_decomposition": {
                "Spin10_gauge": 33, "SU2F_gauge": 3, "weak_Higgs": 4,
            },
            "symmetry_complete_with_fatal_operator_rank": h_fatal_rank,
            "symmetry_complete_with_fatal_operator_nullity": TOTAL_DIM - h_fatal_rank,
            "fatal_kernel_equals_gauge_only": h_fatal_rank == 219 and q_rank == 36,
        },
        "selector": charge_audit(),
        "discrete_anomalies": anomaly_audit(),
        "running": running_audit(),
        "UV_completion": {
            "EFT_operator": "S Tr[E(AB+BA)]/Lambda",
            "clean_tree_completion": (
                "M Tr(R45 T45)+lambda Tr[R45(EA+AE)]+kappa S Tr(T45 B)"
            ),
            "Schur_complement_source_coordinates": 268,
            "Schur_complement_source_rank": 235,
            "Schur_complement_source_nullity": 33,
            "limitation": "the two added 45s drive the anomaly-repaired one-loop pole ratio below 100",
        },
        "no_go": {
            "first_fatal_operator": "S epsilon_ab H_a^T A H_b / Lambda",
            "operator_degree": 4,
            "effect": "A0 has nonzero weak blocks, so the weak filter rank rises 16 -> 20",
            "scope": (
                "any additive ordinary selector retaining B^2, S A B, and epsilon H B H; "
                "the charge identity forces S epsilon H A H"
            ),
            "proton_leak": "S (16_F)^4 / Lambda^2 is also Z8 invariant at degree 5",
        },
        "gate_ledger": {
            f"G{i}": {
                "status": "OPEN",
                "reason": (
                    "same-action natural Higgs kernel is removed by a symmetry-allowed operator"
                    if i in (1, 2, 4) else "this bounded filter redesign does not establish the gate"
                ),
            }
            for i in range(1, 9)
        },
        "verdict": {
            "exact_intermediate_geometry": True,
            "generic_symmetry_complete_action_has_one_Higgs_pair": False,
            "complete_theory": False,
            "gate_promotion": False,
            "statement": (
                "The SU(2)_F filter and charged-spurion source have an exact same-action witness, "
                "but the selector itself allows S H A H, which removes the Higgs pair.  The minimal "
                "source-spurion redesign is therefore rejected."
            ),
        },
        "sources": {
            "Chen_Zhang_filter": "https://arxiv.org/abs/1410.5625",
            "Witten_SU2_anomaly_check": "https://arxiv.org/abs/hep-lat/0209098",
            "four_dimensional_R_symmetry_no_go": "https://arxiv.org/abs/1109.4797",
            "Delta27_SO10_example": "https://arxiv.org/abs/1512.00850",
        },
    }
    report["integrity_checks"] = {
        "source_rank145_null33": source_rank == 145 and SOURCE_EXT_DIM - source_rank == 33,
        "source_ward_and_kernel": report["source_vacuum"]["ward_product_zero"] and report["source_vacuum"]["kernel_equals_Spin10_gauge_orbit"],
        "filter_rank46_null4": filter_rank == 46 and FILTER_DIM - filter_rank == 4,
        "color30_weak16": exact_rank(filter_color) == 30 and exact_rank(filter_weak) == 16,
        "SU2_driver_rank2_orbit3": driver_rank == 2 and exact_rank(flavor_q) == 3,
        "declared_rank215_null40": h_rank == 215 and TOTAL_DIM - h_rank == 40,
        "combined_orbit36_and_ward": q_rank == 36 and np.count_nonzero(h @ q) == 0,
        "fatal_rank219_null36": h_fatal_rank == 219 and TOTAL_DIM - h_fatal_rank == 36,
        "all_required_Z8_terms_allowed": all(v == 0 for v in report["selector"]["required_term_residues"].values()),
        "all_direct_fatal_terms_forbidden": all(v != 0 for v in report["selector"]["direct_forbidden_residues"].values()),
        "all_exposed_terms_allowed": all(v == 0 for v in report["selector"]["first_exposed_residues"].values()),
        "conservative_Z8_anomalies_repaired": all(v == 0 for v in report["discrete_anomalies"]["total_mod8"].values()),
        "Witten_even_and_SU2F_b_zero": report["running"]["SU2_F"]["Witten_parity"] == 0 and report["running"]["SU2_F"]["one_loop_b"] == 0,
        "no_gate_promotion": not report["verdict"]["gate_promotion"],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    s = report["source_vacuum"]
    f = report["filter_ranks"]
    h = report["same_action_hessian"]
    run = report["running"]
    return "\n".join(
        [
            "# SUSY V54 non-Abelian filter route audit",
            "",
            f"Core: `{report['core_sha256']}`",
            "",
            f"Status: `{report['status']}`",
            "",
            "## Exact redesign witness",
            "",
            "The gauged `SU(2)_F` filter uses `H=(10,2)`, three singlet vectors `U,V,W`,",
            "two flavor doublets `P,Q`, and a neutral driver.  A charge-4 `Z8` singlet `S`",
            "replaces the incompatible A/B cross coefficients by `SAB` and `SEAB/Lambda`.",
            "",
            f"The 178-coordinate source has rank {s['hessian_rank']} and nullity {s['hessian_nullity']};",
            "its kernel is exactly the rank-33 broken Spin(10) orbit.  The SU(2)_F driver has",
            "rank 2 and nullity 3, exactly its complexified gauge orbit.",
            "",
            f"The 50-coordinate filter has rank {f['full_rank']}, color rank {f['color_rank']},",
            f"and weak rank {f['weak_rank']} with weak nullity {f['weak_nullity']}.",
            f"Including anomaly spectators, the declared {h['declared_coordinates']}-coordinate action",
            f"has rank {h['declared_rank']} and nullity {h['declared_nullity']} = 36 gauge + 4 weak.",
            "",
            "## Fatal symmetry completion",
            "",
            "The same selector necessarily allows `S epsilon_ab H_a^T A H_b / Lambda`.",
            "The identity is `s+a+b=0`, `2h+b=0`, `2b=0`, hence",
            "`s+2h+a=-2b=0`.  Since the exact A vacuum is nonzero in the weak blocks,",
            f"this operator raises the weak rank to {f['generic_fatal_weak_rank']} and the full",
            f"same-action rank to {h['symmetry_complete_with_fatal_operator_rank']}; only the 36 gauge",
            "directions remain.  `S(16_F)^4/Lambda^2` is also allowed at degree five.",
            "",
            "## Anomalies and running",
            "",
            "One 10 spectator pair of charges (1,3) and one singlet pair of charges (0,4),",
            "massive through S, cancel the conservative mod-8 mixed, gravitational, and cubic",
            "residues.  The SU(2)_F Witten count is 12 and its one-loop coefficient is zero.",
            f"The anomaly-repaired EFT has Spin(10) b={run['Spin10']['EFT_b']} and pole ratio",
            f"{run['Spin10']['EFT_pole_ratio']:.2f}.  A clean two-45 renormalizable completion",
            f"has b={run['Spin10']['UV_b']} and pole ratio {run['Spin10']['UV_pole_ratio']:.2f}.",
            "",
            "## Verdict",
            "",
            report["verdict"]["statement"],
            "No G1-G8 gate is promoted.",
            "",
            "Primary comparisons: [Chen-Zhang](https://arxiv.org/abs/1410.5625),",
            "[SU(2) global anomaly check](https://arxiv.org/abs/hep-lat/0209098), and",
            "[four-dimensional R-symmetry no-go](https://arxiv.org/abs/1109.4797).",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    assert report["core_sha256"] == canonical_sha(report)
    assert all(report["integrity_checks"].values())
    if args.write:
        JSON_PATH.write_text(
            json.dumps(
                report,
                indent=2,
                default=lambda item: item.item() if isinstance(item, np.generic) else str(item),
            ) + "\n",
            encoding="utf-8",
        )
        MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
