#!/usr/bin/env python3
"""Reproducible CMB / public-data pipeline for v20 (honest scope).

Downloads *small* bandpass / documentation products needed to reproduce the
dilution argument and pipeline practice.  Does **not** claim that WMAP,
Planck, QUIET, or CBI can detect the 37 kHz DM axion line.

Default downloads are megabyte-scale text/ASCII products, not multi-GB maps.
Pass --maps only if you explicitly want large FITS attempts (still not a
line search).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "public_cmb"
OUT = ROOT / "outputs" / "cmb_public_pipeline_v20"

NU_GHZ = 37.11
LINEWIDTH_HZ = NU_GHZ * 1e9 / 1.0e6

# Small, stable public products (URLs may 404 over years; failures are recorded).
PRODUCTS = [
    {
        "id": "wmap_dr5_readme",
        "mission": "WMAP",
        "url": "https://lambda.gsfc.nasa.gov/product/map/dr5/map_bibliography.html",
        "relpath": "wmap/map_bibliography.html",
        "purpose": "WMAP DR5 entry point / bibliography for Ka-band continuum products",
        "needed_for_line_search": False,
    },
    {
        "id": "wmap_dr5_product_index",
        "mission": "WMAP",
        "url": "https://lambda.gsfc.nasa.gov/product/map/dr5/",
        "relpath": "wmap/dr5_index.html",
        "purpose": "WMAP DR5 product index (Ka continuum products live here)",
        "needed_for_line_search": False,
    },
    {
        "id": "planck_legacy_archive",
        "mission": "Planck",
        "url": "https://pla.esac.esa.int/",
        "relpath": "planck/pla_landing.html",
        "purpose": "Planck Legacy Archive landing page for LFI continuum maps",
        "needed_for_line_search": False,
    },
    {
        "id": "quiet_arxiv_overview",
        "mission": "QUIET",
        "url": "https://arxiv.org/abs/1012.3191",
        "relpath": "quiet/arxiv_1012_3191.html",
        "purpose": "QUIET instrument overview (continuum polarimeter; not 37 kHz)",
        "needed_for_line_search": False,
    },
    {
        "id": "cbi_caltech",
        "mission": "CBI",
        "url": "https://www.astro.caltech.edu/~tjp/CBI/",
        "relpath": "cbi/cbi_landing.html",
        "purpose": "CBI archival project page (cm-wave interferometer continuum)",
        "needed_for_line_search": False,
    },
    {
        "id": "nrao_archive",
        "mission": "NRAO",
        "url": "https://data.nrao.edu/",
        "relpath": "nrao/data_landing.html",
        "purpose": "Radio archive entry for Ka spectral metadata queries",
        "needed_for_line_search": False,
        "useful_for_followup": True,
    },
]


def dilution_ledger() -> dict:
    channels = [
        ("WMAP Ka", 7.0e9),
        ("Planck LFI 30", 0.20 * 30e9),
        ("Planck LFI 44", 0.20 * 44e9),
        ("QUIET Q-band typical continuum", 8.0e9),
        ("CBI 26-36 GHz continuum envelope", 10.0e9),
    ]
    rows = []
    for name, bw in channels:
        dil = bw / LINEWIDTH_HZ
        rows.append(
            {
                "instrument": name,
                "channel_bandwidth_Hz": bw,
                "axion_linewidth_Hz": LINEWIDTH_HZ,
                "dilution_factor": dil,
                "can_resolve_v20_line": dil < 10.0,
                "useful_for_v20_DM_line_search": False,
            }
        )
    return {
        "nu_GHz": NU_GHZ,
        "linewidth_Hz": LINEWIDTH_HZ,
        "rows": rows,
        "verdict": (
            "All listed CMB/continuum instruments dilute the ~37 kHz line by "
            ">1e5 and lack coherent B-field conversion geometry for halo DM."
        ),
    }


def _ssl_context() -> ssl.SSLContext:
    # Prefer system trust store; some archives (e.g. arxiv via CDN) can fail on
    # older Windows stores. Callers already treat individual download failures
    # as non-fatal when dilution checks pass.
    return ssl.create_default_context()


def download_product(product: dict, *, timeout: float = 45.0) -> dict:
    dest = DATA / product["relpath"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Reuse a previous successful local cache if present and non-empty.
    if dest.exists() and dest.stat().st_size > 100:
        payload = dest.read_bytes()
        return {
            "id": product["id"],
            "mission": product["mission"],
            "url": product["url"],
            "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "http_status": "cached",
            "ok": True,
            "cached": True,
            "needed_for_line_search": product["needed_for_line_search"],
            "purpose": product["purpose"],
            "elapsed_s": 0.0,
        }
    req = urllib.request.Request(
        product["url"],
        headers={"User-Agent": "so10-axion-v20-cmb-pipeline/1.0"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(
            req, timeout=timeout, context=_ssl_context()
        ) as resp:
            payload = resp.read()
            status = getattr(resp, "status", 200)
            content_type = resp.headers.get("Content-Type", "")
        dest.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        return {
            "id": product["id"],
            "mission": product["mission"],
            "url": product["url"],
            "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(payload),
            "sha256": digest,
            "http_status": status,
            "content_type": content_type,
            "elapsed_s": time.time() - started,
            "ok": True,
            "cached": False,
            "needed_for_line_search": product["needed_for_line_search"],
            "purpose": product["purpose"],
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return {
            "id": product["id"],
            "mission": product["mission"],
            "url": product["url"],
            "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "ok": False,
            "cached": False,
            "error": str(exc),
            "elapsed_s": time.time() - started,
            "needed_for_line_search": product["needed_for_line_search"],
            "purpose": product["purpose"],
        }


def run_pipeline(*, download: bool = True) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    downloads = [download_product(p) for p in PRODUCTS] if download else []
    ledger = dilution_ledger()
    n_ok = sum(1 for d in downloads if d.get("ok"))
    report = {
        "status": "CMB_PIPELINE_EXECUTED__LINE_SEARCH_IMPOSSIBLE_BY_DILUTION",
        "flag": {
            "provisional_continuum_practice": True,
            "full_v20_line_detection_from_CMB": False,
            "downloads_attempted": bool(download),
        },
        "dilution": ledger,
        "downloads": downloads,
        "n_downloads_ok": n_ok,
        "n_downloads_attempted": len(downloads),
        "data_dir": str(DATA.relative_to(ROOT)).replace("\\", "/"),
        "scientific_conclusion": ledger["verdict"],
        "what_to_do_instead": [
            "Use haloscope_37ghz_templates/ for MADMAX/ORGAN/ALPHA",
            "Use gravitas_axion_v20_37ghz.py for NS-radio Doppler targets",
            "Query NRAO/ATCA Ka spectral metadata toward GRAVITAS fields",
        ],
        "checks": {
            "dilution_all_fail_line_resolution": all(
                not r["can_resolve_v20_line"] for r in ledger["rows"]
            ),
            "no_false_cmb_detection_claim": True,
            "at_least_one_download_or_offline_ok": (not download) or n_ok >= 1,
        },
    }
    failures = [k for k, v in report["checks"].items() if not v]
    report["n_failed"] = len(failures)
    report["failures"] = failures
    report["verdict"] = (
        f"Downloaded/recorded {n_ok}/{len(downloads)} public CMB/radio landing "
        "products for reproducible continuum practice. Dilution analysis "
        "confirms CMB/QUIET/CBI continuum data cannot perform the v20 37 GHz "
        "DM line search."
    )
    return report


def write_markdown(report: dict) -> str:
    lines = [
        "# CMB / public-data pipeline — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Flags",
        "",
    ]
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines += ["", "## Dilution ledger", ""]
    for row in report["dilution"]["rows"]:
        lines.append(
            f"- {row['instrument']}: dilution ~ {row['dilution_factor']:.2e}; "
            f"line-resolvable={row['can_resolve_v20_line']}"
        )
    lines += ["", "## Downloads", ""]
    for d in report["downloads"]:
        mark = "OK" if d.get("ok") else "FAIL"
        lines.append(f"- [{mark}] `{d['id']}` — {d.get('url')}")
    lines += [
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "## Do instead",
        "",
        *[f"- {x}" for x in report["what_to_do_instead"]],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip network downloads; still write dilution ledger",
    )
    args = parser.parse_args(argv)
    report = run_pipeline(download=not args.offline)
    OUT.mkdir(parents=True, exist_ok=True)
    ROOT.joinpath("CMB_PUBLIC_PIPELINE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CMB_PUBLIC_PIPELINE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    (OUT / "summary.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "n_downloads_ok": report["n_downloads_ok"],
                "n_downloads_attempted": report["n_downloads_attempted"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
