#!/usr/bin/env python3
"""Run the proof-grade external SARAH audit and write evidence on real success.

The runner never synthesizes a successful attestation.  Version 3 accepts only
the exact official SARAH 4.15.3 source tree frozen by the repository, probes a
real Wolfram runtime, fingerprints its resolved launcher and kernel before and
after the validation process, and writes an artifact only after the shipped
driver exits zero with every unique required PASS marker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as gate


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _log_record(content: str) -> dict[str, Any]:
    encoded = content.encode("utf-8")
    return {
        "encoding": "utf-8",
        "content": content,
        "sha256": _sha256(encoded),
        "size_bytes": len(encoded),
    }


def _combined_process_log(completed: subprocess.CompletedProcess[str]) -> str:
    content = completed.stdout
    if completed.stderr:
        content += ("" if not content or content.endswith("\n") else "\n")
        content += completed.stderr
    return content


def _single_marker(pattern: str, content: str, label: str) -> str:
    matches = re.findall(pattern, content, re.MULTILINE)
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one {label} marker, observed {len(matches)}"
        )
    value = matches[0].strip()
    if not value:
        raise RuntimeError(f"{label} marker is empty")
    return value


def load_trusted_release_manifest() -> tuple[dict[str, Any], bytes]:
    try:
        manifest_bytes = gate.TRUSTED_SARAH_RELEASE_MANIFEST.read_bytes()
    except OSError as exc:
        raise RuntimeError(
            f"cannot load trusted SARAH release manifest: {exc}"
        ) from exc
    validation = gate.validate_trusted_sarah_release_manifest_bytes(
        manifest_bytes
    )
    if not validation["valid"]:
        raise RuntimeError(
            "trusted SARAH release manifest is invalid: "
            + ", ".join(validation["failures"])
        )
    return json.loads(manifest_bytes.decode("utf-8")), manifest_bytes


def load_current_manifest() -> dict[str, Any]:
    """Load and verify the pre-execution manifest against repository bytes."""
    _, trusted_release_bytes = load_trusted_release_manifest()
    try:
        artifact = json.loads(
            gate.EXTERNAL_INPUT_MANIFEST.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load external input manifest: {exc}") from exc
    validation = gate.validate_repository_input_manifest(
        gate.MODEL.read_bytes(),
        gate.EXTERNAL_DRIVER.read_bytes(),
        artifact,
        trusted_release_manifest_bytes=trusted_release_bytes,
    )
    if not validation["valid"]:
        raise RuntimeError(
            "external input manifest is stale: "
            + ", ".join(validation["failures"])
        )
    return artifact


def snapshot_sarah_source_tree(sarah_root: Path) -> dict[str, Any]:
    """Hash every regular file and reject links/special entries fail-closed."""
    try:
        resolved_root = sarah_root.resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(f"cannot resolve SARAH root {sarah_root}: {exc}") from exc
    if not resolved_root.is_dir():
        raise RuntimeError(f"SARAH root is not a directory: {resolved_root}")

    entries: list[dict[str, Any]] = []
    for path in sorted(
        resolved_root.rglob("*"),
        key=lambda item: item.relative_to(resolved_root).as_posix(),
    ):
        relative = path.relative_to(resolved_root).as_posix()
        if path.is_symlink():
            raise RuntimeError(f"SARAH source tree contains a link: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError(
                f"SARAH source tree contains a non-regular entry: {relative}"
            )
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise RuntimeError(f"cannot read SARAH source file {relative}: {exc}") from exc
        entries.append(
            {
                "path": relative,
                "sha256": _sha256(payload),
                "size_bytes": len(payload),
            }
        )

    return {
        "schema": gate.SARAH_SOURCE_TREE_SNAPSHOT_SCHEMA,
        "resolved_root": str(resolved_root),
        "sha256": _sha256(gate._canonical_json_bytes(entries)),
        "file_count": len(entries),
        "size_bytes": sum(item["size_bytes"] for item in entries),
        "files": entries,
    }


def verify_trusted_sarah_source_tree(sarah_root: Path) -> dict[str, Any]:
    trusted_manifest, _ = load_trusted_release_manifest()
    snapshot = snapshot_sarah_source_tree(sarah_root)
    expected_tree = trusted_manifest["tree"]
    mismatches = []
    for field in ("sha256", "file_count", "size_bytes"):
        if snapshot[field] != expected_tree[field]:
            mismatches.append(
                f"{field}={snapshot[field]!r} (expected {expected_tree[field]!r})"
            )
    if snapshot["files"] != expected_tree["files"]:
        mismatches.append("per-file canonical manifest differs")
    if mismatches:
        raise RuntimeError(
            "SARAH source tree is not the trusted official 4.15.3 release: "
            + "; ".join(mismatches)
        )
    return snapshot


def _resolve_executable(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        located = shutil.which(value)
        if located is None:
            raise RuntimeError(f"executable is unavailable: {value}")
        candidate = Path(located)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(f"cannot resolve executable {value}: {exc}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"resolved executable is not a regular file: {resolved}")
    return resolved


def discover_wolframscript() -> str | None:
    """Find WolframScript on PATH or in official Windows install layouts."""
    located = shutil.which("wolframscript")
    if located is not None:
        return located
    candidates: list[Path] = []
    for variable in ("ProgramFiles", "ProgramW6432", "LOCALAPPDATA"):
        base = os.environ.get(variable)
        if not base:
            continue
        wolfram_root = Path(base) / "Wolfram Research"
        if not wolfram_root.is_dir():
            continue
        candidates.extend(wolfram_root.glob("WolframScript/wolframscript.exe"))
        candidates.extend(
            wolfram_root.glob("Wolfram Engine/*/Executables/wolframscript.exe")
        )
        candidates.extend(
            wolfram_root.glob("Wolfram Engine/*/wolframscript.exe")
        )
    regular = sorted(
        {candidate.resolve() for candidate in candidates if candidate.is_file()},
        key=lambda path: str(path).casefold(),
        reverse=True,
    )
    return str(regular[0]) if regular else None


def _resolve_kernel_path(marker_path: str, launcher: Path) -> Path:
    value = marker_path.strip().strip('"')
    candidate = Path(value)
    if not candidate.is_absolute():
        located = shutil.which(value)
        if located is not None:
            candidate = Path(located)
        else:
            candidate = launcher.parent / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(
            f"Wolfram kernel marker does not resolve to a file: {marker_path}: {exc}"
        ) from exc
    if not resolved.is_file():
        raise RuntimeError(f"resolved Wolfram kernel is not a file: {resolved}")
    return resolved


def _file_fingerprint(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"cannot fingerprint executable {path}: {exc}") from exc
    return {"sha256": _sha256(payload), "size_bytes": len(payload)}


def _fingerprint_record(
    path: Path,
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    return {
        "resolved_path": str(path),
        "sha256_before": before["sha256"],
        "size_bytes_before": before["size_bytes"],
        "sha256_after": after["sha256"],
        "size_bytes_after": after["size_bytes"],
        "unchanged_during_execution": before == after,
    }


def build_attestation(
    *,
    command: list[str],
    exit_code: int,
    process_log: str,
    runtime_probe_command: list[str],
    runtime_probe_exit_code: int,
    runtime_probe_log: str,
    manifest: dict[str, Any],
    sarah_snapshot_before: dict[str, Any],
    sarah_snapshot_after: dict[str, Any],
    launcher_record: dict[str, Any],
    kernel_record: dict[str, Any],
) -> dict[str, Any]:
    """Construct and self-validate an attestation from captured process data."""
    model_bytes = gate.MODEL.read_bytes()
    tool_version = _single_marker(
        r"^EXACT_X_TOOL\s+SARAH\s+(\S+)\s*$",
        process_log,
        "SARAH version",
    )
    driver_engine_version = _single_marker(
        r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$",
        process_log,
        "driver Wolfram version",
    )
    probe_engine_version = _single_marker(
        r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$",
        runtime_probe_log,
        "probe Wolfram version",
    )
    driver_kernel_path = _single_marker(
        r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$",
        process_log,
        "driver kernel path",
    )
    probe_kernel_path = _single_marker(
        r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$",
        runtime_probe_log,
        "probe kernel path",
    )
    marker_results = {
        name: len(
            re.findall(
                rf"^EXACT_X_CHECK\s+{re.escape(name)}\s+PASS\s*$",
                process_log,
                re.MULTILINE,
            )
        )
        == 1
        for name in gate.REQUIRED_EXTERNAL_CHECKS
    }
    if runtime_probe_exit_code != 0:
        raise RuntimeError(
            f"Wolfram runtime probe exited with status {runtime_probe_exit_code}"
        )
    if exit_code != 0:
        raise RuntimeError(f"SARAH driver exited with status {exit_code}")
    if tool_version != gate.TRUSTED_SARAH_RELEASE["version"]:
        raise RuntimeError(
            f"SARAH reported {tool_version}, expected trusted 4.15.3"
        )
    if driver_engine_version != probe_engine_version:
        raise RuntimeError("probe and driver reported different Wolfram versions")
    if gate._portable_path_key(driver_kernel_path) != gate._portable_path_key(
        probe_kernel_path
    ):
        raise RuntimeError("probe and driver reported different Wolfram kernels")
    missing = [name for name, passed in marker_results.items() if not passed]
    if missing:
        raise RuntimeError(
            "required PASS markers are absent or duplicated: " + ", ".join(missing)
        )
    if re.search(r"^EXACT_X_CHECK\s+\S+\s+FAIL\s*$", process_log, re.MULTILINE):
        raise RuntimeError("process output contains a FAIL marker")
    if sarah_snapshot_before != sarah_snapshot_after:
        raise RuntimeError("SARAH source tree changed during external execution")
    if launcher_record["unchanged_during_execution"] is not True:
        raise RuntimeError("resolved Wolfram launcher changed during execution")
    if kernel_record["unchanged_during_execution"] is not True:
        raise RuntimeError("resolved Wolfram kernel changed during execution")

    _, trusted_release_bytes = load_trusted_release_manifest()
    source_tree_summary = {
        key: sarah_snapshot_before[key]
        for key in ("schema", "resolved_root", "sha256", "file_count", "size_bytes")
    }
    source_tree_summary.update(
        {
            "verified_against_trusted_release_manifest": True,
            "unchanged_during_execution": True,
        }
    )
    artifact = {
        "schema": gate.EXTERNAL_VALIDATION_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": {
            "path": gate.MODEL_REPOSITORY_PATH,
            "sha256": _sha256(model_bytes),
            "size_bytes": len(model_bytes),
            "format": gate.SARAH_MODEL_FORMAT,
        },
        "tool": {
            "name": "SARAH",
            "version": tool_version,
            "trusted_release_manifest": {
                "path": gate.TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
                "sha256": _sha256(trusted_release_bytes),
                "size_bytes": len(trusted_release_bytes),
            },
            "source_tree": source_tree_summary,
        },
        "execution": {
            "external_process_executed": True,
            "command": command,
            "process_exit_code": exit_code,
            "runtime_probe_command": runtime_probe_command,
            "runtime_probe_exit_code": runtime_probe_exit_code,
            "runtime": {
                "wolfram_version": driver_engine_version,
                "launcher": launcher_record,
                "kernel": kernel_record,
            },
        },
        "input_manifest": manifest,
        "evidence": {
            "runtime_probe_log": _log_record(runtime_probe_log),
            "process_log": _log_record(process_log),
        },
        "checks": marker_results,
    }
    validation = gate.validate_external_model_artifact(
        model_bytes,
        artifact,
        driver_bytes=gate.EXTERNAL_DRIVER.read_bytes(),
        trusted_release_manifest_bytes=trusted_release_bytes,
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
    sarah_snapshot_before = verify_trusted_sarah_source_tree(sarah_root)
    resolved_sarah_root = Path(sarah_snapshot_before["resolved_root"])
    launcher = _resolve_executable(wolframscript)
    launcher_before = _file_fingerprint(launcher)

    runtime_probe_command = [
        str(launcher),
        "-code",
        gate.WOLFRAM_RUNTIME_PROBE_CODE,
    ]
    probe = subprocess.run(
        runtime_probe_command,
        cwd=gate.ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    runtime_probe_log = _combined_process_log(probe)
    sys.stdout.write(runtime_probe_log)
    if probe.returncode != 0:
        raise RuntimeError(
            f"Wolfram runtime probe exited with status {probe.returncode}"
        )
    probe_engine_version = _single_marker(
        r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$",
        runtime_probe_log,
        "probe Wolfram version",
    )
    if not probe_engine_version:
        raise RuntimeError("Wolfram runtime probe returned an empty version")
    probe_kernel_marker = _single_marker(
        r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$",
        runtime_probe_log,
        "probe kernel path",
    )
    kernel = _resolve_kernel_path(probe_kernel_marker, launcher)
    kernel_before = _file_fingerprint(kernel)

    driver_argument = gate.EXTERNAL_DRIVER_REPOSITORY_PATH
    command = [
        str(launcher),
        "-file",
        driver_argument,
        "--repo-root",
        str(gate.ROOT),
        "--sarah-root",
        str(resolved_sarah_root),
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
    process_log = _combined_process_log(completed)
    sys.stdout.write(process_log)

    sarah_snapshot_after = snapshot_sarah_source_tree(resolved_sarah_root)
    launcher_after = _file_fingerprint(launcher)
    kernel_after = _file_fingerprint(kernel)
    launcher_record = _fingerprint_record(
        launcher, launcher_before, launcher_after
    )
    kernel_record = _fingerprint_record(kernel, kernel_before, kernel_after)
    artifact = build_attestation(
        command=command,
        exit_code=completed.returncode,
        process_log=process_log,
        runtime_probe_command=runtime_probe_command,
        runtime_probe_exit_code=probe.returncode,
        runtime_probe_log=runtime_probe_log,
        manifest=manifest,
        sarah_snapshot_before=sarah_snapshot_before,
        sarah_snapshot_after=sarah_snapshot_after,
        launcher_record=launcher_record,
        kernel_record=kernel_record,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_name(output.name + ".tmp")
    temporary_output.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary_output.replace(output)


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
            message = f"Exact-X external bundle is current: {manifest['sha256']}"
            if args.sarah_root is not None:
                snapshot = verify_trusted_sarah_source_tree(args.sarah_root)
                message += f"; trusted SARAH tree: {snapshot['sha256']}"
            if args.wolframscript is not None:
                launcher = _resolve_executable(args.wolframscript)
                fingerprint = _file_fingerprint(launcher)
                message += (
                    f"; resolved Wolfram launcher: {launcher} "
                    f"({fingerprint['sha256']})"
                )
            print(message)
            return 0
        if args.sarah_root is None:
            parser.error("--sarah-root is required unless --preflight-only is used")
        wolframscript = args.wolframscript or discover_wolframscript()
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
