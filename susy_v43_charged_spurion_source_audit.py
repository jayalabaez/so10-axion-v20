#!/usr/bin/env python3
"""Fail-closed V43 audit of the minimal charged-spurion source escape.

V42 proved that an extra additive label cannot distinguish ``STheta`` from
the V40 host drivers while *all* three retain naked linear terms.  This file
tests the smallest honest evasion: replace the STheta tadpole by a mass
mixing with a charged chiral spurion Omega, while leaving the X/Zp host
tadpoles naked.

The result is deliberately two-sided:

* at the renormalizable F-term level the new U(1)_S label does separate the
  source from X/Zp, and a formal coupled F-flat branch exists over any
  F-flat host solution; but
* the minimal gauged realization has no zero-FI D-flat branch, its new
  U(1)_S anomaly rows are nonzero, and the obvious neutral compensator
  reintroduces a generic X/Zp portal.

Thus this is a precise design boundary, not a completed replacement theory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import susy_v40_all_ring_selector as v40


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V43_CHARGED_SPURION_SOURCE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V43_CHARGED_SPURION_SOURCE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v43_charged_spurion_source_audit.py"

STATUS = (
    "V43_CHARGED_SPURION_F_TERM_SOURCE_SEPARATION_CERTIFIED__"
    "MINIMAL_GAUGED_D_FLAT_AND_ANOMALY_COMPLETION_NO_GO_CERTIFIED__"
    "NO_FULL_GATE_CLOSED"
)

ORDER_F = 9
PS_GROUPS = ("SU4", "SU2L", "SU2R")


# ``u1s`` is a new proposed additive/gauge factor.  All pre-existing V40
# host fields are U(1)_S-neutral.  The nonzero assignments on the V41
# anomalons are the smallest bookkeeping reassignment that keeps their
# original Theta-mediated mass terms allowed after q_S(ThetaMinus)=-1.
U1S_CHARGES: dict[str, int] = {
    "STheta": 1,
    "ThetaPlus": 0,
    "ThetaMinus": -1,
    "L0": 0,
    "Lminus9": 0,
    "R0": 1,
    "Rplus9": 0,
    "E4": 1,
    "E5": 0,
    "E3": 1,
    "E6": 0,
    "Eminus2": 0,
    "Eminus7": 0,
    "Omega": -1,
}


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields() -> dict[str, dict[str, Any]]:
    """The V40 table plus the charged, U(1)_F-neutral spurion Omega."""

    result = {name: dict(row) | {"u1s": U1S_CHARGES.get(name, 0)} for name, row in v40.FIELDS.items()}
    result["Omega"] = {
        "dim": 1,
        "u1f": 0,
        "u1s": -1,
        "z5610": 0,
        "r4": 0,
        "pq": 0,
        "ps": {},
        "role": "charged dynamical linear-term spurion",
    }
    return result


FIELDS = fields()
SOURCE_VEV_FIELDS = ("ThetaPlus", "ThetaMinus", "Omega")
SOURCE_FIELDS = ("STheta",) + SOURCE_VEV_FIELDS
HOST_DRIVER_FIELDS = ("X", "Zp")
HOST_CORE_FIELDS = tuple(v40.VISIBLE_FIELDS)


# The old naked STheta term is intentionally removed.  Every other V40 term,
# including the original Theta-dependent anomalon masses, is retained.
RETAINED_V40_TERMS = tuple(
    item for item in v40.RENORMALIZABLE_TERMS if item[0] != "STheta_linear"
)
NEW_TERMS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "STheta_Omega_mass_mixing",
        ("STheta", "Omega"),
        "M_Omega STheta Omega",
    ),
)


def charge(names: Iterable[str], key: str, modulus: int | None = None) -> int:
    total = sum(int(FIELDS[name][key]) for name in names)
    return total if modulus is None else total % modulus


def old_product_allowed(names: Iterable[str]) -> bool:
    return (
        charge(names, "u1f") == 0
        and charge(names, "z5610", 5610) == 0
        and charge(names, "pq") == 0
        and charge(names, "r4", 4) == 2
    )


def u1s_term_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for label, names in RETAINED_V40_TERMS:
        rows.append({
            "origin": "retained_V40",
            "label": label,
            "fields": list(names),
            "U1F": charge(names, "u1f"),
            "U1S": charge(names, "u1s"),
            "Z4R": charge(names, "r4", 4),
            "Z5610": charge(names, "z5610", 5610),
            "PQ_numerator_over_170": charge(names, "pq"),
            "allowed": old_product_allowed(names) and charge(names, "u1s") == 0,
        })
    for label, names, expression in NEW_TERMS:
        rows.append({
            "origin": "new_V43",
            "label": label,
            "expression": expression,
            "fields": list(names),
            "U1F": charge(names, "u1f"),
            "U1S": charge(names, "u1s"),
            "Z4R": charge(names, "r4", 4),
            "Z5610": charge(names, "z5610", 5610),
            "PQ_numerator_over_170": charge(names, "pq"),
            "allowed": old_product_allowed(names) and charge(names, "u1s") == 0,
        })
    return {
        "source_redesign": {
            "removed_term": "-kappa mu_F^2 STheta",
            "replacement": "M_Omega STheta Omega",
            "renormalizable_source_piece": (
                "W_source = kappa STheta ThetaPlus ThetaMinus + "
                "M_Omega STheta Omega + W_Theta_anomalon_mass"
            ),
            "why_V42_neutral_parameter_premise_no_longer_holds": (
                "The coefficient of the effective STheta linear term is M_Omega<Omega>, "
                "and Omega has U(1)_S charge -1 rather than being a neutral numerical parameter."
            ),
        },
        "rows": rows,
        "retained_V40_term_count": len(RETAINED_V40_TERMS),
        "all_retained_and_new_terms_allowed": all(row["allowed"] for row in rows),
        "all_original_U1F_Z4R_Z5610_PQ_checks_remain_true": all(
            row["U1F"] == 0
            and row["Z4R"] == 2
            and row["Z5610"] == 0
            and row["PQ_numerator_over_170"] == 0
            for row in rows
        ),
    }


def source_host_cubic_superset() -> dict[str, Any]:
    """Exhaust the abelian-invariant degree<=3 monomial superset.

    Gauge contractions can only remove rows from this list.  Thus absence of
    an abelian-invariant source--host row is a stronger statement than a
    PS-specific cubic scan.  The scan includes the whole V40 visible host
    core (not just X/Zp) plus the four redesigned source fields.
    """

    candidates = HOST_CORE_FIELDS + SOURCE_FIELDS
    allowed: list[dict[str, Any]] = []
    mixed: list[dict[str, Any]] = []
    ps_excluded_mixed: list[dict[str, Any]] = []
    potential_mixed: list[dict[str, Any]] = []
    direct_driver: list[dict[str, Any]] = []
    for degree in range(1, 4):
        for combo in itertools.combinations_with_replacement(candidates, degree):
            if not (
                charge(combo, "u1f") == 0
                and charge(combo, "u1s") == 0
                and charge(combo, "r4", 4) == 2
                and charge(combo, "z5610", 5610) == 0
                and charge(combo, "pq") == 0
            ):
                continue
            row = {
                "degree": degree,
                "fields": list(combo),
                "U1F": 0,
                "U1S": 0,
                "Z4R": 2,
                "Z5610": 0,
                "PQ_numerator_over_170": 0,
            }
            allowed.append(row)
            contains_source = any(name in SOURCE_FIELDS for name in combo)
            contains_host = any(name in HOST_CORE_FIELDS for name in combo)
            if contains_source and contains_host:
                mixed.append(row)
                # Every V43 source field is PS-singlet. A monomial with one
                # non-singlet V40 host factor cannot be a PS invariant.
                nonsinglet_host = [
                    name for name in combo
                    if name in HOST_CORE_FIELDS and bool(FIELDS[name]["ps"])
                ]
                if len(nonsinglet_host) == 1:
                    ps_excluded_mixed.append(row | {
                        "necessary_PS_filter": "one non-singlet host factor times PS-singlet source factors cannot form a PS invariant",
                    })
                else:
                    potential_mixed.append(row)
            if contains_source and any(name in HOST_DRIVER_FIELDS for name in combo):
                direct_driver.append(row)
    return {
        "method": (
            "All monomials of degree one through three are first filtered only by the declared "
            "abelian factors. A gauge invariant mixed portal would have to survive this superset."
        ),
        "candidate_field_count": len(candidates),
        "abelian_allowed_monomials": allowed,
        "abelian_allowed_source_host_monomials": mixed,
        "source_host_rows_excluded_by_necessary_PS_singlet_filter": ps_excluded_mixed,
        "potentially_PS_invariant_source_host_monomials_after_necessary_filter": potential_mixed,
        "abelian_allowed_X_or_Zp_source_monomials": direct_driver,
        "no_renormalizable_source_host_portal_after_necessary_PS_filter": not potential_mixed,
        "no_renormalizable_X_Zp_source_portal_in_abelian_superset": not direct_driver,
        "important_limit": (
            "This is a complete renormalizable abelian scan plus a necessary PS-singlet filter. It is not a classification of arbitrary "
            "higher-dimensional operators involving charged V40 host fields."
        ),
    }


def all_order_driver_source_ring() -> dict[str, Any]:
    """Prove the restricted all-order source-driver statement.

    A monomial built only from one X/Zp driver and STheta, ThetaPlus,
    ThetaMinus, Omega has U(1)_F neutrality only when the two Theta powers
    agree.  U(1)_S neutrality then forces an STheta insertion whenever any
    branch-VEV source field is inserted.  It consequently vanishes on the
    F-flat STheta=0 branch.
    """

    examples: list[dict[str, int | bool]] = []
    counterexamples: list[dict[str, int]] = []
    for n_theta_pair in range(0, 9):
        for n_omega in range(0, 9):
            for n_stheta in range(0, 18):
                u1s = n_stheta - n_theta_pair - n_omega
                z4r = (2 + 2 * n_stheta) % 4
                allowed = u1s == 0 and z4r == 2
                if allowed:
                    row = {
                        "theta_plus_and_minus_power_each": n_theta_pair,
                        "omega_power": n_omega,
                        "STheta_power": n_stheta,
                        "allowed": True,
                        "vanishes_when_STheta_zero": n_stheta > 0,
                    }
                    examples.append(row)
                    if (n_theta_pair > 0 or n_omega > 0) and n_stheta == 0:
                        counterexamples.append({
                            "theta_pair": n_theta_pair,
                            "omega": n_omega,
                            "STheta": n_stheta,
                        })
    return {
        "restricted_ring": "{X or Zp} times C[STheta,ThetaPlus,ThetaMinus,Omega]",
        "derivation": [
            "U(1)_F neutrality gives n(ThetaPlus)=n(ThetaMinus)=n.",
            "U(1)_S neutrality gives n(STheta)-n-n(Omega)=0.",
            "Z4R requires 2+2 n(STheta) = 2 mod 4, so n(STheta) is even.",
            "If STheta=0 on the F branch, U(1)_S neutrality forces n=n(Omega)=0.",
        ],
        "conclusion": (
            "No polynomial X/Zp portal made only from source-branch VEV fields survives on "
            "the STheta=0 branch. Any allowed nontrivial restricted-ring portal contains STheta."
        ),
        "finite_exhaustive_crosscheck_bounds": {
            "theta_pair_power": [0, 8],
            "omega_power": [0, 8],
            "STheta_power": [0, 17],
            "allowed_examples": examples,
            "counterexamples": counterexamples,
        },
        "all_checked_nontrivial_portals_vanish_on_F_branch": not counterexamples,
        "scope_limit": (
            "The theorem deliberately excludes arbitrary additional V40 host fields; those require a "
            "separate higher-dimensional PS/operator-ring audit before any proton or full-vacuum claim."
        ),
    }


def coupled_f_term_audit() -> dict[str, Any]:
    return {
        "declared_full_renormalizable_form": (
            "W = W_host(V40 fields) + kappa STheta ThetaPlus ThetaMinus + "
            "M_Omega STheta Omega + W_Theta_anomalon_mass"
        ),
        "why_this_is_a_coupled_audit": (
            "The cubic scan has no potentially PS-invariant source--host term after its necessary "
            "PS-singlet filter, so at renormalizable order the displayed source F equations and "
            "the arbitrary F-flat host equations are simultaneously valid."
        ),
        "source_F_equations_at_zero_anomalon_VEVs": {
            "F_STheta": "kappa ThetaPlus ThetaMinus + M_Omega Omega",
            "F_ThetaPlus": "kappa STheta ThetaMinus",
            "F_ThetaMinus": "kappa STheta ThetaPlus",
            "F_Omega": "M_Omega STheta",
            "F_anomalons": "ThetaPlus or ThetaMinus times its declared full-rank V41 mass matrix times the partner",
            "F_X": "partial_X W_host",
            "F_Zp": "partial_Zp W_host",
            "F_other_host": "partial_other_host W_host",
        },
        "formal_branch": {
            "STheta": 0,
            "ThetaPlus_times_ThetaMinus": "-(M_Omega/kappa) Omega != 0",
            "Omega": "-(kappa/M_Omega) ThetaPlus ThetaMinus != 0",
            "all_anomalons": 0,
            "host_requirement": "all partial W_host = 0 on the chosen host branch",
            "all_source_F_terms_zero": True,
            "all_host_F_terms_zero_given_an_F_flat_host_solution": True,
            "renormalizable_product_branch_is_F_flat": True,
        },
        "anomalon_mass_witness_preserved": {
            "ThetaPlus_masses": ["four L0/Lminus9 pairs", "Eminus2/Eminus7 pair"],
            "ThetaMinus_masses": ["four R0/Rplus9 pairs", "E4/E5 pair", "E3/E6 pair"],
            "rank_witness": "lambdaL=lambdaR=I_4; all singlet couplings nonzero",
            "all_original_V41_anomalons_massable_when_ThetaPlus_and_ThetaMinus_are_nonzero": True,
        },
        "does_not_establish": [
            "a zero-FI D-flat gauged branch",
            "an anomaly-free U(1)_S parent",
            "a full Kahler/soft vacuum or a higher-dimensional source-host operator proof",
        ],
    }


def minimal_d_and_residual_audit() -> dict[str, Any]:
    return {
        "minimal_gauged_field_charge_matrix": {
            "STheta": {"U1F": 0, "U1S": 1, "Z4R": 2},
            "ThetaPlus": {"U1F": 9, "U1S": 0, "Z4R": 0},
            "ThetaMinus": {"U1F": -9, "U1S": -1, "Z4R": 0},
            "Omega": {"U1F": 0, "U1S": -1, "Z4R": 0},
        },
        "zero_FI_D_terms": {
            "D_F_over_gF": "9(|ThetaPlus|^2-|ThetaMinus|^2)",
            "D_S_over_gS": "|STheta|^2-|ThetaMinus|^2-|Omega|^2",
            "on_nonzero_F_branch": [
                "|ThetaPlus|^2=|ThetaMinus|^2=v^2 from D_F=0.",
                "STheta=0 and Omega!=0 from F_Omega=F_STheta=0.",
                "D_S/gS = -v^2-|Omega|^2 < 0.",
            ],
            "zero_FI_D_flat_branch_exists": False,
            "proof": (
                "The two nonzero U(1)_S-negative F-branch VEV contributions cannot be balanced in "
                "the minimal field set, independent of couplings or of the individual Theta phases."
            ),
        },
        "conditional_FI_escape": {
            "assumption": "A positive constant xi_S is inserted into D_S/gS = |STheta|^2-|ThetaMinus|^2-|Omega|^2+xi_S.",
            "equation_on_F_branch": "alpha x^2+x-xi_S=0, with x=|ThetaPlus|^2=|ThetaMinus|^2 and alpha=|kappa/M_Omega|^2.",
            "positive_solution": "x=(-1+sqrt(1+4 alpha xi_S))/(2 alpha) for xi_S>0.",
            "formal_F_and_D_flat_solution_exists": True,
            "U1F_nonzero_VEV_charges": [9, -9],
            "Omega_U1F_charge": 0,
            "unbroken_U1F_subgroup": "Z9",
            "why_not_a_completion": (
                "A constant FI datum and the anomaly/UV completion of U(1)_S are additional physics. "
                "They are not supplied by this minimal spurion Lagrangian."
            ),
        },
    }


def u1s_anomaly_audit() -> dict[str, Any]:
    rows = FIELDS.values()
    mixed_ps = {
        group: sum(int(row["u1s"]) * int(row["ps"].get(group, 0)) for row in rows)
        for group in PS_GROUPS
    }
    # Recreate the iterator because it was consumed only conceptually above;
    # FIELDS.values() is re-iterable, but spelling it this way keeps the
    # formulae obvious in the emitted certificate.
    return {
        "convention": "PS rows use the V40 doubled-Dynkin coefficients; abelian gravity/cubic rows use physical Weyl-component multiplicities.",
        "new_U1S_rows": {
            "PS_squared_U1S": mixed_ps,
            "gravity_U1S": sum(int(row["dim"]) * int(row["u1s"]) for row in FIELDS.values()),
            "U1S_cubed": sum(int(row["dim"]) * int(row["u1s"]) ** 3 for row in FIELDS.values()),
            "U1F_squared_U1S": sum(int(row["dim"]) * int(row["u1f"]) ** 2 * int(row["u1s"]) for row in FIELDS.values()),
            "U1F_U1S_squared": sum(int(row["dim"]) * int(row["u1f"]) * int(row["u1s"]) ** 2 for row in FIELDS.values()),
        },
        "unchanged_U1F_only_check": v40.u1f_anomaly_audit(),
        "all_new_U1S_local_rows_cancel": False,
        "conclusion": (
            "The U(1)_S label cannot yet be promoted to a completed gauge symmetry. Any spectator or "
            "Green--Schwarz repair must be added explicitly, massed, and re-audited for source-host portals."
        ),
    }


def neutral_compensator_recurrence() -> dict[str, Any]:
    """Show why the most obvious no-FI repair is not protected."""

    omega_bar = {"U1F": 0, "U1S": 1, "Z4R": 0, "Z5610": 0, "PQ": 0}
    return {
        "attempt": (
            "Add a U(1)_F-neutral, U(1)_S=+1, Z4R-neutral field OmegaBar whose VEV would cancel the "
            "minimal D_S contribution without an FI term."
        ),
        "OmegaBar": omega_bar,
        "generic_portals": [
            {
                "operator": "X Omega OmegaBar",
                "charges": {"U1F": 0, "U1S": 0, "Z4R": 2, "Z5610": 0, "PQ": 0},
                "allowed": True,
            },
            {
                "operator": "Zp Omega OmegaBar",
                "charges": {"U1F": 0, "U1S": 0, "Z4R": 2, "Z5610": 0, "PQ": 0},
                "allowed": True,
            },
        ],
        "F_term_consequence": {
            "F_X": "partial_X W_host + lambda_X Omega OmegaBar",
            "F_Zp": "partial_Zp W_host + lambda_Z Omega OmegaBar",
            "unperturbed_host_branch_is_F_flat_when_Omega_and_OmegaBar_nonzero": False,
        },
        "minimal_compensator_class_no_go": (
            "If the positive compensator is neutral under U(1)_F and the old selectors and preserves Z4R, "
            "then its product with Omega is neutral under every declared factor. The generic X/Zp portal is "
            "therefore unavoidable. A differently charged or non-minimal compensator is a new model requiring "
            "a fresh F/D, residual-group, anomaly, mass, and operator audit."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (ROOT / "susy_v43_charged_spurion_source_audit.py", TEST_PATH)
    return [
        {
            "path": path.name,
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else None,
        }
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    terms = u1s_term_audit()
    cubic = source_host_cubic_superset()
    ring = all_order_driver_source_ring()
    f_terms = coupled_f_term_audit()
    d_terms = minimal_d_and_residual_audit()
    anomaly = u1s_anomaly_audit()
    recurrence = neutral_compensator_recurrence()
    report: dict[str, Any] = {
        "schema": "susy-v43-charged-spurion-source-audit-v1",
        "status": STATUS,
        "scope": (
            "A minimal charged-spurion attempt to evade the V42 neutral-parameter source-host no-go. "
            "It proves a renormalizable F-term separation and proves the minimal gauged completion is not yet viable."
        ),
        "new_charge_assignments": {
            name: {
                "representation": FIELDS[name].get("role", FIELDS[name].get("ps", {})),
                "U1F": int(FIELDS[name]["u1f"]),
                "U1S": int(FIELDS[name]["u1s"]),
                "Z4R": int(FIELDS[name]["r4"]),
                "Z5610": int(FIELDS[name]["z5610"]),
                "PQ_numerator_over_170": int(FIELDS[name]["pq"]),
            }
            for name in U1S_CHARGES
        },
        "term_audit": terms,
        "renormalizable_source_host_portal_audit": cubic,
        "restricted_all_order_driver_source_ring": ring,
        "full_coupled_F_term_audit": f_terms,
        "minimal_D_and_residual_audit": d_terms,
        "new_U1S_anomaly_audit": anomaly,
        "neutral_compensator_recurrence": recurrence,
        "decision": {
            "V42_neutral_parameter_no_go_is_evaded_at_renormalizable_F_term_level": True,
            "renormalizable_source_host_separation_is_symmetry_protected": cubic["no_renormalizable_source_host_portal_after_necessary_PS_filter"],
            "formal_F_flat_source_times_F_flat_host_branch_exists": f_terms["formal_branch"]["renormalizable_product_branch_is_F_flat"],
            "zero_FI_minimal_gauged_D_flat_branch_exists": d_terms["zero_FI_D_terms"]["zero_FI_D_flat_branch_exists"],
            "new_U1S_gauge_parent_completed": anomaly["all_new_U1S_local_rows_cancel"],
            "neutral_one_compensator_no_FI_repair_preserves_separation": False,
            "conditional_FI_branch_is_a_completed_physical_theory": False,
            "full_coupled_PS_PQ_U1F_U1S_vacuum_exists": False,
            "full_gate_closed": [],
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    terms = report["term_audit"]
    cubic = report["renormalizable_source_host_portal_audit"]
    ring = report["restricted_all_order_driver_source_ring"]
    f_terms = report["full_coupled_F_term_audit"]
    d_terms = report["minimal_D_and_residual_audit"]
    anomaly = report["new_U1S_anomaly_audit"]
    recurrence = report["neutral_compensator_recurrence"]
    return f"""# V43 charged-spurion source audit

Status: `{report['status']}`

## What the spurion changes

V42 assumed a neutral numerical `STheta` linear coefficient.  This minimal
redesign instead uses

`W_source = kappa STheta ThetaPlus ThetaMinus + M_Omega STheta Omega`

with `q_S(STheta)=+1`, `q_S(ThetaPlus)=0`,
`q_S(ThetaMinus)=q_S(Omega)=-1`, while `X` and `Zp` remain `U(1)_S` neutral.
The old naked `STheta` term is removed; its effective coefficient is
`M_Omega<Omega>`.  The anomalon charges are reassigned only as needed to keep
their old Theta-mediated masses allowed.  All {terms['retained_V40_term_count']}
retained V40 terms plus the new mixing pass every listed charge check.

The degree-one-to-three abelian-invariant superset contains
`{len(cubic['abelian_allowed_source_host_monomials'])}` source--host rows and
`{len(cubic['abelian_allowed_X_or_Zp_source_monomials'])}` rows involving an
`X/Zp` driver.  The three raw source--host rows each contain exactly one
non-singlet Pati--Salam host factor and are therefore excluded by a necessary
PS-singlet test; the potentially PS-invariant list and the direct `X/Zp` list
are both zero.  This is stronger than a gauge-contraction scan for the
surviving rows, since a gauge invariant portal would first have to be abelian
invariant.

For the restricted all-order ring containing only one `X/Zp` and source
fields, `U(1)_F` requires equal `ThetaPlus/ThetaMinus` powers and `U(1)_S`
then requires `n(STheta)=n(Theta pair)+n(Omega)`.  Thus every nontrivial
allowed portal contains `STheta` and vanishes on the source F branch.  This
does *not* classify arbitrary higher-dimensional operators with V40 host
fields.

## Coupled F equations

With all anomalons at the origin, the source equations are

`F_STheta=kappa ThetaPlus ThetaMinus+M_Omega Omega`,
`F_ThetaPlus=kappa STheta ThetaMinus`,
`F_ThetaMinus=kappa STheta ThetaPlus`, and `F_Omega=M_Omega STheta`.

Therefore `STheta=0` and
`Omega=-(kappa/M_Omega)ThetaPlus ThetaMinus` give zero source F terms.
Because the renormalizable source--host portal scan is empty, every F-flat
host solution can be combined with this formal source branch.  The original
V41 Theta-mediated anomalon mass matrices remain allowed and have their old
full-rank witness.  This is a genuine F-term result, summarized in the audit
as `{f_terms['formal_branch']['renormalizable_product_branch_is_F_flat']}`.

## Why it is not yet a new gauge theory

For a gauged `U(1)_S` and zero FI term, `D_F=0` sets
`|ThetaPlus|^2=|ThetaMinus|^2=v^2`, while the same F branch gives

`D_S/g_S=-v^2-|Omega|^2<0`.

So the minimal gauged field set has no zero-FI D-flat branch.  A positive
constant FI term gives a formal branch with
`x=(-1+sqrt(1+4 alpha xi_S))/(2 alpha)` and retains `Z9` because the nonzero
`U(1)_F` VEV charges are `+9,-9` and `Omega` is neutral.  But that FI datum
and a consistent `U(1)_S` UV completion are extra assumptions.

Indeed the raw new local rows are `{anomaly['new_U1S_rows']}`; they do not
cancel.  This audit does not silently invoke a Green--Schwarz or spectator
repair.

The most obvious no-FI compensator, a neutral `OmegaBar` of `U(1)_S=+1`,
also fails: both `X Omega OmegaBar` and `Zp Omega OmegaBar` are allowed.  They
give `{recurrence['F_term_consequence']['F_X']}` and its `Zp` analogue, so a
nonzero compensator VEV re-sources the host driver equations.

## Verdict

The charged spurion is a real escape from the *F-term algebra* of V42, but
not a completed source theory.  It identifies the required next physics:
an anomaly-free, D-flat, non-neutral-compensator or UV/inflow completion that
retains the portal proof after all new VEVs and higher operators are audited.
No G gate is closed.

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS:
        raise RuntimeError("unexpected V43 status")
    if canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale V43 core hash")
    terms = report["term_audit"]
    if not terms["all_retained_and_new_terms_allowed"]:
        raise RuntimeError("the charged-spurion superpotential violates its charge table")
    cubic = report["renormalizable_source_host_portal_audit"]
    if not cubic["no_renormalizable_source_host_portal_after_necessary_PS_filter"]:
        raise RuntimeError("a potentially PS-invariant source-host cubic portal survived")
    if not cubic["no_renormalizable_X_Zp_source_portal_in_abelian_superset"]:
        raise RuntimeError("an X/Zp source cubic portal survived")
    ring = report["restricted_all_order_driver_source_ring"]
    if ring["finite_exhaustive_crosscheck_bounds"]["counterexamples"]:
        raise RuntimeError("restricted source-driver ring proof has a counterexample")
    f_terms = report["full_coupled_F_term_audit"]
    if not f_terms["formal_branch"]["renormalizable_product_branch_is_F_flat"]:
        raise RuntimeError("formal coupled F branch unexpectedly failed")
    d_terms = report["minimal_D_and_residual_audit"]
    if d_terms["zero_FI_D_terms"]["zero_FI_D_flat_branch_exists"]:
        raise RuntimeError("minimal zero-FI branch must remain a no-go")
    if d_terms["conditional_FI_escape"]["unbroken_U1F_subgroup"] != "Z9":
        raise RuntimeError("conditional FI branch lost the required Z9 remnant")
    anomaly = report["new_U1S_anomaly_audit"]
    if anomaly["all_new_U1S_local_rows_cancel"]:
        raise RuntimeError("unimplemented U1S anomaly repair was silently claimed")
    recurrence = report["neutral_compensator_recurrence"]
    if not all(row["allowed"] for row in recurrence["generic_portals"]):
        raise RuntimeError("neutral compensator recurrence arithmetic is inconsistent")
    decision = report["decision"]
    if decision["zero_FI_minimal_gauged_D_flat_branch_exists"]:
        raise RuntimeError("decision contradicts D-term no-go")
    if decision["new_U1S_gauge_parent_completed"]:
        raise RuntimeError("decision silently promotes an anomalous parent")
    if decision["full_gate_closed"]:
        raise RuntimeError("a source-boundary audit may not close a full gate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    markdown = render_markdown(report)
    if args.write:
        JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(markdown, encoding="utf-8")
        print("SUSY V43 charged-spurion source audit: wrote certificates")
    if args.check:
        expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if not JSON_PATH.exists() or not MD_PATH.exists():
            raise SystemExit("generated V43 certificates are missing; run with --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("generated V43 JSON is stale; run with --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown:
            raise SystemExit("generated V43 Markdown is stale; run with --write")
        print("SUSY V43 charged-spurion source audit: PASS")


if __name__ == "__main__":
    main()
