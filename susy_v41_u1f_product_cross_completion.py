#!/usr/bin/env python3
"""V41 audit of the U(1)_F x U(1)_X x U(1)_H cross-anomaly block.

This is deliberately a narrow, fail-closed continuation of the V40
U(1)_F -> Z9 selector.  It distinguishes two questions that must not be
silently conflated:

* A threshold massed only by the charge-nine Theta fields preserves the old
  U(1)_X and U(1)_H lift.  Such a threshold cannot remove the F-X-H anomaly
  residue, because every pair changes that row by a multiple of nine.
* At the later P/Pbar threshold, which itself breaks U(1)_X, a two-pair
  Pati--Salam-singlet construction cancels every *cubic* anomaly coefficient
  containing U(1)_F and at least one of X,H.  This is an EFT threshold
  construction, not a common unbroken product-parent or a complete theory.

The V40 report's ``C_F_squared_X_H`` is retained only as a diagnostic.  A
charge monomial of degree four is not a four-dimensional local triangle
anomaly and is not treated as one here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import susy_v40_all_ring_selector as v40


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V41_U1F_PRODUCT_CROSS_COMPLETION.json"
MD_PATH = ROOT / "SUSY_V41_U1F_PRODUCT_CROSS_COMPLETION.md"
TEST_PATH = ROOT / "test_susy_v41_u1f_product_cross_completion.py"

N_X = 66
N_H = 85
N_Z5610 = N_X * N_H
N_F = 9

STATUS = (
    "V41_U1F_X_H_CUBIC_CROSS_BLOCK_CANCELLED_AT_P_PB_THRESHOLD__"
    "RESIDUAL_PRESERVING_THETA_THRESHOLD_NO_GO_PROVED__"
    "PRODUCT_UV_COMPLETION_FAIL_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combined_z5610(x: int, h: int) -> int:
    """V38's CRT convention for Z66 x Z85 ~= Z5610."""

    return (N_H * (x % N_X) + N_X * (h % N_H)) % N_Z5610


# The two threshold pairs have no Pati--Salam quantum numbers and no VEVs.
# Their z5610 entries are derived, not chosen independently, from their X/H
# charge lifts.  r4 is the superfield Z4R charge and pq is the V40 numerator.
THRESHOLD_FIELDS: dict[str, dict[str, int | str]] = {
    "ChiAPlus": {"F": 12, "X": 6, "H": 0, "r4": 0, "pq": 0, "mass_source": "Pb"},
    "ChiAMinus": {"F": -12, "X": -4, "H": 0, "r4": 0, "pq": 170, "mass_source": "Pb"},
    "ChiBPlus": {"F": 3, "X": -11, "H": 1, "r4": 0, "pq": 0, "mass_source": "P"},
    "ChiBMinus": {"F": -3, "X": 9, "H": -1, "r4": 0, "pq": -170, "mass_source": "P"},
}
for _row in THRESHOLD_FIELDS.values():
    _row["z5610"] = combined_z5610(int(_row["X"]), int(_row["H"]))

MASS_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Pb_ChiAPlus_ChiAMinus", ("Pb", "ChiAPlus", "ChiAMinus")),
    ("P_ChiBPlus_ChiBMinus", ("P", "ChiBPlus", "ChiBMinus")),
)

TRIANGLE_ROWS = (
    "F_X_squared",
    "F_squared_X",
    "F_H_squared",
    "F_squared_H",
    "F_X_H",
)


def f(row: Mapping[str, Any]) -> int:
    return int(row["F"])


def x(row: Mapping[str, Any]) -> int:
    return int(row["X"])


def h(row: Mapping[str, Any]) -> int:
    return int(row["H"])


def cross_triangle_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """All genuine 4D triangle coefficients that contain F and X/H."""

    fields = list(rows)
    return {
        "F_X_squared": sum(f(row) * x(row) ** 2 for row in fields),
        "F_squared_X": sum(f(row) ** 2 * x(row) for row in fields),
        "F_H_squared": sum(f(row) * h(row) ** 2 for row in fields),
        "F_squared_H": sum(f(row) ** 2 * h(row) for row in fields),
        "F_X_H": sum(f(row) * x(row) * h(row) for row in fields),
    }


def f_only_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    fields = list(rows)
    return {
        "F_cubed": sum(f(row) ** 3 for row in fields),
        "F_gravity": sum(f(row) for row in fields),
        "F_PS_squared": 0,  # all threshold fields are Pati--Salam singlets
    }


def non_f_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Rows changed by the workaround but not repaired by this narrow audit."""

    fields = list(rows)
    return {
        "X_cubed": sum(x(row) ** 3 for row in fields),
        "H_cubed": sum(h(row) ** 3 for row in fields),
        "X_squared_H": sum(x(row) ** 2 * h(row) for row in fields),
        "X_H_squared": sum(x(row) * h(row) ** 2 for row in fields),
        "X_gravity": sum(x(row) for row in fields),
        "H_gravity": sum(h(row) for row in fields),
        "Delta_b_F_N1SUSY": sum(f(row) ** 2 for row in fields),
        "Delta_b_X_N1SUSY": sum(x(row) ** 2 for row in fields),
        "Delta_b_H_N1SUSY": sum(h(row) ** 2 for row in fields),
        "Delta_b_XH_N1SUSY": sum(x(row) * h(row) for row in fields),
    }


def diagnostic_degree_four(rows: Iterable[Mapping[str, Any]]) -> int:
    return sum(f(row) ** 2 * x(row) * h(row) for row in rows)


def baseline_cross_rows() -> dict[str, int]:
    old = v40.conditional_v38_parent_cross_anomaly_audit()["rows"]
    return {
        "F_X_squared": int(old["C_F_X_squared"]),
        "F_squared_X": int(old["C_F_squared_X"]),
        "F_H_squared": int(old["C_F_H_squared"]),
        "F_squared_H": int(old["C_F_squared_H"]),
        "F_X_H": int(old["C_F_X_H"]),
    }


def threshold_field_rows() -> list[dict[str, Any]]:
    return [
        {"field": name, **row, "PS_representation": "(1,1,1)", "dim": 1}
        for name, row in THRESHOLD_FIELDS.items()
    ]


def full_field_for_term(name: str) -> Mapping[str, Any]:
    if name in THRESHOLD_FIELDS:
        return THRESHOLD_FIELDS[name]
    if name not in v40.FIELDS:
        raise KeyError(name)
    source = v40.FIELDS[name]
    return {
        "F": int(source["u1f"]),
        "X": int(v40.V38_X_LIFT.get(name, 0)),
        "H": int(v40.V38_H_LIFT.get(name, 0)),
        "z5610": int(source["z5610"]),
        "r4": int(source["r4"]),
        "pq": int(source["pq"]),
    }


def massability_audit() -> dict[str, Any]:
    terms: list[dict[str, Any]] = []
    for label, names in MASS_TERMS:
        rows = [full_field_for_term(name) for name in names]
        terms.append(
            {
                "label": label,
                "fields": list(names),
                "U1F": sum(int(row["F"]) for row in rows),
                "U1X": sum(int(row["X"]) for row in rows),
                "U1H": sum(int(row["H"]) for row in rows),
                "Z9": sum(int(row["F"]) for row in rows) % N_F,
                "Z5610": sum(int(row["z5610"]) for row in rows) % N_Z5610,
                "Z4R": sum(int(row["r4"]) for row in rows) % 4,
                "PQ_numerator_over_170": sum(int(row["pq"]) for row in rows),
            }
        )
    return {
        "superpotential_terms": terms,
        "all_terms_continuous_neutral": all(
            entry["U1F"] == entry["U1X"] == entry["U1H"] == entry["PQ_numerator_over_170"] == 0
            for entry in terms
        ),
        "all_terms_finite_neutral": all(entry["Z9"] == entry["Z5610"] == 0 for entry in terms),
        "all_terms_have_Z4R_superpotential_charge_two": all(entry["Z4R"] == 2 for entry in terms),
        "mass_matrix": {
            "basis": ["ChiAPlus", "ChiAMinus", "ChiBPlus", "ChiBMinus"],
            "nonzero_blocks_after_P_Pb_VEVs": [
                "[[0, lambda_A <Pb>], [lambda_A <Pb>, 0]]",
                "[[0, lambda_B <P>], [lambda_B <P>, 0]]",
            ],
            "determinant": "(lambda_A <Pb>)^2 (lambda_B <P>)^2",
            "rank_if_lambda_A_lambda_B_<P><Pb>_nonzero": 4,
            "conditionality": (
                "This is massability on the declared nonzero P/Pb branch; it is not a proof "
                "that the full F/D/soft potential selects that branch or that the four new scalars have zero VEV."
            ),
        },
        "threshold_relation_to_V38_no_go": (
            "P and Pb carry primitive X charges +2 and -2, rather than charges in 66 Z.  "
            "This threshold is therefore explicitly outside V38's residual-Z66-preserving heavy-threshold theorem."
        ),
    }


def finite_audit() -> dict[str, Any]:
    baseline = v40.finite_z9_audit()
    base_residues = v40.discrete_residue_audit()["necessary_Z9_Z5610_cross_residues"]
    rows = threshold_field_rows()
    delta_s1 = sum(int(row["F"]) % N_F for row in rows)
    delta_s3 = sum((int(row["F"]) % N_F) ** 3 for row in rows)
    coefficient = N_F * N_F + 3 * N_F + 2
    delta_cross_fzz = sum((int(row["F"]) % N_F) * int(row["z5610"]) ** 2 for row in rows) % N_F
    delta_cross_ffz = sum((int(row["F"]) % N_F) ** 2 * int(row["z5610"]) for row in rows) % N_F
    full_s1 = int(baseline["Delta_s1_canonical"]) + delta_s1
    full_s3 = int(baseline["Delta_s3_canonical"]) + delta_s3
    full_fzz = (int(base_residues["C_Z9_Z5610_squared_mod_9"]) + delta_cross_fzz) % N_F
    full_ffz = (int(base_residues["C_Z9_squared_Z5610_mod_9"]) + delta_cross_ffz) % N_F
    return {
        "new_field_Z5610_lifts": {
            row["field"]: {
                "X_mod_66": int(row["X"]) % N_X,
                "H_mod_85": int(row["H"]) % N_H,
                "z5610": int(row["z5610"]),
                "derived_formula": "85 (X mod 66) + 66 (H mod 85) mod 5610",
            }
            for row in rows
        },
        "threshold_Z9_increment": {
            "Delta_s1_canonical": delta_s1,
            "Delta_s3_canonical": delta_s3,
            "linear_condition_2Delta_s1_mod_9": (2 * delta_s1) % N_F,
            "cubic_condition_110Delta_s3_mod_54": (coefficient * delta_s3) % (6 * N_F),
            "C_Z9_Z5610_squared_mod_9_increment": delta_cross_fzz,
            "C_Z9_squared_Z5610_mod_9_increment": delta_cross_ffz,
        },
        "combined_V40_plus_threshold": {
            "Delta_s1_canonical": full_s1,
            "Delta_s3_canonical": full_s3,
            "linear_condition_2Delta_s1_mod_9": (2 * full_s1) % N_F,
            "cubic_condition_110Delta_s3_mod_54": (coefficient * full_s3) % (6 * N_F),
            "C_Z9_Z5610_squared_mod_9": full_fzz,
            "C_Z9_squared_Z5610_mod_9": full_ffz,
            "all_listed_finite_rows_still_vanish": (
                (2 * full_s1) % N_F == 0
                and (coefficient * full_s3) % (6 * N_F) == 0
                and full_fzz == 0
                and full_ffz == 0
            ),
        },
    }


def residual_preserving_theta_nogo() -> dict[str, Any]:
    return {
        "theorem": "Theta-only residual-preserving F-X-H cross-anomaly obstruction",
        "assumptions": [
            "Every full-rank heavy mass entry is a polynomial in ThetaPlus/ThetaMinus VEVs and has total F charge 9 n for an integer n.",
            "Those Higgs fields are X/H neutral, so a mass block connects states of fixed (X,H)=(x,h) only to states of (-x,-h).",
            "The ordinary threshold has no additional VEV carrying nonzero X or H charge.",
        ],
        "pair_identity": (
            "Delta C_F_X_H = f*x*h + (epsilon*9-f)(-x)(-h) = epsilon*9*x*h"
        ),
        "full_rank_block_extension": [
            "For a nonzero determinant monomial of a block, every selected entry obeys f_i+g_sigma(i)=9 n_i.",
            "Summing it gives sum_i f_i + sum_j g_j in 9 Z.",
            "The whole block contributes C_F_X_H=(sum_i f_i+sum_j g_j) x h, hence is in 9 Z.",
            "Adding blocks preserves the congruence, so the conclusion does not rely on diagonal pairwise masses.",
        ],
        "consequence": "Every such full-rank ordinary threshold shifts C_F_X_H by 0 modulo 9.",
        "V40_required_threshold_increment": -6,
        "required_increment_mod_9": (-6) % N_F,
        "conclusion": (
            "No finite collection of ordinary Theta-only residual-preserving pairs can cancel V40's "
            "C_F_X_H=+6 row: their total shift is always a multiple of nine.  This is independent of "
            "their X/H charges and is the decisive obstruction."
        ),
    }


def two_pair_minimality() -> dict[str, Any]:
    return {
        "restricted_class": (
            "Pati--Salam-singlet pairs with F charges (f,-f), each massed by one P or Pb insertion, "
            "so the threshold does not alter F^3, F-gravity, or F-PS^2."
        ),
        "one_pair_identity": {
            "Pb_pair": "Delta C_F_squared_X = +2 f^2",
            "P_pair": "Delta C_F_squared_X = -2 f^2",
            "target": 270,
            "required_square_if_one_Pb_pair": "f^2=135",
            "integer_solution_exists": False,
        },
        "two_pair_solution": {
            "Pb_pair": "(F,X,H)=(12,6,0) plus (-12,-4,0)",
            "P_pair": "(F,X,H)=(3,-11,1) plus (-3,9,-1)",
            "sum_C_F_X_squared": "240 + 120 = 360",
            "sum_C_F_squared_X": "288 - 18 = 270",
            "sum_C_F_X_H": "0 - 6 = -6",
        },
        "conclusion": "Two mass pairs (four chiral singlets) are minimal within this explicitly stated class.",
    }


def simple_quantized_gs_no_go() -> dict[str, Any]:
    return {
        "scope": (
            "Single compact axion, shifting only under U(1)_F by its minimal residual-preserving charge 9, "
            "with integer Chern--Weil levels in the same one-leg convention q_F k=A used by the V38 audit."
        ),
        "equations": {
            "F_X_squared": "9 k_XX = +360",  # cancels A=-360
            "F_X_H": "9 k_XH = -6",  # cancels A=+6
        },
        "integer_solution": {"k_XX": 40, "k_XH": None},
        "obstruction": "-6/9=-2/3 is not an integer.",
        "additional_boundary": (
            "An axion that shifts only under F cannot by itself cancel the F^2-X row under an X gauge variation."
        ),
        "not_excluded": (
            "A specified multi-axion/Stueckelberg/generalized-Chern--Simons or topological response with its full "
            "integral charge lattice and anomaly polynomial.  No such UV datum is supplied here."
        ),
    }


def ring_preservation_audit() -> dict[str, Any]:
    base = v40.ring_proof()
    threshold = threshold_field_rows()
    return {
        "V40_declared_VEVs_still_Z9_neutral": base["all_declared_VEVs_preserve_Z9"],
        "new_threshold_scalars_are_declared_noncondensing": True,
        "new_field_Z9_charges": {row["field"]: int(row["F"]) % N_F for row in threshold},
        "mass_sources_have_U1F_charge": {"P": 0, "Pb": 0},
        "ward_identity": (
            "Integrating out fields with U(1)_F-preserving P/Pb masses cannot generate an operator whose external "
            "Z9 charge is nonzero.  Theta VEV insertions can change a U(1)_F charge only by 9k."
        ),
        "same_orientation_source_charges": {"Q4": 12 % N_F, "Qc4": (-12) % N_F},
        "conditional_result": (
            "With <Chi>=0, the V40 all-declared-VEV proof for same-orientation Q4/Qc4 sources survives exactly.  "
            "A full potential proof of <Chi>=0 and a mixed-operator/proton calculation remain open."
        ),
        "same_orientation_all_ring_subproof_preserved_conditionally": True,
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (Path(__file__), TEST_PATH, ROOT / "susy_v40_all_ring_selector.py")
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path) if path.is_file() else None}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    threshold = threshold_field_rows()
    baseline = baseline_cross_rows()
    increment = cross_triangle_rows(threshold)
    net = {key: baseline[key] + increment[key] for key in TRIANGLE_ROWS}
    f_rows = f_only_rows(threshold)
    finite = finite_audit()
    massability = massability_audit()
    theta_nogo = residual_preserving_theta_nogo()
    minimality = two_pair_minimality()
    ring = ring_preservation_audit()
    gs = simple_quantized_gs_no_go()
    diagnostic_base = int(v40.conditional_v38_parent_cross_anomaly_audit()["rows"]["C_F_squared_X_H"])
    diagnostic_increment = diagnostic_degree_four(threshold)
    report: dict[str, Any] = {
        "schema": "susy-v41-u1f-product-cross-completion-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "full_gate_closed": False,
        "purpose": (
            "Determine the exact status of the V40 U(1)_F cross anomaly block against the V38 X/H lifts "
            "without relabelling an EFT threshold as a UV completion."
        ),
        "threshold_field_packet": threshold,
        "continuous_cross_triangle_audit": {
            "normalization": "sum over left-handed Weyl fermions; all four new fields are PS singlets of multiplicity one",
            "baseline_V40_rows": baseline,
            "threshold_increment": increment,
            "net_rows": net,
            "all_genuine_F_X_H_triangle_rows_cancel": all(value == 0 for value in net.values()),
        },
        "F_only_anomaly_preservation": {
            "threshold_increment": f_rows,
            "all_F_only_rows_preserved": all(value == 0 for value in f_rows.values()),
        },
        "massability": massability,
        "finite_remnant_audit": finite,
        "same_orientation_ring_preservation": ring,
        "residual_preserving_theta_threshold_no_go": theta_nogo,
        "restricted_two_pair_minimality": minimality,
        "simple_quantized_GS_subcase": gs,
        "degree_four_diagnostic_not_a_triangle_anomaly": {
            "baseline_C_F_squared_X_H": diagnostic_base,
            "threshold_increment": diagnostic_increment,
            "net": diagnostic_base + diagnostic_increment,
            "reason_not_promoted": (
                "F^2 X H has charge degree four.  In four dimensions it is not a local perturbative triangle-anomaly "
                "coefficient, so its nonzero diagnostic value is not an uncancelled triangle anomaly."
            ),
        },
        "unrepaired_or_new_rows": {
            "threshold_increment_not_in_F_cross_block": non_f_rows(threshold),
            "why_full_product_parent_is_not_claimed": [
                "The pre-existing V38 X^3, X^2H, XH^2, gravitational, and discrete-R/product-bordism rows are not cancelled here.",
                "The P/Pb threshold breaks the old U(1)_X/Z66 direction and lies outside the V38 residual-preserving no-go assumptions.",
                "The exact F/D/soft vacuum, threshold matching, kinetic mixing, perturbative running, and all mixed baryon operators remain uncomputed.",
                "A multi-axion or topological GS completion requires a specified quantized charge lattice and is not inferred from arithmetic alone.",
            ],
        },
        "promotion_boundary": {
            "established": [
                "a two-pair, four-chiral-singlet P/Pb-threshold solution for the five genuine F-X/H triangle rows",
                "massability of that packet on a nonzero P/Pb background",
                "conditional preservation of the V40 same-orientation Z9 all-declared-VEV selector proof",
                "a Theta-only residual-preserving heavy-threshold obstruction and a simple single-axion GS obstruction",
            ],
            "not_established": [
                "a common unbroken 4D U(1)_F x U(1)_X x U(1)_H UV parent",
                "a complete anomaly-free product including X/H, Z4R, global/bordism, and gravity data",
                "a physical vacuum, spectrum, beta-function evolution, cosmology, flavour fit, or proton lifetime",
            ],
        },
        "references": [
            "https://arxiv.org/abs/hep-ph/9210211",
            "https://arxiv.org/abs/hep-th/9602178",
            "https://arxiv.org/abs/1909.08775",
        ],
        "source_manifest": source_manifest(),
    }
    checks = {
        "baseline_rows_match_V40": baseline == {
            "F_X_squared": -360,
            "F_squared_X": -270,
            "F_H_squared": 0,
            "F_squared_H": 0,
            "F_X_H": 6,
        },
        "all_genuine_F_X_H_triangle_rows_cancel": report["continuous_cross_triangle_audit"]["all_genuine_F_X_H_triangle_rows_cancel"],
        "F_only_rows_preserved": report["F_only_anomaly_preservation"]["all_F_only_rows_preserved"],
        "threshold_mass_terms_are_allowed": (
            massability["all_terms_continuous_neutral"]
            and massability["all_terms_finite_neutral"]
            and massability["all_terms_have_Z4R_superpotential_charge_two"]
            and massability["mass_matrix"]["rank_if_lambda_A_lambda_B_<P><Pb>_nonzero"] == 4
        ),
        "finite_Z9_and_listed_Z9_Z5610_rows_preserved": finite["combined_V40_plus_threshold"]["all_listed_finite_rows_still_vanish"],
        "same_orientation_ring_subproof_preserved_conditionally": ring["same_orientation_all_ring_subproof_preserved_conditionally"],
        "theta_only_residual_preserving_obstruction_is_nonvacuous": theta_nogo["required_increment_mod_9"] == 3,
        "one_pair_restricted_minimality_obstruction_is_nonvacuous": not minimality["one_pair_identity"]["integer_solution_exists"],
        "simple_GS_integrality_obstruction_is_nonvacuous": gs["integer_solution"]["k_XH"] is None,
        "no_full_gate_promoted": report["full_gate_closed"] is False and report["complete_theory_exists"] is False,
        "source_files_present": all(entry["exists"] for entry in report["source_manifest"]),
    }
    report["checks"] = checks
    report["n_failed"] = sum(not value for value in checks.values())
    report["failures"] = [name for name, value in checks.items() if not value]
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = report["continuous_cross_triangle_audit"]
    mass = report["massability"]
    finite = report["finite_remnant_audit"]["combined_V40_plus_threshold"]
    theta = report["residual_preserving_theta_threshold_no_go"]
    extra = report["unrepaired_or_new_rows"]["threshold_increment_not_in_F_cross_block"]
    table = "\n".join(
        f"| {key} | {rows['baseline_V40_rows'][key]} | {rows['threshold_increment'][key]} | {rows['net_rows'][key]} |"
        for key in TRIANGLE_ROWS
    )
    return f"""# V41 U(1)F product cross-anomaly audit

Status: `{report['status']}`

This is a bounded anomaly calculation, not a complete theory or a promoted G1
solution.  It separates an exact obstruction for a residual-preserving threshold
from a conditional later-threshold workaround.

## Exact cubic cross block

| Triangle row | V40 | New singlets | Net |
|---|---:|---:|---:|
{table}

The four new PS-singlet chiral fields are massed by
`Pb ChiAPlus ChiAMinus` and `P ChiBPlus ChiBMinus`.  Every listed continuous,
Z9, Z5610, PQ, and Z4R term check passes.  On a nonzero P/Pb background the
two 2-by-2 blocks have full rank four.  The construction uses exactly two mass
pairs in the stated class; one P/Pb pair would require the non-square
`f^2=135` to produce the required `C_F^2X=+270`.

The combined finite audit still passes: Z9 linear residue
`{finite['linear_condition_2Delta_s1_mod_9']}`, cubic residue
`{finite['cubic_condition_110Delta_s3_mod_54']}`, and both displayed
Z9-Z5610 residues are zero.

## What is obstructed

For a threshold massed only by an X/H-neutral Theta field,
`(f,x,h)` pairs with `(±9-f,-x,-h)`.  Thus
`Delta C_FXH=±9*x*h`, always zero modulo nine.  V40 needs an increment
`{theta['V40_required_threshold_increment']} = {theta['required_increment_mod_9']} mod 9`, so no
finite collection of such residual-preserving ordinary pairs can solve it.

A single compact axion shifting only by the minimal F charge nine also fails
in the stated integer-level convention: `9 k_XH=-6` has no integer solution.
A specified multi-axion/topological response remains a distinct, unprovided
possibility.

## Boundary

The workaround is deliberately outside the V38 unbroken-Z66 theorem: P/Pb
carry X charges `+2/-2`, so their VEVs break that old direction.  It preserves
the V40 Z9 proof only conditionally, assuming the four new threshold scalars do
not condense.  It does not cancel the remaining X/H, Z4R, gravitational,
global/bordism, vacuum, running, flavour, cosmology, or mixed-operator rows.
For example its non-F increments are `{extra}`.

`F^2 X H` is shown only as a degree-four diagnostic, not treated as a 4D
triangle anomaly.

References: [Ibanez](https://arxiv.org/abs/hep-ph/9210211),
[Gonzalez-Rey](https://arxiv.org/abs/hep-th/9602178), and
[Witten--Yonekura](https://arxiv.org/abs/1909.08775).

Core SHA-256: `{report['core_sha256']}`
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
        raise RuntimeError("V41 U1F product JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V41 U1F product Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    if args.check:
        check_artifacts()
        print("V41_U1F_PRODUCT_CROSS_COMPLETION_ARTIFACTS_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
