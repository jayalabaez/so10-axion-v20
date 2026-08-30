#!/usr/bin/env python3
"""Exact first spurion-leakage frontier for the accepted V22R selector.

The degree<=4 V22R catalogue is selected by Z28R x Z2S.  XMP is a gauge
singlet with Z28R charge zero and odd Z2S parity, and the missing-partner
construction requires <XMP> != 0.  Multiplication by XMP therefore maps every
Z28R-allowed/Z2S-odd sector to a Z28R x Z2S allowed sector one degree higher.
This module freezes that exact map for the 82 torsion-only sectors already
present in the source V22 degree-four census.

The result is an all-order boundary, not a rejection of the Wilsonian EFT.
The first audited XMP-spurion leakage layer contains 67 source sectors at
degree five; it is not a complete degree-five census.  After XMP takes a VEV
they induce the corresponding degree-four operators.  The unbroken Z4R
remnant still forbids a direct light-light GUT mass block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_v22_g1_no_new_field_completion as completion
import susy_v22_g1_holomorphic_ring_frontier as ring


ROOT = Path(__file__).resolve().parent
COMPLETION_JSON = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"
RING_JSON = ROOT / "SUSY_V22_G1_HOLOMORPHIC_RING_FRONTIER.json"
OUT_JSON = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.md"
SCHEMA = "susy_v22r_broken_selector_spurion_frontier_v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def core_sha(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def z28_charge(counts: tuple[int, ...]) -> int:
    return sum(
        power * completion.Z28R[name]
        for name, power in zip(completion.FIELD_NAMES, counts)
    ) % 28


def z2s_charge(counts: tuple[int, ...]) -> int:
    return sum(
        power * int(name in completion.Z2S_ODD)
        for name, power in zip(completion.FIELD_NAMES, counts)
    ) % 2


def multiply_xmp(counts: tuple[int, ...]) -> tuple[int, ...]:
    result = list(counts)
    result[completion.FIELD_INDEX["XMP"]] += 1
    return tuple(result)


def build_report() -> dict[str, Any]:
    accepted = json.loads(COMPLETION_JSON.read_text(encoding="utf-8"))
    source = json.loads(RING_JSON.read_text(encoding="utf-8"))
    rows = source["all_allowed_sectors"]
    selected = {tuple(row["count_tuple"]) for row in accepted["selected_sectors"]}

    torsion_rows = [
        row for row in rows
        if z28_charge(tuple(row["count_tuple"])) == completion.Z28R_W
        and z2s_charge(tuple(row["count_tuple"])) == 1
    ]
    leakage = []
    for row in torsion_rows:
        original = tuple(row["count_tuple"])
        lifted = multiply_xmp(original)
        leakage.append({
            "source_degree": row["degree"],
            "lifted_degree": row["degree"] + 1,
            "source_monomial": row["monomial"],
            "lifted_monomial": ring.monomial_label(lifted),
            "source_count_tuple": list(original),
            "lifted_count_tuple": list(lifted),
            "so10_flavour_component_multiplicity": row["so10_flavour_component_multiplicity"],
            "source_Z28R": z28_charge(original),
            "source_Z2S": z2s_charge(original),
            "lifted_Z28R": z28_charge(lifted),
            "lifted_Z2S": z2s_charge(lifted),
            "lifted_is_inside_108_catalogue": lifted in selected,
        })

    audited_source_counts_by_degree = {
        str(degree): {
            "sectors": sum(row["degree"] == degree for row in torsion_rows),
            "components": sum(
                row["so10_flavour_component_multiplicity"]
                for row in torsion_rows if row["degree"] == degree
            ),
        }
        for degree in range(1, 5)
    }
    first_audited_leakage_layer_rows = [
        row for row in leakage if row["lifted_degree"] == 5
    ]
    lower_lifts = [row for row in leakage if row["lifted_degree"] <= 4]

    light_fields = ("H10m", "H10p", "T120m", "T120p")
    vev_fields = (
        "Phi210", "C16", "C16bar", "XMP", "Splus", "Sminus",
        "Phi17p", "Phi17m",
    )
    checks = {
        "accepted_completion_artifact_passes": accepted["n_failed"] == 0,
        "XMP_is_a_gauge_singlet_with_Z28R_zero_and_Z2S_odd":
            completion.Z28R["XMP"] == 0 and "XMP" in completion.Z2S_ODD,
        "exactly_82_torsion_only_source_sectors_are_identified": len(torsion_rows) == 82,
        "torsion_only_component_count_is_184":
            sum(row["so10_flavour_component_multiplicity"] for row in torsion_rows) == 184,
        "audited_XMP_spurion_source_degree_partition_is_7_8_67":
            audited_source_counts_by_degree == {
                "1": {"sectors": 0, "components": 0},
                "2": {"sectors": 7, "components": 7},
                "3": {"sectors": 8, "components": 17},
                "4": {"sectors": 67, "components": 160},
            },
        "multiplication_by_XMP_makes_every_torsion_sector_selector_allowed":
            all(row["lifted_Z28R"] == 2 and row["lifted_Z2S"] == 0 for row in leakage),
        "every_lift_through_degree_four_is_already_in_the_108_catalogue":
            len(lower_lifts) == 15 and all(row["lifted_is_inside_108_catalogue"] for row in lower_lifts),
        "first_audited_XMP_spurion_leakage_layer_has_67_sectors_and_160_components":
            len(first_audited_leakage_layer_rows) == 67
            and sum(
                row["so10_flavour_component_multiplicity"]
                for row in first_audited_leakage_layer_rows
            ) == 160
            and all(
                not row["lifted_is_inside_108_catalogue"]
                for row in first_audited_leakage_layer_rows
            ),
        "pure_global_VEV_stabilizer_contains_Z4R":
            all(completion.Z28R[name] % 4 == 0 for name in vev_fields),
        "Z4R_remnant_forbids_light_light_masses_with_any_VEV_insertions":
            all(completion.Z28R[name] % 4 == 0 for name in light_fields)
            and completion.Z28R_W % 4 == 2,
        "full_all_order_G1_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "accepted.susy_so10x17.v22r.G1.broken_selector_spurion_frontier",
        "status": (
            "V22R_FIRST_AUDITED_XMP_SPURION_LEAKAGE_LAYER__67_DEGREE5_SECTORS__"
            "NOT_COMPLETE_DEGREE5__Z4R_LIGHT_BLOCK_PROTECTED"
            if not failures else "V22R_BROKEN_SELECTOR_SPURION_AUDIT_FAILED"
        ),
        "overall_state": "EXACT_ALL_ORDER_BOUNDARY" if not failures else "EXECUTION_FAIL",
        "source_manifest": [
            {"path": COMPLETION_JSON.name, "mode": "raw", "sha256": sha256(COMPLETION_JSON.read_bytes())},
            {"path": RING_JSON.name, "mode": "raw", "sha256": sha256(RING_JSON.read_bytes())},
        ],
        "spurion": {
            "field": "XMP",
            "SO10": 1,
            "U1X": 0,
            "Z28R": completion.Z28R["XMP"],
            "Z2S": 1,
            "required_nonzero_VEV": True,
            "effect": (
                "breaks Z2S; the pure-global VEV stabilizer contains Z4R, while the larger "
                "gauge-compensated diagonal stabilizer is a separate vacuum-embedding question"
            ),
        },
        "audited_XMP_spurion_source_counts_by_degree": audited_source_counts_by_degree,
        "first_audited_XMP_spurion_leakage_layer": {
            "source_degree": 5,
            "sectors": len(first_audited_leakage_layer_rows),
            "so10_flavour_components": sum(
                row["so10_flavour_component_multiplicity"]
                for row in first_audited_leakage_layer_rows
            ),
            "complete_degree_five_census": False,
            "induced_effect_after_XMP_VEV": (
                "the 67 sectors in the first audited XMP-spurion leakage layer reappear as "
                "degree-four operators with coefficients suppressed by <XMP>/M"
            ),
        },
        "all_82_exact_lifts": leakage,
        "physics_verdict": {
            "degree_le_4_108_sector_selection_remains_exact": not failures,
            "finite_108_sector_catalogue_is_all_order_closed": False,
            "Wilsonian_spurion_completion_required": True,
            "direct_light_light_GUT_mass_block_remains_forbidden_by_the_retained_Z4R_subgroup": not failures,
            "implication": (
                "V22R can be used as a degree-four EFT truncation, but full G1 requires the infinite "
                "spurion tower or a UV selection mechanism and coefficient power counting."
            ),
        },
        "claim_boundary": {
            "first_audited_XMP_spurion_leakage_layer_closed": not failures,
            "complete_degree_five_census_closed": False,
            "all_order_holomorphic_ring_closed": False,
            "Kahler_and_soft_rings_closed": False,
            "full_V22R_G1_closed": False,
            "scoped_missing_partner_light_block_protection_survives": not failures,
            "full_gauge_compensated_discrete_vacuum_stabilizer_closed_here": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = core_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    frontier = report["first_audited_XMP_spurion_leakage_layer"]
    return "\n".join([
        "# SUSY V22R broken-selector spurion frontier", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Exact Z28R-allowed/Z2S-odd sectors through degree four: `82`.",
        f"- First audited XMP-spurion leakage layer: `{frontier['sectors']}` degree-five sectors "
        f"with `{frontier['so10_flavour_components']}` SO(10)-and-flavour components.",
        "- Complete degree-five census: `false`.", "",
        "Because XMP is a Z28R-neutral, Z2S-odd gauge singlet with a required nonzero VEV,",
        "multiplying by XMP makes every torsion-only sector allowed. The 108-sector catalogue",
        "is therefore exact only as a degree-four EFT truncation, not as an all-order finite ring.", "",
        "The surviving Z4R still forbids light-light GUT mass terms for arbitrary insertions of",
        "the declared VEV fields. Full G1 nevertheless remains open until the Wilsonian spurion,",
        "Kahler, soft, tensor-normalization, and UV-selection contracts are supplied.", "",
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
            raise ArithmeticError("V22R spurion-frontier JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R spurion-frontier Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
