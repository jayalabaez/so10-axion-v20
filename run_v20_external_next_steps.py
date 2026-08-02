#!/usr/bin/env python3
"""Master runner: flavour fit + two-loop thresholds + 37 GHz haloscope forecast."""

from __future__ import annotations

import json
from pathlib import Path

import flavour_clebsch_fit_v20 as flavour
import two_loop_thresholds_v20 as thresholds
import haloscope_scan_37ghz_v20 as halo


def main() -> int:
    print("=== 1/3 broken-phase Clebsch/flavour fit ===", flush=True)
    flav = flavour.run_fit(seed=20)
    (Path(__file__).resolve().parent / "flavour_clebsch_fit_v20.json").write_text(
        json.dumps(flav, indent=2) + "\n"
    )

    print("=== 2/3 two-loop threshold RG ===", flush=True)
    thr = thresholds.build_report()
    (Path(__file__).resolve().parent / "two_loop_thresholds_v20.json").write_text(
        json.dumps(thr, indent=2) + "\n"
    )

    print("=== 3/3 37 GHz haloscope scan forecast ===", flush=True)
    scan = halo.build_report(seed=20)
    # Strip bulky spectrum arrays from the saved summary companion if present
    (Path(__file__).resolve().parent / "haloscope_scan_37ghz_v20.json").write_text(
        json.dumps(scan, indent=2) + "\n"
    )

    ss = flav["v20_single_scale_point"]
    bo = flav["best_overall"]
    summary = {
        "flavour": {
            "best_tag": bo["tag"],
            "chi2_best": bo["chi2"],
            "v_r_best_GeV": bo["v_r_GeV"],
            "chi2_v20_scale": ss["chi2"],
            "y126_max_v20": ss["y126_max"],
            "perturbative_v20": ss["perturbative_4pi"],
            "single_scale_viable": ss.get("single_scale_viable"),
            "sum_mnu_eV_v20": ss["observables"].get("sum_mnu_eV"),
            "sin2_th13_v20": ss["observables"].get("sin2_th13"),
            "finding": (
                "Classic 10+126 Clebsches fit NuFIT at both a natural "
                "v_R~1e14 GeV (best) and the exact v20 scale v_R=v_S "
                "(viable but higher chi2). Single-scale is a stressed "
                "benchmark, not a zero-knob prediction."
            ),
        },
        "thresholds": thr["comparison"],
        "threshold_regression_ok": thr["regression_anchors"],
        "haloscope": {
            "window_GHz": scan["benchmark"]["recommended_scan_GHz"],
            "nu_GHz": scan["benchmark"]["nu_central_GHz"],
            "expected_SNR": scan["forecast"]["expected_SNR"],
            "reaches_v20_coupling": scan["forecast"]["reaches_v20_coupling"],
            "mock_discovery_claimed_software_only": scan["mock_scan_with_injected_signal"][
                "discovery_claimed"
            ],
            "physical_detection": False,
            "templates": scan["templates"],
        },
        "bottom_line": (
            "External next steps are computed. The 10+126 fit works at "
            "v_R=v_S with higher chi2 than a natural ~1e14 GeV scale. "
            "Continuous thresholds reject the alpha=1/40 reset. A "
            "MADMAX-like forecast can reach the 37 GHz coupling in "
            "software — that is not a dark-matter discovery."
        ),
    }
    out = Path(__file__).resolve().parent / "v20_external_next_steps_verdict.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    md = Path(__file__).resolve().parent / "V20_EXTERNAL_NEXT_STEPS.md"
    md.write_text(
        f"""# v20 external next steps — executed

## 1. Broken-phase Clebsch / flavour fit

| Point | χ² | $v_R$ | $y_{{126,\\max}}$ | $\\sum m_\\nu$ |
|---|---:|---:|---:|---:|
| Best overall (`{bo['tag']}`) | {bo['chi2']:.3f} | {bo['v_r_GeV']:.3e} GeV | {bo['y126_max']:.3f} | {bo['observables']['sum_mnu_eV']:.4f} eV |
| Exact v20 scale $v_R=v_S$ | {ss['chi2']:.3f} | {ss['v_r_GeV']:.3e} GeV | {ss['y126_max']:.3f} | {ss['observables'].get('sum_mnu_eV', float('nan')):.4f} eV |

**Finding:** the classic $10_H+\\overline{{126}}_H$ Clebsch ansatz fits NuFIT at a
**natural** B–L scale ~$10^{{14}}$ GeV ($\\chi^2\\approx{bo['chi2']:.2f}$) and remains
**viable** at the exact v20 identification $v_R=v_S$ ($\\chi^2\\approx{ss['chi2']:.2f}$,
$\\sum m_\\nu\\approx{ss['observables'].get('sum_mnu_eV', float('nan')):.4f}$ eV,
$y_{{126,\\max}}\\approx{ss['y126_max']:.3f}$). Single-scale is therefore a
stressed benchmark, not a zero-knob prediction.

## 2. Two-loop threshold RG

- One-loop anchors: $M_I={thr['comparison']['MI_one_GeV']:.3e}$ GeV,
  $M_{{\\rm GUT}}={thr['comparison']['MGUT_one_GeV']:.3e}$ GeV (regression OK:
  {thr['regression_anchors']['MI_one_ok']}/{thr['regression_anchors']['MGUT_one_ok']}/{thr['regression_anchors']['IU_one_ok']}).
- Continuous $\\alpha^{{-1}}(v_\\Phi)\\approx{thr['comparison']['alpha_inv_vPhi_phys_two']:.2f}$
  — **not** 40.
- $\\alpha(M_{{\\rm Pl}})\\approx{thr['comparison']['alpha_MPl_phys_two']}$ (physical 210).

## 3. 36.6–37.6 GHz haloscope scan forecast

- Central frequency: **{scan['benchmark']['nu_central_GHz']:.4f} GHz**
- Forecast SNR (MADMAX-like full scale): **{scan['forecast']['expected_SNR']:.2f}**
- Reaches v20 coupling in forecast: **{scan['forecast']['reaches_v20_coupling']}**
- Templates: `{Path(scan['templates'][0]).name}`, brief markdown

**Software mock only. Not a physical detection of dark matter.**

## Bottom line

{summary['bottom_line']}
""",
        encoding="utf-8",
    )
    # Sync to parent folder
    parent = Path(__file__).resolve().parents[1]
    for name in (
        "V20_EXTERNAL_NEXT_STEPS.md",
        "v20_external_next_steps_verdict.json",
        "flavour_clebsch_fit_v20.json",
        "two_loop_thresholds_v20.json",
        "haloscope_scan_37ghz_v20.json",
    ):
        src = Path(__file__).resolve().parent / name
        if src.exists():
            (parent / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
