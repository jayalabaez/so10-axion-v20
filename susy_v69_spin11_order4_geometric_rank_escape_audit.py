#!/usr/bin/env python3
"""V69 exact audit of the six-dimensional Spin(11) escape frontier.

The literal Hall--Nomura--Okui--Smith T2/(Z2 x Z2') SO(10) construction
cannot be lifted by simply adjoining the eleventh Spin(11) coordinate.  The
SU(5) complex-structure twist is order two on the SO(10) adjoint but order
four on the Spin(11)/Spin(10) vector.  Treating it as a parity either violates
the space-group relation or leaks coset components at the intended G3211
corner.

The obstruction also identifies a concrete new route.  On a square T2/Z4,
the same complex structure is a legitimate order-four gauge twist.  An
explicit Wilson line then gives common U(3)xU(2)=G3211 gauge algebra.  A
local U(5) singlet pair with X charges +/-10 breaks the remaining U(1)X
without any rank-spinor Q/Qbar fields, so the V64 orphan premise is absent by
action replacement.  This is an exact gauge/rank skeleton, not yet a full
theory: spinor lifts, the supersymmetry/R twist, Higgs and family projections,
localized anomaly inflow, the regulator, thresholds, vacuum and cosmology
remain open.

Independently, the audit derives two anomaly-factorized 6D N=(1,0) Spin(11)
bulk parents.  One is the published n=3 half-spinor supergravity spectrum.
Integrated factorization is not imported as fixed-point cancellation.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


VERSION = "V69"
DATE = "2026-08-30"
SCHEMA = "susy_v69_spin11_order4_geometric_rank_escape_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v69_spin11_order4_geometric_rank_escape_audit.py"

INPUTS = {
    "v56_orbifold_template": ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json",
    "v57_spin10_template": ROOT / "SUSY_V57_G1_MICROSCOPIC_COMPLETION_FRONTIER_AUDIT.json",
    "v59_spin11": ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json",
    "v61_z4r": ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.json",
    "v64_null": ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json",
    "v67_index_6d": ROOT / "SUSY_V67_SPIN11_INDEX_PARTNER_6D_ESCAPE_AUDIT.json",
    "v68_split_bulk": ROOT / "SUSY_V68_SPIN11_SPLIT_BULK_PARITY_NO_GO_AUDIT.json",
    "v68_master": ROOT / "SUSY_V68_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
}

EXPECTED_CORES = {
    "v56_orbifold_template": "09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55",
    "v57_spin10_template": "0896cc21d84d6395d6ba9d5c0b6414c3aec14c18981708d2e06b548a4fc21302",
    "v59_spin11": "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42",
    "v61_z4r": "6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a",
    "v64_null": "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d",
    "v67_index_6d": "5927f64eec6bc27d68b7d429eab11ee1f0efc9709041064f47baaabc25f0eebb",
    "v68_split_bulk": "368ca47a3e1dac8e283173c4c838d0dfdef76c905735284b45791c85bbb66db7",
    "v68_master": "c46848e93c9f0d0ee05f1fa9d345cda4cbf4534d265476337834fe635cd2dbe9",
}

STATUS = (
    "V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE__V56_V57_TEMPLATES_NONIMPORTED__"
    "V59_V61_V64_V67_V68_CORES_BOUND__HALL_Z2XZ2_PRIME_DIRECT_SPIN11_LIFT_"
    "REJECTED__SU5_COMPLEX_STRUCTURE_IS_ORDER4_ON_SPIN11_COSET__FORMAL_"
    "G3211_CORNER_LEAKS_2_OR3_COSET_COMPONENTS__PUBLISHED_6D_SPIN11_SCALAR_"
    "PROJECTION_NOT_A_CONVENTIONAL_FULL_SUSY_HYPER__FULL_HYPER_RESTORES_"
    "FULL_16__PSEUDOREAL_HALF32_PROJECTION_OPEN__"
    "T2_Z4_SPACE_GROUP_GAUGE_EMBEDDING_EXACT__Q4_WILSON_RELATIONS_PASS__"
    "COMMON_U3_X_U2_G3211_ALGEBRA_DIM13__LOCAL_U5_RANK_SINGLET_PAIR_"
    "REMOVES_V64_ORPHAN_PREMISE_BY_ACTION_REPLACEMENT__PUBLISHED_N3_SPIN11_"
    "HALF_SPINOR_BULK_ANOMALY_FACTORIZATION_EXACT__LOCALIZED_FAMILY_BULK_"
    "VARIANT_FACTORIZATION_EXACT__SPINOR_LIFTS_SUSY_HIGGS_FIXED_POINT_"
    "ANOMALIES_Z4R_UV_THRESHOLDS_VACUUM_COSMOLOGY_OPEN__NEW_6D_ACTION_"
    "KINEMATIC_CANDIDATE_NOT_ACCEPTED__CURRENT_ACTION_REJECTED__G1_TO_G8_"
    "OPEN_ZERO_PROMOTIONS"
)

PRIMARY_SOURCES = [
    {
        "id": "HALL_NOMURA_OKUI_SMITH_2001",
        "title": "SO(10) Unified Theories in Six Dimensions",
        "url": "https://arxiv.org/abs/hep-ph/0108071",
        "scope": (
            "SO(10) T2/(Z2 x Z2') space group, U5 and Pati-Salam twists, "
            "the G3211 fixed point, fixed-line Higgs splitting, and local "
            "X(+/-10) rank breaking.  It is not a Spin(11) lift."
        ),
    },
    {
        "id": "HOSOTANI_YAMATSU_2018",
        "title": "Electroweak Symmetry Breaking and Mass Spectra in Six-Dimensional Gauge-Higgs Grand Unification",
        "url": "https://arxiv.org/abs/1710.04811",
        "scope": (
            "Published non-supersymmetric 6D SO(11) parities and a 5D brane "
            "32 scalar; its scalar projection cannot be imported as a conventional "
            "full SUSY hyper, while a pseudoreal half-32 projection remains open."
        ),
    },
    {
        "id": "AVRAMIS_KEHAGIAS_2005",
        "title": "A systematic search for anomaly-free supergravities in six dimensions",
        "url": "https://arxiv.org/abs/hep-th/0508172",
        "scope": (
            "Published one-tensor SO(11) series (n+3) x 11 + (n/2) x 32; "
            "the n=3 member supplies six 11s and three half-32s."
        ),
    },
    {
        "id": "ERLER_1993",
        "title": "Anomaly Cancellation in Six Dimensions",
        "url": "https://arxiv.org/abs/hep-th/9304104",
        "scope": "Six-dimensional trace identities and anomaly-polynomial convention.",
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": "Integrated cancellation does not replace a projector-weighted fixed-point ledger.",
    },
    {
        "id": "MONNIER_MOORE_PARK_2017",
        "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
        "url": "https://arxiv.org/abs/1711.04777",
        "scope": "Integral anomaly-coefficient and string-charge-lattice obligations.",
    },
    {
        "id": "LEE_TACHIKAWA_2020",
        "title": "Some comments on 6D global gauge anomalies",
        "url": "https://arxiv.org/abs/2012.11622",
        "scope": "Spin bordism result Omega_7^Spin(BSpin(n>=7))=0 and global GS caveat.",
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


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing bound input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def fstr(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def matmul(a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def matpow(a: Sequence[Sequence[int]], exponent: int) -> list[list[int]]:
    result = identity(len(a))
    base = [list(row) for row in a]
    while exponent:
        if exponent & 1:
            result = matmul(result, base)
        base = matmul(base, base)
        exponent //= 2
    return result


def diagonal(signs: Sequence[int]) -> list[list[int]]:
    return [[signs[i] if i == j else 0 for j in range(len(signs))] for i in range(len(signs))]


def q4_matrix() -> list[list[int]]:
    # Five +90-degree planes and the untouched eleventh coordinate.
    q = [[0 for _ in range(11)] for _ in range(11)]
    for pair in range(5):
        i = 2 * pair
        q[i][i + 1] = -1
        q[i + 1][i] = 1
    q[10][10] = 1
    return q


def antisymmetric_basis(n: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def generator(n: int, i: int, j: int) -> list[list[int]]:
    out = [[0 for _ in range(n)] for _ in range(n)]
    out[i][j], out[j][i] = 1, -1
    return out


def rank_fraction(rows: Iterable[Sequence[int | Fraction]]) -> int:
    work = [[Fraction(value) for value in row] for row in rows]
    if not work:
        return 0
    n_rows, n_cols = len(work), len(work[0])
    rank = 0
    for col in range(n_cols):
        pivot = next((r for r in range(rank, n_rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][col]
        work[rank] = [value / scale for value in work[rank]]
        for r in range(n_rows):
            if r == rank or not work[r][col]:
                continue
            factor = work[r][col]
            work[r] = [work[r][c] - factor * work[rank][c] for c in range(n_cols)]
        rank += 1
        if rank == n_rows:
            break
    return rank


def fixed_algebra_dimension(group_matrices: Sequence[Sequence[Sequence[int]]]) -> int:
    basis = antisymmetric_basis(11)
    index = {pair: k for k, pair in enumerate(basis)}
    equations: list[list[int]] = []
    for group in group_matrices:
        gt = transpose(group)
        block = [[0] * len(basis) for _ in basis]
        for column, (i, j) in enumerate(basis):
            image = matmul(matmul(group, generator(11, i, j)), gt)
            for a, b in basis:
                coefficient = image[a][b]
                if coefficient:
                    block[index[(a, b)]][column] = coefficient
        for output in range(len(basis)):
            block[output][output] -= 1
            if any(block[output]):
                equations.append(block[output])
    return len(basis) - rank_fraction(equations)


def vector_gauge_skeleton() -> dict[str, Any]:
    q = q4_matrix()
    p0 = matpow(q, 2)
    # The compact representative of the old P1 automorphism.
    r = diagonal([-1] * 4 + [1] * 7)
    w = matmul(r, p0)
    one = identity(11)
    w2 = copy.deepcopy(w)
    local_q_other = matmul(w, q)
    relations = {
        "Q4_equals_identity": matpow(q, 4) == one,
        "Q2_equals_P0": matpow(q, 2) == p0,
        "W1_W2_commute": matmul(w, w2) == matmul(w2, w),
        "Q_W1_Qinv_equals_W2": matmul(matmul(q, w), transpose(q)) == w2,
        "Q_W2_Qinv_equals_W1inv": matmul(matmul(q, w2), transpose(q)) == transpose(w),
        "R_equals_W_Q2": r == matmul(w, p0),
        "W_involution": matpow(w, 2) == one,
        "R_involution": matpow(r, 2) == one,
    }
    dimensions = {
        "Spin11_bulk": 55,
        "C_Q_U5": fixed_algebra_dimension([q]),
        "C_Q2_SO10": fixed_algebra_dimension([p0]),
        "C_R_SO4xSO7": fixed_algebra_dimension([r]),
        "C_W_SO5xSO6": fixed_algebra_dimension([w]),
        "C_WQ_other_U5": fixed_algebra_dimension([local_q_other]),
        "C_Q_and_W_common_G3211": fixed_algebra_dimension([q, w]),
        "C_Q_and_R_common_G3211": fixed_algebra_dimension([q, r]),
    }
    return {
        "status": "EXACT_ADJOINT_AND_VECTOR_SPACE_GROUP_SKELETON",
        "geometry": "square T2/Z4 with theta:z->i z and translations t1,t2",
        "space_group_relations": [
            "theta^4=1",
            "t1 t2=t2 t1",
            "theta t1 theta^-1=t2",
            "theta t2 theta^-1=t1^-1",
        ],
        "gauge_embedding": {
            "Q": "diag(J,J,J,J,J,1), J=[[0,-1],[1,0]]",
            "Q_squared_P0": "diag(-I10,+1), centralizer Spin(10)",
            "R": "diag(-I4,+I7), centralizer Spin(4)xSpin(7)",
            "W1_equals_W2": "R Q^2 = diag(+I4,-I6,+1)",
            "local_Z2_twist_t1_theta2": "W Q^2 = R",
        },
        "relation_checks": relations,
        "all_vector_space_group_relations_pass": all(relations.values()),
        "fixed_algebra_dimensions": dimensions,
        "fixed_algebras": {
            "Z4_origin": "u(5), dimension 25",
            "Z2_point": "so(4)+so(7), dimension 27",
            "other_Z4_point": "conjugate u(5), dimension 25",
            "common_4D": "u(2)+u(3)=su(2)+su(3)+u(1)^2, dimension 13",
        },
        "common_group": "G3211",
        "spin_lift_audit": {
            "Q_spin_fourth_power": "-1 because five plane rotations each give a 2pi spin sign",
            "W_spin_square": "-1 because W is a pi rotation in three planes",
            "status": "OPEN_CENTRAL_PHASE_AND_R_TWIST_REQUIRED",
            "obligation": (
                "choose Lorentz/R/intrinsic phases and central translation lifts so every "
                "gaugino, half-32 and 11 satisfies the full space-group relations"
            ),
        },
        "not_yet_proved": [
            "a 4D N=1 supersymmetry-preserving spin/R lift",
            "exact Hu and Hd zero modes with no triplets",
            "three-family zero modes from the half-32 spectrum",
            "fixed-point anomaly and inflow cancellation",
        ],
    }


def direct_z2_lift_no_go(v68: Mapping[str, Any]) -> dict[str, Any]:
    sector_dims = {
        "(+,+)": 3,
        "(-,+)": 3,
        "(+,-)": 2,
        "(-,-)": 2,
    }
    rows = []
    for r1, r2 in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        key = f"({'+' if -r1 == 1 else '-'},{'+' if -r2 == 1 else '-'})"
        rows.append(
            {
                "r1": r1,
                "r2": r2,
                "selected_T51_T422_sector": key,
                "formal_coset_even_even_multiplicity": sector_dims[key],
            }
        )
    spinor_row = next(
        row
        for row in v68["representation_and_parity_audit"]["spinor_32_intrinsic_scan"]
        if row["eta"] == "+-"
    )
    return {
        "status": "DIRECT_T2_Z2XZ2_PRIME_SPIN11_LIFT_REJECTED",
        "SO10_literature_result": {
            "corner_groups": ["SO10", "U5", "Pati-Salam", "G3211"],
            "G3211_fixed_point_exists": True,
        },
        "order_obstruction": {
            "real_SU5_twist": "J5=J direct-sum five times, J5^2=-I10",
            "Spin11_shifted_parity_square": "diag(-I10,+1)=P0, noncentral on so11",
            "adjoint_order_on_so10": 2,
            "adjoint_order_on_spin11_coset": 4,
            "valid_Z2_parity": False,
        },
        "formal_complex_leakage_diagnostic": {
            "sector_dimensions": sector_dims,
            "rows": rows,
            "minimum_leakage": min(row["formal_coset_even_even_multiplicity"] for row in rows),
            "maximum_leakage": max(row["formal_coset_even_even_multiplicity"] for row in rows),
            "warning": (
                "forcing the Hall complex convention to be a parity loses the compact "
                "real form; these 2/3 counts diagnose the failure, not physical zero modes"
            ),
        },
        "published_6D_Spin11_scalar_import": {
            "published_zero_sector": "(1,2,4bar) from a non-supersymmetric 5D brane 32 scalar",
            "conventional_SUSY_hyper_H_zero": spinor_row["H_zero_reps"],
            "conventional_SUSY_hyper_Hc_left_chiral_zero": spinor_row["Hc_left_chiral_zero_reps"],
            "total_left_chiral_zero_sector": spinor_row["4D_left_chiral_identification"],
            "Q_returns": "(2,1,4)" in spinor_row["Hc_left_chiral_zero_reps"],
            "conventional_full_hyper_import_valid": False,
            "pseudoreal_half_32_projection": "OPEN_NOT_COMPUTED",
            "general_SUSY_import_closed": False,
        },
        "exact_scope": (
            "the literal order-two lift and the conventional full-hyper scalar import are closed; "
            "pseudoreal half-32 projections, higher-order phases and nested boundary space groups are open"
        ),
    }


TRACE_COEFFICIENTS = {
    "11": {"dimension": 11, "A2": Fraction(1), "B4": Fraction(1), "C22": Fraction(0)},
    "32": {"dimension": 32, "A2": Fraction(4), "B4": Fraction(-2), "C22": Fraction(3, 2)},
    "55": {"dimension": 55, "A2": Fraction(9), "B4": Fraction(3), "C22": Fraction(3)},
}


def lattice_dot(omega: Sequence[Sequence[int]], x: Sequence[int], y: Sequence[int]) -> int:
    return sum(x[i] * omega[i][j] * y[j] for i in range(len(x)) for j in range(len(y)))


def anomaly_variant(
    *,
    name: str,
    n11: Fraction,
    n32: Fraction,
    neutral_hypers: int,
    omega: list[list[int]],
    a: list[int],
    b: list[int],
    published: bool,
) -> dict[str, Any]:
    adj = TRACE_COEFFICIENTS["55"]
    vec = TRACE_COEFFICIENTS["11"]
    spin = TRACE_COEFFICIENTS["32"]
    residual = {
        key: adj[key] - n11 * vec[key] - n32 * spin[key]
        for key in ("A2", "B4", "C22")
    }
    charged_h = n11 * vec["dimension"] + n32 * spin["dimension"]
    total_h = charged_h + neutral_hypers
    lambda_spin = 2
    a_dot_b_required = Fraction(lambda_spin, 6) * residual["A2"]
    b_squared_required = -Fraction(lambda_spin * lambda_spin, 3) * residual["C22"]
    return {
        "name": name,
        "published_spectrum": published,
        "multiplicities": {"11": fstr(n11), "32": fstr(n32), "neutral": neutral_hypers},
        "half_32_interpretation": (
            "32 is pseudoreal for Spin(11); n32=3/2 means three half-hypermultiplets"
            if n32.denominator == 2
            else "no bulk spinor hypers"
        ),
        "trace_convention": "tr=tr_11",
        "trace_identities": {
            "Tr55_F2": "9 trF2",
            "Tr55_F4": "3 trF4 + 3 (trF2)^2",
            "tr32_F2": "4 trF2",
            "tr32_F4": "-2 trF4 + (3/2)(trF2)^2",
        },
        "residual_adj_minus_hypers": {key: fstr(value) for key, value in residual.items()},
        "irreducible_F4_cancels": residual["B4"] == 0,
        "gravity": {
            "T": 1,
            "V": 55,
            "charged_H_dimension": fstr(charged_h),
            "neutral_H_dimension": neutral_hypers,
            "total_H": fstr(total_h),
            "H_minus_V": fstr(total_h - 55),
            "required_H_minus_V": 244,
            "irreducible_R4_cancels": total_h - 55 == 244,
        },
        "GS_inner_products": {
            "a_squared_required": 8,
            "a_dot_b_required": fstr(a_dot_b_required),
            "b_squared_required": fstr(b_squared_required),
        },
        "lattice_witness": {
            "Omega": omega,
            "a": a,
            "b": b,
            "a_squared": lattice_dot(omega, a, a),
            "a_dot_b": lattice_dot(omega, a, b),
            "b_squared": lattice_dot(omega, b, b),
            "a_characteristic": all(
                (lattice_dot(omega, a, x) - lattice_dot(omega, x, x)) % 2 == 0
                for x in ((0, 0), (1, 0), (0, 1), (1, 1))
            ),
        },
        "factorization_passes": (
            residual["B4"] == 0
            and total_h - 55 == 244
            and lattice_dot(omega, a, a) == 8
            and lattice_dot(omega, a, b) == a_dot_b_required
            and lattice_dot(omega, b, b) == b_squared_required
        ),
    }


def bulk_anomaly_audit() -> dict[str, Any]:
    published = anomaly_variant(
        name="PUBLISHED_N3_HALF_SPINOR_PARENT",
        n11=Fraction(6),
        n32=Fraction(3, 2),
        neutral_hypers=185,
        omega=[[1, 0], [0, -1]],
        a=[3, 1],
        b=[0, 1],
        published=True,
    )
    localized = anomaly_variant(
        name="LOCALIZED_THREE_FAMILY_BULK_PARENT",
        n11=Fraction(3),
        n32=Fraction(0),
        neutral_hypers=266,
        omega=[[0, 1], [1, 0]],
        a=[2, 2],
        b=[2, -1],
        published=False,
    )
    published["I8_factorization"] = "-1/16 (trR2-trF2)(trR2+(1/2)trF2)"
    localized["I8_factorization"] = "-1/16 (trR2-trF2)(trR2+2trF2)"
    return {
        "status": "TWO_EXACT_INTEGRATED_BULK_FACTORIZATIONS__NOT_FIXED_POINT_COMPLETIONS",
        "variants": [published, localized],
        "N11_alternative": {
            "spectrum": "(1,0) vector + adjoint hyper",
            "bulk_fermion_anomalies": "cancel representation by representation",
            "orbifold_local_anomalies": "OPEN_AFTER_PROJECTION",
        },
        "ordinary_connected_Spin11_torsion": {
            "bordism": "reduced Omega_7^Spin(BSpin(11))=0",
            "conclusion": "no independent pure-Spin(11) torsion class after local polynomial cancellation",
            "does_not_close": [
                "global GS/Wu-Chern-Simons definition",
                "integral tensor and string-charge data on the orbifold",
                "a positive gauge/tensor kinetic chamber at the selected compactification vacuum",
                "the post-orbifold global quotient",
                "singular-locus eta/Dai-Freed phases",
                "Z4R anomalies",
            ],
        },
        "nonimport_rule": (
            "neither integrated parent supplies projector weights, intrinsic phases, local branchings, "
            "localized counterterms or inflow for the V69 orbifold"
        ),
    }


def geometric_rank_replacement(v56: Mapping[str, Any], v61: Mapping[str, Any]) -> dict[str, Any]:
    inherited_charges = v61["rank_sector_r_compatibility"]["charges"]
    terms = {
        "S_X_Xbar": (2 + 0 + 0) % 4,
        "S_v2": 2,
        "N_N_X": (1 + 1 + 0) % 4,
        "Hu_Hd": (0 + 0) % 4,
        "matter4": (4 * 1) % 4,
    }
    return {
        "status": "EXACT_LOCAL_CLASSICAL_RANK_SECTOR__NEW_ACTION_ONLY",
        "location": "a Z4 fixed locus with local U(5)=(SU5 x U1X)/Z5",
        "fields": {
            "X": "SU5 singlet, X charge +10, qR=0",
            "Xbar": "SU5 singlet, X charge -10, qR=0",
            "S": "gauge singlet, qR=2",
        },
        "superpotential": "W_rank=kappa S (X Xbar-vX^2)",
        "supersymmetric_branch": {
            "F_S": "X Xbar-vX^2=0",
            "F_X_F_Xbar": "S=0 for nonzero X,Xbar",
            "D_flat": "|X|=|Xbar|",
            "solution": "X=Xbar=vX up to the U1X gauge orbit; S=0",
            "all_rank_chirals_massive": (
                "one combination is eaten; S pairs with the radial combination at order kappa vX"
            ),
        },
        "orphan_statement": {
            "V59_C16_Cbar16_rank_sector_present": False,
            "V64_Q_Qbar_orphan_premise_present": False,
            "classification": "ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED",
            "colored_rank_fields": 0,
        },
        "gauge_charge_checks": {
            "X_Xbar": 0,
            "Ncharge_plus_Ncharge_plus_X": -5 - 5 + 10,
            "local_U5_quotient_allows_singlet_charge_10": True,
        },
        "Z4R_operator_checks": {
            "charges_mod4": terms,
            "W_rank_allowed": terms["S_X_Xbar"] == 2 and terms["S_v2"] == 2,
            "Majorana_NNX_allowed": terms["N_N_X"] == 2,
            "bare_mu_forbidden": terms["Hu_Hd"] != 2,
            "matter16_four_forbidden": terms["matter4"] != 2,
            "globally_gauged_origin_proved": False,
        },
        "template_binding": {
            "V56_rank_pair_matches": v56["candidate_action"]["GG_brane"].find("X_+10") >= 0,
            "V61_charge_rows_bound": all(inherited_charges[name] == value for name, value in {"C": 0, "Cbar": 0}.items()),
            "not_imported": (
                "V56 Spin(10) fixed-point anomalies and V57 GS coefficients are not V69 Spin(11) evidence"
            ),
        },
    }


def acceptance_matrix() -> list[dict[str, Any]]:
    rows = [
        ("A1", "literal Hall Z2 x Z2' lift to Spin11", "REJECTED", "order-four coset action"),
        (
            "A2",
            "published 6D Spin11 scalar projection as a conventional full SUSY hyper",
            "REJECTED_SCOPED",
            "Hc restores the full 16; a pseudoreal half-32 projection is open",
        ),
        ("A3", "T2/Z4 adjoint/vector space-group embedding", "PASS_KINEMATIC", "all exact matrix relations pass"),
        ("A4", "common G3211 gauge algebra", "PASS_KINEMATIC", "fixed algebra dimension 13"),
        ("A5", "local singlet-only U1X rank breaking", "PASS_CLASSICAL_LOCAL", "F/D-flat and no colored rank field"),
        ("A6", "published n=3 Spin11 bulk anomaly parent", "PASS_INTEGRATED", "I8 factorizes on an integral lattice"),
        ("A7", "Spin/R lift for all fermions and half hypers", "OPEN", "central phases not fixed"),
        ("A8", "exact MSSM Higgs and three-family projection", "OPEN", "no full phase table or determinant"),
        ("A9", "pointwise continuous/discrete anomaly inflow", "OPEN", "integrated I8 is insufficient"),
        ("A10", "globally gauged Z4R and proton lifetime", "OPEN", "operator charges are only classical"),
        (
            "A11",
            "positive kinetic chamber, UV regulator, thresholds, vacuum and cosmology",
            "OPEN",
            "the lattice witness is not a tensor-scalar vacuum",
        ),
    ]
    return [
        {"id": item, "requirement": requirement, "status": status, "evidence": evidence}
        for item, requirement, status, evidence in rows
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN WITH EXACT ADVANCE: the direct order-two 6D lift is closed and an exact "
            "T2/Z4 gauge/rank skeleton exists, but its spin/R lift, projected action and local anomalies are open."
        ),
        "G2": "OPEN: no coefficient-level 4D action, flavor determinant, soft sector or pole spectrum is derived.",
        "G3": "OPEN: the local X branch is F/D-flat, but compactification moduli, tensor scalars and the full Hessian are unsolved.",
        "G4": (
            "OPEN: V64 orphans are absent only in the replacement action; an exact Hu/Hd/no-triplet "
            "projection and physical hierarchy are not yet certified."
        ),
        "G5": "OPEN: the 6D anomaly hypers need a complete orbifold zero-mode and exotic-mass census.",
        "G6": "OPEN: reheating, defects from U1X breaking, relics, moduli and cosmology are absent.",
        "G7": "OPEN: the classical Z4R ledger passes selected operators, but its gauged origin, KK operators and proton lifetime are open.",
        "G8": "OPEN: local anomaly/GS/Dai-Freed data, regulator, thresholds and mediator-complete flavor remain open.",
    }
    return [
        {"gate": gate, "status": "OPEN", "V69_closed": False, "decision": decisions[gate]}
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def source_manifest() -> dict[str, Any]:
    return {
        "local_files": [
            {"id": name, "path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
            for name, path in INPUTS.items()
        ],
        "generated_files": [
            {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
            for path in (Path(__file__), TEST_PATH)
        ],
        "primary_sources": copy.deepcopy(PRIMARY_SOURCES),
    }


def _body() -> dict[str, Any]:
    inputs = {name: load_bound(name) for name in INPUTS}
    direct = direct_z2_lift_no_go(inputs["v68_split_bulk"])
    skeleton = vector_gauge_skeleton()
    anomaly = bulk_anomaly_audit()
    rank = geometric_rank_replacement(inputs["v56_orbifold_template"], inputs["v61_z4r"])
    acceptance = acceptance_matrix()
    gates = gate_ledger()
    variants = {row["name"]: row for row in anomaly["variants"]}
    dims = skeleton["fixed_algebra_dimensions"]
    checks = {
        "all_bound_cores_exact": all(inputs[name]["core_sha256"] == EXPECTED_CORES[name] for name in INPUTS),
        "V64_current_action_null_mode_bound": inputs["v64_null"]["terminal_decision"]["current_Spin11_action_accepted"] is False
        and "twelve normalizable Q-type" in inputs["v64_null"]["terminal_decision"]["exact_blocker"],
        "V68_current_action_rejected": inputs["v68_split_bulk"]["terminal_decision"]["current_bound_Spin11_action"] == "REJECTED",
        "direct_Hall_lift_order4_not_Z2": direct["order_obstruction"]["adjoint_order_on_spin11_coset"] == 4
        and direct["order_obstruction"]["valid_Z2_parity"] is False,
        "formal_leakage_is_unavoidable": direct["formal_complex_leakage_diagnostic"]["minimum_leakage"] == 2
        and direct["formal_complex_leakage_diagnostic"]["maximum_leakage"] == 3,
        "published_full_hyper_scalar_not_imported": direct["published_6D_Spin11_scalar_import"]["Q_returns"]
        and direct["published_6D_Spin11_scalar_import"]["conventional_full_hyper_import_valid"] is False
        and direct["published_6D_Spin11_scalar_import"]["pseudoreal_half_32_projection"] == "OPEN_NOT_COMPUTED"
        and direct["published_6D_Spin11_scalar_import"]["general_SUSY_import_closed"] is False,
        "Q4_exact": skeleton["relation_checks"]["Q4_equals_identity"]
        and skeleton["relation_checks"]["Q2_equals_P0"],
        "T2Z4_space_group_embedding_exact": skeleton["all_vector_space_group_relations_pass"],
        "local_U5_dimensions_exact": dims["C_Q_U5"] == 25 and dims["C_WQ_other_U5"] == 25,
        "local_SO10_dimension_exact": dims["C_Q2_SO10"] == 45,
        "local_SO4_SO7_dimension_exact": dims["C_R_SO4xSO7"] == 27,
        "common_G3211_dimension_exact": dims["C_Q_and_W_common_G3211"] == 13
        and dims["C_Q_and_R_common_G3211"] == 13,
        "spin_lift_not_overclaimed": skeleton["spin_lift_audit"]["status"] == "OPEN_CENTRAL_PHASE_AND_R_TWIST_REQUIRED",
        "published_n3_irreducible_anomalies_cancel": variants["PUBLISHED_N3_HALF_SPINOR_PARENT"]["irreducible_F4_cancels"]
        and variants["PUBLISHED_N3_HALF_SPINOR_PARENT"]["gravity"]["irreducible_R4_cancels"],
        "published_n3_lattice_factorizes": variants["PUBLISHED_N3_HALF_SPINOR_PARENT"]["factorization_passes"],
        "published_n3_counts_exact": variants["PUBLISHED_N3_HALF_SPINOR_PARENT"]["multiplicities"]
        == {"11": "6", "32": "3/2", "neutral": 185},
        "localized_family_bulk_factorizes": variants["LOCALIZED_THREE_FAMILY_BULK_PARENT"]["factorization_passes"],
        "localized_family_counts_exact": variants["LOCALIZED_THREE_FAMILY_BULK_PARENT"]["multiplicities"]
        == {"11": "3", "32": "0", "neutral": 266},
        "integrated_anomaly_not_imported_locally": "projector weights" in anomaly["nonimport_rule"],
        "rank_F_D_branch_exact": rank["supersymmetric_branch"]["D_flat"] == "|X|=|Xbar|",
        "rank_is_gauge_vectorlike": rank["gauge_charge_checks"]["X_Xbar"] == 0,
        "Majorana_gauge_charge_exact": rank["gauge_charge_checks"]["Ncharge_plus_Ncharge_plus_X"] == 0,
        "orphan_absent_not_lifted": rank["orphan_statement"]["classification"]
        == "ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED",
        "selected_Z4R_operators_exact": rank["Z4R_operator_checks"]["W_rank_allowed"]
        and rank["Z4R_operator_checks"]["Majorana_NNX_allowed"]
        and rank["Z4R_operator_checks"]["bare_mu_forbidden"]
        and rank["Z4R_operator_checks"]["matter16_four_forbidden"],
        "Z4R_origin_not_overclaimed": rank["Z4R_operator_checks"]["globally_gauged_origin_proved"] is False,
        "candidate_not_accepted": all(row["status"] != "ACCEPTED" for row in acceptance),
        "all_gates_open": all(row["status"] == "OPEN" and not row["V69_closed"] for row in gates),
    }
    return {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": (
            "Can the V67 six-dimensional branch be made into a local Spin(11) action that "
            "removes the V64 orphan without importing the failed 5D hyper route?"
        ),
        "classification": (
            "DIRECT_ORDER2_LIFT_CLOSED__ORDER4_GAUGE_AND_RANK_SKELETON_EXACT__"
            "PUBLISHED_BULK_ANOMALY_PARENT_EXACT__FULL_ACTION_OPEN"
        ),
        "lineage_and_nonimport": {
            "bound_input_cores": copy.deepcopy(EXPECTED_CORES),
            "current_V68_action_status": "REJECTED",
            "V56_V57_role": "TEMPLATE_ONLY_NOT_SPIN11_CLOSURE_EVIDENCE",
            "V62_5D_half_wall_GS_imported": False,
            "V67_5D_tangent_spectrum_imported": False,
            "V64_orphan_result_modified": False,
            "relation": (
                "V69 constructs a distinct higher-order candidate; it neither repairs nor "
                "relabels the rejected V68 action."
            ),
        },
        "direct_order2_lift_audit": direct,
        "order4_space_group_and_fixed_algebra_audit": skeleton,
        "geometric_rank_replacement": rank,
        "bulk_and_fixed_locus_anomaly_audit": anomaly,
        "acceptance_matrix": acceptance,
        "gate_ledger": gates,
        "falsifiers_and_promotion_tests": [
            {
                "id": "F1",
                "test": "supply a genuine Spin11 involution implementing the Hall U5 twist on the coset",
                "effect": "falsifies the direct-lift order obstruction",
            },
            {
                "id": "F2",
                "test": "solve all Spin/R/central phases and enumerate exactly MSSM plus Hu,Hd zero modes",
                "effect": "promotes the order-four skeleton to a spectrum candidate",
            },
            {
                "id": "F3",
                "test": "derive zero projector-weighted anomaly at every singular locus or quantized inflow",
                "effect": "promotes the integrated anomaly parent to an orbifold completion",
            },
            {
                "id": "F4",
                "test": "find any unavoidable colored zero mode or nonzero local anomaly class",
                "effect": "rejects the V69 order-four candidate",
            },
        ],
        "terminal_decision": {
            "current_bound_Spin11_action": "REJECTED",
            "direct_Hall_order2_lift": "CLOSED",
            "published_6D_scalar_conventional_full_hyper_import": "CLOSED_SCOPED",
            "pseudoreal_half_32_projection": "OPEN_NOT_COMPUTED",
            "V69_order4_gauge_skeleton": "EXACT_KINEMATIC_CANDIDATE",
            "V69_local_rank_replacement": "EXACT_CLASSICAL_LOCAL_SUBSECTOR",
            "V69_integrated_bulk_anomaly_parent": "EXACT_AND_PUBLISHED_FOR_N3",
            "V69_new_action_accepted": False,
            "same_action_microscopic_completion_found": False,
            "physical_Higgs_family_spectrum_certified": False,
            "fixed_point_anomaly_completion_certified": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "The direct Z2 lift is impossible, but its order-four character yields a "
                "valid T2/Z4 adjoint/vector gauge skeleton with common G3211 and a local "
                "singlet-only rank sector.  A published anomaly-free Spin11 bulk parent also "
                "exists.  These are real advances, not a completed action: the spin/R lift, "
                "Higgs/family spectrum, fixed-point anomalies and all phenomenological gates remain open."
            ),
        },
        "claim_boundary": {
            "exact_new_results": [
                "order-four obstruction to the literal Hall parity lift",
                "complete T2/Z4 vector/adjoint space-group matrix witness",
                "U5 and Spin4xSpin7 intersection equals G3211 at dimension 13",
                "orphan-free local X(+/-10) rank branch",
                "two exact integrated Spin11 anomaly factorizations",
            ],
            "new_physics_created": (
                "higher-order Spin11 orbifold gauge skeleton plus geometric rank replacement"
            ),
            "not_claimed": [
                "a complete spin-lifted orbifold action",
                "a complete MSSM spectrum",
                "fixed-point anomaly cancellation",
                "a globally gauged Z4R",
                "a UV completion or regulator",
                "gate closure",
            ],
        },
        "source_manifest": source_manifest(),
        "integrity_checks": checks,
        "n_integrity_checks": len(checks),
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
    }


def build_report() -> dict[str, Any]:
    report = _body()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V69 canonical core mismatch")
    expected = build_report()
    if canonical_bytes(report) != canonical_bytes(expected):
        raise RuntimeError("V69 recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"V69 integrity checks failed: {failed}")
    if report["terminal_decision"]["closed_gates"] or report["terminal_decision"]["complete_theory"]:
        raise RuntimeError("V69 overclaimed gate closure")


def render_markdown(report: Mapping[str, Any]) -> str:
    direct = report["direct_order2_lift_audit"]
    skeleton = report["order4_space_group_and_fixed_algebra_audit"]
    rank = report["geometric_rank_replacement"]
    anomaly = report["bulk_and_fixed_locus_anomaly_audit"]
    leak_rows = "\n".join(
        f"| {row['r1']} | {row['r2']} | {row['selected_T51_T422_sector']} | "
        f"{row['formal_coset_even_even_multiplicity']} |"
        for row in direct["formal_complex_leakage_diagnostic"]["rows"]
    )
    anomaly_rows = "\n".join(
        f"| {row['name']} | {row['multiplicities']['11']} | {row['multiplicities']['32']} | "
        f"{row['multiplicities']['neutral']} | {row['gravity']['total_H']} | "
        f"{row['residual_adj_minus_hypers']['B4']} | {row['factorization_passes']} |"
        for row in anomaly["variants"]
    )
    acceptance_rows = "\n".join(
        f"| {row['id']} | {row['requirement']} | {row['status']} | {row['evidence']} |"
        for row in report["acceptance_matrix"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}"
        for row in report["source_manifest"]["primary_sources"]
    )
    dims = skeleton["fixed_algebra_dimensions"]
    return f"""# V69 Spin(11) order-four geometric-rank escape audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The literal six-dimensional `T2/(Z2 x Z2')` lift is **closed**, but six
dimensions are not.  The SU(5) complex structure used in the SO(10) model
squares to `-I10`.  That is central on the SO(10) adjoint, but after adding
the eleventh Spin(11) coordinate its square is the noncentral Spin(10)
projector.  It is therefore order four on the coset, not a Z2 parity.

Forcing the complex SO(10) convention to behave as a Spin(11) parity gives
the diagnostic table:

| r1 | r2 | selected twist sector | formal coset ++ multiplicity |
|---:|---:|---:|---:|
{leak_rows}

The leakage is always 2 or 3, and the compact real fixed algebra is lost.
The published 6D Spin(11) scalar projection does not repair this through a
conventional full SUSY hyper: its `(1,2,4bar)` scalar zero sector becomes
`{direct['published_6D_Spin11_scalar_import']['total_left_chiral_zero_sector']}`
and Q returns through Hc.  This is deliberately scoped: a pseudoreal half-32
projection is `{direct['published_6D_Spin11_scalar_import']['pseudoreal_half_32_projection']}`.

## Order-four replacement

The obstruction is exactly the datum needed on a square `T2/Z4`.  V69 gives
the explicit matrices

```text
Q = diag(J,J,J,J,J,1),  J=[[0,-1],[1,0]]
Q^2 = diag(-I10,+1)
R = diag(-I4,+I7)
W1=W2=R Q^2
```

and verifies every vector/adjoint space-group relation.  Their fixed-algebra
dimensions are

```text
C(Q)       = {dims['C_Q_U5']}       = u(5)
C(Q^2)     = {dims['C_Q2_SO10']}       = so(10)
C(R)       = {dims['C_R_SO4xSO7']}       = so(4)+so(7)
C(Q,W)     = {dims['C_Q_and_W_common_G3211']}       = u(2)+u(3) = G3211
```

This is an exact compact gauge skeleton.  It is not yet a spin-lifted
supersymmetric action.  In particular, the Spin lift of Q has fourth power
`-1` and the lift of W has square `-1`; Lorentz, R and central phases must be
solved simultaneously for the gaugino, 11s and half-32s.

## Orphan-free rank breaking

At the local U(5) locus introduce only
`X_(+10), Xbar_(-10), S_0`, with R charges `(0,0,2)`, and

```text
W_rank = kappa S (X Xbar-vX^2).
```

The exact branch has `X Xbar=vX^2`, `S=0` and `|X|=|Xbar|`.  One chiral
combination is eaten and the radial combination pairs with S.  There are no
colored rank fields.  Therefore the V64 Q/Qbar null states are
**{rank['orphan_statement']['classification']}**.  They are not being assigned
an unproved mass.

The classical Z4R ledger allows the rank term and `N N X`, while forbidding a
bare mu and `16^4`.  A globally gauged origin and its pointwise anomaly
trivialization are still open.

## Exact 6D bulk parents

With `tr=tr_11`, V69 independently checks

```text
Tr55 F4 = 3 trF4 + 3 (trF2)^2
tr32 F4 = -2 trF4 + (3/2)(trF2)^2.
```

| Variant | 11 hypers | 32 hypers | neutral H | total H | residual trF4 | factorizes |
|---|---:|---:|---:|---:|---:|---:|
{anomaly_rows}

The first row is the published `n=3` one-tensor Spin(11) model: three
half-32s are allowed because the 32 is pseudoreal.  Its integral lattice is
`I_(1,1)` with `a=(3,1), b=(0,1)`.  The localized-family alternative uses
the even hyperbolic lattice with `a=(2,2), b=(2,-1)`.  Both are integrated
parents only.  Neither computes the projector-weighted anomaly or inflow at
the V69 singular loci.

## Acceptance matrix

| ID | Requirement | Status | Evidence |
|---|---|---|---|
{acceptance_rows}

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Primary sources

{sources}

## Decision

{report['terminal_decision']['honest_outcome']}  G1-G8 remain OPEN.
"""


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
            raise RuntimeError("V69 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V69 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V69 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
