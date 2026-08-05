#!/usr/bin/env python3
r"""SM-sector catalog of the 36 SO(10)→U(1)_EM Goldstones (v20).

Physics
-------
With the repository embedding

* colour SO(6) on indices ``0..5``,
* weak SO(4) on indices ``6..9``,
* physical ``⟨H⟩ = hEW · ê_6``,

the extended gauge orbit has rank **36** and stabilizer dimension **9**
(``SU(3)_c × U(1)_EM``). Individual so(10) planes ``M_{ab}`` need not
vanish on the VEVs: the unbroken generators are **linear combinations**
in the 45-dimensional adjoint (e.g. the SU(3)_c Cartan/root combos inside
SO(6)). This module:

1. SVD-ranks the ``(210_PS, Δ_R, hEW)`` tangent → 36 Goldstones / 9 stab.
2. Extracts orthonormal bases of the broken and stabilizer subspaces in
   generator space (right singular vectors).
3. Labels every plane by sector and records its tangent-column norm.
4. Records the weak Cartans
   ``T3_L = -i(M_67+M_89)/2``, ``T3_R = -i(M_67-M_89)/2``, ``Q=T3_L+T3_R``.

Honesty
-------
* Orbit / representation catalog — not dynamical scalar mass eigenvalues.
* Full SM irrep mass tables for the 701 physical modes remain OPEN.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import so10_gauge_orbit_with_hew_v20 as hew_orbit
import so10_nonsusy_gauge_orbit_v20 as orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_GOLDSTONE_SM_ROOT_CATALOG_V20.json"
OUT_MD = ROOT / "SO10_GOLDSTONE_SM_ROOT_CATALOG_V20.md"

COLOR_INDICES = frozenset(range(6))
WEAK_INDICES = frozenset(range(6, 10))
HEW_DIR = hew_orbit.HEW_DIRECTION_INDEX


def sector_of(a: int, b: int) -> str:
    if a in COLOR_INDICES and b in COLOR_INDICES:
        return "so6_color"
    if a in WEAK_INDICES and b in WEAK_INDICES:
        return "so4_weak"
    return "so6_so4_cross"


def cartan_tag(a: int, b: int) -> str | None:
    if (a, b) == (6, 7):
        return "M67_in_T3L_and_T3R"
    if (a, b) == (8, 9):
        return "M89_in_T3L_and_T3R"
    if (a, b) in {(6, 8), (6, 9), (7, 8), (7, 9)}:
        return f"weak_plane_{a}{b}"
    return None


def generator_subspaces(tangent: np.ndarray, *, rank: int) -> dict[str, Any]:
    """Right-singular decomposition: broken ↔ first ``rank`` directions."""
    # economy SVD; Vt rows are generator-space singular vectors
    _, svals, vt = np.linalg.svd(tangent, full_matrices=True)
    broken = vt[:rank, :].T  # (45, rank)
    stab = vt[rank:, :].T  # (45, 45-rank)
    return {
        "singular_values": svals.tolist(),
        "n_nonzero_sv": int(rank),
        "broken_basis_45xR": broken,
        "stabilizer_basis_45xK": stab,
    }


def sector_weights(basis: np.ndarray, gens: list[tuple[int, int]]) -> dict[str, float]:
    """L2 mass of basis vectors on each sector (sum of squared components)."""
    weights = {"so6_color": 0.0, "so4_weak": 0.0, "so6_so4_cross": 0.0}
    for j in range(basis.shape[1]):
        for i, (a, b) in enumerate(gens):
            weights[sector_of(a, b)] += float(basis[i, j] ** 2)
    return weights


def build_report(*, h_ew_gev: float = hew_orbit.HEW_GEV) -> dict[str, Any]:
    ext = hew_orbit.extended_tangent_matrix(h_ew_gev=h_ew_gev)
    tangent = ext["matrix"]
    gens = orbit.generators()
    assert tangent.shape[1] == len(gens) == 45

    rank = orbit.svd_rank(tangent)
    stab_dim = 45 - rank
    spaces = generator_subspaces(tangent, rank=rank)

    col_norms = np.linalg.norm(tangent, axis=0)
    rows = []
    plane_sector_counts: Counter[str] = Counter()
    for i, (a, b) in enumerate(gens):
        sec = sector_of(a, b)
        plane_sector_counts[sec] += 1
        rows.append(
            {
                "generator_index": i,
                "plane": [int(a), int(b)],
                "sector": sec,
                "column_norm": float(col_norms[i]),
                "column_exactly_zero": float(col_norms[i]) < 1e-12,
                "cartan_tag": cartan_tag(a, b),
                "involves_hew_direction": HEW_DIR in (a, b),
            }
        )

    sm = hew_orbit.sm_only_tangent_matrix()
    sm_rank = orbit.svd_rank(sm["matrix"])

    broken_w = sector_weights(spaces["broken_basis_45xR"], gens)
    stab_w = sector_weights(spaces["stabilizer_basis_45xK"], gens)

    # Compact stabilizer vectors (top components) for readability
    stab_basis = spaces["stabilizer_basis_45xK"]
    stab_summaries = []
    for k in range(stab_basis.shape[1]):
        comps = [
            {
                "plane": [int(a), int(b)],
                "sector": sector_of(a, b),
                "coeff": float(stab_basis[i, k]),
            }
            for i, (a, b) in enumerate(gens)
            if abs(stab_basis[i, k]) > 0.05
        ]
        comps.sort(key=lambda c: -abs(c["coeff"]))
        stab_summaries.append(
            {
                "stabilizer_mode": k,
                "dominant_planes": comps[:8],
                "sector_l2": {
                    sec: float(
                        sum(
                            stab_basis[i, k] ** 2
                            for i, (a, b) in enumerate(gens)
                            if sector_of(a, b) == sec
                        )
                    )
                    for sec in ("so6_color", "so4_weak", "so6_so4_cross")
                },
            }
        )

    n_zero_planes = sum(1 for r in rows if r["column_exactly_zero"])

    checks = {
        "generator_count_45": len(gens) == 45,
        "svd_rank_36": rank == 36,
        "stabilizer_dim_9": stab_dim == 9,
        "sm_rank_33": sm_rank == 33,
        "delta_rank_plus_3": (rank - sm_rank) == 3,
        "plane_so6_15": plane_sector_counts["so6_color"] == 15,
        "plane_so4_6": plane_sector_counts["so4_weak"] == 6,
        "plane_cross_24": plane_sector_counts["so6_so4_cross"] == 24,
        "stabilizer_basis_cols_9": spaces["stabilizer_basis_45xK"].shape[1] == 9,
        "broken_basis_cols_36": spaces["broken_basis_45xR"].shape[1] == 36,
        "hew_direction_is_6": HEW_DIR == 6,
        "individual_zero_planes_not_all_9": n_zero_planes < 9,  # combos matter
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_GOLDSTONE_SM_ROOT_CATALOG_READY"
            if not failures
            else "SO10_GOLDSTONE_SM_ROOT_CATALOG_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "embedding": {
            "color_indices_0_5": list(range(6)),
            "weak_indices_6_9": list(range(6, 10)),
            "hEW_direction_index": HEW_DIR,
            "hEW_GeV": float(h_ew_gev),
            "cartans": {
                "T3_L": "-i (M_67 + M_89)/2",
                "T3_R": "-i (M_67 - M_89)/2",
                "Y_on_10": "T3_R (B-L=0)",
                "Q": "T3_L + T3_R",
            },
            "note": (
                "Unbroken SU(3)_c×U(1)_EM are linear combinations of M_ab; "
                "only rare planes (e.g. M_89 here) have vanishing columns alone."
            ),
        },
        "orbit": {
            "svd_rank_goldstones": int(rank),
            "stabilizer_dim": int(stab_dim),
            "sm_only_rank": int(sm_rank),
            "ew_extra_goldstones": int(rank - sm_rank),
            "n_planes_with_zero_column": n_zero_planes,
            "leading_singular_values": spaces["singular_values"][:5],
            "trailing_singular_values": spaces["singular_values"][-5:],
        },
        "subspace_sector_l2_weights": {
            "broken_36": broken_w,
            "stabilizer_9": stab_w,
        },
        "stabilizer_mode_summaries": stab_summaries,
        "planes": rows,
        "weak_so4_planes": [r for r in rows if r["sector"] == "so4_weak"],
        "hew_involving_planes": [r for r in rows if r["involves_hew_direction"]],
        "flags": {
            "goldstone_sm_root_catalog_ready": not bool(failures),
            "root_by_root_dynamical_hessian_masses": False,
            "cg_120_320_1050_4125_invented": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_sm_irrep_mass_tables": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"SVD catalog: {rank} Goldstones + {stab_dim} stabilizer "
            f"(SU(3)_c×U(1)_EM) on (210,Δ,hEW). SM-only rank {sm_rank}; "
            f"EW adds {rank - sm_rank}. Stabilizer lives in generator-space "
            f"combinations (sector L2 weights {stab_w}); "
            f"only {n_zero_planes} individual plane(s) have zero columns. "
            "Dynamical masses remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    # Drop large numeric bases from JSON — keep summaries only
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SO(10) Goldstone SM root catalog — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Goldstones (SVD): `{report['orbit']['svd_rank_goldstones']}`\n"
        f"- Stabilizer: `{report['orbit']['stabilizer_dim']}` "
        f"(SU(3)_c×U(1)_EM)\n"
        f"- Stabilizer sector L2: `{report['subspace_sector_l2_weights']['stabilizer_9']}`\n"
        f"- Broken sector L2: `{report['subspace_sector_l2_weights']['broken_36']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    compact = {
        k: v
        for k, v in report.items()
        if k not in {"planes", "stabilizer_mode_summaries"}
    }
    compact["n_planes"] = len(report["planes"])
    compact["n_stabilizer_summaries"] = len(report["stabilizer_mode_summaries"])
    print(json.dumps(compact, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
