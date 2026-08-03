#!/usr/bin/env python3
"""Public-data / indirect multi-channel audit for v20.

Brainstorm executed as a machine-readable matrix + runnable ledger.

Honesty first
-------------
Public data can **constrain**, **stress**, or **support consistency** of the
candidate theory.  It cannot *prove* that nature realizes SO(10)×Z17 or that
the 37 GHz axion is dark matter.  A positive lab/astro conversion detection
would be strong evidence; absence of exclusion is not proof.

This module inventories every channel we can touch with Python + public
anchors on a home PC, scores each as:
  RUNNABLE_NOW | ARCHIVE_QUERY | COLLAB_ONLY | MYTH / NOT_APPLICABLE
and executes the RUNNABLE_NOW physics checks.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import fermion_couplings_150uev_v20 as fermion
import gravitas_axion_v20_37ghz as grav
import home_public_37ghz_search_v20 as home
import literature_sweep_150uev_v20 as lit
import thermal_string_v20 as thermal
import two_loop_thresholds_v20 as thr


ROOT = Path(__file__).resolve().parent

VS = 6.313855e11
FA = VS / 17.0
MA_UEV = 153.5
MA_EV = MA_UEV * 1e-6
NU_GHZ = 37.11
G_AGG = 2.335e-14
MPL = 2.435e18
MSUN_GEV = 1.1157e57  # approximate GeV mass-energy of Sun (M c^2)


# ---------------------------------------------------------------------------
# Brainstorm matrix
# ---------------------------------------------------------------------------
def brainstorm_matrix() -> list[dict]:
    """Everything imaginable with public data / home PC for this setup."""
    return [
        {
            "id": "A_haloscope_templates",
            "channel": "Lab haloscope target brief + lineshape",
            "public_data": "in-repo templates (not a detection)",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "forecast / collaboration ask",
            "python": "haloscope_scan_37ghz_v20.py",
        },
        {
            "id": "B_literature_photon",
            "channel": "Published photon-coupling exclusions near 150 µeV",
            "public_data": "CAST, HB, ORGAN, MADMAX papers",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "window still open?",
            "python": "literature_sweep_150uev_v20.py",
        },
        {
            "id": "C_fermion_stellar_SN",
            "channel": "Aligned C_f(tan beta) benchmark vs TRGB & SN",
            "public_data": "published g_ae, correlated SN1987A, universal SN f_a bound",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "aligned benchmark only; full portal/flavour matching open",
            "python": "fermion_couplings_150uev_v20.py",
        },
        {
            "id": "D_flavour_nufit",
            "channel": "10+126 Clebsch fit vs NuFIT-6 public neutrino data",
            "public_data": "NuFIT-6.0 tables (frozen in data/)",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "seesaw / v_R stress",
            "python": "flavour_clebsch_fit_v20.py",
        },
        {
            "id": "E_proton_decay",
            "channel": "GUT-scale proton lifetime vs SK / Hyper-K public limits",
            "public_data": "Super-Kamiokande / Hyper-K projections",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "unification tension",
            "python": "so10_axion_v17_engine.py / next_physics_analysis",
        },
        {
            "id": "F_pta_strings",
            "channel": "Analytic Gμ of (13,-3) sector vs NANOGrav/CMB string anchors",
            "public_data": "NANOGrav 15yr new-physics papers; CMB Gμ≲1e-7",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "cosmic-string sector not grossly excluded",
            "python": "thermal_string_v20.py + this audit",
        },
        {
            "id": "G_isocurvature",
            "channel": "Pre-inflationary misalignment H_I vs Planck isocurvature",
            "public_data": "Planck isocurvature / r bounds (schematic)",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "all-DM pre-inflation viability window",
            "python": "next_physics_analysis / home cosmology",
        },
        {
            "id": "H_gravitas_doppler",
            "channel": "GRAVITAS SB1 ephemerides → 37 GHz Doppler target list",
            "public_data": "Gaia DR3 SB1 / GRAVITAS gold catalog",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "prepares NS-vs-BH radio ask",
            "python": "gravitas_axion_v20_37ghz.py",
        },
        {
            "id": "I_cmb_myth",
            "channel": "WMAP/Planck continuum as 37 kHz line search",
            "public_data": "LAMBDA / PLA maps",
            "status": "MYTH / NOT_APPLICABLE",
            "proves": False,
            "tests": "dilution ~1e5; free-sky emission wrong physics",
            "python": "home_public_37ghz_search_v20.py",
        },
        {
            "id": "J_bh_superradiance",
            "channel": "BH / PBH gravitational-atom window at m_a=153.5 µeV",
            "public_data": "stellar BH catalogs; PBH microlensing bounds",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "whether stellar BHs are in the cloud window (usually no)",
            "python": "this audit",
        },
        {
            "id": "K_nrao_archive",
            "channel": "NRAO/GBT/VLA Ka-band spectral archive toward targets",
            "public_data": "https://data.nrao.edu/",
            "status": "ARCHIVE_QUERY",
            "proves": False,
            "tests": "existing 36–38 GHz spectra near GRAVITAS / GC",
            "python": "manual/API query; metadata planner in home package",
        },
        {
            "id": "L_atca_archive",
            "channel": "ATCA Ka campaigns",
            "public_data": "https://atoa.atnf.csiro.au/",
            "status": "ARCHIVE_QUERY",
            "proves": False,
            "tests": "southern-sky Ka spectra",
            "python": "manual query",
        },
        {
            "id": "M_pulsar_radio_limits",
            "channel": "Published NS-magnetosphere axion-radio limits (Foster+ etc.)",
            "public_data": "GBT/MeerKAT ALP radio papers",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "order-of-magnitude reach vs g_v20",
            "python": "gravitas_axion_v20_37ghz reach scaling",
        },
        {
            "id": "N_xray_cluster_ALP",
            "channel": "X-ray / cluster magnetic conversion (Chandra, XMM)",
            "public_data": "HEASARC",
            "status": "NOT_APPLICABLE",
            "proves": False,
            "tests": "optimized for much lighter ALPs / different g; not 153 µeV DM line",
            "python": None,
        },
        {
            "id": "O_collider_beamdump",
            "channel": "Beam-dump / collider ALP searches",
            "public_data": "NA64, FASER, Belle-II, LHC",
            "status": "NOT_APPLICABLE",
            "proves": False,
            "tests": "wrong mass/coupling regime for QCD axion at f_a~3e10 GeV",
            "python": None,
        },
        {
            "id": "P_fifth_force_CASPEr",
            "channel": "NMR / fifth-force / CASPEr-style nucleon EDM",
            "public_data": "published CASPEr/ARIADNE limits",
            "status": "COLLAB_ONLY",
            "proves": False,
            "tests": "nucleon couplings; complementary but not 37 GHz photon",
            "python": "compare g_ap envelope only",
        },
        {
            "id": "Q_sdr_home_rf",
            "channel": "Home SDR + Ka downconverter DSP drills",
            "public_data": "live RF noise (not sky axions)",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "matched-filter pipeline hygiene",
            "python": "haloscope mock spectrum as software twin",
        },
        {
            "id": "R_plasma_resonance",
            "channel": "Resonant axion-photon conversion in galactic plasmas",
            "public_data": "NE2001 / YMW16 electron-density models",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "whether n_e can hit ω_p≈37 GHz anywhere plausible",
            "python": "this audit",
        },
        {
            "id": "S_minicluster_transits",
            "channel": "Axion minicluster × NS radio flares",
            "public_data": "transient radio surveys (ASKAP, VLA)",
            "status": "COLLAB_ONLY",
            "proves": False,
            "tests": "rate estimates only on home PC",
            "python": "order-of-magnitude placeholder",
        },
        {
            "id": "T_continuous_rg",
            "channel": "Gauge coupling continuous RG vs public α(MZ)",
            "public_data": "PDGish α_s, α1, α2 (frozen)",
            "status": "RUNNABLE_NOW",
            "proves": False,
            "tests": "rejects α10(vΦ)=1/40 reset",
            "python": "two_loop_thresholds_v20.py",
        },
    ]


# ---------------------------------------------------------------------------
# Runnable physics checks
# ---------------------------------------------------------------------------
def bh_superradiance_window() -> dict:
    """Gravitational-atom BH mass for m_a (order-of-magnitude).

    Rough: M ≈ α * M_Pl^2 / m_a  (natural units), with α~0.1–0.5.
    """
    # m_a in GeV
    m_gev = MA_EV * 1e-9
    rows = []
    for alpha in (0.1, 0.4, 1.0):
        m_bh_gev = alpha * (MPL**2) / m_gev
        m_bh_msun = m_bh_gev / MSUN_GEV
        rows.append(
            {
                "alpha": alpha,
                "M_BH_Msun": m_bh_msun,
                "stellar_BH_window_3_to_100": 3.0 <= m_bh_msun <= 100.0,
                "asteroid_PBH_ish": m_bh_msun < 1e-5,
            }
        )
    any_stellar = any(r["stellar_BH_window_3_to_100"] for r in rows)
    return {
        "m_a_eV": MA_EV,
        "rows": rows,
        "stellar_BH_superradiance_relevant": any_stellar,
        "verdict": (
            "Stellar-mass BH clouds are NOT in the v20 window; the cloud mass "
            "sits at asteroid-scale PBHs. Public stellar-BH catalogs therefore "
            "do not probe this mass. PBH microlensing is the relevant public path."
        ),
    }


def plasma_resonance() -> dict:
    """ω_p / 2π ≈ 9 kHz * sqrt(n_e / cm^-3). Set equal to 37.11 GHz."""
    # f_p (Hz) ≈ 8980 * sqrt(n_e) for n_e in cm^-3
    f_target = NU_GHZ * 1e9
    n_e = (f_target / 8980.0) ** 2
    return {
        "target_GHz": NU_GHZ,
        "n_e_for_resonance_cm3": n_e,
        "typical_warm_ISM_cm3": 0.1,
        "typical_HII_cm3": 1e2,
        "solar_corona_cm3": 1e8,
        "resonates_in_typical_ISM": n_e < 1e3,
        "verdict": (
            f"Resonance at 37 GHz needs n_e ~ {n_e:.2e} cm^-3 — far above "
            "warm ISM/HII. Not a galactic-propagation smoking gun for v20."
        ),
    }


def pta_string_ledger() -> dict:
    strings = thermal.string_tension_and_gw()
    gmu = strings["G_mu"]
    return {
        "v20_Gmu": gmu,
        "nanograv_stable_NG_ballpark_upper": 1e-10,
        "cmb_Gmu_upper": 1e-7,
        "below_nanograv_ballpark": gmu < 1e-10,
        "below_cmb": gmu < 1e-7,
        "caveat": (
            "NANOGrav bounds depend on loop fraction f_NG and network model; "
            "(13,-3) holonomy still needs dedicated simulation."
        ),
        "verdict": (
            f"Analytic Gμ={gmu:.3e} sits below the oft-quoted 1e-10 NG ballpark "
            "and far below CMB 1e-7 — not excluded by frozen PTA anchors, "
            "but not proven either."
        ),
    }


def proton_anchor() -> dict:
    one = thr.build_report()["one_loop"]
    m_gut = one["M_GUT_GeV"]
    a_inv = one["alpha_inv_GUT"]
    # reuse formula from next_physics (inline)
    m_p, m_pi, v_ud = 0.9383, 0.1350, 0.9737
    alpha = 1.0 / a_inv
    kin = (1.0 - (m_pi / m_p) ** 2) ** 2
    c = 4.0 * math.pi * alpha / m_gut**2
    flav = 1.0 + (1.0 + v_ud**2) ** 2
    gamma = m_p / (32.0 * math.pi) * kin * c**2 * (2.5**2) * (0.11**2) * flav
    hbar = 6.582119569e-25
    tau = hbar / gamma / 3.156e7
    return {
        "M_GUT_GeV": m_gut,
        "tau_p_benchmark_yr": tau,
        "SK_limit_yr": 2.4e34,
        "passes_SK_central": tau > 2.4e34,
        "verdict": "Central M_GUT lifetime above SK; full MC still has ~35% SK-excluded fraction in v17.",
    }


def build_report() -> dict:
    matrix = brainstorm_matrix()
    lit_rep = lit.build_report()
    ferm = fermion.build_report()
    grav_rep = grav.build_report()
    cmb = home.cmb_cannot_resolve_v20_line()
    bh = bh_superradiance_window()
    plasma = plasma_resonance()
    pta = pta_string_ledger()
    prot = proton_anchor()

    runnable = [m for m in matrix if m["status"] == "RUNNABLE_NOW"]
    archive = [m for m in matrix if m["status"] == "ARCHIVE_QUERY"]
    myth = [m for m in matrix if m["status"] == "MYTH / NOT_APPLICABLE"]
    collab = [m for m in matrix if m["status"] == "COLLAB_ONLY"]
    na = [m for m in matrix if m["status"] == "NOT_APPLICABLE"]

    checks = [
        ("literature_open", not lit_rep["classification"]["theory_fails_from_published_bounds"]),
        (
            "fermion_aligned_beta_envelope_trgb",
            ferm["aligned_bound_checks_only"]["TRGB_safe_central"],
        ),
        (
            "fermion_aligned_beta_envelope_sn",
            ferm["aligned_bound_checks_only"]["SN1987A_safe_central"],
        ),
        (
            "fermion_physical_portal_dependence_detected",
            ferm["portal_current_status"]["scan"][
                "passes_fail_closed_detection"
            ],
        ),
        (
            "fermion_full_model_pass_still_open",
            ferm["aligned_bound_checks_only"]["full_model_pass"] is None,
        ),
        ("pta_gmu_below_1e-10", pta["below_nanograv_ballpark"]),
        ("cmb_not_useful", all(not r["useful_for_v20_DM_line_search"] for r in cmb["rows"])),
        ("stellar_BH_SR_irrelevant", not bh["stellar_BH_superradiance_relevant"]),
        ("plasma_not_ISM", not plasma["resonates_in_typical_ISM"]),
        ("gravitas_targets_built", grav_rep["catalog"]["n_targets_built"] > 0),
        ("proton_central_above_SK", prot["passes_SK_central"]),
    ]
    failed = [n for n, ok in checks if not ok]

    scorecard = {
        "channels_inventoried": len(matrix),
        "runnable_now": len(runnable),
        "archive_query": len(archive),
        "collab_only": len(collab),
        "myth_or_na": len(myth) + len(na),
        "any_channel_proves_theory": False,
        "hard_exclusion_from_this_public_ledger": False,
    }

    return {
        "status": "PASS" if not failed else "FAIL",
        "n_checks": len(checks),
        "n_failed": len(failed),
        "failures": failed,
        "honesty": (
            "No public-data channel in this matrix *proves* the theory. "
            "They leave the photon benchmark open, while full fermion matching "
            "and the corrected single-scale flavour sector remain unresolved."
        ),
        "brainstorm_matrix": matrix,
        "scorecard": scorecard,
        "executed": {
            "literature_photon": {
                "fails": lit_rep["classification"]["theory_fails_from_published_bounds"],
                "sentence": lit_rep["classification"]["one_sentence"],
            },
            "fermion": {
                "status": ferm["status"],
                "portal_gap_closed": False,
                "portal_dependence_detected": ferm["portal_current_status"][
                    "scan"
                ]["passes_fail_closed_detection"],
                "aligned_TRGB_pass": ferm["aligned_bound_checks_only"][
                    "TRGB_safe_central"
                ],
                "aligned_SN_pass": ferm["aligned_bound_checks_only"][
                    "SN1987A_safe_central"
                ],
                "full_model_pass": ferm["aligned_bound_checks_only"][
                    "full_model_pass"
                ],
                "verdict": ferm["verdict"],
            },
            "pta_strings": pta,
            "proton": prot,
            "bh_superradiance": bh,
            "plasma_resonance": plasma,
            "cmb_mythbust": {"verdict": cmb["verdict"], "dilution_WMAP_Ka": cmb["rows"][0]["dilution_factor"]},
            "gravitas": {
                "n_targets": grav_rep["catalog"]["n_targets_built"],
                "reach_kpc_v20": grav_rep["population_channel"]["single_object_reach_kpc_at_v20_g"],
            },
        },
        "home_pc_priority_queue": [
            "Keep literature + fermion + PTA ledgers current",
            "Query NRAO/ATCA for 36–38 GHz spectra on GRAVITAS sightlines",
            "Ship haloscope templates to MADMAX/ORGAN/ALPHA",
            "Optional: SDR DSP twin using mock radiometer spectra",
            "Do NOT claim CMB map residuals as axion proof/falsification",
        ],
        "verdict": (
            f"Inventoried {len(matrix)} channels; {len(runnable)} runnable now on this "
            "Python stack. The 37 GHz photon benchmark is not excluded, but the "
            "complete phenomenological model is not validated. Decisive evidence "
            "still requires B-field conversion and the open theory matching."
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Public-data / indirect multi-channel brainstorm — v20",
        "",
        f"**Status:** {report['status']} — {report['n_checks']} checks, {report['n_failed']} failed",
        "",
        "## Honesty",
        "",
        report["honesty"],
        "",
        f"**Scorecard:** {report['scorecard']['runnable_now']} runnable now / "
        f"{report['scorecard']['channels_inventoried']} inventoried; "
        f"proves theory? `{report['scorecard']['any_channel_proves_theory']}`",
        "",
        "## Brainstorm matrix",
        "",
        "| ID | Channel | Status | Proves? |",
        "|---|---|---|---|",
    ]
    for m in report["brainstorm_matrix"]:
        lines.append(
            f"| `{m['id']}` | {m['channel']} | {m['status']} | {m['proves']} |"
        )
    ex = report["executed"]
    lines += [
        "",
        "## Executed ledger (this run)",
        "",
        f"- Photon literature: {ex['literature_photon']['sentence']}",
        f"- Fermion status: `{ex['fermion']['status']}`",
        f"- Renormalizable portal gap closed: {ex['fermion']['portal_gap_closed']}",
        f"- Physical portal dependence detected: {ex['fermion']['portal_dependence_detected']}",
        f"- Aligned TRGB/SN central benchmark: "
        f"{ex['fermion']['aligned_TRGB_pass']}/{ex['fermion']['aligned_SN_pass']}",
        f"- Full-model stellar/SN pass: {ex['fermion']['full_model_pass']}",
        f"- PTA/strings: {ex['pta_strings']['verdict']}",
        f"- Proton central: τ_p={ex['proton']['tau_p_benchmark_yr']:.2e} yr "
        f"(above SK={ex['proton']['passes_SK_central']})",
        f"- BH SR: {ex['bh_superradiance']['verdict']}",
        f"- Plasma: {ex['plasma_resonance']['verdict']}",
        f"- CMB: {ex['cmb_mythbust']['verdict']}",
        f"- GRAVITAS targets: {ex['gravitas']['n_targets']} "
        f"(reach~{ex['gravitas']['reach_kpc_v20']:.4f} kpc)",
        "",
        "## Home-PC priority queue",
        "",
        *[f"{i+1}. {x}" for i, x in enumerate(report["home_pc_priority_queue"])],
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    print("=== PUBLIC-DATA / INDIRECT MULTI-CHANNEL AUDIT ===", flush=True)
    report = build_report()
    ROOT.joinpath("PUBLIC_DATA_INDIRECT_AUDIT_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PUBLIC_DATA_INDIRECT_AUDIT.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_channels": report["scorecard"]["channels_inventoried"],
                "runnable_now": report["scorecard"]["runnable_now"],
                "proves_theory": report["scorecard"]["any_channel_proves_theory"],
                "failures": report["failures"],
                "priority_queue": report["home_pc_priority_queue"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
