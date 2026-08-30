#!/usr/bin/env python3
"""Fail-closed V40 G1 ultraviolet-route contract.

V39 proved that the displayed inverse Pati--Salam boundary packet cannot be
trivially gapped by an ordinary local superpotential while PS x Z66 is
unbroken.  This module does not pretend that an anomaly EFT is a UV
completion.  It records the two remaining *classes* of escape routes and the
irreducible physical data that a candidate must supply before G1 can be
promoted.

The contract deliberately distinguishes (i) a new four-dimensional,
gauge-derived selector and (ii) a five-dimensional inflow completion with a
microscopic anomalous boundary theory.  A list of charges, a formal
Chern--Simons term, or a low-energy anomaly congruence alone fails both
contracts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import susy_v38_g1_uv_completion_audit as v38
import susy_v39_g1_mirror_gap_audit as v39


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V40_G1_UV_ROUTE_CONTRACT.json"
REPORT_MD = ROOT / "SUSY_V40_G1_UV_ROUTE_CONTRACT.md"

SOURCE_FILES = (
    "susy_v40_g1_uv_route_contract.py",
    "test_susy_v40_g1_uv_route_contract.py",
    "susy_v38_g1_uv_completion_audit.py",
    "susy_v39_g1_mirror_gap_audit.py",
    "SUSY_V38_G1_UV_COMPLETION_AUDIT.json",
    "SUSY_V39_G1_MIRROR_GAP_AUDIT.json",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def requirement(
    identifier: str, new_physical_data: str, acceptance_evidence: str, why_irreducible: str
) -> dict[str, str]:
    return {
        "id": identifier,
        "new_physical_data": new_physical_data,
        "acceptance_evidence": acceptance_evidence,
        "why_irreducible": why_irreducible,
    }


def four_dimensional_route() -> dict[str, Any]:
    """Necessary data for a new 4D gauge-derived discrete construction.

    V38 is intentionally treated as a conditional no-go, not as a theorem
    against every possible 4D theory.  A new charge lattice, a multi-axion GS
    lattice, or a different selector can evade its assumptions, but each is
    new input and must be supplied in one microscopic candidate.
    """

    return {
        "route_id": "V40_4D_GAUGE_DERIVED_SELECTOR_REBUILD",
        "classification": "conditional viable research route; no supplied microscopic candidate",
        "can_close_G1_from_present_inputs": False,
        "retains_exact_V39_conventional_Z66_parent": False,
        "reason_existing_V39_parent_cannot_be_reused": (
            "V38 computes the V37 lifted mixed U(1)X-PS^2 row as (-8,-8,-8), nonzero modulo "
            "66 and modulo 33.  Under its assumptions (PS unbroken at the threshold, all breaking "
            "VEVs in 66 Z, and ordinary full-rank symmetry-preserving masses), heavy thresholds "
            "shift that row by zero modulo the same tests.  A single ordinary compact axion would "
            "require 66 k = 8 and therefore also fails."
        ),
        "allowed_architecture_changes": [
            "replace the Z66 action by a different gauge-derived residual selector while re-solving the full operator ring",
            "change the integral parent charge lattice and complete chiral threshold spectrum",
            "supply a quantized multi-axion/Green--Schwarz lattice or another microscopic anomaly mechanism, including its periods and levels",
            "change the boundary/UV realization so that at least one stated V38 no-go assumption is explicitly not applicable",
        ],
        "minimum_new_physical_data": [
            requirement(
                "4D-1-parent-global-form-and-lattice",
                "The full compact UV gauge group including all quotients, a primitive integral charge lattice, and the normalization of every U(1), axion, and R generator.",
                "A machine-readable generator-action table whose exponentiation gives the claimed remnant Z_N (and the correct fermionic/Spin^Z4R action).",
                "Whether a Higgsed U(1) leaves Z_N and whether a purported GS coefficient is integral are lattice statements; low-energy residues alone do not determine them.",
            ),
            requirement(
                "4D-2-complete-chiral-spectrum",
                "Every UV chiral multiplet and heavy threshold, with Pati--Salam representation, multiplicity, charge, and chirality.",
                "Exact perturbative anomaly polynomial plus discrete/global anomaly calculation before and after Higgsing, with all rows zero or canceled by a stated quantized mechanism.",
                "Heavy fermions can carry the anomaly information that is invisible in a light-field-only calculation.",
            ),
            requirement(
                "4D-3-higgsing-vacuum-and-thresholds",
                "A supersymmetric Higgs/axion sector, complete superpotential and Kähler/gauge-kinetic data sufficient to establish its physical VEV branch and every heavy mass matrix.",
                "F/D equations, gauge quotient, mass determinants, and threshold matching that prove the exact selector remains unbroken and the desired light V39/V40 spectrum is obtained.",
                "A charge list cannot show that unwanted chiral states are actually gapped without breaking the claimed residual symmetry.",
            ),
            requirement(
                "4D-4-quantized-anomaly-mechanism",
                "If anomalies are canceled by Green--Schwarz/Stueckelberg data rather than an anomaly-free spectrum: axion periods, transformation lattice, Wess--Zumino couplings, and integer level matrix.",
                "A gauge-variation calculation of the complete action, including mixed PS, Abelian, gravitational, and Z4R/Spin terms, and a global-anomaly/bordism check for the actual gauge quotient.",
                "A formal continuous coefficient or a parity repair is not a compact, quantized anomaly-canceling action.",
            ),
            requirement(
                "4D-5-all-order-visible-matching",
                "A UV-to-visible map for normalized superpotential, Kähler, gauge-kinetic, and soft operators after integrating out every threshold.",
                "An all-order operator-ring computation and Wilson-coefficient matching which reproduce the claimed selector while excluding every forbidden class, not merely the lowest monomials.",
                "G1 is a statement about the actual UV theory reproducing the visible EFT, not only about anomaly arithmetic.",
            ),
            requirement(
                "4D-6-microscopic-regulator-and-reproducibility",
                "A complete local microscopic action or another specified UV regulator from which the above spectrum, couplings, and quantization are derived.",
                "Versioned source, spectrum/threshold manifests, independent executable checks, and a physical-branch matching calculation.",
                "Fitted charge tables or unconstrained coefficients would define a new EFT but not establish a UV completion.",
            ),
        ],
        "promotion_rule": (
            "Promote G1 through this route only if one *single* candidate provides all six data packets and the exact "
            "residual selector/operator map is matched.  Do not combine anomaly cancellation from one model with vacuum "
            "or Yukawa data from another."
        ),
        "source_basis": [
            "https://arxiv.org/abs/hep-ph/9210211",
            "https://arxiv.org/abs/1212.4371",
            "https://arxiv.org/abs/1808.02881",
        ],
    }


def five_dimensional_route() -> dict[str, Any]:
    """Necessary data for a 5D inflow completion with a gapped far boundary."""

    return {
        "route_id": "V40_5D_INFLOW_AND_MICROSCOPIC_BOUNDARY_COMPLETION",
        "classification": "conditional viable research route; V38 remains only an anomaly-EFT scaffold",
        "can_close_G1_from_present_inputs": False,
        "what_the_present_interval_packet_establishes": (
            "V38 supplies equal-and-opposite continuous boundary anomaly rows.  Thus a globally vanishing localized "
            "anomaly distribution can in principle be represented by quantized 5D inflow.  It does not supply a physical "
            "far-wall gap or a UV regulator."
        ),
        "why_inflow_alone_is_insufficient": (
            "V39 independently finds three net opposite Pati--Salam families and the far-wall mixed selector residue "
            "(+8,+8,+8).  A trivial local N=1 wall with unbroken PS x Z66 therefore cannot be fully gapped.  An eta "
            "invariant or Chern--Simons symbol accounts for anomaly variation; it does not by itself define the missing "
            "boundary degrees of freedom or their gapped dynamics."
        ),
        "minimum_new_physical_data": [
            requirement(
                "5D-1-bulk-global-data-and-boundary-conditions",
                "The compact 5D gauge group/global quotient, tangential Spin/Spin^Z4R structure, interval or orbifold geometry, complete bulk multiplets, and boundary conditions/projections.",
                "A regulated KK spectrum and explicit boundary chiral indices whose zero-mode action is the intended V40 visible theory.",
                "The quotient and boundary projection determine both global anomalies and which localized modes actually exist.",
            ),
            requirement(
                "5D-2-quantized-inflow-functional",
                "The full quantized 5D Chern--Simons/eta/Green--Schwarz functional, including the U(1)X-PS^2, Abelian, gravitational, and discrete-R pieces.",
                "A gauge-variation/descent calculation showing cancellation locally on each boundary and globally, with integer levels fixed by the stated lattice and regulator.",
                "Globally vanishing local anomalies can be canceled by 5D CS/eta inflow, but the formal coefficient is not enough without its quantization and regulator.",
            ),
            requirement(
                "5D-3-microscopic-far-boundary-theory",
                "An explicit 3+1D nontrivial boundary topological order or symmetry-extension construction coupled to PS x Z4R x Z_N, including all emergent gauge/higher-form fields and the symmetry action.",
                "A Lagrangian/state-sum/UV construction plus an anomaly calculation proving that its anomaly exactly equals the mirror residue while its local excitations are gapped and it does not break the selector.",
                "V39 excludes the alternative of a unique trivial local superpotential gap.  Naming a topological order without its symmetry-enriched anomaly data is not a completion.",
            ),
            requirement(
                "5D-4-global-anomaly-and-bordism",
                "The full bordism/invertible-field-theory classification for the actual Spin/Z4R structure, Pati--Salam diagonal quotient, selector, gauginos, gravitino, axions, and boundary topological sector.",
                "A calculation that the combined bulk-plus-both-boundaries partition function is well-defined on every allowed background, not only perturbatively around the trivial bundle.",
                "The V39 Witten-doublet check is necessary but does not calculate the required product/global anomaly.",
            ),
            requirement(
                "5D-5-microscopic-bulk-regulator",
                "A specified microscopic completion or regulator of the nonrenormalizable 5D bulk theory that derives its levels and defect spectrum.",
                "A UV construction with its consistency conditions and a map from microscopic states to the 5D action/eta phase.",
                "A 5D anomaly EFT cannot establish the UV spectrum, level quantization, or the existence of the required topological boundary sector.",
            ),
            requirement(
                "5D-6-threshold-and-visible-matching",
                "The KK/twisted/boundary threshold determinants and the matching of all visible normalized operators, gauge couplings, and residual symmetry actions.",
                "A component-level UV-to-4D matching computation showing no unwanted massless mirror state and no selector-breaking nonlocal operator is induced.",
                "Even a consistent anomaly system fails G1 if its compactification does not reproduce the claimed 4D EFT.",
            ),
        ],
        "promotion_rule": (
            "Promote G1 through this route only after an explicit anomalous but symmetry-preserving gapped far-boundary "
            "theory and the complete bulk-plus-boundary partition function are constructed.  The V38 interval by itself, or "
            "a postulated eta-invariant, is insufficient."
        ),
        "source_basis": [
            "https://arxiv.org/abs/1909.08775",
            "https://arxiv.org/abs/hep-th/0305024",
            "https://arxiv.org/abs/1910.04962",
        ],
    }


def build_report() -> dict[str, Any]:
    v38_report = v38.build_report()
    v39_report = v39.build_report()
    route_4d = four_dimensional_route()
    route_5d = five_dimensional_route()
    manifest = source_manifest()
    checks = {
        "v38_same_selector_conventional_4d_parent_is_excluded": (
            v38_report["gate_decision"][
                "ordinary_4D_Higgsed_U1X_solution_exists_under_theorem_assumptions"
            ]
            is False
        ),
        "v39_trivial_mirror_gap_is_excluded": (
            v39_report["gate_decision"]["ordinary_local_mirror_wall_gap_exists"] is False
        ),
        "four_dimensional_route_requires_an_architecture_change": (
            route_4d["retains_exact_V39_conventional_Z66_parent"] is False
        ),
        "both_routes_are_open_research_classes_not_completed_candidates": (
            route_4d["can_close_G1_from_present_inputs"] is False
            and route_5d["can_close_G1_from_present_inputs"] is False
        ),
        "both_routes_have_explicit_minimum_data_contracts": (
            len(route_4d["minimum_new_physical_data"]) == 6
            and len(route_5d["minimum_new_physical_data"]) == 6
        ),
        "source_manifest_complete": all(row["exists"] for row in manifest),
        "full_G1_remains_fail_closed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v40-g1-uv-route-contract-v1",
        "status": "V40_G1_UV_ROUTE_CONTRACT__TWO_CONDITIONAL_ARCHITECTURES__NO_PRESENT_INPUT_CLOSES_G1",
        "question_answered": (
            "There are two coherent ways to continue beyond V39, but neither can be promoted from the present inputs. "
            "The 4D route must change the excluded conventional selector realization or add a fully quantized new anomaly "
            "mechanism; the 5D route must construct the missing microscopic anomalous gapped boundary theory."
        ),
        "v39_fixed_facts": {
            "V38_visible_lifted_U1X_PS_squared_doubled_row": [-8, -8, -8],
            "V39_mirror_lifted_U1X_PS_squared_doubled_row": [8, 8, 8],
            "V39_mirror_unpaired_opposite_PS_families": 3,
            "same_selector_ordinary_4D_parent_excluded": True,
            "trivial_local_mirror_gap_excluded": True,
        },
        "route_comparison": {
            "four_dimensional_gauge_derived_selector_rebuild": route_4d,
            "five_dimensional_inflow_and_microscopic_boundary_completion": route_5d,
        },
        "minimal_shared_promotion_standard": [
            "one internally consistent microscopic candidate, not an assembly of facts from unrelated EFTs",
            "quantized anomaly/global-structure data rather than anomaly congruences alone",
            "a physical vacuum and all required heavy/boundary mass or topological sectors",
            "reproducible UV-to-visible operator and threshold matching",
        ],
        "gate_decision": {
            "G1_closed": False,
            "a_4D_route_exists_in_principle": True,
            "a_5D_route_exists_in_principle": True,
            "either_route_is_closed_from_present_inputs": False,
            "same_V39_conventional_4D_Z66_route_is_available": False,
            "V38_5D_inflow_EFT_alone_is_a_microscopic_completion": False,
        },
        "literature": {
            "heavy_threshold_and_discrete_anomaly_data": "https://arxiv.org/abs/hep-ph/9210211",
            "discrete_R_and_GS_scope": "https://arxiv.org/abs/1212.4371",
            "discrete_anomaly_global_structure": "https://arxiv.org/abs/1808.02881",
            "eta_inflow": "https://arxiv.org/abs/1909.08775",
            "localized_orbifold_anomaly_and_5D_CS_scope": "https://arxiv.org/abs/hep-th/0305024",
            "gapped_boundary_anomaly_obstruction": "https://arxiv.org/abs/1910.04962",
        },
        "source_manifest": manifest,
        "checks": checks,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    comparison = report["route_comparison"]
    route_4d = comparison["four_dimensional_gauge_derived_selector_rebuild"]
    route_5d = comparison["five_dimensional_inflow_and_microscopic_boundary_completion"]

    def requirements_block(route: Mapping[str, Any]) -> list[str]:
        rows: list[str] = []
        for item in route["minimum_new_physical_data"]:
            rows.extend(
                [
                    f"- `{item['id']}` — {item['new_physical_data']}",
                    f"  Acceptance: {item['acceptance_evidence']}",
                ]
            )
        return rows

    lines = [
        "# SUSY V40 G1 ultraviolet-route contract",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Full G1 closed: **no**.",
        "",
        "## Decision",
        "",
        report["question_answered"],
        "",
        "V39 proves two limits that must not be patched over: the conventional 4D parent preserving the existing Z66 selector has mixed PS residue `(-8,-8,-8)` and is excluded under its stated threshold assumptions; the inverse boundary has residue `(+8,+8,+8)` plus three net opposite PS families, so it has no trivial symmetry-preserving local gap.  These are not proofs that every 4D or 5D completion is impossible.",
        "",
        "## Route A — four-dimensional gauge-derived selector rebuild",
        "",
        "This is the more conventional route, but it cannot reuse the excluded V39 ordinary Z66 parent.  It must provide a new residual selector, changed integral lattice/threshold spectrum, or a genuinely quantized multi-axion/GS mechanism.  No such microscopic candidate is present.",
        "",
        "Minimum new data:",
        "",
        *requirements_block(route_4d),
        "",
        f"Promotion rule: {route_4d['promotion_rule']}",
        "",
        "## Route B — five-dimensional inflow plus a microscopic boundary completion",
        "",
        "The V38 equal-and-opposite boundary rows make a 5D anomaly-EFT sensible, but inflow is only the anomaly-variation account.  The far wall cannot be erased by an ordinary mass superpotential.  This route therefore needs an explicit symmetry-preserving, anomalous gapped boundary topological theory and its microscopic origin.",
        "",
        "Minimum new data:",
        "",
        *requirements_block(route_5d),
        "",
        f"Promotion rule: {route_5d['promotion_rule']}",
        "",
        "## Comparison",
        "",
        "A 4D rebuild can be genuinely closed if one complete anomaly-free or quantized-GS microscopic model supplies the entire spectrum, vacuum, and matching data.  A 5D construction can be genuinely closed if it supplies the entire quantized bulk-plus-boundary system, including a real gapped anomalous boundary theory.  Neither closure follows from the V39 source, its anomaly coefficients, or its 5D eta-inflow scaffold.",
        "",
        "The relevant principles are that heavy thresholds cannot generally be dropped from discrete-anomaly accounting ([Ibáñez](https://arxiv.org/abs/hep-ph/9210211)); discrete R/GS arithmetic requires the actual nonlinear fields and couplings ([Dine--Monteux](https://arxiv.org/abs/1212.4371)); eta invariants furnish a nonperturbative inflow description ([Witten--Yonekura](https://arxiv.org/abs/1909.08775)); and a symmetry-preserving gapped boundary can itself be obstructed by its anomaly ([Córdova--Ohmori](https://arxiv.org/abs/1910.04962)).  In 5D orbifolds, Chern--Simons/Green--Schwarz inflow addresses appropriate localized, globally vanishing anomalies but imposes strong spectrum constraints ([von Gersdorff--Quirós](https://arxiv.org/abs/hep-th/0305024)).",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: Mapping[str, Any]) -> bool:
    return (
        REPORT_JSON.is_file()
        and REPORT_MD.is_file()
        and REPORT_JSON.read_text(encoding="utf-8") == json.dumps(report, indent=2, sort_keys=True) + "\n"
        and REPORT_MD.read_text(encoding="utf-8") == render_markdown(report)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    valid = report["n_failed"] == 0 and (not args.check or check_outputs(report))
    print("V40_G1_UV_ROUTE_CONTRACT " + ("PASS" if valid else "FAIL"))
    print(report["core_sha256"])
    print(json.dumps(report["gate_decision"], sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
