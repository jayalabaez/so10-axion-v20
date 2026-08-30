#!/usr/bin/env python3
"""V56 exact two-site locality/link-parity selector for the SO(10) filter.

This is deliberately a changed representation architecture, not a repair of
the V54/V55 one-site action.  Put the left filter vectors on SO(10)_L, H2 on
SO(10)_R, and replace the missing-VEV adjoint in the filter by the 45 component
of an even bifundamental B_LR.  Odd identity links Omega and Omegabar break the
product group.  Gauge-index path parity then proves that every allowed
left-right Higgs bilinear contains an odd number of B links.  Consequently the
missing-VEV zero protects the weak block, while h A H2, L h H2, and all paths
made solely from identity links are forbidden.

The connected-path selector statement and filter ranks are exact.  A stress
test of disconnected contractions finds a degree-six counterexample,
``(h Omega H2) Tr(A B Omega^T)``, which is nonzero on the declared vacuum.
Thus the finite selector does not protect the complete polynomial action and
no gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V56_TWO_SITE_LINK_PARITY_SELECTOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V56_TWO_SITE_LINK_PARITY_SELECTOR_AUDIT.md"
V55_PATH = ROOT / "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.json"
V54_R1_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
EXPECTED_V55_CORE = "895f999b53fcf7c4e513e0f9c6ee3245d166d8db8d3cfceaff3d9d8c2af25330"
EXPECTED_V54_R1_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"

STATUS = (
    "V56_CHANGED_TWO_SITE_SO10xSO10_ARCHITECTURE__CONNECTED_PATH_SELECTOR_ONLY__"
    "DESIRED_h_B_H2_ALLOWED__h_A_H2_AND_L_h_H2_FORBIDDEN__"
    "BUT_FACTORIZED_DEGREE6_ADJOINT_LINK_INVARIANT_REOPENS_DIRECT_MASS__"
    "MINIMAL_LEFT_POLE165x_AND_R1_TRANSPLANT_POLE16x__NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != expected or canonical_sha(value) != expected:
        raise ArithmeticError(f"stale upstream: {path.name}")
    return value


def exact_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0]) if work else 0):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                factor = work[row][column]
                work[row] = [left - factor * right for left, right in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def field_ledger() -> dict[str, Any]:
    return {
        "gauge_group": "Spin(10)_L x Spin(10)_R",
        "fields": {
            "H1_L": {"representation": ["10", "1"], "Z2_link": "even"},
            "barh_L": {"representation": ["10", "1"], "Z2_link": "even"},
            "h_L": {"representation": ["10", "1"], "Z2_link": "even"},
            "H2_R": {"representation": ["1", "10"], "Z2_link": "even"},
            "B_LR_missing": {"representation": ["10", "10"], "Z2_link": "even"},
            "Omega_LR": {"representation": ["10", "10"], "Z2_link": "odd"},
            "Omegabar_LR": {"representation": ["10", "10"], "Z2_link": "odd"},
            "A_L": {"representation": ["45", "1"], "Z2_link": "even"},
            "P_S_T_L_and_link_drivers": {"representation": ["1", "1"], "Z2_link": "even"},
        },
        "vacuum_targets": {
            "Omega": "v I_10",
            "Omegabar": "v I_10",
            "B": "b diag(epsilon,epsilon,epsilon,0_2,0_2), the diagonal-Spin10 45 component",
        },
        "diagonal_decomposition_of_B": "(10,10) -> 1 + 45 + 54 after identity-link breaking",
        "matter_parity": "independent exact Z2_M may keep all three matter 16s odd and every displayed filter/link field even",
    }


def operator_ledger() -> dict[str, Any]:
    rows = [
        {"operator": "P H1_L barh_L", "gauge_invariant": True, "Z2_even": True, "required": True},
        {"operator": "S barh_L h_L", "gauge_invariant": True, "Z2_even": True, "required": True},
        {"operator": "h_L B_LR H2_R", "gauge_invariant": True, "Z2_even": True, "required": True},
        {"operator": "T H2_R H2_R", "gauge_invariant": True, "Z2_even": True, "required": True},
        {"operator": "h_L A_L H2_R", "gauge_invariant": False, "Z2_even": True, "required": False},
        {"operator": "L h_L H2_R", "gauge_invariant": False, "Z2_even": True, "required": False},
        {"operator": "h_L Omega_LR H2_R", "gauge_invariant": True, "Z2_even": False, "required": False},
        {"operator": "L h_L Omega_LR H2_R", "gauge_invariant": True, "Z2_even": False, "required": False},
        {"operator": "h_L A_L Omega_LR H2_R", "gauge_invariant": True, "Z2_even": False, "required": False},
        {"operator": "h_L A_L B_LR H2_R", "gauge_invariant": True, "Z2_even": True, "required": False},
    ]
    return {
        "minimal_filter_superpotential": (
            "lambdaP P H1_L.barh_L + mh S barh_L.h_L + lambdaB h_L^T B_LR H2_R + "
            "m2 T H2_R.H2_R/2"
        ),
        "identity_link_driver": (
            "Tr[X_L (Omega Omegabar^T-v^2 I_10)], with X_L in 1+45+54; "
            "Omega=Omegabar=v I_10 and X_L=0 is an exact local F-flat target"
        ),
        "rows": rows,
        "all_required_allowed": all(row["gauge_invariant"] and row["Z2_even"] for row in rows if row["required"]),
        "named_fatal_fillers_forbidden": all(
            not (row["gauge_invariant"] and row["Z2_even"])
            for row in rows if row["operator"] in {"h_L A_L H2_R", "L h_L H2_R", "h_L Omega_LR H2_R"}
        ),
    }


def path_census(maximum_link_length: int = 9) -> dict[str, Any]:
    rows = []
    counterexample = []
    for length in range(1, maximum_link_length + 1, 2):
        words = []
        for word in itertools.product(("Omega_odd", "B_even"), repeat=length):
            omega_count = word.count("Omega_odd")
            b_count = word.count("B_even")
            allowed = omega_count % 2 == 0
            item = {
                "word": list(word),
                "Omega_count": omega_count,
                "B_count": b_count,
                "Z2_allowed": allowed,
                "contains_missing_VEV_B": b_count > 0,
            }
            words.append(item)
            if allowed and b_count == 0:
                counterexample.append(item)
        rows.append({
            "link_length": length,
            "all_words": 2**length,
            "Z2_allowed_words": sum(item["Z2_allowed"] for item in words),
            "allowed_words_containing_B": sum(item["Z2_allowed"] and item["contains_missing_VEV_B"] for item in words),
            "word_rows_sha256": hashlib.sha256(canonical_bytes(words)).hexdigest(),
        })
    return {
        "maximum_link_length_enumerated": maximum_link_length,
        "rows": rows,
        "counterexamples": counterexample,
        "bounded_result": "every allowed connected left-right link word contains B",
        "connected_path_all_order_proof": (
            "Spin10 center/vector-index parity at either site requires 1+Nlink to be even, so a left vector "
            "and a right vector require an odd number Nlink of bifundamental tensors, including epsilon contractions. "
            "Z2 invariance requires an even number NOmega of odd identity links. Therefore "
            "NB=Nlink-NOmega is odd, so every allowed connected path contains at least one even missing-VEV B link."
        ),
        "Spin10_center_check": (
            "10 has Z4-center class 2, while adjoints and singlets have class 0; center neutrality of the "
            "left operator gives 2(1+Nlink)=0 mod4 and hence odd Nlink, with the same equation on the right"
        ),
        "connected_adjoint_and_singlet_insertions": (
            "site adjoints and singlets inserted on the same connected endpoint path are Z2-even and do not "
            "change link-count or parity; at the declared block-diagonal adjoint vacuum, a B factor on that path "
            "annihilates the weak subspace"
        ),
        "spontaneous_Z2_breaking_scope": (
            "Omega VEVs break Z2, but the UV polynomial contains only Z2-even operators; with no other odd VEV "
            "species, substituting identity-link VEVs cannot create a path that was absent from the UV action"
        ),
    }


def disconnected_and_epsilon_stress_test() -> dict[str, Any]:
    a_blocks = [1, 1, 1, 3, 3]
    b_blocks = [1, 1, 1, 0, 0]
    trace_ab = -2 * sum(left * right for left, right in zip(a_blocks, b_blocks))
    lower_degree = [
        {"total_degree": 3, "class": "one-link endpoint", "result": "h Omega H2 is Z2-odd; h B H2 is allowed but Bweak=0"},
        {"total_degree": 4, "class": "one-link endpoint plus one even adjoint/singlet", "result": "Omega path remains odd; B path still kills the block-diagonal weak subspace"},
        {"total_degree": 5, "class": "three-link connected path or endpoint times two-link scalar", "result": "connected allowed words contain B; the minimal disconnected scalar Tr(B Omega^T)=Tr(B0)=0"},
    ]
    counterexample = {
        "operator": "(h_L^T Omega H2_R) Tr(A_L B Omegabar^T)",
        "total_degree": 6,
        "gauge_invariant": True,
        "Omega_parity_count": 2,
        "B_count": 1,
        "Z2_even": True,
        "vacuum_reduction": "v_Omega^2 Tr(A0 B0) h_L.H2_R",
        "A0_blocks": a_blocks,
        "B0_blocks": b_blocks,
        "Tr_A0_B0": trace_ab,
        "vacuum_nonzero": trace_ab != 0,
        "effect": "direct cross-site h-H2 mass; generic weak rank16 and full filter rank40",
    }
    return {
        "factorized_invariant_audit": {
            "minimal_pure_link_candidate": "(h Omega H2) Tr(B Omegabar^T)",
            "minimal_pure_link_total_degree": 5,
            "minimal_pure_link_vacuum_value": 0,
            "reason": "Tr(B0)=0 for the antisymmetric missing VEV",
            "first_adjoint_dressed_counterexample": counterexample,
        },
        "site_adjoint_audit": {
            "connected_insertions": "safe at the declared block-diagonal vacuum because B remains on the endpoint path",
            "disconnected_insertions": "unsafe: Tr(A0 B0) is a nonzero odd-B scalar that compensates endpoint-link parity",
        },
        "lower_degree_classification": lower_degree,
        "first_explicit_vacuum_nonzero_counterexample": counterexample,
        "epsilon_determinant_audit": {
            "determinant_formula": "det(I_10+t B0)=(1+t^2)^3",
            "odd_B_coefficients_in_determinant": [0, 0, 0, 0, 0],
            "weak_cofactor_formula": "adj(I_10+t B0)|weak=(1+t^2)^3 I_4",
            "odd_B_coefficients_in_weak_cofactor": [0, 0, 0, 0, 0],
            "pure_link_conclusion": "pure-link epsilon determinant/cofactor odd-B terms vanish in the weak block; adjoint-dressed factorized traces evade this conclusion",
        },
        "corrected_theorem": "connected endpoint and pure-link epsilon paths are protected at the declared vacuum, but the full polynomial invariant ring is not protected once disconnected adjoint-link scalars are admitted",
    }


def filter_hessian() -> list[list[int]]:
    size = 40
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    identity = [[int(i == j) for j in range(10)] for i in range(10)]
    b0 = [[0 for _ in range(10)] for _ in range(10)]
    for left, right in ((0, 1), (2, 3), (4, 5)):
        b0[left][right] = 1
        b0[right][left] = -1

    def set_block(row_field: int, column_field: int, block: Sequence[Sequence[int]]) -> None:
        for row in range(10):
            for column in range(10):
                matrix[10 * row_field + row][10 * column_field + column] = block[row][column]

    set_block(0, 1, identity)
    set_block(1, 0, identity)
    set_block(1, 2, [[2 * value for value in row] for row in identity])
    set_block(2, 1, [[2 * value for value in row] for row in identity])
    set_block(2, 3, b0)
    set_block(3, 2, [list(row) for row in zip(*b0)])
    set_block(3, 3, [[3 * value for value in row] for row in identity])
    return matrix


def with_direct_filler(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    result = [list(row) for row in matrix]
    for internal in range(10):
        result[20 + internal][30 + internal] += 1
        result[30 + internal][20 + internal] += 1
    return result


def filter_rank_audit() -> dict[str, Any]:
    matrix = filter_hessian()
    filled = with_direct_filler(matrix)
    color_indices = [10 * field + internal for field in range(4) for internal in range(6)]
    weak_indices = [10 * field + internal for field in range(4) for internal in range(6, 10)]

    def restrict(source: Sequence[Sequence[int]], indices: Sequence[int]) -> list[list[int]]:
        return [[source[row][column] for column in indices] for row in indices]

    color = restrict(matrix, color_indices)
    weak = restrict(matrix, weak_indices)
    filled_weak = restrict(filled, weak_indices)
    return {
        "ordering": ["H1_L(10)", "barh_L(10)", "h_L(10)", "H2_R(10)"],
        "matrix_sha256": hashlib.sha256(canonical_bytes(matrix)).hexdigest(),
        "full_rank_QQ": exact_rank(matrix),
        "full_nullity": 40 - exact_rank(matrix),
        "color_rank_QQ": exact_rank(color),
        "color_nullity": 24 - exact_rank(color),
        "weak_rank_QQ": exact_rank(weak),
        "weak_nullity": 16 - exact_rank(weak),
        "control_direct_hH2_filler_weak_rank_QQ": exact_rank(filled_weak),
        "control_direct_hH2_filler_full_rank_QQ": exact_rank(filled),
        "rank_conditions": "nonzero P,S,T,lambdaP,mh,lambdaB,m2 and nonzero color blocks of B",
        "coefficient_equality_required": False,
    }


def anomaly_and_cost() -> dict[str, Any]:
    import math

    coupling = 0.73
    def pole(beta: int) -> float:
        return math.exp(8 * math.pi**2 / (beta * coupling**2))

    minimal_left_t = 30 + 20 + 3
    minimal_right_t = 30 + 1
    source_transplant_t = 12 + 8 + 2 + 2
    family_t = 3 * 2
    return {
        "Z2_link_mixed_anomaly": {
            "odd_fields": ["Omega(10,10)", "Omegabar(10,10)"],
            "Spin10L_index_sum_in_T10_equals1_convention": 20,
            "Spin10R_index_sum_in_T10_equals1_convention": 20,
            "odd_Weyl_component_count": 200,
            "all_even_mod2": True,
        },
        "representation_cost": {
            "each_bifundamental_coordinates": 100,
            "minimum_bifundamentals": 3,
            "new_bifundamental_coordinates": 300,
            "per_site_Dynkin_index_from_three_bifundamentals": 30,
            "warning": "already large before a complete source, matter allocation, link drivers, thresholds, or two-loop running",
        },
        "one_loop_per_site_running": {
            "convention": "T10=1,T16=2,T45=8,T54=12,C2(Spin10)=8; b=sumT-24; g=0.73",
            "minimal_three_link_plus_XL_driver_filter": {
                "left_sumT": minimal_left_t,
                "left_b": minimal_left_t - 24,
                "left_pole_ratio": pole(minimal_left_t - 24),
                "right_sumT": minimal_right_t,
                "right_b": minimal_right_t - 24,
                "right_pole_ratio": pole(minimal_right_t - 24),
                "inventory": "three bifundamentals contribute30 per site; X_L=(1+45+54) contributes20 left; three left 10s and one right 10",
            },
            "R1_source_transplant_without_families": {
                "left_sumT": minimal_left_t + source_transplant_t,
                "left_b": minimal_left_t + source_transplant_t - 24,
                "left_pole_ratio": pole(minimal_left_t + source_transplant_t - 24),
                "right_sumT": minimal_right_t,
                "right_b": minimal_right_t - 24,
                "right_pole_ratio": pole(minimal_right_t - 24),
                "qualification": "field-inventory lower bound only; original one-site source couplings involving B are not product-gauge invariant",
            },
            "R1_source_plus_three_left_families": {
                "left_sumT": minimal_left_t + source_transplant_t + family_t,
                "left_b": minimal_left_t + source_transplant_t + family_t - 24,
                "left_pole_ratio": pole(minimal_left_t + source_transplant_t + family_t - 24),
                "right_sumT": minimal_right_t,
                "right_b": minimal_right_t - 24,
                "right_pole_ratio": pole(minimal_right_t - 24),
                "qualification": "field-inventory lower bound only, not a constructed source action",
            },
            "scope": "minimum declared ledgers only; B-alignment drivers and unwanted-component masses can only add charged index",
        },
        "diagonal_low_energy_content": "each (10,10) contains 1+45+54 under diagonal Spin10; unwanted components need masses",
    }


def build_report() -> dict[str, Any]:
    v55 = load_bound(V55_PATH, EXPECTED_V55_CORE)
    r1 = load_bound(V54_R1_PATH, EXPECTED_V54_R1_CORE)
    fields = field_ledger()
    operators = operator_ledger()
    paths = path_census()
    stress = disconnected_and_epsilon_stress_test()
    ranks = filter_rank_audit()
    cost = anomaly_and_cost()
    checks = {
        "V55_fatal_filler_input_bound": v55["core_sha256"] == EXPECTED_V55_CORE,
        "V54_R1_input_bound": r1["core_sha256"] == EXPECTED_V54_R1_CORE,
        "desired_filter_chain_is_allowed": operators["all_required_allowed"],
        "named_hA_H2_LhH2_and_identity_link_fillers_forbidden": operators["named_fatal_fillers_forbidden"],
        "bounded_path_census_has_no_counterexample": not paths["counterexamples"],
        "each_bounded_allowed_path_contains_B": all(
            row["Z2_allowed_words"] == row["allowed_words_containing_B"] for row in paths["rows"]
        ),
        "connected_path_parity_proof_recorded": "NB=Nlink-NOmega is odd" in paths["connected_path_all_order_proof"],
        "Spin10_center_forces_odd_link_count": "2(1+Nlink)=0 mod4" in paths["Spin10_center_check"],
        "factorized_degree6_counterexample_is_exact_and_nonzero": (
            stress["first_explicit_vacuum_nonzero_counterexample"]["Tr_A0_B0"] == -6
            and stress["first_explicit_vacuum_nonzero_counterexample"]["vacuum_nonzero"]
        ),
        "pure_link_epsilon_odd_coefficients_vanish": (
            stress["epsilon_determinant_audit"]["odd_B_coefficients_in_determinant"] == [0] * 5
            and stress["epsilon_determinant_audit"]["odd_B_coefficients_in_weak_cofactor"] == [0] * 5
        ),
        "filter_has_rank36_nullity4": ranks["full_rank_QQ"] == 36 and ranks["full_nullity"] == 4,
        "color_block_is_full_rank24": ranks["color_rank_QQ"] == 24 and ranks["color_nullity"] == 0,
        "weak_block_has_rank12_nullity4": ranks["weak_rank_QQ"] == 12 and ranks["weak_nullity"] == 4,
        "forbidden_direct_filler_would_raise_rank40": (
            ranks["control_direct_hH2_filler_weak_rank_QQ"] == 16
            and ranks["control_direct_hH2_filler_full_rank_QQ"] == 40
        ),
        "Z2_link_anomaly_counts_even": cost["Z2_link_mixed_anomaly"]["all_even_mod2"],
        "minimal_left_one_loop_b29_pole_between100_and1000": (
            cost["one_loop_per_site_running"]["minimal_three_link_plus_XL_driver_filter"]["left_b"] == 29
            and 100 < cost["one_loop_per_site_running"]["minimal_three_link_plus_XL_driver_filter"]["left_pole_ratio"] < 1000
        ),
        "R1_source_transplant_left_b53_pole_below100": (
            cost["one_loop_per_site_running"]["R1_source_transplant_without_families"]["left_b"] == 53
            and cost["one_loop_per_site_running"]["R1_source_transplant_without_families"]["left_pole_ratio"] < 100
        ),
        "changed_representation_architecture_explicit": fields["gauge_group"] == "Spin(10)_L x Spin(10)_R",
        "complete_source_and_alignment_not_claimed": True,
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v56_two_site_link_parity_selector_audit_v1",
        "status": STATUS if not failures else "V56_TWO_SITE_LINK_PARITY_SELECTOR_AUDIT_FAILED",
        "source_manifest": {V55_PATH.name: EXPECTED_V55_CORE, V54_R1_PATH.name: EXPECTED_V54_R1_CORE},
        "cross_action_rule": (
            "B is changed from a one-site 45 to a (10,10) bifundamental and the gauge group is doubled; "
            "no V54/V55 Hessian or anomaly closure is inherited"
        ),
        "field_and_vacuum_ledger": fields,
        "minimal_action_and_operator_checks": operators,
        "exact_link_path_selector": paths,
        "factorized_epsilon_and_adjoint_stress_test": stress,
        "exact_filter_mass_rank": ranks,
        "finite_selector_anomaly_and_representation_cost": cost,
        "unresolved_same_action_obligations": [
            "construct an elementary renormalizable potential that aligns B solely in its diagonal-45 missing-VEV component",
            "compute the complete source+three-link+driver F/D vacuum and Hessian modulo all 90 product-group generators",
            "mass the unwanted diagonal 1 and 54 components of every bifundamental without opening a parity-allowed weak path",
            "place three matter families and prove proton/flavour operators and all discrete/continuous anomalies in this same action",
            "compute doubled-gauge thresholds, perturbativity, Wilson coefficients, SUSY breaking and cosmology",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gate_effect": {
            "filter_selector_mechanism": "CONNECTED_PATH_ONLY__FULL_INVARIANT_RING_FAILED_AT_DEGREE6",
            "complete_two_site_action": "OPEN",
            "same_action_G2": "OPEN",
            "G1_through_G8_promotions": [],
            "candidate_gate_promotions": 0,
        },
        "primary_source": "https://arxiv.org/abs/hep-th/0104005",
        "verdict": (
            "Two-site locality plus Z2 link parity allows h B H2 and forbids the named elementary fillers, and it "
            "protects every connected endpoint path. It is not a selector for the full invariant ring. The degree-six "
            "factorized invariant (h Omega H2) Tr(A B Omegabar^T) is allowed and nonzero because Tr(A0 B0)=-6; it "
            "restores the direct weak mass and rank40. Pure-link determinant/cofactor contractions pass, but adjoint "
            "factorization kills the design. Minimal running is also poor. No gate is promoted."
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    ranks = report["exact_filter_mass_rank"]
    paths = report["exact_link_path_selector"]
    stress = report["factorized_epsilon_and_adjoint_stress_test"]
    cost = report["finite_selector_anomaly_and_representation_cost"]
    return "\n".join([
        "# SUSY V56 two-site link-parity selector audit", "",
        f"Status: `{report['status']}`", "",
        f"Core SHA-256: `{report['core_sha256']}`", "",
        "## Result", "", report["verdict"], "",
        "## Minimal changed action", "",
        "Use `Spin(10)_L x Spin(10)_R`. Place `H1,barh,h` on the left site and `H2` on the right.",
        "An even `(10,10)` link `B` supplies the missing VEV, while odd links `Omega,Omegabar` acquire",
        "identity VEVs. The allowed filter is", "",
        "`P H1 barh + S barh h + h B H2 + (T/2) H2^2`.", "",
        "The direct `h A H2` and `L h H2` expressions are not product-gauge invariants. Their identity-link",
        "completions contain one odd `Omega` and are Z2-forbidden. The desired `h B H2` term is allowed.", "",
        "## Corrected selector scope", "",
        paths["connected_path_all_order_proof"], "",
        f"The explicit word census checks every odd link length through `{paths['maximum_link_length_enumerated']}`",
        "and finds no connected-path counterexample.", "",
        "The full invariant ring nevertheless fails at degree six:", "",
        f"`{stress['first_explicit_vacuum_nonzero_counterexample']['operator']}`.", "",
        f"It is gauge invariant and Z2-even, and `Tr(A0 B0)={stress['first_explicit_vacuum_nonzero_counterexample']['Tr_A0_B0']}`.",
        "It therefore becomes a direct `h H2` mass. Pure-link determinant and cofactor contractions have only",
        "even B coefficients in the weak block, but the disconnected adjoint trace evades that protection.", "",
        "## Filter ranks", "",
        f"The exact 40-coordinate filter matrix has rank `{ranks['full_rank_QQ']}` and nullity",
        f"`{ranks['full_nullity']}`. Color rank is `{ranks['color_rank_QQ']}` with no kernel; weak rank is",
        f"`{ranks['weak_rank_QQ']}` with nullity `{ranks['weak_nullity']}`. Adding the forbidden direct",
        f"`h H2` control raises the full rank to `{ranks['control_direct_hH2_filler_full_rank_QQ']}`.", "",
        "## Running and fail-closed boundary", "",
        f"The minimum filter/link ledger has per-site `b_L={cost['one_loop_per_site_running']['minimal_three_link_plus_XL_driver_filter']['left_b']}`",
        f"and `b_R={cost['one_loop_per_site_running']['minimal_three_link_plus_XL_driver_filter']['right_b']}`; the left pole is only",
        f"`{cost['one_loop_per_site_running']['minimal_three_link_plus_XL_driver_filter']['left_pole_ratio']:.3f}` times matching.",
        f"Transplanting the R1 source raises the left beta coefficient to `{cost['one_loop_per_site_running']['R1_source_transplant_without_families']['left_b']}`",
        f"and lowers its pole ratio to `{cost['one_loop_per_site_running']['R1_source_transplant_without_families']['left_pole_ratio']:.3f}`.", "",
        f"The three required bifundamentals already add `{cost['representation_cost']['new_bifundamental_coordinates']}`",
        "chiral coordinates and index 30 to each site before the source and drivers are completed. The missing-VEV",
        "alignment of the bifundamental, unwanted diagonal `1+54` components, full product-group Hessian, matter",
        "operators, thresholds and perturbativity are open. No result from the one-site R1 action is promoted.", "",
        "The theory-space mechanism is motivated by the four-dimensional moose construction of",
        "[Arkani-Hamed, Cohen and Georgi](https://arxiv.org/abs/hep-th/0104005).", "",
    ])


def validate_report(report: Mapping[str, Any]) -> None:
    if report["n_failed"] or report["failures"]:
        raise ArithmeticError(report["failures"])
    if canonical_sha(report) != report["core_sha256"]:
        raise ArithmeticError("core hash mismatch")
    if report["gate_effect"]["candidate_gate_promotions"] != 0:
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
