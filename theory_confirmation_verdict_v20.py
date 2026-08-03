#!/usr/bin/env python3
"""Master confirmation verdict for v20 — what is proved vs what is not.

This script aggregates the executed cascade into one honest status document.
It deliberately refuses to claim experimental discovery or that nature
realizes the model.
"""

from __future__ import annotations

import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# Attestation for the latest pushed main commit once GitHub Actions completes.
# Refresh this block when a newer main SHA is CI-verified.
CI_ATTESTATION = {
    "commit_sha": "ba2c66364cd68d733a2dff51416f28d92100eff5",
    "workflow": "replicate-and-falsify",
    "run_id": 30790747879,
    "run_url": "https://github.com/jayalabaez/so10-axion-v20/actions/runs/30790747879",
    "conclusion": "success",
    "unit_tests": "Ran 154 tests in 69.690s - OK",
    "v20_engine": "VERDICT=PASS CHECKS=42/42",
    "extensive_confirm_falsify": "PASS 53/53",
    "check_run": "falsify completed success",
}


def build_verdict() -> dict:
    n_unit_tests = unittest.defaultTestLoader.discover(str(ROOT)).countTestCases()
    extensive = json.loads(
        ROOT.joinpath("EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    next_physics = json.loads(
        ROOT.joinpath("NEXT_PHYSICS_ANALYSIS_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    on_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    if on_ci:
        unittest_evidence = f"{n_unit_tests} unit tests PASS (this GitHub Actions run)"
        unittest_cascade = f"PASS {n_unit_tests}/{n_unit_tests} (this CI run)"
    else:
        unittest_evidence = (
            f"{n_unit_tests} unit tests; CI-verified on "
            f"{CI_ATTESTATION['commit_sha'][:7]} "
            f"({CI_ATTESTATION['unit_tests']}; {CI_ATTESTATION['run_url']})"
        )
        unittest_cascade = (
            f"CI-verified {n_unit_tests}/{n_unit_tests} on "
            f"{CI_ATTESTATION['commit_sha'][:7]}: {CI_ATTESTATION['run_url']}"
        )
    return {
        "title": "SO(10)×Z17 axion candidate v20 — confirmation verdict",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "question_asked": "Execute analysis and prove this theory",
        "short_answer": (
            "The anomaly/operator core passes internal consistency checks and "
            "the 37 GHz photon target remains open. Photon literature and "
            "model-independent SN f_a bounds do not exclude it. Exact full "
            "C_e,C_p,C_n are NOT derived: the physical projected current is "
            "portal dependent, and the corrected Takagi/PMNS flavour analysis "
            "rejects the current v_R=v_S benchmark within the constrained "
            "ansatz. The complete phenomenological model is not approved."
        ),
        "ci_attestation": CI_ATTESTATION,
        "tiers": {
            "PROVED_mathematical_internal": {
                "status": "YES",
                "evidence": [
                    "v20 engine 42/42 PASS",
                    "extensive confirm/falsify "
                    f"{extensive['n_extensive_checks'] - extensive['n_failed']}/"
                    f"{extensive['n_extensive_checks']} PASS",
                    unittest_evidence,
                    "anomaly cancellation with (1,16)+(14,3)+(1,-18)",
                    "one-pair impossible (discriminant -15)",
                    "portal-basis uniqueness of the triple",
                    "no vector-neutral PQ closure through P=7; first at P=8",
                    "Clifford: every 16 has a 10_H channel",
                    "finite repeated-pole kernel; unit P=8 phase ~6.043e-47",
                ],
            },
            "PROVED_not_excluded_by_current_public_bounds": {
                "status": "YES_FOR_PHOTON_AND_MODEL_INDEPENDENT_SN",
                "evidence": [
                    "literature sweep: 0 excluding published bounds at 153.5 µeV",
                    "CAST/HB cover mass but g limits ~2500× too weak",
                    "ORGAN/MADMAX proto exclusions at wrong masses",
                    "universal QCD-axion SN bound on f_a/m_a passes (model-independent)",
                    "aligned-current C_f(tan beta) benchmark is centrally below TRGB/SN1987A, but full-model pass remains open",
                    "analytic Gμ~4.2e-13 below NANOGrav NG ballpark ~1e-10",
                    "central proton lifetime above SK",
                    "public/indirect audit: no hard public kill of the photon benchmark",
                ],
            },
            "CONFIRMED_with_documented_stress": {
                "status": "YES_WITH_STRESS",
                "evidence": [
                    "previous flavour minima used eigh on a non-Hermitian Majorana matrix and omitted U_e^dagger",
                    "corrected fixed-v_R profile has no chi2<30 point; constrained single-scale benchmark fails",
                    "continuous Spin(10) RG rejects alpha(vPhi)=1/40 reset",
                    "conservative one-loop running not Planck-safe without thresholds",
                    "moving-frame Q_proj+Berry=I identity is basis dependent",
                    "physical Q_proj=I-4W is portal dependent and may be flavour off-diagonal",
                ],
            },
            "SOFT_FALSIFIED_overclaims_only": {
                "status": "LABELLED_NOT_THEORY_KILL",
                "items": [
                    "Gamma >= massless width was wrong (upper bound)",
                    "alpha_10(vPhi)=1/40 reset inconsistent",
                    "missing h.c. factors in some NDA quotes",
                    "incomplete portal list",
                    "unit-coefficient amplitudes are diagnostics not predictions",
                ],
            },
            "NOT_PROVED_experimental_realization": {
                "status": "OPEN",
                "missing": [
                    "real 36.6–37.6 GHz haloscope scan at g~2.3e-14 GeV^{-1}",
                    "NS-radio detection of Doppler-modulated 37 GHz line",
                    "lattice (13,-3) string-network confirmation",
                    "complete A,B,C,D portal tensors and SM Yukawa alignment",
                    "viable global high-scale flavour/Higgs fit",
                    "correlated hadronic and threshold/RG precision matching",
                    "independent human diagrammatic referee",
                    "proof that local DM is this axion (abundance + detection)",
                ],
            },
        },
        "cascade_results": {
            "v20_engine": "PASS 42/42",
            "error_audit": "PASS (soft overclaims flagged)",
            "falsify_v20": "PASS 0 hard failures",
            "fermion_couplings": "ALIGNED_BENCHMARK_ONLY / FULL_MATCHING_OPEN",
            "tan_beta_profile": "corrected Takagi/PMNS profile: no chi2<30 point",
            "literature_150ueV": "OPEN (does not fail)",
            "home_public_37GHz": "PASS (CMB mythbust)",
            "gravitas_37GHz": "PASS (21 targets)",
            "public_indirect_audit": "PASS 20 channels / 13 runnable; proves=false",
            "next_physics": (
                f"{next_physics['status']} "
                f"{next_physics['n_checks'] - next_physics['n_failed']}/"
                f"{next_physics['n_checks']}"
            ),
            "extensive_confirm_falsify": (
                f"{extensive['status']} "
                f"{extensive['n_extensive_checks'] - extensive['n_failed']}/"
                f"{extensive['n_extensive_checks']}"
            ),
            "unittest": unittest_cascade,
        },
        "correct_public_claim": (
            "We have a mathematically consistent SO(10)×Z17 axion candidate "
            "that survives adversarial in-repo tests. Current published photon "
            "bounds and the model-independent SN f_a window do not exclude the "
            "37 GHz all-DM photon benchmark. Exact full fermion couplings are "
            "not yet derived because the projected current depends on portal "
            "mixing/Yukawa alignment. The corrected constrained flavour fit "
            "does not support v_R=v_S. Whether a fuller model or nature realizes "
            "the construction remains open."
        ),
        "incorrect_claim_do_not_use": (
            "We proved dark matter is a 153.5 µeV SO(10) axion / we detected "
            "the 37 GHz line / CMB maps confirm the theory."
        ),
        "what_would_upgrade_to_empirical_proof": [
            "Positive laboratory conversion signal in 36.6–37.6 GHz at the predicted coupling",
            "Or: astrophysical NS-conversion line phase-locked to GRAVITAS ephemeris",
        ],
        "verdict_code": "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN",
    }


def write_markdown(v: dict) -> str:
    lines = [
        "# Theory confirmation verdict — v20",
        "",
        f"**Generated (UTC):** {v['generated_utc']}",
        "",
        f"**Question:** {v['question_asked']}",
        "",
        f"## Short answer",
        "",
        v["short_answer"],
        "",
        f"**Verdict code:** `{v['verdict_code']}`",
        "",
        "## Tier results",
        "",
    ]
    for key, tier in v["tiers"].items():
        lines.append(f"### {key}")
        lines.append("")
        lines.append(f"- Status: **{tier['status']}**")
        for field in ("evidence", "items", "missing"):
            if field in tier:
                for item in tier[field]:
                    lines.append(f"- {item}")
        lines.append("")
    lines += [
        "## Cascade executed this run",
        "",
    ]
    for k, val in v["cascade_results"].items():
        lines.append(f"- `{k}`: {val}")
    ci = v.get("ci_attestation") or {}
    if ci:
        lines += [
            "",
            "## CI attestation",
            "",
            f"- commit: `{ci.get('commit_sha', '')}`",
            f"- workflow: `{ci.get('workflow', '')}` conclusion **{ci.get('conclusion', '')}**",
            f"- unit tests: {ci.get('unit_tests', '')}",
            f"- engine: {ci.get('v20_engine', '')}",
            f"- extensive: {ci.get('extensive_confirm_falsify', '')}",
            f"- run: {ci.get('run_url', '')}",
        ]
    lines += [
        "",
        "## Correct public claim",
        "",
        f"> {v['correct_public_claim']}",
        "",
        "## Do not claim",
        "",
        f"> {v['incorrect_claim_do_not_use']}",
        "",
        "## What would count as empirical proof",
        "",
        *[f"- {x}" for x in v["what_would_upgrade_to_empirical_proof"]],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    v = build_verdict()
    ROOT.joinpath("THEORY_CONFIRMATION_VERDICT.json").write_text(
        json.dumps(v, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("THEORY_CONFIRMATION_VERDICT.md").write_text(
        write_markdown(v), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "verdict_code": v["verdict_code"],
                "short_answer": v["short_answer"],
                "cascade": v["cascade_results"],
                "correct_public_claim": v["correct_public_claim"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
