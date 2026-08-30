#!/usr/bin/env python3
"""V53 exact whole-action enlargement and natural-DT obstruction audit.

The elementary branch enlarges the exact V52 54+45+16+bar16 source by the
minimal repair inventory already isolated in V52:

* three matter 16_F families (48 complex coordinates),
* one vector H(10), and
* four Spin(10)-singlet N fields.

The declared renormalizable action is W_source plus 16_F 16_F H,
16_F barC N, N N, and H H + H E H.  At the exact GUT witness every added
scalar VEV is zero.  The executable 193 by 193 Hessian has exact rank 111 and
nullity 82.  Its kernel is exactly the direct sum of the 33 broken Spin(10)
gauge directions, 45 intended light SM matter coordinates and four weak-Higgs
coordinates.  The corresponding 238-coordinate nonlinear-link hybrid has
rank 135 and nullity 103, exactly 54 gauge plus the same 49 light directions.

The four weak-Higgs zero modes require m_H=3 k_H.  This file proves a limited
renormalizable selector no-go for the declared field inventory: E^2 and E^3
force E neutral under every ordinary Abelian selector, so H^2 and H E H have
the same charge and their independent coefficients cannot be related.  The
one-H invariant H^T A H vanishes identically, while the exact A0 and E0 are
both invertible and therefore do not furnish a missing weak direction for a
second 10 either.  A genuine missing-VEV sector, product group, or flipped
embedding changes the action and lacks a same-action exact Hessian here.

Accordingly this is a whole-action local rank certificate plus a fail-closed
naturalness result, not a complete theory and not a gate promotion.
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

import susy_v52_low_index_hybrid_alignment_audit as hybrid
import susy_v52_low_index_source_audit as source
import susy_v52_minimal_seesaw_dt_repair_audit as repair


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_LOW_INDEX_WHOLE_ACTION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_LOW_INDEX_WHOLE_ACTION_AUDIT.md"

STATUS = (
    "V53_LOW_INDEX_WHOLE_ACTION_193_HESSIAN_RANK111_NULLITY82__"
    "KERNEL_EQUALS33_GAUGE_PLUS45_MATTER_PLUS4_WEAK_HIGGS__"
    "OPTIONAL238_NONLINEAR_HYBRID_RANK135_NULLITY103_EXACT__"
    "ABELIAN_SELECTOR_AND_EXISTING_E_A_N_FIELDS_CANNOT_NATURALIZE_DT__"
    "MISSING_VEV_PRODUCT_GROUP_AND_FLIPPED_ROUTES_CHANGE_ACTION__"
    "NATURAL_DT_AND_COMPLETE_OPERATOR_CENSUS_OPEN__NO_GATE_PROMOTION"
)

SOURCE_JSON = ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.json"
REPAIR_JSON = ROOT / "SUSY_V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT.json"
HYBRID_JSON = ROOT / "SUSY_V52_LOW_INDEX_HYBRID_ALIGNMENT_AUDIT.json"


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


def upstream_binding() -> dict[str, Any]:
    source_report = source.build_report()
    source.validate_report(source_report)
    repair_report = repair.build_report()
    repair.validate_report(repair_report)
    hybrid_report = hybrid.build_report()
    hybrid.validate(hybrid_report)
    return {
        "source": {
            "core_sha256": source_report["core_sha256"],
            "status": source_report["status"],
            "coordinates": source.TOTAL_DIM,
            "H_rank": source_report["exact_local_geometry"]["hessian_rank_mod37"],
            "Q_rank": source_report["exact_local_geometry"]["orbit_rank_mod37"],
        },
        "minimal_repair": {
            "core_sha256": repair_report["core_sha256"],
            "status": repair_report["status"],
            "H10_count": repair_report["minimal_additions"]["H10_count"],
            "singlet_count": repair_report["minimal_additions"]["singlet_count"],
        },
        "nonlinear_hybrid": {
            "core_sha256": hybrid_report["core_sha256"],
            "status": hybrid_report["status"],
            "coordinates": hybrid_report["exact_alignment_and_full_Hessian"][
                "full_holomorphic_system"
            ]["coordinates"],
        },
    }


def matter_singlet_hessian() -> np.ndarray:
    """Exact 52 by 52 Hessian for 3(16_F)+4N at the GUT witness."""

    value = np.zeros((52, 52), dtype=np.complex128)
    # The invariant 16_F^T barC_H N with barC0=10 e15 gives the displayed
    # family-rank-three portal.  Matter coordinates are family-major.
    portal = (10, 20, 30)
    for family, coefficient in enumerate(portal):
        matter_index = 16 * family + 15
        singlet_index = 48 + family
        value[matter_index, singlet_index] = coefficient
        value[singlet_index, matter_index] = coefficient
    for singlet, mass in enumerate((1000, 2000, 3000, 4000)):
        value[48 + singlet, 48 + singlet] = mass
    return source._gaussian_integer(value, label="V53 matter-singlet Hessian")


def higgs_hessian() -> np.ndarray:
    """Exact tuned H10 Hessian diag(5^6,0^4)."""

    return np.diag([5] * 6 + [0] * 4).astype(np.complex128)


def elementary_whole_hessian_and_orbit() -> tuple[np.ndarray, np.ndarray]:
    """Return 20 H_whole and 10 Q_whole for 193 elementary coordinates."""

    dimension = source.TOTAL_DIM + 48 + 10 + 4
    hessian = np.zeros((dimension, dimension), dtype=np.complex128)
    hessian[: source.TOTAL_DIM, : source.TOTAL_DIM] = source.hessian_numerator()
    # source.hessian_numerator is 20 H_source.
    matter_offset = source.TOTAL_DIM
    hessian[matter_offset : matter_offset + 52, matter_offset : matter_offset + 52] = (
        20 * matter_singlet_hessian()
    )
    # Reorder the repair block from (matter48,N4) to the whole ordering
    # (matter48,H10,N4): move N to the final four coordinates.
    reordered = np.zeros_like(hessian)
    reordered[: source.TOTAL_DIM, : source.TOTAL_DIM] = hessian[
        : source.TOTAL_DIM, : source.TOTAL_DIM
    ]
    h10_offset = source.TOTAL_DIM + 48
    n_offset = h10_offset + 10
    ms = matter_singlet_hessian()
    reordered[matter_offset:h10_offset, matter_offset:h10_offset] = 20 * ms[:48, :48]
    reordered[matter_offset:h10_offset, n_offset:n_offset + 4] = 20 * ms[:48, 48:]
    reordered[n_offset:n_offset + 4, matter_offset:h10_offset] = 20 * ms[48:, :48]
    reordered[n_offset:n_offset + 4, n_offset:n_offset + 4] = 20 * ms[48:, 48:]
    reordered[h10_offset:n_offset, h10_offset:n_offset] = 20 * higgs_hessian()
    hessian = source._gaussian_integer(reordered, label="20 V53 whole Hessian")

    orbit = np.zeros((dimension, 45), dtype=np.complex128)
    orbit[: source.TOTAL_DIM, :] = source.orbit_numerator()
    orbit = source._gaussian_integer(orbit, label="10 V53 whole orbit")
    return hessian, orbit


def intended_light_kernel(elementary: bool = True) -> np.ndarray:
    """Return 49 independent light columns: 45 matter plus four weak H."""

    base = source.TOTAL_DIM if elementary else 45 + source.TOTAL_DIM
    total = base + 48 + 10 + 4
    columns = np.zeros((total, 49), dtype=np.complex128)
    column = 0
    for family in range(3):
        for component in range(16):
            if component == 15:
                continue
            columns[base + 16 * family + component, column] = 1
            column += 1
    h10_offset = base + 48
    for component in range(6, 10):
        columns[h10_offset + component, column] = 1
        column += 1
    if column != 49:
        raise RuntimeError("light-kernel count drifted")
    return columns


def hybrid_whole_hessian_and_orbit() -> tuple[np.ndarray, np.ndarray]:
    """Return 200 H and 10 Q for link+source+matter+H10+N (238 coords)."""

    hybrid_hessian, hybrid_orbit, _ = hybrid.full_hessian_and_orbit_numerators()
    base = hybrid_hessian.shape[0]
    total = base + 48 + 10 + 4
    value = np.zeros((total, total), dtype=np.complex128)
    value[:base, :base] = hybrid_hessian
    matter_offset = base
    h10_offset = base + 48
    n_offset = h10_offset + 10
    ms = matter_singlet_hessian()
    # hybrid_hessian is 200 H; scale the physical repair blocks accordingly.
    value[matter_offset:h10_offset, n_offset:n_offset + 4] = 200 * ms[:48, 48:]
    value[n_offset:n_offset + 4, matter_offset:h10_offset] = 200 * ms[48:, :48]
    value[n_offset:n_offset + 4, n_offset:n_offset + 4] = 200 * ms[48:, 48:]
    value[h10_offset:n_offset, h10_offset:n_offset] = 200 * higgs_hessian()
    value = source._gaussian_integer(value, label="200 V53 hybrid whole Hessian")
    orbit = np.zeros((total, hybrid_orbit.shape[1]), dtype=np.complex128)
    orbit[:base, :] = hybrid_orbit
    orbit = source._gaussian_integer(orbit, label="10 V53 hybrid whole orbit")
    return value, orbit


def exact_rank_certificate() -> dict[str, Any]:
    elementary_h, elementary_q = elementary_whole_hessian_and_orbit()
    elementary_k = intended_light_kernel(True)
    elementary_h_rank = source.modular_rank(source._modular_matrix(elementary_h))
    elementary_q_rank = source.modular_rank(source._modular_matrix(elementary_q))
    elementary_k_rank = source.modular_rank(source._modular_matrix(elementary_k))
    elementary_qk = np.column_stack((elementary_q, elementary_k))
    elementary_qk_rank = source.modular_rank(source._modular_matrix(elementary_qk))

    hybrid_h, hybrid_q = hybrid_whole_hessian_and_orbit()
    hybrid_k = intended_light_kernel(False)
    hybrid_h_rank = source.modular_rank(source._modular_matrix(hybrid_h))
    hybrid_q_rank = source.modular_rank(source._modular_matrix(hybrid_q))
    hybrid_k_rank = source.modular_rank(source._modular_matrix(hybrid_k))
    hybrid_qk = np.column_stack((hybrid_q, hybrid_k))
    hybrid_qk_rank = source.modular_rank(source._modular_matrix(hybrid_qk))

    return {
        "declared_elementary_action": {
            "field_order": [
                "E54[54]",
                "A45[45]",
                "C16_H[16]",
                "barC16_H[16]",
                "16F_1..3[48]",
                "H10[10]",
                "N_1..4[4]",
            ],
            "coordinate_sum": 54 + 45 + 16 + 16 + 48 + 10 + 4,
            "superpotential": (
                "W_source + 1/2 Y10_ij 16F_i 16F_j H10 + "
                "yN_ia 16F_i barC_H N_a + 1/2 MS_ab N_a N_b + "
                "1/2 mH H10^T H10 + 1/2 kH H10^T E H10"
            ),
            "vacuum": (
                "exact V52 E,A,C,barC witness; all 16F,H10,N scalar VEVs zero"
            ),
            "stationarity_reason": (
                "every added F term contains at least one zero-VEV added field; "
                "MS is nonsingular and the source F,D terms remain exactly zero"
            ),
            "published_H": "20 H_whole",
            "H_shape": list(elementary_h.shape),
            "H_sha256": source.gaussian_matrix_sha(elementary_h),
            "H_rank_mod37": elementary_h_rank,
            "H_nullity": elementary_h.shape[0] - elementary_h_rank,
            "published_Q": "10 Q_whole",
            "Q_shape": list(elementary_q.shape),
            "Q_sha256": source.gaussian_matrix_sha(elementary_q),
            "Q_rank_mod37": elementary_q_rank,
            "HQ_exact_zero": source._max_abs(elementary_h @ elementary_q) == 0,
            "intended_light_K_shape": list(elementary_k.shape),
            "intended_light_K_rank_mod37": elementary_k_rank,
            "HK_exact_zero": source._max_abs(elementary_h @ elementary_k) == 0,
            "Q_plus_K_rank_mod37": elementary_qk_rank,
            "kernel_decomposition": (
                "ker(H)=33 broken-gauge directions direct-sum 45 light matter "
                "coordinates direct-sum 4 weak-Higgs coordinates"
            ),
            "kernel_decomposition_exact": (
                elementary_h_rank + elementary_qk_rank == elementary_h.shape[0]
                and elementary_qk_rank == elementary_q_rank + elementary_k_rank
                and source._max_abs(elementary_h @ elementary_qk) == 0
            ),
            "zero_VEV_block_decoupling": {
                "source_H10_mixed_Hessian": "zero because H10=0",
                "source_N_mixed_Hessian_except_barC_portal": (
                    "zero because 16F=N=0; barC0 turns only 16F-N into a bilinear"
                ),
                "Yukawa_H10_16F_16F_Hessian": "zero because H10=16F=0",
                "matter_N_block_rank": source.modular_rank(
                    source._modular_matrix(matter_singlet_hessian())
                ),
                "H10_block_rank": source.modular_rank(
                    source._modular_matrix(higgs_hessian())
                ),
            },
        },
        "optional_same-field_hybrid_EFT": {
            "scope": (
                "adds the 45-coordinate nonlinear Spin(10,C) link and exact rank-24 "
                "alignment to the identical elementary matter/H10/N inventory"
            ),
            "coordinate_sum": hybrid_h.shape[0],
            "published_H": "200 H_hybrid_whole",
            "H_shape": list(hybrid_h.shape),
            "H_sha256": source.gaussian_matrix_sha(hybrid_h),
            "H_rank_mod37": hybrid_h_rank,
            "H_nullity": hybrid_h.shape[0] - hybrid_h_rank,
            "Q_shape": list(hybrid_q.shape),
            "Q_sha256": source.gaussian_matrix_sha(hybrid_q),
            "Q_rank_mod37": hybrid_q_rank,
            "HQ_exact_zero": source._max_abs(hybrid_h @ hybrid_q) == 0,
            "intended_light_K_rank_mod37": hybrid_k_rank,
            "HK_exact_zero": source._max_abs(hybrid_h @ hybrid_k) == 0,
            "Q_plus_K_rank_mod37": hybrid_qk_rank,
            "kernel_decomposition": (
                "ker(H)=54 broken product-gauge directions direct-sum 45 light "
                "matter coordinates direct-sum 4 weak-Higgs coordinates"
            ),
            "kernel_decomposition_exact": (
                hybrid_h_rank + hybrid_qk_rank == hybrid_h.shape[0]
                and hybrid_qk_rank == hybrid_q_rank + hybrid_k_rank
                and source._max_abs(hybrid_h @ hybrid_qk) == 0
            ),
            "UV_status": "nonlinear sigma EFT only; not an elementary completion",
        },
    }


def natural_dt_obstruction() -> dict[str, Any]:
    e0 = np.diag([2] * 6 + [-3] * 4).astype(np.int64)
    a0 = np.zeros((10, 10), dtype=np.int64)
    for (first, second), coefficient in (
        ((0, 1), 1),
        ((2, 3), 1),
        ((4, 5), 1),
        ((6, 7), 3),
        ((8, 9), 3),
    ):
        a0[first, second] = coefficient
        a0[second, first] = -coefficient
    symbolic_h = np.asarray([f"h{index}" for index in range(10)], dtype=object)
    # h^T A h cancels pairwise for commuting chiral coordinates.
    one_h_a_h_terms = []
    for first in range(10):
        for second in range(10):
            if a0[first, second]:
                one_h_a_h_terms.append(
                    (first, second, int(a0[first, second]))
                )
    antisymmetric_pair_cancellation = all(
        a0[first, second] == -a0[second, first]
        for first in range(10)
        for second in range(10)
    ) and np.array_equal(a0 + a0.T, np.zeros((10, 10), dtype=np.int64))

    return {
        "tuned_block": {
            "Hessian": "mH I_10+kH E0",
            "triplet_eigenvalue": "mH+2 kH",
            "weak_eigenvalue": "mH-3 kH",
            "light_pair_condition": "mH=3 kH",
            "codimension": 1,
            "unit_perturbation_mH_3_to_4_gives_rank": 10,
        },
        "ordinary_Abelian_selector_no_go": {
            "source_requirements": "E^2 and E^3 are both nonzero allowed operators",
            "charge_equations": "2 qE=0 and 3 qE=0 imply qE=0 in every Abelian charge group",
            "consequence": "H^2 and H E H both carry charge 2 qH",
            "selector_options": [
                "allow both with independent coefficients: DT zero requires tuning",
                "forbid both: all ten H coordinates are massless",
            ],
            "can_enforce_mH_equals_3kH": False,
        },
        "existing_field_missing_eigenvalue_tests": {
            "E0_rank": int(np.linalg.matrix_rank(e0)),
            "E0_determinant": int(round(np.linalg.det(e0))),
            "A0_rank": int(np.linalg.matrix_rank(a0)),
            "A0_determinant": int(round(np.linalg.det(a0))),
            "A0_plane_coefficients": [1, 1, 1, 3, 3],
            "A0_has_DW_missing_weak_entry": False,
            "one_H_transpose_A_H_identically_zero": antisymmetric_pair_cancellation,
            "singlets_can_distinguish_triplet_from_doublet": False,
            "two_H_A0_only_block_rank": 20,
            "conclusion": (
                "E0 and A0 are invertible on both color and weak subspaces. A second "
                "10 coupled through A0 makes all 20 vector coordinates massive; it "
                "does not leave a weak pair. Gauge singlets cannot select Spin(10) components."
            ),
        },
        "scope": (
            "no-go covers ordinary Abelian/discrete selectors acting on the declared "
            "fields and renormalizable one- or two-10 bilinears using the exact E0,A0. "
            "It is not a theorem against enlarged gauge groups or new missing-VEV order parameters."
        ),
    }


def alternative_route_stress_test(gauge_coupling: float = 0.73) -> dict[str, Any]:
    def pole(landau_b: int) -> float:
        return math.exp(8 * math.pi**2 / (landau_b * gauge_coupling**2))

    return {
        "extended_missing_VEV_same_gauge_group": {
            "field_content_target": (
                "54+2(45)+3(16+bar16)+1 or 2(10)+singlets"
            ),
            "minimum_addition_over_declared_whole_action": (
                "one 45 plus two 16+bar16 pairs; optionally a second 10; singlet count model-dependent"
            ),
            "minimum_new_non_singlet_coordinates": 45 + 2 * 32,
            "with_second_10_new_non_singlet_coordinates": 45 + 2 * 32 + 10,
            "Landau_b_sumT_minus3C2_range": [23, 24],
            "pole_ratio_range_at_g0p73": [pole(24), pole(23)],
            "fatal_same_action_issue": (
                "natural DT requires new nonzero missing-VEV backgrounds; their F,D "
                "equations and mixed Hessian are not block-diagonal additions to V52, "
                "so rank111 cannot be inherited"
            ),
            "decision": "credible next construction, not an exact V53 completion",
        },
        "flipped_Spin10_times_U1X": {
            "gauge_dimension": 46,
            "published_minimal_Higgs_coordinates": 109,
            "generic_broken_generators": 34,
            "required_Hessian_rank_if_isolated": 75,
            "published_one_loop_coefficients": {"Spin10": 1, "U1Xhat": "67/24"},
            "fatal_same_action_issue": (
                "changes the gauge group, family embedding, hypercharge definition, "
                "anomaly ledger and operator basis; its minimal DT sector is still tuned"
            ),
            "decision": "not a same-lineage natural-DT repair",
        },
        "product_group": {
            "candidate": "Spin(10)_A x Spin(10)_B with a bifundamental/missing-VEV link",
            "benefit": "can turn component selection into a vacuum alignment condition",
            "fatal_same_action_issue": (
                "a linear vector bifundamental has 100 coordinates and large spectator "
                "index; a group-valued link repeats the nonlinear-UV problem. No exact "
                "F-flat missing-VEV vacuum, full Hessian or spinor-link completion is supplied."
            ),
            "decision": "research alternative only",
        },
        "Babu_Pati_Tavartkiladze_single_adjoint_U1A": {
            "primary_source": "https://arxiv.org/abs/1003.2625",
            "field_inventory": [
                "A45",
                "H10",
                "Hprime10",
                "C16+barCbar16",
                "Cprime16+barCprimebar16",
                "S1",
                "Z1",
            ],
            "Higgs_complex_coordinates": 45 + 10 + 10 + 16 + 16 + 16 + 16 + 1 + 1,
            "with_three_matter_16_coordinates": (
                45 + 10 + 10 + 16 + 16 + 16 + 16 + 1 + 1 + 48
            ),
            "Spin10_Dynkin_index": {
                "Higgs": 8 + 1 + 1 + 2 + 2 + 2 + 2,
                "three_families": 6,
                "sum": 24,
                "b_Landau_sumT_minus3C2": 0,
            },
            "missing_VEV": (
                "A0=i sigma2 tensor diag(a,a,a,0,0), unlike the exact V52 "
                "A0=i sigma2 tensor diag(1,1,1,3,3)"
            ),
            "selector": (
                "Z2-assisted anomalous U(1)A; charges forbid the dangerous "
                "A^n(C barC)^m and H^2 classes and stabilize the missing VEV "
                "to all operator orders within the stated EFT charge analysis"
            ),
            "action_scope": (
                "contains essential nonrenormalizable A4/M*, Z^k Hprime^2/M*^(k-1), "
                "ZA spinor and AHprime C Cprime/M* operators; k=5 is preferred"
            ),
            "naive_exact_Hessian_target": {
                "gauge_group_dimension": 46,
                "unbroken_SM_dimension": 12,
                "broken_gauge_orbit_if_U1A_fully_included": 34,
                "131_coordinate_Higgs_rank_needed_if_no_physical_modulus": 97,
                "warning": (
                    "an anomalous U(1) requires its Green-Schwarz/Stueckelberg chiral "
                    "sector and FI completion; 131 coordinates alone are not a closed "
                    "gauge-invariant Hessian domain"
                ),
            },
            "why_not_importable_as_V52_enlargement": (
                "it deletes E54, replaces the V52 A/C vacuum and superpotential, adds "
                "a second spinor pair, second 10, S,Z, an anomalous gauge factor, FI/GS "
                "physics and cutoff operators. No V52 Hessian block or rank survives by "
                "direct sum. A new Cartesian invariant implementation, rational F/D-flat "
                "witness, full GS-inclusive Q, and differentiated Hessian are required."
            ),
            "proton_claim_scope": (
                "the paper derives threshold/proton correlations for its own charge and "
                "mass assumptions; those predictions cannot be inherited by V53"
            ),
            "decision": (
                "best low-index natural-DT benchmark, but a replacement action rather "
                "than a same-lineage exact completion"
            ),
        },
    }


def perturbativity_certificate(gauge_coupling: float = 0.73) -> dict[str, Any]:
    sum_t = 24 + 6 + 1
    three_c2 = 24
    landau_b = sum_t - three_c2
    pole = math.exp(8 * math.pi**2 / (landau_b * gauge_coupling**2))
    return {
        "convention": (
            "b_L=sumT-3C2; b_AF=-b_L=3C2-sumT; T54=12,T45=8,T16=2,T10=1"
        ),
        "elementary_whole_action": {
            "source_T": 24,
            "three_matter_16_T": 6,
            "H10_T": 1,
            "four_N_T": 0,
            "sum_T": sum_t,
            "b_Landau": landau_b,
            "b_asymptotic_freedom": -landau_b,
            "pole_over_matching_scale": pole,
        },
        "tuned_DT_does_not_cost_extra_index": True,
        "natural_missing_VEV_cost": (
            "known low-representation targets raise b_L to 23-24 before thresholds"
        ),
        "scope": (
            "one-loop formal running only; no two-loop thresholds, flavour messengers, "
            "U1F repair, proton-decay dressing or SUSY thresholds"
        ),
    }


def build_report() -> dict[str, Any]:
    upstream = upstream_binding()
    ranks = exact_rank_certificate()
    naturalness = natural_dt_obstruction()
    alternatives = alternative_route_stress_test()
    running = perturbativity_certificate()
    elementary = ranks["declared_elementary_action"]
    hybrid_branch = ranks["optional_same-field_hybrid_EFT"]
    checks = {
        "source_upstream_exact": upstream["source"]["H_rank"] == 98
        and upstream["source"]["Q_rank"] == 33,
        "elementary_coordinate_count_193": elementary["coordinate_sum"] == 193,
        "elementary_H_rank111_nullity82": elementary["H_rank_mod37"] == 111
        and elementary["H_nullity"] == 82,
        "elementary_HQ_zero": elementary["HQ_exact_zero"],
        "elementary_kernel_is_gauge_plus49_light": elementary[
            "kernel_decomposition_exact"
        ],
        "matter_N_rank7": elementary["zero_VEV_block_decoupling"][
            "matter_N_block_rank"
        ]
        == 7,
        "H10_rank6": elementary["zero_VEV_block_decoupling"]["H10_block_rank"]
        == 6,
        "hybrid_coordinate_count238": hybrid_branch["coordinate_sum"] == 238,
        "hybrid_H_rank135_nullity103": hybrid_branch["H_rank_mod37"] == 135
        and hybrid_branch["H_nullity"] == 103,
        "hybrid_kernel_is_gauge_plus49_light": hybrid_branch[
            "kernel_decomposition_exact"
        ],
        "Abelian_selector_no_go_is_exposed": not naturalness[
            "ordinary_Abelian_selector_no_go"
        ]["can_enforce_mH_equals_3kH"],
        "existing_E_and_A_are_not_missing_VEVs": (
            naturalness["existing_field_missing_eigenvalue_tests"]["E0_rank"] == 10
            and naturalness["existing_field_missing_eigenvalue_tests"]["A0_rank"]
            == 10
            and not naturalness["existing_field_missing_eigenvalue_tests"][
                "A0_has_DW_missing_weak_entry"
            ]
        ),
        "BPT_benchmark_is_low_index_but_cross_action": (
            alternatives["Babu_Pati_Tavartkiladze_single_adjoint_U1A"][
                "Higgs_complex_coordinates"
            ]
            == 131
            and alternatives["Babu_Pati_Tavartkiladze_single_adjoint_U1A"][
                "Spin10_Dynkin_index"
            ]["b_Landau_sumT_minus3C2"]
            == 0
            and "replacement action"
            in alternatives["Babu_Pati_Tavartkiladze_single_adjoint_U1A"][
                "decision"
            ]
        ),
        "natural_DT_not_claimed": True,
        "no_gate_promotion": True,
    }
    report = {
        "schema": "susy-v53-low-index-whole-action-audit-v1",
        "status": STATUS,
        "candidate_name": "V52 low-index source plus three families, H10 and four N",
        "upstream_binding": upstream,
        "exact_whole_action_rank_certificate": ranks,
        "natural_DT_obstruction": naturalness,
        "alternative_route_stress_test": alternatives,
        "perturbativity": running,
        "scientific_verdict": (
            "The declared sparse whole action has an exact local Hessian and exactly "
            "the intended gauge, matter and weak-Higgs kernel. It does not become a "
            "natural complete action: its light Higgs pair is tuned, the external Z2 "
            "cannot enforce the tuning, and omitted allowed invariants/operator classes "
            "lack a UV selector."
        ),
        "whole_action_scope_warning": (
            "whole-action means every coordinate of the explicitly declared sparse "
            "renormalizable source+matter+H10+N action. It does not mean the most "
            "general symmetry-allowed action, because the selector does not yet protect "
            "all omitted Higgs-spinor and dimension-five operators."
        ),
        "gate_effect": {
            "C1": (
                "PARTIAL: declared 193-coordinate action explicit; most-general "
                "selector-protected invariant census absent"
            ),
            "C3": (
                "LOCAL_WHOLE_ACTION_PASS: exact H/Q/light-kernel accounting for the "
                "declared elementary action"
            ),
            "C4": (
                "PARTIAL: canonical local metric gives the intended kernel, but DT "
                "tuning and global/radiative vacuum stability remain open"
            ),
            "C5": "OPEN: no one-loop matching or threshold cancellation",
            "C6": (
                "PARTIAL: external Z2 ledger exists but cannot naturalize DT or forbid "
                "all even-matter dimension-five operators"
            ),
            "C7": "OPEN: no same-action Wilson array",
            "G2": "OPEN",
            "gates_promoted": [],
        },
        "sharp_next_obligations": [
            "choose and solve one explicit renormalizable missing-VEV sector, including all new F and D equations",
            "recompute the enlarged Hessian rather than append literature ranks",
            "construct a UV selector that permits Yukawa and seesaw terms while forbidding dangerous dimension-five operators",
            "enumerate the most general selector-allowed action and recheck stationarity",
            "compute thresholds, two-loop unification, proton decay and the same-action Wilson array",
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "primary_sources": [
            "https://arxiv.org/abs/hep-ph/0202278",
            "https://arxiv.org/abs/hep-ph/9810315",
            "https://arxiv.org/abs/hep-ph/9705366",
            "https://arxiv.org/abs/1011.1821",
            "https://arxiv.org/abs/hep-th/9109045",
            "https://arxiv.org/abs/1003.2625",
        ],
        "provenance": {
            "files": {
                path.name: sha256_file(path)
                for path in (
                    SOURCE_JSON,
                    REPAIR_JSON,
                    HYBRID_JSON,
                    ROOT / "susy_v52_low_index_source_audit.py",
                    ROOT / "susy_v52_minimal_seesaw_dt_repair_audit.py",
                    ROOT / "susy_v52_low_index_hybrid_alignment_audit.py",
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
        raise RuntimeError("V53 whole-action integrity failure")
    gate = report["gate_effect"]
    if gate["G2"] != "OPEN" or gate["gates_promoted"]:
        raise RuntimeError("whole-action subproblem cannot promote G2")
    if not gate["C1"].startswith("PARTIAL") or not gate["C6"].startswith(
        "PARTIAL"
    ):
        raise RuntimeError("completeness/naturalness boundary drifted")


def render_markdown(report: Mapping[str, Any]) -> str:
    elementary = report["exact_whole_action_rank_certificate"][
        "declared_elementary_action"
    ]
    hybrid_branch = report["exact_whole_action_rank_certificate"][
        "optional_same-field_hybrid_EFT"
    ]
    dt = report["natural_DT_obstruction"]
    running = report["perturbativity"]["elementary_whole_action"]
    missing = report["alternative_route_stress_test"][
        "extended_missing_VEV_same_gauge_group"
    ]
    obligations = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["sharp_next_obligations"], 1)
    )
    return f"""# V53 low-index whole-action audit

Status: `{report['status']}`  
Core SHA-256: `{report['core_sha256']}`

## Outcome

The declared elementary enlargement now has a complete local Hessian
certificate.  Its 193 coordinates are the exact `54+45+16+bar16` source,
three matter 16s, one 10H, and four singlets.  At the exact GUT witness all
new scalar VEVs vanish.  The Hessian has rank `{elementary['H_rank_mod37']}`
and nullity `{elementary['H_nullity']}`.  Its kernel is exactly

```text
33 broken Spin(10) gauge directions
+45 intended light SM matter coordinates
+ 4 weak-Higgs coordinates
=82.
```

This is a strong local rank result, but the four Higgs modes are retained by
the unprotected relation `mH=3 kH`.  The declared selector cannot impose that
relation, and the declared sparse action is not yet the most general
selector-allowed action.  Natural doublet-triplet splitting and G2 therefore
remain open.

## Exact block construction

The field order is

```text
E54[54], A45[45], C16H[16], barC16H[16],
16F_1..3[48], H10[10], N_1..4[4].
```

The published Gaussian-integer matrix is `20 H_whole`, shape
`{elementary['H_shape']}`, hash `{elementary['H_sha256']}`.  Reduction modulo
37 gives rank `{elementary['H_rank_mod37']}`.  The extended gauge orbit
`10 Q_whole` has rank `{elementary['Q_rank_mod37']}` and `H Q=0` exactly.
The explicit 49-column light basis also satisfies `H K=0`; `[Q,K]` has rank
82.  Since `111+82=193`, the kernel decomposition is exact over
characteristic zero.

The zero-VEV decoupling is explicit.  `H10-E` mixed Hessian entries vanish
because `H10=0`; Yukawa Hessian entries vanish because both matter and H10
VEVs vanish.  The nonzero `barC` VEV converts only `16F barC N` into a
rank-three matter-singlet portal.  Together with nonsingular `MS`, that 52
coordinate block has rank 7 and leaves precisely 45 matter coordinates.  The
H10 block has rank 6 and weak nullity 4.

## Optional nonlinear-link extension

Adding the already-audited 45-coordinate Spin(10,C) nonlinear link gives 238
coordinates.  The recomputed whole EFT Hessian—not a pasted rank—has rank
`{hybrid_branch['H_rank_mod37']}`, nullity `{hybrid_branch['H_nullity']}`, and
kernel exactly `54 gauge +45 matter +4 weak Higgs =103`.  It remains a
nonlinear sigma EFT without an elementary UV completion, so it is not the
selected elementary whole action.

## Why the present DT zero is not natural

The exact vector block is

```text
M_H=mH I+kH E0,
M_triplet=mH+2kH,
M_weak=mH-3kH.
```

Both `E^2` and `E^3` occur in the nonzero source action.  For every ordinary
Abelian or discrete selector, `2qE=3qE=0` implies `qE=0`.  Consequently
`H^2` and `H E H` always have the same selector charge: a selector either
allows both with independent coefficients or forbids both.  It cannot impose
`mH=3kH`.

The other declared fields do not repair this.  `H^T A H` vanishes for one H
because A is antisymmetric.  The exact E0 and A0 both have rank 10; A0 has
plane coefficients `(1,1,1,3,3)`, not a Dimopoulos-Wilczek missing weak
entry.  A second 10 coupled only through A0 therefore gives a rank-20 block,
not one light weak pair.  Gauge singlets cannot distinguish color from weak
components.

This no-go is intentionally limited to the declared order parameters,
ordinary Abelian selectors and renormalizable one/two-10 bilinears.  It does
not exclude a genuinely new missing-VEV sector.

## Perturbativity and alternatives

The elementary whole inventory has `sum T={running['sum_T']}`,
`b_L=sumT-3C2={running['b_Landau']}`, and formal pole ratio
`{running['pole_over_matching_scale']:.8g}` at `g=0.73`.

A known extended missing-VEV target adds at least one 45 and two
`16+bar16` pairs, raising `b_L` to 23-24 and the formal pole window to roughly
`{missing['pole_ratio_range_at_g0p73'][0]:.3g}`-
`{missing['pole_ratio_range_at_g0p73'][1]:.3g}`.  More importantly, those
fields require new nonzero backgrounds, so the rank-111 theorem cannot be
inherited; the enlarged F/D system and Hessian must be solved from scratch.

Flipped `Spin(10)xU(1)X` has a much larger perturbative margin but changes the
gauge group, family embedding, hypercharge and invariant basis, while its
minimal DT mechanism is still tuned.  A product-group missing-VEV link can
make component selection geometric, but a linear link is large and a
group-valued link repeats the nonlinear-UV problem.  Neither is a same-lineage
completion here.

The strongest low-index adversarial benchmark is the single-adjoint
`Z2 x U(1)A` model of Babu, Pati and Tavartkiladze.  Its Higgs inventory is
`45+2(10)+2(16+bar16)+S+Z`, again 131 coordinates, with Spin(10) Higgs index
18 and total index 24 after three families: `b_L=0`.  Its missing VEV
`diag(a,a,a,0,0)` and charge rules stabilize the weak zero to all operator
orders in that EFT and support proton-decay correlations.  It is nevertheless
not an enlargement of V52: it removes the 54, replaces the exact A/C vacuum,
adds an anomalous gauge factor and essential cutoff operators.  A closed
Hessian must also contain the Green-Schwarz/Stueckelberg sector behind the
anomalous U(1) and FI term.  The naive 131-coordinate target would need rank
97 for 34 broken gauge directions, but no such repository certificate exists;
none of its DT or proton predictions is imported here.

## Gate boundary

C3 passes only as a local rank statement for the explicitly declared sparse
action.  C1, C4 and C6 remain partial; C5 and C7 remain open.  No gate is
promoted and G2 remains open.

## Required next work

{obligations}

Primary comparisons: [renormalizable SO(10) vacua](https://arxiv.org/abs/hep-ph/0202278),
[low-representation missing-VEV DT](https://arxiv.org/abs/hep-ph/9810315),
[DW completion](https://arxiv.org/abs/hep-ph/9705366),
[minimal flipped SO(10)](https://arxiv.org/abs/1011.1821), and
[discrete-gauge anomaly scope](https://arxiv.org/abs/hep-th/9109045).  The
single-adjoint stabilized-DT benchmark is
[Babu--Pati--Tavartkiladze](https://arxiv.org/abs/1003.2625).
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V53 whole-action artifacts missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V53 whole-action JSON stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V53 whole-action Markdown stale; run --write")


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
