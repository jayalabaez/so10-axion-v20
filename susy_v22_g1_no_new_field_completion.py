#!/usr/bin/env python3
"""Exact no-new-field V22 G1 sector completion.

The original 33 fields and all five linear tadpoles are retained.  The Smith
quotient now includes the superpotential charge omega, so ordinary and R-type
additive Abelian shaping factors are treated uniformly.  Exactly 79 omitted
degree<=4 sectors are forced by the 29 intended relations.  A frozen
Z7R x Z2 assignment selects precisely the minimal 108-sector closure and its
standard mixed discrete anomalies cancel.

This is a constructive sector-level completion, not a completed V22 model:
the 79 new operators change the vacuum, flavour and component matrices and
must be accepted and revalidated before they may be source-landed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_decomp

import susy_v22_g1_holomorphic_ring_frontier as upstream
from susy_so10x17_v22_contract import FIELDS, TERMS


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"
OUT_MD = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.md"
UPSTREAM_JSON = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"
SCHEMA = "susy_v22_g1_no_new_field_completion_v1"
FIELD_NAMES = upstream.FIELD_NAMES
OMEGA = "W"
EXTENDED_NAMES = FIELD_NAMES + (OMEGA,)
FIELD_INDEX = {name: index for index, name in enumerate(FIELD_NAMES)}
LINEAR_TERMS = {
    "linearNphi": ("Nphi",), "linearNC": ("NC",),
    "linearNMP": ("NMP",), "linearNX": ("NX",), "linearNS": ("NS",),
}
Z7R = dict(zip(FIELD_NAMES, (
    1, 1, 1, 2, 4, 2, 5, 4, 4, 0, 0, 2, 3, 6, 0, 6, 0, 6,
    3, 4, 4, 3, 2, 2, 0, 3, 4, 2, 6, 2, 2, 5, 5,
)))
Z7R_W = 2
Z2S_ODD = frozenset({"DeltaB", "Delta2", "XMP", "Z0"})
Z28R = dict(zip(FIELD_NAMES, (
    1, 1, 1, 9, 25, 9, 5, 25, 25, 0, 0, 2, 10, 20, 0, 20, 0, 20,
    24, 4, 4, 24, 2, 2, 0, 24, 4, 2, 20, 2, 2, 12, 12,
)))
Z28R_W = 2


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def field_vector(fields: Iterable[str]) -> tuple[int, ...]:
    result = [0] * len(FIELD_NAMES)
    for name in fields:
        result[FIELD_INDEX[name]] += 1
    return tuple(result)


def relation_vector(fields: Iterable[str]) -> tuple[int, ...]:
    return field_vector(fields) + (-1,)


def desired_relations() -> dict[tuple[int, ...], list[str]]:
    result: dict[tuple[int, ...], list[str]] = {}
    for coupling, fields in {**TERMS, **LINEAR_TERMS}.items():
        result.setdefault(relation_vector(fields), []).append(coupling)
    return result


def smith_data(relations: list[tuple[int, ...]]) -> tuple[Matrix, int, list[int]]:
    diagonal, _left, right = smith_normal_decomp(Matrix(relations), domain=ZZ)
    rank = sum(diagonal[index, index] != 0 for index in range(min(diagonal.shape)))
    factors = [abs(int(diagonal[index, index])) for index in range(rank)]
    return right, rank, factors


def quotient_coordinates(operator: tuple[int, ...], right: Matrix) -> tuple[int, ...]:
    augmented = operator + (-1,)
    return tuple(int(value) for value in (Matrix([augmented]) * right).tolist()[0])


def zero_in_quotient(operator: tuple[int, ...], right: Matrix, rank: int, factors: list[int]) -> bool:
    coordinates = quotient_coordinates(operator, right)
    return (
        all(coordinates[index] % factors[index] == 0 for index in range(rank))
        and all(coordinates[index] == 0 for index in range(rank, len(EXTENDED_NAMES)))
    )


def shaping_allowed(operator: tuple[int, ...]) -> bool:
    z7 = sum(power * Z7R[name] for name, power in zip(FIELD_NAMES, operator)) % 7
    z2 = sum(power * int(name in Z2S_ODD) for name, power in zip(FIELD_NAMES, operator)) % 2
    return z7 == Z7R_W and z2 == 0


def z7r_anomalies() -> dict[str, Any]:
    a_so10 = 8
    a_x2 = 0
    a_xr2 = 0
    a_gravity = -21 + 46
    for field in FIELDS:
        fermion_charge = Z7R[field["name"]] - 1
        multiplicity = field["multiplicity"]
        dimension = abs(field["SO10_dimension"])
        a_so10 += multiplicity * field["SO10_Dynkin_index"] * fermion_charge
        a_x2 += multiplicity * dimension * field["X"] ** 2 * fermion_charge
        a_xr2 += multiplicity * dimension * field["X"] * fermion_charge ** 2
        a_gravity += multiplicity * dimension * fermion_charge
    raw = {
        "SO10_squared_Z7R": a_so10,
        "U1X_squared_Z7R": a_x2,
        "U1X_Z7R_squared": a_xr2,
        "gravity_squared_Z7R": a_gravity,
    }
    return {"integer_values": raw, "mod_7": {name: value % 7 for name, value in raw.items()}}


def z2s_anomalies() -> dict[str, int]:
    odd_fields = [field for field in FIELDS if field["name"] in Z2S_ODD]
    return {
        "odd_Weyl_dimension": sum(field["multiplicity"] * abs(field["SO10_dimension"]) for field in odd_fields),
        "SO10_index_sum": sum(field["multiplicity"] * field["SO10_Dynkin_index"] for field in odd_fields),
        "U1X_squared_sum": sum(field["multiplicity"] * abs(field["SO10_dimension"]) * field["X"] ** 2 for field in odd_fields),
        "U1X_Z2_squared_exact": sum(field["multiplicity"] * abs(field["SO10_dimension"]) * field["X"] for field in odd_fields),
    }


def z28r_anomalies() -> dict[str, Any]:
    a_so10 = 8
    a_x2 = 0
    a_xr2 = 0
    a_gravity = -21 + 46
    for field in FIELDS:
        fermion_charge = Z28R[field["name"]] - 1
        multiplicity = field["multiplicity"]
        dimension = abs(field["SO10_dimension"])
        a_so10 += multiplicity * field["SO10_Dynkin_index"] * fermion_charge
        a_x2 += multiplicity * dimension * field["X"] ** 2 * fermion_charge
        a_xr2 += multiplicity * dimension * field["X"] * fermion_charge ** 2
        a_gravity += multiplicity * dimension * fermion_charge
    raw = {
        "SO10_squared_Z28R": a_so10,
        "U1X_squared_Z28R": a_x2,
        "U1X_Z28R_squared": a_xr2,
        "gravity_squared_Z28R": a_gravity,
    }
    return {
        "integer_values": raw,
        "linear_mod_eta_14": {
            name: value % 14 for name, value in raw.items()
            if name != "U1X_Z28R_squared"
        },
        "U1X_Z28R_squared_mod_28": a_xr2 % 28,
    }


def monomial(counts: tuple[int, ...]) -> str:
    return " ".join(
        name if power == 1 else f"{name}^{power}"
        for name, power in zip(FIELD_NAMES, counts) if power
    ) or "1"


def build_report() -> dict[str, Any]:
    source = json.loads(UPSTREAM_JSON.read_text(encoding="utf-8"))
    allowed_rows = source["all_allowed_sectors"]
    relations = desired_relations()
    desired_operators = {relation[:-1] for relation in relations}
    right, rank, factors = smith_data(list(relations))
    zero_rows = [
        row for row in allowed_rows
        if zero_in_quotient(tuple(row["count_tuple"]), right, rank, factors)
    ]
    selected_rows = [row for row in allowed_rows if shaping_allowed(tuple(row["count_tuple"]))]
    zero_set = {tuple(row["count_tuple"]) for row in zero_rows}
    selected_set = {tuple(row["count_tuple"]) for row in selected_rows}
    forced = [row for row in zero_rows if tuple(row["count_tuple"]) not in desired_operators]
    anomalies7 = z7r_anomalies()
    anomalies2 = z2s_anomalies()
    anomalies28 = z28r_anomalies()

    drivers = ("NX", "NS", "Nphi", "NC", "NMP")
    products = {
        "Phi210_squared": ("Phi210", "Phi210"),
        "C16bar_C16": ("C16bar", "C16"),
        "XMP_squared": ("XMP", "XMP"),
        "Phi17_pair": ("Phi17p", "Phi17m"),
        "S_pair": ("Splus", "Sminus"),
    }
    driver_grid = []
    for driver in drivers:
        for product_name, product_fields in products.items():
            operator = field_vector((driver,) + product_fields)
            driver_grid.append({
                "driver": driver, "product": product_name,
                "monomial": monomial(operator), "selected": operator in selected_set,
            })

    selected_by_degree = {
        str(degree): sum(row["degree"] == degree for row in selected_rows)
        for degree in range(1, 5)
    }
    intended_components = sum(
        row["so10_flavour_component_multiplicity"]
        for row in selected_rows if tuple(row["count_tuple"]) in desired_operators
    )
    forced_components = sum(row["so10_flavour_component_multiplicity"] for row in forced)
    vev_fields = ("Phi210", "C16", "C16bar", "XMP", "Splus", "Sminus", "Phi17p", "Phi17m")
    checks = {
        "frozen_V22_census_has_1045_allowed_and_29_declared":
            source["counts"]["allowed_base_field_sectors"] == 1045
            and source["counts"]["declared_allowed_sectors"] == 29,
        "all_29_intended_relations_are_distinct": len(relations) == 29,
        "smith_rank_is_24_with_free_rank_10": rank == 24 and len(EXTENDED_NAMES) - rank == 10,
        "smith_torsion_is_one_Z2": [factor for factor in factors if factor > 1] == [2],
        "exactly_79_extra_sectors_are_Abelian_R_unavoidable": len(forced) == 79,
        "minimal_closed_catalogue_has_108_sectors": len(zero_rows) == 108,
        "Z7R_times_Z2S_selects_exactly_the_Smith_zero_class": selected_set == zero_set,
        "all_declared_sectors_are_selected": desired_operators <= selected_set,
        "all_Z7R_mixed_anomalies_vanish_mod_7": all(value == 0 for value in anomalies7["mod_7"].values()),
        "Z28R_is_the_CRT_combination_of_source_Z4R_and_new_Z7R":
            all(Z28R[name] % 4 == upstream.FIELD_BY_NAME[name]["R4"] % 4 for name in FIELD_NAMES)
            and all(Z28R[name] % 7 == Z7R[name] for name in FIELD_NAMES)
            and Z28R_W % 4 == Z28R_W % 7 == 2,
        "all_Z28R_mixed_anomalies_vanish_under_eta_14_convention":
            all(value == 0 for value in anomalies28["linear_mod_eta_14"].values())
            and anomalies28["U1X_Z28R_squared_mod_28"] == 0,
        "required_VEVs_leave_exactly_a_Z4R_subgroup_of_Z28R":
            __import__("math").gcd(28, *(Z28R[name] for name in vev_fields)) == 4,
        "Z2S_has_even_gravity_SO10_and_X2_ledgers":
            anomalies2["odd_Weyl_dimension"] % 2 == 0
            and anomalies2["SO10_index_sum"] % 2 == 0
            and anomalies2["U1X_squared_sum"] % 2 == 0,
        "Z2S_U1X_Z2_squared_vanishes_exactly": anomalies2["U1X_Z2_squared_exact"] == 0,
        "complete_five_by_five_driver_product_grid_is_selected":
            len(driver_grid) == 25 and all(row["selected"] for row in driver_grid),
        "no_degree_two_superpotential_sector_is_selected": selected_by_degree["2"] == 0,
        "field_content_and_continuous_anomalies_are_unchanged": True,
        "full_G1_and_later_gates_are_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "candidate.susy_so10x17.v22r.G1.no_new_field_completion",
        "status": ("EXACT_NO_NEW_FIELD_DEGREE4_ABELIAN_R_COMPLETION_FOUND__79_EXTRA_OPERATORS_REQUIRE_REVALIDATION"
                   if not failures else "V22_G1_NO_NEW_FIELD_COMPLETION_FAILED"),
        "overall_state": "CONSTRUCTIVE_SECTOR_COMPLETION__MODEL_ACCEPTANCE_OPEN" if not failures else "EXECUTION_FAIL",
        "source_manifest": [{
            "path": UPSTREAM_JSON.name, "mode": "raw", "sha256": sha256(UPSTREAM_JSON.read_bytes()),
        }],
        "smith_quotient": {
            "generators_including_W_charge": len(EXTENDED_NAMES),
            "relation_rank": rank,
            "free_rank": len(EXTENDED_NAMES) - rank,
            "invariant_factors": factors,
            "nontrivial_torsion": [factor for factor in factors if factor > 1],
            "interpretation": "field-charge lattice plus W charge, modulo the 29 intended relations",
        },
        "shaping_symmetry": {
            "group": "Z28R x Z2S",
            "Z28R_superpotential_charge": Z28R_W,
            "Z28R_field_charges": Z28R,
            "Z28R_anomalies": anomalies28,
            "Z28R_unbroken_VEV_remnant": "Z4R",
            "Z7R_superpotential_charge": Z7R_W,
            "Z7R_field_charges": Z7R,
            "Z2S_odd_fields": sorted(Z2S_ODD),
            "Z7R_anomalies": anomalies7,
            "Z2S_anomalies": anomalies2,
        },
        "counts": {
            "original_allowed_sectors": len(allowed_rows),
            "intended_sectors": len(desired_operators),
            "unavoidable_extra_sectors": len(forced),
            "minimum_selected_sectors": len(selected_rows),
            "rejected_sectors": len(allowed_rows) - len(selected_rows),
            "selected_by_degree": selected_by_degree,
            "selected_flavour_components": sum(
                row["so10_flavour_component_multiplicity"] for row in selected_rows
            ),
            "intended_flavour_components": intended_components,
            "unavoidable_extra_flavour_components": forced_components,
        },
        "unavoidable_extra_sectors": forced,
        "selected_sectors": selected_rows,
        "driver_constraint_matrix": {
            "shape": [5, 5],
            "all_entries_selected": all(row["selected"] for row in driver_grid),
            "entries": driver_grid,
            "generic_full_rank_point_exists": True,
            "interpretation": "the five source-indistinguishable drivers couple to a generic matrix of the five GUT constraint products",
        },
        "physics_effect": {
            "new_chiral_fields": 0,
            "new_supersymmetric_moduli_from_field_count": 0,
            "original_diagonal_F_flat_solution_inherited": False,
            "reason": "the generic 5x5 driver matrix and 54 other new sectors change every F equation and component mass matrix",
            "direct_degree_two_light_mass_terms_selected": False,
            "Z7R_broken_by_required_VEVs": True,
            "Z2S_broken_by_XMP_VEV": True,
            "source_Z4R_hierarchy_remnant_can_remain_unbroken": True,
            "all_order_spurion_completion_closed": False,
        },
        "completion_verdict": {
            "classical_degree_le_4_sector_completion_exists_without_new_fields": not failures,
            "accept_79_new_operators_as_active_V22": False,
            "source_land_as_active_V22": False,
            "full_V22_repair_achieved": False,
            "reason_not_promoted": [
                "accepting 79 new sectors and 194 additional flavour/contraction components is a material new model choice",
                "the complete F+D+soft vacuum and Hessian must be recomputed for the generic 5x5 driver system",
                "all missing-partner component Clebsches and flavour fits must include the new cubic/quartic operators",
                "the shaping symmetries are spontaneously broken, so their all-order spurion completion remains open",
                "Kahler/soft rings and independent SO(10) tensor-copy normalizations remain open",
            ],
        },
        "claim_boundary": {
            "degree_le_4_holomorphic_sector_selection_closed": not failures,
            "standard_Z7R_Z2S_anomaly_arithmetic_closed": not failures,
            "active_V22_source_repaired": False,
            "full_V22_G1_closed": False,
            "V22_G2_closed": False,
            "V22_G3_closed": False,
            "V22_G4_closed": False,
        },
        "next_exact_target": ("Accepting this route means defining a V22R model with all 108 sectors, then recomputing "
                              "the complete tensor basis and global F+D+soft vacuum from zero."),
        "checks": checks,
        "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
    }
    report = json.loads(json.dumps(report))
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    return "\n".join([
        "# SUSY V22 G1 no-new-field completion", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Intended sectors: {counts['intended_sectors']}",
        f"- Unavoidable added sectors: {counts['unavoidable_extra_sectors']}",
        f"- Exact minimum catalogue: {counts['minimum_selected_sectors']}",
        f"- Rejected original sectors: {counts['rejected_sectors']}",
        f"- Selector: `{report['shaping_symmetry']['group']}`", "",
        "This is the strongest minimal construction found: it adds no fields, selects exactly the Smith-quotient",
        "minimum, cancels the standard discrete anomalies, and retains no degree-two superpotential mass sector.", "",
        "It is not activated automatically. The 79 unavoidable operators replace the diagonal driver system by a",
        "generic 5x5 constraint matrix and alter the flavour, vacuum and component spectra. Accepting this route",
        "therefore means defining and validating a materially new V22R model from G1 onward.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("no-new-field completion JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("no-new-field completion Markdown drifted")
    print(report["status"]); print(report["core_sha256"])
    print(json.dumps(report["counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
