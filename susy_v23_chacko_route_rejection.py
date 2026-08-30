#!/usr/bin/env python3
"""Reject the unchanged Chacko--Mohapatra small-representation V23 route.

This certificate is deliberately narrow.  It tests the unchanged W1/W2
operator set with neutral fixed coefficients and the proposed four-dimensional
SO(10) spectrum containing nine 16s, five 10s, two 45s and one 54.  It does not
claim a no-go theorem for restructured/spurionic selectors or for every UV
completion of a small-representation model.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V23_CHACKO_ROUTE_REJECTION.json"
OUT_MD = ROOT / "SUSY_V23_CHACKO_ROUTE_REJECTION.md"
SCHEMA = "susy_v23_chacko_route_rejection_v1"

# Charge equations use E(m)=sum_i q_i-omega, where omega is the additive
# charge of the superpotential.  Vanishing E means that the monomial is
# allowed.  Keeping omega as an explicit coordinate makes every identity
# valid in an arbitrary additive Abelian group, including groups with torsion.
CHARGE_COORDINATES = (
    "S", "A", "Y", "C", "Cbar", "D", "Dbar", "T", "Tp",
    "P", "Pbar", "Abar", "H1", "H2", "omega",
)


def equation(*fields: str) -> tuple[int, ...]:
    values = {name: 0 for name in CHARGE_COORDINATES}
    for name in fields:
        if name == "omega":
            raise ValueError("omega is not a field")
        values[name] += 1
    values["omega"] = -1
    return tuple(values[name] for name in CHARGE_COORDINATES)


ALLOWED_EQUATIONS = {
    "S2": equation("S", "S"),
    "S3": equation("S", "S", "S"),
    "Y_tadpole": equation("Y"),
    "Y_C_Cbar": equation("Y", "C", "Cbar"),
    "f2_C_Abar_Pbar": equation("C", "Abar", "Pbar"),
    "f3_Cbar_Abar_P": equation("Cbar", "Abar", "P"),
    "h1_C_P_H1": equation("C", "P", "H1"),
    "h2_Cbar_Pbar_H2": equation("Cbar", "Pbar", "H2"),
    "Abar2": equation("Abar", "Abar"),
}


def linear_combination(coefficients: Mapping[str, int]) -> tuple[int, ...]:
    result = [0] * len(CHARGE_COORDINATES)
    for name, coefficient in coefficients.items():
        row = ALLOWED_EQUATIONS[name]
        result = [a + coefficient * b for a, b in zip(result, row)]
    return tuple(result)


def sparse_vector(vector: Iterable[int]) -> dict[str, int]:
    return {
        name: value
        for name, value in zip(CHARGE_COORDINATES, vector)
        if value
    }


IDENTITIES = {
    # 2 E(S^3)-3 E(S^2)=omega.  Since both allowed equations vanish,
    # omega=0; E(S^3)-E(S^2)=q(S) also forces q(S)=0.
    "superpotential_charge_is_zero": {
        "coefficients": {"S3": 2, "S2": -3},
        "target": tuple(1 if name == "omega" else 0 for name in CHARGE_COORDINATES),
        "formula": "2 E(S^3) - 3 E(S^2) = omega",
    },
    "S_charge_is_zero": {
        "coefficients": {"S3": 1, "S2": -1},
        "target": tuple(1 if name == "S" else 0 for name in CHARGE_COORDINATES),
        "formula": "E(S^3) - E(S^2) = q(S)",
    },
    # The Y tadpole is the neutral-constant term -M2^2 Y in W1.
    "P_Pbar_is_forced": {
        "coefficients": {
            "f2_C_Abar_Pbar": 1,
            "f3_Cbar_Abar_P": 1,
            "Y_C_Cbar": -1,
            "Y_tadpole": 1,
            "Abar2": -1,
        },
        "target": equation("P", "Pbar"),
        "formula": (
            "E(P Pbar) = E(f2) + E(f3) - E(Y C Cbar) "
            "+ E(Y) - E(Abar^2)"
        ),
    },
    "H1_H2_is_forced": {
        "coefficients": {
            "h1_C_P_H1": 1,
            "h2_Cbar_Pbar_H2": 1,
            "f2_C_Abar_Pbar": -1,
            "f3_Cbar_Abar_P": -1,
            "Abar2": 1,
        },
        "target": equation("H1", "H2"),
        "formula": "E(H1 H2) = E(h1) + E(h2) - E(f2) - E(f3) + E(Abar^2)",
    },
}

# Gauge singlets do not contribute.  T(R) is normalized by T(10)=1 and
# C2(R)=T(R) dim(G)/dim(R), with dim(SO(10))=45 and C2(G)=8.
GAUGE_REPRESENTATIONS = (
    {"representation": "16_or_16bar", "multiplicity": 9, "dimension": 16, "T": 2},
    {"representation": "10", "multiplicity": 5, "dimension": 10, "T": 1},
    {"representation": "45", "multiplicity": 2, "dimension": 45, "T": 8},
    {"representation": "54", "multiplicity": 1, "dimension": 54, "T": 12},
)
C2_G = 8
DIM_G = 45
ALPHA_GUT = Fraction(1, 24)
PLANCK_OVER_GUT = 120


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded)


def display_fraction(value: Fraction | int) -> int | str:
    value = Fraction(value)
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def gauge_coefficients(
    representations: Iterable[Mapping[str, int]] = GAUGE_REPRESENTATIONS,
) -> dict[str, Fraction | int]:
    rows = tuple(representations)
    sum_t = sum(Fraction(row["multiplicity"] * row["T"]) for row in rows)
    sum_c2_t = sum(
        Fraction(row["multiplicity"] * row["T"] * row["T"] * DIM_G, row["dimension"])
        for row in rows
    )
    b = sum_t - 3 * C2_G
    # Gauge-only N=1 SUSY coefficient in
    # d alpha/d ln(mu) = b alpha^2/(2 pi) + B alpha^3/(8 pi^2).
    big_b = -6 * C2_G**2 + 2 * C2_G * sum_t + 4 * sum_c2_t
    return {"sum_T": sum_t, "sum_C2_times_T": sum_c2_t, "b": b, "B": big_b}


def two_loop_log_scale(
    alpha_target: Fraction | float,
    *,
    alpha_initial: Fraction | float = ALPHA_GUT,
    b: int = 27,
    big_b: int = 1919,
) -> float:
    """Return ln(mu/MGUT) for the gauge-only two-loop alpha equation."""
    alpha = float(alpha_target)
    alpha0 = float(alpha_initial)
    if not (0 < alpha0 < alpha):
        raise ValueError("target alpha must exceed the positive initial alpha")
    a = b / (2 * math.pi)
    c = big_b / (8 * math.pi**2)

    def primitive(value: float) -> float:
        return -1 / (a * value) + (c / a**2) * math.log((a + c * value) / value)

    return primitive(alpha) - primitive(alpha0)


def additive_identity_report() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, identity in IDENTITIES.items():
        derived = linear_combination(identity["coefficients"])
        target = identity["target"]
        result[name] = {
            "formula": identity["formula"],
            "integer_coefficients": identity["coefficients"],
            "derived_vector": sparse_vector(derived),
            "target_vector": sparse_vector(target),
            "exact_match": derived == target,
        }
    return result


def gate_ledger() -> list[dict[str, Any]]:
    reasons = {
        "G1": "unchanged W1/W2 has no additive-Abelian selector that forbids P Pbar and H1 H2",
        "G2": "forced H1 H2 and absent normalized component Clebsches leave physical doublet/triplet ranks open",
        "G3": "no source-exact global F+D+soft vacuum and Hessian is landed",
        "G4": "hierarchy protection fails at G1 and perturbative UV control is lost below MPlanck",
        "G5": "no complete axion, inverse-seesaw and positive physical spectrum is landed",
        "G6": "gauge-only two-loop running reaches alpha=1 near 29.54 MGUT, below 120 MGUT",
        "G7": "the physical pole and threshold spectrum is dependency-blocked",
        "G8": "proton-decay matching and lifetime distribution are dependency-blocked",
    }
    return [
        {
            "gate": f"G{index}",
            "closed": False,
            "full_gate_claim": False,
            "state": "OPEN",
            "reason": reasons[f"G{index}"],
        }
        for index in range(1, 9)
    ]


def build_report() -> dict[str, Any]:
    identities = additive_identity_report()
    coefficients = gauge_coefficients()

    target_definitions = (
        ("1/10", Fraction(1, 10), 11.21385794),
        ("3/10", Fraction(3, 10), 25.49052495),
        ("1", Fraction(1), 29.54021000),
    )
    strong_scales = []
    for label, alpha, expected_ratio in target_definitions:
        log_scale = two_loop_log_scale(alpha)
        ratio = math.exp(log_scale)
        strong_scales.append({
            "alpha": label,
            "log_mu_over_MGUT": round(log_scale, 8),
            "mu_over_MGUT": round(ratio, 8),
            "expected_mu_over_MGUT": expected_ratio,
            "matches_expected_to_5e_minus_8": abs(ratio - expected_ratio) < 5e-8,
            "below_MPlanck_over_MGUT_120": ratio < PLANCK_OVER_GUT,
        })

    b_with_extra_45 = int(coefficients["b"] + 8)
    extra_45_pole_log = 2 * math.pi / (b_with_extra_45 * float(ALPHA_GUT))
    extra_45_pole_ratio = math.exp(extra_45_pole_log)
    # A rational certificate for ratio<120 uses the standard strict bounds
    # pi<22/7 and e<11/4:
    #   48 pi/35 < 1056/245 < 9/2,
    #   exp(9/2)=e^4 sqrt(e)<(11/4)^4(5/3)=73205/768<120.
    exponent_upper_from_pi = Fraction(48 * 22, 35 * 7)
    exp_upper_from_e = Fraction(11, 4) ** 4 * Fraction(5, 3)

    gates = gate_ledger()
    checks = {
        "all_four_additive_charge_identities_match_exactly":
            all(row["exact_match"] for row in identities.values()),
        "S2_and_S3_force_neutral_superpotential_and_neutral_S":
            identities["superpotential_charge_is_zero"]["exact_match"]
            and identities["S_charge_is_zero"]["exact_match"],
        "unchanged_W1_W2_force_P_Pbar_and_H1_H2":
            identities["P_Pbar_is_forced"]["exact_match"]
            and identities["H1_H2_is_forced"]["exact_match"],
        "spectrum_is_exactly_nine_16_five_10_two_45_one_54":
            [row["multiplicity"] for row in GAUGE_REPRESENTATIONS] == [9, 5, 2, 1],
        "one_loop_b_is_exactly_27": coefficients["b"] == 27,
        "sum_C2T_is_exactly_1487_over_4": coefficients["sum_C2_times_T"] == Fraction(1487, 4),
        "gauge_only_two_loop_B_is_exactly_1919": coefficients["B"] == 1919,
        "two_loop_target_scales_match_requested_values":
            all(row["matches_expected_to_5e_minus_8"] for row in strong_scales),
        "two_loop_loss_of_control_occurs_below_Planck120":
            all(row["below_MPlanck_over_MGUT_120"] for row in strong_scales),
        "extra_45B_raises_b_from_27_to_35": b_with_extra_45 == 35,
        "extra_45B_one_loop_pole_is_below_Planck120": extra_45_pole_ratio < PLANCK_OVER_GUT,
        "extra_45B_pole_bound_has_a_rational_certificate":
            exponent_upper_from_pi < Fraction(9, 2)
            and exp_upper_from_e == Fraction(73205, 768)
            and exp_upper_from_e < PLANCK_OVER_GUT,
        "all_G1_through_G8_full_claims_are_false_and_open":
            [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
            and all(row["closed"] is False and row["full_gate_claim"] is False for row in gates),
        "universal_small_rep_UV_no_go_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "rejected.susy_so10.v23.chacko_route",
        "status": (
            "V23_CHACKO_ROUTE_EXACTLY_REJECTED__SELECTOR_AND_TWO_LOOP_UV_OBSTRUCTIONS"
            if not failures else "V23_CHACKO_ROUTE_REJECTION_CERTIFICATE_FAILED"
        ),
        "overall_state": "ROUTE_REJECTED" if not failures else "FAIL_CLOSED_EXECUTION_ERROR",
        "scope": {
            "published_basis": "Chacko--Mohapatra small-representation missing-VEV route, hep-ph/9810315",
            "operator_assumption": "unchanged W1/W2 with neutral fixed coefficients",
            "running_assumption": (
                "four-dimensional N=1 SUSY SO(10), all listed nonsinglet chiral multiplets active above MGUT, "
                "gauge-only two-loop beta function"
            ),
            "alpha_SO10_at_MGUT": "1/24",
            "MPlanck_over_MGUT": PLANCK_OVER_GUT,
        },
        "additive_Abelian_rejection": {
            "charge_equation_convention": "E(monomial)=sum(field charges)-omega",
            "charge_domain": "arbitrary additive Abelian group; continuous, discrete and products are included",
            "allowed_equation_vectors": {
                name: sparse_vector(row) for name, row in ALLOWED_EQUATIONS.items()
            },
            "identities": identities,
            "conclusions": {
                "superpotential_charge_omega": 0,
                "genuine_R_selector_for_unchanged_W1_W2": False,
                "P_Pbar_can_be_forbidden": False,
                "H1_H2_can_be_forbidden": False,
            },
        },
        "gauge_running_rejection": {
            "representations": [dict(row) for row in GAUGE_REPRESENTATIONS],
            "group_invariants": {
                "dim_SO10": DIM_G,
                "C2_adjoint": C2_G,
                "C2_by_representation": {
                    row["representation"]: display_fraction(Fraction(row["T"] * DIM_G, row["dimension"]))
                    for row in GAUGE_REPRESENTATIONS
                },
            },
            "coefficient_convention": (
                "d alpha/d ln(mu) = b alpha^2/(2 pi) + B alpha^3/(8 pi^2)"
            ),
            "formulas": {
                "b": "sum_R T(R) - 3 C2(G)",
                "B_gauge_only": "-6 C2(G)^2 + 2 C2(G) sum_R T(R) + 4 sum_R C2(R) T(R)",
            },
            "sum_T": display_fraction(coefficients["sum_T"]),
            "sum_C2_times_T": display_fraction(coefficients["sum_C2_times_T"]),
            "b": display_fraction(coefficients["b"]),
            "B_gauge_only": display_fraction(coefficients["B"]),
            "two_loop_strong_coupling_scales": strong_scales,
            "Planck120_perturbative_completion_demonstrated": False,
        },
        "extra_45B_repair_rejection": {
            "proposal": "add one further SO(10) adjoint chiral multiplet 45B",
            "delta_sum_T": 8,
            "b_one_loop": b_with_extra_45,
            "one_loop_pole_log_mu_over_MGUT": round(extra_45_pole_log, 8),
            "one_loop_pole_mu_over_MGUT": round(extra_45_pole_ratio, 8),
            "rational_bound_chain": [
                "pi < 22/7 and e < 11/4",
                "48 pi/35 < 1056/245 < 9/2",
                "exp(48 pi/35) < (11/4)^4 (5/3) = 73205/768 < 120",
            ],
            "repairs_Planck120_running": False,
        },
        "gates": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "route_verdict": {
            "accepted_as_V23_completion": False,
            "rejected_as_complete_G1_G8_route": not failures,
            "safe_to_promote": False,
            "stop_promoting_unchanged_route": True,
            "reason": (
                "The unchanged W1/W2 selector is algebraically nonselective and the stated spectrum "
                "loses perturbative control below the Planck benchmark."
            ),
        },
        "claim_boundary": {
            "unchanged_neutral_coefficient_additive_Abelian_selector_excluded": not failures,
            "stated_gauge_only_two_loop_Planck120_trajectory_excluded": not failures,
            "all_restructured_or_spurionic_selectors_excluded": False,
            "all_small_representation_models_excluded": False,
            "an_interacting_gauge_Yukawa_UV_fixed_point_excluded": False,
            "a_higher_dimensional_or_threshold_UV_completion_excluded": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    running = report["gauge_running_rejection"]
    scales = running["two_loop_strong_coupling_scales"]
    repair = report["extra_45B_repair_rejection"]
    identity_lines = [
        f"- `{row['formula']}`"
        for row in report["additive_Abelian_rejection"]["identities"].values()
    ]
    scale_lines = [
        f"- `alpha={row['alpha']}` at `mu/MGUT={row['mu_over_MGUT']:.8f}`."
        for row in scales
    ]
    return "\n".join([
        "# SUSY V23 Chacko-route rejection", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full gates closed: `0/8`.", "",
        "## Exact additive-Abelian obstruction", "",
        "Write `E(m)=sum(q_i)-omega` for the charge-selection equation of a monomial.",
        "For unchanged W1/W2 with neutral fixed coefficients, exact integer identities give:", "",
        *identity_lines, "",
        "Thus `S^2+S^3` forces `omega=0`: the selector is not a genuine R symmetry.",
        "The same retained terms force both omitted bilinears `P Pbar` and `H1 H2`.", "",
        "## Gauge-running obstruction", "",
        f"The spectrum `9 x 16 + 5 x 10 + 2 x 45 + 1 x 54` has `sum T={running['sum_T']}`,",
        f"one-loop `b={running['b']}`, `sum C2*T={running['sum_C2_times_T']}`, and gauge-only",
        f"two-loop `B={running['B_gauge_only']}` in the convention recorded in the JSON.",
        "Starting from `alpha(MGUT)=1/24`, the integrated two-loop trajectory reaches:", "",
        *scale_lines, "",
        "The route therefore loses perturbative control before the benchmark reduced-Planck ratio `120`.", "",
        "## Rejected extra-adjoint repair", "",
        f"Adding `45B` raises the one-loop coefficient to `b={repair['b_one_loop']}` and puts the",
        f"one-loop pole at `mu/MGUT={repair['one_loop_pole_mu_over_MGUT']:.8f}<120`.",
        "The JSON includes a rational inequality certificate for this comparison.", "",
        "All G1--G8 completion claims remain false/open. This rejects only the unchanged route under",
        "the stated selector and running assumptions; restructured spurions, genuine gauge--Yukawa",
        "fixed points, threshold completions and other small-representation models are not excluded.", "",
    ])


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the frozen JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="fail if frozen outputs have drifted")
    args = parser.parse_args()

    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            raise FileNotFoundError("frozen V23 Chacko-route rejection outputs are missing")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V23 Chacko-route rejection JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V23 Chacko-route rejection Markdown drifted")

    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
