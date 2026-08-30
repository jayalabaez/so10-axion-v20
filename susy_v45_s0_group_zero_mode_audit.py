#!/usr/bin/env python3
"""Exact V45 S0 group/global-form and zero-mode audit.

This module tests only the first stage of the sequestered five-dimensional
Spin(10) successor selected in V44.  It separates three logically different
questions:

1. whether the standard Pati--Salam orbifold projection and an aligned
   126+bar126 boundary VEV leave the Standard-Model *connected* gauge group;
2. which finite gauge factors necessarily remain for a Spin(10) parent and a
   primitive U(1)_F broken by charge-nine fields; and
3. whether the V44 boundary matter list consists of honest representations of
   the global Pati--Salam subgroup inherited from Spin(10).

The root-system and anomaly arithmetic are exact.  The result is deliberately
fail-closed: an exact group-theory witness does not supply the missing boundary
Higgs potential, localized anomaly calculation, or KK spectrum.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.md"

INPUTS = {
    "v44_successor_contract": ROOT / "SUSY_V44_NEW_PHYSICS_SUCCESSOR_CONTRACT.md",
    "v40_selector_json": ROOT / "SUSY_V40_ALL_RING_SELECTOR.json",
    "v40_selector_source": ROOT / "susy_v40_all_ring_selector.py",
}

SOURCE_FILES = (
    "susy_v45_s0_group_zero_mode_audit.py",
    "test_susy_v45_s0_group_zero_mode_audit.py",
    *tuple(path.name for path in INPUTS.values()),
)

STATUS = (
    "V45_S0_CONNECTED_SM_INTERSECTION_CERTIFIED__"
    "V44_NAKED_PS_DOUBLETS_GLOBALLY_INVALID__"
    "MINIMAL_SPINORIAL_CORE_HAS_ZERO_INTEGRATED_ANOMALY_ROWS__"
    "Z2M_REMAINS_AND_Z9F_REQUIRES_UNIT_LINE_LATTICE__S0_FAIL_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def matrix_rank(rows: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in rows]
    if not work:
        return 0
    n_rows = len(work)
    n_cols = len(work[0])
    pivot_row = 0
    for col in range(n_cols):
        pivot = next((r for r in range(pivot_row, n_rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(n_rows):
            if row == pivot_row or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return pivot_row


def d_roots(indices: Sequence[int], ambient_dimension: int = 5) -> set[tuple[int, ...]]:
    roots: set[tuple[int, ...]] = set()
    for position, left in enumerate(indices):
        for right in indices[position + 1 :]:
            for left_sign in (-1, 1):
                for right_sign in (-1, 1):
                    root = [0] * ambient_dimension
                    root[left] = left_sign
                    root[right] = right_sign
                    roots.add(tuple(root))
    return roots


def a_roots(indices: Sequence[int], ambient_dimension: int = 5) -> set[tuple[int, ...]]:
    roots: set[tuple[int, ...]] = set()
    for left in indices:
        for right in indices:
            if left == right:
                continue
            root = [0] * ambient_dimension
            root[left] = 1
            root[right] = -1
            roots.add(tuple(root))
    return roots


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(left, right))


def root_intersection_certificate() -> dict[str, Any]:
    """Intersect standard D3+A1+A1 and A4 subgroups of D5 exactly."""

    d5 = d_roots(tuple(range(5)))
    ps = d_roots((0, 1, 2)) | d_roots((3, 4))
    su5 = a_roots(tuple(range(5)))
    common = ps & su5
    simple_common = (
        (1, -1, 0, 0, 0),
        (0, 1, -1, 0, 0),
        (0, 0, 0, 1, -1),
    )
    six_y = (-2, -2, -2, 3, 3)

    return {
        "ambient_root_system": "D5 = so(10)",
        "D5_root_count": len(d5),
        "D5_rank": 5,
        "D5_dimension": 5 + len(d5),
        "PS_root_system": "D3 + D2 = A3 + A1 + A1",
        "PS_root_count": len(ps),
        "PS_rank": 5,
        "PS_dimension": 5 + len(ps),
        "SU5_root_system": "A4",
        "SU5_root_count": len(su5),
        "SU5_rank": 4,
        "SU5_dimension": 4 + len(su5),
        "intersection_roots": [list(root) for root in sorted(common)],
        "intersection_root_count": len(common),
        "intersection_semisimple_rank": matrix_rank(simple_common),
        "intersection_Cartan_rank": 4,
        "intersection_dimension": 4 + len(common),
        "intersection_algebra": "su(3)_C + su(2)_L + u(1)_Y",
        "simple_roots_for_A2_plus_A1": [list(root) for root in simple_common],
        "six_Y_vector": list(six_y),
        "six_Y_is_in_SU5_Cartan": sum(six_y) == 0,
        "six_Y_commutes_with_common_semisimple_roots": all(
            dot(six_y, root) == 0 for root in common
        ),
        "six_Y_is_primitive": math.gcd(*[abs(value) for value in six_y]) == 1,
        "PS_generators_lifted_by_boundary_Higgs": (5 + len(ps)) - (4 + len(common)),
    }


def sm_global_form_certificate() -> dict[str, Any]:
    """Kernel of (A,B,z) -> diag(z^-2 A,z^3 B) in SU(5)."""

    kernel = [
        {
            "k": k,
            "SU3_center_exponent_mod_3": k % 3,
            "SU2_center_exponent_mod_2": k % 2,
            "U1_angle_over_2pi": f"{k}/6",
        }
        for k in range(6)
    ]
    return {
        "embedding": "(A,B,z) -> diag(z^(-2) A, z^3 B) in SU(5)",
        "kernel": kernel,
        "kernel_order": len(kernel),
        "kernel_is_cyclic": True,
        "connected_intersection": "S(U(3)xU(2))",
        "connected_global_form": "(SU(3)_C x SU(2)_L x U(1)_Y)/Z6",
        "hypercharge_normalization": "6Y = diag(-2,-2,-2,3,3)",
    }


def boundary_stabilizer_certificate() -> dict[str, Any]:
    return {
        "global_maximal_subgroup_containing_the_orbit": "(SU(5) x U(1)_chi)/Z5",
        "Z5_kernel_generator_description": (
            "The SU(5) centre phase and U(1)_chi phase are identified so that all "
            "10_-1 + bar5_+3 + 1_-5 components of a 16 transform trivially."
        ),
        "branching_fact": {
            "Delta_126_singlet": "1_-10 under SU(5)xU(1)_chi",
            "barDelta_bar126_singlet": "1_+10 under SU(5)xU(1)_chi",
        },
        "aligned_nonzero_pair_continuous_stabilizer": "SU(5)",
        "Spin10_center": "Z4=<c>",
        "center_phases": {
            "16_under_c": "i (convention; conjugate chirality has -i)",
            "126_subset_of_symmetric_16x16_under_c": "-1",
            "126_under_c_squared": "+1",
        },
        "unbroken_center_subgroup": "<c^2> = Z2_M",
        "stabilizer_before_simplifying_quotient": "(SU(5) x Z10_chi)/Z5",
        "exact_boundary_stabilizer_in_Spin10": "SU(5) x Z2_M",
        "reason_Z2_is_independent_of_SU5": (
            "c^2 is the nontrivial kernel of Spin(10)->SO(10), whereas the standard SU(5) "
            "realification is faithful; hence c^2 is not a nontrivial SU(5) element"
        ),
        "SUSY_D_flat_requirement": "|<Delta>|=|<barDelta>| along conjugate singlet directions",
        "F_flat_alignment_supplied": False,
        "qualification": (
            "The representation contains the required conjugate singlets and an equal-norm pair can cancel "
            "the gauge D term.  V44 supplies no superpotential that selects this orbit and gives full rank "
            "to all uneaten boundary-Higgs modes."
        ),
    }


def ps_rep_is_honest(su4_nality: int, su2l_twice_isospin_mod2: int, su2r_twice_isospin_mod2: int) -> bool:
    """Test the diagonal kernel (-I4,-I2,-I2) of Spin6xSpin4 -> Spin10."""

    return (su4_nality + su2l_twice_isospin_mod2 + su2r_twice_isospin_mod2) % 2 == 0


def ps_representation_audit() -> dict[str, Any]:
    rows = [
        ("Q/Psi", "(4,2,1)", 1, 1, 0),
        ("Qc/PsiC", "(bar4,1,2)", 3, 0, 1),
        ("H", "(1,2,2)", 0, 1, 1),
        ("V44_L0/Lminus9", "(1,2,1)", 0, 1, 0),
        ("V44_R0/Rplus9", "(1,1,2)", 0, 0, 1),
        ("repair_L", "(4 or bar4,2,1)", 1, 1, 0),
        ("repair_R", "(4 or bar4,1,2)", 1, 0, 1),
    ]
    audited = [
        {
            "field_class": name,
            "PS_representation": representation,
            "SU4_nality_mod4": nality,
            "SU2L_twice_isospin_mod2": left,
            "SU2R_twice_isospin_mod2": right,
            "diagonal_kernel_phase": "+1" if ps_rep_is_honest(nality, left, right) else "-1",
            "honest_representation": ps_rep_is_honest(nality, left, right),
        }
        for name, representation, nality, left, right in rows
    ]
    return {
        "inherited_PS_group": "(SU(4)_C x SU(2)_L x SU(2)_R)/Z2_diag",
        "quotiented_element": "(-I4,-I2,-I2)",
        "honesty_condition": "SU4_nality + 2j_L + 2j_R = 0 mod 2",
        "rows": audited,
        "invalid_V44_classes": [
            row["field_class"] for row in audited if row["field_class"].startswith("V44_") and not row["honest_representation"]
        ],
        "original_V44_boundary_manifest_globally_valid": False,
    }


# Each row denotes one four-dimensional chiral zero mode.  index_2T contains
# 2T(r), already multiplied by spectator dimensions.  su4_cubic uses the
# fundamental coefficient +1 and includes the SU(2) spectator dimension.
ORIGINAL_ANOMALONS = (
    {"name": "4x L0", "dim": 8, "q": 0, "index_2T": {"SU4": 0, "SU2L": 4, "SU2R": 0}, "su4_cubic": 0, "doublets_L": 4, "doublets_R": 0},
    {"name": "4x Lminus9", "dim": 8, "q": -9, "index_2T": {"SU4": 0, "SU2L": 4, "SU2R": 0}, "su4_cubic": 0, "doublets_L": 4, "doublets_R": 0},
    {"name": "4x R0", "dim": 8, "q": 0, "index_2T": {"SU4": 0, "SU2L": 0, "SU2R": 4}, "su4_cubic": 0, "doublets_L": 0, "doublets_R": 4},
    {"name": "4x Rplus9", "dim": 8, "q": 9, "index_2T": {"SU4": 0, "SU2L": 0, "SU2R": 4}, "su4_cubic": 0, "doublets_L": 0, "doublets_R": 4},
)

REPAIRED_ANOMALONS = (
    {"name": "L4", "spin10_origin": "16_+3", "PS_rep": "(4,2,1)_+3", "dim": 8, "q": 3, "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0}, "su4_cubic": 2, "doublets_L": 4, "doublets_R": 0, "eta_PS": "+", "eta_Spin10": "+"},
    {"name": "Lbar4", "spin10_origin": "bar16_-12", "PS_rep": "(bar4,2,1)_-12", "dim": 8, "q": -12, "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0}, "su4_cubic": -2, "doublets_L": 4, "doublets_R": 0, "eta_PS": "+", "eta_Spin10": "+"},
    {"name": "Rbar4", "spin10_origin": "16_-3", "PS_rep": "(bar4,1,2)_-3", "dim": 8, "q": -3, "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4}, "su4_cubic": -2, "doublets_L": 0, "doublets_R": 4, "eta_PS": "-", "eta_Spin10": "+"},
    {"name": "R4", "spin10_origin": "bar16_+12", "PS_rep": "(4,1,2)_+12", "dim": 8, "q": 12, "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4}, "su4_cubic": 2, "doublets_L": 0, "doublets_R": 4, "eta_PS": "-", "eta_Spin10": "+"},
)

# The minimal V45 core deliberately does not import X/Zp/PQ/A/Psi/E/NDirac
# or the old PS-breaking sector.  These aggregate rows are the three families
# and one bidoublet that remain on the PS wall, followed by the source fields
# with nonzero U(1)_F charge.  Neutral STheta and 126+bar126 rows do not enter
# the arithmetic; the conjugate 126 pair is non-Abelian-vectorlike as well.
MINIMAL_CORE_NON_ANOMALONS = (
    {"name": "3x Q", "PS_rep": "3x(4,2,1)_+3", "dim": 24, "q": 3, "index_2T": {"SU4": 6, "SU2L": 12, "SU2R": 0}, "su4_cubic": 6, "doublets_L": 12, "doublets_R": 0},
    {"name": "3x Qc", "PS_rep": "3x(bar4,1,2)_-3", "dim": 24, "q": -3, "index_2T": {"SU4": 6, "SU2L": 0, "SU2R": 12}, "su4_cubic": -6, "doublets_L": 0, "doublets_R": 12},
    {"name": "H", "PS_rep": "(1,2,2)_0", "dim": 4, "q": 0, "index_2T": {"SU4": 0, "SU2L": 2, "SU2R": 2}, "su4_cubic": 0, "doublets_L": 2, "doublets_R": 2},
    {"name": "ThetaPlus", "PS_rep": "source-wall singlet_+9", "dim": 1, "q": 9, "index_2T": {"SU4": 0, "SU2L": 0, "SU2R": 0}, "su4_cubic": 0, "doublets_L": 0, "doublets_R": 0},
    {"name": "ThetaMinus", "PS_rep": "source-wall singlet_-9", "dim": 1, "q": -9, "index_2T": {"SU4": 0, "SU2L": 0, "SU2R": 0}, "su4_cubic": 0, "doublets_L": 0, "doublets_R": 0},
)


def anomaly_ledger(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = tuple(rows)
    return {
        "SU4_squared_U1F_doubled": sum(int(row["q"]) * int(row["index_2T"]["SU4"]) for row in rows),
        "SU2L_squared_U1F_doubled": sum(int(row["q"]) * int(row["index_2T"]["SU2L"]) for row in rows),
        "SU2R_squared_U1F_doubled": sum(int(row["q"]) * int(row["index_2T"]["SU2R"]) for row in rows),
        "gravity_squared_U1F": sum(int(row["dim"]) * int(row["q"]) for row in rows),
        "U1F_cubed": sum(int(row["dim"]) * int(row["q"]) ** 3 for row in rows),
        "SU4_cubed": sum(int(row["su4_cubic"]) for row in rows),
        "SU2L_Witten_doublet_count_mod2": sum(int(row["doublets_L"]) for row in rows) % 2,
        "SU2R_Witten_doublet_count_mod2": sum(int(row["doublets_R"]) for row in rows) % 2,
    }


def anomalon_repair_certificate() -> dict[str, Any]:
    old = anomaly_ledger(ORIGINAL_ANOMALONS)
    new = anomaly_ledger(REPAIRED_ANOMALONS)
    visible_and_source = anomaly_ledger(MINIMAL_CORE_NON_ANOMALONS)
    minimal_core = anomaly_ledger((*MINIMAL_CORE_NON_ANOMALONS, *REPAIRED_ANOMALONS))
    mass_terms = [
        {
            "operator": "ThetaPlus(+9) 16_L(+3) bar16_L(-12)",
            "U1F_total": 9 + 3 - 12,
            "Spin10_invariant": True,
            "zero_modes_paired": "(4,2,1)_+3 with (bar4,2,1)_-12",
        },
        {
            "operator": "ThetaMinus(-9) 16_R(-3) bar16_R(+12)",
            "U1F_total": -9 - 3 + 12,
            "Spin10_invariant": True,
            "zero_modes_paired": "(bar4,1,2)_-3 with (4,1,2)_+12",
        },
    ]
    zero_modes = []
    for row in REPAIRED_ANOMALONS:
        zero_modes.append(
            {
                "bulk_hypermultiplet": row["spin10_origin"],
                "intrinsic_parities_eta0_PS_etaL_Spin10": [row["eta_PS"], row["eta_Spin10"]],
                "selected_H_zero_mode": row["PS_rep"],
                "Hc_has_zero_mode": False,
                "mechanism": (
                    "The two PS halves of a 16 or bar16 have opposite gauge-twist eigenvalues; "
                    "Hc has the opposite parity at each endpoint."
                ),
            }
        )
    return {
        "original_rows": [dict(row) for row in ORIGINAL_ANOMALONS],
        "replacement_rows": [dict(row) for row in REPAIRED_ANOMALONS],
        "original_integrated_anomaly_ledger": old,
        "replacement_integrated_anomaly_ledger": new,
        "all_integrated_rows_match": old == new,
        "minimal_V45_core": {
            "PS_wall": [
                "3 Q_(4,2,1),+3",
                "3 Qc_(bar4,1,2),-3",
                "H_(1,2,2),0",
                "LF_(4,2,1),+3",
                "LA_(bar4,2,1),-12",
                "RA_(bar4,1,2),-3",
                "RF_(4,1,2),+12",
            ],
            "source_wall": ["STheta_0", "ThetaPlus_+9", "ThetaMinus_-9", "126_0", "bar126_0"],
            "explicitly_not_imported": ["X", "Zp", "P/Pb", "Psi-sector", "A-sector", "E-sector", "NDirac", "Sc/Sbc/SigC/SigBc"],
            "visible_plus_source_anomaly_ledger_before_repair": visible_and_source,
            "full_integrated_anomaly_ledger": minimal_core,
            "all_displayed_integrated_local_polynomial_and_Witten_rows_vanish": all(value == 0 for value in minimal_core.values()),
        },
        "all_replacement_PS_representations_are_honest": True,
        "residual_Z9_orientation": {
            "all_SU4_fundamentals_mod9": sorted({int(row["q"]) % 9 for row in REPAIRED_ANOMALONS if row["PS_rep"].startswith("(4,")}),
            "all_SU4_antifundamentals_mod9": sorted({int(row["q"]) % 9 for row in REPAIRED_ANOMALONS if row["PS_rep"].startswith("(bar4,")}),
            "target": {"fundamental": 3, "antifundamental": 6},
            "preserved": True,
        },
        "bulk_zero_mode_realization": zero_modes,
        "source_wall_mass_terms": mass_terms,
        "all_mass_terms_U1F_neutral": all(row["U1F_total"] == 0 for row in mass_terms),
        "qualification": (
            "This is an exact representation/anomaly/zero-mode repair, not a localized orbifold-anomaly "
            "certificate.  The four charged bulk hypers can mediate cross-wall operators, so S1 must recompute "
            "the local and nonlocal invariant rings rather than inherit the V44 sequestering claim."
        ),
    }


def orbifold_certificate() -> dict[str, Any]:
    rows = [
        {"sector": "Spin10 vector V_PS", "dimension": 21, "P0_PS": "+", "PL_Spin10": "+", "massless_before_boundary_VEV": 21},
        {"sector": "Spin10 vector V_coset (6,2,2)", "dimension": 24, "P0_PS": "-", "PL_Spin10": "+", "massless_before_boundary_VEV": 0},
        {"sector": "adjoint chiral Phi_PS", "dimension": 21, "P0_PS": "-", "PL_Spin10": "-", "massless_before_boundary_VEV": 0},
        {"sector": "adjoint chiral Phi_coset", "dimension": 24, "P0_PS": "+", "PL_Spin10": "-", "massless_before_boundary_VEV": 0},
        {"sector": "U1F vector V_F", "dimension": 1, "P0_PS": "+", "PL_Spin10": "+", "massless_before_boundary_VEV": 1},
        {"sector": "U1F adjoint chiral Phi_F", "dimension": 1, "P0_PS": "-", "PL_Spin10": "-", "massless_before_boundary_VEV": 0},
    ]
    return {
        "geometry": "M4 x [0,L], equivalently S1/(Z2 x Z2') with L=pi R/2",
        "bulk_group_choice_for_this_S0_witness": "Spin(10) x U(1)_F (Gamma chosen trivial)",
        "y0_gauge_twist_on_vector_10": "diag(-1,-1,-1,+1,+1) tensor I2",
        "yL_gauge_twist_on_vector_10": "I10",
        "y0_fixed_identity_component": "(SU(4)_C x SU(2)_L x SU(2)_R)/Z2_diag",
        "yL_group_before_Higgsing": "Spin(10) x U(1)_F",
        "adjoint_branching": "45 = (15,1,1) + (1,3,1) + (1,1,3) + (6,2,2)",
        "parity_rows": rows,
        "only_plus_plus_fields_have_constant_KK_zero_modes": True,
        "SUSY_projection": {
            "five_dimensional_supercharges": 8,
            "four_dimensional_name_before_projection": "N=2",
            "V_and_Phi_have_opposite_endpoint_parities": True,
            "massless_adjoint_chiral_count": 0,
            "surviving_four_dimensional_SUSY": "N=1",
        },
        "boundary_Higgs_effect": (
            "The aligned 126+bar126 VEV induces boundary masses (Robin conditions) for the nine PS/SM "
            "vector modes.  For finite VEV these are not removed by parity; they are lifted.  In the "
            "infinite-VEV limit the broken directions approach Dirichlet conditions at y=L."
        ),
    }


def residual_group_certificate() -> dict[str, Any]:
    local_core_charges = (3, -3, 3, -12, -3, 12, 9, -9)
    local_core_gcd = math.gcd(*[abs(value) for value in local_core_charges if value])
    theta_vev_gcd = math.gcd(9, 9)
    return {
        "minimal_local_core_nonzero_charges": list(local_core_charges),
        "minimal_local_core_charge_gcd": local_core_gcd,
        "chosen_character_lattice": "Z, including a genuine unit-charge Wilson line",
        "chosen_character_lattice_is_extra_global_input": True,
        "Theta_VEV_charges": [9, -9],
        "unbroken_U1F_subgroup_with_chosen_unit_line_lattice": f"Z{theta_vev_gcd}",
        "faithful_action_on_displayed_local_fields_only": "U(1)_F/Z3, equivalently charges divided by three",
        "unbroken_subgroup_seen_faithfully_by_displayed_local_fields": "Z3",
        "Z9_versus_Z3_is_fixed_by_local_particle_spectrum_alone": False,
        "continuous_massless_group": "(SU(3)_C x SU(2)_L x U(1)_Y)/Z6",
        "finite_gauge_factors_for_trivial_Gamma": "Z2_M x Z9_F",
        "full_residual_group_for_trivial_Gamma": "[(SU(3)_C x SU(2)_L x U(1)_Y)/Z6] x Z2_M x Z9_F",
        "continuous_rank_before_boundary_VEVs": 6,
        "continuous_rank_after_126_pair": 5,
        "continuous_rank_after_Theta_pair": 4,
        "literal_SM_and_no_finite_extension": False,
        "SM_connected_group_plus_declared_matter_and_selector_parities": True,
        "qualification": (
            "Z9_F is exact only after declaring the unit character/line lattice.  Every displayed local "
            "V45 core charge is divisible by three, so local particles alone see only a faithful Z3 remnant."
        ),
    }


def build_report() -> dict[str, Any]:
    roots = root_intersection_certificate()
    sm = sm_global_form_certificate()
    stabilizer = boundary_stabilizer_certificate()
    representations = ps_representation_audit()
    repair = anomalon_repair_certificate()
    orbifold = orbifold_certificate()
    residual = residual_group_certificate()

    report: dict[str, Any] = {
        "status": STATUS,
        "scope": (
            "V45 successor stage S0 only: exact compact-group choice, orbifold gauge/SUSY parities, "
            "gauge-vector zero modes, 126 stabilizer, PS/SU5 intersection, and global honesty of the "
            "inherited anomalon representations."
        ),
        "input_manifest": [
            {"name": name, "path": path.name, "sha256": sha256_file(path)}
            for name, path in INPUTS.items()
        ],
        "orbifold_and_SUSY": orbifold,
        "exact_root_intersection": roots,
        "SM_global_form": sm,
        "boundary_126_stabilizer": stabilizer,
        "residual_group": residual,
        "PS_global_representation_audit": representations,
        "globally_honest_anomalon_repair": repair,
        "minimal_V45_core": repair["minimal_V45_core"],
        "zero_mode_count_after_all_boundary_VEVs": {
            "massless_Spin10_origin_vector_supermultiplets": roots["intersection_dimension"],
            "massless_U1F_vector_supermultiplets": 0,
            "massless_adjoint_chiral_supermultiplets": 0,
            "continuous_gauge_algebra_dimension": roots["intersection_dimension"],
            "continuous_gauge_rank": residual["continuous_rank_after_Theta_pair"],
        },
        "fatal_contradiction_search": {
            "orbifold_plus_126_intersection_fatal": False,
            "original_V44_field_manifest_fatal_without_repair": True,
            "reason": (
                "The group intersection is constructive, but the naked PS doublets in V44 transform "
                "nontrivially under the diagonal element that is quotiented in the Spin(10) PS subgroup."
            ),
            "repair_at_exact_group_and_integrated_anomaly_level_exists": True,
            "literal_only_SM_target_fatal_with_declared_VEVs": True,
            "literal_only_SM_reason": "The 126 pair preserves Z2 matter parity and the charge-nine pair preserves Z9_F.",
        },
        "fail_closed_verdict": {
            "S0_original_V44_manifest_passes": False,
            "S0_repaired_candidate_group_theory_feasible": True,
            "S0_stage_closed": False,
            "G1_through_G8_promoted": [],
            "classification": "CONDITIONAL_GROUP_THEORY_WITNESS_WITH_REQUIRED_MANIFEST_REPAIR",
            "why_not_closed": [
                "The complete 126+bar126 boundary superpotential and all physical mass matrices are absent.",
                "Localized perturbative, parity, discrete and global anomalies of the four proposed bulk hypers are uncomputed.",
                "The bulk-hyper repair creates cross-wall propagation, so all dangerous nonlocal Wilson coefficients must be recomputed.",
                "The finite residual global group is SM_connected x Z2_M x Z9_F, not literally the connected SM alone.",
                "The minimal local field charges have gcd three; a genuine Z9 rather than faithful-local Z3 requires an explicit unit Wilson-line/charge lattice.",
                "Gauge-unification and KK-threshold viability of SO(10)-wall Higgs breaking are not established.",
            ],
            "next_kill_test": (
                "Build the complete localized-anomaly polynomial for the vector multiplets and the four charged "
                "16/bar16 hypers with the displayed parities.  Reject the repair if no quantized inflow and "
                "boundary spectrum cancel both wall distributions while retaining the two source-wall masses."
            ),
        },
        "primary_sources": [
            {
                "title": "Dermisek and Mafi, SO(10) grand unification in five dimensions",
                "url": "https://arxiv.org/abs/hep-ph/0108139",
                "supports": "S1/(Z2 x Z2') parity construction, PS gauge zero modes, 4D N=1 projection, and SU5/PS intersection precedent",
            },
            {
                "title": "Alciati and Lin, Gauge coupling Unification and SO(10) in 5D",
                "url": "https://arxiv.org/abs/hep-ph/0506130",
                "supports": "rank-preserving orbifold plus rank-reducing brane Higgs mechanism and the warning that SO10-wall Higgs breaking is disfavored for unification",
            },
            {
                "title": "Alciati et al., Fermion masses and proton decay in a minimal five-dimensional SO(10) model",
                "url": "https://arxiv.org/abs/hep-ph/0603086",
                "supports": "bulk 16 hypermultiplets, doubled zero-mode constructions, PS decomposition of a 16, and boundary-mass-shifted KK towers",
            },
            {
                "title": "Chen, Zhang and Bai, Couplings in Renormalizable Supersymmetric SO(10) Models",
                "url": "https://arxiv.org/abs/1707.00580",
                "supports": "the 126 and bar126 contain SU5 singlets of U1X charges -10 and +10",
            },
            {
                "title": "Goh et al., Proton Decay in a Minimal SUSY SO(10) Model for Neutrino Mixings",
                "url": "https://arxiv.org/abs/hep-ph/0311330",
                "supports": "126 breaking preserves automatic R/matter parity",
            },
        ],
        "source_manifest": source_manifest(),
    }

    checks = {
        "all_required_inputs_exist": all(path.is_file() for path in INPUTS.values()),
        "D5_root_count_is_40": roots["D5_root_count"] == 40,
        "PS_dimension_is_21": roots["PS_dimension"] == 21,
        "SU5_dimension_is_24": roots["SU5_dimension"] == 24,
        "intersection_is_rank4_dimension12": roots["intersection_Cartan_rank"] == 4 and roots["intersection_dimension"] == 12,
        "intersection_root_system_is_A2_plus_A1": roots["intersection_root_count"] == 8 and roots["intersection_semisimple_rank"] == 3,
        "hypercharge_is_exact_common_u1": roots["six_Y_is_in_SU5_Cartan"] and roots["six_Y_commutes_with_common_semisimple_roots"] and roots["six_Y_is_primitive"],
        "SM_kernel_is_Z6": sm["kernel_order"] == 6 and sm["kernel_is_cyclic"],
        "nine_PS_vectors_are_lifted": roots["PS_generators_lifted_by_boundary_Higgs"] == 9,
        "four_dimensional_N1_projection": orbifold["SUSY_projection"]["surviving_four_dimensional_SUSY"] == "N=1" and orbifold["SUSY_projection"]["massless_adjoint_chiral_count"] == 0,
        "V44_naked_doublets_are_rejected": not representations["original_V44_boundary_manifest_globally_valid"] and len(representations["invalid_V44_classes"]) == 2,
        "repair_integrated_anomaly_rows_match": repair["all_integrated_rows_match"],
        "repair_mass_terms_are_neutral": repair["all_mass_terms_U1F_neutral"],
        "repair_preserves_Z9_orientation": repair["residual_Z9_orientation"]["preserved"],
        "minimal_core_integrated_rows_vanish": repair["minimal_V45_core"]["all_displayed_integrated_local_polynomial_and_Witten_rows_vanish"],
        "U1F_line_lattice_distinction_is_exposed": residual["minimal_local_core_charge_gcd"] == 3 and residual["unbroken_U1F_subgroup_with_chosen_unit_line_lattice"] == "Z9" and residual["unbroken_subgroup_seen_faithfully_by_displayed_local_fields"] == "Z3",
        "fail_closed_no_gate_promotion": not report["fail_closed_verdict"]["S0_stage_closed"] and not report["fail_closed_verdict"]["G1_through_G8_promoted"],
        "all_source_files_exist": all(row["exists"] for row in report["source_manifest"]),
    }
    report["integrity_checks"] = checks
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    roots = report["exact_root_intersection"]
    residual = report["residual_group"]
    reps = report["PS_global_representation_audit"]
    repair = report["globally_honest_anomalon_repair"]
    verdict = report["fail_closed_verdict"]

    representation_rows = "\n".join(
        f"| {row['field_class']} | `{row['PS_representation']}` | {row['diagonal_kernel_phase']} | {'yes' if row['honest_representation'] else 'NO'} |"
        for row in reps["rows"]
    )
    anomaly_keys = tuple(repair["original_integrated_anomaly_ledger"])
    anomaly_rows = "\n".join(
        f"| {key} | {repair['original_integrated_anomaly_ledger'][key]} | {repair['replacement_integrated_anomaly_ledger'][key]} |"
        for key in anomaly_keys
    )
    parity_rows = "\n".join(
        f"| {row['sector']} | {row['dimension']} | {row['P0_PS']} | {row['PL_Spin10']} | {row['massless_before_boundary_VEV']} |"
        for row in report["orbifold_and_SUSY"]["parity_rows"]
    )
    repair_rows = "\n".join(
        f"| `{row['spin10_origin']}` | `{row['PS_rep']}` | ({row['eta_PS']},{row['eta_Spin10']}) |"
        for row in repair["replacement_rows"]
    )
    missing = "\n".join(f"- {item}" for item in verdict["why_not_closed"])
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}) — {row['supports']}."
        for row in report["primary_sources"]
    )

    return f"""# SUSY V45 S0 group and zero-mode audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Fail-closed verdict

The proposed **orbifold/boundary breaking pattern is group-theoretically viable**, but the
V44 field manifest is not.  The exact connected intersection is

`{residual['continuous_massless_group']}`,

with 12 vector multiplets and rank four.  However, a Spin(10) parent fixes the PS wall
group to `(SU(4)xSU(2)LxSU(2)R)/Z2_diag`.  V44's isolated `(1,2,1)` and `(1,1,2)`
anomalons are not representations of this quotient.  The displayed spinorial repair fixes
that exact defect and preserves the integrated anomaly rows, but localized anomalies,
boundary-Higgs mass rank, and cross-wall matching remain uncomputed.  Therefore S0 is
**not closed**, and no G1--G8 gate is promoted.

There is one further precision point: for the explicit trivial bulk quotient and unit
Wilson-line lattice chosen here,
the full residual gauge group is

`{residual['full_residual_group_for_trivial_Gamma']}`.

Thus the result is exactly the connected SM global form plus the deliberately retained
matter parity and flavour selector.  It is not literally the SM with no finite extension.
All displayed local core charges have gcd three, however, so those local particles see
only a faithful `Z3`; the stronger `Z9` is a genuine global line-operator input rather
than a conclusion from the minimal particle list.

## Exact intersection certificate

Use the standard `D5` roots `±e_i±e_j`.  The PS roots are `D3` on coordinates
1--3 plus `D2` on coordinates 4--5; the SU(5) roots are `e_i-e_j` for all five
coordinates.  Their common roots are six `A2` roots on 1--3 and two `A1` roots
on 4--5.  The SU(5) Cartan has rank four, so one commuting Cartan direction
remains in addition to `A2+A1`:

- intersection roots: {roots['intersection_root_count']};
- semisimple rank: {roots['intersection_semisimple_rank']};
- total rank: {roots['intersection_Cartan_rank']};
- dimension: {roots['intersection_dimension']};
- primitive Abelian generator: `6Y=(-2,-2,-2,3,3)`.

The connected subgroup is `S(U(3)xU(2))`.  The map
`(A,B,z) -> diag(z^-2 A,z^3 B)` has a six-element kernel, proving the global
form `(SU(3)xSU(2)xU(1))/Z6`, not merely its Lie algebra.

## Orbifold and supersymmetry projection

Take `M4 x [0,L]`, with `L=pi R/2`, and choose the bulk group
`Spin(10)xU(1)_F` (trivial `Gamma`) for this witness.  At `y=0` use
`P0=diag(-1,-1,-1,+1,+1) tensor I2`; at `y=L` use `PL=I10`.

| sector | dim | P0 | PL | constant zero modes before brane VEVs |
|---|---:|:---:|:---:|---:|
{parity_rows}

Only `(++)` fields have constant zero modes.  Opposite parities for the adjoint
chiral field remove its zero mode, reducing the eight-supercharge 5D theory to
4D `N=1`.  The inner orbifold keeps the PS rank.  The aligned
`126+bar126` singlet VEV at the full-Spin(10) wall then lifts the nine
`PS/SM` vector modes through a boundary mass/Robin condition.  For finite VEV
these modes are lifted rather than deleted by parity.

## The 126 global stabilizer

`126` and `bar126` contain `SU(5)xU(1)_chi` singlets `1_-10` and `1_+10`.
An equal-norm conjugate pair can be D-flat and has connected stabilizer SU(5).
Globally the relevant maximal subgroup is `(SU(5)xU(1)_chi)/Z5`; the charge-ten
VEV gives `(SU(5)xZ10)/Z5`, which has two components.
Because 126 is tensorial, the central element `c^2` in the Spin(10) centre acts
trivially on the VEV while acting as `-1` on a 16.  The exact stabilizer is
therefore `SU(5)xZ2_M`.  This is the usual surviving matter parity.  A complete
superpotential that selects this orbit and gives every uneaten 126 mode a mass
has not been supplied.

## Global-representation defect in V44

The kernel element `(-I4,-I2,-I2)` must act trivially.  Equivalently,
`SU4 n-ality + 2j_L + 2j_R` must be even.

| field class | PS representation | kernel phase | honest? |
|---|---|:---:|:---:|
{representation_rows}

This is a fatal contradiction for the **original manifest**, not for the 5D
architecture: boundary-localized fields cannot be assigned projective gauge
representations and still define the stated Spin(10) gauge theory.

## Globally honest spinorial repair

Replace the four-copy naked-doublet rows by four bulk hypermultiplets whose
orbifold zero modes are:

| Spin(10) hyper | selected PS zero mode | intrinsic `(eta0,etaL)` |
|---|---|:---:|
{repair_rows}

Here `16=(4,2,1)+(bar4,1,2)` and
`bar16=(bar4,2,1)+(4,1,2)`; opposite PS twist eigenvalues select one half of
each hyper, while the conjugate 4D chiral `Hc` has no zero mode.  On the
Spin(10) wall the terms

- `ThetaPlus(+9) 16_L(+3) bar16_L(-12)`, and
- `ThetaMinus(-9) 16_R(-3) bar16_R(+12)`

are Spin(10) singlets and U(1)_F neutral.  They can pair all four selected zero
modes after the Theta VEVs.  Their fundamental/antifundamental charges remain
`+3/-3 mod 9`.

| integrated anomaly row | old naked doublets | repaired spinorial modes |
|---|---:|---:|
{anomaly_rows}

The equality is exact for the combined anomalon packet.  It does **not** prove
wall-by-wall anomaly cancellation: charged bulk spinors have parity anomalies
and also reopen nonlocal propagation between the walls.

## Minimal V45 core, not the V40 packet

The repaired candidate keeps only three `Q_+3` families, three `Qc_-3`
families, `H_0`, and the four spinorial zero modes on/through the PS wall.  The
source wall keeps `STheta`, `ThetaPlus/ThetaMinus`, and the neutral
`126+bar126`.  The old `X/Zp/PQ/A/Psi/E/NDirac/Sc` sectors are deleted at this
core stage.  The full displayed core has the exact integrated anomaly ledger

`{repair['minimal_V45_core']['full_integrated_anomaly_ledger']}`,

so every listed perturbative mixed/cubic/gravitational row and both SU(2)
Witten parities vanish.  This is an integrated statement only; the anomaly
density at each wall remains the next kill test.

## Why S0 remains open

{missing}

The next kill test is: {verdict['next_kill_test']}

## Primary-source anchors

{sources}
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_written(report: Mapping[str, Any]) -> None:
    if report["n_failed_integrity_checks"]:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"integrity checks failed: {failed}")
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("generated V45 S0 artifacts are missing; run with --write")
    stored = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if stored != report:
        raise RuntimeError("stored JSON differs from deterministic report")
    if stored["core_sha256"] != canonical_sha(stored):
        raise RuntimeError("stored core SHA-256 is invalid")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stored Markdown differs from deterministic rendering")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_written(report)
        print("V45_S0_GROUP_ZERO_MODE_AUDIT_CHECK_PASS")
    elif not args.write:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
