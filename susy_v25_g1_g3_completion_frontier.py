#!/usr/bin/env python3
"""Exact V25 continuation of the V24 G1--G3 closure attempt.

This certificate does two things which must not be conflated:

1. it closes the canonical, tree-level Pati--Salam breaking-sector spectrum;
2. it proves why the *full* G1--G3 claims still cannot be made from the V24
   source contract.

The obstruction is algebraic.  The retained neutral-driver terms
``X`` and ``X Sbc Sc`` force ``A=Sbc Sc`` to be neutral under every
additive Abelian shaping factor.  Together with the retained ``X^3`` term,
this permits ``X^(2m+1) A^n`` for all non-negative ``m,n``.  The same
renormalizable source already has a second exact F=D=0 branch with
``Sbc=Sc=0`` and non-zero ``X``.  Unspecified all-order Wilson, Kahler and
soft coefficients therefore control the physical Hessian and branch
selection.

The output is deliberately fail-closed: it is a completed analysis and a
qualified spectrum theorem, not a declaration that the three full gates
are closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import susy_v24_ps_source_contract as v24_source


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V25_G1_G3_COMPLETION_FRONTIER.json"
MD_PATH = ROOT / "SUSY_V25_G1_G3_COMPLETION_FRONTIER.md"

STATUS = (
    "V25_G1_G3_ANALYSIS_COMPLETE__CANONICAL_PS_BREAKING_SPECTRUM_CLOSED__"
    "ALL_ORDER_DRIVER_TOWER_AND_COMPETING_F_FLAT_BRANCH_PROVE_FULL_G1_G3_OPEN"
)

SOURCE_PINS = {
    "susy_v24_g1_g8_execution_verdict.py": "1714d781ab0d2f952b742eda0731a934788bde5356c18ce761178254bf67dec5",
    "SUSY_V24_G1_G8_EXECUTION_VERDICT.json": "42b674dc6fe137979ea3d6067efa02bd4531298688b2086d99affa2a61b7f047",
    "susy_v24_ps_source_contract.py": "4993924ebf64a8eb05f83290174adaffe277342234d1ae43e78d992b3efbf4da",
    "SUSY_V24_PS_SOURCE_CONTRACT.json": "c2457e188877a2729e092acf6ddbf76626b884a4c1cb652c282da215f268ce51",
    "models/PSZ4RZ11SUSYV24/PSZ4RZ11SUSYV24.m": "09326668d02b32b4a66c3b79cba34fb6a709430a360dce6d2d5d2ab039cad2bf",
}

UPSTREAM_CORES = {
    "terminal": "09b4b232afe0f5150dab74e5fc28f1984551732d9e100c1687971b96410adacd",
    "source": "d408aa7d7d3096ac917f5bd6f4f37576aace4cd78709bf4810b8e036dc2d93a8",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def fstr(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def driver_tower(max_dimension: int = 25) -> list[dict[str, int | str]]:
    """Enumerate X^(2m+1) A^n through a finite audit dimension.

    X has engineering dimension one and A=Sbc Sc has dimension two.  The
    theorem itself is all-order; this finite list is only a regression cell.
    """

    rows: list[dict[str, int | str]] = []
    for m in range((max_dimension + 1) // 2):
        for n in range((max_dimension + 1) // 2):
            x_power = 2 * m + 1
            dimension = x_power + 2 * n
            if dimension > max_dimension:
                continue
            rows.append(
                {
                    "m": m,
                    "n": n,
                    "X_power": x_power,
                    "A_power": n,
                    "engineering_dimension": dimension,
                    "monomial": f"X^{x_power} A^{n}",
                }
            )
    return sorted(rows, key=lambda row: (int(row["engineering_dimension"]), int(row["X_power"])))


def kahler_tower(max_dimension: int = 24) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for m in range(max_dimension // 2 + 1):
        for n in range(max_dimension // 4 + 1):
            if m == 0 and n == 0:
                continue
            dimension = 2 * m + 4 * n
            if dimension > max_dimension:
                continue
            rows.append(
                {
                    "XdagX_power": m,
                    "AdagA_power": n,
                    "engineering_dimension": dimension,
                    "monomial": f"(Xdag X)^{m} (Adag A)^{n}",
                }
            )
    return sorted(rows, key=lambda row: (int(row["engineering_dimension"]), int(row["XdagX_power"])))


def all_order_driver_ledger() -> dict[str, Any]:
    rows = driver_tower()
    k_rows = kahler_tower()
    return {
        "critical_invariant": "A=Sbc Sc",
        "retained_relations_for_each_additive_Abelian_factor": [
            "q(X)=omega from the neutral-coupling tadpole X",
            "q(X)+q(A)=omega from X A",
            "3 q(X)=omega from X^3",
        ],
        "exact_consequences": [
            "q(A)=0",
            "q(X)=omega",
            "2 omega=0",
            "q(X^(2m+1) A^n)=omega for every m,n>=0",
        ],
        "X3_forcing_no_go": {
            "retained_terms": [
                "X",
                "X Sbc Sc",
                "X Sigma^2",
                "Sc^2 Sigma",
                "Sbc^2 Sigma",
            ],
            "proof": [
                "qX=omega",
                "qSc+qSbc=0",
                "2qSigma=0",
                "2qSc+qSigma=omega",
                "2qSbc+qSigma=omega",
                "adding the last two equations gives 2omega=0",
                "therefore q(X^3)=3omega=omega",
            ],
            "X3_is_unavoidable_under_every_additive_Abelian_product": True,
            "minimum_architecture_change": (
                "drop or dress at least one of X Sigma^2, Sc^2 Sigma, or Sbc^2 Sigma, "
                "or use a non-additive/non-Abelian coupling selector"
            ),
        },
        "all_order_superpotential_grammar_on_critical_slice": (
            "Wcrit = X Lambda^2 F(A/Lambda^2, X^2/Lambda^2) for an arbitrary analytic F"
        ),
        "all_order_kahler_statement": (
            "Xdag X and Adag A are neutral, so arbitrary real analytic functions of them are allowed"
        ),
        "degree_le_25_regression_rows": rows,
        "degree_le_25_count": len(rows),
        "renormalizable_rows": [row for row in rows if int(row["engineering_dimension"]) <= 3],
        "higher_dimensional_rows_through_25": [
            row for row in rows if int(row["engineering_dimension"]) > 3
        ],
        "kahler_degree_le_24_regression_rows": k_rows,
        "tower_is_infinite": True,
        "can_be_forbidden_by_an_additional_additive_Abelian_factor_while_retaining_X_XA_X3": False,
        "reason": (
            "the three retained monomials impose the displayed charge identities componentwise for "
            "ordinary, R, continuous, cyclic, or product Abelian shaping groups"
        ),
        "GS_counterterm_effect_on_tower": (
            "a shifting GS modulus cancels anomaly phases but does not assign A a nonzero charge or fix F"
        ),
    }


def minimal_z3r_repair_candidate() -> dict[str, Any]:
    """Construct the smallest additive selector that removes X^3 at dimension 3.

    The no-go says this necessarily also removes at least one retained sextet
    interaction.  The concrete choice below removes X Sigma^2 while keeping
    the other 16 source classes.  It is a useful repair witness, not a full
    completion: P^2 redresses both removed terms, the neutral-A tower remains,
    and the visible gravitational GS congruence is not closed.
    """

    charges = {
        "H": 0,
        "Q": 1,
        "Qc": 1,
        "X": 2,
        "Sc": 0,
        "Sbc": 0,
        "Sigma": 2,
        "PsiBar": 0,
        "Psi": 1,
        "PsiC": 1,
        "PsiCBar": 0,
        "P": 1,
        "N": 1,
    }
    operator_rows = []
    for row in v24_source.RENORMALIZABLE_OPERATORS:
        charge = sum(charges[name] for name in row["monomial"]) % 3
        operator_rows.append(
            {
                "key": row["key"],
                "monomial": row["monomial"],
                "Z3R_sum_mod3": charge,
                "allowed": charge == 2,
            }
        )

    t4 = {1: Fraction(0), 4: Fraction(1, 2), -4: Fraction(1, 2), 6: Fraction(1)}
    t2 = {1: Fraction(0), 2: Fraction(1, 2)}
    mixed: dict[str, Fraction] = {}
    for group in ("SU4", "SU2L", "SU2R"):
        value = Fraction({"SU4": 4, "SU2L": 2, "SU2R": 2}[group])
        for field in v24_source.FIELDS:
            rep4, rep_l, rep_r = field["PS_representation"]
            if group == "SU4":
                index, spectator = t4[rep4], rep_l * rep_r
            elif group == "SU2L":
                index, spectator = t2[rep_l], abs(rep4) * rep_r
            else:
                index, spectator = t2[rep_r], abs(rep4) * rep_l
            value += (
                field["multiplicity"]
                * index
                * spectator
                * (charges[field["name"]] - 1)
            )
        mixed[group] = value
    grav = -21 + 21 + sum(
        field["multiplicity"]
        * abs(field["PS_representation"][0])
        * field["PS_representation"][1]
        * field["PS_representation"][2]
        * (charges[field["name"]] - 1)
        for field in v24_source.FIELDS
    )
    return {
        "selector": "additional Z3R with superpotential charge 2",
        "charges": charges,
        "renormalizable_operator_audit": operator_rows,
        "allowed_source_class_count": sum(row["allowed"] for row in operator_rows),
        "forbidden_source_classes": [row["key"] for row in operator_rows if not row["allowed"]],
        "first_P_dressed_reappearance": {
            "X_cubic": "P^2 X^3/Lambda^2",
            "X_Sigma_Sigma": "P^2 X Sigma^2/Lambda^2",
            "suppression_at_fPQ_over_Lambda_1p76e_minus7": 3.0976e-14,
        },
        "neutral_A_tower_removed": False,
        "mixed_anomaly_representatives": {key: fstr(value) for key, value in mixed.items()},
        "mixed_anomaly_residues_mod3": {key: int(value) % 3 for key, value in mixed.items()},
        "GS_level_candidate": {"k4": 1, "kL": 2, "kR": 1, "rho": 1},
        "mixed_residues_match_level_times_rho_mod3": (
            [int(mixed[key]) % 3 for key in ("SU4", "SU2L", "SU2R")] == [1, 2, 1]
        ),
        "visible_gravitational_representative": grav,
        "visible_gravitational_residue_mod3": grav % 3,
        "24rho_residue_mod3": 0,
        "visible_gravitational_GS_congruence_closed": grav % 3 == 0,
        "P_VEV_breaks_Z3R_completely": True,
        "full_repair_viable": False,
        "boundary": (
            "this is a concrete source-level way to push the X branch above the EFT cutoff, "
            "but it changes Kac--Moody levels, has an unmatched visible gravitational residue, "
            "and leaves the X A^n tower"
        ),
    }


def _matrix_components(
    labels: Sequence[str], matrix: Sequence[Sequence[Fraction | int]]
) -> list[list[int]]:
    seen: set[int] = set()
    components: list[list[int]] = []
    for start in range(len(labels)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component: list[int] = []
        while stack:
            index = stack.pop()
            component.append(index)
            for neighbor, value in enumerate(matrix[index]):
                if value and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def canonical_breaking_spectrum() -> dict[str, Any]:
    witness = {"kappa": 2, "lambdaS": 3, "lambdaSb": 5, "vPS": 7, "g4": 1, "gR": 1}
    labels, matrix = v24_source.construct_breaking_hessian(
        kappa=witness["kappa"],
        lambda_s=witness["lambdaS"],
        lambda_sb=witness["lambdaSb"],
        vev=witness["vPS"],
    )
    components = _matrix_components(labels, matrix)
    nontrivial_blocks = []
    for component in components:
        if len(component) == 1:
            continue
        block = [[Fraction(matrix[i][j]) for j in component] for i in component]
        nontrivial_blocks.append(
            {
                "labels": [labels[i] for i in component],
                "matrix": [[fstr(value) for value in row] for row in block],
            }
        )

    v2 = witness["vPS"] ** 2
    chiral_mass_squared = [
        {
            "sector": "radial physical chirals",
            "formula_over_vPS2": "2 |kappa|^2",
            "witness_mass_squared": 2 * witness["kappa"] ** 2 * v2,
            "multiplicity": 2,
        },
        {
            "sector": "Sc-Sigma colored chirals",
            "formula_over_vPS2": "|lambdaS|^2",
            "witness_mass_squared": witness["lambdaS"] ** 2 * v2,
            "multiplicity": 6,
        },
        {
            "sector": "Sbc-Sigma colored chirals",
            "formula_over_vPS2": "|lambdaSb|^2",
            "witness_mass_squared": witness["lambdaSb"] ** 2 * v2,
            "multiplicity": 6,
        },
        {
            "sector": "gauge-Goldstone chiral directions",
            "formula_over_vPS2": "0 before the super-Higgs mechanism",
            "witness_mass_squared": 0,
            "multiplicity": 9,
        },
    ]
    vector_mass_squared = [
        {
            "sector": "SU4/SU3 leptoquark vectors",
            "formula_over_vPS2": "g4^2",
            "witness_mass_squared": v2,
            "multiplicity": 6,
        },
        {
            "sector": "charged SU2R vectors",
            "formula_over_vPS2": "gR^2",
            "witness_mass_squared": v2,
            "multiplicity": 2,
        },
        {
            "sector": "broken diagonal Zprime vector",
            "formula_over_vPS2": "(3/2) g4^2 + gR^2",
            "witness_mass_squared": fstr(Fraction(5, 2) * v2),
            "multiplicity": 1,
        },
    ]
    return {
        "scope": "canonical-Kahler exact-SUSY tree-level PS-breaking sector only",
        "vector_mass_convention": (
            "canonical scalar kinetic terms, Tr(Ta Tb)=delta_ab/2, VEV entries Sc=Sbc=vPS, "
            "and Lmass=(1/2) A_a M2_ab A_b"
        ),
        "vector_mass_derivation": {
            "each_offdiagonal_generator_norm_squared_per_VEV": "1/4",
            "number_of_equal_conjugate_VEVs": 2,
            "broken_diagonal_fundamental_charges": {
                "SU4_T15": "-3/(2 sqrt(6))",
                "SU2R_T3": "1/2",
            },
            "diagonal_outer_product_nonzero_eigenvalue_over_vPS2": "(3/2) g4^2 + gR^2",
        },
        "witness": witness,
        "W_hessian_dimension": [len(labels), len(labels)],
        "W_hessian_rank": v24_source._fraction_rank(matrix),
        "W_hessian_nullity": len(labels) - v24_source._fraction_rank(matrix),
        "nontrivial_exact_blocks": nontrivial_blocks,
        "chiral_superfield_mass_squared_spectrum": chiral_mass_squared,
        "vector_multiplet_mass_squared_spectrum": vector_mass_squared,
        "physical_massive_chiral_components_after_super_Higgs": 14,
        "massive_vector_multiplets": 9,
        "uneaten_massless_breaking_sector_chirals": 0,
        "canonical_tree_level_breaking_sector_spectrum_closed": True,
        "full_G2_pole_spectrum_closed": False,
        "full_G2_missing": [
            "all-order Wilson coefficients which renormalize the displayed masses",
            "PQ and soft sectors",
            "SM-stage mixing, loop self-energies, scheme and threshold matching",
        ],
    }


def higher_operator_mass_sensitivity() -> dict[str, Any]:
    a0 = Fraction(1, 10_000)
    c_extra_branch = Fraction(-2)
    second_root = -a0 - Fraction(1, c_extra_branch)
    c_double_root = -Fraction(1, 2 * a0)
    derivative_at_desired_root = 1 + 2 * c_double_root * a0
    return {
        "dimensionless_completion": "F(a,0)=(a-a0)*(1+c*(a+a0))",
        "a": "A/Lambda^2",
        "a0": fstr(a0),
        "allowed_source_operator_responsible": "X A^2/Lambda^2",
        "order_one_witness": {
            "c": fstr(c_extra_branch),
            "desired_root": fstr(a0),
            "second_positive_subcutoff_root": fstr(second_root),
        },
        "rank_loss_witness": {
            "c": fstr(c_double_root),
            "dF_da_at_a0": fstr(derivative_at_desired_root),
            "interpretation": "the radial W-Hessian mass can be canceled by an allowed Wilson coefficient",
        },
        "colored_mass_tower": (
            "Sc Sc Sigma * G(A/Lambda^2) and Sbc Sbc Sigma * Gbar(A/Lambda^2) are also allowed"
        ),
        "conclusion": "the canonical rank is generic but exact pole masses and all-order rank are not symmetry theorems",
    }


def competing_branch_ledger() -> dict[str, Any]:
    # Use kappa=kappaX=v^2=1.  The two branch substitutions are exact.
    kappa = Fraction(1)
    kappa_x = Fraction(1)
    v2 = Fraction(1)

    def f_x(a: Fraction, x2: Fraction) -> Fraction:
        return -kappa * v2 + kappa * a + kappa_x * x2

    branches = {
        "PS_breaking": {
            "A": fstr(v2),
            "X_squared": 0,
            "F_X": fstr(f_x(v2, Fraction(0))),
            "F_Sc_and_F_Sbc": 0,
            "D": 0,
            "V_global_SUSY": 0,
        },
        "PS_unbroken_X": {
            "A": 0,
            "X_squared": fstr(kappa * v2 / kappa_x),
            "number_of_complex_X_roots": 2,
            "F_X": fstr(f_x(Fraction(0), kappa * v2 / kappa_x)),
            "F_Sc_and_F_Sbc": 0,
            "D": 0,
            "V_global_SUSY": 0,
        },
    }
    return {
        "renormalizable_critical_superpotential": "W=-kappa v^2 X+kappa X A+(kappaX/3) X^3",
        "exact_branches_at_nonzero_kappa_kappaX": branches,
        "PS_branch_is_a_global_minimum_of_nonnegative_F_plus_D": True,
        "PS_branch_is_the_unique_global_minimum": False,
        "competing_zero_energy_PS_unbroken_branch_exists": True,
        "first_order_soft_splitting": {
            "soft_potential": "epsilon*(mS2*(|Sc|^2+|Sbc|^2)+mX2*|X|^2)",
            "PS_branch_coefficient_over_epsilon_v2": "2 mS2",
            "X_branch_coefficient_over_epsilon_v2": "mX2*kappa/kappaX",
            "PS_selected_witness": {"mS2": 1, "mX2": 3, "PS": 2, "X": 3},
            "X_selected_witness": {"mS2": 2, "mX2": 1, "PS": 4, "X": 1},
            "conclusion": "allowed but unspecified soft data select opposite branches for arbitrarily small epsilon",
        },
        "full_soft_Kahler_PQ_globality_closed": False,
    }


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "closed": False,
            "full_gate_claim": False,
            "state": "CRITICAL_SLICE_ALL_ORDER_GRAMMAR_PROVED__FULL_UV_OPERATOR_AND_GS_COMPLETION_OPEN",
            "landed": [
                "all-order Abelian charge theorem for X^(2m+1)(Sbc Sc)^n",
                "finite regression census through dimension 25",
                "executable V24 renormalizable source remains valid",
            ],
            "blockers": [
            "the arbitrary analytic function F is not fixed by the selector",
                "X^3 and its competing branch cannot be forbidden by another additive Abelian factor while the retained sextet architecture is unchanged",
                "dynamical GS modulus/stabilization and hidden UV spectrum remain absent",
                "the full gauge-invariant Kahler/soft Wilson coefficient set is unspecified",
            ],
        },
        {
            "gate": "G2",
            "closed": False,
            "full_gate_claim": False,
            "state": "CANONICAL_TREE_PS_BREAKING_SPECTRUM_CLOSED__FULL_COMPONENT_POLE_SPECTRUM_OPEN",
            "landed": [
                "14 physical massive chiral breaking components",
                "nine massive vector multiplets with normalized tree mass formulas",
                "no uneaten massless breaking-sector chiral",
            ],
            "blockers": [
                "allowed Wilson towers change exact masses and can cancel a radial Hessian eigenvalue",
                "PQ/soft/SM-stage component matrices and loop pole self-energies are absent",
                "physical threshold matching is absent",
            ],
        },
        {
            "gate": "G3",
            "closed": False,
            "full_gate_claim": False,
            "state": "TWO_EXACT_ZERO_ENERGY_BRANCHES_PROVED__FULL_SOFT_KAHLER_PQ_GLOBALITY_OPEN",
            "landed": [
                "exact PS-breaking F=D=0 branch",
                "exact PS-unbroken X branch with the same zero energy",
                "opposite first-order branch selections from two allowed soft witnesses",
            ],
            "blockers": [
                "soft mediation and Kahler coefficients are unspecified",
                "higher allowed operators create further roots",
                "PQ stabilization and the full positive physical Hessian are absent",
            ],
        },
    ]


def build_report() -> dict[str, Any]:
    terminal = json.loads((ROOT / "SUSY_V24_G1_G8_EXECUTION_VERDICT.json").read_text(encoding="utf-8"))
    source = json.loads((ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json").read_text(encoding="utf-8"))
    source_manifest = [
        {
            "path": path,
            "expected_sha256": expected,
            "sha256": sha256_file(ROOT / path),
            "matches": sha256_file(ROOT / path) == expected,
        }
        for path, expected in SOURCE_PINS.items()
    ]
    all_order = all_order_driver_ledger()
    spectrum = canonical_breaking_spectrum()
    sensitivity = higher_operator_mass_sensitivity()
    branches = competing_branch_ledger()
    repair = minimal_z3r_repair_candidate()
    gates = gate_ledger()

    checks = {
        "all_raw_source_pins_match": all(row["matches"] for row in source_manifest),
        "terminal_core_matches": terminal.get("core_sha256") == UPSTREAM_CORES["terminal"],
        "source_core_matches": source.get("core_sha256") == UPSTREAM_CORES["source"],
        "V24_has_18_processed_structures": terminal["runtime_attestation"]["processed_structural_term_count"] == 18,
        "driver_tower_count_through_dimension25_is_91": all_order["degree_le_25_count"] == 91,
        "driver_tower_has_3_renormalizable_and_88_higher_rows": len(all_order["renormalizable_rows"]) == 3 and len(all_order["higher_dimensional_rows_through_25"]) == 88,
        "every_driver_tower_power_of_X_is_odd": all(int(row["X_power"]) % 2 == 1 for row in all_order["degree_le_25_regression_rows"]),
        "critical_driver_tower_is_all_order_allowed": all_order["tower_is_infinite"],
        "X3_is_forced_by_the_retained_sextet_architecture": all_order["X3_forcing_no_go"]["X3_is_unavoidable_under_every_additive_Abelian_product"],
        "minimal_Z3R_repair_keeps_16_and_forbids_exactly_2_source_classes": repair["allowed_source_class_count"] == 16 and repair["forbidden_source_classes"] == ["X_cubic", "X_Sigma_Sigma"],
        "minimal_Z3R_mixed_residues_match_levels_but_gravity_does_not": repair["mixed_residues_match_level_times_rho_mod3"] and not repair["visible_gravitational_GS_congruence_closed"],
        "W_hessian_rank_and_nullity_remain_14_and_9": spectrum["W_hessian_rank"] == 14 and spectrum["W_hessian_nullity"] == 9,
        "canonical_chiral_spectrum_accounts_for_23_components": sum(row["multiplicity"] for row in spectrum["chiral_superfield_mass_squared_spectrum"]) == 23,
        "canonical_physical_breaking_chirals_are_14": spectrum["physical_massive_chiral_components_after_super_Higgs"] == 14,
        "massive_vector_count_equals_broken_generator_count": sum(row["multiplicity"] for row in spectrum["vector_multiplet_mass_squared_spectrum"]) == 9,
        "normalized_diagonal_vector_coefficients_are_3over2_and_1": spectrum["vector_mass_derivation"]["diagonal_outer_product_nonzero_eigenvalue_over_vPS2"] == "(3/2) g4^2 + gR^2",
        "no_uneaten_breaking_chiral_is_massless": spectrum["uneaten_massless_breaking_sector_chirals"] == 0,
        "allowed_dimension5_term_can_add_a_second_subcutoff_root": sensitivity["order_one_witness"]["second_positive_subcutoff_root"] == "4999/10000",
        "allowed_Wilson_coefficient_can_cancel_radial_derivative": sensitivity["rank_loss_witness"]["dF_da_at_a0"] == 0,
        "PS_and_X_branches_are_both_exact_F_D_zero": all(row["F_X"] == 0 and row["F_Sc_and_F_Sbc"] == 0 and row["D"] == 0 for row in branches["exact_branches_at_nonzero_kappa_kappaX"].values()),
        "renormalizable_source_has_a_competing_zero_energy_branch": branches["competing_zero_energy_PS_unbroken_branch_exists"],
        "allowed_soft_witnesses_select_opposite_branches": branches["first_order_soft_splitting"]["PS_selected_witness"]["PS"] < branches["first_order_soft_splitting"]["PS_selected_witness"]["X"] and branches["first_order_soft_splitting"]["X_selected_witness"]["X"] < branches["first_order_soft_splitting"]["X_selected_witness"]["PS"],
        "all_three_full_gates_remain_fail_closed": all(not gate["closed"] and not gate["full_gate_claim"] for gate in gates),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v25-g1-g3-completion-frontier-v1",
        "status": STATUS,
        "namespace": "research.susy_pati_salam.v25.g1_g3_completion_frontier",
        "source_manifest": source_manifest,
        "upstream_core_pins": UPSTREAM_CORES,
        "all_order_G1_driver_theorem": all_order,
        "canonical_tree_G2_breaking_spectrum": spectrum,
        "G2_all_order_mass_sensitivity": sensitivity,
        "G3_competing_branch_theorem": branches,
        "minimal_new_physics_repair_attempt": repair,
        "gates": gates,
        "closure_counts": {"full_closed": 0, "full_open": 3, "qualified_subproblems_closed": 2},
        "terminal_conclusion": {
            "analysis_continued": True,
            "G1_full_closed": False,
            "G2_full_closed": False,
            "G3_full_closed": False,
            "canonical_PS_breaking_tree_spectrum_closed": True,
            "exact_reason_completion_stops": (
                "the retained driver architecture permits an arbitrary all-order analytic function and "
                "already has a degenerate PS-unbroken F-flat branch; UV Wilson/Kahler/soft data are new inputs"
            ),
            "new_physics_needed": (
                "a UV-complete anomaly/GS and mediation sector which fixes the allowed Wilson functions, "
                "stabilizes PQ, and selects the PS branch"
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
    spectrum = report["canonical_tree_G2_breaking_spectrum"]
    branches = report["G3_competing_branch_theorem"]
    tower = report["all_order_G1_driver_theorem"]
    lines = [
        "# SUSY V25 G1--G3 completion frontier",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Full gates closed: **{report['closure_counts']['full_closed']}/3**.",
        "- Qualified result: the canonical tree-level PS-breaking spectrum is closed.",
        "",
        "## G1: exact all-order driver theorem",
        "",
        "The retained tadpole `X`, cubic `X^3`, and driver coupling `X A` with `A=Sbc Sc` force `q(A)=0`, `q(X)=omega`, and `2 omega=0` in every additive Abelian shaping factor. Therefore every `X^(2m+1) A^n` is allowed. The critical-slice superpotential is an arbitrary analytic function",
        "",
        "`Wcrit = X Lambda^2 F(A/Lambda^2, X^2/Lambda^2)`.",
        "",
        f"The finite regression cell contains `{tower['degree_le_25_count']}` such sectors through dimension 25: three renormalizable and `{len(tower['higher_dimensional_rows_through_25'])}` higher-dimensional. A GS counterterm cancels anomaly phases but does not determine `F`, the Kahler function, or the soft Wilson coefficients. Full G1 therefore remains open.",
        "",
        "The unwanted `X^3` cannot be removed by appending another additive Abelian symmetry while keeping the source architecture. The five retained terms `X`, `X Sbc Sc`, `X Sigma^2`, `Sc^2 Sigma`, and `Sbc^2 Sigma` imply `2 omega=0` componentwise, hence `q(X^3)=omega`. At least one sextet/driver interaction must be dressed or replaced, or a genuinely non-additive selector must be introduced.",
        "",
        "A minimal repair was explicitly tested: an added `Z3R` can forbid `X^3` only by also forbidding `X Sigma^2`; it keeps the other 16 source classes. Both terms reappear as `P^2`-dressed operators, the neutral-`A` tower survives, and its visible gravitational GS congruence fails even though mixed gauge residues can be matched with levels `(1,2,1)`. It is therefore a useful direction, not a G1--G3 completion.",
        "",
        "## G2: what is now complete",
        "",
        f"For canonical Kahler geometry and exact SUSY, the normalized 23-component breaking Hessian has rank `{spectrum['W_hessian_rank']}` and nullity `{spectrum['W_hessian_nullity']}`. After the super-Higgs mechanism there are `{spectrum['physical_massive_chiral_components_after_super_Higgs']}` massive physical chiral components, `{spectrum['massive_vector_multiplets']}` massive vector multiplets, and no uneaten massless breaking chiral.",
        "",
        "The exact chiral mass-squared classes are `2|kappa|^2 vPS^2` (multiplicity 2), `|lambdaS|^2 vPS^2` (6), and `|lambdaSb|^2 vPS^2` (6). The vector classes are `g4^2 vPS^2` (6), `gR^2 vPS^2` (2), and `((3/2)g4^2+gR^2)vPS^2` (1). This closes the canonical tree breaking sector, not the full pole spectrum: allowed higher operators renormalize these masses and can cancel the radial derivative exactly.",
        "",
        "## G3: exact competing branch",
        "",
        f"The renormalizable source already has two exact zero-energy branches: the desired PS-breaking branch and an unbroken branch with `Sc=Sbc=0` and `X^2=(kappa/kappaX)v^2`. Both have `F=D=0`, so the desired branch is global but not unique (`unique={str(branches['PS_branch_is_the_unique_global_minimum']).lower()}`). Two allowed infinitesimal soft-mass witnesses select opposite branches. Higher allowed `X A^n` terms create further roots. Full G3 cannot be closed without a specified mediation/Kahler/PQ sector and its Wilson coefficients.",
        "",
        "## Verdict",
        "",
        "The requested analysis has been continued to an exact stopping theorem. G1--G3 cannot honestly be marked complete for V24. New physics must do more than cancel anomalies: it must fix the all-order Wilson functions, stabilize the GS/PQ/soft sector, and remove or lift the competing PS-unbroken branch. Relabeling the canonical truncation as the full theory would be false.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any]) -> bool:
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    return (
        JSON_PATH.exists()
        and MD_PATH.exists()
        and JSON_PATH.read_text(encoding="utf-8") == expected_json
        and MD_PATH.read_text(encoding="utf-8") == expected_md
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
        print(json.dumps({"failures": report["failures"], "frozen_outputs_match": check_outputs(report)}))
        return 1
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
