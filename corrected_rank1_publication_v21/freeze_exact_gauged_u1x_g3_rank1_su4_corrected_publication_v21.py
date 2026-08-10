#!/usr/bin/env python3
"""Write or verify the exact byte inventory of the v21 publication bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json"
)
EXPECTED_FILES = {
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json": "runtime theorem report",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json": "generation-time live regression report",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json": "generation-time overflow report",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21.json": "runtime exact primal certificate",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_SYSTEM_V21.npz": "runtime corrected sparse system",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json": "runtime independent exact-verifier report",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json": "generation-time exhaustive source report",
    "README.md": "publication documentation",
    "exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21.py": "generation-time ordered-spectral RHS source",
    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py": "generation-time exhaustive map source",
    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py": "runtime HERE-only canonical loader",
    "freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py": "inventory writer/verifier",
    "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py": "explicit once-only heavy test",
    "test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py": "fast fail-closed tests",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py": "runtime HERE-only theorem bridge",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_live_polynomial_v21.py": "generation-time direct live evaluator",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_ordered_spectral_overflow_v21.py": "generation-time direct overflow evaluator",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py": "runtime HERE-only Fraction/Bareiss verifier",
}
LOGICAL_PINS = {
    "certificate_raw_sha256": "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03",
    "system_raw_sha256": "25ec946b1e9bca50cfe4e31ac9bb58f5d8d0f4a24b83dc11fdeec0d68a80c6f3",
    "map_numerator_csr_sha256": "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16",
    "target_numerator_sha256": "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf",
    "exact_coordinate_sha256": "7a36b579821e135fb7283d02e696153cc78907048e73ca5dce0dd260abdc3147",
    "exact_LDL_pivot_sha256": "bc8626c201d626aa33a97f707bfa963ae887fe9abb64a0fab728343825a430c2",
}


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_canonical_json(path: Path) -> None:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ArithmeticError(f"JSON is not UTF-8: {path.name}") from error
    if "\r" in text or not text.endswith("\n"):
        raise ArithmeticError(f"JSON is not LF/final-newline canonical: {path.name}")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ArithmeticError(f"JSON is invalid: {path.name}") from error
    canonical = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    if raw != canonical:
        raise ArithmeticError(f"JSON is not sorted indent-2 canonical: {path.name}")


def _require_clean_inventory(*, manifest_may_be_absent: bool) -> None:
    cache = HERE / "__pycache__"
    if cache.exists():
        raise ArithmeticError("__pycache__ is forbidden in a frozen publication")
    expected = set(EXPECTED_FILES) | {MANIFEST.name}
    observed = {path.name for path in HERE.iterdir()}
    if manifest_may_be_absent:
        expected_without = expected - {MANIFEST.name}
        if observed not in (expected, expected_without):
            raise ArithmeticError(
                f"publication inventory drifted: expected {sorted(expected)}, observed {sorted(observed)}"
            )
    elif observed != expected:
        raise ArithmeticError(
            f"publication inventory drifted: expected {sorted(expected)}, observed {sorted(observed)}"
        )
    if any(not path.is_file() for path in HERE.iterdir()):
        raise ArithmeticError("publication contains a non-file entry")


def build_manifest() -> dict[str, Any]:
    _require_clean_inventory(manifest_may_be_absent=True)
    for name in EXPECTED_FILES:
        if name.endswith(".json"):
            _require_canonical_json(HERE / name)
    inventory = {
        name: {
            "role": role,
            "size_bytes": (HERE / name).stat().st_size,
            "raw_sha256": raw_sha256(HERE / name),
        }
        for name, role in sorted(EXPECTED_FILES.items())
    }
    return {
        "schema": "so10-rank1-su4-corrected-positive-gram-publication-v21",
        "status": "EXACT_RANK1_SU4_CORRECTED_PUBLICATION_V21_INVENTORY_FROZEN",
        "manifest_self_excluded_by_definition": True,
        "inventory_count": len(inventory),
        "inventory": inventory,
        "logical_pins": LOGICAL_PINS,
        "ordinary_validation": {
            "heavy_source_reconstruction_performed": False,
            "runtime_dependency_root": "HERE only",
            "relocation_tested_with_python_isolated_mode": True,
        },
        "heavy_validation": {
            "entrypoint": (
                "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py --check"
            ),
            "full_map_reconstruction_count": 1,
            "embedded_full_RHS_reconstruction_count": 1,
            "ordinary_unittest_discovery_runs_heavy_entrypoint": False,
        },
        "claim_boundary": {
            "fixed_H": "h_-=(e0-i e1)/sqrt(2)",
            "fixed_Sigma": "q/4",
            "arbitrary_real_Phi_at_fixed_endpoint": True,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
    }


def write_manifest() -> dict[str, Any]:
    report = build_manifest()
    MANIFEST.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def check_manifest() -> dict[str, Any]:
    _require_clean_inventory(manifest_may_be_absent=False)
    _require_canonical_json(MANIFEST)
    observed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = build_manifest()
    if observed != expected:
        raise ArithmeticError("publication manifest or byte inventory drifted")
    return observed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = write_manifest() if args.write else check_manifest()
    print(
        json.dumps(
            {
                "status": report["status"],
                "inventory_count": report["inventory_count"],
                "G3_closed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
