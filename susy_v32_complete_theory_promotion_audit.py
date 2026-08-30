#!/usr/bin/env python3
"""V32 evidence-grade promotion audit for the SUSY Pati--Salam G1--G8 theory.

V31 deliberately used two invented axioms, FCMA-18 and BFA-8, to make one
conditional benchmark.  V32 asks the harder question required for a complete
theory: are the asserted quantities derived from the declared source, and do
the calculations remain valid when all declared thresholds and mechanisms are
included?

The answer is fail-closed.  V32 preserves the useful V24--V31 construction,
but it does not allow an axiom to certify its own microscopic origin.  It also
lands four concrete diagnostics:

* infinite all-order X^(2m+1) and P^(11+22 k) operator towers allowed by
  Z4R x Z11;
* the omitted universal KSVZ threshold Delta b=(4,4,4) between fPQ and MPS;
* exact tree and leading one-loop Higgs diagnostics plus an input-dependency
  mutation test for the hard-coded pole ledger;
* rejection of V31's Pati--Salam gauge-vector proton lifetime, because the
  declared PS gauge bosons do not mediate proton decay at renormalizable level.

The resulting counts are intentionally separate: V31 reported 8/8 conditional
rows; after the inherited domain-wall and proton mechanisms are checked, no
more than 5/8 V31-style conditional rows survive; and 0/8 full predictive gates
are established.  The 5/8 value is only an upper bound because G1 still assumes
FCMA-18 and has additional local-UV consistency failures.  This is a completed
audit and research frontier, not a claim that a complete fundamental theory has
been discovered.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import susy_v31_g1_g8_unified_completion as v31


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V32_COMPLETE_THEORY_PROMOTION_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V32_COMPLETE_THEORY_PROMOTION_AUDIT.md"
PHYSICS_JSON = ROOT / "SUSY_V32_CORRECTED_PHYSICS_LEDGER.json"
GATES_JSON = ROOT / "SUSY_V32_G1_G8_GATE_LEDGER.json"
REQUIRED_JSON = ROOT / "SUSY_V32_REQUIRED_DERIVATIONS.json"

STATUS = (
    "V32_COMPLETE_THEORY_PROMOTION_AUDIT_COMPLETE__V31_PQ_THRESHOLD_"
    "CORRECTED__PATI_SALAM_VECTOR_PROTON_CHANNEL_REJECTED__CORRECTED_"
    "CONDITIONAL_UPPER_BOUND_FIVE_OF_EIGHT__ESTABLISHED_ZERO_OF_EIGHT__"
    "NO_COMPLETE_THEORY"
)

SOURCE_PINS = {
    "susy_v24_ps_vacuum_rg_frontier.py":
        "c5af70ab22756d79eb72a4d5a3c2c23f86a1f1378cb8e09c1e67076609d44125",
    "SUSY_V24_PS_VACUUM_RG_FRONTIER.json":
        "4f47ca9b18902a744c138ddceeec461036e41c6803bb7d60a68a276e09499c0d",
    "SUSY_V24_G1_G8_EXECUTION_VERDICT.json":
        "42b674dc6fe137979ea3d6067efa02bd4531298688b2086d99affa2a61b7f047",
    "susy_v30_g1_finite_flux_completion.py":
        "f3ff7f581ec394e96c7efe7ebd20c9389942eedbf52d0d5fb53e4152df0de651",
    "SUSY_V30_G1_FINITE_FLUX_COMPLETION.json":
        "ebf43b48feb4b00233eccdf36d5755d700726077dd64d74cfc9cd2507bdb0de0",
    "SUSY_V30_FIELD_AND_SELECTOR_MANIFEST.json":
        "80474e4950bbecebb3a02f678783df26495f8cac21e578a69858ffab59e7f686",
    "SUSY_V30_OPERATOR_AND_MATCHING_CONTRACT.json":
        "7cb6f39c85d788937418f61eca9e98c46c21a95549bb220b351ef9e27bff2c6f",
    "SUSY_V30_MODULI_AND_HIDDEN_CONTRACT.json":
        "2231ef13110662a10d1900f3cbb3fc425610191c80defc8c2effae0cb812eba2",
    "susy_v31_g1_g8_unified_completion.py":
        "1f7ae0438454bd1538f0374db22c1f31a6118128e4c111d7fe3ff55724d110a5",
    "SUSY_V31_G1_G8_UNIFIED_COMPLETION.json":
        "017206b65c4a42db2f371da1a54304563e913796d33df7dd86a0531b2f6782bf",
    "SUSY_V31_BENCHMARK_INPUT_LEDGER.json":
        "d54cf0dd2b9775fd191a03c940ec5dbc1771b3c4db740ece961c8ab92db7ec05",
    "SUSY_V31_SPECTRUM_VACUUM_LEDGER.json":
        "e5614165654fa351fc89b1df2c6ee3ede027bcb24fc1eb0d80fd3005e9384ed9",
    "SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json":
        "4f40733abcc3adcdfa32ceedc8c9fcefd5b6057261856fe36514387671073d0f",
    "SUSY_V31_G1_G8_GATE_LEDGER.json":
        "fe3c7311d8130139620a4dfd082f8a6477a5d2629e18e1a06cc2fd078eda01f6",
}

UPSTREAM_CORES = {
    "V24": "09b4b232afe0f5150dab74e5fc28f1984551732d9e100c1687971b96410adacd",
    "V30": "e504aed2ac39cec33a23a3779ea5d99cdbec2592bd16a2ba4353706b21148a28",
    "V31": "8c5dd7ed69871822f96c98f72a099045f4a33c0dad182e096244f3441d21ed95",
}

PRIMARY_REFERENCES = [
    {
        "topic": "original Pati--Salam axion/KSVZ scaffold",
        "url": "https://arxiv.org/abs/2009.04582",
        "audit_use": "field-content and PQ/domain-wall normalization provenance",
    },
    {
        "topic": "Pati--Salam baryon-number violation",
        "url": "https://arxiv.org/abs/2211.02054",
        "audit_use": (
            "PS gauge bosons do not mediate proton decay at renormalizable level; "
            "dimension-five operators require their own matching"
        ),
    },
    {
        "topic": "three-form supergravity duality",
        "url": "https://arxiv.org/abs/1706.09422",
        "audit_use": (
            "three-form duality promotes specific existing superpotential couplings, "
            "not an arbitrary benchmark ledger"
        ),
    },
    {
        "topic": "constrained superfields",
        "url": "https://arxiv.org/abs/0907.2441",
        "audit_use": "nilpotent constrained fields are an infrared SUSY-breaking formalism",
    },
    {
        "topic": "explicit moduli-stabilization precedent",
        "url": "https://arxiv.org/abs/hep-th/0503124",
        "audit_use": (
            "a real compactification can fix moduli, but it is not a derivation of the "
            "chiral V24 Pati--Salam source or FCMA-18"
        ),
    },
    {
        "topic": "fluxed instantons with chiral visible sectors",
        "url": "https://arxiv.org/abs/1105.3193",
        "audit_use": (
            "charged instanton zero modes create a concrete chirality/moduli-stabilization "
            "constraint that V30 does not calculate"
        ),
    },
    {
        "topic": "mixed axion/neutralino cosmology",
        "url": "https://arxiv.org/abs/1309.5365",
        "audit_use": (
            "relic closure requires axino/saxion production, decay, freeze-out, and "
            "re-annihilation calculations"
        ),
    },
    {
        "topic": "thermal leptogenesis bound",
        "url": "https://arxiv.org/abs/hep-ph/0202239",
        "audit_use": (
            "the R=I, diagonal YdaggerY benchmark has no standard decay CP asymmetry, "
            "and its reheating temperature is below the lightest right-neutrino mass"
        ),
    },
    {
        "topic": "current natural-SUSY axion/axino constraints",
        "url": "https://arxiv.org/abs/2604.04687",
        "audit_use": "a depleted higgsino abundance does not by itself close direct detection",
    },
    {
        "topic": "LZ WIMP direct detection",
        "url": "https://arxiv.org/abs/2410.17036",
        "audit_use": "V31 supplies no spin-independent cross section or likelihood",
    },
]


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


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


def read_json(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def finite_selector_tower() -> dict[str, Any]:
    """Construct an exact infinite tower allowed by the selected finite charges."""
    p_samples = []
    for k in range(4):
        power = 11 + 22 * k
        p_samples.append(
            {
                "k": k,
                "operator": f"P^{power}",
                "power": power,
                "Z4R_charge": (2 * power) % 4,
                "Z11_charge": power % 11,
                "allowed_superpotential_charge": (
                    (2 * power) % 4 == 2 and power % 11 == 0
                ),
            }
        )
    x_samples = []
    for m in range(4):
        power = 2 * m + 1
        x_samples.append(
            {
                "m": m,
                "operator": f"X^{power}",
                "power": power,
                "Z4R_charge": (2 * power) % 4,
                "Z11_charge": 0,
                "PQ_charge": 0,
                "allowed_superpotential_charge": (2 * power) % 4 == 2,
            }
        )
    return {
        "selected_charges": {
            "P": {"Z4R": 2, "Z11": 1, "PQ": 1},
            "X": {"Z4R": 2, "Z11": 0, "PQ": 0},
        },
        "towers": ["X^(2*m+1), m>=0", "P^(11+22*k), k>=0"],
        "X_sample_witnesses": x_samples,
        "P_sample_witnesses": p_samples,
        "all_samples_allowed": all(
            row["allowed_superpotential_charge"]
            for row in x_samples + p_samples
        ),
        "proof": (
            "Every odd power of X has Z4R charge 2 and no other charge.  For "
            "n=11+22k, P^n also has Z4R charge 2 and Z11 charge 0.  The finite "
            "selector therefore permits two explicit infinite superpotential towers; "
            "FCMA-18 is an extra truncation axiom, not a consequence of Z4R x Z11."
        ),
    }


def v30_local_uv_consistency_audit(
    v30_operator: dict[str, Any],
    v30_moduli: dict[str, Any],
    v30_manifest: dict[str, Any],
    v31_inputs: dict[str, Any],
    v31_spectrum: dict[str, Any],
) -> dict[str, Any]:
    """Test whether the V30 instanton/three-form story is a controlled local UV model."""
    x_star = 0.5
    instanton_action = -math.log(x_star)
    t_star = instanton_action / (2.0 * math.pi)
    z11_phase_exponents = [(9 * n) % 11 for n in (1, 2, 3)]
    z4r_signs = [-1 if n % 2 else 1 for n in (1, 2, 3)]
    nonzero_soft_inputs = {
        key: value
        for key, value in v31_inputs["soft_benchmark"].items()
        if key
        not in {
            "MSUSY_GeV",
            "tan_beta",
        }
        and value not in (0, 0.0)
    }
    gravitino_mass = next(
        row["pole_mass_GeV"]
        for row in v31_spectrum["pole_spectrum"]
        if row["sector"] == "gravitino"
    )
    return {
        "semiclassical_instanton_control": {
            "x_star": x_star,
            "Re_T_star": t_star,
            "instanton_action_2pi_ReT": instanton_action,
            "action_greater_than_one": instanton_action > 1.0,
            "first_omitted_order_one_x4_term": x_star**4,
            "controlled_E3_expansion_demonstrated": False,
            "reason": (
                "x=1/2 makes the instanton action ln(2)<1, so an omitted order-one "
                "x^4 term is 1/16 and the cubic cancellation is not parametrically stable"
            ),
        },
        "discrete_gauge_covariance": {
            "T01_affine_shifts": v30_manifest["anomaly_and_level_matrix"][
                "T01_affine_shifts"
            ],
            "three_form_coefficients_selector_neutral": (
                "selector-neutral"
                in v30_manifest["new_multiplets"][
                    "three_form_selector_and_anomaly_role"
                ]
            ),
            "all_primitive_E3_charged_zero_modes": sorted(
                {
                    row["charged_zero_modes"]
                    for row in v30_moduli["instanton_inventory"]
                }
            ),
            "Z11_phase_exponents_for_x_x2_x3": z11_phase_exponents,
            "Z4R_signs_for_x_x2_x3": z4r_signs,
            "terms_transform_covariantly_with_neutral_coefficients": (
                len(set(z11_phase_exponents)) == 1 and len(set(z4r_signs)) == 1
            ),
            "required_repair": (
                "derive charged insertions/zero modes or a transforming flux branch and "
                "then derive the residual subgroup"
            ),
        },
        "three_form_scope": {
            "declared_three_form_count": v30_manifest["new_multiplets"][
                "gauge_three_form_multiplets"
            ],
            "declared_role": v30_manifest["new_multiplets"][
                "three_form_selector_and_anomaly_role"
            ],
            "duality_generates_arbitrary_operator_projector": False,
            "duality_replaces_only_auxiliary_components_of_chiral_multiplets": True,
            "boundary": (
                "three-form duality promotes specific pre-existing couplings; a ten-"
                "dimensional p-form/cycle and membrane charge are still needed for every "
                "independent flux coefficient"
            ),
        },
        "SUSY_breaking_contract": {
            "V30_all_soft_terms": v30_operator["soft_contract"]["all_soft_terms"],
            "V31_nonzero_soft_inputs": nonzero_soft_inputs,
            "V31_gravitino_mass_GeV": gravitino_mass,
            "explicit_goldstino_or_uplift_sector_present": False,
            "V30_to_V31_single_N1_vacuum_derived": False,
        },
        "FCMA18_local_UV_interpretation_consistent": False,
        "conditional_G1_may_only_be_retained_by_treating_FCMA18_as_fundamental": True,
    }


def _fraction_matrix(rows: list[list[Any]]) -> list[list[float]]:
    return [
        [float(Fraction(str(value))) for value in row]
        for row in rows
    ]


def _fraction_vector(values: list[Any]) -> list[float]:
    return [float(Fraction(str(value))) for value in values]


def rk4_two_loop_gauge_alpha(
    alpha_start: list[float],
    beta_one: list[float],
    beta_two: list[list[float]],
    log_ratio: float,
) -> list[float]:
    """Gauge-only two-loop RK4 in alpha variables, matching the V24 convention."""
    steps = max(64, int(abs(log_ratio) * 250.0))
    step = log_ratio / steps

    def derivative(values: list[float]) -> list[float]:
        return [
            values[i] ** 2
            / (2.0 * math.pi)
            * (
                beta_one[i]
                + sum(beta_two[i][j] * values[j] for j in range(3))
                / (4.0 * math.pi)
            )
            for i in range(3)
        ]

    values = list(alpha_start)
    for _ in range(steps):
        k1 = derivative(values)
        k2 = derivative(
            [values[i] + step * k1[i] / 2.0 for i in range(3)]
        )
        k3 = derivative(
            [values[i] + step * k2[i] / 2.0 for i in range(3)]
        )
        k4 = derivative([values[i] + step * k3[i] for i in range(3)])
        values = [
            values[i]
            + step * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) / 6.0
            for i in range(3)
        ]
    return values


def gauge_only_two_loop_root(
    baseline: dict[str, Any],
    v24_frontier: dict[str, Any],
    ms: float,
    fa: float,
) -> dict[str, Any]:
    """Solve the V24 gauge-only two-loop PS matching problem in two log scales."""
    below = v24_frontier["RG_below_PS"]
    above = v24_frontier["RG_above_PS"]
    b_mssm = _fraction_vector(below["MSSM"]["b"])
    big_mssm = _fraction_matrix(below["MSSM"]["B"])
    b_vector = _fraction_vector(below["MSSM_plus_vectorlike_family"]["b"])
    big_vector = _fraction_matrix(
        below["MSSM_plus_vectorlike_family"]["B"]
    )
    b_ps = _fraction_vector(above["b"])
    big_ps = _fraction_matrix(above["B"])
    alpha_ms = [1.0 / value for value in baseline["alpha_inverse_MSUSY"]]
    log_fa_over_ms = math.log(fa / ms)
    alpha_fa = rk4_two_loop_gauge_alpha(
        alpha_ms, b_mssm, big_mssm, log_fa_over_ms
    )

    def endpoint(log_ps_over_ms: float, log_g_over_ps: float) -> list[float]:
        log_ps_over_fa = log_ps_over_ms - log_fa_over_ms
        alpha_p = rk4_two_loop_gauge_alpha(
            alpha_fa, b_vector, big_vector, log_ps_over_fa
        )
        inverse_p = [1.0 / value for value in alpha_p]
        inverse_ps = [
            inverse_p[2],
            inverse_p[1],
            (5.0 / 3.0) * inverse_p[0] - (2.0 / 3.0) * inverse_p[2],
        ]
        alpha_g = rk4_two_loop_gauge_alpha(
            [1.0 / value for value in inverse_ps],
            b_ps,
            big_ps,
            log_g_over_ps,
        )
        return [1.0 / value for value in alpha_g]

    def residual(logs: list[float]) -> tuple[list[float], list[float]]:
        inverse_g = endpoint(logs[0], logs[1])
        return (
            [inverse_g[0] - inverse_g[1], inverse_g[0] - inverse_g[2]],
            inverse_g,
        )

    logs = [baseline["log_MPS_over_MSUSY"], baseline["log_MG_over_MPS"]]
    v31_scale_residual, v31_scale_inverse = residual(logs)
    iterations = 0
    for iterations in range(1, 13):
        values, _ = residual(logs)
        if max(abs(value) for value in values) < 1.0e-11:
            break
        finite_step = 1.0e-4
        column_ps, _ = residual([logs[0] + finite_step, logs[1]])
        column_g, _ = residual([logs[0], logs[1] + finite_step])
        jacobian = [
            [
                (column_ps[i] - values[i]) / finite_step,
                (column_g[i] - values[i]) / finite_step,
            ]
            for i in range(2)
        ]
        determinant = (
            jacobian[0][0] * jacobian[1][1]
            - jacobian[0][1] * jacobian[1][0]
        )
        if abs(determinant) < 1.0e-12:
            raise ValueError("singular gauge-only two-loop scale root")
        delta_ps = (
            -values[0] * jacobian[1][1]
            + jacobian[0][1] * values[1]
        ) / determinant
        delta_g = (
            jacobian[1][0] * values[0]
            - jacobian[0][0] * values[1]
        ) / determinant
        logs = [logs[0] + delta_ps, logs[1] + delta_g]
    final_residual, inverse_g = residual(logs)
    mps = ms * math.exp(logs[0])
    mg = mps * math.exp(logs[1])
    return {
        "scope": "V24 N=1 DRbar gauge-only two-loop matrices; Yukawas omitted",
        "beta_MSSM": b_mssm,
        "B_MSSM": big_mssm,
        "beta_MSSM_plus_vectorlike": b_vector,
        "B_MSSM_plus_vectorlike": big_vector,
        "beta_PS": b_ps,
        "B_PS": big_ps,
        "at_V31_one_loop_scales": {
            "alpha_inverse_MG": v31_scale_inverse,
            "unification_spread_inverse_alpha": (
                max(v31_scale_inverse) - min(v31_scale_inverse)
            ),
            "residuals": v31_scale_residual,
        },
        "root": {
            "iterations": iterations,
            "log_MPS_over_MSUSY": logs[0],
            "log_MG_over_MPS": logs[1],
            "MPS_GeV": mps,
            "MG_GeV": mg,
            "alpha_inverse_MG": inverse_g,
            "alpha_G": 3.0 / sum(inverse_g),
            "unification_spread_inverse_alpha": max(inverse_g) - min(inverse_g),
            "residuals": final_residual,
            "converged": max(abs(value) for value in final_residual) < 1.0e-9,
        },
        "precision_G6_closed": False,
        "boundary": (
            "this is stronger than the V31 one-loop replay but still omits Yukawa, "
            "soft, scheme, and pole-threshold effects"
        ),
    }


def corrected_gauge_running(
    inputs: dict[str, Any], v24_frontier: dict[str, Any]
) -> dict[str, Any]:
    """Insert the V24 complete-vectorlike-family threshold omitted in V31."""
    baseline = v31.gauge_unification(inputs)
    delta_b = [
        float(value)
        for value in v24_frontier["RG_below_PS"][
            "one_complete_vectorlike_PS_family"
        ]["Delta_b"]
    ]
    ms = inputs["soft_benchmark"]["MSUSY_GeV"]
    fa = inputs["axion_cosmology_inputs"]["fa_GeV"]
    mps = baseline["MPS_GeV"]
    mg = baseline["MG_GeV"]
    log_ms_fa = math.log(fa / ms)
    log_fa_ps = math.log(mps / fa)
    log_ps_g = math.log(mg / mps)
    beta_mssm = baseline["beta_MSSM"]
    beta_mssm_vectorlike = [b + d for b, d in zip(beta_mssm, delta_b)]

    inv_fa = v31.inverse_run(
        baseline["alpha_inverse_MSUSY"], beta_mssm, log_ms_fa
    )
    inv_p_low = v31.inverse_run(inv_fa, beta_mssm_vectorlike, log_fa_ps)
    inv_ps = [
        inv_p_low[2],
        inv_p_low[1],
        (5.0 / 3.0) * inv_p_low[0] - (2.0 / 3.0) * inv_p_low[2],
    ]
    inv_g = v31.inverse_run(inv_ps, baseline["beta_PS"], log_ps_g)
    alpha_g = 3.0 / sum(inv_g)
    universal_shift = delta_b[0] * log_fa_ps / (2.0 * math.pi)

    rk_fa = v31.rk4_gauge_run(
        baseline["alpha_inverse_MSUSY"], beta_mssm, log_ms_fa
    )
    rk_p_low = v31.rk4_gauge_run(
        rk_fa, beta_mssm_vectorlike, log_fa_ps
    )
    rk_ps = [
        rk_p_low[2],
        rk_p_low[1],
        (5.0 / 3.0) * rk_p_low[0] - (2.0 / 3.0) * rk_p_low[2],
    ]
    rk_g = v31.rk4_gauge_run(rk_ps, baseline["beta_PS"], log_ps_g)
    replay_residual = max(abs(a - b) for a, b in zip(inv_g, rk_g))
    expected = [value - universal_shift for value in baseline["alpha_inverse_MG"]]
    shift_residual = max(abs(a - b) for a, b in zip(inv_g, expected))
    two_loop = gauge_only_two_loop_root(baseline, v24_frontier, ms, fa)

    return {
        "scheme": "V31 one-loop chain with mandatory V24 PQ-family threshold inserted",
        "ordered_scales_GeV": {
            "MSUSY": ms,
            "fPQ": fa,
            "MPS": mps,
            "MG": mg,
        },
        "complete_vectorlike_family_Delta_b": delta_b,
        "Delta_b_is_universal": len(set(delta_b)) == 1,
        "beta_MSSM": beta_mssm,
        "beta_MSSM_plus_vectorlike_family": beta_mssm_vectorlike,
        "beta_PS_including_vectorlike_family": baseline["beta_PS"],
        "universal_inverse_alpha_shift": universal_shift,
        "V31_alpha_inverse_MG": baseline["alpha_inverse_MG"],
        "corrected_alpha_inverse_MG": inv_g,
        "corrected_unification_spread_inverse_alpha": max(inv_g) - min(inv_g),
        "universal_shift_identity_max_residual": shift_residual,
        "V31_alpha_G": baseline["alpha_G"],
        "corrected_alpha_G": alpha_g,
        "relative_alpha_G_increase": alpha_g / baseline["alpha_G"] - 1.0,
        "meeting_scales_unchanged_at_one_loop": True,
        "reason_meeting_scales_unchanged": (
            "a universal Delta b cancels from all inverse-coupling differences"
        ),
        "independent_RK4_alpha_inverse_MG": rk_g,
        "analytic_vs_RK4_max_residual": replay_residual,
        "independent_replay_pass": replay_residual < 1.0e-8,
        "V31_threshold_omission_detected": universal_shift > 0.0,
        "gauge_only_two_loop": two_loop,
        "precision_G6_closed": False,
        "precision_boundary": (
            "the correction is exact at the declared piecewise one-loop level; physical "
            "pole thresholds, scheme conversion, and coupled two-loop gauge-Yukawa-soft "
            "running remain absent"
        ),
    }


def higgs_and_dependency_audit(
    inputs: dict[str, Any],
    v30_report: dict[str, Any],
    baseline_spectrum: dict[str, Any],
    baseline_pheno: dict[str, Any],
) -> dict[str, Any]:
    soft = inputs["soft_benchmark"]
    ew = inputs["electroweak_inputs"]
    tanb = soft["tan_beta"]
    cos2b = (1.0 - tanb * tanb) / (1.0 + tanb * tanb)
    ma2 = soft["mA_GeV"] ** 2
    mz2 = ew["MZ_GeV"] ** 2
    discriminant = (ma2 + mz2) ** 2 - 4.0 * ma2 * mz2 * cos2b**2
    tree_mh2 = 0.5 * (ma2 + mz2 - math.sqrt(discriminant))
    tree_mh_big2 = 0.5 * (ma2 + mz2 + math.sqrt(discriminant))

    stop_masses = next(
        row["pole_masses_GeV"]
        for row in baseline_spectrum["pole_spectrum"]
        if row["sector"] == "stops"
    )
    stop_scale = math.sqrt(stop_masses[0] * stop_masses[1])
    xt = soft["At_GeV"] - soft["mu_GeV"] / tanb
    running_top_gev = 150.0
    mixing = (xt * xt / stop_scale**2) * (
        1.0 - xt * xt / (12.0 * stop_scale**2)
    )
    bracket = math.log(stop_scale**2 / running_top_gev**2) + mixing
    delta_mh2 = (
        3.0
        * running_top_gev**4
        / (2.0 * math.pi**2 * ew["v_GeV"] ** 2)
        * bracket
    )
    leading_one_loop_mh = math.sqrt(tree_mh2 + delta_mh2)
    tree_charged_higgs = math.sqrt(ma2 + ew["MW_GeV"] ** 2)

    common_stop_soft = soft["common_third_squark_GeV"]
    top_pole_diagnostic = 172.76
    sin2w = ew["sin2_thetaW_MSbar_MZ"]
    stop_ll = (
        common_stop_soft**2
        + top_pole_diagnostic**2
        + (0.5 - (2.0 / 3.0) * sin2w) * mz2 * cos2b
    )
    stop_rr = (
        common_stop_soft**2
        + top_pole_diagnostic**2
        + (2.0 / 3.0) * sin2w * mz2 * cos2b
    )
    stop_off = top_pole_diagnostic * xt
    stop_discriminant = math.sqrt(
        (stop_ll - stop_rr) ** 2 + 4.0 * stop_off**2
    )
    common_soft_tree_stops = [
        math.sqrt(0.5 * (stop_ll + stop_rr - stop_discriminant)),
        math.sqrt(0.5 * (stop_ll + stop_rr + stop_discriminant)),
    ]

    inv_ps = baseline_pheno["gauge_unification"][
        "alpha_inverse_MPS_PS_order_4_L_R"
    ]
    g4 = math.sqrt(4.0 * math.pi / inv_ps[0])
    gr = math.sqrt(4.0 * math.pi / inv_ps[2])
    ps_vector_ratios = [g4, gr, math.sqrt(1.5 * g4 * g4 + gr * gr)]

    mutated_inputs = copy.deepcopy(inputs)
    mutated_inputs["electroweak_inputs"]["mh_GeV"] = 1.0
    mutated_inputs["soft_benchmark"]["At_GeV"] = 1.0e12
    mutated_inputs["soft_benchmark"]["gaugino_running_GeV"] = {
        "M1": -1.0e12,
        "M2": -2.0e12,
        "M3": -3.0e12,
    }
    mutated_inputs["soft_benchmark"]["common_third_squark_GeV"] = -1.0e12
    mutated_spectrum = v31.spectrum_and_vacuum(
        mutated_inputs, baseline_pheno["gauge_unification"]
    )
    mutated_gates = v31.gate_ledger(
        v30_report, mutated_spectrum, baseline_pheno
    )
    gate_map = {row["gate"]: row for row in mutated_gates["gates"]}

    selector = baseline_spectrum["vacuum_selector"]
    return {
        "pole_ledger": {
            "declared_sector_count": baseline_spectrum["pole_sector_count"],
            "actual_row_count": len(baseline_spectrum["pole_spectrum"]),
            "V31_G2_evidence_text_claimed_sector_count": 22,
            "pole_mass_matrices_present": False,
            "self_energies_present": False,
            "mixing_matrices_present": False,
            "correlated_threshold_covariance_present": False,
            "declared_moduli_chiral_multiplets": 55,
            "modulini_rows_present": 0,
            "minimum_uneaten_modulini_if_one_goldstino_is_removed": 54,
            "heavy_vector_supermultiplet_partner_inventory_present": False,
            "PS_vector_mass_prediction": {
                "multiplicities": [6, 2, 1],
                "mass_factors_times_PS_VEV": ps_vector_ratios,
                "all_nine_vectors_degenerate_as_listed_by_V31": (
                    max(ps_vector_ratios) - min(ps_vector_ratios) < 1.0e-12
                ),
            },
        },
        "CP_even_Higgs_diagnostic": {
            "tree_mh_GeV": math.sqrt(tree_mh2),
            "tree_mH_GeV": math.sqrt(tree_mh_big2),
            "tree_charged_Higgs_GeV": tree_charged_higgs,
            "stop_geometric_scale_GeV": stop_scale,
            "Xt_GeV": xt,
            "Xt_over_stop_scale": xt / stop_scale,
            "diagnostic_running_top_GeV": running_top_gev,
            "leading_one_loop_mh_GeV": leading_one_loop_mh,
            "V31_inserted_mh_GeV": 125.25,
            "leading_one_loop_minus_inserted_GeV": leading_one_loop_mh - 125.25,
            "full_pole_calculation_present": False,
            "boundary": (
                "this leading formula is a diagnostic, not a precision pole prediction; "
                "the running-top scheme and two-loop corrections must be calculated"
            ),
        },
        "stop_input_dependency_diagnostic": {
            "common_Q3_U3_soft_input_GeV": common_stop_soft,
            "top_mass_diagnostic_GeV": top_pole_diagnostic,
            "tree_stop_masses_from_declared_common_soft_input_GeV": (
                common_soft_tree_stops
            ),
            "V31_inserted_stop_masses_GeV": stop_masses,
            "inserted_stops_derived_from_declared_common_soft_input": all(
                abs(a - b) < 1.0
                for a, b in zip(common_soft_tree_stops, stop_masses)
            ),
        },
        "dependency_mutation": {
            "mutated_values": {
                "mh_GeV": 1.0,
                "At_GeV": 1.0e12,
                "gaugino_running_GeV": mutated_inputs["soft_benchmark"]["gaugino_running_GeV"],
                "common_third_squark_GeV": -1.0e12,
            },
            "pole_rows_unchanged": (
                mutated_spectrum["pole_spectrum"]
                == baseline_spectrum["pole_spectrum"]
            ),
            "G2_still_conditionally_passes": gate_map["G2"]["conditional_closed"],
            "G4_still_conditionally_passes": gate_map["G4"]["conditional_closed"],
            "conclusion": (
                "V31's G2/G4 booleans do not depend on several declared spectrum inputs; "
                "their pass state is not a derived pole-spectrum test"
            ),
        },
        "vacuum_selector_audit": {
            "local_polynomial_UV_derivation_known": selector[
                "local_polynomial_UV_derivation_known"
            ],
            "explicit_quotient_coordinate_values_present": False,
            "explicit_Hessian_matrix_present": False,
            "Hessian_eigenvalues_present": False,
            "competing_branch_enumeration_present": False,
            "unique_global_orbit_is_asserted_boolean": isinstance(
                selector["unique_global_gauge_orbit"], bool
            ),
        },
        "established_G2_G3_G4_closed": False,
    }


def proton_mechanism_audit(
    inputs: dict[str, Any], corrected_gauge: dict[str, Any]
) -> dict[str, Any]:
    proton = inputs["proton_inputs"]
    mg = corrected_gauge["ordered_scales_GeV"]["MG"]
    alpha_g = corrected_gauge["corrected_alpha_G"]
    matrix_element = proton["hadronic_matrix_element_GeV3"]
    counterfactual = (
        1.0e35
        * (mg / 1.0e16) ** 4
        * (0.04 / alpha_g) ** 2
        * (0.012 / matrix_element) ** 2
    )
    return {
        "declared_gauge_group": "SU(4)C x SU(2)L x SU(2)R",
        "V31_claimed_channel": "p_to_e_plus_pi0_dimension6_vector_exchange",
        "PS_gauge_vectors_mediate_proton_decay_at_renormalizable_level": False,
        "V31_has_declared_SO10_XY_vector_source": False,
        "V31_vector_exchange_mechanism_supported": False,
        "V31_reported_lifetime_retired": True,
        "valid_partial_lifetime_years": None,
        "counterfactual_only_corrected_vector_scaling_years": counterfactual,
        "counterfactual_conservative_low_years": (
            counterfactual / proton["theory_uncertainty_factor"]
        ),
        "counterfactual_must_not_be_compared_as_a_prediction": True,
        "required_replacement": (
            "derive every allowed dimension-five and higher baryon-violating operator "
            "from the V24 source, rotate to the mass basis, dress the SUSY operators, "
            "run them to hadronic scale, and propagate lattice/spectrum uncertainties"
        ),
        "primary_source": "https://arxiv.org/abs/2211.02054",
    }


def cosmology_and_flavour_audit(
    inputs: dict[str, Any],
    pheno: dict[str, Any],
    v24_frontier: dict[str, Any],
    corrected_gauge: dict[str, Any],
) -> dict[str, Any]:
    axion = pheno["axion_and_relic"]
    flavour = pheno["flavour_and_neutrinos"]
    target = inputs["axion_cosmology_inputs"]
    inherited_ndw = v24_frontier["phenomenology_frontier"][
        "selected_Z11_axion_candidate"
    ]["harmonics"]["conditional_P_only_QCD_harmonic"]
    declared_pq_vev = target["fa_GeV"]
    physical_fa_if_pole_preserved = declared_pq_vev / inherited_ndw
    corrected_axion_mass = 5.691 * 1.0e12 / physical_fa_if_pole_preserved
    corrected_axion_frequency = corrected_axion_mass * 0.24179893
    pq_vev_if_physical_fa_preserved = inherited_ndw * declared_pq_vev
    mps = corrected_gauge["ordered_scales_GeV"]["MPS"]
    alternative_shift = (
        4.0
        / (2.0 * math.pi)
        * math.log(mps / pq_vev_if_physical_fa_preserved)
    )
    baseline_inverse = sum(corrected_gauge["V31_alpha_inverse_MG"]) / 3.0
    alternative_alpha_g = 1.0 / (baseline_inverse - alternative_shift)
    encoded_yukawa = flavour["Dirac_Yukawa"]
    yukawa = [
        [complex(value["re"], value["im"]) for value in row]
        for row in encoded_yukawa
    ]
    ydag_y = [
        [
            sum(yukawa[a][i].conjugate() * yukawa[a][j] for a in range(3))
            for j in range(3)
        ]
        for i in range(3)
    ]
    ydag_y_offdiagonal_max = max(
        abs(ydag_y[i][j]) for i in range(3) for j in range(3) if i != j
    )
    lightest_rh_neutrino = min(flavour["right_neutrino_masses_GeV"])
    reheating_temperature = target["reheat_temperature_GeV"]
    return {
        "axion": {
            "misalignment_angle_solved_from_target_relic": True,
            "target_axion_relic_is_input": target["target_axion_relic_omega_h2"],
            "target_neutralino_relic_is_input": target[
                "target_neutralino_relic_omega_h2"
            ],
            "physical_domain_wall_number_is_input": target[
                "physical_domain_wall_number"
            ],
            "inherited_KSVZ_QCD_harmonic_and_NDW": inherited_ndw,
            "V31_NDW_matches_inherited_source": (
                target["physical_domain_wall_number"] == inherited_ndw
            ),
            "normalization_branches": {
                "preserve_declared_KSVZ_pole_and_PQ_VEV": {
                    "PQ_VEV_and_vectorlike_mass_GeV": declared_pq_vev,
                    "physical_fa_GeV": physical_fa_if_pole_preserved,
                    "axion_mass_micro_eV": corrected_axion_mass,
                    "axion_frequency_GHz": corrected_axion_frequency,
                    "corrected_alpha_G": corrected_gauge["corrected_alpha_G"],
                },
                "preserve_V31_claimed_physical_fa": {
                    "physical_fa_GeV": declared_pq_vev,
                    "required_PQ_VEV_and_vectorlike_mass_GeV": (
                        pq_vev_if_physical_fa_preserved
                    ),
                    "universal_inverse_alpha_shift": alternative_shift,
                    "corrected_alpha_G": alternative_alpha_g,
                },
            },
            "computed_misalignment_angle_rad": axion[
                "initial_misalignment_angle_rad"
            ],
            "coupled_axino_saxion_neutralino_Boltzmann_solution_present": False,
            "direct_detection_likelihood_present": False,
        },
        "flavour": {
            "CKM_role": flavour["CKM"]["source_role"],
            "PMNS_role": flavour["PMNS"]["source_role"],
            "Casas_Ibarra_R_matrix": flavour["R_matrix"],
            "charged_fermion_global_fit_present": False,
            "covariance_likelihood_present": False,
            "documented_out_of_sample_validation_present": False,
        },
        "baryogenesis": {
            "Casas_Ibarra_R_matrix": flavour["R_matrix"],
            "YdaggerY_max_offdiagonal": ydag_y_offdiagonal_max,
            "standard_hierarchical_decay_CP_asymmetry_nonzero": (
                ydag_y_offdiagonal_max > 1.0e-16
            ),
            "reheat_temperature_GeV": reheating_temperature,
            "lightest_right_neutrino_mass_GeV": lightest_rh_neutrino,
            "TR_over_M1": reheating_temperature / lightest_rh_neutrino,
            "lightest_right_neutrino_thermally_accessible": (
                reheating_temperature >= lightest_rh_neutrino
            ),
            "standard_thermal_leptogenesis_closed": False,
            "primary_source": "https://arxiv.org/abs/hep-ph/0202239",
        },
        "established_G5_or_G8_closed": False,
    }


def required_derivations() -> dict[str, Any]:
    rows = [
        {
            "gate": "G1",
            "promotion_certificate": [
                "explicit compactification, CFT, asymptotic fixed point, or lattice definition",
                "complete divisor/moduli basis and rank-full instanton or condensate charge matrix",
                "neutral and charged zero-mode cohomology plus nonzero Pfaffians for every sector",
                "tadpole, Freed--Witten, K-theory, anomaly, GS-period, and residual-subgroup checks",
                "all-order correlator or selection-rule derivation of the visible operator ideal",
                "parametric instanton/alpha-prime/string-loop control and discrete covariance of every term",
            ],
        },
        {
            "gate": "G2",
            "promotion_certificate": [
                "complete gauge-fixed component mass matrices",
                "renormalized self-energies, mixings, pole eigenvalues, and threshold covariance",
                "proof that every physical sector and eaten mode is counted exactly once",
            ],
        },
        {
            "gate": "G3",
            "promotion_certificate": [
                "derived local F+D+soft+Kahler+PQ effective potential",
                "enumeration or certified exclusion of all competing branches",
                "global quotient proof and positive physical Hessian with tunneling analysis",
            ],
        },
        {
            "gate": "G4",
            "promotion_certificate": [
                "derived mediation boundary and coupled soft-term running",
                "explicit SUSY-breaking order parameter, goldstino/gravitino sector, and uplift",
                "loop-corrected EWSB and Higgs pole prediction",
                "collider/direct-detection likelihood and electroweak-vacuum longevity",
            ],
        },
        {
            "gate": "G5",
            "promotion_certificate": [
                "GS-inclusive axion quotient and derived physical domain-wall number",
                "radiative PQ solution and coupled axion/axino/saxion/neutralino Boltzmann history",
                "neutrino masses and mixings predicted without using their measured central values",
            ],
        },
        {
            "gate": "G6",
            "promotion_certificate": [
                "all physical SUSY, PQ, PS, and UV matching thresholds",
                "independent two-loop gauge-Yukawa-soft evolution with scheme conversion",
                "uncertainty-propagated precision-unification test",
            ],
        },
        {
            "gate": "G7",
            "promotion_certificate": [
                "source-derived baryon-violating operator basis rather than PS vector exchange",
                "mass-basis rotation, SUSY dressing, operator running, and lattice matrix elements",
                "channel-by-channel lifetime distribution with correlated uncertainties",
            ],
        },
        {
            "gate": "G8",
            "promotion_certificate": [
                "charged-fermion, CKM, PMNS, CP, and neutrino fit with covariance",
                "joint proton, axion, relic, collider, flavour, and cosmology likelihood",
                "registered out-of-sample predictions not used to choose the flux or benchmark",
            ],
        },
    ]
    return {
        "schema": "susy-v32-required-derivations-v1",
        "promotion_rule": (
            "a fitted value, asserted boolean, or axiom that directly supplies the required "
            "answer cannot count as its own derivation"
        ),
        "gates": rows,
        "all_certificates_present": False,
        "recommended_new_physics_route": (
            "embed the executable V24 chiral Pati--Salam source in one explicit globally "
            "consistent compactification, then derive K, W, gauge kinetic functions, soft "
            "terms, zero modes, thresholds, and observables from that same construction"
        ),
        "route_is_currently_completed": False,
    }


def gate_ledger(
    v31_gates: dict[str, Any],
    corrected_gauge: dict[str, Any],
    proton: dict[str, Any],
) -> dict[str, Any]:
    prior = {row["gate"]: row for row in v31_gates["gates"]}
    conditional_upper_bound = {
        "G1": prior["G1"]["conditional_closed"],
        "G2": prior["G2"]["conditional_closed"],
        "G3": prior["G3"]["conditional_closed"],
        "G4": prior["G4"]["conditional_closed"],
        "G5": False,
        "G6": corrected_gauge["independent_replay_pass"],
        "G7": not proton["V31_reported_lifetime_retired"],
        "G8": not proton["V31_reported_lifetime_retired"],
    }
    findings = {
        "G1": (
            "conditional FCMA-18 algebra is retained only as an upper-bound assumption; "
            "the selector admits infinite X and P towers, the x=1/2 instanton expansion "
            "is uncontrolled, and the neutral-coefficient instanton sum is not covariant"
        ),
        "G2": (
            "positivity of 30 inserted rows remains a conditional ledger property; the "
            "claimed 22-sector evidence, mass matrices, and pole calculation are absent"
        ),
        "G3": (
            "the quotient-coordinate selector is an asserted potential with no explicit "
            "coordinates, local UV derivation, Hessian, or branch certificate"
        ),
        "G4": (
            "tree EWSB is algebraically back-solved; the pole Higgs, mediation, longevity, "
            "collider, and direct-detection calculations are absent"
        ),
        "G5": (
            "V31 inserts NDW=1 although the inherited KSVZ anomaly is NDW=4; the relic "
            "targets and angle are boundary inputs, with no coupled thermal history, "
            "predicted neutrino flavour, or viable standard thermal leptogenesis"
        ),
        "G6": (
            "the omitted Delta b=(4,4,4) threshold is corrected and replayed at one loop, "
            "but the precision two-loop and physical-threshold chain remains open"
        ),
        "G7": (
            "the V31 vector-exchange mechanism is absent in the declared PS source; no "
            "valid partial lifetime exists until the dimension-five operator chain is derived"
        ),
        "G8": (
            "G8 depended on the invalid G7 replay and otherwise replays fitted CKM/PMNS and "
            "relic targets without a joint likelihood or out-of-sample prediction"
        ),
    }
    rows = []
    for gate in [f"G{i}" for i in range(1, 9)]:
        rows.append(
            {
                "gate": gate,
                "V31_reported_conditional_closed": prior[gate]["conditional_closed"],
                "V32_conditional_upper_bound_closed": conditional_upper_bound[gate],
                "established_full_predictive_closed": False,
                "V32_finding": findings[gate],
                "promotion_requirement": prior[gate]["remaining_external_requirement"],
            }
        )
    return {
        "schema": "susy-v32-g1-g8-gate-ledger-v1",
        "gates": rows,
        "V31_reported_conditional_closed_count": sum(
            int(row["V31_reported_conditional_closed"]) for row in rows
        ),
        "V32_conditional_upper_bound_closed_count": sum(
            int(row["V32_conditional_upper_bound_closed"]) for row in rows
        ),
        "conditional_count_is_only_an_upper_bound": True,
        "upper_bound_boundary": (
            "G1 is counted only after assuming FCMA-18 fundamental; G2--G4 are "
            "bookkeeping/selector/tree identities, and G6 is only a corrected one-loop screen"
        ),
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists_in_V32": False,
        "safe_to_claim_new_fundamental_law": False,
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = source_manifest()
    v24_verdict = read_json("SUSY_V24_G1_G8_EXECUTION_VERDICT.json")
    v24_frontier = read_json("SUSY_V24_PS_VACUUM_RG_FRONTIER.json")
    v30_report = read_json("SUSY_V30_G1_FINITE_FLUX_COMPLETION.json")
    v30_manifest = read_json("SUSY_V30_FIELD_AND_SELECTOR_MANIFEST.json")
    v30_operator = read_json("SUSY_V30_OPERATOR_AND_MATCHING_CONTRACT.json")
    v30_moduli = read_json("SUSY_V30_MODULI_AND_HIDDEN_CONTRACT.json")
    v31_report = read_json("SUSY_V31_G1_G8_UNIFIED_COMPLETION.json")
    v31_inputs = read_json("SUSY_V31_BENCHMARK_INPUT_LEDGER.json")
    v31_spectrum = read_json("SUSY_V31_SPECTRUM_VACUUM_LEDGER.json")
    v31_pheno = read_json("SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json")
    v31_gates = read_json("SUSY_V31_G1_G8_GATE_LEDGER.json")

    tower = finite_selector_tower()
    v30_consistency = v30_local_uv_consistency_audit(
        v30_operator, v30_moduli, v30_manifest, v31_inputs, v31_spectrum
    )
    gauge = corrected_gauge_running(v31_inputs, v24_frontier)
    spectrum = higgs_and_dependency_audit(
        v31_inputs, v30_report, v31_spectrum, v31_pheno
    )
    proton = proton_mechanism_audit(v31_inputs, gauge)
    cosmology_flavour = cosmology_and_flavour_audit(
        v31_inputs, v31_pheno, v24_frontier, gauge
    )
    physics = {
        "schema": "susy-v32-corrected-physics-ledger-v1",
        "finite_selector_all_order_audit": tower,
        "V30_local_UV_consistency_audit": v30_consistency,
        "corrected_gauge_running": gauge,
        "spectrum_vacuum_EWSB_audit": spectrum,
        "proton_mechanism_audit": proton,
        "cosmology_flavour_audit": cosmology_flavour,
        "primary_references": PRIMARY_REFERENCES,
    }
    gates = gate_ledger(v31_gates, gauge, proton)
    required = required_derivations()

    cores_match = (
        v24_verdict["core_sha256"] == UPSTREAM_CORES["V24"]
        and v30_report["core_sha256"] == UPSTREAM_CORES["V30"]
        and v31_report["core_sha256"] == UPSTREAM_CORES["V31"]
    )
    ordered = gauge["ordered_scales_GeV"]
    checks = {
        "all_source_pins_match": all(row["matches"] for row in manifest),
        "upstream_cores_match": cores_match,
        "finite_selector_has_exact_infinite_tower_witness": tower[
            "all_samples_allowed"
        ],
        "V31_reported_eight_conditional_rows_is_preserved": gates[
            "V31_reported_conditional_closed_count"
        ] == 8,
        "PQ_threshold_scales_are_strictly_ordered": (
            ordered["MSUSY"] < ordered["fPQ"] < ordered["MPS"] < ordered["MG"]
        ),
        "V24_vectorlike_threshold_is_universal": gauge["Delta_b_is_universal"],
        "omitted_PQ_threshold_is_detected": gauge[
            "V31_threshold_omission_detected"
        ],
        "corrected_running_obeys_universal_shift_identity": gauge[
            "universal_shift_identity_max_residual"
        ] < 1.0e-12,
        "corrected_running_has_independent_RK4_replay": gauge[
            "independent_replay_pass"
        ],
        "gauge_only_two_loop_root_converges": gauge["gauge_only_two_loop"][
            "root"
        ]["converged"],
        "V31_one_loop_scales_do_not_unify_at_gauge_two_loop": gauge[
            "gauge_only_two_loop"
        ]["at_V31_one_loop_scales"]["unification_spread_inverse_alpha"] > 0.5,
        "corrected_alphaG_is_larger_than_V31": gauge["corrected_alpha_G"]
        > gauge["V31_alpha_G"],
        "pole_ledger_has_thirty_not_twenty_two_rows": (
            spectrum["pole_ledger"]["declared_sector_count"] == 30
            and spectrum["pole_ledger"]["actual_row_count"] == 30
        ),
        "pole_ledger_is_incomplete_and_PS_vectors_are_not_degenerate": (
            spectrum["pole_ledger"]["modulini_rows_present"] == 0
            and spectrum["pole_ledger"]["PS_vector_mass_prediction"][
                "all_nine_vectors_degenerate_as_listed_by_V31"
            ]
            is False
        ),
        "inserted_stops_are_not_derived_from_common_soft_input": spectrum[
            "stop_input_dependency_diagnostic"
        ]["inserted_stops_derived_from_declared_common_soft_input"]
        is False,
        "Higgs_target_is_not_a_derived_pole": (
            spectrum["CP_even_Higgs_diagnostic"]["full_pole_calculation_present"]
            is False
        ),
        "unphysical_input_mutation_does_not_close_dependency_gap": (
            spectrum["dependency_mutation"]["pole_rows_unchanged"]
            and spectrum["dependency_mutation"]["G2_still_conditionally_passes"]
            and spectrum["dependency_mutation"]["G4_still_conditionally_passes"]
        ),
        "vacuum_selector_is_not_a_derived_global_proof": (
            spectrum["vacuum_selector_audit"][
                "local_polynomial_UV_derivation_known"
            ]
            is False
        ),
        "Pati_Salam_vector_proton_lifetime_is_retired": proton[
            "V31_reported_lifetime_retired"
        ],
        "V30_local_UV_interpretation_fails_control_and_covariance": (
            v30_consistency["semiclassical_instanton_control"][
                "controlled_E3_expansion_demonstrated"
            ]
            is False
            and v30_consistency["discrete_gauge_covariance"][
                "terms_transform_covariantly_with_neutral_coefficients"
            ]
            is False
        ),
        "inherited_NDW_regression_is_detected": (
            cosmology_flavour["axion"]["inherited_KSVZ_QCD_harmonic_and_NDW"]
            == 4
            and cosmology_flavour["axion"]["V31_NDW_matches_inherited_source"]
            is False
        ),
        "standard_thermal_leptogenesis_is_not_closed": (
            cosmology_flavour["baryogenesis"][
                "standard_thermal_leptogenesis_closed"
            ]
            is False
        ),
        "conditional_upper_bound_count_is_five": gates[
            "V32_conditional_upper_bound_closed_count"
        ] == 5,
        "zero_established_gates_are_overclaimed": gates[
            "established_full_predictive_closed_count"
        ] == 0,
        "complete_theory_claim_is_fail_closed": gates[
            "complete_theory_exists_in_V32"
        ]
        is False,
        "required_derivations_remain_explicitly_open": required[
            "all_certificates_present"
        ]
        is False,
    }
    failures = [name for name, passed in checks.items() if not passed]
    evidence = {
        PHYSICS_JSON.name: physics,
        GATES_JSON.name: gates,
        REQUIRED_JSON.name: required,
    }
    report: dict[str, Any] = {
        "schema": "susy-v32-complete-theory-promotion-audit-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v32.complete_theory_promotion_audit",
        "audit_date": "2026-08-24",
        "source_manifest": manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "result": {
            "V31_reported_conditional_closed_count": gates[
                "V31_reported_conditional_closed_count"
            ],
            "V32_conditional_upper_bound_closed_count": gates[
                "V32_conditional_upper_bound_closed_count"
            ],
            "established_full_predictive_closed_count": gates[
                "established_full_predictive_closed_count"
            ],
            "complete_theory_exists": gates["complete_theory_exists_in_V32"],
            "safe_to_claim_new_fundamental_law": gates[
                "safe_to_claim_new_fundamental_law"
            ],
        },
        "corrected_numbers": {
            "MPS_GeV": ordered["MPS"],
            "MG_GeV": ordered["MG"],
            "inverse_alpha_universal_PQ_shift": gauge[
                "universal_inverse_alpha_shift"
            ],
            "V31_alpha_G": gauge["V31_alpha_G"],
            "corrected_alpha_G": gauge["corrected_alpha_G"],
            "gauge_only_two_loop_MPS_GeV": gauge["gauge_only_two_loop"]["root"][
                "MPS_GeV"
            ],
            "gauge_only_two_loop_MG_GeV": gauge["gauge_only_two_loop"]["root"][
                "MG_GeV"
            ],
            "gauge_only_two_loop_alpha_G": gauge["gauge_only_two_loop"]["root"][
                "alpha_G"
            ],
            "gauge_only_two_loop_spread_at_V31_scales": gauge[
                "gauge_only_two_loop"
            ]["at_V31_one_loop_scales"]["unification_spread_inverse_alpha"],
            "inherited_NDW": cosmology_flavour["axion"][
                "inherited_KSVZ_QCD_harmonic_and_NDW"
            ],
            "physical_fa_GeV_if_KSVZ_pole_preserved": cosmology_flavour[
                "axion"
            ]["normalization_branches"]["preserve_declared_KSVZ_pole_and_PQ_VEV"][
                "physical_fa_GeV"
            ],
            "corrected_axion_mass_micro_eV_if_KSVZ_pole_preserved": (
                cosmology_flavour["axion"]["normalization_branches"]
                ["preserve_declared_KSVZ_pole_and_PQ_VEV"]["axion_mass_micro_eV"]
            ),
            "tree_mh_GeV": spectrum["CP_even_Higgs_diagnostic"]["tree_mh_GeV"],
            "leading_one_loop_mh_diagnostic_GeV": spectrum[
                "CP_even_Higgs_diagnostic"
            ]["leading_one_loop_mh_GeV"],
            "valid_proton_partial_lifetime_years": proton[
                "valid_partial_lifetime_years"
            ],
        },
        "new_physics_decision": {
            "invent_another_unconstrained_selector": False,
            "reason": (
                "another axiom can assign any desired answer but cannot establish a "
                "microscopic theory or create independent predictions"
            ),
            "constructive_route": required["recommended_new_physics_route"],
            "strongest_known_precedent_not_yet_an_embedding": (
                "explicit flux/instanton/gauge-dynamics moduli stabilization exists, but "
                "the V24 chiral Pati--Salam visible sector and its zero modes, correlators, "
                "anomalies, and thresholds have not been derived in that construction"
            ),
        },
        "generated_evidence_sha256": {
            name: hashlib.sha256(
                (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            ).hexdigest()
            for name, payload in evidence.items()
        },
        "scientific_boundary": (
            "V32 completes the requested investigation, not the fundamental theory.  The "
            "repository contains a useful executable EFT and conditional benchmark, but no "
            "single microscopic construction derives FCMA-18/BFA-8, the global vacuum and "
            "pole spectrum, precision thresholds, cosmological history, proton operators, "
            "and out-of-sample flavour likelihood."
        ),
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report, evidence


def render_markdown(report: dict[str, Any]) -> str:
    result = report["result"]
    numbers = report["corrected_numbers"]
    return f"""# SUSY V32 complete-theory promotion audit

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- V31 reported conditional rows: **{result['V31_reported_conditional_closed_count']}/8**
- V32 conditional upper bound after exact regressions: **{result['V32_conditional_upper_bound_closed_count']}/8**
- Established full predictive gates: **{result['established_full_predictive_closed_count']}/8**

## Decision

No complete G1--G8 theory can honestly be promoted from the current files.
V30/31 remain useful conditional constructions, but `FCMA-18` and `BFA-8`
supply the answers that a microscopic theory must derive.  V32 does not add a
third unrestricted axiom: doing so could fit any benchmark without creating a
new prediction or a UV completion.

## Exact corrections and diagnostics

- **G1:** `Z4R x Z11` permits both `X^(2m+1)` and `P^(11+22k)`
  infinite superpotential towers.  Moreover, V30 fixes an instanton action
  `ln(2)<1`, and its `x+x^2+x^3` terms acquire different discrete phases while
  their coefficients are declared neutral.  `FCMA-18` is neither derived nor
  presently a controlled local discrete-gauge construction.
- **G2--G4:** V31 contains 30 hard-coded pole rows although its G2 evidence says
  22; it omits the moduli fermions, and its own gauge couplings split the nine
  PS vectors into three mass classes rather than one.  The exact declared tree
  masses are `mh={numbers['tree_mh_GeV']:.9f} GeV`
  and the leading one-loop stop diagnostic is
  `{numbers['leading_one_loop_mh_diagnostic_GeV']:.9f} GeV`, while `125.25 GeV`
  is inserted.  Unphysical mutations of `At`, gaugino masses, a squark input,
  and the Higgs input leave the pole rows and G2/G4 pass flags unchanged.
- **G6:** inserting the required complete-family `Delta b=(4,4,4)` threshold
  between `fPQ` and `MPS` shifts every inverse coupling by
  `{numbers['inverse_alpha_universal_PQ_shift']:.9f}`.  The one-loop meeting
  scales stay `MPS={numbers['MPS_GeV']:.6e} GeV` and
  `MG={numbers['MG_GeV']:.6e} GeV`, but `alphaG` changes from
  `{numbers['V31_alpha_G']:.9f}` to `{numbers['corrected_alpha_G']:.9f}`.
  The inherited gauge-only two-loop matrices give an inverse-coupling spread
  `{numbers['gauge_only_two_loop_spread_at_V31_scales']:.6f}` at those scales;
  re-solving gives `MPS={numbers['gauge_only_two_loop_MPS_GeV']:.6e} GeV`,
  `MG={numbers['gauge_only_two_loop_MG_GeV']:.6e} GeV`, and
  `alphaG={numbers['gauge_only_two_loop_alpha_G']:.9f}`.  Yukawa, soft, scheme,
  and pole-threshold effects still prevent precision G6 closure.
- **G7:** the declared Pati--Salam gauge bosons do not mediate proton decay at
  renormalizable level.  V31's vector-exchange lifetime is retired; the valid
  lifetime is `null` until the allowed dimension-five operator chain is
  matched, dressed, run, and combined with lattice matrix elements.
- **G5/G8:** the inherited KSVZ anomaly gives `NDW={numbers['inherited_NDW']}`,
  not one.  Preserving the declared `5e11 GeV` KSVZ pole gives
  `fa={numbers['physical_fa_GeV_if_KSVZ_pole_preserved']:.6e} GeV` and
  `ma={numbers['corrected_axion_mass_micro_eV_if_KSVZ_pole_preserved']:.6f} micro-eV`.
  The relic fractions, misalignment condition, CKM, and PMNS are
  fitted boundary data; the `R=I` benchmark also has no standard thermal
  leptogenesis.  A coupled Boltzmann history and covariance-aware,
  out-of-sample joint likelihood are absent.

## Constructive route

The next valid new-physics step is one explicit globally consistent
compactification (or an equally complete non-string UV definition) containing
the executable V24 chiral Pati--Salam sector.  The same construction must
derive its divisor/zero-mode data, `K`, `W`, gauge kinetic functions, anomalies,
soft terms, physical vacuum, poles, thresholds, flavour tensors, cosmology,
and baryon-violating operators.  The exact per-gate certificate is frozen in
`SUSY_V32_REQUIRED_DERIVATIONS.json`.

## Primary sources

- [Pati--Salam dimension-five baryon violation](https://arxiv.org/abs/2211.02054)
- [Original Pati--Salam axion scaffold](https://arxiv.org/abs/2009.04582)
- [Three-forms in supergravity and flux compactifications](https://arxiv.org/abs/1706.09422)
- [Constrained superfields](https://arxiv.org/abs/0907.2441)
- [Explicit F-theory moduli-stabilization precedent](https://arxiv.org/abs/hep-th/0503124)
- [Fluxed instantons with chiral visible sectors](https://arxiv.org/abs/1105.3193)
- [Mixed axion/neutralino thermal history](https://arxiv.org/abs/1309.5365)
- [Thermal leptogenesis bound](https://arxiv.org/abs/hep-ph/0202239)
- [2026 natural-SUSY axion/axino constraints](https://arxiv.org/abs/2604.04687)
- [LZ 4.2 tonne-year WIMP search](https://arxiv.org/abs/2410.17036)

## Replay

```bash
python -B susy_v32_complete_theory_promotion_audit.py --check
python -m pytest -q test_susy_v32_complete_theory_promotion_audit.py
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


def write_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    for path, content in output_map(report, evidence).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> bool:
    return all(
        path.exists() and path.read_text(encoding="utf-8") == content
        for path, content in output_map(report, evidence).items()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify frozen outputs")
    args = parser.parse_args()
    report, evidence = build_bundle()
    if report["failures"]:
        print("V32 audit checks failed: " + ", ".join(report["failures"]))
        return 1
    if args.check:
        if not check_outputs(report, evidence):
            print("V32 frozen outputs differ; run without --check")
            return 1
    else:
        write_outputs(report, evidence)
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
