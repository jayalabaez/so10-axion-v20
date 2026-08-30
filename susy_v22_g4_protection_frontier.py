#!/usr/bin/env python3
"""Composed exact G4 protection frontier for the V22 SUSY continuation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract
import susy_v22_exact_ew_endpoint as ew
import susy_v22_all_order_r_protection as r_protection
import susy_v22_f_flat_gut_slice as gut_slice
import susy_v22_missing_partner_rank as missing
import susy_v22_perturbative_window as running
import susy_v22_z4r_anomaly as z4r


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G4_PROTECTION_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V22_G4_PROTECTION_FRONTIER.md"


def portable_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_report() -> dict[str, Any]:
    c = contract.build_report()
    m = missing.build_report()
    e = ew.build_report()
    r = running.build_report()
    rp = r_protection.build_report()
    za = z4r.build_report()
    gs = gut_slice.build_report()
    # Exact degree-of-freedom cancellation of the quadratically divergent
    # coefficient in unbroken N=1 multiplets.  These are integer identities,
    # not floating loop estimates.
    cancellation = {
        "chiral_multiplet": {"real_scalar_dof": 2, "Weyl_fermion_dof": 2, "supertrace_dof": 2 - 2},
        "massless_vector_multiplet": {"vector_dof": 2, "Weyl_gaugino_dof": 2, "supertrace_dof": 2 - 2},
        "massive_vector_multiplet": {"vector_plus_real_scalar_dof": 4, "two_Weyl_dof": 4, "supertrace_dof": 4 - 4},
    }
    deps = {
        "contract": {"path": "SUSY_SO10X17_V22_CONTRACT.json", "core_sha256": c["core_sha256"]},
        "missing_partner": {"path": "SUSY_V22_MISSING_PARTNER_RANK.json", "core_sha256": m["core_sha256"]},
        "ew_endpoint": {"path": "SUSY_V22_EXACT_EW_ENDPOINT.json", "core_sha256": e["core_sha256"]},
        "perturbative_window": {"path": "SUSY_V22_PERTURBATIVE_WINDOW.json", "core_sha256": r["core_sha256"]},
        "holomorphic_R_protection": {"path": "SUSY_V22_ALL_ORDER_R_PROTECTION.json", "core_sha256": rp["core_sha256"]},
        "discrete_R_anomaly": {"path": "SUSY_V22_Z4R_ANOMALY.json", "core_sha256": za["core_sha256"]},
        "F_D_flat_GUT_slice": {"path": "SUSY_V22_F_FLAT_GUT_SLICE.json", "core_sha256": gs["core_sha256"]},
    }
    source_pins = {name: portable_sha(ROOT / name) for name in (
        "susy_so10x17_v22_contract.py", "susy_v22_missing_partner_rank.py",
        "susy_v22_exact_ew_endpoint.py", "susy_v22_perturbative_window.py",
        "susy_v22_all_order_r_protection.py", "susy_v22_z4r_anomaly.py",
        "susy_v22_f_flat_gut_slice.py")}
    positive = {
        "N1_source_contract_and_anomalies_closed": c["n_failed"] == 0,
        "light_doublet_pair_count_is_exactly_one": m["corrected_rank_certificate"]["doublet_nullity"] == 1,
        "color_triplet_zero_mode_count_is_zero": m["corrected_rank_certificate"]["triplet_nullity"] == 0,
        "EW_radius_is_exactly_174_GeV": e["checks"]["complex_VEV_radius_is_exactly_174_GeV"],
        "EW_tree_endpoint_has_no_physical_tachyon": e["checks"]["CP_even_matrix_is_positive_definite"] and e["checks"]["CP_odd_sector_has_one_gauge_zero_and_one_positive_mode"] and e["checks"]["charged_sector_has_one_gauge_zero_and_one_positive_mode"],
        "quadratic_dof_supertraces_cancel_exactly": all(row["supertrace_dof"] == 0 for row in cancellation.values()),
        "effective_GUT_gauge_window_is_nonempty": r["checks"]["coupling_is_finite_through_1p5_MGUT"],
        "holomorphic_light_bilinears_are_forbidden_by_source_landed_R_rule": rp["claim_boundary"]["holomorphic_charge_theorem_source_landed"],
        "mixed_discrete_R_anomalies_cancel_mod_eta": za["n_failed"] == 0,
        "exact_local_GUT_singlet_slice_is_F_and_D_flat": gs["claim_boundary"]["declared_GUT_singlet_slice_F_D_flat"],
    }
    open_requirements = {
        "source_exact_SO10_component_doublet_triplet_matrices_realize_rank_witness": False,
        "full_F_D_soft_vacuum_proves_every_R_charge_two_missing_partner_126_VEV_is_zero": False,
        "Kahler_and_soft_breaking_sector_preserve_the_required_hierarchy_to_all_orders": False,
        "complete_V22_F_D_soft_global_vacuum_excludes_deeper_branches": False,
        "complete_tensor_RGE_keeps_all_dimensionless_couplings_perturbative": False,
        "soft_boundary_and_threshold_flow_reaches_exact_EW_endpoint": False,
        "UV_completion_before_one_loop_SO10_Landau_pole": False,
    }
    checks = {
        "all_scoped_inputs_execute": all(x["n_failed"] == 0 for x in (c, m, e, r, rp, za, gs)),
        "all_positive_frontier_claims_hold": all(value is True for value in positive.values()),
        "every_unproved_canonical_acceptance_item_remains_false": all(value is False for value in open_requirements.values()),
        "canonical_G4_and_G5_not_promoted": True,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    out: dict[str, Any] = {
        "schema": "susy_v22_g4_protection_frontier_v1",
        "status": "SUSY_G4_PROTECTION_MECHANISM_SCOPED_CLOSED__CANONICAL_G4_G5_OPEN" if not failures else "SUSY_G4_PROTECTION_FRONTIER_FAILED",
        "dependencies": deps,
        "source_pins_portable_lf": source_pins,
        "exact_supersymmetric_cancellation": cancellation,
        "positive_frontier": positive,
        "open_canonical_requirements": open_requirements,
        "scientific_interpretation": {
            "V21_G3_invalidated": False,
            "V21_G3_scope": "remains a closed theorem for the frozen non-SUSY V21 potential",
            "V22_inherits_V21_G3": False,
            "why": "the hierarchy mechanism changes the field space and potential, so V22 must earn its own G1-G3 certificates",
            "what_is_now_proved": "an anomaly-free N=1 candidate, an exact missing-partner rank architecture, a source-landed holomorphic R selection rule, exact mixed Z4R anomaly cancellation, an exact stable 174 GeV tree endpoint, and a rigorous finite one-loop gauge window",
        },
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"scoped_hierarchy_protection_mechanism_closed": not failures,
                           "canonical_V22_G4_closed": False, "canonical_V22_G5_closed": False,
                           "authoritative_G4_G5_closed": False},
    }
    body = dict(out); out["core_sha256"] = csha(body)
    return out


def markdown(r: dict[str, Any]) -> str:
    return "\n".join(["# SUSY V22 G4 protection frontier", "", f"- Status: `{r['status']}`", f"- Core: `{r['core_sha256']}`",
        "- One exact protected doublet pair; no triplet zero mode in the rank architecture.",
        "- Exact tree endpoint at 174 GeV with positive physical Higgs curvatures.",
        "- Exact N=1 degree-of-freedom cancellation of quadratic sensitivity.", "",
        "- Source-landed holomorphic R selection rule forbids the light-light mass block, with exact mixed Z4R anomaly cancellation.", "",
        "Canonical G4 is not yet closed: the actual component Clebsches, a full V22 F/D/soft vacuum proving the required charge-two VEVs vanish, Kahler/soft radiative stability, the tensor RG/threshold bridge and ultraviolet completion remain required. V21 G3 remains valid in its own frozen contract but is not inherited by V22.", ""])


def write_outputs(r: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(r), encoding="utf-8", newline="\n")


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); r=build_report()
    if a.write: write_outputs(r)
    if a.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r)):
        raise ArithmeticError("V22 G4 frontier output drift")
    print(r["status"]); print(r["core_sha256"]); return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())
