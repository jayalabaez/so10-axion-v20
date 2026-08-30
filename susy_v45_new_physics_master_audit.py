#!/usr/bin/env python3
"""Integrated fail-closed verdict for the reconciled V45 5D Spin(10) core.

V45 is a replacement architecture, not another field-table extension of
V40--V43.  This audit freezes one coherent microscopic skeleton and keeps four
logically different statements separate:

* exact compact-group/orbifold and zero-mode kinematics;
* parity-resolved *ordinary* localized anomaly cancellation;
* conditional lifting of the four exotic zero modes by source-wall masses;
* operator and discrete-R obstructions which keep G7 open.

Passing this executable audit validates the encoded algebra.  It is not a
claim that the remaining global anomaly, vacuum, KK, Wilson-coefficient or
phenomenology calculations have been performed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_NEW_PHYSICS_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_NEW_PHYSICS_MASTER_AUDIT.md"

INPUTS = {
    "v44_terminal": ROOT / "SUSY_V44_TERMINAL_THEORY_DECISION.json",
    "group_zero_modes": ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json",
    "wall_forensic": ROOT / "SUSY_V45_WALL_ANOMALY_MASS_AUDIT.json",
    "reconciled_bulk": ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json",
    "locality": ROOT / "SUSY_V45_LOCALITY_OPERATOR_AUDIT.json",
    "discrete_r": ROOT / "SUSY_V45_DISCRETE_R_AUDIT.json",
}

SOURCE_FILES = (
    "susy_v45_new_physics_master_audit.py",
    "test_susy_v45_new_physics_master_audit.py",
    "susy_v45_s0_group_zero_mode_audit.py",
    "test_susy_v45_s0_group_zero_mode_audit.py",
    "susy_v45_wall_anomaly_mass_audit.py",
    "test_susy_v45_wall_anomaly_mass_audit.py",
    "susy_v45_reconciled_bulk_spinor_audit.py",
    "test_susy_v45_reconciled_bulk_spinor_audit.py",
    "susy_v45_locality_operator_audit.py",
    "test_susy_v45_locality_operator_audit.py",
    "susy_v45_discrete_r_audit.py",
    "test_susy_v45_discrete_r_audit.py",
    *tuple(path.name for path in INPUTS.values()),
)

STATUS = (
    "V45_MINIMAL_5D_SPIN10_CORE_RECONCILED__CONNECTED_SM_GLOBAL_FORM_AND_"
    "ORDINARY_LOCAL_ANOMALIES_CERTIFIED__FOUR_EXOTIC_ZERO_MODES_"
    "CONDITIONALLY_LIFTED__UNIVERSAL_DISCRETE_R_FORCES_DEGREE20_ORIENTED_W__"
    "ZERO_FULL_GATES_CLOSED"
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
        raise RuntimeError(f"required V45 input missing: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"required V45 input is not an object: {path.name}")
    if canonical_sha(payload) != payload.get("core_sha256"):
        raise RuntimeError(f"required V45 input has an invalid core hash: {path.name}")
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


def primitive_charge_table() -> dict[str, int]:
    """Use the faithful normalization; the earlier V40 labels were 3x these."""

    return {
        "Q": 1,
        "Qc": -1,
        "H": 0,
        "HLF_16": 1,
        "HLA_bar16": -4,
        "HRA_16": -1,
        "HRF_bar16": 4,
        "ThetaPlus": 3,
        "ThetaMinus": -3,
        "STheta": 0,
        "Delta126": 0,
        "Delta126Bar": 0,
    }


def candidate_contract() -> dict[str, Any]:
    return {
        "name": "V45 reconciled four-bulk-spinor interval",
        "spacetime": "M4 x [0,L], equivalently a supersymmetric S1/(Z2 x Z2') interval",
        "bulk_group": "Spin(10) x U(1)_F with the direct-product global form used for this witness",
        "charge_normalization": {
            "convention": "primitive displayed local-particle normalization",
            "charges": primitive_charge_table(),
            "relation_to_V40_labels": "q_primitive=q_V40/3",
            "Theta_breaking": "U(1)_F -> Z3_F",
            "Z9_claim_retained": False,
        },
        "PS_wall_y0": {
            "group": "(SU(4)_C x SU(2)_L x SU(2)_R)/Z2_diag x U(1)_F",
            "boundary_chirals": [
                "3 Q=(4,2,1)_+1",
                "3 Qc=(bar4,1,2)_-1",
                "H=(1,2,2)_0",
            ],
            "renormalizable_superpotential": (
                "W0=sum_AB Y_AB L_A H R_B + y_m LA H RF, "
                "where L_A=(Q1,Q2,Q3,LF) and R_B=(Qc1,Qc2,Qc3,RA)"
            ),
        },
        "bulk_hypers": [
            {"name": "HLF", "rep": "16_+1", "eta0": "+", "etaL": "+", "zero_mode": "LF=(4,2,1)_+1"},
            {"name": "HLA", "rep": "bar16_-4", "eta0": "+", "etaL": "+", "zero_mode": "LA=(bar4,2,1)_-4"},
            {"name": "HRA", "rep": "16_-1", "eta0": "-", "etaL": "+", "zero_mode": "RA=(bar4,1,2)_-1"},
            {"name": "HRF", "rep": "bar16_+4", "eta0": "-", "etaL": "+", "zero_mode": "RF=(4,1,2)_+4"},
        ],
        "Spin10_source_wall_yL": {
            "boundary_chirals": [
                "STheta_0",
                "ThetaPlus_+3",
                "ThetaMinus_-3",
                "Delta_126,0",
                "DeltaBar_bar126,0",
            ],
            "specified_terms": [
                "kappa_F STheta(ThetaPlus ThetaMinus-v_F^2)",
                "lambda_L ThetaPlus HLF HLA",
                "lambda_R ThetaMinus HRA HRF",
            ],
            "missing_term": "A complete W_126 that selects and lifts the aligned SU(5)-singlet 126/bar126 branch",
        },
        "not_in_candidate": [
            "V40/V44 X, Zp, P/Pb, Psi, A, E, NDirac and Sc/Sbc/SigC/SigBc sectors",
            "the globally invalid naked (1,2,1) and (1,1,2) anomalons",
            "redundant Bplus/Bminus singlet shining hypermultiplets",
            "the inherited Z4R as an exact gauge symmetry",
            "a faithful Z9_F claim without a unit-charge line lattice",
        ],
    }


def exact_results(group: Mapping[str, Any], reconciled: Mapping[str, Any], locality: Mapping[str, Any], r_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": "E1",
            "result": "exact connected gauge group",
            "statement": "PS intersect SU5 inside Spin10 is S(U3xU2)=(SU3xSU2xU1)/Z6",
            "value": group["SM_global_form"]["connected_global_form"],
        },
        {
            "id": "E2",
            "result": "orbifold zero-mode index",
            "statement": "21 PS vectors survive before the boundary VEV; nine are lifted and 12 connected-SM vectors remain; no adjoint chiral zero mode",
            "value": group["zero_mode_count_after_all_boundary_VEVs"],
        },
        {
            "id": "E3",
            "result": "global representation repair",
            "statement": "V44 naked doublets fail the diagonal-Z2 quotient; all four V45 spinorial zero modes descend",
            "value": group["PS_global_representation_audit"]["original_V44_boundary_manifest_globally_valid"],
        },
        {
            "id": "E4",
            "result": "ordinary localized anomaly cancellation",
            "statement": "PS-wall boundary and bulk densities cancel componentwise in the displayed polynomial; all displayed Spin10-wall rows also vanish",
            "value": {
                "PS_boundary": reconciled["PS_wall"]["boundary_chirals"]["totals"],
                "PS_bulk": reconciled["PS_wall"]["bulk_hyper_density"]["totals"],
                "PS_combined": reconciled["PS_wall"]["combined_totals"],
                "Spin10_combined": reconciled["Spin10_wall"]["combined_totals"],
            },
        },
        {
            "id": "E5",
            "result": "projected exotic zero-mode rank",
            "statement": "The two source-wall bilinears give rank four and determinant mL^2 mR^2 when both boundary overlaps are nonzero",
            "value": reconciled["source_wall_mass_lifting"],
        },
        {
            "id": "E6",
            "result": "local orientation frontier",
            "statement": "No nonzero-orientation PS-U1F invariant occurs through degree 19; explicit degree-20 invariants exist with orientation +/-12",
            "value": locality["local_orientation_frontier"],
        },
        {
            "id": "E7",
            "result": "discrete-R obstruction",
            "statement": "Equal-level family-universal discrete-R universality forces both degree-20 oriented invariants to have W charge two",
            "value": r_audit["degree20_forcing_theorem"],
        },
    ]


def stage_ledger() -> list[dict[str, Any]]:
    return [
        {
            "stage": "S0",
            "status": "OPEN_WITH_KINEMATIC_CORE_CERTIFIED",
            "passed": "compact direct-product witness, orbifold parities, connected SM/Z6 intersection, honest zero-mode representations",
            "missing": "dynamically selected and fully massive 126/bar126 boundary-Higgs realization",
        },
        {
            "stage": "S1",
            "status": "OPEN_WITH_ORDINARY_LOCAL_POLYNOMIAL_CERTIFIED",
            "passed": "displayed perturbative gauge, mixed, cubic, gravitational and zero-mode Witten rows",
            "missing": "eta invariant, parity/global/bordism anomalies and discrete-R completion for the actual quotient",
        },
        {
            "stage": "S2",
            "status": "OPEN_WITH_PROJECTED_ZERO_MODE_RANK_CERTIFIED",
            "passed": "rank-four LF/LA/RA/RF overlap mass matrix for nonzero mL,mR",
            "missing": "complete KK determinant, 126 physical Hessian, coupled F/D/Kahler/radion vacuum",
        },
        {
            "stage": "S3",
            "status": "OPEN_WITH_OPERATOR_FRONTIER_AND_NO_GO_CERTIFIED",
            "passed": "degree-20 local frontier and four-source-unit pure-light charge-flow theorem",
            "missing": "orientation-zero ring, exact cross-wall/KK Wilson coefficients, proton and multinucleon rates",
        },
        {
            "stage": "S4",
            "status": "OPEN",
            "passed": "none promoted",
            "missing": "unification/thresholds, full spectrum, flavour/neutrinos, SUSY breaking, dark sector and cosmology",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {"gate": "G1", "closed": False, "advance": "One global-form/parity skeleton and its ordinary localized anomaly polynomial now exist.", "blocker": "Global eta/bordism, exact discrete symmetry and complete boundary action are missing."},
        {"gate": "G2", "closed": False, "advance": "Source and host are geometrically separated; redundant transport hypers were removed.", "blocker": "Allowed spinor-mediated nonlocal portals and the complete source spectrum are unmatched."},
        {"gate": "G3", "closed": False, "advance": "The isolated Theta source branch and an aligned conjugate 126 D-flat direction are available.", "blocker": "No complete coupled W/Kahler potential selects the branch and lifts every uneaten mode."},
        {"gate": "G4", "closed": False, "advance": "The minimal field core sharply reduces the mediation inventory.", "blocker": "Radion, SUSY breaking, mu/Bmu, soft vacuum and EWSB are absent."},
        {"gate": "G5", "closed": False, "advance": "No excluded V39 large-Yukawa dark benchmark is imported.", "blocker": "V45 has no specified dark sector or cosmological solution."},
        {"gate": "G6", "closed": False, "advance": "The exact KK boundary problem is now well posed.", "blocker": "Full KK determinant, thresholds, perturbative unification, RG evolution and pole spectrum are uncomputed."},
        {"gate": "G7", "closed": False, "advance": "The first local oriented invariant is degree 20 and pure-light nonlocal orientation needs four source-charge units.", "blocker": "Universal discrete-R symmetry forces the degree-20 W class; full Wilson matching and decay bounds are absent."},
        {"gate": "G8", "closed": False, "advance": "The PS wall admits a generic 4x4 Yukawa block plus one mirror Yukawa.", "blocker": "The old NDirac chain was deleted; no neutrino mechanism, three-family likelihood or withheld predictions exist."},
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_json(path) for name, path in INPUTS.items()}
    group = inputs["group_zero_modes"]
    wall = inputs["wall_forensic"]
    reconciled = inputs["reconciled_bulk"]
    locality = inputs["locality"]
    r_audit = inputs["discrete_r"]
    v44 = inputs["v44_terminal"]
    contract = candidate_contract()
    stages = stage_ledger()
    gates = gate_ledger()
    manifest = source_manifest()

    primitive_nonzero = [abs(q) for q in primitive_charge_table().values() if q]
    checks = {
        "all_input_core_hashes_verify": True,
        "v44_had_zero_closed_gates": v44["current_candidate"]["closed_gate_count"] == 0,
        "connected_SM_global_form_is_Z6_quotient": group["SM_global_form"]["kernel_order"] == 6,
        "four_dimensional_N1_and_no_adjoint_chiral": (
            group["orbifold_and_SUSY"]["SUSY_projection"]["surviving_four_dimensional_SUSY"] == "N=1"
            and group["zero_mode_count_after_all_boundary_VEVs"]["massless_adjoint_chiral_supermultiplets"] == 0
        ),
        "V44_global_representation_defect_is_real": not group["PS_global_representation_audit"]["original_V44_boundary_manifest_globally_valid"],
        "repaired_bulk_representations_are_honest": group["globally_honest_anomalon_repair"]["all_replacement_PS_representations_are_honest"],
        "PS_wall_ordinary_local_rows_vanish": all(value == 0 for value in reconciled["PS_wall"]["combined_totals"].values()),
        "Spin10_wall_ordinary_local_rows_vanish": all(value == 0 for value in reconciled["Spin10_wall"]["combined_totals"].values()),
        "ordinary_CS_not_required": not reconciled["inflow_and_parity"]["ordinary_wall_totals_require_CS_inflow"],
        "projected_exotic_mass_rank_is_four": reconciled["source_wall_mass_lifting"]["rank_if_mL_and_mR_nonzero"] == 4,
        "redundant_B_hypers_removed": (
            reconciled["reconciliation_decision"]["separate_singlet_shining_hypers_removed"]
            and locality["decision"]["separate_Bplus_Bminus_singlet_hypers"].startswith("REJECTED")
        ),
        "primitive_charge_normalization_is_faithful": math.gcd(*primitive_nonzero) == 1,
        "faithful_residual_is_Z3": contract["charge_normalization"]["Theta_breaking"] == "U(1)_F -> Z3_F",
        "degree20_oriented_invariants_exist": locality["decision"]["first_oriented_PS_U1F_invariant_degree"] == 20,
        "pure_light_charge_flow_needs_four_units": locality["decision"]["pure_light_nonlocal_minimum_source_charge_units"] == 4,
        "inherited_Z4R_is_not_exact": not r_audit["decision"]["inherited_Z4R_retained_as_exact"],
        "universal_R_cannot_forbid_degree20": not r_audit["decision"]["any_candidate_forbids_first_oriented_local_W_invariant"],
        "wall_forensic_selected_reduced_core": wall["decision"]["coherent_reduced_V45_field_core_selected"],
        "all_stages_fail_closed": all(row["status"] != "CLOSED" for row in stages),
        "all_eight_gates_open": len(gates) == 8 and all(not row["closed"] for row in gates),
        "all_required_sources_exist": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V45 master integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v45-new-physics-master-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "real_new_physics_obtained": True,
            "complete_theory_established": False,
            "empirically_validated": False,
            "full_gates_closed": 0,
            "full_gates_total": 8,
            "summary": (
                "V45 repairs the fatal V44 global-representation/locality mismatch and supplies one coherent "
                "5D Spin(10) skeleton with exact connected-SM group theory, wall-by-wall ordinary anomaly "
                "cancellation and conditional rank-four exotic zero-mode lifting. It remains a research "
                "candidate because global anomalies, the 126/KK vacuum, Wilson coefficients and all physical "
                "reconstruction are absent; moreover a universal discrete-R symmetry cannot remove the first "
                "degree-20 oriented superpotential class."
            ),
            "tests_mean": "deterministic validation of the encoded derivations, not validation by experiment or UV completion",
        },
        "authoritative_candidate": contract,
        "V44_defects_and_V45_repairs": [
            {
                "defect": "The V44 (1,2,1) and (1,1,2) anomalons are not representations of inherited PS/Z2_diag.",
                "repair": "Replace them by four parity-selected zero modes of bulk 16/bar16 hypers.",
            },
            {
                "defect": "Separating Theta from boundary anomalons made their written masses nonlocal.",
                "repair": "The same four spinor hypers reach y=L, so Theta 16 bar16 mass operators are local; no B+/- hypers are added.",
            },
            {
                "defect": "Integrated anomaly cancellation did not certify either orbifold wall.",
                "repair": "Parity-resolved ordinary anomaly densities cancel separately on the PS and Spin10 walls.",
            },
            {
                "defect": "Z9 was named although every displayed charge had a common factor three.",
                "repair": "Adopt primitive charges and the faithful residual Z3_F; a stronger line lattice is not assumed.",
            },
            {
                "defect": "The inherited Z4R was used as though it were an exact selector.",
                "repair": "Withdraw it: its mixed PS residues are nonuniversal, and the universal-R theorem forces the degree-20 W witness.",
            },
        ],
        "exact_results": exact_results(group, reconciled, locality, r_audit),
        "stage_ledger": stages,
        "gate_ledger": gates,
        "terminal_open_requirements": [
            "Choose and solve a complete source-wall 126/bar126 superpotential; compute eaten modes and the full physical Hessian.",
            "Compute the complete boundary-condition-shifted KK determinant and prove no additional massless/tachyonic mode.",
            "Fix the final Spin/global quotient and calculate eta, bordism, discrete and parity anomalies with quantized counterterms.",
            "Match every local and spinor-mediated nonlocal baryon/lepton/source-host operator to physical Wilson coefficients and bounds.",
            "Rebuild neutrino masses, mu/Bmu, SUSY breaking/radion stabilization, flavour, thresholds/RG, dark matter and cosmology in this same candidate.",
        ],
        "kill_or_continue_rule": (
            "Continue V45 only by solving the listed open requirements in this same field/parity manifest. "
            "Kill the candidate if the 126/KK spectrum, global anomaly, Wilson bounds, unification or physical "
            "likelihood fails for every controlled parameter region. Do not declare completion from the exact "
            "subchecks alone and do not import mutually inconsistent sectors from V40--V44."
        ),
        "primary_sources": [
            {"topic": "5D Spin10 orbifold parities and PS/SU5 intersection", "url": "https://arxiv.org/abs/hep-ph/0108139"},
            {"topic": "exact SM subgroup as SU5/PS intersection", "url": "https://arxiv.org/abs/2209.05088"},
            {"topic": "localized orbifold anomalies and inflow conditions", "url": "https://arxiv.org/abs/hep-th/0305024"},
            {"topic": "bulk spinors, boundary masses and 5D SO10 phenomenology", "url": "https://arxiv.org/abs/hep-ph/0603086"},
            {"topic": "discrete-R anomaly universality conventions", "url": "https://arxiv.org/abs/1102.3595"},
            {"topic": "unification warning for SO10-wall Higgs breaking", "url": "https://arxiv.org/abs/hep-ph/0506130"},
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "input_core_hashes": {name: payload["core_sha256"] for name, payload in inputs.items()},
        "source_manifest": manifest,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    verdict = report["scientific_verdict"]
    candidate = report["authoritative_candidate"]
    result_rows = "\n".join(
        f"| {row['id']} | {row['result']} | {row['statement']} |" for row in report["exact_results"]
    )
    stage_rows = "\n".join(
        f"| {row['stage']} | {row['status']} | {row['passed']} | {row['missing']} |" for row in report["stage_ledger"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | open | {row['advance']} | {row['blocker']} |" for row in report["gate_ledger"]
    )
    repairs = "\n".join(
        f"{index}. **Defect:** {row['defect']}  **V45 repair:** {row['repair']}"
        for index, row in enumerate(report["V44_defects_and_V45_repairs"], 1)
    )
    open_items = "\n".join(f"{index}. {item}" for index, item in enumerate(report["terminal_open_requirements"], 1))
    hypers = "\n".join(
        f"- `{row['name']}: {row['rep']}`, intrinsic parities `({row['eta0']},{row['etaL']})`, zero mode `{row['zero_mode']}`"
        for row in candidate["bulk_hypers"]
    )
    return f"""# V45 new-physics master audit

Status: `{report['status']}`

## Verdict

{verdict['summary']}

This is a **real architecture-level advance**, not a complete theory and not
an experimental validation.  Full predictive gates closed: **0/8**.

## The one reconciled candidate

Use `{candidate['spacetime']}` with bulk
`{candidate['bulk_group']}`.  The `y=0` wall carries three `Q`, three `Qc` and
one bidoublet `H`.  The `y=L` Spin(10) wall carries the neutral source driver,
`Theta+/-`, and a provisional neutral `126+bar126` sector.

The faithful primitive charges are
`Q,Qc,HLF,HLA,HRA,HRF,Theta+,Theta- = +1,-1,+1,-4,-1,+4,+3,-3`.
Thus the displayed local spectrum realizes `U(1)F -> Z3F`; V45 does not assume
an invisible unit-charge line lattice to rename this `Z9`.

The four bulk spinors are:

{hypers}

At `y=L`, `ThetaPlus HLF HLA` and `ThetaMinus HRA HRF` are ordinary local
Spin(10) invariants.  They replace the previously nonlocal anomalon masses;
separate `Bplus/Bminus` shining hypers are deleted.

## What was repaired

{repairs}

## Exact results

| ID | Result | Certified statement |
|---|---|---|
{result_rows}

The PS-wall ordinary anomaly vectors are exactly opposite:
boundary `(SU4^3, F-SU2L^2, F-SU2R^2, F-SU4^2, F^3, grav-F)` equals
`(0,+36,-36,0,0,0)` in the V40 normalization, while the four bulk hypers give
`(0,-36,+36,0,0,0)`.  Every displayed ordinary Spin(10)-wall row also sums to
zero.  No ordinary Chern--Simons inflow is required for these rows.

The projected exotic mass matrix in `(LF,LA,RA,RF)` is two off-diagonal
blocks, with `det M = mL^2 mR^2` and rank four if both source-wall overlaps
are nonzero.  This is not the determinant of the full KK tower.

## Operator boundary and discrete-R no-go

For local oriented fields, U(1)F neutrality and the SU(4) centre imply the
first nonzero orientation is `+/-12`; no such invariant exists through degree
19 and explicit degree-20 invariants exist.  Pure-light nonlocal charge flow
obeys `4 k + 3 m = 0`, so its first nonzero class needs twelve net oriented
fields and four source-charge units.  This counts charge flow, not four
independent exponential propagators.

The inherited `Z4R` cannot be used to postpone this frontier: its mixed
`(SU4,SU2L,SU2R)` residues are `(0,1,1) mod 2`.  More generally, allowing the
Yukawa and both Theta mass terms while demanding equal-level universal
discrete-R anomalies forces the explicit degree-20 oriented invariants to
have R charge two.  An ordinary symmetry-preserving massive vectorlike packet
has trivial mixed-R shift and cannot repair that theorem.  G7 therefore stays
open.

## S0--S4 research stages

| Stage | Status | Exact progress | Missing closure object |
|---|---|---|---|
{stage_rows}

## G1--G8 ledger

| Gate | Status | V45 advance | Why it remains open |
|---|---|---|---|
{gate_rows}

## Required next calculations

{open_items}

**Stopping rule:** {report['kill_or_continue_rule']}

Repository tests certify the encoded arithmetic and artifact integrity only;
they do not certify nature, a UV completion, or a fitted likelihood.

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
        raise RuntimeError("V45 master JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V45 master Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V45_NEW_PHYSICS_MASTER_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
