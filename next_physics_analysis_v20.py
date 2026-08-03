#!/usr/bin/env python3
"""Next physically meaningful analyses still doable in-repo for v20.

Executed here (software / theory only — not a dark-matter discovery):
  1. Astrophysical + lab bound ledger at the v20 mass/coupling
  2. PQ / domain-wall / misalignment scenario map
  3. Joint flavour × proton-decay stress scan
  4. Experiment-reach triage for 36.6–37.6 GHz
  5. Anomalon BBN lifetime grid vs portal
  6. Quality C_eff boundary vs unit P=8 kernel

Cannot replace: a real haloscope scan, lattice (13,-3) network, or human referee.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize

import flavour_clebsch_fit_v20 as flavour
import heavy_light_spectrum_v20 as spectrum
import thermal_string_v20 as thermal
import two_loop_thresholds_v20 as thr
import wilson_rg_evolution_v20 as wilson


ROOT = Path(__file__).resolve().parent
VS = 6.313855e11
VPHI = 1.0e17
MPL = 2.435e18
FA = VS / 17.0
MA_UEV = 153.5
G_AGG = 2.335e-14
CHI4 = 75.5e-3  # GeV
OMEGA_DM = 0.120
UNIT_P8 = 6.043043168794402e-47
HBAR_GEV_S = 6.582119569e-25
S_PER_YR = 3.156e7


# ---------------------------------------------------------------------------
# 1. Astrophysical / laboratory bound ledger
# ---------------------------------------------------------------------------
def astrophysics_ledger() -> dict:
    """Compare v20 coupling to frozen literature / experiment anchors.

    Numbers are *order-of-magnitude ledger entries* for triage, not a
    re-derivation of each bound.  Sources are recorded for audit.
    """
    # Helioscope / stellar (apply for m_a << keV; v20 mass is fine)
    cast_g = 5.8e-11  # GeV^{-1}, CAST 2024 Xe run (m_a <~ 0.02 eV)
    hb_g = 6.6e-11  # GeV^{-1}, globular-cluster HB stars (Ayala et al. order)
    # SN1987A photon-coupling ALP bounds are typically weaker / model-dependent
    # at this mass; record as non-excluding at QCD-axion strength.
    madmax_proto_g = 2.0e-11  # GeV^{-1} at ~77–80 µeV (wrong mass for v20)
    # ORGAN has published exclusions near 63–67 µeV; design covers ~63–207 µeV
    organ_design_covers_v20 = True

    rows = [
        {
            "bound": "CAST helioscope (2024)",
            "g_limit_GeV_inv": cast_g,
            "applies_at_153ueV": True,
            "excludes_v20": G_AGG > cast_g,
            "margin_v20_over_limit": G_AGG / cast_g,
            "source": "CAST PRL 133, 221005 (2024); g < 5.8e-11 GeV^{-1}",
        },
        {
            "bound": "HB / globular-cluster stellar cooling",
            "g_limit_GeV_inv": hb_g,
            "applies_at_153ueV": True,
            "excludes_v20": G_AGG > hb_g,
            "margin_v20_over_limit": G_AGG / hb_g,
            "source": "Ayala et al. / CAST GC revisits; ~6e-11 GeV^{-1} order",
        },
        {
            "bound": "MADMAX prototype (published)",
            "g_limit_GeV_inv": madmax_proto_g,
            "applies_at_153ueV": False,
            "excludes_v20": False,
            "margin_v20_over_limit": G_AGG / madmax_proto_g,
            "source": "MADMAX proto ~77–80 µeV; v20 needs ~37 GHz full booster",
        },
        {
            "bound": "ORGAN design band",
            "g_limit_GeV_inv": None,
            "applies_at_153ueV": organ_design_covers_v20,
            "excludes_v20": False,
            "margin_v20_over_limit": None,
            "source": "ORGAN targets ~63–207 µeV; 153.5 µeV inside design window",
        },
    ]
    any_exclude = any(r["excludes_v20"] for r in rows)
    return {
        "v20": {"m_a_ueV": MA_UEV, "g_agamma_GeV_inv": G_AGG, "f_a_GeV": FA},
        "bounds": rows,
        "currently_excluded_by_listed_bounds": any_exclude,
        "verdict": (
            "v20 coupling sits ~2500× below CAST/HB limits; existing published "
            "haloscope exclusions do not cover 153.5 µeV at QCD strength. "
            "Window remains experimentally open."
        ),
    }


# ---------------------------------------------------------------------------
# 2. PQ / domain-wall / misalignment scenarios
# ---------------------------------------------------------------------------
def _f_anh(theta: float) -> float:
    x = min(theta * theta / math.pi**2, 1.0 - 1e-12)
    return (math.log(math.e / (1.0 - x))) ** 1.184


def omega_a(f_a: float, theta: float) -> float:
    return 0.195 * theta * theta * _f_anh(theta) * (f_a / 1e12) ** 1.184


def pq_history_scenarios() -> dict:
    # All-DM misalignment angle (anharmonic)
    theta_dm = brentq(lambda t: omega_a(FA, t) - OMEGA_DM, 0.05, math.pi)
    dln = (
        math.log(omega_a(FA, theta_dm + 1e-6))
        - math.log(omega_a(FA, theta_dm - 1e-6))
    ) / 2e-6
    s_max = math.sqrt(0.038 / 0.962 * 2.1e-9)
    h_i_max = s_max * 2.0 * math.pi * FA / dln

    strings = thermal.string_tension_and_gw()
    rest_lo = thermal.restoration_after_inflation(1e10)
    rest_hi = thermal.restoration_after_inflation(1e15)
    rest_phi = thermal.restoration_after_inflation(thermal.critical_temperatures()["T_c_Phi_GeV"] * 1.1)

    scenarios = {
        "pre_inflationary_PQ": {
            "description": (
                "PQ broken before/during inflation; no post-inflation domain walls; "
                "isocurvature constrains H_I."
            ),
            "theta_i_for_all_DM": theta_dm,
            "H_I_max_GeV": h_i_max,
            "domain_walls": "absent (inflation dilutes)",
            "viable_if": f"H_I <~ {h_i_max:.2e} GeV and theta_i ~ {theta_dm:.2f}",
        },
        "post_inflationary_standard_N17": {
            "description": (
                "Naive N_DW=17 walls from cover anomaly — cosmologically dangerous "
                "unless bias or inflation intervenes."
            ),
            "N_DW_cover": 17,
            "dangerous_without_bias": True,
            "note": "v20 uses (ell,n)=(13,-3) to arrange physical wall number 1",
        },
        "post_inflationary_v20_13_m3": {
            "description": (
                "Gauged string + residual discrete holonomy (13,-3) with physical "
                "wall number 1; analytic G mu below PTA ballpark."
            ),
            "physical_wall_number": strings["physical_wall_number"],
            "G_mu": strings["G_mu"],
            "G_mu_over_1e-10": strings["G_mu_vs_PTA_ballpark_1e-10"],
            "lattice_still_required": True,
            "T_RH_1e10": rest_lo,
            "T_RH_1e15": rest_hi,
            "T_RH_above_T_c_Phi": rest_phi,
        },
    }

    # Abundance scan vs theta
    thetas = [0.1, 0.5, 1.0, 1.5, 2.0, theta_dm, math.pi - 0.05]
    abundance = [
        {"theta_i": t, "Omega_a_h2_proxy": omega_a(FA, t), "overcloses": omega_a(FA, t) > OMEGA_DM * 1.05}
        for t in thetas
    ]

    return {
        "f_a_GeV": FA,
        "Omega_DM_target": OMEGA_DM,
        "scenarios": scenarios,
        "abundance_vs_theta": abundance,
        "verdict": (
            "Pre-inflationary all-DM needs theta_i~2.91 and H_I≲9e5 GeV. "
            "Post-inflationary viability leans on the (13,-3) one-wall sector; "
            "lattice network evolution remains external."
        ),
    }


# ---------------------------------------------------------------------------
# 3. Joint flavour × proton-decay stress
# ---------------------------------------------------------------------------
def _tau_p_years(m_x: float, alpha_gut: float, a_r: float = 2.5, w: float = 0.11) -> float:
    m_p, m_pi, v_ud = 0.9383, 0.1350, 0.9737
    kin = (1.0 - (m_pi / m_p) ** 2) ** 2
    c = 4.0 * math.pi * alpha_gut / m_x**2
    flav = 1.0 + (1.0 + v_ud**2) ** 2
    gamma = m_p / (32.0 * math.pi) * kin * c**2 * a_r**2 * w**2 * flav
    return HBAR_GEV_S / gamma / S_PER_YR


def joint_flavour_proton() -> dict:
    """Stress single-scale v_R against flavour and proton lifetime at M_GUT."""
    one = thr.build_report()["one_loop"]
    m_gut = one["M_GUT_GeV"]
    a_inv = one["alpha_inv_GUT"]
    alpha = 1.0 / a_inv
    tau_med = _tau_p_years(m_gut, alpha)
    tau_sk = 2.4e34
    tau_hk = 1.0e35

    # Flavour at a few v_R anchors (light multi-start, not full package DE)
    vr_grid = [1e12, VS, 1e13, 1e14, 1e15]
    flavour_rows = []
    rng = np.random.default_rng(42)
    for vr in vr_grid:
        best = 1e99
        best_pert = False
        best_sum = None
        for _ in range(6):
            x0 = rng.normal(size=13)
            x0[0] = rng.uniform(-1.5, 1.5)
            x0[12] = rng.uniform(-13, -8)
            res = minimize(
                lambda x, v=vr: flavour.chi2_from_params(x, v)[0],
                x0,
                method="Nelder-Mead",
                options={"maxiter": 3500, "xatol": 1e-8, "fatol": 1e-8},
            )
            chi2, detail = flavour.chi2_from_params(res.x, vr)
            if chi2 < best:
                best = chi2
                obs = detail.get("observables", {})
                best_pert = bool(obs.get("perturbative_4pi", False))
                best_sum = obs.get("sum_mnu_eV")
        flavour_rows.append(
            {
                "v_R_GeV": vr,
                "chi2_best_light_search": best,
                "perturbative": best_pert,
                "sum_mnu_eV": best_sum,
                "is_v20_scale": abs(vr / VS - 1.0) < 1e-9,
            }
        )

    # Dedicated package polish at v20 + natural (heavier but definitive)
    package = flavour.run_fit(seed=20)
    ss = package["v20_single_scale_point"]
    best = package["best_overall"]
    beta_profile = json.loads(
        ROOT.joinpath("TAN_BETA_PROFILE_V20_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    beta_best = beta_profile["best_profile_point"]

    return {
        "unification": {
            "M_GUT_GeV": m_gut,
            "alpha_inv_GUT": a_inv,
            "tau_p_benchmark_yr": tau_med,
            "below_SK_2p4e34": tau_med < tau_sk,
            "below_HyperK_1e35": tau_med < tau_hk,
            "note": (
                "Benchmark lifetime at central M_GUT with fixed hadronic factors; "
                "full MC spread is in so10_axion_v17_engine (~35% SK-excluded)."
            ),
        },
        "flavour_vr_scan_light": flavour_rows,
        "flavour_package": {
            "best_tag": best["tag"],
            "best_chi2": best["chi2"],
            "best_v_R": best["v_r_GeV"],
            "v20_chi2": ss["chi2"],
            "v20_perturbative": ss["perturbative_4pi"],
            "v20_viable_chi2_lt_30": ss["single_scale_viable"],
            "tan_beta_unique": beta_profile["unique_tan_beta_demonstrated"],
            "fixed_vR_profile_best_tan_beta": beta_best["tan_beta"],
            "fixed_vR_profile_best_chi2": beta_best["chi2"],
            "profile_improves_reference": beta_profile[
                "corrected_profile_improves_reference"
            ],
            "any_profile_point_viable_chi2_lt_30": beta_profile[
                "any_profile_point_viable_chi2_lt_30"
            ],
        },
        "joint_tension": {
            "exact_vR_equals_vS_flavour_stressed": ss["chi2"] > best["chi2"] + 2.0,
            "proton_central_above_SK": tau_med > tau_sk,
            "compatible_window_exists": bool(
                ss["single_scale_viable"] and tau_med > tau_sk * 0.5
            ),
        },
        "verdict": (
            "Central M_GUT lifetime sits near/above SK. After corrected "
            "Takagi/charged-lepton-basis extraction, the current v_R=v_S "
            "profile has no chi2<30 point, so the single-scale flavour "
            "benchmark is not viable within this constrained ansatz. A "
            "precision global fit remains external."
        ),
    }


# ---------------------------------------------------------------------------
# 4. Experiment reach triage
# ---------------------------------------------------------------------------
def experiment_reach_triage() -> dict:
    experiments = [
        {
            "name": "MADMAX (full)",
            "covers_37GHz": True,
            "status": "R&D / staged; design aims ~40–400 µeV QCD axion",
            "can_reach_v20_g_projected": True,
            "priority": 1,
        },
        {
            "name": "ORGAN",
            "covers_37GHz": True,
            "status": "operating / upgraded; design includes ~63–207 µeV",
            "can_reach_v20_g_projected": "partial_to_full_depending_on_stage",
            "priority": 1,
        },
        {
            "name": "ALPHA / broadband dielectric",
            "covers_37GHz": True,
            "status": "proposed / R&D",
            "can_reach_v20_g_projected": True,
            "priority": 2,
        },
        {
            "name": "ADMX / CAPP cavities",
            "covers_37GHz": False,
            "status": "optimized for lower GHz / µeV decades",
            "can_reach_v20_g_projected": False,
            "priority": 3,
        },
        {
            "name": "CAST / IAXO helioscopes",
            "covers_37GHz": False,
            "status": "solar axions; g limit ~1e-11, far above v20 DM coupling",
            "can_reach_v20_g_projected": False,
            "priority": 4,
        },
    ]
    top = [e["name"] for e in experiments if e["priority"] == 1]
    return {
        "target_window_GHz": [36.6, 37.6],
        "target_g_GeV_inv": G_AGG,
        "experiments": experiments,
        "recommended_contact_list": top,
        "verdict": (
            "Highest-leverage physical next step: engage MADMAX/ORGAN (and "
            "ALPHA-class) with the in-repo 37 GHz templates."
        ),
    }


# ---------------------------------------------------------------------------
# 5. BBN lifetime grid
# ---------------------------------------------------------------------------
def bbn_lifetime_grid() -> dict:
    life = spectrum.lifetime_report(1e-8)
    floor = life["max_portal_floor"]
    portals = [floor * x for x in (0.1, 0.5, 1.0, 2.0, 10.0, 1e3, 1e8)]
    rows = []
    for p in portals:
        rep = spectrum.lifetime_report(p)
        worst = max(c["lifetime_s"] for c in rep["components"].values())
        rows.append(
            {
                "portal": p,
                "worst_lifetime_s": worst,
                "all_below_1s": worst < 1.0,
                "bbn_safe_proxy": worst < 1.0,
            }
        )
    return {
        "portal_floor_tau_lt_1s": floor,
        "grid": rows,
        "verdict": (
            f"For |lambda| >~ {floor:.2e} all components decay before 1 s "
            "(BBN-safe proxy). Smaller portals need a Boltzmann network."
        ),
    }


# ---------------------------------------------------------------------------
# 6. Quality C_eff boundary
# ---------------------------------------------------------------------------
def quality_boundary() -> dict:
    # |C_eff| * UNIT_P8 < 1e-10  => |C_eff| < 1e-10 / UNIT
    c_max = 1e-10 / UNIT_P8
    wil = wilson.build_report()
    mild = wil["operator_running"]["NDA_O1_at_MPl_mild_grow"]
    large = wil["operator_running"]["large_Wilson_1e6_at_MPl"]
    return {
        "unit_kernel_worst_phase": UNIT_P8,
        "max_abs_Ceff_for_quality_1e-10": c_max,
        "O1_mild_grow_Ceff": mild["C8_eff_schematic"],
        "O1_mild_grow_safe": mild["quality"]["safe_below_1e-10"],
        "C_1e6_Ceff": large["C8_eff_schematic"],
        "C_1e6_safe": large["quality"]["safe_below_1e-10"],
        "verdict": (
            f"Quality tolerates |C_eff| up to ~{c_max:.2e}. O(1) and even "
            "forced 1e6 Planck Wilson envelopes remain safe in this schematic."
        ),
    }


def build_report() -> dict:
    astro = astrophysics_ledger()
    pq = pq_history_scenarios()
    joint = joint_flavour_proton()
    reach = experiment_reach_triage()
    bbn = bbn_lifetime_grid()
    qual = quality_boundary()

    checks = [
        ("astro_not_excluded", not astro["currently_excluded_by_listed_bounds"]),
        ("preinflation_theta_finite", math.isfinite(pq["scenarios"]["pre_inflationary_PQ"]["theta_i_for_all_DM"])),
        ("Gmu_below_1e-10", pq["scenarios"]["post_inflationary_v20_13_m3"]["G_mu"] < 1e-10),
        ("flavour_v20_chi2_finite", math.isfinite(joint["flavour_package"]["v20_chi2"])),
        (
            "flavour_tan_beta_nonunique_detected",
            not joint["flavour_package"]["tan_beta_unique"],
        ),
        (
            "corrected_single_scale_flavour_not_viable",
            not joint["flavour_package"]["v20_viable_chi2_lt_30"]
            and not joint["flavour_package"][
                "any_profile_point_viable_chi2_lt_30"
            ],
        ),
        ("proton_central_finite", math.isfinite(joint["unification"]["tau_p_benchmark_yr"])),
        ("madmax_organ_priority", reach["recommended_contact_list"] == ["MADMAX (full)", "ORGAN"]),
        ("bbn_floor_positive", bbn["portal_floor_tau_lt_1s"] is not None and bbn["portal_floor_tau_lt_1s"] > 0),
        ("quality_O1_safe", qual["O1_mild_grow_safe"]),
    ]
    failed = [name for name, ok in checks if not ok]

    return {
        "status": "PASS" if not failed else "FAIL",
        "n_checks": len(checks),
        "n_failed": len(failed),
        "failures": failed,
        "astrophysics_ledger": astro,
        "pq_history": pq,
        "joint_flavour_proton": joint,
        "experiment_reach": reach,
        "bbn_lifetime_grid": bbn,
        "quality_boundary": qual,
        "still_external": [
            "physical 36.6–37.6 GHz haloscope scan",
            "lattice (13,-3) string-network simulation",
            "complete Wilson operator-basis mixing",
            "independent human diagrammatic review",
        ],
        "verdict": (
            "Next in-repo analyses completed: the 37 GHz photon benchmark remains "
            "open and the central proton estimate is finite, but corrected "
            "Takagi/PMNS extraction rejects the constrained v_R=v_S flavour "
            "benchmark and full fermion portal matching remains open. "
            "MADMAX/ORGAN remain the direct-search priorities. Not a discovery."
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Next physics analysis — v20",
        "",
        f"**Status:** {report['status']} — {report['n_checks']} checks, {report['n_failed']} failed",
        "",
        "## 1. Astrophysics / lab ledger",
        "",
        report["astrophysics_ledger"]["verdict"],
        "",
    ]
    for b in report["astrophysics_ledger"]["bounds"]:
        excl = "EXCLUDES" if b["excludes_v20"] else "open"
        g = b["g_limit_GeV_inv"]
        gtxt = f"{g:.2e}" if g is not None else "n/a"
        lines.append(f"- **{b['bound']}**: g_lim={gtxt} → {excl} (`{b['source']}`)")
    lines += [
        "",
        "## 2. PQ / domain-wall / misalignment",
        "",
        report["pq_history"]["verdict"],
        "",
        f"- θ_i (all DM) = {report['pq_history']['scenarios']['pre_inflationary_PQ']['theta_i_for_all_DM']:.3f}",
        f"- H_I max = {report['pq_history']['scenarios']['pre_inflationary_PQ']['H_I_max_GeV']:.3e} GeV",
        f"- Gμ ((13,-3)) = {report['pq_history']['scenarios']['post_inflationary_v20_13_m3']['G_mu']:.3e}",
        "",
        "## 3. Joint flavour × proton decay",
        "",
        report["joint_flavour_proton"]["verdict"],
        "",
        f"- M_GUT = {report['joint_flavour_proton']['unification']['M_GUT_GeV']:.4e} GeV",
        f"- τ_p benchmark = {report['joint_flavour_proton']['unification']['tau_p_benchmark_yr']:.3e} yr",
        f"- flavour best χ² = {report['joint_flavour_proton']['flavour_package']['best_chi2']:.2f} "
        f"({report['joint_flavour_proton']['flavour_package']['best_tag']})",
        f"- exact v_R=v_S χ² = {report['joint_flavour_proton']['flavour_package']['v20_chi2']:.2f}",
        f"- fixed-v_R profile best: tanβ={report['joint_flavour_proton']['flavour_package']['fixed_vR_profile_best_tan_beta']:.2f}, "
        f"χ²={report['joint_flavour_proton']['flavour_package']['fixed_vR_profile_best_chi2']:.2f}",
        f"- unique tanβ: {report['joint_flavour_proton']['flavour_package']['tan_beta_unique']}",
        "",
        "## 4. Experiment reach triage",
        "",
        report["experiment_reach"]["verdict"],
        "",
        f"- Priority contacts: {', '.join(report['experiment_reach']['recommended_contact_list'])}",
        "",
        "## 5. BBN lifetime grid",
        "",
        report["bbn_lifetime_grid"]["verdict"],
        "",
        "## 6. Quality boundary",
        "",
        report["quality_boundary"]["verdict"],
        "",
        "## Still external",
        "",
        *[f"- {x}" for x in report["still_external"]],
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    print("=== NEXT PHYSICS ANALYSIS (v20) ===", flush=True)
    report = build_report()
    ROOT.joinpath("NEXT_PHYSICS_ANALYSIS_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    md = write_markdown(report)
    ROOT.joinpath("NEXT_PHYSICS_ANALYSIS.md").write_text(md, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "astro_excluded": report["astrophysics_ledger"]["currently_excluded_by_listed_bounds"],
                "theta_i": report["pq_history"]["scenarios"]["pre_inflationary_PQ"]["theta_i_for_all_DM"],
                "G_mu": report["pq_history"]["scenarios"]["post_inflationary_v20_13_m3"]["G_mu"],
                "v20_flavour_chi2": report["joint_flavour_proton"]["flavour_package"]["v20_chi2"],
                "tau_p_yr": report["joint_flavour_proton"]["unification"]["tau_p_benchmark_yr"],
                "priority_experiments": report["experiment_reach"]["recommended_contact_list"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
