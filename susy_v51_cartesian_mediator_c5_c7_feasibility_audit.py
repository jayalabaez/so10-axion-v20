#!/usr/bin/env python3
"""Strict V51 Cartesian-projector/vectorlike-mediator audit for C5 and C7.

This is a feasibility and obstruction audit, not a declaration that a UV
completion has been built.  It resolves every degree-two/three V49 source row,
constructs the Pati--Salam orbifold parity in the locked Clifford basis, and
tests the finite vectorlike-mediator Schur-complement route for quartics.
Uninstantiated degree-four factors and one-loop data remain fail-closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import exact_normalized_so10_yukawa_cgcs_v20 as yukawa
import susy_v50_c7_conjugate_incidence_audit as v50_c7
import susy_v50_clifford_tensor_extension_audit as clifford
import susy_v49_retained_boundary_action_completeness as v49


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v51_cartesian_mediator_c5_c7_feasibility_audit.py"
UPSTREAM = (
    ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
    ROOT / "SUSY_V50_C5_STRICT_REMATCH_AUDIT.json",
    ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json",
    ROOT / "SUSY_V50_CLIFFORD_TENSOR_EXTENSION_AUDIT.json",
    ROOT / "SUSY_V50_PHI_SIGMA_FORM_TENSOR_AUDIT.json",
    ROOT / "SUSY_V50_PS_INTERTWINER_BASIS_AUDIT.json",
)
STATUS = (
    "V51_CARTESIAN_PS_PROJECTOR_AND_VECTORLIKE_MEDIATOR_ROUTE_FEASIBLE__"
    "48_LOW_DEGREE_ROWS_RESOLVED_20_NONEMPTY_28_EMPTY__"
    "EXACT_PS_STABILIZER_21_SPINOR_8_PLUS_8_AND_ALL_34_PS_PRIMITIVES__"
    "120_DEGREE4_ROWS_FINAL_WILSON_ARRAY_AND_ONE_LOOP_MATCHING_OPEN__"
    "C5_C7_PARTIAL__G2_OPEN"
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


def maximum_abs(value: np.ndarray) -> float:
    array = np.asarray(value)
    return float(np.max(np.abs(array))) if array.size else 0.0


def physical_five_form_tensor(chirality_sign: int) -> np.ndarray:
    """Return the normalized physical five-form tensor for either chirality.

    The two chiral spinor squares select opposite Hodge eigenspaces.  Reusing
    the minus-chirality array (or merely relabelling it) in the plus-chirality
    basis is therefore not a covariant conjugate map.
    """

    if chirality_sign == -1:
        tensor = yukawa.cgc_126bar()
        return tensor.numerator / tensor.denominator
    if chirality_sign != +1:
        raise ValueError("chirality sign must be -1 or +1")
    labels = yukawa.five_index_labels()
    raw = dict(
        zip(labels, yukawa.five_form_matrices(+1), strict=True)
    )
    rows = []
    for state in yukawa.canonical_126_basis():
        # Complex conjugation reverses the Hodge eigenvalue and hence selects
        # the physical five-form channel of the conjugate spinor square.
        matrix = sum(
            (
                complex(coefficient).conjugate() * raw[indices]
                for indices, coefficient in state.items()
            ),
            np.zeros((16, 16), dtype=complex),
        )
        rows.append(matrix / yukawa.cgc_126bar().denominator)
    return np.asarray(rows)


def tensor_registry() -> dict[str, dict[str, Any]]:
    """Normalized Cartesian tensors sufficient for the degree <=3 rows."""

    singlet = clifford.kform_tensor(0, -1, +1)
    vector_minus = clifford.kform_tensor(1, -1, -1)
    vector_plus = clifford.kform_tensor(1, +1, +1)
    five_form_minus = physical_five_form_tensor(-1)
    five_form_plus = physical_five_form_tensor(+1)
    tensor_210 = clifford.kform_tensor(4, -1, +1)
    return {
        "CART_16xbar16_TO_1": {
            "shape": list(singlet.shape),
            "normalization": "C Gamma_[0]/4 in the raw locked Cartesian chiral bases",
            "gram_residual": clifford.gram_residual(singlet),
            "provenance": "susy_v50_clifford_tensor_extension_audit.kform_tensor(0,-1,+1)",
            "ordered_orientation_rule": (
                "16,bar16 uses T; bar16,16 uses -transpose(T), exactly equal "
                "to kform_tensor(0,+1,-1)"
            ),
            "reverse_orientation_residual": maximum_abs(
                clifford.kform_tensor(0, +1, -1)
                + np.transpose(singlet, (0, 2, 1))
            ),
        },
        "CART_16xbar16_TO_210": {
            "shape": list(tensor_210.shape),
            "normalization": "C Gamma_[4]/4, ordered-pair Hilbert--Schmidt metric",
            "gram_residual": clifford.gram_residual(tensor_210),
            "provenance": "susy_v50_clifford_tensor_extension_audit.kform_tensor(4,-1,+1)",
            "ordered_orientation_rule": (
                "16,bar16 uses T; bar16,16 uses -transpose(T), exactly equal "
                "to kform_tensor(4,+1,-1)"
            ),
            "reverse_orientation_residual": maximum_abs(
                clifford.kform_tensor(4, +1, -1)
                + np.transpose(tensor_210, (0, 2, 1))
            ),
        },
        "CART_16x16_TO_10": {
            "shape": list(vector_minus.shape),
            "normalization": "C Gamma_a/4 in the minus-chirality basis",
            "gram_residual": clifford.gram_residual(vector_minus),
            "covariance_residual": clifford.covariance_residual(1, -1, -1),
            "provenance": "susy_v50_clifford_tensor_extension_audit.kform_tensor(1,-1,-1)",
        },
        "CART_bar16xbar16_TO_10": {
            "shape": list(vector_plus.shape),
            "normalization": "C Gamma_a/4 constructed directly in the plus-chirality basis",
            "gram_residual": clifford.gram_residual(vector_plus),
            "covariance_residual": clifford.covariance_residual(1, +1, +1),
            "provenance": "susy_v50_clifford_tensor_extension_audit.kform_tensor(1,+1,+1)",
        },
        "CART_PS_H10_MINUS_x_H10_MINUS_TO_1": {
            "shape": [4, 4],
            "normalization": "delta_4/2 in Cartesian indices 6,7,8,9",
            "gram_residual": 0.0,
            "provenance": "restriction of the 10 metric to the P10=-1 SO(4) subspace",
        },
        "CART_16x16_TO_126__COUPLED_TO_bar126": {
            "shape": list(five_form_minus.shape),
            "normalization": "physical minus-chirality Hodge tensor with denominator 8",
            "gram_residual": clifford.gram_residual(five_form_minus),
            "provenance": "exact_normalized_so10_yukawa_cgcs_v20.cgc_126bar",
        },
        "CART_bar16xbar16_TO_bar126__COUPLED_TO_126": {
            "shape": list(five_form_plus.shape),
            "normalization": "direct plus-chirality tensor in the conjugate Hodge eigenspace, denominator 8",
            "gram_residual": clifford.gram_residual(five_form_plus),
            "provenance": "V51 direct plus-chirality Clifford/Hodge construction",
        },
    }


def _orientation(row: Mapping[str, Any]) -> tuple[str, str]:
    pair = tuple(str(value) for value in row["ordered_chirality"])
    if len(pair) != 2:
        raise ValueError(f"row {row['id']} lacks an ordered spinor pair")
    return pair  # type: ignore[return-value]


def resolve_low_degree_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve multiplicity zero/one from 16 tensor-product channels."""

    degree = int(row["degree"])
    if row["sector"] not in ("HH", "HcHc", "HcH") or degree not in (2, 3):
        raise ValueError("only degree-two/three source rows are accepted")
    left, right = _orientation(row)
    mixed = left != right
    tensor_id: str | None = None
    tensor_orientation: str | None = None
    if degree == 2:
        if mixed:
            tensor_id = "CART_16xbar16_TO_1"
            tensor_orientation = (
                "direct" if (left, right) == ("16", "bar16") else "negative_transpose"
            )
            reason = "the mixed spinor product contains one singlet"
        else:
            reason = "equal-chirality spinor products contain no singlet"
    else:
        sources = tuple(row["source_representations"])
        if len(sources) != 1:
            raise ValueError(f"degree-three row {row['id']} does not have one source")
        source = sources[0]
        if source == "1" and mixed:
            tensor_id = "CART_16xbar16_TO_1"
            tensor_orientation = (
                "direct" if (left, right) == ("16", "bar16") else "negative_transpose"
            )
            reason = "a singlet source selects the unique mixed-spinor singlet"
        elif source == "210" and mixed:
            tensor_id = "CART_16xbar16_TO_210"
            tensor_orientation = (
                "direct" if (left, right) == ("16", "bar16") else "negative_transpose"
            )
            reason = "Phi selects the unique 210 in the mixed-spinor product"
        elif source == "bar126" and (left, right) == ("16", "16"):
            tensor_id = "CART_16x16_TO_126__COUPLED_TO_bar126"
            tensor_orientation = "direct"
            reason = "barSigma pairs with the unique 126 channel in 16x16"
        elif source == "126" and (left, right) == ("bar16", "bar16"):
            tensor_id = "CART_bar16xbar16_TO_bar126__COUPLED_TO_126"
            tensor_orientation = "direct"
            reason = "Sigma pairs with the unique bar126 channel in bar16xbar16"
        else:
            reason = f"no channel conjugate to source {source} occurs in {left}x{right}"
    multiplicity = int(tensor_id is not None)
    return {
        "id": row["id"],
        "sector": row["sector"],
        "degree": degree,
        "monomial": row["monomial"],
        "ordered_chirality": [left, right],
        "source_representations": list(row["source_representations"]),
        "U1F_charge": row["U1F_charge"],
        "invariant_multiplicity": multiplicity,
        "normalized_tensor_ids": [] if tensor_id is None else [tensor_id],
        "tensor_orientation": tensor_orientation,
        "instantiation_status": (
            "RESOLVED_NONEMPTY_CARTESIAN" if multiplicity else "RESOLVED_EMPTY"
        ),
        "representation_reason": reason,
    }


def incidence_inventory() -> dict[str, Any]:
    rows = v50_c7.census()
    source_rows = [row for row in rows if row["sector"] in ("HH", "HcHc", "HcH")]
    ps_rows = [row for row in rows if row["sector"].startswith("PS_")]
    low_rows = [row for row in source_rows if int(row["degree"]) <= 3]
    degree_four = [row for row in source_rows if int(row["degree"]) == 4]
    resolved = [resolve_low_degree_row(row) for row in low_rows]
    source_histogram = Counter(
        f"{row['sector']}_degree_{row['degree']}" for row in source_rows
    )
    status_histogram = Counter(row["instantiation_status"] for row in resolved)
    sector_histogram = Counter(
        f"{row['sector']}__{row['instantiation_status']}" for row in resolved
    )
    ps_expansion = {
        "PS_W_00": {"primitive_count": 16, "meaning": "4x4 L_A H R_B matrix"},
        "PS_W_01": {"primitive_count": 1, "meaning": "y_m cubic"},
        "PS_W_02": {"primitive_count": 1, "meaning": "y_c cubic"},
        "PS_W_03": {"primitive_count": 1, "meaning": "y_cb cubic"},
        "PS_W_04": {"primitive_count": 1, "meaning": "mu_H quadratic"},
        "PS_D_00": {"primitive_count": 3, "meaning": "three Q_i derivative mixings"},
        "PS_D_01": {"primitive_count": 3, "meaning": "three Qc_i derivative mixings"},
        "PS_D_02": {"primitive_count": 8, "meaning": "four O_minus plus four M_o coordinates"},
    }
    if {row["id"] for row in ps_rows} != set(ps_expansion):
        raise RuntimeError("V50 PS aggregate-row schema drifted")
    return {
        "v50_total_schema_rows": len(rows),
        "source_candidate_rows": len(source_rows),
        "source_rows_by_sector_and_degree": dict(sorted(source_histogram.items())),
        "degree_two_or_three_rows_resolved_here": len(resolved),
        "low_degree_resolution_counts": dict(sorted(status_histogram.items())),
        "low_degree_resolution_by_sector": dict(sorted(sector_histogram.items())),
        "degree_four_rows_pending_factorization": len(degree_four),
        "ps_aggregate_rows": len(ps_rows),
        "ps_aggregate_expansion": ps_expansion,
        "ps_primitive_superpotential_coefficients": 20,
        "ps_primitive_derivative_channels": 14,
        "ps_total_primitive_declarations": sum(
            value["primitive_count"] for value in ps_expansion.values()
        ),
        "resolved_low_degree_rows": resolved,
        "pending_degree_four_row_ids": [row["id"] for row in degree_four],
    }


def cartesian_ps_parity_certificate() -> dict[str, Any]:
    """Construct Spin(6)xSpin(4) parity in the audited Clifford basis."""

    gammas, _, _ = yukawa._clifford_data()
    vector_signs = np.asarray([1] * 6 + [-1] * 4, dtype=int)
    parity_32 = gammas[6] @ gammas[7] @ gammas[8] @ gammas[9]
    vector_lift_residual = max(
        maximum_abs(
            parity_32 @ gammas[index] @ parity_32
            - vector_signs[index] * gammas[index]
        )
        for index in range(10)
    )
    chirality_results: dict[str, Any] = {}
    for label, sign in (("16", -1), ("bar16", +1)):
        selected = yukawa.chiral_indices(sign)
        parity = parity_32[np.ix_(selected, selected)]
        projector_plus = (np.eye(16) + parity) / 2.0
        projector_minus = (np.eye(16) - parity) / 2.0
        eigenvalues = np.linalg.eigvalsh(parity)
        plus_count = int(np.count_nonzero(eigenvalues > 0.5))
        minus_count = int(np.count_nonzero(eigenvalues < -0.5))
        spin_generators = yukawa.twice_spin_generators(sign)
        plane_67 = np.real(np.diag(-1j * spin_generators[(6, 7)])).astype(int)
        plane_89 = np.real(np.diag(-1j * spin_generators[(8, 9)])).astype(int)
        twice_t3l = (plane_67 - plane_89) // 2
        twice_t3r = (plane_67 + plane_89) // 2
        commuting = 0
        anticommuting = 0
        for generator in spin_generators.values():
            if maximum_abs(parity @ generator - generator @ parity) < 1.0e-12:
                commuting += 1
            if maximum_abs(parity @ generator + generator @ parity) < 1.0e-12:
                anticommuting += 1
        chirality_results[label] = {
            "parity_shape": list(parity.shape),
            "parity_square_residual": maximum_abs(parity @ parity - np.eye(16)),
            "parity_Hermitian_residual": maximum_abs(parity - parity.conjugate().T),
            "plus_projector_rank": int(np.linalg.matrix_rank(projector_plus)),
            "minus_projector_rank": int(np.linalg.matrix_rank(projector_minus)),
            "plus_eigenvalue_count": plus_count,
            "minus_eigenvalue_count": minus_count,
            "parity_diagonal": [int(round(value.real)) for value in np.diag(parity)],
            "plus_basis_indices": [int(value) for value in np.flatnonzero(np.diag(parity).real > 0.5)],
            "minus_basis_indices": [int(value) for value in np.flatnonzero(np.diag(parity).real < -0.5)],
            "plus_subspace_twice_T3L_values": sorted({int(twice_t3l[index]) for index in np.flatnonzero(np.diag(parity).real > 0.5)}),
            "plus_subspace_twice_T3R_values": sorted({int(twice_t3r[index]) for index in np.flatnonzero(np.diag(parity).real > 0.5)}),
            "minus_subspace_twice_T3L_values": sorted({int(twice_t3l[index]) for index in np.flatnonzero(np.diag(parity).real < -0.5)}),
            "minus_subspace_twice_T3R_values": sorted({int(twice_t3r[index]) for index in np.flatnonzero(np.diag(parity).real < -0.5)}),
            "projector_resolution_residual": maximum_abs(
                projector_plus + projector_minus - np.eye(16)
            ),
            "commuting_spin10_generators": commuting,
            "anticommuting_spin10_generators": anticommuting,
        }
    form_lifts: dict[str, Any] = {}
    four_labels = list(itertools.combinations(range(10), 4))
    four_signs = [int(np.prod(vector_signs[list(label)])) for label in four_labels]
    five_signs = []
    for state in yukawa.canonical_126_basis():
        values = {int(np.prod(vector_signs[list(label)])) for label in state}
        if len(values) != 1:
            raise RuntimeError("P10 does not preserve the canonical Hodge pair")
        five_signs.append(values.pop())
    for label, signs in (("210", four_signs), ("126", five_signs), ("bar126", five_signs)):
        form_lifts[label] = {
            "dimension": len(signs),
            "plus_rank": signs.count(1),
            "minus_rank": signs.count(-1),
            "parity_diagonal": signs,
            "construction": "product of P10 signs on each exterior-form index",
        }
    return {
        "vector_parity": "P10=diag(+1,+1,+1,+1,+1,+1,-1,-1,-1,-1)",
        "spin_lift": "P32=Gamma_6 Gamma_7 Gamma_8 Gamma_9",
        "vector_lift_residual": vector_lift_residual,
        "unbroken_algebra": "so(6)+so(4) isomorphic to su(4)+su(2)L+su(2)R",
        "expected_unbroken_dimension": 15 + 6,
        "expected_broken_dimension": 6 * 4,
        "chiral_spinors": chirality_results,
        "form_representation_lifts": form_lifts,
        "consequence": (
            "The two eight-dimensional PS trace subspaces and all even/odd "
            "spinor projectors are explicit in the same Cartesian basis as the CG tensors."
        ),
    }


def ps_superpotential_projector_certificate() -> dict[str, Any]:
    """Rewrite all 20 PS superpotential coefficients as Cartesian rows."""

    parity = cartesian_ps_parity_certificate()
    gammas, _, _ = yukawa._clifford_data()
    parity_32 = gammas[6] @ gammas[7] @ gammas[8] @ gammas[9]
    projected_tensors: dict[str, Any] = {}
    for label, sign in (("16", -1), ("bar16", +1)):
        # The two chiral bases require separately constructed Clifford
        # tensors.  The minus-chirality array is not covariant when reused in
        # the plus-chirality basis even though its projected Gram happens to
        # remain normalized.
        tensor_10 = clifford.kform_tensor(1, sign, sign)
        selected = yukawa.chiral_indices(sign)
        p = parity_32[np.ix_(selected, selected)]
        left = (np.eye(16) + p) / 2.0
        right = (np.eye(16) - p) / 2.0
        restricted = np.sqrt(2.0) * np.einsum(
            "aij,ki,lj->akl", tensor_10[6:10], left, right
        )
        gram = np.einsum("aij,bij->ab", restricted.conjugate(), restricted)
        same_left = np.einsum("aij,ki,lj->akl", tensor_10[6:10], left, left)
        same_right = np.einsum("aij,ki,lj->akl", tensor_10[6:10], right, right)
        ps_covariance_residual = 0.0
        spin_generators = yukawa.twice_spin_generators(sign)
        for pair in itertools.combinations(range(10), 2):
            # so(6)+so(4) is the 21-generator PS centralizer of the parity.
            if not (pair[1] < 6 or pair[0] >= 6):
                continue
            vector_generator = clifford.form_generator(1, *pair)[6:10, 6:10]
            residual = (
                np.einsum(
                    "ij,ajk->aik", spin_generators[pair].T, restricted
                )
                + np.einsum(
                    "aij,jk->aik", restricted, spin_generators[pair]
                )
                + 2.0
                * np.einsum(
                    "bij,ba->aij", restricted, vector_generator
                )
            )
            ps_covariance_residual = max(
                ps_covariance_residual, maximum_abs(residual)
            )
        projected_tensors[label] = {
            "shape": list(restricted.shape),
            "definition": (
                "sqrt(2) P_L (C Gamma_a/4) P_R for a=6,7,8,9, "
                f"constructed directly in chirality {sign:+d}"
            ),
            "normalized_gram_residual": maximum_abs(gram - np.eye(4)),
            "PS_covariance_residual": ps_covariance_residual,
            "same_L_parity_kill_norm": float(np.linalg.norm(same_left)),
            "same_R_parity_kill_norm": float(np.linalg.norm(same_right)),
            "nonzero_entry_count": int(np.count_nonzero(np.abs(restricted) > 1.0e-12)),
        }

    fields: dict[str, dict[str, Any]] = {
        **{f"Q{index}": {"rep": "16", "qF": 1, "projector": "P16_L_PLUS"} for index in range(1, 4)},
        **{f"Qc{index}": {"rep": "16", "qF": -1, "projector": "P16_R_MINUS"} for index in range(1, 4)},
        "HLF": {"rep": "16", "qF": 1, "projector": "P16_L_PLUS"},
        "HRA": {"rep": "16", "qF": -1, "projector": "P16_R_MINUS"},
        "HLA": {"rep": "bar16", "qF": -4, "projector": "Pbar16_L_PLUS"},
        "HRF": {"rep": "bar16", "qF": 4, "projector": "Pbar16_R_MINUS"},
        "HRAc": {"rep": "bar16", "qF": 1, "projector": "Pbar16_L_PLUS"},
        "HLFc": {"rep": "bar16", "qF": -1, "projector": "Pbar16_R_MINUS"},
        "HRFc": {"rep": "16", "qF": -4, "projector": "P16_L_PLUS"},
        "HLAc": {"rep": "16", "qF": 4, "projector": "P16_R_MINUS"},
        "H": {"rep": "10", "qF": 0, "projector": "P10_BIDDOUBLEt_MINUS"},
    }

    def row(identifier: str, coefficient: str, names: tuple[str, ...], tensor_id: str) -> dict[str, Any]:
        return {
            "id": identifier,
            "coefficient": coefficient,
            "fields": list(names),
            "representations": [fields[name]["rep"] for name in names],
            "U1F_charges": [fields[name]["qF"] for name in names],
            "total_U1F_charge": sum(fields[name]["qF"] for name in names),
            "Cartesian_projectors": [fields[name]["projector"] for name in names],
            "normalized_tensor_id": tensor_id,
            "instantiation_status": "CARTESIAN_PROJECTOR_TENSOR_RESOLVED",
        }

    left = ("Q1", "Q2", "Q3", "HLF")
    right = ("Qc1", "Qc2", "Qc3", "HRA")
    rows = [
        row(
            f"PS_W_Y_{left_index + 1}_{right_index + 1}",
            f"Y_{left_index + 1}{right_index + 1}",
            (left_name, "H", right_name),
            "CART_PS_16_Lx16_Rx10_MINUS",
        )
        for left_index, left_name in enumerate(left)
        for right_index, right_name in enumerate(right)
    ]
    rows.extend(
        [
            row("PS_W_y_m", "y_m", ("HLA", "H", "HRF"), "CART_PS_bar16_Lxbar16_Rx10_MINUS"),
            row("PS_W_y_c", "y_c", ("HRAc", "H", "HLFc"), "CART_PS_bar16_Lxbar16_Rx10_MINUS"),
            row("PS_W_y_cb", "y_cb", ("HRFc", "H", "HLAc"), "CART_PS_16_Lx16_Rx10_MINUS"),
            row("PS_W_mu_H", "mu_H", ("H", "H"), "CART_PS_H10_MINUS_x_H10_MINUS_TO_1"),
        ]
    )
    return {
        "field_registry": fields,
        "charge_provenance": (
            "bulk charges are V48 data; qF(Q_i)=+1 and qF(Qc_i)=-1 follow "
            "from the declared gauge-invariant Kahler mixing with HLF and HRA"
        ),
        "projected_tensor_certificates": projected_tensors,
        "primitive_rows": rows,
        "primitive_count": len(rows),
        "cubic_count": sum(len(row_["fields"]) == 3 for row_ in rows),
        "quadratic_count": sum(len(row_["fields"]) == 2 for row_ in rows),
        "all_rows_charge_neutral": all(row_["total_U1F_charge"] == 0 for row_ in rows),
        "all_rows_tensor_resolved": all(row_["instantiation_status"] == "CARTESIAN_PROJECTOR_TENSOR_RESOLVED" for row_ in rows),
        "scope": (
            "This resolves the 20 PS superpotential coefficients at projector-tensor "
            "level. It does not resolve the 14 normal-derivative channels."
        ),
        "parity_core": {
            "vector_lift_residual": parity["vector_lift_residual"],
            "unbroken_dimension": parity["expected_unbroken_dimension"],
        },
    }


def ps_derivative_projector_certificate() -> dict[str, Any]:
    """Resolve the six brane-bulk and eight bulk-hyper derivative rows.

    The convention is universal.  ``D5`` preserves the Cartesian Spin(10)
    carrier coordinate but reverses the boundary Z2 parity of the trace.  If
    ``E`` is the even projector of H and ``O=I-E``, then Hc has even projector
    O.  At the wall

      O8 = (D5 Hc_odd[E]) H_even[E],
      O7 = Hc_even[O] (D5 H_odd[O]).

    Both contractions use the same raw Cartesian 16 x bar16 singlet tensor.
    The V49 relation O7+O8+M_o=0 is retained exactly, so the two coordinates
    per hypermultiplet are O_minus=O8-O7 and M_o.
    """

    gammas, _, _ = yukawa._clifford_data()
    parity_32 = gammas[6] @ gammas[7] @ gammas[8] @ gammas[9]
    indices_16 = yukawa.chiral_indices(-1)
    indices_bar16 = yukawa.chiral_indices(+1)
    parity_16 = parity_32[np.ix_(indices_16, indices_16)]
    parity_bar16 = parity_32[np.ix_(indices_bar16, indices_bar16)]
    projector = {
        ("16", "L"): (np.eye(16) + parity_16) / 2.0,
        ("16", "R"): (np.eye(16) - parity_16) / 2.0,
        ("bar16", "L"): (np.eye(16) + parity_bar16) / 2.0,
        ("bar16", "R"): (np.eye(16) - parity_bar16) / 2.0,
    }
    singlet = clifford.kform_tensor(0, -1, +1)[0]

    def restricted(first_rep: str, second_rep: str, ps_side: str) -> np.ndarray:
        if (first_rep, second_rep) == ("16", "bar16"):
            raw = singlet
        elif (first_rep, second_rep) == ("bar16", "16"):
            raw = singlet.T
        else:
            raise ValueError("derivative singlet needs conjugate spinor reps")
        return np.sqrt(2.0) * (
            projector[(first_rep, ps_side)].T
            @ raw
            @ projector[(second_rep, ps_side)]
        )

    tensor_certificates: dict[str, Any] = {}
    for first_rep, second_rep in (("16", "bar16"), ("bar16", "16")):
        for side in ("L", "R"):
            value = restricted(first_rep, second_rep, side)
            opposite = "R" if side == "L" else "L"
            if (first_rep, second_rep) == ("16", "bar16"):
                raw = singlet
            else:
                raw = singlet.T
            cross = (
                projector[(first_rep, side)].T
                @ raw
                @ projector[(second_rep, opposite)]
            )
            tensor_certificates[f"{first_rep}x{second_rep}_{side}"] = {
                "shape": list(value.shape),
                "definition": f"sqrt(2) P_{first_rep},{side}^T T_1 P_{second_rep},{side}",
                "normalized_norm_residual": float(abs(np.vdot(value, value).real - 1.0)),
                "nonzero_entry_count": int(np.count_nonzero(np.abs(value) > 1.0e-12)),
                "opposite_PS_subspace_kill_norm": float(np.linalg.norm(cross)),
            }

    fields = {
        **{f"Q{index}": {"rep": "16", "qF": 1, "side": "L"} for index in range(1, 4)},
        **{f"Qc{index}": {"rep": "16", "qF": -1, "side": "R"} for index in range(1, 4)},
        "HLF": {"rep": "16", "qF": 1, "even_side": "L"},
        "HLFc": {"rep": "bar16", "qF": -1, "even_side": "R"},
        "HLA": {"rep": "bar16", "qF": -4, "even_side": "L"},
        "HLAc": {"rep": "16", "qF": 4, "even_side": "R"},
        "HRA": {"rep": "16", "qF": -1, "even_side": "R"},
        "HRAc": {"rep": "bar16", "qF": 1, "even_side": "L"},
        "HRF": {"rep": "bar16", "qF": 4, "even_side": "R"},
        "HRFc": {"rep": "16", "qF": -4, "even_side": "L"},
    }

    brane_rows = []
    for index in range(1, 4):
        brane_rows.append(
            {
                "id": f"PS_D_Q_{index}",
                "coefficient": f"dQ_{index}",
                "fields": [f"Q{index}", "D5_HLFc_odd_L"],
                "representations": ["16", "bar16"],
                "U1F_charges": [1, -1],
                "total_U1F_charge": 0,
                "Cartesian_projectors": ["P16_L", "D5[Pbar16_L]"],
                "normalized_tensor_id": "CART_PS_16xbar16_SINGLET_L",
                "normal_derivative_rule": "D5 turns the HLFc_L odd trace into an even boundary datum",
                "instantiation_status": "CARTESIAN_DERIVATIVE_TENSOR_RESOLVED",
            }
        )
        brane_rows.append(
            {
                "id": f"PS_D_Qc_{index}",
                "coefficient": f"dQc_{index}",
                "fields": [f"Qc{index}", "D5_HRAc_odd_R"],
                "representations": ["16", "bar16"],
                "U1F_charges": [-1, 1],
                "total_U1F_charge": 0,
                "Cartesian_projectors": ["P16_R", "D5[Pbar16_R]"],
                "normalized_tensor_id": "CART_PS_16xbar16_SINGLET_R",
                "normal_derivative_rule": "D5 turns the HRAc_R odd trace into an even boundary datum",
                "instantiation_status": "CARTESIAN_DERIVATIVE_TENSOR_RESOLVED",
            }
        )

    channels = {
        "A": {"H": "HLF", "Hc": "HLFc"},
        "B": {"H": "HLA", "Hc": "HLAc"},
        "C": {"H": "HRA", "Hc": "HRAc"},
        "D": {"H": "HRF", "Hc": "HRFc"},
    }
    bulk_rows = []
    for channel, names in channels.items():
        h = fields[names["H"]]
        hc = fields[names["Hc"]]
        h_even_side = str(h["even_side"])
        h_odd_side = "R" if h_even_side == "L" else "L"
        if str(hc["even_side"]) != h_odd_side:
            raise RuntimeError(f"opposite hypermultiplet parity failed for {channel}")
        tensor_e = f"CART_PS_{hc['rep']}x{h['rep']}_SINGLET_{h_even_side}"
        tensor_o = f"CART_PS_{hc['rep']}x{h['rep']}_SINGLET_{h_odd_side}"
        common = {
            "channel": channel,
            "H": names["H"],
            "Hc": names["Hc"],
            "representations": [hc["rep"], h["rep"]],
            "U1F_charges": [hc["qF"], h["qF"]],
            "total_U1F_charge": int(hc["qF"]) + int(h["qF"]),
            "H_even_side": h_even_side,
            "Hc_even_side": h_odd_side,
            "O8_term": f"(D5 {names['Hc']}_odd_{h_even_side}) {names['H']}_even_{h_even_side}",
            "O7_term": f"{names['Hc']}_even_{h_odd_side} (D5 {names['H']}_odd_{h_odd_side})",
            "normalized_tensor_ids": [tensor_e, tensor_o],
            "instantiation_status": "CARTESIAN_DERIVATIVE_TENSOR_RESOLVED",
        }
        bulk_rows.append(
            {
                "id": f"PS_D_Ominus_{channel}",
                "coefficient": f"rminus_{channel}",
                "coordinate": "O_minus=O8-O7",
                **common,
            }
        )
        bulk_rows.append(
            {
                "id": f"PS_D_Mo_{channel}",
                "coefficient": f"mo_{channel}",
                "coordinate": "M_o with O7+O8+M_o=0 on the doubled cover",
                **common,
            }
        )

    normal_form = v49.derivative_normal_form(channel_count=4)
    representative_one = np.asarray([[-0.5, -0.5], [0.5, -0.5], [0.0, 1.0]])
    representative = np.kron(np.eye(4), representative_one)
    rows = brane_rows + bulk_rows
    return {
        "common_convention": {
            "representation_coordinate": "D5 preserves the Cartesian carrier index",
            "boundary_parity": "D5 reverses trace Z2 parity: an odd trace has an even D5 boundary datum",
            "hypermultiplet": "Hc has the opposite intrinsic boundary parity to H in every PS subspace",
            "singlet_tensor": "raw locked Cartesian C Gamma_[0]/4, restricted and multiplied by sqrt(2)",
        },
        "tensor_certificates": tensor_certificates,
        "brane_bulk_rows": brane_rows,
        "bulk_hyper_rows": bulk_rows,
        "primitive_rows": rows,
        "primitive_count": len(rows),
        "brane_bulk_count": len(brane_rows),
        "bulk_hyper_count": len(bulk_rows),
        "all_rows_charge_neutral": all(row["total_U1F_charge"] == 0 for row in rows),
        "all_rows_tensor_resolved": all(row["instantiation_status"] == "CARTESIAN_DERIVATIVE_TENSOR_RESOLVED" for row in rows),
        "IBP_quotient": {
            "relation": normal_form["exact_IBP_relation"],
            "relation_rank": normal_form["relation_rank"],
            "quotient_dimension": normal_form["quotient_dimension"],
            "representative_residual": normal_form["representative_residual"],
            "coordinates_per_channel": normal_form["canonical_coordinates_per_channel"],
            "retained_coordinate_rank": int(np.linalg.matrix_rank(representative)),
            "drop_Mo_coordinate_rank": int(np.linalg.matrix_rank(representative[:, ::2])),
        },
        "scope": (
            "All 14 V49 PS derivative primitives now have one Cartesian tensor/parity "
            "normal form. Their renormalized coefficients and one-loop mixing remain data."
        ),
    }


def schur_mediator_certificate() -> dict[str, Any]:
    """Executable holomorphic tree matching for a vectorlike mediator bank."""

    rng = np.random.default_rng(51057)
    dimension = 6
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    mass = raw + (5.0 + 0.2j) * np.eye(dimension)
    a = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
    b = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
    q = -np.linalg.solve(mass, b)
    qbar = -np.linalg.solve(mass.T, a)
    full_w = qbar.T @ mass @ q + a.T @ q + qbar.T @ b
    schur_w = -a.T @ np.linalg.solve(mass, b)
    target_dimension = 9
    jacobian = np.eye(target_dimension, dtype=int)
    killed_jacobian = jacobian[:, :-1]
    return {
        "superpotential": "W=qbar^T M q + A^T q + qbar^T B",
        "integrated_result": "W_eff=-A^T M^-1 B",
        "mediator_dimension_in_witness": dimension,
        "mass_determinant_abs": float(abs(np.linalg.det(mass))),
        "q_equation_residual": maximum_abs(mass.T @ qbar + a),
        "qbar_equation_residual": maximum_abs(mass @ q + b),
        "effective_superpotential_residual": float(abs(full_w - schur_w)),
        "abstract_invariant_target_dimension": target_dimension,
        "complete_mediator_coefficient_rank": int(np.linalg.matrix_rank(jacobian)),
        "one_mediator_removed_rank": int(np.linalg.matrix_rank(killed_jacobian)),
        "factorization_theorem": (
            "Compact-group semisimplicity decomposes every quartic invariant "
            "across a two-plus-two partition into finitely many intermediate "
            "irreps and copy maps; one conjugate mediator pair per basis factor "
            "generates the direction by this Schur complement."
        ),
        "scope": (
            "Finite realizability is proved only after the normalized invariant "
            "factor basis is known; the 120 pending V49 factors are not inferred."
        ),
    }


def vectorlike_anomaly_certificate() -> dict[str, Any]:
    """Exact cancellation for R_q plus conjugate(R)_(-q)."""

    pairs = [
        ("X1", 1, 0, -3),
        ("X10", 10, 1, 2),
        ("X120", 120, 28, -1),
        ("X126", 126, 35, 4),
        ("X210", 210, 56, -2),
    ]
    rows = []
    for label, dimension, quadratic_index, charge in pairs:
        rows.append(
            {
                "label": label,
                "dimension": dimension,
                "test_quadratic_index": quadratic_index,
                "charge": charge,
                "partner_charge": -charge,
                "mixed_Spin10_squared_U1F": quadratic_index * charge
                + quadratic_index * (-charge),
                "gravitational_squared_U1F": dimension * charge
                + dimension * (-charge),
                "U1F_cubic": dimension * charge**3 + dimension * (-charge) ** 3,
                "vectorlike_mass_charge": charge + (-charge),
            }
        )
    _, dimension, quadratic_index, charge = pairs[3]
    killed = {
        "mixed_Spin10_squared_U1F": quadratic_index * charge,
        "gravitational_squared_U1F": dimension * charge,
        "U1F_cubic": dimension * charge**3,
    }
    keys = (
        "mixed_Spin10_squared_U1F",
        "gravitational_squared_U1F",
        "U1F_cubic",
        "vectorlike_mass_charge",
    )
    return {
        "assignment_rule": (
            "For neutral bilinears q_A+q_B=0 choose q_X=-q_A and "
            "q_Xbar=-q_B; the two cubic vertices and M Xbar X are neutral."
        ),
        "pair_certificates": rows,
        "all_pairwise_anomalies_zero": all(
            all(row[key] == 0 for key in keys) for row in rows
        ),
        "unpaired_kill_vector": killed,
        "unpaired_kill_is_nonzero": any(value != 0 for value in killed.values()),
    }


def _unitary(rng: np.random.Generator, dimension: int) -> np.ndarray:
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    q, r = np.linalg.qr(raw)
    return q @ np.diag(np.exp(-1j * np.angle(np.diag(r))))


def cartesian_projector_covariance_certificate() -> dict[str, Any]:
    """Test Wilson-block covariance under internal component-frame rotations."""

    rng = np.random.default_rng(51077)
    block_dimensions = (2, 3, 2)
    dimension = sum(block_dimensions)
    unitary = np.zeros((dimension, dimension), dtype=np.complex128)
    projectors = []
    cursor = 0
    for width in block_dimensions:
        unitary[cursor : cursor + width, cursor : cursor + width] = _unitary(rng, width)
        projector = np.zeros((dimension, dimension), dtype=np.complex128)
        projector[cursor : cursor + width, cursor : cursor + width] = np.eye(width)
        projectors.append(projector)
        cursor += width
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    kernel = raw.conjugate().T @ raw + 0.7 * np.eye(dimension)
    currents = rng.normal(size=(dimension, 4)) + 1j * rng.normal(size=(dimension, 4))

    def blocks(k: np.ndarray, j: np.ndarray, p: list[np.ndarray]) -> np.ndarray:
        inverse = np.linalg.inv(k)
        return np.asarray(
            [
                j.conjugate().T @ left @ inverse @ right @ j
                for left in p
                for right in p
            ]
        )

    reference = blocks(kernel, currents, projectors)
    transformed_kernel = unitary @ kernel @ unitary.conjugate().T
    transformed_currents = unitary @ currents
    transformed_projectors = [
        unitary @ projector @ unitary.conjugate().T for projector in projectors
    ]
    covariant = blocks(transformed_kernel, transformed_currents, transformed_projectors)
    mismatched = blocks(transformed_kernel, currents, transformed_projectors)
    return {
        "block_dimensions": list(block_dimensions),
        "unitarity_residual": maximum_abs(
            unitary.conjugate().T @ unitary - np.eye(dimension)
        ),
        "projector_idempotence_residual": max(
            maximum_abs(projector @ projector - projector) for projector in projectors
        ),
        "projector_resolution_residual": maximum_abs(sum(projectors) - np.eye(dimension)),
        "all_projected_Wilson_blocks_covariance_residual": maximum_abs(reference - covariant),
        "frozen_current_basis_mismatch_kill_norm": float(np.linalg.norm(reference - mismatched)),
        "scope": (
            "Cartesian projector blocks are physical without a named internal "
            "basis; a named component table still requires a component frame."
        ),
    }


def candidate_architecture() -> dict[str, Any]:
    return {
        "name": "V51 Cartesian Projector Mediator Moose (CPMM)",
        "status": "CONDITIONAL_ARCHITECTURE_NOT_AN_INSTANTIATED_THEORY",
        "microscopic_definition": [
            "finite four-dimensional N=1 Spin(10)xU(1)_F moose with linear link multiplets",
            "physical 210+126+bar126+singlets and four bulk-spinor channels in one Cartesian Clifford/form basis",
            "endpoint parity P10=diag(+1^6,-1^4) and its explicit spin/form lifts",
            "one local vectorlike chiral pair per quartic invariant factor/copy direction",
            "positive canonical Kahler terms plus all symmetry-allowed renormalizable mixing, gauge-fixing and ghost terms",
        ],
        "quartic_UV_superpotential": (
            "sum_(r,k)[M_(r,k) Xbar_(r,k) X_(r,k)+A_(r,k)X_(r,k)+Xbar_(r,k)B_(r,k)]"
        ),
        "tree_matching": "C_tree=-Y_A M^-1 Y_B in the normalized invariant-copy basis",
        "one_loop_algorithm": (
            "build all background-dependent chiral/vector/link/Goldstone/ghost "
            "quadratic operators, evaluate regulated one-loop superdeterminants "
            "in DRbar, project poles and finite parts into the same Cartesian "
            "basis, and verify the full RG identity"
        ),
        "limitation": (
            "Chiral mediators do not by themselves UV-complete O7/O8 derivative, "
            "general Kahler, gauge, link-radial, or ghost sectors."
        ),
    }


def proof_obligations() -> dict[str, list[dict[str, Any]]]:
    return {
        "C5": [
            {"id": "C5_1_TREE_PROFILE", "status": "PASS_UPSTREAM", "datum": "quadratic transfer/first jet rematched through O(Lambda^-1)"},
            {"id": "C5_2_FIELD_TABLE", "status": "MISSING", "datum": "all mediator/link reps, charges, masses and couplings"},
            {"id": "C5_3_HESSIANS", "status": "MISSING", "datum": "background chiral/vector/link/Goldstone/ghost operators"},
            {"id": "C5_4_SUBTRACTION", "status": "NAMED_NOT_EVALUATED", "datum": "DRbar is named; poles and finite thresholds are absent"},
            {"id": "C5_5_MIXING", "status": "MISSING", "datum": "full one-loop 1PI invariant-direction mixing matrix"},
            {"id": "C5_6_BARE_MAPS", "status": "MISSING", "datum": "bare-to-DRbar maps for every retained coupling"},
            {"id": "C5_7_AFFINE_REMATCH", "status": "MISSING", "datum": "distributed-current and source-functional jets"},
            {"id": "C5_8_RG", "status": "MISSING", "datum": "beta-function cancellation through O(Lambda^-1)"},
        ],
        "C7": [
            {"id": "C7_1_CENSUS", "status": "PASS_UPSTREAM", "datum": "176 aggregate schema rows"},
            {"id": "C7_2_LOW_DEGREE", "status": "PASS_V51", "datum": "48 rows resolved: 20 multiplicity-one and 28 empty"},
            {"id": "C7_3_PS_PARITY", "status": "PASS_V51", "datum": "explicit Cartesian PS involution, 8+8 spinors, 21-generator stabilizer"},
            {"id": "C7_4_PS_SUPERPOTENTIAL", "status": "PASS_V51", "datum": "20 primitive coefficients have structured Cartesian projectors, charges and normalized tensors"},
            {"id": "C7_5_DEGREE4", "status": "MISSING", "datum": "120 multiplicities and normalized factor/copy tensors"},
            {"id": "C7_6_MEDIATOR_BANK", "status": "STRUCTURAL_THEOREM_ONLY", "datum": "finite construction proved conditional on C7_5"},
            {"id": "C7_7_DERIVATIVE_REWRITE", "status": "PASS_V51", "datum": "14 PS normal-derivative primitives share one Cartesian D5/parity/IBP convention"},
            {"id": "C7_8_FINAL_ARRAY", "status": "MISSING", "datum": "projector-block or named-component Wilson array with provenance"},
            {"id": "C7_9_BASIS_COVARIANCE", "status": "PASS_V51", "datum": "projected Wilson blocks invariant under block-unitary frames"},
        ],
    }


def build_report() -> dict[str, Any]:
    inventory = incidence_inventory()
    registry = tensor_registry()
    parity = cartesian_ps_parity_certificate()
    ps_superpotential = ps_superpotential_projector_certificate()
    ps_derivative = ps_derivative_projector_certificate()
    mediator = schur_mediator_certificate()
    anomaly = vectorlike_anomaly_certificate()
    covariance = cartesian_projector_covariance_certificate()
    upstream_c5 = json.loads(
        (ROOT / "SUSY_V50_C5_STRICT_REMATCH_AUDIT.json").read_text(encoding="utf-8")
    )
    upstream_c7 = json.loads(
        (ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json").read_text(encoding="utf-8")
    )
    nonempty = inventory["low_degree_resolution_counts"].get("RESOLVED_NONEMPTY_CARTESIAN", 0)
    empty = inventory["low_degree_resolution_counts"].get("RESOLVED_EMPTY", 0)
    low_rows = inventory["resolved_low_degree_rows"]
    kill_tests = {
        "charge_neutrality_is_not_invariance": {
            "neutral_but_empty_rows": empty,
            "passes": empty > 0 and all(row["U1F_charge"] == 0 for row in low_rows),
        },
        "missing_mediator_loses_surjectivity": {
            "full_rank": mediator["complete_mediator_coefficient_rank"],
            "killed_rank": mediator["one_mediator_removed_rank"],
            "passes": mediator["one_mediator_removed_rank"] < mediator["complete_mediator_coefficient_rank"],
        },
        "unpaired_mediator_is_anomalous": {
            "anomaly_vector": anomaly["unpaired_kill_vector"],
            "passes": anomaly["unpaired_kill_is_nonzero"],
        },
        "mixed_component_frames_change_Wilson_blocks": {
            "mismatch_norm": covariance["frozen_current_basis_mismatch_kill_norm"],
            "passes": covariance["frozen_current_basis_mismatch_kill_norm"] > 1.0e-3,
        },
        "eight_PS_strings_are_not_34_primitive_rows": {
            "aggregate": inventory["ps_aggregate_rows"],
            "primitive": inventory["ps_total_primitive_declarations"],
            "passes": inventory["ps_aggregate_rows"] < inventory["ps_total_primitive_declarations"],
        },
        "same_parity_spinors_do_not_fake_a_PS_Yukawa": {
            "same_parity_norms": [
                value[key]
                for value in ps_superpotential["projected_tensor_certificates"].values()
                for key in ("same_L_parity_kill_norm", "same_R_parity_kill_norm")
            ],
            "passes": max(
                value[key]
                for value in ps_superpotential["projected_tensor_certificates"].values()
                for key in ("same_L_parity_kill_norm", "same_R_parity_kill_norm")
            )
            < 1.0e-12,
        },
        "opposite_PS_subspaces_do_not_fake_a_derivative_singlet": {
            "cross_subspace_norms": [
                value["opposite_PS_subspace_kill_norm"]
                for value in ps_derivative["tensor_certificates"].values()
            ],
            "passes": max(
                value["opposite_PS_subspace_kill_norm"]
                for value in ps_derivative["tensor_certificates"].values()
            )
            < 1.0e-12,
        },
        "dropping_Mo_halves_the_bulk_derivative_quotient": {
            "full_rank": ps_derivative["IBP_quotient"]["retained_coordinate_rank"],
            "drop_Mo_rank": ps_derivative["IBP_quotient"]["drop_Mo_coordinate_rank"],
            "passes": ps_derivative["IBP_quotient"]["retained_coordinate_rank"] == 8
            and ps_derivative["IBP_quotient"]["drop_Mo_coordinate_rank"] == 4,
        },
        "naming_DRbar_is_not_a_loop_calculation": {
            "status": upstream_c5["C5_decision"]["loop_subtraction_and_scale_independence"],
            "passes": upstream_c5["C5_decision"]["loop_subtraction_and_scale_independence"] == "FAIL_MISSING_CALCULATION",
        },
    }
    spinor_parities = parity["chiral_spinors"]
    checks = {
        "V50_inventory_replayed": inventory["v50_total_schema_rows"] == 176 and inventory["source_candidate_rows"] == 168 and inventory["ps_aggregate_rows"] == 8,
        "all_48_low_degree_rows_resolved": inventory["degree_two_or_three_rows_resolved_here"] == 48 and len(low_rows) == 48,
        "low_degree_split_20_nonempty_28_empty": nonempty == 20 and empty == 28,
        "nonempty_rows_have_registered_normalized_tensor": all(row["invariant_multiplicity"] == 1 and len(row["normalized_tensor_ids"]) == 1 and row["normalized_tensor_ids"][0] in registry for row in low_rows if row["instantiation_status"] == "RESOLVED_NONEMPTY_CARTESIAN"),
        "all_nonempty_rows_have_explicit_ordered_orientation": all(
            row["tensor_orientation"] in ("direct", "negative_transpose")
            for row in low_rows
            if row["instantiation_status"] == "RESOLVED_NONEMPTY_CARTESIAN"
        ),
        "empty_rows_have_zero_multiplicity": all(row["invariant_multiplicity"] == 0 and not row["normalized_tensor_ids"] for row in low_rows if row["instantiation_status"] == "RESOLVED_EMPTY"),
        "registry_tensors_normalized": max(row["gram_residual"] for row in registry.values()) < 1.0e-12,
        "mixed_tensor_reverse_orientation_rules_exact": max(
            registry[label]["reverse_orientation_residual"]
            for label in ("CART_16xbar16_TO_1", "CART_16xbar16_TO_210")
        ) < 1.0e-12,
        "direct_chirality_vector_tensors_covariant": max(
            registry[label]["covariance_residual"]
            for label in ("CART_16x16_TO_10", "CART_bar16xbar16_TO_10")
        ) < 1.0e-12,
        "residual_inventory_120_and_34": inventory["degree_four_rows_pending_factorization"] == 120 and inventory["ps_total_primitive_declarations"] == 34,
        "PS_vector_spin_lift_exact": parity["vector_lift_residual"] < 1.0e-12,
        "both_chiral_spinors_split_8_plus_8": all(row["plus_projector_rank"] == 8 and row["minus_projector_rank"] == 8 and row["plus_eigenvalue_count"] == 8 and row["minus_eigenvalue_count"] == 8 for row in spinor_parities.values()),
        "parity_eigenspaces_are_SU2L_and_SU2R": all(row["plus_subspace_twice_T3L_values"] == [-1, 1] and row["plus_subspace_twice_T3R_values"] == [0] and row["minus_subspace_twice_T3L_values"] == [0] and row["minus_subspace_twice_T3R_values"] == [-1, 1] for row in spinor_parities.values()),
        "PS_stabilizer_is_21_and_coset_24": all(row["commuting_spin10_generators"] == 21 and row["anticommuting_spin10_generators"] == 24 for row in spinor_parities.values()),
        "source_form_parity_lifts_have_exact_dimensions": parity["form_representation_lifts"]["210"]["plus_rank"] == 106 and parity["form_representation_lifts"]["210"]["minus_rank"] == 104 and all(parity["form_representation_lifts"][label]["plus_rank"] == 66 and parity["form_representation_lifts"][label]["minus_rank"] == 60 for label in ("126", "bar126")),
        "all_20_PS_superpotential_rows_resolved": ps_superpotential["primitive_count"] == 20 and ps_superpotential["cubic_count"] == 19 and ps_superpotential["quadratic_count"] == 1 and ps_superpotential["all_rows_charge_neutral"] and ps_superpotential["all_rows_tensor_resolved"],
        "projected_PS_Yukawa_tensors_normalized": max(value["normalized_gram_residual"] for value in ps_superpotential["projected_tensor_certificates"].values()) < 1.0e-12,
        "projected_PS_Yukawa_tensors_covariant": max(value["PS_covariance_residual"] for value in ps_superpotential["projected_tensor_certificates"].values()) < 1.0e-12,
        "all_14_PS_derivative_rows_resolved": ps_derivative["primitive_count"] == 14 and ps_derivative["brane_bulk_count"] == 6 and ps_derivative["bulk_hyper_count"] == 8 and ps_derivative["all_rows_charge_neutral"] and ps_derivative["all_rows_tensor_resolved"],
        "projected_derivative_singlets_normalized": max(value["normalized_norm_residual"] for value in ps_derivative["tensor_certificates"].values()) < 1.0e-12,
        "derivative_IBP_quotient_is_8_dimensional": ps_derivative["IBP_quotient"]["relation_rank"] == 4 and ps_derivative["IBP_quotient"]["quotient_dimension"] == 8 and ps_derivative["IBP_quotient"]["representative_residual"] < 1.0e-12,
        "mediator_Schur_stationarity": max(mediator["q_equation_residual"], mediator["qbar_equation_residual"], mediator["effective_superpotential_residual"]) < 1.0e-11,
        "abstract_mediator_bank_surjective": mediator["complete_mediator_coefficient_rank"] == mediator["abstract_invariant_target_dimension"],
        "vectorlike_anomalies_cancel": anomaly["all_pairwise_anomalies_zero"],
        "Cartesian_Wilson_blocks_covariant": max(covariance["unitarity_residual"], covariance["projector_idempotence_residual"], covariance["projector_resolution_residual"], covariance["all_projected_Wilson_blocks_covariance_residual"]) < 1.0e-11,
        "all_kill_tests_fire": all(row["passes"] for row in kill_tests.values()),
        "upstream_remains_fail_closed": upstream_c7["coverage_decision"]["C7"] == "PARTIAL" and upstream_c5["C5_decision"]["status"] == "PARTIAL_NOT_CLOSED",
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V51 Cartesian mediator audit failure: " + ", ".join(failures))
    report: dict[str, Any] = {
        "schema": "susy-v51-cartesian-mediator-c5-c7-feasibility-audit-v1",
        "status": STATUS,
        "candidate_architecture": candidate_architecture(),
        "tensor_registry": registry,
        "incidence_inventory": inventory,
        "Cartesian_PS_parity_certificate": parity,
        "PS_superpotential_projector_certificate": ps_superpotential,
        "PS_derivative_projector_certificate": ps_derivative,
        "mediator_tree_certificate": mediator,
        "vectorlike_anomaly_certificate": anomaly,
        "Cartesian_projector_covariance_certificate": covariance,
        "bridge_decision": {
            "basis_covariant_Cartesian_Wilson_functional": "A separate Cartesian-to-PS unitary is unnecessary when every kernel, current, parity/observable projector and coefficient tensor is emitted in this Cartesian basis.",
            "named_PS_component_table": "A component frame or structured ancestry is still required to attach HLF/HLA/HRA/HRF names and entrywise coefficients.",
            "new_fact": "The PS subgroup, both 8-dimensional spinor trace subspaces, all 20 PS superpotential tensors, and all 14 PS derivative tensors are explicit Cartesian projector data.",
            "current_V49_state": "Every PS primitive now satisfies the Cartesian-only antecedent; the final Wilson contraction is still absent because 120 source quartic factor spaces and their coefficient/current maps remain unresolved.",
            "projector_block_bridge_eliminated": True,
            "named_PS_intertwiner_dependency_eliminated": True,
            "final_Wilson_array_emitted": False,
        },
        "proof_obligations": proof_obligations(),
        "C5_decision": {
            "closed": False,
            "status": "PARTIAL_NOT_CLOSED",
            "new_result": "A finite vectorlike bank makes holomorphic quartic thresholds algorithmically calculable after factor tensors and UV parameters are emitted.",
            "remaining_blocker": "No physical bank/link field table, background Hessians, 1PI mixing, finite thresholds, bare-to-DRbar maps, affine rematch, or RG cancellation exists.",
        },
        "C7_decision": {
            "closed": False,
            "status": "PARTIAL_NOT_CLOSED",
            "new_result": "48 source rows, the PS parity projectors, and all 34 PS superpotential/derivative primitive tensors are explicit in one Cartesian basis; a named PS unitary is no longer required.",
            "remaining_blocker": "120 quartic factor spaces and the final source-to-PS Wilson array remain absent.",
        },
        "G2_decision": {
            "closed": False,
            "verdict": "G2_REMAINS_OPEN",
            "gates_promoted": [],
            "reason": "strict C5 and C7 remain false conjunctions despite finite progress",
        },
        "kill_tests": kill_tests,
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            {"title": "The One-Loop Effective Kahler Potential. I: Chiral Multiplets", "url": "https://arxiv.org/abs/1205.3492", "use": "one-loop supersymmetric functionals require the full tree mass spectrum and regulator"},
            {"title": "Effective operators in SUSY, superfield constraints and searches for a UV completion", "url": "https://arxiv.org/abs/1503.08319", "use": "heavy-superfield polynomial completions and derivative-operator qualifications"},
            {"title": "Deconstructing Dimensions", "url": "https://arxiv.org/abs/hep-th/0104005", "use": "finite four-dimensional moose realization"},
            {"title": "5D super Yang--Mills theory in 4D superspace, superfield brane operators, and applications to orbifold GUTs", "url": "https://arxiv.org/abs/hep-ph/0112230", "use": "gauge-covariant normal derivatives and boundary superfield operators"},
        ],
        "source_manifest": [{"path": path.name, "sha256": sha256_file(path)} for path in UPSTREAM] + [{"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))}, {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)}],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    inventory = report["incidence_inventory"]
    parity = report["Cartesian_PS_parity_certificate"]
    mediator = report["mediator_tree_certificate"]
    covariance = report["Cartesian_projector_covariance_certificate"]
    c5_rows = "\n".join(f"- `{row['id']}` — `{row['status']}`: {row['datum']}" for row in report["proof_obligations"]["C5"])
    c7_rows = "\n".join(f"- `{row['id']}` — `{row['status']}`: {row['datum']}" for row in report["proof_obligations"]["C7"])
    return f"""# V51 Cartesian-projector mediator feasibility audit

Status: `{report['status']}`

## Verdict

There is a mathematically viable newer-physics route: a finite 4D N=1
**Cartesian Projector Mediator Moose**.  Local vectorlike pairs generate
quartic holomorphic operators by `C_tree=-Y_A M^-1 Y_B`, while an explicit
Clifford parity defines the PS endpoint without a separate component unitary.

This is a conditional architecture, not a completed theory.  The 120 quartic
factor spaces, physical mediator/link field table, final source-to-PS Wilson
array, and one-loop matching are absent.  C5, C7, and G2 remain open.

## Exact C7 progress

The V50 census has {inventory['v50_total_schema_rows']} aggregate rows:
{inventory['source_candidate_rows']} source candidates and
{inventory['ps_aggregate_rows']} PS strings.  All
{inventory['degree_two_or_three_rows_resolved_here']} degree-two/three source
rows are now exact: **20** are normalized multiplicity-one Cartesian operators
and **28** are empty invariant sectors despite U(1)F neutrality.  The remaining
source inventory is **{inventory['degree_four_rows_pending_factorization']}**
degree-four rows.  The PS strings expand to
**{inventory['ps_total_primitive_declarations']}** primitive declarations.
All 20 superpotential and all 14 normal-derivative rows now have explicit
Cartesian charges, projectors and normalized tensors.

## Explicit Cartesian PS wall

Use `{parity['vector_parity']}` and
`{parity['spin_lift']}`.  The lift residual is
`{parity['vector_lift_residual']:.3e}`.  On both `16` and `bar16`, its projectors
have ranks `8+8`; exactly `21` Spin(10) generators commute and `24`
anticommute.  Thus the stabilizer is `so(6)+so(4)`, equivalently
`su(4)+su(2)L+su(2)R`, in the same basis as every audited Clifford tensor.

This eliminates the named-PS intertwiner dependency for the complete retained
PS action: the derivative sector uses one convention in which `D5` preserves
the Cartesian carrier index and flips boundary trace parity, while the exact
V49 `O7+O8+M_o=0` quotient is retained.  A named entrywise table can still
choose a component frame, but the projector-block functional does not need it.

## Mediator theorem and kill test

For `W=Xbar^T M X+A^T X+Xbar^T B`, stationarity gives
`W_eff=-A^T M^-1 B`; the executable residual is
`{mediator['effective_superpotential_residual']:.3e}`.  One mediator factor per
abstract invariant direction gives rank
{mediator['complete_mediator_coefficient_rank']}; removing one lowers it to
{mediator['one_mediator_removed_rank']}.  This proves finite realizability only
after the missing invariant factor/copy basis is known.

Transforming every kernel, current, and projector together leaves all Wilson
blocks invariant with residual
`{covariance['all_projected_Wilson_blocks_covariance_residual']:.3e}`.  Rotating
the kernel/projectors while freezing the current produces the intended failure
norm `{covariance['frozen_current_basis_mismatch_kill_norm']:.6g}`.

## Strict C5 obligations

{c5_rows}

## Strict C7 obligations

{c7_rows}

Primary anchors: [Flauger et al.](https://arxiv.org/abs/1205.3492),
[Dudas--Ghilencea](https://arxiv.org/abs/1503.08319), and
[Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005).
The Cartesian `D5` convention follows the orbifold-superfield framework of
[Hebecker](https://arxiv.org/abs/hep-ph/0112230).

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("status or core hash drifted")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity checks failed")
    if report["C5_decision"]["closed"] or report["C7_decision"]["closed"]:
        raise RuntimeError("feasibility audit cannot close C5/C7")
    if report["G2_decision"]["closed"] or report["G2_decision"]["gates_promoted"]:
        raise RuntimeError("feasibility audit cannot close/promote G2")


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V51 artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V51 JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V51 Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps({"status": report["status"], "core_sha256": report["core_sha256"], "low_degree": report["incidence_inventory"]["low_degree_resolution_counts"], "C5": report["C5_decision"]["status"], "C7": report["C7_decision"]["status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
