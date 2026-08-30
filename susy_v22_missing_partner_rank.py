#!/usr/bin/env python3
"""Exact representation-count/rank frontier for the V22 missing-partner sector.

The initially staged anomaly-vectorlike V22 field list contains two 10s and
two 120s but only one 126+126bar pair plus a 210.  That is *not* a viable
missing-partner sector.  This module proves the failure by rank bounds and
then proves the minimal count correction: one more vectorlike 126+126bar
pair.  The corrected pair is now source-landed in V22; the remaining rank
claim is still abstract until the actual component Clebsches are derived.

This is an exact architecture theorem, not a substitute for the source-exact
SO(10) component Clebsches, the V22 F/D/soft vacuum, or the RG calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_MISSING_PARTNER_RANK.json"
OUT_MD = ROOT / "SUSY_V22_MISSING_PARTNER_RANK.md"


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csha(value: Any) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def rank_q(matrix: list[list[int | Fraction]]) -> int:
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return 0
    nrow, ncol = len(a), len(a[0])
    if any(len(row) != ncol for row in a):
        raise ValueError("ragged matrix")
    rank = 0
    for col in range(ncol):
        pivot = next((row for row in range(rank, nrow) if a[row][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        p = a[rank][col]
        a[rank] = [x / p for x in a[rank]]
        for row in range(nrow):
            if row != rank and a[row][col]:
                f = a[row][col]
                a[row] = [x - f * y for x, y in zip(a[row], a[rank])]
        rank += 1
        if rank == nrow:
            break
    return rank


def block_matrix(light: int, heavy: int, *, full_triplet: bool) -> list[list[int]]:
    """Return an exact integer witness respecting the missing-partner zeros.

    The top-left light-light block is exactly zero.  For the corrected
    doublet sector (6,5), off-diagonal identity embeddings give rank 10.  For
    the triplet sector (6,7), a nonsingular heavy block plus full-rank
    embeddings gives rank 13.
    """
    n = light + heavy
    m = [[0 for _ in range(n)] for _ in range(n)]
    common = min(light, heavy)
    for i in range(common):
        m[i][light + i] = 1
        m[light + i][i] = 1
    if full_triplet:
        for i in range(heavy):
            m[light + i][light + i] = 1
    return m


def multiplicities(n_10: int, n_120: int, n_126_pairs: int) -> dict[str, int]:
    # SU(5) branching count used by the 126+126bar missing-partner mechanism:
    # each 10 has 1 D/T pair; each 120 has 2 D/T pairs; one 210 plus the
    # first 126 pair has 3 D and 4 T heavy pairs; every extra 126 pair adds
    # 2 D and 3 T pairs.
    return {
        "light_doublet_pairs": n_10 + 2 * n_120,
        "light_triplet_pairs": n_10 + 2 * n_120,
        "heavy_doublet_pairs": 1 + 2 * n_126_pairs,
        "heavy_triplet_pairs": 1 + 3 * n_126_pairs,
    }


def build_report() -> dict[str, Any]:
    model_path = ROOT / "models/SO10X17SUSYV22/SO10X17SUSYV22.m"
    model_text = portable_bytes(model_path).decode("utf-8")
    initial = multiplicities(2, 2, 1)
    corrected = multiplicities(2, 2, 2)
    dmat = block_matrix(6, 5, full_triplet=False)
    tmat = block_matrix(6, 7, full_triplet=True)
    drank, trank = rank_q(dmat), rank_q(tmat)
    initial_d_min_nullity = initial["light_doublet_pairs"] - initial["heavy_doublet_pairs"]
    initial_t_min_nullity = initial["light_triplet_pairs"] - initial["heavy_triplet_pairs"]
    checks = {
        "initial_vectorlike_scaffold_is_not_missing_partner_complete": initial_d_min_nullity == 3 and initial_t_min_nullity == 2,
        "corrected_doublet_count_differs_by_exactly_one": corrected["light_doublet_pairs"] - corrected["heavy_doublet_pairs"] == 1,
        "corrected_heavy_triplet_count_is_not_deficient": corrected["heavy_triplet_pairs"] >= corrected["light_triplet_pairs"],
        "exact_doublet_witness_has_one_zero_pair": len(dmat) == 11 and drank == 10,
        "exact_triplet_witness_is_full_rank": len(tmat) == 13 and trank == 13,
        "light_light_superpotential_block_is_exactly_zero": all(dmat[i][j] == 0 for i in range(6) for j in range(6)) and all(tmat[i][j] == 0 for i in range(6) for j in range(6)),
        "rank_claim_is_structural_not_a_component_CG_claim": True,
        "corrected_second_126_pair_is_source_landed": all(token in model_text for token in (
            "SuperFields[[13]] = {DeltaB2", "SuperFields[[14]] = {Delta2",
            "rho2 XMP.DeltaB2.Delta2", "gammaHb2 Phi210.H10p.DeltaB2",
            "gammaTb2 Phi210.T120p.DeltaB2")),
        "continuous_U1_MP_is_not_misrepresented_as_source_declared": "U1_MP" not in model_text,
        "canonical_G4_not_promoted_before_component_and_RGE_proofs": True,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    sources = {
        "corrected_model": {
            "path": "models/SO10X17SUSYV22/SO10X17SUSYV22.m",
            "portable_sha256": sha(portable_bytes(model_path)),
        },
        "primary_missing_partner_reference": {
            "title": "Missing Partner Mechanism in SO(10) Grand Unification",
            "arXiv": "hep-ph/0612315",
        },
        "representation_count_reference": {
            "title": "Variety of SO(10) GUTs with Natural Doublet-Triplet Splitting via the Missing Partner Mechanism",
            "arXiv": "1112.5387",
        },
    }
    report: dict[str, Any] = {
        "schema": "susy_v22_missing_partner_rank_v1",
        "status": "CORRECTED_MISSING_PARTNER_MULTIPLICITY_AND_EXACT_RANK_WITNESS_CLOSED__COMPONENT_G4_OPEN" if not failures else "MISSING_PARTNER_RANK_AUDIT_FAILED",
        "sources": sources,
        "representation_pair_counts": {"initial_one_126_pair": initial, "corrected_two_126_pairs": corrected},
        "initial_failure": {
            "minimum_unpaired_doublet_pairs": initial_d_min_nullity,
            "minimum_unpaired_triplet_pairs": initial_t_min_nullity,
            "accepted_for_V22": False,
        },
        "corrected_rank_certificate": {
            "doublet_matrix_shape": [11, 11],
            "doublet_rank": drank,
            "doublet_nullity": 11 - drank,
            "triplet_matrix_shape": [13, 13],
            "triplet_rank": trank,
            "triplet_nullity": 13 - trank,
            "matrix_entry_domain": "Z",
            "top_left_light_light_block": "exact zero in the unbroken source-declared Z4R holomorphic limit, conditional on every R4=2 field having zero VEV",
            "interpretation": "the determinant/minor polynomials are nonzero, hence these ranks hold on a nonempty Zariski-open parameter set once the accepted G1 basis and actual Clebsch map span the witness",
        },
        "required_model_correction": {
            "add": ["DeltaB2: bar126, X=-2", "Delta2: 126, X=+2", "XMP: singlet, X=0, literature MP grading +2"],
            "source_landed": True,
            "literature_MP_grading_only": {"light_10_120": "+1", "heavy_126_126bar": "-1", "Phi210": "0", "matter_16": "-1/2"},
            "source_declared_continuous_U1_MP": False,
            "Z4R_conditionally_forbids": ["light-light GUT mass block", "H10m.H10p", "T120m.T120p"],
            "allows": ["Phi210.light.heavy", "XMP.heavy.heavy", "matter.matter.light"],
        },
        "remaining_exact_work": [
            "repair and close the G1 operator basis before selecting the component mass operators",
            "derive the full SO(10)->SM doublet and triplet Clebsch matrices and prove their ranks at one source-exact parameter point after G1 repair",
            "solve the complete V22 F+D+soft vacuum, with C16/C16bar breaking the rank and every missing-partner 126/126bar VEV exactly zero, and exclude deeper branches",
            "prove the light-light block remains zero against every allowed higher-dimensional operator",
            "run the complete perturbativity/RGE and pole-spectrum bridge to the exact 174 GeV endpoint",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "claim_boundary": {
            "initial_V22_scaffold_rejected": not failures,
            "corrected_missing_partner_architecture_exists": not failures,
            "corrected_missing_partner_fields_source_landed": not failures,
            "source_exact_component_missing_partner_closed": False,
            "canonical_G4_closed": False,
            "canonical_G5_closed": False,
        },
    }
    body = dict(report)
    report["core_sha256"] = csha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    cert = report["corrected_rank_certificate"]
    return "\n".join([
        "# SUSY V22 missing-partner rank frontier", "",
        f"- Status: `{report['status']}`", f"- Core: `{report['core_sha256']}`",
        "- Initial one-126-pair scaffold: rejected (at least 3 doublet and 2 triplet pairs remain).",
        f"- Corrected doublet rank/nullity: `{cert['doublet_rank']}/{cert['doublet_nullity']}`.",
        f"- Corrected triplet rank/nullity: `{cert['triplet_rank']}/{cert['triplet_nullity']}`.", "",
        "This proves the exact representation-count/rank architecture. Canonical G4 remains open until the actual SO(10) component Clebsches, V22 vacuum, RGE, thresholds and pole spectrum are source-exact.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    r = build_report()
    if a.write:
        write_outputs(r)
    if a.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r)):
        raise ArithmeticError("missing-partner rank report drifted")
    print(r["status"]); print(r["core_sha256"])
    return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
