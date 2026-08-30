#!/usr/bin/env python3
"""Exact fail-closed G4/G5 continuity obstruction for the current V21 model.

This is a negative frontier theorem, not a canonical gate artifact.  It proves
that the presently accepted canonical G3 point cannot be promoted to G4 or G5
without adding a hierarchy-protection mechanism and re-solving the physical
branch.  The proof is deliberately narrower than a no-go theorem for every
possible extension: it covers the declared fields and linear internal
symmetries that commute with SO(10).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CANONICAL_G4_G5_CURRENT_CONTRACT_OBSTRUCTION_V21.json"
OUT_MD = ROOT / "CANONICAL_G4_G5_CURRENT_CONTRACT_OBSTRUCTION_V21.md"
SCHEMA = "canonical_g4_g5_current_contract_obstruction_v1"
MODEL = "gauged_u1x_phi17_v20"

PORTABLE_PINS = {
    "canonical_g1_g8_gauged_u1x_v21.py": "4158df2bbef369d100ed95cf45a6428b3307cdf4da066f4664981b2c4d61dea0",
    "models/SO10Z17AxionV20.m": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json": "066e2ccd746d97ca562ca4f84957816a2d6babed10574112e8f7118ac23cd309",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json": "e296118ab33c3421350b0720fc8c824b2e218c3d80ec9e6b7c84e7eada491dfd",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json": "03b51b65a0a7d4e597d85acf914957b3f33f81c62f531ac03d62cb1d2fcfc565",
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json": "a94429e7838141cfd7a0860faa93b0a8ee23e9b8e8985222546ce552c9debe06",
    "cal_g_portal_decision_v20.py": "91ffdfe258985f3befe180e5689fe6735b6958f0b00a0c263424c1985ef14000",
    "cal_g_soft_mode_classification_v20.py": "31fb79840ed6f9485f91ece78f3a16ae5cff1d49a665e6e322a2fa20f4662358",
    "lambda_lock_cal_g_lift_v20.py": "6305256799dea28536edd4b7b0b886965ec5fc8c88ca62f30cd224e2f2235e55",
}


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())


def load_json(root: Path, name: str) -> dict[str, Any]:
    value = json.loads((root / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArithmeticError(f"{name} is not a JSON object")
    return value


def source_manifest(root: Path) -> list[dict[str, Any]]:
    rows = []
    for name, expected in PORTABLE_PINS.items():
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ArithmeticError(f"required source is absent or indirect: {name}")
        observed = sha256(portable_bytes(path))
        if observed != expected:
            raise ArithmeticError(f"source pin drifted: {name}")
        rows.append({"path": name, "mode": "portable-lf", "sha256": expected})
    return rows


def row_by_count(rows: list[dict[str, Any]], counts: list[int]) -> dict[str, Any]:
    matches = [row for row in rows if row.get("count_tuple") == counts]
    if len(matches) != 1:
        raise ArithmeticError(f"expected one G1 row for {counts}, found {len(matches)}")
    return matches[0]


def build_report(root: Path = ROOT) -> dict[str, Any]:
    manifest = source_manifest(root)
    model = (root / "models/SO10Z17AxionV20.m").read_text(encoding="utf-8")
    g1 = load_json(root, "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json")
    g2 = load_json(root, "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json")
    g3 = load_json(root, "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json")
    mismatch = load_json(root, "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json")

    h_norm = row_by_count(g1["rows"], [0, 1, 1, 0, 0, 0, 0, 0, 0])
    h_phi = row_by_count(g1["rows"], [2, 1, 1, 0, 0, 0, 0, 0, 0])
    h_sigma = row_by_count(g1["rows"], [0, 1, 1, 1, 1, 0, 0, 0, 0])
    h_s = row_by_count(g1["rows"], [0, 1, 1, 0, 0, 1, 1, 0, 0])
    h_x = row_by_count(g1["rows"], [0, 1, 1, 0, 0, 0, 0, 1, 1])
    lock_row = row_by_count(g1["rows"], [0, 2, 0, 2, 0, 2, 0, 0, 0])

    accepted = g3["accepted_potential"]
    coefficients = accepted["nonzero_coefficients"]
    exact_mismatch = mismatch["exact_branch_mismatch"]
    g2_lock = g2["explicit_required_coefficients"]["dimension_six_lock"]

    model_facts = {
        "model_is_explicitly_non_supersymmetric": "Native non-supersymmetric SARAH 4 input" in model,
        "one_H10_multiplet_declared": model.count("ScalarFields[[3]] = {H10") == 1,
        "H10_is_SO10_vector_10": "{H10,          1, h10,           10," in model,
        "H10_U1X_charge_is_minus_2": "10,  -2," in model,
        "H10_Z17_charge_is_15_mod_17": "Exp[2*Pi*I*15/17]" in model,
        "HdagH_mass_term_is_declared": "m10Sq conj[H10].H10" in model,
    }
    ring_facts = {
        "HdagH_unique_quadratic": h_norm["degree"] == 2 and h_norm["constructive_channel_count"] == 1,
        "HdagH_highest_weight_pair": h_norm["channels"][0]["plethysm_irreps"] == {
            "H": [1, 0, 0, 0, 0], "Hb": [1, 0, 0, 0, 0]
        },
        "PhiPhiHdagH_three_channels": h_phi["degree"] == 4 and h_phi["constructive_channel_count"] == 3,
        "SigmaSigmaHdagH_two_channels": h_sigma["degree"] == 4 and h_sigma["constructive_channel_count"] == 2,
        "SSdagHdagH_exists": h_s["constructive_channel_count"] == 1,
        "Phi17Phi17dagHdagH_exists": h_x["constructive_channel_count"] == 1,
        "dimension_six_lock_unique": lock_row["degree"] == 6 and lock_row["constructive_channel_count"] == 1,
    }
    hierarchy_facts = {
        "current_G3_H_over_Phi_squared": exact_mismatch["five_amplitude_branch"]["H_over_Phi_squared"],
        "required_physical_H_over_Phi_squared": exact_mismatch["canonical_G2_physical_EW_branch"]["H_over_Phi_squared_exact"],
        "exact_squared_ratio_mismatch_factor": exact_mismatch["exact_mismatch"]["five_over_physical_squared_ratio"],
        "common_rescaling_cannot_repair": exact_mismatch["exact_mismatch"]["common_unit_rescaling_can_remove_mismatch"] is False,
        "current_branch_is_globally_accepted_G3": g3["closure_complete"] is True and g3["scope_boundary"]["canonical_G3_closed"] is True,
        "current_branch_has_no_tachyon_or_deeper_vacuum": g3["checks"]["all_transverse_modes_strictly_positive"] is True and g3["checks"]["global_lower_bound_excludes_deeper_extrema"] is True,
        "H_Phi_portal_is_nonzero": coefficients.get("O46_B01_Phi2_HdagH_channels") == "3/5" and coefficients.get("O46_B03_Phi2_HdagH_channels") == "-1",
        "H_Sigma_portal_is_nonzero": coefficients.get("O35_B01_H_Sigma_hermitian") == "1" and coefficients.get("O35_B02_H_Sigma_hermitian") == "-1",
    }
    lock_facts = {
        "G2_lock_circuit_is_live_and_unique": g2_lock["direction_id"] == "g1_row_108_basis_001" and g2_lock["conjugate_direction_id"] == "g1_row_088_basis_001",
        "G3_sets_all_119_dimension_five_coefficients_to_zero": accepted["zero_dimension_five_directions"] == 119,
        "G3_sets_all_721_dimension_six_coefficients_to_zero": accepted["zero_dimension_six_directions"] == 721,
        "G3_lambda_lock_coefficient_is_exactly_zero": g2_lock["direction_id"] not in coefficients and g2_lock["conjugate_direction_id"] not in coefficients,
        "G3_has_exactly_one_axion_modulo_gauge": g3["checks"]["exactly_one_intended_axion_modulo_gauge"] is True,
        "G3_all_non_symmetry_scalar_modes_are_positive": g3["checks"]["all_transverse_modes_strictly_positive"] is True,
    }

    checks = {
        "all_sources_match_frozen_pins": len(manifest) == len(PORTABLE_PINS),
        "declared_model_and_H_representation_match": all(model_facts.values()),
        "G1_contains_every_neutral_H_mass_and_heavy_norm_portal_used_by_the_obstruction": all(ring_facts.values()),
        "physical_hierarchy_is_not_the_current_G3_ratio": hierarchy_facts["current_G3_H_over_Phi_squared"] != hierarchy_facts["required_physical_H_over_Phi_squared"],
        "common_field_unit_rescaling_cannot_fix_the_ratio": hierarchy_facts["common_rescaling_cannot_repair"],
        "current_G3_turns_on_H_heavy_portals": hierarchy_facts["H_Phi_portal_is_nonzero"] and hierarchy_facts["H_Sigma_portal_is_nonzero"],
        "current_G3_is_stable_but_at_the_wrong_hierarchy": hierarchy_facts["current_branch_is_globally_accepted_G3"] and hierarchy_facts["current_branch_has_no_tachyon_or_deeper_vacuum"],
        "lambda_lock_tensor_exists_but_its_G3_coefficient_is_zero": lock_facts["G2_lock_circuit_is_live_and_unique"] and lock_facts["G3_lambda_lock_coefficient_is_exactly_zero"],
        "current_G3_phase_result_is_only_the_single_axion_statement": lock_facts["G3_has_exactly_one_axion_modulo_gauge"] and lock_facts["G3_all_non_symmetry_scalar_modes_are_positive"],
        "not_promoted_to_canonical_G4_or_G5": g3["scope_boundary"]["canonical_G4_closed"] is False and g3["scope_boundary"]["canonical_G5_through_G8_closed"] is False,
    }
    failures = [name for name, passed in checks.items() if passed is not True]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "model_contract_id": MODEL,
        "status": "EXACT_CURRENT_CONTRACT_G4_G5_OBSTRUCTION_CLOSED__CANONICAL_G4_G5_OPEN" if not failures else "G4_G5_OBSTRUCTION_AUDIT_FAILED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_manifest": manifest,
        "exact_hierarchy_continuity": hierarchy_facts,
        "declared_model_facts": model_facts,
        "exact_G1_ring_facts": ring_facts,
        "linear_internal_symmetry_theorem": {
            "domain": "linear internal symmetries acting on the single 10_H and commuting with the irreducible SO(10) vector action",
            "schur_commutant": "C times the identity; its unitary subgroup acts only by an overall phase on 10_H",
            "consequence": "HdagH is invariant under every such symmetry, under U(1)_X, and under Z17; the same is true of HdagH times any heavy-field norm",
            "source_bound_conclusion": "no declared linear internal symmetry forbids the H mass or neutral heavy portals",
            "scope_limit": "this does not rule out a new nonlinear/pNGB, spacetime/SUSY, or enlarged-field protection mechanism",
        },
        "lambda_lock_and_phase": lock_facts,
        "canonical_gate_evaluation": {
            "G4": {
                "A1_physical_h_174_on_same_branch": False,
                "A2_perturbative_running_interval": False,
                "A3_radiative_stability_or_source_bound_protection": False,
                "A4_no_tachyon_or_deeper_vacuum_at_current_wrong_branch": True,
                "closed": False,
            },
            "G5": {
                "dependency_G4_closed": False,
                "A1_nonsusy_calG_scalar_lift_above_physical_tolerance": False,
                "A2_only_intended_axion_at_current_wrong_branch": True,
                "A3_positive_complete_scalar_Hessian_at_current_wrong_branch": True,
                "A4_nonzero_live_lambda_lock_used_on_physical_branch": False,
                "closed": False,
            },
        },
        "required_model_authority": {
            "reason": "the current field/symmetry contract has no source-bound hierarchy protection and the accepted G3 branch has the wrong exact ratio",
            "recommended_extension": "softly broken N=1 SO(10)xU(1)_X with a conjugate 126 for D-flat breaking and a declared soft sector",
            "alternative_extension": "a genuinely specified non-supersymmetric pNGB/collective-protection sector",
            "both_require": "supersede the model contract and recompute canonical G1-G3 before G4/G5 can close",
        },
        "claim_boundary": {
            "current_contract_obstruction_proved": not failures,
            "global_no_go_for_all_model_extensions": False,
            "canonical_G4_closed": False,
            "canonical_G5_closed": False,
            "release_or_authoritative_G4_G5_closed": False,
        },
    }
    body = dict(report)
    report["core_sha256"] = canonical_sha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    h = report["exact_hierarchy_continuity"]
    return "\n".join([
        "# Canonical G4/G5 current-contract obstruction v21",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Current exact `||H||^2/||Phi||^2`: `{h['current_G3_H_over_Phi_squared']}`",
        f"- Required physical ratio: `{h['required_physical_H_over_Phi_squared']}`",
        "- The declared linear internal symmetries allow `Hdag H` and all neutral heavy-norm portals.",
        "- G2 contains the exact lambda-lock circuit, but the accepted G3 coefficient is exactly zero.",
        "",
        "This closes the obstruction audit, not G4 or G5. A new hierarchy-protection mechanism must be authorized and G1-G3 recomputed before either canonical gate can close.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
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
        if not OUT_JSON.is_file() or json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("G4/G5 obstruction JSON drifted")
        if not OUT_MD.is_file() or OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("G4/G5 obstruction Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
