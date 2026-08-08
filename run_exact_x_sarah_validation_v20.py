#!/usr/bin/env python3
"""Run the hash-bound external SARAH audit and write evidence on real success.

This runner never synthesizes a successful attestation.  It writes the v2
artifact only after the shipped Wolfram driver exits zero, emits every required
PASS marker, identifies its SARAH version, and the gate revalidates the complete
candidate artifact against the current model and driver bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as gate


def load_current_manifest() -> dict[str, Any]:
    """Load and verify the pre-execution manifest against repository bytes."""
    try:
        artifact = json.loads(
            gate.EXTERNAL_INPUT_MANIFEST.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load external input manifest: {exc}") from exc
    validation = gate.validate_repository_input_manifest(
        gate.MODEL.read_bytes(), gate.EXTERNAL_DRIVER.read_bytes(), artifact
    )
    if not validation["valid"]:
        raise RuntimeError(
            "external input manifest is stale: "
            + ", ".join(validation["failures"])
        )
    return artifact


def build_attestation(
    *,
    command: list[str],
    exit_code: int,
    process_log: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Construct and self-validate an attestation from captured process data."""
    model_bytes = gate.MODEL.read_bytes()
    tool_match = re.search(
        r"(?m)^EXACT_X_TOOL\s+SARAH\s+(\S+)\s*$", process_log
    )
    marker_results = {
        name: bool(
            re.search(
                rf"(?m)^EXACT_X_CHECK\s+{re.escape(name)}\s+PASS\s*$",
                process_log,
            )
        )
        for name in gate.REQUIRED_EXTERNAL_CHECKS
    }
    if exit_code != 0:
        raise RuntimeError(f"SARAH driver exited with status {exit_code}")
    if tool_match is None:
        raise RuntimeError("SARAH version marker is absent from process output")
    missing = [name for name, passed in marker_results.items() if not passed]
    if missing:
        raise RuntimeError("required PASS markers are absent: " + ", ".join(missing))
    if re.search(r"(?m)^EXACT_X_CHECK\s+\S+\s+FAIL\s*$", process_log):
        raise RuntimeError("process output contains a FAIL marker")

    log_bytes = process_log.encode("utf-8")
    artifact = {
        "schema": gate.EXTERNAL_VALIDATION_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": {
            "path": gate.MODEL_REPOSITORY_PATH,
            "sha256": hashlib.sha256(model_bytes).hexdigest(),
            "size_bytes": len(model_bytes),
            "format": gate.SARAH_MODEL_FORMAT,
        },
        "tool": {"name": "SARAH", "version": tool_match.group(1)},
        "execution": {
            "external_process_executed": True,
            "command": command,
            "process_exit_code": exit_code,
        },
        "input_manifest": manifest,
        "evidence": {
            "process_log": {
                "encoding": "utf-8",
                "content": process_log,
                "sha256": hashlib.sha256(log_bytes).hexdigest(),
                "size_bytes": len(log_bytes),
            }
        },
        "checks": marker_results,
    }
    validation = gate.validate_external_model_artifact(
        model_bytes,
        artifact,
        driver_bytes=gate.EXTERNAL_DRIVER.read_bytes(),
    )
    if not validation["valid"]:
        raise RuntimeError(
            "candidate attestation failed local schema validation: "
            + ", ".join(validation["failures"])
        )
    return artifact


def run_external_validation(
    *,
    sarah_root: Path,
    wolframscript: str,
    output: Path,
) -> None:
    manifest = load_current_manifest()
    sarah_entry = sarah_root.resolve() / "SARAH.m"
    if not sarah_entry.is_file():
        raise RuntimeError(f"SARAH.m not found at {sarah_entry}")

    driver_argument = gate.EXTERNAL_DRIVER_REPOSITORY_PATH
    command = [
        wolframscript,
        "-file",
        driver_argument,
        "--repo-root",
        str(gate.ROOT),
        "--sarah-root",
        str(sarah_root.resolve()),
    ]
    completed = subprocess.run(
        command,
        cwd=gate.ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    process_log = completed.stdout
    if completed.stderr:
        process_log += (
            "" if not process_log or process_log.endswith("\n") else "\n"
        ) + completed.stderr
    sys.stdout.write(process_log)
    artifact = build_attestation(
        command=command,
        exit_code=completed.returncode,
        process_log=process_log,
        manifest=manifest,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sarah-root", type=Path)
    parser.add_argument("--wolframscript")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--output", type=Path, default=gate.EXTERNAL_VALIDATION)
    args = parser.parse_args(argv)
    try:
        manifest = load_current_manifest()
        if args.preflight_only:
            print(
                "Exact-X external bundle is current: "
                f"{manifest['sha256']}"
            )
            return 0
        if args.sarah_root is None:
            parser.error("--sarah-root is required unless --preflight-only is used")
        wolframscript = args.wolframscript or shutil.which("wolframscript")
        if not wolframscript:
            raise RuntimeError(
                "wolframscript is unavailable; provide --wolframscript explicitly"
            )
        run_external_validation(
            sarah_root=args.sarah_root,
            wolframscript=wolframscript,
            output=args.output,
        )
    except RuntimeError as exc:
        print(f"external SARAH validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote verified external attestation: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
