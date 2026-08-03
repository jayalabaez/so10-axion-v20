#!/usr/bin/env python3
"""GRAVITAS-A retargeted to the v20 37 GHz axion line.

The older gravitas_axion_v15.py used m_a~5.72 µeV → 1.382 GHz.
v20 predicts m_a~153.5 µeV → 37.11 GHz.  This module rebuilds the
compact-object search channels at the new frequency.

Channels (still theoretical / planning — not detections):
  1. Dead/isolated NS magnetosphere conversion at 37.11 GHz
  2. GRAVITAS SB1 dark companions: Doppler-modulated 37 GHz line if NS
  3. Reach estimates vs published NS-radio ALP limits (order-of-magnitude)

Requires optional sibling catalog:
  ../So10Theory/outputs/gravitas_omniscan_v14/v14_vetted_gold.csv
If missing, writes a synthetic demo target table and continues.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
C = 299792458.0
H_EV_HZ = 4.135667696e-15

# v20
MA_EV = 153.5e-6
NU0_HZ = MA_EV / H_EV_HZ  # ~37.11e9
G_V20 = 2.335e-14  # GeV^{-1}
# Reference: Foster+2020-scale ALP radio limits ~1e-11 near few–tens µeV (order)
G_NOW_ALP = 1.0e-11

DEFAULT_GOLD = (
    ROOT.parent
    / "So10Theory"
    / "outputs"
    / "gravitas_omniscan_v14"
    / "v14_vetted_gold.csv"
)
OUT = ROOT / "outputs" / "gravitas_axion_v20_37ghz"


def line_centre_ghz(rv_kms: float) -> float:
    return NU0_HZ * (1.0 - rv_kms * 1e3 / C) / 1e9


def orbital_modulation_khz(k2_kms: float) -> float:
    return NU0_HZ * (abs(k2_kms) * 1e3 / C) / 1e3


def reach_scale(g: float, g_ref: float = G_NOW_ALP, d_ref_kpc: float = 3.0) -> float:
    """Naive single-object distance reach scaling as g (flux~g^2 → d~g)."""
    return d_ref_kpc * (g / g_ref)


def load_gold(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_targets(rows: list[dict]) -> list[dict]:
    targets = []
    for r in rows:
        try:
            k1 = float(r.get("K1") or 0.0)
            rv = float(r.get("rv") or 0.0)
            dist = float(r.get("dist") or 0.0)
            period = float(r.get("period") or 0.0)
            m2 = float(r.get("M2") or r.get("M2_median") or 0.0)
        except ValueError:
            continue
        if k1 <= 0 or m2 <= 0:
            continue
        # NS-regime cut: companion mass in NS window (soft)
        ns_like = 1.0 <= m2 <= 3.0
        m1 = 1.0
        k2 = k1 * m1 / m2
        targets.append(
            {
                "source_id": r.get("source_id_full") or r.get("source_id"),
                "ra": r.get("ra"),
                "dec": r.get("dec"),
                "dist_pc": dist,
                "rv_kms": rv,
                "period_d": period,
                "K1_kms": k1,
                "M2_Msun": m2,
                "K2_kms_NS_interp": k2,
                "nu_obs_GHz": line_centre_ghz(rv),
                "dnu_orb_kHz": orbital_modulation_khz(k2),
                "ns_regime_soft": ns_like,
                "channel": "SB1_dark_companion_37GHz_Doppler",
            }
        )
    return targets


def synthetic_demo_targets() -> list[dict]:
    demo = [
        {"source_id_full": "DEMO_NS_1", "ra": "266.4", "dec": "-29.0", "dist": "8000",
         "rv": "50", "period": "10", "K1": "80", "M2": "1.4"},
        {"source_id_full": "DEMO_NS_2", "ra": "83.6", "dec": "22.0", "dist": "2000",
         "rv": "-30", "period": "5", "K1": "40", "M2": "1.6"},
    ]
    return build_targets(demo)


def population_channel() -> dict:
    n_ns = 1e9
    n_pulsar = 3.5e3
    return {
        "galactic_NS_estimate": n_ns,
        "known_pulsars": n_pulsar,
        "invisible_fraction": 1.0 - n_pulsar / n_ns,
        "line_GHz": NU0_HZ / 1e9,
        "single_object_reach_kpc_at_v20_g": reach_scale(G_V20),
        "single_object_reach_kpc_at_1e-11": reach_scale(G_NOW_ALP),
        "note": (
            "Reach scaling is schematic (Foster+2020-like). At g~2e-14 the "
            "single-object radio reach is tiny vs kpc; stacking / SKA-class "
            "collecting area is required. This is a planning estimate, not a limit."
        ),
    }


def build_report(gold_path: Path | None = None) -> dict:
    path = gold_path or DEFAULT_GOLD
    rows = load_gold(path)
    used_demo = False
    if rows:
        targets = build_targets(rows)
        source = str(path)
    else:
        targets = synthetic_demo_targets()
        used_demo = True
        source = "synthetic_demo"
    ns_targets = [t for t in targets if t["ns_regime_soft"]]
    pop = population_channel()
    return {
        "status": "PASS",
        "theory": {
            "m_a_eV": MA_EV,
            "nu0_GHz": NU0_HZ / 1e9,
            "g_agamma_GeV_inv": G_V20,
            "retarget_from": "gravitas_axion_v15 (1.382 GHz) → v20 (37.11 GHz)",
        },
        "catalog": {
            "path": source,
            "n_rows_loaded": len(rows),
            "n_targets_built": len(targets),
            "n_ns_regime_soft": len(ns_targets),
            "used_synthetic_demo": used_demo,
        },
        "population_channel": pop,
        "targets_preview": (ns_targets or targets)[:12],
        "all_targets": targets,
        "observing_ask": {
            "frequency_GHz": NU0_HZ / 1e9,
            "tune_window_GHz": [36.6, 37.6],
            "spectral_resolution_needed_kHz": "≲10 (resolve ~37 kHz halo line / orbital dnu)",
            "facilities": ["GBT Ka", "VLA Ka", "ATCA", "future ngVLA / SKA-mid extensions"],
            "smoking_gun": (
                "Line centre tracks GRAVITAS orbital ephemeris (dnu_orb) for NS companions; "
                "absent for BH companions"
            ),
        },
        "verdict": (
            "GRAVITAS ephemerides retargeted to 37.11 GHz. This prepares an "
            "astrophysical conversion search; it is not a detection. QCD-depth "
            "NS-radio reach at g~2e-14 is extremely challenging and needs "
            "large-N stacking and/or next-generation collecting area."
        ),
    }


def write_outputs(report: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = report["all_targets"]
    csv_path = OUT / "gravitas_v20_37ghz_targets.csv"
    if targets:
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(targets[0].keys()))
            writer.writeheader()
            writer.writerows(targets)
    # JSON without the bulky all_targets duplicate in summary
    summary = {k: v for k, v in report.items() if k != "all_targets"}
    summary["targets_csv"] = str(csv_path.relative_to(ROOT))
    (OUT / "gravitas_axion_v20_37ghz_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("GRAVITAS_AXION_V20_37GHZ.md").write_text(
        "\n".join(
            [
                "# GRAVITAS-A × v20 (37 GHz retarget)",
                "",
                f"**Status:** {report['status']}",
                "",
                f"- Line: **{report['theory']['nu0_GHz']:.4f} GHz** "
                f"(m_a = {report['theory']['m_a_eV']*1e6:.2f} µeV)",
                f"- Catalog: `{report['catalog']['path']}`",
                f"- Targets built: {report['catalog']['n_targets_built']} "
                f"(NS-regime soft: {report['catalog']['n_ns_regime_soft']})",
                f"- Single-object reach (schematic) at v20 g: "
                f"{report['population_channel']['single_object_reach_kpc_at_v20_g']:.4f} kpc",
                "",
                "## Smoking gun",
                "",
                report["observing_ask"]["smoking_gun"],
                "",
                f"Targets CSV: `{summary['targets_csv']}`",
                "",
                "## Verdict",
                "",
                report["verdict"],
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    report = build_report()
    write_outputs(report)
    preview = {
        "status": report["status"],
        "nu0_GHz": report["theory"]["nu0_GHz"],
        "n_targets": report["catalog"]["n_targets_built"],
        "n_ns_regime": report["catalog"]["n_ns_regime_soft"],
        "used_demo": report["catalog"]["used_synthetic_demo"],
        "reach_kpc_v20": report["population_channel"]["single_object_reach_kpc_at_v20_g"],
        "verdict": report["verdict"],
    }
    print(json.dumps(preview, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
