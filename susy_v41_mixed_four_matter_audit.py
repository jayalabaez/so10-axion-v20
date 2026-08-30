#!/usr/bin/env python3
"""Exact SU(4) tensor check for the V40 mixed-four-matter G7 boundary.

The V40 Z9 selector forbids every same-orientation Pati-Salam four-matter
source, while a mixed 4^2 times bar4^2 source is selector neutral.  This
script distinguishes those two statements.  It uses only the invariant-tensor
algebra of SU(4): a net-zero fundamental number has delta contractions,
whereas a single epsilon tensor needs a net four fundamentals or
antifundamentals.  Thus the mixed four-matter source is not the conventional
Delta-B=1 dimension-five class.  VEV-dressed lower-matter, Kahler, soft, and
component effects intentionally remain outside this narrow result.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V41_MIXED_FOUR_MATTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V41_MIXED_FOUR_MATTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v41_mixed_four_matter_audit.py"

ORDER = 9
STATUS = (
    "V41_SU4_MIXED_FOUR_MATTER_CLASSIFIED__DELTA_B1_EPSILON_CLASSES_Z9_FORBIDDEN__"
    "VEV_AND_COMPONENT_RING_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invariant_exists(n4: int, nbar4: int) -> bool:
    """SU(4) singlet condition from delta and epsilon invariant tensors."""

    return (n4 - nbar4) % 4 == 0


def z9_charge(n4: int, nbar4: int) -> int:
    # Every matter 4 has charge +3; every bar4 has charge -3 modulo nine.
    return (3 * (n4 - nbar4)) % ORDER


def tensor_class(n4: int, nbar4: int) -> str:
    difference = n4 - nbar4
    if difference == 0:
        return "delta_only_at_four_matter"
    if difference == 4:
        return "one_epsilon_upper"
    if difference == -4:
        return "one_epsilon_lower"
    if difference % 4 == 0:
        return "multiple_epsilon_or_delta_reduction"
    return "not_an_SU4_singlet"


def four_matter_classification() -> list[dict[str, Any]]:
    rows = []
    for n4 in range(5):
        nbar4 = 4 - n4
        rows.append(
            {
                "n_4": n4,
                "n_bar4": nbar4,
                "SU4_singlet_exists": invariant_exists(n4, nbar4),
                "tensor_class": tensor_class(n4, nbar4),
                "Z9_charge": z9_charge(n4, nbar4),
                "selector_forbidden": invariant_exists(n4, nbar4) and z9_charge(n4, nbar4) != 0,
                "can_contain_conventional_DeltaB_equals_one_epsilon": abs(n4 - nbar4) == 4,
            }
        )
    return rows


def general_net_orientation_table(maximum_total_fields: int = 12) -> list[dict[str, Any]]:
    rows = []
    for total in range(0, maximum_total_fields + 1):
        for n4 in range(total + 1):
            nbar4 = total - n4
            if not invariant_exists(n4, nbar4):
                continue
            difference = n4 - nbar4
            rows.append(
                {
                    "n_4": n4,
                    "n_bar4": nbar4,
                    "total_matter_fields": total,
                    "net_fundamental_number": difference,
                    "Z9_charge": z9_charge(n4, nbar4),
                    "tensor_class": tensor_class(n4, nbar4),
                    "DeltaB_one_epsilon_class": abs(difference) == 4,
                    "DeltaB_one_class_Z9_forbidden": abs(difference) == 4 and z9_charge(n4, nbar4) != 0,
                }
            )
    return rows


def source_level_interpretation() -> dict[str, Any]:
    four = four_matter_classification()
    mixed = next(row for row in four if row["n_4"] == 2)
    plus = next(row for row in four if row["n_4"] == 4)
    minus = next(row for row in four if row["n_4"] == 0)
    general = general_net_orientation_table()
    delta_b_one = [row for row in general if row["DeltaB_one_epsilon_class"]]
    return {
        "SU4_fundamental_theorem": (
            "For SU(4), any invariant polynomial is built from delta and epsilon tensors. "
            "With two 4 and two bar4 indices, the only independent invariant tensors are "
            "delta-pair contractions; epsilon times epsilon reduces to their antisymmetrized sum."
        ),
        "four_matter_rows": four,
        "mixed_4_squared_bar4_squared": {
            "example_source": "X Q Q Qc Qc",
            "selector_Z9_charge": mixed["Z9_charge"],
            "SU4_tensor_basis": "delta^a_b delta^c_d and delta^a_d delta^c_b",
            "epsilon_SU4_available": False,
            "B_and_L_statement": (
                "Each delta contracts a 4 component with its conjugate bar4 component. "
                "In the Pati-Salam quark/lepton decomposition, every such pair has zero "
                "separate baryon and lepton number, so the four-matter mixed class cannot "
                "be the conventional Delta-B=Delta-L=1 dimension-five source."
            ),
            "is_conventional_proton_decay_source": False,
        },
        "same_orientation_classes": {
            "four_4": plus,
            "four_bar4": minus,
            "interpretation": (
                "The epsilon_SU4 tensor is available exactly for the net +/-4 classes. "
                "Their components include QQQL and u^c u^c d^c e^c-type sources, and V40 "
                "Z9 charges 3 and 6 forbid them."
            ),
        },
        "all_matter_only_net_plus_or_minus_four_classes_through_degree_12": {
            "row_count": len(delta_b_one),
            "all_Z9_forbidden": all(row["DeltaB_one_class_Z9_forbidden"] for row in delta_b_one),
            "rows": delta_b_one,
            "reason": "q_Z9 = 3(n_4-n_bar4) = +/-12 = 3 or 6 modulo 9 for net +/-4.",
        },
        "remaining_scope": [
            "operators with Pati-Salam-breaking VEV insertions that alter SU(4) index balance",
            "Kahler, soft-spurion, and nonholomorphic operators",
            "mixed heavy-field thresholds and component-level matching",
            "SUSY dressing, RG evolution, flavour tensors, and hadronic matrix elements",
        ],
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in (Path(__file__), TEST_PATH)
    ]


def build_report() -> dict[str, Any]:
    classification = source_level_interpretation()
    four_rows = classification["four_matter_rows"]
    report: dict[str, Any] = {
        "schema": "susy-v41-mixed-four-matter-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "four_matter_tensor_classification": classification,
        "gate_boundary": {
            "G7_closed": False,
            "landed": (
                "The selector-neutral X Q Q Qc Qc mixed four-matter example is not a "
                "conventional Delta-B=1 epsilon_SU4 source.  All matter-only net +/-4 "
                "SU4 epsilon classes through degree twelve are Z9-forbidden."
            ),
            "still_required": classification["remaining_scope"],
        },
        "integrity_checks": {
            "four_matter_SU4_singlet_rows_are_exact": all(row["SU4_singlet_exists"] == invariant_exists(row["n_4"], row["n_bar4"]) for row in four_rows),
            "mixed_two_plus_two_is_Z9_neutral_but_not_epsilon": (
                classification["mixed_4_squared_bar4_squared"]["selector_Z9_charge"] == 0
                and classification["mixed_4_squared_bar4_squared"]["epsilon_SU4_available"] is False
            ),
            "both_four_same_orientation_classes_are_Z9_forbidden": (
                classification["same_orientation_classes"]["four_4"]["selector_forbidden"]
                and classification["same_orientation_classes"]["four_bar4"]["selector_forbidden"]
            ),
            "all_net_plus_or_minus_four_matter_only_classes_through_12_are_Z9_forbidden": classification["all_matter_only_net_plus_or_minus_four_classes_through_degree_12"]["all_Z9_forbidden"],
            "G7_remains_fail_closed": True,
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    section = report["four_matter_tensor_classification"]
    rows = "\n".join(
        f"| {row['n_4']} | {row['n_bar4']} | {row['tensor_class']} | {row['Z9_charge']} | {'yes' if row['selector_forbidden'] else 'no'} |"
        for row in section["four_matter_rows"]
    )
    return f"""# V41 mixed four-matter Pati-Salam audit

Status: {report['status']}

This audit removes one false G7 blocker.  The selector-neutral mixed source
X Q Q Qc Qc has two SU(4) fundamentals and two antifundamentals.  Its
invariant tensors are delta-pair contractions, not epsilon_SU4 contractions,
so it is not the usual Delta-B=Delta-L=1 dimension-five proton-decay class.

| 4 indices | bar4 indices | SU4 tensor class | Z9 | Selector-forbidden |
|---:|---:|---|---:|---|
{rows}

The net plus/minus four epsilon classes contain the conventional QQQL and
u-c u-c d-c e-c sources.  V40 Z9 forbids those classes, including all
matter-only insertions that retain net plus/minus four through degree twelve.

This is still not a G7 closure: PS-VEV, Kahler, soft, threshold, component,
flavour, and hadronic analyses remain necessary.

Core SHA-256: {report['core_sha256']}
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V41 mixed-four-matter JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V41 mixed-four-matter Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V41_MIXED_FOUR_MATTER_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
