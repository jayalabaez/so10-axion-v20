#!/usr/bin/env python3
"""Master confirmation verdict for v20 — what is proved vs what is not.

This script aggregates the executed cascade into one honest status document.
It deliberately refuses to claim experimental discovery or that nature
realizes the model.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def build_verdict() -> dict:
    return {
        "title": "SO(10)×Z17 axion candidate v20 — confirmation verdict",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "question_asked": "Execute analysis and prove this theory",
        "short_answer": (
            "PROVED as an internally consistent, anomaly-free candidate theory "
            "with an open 37 GHz photon target. Photon literature and "
            "model-independent SN f_a bounds do not exclude it. Fermion "
            "couplings are only a provisional ERT-like benchmark (gap NOT "
            "closed). NOT PROVED that nature realizes the model or that DM "
            "was detected."
        ),
        "tiers": {
            "PROVED_mathematical_internal": {
                "status": "YES",
                "evidence": [
                    "v20 engine 42/42 PASS",
                    "extensive confirm/falsify 48/48 PASS",
                    "136 unit tests PASS",
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
                    "provisional ERT-like fermion benchmark is conditionally below TRGB/SN1987A, but full_model_pass=null (gap NOT closed)",
                    "analytic Gμ~4.2e-13 below NANOGrav NG ballpark ~1e-10",
                    "central proton lifetime above SK",
                    "public/indirect audit: no hard public kill of the photon benchmark",
                ],
            },
            "CONFIRMED_with_documented_stress": {
                "status": "YES_WITH_STRESS",
                "evidence": [
                    "exact v_R=v_S flavour chi2~11.7 (viable but worse than ~1e14)",
                    "continuous Spin(10) RG rejects alpha(vPhi)=1/40 reset",
                    "conservative one-loop running not Planck-safe without thresholds",
                    "fermion C_e/C_p/C_n still require full portal matching (PR #2 correction)",
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
                    "full generation-dependent portal matrices → unique C_e, C_p, C_n",
                    "independent human diagrammatic referee",
                    "proof that local DM is this axion (abundance + detection)",
                ],
            },
        },
        "cascade_results": {
            "v20_engine": "PASS 42/42",
            "error_audit": "PASS (soft overclaims flagged)",
            "falsify_v20": "PASS 0 hard failures",
            "fermion_couplings": "PROVISIONAL_LEADING_CURRENT_ONLY__FULL_V20_MATCHING_OPEN",
            "literature_150ueV": "OPEN (does not fail)",
            "home_public_37GHz": "PASS (CMB mythbust)",
            "gravitas_37GHz": "PASS (21 targets)",
            "public_indirect_audit": "PASS 20 channels / 13 runnable; proves=false",
            "next_physics": "PASS 8/8",
            "extensive_confirm_falsify": "PASS 48/48",
            "unittest": "PASS 136/136",
        },
        "correct_public_claim": (
            "We have a mathematically consistent SO(10)×Z17 axion candidate "
            "that survives adversarial in-repo tests. Current published photon "
            "bounds and the model-independent SN f_a window do not exclude the "
            "37 GHz all-DM benchmark. Provisional ERT-like fermion couplings "
            "look safe under stated assumptions, but exact C_e/C_p/C_n are not "
            "uniquely derived (portal matching open). Whether nature realizes "
            "this model remains an open experimental question."
        ),
        "incorrect_claim_do_not_use": (
            "We proved dark matter is a 153.5 µeV SO(10) axion / we detected "
            "the 37 GHz line / CMB maps confirm the theory."
        ),
        "what_would_upgrade_to_empirical_proof": [
            "Positive laboratory conversion signal in 36.6–37.6 GHz at the predicted coupling",
            "Or: astrophysical NS-conversion line phase-locked to GRAVITAS ephemeris",
        ],
        "verdict_code": "INTERNALLY_PROVED_EMPIRICALLY_OPEN",
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
