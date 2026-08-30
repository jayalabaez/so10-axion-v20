from __future__ import annotations

"""Exact residual-Abelian selector no-go for the V54 charged-source rescue.

The result is deliberately narrow.  It applies to any additive residual factor
(ordinary or R) under which the GUT-scale VEVs are neutral, when the four R1
filter terms and direct Yukawas for two distinct families are retained.  In
that scope the same congruences force a genuine mixed-family Spin(10)
F_a^2 F_b^2 invariant to be allowed.  A same-family fourth power is explicitly
excluded by the exact Spin(10) tensor audit.
"""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
UPSTREAM_PATH = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"
MATTER_PATH = ROOT / "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.json"
EXPECTED_MATTER_CORE = "895f999b53fcf7c4e513e0f9c6ee3245d166d8db8d3cfceaff3d9d8c2af25330"
JSON_PATH = ROOT / "SUSY_V55_R1_RESIDUAL_SELECTOR_NO_GO_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_RESIDUAL_SELECTOR_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v55_r1_residual_selector_no_go_audit.py"
STATUS = (
    "V55_R1_ADDITIVE_SELECTOR_NO_GO__SOURCE_TERMS_FORCE_L_EQUALS_A_EQUALS_B_"
    "AND_THEREFORE_ALLOW_RENORMALIZABLE_h_A_H2_AND_L_h_H2__BOTH_FILL_WEAK_KERNEL__"
    "ANY_RESIDUAL_ORDINARY_OR_R_FACTOR_"
    "PRESERVING_THE_VACUUM_FILTER_AND_TWO_DIRECT_YUKAWAS_ALLOWS_MIXED_FAMILY_F4__"
    "SAME_FAMILY_FOURTH_POWER_TENSOR_ABSENT__ACTUAL_UNIVERSAL_FAMILIES_HAVE_"
    "DEGREE9_S4R_DRESSING__NO_GATE_PROMOTION"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("core_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_upstream() -> dict[str, Any]:
    value = json.loads(UPSTREAM_PATH.read_text(encoding="utf-8"))
    if value["core_sha256"] != EXPECTED_UPSTREAM_CORE:
        raise RuntimeError("stale V54 charged-source rescue core")
    return value


def load_matter_audit() -> dict[str, Any]:
    value = json.loads(MATTER_PATH.read_text(encoding="utf-8"))
    if value["core_sha256"] != EXPECTED_MATTER_CORE:
        raise RuntimeError("stale V55 matter/operator core")
    return value


def determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    total = 0
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = -1 if inversions % 2 else 1
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        total += term
    return total


def finite_congruence_check(maximum_modulus: int = 128) -> dict[str, Any]:
    """Exhaust standard ordinary (w=0) and R (w=2) factors.

    Once H2 and a common direct-Yukawa family residue are chosen, the other
    filter charges are fixed.  Two distinct family fields may carry this same
    residue, as in the actual universal-family R1 ledger.  Every solution is
    checked directly rather than dividing by two modulo a composite modulus.
    """

    rows: list[dict[str, Any]] = []
    total_solutions = 0
    counterexamples: list[dict[str, int | str]] = []
    for modulus in range(2, maximum_modulus + 1):
        row: dict[str, Any] = {"modulus": modulus}
        for kind, raw_w in (("ordinary", 0), ("R", 2)):
            w = raw_w % modulus
            solutions = 0
            for h2 in range(modulus):
                if (2 * h2 - w) % modulus:
                    continue
                h = (w - h2) % modulus
                barh = (w - h) % modulus
                h1 = (w - barh) % modulus
                for f3 in range(modulus):
                    if (2 * f3 + h1 - w) % modulus:
                        continue
                    required = [
                        (h1 + barh - w) % modulus,
                        (barh + h - w) % modulus,
                        (h + h2 - w) % modulus,
                        (2 * h2 - w) % modulus,
                        (2 * f3 + h1 - w) % modulus,
                    ]
                    if any(required):
                        raise ArithmeticError("internal congruence construction failure")
                    solutions += 1
                    if (4 * f3 - w) % modulus:
                        counterexamples.append(
                            {
                                "kind": kind,
                                "modulus": modulus,
                                "w": w,
                                "shared_family_residue": f3,
                                "H1": h1,
                            }
                        )
            row[f"{kind}_superpotential_charge"] = w
            row[f"{kind}_solution_count"] = solutions
            total_solutions += solutions
        rows.append(row)
    return {
        "maximum_modulus": maximum_modulus,
        "factors_checked": 2 * (maximum_modulus - 1),
        "solution_count": total_solutions,
        "counterexample_count": len(counterexamples),
        "counterexamples": counterexamples,
        "per_modulus": rows,
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    matter = load_matter_audit()
    rescue = upstream["charged_source_dynamical_rescue"]
    tensor = matter["Spin10_center_and_tensor_audit"]
    fatal_filler = matter["complete_Higgs_10_bilinear_census"]["fatal_earliest_filler"]
    finite = finite_congruence_check()
    weak_with_A_filler = [
        [0, 1, 0, 0],
        [1, 0, 2, 0],
        [0, 2, 0, 3],
        [0, 0, 3, 3],
    ]
    weak_with_A_determinant = determinant(weak_with_A_filler)

    # P,S,T,R,M,L,K,C,barC all acquire GUT-scale VEVs in the certificate.
    continuous_vev_charges = [6, -12, -6, 4, -2, 1, 2, 0, -1]
    residual_order = math.gcd(*[abs(value) for value in continuous_vev_charges])

    actual_charges = {
        "F1": 11,
        "F2": 11,
        "F3": 11,
        "H1": -22,
        "barh": 16,
        "h": -4,
        "H2": 3,
        "A": 1,
        "P": 6,
        "S": -12,
        "T": -6,
        "B": 1,
        "R": 4,
    }
    actual_required_sums = {
        "P_H1_barh": actual_charges["P"] + actual_charges["H1"] + actual_charges["barh"],
        "S_barh_h": actual_charges["S"] + actual_charges["barh"] + actual_charges["h"],
        "h_B_H2": actual_charges["h"] + actual_charges["B"] + actual_charges["H2"],
        "h_A_H2": actual_charges["h"] + actual_charges["A"] + actual_charges["H2"],
        "T_H2_squared": actual_charges["T"] + 2 * actual_charges["H2"],
        "F1_F1_H1": 2 * actual_charges["F1"] + actual_charges["H1"],
        "F2_F2_H1": 2 * actual_charges["F2"] + actual_charges["H1"],
        "F3_F3_H1": 2 * actual_charges["F3"] + actual_charges["H1"],
    }
    dressing_charge = 4 * actual_charges["S"] + actual_charges["R"]
    f4_charge = 2 * actual_charges["F1"] + 2 * actual_charges["F2"]

    checks = {
        "upstream_core_is_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "matter_tensor_core_is_bound": matter["core_sha256"] == EXPECTED_MATTER_CORE,
        "actual_R1_required_terms_are_continuous_U1_neutral": not any(actual_required_sums.values()),
        "continuous_U1_is_completely_broken": residual_order == 1,
        "actual_S4R_dressing_cancels_mixed_family_F4": f4_charge + dressing_charge == 0,
        "actual_first_F4_dressing_matches_upstream": rescue["operator_screen"]["first_F4_dressing"]
        == {"insertions": 5, "fields": ["S", "S", "S", "S", "R"]},
        "finite_congruence_scan_has_solutions": finite["solution_count"] > 0,
        "finite_congruence_scan_has_no_counterexample": finite["counterexample_count"] == 0,
        "matter_audit_finds_forced_renormalizable_filler": (
            fatal_filler["operator"] == "L h_10 H2_10"
            and fatal_filler["renormalizable"]
            and fatal_filler["charge_arithmetic"] == "1-4+3=0"
        ),
        "independent_h_A_H2_filler_is_neutral": actual_required_sums["h_A_H2"] == 0,
        "nonmissing_A_weak_VEV_fills_filter": weak_with_A_determinant == 9,
        "forced_filler_removes_all_four_weak_modes": (
            fatal_filler["one_weak_component_rank_before_QQ"] == 3
            and fatal_filler["one_weak_component_rank_after_QQ"] == 4
            and fatal_filler["weak_Higgs_nullity_after"] == 0
        ),
        "same_family_fourth_power_is_tensor_absent": tensor[
            "single_family_F_i_fourth_power_is_absent"
        ],
        "mixed_family_two_plus_two_tensor_exists": [2, 2, 0]
        in tensor["gauge_valid_patterns"],
        "no_gate_is_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy-v55-r1-residual-selector-no-go-audit-v1",
        "status": STATUS,
        "upstream_core_sha256": upstream["core_sha256"],
        "matter_operator_core_sha256": matter["core_sha256"],
        "source_filter_filler_theorem": {
            "scope": (
                "any additive symmetry factor, ordinary or R, applied to the full source and "
                "filter superpotential; no assumption about unbroken VEV charges is needed"
            ),
            "required_terms": [
                "M A^2",
                "M A B",
                "barC A C",
                "L barC C",
                "h B H2",
            ],
            "congruences_mod_N": [
                "r(M)+2 r(A)=w",
                "r(M)+r(A)+r(B)=w",
                "r(barC)+r(A)+r(C)=w",
                "r(L)+r(barC)+r(C)=w",
                "r(h)+r(B)+r(H2)=w",
            ],
            "exact_derivation_mod_N": [
                "subtract MAB from MA^2: r(A)=r(B)",
                "subtract L barC C from barC A C: r(A)=r(L)",
                "therefore both r(A)+r(h)+r(H2) and r(L)+r(h)+r(H2) equal w",
            ],
            "forced_operators": ["h_10 A45 H2_10", fatal_filler["operator"]],
            "actual_charge_arithmetic": {
                "h_A_H2": "-4+1+3=0",
                "L_h_H2": fatal_filler["charge_arithmetic"],
            },
            "renormalizable": True,
            "L_VEV_nonzero": fatal_filler["L_VEV_nonzero"],
            "A_weak_block_coefficient": 3,
            "one_weak_component_matrix_with_actual_h_A_H2": weak_with_A_filler,
            "one_weak_component_determinant_with_h_A_H2_coefficient_x": "x^2",
            "one_weak_component_determinant_at_actual_A_weak_coefficient": weak_with_A_determinant,
            "weak_rank_before": fatal_filler["weak_filter_rank_before"],
            "weak_rank_after": fatal_filler[
                "weak_filter_rank_after_generic_direct_hH2_mass"
            ],
            "weak_Higgs_nullity_after": fatal_filler["weak_Higgs_nullity_after"],
            "conclusion": (
                "every product of additive Abelian ordinary/R selectors that retains these "
                "terms also retains h A H2 and L h H2; R1 cannot be repaired by an Abelian "
                "overlay, and removing L alone is insufficient"
            ),
        },
        "theorem": {
            "scope": (
                "any additive residual Abelian factor, ordinary or R, under which every "
                "GUT-scale VEV in P H1 barh, S barh h, h B H2 and T H2^2 is neutral"
            ),
            "required_terms": [
                "P H1 barh",
                "S barh h",
                "h B H2",
                "T H2^2",
                "Fa Fa H1 for one family a",
                "Fb Fb H1 for a distinct family b",
            ],
            "congruences_mod_N": [
                "r(H1)+r(barh)=w",
                "r(barh)+r(h)=w",
                "r(h)+r(H2)=w",
                "2 r(H2)=w",
                "2 r(Fa)+r(H1)=w",
                "2 r(Fb)+r(H1)=w",
            ],
            "exact_derivation_mod_N": [
                "r(h)=w-r(H2)=r(H2)",
                "r(barh)=w-r(h)=r(H2)",
                "r(H1)=w-r(barh)=r(H2)",
                "2 r(Fa)=2 r(Fb)=w-r(H1)=r(H2)",
                "2 r(Fa)+2 r(Fb)=2 r(H2)=w",
            ],
            "conclusion": (
                "the mixed-family Fa^2 Fb^2 charge class is allowed factorwise; therefore any "
                "product of such additive residual factors also allows it"
            ),
            "ordinary_symmetry": "w=0",
            "R_symmetry": "w is the fixed superpotential charge (standard Z_N^R uses w=2 mod N)",
        },
        "SO10_tensor_certificate": {
            "method": tensor["tensor_scope"],
            "same_family_F_i_fourth_power_is_absent": tensor[
                "single_family_F_i_fourth_power_is_absent"
            ],
            "three_plus_one_pattern_is_absent": tensor[
                "three_plus_one_family_pattern_is_absent"
            ],
            "nonzero_mixed_family_pattern": [2, 2, 0],
            "mixed_family_multiplicity": 1,
            "nonzero_mixed_family_invariant": "F1^2 F2^2 in the exact D5 singlet channel",
            "physical_scope": (
                "the invariant contains the supersymmetric baryon/lepton violating four-matter "
                "class; a lifetime still requires mediator matching and dressing"
            ),
        },
        "finite_verification": finite,
        "actual_R1_witness": {
            "continuous_U1_VEV_charges": continuous_vev_charges,
            "VEV_charge_gcd_and_residual_order": residual_order,
            "charges": actual_charges,
            "required_term_charge_sums": actual_required_sums,
            "mixed_F1_squared_F2_squared_charge": f4_charge,
            "S_power4_R_dressing_charge": dressing_charge,
            "allowed_operator": "(F1^2 F2^2)_Spin10-singlet S^4 R / Lambda^6",
            "total_degree": 9,
            "matches_upstream_first_dressing": True,
        },
        "logical_escapes_not_excluded": [
            "change the source or four-10 filter topology and remove at least one filler-theorem hypothesis",
            "replace the direct top Yukawa by mediator mixing, compositeness or locality",
            "use a genuinely non-Abelian family rule whose tensor product removes every mixed F4 class",
            "accept the allowed operator and prove its matched Wilson coefficient is safe",
        ],
        "gate_ledger": {
            "G4": "failed for R1; the symmetry-complete action contains the forced renormalizable L h H2 filler",
            "G7": "not promoted; an exact degree-nine proton-class operator is allowed",
            "other_gates": "unchanged",
        },
        "primary_sources": [
            {
                "title": "Constraining Proton Lifetime in SO(10) with Stabilized Doublet-Triplet Splitting",
                "url": "https://arxiv.org/abs/1003.2625",
            },
            {
                "title": "Neutrino masses, anomalous U(1) gauge symmetry and doublet-triplet splitting",
                "url": "https://arxiv.org/abs/hep-ph/0104200",
            },
        ],
        "checks": checks,
        "n_failed_checks": sum(not value for value in checks.values()),
        "source_manifest": [
            {"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)},
            {"path": UPSTREAM_PATH.name, "sha256": sha256_file(UPSTREAM_PATH)},
            {"path": MATTER_PATH.name, "sha256": sha256_file(MATTER_PATH)},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("V55 selector status drift")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V55 selector core drift")
    if report["n_failed_checks"] or not all(report["checks"].values()):
        raise RuntimeError("V55 selector integrity failure")
    if report["finite_verification"]["counterexamples"]:
        raise RuntimeError("residual selector theorem was falsified")


def render_markdown(report: Mapping[str, Any]) -> str:
    actual = report["actual_R1_witness"]
    finite = report["finite_verification"]
    return f"""# V55 R1 residual-selector no-go audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact theorem

For any additive ordinary or R symmetry factor, the required source terms
`M A^2`, `M A B`, `barC A C`, and `L barC C` force
`r(L)=r(A)=r(B)`.  The required filter term `h B H2` then immediately forces
both `h A H2` and `L h H2` to carry the superpotential charge.  This is
independent of whether the symmetry survives the vacuum.  The exact `A` VEV
has weak coefficient 3, while `L` also has a VEV.  Either filler raises the
weak-filter rank from `{report['source_filter_filler_theorem']['weak_rank_before']}`
to `{report['source_filter_filler_theorem']['weak_rank_after']}` and all four
weak-Higgs zero modes disappear.  Removing `L` alone is therefore insufficient.

No product of additive Abelian selectors can repair this action without
removing a required source/filter term.

## Residual proton theorem

Let `w` be the fixed superpotential charge of any additive residual ordinary or
R symmetry.  If the R1 vacuum is neutral under the residual factor and the
terms `P H1 barh`, `S barh h`, `h B H2`, `T H2^2`, and direct Yukawas for two
distinct families `Fa Fa H1` and `Fb Fb H1` are retained,
their congruences imply

`r(h)=r(barh)=r(H1)=r(H2)`, `2 r(Fa)=2 r(Fb)=r(H2)`, and therefore
`2 r(Fa)+2 r(Fb)=2 r(H2)=w (mod N)`.

The exact tensor census removes a same-family fourth power, but it contains one
genuine `Fa^2 Fb^2` singlet for distinct families.  This mixed operator is
therefore allowed.  The argument applies factorwise, so a product of additive
residual Abelian factors does not repair the universal-family R1 action.

The finite audit checked `{finite['factors_checked']}` ordinary/R factors through
`Z_{finite['maximum_modulus']}`, found `{finite['solution_count']}` charge
solutions satisfying all hypotheses, and found zero counterexamples.

## Actual V54 charged-source action

The VEV-charge gcd is `{actual['VEV_charge_gcd_and_residual_order']}`, so the
continuous U(1) itself leaves no nontrivial discrete subgroup.  The top-family
mixed-family operator has charge
`{actual['mixed_F1_squared_F2_squared_charge']}` and the exact `S^4 R`
dressing has charge `{actual['S_power4_R_dressing_charge']}`.  Hence

`{actual['allowed_operator']}`

is allowed at total degree `{actual['total_degree']}`, exactly matching the V54
bounded operator search.

## Decision

R1 is rejected as a symmetry-complete natural-DT action: its two forced
renormalizable fillers remove the Higgs pair.  No gate is promoted.  G7 also
remains open.  Possible exits require a changed source/filter, mediator-generated
top Yukawa, genuinely non-Abelian matter selection, or an explicit
Wilson/lifetime proof for a successor action.

Primary context: https://arxiv.org/abs/1003.2625
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("stale V55 selector JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale V55 selector Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V55_R1_RESIDUAL_SELECTOR_NO_GO_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
