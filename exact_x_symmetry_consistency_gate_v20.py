#!/usr/bin/env python3
"""Fail-closed audit of the repository's X/Phi17 symmetry contract.

The manuscript is authoritative for the scientific model: it gauges a
primitive U(1)_X and assigns X(Phi17)=17.  The repository supplies a native
non-supersymmetric SARAH input for the complete anomaly-cancelling charge
catalogue and a content-addressed external validation bundle.  Static syntax
is necessary but is not treated as proof that SARAH actually executed.

A successful audit exits zero by default even when the end-to-end contract is
blocked solely on absent external execution evidence.  Strict callers may
pass ``--require-consistent`` to require a current, hash-bound SARAH run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "axion_so10_theory_v20.tex"
MODEL = ROOT / "models" / "SO10Z17AxionV20.m"
FILTER = ROOT / "nonsusy_z17_pq_potential_filter_v20.py"
OUT_JSON = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"
OUT_MD = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md"
EXTERNAL_VALIDATION = (
    ROOT / "models" / "EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"
)
EXTERNAL_INPUT_MANIFEST = (
    ROOT / "models" / "EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json"
)
EXTERNAL_DRIVER = ROOT / "tools" / "validate-exact-x-model.wls"
TRUSTED_SARAH_RELEASE_MANIFEST = (
    ROOT / "models" / "SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"
)

LEGACY_EXTERNAL_VALIDATION_SCHEMA = "so10-exact-x-external-model-validation-v2"
EXTERNAL_VALIDATION_SCHEMA = "so10-exact-x-external-model-validation-v3"
LEGACY_EXTERNAL_INPUT_MANIFEST_SCHEMA = "so10-exact-x-input-manifest-v1"
EXTERNAL_INPUT_MANIFEST_SCHEMA = "so10-exact-x-input-manifest-v2"
TRUSTED_SARAH_RELEASE_MANIFEST_SCHEMA = "sarah-canonical-source-tree-v1"
SARAH_SOURCE_TREE_SNAPSHOT_SCHEMA = "sarah-source-tree-snapshot-v1"
SARAH_MODEL_FORMAT = "sarah-mathematica"
PYRATE_MODEL_FORMAT = "pyrate-yaml"
MODEL_REPOSITORY_PATH = str(MODEL.relative_to(ROOT)).replace("\\", "/")
EXTERNAL_DRIVER_REPOSITORY_PATH = str(EXTERNAL_DRIVER.relative_to(ROOT)).replace(
    "\\", "/"
)
EXTERNAL_DRIVER_FORMAT = "wolfram-language"
TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH = str(
    TRUSTED_SARAH_RELEASE_MANIFEST.relative_to(ROOT)
).replace("\\", "/")
TRUSTED_SARAH_RELEASE_MANIFEST_FORMAT = "sarah-source-tree-manifest"

# Trust anchors independently obtained from the official SARAH 4.15.3
# distribution.  The full per-file manifest is repository-bound below; these
# constants prevent a coherently edited manifest from silently becoming a new
# trusted release.
TRUSTED_SARAH_RELEASE = {
    "name": "SARAH",
    "version": "4.15.3",
    "archive_filename": "SARAH-4.15.3.tar.gz",
    "archive_url": (
        "https://sarah.hepforge.org/downloads/?f=SARAH-4.15.3.tar.gz"
    ),
    "archive_sha256": (
        "6ee5c12d21a38f9de7f08b5b8db368b6653d7bfbcc8e45189016be87743729fb"
    ),
    "archive_size_bytes": 2_902_331,
    "tree_sha256": (
        "de92b2de859efa7a0c4f5fdfb642d9f1ff8e1b071057bc8d4c295f6e2b6f8337"
    ),
    "tree_file_count": 1_056,
    "tree_size_bytes": 20_165_588,
}

WOLFRAM_RUNTIME_PROBE_CODE = (
    'Print["EXACT_X_ENGINE Wolfram " <> ToString[$Version]]; '
    'Print["EXACT_X_KERNEL_PATH " <> ToString[First[$CommandLine]]]'
)

STATIC_CONTRACT_BLOCKER = "AUTHORITATIVE_GAUGED_U1X_CONTRACT_MISMATCH"
EXTERNAL_EXECUTION_BLOCKER = (
    "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
)
# Backward-compatible name for callers that classify malformed static inputs.
BLOCKER = STATIC_CONTRACT_BLOCKER

EXPECTED_SCALAR_CHARGES = {
    "Phi210": (0, 0),
    "Delta126bar": (-2, -2),
    "H10": (-2, -2),
    "S": (4, 4),
    "Phi17": (0, 17),
}
EXPECTED_SCALAR_REPRESENTATIONS = {
    "Phi210": "210",
    "Delta126bar": "126",
    "H10": "10",
    "S": "1",
    "Phi17": "1",
}
EXPECTED_FERMION_SECTORS = (
    ("16", (1, 1), 5, "three F families plus P and R"),
    ("16", (2, 2), 5, "five spectator s fields"),
    ("-16", (-6, -6), 5, "five spectator b fields"),
    ("16", (-3, 14), 1, "Q"),
    ("-16", (-1, 16), 1, "Pbar"),
    ("-16", (3, 3), 1, "Qbar"),
    ("-16", (-1, -18), 1, "Rbar"),
)

REQUIRED_EXTERNAL_CHECKS = (
    "model_parse_succeeded",
    "model_initialization_succeeded",
    "lagrangian_construction_succeeded",
    "gauge_invariance_check_succeeded",
    "anomaly_check_succeeded",
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _valid_sha256(value: object) -> bool:
    return bool(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def build_external_input_manifest(
    model_bytes: bytes,
    driver_bytes: bytes,
    trusted_release_manifest_bytes: bytes,
) -> dict[str, Any]:
    """Build the canonical three-file manifest consumed by the SARAH runner."""
    files = [
        {
            "path": MODEL_REPOSITORY_PATH,
            "sha256": _sha256(model_bytes),
            "size_bytes": len(model_bytes),
            "role": "primary_model",
            "format": SARAH_MODEL_FORMAT,
        },
        {
            "path": EXTERNAL_DRIVER_REPOSITORY_PATH,
            "sha256": _sha256(driver_bytes),
            "size_bytes": len(driver_bytes),
            "role": "validation_driver",
            "format": EXTERNAL_DRIVER_FORMAT,
        },
        {
            "path": TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
            "sha256": _sha256(trusted_release_manifest_bytes),
            "size_bytes": len(trusted_release_manifest_bytes),
            "role": "trusted_sarah_release_manifest",
            "format": TRUSTED_SARAH_RELEASE_MANIFEST_FORMAT,
        },
    ]
    return {
        "schema": EXTERNAL_INPUT_MANIFEST_SCHEMA,
        "sha256": _sha256(_canonical_json_bytes(files)),
        "files": files,
    }


def validate_repository_input_manifest(
    model_bytes: bytes,
    driver_bytes: bytes,
    artifact: object,
    *,
    trusted_release_manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Check that the shipped pre-execution manifest binds current inputs."""
    if trusted_release_manifest_bytes is None:
        try:
            trusted_release_manifest_bytes = TRUSTED_SARAH_RELEASE_MANIFEST.read_bytes()
        except OSError:
            trusted_release_manifest_bytes = b""
    trusted_release_validation = validate_trusted_sarah_release_manifest_bytes(
        trusted_release_manifest_bytes
    )
    expected = build_external_input_manifest(
        model_bytes, driver_bytes, trusted_release_manifest_bytes
    )
    payload = artifact if isinstance(artifact, dict) else {}
    checks = {
        "artifact_is_structured_json_object": isinstance(artifact, dict),
        "schema_is_supported": payload.get("schema")
        == EXTERNAL_INPUT_MANIFEST_SCHEMA,
        "files_match_exact_repository_inputs": payload.get("files")
        == expected["files"],
        "manifest_sha256_matches_exact_entries": payload.get("sha256")
        == expected["sha256"],
        "trusted_sarah_release_manifest_is_canonical": (
            trusted_release_validation["valid"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "source": str(EXTERNAL_INPUT_MANIFEST.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "present": isinstance(artifact, dict),
        "expected": expected,
        "checks": checks,
        "failures": failures,
        "valid": not failures,
        "role": (
            "Pre-execution content manifest only; it is not an external "
            "SARAH execution attestation."
        ),
        "trusted_sarah_release_manifest": trusted_release_validation,
    }


def _safe_repository_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    return bool(
        not path.is_absolute()
        and not re.match(r"^[A-Za-z]:", normalized)
        and ".." not in path.parts
    )


def _safe_source_tree_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return bool(
        not path.is_absolute()
        and value == path.as_posix()
        and value not in {".", ".."}
        and ".." not in path.parts
        and all(part not in {"", "."} for part in path.parts)
    )


def _safe_absolute_execution_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if any(character in value for character in "\r\n\x00"):
        return False
    return bool(PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute())


def _portable_path_key(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.replace("\\", "/").rstrip("/").casefold()


def validate_trusted_sarah_release_manifest_bytes(
    manifest_bytes: bytes,
) -> dict[str, Any]:
    """Validate the frozen, full-file SARAH 4.15.3 release trust anchor."""
    try:
        artifact: object = json.loads(manifest_bytes.decode("utf-8"))
        decode_error = None
    except (UnicodeError, json.JSONDecodeError) as exc:
        artifact = None
        decode_error = f"{type(exc).__name__}: {exc}"
    payload = artifact if isinstance(artifact, dict) else {}
    release = payload.get("release") if isinstance(payload.get("release"), dict) else {}
    archive = release.get("archive") if isinstance(release.get("archive"), dict) else {}
    tree = payload.get("tree") if isinstance(payload.get("tree"), dict) else {}
    files = tree.get("files") if isinstance(tree.get("files"), list) else []

    normalized_files: list[dict[str, Any]] = []
    entries_valid = bool(files)
    for item in files:
        if not isinstance(item, dict):
            entries_valid = False
            continue
        normalized = {
            "path": item.get("path"),
            "sha256": item.get("sha256"),
            "size_bytes": item.get("size_bytes"),
        }
        normalized_files.append(normalized)
        entries_valid = bool(
            entries_valid
            and set(item) == {"path", "sha256", "size_bytes"}
            and _safe_source_tree_path(normalized["path"])
            and _valid_sha256(normalized["sha256"])
            and type(normalized["size_bytes"]) is int
            and normalized["size_bytes"] >= 0
        )

    paths = [item.get("path") for item in normalized_files]
    sorted_unique_paths = bool(
        paths == sorted(paths)
        and len(paths) == len(set(paths))
    )
    calculated_tree_sha256 = _sha256(_canonical_json_bytes(normalized_files))
    calculated_tree_size_bytes = sum(
        item["size_bytes"]
        for item in normalized_files
        if type(item.get("size_bytes")) is int
    )
    checks = {
        "artifact_is_structured_json_object": isinstance(artifact, dict),
        "schema_is_supported": payload.get("schema")
        == TRUSTED_SARAH_RELEASE_MANIFEST_SCHEMA,
        "release_name_is_sarah": release.get("name")
        == TRUSTED_SARAH_RELEASE["name"],
        "release_version_is_exactly_trusted": release.get("version")
        == TRUSTED_SARAH_RELEASE["version"],
        "upstream_archive_filename_is_exactly_trusted": archive.get("filename")
        == TRUSTED_SARAH_RELEASE["archive_filename"],
        "upstream_archive_url_is_exactly_trusted": archive.get("url")
        == TRUSTED_SARAH_RELEASE["archive_url"],
        "upstream_archive_sha256_is_exactly_trusted": archive.get("sha256")
        == TRUSTED_SARAH_RELEASE["archive_sha256"],
        "upstream_archive_size_is_exactly_trusted": type(
            archive.get("size_bytes")
        )
        is int
        and archive.get("size_bytes")
        == TRUSTED_SARAH_RELEASE["archive_size_bytes"],
        "source_tree_entries_are_strictly_structured": entries_valid,
        "source_tree_paths_are_sorted_and_unique": sorted_unique_paths,
        "source_tree_file_count_matches_entries": type(tree.get("file_count"))
        is int
        and tree.get("file_count") == len(normalized_files),
        "source_tree_size_matches_entries": type(tree.get("size_bytes")) is int
        and tree.get("size_bytes") == calculated_tree_size_bytes,
        "source_tree_sha256_matches_entries": _valid_sha256(tree.get("sha256"))
        and tree.get("sha256") == calculated_tree_sha256,
        "source_tree_sha256_is_exactly_trusted": tree.get("sha256")
        == TRUSTED_SARAH_RELEASE["tree_sha256"],
        "source_tree_file_count_is_exactly_trusted": tree.get("file_count")
        == TRUSTED_SARAH_RELEASE["tree_file_count"],
        "source_tree_size_is_exactly_trusted": tree.get("size_bytes")
        == TRUSTED_SARAH_RELEASE["tree_size_bytes"],
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "source": TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
        "present": isinstance(artifact, dict),
        "decode_error": decode_error,
        "schema": payload.get("schema"),
        "release": release,
        "tree": {
            "sha256": tree.get("sha256"),
            "file_count": tree.get("file_count"),
            "size_bytes": tree.get("size_bytes"),
            "calculated_sha256": calculated_tree_sha256,
            "calculated_file_count": len(normalized_files),
            "calculated_size_bytes": calculated_tree_size_bytes,
        },
        "files": normalized_files,
        "checks": checks,
        "failures": failures,
        "valid": not failures,
    }


def _hash_bound_log_record(record: object) -> tuple[bool, str]:
    payload = record if isinstance(record, dict) else {}
    content = payload.get("content")
    encoded = content.encode("utf-8") if isinstance(content, str) else b""
    valid = bool(
        isinstance(content, str)
        and bool(content.strip())
        and payload.get("encoding") == "utf-8"
        and _valid_sha256(payload.get("sha256"))
        and payload.get("sha256") == _sha256(encoded)
        and type(payload.get("size_bytes")) is int
        and payload.get("size_bytes") == len(encoded)
    )
    return valid, content if isinstance(content, str) else ""


def _single_log_marker(pattern: str, content: str) -> str | None:
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches[0].strip() if len(matches) == 1 else None


def _parse_utc_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_external_model_artifact(
    model_bytes: bytes,
    artifact: object,
    *,
    driver_bytes: bytes | None = None,
    trusted_release_manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Validate a fail-closed, proof-grade external SARAH attestation.

    The content SHA-256, rather than a checkout-dependent file timestamp,
    defines freshness: an attestation is current only for the exact model
    bytes that the gate is auditing.  The timestamp remains mandatory and
    must not be implausibly in the future, but an unchanged historical model
    does not become irreproducible merely because it was checked out again.

    Version 3 additionally requires the exact official SARAH 4.15.3 source
    tree, before/after fingerprints of the resolved Wolfram launcher and
    kernel, matching runtime/version markers from an independent probe and the
    validation process, and hash-bound logs for both processes.  Version 2 is
    retained as a named legacy schema but can no longer promote this gate.

    This function never upgrades older reduced-sector LIVE_* dumps into
    whole-model evidence.
    """
    expected_sha256 = _sha256(model_bytes)
    expected_bytes = len(model_bytes)
    if driver_bytes is None:
        try:
            driver_bytes = EXTERNAL_DRIVER.read_bytes()
        except OSError:
            driver_bytes = None
    expected_driver_sha256 = (
        None if driver_bytes is None else _sha256(driver_bytes)
    )
    expected_driver_bytes = None if driver_bytes is None else len(driver_bytes)
    if trusted_release_manifest_bytes is None:
        try:
            trusted_release_manifest_bytes = TRUSTED_SARAH_RELEASE_MANIFEST.read_bytes()
        except OSError:
            trusted_release_manifest_bytes = b""
    trusted_release_validation = validate_trusted_sarah_release_manifest_bytes(
        trusted_release_manifest_bytes
    )
    expected_release_manifest_sha256 = _sha256(trusted_release_manifest_bytes)
    expected_release_manifest_size = len(trusted_release_manifest_bytes)
    payload = artifact if isinstance(artifact, dict) else {}
    model = payload.get("model") if isinstance(payload.get("model"), dict) else {}
    tool = payload.get("tool") if isinstance(payload.get("tool"), dict) else {}
    execution = (
        payload.get("execution")
        if isinstance(payload.get("execution"), dict)
        else {}
    )
    checks_payload = (
        payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
    )
    manifest = (
        payload.get("input_manifest")
        if isinstance(payload.get("input_manifest"), dict)
        else {}
    )
    manifest_files = (
        manifest.get("files") if isinstance(manifest.get("files"), list) else []
    )
    evidence = (
        payload.get("evidence") if isinstance(payload.get("evidence"), dict) else {}
    )
    process_log = (
        evidence.get("process_log")
        if isinstance(evidence.get("process_log"), dict)
        else {}
    )

    source_tree = (
        tool.get("source_tree")
        if isinstance(tool.get("source_tree"), dict)
        else {}
    )
    release_binding = (
        tool.get("trusted_release_manifest")
        if isinstance(tool.get("trusted_release_manifest"), dict)
        else {}
    )
    runtime = (
        execution.get("runtime")
        if isinstance(execution.get("runtime"), dict)
        else {}
    )
    launcher = (
        runtime.get("launcher")
        if isinstance(runtime.get("launcher"), dict)
        else {}
    )
    kernel = (
        runtime.get("kernel")
        if isinstance(runtime.get("kernel"), dict)
        else {}
    )
    tool_name = tool.get("name")
    is_sarah = tool_name == "SARAH"
    supported_tool = is_sarah
    generated_at = _parse_utc_timestamp(payload.get("generated_at_utc"))
    now = datetime.now(timezone.utc)
    exit_code = execution.get("process_exit_code")
    command = execution.get("command")
    command_recorded = bool(
        isinstance(command, list)
        and command
        and all(isinstance(item, str) and item.strip() for item in command)
    )
    probe_command = execution.get("runtime_probe_command")
    probe_command_recorded = bool(
        isinstance(probe_command, list)
        and probe_command
        and all(isinstance(item, str) and item.strip() for item in probe_command)
    )
    command_text = (
        " ".join(command)
        if isinstance(command, list)
        and all(isinstance(item, str) for item in command)
        else ""
    ).lower()
    launcher_path = launcher.get("resolved_path")
    command_matches_tool = bool(
        is_sarah
        and command_recorded
        and _portable_path_key(command[0]) == _portable_path_key(launcher_path)
        and "-file" in command
        and EXTERNAL_DRIVER_REPOSITORY_PATH in command
    )
    source_tree_is_bound_to_command = bool(
        command_recorded
        and "--sarah-root" in command
        and command.index("--sarah-root") + 1 < len(command)
        and _portable_path_key(command[command.index("--sarah-root") + 1])
        == _portable_path_key(source_tree.get("resolved_root"))
    )
    probe_command_matches_contract = bool(
        probe_command_recorded
        and _portable_path_key(probe_command[0])
        == _portable_path_key(launcher_path)
        and probe_command[1:] == ["-code", WOLFRAM_RUNTIME_PROBE_CODE]
    )
    model_path = model.get("path")
    model_format = model.get("format")
    tool_native_model_format = bool(
        is_sarah
        and model_format == SARAH_MODEL_FORMAT
        and isinstance(model_path, str)
        and model_path.lower().endswith(".m")
    )

    normalized_manifest_files: list[dict[str, Any]] = []
    manifest_entries_valid = bool(manifest_files)
    for item in manifest_files:
        if not isinstance(item, dict):
            manifest_entries_valid = False
            continue
        normalized = {
            "path": item.get("path"),
            "sha256": item.get("sha256"),
            "size_bytes": item.get("size_bytes"),
            "role": item.get("role"),
            "format": item.get("format"),
        }
        normalized_manifest_files.append(normalized)
        manifest_entries_valid = bool(
            manifest_entries_valid
            and set(item) == {"path", "sha256", "size_bytes", "role", "format"}
            and _safe_repository_path(normalized["path"])
            and _valid_sha256(normalized["sha256"])
            and type(normalized["size_bytes"]) is int
            and normalized["size_bytes"] >= 0
            and isinstance(normalized["role"], str)
            and bool(normalized["role"].strip())
            and isinstance(normalized["format"], str)
            and bool(normalized["format"].strip())
        )
    manifest_paths = [
        item["path"] for item in normalized_manifest_files if item.get("path")
    ]
    manifest_paths_unique = len(manifest_paths) == len(set(manifest_paths))
    manifest_sha = manifest.get("sha256")
    manifest_hash_matches = bool(
        _valid_sha256(manifest_sha)
        and manifest_sha.lower()
        == _sha256(_canonical_json_bytes(normalized_manifest_files))
    )
    primary_entries = [
        item
        for item in normalized_manifest_files
        if item.get("role") == "primary_model"
    ]
    primary_model_bound = bool(
        len(primary_entries) == 1
        and primary_entries[0].get("path") == MODEL_REPOSITORY_PATH
        and primary_entries[0].get("sha256") == expected_sha256
        and primary_entries[0].get("size_bytes") == expected_bytes
        and primary_entries[0].get("format") == model_format
    )
    driver_entries = [
        item
        for item in normalized_manifest_files
        if item.get("role") == "validation_driver"
    ]
    release_manifest_entries = [
        item
        for item in normalized_manifest_files
        if item.get("role") == "trusted_sarah_release_manifest"
    ]
    validation_driver_bound_to_command = bool(
        len(driver_entries) == 1
        and isinstance(driver_entries[0].get("path"), str)
        and (
            driver_entries[0]["path"].lower() in command_text
            or Path(driver_entries[0]["path"]).name.lower() in command_text
        )
    )
    manifest_has_exact_required_files = bool(
        len(normalized_manifest_files) == 3
        and {item.get("role") for item in normalized_manifest_files}
        == {
            "primary_model",
            "validation_driver",
            "trusted_sarah_release_manifest",
        }
        and {item.get("path") for item in normalized_manifest_files}
        == {
            MODEL_REPOSITORY_PATH,
            EXTERNAL_DRIVER_REPOSITORY_PATH,
            TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH,
        }
    )
    validation_driver_matches_repository_bytes = bool(
        driver_bytes is not None
        and len(driver_entries) == 1
        and driver_entries[0].get("path") == EXTERNAL_DRIVER_REPOSITORY_PATH
        and driver_entries[0].get("sha256") == expected_driver_sha256
        and driver_entries[0].get("size_bytes") == expected_driver_bytes
        and driver_entries[0].get("format") == EXTERNAL_DRIVER_FORMAT
    )
    release_manifest_matches_repository_bytes = bool(
        trusted_release_validation["valid"]
        and len(release_manifest_entries) == 1
        and release_manifest_entries[0].get("path")
        == TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH
        and release_manifest_entries[0].get("sha256")
        == expected_release_manifest_sha256
        and release_manifest_entries[0].get("size_bytes")
        == expected_release_manifest_size
        and release_manifest_entries[0].get("format")
        == TRUSTED_SARAH_RELEASE_MANIFEST_FORMAT
    )

    runtime_probe_log = (
        evidence.get("runtime_probe_log")
        if isinstance(evidence.get("runtime_probe_log"), dict)
        else {}
    )
    log_hash_matches, log_content = _hash_bound_log_record(process_log)
    probe_log_hash_matches, probe_log_content = _hash_bound_log_record(
        runtime_probe_log
    )
    log_markers = {
        name: len(
            re.findall(
                rf"^EXACT_X_CHECK\s+{re.escape(name)}\s+PASS\s*$",
                log_content,
                re.MULTILINE,
            )
        )
        == 1
        for name in REQUIRED_EXTERNAL_CHECKS
    }
    all_required_log_markers_present = all(log_markers.values())
    process_log_has_no_fail_markers = not bool(
        re.search(r"^EXACT_X_CHECK\s+\S+\s+FAIL\s*$", log_content, re.MULTILINE)
    )
    tool_log_version = _single_log_marker(
        r"^EXACT_X_TOOL\s+SARAH\s+(\S+)\s*$", log_content
    )
    process_log_identifies_attested_tool_version = bool(
        tool_log_version is not None
        and tool_log_version == tool.get("version")
    )
    driver_engine_version = _single_log_marker(
        r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$", log_content
    )
    probe_engine_version = _single_log_marker(
        r"^EXACT_X_ENGINE\s+Wolfram\s+(.+?)\s*$", probe_log_content
    )
    driver_kernel_path = _single_log_marker(
        r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$", log_content
    )
    probe_kernel_path = _single_log_marker(
        r"^EXACT_X_KERNEL_PATH\s+(.+?)\s*$", probe_log_content
    )
    wolfram_markers_match_runtime = bool(
        isinstance(runtime.get("wolfram_version"), str)
        and bool(runtime.get("wolfram_version", "").strip())
        and driver_engine_version == runtime.get("wolfram_version")
        and probe_engine_version == runtime.get("wolfram_version")
        and _portable_path_key(driver_kernel_path)
        == _portable_path_key(kernel.get("resolved_path"))
        and _portable_path_key(probe_kernel_path)
        == _portable_path_key(kernel.get("resolved_path"))
    )

    def executable_fingerprint_valid(value: dict[str, Any]) -> bool:
        return bool(
            _safe_absolute_execution_path(value.get("resolved_path"))
            and _valid_sha256(value.get("sha256_before"))
            and _valid_sha256(value.get("sha256_after"))
            and value.get("sha256_before") == value.get("sha256_after")
            and type(value.get("size_bytes_before")) is int
            and value.get("size_bytes_before") > 0
            and type(value.get("size_bytes_after")) is int
            and value.get("size_bytes_before") == value.get("size_bytes_after")
            and value.get("unchanged_during_execution") is True
        )

    release_tree = trusted_release_validation["tree"]
    source_tree_is_exactly_trusted = bool(
        source_tree.get("schema") == SARAH_SOURCE_TREE_SNAPSHOT_SCHEMA
        and _safe_absolute_execution_path(source_tree.get("resolved_root"))
        and source_tree.get("sha256") == release_tree.get("sha256")
        and source_tree.get("file_count") == release_tree.get("file_count")
        and source_tree.get("size_bytes") == release_tree.get("size_bytes")
        and source_tree.get("verified_against_trusted_release_manifest") is True
        and source_tree.get("unchanged_during_execution") is True
    )
    release_binding_matches_repository = bool(
        release_binding.get("path")
        == TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH
        and release_binding.get("sha256") == expected_release_manifest_sha256
        and release_binding.get("size_bytes") == expected_release_manifest_size
    )
    unsafe_gauge_check_disable_absent = (
        "--no-checkgaugeinvariance" not in command_text
    )
    validation_checks = {
        "artifact_is_structured_json_object": isinstance(artifact, dict),
        "schema_is_supported": payload.get("schema")
        == EXTERNAL_VALIDATION_SCHEMA,
        "legacy_v2_schema_is_not_promoted": payload.get("schema")
        != LEGACY_EXTERNAL_VALIDATION_SCHEMA,
        "model_path_is_exact_repository_model": model.get("path")
        == MODEL_REPOSITORY_PATH,
        "model_sha256_matches_exact_bytes": model.get("sha256")
        == expected_sha256,
        "model_size_matches_exact_bytes": type(model.get("size_bytes")) is int
        and model.get("size_bytes") == expected_bytes,
        "tool_native_model_format_matches_path": tool_native_model_format,
        "supported_external_tool_identified": supported_tool,
        "external_tool_version_recorded": tool.get("version")
        == TRUSTED_SARAH_RELEASE["version"],
        "trusted_sarah_release_manifest_is_canonical": (
            trusted_release_validation["valid"]
        ),
        "trusted_sarah_release_manifest_is_input_bound": (
            release_manifest_matches_repository_bytes
        ),
        "tool_release_binding_matches_repository_manifest": (
            release_binding_matches_repository
        ),
        "sarah_source_tree_is_exactly_trusted": source_tree_is_exactly_trusted,
        "sarah_source_tree_was_unchanged_during_execution": source_tree.get(
            "unchanged_during_execution"
        )
        is True,
        "external_process_was_executed": execution.get("external_process_executed")
        is True,
        "external_process_command_recorded": command_recorded,
        "external_process_command_matches_tool": command_matches_tool,
        "sarah_source_tree_is_bound_to_command": source_tree_is_bound_to_command,
        "runtime_probe_command_recorded": probe_command_recorded,
        "runtime_probe_command_matches_contract": probe_command_matches_contract,
        "runtime_probe_exit_code_zero": type(
            execution.get("runtime_probe_exit_code")
        )
        is int
        and execution.get("runtime_probe_exit_code") == 0,
        "gauge_invariance_check_was_not_disabled": unsafe_gauge_check_disable_absent,
        "external_process_exit_code_zero": type(exit_code) is int
        and exit_code == 0,
        "input_manifest_schema_is_supported": manifest.get("schema")
        == EXTERNAL_INPUT_MANIFEST_SCHEMA,
        "input_manifest_entries_are_structured": manifest_entries_valid,
        "input_manifest_paths_are_unique": manifest_paths_unique,
        "input_manifest_has_exact_required_files": (
            manifest_has_exact_required_files
        ),
        "input_manifest_sha256_matches_entries": manifest_hash_matches,
        "primary_model_is_bound_in_input_manifest": primary_model_bound,
        "validation_driver_matches_repository_bytes": (
            validation_driver_matches_repository_bytes
        ),
        "validation_driver_is_bound_to_command": validation_driver_bound_to_command,
        "trusted_release_manifest_matches_repository_bytes": (
            release_manifest_matches_repository_bytes
        ),
        "resolved_wolfram_launcher_is_hash_bound_and_unchanged": (
            executable_fingerprint_valid(launcher)
        ),
        "resolved_wolfram_kernel_is_hash_bound_and_unchanged": (
            executable_fingerprint_valid(kernel)
        ),
        "runtime_probe_log_is_hash_bound": probe_log_hash_matches,
        "captured_process_log_is_hash_bound": log_hash_matches,
        "probe_and_driver_wolfram_markers_match_runtime": (
            wolfram_markers_match_runtime
        ),
        "process_log_identifies_attested_tool_version": (
            process_log_identifies_attested_tool_version
        ),
        "captured_process_log_has_all_required_pass_markers": (
            all_required_log_markers_present
        ),
        "captured_process_log_has_no_fail_markers": (
            process_log_has_no_fail_markers
        ),
        "generated_at_is_timezone_aware": generated_at is not None,
        "generated_at_is_not_in_future": generated_at is not None
        and generated_at <= now + timedelta(minutes=5),
        **{
            name: checks_payload.get(name) is True
            for name in REQUIRED_EXTERNAL_CHECKS
        },
    }
    failures = [name for name, passed in validation_checks.items() if not passed]
    valid = not failures
    return {
        "source": str(EXTERNAL_VALIDATION.relative_to(ROOT)).replace("\\", "/"),
        "present": isinstance(artifact, dict),
        "schema": payload.get("schema"),
        "tool_name": tool_name,
        "tool_version": tool.get("version"),
        "attested_model_format": model_format,
        "generated_at_utc": payload.get("generated_at_utc"),
        "expected_model_path": MODEL_REPOSITORY_PATH,
        "attested_model_path": model.get("path"),
        "expected_model_sha256": expected_sha256,
        "attested_model_sha256": model.get("sha256"),
        "expected_model_size_bytes": expected_bytes,
        "attested_model_size_bytes": model.get("size_bytes"),
        "expected_validation_driver_path": EXTERNAL_DRIVER_REPOSITORY_PATH,
        "expected_validation_driver_sha256": expected_driver_sha256,
        "expected_validation_driver_size_bytes": expected_driver_bytes,
        "expected_trusted_sarah_release_manifest_path": (
            TRUSTED_SARAH_RELEASE_MANIFEST_REPOSITORY_PATH
        ),
        "expected_trusted_sarah_release_manifest_sha256": (
            expected_release_manifest_sha256
        ),
        "expected_trusted_sarah_release_manifest_size_bytes": (
            expected_release_manifest_size
        ),
        "fresh_for_exact_model_bytes": bool(
            validation_checks["model_sha256_matches_exact_bytes"]
            and validation_checks["model_size_matches_exact_bytes"]
        ),
        "required_external_checks": list(REQUIRED_EXTERNAL_CHECKS),
        "input_manifest": {
            "schema": manifest.get("schema"),
            "sha256": manifest_sha,
            "files": normalized_manifest_files,
        },
        "process_log": {
            "sha256": process_log.get("sha256"),
            "size_bytes": process_log.get("size_bytes"),
            "encoding": process_log.get("encoding"),
            "attested_tool_marker": None
            if tool_log_version is None
            else f"EXACT_X_TOOL SARAH {tool_log_version}",
            "required_marker_presence": log_markers,
        },
        "runtime_probe_log": {
            "sha256": runtime_probe_log.get("sha256"),
            "size_bytes": runtime_probe_log.get("size_bytes"),
            "encoding": runtime_probe_log.get("encoding"),
            "wolfram_version_marker": probe_engine_version,
            "kernel_path_marker": probe_kernel_path,
        },
        "trusted_sarah_release_manifest": trusted_release_validation,
        "sarah_source_tree": source_tree,
        "wolfram_runtime": runtime,
        "checks": validation_checks,
        "failures": failures,
        "valid": valid,
        "note": (
            "Freshness is content-addressed: v3 binds the exact tool-native "
            "model and driver, the official canonical SARAH 4.15.3 source "
            "tree, resolved Wolfram launcher/kernel bytes before and after the "
            "run, and hash-bound runtime-probe and validation logs. Legacy v2, "
            "reduced-sector LIVE dumps, and unbound booleans are not accepted."
        ),
    }


def _strip_mathematica_comments(text: str) -> str:
    """Remove nested ``(* ... *)`` comments without touching strings."""
    output: list[str] = []
    depth = 0
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        pair = text[index : index + 2]
        char = text[index]
        if depth:
            if pair == "(*":
                depth += 1
                index += 2
                continue
            if pair == "*)":
                depth -= 1
                index += 2
                continue
            if char == "\n":
                output.append("\n")
            index += 1
            continue
        if not in_string and pair == "(*":
            depth = 1
            index += 2
            continue
        output.append(char)
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        index += 1
    return "".join(output)


def _mask_mathematica_strings(text: str) -> str:
    """Blank string literals while preserving offsets for assignment parsing."""
    output = list(text)
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            output[index] = "\n" if char == "\n" else " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            output[index] = " "
    return "".join(output)


def _split_top_level(expression: str) -> list[str]:
    """Split a Mathematica list or expression on top-level commas."""
    value = expression.strip()
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1]
    items: list[str] = []
    start = 0
    stack: list[str] = []
    in_string = False
    escaped = False
    closing = {"{": "}", "[": "]", "(": ")"}
    for index, char in enumerate(value):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in closing:
            stack.append(closing[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif char == "," and not stack:
            items.append(value[start:index].strip())
            start = index + 1
    tail = value[start:].strip()
    if tail:
        items.append(tail)
    return items


def _indexed_assignments(code: str, head: str) -> tuple[list[dict[str, Any]], int]:
    """Parse ``Head[[n]] = rhs;`` assignments from comment-free code."""
    pattern = re.compile(rf"\b{re.escape(head)}\s*\[\[\s*(\d+)\s*\]\]\s*=")
    matches = list(pattern.finditer(_mask_mathematica_strings(code)))
    rows: list[dict[str, Any]] = []
    for match in matches:
        start = match.end()
        stack: list[str] = []
        in_string = False
        escaped = False
        closing = {"{": "}", "[": "]", "(": ")"}
        end = None
        for index in range(start, len(code)):
            char = code[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char in closing:
                stack.append(closing[char])
            elif stack and char == stack[-1]:
                stack.pop()
            elif char == ";" and not stack:
                end = index
                break
        if end is None:
            continue
        rhs = code[start:end].strip()
        rows.append(
            {
                "index": int(match.group(1)),
                "rhs": rhs,
                "items": _split_top_level(rhs) if rhs.startswith("{") else [],
            }
        )
    return rows, len(matches)


def _named_assignment_rhs(code: str, name: str) -> list[str]:
    """Return uncommented, semicolon-terminated RHS expressions."""
    pattern = re.compile(rf"\b{re.escape(name)}\s*=")
    values: list[str] = []
    for match in pattern.finditer(_mask_mathematica_strings(code)):
        value = _rhs_until_top_level_semicolon(code, match.end())
        if value is not None:
            values.append(value)
    return values


def _rhs_until_top_level_semicolon(code: str, start: int) -> str | None:
    stack: list[str] = []
    in_string = False
    escaped = False
    closing = {"{": "}", "[": "]", "(": ")"}
    for index in range(start, len(code)):
        char = code[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in closing:
            stack.append(closing[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif char == ";" and not stack:
            return code[start:index].strip()
    return None


def _definition_assignment_rhs(
    code: str, state: str, name: str
) -> tuple[list[str], int]:
    pattern = re.compile(
        rf"\bDEFINITION\s*\[\s*{re.escape(state)}\s*\]\s*"
        rf"\[\s*{re.escape(name)}\s*\]\s*="
    )
    matches = list(pattern.finditer(_mask_mathematica_strings(code)))
    values = [
        value
        for match in matches
        if (value := _rhs_until_top_level_semicolon(code, match.end())) is not None
    ]
    return values, len(matches)


def _symbol(value: str) -> str:
    return re.sub(r"\s+", "", value).strip('"')


def _integer_pair(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(
        r"\{\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*\}", value.strip()
    )
    return None if match is None else (int(match.group(1)), int(match.group(2)))


def _integer(value: str) -> int | None:
    match = re.fullmatch(r"[+]?(-?\d+)", _symbol(value))
    return None if match is None else int(match.group(1))


def _cyclic_phase_charge(value: str, order: int) -> int | None:
    """Decode SARAH's exact multiplicative ``Z[order]`` charge syntax."""
    compact = re.sub(r"\s+", "", value)
    if compact == "1":
        return 0
    match = re.fullmatch(
        rf"Exp\[2\*Pi\*I\*([+-]?\d+)/{order}\]",
        compact,
    )
    return None if match is None else int(match.group(1)) % order


def _representation(value: str) -> str | None:
    compact = _symbol(value).lower()
    dynkin_aliases = {
        "{0,0,0,0,0}": "1",
        "{1,0,0,0,0}": "10",
        "{0,0,0,0,1}": "16",
        "{0,0,0,1,0}": "-16",
        "{0,0,0,0,2}": "126",
        "{0,0,0,2,0}": "126",
        "{0,0,0,1,1}": "210",
    }
    if compact in dynkin_aliases:
        return dynkin_aliases[compact]
    items = _split_top_level(value)
    if len(items) != 1:
        return None
    token = _symbol(items[0]).lower()
    aliases = {
        "16": "16",
        "+16": "16",
        "-16": "-16",
        "bar16": "-16",
        "16bar": "-16",
        "conj[16]": "-16",
        "1": "1",
        "10": "10",
        "126": "126",
        "-126": "126",
        "210": "210",
    }
    return aliases.get(token)


def _substantive_lagrangian(values: list[str]) -> bool:
    rejected = {"", "0", "0.", "null", "none", "{}"}
    return any(
        re.sub(r"\s+", "", value).lower() not in rejected
        and not re.search(r"placeholder|todo|fixme", value, re.I)
        for value in values
    )


def manuscript_contract(manuscript_text: str) -> dict[str, Any]:
    """Extract the authoritative U(1)_X statements from the TeX source."""
    compact = re.sub(r"\s+", "", manuscript_text)
    gauges_primitive_u1x = bool(
        re.search(
            r"gauge\s+a\s+primitive\s+\$U\(1\)_X\$",
            manuscript_text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    phi_match = re.search(r"\(X,\{\\rmPQ\}\)=\(([+-]?\d+),([+-]?\d+)\)", compact)
    tuple_match = re.search(
        r"X\(F,s,b,S,10_H,\\overline\{126\}_H,210_H\)="
        r"\(([-+0-9,]+)\)",
        compact,
    )
    tuple_labels = ("F", "s", "b", "S", "H10", "Delta126bar", "Phi210")
    tuple_values: tuple[int, ...] | None = None
    if tuple_match is not None:
        candidate = tuple(int(item) for item in tuple_match.group(1).split(","))
        if len(candidate) == len(tuple_labels):
            tuple_values = candidate

    pq_patterns = {
        "H10": r"\$10_H\$\(\$([+-]?\d+)\$\)",
        "Delta126bar": r"\$\\overline\{126\}_H\$\(\$([+-]?\d+)\$\)",
        "Phi210": r"\$210_H\$\(([+-]?\d+)\)",
        "S": r"\$S\$\(\$([+-]?\d+)\$\)",
    }
    pq_scalars: dict[str, int] = {}
    for field, pattern in pq_patterns.items():
        match = re.search(pattern, compact)
        if match is not None:
            pq_scalars[field] = int(match.group(1))

    scalar_contract: dict[str, list[int]] = {}
    if tuple_values is not None:
        x_charges = dict(zip(tuple_labels, tuple_values, strict=True))
        for field in ("Phi210", "Delta126bar", "H10", "S"):
            if field in pq_scalars:
                scalar_contract[field] = [pq_scalars[field], x_charges[field]]
    if phi_match is not None:
        scalar_contract["Phi17"] = [int(phi_match.group(2)), int(phi_match.group(1))]

    exact_u1x_catalogue_declared = bool(
        re.search(
            r"exact\s+\$U\(1\)_X\$",
            manuscript_text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    return {
        "source": MANUSCRIPT.name,
        "authoritative_for_scientific_contract": True,
        "gauges_primitive_U1X": gauges_primitive_u1x,
        "phi17_X": None if phi_match is None else int(phi_match.group(1)),
        "phi17_PQ": None if phi_match is None else int(phi_match.group(2)),
        "x_charge_tuple_labels": list(tuple_labels),
        "x_charge_tuple_values": None if tuple_values is None else list(tuple_values),
        "pq_scalar_charges": pq_scalars,
        "scalar_final_charge_contract": scalar_contract,
        "charge_tuple_parsed": tuple_values is not None,
        "scalar_charge_contract_matches_expected": scalar_contract
        == {field: list(charges) for field, charges in EXPECTED_SCALAR_CHARGES.items()},
        "declares_exact_U1X_renormalizable_catalogue": (
            exact_u1x_catalogue_declared
        ),
    }


def declared_symmetries(model_text: str) -> dict[str, Any]:
    """Classify and parse either native SARAH syntax or the legacy scaffold.

    The repository historically used a pseudo-SARAH ledger in which the
    representation and a ``{PQ, X}`` metadata pair occupied positions that
    have different meanings in SARAH.  That layout remains readable for
    diagnostics, but can never satisfy ``tool_native_sarah_syntax`` or static
    executability.  Native rows follow SARAH's order
    ``{field, generations, component, gauge reps/charges..., globals...}``.
    """
    code = _strip_mathematica_comments(model_text)
    gauge_assignments, gauge_assignment_count = _indexed_assignments(code, "Gauge")
    global_assignments, global_assignment_count = _indexed_assignments(code, "Global")
    scalar_assignments, scalar_assignment_count = _indexed_assignments(
        code, "ScalarFields"
    )
    fermion_assignments, fermion_assignment_count = _indexed_assignments(
        code, "FermionFields"
    )

    gauge_rows: list[dict[str, Any]] = []
    for assignment in gauge_assignments:
        items = assignment["items"]
        group_symbol = _symbol(items[0]) if len(items) >= 1 else None
        group_type = _symbol(items[1]) if len(items) >= 2 else None
        group_name = _symbol(items[2]) if len(items) >= 3 else None
        normalized_type = (group_type or "").lower()
        is_u1 = normalized_type == "u[1]"
        is_native_so10 = normalized_type == "so[10]"
        is_legacy_so10 = group_type == "SO" and group_name == "10"
        # SARAH 4.15.3 internally takes the first three characters of the
        # descriptive U(1) name.  A one-character ``X`` therefore aborts a
        # genuine model initialization even though it is unambiguous to this
        # parser.  Accept the tool-native long spelling used by the attested
        # model, while binding it to the dedicated ``GX`` gauge symbol.
        is_named_x = (
            (group_symbol or "").lower() == "gx"
            and (group_name or "").lower() in {"x", "xcharge", "u1x"}
        )
        native_row = bool(
            len(items) >= 5 and (is_native_so10 or is_u1)
        )
        gauge_rows.append(
            {
                "index": assignment["index"],
                "raw_rhs": assignment["rhs"],
                "group_symbol": group_symbol,
                "group_type": group_type,
                "group_name": group_name,
                "is_so10": is_native_so10 or is_legacy_so10,
                "is_native_so10": is_native_so10,
                "is_legacy_so10": is_legacy_so10,
                "is_u1": is_u1,
                "is_named_X": is_named_x,
                "is_u1x": is_u1 and is_named_x,
                "syntax": "sarah_native" if native_row else "legacy_or_invalid",
                "structurally_valid": len(items) >= 3,
                "tool_native_structurally_valid": native_row,
            }
        )

    legacy_global_values = _named_assignment_rhs(code, "GlobalSymmetry")
    legacy_global_rows = (
        _split_top_level(legacy_global_values[-1]) if legacy_global_values else []
    )
    native_global_rows: list[dict[str, Any]] = []
    for assignment in global_assignments:
        items = assignment["items"]
        kind = _symbol(items[0]) if items else None
        name = _symbol(items[1]) if len(items) >= 2 else None
        native_global_rows.append(
            {
                "index": assignment["index"],
                "raw_rhs": assignment["rhs"],
                "kind": kind,
                "name": name,
                "is_z17": bool(kind and re.fullmatch(r"Z\[17\]", kind, re.I)),
                "structurally_valid": len(items) >= 2,
            }
        )
    native_global_exact = bool(
        len(native_global_rows) == 1
        and native_global_rows[0]["is_z17"]
        and native_global_rows[0]["structurally_valid"]
        and not legacy_global_values
    )
    legacy_global_exact = bool(
        len(legacy_global_values) == 1
        and len(legacy_global_rows) == 1
        and re.fullmatch(r"Z\[17\]", _symbol(legacy_global_rows[0]), re.I)
        and not native_global_rows
    )
    global_rows = (
        [row["kind"] for row in native_global_rows]
        if native_global_rows
        else legacy_global_rows
    )

    tool_native_gauge_syntax = bool(
        gauge_rows
        and all(row["tool_native_structurally_valid"] for row in gauge_rows)
        and not any(row["is_legacy_so10"] for row in gauge_rows)
    )
    prefer_native_fields = tool_native_gauge_syntax and bool(native_global_rows)
    so10_positions = [i for i, row in enumerate(gauge_rows) if row["is_so10"]]
    u1x_positions = [i for i, row in enumerate(gauge_rows) if row["is_u1x"]]
    z17_positions = [i for i, row in enumerate(native_global_rows) if row["is_z17"]]
    expected_native_row_length = 3 + len(gauge_rows) + len(native_global_rows)

    scalar_aliases = {
        "phi210": "Phi210",
        "delta": "Delta126bar",
        "delta126": "Delta126bar",
        "delta126bar": "Delta126bar",
        "h": "H10",
        "h10": "H10",
        "s": "S",
        "phi17": "Phi17",
    }
    scalar_rows: list[dict[str, Any]] = []
    observed_scalar_charges: dict[str, list[int]] = {}
    observed_scalar_representations: dict[str, str] = {}
    duplicate_scalar_fields: list[str] = []
    scalar_field_counts: dict[str, int] = {}
    unrecognized_scalar_fields: list[str] = []
    for assignment in scalar_assignments:
        items = assignment["items"]
        field_token = _symbol(items[0]) if items else ""
        canonical = scalar_aliases.get(field_token.lower())
        multiplicity: int | None = None
        x_charge: int | None = None
        z17_charge: int | None = None
        representation: str | None = None
        charges: tuple[int, int] | None = None
        syntax = "legacy_pseudo_sarah"
        if prefer_native_fields:
            syntax = "sarah_native"
            multiplicity = _integer(items[1]) if len(items) >= 2 else None
            if len(so10_positions) == 1 and len(items) > 3 + so10_positions[0]:
                representation = _representation(items[3 + so10_positions[0]])
            if len(u1x_positions) == 1 and len(items) > 3 + u1x_positions[0]:
                x_charge = _integer(items[3 + u1x_positions[0]])
            if (
                len(z17_positions) == 1
                and len(items) > 3 + len(gauge_rows) + z17_positions[0]
            ):
                z17_charge = _cyclic_phase_charge(
                    items[3 + len(gauge_rows) + z17_positions[0]], 17
                )
            if canonical is not None and x_charge is not None:
                charges = (EXPECTED_SCALAR_CHARGES[canonical][0], x_charge)
        else:
            representation = _representation(items[1]) if len(items) >= 2 else None
            charges = _integer_pair(items[-1]) if items else None
            multiplicity = 1
            x_charge = None if charges is None else charges[1]
        residual_matches = bool(
            syntax != "sarah_native"
            or x_charge is not None
            and z17_charge is not None
            and z17_charge % 17 == x_charge % 17
        )
        if canonical:
            scalar_field_counts[canonical] = scalar_field_counts.get(canonical, 0) + 1
            if scalar_field_counts[canonical] > 1:
                duplicate_scalar_fields.append(canonical)
        else:
            unrecognized_scalar_fields.append(field_token or "<missing>")
        if canonical and charges is not None:
            observed_scalar_charges[canonical] = list(charges)
        if canonical and representation is not None:
            observed_scalar_representations[canonical] = representation
        structurally_valid = bool(
            canonical
            and representation is not None
            and charges is not None
            and multiplicity == 1
            and (
                syntax != "sarah_native"
                or len(items) == expected_native_row_length
                and residual_matches
            )
            and (syntax == "sarah_native" or len(items) >= 4)
        )
        scalar_rows.append(
            {
                "index": assignment["index"],
                "field": field_token,
                "canonical_field": canonical,
                "representation": representation,
                "raw_representation": items[3 + so10_positions[0]]
                if syntax == "sarah_native"
                and len(so10_positions) == 1
                and len(items) > 3 + so10_positions[0]
                else items[1]
                if len(items) >= 2
                else None,
                "multiplicity": multiplicity,
                "component": _symbol(items[2])
                if syntax == "sarah_native" and len(items) >= 3
                else None,
                "syntax": syntax,
                "X_charge": x_charge,
                "Z17_charge": z17_charge,
                "residual_Z17_matches_X_mod_17": residual_matches,
                "PQ_charge_source": "authoritative_accidental_PQ_contract"
                if syntax == "sarah_native"
                else "legacy_embedded_pair",
                "final_charge_pair_order": ["PQ", "X"],
                "final_charge_pair": None if charges is None else list(charges),
                "structurally_valid": structurally_valid,
            }
        )

    expected_pq_by_rep_x = {
        (representation, charges[1]): charges[0]
        for representation, charges, _multiplicity, _roles in EXPECTED_FERMION_SECTORS
    }
    fermion_rows: list[dict[str, Any]] = []
    observed_fermions: dict[tuple[str, tuple[int, int]], int] = {}
    fermion_field_counts: dict[str, int] = {}
    duplicate_fermion_fields: list[str] = []
    for assignment in fermion_assignments:
        items = assignment["items"]
        field_token = _symbol(items[0]) if items else ""
        if field_token:
            fermion_field_counts[field_token] = fermion_field_counts.get(field_token, 0) + 1
            if fermion_field_counts[field_token] > 1:
                duplicate_fermion_fields.append(field_token)
        representation: str | None = None
        multiplicity: int | None = None
        x_charge: int | None = None
        z17_charge: int | None = None
        charges: tuple[int, int] | None = None
        syntax = "legacy_pseudo_sarah"
        if prefer_native_fields:
            syntax = "sarah_native"
            multiplicity = _integer(items[1]) if len(items) >= 2 else None
            if len(so10_positions) == 1 and len(items) > 3 + so10_positions[0]:
                representation = _representation(items[3 + so10_positions[0]])
            if len(u1x_positions) == 1 and len(items) > 3 + u1x_positions[0]:
                x_charge = _integer(items[3 + u1x_positions[0]])
            if (
                len(z17_positions) == 1
                and len(items) > 3 + len(gauge_rows) + z17_positions[0]
            ):
                z17_charge = _cyclic_phase_charge(
                    items[3 + len(gauge_rows) + z17_positions[0]], 17
                )
            if representation is not None and x_charge is not None:
                pq_charge = expected_pq_by_rep_x.get((representation, x_charge))
                if pq_charge is not None:
                    charges = (pq_charge, x_charge)
        else:
            representation = _representation(items[1]) if len(items) >= 2 else None
            multiplicity = _integer(items[2]) if len(items) >= 3 else None
            charges = _integer_pair(items[-1]) if items else None
            x_charge = None if charges is None else charges[1]
        residual_matches = bool(
            syntax != "sarah_native"
            or x_charge is not None
            and z17_charge is not None
            and z17_charge % 17 == x_charge % 17
        )
        structurally_valid = bool(
            field_token
            and representation is not None
            and multiplicity is not None
            and multiplicity > 0
            and charges is not None
            and (
                syntax != "sarah_native"
                or len(items) == expected_native_row_length
                and residual_matches
            )
            and (syntax == "sarah_native" or len(items) >= 4)
        )
        if structurally_valid:
            sector = (representation, charges)
            observed_fermions[sector] = observed_fermions.get(sector, 0) + multiplicity
        fermion_rows.append(
            {
                "index": assignment["index"],
                "field": field_token or None,
                "representation": representation,
                "raw_representation": items[3 + so10_positions[0]]
                if syntax == "sarah_native"
                and len(so10_positions) == 1
                and len(items) > 3 + so10_positions[0]
                else items[1]
                if len(items) >= 2
                else None,
                "multiplicity": multiplicity,
                "component": _symbol(items[2])
                if syntax == "sarah_native" and len(items) >= 3
                else None,
                "syntax": syntax,
                "X_charge": x_charge,
                "Z17_charge": z17_charge,
                "residual_Z17_matches_X_mod_17": residual_matches,
                "PQ_charge_source": "authoritative_accidental_PQ_contract"
                if syntax == "sarah_native"
                else "legacy_embedded_pair",
                "final_charge_pair_order": ["PQ", "X"],
                "final_charge_pair": None if charges is None else list(charges),
                "structurally_valid": structurally_valid,
            }
        )

    fermion_requirements: list[dict[str, Any]] = []
    expected_fermion_keys: set[tuple[str, tuple[int, int]]] = set()
    for representation, charges, required, roles in EXPECTED_FERMION_SECTORS:
        key = (representation, charges)
        expected_fermion_keys.add(key)
        observed = observed_fermions.get(key, 0)
        fermion_requirements.append(
            {
                "representation": representation,
                "charges_PQ_X": list(charges),
                "required_multiplicity": required,
                "observed_multiplicity": observed,
                "roles": roles,
                "satisfied": observed == required,
            }
        )

    lag_hc_values = _named_assignment_rhs(code, "LagHC")
    lag_no_hc_values = _named_assignment_rhs(code, "LagNoHC")
    lag_input_values, lag_input_assignment_count = _definition_assignment_rhs(
        code, "GaugeES", "LagrangianInput"
    )
    lag_input_entries: list[dict[str, Any]] = []
    for value in lag_input_values:
        for raw_entry in _split_top_level(value):
            items = _split_top_level(raw_entry)
            name = _symbol(items[0]) if items else None
            add_hc_match = re.search(
                r"\bAddHC\s*->\s*(True|False)\b", raw_entry, re.I
            )
            lag_input_entries.append(
                {
                    "name": name,
                    "AddHC": None
                    if add_hc_match is None
                    else add_hc_match.group(1).lower() == "true",
                    "raw": raw_entry,
                }
            )
    lag_hc_registration = [
        row for row in lag_input_entries if row["name"] == "LagHC" and row["AddHC"] is True
    ]
    lag_no_hc_registration = [
        row
        for row in lag_input_entries
        if row["name"] == "LagNoHC" and row["AddHC"] is False
    ]
    lagrangian_input_registered = bool(
        lag_input_assignment_count == 1
        and len(lag_input_values) == 1
        and len(lag_input_entries) == 2
        and len(lag_hc_registration) == 1
        and len(lag_no_hc_registration) == 1
    )

    placeholder_patterns = {
        "self_described_scaffold": r"\bscaffold\b",
        "no_live_execution_claim": r"does\s+not\s+claim\s+a\s+live",
        "external_clebsch_placeholder": r"detailed\s+cg\s+external",
        "must_expand_clebsch": r"must\s+expand\s+cg",
        "placeholder_token": r"\bplaceholder\b|\btodo\b|\bfixme\b",
    }
    placeholder_evidence = [
        label
        for label, pattern in placeholder_patterns.items()
        if re.search(pattern, model_text, re.I)
    ]
    gauge_indices = [row["index"] for row in gauge_assignments]
    global_indices = [row["index"] for row in global_assignments]
    scalar_indices = [row["index"] for row in scalar_assignments]
    fermion_indices = [row["index"] for row in fermion_assignments]
    assignment_indices_unique = all(
        len(indices) == len(set(indices))
        for indices in (gauge_indices, global_indices, scalar_indices, fermion_indices)
    )
    assignment_parse_complete = bool(
        len(gauge_assignments) == gauge_assignment_count
        and len(global_assignments) == global_assignment_count
        and len(scalar_assignments) == scalar_assignment_count
        and len(fermion_assignments) == fermion_assignment_count
        and len(lag_input_values) == lag_input_assignment_count
    )

    scalar_charges_match = observed_scalar_charges == {
        field: list(charges) for field, charges in EXPECTED_SCALAR_CHARGES.items()
    }
    scalar_representations_match = (
        observed_scalar_representations == EXPECTED_SCALAR_REPRESENTATIONS
    )
    scalar_residuals_match = bool(
        scalar_rows
        and all(row["residual_Z17_matches_X_mod_17"] for row in scalar_rows)
    )
    fermion_residuals_match = bool(
        fermion_rows
        and all(row["residual_Z17_matches_X_mod_17"] for row in fermion_rows)
    )
    fermion_catalogue_sufficient = all(
        row["satisfied"] for row in fermion_requirements
    )
    unexpected_fermion_sectors = sorted(
        (
            {
                "representation": representation,
                "charges_PQ_X": list(charges),
                "observed_multiplicity": multiplicity,
            }
            for (representation, charges), multiplicity in observed_fermions.items()
            if (representation, charges) not in expected_fermion_keys
        ),
        key=lambda row: (row["representation"], row["charges_PQ_X"]),
    )
    u1x_rows = [row for row in gauge_rows if row["is_u1x"]]
    gauge_catalogue_exact = bool(
        len(gauge_rows) == 2
        and sum(row["is_so10"] for row in gauge_rows) == 1
        and len(u1x_rows) == 1
        and all(row["is_so10"] or row["is_u1x"] for row in gauge_rows)
        and all(row["structurally_valid"] for row in gauge_rows)
    )
    global_symmetry_catalogue_exact = native_global_exact or legacy_global_exact
    scalar_catalogue_exact = bool(
        len(scalar_rows) == len(EXPECTED_SCALAR_CHARGES)
        and not unrecognized_scalar_fields
        and not duplicate_scalar_fields
        and all(row["structurally_valid"] for row in scalar_rows)
        and scalar_charges_match
        and scalar_representations_match
        and scalar_residuals_match
    )
    fermion_catalogue_exact = bool(
        fermion_catalogue_sufficient
        and set(observed_fermions) == expected_fermion_keys
        and not unexpected_fermion_sectors
        and not duplicate_fermion_fields
        and all(row["structurally_valid"] for row in fermion_rows)
        and fermion_residuals_match
    )
    has_lag_hc = _substantive_lagrangian(lag_hc_values)
    has_lag_no_hc = _substantive_lagrangian(lag_no_hc_values)
    soft_gaugino_absent = not bool(
        re.search(r"\bSoftGauginoMass\s*\[", _mask_mathematica_strings(code))
    )
    named_assignment_counts_exact = bool(
        len(lag_hc_values) == 1 and len(lag_no_hc_values) == 1
    )
    native_field_syntax = bool(
        scalar_rows
        and fermion_rows
        and all(row["syntax"] == "sarah_native" for row in scalar_rows + fermion_rows)
    )
    tool_native_sarah_syntax = bool(
        tool_native_gauge_syntax
        and native_global_exact
        and native_field_syntax
        and lagrangian_input_registered
    )
    legacy_markers = bool(
        legacy_global_values
        or any(row["is_legacy_so10"] for row in gauge_rows)
        or any(
            row["syntax"] == "legacy_pseudo_sarah"
            for row in scalar_rows + fermion_rows
        )
    )
    model_syntax_class = (
        "sarah_native"
        if tool_native_sarah_syntax
        else "legacy_pseudo_sarah_metadata"
        if legacy_markers
        else "mixed_or_unrecognized"
    )
    semantic_requirements = {
        "tool_native_sarah_syntax": tool_native_sarah_syntax,
        "exact_gauge_catalogue": gauge_catalogue_exact,
        "exact_global_symmetry_catalogue": global_symmetry_catalogue_exact,
        "exact_scalar_catalogue": scalar_catalogue_exact,
        "scalar_charges_match_manuscript": scalar_charges_match,
        "scalar_representations_match": scalar_representations_match,
        "fermion_catalogue_exact": fermion_catalogue_exact,
        "real_LagHC_present": has_lag_hc,
        "real_LagNoHC_present": has_lag_no_hc,
        "exactly_one_LagHC_and_LagNoHC_assignment": named_assignment_counts_exact,
        "lagrangian_registered_in_GaugeES_LagrangianInput": (
            lagrangian_input_registered
        ),
        "soft_gaugino_absent_in_nonsusy_model": soft_gaugino_absent,
        "placeholder_free": not placeholder_evidence,
        "assignment_indices_unique": assignment_indices_unique,
        "assignment_parse_complete": assignment_parse_complete,
    }
    static_inventory_matches = all(
        value
        for name, value in semantic_requirements.items()
        if name
        not in {
            "tool_native_sarah_syntax",
            "lagrangian_registered_in_GaugeES_LagrangianInput",
        }
    )
    statically_executable = all(semantic_requirements.values())
    z17_declared = bool(native_global_exact or legacy_global_exact)
    return {
        "source": str(MODEL.relative_to(ROOT)),
        "authoritative_for_scientific_contract": False,
        "model_syntax_class": model_syntax_class,
        "tool_native_sarah_syntax": tool_native_sarah_syntax,
        "legacy_pseudo_sarah_grammar": legacy_markers,
        "static_inventory_matches_contract": static_inventory_matches,
        "explicitly_incomplete_scaffold": bool(
            placeholder_evidence or model_syntax_class != "sarah_native"
        ),
        "placeholder_evidence": placeholder_evidence,
        "gauge_rows": [row["raw_rhs"] for row in gauge_rows],
        "structured_gauge_rows": gauge_rows,
        "global_rows": global_rows,
        "structured_global_rows": native_global_rows,
        "legacy_GlobalSymmetry_assignments": legacy_global_values,
        "so10_gauged": any(row["is_so10"] for row in gauge_rows),
        "u1x_gauged": len(u1x_rows) == 1,
        "u1x_gauge_row_count": len(u1x_rows),
        "x_declared_global": any(_symbol(row or "") == "X" for row in global_rows),
        "z17_declared_global": z17_declared,
        "comments_assign_phi17_X17": (
            "Phi17          : (X, PQ) = (17, 0)" in model_text
        ),
        "scalar_rows": scalar_rows,
        "observed_scalar_charges_PQ_X": observed_scalar_charges,
        "expected_scalar_charges_PQ_X": {
            field: list(charges) for field, charges in EXPECTED_SCALAR_CHARGES.items()
        },
        "scalar_charges_match_manuscript": scalar_charges_match,
        "scalar_representations_match": scalar_representations_match,
        "scalar_residual_Z17_matches_X_mod_17": scalar_residuals_match,
        "scalar_catalogue_exact": scalar_catalogue_exact,
        "duplicate_scalar_fields": sorted(set(duplicate_scalar_fields)),
        "unrecognized_scalar_fields": sorted(set(unrecognized_scalar_fields)),
        "fermion_rows": fermion_rows,
        "fermion_catalogue_requirements": fermion_requirements,
        "fermion_catalogue_sufficient": fermion_catalogue_sufficient,
        "fermion_catalogue_exact": fermion_catalogue_exact,
        "fermion_residual_Z17_matches_X_mod_17": fermion_residuals_match,
        "unexpected_fermion_sectors": unexpected_fermion_sectors,
        "duplicate_fermion_fields": sorted(set(duplicate_fermion_fields)),
        "gauge_catalogue_exact": gauge_catalogue_exact,
        "global_symmetry_catalogue_exact": global_symmetry_catalogue_exact,
        "native_global_symmetry_catalogue_exact": native_global_exact,
        "lagrangian": {
            "LagHC_assignments": lag_hc_values,
            "LagNoHC_assignments": lag_no_hc_values,
            "real_LagHC_present": has_lag_hc,
            "real_LagNoHC_present": has_lag_no_hc,
            "assignment_counts_exact": named_assignment_counts_exact,
            "GaugeES_LagrangianInput_assignments": lag_input_values,
            "GaugeES_LagrangianInput_entries": lag_input_entries,
            "registered_in_GaugeES_LagrangianInput": lagrangian_input_registered,
        },
        "soft_gaugino_mass_present": not soft_gaugino_absent,
        "soft_gaugino_absent_in_nonsusy_model": soft_gaugino_absent,
        "semantic_requirements": semantic_requirements,
        "statically_executable_model_contract": statically_executable,
    }


def filter_contract(filter_text: str) -> dict[str, Any]:
    allowed_requires_x_true = bool(
        re.search(
            r"def _allowed\([^)]*require_x:\s*bool\s*=\s*True",
            filter_text,
            re.S,
        )
    )
    allowed_requires_x_false = bool(
        re.search(
            r"def _allowed\([^)]*require_x:\s*bool\s*=\s*False",
            filter_text,
            re.S,
        )
    )
    entry_requires_x_true = bool(
        re.search(
            r"def _entry\([^)]*require_x:\s*bool\s*=\s*True",
            filter_text,
            re.S,
        )
    )
    entry_requires_x_false = bool(
        re.search(
            r"def _entry\([^)]*require_x:\s*bool\s*=\s*False",
            filter_text,
            re.S,
        )
    )
    live_catalogue_uses_x = bool(
        re.search(
            r"operators\s*=\s*operator_catalogue\(require_x\s*=\s*True\)",
            filter_text,
        )
    )
    live_catalogue_omits_x = bool(
        re.search(
            r"operators\s*=\s*operator_catalogue\(require_x\s*=\s*False\)",
            filter_text,
        )
    )
    requires_x = bool(
        live_catalogue_uses_x
        or entry_requires_x_true
        or allowed_requires_x_true
    ) and not live_catalogue_omits_x
    no_x_policy = bool(
        live_catalogue_omits_x
        or entry_requires_x_false
        or allowed_requires_x_false
    ) and not live_catalogue_uses_x
    phi_match = re.search(
        r'"Phi17"\s*:\s*\{[^}]*"X"\s*:\s*(-?\d+)[^}]*"Z17"\s*:\s*(-?\d+)',
        filter_text,
        re.S,
    )
    if phi_match is None:
        raise RuntimeError("Phi17 charge row not found in signed filter")
    return {
        "source": FILTER.name,
        "requires_exact_x_neutrality_by_default": requires_x,
        "encodes_option_C_no_continuous_X": no_x_policy,
        # Backward-compatible diagnostic name.  It records what the filter
        # encodes, not what this audit accepts as the authoritative contract.
        "declared_option_C_no_continuous_X": no_x_policy,
        "policy": "REQUIRE_X" if requires_x else "NO_X",
        "evidence": {
            "allowed_helper_default_true": allowed_requires_x_true,
            "allowed_helper_default_false": allowed_requires_x_false,
            "entry_default_true": entry_requires_x_true,
            "entry_default_false": entry_requires_x_false,
            "live_catalogue_calls_require_x_true": live_catalogue_uses_x,
            "live_catalogue_calls_require_x_false": live_catalogue_omits_x,
        },
        "phi17_X": int(phi_match.group(1)),
        "phi17_Z17": int(phi_match.group(2)) % 17,
    }


def phi17_monomial_audit(max_dimension: int = 4) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in range(max_dimension + 1):
        for q in range(max_dimension + 1 - p):
            degree = p + q
            if degree == 0:
                continue
            x_charge = 17 * (p - q)
            phase_sensitive = p != q
            rows.append(
                {
                    "label": f"Phi17^{p} Phi17dag^{q}",
                    "dimension": degree,
                    "powers": {"Phi17": p, "Phi17dag": q},
                    "phase_sensitive": phase_sensitive,
                    "SO10xZ17_allowed": True,
                    "continuous_X_charge": x_charge,
                    "authoritative_U1X_gauge_invariant": x_charge == 0,
                    "authoritative_status": (
                        "GAUGE_ALLOWED" if x_charge == 0 else "GAUGE_FORBIDDEN"
                    ),
                }
            )
    return sorted(rows, key=lambda row: (row["dimension"], row["label"]))


def declared_phi17_monomials(max_dimension: int = 4) -> list[dict[str, Any]]:
    """Backward-compatible public alias with corrected gauge semantics."""
    return phi17_monomial_audit(max_dimension)


def dimension17_lift(
    v_phi_gev: float = 1.0e17,
    cutoff_gev: float = 2.435e18,
    kappa: float = 1.0,
) -> dict[str, Any]:
    amplitude = 2.0 * abs(kappa) * (v_phi_gev / 2.0**0.5) ** 17 / cutoff_gev**13
    mass2 = (17.0 / v_phi_gev) ** 2 * amplitude
    x_charge = 17 * 17
    return {
        "operator": "Phi17^17 + h.c.",
        "v_phi_GeV": v_phi_gev,
        "cutoff_GeV": cutoff_gev,
        "abs_kappa": abs(kappa),
        "potential_amplitude_GeV4_if_inserted": amplitude,
        "phi17_angular_mass2_GeV2_if_inserted": mass2,
        "phi17_angular_mass_GeV_if_inserted": mass2**0.5,
        # Retained for consumers of the previous certificate.
        "potential_amplitude_GeV4": amplitude,
        "phi17_angular_mass2_GeV2": mass2,
        "phi17_angular_mass_GeV": mass2**0.5,
        "continuous_X_charge": x_charge,
        "breaks_continuous_X_by_units": float(x_charge),
        "authoritative_U1X_gauge_invariant": False,
        "authoritative_status": "GAUGE_FORBIDDEN",
        "breaks_PQ": False,
        "direct_theta_bar_shift_from_PQ_charge": 0.0,
    }


def build_report(
    *,
    manuscript_text: str | None = None,
    model_text: str | None = None,
    filter_text: str | None = None,
    external_validation_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit repository inputs or explicit in-memory adversarial fixtures."""
    manuscript = manuscript_contract(
        MANUSCRIPT.read_text(encoding="utf-8")
        if manuscript_text is None
        else manuscript_text
    )
    if model_text is None:
        model_bytes = MODEL.read_bytes()
        audited_model_text = model_bytes.decode("utf-8")
    else:
        audited_model_text = model_text
        model_bytes = model_text.encode("utf-8")
    scaffold = declared_symmetries(audited_model_text)

    driver_load_error: str | None = None
    try:
        driver_bytes = EXTERNAL_DRIVER.read_bytes()
    except OSError as exc:
        driver_load_error = f"{type(exc).__name__}: {exc}"
        driver_bytes = None

    trusted_release_manifest_load_error: str | None = None
    try:
        trusted_release_manifest_bytes = TRUSTED_SARAH_RELEASE_MANIFEST.read_bytes()
    except OSError as exc:
        trusted_release_manifest_load_error = f"{type(exc).__name__}: {exc}"
        trusted_release_manifest_bytes = b""

    manifest_load_error: str | None = None
    if model_text is None and driver_bytes is not None:
        loaded_repository_manifest: object = None
        if EXTERNAL_INPUT_MANIFEST.is_file():
            try:
                loaded_repository_manifest = json.loads(
                    EXTERNAL_INPUT_MANIFEST.read_text(encoding="utf-8")
                )
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                manifest_load_error = f"{type(exc).__name__}: {exc}"
        repository_input_manifest = validate_repository_input_manifest(
            model_bytes,
            driver_bytes,
            loaded_repository_manifest,
            trusted_release_manifest_bytes=trusted_release_manifest_bytes,
        )
        repository_input_manifest["applicable_to_repository_inputs"] = True
    elif driver_bytes is not None:
        repository_input_manifest = {
            "source": "in-memory fixture",
            "present": False,
            "expected": build_external_input_manifest(
                model_bytes, driver_bytes, trusted_release_manifest_bytes
            ),
            "checks": {},
            "failures": [],
            "valid": True,
            "applicable_to_repository_inputs": False,
            "role": "Repository manifest validation is not applied to fixtures.",
        }
    else:
        repository_input_manifest = {
            "source": str(EXTERNAL_INPUT_MANIFEST.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "present": False,
            "expected": None,
            "checks": {},
            "failures": ["validation_driver_unreadable"],
            "valid": False,
            "applicable_to_repository_inputs": model_text is None,
            "role": "The validation driver must be readable before manifesting.",
        }
    repository_input_manifest["load_error"] = manifest_load_error
    repository_input_manifest["driver_load_error"] = driver_load_error
    repository_input_manifest["trusted_release_manifest_load_error"] = (
        trusted_release_manifest_load_error
    )

    external_load_error: str | None = None
    loaded_external_artifact: object = external_validation_artifact
    # An on-disk attestation can only attest the on-disk model.  In-memory
    # adversarial fixtures must supply their own explicit test attestation.
    if model_text is None and external_validation_artifact is None:
        if EXTERNAL_VALIDATION.is_file():
            try:
                loaded_external_artifact = json.loads(
                    EXTERNAL_VALIDATION.read_text(encoding="utf-8")
                )
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                external_load_error = f"{type(exc).__name__}: {exc}"
                loaded_external_artifact = None
    external_validation = validate_external_model_artifact(
        model_bytes,
        loaded_external_artifact,
        driver_bytes=driver_bytes,
        trusted_release_manifest_bytes=trusted_release_manifest_bytes,
    )
    external_validation["load_error"] = external_load_error
    signed_filter = filter_contract(
        FILTER.read_text(encoding="utf-8") if filter_text is None else filter_text
    )
    monomials = phi17_monomial_audit()
    phase_rows = [row for row in monomials if row["phase_sensitive"]]
    phase_forbidden = [
        row
        for row in phase_rows
        if row["authoritative_status"] == "GAUGE_FORBIDDEN"
    ]
    d17 = dimension17_lift()

    static_contract_consistent = bool(
        manuscript["gauges_primitive_U1X"]
        and manuscript["phi17_X"] == 17
        and manuscript["phi17_PQ"] == 0
        and manuscript["scalar_charge_contract_matches_expected"]
        and manuscript["declares_exact_U1X_renormalizable_catalogue"]
        and scaffold["statically_executable_model_contract"]
        and repository_input_manifest["valid"]
        and signed_filter["requires_exact_x_neutrality_by_default"]
        and signed_filter["phi17_X"] == 17
    )
    contract_consistent = bool(
        static_contract_consistent and external_validation["valid"]
    )
    active_blocker = (
        None
        if contract_consistent
        else EXTERNAL_EXECUTION_BLOCKER
        if static_contract_consistent
        else STATIC_CONTRACT_BLOCKER
    )
    scientific_blockers = [] if active_blocker is None else [active_blocker]
    contract_conflicts: list[str] = []
    if not scaffold["u1x_gauged"]:
        contract_conflicts.append("executable_scaffold_omits_manuscript_U1X_gauge_factor")
    if not scaffold["scalar_charges_match_manuscript"]:
        contract_conflicts.append("executable_scaffold_scalar_charges_do_not_match_manuscript")
    if not scaffold["fermion_catalogue_exact"]:
        contract_conflicts.append("executable_scaffold_fermion_catalogue_incomplete")
    if not scaffold["lagrangian"]["real_LagHC_present"]:
        contract_conflicts.append("executable_scaffold_missing_real_LagHC")
    if not scaffold["lagrangian"]["real_LagNoHC_present"]:
        contract_conflicts.append("executable_scaffold_missing_real_LagNoHC")
    if not scaffold["soft_gaugino_absent_in_nonsusy_model"]:
        contract_conflicts.append("nonsusy_scaffold_contains_SoftGauginoMass")
    if scaffold["placeholder_evidence"]:
        contract_conflicts.append("executable_scaffold_contains_placeholder_markers")
    if scaffold["legacy_pseudo_sarah_grammar"]:
        contract_conflicts.append(
            "executable_model_is_legacy_pseudo_sarah_scaffold_not_tool_native"
        )
    elif not scaffold["tool_native_sarah_syntax"]:
        contract_conflicts.append(
            "executable_model_not_recognized_as_tool_native_sarah_syntax"
        )
    if not scaffold["gauge_catalogue_exact"]:
        contract_conflicts.append("executable_scaffold_gauge_catalogue_not_exact")
    if not scaffold["scalar_catalogue_exact"]:
        contract_conflicts.append("executable_scaffold_scalar_catalogue_not_exact")
    if not scaffold["global_symmetry_catalogue_exact"]:
        contract_conflicts.append(
            "executable_scaffold_global_symmetry_catalogue_not_exact"
        )
    if not scaffold["lagrangian"]["assignment_counts_exact"]:
        contract_conflicts.append(
            "executable_scaffold_duplicate_or_missing_lagrangian_assignment"
        )
    if not scaffold["lagrangian"]["registered_in_GaugeES_LagrangianInput"]:
        contract_conflicts.append(
            "executable_model_lacks_GaugeES_LagrangianInput_registration"
        )
    if not external_validation["valid"]:
        contract_conflicts.append(
            "executable_scaffold_lacks_current_sha256_bound_external_tool_validation"
        )
        if not (
            external_validation["checks"][
                "input_manifest_sha256_matches_entries"
            ]
            and external_validation["checks"][
                "captured_process_log_is_hash_bound"
            ]
        ):
            contract_conflicts.append(
                "external_attestation_lacks_hash_bound_manifest_or_process_log"
            )
    if not repository_input_manifest["valid"]:
        contract_conflicts.append(
            "repository_external_input_manifest_does_not_match_current_inputs"
        )
    if not signed_filter["requires_exact_x_neutrality_by_default"]:
        contract_conflicts.append("scalar_filter_omits_authoritative_X_neutrality")

    commented_fake = declared_symmetries(
        "(* Gauge[[2]] = {X, U[1], X, gX, False}; *)\n"
        "Gauge[[1]] = {G10, SO, 10};\nGlobalSymmetry = {Z[17]};"
    )
    ambiguous_fake = declared_symmetries(
        "Gauge[[1]] = {G10, SO, 10, X};\nGlobalSymmetry = {Z[17]};"
    )

    # These checks answer whether the audit executed and diagnosed the inputs
    # correctly.  Scientific inconsistency is reported separately and is not
    # mislabeled as an audit execution failure.
    checks = {
        "authoritative_manuscript_parsed": manuscript["gauges_primitive_U1X"],
        "manuscript_assigns_phi17_X17": manuscript["phi17_X"] == 17,
        "manuscript_assigns_phi17_PQ0": manuscript["phi17_PQ"] == 0,
        "manuscript_full_X_charge_tuple_parsed": manuscript["charge_tuple_parsed"],
        "manuscript_scalar_charge_contract_parsed_exactly": manuscript[
            "scalar_charge_contract_matches_expected"
        ],
        "manuscript_requires_exact_U1X_catalogue": manuscript[
            "declares_exact_U1X_renormalizable_catalogue"
        ],
        "scaffold_role_was_parsed": isinstance(
            scaffold["explicitly_incomplete_scaffold"], bool
        ),
        "scaffold_model_syntax_was_classified": scaffold["model_syntax_class"]
        in {
            "sarah_native",
            "legacy_pseudo_sarah_metadata",
            "mixed_or_unrecognized",
        },
        "legacy_pseudo_sarah_is_not_treated_as_executable": bool(
            not scaffold["legacy_pseudo_sarah_grammar"]
            or not scaffold["statically_executable_model_contract"]
        ),
        "scaffold_SO10_and_Z17_parsed": scaffold["so10_gauged"]
        and scaffold["z17_declared_global"],
        "scaffold_gauge_contract_was_parsed": isinstance(
            scaffold["u1x_gauged"], bool
        ),
        "scaffold_scalar_contract_was_parsed": set(
            scaffold["observed_scalar_charges_PQ_X"]
        )
        == set(EXPECTED_SCALAR_CHARGES),
        "scaffold_fermion_catalogue_was_classified": isinstance(
            scaffold["fermion_catalogue_exact"], bool
        ),
        "scaffold_lagrangian_was_classified": all(
            isinstance(scaffold["lagrangian"][name], bool)
            for name in ("real_LagHC_present", "real_LagNoHC_present")
        ),
        "scaffold_lagrangian_input_registration_was_classified": isinstance(
            scaffold["lagrangian"][
                "registered_in_GaugeES_LagrangianInput"
            ],
            bool,
        ),
        "scaffold_static_executability_was_classified": isinstance(
            scaffold["statically_executable_model_contract"], bool
        ),
        "external_execution_attestation_was_classified": isinstance(
            external_validation["valid"], bool
        ),
        "external_manifest_and_log_evidence_were_classified": all(
            isinstance(external_validation["checks"][name], bool)
            for name in (
                "input_manifest_sha256_matches_entries",
                "captured_process_log_is_hash_bound",
            )
        ),
        "commented_fake_u1x_row_is_ignored": not commented_fake["u1x_gauged"],
        "ambiguous_non_u1_gauge_row_named_x_is_rejected": not ambiguous_fake[
            "u1x_gauged"
        ],
        "filter_X_policy_parsed": signed_filter["policy"] in {"REQUIRE_X", "NO_X"},
        "filter_phi17_X17_parsed": signed_filter["phi17_X"] == 17,
        "authoritative_contract_comparison_completed": isinstance(
            contract_consistent, bool
        ),
        "all_dim_le4_phase_sensitive_phi17_terms_gauge_forbidden": (
            bool(phase_rows) and len(phase_forbidden) == len(phase_rows)
        ),
        "phi17_to_17_is_not_U1X_gauge_invariant": not d17[
            "authoritative_U1X_gauge_invariant"
        ],
    }
    audit_failures = [name for name, passed in checks.items() if not passed]
    audit_ok = not audit_failures

    return {
        "status": (
            "X_SYMMETRY_AUDIT_EXECUTION_FAILED"
            if not audit_ok
            else "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__CONSISTENT"
            if contract_consistent
            else "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__BLOCKED"
        ),
        "overall_state": (
            "EXECUTION_FAIL"
            if not audit_ok
            else "PASS"
            if contract_consistent
            else "BLOCKED"
        ),
        "contract_consistent": contract_consistent,
        "static_contract_consistent": static_contract_consistent,
        "blocker": active_blocker,
        "scientific_blockers": scientific_blockers,
        "contract_conflicts": contract_conflicts,
        "n_checks": len(checks),
        "n_failed": len(audit_failures),
        "failures": audit_failures,
        "audit_failures": audit_failures,
        "checks": checks,
        "authoritative_manuscript_contract": manuscript,
        "executable_scaffold_contract": scaffold,
        "external_model_validation": external_validation,
        "repository_external_input_manifest": repository_input_manifest,
        # Kept for callers of the previous report schema.
        "declared_symmetries": scaffold,
        "signed_filter_contract": signed_filter,
        "authoritative_dim_le4_phi17_monomials": monomials,
        "declared_dim_le4_phi17_monomials": monomials,
        "phase_sensitive_count": len(phase_rows),
        "phase_sensitive_gauge_forbidden_count": len(phase_forbidden),
        "dimension17_candidate": d17,
        "required_resolution": {
            "selected": (
                None
                if contract_consistent
                else "external_SARAH_execution"
                if static_contract_consistent
                else "option_A_gauge_U1X"
            ),
            "external_SARAH_execution": {
                "required": not external_validation["valid"],
                "driver": EXTERNAL_DRIVER_REPOSITORY_PATH,
                "input_manifest": str(
                    EXTERNAL_INPUT_MANIFEST.relative_to(ROOT)
                ).replace("\\", "/"),
                "attestation_destination": str(
                    EXTERNAL_VALIDATION.relative_to(ROOT)
                ).replace("\\", "/"),
                "claim_boundary": (
                    "Only a real zero-exit SARAH 4.15.3 process over the exact "
                    "trusted source tree, with unchanged hash-bound Wolfram "
                    "launcher/kernel bytes and all five unique PASS markers, "
                    "may create the v3 external attestation."
                ),
            },
            "option_A_gauge_U1X": {
                "accepted": True,
                "requirements": [
                    (
                        "replace the legacy pseudo-SARAH metadata grammar with "
                        "indexed, tool-native SARAH Gauge/Global/matter syntax"
                    ),
                    "declare a native SO[10] row and a U[1] gauge row named X",
                    (
                        "encode the exact manuscript X charges and residual Z17 "
                        "charges in native matter rows"
                    ),
                    "retain the complete anomaly-cancelling fermion content",
                    "add covariant derivatives and the U(1)_X gauge coupling",
                    "supply substantive LagHC and LagNoHC definitions",
                    (
                        "register LagHC and LagNoHC under "
                        "DEFINITION[GaugeES][LagrangianInput]"
                    ),
                    "remove SoftGauginoMass from the nonsupersymmetric model",
                    "remove scaffold and external-Clebsch placeholders",
                    (
                        "produce a fresh external SARAH 4.15.3 parse, model-load, "
                        "Lagrangian, gauge-invariance, and anomaly-check attestation "
                        "bound to the tool-native model format, exact model-file "
                        "SHA-256, official canonical SARAH source-tree manifest, "
                        "validation driver, resolved Wolfram executable bytes and "
                        "version, and hash-bound probe/validation logs"
                    ),
                    "enforce exact X neutrality in the scalar-potential census",
                    "prove and quotient the Phi17 phase as the eaten Goldstone",
                ],
            },
            "option_B_exact_global_U1X": {
                "accepted": False,
                "reason": "does not match the manuscript's gauged primitive U(1)_X",
            },
            "option_C_no_continuous_X": {
                "accepted": False,
                "rejected": True,
                "reason": (
                    "contradicts the authoritative gauged-U(1)_X manuscript and "
                    "treats an incomplete executable scaffold as the theory definition"
                ),
            },
        },
        "flag": {
            "audit_executed_honestly": audit_ok,
            "authoritative_gauged_U1X_contract": manuscript[
                "gauges_primitive_U1X"
            ],
            "x_selection_rule_consistently_declared": static_contract_consistent,
            "static_contract_consistent": static_contract_consistent,
            "contract_consistent": contract_consistent,
            "structured_u1x_gauge_row_present": scaffold["u1x_gauged"],
            "model_syntax_class": scaffold["model_syntax_class"],
            "tool_native_sarah_syntax": scaffold["tool_native_sarah_syntax"],
            "legacy_pseudo_sarah_grammar": scaffold[
                "legacy_pseudo_sarah_grammar"
            ],
            "lagrangian_registered_in_GaugeES_LagrangianInput": scaffold[
                "lagrangian"
            ]["registered_in_GaugeES_LagrangianInput"],
            "scalar_charge_contract_complete": scaffold[
                "scalar_charges_match_manuscript"
            ],
            "fermion_catalogue_complete": scaffold["fermion_catalogue_exact"],
            "real_nonsusy_lagrangian_present": scaffold["lagrangian"][
                "real_LagHC_present"
            ]
            and scaffold["lagrangian"]["real_LagNoHC_present"],
            "statically_executable_model_contract": scaffold[
                "statically_executable_model_contract"
            ],
            "externally_executed_model_contract": external_validation["valid"],
            "external_validation_bound_to_exact_model_sha256": (
                external_validation["fresh_for_exact_model_bytes"]
            ),
            "external_validation_input_manifest_bound": external_validation[
                "checks"
            ]["input_manifest_sha256_matches_entries"],
            "external_validation_process_log_hash_bound": external_validation[
                "checks"
            ]["captured_process_log_is_hash_bound"],
            "option_C_no_continuous_X_applied": False,
            "option_C_no_continuous_X_rejected": True,
            "dim_le4_phase_sensitive_phi17_terms_gauge_forbidden": (
                len(phase_forbidden) == len(phase_rows) and bool(phase_rows)
            ),
            "phi17_phase_eaten": False,
            "dimension17_operator_is_x_invariant": False,
            "dimension17_operator_directly_breaks_pq": False,
            "complete_multifield_model": contract_consistent,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The authoritative manuscript, executable gauge scaffold, and scalar "
            "filter consistently implement gauged U(1)_X. Every phase-sensitive "
            "Phi17 monomial through dimension four, and Phi17^17 itself, remains "
            "gauge forbidden. This contract result alone does not validate G1-G8."
            if contract_consistent
            else "The authoritative manuscript, native non-supersymmetric SARAH "
            "model, exact charge catalogues, residual Z17 assignments, "
            "GaugeES Lagrangian registration, scalar filter, and hash-bound "
            "input bundle are statically consistent. The sole remaining "
            "contract blocker is a real external SARAH execution of the "
            "shipped driver; the official SARAH 4.15.3 source tree is frozen "
            "and hash-verified, but no current source/runtime-bound execution "
            "attestation is present or inferred. "
            "This static result alone does not validate G1-G8."
            if static_contract_consistent
            else "The audit executes successfully but the scientific contract is "
            "blocked: the authoritative manuscript gauges U(1)_X with "
            "X(Phi17)=17, and the executable contract has not been demonstrated "
            "end to end. The current model syntax is classified as "
            f"{scaffold['model_syntax_class']}. A syntactic Gauge row or legacy "
            "metadata pair is insufficient: indexed tool-native SARAH syntax, "
            "exact scalar charges, the complete anomaly-cancelling fermion "
            "catalogue, GaugeES LagrangianInput registration, real LagHC/LagNoHC "
            "definitions, nonsupersymmetric consistency, a placeholder-free "
            "model, and a fresh external execution attestation with a canonical "
            "input manifest and hash-bound process log are all required. The explicit "
            "scalar-filter "
            "policy is audited separately and cannot unlock the scaffold. Option "
            "C is rejected. Every "
            "phase-sensitive Phi17 monomial through dimension four, and Phi17^17 "
            "itself, is forbidden by the authoritative gauge symmetry. The "
            "repository must repair the executable contract before whole-theory "
            "validation or exclusion claims."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact X-symmetry consistency gate - v20",
            "",
            f"**Status:** `{report['status']}`",
            f"**Overall state:** `{report['overall_state']}`",
            f"**Static contract consistent:** `{report['static_contract_consistent']}`",
            f"**Contract consistent:** `{report['contract_consistent']}`",
            f"**Blocker:** `{report['blocker']}`",
            "",
            report["verdict"],
            "",
            "- Authoritative contract: gauged `U(1)_X`, `X(Phi17)=17`",
            (
                "- Model syntax classification: "
                f"`{report['executable_scaffold_contract']['model_syntax_class']}`"
            ),
            (
                "- Tool-native indexed SARAH syntax: "
                f"`{report['executable_scaffold_contract']['tool_native_sarah_syntax']}`"
            ),
            (
                "- Structured executable `U[1]` row (`GX`, tool-safe `xcharge` label): "
                f"`{report['executable_scaffold_contract']['u1x_gauged']}`"
            ),
            (
                "- Exact manuscript scalar charge pairs: "
                f"`{report['executable_scaffold_contract']['scalar_charges_match_manuscript']}`"
            ),
            (
                "- Complete anomaly-cancelling fermion catalogue: "
                f"`{report['executable_scaffold_contract']['fermion_catalogue_exact']}`"
            ),
            (
                "- Real `LagHC` and `LagNoHC`: "
                f"`{report['flag']['real_nonsusy_lagrangian_present']}`"
            ),
            (
                "- Nonsupersymmetric model is free of `SoftGauginoMass`: "
                f"`{report['executable_scaffold_contract']['soft_gaugino_absent_in_nonsusy_model']}`"
            ),
            (
                "- Registered `DEFINITION[GaugeES][LagrangianInput]`: "
                f"`{report['executable_scaffold_contract']['lagrangian']['registered_in_GaugeES_LagrangianInput']}`"
            ),
            (
                "- Tool-native, placeholder-free static model contract: "
                f"`{report['executable_scaffold_contract']['statically_executable_model_contract']}`"
            ),
            (
                "- Repository model/driver input manifest current: "
                f"`{report['repository_external_input_manifest']['valid']}`"
            ),
            (
                "- Source-tree/runtime/log-bound external SARAH v3 validation: "
                f"`{report['external_model_validation']['valid']}`"
            ),
            (
                "- Gauge-forbidden phase-sensitive Phi17 monomials at dimension "
                f"<=4: `{report['phase_sensitive_gauge_forbidden_count']}`"
            ),
            "- `Phi17^17 + h.c.` U(1)_X gauge invariant: `False`",
            "- Option C accepted: `False`",
            "",
        ]
    )


def exit_code(report: dict[str, Any], *, require_consistent: bool = False) -> int:
    if report["n_failed"]:
        return 1
    if require_consistent and not report["contract_consistent"]:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-consistent",
        action="store_true",
        help=(
            "return nonzero unless static contracts and current external "
            "execution evidence are both valid"
        ),
    )
    args = parser.parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\r\n",
    )
    OUT_MD.write_text(
        write_markdown(report), encoding="utf-8", newline="\r\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return exit_code(report, require_consistent=args.require_consistent)


if __name__ == "__main__":
    raise SystemExit(main())
