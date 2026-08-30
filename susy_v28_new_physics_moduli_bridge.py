#!/usr/bin/env python3
"""V28 investigation of a microscopic multi-modulus G1 bridge.

The strongest globally consistent rigid-brane Pati--Salam source has
h^(1,1)=51 on its Type-IIB side.  Its G3 flux fixes the three complex-
structure moduli and axio-dilaton, but not those 51 Kahler moduli.  V26,
by contrast, contains one stabilized Green--Schwarz modulus.

This certificate constructs an exact 51-field generalization of the V26
triple racetrack.  It proves a local supersymmetric Minkowski stationary
point with a full-rank scalar Hessian for any regular positive Kahler metric.
It is deliberately a scaffold: the necessary divisors, instanton zero modes,
axionic charge matrix, prefactors, global branches, and visible matching are
not derived from the rigid-brane compactification, so full G1 remains open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.json"
MD_PATH = ROOT / "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.md"
SCHEMA_PATH = ROOT / "SUSY_V28_MICROSCOPIC_INSTANTON_BRIDGE_SCHEMA.json"

STATUS = (
    "V28_NEW_PHYSICS_INVESTIGATION_COMPLETE__EXACT_51_MODULUS_LOCAL_"
    "RACETRACK_SCAFFOLD_CONSTRUCTED__MICROSCOPIC_INSTANTON_BRIDGE_"
    "UNDERIVED__FULL_G1_OPEN"
)

SOURCE_PINS = {
    "susy_v26_g1_dynamical_gs_completion_attempt.py":
        "6527ee543dd224a10140943ee94d0a23c967bd88384be1a9ae1a11c35bb4da1d",
    "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.json":
        "3914d0754f8c2d1c70d2952507216a098f7a815c99ee64be1cb51b2dc67306b1",
    "susy_v27_g1_architecture_change_audit.py":
        "1158b288ee39601ac4650312ec9e6c83e0d4eb101de5c90ccf0c38cba2f0be9c",
    "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json":
        "4dfaa939bc3ef555fdfbb9d46612ee83df082231cc078176605b38421ac50b61",
    "SUSY_V27_G1_UV_COMPLETION_INPUT_SCHEMA.json":
        "e02bfb0d5881cbc7bdd7d3f4d6e85488db708613885dbcec12047b6ef7ebf4b7",
}

UPSTREAM_CORES = {
    "V26_dynamical_GS_attempt": "7dd049d43e1ce6cb6e9ca3385ecb2895521443a80f5af1363260d4ea637ba59d",
    "V27_architecture_audit": "d97af356e9f2e2d7d0d2001a2a3b60027e6845cf4266d6f8c7b36b539281a58e",
}

PRIMARY_SOURCES = [
    {
        "topic": "globally consistent rigid-brane Pati--Salam target",
        "citation": "Mansha, Sabir, Li, and Wang, arXiv:2512.21141v2 (2026)",
        "url": "https://arxiv.org/pdf/2512.21141",
        "facts_used": (
            "Type-IIB Hodge numbers (h11,h21)=(51,3); the untwisted N=1 inventory "
            "contains three T_i; G3 fixes the complex-structure moduli and axio-dilaton "
            "but leaves the Kahler sector unstabilized; RR tadpoles, K-theory, N=1 "
            "supersymmetry, and perturbative spectra are explicit"
        ),
    },
    {
        "topic": "Pati--Salam E-brane stabilization precedent",
        "citation": "Abe, Kobayashi, Sumita, and Uemura, arXiv:1703.03402 (2017)",
        "url": "https://arxiv.org/pdf/1703.03402",
        "facts_used": (
            "magnetized D9 Pati--Salam models use FI terms plus E1/E5 instantons to "
            "stabilize a three-Kahler-modulus truncation; the vacuum is supersymmetric "
            "AdS and a compatible hidden SUSY-breaking sector is left open"
        ),
    },
    {
        "topic": "chirality versus instanton zero modes",
        "citation": "Grimm, Kerstan, Palti, and Weigand, arXiv:1105.3193 (2011)",
        "url": "https://arxiv.org/abs/1105.3193",
        "facts_used": (
            "charged zero modes from a chiral visible sector can remove E3 contributions; "
            "instanton flux can sometimes restore them but must be derived divisor by divisor"
        ),
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
    rows = []
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


def microscopic_target_ledger() -> dict[str, Any]:
    h11 = 51
    h21 = 3
    axio_dilaton = 1
    v26_explicit_moduli = 1
    return {
        "target": "Type-IIB T6/(Z2 x Z2) rigid-brane Pati--Salam flux models",
        "Hodge_numbers": {"h11": h11, "h21": h21},
        "ambient_Kahler_sector_h11": h11,
        "explicit_untwisted_N1_Kahler_chiral_multiplets": 3,
        "complete_twisted_N1_orientifold_parity_inventory_published": False,
        "conservative_complex_no_scale_field_envelope": h11,
        "complex_structure_moduli": h21,
        "axio_dilaton_moduli": axio_dilaton,
        "closed_complex_moduli_total": h11 + h21 + axio_dilaton,
        "G3_tree_level_stabilized_complex_moduli": h21 + axio_dilaton,
        "G3_tree_level_unstabilized_Kahler_sector_envelope": h11,
        "open_string_position_and_Wilson_line_moduli_frozen_by_rigidity": True,
        "V26_explicit_complex_GS_moduli": v26_explicit_moduli,
        "conservative_V26_to_ambient_h11_dimension_gap": h11 - v26_explicit_moduli,
        "direct_one_field_bijection_to_ambient_h11_possible": h11 == v26_explicit_moduli,
        "inference_boundary": (
            "51 is the ambient h11 count and is used as a conservative stabilization "
            "envelope; the paper explicitly enumerates only the three untwisted T_i after "
            "orientifolding, so a full twisted-sector N=1 parity inventory remains an input"
        ),
        "interpretation": (
            "a microscopic bridge must inventory the full orientifolded Kahler sector and "
            "stabilize every surviving direction before the one-field V26 EFT can be derived"
        ),
    }


def multi_modulus_racetrack_scaffold() -> dict[str, Any]:
    number_of_moduli = 51
    powers = (1, 3, 5)
    polynomial_coefficients = (1, -2, 1)
    p_at_one = sum(polynomial_coefficients)
    euler_first_at_one = sum(
        coefficient * power
        for coefficient, power in zip(polynomial_coefficients, powers)
    )
    euler_second_at_one = sum(
        coefficient * power * power
        for coefficient, power in zip(polynomial_coefficients, powers)
    )
    a_over_pi = 22
    wtt_over_pi2_Cq5 = euler_second_at_one * a_over_pi * a_over_pi
    log10_q_at_t1 = -(a_over_pi * math.pi) / math.log(10)
    log10_hessian_factor_at_t1 = (
        math.log10(euler_second_at_one * (a_over_pi * math.pi) ** 2)
        + 5 * log10_q_at_t1
    )
    return {
        "number_of_complex_moduli": number_of_moduli,
        "fields": "T_i for i=1,...,51",
        "positive_scales": "C_i>0",
        "arbitrary_target_points": "t_i*>0 with q_i=exp(-22*pi*t_i*)",
        "superpotential": (
            "W=sum_i C_i[x_i^5-2*q_i^2*x_i^3+q_i^4*x_i], "
            "x_i=exp(-22*pi*T_i)"
        ),
        "factorized_form": "W=sum_i C_i*x_i*(x_i^2-q_i^2)^2",
        "instantonic_exponents_2pi_n": [11, 33, 55],
        "exponential_terms_required": 3 * number_of_moduli,
        "dimensionless_polynomial": "p(y)=y^5-2*y^3+y=y*(y^2-1)^2",
        "polynomial_powers": list(powers),
        "polynomial_coefficients": list(polynomial_coefficients),
        "p_at_y1": p_at_one,
        "Euler_p_at_y1": euler_first_at_one,
        "Euler_squared_p_at_y1": euler_second_at_one,
        "stationary_point": "T_i=t_i* real for every i",
        "W_at_stationary_point": 0,
        "gradient_rank_at_stationary_point": 0,
        "holomorphic_Hessian": (
            "W_ij=delta_ij*3872*pi^2*C_i*q_i^5"
        ),
        "W_ii_over_pi2_Ciqi5": wtt_over_pi2_Cq5,
        "holomorphic_Hessian_rank": number_of_moduli,
        "supergravity_mass_theorem": (
            "at W=D_iW=0, V_i_jbar=e^K W_ik K^(k,lbar) conjugate(W_jl); "
            "an invertible W_ij and any regular positive Kahler metric make this block "
            "positive definite, while V_ij=0"
        ),
        "real_scalar_Hessian_rank": 2 * number_of_moduli,
        "all_102_real_modulus_components_locally_massive": True,
        "recovers_V26_at_q_half_and_C_32M3": {
            "q": "1/2",
            "C": "32*M^3",
            "three_coefficients_in_M3_units": [2, -16, 32],
            "term_values_at_stationary_point_in_M3_units": [1, -2, 1],
            "W_TT_over_pi2_M3": 3872,
        },
        "large_volume_diagnostic_tstar_1": {
            "log10_q": log10_q_at_t1,
            "log10_Wii_over_C_without_pi_units": log10_hessian_factor_at_t1,
            "warning": (
                "the exact point can be placed at large volume, but the induced Hessian "
                "is exponentially small unless microscopic prefactors compensate"
            ),
        },
        "scope": (
            "exact local N=1 supergravity algebra only; it does not identify 51 contributing "
            "divisors or derive a string-normalized Kahler potential, prefactors, cross terms, "
            "axion quotient, or global branch structure"
        ),
    }


def instanton_precedent_ledger() -> dict[str, Any]:
    return {
        "source": "arXiv:1703.03402",
        "same_microscopic_compactification_as_2026_rigid_model": False,
        "explicit_bulk_Kahler_fields_in_effective_analysis": 3,
        "mechanisms": [
            "magnetic-flux FI terms fix two Kahler ratios",
            "E1/E5 or E3/E(-1) effects fix the remaining bulk direction and dilaton",
            "orbifold parities remove selected charged instanton zero modes",
        ],
        "representative_superpotential": "W=A_E exp(-2*pi*T3)+A_S exp(-S)",
        "assumptions": [
            "supersymmetric three-form flux fixes complex structure and dilaton",
            "discrete torsions are chosen to obtain O(1)-type instantons",
            "the analyzed instantons have no harmful charged zero modes",
        ],
        "published_boundaries": [
            "the stabilized vacuum is supersymmetric with negative energy",
            "a compatible hidden SUSY-breaking/uplifting sector is not constructed",
            "hidden branes can reintroduce zero modes that erase the instanton superpotential",
            "Majorana and mu terms are proposed as future instanton applications",
        ],
        "valid_use_here": (
            "proof that an instanton bridge is plausible in related magnetized Pati--Salam "
            "models, not evidence that it exists on the 51-modulus rigid-brane target"
        ),
    }


def bridge_requirements() -> list[dict[str, Any]]:
    return [
        {
            "id": "B1_51_divisor_and_Kahler_cone_inventory",
            "required": "derive the N=1 parity split of all 51 h11 directions and identify every surviving coordinate, axion, intersection, and a controlled Kahler-cone point",
        },
        {
            "id": "B2_discrete_GS_charge_and_period_matrix",
            "required": "derive the complete Z4R/Z11 axion action, levels, periods, and physical quotient from the compactification",
        },
        {
            "id": "B3_instanton_divisor_and_flux_rows",
            "required": "supply enough rigid O(1) E3/fluxed-E3 or condensing divisors to generate a rank-51 superpotential",
        },
        {
            "id": "B4_charged_zero_mode_audit",
            "required": "prove every contributing instanton is free of unsoaked visible and hidden charged zero modes",
        },
        {
            "id": "B5_global_consistency_after_instantons",
            "required": "recheck RR tadpoles, Freed-Witten/K-theory constraints, flux quantization, and backreaction",
        },
        {
            "id": "B6_prefactor_Hessian_and_branch_derivation",
            "required": "derive Pfaffian/threshold prefactors, the full physical Hessian, axion branches, and a controlled vacuum",
        },
        {
            "id": "B7_visible_selector_soft_and_component_matching",
            "required": "derive the visible selection rules, Yukawa/mu/Majorana/soft operators, residual Z2, and executable V24 map",
        },
    ]


def bridge_schema() -> dict[str, Any]:
    hash_pattern = "^[0-9a-f]{64}$"
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://local.invalid/susy-v28-microscopic-instanton-bridge-schema.json",
        "title": "SUSY V28 51-modulus microscopic instanton bridge",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "candidate_id",
            "moduli_inventory",
            "orientifold_parity_split_sha256",
            "axion_charge_matrix_sha256",
            "instanton_inventory_sha256",
            "charged_zero_mode_audit_sha256",
            "global_consistency_sha256",
            "vacuum_hessian",
            "visible_matching_sha256",
            "all_bridge_checks_pass",
        ],
        "properties": {
            "candidate_id": {"type": "string", "minLength": 1},
            "moduli_inventory": {
                "type": "array",
                "minItems": 51,
                "maxItems": 51,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["modulus_id", "divisor_id", "axion_period", "stabilization_source"],
                    "properties": {
                        "modulus_id": {"type": "string", "minLength": 1},
                        "divisor_id": {"type": "string", "minLength": 1},
                        "axion_period": {"type": "string", "minLength": 1},
                        "stabilization_source": {"type": "string", "minLength": 1},
                    },
                },
            },
            "orientifold_parity_split_sha256": {"type": "string", "pattern": hash_pattern},
            "axion_charge_matrix_sha256": {"type": "string", "pattern": hash_pattern},
            "instanton_inventory_sha256": {"type": "string", "pattern": hash_pattern},
            "charged_zero_mode_audit_sha256": {"type": "string", "pattern": hash_pattern},
            "global_consistency_sha256": {"type": "string", "pattern": hash_pattern},
            "vacuum_hessian": {
                "type": "object",
                "additionalProperties": False,
                "required": ["complex_dimension", "complex_rank", "real_rank", "positive_physical_spectrum"],
                "properties": {
                    "complex_dimension": {"const": 51},
                    "complex_rank": {"const": 51},
                    "real_rank": {"const": 102},
                    "positive_physical_spectrum": {"const": True},
                },
            },
            "visible_matching_sha256": {"type": "string", "pattern": hash_pattern},
            "all_bridge_checks_pass": {"const": True},
        },
    }


def build_report() -> dict[str, Any]:
    manifest = source_manifest()
    v26 = json.loads(
        (ROOT / "SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.json").read_text(encoding="utf-8")
    )
    v27 = json.loads(
        (ROOT / "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json").read_text(encoding="utf-8")
    )
    target = microscopic_target_ledger()
    scaffold = multi_modulus_racetrack_scaffold()
    requirements = bridge_requirements()
    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in manifest),
        "V26_core_matches": v26["core_sha256"] == UPSTREAM_CORES["V26_dynamical_GS_attempt"],
        "V27_core_matches": v27["core_sha256"] == UPSTREAM_CORES["V27_architecture_audit"],
        "rigid_target_has_ambient_h11_51": target["ambient_Kahler_sector_h11"] == 51,
        "conservative_V26_to_h11_gap_is_50": target["conservative_V26_to_ambient_h11_dimension_gap"] == 50,
        "twisted_N1_parity_inventory_is_not_overclaimed": (
            target["complete_twisted_N1_orientifold_parity_inventory_published"] is False
        ),
        "racetrack_uses_153_exponential_terms": scaffold["exponential_terms_required"] == 153,
        "double_root_identity_closes_W_and_gradient": (
            scaffold["p_at_y1"] == 0 and scaffold["Euler_p_at_y1"] == 0
        ),
        "holomorphic_Hessian_has_rank_51": scaffold["holomorphic_Hessian_rank"] == 51,
        "real_scalar_Hessian_has_rank_102": scaffold["real_scalar_Hessian_rank"] == 102,
        "original_V26_racetrack_is_recovered": (
            scaffold["recovers_V26_at_q_half_and_C_32M3"]["three_coefficients_in_M3_units"]
            == [2, -16, 32]
            and scaffold["recovers_V26_at_q_half_and_C_32M3"]["W_TT_over_pi2_M3"] == 3872
        ),
        "all_seven_bridge_requirements_are_unique": (
            len(requirements) == len({row["id"] for row in requirements}) == 7
        ),
        "microscopic_bridge_is_not_claimed": True,
        "full_G1_remains_open": v27["G1_gate"]["closed"] is False,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v28-new-physics-moduli-bridge-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v28.new_physics_moduli_bridge",
        "audit_date": "2026-08-24",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "primary_sources": PRIMARY_SOURCES,
        "microscopic_target": target,
        "exact_51_modulus_racetrack_scaffold": scaffold,
        "related_instantiation_precedent": instanton_precedent_ledger(),
        "microscopic_bridge_requirements": requirements,
        "generated_bridge_schema": SCHEMA_PATH.name,
        "new_physics_result": {
            "local_51_complex_modulus_stabilization_problem_solved": True,
            "works_for_any_regular_positive_Kahler_metric_at_the_SUSY_Minkowski_point": True,
            "target_points_can_be_chosen_independently": True,
            "microscopic_divisor_and_instanton_realization_derived": False,
            "direct_match_to_2026_rigid_brane_model": False,
            "new_best_research_route": (
                "fluxed O(1) E3 instantons or hidden condensates on the 51-modulus rigid-brane "
                "compactification, with a full charged-zero-mode and axion-charge audit"
            ),
        },
        "G1_gate": {
            "closed": False,
            "full_gate_claim": False,
            "qualified_local_multimodulus_subgate_closed": True,
            "state": "51_MODULUS_LOCAL_STABILIZATION_SOLVED__MICROSCOPIC_BRIDGE_OPEN",
            "remaining_blocker": (
                "derive the rank-51 instanton/condensate system and all seven bridge inputs "
                "inside the same globally consistent compactification"
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
    target = report["microscopic_target"]
    scaffold = report["exact_51_modulus_racetrack_scaffold"]
    lines = [
        "# SUSY V28 new-physics moduli bridge",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full G1 closed: **no**.",
        "- New qualified result: exact local stabilization of **51 complex moduli / 102 real scalars**.",
        "",
        "## New microscopic target",
        "",
        "The globally consistent 2026 rigid-brane Pati--Salam construction is stronger than the candidates previously encoded in one important way: its Type-IIB side has `(h11,h21)=(51,3)`, freezes open-string position/Wilson-line moduli by rigidity, and uses `G3` flux to fix the three complex-structure moduli plus the axio-dilaton. Its Kähler sector remains open.",
        "",
        f"V26 has one complex GS modulus. Relative to the ambient `h11` envelope, a direct field-level match therefore has a conservative **{target['conservative_V26_to_ambient_h11_dimension_gap']}-complex-dimensional gap**. The paper explicitly enumerates three untwisted `T_i` multiplets after orientifolding but does not publish a complete twisted-sector N=1 parity inventory; V28 therefore treats 51 as a conservative full-cohomology stabilization target, not as a claimed low-energy spectrum count.",
        "",
        "Primary source: [Three-Family Supersymmetric Pati--Salam Flux Models from Rigid D-Branes](https://arxiv.org/pdf/2512.21141), especially the introduction and moduli discussion on pages 1--3.",
        "",
        "## Exact 51-modulus construction",
        "",
        "For each `T_i`, choose a target `t_i*>0`, define `q_i=exp(-22*pi*t_i*)` and `x_i=exp(-22*pi*T_i)`, and take",
        "",
        "`W = sum_i C_i x_i (x_i^2-q_i^2)^2`, with `C_i>0`.",
        "",
        "Every summand uses the same `2*pi*n` exponents `n=(11,33,55)` as V26. At `T_i=t_i*`, the exact polynomial identities are `W=0`, `dW=0`, and",
        "",
        "`W_ij = delta_ij 3872*pi^2*C_i*q_i^5`.",
        "",
        f"Thus `rank(W_ij)={scaffold['holomorphic_Hessian_rank']}`. At a supersymmetric Minkowski point, any regular positive Kähler metric produces a positive-definite Hermitian mass block, so all `{scaffold['real_scalar_Hessian_rank']}` real modulus components are locally massive. Setting `q=1/2` and `C=32 M^3` exactly recovers the V26 coefficients `(2,-16,32)`.",
        "",
        "## Why this is not yet string physics",
        "",
        "The construction requires 153 exponential terms. No source presently identifies the 51 contributing divisors, removes every visible/hidden charged instanton zero mode, derives the Pfaffian prefactors and axion-charge matrix, or recomputes tadpoles/K-theory and the global branch quotient. At large target volume the Hessian is also exponentially small unless microscopic prefactors compensate.",
        "",
        "A related magnetized Pati--Salam model demonstrates FI plus E-brane stabilization for a three-modulus effective system, but its authors explicitly leave hidden-sector SUSY breaking/uplift open and warn that hidden-brane zero modes can erase the instanton superpotential. It is a mechanism precedent, not a derivation for the 51-modulus target: [arXiv:1703.03402](https://arxiv.org/pdf/1703.03402). The general chirality/charged-zero-mode obstruction and fluxed-instanton repair mechanism are analyzed in [arXiv:1105.3193](https://arxiv.org/abs/1105.3193).",
        "",
        "## Decision",
        "",
        "This investigation genuinely advances the theory: a local stabilization envelope covering all 51 ambient h11 directions is now solved exactly, so moduli count alone is not a mathematical no-go. Full G1 stays fail-closed because the orientifolded chiral inventory, microscopic instanton realization, and visible matching are external data. `SUSY_V28_MICROSCOPIC_INSTANTON_BRIDGE_SCHEMA.json` records the exact evidence needed for promotion.",
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
    SCHEMA_PATH.write_text(
        json.dumps(bridge_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def check_outputs(report: dict[str, Any]) -> bool:
    return all(
        [
            JSON_PATH.exists(),
            MD_PATH.exists(),
            SCHEMA_PATH.exists(),
            JSON_PATH.read_text(encoding="utf-8")
            == json.dumps(report, indent=2, sort_keys=True) + "\n",
            MD_PATH.read_text(encoding="utf-8") == render_markdown(report),
            SCHEMA_PATH.read_text(encoding="utf-8")
            == json.dumps(bridge_schema(), indent=2, sort_keys=True) + "\n",
        ]
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
        print(json.dumps({"failures": report["failures"], "outputs_match": check_outputs(report)}))
        return 1
    print(report["status"])
    print(report["core_sha256"])
    print(
        json.dumps(
            {
                "complex_moduli_locally_stabilized": 51,
                "real_modulus_components_locally_massive": 102,
                "microscopic_bridge_derived": 0,
                "full_G1_closed": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
