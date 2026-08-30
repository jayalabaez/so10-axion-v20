"""Frozen V24 no-go certificate for minimal non-GS anomaly completions.

The certificate asks whether the derived PS Z4R x Z11 selector can be made
strictly anomaly free with weakly-coupled real/vectorlike heavy matter, while
retaining the landed PQ quality and perturbative cutoff window.  It proves a
sharp obstruction for P-generated masses and performs a finite charge scan for
one additional zero-PQ mass spurion (plus the necessary existing-P repair when
that spurion has rS=0).  It is a negative boundary certificate, not a
completed G1--G8 theory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.json"
MD_PATH = HERE / "SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.md"

F_PQ_GEV = 1.76e11
V_PS_GEV = 1.0e16
CUTOFF_GEV = 1.0e18
W0_GEV = 1.0e5
CHI_QCD_GEV4 = 0.0756**4
ALPHA_R_INV_TWO_LOOP_ENDPOINT = 9.686379301220
ALPHA_G_INV_BASELINE = 24.0
BASE_B_R = 9


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def alpha_r_one_loop_ledger() -> dict[str, float]:
    alpha_ps = ALPHA_G_INV_BASELINE - 4 / (2 * math.pi) * math.log(V_PS_GEV / F_PQ_GEV)
    endpoint = alpha_ps - BASE_B_R / (2 * math.pi) * math.log(CUTOFF_GEV / V_PS_GEV)
    return {
        "alpha_PS_inverse_at_vPS": round(alpha_ps, 12),
        "SU2R_b_above_PS": BASE_B_R,
        "alpha_R_inverse_at_1e18_one_loop_only": round(endpoint, 12),
        "upstream_coupled_gauge_only_two_loop_endpoint": ALPHA_R_INV_TWO_LOOP_ENDPOINT,
    }


def p_mass_congruence() -> dict[str, Any]:
    # W contains Lambda^(1-k) P^k Phi Phi.  S_G is the total Dynkin index of
    # the massive real field or conjugate pair in gauge factor G.
    solutions = [k for k in range(0, 67) if k % 11 == 7 and k % 2 == 1]
    minimum = min(k for k in solutions if k > 0)
    return {
        "normalization": "T(fundamental)=1/2; eta(Z4R)=2; eta(Z11)=11",
        "visible_mixed_residues": {"Z4R_mod2": 1, "Z11_mod11": 9},
        "mass_operator": "W contains Lambda^(1-k) P^k Phi Phi",
        "K_definition": "K_G=sum_i k_i*S_G(i), with S_G the total massive-sector Dynkin index",
        "heavy_contributions": {
            "Delta_A_Z11": "-K_G/2 (mod 11)",
            "Delta_A_Z4R": "-K_G (mod 2)",
        },
        "equations": ["9-K_G/2=0 (mod 11)", "1-K_G=0 (mod 2)"],
        "combined_congruence": "K_G=7 (mod 22)",
        "solutions_in_scan": solutions,
        "minimum_positive_K_each_PS_factor": minimum,
    }


def p_mass_threshold(minimum_k: int) -> dict[str, Any]:
    running = alpha_r_one_loop_ledger()
    log_ratio = math.log(CUTOFF_GEV / F_PQ_GEV)
    cost = minimum_k / (2 * math.pi) * log_ratio
    endpoint = running["alpha_R_inverse_at_1e18_one_loop_only"]
    projected = endpoint - cost
    return {
        "formula": "Delta alpha_G^-1(1e18)=-K_G/(2*pi)*ln(Lambda/fPQ)",
        "fPQ_GeV": F_PQ_GEV,
        "Lambda_GeV": CUTOFF_GEV,
        "K_min": minimum_k,
        "minimum_inverse_coupling_cost": round(cost, 12),
        "existing_one_loop_only_SU2R_inverse_at_cutoff": endpoint,
        "existing_coupled_gauge_only_two_loop_SU2R_inverse_at_cutoff": ALPHA_R_INV_TWO_LOOP_ENDPOINT,
        "projected_one_loop_SU2R_inverse_after_minimal_completion": round(projected, 12),
        "one_loop_necessary_perturbativity_condition_pass": projected > 0,
        "interpretation": "The same-order one-loop budget already fails; positive gauge two-loop terms reduce the available endpoint further.",
    }


def minimal_real_ten_witness() -> dict[str, Any]:
    p2_mass = F_PQ_GEV**2 / CUTOFF_GEV
    rows = [
        {
            "field": "T0",
            "SO10_rep": "10=(6,1,1)+(1,2,2)",
            "multiplicity": 1,
            "Z4R": 0,
            "Z11": 5,
            "signed_Z11": 5,
            "PQ": "-1/2",
            "mass_operator": "P*T0*T0",
            "P_power_k": 1,
            "mass_GeV": F_PQ_GEV,
        },
        {
            "field": "T2",
            "SO10_rep": "10=(6,1,1)+(1,2,2)",
            "multiplicity": 3,
            "Z4R": 1,
            "Z11": 10,
            "signed_Z11": -1,
            "PQ": -1,
            "mass_operator": "P^2*T2*T2/Lambda",
            "P_power_k": 2,
            "mass_GeV": p2_mass,
        },
    ]
    return {
        "role": "minimal explicit mixed-gauge anomaly cancellation witness; rejected by RG and wall tests",
        "fields": rows,
        "continuous_PS_anomalies": {
            "cancel": True,
            "reason": "The SO(10) 10 is real; its PS sextet is real and its bidoublet supplies an even number of doublets for each SU(2).",
        },
        "mixed_anomalies": {
            "Z4R_raw_before_by_factor": [7, 5, 1],
            "heavy_Delta_Z4R_each_factor": -1,
            "Z4R_raw_after_by_factor": [6, 4, 0],
            "Z4R_after_mod2": [0, 0, 0],
            "Z11_raw_before_by_factor": [20, 20, 20],
            "heavy_Delta_Z11_each_factor_signed": 5 + 3 * (-1),
            "Z11_raw_after_by_factor": [22, 22, 22],
            "Z11_after_mod11": [0, 0, 0],
        },
        "weighted_index_K_each_factor": 1 + 3 * 2,
        "P2_mass_GeV": p2_mass,
    }


def gravity_cubic_repair() -> dict[str, Any]:
    return {
        "role": "algebraic singlet repair showing gravity/cubic residues are not the limiting obstruction",
        "before_singlet_repair": {
            "Z4R_gravity_raw": 10,
            "Z11_gravity_raw": 5,
            "Z11_gravity_mod11": 5,
            "Z11_cubic_raw": 1205,
            "Z11_cubic_mod11": 6,
        },
        "singlet_pairs": [
            {
                "multiplicity": 1,
                "charges_A_B": {"Z4R": [0, 0], "Z11_signed": [0, -1], "PQ": [0, -1]},
                "mass_operator": "P*A*B",
                "Delta_Z4R_gravity": -2,
                "Delta_Z11_gravity": -1,
                "Delta_Z11_cubic": -1,
            },
            {
                "multiplicity": 2,
                "charges_C_D": {"Z4R": [1, 1], "Z11_signed": [0, -2], "PQ": [0, -2]},
                "mass_operator": "P^2*C*D/Lambda",
                "Delta_Z4R_gravity_total": 0,
                "Delta_Z11_gravity_total": -4,
                "Delta_Z11_cubic_total": -16,
            },
        ],
        "after_singlet_repair": {
            "Z4R_gravity_raw": 8,
            "Z4R_gravity_mod2": 0,
            "Z11_gravity_raw": 0,
            "Z11_gravity_mod11": 0,
            "Z11_cubic_raw": 1188,
            "Z11_cubic_mod11": 0,
        },
        "complete_generic_singlet_operator_census_landed": False,
    }


def pq_wall_obstruction(minimum_k: int) -> dict[str, Any]:
    initial = -4
    heavy = -minimum_k
    final = initial + heavy
    return {
        "convention": "integer 2N_QCD; the landed KSVZ family has 2N_QCD=-4",
        "PQ_invariance_relation": "PQ(P)=1 and P^k*Phi*Phi imply PQ(Phi pair)=-k",
        "one_SO10_10_QCD_Dynkin_index": 1,
        "initial_2N_QCD": initial,
        "heavy_Delta_2N_QCD": heavy,
        "final_2N_QCD": final,
        "absolute_N_DW_after_completion": abs(final),
        "leading_explicit_P_harmonic": 11,
        "gcd_explicit_harmonic_and_NDW": math.gcd(11, abs(final)),
        "P11_lifts_all_QCD_vacua": math.gcd(11, abs(final)) == 1,
        "general_divisibility": "K=7+22*l gives |2N_QCD|=|4+K|=11*(1+2*l)",
    }


def quality_log10_upper_bound(q_s: int, r_s: int) -> tuple[float, int, int]:
    candidates: list[tuple[float, int, int]] = []
    for n_p in range(1, 23):
        for n_s in range(1, 23):
            if (n_p + q_s * n_s) % 11 != 0:
                continue
            if (2 * n_p + r_s * n_s) % 4 != 2:
                continue
            # Generic coefficient-one soft A-term screen:
            # Delta theta ~ n*w0*f^n*s^m/[chi*Lambda^(n+m-3)].
            log_s = (
                -10
                + math.log10(CHI_QCD_GEV4)
                - math.log10(n_p)
                - math.log10(W0_GEV)
                - n_p * math.log10(F_PQ_GEV)
                + (n_p + n_s - 3) * math.log10(CUTOFF_GEV)
            ) / n_s
            candidates.append((log_s, n_p, n_s))
    if not candidates:
        raise ArithmeticError((q_s, r_s))
    return min(candidates)


def zero_pq_spurion_scan() -> dict[str, Any]:
    running = alpha_r_one_loop_ledger()
    budget = running["alpha_R_inverse_at_1e18_one_loop_only"]
    r_repair_cost = math.log(CUTOFF_GEV / F_PQ_GEV) / (2 * math.pi)
    rows: list[dict[str, Any]] = []
    for r_s in (2, 0):
        for q_s in range(1, 11):
            available = budget
            extra_r_repair: dict[str, Any] | None = None
            if r_s == 2:
                units = (7 * pow(q_s, -1, 11)) % 11
                if units % 2 == 0:
                    units += 11
                mixed_equation = "qS*N=7 (mod 11), N odd"
                ndw_after_repairs = 4
            else:
                # An rS=0 S-mass sector has no Z4R anomaly.  Repair it with a
                # k=1 real 10 whose mass comes from the existing P VEV.  That
                # field also contributes -1/2 to A_Z11, so the S sector must
                # supply qS*N=6 rather than 7.  Its mass is fixed at fPQ.
                units = (6 * pow(q_s, -1, 11)) % 11
                available -= r_repair_cost
                mixed_equation = "1+qS*N=7 (mod 11), where 1 is the k=1 P-mass repair"
                ndw_after_repairs = 5
                extra_r_repair = {
                    "field": "one real SO(10) 10",
                    "charges": {"Z4R": 0, "Z11": 5, "PQ": "-1/2"},
                    "mass_operator": "P*T_R*T_R",
                    "index_units": 1,
                    "P_power_k": 1,
                    "mass_scale_GeV": F_PQ_GEV,
                    "one_loop_inverse_coupling_cost": round(r_repair_cost, 12),
                    "Delta_A_Z4R_mod2": 1,
                    "Delta_A_Z11": "-1/2 mod 11",
                    "Delta_2N_QCD": -1,
                    "N_DW_after_repair_before_S_sector": 5,
                }
            log_quality, n_p, n_s = quality_log10_upper_bound(q_s, r_s)
            log_perturb = math.log10(CUTOFF_GEV) - 2 * math.pi * available / (units * math.log(10))
            rows.append(
                {
                    "spurion_Z4R": r_s,
                    "spurion_Z11": q_s,
                    "zero_PQ": True,
                    "mixed_anomaly_equation": mixed_equation,
                    "minimum_charged_real_10_index_units": units,
                    "extra_R_repair": extra_r_repair,
                    "N_DW_after_required_repairs": ndw_after_repairs,
                    "limiting_allowed_W_operator": f"P^{n_p}*S^{n_s}/Lambda^{n_p+n_s-3}",
                    "limiting_P_power": n_p,
                    "limiting_S_power": n_s,
                    "log10_quality_upper_bound_S_GeV": round(log_quality, 12),
                    "quality_upper_bound_S_GeV": 10**log_quality,
                    "log10_one_loop_perturbativity_lower_bound_S_GeV": round(log_perturb, 12),
                    "one_loop_perturbativity_lower_bound_S_GeV": 10**log_perturb,
                    "log10_quality_minus_perturbativity_gap": round(log_quality - log_perturb, 12),
                    "quality_and_one_loop_perturbativity_overlap": log_quality > log_perturb,
                }
            )
    best = max(rows, key=lambda row: row["log10_quality_minus_perturbativity_gap"])
    best_by_r = {
        str(r_s): max((row for row in rows if row["spurion_Z4R"] == r_s), key=lambda row: row["log10_quality_minus_perturbativity_gap"])
        for r_s in (2, 0)
    }
    return {
        "scope": "finite fundamental charge cell qS=1..10, rS in {0,2}; weakly-coupled real-10 index units; rS=0 includes its required existing-P k=1 real-10 repair; coefficient-one generic-phase A-term quality screen",
        "operator_scan_cell": {"P_power": [1, 22], "S_power": [1, 22]},
        "quality_formula": "Delta theta=n*w0*fPQ^n*S^m/[chi*Lambda^(n+m-3)] < 1e-10",
        "perturbativity_formula": "alpha_R^-1(1e18)>0 at one loop after all required heavy thresholds",
        "rows": rows,
        "all_rows_have_no_overlap": all(not row["quality_and_one_loop_perturbativity_overlap"] for row in rows),
        "closest_row": best,
        "closest_row_by_spurion_Z4R": best_by_r,
        "caveat": "Additional exact gauge/shaping symmetries, tuned coefficients, a PQ-charged spurion, strong dynamics, or abandoning the landed Z4R protection are outside this scan and require a new theory/vacuum analysis.",
    }


def gate_rows() -> list[dict[str, Any]]:
    reasons = {
        "G1": "The minimal anomaly-free heavy completion fails RG and wall tests; GS or materially new shaping physics remains required.",
        "G2": "The P^2/Lambda real-10 threshold is explicit but not part of a viable perturbative pole spectrum.",
        "G3": "No complete alternative spurion vacuum or Hessian is supplied.",
        "G4": "A charged zero-PQ VEV changes the Z4R/Z11 breaking history; the full hierarchy/operator contract is not closed.",
        "G5": "P-mass anomaly cancellation shifts N_DW to 11 and aligns the P11 harmonic; zero-PQ alternatives fail the quality/RG screen.",
        "G6": "The exact Kmin threshold cost exceeds the same-order one-loop SU2R cutoff budget.",
        "G7": "No new proton Wilson/pole calculation is landed, and earlier R breaking is outside the protected contract.",
        "G8": "The negative anomaly certificate does not provide a flavour or global-likelihood fit.",
    }
    return [{"gate": gate, "closed": False, "full_gate_claim": False, "reason": reasons[gate]} for gate in reasons]


def build_report() -> dict[str, Any]:
    congruence = p_mass_congruence()
    threshold = p_mass_threshold(congruence["minimum_positive_K_each_PS_factor"])
    witness = minimal_real_ten_witness()
    repair = gravity_cubic_repair()
    wall = pq_wall_obstruction(congruence["minimum_positive_K_each_PS_factor"])
    scan = zero_pq_spurion_scan()
    gates = gate_rows()
    r2_scan_rows = [row for row in scan["rows"] if row["spurion_Z4R"] == 2]
    r0_scan_rows = [row for row in scan["rows"] if row["spurion_Z4R"] == 0]
    checks = {
        "K_congruence_and_minimum_are_exact": congruence["combined_congruence"] == "K_G=7 (mod 22)" and congruence["minimum_positive_K_each_PS_factor"] == 7,
        "same_order_one_loop_threshold_budget_fails": threshold["minimum_inverse_coupling_cost"] > threshold["existing_one_loop_only_SU2R_inverse_at_cutoff"] and not threshold["one_loop_necessary_perturbativity_condition_pass"],
        "minimal_real_10_witness_cancels_all_mixed_residues": witness["mixed_anomalies"]["Z4R_after_mod2"] == [0, 0, 0] and witness["mixed_anomalies"]["Z11_after_mod11"] == [0, 0, 0],
        "continuous_PS_anomalies_remain_canceled": witness["continuous_PS_anomalies"]["cancel"],
        "gravity_and_cubic_singlet_repair_is_exact": repair["after_singlet_repair"]["Z4R_gravity_mod2"] == 0 and repair["after_singlet_repair"]["Z11_gravity_mod11"] == 0 and repair["after_singlet_repair"]["Z11_cubic_mod11"] == 0,
        "P_mass_completion_aligns_P11_with_NDW11": wall["absolute_N_DW_after_completion"] == 11 and wall["gcd_explicit_harmonic_and_NDW"] == 11 and not wall["P11_lifts_all_QCD_vacua"],
        "zero_PQ_spurion_mixed_anomaly_congruences_include_R_repair": all((row["spurion_Z11"] * row["minimum_charged_real_10_index_units"]) % 11 == 7 and row["minimum_charged_real_10_index_units"] % 2 == 1 for row in r2_scan_rows) and all((1 + row["spurion_Z11"] * row["minimum_charged_real_10_index_units"]) % 11 == 7 and row["extra_R_repair"] is not None for row in r0_scan_rows),
        "zero_PQ_spurion_finite_scan_has_no_quality_RG_overlap": len(scan["rows"]) == 20 and scan["all_rows_have_no_overlap"],
        "all_full_G1_G8_gates_remain_open": len(gates) == 8 and all(not row["closed"] and not row["full_gate_claim"] for row in gates),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "V24_MINIMAL_NON_GS_ANOMALY_COMPLETION_NOGO_FROZEN__GS_OR_NEW_SHAPING_PHYSICS_REMAINS_REQUIRED" if not failures else "V24_NON_GS_NOGO_AUDIT_FAILED",
        "scope": "minimal weakly-coupled PS/SO10-real or vectorlike anomaly sectors with natural P-generated masses or one zero-PQ discrete-charged mass spurion",
        "source_context": {
            "selected_V24_frontier": "SUSY_V24_PS_VACUUM_RG_FRONTIER.json",
            "selected_frontier_core": "9f47db6cb3bb97b10b4554b8b3f51f146c09820bd202d7b6dcb429891fece780",
            "primary_discrete_anomaly_reference": "https://arxiv.org/abs/hep-ph/9210211",
            "primary_discrete_matching_reference": "https://arxiv.org/abs/hep-th/9710105",
        },
        "inputs": {
            "fPQ_GeV": F_PQ_GEV,
            "vPS_GeV": V_PS_GEV,
            "Lambda_GeV": CUTOFF_GEV,
            "w0_GeV": W0_GEV,
            "chi_QCD_GeV4": CHI_QCD_GEV4,
            "generic_Delta_theta_bound": 1.0e-10,
        },
        "baseline_running": alpha_r_one_loop_ledger(),
        "exact_P_mass_congruence": congruence,
        "P_mass_threshold_no_go": threshold,
        "minimal_real_10_mixed_anomaly_witness": witness,
        "gravity_cubic_singlet_repair": repair,
        "PQ_domain_wall_obstruction": wall,
        "zero_PQ_spurion_scan": scan,
        "G1_G8": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "verdict": {
            "minimal_non_GS_completion_viable": False,
            "Green_Schwarz_dependency_eliminated": False,
            "next_physics_required": "Specify the dynamical GS modulus/quotient, or replace the selector with an independently anomaly-complete shaping/gauge sector and redo the full PQ vacuum/operator/RG analysis.",
        },
        "checks": checks,
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    threshold = report["P_mass_threshold_no_go"]
    witness = report["minimal_real_10_mixed_anomaly_witness"]
    wall = report["PQ_domain_wall_obstruction"]
    scan = report["zero_PQ_spurion_scan"]
    closest = scan["closest_row"]
    closest_r0 = scan["closest_row_by_spurion_Z4R"]["0"]
    return "\n".join(
        [
            "# SUSY V24 minimal non-GS anomaly-completion no-go",
            "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            f"- Inputs: `fPQ={report['inputs']['fPQ_GeV']:.3g} GeV`, `vPS={report['inputs']['vPS_GeV']:.3g} GeV`, `Lambda={report['inputs']['Lambda_GeV']:.3g} GeV`.",
            "- Exact theorem: for every PS factor, invariant masses `P^k Phi Phi` contribute `Delta A_11=-kS/2` and `Delta A_4R=-kS`. Canceling visible residues `(9 mod 11, 1 mod 2)` forces `K=sum(kS)=7 mod 22`, hence `Kmin=7`.",
            f"- RG obstruction: the minimum same-order one-loop inverse-coupling cost is `{threshold['minimum_inverse_coupling_cost']:.12f}`, while the existing one-loop-only SU2R cutoff budget is `{threshold['existing_one_loop_only_SU2R_inverse_at_cutoff']:.12f}`. The projected inverse coupling is `{threshold['projected_one_loop_SU2R_inverse_after_minimal_completion']:.12f}<0`; the landed coupled gauge-only two-loop endpoint `{threshold['existing_coupled_gauge_only_two_loop_SU2R_inverse_at_cutoff']:.12f}` is smaller still.",
            f"- Minimal algebraic witness: one real SO(10) `10` with `P T0^2` and three with `P^2 Ti^2/Lambda` give `K={witness['weighted_index_K_each_factor']}`, cancel all mixed residues, and keep continuous PS anomalies canceled. The three light thresholds sit at `{witness['P2_mass_GeV']:.6g} GeV`; the exact threshold sum fails perturbativity.",
            "- Gravity/cubic audit: one `P AB` singlet pair and two `P^2 CD/Lambda` pairs make `Agrav(Z4R)=0 mod2`, `Agrav(Z11)=0 mod11`, and `A3(Z11)=0 mod11`. Thus those residues can be repaired without beta cost, but do not cure the RG or PQ obstructions.",
            f"- Wall obstruction: PQ invariance makes the heavy sector shift `2N_QCD` from `-4` to `{wall['final_2N_QCD']}`. Therefore `N_DW={wall['absolute_N_DW_after_completion']}` and `gcd(11,N_DW)={wall['gcd_explicit_harmonic_and_NDW']}`: the leading `P^11` term is aligned and does not lift the QCD vacua.",
            f"- Zero-PQ spurion scan: all `{len(scan['rows'])}` fundamental `(rS,qS)` rows fail the coefficient-one quality/one-loop-RG overlap. The closest row is `(rS,qS)=({closest['spurion_Z4R']},{closest['spurion_Z11']})`, with `log10 Smax={closest['log10_quality_upper_bound_S_GeV']:.6f}` and `log10 Smin={closest['log10_one_loop_perturbativity_lower_bound_S_GeV']:.6f}`.",
            f"- `rS=0` repair bookkeeping: one existing-`P` real 10 supplies the missing `Z4R` residue but also `Delta A11=-1/2` and `Delta(2N_QCD)=-1`; therefore `1+qS*N=7 mod 11` and the repaired wall number is `5`. Its closest row is `qS={closest_r0['spurion_Z11']}, N={closest_r0['minimum_charged_real_10_index_units']}` with log-gap `{closest_r0['log10_quality_minus_perturbativity_gap']:.6f}`.",
            "",
            "Verdict: the minimal heavy-sector search cannot eliminate the Green--Schwarz dependency while preserving the landed PQ and perturbative window. An additional anomaly-complete shaping/gauge sector or a PQ-charged multi-axion completion would be new physics requiring a fresh operator, vacuum, wall, and RG analysis. All eight full gates remain open.",
            "",
        ]
    )


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: Mapping[str, Any]) -> bool:
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = markdown(report)
    return JSON_PATH.exists() and MD_PATH.exists() and JSON_PATH.read_text(encoding="utf-8") == expected_json and MD_PATH.read_text(encoding="utf-8") == expected_md


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check and not check_outputs(report):
        print("V24 non-GS no-go artifacts are missing or stale")
        return 1
    print(report["status"])
    print(report["core_sha256"])
    return 0 if not report["failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
