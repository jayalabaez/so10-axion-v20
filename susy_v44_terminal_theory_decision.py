#!/usr/bin/env python3
"""Terminal V44 decision for the V40--V43 complete-theory program.

This audit does four things which must remain logically separate:

1. verifies that the V43 master artifact still has zero closed G1--G8 gates;
2. independently rederives the renormalizable ``NDirac E3 Omega`` portal
   omitted from the V43 charged-spurion scan;
3. closes and freezes V40--V43 as a *complete-theory candidate* while
   preserving its scoped EFT calculations and no-go results; and
4. preregisters one replacement architecture, a sequestered 5D Spin(10)
   interval, without pretending that its missing microscopic data exist.

The output is fail-closed.  Selecting a successor research direction closes
no physics gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import susy_v43_charged_spurion_source_audit as spurion
import susy_v43_complete_theory_audit as v43


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V44_TERMINAL_THEORY_DECISION.json"
MD_PATH = ROOT / "SUSY_V44_TERMINAL_THEORY_DECISION.md"

INPUTS = {
    "v43_master": ROOT / "SUSY_V43_COMPLETE_THEORY_AUDIT.json",
    "v43_spurion": ROOT / "SUSY_V43_CHARGED_SPURION_SOURCE_AUDIT.json",
    "v44_erratum_json": ROOT / "SUSY_V44_TERMINAL_VALIDITY_ERRATUM.json",
    "v44_erratum_md": ROOT / "SUSY_V44_TERMINAL_VALIDITY_ERRATUM.md",
    "v44_stopping_rule": ROOT / "SUSY_V44_RESEARCH_STOPPING_RULE.md",
    "v44_successor_contract": ROOT / "SUSY_V44_NEW_PHYSICS_SUCCESSOR_CONTRACT.md",
}

SOURCE_FILES = (
    "susy_v44_terminal_theory_decision.py",
    "test_susy_v44_terminal_theory_decision.py",
    "susy_v43_charged_spurion_source_audit.py",
    "susy_v43_complete_theory_audit.py",
    *tuple(path.name for path in INPUTS.values()),
)

STATUS = (
    "V44_V43_COMPLETE_THEORY_CANDIDATE_CLOSED__"
    "SCOPED_EFT_RESULTS_PRESERVED__"
    "5D_SPIN10_SUCCESSOR_PREREGISTERED__ZERO_GATES_PROMOTED"
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
        raise RuntimeError(f"required input missing: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"required input is not a JSON object: {path.name}")
    return payload


def source_manifest() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in SOURCE_FILES:
        path = ROOT / name
        rows.append(
            {
                "path": name,
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
        )
    return rows


def charge(names: Iterable[str], key: str, modulus: int | None = None) -> int:
    total = sum(int(spurion.FIELDS[name][key]) for name in names)
    return total if modulus is None else total % modulus


def is_abelian_superpotential_invariant(names: Sequence[str]) -> bool:
    return (
        charge(names, "u1f") == 0
        and charge(names, "u1s") == 0
        and charge(names, "r4", 4) == 2
        and charge(names, "z5610", 5610) == 0
        and charge(names, "pq") == 0
    )


def matrix_rank(matrix: Sequence[Sequence[int]]) -> int:
    """Exact Gaussian-elimination rank over the rationals."""

    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    n_rows = len(work)
    n_cols = len(work[0])
    pivot_row = 0
    for col in range(n_cols):
        pivot = next((row for row in range(pivot_row, n_rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(n_rows):
            if row == pivot_row or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return pivot_row


def portal_erratum() -> dict[str, Any]:
    """Recompute the omitted cubic and its generic singlet-mass consequence."""

    witness = ("NDirac", "E3", "Omega")
    charges = {
        "U1F": charge(witness, "u1f"),
        "U1S": charge(witness, "u1s"),
        "Z4R": charge(witness, "r4", 4),
        "Z5610": charge(witness, "z5610", 5610),
        "PQ_numerator_over_170": charge(witness, "pq"),
    }
    scanned_candidates = set(spurion.HOST_CORE_FIELDS + spurion.SOURCE_FIELDS)
    all_fields = tuple(spurion.FIELDS)
    source = set(spurion.SOURCE_FIELDS)
    singlet_mixed_rows: list[list[str]] = []
    direct_driver_rows: list[list[str]] = []
    for degree in range(1, 4):
        for combo in itertools.combinations_with_replacement(all_fields, degree):
            if not (set(combo) & source and set(combo) - source):
                continue
            if not is_abelian_superpotential_invariant(combo):
                continue
            if all(not spurion.FIELDS[name]["ps"] for name in combo):
                singlet_mixed_rows.append(list(combo))
            if set(combo) & set(spurion.HOST_DRIVER_FIELDS):
                direct_driver_rows.append(list(combo))

    # After both <ThetaMinus> and <Omega> are nonzero, the generic symmetric
    # mass matrix for (E3,E6,N1,N2,N3) is a star.  Nonzero example entries
    # establish the generic rank; the rank is two and the light nullity is
    # three, but the light basis mixes the intended NDirac and anomalon fields.
    generic_star_mass_matrix = [
        [0, 1, 1, 2, 3],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
        [3, 0, 0, 0, 0],
    ]
    rank = matrix_rank(generic_star_mass_matrix)
    return {
        "omitted_operator": "NDirac E3 Omega",
        "fields": list(witness),
        "total_charges": charges,
        "all_fields_are_PS_singlets": all(not spurion.FIELDS[name]["ps"] for name in witness),
        "renormalizable_superpotential_operator_is_allowed": is_abelian_superpotential_invariant(witness),
        "E3_was_in_original_scan_candidates": "E3" in scanned_candidates,
        "why_omitted": (
            "V43 scanned V40.VISIBLE_FIELDS plus SOURCE_FIELDS.  E3 belongs to the already-declared "
            "anomaly sector and was absent from that candidate tuple."
        ),
        "full_table_PS_singlet_mixed_rows_through_degree_three": singlet_mixed_rows,
        "full_table_direct_X_or_Zp_source_rows_through_degree_three": direct_driver_rows,
        "target_zero_NDirac_zero_E3_branch_survives_this_operator": True,
        "generic_singlet_mass_matrix_basis": ["E3", "E6", "N1", "N2", "N3"],
        "generic_example_mass_matrix_rank": rank,
        "generic_example_mass_matrix_nullity": len(generic_star_mass_matrix) - rank,
        "physical_correction": (
            "The displayed zero-matter F-flat branch is not contradicted, but <Omega> generically mixes "
            "the NDirac and anomalon singlet sectors.  The broad source-host protection and factorization "
            "claims are therefore withdrawn; the absence of direct X/Zp-source cubics survives."
        ),
    }


def corrected_gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "closed": False,
            "terminal_classification": "scoped 4D threshold classes excluded; no common microscopic parent",
            "retained_result": "The self-Majorana gravity-row escape and the scoped 33Z/66Z PS-threshold obstruction remain exact.",
        },
        {
            "gate": "G2",
            "closed": False,
            "terminal_classification": "restricted F-flat source branch only; full-field portal overclaim corrected",
            "retained_result": "The target zero-NDirac, zero-E3 branch and absence of direct X/Zp-source cubics survive.",
        },
        {
            "gate": "G3",
            "closed": False,
            "terminal_classification": "minimal gauged U1S spurion realization internally excluded",
            "retained_result": "The isolated neutral Theta+/- source remains an EFT F/D-flat building block.",
        },
        {
            "gate": "G4",
            "closed": False,
            "terminal_classification": "mediation, Kähler/soft vacuum, mu/Bmu, EWSB, and likelihood missing",
            "retained_result": "No complete G4 derivation is claimed.",
        },
        {
            "gate": "G5",
            "closed": False,
            "terminal_classification": "stated isolated large-Yukawa dark benchmark excluded; replacement missing",
            "retained_result": "The perturbativity/Landau-pole exclusion remains a quantitative negative result.",
        },
        {
            "gate": "G6",
            "closed": False,
            "terminal_classification": "physical boundary conditions, coupled RG, thresholds, and spectrum missing",
            "retained_result": "Threshold inventories remain inputs, not a spectrum prediction.",
        },
        {
            "gate": "G7",
            "closed": False,
            "terminal_classification": "ordinary no-GS Z4M realization excluded; full ring and amplitudes incomplete",
            "retained_result": "Z4M arithmetically blocks the named witness, but is not a completed gauge symmetry.",
        },
        {
            "gate": "G8",
            "closed": False,
            "terminal_classification": "local Dirac messenger matching valid; flavour prediction absent",
            "retained_result": "The tree-level Q H Sc NDirac matching remains a valid local EFT calculation.",
        },
    ]


def successor_contract() -> dict[str, Any]:
    stages = [
        {
            "id": "S0-global-form-parities-and-localization",
            "required_output": (
                "One compact [Spin(10) x U(1)_F]/Gamma interval, both boundary groups, every vector/hyper/boundary "
                "multiplet, both parities, chirality, localization, and an exact zero-mode index."
            ),
            "kill_if": "No assignment yields exactly the intended Standard-Model global form and chiral light spectrum.",
        },
        {
            "id": "S1-localized-anomalies-and-quantized-inflow",
            "required_output": (
                "Regulated anomaly density on each wall, integrated zero-mode anomaly, integer CS/eta data, and "
                "global/bordism checks for the actual quotient."
            ),
            "kill_if": "Any integrated anomaly remains or the necessary inflow coefficient is not quantized.",
        },
        {
            "id": "S2-boundary-vacuum-and-heavy-mass-rank",
            "required_output": (
                "Complete wall W/K/gauge data, source and rank-reducing Higgs F/D equations, gauge quotient, "
                "eaten modes, and full-rank exotic/KK mass matrices."
            ),
            "kill_if": "No simultaneous physical branch exists or an unavoidable charged exotic remains massless.",
        },
        {
            "id": "S3-local-and-cross-wall-operator-matching",
            "required_output": (
                "Wall-local invariant rings plus regulated bulk propagator/KK matching for source-host and every "
                "dangerous baryon/lepton class, with Wilson coefficients."
            ),
            "kill_if": "A forbidden local term exists or cross-wall suppression cannot meet proton/multinucleon limits.",
        },
        {
            "id": "S4-compactification-threshold-and-phenomenology",
            "required_output": (
                "Radion/Kähler/soft vacuum, cutoff and KK thresholds, perturbative unification, pole spectrum, "
                "flavour/neutrino likelihood, dark cosmology, and withheld predictions."
            ),
            "kill_if": "No perturbative and phenomenologically allowed region survives.",
        },
    ]
    return {
        "selected_route": "SEQUESTERED_5D_SPIN10_INTERVAL",
        "current_status": "PREREGISTERED_REPLACEMENT_ARCHITECTURE_NOT_INSTANTIATED",
        "current_closed_gate_count": 0,
        "provisional_skeleton": {
            "spacetime": "M4 x [0,L], supersymmetric interval/orbifold",
            "bulk_algebra": "so(10) + u(1)_F; compact quotient not yet fixed",
            "PS_wall_target": "visible host/matter sector with unbroken continuous U(1)_F",
            "source_GUT_wall_target": "neutral STheta, Theta+/- source plus a fully specified rank-reducing boundary sector",
            "mechanism": (
                "Use locality, rather than another additive label, to separate source from X/Zp and to make "
                "U(1)_F-breaking dressings of oriented G7 sources cross-wall effects."
            ),
            "V43_Omega_and_U1S_retained": False,
            "old_U1X_U1H_Z5610_parent_retained_as_microscopic_factor": False,
        },
        "why_selected": [
            "It changes the physical mechanism targeted by the exhausted 4D additive-charge iterations.",
            "One locality structure can address source-host separation and G7 operator generation together.",
            "It is falsifiable in dependency order by zero modes, local anomalies, mass rank, and nonlocal Wilson coefficients.",
        ],
        "essential_caution": (
            "Four-dimensional anomaly cancellation does not imply wall-by-wall consistency.  The provisional "
            "Theta/anomalon separation is not certified until localized anomalies and all cross-wall exotic mass "
            "ranks are solved together.  No inflow term or bulk messenger is silently assumed."
        ),
        "ordered_stages": stages,
        "reopen_rule": (
            "Reopen G1--G3 and G7 only after one versioned candidate passes S0--S3 simultaneously.  Restart G4--G8 "
            "only after that same candidate also has the S4 inputs; never combine sectors from different candidates."
        ),
        "literature_scope": {
            "5D_SO10_orbifold_precedent": "https://arxiv.org/abs/hep-ph/0603086",
            "localized_orbifold_anomaly_constraints": "https://arxiv.org/abs/hep-th/0305024",
            "localized_anomaly_warning": "https://arxiv.org/abs/hep-th/0110073",
            "global_eta_inflow": "https://arxiv.org/abs/1909.08775",
            "gapped_boundary_obstruction": "https://arxiv.org/abs/1910.04962",
        },
    }


def build_report() -> dict[str, Any]:
    v43_stored = load_json(INPUTS["v43_master"])
    spurion_stored = load_json(INPUTS["v43_spurion"])
    erratum_stored = load_json(INPUTS["v44_erratum_json"])
    v43_live = v43.build_report()
    portal = portal_erratum()
    gates = corrected_gate_ledger()
    successor = successor_contract()
    manifest = source_manifest()

    checks = {
        "v43_stored_core_verifies": v43.canonical_sha(v43_stored) == v43_stored.get("core_sha256"),
        "v43_live_matches_stored_core": v43_live.get("core_sha256") == v43_stored.get("core_sha256"),
        "spurion_stored_core_verifies": spurion.canonical_sha(spurion_stored) == spurion_stored.get("core_sha256"),
        "v43_has_zero_closed_gates": (
            v43_stored.get("established_full_predictive_closed_count") == 0
            and all(not row.get("closed") for row in v43_stored.get("gate_ledger", []))
        ),
        "portal_witness_rederived": (
            portal["renormalizable_superpotential_operator_is_allowed"]
            and portal["all_fields_are_PS_singlets"]
            and not portal["E3_was_in_original_scan_candidates"]
        ),
        "direct_X_Zp_source_cubic_absence_survives": not portal[
            "full_table_direct_X_or_Zp_source_rows_through_degree_three"
        ],
        "generic_portal_mass_matrix_rank_is_two": portal["generic_example_mass_matrix_rank"] == 2,
        "erratum_names_same_operator": erratum_stored.get("v43_erratum", {}).get("omitted_operator") == portal["omitted_operator"],
        "all_corrected_gates_fail_closed": len(gates) == 8 and all(not row["closed"] for row in gates),
        "successor_promotes_no_gate": successor["current_closed_gate_count"] == 0,
        "all_required_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V44 terminal integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v44-terminal-theory-decision-v1",
        "status": STATUS,
        "terminal_answer": (
            "This is the end of V40--V43 as a candidate complete theory.  It is not a proof that every UV completion "
            "is impossible.  Preserve the scoped EFT/no-go archive and permit continuation only through the single "
            "preregistered 5D successor contract."
        ),
        "current_candidate": {
            "label": "V40--V43 weakly coupled 4D SUSY Pati-Salam additive-selector program",
            "complete_theory_status": "CLOSED_AND_FROZEN",
            "complete_theory_exists_from_supplied_data": False,
            "empirically_falsified_by_a_joint_likelihood": False,
            "one_integrated_action_was_established": False,
            "closed_gate_count": 0,
            "total_gate_count": 8,
            "ordinary_additive_charge_iteration_allowed": False,
            "preservation_label": "REJECTED_AS_COMPLETE_THEORY__RETAINED_AS_CONDITIONAL_SUSY_PS_EFT_AND_NO_GO_TOOLKIT",
        },
        "v43_portal_erratum": portal,
        "corrected_gate_ledger": gates,
        "surviving_scoped_results": [
            "V41 tree-level Dirac-messenger matching to Q H Sc NDirac.",
            "V43 self-Majorana exception to the earlier even-X Dirac gravity-parity inference.",
            "The ordinary PS-unbroken self-paired/Pfaffian 33Z/66Z threshold obstruction.",
            "The V39 isolated large-Yukawa dark benchmark perturbativity exclusion.",
            "The arithmetic fact that Z4M blocks the named degree-ten witness, without promoting it to a gauge completion.",
        ],
        "claims_withdrawn": [
            "V43 is one integrated EFT or a complete theory.",
            "The full declared V43 field table has no renormalizable source-host portal.",
            "Every F-flat host branch factors with the V43 charged-spurion source branch.",
            "Anomaly completion is the only remaining cost of the Z4M proposal.",
            "Passing repository tests validates UV or empirical physics rather than the encoded calculations.",
        ],
        "selected_successor": successor,
        "not_selected": {
            "more_4D_additive_charge_tables": "frozen by analytic divisibility, parity, anomaly, vacuum, and pole obstructions",
            "non_Abelian_finite_selector": "no group, representation assignment, invariant ring, or anomaly class is supplied",
            "composite_or_topological_completion": "no microscopic gauge theory, moduli space, or boundary topological action is supplied",
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "source_manifest": manifest,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    current = report["current_candidate"]
    portal = report["v43_portal_erratum"]
    successor = report["selected_successor"]
    gate_rows = "\n".join(
        f"| {row['gate']} | open | {row['terminal_classification']} | {row['retained_result']} |"
        for row in report["corrected_gate_ledger"]
    )
    stages = "\n".join(
        f"{index}. **{row['id']}** — {row['required_output']}  **Kill condition:** {row['kill_if']}"
        for index, row in enumerate(successor["ordered_stages"], start=1)
    )
    surviving = "\n".join(f"- {item}" for item in report["surviving_scoped_results"])
    withdrawn = "\n".join(f"- {item}" for item in report["claims_withdrawn"])
    charge_tuple = ",".join(
        str(portal["total_charges"][key])
        for key in ("U1F", "U1S", "Z4R", "Z5610", "PQ_numerator_over_170")
    )
    return f"""# V44 terminal theory decision

Status: `{report['status']}`

## Terminal answer

{report['terminal_answer']}

The current candidate is **{current['complete_theory_status']}** with
`{current['closed_gate_count']}/{current['total_gate_count']}` full predictive
gates closed.  This is a deductive failure of its own completeness contract,
not an empirical falsification by a joint likelihood.  The workspace never
established one common action containing all V40--V43 repair branches.

## V43 erratum independently rederived

The full declared field table allows the PS-singlet cubic
`{portal['omitted_operator']}` with total
`(U1F,U1S,Z4R,Z5610,PQ)=({charge_tuple})`.
`E3` was outside the V43 `VISIBLE_FIELDS+SOURCE_FIELDS` scan.  The generic
`(E3,E6,N1,N2,N3)` star mass matrix has rank
`{portal['generic_example_mass_matrix_rank']}` and nullity
`{portal['generic_example_mass_matrix_nullity']}`: three light singlet
combinations remain, but their basis is mixed.  The zero-`NDirac`, zero-`E3`
F branch and the absence of direct `X/Zp` source cubics survive; the broad
separation theorem does not.

## Corrected G1--G8 ledger

| Gate | Status | Terminal classification | Scoped result retained |
|---|---|---|---|
{gate_rows}

## What remains scientifically valid

{surviving}

## Claims withdrawn

{withdrawn}

## Sole successor: sequestered 5D Spin(10) interval

The successor is **selected for research, not instantiated** and closes
`{successor['current_closed_gate_count']}` gates.  Its provisional mechanism
is five-dimensional locality: place the source and the PS host on opposite
walls so source-host portals and U(1)F-breaking dressings of oriented G7
operators require explicit cross-wall propagation.  V43's `Omega/U(1)S`
construction and the old `U(1)X/U(1)H/Z5610` microscopic parent are dropped.

{successor['essential_caution']}

### Ordered falsification stages

{stages}

**Reopen rule:** {successor['reopen_rule']}

The detailed route contract is `SUSY_V44_NEW_PHYSICS_SUCCESSOR_CONTRACT.md`.
The stopping rule is `SUSY_V44_RESEARCH_STOPPING_RULE.md`.

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
        raise RuntimeError("V44 terminal JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V44 terminal Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V44_TERMINAL_THEORY_DECISION_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
