#!/usr/bin/env python3
"""Exact V22 holomorphic superpotential census through field degree four.

The census treats chiral superfields as commuting variables.  Repeated copies
of one field therefore use symmetric powers of its SO(10) representation,
while different flavour copies tensor independently.  This is the distinction
that produces symmetric 10/126 Yukawa tensors and antisymmetric 120 Yukawas.

Only the symmetries actually declared by the V22 source are imposed:
SO(10) x U(1)_X and Z4R, with W carrying R charge two.  The result is compared
sector by sector with SuperPotentialCatalogue plus its five linear drivers.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import g1_exact_declared_symmetry_character_census_v20 as d5
from susy_so10x17_v22_contract import FIELDS, MODEL_PATH, TERMS


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.md"
SCHEMA = "susy_v22_g1_holomorphic_ring_frontier_v1"
MAX_DEGREE = 4
FIELD_NAMES = tuple(field["name"] for field in FIELDS)
FIELD_INDEX = {name: index for index, name in enumerate(FIELD_NAMES)}
FIELD_BY_NAME = {field["name"]: field for field in FIELDS}
LINEAR_DRIVERS = {
    "linearNphi": ("Nphi",),
    "linearNC": ("NC",),
    "linearNMP": ("NMP",),
    "linearNX": ("NX",),
    "linearNS": ("NS",),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def weak_compositions(total: int, slots: int) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, slots - 1):
            yield (first,) + rest


@lru_cache(None)
def r120() -> Counter[tuple[int, ...]]:
    return d5.exterior(list(d5.vector().elements()), 3)


@lru_cache(None)
def conjugate_spinor() -> Counter[tuple[int, ...]]:
    return Counter({tuple(-component for component in weight): multiplicity
                    for weight, multiplicity in d5.spinor().items()})


@lru_cache(None)
def irrep(dimension: int) -> Counter[tuple[int, ...]]:
    table = {
        1: lambda: Counter({d5.ZERO: 1}),
        10: d5.vector,
        16: d5.spinor,
        -16: conjugate_spinor,
        120: r120,
        126: d5.r126,
        -126: d5.r126b,
        210: d5.r210,
    }
    if dimension not in table:
        raise KeyError(f"unsupported SO(10) representation {dimension}")
    return table[dimension]()


@lru_cache(None)
def symmetric_irrep(dimension: int, power: int) -> Counter[tuple[int, ...]]:
    return d5.sym(irrep(dimension), power)


@lru_cache(None)
def singlet_for_species_key(key: tuple[tuple[int, int], ...]) -> int:
    factors = [symmetric_irrep(dimension, power)
               for dimension, power in key if abs(dimension) != 1]
    if not factors:
        return 1
    factors.sort(key=len)
    character = factors[0]
    for factor in factors[1:]:
        character = d5.tensor(character, factor)
    return d5.singlet(character)


def count_tuple(names: Iterable[str]) -> tuple[int, ...]:
    counts = [0] * len(FIELD_NAMES)
    for name in names:
        counts[FIELD_INDEX[name]] += 1
    return tuple(counts)


def monomial_label(counts: tuple[int, ...]) -> str:
    pieces = []
    for name, power in zip(FIELD_NAMES, counts):
        if power:
            pieces.append(name if power == 1 else f"{name}^{power}")
    return " ".join(pieces) or "1"


def charge_allowed(counts: tuple[int, ...]) -> bool:
    x_charge = sum(power * field["X"] for power, field in zip(counts, FIELDS))
    r_charge = sum(power * field["R4"] for power, field in zip(counts, FIELDS)) % 4
    return x_charge == 0 and r_charge == 2


def flavour_distributions(counts: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    """Yield representation/power keys for all unordered flavour monomials."""
    options: list[tuple[tuple[int, ...], ...]] = []
    active_fields: list[dict[str, Any]] = []
    for power, field in zip(counts, FIELDS):
        if not power:
            continue
        active_fields.append(field)
        options.append(tuple(weak_compositions(power, field["multiplicity"])))
    for distributions in itertools.product(*options):
        key = []
        for field, distribution in zip(active_fields, distributions):
            dimension = field["SO10_dimension"]
            key.extend((dimension, occupancy) for occupancy in distribution if occupancy)
        yield tuple(sorted(key))


def declared_catalogue() -> dict[tuple[int, ...], list[str]]:
    out: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for coupling, fields in {**LINEAR_DRIVERS, **TERMS}.items():
        out[count_tuple(fields)].append(coupling)
    return {key: sorted(value) for key, value in out.items()}


@lru_cache(None)
def census() -> tuple[dict[str, Any], ...]:
    declared = declared_catalogue()
    rows = []
    for degree in range(1, MAX_DEGREE + 1):
        for indices in itertools.combinations_with_replacement(range(len(FIELDS)), degree):
            counts = [0] * len(FIELDS)
            for index in indices:
                counts[index] += 1
            counts_tuple = tuple(counts)
            if not charge_allowed(counts_tuple):
                continue
            multiplicity = 0
            nonzero_flavour_monomials = 0
            histogram: Counter[int] = Counter()
            for species_key in flavour_distributions(counts_tuple):
                singlets = singlet_for_species_key(species_key)
                if singlets:
                    multiplicity += singlets
                    nonzero_flavour_monomials += 1
                    histogram[singlets] += 1
            if not multiplicity:
                continue
            couplings = declared.get(counts_tuple, [])
            rows.append({
                "count_tuple": list(counts_tuple),
                "counts": {name: power for name, power in zip(FIELD_NAMES, counts_tuple) if power},
                "degree": degree,
                "monomial": monomial_label(counts_tuple),
                "X_sum": 0,
                "R4_sum_mod_4": 2,
                "flavour_monomials_with_singlets": nonzero_flavour_monomials,
                "so10_flavour_component_multiplicity": multiplicity,
                "so10_multiplicity_histogram": {str(key): histogram[key] for key in sorted(histogram)},
                "declared_catalogue_couplings": couplings,
                "declared_sector": bool(couplings),
            })
    return tuple(rows)


def find_multiplicity(*names: str) -> int:
    target = count_tuple(names)
    row = next((row for row in census() if tuple(row["count_tuple"]) == target), None)
    return 0 if row is None else int(row["so10_flavour_component_multiplicity"])


def build_report() -> dict[str, Any]:
    rows = list(census())
    allowed = {tuple(row["count_tuple"]) for row in rows}
    declared = declared_catalogue()
    declared_set = set(declared)
    missing = [row for row in rows if not row["declared_sector"]]
    declared_but_forbidden = [
        {"monomial": monomial_label(key), "couplings": declared[key]}
        for key in sorted(declared_set - allowed, key=lambda item: (sum(item), item))
    ]
    declared_rows = [row for row in rows if row["declared_sector"]]
    sectors_by_degree = {
        str(degree): sum(row["degree"] == degree for row in rows)
        for degree in range(1, MAX_DEGREE + 1)
    }
    components_by_degree = {
        str(degree): sum(row["so10_flavour_component_multiplicity"]
                         for row in rows if row["degree"] == degree)
        for degree in range(1, MAX_DEGREE + 1)
    }
    anchors = {
        "dimensions": {
            "10": d5.cdim(irrep(10)), "16": d5.cdim(irrep(16)),
            "16bar": d5.cdim(irrep(-16)), "120": d5.cdim(irrep(120)),
            "126": d5.cdim(irrep(126)), "126bar": d5.cdim(irrep(-126)),
            "210": d5.cdim(irrep(210)),
        },
        "Sym2_16_x_10_singlets": d5.singlet(d5.tensor(d5.sym(irrep(16), 2), irrep(10))),
        "Sym2_16_x_120_singlets": d5.singlet(d5.tensor(d5.sym(irrep(16), 2), irrep(120))),
        "16_x_16_x_120_singlets": d5.singlet(d5.tensor(d5.tensor(irrep(16), irrep(16)), irrep(120))),
        "Sym2_16_x_126bar_singlets": d5.singlet(d5.tensor(d5.sym(irrep(16), 2), irrep(-126))),
        "F_F_H10m_components": find_multiplicity("F", "F", "H10m"),
        "F_F_T120m_components": find_multiplicity("F", "F", "T120m"),
        "XMP_F_F_DeltaB_components": find_multiplicity("XMP", "F", "F", "DeltaB"),
        "Splus_SpecS_SpecB_components": find_multiplicity("Splus", "SpecS", "SpecB"),
    }
    source_paths = {
        "contract_python": ROOT / "susy_so10x17_v22_contract.py",
        "D5_character_engine": ROOT / "g1_exact_declared_symmetry_character_census_v20.py",
        "SARAH_model": MODEL_PATH,
    }
    source_manifest = [
        {"role": role, "path": str(path.relative_to(ROOT)).replace("\\", "/"),
         "mode": "portable-lf", "sha256": sha256(portable_bytes(path))}
        for role, path in source_paths.items()
    ]
    checks = {
        "character_dimensions_are_exact": anchors["dimensions"] == {
            "10": 10, "16": 16, "16bar": 16, "120": 120,
            "126": 126, "126bar": 126, "210": 210,
        },
        "D5_Weyl_denominator_order_is_1920": sum(abs(value) for value in d5.offsets().values()) == 1920,
        "same_copy_spinors_select_symmetric_10_not_120":
            anchors["Sym2_16_x_10_singlets"] == 1 and anchors["Sym2_16_x_120_singlets"] == 0,
        "distinct_spinors_admit_one_120_contraction": anchors["16_x_16_x_120_singlets"] == 1,
        "same_copy_spinors_admit_one_126bar_contraction": anchors["Sym2_16_x_126bar_singlets"] == 1,
        "three_family_Yukawa_component_counts_are_6_3_6":
            (anchors["F_F_H10m_components"], anchors["F_F_T120m_components"],
             anchors["XMP_F_F_DeltaB_components"]) == (6, 3, 6),
        "five_by_five_spectator_Yukawa_has_25_components": anchors["Splus_SpecS_SpecB_components"] == 25,
        "every_declared_catalogue_sector_is_symmetry_and_SO10_allowed": not declared_but_forbidden,
        "every_row_is_X_neutral_and_R2": all(row["X_sum"] == 0 and row["R4_sum_mod_4"] == 2 for row in rows),
        "catalogue_incompleteness_is_exhibited_by_exact_witnesses": bool(missing),
        "no_full_V22_G1_closure_is_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    catalogue_complete = not missing and not declared_but_forbidden
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "canonical.susy_so10x17.v22.G1.holomorphic_degree_le_4",
        "status": ("EXACT_V22_HOLOMORPHIC_RING_CENSUS_CLOSED__DECLARED_CATALOGUE_INCOMPLETE"
                   if not failures and not catalogue_complete
                   else "EXACT_V22_HOLOMORPHIC_RING_CENSUS_COMPLETE"
                   if not failures else "V22_HOLOMORPHIC_RING_CENSUS_FAILED"),
        "overall_state": "OBSTRUCTION_LANDED" if not failures and not catalogue_complete else "CLOSED" if not failures else "EXECUTION_FAIL",
        "scope": {
            "operator_type": "holomorphic superpotential monomials",
            "field_degree": [1, MAX_DEGREE],
            "symmetries_imposed": ["SO(10)", "U(1)_X", "Z4R with R(W)=2 mod 4"],
            "flavour_treatment": "all 3/5/5 copies expanded; repeated identical copies use symmetric representation powers",
            "not_in_scope": ["Kahler operators", "soft operators", "SO(10) tensor normalizations", "component Clebsches"],
        },
        "source_manifest": source_manifest,
        "anchors": anchors,
        "counts": {
            "allowed_base_field_sectors": len(rows),
            "declared_base_field_sectors": len(declared_set),
            "declared_allowed_sectors": len(declared_rows),
            "allowed_undeclared_sectors": len(missing),
            "declared_but_forbidden_sectors": len(declared_but_forbidden),
            "allowed_sectors_by_degree": sectors_by_degree,
            "allowed_flavour_components_by_degree": components_by_degree,
            "total_allowed_flavour_components": sum(components_by_degree.values()),
        },
        "declared_but_forbidden": declared_but_forbidden,
        "allowed_undeclared_sectors": missing,
        "all_allowed_sectors": rows,
        "catalogue_verdict": {
            "complete_under_declared_symmetries": catalogue_complete,
            "result": ("The 24 named catalogue terms plus five linear drivers do not define the complete degree<=4 "
                       "holomorphic ring allowed by the declared source symmetries. Additional source-landed shaping "
                       "selection rules or the omitted operators are required before V22 G1 can close."),
            "first_exact_witness": None if not missing else missing[0]["monomial"],
        },
        "claim_boundary": {
            "degree_le_4_holomorphic_charge_and_character_census_closed": not failures,
            "declared_superpotential_catalogue_complete": catalogue_complete,
            "Kahler_and_soft_ring_closed": False,
            "tensor_normalizations_closed": False,
            "full_V22_G1_closed": False,
            "V22_G2_closed": False,
        },
        "next_exact_target": ("Find and source-land additional shaping symmetries that retain every declared sector while "
                              "forbidding every unwanted sector, then rerun this census before component Clebsch promotion."),
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    first = report["catalogue_verdict"]["first_exact_witness"]
    return "\n".join([
        "# SUSY V22 G1 holomorphic-ring frontier", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Exact allowed base-field sectors through degree four: {counts['allowed_base_field_sectors']}",
        f"- Declared allowed sectors: {counts['declared_allowed_sectors']}",
        f"- Allowed but undeclared sectors: {counts['allowed_undeclared_sectors']}",
        f"- First exact undeclared witness: `{first}`", "",
        report["catalogue_verdict"]["result"], "",
        "This closes the charge/flavour/character census only. It does not close the Kahler or soft rings,",
        "SO(10) tensor normalizations, component Clebsches, V22 G1, or any later full gate.", "",
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
            raise ArithmeticError("V22 G1 holomorphic-ring JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22 G1 holomorphic-ring Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
