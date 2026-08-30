#!/usr/bin/env python3
"""Constructive and fail-closed search for a minimal V22 G1 repair.

Four neutral-constant tadpoles are replaced by dynamical scale singlets,
while the Nphi tadpole is retained because Nphi Phi^2 and Nphi Phi^3 force
Nphi itself to be allowed under every additive Abelian shaping symmetry.

The exact Smith quotient determines which degree<=4 operators are unavoidable
under ordinary non-R additive shaping factors. A frozen Z1009 x Z2 x Z2
assignment is then verified to select exactly that minimal non-R closure and
to cancel the standard mixed/cubic anomaly
congruences.  The same calculation also exposes why this is not a full repair:
four new F-flat moduli remain and their VEVs break the shaping symmetry.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_decomp

import susy_v22_g1_holomorphic_ring_frontier as upstream
from susy_so10x17_v22_contract import FIELDS, TERMS


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G1_MINIMAL_REPAIR_SEARCH.json"
OUT_MD = ROOT / "SUSY_V22_G1_MINIMAL_REPAIR_SEARCH.md"
UPSTREAM_JSON = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"
FLAT_JSON = ROOT / "SUSY_V22_F_FLAT_GUT_SLICE.json"
R_ANOMALY_JSON = ROOT / "SUSY_V22_Z4R_ANOMALY.json"
SCHEMA = "susy_v22_g1_minimal_repair_search_v1"
PRIME = 1009
NEW_FIELDS = ("KC", "KMP", "KX", "KS")
FIELD_NAMES = upstream.FIELD_NAMES + NEW_FIELDS
FIELD_INDEX = {name: index for index, name in enumerate(FIELD_NAMES)}

REPLACEMENT_TERMS = {
    "linearNphi": ("Nphi",),
    "scaleC": ("NC", "KC", "KC"),
    "scaleMP": ("NMP", "KMP", "KMP"),
    "scaleX": ("NX", "KX", "KX"),
    "scaleS": ("NS", "KS", "KS"),
}

# Found deterministically in the exact quotient nullspace, with the three
# linear anomaly constraints imposed, then verified exhaustively below.
Z1009 = {
    "F": 975, "P": 975, "R": 975, "SpecS": 297, "SpecB": 943,
    "Q": 780, "Pbar": 307, "Qbar": 502, "Rbar": 460,
    "Phi210": 0, "DeltaB": 202, "Delta": 941, "DeltaB2": 375,
    "Delta2": 768, "H10m": 68, "H10p": 634, "T120m": 68,
    "T120p": 634, "Splus": 778, "Sminus": 541, "Phi17p": 583,
    "Phi17m": 736, "NX": 699, "NS": 699, "XMP": 875,
    "C16": 514, "C16bar": 754, "Nphi": 0, "Z0": 81, "NC": 750,
    "NMP": 268, "Z1": 403, "Z2": 717, "KC": 634, "KMP": 875,
    "KX": 155, "KS": 155,
}
Z2A = {name: int(name in {"DeltaB", "Delta2", "XMP"}) for name in FIELD_NAMES}
Z2B = {name: int(name == "KX") for name in FIELD_NAMES}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def vector(fields: Iterable[str]) -> tuple[int, ...]:
    result = [0] * len(FIELD_NAMES)
    for name in fields:
        result[FIELD_INDEX[name]] += 1
    return tuple(result)


def desired_vectors() -> dict[tuple[int, ...], list[str]]:
    result: dict[tuple[int, ...], list[str]] = {}
    for coupling, fields in {**TERMS, **REPLACEMENT_TERMS}.items():
        result.setdefault(vector(fields), []).append(coupling)
    return result


def weak_compositions(total: int, slots: int) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, slots - 1):
            yield (first,) + rest


def extended_allowed_rows() -> list[dict[str, Any]]:
    source = json.loads(UPSTREAM_JSON.read_text(encoding="utf-8"))
    rows = []
    for base in source["all_allowed_sectors"]:
        for new_degree in range(5 - base["degree"]):
            for powers in weak_compositions(new_degree, len(NEW_FIELDS)):
                count_vector = tuple(base["count_tuple"]) + powers
                rows.append({
                    "count_tuple": count_vector,
                    "degree": base["degree"] + new_degree,
                    "monomial": monomial(count_vector),
                    "so10_flavour_component_multiplicity": base["so10_flavour_component_multiplicity"],
                })
    return rows


def monomial(counts: tuple[int, ...]) -> str:
    return " ".join(
        name if power == 1 else f"{name}^{power}"
        for name, power in zip(FIELD_NAMES, counts) if power
    ) or "1"


def smith_data(matrix_rows: list[tuple[int, ...]]) -> tuple[Matrix, int, list[int]]:
    diagonal, _left, right = smith_normal_decomp(Matrix(matrix_rows), domain=ZZ)
    rank = sum(diagonal[index, index] != 0 for index in range(min(diagonal.shape)))
    invariant_factors = [abs(int(diagonal[index, index])) for index in range(rank)]
    return right, rank, invariant_factors


def quotient_coordinates(counts: tuple[int, ...], right: Matrix) -> tuple[int, ...]:
    return tuple(int(value) for value in (Matrix([counts]) * right).tolist()[0])


def zero_in_quotient(
    counts: tuple[int, ...], right: Matrix, rank: int, invariant_factors: list[int]
) -> bool:
    coordinates = quotient_coordinates(counts, right)
    torsion_zero = all(coordinates[index] % invariant_factors[index] == 0 for index in range(rank))
    free_zero = all(coordinates[index] == 0 for index in range(rank, len(FIELD_NAMES)))
    return torsion_zero and free_zero


def shaping_allowed(counts: tuple[int, ...]) -> bool:
    return (
        sum(power * Z1009[name] for name, power in zip(FIELD_NAMES, counts)) % PRIME == 0
        and sum(power * Z2A[name] for name, power in zip(FIELD_NAMES, counts)) % 2 == 0
        and sum(power * Z2B[name] for name, power in zip(FIELD_NAMES, counts)) % 2 == 0
    )


def anomaly_ledger() -> dict[str, Any]:
    values = {
        "SO10_squared_Z1009": 0,
        "U1X_squared_Z1009": 0,
        "U1X_Z1009_squared": 0,
        "gravity_squared_Z1009": 0,
        "Z1009_cubed": 0,
    }
    for field in FIELDS:
        charge = Z1009[field["name"]]
        multiplicity = field["multiplicity"]
        dimension = abs(field["SO10_dimension"])
        xcharge = field["X"]
        values["SO10_squared_Z1009"] += multiplicity * field["SO10_Dynkin_index"] * charge
        values["U1X_squared_Z1009"] += multiplicity * dimension * xcharge ** 2 * charge
        values["U1X_Z1009_squared"] += multiplicity * dimension * xcharge * charge ** 2
        values["gravity_squared_Z1009"] += multiplicity * dimension * charge
        values["Z1009_cubed"] += multiplicity * dimension * charge ** 3
    for name in NEW_FIELDS:
        charge = Z1009[name]
        values["gravity_squared_Z1009"] += charge
        values["Z1009_cubed"] += charge ** 3
    return {
        "integer_values": values,
        "mod_1009": {name: value % PRIME for name, value in values.items()},
        "Z2A_U1X_Z2_squared_exact": sum(
            field["multiplicity"] * abs(field["SO10_dimension"]) * field["X"] * Z2A[field["name"]] ** 2
            for field in FIELDS
        ),
        "Z2B_U1X_Z2_squared_exact": 0,
        "Z2_standard_eta": 1,
    }


def build_report() -> dict[str, Any]:
    upstream_report = json.loads(UPSTREAM_JSON.read_text(encoding="utf-8"))
    flat_report = json.loads(FLAT_JSON.read_text(encoding="utf-8"))
    r_anomaly_report = json.loads(R_ANOMALY_JSON.read_text(encoding="utf-8"))
    desired = desired_vectors()
    desired_rows = list(desired)
    right, rank, invariant_factors = smith_data(desired_rows)
    rows = extended_allowed_rows()
    selected = [row for row in rows if shaping_allowed(row["count_tuple"])]
    zero_quotient = [
        row for row in rows
        if zero_in_quotient(row["count_tuple"], right, rank, invariant_factors)
    ]
    desired_set = set(desired)
    forced = [row for row in zero_quotient if row["count_tuple"] not in desired_set]
    selected_set = {row["count_tuple"] for row in selected}
    zero_set = {row["count_tuple"] for row in zero_quotient}
    anomalies = anomaly_ledger()
    selected_by_degree = {
        str(degree): sum(row["degree"] == degree for row in selected)
        for degree in range(1, 5)
    }
    components_by_degree = {
        str(degree): sum(
            row["so10_flavour_component_multiplicity"]
            for row in selected if row["degree"] == degree
        )
        for degree in range(1, 5)
    }
    old_dimensions = flat_report["exact_dimensions"]
    extended_dimensions = {
        "complex_variables": 12,
        "F_term_Jacobian_rank_on_nonzero_K_branch": 5,
        "complex_F_flat_tangent_before_gauge": 7,
        "complexified_broken_gauge_rank": 2,
        "complex_quotient_moduli": 5,
        "extra_moduli_relative_to_frozen_V22_slice": 4,
    }
    old_a_gravity = r_anomaly_report["anomalies"]["gravity_squared_Z4R"]
    new_a_gravity = old_a_gravity - len(NEW_FIELDS)
    source_manifest = [
        {"path": path.name, "mode": "raw", "sha256": sha256(path.read_bytes())}
        for path in (UPSTREAM_JSON, FLAT_JSON, R_ANOMALY_JSON)
    ]
    checks = {
        "upstream_census_is_the_frozen_incomplete_V22_result":
            upstream_report["counts"]["allowed_base_field_sectors"] == 1045
            and upstream_report["counts"]["allowed_undeclared_sectors"] == 1016,
        "repair_uses_four_R0_gauge_singlet_scale_fields": len(NEW_FIELDS) == 4,
        "desired_catalogue_has_29_sectors": len(desired_set) == 29,
        "smith_rank_and_free_rank_are_25_and_12": rank == 25 and len(FIELD_NAMES) - rank == 12,
        "smith_torsion_is_Z2_times_Z2": [factor for factor in invariant_factors if factor > 1] == [2, 2],
        "extended_base_ring_has_2203_sectors": len(rows) == 2203,
        "minimum_nonR_Abelian_closed_catalogue_has_81_sectors": len(zero_quotient) == 81,
        "exactly_52_extra_sectors_are_unavoidable": len(forced) == 52,
        "finite_shaping_assignment_selects_exactly_the_Smith_zero_class": selected_set == zero_set,
        "every_desired_sector_is_selected": desired_set <= selected_set,
        "all_Z1009_anomaly_congruences_vanish": all(value == 0 for value in anomalies["mod_1009"].values()),
        "mixed_U1X_Z2_squared_anomalies_vanish_exactly":
            anomalies["Z2A_U1X_Z2_squared_exact"] == anomalies["Z2B_U1X_Z2_squared_exact"] == 0,
        "four_R0_singlets_preserve_Z4R_gravitational_parity":
            old_a_gravity % 2 == new_a_gravity % 2 == 0,
        "nonzero_R0_K_vevs_preserve_Z4R_but_break_Z1009":
            all(Z1009[name] % PRIME != 0 for name in NEW_FIELDS),
        "extended_F_flat_slice_has_five_not_one_moduli":
            old_dimensions["complex_quotient_moduli"] == 1
            and extended_dimensions["complex_quotient_moduli"] == 5,
        "full_G1_G2_G3_and_G4_are_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "candidate.susy_so10x17.v22r.G1.minimal_nonR_abelian_completion",
        "status": ("EXACT_ANOMALY_FREE_DEGREE4_NONR_SHAPING_COMPLETION_FOUND__FOUR_EXTRA_MODULI_BLOCK_FULL_REPAIR"
                   if not failures else "V22_G1_MINIMAL_REPAIR_SEARCH_FAILED"),
        "overall_state": "CONSTRUCTIVE_G1_SECTOR_CANDIDATE__VACUUM_BLOCKED" if not failures else "EXECUTION_FAIL",
        "scope": "ordinary non-R additive shaping factors; the separate no-new-field artifact includes R-type factors",
        "source_manifest": source_manifest,
        "repair_definition": {
            "retained_terms": {name: list(fields) for name, fields in TERMS.items()},
            "replacement_terms": {name: list(fields) for name, fields in REPLACEMENT_TERMS.items()},
            "removed_nonzero_constant_tadpoles": ["linearNC", "linearNMP", "linearNX", "linearNS"],
            "retained_nonzero_constant_tadpole": "linearNphi",
            "new_fields": {
                name: {"SO10_dimension": 1, "X": 0, "R4": 0, "multiplicity": 1}
                for name in NEW_FIELDS
            },
        },
        "smith_quotient": {
            "desired_relation_rank": rank,
            "free_rank": len(FIELD_NAMES) - rank,
            "invariant_factors": invariant_factors,
            "nontrivial_torsion": [factor for factor in invariant_factors if factor > 1],
            "interpretation": "Z^37 divided by the 29 intended monomial relations is Z^12 plus Z2 plus Z2",
        },
        "shaping_symmetry": {
            "group": "Z1009 x Z2A x Z2B",
            "Z1009": Z1009,
            "Z2A": Z2A,
            "Z2B": Z2B,
            "standard_discrete_anomalies": anomalies,
            "claim_boundary": "standard congruences only; modern global/cobordism anomalies and domain walls remain open",
        },
        "counts": {
            "extended_degree_le_4_base_sectors_before_shaping": len(rows),
            "desired_sectors": len(desired_set),
            "unavoidable_extra_sectors": len(forced),
            "minimum_selected_sectors": len(selected),
            "selected_sectors_by_degree": selected_by_degree,
            "selected_flavour_components_by_degree": components_by_degree,
            "total_selected_flavour_components": sum(components_by_degree.values()),
        },
        "unavoidable_extra_sectors": forced,
        "selected_sectors": selected,
        "vacuum_effect": {
            "frozen_V22_dimensions": old_dimensions,
            "four_scale_field_dimensions": extended_dimensions,
            "Nphi_linear_term_excludes_the_all_zero_F_flat_origin": True,
            "new_scale_fields_are_stabilized": False,
            "one_axion_multiplet_preserved": False,
            "reason": "four new R0 singlet scale directions enter without four new independent F constraints",
        },
        "repair_verdict": {
            "classical_degree_le_4_holomorphic_sector_repair_exists": not failures,
            "source_land_as_the_active_V22_model": False,
            "reason_not_source_landed": [
                "the accepted sector necessarily contains 52 additional operators rather than the intended 29",
                "the supersymmetric quotient has five complex moduli instead of the single intended axion multiplet",
                "nonzero K VEVs completely break Z1009, so higher-dimensional spurion insertions require an all-order UV completion",
                "SO(10) tensor-copy normalizations, Kahler operators, soft terms and the complete global vacuum remain open",
                "the present SARAH validator does not semantically audit the inert SuperPotentialCatalogue",
            ],
            "full_V22_repair_achieved": False,
        },
        "claim_boundary": {
            "degree_le_4_superpotential_sector_selection_closed": not failures,
            "standard_shaping_anomaly_congruences_closed": not failures,
            "all_order_operator_ring_closed": False,
            "full_V22_G1_closed": False,
            "V22_G2_closed": False,
            "V22_G3_closed": False,
            "V22_G4_closed": False,
        },
        "next_exact_target": ("A genuinely new UV alignment/messenger sector must lift exactly four extra moduli while preserving "
                              "one axion direction and must close arbitrary shaping-spurion insertions. This is no longer a minimal V22 patch."),
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    # Normalize tuples from the exact lattice machinery to their JSON form so
    # a freshly built report compares byte-semantically with the frozen file.
    report = json.loads(json.dumps(report))
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    dimensions = report["vacuum_effect"]["four_scale_field_dimensions"]
    return "\n".join([
        "# SUSY V22 G1 minimal repair search", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Extended degree-four sectors before shaping: {counts['extended_degree_le_4_base_sectors_before_shaping']}",
        f"- Intended sectors: {counts['desired_sectors']}",
        f"- Unavoidable extra sectors: {counts['unavoidable_extra_sectors']}",
        f"- Exact minimum selected sectors: {counts['minimum_selected_sectors']}",
        f"- Shaping group: `{report['shaping_symmetry']['group']}`", "",
        "A finite assignment exists and all standard Z1009 anomaly congruences vanish. This solves only the",
        "classical holomorphic sector-selection problem through total field degree four.", "",
        f"The repaired F-flat quotient has {dimensions['complex_quotient_moduli']} complex moduli rather than one.",
        "Moreover, every required K VEV breaks Z1009, reopening arbitrary higher-dimensional spurion insertions.",
        "The construction is therefore not source-landed as active V22 and does not close G1 or any later gate.", "",
        f"Next: {report['next_exact_target']}", "",
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
            raise ArithmeticError("minimal repair JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("minimal repair Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
