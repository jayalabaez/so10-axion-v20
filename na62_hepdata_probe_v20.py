#!/usr/bin/env python3
"""Online drift guard for the official NA62 HEPData Figure 2-a anchors.

This network-dependent check is intentionally separate from the main offline
physics workflow. It follows official HEPData publication metadata, parses the
observed 90% CL upper-limit column, and verifies that the vendored zero-mass
anchors have not drifted.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PUBLICATION_RECORD = "https://www.hepdata.net/record/ins2953428?format=json"
ANCHOR_PATH = ROOT / "data" / "na62_figure2a_v2_zero_mass_anchor.json"


def fetch_json(url: str, timeout: float = 45.0) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 so10-axion-v20-reproducibility/1.0",
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://www.hepdata.net/record/ins2953428",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def find_figure_2a(publication: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row
        for row in publication.get("data_tables", [])
        if isinstance(row, dict)
        and str(row.get("name", "")).strip().lower() == "figure 2-a"
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one Figure 2-a table, found {len(matches)}")
    return matches[0]


def endpoint_candidates(publication: dict[str, Any], table: dict[str, Any]) -> list[str]:
    recid = int(publication["recid"])
    version = int(publication["version"])
    table_id = int(table["id"])
    encoded_name = urllib.parse.quote(str(table["name"]), safe="")
    raw_download = str((table.get("data") or {}).get("json", ""))
    candidates = [
        f"https://www.hepdata.net/record/ins2953428?format=json&table={encoded_name}",
        f"https://www.hepdata.net/record/data/{recid}/{table_id}/{version}?format=json",
        f"https://www.hepdata.net/record/data/{recid}/{table_id}/{version}",
    ]
    if raw_download:
        joined = urllib.parse.urljoin("https://www.hepdata.net", raw_download)
        parts = urllib.parse.urlsplit(joined)
        path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/;:@")
        candidates.append(
            urllib.parse.urlunsplit(
                (parts.scheme, parts.netloc, path, parts.query, parts.fragment)
            )
        )
    return candidates


def fetch_first(urls: list[str]) -> tuple[dict[str, Any], str, list[str]]:
    failures: list[str] = []
    for url in urls:
        try:
            payload = fetch_json(url)
            if not isinstance(payload, dict):
                raise TypeError("table payload is not an object")
            return payload, url, failures
        except (OSError, RuntimeError, TypeError, json.JSONDecodeError, urllib.error.URLError) as exc:
            failures.append(f"{url}: {type(exc).__name__}: {exc}")
    raise RuntimeError("all official endpoints failed: " + " | ".join(failures))


def parse_observed_curve(payload: dict[str, Any]) -> list[dict[str, float]]:
    headers = payload.get("headers")
    values = payload.get("values")
    if not isinstance(headers, list) or len(headers) < 2:
        raise ValueError("missing HEPData headers")
    if str(headers[0].get("name", "")) != "X mass":
        raise ValueError("unexpected independent-variable header")
    if str(headers[1].get("name", "")) != "Obs. BR UL":
        raise ValueError("unexpected observed-limit header")
    if not isinstance(values, list):
        raise ValueError("missing HEPData values")

    curve: list[dict[str, float]] = []
    for row in values:
        x = row.get("x") or []
        y = row.get("y") or []
        if len(x) != 1:
            raise ValueError("expected one X-mass value per row")
        observed = [item for item in y if str(item.get("group")) == "0"]
        if len(observed) != 1:
            raise ValueError("expected one observed upper limit per row")
        mass = float(x[0]["value"])
        limit = float(observed[0]["value"])
        if not (math.isfinite(mass) and math.isfinite(limit) and limit > 0.0):
            raise ValueError("non-finite or non-positive HEPData value")
        curve.append({"mass_MeV": mass, "observed_br_ul_90cl": limit})
    if any(b["mass_MeV"] <= a["mass_MeV"] for a, b in zip(curve, curve[1:])):
        raise ValueError("NA62 mass grid is not strictly increasing")
    return curve


def build_report() -> dict[str, Any]:
    errors: list[str] = []
    result: dict[str, Any] = {}
    try:
        publication = fetch_json(PUBLICATION_RECORD)
        table = find_figure_2a(publication)
        payload, endpoint, failed_before_success = fetch_first(
            endpoint_candidates(publication, table)
        )
        curve = parse_observed_curve(payload)
        anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
        expected = anchor["anchor_points"]
        comparisons = []
        for expected_row, live_row in zip(expected, curve[: len(expected)]):
            mass_match = math.isclose(
                float(expected_row["mass_MeV"]),
                live_row["mass_MeV"],
                rel_tol=0.0,
                abs_tol=1e-15,
            )
            limit_match = math.isclose(
                float(expected_row["observed_br_ul_90cl"]),
                live_row["observed_br_ul_90cl"],
                rel_tol=1e-12,
                abs_tol=0.0,
            )
            comparisons.append(
                {
                    "expected": expected_row,
                    "live": live_row,
                    "mass_match": mass_match,
                    "limit_match": limit_match,
                }
            )
        drift = any(
            not row["mass_match"] or not row["limit_match"]
            for row in comparisons
        )
        canonical_payload = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        result = {
            "publication_doi": (publication.get("record") or {}).get("hepdata_doi"),
            "table_doi": table.get("doi"),
            "table_id": table.get("id"),
            "version": publication.get("version"),
            "successful_endpoint": endpoint,
            "failed_endpoints_before_success": failed_before_success,
            "n_curve_points": len(curve),
            "curve_first": curve[:2],
            "curve_last": curve[-2:],
            "live_payload_sha256": hashlib.sha256(canonical_payload).hexdigest(),
            "anchor_comparisons": comparisons,
            "anchor_drift_detected": drift,
        }
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")

    drift = bool(result.get("anchor_drift_detected", True))
    passed = not errors and not drift and result.get("n_curve_points") == 151
    return {
        "status": "PASS" if passed else "FAIL",
        "n_errors": len(errors),
        "errors": errors,
        "result": result,
        "flag": {
            "official_publication_contacted": bool(result),
            "observed_curve_parsed": bool(result),
            "expected_151_points": result.get("n_curve_points") == 151,
            "vendored_anchor_matches_live_table": not drift,
            "network_check_used_for_main_physics_ci": False,
        },
        "verdict": (
            "The official NA62 Figure 2-a observed-limit anchors match the vendored offline values."
            if passed
            else "The online NA62 provenance or drift check failed."
        ),
    }


def main() -> int:
    report = build_report()
    ROOT.joinpath("NA62_HEPDATA_DRIFT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
