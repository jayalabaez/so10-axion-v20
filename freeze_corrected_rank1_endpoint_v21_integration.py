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
EFT_O6_CORE_SHA256 = (
    "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
)
EFT_FROZEN_GLOBAL_G3_THEOREM_CORE_SHA256 = (
    "37acd6063765c0a28469b2f22c4502824871674ca99853ec2c940617b9c46423"
)
EFT_GLOBAL_G3_THEOREM_CORE_SHA256 = (
    "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
)
EFT_G3_ACCEPTANCE_GATE_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
EFT_BETA_ZERO_BASE_HESSIAN_PAYLOAD_SHA256 = (
    "194740e7e90eeee33d5d772ab549df969e9665e3aebc1580c3319f58eee36930"
)
EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256 = (
    "7ea54d59138f8e5b66aad3d1f1ecb707c65ac9bb0f0e118a597daaccc136b568"
)
EFT_G4_MATHEMATICAL_GATE_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)
EFT_G5_MATHEMATICAL_GATE_CORE_SHA256 = (
    "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
)
EFT_G5_EXACT_GLOBAL_LOWER_BOUND = "-40661/20000"
EFT_G6_SPECTRUM_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
EFT_G6_MATHEMATICAL_GATE_CORE_SHA256 = (
    "e34b791478bf9cb00f951819cbfec45a99d51be776889d8a4e13cf1717eee738"
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
    "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
    "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
    "final_g3_eft_acceptance_gate_v20.py",
    "final_g4_eft_mathematical_gate_v20.py",
    "final_g5_eft_mathematical_gate_v20.py",
    "exact_eft_physical_scalar_spectrum_v20.py",
    "final_g6_eft_mathematical_gate_v20.py",
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
EFT_G3_RAW_PINS = {
    "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py": (
        "c113abf41ca9527528dc00d248fdfa3fcae990e39ba4b76251ca197167cbad23"
    ),
    "FROZEN_EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER_SOURCE_V20.py": (
        "c113abf41ca9527528dc00d248fdfa3fcae990e39ba4b76251ca197167cbad23"
    ),
    "test_exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py": (
        "bc8397bf74bc28ed7b372c508d65d843ad0baf1bd9078f25a141e700cbb25f65"
    ),
    "EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER.md": (
        "181632706a73d68f439083b9b3f95314d2be390aee9486caa527be3ab6f23917"
    ),
    "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py": (
        "d3b3368e8e640b285f43a106f5c236dc2780c01df4d71e88365cb607f35277f9"
    ),
    "FROZEN_EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3_SOURCE_V20.py": (
        "9db99e83a32eefd43c74f3fb006e0ef32c37162980c7abb031efdbb8422a360f"
    ),
    "test_exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py": (
        "dc9d424c0bd0247978c22d0c9384fdee208ed903578354286a704b208a681551"
    ),
    "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json": (
        "38520c5aed7a3a72dbede3e4358e5edb48c16f35a5bb31601864e1f8dc0e2271"
    ),
    "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.md": (
        "3de0990e13a5c6f9fd9e9663e9115a06b41b99cee32ac210090d09afa481e47b"
    ),
    "final_g3_eft_acceptance_gate_v20.py": (
        "bd67e726fb2f482ef415307943bacdc5a54a0ebeae757852fe4c40010d6a0af5"
    ),
    "test_final_g3_eft_acceptance_gate_v20.py": (
        "7520de4bc4176eb17b648b5f70a66a420a1b7999f855b389f8a2214c7fbf312a"
    ),
    "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json": (
        "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0"
    ),
    "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.md": (
        "93fb87a00d34069a0fa4dfacb7c7c41714d2eff64686cacfed2bfbae73fd9936"
    ),
}
EFT_G4_G5_RAW_PINS = {
    "final_g4_eft_mathematical_gate_v20.py": (
        "1ba0a11fa09b1893fa10ec940e9c7444ff54003e25623ab82f0796fe732f5d35"
    ),
    "test_final_g4_eft_mathematical_gate_v20.py": (
        "078b8dbc34c8003c9e5fa98a2adaa432238cacd5bd0a42278c9a0082334edd05"
    ),
    "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json": (
        "98664542a4e1bbfba233652737826b974963a31c2e86a15e2d73fda1457d987b"
    ),
    "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.md": (
        "e859af53c619b90c265e410d6ddc26a2f20c5aaf26269e9619250aa8fc4f70ce"
    ),
    "final_g5_eft_mathematical_gate_v20.py": (
        "54ccea280c911ad8999ba4a233651d4892c2f6a3d6751cde48e26a5ff5ab828b"
    ),
    "test_final_g5_eft_mathematical_gate_v20.py": (
        "8cdfe60bd8d568de58a76321ae954d6fbbcc00df19c27528d9bfae0bf61864ad"
    ),
    "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json": (
        "6d6e4fd9932a03e35146afb1bca850666e883aaed5e23b73b81f0f703e4e7db9"
    ),
    "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.md": (
        "4ed0d85930430c78b0fe8465e50bde9f4b114014c76c1708c6e332e0c4490d33"
    ),
}
EFT_G6_RAW_PINS = {
    "exact_eft_physical_scalar_spectrum_v20.py": (
        "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36"
    ),
    "test_exact_eft_physical_scalar_spectrum_v20.py": (
        "6867a703bc3fed1fa1b7a76696a2d2e34159df3fb6be3a2db907fbebd51137c4"
    ),
    "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json": (
        "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416"
    ),
    "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.md": (
        "0b356c55a231432bf72d1877f35664abe2457f095c926e538b371d412764c153"
    ),
    "final_g6_eft_mathematical_gate_v20.py": (
        "6ef314bf22e1d6ce43b382b5cb6e7673cef1e328f2f4c38abdafab6038edc150"
    ),
    "test_final_g6_eft_mathematical_gate_v20.py": (
        "841badaa0fb1931060159233fad85d378bcaf68b71944f02bdd280e197813570"
    ),
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json": (
        "85000f555eb3bc4e2e4bc49236a82ce2161987212906d78efd667bb52dd432f8"
    ),
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md": (
        "288c53bce177ac687cbf6ceee3c6d74808a1dde2e2b39e0ac5728ab577db5fba"
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
) + tuple(EFT_G3_RAW_PINS) + tuple(EFT_G4_G5_RAW_PINS) + tuple(
    EFT_G6_RAW_PINS
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
) + tuple(EFT_G3_RAW_PINS) + tuple(
    EFT_G4_G5_RAW_PINS
) + tuple(EFT_G6_RAW_PINS) + GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS


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
    if relative in EFT_G3_RAW_PINS:
        return "byte-pinned dimension-six EFT G3 theorem and acceptance bundle"
    if relative in EFT_G4_G5_RAW_PINS:
        return "byte-pinned dimension-six EFT mathematical G4/G5 gate bundle"
    if relative in EFT_G6_RAW_PINS:
        return "byte-pinned exact EFT scalar spectrum and mathematical G6 gate bundle"
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
    for relative, expected in EFT_G3_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(f"raw EFT G3 bundle member drifted: {relative}")
    for relative, expected in EFT_G4_G5_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw EFT G4/G5 bundle member drifted: {relative}"
            )
    for relative, expected in EFT_G6_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(f"raw EFT G6 bundle member drifted: {relative}")


def _source_string_constant(relative: str, name: str) -> str:
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"), filename=relative)
    values: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
            continue
        if not isinstance(node.value.value, str):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            values.append(node.value.value)
    if len(values) != 1:
        raise ArithmeticError(f"expected one string constant {name} in {relative}")
    return values[0]


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise ArithmeticError(f"the frozen EFT theorem {label} anchor drifted")
    return source.replace(old, new, 1)


def _require_eft_theorem_adapter_allowlist() -> dict[str, Any]:
    """Prove that production changes only two frozen integration anchors."""
    frozen_name = "FROZEN_EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3_SOURCE_V20.py"
    production_name = (
        "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py"
    )
    frozen = (ROOT / frozen_name).read_text(encoding="utf-8")
    production = (ROOT / production_name).read_text(encoding="utf-8")
    frozen_core = (
        'EXPECTED_CORE_SHA256 = "'
        + EFT_FROZEN_GLOBAL_G3_THEOREM_CORE_SHA256
        + '"'
    )
    production_core = (
        'EXPECTED_CORE_SHA256 = "' + EFT_GLOBAL_G3_THEOREM_CORE_SHA256 + '"'
    )
    expected = _replace_once(
        frozen, frozen_core, production_core, "production-core replacement"
    )
    frozen_equality_pin = """    "fixed_F_equality_source": (
        REPO / "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        "f0f3efd4cb930825523d3b70c285d2a85c37b1c19bfdbcf1363597c6e9a4ba52",
    ),"""
    production_equality_pin = """    "fixed_F_equality_source": (
        REPO / "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        (
            "53f8b5b6175f4c3a7a5b3ab49ef151be2baa91c4dcd3fdd4f4de07e15d002df6"
            if REPO == HERE
            else "f0f3efd4cb930825523d3b70c285d2a85c37b1c19bfdbcf1363597c6e9a4ba52"
        ),
    ),"""
    expected = _replace_once(
        expected,
        frozen_equality_pin,
        production_equality_pin,
        "production equality-source replacement",
    )
    if expected != production:
        raise ArithmeticError(
            "production EFT theorem differs from the frozen source outside "
            "the two allowlisted integration anchors"
        )
    return {
        "frozen_source": frozen_name,
        "production_source": production_name,
        "allowlisted_difference_count": 2,
        "differences": [
            "production core pin",
            "production-local equality-source raw pin",
        ],
        "all_other_bytes_identical": True,
    }


def _require_eft_g3_bundle() -> dict[str, Any]:
    if len(EFT_G3_RAW_PINS) != 13:
        raise ArithmeticError("the EFT G3 raw bundle must contain exactly 13 files")
    allowlist = _require_eft_theorem_adapter_allowlist()
    o6_source = "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py"
    o6_frozen = (
        "FROZEN_EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER_SOURCE_V20.py"
    )
    theorem_source = (
        "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py"
    )
    gate_source = "final_g3_eft_acceptance_gate_v20.py"
    theorem = json.loads(
        (ROOT / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json").read_text(
            encoding="utf-8"
        )
    )
    gate = json.loads(
        (ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    hessian = theorem.get("exact_stabilized_Hessian", {})
    flags = theorem.get("closure_flags", {})
    classification = gate.get("classification", {})
    checks = {
        "O6_frozen_equals_production": (
            (ROOT / o6_frozen).read_bytes() == (ROOT / o6_source).read_bytes()
        ),
        "O6_core_exact": (
            _source_string_constant(o6_source, "EXPECTED_CORE_SHA256")
            == EFT_O6_CORE_SHA256
        ),
        "theorem_source_core_exact": (
            _source_string_constant(theorem_source, "EXPECTED_CORE_SHA256")
            == EFT_GLOBAL_G3_THEOREM_CORE_SHA256
        ),
        "theorem_report_core_exact": (
            theorem.get("core_sha256") == EFT_GLOBAL_G3_THEOREM_CORE_SHA256
        ),
        "acceptance_source_core_exact": (
            _source_string_constant(gate_source, "EXPECTED_CORE_SHA256")
            == EFT_G3_ACCEPTANCE_GATE_CORE_SHA256
        ),
        "acceptance_report_core_exact": (
            gate.get("core_sha256") == EFT_G3_ACCEPTANCE_GATE_CORE_SHA256
        ),
        "beta_zero_Hessian_payload_exact": (
            hessian.get("beta_zero_base", {}).get("payload_sha256")
            == EFT_BETA_ZERO_BASE_HESSIAN_PAYLOAD_SHA256
        ),
        "stabilized_Hessian_payload_exact": (
            hessian.get("stabilized", {}).get("payload_sha256")
            == EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256
        ),
        "EFT_mathematical_G3_closed": (
            flags.get("G3_closed_for_EFT_extended_model") is True
            and classification.get("mathematical_G3_closed_for_EFT_model") is True
        ),
        "renormalizable_G3_open": (
            flags.get("G3_closed_for_original_renormalizable_model") is False
            and classification.get(
                "mathematical_G3_closed_for_original_renormalizable_model"
            )
            is False
        ),
        "EFT_release_open": (
            classification.get("release_G3_verified_for_EFT_model") is False
        ),
        "G4_open": (
            flags.get("G4_closed") is False
            and classification.get("G4_closed") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the frozen EFT G3 logical bundle drifted: {failed}")
    return {
        "raw_file_count": len(EFT_G3_RAW_PINS),
        "theorem_adapter_allowlist": allowlist,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_eft_g4_g5_bundle() -> dict[str, Any]:
    if len(EFT_G4_G5_RAW_PINS) != 8:
        raise ArithmeticError("the EFT G4/G5 raw bundle must contain exactly 8 files")
    g4_source = "final_g4_eft_mathematical_gate_v20.py"
    g5_source = "final_g5_eft_mathematical_gate_v20.py"
    g4 = json.loads(
        (ROOT / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    g5 = json.loads(
        (ROOT / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    g4_classification = g4.get("classification", {})
    g4_geometry = g4.get("exact_EFT_witness_quotient_geometry", {})
    g4_hessian = g4.get("exact_Hessian_classification", {})
    g4_positive_kappa = g4_hessian.get("positive_kappa_family", {})
    g4_release_criteria = g4.get("release_criteria", {})
    g4_production_mapping = g4.get("production_mapping", {})
    g5_classification = g5.get("classification", {})
    g5_proof = g5.get("proof_reuse", {})
    g5_release_criteria = g5.get("release_criteria", {})
    g5_production_mapping = g5.get("production_mapping", {})
    checks = {
        "G4_source_core_exact": (
            _source_string_constant(g4_source, "EXPECTED_CORE_SHA256")
            == EFT_G4_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "G4_report_core_exact": (
            g4.get("core_sha256") == EFT_G4_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "G4_internal_checks_all_exact": (
            bool(g4.get("mathematical_checks"))
            and all(value is True for value in g4["mathematical_checks"].values())
        ),
        "G4_same_witness_orbit_ranks_exact": (
            g4_geometry.get("exact_tangent_ranks")
            == {
                "SO10": 36,
                "SO10_plus_U1X": 37,
                "SO10_plus_U1X_plus_PQ": 38,
            }
            and g4_geometry.get("source_binding_exact") is True
        ),
        "G4_physical_quotient_exact": (
            g4_geometry.get("real_field_dimension") == 486
            and g4_geometry.get("gauge_quotient_dimension_including_axion")
            == 449
            and g4_geometry.get("independent_PQ_axion_dimension") == 1
            and g4_geometry.get("massive_transverse_quotient_dimension") == 448
        ),
        "G4_Hessian_classification_exact": (
            g4_hessian.get("Hessian_rank") == 448
            and g4_hessian.get("Hessian_nullity") == 38
            and g4_hessian.get("negative_modes") == 0
            and g4_hessian.get("unexplained_zero_modes") == 0
            and g4_hessian.get("strictly_positive_massive_transverse_modes")
            == 448
            and g4_hessian.get("stabilized_payload_sha256")
            == EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256
        ),
        "G4_all_positive_kappa_exact": (
            g4_positive_kappa.get(
                "rank448_nullity38_for_every_positive_kappa"
            )
            is True
            and g4_positive_kappa.get("kernel_identity")
            == "ker H(kappa)=ker H0 intersect ker J for every kappa>0"
        ),
        "G4_claim_boundary_exact": (
            g4_classification.get("mathematical_G4_closed_for_EFT_model")
            is True
            and g4_classification.get(
                "mathematical_G4_closed_for_original_renormalizable_model"
            )
            is False
            and g4_classification.get("release_G4_verified_for_EFT_model")
            is False
            and g4_classification.get(
                "authoritative_renormalizable_G4_gate_mutated"
            )
            is False
        ),
        "G4_completed_integration_and_blockers_exact": (
            g4_release_criteria.get(
                "parallel_EFT_G4_integrated_into_release_orchestrators"
            )
            is True
            and g4_production_mapping.get("release_integration_completed")
            is True
            and "release_integration_required" not in g4_production_mapping
            and set(g4.get("release_blockers", ()))
            == {
                "Lambda_EFT_and_positive_Wilson_matching_approved",
                "radiative_stability_completed",
                "external_extended_model_contract_executed",
                "G1_promoted_closed",
                "G2_promoted_closed",
                "release_G3_verified_for_EFT_model",
            }
        ),
        "G5_source_core_exact": (
            _source_string_constant(g5_source, "EXPECTED_CORE_SHA256")
            == EFT_G5_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "G5_report_core_exact": (
            g5.get("core_sha256") == EFT_G5_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "G5_internal_checks_all_exact": (
            bool(g5.get("mathematical_checks"))
            and all(value is True for value in g5["mathematical_checks"].values())
        ),
        "G5_exact_global_lower_bound": (
            g5.get("exact_global_lower_bound") == EFT_G5_EXACT_GLOBAL_LOWER_BOUND
        ),
        "G5_reuses_frozen_exact_theorems": (
            g5_proof.get("kind")
            == "composition_of_existing_frozen_exact_theorems"
            and g5_proof.get("new_SOS_constructed_or_claimed") is False
            and g5_proof.get("EFT_theorem_core_sha256")
            == EFT_GLOBAL_G3_THEOREM_CORE_SHA256
            and g5_proof.get("O6_theorem_core_sha256") == EFT_O6_CORE_SHA256
            and g5_proof.get("immutable_EFT_G3_gate_core_sha256")
            == EFT_G3_ACCEPTANCE_GATE_CORE_SHA256
        ),
        "G5_claim_boundary_exact": (
            g5_classification.get("mathematical_G5_closed_for_EFT_model")
            is True
            and g5_classification.get("release_G5_verified_for_EFT_model")
            is False
            and g5_classification.get("authoritative_renormalizable_G5_closed")
            is False
            and g5_classification.get("authoritative_renormalizable_G5_mutated")
            is False
            and g5_classification.get("new_SOS_claimed") is False
        ),
        "G5_completed_integration_and_blockers_exact": (
            g5_release_criteria.get(
                "downstream_parallel_G5_integration_completed"
            )
            is True
            and g5_production_mapping.get("downstream_integration_completed")
            is True
            and set(g5.get("release_blockers", ()))
            == {
                "Lambda_EFT_and_positive_Wilson_matching_approved",
                "radiative_stability_completed",
                "external_extended_model_contract_executed",
                "G1_promoted_closed",
                "G2_promoted_closed",
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the frozen EFT G4/G5 logical bundle drifted: {failed}")
    return {
        "raw_file_count": len(EFT_G4_G5_RAW_PINS),
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_eft_g6_bundle() -> dict[str, Any]:
    if len(EFT_G6_RAW_PINS) != 8:
        raise ArithmeticError("the EFT G6 raw bundle must contain exactly 8 files")
    spectrum_source = "exact_eft_physical_scalar_spectrum_v20.py"
    gate_source = "final_g6_eft_mathematical_gate_v20.py"
    spectrum = json.loads(
        (ROOT / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json").read_text(
            encoding="utf-8"
        )
    )
    gate = json.loads(
        (ROOT / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    spectrum_classification = spectrum.get("classification", {})
    factorization = spectrum.get("exact_factorization", {})
    provenance = spectrum.get("stabilizer_provenance", {})
    sectors = provenance.get("sector_reports", {})
    mixing = spectrum.get("mixing_classification", {})
    quotient = spectrum.get("physical_quotient", {})
    uncertainty = spectrum.get("uncertainty_scope", {})
    scope = spectrum.get("scope", {})
    gate_classification = gate.get("classification", {})
    gate_release_criteria = gate.get("release_criteria", {})
    gate_summary = gate.get("spectrum_summary", {})
    expected_sector_dimensions = {
        "C0_Q0": (24, 4, 20),
        "C0_Q1": (24, 4, 20),
        "C16_Q0": (102, 18, 84),
        "C16_Q1": (96, 12, 84),
        "C36_Q0": (56, 0, 56),
        "C36_Q1": (64, 0, 64),
        "C40_Q0": (48, 0, 48),
        "C40_Q1": (72, 0, 72),
    }
    observed_sector_dimensions = {
        name: (
            row.get("full_real_dimension"),
            row.get("zero_dimension"),
            row.get("massive_real_dimension"),
        )
        for name, row in sectors.items()
    }
    checks = {
        "spectrum_source_core_exact": (
            _source_string_constant(spectrum_source, "EXPECTED_CORE_SHA256")
            == EFT_G6_SPECTRUM_CORE_SHA256
        ),
        "spectrum_report_core_exact": (
            spectrum.get("core_sha256") == EFT_G6_SPECTRUM_CORE_SHA256
        ),
        "gate_source_core_exact": (
            _source_string_constant(gate_source, "EXPECTED_CORE_SHA256")
            == EFT_G6_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "gate_report_core_exact": (
            gate.get("core_sha256") == EFT_G6_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "normalized_generalized_pencil_exact": (
            spectrum.get("normalization", {}).get("gamma") == "1/20"
            and spectrum.get("normalization", {}).get("Lambda_EFT") == "1"
            and spectrum.get("normalization", {}).get("raw_Hessian_denominator")
            == 25_200_000
            and spectrum.get("normalization", {}).get("kinetic_metric_times_100")
            == {
                "H10": 100,
                "Phi17": 200,
                "Phi210": 10,
                "S": 8,
                "Sigma126bar": 1,
            }
            and spectrum.get("normalization", {}).get("generalized_pencil")
            == "det(M-252000*x*K100)=0"
        ),
        "stabilized_Hessian_source_bound": (
            spectrum.get("source_binding", {}).get(
                "stabilized_Hessian_payload_sha256"
            )
            == EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256
            and spectrum.get("source_binding", {}).get(
                "expected_stabilized_Hessian_payload_sha256"
            )
            == EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256
            and spectrum.get("source_binding", {}).get("EFT_G4_core_sha256")
            == EFT_G4_MATHEMATICAL_GATE_CORE_SHA256
        ),
        "complete_exact_positive_factorization": (
            factorization.get("support_component_count") == 39
            and factorization.get("support_component_type_count") == 15
            and factorization.get("primitive_factor_count") == 45
            and factorization.get("distinct_mass_squared_root_count_including_zero")
            == 61
            and factorization.get("total_algebraic_degree") == 486
            and factorization.get("zero_multiplicity") == 38
            and factorization.get("positive_massive_multiplicity") == 448
            and factorization.get("all_roots_real_from_symmetric_positive_metric_pencil")
            is True
            and factorization.get("no_negative_roots_by_p_of_minus_x_coefficient_certificate")
            is True
            and factorization.get("all_nonzero_roots_strictly_positive") is True
        ),
        "SU3C_U1em_provenance_exact": (
            provenance.get("unbroken_group") == "SU(3)_C x U(1)_em"
            and provenance.get("casimir12_eigenvalues") == [0, 16, 36, 40]
            and provenance.get("charge_squared_eigenvalues") == [0, 1]
            and provenance.get(
                "operators_commute_exactly_with_Hessian_and_kinetic_metric"
            )
            is True
            and observed_sector_dimensions == expected_sector_dimensions
        ),
        "exact_algebraic_mixing_complete": (
            mixing.get("complete") is True
            and mixing.get(
                "projector_traces_reproduce_every_sector_factor_exponent"
            )
            is True
            and len(mixing.get("component_signatures", ())) == 39
        ),
        "physical_quotient_and_PQ_axion_exact": (
            quotient.get("ambient_real_dimension") == 486
            and quotient.get("Hessian_kernel_dimension") == 38
            and quotient.get("gauged_tangent_dimension") == 37
            and quotient.get("physical_PQ_axion_count") == 1
            and quotient.get("gauge_quotient_dimension") == 449
            and quotient.get("massive_positive_dimension") == 448
            and quotient.get("all_38_zero_modes_are_unphysical") is False
        ),
        "spectrum_claim_boundary_exact": (
            spectrum_classification.get(
                "EFT_dimension6_tree_level_mathematical_G6_closed"
            )
            is True
            and spectrum_classification.get("EFT_release_G6_verified") is False
            and spectrum_classification.get(
                "renormalizable_authoritative_G6_closed"
            )
            is False
            and scope.get("EFT_tree_level_mathematical_spectrum_complete") is True
            and scope.get("authoritative_renormalizable_G6_closed") is False
            and scope.get("EFT_release_G6_verified") is False
            and scope.get("authoritative_G6_acceptance_satisfied") is False
        ),
        "tree_level_exactness_and_release_uncertainties_exact": (
            uncertainty.get("exact_algebraic_tree_level_uncertainty") == "0"
            and uncertainty.get("root_intervals_are_rendering_certificates_not_physical_errors")
            is True
            and uncertainty.get("absolute_scale_and_Wilson_matching_complete")
            is False
            and uncertainty.get("loop_and_pole_mass_corrections_complete")
            is False
            and uncertainty.get("renormalization_scheme_and_running_complete")
            is False
            and uncertainty.get("physical_threshold_uncertainties_complete")
            is False
        ),
        "gate_internal_checks_all_exact": (
            bool(gate.get("mathematical_checks"))
            and all(value is True for value in gate["mathematical_checks"].values())
        ),
        "gate_upstream_cores_exact": (
            gate.get("upstream_cores")
            == {
                "G4": EFT_G4_MATHEMATICAL_GATE_CORE_SHA256,
                "G5": EFT_G5_MATHEMATICAL_GATE_CORE_SHA256,
                "spectrum": EFT_G6_SPECTRUM_CORE_SHA256,
            }
        ),
        "gate_summary_exact": (
            gate_summary.get("ambient_real_fields") == 486
            and gate_summary.get("gauge_quotient_dimension") == 449
            and gate_summary.get("physical_PQ_axions") == 1
            and gate_summary.get("positive_massive_modes") == 448
            and gate_summary.get("primitive_factors") == 45
            and gate_summary.get("distinct_mass_squared_roots_including_zero")
            == 61
            and gate_summary.get("residual_group") == "SU(3)_C x U(1)_em"
            and gate_summary.get("mixing_subspaces_complete") is True
        ),
        "gate_claim_boundary_exact": (
            gate_classification.get("mathematical_G6_closed_for_EFT_model")
            is True
            and gate_classification.get("release_G6_verified_for_EFT_model")
            is False
            and gate_classification.get("authoritative_renormalizable_G6_closed")
            is False
            and gate_classification.get("authoritative_G6_gate_mutated") is False
            and gate_classification.get("whole_model_validated") is False
        ),
        "gate_completed_integration_and_blockers_exact": (
            gate_release_criteria.get("mathematical_tree_level_EFT_G6_complete")
            is True
            and gate_release_criteria.get(
                "parallel_EFT_G6_integrated_into_release_orchestrators"
            )
            is True
            and set(gate.get("release_blockers", ()))
            == {
                "absolute_Lambda_EFT_and_Wilson_matching_approved",
                "loop_running_and_pole_mass_spectrum_complete",
                "threshold_uncertainty_budget_complete",
                "external_extended_model_contract_executed",
                "authoritative_G1_closed",
                "authoritative_G2_closed",
                "authoritative_renormalizable_G3_G4_G5_closed",
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the frozen EFT G6 logical bundle drifted: {failed}")
    return {
        "raw_file_count": len(EFT_G6_RAW_PINS),
        "checks": checks,
        "all_checks_pass": True,
    }


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
    expected_read_only_commands = (
        len(READ_ONLY_FROZEN_REPORT_SOURCES)
        * len(READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS)
    )
    if (
        len(READ_ONLY_FROZEN_REPORT_SOURCES) != 17
        or expected_read_only_commands != 51
        or read_only_report_commands != expected_read_only_commands
    ):
        raise ArithmeticError(
            "read-only frozen report command census drifted: "
            f"sources={len(READ_ONLY_FROZEN_REPORT_SOURCES)}, "
            f"commands={read_only_report_commands}, "
            f"expected={expected_read_only_commands}"
        )
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
    eft_g3_bundle = _require_eft_g3_bundle()
    eft_g4_g5_bundle = _require_eft_g4_g5_bundle()
    eft_g6_bundle = _require_eft_g6_bundle()
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
            "EFT_O6_current_endomorphism_core_sha256": EFT_O6_CORE_SHA256,
            "EFT_global_G3_theorem_core_sha256": (
                EFT_GLOBAL_G3_THEOREM_CORE_SHA256
            ),
            "EFT_G3_acceptance_gate_core_sha256": (
                EFT_G3_ACCEPTANCE_GATE_CORE_SHA256
            ),
            "EFT_beta_zero_base_Hessian_payload_sha256": (
                EFT_BETA_ZERO_BASE_HESSIAN_PAYLOAD_SHA256
            ),
            "EFT_stabilized_Hessian_payload_sha256": (
                EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256
            ),
            "EFT_G4_mathematical_gate_core_sha256": (
                EFT_G4_MATHEMATICAL_GATE_CORE_SHA256
            ),
            "EFT_G5_mathematical_gate_core_sha256": (
                EFT_G5_MATHEMATICAL_GATE_CORE_SHA256
            ),
            "EFT_G5_exact_global_lower_bound": EFT_G5_EXACT_GLOBAL_LOWER_BOUND,
            "EFT_G6_spectrum_core_sha256": EFT_G6_SPECTRUM_CORE_SHA256,
            "EFT_G6_mathematical_gate_core_sha256": (
                EFT_G6_MATHEMATICAL_GATE_CORE_SHA256
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
        "EFT_G3_bundle": eft_g3_bundle,
        "EFT_G4_G5_bundle": eft_g4_g5_bundle,
        "EFT_G6_bundle": eft_g6_bundle,
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
            "EFT_G3_raw_sha256": dict(sorted(EFT_G3_RAW_PINS.items())),
            "EFT_G4_G5_raw_sha256": dict(
                sorted(EFT_G4_G5_RAW_PINS.items())
            ),
            "EFT_G6_raw_sha256": dict(sorted(EFT_G6_RAW_PINS.items())),
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
            "renormalizable_G3_closed": False,
            "EFT_dimension6_mathematical_G3_closed": True,
            "EFT_release_G3_verified": False,
            "renormalizable_G4_closed": False,
            "EFT_dimension6_mathematical_G4_closed": True,
            "EFT_release_G4_verified": False,
            "renormalizable_G5_closed": False,
            "EFT_dimension6_mathematical_G5_closed": True,
            "EFT_release_G5_verified": False,
            "authoritative_renormalizable_G6_closed": False,
            "EFT_dimension6_tree_level_mathematical_G6_closed": True,
            "EFT_release_G6_verified": False,
            "G4_closed": False,
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
