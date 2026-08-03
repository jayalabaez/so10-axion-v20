#!/usr/bin/env python3
"""Probe the official NA62 HEPData Figure 2-a table without guessing schema.

The purpose of this first-stage module is to discover and record the exact
machine-readable payload for the model-independent K+ -> pi+ X limit.  It does
not yet promote the table into a frozen repository input.
"""
from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
PUBLICATION_RECORD = "https://www.hepdata.net/record/ins2953428?format=json"
CURRENT_TABLE_RECORD = "https://www.hepdata.net/record/165349?format=json"
LEGACY_TABLE_RECORD = "https://www.hepdata.net/record/160250?format=json"
TARGET_MASS_GEV = 153.5e-6 * 1e-9
TARGET_MASS_MEV = TARGET_MASS_GEV * 1e3


def fetch_json(url: str, timeout: float = 45.0) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "so10-axion-v20-reproducibility/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
        if response.status != 200:
            raise RuntimeError(f"HEPData returned HTTP {response.status} for {url}")
    return json.loads(payload.decode("utf-8"))


def schema_summary(value: Any, *, depth: int = 0, max_depth: int = 4) -> Any:
    """Compact recursive type/key summary suitable for CI logs."""
    if depth >= max_depth:
        if isinstance(value, dict):
            return {"type": "dict", "n_keys": len(value), "keys": list(value)[:12]}
        if isinstance(value, list):
            return {"type": "list", "length": len(value)}
        return type(value).__name__
    if isinstance(value, dict):
        return {
            "type": "dict",
            "keys": {
                str(key): schema_summary(child, depth=depth + 1, max_depth=max_depth)
                for key, child in list(value.items())[:20]
            },
        }
    if isinstance(value, list):
        return {
            "type": "list",
            "length": len(value),
            "sample": [
                schema_summary(child, depth=depth + 1, max_depth=max_depth)
                for child in value[:2]
            ],
        }
    return {"type": type(value).__name__, "value": value}


def iter_numeric_leaves(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], float]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_numeric_leaves(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_numeric_leaves(child, path + (str(index),))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if math.isfinite(number):
            yield path, number
    elif isinstance(value, str):
        try:
            number = float(value)
        except ValueError:
            return
        if math.isfinite(number):
            yield path, number


def keyword_paths(value: Any, keywords: tuple[str, ...], path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    found: list[tuple[str, ...]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            new_path = path + (str(key),)
            text = str(key).lower()
            if any(token in text for token in keywords):
                found.append(new_path)
            found.extend(keyword_paths(child, keywords, new_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(keyword_paths(child, keywords, path + (str(index),)))
    return found


def build_report() -> dict[str, Any]:
    results: dict[str, Any] = {}
    errors: list[str] = []
    for name, url in (
        ("publication", PUBLICATION_RECORD),
        ("current_figure_2a", CURRENT_TABLE_RECORD),
        ("legacy_figure_2a", LEGACY_TABLE_RECORD),
    ):
        try:
            payload = fetch_json(url)
        except (OSError, RuntimeError, json.JSONDecodeError, urllib.error.URLError) as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        numeric = list(iter_numeric_leaves(payload))
        results[name] = {
            "url": url,
            "schema": schema_summary(payload),
            "top_level_type": type(payload).__name__,
            "top_level_keys": list(payload)[:50] if isinstance(payload, dict) else None,
            "numeric_leaf_count": len(numeric),
            "numeric_leaf_head": [
                {"path": list(path), "value": number} for path, number in numeric[:25]
            ],
            "numeric_leaf_tail": [
                {"path": list(path), "value": number} for path, number in numeric[-25:]
            ],
            "mass_keyword_paths": [
                list(path)
                for path in keyword_paths(payload, ("mass", "m_x", "mx", "gev", "mev"))[:100]
            ],
            "limit_keyword_paths": [
                list(path)
                for path in keyword_paths(payload, ("limit", "upper", "branch", "dependent", "observed"))[:100]
            ],
        }
    current_ok = "current_figure_2a" in results
    return {
        "status": "NA62_HEPDATA_SCHEMA_CAPTURED" if current_ok else "NA62_HEPDATA_PROBE_FAILED",
        "target": {
            "axion_mass_GeV": TARGET_MASS_GEV,
            "axion_mass_MeV": TARGET_MASS_MEV,
            "note": "The v20 mass is effectively zero on the MeV-scale NA62 grid.",
        },
        "n_errors": len(errors),
        "errors": errors,
        "records": results,
        "flag": {
            "official_hepdata_contacted": current_ok,
            "figure_2a_payload_captured": current_ok,
            "pointwise_limit_parsed": False,
            "limit_vendored_for_offline_ci": False,
            "counterexample_excluded": False,
        },
        "next_step": (
            "Use the captured schema to implement a narrow parser, freeze the official "
            "Figure 2-a values with SHA256 provenance, and compare the zero-mass observed "
            "90% CL limit with BR(K+->pi+a)=3.65003319938114e-11."
        ),
    }


def main() -> int:
    report = build_report()
    ROOT.joinpath("NA62_HEPDATA_PROBE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "NA62_HEPDATA_SCHEMA_CAPTURED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
