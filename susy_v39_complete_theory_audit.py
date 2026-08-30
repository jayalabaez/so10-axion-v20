#!/usr/bin/env python3
"""Fail-closed integration audit for the redesigned V39 theory candidate.

V39 is allowed to record exact advances and exact obstructions, but this
integrator never promotes a phenomenological gate merely because a parameter
was fitted or a missing microscopic sector could in principle be invented.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V39_COMPLETE_THEORY_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V39_COMPLETE_THEORY_AUDIT.md"

INPUT_PATHS = {
    "v38": ROOT / "SUSY_V38_COMPLETE_THEORY_AUDIT.json",
    "g1": ROOT / "SUSY_V39_G1_MIRROR_GAP_AUDIT.json",
    "soft": ROOT / "SUSY_V39_SOFT_BOUNDARY_AUDIT.json",
    "g5": ROOT / "SUSY_V39_G5_SECLUDED_FREEZEOUT_CERTIFICATE.json",
    "g7g8": ROOT / "SUSY_V39_G7_G8_ARCHITECTURE.json",
}

SOURCE_FILES = (
    "susy_v39_complete_theory_audit.py",
    "test_susy_v39_complete_theory_audit.py",
    "susy_v39_g1_mirror_gap_audit.py",
    "susy_v39_soft_boundary_audit.py",
    "susy_v39_g5_freezein_cosmology.py",
    "susy_v39_g5_secluded_freezeout.py",
    "susy_v39_g7_g8_architecture.py",
    "SUSY_V39_SARAH_RGE_ATTESTATION.json",
    "SUSY_V39_Z3_FORMAL_SOFT_RGE_ATTESTATION.json",
    "models/PSZ4RZ5610Z3SUSYV39/PSZ4RZ5610Z3SUSYV39.m",
    "tools/derive-susy-v33-ps-rges.wls",
    "tools/validate-susy-v39-baryon-repair.wls",
    ".github/workflows/susy-v39-complete-theory-audit.yml",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, path in INPUT_PATHS.items():
        if not path.is_file():
            raise RuntimeError(f"required V39 input is missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"required V39 input is not an object: {path.name}")
        core = payload.get("core_sha256")
        if not isinstance(core, str) or canonical_sha(payload) != core:
            raise RuntimeError(f"required V39 input checksum does not verify: {path.name}")
        loaded[name] = payload
    return loaded


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def gates(inputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    g1 = inputs["g1"]
    soft = inputs["soft"]
    g5 = inputs["g5"]
    g7g8 = inputs["g7g8"]
    selector = g7g8["V39_selector_and_necessary_anomaly_audit"]
    g7_status = next(row for row in g7g8["gate_statuses"] if row["gate"] == "G7")
    g8_status = next(row for row in g7g8["gate_statuses"] if row["gate"] == "G8")
    beta_counts = soft["live_soft_RGE"]["beta_counts"]
    freeze = g5["benchmark"]["freezeout_boltzmann_solution"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "advance": (
                "The ordinary local supersymmetric mirror-wall gap is now excluded twice: the inverse wall has "
                "three unpaired opposite PS families and mixed U(1)X-PS^2 residue (+8,+8,+8). The first local "
                "mass witness breaks Z66 to Z2; the correct PS quotient passes the elementary Witten tests."
            ),
            "blocker": "; ".join(g1["required_for_G1_promotion"]),
        },
        {
            "gate": "G2",
            "closed": False,
            "advance": (
                "The active split-six source initializes and has a live supersymmetric two-loop RGE system; its "
                "formal-soft mirror contains %s scalar-mass beta rows." % beta_counts["soft_scalar_mass"]
            ),
            "blocker": (
                "No stabilized broken-phase numerical point, component mass matrices, self energies, mixings, "
                "pole solution, or covariance matrix is derived."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "advance": (
                "The canonical equal-conjugate F/D branch survives the split-six source-level redesign, and a "
                "sequestered gauge-only soft trajectory is explicit."
            ),
            "blocker": (
                "The Kähler and gauge-kinetic functions, singlet soft/tadpole sector, competing vacua, bounce "
                "actions, finite-temperature history, and cosmological vacuum selection are absent."
            ),
        },
        {
            "gate": "G4",
            "closed": False,
            "advance": (
                "A transient formal-soft two-loop system and a positive gauge-only 5D gaugino-mediation witness "
                "exist for every PS-charged chiral multiplet of the active V39 source."
            ),
            "blocker": (
                "All exact singlets remain unlifted at gauge-only order; no microscopic singlet mediation, "
                "mu/Bmu solution, electroweak vacuum, threshold matching, or collider likelihood is specified."
            ),
        },
        {
            "gate": "G5",
            "closed": False,
            "advance": (
                "The six-field Z170 cascade has compatible active-V39 Z3 charges and passes the listed pure/cross "
                "residue plus selector/quality checks; the corrected "
                "thermal relic ODE provides an explicit low-energy stress test (Omega_D h^2=%0.6g at the fitted point)."
                % freeze["Omega_h2"]
            ),
            "blocker": " ".join(
                g5["promotion"]["hard_fail_closed_blockers"]
                + g5["promotion"]["not_predictive_because"]
            ),
        },
        {
            "gate": "G6",
            "closed": False,
            "advance": (
                "The active V39 declared source and its formal-soft mirror both complete live two-loop SARAH RGE "
                "derivations; the exact one-loop PS coefficients are (2,5,9), and a 5D boundary trajectory is solved."
            ),
            "blocker": (
                "The boundary is an ansatz, not a derived hidden sector; individual PS/KK thresholds, Abelian mixing "
                "when active, Wilson matching, a physical soft trajectory, and uncertainty propagation are absent."
            ),
        },
        {
            "gate": "G7",
            "closed": False,
            "advance": (
                "The split-six Z3 local block is live source code: all 32 retained W terms are neutral, while all four "
                "local X/Zp Q^4/Qc^4 sources are forbidden with charges (1,2,1,2). The full-ring audit also "
                "exhibits the allowed degree-nine X/Zp (Qc Sbc)^4 canonical-VEV dressing, so the limitation is explicit."
            ),
            "blocker": "; ".join(g7_status["still_required"]),
            "local_sources_forbidden": selector["all_four_local_sources_forbidden"],
        },
        {
            "gate": "G8",
            "closed": False,
            "advance": "; ".join(g8_status["landed"]),
            "blocker": "; ".join(g8_status["still_required"]),
            "nonidentifiability_witness": g8_status["nonidentifiability_witness"],
        },
    ]


def report() -> dict[str, Any]:
    inputs = load_inputs()
    gate_rows = gates(inputs)
    closed_count = sum(bool(row["closed"]) for row in gate_rows)
    g1 = inputs["g1"]
    soft = inputs["soft"]
    g5 = inputs["g5"]
    g7g8 = inputs["g7g8"]
    selector = g7g8["V39_selector_and_necessary_anomaly_audit"]
    integrity = {
        "all_required_report_cores_verify": True,
        "v38_baseline_had_zero_closed_gates": inputs["v38"]["established_full_predictive_closed_count"] == 0,
        "g1_trivial_mirror_gap_no_go_verified": g1["gate_decision"]["ordinary_local_mirror_wall_gap_exists"] is False,
        "active_V39_declared_and_formal_soft_two_loop_RGEs_succeeded": (
            soft["live_soft_RGE"]["two_loop_succeeded"] is True
            and soft["live_soft_RGE"]["declared_source_two_loop_succeeded"] is True
        ),
        "active_V39_one_loop_PS_coefficients_are_2_5_9": (
            soft["live_soft_RGE"]["one_loop_gauge_coefficients_input_form"]
            == ["2*g4^3", "5*gL^3", "9*gR^3"]
        ),
        "g5_remains_fail_closed": g5["promotion"]["G5_closed"] is False,
        "g5_corrected_candidate_not_promoted": g5["promotion"]["candidate_passes_its_quantitative_proxies"] is False,
        "g5_displayed_point_has_PQ_scale_UV_blocker": (
            g5["benchmark"]["constraints"]["one_loop_lambda_running"]["pole_below_fPQ"] is True
        ),
        "g5_dark_extension_is_compatible_with_listed_active_V39_Z3_checks": (
            g5["exact_symmetry_and_quality"]["all_terms_active_V39_Z3_neutral"] is True
            and g5["exact_symmetry_and_quality"]["active_V39_Z3_dark_anomaly_increment"]["all_listed_increments_vanish"] is True
        ),
        "g7_four_local_sources_forbidden": selector["all_four_local_sources_forbidden"] is True,
        "g7_degree9_Qc4_dressing_counterexample_verified": (
            g7g8["explicit_Qc4_PSVev_dressing_witness"]["both_selectors_allow_both_operators"] is True
        ),
        "active_V39_quality_lattice_reenumerated_to_W33_K32": (
            g7g8["canonical_branch_and_PQ_quality_scope"]["fresh_V39_charge_lattice_enumeration"]["superpotential"]["first_breaking_degree"] == 33
            and g7g8["canonical_branch_and_PQ_quality_scope"]["fresh_V39_charge_lattice_enumeration"]["Kahler"]["first_breaking_degree"] == 32
        ),
        "g7_g8_remain_fail_closed": all(not row["full_gate_closed"] for row in g7g8["gate_statuses"]),
        "no_full_gate_promoted": closed_count == 0,
    }
    data: dict[str, Any] = {
        "schema": "susy-v39-complete-theory-audit-v1",
        "status": "V39_MAXIMAL_FAIL_CLOSED_REDESIGN__EXACT_NO_GOS_AND_SOURCE_REPAIRS_LANDED__ZERO_OF_EIGHT_FULL_GATES_CLOSED",
        "active_model": "PSZ4RZ5610Z3SUSYV39",
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": closed_count,
        "integrity_checks": integrity,
        "gate_ledger": gate_rows,
        "what_V39_actually_settles": [
            "A conventional local supersymmetric mirror wall cannot trivially gap the V38 inverse anomaly packet while preserving PS x Z66.",
            "The active split-six Z3 source removes the four immediate driver-dressed Q^4/Qc^4 monomials that defeated V37, but an explicit degree-nine Qc4 dressing shows it is not full baryon protection.",
            "The redesigned 21-field source and a transient formal-soft mirror have live two-loop RGE attestations; gauge-only gaugino mediation lifts PS-charged fields but not the singlet sector.",
            "The residual Z170 dark cascade admits quantitative low-energy Boltzmann tests, but the tested point does not supply its own perturbative PQ-scale UV completion or component spectrum.",
        ],
        "terminal_assessment": {
            "reason_theory_is_not_finished": (
                "The remaining objects are independent microscopic data, not algebraic consequences of the supplied source: "
                "boundary topological order/UV completion, Kähler and SUSY-breaking functions, stabilized vacuum and pole "
                "spectrum, full Wilson/operator matching, reheating/PQ history, and flavour tensors/likelihood."
            ),
            "why_numbers_are_not_inserted": (
                "Choosing these missing functions or fitting benchmarks would define additional theories; it would not derive "
                "the requested complete theory from V39."
            ),
            "strongest_honest_classification": (
                "A reproducible research EFT with exact selector/no-go results and calculational scaffolds, not an established complete predictive theory."
            ),
        },
        "promotion_contract": {
            "G1": g1["required_for_G1_promotion"],
            "G2": ["derive a stabilized broken phase and a full numerical pole spectrum with covariance"],
            "G3": ["supply microscopic Kähler/gauge-kinetic/SUSY-breaking data and audit all vacua and cosmological selection"],
            "G4": ["derive singlet mediation and mu/Bmu, then demonstrate radiative EWSB with threshold and collider likelihoods"],
            "G5": g5["promotion"]["next_required_calculations"],
            "G6": ["derive physical boundaries and individual thresholds/Wilsons, evolve the full system, and propagate uncertainties"],
            "G7": g7_status_contract(g7g8),
            "G8": g8_status_contract(g7g8),
        },
        "primary_sources": [
            "https://arxiv.org/abs/1909.08775",
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/1910.04962",
            "https://arxiv.org/abs/0808.3598",
            "https://arxiv.org/abs/0803.1758",
            "https://arxiv.org/abs/0909.2863",
            "https://arxiv.org/abs/2211.02054",
            "https://arxiv.org/abs/0911.1120",
            "https://arxiv.org/abs/1807.06209",
            "https://arxiv.org/abs/1807.06211",
        ],
        "source_manifest": source_manifest(),
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def g7_status_contract(g7g8: Mapping[str, Any]) -> list[str]:
    return next(row for row in g7g8["gate_statuses"] if row["gate"] == "G7")["still_required"]


def g8_status_contract(g7g8: Mapping[str, Any]) -> list[str]:
    return next(row for row in g7g8["gate_statuses"] if row["gate"] == "G8")["still_required"]


def markdown(data: Mapping[str, Any]) -> str:
    lines = [
        "# SUSY V39 complete-theory audit",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Active model: `{data['active_model']}`.",
        "",
        f"Full predictive gates closed: **{data['established_full_predictive_closed_count']} / 8**.",
        "",
        "## What V39 settles",
        "",
    ]
    lines.extend(f"- {item}" for item in data["what_V39_actually_settles"])
    lines.extend(["", "## Gate ledger", ""])
    for row in data["gate_ledger"]:
        lines.extend(
            [
                f"### {row['gate']} — open",
                "",
                f"Advance: {row['advance']}",
                "",
                f"Blocking evidence: {row['blocker']}",
                "",
            ]
        )
    terminal = data["terminal_assessment"]
    lines.extend(
        [
            "## Final classification",
            "",
            terminal["reason_theory_is_not_finished"],
            "",
            terminal["why_numbers_are_not_inserted"],
            "",
            f"**Result:** {terminal['strongest_honest_classification']}",
            "",
            "## Primary references",
            "",
            "- [Witten--Yonekura: anomaly inflow and eta invariants](https://arxiv.org/abs/1909.08775)",
            "- [Hsieh: discrete gauge anomalies](https://arxiv.org/abs/1808.02881)",
            "- [Cordova--Ohmori: anomaly obstructions to symmetric gapping](https://arxiv.org/abs/1910.04962)",
            "- [5D SO(10) gaugino mediation](https://arxiv.org/abs/0808.3598)",
            "- [SARAH](https://arxiv.org/abs/0909.2863)",
            "- [Pati--Salam baryon-violating operators](https://arxiv.org/abs/2211.02054)",
            "- [Planck 2018 cosmological parameters](https://arxiv.org/abs/1807.06209)",
            "",
            f"Core SHA-256: `{data['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    data = report()
    if args.write:
        REPORT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT_MD.write_text(markdown(data), encoding="utf-8")
    if args.check:
        if not REPORT_JSON.is_file() or not REPORT_MD.is_file():
            raise SystemExit("generated V39 master report is missing; run with --write")
        if json.loads(REPORT_JSON.read_text(encoding="utf-8")) != data:
            raise SystemExit("generated V39 master JSON is stale; run with --write")
        if REPORT_MD.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V39 master Markdown is stale; run with --write")
        print("SUSY V39 complete-theory audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
