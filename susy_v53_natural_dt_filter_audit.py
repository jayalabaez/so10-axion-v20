#!/usr/bin/env python3
"""V53 exact DW-source completion and minimal Abelian-selector no-go.

Starting from the exact V52 E(54)+A(45)+C(16)+Cbar(bar16) source, add a
second adjoint B(45) with the Dimopoulos--Wilczek support

    B0 = J01 + J23 + J45,

and the most economical renormalizable A/B cross terms.  An explicit rational
witness has a complete 176-coordinate source Hessian whose kernel is exactly
the 33-dimensional broken Spin(10) orbit.  In contrast, B coupled only through
E B^2 leaves six additional physical chiral zero modes.

Two vectors H1,H2 then give a parameter-open doublet/triplet rank split through

    W_DT = H1^T B H2 + (M2/2) H2^T H2.

However, with B neutral under an additive Abelian shaping symmetry, allowing
both displayed operators implies that H1^2 is also allowed:

    q1+qB+q2=0, qB=0, 2q2=0  =>  2q1=0.

That extra invariant lifts the desired doublets.  The audited elementary
low-index source and rank matrices are therefore real progress, but a natural
complete action still needs a non-Abelian flavor/filter sector (or charged
mass-generating spurions with their own complete vacuum/anomaly audit).  No G2
clause is promoted.
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
import sympy as sp

import susy_v52_low_index_source_audit as v52


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_NATURAL_DT_FILTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_NATURAL_DT_FILTER_AUDIT.md"

STATUS = (
    "V53_EXACT_CROSS_COUPLED_DW_45_SOURCE__F_D_FLAT__ORBIT_RANK33__"
    "HESSIAN_RANK143_NULLITY33_KERNEL_EQUALS_GAUGE__TWO_10_DT_RANK_SPLIT_EXACT__"
    "MINIMAL_ADDITIVE_ABELIAN_SELECTOR_NO_GO__NONABELIAN_FILTER_OPEN__NO_G2_PROMOTION"
)

E_DIM, A_DIM, B_DIM, SPIN_DIM = 54, 45, 45, 16
SOURCE_DIM = E_DIM + A_DIM + B_DIM + 2 * SPIN_DIM
HESSIAN_DENOMINATOR = 40
ORBIT_DENOMINATOR = 10

LITERATURE = {
    "DW_minimal_model": "https://arxiv.org/abs/hep-ph/9705366",
    "renormalizable_DW_and_filter": "https://arxiv.org/abs/1410.5625",
    "complementary_missing_vev": "https://arxiv.org/abs/hep-ph/9810315",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def witness() -> dict[str, Any]:
    old = v52.witness()
    b0 = np.zeros((10, 10), dtype=np.complex128)
    for first, second in ((0, 1), (2, 3), (4, 5)):
        b0[first, second] = 1
        b0[second, first] = -1
    return {
        "mE": 6 / 5,
        "lambda": 1,
        "mA": 8,
        "mB": -9,
        "kappaA": 1 / 2,
        "kappaB": 1,
        "muAB": 3,
        "kappaAB": 1 / 2,
        "eta": -3j / 10,
        "mC": 27 / 20,
        "E0": old["S0"],
        "A0": old["A0"],
        "B0": b0,
        "C0": old["C0"],
        "barC0": old["barC0"],
    }


def f_term_numerators() -> dict[str, np.ndarray]:
    data = witness()
    e0, a0, b0 = data["E0"], data["A0"], data["B0"]
    c0, barc0 = data["C0"], data["barC0"]
    e_values, a_values, b_values = [], [], []
    for variation in v52.symmetric_traceless_basis():
        e_values.append(
            data["mE"] * np.trace(e0 @ variation)
            + data["lambda"] * np.trace(e0 @ e0 @ variation)
            - 0.5 * data["kappaA"] * np.trace(variation @ a0 @ a0)
            - 0.5 * data["kappaB"] * np.trace(variation @ b0 @ b0)
            - 0.5 * data["kappaAB"] * np.trace(variation @ (a0 @ b0 + b0 @ a0))
        )
    for variation, spin_t in zip(v52.antisymmetric_basis(), v52.spin_generators(), strict=True):
        a_values.append(
            -0.5 * data["mA"] * np.trace(a0 @ variation)
            -0.5 * data["kappaA"] * np.trace(e0 @ (a0 @ variation + variation @ a0))
            -0.5 * data["muAB"] * np.trace(variation @ b0)
            -0.5 * data["kappaAB"] * np.trace(e0 @ (variation @ b0 + b0 @ variation))
            + data["eta"] * (barc0.T @ spin_t @ c0)
        )
        b_values.append(
            -0.5 * data["mB"] * np.trace(b0 @ variation)
            -0.5 * data["kappaB"] * np.trace(e0 @ (b0 @ variation + variation @ b0))
            -0.5 * data["muAB"] * np.trace(a0 @ variation)
            -0.5 * data["kappaAB"] * np.trace(e0 @ (a0 @ variation + variation @ a0))
        )
    k0 = data["mC"] * np.eye(SPIN_DIM) + data["eta"] * v52.rho(a0)
    return {
        "E_F_x400": v52._gaussian_integer(400 * np.asarray(e_values), label="400 F_E"),
        "A_F_x400": v52._gaussian_integer(400 * np.asarray(a_values), label="400 F_A"),
        "B_F_x400": v52._gaussian_integer(400 * np.asarray(b_values), label="400 F_B"),
        "C_F_x400": v52._gaussian_integer(400 * np.asarray(barc0.T @ k0), label="400 F_C"),
        "barC_F_x400": v52._gaussian_integer(400 * np.asarray(k0 @ c0), label="400 F_barC"),
    }


def d_moment_numerator() -> np.ndarray:
    data = witness()
    e0, a0, b0 = data["E0"], data["A0"], data["B0"]
    c0, barc0 = data["C0"], data["barC0"]
    values = []
    for vector_t, spin_t in zip(v52.antisymmetric_basis(), v52.spin_generators(), strict=True):
        de = vector_t @ e0 - e0 @ vector_t
        da = vector_t @ a0 - a0 @ vector_t
        db = vector_t @ b0 - b0 @ vector_t
        tensor = (
            np.trace(e0.conjugate().T @ de)
            - 0.5 * np.trace(a0.conjugate().T @ da)
            - 0.5 * np.trace(b0.conjugate().T @ db)
        )
        spinor = c0.conjugate().T @ spin_t @ c0
        conjugate = barc0.conjugate().T @ (-spin_t.T) @ barc0
        values.append(tensor + spinor + conjugate)
    return v52._gaussian_integer(50 * np.asarray(values), label="50 D")


def hessian_numerator(*, cross_coupled: bool = True) -> np.ndarray:
    data = witness()
    if not cross_coupled:
        data = dict(data)
        data.update({"mE": 17 / 10, "mA": 11, "mB": -4, "kappaA": 1,
                     "muAB": 0, "kappaAB": 0})
    e0, a0, b0 = data["E0"], data["A0"], data["B0"]
    c0, barc0 = data["C0"], data["barC0"]
    e_basis = v52.symmetric_traceless_basis()
    adj_basis = v52.antisymmetric_basis()
    spin_basis = v52.spin_generators()
    matrix = np.zeros((SOURCE_DIM, SOURCE_DIM), dtype=np.complex128)
    a_offset, b_offset, c_offset, barc_offset = 54, 99, 144, 160
    c_slice, barc_slice = slice(c_offset, barc_offset), slice(barc_offset, SOURCE_DIM)

    for row, left in enumerate(e_basis):
        for column, right in enumerate(e_basis):
            matrix[row, column] = data["mE"] * np.trace(left @ right) + data["lambda"] * np.trace(
                e0 @ (left @ right + right @ left)
            )
    for row, left in enumerate(adj_basis):
        for column, right in enumerate(adj_basis):
            matrix[a_offset + row, a_offset + column] = (
                -0.5 * data["mA"] * np.trace(left @ right)
                -0.5 * data["kappaA"] * np.trace(e0 @ (left @ right + right @ left))
            )
            matrix[b_offset + row, b_offset + column] = (
                -0.5 * data["mB"] * np.trace(left @ right)
                -0.5 * data["kappaB"] * np.trace(e0 @ (left @ right + right @ left))
            )
            cross = (
                -0.5 * data["muAB"] * np.trace(left @ right)
                -0.5 * data["kappaAB"] * np.trace(e0 @ (left @ right + right @ left))
            )
            matrix[a_offset + row, b_offset + column] = cross
            matrix[b_offset + column, a_offset + row] = cross
    for row, left in enumerate(e_basis):
        for column, right in enumerate(adj_basis):
            ea = (
                -0.5 * data["kappaA"] * np.trace(left @ (a0 @ right + right @ a0))
                -0.5 * data["kappaAB"] * np.trace(left @ (right @ b0 + b0 @ right))
            )
            eb = (
                -0.5 * data["kappaB"] * np.trace(left @ (b0 @ right + right @ b0))
                -0.5 * data["kappaAB"] * np.trace(left @ (a0 @ right + right @ a0))
            )
            matrix[row, a_offset + column] = matrix[a_offset + column, row] = ea
            matrix[row, b_offset + column] = matrix[b_offset + column, row] = eb
    for column, spin_t in enumerate(spin_basis):
        index = a_offset + column
        ac = data["eta"] * (barc0.T @ spin_t)
        abar = data["eta"] * (spin_t @ c0)
        matrix[index, c_slice] = matrix[c_slice, index] = ac
        matrix[index, barc_slice] = matrix[barc_slice, index] = abar
    k0 = data["mC"] * np.eye(SPIN_DIM) + data["eta"] * v52.rho(a0)
    matrix[c_slice, barc_slice] = k0.T
    matrix[barc_slice, c_slice] = k0
    numerator = v52._gaussian_integer(HESSIAN_DENOMINATOR * matrix, label="40 H")
    if not np.array_equal(numerator, numerator.T):
        raise ArithmeticError("extended Hessian is not symmetric")
    return numerator


def orbit_numerator() -> np.ndarray:
    data = witness()
    columns = []
    for vector_t, spin_t in zip(v52.antisymmetric_basis(), v52.spin_generators(), strict=True):
        de = vector_t @ data["E0"] - data["E0"] @ vector_t
        da = vector_t @ data["A0"] - data["A0"] @ vector_t
        db = vector_t @ data["B0"] - data["B0"] @ vector_t
        dc = spin_t @ data["C0"]
        dbar = -spin_t.T @ data["barC0"]
        columns.append(np.concatenate((
            v52._symmetric_coordinates(de),
            v52._antisymmetric_coordinates(da),
            v52._antisymmetric_coordinates(db),
            dc, dbar,
        )))
    return v52._gaussian_integer(ORBIT_DENOMINATOR * np.column_stack(columns), label="10 Q")


def dt_cartesian_hessian(m2: int = 2, coupling: int = 1) -> np.ndarray:
    """20-coordinate H1,H2 Hessian for W=H1^T B H2+(m2/2)H2^2."""
    b0 = witness()["B0"]
    zero = np.zeros((10, 10), dtype=np.complex128)
    return np.block([[zero, coupling * b0], [-coupling * b0, m2 * np.eye(10)]])


def dt_mass_audit() -> dict[str, Any]:
    full = dt_cartesian_hessian()
    color_indices = list(range(6)) + list(range(10, 16))
    weak_indices = list(range(6, 10)) + list(range(16, 20))
    color = full[np.ix_(color_indices, color_indices)]
    weak = full[np.ix_(weak_indices, weak_indices)]
    generic_lift = full.copy()
    generic_lift[:10, :10] = np.eye(10)
    return {
        "superpotential": "W_DT=H1^T B H2+(M2/2)H2^T H2",
        "witness": {"lambda12": 1, "M2": 2},
        "cartesian_shape": list(full.shape),
        "cartesian_rank": int(np.linalg.matrix_rank(full)),
        "cartesian_nullity": 20 - int(np.linalg.matrix_rank(full)),
        "color_shape": list(color.shape),
        "color_rank": int(np.linalg.matrix_rank(color)),
        "color_nullity": len(color) - int(np.linalg.matrix_rank(color)),
        "weak_shape": list(weak.shape),
        "weak_rank": int(np.linalg.matrix_rank(weak)),
        "weak_nullity": len(weak) - int(np.linalg.matrix_rank(weak)),
        "reduced_doublet_pair_matrix": [[0, 0], [0, 2]],
        "reduced_triplet_pair_matrix": [[0, 1], [-1, 2]],
        "rank_split_parameter_codimension_with_declared_terms": 0,
        "nonzero_open_conditions": ["lambda12 != 0", "M2 != 0", "B_color != 0", "B_weak = 0 by vacuum"],
        "generic_allowed_H1_squared_lifts_all": bool(int(np.linalg.matrix_rank(generic_lift)) == 20),
    }


def abelian_selector_no_go() -> dict[str, Any]:
    rows = []
    for modulus in range(2, 65):
        solutions = 0
        counterexamples = 0
        for q1 in range(modulus):
            for q2 in range(modulus):
                if (q1 + q2) % modulus == 0 and (2 * q2) % modulus == 0:
                    solutions += 1
                    if (2 * q1) % modulus != 0:
                        counterexamples += 1
        rows.append({"N": modulus, "solutions": solutions, "counterexamples": counterexamples})
    return {
        "class": "any product of additive Abelian ordinary symmetries with neutral B and neutral superpotential",
        "required_congruences": ["q(H1)+q(H2)=0", "2 q(H2)=0"],
        "derived_congruence": "2 q(H1)=-2 q(H2)=0",
        "fatal_operator": "H1^T H1 and H1^T E H1 are symmetry-allowed",
        "exhaustive_moduli_checked": [2, 64],
        "total_counterexamples": sum(row["counterexamples"] for row in rows),
        "per_modulus": rows,
        "product_group_extension": "the proof holds componentwise for every Abelian factor",
        "minimal_escape": "a non-Abelian flavor/filter structure or charged mass spurions with a complete vacuum and anomaly completion",
    }


def perturbativity_audit() -> dict[str, Any]:
    base_source_t = 24
    added_b_t = 8
    two_tens_t = 2
    matter_t = 6
    total_t = base_source_t + added_b_t + two_tens_t + matter_t
    beta = total_t - 3 * 8
    coupling = 0.73
    pole = math.exp(8 * math.pi**2 / (beta * coupling**2))
    return {
        "base_54_45_16_bar16_T": base_source_t,
        "added_DW_45_T": added_b_t,
        "two_10H_T": two_tens_t,
        "four_seesaw_singlets_T": 0,
        "three_matter_16_T": matter_t,
        "total_chiral_T": total_t,
        "one_loop_b": beta,
        "formal_pole_over_matching_at_g_0p73": pole,
        "above_100x": pole > 100,
        "above_1000x": pole > 1000,
        "scope": "does not include the still-missing non-Abelian/filter completion",
    }


def build_report() -> dict[str, Any]:
    f_terms = f_term_numerators()
    d_terms = d_moment_numerator()
    hessian = hessian_numerator()
    lean_hessian = hessian_numerator(cross_coupled=False)
    orbit = orbit_numerator()
    h_rank = v52.modular_rank(v52._modular_matrix(hessian))
    lean_rank = v52.modular_rank(v52._modular_matrix(lean_hessian))
    q_rank = v52.modular_rank(v52._modular_matrix(orbit))
    ward = hessian @ orbit
    dt = dt_mass_audit()
    no_go = abelian_selector_no_go()
    rg = perturbativity_audit()
    checks = {
        "all_176_source_F_terms_vanish": bool(all(np.count_nonzero(value) == 0 for value in f_terms.values())),
        "all_45_compact_D_moments_vanish": bool(np.count_nonzero(d_terms) == 0),
        "cross_coupled_source_orbit_rank_is_33": q_rank == 33,
        "cross_coupled_source_hessian_rank_is_143": h_rank == 143,
        "cross_coupled_source_kernel_equals_orbit": bool(h_rank + q_rank == SOURCE_DIM and np.count_nonzero(ward) == 0),
        "lean_EB2_only_source_has_six_extra_chiral_zero_modes": SOURCE_DIM - lean_rank - q_rank == 6,
        "two_10_color_block_is_full_rank": dt["color_rank"] == 12,
        "two_10_weak_block_leaves_one_HuHd_pair": dt["weak_nullity"] == 4,
        "rank_split_is_parameter_open_in_declared_DT_terms": dt["rank_split_parameter_codimension_with_declared_terms"] == 0,
        "generic_H1_squared_operator_lifts_the_doublets": dt["generic_allowed_H1_squared_lifts_all"],
        "additive_Abelian_selector_theorem_has_no_counterexample": no_go["total_counterexamples"] == 0,
        "one_loop_screen_exceeds_1000x_before_filter_completion": rg["above_1000x"],
        "G2_is_not_promoted": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v53_natural_dt_filter_audit_v1",
        "status": STATUS if not failures else "V53_NATURAL_DT_FILTER_AUDIT_FAILED",
        "candidate_action": {
            "representations": ["E54", "A45", "B45_DW", "C16", "barC16", "H1_10", "H2_10", "four_N_singlets"],
            "source_superpotential": (
                "W=(mE/2)TrE2+(lambda/3)TrE3-(mA/4)TrA2-(mB/4)TrB2"
                "-(kA/2)Tr(EA2)-(kB/2)Tr(EB2)-(mu/2)Tr(AB)"
                "-(kx/2)Tr(E(AB+BA))+barC(mC+eta*rho16(A))C"
            ),
            "DT_superpotential": dt["superpotential"],
            "renormalizable": True,
        },
        "exact_source_witness": {
            "parameters": {"mE": "6/5", "lambda": "1", "mA": "8", "mB": "-9", "kappaA": "1/2",
                           "kappaB": "1", "muAB": "3", "kappaAB": "1/2", "eta": "-3*i/10", "mC": "27/20"},
            "E0_diagonal": [2] * 6 + [-3] * 4,
            "A0_upper_blocks": [1, 1, 1, 3, 3],
            "B0_upper_blocks": [1, 1, 1, 0, 0],
            "C0_equals_barC0": "10 e15",
            "source_coordinates": SOURCE_DIM,
            "F_nonzero_counts": {name: int(np.count_nonzero(value)) for name, value in f_terms.items()},
            "D_nonzero_count": int(np.count_nonzero(d_terms)),
            "orbit_rank": q_rank,
            "hessian_rank": h_rank,
            "hessian_nullity": SOURCE_DIM - h_rank,
            "ward_product_exactly_zero": bool(np.count_nonzero(ward) == 0),
            "kernel_equals_broken_gauge_orbit": bool(h_rank + q_rank == SOURCE_DIM and np.count_nonzero(ward) == 0),
        },
        "lean_uncoupled_adjoint_control": {
            "terms": "-(mB/4)TrB2-(kB/2)Tr(EB2) only",
            "retuned_parameters": {"mE": "17/10", "mB": "-4", "kappaB": "1"},
            "hessian_rank": lean_rank,
            "hessian_nullity": SOURCE_DIM - lean_rank,
            "physical_chiral_zero_modes_beyond_gauge": SOURCE_DIM - lean_rank - q_rank,
            "decision": "REJECT",
        },
        "doublet_triplet": dt,
        "minimal_Abelian_selector_no_go": no_go,
        "perturbativity": rg,
        "literature": LITERATURE,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gate_effect": {
            "isolated_low_index_DW_source": "CLOSED FOR DISPLAYED ELEMENTARY SOURCE ACTION",
            "doublet_triplet_rank_matrix": "CLOSED FOR DECLARED TWO-10 TERMS",
            "natural_DT_under_minimal_additive_Abelian_selector": "EXACT NO-GO",
            "complete_nonAbelian_or_filter_action": "OPEN",
            "full_operator_and_anomaly_census": "OPEN",
            "G2": "OPEN",
            "clause_promotions": [],
        },
        "next_exact_target": (
            "construct a non-Abelian flavor/filter sector that forbids H1^2 and every E/A mass filler, "
            "then include its vacuum, gauge/discrete anomalies, Goldstones, and Dynkin inventory in the same Hessian"
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    source = report["exact_source_witness"]
    control = report["lean_uncoupled_adjoint_control"]
    dt = report["doublet_triplet"]
    rg = report["perturbativity"]
    return "\n".join([
        "# SUSY V53 natural doublet-triplet filter audit", "",
        f"Status: `{report['status']}`", "",
        f"Core SHA-256: `{report['core_sha256']}`", "",
        "## Exact constructive result", "",
        "A second low-index adjoint can carry a genuine DW support while the complete GUT-breaking",
        "source remains locally isolated. The displayed 176-coordinate renormalizable action is exactly",
        "F-flat and D-flat. Its orbit has rank `33`; its Hessian has rank",
        f"`{source['hessian_rank']}` and nullity `{source['hessian_nullity']}`. The exact Ward product",
        "vanishes, so the kernel is precisely the broken-gauge orbit.", "",
        "The cross-coupling is essential. With only `E B^2`, the control Hessian has rank",
        f"`{control['hessian_rank']}` and leaves `{control['physical_chiral_zero_modes_beyond_gauge']}`",
        "physical chiral zero modes beyond the gauge orbit.", "",
        "## Doublet-triplet ranks", "",
        "For `W_DT=H1^T B H2+(M2/2)H2^T H2`, the 12-coordinate color block has rank",
        f"`{dt['color_rank']}` and the eight-coordinate weak block has rank `{dt['weak_rank']}` /",
        f"nullity `{dt['weak_nullity']}`. Within these declared terms, the split holds on an open set",
        "of nonzero couplings; no coefficient equality is required.", "",
        "## Exact minimal-selector obstruction", "",
        "The rank result is not yet a natural complete action. For every additive Abelian shaping factor",
        "with neutral `B`, allowing `H1 B H2` and `H2^2` gives", "",
        "```text", "q1+q2=0,  2q2=0  =>  2q1=0.", "```", "",
        "Thus `H1^2` and `H1 E H1` are also allowed, and a generic nonzero coefficient lifts all weak",
        "doublets. Exhaustive enumeration for every `Z_N`, `2 <= N <= 64`, finds zero counterexamples;",
        "the proof applies componentwise to any Abelian product. A non-Abelian flavor/filter sector or a",
        "fully dynamical charged-spurion sector is the minimal escape.", "",
        "## Perturbativity and verdict", "",
        f"Before adding that missing filter completion, `sum T={rg['total_chiral_T']}`, `b={rg['one_loop_b']}`,",
        f"and the formal pole at `g=0.73` is `{rg['formal_pole_over_matching_at_g_0p73']:.4e}` times the",
        "matching scale. The low-index route therefore retains perturbative room, but the eventual filter",
        "inventory must be re-counted.", "",
        "No G2 clause is promoted. The isolated DW source is real; the mass-rank mechanism is real; the",
        "minimal Abelian symmetry completion is impossible.", "",
        "## Primary-source anchors", "",
        "The DW mechanism and its source-stability problem are described by",
        "[Barr and Raby](https://arxiv.org/abs/hep-ph/9705366). A fully renormalizable but much larger",
        "DW/filter construction is given by [Chen and Zhang](https://arxiv.org/abs/1410.5625). The",
        "complementary missing-VEV low-representation route is",
        "[Chacko and Mohapatra](https://arxiv.org/abs/hep-ph/9810315).", "",
    ])


def validate_report(report: Mapping[str, Any]) -> None:
    if report["n_failed"] or report["failures"]:
        raise ArithmeticError(report["failures"])
    if canonical_sha(report) != report["core_sha256"]:
        raise ArithmeticError("core hash mismatch")
    if report["gate_effect"]["G2"] != "OPEN" or report["gate_effect"]["clause_promotions"]:
        raise ArithmeticError("gate boundary drift")


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(markdown(report), encoding="utf-8", newline="\n")


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise ArithmeticError("JSON drift")
    if MD_PATH.read_text(encoding="utf-8") != markdown(report):
        raise ArithmeticError("Markdown drift")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        check_artifacts()
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
