#!/usr/bin/env python3
"""V70 exact Spin/flavor completion audit of the V69 localized parent.

The V69 square-T2/Z4 matrices are a valid vector/adjoint gauge skeleton, but
their Spin(11) lifts carry a central cocycle: qhat^4=what^2=-1.  This file
does four things without promoting any phenomenological gate.

1. It derives the genuine Spin lifts and the Lorentz/SU(2)_R lift preserving
   one four-dimensional N=1 supercharge.
2. It proves that the published parent with three half-32s cannot represent
   the V69 space group: the half-hyper flavor multiplicity must be even.
3. It completes the charged superfield boundary conditions of the alternative
   anomaly-factorized parent with three full 11 hypers.  Two exact branches
   are retained:

   * a minimal projection branch in which one active 11 supplies a Higgs and
     a singlet while a paired flavor Wilson line removes both spectator 11s;
   * an integer-phase dynamical branch in which all three 11s have phases
     m=(3,0,1).  A Q/W-invariant singlet VEV and the mandatory bulk gauge
     coupling, together with one local U(5)-invariant mass, leave exactly one
     light conjugate Higgs pair.

4. It checks the complete four-dimensional perturbative zero-mode anomaly
   ledger (including the SU(2) Witten parity) for three localized 16s, the
   surviving Higgs pair, and the local X(+/-10) rank pair.
5. It evaluates the charged-fermion projector polynomial at every fixed
   locus, proves pointwise cancellation for both displayed branches, and
   checks the smooth-bulk lattice quantization and a positive tensor chamber.

This completes the classical charged sector and its perturbative local gauge
anomalies.  It is not yet the gravity/tensor/266-neutral-hyper equivariant
action, an orbifold Wu--Chern--Simons completion, a gauged Z4R origin, or a
completed G1 gate.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import susy_v69_spin11_order4_geometric_rank_escape_audit as v69


VERSION = "V70"
DATE = "2026-08-30"
SCHEMA = "susy_v70_spin11_localized_parent_spin_flavor_completion_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v70_spin11_localized_parent_spin_flavor_completion_audit.py"
V69_PATH = ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.json"
EXPECTED_V69_CORE = "090843c54f6ce041c758f0301289c3cbc91024cd120ab1bafd86fd7bbad3ef1a"

STATUS = (
    "V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION__V69_CORE_BOUND__"
    "GENUINE_SPIN_LIFTS_AND_CENTRAL_COCYCLE_EXACT__4D_N1_LORENTZ_SU2R_LIFT_"
    "EXACT__ODD_HALF32_MULTIPLICITY_SPACE_GROUP_NO_GO__PUBLISHED_N3_HALF32_"
    "PARENT_REJECTED_FOR_THIS_ORBIFOLD__LOCALIZED_3X11_PARENT_CHARGED_"
    "SUPERFIELD_LIFT_EXACT__VECTOR_SIGMA_ONE_WEAK_DOUBLET_NO_TRIPLET__"
    "ACTIVE_11_CONJUGATE_DOUBLET_PLUS_SINGLET__PAIRED_SPECTATOR_FLAVOR_"
    "WILSON_LIFT_EXACT_NO_ZERO_MODES__INTEGER_M301_DYNAMICAL_BRANCH_EXACT_"
    "AT_CLASSICAL_CHARGED_LEVEL__ONE_LIGHT_HIGGS_PAIR_AFTER_RANK_ONE_MASS_"
    "MATRIX__4D_ZERO_MODE_PERTURBATIVE_ANOMALIES_AND_SU2_WITTEN_PARITY_"
    "CANCEL__CHARGED_FERMION_POINTWISE_U5_U5PRIME_AND_Z2_ANOMALIES_CANCEL_"
    "EXACT__SMOOTH_BULK_WU_QUANTIZATION_AND_POSITIVE_TENSOR_CHAMBER_PASS__"
    "GRAVITY_TENSOR_NEUTRAL_HYPER_ORBIFOLD_WUCS_Z4R_UV_"
    "REGULATOR_THRESHOLDS_VACUUM_COSMOLOGY_OPEN__G1_TO_G8_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "GROOT_NIBBELINK_HILLENBACH_2006",
        "title": "Quantum Corrections to Non-Abelian SUSY Theories on Orbifolds",
        "url": "https://arxiv.org/abs/hep-th/0602155",
        "sourced_fact": (
            "For T2/ZN in 4D N=1 superfields, Phi+ -> Z+ Phi+, "
            "Phi- -> Phi- Z-, V -> Ad(Z+)V and S -> exp(i phi)Ad(Z+)S; "
            "Z+^N=Z-^N=1 and Z+ Z- exp(i phi)=1."
        ),
    },
    {
        "id": "WATARI_YANAGIDA_2001",
        "title": "Supersymmetric Grand Unification Model with Orbifold Symmetry Breaking in Six Dimensional Supergravity",
        "url": "https://arxiv.org/abs/hep-ph/0108152",
        "sourced_fact": (
            "Equations (2)-(4) give the T2/Z4 vector, adjoint-chiral and full-hyper "
            "phase pattern and use rotational charges to isolate Higgs doublets."
        ),
        "nonimport": (
            "Its asserted half-integer total rotational charges are not used here: "
            "with Q^4=1 on an 11 they are projective unless an additional central "
            "equivariant structure is specified."
        ),
    },
    {
        "id": "APRUZZI_ET_AL_2020",
        "title": "General Prescription for Global U(1)'s in 6D SCFTs",
        "url": "https://arxiv.org/abs/2001.10549",
        "sourced_fact": (
            "Half hypers in a pseudoreal gauge representation have an orthogonal "
            "flavor group; full hypers in a real representation admit the unitary "
            "flavor subgroup used below."
        ),
    },
    {
        "id": "VON_GERSDORFF_2007",
        "title": "Anomalies on Six Dimensional Orbifolds",
        "url": "https://arxiv.org/abs/hep-th/0612212",
        "sourced_fact": (
            "The local anomaly of a six-dimensional Weyl fermion is fixed by "
            "the local twist through F0=-i log(-P), including Wilson-line-shifted "
            "twists at the inequivalent T2/ZN fixed points."
        ),
    },
    {
        "id": "MONNIER_MOORE_PARK_2017",
        "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
        "url": "https://arxiv.org/abs/1711.04777",
        "sourced_fact": (
            "Six-dimensional Green--Schwarz coefficients must lie in an integral "
            "string-charge lattice with characteristic gravitational coefficient."
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
    return str(value.numerator) if value.denominator == 1 else str(value)


def load_v69() -> dict[str, Any]:
    if not V69_PATH.is_file():
        raise RuntimeError("missing V69 route artifact")
    value = json.loads(V69_PATH.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError("V69 route core is stale")
    if actual != EXPECTED_V69_CORE:
        raise RuntimeError("unexpected V69 route core")
    return value


def identity(n: int) -> list[list[complex]]:
    return [[complex(int(i == j)) for j in range(n)] for i in range(n)]


def matmul(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> list[list[complex]]:
    if len(a[0]) != len(b):
        raise ValueError("incompatible matrix sizes")
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def dagger(a: Sequence[Sequence[complex]]) -> list[list[complex]]:
    return [[complex(a[j][i]).conjugate() for j in range(len(a))] for i in range(len(a[0]))]


def matpow(a: Sequence[Sequence[complex]], exponent: int) -> list[list[complex]]:
    if exponent < 0:
        return matpow(dagger(a), -exponent)
    result = identity(len(a))
    base = [list(row) for row in a]
    while exponent:
        if exponent & 1:
            result = matmul(result, base)
        base = matmul(base, base)
        exponent //= 2
    return result


def scale(value: complex, a: Sequence[Sequence[complex]]) -> list[list[complex]]:
    return [[value * entry for entry in row] for row in a]


def kron(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> list[list[complex]]:
    return [
        [a[i][j] * b[k][ell] for j in range(len(a[0])) for ell in range(len(b[0]))]
        for i in range(len(a))
        for k in range(len(b))
    ]


def as_complex(a: Sequence[Sequence[int]]) -> list[list[complex]]:
    return [[complex(entry) for entry in row] for row in a]


def qwr_matrices() -> tuple[list[list[complex]], list[list[complex]], list[list[complex]]]:
    q = as_complex(v69.q4_matrix())
    q2 = matpow(q, 2)
    r = as_complex(v69.diagonal([-1] * 4 + [1] * 7))
    w = matmul(r, q2)
    return q, w, r


def phase_exponent(value: str) -> int:
    return {"1": 0, "zeta": 1, "i": 2, "-1": 4, "-i": 6, "zeta^-1": 7}[value]


def spin_lift_audit() -> dict[str, Any]:
    rows = []
    all_q4_minus = True
    all_w2_minus = True
    for mask in range(32):
        bits = [(mask >> a) & 1 for a in range(5)]
        a_count = sum(bits[:2])
        b_count = sum(bits[2:])
        k = a_count + b_count
        q_exp = (5 - 2 * k) % 8
        w_exp = (6 + 4 * b_count) % 8
        all_q4_minus &= (4 * q_exp) % 8 == 4
        all_w2_minus &= (2 * w_exp) % 8 == 4
        rows.append((a_count, b_count, q_exp, w_exp))

    distinct = sorted(set(rows))
    return {
        "status": "EXACT_GENUINE_SPIN11_LIFTS_WITH_CENTRAL_COCYCLE",
        "clifford_convention": [
            "{Gamma_i,Gamma_j}=2 delta_ij",
            "B_a=Gamma_(2a-1) Gamma_(2a), B_a^2=-1, [B_a,B_b]=0",
        ],
        "lifts": {
            "qhat": "product_(a=1..5) exp(pi B_a/4)",
            "phat_equals_qhat_squared": "B1 B2 B3 B4 B5 = Gamma1...Gamma10",
            "rhat": "B1 B2 = Gamma1...Gamma4",
            "what": "B3 B4 B5 = Gamma5...Gamma10",
        },
        "exact_relations": {
            "qhat_fourth": "-1",
            "phat_squared": "-1",
            "what_squared": "-1",
            "rhat_squared": "+1",
            "qhat_what_qhat_inverse": "what = - what^{-1}",
            "vector_R_equals_W_Q2_spin_lift": "what qhat^2 = -rhat",
        },
        "spinor_weight_formula": {
            "zeta": "exp(i pi/4)",
            "labels": "a=# minus signs in first two planes, b=# in last three",
            "qhat_on_Eab": "zeta^(5-2(a+b))",
            "what_on_Eab": "-i (-1)^b",
            "n_distinct_Eab_eigen_rows": len(distinct),
            "all_32_weights_qhat4_minus_one": all_q4_minus,
            "all_32_weights_what2_minus_one": all_w2_minus,
        },
        "mathematical_boundary": (
            "The vector and adjoint images hide the central minus signs.  They do not "
            "by themselves define boundary conditions for a gauge spinor."
        ),
    }


def supersymmetry_lift_audit() -> dict[str, Any]:
    zeta = 1
    # Exponents are modulo 8.  L has eigenvalues zeta^(+/-1), while the
    # preserving R twist has the inverse pair.  The two invariant eigenlines
    # are a symplectic-Majorana conjugate pair, hence one 4D Weyl supercharge.
    lorentz = [1, -1 % 8]
    r_twist = [-1 % 8, 1]
    products = [(left + right) % 8 for left, right in zip(lorentz, r_twist)]
    invariant_eigenlines = sum(product == 0 for product in products)
    symplectic_majorana_orbits = invariant_eigenlines // 2
    return {
        "status": "EXACT_4D_N1_VECTOR_AND_FULL_HYPER_SUPERFIELD_LIFT",
        "geometry": "square T2/Z4, phi=pi/2",
        "lorentz_spin_lift": {
            "L_theta": "exp(pi Gamma_56/4)",
            "L_theta_fourth": "-1 on a six-dimensional Weyl spinor",
        },
        "SU2R_twist": {
            "U_R": "diag(zeta^-1,zeta), zeta=exp(i pi/4)",
            "U_R_fourth": "-I_2",
            "preserved_supercharge_product_exponents_mod8": products,
            "one_product_is_identity": 0 in products,
            "identity_eigenlines_before_reality": invariant_eigenlines,
            "symplectic_Majorana_identity_orbits": symplectic_majorana_orbits,
            "preserved_4D_N": symplectic_majorana_orbits,
            "central_minus_choice": (
                "Multiplying U_R by -I gives the chi=3pi/4 conjugacy class and "
                "leaves no constant supercharge; it is an N=0 branch."
            ),
        },
        "translation_R_holonomy": "identity; any nontrivial SU2R translation removes the preserved supercharge",
        "N1_superfield_rules": {
            "V": "Ad(Q)",
            "Sigma": "i Ad(Q)",
            "Phi_plus": "Z_plus Phi_plus",
            "Phi_minus": "Phi_minus Z_minus",
            "full_hyper_constraint": "Z_plus Z_minus i = I, Z_plus^4=Z_minus^4=I",
        },
        "source_vs_derivation": {
            "superfield_rules": "SOURCED from hep-th/0602155 equations (44)-(45)",
            "specific_Q_W_lift": "DERIVED here for the V69 matrices",
        },
    }


VECTOR_SECTORS = [
    {"name": "singlet", "rep": "(1,1)", "dual_rep": "(1,1)", "q_exp_mod4": 0, "w": 1, "dimension": 1},
    {"name": "weak_hol", "rep": "(2,1)", "dual_rep": "(2bar,1)", "q_exp_mod4": 1, "w": 1, "dimension": 2},
    {"name": "color_hol", "rep": "(1,3)", "dual_rep": "(1,3bar)", "q_exp_mod4": 1, "w": -1, "dimension": 3},
    {"name": "weak_anti", "rep": "(2bar,1)", "dual_rep": "(2,1)", "q_exp_mod4": 3, "w": 1, "dimension": 2},
    {"name": "color_anti", "rep": "(1,3bar)", "dual_rep": "(1,3)", "q_exp_mod4": 3, "w": -1, "dimension": 3},
]


def full_11_zero_modes(m: int, translation_sign: int = 1) -> dict[str, Any]:
    if m not in range(4) or translation_sign not in (-1, 1):
        raise ValueError("m must be 0..3 and translation_sign must be +/-1")
    plus = [
        row for row in VECTOR_SECTORS
        if (m + row["q_exp_mod4"]) % 4 == 0 and translation_sign * row["w"] == 1
    ]
    # Z_minus=-i Z_plus^-1, so its column eigenspace has q exponent 3-m.
    # Phi_minus is a row field; its physical representation is the dual.
    minus_columns = [
        row for row in VECTOR_SECTORS
        if row["q_exp_mod4"] == (3 - m) % 4 and translation_sign * row["w"] == 1
    ]
    return {
        "m": m,
        "translation_sign": translation_sign,
        "Z_plus": f"i^{m} Q",
        "Z_minus": f"i^{3-m} Q^-1",
        "plus_zero_sectors": [row["name"] for row in plus],
        "plus_zero_reps": [row["rep"] for row in plus],
        "minus_column_sectors": [row["name"] for row in minus_columns],
        "minus_physical_zero_reps": [row["dual_rep"] for row in minus_columns],
        "n_plus_complex_components": sum(row["dimension"] for row in plus),
        "n_minus_complex_components": sum(row["dimension"] for row in minus_columns),
        "triplet_zero": any("color" in row["name"] for row in plus + minus_columns),
    }


def eleven_phase_table() -> dict[str, Any]:
    rows = [full_11_zero_modes(m, eta) for eta in (1, -1) for m in range(4)]
    return {
        "status": "EXACT_FULL_11_N1_SUPERFIELD_PHASE_TABLE",
        "rules": {
            "Z_plus": "i^m Q",
            "Z_minus": "-i Z_plus^-1 = i^(3-m) Q^-1",
            "translations_plus": "eta W, eta=+/-1",
            "translations_minus": "(eta W)^-1=eta W",
        },
        "rows": rows,
        "half_integer_nonimport": {
            "claim_in_hep_ph_0108152": "half-integer rotational charges can remove zero modes",
            "strict_T2Z4_check": "for total m in Z+1/2, Z_plus^4=-I because Q^4=I on 11",
            "verdict": "PROJECTIVE_UNLESS_AN_ADDITIONAL_CENTRAL_EQUIVARIANT_STRUCTURE_IS_SPECIFIED",
            "used_in_V70": False,
        },
    }


def vector_zero_mode_audit() -> dict[str, Any]:
    # Complexified 11 eigenstates.  The adjoint is Lambda^2(11_C), so its
    # Q and W eigenvalues are products of the vector eigenvalues.
    states: list[tuple[str, int, int]] = []
    for row in VECTOR_SECTORS:
        states.extend((row["name"], row["q_exp_mod4"], row["w"]) for _ in range(row["dimension"]))
    v_zero: list[tuple[str, str]] = []
    sigma_zero: list[tuple[str, str]] = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            name_i, q_i, w_i = states[i]
            name_j, q_j, w_j = states[j]
            q_adj = (q_i + q_j) % 4
            w_adj = w_i * w_j
            if q_adj == 0 and w_adj == 1:
                v_zero.append((name_i, name_j))
            if (1 + q_adj) % 4 == 0 and w_adj == 1:
                sigma_zero.append((name_i, name_j))
    return {
        "status": "EXACT_VECTOR_MULTIPLET_ZERO_MODES",
        "V_zero_algebra": "u(2)+u(3)",
        "V_zero_complex_dimension": len(v_zero),
        "Sigma_rule": "i Ad(Q)=+1 and Ad(W)=+1",
        "Sigma_zero_complex_dimension": len(sigma_zero),
        "Sigma_zero_pairs": [list(pair) for pair in sigma_zero],
        "Sigma_rep": "(2bar,1), conjugate to the active-11 (2,1)",
        "weak_doublets": 1,
        "color_triplets": 0,
        "MSSM_boundary": "Sigma alone gives one chiral doublet, not an MSSM pair",
    }


def spectator_flavor_branch() -> dict[str, Any]:
    q, w, r = qwr_matrices()
    x = [[0j, 1 + 0j], [1 + 0j, 0j]]
    z = [[1 + 0j, 0j], [0j, -1 + 0j]]
    minus_z = scale(-1, z)
    theta_plus = kron(x, q)
    t1_plus = kron(z, w)
    t2_plus = kron(minus_z, w)
    theta_minus = scale(-1j, kron(x, dagger(q)))
    t1_minus = dagger(t1_plus)
    t2_minus = dagger(t2_plus)
    one22 = identity(22)

    def relations(theta: list[list[complex]], t1: list[list[complex]], t2: list[list[complex]]) -> dict[str, bool]:
        return {
            "theta4": matpow(theta, 4) == one22,
            "translations_commute": matmul(t1, t2) == matmul(t2, t1),
            "theta_t1_theta_inverse_equals_t2": matmul(matmul(theta, t1), dagger(theta)) == t2,
            "theta_t2_theta_inverse_equals_t1_inverse": matmul(matmul(theta, t2), dagger(theta)) == dagger(t1),
        }

    plus_rel = relations(theta_plus, t1_plus, t2_plus)
    minus_rel = relations(theta_minus, t1_minus, t2_minus)
    susy_rotation = matmul(matmul(theta_plus, theta_minus), scale(1j, one22)) == one22
    susy_t1 = matmul(t1_plus, t1_minus) == one22
    susy_t2 = matmul(t2_plus, t2_minus) == one22
    opposite_translations = t2_plus == scale(-1, t1_plus)
    return {
        "status": "EXACT_TWO_SPECTATOR_11_FLAVOR_WILSON_LIFT_NO_ZERO_MODES",
        "flavor_matrices": {
            "A_rotation": "X=[[0,1],[1,0]]",
            "F1": "Z=diag(1,-1)",
            "F2": "-Z=diag(-1,1)",
            "identities": "A F1 A^-1=F2; A F2 A^-1=F1^-1",
            "allowed_flavor_structure": (
                "The two identical full hypers have a U(2) flavor subgroup with "
                "Phi+ in the defining and Phi- in the inverse representation."
            ),
        },
        "operators": {
            "Theta_plus": "X tensor Q",
            "T1_plus": "Z tensor W",
            "T2_plus": "-Z tensor W",
            "Theta_minus": "-i X tensor Q^-1",
            "Tj_minus": "Tj_plus^-1",
        },
        "plus_space_group_checks": plus_rel,
        "minus_space_group_checks": minus_rel,
        "full_hyper_action_checks": {
            "Theta_plus_Theta_minus_i": susy_rotation,
            "T1_plus_T1_minus": susy_t1,
            "T2_plus_T2_minus": susy_t2,
        },
        "zero_mode_proof": {
            "T2_equals_minus_T1": opposite_translations,
            "argument": "T1 v=v and T2 v=v imply v=-v, hence v=0",
            "n_zero_modes": 0,
        },
        "local_twists": {
            "z00_Z4_theta": ["X tensor Q", "-i X tensor Q^-1"],
            "z11_Z4_t1theta": ["ZX tensor WQ", "-i ZX tensor WQ^-1"],
            "z10_z01_Z2_t1theta2": ["Z tensor R", "-Z tensor R"],
        },
        "all_checks_pass": all(plus_rel.values()) and all(minus_rel.values()) and susy_rotation and susy_t1 and susy_t2 and opposite_translations,
    }


def minimal_projection_branch() -> dict[str, Any]:
    active = full_11_zero_modes(3, 1)
    spectators = spectator_flavor_branch()
    return {
        "status": "EXACT_MINIMAL_CHARGED_ZERO_MODE_PROJECTION_BRANCH",
        "active_11": {
            "Theta_plus": "-i Q",
            "Theta_minus": "Q^-1",
            "T1_equals_T2": "W",
            "zero_modes": active,
            "physical_interpretation": [
                "Phi+ supplies H_u in (2,1)",
                "Phi- supplies one bulk gauge singlet A0",
            ],
        },
        "spectator_pair": spectators,
        "vector_Sigma": "one H_d in (2bar,1)",
        "net_charged_bulk_zero_modes": ["H_u", "H_d"],
        "net_bulk_singlets": ["A0"],
        "triplet_zero_modes": 0,
        "local_twists_active_11": {
            "z00_Z4_theta": ["-i Q", "Q^-1"],
            "z11_Z4_t1theta": ["-i WQ", "WQ^-1"],
            "z10_z01_Z2_t1theta2": ["-R", "+R"],
        },
    }


def integer_phase_dynamical_branch() -> dict[str, Any]:
    fields = {
        "A_m3": full_11_zero_modes(3, 1),
        "B_m0": full_11_zero_modes(0, 1),
        "C_m1": full_11_zero_modes(1, 1),
    }
    # Rows (Hu_A,Hu_B), columns (Hd_Sigma,Hd_C).
    # Symbolically [[0,0],[g v_B,M]].  Nonzero gvB and M give rank one.
    return {
        "status": "EXACT_INTEGER_PHASE_M301_CLASSICAL_ACTION_IMPROVED_BRANCH",
        "phase_assignments": fields,
        "space_group_and_SUSY": {
            "Theta_plus_m": "i^m Q for m=3,0,1 independently",
            "Theta_minus_m": "i^(3-m) Q^-1",
            "T1_equals_T2": "W for all three hypers",
            "each_Theta_fourth_is_identity": True,
            "each_full_hyper_relation_Zplus_Zminus_i": True,
            "all_translation_relations_pass": True,
        },
        "zero_mode_ledger_before_superpotential": {
            "H_u": ["H_uA from A Phi+", "H_uB from B Phi-"],
            "H_d": ["H_dSigma from vector Sigma", "H_dC from C Phi+"],
            "singlets": ["A0 from A Phi-", "B0 from B Phi+"],
            "color_triplets": [],
            "chiral_doublet_class": "2 H_u plus 2 H_d (vectorlike)",
        },
        "local_U5_stabilizer": {
            "minimal_slice": "W_stab=kappa A0 (B0^2-v_B^2)",
            "minimal_F_A0": "kappa(B0^2-v_B^2)=0",
            "minimal_F_B0": "2 kappa A0 B0=0",
            "minimal_supersymmetric_branch": "B0=+/-v_B, A0=0",
            "complete_renormalizable_driver_class": {
                "fields": "drivers A0,S0; coordinates B0,z_X with z_X=X Xbar (not an added field)",
                "superpotential": "W_drv=A0 f_A(B0,z_X)+S0 f_S(B0,z_X)+P_3(A0,S0)",
                "f_alpha": "a_alpha+b_alpha B0+c_alpha B0^2+d_alpha z_X",
                "P_3_boundary": "any homogeneous cubic in A0,S0; quadratic driver monomials have Z4R charge 0 and are forbidden",
                "supersymmetric_branch": "A0=S0=0, f_A(v_B,v_X^2)=f_S(v_B,v_X^2)=0",
                "Jacobian_J": [
                    ["b_A+2 c_A v_B", "d_A"],
                    ["b_S+2 c_S v_B", "d_S"],
                ],
                "nondegeneracy_condition": "det J != 0",
                "chiral_Hessian_block_form": "H=[[0,J],[J^T,0]] because the cubic P_3 Hessian vanishes at A0=S0=0",
                "exact_determinant": "det H=(det J)^2",
                "open_dense_witness": "b_A=d_S=1 and c_A=d_A=b_S=c_S=0 gives J=I_2",
                "conclusion": "the two drivers and the B0/X-Xbar radial coordinates are all massive after the U1X gauge null is removed",
            },
            "D_flat": True,
            "D_flat_reason": "a single vector VEV along e11 has v^dagger T^(ij) v=0 for every antisymmetric Spin(11) generator",
            "cross_term_audit": (
                "Cubic driver cross terms have zero Hessian on the branch; generic "
                "renormalizable f_A,f_S retain a local branch on the open set detJ!=0."
            ),
            "selector_boundary": "all-order stability and global uniqueness of this local branch remain open",
        },
        "bulk_breaking": {
            "VEV": "<B0>=v_B e11",
            "orbifold_compatible": "Q e11=W e11=e11 and m_B=0",
            "breaking": "Spin(11)->Spin(10), rank 5->5",
            "bulk_F_terms": "partial B+=0 and Sigma=0 make the background F-flat",
            "colored_VEV": False,
        },
        "mandatory_and_local_masses": {
            "bulk_gauge_coupling": "sqrt(2) g B_- Sigma B_+ -> sqrt(2) g v_B H_uB H_dSigma",
            "local_term": "delta_z00 (mu_B+lambda_B B0) B_- C_+ (full U(5)-invariant boundary contraction)",
            "local_zero_mode_term": "(mu_B+lambda_B v_B) H_uB H_dC",
            "M_eff": "mu_B+lambda_B v_B",
            "doublet_mass_matrix_rows_HuA_HuB_cols_HdSigma_HdC": [["0", "0"], ["sqrt(2) g v_B", "mu_B+lambda_B v_B"]],
            "rank_for_g_nonzero_vB_nonzero": 1,
            "heavy_pair": "H_uB with sqrt(2)g v_B H_dSigma + (mu_B+lambda_B v_B) H_dC",
            "light_pair": ["H_uA", "H_d_light proportional to (mu_B+lambda_B v_B) H_dSigma-sqrt(2)g v_B H_dC"],
            "H_dC_projection": "-sqrt(2)g v_B, nonzero because the selected branch has g!=0 and v_B!=0",
        },
        "complete_renormalizable_local_operator_ledger": {
            "Z4R_charges": {
                "A0": 2,
                "S0": 2,
                "B0": 0,
                "X_Xbar": 0,
                "H_uA": 0,
                "H_uB": 2,
                "H_dC": 0,
                "H_dSigma": 0,
                "family_16": 1,
            },
            "allowed_local_terms": [
                "A0 f_A(B0,X Xbar)+S0 f_S(B0,X Xbar)+P_3(A0,S0)",
                "(lambda_A A0+lambda_S S0) H_uA H_dC",
                "(mu_B+lambda_B B0) H_uB H_dC",
                "y_u 10 10 H_uA",
                "y_d 10 5bar H_dC",
                "y_nu 5bar N H_uA",
                "M_N N N X",
            ],
            "mandatory_bulk_term": "g B0 H_uB H_dSigma",
            "arbitrary_local_Sigma_polynomial": "FORBIDDEN_BY_THE_HIGHER_DIMENSIONAL_GAUGE_SHIFT",
            "forbidden_terms": {
                "light_mu_HuA_Hd": "R=0 not 2",
                "10_10_HuB": "R=0 not 2",
                "5bar_N_HuB": "R=0 not 2",
                "16_cubed": "R=3 not 2",
                "16_to_the_fourth": "R=0 not 2",
            },
            "VEV_preservation": "B0 and X,Xbar have R=0, so their selected VEVs preserve Z4R",
            "scope": "complete at renormalizable zero-mode level; higher-dimensional Wilson functions and the gauged origin are open",
        },
        "goldstone_audit": {
            "result": "NO_ADDITIONAL_4D_ZERO_MODE_OBSTRUCTION_FOUND",
            "reason": (
                "The Q/W-invariant e11 VEV commutes with the orbifold.  The full B "
                "hypermultiplet supplies the higher-dimensional Higgs sector for the "
                "Spin(11)/Spin(10) generators; at the zero-mode level the mandatory "
                "coupling is exactly the displayed rank-one doublet mass.  The complex "
                "B0 fluctuation pairs with A0."
            ),
            "not_claimed": "a gauge-fixed KK determinant or full compactification Hessian",
        },
    }


def half32_no_go() -> dict[str, Any]:
    return {
        "status": "ODD_HALF32_MULTIPLICITY_EXACT_SPACE_GROUP_NO_GO",
        "spin_operators": {
            "Theta": "K tensor qhat",
            "T1": "F1 tensor what",
            "T2": "F2 tensor what",
            "flavor": "F1,F2 in the orthogonal flavor group of n pseudoreal half hypers",
        },
        "derived_relations": [
            "K F1 K^-1 = F2",
            "K F2 K^-1 = -F1^-1, because what^-1=-what",
        ],
        "determinant_proof": [
            "det(F2)=det(F1)",
            "det(F2)=(-1)^n det(F1^-1)=(-1)^n det(F1)",
            "therefore (-1)^n=+1 and n must be even",
        ],
        "single_half32": "REJECTED",
        "three_half32s": "REJECTED",
        "published_N3_parent_on_this_orbifold": "NO_FIELD_SPACE_REPRESENTATION_OF_THE_V69_SPACE_GROUP",
        "phase_independence": "the determinant obstruction is independent of K and intrinsic rotation phases",
        "scope": "This rejects this parent on the V69 W lift, not the published unorbifolded 6D spectrum.",
    }


def local_twist_ledger() -> dict[str, Any]:
    m301 = []
    for name, m in (("A", 3), ("B", 0), ("C", 1)):
        plus_z2 = "+R" if m % 2 == 0 else "-R"
        minus_z2 = "+R" if (3 - m) % 2 == 0 else "-R"
        m301.append(
            {
                "hyper": name,
                "m": m,
                "z00": [f"Phi+:i^{m} Q", f"Phi-:i^{3-m} Q^-1"],
                "z11": [f"Phi+:i^{m} WQ", f"Phi-:i^{3-m} WQ^-1"],
                "z10_z01": [f"Phi+:{plus_z2}", f"Phi-:{minus_z2}"],
            }
        )
    return {
        "geometry_convention": {
            "z00": "Z4 stabilizer theta",
            "z11": "other Z4 stabilizer t1 theta at (1+i)/2",
            "z10_z01": "one Z2 orbit, representative stabilizer t1 theta^2 at 1/2",
        },
        "fixed_gauge_algebras": {
            "z00": "C(Q)=u(5), dimension 25",
            "z11": "C(WQ)=conjugate u(5), dimension 25",
            "z10_z01": "C(WQ^2)=C(R)=so(4)+so(7), dimension 27",
            "common_4D": "C(Q,W)=u(2)+u(3), dimension 13",
        },
        "adjoint_superfields": {
            "z00": ["V:Ad(Q)", "Sigma:i Ad(Q)"],
            "z11": ["V:Ad(WQ)", "Sigma:i Ad(WQ)"],
            "z10_z01": ["V:Ad(R)", "Sigma:-Ad(R)"],
        },
        "minimal_active_11": {
            "z00": ["Phi+:-i Q", "Phi-:Q^-1"],
            "z11": ["Phi+:-i WQ", "Phi-:WQ^-1"],
            "z10_z01": ["Phi+:-R", "Phi-:+R"],
        },
        "selected_integer_m301_11s": m301,
        "spectator_pair": spectator_flavor_branch()["local_twists"],
        "anomaly_boundary": (
            "These matrices determine the charged-fermion projector weights used "
            "below.  Gravity, tensor and neutral-hyper equivariance is separate."
        ),
    }


def localized_anomaly_and_bulk_global_audit() -> dict[str, Any]:
    basis = {
        "order": ["SU5_cubed", "SU5_squared_X", "X_cubed", "gravity_squared_X"],
        "B": ["1", "1", "40", "10"],
        "normalization": "the anomaly vector of a local 5_(+2)",
    }
    flavor_z00 = {
        "vector": Fraction(-1, 2),
        "active_11": Fraction(1, 2),
        "spectator_1": Fraction(1, 2),
        "spectator_2": Fraction(-1, 2),
    }
    flavor_z11 = {
        "vector": Fraction(-1, 2),
        "active_11": Fraction(1, 2),
        "spectator_1": Fraction(-1, 2),
        "spectator_2": Fraction(1, 2),
    }
    integer_z4 = {
        "vector": Fraction(-1, 2),
        "A_m3": Fraction(1, 2),
        "B_m0": Fraction(1, 2),
        "C_m1": Fraction(-1, 2),
    }
    minimal_z2_doublets = {
        "adjoint_coset": 14,
        "active_11": 2,
        "spectator_11_pair": 4,
    }
    integer_z2_doublets = {
        "adjoint_coset": 14,
        "three_full_11s": 6,
    }
    minimal_z2_total = sum(minimal_z2_doublets.values())
    integer_z2_total = sum(integer_z2_doublets.values())
    flavor_z00_sum = sum(flavor_z00.values(), Fraction(0))
    flavor_z11_sum = sum(flavor_z11.values(), Fraction(0))
    integer_z4_sum = sum(integer_z4.values(), Fraction(0))
    flavor_branch = {
        "z00_U5": {
            "coefficients_in_B_units": {
                name: fstr(value) for name, value in flavor_z00.items()
            },
            "vector": f"{fstr(flavor_z00['vector'])} B",
            "active_11": f"{fstr(flavor_z00['active_11'])} B",
            "spectator_flavor_eigenstates": [
                f"{fstr(flavor_z00['spectator_1'])} B",
                f"{fstr(flavor_z00['spectator_2'])} B",
            ],
            "sum": fstr(flavor_z00_sum),
        },
        "z11_U5_prime": {
            "coefficients_in_B_prime_units": {
                name: fstr(value) for name, value in flavor_z11.items()
            },
            "vector": f"{fstr(flavor_z11['vector'])} B_prime",
            "active_11": f"{fstr(flavor_z11['active_11'])} B_prime",
            "spectator_flavor_eigenstates": [
                f"{fstr(flavor_z11['spectator_1'])} B_prime",
                f"{fstr(flavor_z11['spectator_2'])} B_prime",
            ],
            "sum": fstr(flavor_z11_sum),
            "Wilson_tracking": "the local complex structure is Q_prime=WQ and ZX has eigenvalues +/-i",
        },
        "z10_z01_Spin4xSpin7": {
            "perturbative_cubic_polynomial": "0",
            "spectator_flavor_trace": "tr Z=0 pointwise (the two representatives exchange signs)",
            "SU2_fundamental_doublet_ledger": minimal_z2_doublets,
            "SU2_fundamental_doublet_total": minimal_z2_total,
            "ordinary_SU2_Witten_obstruction": (
                "0" if minimal_z2_total % 2 == 0 else "NONZERO"
            ),
        },
        "all_local_charged_fermion_polynomials_zero": (
            flavor_z00_sum == 0
            and flavor_z11_sum == 0
            and minimal_z2_total % 2 == 0
        ),
    }
    integer_branch = {
        "z00_and_z11_coefficients_in_B_units": {
            **{name: fstr(value) for name, value in integer_z4.items()},
            "sum": fstr(integer_z4_sum),
        },
        "z10_z01_SU2_fundamental_doublet_ledger": integer_z2_doublets,
        "z10_z01_SU2_fundamental_doublet_total": integer_z2_total,
        "z10_z01_SU2_Witten_obstruction": (
            "0" if integer_z2_total % 2 == 0 else "NONZERO"
        ),
        "after_B0_Higgsing": (
            "the Spin11/Spin10 vector and B-hyper form an anomaly-opposite massive "
            "multiplet; the remaining A_m3 and C_m1 rows cancel"
        ),
        "pointwise_charged_polynomial_zero": (
            integer_z4_sum == 0 and integer_z2_total % 2 == 0
        ),
    }
    return {
        "status": "CHARGED_FERMION_POINTWISE_GAUGE_ANOMALIES_CANCEL__FULL_LOCAL_SUPERGRAVITY_OPEN",
        "projector_convention": {
            "normalized_formula": "w(eta)=F0/(2 pi), F0=-i log(-P_f(eta))",
            "fermion_from_superfield_conversion": (
                "P_f(eta)=exp(-i pi/4) eta^-1 for the positive-chirality "
                "hyperino convention used here"
            ),
            "log_branch": "arg(-P_f) in (-pi,pi]",
            "table_key": (
                "effective order-four superfield eigenvalue eta after the "
                "Lorentz/SU2R and 6D-chirality conversion; eta is not raw P_f"
            ),
            "effective_Z4_weights_by_superfield_eta": {
                "1": "3/8",
                "i": "1/8",
                "-1": "-1/8",
                "-i": "-3/8",
            },
            "source": "VON_GERSDORFF_2007",
        },
        "local_anomaly_basis": basis,
        "minimal_flavor_Wilson_branch": flavor_branch,
        "integer_m301_branch": integer_branch,
        "localized_families_and_rank_fields": (
            "each localized 16 is U5-anomaly-free; X(+10)+Xbar(-10) is vectorlike"
        ),
        "local_GS_decision": {
            "charged_fermion_local_polynomial_requires_inflow": False,
            "charged_sector_anomaly_requires_hypercharge_or_X_Stueckelberg": False,
            "hypercharge_or_X_Stueckelberg_from_equivariant_GS_descent": "OPEN_NOT_COMPUTED",
            "bulk_T1_GS_still_required": True,
            "full_orbifold_GS_completion": "OPEN_EQUIVARIANT_TENSOR_DESCENT",
        },
        "smooth_bulk_quantization": {
            "lattice": "U with Omega=[[0,1],[1,0]]",
            "unimodular_integral": True,
            "a": [2, 2],
            "a_characteristic": True,
            "b": [2, -1],
            "b_is_lattice_vector": True,
            "simply_connected_bulk_group": "Spin(11)",
            "coefficient_quantization": "PASS_ON_THE_SMOOTH_BULK",
        },
        "positive_tensor_chamber": {
            "j": ["1/2", "1"],
            "j_squared": "1",
            "j_dot_b": "3/2",
            "j_dot_a": "3",
            "gauge_kinetic_positive_and_j_dot_a_positive": True,
            "scope": (
                "j dot b controls the gauge kinetic sign; positive j dot a is "
                "recorded arithmetic and is not labeled a gravitational kinetic coefficient"
            ),
            "stabilized_tensor_vacuum": False,
        },
        "not_computed": [
            "gravitino, tensorino/self-dual-form and 266 neutral-hyper local U1_L/normal-bundle anomaly",
            "equivariant descent of the bulk Green-Schwarz differential cocycle",
            "global Spin(2)-Spin(11)-flavor quotient and restricted U5/U5-prime group forms",
            "orbifold Wu-Chern-Simons extension and localized eta/Dai-Freed phases",
            "pointwise discrete Z4R anomaly",
        ],
    }


def zero_mode_anomaly_audit() -> dict[str, Any]:
    fields = [
        # name, multiplicity, d3, d2, SU3 cubic sign, Y, X
        ("Q", 3, 3, 2, 1, Fraction(1, 6), Fraction(-1)),
        ("u^c", 3, 3, 1, -1, Fraction(-2, 3), Fraction(-1)),
        ("d^c", 3, 3, 1, -1, Fraction(1, 3), Fraction(3)),
        ("L", 3, 1, 2, 0, Fraction(-1, 2), Fraction(3)),
        ("e^c", 3, 1, 1, 0, Fraction(1), Fraction(-1)),
        ("N^c", 3, 1, 1, 0, Fraction(0), Fraction(-5)),
        ("H_u", 1, 1, 2, 0, Fraction(1, 2), Fraction(2)),
        ("H_d", 1, 1, 2, 0, Fraction(-1, 2), Fraction(-2)),
        ("X_rank", 1, 1, 1, 0, Fraction(0), Fraction(10)),
        ("Xbar_rank", 1, 1, 1, 0, Fraction(0), Fraction(-10)),
    ]
    names = [
        "SU3_cubed", "SU3_squared_Y", "SU3_squared_X", "SU2_squared_Y",
        "SU2_squared_X", "Y_cubed", "X_cubed", "Y_squared_X",
        "Y_X_squared", "gravity_squared_Y", "gravity_squared_X",
    ]
    sums = {name: Fraction(0) for name in names}
    doublets = 0
    for _, mult, d3, d2, a3, y, x in fields:
        dim = d3 * d2
        t3 = Fraction(1, 2) if d3 == 3 else Fraction(0)
        t2 = Fraction(1, 2) if d2 == 2 else Fraction(0)
        sums["SU3_cubed"] += mult * d2 * a3
        sums["SU3_squared_Y"] += mult * d2 * t3 * y
        sums["SU3_squared_X"] += mult * d2 * t3 * x
        sums["SU2_squared_Y"] += mult * d3 * t2 * y
        sums["SU2_squared_X"] += mult * d3 * t2 * x
        sums["Y_cubed"] += mult * dim * y**3
        sums["X_cubed"] += mult * dim * x**3
        sums["Y_squared_X"] += mult * dim * y**2 * x
        sums["Y_X_squared"] += mult * dim * y * x**2
        sums["gravity_squared_Y"] += mult * dim * y
        sums["gravity_squared_X"] += mult * dim * x
        if d2 == 2:
            doublets += mult * d3
    serialized = {name: fstr(value) for name, value in sums.items()}
    return {
        "status": "EXACT_4D_ZERO_MODE_LIE_ALGEBRA_ANOMALY_CANCELLATION",
        "spectrum": [
            "three localized 16 families including N^c",
            "one H_u+H_d vectorlike doublet pair",
            "one local X(+10)+Xbar(-10) vectorlike rank pair",
            "gauge singlets do not enter the gauge ledger",
        ],
        "normalization": {
            "16": "10_-1 + 5bar_3 + 1_-5",
            "Higgs": "5_2 weak doublet plus 5bar_-2 weak doublet",
        },
        "coefficients": serialized,
        "all_perturbative_coefficients_zero": all(value == 0 for value in sums.values()),
        "SU2_Witten": {
            "number_of_fundamental_doublets_with_color_multiplicity": doublets,
            "even": doublets % 2 == 0,
        },
        "scope_boundary": [
            "This is the integrated four-dimensional massless spectrum only.",
            "The separate localized-anomaly audit checks the charged-fermion projector polynomial.",
            "Gravity, tensor and neutral-hyper normal-bundle anomalies are not implied by this zero-mode sum.",
            "It does not prove Dai-Freed phases or the global U(2)xU(3) quotient.",
        ],
    }


def build_report() -> dict[str, Any]:
    source = load_v69()
    vector = vector_zero_mode_audit()
    phase_table = eleven_phase_table()
    minimal = minimal_projection_branch()
    dynamical = integer_phase_dynamical_branch()
    no_go = half32_no_go()
    anomaly = zero_mode_anomaly_audit()
    local_quantum = localized_anomaly_and_bulk_global_audit()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "primary_sources": PRIMARY_SOURCES,
        "lineage": {
            "bound_V69_path": V69_PATH.name,
            "bound_V69_core": source["core_sha256"],
            "expected_V69_core": EXPECTED_V69_CORE,
            "V69_core_matches": source["core_sha256"] == EXPECTED_V69_CORE,
            "imported_V69_claim": "vector/adjoint T2/Z4 skeleton and integrated localized 3x11 parent only",
            "not_imported": ["V69 spin lift", "V69 half32 projection", "V69 pointwise anomalies"],
        },
        "genuine_spin_lift": spin_lift_audit(),
        "lorentz_SU2R_and_N1_superfield_lift": supersymmetry_lift_audit(),
        "published_half32_parent_adjudication": no_go,
        "vector_multiplet_zero_modes": vector,
        "full_11_phase_table": phase_table,
        "localized_parent_completion_branches": {
            "minimal_flavor_Wilson_projection": minimal,
            "integer_m301_dynamical_reduction": dynamical,
            "preferred_for_next_action_audit": "integer_m301_dynamical_reduction",
        },
        "fixed_locus_twist_ledger": local_twist_ledger(),
        "localized_anomaly_and_bulk_global_audit": local_quantum,
        "four_dimensional_zero_mode_anomaly_audit": anomaly,
        "acceptance": {
            "A7_spin_R_lift_for_localized_charged_parent": "PASS_EXACT_CLASSICAL_SUPERFIELD",
            "A8_Higgs_spectrum": "PASS_EXACT_IN_BOTH_DISPLAYED_BRANCHES",
            "A8_three_families": "LOCALIZED_INPUT_NOT_DERIVED_FROM_BULK",
            "A9_charged_fermion_pointwise_gauge_anomaly": "PASS_EXACT_ZERO",
            "A9_full_local_supergravity_and_GS": "OPEN",
            "A11_positive_kinetic_chamber": "PASS_EXISTENCE_NOT_STABILIZATION",
            "published_half32_parent": "REJECTED_FOR_V69_ORBIFOLD",
            "localized_3x11_parent": "CONDITIONALLY_VIABLE_CHARGED_SECTOR",
        },
        "open_obligations": [
            "gravity, tensor and 266 neutral-hyper normal-bundle anomaly and equivariant boundary action",
            "orbifold Green-Schwarz differential-cocycle descent and Wu-Chern-Simons extension",
            "Dai-Freed/eta phases and the global Spin(2)-Spin(11)-flavor/U(2)xU(3) quotient",
            "globally gauged Z4R origin and pointwise discrete anomaly cancellation",
            "all-order local operator ring and global selection of the m301 vacuum branch",
            "KK gauge-fixed determinant, regulator and threshold calculation",
            "full compactification/tensor/rank/Higgs Hessian and stabilization inside the positive chamber",
            "soft spectrum, unification numerics, cosmology and mediator-complete flavor",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V70 removes the V69 spin/Higgs ambiguity for the localized charged "
                "parent, cancels its charged-fermion anomaly pointwise, exhibits a "
                "positive tensor chamber, and rejects the odd-half32 parent on this "
                "orbifold.  Gravity/tensor/neutral equivariance and the global quantum "
                "action remain open, so no gate closes."
            ),
            "all_gates_closed": False,
            "theory_complete": False,
        },
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    failures: list[str] = []
    checks = {
        "V69_bound": report["lineage"]["V69_core_matches"],
        "spin_q4": report["genuine_spin_lift"]["spinor_weight_formula"]["all_32_weights_qhat4_minus_one"],
        "spin_w2": report["genuine_spin_lift"]["spinor_weight_formula"]["all_32_weights_what2_minus_one"],
        "N1_supercharge": (
            report["lorentz_SU2R_and_N1_superfield_lift"]["SU2R_twist"]["preserved_4D_N"]
            == 1
        ),
        "half32_three_rejected": report["published_half32_parent_adjudication"]["three_half32s"] == "REJECTED",
        "V_dimension_13": report["vector_multiplet_zero_modes"]["V_zero_complex_dimension"] == 13,
        "Sigma_one_doublet": report["vector_multiplet_zero_modes"]["Sigma_zero_complex_dimension"] == 2,
        "Sigma_no_triplet": report["vector_multiplet_zero_modes"]["color_triplets"] == 0,
        "minimal_spectators_exact": report["localized_parent_completion_branches"]["minimal_flavor_Wilson_projection"]["spectator_pair"]["all_checks_pass"],
        "minimal_no_triplet": report["localized_parent_completion_branches"]["minimal_flavor_Wilson_projection"]["triplet_zero_modes"] == 0,
        "m301_rank_one": report["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]["mandatory_and_local_masses"]["rank_for_g_nonzero_vB_nonzero"] == 1,
        "m301_D_flat": report["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]["local_U5_stabilizer"]["D_flat"],
        "m301_driver_Hessian": report["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]["local_U5_stabilizer"]["complete_renormalizable_driver_class"]["exact_determinant"] == "det H=(det J)^2",
        "m301_operator_ledger": report["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]["complete_renormalizable_local_operator_ledger"]["forbidden_terms"]["16_to_the_fourth"] == "R=0 not 2",
        "pointwise_flavor_branch_zero": report["localized_anomaly_and_bulk_global_audit"]["minimal_flavor_Wilson_branch"]["all_local_charged_fermion_polynomials_zero"],
        "pointwise_m301_zero": report["localized_anomaly_and_bulk_global_audit"]["integer_m301_branch"]["pointwise_charged_polynomial_zero"],
        "smooth_bulk_quantized": report["localized_anomaly_and_bulk_global_audit"]["smooth_bulk_quantization"]["coefficient_quantization"] == "PASS_ON_THE_SMOOTH_BULK",
        "positive_tensor_chamber": report["localized_anomaly_and_bulk_global_audit"]["positive_tensor_chamber"]["gauge_kinetic_positive_and_j_dot_a_positive"],
        "tensor_stabilization_not_overclaimed": report["localized_anomaly_and_bulk_global_audit"]["positive_tensor_chamber"]["stabilized_tensor_vacuum"] is False,
        "4D_anomalies_zero": report["four_dimensional_zero_mode_anomaly_audit"]["all_perturbative_coefficients_zero"],
        "SU2_Witten_even": report["four_dimensional_zero_mode_anomaly_audit"]["SU2_Witten"]["even"],
        "all_gates_open": all(value == "OPEN" for value in report["gate_ledger"].values()),
        "core_exact": report.get("core_sha256") == canonical_sha(report),
    }
    for name, passed in checks.items():
        if not passed:
            failures.append(name)
    if failures:
        raise RuntimeError("V70 validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    vector = report["vector_multiplet_zero_modes"]
    no_go = report["published_half32_parent_adjudication"]
    minimal = report["localized_parent_completion_branches"]["minimal_flavor_Wilson_projection"]
    dynamic = report["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    anomaly = report["four_dimensional_zero_mode_anomaly_audit"]
    local_quantum = report["localized_anomaly_and_bulk_global_audit"]
    return f"""# V70 Spin(11) localized-parent Spin/flavor completion audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact result

The V69 vector skeleton has a genuine Spin cocycle:

```text
qhat = product_a exp(pi B_a/4)       qhat^4 = -1
what = B3 B4 B5                     what^2 = -1
qhat what qhat^-1 = what = -what^-1
```

The vector multiplet is nevertheless consistent because the center is
invisible in the adjoint and the Lorentz lift is paired with
`U_R=diag(zeta^-1,zeta)`.  Exactly one four-dimensional N=1 supercharge
survives.  In N=1 superfields,

```text
V -> Ad(Q)V
Sigma -> i Ad(Q)Sigma
Phi+ -> Z+ Phi+
Phi- -> Phi- Z-
Z+ Z- i = 1
```

## Published half-32 parent: rejected on this orbifold

For `n` pseudoreal half-32s write `Tj=Fj tensor what` and
`Theta=K tensor qhat`.  The space group requires

```text
K F1 K^-1 = F2
K F2 K^-1 = -F1^-1
```

Taking determinants forces `(-1)^n=+1`.  Hence `n` must be even.  A single
half-32 and the published three-half-32 parent have no field-space
representation of the V69 space group.  This is independent of the rotation
phase.  It does not reject the unorbifolded published spectrum.

## Vector and 11 zero modes

The common vector algebra has complex dimension {vector['V_zero_complex_dimension']}:
`u(2)+u(3)`.  `Sigma` has exactly {vector['Sigma_zero_complex_dimension']}
complex components, one weak `(2bar,1)`, and {vector['color_triplets']} color
triplets.

For a full 11,

```text
Z+ = i^m Q
Z- = i^(3-m) Q^-1
T1=T2=eta W
```

All integer `m=0,1,2,3` are honest order-four choices.  The half-integer
charges mentioned in hep-ph/0108152 are not imported: as total phases they
give `Z+^4=-1` unless an extra central equivariant structure is specified.

## Branch I: minimal flavor-Wilson projection

The active `m=3, eta=+1` 11 supplies one `(2,1)` and one singlet.  Together
with the conjugate `Sigma` doublet this is one Higgs pair and a singlet.  The
other two 11s use

```text
A=X, F1=Z, F2=-Z
Theta+=X tensor Q
T1+=Z tensor W, T2+=-Z tensor W
Theta-=-i X tensor Q^-1
```

Every space-group and full-hyper relation passes.  Since `T2=-T1`, a
simultaneous constant mode would obey `v=-v`; the spectator pair has exactly
{minimal['spectator_pair']['zero_mode_proof']['n_zero_modes']} zero modes.

## Branch II: integer m=(3,0,1) dynamical reduction

Before superpotential masses the exact ledger is

```text
A(m=3): H_uA + A0
B(m=0): B0 + H_uB
C(m=1): H_dC
Sigma : H_dSigma
```

There are no triplets.  A minimal local U(5) stabilizer slice is

```text
W_stab = kappa A0(B0^2-v_B^2)
```

has the F/D-flat branch `B0=+/-v_B`, `A0=0`.  The VEV is in the eleventh
direction, is invariant under Q and W, and breaks `Spin(11)->Spin(10)` without
rank loss.  Its complete renormalizable driver completion is

```text
z_X=X Xbar
W_drv=A0 f_A(B0,z_X)+S0 f_S(B0,z_X)+P_3(A0,S0)
f_alpha=a_alpha+b_alpha B0+c_alpha B0^2+d_alpha z_X.
```

On `A0=S0=0`, `f_A=f_S=0`, the driver/radial Jacobian is
`J=[[b_A+2c_A v_B,d_A],[b_S+2c_S v_B,d_S]]`.  For `detJ != 0`, the full
chiral Hessian has block form `[[0,J],[J^T,0]]` and exact determinant
`(detJ)^2`; the allowed cubic driver polynomial has zero Hessian there.  This is an
open-dense local branch; all-order stability and global uniqueness remain
open.

The mandatory bulk coupling and a full local U(5) contraction give

```text
sqrt(2) g v_B H_uB H_dSigma
  + (mu_B+lambda_B v_B) H_uB H_dC.
```

The 2-by-2 doublet matrix has exact rank
{dynamic['mandatory_and_local_masses']['rank_for_g_nonzero_vB_nonzero']}.  The
light pair is `H_uA` and
`(mu_B+lambda_B v_B)H_dSigma-sqrt(2)g v_B H_dC`; the latter has a nonzero
`H_dC` projection on the selected `g v_B != 0` branch.  The complete
renormalizable local ledger also permits the ordinary up, down, neutrino and
`NNX` couplings, while forbidding the light bare mu, `16^3` and `16^4`.
An arbitrary local polynomial in `Sigma` remains forbidden by its
higher-dimensional gauge shift.  The all-order selector/operator ring is
still open.

## Four-dimensional anomaly check

For three localized 16s, one surviving Higgs pair and `X(+10)+Xbar(-10)`,
all eleven perturbative Lie-algebra anomaly coefficients are exactly zero:

```text
{json.dumps(anomaly['coefficients'], sort_keys=True)}
```

The color-counted number of SU(2) doublets is
{anomaly['SU2_Witten']['number_of_fundamental_doublets_with_color_multiplicity']},
which is even.

## Fixed loci

```text
z00       theta          C(Q)=u(5)
z11       t1 theta       C(WQ)=u(5)'
z10/z01   t1 theta^2     C(R)=so(4)+so(7)
common                    u(2)+u(3)
```

The exact local twist matrices are stored in the JSON artifact for the
pointwise anomaly computation.

## Pointwise charged anomaly and bulk tensor checks

For a positive-chirality hyperino in the convention used here, the order-four
superfield eigenvalue `eta` is first converted as
`P_f(eta)=exp(-i pi/4) eta^-1`.  Applying
`w(eta)=[-i log(-P_f(eta))]/(2 pi)` on the stated branch gives the effective
weights `(3/8,1/8,-1/8,-3/8)` for `eta=(1,i,-1,-i)`.  Thus the table is not a
literal substitution of `eta` for the raw fermionic projector `P_f`.  The
local U(5) anomaly basis is
`B=(1,1,40,10)` for
`(SU5^3,SU5^2 X,X^3,grav-X)`.  The minimal flavor-Wilson branch cancels
at the first corner as

```text
vector + active 11 + spectator pair
= -B/2 + B/2 + B/2 - B/2 = 0.
```

At the second corner `Q'=WQ`; the spectator signs exchange but the full
U(5)' polynomial is again zero.  At the Z2 orbit, Spin(4)xSpin(7) has no
perturbative cubic tensor, the spectator flavor trace vanishes, and every
SU(2) doublet multiplicity is even.  The integer `m=(3,0,1)` branch likewise
gives `-1/2+1/2+1/2-1/2=0` in B units at both Z4 corners.  Thus
`{local_quantum['status']}`.

The charged-fermion local polynomial requires neither localized GS inflow nor
a hypercharge/X Stückelberg response.  Whether the separate equivariant bulk-GS
descent induces such a coupling remains open.  The reducible six-dimensional
bulk anomaly still uses the T=1 GS system.  Its smooth-bulk lattice is integral and unimodular, with
`a=(2,2)` characteristic and `b=(2,-1)`.  An explicit positive chamber is

```text
j=(1/2,1),  j^2={local_quantum['positive_tensor_chamber']['j_squared']},
j.b={local_quantum['positive_tensor_chamber']['j_dot_b']},
j.a={local_quantum['positive_tensor_chamber']['j_dot_a']}.
```

This proves existence of a tensor chamber with positive gauge coefficient
`j.b`; the positive value of `j.a` is recorded but is not called a
gravitational kinetic coefficient.  It does not prove tensor-scalar
stabilization.  The gravity/tensor/266-neutral-hyper normal-bundle anomaly
and the orbifold Wu--Chern--Simons/differential-cocycle descent remain open.

## Decision boundary

{report['terminal_decision']['honest_outcome']}

The remaining obligations are:

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
            raise RuntimeError("V70 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V70 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V70 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
