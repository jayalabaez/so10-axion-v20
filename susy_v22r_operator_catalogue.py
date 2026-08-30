#!/usr/bin/env python3
"""Generate the source-exact V22R degree-four operator catalogue and model.

V22R is the no-new-field completion of the V22 candidate.  It retains the
24 named V22 sectors and five linear drivers, accepts the 79 sectors that are
unavoidable under every additive Abelian shaping symmetry, and lands the
finite Z28R x Z2S selector that forbids every other sector in the frozen V22
degree<=4 holomorphic census.

The generated SARAH source contains the complete 108-entry *base-sector*
catalogue as Mathematica data.  It deliberately does not invent the 265
individual SO(10)/flavour tensor contractions or promote them into an
executable SARAH SuperPotential.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import susy_so10x17_v22_contract as v22
import susy_v22_g1_no_new_field_completion as completion


ROOT = Path(__file__).resolve().parent
UPSTREAM_JSON = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"
COMPLETION_JSON = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"
SPURION_FRONTIER_JSON = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json"
OUT_JSON = ROOT / "SUSY_V22R_OPERATOR_CATALOGUE.json"
MODEL_DIR = ROOT / "models/SO10X17SUSYV22R"
MODEL_PATH = MODEL_DIR / "SO10X17SUSYV22R.m"
SCHEMA = "susy_v22r_operator_catalogue_v1"

FIELD_NAMES = tuple(field["name"] for field in v22.FIELDS)
FIELD_INDEX = {name: index for index, name in enumerate(FIELD_NAMES)}
FIELD_BY_NAME = {field["name"]: field for field in v22.FIELDS}

# CRT combination of the source Z4R charges and the anomaly-free Z7R
# selector.  The superpotential has charge two in every representation.
Z7R_VECTOR = tuple(completion.Z7R[name] for name in FIELD_NAMES)
Z28R_VECTOR = tuple(completion.Z28R[name] for name in FIELD_NAMES)

# An integer U(1)R lift that is selection-equivalent to Z28R on the frozen
# degree<=4 census.  It is used only as a SARAH-friendly encoding there; at
# higher degree, sums differing by +/-28 make the finite Python/JSON ledger
# authoritative.  No new continuous gauge/global symmetry is claimed.
SARAH_R_LIFT_VECTOR = (
    1, 1, 1, 9, 25, 9, -23, -31, 25, 0, 0, 2, 10, -8, 0, -8,
    0, -8, -32, 32, -24, 24, 2, 2, 0, 24, -24, 2, 20, 2, 2, 12, 12,
)

Z2S_ODD = completion.Z2S_ODD
RPARITY_ODD = frozenset({"F", "P", "R", "SpecS", "SpecB", "Q", "Pbar", "Qbar", "Rbar"})
LINEAR_DRIVERS = completion.LINEAR_TERMS

SARAH_COMPONENT_SYMBOL = {
    "F": "f16", "P": "p16", "R": "r16", "SpecS": "s16", "SpecB": "b16bar",
    "Q": "q16", "Pbar": "pbar16", "Qbar": "qbar16", "Rbar": "rbar16",
    "Phi210": "phi210", "DeltaB": "deltaB", "Delta": "delta", "DeltaB2": "deltaB2",
    "Delta2": "delta2", "H10m": "h10m", "H10p": "h10p", "T120m": "t120m",
    "T120p": "t120p", "Splus": "splus", "Sminus": "sminus", "Phi17p": "phi17p",
    "Phi17m": "phi17m", "NX": "nx", "NS": "ns", "XMP": "xmp", "C16": "c16",
    "C16bar": "c16bar", "Nphi": "nphi", "Z0": "z0", "NC": "nc", "NMP": "nmp",
    "Z1": "z1", "Z2": "z2",
}

DIRECT_MISSING_PARTNER_EXTRAS = frozenset({
    ("Phi210", "Phi210", "Delta", "H10m"),
    ("Phi210", "Phi210", "Delta", "T120m"),
    ("Phi210", "Phi210", "DeltaB2", "H10p"),
    ("Phi210", "Phi210", "DeltaB2", "T120p"),
    ("Phi210", "XMP", "DeltaB", "Delta"),
    ("Phi210", "XMP", "DeltaB2", "Delta2"),
    ("C16bar", "C16", "Delta", "H10m"),
    ("C16bar", "C16", "Delta", "T120m"),
    ("C16bar", "C16", "DeltaB2", "H10p"),
    ("C16bar", "C16", "DeltaB2", "T120p"),
})


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def expanded_fields(count_tuple: Iterable[int]) -> tuple[str, ...]:
    return tuple(
        name
        for name, power in zip(FIELD_NAMES, count_tuple)
        for _ in range(int(power))
    )


def canonical_field_multiset(fields: Iterable[str]) -> tuple[str, ...]:
    counts = {name: 0 for name in FIELD_NAMES}
    for name in fields:
        counts[name] += 1
    return tuple(name for name in FIELD_NAMES for _ in range(counts[name]))


def original_sector_map() -> dict[tuple[str, ...], list[str]]:
    out: dict[tuple[str, ...], list[str]] = {}
    for coupling, fields in {**LINEAR_DRIVERS, **v22.TERMS}.items():
        out.setdefault(canonical_field_multiset(fields), []).append(coupling)
    return {key: sorted(value) for key, value in out.items()}


def charge_sum(fields: Iterable[str], vector: tuple[int, ...], modulus: int | None = None) -> int:
    total = sum(vector[FIELD_INDEX[name]] for name in fields)
    return total if modulus is None else total % modulus


def z2s_sum(fields: Iterable[str]) -> int:
    return sum(name in Z2S_ODD for name in fields) % 2


def rparity_sum(fields: Iterable[str]) -> int:
    return sum(name in RPARITY_ODD for name in fields) % 2


def selected(fields: Iterable[str]) -> bool:
    fields = tuple(fields)
    return charge_sum(fields, Z28R_VECTOR, 28) == 2 and z2s_sum(fields) == 0


def direct_mp_extra(fields: Iterable[str]) -> bool:
    return canonical_field_multiset(fields) in {
        canonical_field_multiset(row) for row in DIRECT_MISSING_PARTNER_EXTRAS
    }


def load_core_checked(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    body = dict(report)
    frozen_core = body.pop("core_sha256")
    if sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()) != frozen_core:
        raise ArithmeticError(f"invalid canonical core hash in {path.name}")
    return report


def load_upstream() -> dict[str, Any]:
    report = load_core_checked(UPSTREAM_JSON)
    if report["counts"]["allowed_base_field_sectors"] != 1045:
        raise ArithmeticError("upstream V22 sector count drifted")
    return report


def build_catalogue() -> dict[str, Any]:
    upstream = load_upstream()
    completion_report = load_core_checked(COMPLETION_JSON)
    spurion_frontier = load_core_checked(SPURION_FRONTIER_JSON)
    original = original_sector_map()
    selected_rows = []
    rejected_count = 0
    for upstream_row in upstream["all_allowed_sectors"]:
        fields = expanded_fields(upstream_row["count_tuple"])
        if not selected(fields):
            rejected_count += 1
            continue
        couplings = original.get(fields, [])
        selected_rows.append({
            "sector_id": f"V22R-S{len(selected_rows) + 1:03d}",
            "count_tuple": list(upstream_row["count_tuple"]),
            "counts": dict(upstream_row["counts"]),
            "fields": list(fields),
            "degree": int(upstream_row["degree"]),
            "monomial": upstream_row["monomial"],
            "Z28R_sum_mod_28": charge_sum(fields, Z28R_VECTOR, 28),
            "Z2S_sum_mod_2": z2s_sum(fields),
            "RParity_sum_mod_2": rparity_sum(fields),
            "SARAH_R_lift_sum": charge_sum(fields, SARAH_R_LIFT_VECTOR),
            "so10_flavour_component_multiplicity": int(upstream_row["so10_flavour_component_multiplicity"]),
            "so10_multiplicity_histogram": dict(upstream_row["so10_multiplicity_histogram"]),
            "provenance": "retained_v22_29" if couplings else "abelian_forced_completion_79",
            "v22_couplings": couplings,
            "direct_missing_partner_deformation": direct_mp_extra(fields),
        })

    retained = [row for row in selected_rows if row["provenance"] == "retained_v22_29"]
    forced = [row for row in selected_rows if row["provenance"] == "abelian_forced_completion_79"]
    component_count = sum(row["so10_flavour_component_multiplicity"] for row in selected_rows)
    forced_component_count = sum(row["so10_flavour_component_multiplicity"] for row in forced)
    completion_selected = {
        tuple(row["count_tuple"]) for row in completion_report["selected_sectors"]
    }
    landed_selected = {tuple(row["count_tuple"]) for row in selected_rows}
    sarah_lift_selected = {
        tuple(row["count_tuple"])
        for row in upstream["all_allowed_sectors"]
        if charge_sum(expanded_fields(row["count_tuple"]), SARAH_R_LIFT_VECTOR) == 2
        and z2s_sum(expanded_fields(row["count_tuple"])) == 0
    }
    by_degree = {
        str(degree): sum(row["degree"] == degree for row in selected_rows)
        for degree in range(1, 5)
    }
    components_by_degree = {
        str(degree): sum(
            row["so10_flavour_component_multiplicity"]
            for row in selected_rows if row["degree"] == degree
        )
        for degree in range(1, 5)
    }
    charge_rows = []
    for index, field in enumerate(v22.FIELDS):
        name = field["name"]
        charge_rows.append({
            "name": name,
            "multiplicity": field["multiplicity"],
            "SO10_dimension": field["SO10_dimension"],
            "X": field["X"],
            "Z17": field["Z17"],
            "RParity_mod_2": int(name in RPARITY_ODD),
            "Z4R": field["R4"],
            "Z7R": Z7R_VECTOR[index],
            "Z28R": Z28R_VECTOR[index],
            "Z2S": int(name in Z2S_ODD),
            "SARAH_R_integer_lift": SARAH_R_LIFT_VECTOR[index],
        })

    checks = {
        "field_vectors_cover_the_unchanged_33_field_source":
            len(FIELD_NAMES) == len(Z7R_VECTOR) == len(Z28R_VECTOR) == len(SARAH_R_LIFT_VECTOR) == 33,
        "Z28R_is_the_CRT_combination_of_Z4R_and_Z7R": all(
            q28 % 4 == field["R4"] and q28 % 7 == q7
            for field, q7, q28 in zip(v22.FIELDS, Z7R_VECTOR, Z28R_VECTOR)
        ),
        "exactly_108_base_sectors_are_selected": len(selected_rows) == 108,
        "all_29_V22_sectors_are_retained": len(retained) == 29 and set(original) == {tuple(row["fields"]) for row in retained},
        "exactly_79_Abelian_forced_sectors_are_added": len(forced) == 79,
        "exactly_937_upstream_sectors_are_rejected": rejected_count == 937,
        "selected_sector_degree_distribution_is_5_0_53_50": by_degree == {"1": 5, "2": 0, "3": 53, "4": 50},
        "selected_component_count_is_265": component_count == 265,
        "forced_component_count_is_194": forced_component_count == 194,
        "every_selected_sector_has_Z28R_W_charge_two_and_even_Z2S": all(
            row["Z28R_sum_mod_28"] == 2 and row["Z2S_sum_mod_2"] == 0
            for row in selected_rows
        ),
        "SARAH_integer_lift_selects_every_landed_sector_exactly": all(
            row["SARAH_R_lift_sum"] == 2 for row in selected_rows
        ),
        "SARAH_integer_lift_plus_Z2S_selects_exactly_the_same_108_degree4_sectors":
            sarah_lift_selected == landed_selected and len(sarah_lift_selected) == 108,
        "source_RParity_is_automatically_even_on_every_landed_sector": all(
            row["RParity_sum_mod_2"] == 0 for row in selected_rows
        ),
        "ten_direct_missing_partner_deformations_are_landed": sum(
            row["direct_missing_partner_deformation"] for row in forced
        ) == 10,
        "accepted_no_new_field_completion_is_reproduced_exactly":
            {tuple(row["count_tuple"]) for row in selected_rows} == completion_selected,
        "first_audited_XMP_spurion_leakage_layer_is_pinned":
            spurion_frontier["n_failed"] == 0
            and spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["sectors"] == 67
            and spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["so10_flavour_components"] == 160
            and not spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["complete_degree_five_census"],
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "canonical.susy_so10x17.v22r.G1.base_sector_catalogue",
        "status": (
            "V22R_EXACT_108_BASE_SECTOR_CATALOGUE_LANDED__265_COMPONENT_REALIZATION_OPEN"
            if not failures else "V22R_OPERATOR_CATALOGUE_GENERATION_FAILED"
        ),
        "source_model_id": "SO10X17SUSYV22R",
        "upstream": {
            "path": UPSTREAM_JSON.name,
            "core_sha256": upstream["core_sha256"],
            "allowed_base_field_sectors": upstream["counts"]["allowed_base_field_sectors"],
            "accepted_completion_path": COMPLETION_JSON.name,
            "accepted_completion_core_sha256": completion_report["core_sha256"],
        },
        "scope": {
            "operator_type": "holomorphic superpotential base-field monomials",
            "field_degree": [1, 4],
            "EFT_interpretation": "exact Wilsonian degree-four truncation",
            "all_order_finite_catalogue": False,
            "reason": (
                "the required odd-Z2S XMP VEV opens a Wilsonian tower; the 67-sector count is "
                "only the first audited XMP-spurion leakage layer, not a complete degree-five census"
            ),
        },
        "all_order_boundary": {
            "path": SPURION_FRONTIER_JSON.name,
            "core_sha256": spurion_frontier["core_sha256"],
            "Z2S_odd_sectors_through_degree_four": 82,
            "lifts_already_inside_degree_four_catalogue": 15,
            "first_audited_XMP_spurion_leakage_layer": {
                "source_degree": 5,
                "sectors": 67,
                "so10_flavour_components": 160,
                "complete_degree_five_census": False,
            },
            "unbroken_Z4R_light_block_protection_survives": True,
        },
        "symmetry": {
            "finite_R": {"name": "Z28R", "order": 28, "superpotential_charge": 2},
            "selector": {"name": "Z2S", "order": 2, "superpotential_charge": 0},
            "field_charges": charge_rows,
        },
        "counts": {
            "source_fields": len(FIELD_NAMES),
            "selected_base_sectors": len(selected_rows),
            "retained_v22_base_sectors": len(retained),
            "forced_completion_base_sectors": len(forced),
            "rejected_upstream_base_sectors": rejected_count,
            "selected_sectors_by_degree": by_degree,
            "selected_so10_flavour_components_by_degree": components_by_degree,
            "selected_so10_flavour_components": component_count,
            "forced_completion_so10_flavour_components": forced_component_count,
            "SARAH_integer_lift_plus_Z2S_selected_degree4_sectors": len(sarah_lift_selected),
            "direct_missing_partner_deformation_sectors": sum(
                row["direct_missing_partner_deformation"] for row in forced
            ),
        },
        "operator_sectors": selected_rows,
        "claim_boundary": {
            "degree_le_4_base_sector_catalogue_complete": not failures,
            "so10_flavour_component_count_closed": not failures,
            "individual_tensor_contractions_source_landed": False,
            "component_Clebsches_closed": False,
            "SARAH_executable_108_sector_superpotential_landed": False,
            "all_order_holomorphic_catalogue_closed": False,
            "broken_Z2S_spurion_tower_closed": False,
            "vacuum_revalidated": False,
            "missing_partner_rank_revalidated": False,
            "full_V22R_G1_closed": False,
            "V22R_G2_closed": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def mathematica_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_model(catalogue: dict[str, Any]) -> str:
    lines = [
        "(* ==================================================================== *)",
        "(* Active V22R source completion of SO10X17SUSYV22.                   *)",
        "(* Exact scope: 33 unchanged fields and 108 holomorphic base sectors *)",
        "(* through field degree four, selected by Z28R x Z2S.                *)",
        "(* The 265 SO(10)/flavour components are counted but their tensor     *)",
        "(* contractions and Clebsches are NOT encoded in SuperPotential.      *)",
        "(* ==================================================================== *)",
        "",
        "Off[General::spell];",
        "",
        'Model`Name = "SO10X17SUSYV22R";',
        'Model`NameLaTeX = "SUSY SO(10) x U(1)_X V22R exact base-sector completion";',
        'Model`Authors = "SO10 axion V22R verified completion";',
        'Model`Date = "2026-08-19";',
        "",
        "Global[[1]] = {Z[2], RParity};",
        "Global[[2]] = {Z[17], Z17};",
        "Global[[3]] = {Z[2], Z2S};",
        "Global[[4]] = {U[1], RSymmetry};",
        "RpM = {-1, -1, 1};",
        "RpP = {1, 1, -1};",
        "Z2SEven = 1;",
        "Z2SOdd = -1;",
        "",
        "(* The continuous RSymmetry slot is an integer lift used by SARAH.   *)",
        "(* It is faithful only on the frozen degree<=4 census. At higher     *)",
        "(* degree, finite Z28R data and the Python/JSON ledger are binding.  *)",
        "(* No physical continuous U(1)R is declared; finite Z28R has W=2.   *)",
        f'V22RFiniteSymmetry = <|"RGroup" -> "Z28R", "ROrder" -> 28, "WCharge" -> 2, "Selector" -> "Z2S"|>;',
        f'V22ROperatorCatalogueCore = "{catalogue["core_sha256"]}";',
        "",
        "Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, RpM, 1, Z2SEven, {0,1,0}};",
        "Gauge[[2]] = {GX, U[1], xcharge, gX, False, RpM, 1, Z2SEven, {0,1,0}};",
        "",
    ]
    for number, (field, r_lift) in enumerate(zip(v22.FIELDS, SARAH_R_LIFT_VECTOR), start=1):
        name = field["name"]
        parity = "RpM" if name in RPARITY_ODD else "RpP"
        z17 = "1" if field["Z17"] == 0 else f"Exp[2*Pi*I*{field['Z17']}/17]"
        z2s = "Z2SOdd" if name in Z2S_ODD else "Z2SEven"
        lines.append(
            f"SuperFields[[{number}]] = {{{name}, {field['multiplicity']}, {SARAH_COMPONENT_SYMBOL[name]}, "
            f"{field['SO10_dimension']}, {field['X']}, {parity}, {z17}, {z2s}, "
            f"{{{r_lift},{r_lift},{r_lift - 1}}}}};"
        )
    lines.extend([
        "",
        "(* Complete machine-readable degree<=4 base-sector catalogue.       *)",
        "(* Components gives the exact SO(10) x flavour invariant count.     *)",
        "V22RBaseSectorCatalogue = {",
    ])
    for index, row in enumerate(catalogue["operator_sectors"]):
        fields = ", ".join(row["fields"])
        coupling_strings = ", ".join(mathematica_string(value) for value in row["v22_couplings"])
        comma = "," if index + 1 < len(catalogue["operator_sectors"]) else ""
        lines.append(
            "  <|"
            f'"ID" -> "{row["sector_id"]}", '
            f'"Fields" -> {{{fields}}}, '
            f'"Degree" -> {row["degree"]}, '
            f'"Components" -> {row["so10_flavour_component_multiplicity"]}, '
            f'"Provenance" -> "{row["provenance"]}", '
            f'"V22Couplings" -> {{{coupling_strings}}}'
            f"|>{comma}"
        )
    lines.extend([
        "};",
        "",
        "(* No component polynomial is asserted.  Downstream G1/G2 work must *)",
        "(* source-land normalized invariant tensors before replacing zero.   *)",
        "SuperPotential = 0;",
        "NameOfStates = {GaugeES};",
        "",
    ])
    return "\n".join(lines)


def write_outputs(catalogue: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(catalogue, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(render_model(catalogue), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalogue = build_catalogue()
    if args.write:
        write_outputs(catalogue)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != catalogue:
            raise ArithmeticError("V22R operator catalogue JSON drifted")
        if MODEL_PATH.read_text(encoding="utf-8") != render_model(catalogue):
            raise ArithmeticError("V22R SARAH source drifted")
    print(catalogue["status"])
    print(catalogue["core_sha256"])
    print(json.dumps(catalogue["counts"], sort_keys=True))
    return 0 if catalogue["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
