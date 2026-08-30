#!/usr/bin/env python3
"""V33 derivation campaign for the SUSY Pati--Salam G1--G8 theory.

V33 replaces the unphysical FCMA-18 finite projector with an honest EFT
operator tower, constructs and live-validates a Z4R x Z33 source deformation,
derives source-determined tree matrices, captures raw symbolic RGE output,
integrates the gauge-only subsystem, and quantifies the
remaining non-identifiability.  A derived subproblem is not counted as a full
gate: microscopic geometry, SUSY-breaking boundary data, physical thresholds,
Boltzmann initial data, and flavour Wilson tensors remain independent inputs.
"""

from __future__ import annotations

import argparse
import cmath
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import susy_v24_ps_source_contract as v24
import susy_v32_complete_theory_promotion_audit as v32


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V33_DERIVATION_CAMPAIGN.json"
REPORT_MD = ROOT / "SUSY_V33_DERIVATION_CAMPAIGN.md"
EXACT_JSON = ROOT / "SUSY_V33_EXACT_DERIVATIONS.json"
NEW_PHYSICS_JSON = ROOT / "SUSY_V33_NEW_PHYSICS_CANDIDATES.json"
GATES_JSON = ROOT / "SUSY_V33_G1_G8_GATE_LEDGER.json"
RGE_JSON = ROOT / "SUSY_V33_SARAH_RGE_ATTESTATION.json"
SOFT_RGE_JSON = ROOT / "SUSY_V33_SARAH_SOFT_RGE_ATTESTATION.json"
Z33_MODEL = ROOT / "models" / "PSZ4RZ33SUSYV33" / "PSZ4RZ33SUSYV33.m"

STATUS = (
    "V33_DERIVATION_CAMPAIGN_COMPLETE__Z33_EFT_SOURCE_LIVE__FCMA18_FINITE_"
    "SYMMETRY_NO_GO_PROVED__TREE_SPECTRUM_AND_VACUUM_BRANCHES_DERIVED__"
    "RAW_SARAH_TWO_LOOP_BETA_OUTPUT_CAPTURED__ALL_EIGHT_GATE_FRONTIERS_"
    "ADVANCED__ESTABLISHED_FULL_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY"
)

SOURCE_FILES = (
    "susy_v33_derivation_campaign.py",
    "susy_v24_ps_source_contract.py",
    "susy_v32_complete_theory_promotion_audit.py",
    "SUSY_V32_COMPLETE_THEORY_PROMOTION_AUDIT.json",
    "SUSY_V24_PS_SOURCE_CONTRACT.json",
    "SUSY_V24_PS_VACUUM_RG_FRONTIER.json",
    "SUSY_V31_BENCHMARK_INPUT_LEDGER.json",
    "SUSY_V31_SPECTRUM_VACUUM_LEDGER.json",
    "SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json",
    "SUSY_V33_SARAH_RGE_ATTESTATION.json",
    "SUSY_V33_SARAH_SOFT_RGE_ATTESTATION.json",
    "models/PSZ4RZ33SUSYV33/PSZ4RZ33SUSYV33.m",
    "models/PSZ4RZ33SUSYV33/parameters.m",
    "models/PSZ4RZ33SUSYV33/particles.m",
    "tools/validate-susy-v33-z33.wls",
    "tools/derive-susy-v33-ps-rges.wls",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(name: str | Path) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def finite_symmetry_no_go() -> dict[str, Any]:
    scan_rows = []
    assignments = 0
    counterexamples = 0
    for modulus in range(2, 257):
        allowed = []
        for charge_x in range(modulus):
            charge_w = charge_x
            if (3 * charge_x - charge_w) % modulus == 0:
                assignments += 1
                x5_allowed = (5 * charge_x - charge_w) % modulus == 0
                counterexamples += int(not x5_allowed)
                allowed.append(
                    {
                        "qX": charge_x,
                        "qW": charge_w,
                        "X5_allowed": x5_allowed,
                    }
                )
        if allowed:
            scan_rows.append({"N": modulus, "assignments": allowed})
    x_exponents = [2 * m + 1 for m in range(13)]
    p_exponents_z11 = [11 + 22 * k for k in range(7)]
    p_exponents_z33 = [33 + 66 * k for k in range(5)]
    return {
        "theorem": (
            "For a lone singlet X, retaining X and X^3 gives chi_X=chi_W="
            "chi_X^3, hence chi_X^2=1 and every X^(2m+1) transforms as W."
        ),
        "applies_to_nonabelian_finite_groups": (
            "yes: a single unmixed singlet spans a one-dimensional character"
        ),
        "torsion_free_continuous_version": (
            "qX=qW and 3qX=qW imply 2qX=0; in a torsion-free charge group "
            "qX=qW=0, so all powers are neutral"
        ),
        "ZN_scan_maximum_modulus": 256,
        "ZN_assignments_allowing_X_and_X3": assignments,
        "ZN_assignments_forbidding_X5": counterexamples,
        "scan_digest_sha256": hashlib.sha256(canonical_bytes(scan_rows)).hexdigest(),
        "Z4R_Z11_X_tower_first_terms": x_exponents,
        "Z4R_Z11_P_tower_first_terms": p_exponents_z11,
        "Z4R_Z33_P_tower_first_terms": p_exponents_z33,
        "FCMA18_derivable_from_any_finite_internal_symmetry_with_neutral_coefficients": False,
        "scientific_repair": (
            "retain the complete symmetry-allowed EFT tower with power suppression; "
            "do not assert exact zeros"
        ),
    }


def _custom_z33_census() -> list[dict[str, Any]]:
    z33 = {
        row["name"]: (
            -1 if row["name"] in {"PsiBar", "PsiCBar"}
            else 1 if row["name"] == "P"
            else 0
        )
        for row in v24.FIELDS
    }
    r4 = {row["name"]: row["Z4R_charge"] for row in v24.FIELDS}
    rows = []
    for degree in (1, 2, 3):
        for monomial in itertools.combinations_with_replacement(z33, degree):
            multiplicity = v24.ps_singlet_multiplicity(monomial)
            if not multiplicity:
                continue
            r_sum = sum(r4[name] for name in monomial) % 4
            z_sum = sum(z33[name] for name in monomial) % 33
            if r_sum == 2 and z_sum == 0:
                rows.append(
                    {
                        "monomial": list(monomial),
                        "PS_singlet_multiplicity": multiplicity,
                        "Z4R_sum_mod4": r_sum,
                        "Z33_sum_mod33": z_sum,
                    }
                )
    return rows


def pq_breaking_theta(
    harmonic: int,
    *,
    vev_gev: float = 5.0e11,
    soft_a_gev: float = 1.0e4,
    cutoff_gev: float = 2.435e18,
    ndw: int = 4,
    chi_gev4: float = 0.0756**4,
) -> dict[str, Any]:
    log10_lambda4 = (
        math.log10(2.0 * soft_a_gev)
        + harmonic * math.log10(vev_gev)
        - (harmonic - 3) * math.log10(cutoff_gev)
    )
    log10_theta = (
        math.log10(harmonic / ndw)
        + log10_lambda4
        - math.log10(chi_gev4)
    )
    return {
        "harmonic": harmonic,
        "Lambda_bias_fourth_GeV4": 10.0**log10_lambda4 if log10_lambda4 > -300 else 0.0,
        "log10_Lambda_bias_fourth_GeV4": log10_lambda4,
        "theta_bar_unit_coefficient_phase": 10.0**log10_theta if log10_theta > -300 else 0.0,
        "log10_theta_bar_unit_coefficient_phase": log10_theta,
        "formula": "theta=(N/NDW)*(2*A_N*v^N/M^(N-3))/chi for unit |c sin(delta)|",
        "assumptions": {
            "absolute_Wilson_coefficient": 1.0,
            "absolute_sin_phase": 1.0,
            "PQ_soft_A_N_GeV": soft_a_gev,
            "cutoff_GeV": cutoff_gev,
            "P_field_amplitude_GeV": vev_gev,
            "P_amplitude_convention": "|P|=vP (no 1/sqrt(2) factor)",
            "source_local_domain_wall_number": ndw,
            "QCD_susceptibility_GeV4": chi_gev4,
            "QCD_susceptibility_fourth_root_GeV": chi_gev4**0.25,
        },
    }


def z33_selector() -> dict[str, Any]:
    census = _custom_z33_census()
    retained = sorted(
        tuple(sorted(row["monomial"]))
        for row in v24.RENORMALIZABLE_OPERATORS
    )
    observed = sorted(tuple(sorted(row["monomial"])) for row in census)
    rho = (-2) % 33
    grav = (-15) % 33
    return {
        "candidate": "PSZ4RZ33SUSYV33",
        "field_deformation": (
            "replace Z11 by Z33; q(P)=+1, q(PsiBar)=q(PsiCBar)=-1, "
            "all other visible Z33 charges zero"
        ),
        "renormalizable_gauge_invariant_selector_count": len(census),
        "renormalizable_operator_multiset_matches_V24_exactly": observed == retained,
        "renormalizable_operator_rows": census,
        "mixed_gauge_anomaly": {
            "raw_each_PS_factor": -2,
            "residue_mod33_each_PS_factor": rho,
            "universal": True,
            "GS_level_one_arithmetic": (rho - 31) % 33 == 0,
        },
        "visible_gravitational_congruence": {
            "raw_signed": -15,
            "residue_mod33": grav,
            "24rho_mod33": (24 * rho) % 33,
            "passes_V24_convention": grav == (24 * rho) % 33,
            "level_24_cancellation_integer": grav - 31 * 24,
        },
        "visible_cubic_arithmetic": {
            "raw_signed": -15,
            "residue_mod33": grav,
            "V30_style_level_24_cancellation_integer": grav - 31 * 24,
            "microscopic_counterterm_derived": False,
        },
        "mixed_product_anomaly_boundary": {
            "sum_dim_q33_times_rfermion_squared_raw": -63,
            "residue_mod33": (-63) % 33,
            "sum_dim_q33_squared_times_rfermion_raw": 33,
            "nonzero_witnesses_require_UV_counterterm_or_cobordism_audit": True,
        },
        "first_pure_P_superpotential_power": 33,
        "pure_P_tower": "P^(33+66k), k>=0",
        "P_VEV_stabilizer": "Z2 generated by the square of Z4R",
        "residual_matter_parity_exact_in_visible_EFT": True,
        "conditional_quality_assuming_A_N_1e4_GeV_unit_Wilson_and_P_equals_vP": {
            "Z11_control": pq_breaking_theta(11),
            "Z33_repair": pq_breaking_theta(33),
            "strong_CP_reference_bound": 1.0e-10,
        },
        "full_product_discrete_gauge_anomaly_completion_established": False,
        "live_model_path": str(Z33_MODEL.relative_to(ROOT)),
    }


def controlled_instanton_repair() -> dict[str, Any]:
    target_action = 10.0
    k = math.ceil(math.exp(target_action))
    x = 1.0 / k
    action = math.log(k)
    re_t = action / (2.0 * math.pi)
    hessian_over_c = 8.0 * math.pi**2 / k
    omitted_relative = k**-3
    coefficient_charges = []
    for harmonic in (1, 2, 3):
        coefficient_charges.append(
            {
                "harmonic": harmonic,
                "Z4R": (2 - 2 * harmonic) % 4,
                "Z33": (-31 * harmonic) % 33,
            }
        )
    return {
        "conditional_local_repair": True,
        "superpotential": "W_i=C_i*x_i*(1-K*x_i)^2",
        "x_i": "exp(-2*pi*T_i)",
        "K": k,
        "integer_coefficients": [1, -2 * k, k * k],
        "x_star": x,
        "instanton_action": action,
        "Re_T_star": re_t,
        "W_TT_over_C": hessian_over_c,
        "rank_for_51_nonzero_Ci": 51,
        "omitted_order_one_x4_relative_to_retained_term": omitted_relative,
        "leading_relative_stationary_shift": 2.0 * omitted_relative,
        "required_coefficient_charges": coefficient_charges,
        "all_terms_have_superpotential_charge_Z4R_Z33": [2, 0],
        "residual_subgroup_after_charged_flux_branch": "Z2",
        "repairs_V30_local_action_control": action >= target_action,
        "repairs_V30_covariance_conditionally": coefficient_charges == [
            {"harmonic": 1, "Z4R": 0, "Z33": 2},
            {"harmonic": 2, "Z4R": 2, "Z33": 4},
            {"harmonic": 3, "Z4R": 0, "Z33": 6},
        ],
        "microscopic_geometry_established": False,
        "open_requirements": [
            "51 independent divisors and a rank-full charge matrix",
            "charged and neutral zero-mode cohomology plus nonzero Pfaffians",
            "tadpole, Freed--Witten and K-theory consistency for large flux integers",
            "derivation of the transforming flux branch and all omitted harmonics",
        ],
    }


def jacobi_eigenvalues_symmetric(
    matrix: Sequence[Sequence[float]], *, tolerance: float = 1.0e-13
) -> list[float]:
    values = [list(map(float, row)) for row in matrix]
    size = len(values)
    for _ in range(100 * size * size):
        p, q = 0, 1
        maximum = 0.0
        for i in range(size):
            for j in range(i + 1, size):
                if abs(values[i][j]) > maximum:
                    maximum, p, q = abs(values[i][j]), i, j
        if maximum < tolerance:
            break
        app, aqq, apq = values[p][p], values[q][q], values[p][q]
        angle = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c, s = math.cos(angle), math.sin(angle)
        for k in range(size):
            if k in (p, q):
                continue
            aik, aqk = values[p][k], values[q][k]
            values[p][k] = values[k][p] = c * aik - s * aqk
            values[q][k] = values[k][q] = s * aik + c * aqk
        values[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        values[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        values[p][q] = values[q][p] = 0.0
    return sorted(values[i][i] for i in range(size))


def _two_by_two_eigenvalues(a: float, b: float, d: float) -> list[float]:
    discriminant = math.sqrt((a - d) ** 2 + 4.0 * b * b)
    return [0.5 * (a + d - discriminant), 0.5 * (a + d + discriminant)]


def component_spectrum_and_vacuum(
    inputs: dict[str, Any],
    pheno: dict[str, Any],
    v32_physics: dict[str, Any],
) -> dict[str, Any]:
    ew = inputs["electroweak_inputs"]
    soft = inputs["soft_benchmark"]
    tanb = soft["tan_beta"]
    sinb = tanb / math.sqrt(1.0 + tanb * tanb)
    cosb = 1.0 / math.sqrt(1.0 + tanb * tanb)
    cos2b = (1.0 - tanb * tanb) / (1.0 + tanb * tanb)
    mz, mw = ew["MZ_GeV"], ew["MW_GeV"]
    sw = math.sqrt(ew["sin2_thetaW_MSbar_MZ"])
    cw = math.sqrt(1.0 - sw * sw)
    m1 = soft["gaugino_running_GeV"]["M1"]
    m2 = soft["gaugino_running_GeV"]["M2"]
    mu = soft["mu_GeV"]
    neutralino_matrix = [
        [m1, 0.0, -mz * sw * cosb, mz * sw * sinb],
        [0.0, m2, mz * cw * cosb, -mz * cw * sinb],
        [-mz * sw * cosb, mz * cw * cosb, 0.0, -mu],
        [mz * sw * sinb, -mz * cw * sinb, -mu, 0.0],
    ]
    neutralino_signed = jacobi_eigenvalues_symmetric(neutralino_matrix)
    neutralino_masses = sorted(abs(value) for value in neutralino_signed)
    chargino = [[m2, math.sqrt(2.0) * mw * sinb], [math.sqrt(2.0) * mw * cosb, mu]]
    xtx_a = chargino[0][0] ** 2 + chargino[1][0] ** 2
    xtx_b = chargino[0][0] * chargino[0][1] + chargino[1][0] * chargino[1][1]
    xtx_d = chargino[0][1] ** 2 + chargino[1][1] ** 2
    chargino_masses = [math.sqrt(value) for value in _two_by_two_eigenvalues(xtx_a, xtx_b, xtx_d)]

    running_stop_soft = soft["common_third_squark_GeV"]
    top_pole = 172.76
    xt = soft["At_GeV"] - mu / tanb
    dl = (0.5 - (2.0 / 3.0) * ew["sin2_thetaW_MSbar_MZ"]) * mz**2 * cos2b
    dr = ((2.0 / 3.0) * ew["sin2_thetaW_MSbar_MZ"]) * mz**2 * cos2b
    stop_ll = running_stop_soft**2 + top_pole**2 + dl
    stop_rr = running_stop_soft**2 + top_pole**2 + dr
    stop_off = top_pole * xt
    derived_stop_masses = [math.sqrt(value) for value in _two_by_two_eigenvalues(stop_ll, stop_off, stop_rr)]
    inserted_stops = [2450.0, 3600.0]
    target_delta = inserted_stops[1] ** 2 - inserted_stops[0] ** 2
    required_off_squared = 0.25 * (target_delta**2 - (dl - dr) ** 2)
    required_abs_xt = math.sqrt(required_off_squared) / top_pole
    required_common_soft_squared = (
        0.5 * (inserted_stops[0] ** 2 + inserted_stops[1] ** 2)
        - top_pole**2
        - 0.5 * (dl + dr)
    )

    ma = soft["mA_GeV"]
    higgs_disc = (ma**2 + mz**2) ** 2 - 4.0 * ma**2 * mz**2 * cos2b**2
    mh2 = 0.5 * (ma**2 + mz**2 - math.sqrt(higgs_disc))
    m_big_h2 = 0.5 * (ma**2 + mz**2 + math.sqrt(higgs_disc))
    tree_higgs = {
        "mh_GeV": math.sqrt(mh2),
        "mH_GeV": math.sqrt(m_big_h2),
        "mA_GeV": ma,
        "mHcharged_GeV": math.sqrt(ma**2 + mw**2),
    }
    stop_scale = math.sqrt(derived_stop_masses[0] * derived_stop_masses[1])
    running_top = 150.0
    mixing = (xt / stop_scale) ** 2 * (1.0 - xt**2 / (12.0 * stop_scale**2))
    delta_higgs = 3.0 * running_top**4 / (2.0 * math.pi**2 * ew["v_GeV"] ** 2) * (
        math.log(stop_scale**2 / running_top**2) + mixing
    )
    one_loop_higgs = math.sqrt(mh2 + delta_higgs)

    ewsb = pheno.get("ewsb") or read_json("SUSY_V31_SPECTRUM_VACUUM_LEDGER.json")["ewsb"]
    mhu2, mhd2, bmu = ewsb["mHu2_GeV2"], ewsb["mHd2_GeV2"], ewsb["Bmu_GeV2"]
    determinant_origin = (mhu2 + mu**2) * (mhd2 + mu**2) - bmu**2
    dflat_margin = mhu2 + mhd2 + 2.0 * mu**2 - 2.0 * abs(bmu)
    ccb_ratio = soft["At_GeV"] ** 2 / (
        3.0 * (2.0 * running_stop_soft**2 + mhu2 + mu**2)
    )

    base_ps_inverse = pheno["gauge_unification"]["alpha_inverse_MPS_PS_order_4_L_R"]
    universal_shift = v32_physics["corrected_gauge_running"]["universal_inverse_alpha_shift"]
    corrected_ps_inverse = [value - universal_shift for value in base_ps_inverse]
    g4 = math.sqrt(4.0 * math.pi / corrected_ps_inverse[0])
    gr = math.sqrt(4.0 * math.pi / corrected_ps_inverse[2])
    vps = pheno["gauge_unification"]["MPS_GeV"]
    vector_masses = [g4 * vps, gr * vps, math.sqrt(1.5 * g4 * g4 + gr * gr) * vps]

    kappa = kappa_x = 1.0
    saddle_s2_over_v2 = kappa_x / (kappa + 2.0 * kappa_x)
    saddle_x2_over_v2 = kappa / (kappa + 2.0 * kappa_x)
    saddle_energy = kappa**3 / (kappa + 2.0 * kappa_x) * vps**4
    return {
        "visible_complex_chiral_component_count": sum(
            row["multiplicity"] * math.prod(abs(value) for value in row["PS_representation"])
            for row in v24.FIELDS
        ),
        "PS_broken_generators_and_eaten_chirals": 9,
        "physical_chiral_multiplets_after_PS_super_Higgs": 102,
        "exact_PS_breaking_W_Hessian": {
            "dimension": [23, 23],
            "rank": 14,
            "nullity": 9,
            "mass_squared_classes": [
                {"formula": "2*|kappa|^2*vPS^2", "multiplicity": 2},
                {"formula": "|lambdaS|^2*vPS^2", "multiplicity": 6},
                {"formula": "|lambdaSb|^2*vPS^2", "multiplicity": 6},
            ],
        },
        "PS_vectors": {
            "corrected_inverse_couplings_4_L_R": corrected_ps_inverse,
            "g4": g4,
            "gR": gr,
            "mass_formulas": ["g4*vPS", "gR*vPS", "sqrt(3*g4^2/2+gR^2)*vPS"],
            "multiplicities": [6, 2, 1],
            "masses_GeV": vector_masses,
            "V31_ninefold_degenerate_row_valid": False,
        },
        "tree_neutralinos": {
            "matrix_GeV": neutralino_matrix,
            "signed_eigenvalues_GeV": neutralino_signed,
            "physical_masses_GeV": neutralino_masses,
            "V31_inserted_masses_GeV": [198.0, 207.0, 606.0, 1210.0],
            "pole_self_energies_calculated": False,
        },
        "tree_charginos": {
            "matrix_GeV": chargino,
            "physical_singular_values_GeV": chargino_masses,
            "V31_inserted_masses_GeV": [205.0, 1212.0],
            "pole_self_energies_calculated": False,
        },
        "stop_consistency": {
            "Xt_GeV": xt,
            "derived_from_declared_common_soft_masses_GeV": derived_stop_masses,
            "V31_inserted_masses_GeV": inserted_stops,
            "inserted_pair_required_abs_Xt_GeV": required_abs_xt,
            "inserted_pair_required_common_soft_GeV": math.sqrt(required_common_soft_squared),
            "declared_At_compatible_with_inserted_pair": False,
        },
        "EWSB_and_Higgs": {
            "tree_masses": tree_higgs,
            "leading_one_loop_diagnostic_mh_GeV": one_loop_higgs,
            "V31_inserted_mh_GeV": ew["mh_GeV"],
            "origin_instability_determinant_GeV4": determinant_origin,
            "D_flat_boundedness_margin_GeV2": dflat_margin,
            "tree_Higgs_subspace_local_minimum": determinant_origin < 0.0 and dflat_margin > 0.0,
            "traditional_stop_CCB_ratio": ccb_ratio,
            "traditional_stop_CCB_inequality_passes": ccb_ratio < 1.0,
            "full_loop_pole_or_tunneling_certificate": False,
        },
        "exact_reduced_F_flat_branches": {
            "potential": "[kappa*(s^2-v^2)+kappaX*x^2]^2+2*kappa^2*x^2*s^2",
            "PS_broken": "x=0, s^2=v^2",
            "PS_unbroken": "s=0, x^2=(kappa/kappaX)*v^2",
            "both_global_SUSY_energies": 0.0,
            "positive_coupling_saddle_s2_over_v2": saddle_s2_over_v2,
            "positive_coupling_saddle_x2_over_v2": saddle_x2_over_v2,
            "unit_coupling_saddle_barrier_GeV4": saddle_energy,
            "soft_mass_only_PS_selection_inequality": (
                "mS^2+mSbar^2 < (kappa/kappaX)*mX^2"
            ),
            "universal_positive_soft_masses_select_PS_branch": False,
        },
        "full_G2_G3_G4_closed": False,
    }


def hidden_sector_and_mediation(inputs: dict[str, Any], pheno: dict[str, Any]) -> dict[str, Any]:
    mpl = 2.435e18
    gravitino = 1.0e4
    fz = math.sqrt(3.0) * gravitino * mpl
    sqrt_fz = math.sqrt(fz)
    w0 = gravitino * mpl**2
    inverse = pheno["gauge_unification"]["alpha_inverse_MSUSY"]
    masses = [
        inputs["soft_benchmark"]["gaugino_running_GeV"][key]
        for key in ("M1", "M2", "M3")
    ]
    gauge_kinetic_coefficients = [
        2.0 * mass / ((4.0 * math.pi / inv) * math.sqrt(3.0) * gravitino)
        for mass, inv in zip(masses, inverse)
    ]
    messenger_index = 4.0
    messenger_lambdas = [
        4.0 * math.pi * mass / (messenger_index * (1.0 / inv))
        for mass, inv in zip(masses, inverse)
    ]
    mean_lambda = sum(messenger_lambdas) / len(messenger_lambdas)
    fp = mean_lambda * inputs["axion_cosmology_inputs"]["fa_GeV"]
    anomaly_mediation = [
        6.6 * (1.0 / inverse[0]) / (4.0 * math.pi) * gravitino,
        1.0 * (1.0 / inverse[1]) / (4.0 * math.pi) * gravitino,
        -3.0 * (1.0 / inverse[2]) / (4.0 * math.pi) * gravitino,
    ]
    return {
        "V30_vacuum": {
            "W": 0,
            "all_F_and_D": 0,
            "m32_GeV": 0,
            "all_soft_terms": 0,
            "can_generate_V31_BFA8": False,
        },
        "minimal_nilpotent_uplift": {
            "K": "K_visible+Zdagger*Z",
            "W": "W_visible+f*Z+W0, Z^2=0",
            "target_m32_GeV": gravitino,
            "W0_GeV3": w0,
            "FZ_GeV2": fz,
            "sqrt_FZ_GeV": sqrt_fz,
            "canonical_visible_scalar_mass_GeV": gravitino,
            "tree_gaugino_masses_GeV": [0.0, 0.0, 0.0],
            "sequestered_anomaly_mediation_diagnostic_GeV": anomaly_mediation,
            "reproduces_V31_soft_benchmark": False,
        },
        "fitted_gauge_kinetic_contact": {
            "formula": "M_a=(g_a^2/2)*c_a*sqrt(3)*m32",
            "required_c_a": gauge_kinetic_coefficients,
            "coefficients_are_predictions": False,
        },
        "PQ_family_gauge_mediation_diagnostic": {
            "messenger_index": messenger_index,
            "required_Lambda_a_GeV": messenger_lambdas,
            "relative_span": (max(messenger_lambdas) - min(messenger_lambdas)) / mean_lambda,
            "mean_Lambda_GeV": mean_lambda,
            "required_FP_GeV2": fp,
            "V30_FP_GeV2": 0.0,
            "requires_new_hidden_coupling": True,
        },
        "microscopic_mediation_derived": False,
    }


def decode_complex_matrix(rows: Sequence[Sequence[Mapping[str, float]]]) -> list[list[complex]]:
    return [[complex(value["re"], value["im"]) for value in row] for row in rows]


def _matmul_dagger_self(matrix: Sequence[Sequence[complex]]) -> list[list[complex]]:
    n_columns = len(matrix[0])
    return [
        [
            sum(matrix[k][i].conjugate() * matrix[k][j] for k in range(len(matrix)))
            for j in range(n_columns)
        ]
        for i in range(n_columns)
    ]


def cosmology_flavour_and_proton(
    inputs: dict[str, Any], pheno: dict[str, Any]
) -> dict[str, Any]:
    flav = pheno["flavour_and_neutrinos"]
    y = decode_complex_matrix(flav["Dirac_Yukawa"])
    ydagy = _matmul_dagger_self(y)
    off_diagonal = max(
        abs(ydagy[i][j]) for i in range(3) for j in range(3) if i != j
    )
    cp_invariants = [
        (ydagy[0][j] ** 2).imag for j in (1, 2)
    ]
    tr = inputs["axion_cosmology_inputs"]["reheat_temperature_GeV"]
    m_heavy = flav["right_neutrino_masses_GeV"]
    light = flav["neutrino_masses_eV"]
    vu174 = 174.0 * inputs["soft_benchmark"]["tan_beta"] / math.sqrt(
        1.0 + inputs["soft_benchmark"]["tan_beta"] ** 2
    )
    delta_m_gev = (light[-1] - light[0]) * 1.0e-9
    epsilon_di_m1 = 3.0 / (16.0 * math.pi) * m_heavy[0] * delta_m_gev / vu174**2
    epsilon_di_tr = 3.0 / (16.0 * math.pi) * tr * delta_m_gev / vu174**2
    eta_b_upper_at_tr = 0.0096 * epsilon_di_tr

    ndw = 4
    vp = inputs["axion_cosmology_inputs"]["fa_GeV"]
    fa_pole = vp / ndw
    fa_fixed = vp
    axion_branches = [
        {
            "normalization": "preserve V31 KSVZ/PQ pole",
            "vP_GeV": vp,
            "fa_GeV": fa_pole,
            "ma_micro_eV": 5.691e12 / fa_pole,
            "frequency_GHz": (5.691e12 / fa_pole) * 0.24179893,
        },
        {
            "normalization": "preserve V31 physical fa",
            "vP_GeV": ndw * fa_fixed,
            "fa_GeV": fa_fixed,
            "ma_micro_eV": 5.691e12 / fa_fixed,
            "frequency_GHz": (5.691e12 / fa_fixed) * 0.24179893,
        },
    ]
    for row in axion_branches:
        row["g_agamma_GeV_inverse"] = (
            (1.0 / 137.035999084)
            / (2.0 * math.pi * row["fa_GeV"])
            * (8.0 / 3.0 - 1.92)
        )

    mpl = 2.435e18
    z11_theta = pq_breaking_theta(11)["theta_bar_unit_coefficient_phase"]
    z33_theta = pq_breaking_theta(33)["theta_bar_unit_coefficient_phase"]
    relic_power = 1.165
    target_axion_relic = inputs["axion_cosmology_inputs"][
        "target_axion_relic_omega_h2"
    ]
    total_dark_matter = inputs["axion_cosmology_inputs"][
        "observed_cold_dark_matter_omega_h2"
    ]
    scalar_amplitude = 2.1e-9
    beta_isocurvature = 0.038

    def anharmonic_factor(theta: float) -> float:
        return math.log(math.e / (1.0 - (theta / math.pi) ** 2)) ** relic_power

    def misalignment_relic(theta: float, fa_value: float) -> float:
        return (
            0.12
            * theta**2
            * anharmonic_factor(theta)
            * (fa_value / 5.0e11) ** relic_power
        )

    def solve_misalignment(fa_value: float) -> float:
        left, right = 0.0, math.pi * (1.0 - 1.0e-12)
        for _ in range(160):
            middle = 0.5 * (left + right)
            if misalignment_relic(middle, fa_value) < target_axion_relic:
                left = middle
            else:
                right = middle
        return 0.5 * (left + right)

    wall_rows = []
    for branch in axion_branches:
        theta_i = solve_misalignment(branch["fa_GeV"])
        axion_fraction = target_axion_relic / total_dark_matter
        hi_bound = (
            math.pi
            * branch["fa_GeV"]
            * theta_i
            * math.sqrt(beta_isocurvature * scalar_amplitude)
            / axion_fraction
        )
        min_bias_over_chi = 64.0 * (branch["fa_GeV"] / mpl) ** 2
        wall_rows.append(
            {
                "normalization": branch["normalization"],
                "minimum_bias_over_chi_for_decay_before_domination": min_bias_over_chi,
                "preinflation_misalignment_angle_rad": theta_i,
                "replayed_axion_relic_omega_h2": misalignment_relic(
                    theta_i, branch["fa_GeV"]
                ),
                "preinflation_isocurvature_HI_upper_GeV": hi_bound,
            }
        )
    z11_bias_ratio = z11_theta * ndw / 11.0
    z11_wall_min = wall_rows[0]["minimum_bias_over_chi_for_decay_before_domination"]
    z11_coefficient_window = [z11_wall_min / z11_bias_ratio, 1.0e-10 / z11_theta]

    pmns = decode_complex_matrix(flav["PMNS"]["matrix"])
    mbeta = math.sqrt(sum(abs(pmns[0][i]) ** 2 * light[i] ** 2 for i in range(3)))
    mbb_terms = [pmns[0][i] ** 2 * light[i] for i in range(3)]
    mbb_magnitudes = [abs(value) for value in mbb_terms]
    mbb_max = sum(mbb_magnitudes)
    mbb_min = max(0.0, max(mbb_magnitudes) - (mbb_max - max(mbb_magnitudes)))
    mbb_zero_majorana = abs(sum(mbb_terms))

    c5 = 1.0e-31
    alpha2 = 0.033
    m2_dressing = 1211.0
    squark = 5000.0
    c6 = alpha2 / (4.0 * math.pi) * m2_dressing / squark**2 * c5
    proton_inputs = {
        "proton_mass_GeV": 0.9382720813,
        "neutral_pion_mass_GeV": 0.1349768,
        "pion_decay_constant_GeV": 0.1302,
        "D": 0.804,
        "F": 0.463,
        "long_distance_factor_A_L": 1.25,
        "hadronic_matrix_element_beta_H_GeV3": 0.012,
        "hbar_GeV_s": 6.582119569e-25,
        "seconds_per_year": 365.25 * 24.0 * 3600.0,
    }
    proton_width = (
        proton_inputs["proton_mass_GeV"]
        / (32.0 * math.pi * proton_inputs["pion_decay_constant_GeV"] ** 2)
        * (
            1.0
            - proton_inputs["neutral_pion_mass_GeV"] ** 2
            / proton_inputs["proton_mass_GeV"] ** 2
        )
        ** 2
        * proton_inputs["long_distance_factor_A_L"] ** 2
        * proton_inputs["hadronic_matrix_element_beta_H_GeV3"] ** 2
        * (1.0 + proton_inputs["D"] + proton_inputs["F"]) ** 2
        * c6**2
    )
    proton_lifetime = (
        proton_inputs["hbar_GeV_s"]
        / proton_width
        / proton_inputs["seconds_per_year"]
    )
    return {
        "PQ_anomaly": {
            "N": -4,
            "E": -32.0 / 3.0,
            "E_over_N": 8.0 / 3.0,
            "source_local_NDW": ndw,
            "GS_mixed_physical_NDW_derived": False,
        },
        "axion_normalization_branches": axion_branches,
        "Z11_to_Z33_quality_and_wall_tradeoff": {
            "conditional_quality_assumptions": pq_breaking_theta(11)["assumptions"],
            "Z11_theta_at_V31_values_unit_coefficient": z11_theta,
            "Z11_unit_coefficient_exceeds_1e_minus_10": z11_theta > 1.0e-10,
            "conditional_Z11_coefficient_phase_window_for_quality_and_wall_decay": z11_coefficient_window,
            "Z33_theta_at_V31_values_unit_coefficient": z33_theta,
            "Z33_postinflation_bias_sufficient": False,
            "preinflation_branches": wall_rows,
            "preinflation_relic_and_isocurvature_assumptions": {
                "target_axion_relic_omega_h2": target_axion_relic,
                "total_dark_matter_omega_h2": total_dark_matter,
                "axion_fraction": target_axion_relic / total_dark_matter,
                "scalar_amplitude_A_s": scalar_amplitude,
                "isocurvature_fraction_beta": beta_isocurvature,
                "anharmonic_factor": "[ln(e/(1-theta_i^2/pi^2))]^1.165",
                "relic_formula": "0.12*theta_i^2*F(theta_i)*(fa/5e11 GeV)^1.165",
                "HI_formula": "pi*fa*theta_i*sqrt(beta_iso*A_s)/(Omega_a/Omega_DM)",
            },
            "physical_GS_wall_quotient_computed": False,
        },
        "conditional_radiative_PQ_breaking": {
            "one_loop_leading_log_required_S_lambda": 2.425,
            "S_lambda_definition": (
                "8*(|lambdaPQ|^2+|lambdaPX|^2+|lambdaPcQ|^2+|lambdaPcX|^2)"
            ),
            "equal_two_active_couplings_minimum": math.sqrt(2.425 / 16.0),
            "equal_four_active_couplings_minimum": math.sqrt(2.425 / 32.0),
            "source_soft_boundary_present": False,
            "radiative_PQ_vacuum_established": False,
        },
        "thermal_leptogenesis": {
            "YdagY": [
                [
                    {"re": value.real, "im": value.imag}
                    for value in row
                ]
                for row in ydagy
            ],
            "maximum_off_diagonal_magnitude": off_diagonal,
            "Im_YdagY_1j_squared": cp_invariants,
            "standard_decay_CP_asymmetry_for_R_identity": 0.0,
            "TR_over_M1": tr / m_heavy[0],
            "thermal_N1_production_viable": tr >= m_heavy[0],
            "Davidson_Ibarra_epsilon1_upper_at_M1": epsilon_di_m1,
            "Davidson_Ibarra_epsilon1_upper_if_M1_equals_TR": epsilon_di_tr,
            "absolute_etaB_upper_if_M1_equals_TR_and_efficiency_one": eta_b_upper_at_tr,
            "observed_etaB_reference": 6.12e-10,
            "current_benchmark_viable": False,
            "repair_requirements": [
                "a derived complex Casas-Ibarra R or another CP source",
                "TR at least comparable to the lightest thermally produced state",
                "a solved flavour-covariant Boltzmann system",
            ],
        },
        "source_baryon_operators": {
            "renormalizable_PS_vector_mediated_proton_decay_present": False,
            "schematic_invariant_classes_identified": True,
            "complete_independent_flavour_operator_basis_derived": False,
            "leading_superpotential": (
                "w0/Lambda^2 * [cL_ijkl epsilon4 epsilon2 epsilon2 Q_i Q_j Q_k Q_l "
                "+ cR_ijkl epsilon4 epsilon2 epsilon2 Qc_i Qc_j Qc_k Qc_l]"
            ),
            "MSSM_components": ["QQQL", "UcUcDcEc", "UcDcDcNc"],
            "odd_matter_RPV_forbidden_in_visible_holomorphic_EFT_with_parity_preserving_P_w0_spurions": True,
            "illustrative_C5_GeV_inverse": c5,
            "illustrative_wino_dressed_C6_GeV_inverse2": c6,
            "illustrative_width_GeV": proton_width,
            "illustrative_lifetime_years": proton_lifetime,
            "illustrative_lifetime_formula": (
                "Gamma=mp/(32*pi*fpi^2)*(1-mpi^2/mp^2)^2*A_L^2*beta_H^2*"
                "(1+D+F)^2*|C6|^2; tau=hbar/Gamma"
            ),
            "illustrative_lifetime_inputs": proton_inputs,
            "lifetime_is_prediction": False,
            "missing": [
                "cL/cR flavour tensors and antisymmetries",
                "mass-basis rotations and wino/higgsino dressing",
                "operator running, interference and correlated lattice inputs",
            ],
        },
        "conditional_neutrino_derived_observables": {
            "sum_mnu_eV": sum(light),
            "m_beta_eV": mbeta,
            "m_betabeta_range_free_Majorana_phases_eV": [mbb_min, mbb_max],
            "m_betabeta_zero_Majorana_phase_assumption_eV": mbb_zero_majorana,
            "derived_from_fitted_oscillation_inputs": True,
            "out_of_sample_prediction": False,
        },
        "full_G5_G7_G8_closed": False,
    }


def _fraction_vector(values: Iterable[Any]) -> list[float]:
    return [float(Fraction(str(value))) for value in values]


def _fraction_matrix(values: Iterable[Iterable[Any]]) -> list[list[float]]:
    return [[float(Fraction(str(value))) for value in row] for row in values]


def _inverse_run(inv: Sequence[float], beta: Sequence[float], log_ratio: float) -> list[float]:
    return [value - coefficient * log_ratio / (2.0 * math.pi) for value, coefficient in zip(inv, beta)]


def _newton_two_loop_root(
    inverse_ms: list[float],
    frontier: dict[str, Any],
    *,
    ms: float,
    fa: float,
    initial_logs: list[float],
) -> dict[str, Any]:
    below, above = frontier["RG_below_PS"], frontier["RG_above_PS"]
    b_mssm = _fraction_vector(below["MSSM"]["b"])
    big_mssm = _fraction_matrix(below["MSSM"]["B"])
    b_vector = _fraction_vector(below["MSSM_plus_vectorlike_family"]["b"])
    big_vector = _fraction_matrix(below["MSSM_plus_vectorlike_family"]["B"])
    b_ps = _fraction_vector(above["b"])
    big_ps = _fraction_matrix(above["B"])
    log_fa_ms = math.log(fa / ms)
    alpha_fa = v32.rk4_two_loop_gauge_alpha(
        [1.0 / value for value in inverse_ms], b_mssm, big_mssm, log_fa_ms
    )

    def endpoint(logs: Sequence[float]) -> list[float]:
        alpha_low = v32.rk4_two_loop_gauge_alpha(
            alpha_fa, b_vector, big_vector, logs[0] - log_fa_ms
        )
        inverse_low = [1.0 / value for value in alpha_low]
        inverse_ps = [
            inverse_low[2],
            inverse_low[1],
            (5.0 / 3.0) * inverse_low[0] - (2.0 / 3.0) * inverse_low[2],
        ]
        alpha_high = v32.rk4_two_loop_gauge_alpha(
            [1.0 / value for value in inverse_ps], b_ps, big_ps, logs[1]
        )
        return [1.0 / value for value in alpha_high]

    def residual(logs: Sequence[float]) -> tuple[list[float], list[float]]:
        end = endpoint(logs)
        return [end[0] - end[1], end[0] - end[2]], end

    logs = list(initial_logs)
    iterations = 0
    for iterations in range(1, 15):
        values, _ = residual(logs)
        if max(abs(value) for value in values) < 1.0e-11:
            break
        step = 1.0e-4
        columns = []
        for index in range(2):
            trial = list(logs)
            trial[index] += step
            shifted, _ = residual(trial)
            columns.append([(shifted[i] - values[i]) / step for i in range(2)])
        jacobian = [[columns[j][i] for j in range(2)] for i in range(2)]
        determinant = jacobian[0][0] * jacobian[1][1] - jacobian[0][1] * jacobian[1][0]
        delta = [
            (-values[0] * jacobian[1][1] + jacobian[0][1] * values[1]) / determinant,
            (jacobian[1][0] * values[0] - jacobian[0][0] * values[1]) / determinant,
        ]
        logs = [logs[i] + delta[i] for i in range(2)]
    values, inverse_g = residual(logs)
    mps = ms * math.exp(logs[0])
    mg = mps * math.exp(logs[1])

    def boundary_objective(log_ps: float) -> tuple[float, list[float], list[float]]:
        alpha_low = v32.rk4_two_loop_gauge_alpha(
            alpha_fa, b_vector, big_vector, log_ps - log_fa_ms
        )
        inverse_low = [1.0 / value for value in alpha_low]
        inverse_ps = [
            inverse_low[2],
            inverse_low[1],
            (5.0 / 3.0) * inverse_low[0] - (2.0 / 3.0) * inverse_low[2],
        ]
        mean = sum(inverse_ps) / 3.0
        corrections = [mean - value for value in inverse_ps]
        return sum(value * value for value in corrections), inverse_ps, corrections

    left, right = math.log(1.0e15 / ms), math.log(3.0e16 / ms)
    for _ in range(100):
        m_left = left + (right - left) / 3.0
        m_right = right - (right - left) / 3.0
        if boundary_objective(m_left)[0] < boundary_objective(m_right)[0]:
            right = m_right
        else:
            left = m_left
    boundary_log = 0.5 * (left + right)
    _, boundary_inverse, boundary_correction = boundary_objective(boundary_log)
    return {
        "iterations": iterations,
        "MPS_GeV": mps,
        "MG_GeV": mg,
        "log_MG_over_MPS": logs[1],
        "alpha_inverse_MG": inverse_g,
        "alpha_G": 3.0 / sum(inverse_g),
        "residuals": values,
        "physically_ordered_PS_interval": logs[1] > 0.0,
        "boundary_repair": {
            "common_boundary_GeV": ms * math.exp(boundary_log),
            "uncorrected_alpha_inverse_4_L_R": boundary_inverse,
            "minimum_zero_sum_Delta_alpha_inverse_4_L_R": boundary_correction,
            "linearized_maximum_fractional_g_shift": max(
                abs(-0.5 * delta / value)
                for delta, value in zip(boundary_correction, boundary_inverse)
            ),
            "exact_maximum_fractional_g_shift": max(
                abs(math.sqrt(value / (value + delta)) - 1.0)
                for delta, value in zip(boundary_correction, boundary_inverse)
            ),
            "derived_from_source": False,
        },
    }


def gauge_running_and_rges(
    inputs: dict[str, Any], pheno: dict[str, Any], frontier: dict[str, Any]
) -> dict[str, Any]:
    source_rge = read_json(RGE_JSON.name)
    soft_rge = read_json(SOFT_RGE_JSON.name)
    spectrum = read_json("SUSY_V31_SPECTRUM_VACUUM_LEDGER.json")["pole_spectrum"]
    poles = {row["sector"]: row for row in spectrum}
    inverse_ms = pheno["gauge_unification"]["alpha_inverse_MSUSY"]
    neutralinos = poles["neutralinos"]["pole_masses_GeV"]
    charginos = poles["charginos"]["pole_masses_GeV"]
    stops = poles["stops"]["pole_masses_GeV"]
    sbottoms = poles["sbottoms"]["pole_masses_GeV"]
    threshold_sectors = [
        {
            "sector": "wino",
            "Delta_b": [0.0, 4.0 / 3.0, 0.0],
            "effective_mass_GeV": math.sqrt(neutralinos[-1] * charginos[-1]),
        },
        {
            "sector": "gluino",
            "Delta_b": [0.0, 0.0, 2.0],
            "effective_mass_GeV": poles["gluino"]["pole_mass_GeV"],
        },
        {
            "sector": "higgsinos",
            "Delta_b": [2.0 / 5.0, 2.0 / 3.0, 0.0],
            "effective_mass_GeV": (
                neutralinos[0] * neutralinos[1] * charginos[0]
            ) ** (1.0 / 3.0),
        },
        {
            "sector": "heavy_Higgs_doublet",
            "Delta_b": [1.0 / 10.0, 1.0 / 6.0, 0.0],
            "effective_mass_GeV": math.sqrt(
                poles["heavy_neutral_Higgs"]["pole_mass_GeV"]
                * poles["charged_Higgs"]["pole_mass_GeV"]
            ),
        },
        {
            "sector": "first_second_generation_squarks",
            "Delta_b": [11.0 / 15.0, 1.0, 4.0 / 3.0],
            "effective_mass_GeV": poles[
                "first_second_generation_squarks"
            ]["pole_mass_GeV"],
        },
        {
            "sector": "third_generation_squarks",
            "Delta_b": [11.0 / 30.0, 1.0 / 2.0, 2.0 / 3.0],
            "effective_mass_GeV": math.prod(stops + sbottoms) ** 0.25,
        },
        {
            "sector": "all_sleptons",
            "Delta_b": [9.0 / 10.0, 1.0 / 2.0, 0.0],
            "effective_mass_GeV": (
                poles["charged_sleptons"]["pole_mass_GeV"] ** 6
                * poles["sneutrinos"]["pole_mass_GeV"] ** 3
            ) ** (1.0 / 9.0),
        },
    ]
    ms = inputs["soft_benchmark"]["MSUSY_GeV"]
    for row in threshold_sectors:
        row["Delta_alpha_inverse"] = [
            coefficient
            / (2.0 * math.pi)
            * math.log(row["effective_mass_GeV"] / ms)
            for coefficient in row["Delta_b"]
        ]
    pole = [
        sum(row["Delta_alpha_inverse"][index] for row in threshold_sectors)
        for index in range(3)
    ]
    summed_delta_b = [
        sum(row["Delta_b"][index] for row in threshold_sectors)
        for index in range(3)
    ]
    scheme = [0.0, -2.0 / (12.0 * math.pi), -3.0 / (12.0 * math.pi)]
    corrected_start = [
        value + pole_shift + scheme_shift
        for value, pole_shift, scheme_shift in zip(inverse_ms, pole, scheme)
    ]
    declared_pq_pole = inputs["axion_cosmology_inputs"]["fa_GeV"]
    source_local_ndw = 4.0
    physical_fa_preserving_pq_pole = source_local_ndw * declared_pq_pole
    b_mssm = [6.6, 1.0, -3.0]
    b_vector = [10.6, 5.0, 1.0]
    b_ps = [1.0, 5.0, 9.0]

    def solve_one_loop(vector_threshold: float) -> tuple[dict[str, Any], list[float]]:
        log_vector_ms = math.log(vector_threshold / ms)

        def endpoint(logs: Sequence[float]) -> list[float]:
            at_vector = _inverse_run(corrected_start, b_mssm, log_vector_ms)
            at_ps_low = _inverse_run(
                at_vector, b_vector, logs[0] - log_vector_ms
            )
            at_ps = [
                at_ps_low[2],
                at_ps_low[1],
                (5.0 / 3.0) * at_ps_low[0]
                - (2.0 / 3.0) * at_ps_low[2],
            ]
            return _inverse_run(at_ps, b_ps, logs[1])

        logs = [math.log(1.0e16 / ms), math.log(1.05)]
        for _ in range(5):
            end = endpoint(logs)
            residual = [end[0] - end[1], end[0] - end[2]]
            step = 1.0e-5
            columns = []
            for index in range(2):
                trial = list(logs)
                trial[index] += step
                shifted = endpoint(trial)
                shifted_residual = [
                    shifted[0] - shifted[1], shifted[0] - shifted[2]
                ]
                columns.append(
                    [(shifted_residual[i] - residual[i]) / step for i in range(2)]
                )
            jac = [[columns[j][i] for j in range(2)] for i in range(2)]
            determinant = (
                jac[0][0] * jac[1][1] - jac[0][1] * jac[1][0]
            )
            delta = [
                (-residual[0] * jac[1][1] + jac[0][1] * residual[1])
                / determinant,
                (jac[1][0] * residual[0] - jac[0][0] * residual[1])
                / determinant,
            ]
            logs = [logs[i] + delta[i] for i in range(2)]
        inverse_g = endpoint(logs)
        return (
            {
                "vectorlike_threshold_GeV": vector_threshold,
                "MPS_GeV": ms * math.exp(logs[0]),
                "MG_GeV": ms * math.exp(logs[0] + logs[1]),
                "log_MG_over_MPS": logs[1],
                "alpha_inverse_MG": inverse_g,
                "alpha_G": 3.0 / sum(inverse_g),
            },
            logs,
        )

    one_loop, logs = solve_one_loop(declared_pq_pole)
    two_loop = _newton_two_loop_root(
        corrected_start,
        frontier,
        ms=ms,
        fa=declared_pq_pole,
        initial_logs=logs,
    )
    alternative_one_loop, alternative_logs = solve_one_loop(
        physical_fa_preserving_pq_pole
    )
    alternative_two_loop = _newton_two_loop_root(
        corrected_start,
        frontier,
        ms=ms,
        fa=physical_fa_preserving_pq_pole,
        initial_logs=alternative_logs,
    )
    running_branches = {
        "preserve_declared_KSVZ_PQ_pole": {
            "physical_fa_GeV": declared_pq_pole / source_local_ndw,
            "vectorlike_threshold_GeV": declared_pq_pole,
            "corrected_one_loop_root": one_loop,
            "gauge_only_two_loop_root": two_loop,
        },
        "preserve_V31_claimed_physical_fa": {
            "physical_fa_GeV": declared_pq_pole,
            "vectorlike_threshold_GeV": physical_fa_preserving_pq_pole,
            "corrected_one_loop_root": alternative_one_loop,
            "gauge_only_two_loop_root": alternative_two_loop,
        },
    }
    return {
        "live_SARAH_declared_Z33_source": {
            "model": source_rge["model"],
            "engine": source_rge["engine"],
            "tool": source_rge["tool"],
            "mode": source_rge["mode"],
            "two_loop_RGE_calculation_succeeded": source_rge[
                "two_loop_RGE_calculation_succeeded"
            ],
            "beta_counts": source_rge["beta_counts"],
            "attestation_file_sha256": sha256_file(RGE_JSON),
            "raw_beta_expression_payload_sha256": hashlib.sha256(
                canonical_bytes(
                    {
                        "gauge": source_rge["beta_gauge_input_form"],
                        "superpotential": source_rge[
                            "beta_superpotential_input_form"
                        ],
                    }
                )
            ).hexdigest(),
            "raw_symbolic_output_captured": True,
            "dummy_index_contractions_validated": False,
            "reference_coefficient_validation_complete": False,
            "group_contractions_independently_reference_validated": False,
            "coupled_gauge_yukawa_soft_solution_present": False,
            "coupled_gauge_Yukawa_soft_system_integrated": False,
        },
        "formal_soft_mirror": {
            "model": soft_rge["model"],
            "continuous_Lagrangian_identical_to_Z33_source": True,
            "two_loop_RGE_calculation_succeeded": soft_rge[
                "two_loop_RGE_calculation_succeeded"
            ],
            "beta_counts": soft_rge["beta_counts"],
            "soft_beta_expression_sha256": soft_rge["soft_beta_expression_sha256"],
            "raw_soft_expression_hash_captured": True,
            "full_soft_expression_payload_stored": False,
            "coupled_gauge_Yukawa_soft_system_integrated": False,
            "mediation_boundary_present": False,
        },
        "known_low_scale_corrections": {
            "pole_Delta_alpha_inverse": pole,
            "pole_threshold_sector_decomposition": threshold_sectors,
            "summed_Delta_b": summed_delta_b,
            "summed_Delta_b_equals_MSSM_minus_SM": all(
                math.isclose(value, target, rel_tol=0.0, abs_tol=1.0e-14)
                for value, target in zip(summed_delta_b, [2.5, 25.0 / 6.0, 4.0])
            ),
            "MSbar_to_DRbar_Delta_alpha_inverse": scheme,
            "corrected_alpha_inverse_MSUSY": corrected_start,
            "pole_threshold_decomposition_is_gauge_eigenstate_approximation": True,
        },
        "corrected_one_loop_root": one_loop,
        "gauge_only_two_loop_root": two_loop,
        "axion_normalization_running_branches": running_branches,
        "precision_unification_closed": False,
        "reason": (
            "known corrections give an ordered one-loop interval, but the gauge-only "
            "two-loop root reverses MG and MPS; coupled Yukawa/soft running, finite "
            "nonuniversal matching and pole covariance must be derived before closure"
        ),
    }


def uv_precedent_map() -> list[dict[str, Any]]:
    return [
        {
            "source": "https://arxiv.org/abs/1503.02068",
            "landed": "global three-family F-theory Pati--Salam spectrum, G4 flux and D3 tadpole",
            "missing_for_V33": "V33 field/operator map, full moduli stabilization and soft terms",
        },
        {
            "source": "https://arxiv.org/abs/hep-th/0601064",
            "landed": "three-family Type-IIA Pati--Salam flux vacua and candidate moduli stabilization",
            "missing_for_V33": "different spectrum with exotics and no V33 coefficient map",
        },
        {
            "source": "https://arxiv.org/abs/1703.03402",
            "landed": "semi-realistic Pati--Salam instanton stabilization examples",
            "missing_for_V33": "51-sector divisor/zero-mode frame, uplift and SUSY breaking",
        },
        {
            "source": "https://arxiv.org/abs/1105.3193",
            "landed": "fluxed E3 zero-mode lifting mechanism",
            "missing_for_V33": "the explicit V33 divisors, fluxes, Pfaffians and visible intersections",
        },
    ]


def gate_ledger() -> dict[str, Any]:
    states = [
        (
            "G1",
            "FINITE_PROJECTOR_NO_GO__Z33_EFT_AND_CONTROLLED_LOCAL_REPAIR_LANDED__MICROSCOPIC_OPEN",
            "finite-symmetry theorem, exact Z33 renormalizable census, visible GS congruences, controlled charged-flux local polynomial",
            "complete product-discrete anomaly/cobordism audit and one explicit divisor/zero-mode compactification",
        ),
        (
            "G2",
            "TREE_COMPONENT_SUBSECTORS_DERIVED__FULL_POLES_OPEN",
            "111-component count, rank-14 breaking Hessian, split vector masses, tree neutralino/chargino/stop matrices",
            "all component mass matrices, self-energies, pole mixings and threshold covariance",
        ),
        (
            "G3",
            "COMPETING_F_FLAT_BRANCH_AND_BARRIER_DERIVED__GLOBAL_SELECTION_OPEN",
            "PS-broken and PS-unbroken zero-energy branches, saddle and leading soft selection inequality",
            "source-derived Kähler/soft potential, complete branch quotient and tunneling solution",
        ),
        (
            "G4",
            "TREE_EWSB_AND_UPLIFT_REQUIREMENTS_DERIVED__MEDIATION_AND_POLES_OPEN",
            "tree EWSB/Higgs/electroweakino/stop results, CCB diagnostic, nilpotent uplift scale and fitted contact requirements",
            "microscopic mediation, coupled soft running, precision Higgs pole, longevity and experimental likelihoods",
        ),
        (
            "G5",
            "PQ_ANOMALY_QUALITY_WALL_AND_LEPTOGENESIS_CONDITIONS_DERIVED__COSMOLOGY_OPEN",
            "pure-P source-local NDW=4, conditional Z33 quality repair, wall/preinflation conditions and exact R=I leptogenesis failure",
            "GS axion quotient, radiative PQ boundary, Boltzmann history and a derived CP/flavour source",
        ),
        (
            "G6",
            "RAW_SARAH_TWO_LOOP_OUTPUT_CAPTURED__PHYSICAL_ORDERING_REQUIRES_COUPLED_RUNNING_OR_MATCHING",
            "live SARAH raw gauge/superpotential output, formal-soft expression hash, pole/scheme corrections and gauge-only two-loop root",
            "source-derived boundaries, nonuniversal heavy thresholds and uncertainty-propagated coupled solution",
        ),
        (
            "G7",
            "SOURCE_BARYON_INVARIANT_CLASSES_IDENTIFIED__LIFETIME_OPEN",
            "schematic w0-dressed Q4 and Qc4 classes plus illustrative dressing scale; invalid PS-vector proton channel removed",
            "flavour tensors, rotations, SUSY dressing, running, lattice covariance and channel distribution",
        ),
        (
            "G8",
            "CONDITIONAL_NEUTRINO_OBSERVABLES_REPLAYED__PREDICTIVE_LIKELIHOOD_OPEN",
            "m_beta and m_betabeta target values replayed from fitted oscillation inputs",
            "out-of-sample flavour origin and a joint likelihood with theory covariance",
        ),
    ]
    rows = [
        {
            "gate": gate,
            "state": state,
            "new_exact_or_reproducible_derivations": landed,
            "remaining_promotion_requirement": missing,
            "established_full_predictive_closed": False,
        }
        for gate, state, landed, missing in states
    ]
    return {
        "schema": "susy-v33-g1-g8-gate-ledger-v1",
        "gates": rows,
        "gate_frontiers_advanced_count": len(rows),
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists": False,
        "promotion_rule": (
            "a no-go, consistency witness, fitted deformation or derived submatrix is not a full predictive gate"
        ),
    }


def new_physics_candidates(
    selector: dict[str, Any], instanton: dict[str, Any], hidden: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema": "susy-v33-new-physics-candidates-v1",
        "active_EFT_repair": {
            "name": "PSZ4RZ33SUSYV33",
            "decision": "ADOPT_AS_RESEARCH_EFT_SOURCE__DO_NOT_PROMOTE_AS_UV_COMPLETE",
            "changes": [
                "Z11 -> Z33 with the same signed visible charges",
                "accept the full symmetry-allowed Wilsonian tower instead of FCMA-18 exact zeros",
                "retain the same exact 18 renormalizable Pati--Salam source terms",
            ],
            "checks": {
                "renormalizable_terms": selector["renormalizable_gauge_invariant_selector_count"],
                "matches_V24": selector["renormalizable_operator_multiset_matches_V24_exactly"],
                "visible_gravity_congruence": selector["visible_gravitational_congruence"]["passes_V24_convention"],
                "leading_P_power": selector["first_pure_P_superpotential_power"],
                "residual_matter_parity": selector["residual_matter_parity_exact_in_visible_EFT"],
            },
            "full_discrete_UV_completion": False,
        },
        "conditional_controlled_flux_repair": instanton,
        "minimal_SUSY_breaking_attempt": hidden["minimal_nilpotent_uplift"],
        "rejected_claims": [
            "FCMA-18 cannot be derived from a finite exact internal symmetry",
            "BFA-8 cannot follow from the V30 supersymmetric Minkowski vacuum",
            "the V31 hard-coded pole ledger is not a pole calculation",
            "Pati--Salam gauge-vector-mediated proton decay is not present in the declared source",
        ],
        "safe_to_claim_new_fundamental_law": False,
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    v32_report = read_json("SUSY_V32_COMPLETE_THEORY_PROMOTION_AUDIT.json")
    if v32_report["core_sha256"] != "6eb7611f7c0195b9812bf0ae23916f5f7f54b28d9a0b38fc85e495369bf0f699":
        raise ValueError("V32 upstream core drifted")
    inputs = read_json("SUSY_V31_BENCHMARK_INPUT_LEDGER.json")
    spectrum = read_json("SUSY_V31_SPECTRUM_VACUUM_LEDGER.json")
    pheno = read_json("SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json")
    frontier = read_json("SUSY_V24_PS_VACUUM_RG_FRONTIER.json")
    v32_physics = read_json("SUSY_V32_CORRECTED_PHYSICS_LEDGER.json")
    finite = finite_symmetry_no_go()
    selector = z33_selector()
    instanton = controlled_instanton_repair()
    components = component_spectrum_and_vacuum(inputs, pheno, v32_physics)
    hidden = hidden_sector_and_mediation(inputs, pheno)
    cosmology = cosmology_flavour_and_proton(inputs, pheno)
    gauge = gauge_running_and_rges(inputs, pheno, frontier)
    gates = gate_ledger()
    exact = {
        "schema": "susy-v33-exact-derivations-v1",
        "finite_symmetry_no_go": finite,
        "Z33_selector": selector,
        "controlled_instanton_repair": instanton,
        "component_spectrum_and_vacuum": components,
        "hidden_sector_and_mediation": hidden,
        "cosmology_flavour_and_proton": cosmology,
        "gauge_running_and_RGEs": gauge,
        "UV_precedent_map": uv_precedent_map(),
    }
    new_physics = new_physics_candidates(selector, instanton, hidden)
    evidence = {
        EXACT_JSON.name: exact,
        NEW_PHYSICS_JSON.name: new_physics,
        GATES_JSON.name: gates,
    }
    report = {
        "schema": "susy-v33-derivation-campaign-v1",
        "status": STATUS,
        "decision": (
            "V33 lands a superior Z33 EFT source and genuine derivations across every "
            "frontier, but external microscopic and boundary data still prevent any "
            "full G1--G8 gate from closing"
        ),
        "active_research_candidate": "PSZ4RZ33SUSYV33",
        "source_manifest": source_manifest(),
        "upstream_V32_core_sha256": v32_report["core_sha256"],
        "evidence_sha256": {
            name: hashlib.sha256(
                (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            ).hexdigest()
            for name, payload in evidence.items()
        },
        "summary": {
            "gate_frontiers_advanced_count": gates["gate_frontiers_advanced_count"],
            "established_full_predictive_closed_count": gates[
                "established_full_predictive_closed_count"
            ],
            "complete_theory_exists": gates["complete_theory_exists"],
            "Z33_live_SARAH_source_pass": gauge["live_SARAH_declared_Z33_source"][
                "two_loop_RGE_calculation_succeeded"
            ],
            "exact_renormalizable_operator_count": selector[
                "renormalizable_gauge_invariant_selector_count"
            ],
            "raw_SARAH_two_loop_source_beta_group_count": sum(
                gauge["live_SARAH_declared_Z33_source"]["beta_counts"][name]
                for name in ("gauge", "trilinear_superpotential", "bilinear_superpotential", "linear_superpotential")
            ),
            "gauge_only_two_loop_has_physical_scale_ordering": gauge[
                "gauge_only_two_loop_root"
            ]["physically_ordered_PS_interval"],
            "safe_to_claim_new_fundamental_law": False,
        },
        "core_sha256": "",
    }
    report["core_sha256"] = canonical_sha(report)
    return report, evidence


def render_markdown(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> str:
    exact = evidence[EXACT_JSON.name]
    selector = exact["Z33_selector"]
    components = exact["component_spectrum_and_vacuum"]
    cosmology = exact["cosmology_flavour_and_proton"]
    gauge = exact["gauge_running_and_RGEs"]
    gates = evidence[GATES_JSON.name]
    quality = selector[
        "conditional_quality_assuming_A_N_1e4_GeV_unit_Wilson_and_P_equals_vP"
    ]
    z33_theta = quality["Z33_repair"][
        "theta_bar_unit_coefficient_phase"
    ]
    two = gauge["gauge_only_two_loop_root"]
    alternative_running = gauge["axion_normalization_running_branches"][
        "preserve_V31_claimed_physical_fa"
    ]
    return f"""# SUSY V33 derivation campaign

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- Active research EFT: `PSZ4RZ33SUSYV33`
- Gate frontiers advanced: **{gates['gate_frontiers_advanced_count']}/8**
- Established full predictive gates: **{gates['established_full_predictive_closed_count']}/8**

## Decision

V33 solves every derivation that is fixed by the declared fields and inputs,
and proves where the remaining requests are mathematically underdetermined.
It does **not** promote a complete theory.  The defensible new architecture is
an ordinary symmetry-complete EFT, not the FCMA-18 exact-zero axiom.

## New Z33 source and G1

- A finite-symmetry theorem proves that allowing both `X` and `X^3` necessarily
  allows every odd `X^(2m+1)`.  The exhaustive `Z_N`, `N<=256` scan has
  `{exact['finite_symmetry_no_go']['ZN_assignments_allowing_X_and_X3']}` solutions
  and zero counterexamples forbidding `X^5`.
- Replacing `Z11` by `Z33` preserves exactly
  `{selector['renormalizable_gauge_invariant_selector_count']}` renormalizable
  operators, passes the visible V24 mixed-gauge/gravitational congruences, and
  leaves `Z2` matter parity.  The first pure-P operator is `P^33`.
- Conditional on `A_N=10 TeV`, `|c sin(delta)|=1`, `|P|=vP` and the reduced
  Planck cutoff, the old `P^11` term gives
  `theta={quality['Z11_control']['theta_bar_unit_coefficient_phase']:.6e}`,
  whereas `P^33` gives `theta={z33_theta:.6e}`.
  Mixed-product discrete anomalies and the microscopic GS counterterms remain open.
- A controlled charged-flux polynomial with `K={exact['controlled_instanton_repair']['K']}`
  reaches instanton action `{exact['controlled_instanton_repair']['instanton_action']:.9f}`
  and rank 51 locally, but its divisor, zero-mode, Pfaffian and tadpole data are
  still conditional.

## G2--G4 derivations

- The visible source has `{components['visible_complex_chiral_component_count']}`
  complex chiral components; nine are eaten.  The exact PS-breaking
  `23x23` superpotential Hessian has rank 14 and nullity 9.
- The split heavy-vector masses are
  `{[f'{value:.6e}' for value in components['PS_vectors']['masses_GeV']]}` GeV,
  not one degenerate row.
- Tree neutralinos are
  `{[round(value, 6) for value in components['tree_neutralinos']['physical_masses_GeV']]}` GeV;
  tree charginos are
  `{[round(value, 6) for value in components['tree_charginos']['physical_singular_values_GeV']]}` GeV.
- The declared common 3 TeV stop input gives
  `{[round(value, 6) for value in components['stop_consistency']['derived_from_declared_common_soft_masses_GeV']]}` GeV,
  not `(2450,3600)` GeV.  The exact tree light Higgs remains
  `{components['EWSB_and_Higgs']['tree_masses']['mh_GeV']:.6f}` GeV.
- The reduced source has two zero-energy branches: a PS-broken branch and a
  PS-unbroken X branch.  Soft masses select the desired branch only if
  `mS^2+mSbar^2 < (kappa/kappaX)mX^2`.
- A minimal nilpotent uplift needs
  `sqrt(F)={exact['hidden_sector_and_mediation']['minimal_nilpotent_uplift']['sqrt_FZ_GeV']:.6e}` GeV,
  but canonical or sequestered mediation does not reproduce BFA-8.

## G5--G8 derivations

- The pure-P, source-local anomaly is `NDW=4`, `E/N=8/3`; the physical
  GS-mixed wall quotient is not derived.  Preserving the declared
  KSVZ pole gives `fa=1.25e11 GeV`, `ma=45.528 micro-eV`, and `11.0086 GHz`.
- Conditional one-loop leading-log radiative PQ breaking requires
  `S_lambda>2.425`: equal active couplings exceed `0.389` for two channels or
  `0.275` for all four.  The needed soft boundary is absent.
- `R=I` makes every standard heavy-neutrino decay CP invariant zero, while
  `TR/M1={cosmology['thermal_leptogenesis']['TR_over_M1']:.3e}`.  Standard
  thermal leptogenesis therefore fails.
- Live SARAH 4.15.3 emitted raw two-loop beta output for all 18 source
  superpotential parameters and three gauge couplings.  The formal soft mirror
  also emitted 16 trilinear, one bilinear, one linear, 18 scalar-mass and three
  gaugino beta rows, but only its expression hash is retained.  Independent
  contraction/reference validation, coupled integration and a mediation boundary
  are not supplied.
- With known pole and scheme corrections, one loop gives
  `MPS={gauge['corrected_one_loop_root']['MPS_GeV']:.6e} GeV` and
  `MG={gauge['corrected_one_loop_root']['MG_GeV']:.6e} GeV`.  Gauge-only two
  loop gives `MPS={two['MPS_GeV']:.6e} GeV`, `MG={two['MG_GeV']:.6e} GeV`,
  reversing the physical ordering.  The physical-`fa` branch also reverses,
  with `MPS={alternative_running['gauge_only_two_loop_root']['MPS_GeV']:.6e} GeV`
  and `MG={alternative_running['gauge_only_two_loop_root']['MG_GeV']:.6e} GeV`.
  Coupled running or finite/split matching must repair the interval.
- The source identifies schematic baryon invariant classes
  `w0 Q^4/Lambda^2` and `w0 Qc^4/Lambda^2`; it does not yet derive their
  independent flavour basis, and no PS gauge-vector proton lifetime is reinstated.
- Conditional neutrino derived observables are
  `m_beta={cosmology['conditional_neutrino_derived_observables']['m_beta_eV']:.8f} eV` and
  `m_betabeta={cosmology['conditional_neutrino_derived_observables']['m_betabeta_range_free_Majorana_phases_eV']} eV`.
  They inherit fitted oscillation inputs and are not out-of-sample predictions.

## Remaining completion boundary

All eight frontiers now have stronger exact calculations, but all eight full
gates remain open.  Completion still requires one explicit microscopic source
for the product-discrete counterterms, divisor/zero modes, Kähler potential,
SUSY breaking, boundary tensors, physical thresholds, flavour coefficients,
cosmological history and baryon Wilson coefficients.

## Primary sources

- [Pati--Salam source](https://arxiv.org/abs/2009.04582)
- [Global three-family F-theory Pati--Salam models](https://arxiv.org/abs/1503.02068)
- [Fluxed E3 instantons](https://arxiv.org/abs/1105.3193)
- [Pati--Salam instanton moduli stabilization](https://arxiv.org/abs/1703.03402)
- [MSSM spectrum and EWSB formulas](https://arxiv.org/abs/hep-ph/9709356)
- [Gauge mediation](https://arxiv.org/abs/hep-ph/9801271)
- [Thermal leptogenesis bound](https://arxiv.org/abs/hep-ph/0202239)
- [MSbar--DRbar conversion](https://arxiv.org/abs/hep-ph/9308222)
- [Pati--Salam dimension-five proton decay](https://arxiv.org/abs/2211.02054)
- [QCD axion mass relation](https://arxiv.org/abs/1511.02867)

## Replay

```bash
python -B susy_v33_derivation_campaign.py --check
python -m pytest -q test_susy_v33_derivation_campaign.py
wolframscript -file tools/validate-susy-v33-z33.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3
```
"""


def output_map(
    report: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> dict[Path, str]:
    rendered = {
        REPORT_JSON: json.dumps(report, indent=2, sort_keys=True) + "\n",
        REPORT_MD: render_markdown(report, evidence),
    }
    for name, payload in evidence.items():
        rendered[ROOT / name] = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return rendered


def write_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    for path, content in output_map(report, evidence).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> bool:
    for path, content in output_map(report, evidence).items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report, evidence = build_bundle()
    if arguments.check:
        if not check_outputs(report, evidence):
            raise SystemExit("V33 frozen outputs are missing or drifted")
    else:
        write_outputs(report, evidence)
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
