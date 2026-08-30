#!/usr/bin/env python3
"""V59 audit of the gauged-U(1)_R local-orbifold completion route.

This certificate reconstructs the exact integrated Spin(10) x U(1)_{R+}
seed found in the V58 bounded search, binds the canonical V56 orbifold and V57
G1-frontier cores, and then applies the parity-weighted fixed-point anomaly
formula to the same V56 projector.

The result is fail-closed.  A complete, constructive parity assignment exists
for all 270 singlet hypers and supports the two formal Higgs coordinates used
by the diagonal-U(1) moment-map seed.  Nevertheless, the conventional
q(theta)=1 lift has non-universal mixed U(1)_R-G_f^2 anomalies at the GG,
flipped-GG, and Pati--Salam fixed points.  They cannot be produced by the
restriction of the only bulk Spin(10) Green--Schwarz invariant.  Repair needs
new localized non-singlet matter or new independently quantized localized
levels, neither of which belongs to the tested action.

Nothing here is an empirical discovery or a microscopic UV completion.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v59_gauged_u1r_local_completion_audit.py"

INPUTS = {
    "v56_orbifold": ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json",
    "v57_frontier": ROOT / "SUSY_V57_G1_MICROSCOPIC_COMPLETION_FRONTIER_AUDIT.json",
}

EXPECTED_CORES = {
    "v56_orbifold": "09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55",
    "v57_frontier": "0896cc21d84d6395d6ba9d5c0b6414c3aec14c18981708d2e06b548a4fc21302",
}

FIXED_POINTS = ("O_SO10", "O_GG", "O_flipped", "O_PS")

STATUS = (
    "V59_GAUGED_U1R_LOCAL_COMPLETION__V56_V57_CORES_BOUND__V58_INTEGRATED_"
    "SPIN10_X_U1R_SEED_RECONSTRUCTED_EXACTLY__270_SINGLET_PARITIES_HAVE_AN_"
    "EXPLICIT_VEV_COMPATIBLE_SOLUTION__CONVENTIONAL_QTHETA1_LIFT_HAS_"
    "NONUNIVERSAL_MIXED_U1R_GFP2_ANOMALIES_AT_GG_FLIPPED_AND_PS__EXISTING_"
    "BULK_SPIN10_GS_INVARIANT_CANNOT_CANCEL_THEM__LOCALIZED_LEVELS_NORMAL_"
    "BUNDLE_DYONIC_STRING_AND_RESIDUAL_NORMALIZATION_DATA_OPEN__SAME_ACTION_"
    "MICROSCOPIC_COMPLETION_FALSE__G1_OPEN__ZERO_GATE_PROMOTIONS"
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


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing V59 input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def dot_i11(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> Fraction:
    return x[0] * y[0] - x[1] * y[1]


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def integrated_u1r_seed() -> dict[str, Any]:
    """Reconstruct the exact V58 integrated seed equation by equation."""

    blocks = [
        {"representation": "10", "dimension": 10, "multiplicity": 2, "q": -1},
        {"representation": "1", "dimension": 1, "multiplicity": 161, "q": 0},
        {"representation": "1", "dimension": 1, "multiplicity": 4, "q": 1},
        {"representation": "1", "dimension": 1, "multiplicity": 10, "q": 2},
        {"representation": "1", "dimension": 1, "multiplicity": 94, "q": 3},
        {"representation": "1", "dimension": 1, "multiplicity": 1, "q": 4},
    ]
    n_h = sum(row["dimension"] * row["multiplicity"] for row in blocks)
    n_v = 45 + 1
    tensors = 1
    s1 = sum(row["dimension"] * row["multiplicity"] * row["q"] for row in blocks)
    s2 = sum(row["dimension"] * row["multiplicity"] * row["q"] ** 2 for row in blocks)
    s4 = sum(row["dimension"] * row["multiplicity"] * row["q"] ** 4 for row in blocks)
    q10_square_sum = 2

    alpha = Fraction(n_v - 20 - s2, 6)
    beta = Fraction(8 - 2, 6)
    gamma = Fraction(2 * (s4 - n_v - 4), 3)
    delta = 4 * (q10_square_sum - 8)
    epsilon = Fraction(2 * (0 - 3), 3)

    a = (Fraction(3), Fraction(1))
    b10 = (Fraction(0), Fraction(-2))
    b_r = (Fraction(52), Fraction(6))
    bar_b_r = (Fraction(26), Fraction(3))
    j = (Fraction(5, 3), Fraction(4, 3))

    # Y_1=(3/2)u-104f, Y_2=(1/2)u-12f-2t and
    # P=1/2(Y_1^2-Y_2^2).  Coefficients are ordered as
    # (u^2, uf, ut, f^2, ft, t^2).
    y1 = (Fraction(3, 2), Fraction(-104), Fraction(0))
    y2 = (Fraction(1, 2), Fraction(-12), Fraction(-2))
    expanded = (
        Fraction(y1[0] ** 2 - y2[0] ** 2, 2),
        y1[0] * y1[1] - y2[0] * y2[1],
        y1[0] * y1[2] - y2[0] * y2[2],
        Fraction(y1[1] ** 2 - y2[1] ** 2, 2),
        y1[1] * y1[2] - y2[1] * y2[2],
        Fraction(y1[2] ** 2 - y2[2] ** 2, 2),
    )
    target = (Fraction(1), alpha, beta, gamma, Fraction(delta), epsilon)

    q_av = Fraction(s1, n_h)
    moment_q0 = Fraction(2 + n_h * q_av, 2)
    moment_q4 = moment_q0 + 4
    formal_tangent_weights = (144, 148)

    return {
        "id": "V58_RECONSTRUCTED_DIAGONAL_SPIN10_X_U1R_PLUS_SEED",
        "provenance": (
            "Reconstructed from the exact V58 route-C equations supplied to V59; "
            "there is no canonical V58 gauged-U1R artifact to import."
        ),
        "gauge_group": "Spin(10) x U(1)_{R+}",
        "hypermultiplet_blocks": blocks,
        "spectrum": {
            "T": tensors,
            "V": n_v,
            "H": n_h,
            "H_minus_V_plus_29T": n_h - n_v + 29 * tensors,
            "gravitational_irreducible_cancels": n_h - n_v + 29 * tensors == 273,
        },
        "charge_sums": {
            "S1": s1,
            "S2": s2,
            "S4": s4,
            "q_average": fraction_text(q_av),
            "q10_square_sum": q10_square_sum,
        },
        "anomaly_polynomial": {
            "variables": {"u": "tr R^2", "f": "F_R^2", "t": "tr_10 F_Spin10^2"},
            "coefficient_order": ["u^2", "u f", "u t", "f^2", "f t", "t^2"],
            "coefficients": [fraction_text(x) for x in target],
            "expression": "u^2 - 150 u f + u t + 5336 f^2 - 24 f t - 2 t^2",
            "factorization": "1/2[(3u/2-104f)^2-(u/2-12f-2t)^2]",
            "expanded_factorization_coefficients": [fraction_text(x) for x in expanded],
            "factorization_exact": expanded == target,
        },
        "string_charge_lattice": {
            "name": "odd unimodular I_(1,1)",
            "Omega": [[1, 0], [0, -1]],
            "determinant": -1,
            "a": [3, 1],
            "b_Spin10": [0, -2],
            "b_R": [52, 6],
            "bar_b_R": [26, 3],
            "pairings": {
                "a_squared": int(dot_i11(a, a)),
                "a_dot_b_Spin10": int(dot_i11(a, b10)),
                "b_Spin10_squared": int(dot_i11(b10, b10)),
                "a_dot_bar_b_R": int(dot_i11(a, bar_b_r)),
                "b_Spin10_dot_bar_b_R": int(dot_i11(b10, bar_b_r)),
                "bar_b_R_squared": int(dot_i11(bar_b_r, bar_b_r)),
            },
            "a_characteristic": True,
            "b_Spin10_even": True,
            "integral_unimodular": True,
        },
        "positive_chamber": {
            "j": ["5/3", "4/3"],
            "j_squared": fraction_text(dot_i11(j, j)),
            "j_dot_a": fraction_text(dot_i11(j, a)),
            "j_dot_b_Spin10": fraction_text(dot_i11(j, b10)),
            "j_dot_b_R": fraction_text(dot_i11(j, b_r)),
            "all_declared_kinetic_pairings_positive": all(
                dot_i11(j, x) > 0 for x in (a, b10, b_r)
            ),
        },
        "formal_rank_one_vacuum": {
            "moment_map_equation": "150 |z_4|^2 + 146 |z_0|^2 = 2",
            "solution": {"abs_z4_squared": "1/150", "abs_z0_squared": "1/146"},
            "equation_exact": moment_q4 * Fraction(1, 150) + moment_q0 * Fraction(1, 146) == 2,
            "unrescaled_tangent_weights": list(formal_tangent_weights),
            "formal_gcd": math.gcd(*formal_tangent_weights),
            "warning": (
                "The anomaly charges q_I, the -2 A_+ T_R+ scalar covariant derivative, "
                "and the supercharge/orbifold spin lift have not been placed in one "
                "faithful compact-group normalization.  The formal gcd=4 is not yet a "
                "proof of a residual q(theta)=1 Z4R."
            ),
        },
    }


def local_signs(base: int, t1: int, t2: int) -> tuple[int, int, int, int]:
    if any(x not in (-1, 1) for x in (base, t1, t2)):
        raise ValueError("parities must be +/-1")
    return (base, base * t1, base * t2, base * t1 * t2)


def parity_key(triple: tuple[int, int, int]) -> str:
    return "".join("+" if x == 1 else "-" for x in triple)


def parity_triple(key: str) -> tuple[int, int, int]:
    if len(key) != 3 or any(x not in "+-" for x in key):
        raise ValueError(f"bad parity key: {key}")
    return tuple(1 if x == "+" else -1 for x in key)  # type: ignore[return-value]


def constructive_singlet_parities() -> dict[str, Any]:
    """Give an exact parity solution for every singlet hyper.

    One q=0 and the unique q=4 hyper use (+++) and therefore have constant
    zero modes.  Every other singlet is paired between (+-+) and (--+), whose
    local sign vectors are negatives.  All non-VEV spectator contributions to
    every parity-weighted moment cancel pointwise.
    """

    counts = {
        0: {"+++": 1, "+-+": 80, "--+": 80},
        1: {"+-+": 2, "--+": 2},
        2: {"+-+": 5, "--+": 5},
        3: {"+-+": 47, "--+": 47},
        4: {"+++": 1},
    }
    expected = {0: 161, 1: 4, 2: 10, 3: 94, 4: 1}
    totals = {q: sum(classes.values()) for q, classes in counts.items()}

    def moment(power: int) -> list[int]:
        out = [0, 0, 0, 0]
        for q, classes in counts.items():
            weight = 1 if power == 0 else q**power
            for key, number in classes.items():
                signs = local_signs(*parity_triple(key))
                for index, sign in enumerate(signs):
                    out[index] += number * weight * sign
        return out

    non_vev_cancel = all(
        local_signs(*parity_triple("+-+"))[i]
        + local_signs(*parity_triple("--+"))[i]
        == 0
        for i in range(4)
    )
    return {
        "parity_key_order": "(base reflection, translation 1, translation 2)",
        "fixed_point_order": list(FIXED_POINTS),
        "counts_by_charge_and_parity": {str(q): rows for q, rows in counts.items()},
        "expected_charge_multiplicities": {str(q): n for q, n in expected.items()},
        "actual_charge_multiplicities": {str(q): n for q, n in totals.items()},
        "all_270_singlets_assigned": totals == expected and sum(totals.values()) == 270,
        "q0_global_zero_mode_count": counts[0].get("+++", 0),
        "q4_global_zero_mode_count": counts[4].get("+++", 0),
        "no_other_singlet_zero_modes": all(
            counts[q].get("+++", 0) == 0 for q in (1, 2, 3)
        ),
        "non_VEV_spectator_pairs_cancel_pointwise": non_vev_cancel,
        "local_parity_moments": {
            "sum_sign": moment(0),
            "sum_q_sign": moment(1),
            "sum_q_cubed_sign": moment(3),
        },
        "interpretation": (
            "The singlet parity problem is feasible.  It is not the obstruction: "
            "the surviving constant q=4 coordinate contributes q=(4,4,4,4) and "
            "q^3=(64,64,64,64), which still requires local inflow."
        ),
    }


def v56_ten_traces(v56: Mapping[str, Any]) -> dict[str, Any]:
    ledger = v56["orbifold_mode_certificate"]["component_ledger"]
    dimensions = {"h3": 3, "bar_h3": 3, "h2": 2, "bar_h2": 2}
    by_hyper: dict[str, list[int]] = {}
    for hyper in ("H10", "H10_prime"):
        rows = [
            row
            for row in ledger
            if row["hypermultiplet"] == hyper and row["four_dimensional_chiral"] == "H"
        ]
        traces = []
        for point in FIXED_POINTS:
            traces.append(
                sum(
                    dimensions[row["component"]]
                    * row["fixed_point_local_signs"][point]
                    for row in rows
                )
            )
        by_hyper[hyper] = traces
    combined = [sum(by_hyper[h][i] for h in by_hyper) for i in range(4)]
    return {
        "fixed_point_order": list(FIXED_POINTS),
        "trace_of_local_parity_in_10": by_hyper,
        "combined_trace": combined,
        "expected_each_trace": [10, 0, 0, -2],
        "matches_V56_projector": all(row == [10, 0, 0, -2] for row in by_hyper.values()),
        "U1R_linear_and_cubic_contribution_for_q10_minus1": [-x for x in combined],
    }


def proportionality_certificate(
    labels: Iterable[str], local: Iterable[int], bulk_restriction: Iterable[int]
) -> dict[str, Any]:
    labels_t = tuple(labels)
    local_t = tuple(local)
    bulk_t = tuple(bulk_restriction)
    minors = {}
    for i in range(len(labels_t)):
        for j in range(i + 1, len(labels_t)):
            minors[f"{labels_t[i]}__{labels_t[j]}"] = (
                local_t[i] * bulk_t[j] - local_t[j] * bulk_t[i]
            )
    proportional = all(value == 0 for value in minors.values())
    return {
        "invariant_order": list(labels_t),
        "local_mixed_anomaly_coefficients": list(local_t),
        "bulk_tr10_restriction_coefficients": list(bulk_t),
        "two_by_two_minors": minors,
        "lies_in_existing_bulk_GS_direction": proportional,
    }


def fixed_point_mixed_anomaly_ledger() -> list[dict[str, Any]]:
    """Exact mixed U(1)_R-G_f^2 coefficients in the q(theta)=1 branch.

    Dynkin indices use A(fundamental)=1.  The raw integer X charges are the
    V56 convention.  Overall common orbifold factors do not affect the tested
    proportionality minors.
    """

    so10 = proportionality_certificate(["Spin10"], [8 - 2], [1])
    so10.update(
        {
            "fixed_point": "O_SO10",
            "sources": {
                "Spin10_gaugino": 8,
                "two_10_hyperinos_q_minus1": -2,
            },
            "status": "NO_RATIO_OBSTRUCTION_AT_THIS_POINT",
        }
    )

    # At GG, 45 -> 24_0 + 1_0 + 10_4 + 10bar_-4.  The unbroken pieces
    # have vector parity + and the coset pieces have parity -.  The two bulk
    # 10 hypers have opposite GG parity matrices and cancel.  Brane X, Xbar
    # have fermion R charge -1 and raw X charges +/-10.
    gg_bulk = [10 - 2 * 3, -(10 * 4**2 + 10 * 4**2)]
    gg_brane = [0, -(10**2 + 10**2)]
    # The inherited bulk delta function integrates to a convention-dependent
    # corner weight relative to a canonically normalized localized 4D field.
    # Keep the exact bulk vector as the ratio test.  A positive relative brane
    # weight c only changes the minor from 800 to 800+400c, so X/Xbar cannot
    # rescue it in any physical normalization.
    gg = proportionality_certificate(["SU5_squared", "X_squared"], gg_bulk, [2, 40])
    gg.update(
        {
            "fixed_point": "O_GG",
            "sources": {
                "bulk_vector_45": gg_bulk,
                "bulk_10_pair": [0, 0],
                "three_brane_families": [0, 0],
                "brane_X_Xbar_raw_4D": gg_brane,
                "brane_S": [0, 0],
            },
            "bulk_only_minor": gg_bulk[0] * 40 - gg_bulk[1] * 2,
            "minor_after_positive_brane_weight": "800 + 400 c_brane > 0",
            "all_positive_brane_delta_normalizations_fail": True,
            "status": "FAIL_EXISTING_BULK_GS_DIRECTION",
        }
    )

    flipped_bulk = [10 - 2 * 3, -(10 * 4**2 + 10 * 4**2)]
    flipped = proportionality_certificate(
        ["SU5prime_squared", "Xprime_squared"], flipped_bulk, [2, 40]
    )
    flipped.update(
        {
            "fixed_point": "O_flipped",
            "sources": {"bulk_vector_45": flipped_bulk, "bulk_10_pair": [0, 0]},
            "status": "FAIL_EXISTING_BULK_GS_DIRECTION",
        }
    )

    # At PS, vector: (A_adj4-4 A_6, A_adj2-12 A_2, same)=(0,-8,-8).
    # Each q=-1 ten has P=+ on (1,2,2) and P=- on (6,1,1), hence
    # (+2,-2,-2); the pair gives (+4,-4,-4).
    ps_vector = [8 - 4 * 2, 4 - 12, 4 - 12]
    ps_two_tens = [4, -4, -4]
    ps_total = [ps_vector[i] + ps_two_tens[i] for i in range(3)]
    ps = proportionality_certificate(
        ["SU4_squared", "SU2L_squared", "SU2R_squared"], ps_total, [2, 2, 2]
    )
    ps.update(
        {
            "fixed_point": "O_PS",
            "sources": {
                "bulk_vector_45": ps_vector,
                "two_10_hyperinos_q_minus1": ps_two_tens,
                "localized_matter": [0, 0, 0],
            },
            "four_weak_mode_topology_forces_both_ten_PS_patterns": True,
            "status": "FAIL_EXISTING_BULK_GS_DIRECTION",
        }
    )
    return [so10, gg, flipped, ps]


def partial_u1r_local_ledger(
    singlets: Mapping[str, Any], tens: Mapping[str, Any]
) -> dict[str, Any]:
    """Resolved spin-1/2 U(1)_R moments before gravity/tensor fields."""

    spin10_gaugino_trace = [45, 5, 5, -3]
    u1r_gaugino_trace = [1, 1, 1, 1]
    ten_q1 = tens["U1R_linear_and_cubic_contribution_for_q10_minus1"]
    singlet_q1 = singlets["local_parity_moments"]["sum_q_sign"]
    singlet_q3 = singlets["local_parity_moments"]["sum_q_cubed_sign"]
    linear = [
        spin10_gaugino_trace[i] + u1r_gaugino_trace[i] + ten_q1[i] + singlet_q1[i]
        for i in range(4)
    ]
    cubic = [
        spin10_gaugino_trace[i] + u1r_gaugino_trace[i] + ten_q1[i] + singlet_q3[i]
        for i in range(4)
    ]
    return {
        "fixed_point_order": list(FIXED_POINTS),
        "scope": (
            "Spin(10) and U(1)_R gauginos, two charged tens, and all charged "
            "singlet hyperinos; common orbifold normalization suppressed."
        ),
        "source_vectors": {
            "Spin10_gaugino_parity_trace_q1": spin10_gaugino_trace,
            "U1R_gaugino_parity_trace_q1": u1r_gaugino_trace,
            "two_10_hyperinos_q_minus1": ten_q1,
            "singlets_sum_q_sign": singlet_q1,
            "singlets_sum_q_cubed_sign": singlet_q3,
        },
        "mixed_gravity_U1R_spin_half_numerator": linear,
        "pure_U1R_cubic_spin_half_numerator": cubic,
        "not_included": [
            "orbifold parities and local anomaly coefficients of the gravitino and tensorino",
            "normal-bundle SO(2) charges of bulk and localized fermions",
            "localized regulator/Bardeen-counterterm convention",
        ],
        "complete_local_anomaly_polynomial": False,
    }


def local_gs_and_global_obligations(mixed_rows: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [row["fixed_point"] for row in mixed_rows if not row["lies_in_existing_bulk_GS_direction"]]
    return {
        "standard_bulk_tensor_inflow_test": {
            "principle": (
                "For U(1)_R variation, any inflow from the existing two bulk tensors "
                "multiplies the restriction of the single Spin(10) invariant "
                "tr_10 F^2.  Tensor-lattice rank changes the overall local coefficient, "
                "not the relative subgroup embedding indices."
            ),
            "failed_fixed_points": failed,
            "passes_all_four": not failed,
        },
        "why_arbitrary_local_levels_are_not_imported": (
            "Independent B wedge tr F_k^2 coefficients at a broken fixed point would be "
            "new localized action data.  Their lattice vectors, tensor transformations, "
            "large-gauge quantization, supersymmetric completion, and sum-rule/Bianchi "
            "integrability are absent from the existing seed."
        ),
        "normal_bundle_local_lorentz": {
            "status": "OPEN_DATA_DEFICIT",
            "reason": (
                "The fixed-point lift on the gravitino/tensorino and the SO(2) normal-"
                "bundle charges of localized fields are unspecified; a gauge-only "
                "parity ledger cannot certify local Lorentz invariance."
            ),
        },
        "self_dual_strings": {
            "integrated_prerequisites_that_pass": [
                "integral unimodular I_(1,1) lattice",
                "characteristic gravitational vector a",
                "integral Spin(10) and abelian anomaly vectors",
                "positive classical kinetic chamber",
            ],
            "status": "OPEN_DATA_DEFICIT",
            "missing": [
                "effective/dyonic string charge cone",
                "existence of string solutions in the diagonal U(1)_R potential",
                "worldsheet anomaly polynomial for every primitive effective charge",
                "unitarity/central-charge and current-algebra-level checks",
                "orbifold action and endpoints/defects on the strings",
            ],
        },
        "connected_global_anomaly": {
            "bulk_statement": "Omega_7^Spin(B(Spin(10) x U(1)))=0 in the cited connected-group theorem",
            "does_not_cover": [
                "the orbifold space group",
                "the residual discrete R group and its spin extension",
                "localized tensor defects",
                "normal-bundle anomalies",
            ],
        },
    }


def residual_z4r_normalization() -> dict[str, Any]:
    return {
        "required_4D_convention": {
            "q_theta": 1,
            "vector_gaugino": 1,
            "H_and_Hprime_hyperino": -1,
            "Hc_and_Hprimec_hyperino": 1,
        },
        "conditional_branch_used_for_local_no_go": (
            "The conventional lift q_10=-1 is imposed because it is exactly what maps "
            "the surviving H/Hprime superfields to R charge zero when q(theta)=1."
        ),
        "formal_diagonal_coset_result": {
            "q_average": 1,
            "VEV_coordinate_naive_weights": [144, 148],
            "naive_gcd": 4,
        },
        "why_not_proved": (
            "The published diagonal-gauging action normalizes anomaly charges with "
            "minimal hyperfermion charge one while the nonlinear scalar derivative is "
            "D phi=d phi-2 A_+ T_R+ phi.  No explicit compact generator, supercharge "
            "spin lift, and V56 orbifold action has been supplied in one normalization."
        ),
        "bifurcated_verdict": {
            "if_conventional_lift_is_adopted": (
                "the exact fixed-point mixed-anomaly ratio obstruction rejects the "
                "existing same-action completion"
            ),
            "if_the_lift_is_changed": (
                "preservation of the V56 q(theta)=1 Z4R charges is no longer proved"
            ),
        },
        "faithful_residual_Z4R_proved": False,
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {
            "title": "Bulk and Brane Anomalies in Six Dimensions",
            "url": "https://arxiv.org/abs/hep-ph/0209144",
            "use": "four-fixed-point parity trace formula and the SO(10) projector",
        },
        {
            "title": "Localized anomalies in orbifold gauge theories",
            "url": "https://arxiv.org/abs/hep-th/0305024",
            "use": "conditions and restricted tensor mechanisms for localized inflow",
        },
        {
            "title": "Anomalies on Six Dimensional Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "use": "fixed-point gauge and normal-bundle/local-Lorentz anomaly obligations",
        },
        {
            "title": "Diagonally gauged anomaly-free 6D supergravities and their vacua",
            "url": "https://arxiv.org/abs/2607.21311",
            "use": "U(1)_R+ anomaly polynomial, lattice normalization, action, and moment-map vacua",
        },
        {
            "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
            "url": "https://arxiv.org/abs/1711.04777",
            "use": "string-charge lattice and global-form quantization",
        },
        {
            "title": "Global anomalies in 6D gauged supergravities",
            "url": "https://arxiv.org/abs/2507.22127",
            "use": "connected-group bordism and gauged-R global consistency",
        },
        {
            "title": "On the consistency of a class of R-symmetry gauged 6D N=(1,0) supergravities",
            "url": "https://arxiv.org/abs/2002.04619",
            "use": "dyonic-string existence and worldsheet-inflow caveats for gauged R symmetry",
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def gate_ledger() -> list[dict[str, Any]]:
    reasons = {
        "G1": (
            "OPEN/REJECTED FOR THIS ROUTE: exact non-universal U(1)_R-G_f^2 fixed-point "
            "anomalies are outside the existing bulk Spin(10) GS direction; local Lorentz, "
            "dyonic-string, and faithful residual-Z4R data are also open."
        ),
        "G2": "OPEN: no one-action microscopic symmetry lift or complete local counterterm action.",
        "G3": "OPEN: the orbifolded interacting gauged-supergravity vacuum/Hessian is not solved.",
        "G4": "OPEN: V56's bounded projector remains conditional on the unresolved full boundary ring.",
        "G5": "OPEN: no dark/cosmological completion.",
        "G6": "OPEN: no compactification threshold or precision-unification match.",
        "G7": "OPEN: no full KK proton tensor or lifetime prediction.",
        "G8": "OPEN: no mediator-complete flavour/seesaw fit.",
    }
    return [
        {"gate": gate, "status": "OPEN", "V59_candidate_closed": False, "decision": reason}
        for gate, reason in reasons.items()
    ]


def build_report() -> dict[str, Any]:
    v56 = load_bound("v56_orbifold")
    v57 = load_bound("v57_frontier")
    seed = integrated_u1r_seed()
    singlets = constructive_singlet_parities()
    tens = v56_ten_traces(v56)
    mixed = fixed_point_mixed_anomaly_ledger()
    partial = partial_u1r_local_ledger(singlets, tens)
    obligations = local_gs_and_global_obligations(mixed)
    residual = residual_z4r_normalization()
    gates = gate_ledger()

    integrity = {
        "bound_V56_V57_cores_are_canonical_and_expected": True,
        "integrated_seed_gravitational_equation_is_273": seed["spectrum"]["H_minus_V_plus_29T"] == 273,
        "integrated_seed_factorization_is_exact": seed["anomaly_polynomial"]["factorization_exact"],
        "integrated_seed_lattice_is_integral_unimodular": seed["string_charge_lattice"]["integral_unimodular"],
        "integrated_seed_positive_chamber_exists": seed["positive_chamber"]["all_declared_kinetic_pairings_positive"],
        "formal_rank_one_moment_map_solution_is_exact": seed["formal_rank_one_vacuum"]["equation_exact"],
        "all_270_singlet_parities_are_assigned": singlets["all_270_singlets_assigned"],
        "singlet_assignment_supports_q0_and_q4_zero_modes": singlets["q0_global_zero_mode_count"] == 1 and singlets["q4_global_zero_mode_count"] == 1,
        "non_VEV_singlet_spectators_cancel_pointwise": singlets["non_VEV_spectator_pairs_cancel_pointwise"],
        "V56_ten_trace_is_recomputed_from_component_ledger": tens["matches_V56_projector"],
        "SO10_fixed_point_has_no_subgroup_ratio_obstruction": mixed[0]["lies_in_existing_bulk_GS_direction"],
        "GG_fixed_point_fails_existing_GS_direction": not mixed[1]["lies_in_existing_bulk_GS_direction"],
        "flipped_fixed_point_fails_existing_GS_direction": not mixed[2]["lies_in_existing_bulk_GS_direction"],
        "PS_fixed_point_fails_existing_GS_direction": not mixed[3]["lies_in_existing_bulk_GS_direction"],
        "standard_bulk_tensor_inflow_fails_at_three_points": obligations["standard_bulk_tensor_inflow_test"]["failed_fixed_points"] == ["O_GG", "O_flipped", "O_PS"],
        "partial_U1R_ledger_is_not_misreported_as_complete": not partial["complete_local_anomaly_polynomial"],
        "faithful_residual_Z4R_is_not_overclaimed": not residual["faithful_residual_Z4R_proved"],
        "no_gate_is_promoted": all(row["status"] == "OPEN" and not row["V59_candidate_closed"] for row in gates),
    }

    report: dict[str, Any] = {
        "schema": "susy_v59_gauged_u1r_local_completion_audit/v1",
        "status": STATUS,
        "question": (
            "Can the exact integrated Spin(10) x U(1)_R+ seed be promoted to a "
            "four-fixed-point, localized-GS, self-dual-string-consistent microscopic "
            "completion of the V56 orbifold while preserving q(theta)=1 Z4R?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "upstream_status": {"V56": v56["status"], "V57": v57["status"]},
        "integrated_u1r_seed": seed,
        "singlet_parity_solution": singlets,
        "V56_two_ten_parity_trace": tens,
        "fixed_point_mixed_U1R_gauge_anomaly_ledger": mixed,
        "partial_local_U1R_anomaly_ledger": partial,
        "localized_GS_and_global_obligations": obligations,
        "residual_Z4R_normalization_audit": residual,
        "smallest_action_change": {
            "required": True,
            "options": [
                (
                    "add explicitly charged localized non-singlet fermions at O_GG, "
                    "O_flipped, and O_PS whose anomaly vectors cancel the non-universal "
                    "minors, then re-solve all 6D/local gravitational and discrete anomalies"
                ),
                (
                    "or add independently quantized localized tensor/axion levels for each "
                    "unbroken subgroup invariant, with a supersymmetric action, Bianchi "
                    "sum rules, and large-gauge proof"
                ),
                (
                    "or change the four-weak-mode parity topology/10 charges and rerun the "
                    "integrated anomaly/lattice/vacuum problem from the beginning"
                ),
            ],
            "not_a_small_parameter_retuning": True,
            "no_repair_is_part_of_the_tested_action": True,
        },
        "strict_decision": {
            "singlet_parity_problem_solved": True,
            "four_fixed_point_existing_GS_completion": False,
            "same_action_microscopic_completion": False,
            "V59_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "honest_outcome": (
                "Route C advances beyond integrated I8 and is rejected for the existing "
                "action by an exact fixed-point invariant-ratio certificate.  The result "
                "is stronger than a mere missing-data verdict, while the normal-bundle, "
                "string-worldsheet, and faithful residual-Z4R sectors remain explicit "
                "data deficits rather than assumed passes."
            ),
        },
        "gate_ledger": gates,
        "primary_sources": primary_sources(),
        "source_manifest": source_manifest(),
        "integrity_checks": integrity,
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise AssertionError("V59 canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise AssertionError(f"V59 integrity failures: {failed}")
    if report["strict_decision"]["same_action_microscopic_completion"]:
        raise AssertionError("V59 must not promote the rejected local route")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V59 promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    seed = report["integrated_u1r_seed"]
    singlets = report["singlet_parity_solution"]
    mixed = report["fixed_point_mixed_U1R_gauge_anomaly_ledger"]
    partial = report["partial_local_U1R_anomaly_ledger"]
    lattice = seed["string_charge_lattice"]
    rows = "\n".join(
        f"| {row['fixed_point']} | {row['local_mixed_anomaly_coefficients']} | "
        f"{row['bulk_tr10_restriction_coefficients']} | "
        f"{row['two_by_two_minors'] or 'n/a'} | {row['status']} |"
        for row in mixed
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['use']}"
        for row in report["primary_sources"]
    )
    return f"""# V59 gauged-U(1)R local-completion audit

Status: `{report['status']}`

## Result

**The existing route-C action cannot be completed by its bulk Green--Schwarz
sector. G1 remains OPEN, and no gate is promoted.**

V59 does solve the previously unspecified 270-singlet parity problem: an exact
assignment supports one neutral and one charge-four constant coordinate and
pairs every other spectator so its parity-weighted moments cancel pointwise.
The obstruction instead comes from fields that the four-weak-mode topology
fixes: the Spin(10) gaugino and the two charged bulk tens.

## Reconstructed integrated seed

```text
T=1, V=46, H=290,       H-V+29T = {seed['spectrum']['H_minus_V_plus_29T']}
S2={seed['charge_sums']['S2']}, S4={seed['charge_sums']['S4']}, q_av={seed['charge_sums']['q_average']}
P = {seed['anomaly_polynomial']['expression']}
  = {seed['anomaly_polynomial']['factorization']}
Omega = {lattice['Omega']}
a={lattice['a']}, b10={lattice['b_Spin10']}, bar_bR={lattice['bar_b_R']}
```

The lattice is integral and unimodular, `a` is characteristic, the polynomial
factorization is exact, and the positive chamber `j=(5/3,4/3)` exists. These
remain integrated-bulk results only.

The formal moment-map seed is

```text
150 |z4|^2 + 146 |z0|^2 = 2,
|z4|^2=1/150, |z0|^2=1/146.
```

Its unrescaled tangent weights `(148,144)` have gcd four. Because the scalar
derivative is `Dphi=dphi-2 A T phi`, while the anomaly spectrum uses minimal
hyperfermion charge one, this gcd is not yet a faithful `q(theta)=1` residual
group calculation.

## Exact singlet parity solution

Parity keys are `(base,t1,t2)`. The nonzero counts are

```text
q=0: +++ x1, +-+ x80, --+ x80
q=1:          +-+ x2,  --+ x2
q=2:          +-+ x5,  --+ x5
q=3:          +-+ x47, --+ x47
q=4: +++ x1
```

The two paired character vectors are negatives at every fixed point. Hence

```text
sum sign       = {singlets['local_parity_moments']['sum_sign']}
sum q sign     = {singlets['local_parity_moments']['sum_q_sign']}
sum q^3 sign   = {singlets['local_parity_moments']['sum_q_cubed_sign']}.
```

This is a feasibility witness, not local anomaly cancellation.

## Fixed-point mixed-anomaly certificate

Indices use `A(fund)=1`; raw `X` charges are the V56 convention. A common
orbifold normalization cancels from every proportionality minor.

| Fixed point | Local U(1)R-Gf^2 vector | restriction of tr10 F^2 | minors | verdict |
|---|---|---|---|---|
{rows}

At `O_PS`, for example,

```text
45 gaugino:  (0,-8,-8)
two 10s:     (4,-4,-4)
total:       (4,-12,-12)
bulk tr10:   (2, 2, 2).
```

The nonzero minors are invariant under any overall tensor-inflow coefficient.
At `O_GG`, the exact bulk vector `(4,-320)` is not proportional to the
Spin(10) restriction `(2,40)`; its minor is `800`. The brane `X_10` and
`Xbar_-10` fermions have the raw 4D contribution `(0,-200)` because their
superfields have R charge zero and their fermions charge minus one. If the
relative corner delta normalization is any positive `c_brane`, the minor is
`800+400 c_brane`, so this localized pair cannot rescue the mismatch.

Two bulk tensors do not repair these ratios: they can alter the local overall
coefficient but both couple to the same restricted Spin(10) invariant. New
subgroup-specific localized levels or non-singlet localized matter would be a
new action and require fresh quantization, Bianchi, supersymmetry, and anomaly
checks.

## Remaining local/global data deficits

The resolved spin-half numerators are

```text
grav^2-U(1)R: {partial['mixed_gravity_U1R_spin_half_numerator']}
U(1)R^3:      {partial['pure_U1R_cubic_spin_half_numerator']}.
```

They deliberately exclude the gravitino/tensorino fixed-point lift and do not
pretend to be a complete local polynomial. The normal-bundle `SO(2)` anomaly,
localized tensor transformations, effective dyonic-string cone, string
worldsheet anomaly/central-charge tests, and orbifold action on strings remain
unspecified. The connected bulk bordism result does not cover these defects or
the residual discrete R group.

## Fail-closed decision

{report['strict_decision']['honest_outcome']}

The smallest repair is not a coupling retuning: add explicitly quantized
localized subgroup-specific GS data or anomaly-canceling non-singlet matter,
then recompute the complete integrated and local theory. Alternatively change
the Higgs parity topology and restart the bulk spectrum/lattice problem.

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown artifacts")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()

    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V59 artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V59 JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V59 Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
