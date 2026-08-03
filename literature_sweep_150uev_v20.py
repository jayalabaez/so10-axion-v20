#!/usr/bin/env python3
"""Literature sweep: excluded vs open around the v20 ~153.5 µeV window.

This is a *triage ledger* of published / design-reach constraints near
100–200 µeV.  It does not re-analyse raw experimental data.

Verdict question answered here:
  Does existing literature already kill the v20 all-DM 37 GHz benchmark?
Answer computed below (spoiler: no — window remains OPEN).
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# v20 all-DM benchmark
V20 = {
    "m_a_ueV": 153.5,
    "m_a_unc_ueV": 2.0,
    "nu_GHz": 37.11,
    "scan_GHz": [36.6, 37.6],
    "g_agamma_GeV_inv": 2.335e-14,
    "g_unc": 0.125e-14,
    "assumption": "axion = 100% local DM at rho~0.3–0.45 GeV/cm^3",
}


def literature_entries() -> list[dict]:
    """Frozen literature anchors. Status at v20 mass/coupling only."""
    g = V20["g_agamma_GeV_inv"]
    m = V20["m_a_ueV"]

    def row(
        name: str,
        kind: str,
        m_lo: float | None,
        m_hi: float | None,
        g_lim: float | None,
        covers_mass: bool,
        excludes_v20: bool,
        status: str,
        cite: str,
        note: str,
    ) -> dict:
        return {
            "name": name,
            "kind": kind,
            "mass_window_ueV": [m_lo, m_hi] if m_lo is not None else None,
            "g_limit_GeV_inv": g_lim,
            "covers_v20_mass": covers_mass,
            "excludes_v20_coupling": excludes_v20,
            "status_at_v20": status,
            "citation": cite,
            "note": note,
            "sensitivity_ratio_g_lim_over_v20": (
                None if g_lim is None else g_lim / g
            ),
        }

    return [
        row(
            "CAST helioscope (2024 Xe)",
            "helioscope",
            0.0,
            2.0e4,  # ~0.02 eV
            5.8e-11,
            True,
            False,
            "OPEN — bound too weak",
            "Altenmüller et al., PRL 133, 221005 (2024)",
            "Solar axions; g<5.8e-11 for m_a≲0.02 eV. v20 g is ~2500× smaller.",
        ),
        row(
            "HB / globular-cluster stellar cooling",
            "astrophysics",
            0.0,
            1.0e5,
            6.6e-11,
            True,
            False,
            "OPEN — bound too weak",
            "Ayala et al., PRL 113, 191302 (2014); CAST GC revisits 2024",
            "Order 6e-11 GeV^{-1}; does not touch QCD-axion strength at 150 µeV.",
        ),
        row(
            "SN1987A / supernova photon-coupling (schematic)",
            "astrophysics",
            0.0,
            1.0e5,
            5.0e-10,
            True,
            False,
            "OPEN — bound too weak / model-dependent",
            "literature envelope used in MADMAX proto comparisons",
            "Much weaker than CAST/HB for this coupling; not a v20 killer.",
        ),
        row(
            "ORGAN Phase 1a",
            "haloscope",
            63.0,
            67.0,
            None,  # excluded ALP-cogenesis, not QCD band at that mass
            False,
            False,
            "OPEN — wrong mass window",
            "Quiskamp et al., Sci. Adv. 8, eabq3765 (2022)",
            "Excluded ALP-cogenesis near 63–67 µeV; does not cover 153.5 µeV.",
        ),
        row(
            "ORGAN Phase 1b",
            "haloscope",
            107.42,
            111.93,
            None,
            False,
            False,
            "OPEN — wrong mass window",
            "Quiskamp et al., PRL 132, 031601 (2024) [arXiv:2310.00904]",
            "Excluded ALP-cogenesis at 107–112 µeV (~26–27 GHz). v20 is ~37 GHz.",
        ),
        row(
            "MADMAX CB200 prototype",
            "haloscope",
            76.56,
            79.53,
            2.0e-11,
            False,
            False,
            "OPEN — wrong mass window",
            "MADMAX, PRL (2025) DOI 10.1103/c749-419q",
            "First dielectric-haloscope axion search; ~77–80 µeV at g~2e-11. Not 153 µeV.",
        ),
        row(
            "QUAX-aγ (~43 µeV)",
            "haloscope",
            42.0,
            44.0,
            7.7e-14,
            False,
            False,
            "OPEN — wrong mass window",
            "Alesini et al., PRD 103, 102004 (2021)",
            "Near-QCD sensitivity around 43 µeV / 10 GHz; far from 37 GHz.",
        ),
        row(
            "ADMX / HAYSTAC / CAPP (low-GHz cavities)",
            "haloscope",
            1.0,
            40.0,
            1.0e-15,  # order: DFSZ-level in pockets — schematic
            False,
            False,
            "OPEN — wrong mass window",
            "ADMX G2 / HAYSTAC / CAPP published runs (various)",
            "Mature QCD exclusions exist at few–tens of µeV, not at 150 µeV.",
        ),
        row(
            "ORGAN design envelope (future phases)",
            "haloscope_design",
            62.0,
            207.0,
            None,
            True,
            False,
            "OPEN — not yet scanned at v20 depth",
            "ORGAN programme: 15–50 GHz design band",
            "153.5 µeV sits inside design band; QCD-depth scan at 37 GHz not published.",
        ),
        row(
            "MADMAX full booster (design)",
            "haloscope_design",
            40.0,
            400.0,
            None,
            True,
            False,
            "OPEN — not yet scanned at v20 depth",
            "MADMAX design / DESY programme",
            "Design aims post-inflationary ~100 µeV QCD axions; 37 GHz is on-roadmap.",
        ),
        row(
            "ALPHA / dielectric broadband (design)",
            "haloscope_design",
            80.0,
            200.0,
            None,
            True,
            False,
            "OPEN — not yet scanned at v20 depth",
            "ALPHA collaboration proposals",
            "Later stages advertised around 80–200 µeV; no v20 exclusion yet.",
        ),
    ]


def classify(entries: list[dict]) -> dict:
    excluded = [e for e in entries if e["excludes_v20_coupling"]]
    mass_covered_but_weak = [
        e
        for e in entries
        if e["covers_v20_mass"] and e["kind"] in ("helioscope", "astrophysics")
        and not e["excludes_v20_coupling"]
    ]
    wrong_mass = [
        e for e in entries if e["kind"] == "haloscope" and not e["covers_v20_mass"]
    ]
    design_open = [e for e in entries if e["kind"] == "haloscope_design"]

    theory_fails_from_literature = len(excluded) > 0
    return {
        "theory_fails_from_published_bounds": theory_fails_from_literature,
        "n_entries": len(entries),
        "n_excluding_v20": len(excluded),
        "buckets": {
            "EXCLUDED_by_literature": [e["name"] for e in excluded],
            "OPEN_mass_covered_but_g_too_weak": [e["name"] for e in mass_covered_but_weak],
            "OPEN_published_haloscope_wrong_mass": [e["name"] for e in wrong_mass],
            "OPEN_design_reach_not_yet_done": [e["name"] for e in design_open],
        },
        "one_sentence": (
            "FAIL — literature already excludes the v20 coupling at 153.5 µeV."
            if theory_fails_from_literature
            else (
                "DOES NOT FAIL — no published bound excludes the v20 all-DM "
                "benchmark at 153.5 µeV / 37 GHz; the window is experimentally OPEN."
            )
        ),
    }


def build_report() -> dict:
    entries = literature_entries()
    cls = classify(entries)
    return {
        "status": "PASS",
        "v20_benchmark": V20,
        "entries": entries,
        "classification": cls,
        "soft_stresses_not_literature_exclusion": [
            "exact v_R=v_S flavour fit stressed vs natural ~1e14 GeV",
            "continuous RG rejects old alpha_10(v_Phi)=1/40 reset",
            "unit-coefficient loop numbers are diagnostics, not predictions",
            "lattice (13,-3) string network not simulated",
        ],
        "next_physical_step": {
            "action": "Request / collaborate on a real 36.6–37.6 GHz scan",
            "targets": ["ORGAN", "MADMAX", "ALPHA-class"],
            "deliverables_in_repo": [
                "haloscope_37ghz_templates/v20_haloscope_target_brief.md",
                "haloscope_37ghz_templates/v20_axion_lineshape_37GHz.csv",
            ],
            "what_would_fail_the_theory": (
                "A null result at g_agamma ≲ 2.3e-14 GeV^{-1} over 36.6–37.6 GHz "
                "kills the all-DM benchmark (not necessarily every diluted/subcomponent scenario)."
            ),
        },
        "verdict": cls["one_sentence"],
    }


def write_markdown(report: dict) -> str:
    cls = report["classification"]
    lines = [
        "# Literature sweep — ~150 µeV axion bounds (v20)",
        "",
        f"**Does the theory fail from published bounds?** {cls['one_sentence']}",
        "",
        "## v20 target",
        "",
        f"- m_a = {V20['m_a_ueV']} ± {V20['m_a_unc_ueV']} µeV",
        f"- nu ≈ {V20['nu_GHz']} GHz (scan {V20['scan_GHz'][0]}–{V20['scan_GHz'][1]} GHz)",
        f"- g_agamma = {V20['g_agamma_GeV_inv']:.3e} GeV^-1 (all-DM benchmark)",
        "",
        "## Bucket summary",
        "",
    ]
    for key, names in cls["buckets"].items():
        lines.append(f"### {key}")
        lines.append("")
        if not names:
            lines.append("- *(none)*")
        else:
            for n in names:
                lines.append(f"- {n}")
        lines.append("")

    lines += ["## Entry-by-entry ledger", ""]
    for e in report["entries"]:
        ratio = e["sensitivity_ratio_g_lim_over_v20"]
        rtxt = f"{ratio:.1e}× weaker than needed" if ratio else "n/a"
        mw = e["mass_window_ueV"]
        mtxt = f"{mw[0]}–{mw[1]} µeV" if mw else "n/a"
        lines += [
            f"### {e['name']}",
            "",
            f"- Kind: `{e['kind']}`",
            f"- Mass window: {mtxt}",
            f"- Status at v20: **{e['status_at_v20']}**",
            f"- g_lim / g_v20: {rtxt}",
            f"- Cite: {e['citation']}",
            f"- Note: {e['note']}",
            "",
        ]

    lines += [
        "## Soft stresses (not literature exclusion)",
        "",
        *[f"- {x}" for x in report["soft_stresses_not_literature_exclusion"]],
        "",
        "## Next physical step",
        "",
        f"- **Action:** {report['next_physical_step']['action']}",
        f"- **Targets:** {', '.join(report['next_physical_step']['targets'])}",
        f"- **Kill criterion:** {report['next_physical_step']['what_would_fail_the_theory']}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("LITERATURE_SWEEP_150UEV_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LITERATURE_SWEEP_150UEV.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "theory_fails_from_published_bounds": report["classification"][
                    "theory_fails_from_published_bounds"
                ],
                "one_sentence": report["classification"]["one_sentence"],
                "buckets": {k: len(v) for k, v in report["classification"]["buckets"].items()},
                "next_step": report["next_physical_step"]["action"],
                "targets": report["next_physical_step"]["targets"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
