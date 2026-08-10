#!/usr/bin/env python3
"""Explicit once-only heavy reconstruction test for the corrected v21 system.

This file is deliberately outside ``test*.py`` discovery.  Set
``SO10_PUBLISHED_API_ROOT`` to the byte-pinned structural API directory and
invoke it once in the dedicated heavy job.  The corrected RHS is reconstructed
inside ``reconstruct_system``; no second RHS pass is performed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence


HERE = Path(__file__).resolve().parent
source_root = os.environ.get("SO10_PUBLISHED_API_ROOT")
if source_root is None:
    raise RuntimeError("SO10_PUBLISHED_API_ROOT is required for the explicit heavy test")
SOURCE_ROOT = Path(source_root).resolve()
if not SOURCE_ROOT.is_dir():
    raise RuntimeError("SO10_PUBLISHED_API_ROOT is not a directory")
for source in (SOURCE_ROOT, HERE):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21 as system
import verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21 as theorem


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check")
    if Path(system.__file__).resolve() != (
        HERE / "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py"
    ).resolve():
        raise ImportError("heavy corrected-map source escaped HERE")
    source_report = theorem._load_pinned(theorem.SOURCE_REPORT)
    theorem._validate_source(source_report)
    matrix, denominator, target, target_denominator, blocks, diagnostics = (
        system.reconstruct_system()
    )
    if not (
        matrix.shape == (6_585, 19_594)
        and matrix.nnz == 138_550
        and denominator == 256
        and system.sparse_sha256(matrix)
        == source_report["map"]["numerator_csr_sha256"]
        and target.shape == (6_585,)
        and target_denominator == 576_000
        and system.int64_array_sha256(target)
        == source_report["physical_RHS"]["numerator_sha256"]
        and len(blocks) == 22
        and diagnostics.get("prior_assembled_map_read") is False
        and diagnostics.get("prior_primal_certificate_read") is False
        and diagnostics.get("v20_physical_target_payload_read") is False
        and diagnostics["corrected_physical_RHS"].get(
            "v20_physical_target_artifact_read"
        )
        is False
        and diagnostics["corrected_physical_RHS"].get(
            "row_by_row_direct_evaluator_mismatch_count"
        )
        == 0
    ):
        raise ArithmeticError("once-only heavy corrected-system reconstruction drifted")
    print(
        json.dumps(
            {
                "status": "EXACT_RANK1_SU4_CORRECTED_SYSTEM_V21_HEAVY_REGENERATION_PASS",
                "heavy_reconstruction_count_in_this_process": 1,
                "RHS_reconstruction_count_in_this_process": 1,
                "map_numerator_csr_sha256": system.sparse_sha256(matrix),
                "target_numerator_sha256": system.int64_array_sha256(target),
                "v20_physical_target_payload_read": False,
                "G3_closed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
