#!/usr/bin/env python3
"""Fail-closed V26 attempt to complete the V24 Pati--Salam G1 gate.

The certificate constructs the strongest explicit four-dimensional Green--
Schwarz completion presently supported by the source.  Three hidden pure-SYM
sectors have exact mixed-discrete anomaly congruences and generate a
three-exponential racetrack.  The racetrack has an exact supersymmetric
Minkowski stationary point with both real modulus components massive.

This is a dynamical EFT completion, not a microscopic UV completion.  The
integer levels, condensate prefactors, branch quotient, all-order normalized
operator basis, Kahler matching, and soft matching are not derived from a
compactification or other UV source.  The full G1 result therefore remains
fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.json"
MD_PATH = ROOT / "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.md"

STATUS = (
    "V26_G1_DYNAMICAL_GS_EFT_CONSTRUCTED__MODULUS_STABILIZED__"
    "HIDDEN_ANOMALIES_MATCH__MICROSCOPIC_UV_AND_WILSON_MATCHING_OPEN__"
    "FULL_G1_NOT_CLOSED"
)

SOURCE_PINS = {
    "susy_v25_g1_g3_completion_frontier.py":
        "51833f307b05d13ae828cab3dec5922795e80b7d56187c554367692a079db638",
    "SUSY_V25_G1_G3_COMPLETION_FRONTIER.json":
        "08c25dbd3b978dc28746f87c8ff0cb89aae3fab5346dad61c8230da63717f027",
    "SUSY_V25_G1_G3_COMPLETION_FRONTIER.md":
        "bc926ce92a4b85f6ff3527660daafee4f1fd45435ab67c1ca10333fc5e3830e6",
    "susy_v24_ps_source_contract.py":
        "4993924ebf64a8eb05f83290174adaffe277342234d1ae43e78d992b3efbf4da",
    "SUSY_V24_PS_SOURCE_CONTRACT.json":
        "c2457e188877a2729e092acf6ddbf76626b884a4c1cb652c282da215f268ce51",
    "models/PSZ4RZ11SUSYV24/PSZ4RZ11SUSYV24.m":
        "09326668d02b32b4a66c3b79cba34fb6a709430a360dce6d2d5d2ab039cad2bf",
}

UPSTREAM_CORES = {
    "v24_source": "d408aa7d7d3096ac917f5bd6f4f37576aace4cd78709bf4810b8e036dc2d93a8",
    "v25_frontier": "5aa1d0bffd39fa3a520105291d95906882842fd185e85cae72b519b03528e307",
}

PRIMARY_SOURCES = [
    {
        "topic": "visible Pati--Salam source architecture",
        "citation": "Kawamura and Raby, 2020",
        "url": "https://arxiv.org/abs/2009.04582",
    },
    {
        "topic": "discrete R anomalies and Green--Schwarz cancellation",
        "citation": "Dine and Monteux, 2012",
        "url": "https://arxiv.org/abs/1212.4371",
    },
    {
        "topic": "gaugino condensation with field-dependent gauge couplings",
        "citation": "Burgess, Derendinger, Quevedo, and Quiros, 1995",
        "url": "https://arxiv.org/abs/hep-th/9505171",
    },
    {
        "topic": "supersymmetric Minkowski racetrack stabilization",
        "citation": "Blanco-Pillado, Kallosh, and Linde, 2005",
        "url": "https://arxiv.org/abs/hep-th/0511042",
    },
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative, expected in SOURCE_PINS.items():
        path = ROOT / relative
        actual = sha256_file(path) if path.exists() else None
        rows.append(
            {
                "path": relative,
                "mode": "raw",
                "expected_sha256": expected,
                "sha256": actual,
                "matches": actual == expected,
            }
        )
    return rows


def gs_quotient_ledger() -> dict[str, Any]:
    # theta has period one.  In denominator 22 units the two shifts are
    # -11/22 and -18/22.  gcd(22,11,18)=1, so their generated translation
    # lattice has elementary step 1/22.
    denominator = 22
    shift_units = (-11, -18)
    lattice_gcd = math.gcd(denominator, math.gcd(abs(shift_units[0]), abs(shift_units[1])))
    elementary_step = Fraction(lattice_gcd, denominator)

    allowed_exponents = [
        n
        for n in range(1, 122)
        if n % 2 == 1 and n % 11 == 0
    ]
    return {
        "field": "T=t+i theta_GS",
        "theta_period": 1,
        "Kahler_shift_invariant_form": "K_GS=-log(T+Tdag)",
        "discrete_shifts_mod_period": {
            "Z4R": "-1/2",
            "Z11": "-9/11",
        },
        "common_denominator_22_shift_units": list(shift_units),
        "generated_translation_lattice_gcd": lattice_gcd,
        "physical_quotient_elementary_step": str(elementary_step),
        "exponential_convention": "E_n(T)=exp(-2*pi*n*T)",
        "superpotential_covariance_conditions": {
            "Z4R_target_charge_2": "n odd",
            "Z11_target_charge_0": "n=0 mod 11",
            "combined": "n=11 mod 22",
        },
        "allowed_positive_exponents_through_121": allowed_exponents,
        "first_three_allowed_exponents": allowed_exponents[:3],
        "relative_harmonics_for_first_three": [
            allowed_exponents[1] - allowed_exponents[0],
            allowed_exponents[2] - allowed_exponents[1],
        ],
        "relative_harmonic_matches_quotient_order": (
            allowed_exponents[1] - allowed_exponents[0] == denominator
        ),
    }


def hidden_sector_ledger() -> dict[str, Any]:
    # With W_cond ~ exp[-2*pi*(k/N)*T], the chosen level/rank ratios give
    # the first three symmetry-covariant exponents 11, 33, and 55.
    definitions = (
        (2, 22, 11, 2),
        (3, 99, 33, -16),
        (5, 275, 55, 32),
    )
    rows: list[dict[str, Any]] = []
    for rank, level, exponent, prefactor in definitions:
        rows.append(
            {
                "gauge_group": f"SU({rank})_h",
                "rank_N": rank,
                "pure_SYM": True,
                "one_loop_b0": 3 * rank,
                "asymptotically_free": 3 * rank > 0,
                "topological_level_k": level,
                "condensate_exponent_k_over_N": level // rank,
                "target_exponent": exponent,
                "racetrack_prefactor_in_M3_units": prefactor,
                "Z4R_mixed_anomaly_representative": rank,
                "Z4R_mixed_anomaly_mod_eta2": rank % 2,
                "Z4R_level_times_rho_mod_eta2": level % 2,
                "Z4R_mixed_GS_congruence": rank % 2 == level % 2,
                "Z11_mixed_anomaly_representative": 0,
                "Z11_mixed_anomaly_mod11": 0,
                "Z11_level_times_rho9_mod11": (9 * level) % 11,
                "Z11_mixed_GS_congruence": (9 * level) % 11 == 0,
                "R_gaugino_gravitational_contribution": rank * rank - 1,
                "number_of_pure_SYM_condensate_branches": rank,
            }
        )

    hidden_grav_r = sum(row["R_gaugino_gravitational_contribution"] for row in rows)
    visible_grav_r = 20
    # T has affine scalar shifts but R charge zero as a chiral superfield;
    # its modulino therefore carries fermion R charge -1.  Under the non-R
    # Z11 shift the modulino is neutral.
    modulus_grav_r = -1
    visible_grav_z11 = -15
    return {
        "condensate_convention": "W_h=N Lambda_h^3 proportional to exp[-2*pi*(k/N)*T] on a selected branch",
        "sectors": rows,
        "all_hidden_mixed_GS_congruences_match": all(
            row["Z4R_mixed_GS_congruence"] and row["Z11_mixed_GS_congruence"]
            for row in rows
        ),
        "gravitational_anomaly_audit": {
            "visible_Z4R_representative": visible_grav_r,
            "hidden_Z4R_gaugino_contribution": hidden_grav_r,
            "GS_modulino_Z4R_contribution": modulus_grav_r,
            "combined_Z4R_mod_eta2": (
                visible_grav_r + hidden_grav_r + modulus_grav_r
            ) % 2,
            "required_24rho_mod_eta2": 0,
            "Z4R_gravitational_GS_congruence": (
                (visible_grav_r + hidden_grav_r + modulus_grav_r) % 2 == 0
            ),
            "visible_Z11_representative": visible_grav_z11,
            "hidden_Z11_gaugino_contribution": 0,
            "GS_modulino_Z11_contribution": 0,
            "combined_Z11_mod11": visible_grav_z11 % 11,
            "required_24rho_mod11": (24 * 9) % 11,
            "Z11_gravitational_GS_congruence": (
                visible_grav_z11 % 11 == (24 * 9) % 11
            ),
        },
        "raw_condensate_branch_product": math.prod(row["number_of_pure_SYM_condensate_branches"] for row in rows),
        "residual_matter_parity": {
            "gaugino_bilinear_Z4R_charge": 2,
            "condensates_break_Z4R_to_Z2": True,
            "hidden_gauge_fields_are_visible_matter_parity_even": True,
            "P_VEV_and_condensates_preserve_the_same_Z2": True,
        },
        "important_boundary": (
            "the selected condensate branch is explicit, but the full Veneziano--Yankielowicz "
            "composite branch quotient and threshold determinants have not been derived"
        ),
    }


def racetrack_stabilization_ledger() -> dict[str, Any]:
    # Set z=exp(-22*pi*t0)=1/2.  At real T=t0, the three W contributions
    # are exactly (1,-2,1) M^3.  Their first derivatives also cancel, while
    # W_TT/M^3=3872*pi^2 is nonzero.
    contributions = (1, -2, 1)
    angular_coefficients = (22, 66, 110)  # a_i/pi
    w_value = sum(contributions)
    wt_over_minus_pi = sum(a * c for a, c in zip(angular_coefficients, contributions))
    wtt_over_pi2 = sum(a * a * c for a, c in zip(angular_coefficients, contributions))
    return {
        "Planck_units": True,
        "modulus": "T=t+i theta_GS",
        "Kahler_potential": "K=-log(T+Tdag)",
        "gauge_kinetic_functions": (
            "f_a=f_a0+k_a*T with positive real constants f_a0; the constants set "
            "physical couplings and are absorbed into condensate prefactors"
        ),
        "superpotential": (
            "W_GS=M^3[2 exp(-22*pi*T)-16 exp(-66*pi*T)+32 exp(-110*pi*T)]"
        ),
        "exact_stationary_point": "T0=log(2)/(22*pi), Im(T0)=0 modulo the discrete gauge quotient",
        "exp_minus_22pi_T0": "1/2",
        "term_values_over_M3_at_T0": list(contributions),
        "W_over_M3_at_T0": w_value,
        "W_T_over_minus_pi_M3_at_T0": wt_over_minus_pi,
        "W_TT_over_pi2_M3_at_T0": wtt_over_pi2,
        "D_T_W_at_T0": 0,
        "F_term_potential_at_T0": 0,
        "spacetime": "supersymmetric Minkowski",
        "K_T_Tdag_at_T0": "(2 Re T0)^-2 > 0",
        "canonically_normalized_real_scalar_mass_squared": (
            "m_T^2=(2 Re T0)^3 |3872*pi^2*M^3|^2 > 0"
        ),
        "both_real_modulus_components_locally_massive": wtt_over_pi2 != 0,
        "dynamical_GS_modulus_stabilization_closed_at_selected_4D_EFT_branch": True,
    }


def all_order_operator_grammar() -> dict[str, Any]:
    return {
        "chiral_field_multidegree": "n=(n_H,...,n_N) in nonnegative integers^13",
        "constructive_PS_tensor_alphabet": {
            "SU4": [
                "delta^a_b",
                "epsilon_abcd",
                "epsilon^abcd",
                "Sigma_[ab] realization of the 6",
            ],
            "SU2L": ["epsilon_alpha_beta"],
            "SU2R": ["epsilon_dotalpha_dotbeta"],
        },
        "holomorphic_spanning_rule": (
            "expand every 6 as an antisymmetric pair, contract every gauge index with the "
            "listed delta/epsilon tensors, impose identical-superfield symmetrization and "
            "flavor tensors, then retain sum(r_i n_i)=2 mod4 and sum(z_i n_i)=0 mod11"
        ),
        "superpotential_form": (
            "W=sum_[n,a] c_[n,a] I_[n,a]/Lambda^(|n|-3), including nonnegative powers "
            "and the GS exponentials E_(11+22j)(T) with the same selector covariance"
        ),
        "kahler_spanning_rule": (
            "repeat the tensor construction for chiral and antichiral indices, retain total "
            "Z4R and Z11 charge zero, and pair coefficients to make K Hermitian"
        ),
        "gauge_kinetic_spanning_rule": (
            "holomorphic PS singlets of selector charge (0,0) multiply W_alpha W_alpha; "
            "the universal shifting term is k_a*T*W_alpha^a W_alpha^a"
        ),
        "soft_spurion_rule": (
            "once a mediation spurion and its charges are supplied, insert it into the same "
            "D-term and F-term contraction grammar"
        ),
        "critical_slice_exact_subgrammar_from_V25": (
            "Wcrit=X Lambda^2 F(Sbc Sc/Lambda^2,X^2/Lambda^2)"
        ),
        "grammar_is_all_order_and_constructive": True,
        "independent_normalized_basis_and_syzygy_reducer_implemented_at_all_orders": False,
        "wilson_coefficients_derived_from_hidden_or_microscopic_UV": False,
        "kahler_and_soft_matching_derived": False,
        "boundary": (
            "the tensor alphabet spans the invariant ring, but it is not the requested "
            "UV-matched independent normalized operator/tensor contract"
        ),
    }


def gate_ledger(
    quotient: dict[str, Any],
    hidden: dict[str, Any],
    racetrack: dict[str, Any],
    operators: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gate": "G1",
        "qualified_id": "research.susy_pati_salam.v26.G1.full_closure",
        "closed": False,
        "full_gate_claim": False,
        "state": (
            "DYNAMICAL_GS_EFT_AND_LOCAL_MODULUS_STABILIZATION_LANDED__"
            "MICROSCOPIC_UV_OPERATOR_MATCHING_OPEN"
        ),
        "new_evidence_landed": [
            "exact Z4R x Z11 axion quotient with elementary shift 1/22",
            "three hidden pure-SYM mixed and gravitational anomaly congruences",
            "exact symmetry-covariant triple racetrack",
            "supersymmetric Minkowski stationary point with two positive modulus masses",
            "hidden condensates preserve the visible residual Z2 matter parity",
            "constructive all-order PS invariant tensor grammar",
        ],
        "open_requirements": [
            "microscopic origin of T and of visible/hidden integer topological levels",
            "UV derivation of condensate prefactors, threshold determinants, and the full hidden branch quotient",
            "microscopic pure-discrete/cubic anomaly and local-counterterm audit",
            "independent normalized all-order operator basis with syzygies",
            "UV-matched Wilson, Kahler, gauge-kinetic, and soft coefficients",
        ],
        "qualified_dynamical_GS_EFT_subgate_closed": all(
            [
                quotient["physical_quotient_elementary_step"] == "1/22",
                hidden["all_hidden_mixed_GS_congruences_match"],
                hidden["gravitational_anomaly_audit"]["Z4R_gravitational_GS_congruence"],
                hidden["gravitational_anomaly_audit"]["Z11_gravitational_GS_congruence"],
                hidden["residual_matter_parity"]["P_VEV_and_condensates_preserve_the_same_Z2"],
                racetrack["both_real_modulus_components_locally_massive"],
            ]
        ),
        "full_G1_closure_blocked_by_missing_UV_data": not all(
            [
                operators["independent_normalized_basis_and_syzygy_reducer_implemented_at_all_orders"],
                operators["wilson_coefficients_derived_from_hidden_or_microscopic_UV"],
                operators["kahler_and_soft_matching_derived"],
            ]
        ),
    }


def build_report() -> dict[str, Any]:
    manifest = source_manifest()
    quotient = gs_quotient_ledger()
    hidden = hidden_sector_ledger()
    racetrack = racetrack_stabilization_ledger()
    operators = all_order_operator_grammar()
    gate = gate_ledger(quotient, hidden, racetrack, operators)

    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in manifest),
        "V25_core_matches": json.loads(
            (ROOT / "SUSY_V25_G1_G3_COMPLETION_FRONTIER.json").read_text(encoding="utf-8")
        )["core_sha256"] == UPSTREAM_CORES["v25_frontier"],
        "V24_source_core_matches": json.loads(
            (ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json").read_text(encoding="utf-8")
        )["core_sha256"] == UPSTREAM_CORES["v24_source"],
        "GS_quotient_elementary_step_is_1_over_22": quotient["physical_quotient_elementary_step"] == "1/22",
        "first_three_covariant_exponents_are_11_33_55": quotient["first_three_allowed_exponents"] == [11, 33, 55],
        "all_hidden_sectors_are_asymptotically_free": all(row["asymptotically_free"] for row in hidden["sectors"]),
        "hidden_level_rank_ratios_match_racetrack_exponents": all(
            row["condensate_exponent_k_over_N"] == row["target_exponent"]
            for row in hidden["sectors"]
        ),
        "all_hidden_mixed_anomaly_congruences_match": hidden["all_hidden_mixed_GS_congruences_match"],
        "combined_gravitational_congruences_match": all(
            [
                hidden["gravitational_anomaly_audit"]["Z4R_gravitational_GS_congruence"],
                hidden["gravitational_anomaly_audit"]["Z11_gravitational_GS_congruence"],
            ]
        ),
        "racetrack_W_and_WT_vanish_exactly": (
            racetrack["W_over_M3_at_T0"] == 0
            and racetrack["W_T_over_minus_pi_M3_at_T0"] == 0
        ),
        "racetrack_WTT_is_nonzero_3872_pi2": racetrack["W_TT_over_pi2_M3_at_T0"] == 3872,
        "both_modulus_components_are_locally_massive": racetrack["both_real_modulus_components_locally_massive"],
        "residual_Z2_matter_parity_is_preserved": hidden["residual_matter_parity"]["P_VEV_and_condensates_preserve_the_same_Z2"],
        "qualified_dynamical_GS_EFT_subgate_is_closed": gate["qualified_dynamical_GS_EFT_subgate_closed"],
        "full_G1_remains_fail_closed": (
            gate["closed"] is False
            and gate["full_gate_claim"] is False
            and gate["full_G1_closure_blocked_by_missing_UV_data"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v26-g1-dynamical-gs-completion-attempt-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v26.g1_dynamical_gs_completion_attempt",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "primary_sources": PRIMARY_SOURCES,
        "GS_discrete_quotient": quotient,
        "hidden_condensation_and_anomaly_ledger": hidden,
        "exact_racetrack_stabilization": racetrack,
        "all_order_operator_grammar": operators,
        "G1_gate": gate,
        "closure_counts": {
            "full_G1_closed": 0,
            "full_G1_open": 1,
            "qualified_dynamical_GS_EFT_subgates_closed": int(
                gate["qualified_dynamical_GS_EFT_subgate_closed"]
            ),
        },
        "terminal_decision": {
            "continue_attempt_completed": True,
            "new_dynamical_GS_EFT_candidate_created": True,
            "candidate_is_mathematically_consistent_at_declared_scope": not failures,
            "candidate_is_a_microscopic_UV_completion": False,
            "full_G1_can_be_closed_now": False,
            "stop_reason": (
                "a 4D anomaly-matched stabilized racetrack can be constructed, but no microscopic "
                "source derives its levels, threshold prefactors, branch quotient, or the visible "
                "all-order Wilson/Kahler/soft data"
            ),
            "honest_next_input_if_reopened": (
                "an explicit compactification or other UV-complete source whose massless spectrum, "
                "levels, selection rules, moduli stabilization, and threshold matching reproduce this ledger"
            ),
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    quotient = report["GS_discrete_quotient"]
    hidden = report["hidden_condensation_and_anomaly_ledger"]
    racetrack = report["exact_racetrack_stabilization"]
    gate = report["G1_gate"]
    lines = [
        "# SUSY V26 G1 dynamical Green--Schwarz completion attempt",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full G1 closed: **no**.",
        f"- Qualified dynamical GS EFT subgate closed: **{str(gate['qualified_dynamical_GS_EFT_subgate_closed']).lower()}**.",
        "",
        "## New result",
        "",
        "A dynamical four-dimensional completion of the previously topological-only GS term now exists at a precise EFT scope. With `theta_GS` of period one, the `Z4R` and `Z11` shifts generate the elementary quotient translation `1/22`. A superpotential exponential `exp(-2*pi*n*T)` is covariant only for `n=11 mod 22`; the first three choices are `11, 33, 55`.",
        "",
        "Three hidden pure-SYM groups realize those exponents in the declared condensation convention: `SU(2)_h` at level 22, `SU(3)_h` at level 99, and `SU(5)_h` at level 275. Every hidden `Z4R` and `Z11` mixed anomaly congruence matches the same GS shifts. Their R-gravitational contribution is 35; including the R-neutral chiral modulus's charge-minus-one modulino gives `20+35-1=54`, so the visible + hidden + modulus congruence remains matched. The condensates break `Z4R` only to the same residual `Z2` matter parity.",
        "",
        "The exact racetrack is",
        "",
        f"`{racetrack['superpotential']}`.",
        "",
        "At `T0=log(2)/(22*pi)` its three terms are exactly `(1,-2,1) M^3`, so `W=0` and `W_T=0`, while `W_TT=3872*pi^2 M^3`. With `K=-log(T+Tdag)`, this is a supersymmetric Minkowski point and both canonically normalized real modulus components have strictly positive mass squared.",
        "",
        "## Why full G1 still does not close",
        "",
        "This construction is a consistent 4D dynamical GS/racetrack EFT, not a microscopic UV realization. No compactification or other fundamental source has been supplied that derives the integer levels, the condensate threshold prefactors `(2,-16,32)`, or the quotient of all `2*3*5=30` pure-SYM branches. Those quantities are inputs here.",
        "",
        "The all-order PS tensor grammar is now stated constructively using the `SU(4)` delta/epsilon tensors, the antisymmetric realization of the 6, and the two `SU(2)` epsilon tensors, followed by the exact `Z4R x Z11` filters. But an independent normalized all-order basis and syzygy reducer is not implemented, and the Wilson, Kahler, gauge-kinetic, and soft coefficients are not UV matched. The pure-discrete/cubic anomaly is likewise UV-sensitive and has no microscopic counterterm audit. The V25 arbitrary driver function therefore remains genuine input data.",
        "",
        "## Decision",
        "",
        "The plausible dynamical route was executed and passes every internal check, but it does not satisfy the repository's microscopic-UV G1 definition. Full G1 remains open. Closing it would require an explicit UV source reproducing the spectrum, levels, selectors, stabilized moduli, branch quotient, and all-order matching; inventing those data would not be a physics solution.",
        "",
        "Primary references: [Kawamura--Raby PS model](https://arxiv.org/abs/2009.04582), [discrete R anomalies and GS cancellation](https://arxiv.org/abs/1212.4371), [field-dependent gaugino condensation](https://arxiv.org/abs/hep-th/9505171), and [supersymmetric racetrack stabilization](https://arxiv.org/abs/hep-th/0511042).",
        "",
        f"Finite quotient regression: first exponents `{quotient['first_three_allowed_exponents']}`. Hidden raw branch count: `{hidden['raw_condensate_branch_product']}`.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any]) -> bool:
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    return (
        JSON_PATH.exists()
        and MD_PATH.exists()
        and JSON_PATH.read_text(encoding="utf-8") == expected_json
        and MD_PATH.read_text(encoding="utf-8") == expected_md
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check and (report["n_failed"] or not check_outputs(report)):
        print(
            json.dumps(
                {
                    "failures": report["failures"],
                    "frozen_outputs_match": check_outputs(report),
                }
            )
        )
        return 1
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
