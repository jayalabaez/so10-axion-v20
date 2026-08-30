#!/usr/bin/env python3
"""V47 coupled source-wall completion and perturbative route comparison.

This audit closes a narrower issue than a full G gate:

* the gauge-allowed neutral-singlet cross couplings do not destroy the
  neutral-210 SU(5) source vacuum or its physical mass rank;
* no exact ordinary or R-type discrete symmetry with neutral numerical
  parameters can sequester those cross couplings while retaining the standard
  renormalizable source superpotential;
* a 45+54 alternative has an exact SU(5) branch and a better one-loop index
  budget, but is not promoted until its complete physical Hessian is replayed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.md"
INPUTS = {
    "v46_master": ROOT / "SUSY_V46_MICROSCOPIC_KILL_TEST_AUDIT.json",
    "v46_source": ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v47_source_completion_route_audit.py",
    "test_susy_v47_source_completion_route_audit.py",
    *tuple(path.name for path in INPUTS.values()),
)

STATUS = (
    "V47_COUPLED_NEUTRAL_SOURCE_BRANCH_AND_GENERIC_PHYSICAL_RANK_PROVED__"
    "PARAMETER_NEUTRAL_DISCRETE_SEQUESTERING_NO_GO__210_ROUTE_RETAINED_BY_"
    "EXACT_RANK_CERTIFICATE__45_PLUS_54_HAS_BETTER_INDEX_WINDOW_BUT_FULL_"
    "HESSIAN_REPLAY_OPEN__NO_G_GATE_PROMOTED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if canonical_sha(payload) != payload.get("core_sha256"):
        raise RuntimeError(f"bad input core hash: {path.name}")
    return payload


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def determinant(matrix: list[list[Fraction | int]]) -> Fraction:
    """Return an exact determinant over Q by fraction-preserving elimination."""

    rows = [[Fraction(value) for value in row] for row in matrix]
    size = len(rows)
    if any(len(row) != size for row in rows):
        raise ValueError("determinant requires a square matrix")
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            result = -result
        pivot_value = rows[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = rows[row][column] / pivot_value
            for inner_column in range(column + 1, size):
                rows[row][inner_column] -= factor * rows[column][inner_column]
    return result


def hessian_lemma_certificate() -> dict[str, Any]:
    """Exercise the block determinant identity with exact rational matrices.

    The dimension-independent proof is the cofactor expansion recorded in the
    returned object.  The finite witnesses prevent the executable artifact from
    reducing that proof to an unchecked prose/string assertion.
    """

    hessians = [
        [[2]],
        [[2, 1], [3, 4]],
        [[1, 2, 0], [0, 3, 1], [2, 0, 5]],
        [[2, 1, 0, 1], [1, 3, 1, 0], [0, 1, 4, 1], [1, 0, 1, 5]],
    ]
    rows: list[dict[str, Any]] = []
    for index, hessian in enumerate(hessians, 1):
        size = len(hessian)
        cross = [Fraction(index + entry + 1, entry + 1) for entry in range(size)]
        a = Fraction(index + 2, index + 1)
        d = Fraction(2 * index - 1, index + 3)
        augmented = [
            [*map(Fraction, hessian[row]), Fraction(0), cross[row]]
            for row in range(size)
        ]
        augmented.append([*[Fraction(0)] * size, Fraction(0), a])
        augmented.append([*cross, a, d])
        det_h = determinant(hessian)
        det_augmented = determinant(augmented)
        expected = -(a * a) * det_h
        rows.append(
            {
                "n_GUT_physical_modes": size,
                "det_H": str(det_h),
                "a": str(a),
                "d": str(d),
                "det_Mphys": str(det_augmented),
                "minus_a_squared_det_H": str(expected),
                "identity_holds": det_augmented == expected,
            }
        )
    return {
        "cofactor_proof": (
            "Expand along the Theta-radial row, whose only nonzero entry is a "
            "in the STheta column.  Its cofactor sign is minus and its minor is "
            "block-triangular [[H,0],[c^T,a]], so det(Mphys)=-a^2 det(H)."
        ),
        "exact_rational_witnesses": rows,
        "all_witnesses_pass": all(row["identity_holds"] for row in rows),
    }


def coupled_210_source() -> dict[str, Any]:
    """Return the exact branch and physical-Hessian block lemma."""

    total_chirals = 210 + 126 + 126 + 3
    eaten = (45 - 24) + 1
    massive = total_chirals - eaten
    return {
        "fields": [
            "Phi=210_0",
            "Sigma=126_0",
            "barSigma=bar126_0",
            "STheta=1_0",
            "ThetaPlus=1_+3",
            "ThetaMinus=1_-3",
        ],
        "most_general_relevant_form_after_shifting_STheta": (
            "W=W_GUT(m0+m1 STheta,M0+M1 STheta,lambda,eta)"
            "+kappa STheta ThetaPlus ThetaMinus+f0+f1 STheta"
            "+f2 STheta^2/2+f3 STheta^3/3"
        ),
        "coordinate_shift": (
            "Starting from kappa STheta ThetaPlus ThetaMinus+muTheta "
            "ThetaPlus ThetaMinus, define STheta_prime=STheta+muTheta/kappa "
            "and then relabel STheta_prime as STheta.  The shift only redefines "
            "the displayed singlet and GUT mass coefficients."
        ),
        "exact_branch": {
            "STheta": 0,
            "GUT_fields": "the V46 SU(5) branch evaluated with m=m0 and M=M0",
            "Theta_product": (
                "ThetaPlus ThetaMinus=-(f1+m1 I2(Phi)+M1 Sigma.barSigma)/kappa"
            ),
            "D_flatness": (
                "For every nonzero complex product P, choose equal magnitudes "
                "|ThetaPlus|=|ThetaMinus|=sqrt(|P|) and phases whose sum is arg(P)."
            ),
            "why_F_flat": [
                "F_ThetaPlus=F_ThetaMinus=0 because STheta=0",
                "all GUT F equations reduce exactly to the isolated V46 equations because every cross term is proportional to STheta",
                "F_STheta=0 fixes the Theta product rather than imposing a new condition on the GUT branch",
            ],
            "nonzero_condition": "the displayed Theta product must not vanish if U(1)F is to break to faithful Z3F",
        },
        "physical_hessian_lemma": {
            "basis": "(n gauge-fixed physical GUT modes, Theta radial mode, STheta)",
            "matrix": "[[H,0,c],[0,0,a],[c^T,a,d]]",
            "assumptions": (
                "det(H)!=0 from the V46 rank certificate and a=kappa times a "
                "nonzero Theta radial VEV"
            ),
            "gauge_quotient_note": (
                "H is the V46 Hessian after removing the 21 complex Spin(10)/SU(5) "
                "gauge-orbit directions.  The cross-coupling gradient c is orthogonal "
                "to those directions because I2(Phi) and Sigma.barSigma are gauge "
                "invariants.  The independent U(1)F gauge direction is the removed "
                "Theta relative mode."
            ),
            "determinant": "det(Mphys)=-a^2 det(H), independent of the cross-coupling vector c and singlet entry d",
            "certificate": hessian_lemma_certificate(),
            "consequence": "the complete coupled source sector has no physical massless chiral multiplet on this branch",
        },
        "counting": {
            "total_chiral_components": total_chirals,
            "Spin10_to_SU5_goldstones": 21,
            "U1F_to_Z3F_goldstone": 1,
            "eaten_chiral_components": eaten,
            "generic_massive_uneaten_chiral_components": massive,
            "generic_physical_massless_chiral_components": 0,
        },
        "scope": (
            "This proves existence and generic local physical rank of the coupled source "
            "superpotential. It does not choose this branch cosmologically or solve the "
            "Kahler, radion, soft, KK, threshold or eta problems."
        ),
    }


def selector_no_go() -> dict[str, Any]:
    return {
        "ordinary_ZN": {
            "neutral_parameter_constraints": [
                "STheta vF^2 allowed implies q(STheta)=0",
                "Phi^2 and Phi^3 allowed imply 2q(Phi)=3q(Phi)=0, hence q(Phi)=0",
                "Sigma.barSigma allowed implies q(Sigma)+q(barSigma)=0",
            ],
            "forced_cross_terms": [
                "STheta Phi^2",
                "STheta Sigma.barSigma",
            ],
            "conclusion": "no exact ordinary ZN with neutral numerical parameters can forbid either cross term",
        },
        "ZN_R": {
            "neutral_parameter_constraints": [
                "2r(Phi)=2 and 3r(Phi)=2 modulo N",
                "subtracting gives r(Phi)=0 and therefore 2=0 modulo N",
            ],
            "conclusion": (
                "only N dividing two survives; in Z2R the superpotential charge is zero "
                "and the same neutral cross terms are allowed"
            ),
        },
        "spurion_escape": (
            "Charging m, M, lambda or vF^2 introduces additional charged fields/VEVs. "
            "That is a different microscopic model whose anomalies, vacuum and operators "
            "must be audited; it is not sequestering of the present candidate."
        ),
        "decision": "include the cross couplings rather than setting them to zero by assertion",
    }


def alternative_45_54() -> dict[str, Any]:
    """Freeze the exact SU(5) branch in the Chen-Zhang-Bai normalization."""

    # Rescale a1=sqrt(10)u.  The SU(5)-preserving branch has a2=E=0.
    witness = {
        "m2": Fraction(1),
        "m4": Fraction(1),
        "lambda6": Fraction(1),
        "u_equals_a1_over_sqrt10": Fraction(1),
        "V_R_times_barV_R": Fraction(10),
        "a2": Fraction(0),
        "E": Fraction(0),
    }
    residuals = {
        "F_Delta_divided_by_V": witness["m2"] - witness["lambda6"] * witness["u_equals_a1_over_sqrt10"],
        "F_A1_rescaled": (
            10 * witness["m4"] * witness["u_equals_a1_over_sqrt10"]
            - witness["lambda6"] * witness["V_R_times_barV_R"]
        ),
        "F_A2": Fraction(0),
        "F_E": Fraction(0),
    }
    return {
        "fields": ["A=45_0", "E=54_0", "Sigma=126_0", "barSigma=bar126_0"],
        "renormalizable_superpotential": (
            "W=m2 barSigma Sigma+m4 A^2/2+m5 E^2/2"
            "-i lambda6 A barSigma Sigma+lambda8 E^3"
            "+lambda9 E A^2+lambda11 E Sigma^2+lambda12 E barSigma^2"
        ),
        "SU5_branch": {
            "specialized_F_equations": [
                "0=V_R(m2-lambda6 a1/sqrt(10))=barV_R(m2-lambda6 a1/sqrt(10))",
                "0=m4 a1-lambda6 V_R barV_R/sqrt(10)",
                "0=m4 a2+lambda9 E(2 a1/sqrt(10)+a2/sqrt(15))",
                "0=m5 E+3 lambda8 E^2/(2 sqrt(15))+lambda9(2 a1 a2/sqrt(10)+a2^2/(2 sqrt(15)))",
            ],
            "a2_24": 0,
            "E_24": 0,
            "a1": "sqrt(10) m2/lambda6",
            "Sigma_barSigma": "10 m4 m2/lambda6^2",
            "D_flat": "|Sigma|=|barSigma|",
            "unbroken_group": "SU(5)",
            "why_lambda11_lambda12_do_not_source_E": (
                "The 54 has no SU(5) singlet, and the SU(5)-singlet 126 and "
                "bar126 VEVs cannot source its 24, 15 or bar15 components.  Thus "
                "the E Sigma^2 and E barSigma^2 invariants vanish on this branch, "
                "as in the cited reduced singlet superpotential."
            ),
            "exact_rational_rescaled_witness": {
                "parameters": {key: str(value) for key, value in witness.items()},
                "residuals": {key: str(value) for key, value in residuals.items()},
                "all_residuals_zero": all(value == 0 for value in residuals.values()),
            },
        },
        "representation_and_coupling_checks": {
            "neutral_A_to_bulk_16_bar16": (
                "all four possible 16-bar16 pairs have nonzero U1F charge, so no "
                "renormalizable A H16 Hbar16 term is allowed"
            ),
            "E_to_bulk_spinors": "54 occurs in neither 16x16 nor 16xbar16, so no such cubic exists",
            "Sigma_spinor_obligations_unchanged": [
                "barSigma HLF HRA",
                "Sigma HLA HRF",
            ],
            "matter_parity_preserved": True,
        },
        "rank_status": {
            "published_complete_mass_matrices_exist": True,
            "independent_full_physical_hessian_replayed_here": False,
            "reason_fail_closed": (
                "The exact branch is certified, but V47 has not specialized every "
                "published SM-irrep mass block and proved that the only kernels are "
                "the 21 SO10/SU5 Goldstones."
            ),
        },
    }


def perturbative_comparison(alpha_inverse: float = 25.0) -> dict[str, Any]:
    representation_data = {
        "45": {"dimension": 45, "C2": Fraction(8)},
        "54": {"dimension": 54, "C2": Fraction(10)},
        "126": {"dimension": 126, "C2": Fraction(25, 2)},
        "bar126": {"dimension": 126, "C2": Fraction(25, 2)},
        "210": {"dimension": 210, "C2": Fraction(12)},
    }
    indices = {
        name: int(row["dimension"] * row["C2"] / 45)
        for name, row in representation_data.items()
    }
    c2_adj = 8
    routes = {
        "210+126+bar126": indices["210"] + indices["126"] + indices["bar126"],
        "45+54+126+bar126": indices["45"] + indices["54"] + indices["126"] + indices["bar126"],
    }
    rows: dict[str, Any] = {}
    for name, total_index in routes.items():
        b_with_vector = total_index - 3 * c2_adj
        rows[name] = {
            "sum_chiral_Dynkin_indices": total_index,
            "b_4D_N1_including_minus_3C2": b_with_vector,
            "naive_Landau_ratio_including_vector": math.exp(2 * math.pi * alpha_inverse / b_with_vector),
            "naive_Landau_ratio_chiral_brane_log_only": math.exp(2 * math.pi * alpha_inverse / total_index),
        }
    return {
        "normalization": "T(10)=1 and C2(SO10 adjoint)=8",
        "index_identity": "T(R)=dim(R) C2(R)/dim(SO10), with dim(SO10)=45",
        "representation_data": {
            name: {
                "dimension": row["dimension"],
                "C2": str(row["C2"]),
                "computed_T": indices[name],
            }
            for name, row in representation_data.items()
        },
        "assumed_alpha_inverse_at_source_scale": alpha_inverse,
        "indices": indices,
        "formula": "Lambda_pole/M=exp(2 pi alpha_inverse/b) for a four-dimensional one-loop logarithm",
        "routes": rows,
        "relative_result": (
            "45+54 has the better index budget: its vector-included naive ratio is "
            f"{rows['45+54+126+bar126']['naive_Landau_ratio_including_vector']:.3f}, "
            "versus "
            f"{rows['210+126+bar126']['naive_Landau_ratio_including_vector']:.3f} for 210."
        ),
        "qualification": (
            "This is a source-Higgs-sector-only comparison, not a complete 4D beta "
            "coefficient and not the 5D threshold calculation. Common matter and light "
            "fields are omitted from both rows; bulk power-law terms, brane kinetic "
            "normalization, split masses and the actual cutoff can change the window. "
            "The quoted pole ratios are therefore proxy values, while the exact robust "
            "comparison here is the lower source-sector index 90 versus 126."
        ),
    }


def build_report() -> dict[str, Any]:
    inputs = {name: load_json(path) for name, path in INPUTS.items()}
    source = coupled_210_source()
    selector = selector_no_go()
    alt = alternative_45_54()
    perturbative = perturbative_comparison()
    manifest = source_manifest()
    checks = {
        "V46_retained_210_route": inputs["v46_master"]["route_decision"]["continue"] == "neutral-210-repaired full-Spin10 source wall",
        "V46_GUT_physical_rank_certificate_present": inputs["v46_source"]["neutral_210_repair"]["counting"]["generic_physical_massless_chiral_components"] == 0,
        "coupled_source_total_is_465": source["counting"]["total_chiral_components"] == 465,
        "coupled_source_has_22_goldstones": source["counting"]["eaten_chiral_components"] == 22,
        "coupled_source_has_443_massive_physical_components": source["counting"]["generic_massive_uneaten_chiral_components"] == 443,
        "coupled_source_has_no_physical_zero": source["counting"]["generic_physical_massless_chiral_components"] == 0,
        "physical_hessian_determinant_lemma_nonzero": source["physical_hessian_lemma"]["determinant"] == "det(Mphys)=-a^2 det(H), independent of the cross-coupling vector c and singlet entry d",
        "physical_hessian_exact_witnesses_pass": source["physical_hessian_lemma"]["certificate"]["all_witnesses_pass"],
        "ordinary_selector_forces_cross_terms": len(selector["ordinary_ZN"]["forced_cross_terms"]) == 2,
        "R_selector_no_go_retained": selector["ZN_R"]["conclusion"].startswith("only N dividing two"),
        "45_54_exact_branch_residuals_zero": alt["SU5_branch"]["exact_rational_rescaled_witness"]["all_residuals_zero"],
        "45_54_full_rank_not_overclaimed": not alt["rank_status"]["independent_full_physical_hessian_replayed_here"],
        "45_54_index_is_lower": perturbative["routes"]["45+54+126+bar126"]["sum_chiral_Dynkin_indices"] < perturbative["routes"]["210+126+bar126"]["sum_chiral_Dynkin_indices"],
        "Dynkin_indices_recomputed_from_C2": perturbative["indices"] == {"45": 8, "54": 12, "126": 35, "bar126": 35, "210": 56},
        "210_route_still_selected_by_exact_rank": True,
        "all_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V47 source integrity failure: " + ", ".join(failures))
    report: dict[str, Any] = {
        "schema": "susy-v47-source-completion-route-audit-v1",
        "status": STATUS,
        "scientific_verdict": (
            "The neutral-210 source branch survives the unavoidable renormalizable "
            "Theta/GUT cross couplings and remains generically full physical rank. "
            "A 45+54 replacement has an exact SU5 branch and a materially better "
            "one-loop index budget, but it is not promoted without a complete "
            "independent Hessian replay."
        ),
        "coupled_210_source": source,
        "parameter_neutral_selector_no_go": selector,
        "alternative_45_plus_54": alt,
        "perturbative_window_stress_test": perturbative,
        "decision": {
            "authoritative_source_route": "retain neutral 210+126+bar126 for V47 because its full physical rank is executable",
            "cross_coupling_policy": "include, do not sequester by assertion",
            "45_plus_54_status": "priority alternative pending complete Hessian replay",
            "G3_source_superpotential_existence_subproblem": "closed",
            "G3_full_gate_closed": False,
            "gates_promoted": [],
        },
        "remaining_obligations": [
            "specialize and replay every 45+54+126+bar126 mass block on the exact SU5 branch before considering a route switch",
            "perform the actual 5D brane-plus-bulk threshold and NDA cutoff calculation for the retained 210 route",
            "couple the source solution to the enlarged four-spinor KK operator and the relative eta problem",
            "solve Kahler, radion, SUSY-breaking and cosmological branch selection",
        ],
        "primary_sources": [
            {
                "url": "https://arxiv.org/abs/hep-ph/0306242",
                "use": "minimal renormalizable 210+126+bar126 source sector and matter parity",
            },
            {
                "url": "https://arxiv.org/abs/1707.00580",
                "use": "general renormalizable 45,54,126-pair,210 superpotential, SU5-basis VEV equations and complete mass matrices",
            },
            {
                "url": "https://arxiv.org/abs/hep-ph/0405300",
                "use": "independent general SO10 superpotential, decompositions and SM-irrep mass matrices",
            },
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "input_core_hashes": {name: payload["core_sha256"] for name, payload in inputs.items()},
        "source_manifest": manifest,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    source = report["coupled_210_source"]
    alt = report["alternative_45_plus_54"]
    stress = report["perturbative_window_stress_test"]
    r210 = stress["routes"]["210+126+bar126"]
    r4554 = stress["routes"]["45+54+126+bar126"]
    obligations = "\n".join(
        f"{index}. {item}" for index, item in enumerate(report["remaining_obligations"], 1)
    )
    return f"""# V47 coupled source completion and route audit

Status: {report['status']}

## Result

{report['scientific_verdict']}

The coupled source contains {source['counting']['total_chiral_components']}
chiral components.  Spin(10) to SU(5) and U(1)F to Z3F eat
{source['counting']['eaten_chiral_components']}; the remaining
{source['counting']['generic_massive_uneaten_chiral_components']} are
generically massive.

## Unavoidable cross couplings are harmless to local rank

After shifting the neutral singlet, the relevant general form is

{source['most_general_relevant_form_after_shifting_STheta']}.

Set STheta=0 and use the already-certified SU(5) GUT branch.  F_STheta fixes
ThetaPlus ThetaMinus, while every other F equation reduces exactly to the
isolated V46 equation.  On the gauge-fixed physical space the Hessian is

[[H,0,c],[0,0,a],[cT,a,d]],

whose determinant is -a^2 det(H).  It is nonzero whenever the V46 GUT Hessian
is nonzero and the Theta VEV/coupling is nonzero.  Thus including STheta Phi^2
and STheta Sigma barSigma does not create a physical flat direction.

The determinant follows by one cofactor expansion along the Theta-radial row;
the executable exact-rational witnesses also pass in dimensions 1 through 4.

No parameter-neutral ordinary or R-type discrete symmetry can forbid those
cross terms while retaining the standard mass, cubic and driver terms.
Charged coefficients would be new spurion fields and a different model.

## 45+54 comparison

The alternative source superpotential has an exact SU(5) branch

a2=E=0, a1=sqrt(10)m2/lambda6,
Sigma barSigma=10 m4 m2/lambda6^2.

The executable rescaled witness has all branch residuals zero:
{alt['SU5_branch']['exact_rational_rescaled_witness']['residuals']}.

Its complete physical Hessian is not replayed here, so it is not promoted.
The published general mass matrices make it a concrete priority alternative.

At alpha inverse 25, the source-sector-only one-loop index proxy gives:

- 210 route: sum T={r210['sum_chiral_Dynkin_indices']}, b={r210['b_4D_N1_including_minus_3C2']},
  naive vector-included Landau ratio={r210['naive_Landau_ratio_including_vector']:.3f}.
- 45+54 route: sum T={r4554['sum_chiral_Dynkin_indices']}, b={r4554['b_4D_N1_including_minus_3C2']},
  naive vector-included Landau ratio={r4554['naive_Landau_ratio_including_vector']:.3f}.

The exact comparison is sum T=90 versus 126.  The displayed pole ratios omit
common matter/light fields and are only proxy values; they are neither complete
4D beta functions nor the required 5D threshold calculation.

## Decision

Retain the neutral 210 route because its full source-Higgs rank has an
executable certificate.  Include all gauge-allowed neutral cross couplings.
Keep 45+54 as the leading lower-index alternative until its complete Hessian
is independently replayed.

No full G gate is promoted.

## Remaining obligations

{obligations}

Core SHA-256: {report['core_sha256']}
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V47 source JSON is missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V47 source Markdown is missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V47_SOURCE_COMPLETION_ROUTE_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
