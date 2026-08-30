#!/usr/bin/env python3
"""V66 multipath master: retract V65's action upgrade without altering V65."""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V66"
DATE = "2026-08-30"
SCHEMA = "susy_v66_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V66_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V66_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v66_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v65_master": ROOT / "SUSY_V65_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v66_route": ROOT / "SUSY_V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR_AUDIT.json",
    "A60": ROOT / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "C": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}
CORE_KEYS = {
    "v65_master": "core_sha256",
    "v66_route": "core_sha256",
    "A60": "canonical_core_sha256",
    "C": "core_sha256",
}
EXPECTED_CORES = {
    "v65_master": "5b3056510129107959a6725139942307fc47b8cf56b375511a72cf9c6c8e58b8",
    "v66_route": "07593002755158c96647701da7453b1942114424a5d3aff5318ebb891a2964ae",
    "A60": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "C": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}
V64_NULL_CORE = "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d"
V65_ROW_SHA = {
    "A60": "6da4639c992fa999dd4d21752f1b9293568f899ea2455f2369440c2d13e56f78",
    "B65": "91e4a9e248c50508433ba5854dc6b7e65532fbb20a5c9b2812b80bb28f5bda05",
    "C": "f31e22fc1eab066f86f033192bfc6ee06b2e1e0398d3ed9b3ac33e987d392c25",
}
STATUS = (
    "V66_MULTIPATH_G1_FRONTIER_MASTER__V65_AND_V66_CORES_BOUND__ONLY_B65_TO_"
    "B66_SUPERSESSION__A60_AND_C_PRESERVED__V65_ARTIFACT_VALID_ACTION_UPGRADE_"
    "RETRACTED__CURRENT_SPIN11_ACTION_REJECTED__V64_NULL_MODE_AND_NO_WZ_STAND__"
    "H66_HIGH_SCALE_ORPHAN_ONLY_AND_T66_LOW_SCALE_FULL_TEN_ARE_CANDIDATES_ONLY__"
    "NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def canonical_sha(value: Mapping[str, Any], key: str = "core_sha256") -> str:
    body = copy.deepcopy(dict(value))
    body.pop(key, None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    value = json.loads(path.read_text(encoding="utf-8"))
    key = CORE_KEYS[name]
    if value.get(key) != canonical_sha(value, key):
        raise RuntimeError(f"stale canonical core: {path.name}")
    if value[key] != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(next(row for row in master["route_matrix"] if row["route_id"] == route_id))


def carried(v65: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(v65, route_id)
    if object_sha(row) != V65_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V65 route row: {route_id}")
    row["carried_forward_unchanged_from_V65_master_core"] = v65["core_sha256"]
    row["direct_core_rebound_in_V66"] = True
    return row


def strip_carry(row: Mapping[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(dict(row))
    value.pop("carried_forward_unchanged_from_V65_master_core", None)
    value.pop("direct_core_rebound_in_V66", None)
    return value


def regression_scope() -> dict[str, Any]:
    file_re = re.compile(r"^test_susy_v(?:59|60|61|62|63|64|65)_.*\.py$")
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = []
    for path in sorted(ROOT.glob("test_susy_v*.py")):
        if file_re.match(path.name):
            rows.append({
                "path": path.name,
                "test_functions": len(test_re.findall(path.read_text(encoding="utf-8"))),
            })
    return {
        "selection": "every test_susy_v59 through test_susy_v65 Python file",
        "pre_V66_file_count": len(rows),
        "pre_V66_test_count": sum(row["test_functions"] for row in rows),
        "incorrect_prior_narrow_count": 199,
        "correction": "208 pre-V66 tests, not 199",
        "files": rows,
    }


def one_loop_residual(one: Mapping[str, Any], solution: Mapping[str, Any]) -> float:
    inputs = one["inputs"]
    betas = one["beta_coefficients"]
    mz, ms = float(inputs["MZ_GeV"]), float(solution["MS_GeV"])
    mq, mg = float(solution["MQ_GeV"]), float(solution["MG_GeV"])
    a0 = [float(x) for x in inputs["derived_alpha_inverse_GUT_order"]]
    bsm = [float(Fraction(x)) for x in betas["SM"]]
    bm = [float(Fraction(x)) for x in betas["MSSM"]]
    db = [float(Fraction(x)) for x in betas["orphan_Q_pair_Delta_b"]]
    values = [
        a0[i]
        - bsm[i] * math.log(ms / mz) / (2 * math.pi)
        - bm[i] * math.log(mg / ms) / (2 * math.pi)
        - db[i] * math.log(mg / mq) / (2 * math.pi)
        for i in range(3)
    ]
    return max(values) - min(values)


def b66_row(route: Mapping[str, Any]) -> dict[str, Any]:
    one = copy.deepcopy(route["one_loop_threshold_solution"])
    one["c_equals_1"]["master_recomputed_residual"] = one_loop_residual(
        one, one["c_equals_1"]
    )
    one["fixed_MS_1_TeV"]["master_recomputed_residual"] = one_loop_residual(
        one, one["fixed_MS_1_TeV"]
    )
    return {
        "route_id": "B66",
        "name": "Spin(11) correction with two unaccepted candidate extensions",
        "bound_core_sha256": route["core_sha256"],
        "classification": route["classification"],
        "supersedes_V65_route_id": "B65",
        "V65_artifact_integrity": "PRESERVED",
        "V65_action_upgrade": "RETRACTED",
        "current_action_status": "REJECTED",
        "V64_null_mode_core": route["lineage"]["bound_V64_null_mode_route_core"],
        "V64_null_mode_stands": route["terminal_decision"]["V64_null_mode_retraction_preserved"],
        "WZ_term": route["terminal_decision"]["WZ_term"],
        "gm_overlap": copy.deepcopy(route["gm_overlap_and_retraction"]),
        "beta_and_two_loop_matrices": copy.deepcopy(route["martin_vaughn_group_theory"]),
        "one_loop_crossing": one,
        "two_loop_diagnostics": copy.deepcopy(route["two_loop_gauge_only_diagnostics"]),
        "candidate_extensions": copy.deepcopy(route["candidate_extensions"]),
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates(v65: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v65["gate_ledger"]}
    decisions = {
        "G1": "OPEN: current Spin(11) action REJECTED; H66 and T66 are incomplete alternative extensions.",
        "G2": "OPEN: no complete coefficient-level action, flavor/KK determinant or soft spectrum.",
        "G3": "OPEN: no compactification, hidden-sector vacuum, saxion stabilization or full Hessian.",
        "G4": "OPEN WITH REJECTION: the V64 post-rank normalizable colored chiral pair survives; GM is unconstructed.",
        "G5": "OPEN: R-parity arithmetic survives, but colored-LSP ordering, decays, relics and collider limits are absent.",
        "G6": "OPEN: inflation, reheating, defects and moduli history remain absent; crossing is not cosmology.",
        "G7": "OPEN: no proton lifetime; T66 adds Uc_X dc dc and Ec_X L L baryon-danger channels.",
        "G8": "OPEN: no UV regulator, Dai-Freed completion or predictivity score.",
    }
    return [{
        "gate": gate,
        "status": "OPEN",
        "V66_master_closed": False,
        "decision": decisions[gate],
        "prior_master_semantics_preserved": prior[gate]["status"] == "OPEN",
        "cross_route_aggregation_used": False,
    } for gate in (f"G{i}" for i in range(1, 9))]


def theory_card(b66: Mapping[str, Any], criteria: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": "V66 fail-closed 5D SUSY Spin(11) frontier card",
        "current_bound_action_status": "REJECTED",
        "preserved": [
            "V65 files remain canonically valid historical artifacts",
            "V64 normalizable Q-like null mode stands",
            "no Wess-Zumino term is forced",
            "GM is allowed but not constructed",
            "Delta b uses conventional (b1_GUT,b2,b3) order",
        ],
        "retracted": [
            "nonzero GM orphan mass in the bound action",
            "fast orphan decay after overlap suppression",
            "V65 global baryon-safety inference",
            "conditionally viable current action",
        ],
        "candidate_extensions": [{
            "id": row["id"],
            "status": row["status"],
            "accepted": False,
            "same_action_complete": False,
        } for row in b66["candidate_extensions"]],
        "acceptance_criteria": copy.deepcopy(criteria),
        "open_obligations": [
            "explicit hidden/Kahler/soft sector and overlap-normalized spectrum",
            "pole thresholds, decays, relic history and collider constraints",
            "precision matching with Yukawa, soft, KK and brane thresholds",
            "T66 Spin(11)/Spin(10) embedding and localized anomaly/GS closure",
            "T66 baryon safety including Uc_X dc dc and Ec_X L L",
            "vacuum, Dai-Freed, flavor, proton lifetime and UV regulator",
        ],
        "honesty_clause": "H66 and T66 are candidates only, not an accepted or complete theory.",
    }


def recompute(report: Mapping[str, Any]) -> dict[str, bool]:
    routes = {row["route_id"]: row for row in report["route_matrix"]}
    b = routes.get("B66", {})
    gm = b.get("gm_overlap", {})
    norm = gm.get("v64_null_mode_normalization", {})
    group = b.get("beta_and_two_loop_matrices", {})
    one = b.get("one_loop_crossing", {})
    two = b.get("two_loop_diagnostics", {})
    cand = {row.get("id"): row for row in b.get("candidate_extensions", [])}
    t = cand.get("T66", {})
    baryon = t.get("baryon_safety", {})
    criteria = report.get("acceptance_criteria", [])
    gates = report.get("gate_ledger", [])
    strict = report.get("strict_master_decision", {})
    scope = report.get("regression_scope_correction", {})
    try:
        residuals_ok = (
            one_loop_residual(one, one["c_equals_1"]) < 1e-10
            and one_loop_residual(one, one["fixed_MS_1_TeV"]) < 1e-10
        )
    except Exception:
        residuals_ok = False
    return {
        "input_cores": report.get("input_core_hashes") == EXPECTED_CORES,
        "only_B65_to_B66": list(routes) == ["A60", "B66", "C"] and b.get("supersedes_V65_route_id") == "B65",
        "A60_preserved": routes.get("A60", {}).get("bound_core_sha256") == EXPECTED_CORES["A60"] and object_sha(strip_carry(routes.get("A60", {}))) == V65_ROW_SHA["A60"],
        "C_preserved": routes.get("C", {}).get("bound_core_sha256") == EXPECTED_CORES["C"] and object_sha(strip_carry(routes.get("C", {}))) == V65_ROW_SHA["C"],
        "V65_valid_upgrade_retracted": b.get("V65_artifact_integrity") == "PRESERVED" and b.get("V65_action_upgrade") == "RETRACTED" and b.get("current_action_status") == "REJECTED",
        "V64_null_no_WZ": b.get("V64_null_mode_core") == V64_NULL_CORE and b.get("V64_null_mode_stands") is True and b.get("WZ_term") == "NONE_FORCED",
        "GM_overlap": gm.get("nonzero_mass_constructed_in_bound_action") is False and gm.get("general_supergravity_mass") == "mu_Q = [m_3/2 Z_Q - Fbar^I partial_bar_I Z_Q]/sqrt(Y_Q Y_Qbar)" and norm.get("effective_bilinear") == "Z_eff = c_K/(1+alpha^2)" and norm.get("portal_amplitude_overlap") == "1/sqrt(1+alpha^2)",
        "beta_order": group.get("convention") == "rows and columns are ordered (U1_GUT, SU2_L, SU3_c)" and group.get("orphan_Q_pair", {}).get("Delta_b") == ["1/5", "3", "2"] and group.get("complete_10_plus_10bar", {}).get("Delta_b") == ["3", "3", "3"],
        "one_loop": residuals_ok and one.get("analytic_c_family", {}).get("derived_exact_powers") == {"MG": "3/64", "MQ": "11/32", "MS": "-21/32", "alphaU_inverse_ln_c": "-121/(128*pi)"} and math.isclose(one.get("fixed_MS_1_TeV", {}).get("MQ_GeV", 0), 5.337995621018032e15, rel_tol=1e-12),
        "two_loop_boundary": two.get("claim_boundary") == "these are gauge-only diagnostics, not precision unification fits" and len(two.get("not_included", [])) == 4,
        "two_candidates_only": set(cand) == {"H66", "T66"} and len(cand) == 2 and all(row.get("not_complete") and row.get("status") == "CANDIDATE_CONDITIONAL_EXTENSION" for row in cand.values()) and b.get("accepted_extension_count") == 0,
        "T66_benefit_dangers": t.get("total_Delta_b") == ["3", "3", "3"] and baryon.get("inherits_V65_claim") is False and "Uc_X dc dc" in baryon.get("reason", "") and "Ec_X L L" in baryon.get("reason", "") and any("embedding" in x for x in t.get("missing", [])) and any("anomaly" in x for x in t.get("missing", [])),
        "suite_208_not_199": scope.get("pre_V66_file_count") == 16 and scope.get("pre_V66_test_count") == 208 and scope.get("incorrect_prior_narrow_count") == 199 and sum(x.get("test_functions", 0) for x in scope.get("files", [])) == 208,
        "A1_A8_open": [x.get("id") for x in criteria] == [f"A{i}" for i in range(1, 9)] and all(x.get("status") == "OPEN" for x in criteria),
        "G1_G8_open": [x.get("gate") for x in gates] == [f"G{i}" for i in range(1, 9)] and all(x.get("status") == "OPEN" and x.get("V66_master_closed") is False and x.get("cross_route_aggregation_used") is False for x in gates) and "post-rank" in gates[3].get("decision", "") and "inflation" in gates[5].get("decision", "") and "proton lifetime" in gates[6].get("decision", ""),
        "fail_closed": report.get("cross_route_composition_rule", {}).get("cross_route_splicing_allowed") is False and strict.get("current_Spin11_action_status") == "REJECTED" and strict.get("accepted_extension_count") == 0 and strict.get("same_action_microscopic_completion_found") is False and strict.get("V66_G1_closed") is False and strict.get("closed_gates") == [] and strict.get("complete_theory") is False,
    }


def source_manifest() -> list[dict[str, Any]]:
    return [{"path": p.name, "exists": p.is_file(), "sha256": file_sha(p)}
            for p in (Path(__file__), TEST_PATH, *INPUTS.values())]


def build_report() -> dict[str, Any]:
    v65 = load_bound("v65_master")
    v66 = load_bound("v66_route")
    live = load_bound("A60")
    gauged = load_bound("C")
    old_b = route_by_id(v65, "B65")
    if object_sha(old_b) != V65_ROW_SHA["B65"]:
        raise RuntimeError("changed V65 B65 row")
    a, b, c = carried(v65, "A60"), b66_row(v66), carried(v65, "C")
    if a["bound_core_sha256"] != live["canonical_core_sha256"] or c["bound_core_sha256"] != gauged["core_sha256"]:
        raise RuntimeError("direct carried-route core mismatch")
    criteria = copy.deepcopy(v66["acceptance_criteria"])
    gates = master_gates(v65)
    scope = regression_scope()
    if scope["pre_V66_test_count"] != v66["V65_integrity_scope_correction"]["current_full_test_count"] or scope["files"] != v66["V65_integrity_scope_correction"]["files"]:
        raise RuntimeError("pre-V66 test enumeration mismatch")
    report: dict[str, Any] = {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": "Does any one route close strict G1 after the V66 correction?",
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_V65_master_core": v65["core_sha256"],
            "V66_route_core": v66["core_sha256"],
            "superseded_route": {"route_id": "B65", "route_core": old_b["bound_core_sha256"], "source_row_sha256": object_sha(old_b), "historical_artifact_modified": False},
            "replacement_route": {"route_id": "B66", "route_core": v66["core_sha256"], "classification": v66["classification"]},
            "route_A60_core_unchanged": a["bound_core_sha256"],
            "route_C_core_unchanged": c["bound_core_sha256"],
            "supersession_scope": "B65 to B66 only",
        },
        "upstream_status": {"V65_master": v65["status"], "V66_route": v66["status"], "A60": live["status"], "C": gauged["status"]},
        "artifact_integrity_and_retraction": {"V65_artifact_integrity": "PRESERVED", "V65_files_modified": False, "V65_action_upgrade": "RETRACTED", "current_Spin11_action_status": "REJECTED"},
        "regression_scope_correction": scope,
        "route_matrix": [a, b, c],
        "consolidated_theory_card": theory_card(b, criteria),
        "acceptance_criteria": criteria,
        "cross_route_composition_rule": {"logical_rule": "G1 requires one versioned action; A60, B66 and C cannot be spliced, and H66/T66 are alternatives.", "cross_route_splicing_allowed": False, "aggregated_G1_closure": False},
        "comparison_conclusion": {
            "heterotic": v65["comparison_conclusion"]["heterotic"],
            "Spin11": "Current action rejected. H66 has a high-scale orphan-only crossing; T66 restores universal one-loop Delta b but adds embedding, anomaly and baryon obligations.",
            "gauged_U1R": v65["comparison_conclusion"]["gauged_U1R"],
            "frontier": "Accept a branch only after A1-A8 are met in one action.",
        },
        "strict_master_decision": {
            "V65_artifact_integrity_preserved": True,
            "V65_conditionally_viable_action_upgrade": "RETRACTED",
            "current_Spin11_action_status": "REJECTED",
            "V64_null_mode_retraction_preserved": True,
            "WZ_term": "NONE_FORCED",
            "candidate_extensions": ["H66", "T66"],
            "accepted_extension_count": 0,
            "same_action_microscopic_completion_found": False,
            "V66_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": "V65 remains a valid historical artifact, but its action upgrade is retracted. Current Spin11 action REJECTED; H66/T66 candidates only; A1-A8 and G1-G8 OPEN.",
        },
        "gate_ledger": gates,
        "source_policy": {"master_adds_no_new_literature_claim": True, "two_loop_diagnostics_are_not_precision_unification": True},
        "source_manifest": source_manifest(),
    }
    checks = recompute(report)
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not x for x in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise AssertionError("V66 master canonical core mismatch")
    try:
        checks = recompute(report)
    except Exception as exc:
        raise AssertionError(f"V66 master recomputation mismatch: {exc}") from exc
    failed = [name for name, ok in checks.items() if not ok]
    if report.get("integrity_checks") != checks:
        failed.append("cached_integrity_checks")
    if report.get("n_integrity_checks") != len(checks):
        failed.append("n_integrity_checks")
    if report.get("n_failed_integrity_checks") != sum(not x for x in checks.values()):
        failed.append("n_failed_integrity_checks")
    if failed:
        raise AssertionError(f"V66 master recomputation mismatch: {failed}")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {x["route_id"]: x for x in report["route_matrix"]}
    b = rows["B66"]
    gm, one, two = b["gm_overlap"], b["one_loop_crossing"], b["two_loop_diagnostics"]
    norm = gm["v64_null_mode_normalization"]
    cand = {x["id"]: x for x in b["candidate_extensions"]}
    criteria = "\n".join(f"| {x['id']} | {x['status']} | {x['requirement']} |" for x in report["acceptance_criteria"])
    gates = "\n".join(f"| {x['gate']} | {x['status']} | {x['decision']} |" for x in report["gate_ledger"])
    opens = "\n".join(f"- {x}" for x in report["consolidated_theory_card"]["open_obligations"])
    return f"""# V66 multipath G1 frontier master audit

Version: {report['version']}  
Date: {report['date']}  
Schema: {report['schema']}  
Status: {report['status']}

## Result

The V65 artifacts remain canonically valid, but the conditionally-viable action
upgrade is retracted. The current Spin(11) action is **REJECTED**. The V64
normalizable null mode and no-WZ result stand. H66 and T66 are candidate
conditional extensions only. G1-G8 remain OPEN with zero promotions.

Only B65 is superseded by B66. A60 remains bound to
{rows['A60']['bound_core_sha256']} and C to
{rows['C']['bound_core_sha256']}. No route evidence is spliced.

## Corrected regression scope

The full pre-V66 suite is {report['regression_scope_correction']['pre_V66_test_count']}
tests in {report['regression_scope_correction']['pre_V66_file_count']} files,
not the earlier narrow count of 199.

## GM and overlap result

General mass: {gm['general_supergravity_mass']}

Local-wall normalization:
- {norm['alpha_squared']}
- {norm['effective_bilinear']}
- portal amplitude {norm['portal_amplitude_overlap']}
- portal rate {norm['portal_rate_suppression']}

The term is allowed, but no nonzero coefficient or mass was constructed.

## One-loop result in conventional order

Order: (b1_GUT,b2,b3). Orphan shift:
{b['beta_and_two_loop_matrices']['orphan_Q_pair']['Delta_b']}.
Full 10+10bar shift:
{b['beta_and_two_loop_matrices']['complete_10_plus_10bar']['Delta_b']}.

For c=MQ/MS:
- MG = {one['analytic_c_family']['MG']}
- MQ = {one['analytic_c_family']['MQ']}
- MS = {one['analytic_c_family']['MS']}
- alphaU inverse = {one['analytic_c_family']['alphaU_inverse']}

At c=1, MS=MQ={one['c_equals_1']['MS_GeV']:.9e} GeV and
MG={one['c_equals_1']['MG_GeV']:.9e} GeV.
With MS=1 TeV, MQ={one['fixed_MS_1_TeV']['MQ_GeV']:.9e} GeV and
MG={one['fixed_MS_1_TeV']['MG_GeV']:.9e} GeV.

## Two-loop claim boundary

{two['claim_boundary']}.

- orphan raw: MS=MQ={two['orphan_only_raw_no_matching']['computed']['MS']:.9e} GeV
- orphan universal MSbar-to-DRbar: MS=MQ={two['orphan_only_universal_MSbar_to_DRbar']['computed']['MS']:.9e} GeV
- full 10 raw: MS=M10={two['full_ten_raw_no_matching']['computed']['MS']:.6f} GeV

These omit finite decoupling, Yukawa/tan(beta), soft splittings, and KK/brane
thresholds.

## Candidate branches

H66: {cand['H66']['diagnostic']}. Candidate only.

T66: {cand['T66']['diagnostic']}. Its universal Delta b improves relative
one-loop unification, but the full-10 portal includes Uc_X dc dc and Ec_X L L.
It needs a local Spin(11)/Spin(10) embedding, anomaly/GS recomputation, a soft
sector, thresholds, and a baryon-safety proof.

## Complete theory card obligations

{opens}

## Acceptance criteria

| ID | Status | Requirement |
|---|---|---|
{criteria}

## Established multipath gates

The established master meanings are preserved; V66 route-local labels are not
substituted.

| Gate | Status | Decision |
|---|---|---|
{gates}

## Decision

{report['strict_master_decision']['honest_outcome']}

Core SHA-256: {report['core_sha256']}
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    parser.add_argument("--emit-markdown", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("stale V66 master JSON")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("stale V66 master Markdown")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.emit_markdown:
        print(render_markdown(report), end="")
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

