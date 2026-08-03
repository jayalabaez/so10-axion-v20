#!/usr/bin/env python3
"""Referee next-step runner: spectrum, P=8 reconstruction, Wilson RG, thermal/strings."""

from __future__ import annotations

import json
from pathlib import Path

import heavy_light_spectrum_v20 as spectrum
import p8_spin10_reconstruction_v20 as p8
import wilson_rg_evolution_v20 as wilson
import thermal_string_v20 as thermal


def main() -> int:
    print("=== 1/4 heavy-light spectrum + lifetimes ===", flush=True)
    spec = spectrum.build_report()
    Path("heavy_light_spectrum_v20.json").write_text(json.dumps(spec, indent=2) + "\n")

    print("=== 2/4 explicit P=8 Spin(10) reconstruction ===", flush=True)
    rec = p8.build_report()
    Path("p8_spin10_reconstruction_v20.json").write_text(json.dumps(rec, indent=2) + "\n")

    print("=== 3/4 Wilson RG evolution ===", flush=True)
    wil = wilson.build_report()
    Path("wilson_rg_evolution_v20.json").write_text(json.dumps(wil, indent=2) + "\n")

    print("=== 4/4 thermal + string estimates ===", flush=True)
    th = thermal.build_report()
    Path("thermal_string_v20.json").write_text(json.dumps(th, indent=2) + "\n")

    summary = {
        "spectrum": {
            "light_families": spec["x1_block_with_extra_portals"]["n_light_chiral_families"],
            "stable_under_extra_portals": spec["light_family_count_stable"],
            "all_components_decay_at_1e-8": spec["all_components_decay_before_1s_at_1e-8"],
            "portal_floor_1s": spec["max_portal_floor_for_1s"],
        },
        "p8_reconstruction": {
            "group_ok": rec["spin10_group_factors"]["group_ok"],
            "lorentz": rec["lorentz"]["one_loop_lorentz_factor"],
            "charge_ok": rec["topology"]["charge_ok"],
            "rel_diff_vs_engine": rec["compared_to_engine_benchmark"]["relative_difference"],
        },
        "wilson": {
            "mild_C8_eff": wil["operator_running"]["NDA_O1_at_MPl_mild_shrink"][
                "C8_eff_schematic"
            ],
            "mild_safe": wil["operator_running"]["NDA_O1_at_MPl_mild_shrink"]["quality"][
                "safe_below_1e-10"
            ],
            "large_1e6_safe": wil["operator_running"]["large_Wilson_1e6_at_MPl"]["quality"][
                "safe_below_1e-10"
            ],
        },
        "thermal_string": {
            "G_mu": th["string_network"]["G_mu"],
            "restores_U1X_at_TRH_1e10": th["restoration_benchmarks"]["T_RH_1e10"][
                "restores_U1X_Phi"
            ],
            "restores_S_at_TRH_1e10": th["restoration_benchmarks"]["T_RH_1e10"][
                "restores_S_vev"
            ],
        },
        "still_external": [
            "real 36.6–37.6 GHz haloscope scan",
            "lattice (13,-3) string-network simulation",
            "complete Wilson operator-basis mixing",
            "independent diagrammatic review by another group",
        ],
        "bottom_line": (
            "Referee next checks computable in-repo are done: heavy-light "
            "spectrum/lifetimes, explicit P=8 Spin(10) factors, Wilson RG "
            "envelopes, and thermal/string estimates. The theory remains a "
            "candidate — not a dark-matter discovery."
        ),
    }
    Path("v20_referee_next_verdict.json").write_text(json.dumps(summary, indent=2) + "\n")
    md = f"""# v20 referee next steps — executed

## 1. Heavy–light spectrum and component lifetimes

- Light chiral families after 5×2 block: **{summary['spectrum']['light_families']}**
- Stable with extra portals: **{summary['spectrum']['stable_under_extra_portals']}**
- All PS/SM components decay before 1 s at $\\lambda=10^{{-8}}$: **{summary['spectrum']['all_components_decay_at_1e-8']}**
- Portal floor for $\\tau<1$ s: **{summary['spectrum']['portal_floor_1s']:.3e}**

Exact stable anomalons remain falsified under O(1) Clebsches above that floor.

## 2. Explicit P=8 Spin(10) reconstruction

- Group factors OK: **{summary['p8_reconstruction']['group_ok']}**
- Lorentz loop factor: **{summary['p8_reconstruction']['lorentz']}**
- Charge closure OK: **{summary['p8_reconstruction']['charge_ok']}**
- Relative difference vs engine unit kernel: **{summary['p8_reconstruction']['rel_diff_vs_engine']:.3e}**

## 3. Wilson RG envelopes

- Mild O(1) Planck Wilson → safe P=8 quality: **{summary['wilson']['mild_safe']}**
- Forced $|C|\\sim10^6$ at $M_{{\\rm Pl}}$ with IR growth safe?: **{summary['wilson']['large_1e6_safe']}**

## 4. Thermal + $(\\ell,n)=(13,-3)$ strings

- $G\\mu$ ≈ **{summary['thermal_string']['G_mu']:.3e}**
- $T_{{\\rm RH}}=10^{{10}}$ GeV restores $U(1)_X$? **{summary['thermal_string']['restores_U1X_at_TRH_1e10']}**
- Restores $S$? **{summary['thermal_string']['restores_S_at_TRH_1e10']}**

Lattice network simulation remains external.

## Still external

{chr(10).join('- ' + x for x in summary['still_external'])}

## Bottom line

{summary['bottom_line']}
"""
    Path("V20_REFEREE_NEXT_STEPS.md").write_text(md, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
