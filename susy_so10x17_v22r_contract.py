#!/usr/bin/env python3
"""Source-bound contract for the active no-new-field V22R completion.

This contract promotes the accepted Z28R x Z2S construction into a separate
model without mutating V22.  It closes the complete degree<=4 holomorphic
base-sector catalogue (108 sectors, 265 SO(10)/flavour components counted),
but it does not claim normalized tensor contractions, component Clebsches, an
executable 108-term SARAH superpotential, or an all-order finite ring.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as v22
import susy_v22_g1_no_new_field_completion as completion
import susy_v22r_operator_catalogue as catalogue_generator


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_SO10X17_V22R_CONTRACT.json"
OUT_MD = ROOT / "SUSY_SO10X17_V22R_CONTRACT.md"
SCHEMA = "susy_so10x17_v22r_contract_v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def load_core_checked(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    body = dict(report)
    expected = body.pop("core_sha256")
    if sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()) != expected:
        raise ArithmeticError(f"invalid canonical core in {path.name}")
    return report


def anomaly_ledger() -> dict[str, Any]:
    z28 = completion.z28r_anomalies()
    z2 = completion.z2s_anomalies()
    return {
        "Z28R": z28,
        "Z2S": z2,
        "Z28R_passes_eta14":
            all(value == 0 for value in z28["linear_mod_eta_14"].values())
            and z28["U1X_Z28R_squared_mod_28"] == 0,
        "Z2S_even_ledgers":
            z2["odd_Weyl_dimension"] % 2 == 0
            and z2["SO10_index_sum"] % 2 == 0
            and z2["U1X_squared_sum"] % 2 == 0
            and z2["U1X_Z2_squared_exact"] == 0,
    }


def vacuum_stabilizer() -> dict[str, Any]:
    """Audit the diagonal Z28R x broken-gauge stabilizer of the VEVs.

    The standard SO(10) -> SU(5) x U(1)_chi normalization assigns the
    rank-breaking SM singlets in C16/C16bar charges +5/-5 (the simultaneous
    sign reversal is equivalent).  Phi210's standard singlet VEV directions
    are chi-neutral.
    """
    vev_rows = {
        "Phi210": {"X": 0, "chi": 0},
        "C16": {"X": 0, "chi": 5},
        "C16bar": {"X": 0, "chi": -5},
        "XMP": {"X": 0, "chi": 0},
        "Splus": {"X": 4, "chi": 0},
        "Sminus": {"X": -4, "chi": 0},
        "Phi17p": {"X": 17, "chi": 0},
        "Phi17m": {"X": -17, "chi": 0},
    }
    diagonal = []
    for element in range(28):
        t_x = Fraction(-5 * element, 7)
        t_chi = Fraction(element, 35)
        phases = {
            name: Fraction(element * completion.Z28R[name], 28)
            + t_x * row["X"] + t_chi * row["chi"]
            for name, row in vev_rows.items()
        }
        if all(phase.denominator == 1 for phase in phases.values()):
            diagonal.append(element)
    pure_global = [
        element for element in range(28)
        if all(element * completion.Z28R[name] % 28 == 0 for name in vev_rows)
    ]
    return {
        "SO10_singlet_chi_convention": {"C16": 5, "C16bar": -5, "Phi210": 0},
        "compensator_for_element_k": {
            "U1X_parameter": "-5 k / 7",
            "U1chi_parameter": "k / 35",
            "phase_convention": "exp(2 pi i [k q28/28 + tX X + tchi chi])",
        },
        "pure_global_stabilizer_elements": pure_global,
        "gauge_compensated_diagonal_stabilizer_elements": diagonal,
        "pure_global_stabilizer": "Z4R",
        "physical_diagonal_stabilizer": "Z28R",
        "interpretation": (
            "the earlier gcd=4 statement describes only transformations with no gauge compensation; "
            "the standard rank-breaking singlet embedding preserves the full gauge-compensated diagonal Z28R"
        ),
    }


def build_report() -> dict[str, Any]:
    catalogue = catalogue_generator.build_catalogue()
    frozen_catalogue = load_core_checked(catalogue_generator.OUT_JSON)
    accepted_completion = load_core_checked(catalogue_generator.COMPLETION_JSON)
    spurion_frontier = load_core_checked(catalogue_generator.SPURION_FRONTIER_JSON)
    model_text = catalogue_generator.MODEL_PATH.read_text(encoding="utf-8")
    expected_model = catalogue_generator.render_model(catalogue)
    anomalies = anomaly_ledger()
    stabilizer = vacuum_stabilizer()
    audited_leakage = catalogue["all_order_boundary"][
        "first_audited_XMP_spurion_leakage_layer"
    ]
    field_names = tuple(field["name"] for field in v22.FIELDS)
    selected_rows = catalogue["operator_sectors"]
    forced_rows = [row for row in selected_rows if row["provenance"] == "abelian_forced_completion_79"]
    direct_mp_rows = [row for row in forced_rows if row["direct_missing_partner_deformation"]]
    driver_names = {"Nphi", "NC", "NMP", "NX", "NS"}
    driver_rows = [row for row in selected_rows if driver_names.intersection(row["fields"])]
    vev_fields = ("Phi210", "C16", "C16bar", "XMP", "Splus", "Sminus", "Phi17p", "Phi17m")
    unbroken_elements = stabilizer["pure_global_stabilizer_elements"]
    source_paths = {
        "catalogue_generator": Path(catalogue_generator.__file__).resolve(),
        "operator_catalogue": catalogue_generator.OUT_JSON,
        "SARAH_source_model": catalogue_generator.MODEL_PATH,
        "accepted_completion": catalogue_generator.COMPLETION_JSON,
        "broken_selector_frontier": catalogue_generator.SPURION_FRONTIER_JSON,
    }
    source_manifest = [
        {
            "role": role,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "mode": "portable-lf",
            "sha256": sha256(portable_bytes(path)),
        }
        for role, path in source_paths.items()
    ]
    checks = {
        "generated_catalogue_core_is_frozen": frozen_catalogue == catalogue,
        "generated_SARAH_source_is_frozen": model_text == expected_model,
        "V22R_is_a_separate_model_and_does_not_overwrite_V22":
            catalogue_generator.MODEL_PATH != v22.MODEL_PATH
            and catalogue_generator.MODEL_PATH.parent.name == "SO10X17SUSYV22R",
        "field_content_is_exactly_the_unchanged_33_field_V22_source":
            field_names == catalogue_generator.FIELD_NAMES and len(field_names) == 33,
        "accepted_completion_core_is_pinned":
            catalogue["upstream"]["accepted_completion_core_sha256"] == accepted_completion["core_sha256"],
        "exact_degree_four_catalogue_has_108_base_sectors": len(selected_rows) == 108,
        "catalogue_partition_is_29_plus_79":
            catalogue["counts"]["retained_v22_base_sectors"] == 29
            and catalogue["counts"]["forced_completion_base_sectors"] == 79,
        "catalogue_has_exactly_265_counted_components":
            catalogue["counts"]["selected_so10_flavour_components"] == 265,
        "forced_completion_has_194_counted_components":
            catalogue["counts"]["forced_completion_so10_flavour_components"] == 194,
        "all_108_sectors_are_source_symmetry_allowed": all(
            row["Z28R_sum_mod_28"] == 2
            and row["Z2S_sum_mod_2"] == 0
            and row["SARAH_R_lift_sum"] == 2
            for row in selected_rows
        ),
        "standard_Z28R_and_Z2S_anomaly_ledgers_pass":
            anomalies["Z28R_passes_eta14"] and anomalies["Z2S_even_ledgers"],
        "pure_global_VEV_stabilizer_is_Z4R":
            unbroken_elements == [0, 7, 14, 21]
            and math.gcd(28, *(completion.Z28R[name] for name in vev_fields)) == 4,
        "standard_gauge_compensated_physical_stabilizer_is_full_Z28R":
            stabilizer["gauge_compensated_diagonal_stabilizer_elements"] == list(range(28)),
        "XMP_VEV_breaks_the_Z2S_selector":
            completion.Z28R["XMP"] == 0 and "XMP" in completion.Z2S_ODD,
        "broken_selector_frontier_is_source_pinned":
            catalogue["all_order_boundary"]["core_sha256"] == spurion_frontier["core_sha256"],
        "first_audited_XMP_spurion_leakage_layer_is_67_sectors_160_components":
            spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["sectors"] == 67
            and spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["so10_flavour_components"] == 160
            and not spurion_frontier["first_audited_XMP_spurion_leakage_layer"]["complete_degree_five_census"],
        "ten_direct_missing_partner_deformations_are_explicit": len(direct_mp_rows) == 10,
        "generic_driver_basis_is_materially_larger_than_the_original_diagonal_five":
            len(driver_rows) > 5
            and accepted_completion["driver_constraint_matrix"]["all_entries_selected"] is True,
        "model_marks_component_superpotential_as_unimplemented":
            "SuperPotential = 0;" in model_text
            and "265 SO(10)/flavour components are counted" in model_text,
        "model_declares_exactly_one_SARAH_gauge_eigenstate":
            model_text.count("NameOfStates = {GaugeES};") == 1,
        "model_embeds_all_108_machine_readable_sector_ids": all(
            row["sector_id"] in model_text for row in selected_rows
        ),
        "no_full_G1_or_later_gate_is_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "active.susy_so10x17.v22r.source_contract",
        "model_contract_id": "susy_so10x17_v22r_active_degree4_completion",
        "status": (
            "V22R_ACTIVE_SOURCE_108_SECTOR_DEGREE4_CONTRACT_CLOSED__TENSOR_VACUUM_G2_OPEN"
            if not failures else "V22R_SOURCE_CONTRACT_AUDIT_FAILED"
        ),
        "overall_state": "ACTIVE_DEGREE4_EFT_SOURCE_LANDED" if not failures else "EXECUTION_FAIL",
        "model_source": {
            "path": str(catalogue_generator.MODEL_PATH.relative_to(ROOT)).replace("\\", "/"),
            "mode": "portable-lf",
            "sha256": sha256(portable_bytes(catalogue_generator.MODEL_PATH)),
        },
        "operator_catalogue": {
            "path": catalogue_generator.OUT_JSON.name,
            "core_sha256": catalogue["core_sha256"],
            "field_degree": [1, 4],
            "base_sectors": 108,
            "retained_v22_sectors": 29,
            "forced_completion_sectors": 79,
            "counted_so10_flavour_components": 265,
            "component_tensor_realizations_landed": 0,
        },
        "source_manifest": source_manifest,
        "field_content": {
            "new_chiral_fields_relative_to_V22": 0,
            "source_fields": 33,
            "field_names": list(field_names),
        },
        "symmetry": {
            "group": "Z28R x Z2S",
            "Z28R_superpotential_charge": 2,
            "Z28R_field_charges": completion.Z28R,
            "Z2S_odd_fields": sorted(completion.Z2S_ODD),
            "SARAH_encoding": (
                "integer U(1)R lift plus ordinary Z2S, selection-equivalent only on the frozen "
                "degree<=4 census; finite Z28R Python/JSON data are authoritative at higher degree"
            ),
            "anomaly_ledger": anomalies,
            "vacuum_stabilizer": stabilizer,
            "pure_global_R_remnant": "Z4R",
            "physical_gauge_compensated_R_remnant": "Z28R",
        },
        "all_order_boundary": {
            "path": catalogue_generator.SPURION_FRONTIER_JSON.name,
            "core_sha256": spurion_frontier["core_sha256"],
            "degree_four_EFT_catalogue_exact": True,
            "finite_108_sector_catalogue_all_order_closed": False,
            "reason": (
                "the required Z2S-odd XMP VEV opens a Wilsonian spurion tower; the reported "
                "67-sector count is only the first audited XMP-spurion leakage layer, not a "
                "complete degree-five census"
            ),
            "lifts_already_inside_degree_four_catalogue": 15,
            "first_audited_XMP_spurion_leakage_layer": dict(audited_leakage),
            "pure_Z4R_direct_light_block_protection_survives": True,
            "physical_diagonal_Z28R_strengthens_the_remnant_under_standard_embedding": True,
        },
        "material_revalidation": {
            "generic_driver_product_matrix_shape": [5, 5],
            "driver_related_selected_sectors": len(driver_rows),
            "direct_missing_partner_deformation_sectors": [
                {"sector_id": row["sector_id"], "monomial": row["monomial"]}
                for row in direct_mp_rows
            ],
            "global_F_D_soft_vacuum_recompute_required": True,
            "doublet_triplet_component_matrix_recompute_required": True,
            "flavour_fit_recompute_required": True,
        },
        "claim_boundary": {
            "active_V22R_source_model_landed": not failures,
            "degree_le_4_base_sector_selection_closed": not failures,
            "standard_source_symmetry_anomaly_arithmetic_closed": not failures,
            "individual_SO10_tensor_contractions_landed": False,
            "component_Clebsches_closed": False,
            "SARAH_executable_full_superpotential_landed": False,
            "all_order_holomorphic_ring_closed": False,
            "Kahler_and_soft_rings_closed": False,
            "global_F_D_soft_vacuum_closed": False,
            "full_V22R_G1_closed": False,
            "V22R_G2_closed": False,
            "V22R_G3_closed": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    catalogue = report["operator_catalogue"]
    boundary = report["all_order_boundary"]
    leakage = boundary["first_audited_XMP_spurion_leakage_layer"]
    return "\n".join([
        "# SUSY SO(10) x U(1)X V22R active source contract", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Source model: `{report['model_source']['path']}`",
        f"- Exact degree<=4 base sectors: {catalogue['base_sectors']} (29 retained + 79 forced)",
        f"- Counted SO(10)/flavour components: {catalogue['counted_so10_flavour_components']}",
        f"- First audited XMP-spurion leakage layer: {leakage['sectors']} degree-five sectors / "
        f"{leakage['so10_flavour_components']} components (not a complete degree-five census)", "",
        "V22R is now source-landed as a separate no-new-field degree-four EFT completion selected by",
        "Z28R x Z2S. The complete 108-entry base-sector catalogue is machine-readable in both JSON",
        "and the Mathematica model source.", "",
        "The 265 invariant components are counted, not tensor-normalized or promoted into an executable",
        "SARAH superpotential. Because the required XMP VEV breaks Z2S, the finite catalogue is not",
        "all-order closed; its first audited XMP-spurion leakage layer has 67 degree-five sectors.", "",
        "The global vacuum, component missing-partner matrices, flavour fit, Kahler ring, soft ring, and",
        "full V22R G1-G3 gates remain open.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        catalogue_generator.write_outputs(catalogue_generator.build_catalogue())
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V22R contract JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R contract Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["operator_catalogue"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
