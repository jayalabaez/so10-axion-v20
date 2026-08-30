#!/usr/bin/env python3
"""Exact branch-mismatch certificate for the physical-SM G4/G5 frontier.

The source-exact five-amplitude theorem is a useful local/equality result, but
its frozen target is not the canonical electroweak-hierarchy branch consumed
by G4 and G5.  This module proves that statement without a floating-point
tolerance.

Both targets use the same canonical 486-real chart.  In that chart a complex
coefficient ``z`` is represented by ``(sqrt(2) Re z, sqrt(2) Im z)``.  The
five-amplitude target has exact block norms

    ||H||^2 / ||Phi||^2 = 2,

and its exact stationary-equality ideal forces ``p=1`` and ``h^2=1``.  The
authoritative G2 hierarchy input instead has one complex H component
``174 GeV / M_GUT`` and unit Phi norm, hence

    ||H||^2 / ||Phi||^2 = 2 (174 / M_GUT)^2.

The JSON decimal lexemes ``174.0`` and ``9917564798898606.0`` are interpreted
as exact rationals for this comparison.  Thus the two squared ratios differ by
the exact factor ``(M_GUT/174)^2``.  This is conditional on the frozen decimal
G2 input; it does not turn the numerically derived unification scale into a
fundamental exact observable.

Consequently, even a future source-exact 486-field Hessian at the present
five-amplitude target would not by itself close canonical G4 or G5.  This is
not a no-go theorem for another physical-EW branch or for a future hierarchy
mechanism.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md"

SCHEMA = "exact_physical_sm_g4_g5_branch_mismatch_v1"
STATUS = (
    "EXACT_FIVE_AMPLITUDE_VS_PHYSICAL_EW_BRANCH_MISMATCH_PROVED__"
    "CANONICAL_G4_G5_AND_DOWNSTREAM_G6_G8_OPEN"
)
CONTRACT_ID = "exact_physical_sm_g4_g5_branch_mismatch_v20"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"

# Filled after the core payload is frozen.  The core deliberately excludes
# output-file hashes, timestamps and this expected value.
EXPECTED_CORE_SHA256 = (
    "1b91227393a4402a8433d7947c2b1ce954ebc69ff7fbcc4e8606c61afcfdfdbe"
)

EXPECTED_FIVE_CORE_SHA256 = (
    "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"
)
EXPECTED_FOUNDATION_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)

# Text is bound by portable LF hashes.  JSON is bound by semantic canonical
# hashes so a CRLF checkout cannot change the theorem's provenance.
DEPENDENCIES: dict[str, dict[str, str]] = {
    "authoritative_G2_hierarchy_source": {
        "path": "gauged_u1x_g2_derivative_audit_v20.py",
        "mode": "portable_lf",
        "sha256": "584e03994ca1187228377c3e4c145d95446ade50616e2d58068e0fee9f96507d",
    },
    "canonical_486_chart_source": {
        "path": "live_g2_canonical_486_field_chart_v20.py",
        "mode": "portable_lf",
        "sha256": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
    },
    "authoritative_G2_hierarchy_report": {
        "path": "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        "mode": "semantic_json",
        "sha256": "725cd7582ff1d9b0c69e046ada9f34df413d72db76ce3a43d2fbce01d44eabef",
    },
    "five_amplitude_theorem_source": {
        "path": "exact_physical_sm_five_amplitude_equality_v20.py",
        "mode": "portable_lf",
        "sha256": "777b11664047574432405373b71bf30ed473fa735bdce56ef95be43dccc76972",
    },
    "five_amplitude_theorem_report": {
        "path": "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json",
        "mode": "semantic_json",
        "sha256": "03bbbf3e09ed045fa16b23b0a99135a6adcc8b5284f597bdf6cb8492bcafded9",
    },
    "physical_SM_target_foundation_source": {
        "path": "physical_sm_vacuum_local_feasibility_v20.py",
        "mode": "portable_lf",
        "sha256": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    },
    "physical_SM_target_foundation_report": {
        "path": "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
        "mode": "semantic_json",
        "sha256": "0b581ec26fa47bbfb6c331d1da2cf1b361cd455fda0eb141f16e1e400ca36ba8",
    },
}

EXPECTED_GROEBNER_BASIS = (
    "h**2 - 1",
    "d**2 - 1",
    "s**2 - 1",
    "x**2 - 1",
    "p - 1",
)


def _fraction_text(value: Fraction | int) -> str:
    result = Fraction(value)
    if result.denominator == 1:
        return str(result.numerator)
    return f"{result.numerator}/{result.denominator}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return _fraction_text(value)
    if isinstance(value, Decimal):
        return str(value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _portable_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _semantic_json_sha256(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _load_json_decimal(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_float=Decimal,
        parse_int=int,
    )


def _as_exact_fraction(name: str, value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{name} must not pass through binary floating point")
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"{name} must be finite")
        result = Fraction(value)
    elif isinstance(value, int):
        result = Fraction(value)
    elif isinstance(value, str):
        result = Fraction(value)
    else:
        raise TypeError(f"{name} must be an exact integer, decimal, string or Fraction")
    if result <= 0:
        raise ValueError(f"{name} must be strictly positive")
    return result


def source_guard() -> dict[str, Any]:
    bindings: dict[str, Any] = {}
    for name, specification in DEPENDENCIES.items():
        path = ROOT / specification["path"]
        if not path.is_file():
            raise FileNotFoundError(f"branch-mismatch dependency missing: {path.name}")
        mode = specification["mode"]
        if mode == "portable_lf":
            observed = _portable_lf_sha256(path)
        elif mode == "semantic_json":
            observed = _semantic_json_sha256(path)
        else:  # pragma: no cover - immutable table guard
            raise AssertionError(f"unsupported binding mode: {mode}")
        if observed != specification["sha256"]:
            raise ArithmeticError(f"branch-mismatch dependency drifted: {name}")
        bindings[name] = {
            "path": specification["path"],
            "binding_mode": mode,
            "observed_sha256": observed,
            "expected_sha256": specification["sha256"],
            "matches": True,
        }

    g2 = _load_json_decimal(ROOT / DEPENDENCIES["authoritative_G2_hierarchy_report"]["path"])
    five = _load_json_decimal(ROOT / DEPENDENCIES["five_amplitude_theorem_report"]["path"])
    foundation = _load_json_decimal(ROOT / DEPENDENCIES["physical_SM_target_foundation_report"]["path"])

    if g2.get("model_contract_id") != MODEL_CONTRACT_ID:
        raise ArithmeticError("authoritative G2 model contract drifted")
    if g2.get("authoritative_for_manuscript_G2_scalar_contract") is not True:
        raise ArithmeticError("G2 hierarchy report is not authoritative for the scalar contract")
    if g2.get("n_failed") != 0:
        raise ArithmeticError("authoritative G2 hierarchy report has failures")
    if five.get("model_contract_id") != MODEL_CONTRACT_ID or five.get("n_failed") != 0:
        raise ArithmeticError("five-amplitude theorem contract/status drifted")
    if five.get("integrity", {}).get("core_sha256") != EXPECTED_FIVE_CORE_SHA256:
        raise ArithmeticError("five-amplitude theorem core drifted")
    if foundation.get("model_contract_id") != MODEL_CONTRACT_ID:
        raise ArithmeticError("physical-SM foundation model contract drifted")
    if foundation.get("integrity", {}).get("core_sha256") != EXPECTED_FOUNDATION_CORE_SHA256:
        raise ArithmeticError("physical-SM foundation core drifted")

    g2_source = (ROOT / DEPENDENCIES["authoritative_G2_hierarchy_source"]["path"]).read_text(encoding="utf-8")
    chart_source = (ROOT / DEPENDENCIES["canonical_486_chart_source"]["path"]).read_text(encoding="utf-8")
    if "h[6] = 174.0 / m_gut" not in g2_source:
        raise ArithmeticError("G2 one-component H hierarchy formula drifted")
    if "z=(x+i y)/sqrt(2)" not in chart_source or "SQRT2 * source.real" not in chart_source:
        raise ArithmeticError("canonical complex-coordinate normalization drifted")

    return {
        "files": bindings,
        "all_dependency_pins_match": True,
        "five_amplitude_core_sha256": EXPECTED_FIVE_CORE_SHA256,
        "physical_SM_foundation_core_sha256": EXPECTED_FOUNDATION_CORE_SHA256,
        "shared_model_contract_id": MODEL_CONTRACT_ID,
    }


def _require_exact_branch_contracts(
    g2: Mapping[str, Any],
    five: Mapping[str, Any],
    foundation: Mapping[str, Any],
) -> None:
    hierarchy = g2.get("physical_hierarchy_state")
    if not isinstance(hierarchy, Mapping):
        raise ArithmeticError("authoritative G2 physical hierarchy state is absent")
    required_hierarchy_keys = {
        "M_GUT_GeV",
        "M_I_GeV",
        "h_EW_GeV",
        "Phi17_scale_GeV",
        "block_norms",
    }
    if not required_hierarchy_keys.issubset(hierarchy):
        raise ArithmeticError("authoritative G2 GeV unit contract is incomplete")
    if hierarchy.get("source") != "canonical physical hierarchy used by the existing G3 bridge":
        raise ArithmeticError("authoritative G2 branch label drifted")

    m_gut = _as_exact_fraction("M_GUT_GeV", hierarchy["M_GUT_GeV"])
    h_ew = _as_exact_fraction("h_EW_GeV", hierarchy["h_EW_GeV"])
    if m_gut <= h_ew:
        raise ArithmeticError("GUT/EW hierarchy ordering was swapped or destroyed")
    norms = hierarchy["block_norms"]
    if not isinstance(norms, Mapping) or _as_exact_fraction("G2 Phi norm", norms.get("Phi210")) != 1:
        raise ArithmeticError("authoritative G2 Phi normalization drifted")

    basis = five.get("exact_Groebner_certificate", {}).get("expected_reduced_Groebner_basis")
    if tuple(basis or ()) != EXPECTED_GROEBNER_BASIS:
        raise ArithmeticError("five-amplitude stationary-equality basis drifted")
    if five.get("restriction", {}).get("map") != "(Phi,H,Sigma,S,Phi17)=(p Phi*,h H*,d Sigma*,s S*,x Phi17*)":
        raise ArithmeticError("five-amplitude branch map drifted")

    target_norms = foundation.get("target", {}).get("field_block_q_norm_squared")
    if not isinstance(target_norms, Mapping):
        raise ArithmeticError("five-amplitude foundation block norms are absent")
    if _as_exact_fraction("target Phi norm squared", target_norms.get("Phi210")) != 1:
        raise ArithmeticError("five-amplitude target Phi normalization drifted")
    if _as_exact_fraction("target H norm squared", target_norms.get("H10")) != 2:
        raise ArithmeticError("five-amplitude target H normalization drifted")


def physical_hierarchy_squared_ratio(
    m_gut: Any,
    h_ew: Any,
    *,
    m_gut_unit: str = "GeV",
    h_ew_unit: str = "GeV",
) -> Fraction:
    """Return exact ``||H||^2/||Phi||^2`` for the one-component G2 branch."""
    if m_gut_unit != h_ew_unit:
        raise ValueError("M_GUT and h_EW must be expressed in the same unit")
    if not m_gut_unit.strip():
        raise ValueError("the common mass unit must be declared")
    m_value = _as_exact_fraction("M_GUT", m_gut)
    h_value = _as_exact_fraction("h_EW", h_ew)
    if m_value <= h_value:
        raise ArithmeticError("the declared physical hierarchy must satisfy M_GUT > h_EW")
    return 2 * (h_value / m_value) ** 2


def branch_mismatch_certificate(
    g2: Mapping[str, Any] | None = None,
    five: Mapping[str, Any] | None = None,
    foundation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the exact certificate, allowing mutated dictionaries in tests."""
    g2_payload = g2 or _load_json_decimal(
        ROOT / DEPENDENCIES["authoritative_G2_hierarchy_report"]["path"]
    )
    five_payload = five or _load_json_decimal(
        ROOT / DEPENDENCIES["five_amplitude_theorem_report"]["path"]
    )
    foundation_payload = foundation or _load_json_decimal(
        ROOT / DEPENDENCIES["physical_SM_target_foundation_report"]["path"]
    )
    _require_exact_branch_contracts(g2_payload, five_payload, foundation_payload)

    hierarchy = g2_payload["physical_hierarchy_state"]
    m_gut = _as_exact_fraction("M_GUT_GeV", hierarchy["M_GUT_GeV"])
    h_ew = _as_exact_fraction("h_EW_GeV", hierarchy["h_EW_GeV"])
    target_norms = foundation_payload["target"]["field_block_q_norm_squared"]
    five_ratio = _as_exact_fraction("target H norm squared", target_norms["H10"]) / _as_exact_fraction(
        "target Phi norm squared", target_norms["Phi210"]
    )
    physical_ratio = physical_hierarchy_squared_ratio(m_gut, h_ew)
    mismatch_factor = five_ratio / physical_ratio

    # The stored float-like diagnostic is never used to prove the mismatch.
    # It only checks that the report was produced with the pinned chart.
    observed_h_norm = Decimal(str(hierarchy["block_norms"]["H10"]))
    observed_h_norm_squared = Fraction(observed_h_norm * observed_h_norm)
    diagnostic_difference = abs(observed_h_norm_squared - physical_ratio)

    return {
        "comparison_domain": "QQ after exact parsing of the frozen JSON decimal lexemes",
        "shared_chart": "canonical 486-real chart with z=(x+i y)/sqrt(2)",
        "shared_mass_unit": "GeV",
        "frozen_decimal_input_semantics": {
            "M_GUT_GeV_lexeme_as_exact_rational": _fraction_text(m_gut),
            "h_EW_GeV_lexeme_as_exact_rational": _fraction_text(h_ew),
            "limitation": (
                "the comparison is exact conditional on these frozen decimal inputs; "
                "it does not certify the numerically derived M_GUT as a fundamental exact value"
            ),
        },
        "five_amplitude_branch": {
            "stationary_equality_constraints": ["p=1", "h^2=1"],
            "Phi_q_norm_squared": _fraction_text(Fraction(target_norms["Phi210"])),
            "H_q_norm_squared": _fraction_text(Fraction(target_norms["H10"])),
            "H_over_Phi_squared": _fraction_text(five_ratio),
        },
        "canonical_G2_physical_EW_branch": {
            "H_complex_component": "174 GeV / M_GUT",
            "Phi_q_norm_squared": "1",
            "H_over_Phi_squared_formula": "2*(174/M_GUT)^2",
            "H_over_Phi_squared_exact": _fraction_text(physical_ratio),
            "reported_H_q_norm_decimal": str(hierarchy["block_norms"]["H10"]),
            "reported_norm_squared_minus_exact_formula_abs": _fraction_text(diagnostic_difference),
            "reported_norm_is_diagnostic_not_proof": True,
        },
        "exact_mismatch": {
            "ratios_are_equal": five_ratio == physical_ratio,
            "five_over_physical_squared_ratio": _fraction_text(mismatch_factor),
            "five_over_physical_norm_ratio": _fraction_text(m_gut / h_ew),
            "cross_multiplication_nonzero": _fraction_text(five_ratio - physical_ratio),
            "mismatch_exceeds_10_pow_26_in_squared_ratio": mismatch_factor > 10**26,
            "common_unit_rescaling_can_remove_mismatch": False,
        },
    }


def common_unit_rescaling_audit_0_through_100() -> dict[str, Any]:
    """Prove the ratio comparison is invariant under 101 common unit changes."""
    g2 = _load_json_decimal(
        ROOT / DEPENDENCIES["authoritative_G2_hierarchy_report"]["path"]
    )
    hierarchy = g2["physical_hierarchy_state"]
    m_gut = _as_exact_fraction("M_GUT_GeV", hierarchy["M_GUT_GeV"])
    h_ew = _as_exact_fraction("h_EW_GeV", hierarchy["h_EW_GeV"])
    reference = physical_hierarchy_squared_ratio(m_gut, h_ew)
    records: list[dict[str, Any]] = []
    for case in range(101):
        common_scale = Fraction(case + 1, 51)
        rescaled = physical_hierarchy_squared_ratio(
            common_scale * m_gut,
            common_scale * h_ew,
            m_gut_unit="common_exact_unit",
            h_ew_unit="common_exact_unit",
        )
        records.append(
            {
                "case": case,
                "common_scale": _fraction_text(common_scale),
                "ratio_unchanged": rescaled == reference,
            }
        )
    return {
        "case_range": [0, 100],
        "case_count": len(records),
        "identity_case": 50,
        "all_common_rescalings_preserve_ratio": all(
            row["ratio_unchanged"] for row in records
        ),
        "records_sha256": hashlib.sha256(canonical_json_bytes(records)).hexdigest(),
        "first_case": records[0],
        "identity_record": records[50],
        "last_case": records[-1],
    }


def gate_acceptance_boundary() -> dict[str, Any]:
    return {
        "G4": {
            "canonical_required_artifact": "EW_HIERARCHY_MECHANISM_V20.json",
            "five_amplitude_witness_is_the_canonical_h_174_GeV_branch": False,
            "h_174_GeV_hierarchy_mechanism_demonstrated": False,
            "radiative_stability_or_symmetry_protection_demonstrated": False,
            "physical_SM_G4_closed": False,
            "release_G4_closed": False,
            "authoritative_G4_closed": False,
        },
        "G5": {
            "canonical_required_artifact": "CAL_G_LOCK_PHYSICAL_EW_REVALIDATION_V20.json",
            "same_surviving_physical_EW_branch_used": False,
            "live_phase_component_Hessian_on_that_branch_complete": False,
            "physical_SM_G5_closed": False,
            "release_G5_closed": False,
            "authoritative_G5_closed": False,
        },
        "G6": {
            "promoted_by_this_branch_certificate": False,
            "physical_SM_G6_closed": False,
            "release_G6_closed": False,
            "authoritative_G6_closed": False,
        },
        "G7": {
            "promoted_by_this_branch_certificate": False,
            "physical_SM_G7_closed": False,
            "release_G7_closed": False,
            "authoritative_G7_closed": False,
        },
        "G8": {
            "promoted_by_this_branch_certificate": False,
            "physical_SM_G8_closed": False,
            "release_G8_closed": False,
            "authoritative_G8_closed": False,
        },
    }


def _core_payload(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: report[key]
        for key in (
            "schema",
            "status",
            "contract_id",
            "model_contract_id",
            "source_binding",
            "exact_branch_mismatch",
            "unit_rescaling_audit_0_through_100",
            "gate_acceptance_boundary",
            "scope",
            "next_required_work",
        )
    }


def build_report() -> dict[str, Any]:
    binding = source_guard()
    mismatch = branch_mismatch_certificate()
    rescaling = common_unit_rescaling_audit_0_through_100()
    gates = gate_acceptance_boundary()
    closure_flags = [
        value
        for gate in gates.values()
        for key, value in gate.items()
        if key.endswith("_closed")
    ]
    scope = {
        "exact_branch_mismatch_proved": True,
        "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G4": False,
        "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G5": False,
        "global_no_go_for_all_possible_physical_EW_branches": False,
        "new_hierarchy_mechanism_ruled_out": False,
        "physical_G4_G5_G6_G7_G8_closed": False,
        "release_G4_G5_G6_G7_G8_closed": False,
        "authoritative_G4_G5_G6_G7_G8_closed": False,
    }
    checks = {
        "all_dependency_pins_match": binding["all_dependency_pins_match"],
        "five_amplitude_ratio_is_exactly_two": mismatch["five_amplitude_branch"]["H_over_Phi_squared"] == "2",
        "physical_hierarchy_ratio_is_exact_nonzero": Fraction(mismatch["canonical_G2_physical_EW_branch"]["H_over_Phi_squared_exact"]) > 0,
        "branch_ratios_are_exactly_unequal": mismatch["exact_mismatch"]["ratios_are_equal"] is False,
        "mismatch_exceeds_10_pow_26": mismatch["exact_mismatch"]["mismatch_exceeds_10_pow_26_in_squared_ratio"],
        "all_101_common_unit_rescalings_preserve_ratio": rescaling["all_common_rescalings_preserve_ratio"],
        "unit_audit_covers_cases_0_through_100": rescaling["case_range"] == [0, 100] and rescaling["case_count"] == 101,
        "all_G4_through_G8_closure_flags_fail_closed": not any(closure_flags),
        "current_witness_not_promoted_to_canonical_G4_or_G5": not scope["source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G4"] and not scope["source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G5"],
        "not_misrepresented_as_global_no_go": scope["global_no_go_for_all_possible_physical_EW_branches"] is False,
    }
    failures = sorted(key for key, passed in checks.items() if not passed)
    if failures:
        raise ArithmeticError(f"G4/G5 branch-mismatch checks failed: {failures}")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "contract_id": CONTRACT_ID,
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_binding": binding,
        "exact_branch_mismatch": mismatch,
        "unit_rescaling_audit_0_through_100": rescaling,
        "gate_acceptance_boundary": gates,
        "scope": scope,
        "next_required_work": [
            "construct or identify a technically stable h=174 GeV branch in the authoritative field/charge contract",
            "derive its complete source-algebra stationarity and gauge-projected component Hessian",
            "prove radiative stability or an exact protecting symmetry before canonical G4",
            "revalidate the cal-G and axion phase directions on that same surviving branch before G5",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "verdict": (
            "The exact five-amplitude stationary-equality target and the canonical "
            "G2 physical-EW hierarchy target are different branches in the shared "
            "486-real normalization. Their H/Phi squared-norm ratios differ by "
            "the exact frozen-input factor (M_GUT/174)^2. Therefore the present "
            "five-amplitude theorem, even with a future source-exact Hessian at "
            "that target, cannot by itself promote canonical G4 or G5. This is "
            "not a no-go for a different protected h=174 GeV branch. G4-G8 remain open."
        ),
    }
    core = hashlib.sha256(canonical_json_bytes(_core_payload(report))).hexdigest()
    report["integrity"] = {"core_sha256": core}
    if EXPECTED_CORE_SHA256 and core != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"branch-mismatch core drifted: expected {EXPECTED_CORE_SHA256}, observed {core}"
        )
    return _jsonable(report)


def render_markdown(report: Mapping[str, Any]) -> str:
    mismatch = report["exact_branch_mismatch"]
    return "\n".join(
        [
            "# Exact physical-SM G4/G5 branch-mismatch certificate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact comparison",
            "",
            f"- Five-amplitude `||H||²/||Phi||²`: `{mismatch['five_amplitude_branch']['H_over_Phi_squared']}`.",
            f"- Canonical physical-EW `||H||²/||Phi||²`: `{mismatch['canonical_G2_physical_EW_branch']['H_over_Phi_squared_exact']}`.",
            f"- Squared-ratio mismatch factor: `{mismatch['exact_mismatch']['five_over_physical_squared_ratio']}`.",
            f"- Norm-ratio mismatch factor: `{mismatch['exact_mismatch']['five_over_physical_norm_ratio']}`.",
            "- The comparison parses the frozen GeV decimal lexemes as exact rationals; it does not claim the fitted unification scale is fundamentally exact.",
            "- 101 exact common-unit rescalings (cases 0–100) leave the mismatch unchanged.",
            "",
            "## Claim boundary",
            "",
            "A source-exact Hessian at the current order-one-H five-amplitude target would still not establish the required protected `h=174 GeV` branch. Canonical physical, release and authoritative G4–G8 remain false. This certificate is not a global no-go for other branches or new hierarchy mechanisms.",
            "",
            f"Core SHA-256: `{report['integrity']['core_sha256']}`.",
            "",
        ]
    )


def _write_or_check(*, check: bool) -> dict[str, Any]:
    report = build_report()
    json_bytes = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    md_bytes = render_markdown(report).encode("utf-8")
    if check:
        if not OUT_JSON.is_file() or OUT_JSON.read_bytes() != json_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_JSON.name}")
        if not OUT_MD.is_file() or OUT_MD.read_bytes() != md_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_MD.name}")
    else:
        OUT_JSON.write_bytes(json_bytes)
        OUT_MD.write_bytes(md_bytes)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write or args.check:
        report = _write_or_check(check=args.check)
    else:
        report = build_report()
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["integrity"]["core_sha256"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
