#!/usr/bin/env python3
"""Probe the official NA62 HEPData Figure 2-a payload via publication links."""
from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
PUBLICATION_RECORD = "https://www.hepdata.net/record/ins2953428?format=json"
TARGET_MASS_GEV = 153.5e-6 * 1e-9
TARGET_MASS_MEV = TARGET_MASS_GEV * 1e3


def fetch_json(url: str, timeout: float = 45.0) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "so10-axion-v20-reproducibility/1.0",
            "Accept": "application/json",
            "Referer": "https://www.hepdata.net/record/ins2953428",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
        if response.status != 200:
            raise RuntimeError(f"HEPData returned HTTP {response.status} for {url}")
    return json.loads(payload.decode("utf-8"))


def schema_summary(value: Any, *, depth: int = 0, max_depth: int = 5) -> Any:
    if depth >= max_depth:
        if isinstance(value, dict):
            return {"type": "dict", "n_keys": len(value), "keys": list(value)[:16]}
        if isinstance(value, list):
            return {"type": "list", "length": len(value)}
        return type(value).__name__
    if isinstance(value, dict):
        return {
            "type": "dict",
            "keys": {
                str(key): schema_summary(child, depth=depth + 1, max_depth=max_depth)
                for key, child in list(value.items())[:30]
            },
        }
    if isinstance(value, list):
        return {
            "type": "list",
            "length": len(value),
            "sample": [
                schema_summary(child, depth=depth + 1, max_depth=max_depth)
                for child in value[:3]
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


def find_figure_2a_table(publication: dict[str, Any]) -> dict[str, Any]:
    tables = publication.get("data_tables")
    if not isinstance(tables, list):
        raise KeyError("publication JSON has no data_tables list")
    matches = [
        table
        for table in tables
        if isinstance(table, dict)
        and str(table.get("name", "")).strip().lower() == "figure 2-a"
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one Figure 2-a table, found {len(matches)}")
    return matches[0]


def normalize_data_url(raw_url: str) -> str:
    if not raw_url:
        raise ValueError("Figure 2-a table has no JSON download URL")
    joined = urllib.parse.urljoin("https://www.hepdata.net", raw_url)
    parts = urllib.parse.urlsplit(joined)
    encoded_path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/;:@")
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment)
    )


def payload_diagnostics(payload: Any, url: str) -> dict[str, Any]:
    numeric = list(iter_numeric_leaves(payload))
    return {
        "url": url,
        "schema": schema_summary(payload),
        "top_level_type": type(payload).__name__,
        "top_level_keys": list(payload)[:50] if isinstance(payload, dict) else None,
        "numeric_leaf_count": len(numeric),
        "numeric_leaf_head": [
            {"path": list(path), "value": number} for path, number in numeric[:40]
        ],
        "numeric_leaf_tail": [
            {"path": list(path), "value": number} for path, number in numeric[-40:]
        ],
        "mass_keyword_paths": [
            list(path)
            for path in keyword_paths(payload, ("mass", "m_x", "mx", "gev", "mev"))[:150]
        ],
        "limit_keyword_paths": [
            list(path)
            for path in keyword_paths(payload, ("limit", "upper", "branch", "dependent", "observed"))[:150]
        ],
    }


def build_report() -> dict[str, Any]:
    errors: list[str] = []
    records: dict[str, Any] = {}
    table_metadata: dict[str, Any] | None = None
    table_payload: Any | None = None
    table_url = ""
    try:
        publication = fetch_json(PUBLICATION_RECORD)
        records["publication"] = {
            "url": PUBLICATION_RECORD,
            "recid": publication.get("recid"),
            "version": publication.get("version"),
            "hepdata_doi": (publication.get("record") or {}).get("hepdata_doi"),
            "n_visible_tables": len(publication.get("data_tables") or []),
        }
        table_metadata = find_figure_2a_table(publication)
        data_links = table_metadata.get("data") or {}
        table_url = normalize_data_url(str(data_links.get("json", "")))
        table_payload = fetch_json(table_url)
        records["figure_2a"] = payload_diagnostics(table_payload, table_url)
        records["figure_2a"]["metadata"] = {
            "name": table_metadata.get("name"),
            "description": table_metadata.get("description"),
            "doi": table_metadata.get("doi"),
            "id": table_metadata.get("id"),
            "location": table_metadata.get("location"),
            "all_download_links": data_links,
        }
    except (OSError, RuntimeError, KeyError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
        errors.append(f"{type(exc).__name__}: {exc}")

    captured = table_payload is not None
    return {
        "status": "NA62_HEPDATA_SCHEMA_CAPTURED" if captured else "NA62_HEPDATA_PROBE_FAILED",
        "target": {
            "axion_mass_GeV": TARGET_MASS_GEV,
            "axion_mass_MeV": TARGET_MASS_MEV,
            "note": "The v20 mass is effectively zero on the MeV-scale NA62 grid.",
        },
        "n_errors": len(errors),
        "errors": errors,
        "records": records,
        "flag": {
            "official_hepdata_contacted": "publication" in records,
            "figure_2a_discovered_from_publication": table_metadata is not None,
            "figure_2a_payload_captured": captured,
            "pointwise_limit_parsed": False,
            "limit_vendored_for_offline_ci": False,
            "counterexample_excluded": False,
        },
        "next_step": (
            "Use the captured Figure 2-a schema to implement a narrow parser, freeze "
            "the official values with SHA256 provenance, and compare the zero-mass "
            "observed 90% CL limit with BR(K+->pi+a)=3.65003319938114e-11."
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
