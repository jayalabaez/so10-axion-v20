#!/usr/bin/env python3
"""Run and attest the genuine Wolfram/SARAH validation of the V22 model."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_exact_x_sarah_validation_v20 as provenance


ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models/SO10X17SUSYV22/SO10X17SUSYV22.m"
DRIVER = ROOT / "tools/validate-susy-so10x17-v22.wls"
OUTPUT = ROOT / "SUSY_V22_SARAH_VALIDATION.json"
OUTPUT_MD = ROOT / "SUSY_V22_SARAH_VALIDATION.md"
SCHEMA = "susy_so10x17_v22_sarah_validation_v1"
REQUIRED_CHECKS = (
    "model_parse_succeeded",
    "model_initialization_succeeded",
    "supersymmetric_potential_constructed",
    "sarah_anomaly_check_succeeded",
    "sarah_model_check_completed_without_abort",
)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def csha(value: Any) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def input_pins() -> dict[str, dict[str, Any]]:
    out = {}
    for label, path in (("model", MODEL), ("driver", DRIVER), ("runner", Path(__file__).resolve())):
        payload = path.read_bytes()
        out[label] = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(payload), "size_bytes": len(payload)}
    return out


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("schema") != SCHEMA:
        errors.append("schema")
    if report.get("input_pins") != input_pins():
        errors.append("input_pins")
    checks = report.get("checks")
    if not isinstance(checks, dict) or tuple(checks) != REQUIRED_CHECKS or not all(value is True for value in checks.values()):
        errors.append("checks")
    execution = report.get("execution", {})
    if execution.get("process_exit_code") != 0 or execution.get("runtime_probe_exit_code") != 0:
        errors.append("exit_codes")
    if report.get("tool", {}).get("SARAH_version") != "4.15.3":
        errors.append("SARAH_version")
    source = report.get("tool", {}).get("SARAH_source_tree", {})
    if source.get("sha256") != provenance.gate.TRUSTED_SARAH_RELEASE["tree_sha256"]:
        errors.append("SARAH_tree")
    for name in ("launcher", "kernel"):
        row = report.get("tool", {}).get(name, {})
        if row.get("unchanged_during_execution") is not True:
            errors.append(name)
    body = dict(report)
    observed = body.pop("core_sha256", None)
    if observed != csha(body):
        errors.append("core_sha256")
    return errors


def execute(sarah_root: Path, wolframscript: str) -> dict[str, Any]:
    sarah_before = provenance.verify_trusted_sarah_source_tree(sarah_root)
    launcher = provenance._resolve_executable(wolframscript)
    launcher_before = provenance._file_fingerprint(launcher)

    probe_command = [str(launcher), "-code", provenance.gate.WOLFRAM_RUNTIME_PROBE_CODE]
    probe = subprocess.run(probe_command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    probe_log = provenance._combined_process_log(probe)
    if probe.returncode != 0:
        raise RuntimeError(f"Wolfram probe exited {probe.returncode}")
    kernel_marker = provenance._single_marker(r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$", probe_log, "probe kernel")
    probe_version = provenance._single_marker(r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$", probe_log, "probe Wolfram version")
    kernel = provenance._resolve_kernel_path(kernel_marker, launcher)
    kernel_before = provenance._file_fingerprint(kernel)

    command = [str(launcher), "-file", DRIVER.relative_to(ROOT).as_posix(), "--repo-root", str(ROOT), "--sarah-root", str(Path(sarah_before["resolved_root"]))]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    process_log = provenance._combined_process_log(completed)
    sys.stdout.write(process_log)
    if completed.returncode != 0:
        raise RuntimeError(f"V22 SARAH driver exited {completed.returncode}")

    engine_version = provenance._single_marker(r"^V22_SARAH_ENGINE\s+Wolfram\s+(.+?)\s*$", process_log, "driver Wolfram version")
    driver_kernel = provenance._single_marker(r"^V22_SARAH_KERNEL_PATH\s+(.+?)\s*$", process_log, "driver kernel")
    sarah_version = provenance._single_marker(r"^V22_SARAH_TOOL\s+SARAH\s+(\S+)\s*$", process_log, "SARAH version")
    if engine_version != probe_version:
        raise RuntimeError("probe and driver Wolfram versions differ")
    if provenance.gate._portable_path_key(driver_kernel) != provenance.gate._portable_path_key(kernel_marker):
        raise RuntimeError("probe and driver kernels differ")
    if sarah_version != "4.15.3":
        raise RuntimeError(f"unexpected SARAH version {sarah_version}")
    checks = {}
    for name in REQUIRED_CHECKS:
        passes = len(re.findall(rf"^V22_SARAH_CHECK\s+{re.escape(name)}\s+PASS\s*$", process_log, re.MULTILINE))
        fails = len(re.findall(rf"^V22_SARAH_CHECK\s+{re.escape(name)}\s+FAIL\s*$", process_log, re.MULTILINE))
        checks[name] = passes == 1 and fails == 0
    if not all(checks.values()) or re.search(r"^V22_SARAH_CHECK\s+\S+\s+FAIL\s*$", process_log, re.MULTILINE):
        raise RuntimeError("required unique V22 SARAH PASS markers are not complete")

    sarah_after = provenance.verify_trusted_sarah_source_tree(Path(sarah_before["resolved_root"]))
    launcher_after = provenance._file_fingerprint(launcher)
    kernel_after = provenance._file_fingerprint(kernel)
    if sarah_before != sarah_after:
        raise RuntimeError("SARAH tree changed during execution")
    launcher_record = provenance._fingerprint_record(launcher, launcher_before, launcher_after)
    kernel_record = provenance._fingerprint_record(kernel, kernel_before, kernel_after)
    if not launcher_record["unchanged_during_execution"] or not kernel_record["unchanged_during_execution"]:
        raise RuntimeError("Wolfram executable changed during execution")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_pins": input_pins(),
        "tool": {
            "SARAH_version": sarah_version,
            "SARAH_source_tree": {key: sarah_before[key] for key in ("sha256", "file_count", "size_bytes", "resolved_root")},
            "Wolfram_version": engine_version,
            "launcher": launcher_record,
            "kernel": kernel_record,
        },
        "execution": {
            "command": command,
            "process_exit_code": completed.returncode,
            "runtime_probe_command": probe_command,
            "runtime_probe_exit_code": probe.returncode,
            "process_log": provenance._log_record(process_log),
            "runtime_probe_log": provenance._log_record(probe_log),
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": sum(value is not True for value in checks.values()),
        "claim_boundary": {
            "genuine_Wolfram_SARAH_V22_model_initialization_closed": True,
            "full_high_representation_component_superpotential_validated": False,
            "V22_G1_G2_G3_closed": False,
            "canonical_G4_G5_closed": False,
        },
    }
    report["core_sha256"] = csha(report)
    errors = validate_report(report)
    if errors:
        raise RuntimeError("candidate V22 attestation invalid: " + ", ".join(errors))
    return report


def markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# SUSY V22 Wolfram/SARAH validation",
        "",
        f"- Core: `{report['core_sha256']}`",
        f"- SARAH: `{report['tool']['SARAH_version']}`",
        f"- Wolfram: `{report['tool']['Wolfram_version']}`",
        f"- Checks: `{report['n_checks'] - report['n_failed']}/{report['n_checks']}`",
        "",
        "This attests genuine model initialization, anomaly execution and model-check completion. The high-representation component superpotential and V22 G1-G5 remain separately gated.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sarah-root", type=Path)
    parser.add_argument("--wolframscript", default=provenance.discover_wolframscript())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        report = json.loads(OUTPUT.read_text(encoding="utf-8"))
        errors = validate_report(report)
        if errors or OUTPUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise RuntimeError("V22 SARAH attestation drift: " + ", ".join(errors))
        print(report["core_sha256"])
        return 0
    if args.sarah_root is None or not args.wolframscript:
        parser.error("--sarah-root and an available --wolframscript are required")
    report = execute(args.sarah_root, args.wolframscript)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUTPUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
