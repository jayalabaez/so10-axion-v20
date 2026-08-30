#!/usr/bin/env python3
"""V52 minimal renormalizable seesaw/selector and doublet-triplet audit.

This audit starts from the exact V52 ``54+45+16+bar16`` source witness and
adds only

* one vector Higgs ``H(10)``; and
* four Spin(10)-singlet chiral multiplets ``N_a``.

The fourth singlet is not needed for the rank-three double seesaw.  It is the
minimal spectator that makes the conservative ordinary-Z2 gravitational and
cubic parity ledgers even when the three matter 16s and all singlets are odd.

At the source vacuum ``E0=diag(2^6,-3^4)``, the renormalizable vector-Higgs
superpotential

    W_DT = 1/2 m_H H^T H + 1/2 k_H H^T E H

has Hessian ``m_H I + k_H E0``.  The rational witness ``m_H=3, k_H=1``
therefore gives six triplet coordinates mass 5 and leaves exactly four weak
coordinates massless.  This is an exact existence witness, but the relation
``m_H=3 k_H`` is a codimension-one tuning and is not enforced by the declared
Z2.  Consequently this module does *not* claim a natural missing-partner/DW
solution or promote G2.

The singlets provide the entirely renormalizable neutral mass matrix

    ( 0    m_D   0 )
    ( m_D   0    F )
    ( 0    F^T  M_S)

in the basis ``(nu_L, nu_R^c, N)``.  Exact rational ranks and Schur
complements certify a rank-three double seesaw.  An independent unbroken Z2
makes all three matter 16s and all four N fields odd and every Higgs field
even.  It permits the needed Yukawa, portal and singlet-mass operators while
forbidding matter--Higgs bilinear mixing and every operator with an odd number
of matter/singlet fields.  Only the conventional discrete-anomaly arithmetic
is claimed; a UV embedding and the full operator/proton-decay census remain
open.
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

import sympy as sp


ROOT = Path(__file__).resolve().parent
UPSTREAM_JSON = ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.json"
JSON_PATH = ROOT / "SUSY_V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT.md"

SCHEMA = "susy_v52_minimal_seesaw_dt_repair_audit_v1"
STATUS = (
    "V52_MINIMAL_RENORMALIZABLE_DOUBLE_SEESAW_AND_UNBROKEN_Z2_SELECTOR_CERTIFIED__"
    "ONE_10H_EXACT_TRIPLET_RANK6_DOUBLET_NULLITY4_EXISTS_BUT_IS_CODIMENSION_ONE__"
    "NATURAL_DT_UV_SELECTOR_AND_FULL_OPERATOR_CENSUS_OPEN__NO_G2_PROMOTION"
)

LITERATURE = {
    "singlet_assisted_seesaw_origin": "https://doi.org/10.1103/PhysRevD.34.1642",
    "natural_low_rep_DT_comparison": "https://arxiv.org/abs/hep-ph/9810315",
    "DW_minimal_SO10_comparison": "https://arxiv.org/abs/hep-ph/9705366",
    "discrete_gauge_anomaly_scope": "https://arxiv.org/abs/hep-th/9109045",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def _rational_text(value: sp.Expr) -> str:
    return str(sp.factor(value))


def doublet_triplet_block(m_h: int | sp.Rational = 3, k_h: int | sp.Rational = 1) -> sp.Matrix:
    """Exact 10-vector Hessian in the V52 Cartesian ordering."""
    return sp.diag(*([sp.Rational(m_h) + 2 * sp.Rational(k_h)] * 6
                     + [sp.Rational(m_h) - 3 * sp.Rational(k_h)] * 4))


def doublet_triplet_audit() -> dict[str, Any]:
    matrix = doublet_triplet_block()
    perturbed = doublet_triplet_block(4, 1)
    color = matrix[:6, :6]
    weak = matrix[6:, 6:]
    return {
        "field_addition": "one H(10)",
        "renormalizable_superpotential": "W_DT=(mH/2) H^T H+(kH/2) H^T E H",
        "source_order_parameter": "E0=diag(2,2,2,2,2,2,-3,-3,-3,-3)",
        "rational_witness": {"mH": 3, "kH": 1},
        "full_10x10_diagonal": [int(value) for value in matrix.diagonal()],
        "color_triplet_coordinate_block": {
            "shape": list(color.shape), "rank": color.rank(), "nullity": 6 - color.rank(),
            "mass_eigenvalue": 5,
        },
        "weak_doublet_coordinate_block": {
            "shape": list(weak.shape), "rank": weak.rank(), "nullity": 4 - weak.rank(),
            "interpretation": "one massless Hu,Hd pair (four weak-component coordinates)",
        },
        "full_rank": matrix.rank(),
        "full_nullity": 10 - matrix.rank(),
        "massless_condition": "mH-3*kH=0",
        "condition_codimension": 1,
        "unit_mass_perturbation": {
            "mH": 4, "kH": 1, "rank": perturbed.rank(), "nullity": 10 - perturbed.rank(),
        },
        "selector_enforces_coefficient_relation": False,
        "natural_missing_partner_or_DW": False,
        "claim": "exact tree-level rank witness only; the required coefficient cancellation is tuned",
    }


def seesaw_matrices() -> dict[str, sp.Matrix]:
    m_d = sp.diag(sp.Rational(1, 100), sp.Rational(1, 50), sp.Rational(3, 100))
    portal = sp.zeros(3, 4)
    portal[0, 0], portal[1, 1], portal[2, 2] = 10, 20, 30
    singlet_mass = sp.diag(1000, 2000, 3000, 4000)
    zero33 = sp.zeros(3, 3)
    zero34 = sp.zeros(3, 4)
    heavy = zero33.row_join(portal).col_join(portal.T.row_join(singlet_mass))
    full = (
        zero33.row_join(m_d).row_join(zero34)
        .col_join(m_d.T.row_join(zero33).row_join(portal))
        .col_join(zero34.T.row_join(portal.T).row_join(singlet_mass))
    )
    induced_rh = -(portal * singlet_mass.inv() * portal.T)
    light = -(m_d.row_join(zero34) * heavy.inv() * m_d.T.col_join(zero34.T))
    return {
        "mD": m_d,
        "F": portal,
        "MS": singlet_mass,
        "heavy": heavy,
        "full": full,
        "induced_RH": induced_rh,
        "light": light,
    }


def seesaw_audit() -> dict[str, Any]:
    matrices = seesaw_matrices()
    return {
        "field_addition": "four Spin(10) singlets N_a; three participate in the rank witness and one is a massive parity spectator",
        "renormalizable_operators": [
            "(1/2) Y10_ij 16F_i 16F_j H10",
            "yN_ia 16F_i barC_H N_a",
            "(1/2) MS_ab N_a N_b",
        ],
        "neutral_basis": ["nu_L[3]", "nu_R^c[3]", "N[4]"],
        "dimensions": {name: list(matrix.shape) for name, matrix in matrices.items()},
        "ranks": {name: matrix.rank() for name, matrix in matrices.items()},
        "determinants": {
            "heavy_7x7": _rational_text(matrices["heavy"].det()),
            "full_10x10": _rational_text(matrices["full"].det()),
        },
        "induced_RH_Majorana_diagonal": [_rational_text(value) for value in matrices["induced_RH"].diagonal()],
        "effective_light_diagonal": [_rational_text(value) for value in matrices["light"].diagonal()],
        "exact_formula": "mnu=mD (F MS^{-1} F^T)^{-1} mD^T for the displayed nonsingular witness",
        "rank_three_Majorana_generation": matrices["induced_RH"].rank() == 3,
        "full_neutral_matrix_nonsingular": matrices["full"].rank() == 10,
        "source_vacuum_unchanged": "all matter and N scalar VEVs are zero; nonsingular MS fixes N=0",
    }


def selector_audit() -> dict[str, Any]:
    odd_weyl_dimension = 3 * 16 + 4
    so10_index_sum = 3 * 2
    operators = {
        "source_W": 0,
        "16F_16F_H10": (1 + 1 + 0) % 2,
        "16F_barC_N": (1 + 0 + 1) % 2,
        "N_N": (1 + 1) % 2,
        "forbidden_16F_barC_bilinear": (1 + 0) % 2,
        "forbidden_16F_C_H10_matter_Higgs_mixing": (1 + 0 + 0) % 2,
        "forbidden_three_matter_RPV_class": (1 + 1 + 1) % 2,
    }
    return {
        "group": "ordinary external Z2",
        "odd_superfields": ["16F_1", "16F_2", "16F_3", "N_1", "N_2", "N_3", "N_4"],
        "even_superfields": ["E54", "A45", "C16_H", "barC16_H", "H10"],
        "all_nonzero_VEV_fields_even": True,
        "operator_parities": operators,
        "required_operators_even": all(operators[name] == 0 for name in (
            "source_W", "16F_16F_H10", "16F_barC_N", "N_N")),
        "listed_dangerous_operators_odd": all(operators[name] == 1 for name in (
            "forbidden_16F_barC_bilinear",
            "forbidden_16F_C_H10_matter_Higgs_mixing",
            "forbidden_three_matter_RPV_class",
        )),
        "standard_discrete_anomaly_ledgers": {
            "odd_Weyl_dimension": odd_weyl_dimension,
            "odd_Weyl_dimension_mod2": odd_weyl_dimension % 2,
            "SO10_Dynkin_index_sum": so10_index_sum,
            "SO10_Dynkin_index_sum_mod2": so10_index_sum % 2,
            "cubic_Z2_charge_sum": odd_weyl_dimension,
            "cubic_Z2_charge_sum_mod2": odd_weyl_dimension % 2,
        },
        "why_four_not_three_singlets": "three N fields would give 51 odd Weyl components; the fourth makes the conservative gravity/cubic parity ledgers even",
        "all_order_selection_statement": "because every VEV is Z2-even, inserting any number of source VEVs cannot turn an odd-matter monomial even",
        "scope_caveat": "conventional low-energy anomaly arithmetic only; no continuous-parent or complete UV discrete-gauge construction is supplied",
    }


def perturbativity_audit() -> dict[str, Any]:
    source_t = 12 + 8 + 2 + 2
    added_higgs_t = 1
    matter_t = 3 * 2
    total_t = source_t + added_higgs_t + matter_t
    three_c2 = 3 * 8
    b = total_t - three_c2
    coupling = 0.73
    pole = math.exp(8 * math.pi**2 / (b * coupling**2)) if b > 0 else math.inf
    return {
        "convention": "b=sum_chiral T(R)-3 C2(Spin10), T10=1,T16=2,T45=8,T54=12,C2=8",
        "source_T": source_t,
        "added_H10_T": added_higgs_t,
        "four_singlets_T": 0,
        "three_matter_16_T": matter_t,
        "total_chiral_T": total_t,
        "one_loop_b": b,
        "g_at_matching_witness": coupling,
        "formal_landau_pole_over_matching_scale": pole,
        "above_100x_matching_scale": pole > 100,
        "scope_caveat": "excludes any future link/moose, doublet-triplet naturalizer, flavor messenger, or UV-selector completion",
    }


def build_report() -> dict[str, Any]:
    upstream = json.loads(UPSTREAM_JSON.read_text(encoding="utf-8"))
    dt = doublet_triplet_audit()
    seesaw = seesaw_audit()
    selector = selector_audit()
    perturbativity = perturbativity_audit()
    checks = {
        "upstream_exact_source_is_closed": upstream["core_sha256"] == "c07fd055da382cdc461b212679f70971ced8d4d13a319a51e2cbaabfecbeba52",
        "one_10H_has_exact_triplet_rank6": dt["color_triplet_coordinate_block"]["rank"] == 6,
        "one_10H_leaves_exactly_one_weak_HuHd_pair": dt["weak_doublet_coordinate_block"]["nullity"] == 4,
        "DT_relation_is_exposed_as_codimension_one": dt["condition_codimension"] == 1 and not dt["natural_missing_partner_or_DW"],
        "double_seesaw_heavy_block_has_rank7": seesaw["ranks"]["heavy"] == 7,
        "double_seesaw_full_matrix_has_rank10": seesaw["ranks"]["full"] == 10,
        "induced_RH_Majorana_matrix_has_rank3": seesaw["rank_three_Majorana_generation"],
        "all_required_Z2_operators_are_allowed": selector["required_operators_even"],
        "listed_matter_Higgs_and_RPV_operators_are_forbidden": selector["listed_dangerous_operators_odd"],
        "Z2_survives_all_declared_VEVs": selector["all_nonzero_VEV_fields_even"],
        "conservative_Z2_gravity_SO10_and_cubic_ledgers_are_even": all(
            selector["standard_discrete_anomaly_ledgers"][name] == 0
            for name in ("odd_Weyl_dimension_mod2", "SO10_Dynkin_index_sum_mod2", "cubic_Z2_charge_sum_mod2")
        ),
        "repaired_low_index_inventory_stays_perturbative_for_100x": perturbativity["above_100x_matching_scale"],
        "natural_DT_is_not_claimed": not dt["natural_missing_partner_or_DW"],
        "full_G2_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS if not failures else "V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT_FAILED",
        "upstream": {
            "path": UPSTREAM_JSON.name,
            "core_sha256": upstream["core_sha256"],
            "status": upstream["status"],
        },
        "minimal_additions": {
            "H10_count": 1,
            "singlet_count": 4,
            "new_Spin10_chiral_coordinates": 10,
            "new_Dynkin_index": 1,
        },
        "doublet_triplet": dt,
        "renormalizable_double_seesaw": seesaw,
        "surviving_selector": selector,
        "perturbativity": perturbativity,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "literature": LITERATURE,
        "gate_effect": {
            "renormalizable_RH_neutrino_mass_mechanism": "EXACT EXISTENCE WITNESS",
            "unbroken_matter_selector": "STANDARD Z2 LEDGER AND ALL-ORDER VEV-STABILITY WITNESS",
            "doublet_triplet_rank_existence": "EXACT BUT FINE-TUNED",
            "natural_doublet_triplet_splitting": "OPEN",
            "complete_operator_and_proton_decay_census": "OPEN",
            "UV_discrete_gauge_embedding": "OPEN",
            "G2": "OPEN",
            "clause_promotions": [],
        },
        "next_exact_target": (
            "replace mH=3*kH by a symmetry- or vacuum-enforced relation (or a genuine missing-VEV block), "
            "then enumerate every Z2-even renormalizable and leading nonrenormalizable operator and recompute the full source+Higgs vacuum/Hessian"
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    dt = report["doublet_triplet"]
    ss = report["renormalizable_double_seesaw"]
    z2 = report["surviving_selector"]
    rg = report["perturbativity"]
    lines = [
        "# SUSY V52 minimal seesaw and doublet-triplet repair audit",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
        "## Outcome",
        "",
        "A small, executable repair exists for two of the lean source's open obligations. Adding one",
        "`10_H` and four gauge singlets supplies a fully renormalizable rank-three double seesaw and",
        "an independent unbroken ordinary `Z2` selector. The same `10_H`, coupled to the existing",
        "`54_H`, has an exact color-triplet rank-six / weak-doublet nullity-four mass witness.",
        "",
        "The doublet-triplet result is deliberately fail-closed: it needs `m_H=3 k_H`, a",
        "codimension-one coefficient cancellation that the `Z2` does not enforce. It is therefore",
        "not a natural missing-partner or Dimopoulos-Wilczek solution, and G2 remains open.",
        "",
        "## Exact doublet-triplet block",
        "",
        "```text",
        "W_DT = (m_H/2) H^T H + (k_H/2) H^T E H",
        "E0   = diag(2,2,2,2,2,2,-3,-3,-3,-3)",
        "m_H=3, k_H=1  =>  M_H=diag(5,5,5,5,5,5,0,0,0,0)",
        "```",
        "",
        f"The triplet block has rank `{dt['color_triplet_coordinate_block']['rank']}` and the weak block",
        f"has nullity `{dt['weak_doublet_coordinate_block']['nullity']}`, exactly one `H_u,H_d` pair.",
        "Changing only `m_H` from 3 to 4 makes the full 10 by 10 block rank ten, exposing the tuning.",
        "",
        "## Renormalizable neutrino repair",
        "",
        "The allowed operators are `16_F 16_F 10_H`, `16_F barC_H N`, and `N N`. In the",
        "displayed rational witness the heavy 7 by 7 block has rank",
        f"`{ss['ranks']['heavy']}`, the full 10 by 10 neutral matrix has rank `{ss['ranks']['full']}`,",
        "and the induced right-handed Majorana matrix has rank three. Its exact light Schur",
        f"diagonal is `{ss['effective_light_diagonal']}` in witness units.",
        "",
        "## Surviving selector",
        "",
        "All three matter `16_F` multiplets and all four `N` singlets are odd; every Higgs field is",
        "even. Hence the odd-`B-L` Higgs VEV does not break this independent selector. The required",
        "operators are even, while matter-Higgs bilinears and the three-matter RPV class are odd.",
        f"The conservative ledgers contain `{z2['standard_discrete_anomaly_ledgers']['odd_Weyl_dimension']}` odd Weyl",
        f"components and Spin(10) index `{z2['standard_discrete_anomaly_ledgers']['SO10_Dynkin_index_sum']}`, both even.",
        "This is conventional discrete-anomaly arithmetic, not a constructed continuous-parent UV theory.",
        "",
        "## Perturbativity and boundary",
        "",
        f"The complete source + one `10_H` + three matter families has `sum T={rg['total_chiral_T']}`",
        f"and one-loop `b={rg['one_loop_b']}`. At `g=0.73`, the formal pole is",
        f"`{rg['formal_landau_pole_over_matching_scale']:.4e}` times the matching scale.",
        "Singlets add no Spin(10) index.",
        "",
        "No G2 clause is promoted. Natural doublet-triplet splitting, a UV origin for the selector,",
        "the exhaustive operator census, flavor fitting, proton decay, thresholds, and any link/moose",
        "integration remain open.",
        "",
        "## Primary-source anchors",
        "",
        "Singlet-assisted seesaw physics originates in [Mohapatra and Valle](https://doi.org/10.1103/PhysRevD.34.1642).",
        "Natural low-representation SO(10) doublet-triplet mechanisms require extra missing-VEV structure;",
        "see [Chacko and Mohapatra](https://arxiv.org/abs/hep-ph/9810315) and",
        "[Barr and Raby](https://arxiv.org/abs/hep-ph/9705366). The scope of low-energy discrete-gauge",
        "anomaly tests is discussed by [Banks and Dine](https://arxiv.org/abs/hep-th/9109045).",
        "",
    ]
    return "\n".join(lines)


def validate_report(report: Mapping[str, Any]) -> None:
    if report["n_failed"] != 0 or report["failures"]:
        raise ArithmeticError(report["failures"])
    if canonical_sha(report) != report["core_sha256"]:
        raise ArithmeticError("core hash mismatch")
    if report["gate_effect"]["G2"] != "OPEN" or report["gate_effect"]["clause_promotions"]:
        raise ArithmeticError("fail-closed gate boundary drift")
    if report["doublet_triplet"]["natural_missing_partner_or_DW"]:
        raise ArithmeticError("tuned rank witness was over-promoted")


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(markdown(report), encoding="utf-8", newline="\n")


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise ArithmeticError("JSON artifact drift")
    if MD_PATH.read_text(encoding="utf-8") != markdown(report):
        raise ArithmeticError("Markdown artifact drift")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        check_artifacts()
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
