#!/usr/bin/env python3
"""Maximum practical NRAO TAP harvest for the 36.6–37.6 GHz window.

Runs many short project-scoped queries (the only pattern that reliably returns
before timeout) and writes a merged CSV inventory.  Also attempts ADQL filters
that prefer finer spectral_resolutions when the server accepts them.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import nrao_37ghz_archival_inventory_v20 as nrao

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nrao_37ghz_archival_inventory"
OUT.mkdir(parents=True, exist_ok=True)

# Broad but still project-scoped: Ka-capable EVLA programs often use 1* / 1[4-9]* codes.
PROJECT_PREFIXES = [
    "12B-",
    "13A-",
    "13B-",
    "14A-231",
    "14A-232",
    "14B-",
    "15A-",
    "15B-",
    "16A-",
    "16B-",
    "17A-",
    "17B-",
    "18A-",
    "18B-",
    "19A-",
    "19B-",
    "20A-",
    "20B-",
    "21A-",
    "21B-",
    "22A-",
    "22B-",
    "23A-",
    "23B-",
    "24A-",
    "24B-",
]


def query_project(prefix: str, *, top: int = 100, timeout_s: float = 40.0) -> list[dict]:
    freq = f"freq_min < {nrao.NU_MAX_HZ:.6e} AND freq_max > {nrao.NU_MIN_HZ:.6e}"
    q = f"""
SELECT TOP {top}
  instrument_name, target_name, freq_min, freq_max, t_exptime,
  obs_publisher_did, spectral_resolutions, center_frequencies,
  nums_channels, bandwidths, spw_names, s_ra, s_dec, pol_states,
  access_url, project_code, proprietary_status, configuration
FROM tap_schema.obscore
WHERE project_code LIKE '{prefix}%'
  AND (instrument_name='EVLA' OR instrument_name='VLA' OR instrument_name='GBT')
  AND {freq}
""".strip()
    text = nrao.tap_query_csv(q, timeout_s=timeout_s)
    return nrao.parse_csv_table(text)


def main() -> int:
    rows: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    log: list[dict] = []
    for prefix in PROJECT_PREFIXES:
        t0 = time.monotonic()
        entry = {"prefix": prefix, "ok": False, "n": 0, "error": None, "s": None}
        try:
            batch = query_project(prefix)
            kept = 0
            for row in batch:
                key = (
                    str(row.get("obs_publisher_did") or ""),
                    str(row.get("target_name") or ""),
                    str(row.get("freq_min") or ""),
                )
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
                kept += 1
            entry.update({"ok": True, "n": kept})
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        entry["s"] = round(time.monotonic() - t0, 2)
        log.append(entry)
        print(json.dumps(entry), flush=True)

    # Classify
    report = nrao.build_inventory(rows, source_mode="max_live_harvest", query_log=log)
    fine = [
        o
        for o in report["observations"]
        if o.get("best_channel_width_Hz") is not None
        and o["best_channel_width_Hz"] <= 200e3
    ]
    halo = [o for o in report["observations"] if o["usable_for_37kHz_halo_line"]]

    csv_path = OUT / "max_harvest_rows.csv"
    if rows:
        fields = sorted({k for r in rows for k in r})
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    out = {
        "n_rows": len(rows),
        "n_obs_classified": report["summary"]["n_overlapping_observations"],
        "n_unique_filesets": report["summary"]["n_unique_filesets"],
        "n_channel_le_200kHz": len(fine),
        "n_usable_37kHz_halo": len(halo),
        "resolution_class_counts": report["summary"]["resolution_class_counts"],
        "fine_targets": [
            {
                "target": o["target_name"],
                "project": o["project_code"],
                "ch_kHz": o["best_channel_width_Hz"] / 1e3,
                "did": o["obs_publisher_did"],
            }
            for o in fine[:50]
        ],
        "query_log": log,
    }
    (OUT / "max_harvest_summary.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    # refresh main inventory artifacts from this harvest + fixture merge
    for row in nrao.load_fixture_rows():
        key = (
            str(row.get("obs_publisher_did") or ""),
            str(row.get("target_name") or ""),
            str(row.get("freq_min") or ""),
        )
        if key not in seen:
            rows.append(row)
    full = nrao.build_inventory(rows, source_mode="max_live_harvest+fixture", query_log=log)
    ROOT.joinpath("NRAO_37GHZ_ARCHIVAL_INVENTORY_V20_VERDICT.json").write_text(
        json.dumps(full, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NRAO_37GHZ_ARCHIVAL_INVENTORY_V20.md").write_text(
        nrao.write_markdown(full), encoding="utf-8"
    )
    nrao.write_queue_csv(full, OUT / "download_reanalysis_queue.csv")
    print(json.dumps({k: out[k] for k in out if k != "query_log"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
