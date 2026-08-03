#!/usr/bin/env python3
"""Honest home-PC / public-data options for the v20 37 GHz axion target.

IMPORTANT PHYSICS (read first)
------------------------------
Axion *dark-matter* does **not** paint a free-streaming monochromatic
37 GHz line onto the CMB sky.  Conversion needs a coherent laboratory or
astrophysical magnetic field (haloscope / NS magnetosphere).

WMAP Ka (~33 GHz, ~7 GHz bandwidth) and Planck LFI 30/44 GHz (~20% bands)
are broadband continuum radiometers.  The galactic-halo axion linewidth is
~37 kHz.  Diluting a ~37 kHz line into a ~GHz band makes CMB maps
**incapable** of a dedicated v20 line search.  That common suggestion is
scientifically incorrect for this benchmark.

What *is* legitimate on a good home PC:
  A. Retarget GRAVITAS compact-object ephemerides to 37 GHz NS-conversion
  B. Simulate haloscope radiometer scans (already in-repo)
  C. Query radio-archive Ka-band metadata and build a search plan
  D. Optional SDR + Ka downconverter to stress-test DSP (not detect axions)
  E. Use Planck/WMAP only as continuum / pipeline practice — not as a kill shot

This module computes the dilution argument, lists public resources, and
writes a falsification roadmap.  It does not download multi-GB CMB maps
by default.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# v20 anchors
MA_UEV = 153.5
NU_GHZ = 37.11
NU_HZ = NU_GHZ * 1e9
G_AGG = 2.335e-14  # GeV^{-1}
LINEWIDTH_HZ = NU_HZ / 1.0e6  # Q~1e6 halo
SCAN = (36.6, 37.6)

# Literature channel bandwidths (order-of-magnitude)
WMAP_KA_BW_HZ = 7.0e9
PLANCK_LFI30_BW_HZ = 0.20 * 30e9  # ~20% goal bandwidth
PLANCK_LFI44_BW_HZ = 0.20 * 44e9


def dilution_factor(channel_bw_hz: float, line_hz: float = LINEWIDTH_HZ) -> float:
    return channel_bw_hz / line_hz


def cmb_cannot_resolve_v20_line() -> dict:
    rows = []
    for name, bw in (
        ("WMAP Ka (~33 GHz)", WMAP_KA_BW_HZ),
        ("Planck LFI 30 GHz", PLANCK_LFI30_BW_HZ),
        ("Planck LFI 44 GHz", PLANCK_LFI44_BW_HZ),
    ):
        dil = dilution_factor(bw)
        rows.append(
            {
                "instrument": name,
                "channel_bandwidth_Hz": bw,
                "axion_linewidth_Hz": LINEWIDTH_HZ,
                "dilution_factor": dil,
                "can_resolve_v20_line": dil < 10.0,
                "useful_for_v20_DM_line_search": False,
                "why": (
                    "Broadband continuum channel; line power diluted by "
                    f"~{dil:.1e}. Also: free-sky axion emission without B-field "
                    "conversion is not the DM signal."
                ),
            }
        )
    return {
        "verdict": "CMB maps cannot perform the v20 37 GHz DM line search",
        "rows": rows,
        "correct_use_of_CMB": [
            "Foreground / continuum practice for mapmaking skills",
            "Noise and beam characterization exercises",
            "NOT a substitute for MADMAX/ORGAN/ALPHA or NS-radio searches",
        ],
    }


def public_resources() -> list[dict]:
    return [
        {
            "name": "NRAO Archive (VLA / GBT)",
            "url": "https://data.nrao.edu/",
            "bands": "Ka / Q (26–50 GHz) on selected receivers",
            "home_PC_use": (
                "Search metadata for 36–38 GHz spectral setups toward GC, "
                "pulsars, or GRAVITAS targets; download reduced spectra if public"
            ),
            "can_detect_v20_DM": "Only if sensitivity + B-field conversion geometry allow; usually not yet at QCD depth",
            "priority": 1,
        },
        {
            "name": "Planck Legacy Archive",
            "url": "https://pla.esac.esa.int/",
            "bands": "LFI 30/44/70 GHz continuum",
            "home_PC_use": "Pipeline practice only; see dilution analysis",
            "can_detect_v20_DM": False,
            "priority": 3,
        },
        {
            "name": "WMAP data products (LAMBDA)",
            "url": "https://lambda.gsfc.nasa.gov/product/map/dr5/",
            "bands": "K/Ka/Q/V/W continuum",
            "home_PC_use": "Pipeline practice only; Ka brackets 37 GHz but is broadband",
            "can_detect_v20_DM": False,
            "priority": 3,
        },
        {
            "name": "ATCA / Australia Telescope Online Archive",
            "url": "https://atoa.atnf.csiro.au/",
            "bands": "selected cm/mm including Ka-ish campaigns",
            "home_PC_use": "Archive query for Ka spectral projects",
            "can_detect_v20_DM": "Unlikely for all-DM QCD depth without dedicated design",
            "priority": 2,
        },
        {
            "name": "In-repo haloscope templates",
            "url": "haloscope_37ghz_templates/",
            "bands": "36.6–37.6 GHz target brief + lineshape CSV",
            "home_PC_use": "Send to MADMAX/ORGAN/ALPHA; run software forecast",
            "can_detect_v20_DM": "Software forecast only — not a detection",
            "priority": 1,
        },
        {
            "name": "GRAVITAS gold SB1 catalog (sibling So10Theory outputs)",
            "url": "../So10Theory/outputs/gravitas_omniscan_v14/v14_vetted_gold.csv",
            "bands": "ephemerides for Doppler-tracked 37 GHz NS-conversion search",
            "home_PC_use": "Run gravitas_axion_v20_37ghz.py to retarget line centres",
            "can_detect_v20_DM": "Requires telescope time; PC prepares target list",
            "priority": 1,
        },
    ]


def home_pc_playbook() -> dict:
    return {
        "do_now_on_PC": [
            {
                "step": 1,
                "task": "Run gravitas_axion_v20_37ghz.py",
                "outcome": "37 GHz Doppler target list for NS-regime companions",
            },
            {
                "step": 2,
                "task": "Run haloscope_scan_37ghz_v20.py",
                "outcome": "Dicke SNR forecast + mock spectrum (software only)",
            },
            {
                "step": 3,
                "task": "Query NRAO/ATCA metadata for 36–38 GHz",
                "outcome": "List of public Ka spectra overlapping target directions",
            },
            {
                "step": 4,
                "task": "Optional: SDR + Ka downconverter IF chain",
                "outcome": "Real RF noise to test matched-filter DSP — not axion reach",
            },
            {
                "step": 5,
                "task": "Email MADMAX/ORGAN with templates/",
                "outcome": "Path to a real falsifier at g~2.3e-14 GeV^{-1}",
            },
        ],
        "cannot_do_at_home": [
            "Direct axion DM detection (signal << thermal noise without lab B/cryo)",
            "Competitive 37 GHz cavity/dielectric haloscope",
            "Meaningful sky-brightness axion line from a backyard dish",
            "Resolving the 37 kHz line inside WMAP/Planck broadband maps",
        ],
        "cheap_hardware_optional": {
            "SDR": "RTL-SDR / HackRF / USRP for IF DSP drills",
            "Ka_downconverter": "commercial LNBs/mixers (~26–40 GHz → IF)",
            "honesty": "Educational RF only; sensitivity gap to QCD axion is enormous",
        },
    }


def falsification_roadmap() -> dict:
    return {
        "hard_kill_all_DM_photon_benchmark": {
            "criterion": (
                f"Null scan of {SCAN[0]}–{SCAN[1]} GHz at "
                f"g_agamma <= {G_AGG:.3e} GeV^{{-1}} (local DM density assumed)"
            ),
            "who": "MADMAX / ORGAN / ALPHA-class",
            "home_PC_role": "prepare templates, forecasts, and collaboration brief",
        },
        "soft_kill_channels": [
            "NS-radio non-detection stacked over GRAVITAS targets after adequate exposure",
            "Fermion-coupling revision: provisional ERT-like numbers are conditional; full portal matching remains open",
            "Lattice (13,-3) cosmology incompatible with PTA/CMB",
        ],
        "does_not_count_as_falsification": [
            "Null result in Planck/WMAP continuum maps",
            "Mock radiometer software 'discovery'",
            "Home SDR non-detection",
        ],
    }


def build_report() -> dict:
    cmb = cmb_cannot_resolve_v20_line()
    resources = public_resources()
    play = home_pc_playbook()
    fals = falsification_roadmap()
    checks = [
        ("cmb_dilution_gt_1e4", all(r["dilution_factor"] > 1e4 for r in cmb["rows"])),
        ("no_cmb_row_claims_detection", all(not r["useful_for_v20_DM_line_search"] for r in cmb["rows"])),
        ("priority1_resources_exist", any(r["priority"] == 1 for r in resources)),
        ("linewidth_positive", LINEWIDTH_HZ > 0),
    ]
    failed = [n for n, ok in checks if not ok]
    return {
        "status": "PASS" if not failed else "FAIL",
        "n_checks": len(checks),
        "n_failed": len(failed),
        "failures": failed,
        "v20_target": {
            "m_a_ueV": MA_UEV,
            "nu_GHz": NU_GHZ,
            "linewidth_kHz": LINEWIDTH_HZ / 1e3,
            "g_agamma_GeV_inv": G_AGG,
            "scan_GHz": list(SCAN),
        },
        "cmb_mythbust": cmb,
        "public_resources": resources,
        "home_pc_playbook": play,
        "falsification_roadmap": fals,
        "verdict": (
            "Home PC work is real and useful for target lists, forecasts, and "
            "archive planning — but CMB continuum maps cannot search the v20 "
            "37 GHz DM line. The decisive path remains a lab/astrophysical "
            "B-field conversion experiment (haloscope or NS-radio)."
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Home PC + public data for the v20 37 GHz target",
        "",
        f"**Status:** {report['status']}",
        "",
        "## Straight answer",
        "",
        report["verdict"],
        "",
        "## CMB mythbust (why WMAP/Planck are not the search)",
        "",
        f"Axion linewidth ≈ {report['v20_target']['linewidth_kHz']:.2f} kHz at "
        f"{report['v20_target']['nu_GHz']} GHz.",
        "",
    ]
    for r in report["cmb_mythbust"]["rows"]:
        lines.append(
            f"- **{r['instrument']}**: dilution ≈ {r['dilution_factor']:.2e} → "
            f"{'CANNOT' if not r['can_resolve_v20_line'] else 'can'} resolve the line"
        )
    lines += [
        "",
        "## Public resources (prioritized)",
        "",
    ]
    for r in sorted(report["public_resources"], key=lambda x: x["priority"]):
        lines += [
            f"### P{r['priority']}: {r['name']}",
            "",
            f"- URL/path: `{r['url']}`",
            f"- Home-PC use: {r['home_PC_use']}",
            f"- Detect v20 DM?: `{r['can_detect_v20_DM']}`",
            "",
        ]
    lines += ["## Home-PC playbook", ""]
    for step in report["home_pc_playbook"]["do_now_on_PC"]:
        lines.append(f"{step['step']}. **{step['task']}** — {step['outcome']}")
    lines += [
        "",
        "## Cannot do at home",
        "",
        *[f"- {x}" for x in report["home_pc_playbook"]["cannot_do_at_home"]],
        "",
        "## Falsification roadmap",
        "",
        f"- Hard kill: {report['falsification_roadmap']['hard_kill_all_DM_photon_benchmark']['criterion']}",
        f"- Who: {report['falsification_roadmap']['hard_kill_all_DM_photon_benchmark']['who']}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("HOME_PUBLIC_37GHZ_SEARCH_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("HOME_PUBLIC_37GHZ_SEARCH.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "cmb_can_search_v20_line": False,
                "dilution_WMAP_Ka": report["cmb_mythbust"]["rows"][0]["dilution_factor"],
                "next_on_PC": [s["task"] for s in report["home_pc_playbook"]["do_now_on_PC"][:3]],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
