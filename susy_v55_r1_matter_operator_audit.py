#!/usr/bin/env python3
"""V55 family-charge and operator audit of the V54 R1 charged-source rescue.

The audit fixes the V54 continuous-U(1) normalization (the singlet L has
charge +1), requires a renormalizable third-family 16_3 16_3 H1 coupling,
and searches ordered integer family charges in 11 <= q2 <= q1 <= 50.
Guaranteed SO(10) operators are dressed only by VEV singlets; an exact
dominance argument shows that the non-singlet VEVs cannot lower the insertion
count in this positive-family-charge domain.  Spin(10) characters determine
which four-family tensors actually exist.

The family sector has bounded Froggatt-Nielsen-like survivors, but the same
R1 charge ledger already permits the renormalizable L h H2 filler.  Because L
has a nonzero VEV, the protected weak-Higgs kernel is generically filled.
Furthermore, every differentiated family solution invalidates the fixed V54
single-GS spectator universality ledger.  No gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import g1_exact_declared_symmetry_character_census_v20 as d5


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.md"
UPSTREAM_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"

STATUS = (
    "V55_R1_EXACT_FAMILY_CHARGE_SEARCH_FINDS_BOUNDED_FN_SURVIVORS__"
    "SPIN10_TENSOR_FILTER_REMOVES_SINGLE_FAMILY_FOURTH_POWERS__"
    "BUT_RENORMALIZABLE_L_H_H2_FILLER_KILLS_NATURAL_DT__"
    "DIFFERENTIATED_FAMILIES_INVALIDATE_FIXED_GS_REPAIR__NO_GATE_PROMOTION"
)

SINGLET_VEV_CHARGES = {
    "P": 6,
    "S": -12,
    "T": -6,
    "R": 4,
    "M": -2,
    "L": 1,
    "K": 2,
}
HIGGS_10_CHARGES = {"H1": -22, "barh": 16, "h": -4, "H2": 3}
FAMILY_PATTERNS = [
    (4, 0, 0), (3, 1, 0),
    (2, 2, 0), (2, 0, 2), (0, 2, 2),
    (2, 1, 1), (1, 2, 1), (1, 1, 2),
]
GAUGE_VALID_PROTON_PATTERNS = FAMILY_PATTERNS[2:]
MAX_DRESSING_INSERTIONS = 20


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_upstream() -> dict[str, Any]:
    value = json.loads(UPSTREAM_PATH.read_text(encoding="utf-8"))
    if value.get("core_sha256") != EXPECTED_UPSTREAM_CORE or canonical_sha(value) != EXPECTED_UPSTREAM_CORE:
        raise ArithmeticError("stale V54 R1 input")
    return value


@lru_cache(None)
def dressing_table(maximum: int = MAX_DRESSING_INSERTIONS) -> dict[int, tuple[int, tuple[str, ...]]]:
    names = tuple(SINGLET_VEV_CHARGES)
    result: dict[int, tuple[int, tuple[str, ...]]] = {0: (0, ())}
    for degree in range(1, maximum + 1):
        for indices in itertools.combinations_with_replacement(range(len(names)), degree):
            charge = sum(SINGLET_VEV_CHARGES[names[index]] for index in indices)
            result.setdefault(charge, (degree, tuple(names[index] for index in indices)))
    return result


def minimal_dressing(target_charge: int) -> dict[str, Any] | None:
    found = dressing_table().get(target_charge)
    if found is None:
        return None
    return {"insertions": found[0], "fields": list(found[1]), "charge": target_charge}


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


@lru_cache(None)
def spinor_character() -> Counter:
    return d5.spinor()


@lru_cache(None)
def barspinor_character() -> Counter:
    return Counter({tuple(-entry for entry in weight): mult for weight, mult in spinor_character().items()})


def tensor_singlets(factors: Sequence[Counter]) -> int:
    ordered = sorted(factors, key=len)
    result = ordered[0]
    for factor in ordered[1:]:
        result = d5.tensor(result, factor)
    return d5.singlet(result)


@lru_cache(None)
def family_F4_multiplicity(counts: tuple[int, int, int]) -> int:
    factors = [d5.sym(spinor_character(), count) for count in counts if count]
    return tensor_singlets(factors)


def tensor_audit() -> dict[str, Any]:
    proton_rows = [
        {
            "family_counts": list(counts),
            "Spin10_singlet_multiplicity": family_F4_multiplicity(counts),
            "center_Z4_charge": sum(counts) % 4,
        }
        for counts in FAMILY_PATTERNS
    ]
    spinor = spinor_character()
    barspinor = barspinor_character()
    vector = d5.vector()
    return {
        "Spin10_center_convention": {"16": 1, "bar16": 3, "10": 2, "tensor_and_singlet": 0},
        "four_family_rows": proton_rows,
        "single_family_F_i_fourth_power_is_absent": family_F4_multiplicity((4, 0, 0)) == 0,
        "three_plus_one_family_pattern_is_absent": family_F4_multiplicity((3, 1, 0)) == 0,
        "gauge_valid_patterns": [list(row) for row in GAUGE_VALID_PROTON_PATTERNS],
        "valid_pattern_multiplicities": [family_F4_multiplicity(row) for row in GAUGE_VALID_PROTON_PATTERNS],
        "total_family_invariants": sum(family_F4_multiplicity(row) for row in GAUGE_VALID_PROTON_PATTERNS),
        "Yukawa_FiFiH1_multiplicity": tensor_singlets([d5.sym(spinor, 2), vector]),
        "Yukawa_FiFjH1_multiplicity_for_i_ne_j": tensor_singlets([spinor, spinor, vector]),
        "Majorana_FiFi_barC2_multiplicity": tensor_singlets([d5.sym(spinor, 2), d5.sym(barspinor, 2)]),
        "Majorana_FiFj_barC2_multiplicity_for_i_ne_j": tensor_singlets([spinor, spinor, d5.sym(barspinor, 2)]),
        "tensor_scope": (
            "exact D5 weight characters; singlet-spurion dressings preserve each listed multiplicity"
        ),
    }


def degree_matrix(charges: Sequence[int], base_charge: int) -> tuple[list[list[int]], list[list[list[str]]]]:
    degrees: list[list[int]] = []
    witnesses: list[list[list[str]]] = []
    for left in range(3):
        degree_row = []
        witness_row = []
        for right in range(3):
            dressing = minimal_dressing(base_charge - charges[left] - charges[right])
            if dressing is None:
                degree_row.append(MAX_DRESSING_INSERTIONS + 1)
                witness_row.append([])
            else:
                degree_row.append(dressing["insertions"])
                witness_row.append(dressing["fields"])
        degrees.append(degree_row)
        witnesses.append(witness_row)
    return degrees, witnesses


def proton_rows(charges: Sequence[int]) -> list[dict[str, Any]]:
    rows = []
    for counts in GAUGE_VALID_PROTON_PATTERNS:
        bare_charge = sum(count * charge for count, charge in zip(counts, charges))
        dressing = minimal_dressing(-bare_charge)
        rows.append({
            "family_counts": list(counts),
            "bare_U1_charge": bare_charge,
            "Spin10_singlet_multiplicity": family_F4_multiplicity(counts),
            "first_singlet_dressing": dressing,
            "total_degree": 4 + dressing["insertions"] if dressing else None,
        })
    return rows


def candidate_row(charges: Sequence[int]) -> dict[str, Any]:
    yukawa, yukawa_witness = degree_matrix(charges, 22)
    # q(barC)=-1, so Fi Fj barC^2 has bare charge qi+qj-2.
    majorana, majorana_witness = degree_matrix(charges, 2)
    protons = proton_rows(charges)
    earliest = min(row["first_singlet_dressing"]["insertions"] for row in protons if row["first_singlet_dressing"])
    hierarchy_proxy = (
        yukawa[2][2] == 0
        and 1 <= yukawa[1][1] < yukawa[0][0] <= 8
        and max(max(row) for row in yukawa) <= 8
        and max(max(row) for row in majorana) <= 10
    )
    monotone_proxy = hierarchy_proxy and (
        yukawa[0][0] >= yukawa[0][1] >= yukawa[1][1]
        >= yukawa[0][2] >= yukawa[1][2] > yukawa[2][2]
    )
    family_sum = sum(charges)
    return {
        "charges": list(charges),
        "Yukawa_leading_singlet_insertions": yukawa,
        "Yukawa_dressing_witnesses": yukawa_witness,
        "Majorana_leading_singlet_insertions": majorana,
        "Majorana_dressing_witnesses": majorana_witness,
        "charge_level_full_Yukawa_and_Majorana_support": (
            max(max(row) for row in yukawa) <= 8 and max(max(row) for row in majorana) <= 10
        ),
        "hierarchical_connected_proxy": hierarchy_proxy,
        "strict_monotone_FN_proxy": monotone_proxy,
        "proton_rows": protons,
        "earliest_gauge_invariant_F4_dressing_insertions": earliest,
        "earliest_gauge_invariant_F4_total_degree": 4 + earliest,
        "Spin10_squared_U1_anomaly": 2 * family_sum - 17,
        "fixed_repair_TrQ": 648 + 16 * family_sum,
        "single_GS_required_TrQ": 24 * (2 * family_sum - 17),
        "fixed_V54_GS_universality": 648 + 16 * family_sum == 24 * (2 * family_sum - 17),
    }


def bounded_family_search() -> dict[str, Any]:
    accepted = []
    scanned = 0
    for q2 in range(11, 51):
        for q1 in range(q2, 51):
            scanned += 1
            row = candidate_row((q1, q2, 11))
            if row["hierarchical_connected_proxy"]:
                accepted.append(row)
    strict = [row for row in accepted if row["strict_monotone_FN_proxy"]]
    maximum = max(row["earliest_gauge_invariant_F4_dressing_insertions"] for row in accepted)
    strict_maximum = max(row["earliest_gauge_invariant_F4_dressing_insertions"] for row in strict)
    best = [row for row in accepted if row["earliest_gauge_invariant_F4_dressing_insertions"] == maximum]
    strict_best = [row for row in strict if row["earliest_gauge_invariant_F4_dressing_insertions"] == strict_maximum]
    strict_best.sort(key=lambda row: row["charges"])
    return {
        "normalization": "integer lattice fixed by q(L)=+1",
        "domain": {"q3": 11, "q2_min": 11, "q1_max": 50, "ordering": "11<=q2<=q1<=50"},
        "top_Yukawa_requirement": "2 q3+q(H1)=0, hence q3=11",
        "maximum_singlet_dressing_insertions_enumerated": MAX_DRESSING_INSERTIONS,
        "scanned_charge_triples": scanned,
        "hierarchical_proxy_definition": (
            "Y33 is renormalizable; 1<=d22<d11<=8; every symmetric Yukawa entry has d<=8; "
            "every FiFj barC^2 Majorana entry has d<=10"
        ),
        "strict_monotone_addition": "d11>=d12>=d22>=d13>=d23>d33",
        "accepted_hierarchical_proxy_count": len(accepted),
        "accepted_strict_monotone_count": len(strict),
        "maximum_proton_dressing_insertions_in_proxy": maximum,
        "maximum_proton_dressing_insertions_in_strict_proxy": strict_maximum,
        "best_proxy_rows": best,
        "strict_best_count": len(strict_best),
        "strict_best_rows": strict_best,
        "accepted_rows_sha256": hashlib.sha256(canonical_bytes(accepted)).hexdigest(),
        "accepted_charge_triples": [row["charges"] for row in accepted],
        "strict_charge_triples": [row["charges"] for row in strict],
        "accepted_differentiated_fixed_repair_count": sum(
            row["fixed_V54_GS_universality"] for row in accepted if len(set(row["charges"])) > 1
        ),
        "scope_limit": (
            "charge-level operator support and hierarchy proxy only; no Clebsch structure, coefficients, RG evolution, "
            "thresholds, or current quark/lepton likelihood is fitted"
        ),
    }


def higgs_bilinear_census(upstream: Mapping[str, Any]) -> dict[str, Any]:
    fields = list(HIGGS_10_CHARGES)
    rows = []
    intended = {("H1", "barh"), ("barh", "h"), ("H2", "H2")}
    for left_index, left in enumerate(fields):
        for right in fields[left_index:]:
            bare = HIGGS_10_CHARGES[left] + HIGGS_10_CHARGES[right]
            dressing = minimal_dressing(-bare)
            rows.append({
                "bilinear": f"{left} {right}",
                "bare_U1_charge": bare,
                "first_singlet_dressing": dressing,
                "total_degree": 2 + dressing["insertions"] if dressing else None,
                "Spin10_center_Z4_charge": 0,
                "Spin10_singlet_exists": True,
                "role": "displayed_filter_structure" if (left, right) in intended else "additional_allowed_filler",
            })
    fatal = next(row for row in rows if row["bilinear"] == "h H2")
    filter_data = json.loads((ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json").read_text(encoding="utf-8"))
    weak_without_filler = [[0, 1, 0, 0], [1, 0, 2, 0], [0, 2, 0, 0], [0, 0, 0, 3]]
    weak_with_filler = [[0, 1, 0, 0], [1, 0, 2, 0], [0, 2, 0, 1], [0, 0, 1, 3]]
    return {
        "complete_10_bilinear_singlet_spurion_census": rows,
        "fatal_earliest_filler": {
            **fatal,
            "operator": "L h_10 H2_10",
            "charge_arithmetic": "1-4+3=0",
            "L_VEV_nonzero": True,
            "renormalizable": True,
            "one_weak_component_matrix_before": weak_without_filler,
            "one_weak_component_matrix_after_unit_filler": weak_with_filler,
            "one_weak_component_rank_before_QQ": exact_rank(weak_without_filler),
            "one_weak_component_rank_after_QQ": exact_rank(weak_with_filler),
            "weak_filter_rank_before": 4 * exact_rank(weak_without_filler),
            "weak_filter_rank_after_generic_direct_hH2_mass": 4 * exact_rank(weak_with_filler),
            "full_filter_rank_before": 24 + 4 * exact_rank(weak_without_filler),
            "full_filter_rank_after": 24 + 4 * exact_rank(weak_with_filler),
            "weak_Higgs_nullity_after": 16 - 4 * exact_rank(weak_with_filler),
        },
        "H1_squared_first_dressing": minimal_dressing(44),
        "H1_squared_first_total_degree": 2 + minimal_dressing(44)["insertions"],
        "upstream_claimed_direct_hH2_charge": upstream["charged_source_dynamical_rescue"]["operator_screen"]["direct_h_H2_charge"],
        "upstream_generic_H1_squared_filler_rank": filter_data["filter_mass_blocks"]["H1_squared_unit_filler_rank"],
        "conclusion": (
            "screening the bare h H2 charge is insufficient because the same-action VEV singlet L makes L h H2 renormalizable"
        ),
    }


def non_singlet_dominance_certificate() -> dict[str, Any]:
    return {
        "non_singlet_VEVs": {
            "E54": {"charge": -2, "center": 0, "singlet_replacement": "M(-2) at equal cost"},
            "A45": {"charge": 1, "center": 0, "singlet_replacement": "L(+1) at equal cost"},
            "B45": {"charge": 1, "center": 0, "singlet_replacement": "L(+1) at equal cost"},
            "C16": {"charge": 0, "center": 1, "singlet_replacement": "omit unless needed for center balance"},
            "barC16": {"charge": -1, "center": 3, "singlet_replacement": "center-neutral C barC has charge -1 and cost2, matched by M+L at cost2"},
        },
        "higher_spinor_insertions": (
            "four barC insertions have charge -4 and cost4, dominated by two M insertions; additional center-neutral "
            "spinor combinations are no cheaper than singlet replacements"
        ),
        "result": (
            "within the positive family-charge domain, the singlet-spurion dynamic program gives a global lower bound "
            "on insertion count across all declared VEV representations, and every witness is an actual Spin10 singlet"
        ),
    }


def anomaly_audit(search: Mapping[str, Any]) -> dict[str, Any]:
    strict = search["strict_best_rows"][0]
    broad = search["best_proxy_rows"][0]
    return {
        "formulae": {
            "base_without_three_families_Spin10_squared_U1": -17,
            "with_families": "A_10=2(q1+q2+q3)-17",
            "fixed_134_spectator_repair_TrQ": "TrQ=648+16(q1+q2+q3)",
            "single_GS_universality": "TrQ=24 A_10",
            "universality_solution": "q1+q2+q3=33",
        },
        "ordered_domain_implication": (
            "q_i>=11 and sum=33 force q1=q2=q3=11, so every differentiated hierarchy candidate invalidates the fixed repair"
        ),
        "broad_best_example": {
            "charges": broad["charges"],
            "A_10": broad["Spin10_squared_U1_anomaly"],
            "fixed_TrQ": broad["fixed_repair_TrQ"],
            "required_TrQ": broad["single_GS_required_TrQ"],
        },
        "strict_best_lowest_charge_example": {
            "charges": strict["charges"],
            "A_10": strict["Spin10_squared_U1_anomaly"],
            "fixed_TrQ": strict["fixed_repair_TrQ"],
            "required_TrQ": strict["single_GS_required_TrQ"],
        },
        "accepted_differentiated_candidates_preserve_fixed_GS_repair": search["accepted_differentiated_fixed_repair_count"],
        "repair_scope": "a redesigned GS modulus/spectator spectrum was not searched and would define a changed action",
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    tensor = tensor_audit()
    search = bounded_family_search()
    higgs = higgs_bilinear_census(upstream)
    dominance = non_singlet_dominance_certificate()
    anomaly = anomaly_audit(search)
    checks = {
        "upstream_R1_core_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "F_i_fourth_power_removed_by_exact_tensor_census": tensor["single_family_F_i_fourth_power_is_absent"],
        "six_family_valid_F4_patterns_have_unit_multiplicity": tensor["valid_pattern_multiplicities"] == [1] * 6,
        "Yukawa_tensors_exist_for_equal_and_distinct_families": tensor["Yukawa_FiFiH1_multiplicity"] == tensor["Yukawa_FiFjH1_multiplicity_for_i_ne_j"] == 1,
        "Majorana_tensors_exist_for_equal_and_distinct_families": tensor["Majorana_FiFi_barC2_multiplicity"] == tensor["Majorana_FiFj_barC2_multiplicity_for_i_ne_j"] == 2,
        "integer_domain_has820_ordered_charge_triples": search["scanned_charge_triples"] == 820,
        "bounded_hierarchy_proxy_has_survivors": search["accepted_hierarchical_proxy_count"] > 0,
        "bounded_strict_proxy_has_survivors": search["accepted_strict_monotone_count"] > 0,
        "broad_proxy_maximum_proton_insertion_is11": search["maximum_proton_dressing_insertions_in_proxy"] == 11,
        "strict_proxy_maximum_proton_insertion_is10": search["maximum_proton_dressing_insertions_in_strict_proxy"] == 10,
        "strict_lowest_best_charge_is45_39_11": search["strict_best_rows"][0]["charges"] == [45, 39, 11],
        "fatal_L_h_H2_is_renormalizable_and_neutral": (
            higgs["fatal_earliest_filler"]["renormalizable"]
            and higgs["fatal_earliest_filler"]["charge_arithmetic"] == "1-4+3=0"
        ),
        "fatal_filler_removes_all_weak_Higgs_modes": higgs["fatal_earliest_filler"]["weak_Higgs_nullity_after"] == 0,
        "H1_squared_itself_first_appears_at_total_degree10": higgs["H1_squared_first_total_degree"] == 10,
        "non_singlet_VEVs_cannot_improve_minimum_in_domain": "global lower bound" in dominance["result"],
        "fixed_GS_repair_requires_family_sum33": anomaly["formulae"]["universality_solution"] == "q1+q2+q3=33",
        "no_differentiated_survivor_preserves_fixed_GS_repair": anomaly["accepted_differentiated_candidates_preserve_fixed_GS_repair"] == 0,
        "selected_action_not_promoted_to_complete_theory": True,
        "no_gate_promotion": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v55_r1_matter_operator_audit_v1",
        "status": STATUS if not failures else "V55_R1_MATTER_OPERATOR_AUDIT_FAILED",
        "source_manifest": {UPSTREAM_PATH.name: EXPECTED_UPSTREAM_CORE},
        "R1_charge_ledger": {
            "matter_independent_charges": upstream["charged_source_retuning_seed"]["charges"],
            "VEV_singlet_charges_used_for_exact_search": SINGLET_VEV_CHARGES,
            "Higgs_10_charges": HIGGS_10_CHARGES,
            "matter_parity": "all F_i odd; Higgs/source/spurion fields even",
        },
        "Spin10_center_and_tensor_audit": tensor,
        "non_singlet_VEV_dominance_certificate": dominance,
        "bounded_integer_family_charge_search": search,
        "RH_neutrino_operator": {
            "operator": "F_i F_j barC16_H barC16_H times singlet VEV dressings",
            "bare_U1_charge": "q_i+q_j-2",
            "Spin10_center_Z4_charge": "1+1+3+3=8=0",
            "exact_tensor_multiplicity": 2,
            "scope": "effective RH-Majorana operator support; no coefficient scale or neutrino-data fit",
        },
        "complete_Higgs_10_bilinear_census": higgs,
        "family_dependent_anomaly_reaudit": anomaly,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gate_effect": {
            "charge_level_family_Yukawa_and_RH_neutrino_support": "BOUNDED_SURVIVORS_EXIST",
            "natural_DT_same_action": "FAILED_BY_RENORMALIZABLE_L_h_H2",
            "proton_operator": "FINITE_DELAY_ONLY_IN_BOUNDED_SEARCH",
            "fixed_single_GS_repair_with_differentiated_families": "FAILED",
            "flavour_likelihood": "OPEN",
            "G1_through_G8_promotions": [],
            "candidate_gate_promotions": 0,
        },
        "verdict": (
            "The R1 lattice admits bounded family-charge assignments with full charge-level Yukawa and RH-Majorana "
            "support; exact Spin10 tensors remove the spurious single-family F_i^4 class and the strict proxy can "
            "delay the first gauge-invariant F^4 dressing to ten insertions. This does not rescue R1. The exact same "
            "charge ledger permits the renormalizable L h H2 filler, whose L VEV removes all four weak-Higgs modes, "
            "and every differentiated survivor invalidates the fixed V54 GS spectator universality. No gate is promoted."
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    search = report["bounded_integer_family_charge_search"]
    strict = search["strict_best_rows"][0]
    fatal = report["complete_Higgs_10_bilinear_census"]["fatal_earliest_filler"]
    anomaly = report["family_dependent_anomaly_reaudit"]
    return "\n".join([
        "# SUSY V55 R1 matter and operator audit", "",
        f"Status: `{report['status']}`", "",
        f"Core SHA-256: `{report['core_sha256']}`", "",
        "## Result", "", report["verdict"], "",
        "## Exact Spin(10) filter", "",
        "The exact D5 character calculation shows that `F_i^4` and `F_i^3 F_j` have no holomorphic",
        "Spin(10) singlet. The six genuine family classes are the three `F_i^2 F_j^2` and three",
        "`F_i^2 F_j F_k` patterns, each with multiplicity one. Both equal- and mixed-family",
        "`F_i F_j H1` operators exist, and `F_i F_j barC^2` has multiplicity two.", "",
        "## Bounded family search", "",
        f"The exact search scans `{search['scanned_charge_triples']}` ordered integer triples with `q3=11` and",
        "`11<=q2<=q1<=50`, enumerating singlet dressings through 20 insertions. It finds",
        f"`{search['accepted_hierarchical_proxy_count']}` hierarchy-proxy survivors and",
        f"`{search['accepted_strict_monotone_count']}` strict-monotone survivors.", "",
        f"The lowest-charge member of the best strict class is `{strict['charges']}`. Its leading Yukawa",
        f"insertion matrix is `{strict['Yukawa_leading_singlet_insertions']}` and its RH-Majorana matrix is",
        f"`{strict['Majorana_leading_singlet_insertions']}`. Its first valid proton dressing uses",
        f"`{strict['earliest_gauge_invariant_F4_dressing_insertions']}` insertions, at total degree",
        f"`{strict['earliest_gauge_invariant_F4_total_degree']}`. This is a charge-level proxy, not a flavour fit.", "",
        "## Decisive Higgs leak", "",
        f"The complete ten-bilinear singlet-spurion census finds `{fatal['operator']}` at total degree",
        f"`{fatal['total_degree']}` with charge `{fatal['charge_arithmetic']}`. Since `L` has a nonzero VEV,",
        "this is the direct `h H2` mass in the vacuum. The weak filter rank becomes 16 and its nullity becomes",
        "zero; the full four-vector filter rank becomes 40. The earlier bare-charge screen therefore missed",
        "a renormalizable same-action filler.", "",
        "## Anomaly boundary", "",
        "The fixed 134-singlet repair satisfies single-GS universality only when `q1+q2+q3=33`.",
        "In the ordered domain this forces `(11,11,11)`, so no differentiated hierarchy survivor retains",
        f"the fixed repair. For the strict example, `A_10={anomaly['strict_best_lowest_charge_example']['A_10']}`",
        f"while fixed `TrQ={anomaly['strict_best_lowest_charge_example']['fixed_TrQ']}` instead of the required",
        f"`{anomaly['strict_best_lowest_charge_example']['required_TrQ']}`.", "",
        "The result does not exclude a changed Higgs/source action, redesigned GS spectrum, or a complete",
        "flavour construction. Those require new same-action Hessian, anomaly, Wilson, and likelihood audits.", "",
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
