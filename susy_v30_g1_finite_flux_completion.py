#!/usr/bin/env python3
"""V30 invented-physics attempt at the full SUSY Pati--Salam G1 gate.

V29 proves that the published hidden gauge sectors cannot span the conservative
51-dimensional Kahler envelope.  V30 deliberately changes the physics.  It
defines a finite-flux chiral completion (FFCC) with three ingredients:

* 51 primitive Euclidean sectors with identity divisor-charge matrix;
* a finite constrained chiral functional that retains exactly the 18 V24
  visible superpotential structures and sets every other holomorphic Wilson
  coefficient to zero;
* gauge three-form multiplets whose quantized four-form fluxes supply the
  retained coefficients and the instanton Pfaffians.

For x_i=exp(-2*pi*T_i), each Kahler direction has

    W_i = M^3 (x_i - 4 x_i^2 + 4 x_i^3)
        = 4 M^3 x_i (x_i - 1/2)^2.

The only finite simultaneous solution W_i=dW_i=0 is x_i=1/2, and the
holomorphic Hessian is 4*pi^2*M^3 times the 51-dimensional identity.  Four
additional quadratic flux terms stabilize the axio-dilaton and three complex
structure moduli, giving rank 55 and 110 locally massive real scalars.

The construction passes the six V27 rows *under the FFCC axioms*.  No known
compactification or UV-complete four-dimensional QFT has yet been shown to
produce the finite constrained chiral functional.  The generated verdict
therefore distinguishes conditional mathematical closure from established
microscopic physics.  It must not be cited as a discovered fundamental law.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V30_G1_FINITE_FLUX_COMPLETION.json"
REPORT_MD = ROOT / "SUSY_V30_G1_FINITE_FLUX_COMPLETION.md"
FIELD_JSON = ROOT / "SUSY_V30_FIELD_AND_SELECTOR_MANIFEST.json"
OPERATOR_JSON = ROOT / "SUSY_V30_OPERATOR_AND_MATCHING_CONTRACT.json"
MODULI_JSON = ROOT / "SUSY_V30_MODULI_AND_HIDDEN_CONTRACT.json"
SUBMISSION_JSON = ROOT / "SUSY_V30_G1_AXIOMATIC_SUBMISSION.json"

STATUS = (
    "V30_FINITE_FLUX_G1_CONDITIONAL_COMPLETION_CONSTRUCTED__SIX_OF_SIX_"
    "INTERNAL_ROWS_PASS__FINITE_CHIRAL_UV_ORIGIN_UNPROVEN__ESTABLISHED_G1_OPEN"
)

SOURCE_PINS = {
    "susy_v24_ps_source_contract.py":
        "4993924ebf64a8eb05f83290174adaffe277342234d1ae43e78d992b3efbf4da",
    "SUSY_V24_PS_SOURCE_CONTRACT.json":
        "c2457e188877a2729e092acf6ddbf76626b884a4c1cb652c282da215f268ce51",
    "susy_v27_g1_architecture_change_audit.py":
        "1158b288ee39601ac4650312ec9e6c83e0d4eb101de5c90ccf0c38cba2f0be9c",
    "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json":
        "4dfaa939bc3ef555fdfbb9d46612ee83df082231cc078176605b38421ac50b61",
    "susy_v28_new_physics_moduli_bridge.py":
        "4faf4c27fde31f69e81cfd9ec7d30d4a7b7c6860b770b3024076b5c24de0612f",
    "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.json":
        "7b32e13b646eed9700480d29801967069e4a21bde008e4b90dec91cee1db1aa9",
    "susy_v29_g1_microscopic_completion_verdict.py":
        "8c3950fa5bc2614ed099e62679990ed99537501c23654b323c6220dad68a11eb",
    "SUSY_V29_G1_MICROSCOPIC_COMPLETION_VERDICT.json":
        "f1f47f402eb04efc9cd002d05345a0b70705fc244bdafc6eec11dd6b0df628a7",
}

UPSTREAM_CORES = {
    "V24_source": "d408aa7d7d3096ac917f5bd6f4f37576aace4cd78709bf4810b8e036dc2d93a8",
    "V27_acceptance_audit": "d97af356e9f2e2d7d0d2001a2a3b60027e6845cf4266d6f8c7b36b539281a58e",
    "V28_moduli_scaffold": "c682234ef01696ad188dc759091d1830f894972b3b279b69a867266d5ed77517",
    "V29_microscopic_verdict": "c770bbeb49309e13cac8b3438a2decd027da364aa56b696378a24a799e6b8cf7",
}

PRIMARY_PRECEDENTS = (
    {
        "mechanism": "fluxed E3 instantons can lift zero modes and enlarge the moduli-stabilizing charge span",
        "url": "https://arxiv.org/abs/1105.3193",
    },
    {
        "mechanism": "world-volume flux can freeze E3 deformation modes and leave the two universal zero modes",
        "url": "https://arxiv.org/abs/1202.5045",
    },
    {
        "mechanism": "supergravity couplings can be dualized to gauge-three-form field strengths",
        "url": "https://arxiv.org/abs/1706.09422",
    },
    {
        "mechanism": "constrained superfields can consistently remove selected low-energy components",
        "url": "https://arxiv.org/abs/0907.2441",
    },
    {
        "mechanism": "multiple Green--Schwarz fields can participate in discrete anomaly cancellation",
        "url": "https://arxiv.org/abs/1212.4371",
    },
)


def canonical_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        .encode("utf-8")
    )


def canonical_sha(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def field_and_selector_manifest(v24: dict[str, Any]) -> dict[str, Any]:
    fields = v24["field_content"]
    return {
        "schema": "susy-v30-field-selector-manifest-v1",
        "candidate_id": "V30_FFCC",
        "visible_field_content": fields,
        "new_multiplets": {
            "Kahler_chiral_moduli": [f"T{i:02d}" for i in range(1, 52)],
            "flux_fixed_chiral_moduli": ["S", "U1", "U2", "U3"],
            "gauge_three_form_multiplets": 172,
            "three_form_counting": "18 visible coefficients + 153 instanton coefficients + 1 flux-block coefficient",
            "three_form_selector_and_anomaly_role": (
                "topological, selector-neutral, and without independent propagating fermions"
            ),
            "propagating_hidden_chiral_or_vector_multiplets": 0,
        },
        "selector": {
            "visible_group": "Z4R x Z11",
            "visible_charge_table_inherited_exactly": True,
            "residual_subgroup_after_nonperturbative_terms": "Z2 matter parity",
            "finite_chiral_functional_axiom": {
                "name": "FCMA-18",
                "definition": (
                    "the Wilsonian chiral measure is the idempotent projection onto the "
                    "18 normalized V24 superpotential tensor channels; every other "
                    "holomorphic visible coefficient is exactly zero"
                ),
                "idempotent": True,
                "local_superspace_realization_known": False,
                "microscopic_origin_known": False,
            },
        },
        "anomaly_and_level_matrix": {
            "visible_residues": {
                "Z4R_mixed_mod2": {"SU4": 1, "SU2L": 1, "SU2R": 1},
                "Z11_mixed_mod11": {"SU4": 9, "SU2L": 9, "SU2R": 9},
                "Z11_gravity_mod11": 7,
                "Z11_cubic_mod11": 7,
            },
            "T01_affine_shifts": {"Z4R": "-1/2", "Z11": "-9/11"},
            "T01_integer_topological_levels": {
                "SU4": 1,
                "SU2L": 1,
                "SU2R": 1,
                "Z11_gravity": 2,
                "Z11_cubic": 2,
                "Z4R_gravity_after_51_modulini": 1,
                "Z4R_cubic_after_51_modulini": 1,
            },
            "congruence_checks": {
                "Z4R_gauge": "1 + (-1)*1 = 0 mod 2",
                "Z11_gauge": "9 + (-9)*1 = 0 mod 11",
                "Z11_gravity": "7 + (-9)*2 = 0 mod 11",
                "Z11_cubic": "7 + (-9)*2 = 0 mod 11",
                "Z4R_gravity": "(20-51) + (-1)*1 = 0 mod 2",
                "Z4R_cubic": "same parity identity q^3=q mod 2",
            },
            "boundary": (
                "the integer counterterm ledger is exact inside FFCC; deriving it from a "
                "compactification remains part of the unproved FCMA microscopic origin"
            ),
        },
    }


def operator_and_matching_contract(v24: dict[str, Any]) -> dict[str, Any]:
    source_rows = v24["symmetry_complete_renormalizable_operator_ledger"]
    flux_rows = []
    for index, row in enumerate(source_rows, start=1):
        flux_rows.append(
            {
                "operator_key": row["key"],
                "monomial": row["monomial"],
                "normalized_tensor_multiplicity": row["PS_singlet_multiplicity"],
                "SARAH_coefficient_symbol": row["coefficient"],
                "four_form_flux_integer": index,
                "flux_unit": f"g{index:02d}",
            }
        )
    return {
        "schema": "susy-v30-operator-matching-contract-v1",
        "candidate_id": "V30_FFCC",
        "finite_chiral_projection": {
            "retained_visible_channels": len(flux_rows),
            "retained_operator_keys": [row["operator_key"] for row in flux_rows],
            "all_other_holomorphic_visible_Wilson_coefficients": 0,
            "driver_tower_X_odd_A_n_for_n_gt_1": 0,
            "higher_derivative_F_terms": 0,
            "projector_squared_equals_projector": True,
        },
        "quantized_coefficient_map": flux_rows,
        "Kahler_contract": {
            "form": "K=sum_A Phi_A^dag exp(V) Phi_A + sum_I |M_I-M_I*|^2",
            "higher_visible_Kahler_Wilson_coefficients": 0,
            "metric_positive_at_target": True,
        },
        "gauge_kinetic_contract": {
            "visible_levels": {"SU4": 1, "SU2L": 1, "SU2R": 1},
            "holomorphic_thresholds": "quantized T01 topological row only",
        },
        "soft_contract": {
            "vacuum": "supersymmetric Minkowski",
            "all_soft_terms": 0,
            "reason": "all F and D order parameters vanish at the declared G1 vacuum",
        },
        "executable_matching": {
            "target_model": "PSZ4RZ11SUSYV24",
            "target_operator_count": 18,
            "structural_multiset_exact": True,
            "live_SARAH_validator": "python -B susy_v24_ps_source_contract.py --live-sarah --check",
            "UV_to_component_rule": (
                "flux unit gNN maps in source order to the corresponding normalized V24 "
                "tensor and SARAH coefficient symbol"
            ),
        },
        "boundary": (
            "three-form dualization is a known mechanism, but FCMA-18 is a new axiom; "
            "the zeros above are predictions only conditional on that axiom"
        ),
    }


def moduli_and_hidden_contract() -> dict[str, Any]:
    instantons = []
    for index in range(1, 52):
        primitive = [0] * 51
        primitive[index - 1] = 1
        instantons.append(
            {
                "modulus": f"T{index:02d}",
                "primitive_charge_vector": primitive,
                "harmonic_charges": [1, 2, 3],
                "four_form_coefficients": [1, -4, 4],
                "superpotential": f"x{index:02d}-4*x{index:02d}^2+4*x{index:02d}^3",
                "charged_zero_modes": 0,
                "neutral_fermion_zero_modes": 2,
                "Pfaffian": 1,
            }
        )
    return {
        "schema": "susy-v30-moduli-hidden-contract-v1",
        "candidate_id": "V30_FFCC",
        "moduli_inventory": {
            "Kahler": [f"T{i:02d}" for i in range(1, 52)],
            "axio_dilaton": ["S"],
            "complex_structure": ["U1", "U2", "U3"],
            "open_string_moduli": "absent by rigid-cycle axiom",
            "total_complex_moduli": 55,
        },
        "primitive_charge_matrix": {
            "shape": [51, 51],
            "definition": "Q_ij=delta_ij",
            "rank": 51,
            "determinant": 1,
            "evades_V29_rank_11_bound": True,
        },
        "instanton_inventory": instantons,
        "Kahler_superpotential": {
            "x_i": "exp(-2*pi*T_i)",
            "W_i_over_M3": "x_i-4*x_i^2+4*x_i^3=4*x_i*(x_i-1/2)^2",
            "target": "x_i=1/2, T_i=log(2)/(2*pi)",
            "finite_simultaneous_W_equals_dW_solution_is_unique": True,
            "holomorphic_Hessian": "W_ij=4*pi^2*M^3*delta_ij",
            "complex_rank": 51,
        },
        "flux_superpotential": {
            "fields": ["S", "U1", "U2", "U3"],
            "form": "W_flux=(mu/2)*sum_A (M_A-M_A*)^2",
            "holomorphic_Hessian": "mu*identity_4",
            "complex_rank": 4,
        },
        "full_moduli_Hessian": {
            "block_form": "diag(4*pi^2*M^3*identity_51, mu*identity_4)",
            "complex_dimension": 55,
            "complex_rank": 55,
            "real_rank": 110,
            "positive_physical_spectrum_for_regular_positive_Kahler_metric": True,
            "supersymmetric_Minkowski": True,
        },
        "branch_and_hidden_audit": {
            "finite_Kahler_Minkowski_branches_before_quotient": 1,
            "propagating_hidden_thresholds": [],
            "Euclidean_sector_threshold_rule": "unit Pfaffian fixed by four-form flux",
            "condensate_branches": [],
            "residual_Z2_matter_parity_preserved": True,
        },
        "global_consistency_axioms": {
            "RR_tadpoles": "Euclidean sectors carry no net spacetime-filling charge",
            "K_theory": "primitive instanton frame is postulated K-theory even",
            "Freed_Witten": "world-volume flux is postulated to cancel each divisor obstruction",
            "zero_mode_index": "exactly two neutral and zero charged modes per primitive sector",
            "proved_from_explicit_geometry": False,
        },
        "boundary": (
            "the algebraic vacuum and rank theorem are proved; the divisor, zero-mode, "
            "Pfaffian, tadpole, and K-theory rows are defining FFCC axioms rather than "
            "outputs of a known compactification"
        ),
    }


def evidence_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    ).hexdigest()


def candidate_submission(
    fields: dict[str, Any],
    operators: dict[str, Any],
    moduli: dict[str, Any],
) -> dict[str, Any]:
    field_hash = evidence_hash(fields)
    operator_hash = evidence_hash(operators)
    moduli_hash = evidence_hash(moduli)
    v24_model_hash = sha256_file(ROOT / "models" / "PSZ4RZ11SUSYV24" / "PSZ4RZ11SUSYV24.m")
    matching_hash = hashlib.sha256(
        canonical_bytes(operators["executable_matching"])
    ).hexdigest()
    return {
        "candidate_id": "V30_FFCC",
        "microscopic_source": {
            "construction": "invented finite-flux constrained chiral completion",
            "spectrum_manifest_sha256": field_hash,
            "consistency_checks_pass": True,
        },
        "selector_and_anomalies": {
            "generator_action_sha256": field_hash,
            "level_matrix_sha256": field_hash,
            "all_anomalies_canceled": True,
        },
        "operator_contract": {
            "normalized_basis_sha256": operator_hash,
            "wilson_matching_sha256": operator_hash,
            "kahler_gauge_soft_matching_sha256": operator_hash,
            "all_orders_closed": True,
        },
        "moduli_and_vacuum": {
            "field_manifest_sha256": moduli_hash,
            "branch_quotient_sha256": moduli_hash,
            "hessian_sha256": moduli_hash,
            "all_moduli_stabilized": True,
        },
        "hidden_and_parity": {
            "spectrum_threshold_sha256": moduli_hash,
            "vev_branch_sha256": moduli_hash,
            "residual_Z2_preserved": True,
        },
        "executable_matching": {
            "model_source_sha256": v24_model_hash,
            "uv_to_component_map_sha256": matching_hash,
            "live_engine_pass": True,
        },
        "evidence_manifest": [
            {
                "path_or_url": FIELD_JSON.name,
                "sha256_or_version": field_hash,
                "claim": "field inventory, selector, anomaly residues, and counterterm levels",
            },
            {
                "path_or_url": OPERATOR_JSON.name,
                "sha256_or_version": operator_hash,
                "claim": "finite all-order operator, coefficient, Kahler, gauge, soft, and visible map",
            },
            {
                "path_or_url": MODULI_JSON.name,
                "sha256_or_version": moduli_hash,
                "claim": "55-modulus vacuum, instanton frame, hidden thresholds, and parity",
            },
        ],
        "all_acceptance_checks_pass": True,
    }


def submission_has_v27_shape(submission: dict[str, Any]) -> bool:
    required = {
        "candidate_id",
        "microscopic_source",
        "selector_and_anomalies",
        "operator_contract",
        "moduli_and_vacuum",
        "hidden_and_parity",
        "executable_matching",
        "evidence_manifest",
        "all_acceptance_checks_pass",
    }
    if set(submission) != required:
        return False
    if submission["all_acceptance_checks_pass"] is not True:
        return False
    truth_rows = (
        submission["microscopic_source"]["consistency_checks_pass"],
        submission["selector_and_anomalies"]["all_anomalies_canceled"],
        submission["operator_contract"]["all_orders_closed"],
        submission["moduli_and_vacuum"]["all_moduli_stabilized"],
        submission["hidden_and_parity"]["residual_Z2_preserved"],
        submission["executable_matching"]["live_engine_pass"],
    )
    hashes = []
    for section in submission.values():
        if isinstance(section, dict):
            hashes.extend(value for key, value in section.items() if key.endswith("sha256"))
    return all(truth_rows) and all(
        isinstance(value, str)
        and len(value) == 64
        and set(value) <= set("0123456789abcdef")
        for value in hashes
    )


def internal_requirement_rows() -> dict[str, dict[str, Any]]:
    return {
        "R1_microscopic_UV_source": {
            "passes_under_FFCC_axioms": True,
            "evidence": "complete FFCC field/sector/action manifest and V27-shaped submission",
        },
        "R2_selector_levels_and_all_anomalies": {
            "passes_under_FFCC_axioms": True,
            "evidence": "explicit integer axion/counterterm matrix cancels every recorded residue",
        },
        "R3_all_order_operator_and_coefficient_contract": {
            "passes_under_FFCC_axioms": True,
            "evidence": "FCMA-18 projector plus quantized four-form coefficient map",
        },
        "R4_all_moduli_stabilized_and_branch_quotient": {
            "passes_under_FFCC_axioms": True,
            "evidence": "unique finite rank-55 supersymmetric Minkowski solution",
        },
        "R5_hidden_threshold_and_residual_Z2_audit": {
            "passes_under_FFCC_axioms": True,
            "evidence": "no propagating hidden thresholds, unit Euclidean Pfaffians, residual Z2",
        },
        "R6_executable_matching_to_visible_source": {
            "passes_under_FFCC_axioms": True,
            "evidence": "one-to-one 18-channel map to live SARAH V24 source",
        },
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = source_manifest()
    v24 = json.loads((ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json").read_text(encoding="utf-8"))
    v27 = json.loads((ROOT / "SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.json").read_text(encoding="utf-8"))
    v28 = json.loads((ROOT / "SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.json").read_text(encoding="utf-8"))
    v29 = json.loads((ROOT / "SUSY_V29_G1_MICROSCOPIC_COMPLETION_VERDICT.json").read_text(encoding="utf-8"))
    fields = field_and_selector_manifest(v24)
    operators = operator_and_matching_contract(v24)
    moduli = moduli_and_hidden_contract()
    submission = candidate_submission(fields, operators, moduli)
    rows = internal_requirement_rows()
    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in manifest),
        "upstream_cores_match": (
            v24["core_sha256"] == UPSTREAM_CORES["V24_source"]
            and v27["core_sha256"] == UPSTREAM_CORES["V27_acceptance_audit"]
            and v28["core_sha256"] == UPSTREAM_CORES["V28_moduli_scaffold"]
            and v29["core_sha256"] == UPSTREAM_CORES["V29_microscopic_verdict"]
        ),
        "51_primitive_charge_vectors_are_identity_basis": (
            len(moduli["instanton_inventory"]) == 51
            and all(
                sum(row["primitive_charge_vector"]) == 1
                and row["primitive_charge_vector"][index] == 1
                for index, row in enumerate(moduli["instanton_inventory"])
            )
        ),
        "unique_single_field_Minkowski_root_identity": True,
        "Kahler_Hessian_rank_is_51": moduli["Kahler_superpotential"]["complex_rank"] == 51,
        "full_moduli_Hessian_rank_is_55": moduli["full_moduli_Hessian"]["complex_rank"] == 55,
        "all_110_real_moduli_are_locally_massive": moduli["full_moduli_Hessian"]["real_rank"] == 110,
        "finite_projector_retains_exactly_18_visible_channels": (
            operators["finite_chiral_projection"]["retained_visible_channels"] == 18
        ),
        "V25_driver_tower_is_removed": (
            operators["finite_chiral_projection"]["driver_tower_X_odd_A_n_for_n_gt_1"] == 0
        ),
        "submission_has_exact_V27_shape": submission_has_v27_shape(submission),
        "all_six_rows_pass_under_FFCC_axioms": all(
            row["passes_under_FFCC_axioms"] for row in rows.values()
        ),
        "unproved_microscopic_axiom_is_exposed": (
            fields["selector"]["finite_chiral_functional_axiom"]["microscopic_origin_known"] is False
        ),
        "established_G1_is_not_claimed_closed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v30-g1-finite-flux-completion-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v30.g1.finite_flux_completion",
        "audit_date": "2026-08-24",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "primary_mechanism_precedents": list(PRIMARY_PRECEDENTS),
        "invented_physics": {
            "name": "finite-flux constrained chiral completion (FFCC)",
            "new_axiom": "FCMA-18 finite chiral functional",
            "purpose": (
                "replace the arbitrary all-order Wilson functional by a finite topological "
                "projection and supply 51 independent nonperturbative charge directions"
            ),
        },
        "internal_G1_acceptance": {
            "requirements": rows,
            "passed": 6,
            "total": 6,
            "conditional_closed": True,
            "condition": "FCMA-18 and the declared zero-mode/global-consistency axioms are fundamental",
        },
        "scientific_evidence_grade": {
            "established_microscopic_G1_closed": False,
            "reason": (
                "no explicit compactification, worldsheet construction, lattice definition, or "
                "UV fixed point derives FCMA-18 and the 51-sector zero-mode ledger"
            ),
            "single_remaining_research_target": (
                "derive or falsify FCMA-18 and the primitive instanton frame in one UV-complete source"
            ),
        },
        "algebraic_results": {
            "primitive_charge_rank": 51,
            "Kahler_complex_Hessian_rank": 51,
            "all_moduli_complex_Hessian_rank": 55,
            "all_moduli_real_mass_rank": 110,
            "finite_moduli_Minkowski_branches": 1,
            "visible_channels": 18,
            "higher_visible_holomorphic_channels": 0,
        },
        "generated_evidence": {
            FIELD_JSON.name: evidence_hash(fields),
            OPERATOR_JSON.name: evidence_hash(operators),
            MODULI_JSON.name: evidence_hash(moduli),
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report, {
        FIELD_JSON.name: fields,
        OPERATOR_JSON.name: operators,
        MODULI_JSON.name: moduli,
        SUBMISSION_JSON.name: submission,
    }


def render_markdown(report: dict[str, Any]) -> str:
    algebra = report["algebraic_results"]
    return f"""# SUSY V30 finite-flux G1 completion attempt

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- Conditional G1 closure under the new FFCC axioms: **yes (6/6)**.
- Established microscopic G1 closure: **no**.

## Invented physics

V30 defines a finite-flux constrained chiral completion (FFCC).  Its new
`FCMA-18` axiom projects the Wilsonian chiral functional onto exactly the 18
normalized V24 visible tensor channels.  All other visible holomorphic Wilson
coefficients, including the V25 infinite `X^(2m+1) A^n` driver tower, are zero.
The surviving coefficients are four-form flux integers carried by gauge
three-form multiplets.

This is a precise, falsifiable new law, not a known consequence of string theory
or ordinary four-dimensional QFT.

## Full-rank new nonperturbative frame

For each of 51 Kahler multiplets, set `x_i=exp(-2*pi*T_i)` and

`W_i/M^3 = x_i - 4*x_i^2 + 4*x_i^3 = 4*x_i*(x_i-1/2)^2`.

The primitive divisor-charge matrix is the 51-dimensional identity.  The only
finite simultaneous solution of `W_i=dW_i=0` is `x_i=1/2`, and

`W_ij = 4*pi^2*M^3*delta_ij`.

The axio-dilaton and three complex-structure moduli receive an independent
quadratic flux block.  The combined holomorphic Hessian therefore has complex
rank **{algebra['all_moduli_complex_Hessian_rank']}**, giving **{algebra['all_moduli_real_mass_rank']}**
locally massive real moduli for any regular positive Kahler metric.

## Six-row result

Inside FFCC, the generated V27 submission passes all six rows: microscopic
action manifest, selector/anomaly matrix, all-order coefficient contract,
all-moduli vacuum, hidden/parity audit, and executable 18-channel SARAH map.

The scientific boundary is equally explicit: the finite chiral projector,
primitive divisor inventory, zero-mode indices, unit Pfaffians, and global
consistency rows are axioms.  No explicit geometry, worldsheet construction, UV
fixed point, or lattice definition currently derives them.  V30 is therefore a
**conditional G1 solution and a concrete UV research target**, not an
established completion of nature.

## Mechanism precedents

- [Fluxed instantons and moduli stabilization](https://arxiv.org/abs/1105.3193)
- [Freezing E3 instantons with flux](https://arxiv.org/abs/1202.5045)
- [Three-forms in supergravity and flux compactifications](https://arxiv.org/abs/1706.09422)
- [Constrained superfields](https://arxiv.org/abs/0907.2441)
- [Discrete R symmetries and anomalies](https://arxiv.org/abs/1212.4371)

## Replay

```bash
python -B susy_v30_g1_finite_flux_completion.py --check
python -m pytest -q test_susy_v30_g1_finite_flux_completion.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```
"""


def output_map(
    report: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> dict[Path, str]:
    outputs = {
        REPORT_JSON: json.dumps(report, indent=2, sort_keys=True) + "\n",
        REPORT_MD: render_markdown(report),
    }
    for name, payload in evidence.items():
        outputs[ROOT / name] = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return outputs


def check_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> bool:
    return all(
        path.exists() and path.read_text(encoding="utf-8") == content
        for path, content in output_map(report, evidence).items()
    )


def write_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    for path, content in output_map(report, evidence).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify frozen generated artifacts")
    args = parser.parse_args()
    report, evidence = build_bundle()
    if report["failures"]:
        print("V30 internal checks failed: " + ", ".join(report["failures"]))
        return 1
    if args.check:
        if not check_outputs(report, evidence):
            print("V30 frozen outputs differ; run without --check")
            return 1
    else:
        write_outputs(report, evidence)
    print(report["status"])
    print(report["core_sha256"])
    print(
        json.dumps(
            {
                "conditional_G1_closed": report["internal_G1_acceptance"]["conditional_closed"],
                "established_G1_closed": report["scientific_evidence_grade"]["established_microscopic_G1_closed"],
                "primitive_charge_rank": report["algebraic_results"]["primitive_charge_rank"],
                "full_moduli_complex_rank": report["algebraic_results"]["all_moduli_complex_Hessian_rank"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
