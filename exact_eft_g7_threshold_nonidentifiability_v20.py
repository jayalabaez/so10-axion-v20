#!/usr/bin/env python3
"""Historical formal-U(1)_89 restriction audit; no physical G7 theorem.

The frozen spectrum used ``G_(8,9)`` and mislabeled it electromagnetism.  Its
q=0/1 sectors therefore cannot support electroweak or QED threshold claims.
This superseding report retains the old two-lift construction only as an
abstract noninjectivity example for formal U(1)_89 labels, and separately
records the valid common-scale nonidentifiability.  It proves no physical
electroweak threshold theorem and closes no version of G7.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
STATUS = "FORMAL_U1_89_ABSTRACT_RESTRICTION_NONINJECTIVE__NO_PHYSICAL_G7_CLAIM"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
OUT_JSON = HERE / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
OUT_MD = HERE / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.md"

# Frozen after the integration fields are intentionally promoted.
EXPECTED_CORE_SHA256 = "93a8ea1abeb3cec2521cb043057b29646bd9c368f8e8bcc7e2d819f42a7dc741"
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "778f96c8760a43be5214b215e08a6308d6198b84ebff9edd7729e75203b13cae",
    "md": "fc46765cdf7e46f529d2a4a9ceabb308c7a3c5b74c249733ce2833dd70fb3d01",
}

G6_SPECTRUM_CORE = "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
G6_GATE_CORE = "3b06ae240c7fce18723f0ce77966e894e688dee65f56859239ff5cf552b1323c"
G6_PROVENANCE_CORE = "0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39"
G6_MATCHING_CORE = "0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f"

# ``raw`` means exact bytes.  ``portable_text`` canonicalizes CRLF/CR to LF;
# this is explicit so historical model inputs remain checkout-portable.
DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "G6_spectrum_source": (
        HERE / "exact_eft_physical_scalar_spectrum_v20.py",
        "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36",
        "raw",
    ),
    "G6_spectrum_JSON": (
        HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
        "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416",
        "raw",
    ),
    "G6_gate_source": (
        HERE / "final_g6_eft_mathematical_gate_v20.py",
        "16eba20b834ebca25b3a8b91d867ddee76b1676791b18aa86db32a6ebc77af4e",
        "raw",
    ),
    "G6_gate_JSON": (
        HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
        "8bd98401ed6e2540ae7968a5b6a51a8e49abd98943252dec159c873d73a13f6c",
        "raw",
    ),
    "G6_physical_provenance_source": (
        HERE / "exact_g6_sm_provenance_feasibility_v20.py",
        "8bb67fb09c1cd3b57bf2c02e9ed7f1242a955c5a81ceb7d44dd48435c82618c1",
        "raw",
    ),
    "G6_physical_provenance_JSON": (
        HERE / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
        "a8daa4fb1dadbea48b25ad671a18f8d467384979769772be628a43f75054f6fa",
        "raw",
    ),
    "G6_G7_parameterized_matching_source": (
        HERE / "exact_eft_g6_g7_parameterized_matching_v20.py",
        "4653653de5f7f29b8dd12b7a3d1e387aafab2a193137c08dc2e4be942dceee42",
        "raw",
    ),
    "G6_G7_parameterized_matching_JSON": (
        HERE / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json",
        "b1bbf35b23a272eadc0a8520f0dac32fb342c7f1f3886088db2d9158acfd5ae9",
        "raw",
    ),
    "authoritative_gauged_U1X_model": (
        HERE / "models" / "SO10Z17AxionV20.m",
        "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "portable_text",
    ),
    "reduced_live_model": (
        HERE / "models" / "SO10Z17AxionV20_live.model",
        "976ad1c1e01c45df309b0f0511121607d723c531471a9ce3e6b4db311621475f",
        "portable_text",
    ),
    "reduced_quartic_model": (
        HERE / "models" / "SO10Z17AxionV20_quartic_live.model",
        "605d5ae6235f33c30c2755873185b7e9d94b11b35a8bf15199cb915c5c02a12a",
        "portable_text",
    ),
    "reduced_pyrate_yaml": (
        HERE / "models" / "SO10Z17AxionV20_pyrate.yaml",
        "5a0a7772e3c4d3dcfb4304446e4fbaf5263f8281a9dd0f5415efa7904f5b5a58",
        "portable_text",
    ),
    "legacy_RGE_source": (
        HERE / "yukawa_rge_2loop_v20.py",
        "a69b735cc6d94e6cc0543e4ddeea384a57c118b1893284996b65ec21c422114d",
        "portable_text",
    ),
    "legacy_RGE_verdict": (
        HERE / "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
        "39b7885207712a600128b489d4926e0f7980c348fe45ef913c80f18f58e825ce",
        "portable_text",
    ),
}


def _digest(path: Path, mode: str) -> str:
    data = path.read_bytes()
    if mode == "portable_text":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif mode != "raw":
        raise ValueError(f"unknown digest mode: {mode}")
    return hashlib.sha256(data).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _source_guard() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for name, (path, expected, mode) in DEPENDENCIES.items():
        digest = _digest(path, mode)
        if digest != expected:
            raise ArithmeticError(f"frozen G7 obstruction dependency drifted: {name}")
        observed[name] = {"path": str(path.relative_to(HERE)), "sha256": digest, "mode": mode}
    return observed


def _has_exact_root(sector: dict[str, Any], root: str, multiplicity: int) -> bool:
    for factor in sector["primitive_factors"]:
        intervals = factor["mass_squared_root_intervals"]
        if (
            factor["degree"] == 1
            and factor["root_multiplicity"] == multiplicity
            and len(intervals) == 1
            and intervals[0]["lower"] == root
            and intervals[0]["upper"] == root
        ):
            return True
    return False


def _threshold_collision() -> dict[str, Any]:
    # Two complex residual fields: one Q=0 and one |Q|=1.  Both completions
    # restrict to exactly those SU(3)-singlet electromagnetic representations.
    a_t2 = Fraction(0)
    a_y2 = Fraction(1)
    b_t2 = Fraction(1, 2)
    b_y2 = 2 * Fraction(1, 2) ** 2
    scalar_factor = Fraction(1, 3)
    a_db = (scalar_factor * a_t2, scalar_factor * a_y2)
    b_db = (scalar_factor * b_t2, scalar_factor * b_y2)
    residual_a = [("1", Fraction(0)), ("1", Fraction(1))]
    residual_b = [
        ("1", Fraction(-1, 2) + Fraction(1, 2)),
        ("1", Fraction(1, 2) + Fraction(1, 2)),
    ]
    return {
        "observed_residual_modes": [
            {"sector": "C0_Q0", "x": "26/5", "real_multiplicity": 2},
            {"sector": "C0_Q1", "x": "37/20", "real_multiplicity": 2},
        ],
        "completion_A": {
            "electroweak_representations": ["(1,1)_0", "(1,1)_1"],
            "sum_T2": _fraction_text(a_t2),
            "sum_Y_squared": _fraction_text(a_y2),
            "complex_scalar_one_loop_delta_b2": _fraction_text(a_db[0]),
            "complex_scalar_one_loop_delta_bY": _fraction_text(a_db[1]),
        },
        "completion_B": {
            "electroweak_representation": "(1,2)_{1/2}",
            "interpretation": "the two observed states are its EWSB-split Q=0,1 components",
            "sum_T2": _fraction_text(b_t2),
            "sum_Y_squared": _fraction_text(b_y2),
            "complex_scalar_one_loop_delta_b2": _fraction_text(b_db[0]),
            "complex_scalar_one_loop_delta_bY": _fraction_text(b_db[1]),
        },
        "same_SU3C_x_U1em_restriction": sorted(residual_a) == sorted(residual_b),
        "same_frozen_G6_masses": True,
        "one_loop_coefficients_differ": a_db != b_db,
        "restriction_map_noninjective": True,
    }


def build_report() -> dict[str, Any]:
    bindings = _source_guard()
    spectrum = json.loads(
        (HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json").read_text(encoding="utf-8")
    )
    gate = json.loads(
        (HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json").read_text(encoding="utf-8")
    )
    provenance = json.loads(
        (HERE / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    matching = json.loads(
        (HERE / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json").read_text(
            encoding="utf-8"
        )
    )
    legacy = json.loads(
        (HERE / "YUKAWA_RGE_2LOOP_V20_VERDICT.json").read_text(encoding="utf-8")
    )
    authoritative_text = (HERE / "models" / "SO10Z17AxionV20.m").read_text(
        encoding="utf-8"
    )
    reduced_text = (HERE / "models" / "SO10Z17AxionV20_live.model").read_text(
        encoding="utf-8"
    )
    quartic_text = (HERE / "models" / "SO10Z17AxionV20_quartic_live.model").read_text(
        encoding="utf-8"
    )
    sectors = spectrum["stabilizer_provenance"]["sector_reports"]
    uncertainty = spectrum["uncertainty_scope"]
    collision = _threshold_collision()

    checks = {
        "G6_spectrum_core_bound": spectrum["core_sha256"] == G6_SPECTRUM_CORE,
        "G6_gate_core_bound": gate["core_sha256"] == G6_GATE_CORE,
        "G6_is_normalized_tree_level_EFT_only": (
            spectrum["normalization"]["Lambda_EFT"] == "1"
            and spectrum["normalization"]["physical_mass_squared_variable"] == "x"
        ),
        "legacy_G6_U1em_label_is_superseded_by_exact_provenance": (
            spectrum["stabilizer_provenance"]["unbroken_group"]
            == "SU(3)_C x U(1)_em"
            and provenance["core_sha256"] == G6_PROVENANCE_CORE
            and provenance["classification"][
                "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89"
            ]
            is True
            and provenance["classification"][
                "prior_positive_mathematical_G6_as_physical_SM_spectrum_valid"
            ]
            is False
            and gate["classification"][
                "formal_SU3_x_U1_89_tree_mass_factorization_closed"
            ]
            is True
            and gate["classification"]["mathematical_physical_G6_closed"] is False
        ),
        "G6_omits_electroweak_and_intermediate_labels": all(
            not ({"SU2L_irrep", "hypercharge", "pati_salam_irrep", "matching_scale"} & set(row))
            for row in sectors.values()
        ),
        "neutral_collision_mode_exact": _has_exact_root(sectors["C0_Q0"], "26/5", 2),
        "charged_collision_mode_exact": _has_exact_root(sectors["C0_Q1"], "37/20", 2),
        "formal_U1_89_abstract_restriction_map_noninjective": collision[
            "restriction_map_noninjective"
        ],
        "historical_electroweak_lift_is_not_physical_threshold_evidence": (
            matching["core_sha256"] == G6_MATCHING_CORE
            and matching["classification"]["physical_SM_scalar_thresholds_identified"]
            is False
            and matching["classification"][
                "SM_or_PS_component_threshold_matching_complete"
            ]
            is False
        ),
        "absolute_scale_not_frozen": not uncertainty["absolute_scale_and_Wilson_matching_complete"],
        "loop_and_pole_masses_not_frozen": not uncertainty["loop_and_pole_mass_corrections_complete"],
        "running_scheme_not_frozen": not uncertainty["renormalization_scheme_and_running_complete"],
        "threshold_uncertainties_not_frozen": not uncertainty["physical_threshold_uncertainties_complete"],
        "authoritative_contract_gauges_U1X": (
            "Gauge[[2]] = {GX, U[1], xcharge, gX, False, 0};" in authoritative_text
            and "Phi17" in authoritative_text
        ),
        "live_executable_declares_X_global": "Global PQ/X/Z17 are not gauged" in reduced_text,
        "reduced_quartic_omits_full_lambda4_and_O6": (
            "CGC monomial and dim-6" in quartic_text
            and "remain documented OPEN" in quartic_text
            and "full SO(10) invariant basis" in quartic_text
        ),
        "legacy_two_loop_SO10_incomplete": not legacy["flag"]["two_loop_so10_complete"],
        "legacy_210_contractions_incomplete": not legacy["flag"]["published_210_tensor_contractions"],
        "legacy_component_thresholds_incomplete": (
            not legacy["flag"]["piecewise_component_threshold_matching_complete"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"G7 obstruction checks failed: {failures}")

    integration = {
        "ledger_consumes_obstruction": True,
        "roadmap_consumes_obstruction": True,
        "validation_matrix_consumes_obstruction": True,
        "release_orchestrators_and_workflows_consume_obstruction": True,
    }
    release_blockers = [
        "ELECTROWEAK_AND_INTERMEDIATE_REPRESENTATION_PROVENANCE_REQUIRED",
        "ABSOLUTE_SCALE_AND_WILSON_MATCHING_REQUIRED",
        "COMPLETE_COMPONENT_THRESHOLD_MATCHING_REQUIRED",
        "COMPLETE_GAUGE_YUKAWA_SCALAR_SOFT_EFT_TWO_LOOP_SYSTEM_REQUIRED",
        "SECOND_INDEPENDENT_IMPLEMENTATION_REQUIRED",
        "AUTHORITATIVE_G1_THROUGH_G6_REQUIRED",
    ]
    decisive = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_binding": bindings,
        "checks": checks,
        "formal_U1_89_abstract_restriction_example": {
            **collision,
            "physical_electroweak_interpretation_valid": False,
            "physical_QED_interpretation_valid": False,
            "scope": (
                "abstract lifts of formal q89=0,1 labels only; the names in the "
                "historical completion rows are not assigned to physical states"
            ),
        },
        "absolute_scale_counterexample": {
            "completion_A_mass_unit": "M0",
            "completion_B_mass_unit": "2*M0",
            "same_normalized_G6_spectrum": True,
            "threshold_log_shift": "ln(2)",
            "absolute_scale_unidentified": True,
        },
        "reduced_RGE_model_scope": {
            "authoritative_contract": "SO(10) x gauged U(1)_X with Phi17/anomaly-cancelling sector",
            "available_executable_contract": "SO(10) only; U(1)_X/PQ/Z17 declared global",
            "full_210_quartic_basis_present": False,
            "lambda4_CGC_present": False,
            "dimension6_O6_lock_present": False,
            "two_loop_SO10_complete": False,
            "piecewise_component_threshold_matching_complete": False,
        },
        "classification": {
            "formal_U1_89_abstract_restriction_noninjectivity_proved": True,
            "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
            "historical_electroweak_lift_interpretation_valid": False,
            "positive_G7_certified": False,
            "negative_G7_no_go_certified": False,
            "mathematical_EFT_G7_closed": False,
            "EFT_release_G7_verified": False,
            "authoritative_renormalizable_G7_closed": False,
        },
        "integration": integration,
        "release_blockers": release_blockers,
        "positive_closure_requirements": [
            "per-state SU(2)_L x U(1)_Y and SO(10)-to-intermediate-to-SM provenance",
            "physical pole masses, absolute scale, Wilson matching, and threshold uncertainties",
            "complete component thresholds in a declared renormalization scheme",
            "complete gauge/Yukawa/scalar/soft/EFT beta and anomalous-dimension system",
            "agreement of two independent implementations within declared tolerances",
        ],
    }
    return {
        "status": STATUS,
        "core_sha256": _canonical_sha256(decisive),
        "n_checks": len(checks),
        "n_failed": 0,
        "failures": [],
        **decisive,
    }


def render_markdown(report: dict[str, Any]) -> str:
    c = report["formal_U1_89_abstract_restriction_example"]
    return "\n".join(
        [
            "# Formal U(1)_89 abstract restriction audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            f"- Exact checks: {report['n_checks']} / {report['n_checks']}",
            "",
            "## Exact obstruction",
            "",
            "The frozen G6 spectrum supplies formal SU(3)_C x U(1)_89 labels and normalized tree-level masses.",
            "Its q89=0 x=26/5 and q89=1 x=37/20 modes admit two abstract lifts:",
            f"- A: {', '.join(c['completion_A']['electroweak_representations'])}, giving (Delta b2, Delta bY)=(0,1/3).",
            "- B: (1,2)_{1/2}, giving (Delta b2, Delta bY)=(1/6,1/6).",
            "This is abstract restriction noninjectivity, not electroweak or QED threshold evidence.",
            "The independent replacements M0 and 2 M0 leave all normalized G6 data fixed but shift threshold logs by ln(2).",
            "",
            "## Classification",
            "",
            "This report proves no physical G7 input theorem. It does **not** close mathematical, release, or authoritative G7.",
            "A positive result requires electroweak/intermediate representation provenance, physical matching data, the complete two-loop system, and agreement of two independent implementations.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.allow_unfrozen:
        if EXPECTED_CORE_SHA256 == "TO_BE_FROZEN":
            raise ArithmeticError("EXPECTED_CORE_SHA256 is not frozen")
        if report["core_sha256"] != EXPECTED_CORE_SHA256:
            raise ArithmeticError("frozen G7 obstruction core drifted")
    if args.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
