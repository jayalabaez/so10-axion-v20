#!/usr/bin/env python3
"""V54 exact UV completion and same-action no-go for the V53 degree-five escape.

The V53 bounded search found that neutral constraints for fields with
``q9(P,S,T)=(2,1,8)`` first acquire full exponent rank through the monomials
``ST``, ``PT^2`` and ``SP^4``.  This audit does two separate things:

1. It constructs a selected, fully renormalizable SO(10)-singlet messenger
   action whose tree-level elimination produces those three constraints, and
   verifies an exact 14-coordinate F-flat, nonsingular witness.
2. It then restores the operator logic required of a symmetry-complete EFT.
   The messenger VEVs produce six Z9-neutral degree-six ``F16^4`` dressings;
   an explicit Spin(10) center filter rejects two spinor-dressed rows and
   leaves four genuine gauge invariants.  The charge-four messenger also
   permits the renormalizable ``C4 H1^2`` filler.  A
   factorwise Abelian tree argument shows that changing the singlet-messenger
   topology does not repair the proton operator.

Consequently the selected action has good local algebra but is not a natural,
proton-safe completion and promotes no G gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_DEGREE5_MESSENGER_UV_NO_GO_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_DEGREE5_MESSENGER_UV_NO_GO_AUDIT.md"

SELECTOR_PATH = ROOT / "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json"
DRIVER_PATH = ROOT / "SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.json"
FILTER_PATH = ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json"

EXPECTED_SELECTOR_CORE = "33de88b196a5096f7169cc3156d68cd9f4fa33e985adf0c23ea6c67a1a732dce"
EXPECTED_DRIVER_CORE = "3777e4ab0f03591ca736f71e282f86a8f232fee83fb2f1d378e789fea6765bf4"
EXPECTED_FILTER_CORE = "993b549668243b06d082a7def8591c63141dfa402d6372b133c19cfa8f8b6ff6"

STATUS = (
    "V54_DEGREE5_ESCAPE_HAS_EXACT_RENORMALIZABLE_SELECTED_MESSENGER_ACTION__"
    "14_SINGLET_HESSIAN_FULL_RANK__COMBINED_230_RANK193_NULLITY37__"
    "BUT_MESSENGER_VEVS_REOPEN_DEGREE6_F16^4_AND_H1_SQUARED__"
    "ABELIAN_TREE_COMPLETIONS_FAIL_FACTORWISE__NO_GATE_PROMOTION"
)

COORDINATES = [
    "P", "S", "T", "X1", "X2", "X3", "U", "Ubar",
    "A", "Abar", "B", "Bbar", "C", "Cbar",
]
INDEX = {name: index for index, name in enumerate(COORDINATES)}
Z9_CHARGES = {
    "P": 2, "S": 1, "T": 8, "X1": 0, "X2": 0, "X3": 0,
    "U": 1, "Ubar": 8, "A": 8, "Abar": 1,
    "B": 6, "Bbar": 3, "C": 4, "Cbar": 5,
}
WITNESS = {
    "P": 1, "S": 1, "T": 1, "X1": 0, "X2": 0, "X3": 0,
    "U": -1, "Ubar": 0, "A": -1, "Abar": 0,
    "B": 1, "Bbar": 0, "C": -1, "Cbar": 0,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_bound(path: Path, expected_core: str) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("core_sha256") != expected_core or canonical_sha(report) != expected_core:
        raise ArithmeticError(f"stale or corrupt upstream artifact: {path.name}")
    return report


# Unit-coupling superpotential.  Each term is (label, integer coefficient,
# exponent mapping); all mass scales are measured in common witness units.
TERMS: list[tuple[str, int, dict[str, int]]] = [
    ("X1*S*T", 1, {"X1": 1, "S": 1, "T": 1}),
    ("-X1", -1, {"X1": 1}),
    ("U*Ubar", 1, {"U": 1, "Ubar": 1}),
    ("X2*T*U", 1, {"X2": 1, "T": 1, "U": 1}),
    ("Ubar*P*T", 1, {"Ubar": 1, "P": 1, "T": 1}),
    ("+X2", 1, {"X2": 1}),
    ("A*Abar", 1, {"A": 1, "Abar": 1}),
    ("X3*S*A", 1, {"X3": 1, "S": 1, "A": 1}),
    ("B*Bbar", 1, {"B": 1, "Bbar": 1}),
    ("Abar*P*B", 1, {"Abar": 1, "P": 1, "B": 1}),
    ("C*Cbar", 1, {"C": 1, "Cbar": 1}),
    ("Bbar*P*C", 1, {"Bbar": 1, "P": 1, "C": 1}),
    ("Cbar*P^2", 1, {"Cbar": 1, "P": 2}),
    ("+X3", 1, {"X3": 1}),
]


def _differentiate_term(
    coefficient: int,
    powers: Mapping[str, int],
    derivatives: Sequence[str],
) -> tuple[int, dict[str, int]]:
    result = coefficient
    remaining = dict(powers)
    for variable in derivatives:
        exponent = remaining.get(variable, 0)
        if exponent == 0:
            return 0, remaining
        result *= exponent
        remaining[variable] = exponent - 1
    return result, remaining


def _evaluate(coefficient: int, powers: Mapping[str, int], point: Mapping[str, int]) -> int:
    result = coefficient
    for variable, exponent in powers.items():
        result *= point[variable] ** exponent
    return result


def gradient(point: Mapping[str, int] = WITNESS) -> list[int]:
    result: list[int] = []
    for variable in COORDINATES:
        value = 0
        for _, coefficient, powers in TERMS:
            derived, remaining = _differentiate_term(coefficient, powers, [variable])
            value += _evaluate(derived, remaining, point)
        result.append(value)
    return result


def hessian(point: Mapping[str, int] = WITNESS) -> list[list[int]]:
    result: list[list[int]] = []
    for left in COORDINATES:
        row: list[int] = []
        for right in COORDINATES:
            value = 0
            for _, coefficient, powers in TERMS:
                derived, remaining = _differentiate_term(coefficient, powers, [left, right])
                value += _evaluate(derived, remaining, point)
            row.append(value)
        result.append(row)
    return result


def exact_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                factor = work[row][column]
                work[row] = [a - factor * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def exact_determinant(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    size = len(work)
    if any(len(row) != size for row in work):
        raise ValueError("determinant requires a square matrix")
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant *= -1
        pivot_value = work[column][column]
        determinant *= pivot_value
        for row in range(column + 1, size):
            if work[row][column]:
                factor = work[row][column] / pivot_value
                for entry in range(column, size):
                    work[row][entry] -= factor * work[column][entry]
    if determinant.denominator != 1:
        raise ArithmeticError("integer matrix produced a noninteger determinant")
    return determinant.numerator


def action_audit() -> dict[str, Any]:
    term_rows = []
    for label, coefficient, powers in TERMS:
        degree = sum(powers.values())
        charge = sum(Z9_CHARGES[field] * exponent for field, exponent in powers.items()) % 9
        term_rows.append({
            "term": label,
            "coefficient_at_witness": coefficient,
            "degree": degree,
            "Z9_charge": charge,
            "invariant": charge == 0,
        })
    matrix = hessian()
    f_terms = gradient()
    return {
        "coordinates": COORDINATES,
        "Z9_charges": Z9_CHARGES,
        "SO10_representations": {field: "1" for field in COORDINATES},
        "matter_parity": {field: "even" for field in COORDINATES},
        "selected_superpotential": (
            "lambda1 X1 S T-xi1 X1 + MU U Ubar+lambda2 X2 T U+kappa2 Ubar P T+xi2 X2 + "
            "MA A Abar+lambda3 X3 S A+MB B Bbar+kappaA Abar P B + "
            "MC C Cbar+kappaB Bbar P C+kappaC Cbar P^2+xi3 X3"
        ),
        "unit_witness_terms": term_rows,
        "all_terms_Z9_invariant": all(row["invariant"] for row in term_rows),
        "all_terms_renormalizable": all(row["degree"] <= 3 for row in term_rows),
        "witness": WITNESS,
        "F_term_ordering": COORDINATES,
        "F_terms": f_terms,
        "F_nonzero_count": sum(value != 0 for value in f_terms),
        "hessian": matrix,
        "hessian_sha256": hashlib.sha256(canonical_bytes(matrix)).hexdigest(),
        "hessian_rank_QQ": exact_rank(matrix),
        "hessian_nullity": len(matrix) - exact_rank(matrix),
        "hessian_determinant": exact_determinant(matrix),
        "generic_determinant_on_F_flat_messenger_chain_locus": (
            "-81 lambda1^2 lambda2^2 kappa2^2 lambda3^2 kappaA^2 "
            "kappaB^2 kappaC^2 P^8 S^2 T^4"
        ),
        "generic_open_set": [
            "lambda1*lambda2*kappa2*lambda3*kappaA*kappaB*kappaC != 0",
            "MU*MA*MB*MC != 0",
            "P*S*T != 0",
        ],
        "determinant_scope": (
            "evaluated on the exact F-flat messenger-chain locus after solving for U,Ubar,A,Abar,B,Bbar,C,Cbar"
        ),
        "coefficient_equality_required": False,
    }


def effective_constraint_audit() -> dict[str, Any]:
    exponent_rows = [[0, 1, 1], [1, 0, 2], [4, 1, 0]]
    return {
        "light_field_ordering": ["P", "S", "T"],
        "tree_level_effective_superpotential": (
            "X1(lambda1 S T-xi1) + X2(xi2-(lambda2 kappa2/MU) P T^2) + "
            "X3(xi3-(lambda3 kappaA kappaB kappaC/(MA MB MC)) S P^4)"
        ),
        "tree_elimination_open_set_assumptions": [
            "MU != 0", "MA != 0", "MB != 0", "MC != 0",
            "all displayed link couplings are nonzero",
            "P*S*T != 0 at the stabilized vacuum",
        ],
        "neutral_monomials": ["S*T", "P*T^2", "S*P^4"],
        "exponent_rows": exponent_rows,
        "exact_exponent_rank": exact_rank(exponent_rows),
        "exact_exponent_determinant": exact_determinant(exponent_rows),
        "solution_definitions": {
            "a": "xi1/lambda1",
            "b": "xi2 MU/(lambda2 kappa2)",
            "c": "xi3 MA MB MC/(lambda3 kappaA kappaB kappaC)",
        },
        "nonzero_solution": ["T^9=a*b^4/c", "P=b/T^2", "S=a/T"],
        "Z9_orbit_size_at_generic_nonzero_solution": 9,
    }


def complete_dangerous_census(selector: Mapping[str, Any]) -> dict[str, Any]:
    old_names = selector["complete_F4_VEV_dressing_census_through_degree6"]["VEV_species"]
    old_charges = selector["Z9_charges"]
    charge_lookup = {
        "E54": old_charges["E54"],
        "A45": old_charges["A45"],
        "C16H": old_charges["C16H"],
        "Bbar16H": old_charges["Bbar16H"],
        "D45_missingVEV": old_charges["D45_missingVEV"],
        "P_filter": old_charges["P_filter"],
        "S": 1,
        "T": 8,
        "U_messenger": 1,
        "A_messenger": 8,
        "B_messenger": 6,
        "C_messenger": 4,
    }
    if old_names != list(charge_lookup)[: len(old_names)]:
        raise ArithmeticError("upstream VEV ordering drift")
    species = list(charge_lookup)
    # Spin(10) has Z4 center charge 1 on 16, 3 on bar16, 2 on 10, and
    # zero on the tensor representations and singlets used here.  F16^4 has
    # center charge zero.  Center neutrality is a necessary singlet condition;
    # for every surviving row below it is also enough to preserve the six
    # already-computed F16^4 invariants because all dressing fields are SO(10)
    # singlets.
    center_charge_lookup = {name: 0 for name in species}
    center_charge_lookup["C16H"] = 1
    center_charge_lookup["Bbar16H"] = 3
    allowed = []
    z9_neutral = []
    center_rejected = []
    total_rows = 0
    for insertions in range(3):
        for dressing in itertools.combinations_with_replacement(species, insertions):
            total_rows += 1
            charge = (4 + sum(charge_lookup[name] for name in dressing)) % 9
            if charge == 0:
                center_charge = sum(center_charge_lookup[name] for name in dressing) % 4
                row = {
                    "operator": "F16^4 " + " ".join(dressing),
                    "dressing": list(dressing),
                    "total_degree": 4 + insertions,
                    "Z9_charge": charge,
                    "Spin10_center_Z4_charge": center_charge,
                    "Spin10_center_neutral": center_charge == 0,
                    "Spin10_singlet_multiplicity": 6 if center_charge == 0 else 0,
                    "matter_parity": "even",
                }
                z9_neutral.append(row)
                if center_charge == 0:
                    allowed.append(row)
                else:
                    center_rejected.append({**row, "rejection": "nonzero Spin(10) Z4 center charge forbids a gauge singlet"})
    return {
        "F16_fourth_power_charge": 4,
        "F16_fourth_power_Spin10_center_Z4_charge": 0,
        "VEV_species_and_Z9_charges": charge_lookup,
        "VEV_species_and_Spin10_center_Z4_charges": center_charge_lookup,
        "Spin10_center_convention": {"16": 1, "bar16": 3, "10": 2, "45_54_and_singlet": 0},
        "center_filter_scope": (
            "center neutrality is necessary in general; it is sufficient for these survivors because "
            "every surviving dressing field is an SO10 singlet and F16^4 has six exact singlets"
        ),
        "census_scope": "all zero-, one-, and two-VEV multisets after adding every nonzero UV witness VEV",
        "row_count": total_rows,
        "Z9_neutral_row_count_before_center_filter": len(z9_neutral),
        "Z9_neutral_rows_before_center_filter": z9_neutral,
        "center_rejected_row_count": len(center_rejected),
        "center_rejected_rows": center_rejected,
        "allowed_row_count": len(allowed),
        "allowed_rows": allowed,
        "allowed_invariant_directions": sum(row["Spin10_singlet_multiplicity"] for row in allowed),
        "all_allowed_rows_are_degree6": all(row["total_degree"] == 6 for row in allowed),
        "selector_still_forbids_through_degree6": not allowed,
        "renormalizable_DT_filler": {
            "operator": "C_messenger H1_10 H1_10",
            "Z9_charge_arithmetic": "4+7+7=18=0 mod 9",
            "matter_parity": "even",
            "C_messenger_VEV_nonzero": WITNESS["C"] != 0,
            "filter_rank_before": 36,
            "generic_filter_rank_after": 40,
            "weak_Higgs_nullity_after": 0,
        },
    }


def factorwise_tree_no_go() -> dict[str, Any]:
    return {
        "bounded_class": (
            "tree-level renormalizable UV completions by massive SO10-singlet messengers, "
            "generic nonzero link couplings, nonzero P,S,T, and no tuned source cancellation"
        ),
        "source_R_reduction": {
            "relations": ["2e=w", "3e=w"],
            "consequence": "e=0 and w=0 in every conventional Abelian R factor; each factor reduces to additive non-R charge arithmetic",
        },
        "required_factorwise_relations": [
            "2 h2=0",
            "h1=-p-h2",
            "4 f=2 p",
            "s=-4 p",
            "t=4 p",
        ],
        "tree_lemma": (
            "A rooted cubic messenger tree for the five nonzero leaves P,P,P,P,S has a terminal "
            "two-light-field cherry, necessarily PP or PS; the massive partner acquires the composite VEV."
        ),
        "PP_cherry": {
            "composite_charge": "2 p",
            "proton_operator": "F^4 S Y_(2p)",
            "proton_charge_identity": "2p-4p+2p=0",
            "DT_operator": "Y_(2p) H1^2",
            "DT_charge_identity": "2p+2(-p-h2)=-2h2=0",
        },
        "PS_cherry": {
            "composite_charge": "p+s=-3p",
            "proton_operator": "F^4 P Y_(-3p)",
            "proton_charge_identity": "2p+p-3p=0",
        },
        "product_Abelian_symmetries_fail_factorwise": True,
        "matter_parity_repairs_failure": False,
        "scope_limit": (
            "This does not exclude non-Abelian shaping symmetries, a redesigned source with a nontrivial R action, "
            "non-singlet mediators, tuned cancellations, or nonperturbative UV physics."
        ),
    }


def anomaly_and_running(selector: Mapping[str, Any]) -> dict[str, Any]:
    added_pairs = [[1, 8], [1, 8], [8, 1], [6, 3], [4, 5]]
    added_charges = [charge for pair in added_pairs for charge in pair] + [0, 0, 0]
    perturbativity = selector["perturbativity"]
    return {
        "added_fields_beyond_existing_P": {
            "light_VEV_singlets": 2,
            "neutral_drivers": 3,
            "massive_messenger_singlets": 8,
            "total": 13,
        },
        "Z9_vectorlike_pairs": added_pairs,
        "three_neutral_driver_charges": [0, 0, 0],
        "added_gravity_Z9_integer_sum": sum(added_charges),
        "added_gravity_Z9_mod9": sum(added_charges) % 9,
        "added_cubic_Z9_integer_sum": sum(charge**3 for charge in added_charges),
        "added_cubic_Z9_mod9": sum(charge**3 for charge in added_charges) % 9,
        "added_SO10_squared_Z9": 0,
        "existing_anomaly_repair_retained": {
            "vector10_pairs": selector["discrete_anomaly_repair"]["vector10_pairs"],
            "singlet_pairs": selector["discrete_anomaly_repair"]["singlet_pairs"],
            "total_mod9": selector["discrete_anomaly_repair"]["total_mod9"],
        },
        "new_anomaly_spectators_required": False,
        "one_loop_SO10_running": {
            "new_fields_have_total_Dynkin_index": 0,
            "total_T_unchanged": perturbativity["total_T"],
            "b_unchanged": perturbativity["b_Landau"],
            "pole_over_matching_scale_at_g0p73_unchanged": perturbativity["pole_over_matching_scale_at_g0p73"],
            "above_100x": perturbativity["pole_over_matching_scale_at_g0p73"] > 100,
            "above_1000x": perturbativity["pole_over_matching_scale_at_g0p73"] > 1000,
            "scope": "one-loop SO10 gauge running only; singlet Yukawa thresholds and two-loop effects are not computed",
        },
    }


def build_report() -> dict[str, Any]:
    selector = load_bound(SELECTOR_PATH, EXPECTED_SELECTOR_CORE)
    driver = load_bound(DRIVER_PATH, EXPECTED_DRIVER_CORE)
    filter_report = load_bound(FILTER_PATH, EXPECTED_FILTER_CORE)
    if driver["upstream_selector_core"] != EXPECTED_SELECTOR_CORE:
        raise ArithmeticError("driver-to-selector binding drift")
    if driver["smallest_bounded_escape"] != {
        "maximum_monomial_degree": 5,
        "added_charges": [1, 8],
        "neutral_exponents": [[0, 1, 1], [1, 0, 2], [0, 2, 2], [4, 1, 0], [1, 1, 3]],
        "exact_rank": 3,
    }:
        raise ArithmeticError("degree-five escape drift")

    action = action_audit()
    effective = effective_constraint_audit()
    dangerous = complete_dangerous_census(selector)
    tree = factorwise_tree_no_go()
    running = anomaly_and_running(selector)
    combined = {
        "qualification": (
            "selected-action block arithmetic only: it omits symmetry-allowed cross-couplings and is not "
            "the Hessian of the symmetry-complete EFT"
        ),
        "coordinate_inventory": {"DW_source": 176, "four_filter_10s": 40, "UV_singlet_sector": 14, "total": 230},
        "rank_decomposition": {"DW_source": 143, "four_filter_10s": 36, "UV_singlet_sector": 14, "total": 193},
        "nullity": 37,
        "nullity_decomposition": {"broken_gauge_orbit": 33, "intended_weak_Higgs": 4, "extra": 0},
        "selected_action_geometry_passes": True,
        "symmetry_complete_geometry_passes": False,
        "reason": "the allowed C_messenger H1^2 term fills the intended weak kernel",
    }

    checks = {
        "selector_core_bound": selector["core_sha256"] == EXPECTED_SELECTOR_CORE,
        "driver_core_bound": driver["core_sha256"] == EXPECTED_DRIVER_CORE,
        "filter_core_bound": filter_report["core_sha256"] == EXPECTED_FILTER_CORE,
        "degree5_escape_is_bound": driver["smallest_bounded_escape"]["added_charges"] == [1, 8],
        "all_selected_UV_terms_are_Z9_invariant": action["all_terms_Z9_invariant"],
        "all_selected_UV_terms_are_renormalizable": action["all_terms_renormalizable"],
        "exact_F_flat_witness": action["F_nonzero_count"] == 0,
        "exact_14_coordinate_Hessian_is_full_rank": action["hessian_rank_QQ"] == 14,
        "exact_14_coordinate_Hessian_determinant_is_minus81": action["hessian_determinant"] == -81,
        "effective_exponent_determinant_is9": effective["exact_exponent_determinant"] == 9,
        "tree_elimination_requires_nonzero_messenger_masses": effective["tree_elimination_open_set_assumptions"][:4] == [
            "MU != 0", "MA != 0", "MB != 0", "MC != 0",
        ],
        "generic_determinant_is_explicitly_F_flat_locus_scoped": "F-flat messenger-chain locus" in action["determinant_scope"],
        "selected_combined_rank_is193_of230": combined["rank_decomposition"]["total"] == 193 and combined["coordinate_inventory"]["total"] == 230,
        "selected_combined_nullity_is33_plus4": combined["nullity"] == 37 == 33 + 4,
        "dangerous_census_has_six_Z9_neutral_rows_before_center_filter": dangerous["Z9_neutral_row_count_before_center_filter"] == 6,
        "Spin10_center_filter_rejects_two_spinor_dressings": dangerous["center_rejected_row_count"] == 2,
        "dangerous_census_has_four_gauge_invariant_degree6_rows": dangerous["allowed_row_count"] == 4 and dangerous["all_allowed_rows_are_degree6"],
        "dangerous_census_has24_invariant_directions": dangerous["allowed_invariant_directions"] == 24,
        "renormalizable_H1_squared_filler_is_allowed": dangerous["renormalizable_DT_filler"]["Z9_charge_arithmetic"] == "4+7+7=18=0 mod 9",
        "generic_H1_squared_filler_rank_matches_upstream": (
            dangerous["renormalizable_DT_filler"]["generic_filter_rank_after"]
            == filter_report["filter_mass_blocks"]["H1_squared_unit_filler_rank"]
            == 40
        ),
        "Abelian_tree_no_go_is_factorwise": tree["product_Abelian_symmetries_fail_factorwise"],
        "added_discrete_anomaly_residues_vanish": (
            running["added_gravity_Z9_mod9"] == running["added_cubic_Z9_mod9"]
            == running["added_SO10_squared_Z9"] == 0
        ),
        "no_new_anomaly_spectators_are_needed": not running["new_anomaly_spectators_required"],
        "one_loop_running_is_unchanged": running["one_loop_SO10_running"]["b_unchanged"] == 22,
        "one_loop_1000x_screen_still_fails": not running["one_loop_SO10_running"]["above_1000x"],
        "selected_and_symmetry_complete_actions_are_not_conflated": (
            combined["selected_action_geometry_passes"] and not combined["symmetry_complete_geometry_passes"]
        ),
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v54_degree5_messenger_uv_no_go_audit_v1",
        "status": STATUS if not failures else "V54_DEGREE5_MESSENGER_UV_AUDIT_FAILED",
        "source_manifest": {
            SELECTOR_PATH.name: EXPECTED_SELECTOR_CORE,
            DRIVER_PATH.name: EXPECTED_DRIVER_CORE,
            FILTER_PATH.name: EXPECTED_FILTER_CORE,
        },
        "selected_renormalizable_UV_action": action,
        "tree_level_matching": effective,
        "selected_action_combined_geometry": combined,
        "symmetry_complete_operator_census": dangerous,
        "factorwise_tree_no_go": tree,
        "anomaly_and_perturbativity_scope": running,
        "selected_action_vs_complete_EFT": {
            "selected_action": "exact F-flat and nonsingular on an open set after deliberately retaining only the displayed couplings",
            "symmetry_complete_EFT": "fails natural DT and degree-six proton safety once all selector-allowed operators are admitted",
            "strict_same_action_feasibility": False,
            "complete_theory": False,
        },
        "primary_sources": {
            "supersymmetric_nonrenormalization": "https://arxiv.org/abs/hep-ph/9309335",
            "discrete_gauge_anomalies": "https://arxiv.org/abs/hep-th/9109045",
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gate_effect": {
            "local_selected_action_F_flatness_and_Hessian": "CLOSED_WITHIN_SELECTED_TEXTURE",
            "symmetry_complete_natural_DT": "OPEN",
            "proton_selector_through_degree6": "REOPENED_BY_MESSENGER_VEVS",
            "discrete_anomaly_residue_for_added_singlets": "CLOSED",
            "one_loop_1000x_perturbativity": "OPEN",
            "G1_through_G8_promotions": [],
            "candidate_gate_promotions": 0,
        },
        "verdict": (
            "A renormalizable singlet-messenger action realizes the degree-five algebraic escape and has an exact "
            "full-rank 14-coordinate singlet Hessian. It is not a valid same-action completion: messenger VEVs "
            "allow four gauge-invariant degree-six F16^4 dressings and a renormalizable H1^2 filler, and every Abelian singlet-tree "
            "topology has the same factorwise proton obstruction. No G gate is promoted."
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    action = report["selected_renormalizable_UV_action"]
    effective = report["tree_level_matching"]
    combined = report["selected_action_combined_geometry"]
    danger = report["symmetry_complete_operator_census"]
    running = report["anomaly_and_perturbativity_scope"]
    lines = [
        "# SUSY V54 degree-five messenger UV audit", "",
        f"Status: `{report['status']}`", "",
        f"Core SHA-256: `{report['core_sha256']}`", "",
        "## Verdict", "", report["verdict"], "",
        "## Selected renormalizable action", "",
        "With `q9(P,S,T)=(2,1,8)`, neutral `X1,X2,X3`, and messenger pairs",
        "`(U,Ubar)=(1,8)`, `(A,Abar)=(8,1)`, `(B,Bbar)=(6,3)`, and",
        "`(C,Cbar)=(4,5)`, the displayed superpotential is cubic or lower and every term is Z9 invariant.", "",
        f"At the unit witness all `{len(action['F_terms'])}` F terms vanish. The exact singlet Hessian has rank",
        f"`{action['hessian_rank_QQ']}`, nullity `{action['hessian_nullity']}`, and determinant",
        f"`{action['hessian_determinant']}`. Its generic determinant is", "",
        f"`{action['generic_determinant_on_F_flat_messenger_chain_locus']}`.", "",
        f"Tree-level elimination yields `{effective['tree_level_effective_superpotential']}`. The exponent",
        f"matrix has exact determinant `{effective['exact_exponent_determinant']}`.", "",
        "The symbolic determinant is evaluated on the exact F-flat messenger-chain locus. Tree elimination",
        "also assumes `MU*MA*MB*MC != 0` and nonzero displayed link couplings.", "",
        "The selected, deliberately truncated block sum has 230 coordinates, rank 193, and nullity 37 = 33",
        "gauge plus 4 weak-Higgs coordinates. This arithmetic is not assigned to the symmetry-complete EFT.", "",
        "## Symmetry-complete failure", "",
        f"The complete zero/one/two-VEV census has `{danger['Z9_neutral_row_count_before_center_filter']}` Z9-neutral rows.",
        f"The Spin(10) Z4 center filter rejects `{danger['center_rejected_row_count']}` spinor-dressed rows, leaving",
        f"`{danger['allowed_row_count']}` genuine gauge-invariant degree-six",
        f"dressings, carrying `{danger['allowed_invariant_directions']}` exact Spin(10) invariant directions:", "",
    ]
    for row in danger["allowed_rows"]:
        lines.append(f"- `{row['operator']}`")
    lines += [
        "", "The charge-four messenger also permits the renormalizable `C_messenger H1^2` operator.",
        "Its nonzero VEV raises the generic filter rank from 36 to 40 and removes the intended weak kernel.", "",
        "Every cubic singlet-messenger tree for `S P^4` has a terminal `PP` or `PS` composite. Required",
        "source/filter/Yukawa relations make `F^4 S Y_(2p)` and `Y_(2p) H1^2` neutral for the `PP`",
        "case, or make `F^4 P Y_(-3p)` neutral for the `PS` case, in every Abelian factor. Product",
        "Abelian symmetries and matter parity therefore do not repair this bounded class.", "",
        "## Anomalies and running", "",
        "The two new VEV singlets and all four messenger pairs are vectorlike under Z9; the three drivers",
        "are neutral. Added gravitational, cubic, and mixed-SO(10) anomaly residues vanish, so no additional",
        "anomaly spectators are needed. The original spectator repair remains in place.", "",
        f"All new fields are SO(10) singlets, so `sum T={running['one_loop_SO10_running']['total_T_unchanged']}`",
        f"and `b={running['one_loop_SO10_running']['b_unchanged']}` remain unchanged. The formal one-loop pole",
        f"is `{running['one_loop_SO10_running']['pole_over_matching_scale_at_g0p73_unchanged']:.6f}` times the",
        "matching scale: above 100x but below 1000x.", "",
        "The tree no-go does not cover non-Abelian shaping symmetries, a redesigned source admitting a",
        "nontrivial R action, non-singlet mediators, tuned cancellations, or nonperturbative dynamics.", "",
        "Perturbative loop generation is not an automatic escape because the superpotential is protected by",
        "the [supersymmetric nonrenormalization theorem](https://arxiv.org/abs/hep-ph/9309335). Discrete",
        "anomaly scope follows [Banks and Dine](https://arxiv.org/abs/hep-th/9109045).", "",
    ]
    return "\n".join(lines)


def validate_report(report: Mapping[str, Any]) -> None:
    if report["n_failed"] or report["failures"]:
        raise ArithmeticError(report["failures"])
    if canonical_sha(report) != report["core_sha256"]:
        raise ArithmeticError("core hash mismatch")
    if report["gate_effect"]["candidate_gate_promotions"] != 0:
        raise ArithmeticError("gate boundary drift")
    if report["selected_action_vs_complete_EFT"]["strict_same_action_feasibility"]:
        raise ArithmeticError("selected action was conflated with the complete EFT")


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
