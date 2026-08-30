#!/usr/bin/env python3
"""V52 low-index source plus nonlinear-link alignment hybrid audit.

This audit combines, without modifying, two independent V52 ingredients:

* the exact renormalizable 54+45+16+bar16 source witness; and
* the two-site group-valued Spin(10,C) nonlinear link, whose vector image is
  used in the displayed alignment operator.

The low-index source has an exact 12-generator SM stabilizer.  Its 54 vacuum
E0=diag(2^6,-3^4)=(-I+5P)/2 also proves that the SM stabilizer is a subgroup
of the host PS centralizer of P.  The endpoint partition is consequently
12 both, 9 PS-only, 0 source-only and 24 neither.

Unlike a chart projector inserted by hand, the local holomorphic expression

    W_align = -mu/400 Tr([P,U E U^T]^2)

is invariant under PS_host x Spin(10)_source.  At the exact witness its
linear map has rank 24 and its Hessian lifts precisely the 24 relative
orientations.  The complete 176-coordinate holomorphic Hessian (45 link plus
131 source coordinates) has exact rank 122 and nullity 54; its kernel equals
the full broken gauge orbit.

This remains a nonlinear sigma-model EFT, not a renormalizable link UV
completion.  No frozen G2 clause is inherited or promoted.
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

import susy_v52_lean_nonlinear_alignment_audit as lean
import susy_v52_low_index_source_audit as source


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V52_LOW_INDEX_HYBRID_ALIGNMENT_AUDIT.json"
MD_PATH = ROOT / "SUSY_V52_LOW_INDEX_HYBRID_ALIGNMENT_AUDIT.md"

STATUS = (
    "V52_TWO_SITE_NONLINEAR_LINK_PLUS_EXACT_54_45_16_BAR16_SOURCE__"
    "PS_VS_SM_PARTITION_12_9_0_24__"
    "GAUGE_INVARIANT_LOCAL_ALIGNMENT_RANK24__"
    "FULL176_HESSIAN_RANK122_NULLITY54_KERNEL_EQUALS_GAUGE_ORBIT__"
    "LEAN_INDEX_PROXY_AVOIDS_PRE_CUTOFF_LANDAU_POLE__"
    "NONLINEAR_LINK_UV_AND_FULL_MATCHING_OPEN__NO_G2_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_binding() -> dict[str, Any]:
    report = source.build_report()
    source.validate_report(report)
    geometry = report["exact_local_geometry"]
    return {
        "schema": report["schema"],
        "status": report["status"],
        "core_sha256": report["core_sha256"],
        "F_terms_all_zero": report["exact_witness"]["F_terms_all_zero"],
        "D_terms_all_zero": report["exact_witness"]["D_terms_all_zero"],
        "coordinates": source.TOTAL_DIM,
        "orbit_rank": geometry["orbit_rank_mod37"],
        "stabilizer_dimension": geometry["stabilizer_dimension"],
        "source_Hessian_rank": geometry["hessian_rank_mod37"],
        "source_Hessian_nullity": geometry["hessian_nullity_mod37"],
        "source_kernel_equals_orbit": geometry[
            "kernel_equals_broken_gauge_orbit"
        ],
        "source_sum_T": report["perturbativity"]["source_sum_T"],
        "E0_diagonal": report["exact_witness"]["E0_diagonal"],
    }


def endpoint_partition_certificate() -> dict[str, Any]:
    parity = np.diag([1] * 6 + [-1] * 4).astype(np.int64)
    e0 = np.diag([2] * 6 + [-3] * 4).astype(np.int64)
    affine_identity = np.array_equal(2 * e0, -np.eye(10, dtype=np.int64) + 5 * parity)
    binding = source_binding()
    ps_dimension = 21
    source_sm_dimension = binding["stabilizer_dimension"]
    # Because E0 is part of the jointly stabilized source tuple and its two
    # eigenspaces are 6+4, every source stabilizer generator commutes with P.
    source_stabilizer_is_inside_ps = affine_identity and source_sm_dimension == 12
    intersection = source_sm_dimension if source_stabilizer_is_inside_ps else -1
    dimensions = {
        "PS_intersection_source_SM": intersection,
        "PS_only": ps_dimension - intersection,
        "source_SM_only": source_sm_dimension - intersection,
        "neither": 45 - (ps_dimension + source_sm_dimension - intersection),
    }
    return {
        "E0_diagonal": [2] * 6 + [-3] * 4,
        "P_diagonal": [1] * 6 + [-1] * 4,
        "exact_affine_identity": "2 E0 = -I_10 + 5 P",
        "affine_identity_holds": affine_identity,
        "logical_inclusion_proof": (
            "Every generator stabilizing the full source tuple stabilizes E0. "
            "Since E0=(-I+5P)/2, it commutes with P and lies in the 21-dimensional "
            "PS algebra. The independently certified source stabilizer has dimension 12."
        ),
        "source_stabilizer_is_subalgebra_of_PS": source_stabilizer_is_inside_ps,
        "dimensions": dimensions,
        "sum": sum(dimensions.values()),
    }


def alignment_map() -> np.ndarray:
    """B_link: x -> [P,[x,E0]], an exact 100 by 45 integer map."""

    parity = np.diag([1] * 6 + [-1] * 4).astype(np.complex128)
    e0 = np.diag([2] * 6 + [-3] * 4).astype(np.complex128)
    value = np.zeros((100, 45), dtype=np.complex128)
    for column, generator in enumerate(source.antisymmetric_basis()):
        delta_e = generator @ e0 - e0 @ generator
        commutator = parity @ delta_e - delta_e @ parity
        value[:, column] = commutator.reshape(-1)
    return source._gaussian_integer(value, label="hybrid link alignment map")


def full_alignment_map() -> np.ndarray:
    """B on 45 link plus all 131 source coordinates."""

    parity = np.diag([1] * 6 + [-1] * 4).astype(np.complex128)
    value = np.zeros((100, 45 + source.TOTAL_DIM), dtype=np.complex128)
    value[:, :45] = alignment_map()
    for column, variation in enumerate(source.symmetric_traceless_basis()):
        commutator = parity @ variation - variation @ parity
        value[:, 45 + column] = commutator.reshape(-1)
    return source._gaussian_integer(value, label="hybrid full alignment map")


def hybrid_goldstone_incidence() -> tuple[np.ndarray, np.ndarray]:
    """Return exact D(78x66) and A(24x78) in adapted coordinates."""

    blocks: list[np.ndarray] = []
    row_labels: list[tuple[str, int]] = []
    for name, count in (("both", 12), ("PS_only", 9), ("neither", 24)):
        for _ in range(count):
            if name == "both":
                block = np.asarray([[1, -1]], dtype=np.int64)
            elif name == "PS_only":
                block = np.asarray([[1, -1], [0, 1]], dtype=np.int64)
            else:
                block = np.asarray([[-1], [1]], dtype=np.int64)
            blocks.append(block)
            row_labels.append((name, block.shape[0]))
    rows = sum(block.shape[0] for block in blocks)
    columns = sum(block.shape[1] for block in blocks)
    incidence = np.zeros((rows, columns), dtype=np.int64)
    row_cursor = 0
    column_cursor = 0
    for block in blocks:
        next_row = row_cursor + block.shape[0]
        next_column = column_cursor + block.shape[1]
        incidence[row_cursor:next_row, column_cursor:next_column] = block
        row_cursor = next_row
        column_cursor = next_column
    alignment = np.zeros((24, rows), dtype=np.int64)
    output_row = 0
    input_column = 0
    for name, width in row_labels:
        if name == "neither":
            alignment[output_row, input_column] = 1
            alignment[output_row, input_column + 1] = 1
            output_row += 1
        input_column += width
    return incidence, alignment


def full_hessian_and_orbit_numerators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return 200 H_total, 10 Q_total and B for the mu=1 witness."""

    b_map = full_alignment_map()
    alignment_gram = b_map.T @ b_map
    hessian = np.zeros(
        (45 + source.TOTAL_DIM, 45 + source.TOTAL_DIM),
        dtype=np.complex128,
    )
    # source.hessian_numerator() is 20 H_source.  W_align=-Tr(C^2)/400
    # has H_align=B^T B/200 because C is antisymmetric.  Thus this is 200 H.
    hessian[45:, 45:] = 10 * source.hessian_numerator()
    hessian += alignment_gram
    hessian = source._gaussian_integer(hessian, label="200 hybrid Hessian")

    source_orbit = source.orbit_numerator()  # 10 Q_source
    orbit = np.zeros((45 + source.TOTAL_DIM, 21 + 45), dtype=np.complex128)
    ps_indices: list[int] = []
    for index, generator in enumerate(source.antisymmetric_basis()):
        pair = next(
            (a, b)
            for a in range(10)
            for b in range(a + 1, 10)
            if generator[a, b] != 0
        )
        if (pair[0] < 6) == (pair[1] < 6):
            ps_indices.append(index)
    if len(ps_indices) != 21:
        raise RuntimeError("PS generator count drifted")
    for column, generator_index in enumerate(ps_indices):
        orbit[generator_index, column] = 10
    for generator_index in range(45):
        orbit[generator_index, 21 + generator_index] = -10
        orbit[45:, 21 + generator_index] = source_orbit[:, generator_index]
    orbit = source._gaussian_integer(orbit, label="10 hybrid orbit")
    return hessian, orbit, b_map


def exact_hybrid_certificate() -> dict[str, Any]:
    link_map = alignment_map()
    link_gram = link_map.T @ link_map
    ps_broken = np.zeros((45, 45), dtype=np.int64)
    for index, generator in enumerate(source.antisymmetric_basis()):
        pair = next(
            (a, b)
            for a in range(10)
            for b in range(a + 1, 10)
            if generator[a, b] != 0
        )
        if (pair[0] < 6) != (pair[1] < 6):
            ps_broken[index, index] = 1
    gram_identity = np.array_equal(link_gram, 200 * ps_broken)

    incidence, adapted_alignment = hybrid_goldstone_incidence()
    d_rank = int(np.linalg.matrix_rank(incidence))
    a_rank = int(np.linalg.matrix_rank(adapted_alignment))
    combined = incidence @ incidence.T + adapted_alignment.T @ adapted_alignment
    combined_rank = int(np.linalg.matrix_rank(combined))
    combined_determinant = int(sp.Matrix(combined.tolist()).det())

    hessian, orbit, full_map = full_hessian_and_orbit_numerators()
    hessian_rank = source.modular_rank(source._modular_matrix(hessian))
    orbit_rank = source.modular_rank(source._modular_matrix(orbit))
    ward = hessian @ orbit
    ward_max = source._max_abs(ward)
    return {
        "alignment_action": {
            "definition": "C=[P,U E U^T], W_align=-(mu/400) Tr(C^2)",
            "spin_lift_contract": (
                "U is the vector image rho10(mathcal_U) of a fundamental "
                "mathcal_U in Spin(10,C), so rho16(mathcal_U) exists locally for "
                "spinor transport; global bundle sectors remain unaudited"
            ),
            "holomorphic": True,
            "host_PS_covariance": (
                "U->h U, [h,P]=0 gives C->h C h^T and leaves Tr(C^2) invariant"
            ),
            "source_Spin10_covariance": (
                "U->U g^{-1}, E->g E g^T makes U E U^T source-gauge invariant"
            ),
            "theory_space_locality": (
                "local on the single V52 edge; the four-edge V51 analogue is a "
                "Wilson-product operator and requires a separate mediator completion"
            ),
            "renormalizable_elementary_link_completion": False,
            "reason": (
                "U is a constrained group-valued chiral field; expanding it in "
                "canonical coordinates makes the action nonpolynomial"
            ),
        },
        "link_orientation_map": {
            "shape": list(link_map.shape),
            "rank": source.modular_rank(source._modular_matrix(link_map)),
            "sha256": source.gaussian_matrix_sha(link_map),
            "Gram_sha256": source.gaussian_matrix_sha(link_gram),
            "exact_identity": "B_link^T B_link = 200 Pi_(Spin10/PS)",
            "identity_holds": gram_identity,
            "nonzero_Gram_eigenvalue": 200,
            "multiplicity": 24,
        },
        "adapted_Rxi_count": {
            "D_shape": list(incidence.shape),
            "D_rank": d_rank,
            "massless_SM_vectors": incidence.shape[1] - d_rank,
            "uneaten_chirals_before_alignment": incidence.shape[0] - d_rank,
            "A_shape": list(adapted_alignment.shape),
            "A_rank": a_rank,
            "A_D_exact_zero": bool(np.count_nonzero(adapted_alignment @ incidence) == 0),
            "combined_Goldstone_rank": combined_rank,
            "combined_Goldstone_nullity": combined.shape[0] - combined_rank,
            "combined_Goldstone_determinant": str(combined_determinant),
            "exact_determinant_formula": "2^60",
            "spectrum": {
                "2": 60,
                "(3-sqrt(5))/2": 9,
                "(3+sqrt(5))/2": 9,
            },
        },
        "full_holomorphic_system": {
            "coordinates": hessian.shape[0],
            "scope": (
                "source plus nonlinear link and alignment only; transported families, "
                "electroweak Higgs, U(1)F repair, seesaw, doublet-triplet and channel "
                "mediators are not coordinates of this Hessian"
            ),
            "field_order": "45 link chart; 54 E; 45 A; 16 C; 16 barC",
            "published_matrix": "200 H_total at mu=1",
            "H_shape": list(hessian.shape),
            "H_sha256": source.gaussian_matrix_sha(hessian),
            "H_rank_mod37": hessian_rank,
            "H_nullity_mod37": hessian.shape[0] - hessian_rank,
            "orbit_matrix": "10 Q_total for 21 host-PS plus 45 source generators",
            "Q_shape": list(orbit.shape),
            "Q_sha256": source.gaussian_matrix_sha(orbit),
            "Q_rank_mod37": orbit_rank,
            "broken_gauge_dimension": orbit_rank,
            "HQ_exact_zero": ward_max == 0,
            "HQ_max_abs": ward_max,
            "kernel_equals_broken_gauge_orbit": (
                hessian_rank + orbit_rank == hessian.shape[0] and ward_max == 0
            ),
            "full_alignment_map_shape": list(full_map.shape),
            "full_alignment_map_rank": source.modular_rank(
                source._modular_matrix(full_map)
            ),
            "exact_rank_lemma": (
                "mod-37 gives rank(H)>=122 and rank(Q)>=54; exact HQ=0 gives "
                "rank(H)+rank(Q)<=176. Saturation proves both characteristic-zero "
                "ranks and ker(H)=im(Q)."
            ),
        },
    }


def perturbativity_certificate(gauge_coupling: float = 0.73) -> dict[str, Any]:
    source_index = 24
    link_proxy = 8
    four_transport_spinors = 8
    three_families_and_ten = 7
    three_c2 = 24

    def pole(sum_t: int) -> float | None:
        b = three_c2 - sum_t
        if b >= 0:
            return None
        return math.exp(8 * math.pi**2 / (abs(b) * gauge_coupling**2))

    source_link_sum = source_index + link_proxy
    same_site_inventory = source_link_sum + four_transport_spinors
    with_visible = same_site_inventory + three_families_and_ten
    return {
        "convention": "b=3 C2-sum T, T(10)=1, C2(Spin10)=8",
        "gauge_coupling": gauge_coupling,
        "components": {
            "54_plus_45_plus_16_plus_bar16": source_index,
            "nonlinear_link_adjoint_tangent_proxy": link_proxy,
            "four_transport_spinors": four_transport_spinors,
            "three_16_families_plus_one_10H_if_colocated": three_families_and_ten,
            "alignment_extra_index": 0,
        },
        "minimal_source_plus_link_proxy": {
            "sum_T": source_link_sum,
            "b": three_c2 - source_link_sum,
            "b_asymptotic_freedom__3C2_minus_sumT": three_c2 - source_link_sum,
            "b_Landau__sumT_minus_3C2": source_link_sum - three_c2,
            "pole_over_matching_scale": pole(source_link_sum),
        },
        "same_inventory_as_V51_source_site_except_source_and_link_replaced": {
            "sum_T": same_site_inventory,
            "b": three_c2 - same_site_inventory,
            "b_asymptotic_freedom__3C2_minus_sumT": three_c2 - same_site_inventory,
            "b_Landau__sumT_minus_3C2": same_site_inventory - three_c2,
            "pole_over_matching_scale": pole(same_site_inventory),
            "V51_sum_T": 316,
            "V51_b": -292,
            "V51_pole_over_matching_scale": math.exp(
                8 * math.pi**2 / (292 * gauge_coupling**2)
            ),
        },
        "including_colocated_visible_families_and_10H": {
            "sum_T": with_visible,
            "b": three_c2 - with_visible,
            "b_asymptotic_freedom__3C2_minus_sumT": three_c2 - with_visible,
            "b_Landau__sumT_minus_3C2": with_visible - three_c2,
            "pole_over_matching_scale": pole(with_visible),
        },
        "nonlinear_sigma_NDA_cutoff_over_vector_mass": 4 * math.pi / gauge_coupling,
        "interpretation": (
            "All formal one-loop poles are above the sigma-model NDA cutoff, so the "
            "V51 pre-cutoff Landau catastrophe is removed in this proxy. The link "
            "has no elementary linear representation above that cutoff, so this is "
            "not a UV beta-function certificate. Here b=3C2-sumT is the asymptotic-"
            "freedom convention; the positive Landau coefficient is -b=sumT-3C2."
        ),
    }


def build_report() -> dict[str, Any]:
    binding = source_binding()
    partition = endpoint_partition_certificate()
    exact = exact_hybrid_certificate()
    running = perturbativity_certificate()
    full = exact["full_holomorphic_system"]
    rxi = exact["adapted_Rxi_count"]
    checks = {
        "low_index_source_is_exact": (
            binding["F_terms_all_zero"]
            and binding["D_terms_all_zero"]
            and binding["source_kernel_equals_orbit"]
        ),
        "source_SM_is_inside_PS": partition[
            "source_stabilizer_is_subalgebra_of_PS"
        ],
        "partition_is_12_9_0_24": partition["dimensions"]
        == {
            "PS_intersection_source_SM": 12,
            "PS_only": 9,
            "source_SM_only": 0,
            "neither": 24,
        },
        "alignment_rank_is_24": exact["link_orientation_map"]["rank"] == 24,
        "alignment_is_exact_PS_broken_projector": exact[
            "link_orientation_map"
        ]["identity_holds"],
        "alignment_annihilates_gauge_orbit": rxi["A_D_exact_zero"],
        "all_24_residuals_are_lifted": (
            rxi["uneaten_chirals_before_alignment"] == 24
            and rxi["combined_Goldstone_nullity"] == 0
        ),
        "full_HQ_is_exact": full["HQ_exact_zero"],
        "full_kernel_equals_gauge_orbit": full[
            "kernel_equals_broken_gauge_orbit"
        ],
        "SM_vectors_preserved": rxi["massless_SM_vectors"] == 12,
        "alignment_adds_no_Dynkin_index": (
            running["components"]["alignment_extra_index"] == 0
        ),
        "pole_is_above_NDA_cutoff_in_proxy": (
            running[
                "including_colocated_visible_families_and_10H"
            ]["pole_over_matching_scale"]
            > running["nonlinear_sigma_NDA_cutoff_over_vector_mass"]
        ),
        "nonlinear_link_not_called_renormalizable": not exact[
            "alignment_action"
        ]["renormalizable_elementary_link_completion"],
    }
    report = {
        "schema": "susy-v52-low-index-source-nonlinear-link-hybrid-v1",
        "status": STATUS,
        "candidate_name": "two-site nonlinear link plus exact low-index SM source",
        "source_binding": binding,
        "endpoint_partition": partition,
        "exact_alignment_and_full_Hessian": exact,
        "field_and_perturbativity_proxy": running,
        "scientific_result": (
            "A concrete source-order-parameter invariant, not an arbitrary chart mass, "
            "lifts all 24 relative orientations. The exact combined holomorphic "
            "Hessian has no kernel beyond the 54 broken gauge directions."
        ),
        "limitations": [
            "the Spin(10,C) link is a nonlinear sigma EFT without a linear UV completion",
            "the 176-coordinate Hessian covers only the source, link and alignment—not the complete phenomenological field inventory",
            "the result changes the V50/V51 action and site count",
            "the low-index source loses the renormalizable 126-Higgs seesaw and automatic matter parity",
            "the missing-partner/doublet-triplet sector is absent",
            "the independent U(1)F breaking sector remains to be supplied",
            "one-loop matching, Wilson coefficients and global Kähler topology are unaudited",
        ],
        "gate_effect": {
            "V51_link_multiplier_blocker": "REPAIRED_INSIDE_NEW_NONLINEAR_EFT",
            "V51_residual_A5_blocker": (
                "REPAIRED_INSIDE_NEW_HYBRID; source change makes the exact count 24"
            ),
            "C2": "NEW_ACTION_LOCALITY_PASS_ONLY__NO_FROZEN_PROMOTION",
            "C3": (
                "PARTIAL: exact full local holomorphic kernel/orbit theorem passes, "
                "but the gauge-fixed physical pencil and UV link completion are absent"
            ),
            "C4": (
                "PARTIAL: positive local sigma Kähler chart assumed; global Kähler "
                "completion and radiative stability are unproved"
            ),
            "C5": "OPEN_FOR_NEW_ACTION: no one-loop matching",
            "C6": "UNASSESSED_FOR_NEW_ACTION",
            "C7": "OPEN_FOR_NEW_ACTION: no matched Wilson array",
            "candidate_UV_viability": (
                "PARTIAL_EFT_ONLY: perturbativity proxy survives to NDA cutoff, but "
                "no elementary/composite UV completion is constructed"
            ),
            "G2_closed": False,
            "gates_promoted": [],
        },
        "sharp_next_obligations": [
            "construct a calculable anomaly-safe UV completion of the nonlinear link",
            "derive the alignment coefficient from that completion",
            "add and audit the U(1)F-breaking, seesaw/matter-parity and doublet-triplet sectors",
            "compute the complete gauge-fixed physical mass pencil with a chosen Kähler metric",
            "perform one-loop matching and build the final Wilson array",
            "match the new action to the frozen target before moving any G2 clause",
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0104005",
            "https://arxiv.org/abs/hep-th/0006025",
            "https://arxiv.org/abs/hep-ph/0202278",
            "https://arxiv.org/abs/hep-th/0109116",
        ],
        "provenance": {
            "files": {
                path.name: sha256_file(path)
                for path in (
                    ROOT / "susy_v52_low_index_source_audit.py",
                    ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.json",
                    ROOT / "susy_v52_lean_nonlinear_alignment_audit.py",
                    ROOT / "SUSY_V52_LEAN_NONLINEAR_ALIGNMENT_AUDIT.json",
                )
            },
            "existing_files_modified": False,
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash stale")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("hybrid integrity check failed")
    gate = report["gate_effect"]
    if gate["G2_closed"] or gate["gates_promoted"]:
        raise RuntimeError("new hybrid cannot promote frozen gates")
    if not gate["candidate_UV_viability"].startswith("PARTIAL_EFT_ONLY"):
        raise RuntimeError("UV status must stay EFT-only")


def render_markdown(report: Mapping[str, Any]) -> str:
    partition = report["endpoint_partition"]
    exact = report["exact_alignment_and_full_Hessian"]
    link = exact["link_orientation_map"]
    rxi = exact["adapted_Rxi_count"]
    full = exact["full_holomorphic_system"]
    running = report["field_and_perturbativity_proxy"]
    same = running[
        "same_inventory_as_V51_source_site_except_source_and_link_replaced"
    ]
    visible = running["including_colocated_visible_families_and_10H"]
    obligations = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["sharp_next_obligations"], 1)
    )
    return f"""# V52 low-index source/nonlinear-link hybrid audit

Status: `{report['status']}`  
Core SHA-256: `{report['core_sha256']}`

## Outcome

This hybrid removes both of V51's sharp local blockers inside a new EFT.  It
uses one 45-coordinate Spin(10,C)-valued link (with vector image `U`) and the independently exact
renormalizable `54+45+16+bar16` source.  A concrete invariant made from the
source 54 order parameter lifts every relative endpoint orientation.  The
full 176-coordinate holomorphic Hessian has rank 122, nullity 54, and kernel
exactly equal to the broken gauge orbit.

It is not G2 closure.  The link remains a nonlinear sigma field without an
elementary UV completion, and the new source requires new seesaw/parity,
doublet-triplet, U(1)F and matching sectors.

## Exact endpoint partition

The source witness contains

```text
E0=diag(2,2,2,2,2,2,-3,-3,-3,-3),
P =diag(1,1,1,1,1,1,-1,-1,-1,-1),
2 E0 = -I + 5 P.
```

The source audit independently proves that the joint source stabilizer has
dimension 12.  Any joint stabilizer generator must stabilize `E0`, hence
commute with `P`; the source SM is therefore a subalgebra of host PS.  The
45 generators split exactly as

```text
both (SM) = {partition['dimensions']['PS_intersection_source_SM']},
PS only   = {partition['dimensions']['PS_only']},
SM only   = {partition['dimensions']['source_SM_only']},
neither   = {partition['dimensions']['neither']}.
```

The change from the SU(5)-stabilized V51 source doubles the physical relative
orientation count from 12 to 24.

## Explicit local alignment

For `U -> h_PS U g^(-1)` and `E -> g E g^T`, define

```text
C=[P,U E U^T],
W_align=-(mu/400) Tr(C^2).
```

The transported tensor `U E U^T` is invariant under source Spin(10) and
transforms by conjugation under host PS, so the trace is gauge invariant.  At
the witness the exact map `B_link(X)=[P,[X,E0]]` has rank
`{link['rank']}` and satisfies

```text
B_link^T B_link = 200 Pi_(Spin10/PS).
```

This is a source-order-parameter invariant, not a chart projector inserted as
a mass.  It is local on one edge.  It is not renormalizable in elementary
canonical link coordinates because the group-valued chiral field is
nonlinear.

The Goldstone incidence matrix has shape `{rxi['D_shape']}`, rank
`{rxi['D_rank']}`, 12 massless SM vectors, and 24 uneaten chirals before
alignment.  The rank-24 alignment map obeys `A D=0` exactly.  The combined
Goldstone block has rank `{rxi['combined_Goldstone_rank']}`, nullity
`{rxi['combined_Goldstone_nullity']}`, and determinant
`{rxi['exact_determinant_formula']}`.

## Full source-plus-link Hessian theorem

The audit differentiates the actual alignment term with respect to all 45
link coordinates and all 131 source coordinates, then adds it to the exact
source Hessian.  This 176-coordinate matrix does **not** contain the
transported families, electroweak Higgs, U(1)F repair, seesaw,
doublet-triplet, or channel-mediator sectors.  At `mu=1`, the published
Gaussian-integer matrix `200 H` has
shape `{full['H_shape']}`, modular rank `{full['H_rank_mod37']}`, and nullity
`{full['H_nullity_mod37']}`.  The full `10 Q` has shape `{full['Q_shape']}`
and rank `{full['Q_rank_mod37']}`.  `H Q=0` entry by entry.  Since
`122+54=176`, the modular lower bounds and Ward upper bound saturate: over
characteristic zero,

```text
rank(H)=122, nullity(H)=54, ker(H)=im(Q).
```

Thus no additional local holomorphic chiral modulus survives at this witness.

## Perturbativity proxy

The source index is 24, the nonlinear-link adjoint-tangent proxy is 8, and
the alignment adds no field or index.  Replacing the V51 source/link while
retaining its four transported spinors gives

```text
sum T={same['sum_T']}, b_AF=3C2-sumT={same['b_asymptotic_freedom__3C2_minus_sumT']},
b_L=sumT-3C2={same['b_Landau__sumT_minus_3C2']},
formal pole/matching={same['pole_over_matching_scale']:.8g}.
```

Adding three matter 16s and one 10H at the same site gives
`sum T={visible['sum_T']}`,
`b_AF={visible['b_asymptotic_freedom__3C2_minus_sumT']}`,
`b_L={visible['b_Landau__sumT_minus_3C2']}`, and formal pole ratio
`{visible['pole_over_matching_scale']:.8g}`.  Both are above the nonlinear
sigma NDA ceiling `4 pi/g={running['nonlinear_sigma_NDA_cutoff_over_vector_mass']:.8g}`.
This removes V51's pre-cutoff Landau catastrophe, but is not a UV running
proof because the nonlinear link has no linear representation above that
ceiling.

## Decision

The local alignment and source/link Hessian subproblem is solved exactly for
this new action.  C3 and C4 remain partial because the full gauge-fixed
physical pencil, global Kähler completion and UV link are absent.  C5 and C7
need a new matching calculation; C6 is unassessed.  No frozen gate moves.

## Required next work

{obligations}

Primary framework sources: [deconstruction](https://arxiv.org/abs/hep-th/0104005),
[supersymmetric nonlinear sigma models](https://arxiv.org/abs/hep-th/0006025),
[renormalizable SO(10) SM vacua](https://arxiv.org/abs/hep-ph/0202278), and
[SO(10) spinor/tensor couplings](https://arxiv.org/abs/hep-th/0109116).
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("hybrid artifacts missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("hybrid JSON stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("hybrid Markdown stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
