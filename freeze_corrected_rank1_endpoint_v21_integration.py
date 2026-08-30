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
LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
G6_SM_PROVENANCE_CORE_SHA256 = (
    "0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39"
)
EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256 = (
    "0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f"
)
EFT_G6_FORMAL_GATE_CORE_SHA256 = (
    "3b06ae240c7fce18723f0ce77966e894e688dee65f56859239ff5cf552b1323c"
)
AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_CORE_SHA256 = (
    "714796e4e8f1aa768d9e9f8434c6919aca854d33541b2bccc779f96933345752"
)
PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_CORE_SHA256 = (
    "63f097be00c5da69982909b79b5ac9c64c1080efa142ae5d419820fb260cbccf"
)
EFT_G7_FORMAL_RESTRICTION_CORE_SHA256 = (
    "93a8ea1abeb3cec2521cb043057b29646bd9c368f8e8bcc7e2d819f42a7dc741"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256 = (
    "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2"
)
NORMALIZED_YUKAWA_CGCS_CORE_SHA256 = (
    "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7"
)
PHYSICAL_SM_VACUUM_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256 = (
    "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256 = (
    "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256 = (
    "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
)
PHYSICAL_SM_VECTOR_RXI_CORE_SHA256 = (
    "ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93"
)
PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256 = (
    "eedc4bf7c068318f7cf597beaed25ff2eb5893951872475ade02ea8a91386aae"
)
PHYSICAL_SM_G8_FRONTIER_CORE_SHA256 = (
    "029dfd8b707825742c85b6d223a54ee964c76cf519496c5d5da28a7cad407fd5"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256 = (
    "5d6f01c0ed131dcbc2813fa93f0bd81987178f2dac051e67b6db538b5a55f13d"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256 = (
    "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256 = (
    "5c464a3e6725a8ba993d672667d16ea5fb6105b3f8015febcc90c7ea68640d59"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256 = (
    "07666dc9ea513c579ed5f82d19f9b636b21926f552dab49b4b02af288762348b"
)
PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256 = (
    "8c1aeffcd29a4f78c42014f92cf4bfa09823a6a2efbd660d512d6b014db99f43"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256 = (
    "8ddf130f5212db6e918425b093d9b68278f22154f43fc5c1734812f8057768be"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256 = (
    "1b91227393a4402a8433d7947c2b1ce954ebc69ff7fbcc4e8606c61afcfdfdbe"
)
EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256 = (
    "de92b2de859efa7a0c4f5fdfb642d9f1ff8e1b071057bc8d4c295f6e2b6f8337"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256 = (
    "eb11744d0dbc9ceb883e8a6063177d8e3e370b1dcdc2c4e3eba97541b53d8fc4"
)
CANONICAL_G1_G8_V21_DEFINITION_SHA256 = (
    "1ecc4a5ae0cb1c51a24438f56f4181a2e1cc03c0fc17bc4ca2c0ce522be75df5"
)
CANONICAL_G1_G8_V21_CORE_SHA256 = (
    "b1a0c9e89794b2e0dc252f874dc2625e04468932d679c1249e96980b71c36ed7"
)
CANONICAL_G1_DIM6_FRONTIER_CORE_SHA256 = (
    "0d58c47752aebebc9fc227dba8be3e7f88aba4528acc2415e8f8d3d2cf7c4838"
)
CANONICAL_G1_SUSYNO_CHANNEL_CORE_SHA256 = (
    "31e789c63e670c59e6db265946f3487afbc58bb0881d3a58dbbb900903eab549"
)
CANONICAL_G1_COMPLETE_RING_CORE_SHA256 = (
    "5ad999a8d1d3af208427aab841816fafb1c286b289fe826114e3fbaa98f6dfa9"
)
CANONICAL_G1_TRUSTED_VERIFIER_SHA256 = (
    "26f5dfe44355923b25e264871765b82b779c9bccaa86630b18254fd8a690f2d1"
)
CANONICAL_G1_G8_V21_PORTABLE_PINS = {
    "canonical_g1_g8_gauged_u1x_v21.py": (
        "4158df2bbef369d100ed95cf45a6428b3307cdf4da066f4664981b2c4d61dea0"
    ),
    "test_canonical_g1_g8_gauged_u1x_v21.py": (
        "58a150d146cb70f2287145cf809032767fa9bf6e0e00e6ee4ca200852d8b2e28"
    ),
    "CANONICAL_G1_G8_GAUGED_U1X_V21.json": (
        "b5c8977b97f6f14a12a66ec20c8ba278ff1f8406b22d823b3eac7d4028fa4d1d"
    ),
    "CANONICAL_G1_G8_GAUGED_U1X_V21.md": (
        "8645228be6ac24ba9958ad5ebd793dd2341093d16d8f10d78e1c524736d51101"
    ),
}
CANONICAL_G1_DIM6_PORTABLE_PINS = {
    "canonical_g1_scalar_ring_dim6_frontier_v21.py": "b9b48b93a2e440a2393b6e9b9c3d02a044293aecf7184834e01cf67f0df787a1",
    "test_canonical_g1_scalar_ring_dim6_frontier_v21.py": "595f4131cf10915e0804057c06fbf5ce7e0c77ecf442cd7a99c58d6ea0a1a1f4",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json": "30df5a88f55d0a4d5c683e4f63a013574fdd96ebd7ccb4ed3d8a214d09d24a95",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.md": "42c06fb69df6755b15db3bdbca462020aa9d5273c67e6722c6d07243f9e8f4d6",
    "canonical_g1_susyno_channel_basis_v21.wls": "3fae45e08c291ad80f916a2d851bba869c787eea0da50576177781cc9d8fe34e",
    "test_canonical_g1_susyno_channel_basis_v21.py": "ba70f83c9f7982d668b3b4ba3231d4f6e38025d5b9094372b71622816cf001cf",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json": "066e2ccd746d97ca562ca4f84957816a2d6babed10574112e8f7118ac23cd309",
    "canonical_g1_complete_operator_ring_dim6_v21.py": "37f6343b16f231b87a4e9b4f97c7ac563fe19f5b7a196bde02dfd286b13902e9",
    "verify_canonical_g1_complete_operator_ring_dim6_v21.py": CANONICAL_G1_TRUSTED_VERIFIER_SHA256,
    "test_canonical_g1_complete_operator_ring_dim6_v21.py": "9f33b814e089e819354ea10e9d36d22ed313c0f924af12f3b5cb53190fde6872",
    "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json": "1fe406910513c171006280edb137dd58ec4eaa01ea159c4b5a9ba97bad0def35",
    "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.md": "278d47f93a6b286019ccf8d416651bef4f839b18044986055591eb96ee98640a",
}
CANONICAL_G2_EXACT_BASIS_CORE_SHA256 = (
    "c731111ba16faaf1efaaebc83e57624e896a001e02f6ae5b6e63a07d00e3338c"
)
CANONICAL_G2_FULL_PROJECTION_CORE_SHA256 = (
    "31bf4ad11049db23694cbd92c423c7355ee26a376bb6ea5a8b7ea1e7be667225"
)
CANONICAL_G2_TRUSTED_VERIFIER_SHA256 = (
    "a13ceb61871da641fce3ca1146c9bb91d1045418686712e3373a56e4233370e7"
)
CANONICAL_G2_DIM6_PORTABLE_PINS = {
    "_g2_contraction_graphs.py": "c2d65e4ff5f90448bf5b58a4806a1d2229802bf76a59584c1353b721c1b1db44",
    "_g2_metric_rank_probe.py": "a218c18915718036827856644c9ebe0b73b6339b070850a00c57c75d03cdeb53",
    "canonical_g2_exact_contraction_basis_v21.py": "e02417b959d61acacd0d69a68d52b5b4427c4f0e8595b3d94627e5ad4608b75d",
    "test_canonical_g2_exact_contraction_basis_v21.py": "8917d6cd8dea2df95e3415db7d27d599f90d60a5d77b8974a0d06e94f8f1e7b6",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json": "e88c6ddd02818eebf80b554118a5cad14e8d16581430c95f43501e1a6d4736a2",
    "canonical_g2_full_component_projection_dim6_v21.py": "1a94943835eb11cd8e446cdce9925d5cd00bc8471d9bb58c55028b4faca3be66",
    "verify_canonical_g2_full_component_projection_dim6_v21.py": CANONICAL_G2_TRUSTED_VERIFIER_SHA256,
    "test_canonical_g2_full_component_projection_dim6_v21.py": "67e24697eedf0681b917ba70fee449a469432d704d6e7f38c82b2db2c55fc7d7",
    "test_verify_canonical_g2_full_component_projection_dim6_v21.py": "26598a42cf232c7d099352cd65fb07879bbddaf0d4b7c1e25bc8bdcf709cb524",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json": "e296118ab33c3421350b0720fc8c824b2e218c3d80ec9e6b7c84e7eada491dfd",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.md": "dea5c22194cfe3e4cebb6e0b4cc9464108991a100cf3f57c84f0538de221de46",
}
CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256 = (
    "1cf871141c5400d237b0ea9203afb10905e46a0c49a98ebe0fe047fcf6c189dc"
)
CANONICAL_G3_TRUSTED_VERIFIER_SHA256 = (
    "49bff6ba5b89f321565a30a762fd5559adfcbca1ee157943082acf770b9d461b"
)
CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS = {
    "canonical_g3_physical_ew_global_vacuum_v21.py": "d9cfab99505ac0fce0e7bdaad336a769dbb50ed29d02c73d9c9afc96dc81f99c",
    "verify_canonical_g3_physical_ew_global_vacuum_v21.py": CANONICAL_G3_TRUSTED_VERIFIER_SHA256,
    "test_canonical_g3_physical_ew_global_vacuum_v21.py": "b39a48688985948869b54eaf21d9b06b1e4a928ac40817d759e2d3e33c51d88b",
    "test_verify_canonical_g3_physical_ew_global_vacuum_v21.py": "8c81d43c6edb6d6ef03048fc4ff2073b8205509e85a71defc7a31687a58b1917",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json": "03b51b65a0a7d4e597d85acf914957b3f33f81c62f531ac03d62cb1d2fcfc565",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.md": "a7aa62b9a7838f99f7792ac3122571d3c26775a76efabaf522efc857fa7161ce",
}
CANONICAL_G1_G8_V21_NAMESPACE = "canonical.gauged_u1x.phenomenology.v21"
CANONICAL_G1_G8_V21_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
CANONICAL_G1_G8_V21_GATE_IDS = (
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G1.complete_operator_ring_dim6",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G2.full_component_projection_dim6",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G3.physical_ew_global_vacuum",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G4.protected_ew_hierarchy",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G5.calg_axion_phase_revalidation",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G6.full_nonsusy_two_loop_chain",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G7.physical_pole_threshold_spectrum",
    f"{CANONICAL_G1_G8_V21_NAMESPACE}.G8.unique_proton_lifetime_distribution",
)
CANONICAL_G1_G8_V21_REQUIRED_ARTIFACTS = (
    "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json",
    "CANONICAL_G4_PROTECTED_EW_HIERARCHY_V21.json",
    "CANONICAL_G5_CALG_AXION_PHASE_REVALIDATION_V21.json",
    "CANONICAL_G6_FULL_NONSUSY_TWO_LOOP_CHAIN_V21.json",
    "CANONICAL_G7_PHYSICAL_POLE_THRESHOLD_SPECTRUM_V21.json",
    "CANONICAL_G8_UNIQUE_PROTON_LIFETIME_V21.json",
)
CANONICAL_G1_G8_V21_TRUSTED_VERIFIER_PATHS = (
    "verify_canonical_g1_complete_operator_ring_dim6_v21.py",
    "verify_canonical_g2_full_component_projection_dim6_v21.py",
    "verify_canonical_g3_physical_ew_global_vacuum_v21.py",
    "verify_canonical_g4_protected_ew_hierarchy_v21.py",
    "verify_canonical_g5_calg_axion_phase_revalidation_v21.py",
    "verify_canonical_g6_full_nonsusy_two_loop_chain_v21.py",
    "verify_canonical_g7_physical_pole_threshold_spectrum_v21.py",
    "verify_canonical_g8_unique_proton_lifetime_distribution_v21.py",
)
CANONICAL_G1_G8_V21_VERIFIER_PROTOCOL = (
    "canonical_gauged_u1x_gate_verification_v1"
)
CANONICAL_G1_G8_V21_DEPENDENCIES = (
    (),
    (CANONICAL_G1_G8_V21_GATE_IDS[0],),
    (CANONICAL_G1_G8_V21_GATE_IDS[1],),
    (CANONICAL_G1_G8_V21_GATE_IDS[1], CANONICAL_G1_G8_V21_GATE_IDS[2]),
    (CANONICAL_G1_G8_V21_GATE_IDS[2], CANONICAL_G1_G8_V21_GATE_IDS[3]),
    CANONICAL_G1_G8_V21_GATE_IDS[1:5],
    CANONICAL_G1_G8_V21_GATE_IDS[1:5],
    CANONICAL_G1_G8_V21_GATE_IDS[4:7],
)
CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS = {
    "IRREDUCIBLE_GAP_CONTRACT_V20_LEGACY": {
        "binding_mode": "raw",
        "path": "irreducible_gap_closure_contract_v20.py",
        "raw_sha256": (
            "2121c87b0eadd001156a70ce08dd1b3e26ca205d15c438bf07773c114cf165c0"
        ),
    },
    "RENORMALIZABLE_SCALAR_CHAIN_V20": {
        "binding_mode": "semantic-definition",
        "definition_sha256": (
            "1b96316304b80a995a0d39b581d3d6d942599b0efaa69035562ff6f72c4f0e62"
        ),
        "path": "g1_g8_gate_ledger_v20.py",
        "semantic_projection": "gate_titles_and_dependency_DAG",
    },
}

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
    "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
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
    "exact_g6_sm_provenance_feasibility_v20.py",
    "exact_eft_g6_g7_parameterized_matching_v20.py",
    "final_g6_eft_mathematical_gate_v20.py",
    "exact_authoritative_so10_u1x_gauge_betas_v20.py",
    "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
    "exact_eft_g7_threshold_nonidentifiability_v20.py",
    "exact_physical_g7_component_threshold_contract_v20.py",
    "exact_normalized_so10_yukawa_cgcs_v20.py",
    "physical_sm_vacuum_local_feasibility_v20.py",
    "conditional_physical_sm_eft_hessian_spectrum_v20.py",
    "exact_physical_sm_heavy_vector_masses_v20.py",
    "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
    "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
    "exact_physical_sm_g6_g7_closure_frontier_v20.py",
    "exact_physical_sm_g8_identifiability_frontier_v20.py",
    "physical_sm_source_algebra_equality_frontier_v20.py",
    "exact_physical_sm_five_amplitude_equality_v20.py",
    "exact_physical_sm_hard_projector_hessians_v20.py",
    "exact_physical_sm_last_six_hessians_v20.py",
    "exact_physical_sm_37_row_aggregate_v20.py",
    "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
    "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
    "exact_gauged_u1x_g2_mathematical_closure_v20.py",
    "canonical_g1_scalar_ring_dim6_frontier_v21.py",
    "canonical_g1_complete_operator_ring_dim6_v21.py",
    "canonical_g2_exact_contraction_basis_v21.py",
    "canonical_g2_full_component_projection_dim6_v21.py",
    "canonical_g3_physical_ew_global_vacuum_v21.py",
    "canonical_g1_g8_gauged_u1x_v21.py",
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
LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS = {
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
}
G6_SM_PROVENANCE_RAW_PINS = {
    "exact_g6_sm_provenance_feasibility_v20.py": (
        "8bb67fb09c1cd3b57bf2c02e9ed7f1242a955c5a81ceb7d44dd48435c82618c1"
    ),
    "test_exact_g6_sm_provenance_feasibility_v20.py": (
        "433a6ebea359a5f2be2d1f43df69b02734ccbb4b61493bd2a6e780d95ba96690"
    ),
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json": (
        "a8daa4fb1dadbea48b25ad671a18f8d467384979769772be628a43f75054f6fa"
    ),
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.md": (
        "e3d05634421c4721003cb1916a3d02dc2d2b0c93bd58c03523bc927fa3793673"
    ),
}
G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS = {
    "exact_126bar_triplet_clebsch_v20.py": (
        "d94f37da94333fbf58e448ef6effb00e718191ed45b63bafdc0e2650ccdb0499"
    ),
    "exact_210_pati_salam_global_vacuum_v20.py": (
        "d98baa655cd5af9ccbc34fd2637670b7ceadedd5b2eccc10e1d6c000fda943c4"
    ),
    "live_g2_canonical_486_field_chart_v20.py": (
        "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e"
    ),
}
EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS = {
    "exact_eft_g6_g7_parameterized_matching_v20.py": (
        "4653653de5f7f29b8dd12b7a3d1e387aafab2a193137c08dc2e4be942dceee42"
    ),
    "test_exact_eft_g6_g7_parameterized_matching_v20.py": (
        "fa044432c6862a86f46b9edc807d6a07db204d35a301cc339b2345125cec3ef4"
    ),
    "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json": (
        "b1bbf35b23a272eadc0a8520f0dac32fb342c7f1f3886088db2d9158acfd5ae9"
    ),
    "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.md": (
        "18b061d39d0f9272227bc1a021c66b10e1b893e1cef11889b161c0023239e7e4"
    ),
}
EFT_G6_FORMAL_GATE_RAW_PINS = {
    "final_g6_eft_mathematical_gate_v20.py": (
        "16eba20b834ebca25b3a8b91d867ddee76b1676791b18aa86db32a6ebc77af4e"
    ),
    "test_final_g6_eft_mathematical_gate_v20.py": (
        "f5447ed457035110d292337a17fcbdb894d68b6064b740addf61fd402d54d68e"
    ),
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json": (
        "8bd98401ed6e2540ae7968a5b6a51a8e49abd98943252dec159c873d73a13f6c"
    ),
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md": (
        "4615263add89bd825f29dfd09a05bd242013af93847962ba5db5ad74b285c3e0"
    ),
}
AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS = {
    "exact_authoritative_so10_u1x_gauge_betas_v20.py": (
        "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6"
    ),
    "test_exact_authoritative_so10_u1x_gauge_betas_v20.py": (
        "1612dca09f3a6cdd6883e9cf96b0e12467b724d4267a3728557c9a8256aee7f6"
    ),
    "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json": (
        "f5c12e8b8f9ec40976f675a743d5fd5d8cf4e98ab2087d92e3cf855c756c75eb"
    ),
    "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.md": (
        "39b0c05284c7e66cef484df8b599c8bc963ad1237395fb6cf21428779ab1f3db"
    ),
}
PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS = {
    "pyrate3_so10_u1x_gauge_beta_replay_v20.py": (
        "74b70c7d403bd5fc1cefc30ab1a58dd5c6e74c99672c81e9b2a2c59e34a1c42a"
    ),
    "test_pyrate3_so10_u1x_gauge_beta_replay_v20.py": (
        "4fbf1eadf0bb5c6f3e9629a5ddab18743671118b84af709acb2053096fff18d5"
    ),
    "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json": (
        "e17dcc1dc939c8475b6827f4c781f3f5fce6c728cf5aa6511287066087b01fd4"
    ),
    "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.md": (
        "ffaeaa138f3831369d6b2b1b5617bc1148f62d3e8fe7f40a828a7c72c05aecfc"
    ),
    "models/SO10U1XGaugeAuditV20.model": (
        "18191bc9db705ed9e8a89eff214ad967bac37830c91fede82c418d38ce0c949e"
    ),
    "data/PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json": (
        "047632c3e81f8eb2dcc1cd922b8d3e34c300743693e18606ff8953e28ccd280b"
    ),
}
EFT_G7_FORMAL_RESTRICTION_RAW_PINS = {
    "exact_eft_g7_threshold_nonidentifiability_v20.py": (
        "16e4a011e759df3a31664bcac2711b5270598551f1e2791c8f629f9bb6483406"
    ),
    "test_exact_eft_g7_threshold_nonidentifiability_v20.py": (
        "6daed6acb85f751ba36699d712e5898f53934c9be8f52a6f79e4115237685989"
    ),
    "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json": (
        "778f96c8760a43be5214b215e08a6308d6198b84ebff9edd7729e75203b13cae"
    ),
    "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.md": (
        "fc46765cdf7e46f529d2a4a9ceabb308c7a3c5b74c249733ce2833dd70fb3d01"
    ),
}
PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS = {
    "exact_physical_g7_component_threshold_contract_v20.py": (
        "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0"
    ),
    "test_exact_physical_g7_component_threshold_contract_v20.py": (
        "bdceea8f8e10f566119793c0e0cfc31316bd9704aab89a1b70a9fdc880f7cd4a"
    ),
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json": (
        "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e"
    ),
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md": (
        "23b78d68d4732da2160d7b3911aa3ac0c7e6f9bce59e58228d4a6c755b21d071"
    ),
}
NORMALIZED_YUKAWA_CGCS_RAW_PINS = {
    "exact_normalized_so10_yukawa_cgcs_v20.py": (
        "432faa3fdf5adebf25015f7f2fda7f040d89d86bce31f6c85b4cc56e37eb14df"
    ),
    "test_exact_normalized_so10_yukawa_cgcs_v20.py": (
        "450321d322634630c3a6713d16f08fbefdba71b7b2bc886f0d95dc4dcf093a02"
    ),
    "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json": (
        "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b"
    ),
    "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md": (
        "5acbb5eb78451b8f37f1d8b990962a7ad4c39fe1974cb4720cf2131a85c14112"
    ),
}
NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS = {
    "direct_phi_h_sigmabar_tensor_v20.py": (
        "3a87470a06362a2a4c05eac6b71fe9cd4cd6c9b8a41732786184cbfeae89fac4"
    ),
    "spin10_referee_audit.py": (
        "daf80f5ab2b4480e5e03b025bd685dd1ffdce91a4cb0435774dd52ad702b72c9"
    ),
}
PHYSICAL_SM_VACUUM_RAW_PINS = {
    "physical_sm_vacuum_local_feasibility_v20.py": (
        "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c"
    ),
    "test_physical_sm_vacuum_local_feasibility_v20.py": (
        "3b688b8a2bd33a03e19edf4225568a3eaef96b4580f7d9ea23c38857dc069f5c"
    ),
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json": (
        "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315"
    ),
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md": (
        "d312fb960e7a458fadf38977573315a6d0a5eee37437c49c149589abd36416c3"
    ),
}
PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS = {
    "live_g2_arbitrary_component_potential_values_v20.py": (
        "997ab9e2a29c3125d47b006189b1ed69599644313b499754f7ee5e1e7e12d6bf"
    ),
    "live_g2_exact_final_mixed_quartic_derivatives_v20.py": (
        "50c3519de91dea74509b2e6383a930d8804680533bee7faf00f8f13415045ed1"
    ),
    "live_g2_exact_h10_self_quartic_derivatives_v20.py": (
        "1b05c3bc53525c71dc134dce7ff1f60321d5ce6d56eb8759e4ae91b87c8ba74f"
    ),
    "live_g2_exact_hsigma_hermitian_derivatives_v20.py": (
        "bd15f4c15585e49e7884558992c3ca14a1e9777282e747f98f31fb2d8e32b1af"
    ),
    "live_g2_exact_phi2_hdagh_derivatives_v20.py": (
        "a7ccc19d0fb31227f89695b64469918c5198000333c15f6f1ff10fa1a8eb9857"
    ),
    "live_g2_exact_phi_self_quartic_derivatives_v20.py": (
        "69e1fd25900b8264ede773d72c348303bc0a3eb951b4d0ab4a3eeaeda2ac94d8"
    ),
    "live_g2_exact_portal_family_derivatives_v20.py": (
        "5f4eb0d813be606c2cdae8f2fb382855ce313b507bb9e167161f9826a73e24c9"
    ),
    "live_g2_exact_quadratic_family_derivatives_v20.py": (
        "abdf1cf943908ff338208ce57bad4db2c70710ec36b9654eb56d06f3ca4aa9c8"
    ),
    "live_g2_exact_remaining_cubic_derivatives_v20.py": (
        "ee0ef9add618701d70910c2dffd1b9598ce93fd58e770c5cda18e137af565e6e"
    ),
    "live_g2_exact_sigma_self_quartic_derivatives_v20.py": (
        "69ca58a65803e79a996fc316e1d22134774469c177a9c5d2eb294b9d1c084ded"
    ),
    "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py": (
        "0157f4f92adec1f8e893732c86ab327a1615d9f7a862f6950244569940501592"
    ),
}
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS = {
    "conditional_physical_sm_eft_hessian_spectrum_v20.py": (
        "4d1c146f9ab9cd9679bdef7f5c145381c5d53871e62f79c1e59864a5aec981c9"
    ),
    "test_conditional_physical_sm_eft_hessian_spectrum_v20.py": (
        "80ea03cbc4c6079e937d0a133e40ef172e3ffa72f7b2aad36d587f0b5436033d"
    ),
    "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json": (
        "6a4354baac91881b796e70d86e529158fe8c51a0a2a9e1dc9ba876130c3510ef"
    ),
    "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md": (
        "60e5907263e06f9340d364ecd01f495b1cd470482a409f4ec6a27d86bdd6508e"
    ),
}
PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS = {
    "exact_physical_sm_heavy_vector_masses_v20.py": (
        "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587"
    ),
    "test_exact_physical_sm_heavy_vector_masses_v20.py": (
        "6f5bd8638cfdd593e722055f74c2de761865b4391720b1b4a11ae9089eb61b42"
    ),
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json": (
        "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0"
    ),
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md": (
        "47b598aed6af33a89ecc47598d5280258e0b5304a23a8873764c9c4778768fff"
    ),
}
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS = {
    "exact_physical_sm_heavy_vector_msbar_matching_v20.py": (
        "d6c69059b679342b0aff843044eef15e540f0c68836b41f432c878883aad3192"
    ),
    "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py": (
        "e3b9118379cb6bc83e63646c4147a056f5cadc3faed13bc9c25bf42882f83b46"
    ),
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json": (
        "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee"
    ),
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md": (
        "130ec2f078e429cc6b19c7d9013fb803d4ffad9069a24509120f6467f9e72afe"
    ),
}
PHYSICAL_SM_VECTOR_RXI_RAW_PINS = {
    "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py": (
        "5a850a37ac97043a4857002bbe96ab963380462a6ec17f1c43eb9a7a371e6a44"
    ),
    "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py": (
        "97275dad209ecef945b95b5dc9ec97b79b6d319346b8f769af5a9f9ae28d1aa7"
    ),
    "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json": (
        "e1553d18c5acb9fd738dfc8c16277a634ae42bca2960296656eee57a78101221"
    ),
    "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md": (
        "b549642e47656257c90b13361715c1602f202548ba4e01f068d26ffa163a4286"
    ),
}
PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS = {
    "exact_physical_sm_g6_g7_closure_frontier_v20.py": (
        "db811c803bfb008d800d79a422918548d72cc87081a966075789178d06fb5043"
    ),
    "test_exact_physical_sm_g6_g7_closure_frontier_v20.py": (
        "525f96ecadc331b3cd1041c457cb40c71fbd59ce8a987a83f7fafe167caf5535"
    ),
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json": (
        "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a"
    ),
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md": (
        "ffea781db860ee162b8a61252900c44315ae2b9afa24561e6395a1be4e16af3b"
    ),
}
PHYSICAL_SM_G8_FRONTIER_RAW_PINS = {
    "exact_physical_sm_g8_identifiability_frontier_v20.py": (
        "d4c294c4ea42e16764de3c8763e5e5a843e37958d4cd1bb57e10024900f93ee4"
    ),
    "test_exact_physical_sm_g8_identifiability_frontier_v20.py": (
        "6f2a5a249084517cf442e0e16856082b1a2b75e7e1e2cfcdda57fd3ef609d527"
    ),
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json": (
        "bb58ef10bef730cefa8da4cee342711e1033134a5e9468febed5cc0f8a93acac"
    ),
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md": (
        "b946701143bbbf68c1a528e1ac671e65066410808c49fdb906624cff25fc5c17"
    ),
}
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS = {
    "physical_sm_source_algebra_equality_frontier_v20.py": (
        "3ab97985eb2d178aa1d7b77d2c1e9e30f6134599456fce07e0a071856fc7557f"
    ),
    "test_physical_sm_source_algebra_equality_frontier_v20.py": (
        "e9d5200cbecdb22cbda4479607430f936e03e16b7c4663283abbbece99c7b770"
    ),
    "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json": (
        "96d00f47eb5365dd9ff43ace871a04252aeb4b3a5d2543f03870091ff78760f2"
    ),
    "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md": (
        "e2d7b84c06ba706991a4bb123df3894569f2ee14f330a1b64030ab7656fce9ed"
    ),
}
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS = {
    "exact_physical_sm_five_amplitude_equality_v20.py": (
        "777b11664047574432405373b71bf30ed473fa735bdce56ef95be43dccc76972"
    ),
    "test_exact_physical_sm_five_amplitude_equality_v20.py": (
        "23b5491460efa8bc09d4b4d978619df808f5c796baf07ae6a5aa271dd693049e"
    ),
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json": (
        "61bca8d55230b798b1d45ae4496c2b1b39490f73d0596e671478a388f72449ce"
    ),
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md": (
        "5a22cb172ff26ac698ca19bb722590cf15368c30d37190a211e5f5f1eff214d6"
    ),
}
PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS = {
    "gauged_u1x_g2_derivative_audit_v20.py": "584e03994ca1187228377c3e4c145d95446ade50616e2d58068e0fee9f96507d",
    "live_g1_tensor_closure_ledger_v20.py": "e17dd3a443ddd04ab412844f8d4273c27322371518bbc805705be9c030287d57",
    "exact_h10_self_quartic_family_v20.py": "a6a54818fce5a98b9e06d657581bb43482eb63a8598860840bc2553060b3f94e",
    "exact_210_self_invariant_basis_v20.py": "663747aa896d8609a0a12fb0bbf5374520ef4fc3a205b6525cbba66022654ae5",
    "exact_p_delta_second_stage_hessian_v20.py": "6f03a6305c9a302d6a1664c3100d1f629bd8af08ac303e5766d6ae463d35dc58",
    "exact_126bar_self_quartic_basis_v20.py": "6b945b21b991ad1c055e7ae39190bcbb258fd8503c1ad37789003310041ddd30",
    "exact_hsigma_hermitian_family_closure_v20.py": "1d27e3a089fd7b4e44f3534eb91c58a1505c8396ddc6301df6df87d07cac9863",
    "exact_phi2_126dag126_six_contractions_v20.py": "78bd1110530be968ab2e62d150c73def74fe96d1d1100ccfb88cb9c4710a6dba",
    "exact_phisigma_126bar_minus_projectors_v20.py": "35574f536dd6a5a6619075784324d3a8e5965544dd91fdca5ce2ce3de6bb2af7",
    "exact_phi2_hdagh_channel_family_v20.py": "42f347e5d8cb8d378f737425d7b152cc71e678627b8a2128b8faba0ce41261cf",
}
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS = {
    "exact_physical_sm_hard_projector_hessians_v20.py": (
        "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e"
    ),
    "test_exact_physical_sm_hard_projector_hessians_v20.py": (
        "08deeb86a522ba64eee0152b3f68f8fff9bdd75dac13aca9d855fee3652ed76b"
    ),
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json": (
        "b8a498926d1ba6a7f07f9c64b56443a14fba098514a8d5cb3e8358bbf7baabfa"
    ),
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md": (
        "47b44edaa79546d294fe7d2a50ae53de764259422967356d74b79235bddc2159"
    ),
}
PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS = {
    "exact_phisigma_casimir_projectors_v20.py": (
        "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355"
    ),
}
PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS = {
    "exact_physical_sm_last_six_hessians_v20.py": (
        "78d712d3573ec3377a331eb52dbf429452aa1c7ed82aeb7eeb0aa5900b3774ce"
    ),
    "test_exact_physical_sm_last_six_hessians_v20.py": (
        "1565454ca40608367e275a2a3cb2fb1a6b3277418a1479720e313431b5d9379f"
    ),
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json": (
        "fe1a92c3bc8e809c41abb88a85f3cf0198c88f7a70482b3f26359d6df78907c5"
    ),
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md": (
        "74117a1f5c8a8add31ff82d7034dda32061fb5349b1d8662453cfcc2b266590e"
    ),
}
PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS = {
    "exact_mixed_45_triplet_channel_v20.py": (
        "3ac36a491014d59bb4d08a0939e63cd7d5bde8aa9c7cde0bfc4b491521c1073c"
    ),
    "exact_physical_sm_easy_21_hessians_v20.py": (
        "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311"
    ),
}
PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS = {
    "exact_physical_sm_37_row_aggregate_v20.py": (
        "801b456743d9037d4478dcb3c94fef3d745ad312b58c3b262324aeded7567f5c"
    ),
    "test_exact_physical_sm_37_row_aggregate_v20.py": (
        "8af93e63ed0ffb06734d8cffe60c75a41811dbf5b765fc93e09fc2c3febc2f96"
    ),
    "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json": (
        "66bafa7e00ce543abea0e29b8be586cca8ecb1c5417204fc0ec75f6736c984b3"
    ),
    "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md": (
        "d0ddb600e27b69ad1f45af832fc4381006ef2471dfcf4b028b155b7210bb2fcd"
    ),
}
PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS = {
    "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json": (
        "bea6bb1b519eb42a610b6a0c66a6b7178e4f1f912aa154035aacecc815089ae8"
    ),
}
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS = {
    "exact_physical_sm_local_equality_orbit_v20.py": (
        "5358c084cd46bdf154fd42505e51d28dc75c6817d392e9bbad5b0d47c55184c7"
    ),
    "test_exact_physical_sm_local_equality_orbit_v20.py": (
        "100488ad2c0173134be41ef52e17c82cc9445fc481bf922d4c36a6b7fe0b8f12"
    ),
    "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json": (
        "4a443274dbd6e5f3887161dde5bbdb8e7410d4c951e307b7105587f99d9001c0"
    ),
    "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md": (
        "2284d1cd3666af797116d2d150963eae05be8be27420e85132f24e66de2a2ee7"
    ),
}
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS = {
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json": (
        "506dc21cffda5d25d7f6a86bb100a961186a9f54fe716d3a8daf4251c92248d3"
    ),
    "GAUGED_U1X_SCALAR_CONTRACT_V20.json": (
        "3244ed71f185f22441f73707a8a7ee34e9dcbcae3b1bcb478df560ccb2366375"
    ),
    "exact_gauged_u1x_physical_quotient_v20.py": (
        "405fd691d633d9b925af27c6bc0504bf741784198ae3b0c1fe83da7ca2284324"
    ),
}
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS = {
    "exact_physical_sm_g4_g5_branch_mismatch_v20.py": (
        "cf87a140b031ba625e2f656646402d0eb68aea3d34a555dc391274a198573251"
    ),
    "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py": (
        "4595149177660f51d7b17e5ef7425d55acfd748df38aad02911f22e96041b958"
    ),
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json": (
        "a94429e7838141cfd7a0860faa93b0a8ee23e9b8e8985222546ce552c9debe06"
    ),
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md": (
        "7cdde1e96c5a47da405ed3c8f89324b807a0032e087e36732d6b986e49cbba9e"
    ),
}
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS = {
    "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json": (
        "faeded3309949504b1b0e04ec9338db79dad0bf0dac29804f87a0fa1012beaee"
    ),
}
EXACT_X_V3_RAW_PINS = {
    "exact_x_symmetry_consistency_gate_v20.py": "5c70efb039b795f94a6b03e8681ad512af837c48f4496948f918eae7faa529d8",
    "test_exact_x_symmetry_consistency_gate_v20.py": "9397d65593994f9267845e08d92235a9b934cdea7053dcc7292c8c1f752253ee",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json": "c0393187fc07848a218830cc23cd59c1ecaaa091ea004f59b3777370ffcef2fa",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md": "d6c3d3cf2e38542206e8963c91190dfa377a0a3fa697292e576caa6faf3a2a49",
    "models/EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json": "1a6c8f8d79186801c840ddb63c30ee518b73c1929642be2139a7d01ed8c41a2f",
    "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json": "c28f08d56a488050b96ce3491473f22fe1b673aad8ac3ac3d0e590dd60e70d91",
    "models/SO10Z17AxionV20.m": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
    "tools/validate-exact-x-model.wls": "1d1dea122de1d3465cd0af14e10574b87bf72594de69e3a888fc7bcba5d1e281",
    "run_exact_x_sarah_validation_v20.py": "351435619bc45aa9b1bf1ebe2fbc4e9a92e14148c2881e0f37357a8df48d2057",
}
EXACT_X_V3_PORTABLE_PINS = {
    "nonsusy_z17_pq_potential_filter_v20.py": (
        "60e076e7841f60ab19da79ac090220b210cd5ee3c36243a6549fbb08da73a903"
    ),
    "models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json": (
        "f5108d94770b9525deff58ddd42f1ba623b54670f13b4809c3c0965217f4dc09"
    ),
}
LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256 = (
    "3b318e32a2ceb43dc26191c32026609ca121d66f9235f1b76a00f0a5da007fa5"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_TEST_RAW_SHA256 = (
    "162b1aad99ba90d18f707feb4baf6a2c3d05d8e00af8a382ac6493aedc6159e0"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS = {
    "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json": (
        "f9eedea44ae98547f94e123fa99ab38450c2c1c57b5871df624a78d6104dbcd9"
    ),
    "SARAH_PYRATE_SO10_210_BETAS_V20.md": (
        "3d6cc2869b56452e4a8bd6a3e30d5c932506b686db349f34b773166df35a4f44"
    ),
}
LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW = (
    ".github/workflows/sarah-pyrate-so10-210-betas.yml"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS = {
    "exact_gauged_u1x_g1_component_tensor_closure_v20.py": (
        "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f"
    ),
    "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py": (
        "084c168bb622b3a56ed06cc885571423135e375e48dbe99a616ab657fd4ebc3e"
    ),
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json": (
        "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
    ),
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.md": (
        "b5901f73551750524d369e8327c93b00ebb791c312e379dd571f2f6be915c955"
    ),
}
RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS = {
    "exact_gauged_u1x_g2_mathematical_closure_v20.py": (
        "5f56a55a7c9597918c530ad6c77252ed161a206ad0dffbf25651e32f4f590a8b"
    ),
    "test_exact_gauged_u1x_g2_mathematical_closure_v20.py": (
        "379bcbd4dd593a7865cdab4723f3d1b3122c276c4bad5bfcd8b07255c2dacd58"
    ),
    "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json": (
        "de105a206685a236dcddc4cb70d98d756d87b9641e02150c41493897e01f7ff0"
    ),
    "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.md": (
        "570c9ae557bf39ffb5bb54476bcb3e57fc05c47d06092ba5ea332af7bfe00ebc"
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
    LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS
) + tuple(
    G6_SM_PROVENANCE_RAW_PINS
) + tuple(
    G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS
) + tuple(
    EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS
) + tuple(
    EFT_G6_FORMAL_GATE_RAW_PINS
) + tuple(
    AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS
) + tuple(
    PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS
) + tuple(
    EFT_G7_FORMAL_RESTRICTION_RAW_PINS
) + tuple(
    PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS
) + tuple(
    NORMALIZED_YUKAWA_CGCS_RAW_PINS
) + tuple(
    PHYSICAL_SM_VACUUM_RAW_PINS
) + tuple(
    PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS
) + tuple(
    CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS
) + tuple(
    PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS
) + tuple(
    PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS
) + tuple(
    PHYSICAL_SM_VECTOR_RXI_RAW_PINS
) + tuple(
    PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_G8_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS
) + tuple(
    PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS
) + tuple(
    PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS
) + tuple(
    PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS
) + tuple(
    PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS
) + tuple(
    PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS
) + tuple(
    EXACT_X_V3_RAW_PINS
) + tuple(
    LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS
) + tuple(
    RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS
) + tuple(
    RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS
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
    WORKFLOW_PATHS
    + (LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW,)
    + GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS
    + tuple(NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS)
    + tuple(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS)
    + tuple(EXACT_X_V3_PORTABLE_PINS)
    + tuple(CANONICAL_G1_G8_V21_PORTABLE_PINS)
    + tuple(CANONICAL_G1_DIM6_PORTABLE_PINS)
    + tuple(CANONICAL_G2_DIM6_PORTABLE_PINS)
    + tuple(CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS)
    + (
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
) + tuple(LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS) + tuple(
    G6_SM_PROVENANCE_RAW_PINS
) + tuple(
    G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS
) + tuple(
    EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS
) + tuple(
    EFT_G6_FORMAL_GATE_RAW_PINS
) + tuple(
    AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS
) + tuple(
    PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS
) + tuple(
    EFT_G7_FORMAL_RESTRICTION_RAW_PINS
) + tuple(
    PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS
) + tuple(
    NORMALIZED_YUKAWA_CGCS_RAW_PINS
) + tuple(
    PHYSICAL_SM_VACUUM_RAW_PINS
) + tuple(
    PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS
) + tuple(
    CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS
) + tuple(
    PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS
) + tuple(
    PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS
) + tuple(
    PHYSICAL_SM_VECTOR_RXI_RAW_PINS
) + tuple(
    PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_G8_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS
) + tuple(
    PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS
) + tuple(
    PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS
) + tuple(
    PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS
) + tuple(
    PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS
) + tuple(
    PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS
) + tuple(
    PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS
) + tuple(
    EXACT_X_V3_RAW_PINS
) + tuple(
    LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS
) + tuple(
    RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS
) + tuple(
    RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS
) + GLOBAL_PHI_CLASSIFICATION_PORTABLE_PATHS + tuple(
    NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS
) + tuple(
    PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS
) + tuple(
    EXACT_X_V3_PORTABLE_PINS
) + tuple(
    CANONICAL_G1_G8_V21_PORTABLE_PINS
) + tuple(
    CANONICAL_G1_DIM6_PORTABLE_PINS
) + tuple(
    CANONICAL_G2_DIM6_PORTABLE_PINS
) + tuple(
    CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS
) + (LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW,)


def _raw_payload(path: Path) -> bytes:
    return path.read_bytes()


def _portable_payload(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _producer_core_sha256(report: dict[str, Any], field: str = "core_sha256") -> str:
    payload = {key: value for key, value in report.items() if key != field}
    canonical = (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return _sha256(canonical)


def _canonical_legacy_scalar_definition_sha256(path: Path) -> str | None:
    """Hash the legacy gate-title/DAG projection without a provenance cycle."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        dependencies: dict[str, list[str]] | None = None
        specifications: dict[str, Any] | None = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id == "DEPENDENCIES":
                    dependencies = ast.literal_eval(node.value)
                elif target.id == "specifications":
                    try:
                        specifications = ast.literal_eval(node.value)
                    except (TypeError, ValueError):
                        pass
        gate_ids = [f"G{index}" for index in range(1, 9)]
        if dependencies is None or specifications is None:
            return None
        projection = {
            gate_id: {
                "title": specifications[gate_id][0],
                "dependencies": dependencies[gate_id],
            }
            for gate_id in gate_ids
        }
        payload = (
            json.dumps(
                projection,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n"
        ).encode("utf-8")
        return _sha256(payload)
    except (OSError, SyntaxError, KeyError, TypeError, ValueError):
        return None


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
    if relative in LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS:
        return "byte-pinned legacy formal SU(3) x U(1)_89 scalar factorization; physical labels superseded"
    if relative in G6_SM_PROVENANCE_RAW_PINS:
        return "byte-pinned exact G6 physical-stabilizer mismatch and provenance audit"
    if relative in G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS:
        return "byte-pinned exact transitive representation/provenance dependency"
    if relative in EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS:
        return "byte-pinned dimensionful G6 family and formal U(1)_89 threshold audit"
    if relative in EFT_G6_FORMAL_GATE_RAW_PINS:
        return "byte-pinned fail-closed formal G6 gate"
    if relative in AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS:
        return "byte-pinned exact non-Yukawa gauge-beta subtheorem"
    if relative in PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS:
        return "byte-pinned independent PyR@TE gauge-only replay bundle"
    if relative in EFT_G7_FORMAL_RESTRICTION_RAW_PINS:
        return "byte-pinned formal U(1)_89 abstract-restriction example; no physical G7 no-go claim"
    if relative in PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS:
        return "byte-pinned physical PS/SM branching and parameterized matter-threshold subtheorem; full G7 open"
    if relative in NORMALIZED_YUKAWA_CGCS_RAW_PINS:
        return "byte-pinned exact normalized SO(10) representation Yukawa-CGC subtheorem; flavor/RGE/full G7 open"
    if relative in NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned normalized SO(10) Yukawa-CGC transitive source dependency"
    if relative in PHYSICAL_SM_VACUUM_RAW_PINS:
        return "byte-pinned physical-SM target/stabilizer truth overlay; source algebra/global orbit/physical G3-G7 open"
    if relative in PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS:
        return "byte-pinned physical-SM vacuum transitive reconstructed-Hessian dependency"
    if relative in CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS:
        return "byte-pinned conditional reconstructed physical-SM tree Hessian spectrum; source algebra/pole/release G6 open"
    if relative in PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS:
        return "byte-pinned exact parameterized physical-SM heavy-vector tree masses and threshold logs; loop/full G6-G7 open"
    if relative in PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS:
        return "byte-pinned exact combined heavy-vector/FP-ghost/Goldstone non-SUSY MSbar kernel and finite constant; pole/pre-EW/full G6-G7 open"
    if relative in PHYSICAL_SM_VECTOR_RXI_RAW_PINS:
        return "byte-pinned exact zero-background arbitrary-positive-Rxi vacuum determinant cancellation; general-background/pole/full G6-G7 open"
    if relative in PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS:
        return "byte-pinned exact G6/G7 continuous nonidentifiability frontier and closure path; physical/release G6-G7 open"
    if relative in PHYSICAL_SM_G8_FRONTIER_RAW_PINS:
        return "byte-pinned exact G8 scale/flavor/interference nonidentifiability frontier and PDG-2025 single-channel constraint; physical/release/authoritative G8 open"
    if relative in PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS:
        return "byte-pinned exact physical-SM radial equality frontier; direct source Hessian/full equality/physical G3-G5 open"
    if relative in PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS:
        return "byte-pinned exact five-amplitude stationary equality classification; full 486 orbit and physical G3-G5 open"
    if relative in PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned transitive source for the exact five-amplitude equality theorem"
    if relative in PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS:
        return "byte-pinned exact ten hard-projector source Hessians; full 37-row aggregate and physical G3-G5 open"
    if relative in PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned transitive source for the hard-projector Hessian theorem"
    if relative in PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS:
        return "byte-pinned exact last-six source Hessians; all 37 source Hessians available but aggregate/global physical G3-G5 open"
    if relative in PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned transitive source for the exact last-six Hessian theorem"
    if relative in PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS:
        return "byte-pinned exact source-derived 37-row local Hessian theorem; global equality and physical G3-G5 open"
    if relative in PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned transitive report for the exact 37-row aggregate theorem"
    if relative in PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS:
        return "portable-LF-pinned full-486 local equality-orbit theorem; radius/global equality and physical G3-G5 open"
    if relative in PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS:
        return "portable-LF-pinned transitive source/report for the local equality-orbit theorem"
    if relative in PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS:
        return "byte-pinned exact five-amplitude/physical-EW branch mismatch; not a global hierarchy no-go and physical G4-G8 open"
    if relative in PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS:
        return "byte-pinned transitive semantic-JSON dependency for the G4/G5 branch-mismatch theorem"
    if relative in EXACT_X_V3_RAW_PINS:
        return "byte-pinned exact-X v3 static/input/trusted-tree and genuine Wolfram/SARAH execution contract"
    if relative in EXACT_X_V3_PORTABLE_PINS:
        return "portable-LF-pinned exact-X static filter or genuine v3 execution attestation"
    if relative in LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS:
        return "byte-pinned corrected legacy SO(10)+210 gauge-polynomial diagnostic; full physical/mathematical/release G7 open"
    if relative == LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW:
        return "portable-LF active CI for the fail-closed legacy SO(10)+210 G7 diagnostic"
    if relative in RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS:
        return "byte-pinned complete renormalizable mathematical G1 component-tensor bundle"
    if relative in RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS:
        return "byte-pinned complete renormalizable mathematical G2 projected-potential bundle"
    if relative in CANONICAL_G1_G8_V21_PORTABLE_PINS:
        return "portable-LF-pinned canonical closure-capable G1--G8 v21 contract; canonical G1/G2 closed and G3--G8 open"
    if relative in CANONICAL_G1_DIM6_PORTABLE_PINS:
        return "portable-LF-pinned exact dimension-six canonical G1 character/channel/completeness proof and trusted verifier"
    if relative in CANONICAL_G2_DIM6_PORTABLE_PINS:
        return "portable-LF-pinned exact canonical G2 contraction/projection proof and trusted verifier"
    if relative in CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS:
        return "portable-LF-pinned exact canonical G3 physical-EW global-vacuum proof and trusted verifier"
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
    for relative, expected in LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw legacy EFT G6 formal-spectrum member drifted: {relative}"
            )
    for relative, expected in G6_SM_PROVENANCE_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw G6 SM-provenance audit member drifted: {relative}"
            )
    for relative, expected in G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw G6 SM-provenance transitive dependency drifted: {relative}"
            )
    for relative, expected in EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw G6/G7 parameterized-matching member drifted: {relative}"
            )
    for relative, expected in EFT_G6_FORMAL_GATE_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(f"raw formal G6 gate member drifted: {relative}")
    for relative, expected in AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw authoritative gauge-beta member drifted: {relative}"
            )
    for relative, expected in PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw PyR@TE gauge-beta replay member drifted: {relative}"
            )
    for relative, expected in EFT_G7_FORMAL_RESTRICTION_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw formal EFT G7 restriction member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical G7 component-threshold member drifted: {relative}"
            )
    for relative, expected in NORMALIZED_YUKAWA_CGCS_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw normalized Yukawa-CGC member drifted: {relative}"
            )
    for relative, expected in NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS.items():
        observed = _sha256(_portable_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                "portable normalized Yukawa-CGC transitive dependency drifted: "
                f"{relative}"
            )
    for relative, expected in PHYSICAL_SM_VACUUM_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM vacuum member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM vacuum transitive dependency drifted: {relative}"
            )
    for relative, expected in (
        CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS.items()
    ):
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                "raw conditional physical-SM Hessian-spectrum member drifted: "
                f"{relative}"
            )
    for relative, expected in PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM heavy-vector member drifted: {relative}"
            )
    for (
        relative,
        expected,
    ) in PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                "raw physical-SM heavy-vector MSbar matching member drifted: "
                f"{relative}"
            )
    for relative, expected in PHYSICAL_SM_VECTOR_RXI_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM vector Rxi member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM G6/G7 frontier member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_G8_FRONTIER_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM G8 frontier member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw physical-SM source/equality frontier member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw five-amplitude equality member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable five-amplitude transitive dependency drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw hard-projector Hessian bundle member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable hard-projector dependency drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw last-six Hessian bundle member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable last-six Hessian dependency drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw 37-row aggregate bundle member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable 37-row aggregate dependency drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable local equality-orbit bundle member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable local equality-orbit dependency drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw G4/G5 branch-mismatch bundle member drifted: {relative}"
            )
    for relative, expected in PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw G4/G5 branch-mismatch dependency drifted: {relative}"
            )
    for relative, expected in EXACT_X_V3_RAW_PINS.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(f"raw exact-X v3 bundle member drifted: {relative}")
    for relative, expected in EXACT_X_V3_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable exact-X v3 bundle member drifted: {relative}"
            )
    for relative, expected in CANONICAL_G1_G8_V21_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable canonical G1--G8 v21 bundle member drifted: {relative}"
            )
    for relative, expected in CANONICAL_G1_DIM6_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable canonical G1 dimension-six proof member drifted: {relative}"
            )
    for relative, expected in CANONICAL_G2_DIM6_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable canonical G2 dimension-six proof member drifted: {relative}"
            )
    for relative, expected in CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"portable canonical G3 global-vacuum proof member drifted: {relative}"
            )
    for relative, expected in LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw legacy SO(10)+210 beta diagnostic drifted: {relative}"
            )
    legacy_source_pins = {
        "sarah_pyrate_so10_210_betas_v20.py": (
            LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256
        ),
        "test_sarah_pyrate_so10_210_betas_v20.py": (
            LEGACY_SO10_210_BETA_DIAGNOSTIC_TEST_RAW_SHA256
        ),
    }
    for relative, expected in legacy_source_pins.items():
        if _sha256(_raw_payload(ROOT / relative)) != expected:
            raise ArithmeticError(
                f"raw legacy SO(10)+210 beta diagnostic source drifted: {relative}"
            )
    for relative, expected in RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw renormalizable G1 component-tensor bundle member drifted: {relative}"
            )
    for relative, expected in RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS.items():
        observed = _sha256(_raw_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"raw renormalizable G2 mathematical bundle member drifted: {relative}"
            )


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


def _require_eft_g6_truth_bundle() -> dict[str, Any]:
    component_counts = {
        "legacy_formal_spectrum": len(LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS),
        "physical_provenance_correction": len(G6_SM_PROVENANCE_RAW_PINS),
        "parameterized_matching": len(EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS),
        "formal_fail_closed_gate": len(EFT_G6_FORMAL_GATE_RAW_PINS),
    }
    if component_counts != {
        "legacy_formal_spectrum": 4,
        "physical_provenance_correction": 4,
        "parameterized_matching": 4,
        "formal_fail_closed_gate": 4,
    }:
        raise ArithmeticError("the corrected EFT G6 truth bundle must contain 16 files")
    spectrum_source = "exact_eft_physical_scalar_spectrum_v20.py"
    provenance_source = "exact_g6_sm_provenance_feasibility_v20.py"
    matching_source = "exact_eft_g6_g7_parameterized_matching_v20.py"
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
    provenance_correction = json.loads(
        (ROOT / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    matching = json.loads(
        (ROOT / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json").read_text(
            encoding="utf-8"
        )
    )
    spectrum_classification = spectrum.get("classification", {})
    factorization = spectrum.get("exact_factorization", {})
    legacy_provenance = spectrum.get("stabilizer_provenance", {})
    sectors = legacy_provenance.get("sector_reports", {})
    mixing = spectrum.get("mixing_classification", {})
    quotient = spectrum.get("physical_quotient", {})
    uncertainty = spectrum.get("uncertainty_scope", {})
    scope = spectrum.get("scope", {})
    gate_classification = gate.get("classification", {})
    gate_release_criteria = gate.get("release_criteria", {})
    gate_summary = gate.get("spectrum_summary", {})
    correction_classification = provenance_correction.get("classification", {})
    selected_background = provenance_correction.get("selected_background_audit", {})
    commutant = provenance_correction.get("mass_pencil_commutant", {})
    live_swap = provenance_correction.get(
        "independent_live_true_SM_singlet_swap_diagnostic", {}
    )
    correction_source_binding = provenance_correction.get("source_binding", {})
    matching_classification = matching.get("classification", {})
    stabilizer_audit = matching.get("physical_stabilizer_audit", {})
    formal_thresholds = matching.get("exact_residual_scalar_thresholds", {})
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
            == LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256
        ),
        "spectrum_report_core_exact": (
            spectrum.get("core_sha256")
            == LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256
        ),
        "gate_source_core_exact": (
            _source_string_constant(gate_source, "EXPECTED_CORE_SHA256")
            == EFT_G6_FORMAL_GATE_CORE_SHA256
        ),
        "gate_report_core_exact": (
            gate.get("core_sha256") == EFT_G6_FORMAL_GATE_CORE_SHA256
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
        "legacy_embedded_U1em_label_recorded_only_for_explicit_override": (
            legacy_provenance.get("unbroken_group") == "SU(3)_C x U(1)_em"
            and legacy_provenance.get("casimir12_eigenvalues")
            == [0, 16, 36, 40]
            and legacy_provenance.get("charge_squared_eigenvalues") == [0, 1]
            and legacy_provenance.get(
                "operators_commute_exactly_with_Hessian_and_kinetic_metric"
            )
            is True
            and observed_sector_dimensions == expected_sector_dimensions
            and correction_classification.get(
                "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89"
            )
            is True
            and correction_classification.get(
                "frozen_G6_physical_U1em_provenance_complete"
            )
            is False
            and matching_classification.get("frozen_U1em_identification_correct")
            is False
        ),
        "exact_algebraic_mixing_complete": (
            mixing.get("complete") is True
            and mixing.get(
                "projector_traces_reproduce_every_sector_factor_exponent"
            )
            is True
            and len(mixing.get("component_signatures", ())) == 39
        ),
        "legacy_formal_kernel_and_PQ_zero_mode_census_exact": (
            quotient.get("ambient_real_dimension") == 486
            and quotient.get("Hessian_kernel_dimension") == 38
            and quotient.get("gauged_tangent_dimension") == 37
            and quotient.get("physical_PQ_axion_count") == 1
            and quotient.get("gauge_quotient_dimension") == 449
            and quotient.get("massive_positive_dimension") == 448
            and quotient.get("all_38_zero_modes_are_unphysical") is False
        ),
        "legacy_positive_physical_G6_claim_explicitly_overridden": (
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
            and correction_classification.get(
                "prior_positive_physical_G6_interpretation_valid"
            )
            is False
            and correction_classification.get("mathematical_physical_G6_closed")
            is False
            and correction_classification.get("release_level_G6_complete")
            is False
            and matching_classification.get("physical_SM_scalar_thresholds_identified")
            is False
            and gate_classification.get("mathematical_physical_G6_closed") is False
            and gate_classification.get("mathematical_G6_closed_for_EFT_model")
            is False
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
        "physical_provenance_source_report_and_internal_checks_exact": (
            _source_string_constant(provenance_source, "EXPECTED_CORE_SHA256")
            == G6_SM_PROVENANCE_CORE_SHA256
            and provenance_correction.get("core_sha256")
            == G6_SM_PROVENANCE_CORE_SHA256
            and provenance_correction.get("status")
            == "EXACT_G6_SM_PROVENANCE_MISMATCH_PROVED__G6_RELEASE_OPEN"
            and provenance_correction.get("n_failed") == 0
            and provenance_correction.get("failures") == []
            and bool(provenance_correction.get("checks"))
            and all(
                value is True
                for value in provenance_correction["checks"].values()
            )
        ),
        "physical_provenance_transitive_dependencies_exact": (
            correction_source_binding.get(
                "standard_PS_SM_embedding_source"
            )
            == {
                "path": "exact_126bar_triplet_clebsch_v20.py",
                "sha256": G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS[
                    "exact_126bar_triplet_clebsch_v20.py"
                ],
            }
            and correction_source_binding.get("Pati_Salam_210_source")
            == {
                "path": "exact_210_pati_salam_global_vacuum_v20.py",
                "sha256": G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS[
                    "exact_210_pati_salam_global_vacuum_v20.py"
                ],
            }
            and correction_source_binding.get("canonical_486_chart")
            == {
                "path": "live_g2_canonical_486_field_chart_v20.py",
                "sha256": G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS[
                    "live_g2_canonical_486_field_chart_v20.py"
                ],
            }
        ),
        "actual_G89_and_standard_Q_mismatch_exact": (
            selected_background.get("selected_full_target_tangents")
            == {
                "actual_G89_nnz": 0,
                "standard_Q3_nnz": 10,
                "standard_Q3_norm_squared": 90,
            }
            and commutant.get("actual_G89")
            == {"l1_abs": 0, "max_abs": 0, "nnz": 0}
            and commutant.get("actual_G89_squared")
            == {"l1_abs": 0, "max_abs": 0, "nnz": 0}
            and commutant.get("standard_Q3", {}).get("nnz") == 3576
            and commutant.get("standard_Q3", {}).get("max_abs") == 151_200_000
            and selected_background.get(
                "true_SM_neutral_126bar_singlet", {}
            ).get("Q3_annihilation_nnz")
            == 0
        ),
        "independent_true_SM_singlet_swap_fails_stationarity_and_stability": (
            live_swap.get("evidence_kind")
            == "independent_live_486_field_compiler_float64"
            and live_swap.get("gradient_entries_above_1e_minus_9") == 26
            and live_swap.get("gradient_max_abs", 0) > 0
            and live_swap.get("minimum_full_Hessian_eigenvalue", 0) < 0
            and live_swap.get("naive_swap_is_stationary") is False
            and live_swap.get("naive_swap_is_locally_stable") is False
            and live_swap.get("proof_grade") is False
        ),
        "parameterized_matching_source_and_report_core_exact": (
            _source_string_constant(matching_source, "EXPECTED_CORE_SHA256")
            == EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
            and matching.get("core_sha256")
            == EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
            and matching.get("status")
            == "EXACT_G6_SCALING_AND_FORMAL_G89_THRESHOLD__PHYSICAL_STABILIZER_MISMATCH__G7_OPEN"
        ),
        "standard_electromagnetic_vacuum_noninvariance_exact": (
            stabilizer_audit.get("actual_source_generator") == "G_(8,9)"
            and stabilizer_audit.get("G89_equals_standard_electromagnetism")
            is False
            and stabilizer_audit.get("three_Q_standard")
            == "3 Q_std=3 G67-(G01+G23+G45)"
            and stabilizer_audit.get(
                "three_Q_standard_exact_vacuum_action", {}
            ).get("H")
            == {"integer_squared_norm": 18, "nonzero_integer_coordinates": 2}
            and stabilizer_audit.get(
                "three_Q_standard_exact_vacuum_action", {}
            ).get("Delta_R")
            == {"integer_squared_norm": 72, "nonzero_integer_coordinates": 8}
            and stabilizer_audit.get("selected_full_target_tangent")
            == {"integer_squared_norm": 90, "nonzero_integer_coordinates": 10}
            and stabilizer_audit.get(
                "selected_vacuum_preserves_standard_electromagnetism"
            )
            is False
            and stabilizer_audit.get("physical_U1em_sector_labels_valid")
            is False
        ),
        "formal_U1_89_threshold_scope_and_G7_boundary_exact": (
            formal_thresholds.get("scope")
            == "448 massive tree-level scalar real modes, formal residual SU(3) x U(1)_89 only"
            and formal_thresholds.get("interpretation_guard", {}).get(
                "abelian_generator"
            )
            == "G_(8,9)"
            and formal_thresholds.get("interpretation_guard", {}).get(
                "physical_electromagnetic_interpretation_allowed"
            )
            is False
            and matching_classification.get(
                "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete"
            )
            is True
            and matching_classification.get("SM_or_PS_component_threshold_matching_complete")
            is False
            and matching_classification.get("standard_electromagnetic_vacuum_preserved")
            is False
            and matching_classification.get("positive_G7_closed") is False
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
                "G6_G7_parameterized_matching": (
                    EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
                ),
                "G6_physical_provenance": G6_SM_PROVENANCE_CORE_SHA256,
                "spectrum": LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256,
            }
        ),
        "gate_summary_exact": (
            gate_summary.get("ambient_real_fields") == 486
            and gate_summary.get("gauge_quotient_dimension") == 449
            and gate_summary.get("ungauged_PQ_zero_modes") == 1
            and gate_summary.get("positive_massive_modes") == 448
            and gate_summary.get("primitive_factors") == 45
            and gate_summary.get("distinct_mass_squared_roots_including_zero")
            == 61
            and gate_summary.get("residual_group") == "SU(3)_C x U(1)_89"
            and gate_summary.get("upstream_mislabelled_residual_group")
            == "SU(3)_C x U(1)_em"
            and gate_summary.get("physical_U1em_interpretation_valid") is False
            and gate_summary.get("mixing_subspaces_complete") is True
        ),
        "gate_claim_boundary_exact": (
            gate_classification.get(
                "formal_SU3_x_U1_89_tree_mass_factorization_closed"
            )
            is True
            and gate_classification.get("mathematical_physical_G6_closed")
            is False
            and gate_classification.get("mathematical_G6_closed_for_EFT_model")
            is False
            and gate_classification.get(
                "prior_positive_physical_G6_interpretation_valid"
            )
            is False
            and gate_classification.get("release_G6_verified_for_EFT_model")
            is False
            and gate_classification.get("authoritative_renormalizable_G6_closed")
            is False
            and gate_classification.get("authoritative_G6_gate_mutated") is False
            and gate_classification.get("whole_model_validated") is False
        ),
        "gate_completed_integration_and_blockers_exact": (
            gate_release_criteria.get(
                "formal_SU3_x_U1_89_tree_mass_factorization_complete"
            )
            is True
            and gate_release_criteria.get("mathematical_physical_SM_G6_complete")
            is False
            and gate_release_criteria.get("SM_preserving_staged_vacuum_verified")
            is False
            and gate_release_criteria.get(
                "per_state_SM_and_Pati_Salam_provenance_complete"
            )
            is False
            and gate_release_criteria.get(
                "parallel_EFT_G6_integrated_into_release_orchestrators"
            )
            is True
            and set(gate.get("release_blockers", ()))
            == {
                "mathematical_physical_SM_G6_complete",
                "SM_preserving_staged_vacuum_verified",
                "per_state_SM_and_Pati_Salam_provenance_complete",
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
        raise ArithmeticError(f"the corrected EFT G6 truth bundle drifted: {failed}")
    return {
        "raw_file_count": sum(component_counts.values()),
        "component_raw_file_counts": component_counts,
        "legacy_spectrum_physical_interpretation_accepted": False,
        "formal_SU3_x_U1_89_tree_mass_factorization_closed": True,
        "mathematical_physical_G6_closed": False,
        "release_G6_verified": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_eft_g7_truth_bundle() -> dict[str, Any]:
    component_counts = {
        "authoritative_gauge_beta_subtheorem": len(
            AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS
        ),
        "independent_PyRATE3_gauge_only_replay": len(
            PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS
        ),
        "formal_U1_89_abstract_restriction": len(
            EFT_G7_FORMAL_RESTRICTION_RAW_PINS
        ),
        "physical_PS_SM_component_threshold_contract": len(
            PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS
        ),
    }
    if component_counts != {
        "authoritative_gauge_beta_subtheorem": 4,
        "independent_PyRATE3_gauge_only_replay": 6,
        "formal_U1_89_abstract_restriction": 4,
        "physical_PS_SM_component_threshold_contract": 4,
    }:
        raise ArithmeticError("the corrected EFT G7 truth bundle must contain 18 files")
    source_name = "exact_eft_g7_threshold_nonidentifiability_v20.py"
    report = json.loads(
        (
            ROOT / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
        ).read_text(encoding="utf-8")
    )
    gauge_source = "exact_authoritative_so10_u1x_gauge_betas_v20.py"
    replay_source = "pyrate3_so10_u1x_gauge_beta_replay_v20.py"
    gauge = json.loads(
        (ROOT / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json").read_text(
            encoding="utf-8"
        )
    )
    replay = json.loads(
        (ROOT / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    physical_source = "exact_physical_g7_component_threshold_contract_v20.py"
    physical = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
        ).read_text(encoding="utf-8")
    )
    formal_restriction = report.get(
        "formal_U1_89_abstract_restriction_example", {}
    )
    scale = report.get("absolute_scale_counterexample", {})
    classification = report.get("classification", {})
    integration = report.get("integration", {})
    reduced = report.get("reduced_RGE_model_scope", {})
    gauge_classification = gauge.get("classification", {})
    replay_classification = replay.get("classification", {})
    physical_completion = physical.get("completion_matrix", {})
    checks = {
        "source_and_report_core_exact": (
            _source_string_constant(source_name, "EXPECTED_CORE_SHA256")
            == EFT_G7_FORMAL_RESTRICTION_CORE_SHA256
            and report.get("core_sha256")
            == EFT_G7_FORMAL_RESTRICTION_CORE_SHA256
        ),
        "status_and_checks_exact": (
            report.get("status")
            == "FORMAL_U1_89_ABSTRACT_RESTRICTION_NONINJECTIVE__NO_PHYSICAL_G7_CLAIM"
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and bool(report.get("checks"))
            and all(value is True for value in report["checks"].values())
        ),
        "formal_U1_89_abstract_restriction_noninjectivity_exact": (
            formal_restriction.get("scope")
            == (
                "abstract lifts of formal q89=0,1 labels only; the names in the "
                "historical completion rows are not assigned to physical states"
            )
            and formal_restriction.get("same_frozen_G6_masses") is True
            and formal_restriction.get("restriction_map_noninjective") is True
            and formal_restriction.get("one_loop_coefficients_differ") is True
            and formal_restriction.get("physical_electroweak_interpretation_valid")
            is False
            and formal_restriction.get("physical_QED_interpretation_valid") is False
            and formal_restriction.get("completion_A", {}).get(
                "complex_scalar_one_loop_delta_b2"
            )
            == "0"
            and formal_restriction.get("completion_A", {}).get(
                "complex_scalar_one_loop_delta_bY"
            )
            == "1/3"
            and formal_restriction.get("completion_B", {}).get(
                "complex_scalar_one_loop_delta_b2"
            )
            == "1/6"
            and formal_restriction.get("completion_B", {}).get(
                "complex_scalar_one_loop_delta_bY"
            )
            == "1/6"
        ),
        "absolute_scale_collision_exact": (
            scale.get("same_normalized_G6_spectrum") is True
            and scale.get("threshold_log_shift") == "ln(2)"
            and scale.get("absolute_scale_unidentified") is True
        ),
        "reduced_RGE_scope_incomplete_exact": (
            reduced.get("full_210_quartic_basis_present") is False
            and reduced.get("lambda4_CGC_present") is False
            and reduced.get("dimension6_O6_lock_present") is False
            and reduced.get("two_loop_SO10_complete") is False
            and reduced.get("piecewise_component_threshold_matching_complete")
            is False
        ),
        "claim_boundary_remains_fail_closed": (
            classification.get(
                "formal_U1_89_abstract_restriction_noninjectivity_proved"
            )
            is True
            and classification.get(
                "exact_physical_EFT_G7_input_nonidentifiability_proved"
            )
            is False
            and classification.get(
                "historical_electroweak_lift_interpretation_valid"
            )
            is False
            and classification.get("mathematical_EFT_G7_closed") is False
            and classification.get("EFT_release_G7_verified") is False
            and classification.get("authoritative_renormalizable_G7_closed")
            is False
            and classification.get("positive_G7_certified") is False
            and classification.get("negative_G7_no_go_certified") is False
        ),
        "authoritative_gauge_beta_source_report_and_checks_exact": (
            _source_string_constant(gauge_source, "EXPECTED_CORE_SHA256")
            == AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_CORE_SHA256
            and gauge.get("core_sha256")
            == AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_CORE_SHA256
            and gauge.get("status")
            == "EXACT_NONYUKAWA_GAUGE_POLYNOMIAL_CLOSED__FULL_G7_OPEN"
            and gauge.get("n_failed") == 0
            and gauge.get("failures") == []
            and bool(gauge.get("checks"))
            and all(value is True for value in gauge["checks"].values())
        ),
        "authoritative_gauge_only_coefficients_exact": (
            gauge.get("regimes", {}).get("all_active_above_vPhi", {}).get(
                "a_one_loop"
            )
            == {"SO10": "52/3", "X": "10843"}
            and gauge.get("regimes", {}).get("all_active_above_vPhi", {}).get(
                "b_two_loop_nonyukawa"
            )
            == {
                "SO10": {"SO10": "25013/6", "X": "4536"},
                "X": {"SO10": "204120", "X": "7242180"},
            }
            and gauge_classification.get(
                "exact_nonyukawa_two_loop_gauge_polynomial_closed"
            )
            is True
            and gauge_classification.get("full_two_loop_gauge_beta_closed")
            is False
            and gauge_classification.get(
                "full_two_loop_Yukawa_scalar_dimensionful_EFT_system_closed"
            )
            is False
            and gauge_classification.get("physical_G6_input_accepted_for_G7")
            is False
            and gauge_classification.get("mathematical_G7_closed") is False
            and gauge_classification.get("release_G7_verified") is False
        ),
        "independent_PyRATE3_replay_source_report_and_inputs_exact": (
            _source_string_constant(replay_source, "EXPECTED_CORE_SHA256")
            == PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_CORE_SHA256
            and replay.get("core_sha256")
            == PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_CORE_SHA256
            and replay.get("status")
            == "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN"
            and replay.get("n_failed") == 0
            and replay.get("failures") == []
            and bool(replay.get("checks"))
            and all(value is True for value in replay["checks"].values())
            and replay.get("source_binding", {}).get("canonical_model", {}).get(
                "raw_sha256"
            )
            == PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS[
                "models/SO10U1XGaugeAuditV20.model"
            ]
            and replay.get("source_binding", {}).get(
                "frozen_replay_data", {}
            ).get("raw_sha256")
            == PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS[
                "data/PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json"
            ]
        ),
        "independent_PyRATE3_exact_match_scoped_fail_closed": (
            replay.get("executed_input_provenance", {}).get(
                "byte_identical_rename"
            )
            is True
            and replay.get("comparison", {}).get("all_coefficients_match")
            is True
            and replay.get("comparison", {}).get("tolerance") == "0"
            and replay.get("exact_coefficients")
            == {
                "beta_g10_loop1": {"g10^3": "52/3"},
                "beta_g10_loop2": {
                    "g10^3*gX^2": "4536",
                    "g10^5": "25013/6",
                },
                "beta_gX_loop1": {"gX^3": "10843"},
                "beta_gX_loop2": {
                    "g10^2*gX^3": "204120",
                    "gX^5": "7242180",
                },
            }
            and replay_classification.get(
                "independent_gauge_polynomial_replay_closed"
            )
            is True
            and replay_classification.get("full_two_loop_gauge_beta_closed")
            is False
            and replay_classification.get(
                "full_Yukawa_scalar_dimensionful_EFT_system_closed"
            )
            is False
            and replay_classification.get("physical_G6_threshold_matching_closed")
            is False
            and replay_classification.get("mathematical_G7_closed") is False
            and replay_classification.get("release_G7_verified") is False
        ),
        "physical_component_threshold_source_report_and_checks_exact": (
            _source_string_constant(physical_source, "EXPECTED_CORE_SHA256")
            == PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256
            and physical.get("core_sha256")
            == PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256
            and physical.get("status")
            == "EXACT_PHYSICAL_MATTER_BRANCHING_AND_PARAMETERIZED_ONE_LOOP_THRESHOLDS_CLOSED__FULL_G7_OPEN"
            and physical.get("contract_id")
            == "physical_g7_component_threshold_contract_v20"
            and physical.get("n_checks") == 31
            and physical.get("n_failed") == 0
            and physical.get("failures") == []
            and len(physical.get("checks", {})) == 31
            and all(value is True for value in physical["checks"].values())
        ),
        "physical_component_threshold_scoped_truth_exact": (
            all(
                physical_completion.get(name) is True
                for name in (
                    "authoritative_19_Weyl_and_5_scalar_inventory",
                    "continuous_gauge_anomaly_cancellation",
                    "exact_one_loop_full_inventory_gauge_coefficients",
                    "exact_two_loop_nonyukawa_full_inventory_gauge_coefficients",
                    "independent_official_PyRATE3_gauge_replay",
                    "complete_physical_PS_and_SM_matter_branching",
                    "parameterized_one_loop_matter_component_threshold_kernel",
                )
            )
            and all(
                physical_completion.get(name) is False
                for name in (
                    "physical_component_pole_mass_matrices",
                    "heavy_vector_Goldstone_ghost_thresholds",
                    "finite_one_loop_matching_constants",
                    "normalized_Yukawa_tensor_embeddings",
                    "full_two_loop_Yukawa_betas",
                    "full_51_real_parameter_scalar_tensor_translation",
                    "full_two_loop_scalar_quartic_betas",
                    "dimensionful_mass_and_trilinear_betas",
                    "dimension_six_EFT_anomalous_dimension_and_mixing",
                    "physical_G6_input_available",
                    "second_independent_full_RGE_and_matching_implementation",
                    "mathematical_G7_closed",
                    "release_G7_verified",
                )
            )
            and physical.get("adversarial_guards", {}).get(
                "G89_never_used_as_hypercharge"
            )
            is True
            and physical.get("UV_two_loop_gauge_flow", {}).get("Y4_status")
            == "symbolic only; normalized full Yukawa tensors are required"
            and physical.get("heavy_vector_provenance_not_yet_matched", {}).get(
                "one_loop_vector_Goldstone_ghost_matching_implemented"
            )
            is False
            and len(physical.get("release_blockers", [])) == 7
        ),
        "central_integration_complete_exact": (
            set(integration)
            == {
                "ledger_consumes_obstruction",
                "roadmap_consumes_obstruction",
                "validation_matrix_consumes_obstruction",
                "release_orchestrators_and_workflows_consume_obstruction",
            }
            and all(value is True for value in integration.values())
            and "FORMAL_U1_89_RESTRICTION_DOWNSTREAM_INTEGRATION_REQUIRED"
            not in report.get("release_blockers", ())
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the corrected EFT G7 truth bundle drifted: {failed}"
        )
    return {
        "raw_file_count": sum(component_counts.values()),
        "component_raw_file_counts": component_counts,
        "formal_U1_89_abstract_restriction_noninjectivity_proved": True,
        "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
        "physical_PS_SM_matter_branching_closed": True,
        "parameterized_one_loop_matter_threshold_kernel_closed": True,
        "exact_two_loop_nonyukawa_gauge_flow_closed": True,
        "physical_component_pole_mass_matrices_closed": False,
        "heavy_vector_matching_closed": False,
        "physical_G7_closed": False,
        "full_mathematical_G7_closed": False,
        "release_G7_verified": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_normalized_yukawa_cgc_truth_bundle() -> dict[str, Any]:
    if len(NORMALIZED_YUKAWA_CGCS_RAW_PINS) != 4:
        raise ArithmeticError(
            "the normalized SO(10) Yukawa-CGC raw bundle must contain 4 files"
        )
    report = json.loads(
        (ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json").read_text(
            encoding="utf-8"
        )
    )
    scope = report.get("scope", {})
    declared = report.get("declared_yukawa_closure", [])
    checks_report = report.get("checks", {})
    expected_false_checks = {
        "flavor_boundary_values_closed",
        "sarah_symbol_normalization_closed",
        "full_yukawa_rge_closed",
        "full_physical_G7_closed",
    }
    checks = {
        "status_core_and_contract_exact": (
            report.get("core_sha256") == NORMALIZED_YUKAWA_CGCS_CORE_SHA256
            and report.get("contract_id")
            == "exact_normalized_so10_yukawa_cgcs_v20"
            and report.get("status")
            == "EXACT_NORMALIZED_SO10_REPRESENTATION_YUKAWA_CGCS_CLOSED__FLAVOR_RGE_AND_FULL_G7_OPEN"
        ),
        "dependency_and_tensor_inventory_exact": (
            len(report.get("dependencies", {})) == 4
            and all(
                binding.get("mode") in {"raw", "portable_text"}
                and re.fullmatch(r"[0-9a-f]{64}", binding.get("sha256", ""))
                for binding in report.get("dependencies", {}).values()
            )
            and report.get("weyl_multiplet_count") == 19
            and report.get("weyl_component_count") == 304
            and set(report.get("normalized_tensors", {}))
            == {"10", "126bar", "singlet_dual_basis"}
        ),
        "all_ten_declared_representation_cgcs_exact": (
            len(declared) == 10
            and {row.get("symbol") for row in declared}
            == {
                "Y10", "Y126", "yP", "yQ", "yR", "ys",
                "lambdaP", "lambdaR", "lambdaQB", "lambdaQR",
            }
            and all(row.get("representation_CGC_closed") is True for row in declared)
            and all(
                row.get("flavor_tensor_preserved_symbolically") is True
                for row in declared
            )
        ),
        "producer_checks_preserve_scoped_false_flags": (
            len(checks_report) == 28
            and all(
                value is (name not in expected_false_checks)
                for name, value in checks_report.items()
            )
            and expected_false_checks <= set(checks_report)
        ),
        "claim_boundary_exact": (
            scope
            == {
                "normalized_representation_CGCs_for_all_declared_Yukawas": True,
                "canonical_304_Weyl_sparse_embedding": True,
                "flavor_tensor_values_or_textures": False,
                "sarah_implicit_contraction_normalization": False,
                "one_or_two_loop_Yukawa_betas": False,
                "threshold_matching_and_running": False,
                "full_yukawa_sector": False,
                "mathematical_G7": False,
                "release_G7": False,
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the normalized SO(10) Yukawa-CGC truth bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(NORMALIZED_YUKAWA_CGCS_RAW_PINS),
        "normalized_representation_CGCs_closed": True,
        "full_yukawa_sector_closed": False,
        "physical_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_vacuum_truth_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_VACUUM_RAW_PINS) != 4:
        raise ArithmeticError("the physical-SM vacuum raw bundle must contain 4 files")
    report = json.loads(
        (ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    closure = report.get("closure_claims", {})
    supersession = report.get("supersession", {})
    symmetry = report.get("exact_symmetry", {})
    dependencies = report.get("source_binding", {}).get("dependencies", {})
    checks = {
        "schema_status_core_exact": (
            report.get("schema") == "physical_sm_vacuum_local_feasibility_v1"
            and report.get("status")
            == "PHYSICAL_SM_RECONSTRUCTED_GLOBAL_EFT_CERTIFICATE__DIRECT_SOURCE_ALGEBRA_AND_GLOBAL_EQUALITY_ORBIT_OPEN"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
        ),
        "dependencies_and_standard_stabilizer_exact": (
            dependencies.get("validation", {}).get("dependency_file_count") == 20
            and dependencies.get("validation", {}).get(
                "all_dependency_files_present"
            )
            is True
            and symmetry.get("exact_stabilizer_is_su3C_plus_u1em") is True
            and symmetry.get("all_expected_ranks_proved") is True
            and report.get("target", {}).get(
                "standard_Q3_annihilates_full_target"
            )
            is True
        ),
        "old_physical_label_superseded_exact": (
            supersession.get("new_target_exact_stabilizer")
            == "standard SU(3)_C x U(1)_em"
            and supersession.get("old_selected_EFT_target_actual_stabilizer")
            == "SU(3)_C x U(1)_89"
            and supersession.get("old_selected_EFT_target_was_standard_SU3C_x_U1em")
            is False
            and supersession.get(
                "old_abstract_EFT_theorems_do_not_close_physical_SM_G3_G4_G5"
            )
            is True
        ),
        "reconstructed_not_source_proof_exact": (
            report.get("exact_reconstructed_Hessian_rank", {}).get(
                "exact_reconstructed_rank"
            )
            == 448
            and report.get("exact_reconstructed_Hessian_rank", {}).get(
                "exact_reconstructed_nullity"
            )
            == 38
            and report.get("exact_reconstructed_Hessian_rank", {}).get(
                "source_proof_grade"
            )
            is False
            and report.get("squared_stationarity_global_EFT_completion", {}).get(
                "global_zero_locus_classification_open"
            )
            is True
        ),
        "physical_G3_through_G7_fail_closed": (
            closure
            == {
                "physical_SM_G3": False,
                "physical_SM_G4": False,
                "physical_SM_G5": False,
                "physical_SM_G6": False,
                "physical_SM_G7": False,
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the physical-SM vacuum truth bundle drifted: {failed}")
    return {
        "raw_file_count": len(PHYSICAL_SM_VACUUM_RAW_PINS),
        "standard_SU3C_x_U1em_stabilizer_proved": True,
        "old_U1em_label_superseded": True,
        "physical_SM_G3_G4_G5_G6_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_conditional_physical_sm_eft_hessian_spectrum_bundle() -> dict[str, Any]:
    if len(CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS) != 4:
        raise ArithmeticError(
            "the conditional physical-SM EFT Hessian spectrum bundle must contain 4 files"
        )
    report = json.loads(
        (ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json").read_text(
            encoding="utf-8"
        )
    )
    spectrum = report.get("squared_EFT_spectrum", {})
    kernel = report.get("kernel_and_physics_boundary", {})
    proof = report.get("proof_boundary", {})
    checks = {
        "schema_status_core_and_self_pin_exact": (
            report.get("schema") == "conditional_physical_sm_eft_hessian_spectrum_v1"
            and report.get("status")
            == "CONDITIONAL_EXACT_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM__SOURCE_ALGEBRA_POLE_AND_RELEASE_CLOSURE_OPEN"
            and report.get("integrity", {}).get("core_sha256")
            == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256
            and report.get("source_binding", {}).get("self_sha256")
            == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS[
                "conditional_physical_sm_eft_hessian_spectrum_v20.py"
            ]
            and report.get("source_binding", {}).get("foundation", {}).get(
                "all_terminal_foundation_pins_match"
            )
            is True
        ),
        "conditional_tree_spectrum_census_exact": (
            spectrum.get("total_root_count_with_multiplicity") == 486
            and spectrum.get("zero_root_count_with_multiplicity") == 38
            and spectrum.get("positive_root_count_with_multiplicity") == 448
            and kernel.get("exact_reconstructed_H_rank") == 448
            and kernel.get("exact_reconstructed_H_nullity") == 38
            and kernel.get("gauged_orbit_kernel_dimension") == 37
            and kernel.get("global_PQ_axion_kernel_dimension") == 1
        ),
        "conditional_not_physical_or_release_G6_exact": (
            report.get("closure_claims")
            == {
                "conditional_reconstructed_squared_EFT_spectrum": True,
                "conditional_reconstructed_tree_Hessian_factorization": True,
                "conditional_reconstructed_tree_Hessian_sector_assignment": True,
                "pole_spectrum_G6": False,
                "release_G6": False,
                "source_bound_physical_G6": False,
            }
            and proof.get("exact_on_reconstructed_rational_Hessian") is True
            and proof.get("tree_level_only") is True
            and proof.get("upstream_source_algebra_derivation_complete") is False
            and proof.get("pole_and_release_claims") is False
            and kernel.get("rho_is_a_pole_mass_squared") is False
            and kernel.get("physical_G6_closed") is False
            and kernel.get("release_G6_closed") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the conditional physical-SM EFT Hessian spectrum bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS),
        "conditional_reconstructed_tree_spectrum_closed": True,
        "source_bound_physical_G6_closed": False,
        "pole_spectrum_G6_closed": False,
        "release_G6_verified": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_heavy_vector_mass_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS) != 4:
        raise ArithmeticError(
            "the physical-SM heavy-vector mass bundle must contain 4 files"
        )
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json").read_text(
            encoding="utf-8"
        )
    )
    rank = report.get("rank_kernel_Goldstone", {})
    scope = report.get("scope", {})
    producer_checks = report.get("checks", {})
    expected_false_checks = {
        "physical_scale_and_coupling_boundaries_fixed",
        "pole_masses_fixed",
        "vector_Goldstone_ghost_matching_closed",
        "finite_scheme_constants_closed",
        "SM_symmetric_pre_EW_threshold_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    checks = {
        "status_core_contract_and_dependencies_exact": (
            report.get("core_sha256")
            == PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256
            and report.get("contract_id")
            == "exact_physical_sm_heavy_vector_masses_v20"
            and report.get("status")
            == "EXACT_PARAMETERIZED_PHYSICAL_SM_HEAVY_VECTOR_MASS_THEOREM_CLOSED__LOOP_MATCHING_AND_FULL_G6_G7_OPEN"
            and len(report.get("source_binding", {})) == 5
            and report.get("normalization", {}).get("normalization_matches") is True
        ),
        "exact_tree_mass_rank_kernel_and_goldstone_exact": (
            report.get("exact_matrix", {}).get("shape") == [46, 46]
            and rank.get("exact_gram_rank") == 37
            and rank.get("exact_gram_nullity") == 9
            and rank.get("unbroken_algebra") == "su(3)_C + u(1)_em"
            and rank.get("declared_basis_is_complete_kernel") is True
            and rank.get("gauge_Goldstone_image_dimension") == 37
            and rank.get("full_gauge_plus_PQ_tangent_rank") == 38
            and rank.get("uneaten_accidental_PQ_dimension") == 1
        ),
        "parameterized_threshold_interface_exact": (
            report.get("parameterized_threshold_interface", {}).get(
                "unbroken_group_at_full_target"
            )
            == "SU(3)_C x U(1)_em"
            and report.get("parameterized_threshold_interface", {}).get(
                "total_indices"
            )
            == {"SU3": "5/2", "QED": "32/3"}
            and report.get("parameterized_threshold_interface", {}).get(
                "complete_vector_Goldstone_ghost_matching"
            )
            is False
        ),
        "producer_checks_preserve_scoped_false_flags": (
            all(
                value is (name not in expected_false_checks)
                for name, value in producer_checks.items()
            )
            and expected_false_checks <= set(producer_checks)
        ),
        "claim_boundary_exact": (
            scope
            == {
                "exact_parameterized_46x46_tree_mass_matrix": True,
                "exact_rank_kernel_and_Goldstone_image": True,
                "exact_non_neutral_sector_masses_and_multiplicities": True,
                "exact_neutral_characteristic_polynomial": True,
                "unbroken_group_threshold_log_inputs": True,
                "absolute_physical_masses": False,
                "pole_masses": False,
                "complete_one_loop_vector_threshold_matching": False,
                "complete_physical_scalar_spectrum": False,
                "physical_G6": False,
                "physical_G7": False,
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the physical-SM heavy-vector mass bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS),
        "parameterized_tree_vector_masses_closed": True,
        "parameterized_unbroken_group_threshold_logs_closed": True,
        "pole_masses_closed": False,
        "vector_Goldstone_ghost_matching_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_heavy_vector_msbar_matching_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS) != 4:
        raise ArithmeticError(
            "the physical-SM heavy-vector MSbar matching bundle must contain 4 files"
        )
    report = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
        ).read_text(encoding="utf-8")
    )
    expected_top_level = {
        "core_sha256",
        "contract_id",
        "status",
        "source_binding",
        "primary_equation_sources",
        "scheme_contract",
        "exact_group_factors",
        "massive_charged_multiplets",
        "consumer_interface",
        "gauge_parameter_obstruction",
        "checks",
        "scope",
        "blockers",
    }
    expected_sources = {
        "exact_heavy_vector_mass_source": {
            "path": "exact_physical_sm_heavy_vector_masses_v20.py",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS[
                "exact_physical_sm_heavy_vector_masses_v20.py"
            ],
            "mode": "raw",
        },
        "exact_heavy_vector_mass_report": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS[
                "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json"
            ],
            "mode": "raw",
        },
        "authoritative_SO10_normalization": {
            "path": "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "sha256": AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS[
                "exact_authoritative_so10_u1x_gauge_betas_v20.py"
            ],
            "mode": "raw",
        },
        "authoritative_model": {
            "path": "models\\SO10Z17AxionV20.m",
            "sha256": (
                "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1"
            ),
            "mode": "raw",
        },
    }
    expected_scope = {
        "combined_heavy_vector_FPghost_Goldstone_MSbar_matching": True,
        "finite_MSbar_vector_constant": True,
        "exact_SU3_and_physical_QED_group_factors": True,
        "parameterized_tree_masses": True,
        "arbitrary_Rxi_sector_resolved_determinants": False,
        "pole_mass_thresholds": False,
        "SM_symmetric_pre_EW_threshold": False,
        "complete_scalar_and_fermion_thresholds": False,
        "complete_one_loop_model_matching": False,
        "physical_G6": False,
        "physical_G7": False,
    }
    negative_checks = {
        "arbitrary_Rxi_determinant_cancellation_rederived",
        "pole_mass_conversion_closed",
        "SM_symmetric_pre_EW_matching_closed",
        "complete_scalar_fermion_threshold_matching_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    producer_checks = report.get("checks", {})
    scheme = report.get("scheme_contract", {})
    group = report.get("exact_group_factors", {})
    obstruction = report.get("gauge_parameter_obstruction", {})
    consumer = report.get("consumer_interface", {})
    sources = report.get("primary_equation_sources", [])
    checks = {
        "status_core_schema_and_dependencies_exact": (
            set(report) == expected_top_level
            and report.get("core_sha256")
            == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256
            and report.get("contract_id")
            == "exact_physical_sm_heavy_vector_msbar_matching_v20"
            and report.get("status")
            == "EXACT_COMBINED_HEAVY_VECTOR_GHOST_GOLDSTONE_MSBAR_MATCHING_CLOSED__ARBITRARY_RXI_POLE_PRE_EW_AND_FULL_G7_OPEN"
            and report.get("source_binding") == expected_sources
        ),
        "primary_equation_provenance_exact": (
            len(sources) == 3
            and {source.get("doi") for source in sources}
            == {
                "10.1103/PhysRevD.91.075016",
                "10.1103/PhysRevD.108.055003",
                "10.1016/0550-3213(81)90498-3",
            }
            and any(source.get("equations") == ["(B14)", "(B15)"] for source in sources)
        ),
        "combined_MSbar_formula_and_finite_constants_exact": (
            scheme.get("renormalization_scheme") == "non-supersymmetric MS-bar"
            and scheme.get("per_complex_vector")
            == "Delta_i=-T_i/(6*pi)+7*T_i/(2*pi)*log(M_tree/mu)"
            and scheme.get("mass_definition") == "tree_running_mass"
            and scheme.get("gauge_parameter")
            == "not an input; published combined result only; explicit xi is rejected"
            and group.get("complex_index_totals")
            == {"SU3": "5/2", "QED": "32/3"}
            and group.get("real_broken_generator_index_totals")
            == {"SU3": "5", "QED": "64/3"}
            and group.get("combined_threshold_coefficients")
            == {
                "SU3": {"finite_over_pi": "-5/12", "log_over_pi": "35/4"},
                "QED": {"finite_over_pi": "-16/9", "log_over_pi": "112/3"},
            }
        ),
        "multiplicity_goldstone_and_neutral_guards_exact": (
            len(report.get("massive_charged_multiplets", [])) == 7
            and group.get("charged_real_vectors") == 34
            and group.get("neutral_massive_vectors") == 3
            and group.get("all_massive_vectors") == 37
            and group.get("Goldstone_image_dimension") == 37
            and group.get("uneaten_accidental_PQ_dimension") == 1
            and consumer.get("Goldstone_exclusion_guard")
            == "assert_goldstone_exclusion(37)"
        ),
        "producer_checks_preserve_exact_scoped_truth_boundary": (
            len(producer_checks) == 29
            and negative_checks <= set(producer_checks)
            and all(
                value is (name not in negative_checks)
                for name, value in producer_checks.items()
            )
            and report.get("scope") == expected_scope
        ),
        "arbitrary_Rxi_pole_preEW_and_full_G6_G7_fail_closed": (
            obstruction.get("arbitrary_Rxi_sector_resolved_matching_closed")
            is False
            and obstruction.get("combined_MSbar_matching_closed") is True
            and len(
                obstruction.get(
                    "missing_for_independent_xi_cancellation_proof", []
                )
            )
            == 4
            and len(report.get("blockers", [])) == 4
            and report.get("scope", {}).get("pole_mass_thresholds") is False
            and report.get("scope", {}).get("SM_symmetric_pre_EW_threshold")
            is False
            and report.get("scope", {}).get("complete_scalar_and_fermion_thresholds")
            is False
            and report.get("scope", {}).get("physical_G6") is False
            and report.get("scope", {}).get("physical_G7") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            "the physical-SM heavy-vector MSbar matching bundle drifted: "
            f"{failed}"
        )
    return {
        "raw_file_count": len(PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS),
        "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed": True,
        "finite_MSbar_vector_constant_closed": True,
        "exact_SU3_and_physical_QED_group_factors_closed": True,
        "Goldstone_double_count_guard_active": True,
        "independent_background_covariant_general_field_Rxi_replay_closed": False,
        "pole_mass_conversion_closed": False,
        "stationary_SM_symmetric_pre_EW_matching_closed": False,
        "complete_scalar_fermion_thresholds_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_vector_rxi_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_VECTOR_RXI_RAW_PINS) != 4:
        raise ArithmeticError("the physical-SM vector Rxi bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json").read_text(
            encoding="utf-8"
        )
    )
    scope = report.get("scope", {})
    direction = report.get("direction_census", {})
    checks = {
        "canonical_core_exact": (
            report.get("core_sha256") == PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
            and _producer_core_sha256(report) == PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
        ),
        "status_and_exact_vacuum_scope": (
            report.get("contract_id")
            == "exact_physical_sm_vector_rxi_vacuum_cancellation_v20"
            and report.get("status")
            == "EXACT_ALL_37_BROKEN_DIRECTION_RXI_VACUUM_DETERMINANT_CANCELLATION_CLOSED__BACKGROUND_FIELD_POLE_AND_FULL_G6_G7_OPEN"
            and scope.get(
                "arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation"
            )
            is True
            and scope.get("all_37_broken_real_directions_resolved") is True
            and direction.get("total_broken_real_directions") == 37
            and direction.get("gauge_Goldstone_directions") == 37
            and direction.get("complex_FP_ghost_pairs") == 37
        ),
        "general_background_pole_and_G6_G7_fail_closed": (
            scope.get("background_covariant_heat_kernel_matching_coefficient")
            is False
            and scope.get(
                "sector_resolved_general_background_gauge_determinants"
            )
            is False
            and scope.get("one_loop_vector_pole_masses") is False
            and scope.get("complete_scalar_and_fermion_thresholds") is False
            and scope.get("physical_G6") is False
            and scope.get("physical_G7") is False
            and scope.get("release_G6") is False
            and scope.get("release_G7") is False
        ),
        "hundred_exact_cases_closed": (
            report.get("hundred_point_exact_audit", {}).get("case_count") == 100
            and report.get("hundred_point_exact_audit", {}).get("case_range")
            == [0, 99]
            and report.get("hundred_point_exact_audit", {}).get(
                "all_exact_rational_cases_pass"
            )
            is True
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the physical-SM vector Rxi bundle drifted: {failed}")
    return {
        "raw_file_count": len(PHYSICAL_SM_VECTOR_RXI_RAW_PINS),
        "zero_background_Rxi_vacuum_determinant_cancellation_closed": True,
        "all_37_broken_directions_closed": True,
        "background_covariant_general_field_determinants_closed": False,
        "pole_vector_masses_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_g6_g7_frontier_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS) != 4:
        raise ArithmeticError("the physical-SM G6/G7 frontier bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json").read_text(
            encoding="utf-8"
        )
    )
    scope = report.get("scope", {})
    matrix = report.get("completed_and_open_matrix", {})
    checks = {
        "canonical_core_exact": (
            report.get("core_sha256") == PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
            and _producer_core_sha256(report)
            == PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
        ),
        "status_nonidentifiability_and_path_exact": (
            report.get("contract_id")
            == "exact_physical_sm_g6_g7_closure_frontier_v20"
            and report.get("status")
            == "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_AND_NONIDENTIFIABILITY_CLOSED__PHYSICAL_G6_G7_REMAIN_OPEN"
            and scope.get("continuous_nonidentifiability_proved") is True
            and scope.get("minimal_closure_path_machine_readable") is True
            and [row.get("order") for row in report.get("minimal_closure_path", [])]
            == list(range(1, 8))
        ),
        "closed_and_open_matrix_exact": (
            len(matrix.get("closed", {})) == 8
            and len(matrix.get("open", {})) == 11
            and all(value is True for value in matrix.get("closed", {}).values())
            and all(value is True for value in matrix.get("open", {}).values())
        ),
        "unique_outputs_and_G6_G7_fail_closed": (
            scope.get("unique_absolute_tree_spectrum") is False
            and scope.get("unique_pole_spectrum") is False
            and scope.get("unique_threshold_vector") is False
            and scope.get("unique_full_RGE_trajectory") is False
            and scope.get("physical_G6") is False
            and scope.get("physical_G7") is False
            and scope.get("release_G6") is False
            and scope.get("release_G7") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the physical-SM G6/G7 frontier bundle drifted: {failed}")
    return {
        "raw_file_count": len(PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS),
        "continuous_nonidentifiability_proved": True,
        "minimal_closure_path_machine_readable": True,
        "unique_absolute_tree_spectrum": False,
        "unique_pole_spectrum": False,
        "unique_threshold_vector": False,
        "unique_full_RGE_trajectory": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_g8_frontier_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_G8_FRONTIER_RAW_PINS) != 4:
        raise ArithmeticError("the physical-SM G8 frontier bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json").read_text(
            encoding="utf-8"
        )
    )
    expected_top_level = {
        "schema",
        "status",
        "contract_id",
        "core_sha256",
        "source_binding",
        "canonical_G8_definition",
        "exact_nonidentifiability_witnesses",
        "scale_audit_0_through_100",
        "repository_frozen_experimental_input",
        "acceptance_matrix",
        "minimal_exhibited_free_input_vector",
        "exact_missing_inputs",
        "scope",
        "checks",
        "n_checks",
        "n_failed",
        "failures",
        "verdict",
    }
    expected_checks = {
        "above_limit_scale_witness_is_sixteen",
        "all_101_scaling_identities_are_exact",
        "all_dependency_raw_and_core_hashes_match",
        "all_five_G8_acceptance_criteria_fail_closed",
        "authoritative_G8_fail_closed",
        "below_limit_scale_witness_is_one_sixteenth",
        "canonical_G8_definition_is_unique",
        "canonical_G8_has_five_acceptance_criteria",
        "canonical_G8_has_three_dependencies",
        "fifty_complex_flavor_entries_are_unfixed",
        "gauge_lifetime_scales_exactly_as_lambda_four",
        "independent_raw_v_b_flavor_witness_has_102_real_coordinates",
        "one_dimensional_scale_witness_already_breaks_G6_G7_G8_uniqueness",
        "physical_G8_fail_closed",
        "release_G8_fail_closed",
        "same_normalized_spectrum_crosses_finite_limit",
        "scale_audit_covers_cases_zero_through_one_hundred",
        "unfixed_relative_phase_changes_total_width",
        "vector_scale_is_unidentified",
        "vector_threshold_coefficients_are_exact",
    }
    expected_source_binding = {
        "canonical_gauged_u1x_v21_contract_source": {
            "binding_mode": "raw",
            "path": "canonical_g1_g8_gauged_u1x_v21.py",
            "raw_sha256": (
                    "4158df2bbef369d100ed95cf45a6428b3307cdf4da066f4664981b2c4d61dea0"
            ),
        },
        "normalized_SO10_Yukawa_CGCs": {
            "binding_mode": "raw",
            "core_sha256": NORMALIZED_YUKAWA_CGCS_CORE_SHA256,
            "path": "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
            "raw_sha256": (
                "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b"
            ),
        },
        "physical_G7_component_threshold_contract": {
            "binding_mode": "raw",
            "core_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256,
            "path": "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
            "raw_sha256": (
                "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e"
            ),
        },
        "physical_SM_G6_G7_frontier": {
            "binding_mode": "raw",
            "core_sha256": PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256,
            "path": "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json",
            "raw_sha256": (
                "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a"
            ),
        },
        "physical_SM_heavy_vector_MSbar_matching": {
            "binding_mode": "raw",
            "core_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256,
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
            "raw_sha256": (
                "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee"
            ),
        },
        "physical_SM_heavy_vector_masses": {
            "binding_mode": "raw",
            "core_sha256": PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256,
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "raw_sha256": (
                "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0"
            ),
        },
        "repository_frozen_proton_gate_source": {
            "binding_mode": "raw",
            "path": "proton_decay_falsification_gate_v20.py",
            "raw_sha256": (
                "f2d875ba665707a929bf912dfc83af547452d04cb8ebb6932e67dffd076dd921"
            ),
        },
    }
    expected_scope = {
        "authoritative_G8": False,
        "canonical_G8_contract_audited": True,
        "continuous_absolute_scale_nonidentifiability_proved": True,
        "flavor_and_interference_nonidentifiability_audited": True,
        "negative_no_go_for_future_G8_closure": False,
        "physical_G8": False,
        "release_G8": False,
        "repository_frozen_single_channel_constraint_computed": True,
        "unique_proton_lifetime_or_distribution": False,
        "whole_model_excluded_by_conditional_points": False,
    }
    canonical = report.get("canonical_G8_definition", {})
    acceptance = report.get("acceptance_matrix", {})
    witnesses = report.get("exact_nonidentifiability_witnesses", {})
    vector = witnesses.get("absolute_vector_scale", {})
    crossing = witnesses.get("finite_limit_crossing", {})
    flavor = witnesses.get("flavor_and_interference", {})
    audit = report.get("scale_audit_0_through_100", {})
    experimental = report.get("repository_frozen_experimental_input", {})
    pdg = experimental.get("official_current_review_verification", {})
    free_vector = report.get("minimal_exhibited_free_input_vector", {})
    minimum = free_vector.get("smallest_exhibited_joint_witness", {})
    missing = report.get("exact_missing_inputs", {})
    embedded_checks = report.get("checks", {})
    checks = {
        "canonical_core_and_source_binding_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "exact_physical_sm_g8_identifiability_frontier_v1"
            and report.get("contract_id")
            == "exact_physical_sm_g8_identifiability_frontier_v20"
            and report.get("status")
            == "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_CLOSED__PHYSICAL_RELEASE_AUTHORITATIVE_G8_OPEN"
            and report.get("core_sha256") == PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
            and _producer_core_sha256(report) == PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
            and report.get("source_binding") == expected_source_binding
        ),
        "canonical_G8_definition_and_acceptance_exact": (
            canonical.get("gap_id") == CANONICAL_G1_G8_V21_GATE_IDS[7]
            and canonical.get("definition_sha256")
            == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and canonical.get("required_artifact")
            == CANONICAL_G1_G8_V21_REQUIRED_ARTIFACTS[7]
            and canonical.get("dependencies")
            == list(CANONICAL_G1_G8_V21_DEPENDENCIES[7])
            and canonical.get("required_evidence_schema")
            == "canonical_gauged_u1x_gate_evidence_v1"
            and len(canonical.get("acceptance", [])) == 5
            and list(acceptance) == [f"criterion_{index}" for index in range(1, 6)]
            and all(row.get("passed") is False for row in acceptance.values())
        ),
        "embedded_checks_and_truth_boundary_exact": (
            set(embedded_checks) == expected_checks
            and all(embedded_checks.get(name) is True for name in expected_checks)
            and report.get("n_checks") == 20
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and report.get("scope") == expected_scope
        ),
        "scale_and_finite_limit_nonidentifiability_exact": (
            vector.get("mass_ratio") == "2"
            and vector.get("dimension_six_Wilson_ratio_at_fixed_dimensionless_data")
            == "1/4"
            and vector.get("partial_width_ratio_at_fixed_dimensionless_data")
            == "1/16"
            and vector.get("partial_lifetime_ratio_at_fixed_dimensionless_data")
            == "16"
            and vector.get("threshold_log_coefficients")
            == {"QED": "112/3", "SU3": "35/4"}
            and vector.get("absolute_vector_scale_identified") is False
            and crossing.get("same_normalized_vector_spectrum") is True
            and crossing.get("model_classification_identified_without_absolute_scale")
            is False
            and crossing.get("below_limit_completion", {}).get(
                "lifetime_margin_over_limit"
            )
            == "1/16"
            and crossing.get("above_limit_completion", {}).get(
                "lifetime_margin_over_limit"
            )
            == "16"
        ),
        "flavor_and_interference_nonidentifiability_exact": (
            flavor.get("raw_complex_entries_before_flavour_quotients") == 50
            and flavor.get("raw_real_entries_before_flavour_quotients") == 100
            and flavor.get("flavor_tensor_values_or_textures_fixed") is False
            and flavor.get("unique_mass_basis_scalar_Wilson_coefficients") is False
            and flavor.get("vacuum_fixed_gauge_scalar_interference") is False
            and flavor.get("equal_magnitude_interference_witness", {}).get(
                "relative_sign_plus_squared_amplitude"
            )
            == "4"
            and flavor.get("equal_magnitude_interference_witness", {}).get(
                "relative_sign_minus_squared_amplitude"
            )
            == "0"
        ),
        "exact_101_case_scale_audit": (
            audit.get("case_range") == [0, 100]
            and audit.get("case_count") == 101
            and audit.get("identity_case") == 50
            and audit.get("all_scaling_identities_exact") is True
            and audit.get("records_sha256")
            == "7402efea7c377a709a4bb33ec08a0e717418973c38e3e684de54ea92489311cd"
        ),
        "PDG_2025_constraint_exact_but_not_unique_prediction": (
            experimental.get("reported_limit_90CL_years")
            == "2.400000000000e+34"
            and experimental.get("current_PDG_review_numeric_verification_performed")
            is True
            and experimental.get("complete_live_all_channel_limit_verification_performed")
            is False
            and experimental.get("usable_as_conditional_constraint") is True
            and experimental.get("usable_as_unique_G8_prediction") is False
            and pdg.get("publisher") == "Particle Data Group"
            and pdg.get("edition") == 2025
            and pdg.get("pdf_page") == 14
            and pdg.get("reference_number") == 117
            and pdg.get("numeric_value_agrees_with_repository") is True
            and pdg.get("pdf_sha256_retrieved_2026_08_12")
            == "a320b62680575d1a37d29de60fe4f259afef2d24d5ab3550c59294bfd187b693"
        ),
        "minimal_free_vector_and_missing_input_boundary_exact": (
            minimum.get("coordinates") == ["lambda_v"]
            and minimum.get("real_dimension") == 1
            and minimum.get("claim_of_global_parameter_minimality") is False
            and free_vector.get(
                "exhibited_raw_real_dimension_including_v_b_and_all_flavor_entries"
            )
            == 102
            and len(missing.get("continuous_boundary_values_or_distributions", []))
            == 5
            and len(missing.get("derivable_but_not_yet_derived", [])) == 7
            and len(
                missing.get("measured_or_lattice_inputs_to_freeze_with_covariance", [])
            )
            == 3
            and len(missing.get("software_environment_not_laboratory", [])) == 1
            and missing.get("new_laboratory_measurement_required_for_theory_gate")
            == []
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the physical-SM G8 frontier bundle drifted: {failed}")
    return {
        "raw_file_count": len(PHYSICAL_SM_G8_FRONTIER_RAW_PINS),
        "canonical_G8_contract_audited": True,
        "continuous_absolute_scale_nonidentifiability_proved": True,
        "flavor_and_interference_nonidentifiability_audited": True,
        "repository_frozen_PDG_2025_single_channel_constraint_verified": True,
        "exact_101_case_scale_audit_closed": True,
        "minimal_exhibited_joint_free_real_dimension": 1,
        "unique_proton_lifetime_or_distribution": False,
        "physical_G8_closed": False,
        "release_G8_verified": False,
        "authoritative_G8_closed": False,
        "all_acceptance_criteria_pass": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_canonical_g1_g8_v21_bundle() -> dict[str, Any]:
    """Bind the qualified, closure-capable G1--G8 contract without promotion."""
    if len(CANONICAL_G1_G8_V21_PORTABLE_PINS) != 4:
        raise ArithmeticError("the canonical G1--G8 v21 bundle must contain 4 files")
    for relative, expected in CANONICAL_G1_G8_V21_PORTABLE_PINS.items():
        observed = _sha256(_portable_payload(ROOT / relative))
        if observed != expected:
            raise ArithmeticError(
                f"portable canonical G1--G8 v21 bundle member drifted: {relative}"
            )
    report = json.loads(
        (ROOT / "CANONICAL_G1_G8_GAUGED_U1X_V21.json").read_text(
            encoding="utf-8"
        )
    )
    expected_top_level = {
        "schema",
        "status",
        "overall_state",
        "contract_namespace",
        "model_contract_id",
        "definition_sha256",
        "gauge_dimension_derivation",
        "gates",
        "closure_counts",
        "legacy_mapping",
        "legacy_source_bindings",
        "checks",
        "n_checks",
        "n_failed",
        "failures",
        "classification",
        "verdict",
        "integrity",
    }
    expected_check_names = {
        "G6_is_explicitly_nonsupersymmetric",
        "broken_gauge_count_is_derived_as_37",
        "dedicated_artifacts_are_unique",
        "definition_sha256_is_canonical",
        "dependency_DAG_is_topologically_ordered",
        "eight_unique_qualified_gate_ids",
        "legacy_namespace_definitions_are_bound_without_hash_cycles",
        "legacy_namespaces_cannot_satisfy_by_gate_number",
        "no_naked_gate_id_is_canonical",
        "trusted_verifier_slots_are_unique_and_fail_closed",
    }
    expected_gate_keys = {
        "acceptance",
        "closed",
        "definition_sha256",
        "dependencies",
        "dependencies_closed",
        "evidence_state",
        "gate_number",
        "qualified_gate_id",
        "required_artifact",
        "required_evidence_schema",
        "title",
        "trusted_verifier",
    }
    expected_absent_evidence = {
        "exists": False,
        "valid": False,
        "closed": False,
        "reason": "required canonical artifact absent",
        "errors": [],
    }
    gates = report.get("gates", [])

    def gate_row_exact(gate: dict[str, Any], index: int) -> bool:
        expected_verifier_sha = {
            1: CANONICAL_G1_TRUSTED_VERIFIER_SHA256,
            2: CANONICAL_G2_TRUSTED_VERIFIER_SHA256,
            3: CANONICAL_G3_TRUSTED_VERIFIER_SHA256,
        }.get(index)
        common = (
            set(gate) == expected_gate_keys
            and gate.get("gate_number") == index
            and gate.get("qualified_gate_id")
            == CANONICAL_G1_G8_V21_GATE_IDS[index - 1]
            and gate.get("required_artifact")
            == CANONICAL_G1_G8_V21_REQUIRED_ARTIFACTS[index - 1]
            and gate.get("dependencies")
            == list(CANONICAL_G1_G8_V21_DEPENDENCIES[index - 1])
            and gate.get("definition_sha256")
            == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and gate.get("required_evidence_schema")
            == "canonical_gauged_u1x_gate_evidence_v1"
            and gate.get("trusted_verifier")
            == {
                "path": CANONICAL_G1_G8_V21_TRUSTED_VERIFIER_PATHS[index - 1],
                "mode": "raw",
                "protocol": CANONICAL_G1_G8_V21_VERIFIER_PROTOCOL,
                "sha256": expected_verifier_sha,
            }
            and isinstance(gate.get("title"), str)
            and bool(gate.get("title"))
            and isinstance(gate.get("acceptance"), list)
            and len(gate.get("acceptance", [])) == (5 if index == 8 else 4)
            and all(
                isinstance(criterion, str) and bool(criterion)
                for criterion in gate.get("acceptance", [])
            )
        )
        if not common:
            return False
        if index not in (1, 2, 3):
            return (
                gate.get("evidence_state") == expected_absent_evidence
                and gate.get("dependencies_closed") is (index == 4)
                and gate.get("closed") is False
            )
        evidence = gate.get("evidence_state", {})
        verifier = evidence.get("trusted_verifier_result", {})
        expected_core = {
            1: CANONICAL_G1_COMPLETE_RING_CORE_SHA256,
            2: CANONICAL_G2_FULL_PROJECTION_CORE_SHA256,
            3: CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256,
        }[index]
        expected_artifact_hash = {
            1: CANONICAL_G1_DIM6_PORTABLE_PINS[
                "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json"
            ],
            2: CANONICAL_G2_DIM6_PORTABLE_PINS[
                "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json"
            ],
            3: CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS[
                "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json"
            ],
        }[index]
        return (
            evidence.get("exists") is True
            and evidence.get("valid") is True
            and evidence.get("closed") is True
            and evidence.get("reason") == "accepted"
            and evidence.get("errors") == []
            and evidence.get("core_sha256") == expected_core
            and evidence.get("raw_sha256") == expected_artifact_hash
            and verifier.get("schema") == CANONICAL_G1_G8_V21_VERIFIER_PROTOCOL
            and verifier.get("qualified_gate_id")
            == CANONICAL_G1_G8_V21_GATE_IDS[index - 1]
            and verifier.get("definition_sha256")
            == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and verifier.get("artifact_core_sha256")
            == expected_core
            and verifier.get("verifier_sha256")
            == expected_verifier_sha
            and verifier.get("acceptance_results")
            == {"A1": True, "A2": True, "A3": True, "A4": True}
            and verifier.get("all_acceptance_criteria_verified") is True
            and type(verifier.get("n_failed")) is int
            and verifier.get("n_failed") == 0
            and verifier.get("failures") == []
            and gate.get("dependencies_closed") is True
            and gate.get("closed") is True
        )

    gate_rows_exact = (
        isinstance(gates, list)
        and len(gates) == 8
        and all(
            gate_row_exact(gate, index)
            for index, gate in enumerate(gates, start=1)
        )
    )
    report_without_integrity = {
        key: value for key, value in report.items() if key != "integrity"
    }
    observed_core = _sha256(
        (
            json.dumps(
                report_without_integrity,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n"
        ).encode("utf-8")
    )
    legacy_bindings = report.get("legacy_source_bindings", {})
    legacy_sources_exact = (
        legacy_bindings == CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS
        and _sha256(
            _raw_payload(
                ROOT
                / legacy_bindings["IRREDUCIBLE_GAP_CONTRACT_V20_LEGACY"]["path"]
            )
        )
        == legacy_bindings["IRREDUCIBLE_GAP_CONTRACT_V20_LEGACY"]["raw_sha256"]
        and _canonical_legacy_scalar_definition_sha256(
            ROOT / legacy_bindings["RENORMALIZABLE_SCALAR_CHAIN_V20"]["path"]
        )
        == legacy_bindings["RENORMALIZABLE_SCALAR_CHAIN_V20"][
            "definition_sha256"
        ]
    )
    legacy_mapping = report.get("legacy_mapping", {})
    checks = {
        "schema_namespace_definition_and_integrity_exact": (
            set(report) == expected_top_level
            and report.get("schema") == "canonical_g1_g8_gauged_u1x_v21"
            and report.get("status")
            == "CANONICAL_GAUGED_U1X_G1_G8_V21_EVALUATED"
            and report.get("contract_namespace") == CANONICAL_G1_G8_V21_NAMESPACE
            and report.get("model_contract_id")
            == CANONICAL_G1_G8_V21_MODEL_CONTRACT_ID
            and report.get("definition_sha256")
            == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and report.get("integrity")
            == {"core_sha256": CANONICAL_G1_G8_V21_CORE_SHA256}
            and observed_core == CANONICAL_G1_G8_V21_CORE_SHA256
        ),
        "qualified_gate_DAG_artifacts_and_acceptance_exact": gate_rows_exact,
        "gauge_count_and_nonsupersymmetric_G6_exact": (
            report.get("gauge_dimension_derivation")
            == {
                "SO10": 45,
                "U1X": 1,
                "SU3C_stabilizer": 8,
                "U1em_stabilizer": 1,
                "broken": 37,
            }
            and "dimensionful beta"
            in " ".join(gates[5].get("acceptance", [])).lower()
            and "soft beta" not in " ".join(gates[5].get("acceptance", [])).lower()
            if len(gates) == 8
            else False
        ),
        "legacy_namespaces_and_cycle_free_definitions_exact": (
            set(legacy_mapping) == set(CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS)
            and legacy_mapping
            == {
                "IRREDUCIBLE_GAP_CONTRACT_V20_LEGACY": {
                    "definition_sha256": (
                        "87e35c776a024d3129d41c232d22343652ef2cb9905128bae38c1ca63007cb80"
                    ),
                    "scope": (
                        "historical phenomenology draft with stale 33-Goldstone "
                        "and soft-beta wording"
                    ),
                    "can_satisfy_canonical_gate_by_number": False,
                },
                "RENORMALIZABLE_SCALAR_CHAIN_V20": {
                    "definition_sha256": (
                        "1b96316304b80a995a0d39b581d3d6d942599b0efaa69035562ff6f72c4f0e62"
                    ),
                    "scope": (
                        "degree<=4 scalar ring/potential, vacuum, quotient, BFB, "
                        "spectrum and RGE audit"
                    ),
                    "can_satisfy_canonical_gate_by_number": False,
                },
            }
            and legacy_sources_exact
        ),
        "embedded_definition_checks_exact": (
            set(report.get("checks", {})) == expected_check_names
            and all(
                report.get("checks", {}).get(name) is True
                for name in expected_check_names
            )
            and report.get("n_checks") == 10
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "current_three_of_eight_boundary_exact": (
            report.get("overall_state") == "BLOCKED"
            and report.get("closure_counts") == {"closed": 3, "open": 5}
            and report.get("classification")
            == {
                "all_canonical_gates_closed": False,
                "whole_model_validated": False,
                "legacy_bare_gate_numbers_authoritative": False,
            }
            and all(
                (ROOT / artifact).is_file()
                for artifact in CANONICAL_G1_G8_V21_REQUIRED_ARTIFACTS[:3]
            )
            and all(
                not (ROOT / artifact).exists()
                for artifact in CANONICAL_G1_G8_V21_REQUIRED_ARTIFACTS[3:]
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the canonical G1--G8 v21 bundle drifted: {failed}")
    return {
        "portable_file_count": 4,
        "contract_namespace": CANONICAL_G1_G8_V21_NAMESPACE,
        "definition_sha256": CANONICAL_G1_G8_V21_DEFINITION_SHA256,
        "core_sha256": CANONICAL_G1_G8_V21_CORE_SHA256,
        "qualified_gate_count": 8,
        "required_artifact_count": 8,
        "acceptance_criterion_count": 33,
        "closure_capable_contract_and_regression_test_frozen": True,
        "current_closed_gate_count": 3,
        "current_open_gate_count": 5,
        "canonical_G1_closed": True,
        "canonical_G2_closed": True,
        "canonical_G3_closed": True,
        "all_canonical_gates_closed": False,
        "whole_model_validated": False,
        "legacy_bare_gate_numbers_authoritative": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_source_equality_frontier_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS) != 4:
        raise ArithmeticError("the physical-SM source/equality frontier must contain 4 files")
    report = json.loads(
        (ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core_payload = {
        key: report[key]
        for key in (
            "schema",
            "status",
            "model_contract_id",
            "source_bindings",
            "source_row_lattice_frontier",
            "exact_radial_equality",
            "closure_claims",
            "next_required_calculation",
        )
    }
    observed_core = _sha256(
        (
            json.dumps(core_payload, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
    )
    claims = report.get("closure_claims", {})
    lattice = report.get("source_row_lattice_frontier", {})
    checks = {
        "core_schema_status_exact": (
            report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256
            and observed_core == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256
            and report.get("schema")
            == "physical_sm_source_algebra_equality_frontier_v20"
            and report.get("status")
            == "RADIAL_EQUALITY_CLOSED__FULL_SOURCE_ALGEBRA_AND_EQUALITY_ORBIT_OPEN"
        ),
        "radial_equality_only_exact": (
            claims.get("radial_stationary_equality_classified_exactly") is True
            and report.get("exact_radial_equality", {}).get(
                "gcd_V_plus_1_and_dV_dt_monic"
            )
            == "t - 1"
        ),
        "float_lattice_not_promoted": (
            lattice.get("proof_grade") is False
            and lattice.get("source_algebra_derivation_complete") is False
            and lattice.get("direct_exact_projector_arithmetic_used_for_rows")
            is False
        ),
        "full_equality_and_G3_G5_fail_closed": (
            claims.get("direct_source_algebra_stationary_Hessian_available")
            is False
            and claims.get("complete_global_equality_orbit_proved") is False
            and claims.get("physical_SM_G3_closed") is False
            and claims.get("physical_SM_G4_closed") is False
            and claims.get("physical_SM_G5_closed") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the physical-SM source/equality frontier bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS),
        "radial_stationary_equality_classified_exactly": True,
        "direct_source_algebra_Hessian_closed": False,
        "complete_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_five_amplitude_equality_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS) != 4:
        raise ArithmeticError("the five-amplitude equality bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core_keys = (
        "schema", "status", "model_contract_id", "source_bindings",
        "restriction", "exact_polynomial", "exact_Groebner_certificate",
        "discrete_variants", "closure_claims", "remaining_scope",
    )
    observed_core = _sha256(
        (json.dumps({key: report[key] for key in core_keys}, sort_keys=True,
                    separators=(",", ":")) + "\n").encode("utf-8")
    )
    bindings = report.get("source_bindings", {})
    binding_files = bindings.get("files", {})
    live_bindings_exact = bool(
        len(binding_files) == 14
        and all(
            row.get("portable_lf_sha256")
            == row.get("expected_portable_lf_sha256")
            == _sha256(_portable_payload(ROOT / relative))
            and row.get("matches") is True
            for relative, row in binding_files.items()
        )
    )
    restriction = report.get("restriction", {})
    groebner = report.get("exact_Groebner_certificate", {})
    variants = report.get("discrete_variants", {})
    claims = report.get("closure_claims", {})
    checks = {
        "core_schema_status_and_live_sources_exact": (
            observed_core == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and report.get("schema") == "exact_physical_sm_five_amplitude_equality_v20"
            and report.get("status")
            == "EXACT_FIVE_AMPLITUDE_STATIONARY_EQUALITY_CLASSIFIED__FULL_486_ORBIT_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and live_bindings_exact
            and bindings.get("all_portable_lf_and_core_pins_match") is True
        ),
        "exact_five_amplitude_Groebner_classification": (
            restriction.get("ambient_real_field_dimension") == 486
            and restriction.get("slice_dimension") == 5
            and restriction.get("polynomial_fitting_or_float_sampling_used") is False
            and restriction.get("witness_coefficients_directly_derived_from_integer_projector_source_algebra") is False
            and restriction.get("renormalizable_witness_nonzero_parameter_count") == 37
            and restriction.get("nonzero_target_contribution_count") == 28
            and report.get("exact_polynomial", {}).get("aggregate_monomial_count") == 21
            and report.get("exact_polynomial", {}).get("common_denominator") == 1050017221265
            and groebner.get("coefficient_domain") == "QQ"
            and groebner.get("monomial_order") == "grevlex"
            and groebner.get("variables") == ["p", "h", "d", "s", "x"]
            and groebner.get("reduced_Groebner_basis")
            == ["h**2 - 1", "d**2 - 1", "s**2 - 1", "x**2 - 1", "p - 1"]
            and groebner.get("ideals_equal_by_mutual_exact_reduction") is True
            and groebner.get("ideal_zero_dimensional") is True
            and groebner.get("ideal_is_radical_from_squarefree_separated_basis") is True
            and groebner.get("all_solutions_real") is True
            and groebner.get("target_slice_Hessian_positive_definite") is True
        ),
        "sixteen_discrete_variants_but_no_continuous_orbit_claim": (
            variants.get("count") == 16
            and variants.get("exact_discrete_sign_symmetries_of_selected_witness") is True
            and variants.get("full_486_stationarity_inherited_from_upstream_target_under_discrete_sign_symmetry") is True
            and variants.get("continuous_SO10_x_U1X_x_PQ_orbit_equivalence_classified") is False
        ),
        "full_486_and_physical_G3_G4_G5_fail_closed": (
            claims.get("five_real_amplitude_slice_stationary_equality_classified") is True
            and claims.get("full_486_field_stationary_equality_classified") is False
            and claims.get("declared_continuous_symmetry_orbit_equivalence_of_16_variants_proved") is False
            and claims.get("direct_source_algebra_full_486_Hessian_available") is False
            and claims.get("physical_SM_G3_closed") is False
            and claims.get("physical_SM_G4_closed") is False
            and claims.get("physical_SM_G5_closed") is False
            and report.get("n_checks") == 12
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(report.get("checks", {})) == 12
            and all(report.get("checks", {}).values())
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the five-amplitude equality bundle drifted: {failed}")
    return {
        "raw_file_count": 4,
        "transitive_portable_source_count": 14,
        "five_real_amplitude_stationary_equality_classified": True,
        "discrete_real_solution_count": 16,
        "full_486_equality_classified": False,
        "continuous_orbit_equivalence_classified": False,
        "direct_source_algebra_full_486_Hessian_available": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_hard_projector_hessians_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS) != 4:
        raise ArithmeticError("the hard-projector Hessian bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core = {key: value for key, value in report.items() if key != "integrity"}
    observed_core = _sha256(
        (json.dumps(core, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    rows = report.get("certified_rows", [])
    claims = report.get("claims", {})
    scope = report.get("scope_accounting", {})
    checks = {
        "schema_status_core_and_live_source_pins_exact": (
            report.get("schema") == "exact_physical_sm_hard_projector_hessians_v20"
            and report.get("status")
            == "EXACT_TEN_HARD_PROJECTOR_HESSIANS__FULL_37_ROW_AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and observed_core == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
            and bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 6
            and all(
                row.get("portable_lf_sha256")
                == row.get("expected_portable_lf_sha256")
                == _sha256(_portable_payload(ROOT / relative))
                and row.get("matches") is True
                for relative, row in files.items()
            )
        ),
        "ten_exact_486_dimensional_source_Hessians": (
            len(rows) == 10
            and len({row.get("direction_id") for row in rows}) == 10
            and sum(str(row.get("direction_id", "")).startswith("O27_") for row in rows) == 4
            and sum(str(row.get("direction_id", "")).startswith("O44_") for row in rows) == 6
            and all(
                row.get("Hessian", {}).get("dimension") == 486
                and row.get("Hessian", {}).get("symmetric_entrywise_over_Q") is True
                and row.get("exact_target_jet_from_homogeneity", {}).get(
                    "Hq_equals_3_gradient_exactly"
                ) is True
                and row.get("exact_target_jet_from_homogeneity", {}).get(
                    "q_dot_gradient_equals_4V_exactly"
                ) is True
                for row in rows
            )
        ),
        "scope_and_physical_claims_fail_closed": (
            scope.get("active_witness_row_count") == 37
            and scope.get("exact_source_rows_certified_here") == 10
            and scope.get("remaining_active_row_count") == 27
            and claims.get("exact_source_algebra_Hessians_for_all_10_O27_O44_rows") is True
            and claims.get("exact_source_algebra_Hessians_for_all_37_active_witness_rows") is False
            and claims.get("exact_full_witness_aggregate_stationarity") is False
            and claims.get("exact_full_witness_symmetry_kernel") is False
            and claims.get("exact_full_witness_rank_448_and_PSD") is False
            and claims.get("full_486_field_global_equality_orbit_classified") is False
            and all(claims.get(f"physical_SM_{gate}_closed") is False for gate in ("G3", "G4", "G5"))
            and report.get("n_checks") == 11
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(report.get("checks", {})) == 11
            and all(report.get("checks", {}).values())
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the hard-projector Hessian bundle drifted: {failed}")
    return {
        "raw_file_count": 4,
        "live_transitive_source_count": 6,
        "exact_source_Hessian_row_count": 10,
        "remaining_active_row_count": 27,
        "all_37_source_Hessians_available": False,
        "aggregate_stationarity_kernel_rank_PSD_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_last_six_hessians_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS) != 4:
        raise ArithmeticError("the last-six Hessian bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core = {key: value for key, value in report.items() if key != "integrity"}
    observed_core = _sha256(
        (json.dumps(core, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    rows = report.get("certified_rows", [])
    claims = report.get("claims", {})
    scope = report.get("scope_accounting", {})
    checks = {
        "schema_status_core_and_ten_live_sources_exact": (
            report.get("schema") == "exact_physical_sm_last_six_hessians_v20"
            and report.get("status")
            == "EXACT_LAST_SIX_SOURCE_HESSIANS__ALL_37_ROWS_AVAILABLE__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and observed_core == PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
            and bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 10
            and all(
                row.get("portable_lf_sha256")
                == _sha256(_portable_payload(ROOT / relative))
                and row.get("matches") is True
                for relative, row in files.items()
            )
        ),
        "six_exact_486_dimensional_source_Hessians": (
            len(rows) == 6
            and len({row.get("direction_id") for row in rows}) == 6
            and sum(str(row.get("direction_id", "")).startswith("O14_") for row in rows) == 1
            and sum(str(row.get("direction_id", "")).startswith("O35_") for row in rows) == 2
            and sum(str(row.get("direction_id", "")).startswith("O46_") for row in rows) == 3
            and all(
                row.get("Hessian", {}).get("dimension") == 486
                and row.get("Hessian", {}).get("symmetric_entrywise_over_Q") is True
                and row.get("exact_target_jet_from_homogeneity", {}).get(
                    "Hq_equals_degree_minus_1_times_gradient_exactly"
                ) is True
                and row.get("exact_target_jet_from_homogeneity", {}).get(
                    "q_dot_gradient_equals_degree_times_value_exactly"
                ) is True
                for row in rows
            )
        ),
        "all_37_available_but_aggregate_global_and_G3_G5_fail_closed": (
            scope.get("easy_rows") == 21
            and scope.get("hard_rows") == 10
            and scope.get("last_rows") == 6
            and scope.get("total_active_source_Hessians_available") == 37
            and claims == {
                "all_37_active_source_Hessians_available_across_three_theorems": True,
                "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here": False,
                "exact_last_six_source_Hessians": True,
                "full_486_field_global_equality_orbit_classified": False,
                "physical_SM_G3_closed": False,
                "physical_SM_G4_closed": False,
                "physical_SM_G5_closed": False,
            }
            and report.get("n_checks") == 6
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(report.get("checks", {})) == 6
            and all(report.get("checks", {}).values())
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the last-six Hessian bundle drifted: {failed}")
    return {
        "raw_file_count": 4,
        "live_transitive_source_count": 10,
        "exact_last_six_source_Hessians_closed": True,
        "all_37_active_source_Hessians_available": True,
        "aggregate_stationarity_kernel_rank_PSD_closed": False,
        "full_486_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_37_row_aggregate_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS) != 4:
        raise ArithmeticError("the 37-row aggregate bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core = {key: value for key, value in report.items() if key != "integrity"}
    observed_core = _sha256(
        (json.dumps(core, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    assembly = report.get("source_aggregate_assembly", {})
    stationarity = report.get("exact_stationarity", {})
    kernel = report.get("exact_kernel_and_rank", {})
    modular = kernel.get("modular_lower_bound_certificate", {})
    psd = report.get("exact_PSD_certificate", {})
    claims = report.get("claims", {})
    scope = report.get("scope_boundary", {})
    expected_checks = {
        "all_37_rows_present", "all_generator_columns_annihilated",
        "exact_PSD", "exact_rank_and_kernel", "exact_source_Hq_consistency",
        "exact_value_and_stationarity", "global_equality_and_G3_G4_G5_fail_closed",
        "source_aggregate_matches_historical_reconstruction_entrywise",
        "source_pins_match",
    }
    checks = {
        "schema_status_core_and_eight_live_sources_exact": (
            report.get("schema") == "exact_physical_sm_37_row_aggregate_v20"
            and report.get("status")
            == "EXACT_ALL_37_SOURCE_AGGREGATE_STATIONARY_KERNEL_RANK_PSD__GLOBAL_EQUALITY_ORBIT_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and observed_core == PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
            and bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 8
            and all(
                row.get("portable_lf_sha256")
                == _sha256(_portable_payload(ROOT / relative))
                and row.get("matches") is True
                for relative, row in files.items()
            )
        ),
        "exact_value_stationarity_kernel_rank_and_PSD": (
            assembly.get("active_row_count") == 37
            and assembly.get("nonzero_entries") == 5840
            and assembly.get("denominator") == 6300103327590
            and assembly.get("canonical_sparse_Q_sqrt2_serialization_sha256")
            == "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458"
            and assembly.get("entrywise_identity_to_historical_reconstructed_rational_aggregate") is True
            and stationarity.get("exact_potential_value") == "-1"
            and stationarity.get("exact_gradient_is_zero") is True
            and stationarity.get("aggregate_Hq_matches_weighted_source_Hq_entrywise") is True
            and kernel.get("exact_rank") == 448
            and kernel.get("exact_nullity") == 38
            and kernel.get("exact_symmetry_tangent_span_dimension") == 38
            and kernel.get("kernel_equals_exact_symmetry_tangent_span") is True
            and modular.get("prime") == 1009
            and modular.get("rank") == 448
            and modular.get("principal_minor_determinant_mod_prime") == 870
            and psd.get("principal_minor_dimension") == 448
            and psd.get("strictly_positive_exact_pivot_count") == 448
            and psd.get("all_exact_pivots_strictly_positive") is True
            and psd.get("positive_pivot_sha256_chain")
            == "58b41d4c2be5fbc31b0ada79b653e84561e0db629a3d600053d44d760824c259"
            and psd.get("full_Hessian_is_positive_semidefinite") is True
            and psd.get("full_Hessian_is_positive_definite_mod_kernel") is True
        ),
        "local_complete_but_global_and_physical_G3_G5_fail_closed": (
            scope.get("source_bound_local_stationary_Hessian_problem_complete") is True
            and scope.get("global_equality_orbit_classification_complete") is False
            and claims.get("all_37_active_Hessians_derived_from_exact_source_algebra") is True
            and claims.get("exact_source_aggregate_value_minus_one_and_stationary") is True
            and claims.get("exact_source_aggregate_kernel_is_38_dimensional_symmetry_span") is True
            and claims.get("exact_source_aggregate_rank_is_448") is True
            and claims.get("exact_source_aggregate_is_PSD_and_strictly_positive_mod_symmetry") is True
            and claims.get("full_486_field_global_equality_orbit_classified") is False
            and all(claims.get(f"physical_SM_{gate}_closed") is False for gate in ("G3", "G4", "G5"))
            and set(report.get("checks", {})) == expected_checks
            and all(report.get("checks", {}).get(name) is True for name in expected_checks)
            and report.get("n_checks") == 9
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the 37-row aggregate bundle drifted: {failed}")
    return {
        "raw_file_count": 4,
        "live_transitive_source_count": 8,
        "all_37_active_Hessians_source_derived": True,
        "exact_stationary_value_minus_one": True,
        "exact_symmetry_kernel_dimension": 38,
        "exact_rank": 448,
        "exact_PSD_strict_mod_symmetry": True,
        "source_bound_local_stationary_Hessian_problem_complete": True,
        "full_486_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_local_equality_orbit_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS) != 4:
        raise ArithmeticError("the local equality-orbit bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core = {key: value for key, value in report.items() if key != "integrity"}
    observed_core = _sha256(
        (json.dumps(core, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    theorem = report.get("local_orbit_theorem", {})
    hypotheses = theorem.get("hypotheses", {})
    signs = report.get("sixteen_sign_orbit", {})
    rows = signs.get("rows", [])
    embedding = signs.get("actual_target_representation_embedding", {})
    embedding_checks = embedding.get("checks", {})
    scope = report.get("scope_boundary", {})
    claims = report.get("claims", {})
    expected_top = {
        "schema", "status", "model_contract_id", "source_bindings",
        "local_orbit_theorem", "sixteen_sign_orbit", "scope_boundary",
        "claims", "checks", "n_checks", "n_failed", "failures", "integrity",
    }
    expected_claims = {
        "Crit_V_intersection_U_equals_target_orbit": True,
        "all_16_five_amplitude_sign_variants_one_continuous_K_orbit": True,
        "complete_486_field_global_equality_orbit_classified": False,
        "exists_K_invariant_open_neighborhood_U_of_target_orbit": True,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "quantitative_radius_for_U_proved": False,
        "stationary_V_minus_one_locus_intersection_U_equals_target_orbit": True,
        "target_orbit_is_strict_local_minimum_in_U_mod_K": True,
    }
    expected_checks = {
        "actual_486_target_and_representation_embedding_source_verified",
        "all_16_five_amplitude_variants_are_one_declared_continuous_orbit",
        "all_equivariant_Morse_Bott_slice_hypotheses_hold", "dependency_pins_match",
        "every_sign_row_group_action_matches_all_actual_nonzero_target_coordinates",
        "every_sign_row_has_verified_exact_phase_action", "exactly_16_sign_rows",
        "five_amplitude_exact_solution_ideal_and_bit_order_source_bound",
        "full_486_local_stationary_equality_locus_is_exactly_one_K_orbit",
        "full_486_local_stationary_locus_is_exactly_one_K_orbit",
        "global_G3_G4_G5_remain_fail_closed",
        "no_quantitative_neighborhood_radius_claimed", "upstream_core_pins_match",
    }
    checks = {
        "schema_status_core_and_seven_live_sources_exact": (
            set(report) == expected_top
            and report.get("schema") == "exact_physical_sm_local_equality_orbit_v20"
            and report.get("status")
            == "EXACT_FULL_486_LOCAL_EQUALITY_ORBIT_AND_16_SIGN_ORBIT__GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and observed_core == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
            and bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 7
            and all(
                set(row)
                == {"portable_lf_sha256", "expected_portable_lf_sha256", "matches"}
                and row.get("portable_lf_sha256")
                == row.get("expected_portable_lf_sha256")
                == _sha256(_portable_payload(ROOT / relative))
                and row.get("matches") is True
                for relative, row in files.items()
            )
        ),
        "full_486_local_Morse_Bott_orbit_exact": (
            theorem.get("ambient_real_dimension") == 486
            and theorem.get("group_K") == "SO(10) x U(1)_X x U(1)_PQ"
            and theorem.get("target_orbit_dimension") == 38
            and theorem.get("normal_slice_dimension") == 448
            and theorem.get("quantitative_radius") is None
            and hypotheses.get("K_is_compact") is True
            and hypotheses.get("K_acts_smoothly_and_orthogonally_on_R486") is True
            and hypotheses.get("selected_potential_is_K_invariant") is True
            and hypotheses.get("target_is_exact_stationary_point_with_V_minus_one") is True
            and hypotheses.get("orbit_tangent_dimension") == 38
            and hypotheses.get("Hessian_kernel_dimension") == 38
            and hypotheses.get("Hessian_kernel_equals_orbit_tangent") is True
            and hypotheses.get("Hessian_positive_definite_on_a_transverse_complement") is True
        ),
        "all_16_sign_variants_one_continuous_K_orbit_exact": (
            len(rows) == 16
            and len({tuple(row.get("bits_h_d_s_x", [])) for row in rows}) == 16
            and {tuple(row.get("bits_h_d_s_x", [])) for row in rows}
            == {
                (h, d, s, x)
                for h in (0, 1)
                for d in (0, 1)
                for s in (0, 1)
                for x in (0, 1)
            }
            and all(
                row.get("actual_486_coordinate_endpoint_matches_amplitude_variant")
                is True
                and len(row.get("SO10_Cartan_theta_0_to_4_over_pi", [])) == 5
                and set(row.get("verified_net_phase_exponents_over_pi", {}))
                == {"H", "Sigma", "S", "Phi17"}
                and isinstance(row.get("transformed_target_sparse_sha256"), str)
                and len(row.get("transformed_target_sparse_sha256")) == 64
                for row in rows
            )
            and signs.get("continuous_path")
            == "scale every listed angle simultaneously from t=0 to t=1"
            and signs.get("source_solution_set")
            == "p=1; h,d,s,x independently in {-1,+1}"
            and set(embedding)
            == {
                "PQ_charges", "U1X_charges", "checks", "plane_actions",
                "source", "target_sparse_integer_coordinates",
            }
            and len(embedding.get("target_sparse_integer_coordinates", {})) == 21
            and len(embedding.get("plane_actions", [])) == 5
            and len(embedding_checks) == 7
            and all(embedding_checks.values())
        ),
        "local_positive_but_radius_global_and_physical_G3_G5_fail_closed": (
            claims == expected_claims
            and scope
            == {
                "distant_or_disconnected_equality_components_excluded": False,
                "global_polynomial_ideal_or_global_SOS_orbit_separator_supplied": False,
                "not_just_five_amplitude_slice": True,
                "theorem_is_full_486_dimensional_but_local_near_the_entire_compact_orbit": True,
            }
            and set(report.get("checks", {})) == expected_checks
            and all(report.get("checks", {}).get(name) is True for name in expected_checks)
            and report.get("n_checks") == 13
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the local equality-orbit bundle drifted: {failed}")
    return {
        "portable_file_count": 4,
        "live_transitive_source_count": 7,
        "full_486_local_stationary_orbit_classified": True,
        "full_486_local_stationary_equality_orbit_classified": True,
        "all_16_sign_variants_one_continuous_K_orbit": True,
        "target_orbit_strict_local_minimum_mod_K": True,
        "quantitative_neighborhood_radius_proved": False,
        "complete_486_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_physical_sm_g4_g5_branch_mismatch_bundle() -> dict[str, Any]:
    if len(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS) != 4:
        raise ArithmeticError("the G4/G5 branch-mismatch bundle must contain 4 files")
    report = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json").read_text(
            encoding="utf-8"
        )
    )
    core_keys = (
        "schema", "status", "contract_id", "model_contract_id", "source_binding",
        "exact_branch_mismatch", "unit_rescaling_audit_0_through_100",
        "gate_acceptance_boundary", "scope", "next_required_work",
    )
    observed_core = _sha256(
        (json.dumps({key: report[key] for key in core_keys}, sort_keys=True,
                    separators=(",", ":")) + "\n").encode()
    )
    binding = report.get("source_binding", {})
    files = binding.get("files", {})
    live_files_exact = True
    for row in files.values():
        path = ROOT / str(row.get("path", ""))
        mode = row.get("binding_mode")
        if mode == "portable_lf":
            observed = _sha256(_portable_payload(path))
        elif mode == "semantic_json":
            observed = _sha256(
                (json.dumps(json.loads(path.read_text(encoding="utf-8")),
                            sort_keys=True, separators=(",", ":")) + "\n").encode()
            )
        else:
            observed = ""
        live_files_exact = bool(
            live_files_exact
            and row.get("observed_sha256") == row.get("expected_sha256") == observed
            and row.get("matches") is True
        )
    mismatch = report.get("exact_branch_mismatch", {})
    exact = mismatch.get("exact_mismatch", {})
    audit = report.get("unit_rescaling_audit_0_through_100", {})
    gates = report.get("gate_acceptance_boundary", {})
    scope = report.get("scope", {})
    expected_check_names = {
        "all_101_common_unit_rescalings_preserve_ratio",
        "all_G4_through_G8_closure_flags_fail_closed",
        "all_dependency_pins_match",
        "branch_ratios_are_exactly_unequal",
        "current_witness_not_promoted_to_canonical_G4_or_G5",
        "five_amplitude_ratio_is_exactly_two",
        "mismatch_exceeds_10_pow_26",
        "not_misrepresented_as_global_no_go",
        "physical_hierarchy_ratio_is_exact_nonzero",
        "unit_audit_covers_cases_0_through_100",
    }
    checks = {
        "schema_status_core_and_seven_live_dependencies_exact": (
            report.get("schema") == "exact_physical_sm_g4_g5_branch_mismatch_v1"
            and report.get("status")
            == "EXACT_FIVE_AMPLITUDE_VS_PHYSICAL_EW_BRANCH_MISMATCH_PROVED__CANONICAL_G4_G5_AND_DOWNSTREAM_G6_G8_OPEN"
            and report.get("contract_id") == "exact_physical_sm_g4_g5_branch_mismatch_v20"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and observed_core == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
            and binding.get("all_dependency_pins_match") is True
            and binding.get("five_amplitude_core_sha256")
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and binding.get("physical_SM_foundation_core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
            and len(files) == 7
            and live_files_exact
        ),
        "exact_mismatch_and_101_rescalings": (
            mismatch.get("five_amplitude_branch", {}).get("H_over_Phi_squared") == "2"
            and exact.get("ratios_are_equal") is False
            and exact.get("mismatch_exceeds_10_pow_26_in_squared_ratio") is True
            and exact.get("common_unit_rescaling_can_remove_mismatch") is False
            and audit.get("case_range") == [0, 100]
            and audit.get("case_count") == 101
            and audit.get("identity_case") == 50
            and audit.get("all_common_rescalings_preserve_ratio") is True
        ),
        "not_global_no_go_and_G4_through_G8_fail_closed": (
            set(gates) == {"G4", "G5", "G6", "G7", "G8"}
            and all(
                value is False
                for gate in gates.values()
                for key, value in gate.items()
                if key.endswith("_closed") or key.startswith("promoted_by_this_")
            )
            and scope.get("exact_branch_mismatch_proved") is True
            and scope.get("global_no_go_for_all_possible_physical_EW_branches") is False
            and scope.get("new_hierarchy_mechanism_ruled_out") is False
            and scope.get("physical_G4_G5_G6_G7_G8_closed") is False
            and scope.get("release_G4_G5_G6_G7_G8_closed") is False
            and scope.get("authoritative_G4_G5_G6_G7_G8_closed") is False
            and report.get("n_checks") == 10
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and set(report.get("checks", {})) == expected_check_names
            and all(
                report.get("checks", {}).get(name) is True
                for name in expected_check_names
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the G4/G5 branch-mismatch bundle drifted: {failed}")
    return {
        "raw_file_count": 4,
        "live_dependency_count": 7,
        "exact_branch_mismatch_proved": True,
        "unit_rescaling_case_count": 101,
        "global_no_go_for_other_physical_EW_branches": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "physical_SM_G6_closed": False,
        "physical_SM_G7_closed": False,
        "physical_SM_G8_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_exact_x_v3_fail_closed_bundle() -> dict[str, Any]:
    if len(EXACT_X_V3_RAW_PINS) != 9 or len(EXACT_X_V3_PORTABLE_PINS) != 2:
        raise ArithmeticError("the exact-X v3 bundle must contain 11 files")
    report = json.loads(
        (ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    input_manifest = json.loads(
        (ROOT / "models/EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json").read_text(
            encoding="utf-8"
        )
    )
    trusted_manifest = json.loads(
        (ROOT / "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    attestation = json.loads(
        (ROOT / "models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json").read_text(
            encoding="utf-8"
        )
    )
    expected_entries = [
        {"path": "models/SO10Z17AxionV20.m", "sha256": EXACT_X_V3_RAW_PINS["models/SO10Z17AxionV20.m"], "size_bytes": 5182, "role": "primary_model", "format": "sarah-mathematica"},
        {"path": "tools/validate-exact-x-model.wls", "sha256": EXACT_X_V3_RAW_PINS["tools/validate-exact-x-model.wls"], "size_bytes": 10529, "role": "validation_driver", "format": "wolfram-language"},
        {"path": "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json", "sha256": EXACT_X_V3_RAW_PINS["models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"], "size_bytes": 198868, "role": "trusted_sarah_release_manifest", "format": "sarah-source-tree-manifest"},
    ]
    tree = trusted_manifest.get("tree", {})
    tree_files = tree.get("files", [])
    tree_core = _sha256(
        json.dumps(tree_files, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")
    )
    repository = report.get("repository_external_input_manifest", {})
    trusted = repository.get("trusted_sarah_release_manifest", {})
    external = report.get("external_model_validation", {})
    external_checks = external.get("checks", {})
    attestation_checks = {
        "model_parse_succeeded": True,
        "model_initialization_succeeded": True,
        "lagrangian_construction_succeeded": True,
        "gauge_invariance_check_succeeded": True,
        "anomaly_check_succeeded": True,
    }
    checks = {
        "input_manifest_exact_and_transitive_bytes_bound": (
            input_manifest.get("schema") == "so10-exact-x-input-manifest-v2"
            and input_manifest.get("sha256") == "0f9050ef8e9ac9cd0a398e7fb8d59b12675d51065610d8dbf4903b87fcd7c313"
            and input_manifest.get("files") == expected_entries
            and repository.get("expected") == input_manifest
            and repository.get("present") is True
            and repository.get("valid") is True
            and repository.get("load_error") is None
            and repository.get("driver_load_error") is None
            and repository.get("trusted_release_manifest_load_error") is None
        ),
        "trusted_SARAH_4_15_3_tree_exact": (
            trusted_manifest.get("schema") == "sarah-canonical-source-tree-v1"
            and tree.get("file_count") == len(tree_files) == 1056
            and tree.get("size_bytes") == sum(row["size_bytes"] for row in tree_files) == 20165588
            and tree.get("sha256") == tree_core == EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
            and trusted.get("valid") is True
            and trusted.get("failures") == []
            and trusted.get("tree", {}).get("calculated_sha256") == EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
        ),
        "external_v3_attestation_is_genuine_and_source_bound": (
            external.get("present") is True
            and external.get("valid") is True
            and external.get("schema") == "so10-exact-x-external-model-validation-v3"
            and external.get("fresh_for_exact_model_bytes") is True
            and external.get("load_error") is None
            and len(external_checks) == 47
            and all(value is True for value in external_checks.values())
            and attestation.get("schema") == "so10-exact-x-external-model-validation-v3"
            and attestation.get("checks") == attestation_checks
            and attestation.get("execution", {}).get("external_process_executed") is True
            and attestation.get("execution", {}).get("process_exit_code") == 0
            and attestation.get("execution", {}).get("runtime_probe_exit_code") == 0
            and attestation.get("tool", {}).get("name") == "SARAH"
            and attestation.get("tool", {}).get("version") == "4.15.3"
            and attestation.get("tool", {}).get("source_tree", {}).get("sha256")
            == EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
            and attestation.get("tool", {}).get("source_tree", {}).get(
                "unchanged_during_execution"
            ) is True
        ),
        "exact_X_contract_and_authoritative_runtime_are_closed": (
            report.get("status") == "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__CONSISTENT"
            and report.get("overall_state") == "PASS"
            and report.get("n_checks") == 25
            and report.get("n_failed") == 0
            and report.get("static_contract_consistent") is True
            and report.get("contract_consistent") is True
            and report.get("blocker") is None
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the exact-X v3 fail-closed bundle drifted: {failed}")
    return {
        "raw_file_count": 9,
        "portable_file_count": 2,
        "trusted_SARAH_source_tree_file_count": 1056,
        "trusted_SARAH_source_tree_core_sha256": EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256,
        "static_native_contract_closed": True,
        "external_v3_execution_attestation_present": True,
        "external_v3_execution_attestation_valid": True,
        "authoritative_exact_X_contract_closed": True,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_canonical_g1_dim6_bundle() -> dict[str, Any]:
    """Bind the exact dimension-six G1 character, channel and verifier chain."""
    if len(CANONICAL_G1_DIM6_PORTABLE_PINS) != 12:
        raise ArithmeticError("the canonical G1 dimension-six bundle must contain 12 files")
    for relative, expected in CANONICAL_G1_DIM6_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(f"canonical G1 dimension-six member drifted: {relative}")
    frontier = json.loads(
        (ROOT / "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json").read_text(
            encoding="utf-8"
        )
    )
    channels = json.loads(
        (ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json").read_text(
            encoding="utf-8"
        )
    )
    complete = json.loads(
        (ROOT / "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json").read_text(
            encoding="utf-8"
        )
    )
    counts = frontier.get("exact_character_census", {}).get("counts", {})
    construction = channels.get("construction", {})
    proof = complete.get("proof_summary", {})
    checks = {
        "character_census_is_exact_and_source_bound": (
            frontier.get("schema") == "canonical_g1_scalar_ring_dim6_frontier_v1"
            and frontier.get("core_sha256") == CANONICAL_G1_DIM6_FRONTIER_CORE_SHA256
            and frontier.get("n_failed") == 0
            and counts.get("charge_and_so10_allowed_multidegrees") == 168
            and counts.get("complex_invariant_multiplicity") == 891
            and counts.get("real_coefficient_count") == 891
            and counts.get("complex_invariant_multiplicity_by_degree", {}).get("5") == 119
            and counts.get("complex_invariant_multiplicity_by_degree", {}).get("6") == 721
            and frontier.get("v3_SARAH_runtime_attestation", {}).get("valid") is True
        ),
        "independent_Susyno_channel_basis_matches_every_sector": (
            channels.get("schema") == "canonical_g1_susyno_channel_basis_v1"
            and channels.get("status") == "EXACT_SUSYNO_CONSTRUCTIVE_CHANNEL_BASIS_DIM6_COMPLETE"
            and channels.get("core_sha256") == CANONICAL_G1_SUSYNO_CHANNEL_CORE_SHA256
            and channels.get("n_failed") == 0
            and len(channels.get("rows", [])) == 168
            and construction.get("basis_direction_count") == 891
            and construction.get("all_sector_lower_bounds_equal_character_upper_bounds") is True
        ),
        "trusted_final_verifier_and_complete_evidence_are_exact": (
            complete.get("schema") == "canonical_gauged_u1x_gate_evidence_v1"
            and complete.get("qualified_gate_id") == CANONICAL_G1_G8_V21_GATE_IDS[0]
            and complete.get("definition_sha256") == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and complete.get("core_sha256") == CANONICAL_G1_COMPLETE_RING_CORE_SHA256
            and _producer_core_sha256(complete) == CANONICAL_G1_COMPLETE_RING_CORE_SHA256
            and complete.get("closure_complete") is True
            and type(complete.get("n_failed")) is int
            and complete.get("n_failed") == 0
            and complete.get("failures") == []
            and set(complete.get("acceptance_evidence", {})) == {"A1", "A2", "A3", "A4"}
            and all(
                row.get("passed") is True
                for row in complete.get("acceptance_evidence", {}).values()
            )
            and proof.get("neutral_field_content_sectors") == 168
            and proof.get("complex_invariant_directions") == 891
            and proof.get("real_potential_coefficients") == 891
            and proof.get("v3_SARAH_runtime_attestation_valid") is True
            and CANONICAL_G1_DIM6_PORTABLE_PINS[
                "verify_canonical_g1_complete_operator_ring_dim6_v21.py"
            ] == CANONICAL_G1_TRUSTED_VERIFIER_SHA256
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the canonical G1 dimension-six bundle drifted: {failed}")
    return {
        "portable_file_count": 12,
        "neutral_field_content_sector_count": 168,
        "complex_invariant_direction_count": 891,
        "real_potential_coefficient_count": 891,
        "degree_five_direction_count": 119,
        "degree_six_direction_count": 721,
        "frontier_core_sha256": CANONICAL_G1_DIM6_FRONTIER_CORE_SHA256,
        "Susyno_channel_core_sha256": CANONICAL_G1_SUSYNO_CHANNEL_CORE_SHA256,
        "complete_ring_core_sha256": CANONICAL_G1_COMPLETE_RING_CORE_SHA256,
        "trusted_verifier_raw_sha256": CANONICAL_G1_TRUSTED_VERIFIER_SHA256,
        "canonical_G1_closed": True,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_canonical_g2_dim6_bundle() -> dict[str, Any]:
    """Bind all exact G2 contraction bases, PS/SM projections and verifier."""
    if len(CANONICAL_G2_DIM6_PORTABLE_PINS) != 11:
        raise ArithmeticError("the canonical G2 dimension-six bundle must contain 11 files")
    for relative, expected in CANONICAL_G2_DIM6_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(f"canonical G2 dimension-six member drifted: {relative}")
    basis = json.loads(
        (ROOT / "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json").read_text(
            encoding="utf-8"
        )
    )
    projection = json.loads(
        (ROOT / "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json").read_text(
            encoding="utf-8"
        )
    )
    proof = projection.get("proof_summary", {})
    explicit = projection.get("explicit_required_coefficients", {})
    checks = {
        "all_exact_contraction_bases_are_source_bound": (
            basis.get("schema") == "canonical_g2_exact_contraction_basis_v1"
            and basis.get("status")
            == "EXACT_ALL_891_G1_INVARIANTS_HAVE_COMPONENT_CONTRACTION_CIRCUITS"
            and basis.get("core_sha256") == CANONICAL_G2_EXACT_BASIS_CORE_SHA256
            and _producer_core_sha256(basis) == CANONICAL_G2_EXACT_BASIS_CORE_SHA256
            and type(basis.get("n_failed")) is int
            and basis.get("n_failed") == 0
            and basis.get("non_singlet_sector_count") == 105
            and basis.get("non_singlet_basis_direction_count") == 794
            and basis.get("neutral_field_content_sector_count") == 168
            and basis.get("canonical_invariant_direction_count") == 891
            and len(basis.get("sectors", [])) == 105
            and len(basis.get("g1_row_projection_map", [])) == 168
            and all(value is True for value in basis.get("checks", {}).values())
        ),
        "all_normalized_PS_and_SM_component_circuits_are_exact": (
            projection.get("schema") == "canonical_gauged_u1x_gate_evidence_v1"
            and projection.get("qualified_gate_id") == CANONICAL_G1_G8_V21_GATE_IDS[1]
            and projection.get("definition_sha256") == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and projection.get("dependencies") == [CANONICAL_G1_G8_V21_GATE_IDS[0]]
            and projection.get("core_sha256") == CANONICAL_G2_FULL_PROJECTION_CORE_SHA256
            and _producer_core_sha256(projection) == CANONICAL_G2_FULL_PROJECTION_CORE_SHA256
            and projection.get("closure_complete") is True
            and type(projection.get("n_failed")) is int
            and projection.get("n_failed") == 0
            and projection.get("failures") == []
            and proof.get("G1_neutral_sectors") == 168
            and proof.get("G1_canonical_directions") == 891
            and proof.get("unique_non_singlet_count_tuples") == 105
            and proof.get("independent_non_singlet_contraction_directions") == 794
            and proof.get("materialized_direction_records") == 891
            and len(projection.get("projection_catalog", [])) == 891
            and all(value is True for value in projection.get("checks", {}).values())
        ),
        "lambda4_and_dimension_six_lock_are_explicit_and_normalized": (
            explicit.get("lambda4", {}).get("formula")
            == "lambda4*S*H_e*P_abcd*D_abcde/4! + h.c."
            and explicit.get("lambda4", {}).get("direction_id")
            == "g1_row_026_basis_001"
            and explicit.get("dimension_six_lock", {}).get("formula")
            == "lambda_lock*S^2*H_i*H_j*D_iabcd*D_jabcd/4! + h.c."
            and explicit.get("dimension_six_lock", {}).get("direction_id")
            == "g1_row_108_basis_001"
            and "unique symmetric-traceless 54 contraction"
            in explicit.get("dimension_six_lock", {}).get("channel", "")
        ),
        "trusted_gate_verifier_is_raw_hash_bound": (
            CANONICAL_G2_DIM6_PORTABLE_PINS[
                "verify_canonical_g2_full_component_projection_dim6_v21.py"
            ]
            == CANONICAL_G2_TRUSTED_VERIFIER_SHA256
            and set(projection.get("acceptance_evidence", {}))
            == {"A1", "A2", "A3", "A4"}
            and all(
                row.get("passed") is True
                for row in projection.get("acceptance_evidence", {}).values()
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the canonical G2 dimension-six bundle drifted: {failed}")
    return {
        "portable_file_count": 11,
        "non_singlet_sector_count": 105,
        "non_singlet_direction_count": 794,
        "neutral_G1_sector_count": 168,
        "canonical_direction_count": 891,
        "PS_component_block_combination_count": 9_606_125,
        "SM_component_block_combination_count": 177_282_240_225,
        "exact_basis_core_sha256": CANONICAL_G2_EXACT_BASIS_CORE_SHA256,
        "full_projection_core_sha256": CANONICAL_G2_FULL_PROJECTION_CORE_SHA256,
        "trusted_verifier_raw_sha256": CANONICAL_G2_TRUSTED_VERIFIER_SHA256,
        "canonical_G2_closed": True,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_canonical_g3_global_vacuum_bundle() -> dict[str, Any]:
    """Bind the exact full-field global-vacuum certificate and trusted replay."""
    if len(CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS) != 6:
        raise ArithmeticError("the canonical G3 global-vacuum bundle must contain 6 files")
    for relative, expected in CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS.items():
        if _sha256(_portable_payload(ROOT / relative)) != expected:
            raise ArithmeticError(f"canonical G3 global-vacuum member drifted: {relative}")
    report = json.loads(
        (ROOT / "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json").read_text(
            encoding="utf-8"
        )
    )
    stationarity = report.get("stationarity_and_Hessian", {})
    global_orbit = report.get("global_orbit", {})
    potential = report.get("accepted_potential", {})
    scope = report.get("scope_boundary", {})
    manifest = report.get("source_manifest", [])
    checks = {
        "qualified_evidence_and_core_are_exact": (
            report.get("schema") == "canonical_gauged_u1x_gate_evidence_v1"
            and report.get("contract_namespace") == CANONICAL_G1_G8_V21_NAMESPACE
            and report.get("definition_sha256") == CANONICAL_G1_G8_V21_DEFINITION_SHA256
            and report.get("qualified_gate_id") == CANONICAL_G1_G8_V21_GATE_IDS[2]
            and report.get("dependencies") == [CANONICAL_G1_G8_V21_GATE_IDS[1]]
            and report.get("core_sha256") == CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256
            and _producer_core_sha256(report) == CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256
            and report.get("closure_complete") is True
            and type(report.get("n_failed")) is int
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and report.get("status")
            == "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_EXACTLY_CLOSED"
        ),
        "complete_accepted_potential_is_bound": (
            potential.get("canonical_total_real_directions") == 891
            and potential.get("degree_direction_counts")
            == {"2": 5, "3": 6, "4": 40, "5": 119, "6": 721}
            and potential.get("degree_at_most_four_real_directions") == 51
            and potential.get("nonzero_renormalizable_tensor_directions") == 28
            and potential.get("zero_dimension_five_directions") == 119
            and potential.get("zero_dimension_six_directions") == 721
            and potential.get("all_dimension_five_and_six_coefficients")
            == "exactly zero"
        ),
        "global_value_stationarity_Hessian_and_kernel_are_exact": (
            stationarity.get("field_dimension") == 486
            and stationarity.get("exact_total_value") == "-1"
            and stationarity.get("exact_gradient_nonzero_entries") == 0
            and stationarity.get("exact_rank") == 448
            and stationarity.get("exact_nullity") == 38
            and stationarity.get("gauge_orbit_rank") == 37
            and stationarity.get("full_symmetry_orbit_rank") == 38
            and stationarity.get("kernel_equals_full_symmetry_tangent_span") is True
            and stationarity.get("all_448_non_symmetry_modes_strictly_positive") is True
            and stationarity.get("intended_axion_direction_count") == 1
        ),
        "global_minimum_and_equality_orbit_are_exact": (
            global_orbit.get("standard_Q3_annihilates_target") is True
            and global_orbit.get("exact_stabilizer_is_SU3C_plus_U1em") is True
            and global_orbit.get("broken_gauge_directions") == 37
            and isinstance(global_orbit.get("connectedness"), str)
            and "connected" in global_orbit.get("connectedness", "")
            and global_orbit.get("all_global_minima_one_continuous_symmetry_orbit") is True
            and global_orbit.get("no_deeper_extremum") is True
            and global_orbit.get("no_disconnected_equal_minimum") is True
        ),
        "source_manifest_and_trusted_verifier_are_frozen": (
            isinstance(manifest, list)
            and len(manifest) == 15
            and all(
                row.get("mode") == "portable-lf"
                and _sha256(_portable_payload(ROOT / row.get("path", "")))
                == row.get("sha256")
                for row in manifest
            )
            and CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS[
                "verify_canonical_g3_physical_ew_global_vacuum_v21.py"
            ]
            == CANONICAL_G3_TRUSTED_VERIFIER_SHA256
        ),
        "embedded_checks_and_scope_boundary_are_exact": (
            report.get("n_checks") == 11
            and len(report.get("checks", {})) == 11
            and all(value is True for value in report.get("checks", {}).values())
            and scope
            == {
                "canonical_G3_closed": True,
                "absolute_electroweak_hierarchy_h_174_GeV_proved": False,
                "canonical_G4_closed": False,
                "canonical_G5_through_G8_closed": False,
            }
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(f"the canonical G3 global-vacuum bundle drifted: {failed}")
    return {
        "portable_file_count": 6,
        "canonical_total_real_direction_count": 891,
        "nonzero_renormalizable_direction_count": 28,
        "field_dimension": 486,
        "exact_value": "-1",
        "exact_rank": 448,
        "exact_nullity": 38,
        "gauge_orbit_rank": 37,
        "full_symmetry_orbit_rank": 38,
        "global_minimum_orbit_unique": True,
        "core_sha256": CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256,
        "trusted_verifier_raw_sha256": CANONICAL_G3_TRUSTED_VERIFIER_SHA256,
        "canonical_G3_closed": True,
        "canonical_G4_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_legacy_so10_210_beta_diagnostic_bundle() -> dict[str, Any]:
    if len(LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS) != 2:
        raise ArithmeticError(
            "the legacy SO(10)+210 beta diagnostic must contain exactly 2 reports"
        )
    json_path = ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json"
    md_path = ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20.md"
    report = json.loads(json_path.read_text(encoding="utf-8"))
    flags = report.get("flag", {})
    workflow = (ROOT / LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW).read_text(
        encoding="utf-8"
    )
    checks = {
        "diagnostic_integrity_exact": (
            report.get("status")
            == "CORRECTED_SO10_NONYUKAWA_GAUGE_POLYNOMIAL__FULL_G7_OPEN"
            and report.get("n_checks") == 11
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and report.get("content", {}).get("casimirs", {}).get("16")
            == 45.0 / 8.0
        ),
        "diagnostic_scope_fail_closed": (
            flags.get("sarah_validated_210_betas") is False
            and flags.get("live_sarah_or_pyrate_executable_run") is False
            and flags.get("two_loop_so10_gauge_complete_for_content") is False
            and flags.get("two_loop_so10_nonyukawa_gauge_polynomial_complete")
            is True
            and flags.get("two_loop_quartic_betas_complete") is False
            and flags.get("exact_unique_proton_lifetime") is False
            and flags.get("whole_model_excluded") is False
            and flags.get("pyrate_sarah_mv_formulas_ingested") is True
            and "remain OPEN" in report.get("verdict", "")
            and "full SARAH/PyR@TE scalar sector"
            in " ".join(report.get("next_exact_calculation", []))
        ),
        "generated_reports_are_exact_crlf": all(
            payload.count(b"\n") == payload.count(b"\r\n")
            and b"\r\n" in payload
            for payload in (json_path.read_bytes(), md_path.read_bytes())
        ),
        "active_deterministic_workflow_exact": (
            "pull_request:" in workflow
            and "push:" in workflow
            and "workflow_dispatch:" in workflow
            and "sarah_pyrate_so10_210_betas_v20.py" in workflow
            and "test_sarah_pyrate_so10_210_betas_v20.py" in workflow
            and "--check" not in workflow
            and "C2" not in workflow
            and "45.0/8.0" in workflow
            and "not r['flag']['sarah_validated_210_betas']" in workflow
            and "not r['flag']['live_sarah_or_pyrate_executable_run']" in workflow
            and all(
                f'{name}: "1"' in workflow
                for name in (
                    "OPENBLAS_NUM_THREADS",
                    "OMP_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS",
                )
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the legacy SO(10)+210 beta diagnostic bundle drifted: {failed}"
        )
    return {
        "raw_report_count": len(LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS),
        "diagnostic_checks_pass": True,
        "live_SARAH_or_PyRATE_execution_attested": False,
        "full_two_loop_gauge_content_closed": False,
        "quartic_dimensionful_EFT_betas_closed": False,
        "physical_thresholds_and_pole_masses_closed": False,
        "unique_physical_mathematical_release_G7_closed": False,
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_renormalizable_g1_component_tensor_bundle() -> dict[str, Any]:
    if len(RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS) != 4:
        raise ArithmeticError(
            "the renormalizable G1 component-tensor raw bundle must contain exactly 4 files"
        )
    source_name = "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
    report = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
        ).read_text(encoding="utf-8")
    )
    counts = report.get("counts", {})
    closure = report.get("closure", {})
    classification = report.get("classification", {})
    integration = report.get("integration", {})
    checks = {
        "source_and_report_core_exact": (
            _source_string_constant(source_name, "EXPECTED_CORE_SHA256")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
            and report.get("core_sha256")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        ),
        "status_and_contract_exact": (
            report.get("status")
            == "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_RING_CLOSED"
            and report.get("overall_state") == "CLOSED_SUBPROBLEM"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "complete_28_44_51_tensor_ring_exact": (
            counts
            == {
                "multidegrees": 34,
                "Hermitian_conjugacy_orbits": 28,
                "invariant_directions": 44,
                "self_conjugate_directions": 37,
                "complex_paired_directions": 7,
                "real_parameters": 51,
                "tensor_families": 18,
                "real_field_dimension": 486,
            }
            and len(report.get("direction_ids", ())) == 44
            and len(set(report.get("direction_ids", ()))) == 44
            and len(report.get("parameter_ids", ())) == 51
            and len(set(report.get("parameter_ids", ()))) == 51
            and len(report.get("family_ids", ())) == 18
            and len(set(report.get("family_ids", ()))) == 18
        ),
        "exact_family_certificates_and_source_binding_complete": (
            len(report.get("certificate_reports", {})) == 14
            and all(
                row.get("n_failed") == 0
                for row in report.get("certificate_reports", {}).values()
            )
            and len(report.get("source_sha256", {})) == 18
            and report.get("source_hash_convention")
            == "text bytes canonicalized to LF before SHA-256"
            and len(report.get("checks", {})) == 21
            and all(value is True for value in report.get("checks", {}).values())
        ),
        "mathematical_G1_ring_closed_exact": (
            closure.get("declared_symmetry_charge_multidegrees_degree_le_4_closed")
            is True
            and closure.get("so10_singlet_multiplicities_degree_le_4_closed")
            is True
            and closure.get("gauged_u1x_44_direction_subcensus_closed") is True
            and closure.get("explicit_component_tensor_subset_integration_closed")
            is True
            and closure.get("normalized_component_tensor_basis_all_44_directions_closed")
            is True
            and closure.get("full_renormalizable_G1_mathematical_ring_closed")
            is True
            and closure.get("external_model_execution_contract_closed") is False
        ),
        "central_integration_completed_exact": (
            integration
            == {
                "consumed_by_central_G1_G8_ledger": True,
                "consumed_by_execution_roadmap": True,
                "consumed_by_validation_matrix": True,
                "release_orchestrators_execute_read_only": True,
            }
        ),
        "authoritative_and_release_claims_remain_fail_closed": (
            classification.get("scoped_mathematical_G1_closed") is True
            and classification.get("authoritative_G1_promoted_closed") is False
            and classification.get("release_G1_verified") is False
            and classification.get("renormalizable_model_mutated") is False
            and classification.get("new_physics_required_for_G1") is False
            and report.get("release_blockers")
            == ["AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the frozen renormalizable G1 component-tensor logical bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS),
        "checks": checks,
        "all_checks_pass": True,
    }


def _require_renormalizable_g2_mathematical_bundle() -> dict[str, Any]:
    if len(RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS) != 4:
        raise ArithmeticError(
            "the renormalizable G2 mathematical raw bundle must contain exactly 4 files"
        )
    source_name = "exact_gauged_u1x_g2_mathematical_closure_v20.py"
    report = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
        ).read_text(encoding="utf-8")
    )
    counts = report.get("counts", {})
    coverage = report.get("derivative_coverage", {})
    stationarity = report.get("stationarity", {})
    closure = report.get("closure", {})
    classification = report.get("classification", {})
    integration = report.get("integration", {})
    checks = {
        "source_and_report_core_exact": (
            _source_string_constant(source_name, "EXPECTED_CORE_SHA256")
            == RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
            and report.get("core_sha256")
            == RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
        ),
        "status_contract_and_upstream_G1_exact": (
            report.get("status")
            == "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSED_RELEASE_OPEN"
            and report.get("overall_state") == "CLOSED_SUBPROBLEM"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("upstream_cores", {}).get("terminal_mathematical_G1")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
            and report.get("n_checks") == 17
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(report.get("checks", {})) == 17
            and all(value is True for value in report.get("checks", {}).values())
        ),
        "complete_44_51_18_486_projected_potential_exact": (
            counts
            == {
                "Hessian_shape_per_parameter": [486, 486],
                "base_tensor_families": 18,
                "gradient_entries_per_parameter": 486,
                "invariant_directions": 44,
                "real_field_dimension": 486,
                "real_parameters": 51,
                "symmetric_Hessian_entries_per_parameter": 118341,
                "upstream_derivative_audit_checks": 49,
            }
            and len(report.get("upstream_derivative_check_surface", {})) == 49
            and all(
                value is True
                for value in report.get("upstream_derivative_check_surface", {}).values()
            )
            and len(report.get("derivative_owner_modules", ())) == 10
            and len(set(report.get("derivative_owner_modules", ()))) == 10
        ),
        "values_gradients_Hessians_and_Ward_identites_exact": (
            coverage
            == {
                "all_44_Hessians_closed": True,
                "all_44_gradients_closed": True,
                "all_44_values_closed": True,
                "all_51_real_parameter_derivatives_closed": True,
                "arbitrary_component_486_real_chart_closed": True,
            }
            and len(report.get("Ward_identity_coverage", {})) == 12
            and all(
                value is True
                for value in report.get("Ward_identity_coverage", {}).values()
            )
        ),
        "stationarity_rank_nullity_and_compiler_binding_exact": (
            stationarity.get("matrix_shape") == [486, 51]
            and stationarity.get("exact_rank") == 13
            and stationarity.get("exact_nullity") == 38
            and stationarity.get("exact_nonzero_13x13_minor") is True
            and stationarity.get("exact_rank_upper_factorization") is True
            and stationarity.get("compiler_minor_binding") is True
            and stationarity.get("stationary_Hessian_compiler_binding") is True
            and stationarity.get("stationary_witness_P24_trace") == 288
            and stationarity.get("float64_SVD_is_diagnostic_only") is True
        ),
        "mathematical_G2_closed_exact": (
            closure.get("terminal_mathematical_G1_prerequisite_closed") is True
            and closure.get("full_component_potential_G2_mathematically_closed")
            is True
            and closure.get("values_gradients_Hessians_and_Ward_identities_closed")
            is True
            and closure.get("exact_stationarity_rank_nullity_closed") is True
            and closure.get("external_model_execution_contract_closed") is False
        ),
        "central_integration_completed_exact": (
            integration
            == {
                "consumed_by_central_G1_G8_ledger": True,
                "consumed_by_execution_roadmap": True,
                "consumed_by_validation_matrix": True,
                "release_orchestrators_execute_read_only": True,
            }
            and report.get("integration_blockers") == []
        ),
        "authoritative_and_release_claims_remain_fail_closed": (
            classification.get("mathematical_renormalizable_G2_closed") is True
            and classification.get("authoritative_G2_promoted_closed") is False
            and classification.get("release_G2_verified") is False
            and classification.get("renormalizable_model_mutated") is False
            and classification.get("new_physics_required_for_G2") is False
            and classification.get("G3_closed_by_this_theorem") is False
            and report.get("release_blockers")
            == ["AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ArithmeticError(
            f"the frozen renormalizable G2 mathematical logical bundle drifted: {failed}"
        )
    return {
        "raw_file_count": len(RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS),
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
        len(READ_ONLY_FROZEN_REPORT_SOURCES) != 46
        or expected_read_only_commands != 138
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
    inventory_paths = set(RAW_INTEGRATION_PATHS) | set(PORTABLE_INTEGRATION_PATHS)
    checksum_inventory_paths = inventory_paths - {"SHA256SUMS"}
    inventory_missing = sorted(checksum_inventory_paths - set(entries))
    if inventory_missing:
        raise ArithmeticError(
            "release checksum lacks inventoried paths: "
            f"{inventory_missing}"
        )
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
    eft_g6_truth_bundle = _require_eft_g6_truth_bundle()
    eft_g7_truth_bundle = _require_eft_g7_truth_bundle()
    normalized_yukawa_cgc_truth_bundle = (
        _require_normalized_yukawa_cgc_truth_bundle()
    )
    physical_sm_vacuum_truth_bundle = _require_physical_sm_vacuum_truth_bundle()
    conditional_physical_sm_eft_hessian_spectrum_bundle = (
        _require_conditional_physical_sm_eft_hessian_spectrum_bundle()
    )
    physical_sm_heavy_vector_mass_bundle = (
        _require_physical_sm_heavy_vector_mass_bundle()
    )
    physical_sm_heavy_vector_msbar_matching_bundle = (
        _require_physical_sm_heavy_vector_msbar_matching_bundle()
    )
    physical_sm_vector_rxi_bundle = _require_physical_sm_vector_rxi_bundle()
    physical_sm_g6_g7_frontier_bundle = (
        _require_physical_sm_g6_g7_frontier_bundle()
    )
    physical_sm_g8_frontier_bundle = _require_physical_sm_g8_frontier_bundle()
    canonical_g1_g8_v21_bundle = _require_canonical_g1_g8_v21_bundle()
    physical_sm_source_equality_frontier_bundle = (
        _require_physical_sm_source_equality_frontier_bundle()
    )
    physical_sm_five_amplitude_equality_bundle = (
        _require_physical_sm_five_amplitude_equality_bundle()
    )
    physical_sm_hard_projector_hessians_bundle = (
        _require_physical_sm_hard_projector_hessians_bundle()
    )
    physical_sm_last_six_hessians_bundle = (
        _require_physical_sm_last_six_hessians_bundle()
    )
    physical_sm_37_row_aggregate_bundle = (
        _require_physical_sm_37_row_aggregate_bundle()
    )
    physical_sm_local_equality_orbit_bundle = (
        _require_physical_sm_local_equality_orbit_bundle()
    )
    physical_sm_g4_g5_branch_mismatch_bundle = (
        _require_physical_sm_g4_g5_branch_mismatch_bundle()
    )
    exact_x_v3_fail_closed_bundle = _require_exact_x_v3_fail_closed_bundle()
    canonical_g1_dim6_bundle = _require_canonical_g1_dim6_bundle()
    canonical_g2_dim6_bundle = _require_canonical_g2_dim6_bundle()
    canonical_g3_global_vacuum_bundle = (
        _require_canonical_g3_global_vacuum_bundle()
    )
    legacy_so10_210_beta_diagnostic_bundle = (
        _require_legacy_so10_210_beta_diagnostic_bundle()
    )
    renormalizable_g1_component_tensor_bundle = (
        _require_renormalizable_g1_component_tensor_bundle()
    )
    renormalizable_g2_mathematical_bundle = (
        _require_renormalizable_g2_mathematical_bundle()
    )
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
            "legacy_EFT_G6_formal_spectrum_core_sha256": (
                LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256
            ),
            "G6_SM_provenance_core_sha256": G6_SM_PROVENANCE_CORE_SHA256,
            "EFT_G6_G7_parameterized_matching_core_sha256": (
                EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
            ),
            "EFT_G6_formal_gate_core_sha256": EFT_G6_FORMAL_GATE_CORE_SHA256,
            "authoritative_SO10_U1X_gauge_betas_core_sha256": (
                AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_CORE_SHA256
            ),
            "PyRATE3_SO10_U1X_gauge_beta_replay_core_sha256": (
                PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_CORE_SHA256
            ),
            "EFT_G7_formal_U1_89_restriction_core_sha256": (
                EFT_G7_FORMAL_RESTRICTION_CORE_SHA256
            ),
            "physical_G7_component_threshold_core_sha256": (
                PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256
            ),
            "normalized_SO10_Yukawa_CGC_core_sha256": (
                NORMALIZED_YUKAWA_CGCS_CORE_SHA256
            ),
            "physical_SM_vacuum_core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
            "conditional_physical_SM_EFT_Hessian_spectrum_core_sha256": (
                CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256
            ),
            "physical_SM_heavy_vector_masses_core_sha256": (
                PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256
            ),
            "physical_SM_heavy_vector_MSbar_matching_core_sha256": (
                PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256
            ),
            "physical_SM_vector_Rxi_core_sha256": (
                PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
            ),
            "physical_SM_G6_G7_frontier_core_sha256": (
                PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
            ),
            "physical_SM_G8_frontier_core_sha256": (
                PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
            ),
            "canonical_G1_G8_v21_definition_sha256": (
                CANONICAL_G1_G8_V21_DEFINITION_SHA256
            ),
            "canonical_G1_G8_v21_core_sha256": (
                CANONICAL_G1_G8_V21_CORE_SHA256
            ),
            "canonical_G1_dim6_frontier_core_sha256": (
                CANONICAL_G1_DIM6_FRONTIER_CORE_SHA256
            ),
            "canonical_G1_Susyno_channel_core_sha256": (
                CANONICAL_G1_SUSYNO_CHANNEL_CORE_SHA256
            ),
            "canonical_G1_complete_ring_core_sha256": (
                CANONICAL_G1_COMPLETE_RING_CORE_SHA256
            ),
            "canonical_G1_trusted_verifier_raw_sha256": (
                CANONICAL_G1_TRUSTED_VERIFIER_SHA256
            ),
            "canonical_G2_exact_basis_core_sha256": (
                CANONICAL_G2_EXACT_BASIS_CORE_SHA256
            ),
            "canonical_G2_full_projection_core_sha256": (
                CANONICAL_G2_FULL_PROJECTION_CORE_SHA256
            ),
            "canonical_G2_trusted_verifier_raw_sha256": (
                CANONICAL_G2_TRUSTED_VERIFIER_SHA256
            ),
            "canonical_G3_global_vacuum_core_sha256": (
                CANONICAL_G3_GLOBAL_VACUUM_CORE_SHA256
            ),
            "canonical_G3_trusted_verifier_raw_sha256": (
                CANONICAL_G3_TRUSTED_VERIFIER_SHA256
            ),
            "physical_SM_source_equality_frontier_core_sha256": (
                PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256
            ),
            "physical_SM_five_amplitude_equality_core_sha256": (
                PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            ),
            "physical_SM_hard_projector_Hessians_core_sha256": (
                PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
            ),
            "physical_SM_last_six_Hessians_core_sha256": (
                PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
            ),
            "physical_SM_37_row_aggregate_core_sha256": (
                PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
            ),
            "physical_SM_local_equality_orbit_core_sha256": (
                PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
            ),
            "physical_SM_G4_G5_branch_mismatch_core_sha256": (
                PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
            ),
            "exact_X_v3_trusted_SARAH_tree_core_sha256": (
                EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
            ),
            "legacy_SO10_210_beta_diagnostic_source_raw_sha256": (
                LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256
            ),
            "legacy_SO10_210_beta_diagnostic_test_raw_sha256": (
                LEGACY_SO10_210_BETA_DIAGNOSTIC_TEST_RAW_SHA256
            ),
            "renormalizable_G1_component_tensor_core_sha256": (
                RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
            ),
            "renormalizable_G2_mathematical_core_sha256": (
                RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
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
        "EFT_G6_truth_bundle": eft_g6_truth_bundle,
        "EFT_G7_truth_bundle": eft_g7_truth_bundle,
        "normalized_SO10_Yukawa_CGC_truth_bundle": (
            normalized_yukawa_cgc_truth_bundle
        ),
        "physical_SM_vacuum_truth_bundle": physical_sm_vacuum_truth_bundle,
        "conditional_physical_SM_EFT_Hessian_spectrum_bundle": (
            conditional_physical_sm_eft_hessian_spectrum_bundle
        ),
        "physical_SM_heavy_vector_mass_bundle": (
            physical_sm_heavy_vector_mass_bundle
        ),
        "physical_SM_heavy_vector_MSbar_matching_bundle": (
            physical_sm_heavy_vector_msbar_matching_bundle
        ),
        "physical_SM_vector_Rxi_bundle": physical_sm_vector_rxi_bundle,
        "physical_SM_G6_G7_frontier_bundle": (
            physical_sm_g6_g7_frontier_bundle
        ),
        "physical_SM_G8_frontier_bundle": physical_sm_g8_frontier_bundle,
        "canonical_G1_G8_v21_bundle": canonical_g1_g8_v21_bundle,
        "canonical_G1_dim6_bundle": canonical_g1_dim6_bundle,
        "canonical_G2_dim6_bundle": canonical_g2_dim6_bundle,
        "canonical_G3_global_vacuum_bundle": (
            canonical_g3_global_vacuum_bundle
        ),
        "physical_SM_source_equality_frontier_bundle": (
            physical_sm_source_equality_frontier_bundle
        ),
        "physical_SM_five_amplitude_equality_bundle": (
            physical_sm_five_amplitude_equality_bundle
        ),
        "physical_SM_hard_projector_Hessians_bundle": (
            physical_sm_hard_projector_hessians_bundle
        ),
        "physical_SM_last_six_Hessians_bundle": (
            physical_sm_last_six_hessians_bundle
        ),
        "physical_SM_37_row_aggregate_bundle": (
            physical_sm_37_row_aggregate_bundle
        ),
        "physical_SM_local_equality_orbit_bundle": (
            physical_sm_local_equality_orbit_bundle
        ),
        "physical_SM_G4_G5_branch_mismatch_bundle": (
            physical_sm_g4_g5_branch_mismatch_bundle
        ),
        "exact_X_v3_fail_closed_bundle": exact_x_v3_fail_closed_bundle,
        "legacy_SO10_210_beta_diagnostic_bundle": (
            legacy_so10_210_beta_diagnostic_bundle
        ),
        "renormalizable_G1_component_tensor_bundle": (
            renormalizable_g1_component_tensor_bundle
        ),
        "renormalizable_G2_mathematical_bundle": (
            renormalizable_g2_mathematical_bundle
        ),
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
            "legacy_EFT_G6_formal_spectrum_raw_sha256": dict(
                sorted(LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS.items())
            ),
            "G6_SM_provenance_raw_sha256": dict(
                sorted(G6_SM_PROVENANCE_RAW_PINS.items())
            ),
            "G6_SM_provenance_transitive_raw_sha256": dict(
                sorted(G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS.items())
            ),
            "EFT_G6_G7_parameterized_matching_raw_sha256": dict(
                sorted(EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS.items())
            ),
            "EFT_G6_formal_gate_raw_sha256": dict(
                sorted(EFT_G6_FORMAL_GATE_RAW_PINS.items())
            ),
            "authoritative_SO10_U1X_gauge_betas_raw_sha256": dict(
                sorted(AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS.items())
            ),
            "PyRATE3_SO10_U1X_gauge_beta_replay_raw_sha256": dict(
                sorted(PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS.items())
            ),
            "EFT_G7_formal_U1_89_restriction_raw_sha256": dict(
                sorted(EFT_G7_FORMAL_RESTRICTION_RAW_PINS.items())
            ),
            "physical_G7_component_threshold_raw_sha256": dict(
                sorted(PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS.items())
            ),
            "normalized_SO10_Yukawa_CGC_raw_sha256": dict(
                sorted(NORMALIZED_YUKAWA_CGCS_RAW_PINS.items())
            ),
            "normalized_SO10_Yukawa_CGC_transitive_portable_lf_sha256": dict(
                sorted(NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS.items())
            ),
            "physical_SM_vacuum_raw_sha256": dict(
                sorted(PHYSICAL_SM_VACUUM_RAW_PINS.items())
            ),
            "physical_SM_vacuum_transitive_raw_sha256": dict(
                sorted(PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS.items())
            ),
            "conditional_physical_SM_EFT_Hessian_spectrum_raw_sha256": dict(
                sorted(
                    CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS.items()
                )
            ),
            "physical_SM_heavy_vector_masses_raw_sha256": dict(
                sorted(PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS.items())
            ),
            "physical_SM_heavy_vector_MSbar_matching_raw_sha256": dict(
                sorted(
                    PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS.items()
                )
            ),
            "physical_SM_vector_Rxi_raw_sha256": dict(
                sorted(PHYSICAL_SM_VECTOR_RXI_RAW_PINS.items())
            ),
            "physical_SM_G6_G7_frontier_raw_sha256": dict(
                sorted(PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS.items())
            ),
            "physical_SM_G8_frontier_raw_sha256": dict(
                sorted(PHYSICAL_SM_G8_FRONTIER_RAW_PINS.items())
            ),
            "canonical_G1_G8_v21_portable_lf_sha256": dict(
                sorted(CANONICAL_G1_G8_V21_PORTABLE_PINS.items())
            ),
            "canonical_G1_dim6_portable_lf_sha256": dict(
                sorted(CANONICAL_G1_DIM6_PORTABLE_PINS.items())
            ),
            "canonical_G2_dim6_portable_lf_sha256": dict(
                sorted(CANONICAL_G2_DIM6_PORTABLE_PINS.items())
            ),
            "canonical_G3_global_vacuum_portable_lf_sha256": dict(
                sorted(CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS.items())
            ),
            "physical_SM_source_equality_frontier_raw_sha256": dict(
                sorted(PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS.items())
            ),
            "physical_SM_five_amplitude_equality_raw_sha256": dict(
                sorted(PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS.items())
            ),
            "physical_SM_five_amplitude_transitive_portable_lf_sha256": dict(
                sorted(PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS.items())
            ),
            "physical_SM_hard_projector_Hessians_raw_sha256": dict(
                sorted(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS.items())
            ),
            "physical_SM_hard_projector_transitive_portable_lf_sha256": dict(
                sorted(PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS.items())
            ),
            "physical_SM_last_six_Hessians_raw_sha256": dict(
                sorted(PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS.items())
            ),
            "physical_SM_last_six_transitive_portable_lf_sha256": dict(
                sorted(PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS.items())
            ),
            "physical_SM_37_row_aggregate_raw_sha256": dict(
                sorted(PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS.items())
            ),
            "physical_SM_37_row_aggregate_transitive_portable_lf_sha256": dict(
                sorted(PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS.items())
            ),
            "physical_SM_local_equality_orbit_portable_lf_sha256": dict(
                sorted(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS.items())
            ),
            "physical_SM_local_equality_orbit_transitive_portable_lf_sha256": dict(
                sorted(
                    PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS.items()
                )
            ),
            "physical_SM_G4_G5_branch_mismatch_raw_sha256": dict(
                sorted(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS.items())
            ),
            "physical_SM_G4_G5_branch_mismatch_transitive_raw_sha256": dict(
                sorted(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS.items())
            ),
            "exact_X_v3_raw_sha256": dict(sorted(EXACT_X_V3_RAW_PINS.items())),
            "exact_X_v3_portable_lf_sha256": dict(
                sorted(EXACT_X_V3_PORTABLE_PINS.items())
            ),
            "legacy_SO10_210_beta_diagnostic_raw_sha256": dict(
                sorted(LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS.items())
            ),
            "renormalizable_G1_component_tensor_raw_sha256": dict(
                sorted(RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS.items())
            ),
            "renormalizable_G2_mathematical_raw_sha256": dict(
                sorted(RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS.items())
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
            "renormalizable_mathematical_G1_closed": True,
            "authoritative_renormalizable_G1_closed": True,
            "canonical_dimension6_G1_closed": True,
            "release_G1_verified": True,
            "exact_X_v3_static_native_contract_closed": True,
            "exact_X_v3_trusted_SARAH_tree_manifest_closed": True,
            "exact_X_v3_external_execution_attestation_present": True,
            "exact_X_v3_external_execution_attestation_valid": True,
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
            "legacy_G6_spectrum_embedded_U1em_label_valid": False,
            "formal_SU3_x_U1_89_tree_mass_factorization_closed": True,
            "mathematical_physical_G6_closed": False,
            "EFT_dimension6_tree_level_mathematical_G6_closed": False,
            "EFT_release_G6_verified": False,
            "formal_U1_89_abstract_restriction_noninjectivity_proved": True,
            "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
            "historical_electroweak_lift_interpretation_valid": False,
            "exact_nonyukawa_two_loop_gauge_polynomial_closed": True,
            "legacy_SO10_210_beta_diagnostic_integrity_closed": True,
            "legacy_SO10_210_live_SARAH_or_PyRATE_execution_attested": False,
            "legacy_SO10_210_full_physical_mathematical_release_G7_closed": False,
            "independent_gauge_only_PyRATE3_replay_closed": True,
            "physical_PS_SM_matter_branching_closed": True,
            "parameterized_one_loop_matter_threshold_kernel_closed": True,
            "normalized_SO10_representation_Yukawa_CGCs_closed": True,
            "flavor_tensor_values_and_textures_closed": False,
            "full_one_two_loop_Yukawa_betas_closed": False,
            "physical_SM_target_and_standard_stabilizer_constructed": True,
            "old_selected_EFT_U1em_label_superseded_by_U1_89": True,
            "physical_SM_G3_closed": False,
            "physical_SM_G4_closed": False,
            "physical_SM_G5_closed": False,
            "physical_SM_radial_stationary_equality_classified_exactly": True,
            "physical_SM_five_amplitude_stationary_equality_classified_exactly": True,
            "physical_SM_five_amplitude_discrete_real_solution_count": 16,
            "physical_SM_five_amplitude_full_486_equality_classified": False,
            "physical_SM_five_amplitude_continuous_orbit_equivalence_classified": False,
            "physical_SM_five_amplitude_direct_source_algebra_Hessian_closed": False,
            "physical_SM_hard_projector_exact_source_Hessian_row_count": 10,
            "physical_SM_all_37_source_Hessians_available_in_hard_projector_bundle": False,
            "physical_SM_37_row_aggregate_stationarity_kernel_rank_PSD_closed": False,
            "physical_SM_last_six_source_Hessians_closed": True,
            "physical_SM_all_37_active_source_Hessians_available": True,
            "physical_SM_37_row_source_aggregate_value_minus_one_stationary": True,
            "physical_SM_37_row_source_aggregate_kernel_dimension": 38,
            "physical_SM_37_row_source_aggregate_rank": 448,
            "physical_SM_37_row_source_aggregate_PSD_strict_mod_symmetry": True,
            "physical_SM_local_stationary_Hessian_problem_complete": True,
            "physical_SM_full_486_local_stationary_orbit_classified": True,
            "physical_SM_full_486_local_stationary_equality_orbit_classified": True,
            "physical_SM_all_16_sign_variants_one_continuous_K_orbit": True,
            "physical_SM_target_orbit_strict_local_minimum_mod_K": True,
            "physical_SM_quantitative_local_orbit_radius_proved": False,
            "physical_SM_G4_G5_branch_mismatch_proved": True,
            "physical_SM_current_five_amplitude_target_is_canonical_EW_branch": False,
            "physical_SM_global_no_go_for_other_EW_branches": False,
            "physical_SM_direct_source_algebra_Hessian_closed": False,
            "physical_SM_complete_global_equality_orbit_closed": False,
            "conditional_reconstructed_physical_SM_tree_scalar_spectrum_closed": True,
            "source_bound_physical_SM_tree_scalar_spectrum_closed": False,
            "physical_SM_tree_vector_mass_matrix_parameterized_closed": True,
            "physical_SM_unbroken_group_vector_threshold_logs_parameterized_closed": True,
            "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed": True,
            "finite_MSbar_vector_constant_closed": True,
            "heavy_vector_Goldstone_double_count_guard_active": True,
            "absolute_physical_heavy_vector_masses_closed": False,
            "physical_scalar_pole_spectrum_closed": False,
            "physical_G6_closed": False,
            "physical_component_pole_mass_matrices_closed": False,
            "zero_background_arbitrary_positive_Rxi_vacuum_determinant_cancellation_closed": True,
            "all_37_broken_vector_directions_Rxi_cancelled": True,
            "background_covariant_general_field_Rxi_determinants_closed": False,
            "background_covariant_heat_kernel_replay_closed": False,
            "stationary_SM_symmetric_pre_EW_matching_closed": False,
            "complete_scalar_and_fermion_thresholds_closed": False,
            "full_Yukawa_scalar_dimensionful_EFT_flow_closed": False,
            "continuous_G6_G7_nonidentifiability_proved": True,
            "unique_absolute_tree_spectrum_identified": False,
            "unique_pole_spectrum_identified": False,
            "unique_threshold_vector_identified": False,
            "unique_full_RGE_trajectory_identified": False,
            "physical_G7_closed": False,
            "EFT_mathematical_G7_closed": False,
            "EFT_release_G7_verified": False,
            "authoritative_renormalizable_G7_closed": False,
            "positive_G7_certified": False,
            "negative_G7_no_go_certified": False,
            "canonical_G8_contract_audited": True,
            "canonical_G1_G8_v21_contract_frozen": True,
            "canonical_G1_G8_v21_closure_capable": True,
            "canonical_G1_G8_v21_current_closed_gate_count": 3,
            "canonical_G1_G8_v21_current_open_gate_count": 5,
            "canonical_G3_physical_EW_global_vacuum_closed": True,
            "canonical_G1_G8_v21_all_gates_closed": False,
            "canonical_G1_G8_v21_whole_model_validated": False,
            "legacy_bare_gate_numbers_authoritative": False,
            "continuous_absolute_scale_G8_nonidentifiability_proved": True,
            "flavor_and_interference_G8_nonidentifiability_audited": True,
            "exact_101_case_G8_scale_audit_closed": True,
            "repository_frozen_PDG_2025_single_channel_constraint_verified": True,
            "unique_proton_lifetime_or_distribution_identified": False,
            "all_G8_acceptance_criteria_pass": False,
            "physical_G8_closed": False,
            "release_G8_verified": False,
            "authoritative_G8_closed": False,
            "whole_model_excluded_by_conditional_G8_points": False,
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
                "canonical_G3_closed": report["canonical_G1_G8_v21_bundle"][
                    "canonical_G3_closed"
                ],
                "legacy_physical_SM_G3_closed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
