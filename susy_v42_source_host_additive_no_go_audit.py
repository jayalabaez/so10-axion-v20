#!/usr/bin/env python3
"""Fail-closed V42 audit of source--host separation in the V40 Z9 route.

V41 exhibited a canonical U(1)_F -> Z9 source branch, but its stabilizer
STheta has the same listed selector signature as the pre-existing X and Zp
host drivers.  This program proves the precise obstruction: no *additional
additive selection rule with neutral parameters* can forbid the bridge
X ThetaPlus ThetaMinus (or its Zp counterpart) while retaining the naked
linear source and host driver terms and the source stabilizer cubic.

The result is intentionally a no-go for symmetry-protected separation, not a
claim that a fully coupled vacuum cannot exist.  A charged-spurion/dynamical
linear-term construction is outside the theorem and must be audited as a new
model, including its F/D branch, anomalies, residual group, and induced
operators.
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
OUTPUT_JSON = ROOT / "SUSY_V42_SOURCE_HOST_ADDITIVE_NO_GO_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V42_SOURCE_HOST_ADDITIVE_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v42_source_host_additive_no_go_audit.py"
V40_PATH = ROOT / "susy_v40_all_ring_selector.py"

STATUS = (
    "V42_ADDITIVE_SOURCE_HOST_SEPARATION_NO_GO_CERTIFIED_FOR_NEUTRAL_"
    "PARAMETERS__COUPLED_VACUUM_AND_SPURION_EXTENSIONS_FAIL_CLOSED"
)

# A selection rule can be an ordinary, discrete, or R-type additive factor.
# In each factor the superpotential has one target charge w (zero for an
# ordinary non-R factor).  Parameters are assumed neutral in that factor.
LOGICAL_REQUIRED_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("source_linear", ("STheta",)),
    ("host_X_linear", ("X",)),
    ("host_Zp_linear", ("Zp",)),
    ("source_stabilizer_cubic", ("STheta", "ThetaPlus", "ThetaMinus")),
)

BRIDGE_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("X_ThetaPlus_ThetaMinus", ("X", "ThetaPlus", "ThetaMinus")),
    ("Zp_ThetaPlus_ThetaMinus", ("Zp", "ThetaPlus", "ThetaMinus")),
    # These additional mixings are allowed by the already-declared V40
    # product.  The universal no-go below needs only the first two bridges.
    ("X_STheta_STheta", ("X", "STheta", "STheta")),
    ("Zp_STheta_STheta", ("Zp", "STheta", "STheta")),
    ("STheta_X_X", ("STheta", "X", "X")),
    ("STheta_X_Zp", ("STheta", "X", "Zp")),
    ("STheta_Zp_Zp", ("STheta", "Zp", "Zp")),
)

SELECTION_KEYS: tuple[tuple[str, int], ...] = (
    ("u1f", 0),
    ("z5610", 5610),
    ("pq", 0),
    ("r4", 4),
)
TARGETS = {"u1f": 0, "z5610": 0, "pq": 0, "r4": 2}


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge(fields: Iterable[str], key: str, modulus: int) -> int:
    total = sum(int(v40.FIELDS[field][key]) for field in fields)
    return total if modulus == 0 else total % modulus


def old_product_charge_audit() -> dict[str, Any]:
    """Check the starting V40 ledger rather than assuming its signatures."""

    def row(label: str, fields: tuple[str, ...]) -> dict[str, Any]:
        values = {key: charge(fields, key, modulus) for key, modulus in SELECTION_KEYS}
        allowed = all(values[key] == TARGETS[key] for key, _ in SELECTION_KEYS)
        return {
            "label": label,
            "fields": list(fields),
            "charges": values,
            "allowed_by_existing_V40_product": allowed,
        }

    required = [row(label, fields) for label, fields in LOGICAL_REQUIRED_TERMS]
    bridges = [row(label, fields) for label, fields in BRIDGE_TERMS]
    v40_terms = [
        row(label, fields)
        for label, fields in v40.RENORMALIZABLE_TERMS
    ]
    return {
        "V40_field_signatures": {
            field: {
                "u1f": int(v40.FIELDS[field]["u1f"]),
                "z5610": int(v40.FIELDS[field]["z5610"]),
                "pq": int(v40.FIELDS[field]["pq"]),
                "r4": int(v40.FIELDS[field]["r4"]),
            }
            for field in ("STheta", "X", "Zp", "ThetaPlus", "ThetaMinus")
        },
        "required_term_rows": required,
        "bridge_term_rows": bridges,
        "existing_V40_renormalizable_term_count": len(v40_terms),
        "all_existing_V40_renormalizable_terms_allowed": all(
            item["allowed_by_existing_V40_product"] for item in v40_terms
        ),
        "all_required_terms_allowed": all(item["allowed_by_existing_V40_product"] for item in required),
        "all_listed_bridges_already_allowed": all(item["allowed_by_existing_V40_product"] for item in bridges),
    }


def symbolic_additive_no_go() -> dict[str, Any]:
    """State a factor-by-factor proof valid for arbitrary additive A.

    Let q map fields to an additive abelian group A and let w be the target
    superpotential charge in A.  The linear terms force q(S)=q(X)=q(Z)=w.
    The stabilizer cubic then forces q(ThetaPlus)+q(ThetaMinus)=0, so both
    driver--Theta bridges have charge w and are allowed.  The proof applies
    independently to each factor of a product of additive symmetries.
    """

    return {
        "theorem": "neutral-parameter additive source-host separation no-go",
        "assumptions": [
            "A is any additive abelian selection group; it may be finite, continuous, R-type, or a direct product of such factors.",
            "Every numerical coupling and every dimensionful parameter in the naked linear terms is neutral under A.",
            "The superpotential target charge is a fixed element w in A (w=0 for a non-R factor).",
            "The required terms are STheta, X, Zp, and STheta ThetaPlus ThetaMinus; their coefficients are not replaced by VEV-carrying spurions.",
        ],
        "allowed_term_equations": [
            "q(STheta) = w from the naked source linear term.",
            "q(X) = w and q(Zp) = w from the naked host-driver linear terms.",
            "q(STheta)+q(ThetaPlus)+q(ThetaMinus) = w from the source stabilizer cubic.",
        ],
        "deductions": [
            "q(ThetaPlus)+q(ThetaMinus) = 0.",
            "q(X ThetaPlus ThetaMinus) = q(X) = w.",
            "q(Zp ThetaPlus ThetaMinus) = q(Zp) = w.",
        ],
        "universal_forbidden_goal_fails": [
            "X ThetaPlus ThetaMinus cannot be forbidden by A.",
            "Zp ThetaPlus ThetaMinus cannot be forbidden by A.",
        ],
        "componentwise_product_extension_statement": (
            "Adding any number of new additive factors does not help: the same three equations hold in every factor, so the bridge is allowed componentwise."
        ),
        "conclusion": (
            "There is no symmetry-protected separation of the V41 source from both X and Zp within the stated neutral-parameter, naked-linear-term class."
        ),
        "strength_with_respect_to_the_full_V40_ledger": (
            "The proof uses only a necessary subset of the current source and host terms. Requiring every remaining V40 host term can only reduce the allowed charge assignments, not evade an implication already forced by that subset."
        ),
        "does_not_prove": [
            "that a fully coupled source-plus-host F/D solution is impossible",
            "that a new model with charged spurions/dynamical linear terms is impossible",
            "a full G-gate closure",
        ],
    }


def finite_cyclic_check() -> dict[str, Any]:
    """Exhaustively check the algebra in representative finite additive factors."""

    checked = 0
    counterexamples: list[dict[str, int]] = []
    for order in range(2, 65):
        for target_w in range(order):
            for theta_plus in range(order):
                theta_minus = (-theta_plus) % order
                s_theta = target_w
                x = target_w
                zp = target_w
                checked += 1
                source_cubic = (s_theta + theta_plus + theta_minus) % order
                x_bridge = (x + theta_plus + theta_minus) % order
                zp_bridge = (zp + theta_plus + theta_minus) % order
                if source_cubic != target_w or x_bridge != target_w or zp_bridge != target_w:
                    counterexamples.append({
                        "N": order,
                        "w": target_w,
                        "theta_plus": theta_plus,
                        "theta_minus": theta_minus,
                        "source_cubic": source_cubic,
                        "X_bridge": x_bridge,
                        "Zp_bridge": zp_bridge,
                    })
    return {
        "orders_checked": [2, 64],
        "constructed_assignments_checked": checked,
        "counterexamples": counterexamples,
        "all_finite_cyclic_examples_confirm_the_symbolic_proof": not counterexamples,
    }


def coupled_F_branch_boundary() -> dict[str, Any]:
    """Show why the isolated V41 branch cannot be silently promoted."""

    return {
        "generic_allowed_superpotential_piece": (
            "W = kappa STheta(ThetaPlus ThetaMinus-mu_F^2) + "
            "lambda_X X ThetaPlus ThetaMinus + lambda_Z Zp ThetaPlus ThetaMinus + W_host"
        ),
        "source_branch_conditions": {
            "STheta": 0,
            "ThetaPlus_times_ThetaMinus": "mu_F^2 != 0",
            "X": 0,
            "Zp": 0,
            "unperturbed_host_driver_conditions": "partial_X W_host = partial_Zp W_host = 0",
        },
        "F_terms_on_that_putative_product_branch": {
            "F_STheta": "kappa(ThetaPlus ThetaMinus-mu_F^2) = 0",
            "F_X": "partial_X W_host + lambda_X mu_F^2 = lambda_X mu_F^2",
            "F_Zp": "partial_Zp W_host + lambda_Z mu_F^2 = lambda_Z mu_F^2",
        },
        "generic_result": {
            "isolated_source_times_unperturbed_host_branch_is_F_flat": False,
            "reason": "For mu_F^2 != 0, it requires lambda_X=lambda_Z=0; the no-go proves no additive neutral-parameter symmetry can enforce those two zeros while retaining the required terms.",
        },
        "honest_remaining_options": [
            "solve a genuinely coupled F/D system with all allowed coefficients and the full PS/PQ host field content",
            "replace one or more naked linear terms by explicitly modelled charged-spurion/dynamical terms, then re-audit anomalies, the residual symmetry, every induced operator, and the F/D branch",
            "supply a non-additive or geometrical sequestering construction with its microscopic derivation",
        ],
        "coupled_full_host_F_D_branch_solved": False,
        "coupled_full_host_F_D_branch_disproved": False,
    }


def spurion_evasion_boundary() -> dict[str, Any]:
    return {
        "why_it_is_outside_the_no_go": (
            "A charged field VEV can replace a numerical coefficient in a linear term, invalidating the neutral-parameter premise.  It is a new theory, not an added label on the V41 ledger."
        ),
        "minimal_required_reaudit": [
            "all renormalizable and induced effective source-host operators after the spurion VEVs",
            "continuous, discrete, mixed-product, gravitational, and global anomaly rows for the new fields",
            "an explicit F-flat and D-flat branch with every charged-spurion VEV, including the surviving discrete subgroup",
            "mass ranks and non-condensation of all anomalons/messengers",
            "the fully coupled PS/PQ/U(1)_F vacuum and its Kahler/soft deformation",
        ],
        "can_be_used_as_evidence_for_current_V41_full_source": False,
        "can_be_used_to_close_a_gate_without_that_reaudit": False,
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.exists(), "sha256": sha256_file(path) if path.exists() else None}
        for path in (Path(__file__), TEST_PATH, V40_PATH)
    ]


def build_report() -> dict[str, Any]:
    old_product = old_product_charge_audit()
    theorem = symbolic_additive_no_go()
    finite = finite_cyclic_check()
    coupled = coupled_F_branch_boundary()
    report: dict[str, Any] = {
        "schema": "susy-v42-source-host-additive-no-go-audit-v1",
        "status": STATUS,
        "scope": (
            "A formal no-go for additive symmetry-protected separation of the V41 U(1)_F-to-Z9 source from V40 X/Zp drivers when all current naked linear terms have neutral parameters."
        ),
        "V40_charge_starting_point": old_product,
        "additive_no_go": theorem,
        "finite_cyclic_crosscheck": finite,
        "coupled_F_branch_boundary": coupled,
        "charged_spurion_evasion_boundary": spurion_evasion_boundary(),
        "decision": {
            "current_V41_source_host_symmetry_protected_separation_exists": False,
            "all_current_V40_bridges_are_forbidden": False,
            "generic_isolated_source_times_unperturbed_host_branch_is_F_flat": False,
            "a_full_coupled_source_host_branch_is_disproved": False,
            "charged_spurion_extension_completed": False,
            "full_gate_closed": [],
        },
        "source_manifest": source_manifest(),
    }
    report["integrity_checks"] = {
        "V40_required_terms_are_allowed": old_product["all_required_terms_allowed"],
        "V40_existing_renormalizable_ledger_is_consistent": old_product["all_existing_V40_renormalizable_terms_allowed"],
        "V40_bridges_already_allowed": old_product["all_listed_bridges_already_allowed"],
        "symbolic_no_go_has_two_universal_bridges": len(theorem["universal_forbidden_goal_fails"]) == 2,
        "finite_cyclic_check_passes": finite["all_finite_cyclic_examples_confirm_the_symbolic_proof"],
        "no_false_coupled_vacuum_claim": not coupled["coupled_full_host_F_D_branch_solved"],
        "no_full_gate_promoted": report["decision"]["full_gate_closed"] == [],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    old = report["V40_charge_starting_point"]
    theorem = report["additive_no_go"]
    finite = report["finite_cyclic_crosscheck"]
    coupled = report["coupled_F_branch_boundary"]
    bridges = "\n".join(
        f"| `{row['label']}` | `{row['charges']}` | {'yes' if row['allowed_by_existing_V40_product'] else 'no'} |"
        for row in old["bridge_term_rows"]
    )
    return f"""# V42 source–host additive-separation no-go

Status: `{report['status']}`

The V41 `U(1)_F -> Z9` source is a valid isolated canonical-SUSY
construction, but it is not symmetrically separated from the existing V40
`X` and `Zp` driver system.  This audit proves that an extra additive label
cannot supply that separation while the present naked linear terms are kept.

## Starting ledger

`STheta`, `X`, and `Zp` have identical V40 signatures:
`{old['V40_field_signatures']['STheta']}`,
`{old['V40_field_signatures']['X']}`, and
`{old['V40_field_signatures']['Zp']}`.  All
{old['existing_V40_renormalizable_term_count']} existing renormalizable V40
terms pass the old product check.  The following source–host mixings also
pass it:

| Bridge | `(U1F, Z5610, PQ, Z4R)` charges | Allowed |
|---|---|---|
{bridges}

## Exact additive no-go

For an arbitrary additive factor `A`, let `w` be the superpotential target
charge.  Neutral-parameter naked linear terms require
`q(STheta)=q(X)=q(Zp)=w`.  The required stabilizer cubic
`STheta ThetaPlus ThetaMinus` then requires
`q(ThetaPlus)+q(ThetaMinus)=0`.  Consequently both
`X ThetaPlus ThetaMinus` and `Zp ThetaPlus ThetaMinus` have charge `w` and
are allowed.  The proof applies componentwise to any product of additive
factors, including ordinary/discrete/R-type choices.  It uses only a required
subset of the source/host ledger, so imposing the remaining V40 host terms
cannot evade the implication.

An exhaustive finite check of cyclic factors `Z_N`, `2 <= N <= 64`, tested
{finite['constructed_assignments_checked']} consistent assignments and found
{len(finite['counterexamples'])} counterexamples.

## Consequence for the V41 branch

The generic allowed piece is

`{coupled['generic_allowed_superpotential_piece']}`.

On the isolated-source × unperturbed-host branch,
`F_X=lambda_X mu_F^2` and `F_Zp=lambda_Z mu_F^2`.  Thus that product branch
is not generically F-flat for nonzero `mu_F^2`; setting both lambdas to zero
is a tuning, not a symmetry consequence in this class.  A fully coupled
source–host F/D solution may still exist, but has not been solved or claimed.

A charged-spurion/dynamical-linear-term mechanism falls outside the theorem
and is a new model requiring a full residual-symmetry, anomaly, induced-term,
mass-rank, and coupled-vacuum audit.  No G gate is closed here.

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS:
        raise RuntimeError("unexpected V42 source-host no-go status")
    if canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale V42 source-host no-go core hash")
    old = report["V40_charge_starting_point"]
    if not old["all_existing_V40_renormalizable_terms_allowed"]:
        raise RuntimeError("the V40 source ledger no longer passes its listed product charges")
    if not old["all_required_terms_allowed"] or not old["all_listed_bridges_already_allowed"]:
        raise RuntimeError("the V42 starting charge ledger is inconsistent")
    theorem = report["additive_no_go"]
    if len(theorem["universal_forbidden_goal_fails"]) != 2:
        raise RuntimeError("the universal source-host bridge proof is incomplete")
    finite = report["finite_cyclic_crosscheck"]
    if finite["counterexamples"] or not finite["all_finite_cyclic_examples_confirm_the_symbolic_proof"]:
        raise RuntimeError("finite additive crosscheck contradicts the symbolic theorem")
    decision = report["decision"]
    if decision["current_V41_source_host_symmetry_protected_separation_exists"]:
        raise RuntimeError("neutral-parameter source-host separation was falsely promoted")
    if decision["a_full_coupled_source_host_branch_is_disproved"]:
        raise RuntimeError("the audit must not overstate its no-go as a coupled-vacuum no-go")
    if decision["full_gate_closed"]:
        raise RuntimeError("a separation sub-audit must not close a full gate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    markdown = render_markdown(report)
    if args.write:
        OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUTPUT_MD.write_text(markdown, encoding="utf-8")
        print("SUSY V42 source-host additive no-go audit: wrote certificates")
    if args.check:
        expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if not OUTPUT_JSON.exists() or not OUTPUT_MD.exists():
            raise SystemExit("generated V42 source-host certificates are missing; run with --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("generated V42 source-host JSON is stale; run with --write")
        if OUTPUT_MD.read_text(encoding="utf-8") != markdown:
            raise SystemExit("generated V42 source-host Markdown is stale; run with --write")
        print("SUSY V42 source-host additive no-go audit: PASS")


if __name__ == "__main__":
    main()
