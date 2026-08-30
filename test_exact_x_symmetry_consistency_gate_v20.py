#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as gate
import run_exact_x_sarah_validation_v20 as runner


def _legacy_pseudo_sarah_model() -> str:
    return r"""
NameOfModel = "SO10U1XComplete";
GlobalSymmetry = {Z[17]};
Gauge[[1]] = {G10, SO, 10, g10};
Gauge[[2]] = {GX, U[1], X, gX, False};
ScalarFields[[1]] = {Phi210, {210}, SO10Real, {0, 0}};
ScalarFields[[2]] = {Delta126bar, {126}, Complex, {-2, -2}};
ScalarFields[[3]] = {H10, {10}, Complex, {-2, -2}};
ScalarFields[[4]] = {S, {1}, Complex, {4, 4}};
ScalarFields[[5]] = {Phi17, {1}, Complex, {0, 17}};
FermionFields[[1]] = {FPR, {16}, 5, {1, 1}};
FermionFields[[2]] = {SpecS, {16}, 5, {2, 2}};
FermionFields[[3]] = {SpecB, {-16}, 5, {-6, -6}};
FermionFields[[4]] = {Q, {16}, 1, {-3, 14}};
FermionFields[[5]] = {Pbar, {-16}, 1, {-1, 16}};
FermionFields[[6]] = {Qbar, {-16}, 1, {3, 3}};
FermionFields[[7]] = {Rbar, {-16}, 1, {-1, -18}};
LagHC = -(lambdaH H10.H10.S);
LagNoHC = -(mH2 H10.H10);
"""


def _native_sarah_model() -> str:
    return r"""
NameOfModel = "SO10U1XComplete";
NameOfStates = {GaugeES};
Gauge[[1]] = {G10, SO[10], SOGUT, g10, False};
Gauge[[2]] = {GX, U[1], X, gX, False};
Global[[1]] = {Z[17], Z17};
ScalarFields[[1]] = {Phi210, 1, phi210, 210, 0, 1};
ScalarFields[[2]] = {Delta126bar, 1, delta126bar, -126, -2, Exp[2*Pi*I*15/17]};
ScalarFields[[3]] = {H10, 1, h10, 10, -2, Exp[2*Pi*I*15/17]};
ScalarFields[[4]] = {S, 1, singletS, 1, 4, Exp[2*Pi*I*4/17]};
ScalarFields[[5]] = {Phi17, 1, phi17, 1, 17, 1};
FermionFields[[1]] = {F, 3, f16, 16, 1, Exp[2*Pi*I*1/17]};
FermionFields[[2]] = {P, 1, p16, 16, 1, Exp[2*Pi*I*1/17]};
FermionFields[[3]] = {R, 1, r16, 16, 1, Exp[2*Pi*I*1/17]};
FermionFields[[4]] = {SpecS, 5, s16, 16, 2, Exp[2*Pi*I*2/17]};
FermionFields[[5]] = {SpecB, 5, b16bar, -16, -6, Exp[2*Pi*I*11/17]};
FermionFields[[6]] = {Q, 1, q16, 16, 14, Exp[2*Pi*I*14/17]};
FermionFields[[7]] = {Pbar, 1, pbar16, -16, 16, Exp[2*Pi*I*16/17]};
FermionFields[[8]] = {Qbar, 1, qbar16, -16, 3, Exp[2*Pi*I*3/17]};
FermionFields[[9]] = {Rbar, 1, rbar16, -16, -18, Exp[2*Pi*I*16/17]};
DEFINITION[GaugeES][LagrangianInput] = {
  {LagHC, {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};
LagHC = -(lambdaH H10.H10.S);
LagNoHC = -(mH2 conj[H10].H10);
"""


def _external_attestation(model_text: str) -> dict[str, Any]:
    model_bytes = model_text.encode("utf-8")
    driver_path = gate.EXTERNAL_DRIVER_REPOSITORY_PATH
    driver_bytes = gate.EXTERNAL_DRIVER.read_bytes()
    trusted_release_bytes = gate.TRUSTED_SARAH_RELEASE_MANIFEST.read_bytes()
    trusted_release = json.loads(trusted_release_bytes.decode("utf-8"))
    manifest_files = [
        {
            "path": gate.MODEL_REPOSITORY_PATH,
            "sha256": hashlib.sha256(model_bytes).hexdigest(),
            "size_bytes": len(model_bytes),
            "role": "primary_model",
            "format": gate.SARAH_MODEL_FORMAT,
        },
        {
            "path": driver_path,
            "sha256": hashlib.sha256(driver_bytes).hexdigest(),
            "size_bytes": len(driver_bytes),
            "role": "validation_driver",
            "format": gate.EXTERNAL_DRIVER_FORMAT,
        },
        {
            "path": gate.TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
            "sha256": hashlib.sha256(trusted_release_bytes).hexdigest(),
            "size_bytes": len(trusted_release_bytes),
            "role": "trusted_sarah_release_manifest",
            "format": gate.TRUSTED_SARAH_RELEASE_MANIFEST_FORMAT,
        },
    ]
    launcher_path = (
        r"C:\Program Files\Wolfram Research\Wolfram Engine\15.0\wolframscript.exe"
    )
    kernel_path = (
        r"C:\Program Files\Wolfram Research\Wolfram Engine\15.0\WolframKernel.exe"
    )
    wolfram_version = "15.0.0 for Microsoft Windows (64-bit)"
    process_log_content = "\n".join(
        [
            f"EXACT_X_ENGINE Wolfram {wolfram_version}",
            f"EXACT_X_KERNEL_PATH {kernel_path}",
            "SARAH 4.15.3 external validation",
            "EXACT_X_TOOL SARAH 4.15.3",
        ]
        + [f"EXACT_X_CHECK {name} PASS" for name in gate.REQUIRED_EXTERNAL_CHECKS]
    )
    process_log_bytes = process_log_content.encode("utf-8")
    runtime_probe_content = "\n".join(
        [
            f"EXACT_X_ENGINE Wolfram {wolfram_version}",
            f"EXACT_X_KERNEL_PATH {kernel_path}",
        ]
    )
    runtime_probe_bytes = runtime_probe_content.encode("utf-8")
    tree = trusted_release["tree"]
    executable_fingerprint = "a" * 64
    return {
        "schema": gate.EXTERNAL_VALIDATION_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": {
            "path": gate.MODEL_REPOSITORY_PATH,
            "sha256": hashlib.sha256(model_bytes).hexdigest(),
            "size_bytes": len(model_bytes),
            "format": gate.SARAH_MODEL_FORMAT,
        },
        "tool": {
            "name": "SARAH",
            "version": "4.15.3",
            "trusted_release_manifest": {
                "path": gate.TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
                "sha256": hashlib.sha256(trusted_release_bytes).hexdigest(),
                "size_bytes": len(trusted_release_bytes),
            },
            "source_tree": {
                "schema": gate.SARAH_SOURCE_TREE_SNAPSHOT_SCHEMA,
                "resolved_root": r"C:\external-tools\SARAH-4.15.3",
                "sha256": tree["sha256"],
                "file_count": tree["file_count"],
                "size_bytes": tree["size_bytes"],
                "verified_against_trusted_release_manifest": True,
                "unchanged_during_execution": True,
            },
        },
        "execution": {
            "external_process_executed": True,
            "command": [
                launcher_path,
                "-file",
                driver_path,
                "--repo-root",
                r"C:\repository",
                "--sarah-root",
                r"C:\external-tools\SARAH-4.15.3",
            ],
            "process_exit_code": 0,
            "runtime_probe_command": [
                launcher_path,
                "-code",
                gate.WOLFRAM_RUNTIME_PROBE_CODE,
            ],
            "runtime_probe_exit_code": 0,
            "runtime": {
                "wolfram_version": wolfram_version,
                "launcher": {
                    "resolved_path": launcher_path,
                    "sha256_before": executable_fingerprint,
                    "size_bytes_before": 100,
                    "sha256_after": executable_fingerprint,
                    "size_bytes_after": 100,
                    "unchanged_during_execution": True,
                },
                "kernel": {
                    "resolved_path": kernel_path,
                    "sha256_before": executable_fingerprint,
                    "size_bytes_before": 200,
                    "sha256_after": executable_fingerprint,
                    "size_bytes_after": 200,
                    "unchanged_during_execution": True,
                },
            },
        },
        "input_manifest": {
            "schema": gate.EXTERNAL_INPUT_MANIFEST_SCHEMA,
            "sha256": hashlib.sha256(
                gate._canonical_json_bytes(manifest_files)
            ).hexdigest(),
            "files": manifest_files,
        },
        "evidence": {
            "runtime_probe_log": {
                "encoding": "utf-8",
                "content": runtime_probe_content,
                "sha256": hashlib.sha256(runtime_probe_bytes).hexdigest(),
                "size_bytes": len(runtime_probe_bytes),
            },
            "process_log": {
                "encoding": "utf-8",
                "content": process_log_content,
                "sha256": hashlib.sha256(process_log_bytes).hexdigest(),
                "size_bytes": len(process_log_bytes),
            }
        },
        "checks": {
            "model_parse_succeeded": True,
            "model_initialization_succeeded": True,
            "lagrangian_construction_succeeded": True,
            "gauge_invariance_check_succeeded": True,
            "anomaly_check_succeeded": True,
        },
    }


def test_native_static_contract_tracks_real_external_execution():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["failures"] == []
    assert report["static_contract_consistent"] is True
    assert report["repository_external_input_manifest"]["valid"] is True
    if report["external_model_validation"]["valid"] is True:
        assert report["status"] == (
            "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__CONSISTENT"
        )
        assert report["overall_state"] == "PASS"
        assert report["contract_consistent"] is True
        assert report["blocker"] is None
        assert report["scientific_blockers"] == []
    else:
        assert report["status"] == (
            "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__BLOCKED"
        )
        assert report["overall_state"] == "BLOCKED"
        assert report["contract_consistent"] is False
        assert report["blocker"] == gate.EXTERNAL_EXECUTION_BLOCKER
        assert report["scientific_blockers"] == [gate.EXTERNAL_EXECUTION_BLOCKER]


def test_manuscript_is_authoritative_and_gauges_u1x():
    report = gate.build_report()
    manuscript = report["authoritative_manuscript_contract"]
    assert manuscript["authoritative_for_scientific_contract"] is True
    assert manuscript["gauges_primitive_U1X"] is True
    assert manuscript["phi17_X"] == 17
    assert manuscript["phi17_PQ"] == 0
    assert manuscript["charge_tuple_parsed"] is True
    assert manuscript["x_charge_tuple_values"] == [1, 2, -6, 4, -2, -2, 0]
    assert manuscript["scalar_final_charge_contract"] == {
        "Phi210": [0, 0],
        "Delta126bar": [-2, -2],
        "H10": [-2, -2],
        "S": [4, 4],
        "Phi17": [0, 17],
    }
    assert manuscript["scalar_charge_contract_matches_expected"] is True
    assert manuscript["declares_exact_U1X_renormalizable_catalogue"] is True


def test_native_model_and_explicit_filter_contract_are_compared():
    report = gate.build_report()
    model_text = gate.MODEL.read_text(encoding="utf-8")
    scaffold = report["executable_scaffold_contract"]
    contract = report["signed_filter_contract"]
    assert scaffold["authoritative_for_scientific_contract"] is False
    assert scaffold["explicitly_incomplete_scaffold"] is False
    assert scaffold["model_syntax_class"] == "sarah_native"
    assert scaffold["legacy_pseudo_sarah_grammar"] is False
    assert scaffold["tool_native_sarah_syntax"] is True
    assert scaffold["so10_gauged"] is True
    assert scaffold["u1x_gauged"] is True
    u1_rows = [row for row in scaffold["structured_gauge_rows"] if row["is_u1x"]]
    assert len(u1_rows) == 1
    assert u1_rows[0]["group_symbol"] == "GX"
    assert u1_rows[0]["group_name"] == "xcharge"
    assert scaffold["observed_scalar_charges_PQ_X"] == {
        "Phi210": [0, 0],
        "Delta126bar": [-2, -2],
        "H10": [-2, -2],
        "S": [4, 4],
        "Phi17": [0, 17],
    }
    assert scaffold["scalar_charges_match_manuscript"] is True
    assert scaffold["fermion_catalogue_exact"] is True
    assert scaffold["lagrangian"]["real_LagHC_present"] is True
    assert scaffold["lagrangian"]["real_LagNoHC_present"] is True
    assert scaffold["soft_gaugino_absent_in_nonsusy_model"] is True
    assert scaffold["statically_executable_model_contract"] is True
    assert "LagScalarCatalogue = -(" in model_text
    assert "LagFermionCatalogue = -(" in model_text
    assert "ContractionRGE[lambdaAudit] = 1;" in model_text
    assert "ContractionRGE[m210Sq] = 1;" in model_text
    assert contract["requires_exact_x_neutrality_by_default"] is True
    assert contract["encodes_option_C_no_continuous_X"] is False
    assert contract["policy"] == "REQUIRE_X"
    assert contract["evidence"]["live_catalogue_calls_require_x_true"] is True
    assert contract["phi17_X"] == 17
    resolution = report["required_resolution"]
    assert resolution["selected"] is None
    assert resolution["external_SARAH_execution"]["required"] is False
    assert resolution["option_A_gauge_U1X"]["accepted"] is True
    assert resolution["option_C_no_continuous_X"]["accepted"] is False
    assert resolution["option_C_no_continuous_X"]["rejected"] is True
    assert "executable_scaffold_omits_manuscript_U1X_gauge_factor" not in report[
        "contract_conflicts"
    ]
    assert "executable_scaffold_scalar_charges_do_not_match_manuscript" not in report[
        "contract_conflicts"
    ]
    assert "executable_scaffold_fermion_catalogue_incomplete" not in report[
        "contract_conflicts"
    ]


def test_all_phase_sensitive_phi17_terms_through_dimension_four_are_forbidden():
    report = gate.build_report()
    rows = report["authoritative_dim_le4_phi17_monomials"]
    phase_rows = [row for row in rows if row["phase_sensitive"]]
    balanced_rows = [row for row in rows if not row["phase_sensitive"]]
    assert phase_rows
    assert report["phase_sensitive_count"] == len(phase_rows)
    assert report["phase_sensitive_gauge_forbidden_count"] == len(phase_rows)
    assert all(row["continuous_X_charge"] != 0 for row in phase_rows)
    assert all(row["authoritative_U1X_gauge_invariant"] is False for row in phase_rows)
    assert all(row["authoritative_status"] == "GAUGE_FORBIDDEN" for row in phase_rows)
    assert balanced_rows
    assert all(row["authoritative_U1X_gauge_invariant"] is True for row in balanced_rows)
    assert all(row["authoritative_status"] == "GAUGE_ALLOWED" for row in balanced_rows)


def test_phi17_to_17_is_gauge_forbidden_even_though_it_is_pq_neutral():
    candidate = gate.build_report()["dimension17_candidate"]
    assert candidate["operator"] == "Phi17^17 + h.c."
    assert candidate["continuous_X_charge"] == 289
    assert candidate["breaks_continuous_X_by_units"] == 289.0
    assert candidate["authoritative_U1X_gauge_invariant"] is False
    assert candidate["authoritative_status"] == "GAUGE_FORBIDDEN"
    assert candidate["breaks_PQ"] is False
    assert candidate["direct_theta_bar_shift_from_PQ_charge"] == 0.0


def test_contract_flags_track_attestation_without_claiming_whole_model():
    report = gate.build_report()
    flags = report["flag"]
    assert flags["audit_executed_honestly"] is True
    assert flags["authoritative_gauged_U1X_contract"] is True
    assert flags["contract_consistent"] is report["contract_consistent"]
    assert flags["static_contract_consistent"] is True
    assert flags["x_selection_rule_consistently_declared"] is True
    assert flags["option_C_no_continuous_X_applied"] is False
    assert flags["option_C_no_continuous_X_rejected"] is True
    assert flags["dim_le4_phase_sensitive_phi17_terms_gauge_forbidden"] is True
    assert flags["dimension17_operator_is_x_invariant"] is False
    assert flags["complete_multifield_model"] is report["contract_consistent"]
    assert flags["whole_model_validated"] is False
    assert flags["whole_model_excluded"] is False


def test_exit_policy_distinguishes_honest_audit_from_strict_consistency():
    report = gate.build_report()
    assert gate.exit_code(report) == 0
    assert gate.exit_code(report, require_consistent=False) == 0
    assert (gate.exit_code(report, require_consistent=True) == 0) is report[
        "contract_consistent"
    ]


def test_fake_commented_second_gauge_row_cannot_unlock_contract():
    original = _legacy_pseudo_sarah_model().replace(
        "Gauge[[2]] = {GX, U[1], X, gX, False};", ""
    )
    report = gate.build_report(
        model_text=original
        + "\n(* Gauge[[2]] = {GX, U[1], X, gX, False}; *)\n"
    )
    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["executable_scaffold_contract"]["u1x_gauged"] is False
    assert report["contract_consistent"] is False
    assert report["overall_state"] == "BLOCKED"


def test_fake_gauge_row_inside_string_is_not_code():
    parsed = gate.declared_symmetries(
        'NameOfModel = "Gauge[[2]] = {GX, U[1], X, gX, False};";\n'
        "Gauge[[1]] = {G10, SO, 10};"
    )
    assert parsed["u1x_gauged"] is False
    assert len(parsed["structured_gauge_rows"]) == 1


def test_real_gauge_row_alone_cannot_unlock_incomplete_scaffold():
    original = _legacy_pseudo_sarah_model().replace(
        "Gauge[[2]] = {GX, U[1], X, gX, False};", ""
    ).replace("{-2, -2}", "{-2, 0}").replace(
        "FermionFields[[7]] = {Rbar, {-16}, 1, {-1, -18}};", ""
    )
    report = gate.build_report(
        model_text=original + "\nGauge[[2]] = {GX, U[1], X, gX, False};\n"
    )
    scaffold = report["executable_scaffold_contract"]
    assert scaffold["u1x_gauged"] is True
    assert scaffold["scalar_charges_match_manuscript"] is False
    assert scaffold["fermion_catalogue_exact"] is False
    assert scaffold["statically_executable_model_contract"] is False
    assert report["contract_consistent"] is False
    assert report["overall_state"] == "BLOCKED"


def test_ambiguous_u1_row_with_x_only_outside_name_is_rejected():
    parsed = gate.declared_symmetries(
        "Gauge[[1]] = {G10, SO, 10};\n"
        "Gauge[[2]] = {B, U[1], hypercharge, gX, False};"
    )
    assert parsed["structured_gauge_rows"][1]["is_u1"] is True
    assert parsed["structured_gauge_rows"][1]["is_named_X"] is False
    assert parsed["u1x_gauged"] is False


def test_complete_looking_legacy_pseudo_sarah_text_cannot_promote_contract():
    report = gate.build_report(model_text=_legacy_pseudo_sarah_model())
    assert report["n_failed"] == 0, report["audit_failures"]
    scaffold = report["executable_scaffold_contract"]
    assert scaffold["u1x_gauged"] is True
    assert scaffold["scalar_charges_match_manuscript"] is True
    assert scaffold["fermion_catalogue_exact"] is True
    assert scaffold["lagrangian"]["real_LagHC_present"] is True
    assert scaffold["lagrangian"]["real_LagNoHC_present"] is True
    assert scaffold["soft_gaugino_absent_in_nonsusy_model"] is True
    assert scaffold["static_inventory_matches_contract"] is True
    assert scaffold["model_syntax_class"] == "legacy_pseudo_sarah_metadata"
    assert scaffold["legacy_pseudo_sarah_grammar"] is True
    assert scaffold["tool_native_sarah_syntax"] is False
    assert scaffold["lagrangian"]["registered_in_GaugeES_LagrangianInput"] is False
    assert scaffold["statically_executable_model_contract"] is False
    assert report["external_model_validation"]["valid"] is False
    assert report["contract_consistent"] is False
    assert report["status"].endswith("__BLOCKED")
    assert report["overall_state"] == "BLOCKED"
    assert report["blocker"] == gate.BLOCKER
    assert gate.exit_code(report, require_consistent=True) != 0


def test_full_static_semantics_plus_bound_external_execution_can_promote_contract():
    model_text = _native_sarah_model()
    report = gate.build_report(
        model_text=model_text,
        external_validation_artifact=_external_attestation(model_text),
    )
    assert report["n_failed"] == 0, report["audit_failures"]
    evidence = report["external_model_validation"]
    assert evidence["valid"] is True
    assert evidence["fresh_for_exact_model_bytes"] is True
    scaffold = report["executable_scaffold_contract"]
    assert scaffold["model_syntax_class"] == "sarah_native"
    assert scaffold["tool_native_sarah_syntax"] is True
    assert scaffold["lagrangian"]["registered_in_GaugeES_LagrangianInput"] is True
    assert report["contract_consistent"] is True
    assert report["status"].endswith("__CONSISTENT")
    assert report["overall_state"] == "PASS"
    assert report["blocker"] is None
    assert report["scientific_blockers"] == []
    assert report["required_resolution"]["selected"] is None
    assert gate.exit_code(report, require_consistent=True) == 0


def test_native_sarah_contract_requires_gaugees_lagrangianinput_registration():
    registration = r"""DEFINITION[GaugeES][LagrangianInput] = {
  {LagHC, {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};
"""
    model_text = _native_sarah_model().replace(registration, "")
    scaffold = gate.declared_symmetries(model_text)
    assert scaffold["gauge_catalogue_exact"] is True
    assert scaffold["scalar_catalogue_exact"] is True
    assert scaffold["fermion_catalogue_exact"] is True
    assert scaffold["lagrangian"]["real_LagHC_present"] is True
    assert scaffold["lagrangian"]["real_LagNoHC_present"] is True
    assert scaffold["lagrangian"]["registered_in_GaugeES_LagrangianInput"] is False
    assert scaffold["tool_native_sarah_syntax"] is False
    assert scaffold["statically_executable_model_contract"] is False


def test_bound_attestation_cannot_promote_legacy_pseudo_sarah_grammar():
    model_text = _legacy_pseudo_sarah_model()
    report = gate.build_report(
        model_text=model_text,
        external_validation_artifact=_external_attestation(model_text),
    )
    assert report["external_model_validation"]["valid"] is True
    assert report["executable_scaffold_contract"][
        "legacy_pseudo_sarah_grammar"
    ] is True
    assert report["executable_scaffold_contract"][
        "statically_executable_model_contract"
    ] is False
    assert report["contract_consistent"] is False
    assert report["overall_state"] == "BLOCKED"


def test_wrong_model_sha256_cannot_reuse_external_execution_attestation():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["model"]["sha256"] = "0" * 64
    report = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )
    evidence = report["external_model_validation"]
    assert evidence["valid"] is False
    assert evidence["fresh_for_exact_model_bytes"] is False
    assert "model_sha256_matches_exact_bytes" in evidence["failures"]
    assert report["contract_consistent"] is False


def test_self_labelled_tool_with_unrelated_command_is_not_external_evidence():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["execution"]["command"] = ["python", "fake_validator.py"]
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "external_process_command_matches_tool" in evidence["failures"]


def test_unbound_boolean_attestation_is_not_external_execution_evidence():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact.pop("input_manifest")
    artifact.pop("evidence")
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "input_manifest_schema_is_supported" in evidence["failures"]
    assert "input_manifest_sha256_matches_entries" in evidence["failures"]
    assert "captured_process_log_is_hash_bound" in evidence["failures"]
    assert "captured_process_log_has_all_required_pass_markers" in evidence[
        "failures"
    ]


def test_manifest_and_process_log_tampering_are_rejected():
    model_text = _native_sarah_model()
    manifest_artifact = _external_attestation(model_text)
    manifest_artifact["input_manifest"]["files"][0]["sha256"] = "f" * 64
    manifest_evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=manifest_artifact,
    )["external_model_validation"]
    assert manifest_evidence["valid"] is False
    assert "input_manifest_sha256_matches_entries" in manifest_evidence["failures"]
    assert "primary_model_is_bound_in_input_manifest" in manifest_evidence[
        "failures"
    ]

    log_artifact = _external_attestation(model_text)
    log_artifact["evidence"]["process_log"]["content"] += "\ntampered"
    log_evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=log_artifact,
    )["external_model_validation"]
    assert log_evidence["valid"] is False
    assert "captured_process_log_is_hash_bound" in log_evidence["failures"]


def test_driver_entry_must_match_shipped_repository_bytes():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    driver = next(
        row
        for row in artifact["input_manifest"]["files"]
        if row["role"] == "validation_driver"
    )
    driver["sha256"] = "a" * 64
    artifact["input_manifest"]["sha256"] = hashlib.sha256(
        gate._canonical_json_bytes(artifact["input_manifest"]["files"])
    ).hexdigest()
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert evidence["checks"]["input_manifest_sha256_matches_entries"] is True
    assert "validation_driver_matches_repository_bytes" in evidence["failures"]


def test_repository_manifest_and_runner_preflight_bind_current_inputs():
    artifact = json.loads(
        gate.EXTERNAL_INPUT_MANIFEST.read_text(encoding="utf-8")
    )
    validation = gate.validate_repository_input_manifest(
        gate.MODEL.read_bytes(), gate.EXTERNAL_DRIVER.read_bytes(), artifact
    )
    assert validation["valid"] is True, validation["failures"]
    assert runner.main(["--preflight-only"]) == 0


def test_external_tool_must_match_native_model_type_and_command():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["tool"] = {"name": "PyR@TE", "version": "3.test"}
    artifact["model"]["format"] = gate.PYRATE_MODEL_FORMAT
    artifact["execution"]["command"] = [
        "pyrate",
        "tools/validate-exact-x-model.wls",
    ]
    artifact["input_manifest"]["files"][0]["format"] = gate.PYRATE_MODEL_FORMAT
    artifact["input_manifest"]["sha256"] = hashlib.sha256(
        gate._canonical_json_bytes(artifact["input_manifest"]["files"])
    ).hexdigest()
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "tool_native_model_format_matches_path" in evidence["failures"]


def test_command_cannot_disable_gauge_invariance_check():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["execution"]["command"].append("--no-CheckGaugeInvariance")
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "gauge_invariance_check_was_not_disabled" in evidence["failures"]


def test_duplicate_or_extra_structured_catalogue_rows_are_rejected():
    base = _native_sarah_model()
    duplicate = gate.build_report(
        model_text=base
        + "\nScalarFields[[6]] = {H10, 1, h10b, 10, -2, 15};\n"
    )
    extra = gate.build_report(
        model_text=base
        + "\nGauge[[3]] = {GY, U[1], hypercharge, gY, False};\n"
        + "FermionFields[[10]] = {Mystery, 1, mystery, 10, 0, 0, 0};\n"
    )
    zero_multiplicity_extra = gate.build_report(
        model_text=base
        + "\nFermionFields[[10]] = {Decorative, 0, decorative, 16, 1, 1};\n"
    )
    assert (
        duplicate["executable_scaffold_contract"]["scalar_catalogue_exact"] is False
    )
    assert (
        duplicate["executable_scaffold_contract"][
            "statically_executable_model_contract"
        ]
        is False
    )
    assert extra["executable_scaffold_contract"]["gauge_catalogue_exact"] is False
    assert extra["executable_scaffold_contract"]["fermion_catalogue_exact"] is False
    assert (
        zero_multiplicity_extra["executable_scaffold_contract"][
            "fermion_catalogue_exact"
        ]
        is False
    )
    assert duplicate["contract_consistent"] is False
    assert extra["contract_consistent"] is False


def test_v2_external_attestation_is_retained_as_legacy_but_cannot_promote():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["schema"] = gate.LEGACY_EXTERNAL_VALIDATION_SCHEMA
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "schema_is_supported" in evidence["failures"]
    assert "legacy_v2_schema_is_not_promoted" in evidence["failures"]


def test_fake_and_mutated_sarah_source_trees_are_rejected():
    with tempfile.TemporaryDirectory() as directory:
        fake_root = Path(directory)
        (fake_root / "SARAH.m").write_text(
            'SA`Version = "4.15.3";\n', encoding="utf-8"
        )
        try:
            runner.verify_trusted_sarah_source_tree(fake_root)
        except RuntimeError as exc:
            assert "not the trusted official 4.15.3 release" in str(exc)
        else:
            raise AssertionError("a fake SARAH tree was accepted")

    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["tool"]["source_tree"]["sha256"] = "0" * 64
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "sarah_source_tree_is_exactly_trusted" in evidence["failures"]


def test_coherently_rehashed_release_manifest_cannot_replace_trust_anchor():
    payload = json.loads(
        gate.TRUSTED_SARAH_RELEASE_MANIFEST.read_text(encoding="utf-8")
    )
    payload["tree"]["files"][0]["sha256"] = "f" * 64
    payload["tree"]["sha256"] = hashlib.sha256(
        gate._canonical_json_bytes(payload["tree"]["files"])
    ).hexdigest()
    manifest_bytes = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    validation = gate.validate_trusted_sarah_release_manifest_bytes(
        manifest_bytes
    )
    assert validation["checks"]["source_tree_sha256_matches_entries"] is True
    assert validation["valid"] is False
    assert "source_tree_sha256_is_exactly_trusted" in validation["failures"]


def test_wolfram_launcher_and_kernel_drift_fail_closed():
    model_text = _native_sarah_model()
    launcher_drift = _external_attestation(model_text)
    launcher = launcher_drift["execution"]["runtime"]["launcher"]
    launcher["sha256_after"] = "b" * 64
    launcher["unchanged_during_execution"] = False
    launcher_evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=launcher_drift,
    )["external_model_validation"]
    assert launcher_evidence["valid"] is False
    assert (
        "resolved_wolfram_launcher_is_hash_bound_and_unchanged"
        in launcher_evidence["failures"]
    )

    kernel_drift = _external_attestation(model_text)
    kernel = kernel_drift["execution"]["runtime"]["kernel"]
    kernel["size_bytes_after"] += 1
    kernel["unchanged_during_execution"] = False
    kernel_evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=kernel_drift,
    )["external_model_validation"]
    assert kernel_evidence["valid"] is False
    assert (
        "resolved_wolfram_kernel_is_hash_bound_and_unchanged"
        in kernel_evidence["failures"]
    )


def test_runtime_marker_spoofing_duplicate_pass_and_fail_marker_are_rejected():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    log = artifact["evidence"]["process_log"]
    check_name = gate.REQUIRED_EXTERNAL_CHECKS[0]
    log["content"] += (
        f"\nEXACT_X_CHECK {check_name} PASS"
        "\nEXACT_X_CHECK invented_check FAIL"
    )
    encoded = log["content"].encode("utf-8")
    log["sha256"] = hashlib.sha256(encoded).hexdigest()
    log["size_bytes"] = len(encoded)
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "captured_process_log_has_all_required_pass_markers" in evidence[
        "failures"
    ]
    assert "captured_process_log_has_no_fail_markers" in evidence["failures"]


def test_source_tree_path_substitution_and_noncanonical_manifest_keys_fail_closed():
    model_text = _native_sarah_model()
    artifact = _external_attestation(model_text)
    artifact["execution"]["command"][-1] = r"C:\external-tools\fake-SARAH"
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["valid"] is False
    assert "sarah_source_tree_is_bound_to_command" in evidence["failures"]

    artifact = _external_attestation(model_text)
    artifact["input_manifest"]["files"][0]["unexpected"] = "ignored"
    artifact["input_manifest"]["sha256"] = hashlib.sha256(
        gate._canonical_json_bytes(
            [
                {
                    "path": item.get("path"),
                    "sha256": item.get("sha256"),
                    "size_bytes": item.get("size_bytes"),
                    "role": item.get("role"),
                    "format": item.get("format"),
                }
                for item in artifact["input_manifest"]["files"]
            ]
        )
    ).hexdigest()
    evidence = gate.build_report(
        model_text=model_text,
        external_validation_artifact=artifact,
    )["external_model_validation"]
    assert evidence["checks"]["input_manifest_sha256_matches_entries"] is True
    assert evidence["valid"] is False
    assert "input_manifest_entries_are_structured" in evidence["failures"]


def test_cli_report_bytes_are_explicit_crlf_on_every_platform(
    monkeypatch, tmp_path: Path, capsys
):
    """The raw-hash-bound reports must not depend on the host newline mode."""
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    report = {
        "contract_consistent": False,
        "n_failed": 0,
        "status": "TEST_BLOCKED",
    }
    markdown = "# Exact-X test\n\nBlocked.\n"
    monkeypatch.setattr(gate, "OUT_JSON", out_json)
    monkeypatch.setattr(gate, "OUT_MD", out_md)
    monkeypatch.setattr(gate, "build_report", lambda: report)
    monkeypatch.setattr(gate, "write_markdown", lambda _report: markdown)

    assert gate.main([]) == 0
    capsys.readouterr()

    for payload in (out_json.read_bytes(), out_md.read_bytes()):
        assert b"\r\n" in payload
        assert payload.replace(b"\r\n", b"").find(b"\n") == -1
    assert json.loads(out_json.read_text(encoding="utf-8")) == report
    assert out_md.read_bytes() == markdown.replace("\n", "\r\n").encode("utf-8")
