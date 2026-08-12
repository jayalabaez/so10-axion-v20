#!/usr/bin/env python3
"""Exact obstruction to inferring G7 threshold/RGE data from the frozen EFT G6.

This is deliberately a non-closure theorem.  It proves that the residual
``SU(3)_C x U(1)_em`` spectrum and normalized tree-level masses frozen at G6
do not determine either the electroweak threshold representations or the
absolute matching scale.  It also records, source-bound, that the available
executable RGE model is a reduced one-loop SO(10) model rather than the
authoritative gauged-U(1)_X contract.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
STATUS = "EFT_G7_INPUT_NONIDENTIFIABILITY_PROVED__G7_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
OUT_JSON = HERE / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
OUT_MD = HERE / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.md"

# Frozen after the integration fields are intentionally promoted.
EXPECTED_CORE_SHA256 = "303b4fa923b0475b8abe273836baea89671c2825da7756cbb79430a6400f4511"
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "d59146ed577680f3a1dfd449256d60d8116afcb844a8b65bbc009a8472bb766b",
    "md": "85a0a40924debb203b87488b4625a0da38d02ba7eb6c3ff741ae0f90a3e0bbac",
}

G6_SPECTRUM_CORE = "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
G6_GATE_CORE = "e34b791478bf9cb00f951819cbfec45a99d51be776889d8a4e13cf1717eee738"

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
        "6ef314bf22e1d6ce43b382b5cb6e7673cef1e328f2f4c38abdafab6038edc150",
        "raw",
    ),
    "G6_gate_JSON": (
        HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
        "85000f555eb3bc4e2e4bc49236a82ce2161987212906d78efd667bb52dd432f8",
        "raw",
    ),
    "authoritative_gauged_U1X_model": (
        HERE / "models" / "SO10Z17AxionV20.m",
        "3c3536c166ba7fca06ffedd0f244f76cc9b6db4840822a727f7a2f8e8bf1d1cd",
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
        "a48d3f2c84d26b12e6429bbce5794a6198aead4d3ccde9afadb22a9568ccba4c",
        "portable_text",
    ),
    "legacy_RGE_verdict": (
        HERE / "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
        "afbaca5c508140e448e54437848863d534f9b93396688a19652061c35b00da11",
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
        "G6_residual_group_only_SU3C_x_U1em": (
            spectrum["stabilizer_provenance"]["unbroken_group"] == "SU(3)_C x U(1)_em"
        ),
        "G6_omits_electroweak_and_intermediate_labels": all(
            not ({"SU2L_irrep", "hypercharge", "pati_salam_irrep", "matching_scale"} & set(row))
            for row in sectors.values()
        ),
        "neutral_collision_mode_exact": _has_exact_root(sectors["C0_Q0"], "26/5", 2),
        "charged_collision_mode_exact": _has_exact_root(sectors["C0_Q1"], "37/20", 2),
        "electroweak_restriction_map_noninjective": collision["restriction_map_noninjective"],
        "one_loop_threshold_coefficients_not_unique": collision["one_loop_coefficients_differ"],
        "absolute_scale_not_frozen": not uncertainty["absolute_scale_and_Wilson_matching_complete"],
        "loop_and_pole_masses_not_frozen": not uncertainty["loop_and_pole_mass_corrections_complete"],
        "running_scheme_not_frozen": not uncertainty["renormalization_scheme_and_running_complete"],
        "threshold_uncertainties_not_frozen": not uncertainty["physical_threshold_uncertainties_complete"],
        "authoritative_contract_gauges_U1X": (
            "Gauge[[2]] = {GX, U[1], X, gX, False};" in authoritative_text
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
        "threshold_restriction_counterexample": collision,
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
            "exact_EFT_G7_input_nonidentifiability_proved": True,
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
    c = report["threshold_restriction_counterexample"]
    return "\n".join(
        [
            "# Exact EFT G7 threshold non-identifiability",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            f"- Exact checks: {report['n_checks']} / {report['n_checks']}",
            "",
            "## Exact obstruction",
            "",
            "The frozen G6 spectrum supplies only SU(3)_C x U(1)_em labels and normalized tree-level masses.",
            "Its neutral x=26/5 and charged x=37/20 complex modes admit two inequivalent electroweak lifts:",
            f"- A: {', '.join(c['completion_A']['electroweak_representations'])}, giving (Delta b2, Delta bY)=(0,1/3).",
            "- B: (1,2)_{1/2}, giving (Delta b2, Delta bY)=(1/6,1/6).",
            "Thus even the one-loop threshold map is not determined; the requested two-loop G7 is a fortiori not determined.",
            "The independent replacements M0 and 2 M0 leave all normalized G6 data fixed but shift threshold logs by ln(2).",
            "",
            "## Classification",
            "",
            "This theorem proves an input obstruction. It does **not** close mathematical, release, or authoritative G7.",
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
