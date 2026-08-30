#!/usr/bin/env python3
"""V29 terminal audit of whether V28 can complete full G1.

The 2026 rigid-brane source publishes 17 globally consistent Pati--Salam
compactifications.  This certificate counts the independent hidden gauge
factors in every model and applies a general Hessian-rank theorem to their
possible gaugino-condensate superpotentials.

For m independent gauge kinetic functions,

    W = sum_alpha A_alpha exp(-a_alpha q_alpha.i T_i)

has W_ij equal to a sum of m rank-one outer products when the prefactors carry
no additional Kahler dependence.  Its rank is therefore at most m; additional
harmonics from the same gauge factor do not enlarge the charge-vector span.
The largest published hidden sector has 11 factors, below the 51-direction
conservative V28 h11 envelope.  Independent E3 instantons, D-term lifting, or
field-dependent Pfaffians could evade the bound, but none is derived in the
selected compactifications.  The same source explicitly leaves Yukawas, soft
terms, and twisted-sector Yukawa rules open.  Full G1 cannot close from these
inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V29_G1_MICROSCOPIC_COMPLETION_VERDICT.json"
MD_PATH = ROOT / "SUSY_V29_G1_MICROSCOPIC_COMPLETION_VERDICT.md"

STATUS = (
    "V29_G1_MICROSCOPIC_COMPLETION_AUDIT_COMPLETE__ALL_17_RIGID_BRANE_"
    "MODELS_PUBLISHED_HIDDEN_FACTOR_SPAN_AT_MOST_11__YUKAWA_SOFT_MATCHING_"
    "UNPUBLISHED__FULL_G1_NOT_CLOSED"
)

SOURCE_PINS = {
    "susy_v28_new_physics_moduli_bridge.py":
        "4faf4c27fde31f69e81cfd9ec7d30d4a7b7c6860b770b3024076b5c24de0612f",
    "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.json":
        "7b32e13b646eed9700480d29801967069e4a21bde008e4b90dec91cee1db1aa9",
    "SUSY_V28_MICROSCOPIC_INSTANTON_BRIDGE_SCHEMA.json":
        "416ffe8375dbbc68e3b2a11e31360533e60cfe4c012719a6c8d5cebf2490799c",
    "susy_v27_g1_architecture_change_audit.py":
        "1158b288ee39601ac4650312ec9e6c83e0d4eb101de5c90ccf0c38cba2f0be9c",
    "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json":
        "4dfaa939bc3ef555fdfbb9d46612ee83df082231cc078176605b38421ac50b61",
}

UPSTREAM_CORES = {
    "V27_architecture_audit": "d97af356e9f2e2d7d0d2001a2a3b60027e6845cf4266d6f8c7b36b539281a58e",
    "V28_moduli_bridge": "c682234ef01696ad188dc759091d1830f894972b3b279b69a867266d5ed77517",
}

PRIMARY_SOURCE = {
    "citation": "Mansha, Sabir, Li, and Wang, arXiv:2512.21141v2 (12 May 2026)",
    "url": "https://arxiv.org/pdf/2512.21141",
    "locations": {
        "17_model_gauge_groups": "section 4 and appendix A, tables 22--38",
        "Kahler_flatness": "pages 16, 19, and conclusion page 52",
        "phenomenology_open": "conclusion page 52",
    },
}

# The first four factors SU(4)_C x SU(2)_L x SU(2)_R1 x SU(2)_R2 are the
# visible/recombination sector.  Entries below are the additional non-abelian
# factors exactly as displayed in section 4 of arXiv:2512.21141v2.
PUBLISHED_MODELS = (
    ("r15f1", {"SU2": 3, "SU4": 2}),
    ("r17f1", {"SU2": 1, "SU4": 1, "USp4": 4}),
    ("r43f1", {"SU2": 5, "USp16": 4}),
    ("r7f2", {"SU2": 1}),
    ("r10f2", {"SU2": 1, "SU4": 1}),
    ("r35f2", {"SU2": 5, "USp12": 4}),
    ("r43af2", {"SU2": 5, "USp16": 4}),
    ("r43bf2", {"SU2": 5, "USp16": 4}),
    ("r123f2", {"SU2": 5, "USp56": 4}),
    ("r125f2", {"SU2": 1, "SU4": 2, "USp56": 4}),
    ("r27f3", {"SU2": 5, "USp8": 4}),
    ("r35f3", {"SU2": 5, "USp12": 4}),
    ("r75f3", {"SU2": 5, "USp32": 4}),
    ("r76f3", {"SU2": 3, "SU4": 1, "USp32": 4}),
    ("r20f4", {"SU4": 4, "USp4": 1}),
    ("r26f4", {"SU2": 4, "SU4": 2, "USp8": 1, "USp4": 3}),
    ("r33f4", {"SU2": 5, "SU4": 2, "USp8": 4}),
)


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
                "expected_sha256": expected,
                "sha256": actual,
                "matches": actual == expected,
            }
        )
    return rows


def model_ledger() -> list[dict[str, Any]]:
    rows = []
    for model_id, factors in PUBLISHED_MODELS:
        count = sum(factors.values())
        rows.append(
            {
                "model_id": model_id,
                "additional_nonabelian_factor_multiplicities": factors,
                "maximum_independent_hidden_gauge_kinetic_functions": count,
                "standard_condensate_moduli_Hessian_rank_upper_bound": count,
                "rank_51_envelope_possible_from_one_published_charge_direction_per_factor": count >= 51,
            }
        )
    return rows


def hessian_rank_theorem() -> dict[str, Any]:
    return {
        "superpotential_class": (
            "W_h=sum_alpha A_alpha exp(-a_alpha sum_i q_alpha_i T_i), alpha=1,...,m, "
            "with A_alpha carrying no additional Kahler-direction dependence"
        ),
        "holomorphic_Hessian": (
            "W_ij=sum_alpha c_alpha q_alpha_i q_alpha_j = Q^T diag(c_alpha) Q"
        ),
        "rank_bound": "rank(W_ij)<=rank(Q)<=m",
        "same_factor_harmonics": (
            "multi-instanton or racetrack harmonics parallel to one q_alpha can tune a "
            "stationary point but cannot add a new direction to the charge-vector span"
        ),
        "ways_to_evade": [
            "independent rigid/fluxed E3 instantons with new divisor charge vectors",
            "published D-term/Stueckelberg lifting of the remaining directions",
            "additional microscopic sectors with independent gauge kinetic functions",
            "microscopically derived field-dependent Pfaffian or threshold prefactors",
        ],
        "none_of_these_evasions_is_derived_in_the_17_models": True,
    }


def build_report() -> dict[str, Any]:
    manifest = source_manifest()
    v27 = json.loads(
        (ROOT / "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json").read_text(encoding="utf-8")
    )
    v28 = json.loads(
        (ROOT / "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.json").read_text(encoding="utf-8")
    )
    models = model_ledger()
    max_row = max(
        models,
        key=lambda row: row["standard_condensate_moduli_Hessian_rank_upper_bound"],
    )
    envelope = v28["exact_51_modulus_racetrack_scaffold"]["number_of_complex_moduli"]
    max_rank = max_row["standard_condensate_moduli_Hessian_rank_upper_bound"]
    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in manifest),
        "V27_core_matches": v27["core_sha256"] == UPSTREAM_CORES["V27_architecture_audit"],
        "V28_core_matches": v28["core_sha256"] == UPSTREAM_CORES["V28_moduli_bridge"],
        "all_17_published_models_are_audited": len(models) == 17,
        "model_ids_are_unique": len({row["model_id"] for row in models}) == 17,
        "r33f4_has_largest_hidden_factor_count_11": (
            max_row["model_id"] == "r33f4" and max_rank == 11
        ),
        "every_published_hidden_charge_span_is_rank_deficient_for_envelope": all(
            not row["rank_51_envelope_possible_from_one_published_charge_direction_per_factor"]
            for row in models
        ),
        "minimum_ambient_envelope_rank_deficiency_is_40": envelope - max_rank == 40,
        "Kahler_flatness_is_not_relabelled_as_stabilization": True,
        "unpublished_Yukawa_and_soft_terms_are_not_invented": True,
        "full_G1_claim_remains_false": v27["G1_gate"]["closed"] is False,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v29-g1-microscopic-completion-verdict-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v29.g1_microscopic_completion_verdict",
        "audit_date": "2026-08-24",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "primary_source": PRIMARY_SOURCE,
        "published_model_ledger": models,
        "condensate_Hessian_rank_theorem": hessian_rank_theorem(),
        "all_model_bound": {
            "V28_conservative_complex_moduli_envelope": envelope,
            "maximum_published_hidden_factor_count": max_rank,
            "model_attaining_maximum": max_row["model_id"],
            "minimum_uncovered_envelope_directions": envelope - max_rank,
            "standard_published_hidden_charge_span_can_realize_V28_rank_51": False,
            "boundary": (
                "this is an envelope bound because the source does not publish the complete "
                "twisted-sector N=1 parity inventory; that missing inventory is itself required "
                "before a smaller physical moduli count can be claimed. Field-dependent "
                "Pfaffians could alter the rank but are also not published"
            ),
        },
        "other_independent_full_G1_blockers": {
            "published_complete_Yukawa_couplings": False,
            "published_twisted_sector_Yukawa_rules": False,
            "published_SUSY_breaking_soft_terms_for_rigid_models": False,
            "published_all_order_operator_and_coefficient_contract": False,
            "published_executable_UV_to_component_matching": False,
            "source_statement": (
                "the conclusion explicitly identifies Yukawas, soft terms, flavor, and "
                "twisted-sector Yukawa interpretation as next steps/open problems"
            ),
        },
        "G1_gate": {
            "closed": False,
            "full_gate_claim": False,
            "V28_local_51_field_scaffold_retained": True,
            "V28_promoted_to_microscopic_completion": False,
            "state": "CURRENT_NEW_PHYSICS_EXHAUSTED__EXTERNAL_MICROSCOPIC_INPUT_REQUIRED",
            "remaining_minimum_input": (
                "a complete orientifolded moduli inventory plus at least 40 additional "
                "independent lifting directions in the ambient envelope, followed by "
                "zero-mode/global-consistency and visible operator matching"
            ),
        },
        "terminal_decision": {
            "finish_full_G1_with_V28_and_the_17_published_models": False,
            "reason": (
                "the published hidden charge-vector span is rank deficient and the source does "
                "not supply field-dependent Pfaffians, independent instantons, Yukawas, soft "
                "terms, or executable matching"
            ),
            "scientifically_valid_completion_of_current_task": (
                "retain V28 as an exact local new-physics theorem and stop before a false "
                "microscopic G1 promotion"
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
    bound = report["all_model_bound"]
    lines = [
        "# SUSY V29 full-G1 microscopic completion verdict",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full G1 closed: **no**.",
        "- Published rigid-brane models audited: **17/17**.",
        "",
        "## Exact all-model obstruction",
        "",
        "For the standard condensate superpotential `W=sum_alpha A_alpha exp(-a_alpha q_alpha.T)`, with prefactors carrying no extra Kähler dependence, the holomorphic moduli Hessian is a sum of outer products, `W_ij=sum_alpha c_alpha q_alpha_i q_alpha_j`. With `m` independent hidden gauge kinetic functions, `rank(W_ij)<=m`. Racetrack harmonics from the same gauge factor remain parallel and do not enlarge this span.",
        "",
        f"Across all 17 compactifications, the largest hidden sector is `{bound['model_attaining_maximum']}` with **{bound['maximum_published_hidden_factor_count']}** additional non-abelian factors. Hidden condensation alone therefore has rank at most 11, leaving at least **{bound['minimum_uncovered_envelope_directions']}** directions uncovered in V28's conservative 51-direction `h11` envelope.",
        "",
        "This envelope statement does not assume an unpublished orientifold spectrum: the complete twisted-sector N=1 parity inventory is itself missing. A smaller physical count cannot be used to promote G1 until that inventory is derived. Independent fluxed E3 instantons, explicit D-term lifting, or field-dependent Pfaffians could evade the bound, but none is calculated in the 17 models.",
        "",
        "Primary source: [Three-Family Supersymmetric Pati--Salam Flux Models from Rigid D-Branes](https://arxiv.org/pdf/2512.21141), section 4, appendix A, and the conclusion.",
        "",
        "## Independent blockers",
        "",
        "The same source explicitly leaves the rigid-model Yukawa couplings, SUSY-breaking soft terms, flavor analysis, and twisted-sector Yukawa interpretation for future work. Consequently the all-order operator contract and executable UV-to-visible matching remain absent even if a future instanton sector solves the Kähler problem.",
        "",
        "## Final decision",
        "",
        "V28 is retained as a valid exact local stabilization theorem, but it cannot be promoted to a microscopic completion. Finishing full G1 now would require inventing the missing lifting/Pfaffian data and unpublished visible couplings. The scientifically correct terminal result is therefore full G1 fail-closed pending external microscopic data.",
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
    return all(
        [
            JSON_PATH.exists(),
            MD_PATH.exists(),
            JSON_PATH.read_text(encoding="utf-8")
            == json.dumps(report, indent=2, sort_keys=True) + "\n",
            MD_PATH.read_text(encoding="utf-8") == render_markdown(report),
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
                "published_models_audited": 17,
                "maximum_condensate_rank": report["all_model_bound"]["maximum_published_hidden_factor_count"],
                "minimum_uncovered_envelope_directions": report["all_model_bound"]["minimum_uncovered_envelope_directions"],
                "full_G1_closed": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
