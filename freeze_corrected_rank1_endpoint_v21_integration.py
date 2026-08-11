#!/usr/bin/env python3
"""Write or verify the exact corrected-endpoint central-integration snapshot.

The publication bundle and the generation dependencies whose source modules
pin raw bytes use raw SHA-256.  Other repository text uses an LF-normalized
portable payload so this integration fingerprint survives Git's platform line
ending policy.  The manifest excludes itself and is not listed in SHA256SUMS;
instead, its raw SHA-256 is the external freeze identifier.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = "CORRECTED_RANK1_ENDPOINT_V21_INTEGRATION_MANIFEST.json"
MANIFEST = ROOT / MANIFEST_NAME
PUBLICATION_MANIFEST_SHA256 = (
    "7ecf96a12321b9df5e7d118ce0fb83e65ad9859516b520936408ec4d46a11017"
)
MAP_SHA256 = "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16"
TARGET_SHA256 = (
    "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf"
)
CERTIFICATE_SHA256 = (
    "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03"
)
COORDINATE_SHA256 = (
    "7a36b579821e135fb7283d02e696153cc78907048e73ca5dce0dd260abdc3147"
)
LDL_SHA256 = "bc8626c201d626aa33a97f707bfa963ae887fe9abb64a0fab728343825a430c2"
GLOBAL_PHI_CLASSIFICATION_SOURCE_SHA256 = (
    "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
)
GLOBAL_PHI_CLASSIFICATION_CORE_SHA256 = (
    "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
)

PUBLICATION_FILES = (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_SYSTEM_V21.npz",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json",
    "README.md",
    "exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21.py",
    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py",
    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
    "freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
    "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py",
    "test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_live_polynomial_v21.py",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_ordered_spectral_overflow_v21.py",
    "verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
)
PUBLICATION_PATHS = tuple(
    f"corrected_rank1_publication_v21/{name}" for name in PUBLICATION_FILES
)

WORKFLOW_PATHS = (
    ".github/workflows/current-main-full-reaudit.yml",
    ".github/workflows/g1-g8-execution-roadmap.yml",
    ".github/workflows/g1-g8-gate-ledger.yml",
    ".github/workflows/gauged-u1x-g3-stability.yml",
    ".github/workflows/latest-main-final-scalar-gate.yml",
    ".github/workflows/replicate-and-falsify.yml",
)
CORRECTED_CONSUMER_WORKFLOWS = tuple(
    path for path in WORKFLOW_PATHS if "latest-main-final-scalar-gate" not in path
)
READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS = (
    "prepare_validation_artifacts_v20.py",
    "replicate.py",
    "validate_release_v20.py",
)
FROZEN_STABILIZER_SOURCE = (
    "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
)
READ_ONLY_FROZEN_REPORT_SOURCES = (
    "gauged_u1x_g2_derivative_audit_v20.py",
    "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
    "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
    "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
    "gauged_u1x_g3_sos_candidate_v20.py",
    "gauged_u1x_g3_stability_v20.py",
    "gauged_u1x_g3_corrected_common_kernel_v20.py",
    "g1_g8_gate_ledger_v20.py",
    "final_g3_acceptance_gate_v20.py",
    "g1_g8_execution_roadmap_v20.py",
)
NO_WRITE_FROZEN_CLASSIFICATION_SOURCES = (
    "theory_validation_matrix_v20.py",
    "theory_confirmation_verdict_v20.py",
    "ultimate_theory_gate_v20.py",
)
NO_WRITE_STOCHASTIC_REPORT_SOURCE = "global_flavour_fit_v20.py"
NO_WRITE_STOCHASTIC_REPORT_ORCHESTRATORS = (
    "prepare_validation_artifacts_v20.py",
    "replicate.py",
)
NO_WRITE_STOCHASTIC_REPORT_WORKFLOW = (
    ".github/workflows/replicate-and-falsify.yml"
)

RAW_SOURCE_PINS = {
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py":
        "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py":
        "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py":
        "9964606de2ef2a322536c6185342bc6e8fe61a46fb6ceeed9ab51d812c395b84",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py":
        "a6ca509755d352ddb17d8f8081a247cc55861b75c7f15f85b3a7a6b9218af85c",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py":
        "b848448fa6badfcb491136862b26ec9f6c80a0b509e2aad79fdb917be9eb7617",
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py":
        "cb54ad8b5222872187af404d3bbfa939157d4fb25db9941bc9ac3a6976fa0492",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py":
        "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json":
        "0efce9154b5b4204107cf211ff3c355641783353bf8d68ddb931f40994fdbb08",
    "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py":
        "a0641dfda3573cbd9343c65a4c26d7f89602bb4a21eb6e4ab8a360fa1d434e8f",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json":
        "91996a1e36b8169ffe5a8553f7efacf4586935aec7f971ad9689805049c62feb",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md":
        "a243c9b9de43fe8e5245e58dc1f3d0464dc93127cd1142317108e0518f4954f9",
}
GLOBAL_PHI_CLASSIFICATION_RAW_PINS = {
    "FROZEN_EXACT_SIGNED_KAEHLER_FULL126_STRONG_OPERATOR_SOURCE_V20.py": (
        "c7ad27cc1566e743f762f675dabfcfb0ccc499c8acf5c5956c2bf768a90eb771"
    ),
    "FROZEN_PHI_SELF_ZERO_GLOBAL_SEXTIC_SYZYGY_SOURCE_V20.py": (
        "0ad2c69915d0b758342d68c568c9d29c5bd80c0e39c0ab686824eba1a1350a8c"
    ),
    "FROZEN_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION_SOURCE_V20.py": (
        GLOBAL_PHI_CLASSIFICATION_SOURCE_SHA256
    ),
    "FROZEN_PHI_ZERO_CUBIC_CAUCHY_BRIDGE_SOURCE_V20.py": (
        "01b1bb5f450521506bf6a025650629691ce738325d1f16c5aafc050abe34e1c7"
    ),
    "FROZEN_PHI_ZERO_DEGREE8_CONDUCTOR_IDENTITY_SOURCE_V20.py": (
        "92c5b244daa40ec423c6292f3816f6c87395ce31fe7aebe73dd264a5596f44df"
    ),
    "FROZEN_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_SOURCE_V20.py": (
        "0bdb091d506a1fc180dbd68fa1c32b7bdb09084a78bcf86ebedad2aa2d2bc9f6"
    ),
    "FROZEN_SIGNED_KAEHLER_FULL126_PHYSICAL_SUBTRACTION_SOURCE_V20.py": (
        "911f9566cbdc957e2ec8bbf90f6d3546505a03e1bd76d66d85267a0536066c1a"
    ),
    "FROZEN_SIGNED_KAEHLER_P0_FULL126_KERNEL_RADIAL_STRICTNESS_SOURCE_V20.py": (
        "73819bb79be24a1cc2234c87b90bfb4bc2029e00c41fdedfa491bb89b9f06c4f"
    ),
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_EVALUATION_TABLE.json": (
        "beab3649ca03c3ee3c6fc2ab700efedfe614328a6da52f2234d3b9610f3c167c"
    ),
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_CHECKPOINT.json": (
        "0afad3c1a1de58243d27fd07fe550c90ca516e1c5483c027bcbd8e752e892179"
    ),
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_SOLUTION.json": (
        "c49833b4f90b0b5a6604d4d5aded36ea00944dd198d2ceefd8def8213174dcfa"
    ),
    "exact_phi_zero_o10_degree8_invariant_split_v20.py": (
        "6a80a8f95efc1f4515b8b8e9120c4011df5d378ebeb38f59f6119c73308daa90"
    ),
    "reconstruct_exact_phi_zero_degree8_radical_v20.py": (
        "8c835c5df2bce72d263117061fde770d53bb7d607cd305cc4a6a039466529133"
    ),
    "reconstruct_exact_phi_zero_degree8_conductor_table_v20.py": (
        "968c4f63bbc4a1eb213a335d10ee465e8f27621b79c9ce860ca187702f49bbc9"
    ),
    "solve_exact_phi_zero_degree8_conductor_identity_v20.py": (
        "3679695424452230c1583088b83291a7671348cfa90deb872cba51f2a07eceb0"
    ),
    "exact_phi_zero_degree8_conductor_identity_v20.py": (
        "d8587194b647a49f2b9950aebb920ee7a3c7f28f9f0823d8257676fe70e81fd9"
    ),
    "exact_phi_zero_cubic_cauchy_bridge_v20.py": (
        "282307be1abfe6d8d59c4e63861dbd5f8b4cf01d488d5df8793c27e029060bb0"
    ),
    "exact_phi_self_zero_global_sextic_syzygy_v20.py": (
        "5de73274c9def8bbc9628895457065fb1a93536eb611288dd66ffa6e1f8b2766"
    ),
    "exact_phi_self_zero_global_signed_kaehler_classification_v20.py": (
        "6887429cebbe0e0ee9171b9346b85c671959c2fdbc2b5187efc73a52552b0883"
    ),
}
RHS_PORTABLE_SOURCE_PINS = {
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py":
        "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py":
        "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py":
        "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py":
        "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49",
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py":
        "e2499baf3f7a572df7647ca02f109666a549c9e2c1989110c682ee584e0483c6",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json":
        "056e1a90c028f0aaca8fb17f2f53dfb02d5e7a33230ec3675537d2778755266a",
}

RAW_INTEGRATION_PATHS = (
    ".gitattributes",
    "axion_so10_theory_v20.pdf",
    "corrected_rank1_endpoint_v21.py",
    "freeze_corrected_rank1_endpoint_v21_integration.py",
    "test_freeze_corrected_rank1_endpoint_v21_integration.py",
) + PUBLICATION_PATHS + tuple(RAW_SOURCE_PINS) + tuple(
    GLOBAL_PHI_CLASSIFICATION_RAW_PINS
)

GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS = (
    "EXACT_PHI_SELF_ZERO_GLOBAL_SEXTIC_SYZYGY.md",
    "EXACT_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION.md",
    "EXACT_PHI_ZERO_CUBIC_CAUCHY_BRIDGE.md",
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_IDENTITY.md",
    "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.md",
    "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.md",
    "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
    "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
    "test_exact_phi_zero_degree8_conductor_identity_v20.py",
    "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
    "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
    "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
    "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
    "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
)

PORTABLE_INTEGRATION_PATHS = (
    WORKFLOW_PATHS + GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS + (
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.md",
    "G1_G8_EXECUTION_ROADMAP_V20.json",
    "G1_G8_EXECUTION_ROADMAP_V20.md",
    "G1_G8_GATE_LEDGER_V20.json",
    "G1_G8_GATE_LEDGER_V20.md",
    "README.md",
    "THEORY_VALIDATION_MATRIX_V20.md",
    "THEORY_VALIDATION_MATRIX_V20_VERDICT.json",
    "VALIDATION_EXECUTION_V20.md",
    "VALIDATION_EXECUTION_V20_VERDICT.json",
    "SHA256SUMS",
    "axion_so10_theory_v20.tex",
    "final_g3_acceptance_gate_v20.py",
    "g1_g8_execution_roadmap_v20.py",
    "g1_g8_gate_ledger_v20.py",
    "global_flavour_fit_v20.py",
    "prepare_validation_artifacts_v20.py",
    "replicate.py",
    "test_corrected_rank1_endpoint_v21.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
    "test_final_g3_acceptance_gate_v20.py",
    "test_g1_g8_execution_roadmap_v20.py",
    "test_g1_g8_gate_ledger_v20.py",
    "test_global_flavour_fit_v20.py",
    "test_prepare_validation_artifacts_v20.py",
    "test_replicate_v20.py",
    "test_theory_validation_matrix_v20.py",
    "test_validate_release_v20.py",
    "theory_validation_matrix_v20.py",
    "validate_release_v20.py",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
    )
)

QUARANTINED_SIGMA35_PATHS = (
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_SIGMA35_ORBITS_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_SIGMA35_ORBITS_V20.md",
    "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20.py",
    "test_exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20.py",
)

CHECKSUM_REQUIRED_PATHS = (
    ".gitattributes",
    "corrected_rank1_endpoint_v21.py",
    "freeze_corrected_rank1_endpoint_v21_integration.py",
    "test_corrected_rank1_endpoint_v21.py",
    "test_freeze_corrected_rank1_endpoint_v21_integration.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
) + WORKFLOW_PATHS + PUBLICATION_PATHS + tuple(
    GLOBAL_PHI_CLASSIFICATION_RAW_PINS
) + GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS


def _raw_payload(path: Path) -> bytes:
    return path.read_bytes()


def _portable_payload(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _inventory_row(relative: str, mode: str) -> dict[str, Any]:
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ArithmeticError(f"integration path escaped repository: {relative}") from error
    if path.is_symlink() or not path.is_file():
        raise ArithmeticError(f"integration inventory member is not a regular file: {relative}")
    payload = _raw_payload(path) if mode == "raw" else _portable_payload(path)
    return {
        "content_sha256": _sha256(payload),
        "content_size_bytes": len(payload),
        "hash_mode": mode,
        "role": _role(relative),
    }


def _role(relative: str) -> str:
    if relative in PUBLICATION_PATHS:
        return "audited corrected v21 publication byte"
    if relative in GLOBAL_PHI_CLASSIFICATION_RAW_PINS:
        return "byte-pinned exact global Phi self-zero proof dependency"
    if relative in RAW_SOURCE_PINS or relative in RHS_PORTABLE_SOURCE_PINS:
        return "generation-only byte-pinned structural dependency"
    if relative in WORKFLOW_PATHS:
        return "CI orchestration and claim-boundary enforcement"
    if relative in {
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
    }:
        return "superseded invalid historical artifact; structural routes only"
    if relative.endswith(".pdf") or relative.endswith(".tex"):
        return "corrected theorem manuscript"
    if relative.startswith("test_"):
        return "fail-closed central integration regression"
    if relative.endswith(".json") or relative.endswith(".md"):
        return "regenerated central report or documentation"
    if relative == "SHA256SUMS":
        return "release-core portable checksum manifest"
    return "central corrected-endpoint integration source"


def _require_source_pins() -> None:
    for relative, expected in RAW_SOURCE_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(f"raw generation dependency drifted: {relative}")
    for relative, expected in RHS_PORTABLE_SOURCE_PINS.items():
        observed = _sha256(_portable_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(f"portable RHS dependency drifted: {relative}")
    for relative, expected in GLOBAL_PHI_CLASSIFICATION_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw global Phi classification dependency drifted: {relative}"
            )


def _require_publication_inventory() -> None:
    directory = ROOT / "corrected_rank1_publication_v21"
    if (directory / "__pycache__").exists():
        raise ArithmeticError("publication __pycache__ is forbidden")
    observed = {path.name for path in directory.iterdir()}
    if observed != set(PUBLICATION_FILES) or any(
        not path.is_file() for path in directory.iterdir()
    ):
        raise ArithmeticError("corrected publication inventory drifted")
    nested = directory / (
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json"
    )
    if _sha256(nested.read_bytes()) != PUBLICATION_MANIFEST_SHA256:
        raise ArithmeticError("audited publication manifest hash drifted")


def _require_workflow_contract() -> dict[str, int]:
    consumer_text = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative in CORRECTED_CONSUMER_WORKFLOWS
    )
    all_text = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8") for relative in WORKFLOW_PATHS
    )
    heredocs = len(re.findall(r"corrected\s*=\s*central_view\(", consumer_text))
    legacy_rejections = len(
        re.findall(
            r"assert not gate_ledger\."
            r"_rank1_su4_augmented_sos_psd_target_exact\(",
            consumer_text,
        )
    )
    heavy = len(
        re.findall(
            r"heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_"
            r"system_v21\.py --check",
            all_text,
        )
    )
    if (heredocs, legacy_rejections, heavy) != (7, 7, 1):
        raise ArithmeticError(
            "workflow corrected-chain count drifted: "
            f"heredocs={heredocs}, legacy_rejections={legacy_rejections}, heavy={heavy}"
        )
    forbidden_runs = (
        "python exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
        "python -B exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
    )
    if any(token in all_text for token in forbidden_runs):
        raise ArithmeticError("a workflow executes the rejected legacy target generator")
    mutating_stabilizer_workflow = re.compile(
        rf"\bpython(?:\s+-B)?\s+{re.escape(FROZEN_STABILIZER_SOURCE)}"
        r"\s+--write\b"
    )
    if mutating_stabilizer_workflow.search(all_text):
        raise ArithmeticError("a workflow rewrites the frozen stabilizer dependency")
    for relative in WORKFLOW_PATHS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "compileall" in text:
            for line in text.splitlines():
                if "compileall" in line and "corrected_rank1_publication_v21" not in line:
                    raise ArithmeticError(
                        f"workflow compileall can contaminate publication: {relative}"
                    )
    mutating_stabilizer = re.compile(
        rf'["\']{re.escape(FROZEN_STABILIZER_SOURCE)}["\']\s*,\s*'
        r'["\']--write["\']'
    )
    read_only_report_commands = 0
    no_write_classification_commands = 0
    for relative in READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if FROZEN_STABILIZER_SOURCE not in text:
            raise ArithmeticError(
                f"frozen stabilizer validation is absent from orchestrator: {relative}"
            )
        if mutating_stabilizer.search(text):
            raise ArithmeticError(
                f"orchestrator rewrites the frozen stabilizer dependency: {relative}"
            )
        tree = ast.parse(text, filename=relative)
        for source in READ_ONLY_FROZEN_REPORT_SOURCES:
            commands = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.List, ast.Tuple)):
                    continue
                literals = {
                    item.value
                    for item in node.elts
                    if isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                }
                if source in literals:
                    commands.append(literals)
            if not commands:
                raise ArithmeticError(
                    f"frozen report validation is absent from orchestrator: "
                    f"{relative}: {source}"
                )
            if any("--write" in command for command in commands):
                raise ArithmeticError(
                    f"orchestrator rewrites a frozen validation report: "
                    f"{relative}: {source}"
                )
            read_only_report_commands += 1
        for source in NO_WRITE_FROZEN_CLASSIFICATION_SOURCES:
            commands = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.List, ast.Tuple)):
                    continue
                literals = {
                    item.value
                    for item in node.elts
                    if isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                }
                if source in literals:
                    commands.append(literals)
            if not commands:
                raise ArithmeticError(
                    f"frozen classification gate is absent from orchestrator: "
                    f"{relative}: {source}"
                )
            if any("--no-write" not in command for command in commands):
                raise ArithmeticError(
                    f"orchestrator rewrites a frozen classification report: "
                    f"{relative}: {source}"
                )
            no_write_classification_commands += len(commands)
    no_write_stochastic_report_commands = 0
    for relative in NO_WRITE_STOCHASTIC_REPORT_ORCHESTRATORS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        tree = ast.parse(text, filename=relative)
        commands = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.List, ast.Tuple)):
                continue
            literals = {
                item.value
                for item in node.elts
                if isinstance(item, ast.Constant)
                and isinstance(item.value, str)
            }
            if NO_WRITE_STOCHASTIC_REPORT_SOURCE in literals:
                commands.append(literals)
        if not commands:
            raise ArithmeticError(
                "stochastic frozen report validation is absent from "
                f"orchestrator: {relative}"
            )
        if any("--no-write" not in command for command in commands):
            raise ArithmeticError(
                "orchestrator rewrites the stochastic frozen report: "
                f"{relative}: {NO_WRITE_STOCHASTIC_REPORT_SOURCE}"
            )
        no_write_stochastic_report_commands += len(commands)
    workflow_text = (ROOT / NO_WRITE_STOCHASTIC_REPORT_WORKFLOW).read_text(
        encoding="utf-8"
    )
    workflow_commands = re.findall(
        rf"\bpython(?:\s+-B)?\s+"
        rf"{re.escape(NO_WRITE_STOCHASTIC_REPORT_SOURCE)}([^\n]*)",
        workflow_text,
    )
    if len(workflow_commands) != 1 or "--no-write" not in workflow_commands[0]:
        raise ArithmeticError(
            "workflow rewrites the stochastic frozen report: "
            f"{NO_WRITE_STOCHASTIC_REPORT_WORKFLOW}: "
            f"{NO_WRITE_STOCHASTIC_REPORT_SOURCE}"
        )
    return {
        "corrected_assertion_heredocs": heredocs,
        "legacy_rejection_assertions": legacy_rejections,
        "full_source_rebuild_invocations": heavy,
        "read_only_frozen_dependency_orchestrators": len(
            READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS
        ),
        "read_only_frozen_report_sources": len(READ_ONLY_FROZEN_REPORT_SOURCES),
        "read_only_frozen_report_commands": read_only_report_commands,
        "no_write_frozen_classification_sources": len(
            NO_WRITE_FROZEN_CLASSIFICATION_SOURCES
        ),
        "no_write_frozen_classification_commands": (
            no_write_classification_commands
        ),
        "no_write_stochastic_report_orchestrators": len(
            NO_WRITE_STOCHASTIC_REPORT_ORCHESTRATORS
        ),
        "no_write_stochastic_report_commands": (
            no_write_stochastic_report_commands + len(workflow_commands)
        ),
    }


def _require_legacy_quarantine() -> dict[str, Any]:
    artifact = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
        ).read_text(encoding="utf-8")
    )
    physical = artifact.get("physical_target", {})
    scope = artifact.get("scope", {})
    if not (
        artifact.get("status")
        == "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY"
        and artifact.get("proof_grade") is False
        and artifact.get("rejection", {}).get("v20_physical_target_accepted")
        is False
        and physical.get("accepted_as_physical_target") is False
        and physical.get("full_graded_chart", {}).get("proof_grade") is False
        and physical.get("quartic", {}).get("proof_grade") is False
        and scope.get("legacy_physical_target_rejected") is True
        and scope.get("physical_target_formula_all_five_grades_constructed")
        is False
        and scope.get("physical_target_full_6585_row_vector_constructed")
        is False
    ):
        raise ArithmeticError("legacy v20 artifact is not fail-closed rejected")
    source = (
        ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
    ).read_text(encoding="utf-8")
    for token in (
        'STATUS = "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY"',
        "writing the rejected v20 physical target is permanently disabled",
        "no files were read or written",
        "return 2",
    ):
        if token not in source:
            raise ArithmeticError("legacy structural source quarantine drifted")
    return {
        "artifact_status": artifact["status"],
        "artifact_proof_grade": False,
        "public_report_render_write_entrypoints_disabled": True,
        "CLI_exit_code": 2,
        "CLI_writes_files": False,
        "private_structural_APIs_retained_for_v21_generation": True,
    }


def _require_checksum_coverage() -> int:
    lines = (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    entries: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\\]+)", line)
        if match is None or match.group(2) in entries:
            raise ArithmeticError("SHA256SUMS is malformed or has duplicate paths")
        entries[match.group(2)] = match.group(1)
    missing = sorted(set(CHECKSUM_REQUIRED_PATHS) - set(entries))
    if missing:
        raise ArithmeticError(f"release checksum lacks corrected paths: {missing}")
    if MANIFEST_NAME in entries:
        raise ArithmeticError("integration manifest must not form a checksum cycle")
    return len(entries)


def build_manifest() -> dict[str, Any]:
    if set(RAW_INTEGRATION_PATHS) & set(PORTABLE_INTEGRATION_PATHS):
        raise ArithmeticError("integration inventory modes overlap")
    inventory_paths = set(RAW_INTEGRATION_PATHS) | set(PORTABLE_INTEGRATION_PATHS)
    if MANIFEST_NAME in inventory_paths:
        raise ArithmeticError("integration manifest must exclude itself")
    if set(QUARANTINED_SIGMA35_PATHS) & inventory_paths:
        raise ArithmeticError("quarantined Sigma35 paths entered integration inventory")
    _require_publication_inventory()
    _require_source_pins()
    workflow_counts = _require_workflow_contract()
    legacy_quarantine = _require_legacy_quarantine()
    checksum_count = _require_checksum_coverage()
    inventory = {
        relative: _inventory_row(
            relative, "raw" if relative in RAW_INTEGRATION_PATHS else "portable-lf"
        )
        for relative in sorted(inventory_paths)
    }
    return {
        "schema": "so10-rank1-su4-corrected-endpoint-central-integration-v21",
        "status": "EXACT_CORRECTED_ENDPOINT_V21_CENTRAL_INTEGRATION_FROZEN",
        "manifest_self_excluded_by_definition": True,
        "inventory_count": len(inventory),
        "inventory": inventory,
        "publication_manifest_raw_sha256": PUBLICATION_MANIFEST_SHA256,
        "logical_pins": {
            "certificate_raw_sha256": CERTIFICATE_SHA256,
            "exact_coordinate_sha256": COORDINATE_SHA256,
            "exact_LDL_pivot_sha256": LDL_SHA256,
            "map_numerator_csr_sha256": MAP_SHA256,
            "target_numerator_sha256": TARGET_SHA256,
            "global_Phi_classification_source_raw_sha256": (
                GLOBAL_PHI_CLASSIFICATION_SOURCE_SHA256
            ),
            "global_Phi_classification_core_sha256": (
                GLOBAL_PHI_CLASSIFICATION_CORE_SHA256
            ),
        },
        "exact_dimensions": {
            "map_shape": [6585, 19594],
            "map_common_denominator": 256,
            "map_nnz": 138550,
            "target_common_denominator": 576000,
            "target_nonzero_count": 512,
            "coefficient_equalities": 6585,
            "strict_positive_Gram_blocks": 22,
            "strict_positive_LDL_pivots": 824,
        },
        "workflow_contract": workflow_counts,
        "legacy_v20_quarantine": legacy_quarantine,
        "release_checksum_entry_count": checksum_count,
        "generation_source_pins": {
            "map_raw_sha256": dict(sorted(RAW_SOURCE_PINS.items())),
            "global_Phi_classification_raw_sha256": dict(
                sorted(GLOBAL_PHI_CLASSIFICATION_RAW_PINS.items())
            ),
            "physical_RHS_portable_lf_sha256": dict(
                sorted(RHS_PORTABLE_SOURCE_PINS.items())
            ),
        },
        "claim_boundary": {
            "fixed_H": "h_-=(e0-i e1)/sqrt(2)",
            "fixed_Sigma": "q/4",
            "arbitrary_real_Phi_at_fixed_endpoint": True,
            "all_PD_equality_orbits_classified_exactly": True,
            "global_signed_kaehler_Phi_self_zero_classification_proved": True,
            "Dynkin_maximal_subgroup_classification_external_dependency": True,
            "quantitative_beta_global_coercivity_proved": False,
            "legacy_v20_physical_target_valid": False,
            "legacy_v20_primal_valid": False,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
        "quarantine": {
            "excluded_from_inventory": list(QUARANTINED_SIGMA35_PATHS),
            "touched_or_promoted": False,
        },
    }


def write_manifest() -> dict[str, Any]:
    report = build_manifest()
    MANIFEST.write_bytes(_canonical_json_bytes(report))
    return report


def check_manifest() -> dict[str, Any]:
    observed_bytes = MANIFEST.read_bytes()
    try:
        observed = json.loads(observed_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArithmeticError("integration manifest is not canonical JSON") from error
    expected = build_manifest()
    if observed_bytes != _canonical_json_bytes(observed):
        raise ArithmeticError("integration manifest is not sorted indent-2 UTF-8/LF")
    if observed != expected:
        raise ArithmeticError("integration manifest or intended path bytes drifted")
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
                "release_checksum_entry_count": report["release_checksum_entry_count"],
                "G3_closed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
