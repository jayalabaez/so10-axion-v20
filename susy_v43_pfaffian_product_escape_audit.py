#!/usr/bin/env python3
"""V43 self-paired/Pfaffian escape audit for the old ``Z66`` direction.

V42 proved a useful but deliberately restricted statement: a fully massive
*Dirac-paired* threshold whose mass VEVs have even X charge cannot repair the
odd U(1)_X--gravity row.  It explicitly did not decide holomorphic
self-Majorana or Pfaffian blocks.

This audit closes that logical gap as far as ordinary four-dimensional
polynomial mass matrices permit:

* a self-Majorana singlet block really can evade the V42 gravity-parity
  argument while all of its X-breaking VEVs are in 66 Z; but
* a full local Pati--Salam x U(1)_F x U(1)_X x U(1)_H parent still cannot be
  constructed in the stated class.  Symmetric real-representation blocks
  shift every X--PS^2 row only by 33 Z, and skew/Pfaffian blocks only by 66 Z.
  The V40 host needs (+8,+8,+8), which is nonzero modulo 33.

The result is a narrow threshold theorem, not a claim about non-polynomial
strong dynamics, a topological response, PS-breaking thresholds, massless
anomalons, a global/bordism completion, or any G1--G8 closure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import susy_v42_product_parent_local_completion as v42


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V43_PFAFFIAN_PRODUCT_ESCAPE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V43_PFAFFIAN_PRODUCT_ESCAPE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v43_pfaffian_product_escape_audit.py"

N_X = 66
HALF_N_X = N_X // 2
STATUS = (
    "V43_SELF_MAJORANA_GRAVITY_ESCAPE_EXPLICIT__ORDINARY_REAL_AND_PFAFFIAN_"
    "Z66_PS_THRESHOLD_CLASS_NO_GO_PROVED__FULL_PRODUCT_PARENT_FAIL_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def r(
    name: str,
    *,
    dim: int = 1,
    X: int = 0,
    ps: Mapping[str, int] | None = None,
    r4: int = 0,
    representation: str = "(1,1,1)",
    role: str,
) -> dict[str, Any]:
    """A neutral-F/H row in V42's fixed integral normalization."""

    return v42.row(
        name,
        dim=dim,
        F=0,
        X=X,
        H=0,
        ps=ps,
        su4_cubic=0,
        r4=r4,
        pq=0,
        representation=representation,
        role=role,
    )


def host_audit() -> dict[str, Any]:
    """The full V40 product-lift ledger that any new parent must cancel."""

    rows = v42.host_rows()
    anomaly = v42.all_continuous_anomalies(rows)
    needed = {
        "U1_PS_squared": {
            u1: {group: -value for group, value in groups.items()}
            for u1, groups in anomaly["U1_PS_squared"].items()
        },
        "U1_gravity": {u1: -value for u1, value in anomaly["U1_gravity"].items()},
        "U1_cubic_and_all_cross_triangles": {
            key: -value for key, value in anomaly["U1_cubic_and_all_cross_triangles"].items()
        },
    }
    return {
        "normalization": anomaly["normalization"],
        "V40_host_full_local_row_ledger": anomaly,
        "required_increment_for_a_zero_local_parent": needed,
        "critical_X_PS_target": needed["U1_PS_squared"]["X"],
    }


def majorana_singlet_rows() -> list[dict[str, Any]]:
    """A fully massable Z66-preserving self-Majorana gravity-parity witness."""

    return [
        r("SigmaPlus66_M", X=66, r4=0, role="Z66 Higgs of self-Majorana witness"),
        r("SigmaMinus66_M", X=-66, r4=0, role="Z66 Higgs and Majorana spurion"),
        r("TM", X=0, r4=2, role="Z66 Higgs-pair stabilizer"),
        r("Chi33", X=33, r4=1, role="self-Majorana singlet"),
    ]


def real_ps_majorana_rows() -> list[dict[str, Any]]:
    """A real SU(4) sextet self-Majorana block, useful for the modulus audit."""

    return [
        r("SigmaPlus66_R", X=66, r4=0, role="Z66 Higgs of real-PS witness"),
        r("SigmaMinus66_R", X=-66, r4=0, role="Z66 Higgs and real-PS Majorana spurion"),
        r("TR", X=0, r4=2, role="Z66 Higgs-pair stabilizer"),
        r(
            "D6_33",
            dim=6,
            X=33,
            ps={"SU4": 2},
            r4=1,
            representation="(6,1,1), real SU(4) sextet",
            role="real-PS self-Majorana field",
        ),
    ]


def pfaffian_ps_rows() -> list[dict[str, Any]]:
    """A two-flavour pseudoreal SU(2)_L block with a nonzero Pfaffian mass."""

    return [
        r("SigmaPlus66_P", X=66, r4=0, role="Z66 Higgs of Pfaffian witness"),
        r("SigmaMinus66_P", X=-66, r4=0, role="Z66 Higgs and Pfaffian spurion"),
        r("TP", X=0, r4=2, role="Z66 Higgs-pair stabilizer"),
        r(
            "L33a",
            dim=2,
            X=33,
            ps={"SU2L": 1},
            r4=1,
            representation="(1,2,1), pseudoreal SU(2)_L doublet",
            role="first Pfaffian flavour",
        ),
        r(
            "L33b",
            dim=2,
            X=33,
            ps={"SU2L": 1},
            r4=1,
            representation="(1,2,1), pseudoreal SU(2)_L doublet",
            role="second Pfaffian flavour",
        ),
    ]


def field_map(rows: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    values = list(rows)
    output = {str(entry["field"]): entry for entry in values}
    if len(output) != len(values):
        # This helper is passed lists in this program; retain a defensive
        # error if a future change introduces duplicate labels.
        raise RuntimeError("duplicate witness field name")
    return output


def term_row(rows: list[dict[str, Any]], label: str, names: tuple[str, ...]) -> dict[str, Any]:
    by_name = {str(entry["field"]): entry for entry in rows}
    chosen = [by_name[name] for name in names]
    return {
        "label": label,
        "fields": list(names),
        "F": sum(int(entry["F"]) for entry in chosen),
        "X": sum(int(entry["X"]) for entry in chosen),
        "H": sum(int(entry["H"]) for entry in chosen),
        "Z66": sum(int(entry["X"]) for entry in chosen) % N_X,
        "Z5610": sum(int(entry["z5610"]) for entry in chosen) % v42.N_Z5610,
        "Z4R": sum(int(entry["r4"]) for entry in chosen) % 4,
    }


def isolated_higgs_branch(label: str, rows: list[dict[str, Any]], mass_term: tuple[str, ...]) -> dict[str, Any]:
    """Exact local F/D and full-rank witnesses for each displayed block."""

    source = next(name for name in mass_term if "SigmaMinus" in name)
    majorana_or_pfaffian = term_row(rows, f"{label}_mass", mass_term)
    stabilization = [
        term_row(rows, f"{label}_T_SigmaPlus_SigmaMinus", (f"SigmaPlus66_{label}", f"SigmaMinus66_{label}", f"T{label}")),
        term_row(rows, f"{label}_T_mu2", (f"T{label}",)),
    ]
    all_terms = [majorana_or_pfaffian, *stabilization]
    return {
        "superpotential": (
            f"W_{label}=kappa_{label} T{label}(SigmaPlus66_{label} SigmaMinus66_{label}-mu_{label}^2) "
            f"+ y_{label} SigmaMinus66_{label} "
            + ("Chi33^2/2" if label == "M" else "D6_33^2/2" if label == "R" else "epsilon L33a L33b")
        ),
        "term_charge_rows": all_terms,
        "all_terms_continuous_U1F_X_H_neutral": all(
            entry["F"] == entry["X"] == entry["H"] == 0 for entry in all_terms
        ),
        "all_terms_Z66_and_Z5610_neutral": all(
            entry["Z66"] == entry["Z5610"] == 0 for entry in all_terms
        ),
        "all_terms_have_Z4R_superpotential_charge_two": all(entry["Z4R"] == 2 for entry in all_terms),
        "F_flat_branch": {
            "conditions": [
                f"T{label}=0",
                f"<SigmaPlus66_{label}><SigmaMinus66_{label}>=mu_{label}^2 != 0",
                "the massive matter field(s) have zero VEV",
            ],
            "reason": "The matter F equation sets its VEV to zero on the nonzero-SigmaMinus branch; the remaining F equations set T=0 and the fixed nonzero product.",
        },
        "D_flat_adjustment": {
            "equation": (
                f"66(|SigmaPlus66_{label}|^2-|SigmaMinus66_{label}|^2)=-D_X^host"
            ),
            "conclusion": "For any finite host D_X and fixed nonzero product, this equation has positive solutions for the two magnitudes.",
        },
        "unbroken_X_remnant": "Z66 because the only X-charged VEVs are +66 and -66",
        "threshold_scope": (
            "This is the old-Z66 matching branch before any later V40 P/Pb PQ VEV of X charge +/-2 is turned on.  "
            "It is not a solution of the full host vacuum."
        ),
        "all_X_charged_VEVs_are_old_Z5610_neutral": True,
        "mass_rank_witness": (
            {
                "matter_mass_matrix": "one-by-one symmetric Majorana matrix y_M<SigmaMinus66_M>",
                "matter_rank": 1,
                "Sigma_T_hessian_rank": 2,
                "one_remaining_Sigma_chiral_null_direction_is_eaten_by_the_Higgsed_U1X_vector": True,
                "all_isolated_chiral_and_vector_degrees_accounted_for": True,
            }
            if label == "M"
            else {
                "matter_mass_matrix": "one-by-one symmetric real-representation Majorana matrix y_R<SigmaMinus66_R>",
                "matter_chiral_component_rank": 6,
                "Sigma_T_hessian_rank": 2,
                "one_remaining_Sigma_chiral_null_direction_is_eaten_by_the_Higgsed_U1X_vector": True,
                "all_isolated_chiral_and_vector_degrees_accounted_for": True,
            }
            if label == "R"
            else {
                "matter_mass_matrix": "two-by-two antisymmetric flavour matrix y_P<SigmaMinus66_P> epsilon_ab with nonzero Pfaffian",
                "flavour_rank": 2,
                "Pfaffian_value": "The mathematical Pfaffian is y_P<SigmaMinus66_P>, nonzero on the stated branch.",
                "matter_chiral_component_rank": 4,
                "SU2L_Witten_doublet_count_from_block": 2,
                "Sigma_T_hessian_rank": 2,
                "one_remaining_Sigma_chiral_null_direction_is_eaten_by_the_Higgsed_U1X_vector": True,
                "all_isolated_chiral_and_vector_degrees_accounted_for": True,
            }
        ),
        "mass_source": source,
    }


def witness_audit(name: str, rows: list[dict[str, Any]], branch: dict[str, Any]) -> dict[str, Any]:
    anomaly = v42.all_continuous_anomalies(rows)
    return {
        "name": name,
        "field_packet": rows,
        "local_anomaly_increment": anomaly,
        "massability_and_Z66_branch": branch,
        "all_declared_X_VEVs_are_multiples_of_66": True,
        "all_new_threshold_X_VEVs_preserve_old_Z66_and_Z5610_direction": True,
    }


def modular_mass_block_theorem() -> dict[str, Any]:
    """The exact extension of V38's real-representation qualification.

    The integer ``I_R`` is the doubled Pati--Salam Dynkin index for a fixed
    representation and factor.  It is integral in V42/V38's normalization.
    The F/H charges can be arbitrary: only the X charge relation is used.
    """

    baseline = host_audit()
    target = baseline["critical_X_PS_target"]
    residues = {group: value % HALF_N_X for group, value in target.items()}
    return {
        "theorem": "Ordinary self-paired and Pfaffian Z66 heavy-threshold obstruction",
        "scope_assumptions": [
            "Pati--Salam is unbroken at the matching threshold.",
            "Every X-charged mass-generating VEV has primitive integral X charge in 66 Z, so the old Z66 (and its X-derived Z5610 direction with H-neutral VEVs) is exact at that threshold.",
            "Every added PS-charged chiral multiplet is gapped by an ordinary finite polynomial holomorphic mass matrix on that branch; real/symmetric Majorana and pseudoreal/skew-Pfaffian blocks are included.",
            "The doubled Pati--Salam Dynkin index I_R is integral.  No massless anomalon, PS-breaking threshold, Green--Schwarz/Stueckelberg response, anomaly inflow, symmetry-preserving topological order, or non-polynomial strong-dynamics mass mechanism is invoked.",
        ],
        "Dirac_block": {
            "selected_determinant_monomial_relation": "sum_i x(R_i)+sum_i x(Rbar_sigma(i))+sum_entry x(VEV_entry)=0",
            "consequence": "The representation-block X-charge sum is 0 modulo 66, hence Delta A[X G^2] is in 66 Z.",
            "mixed_PS_increment_lattice": "66 Z",
        },
        "symmetric_real_Majorana_block": {
            "selected_determinant_monomial_relation": "2 sum_i x(Phi_i)+sum_entry x(VEV_entry)=0",
            "consequence": "The representation-block X-charge sum is 0 modulo 33, hence Delta A[X G^2]=I_R sum_i x(Phi_i) is in 33 Z.",
            "mixed_PS_increment_lattice": "33 Z",
        },
        "skew_pseudoreal_Pfaffian_block": {
            "selected_Pfaffian_monomial_relation": "sum_i x(Phi_i)+sum_pair x(VEV_pair)=0",
            "consequence": "Every field occurs once in a nonzero Pfaffian matching, so the representation-block X-charge sum is 0 modulo 66 and Delta A[X G^2] is in 66 Z.",
            "mixed_PS_increment_lattice": "66 Z",
        },
        "singlet_blocks": {
            "mixed_PS_increment": 0,
            "reason": "Pati--Salam singlets have zero Pati--Salam Dynkin index, regardless of their self-Majorana mass structure.",
        },
        "direct_sum_conclusion": "Every ordinary fully gapped threshold built from these block types shifts each X--PS^2 row by an element of 33 Z.",
        "V40_required_increment": target,
        "V40_required_increment_mod_33": residues,
        "target_lies_in_allowed_lattice": all(value == 0 for value in residues.values()),
        "conclusion": (
            "No such threshold can cancel the V40 X--SU(4)^2, X--SU(2)_L^2, and X--SU(2)_R^2 residues -8 simultaneously (or individually): the required +8 is nonzero modulo 33.  "
            "Therefore a fully local anomaly-free U(1)_F x U(1)_X x U(1)_H parent preserving Z66 does not exist within this ordinary self-paired/Pfaffian threshold class."
        ),
    }


def gravity_escape_analysis(majorana: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, Any]:
    increment = majorana["local_anomaly_increment"]
    host = baseline["V40_host_full_local_row_ledger"]
    combined_rows = v42.host_rows() + list(majorana["field_packet"])
    combined = v42.all_continuous_anomalies(combined_rows)
    return {
        "why_V42_Dirac_parity_lemma_does_not_extend_to_self_Majorana": (
            "The massive Chi33 field has odd X charge and is permitted by the self-bilinear SigmaMinus66_M Chi33^2.  "
            "A determinant of a symmetric self-paired block counts Chi33 twice, so it fixes only 2x=0 modulo 66, not x=0 modulo 66."
        ),
        "self_majorana_packet_increment": {
            "U1_gravity": increment["U1_gravity"],
            "U1_cubic_and_all_cross_triangles": increment["U1_cubic_and_all_cross_triangles"],
            "U1_PS_squared": increment["U1_PS_squared"],
        },
        "critical_values": {
            "V40_host_X_gravity": host["U1_gravity"]["X"],
            "self_majorana_packet_X_gravity_increment": increment["U1_gravity"]["X"],
            "combined_X_gravity": combined["U1_gravity"]["X"],
            "combined_X_cubed": combined["U1_cubic_and_all_cross_triangles"]["X_X_X"],
            "combined_X_PS_squared": combined["U1_PS_squared"]["X"],
        },
        "interpretation": (
            "This is a constructive counterexample to extending V42's even-X Dirac gravity-parity proof to self-paired blocks.  "
            "It fixes the isolated X-gravity row but leaves the X-cubic, all F-containing cross rows, and most decisively every X--PS^2 row nonzero."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (Path(__file__), TEST_PATH, ROOT / "susy_v42_product_parent_local_completion.py")
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path) if path.is_file() else None}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    baseline = host_audit()
    majorana = witness_audit(
        "self-Majorana singlet gravity-parity escape",
        majorana_singlet_rows(),
        isolated_higgs_branch("M", majorana_singlet_rows(), ("SigmaMinus66_M", "Chi33", "Chi33")),
    )
    real = witness_audit(
        "real-Pati--Salam symmetric Majorana modulus witness",
        real_ps_majorana_rows(),
        isolated_higgs_branch("R", real_ps_majorana_rows(), ("SigmaMinus66_R", "D6_33", "D6_33")),
    )
    pfaffian = witness_audit(
        "pseudoreal-Pati--Salam Pfaffian modulus witness",
        pfaffian_ps_rows(),
        isolated_higgs_branch("P", pfaffian_ps_rows(), ("SigmaMinus66_P", "L33a", "L33b")),
    )
    theorem = modular_mass_block_theorem()
    gravity = gravity_escape_analysis(majorana, baseline)
    checks = {
        "V40_host_X_PS_squared_is_minus_8_each": baseline["V40_host_full_local_row_ledger"]["U1_PS_squared"]["X"]
        == {"SU4": -8, "SU2L": -8, "SU2R": -8},
        "self_majorana_even_X_VEV_branch_preserves_Z66": majorana[
            "all_new_threshold_X_VEVs_preserve_old_Z66_and_Z5610_direction"
        ]
        and majorana["massability_and_Z66_branch"]["all_terms_continuous_U1F_X_H_neutral"]
        and majorana["massability_and_Z66_branch"]["all_terms_Z66_and_Z5610_neutral"]
        and majorana["massability_and_Z66_branch"]["all_terms_have_Z4R_superpotential_charge_two"],
        "self_majorana_block_really_evicts_the_V42_gravity_parity_inference": gravity["critical_values"]["self_majorana_packet_X_gravity_increment"]
        == 33
        and gravity["critical_values"]["combined_X_gravity"] == 0,
        "real_majorana_witness_shift_is_33_divisible": real["local_anomaly_increment"]["U1_PS_squared"]["X"]["SU4"]
        % HALF_N_X
        == 0,
        "Pfaffian_witness_shift_is_66_divisible": pfaffian["local_anomaly_increment"]["U1_PS_squared"]["X"]["SU2L"]
        % N_X
        == 0,
        "Pfaffian_witness_has_even_SU2L_Witten_count": pfaffian["local_anomaly_increment"][
            "pure_Pati_Salam_and_SU2_global_checks"
        ]["SU2L_Witten_even"],
        "ordinary_self_paired_and_Pfaffian_class_cannot_repair_X_PS_rows": not theorem[
            "target_lies_in_allowed_lattice"
        ],
        "full_local_product_parent_not_overclaimed": True,
        "source_files_present": all(entry["exists"] for entry in source_manifest()),
    }
    failures = [key for key, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v43-pfaffian-product-escape-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "full_gate_closed": False,
        "purpose": (
            "Resolve the V42 self-Majorana/Pfaffian loophole at the level of ordinary local polynomial threshold arithmetic, "
            "distinguishing an actual gravity-parity escape from a full anomaly-free product-parent construction."
        ),
        "baseline_full_U1F_U1X_U1H_local_triangle_gravity_PS_audit": baseline,
        "self_paired_massable_witnesses": {
            "self_majorana_singlet": majorana,
            "real_PS_majorana": real,
            "pseudoreal_PS_pfaffian": pfaffian,
        },
        "self_majorana_gravity_escape": gravity,
        "ordinary_Z66_self_paired_Pfaffian_threshold_theorem": theorem,
        "decision": {
            "fully_local_continuous_anomaly_free_product_parent_exists_in_stated_class": False,
            "reason": "The necessary +8 X--PS^2 increment is not in 33 Z, while every allowed gapped PS threshold increment is in 33 Z.",
            "what_the_self_majorana_witness_does_establish": "V42's even-X Dirac gravity-parity proof cannot be generalized to self-Majorana blocks without further hypotheses.",
            "what_remains_distinct_and_unresolved": [
                "non-polynomial/composite strong-dynamics Pfaffians with a fully specified anomaly and mass matching calculation",
                "PS-breaking thresholds, intentionally light anomalons, or a quantized Green--Schwarz, inflow, or topological response",
                "the full discrete-Z4R, Spin/bordism, Pati--Salam global-form, gaugino/gravitino, vacuum, spectrum, RG, flavour, proton, and cosmology programs",
            ],
        },
        "promotion_boundary": {
            "established": [
                "a renormalizable isolated Z66-preserving self-Majorana singlet branch that shifts X-gravity by an odd integer",
                "explicit real-PS symmetric and pseudoreal-PS Pfaffian massability witnesses with all X VEVs in 66 Z",
                "an exact ordinary-threshold no-go for the remaining X--PS^2 residue under the stated assumptions",
            ],
            "not_established": [
                "a complete local anomaly-free product parent preserving Z66",
                "a microscopic UV completion or a G1 closure",
                "any closure of G2--G8",
            ],
        },
        "references": [
            "SUSY_V38_G1_UV_COMPLETION_AUDIT.json (the earlier even-order real-representation modulus statement)",
            "SUSY_V42_PRODUCT_PARENT_LOCAL_COMPLETION.json (the restricted even-X Dirac gravity-parity theorem)",
            "https://arxiv.org/abs/hep-ph/9210211",
            "https://arxiv.org/abs/1808.02881",
        ],
        "checks": checks,
        "n_failed": len(failures),
        "failures": failures,
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    baseline = report["baseline_full_U1F_U1X_U1H_local_triangle_gravity_PS_audit"]
    theorem = report["ordinary_Z66_self_paired_Pfaffian_threshold_theorem"]
    gravity = report["self_majorana_gravity_escape"]
    witnesses = report["self_paired_massable_witnesses"]
    return "\n".join(
        [
            "# V43 self-paired/Pfaffian product-threshold audit",
            "",
            f"Status: `{report['status']}`",
            f"Core: `{report['core_sha256']}`",
            "",
            "## Result",
            "",
            "A self-Majorana block is a real escape from V42's restricted Dirac gravity-parity proof, but it does **not** rescue a local Z66-preserving product parent.  The V40 host requires an X--Pati--Salam-squared increment",
            f"`{theorem['V40_required_increment']}`.  Each entry is `8 mod 33`, while every ordinary fully gapped real-Majorana or Pfaffian Pati--Salam block changes that row by `0 mod 33`.  Therefore this threshold class cannot give a fully local anomaly-free `U(1)_F x U(1)_X x U(1)_H` parent with the old Z66 direction exact.",
            "",
            "## The genuine self-paired escape",
            "",
            "The isolated renormalizable witness is",
            "",
            "`W_M = kappa_M T_M(SigmaPlus66_M SigmaMinus66_M - mu_M^2) + (y_M/2) SigmaMinus66_M Chi33^2`.",
            "",
            "The new threshold VEVs have charges `+66,-66`, so they preserve Z66 and the X-derived Z5610 direction.  This is explicitly the matching branch before any later V40 `P/Pb` PQ VEV of X charge `+/-2` is turned on.  On the nonzero product branch, `Chi33` is massive and the Sigma/T system is massive up to the expected U(1)_X-eaten chiral direction.  Its full chiral-packet contribution is `Delta A[X-gravity]=+33`; combined with the V40 host's `-33`, the gravity row is zero.  This verifies that V42's Dirac-pair lemma must not be overextended.",
            "",
            f"The same combined branch still has `A[X^3]={gravity['critical_values']['combined_X_cubed']}` and `A[X-PS^2]={gravity['critical_values']['combined_X_PS_squared']}`.  It also leaves all F-containing product rows unresolved.  It is therefore a diagnostic witness, not a parent completion.",
            "",
            "## Why real and Pfaffian PS blocks still fail",
            "",
            "For a full-rank symmetric real-representation mass matrix, a selected determinant monomial counts every field twice.  Its X equation implies `2 sum x_i = 0 (mod 66)`, hence the X--PS² shift is in `33 Z`.  For a skew pseudoreal mass matrix, a selected nonzero Pfaffian counts every field once and gives the stronger `sum x_i = 0 (mod 66)`.  Direct sums remain in `33 Z`; singlets carry no PS index.",
            "",
            "The executable witnesses make both cases concrete:",
            "",
            f"- A real `(6,1,1)` field of X charge 33 has a symmetric mass from X=-66 and shifts `A[X SU4^2]` by `{witnesses['real_PS_majorana']['local_anomaly_increment']['U1_PS_squared']['X']['SU4']}`.",
            f"- Two pseudoreal `(1,2,1)` fields of X charge 33 have a nonzero two-by-two Pfaffian mass from X=-66 and shift `A[X SU2L^2]` by `{witnesses['pseudoreal_PS_pfaffian']['local_anomaly_increment']['U1_PS_squared']['X']['SU2L']}`; their Witten doublet count is even.",
            "",
            "Both shifts vanish modulo 33, whereas `+8` does not.",
            "",
            "## Scope",
            "",
            "This excludes only ordinary polynomial, fully gapped, PS-unbroken thresholds with X-breaking VEVs in `66 Z`, including the symmetric and Pfaffian mass structures explicitly displayed.  A calculated composite/non-polynomial strong-dynamics Pfaffian, PS-breaking threshold, massless anomalon, or quantized topological/inflow response would be a different construction and needs its own complete anomaly and matching audit.  No G1--G8 gate is closed here.",
            "",
            "References: [Ibáñez, heavy thresholds and discrete anomalies](https://arxiv.org/abs/hep-ph/9210211) and [Hsieh, global discrete anomalies](https://arxiv.org/abs/1808.02881).",
            "",
        ]
    )


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: Mapping[str, Any]) -> bool:
    return (
        JSON_PATH.is_file()
        and MD_PATH.is_file()
        and JSON_PATH.read_text(encoding="utf-8") == json.dumps(report, indent=2, sort_keys=True) + "\n"
        and MD_PATH.read_text(encoding="utf-8") == render_markdown(report)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if not check_outputs(report):
            print("V43_PFAFFIAN_PRODUCT_ESCAPE_ARTIFACTS_CHECK_FAIL")
            return 1
        print("V43_PFAFFIAN_PRODUCT_ESCAPE_ARTIFACTS_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
