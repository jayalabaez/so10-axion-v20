#!/usr/bin/env python3
"""V71 normal-bundle and equivariant Green--Schwarz frontier audit.

V70 completed the charged classical Spin/flavor lift and the ordinary local
gauge-anomaly ledger of two candidate T2/Z4 Spin(11) parents.  That is not the
full fixed-point anomaly.  A codimension-two fixed locus also retains the
normal Lorentz group U(1)_L.  This audit computes the missing perturbative
normal-bundle polynomial with exact rational arithmetic.

The result has two sharp parts.

* The unmodified V70 candidates have, at each Z4 U(5) corner, mixed
  U(1)_L-(SU(5)^2,X^2) coefficient (-1/4,40) in the ordinary localized-Weyl
  anomaly-polynomial normalization.  The restriction of every
  ordinary bulk Spin(11) Green--Schwarz invariant is proportional to (1,40),
  and the determinant is -50.  Thus standard bulk GS inflow cannot cancel
  the orthogonal component.  The second corner has no V70 localized repair.

* Including the gravity/tensor system and all charged bulk fermions, 266
  neutral hypers with phase imbalance Delta give

      I6 = [(86+11 Delta)x^3 + (-14+Delta)x p1(T4)]/192.

  This is proportional to x p1(T6)=x[p1(T4)+x^2] iff Delta=-10.  In any
  unitary flavor lift satisfying that condition at both Z4 corners, at least
  ten neutral chiral zero modes survive.  An explicit 10+64*4 dimensional
  witness is checked below and embedded into the symmetric quaternionic-
  Kahler target Sp(266,1)/(Sp(266)xSp(1)).

The file retracts the former standalone R-compatible repair module after an
explicit common-normalization check.  X(+10), Xbar(-10) fermions of normal
charge -1/2 plus two neutral driver fermions of charge +1/2 do have zero
linear and cubic moments and zero U(1)_L^2-X anomaly, but their mixed shift is
-100 while alignment needs -50.  A corrected exact local witness uses charge
+/-5 singlets of the spinorial preimage U(5)-tilde inside Spin(11).  At z00
the inherited rank pair and S0 plus seven
new chirals give the required shift with every spectator anomaly zero; z11
uses an eight-chiral mirror module.  Their mass/decay sector and all global
data remain unconstructed.  A
global combined H-bundle, the localized fields' actual isotropy
representations, the equivariant GS/Wu--Chern--Simons cocycle, neutral-mode
stabilization and global eta phases remain absent.  No G gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


VERSION = "V71"
DATE = "2026-08-30"
SCHEMA = "susy_v71_spin11_normal_bundle_equivariant_gs_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
MD_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v71_spin11_normal_bundle_equivariant_gs_audit.py"
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
EXPECTED_V70_CORE = "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"

STATUS = (
    "V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT__V70_CORE_BOUND__"
    "SPIN_HALF_EQUIVARIANT_FIXED_POLYNOMIAL_EXACT__GRAVITINO_TENSORINO_AND_"
    "SELF_DUAL_PAIR_LEDGER_EXACT_UNDER_STANDARD_LIFT__CHARGED_BULK_NORMAL_"
    "GRAVITY_CLASS_EXACT__NEUTRAL_PHASE_FACTORIZATION_IFF_DELTA_MINUS10__"
    "TEN_NEUTRAL_ZERO_MODE_LOWER_BOUND_AND_266_SYMMETRIC_QUATERNIONIC_KAHLER_"
    "TARGET_ISOMETRY_WITNESS_EXACT__MIXED_U1L_U5_GAUGE_VECTOR_MINUS_QUARTER_"
    "PLUS40__BULK_GS_DIRECTION_1_40__DETERMINANT_MINUS50__U1L2X_LEDGER_ZERO__"
    "UNMODIFIED_F70_AND_ALT_REJECTED__FORMER_FOUR_FERMION_REPAIR_RETRACTED_BY_"
    "FACTOR_TWO_NORMALIZATION__CORRECTED_PROVISIONAL_SPINORIAL_U5_PREIMAGE_"
    "CHARGE_LATTICE_"
    "Z00_SEVEN_NEW_"
    "AND_Z11_EIGHT_NEW_CHIRAL_MODULES_EXACT_PERTURBATIVELY__EXOTIC_MASSES_DECAYS_"
    "AND_COSMOLOGY_OPEN__"
    "ORDINARY_SPIN_WUCS_NOT_APPLICABLE_WITHOUT_GENERALIZED_EQUIVARIANT_"
    "EXTENSION__LOCALIZED_NORMAL_CHARGES_GLOBAL_PHASES_AND_PHENOMENOLOGY_"
    "OPEN__G1_TO_G8_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "VON_GERSDORFF_2007",
        "title": "Anomalies on Six Dimensional Orbifolds",
        "url": "https://arxiv.org/abs/hep-th/0612212",
        "sourced_fact": (
            "Equation (3.36) gives the localized remnant-Lorentz anomaly of a "
            "six-dimensional Weyl fermion.  Equations (4.3)-(4.5) calibrate one "
            "four-dimensional zero-mode Weyl of |qL|=1/2 to one A2 unit.  "
            "Equations (3.37)-(3.38) show that "
            "ordinary bulk GS inflow cancels only bulk-invariant trace directions; "
            "F0-dependent orthogonal terms need localized fermions or axions."
        ),
        "scope_boundary": (
            "The paper explicitly leaves gravitino and self-dual-form contributions "
            "outside its spin-1/2 calculation; those are derived separately here."
        ),
    },
    {
        "id": "MONNIER_MOORE_2018",
        "title": "Remarks on the Green-Schwarz terms of six-dimensional supergravity theories",
        "url": "https://arxiv.org/abs/1808.01334",
        "sourced_fact": (
            "The global GS term on smooth spin manifolds is a Wu--Chern--Simons "
            "construction and requires the characteristic gravitational coefficient."
        ),
        "nonimport": (
            "A smooth-spin result is not an equivariant construction on the present "
            "orbifold with a diagonal Spin-SU(2)R lift and fixed strata."
        ),
    },
    {
        "id": "MONNIER_MOORE_PARK_2017",
        "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
        "url": "https://arxiv.org/abs/1711.04777",
        "sourced_fact": (
            "Six-dimensional gauge anomaly coefficients obey integral string-charge "
            "lattice constraints depending on the global gauge group."
        ),
    },
    {
        "id": "ZHANG_2026",
        "title": "Perturbative Anomaly Inflow on Orbifolds",
        "url": "https://arxiv.org/abs/2608.23326",
        "sourced_fact": (
            "The equivariant fixed density is Ahat(TF) K_g(NF) ch_g(E), with "
            "K_g=product[2 sinh((x+i theta)/2)]^-1."
        ),
        "scope_boundary": (
            "The construction determines perturbative polynomials, not torsion, eta "
            "holonomy, or the full Rarita/self-dual/global gluing problem."
        ),
    },
    {
        "id": "LEE_TACHIKAWA_2020",
        "title": "Some comments on 6d global gauge anomalies",
        "url": "https://arxiv.org/abs/2012.11622",
        "sourced_fact": (
            "Spin-bordism, rather than pi_6 alone, classifies the relevant global "
            "gauge anomaly; the simply connected cases used in six dimensions have "
            "trivial degree-seven spin bordism after the GS system is treated properly."
        ),
    },
    {
        "id": "NISHINO_SEZGIN_1997",
        "title": "New Couplings of Six-Dimensional Supergravity",
        "url": "https://arxiv.org/abs/hep-th/9703075",
        "sourced_fact": (
            "Six-dimensional supergravity hypermultiplets admit quaternionic-Kahler "
            "symmetric targets, with Sp(n,1)/(Sp(n)xSp(1)) as the generic example."
        ),
    },
    {
        "id": "MILLS_2023",
        "title": "The Structure of the Spin^h Bordism Spectrum",
        "url": "https://arxiv.org/abs/2306.17709",
        "sourced_fact": (
            "A diagonal Spin-Sp(1) quotient defines a generalized Spin^h-type "
            "tangential structure with bordism theory different from ordinary Spin."
        ),
        "scope_boundary": "The larger model-specific H-bordism group is not computed here.",
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "sourced_fact": (
            "A GS two-form breaks a U(1) only when the canceled mixed anomaly "
            "survives in the four-dimensional zero-mode theory; globally vanishing "
            "localized anomalies need not generate that mass."
        ),
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def fstr(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def load_v70() -> dict[str, Any]:
    if not V70_PATH.is_file():
        raise RuntimeError("missing V70 route artifact")
    value = json.loads(V70_PATH.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError("V70 route core is stale")
    if actual != EXPECTED_V70_CORE:
        raise RuntimeError("unexpected V70 route core")
    return value


Z4_WEIGHTS = {
    0: Fraction(3, 8),
    1: Fraction(1, 8),
    2: Fraction(-1, 8),
    3: Fraction(-3, 8),
}

Z4_SERIES = {
    # coefficients of 1, x, x^2, x^3 in (1/4) sum h_m^j K_j(x)
    0: (Fraction(3, 8), Fraction(1, 8), Fraction(-7, 64), Fraction(-11, 192)),
    1: (Fraction(1, 8), Fraction(-1, 8), Fraction(-5, 64), Fraction(11, 192)),
    2: (Fraction(-1, 8), Fraction(-1, 8), Fraction(5, 64), Fraction(11, 192)),
    3: (Fraction(-3, 8), Fraction(1, 8), Fraction(7, 64), Fraction(-11, 192)),
}


def phase_sign(m: int) -> int:
    return (-1, 1, 1, -1)[m % 4]


def spin_half_index_audit() -> dict[str, Any]:
    rows = []
    for m in range(4):
        c0, c1, c2, c3 = Z4_SERIES[m]
        xp = -c1 / 24  # Ahat(T4)=1-p1(T4)/24+...
        expected = Fraction(phase_sign(m), 192)
        rows.append(
            {
                "m": m,
                "eta": ("1", "i", "-1", "-i")[m],
                "h_m": f"zeta*i^{m}",
                "series_coefficients_1_x_x2_x3": [fstr(x) for x in (c0, c1, c2, c3)],
                "I6_x3": fstr(c3),
                "I6_x_p1T4": fstr(xp),
                "compact_I6": f"{fstr(expected)} (11 x^3 + x p1(T4))",
                "matches_compact_form": c3 == 11 * expected and xp == expected,
            }
        )
    return {
        "status": "EXACT_Z4_SPIN_HALF_EQUIVARIANT_FIXED_POLYNOMIAL",
        "definitions": {
            "zeta": "exp(i pi/4)",
            "x": "c1(N), the remnant normal U(1)_L root",
            "p": "p1(T4)",
            "K_j": "[2 sinh((x+i pi j/2)/2)]^-1",
            "h_m": "zeta*i^m, calibrated to the V70 projector weights",
            "fixed_sum": "(1/4) sum_(j=1..3) h_m^j K_j",
            "Ahat_T4": "1-p/24+...",
        },
        "weight_calibration": [fstr(Z4_WEIGHTS[m]) for m in range(4)],
        "phase_signs_m0123": [phase_sign(m) for m in range(4)],
        "rows": rows,
        "Z2_result": "0: the order-two normal factor is even in x, so its degree-six x^3 and x p terms vanish",
        "all_compact_forms_exact": all(row["matches_compact_form"] for row in rows),
    }


def gravity_tensor_index_audit() -> dict[str, Any]:
    x3 = Fraction(7, 32)
    xp = Fraction(-3, 32)
    return {
        "status": "EXACT_UNDER_THE_STANDARD_UNTWISTED_TENSOR_LIFT",
        "fermionic_virtual_bundle": "-(T_C M6-1)+1 = -(T_C M6-2)",
        "explanation": [
            "the gauge-fixed Rarita-Weyl index is twisted by T_C M6-1",
            "the gravitino has chirality opposite the hyperino and the tensorino the same chirality",
            "ch_g(T_C M6-2)=2+p1(T4)+2 cosh(x+i theta_j)",
        ],
        "I6_gravity_plus_tensor_fermions": {
            "x3": fstr(x3),
            "x_p1T4": fstr(xp),
            "common_denominator_192": [fstr(192 * x3), fstr(192 * xp)],
            "formula": "(42 x^3-18 x p1(T4))/192",
        },
        "smooth_identity_crosscheck": "gravity plus one tensor = -273+29=-244 irreducible-gravity units",
        "self_dual_forms": {
            "standard_lift": "the gravity B+ and tensor B- equivariant signature complexes cancel pointwise",
            "extra_tensor_lattice_twist": "NOT_ASSUMED; any O(1,1;Z) twist is new data and requires recomputation",
        },
        "Z2_result": "0 in the normal degree-six sector",
    }


def full_11_normal_unit(m: int) -> int:
    # Q eigenvalue multiplicities on 11_C: 5*i, 5*(-i), 1.
    return (
        5 * phase_sign(m + 1)
        + 5 * phase_sign(m - 1)
        + phase_sign(m)
    )


def charged_bulk_normal_gravity_audit() -> dict[str, Any]:
    adjoint_phase_dimensions = (25, 5, 20, 5)
    adjoint_hyper_chirality_units = sum(
        dim * phase_sign(m) for m, dim in enumerate(adjoint_phase_dimensions)
    )
    gaugino_units = -adjoint_hyper_chirality_units
    m301 = [3, 0, 1]
    m301_units = [full_11_normal_unit(m) for m in m301]
    flavor_spectator_options = {
        "m0_plus_m2": full_11_normal_unit(0) + full_11_normal_unit(2),
        "m1_plus_m3": full_11_normal_unit(1) + full_11_normal_unit(3),
    }
    flavor_units = full_11_normal_unit(3) + flavor_spectator_options["m0_plus_m2"]
    total_m301 = gaugino_units + sum(m301_units)
    total_flavor = gaugino_units + flavor_units
    return {
        "status": "EXACT_SAME_PLUS4_HYPER_UNITS_FOR_BOTH_V70_BRANCHES",
        "adjoint": {
            "phase_dimensions_m0123": list(adjoint_phase_dimensions),
            "same_chirality_weighted_sum": adjoint_hyper_chirality_units,
            "gaugino_opposite_chirality_units": gaugino_units,
        },
        "full_11_identity": {
            "formula": "u_11(m)=5 s_(m+1)+5 s_(m-1)+s_m=s_m",
            "values_m0123": [full_11_normal_unit(m) for m in range(4)],
        },
        "integer_m301_branch": {
            "m_values": m301,
            "individual_units": m301_units,
            "three_11_sum": sum(m301_units),
            "with_gaugino": total_m301,
        },
        "flavor_Wilson_branch": {
            "active_m3": full_11_normal_unit(3),
            "spectator_pair_options": flavor_spectator_options,
            "with_gaugino": total_flavor,
        },
        "I6_at_each_Z4_corner": "4 (11 x^3+x p1(T4))/192",
        "z00_equals_z11": total_m301 == total_flavor == 4,
        "Z2_result": "0",
    }


def neutral_phase_audit() -> dict[str, Any]:
    gravity = (42, -18)
    charged = (44, 4)
    base = (gravity[0] + charged[0], gravity[1] + charged[1])
    # Coefficients are (x^3, x*p) in denominator 192.
    delta_factorization = Fraction(base[1] - base[0], 11 - 1)
    delta_factorization = int(delta_factorization)
    factored = (base[0] + 11 * delta_factorization, base[1] + delta_factorization)
    zero_delta_x3 = Fraction(-base[0], 11)
    zero_delta_xp = -base[1]
    explicit_counts = {"m0": 74, "m1": 64, "m2": 64, "m3": 64}
    explicit_delta = explicit_counts["m1"] + explicit_counts["m2"] - explicit_counts["m0"] - explicit_counts["m3"]
    return {
        "status": "EXACT_UNITARY_CLASSIFICATION_AND_SYMMETRIC_QK_TARGET_ISOMETRY_WITNESS__GLOBAL_H_BUNDLE_OPEN",
        "definition": "Delta_f=N1_f+N2_f-N0_f-N3_f at a Z4 corner f",
        "component_ledger_over_192": {
            "gravity_plus_tensor": list(gravity),
            "charged_bulk": list(charged),
            "before_266_neutrals": list(base),
            "one_neutral_hyper_phase_m": "s_m*(11,1)",
        },
        "total_polynomial": "[(86+11 Delta_f)x^3+(-14+Delta_f)x p1(T4)]/192",
        "scope_of_Delta_minus10": (
            "bulk fields only, or a localized sector with Q1=sum(d q)=0 and "
            "Q3=sum(d q^3)=0; arbitrary localized normal charges change the condition"
        ),
        "general_localized_extension": {
            "definitions": [
                "Q1_f=sum_local d_i q_i",
                "Q3_f=sum_local d_i q_i^3",
            ],
            "local_Weyl_addition_over_192": "(32 Q3_f, -8 Q1_f)",
            "full_directional_factorization_equation": "100+10 Delta_f+32 Q3_f+8 Q1_f=0",
        },
        "cannot_vanish": {
            "x3_requires_Delta": fstr(zero_delta_x3),
            "xp_requires_Delta": fstr(zero_delta_xp),
            "requirements_incompatible": zero_delta_x3 != zero_delta_xp,
        },
        "bulk_gravitational_trace_factorization": {
            "restricted_trace": "p1(T6)|_f=p1(T4)+x^2",
            "condition": "coefficient(x^3)=coefficient(x p1(T4))",
            "unique_Delta": delta_factorization,
            "coefficient_pair_over_192": list(factored),
            "factored_polynomial": "-(1/8) x [p1(T4)+x^2] = -(1/8)x p1(T6)|_f",
            "necessary_not_sufficient": True,
        },
        "two_corner_zero_mode_theorem": {
            "space_group": [
                "A^4=1, [U,V]=0",
                "A U A^-1=V",
                "A V A^-1=U^-1",
            ],
            "orbit_proof": [
                "length-four and length-two translation-character orbits give Delta_00=Delta_11=0",
                "the fixed (-1,-1) character gives opposite signs because (UA)=-A",
                "only the translation-trivial (+1,+1) eigenspace contributes to the common corner value",
                "there Delta=N_(m1,m2)-N_(m0,m3), while m0 and m3 are precisely neutral Phi+ and Phi- zero modes",
            ],
            "if_Delta00_equals_Delta11_equals_minus10": "N_zero=N_(m0,m3)=N_(m1,m2)+10 >= 10",
            "minimum_neutral_chiral_zero_modes": 10,
        },
        "conventional_local_fermion_only_no_go_for_factored_residue": {
            "target_to_cancel": "+(1/8)x[p1(T4)+x^2]",
            "required_charge_moments": ["sum q=-3", "sum q^3=+3/4"],
            "half_integer_spin2_rewrite": ["r_i=2q_i odd", "sum r=-6", "sum r^3=+6"],
            "congruence": "every odd r obeys r^3=r mod 24, but +6 is not congruent to -6 mod 24",
            "solution_exists": False,
            "scope": "conventional half-integral Spin(2) charges; projective/twisted isotropy data require a separate audit",
            "conclusion": "the residual needs tensor/GS inflow or nonstandard localized isotropy, not ordinary brane fermions alone",
        },
        "explicit_266_dimensional_witness": {
            "target_isometry_constructed": True,
            "global_H_bundle_constructed": False,
            "ten_trivial_blocks": "A=U=V=1, m=0; ten Phi+ zero modes",
            "sixty_four_length4_blocks": {
                "A": "A e_k=e_(k+1 mod 4)",
                "U_diagonal": ["i", "-1", "-i", "-1"],
                "V_diagonal": ["-1", "i", "-1", "-i"],
                "each_A_and_UA_spectrum": ["1", "i", "-1", "-i"],
                "constant_modes": 0,
            },
            "dimension": 10 + 64 * 4,
            "phase_counts_at_each_corner": explicit_counts,
            "Delta_at_each_corner": explicit_delta,
            "neutral_chiral_zero_modes": 10,
        },
        "symmetric_quaternionic_Kahler_realization": {
            "target": "Sp(266,1)/(Sp(266)xSp(1))",
            "real_dimension": 4 * 266,
            "fixed_vacuum_point": "the symmetric-space origin fixed by Sp(266)xSp(1)",
            "effective_superfield_rotation": "A_eff=I_10 direct_sum C4^(direct_sum 64), A_eff^4=I",
            "effective_translations": "U_eff=I_10 direct_sum U4^64 and V_eff=I_10 direct_sum V4^64 from the exact matrix witness",
            "underlying_half_angle_flavor_lift": "A_F=zeta A_eff in U(266) subset Sp(266), so A_F^4=-I",
            "complex_symplectic_embedding": "iota(A_F)=diag(A_F,conjugate(A_F)) in the complex 532",
            "SU2R_lift": "U_R=diag(zeta^-1,zeta), U_R^4=-I",
            "effective_N1_fields": [
                "Phi+ -> zeta^-1 A_F Phi+ = A_eff Phi+",
                "Phi- -> zeta^-1 conjugate(A_F) Phi- = -i A_eff^-1 Phi-",
            ],
            "scalar_order_four": "(iota(A_F),U_R)^4=(-I,-I), trivial in the diagonal-center isotropy quotient",
            "hyperino_lift": "A_F^-1=zeta^-1 A_eff^-1=P_f; its fourth -I cancels L_theta^4=-I",
            "translation_lift": "U_eff,V_eff embed directly in U(266) subset Sp(266) with trivial SU2R translation holonomy",
            "local_space_group_and_bundle_lift": "PASS_EXACT_AT_THE_SYMMETRIC_FIXED_POINT",
            "still_open": [
                "global T2/Z4 combined Spin-SU2R-Sp266 H-bundle and quotient",
                "global composite Sp(1) connection and hyperino bundle",
                "neutral zero-mode stabilization and couplings",
                "equivariant WCS/H-bordism and Dai-Freed phase",
            ],
        },
        "microscopic_caveat": (
            "The symmetric QK target and local isotropy representation now exist "
            "explicitly, but their combined H-bundle has not been globalized over "
            "the orbifold and the ten neutral zero modes are not stabilized."
        ),
    }


def kappa(m: int) -> Fraction:
    return 4 * Z4_WEIGHTS[m % 4] ** 2 - Fraction(5, 16)


def mixed_index_weight(m: int) -> Fraction:
    """Coefficient of x in the fixed density, in ordinary local-Weyl units."""
    return Z4_SERIES[m % 4][1]


ADJOINT_U5 = [
    # name, eta exponent, SU5 Dynkin index, dimension, X charge
    ("24_0", 0, Fraction(5), 24, 0),
    ("1_0", 0, Fraction(0), 1, 0),
    ("10_4", 2, Fraction(3, 2), 10, 4),
    ("10bar_-4", 2, Fraction(3, 2), 10, -4),
    ("5_2", 1, Fraction(1, 2), 5, 2),
    ("5bar_-2", 3, Fraction(1, 2), 5, -2),
]


def weighted_gauge_trace(rows: Sequence[tuple[str, int, Fraction, int, int]]) -> tuple[Fraction, Fraction]:
    su5 = sum(mixed_index_weight(m) * index for _, m, index, _, _ in rows)
    x2 = sum(mixed_index_weight(m) * dim * charge * charge for _, m, _, dim, charge in rows)
    return Fraction(su5), Fraction(x2)


def eleven_mixed_trace(m: int) -> tuple[Fraction, Fraction]:
    rows = [
        ("1_0", m, Fraction(0), 1, 0),
        ("5_2", m + 1, Fraction(1, 2), 5, 2),
        ("5bar_-2", m + 3, Fraction(1, 2), 5, -2),
    ]
    return weighted_gauge_trace(rows)


def eleven_x2_X_trace(m: int) -> Fraction:
    # Coefficient of x^2 F_X before the common Chern-character normalization.
    c2 = {phase: Z4_SERIES[phase][2] for phase in range(4)}
    return 10 * (c2[(m + 1) % 4] - c2[(m + 3) % 4])


def localized_singlet_module_ledger(
    rows: Sequence[tuple[str, int, Fraction, str]],
) -> dict[str, Any]:
    q1 = sum((q for _, _, q, _ in rows), Fraction(0))
    q3 = sum((q**3 for _, _, q, _ in rows), Fraction(0))
    mixed_x2 = sum((q * x_charge * x_charge for _, x_charge, q, _ in rows), Fraction(0))
    normal2_x = sum((q * q * x_charge for _, x_charge, q, _ in rows), Fraction(0))
    gravity_x = sum(x_charge for _, x_charge, _, _ in rows)
    x3 = sum(x_charge**3 for _, x_charge, _, _ in rows)
    fields = [
        {
            "field": name,
            "U5_representation": f"1_({x_charge:+d})" if x_charge else "1_(0)",
            "X": x_charge,
            "qL_fermion": fstr(q),
            "qL_scalar": fstr(q + Fraction(1, 2)),
            "Z4R_scalar": int(2 * (q + Fraction(1, 2))) % 4,
            "origin": origin,
        }
        for name, x_charge, q, origin in rows
    ]
    return {
        "fields": fields,
        "field_count": len(rows),
        "Q1": fstr(q1),
        "Q3": fstr(q3),
        "U1L_SU5_squared": "0",
        "U1L_X_squared": fstr(mixed_x2),
        "U1L_squared_X": fstr(normal2_x),
        "ordinary_gravity_X": gravity_x,
        "ordinary_X_cubed": x3,
        "all_spectator_anomalies_zero": q1 == q3 == normal2_x == gravity_x == x3 == 0,
    }


def mixed_normal_gauge_audit(v70: Mapping[str, Any]) -> dict[str, Any]:
    v70_r_charges = v70["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"][
        "complete_renormalizable_local_operator_ledger"
    ]["Z4R_charges"]
    if v70_r_charges.get("X_Xbar") != 0 or v70_r_charges.get("S0") != 2:
        raise RuntimeError("V70 z00 X/Xbar/S0 R-charge assumptions changed")
    weighted_adjoint = weighted_gauge_trace(ADJOINT_U5)
    vector = (-weighted_adjoint[0], -weighted_adjoint[1])
    eleven_rows = {f"m{m}": eleven_mixed_trace(m) for m in range(4)}
    bulk_direction = (Fraction(1), Fraction(40))
    determinant = vector[0] * bulk_direction[1] - vector[1] * bulk_direction[0]
    pair_shift = (Fraction(0), Fraction(-100))
    repaired = (vector[0] + pair_shift[0], vector[1] + pair_shift[1])
    aligned_target = tuple(vector[0] * x for x in bulk_direction)
    required_net_shift = tuple(aligned_target[i] - vector[i] for i in range(2))
    pair_overshoot = tuple(pair_shift[i] - required_net_shift[i] for i in range(2))
    z00_compensating_axion = tuple(-x for x in pair_overshoot)
    family16_direction = (Fraction(2), Fraction(80))
    pair_qsum = Fraction(-1)
    pair_qcube = 2 * Fraction(-1, 2) ** 3
    local_pair_x3 = pair_qcube / 6
    local_pair_xp = -pair_qsum / 24
    c2 = {phase: Z4_SERIES[phase][2] for phase in range(4)}
    adjoint_x2_X_before_chirality = sum(
        c2[m % 4] * dim * charge for _, m, _, dim, charge in ADJOINT_U5
    )
    gaugino_x2_X = -adjoint_x2_X_before_chirality
    eleven_x2 = {f"m{m}": eleven_x2_X_trace(m) for m in range(4)}
    m301_x2_X = gaugino_x2_X + sum(eleven_x2_X_trace(m) for m in (3, 0, 1))
    flavor_x2_X = gaugino_x2_X + eleven_x2_X_trace(3) + eleven_x2_X_trace(0) + eleven_x2_X_trace(2)
    repair_charges = [Fraction(-1, 2), Fraction(-1, 2), Fraction(1, 2), Fraction(1, 2)]
    repair_Q1 = sum(repair_charges, Fraction(0))
    repair_Q3 = sum((q**3 for q in repair_charges), Fraction(0))
    pair_x2_X = Fraction(1, 2) * (
        10 * repair_charges[0] ** 2 - 10 * repair_charges[1] ** 2
    )
    z00_rows = [
        ("X_plus10", 10, Fraction(-1, 2), "inherited V70 rank field"),
        ("Xbar_minus10", -10, Fraction(-1, 2), "inherited V70 rank field"),
        ("S0", 0, Fraction(1, 2), "inherited V70 localized R=2 driver"),
        *((f"P5_plus_{i}", 5, Fraction(1, 2), "new F71 compensator") for i in (1, 2)),
        *((f"P5_minus_{i}", -5, Fraction(1, 2), "new F71 compensator") for i in (1, 2)),
        *((f"N0_{i}", 0, Fraction(-1, 2), "new F71 neutral") for i in (1, 2, 3)),
    ]
    z11_rows = [
        *((f"P5prime_plus_{i}", 5, Fraction(-1, 2), "new F71 primed compensator") for i in (1, 2)),
        *((f"P5prime_minus_{i}", -5, Fraction(-1, 2), "new F71 primed compensator") for i in (1, 2)),
        *((f"N2prime_{i}", 0, Fraction(1, 2), "new F71 primed neutral") for i in (1, 2, 3, 4)),
    ]
    z00_module = localized_singlet_module_ledger(z00_rows)
    z11_module = localized_singlet_module_ledger(z11_rows)
    return {
        "status": "EXACT_ORTHOGONAL_OBSTRUCTION__FORMER_LOCAL_REPAIR_RETRACTED_BY_COMMON_NORMALIZATION",
        "basis": {
            "order": ["U1L_SU5_squared", "U1L_X_squared"],
            "SU5_index": "T(5)=1/2, T(10)=3/2, T(24)=5",
            "X_trace": "dimension times X^2",
            "normalization": "ordinary 4D localized-Weyl anomaly polynomial: a left Weyl of normal charge q contributes q*(T(R),dim(R) X^2)",
        },
        "von_Gersdorff_factor": {
            "formula": "kappa(eta)=4 w(eta)^2-5/16",
            "weights_eta_1_i_minus1_minusi": [fstr(Z4_WEIGHTS[m]) for m in range(4)],
            "kappa_eta_1_i_minus1_minusi": [fstr(kappa(m)) for m in range(4)],
            "fixed_density_c1_eta_1_i_minus1_minusi": [fstr(mixed_index_weight(m)) for m in range(4)],
            "common_normalization_conversion": "kappa=2*c1; Eq. 4.3-4.5 calibrates |qL|=1/2 to one A2 unit, so a local Weyl contributes 2qL in the kappa/A2 convention and qL in the c1/index-polynomial convention used below",
        },
        "adjoint_branching": [
            {
                "representation": name,
                "eta": ("1", "i", "-1", "-i")[m % 4],
                "kappa": fstr(kappa(m)),
                "c1_mixed_weight": fstr(mixed_index_weight(m)),
                "T_SU5": fstr(index),
                "dimension": dim,
                "X": charge,
            }
            for name, m, index, dim, charge in ADJOINT_U5
        ],
        "weighted_adjoint_trace_before_chirality": [fstr(x) for x in weighted_adjoint],
        "gaugino_opposite_chirality": [fstr(x) for x in vector],
        "three_full_11_hypers": {
            "each_intrinsic_phase_m0123": {
                name: [fstr(x) for x in values] for name, values in eleven_rows.items()
            },
            "all_zero": all(values == (0, 0) for values in eleven_rows.values()),
        },
        "F70_bulk_result_each_Z4_corner": [fstr(x) for x in vector],
        "U1L_squared_X_ledger": {
            "spin_half_x2_coefficients_m0123": [fstr(c2[m]) for m in range(4)],
            "adjoint_before_chirality": fstr(adjoint_x2_X_before_chirality),
            "gaugino": fstr(gaugino_x2_X),
            "one_11_m0123": [fstr(eleven_x2_X_trace(m)) for m in range(4)],
            "integer_m301_total_with_gaugino": fstr(m301_x2_X),
            "flavor_Wilson_total_with_gaugino": fstr(flavor_x2_X),
            "both_V70_branches_zero": m301_x2_X == flavor_x2_X == 0,
        },
        "z11_prime_basis": "WQ has the same eigenvalue multiplicities, so the result is identical in U(5)'",
        "Z2_result": "0 because cos(pi/2)=0 in the spin-half remnant-Lorentz trace",
        "standard_bulk_GS": {
            "Spin11_invariant": "tr_11 F^2",
            "restriction_to_U5": [fstr(x) for x in bulk_direction],
            "reason": "11=5_2+5bar_-2+1_0 gives (T_SU5,X^2)=(1,40)",
            "all_tensor_couplings_same_gauge_direction": True,
            "determinant_with_F70_vector": fstr(determinant),
            "orthogonal_component_nonzero": determinant != 0,
            "ordinary_bulk_GS_can_cancel_F70_vector": False,
        },
        "complete_16_check": {
            "branching": "16=10_-1+5bar_3+1_-5",
            "trace_direction": [fstr(x) for x in family16_direction],
            "equals_two_times_bulk_direction": family16_direction == tuple(2 * x for x in bulk_direction),
            "conclusion": "a complete localized 16 with one normal charge cannot remove the orthogonal component",
        },
        "minimal_singlet_pair_repair": {
            "status": "FAILS_STANDALONE_ALIGNMENT_BY_FACTOR_TWO_AFTER_COMMON_NORMALIZATION",
            "representations": ["1_(+10)", "1_(-10)"],
            "required_fermion_normal_charge_sum": fstr(pair_qsum),
            "mixed_shift": [fstr(x) for x in pair_shift],
            "repaired_vector": [fstr(x) for x in repaired],
            "aligned_target_vector": [fstr(x) for x in aligned_target],
            "required_net_local_shift_without_the_pair": [fstr(x) for x in required_net_shift],
            "pair_overshoot_relative_to_alignment": [fstr(x) for x in pair_overshoot],
            "conditional_z00_compensating_axion_variation": [fstr(x) for x in z00_compensating_axion],
            "aligns_with_bulk_direction": repaired == aligned_target,
            "symmetric_charge_witness": ["-1/2", "-1/2"],
            "symmetric_pair_additional_local_I6": {
                "x3": fstr(local_pair_x3),
                "x_p1T4": fstr(local_pair_xp),
                "formula": "-x^3/24+x p1(T4)/24",
            },
            "scope": "the pair's local polynomial is exact, but it overshoots the mixed correction needed for GS alignment and also creates cubic-normal and normal-gravity terms",
        },
        "minimal_R_compatible_four_fermion_module": {
            "fermion_content": [
                "psi_X: 1_(+10), qL=-1/2",
                "psi_Xbar: 1_(-10), qL=-1/2",
                "psi_S: gauge neutral, qL=+1/2",
                "psi_P: gauge neutral, qL=+1/2",
            ],
            "superspace_lift": "qL(theta)=+1/2; scalar charges are (0,0,1,1), mapping to V70-like Z4R charges (0,0,2,2)",
            "Q1": fstr(repair_Q1),
            "Q3": fstr(repair_Q3),
            "U1L_squared_X": fstr(pair_x2_X),
            "ordinary_X_cubed_and_gravity_X": "0 because the charged pair is vectorlike",
            "U1L_X_squared": "-100",
            "only_nonzero_local_anomaly_component": "U1L-X^2=-100 in the common local-Weyl convention",
            "standalone_mixed_repair": "FAIL: the unmodified bulk needs -50, so this module overshoots by -50",
            "conditional_z00_axion_variation_after_module": "+50 in U1L-X^2",
            "restores_bulk_Delta_condition": "Delta_f=-10 because Q1=Q3=0",
            "minimality": (
                "one half-integrally charged neutral fermion cannot make the "
                "factorization equation admit an integer Delta; two q=+1/2 do"
            ),
            "new_fields_relative_to_V70": {
                "z00": "V70 has the X pair and one R=2 driver S0; the contract still needs one independent R=2 neutral P0 and a pinned isotropy lift",
                "z11": "the entire primed pair plus two neutral R=2 drivers is new",
            },
            "supersymmetric_mass_and_VEV_theorem": {
                "fermion_charge_sum": "qpsi_X+qpsi_Xbar=r_X+r_Xbar-1 for qL(theta)=1/2",
                "bare_mass": "M X Xbar requires r_X+r_Xbar=1 and therefore qpsi sum 0; it cannot make the needed anomaly shift",
                "repair_assignment": "r_X=r_Xbar=0 gives qpsi sum -1",
                "allowed_driver": "r_S=1 permits W=S(X Xbar-v^2) and maps to Z4R(S)=2",
                "z11_boundary": "the primed pair must remain at zero VEV because 1'_(+/-10) has common hypercharge +/-2",
            },
            "localized_family_contract": "V70 R=1 family scalars map to qL=1/2 and qL(psi_16)=0; alternatively any uniform 16 charge shifts only the GS direction (2,80)",
        },
        "corrected_spinorial_U5_preimage_modules": {
            "status": "EXACT_PERTURBATIVE_IN_PROVISIONAL_SPINORIAL_PREIMAGE__GLOBAL_ORBIBUNDLE_AND_MICROSCOPIC_MASSES_OPEN",
            "charge_lattice_reason": "1_(+/-5) are representations of the spinorial preimage U(5)-tilde in Spin(11): the restricted 16 contains 1_(-5) in 16=10_(-1)+5bar_(3)+1_(-5)",
            "global_form_boundary": "a literal vector-form U(5) in the X normalization of 11=5_(2)+5bar_(-2)+1 permits singlet characters in multiples of 10; the charge-five witness therefore requires the Spin(11) preimage already suggested by V70 localized 16s, and its global orbibundle quotient must still be pinned",
            "V70_z00_R_charge_binding": {
                "source_path": "localized_parent_completion_branches.integer_m301_dynamical_reduction.complete_renormalizable_local_operator_ledger.Z4R_charges",
                "X_Xbar": v70_r_charges["X_Xbar"],
                "S0": v70_r_charges["S0"],
                "normal_lift_used": "qL(theta)=1/2 gives qpsi(X,Xbar,S0)=(-1/2,-1/2,+1/2)",
            },
            "required_local_shift_each_Z4": [fstr(x) for x in required_net_shift],
            "z00_complete_ledger": z00_module,
            "z00_new_fields_relative_to_V70": 7,
            "z00_interpretation": "the inherited X(+/-10) pair contributes -100 and S0 contributes only to Q1/Q3; four new 1_(+/-5) fields contribute +50 and three qL=-1/2 neutrals close Q1=Q3=0",
            "z11_complete_ledger": z11_module,
            "z11_new_fields_relative_to_V70": 8,
            "z11_hypercharge": "for an SU(5)' singlet Y=X'/5, so 1'_(+/-5) has Y=+/-1; there are two vectorlike charged-lepton pairs",
            "mass_boundary": "bare superpotential masses are Z4R-forbidden at both corners; at z11 the R-neutral and normal-neutral Kahler bilinears can generate only m3/2-scale Giudice-Masiero masses, while at z00 each charged scalar has continuous normal charge +1 and its bilinear needs a charge -2 spurion/section or a proven reduction to the discrete symmetry; all z00 masses, decay portals and cosmology remain open",
            "both_mixed_vectors_align": (
                z00_module["U1L_X_squared"] == "-50"
                and z11_module["U1L_X_squared"] == "-50"
            ),
            "aligned_total_vector_each_Z4": [fstr(x) for x in aligned_target],
            "old_pair_no_go": "an honest vectorlike 1_(+10)+1_(-10) pair has two half-integral qL charges, hence integer q-sum and an X^2 shift in multiples of 100; it cannot supply -50",
            "scope_boundary": "this is an exact local perturbative anomaly witness, not a mass spectrum, defect superpotential, global H-bundle, discrete-R anomaly cancellation or Dai-Freed completion",
        },
        "locality": {
            "z00": "the corrected complete ledger uses the existing X/Xbar pair and S0 plus seven new local singlet chirals",
            "z11": "the corrected complete ledger requires eight new primed local singlet chirals",
            "one_corner_cannot_cancel_the_other": True,
        },
    }


def identity(n: int) -> list[list[complex]]:
    return [[complex(int(i == j)) for j in range(n)] for i in range(n)]


def matmul(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> list[list[complex]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def dagger(a: Sequence[Sequence[complex]]) -> list[list[complex]]:
    return [[complex(a[j][i]).conjugate() for j in range(len(a))] for i in range(len(a[0]))]


def matpow(a: Sequence[Sequence[complex]], exponent: int) -> list[list[complex]]:
    result = identity(len(a))
    base = [list(row) for row in a]
    while exponent:
        if exponent & 1:
            result = matmul(result, base)
        base = matmul(base, base)
        exponent //= 2
    return result


def trace(a: Sequence[Sequence[complex]]) -> complex:
    return sum(a[i][i] for i in range(len(a)))


def neutral_witness_matrix_audit() -> dict[str, Any]:
    # A e_k=e_(k+1), U=diag(i,-1,-i,-1), V=diag(-1,i,-1,-i).
    A = [[0j for _ in range(4)] for _ in range(4)]
    for k in range(4):
        A[(k + 1) % 4][k] = 1 + 0j
    U = [[0j for _ in range(4)] for _ in range(4)]
    V = [[0j for _ in range(4)] for _ in range(4)]
    for k, value in enumerate((1j, -1 + 0j, -1j, -1 + 0j)):
        U[k][k] = value
    for k, value in enumerate((-1 + 0j, 1j, -1 + 0j, -1j)):
        V[k][k] = value
    one = identity(4)
    UA = matmul(U, A)
    checks = {
        "A4": matpow(A, 4) == one,
        "UV_commute": matmul(U, V) == matmul(V, U),
        "A_U_Ainverse_equals_V": matmul(matmul(A, U), dagger(A)) == V,
        "A_V_Ainverse_equals_Uinverse": matmul(matmul(A, V), dagger(A)) == dagger(U),
        "UA4": matpow(UA, 4) == one,
        "A_nontrivial_power_traces_zero": all(trace(matpow(A, j)) == 0 for j in (1, 2, 3)),
        "UA_nontrivial_power_traces_zero": all(trace(matpow(UA, j)) == 0 for j in (1, 2, 3)),
        "no_translation_constant_basis_vector": all(
            not (U[k][k] == 1 and V[k][k] == 1) for k in range(4)
        ),
    }
    return {
        "status": "EXACT_4_ORBIT_MATRIX_WITNESS",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def naive_wcs_torsion_divisibility_audit() -> dict[str, Any]:
    def row(name: str, order: int, p1_tangent_weight_sum: int, p1_gauge_weight_sum: int) -> dict[str, Any]:
        p_t = p1_tangent_weight_sum % order
        p_e = p1_gauge_weight_sum % order
        two_y = ((p_t - 2 * p_e) % order, (p_t + p_e) % order)
        doubling_image = sorted({(2 * value) % order for value in range(order)})
        divisible = all(value in doubling_image for value in two_y)
        return {
            "locus": name,
            "isotropy": f"Z{order}",
            "cohomology": f"H4(BZ{order};U)=(Z{order})^2",
            "p1_Tperp_weight_sum": p1_tangent_weight_sum,
            "p1_E11_weight_sum": p1_gauge_weight_sum,
            "classes_mod_order": {"p1_Tperp": p_t, "p1_E11": p_e},
            "two_Y_mod_order": list(two_y),
            "doubling_image_each_coordinate": doubling_image,
            "Y_exists_in_ordinary_integral_cohomology": divisible,
        }

    z00 = row("z00", 4, 1, 5)
    z11 = row("z11", 4, 1, 29)
    z2 = row("z10_z01", 2, 1, 2)
    rows = [z00, z11, z2]
    return {
        "status": "EXACT_NAIVE_SMOOTH_MMP_COCYCLE_TORSION_DIVISIBILITY_NO_GO",
        "generator": "u in H2(BZn;Z)=Zn; u^2 generates H4(BZn;Z)",
        "weight_rule": "for a real two-plane of complex isotropy weight w, p1=w^2 u^2",
        "ordinary_smooth_cocycle": {
            "lambda": "p1(T)/2",
            "c2_Spin11": "p1(E11)/2",
            "Y_in_U_basis": ["lambda-2c2", "lambda+c2"],
            "twice_Y": ["p1(T)-2p1(E11)", "p1(T)+p1(E11)"],
        },
        "local_weight_sums": {
            "z00": "tangent 1; Q has five vector-plane weights 1, so p1(E11)=5u^2",
            "z11": "tangent 1; WQ has two weights 1 and three weights 3, so p1(E11)=(2+27)u^2=29u^2",
            "z10_z01": "tangent 1; R flips two vector planes, so p1(E11)=2u^2",
        },
        "rows": rows,
        "all_loci_fail_ordinary_divisibility": all(not row_["Y_exists_in_ordinary_integral_cohomology"] for row_ in rows),
        "interpretation": (
            "the smooth Spin(11) shifted cocycle has no naive restriction to the "
            "orbifold isotropy groups; an R/flavor torsion correction and generalized "
            "integral lift of lambda on the combined H-structure are mandatory"
        ),
        "minimal_restriction_level_corrections_to_twice_Y": {
            "Z4": "the first coordinate must be odd; delta=(1,0)u^2 is the smallest choice and changes (3,2) to (0,2)",
            "Z2": "delta=(1,1)u^2 is mandatory and changes (1,1) to (0,0)",
            "SU2R_alone": "p1(R)=u_n^2 at both strata, so one fixed U-vector coefficient cannot realize both correction patterns",
        },
        "local_relative_halves_and_gluing_obstruction": {
            "lambda_H": "(p1(T)-p1(R))/2 is locally integral because w2(T)=w2(R)",
            "Z4_c2_relative": "(p1(E11)-p1(R))/2 is locally integral and can make the local Y class zero",
            "Z2_boundary": "E11 is already spin with p1(E11)=0, while w2(E11) differs from w2(R)",
            "conclusion": "the local relative halves do not define one global class; an H-characteristic cocycle must be constructed and glued",
        },
        "not_a_no_go_for": "a newly constructed combined Spin-SU2R-Sp266-Spin11 equivariant cocycle",
    }


def continuous_stueckelberg_audit() -> dict[str, Any]:
    return {
        "status": "NO_CONTINUOUS_HYPERCHARGE_OR_X_STUECKELBERG_FOR_FLAT_TORSION_HOLONOMY",
        "orbifold_gauge_background": {
            "data": "Q and W are finite flat space-group holonomies",
            "de_Rham_internal_curvature": "0",
            "fixed_point_characteristic_classes": "torsion only",
        },
        "bulk_GS_reduction": {
            "schematic_coefficient": "k_A proportional to integral_(T2/Z4) tr(T_A F_internal)",
            "value": "0",
            "cohomological_reason": "pushforward of torsion into the free group H2(BU1;Z)=Z cannot generate a nonzero continuous BF coefficient",
            "coarse_delta_flux_warning": "a branch-dependent delta-flux representative describes the same flat stack bundle and does not change the de Rham integral",
        },
        "four_dimensional_crosscheck": {
            "V70_zero_mode_gauge_anomalies": "all zero",
            "two_form_mass_rule": "a canceled mixed U1 anomaly breaks the U1 only if it survives in the 4D theory",
            "forced_mass_for_hypercharge": False,
            "forced_mass_for_X": False,
        },
        "allowed_remaining_effects": [
            "a discrete differential-cohomology phase",
            "a continuous mass from deliberately added nonzero real internal flux",
            "a continuous mass from a localized axion chosen to shift under the gauge U1",
        ],
        "repair_design_rule": "a z11 defect axion should shift under normal U1L, not hypercharge, if it is to preserve the massless gauge group",
        "assumptions": [
            "no additional real internal flux",
            "the eventual generalized H-cocycle does not introduce a gauge-shifting localized axion",
        ],
    }


def equivariant_wcs_boundary() -> dict[str, Any]:
    torsion = naive_wcs_torsion_divisibility_audit()
    return {
        "status": "SMOOTH_PARENT_WUCS_DATA_PASS__ORBIFOLD_EQUIVARIANT_WUCS_OPEN",
        "smooth_parent_imported_from_V70": {
            "lattice": "U with Omega=[[0,1],[1,0]]",
            "a": [2, 2],
            "a_characteristic": True,
            "b": [2, -1],
            "integral_unimodular": True,
            "global_form": "Spin(11)",
            "reduced_Omega7_spin_BSpin11": "0",
            "smooth_shifted_WCS_verdict": "PASS, subject to the ordinary self-dual-string/tadpole caveat",
        },
        "SO11_fallback_fails": {
            "pullback": "the H4(BSO11;Z) generator pulls back to twice the H4(BSpin11;Z) generator",
            "strong_quantization_requirement": "b must lie in 2U in Spin normalization",
            "b": [2, -1],
            "b_is_even": False,
            "verdict": "FAIL",
        },
        "ordinary_spin_orbifold_obstruction": {
            "geometric_spin_lift": "L_theta=exp(pi Gamma45/4)",
            "L_theta_fourth": "-1",
            "conclusion": "there is no order-four lift Z4 -> Spin(2) covering the 90-degree rotation",
        },
        "preserved_supersymmetry_structure": {
            "SU2R_lift_fourth": "-1",
            "combined_fourth": "(L_theta,U_R)^4=(-1,-1)=+1 after the diagonal Z2 quotient",
            "required_tangential_structure": "a combined Spin-SU(2)R equivariant structure, not an ordinary independent spin lift",
        },
        "gauge_lift_boundary": {
            "qhat_fourth": "-1 in Spin(11)",
            "vector_and_adjoint": "the center is invisible",
            "spinorial_or_global_bundle": "requires the combined quotient/global orbibundle to be specified",
        },
        "why_smooth_WCS_is_not_enough": [
            "the cited smooth construction assumes a smooth spin spacetime and an independently defined gauge bundle",
            "the present quotient has fixed strata and only a diagonal Spin-SU(2)R lift",
            "fixed-stratum differential cocycles, tensor boundary conditions and torsion refinements are not supplied by V70",
            "replacing Spin(11) by SO(11) does not evade the central lift: b=(2,-1) fails the SO global-form quantization condition",
        ],
        "naive_orbifold_torsion_divisibility": torsion,
        "continuous_Stueckelberg": continuous_stueckelberg_audit(),
        "perturbative_equivariant_index_scope": "computes the local polynomial used here but not torsion, eta holonomy or global gluing",
        "equivariant_GS_descent_constructed": False,
        "Dai_Freed_phases_computed": False,
    }


def repair_candidate() -> dict[str, Any]:
    return {
        "id": "F71",
        "name": "corrected two-corner spinorial U(5)-preimage charge-lattice frontier after factor-two retraction",
        "status": "EXACT_LOCAL_PERTURBATIVE_WITNESS_IN_PROVISIONAL_SPINORIAL_PREIMAGE__MASS_DECAY_GLOBAL_AND_QUANTUM_COMPLETION_OPEN",
        "selected_for_next_frontier": True,
        "accepted": False,
        "same_action_complete": False,
        "supersedes": ["F70", "F70_ALT"],
        "required_new_data": [
            "at z00, pin the Spin(11) preimage U(5)-tilde lift, retain the existing X(+10),Xbar(-10),S0 fields and assign/pin their F71 continuous normal lifts, then add two copies each of 1_(+5),1_(-5) with qL=+1/2 plus three neutral qL=-1/2 chirals",
            "at z11, pin the conjugate preimage lift and add two copies each of 1'_(+5),1'_(-5) with qL=-1/2 plus four neutral qL=+1/2 chirals",
            "construct R-compatible masses and decay portals for the new vectorlike charged singlets without destabilizing the rank-breaking vacuum or the proton selector",
            "globalize the explicit Sp(266,1)/(Sp(266)xSp(1)) target-space isometry to a combined Spin-SU2R-Sp266 orbifold H-bundle",
            "construct an equivariant GS/Wu-Chern-Simons differential cocycle on the combined Spin-SU(2)R-gauge orbifold structure",
            "cancel the complete localized U1L^3, U1L-gravity, discrete-R and eta/Dai-Freed anomaly ledgers",
        ],
        "exact_required_variation_ledger": {
            "common_normalization": "bulk=(-1/4,40), GS direction=(1,40), so the aligned target is (-1/4,-10)",
            "mixed_gauge_normal_at_z00": "the complete inherited-plus-seven-new module contributes (0,-50), so (-1/4,40)+(0,-50)=(-1/4,-10)=(-1/4)(1,40)",
            "mixed_gauge_normal_at_z11": "the eight-new-chiral primed module contributes (0,-50), giving the same aligned vector",
            "four_fermion_module_moments": "Q1=Q3=U1L^2-X=X^3=grav-X=0, but U1L-X^2=-100 overshoots the needed -50",
            "corrected_modules_spectator_moments": "Q1=Q3=U1L^2-X=X^3=grav-X=0 independently at both corners",
            "bulk_plus_corrected_modules_normal_gravity": "Delta_00=Delta_11=-10 still gives -(1/8)x p1(T6)",
            "Z2_normal_polynomial": "0",
            "neutral_zero_mode_count": 10,
            "continuous_hypercharge_or_X_Stueckelberg_from_flat_bulk_holonomy_forced": False,
        },
        "repair_options": {
            "selected_hybrid": {
                "z00": "inherited X/Xbar/S0 plus seven-new-chiral 1_(+/-5) compensator module",
                "z11": "eight-new-chiral 1'_(+/-5) compensator module",
                "why_selected": "uses the Spin(11) spinorial-preimage charge lattice and closes every perturbative spectator moment without an unquantized axion",
                "z11_primed_hypercharge": "+/-1 for the charged singlets",
                "mass_decay_cosmology_complete": False,
            },
            "alternate_fermion_module_at_z11": {
                "alignment": "FAIL in the claimed half-integral assignment: it shifts -100 where -50 is needed",
                "problem": "besides the factor-two failure, the charged pair has Y=+/-2, no R-preserving bare mass, and creates exotic decay/cosmology obligations",
                "accepted": False,
            },
        },
        "not_yet_passes": [
            "the corrected local representations have an exact anomaly ledger, but their full defect superpotential, masses, decays and vacuum Hessian are not constructed",
            "the symmetric quaternionic target/isometry is explicit, but its global H-bundle and the ten neutral-mode stabilization are not constructed",
            "the primed hypercharge Y=+/-1 exotics require a viable mass/decay/cosmology analysis and the discrete-R anomaly ledger must be recomputed",
            "factorization is necessary but no generalized global GS/Wu-CS H-cocycle has been constructed",
        ],
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (Path(__file__).resolve(), TEST_PATH, V70_PATH)
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    v70 = load_v70()
    spin_half = spin_half_index_audit()
    gravity = gravity_tensor_index_audit()
    charged = charged_bulk_normal_gravity_audit()
    neutral = neutral_phase_audit()
    mixed = mixed_normal_gauge_audit(v70)
    witness = neutral_witness_matrix_audit()
    wcs = equivariant_wcs_boundary()
    candidate = repair_candidate()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "primary_sources": PRIMARY_SOURCES,
        "lineage": {
            "bound_V70_path": V70_PATH.name,
            "bound_V70_core": v70["core_sha256"],
            "expected_V70_core": EXPECTED_V70_CORE,
            "V70_core_matches": v70["core_sha256"] == EXPECTED_V70_CORE,
            "imported": [
                "genuine Spin/SU2R charged lift",
                "F70 integer-m301 and F70_ALT flavor-Wilson charged branches",
                "fixed-locus U5, U5-prime and Spin4xSpin7 branching",
                "smooth U-lattice Green-Schwarz coefficients",
            ],
            "not_imported": [
                "a completed normal-bundle anomaly",
                "localized U1L charges",
                "an equivariant Green-Schwarz or Wu-Chern-Simons action",
            ],
        },
        "spin_half_equivariant_index": spin_half,
        "gravity_tensor_equivariant_index": gravity,
        "charged_bulk_normal_gravity_ledger": charged,
        "neutral_266_phase_classification": neutral,
        "neutral_four_orbit_matrix_witness": witness,
        "mixed_normal_gauge_obstruction": mixed,
        "equivariant_GS_WuCS_boundary": wcs,
        "F71_repair_candidate": candidate,
        "acceptance": {
            "F70_unmodified": "REJECTED_BY_Z11_MIXED_NORMAL_GAUGE_ANOMALY",
            "F70_ALT_unmodified": "REJECTED_BY_Z11_MIXED_NORMAL_GAUGE_ANOMALY",
            "F71_perturbative_alignment": "PASS_EXACT_CONDITIONAL_ON_SPINORIAL_PREIMAGE_GLOBAL_FORM",
            "F71_microscopic_supergravity_action": "OPEN_NOT_CONSTRUCTED",
            "neutral_hyper_target_isometry": "PASS_EXACT_LOCAL_SYMMETRIC_QK_WITNESS",
            "neutral_global_H_bundle": "OPEN",
            "full_local_normal_anomaly": "OPEN",
            "equivariant_GS_WuCS": "OPEN",
            "global_anomaly": "OPEN",
            "continuous_hypercharge_or_X_Stueckelberg_from_flat_holonomy": "PASS_NOT_FORCED",
        },
        "frontier_status_ledger": [
            "SMOOTH_SPIN11_WCS_PASS_EXACT",
            "ORDINARY_SPIN_ORBIFOLD_FAIL_EXACT",
            "INDEPENDENT_SPIN11_ORBIBUNDLE_FAIL_EXACT",
            "SO11_FALLBACK_QUANTIZATION_FAIL_EXACT",
            "NAIVE_FIXED_STRATUM_MMP_COCYCLE_FAIL_EXACT",
            "COMBINED_H_TANGENTIAL_STRUCTURE_CONSTRUCTED_CLASSICALLY",
            "GLOBAL_H_DIFFERENTIAL_COCYCLE_AND_OMEGA7_OPEN",
            "NEUTRAL_QK_SPACE_GROUP_LIFT_PASS_EXACT",
            "Z4_NORMAL_POLYNOMIAL_GS_ALIGNED_NOT_CANCELLED",
            "Z4_MIXED_NORMAL_GAUGE_ORTHOGONAL_FAIL_FOR_UNMODIFIED_F70",
            "Z00_PAIR_PLUS_TWO_NEUTRALS_STANDALONE_REPAIR_FAIL_FACTOR_TWO",
            "CORRECTED_PROVISIONAL_SPINORIAL_U5_PREIMAGE_MODULES_PASS_EXACT_LOCAL_PERTURBATIVE",
            "CONTINUOUS_STUECKELBERG_NOT_FORCED",
            "G1_TO_G8_OPEN",
        ],
        "open_obligations": [
            "globalize the explicit symmetric quaternionic-Kahler target/isometry to the combined orbifold H-bundle and stabilize its ten neutral chiral zero modes",
            "specify every localized field's normal U1L lift at z00 and z11 and cancel U1L^3, U1L-gravity and mixed anomalies together",
            "construct and quantize the equivariant GS/Wu-Chern-Simons differential cocycle on the combined tangential structure",
            "compute fixed-stratum eta/Dai-Freed phases and the global Spin-SU2R-Spin11/flavor quotient",
            "construct masses, decay portals, vacuum stabilization and cosmology for the new z00 and primed z11 charge-five singlet modules and recompute the discrete-R ledger",
            "complete the KK determinant, regulator, thresholds, all-order operator ring, soft spectrum, unification and cosmology",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V71 rejects both unmodified V70 candidates by a nonzero mixed "
                "normal-gauge component at the second Z4 corner.  It derives the "
                "unique neutral phase imbalance Delta=-10, proves a ten-neutral-zero-"
                "mode lower bound, embeds its sharp witness in a symmetric QK target, "
                "and retracts the former four-fermion repair after a factor-two "
                "normalization check.  It replaces it with exact local fermion modules "
                "in the provisional spinorial U(5)-preimage lattice at both Z4 corners; "
                "their global group form, mass, decay, vacuum "
                "and cosmology sectors are not constructed.  The "
                "naive smooth WCS cocycle also fails an exact local torsion-divisibility "
                "test.  The repair is not a global microscopic supergravity action and "
                "does not supply the required generalized equivariant quantum theory."
            ),
            "current_V70_candidates_viable_without_new_local_data": False,
            "F71_accepted": False,
            "all_gates_closed": False,
            "theory_complete": False,
        },
        "source_manifest": source_manifest(),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    mixed = report["mixed_normal_gauge_obstruction"]
    neutral = report["neutral_266_phase_classification"]
    checks = {
        "V70_bound": report["lineage"]["V70_core_matches"],
        "spin_half_exact": report["spin_half_equivariant_index"]["all_compact_forms_exact"],
        "charged_plus4": report["charged_bulk_normal_gravity_ledger"]["z00_equals_z11"],
        "neutral_zero_incompatible": neutral["cannot_vanish"]["requirements_incompatible"],
        "neutral_delta_minus10": neutral["bulk_gravitational_trace_factorization"]["unique_Delta"] == -10,
        "localized_factorization_formula": neutral["general_localized_extension"]["full_directional_factorization_equation"] == "100+10 Delta_f+32 Q3_f+8 Q1_f=0",
        "neutral_ten_minimum": neutral["two_corner_zero_mode_theorem"]["minimum_neutral_chiral_zero_modes"] == 10,
        "neutral_witness_266": neutral["explicit_266_dimensional_witness"]["dimension"] == 266,
        "neutral_witness_delta": neutral["explicit_266_dimensional_witness"]["Delta_at_each_corner"] == -10,
        "matrix_witness": report["neutral_four_orbit_matrix_witness"]["all_checks_pass"],
        "eleven_zero": mixed["three_full_11_hypers"]["all_zero"],
        "mixed_common_normalization": mixed["von_Gersdorff_factor"]["common_normalization_conversion"].startswith("kappa=2*c1"),
        "det_minus50": mixed["standard_bulk_GS"]["determinant_with_F70_vector"] == "-50",
        "bulk_GS_fails": not mixed["standard_bulk_GS"]["ordinary_bulk_GS_can_cancel_F70_vector"],
        "former_pair_repair_fails": not mixed["minimal_singlet_pair_repair"]["aligns_with_bulk_direction"],
        "corrected_required_shift": mixed["minimal_singlet_pair_repair"]["required_net_local_shift_without_the_pair"] == ["0", "-50"],
        "conditional_z00_compensator": mixed["minimal_singlet_pair_repair"]["conditional_z00_compensating_axion_variation"] == ["0", "50"],
        "corrected_charge_lattice_modules_align": mixed["corrected_spinorial_U5_preimage_modules"]["both_mixed_vectors_align"],
        "corrected_charge_lattice_spectators_zero": (
            mixed["corrected_spinorial_U5_preimage_modules"]["z00_complete_ledger"]["all_spectator_anomalies_zero"]
            and mixed["corrected_spinorial_U5_preimage_modules"]["z11_complete_ledger"]["all_spectator_anomalies_zero"]
        ),
        "V70_z00_R_charges_bound": mixed["corrected_spinorial_U5_preimage_modules"]["V70_z00_R_charge_binding"]["X_Xbar"] == 0
        and mixed["corrected_spinorial_U5_preimage_modules"]["V70_z00_R_charge_binding"]["S0"] == 2,
        "bulk_x2X_zero": mixed["U1L_squared_X_ledger"]["both_V70_branches_zero"],
        "four_fermion_module_pure_zero": (
            mixed["minimal_R_compatible_four_fermion_module"]["Q1"] == "0"
            and mixed["minimal_R_compatible_four_fermion_module"]["Q3"] == "0"
            and mixed["minimal_R_compatible_four_fermion_module"]["U1L_squared_X"] == "0"
        ),
        "source_manifest_complete": (
            {row["path"] for row in report["source_manifest"]}
            == {Path(__file__).name, TEST_PATH.name, V70_PATH.name}
            and all(row["exists"] and row["sha256"] for row in report["source_manifest"])
        ),
        "WCS_open": not report["equivariant_GS_WuCS_boundary"]["equivariant_GS_descent_constructed"],
        "naive_WCS_torsion_fails": report["equivariant_GS_WuCS_boundary"]["naive_orbifold_torsion_divisibility"]["all_loci_fail_ordinary_divisibility"],
        "no_forced_continuous_Stueckelberg": (
            not report["equivariant_GS_WuCS_boundary"]["continuous_Stueckelberg"]["four_dimensional_crosscheck"]["forced_mass_for_hypercharge"]
            and not report["equivariant_GS_WuCS_boundary"]["continuous_Stueckelberg"]["four_dimensional_crosscheck"]["forced_mass_for_X"]
        ),
        "F71_unaccepted": not report["F71_repair_candidate"]["accepted"],
        "all_gates_open": all(value == "OPEN" for value in report["gate_ledger"].values()),
        "core_exact": report.get("core_sha256") == canonical_sha(report),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V71 validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    mixed = report["mixed_normal_gauge_obstruction"]
    neutral = report["neutral_266_phase_classification"]
    candidate = report["F71_repair_candidate"]
    return f"""# V71 Spin(11) normal-bundle and equivariant-GS audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact new obstruction

V70 canceled the ordinary localized gauge polynomial, but a codimension-two
fixed point also has the remnant normal Lorentz group `U(1)_L`.  For
`x=c1(N)`, von Gersdorff's order-four coefficient is

```text
kappa(eta)=4 w(eta)^2-5/16
w(1,i,-1,-i)=(3,1,-1,-3)/8
kappa=(+1,-1,-1,+1)/4,
c1(index density)=kappa/2.
```

At either `U(5)` corner,

```text
55 = 24_0 + 1_0 + 10_4 + 10bar_-4 + 5_2 + 5bar_-2.
```

Equation (4.3)-(4.5) calibrates one localized Weyl of `|qL|=1/2` to one
`A2` unit.  Therefore a local Weyl contributes `2qL` in the kappa convention,
or `qL` in the common index-polynomial convention used for both bulk and local
fields below.  The weighted adjoint trace in that convention is `(1/4,-40)` in the basis
`(SU5^2,X^2)`.  Gaugino chirality reverses it, giving

```text
I_F70^(U1L-gauge) = (-1/4,+40).
```

Every full `11` contributes exactly `(0,0)`, independently of its intrinsic
phase.  The only bulk Spin(11) gauge invariant restricts as
`tr_11 F^2 -> (1,40)`.  Their determinant is
`{mixed['standard_bulk_GS']['determinant_with_F70_vector']}`, so standard bulk
GS inflow cannot cancel the orthogonal component.  `WQ` has the same spectrum,
therefore the result holds at the inequivalent `U(5)'` corner.  The V70 action
has no local primed repair there.  Both unmodified V70 candidates are rejected.

## Exact neutral/gravity theorem

The equivariant spin-half sum gives

```text
I6^H(m)=s_m (11 x^3+x p1(T4))/192,
s_(0,1,2,3)=(-1,+1,+1,-1).
```

The gauge-fixed gravitino plus tensorino is the virtual Dirac bundle
`-(T_C M6-2)` and contributes

```text
I6^(G+T)=(42 x^3-18 x p1(T4))/192.
```

With the standard identical tensor lift, the self-dual and anti-self-dual
signature complexes cancel pointwise.  Both V70 charged branches contribute
another `4(11x^3+xp)/192`.  If
`Delta_f=N1_f+N2_f-N0_f-N3_f` for the 266 neutral hypers, the full bulk result
at a Z4 corner is

```text
{neutral['total_polynomial']}.
```

It cannot vanish.  For bulk fields alone it is aligned with the bulk gravitational trace
`x p1(T6)=x[p1(T4)+x^2]` if and only if
`Delta_f={neutral['bulk_gravitational_trace_factorization']['unique_Delta']}`;
then it is exactly `-(1/8)x p1(T6)`.

Localized left Weyl fermions change this condition.  Defining
`Q1=sum d q_L` and `Q3=sum d q_L^3`, the full necessary directional test is

```text
100+10 Delta_f+32 Q3_f+8 Q1_f=0.
```

For an arbitrary finite-dimensional unitary flavor space-group lift,
translation-character orbits of length four or two have zero common Delta,
and the translation `(-1,-1)` fixed space contributes with opposite signs at
the two corners.  Thus `Delta_00=Delta_11=-10` can come only from the
translation-trivial sector.  There the negative phases `m=0,3` are precisely
neutral chiral zero modes, proving

```text
N_neutral_zero >= 10.
```

The bound is sharp.  Ten trivial `m=0` blocks plus 64 explicit four-orbits
have dimension 266, Delta `-10` at both corners, and exactly ten neutral
chiral zero modes.  Every matrix space-group relation is checked in the JSON.
It has an explicit nonlinear realization on the symmetric quaternionic-Kahler
target `Sp(266,1)/(Sp(266)xSp(1))`.  Writing `A_eff` for the tested superfield
matrix, the underlying flavor lift is `A_F=zeta A_eff`, so `A_F^4=-1`.
Together with `U_R^4=-1`, the scalar action is honest order four in the
diagonal-center isotropy quotient; `A_F^-1` is exactly the calibrated
hyperino projector.  The nontrivial translations embed in `U(266) subset
Sp(266)` and remove every four-orbit constant mode.  What remains open is the
global combined H-bundle over the orbifold and stabilization of the ten
neutral chirals, not the local target/isometry witness.

The remaining factorized `-(1/8)x p1(T6)` cannot be canceled by conventional
localized fermions of half-integral Spin(2) charge alone.  Cancellation would
require `sum q=-3` and `sum q^3=3/4`; with odd integers `r=2q`, this says
`sum r=-6` and `sum r^3=+6`, contradicting `r^3=r (mod 24)`.  A tensor/GS
inflow (or separately specified nonstandard twisted isotropy) is genuinely
required.

## F71 retraction and corrected charge-lattice witness

At `z00`, a local `1_(+10)+1_(-10)` pair with fermion charges
`(-1/2,-1/2)` shifts `(0,-100)`, but alignment requires only `(0,-50)`:

```text
(-1/4,40)+(0,-100)=(-1/4,-60) != a(1,40).
```

This retracts the former standalone repair.  More generally, two half-integral
normal charges in a vectorlike `1_(+10)+1_(-10)` pair have integer sum, so their
`X^2` shift is a multiple of 100 and can never equal -50.

There is nevertheless an exact perturbative solution in the provisional
spinorial `U(5)`-preimage charge lattice.  At `z00`, use
the inherited `X_(+10),Xbar_(-10),S0` with qL `(-1/2,-1/2,+1/2)`, add two
copies each of `1_(+5),1_(-5)` with qL `+1/2`, and add three neutral qL `-1/2`
chirals.  The complete ten-field ledger has

```text
(U1L-SU5^2,U1L-X^2)=(0,-50),
Q1=Q3=U1L^2-X=X^3=gravity-X=0.
```

Only seven of these fields are new relative to V70.  At `z11`, two copies each
of `1'_(+5),1'_(-5)` with qL `-1/2` plus four neutral qL `+1/2` chirals give
the same exact ledger.  The spinorial preimage contains `1_(-5)` in the
restricted 16; a literal vector-form `U(5)` would instead allow singlet
characters only in multiples of 10.  Thus the witness requires the preimage
suggested by V70's localized 16s, while the global orbibundle quotient remains
to be pinned.  With
`qL(theta)=+1/2`, every scalar has integral normal charge and Z4R charge 0 or 2.

For a primed SU(5) singlet `Y=X'/5`, so the z11 charged states have
hypercharge `+/-1`, giving two vectorlike charged-lepton pairs.  Bare
superpotential masses are Z4R-forbidden.  At z11, normal-neutral Kahler
bilinears allow gravitino-scale Giudice-Masiero masses.  At z00, however, each
new charged scalar has continuous normal charge `+1`, so its bilinear has
charge `+2` and needs a charge `-2` spurion/section or a proven reduction to the
discrete symmetry.  The z00 masses, all decay portals, discrete-R anomalies and
cosmology have not been completed.  The flat Q/W background still has zero real internal flux,
so bulk torsion holonomy alone forces no continuous hypercharge or X
Stueckelberg mass.

F71 combines these exact local perturbative modules with the exact
266-dimensional neutral witness.  Its status is `{candidate['status']}`.
The local polynomial now aligns, but no global equivariant tensor cocycle or
same-action phenomenological completion has yet been built.

## Why the smooth Wu--Chern--Simons pass does not close the orbifold

The 90-degree tangent lift obeys `L_theta^4=-1`; it is not an ordinary Z4 spin
lift.  Supersymmetry works only after pairing it with the SU(2)R lift, whose
fourth power is also `-1`, and taking the diagonal quotient.  Likewise the
genuine Spin(11) lift has `qhat^4=-1`.  The smooth-parent lattice
`U, a=(2,2), b=(2,-1)` still passes its integral/characteristic and smooth
degree-seven bordism tests for `Spin(11)`.  Replacing it by `SO(11)` is not an
escape: strong global-form quantization would require `b` to be even in `U`,
while `(2,-1)` is not.  A smooth-spin Wu--Chern--Simons construction cannot
simply be imported as the
fixed-stratum, combined-structure orbifold action.  The equivariant index used
here fixes the perturbative polynomial only; torsion and eta phases remain
open.

There is an exact torsion obstruction to the naive restriction.  With
`u` generating `H^2(BZ_n;Z)`, the ordinary smooth cocycle is

```text
Y=(lambda-2c2,lambda+c2),
2Y=(p1(T)-2p1(E11),p1(T)+p1(E11)).
```

At either Z4 corner, `p1(T)=u^2` and `p1(E11)=u^2` modulo four, so
`2Y=(3,2)u^2` in `(Z4)^2`.  Doubling has image `{{0,2}}` and the first
coordinate has no preimage.  At the Z2 locus, `2Y=(1,1)u^2` while doubling
is zero.  Thus an R/flavor torsion correction and generalized integral
`lambda` on the combined H-structure are mandatory.  This rejects the naive
smooth descent, not every possible new combined cocycle.

## Decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

""" + "".join(f"- {item}\n" for item in report["open_obligations"]) + "\nG1-G8 remain OPEN.\n"


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V71 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V71 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V71 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
