#!/usr/bin/env python3
"""Exact scaling, formal residual thresholds, and stabilizer audit for G6.

This artifact computes everything about one-loop *scalar* threshold logarithms
that is identifiable from the exact G6 spectrum.  It deliberately does not
invent electroweak or Pati--Salam representation labels.  Moreover, it checks
the generator that the frozen G6 report calls electromagnetism: the source
actually uses the elementary rotation ``G_(8,9)``.  That is not the standard
PS/SM-provenance electromagnetic generator, and neither the chosen chiral
``H`` nor the chosen ``Delta_R`` vacuum is invariant under the latter.  Thus
the abelian result below is only a
formal ``U(1)_89`` threshold, not a QED threshold.  The two calculations
of every determinant are independent at the implementation level:

* exact Vieta products over the frozen primitive polynomials; and
* direct floating-point companion-matrix roots (``numpy.roots``).

The result also restores dimensions to the normalized EFT and proves the
remaining common-scale/Wilson degeneracy.  It is a parameterized matching
theorem, not a positive G7 closure certificate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_stationarity_rank_certificate_v20 as stabilizer_source


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json"
OUT_MD = HERE / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.md"
STATUS = "EXACT_G6_SCALING_AND_FORMAL_G89_THRESHOLD__PHYSICAL_STABILIZER_MISMATCH__G7_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"

EXPECTED_CORE_SHA256 = "0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f"
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "b1bbf35b23a272eadc0a8520f0dac32fb342c7f1f3886088db2d9158acfd5ae9",
    "md": "18b061d39d0f9272227bc1a021c66b10e1b893e1cef11889b161c0023239e7e4",
}
EXPECTED_G6_CORE_SHA256 = "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
EXPECTED_G3_CORE_SHA256 = "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"

DEPENDENCIES: dict[str, tuple[Path, str]] = {
    "G6_spectrum_source": (
        HERE / "exact_eft_physical_scalar_spectrum_v20.py",
        "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36",
    ),
    "G6_spectrum_JSON": (
        HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
        "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416",
    ),
    "G3_EFT_source": (
        HERE / "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
        "d3b3368e8e640b285f43a106f5c236dc2780c01df4d71e88365cb607f35277f9",
    ),
    "G3_EFT_JSON": (
        HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json",
        "38520c5aed7a3a72dbede3e4358e5edb48c16f35a5bb31601864e1f8dc0e2271",
    ),
    "exact_stabilizer_source": (
        HERE / "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        "846bd3e57a816dfa8df4a4ce9957c547a591442200fbc3800dfe27f3c84df9c7",
    ),
    "standard_PS_SM_embedding_source": (
        HERE / "exact_126bar_triplet_clebsch_v20.py",
        "d94f37da94333fbf58e448ef6effb00e718191ed45b63bafdc0e2650ccdb0499",
    ),
}


def _raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _source_guard() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for name, (path, expected) in DEPENDENCIES.items():
        digest = _raw_sha256(path)
        if digest != expected:
            raise ArithmeticError(f"frozen parameterized-matching dependency drifted: {name}")
        observed[name] = {"path": str(path.relative_to(HERE)), "sha256": digest}
    return observed


def _positive_root_product(coefficients: list[int]) -> Fraction:
    """Return the product of all roots by Vieta for a nonzero-mass factor."""
    degree = len(coefficients) - 1
    value = Fraction(((-1) ** degree) * coefficients[-1], coefficients[0])
    if value <= 0:
        raise ArithmeticError("a frozen positive-mass factor has nonpositive root product")
    return value


def _stabilizer_misidentification_certificate() -> dict[str, Any]:
    """Prove that frozen ``Q^2`` is G89^2, not standard electromagnetic Q^2.

    In the repository's exact Pati--Salam/SM embedding,

        B-L = -(2/3)(G01+G23+G45),
        T3L = (G67-G89)/2,  T3R = (G67+G89)/2,
        Q = T3L + T3R + (B-L)/2,

    hence

        3 Q_std = 3 G67 - (G01+G23+G45).

    Overall sign is immaterial.  The exact integer action below is enough to
    distinguish it from bare G89 and to show that it does not stabilize the
    selected 126bar direction.
    """
    bare_g89 = stabilizer_source._linear_combination({(8, 9): 1})
    three_q_standard = stabilizer_source._linear_combination(
        {(0, 1): -1, (2, 3): -1, (4, 5): -1, (6, 7): 3}
    )
    vacuum = dict(stabilizer_source._vacuum_block_vectors())
    # The final G3--G6 target is the chiral H=(e6+i e7)/sqrt(2), not the
    # earlier real-H stationarity probe stored by _vacuum_block_vectors().
    chart = stabilizer_source.chart
    vacuum["H"] = {
        chart.H_SLICE.start + 2 * 6: 1,
        chart.H_SLICE.start + 2 * 7 + 1: 1,
    }

    def action_census(generator: dict[tuple[int, int], int]) -> dict[str, dict[str, int]]:
        output: dict[str, dict[str, int]] = {}
        for block, vector in vacuum.items():
            image = stabilizer_source._sparse_matvec(generator, vector)
            output[block] = {
                "nonzero_integer_coordinates": len(image),
                "integer_squared_norm": sum(value * value for value in image.values()),
            }
        return output

    bare_action = action_census(bare_g89)
    standard_action = action_census(three_q_standard)
    source_text = (HERE / "exact_eft_physical_scalar_spectrum_v20.py").read_text(encoding="utf-8")
    stabilizer_text = (HERE / "exact_gauged_u1x_stationarity_rank_certificate_v20.py").read_text(encoding="utf-8")
    embedding_text = (HERE / "exact_126bar_triplet_clebsch_v20.py").read_text(encoding="utf-8")
    if not (
        "charge_squared = -(t[8] @ t[8])" in source_text
        and '"""Exact ``su(3)_c`` basis plus the unbroken ``G_89`` generator."""' in stabilizer_text
        and "hypercharge = t3r + 0.5 * b_minus_l" in embedding_text
        and '"B_minus_L": "-(2/3)(H01+H23+H45)"' in embedding_text
        and '"SU2R": "self-dual SO(4)"' in embedding_text
        and '"SU2L": "anti-self-dual SO(4)"' in embedding_text
        and all(row["nonzero_integer_coordinates"] == 0 for row in bare_action.values())
        and standard_action["H"]["nonzero_integer_coordinates"] == 2
        and standard_action["H"]["integer_squared_norm"] == 18
        and standard_action["Delta_R"]["nonzero_integer_coordinates"] == 8
        and standard_action["Delta_R"]["integer_squared_norm"] == 72
    ):
        raise ArithmeticError("the exact physical-stabilizer mismatch certificate drifted")
    return {
        "frozen_report_label": "U(1)_em",
        "actual_source_generator": "G_(8,9)",
        "actual_source_projector": "Q_source^2=-G_(8,9)^2",
        "standard_PS_SM_embedding_derivation": {
            "B_minus_L": "-(2/3)(G01+G23+G45)",
            "T3L": "(G67-G89)/2",
            "T3R": "(G67+G89)/2",
            "Q": "T3L+T3R+(B-L)/2",
        },
        "three_Q_standard": "3 Q_std=3 G67-(G01+G23+G45)",
        "standard_candidate_overall_sign_irrelevant": True,
        "bare_G89_exact_vacuum_action": bare_action,
        "three_Q_standard_exact_vacuum_action": standard_action,
        "decisive_noninvariance": (
            "3 Q_std has 2 nonzero integer coordinates on selected chiral H "
            "(norm squared 18) and 8 on Delta_R (norm squared 72); the full "
            "target tangent therefore has 10 nonzero coordinates and norm squared 90"
        ),
        "selected_full_target_tangent": {
            "nonzero_integer_coordinates": (
                standard_action["H"]["nonzero_integer_coordinates"]
                + standard_action["Delta_R"]["nonzero_integer_coordinates"]
            ),
            "integer_squared_norm": (
                standard_action["H"]["integer_squared_norm"]
                + standard_action["Delta_R"]["integer_squared_norm"]
            ),
        },
        "G89_equals_standard_electromagnetism": False,
        "selected_vacuum_preserves_standard_electromagnetism": False,
        "physical_U1em_sector_labels_valid": False,
    }


def _sector_record(name: str, sector: dict[str, Any]) -> dict[str, Any]:
    c2 = Fraction(int(sector["casimir12"]), 12)
    # The frozen JSON calls this U1em_charge_squared, but the exact source
    # audit below proves that its operator is bare -G89^2.  Keep the numeric
    # data while correcting its physical interpretation here.
    q89_squared = Fraction(int(sector["U1em_charge_squared"]))
    determinant = Fraction(1)
    exact_log_determinant = 0.0
    numerical_log_determinant = 0.0
    numerical_max_imaginary = 0.0
    massive_count = 0
    zero_count = 0
    factor_rows: list[dict[str, Any]] = []

    for factor in sector["primitive_factors"]:
        coefficients = [int(value) for value in factor["primitive_coefficients_high_to_low"]]
        degree = int(factor["degree"])
        multiplicity = int(factor["root_multiplicity"])
        if degree != len(coefficients) - 1:
            raise ArithmeticError(f"degree drift in {name}")
        if coefficients[-1] == 0:
            if coefficients != [1, 0]:
                raise ArithmeticError(f"unexpected zero-mass polynomial in {name}")
            zero_count += degree * multiplicity
            continue

        product = _positive_root_product(coefficients)
        determinant *= product**multiplicity
        exact_factor_log = multiplicity * math.log(float(product))
        exact_log_determinant += exact_factor_log
        roots = np.roots(np.asarray(coefficients, dtype=float))
        max_imaginary = float(max((abs(root.imag) for root in roots), default=0.0))
        min_real = float(min((root.real for root in roots), default=math.inf))
        if max_imaginary > 1.0e-10 or min_real <= 0.0:
            raise ArithmeticError(f"numerical root cross-check failed positivity in {name}")
        numerical_factor_log = multiplicity * sum(math.log(float(root.real)) for root in roots)
        numerical_log_determinant += numerical_factor_log
        numerical_max_imaginary = max(numerical_max_imaginary, max_imaginary)
        massive_count += degree * multiplicity
        factor_rows.append(
            {
                "primitive_coefficients_high_to_low": coefficients,
                "degree": degree,
                "real_root_multiplicity": multiplicity,
                "exact_root_product": _fraction_text(product),
                "exact_log_product_with_multiplicity": exact_factor_log,
                "numerical_log_product_with_multiplicity": numerical_factor_log,
            }
        )

    if (
        zero_count != int(sector["zero_dimension"])
        or massive_count != int(sector["massive_real_dimension"])
        or zero_count + massive_count != int(sector["full_real_dimension"])
    ):
        raise ArithmeticError(f"dimension census drift in {name}")

    # For real scalar coordinates, Delta b=(1/6)T(R).  Trace C2=d(G)T
    # gives C2/48 per real coordinate for SU(3); the formal U(1)_89 gives
    # q89^2/6.  The latter is not interpreted as QED.
    b3 = Fraction(massive_count) * c2 / 48
    b89 = Fraction(massive_count) * q89_squared / 6
    c3 = float(c2 / 96) * exact_log_determinant
    c89 = float(q89_squared / 12) * exact_log_determinant
    return {
        "sector": name,
        "residual_representation": {
            "SU3C_irrep": sector["SU3C_irrep"],
            "SU3C_quadratic_Casimir": _fraction_text(c2),
            "formal_U1_89_charge_squared": _fraction_text(q89_squared),
            "source_field_mislabelled_as": "U1em_charge_squared",
        },
        "full_real_dimension": int(sector["full_real_dimension"]),
        "zero_real_dimension_excluded": zero_count,
        "massive_real_dimension": massive_count,
        "mass_squared_determinant_over_M0": {
            "definition": "product over massive roots of x_a, including real multiplicity",
            "exact_numerator": str(determinant.numerator),
            "exact_denominator": str(determinant.denominator),
            "natural_log_exact_via_Vieta": exact_log_determinant,
            "natural_log_independent_numerical_roots": numerical_log_determinant,
            "absolute_log_difference": abs(exact_log_determinant - numerical_log_determinant),
            "maximum_numerical_root_imaginary_part": numerical_max_imaginary,
        },
        "one_loop_real_scalar_beta_contribution": {
            "Delta_b3": _fraction_text(b3),
            "Delta_b89": _fraction_text(b89),
        },
        "dimensionless_threshold_log_constant": {
            "c3": c3,
            "c89": c89,
        },
        "massive_primitive_factors": factor_rows,
    }


def build_report() -> dict[str, Any]:
    bindings = _source_guard()
    spectrum = json.loads((HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json").read_text(encoding="utf-8"))
    g3 = json.loads((HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json").read_text(encoding="utf-8"))
    if spectrum["core_sha256"] != EXPECTED_G6_CORE_SHA256:
        raise ArithmeticError("G6 spectrum core drifted")
    if g3["core_sha256"] != EXPECTED_G3_CORE_SHA256:
        raise ArithmeticError("G3 EFT core drifted")
    operator = g3["candidate_and_global_SOS"]["EFT_operator"]
    if not (
        spectrum["model_contract_id"] == MODEL_CONTRACT_ID
        and spectrum["normalization"]["gamma"] == "1/20"
        and spectrum["normalization"]["Lambda_EFT"] == "1"
        and operator["Wilson_coefficient"] == "kappa=gamma/Lambda_EFT^2"
        and operator["field_degree"] == 6
    ):
        raise ArithmeticError("normalized EFT/Wilson contract drifted")

    sectors = [
        _sector_record(name, sector)
        for name, sector in spectrum["stabilizer_provenance"]["sector_reports"].items()
    ]
    b3 = sum((Fraction(row["one_loop_real_scalar_beta_contribution"]["Delta_b3"]) for row in sectors), Fraction())
    b89 = sum((Fraction(row["one_loop_real_scalar_beta_contribution"]["Delta_b89"]) for row in sectors), Fraction())
    c3 = sum(float(row["dimensionless_threshold_log_constant"]["c3"]) for row in sectors)
    c89 = sum(float(row["dimensionless_threshold_log_constant"]["c89"]) for row in sectors)
    massive = sum(int(row["massive_real_dimension"]) for row in sectors)
    zero = sum(int(row["zero_real_dimension_excluded"]) for row in sectors)
    max_log_difference = max(
        float(row["mass_squared_determinant_over_M0"]["absolute_log_difference"])
        for row in sectors
    )
    if not (
        massive == 448
        and zero == 38
        and b3 == Fraction(41, 2)
        and b89 == Fraction(40)
        and max_log_difference < 1.0e-12
    ):
        raise ArithmeticError("global scalar threshold census failed")
    stabilizer_audit = _stabilizer_misidentification_certificate()

    scalar_threshold = {
        "scope": "448 massive tree-level scalar real modes, formal residual SU(3) x U(1)_89 only",
        "interpretation_guard": {
            "abelian_generator": "G_(8,9)",
            "physical_electromagnetic_interpretation_allowed": False,
            "physical_hypercharge_interpretation_allowed": False,
            "Pati_Salam_matching_interpretation_allowed": False,
            "forbidden_aliases": ["QED", "U(1)_em", "U(1)_Y"],
            "reason": "standard Q stabilizes neither selected chiral H nor selected Delta_R",
        },
        "mass_parameterization": "M_a^2=M0^2*x_a with M0>0",
        "matching_scale_parameter": "rho=M0/mu",
        "weighted_log_definition": "L_i(mu)=sum_a Delta_b_i,a*ln(M_a/mu)",
        "exact_parameterized_result": {
            "L3(mu)": f"({_fraction_text(b3)})*ln(M0/mu)+{c3:.17g}",
            "L89(mu)": f"({_fraction_text(b89)})*ln(M0/mu)+{c89:.17g}",
            "B3": _fraction_text(b3),
            "B89": _fraction_text(b89),
            "c3": c3,
            "c89": c89,
        },
        "decoupling_convention": {
            "definition": "low theory excludes these scalar modes; high theory includes them",
            "inverse_coupling_formula": "alpha_low^-1(mu)-alpha_high^-1(mu)=-L_i(mu)/(2*pi)",
            "finite_scheme_constants_included": False,
        },
        "at_mu_equals_M0": {
            "L3": c3,
            "L89": c89,
            "alpha3_inverse_shift_low_minus_high": -c3 / (2.0 * math.pi),
            "alpha89_inverse_shift_low_minus_high": -c89 / (2.0 * math.pi),
        },
        "sector_data": sectors,
        "independent_implementation_comparison": {
            "implementation_A": "exact rational Vieta root products",
            "implementation_B": "floating companion-matrix roots via numpy.roots",
            "maximum_sector_log_determinant_difference": max_log_difference,
            "tolerance": 1.0e-12,
            "agreement": True,
            "scope_warning": "This compares the residual scalar determinant only, not two independent two-loop RGE implementations.",
        },
    }
    if not (
        scalar_threshold["interpretation_guard"]["abelian_generator"] == "G_(8,9)"
        and not scalar_threshold["interpretation_guard"][
            "physical_electromagnetic_interpretation_allowed"
        ]
        and "L89(mu)" in scalar_threshold["exact_parameterized_result"]
        and "Lem(mu)" not in scalar_threshold["exact_parameterized_result"]
        and all(
            "Delta_b89" in row["one_loop_real_scalar_beta_contribution"]
            and "Delta_bem" not in row["one_loop_real_scalar_beta_contribution"]
            for row in sectors
        )
    ):
        raise ArithmeticError("formal G89 threshold was physically mislabelled")

    scaling = {
        "dimension_restoration": {
            "canonical_common_scale": "q_phys=M0*q_hat and V_phys=M0^4*V_hat(q_phys/M0)",
            "tree_scalar_masses": "m_tree,a^2=M0^2*x_a",
            "uniform_scale_transformation": "M0 -> c*M0 sends every tree mass and VEV magnitude to c times itself",
        },
        "dimension_six_matching": {
            "physical_operator": "C6*||A_H Sigma||^2 with C6=gamma_phys/Lambda_phys^2",
            "frozen_dimensionless_coefficient": "C6*M0^2=1/20",
            "equivalent_Wilson_locus": "C6=1/(20*M0^2)",
            "equivalent_cutoff_locus": "Lambda_phys=M0*sqrt(20*gamma_phys)",
            "if_gamma_phys_equals_1_over_20": "Lambda_phys=M0",
        },
        "normalized_target_norm_ratios": {
            "Phi210": "1",
            "H10": "1",
            "Sigma126bar": "1/5",
            "S": "1/5",
            "Phi17": "1",
            "warning": "A physical hierarchy cannot be assigned without a declared field/VEV matching map and wave-function normalization.",
        },
        "common_scale_hierarchy_test": {
            "conditional_assumption": "all canonical normalized field coordinates are restored with the same M0",
            "then_vH_over_vPhi210": "1",
            "then_vPhi17_over_vPhi210": "1",
            "cannot_generate_EW_over_GUT_hierarchy_by_selecting_M0": True,
            "required_if_nonuniform_matching_is_intended": (
                "field-dependent wave-function/VEV matching followed by a recomputation "
                "of canonical masses and threshold couplings"
            ),
        },
        "nonidentifiability_proof": {
            "family": "for every c>0, (M0,C6)->(c*M0,C6/c^2) leaves all frozen x_a and C6*M0^2 unchanged",
            "dimensionful_observable_in_frozen_G6": False,
            "M0_solvable_from_frozen_G6": False,
            "Wilson_coefficient_or_cutoff_separately_solvable": False,
            "minimum_external_scale_input": "one dimensionful anchor plus its field/observable matching prescription",
            "minimum_external_UV_input_after_M0": (
                "either gamma_phys or Lambda_phys; G6 fixes only their ratio C6=gamma_phys/Lambda_phys^2"
            ),
        },
    }

    loop_pole = {
        "exact_parameterization": (
            "in each massive mixing sector, det[p^2*I-M0^2*X_tree-"
            "Pi_ren(p^2;mu,scheme,boundary_data)]=0"
        ),
        "tree_level_matrix_X_identified": True,
        "renormalized_self_energy_Pi_identified": False,
        "pole_masses_identified": False,
        "uncertainty_distribution_identified": False,
        "required_external_or_unfrozen_inputs": [
            "renormalization and tadpole scheme plus matching scales",
            "complete gauge, Yukawa, scalar-tensor and EFT operator couplings with boundary values",
            "wave-function, operator-mixing and counterterm matrices",
            "gauge-boson, ghost, fermion and scalar component masses and mixings",
            "absolute M0/Wilson/VEV matching and experimental input covariance",
        ],
    }

    decisive = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_binding": bindings,
        "physical_stabilizer_audit": stabilizer_audit,
        "dimensionful_EFT_family": scaling,
        "exact_residual_scalar_thresholds": scalar_threshold,
        "loop_and_pole_mass_boundary": loop_pole,
        "positive_G7_missing_inputs": [
            "a corrected vacuum that preserves standard SU(3)_C x U(1)_em, followed by a recomputed G6 spectrum",
            "per-state SU(2)_L x U(1)_Y labels and SO(10)->PS->SM parent provenance",
            "absolute physical scale, VEV map, Wilson coefficient and pole masses",
            "complete gauge-boson, fermion and scalar component threshold table",
            "complete two-loop gauge/Yukawa/scalar/EFT beta and anomalous-dimension system",
            "declared subtraction/decoupling/tadpole scheme and low-energy boundary covariance",
            "agreement of two independent complete RGE/matching implementations",
        ],
        "classification": {
            "G6_normalized_tree_spectrum_reused_exactly": True,
            "G6_dimensionful_family_parameterized_exactly": True,
            "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete": True,
            "frozen_U1em_identification_correct": False,
            "standard_electromagnetic_vacuum_preserved": False,
            "selected_chiral_H_neutral_under_standard_Q": False,
            "selected_Delta_R_neutral_under_standard_Q": False,
            "physical_SM_scalar_thresholds_identified": False,
            "absolute_scale_and_Wilson_matching_complete": False,
            "loop_and_pole_mass_corrections_complete": False,
            "SM_or_PS_component_threshold_matching_complete": False,
            "two_loop_RGE_complete": False,
            "positive_G7_closed": False,
        },
    }
    return {"status": STATUS, "core_sha256": _canonical_sha256(decisive), **decisive}


def render_markdown(report: dict[str, Any]) -> str:
    threshold = report["exact_residual_scalar_thresholds"]
    exact = threshold["exact_parameterized_result"]
    scale = report["dimensionful_EFT_family"]["dimension_six_matching"]
    return "\n".join(
        [
            "# Exact G6 scaling, formal thresholds, and physical-stabilizer audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            "- Massive scalar real modes included: 448",
            "- Goldstone/axion zero modes excluded: 38",
            "",
            "## Exact parameterized threshold",
            "",
            f"- `L3(mu) = {exact['L3(mu)']}`",
            f"- `L89(mu) = {exact['L89(mu)']}`",
            "- Convention: `alpha_low^-1-alpha_high^-1=-L/(2*pi)`.",
            "- Vieta determinants and independently computed numerical roots agree below `1e-12`.",
            "",
            "These are formal scalar threshold logs under the actual frozen `SU(3) x U(1)_89`",
            "operators. The source's `U(1)_em` label is invalid: standard electromagnetic Q annihilates",
            "neither the selected chiral H nor Delta_R. These are not QED, hypercharge, weak, or PS thresholds.",
            "",
            "## Restored dimensions",
            "",
            "- `m_tree,a^2=M0^2*x_a`.",
            f"- `{scale['frozen_dimensionless_coefficient']}`, equivalently `{scale['equivalent_Wilson_locus']}`.",
            f"- `{scale['equivalent_cutoff_locus']}`.",
            "- No frozen dimensionful observable fixes `M0`; the common scale is genuinely free.",
            "",
            "## Boundary of the result",
            "",
            "Pole masses require the renormalized self-energy matrices. Positive G7 first requires a",
            "corrected SM-preserving vacuum and recomputed G6, then electroweak/intermediate provenance and all thresholds,",
            "a complete two-loop system, a declared scheme, boundary covariance, and an independent full implementation.",
            "",
        ]
    )


def _verify_frozen(report: dict[str, Any], allow_unfrozen: bool) -> None:
    if EXPECTED_CORE_SHA256:
        if report["core_sha256"] != EXPECTED_CORE_SHA256:
            raise ArithmeticError("parameterized matching core drifted")
    elif not allow_unfrozen:
        raise ArithmeticError("EXPECTED_CORE_SHA256 is not frozen; pass --allow-unfrozen only while freezing")


def _verify_report_files(allow_unfrozen: bool) -> None:
    for kind, path in (("json", OUT_JSON), ("md", OUT_MD)):
        expected = EXPECTED_REPORT_RAW_SHA256[kind]
        if not expected:
            if not allow_unfrozen:
                raise ArithmeticError(f"expected {kind} report hash is not frozen")
            continue
        if not path.is_file() or _raw_sha256(path) != expected:
            raise ArithmeticError(f"frozen {kind} report bytes drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = build_report()
    _verify_frozen(report, args.allow_unfrozen)
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(markdown, encoding="utf-8")
    _verify_report_files(args.allow_unfrozen)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "threshold": report["exact_residual_scalar_thresholds"]["exact_parameterized_result"],
                "classification": report["classification"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
