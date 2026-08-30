#!/usr/bin/env python3
"""Conditional protection-layer audit for the V56 6D SO(10) orbifold.

This artifact does not claim a completed six-dimensional theory.  It tests a
specific topology-changing candidate using conventional four-dimensional
N=1 bookkeeping: R(H)=0, R(Hc)=2, and the transverse derivative is neutral.
The bulk Hc*D_perp*H term then has superpotential charge two while a direct
H*H' mass has charge zero.  A higher-dimensional/geometric origin for this
Z4^R is only a candidate assumption, not a proved spin-bundle construction.
The exact result is restricted to the declared non-derivative R0-R0 operator
ring.  H-Hc boundary terms, normal-derivative operators, the discrete-gauge
lift, localized anomalies, the Green--Schwarz sector, thresholds, and the UV
completion remain explicit obligations.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v56_orbifold_geometric_z4r_protection_audit.py"
V55_PATH = ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.json"
V56_ARCH_PATH = ROOT / "SUSY_V56_ARCHITECTURE_ESCAPE_RESEARCH_AUDIT.json"

EXPECTED_V55_CORE = (
    "52d0044e8d227be29b2cab63c565c1f4335aae9a72c9d51f3c9044fe7289a1f7"
)
EXPECTED_V56_ARCH_CORE = (
    "3f3f662cdb8ba0e1081dc77fa2d579fef7c5421b97ca7b16fdce0760f796af0a"
)

STATUS = (
    "V56_6D_ORBIFOLD_Z4R_PROTECTION__V55_AND_V56_ARCHITECTURE_"
    "CORES_BOUND__TWO_WEAK_ZERO_MODES_AND_ZERO_COLORED_ZERO_MODES__"
    "NONDERIVATIVE_R0_R0_HIGGS_MASSES_FORBIDDEN_TO_ALL_R0_VEV_ORDERS__YUKAWA_"
    "AND_MAJORANA_ALLOWED__SOFT_R_BREAKING_MU_ROUTE_IDENTIFIED__BULK_"
    "IRREDUCIBLE_GAUGE_ANOMALY_CANCELS__HIGHER_DIMENSIONAL_ORIGIN_DERIVATIVE_BRANE_"
    "LOCALIZED_ANOMALY_GS_THRESHOLD_AND_UV_OBLIGATIONS_OPEN__ZERO_GATE_"
    "PROMOTIONS"
)

MODULUS = 4
SUPERPOTENTIAL_CHARGE = 2


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


def load_bound(path: Path, expected_core: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing bound {label} input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"bound {label} JSON has a stale canonical core")
    if actual != expected_core:
        raise RuntimeError(
            f"unexpected {label} core: expected {expected_core}, got {actual}"
        )
    return value


def component_parities(p1: int, p2: int) -> dict[str, tuple[int, int]]:
    """Published 10-plet translation parity pattern used by the V56 audit."""

    if p1 not in (-1, 1) or p2 not in (-1, 1):
        raise ValueError("translation parities must be +/-1")
    return {
        "h3": (p1, p2),
        "h2": (p1, -p2),
        "bar_h3": (-p1, -p2),
        "bar_h2": (-p1, p2),
    }


def local_reflection_signs(base: int, t1: int, t2: int) -> dict[str, int]:
    """Local Z2 signs at the four fixed points of T2/Z2."""

    return {
        "O_SO10": base,
        "O_GG": base * t1,
        "O_flipped": base * t2,
        "O_PS": base * t1 * t2,
    }


def lowest_equal_radius_mass2(base: int, t1: int, t2: int) -> Fraction:
    """Lowest m^2 R^2 for a free parity tower on an equal-radius torus.

    Translation-odd fields have half-integer momentum.  For a translation-even
    but reflection-odd field, the constant wavefunction is removed and the
    first sine combination has m^2 R^2=1.  This is a tower-level diagnostic,
    not the determinant after boundary interactions.
    """

    shifts = [Fraction(0) if sign == 1 else Fraction(1, 2) for sign in (t1, t2)]
    value = shifts[0] ** 2 + shifts[1] ** 2
    if value == 0 and base == -1:
        return Fraction(1)
    return value


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def orbifold_mode_certificate() -> dict[str, Any]:
    hypers = {"H10": (1, -1), "H10_prime": (-1, 1)}
    ledger: list[dict[str, Any]] = []
    for hyper, intrinsic in hypers.items():
        for component, (t1, t2) in component_parities(*intrinsic).items():
            for chiral, base in (("H", 1), ("Hc", -1)):
                local = local_reflection_signs(base, t1, t2)
                zero = base == 1 and t1 == 1 and t2 == 1
                kind = "weak_doublet" if "h2" in component else "color_triplet"
                ledger.append(
                    {
                        "hypermultiplet": hyper,
                        "four_dimensional_chiral": chiral,
                        "component": component,
                        "SM_kind": kind,
                        "base_reflection": base,
                        "translation_parities": [t1, t2],
                        "fixed_point_local_signs": local,
                        "fixed_point_support": [name for name, sign in local.items() if sign == 1],
                        "has_massless_zero_mode": zero,
                        "lowest_free_m2_R2_equal_radii": fraction_text(
                            lowest_equal_radius_mass2(base, t1, t2)
                        ),
                    }
                )

    zero_rows = [row for row in ledger if row["has_massless_zero_mode"]]
    gg_support = [row for row in ledger if "O_GG" in row["fixed_point_support"]]
    desired_zero_ids = {
        "H10:H:h2",
        "H10_prime:H:bar_h2",
    }
    return {
        "geometry": "T^2/Z2 with two independent SO(10) translation twists",
        "hypermultiplet_intrinsic_translation_choices": {
            name: list(values) for name, values in hypers.items()
        },
        "fixed_point_groups": {
            "O_SO10": "SO(10)",
            "O_GG": "SU(5) x U(1)X",
            "O_flipped": "flipped SU(5)' x U(1)'X",
            "O_PS": "SU(4)C x SU(2)L x SU(2)R",
        },
        "component_ledger": ledger,
        "zero_modes": [
            f"{row['hypermultiplet']}:{row['four_dimensional_chiral']}:{row['component']}"
            for row in zero_rows
        ],
        "weak_doublet_zero_mode_count": sum(
            row["SM_kind"] == "weak_doublet" for row in zero_rows
        ),
        "color_triplet_zero_mode_count": sum(
            row["SM_kind"] == "color_triplet" for row in zero_rows
        ),
        "conjugate_Hc_zero_mode_count": sum(
            row["four_dimensional_chiral"] == "Hc" for row in zero_rows
        ),
        "GG_brane_support_result": {
            "H_component_count": sum(
                row["four_dimensional_chiral"] == "H" for row in gg_support
            ),
            "Hc_component_count": sum(
                row["four_dimensional_chiral"] == "Hc" for row in gg_support
            ),
            "desired_doublet_zero_modes_supported": all(
                any(
                    f"{row['hypermultiplet']}:{row['four_dimensional_chiral']}:{row['component']}" == zero_id
                    and "O_GG" in row["fixed_point_support"]
                    for row in ledger
                )
                for zero_id in desired_zero_ids
            ),
            "Higgs_representations_used": [
                "H10:H:(h3,h2) = 5_(+2)",
                "H10_prime:H:(bar_h3,bar_h2) = bar5_(-2)",
            ],
            "meaning": (
                "Both desired doublets and their massive color partners are "
                "supported at the SU(5)xU(1)X fixed point. Complementary Hc "
                "components also have local support, but q(Hc)=2 forbids their "
                "Yukawa coupling to two q=1 matter fields."
            ),
        },
        "scope": (
            "Exact for the free translation/reflection projector. Boundary quadratic "
            "operators can change the KK determinant and are audited separately."
        ),
    }


R_CHARGES = {
    "theta": 1,
    "W_alpha": 1,
    "D_perp": 0,
    "Sigma": 0,
    "H": 0,
    "Hp": 0,
    "Hc": 2,
    "Hpc": 2,
    "T10": 1,
    "Fbar5": 1,
    "N1": 1,
    "X": 0,
    "Xbar": 0,
    "S": 2,
    "constant": 0,
}


def operator_charge(factors: Sequence[str]) -> int:
    return sum(R_CHARGES[field] for field in factors) % MODULUS


def operator_row(
    operator_id: str,
    factors: Sequence[str],
    expected_allowed: bool,
    role: str,
    support: str,
    caveat: str = "",
) -> dict[str, Any]:
    charge = operator_charge(factors)
    allowed = charge == SUPERPOTENTIAL_CHARGE
    return {
        "id": operator_id,
        "factors": list(factors),
        "R_charge_mod4": charge,
        "superpotential_allowed_by_Z4R": allowed,
        "expected_allowed": expected_allowed,
        "selector_matches_expectation": allowed == expected_allowed,
        "role": role,
        "support": support,
        "caveat": caveat,
    }


def r_symmetry_certificate() -> dict[str, Any]:
    rows = [
        operator_row("gauge_kinetic", ["W_alpha", "W_alpha"], True, "required", "bulk"),
        operator_row("bulk_H", ["Hc", "D_perp", "H"], True, "required", "bulk"),
        operator_row("bulk_H_gauge", ["Hc", "Sigma", "H"], True, "required", "bulk"),
        operator_row("bulk_Hp", ["Hpc", "D_perp", "Hp"], True, "required", "bulk"),
        operator_row("bulk_Hp_gauge", ["Hpc", "Sigma", "Hp"], True, "required", "bulk"),
        operator_row("up_Yukawa", ["T10", "T10", "H"], True, "required", "O_GG"),
        operator_row("down_lepton_Yukawa", ["T10", "Fbar5", "Hp"], True, "required", "O_GG"),
        operator_row(
            "right_neutrino_Majorana",
            ["N1", "N1", "X"],
            True,
            "required",
            "O_GG",
        ),
        operator_row("rank_breaking_driver", ["S", "X", "Xbar"], True, "required", "O_GG"),
        operator_row("rank_breaking_linear", ["S", "constant"], True, "required", "O_GG"),
        operator_row(
            "soft_mu_parent",
            ["S", "H", "Hp"],
            True,
            "required",
            "O_GG",
            "It is harmless at the supersymmetric vacuum only if <S>=0.",
        ),
        operator_row("direct_H_Hp_mass", ["H", "Hp"], False, "must_forbid", "any brane or bulk"),
        operator_row("direct_H_H_mass", ["H", "H"], False, "must_forbid", "any brane or bulk"),
        operator_row("direct_Hp_Hp_mass", ["Hp", "Hp"], False, "must_forbid", "any brane or bulk"),
        operator_row(
            "boundary_Hc_H",
            ["Hc", "H"],
            True,
            "unresolved_but_bipartite",
            "fixed points with both local components",
            "It changes boundary conditions but occupies the H-Hc block, not Hc-Hc.",
        ),
        operator_row(
            "boundary_Hc_Hp",
            ["Hc", "Hp"],
            True,
            "unresolved_but_bipartite",
            "fixed points with both local components",
        ),
        operator_row(
            "boundary_Hpc_H",
            ["Hpc", "H"],
            True,
            "unresolved_but_bipartite",
            "fixed points with both local components",
        ),
        operator_row(
            "boundary_Hpc_Hp",
            ["Hpc", "Hp"],
            True,
            "unresolved_but_bipartite",
            "fixed points with both local components",
        ),
        operator_row("direct_Hc_Hpc_mass", ["Hc", "Hpc"], False, "must_forbid", "any brane"),
        operator_row(
            "soft_Hc_Hpc_parent",
            ["S", "Hc", "Hpc"],
            True,
            "controlled_after_R_breaking",
            "O_GG",
            "After <S> this supplies the Hc-Hc block and gives C5 proportional to <S>/Mc^2.",
        ),
        operator_row("direct_X_Xbar_mass", ["X", "Xbar"], False, "controlled_by_S", "O_GG"),
        operator_row("matter_Higgs_mixing", ["Fbar5", "H"], False, "must_forbid", "O_GG"),
        operator_row("up_Yukawa_to_Hpc", ["T10", "T10", "Hpc"], False, "must_forbid", "O_GG"),
        operator_row("down_Yukawa_to_Hc", ["T10", "Fbar5", "Hc"], False, "must_forbid", "O_GG"),
        operator_row("renormalizable_RPV_proxy", ["T10", "Fbar5", "Fbar5"], False, "must_forbid", "O_GG"),
        operator_row("dimension5_proton_proxy", ["T10", "T10", "T10", "Fbar5"], False, "must_forbid", "O_GG"),
        operator_row(
            "R_broken_dimension5_proton_parent",
            ["S", "T10", "T10", "T10", "Fbar5"],
            True,
            "controlled_after_R_breaking",
            "O_GG",
        ),
        operator_row(
            "normal_derivative_boundary_loophole",
            ["H", "D_perp", "Hc"],
            True,
            "unresolved",
            "fixed points where the differentiated odd profile is nonzero",
            "Z4R alone does not eliminate normal-derivative H-Hc boundary operators.",
        ),
    ]
    return {
        "bookkeeping_convention": (
            "Conventional 4D N=1 charges: q(theta)=1, q(H)=0, q(Hc)=2, "
            "q(D_perp)=q(Sigma)=0. This must not be mixed with a convention "
            "that assigns geometric charge to D_perp."
        ),
        "charge_ledger": R_CHARGES,
        "superpotential_selection_rule": "sum(q_R)=2 mod 4",
        "operator_ledger": rows,
        "all_selector_expectations_met": all(
            row["selector_matches_expectation"] for row in rows
        ),
        "nonderivative_R0_R0_Higgs_bilinears_all_forbidden": all(
            not row["superpotential_allowed_by_Z4R"]
            for row in rows
            if row["id"] in {"direct_H_Hp_mass", "direct_H_H_mass", "direct_Hp_Hp_mass"}
        ),
        "conditional_exactness": (
            "If this Z4R is an exact discrete gauge symmetry and every GUT-scale "
            "scalar VEV has q_R=0, every non-derivative R0-R0 local "
            "superpotential Higgs bilinear is excluded."
        ),
        "not_proved": [
            "A higher-dimensional/geometric origin for the Z4R has not been embedded in a complete 6D supergravity/string compactification.",
            "H-Hc and normal-derivative fixed-point operators are allowed and can alter boundary conditions.",
            "No complete fixed-point operator basis or regulator-level locality theorem is supplied.",
        ],
    }


LOCAL_U1X_CHARGES = {
    "T10": -1,
    "Fbar5": 3,
    "N1": -5,
    "H5": 2,
    "Hpbar5": -2,
    "Hcbar5": -2,
    "Hpc5": 2,
    "X": 10,
    "Xbar": -10,
    "S": 0,
}


def local_gauge_operator_certificate() -> dict[str, Any]:
    specifications = [
        ("up_Yukawa", ["T10", "T10", "H5"], True),
        ("down_lepton_Yukawa", ["T10", "Fbar5", "Hpbar5"], True),
        ("right_neutrino_Majorana", ["N1", "N1", "X"], True),
        ("rank_breaking_driver", ["S", "X", "Xbar"], True),
        ("soft_mu_parent", ["S", "H5", "Hpbar5"], True),
        ("soft_Hc_Hpc_parent", ["S", "Hcbar5", "Hpc5"], True),
        ("dimension5_proton_proxy", ["T10", "T10", "T10", "Fbar5"], True),
        ("renormalizable_RPV_proxy", ["T10", "Fbar5", "Fbar5"], True),
    ]
    rows = []
    for operator_id, factors, su5_singlet_exists in specifications:
        charge_sum = sum(LOCAL_U1X_CHARGES[field] for field in factors)
        rows.append(
            {
                "id": operator_id,
                "factors": factors,
                "U1X_charge_sum": charge_sum,
                "SU5_singlet_exists": su5_singlet_exists,
                "local_gauge_invariant": charge_sum == 0 and su5_singlet_exists,
            }
        )
    return {
        "field_U1X_charges": LOCAL_U1X_CHARGES,
        "operator_ledger": rows,
        "required_rows_gauge_invariant": all(
            row["local_gauge_invariant"]
            for row in rows
            if row["id"]
            in {
                "up_Yukawa",
                "down_lepton_Yukawa",
                "right_neutrino_Majorana",
                "rank_breaking_driver",
                "soft_mu_parent",
                "soft_Hc_Hpc_parent",
            }
        ),
        "dimension5_proton_operator_is_gauge_invariant_but_R_forbidden": next(
            row["local_gauge_invariant"]
            for row in rows
            if row["id"] == "dimension5_proton_proxy"
        ),
    }


def neutral_vev_dressing_certificate(max_total_degree: int = 12) -> dict[str, Any]:
    """Exhaust R0-VEV dressings of H Hp inside the declared scalar ring."""

    vev_fields = ("X", "Xbar", "constant")
    checked = []
    for exponents in product(range(max_total_degree + 1), repeat=len(vev_fields)):
        if sum(exponents) > max_total_degree:
            continue
        charge = (R_CHARGES["H"] + R_CHARGES["Hp"]) % MODULUS
        charge += sum(
            exponent * R_CHARGES[field]
            for exponent, field in zip(exponents, vev_fields)
        )
        checked.append(charge % MODULUS)
    return {
        "declared_GUT_scale_VEV_fields": list(vev_fields),
        "all_declared_VEV_charges": [R_CHARGES[field] for field in vev_fields],
        "maximum_total_insertion_degree": max_total_degree,
        "number_of_exponent_vectors_checked": len(checked),
        "distinct_dressed_H_Hp_charges": sorted(set(checked)),
        "all_dressed_H_Hp_terms_forbidden": all(
            charge != SUPERPOTENTIAL_CHARGE for charge in checked
        ),
        "first_fatal_spurion": (
            "Any scalar or effective spurion of q_R=2 with a GUT-scale expectation "
            "allows the mass; S is deliberately q_R=2 but must have <S>=0 before "
            "soft breaking."
        ),
    }


def exact_rank(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        p = rows[rank][column]
        rows[rank] = [value / p for value in rows[rank]]
        for i in range(len(rows)):
            if i == rank or not rows[i][column]:
                continue
            factor = rows[i][column]
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def exact_inverse(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be nonempty and square")
    rows = [
        [Fraction(value) for value in row]
        + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        if pivot is None:
            raise ValueError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        p = rows[column][column]
        rows[column] = [value / p for value in rows[column]]
        for i in range(size):
            if i == column or not rows[i][column]:
                continue
            factor = rows[i][column]
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[column])]
    return [row[size:] for row in rows]


def block_matrix(
    top_left: Sequence[Sequence[int]],
    top_right: Sequence[Sequence[int]],
    bottom_left: Sequence[Sequence[int]],
    bottom_right: Sequence[Sequence[int]],
) -> list[list[int]]:
    return [list(a) + list(b) for a, b in zip(top_left, top_right)] + [
        list(a) + list(b) for a, b in zip(bottom_left, bottom_right)
    ]


def kk_triplet_exchange_certificate(size: int = 4) -> dict[str, Any]:
    """Exact finite KK witness for the bipartite triplet propagator selection."""

    zero = [[0 for _ in range(size)] for _ in range(size)]
    diagonal = [[(i + 1) * int(i == j) for j in range(size)] for i in range(size)]
    h_h_mass = [[int((i + j) % 3 == 0) for j in range(size)] for i in range(size)]
    h_h_mass = [
        [max(h_h_mass[i][j], h_h_mass[j][i]) for j in range(size)]
        for i in range(size)
    ]
    protected = block_matrix(h_h_mass, diagonal, diagonal, zero)
    protected_inverse = exact_inverse(protected)
    hh_block = [row[:size] for row in protected_inverse[:size]]

    fatal_hc_hc = [[int(i == j) for j in range(size)] for i in range(size)]
    unprotected = block_matrix(zero, diagonal, diagonal, fatal_hc_hc)
    unprotected_inverse = exact_inverse(unprotected)
    fatal_hh_block = [row[:size] for row in unprotected_inverse[:size]]

    zero_doublet = [[0, 0], [0, 0]]
    soft_doublet = [[0, 1], [1, 0]]
    return {
        "basis": "first H-type KK modes, then Hc-type KK modes",
        "matter_support": (
            "At O_GG, Z4R permits q=1 matter Yukawas only to q=0 H-type "
            "fields and forbids the corresponding q=2 Hc-type Yukawas."
        ),
        "protected_sample_size_per_block": size,
        "protected_matrix_rank": exact_rank(protected),
        "protected_HH_inverse_block_exactly_zero": all(
            value == 0 for row in hh_block for value in row
        ),
        "meaning": (
            "For invertible bulk H-Hc KK masses and no Hc-Hc mass, the inverse "
            "between two matter-coupled H sources vanishes exactly, even with an "
            "H-H block. This is only a structural finite-tower witness."
        ),
        "fatal_HcHc_control": {
            "nonzero_HH_inverse_entries": sum(
                value != 0 for row in fatal_hh_block for value in row
            ),
            "meaning": (
                "An Hc-Hc block makes the matter-source propagator nonzero and is "
                "therefore the controlled colored-Higgsino dimension-five source. "
                "Z4R forbids it before breaking, while S Hc Hpc can generate it "
                "at the soft scale."
            ),
        },
        "doublet_zero_sector": {
            "supersymmetric_rank": exact_rank(zero_doublet),
            "supersymmetric_nullity": 2 - exact_rank(zero_doublet),
            "after_unit_soft_mu_rank": exact_rank(soft_doublet),
            "after_unit_soft_mu_nullity": 2 - exact_rank(soft_doublet),
        },
    }


def anomaly_audit() -> dict[str, Any]:
    # Standard MSSM Z4R charges: three matter generations q=1 and Hu,Hd q=0.
    a3 = Fraction(3)
    a2 = Fraction(2) - 2 * Fraction(1, 2)
    a1 = -2 * Fraction(3, 5) * 2 * Fraction(1, 4)
    integerized = [int(a3), int(a2), int(5 * a1)]
    family = [
        {"field": "10_-1", "dimension": 10, "X": -1, "SU5_cubic": 1, "T_SU5": Fraction(3, 2)},
        {"field": "bar5_3", "dimension": 5, "X": 3, "SU5_cubic": -1, "T_SU5": Fraction(1, 2)},
        {"field": "1_-5", "dimension": 1, "X": -5, "SU5_cubic": 0, "T_SU5": Fraction(0)},
    ]
    family_su5_cubic = sum(row["SU5_cubic"] for row in family)
    family_su5sq_x = sum(row["T_SU5"] * row["X"] for row in family)
    family_x3 = sum(row["dimension"] * row["X"] ** 3 for row in family)
    family_grav_x = sum(row["dimension"] * row["X"] for row in family)
    x_pair_x3 = 10**3 + (-10) ** 3
    x_pair_grav_x = 10 + (-10)
    return {
        "six_dimensional_bulk": {
            "irreducible_trF4_normalization": "A(10)=1 and A(adj_SO10)=10-8=2",
            "vector_contribution": 2,
            "two_same_chirality_10_hyper_contributions": [-1, -1],
            "irreducible_gauge_sum": 0,
            "irreducible_gauge_anomaly_cancels": True,
            "rigid_chiral_dimension_mismatch_vector_minus_hypers": 45 - 2 * 10,
            "reducible_anomaly_status": "OPEN: factorization and a physical tensor/GS action are absent",
            "full_supergravity_status": (
                "OPEN: the H-V+29T=273 condition, gravity/tensor multiplets, and "
                "the entire neutral hidden spectrum have not been supplied"
            ),
        },
        "four_dimensional_massless_Z4R": {
            "convention": "T(fund)=1/2; hypercharge uses SU(5) normalization",
            "A3_R": str(a3),
            "A2_R": str(a2),
            "A1_R": str(a1),
            "integerized_comparison": {"A3": int(a3), "A2": int(a2), "5A1": int(5 * a1)},
            "residues_mod_eta_with_eta_2": [value % 2 for value in integerized],
            "gauge_coefficients_universal_mod_eta": len(
                {value % 2 for value in integerized}
            )
            == 1,
            "visible_gravitational_coefficient_before_GS_or_singlets": -13,
            "gravitational_discrete_anomaly_closed": False,
            "interpretation": (
                "The familiar low-energy gauge residues are universal modulo eta=2, "
                "but this neither computes nor cancels the six-dimensional or "
                "fixed-point discrete anomaly."
            ),
        },
        "O_GG_local_chiral_gauge_anomalies": {
            "family_decomposition": [
                {
                    **{key: value for key, value in row.items() if key != "T_SU5"},
                    "T_SU5": fraction_text(row["T_SU5"]),
                }
                for row in family
            ],
            "per_family_sums": {
                "SU5_cubic": family_su5_cubic,
                "SU5_squared_U1X": fraction_text(family_su5sq_x),
                "U1X_cubed": family_x3,
                "gravity_squared_U1X": family_grav_x,
            },
            "three_families_are_each_gauge_anomaly_free": all(
                value == 0
                for value in (family_su5_cubic, family_su5sq_x, family_x3, family_grav_x)
            ),
            "X_plus10_Xbar_minus10_pair": {
                "U1X_cubed_sum": x_pair_x3,
                "gravity_squared_U1X_sum": x_pair_grav_x,
                "vectorlike_and_gauge_anomaly_free": x_pair_x3 == 0 and x_pair_grav_x == 0,
            },
            "scope_warning": (
                "These exact sums close only the explicitly localized family and "
                "rank-breaking chiral gauge anomaly. Parity-split bulk Higgs/vector "
                "inflow and local discrete-R anomalies are not included."
            ),
        },
        "global_and_local_obligations": [
            "Compute the anomaly polynomial including every bulk hypermultiplet, tensor, and supergravity multiplet.",
            "Distribute parity-induced anomalies among all four fixed points and add explicit inflow/counterterms.",
            "Check mixed Z4R-G_local^2 and Z4R-gravity anomalies separately at every fixed point.",
            "Specify a quantized axion/tensor shift that cancels all universal residues; low-energy congruence is insufficient.",
            "Recheck the SU(2) Witten anomaly and all global/cobordism anomalies after adding boundary and hidden matter.",
        ],
        "low_energy_SU2_doublet_count": {
            "three_families": 12,
            "two_Higgs_doublets": 2,
            "total": 14,
            "even_in_declared_massless_spectrum": True,
        },
    }


def mu_and_neutrino_audit() -> dict[str, Any]:
    return {
        "supersymmetric_rank_breaking_action": (
            "W_GG = yu_ij 10_i 10_j H5 + yd_ij 10_i bar5_j Hprime_bar5 "
            "+ yN_ij 1_i 1_j X + kappa S(X Xbar-v_X^2) + lambda S H10 H10'"
        ),
        "supersymmetric_vacuum": {
            "X_Xbar": "v_X^2",
            "S": 0,
            "Z4R_preserved_by_GUT_rank_breaking": True,
            "Higgs_zero_mode_mu": 0,
        },
        "right_handed_neutrino": {
            "operator_R_charge": operator_charge(["N1", "N1", "X"]),
            "allowed": True,
            "local_gauge_charge_check": "(-5)+(-5)+(+10)=0",
            "scale_relation": "M_N = yN <X>",
            "open": (
                "The full F/D vacuum, hierarchy of yN, light-neutrino seesaw fit, "
                "and threshold feedback are not supplied."
            ),
        },
        "low_energy_mu": {
            "route": "soft terms shift the driving field to <S>~m_soft, giving mu_eff=lambda<S>",
            "breaks_Z4R_to": "Z2 matter parity",
            "why_residual_Z2": "all matter has q=1, H/Hp have q=0, and the q(S)=2 VEV is invariant under the squared generator",
            "status": (
                "Plausible but not calculated: the hidden sector and the soft scalar "
                "minimization must demonstrate the magnitude and phases of <S>, B_mu, "
                "and the gravitino-dependent operators."
            ),
        },
    }


def proton_audit(exchange: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "perturbative_RPV_dimension4": "forbidden: cubic matter charge is 3 mod 4",
        "direct_superpotential_dimension5": "forbidden: quartic matter charge is 0 mod 4",
        "colored_zero_modes": 0,
        "KK_colored_higgsino_exchange": {
            "conditional_result": (
                "The finite bipartite witness has an exactly zero H-H inverse block "
                "because Z4R permits O_GG matter Yukawas only to H, not Hc."
            ),
            "certificate_passes": exchange["protected_HH_inverse_block_exactly_zero"],
            "not_a_full_proof": (
                "The infinite KK determinant with every allowed fixed-point normal-"
                "derivative term has not been evaluated."
            ),
        },
        "after_R_breaking": (
            "S(10 10 10 bar5)/M_*^2 is allowed, so its coefficient scales as <S>/M_*^2; "
            "this is parametrically suppressed but still requires flavor, dressing, "
            "and lifetime matching."
        ),
        "colored_Higgsino_after_soft_mu": {
            "parametric_coefficient": "C5 ~ yu yd lambda_c<S>/Mc^2 ~ yu yd mu_R/Mc^2",
            "status": (
                "S Hc Hpc is Z4R-allowed and supplies the soft Hc-Hc block. The "
                "suppression follows only if the full KK inverse retains the "
                "declared block hierarchy; it is not a lifetime prediction."
            ),
        },
        "dimension6": (
            "X,Y KK gauge exchange and boundary Kähler operators remain; Z4R does "
            "not remove them."
        ),
        "falsifier": (
            "Any GUT-scale Hc-Hc quadratic block, direct baryon operator with an "
            "unsuppressed q_R=2 spurion, or matched proton lifetime below data "
            "rejects the candidate; the intended soft Hc-Hc block must remain small."
        ),
    }


def threshold_and_uv_obligations() -> dict[str, Any]:
    return {
        "not_calculated": [
            "The full two-radius KK determinant and regulator-matched gauge thresholds.",
            "Nonuniversal fixed-point gauge kinetic terms at SO(10), GG, flipped, and PS branes.",
            "U(1)X/rank-breaking, X/Xbar, S, flavor-mediator, and supersymmetry-breaking thresholds.",
            "The relation among M_c, M_*, the six-dimensional gauge coupling, and the observed unified coupling.",
        ],
        "power_law_warning": (
            "Bulk power-law pieces are cutoff sensitive; only symmetry-controlled "
            "differences can be used without a declared UV matching prescription."
        ),
        "falsifiers": [
            "No perturbative window M_*/M_c supports the required running.",
            "Allowed brane kinetic coefficients must be tuned beyond the declared naturalness criterion.",
            "The matched alpha_s, weak angle, or proton scale fails current constraints.",
        ],
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {
            "id": "HNOS2001",
            "authors": "L.J. Hall, Y. Nomura, T. Okui, D.R. Smith",
            "title": "SO(10) Unified Theories in Six Dimensions",
            "arxiv": "hep-ph/0108071",
            "url": "https://arxiv.org/abs/hep-ph/0108071",
            "used_for": "T2/Z2 SO(10) twists, Higgs parities, bulk-anomaly and threshold obligations",
        },
        {
            "id": "LRRRSSV2010",
            "authors": "H.M. Lee et al.",
            "title": "A unique Z_4^R symmetry for the MSSM",
            "arxiv": "1009.0905",
            "url": "https://arxiv.org/abs/1009.0905",
            "used_for": "SO(10)-compatible low-energy Z4R charges, residual matter parity, mu/proton logic",
        },
        {
            "id": "BCECW2004",
            "authors": "W. Buchmuller, L. Covi, D. Emmanuel-Costa, S. Wiesenfeldt",
            "title": "Flavour structure and proton decay in 6D orbifold GUTs",
            "arxiv": "hep-ph/0407070",
            "url": "https://arxiv.org/abs/hep-ph/0407070",
            "used_for": "R-symmetry dimension-five suppression and KK dimension-six proton obligations",
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, V55_PATH, V56_ARCH_PATH]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    v55 = load_bound(V55_PATH, EXPECTED_V55_CORE, "V55")
    architecture = load_bound(
        V56_ARCH_PATH, EXPECTED_V56_ARCH_CORE, "V56 architecture"
    )
    modes = orbifold_mode_certificate()
    selector = r_symmetry_certificate()
    local_gauge = local_gauge_operator_certificate()
    dressing = neutral_vev_dressing_certificate()
    exchange = kk_triplet_exchange_certificate()
    anomalies = anomaly_audit()
    mu_neutrino = mu_and_neutrino_audit()
    proton = proton_audit(exchange)

    checks = {
        "bound_V55_core_is_canonical_and_expected": v55["core_sha256"] == EXPECTED_V55_CORE,
        "bound_V56_architecture_core_is_canonical_and_expected": architecture["core_sha256"] == EXPECTED_V56_ARCH_CORE,
        "exactly_two_weak_doublet_zero_modes": modes["weak_doublet_zero_mode_count"] == 2,
        "zero_colored_zero_modes": modes["color_triplet_zero_mode_count"] == 0,
        "zero_Hc_zero_modes": modes["conjugate_Hc_zero_mode_count"] == 0,
        "both_desired_doublets_are_supported_at_GG_brane": modes["GG_brane_support_result"]["desired_doublet_zero_modes_supported"],
        "declared_Z4R_operator_expectations_match": selector["all_selector_expectations_met"],
        "required_GG_brane_operators_are_gauge_invariant": local_gauge["required_rows_gauge_invariant"],
        "all_nonderivative_R0_R0_Higgs_bilinears_forbidden": selector["nonderivative_R0_R0_Higgs_bilinears_all_forbidden"],
        "R0_VEV_dressings_cannot_regenerate_H_Hp_mass": dressing["all_dressed_H_Hp_terms_forbidden"],
        "finite_KK_bipartite_HH_inverse_is_zero": exchange["protected_HH_inverse_block_exactly_zero"],
        "HcHc_control_exposes_fatal_propagator": exchange["fatal_HcHc_control"]["nonzero_HH_inverse_entries"] > 0,
        "bulk_irreducible_gauge_anomaly_cancels": anomalies["six_dimensional_bulk"]["irreducible_gauge_anomaly_cancels"],
        "low_energy_Z4R_gauge_residues_are_universal": anomalies["four_dimensional_massless_Z4R"]["gauge_coefficients_universal_mod_eta"],
        "each_GG_brane_family_is_gauge_anomaly_free": anomalies["O_GG_local_chiral_gauge_anomalies"]["three_families_are_each_gauge_anomaly_free"],
        "GG_brane_rank_breaking_pair_is_gauge_anomaly_free": anomalies["O_GG_local_chiral_gauge_anomalies"]["X_plus10_Xbar_minus10_pair"]["vectorlike_and_gauge_anomaly_free"],
        "Majorana_operator_is_Z4R_allowed": mu_neutrino["right_handed_neutrino"]["operator_R_charge"] == 2,
        "no_gate_is_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy_v56_orbifold_z4r_protection_audit/v1",
        "status": STATUS,
        "scope_and_nonclaim": {
            "question": (
                "Can a Z4R with a possible higher-dimensional origin protect the "
                "V56 T2/Z2 orbifold Higgs zero "
                "modes while retaining Yukawas, Majorana mass, and a soft-scale mu?"
            ),
            "bounded_answer": (
                "Yes for direct non-derivative R0-R0 masses inside the declared local operator ring, "
                "conditional on a consistent higher-dimensional discrete-gauge realization and "
                "only R0 GUT-scale VEVs. This is a candidate mechanism, not a "
                "complete theory."
            ),
            "not_claimed": [
                "No regulator-level proof of a higher-dimensional/geometric origin for Z4R or complete fixed-point operator ring.",
                "No infinite KK determinant with normal-derivative boundary interactions.",
                "No localized/discrete/gravitational anomaly cancellation or physical GS completion.",
                "No threshold, flavor, seesaw, proton-lifetime, soft-spectrum, or cosmology fit.",
                "No G1-G8 gate promotion and no empirical discovery.",
            ],
        },
        "input_bindings": {
            "V55_completion_kill_test": {
                "path": V55_PATH.name,
                "expected_core_sha256": EXPECTED_V55_CORE,
                "actual_core_sha256": v55["core_sha256"],
                "relation": "The candidate replaces the rejected finite 4D R1 filter topology.",
            },
            "V56_architecture_escape": {
                "path": V56_ARCH_PATH.name,
                "expected_core_sha256": EXPECTED_V56_ARCH_CORE,
                "actual_core_sha256": architecture["core_sha256"],
                "selected_blueprint": "BP2_6D_SO10_T2_OVER_Z2_LOCALITY",
            },
        },
        "candidate_action": {
            "bulk": "6D N=1 SO(10) vector plus two same-chirality 10 hypermultiplets on T2/Z2",
            "GG_brane": (
                "three local families 10_-1+bar5_3+1_-5, X_+10, Xbar_-10, "
                "and S_0 at the SU(5)xU(1)X fixed point"
            ),
            "Z4R_conventional_4D_N1_bookkeeping": (
                "q(theta)=1, q(D_perp)=q(Sigma)=0, q(H)=0, q(Hc)=2; "
                "the superpotential has charge 2. A geometric origin is conditional."
            ),
            "change_from_V55": (
                "Doublet-triplet splitting is a component-parity/KK-kernel effect, "
                "not a four-dimensional h-B-H2 filter or additive selector."
            ),
        },
        "orbifold_mode_certificate": modes,
        "Z4R_certificate": selector,
        "O_GG_local_operator_gauge_certificate": local_gauge,
        "neutral_VEV_dressing_certificate": dressing,
        "KK_triplet_exchange_certificate": exchange,
        "mu_and_neutrino_audit": mu_neutrino,
        "anomaly_audit": anomalies,
        "proton_audit": proton,
        "threshold_and_UV_obligations": threshold_and_uv_obligations(),
        "decisive_open_falsifiers": [
            "No consistent exact higher-dimensional/discrete-gauge realization of the Z4R exists for the full compactification.",
            "A permitted H-Hc or normal-derivative brane operator lifts the weak zero modes or indirectly creates an Hc-Hc triplet block.",
            "Any q_R=2 scalar/spurion has a GUT-scale expectation and regenerates a Higgs mass.",
            "The full bulk plus localized anomaly system cannot be canceled with quantized inflow and physical fields.",
            "The infinite KK determinant contains a colored zero mode or lacks exactly one Hu/Hd pair before soft breaking.",
            "Threshold, seesaw/flavor, proton, or soft-spectrum matching fails data.",
        ],
        "primary_sources": primary_sources(),
        "decision": {
            "candidate_mechanism_survives_bounded_algebraic_audit": True,
            "exact_statement": (
                "All non-derivative R0-R0 Higgs bilinears are Z4R-forbidden to "
                "every order in the declared q_R=0 GUT-VEV ring."
            ),
            "higher_dimensional_Z4R_realization_proved": False,
            "all_boundary_operators_closed": False,
            "physical_anomaly_cancellation_complete": False,
            "one_action_completion": False,
            "complete_theory": False,
            "G1_to_G8_promotions": [],
            "next_exact_test": (
                "Classify all supersymmetric H-Hc and normal-derivative operators "
                "at the four fixed points, then compute the regulated infinite KK determinant."
            ),
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not passed for passed in checks.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    failures: list[str] = []
    if report.get("core_sha256") != canonical_sha(report):
        failures.append("stale canonical core")
    if report.get("status") != STATUS:
        failures.append("status mismatch")
    failures.extend(
        name for name, passed in report.get("integrity_checks", {}).items() if not passed
    )
    if report.get("n_failed_integrity_checks") != 0:
        failures.append("nonzero integrity-failure count")
    decision = report.get("decision", {})
    if decision.get("one_action_completion") or decision.get("complete_theory"):
        failures.append("candidate was overclaimed as complete")
    if decision.get("G1_to_G8_promotions"):
        failures.append("candidate overclaimed a gate")
    if decision.get("higher_dimensional_Z4R_realization_proved"):
        failures.append("unproved higher-dimensional Z4R realization was overclaimed")
    if decision.get("all_boundary_operators_closed"):
        failures.append("normal-derivative boundary loophole was overclaimed closed")
    if failures:
        raise RuntimeError("V56 orbifold Z4R audit failed: " + "; ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    modes = report["orbifold_mode_certificate"]
    dressing = report["neutral_VEV_dressing_certificate"]
    exchange = report["KK_triplet_exchange_certificate"]
    anomalies = report["anomaly_audit"]
    ops = report["Z4R_certificate"]["operator_ledger"]
    allowed = ", ".join(row["id"] for row in ops if row["superpotential_allowed_by_Z4R"])
    forbidden = ", ".join(row["id"] for row in ops if not row["superpotential_allowed_by_Z4R"])
    sources = "\n".join(
        f"- {row['authors']}, [{row['title']}]({row['url']}) (`{row['arxiv']}`)."
        for row in report["primary_sources"]
    )
    falsifiers = "\n".join(f"- {item}" for item in report["decisive_open_falsifiers"])
    open_items = "\n".join(f"- {item}" for item in report["scope_and_nonclaim"]["not_claimed"])
    anomaly_open = "\n".join(
        f"- {item}" for item in anomalies["global_and_local_obligations"]
    )
    threshold_open = "\n".join(
        f"- {item}" for item in report["threshold_and_UV_obligations"]["not_calculated"]
    )
    local_anom = anomalies["O_GG_local_chiral_gauge_anomalies"]
    return f"""# V56 6D orbifold Z4R protection audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Bounded result

The candidate passes one exact, useful test: **all non-derivative R0-R0 local
Higgs bilinears are forbidden to every order in the declared R-neutral
GUT-VEV ring**.  In conventional 4D N=1 bookkeeping,
`q(theta)=1`, `q(D_perp)=q(Sigma)=0`,
`q(H)=q(H')=0`, and `q(Hc)=q(H'c)=2`, while a superpotential term must have
charge 2.  Consequently `Hc D_perp H` is allowed, direct `H H'` and `Hc Hc`
are forbidden, and H-Hc boundary terms are allowed but remain in the
bipartite block.

That result is conditional.  A higher-dimensional/geometric origin of this
Z4R must exist as an exact discrete gauge symmetry of the full compactification.
H-Hc and normal-derivative fixed-point operators still require a regulator-level
classification.  The artifact does not close a theory gate.

The inputs are bound to V55 core
`{report['input_bindings']['V55_completion_kill_test']['actual_core_sha256']}`
and V56 architecture core
`{report['input_bindings']['V56_architecture_escape']['actual_core_sha256']}`.

## Orbifold kernel

The free translation/reflection projector gives zero modes
`{', '.join(modes['zero_modes'])}`.  There are exactly
`{modes['weak_doublet_zero_mode_count']}` weak-doublet zero modes,
`{modes['color_triplet_zero_mode_count']}` colored zero modes, and
`{modes['conjugate_Hc_zero_mode_count']}` conjugate-hyper zero modes.
At the `O_GG` SU(5)xU(1)X fixed point, both desired doublets and their massive
color partners have support.  Complementary Hc components also have local
support, but q=1 matter couples only to q=0 H fields: the corresponding Hc
Yukawas have charge 0 rather than the superpotential charge 2.

This is a projector certificate, not the infinite interacting KK determinant.

## Exact charge census

Allowed rows: {allowed}.

Forbidden rows: {forbidden}.

The neutral-VEV exhaust checked
`{dressing['number_of_exponent_vectors_checked']}` exponent vectors through
total insertion degree `{dressing['maximum_total_insertion_degree']}`.  Every
dressed `H H'` operator has charge 0 rather than 2.  The first fatal spurion is
therefore any charge-2 scalar or effective background with a GUT-scale
expectation.  The driving singlet S has charge 2 and must obey `<S>=0` in the
supersymmetric vacuum.

## Yukawa, Majorana, and mu

On the SU(5)xU(1)X brane the candidate action is

`W = yu 10 10 H5 + yd 10 bar5 H'bar5 + yN 1 1 X +
kappa S(X Xbar-v_X^2) + lambda S H H'`.

Each family is `10_-1+bar5_3+1_-5`, all with R charge 1;
`q(X)=q(Xbar)=0` and `q(S)=2`.  Both Yukawas and `1_-5 1_-5 X_+10` are
allowed.  The supersymmetric solution has `X Xbar=v_X^2` and `S=0`, preserving
Z4R and leaving `mu=0`.  Soft terms may
shift `<S>` to the soft scale and generate `mu=lambda<S>`, breaking Z4R to
matter parity.  That soft minimization, `B_mu`, phases, and the seesaw/flavour
fit have not been calculated.  Minimal SU(5) down/lepton mass relations are an
explicit flavor obligation, not a prediction accepted here.

## Colored exchange and proton operators

The exact finite `{exchange['protected_sample_size_per_block']}+{exchange['protected_sample_size_per_block']}`
KK witness has full rank `{exchange['protected_matrix_rank']}` and a zero H-H
inverse block.  Thus two Z4R-selected O_GG matter sources have no colored-Higgsino
dimension-five propagator in the declared bipartite quadratic topology.
Adding an Hc-Hc block produces
`{exchange['fatal_HcHc_control']['nonzero_HH_inverse_entries']}` nonzero H-H
inverse entries.  A direct Hc-Hc mass is forbidden before R breaking, but
`S Hc H'c` is allowed and generates this block after `<S>` becomes nonzero.

Z4R forbids `10 bar5 bar5` R parity violation and direct
`10 10 10 bar5/M_*` proton operators.  After R breaking,
`S(10 10 10 bar5)/M_*^2` is allowed and must be matched.  Conditional on the
full KK inverse retaining the block hierarchy, colored exchange scales as
`C5 ~ yu yd lambda_c<S>/Mc^2`, not as an unsuppressed `1/Mc` coefficient.
KK gauge exchange and boundary Kähler operators remain as dimension-six
obligations.

## Anomalies

In the normalization `A(10)=1`, the irreducible six-dimensional SO(10)
coefficient is `2-1-1=0`.  The rigid chiral dimension mismatch is nevertheless
`{anomalies['six_dimensional_bulk']['rigid_chiral_dimension_mismatch_vector_minus_hypers']}`,
and reducible, gravitational, fixed-point, and discrete anomalies are open.

For the massless MSSM fields the mixed coefficients are
`A3={anomalies['four_dimensional_massless_Z4R']['A3_R']}`,
`A2={anomalies['four_dimensional_massless_Z4R']['A2_R']}`, and
`A1={anomalies['four_dimensional_massless_Z4R']['A1_R']}`.  Their integerized
residues are universal modulo `eta=2`; this is only a necessary low-energy
check and is not localized six-dimensional anomaly cancellation.

The explicitly localized family sums vanish exactly, family by family:
`A_SU5^3={local_anom['per_family_sums']['SU5_cubic']}`,
`A_SU5^2-X={local_anom['per_family_sums']['SU5_squared_U1X']}`,
`A_X^3={local_anom['per_family_sums']['U1X_cubed']}`, and
`A_grav-X={local_anom['per_family_sums']['gravity_squared_U1X']}`.
The `X_+10+Xbar_-10` pair is vectorlike.  These sums do not include
parity-localized bulk inflow or discrete-R anomalies.

Remaining anomaly work:

{anomaly_open}

## Threshold and UV obligations

{threshold_open}

## Decisive falsifiers

{falsifiers}

## Explicit nonclaims

{open_items}

## Primary literature

{sources}

The Z4R protection layer is a new conditional candidate built on the
published orbifold and low-energy Z4R mechanisms; it is not attributed to those
papers as a completed model.
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("generated V56 orbifold Z4R artifacts are missing")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("generated V56 orbifold Z4R JSON is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("generated V56 orbifold Z4R Markdown is stale")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write JSON and Markdown")
    mode.add_argument("--check", action="store_true", help="check generated artifacts")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = check_artifacts() if args.check else write_artifacts() if args.write else build_report()
    validate(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
