#!/usr/bin/env python3
"""Fail-closed release gate for the combined v17/v19/v20 package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import g1_g8_gate_ledger_v20 as gate_ledger
import corrected_rank1_endpoint_v21 as corrected_rank1
import authoritative_full_model_gate_v20 as authoritative_gate


ROOT = Path(__file__).resolve().parent
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256 = (
    "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON_RAW_SHA256 = (
    "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
)
RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256 = (
    "eb11744d0dbc9ceb883e8a6063177d8e3e370b1dcdc2c4e3eba97541b53d8fc4"
)
RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256 = (
    "5f56a55a7c9597918c530ad6c77252ed161a206ad0dffbf25651e32f4f590a8b"
)
RENORMALIZABLE_G2_MATHEMATICAL_JSON_RAW_SHA256 = (
    "de105a206685a236dcddc4cb70d98d756d87b9641e02150c41493897e01f7ff0"
)
EFT_G7_THRESHOLD_NONIDENTIFIABILITY_CORE_SHA256 = (
    "93a8ea1abeb3cec2521cb043057b29646bd9c368f8e8bcc7e2d819f42a7dc741"
)
PYRATE3_GAUGE_REPLAY_CORE_SHA256 = (
    "63f097be00c5da69982909b79b5ac9c64c1080efa142ae5d419820fb260cbccf"
)
PYRATE3_GAUGE_REPLAY_SOURCE_RAW_SHA256 = (
    "74b70c7d403bd5fc1cefc30ab1a58dd5c6e74c99672c81e9b2a2c59e34a1c42a"
)
PYRATE3_GAUGE_REPLAY_JSON_RAW_SHA256 = (
    "e17dcc1dc939c8475b6827f4c781f3f5fce6c728cf5aa6511287066087b01fd4"
)
PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256 = (
    "18191bc9db705ed9e8a89eff214ad967bac37830c91fede82c418d38ce0c949e"
)
PYRATE3_GAUGE_REPLAY_DATA_RAW_SHA256 = (
    "047632c3e81f8eb2dcc1cd922b8d3e34c300743693e18606ff8953e28ccd280b"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256 = (
    "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256 = (
    "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256 = (
    "bdceea8f8e10f566119793c0e0cfc31316bd9704aab89a1b70a9fdc880f7cd4a"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_JSON_RAW_SHA256 = (
    "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256 = (
    "23b78d68d4732da2160d7b3911aa3ac0c7e6f9bce59e58228d4a6c755b21d071"
)
NORMALIZED_YUKAWA_CGCS_CORE_SHA256 = (
    "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7"
)
NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256 = (
    "432faa3fdf5adebf25015f7f2fda7f040d89d86bce31f6c85b4cc56e37eb14df"
)
NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256 = (
    "450321d322634630c3a6713d16f08fbefdba71b7b2bc886f0d95dc4dcf093a02"
)
NORMALIZED_YUKAWA_CGCS_JSON_RAW_SHA256 = (
    "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b"
)
NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256 = (
    "5acbb5eb78451b8f37f1d8b990962a7ad4c39fe1974cb4720cf2131a85c14112"
)
PHYSICAL_SM_VACUUM_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)
PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256 = (
    "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c"
)
PHYSICAL_SM_VACUUM_TEST_RAW_SHA256 = (
    "3b688b8a2bd33a03e19edf4225568a3eaef96b4580f7d9ea23c38857dc069f5c"
)
PHYSICAL_SM_VACUUM_JSON_RAW_SHA256 = (
    "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315"
)
PHYSICAL_SM_VACUUM_MD_RAW_SHA256 = (
    "d312fb960e7a458fadf38977573315a6d0a5eee37437c49c149589abd36416c3"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256 = (
    "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_SOURCE_RAW_SHA256 = (
    "4d1c146f9ab9cd9679bdef7f5c145381c5d53871e62f79c1e59864a5aec981c9"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_TEST_RAW_SHA256 = (
    "80ea03cbc4c6079e937d0a133e40ef172e3ffa72f7b2aad36d587f0b5436033d"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_JSON_RAW_SHA256 = (
    "6a4354baac91881b796e70d86e529158fe8c51a0a2a9e1dc9ba876130c3510ef"
)
CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_MD_RAW_SHA256 = (
    "60e5907263e06f9340d364ecd01f495b1cd470482a409f4ec6a27d86bdd6508e"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256 = (
    "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_SOURCE_RAW_SHA256 = (
    "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_TEST_RAW_SHA256 = (
    "6f5bd8638cfdd593e722055f74c2de761865b4391720b1b4a11ae9089eb61b42"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_JSON_RAW_SHA256 = (
    "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0"
)
PHYSICAL_SM_HEAVY_VECTOR_MASSES_MD_RAW_SHA256 = (
    "47b598aed6af33a89ecc47598d5280258e0b5304a23a8873764c9c4778768fff"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256 = (
    "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_SOURCE_RAW_SHA256 = (
    "d6c69059b679342b0aff843044eef15e540f0c68836b41f432c878883aad3192"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_TEST_RAW_SHA256 = (
    "e3b9118379cb6bc83e63646c4147a056f5cadc3faed13bc9c25bf42882f83b46"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_JSON_RAW_SHA256 = (
    "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_MD_RAW_SHA256 = (
    "130ec2f078e429cc6b19c7d9013fb803d4ffad9069a24509120f6467f9e72afe"
)
PHYSICAL_SM_VECTOR_RXI_CORE_SHA256 = (
    "ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93"
)
PHYSICAL_SM_VECTOR_RXI_SOURCE_RAW_SHA256 = (
    "5a850a37ac97043a4857002bbe96ab963380462a6ec17f1c43eb9a7a371e6a44"
)
PHYSICAL_SM_VECTOR_RXI_TEST_RAW_SHA256 = (
    "97275dad209ecef945b95b5dc9ec97b79b6d319346b8f769af5a9f9ae28d1aa7"
)
PHYSICAL_SM_VECTOR_RXI_JSON_RAW_SHA256 = (
    "e1553d18c5acb9fd738dfc8c16277a634ae42bca2960296656eee57a78101221"
)
PHYSICAL_SM_VECTOR_RXI_MD_RAW_SHA256 = (
    "b549642e47656257c90b13361715c1602f202548ba4e01f068d26ffa163a4286"
)
PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256 = (
    "eedc4bf7c068318f7cf597beaed25ff2eb5893951872475ade02ea8a91386aae"
)
PHYSICAL_SM_G6_G7_FRONTIER_SOURCE_RAW_SHA256 = (
    "db811c803bfb008d800d79a422918548d72cc87081a966075789178d06fb5043"
)
PHYSICAL_SM_G6_G7_FRONTIER_TEST_RAW_SHA256 = (
    "525f96ecadc331b3cd1041c457cb40c71fbd59ce8a987a83f7fafe167caf5535"
)
PHYSICAL_SM_G6_G7_FRONTIER_JSON_RAW_SHA256 = (
    "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a"
)
PHYSICAL_SM_G6_G7_FRONTIER_MD_RAW_SHA256 = (
    "ffea781db860ee162b8a61252900c44315ae2b9afa24561e6395a1be4e16af3b"
)
PHYSICAL_SM_G8_FRONTIER_CORE_SHA256 = (
    "029dfd8b707825742c85b6d223a54ee964c76cf519496c5d5da28a7cad407fd5"
)
PHYSICAL_SM_G8_FRONTIER_SOURCE_RAW_SHA256 = (
    "d4c294c4ea42e16764de3c8763e5e5a843e37958d4cd1bb57e10024900f93ee4"
)
PHYSICAL_SM_G8_FRONTIER_TEST_RAW_SHA256 = (
    "6f2a5a249084517cf442e0e16856082b1a2b75e7e1e2cfcdda57fd3ef609d527"
)
PHYSICAL_SM_G8_FRONTIER_JSON_RAW_SHA256 = (
    "bb58ef10bef730cefa8da4cee342711e1033134a5e9468febed5cc0f8a93acac"
)
PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256 = (
    "b946701143bbbf68c1a528e1ac671e65066410808c49fdb906624cff25fc5c17"
)
PHYSICAL_SM_FIVE_AMPLITUDE_CORE_SHA256 = (
    "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"
)
PHYSICAL_SM_FIVE_AMPLITUDE_SOURCE_RAW_SHA256 = (
    "777b11664047574432405373b71bf30ed473fa735bdce56ef95be43dccc76972"
)
PHYSICAL_SM_FIVE_AMPLITUDE_TEST_RAW_SHA256 = (
    "23b5491460efa8bc09d4b4d978619df808f5c796baf07ae6a5aa271dd693049e"
)
PHYSICAL_SM_FIVE_AMPLITUDE_JSON_RAW_SHA256 = (
    "61bca8d55230b798b1d45ae4496c2b1b39490f73d0596e671478a388f72449ce"
)
PHYSICAL_SM_FIVE_AMPLITUDE_MD_RAW_SHA256 = (
    "5a22cb172ff26ac698ca19bb722590cf15368c30d37190a211e5f5f1eff214d6"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256 = (
    "5c464a3e6725a8ba993d672667d16ea5fb6105b3f8015febcc90c7ea68640d59"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE_RAW_SHA256 = (
    "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST_RAW_SHA256 = (
    "08deeb86a522ba64eee0152b3f68f8fff9bdd75dac13aca9d855fee3652ed76b"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON_RAW_SHA256 = (
    "b8a498926d1ba6a7f07f9c64b56443a14fba098514a8d5cb3e8358bbf7baabfa"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD_RAW_SHA256 = (
    "47b44edaa79546d294fe7d2a50ae53de764259422967356d74b79235bddc2159"
)
PHYSICAL_SM_EASY_21_HESSIANS_CORE_SHA256 = (
    "b0c44e534585ae0e078218f33069d1e86b1353278a841d206ba21111819324db"
)
PHYSICAL_SM_EASY_21_HESSIANS_SOURCE_RAW_SHA256 = (
    "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311"
)
PHYSICAL_SM_EASY_21_HESSIANS_TEST_RAW_SHA256 = (
    "13232e28f53a0bbfc3db4e793f056f5f51e1c4b233720f56a15c6a0496953cbe"
)
PHYSICAL_SM_EASY_21_HESSIANS_JSON_RAW_SHA256 = (
    "bea6bb1b519eb42a610b6a0c66a6b7178e4f1f912aa154035aacecc815089ae8"
)
PHYSICAL_SM_EASY_21_HESSIANS_MD_RAW_SHA256 = (
    "cd7d25ec2b918196ae3a820dc6c8bc84b374d1c94d126c0975a848a420d8b113"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256 = (
    "07666dc9ea513c579ed5f82d19f9b636b21926f552dab49b4b02af288762348b"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE_RAW_SHA256 = (
    "78d712d3573ec3377a331eb52dbf429452aa1c7ed82aeb7eeb0aa5900b3774ce"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_TEST_RAW_SHA256 = (
    "1565454ca40608367e275a2a3cb2fb1a6b3277418a1479720e313431b5d9379f"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_JSON_RAW_SHA256 = (
    "fe1a92c3bc8e809c41abb88a85f3cf0198c88f7a70482b3f26359d6df78907c5"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_MD_RAW_SHA256 = (
    "74117a1f5c8a8add31ff82d7034dda32061fb5349b1d8662453cfcc2b266590e"
)
PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256 = (
    "8c1aeffcd29a4f78c42014f92cf4bfa09823a6a2efbd660d512d6b014db99f43"
)
PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE_RAW_SHA256 = (
    "801b456743d9037d4478dcb3c94fef3d745ad312b58c3b262324aeded7567f5c"
)
PHYSICAL_SM_37_ROW_AGGREGATE_TEST_RAW_SHA256 = (
    "8af93e63ed0ffb06734d8cffe60c75a41811dbf5b765fc93e09fc2c3febc2f96"
)
PHYSICAL_SM_37_ROW_AGGREGATE_JSON_RAW_SHA256 = (
    "66bafa7e00ce543abea0e29b8be586cca8ecb1c5417204fc0ec75f6736c984b3"
)
PHYSICAL_SM_37_ROW_AGGREGATE_MD_RAW_SHA256 = (
    "d0ddb600e27b69ad1f45af832fc4381006ef2471dfcf4b028b155b7210bb2fcd"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256 = (
    "8ddf130f5212db6e918425b093d9b68278f22154f43fc5c1734812f8057768be"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE_RAW_SHA256 = (
    "5358c084cd46bdf154fd42505e51d28dc75c6817d392e9bbad5b0d47c55184c7"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST_RAW_SHA256 = (
    "100488ad2c0173134be41ef52e17c82cc9445fc481bf922d4c36a6b7fe0b8f12"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON_RAW_SHA256 = (
    "4a443274dbd6e5f3887161dde5bbdb8e7410d4c951e307b7105587f99d9001c0"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD_RAW_SHA256 = (
    "2284d1cd3666af797116d2d150963eae05be8be27420e85132f24e66de2a2ee7"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256 = (
    "1b91227393a4402a8433d7947c2b1ce954ebc69ff7fbcc4e8606c61afcfdfdbe"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE_RAW_SHA256 = (
    "cf87a140b031ba625e2f656646402d0eb68aea3d34a555dc391274a198573251"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST_RAW_SHA256 = (
    "4595149177660f51d7b17e5ef7425d55acfd748df38aad02911f22e96041b958"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON_RAW_SHA256 = (
    "a94429e7838141cfd7a0860faa93b0a8ee23e9b8e8985222546ce552c9debe06"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD_RAW_SHA256 = (
    "7cdde1e96c5a47da405ed3c8f89324b807a0032e087e36732d6b986e49cbba9e"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256 = (
    "5d6f01c0ed131dcbc2813fa93f0bd81987178f2dac051e67b6db538b5a55f13d"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_SOURCE_RAW_SHA256 = (
    "3ab97985eb2d178aa1d7b77d2c1e9e30f6134599456fce07e0a071856fc7557f"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_TEST_RAW_SHA256 = (
    "e9d5200cbecdb22cbda4479607430f936e03e16b7c4663283abbbece99c7b770"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_JSON_RAW_SHA256 = (
    "96d00f47eb5365dd9ff43ace871a04252aeb4b3a5d2543f03870091ff78760f2"
)
PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_MD_RAW_SHA256 = (
    "e2d7b84c06ba706991a4bb123df3894569f2ee14f330a1b64030ab7656fce9ed"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256 = (
    "3b318e32a2ceb43dc26191c32026609ca121d66f9235f1b76a00f0a5da007fa5"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_TEST_RAW_SHA256 = (
    "162b1aad99ba90d18f707feb4baf6a2c3d05d8e00af8a382ac6493aedc6159e0"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_JSON_RAW_SHA256 = (
    "f9eedea44ae98547f94e123fa99ab38450c2c1c57b5871df624a78d6104dbcd9"
)
LEGACY_SO10_210_BETA_DIAGNOSTIC_MD_RAW_SHA256 = (
    "3d6cc2869b56452e4a8bd6a3e30d5c932506b686db349f34b773166df35a4f44"
)
V17_ENGINE = ROOT / "so10_axion_v17_engine.py"
V19_ENGINE = ROOT / "so10_axion_v19_engine.py"
V20_ENGINE = ROOT / "so10_axion_v20_engine.py"
V17_VERDICT = ROOT / "so10_axion_v17_verdict.json"
V19_VERDICT = ROOT / "so10_axion_v19_verdict.json"
V20_VERDICT = ROOT / "so10_axion_v20_verdict.json"
TEX = ROOT / "axion_so10_theory_v20.tex"
PDF = ROOT / "axion_so10_theory_v20.pdf"
LOG = ROOT / "axion_so10_theory_v20.log"

# Files that complete the script/test/report bundles for the current exact-X
# G1--G5 release chain and its reproducibility gates.  Keep paths relative so
# the checksum manifest is portable across checkout locations and platforms.
FINAL_THEOREM_CORE_PATHS: tuple[str, ...] = (
    ".gitattributes",
    "test_global_flavour_fit_v20.py",
    "CANONICAL_G1_G8_GAUGED_U1X_V21.json",
    "CANONICAL_G1_G8_GAUGED_U1X_V21.md",
    "canonical_g1_g8_gauged_u1x_v21.py",
    "test_canonical_g1_g8_gauged_u1x_v21.py",
    "canonical_g1_scalar_ring_dim6_frontier_v21.py",
    "test_canonical_g1_scalar_ring_dim6_frontier_v21.py",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.md",
    "canonical_g1_susyno_channel_basis_v21.wls",
    "test_canonical_g1_susyno_channel_basis_v21.py",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json",
    "canonical_g1_complete_operator_ring_dim6_v21.py",
    "verify_canonical_g1_complete_operator_ring_dim6_v21.py",
    "test_canonical_g1_complete_operator_ring_dim6_v21.py",
    "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json",
    "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.md",
    "_g2_contraction_graphs.py",
    "_g2_metric_rank_probe.py",
    "canonical_g2_exact_contraction_basis_v21.py",
    "test_canonical_g2_exact_contraction_basis_v21.py",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json",
    "canonical_g2_full_component_projection_dim6_v21.py",
    "verify_canonical_g2_full_component_projection_dim6_v21.py",
    "test_canonical_g2_full_component_projection_dim6_v21.py",
    "test_verify_canonical_g2_full_component_projection_dim6_v21.py",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.md",
    "canonical_g3_physical_ew_global_vacuum_v21.py",
    "verify_canonical_g3_physical_ew_global_vacuum_v21.py",
    "test_canonical_g3_physical_ew_global_vacuum_v21.py",
    "test_verify_canonical_g3_physical_ew_global_vacuum_v21.py",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json",
    "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.md",
    "AUTHORITATIVE_FULL_MODEL_GATE_V20.md",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md",
    "EXACT_PHI_SELF_ZERO_GLOBAL_SEXTIC_SYZYGY.md",
    "EXACT_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION.md",
    "EXACT_PHI_ZERO_CUBIC_CAUCHY_BRIDGE.md",
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_EVALUATION_TABLE.json",
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_IDENTITY.md",
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_CHECKPOINT.json",
    "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_SOLUTION.json",
    "FROZEN_EXACT_SIGNED_KAEHLER_FULL126_STRONG_OPERATOR_SOURCE_V20.py",
    "FROZEN_PHI_SELF_ZERO_GLOBAL_SEXTIC_SYZYGY_SOURCE_V20.py",
    "FROZEN_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION_SOURCE_V20.py",
    "FROZEN_PHI_ZERO_CUBIC_CAUCHY_BRIDGE_SOURCE_V20.py",
    "FROZEN_PHI_ZERO_DEGREE8_CONDUCTOR_IDENTITY_SOURCE_V20.py",
    "FROZEN_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_SOURCE_V20.py",
    "FROZEN_SIGNED_KAEHLER_FULL126_PHYSICAL_SUBTRACTION_SOURCE_V20.py",
    "FROZEN_SIGNED_KAEHLER_P0_FULL126_KERNEL_RADIAL_STRICTNESS_SOURCE_V20.py",
    "exact_phi_zero_o10_degree8_invariant_split_v20.py",
    "reconstruct_exact_phi_zero_degree8_radical_v20.py",
    "reconstruct_exact_phi_zero_degree8_conductor_table_v20.py",
    "solve_exact_phi_zero_degree8_conductor_identity_v20.py",
    "exact_phi_zero_degree8_conductor_identity_v20.py",
    "exact_phi_zero_cubic_cauchy_bridge_v20.py",
    "exact_phi_self_zero_global_sextic_syzygy_v20.py",
    "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
    "test_exact_phi_zero_degree8_conductor_identity_v20.py",
    "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
    "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
    "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
    "EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER.md",
    "FROZEN_EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER_SOURCE_V20.py",
    "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
    "test_exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
    "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json",
    "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.md",
    "FROZEN_EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3_SOURCE_V20.py",
    "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
    "test_exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
    "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json",
    "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.md",
    "final_g3_eft_acceptance_gate_v20.py",
    "test_final_g3_eft_acceptance_gate_v20.py",
    "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
    "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.md",
    "final_g4_eft_mathematical_gate_v20.py",
    "test_final_g4_eft_mathematical_gate_v20.py",
    "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
    "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.md",
    "final_g5_eft_mathematical_gate_v20.py",
    "test_final_g5_eft_mathematical_gate_v20.py",
    "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
    "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.md",
    "exact_eft_physical_scalar_spectrum_v20.py",
    "test_exact_eft_physical_scalar_spectrum_v20.py",
    "exact_126bar_triplet_clebsch_v20.py",
    "exact_210_pati_salam_global_vacuum_v20.py",
    "live_g2_canonical_486_field_chart_v20.py",
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.md",
    "exact_g6_sm_provenance_feasibility_v20.py",
    "test_exact_g6_sm_provenance_feasibility_v20.py",
    "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json",
    "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.md",
    "exact_eft_g6_g7_parameterized_matching_v20.py",
    "test_exact_eft_g6_g7_parameterized_matching_v20.py",
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md",
    "final_g6_eft_mathematical_gate_v20.py",
    "test_final_g6_eft_mathematical_gate_v20.py",
    "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json",
    "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.md",
    "exact_authoritative_so10_u1x_gauge_betas_v20.py",
    "test_exact_authoritative_so10_u1x_gauge_betas_v20.py",
    "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json",
    "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.md",
    "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
    "test_pyrate3_so10_u1x_gauge_beta_replay_v20.py",
    "models/SO10U1XGaugeAuditV20.model",
    "data/PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json",
    "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json",
    "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.md",
    "exact_eft_g7_threshold_nonidentifiability_v20.py",
    "test_exact_eft_g7_threshold_nonidentifiability_v20.py",
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md",
    "exact_physical_g7_component_threshold_contract_v20.py",
    "test_exact_physical_g7_component_threshold_contract_v20.py",
    "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
    "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md",
    "exact_normalized_so10_yukawa_cgcs_v20.py",
    "test_exact_normalized_so10_yukawa_cgcs_v20.py",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md",
    "physical_sm_vacuum_local_feasibility_v20.py",
    "test_physical_sm_vacuum_local_feasibility_v20.py",
    "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json",
    "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md",
    "conditional_physical_sm_eft_hessian_spectrum_v20.py",
    "test_conditional_physical_sm_eft_hessian_spectrum_v20.py",
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md",
    "exact_physical_sm_heavy_vector_masses_v20.py",
    "test_exact_physical_sm_heavy_vector_masses_v20.py",
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md",
    "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
    "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py",
    "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json",
    "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md",
    "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
    "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json",
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md",
    "exact_physical_sm_g6_g7_closure_frontier_v20.py",
    "test_exact_physical_sm_g6_g7_closure_frontier_v20.py",
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json",
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md",
    "exact_physical_sm_g8_identifiability_frontier_v20.py",
    "test_exact_physical_sm_g8_identifiability_frontier_v20.py",
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json",
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md",
    "exact_physical_sm_five_amplitude_equality_v20.py",
    "test_exact_physical_sm_five_amplitude_equality_v20.py",
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json",
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md",
    "exact_physical_sm_hard_projector_hessians_v20.py",
    "test_exact_physical_sm_hard_projector_hessians_v20.py",
    "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json",
    "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.md",
    "exact_physical_sm_easy_21_hessians_v20.py",
    "test_exact_physical_sm_easy_21_hessians_v20.py",
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json",
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md",
    "exact_physical_sm_last_six_hessians_v20.py",
    "test_exact_physical_sm_last_six_hessians_v20.py",
    "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json",
    "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md",
    "exact_physical_sm_37_row_aggregate_v20.py",
    "test_exact_physical_sm_37_row_aggregate_v20.py",
    "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json",
    "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md",
    "exact_physical_sm_local_equality_orbit_v20.py",
    "test_exact_physical_sm_local_equality_orbit_v20.py",
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json",
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md",
    "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
    "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py",
    "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json",
    "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md",
    "physical_sm_source_algebra_equality_frontier_v20.py",
    "test_physical_sm_source_algebra_equality_frontier_v20.py",
    "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json",
    "SARAH_PYRATE_SO10_210_BETAS_V20.md",
    ".github/workflows/sarah-pyrate-so10-210-betas.yml",
    # Transitive source-bound physical-SM/Yukawa-CGC dependencies.  These
    # must remain in the release core so a dependency-only change cannot
    # evade the central checksum attestation.
    "direct_phi_h_sigmabar_tensor_v20.py",
    "exact_126bar_self_quartic_basis_v20.py",
    "exact_210_self_invariant_basis_v20.py",
    "exact_h10_self_quartic_family_v20.py",
    "exact_hsigma_hermitian_family_closure_v20.py",
    "exact_mixed_45_triplet_channel_v20.py",
    "exact_p_delta_second_stage_hessian_v20.py",
    "exact_phi2_126dag126_six_contractions_v20.py",
    "exact_phi2_hdagh_channel_family_v20.py",
    "exact_phisigma_126bar_minus_projectors_v20.py",
    "exact_phisigma_casimir_projectors_v20.py",
    "live_g1_tensor_closure_ledger_v20.py",
    "nonsusy_z17_pq_potential_filter_v20.py",
    "spin10_referee_audit.py",
    "live_g2_arbitrary_component_potential_values_v20.py",
    "live_g2_exact_final_mixed_quartic_derivatives_v20.py",
    "live_g2_exact_h10_self_quartic_derivatives_v20.py",
    "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
    "live_g2_exact_phi2_hdagh_derivatives_v20.py",
    "live_g2_exact_phi_self_quartic_derivatives_v20.py",
    "live_g2_exact_portal_family_derivatives_v20.py",
    "live_g2_exact_quadratic_family_derivatives_v20.py",
    "live_g2_exact_remaining_cubic_derivatives_v20.py",
    "live_g2_exact_sigma_self_quartic_derivatives_v20.py",
    "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py",
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
    "corrected_rank1_endpoint_v21.py",
    "freeze_corrected_rank1_endpoint_v21_integration.py",
    "test_corrected_rank1_endpoint_v21.py",
    "test_freeze_corrected_rank1_endpoint_v21_integration.py",
    ".github/workflows/current-main-full-reaudit.yml",
    ".github/workflows/g1-g8-execution-roadmap.yml",
    ".github/workflows/g1-g8-gate-ledger.yml",
    ".github/workflows/gauged-u1x-g3-stability.yml",
    ".github/workflows/latest-main-final-scalar-gate.yml",
    ".github/workflows/replicate-and-falsify.yml",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_SYSTEM_V21.npz",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json",
    "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json",
    "corrected_rank1_publication_v21/README.md",
    "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21.py",
    "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py",
    "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
    "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
    "corrected_rank1_publication_v21/heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py",
    "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
    "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py",
    "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_live_polynomial_v21.py",
    "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_ordered_spectral_overflow_v21.py",
    "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json",
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.md",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.md",
    "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json",
    "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.md",
    "G1_G8_EXECUTION_ROADMAP_V20.md",
    "G1_G8_GATE_LEDGER_V20.md",
    "GAUGED_U1X_SCALAR_CONTRACT_V20.md",
    "REPLICATE.md",
    "THEORY_CONFIRMATION_VERDICT.md",
    "THEORY_VALIDATION_MATRIX_V20.md",
    "ULTIMATE_THEORY_GATE_V20.md",
    "ULTIMATE_THEORY_GATE_V20_SCOPE.md",
    "VALIDATION_EXECUTION_V20.md",
    "VALIDATION_EXECUTION_V20_VERDICT.json",
    "g1_exact_declared_symmetry_character_census_v20.py",
    "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
    "exact_gauged_u1x_g2_mathematical_closure_v20.py",
    "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
    "prepare_validation_artifacts_v20.py",
    "replicate.py",
    "test_authoritative_full_model_gate_v20.py",
    "test_exact_x_symmetry_consistency_gate_v20.py",
    "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
    "test_g1_exact_declared_symmetry_character_census_v20.py",
    "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
    "test_exact_gauged_u1x_g2_mathematical_closure_v20.py",
    "test_g1_g8_execution_roadmap_v20.py",
    "test_g1_g8_gate_ledger_v20.py",
    "test_gauged_u1x_scalar_contract_v20.py",
    "test_prepare_validation_artifacts_v20.py",
    "test_theory_validation_matrix_v20.py",
    "test_ultimate_theory_gate_v20.py",
    "test_validate_release_v20.py",
)


def run(
    command: list[str], *, environment_overrides: dict[str, str] | None = None
) -> None:
    print("+", " ".join(command), flush=True)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785638400"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["SO10_PUBLISHED_API_ROOT"] = str(ROOT)
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        environment[name] = "1"
    if environment_overrides is not None:
        environment.update(environment_overrides)
    subprocess.run(command, cwd=ROOT, check=True, env=environment)


def run_pytest_with_private_basetemp(command: list[str]) -> None:
    """Run pytest without trusting or polluting the process-global temp root."""
    require("pytest" in command, "private pytest runner requires a pytest command")
    require("--basetemp" not in command, "pytest command already declares --basetemp")
    with tempfile.TemporaryDirectory(prefix=".so10-release-pytest-", dir=ROOT) as directory:
        run([*command, "--basetemp", directory])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rank1_su4_release_predicates(
    stabilizer_report: dict,
    intertwiners_report: dict,
    aligned_report: dict,
    quadratic_report: dict,
    census_report: dict,
    cubic_report: dict,
    quartic_report: dict,
    psd_target_report: dict,
    corrected_publication: dict | None = None,
) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
    """Return exact infrastructure plus the corrected endpoint theorem."""
    stabilizer_exact = gate_ledger._rank1_su4_stabilizer_infrastructure_exact(
        stabilizer_report
    )
    intertwiners_exact = gate_ledger._rank1_su4_phi210_intertwiners_exact(
        intertwiners_report,
        stabilizer_report,
    )
    aligned_exact = gate_ledger._rank1_su4_aligned_carriers_exact(
        aligned_report, intertwiners_report, stabilizer_report
    )
    quadratic_exact = gate_ledger._rank1_su4_phi210_quadratic_basis_exact(
        quadratic_report, stabilizer_report, intertwiners_report, aligned_report
    )
    census_exact = gate_ledger._rank1_su4_augmented_sos_census_exact(
        census_report, stabilizer_report, intertwiners_report, aligned_report,
        quadratic_report,
    )
    cubic_exact = gate_ledger._rank1_su4_augmented_sos_cubic_map_exact(
        cubic_report, stabilizer_report, intertwiners_report, aligned_report,
        quadratic_report, census_report,
    )
    quartic_exact = (
        census_exact
        and cubic_exact
        and gate_ledger._rank1_su4_augmented_sos_quartic_map_exact(
            quartic_report, census_report, cubic_report,
        )
    )
    legacy_routes_well_formed = (
        quartic_exact
        and gate_ledger._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
            psd_target_report, census_report, cubic_report, quartic_report,
        )
    )
    corrected_publication = (
        corrected_rank1.load_validated_publication()
        if corrected_publication is None
        else corrected_publication
    )
    corrected_endpoint_exact = bool(
        legacy_routes_well_formed
        and gate_ledger._rank1_su4_augmented_sos_psd_target_exact(
            psd_target_report, census_report, cubic_report, quartic_report,
        ) is False
        and corrected_rank1.corrected_fixed_endpoint_theorem_exact(
            corrected_publication
        )
    )
    return (
        stabilizer_exact, intertwiners_exact, aligned_exact, quadratic_exact,
        census_exact,
        cubic_exact,
        quartic_exact,
        corrected_endpoint_exact,
    )


PORTABLE_TEXT_CHECKSUM_SUFFIXES = frozenset(
    {".json", ".m", ".md", ".py", ".tex", ".txt", ".wls", ".yaml", ".yml"}
)
PORTABLE_TEXT_CHECKSUM_NAMES = frozenset({".gitattributes"})


def portable_checksum_payload(path: Path) -> bytes:
    """Return platform-stable bytes for release checksum attestation."""
    payload = path.read_bytes()
    is_text = (
        path.suffix.lower() in PORTABLE_TEXT_CHECKSUM_SUFFIXES
        or path.name in PORTABLE_TEXT_CHECKSUM_NAMES
    )
    if not is_text:
        return payload
    return payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def write_checksums(files: list[Path], *, root: Path | None = None) -> None:
    repository_root = (ROOT if root is None else root).resolve()
    entries: list[tuple[str, Path]] = []
    for path in files:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(repository_root).as_posix()
        except ValueError as exc:
            raise ValueError(
                f"checksum path is outside repository: {resolved}"
            ) from exc
        entries.append((relative, resolved))

    names = [name for name, _ in entries]
    require(len(names) == len(set(names)), "duplicate release-core checksum path")
    lines = []
    for relative, path in sorted(entries):
        digest = hashlib.sha256(portable_checksum_payload(path)).hexdigest()
        lines.append(f"{digest}  {relative}")
    (repository_root / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    run(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "-x",
            "corrected_rank1_publication_v21",
            str(ROOT),
        ]
    )

    run(
        [
            sys.executable,
            str(V17_ENGINE),
            "--trials",
            "100000",
            "--output",
            str(V17_VERDICT),
        ]
    )
    v17 = json.loads(V17_VERDICT.read_text())
    require(v17["n_checks_total"] == 65, "v17 check count changed")
    require(v17["n_checks_failed"] == 0 and v17["failures"] == [], "v17 engine failed")

    run([sys.executable, str(V19_ENGINE), "--output", str(V19_VERDICT)])
    v19 = json.loads(V19_VERDICT.read_text())
    require(v19["n_checks_total"] == 59, "v19 check count changed")
    require(v19["n_checks_failed"] == 0 and v19["failures"] == [], "v19 engine failed")
    require(
        v19["uv_completion"]["quality_overcatalogue"]["minimum"]["P"] == 13,
        "v19 historical P=13 regression changed",
    )

    run([sys.executable, str(V20_ENGINE), "--output", str(V20_VERDICT)])
    v20 = json.loads(V20_VERDICT.read_text())
    require(v20["n_checks_total"] == 42, "v20 check count changed")
    require(v20["n_checks_failed"] == 0 and v20["failures"] == [], "v20 engine failed")
    require(
        v20["completion"]["quality_overcatalogue"]["minimum"]["P"] == 8,
        "v20 P=8 threshold result changed",
    )
    require(
        v20["completion"]["minimality"]["minimum_number_of_pairs"] == 3,
        "v20 three-pair minimum changed",
    )
    require(
        v20["amplitudes"]["dominant_computed_unit_coefficient_term"]
        == "v20_U1X_direct_scalar_dimension21",
        "dominant v20 computed term changed",
    )
    require(
        v20["completion"]["running"]["continuous_from_spectator_corrected_alpha_GUT"][
            "conservative"
        ]["landau_pole_below_MPl"],
        "continuous Spin(10) soft-falsification flag missing",
    )

    run([sys.executable, "exact_x_symmetry_consistency_gate_v20.py"])
    run([sys.executable, "sarah_pyrate_210n_model_file_v20.py"])
    run([sys.executable, "gauged_u1x_scalar_contract_v20.py", "--write"])
    run([sys.executable, "g1_exact_declared_symmetry_character_census_v20.py", "--write"])
    run([sys.executable, "exact_gauged_u1x_g1_component_tensor_closure_v20.py"])
    run([sys.executable, "exact_gauged_u1x_stationarity_rank_certificate_v20.py"])
    run([sys.executable, "gauged_u1x_g2_derivative_audit_v20.py"])
    run([sys.executable, "exact_gauged_u1x_g2_mathematical_closure_v20.py"])
    run(
        [
            sys.executable,
            "exact_gauged_u1x_physical_quotient_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
            "--recompute-heavy",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
            "--recompute",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
            "--recompute",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_global_counterexample_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
        ]
    )
    corrected_dir = ROOT / "corrected_rank1_publication_v21"
    run(
        [
            sys.executable,
            "-B",
            str(
                corrected_dir
                / "freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py"
            ),
            "--check",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            str(
                corrected_dir
                / "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
            ),
            "--check",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            str(
                corrected_dir
                / "verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
            ),
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            str(
                corrected_dir
                / "verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py"
            ),
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "gauged_u1x_g3_sos_candidate_v20.py",
            "--recompute-heavy",
        ]
    )
    run([sys.executable, "gauged_u1x_g3_stability_v20.py"])
    run(
        [
            sys.executable,
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "--recompute-heavy",
        ]
    )
    run(
        [
            sys.executable,
            "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
        ]
    )
    run([sys.executable, "final_g3_eft_acceptance_gate_v20.py"])
    run([sys.executable, "final_g4_eft_mathematical_gate_v20.py"])
    run([sys.executable, "final_g5_eft_mathematical_gate_v20.py"])
    run([sys.executable, "exact_eft_physical_scalar_spectrum_v20.py"])
    run([sys.executable, "exact_g6_sm_provenance_feasibility_v20.py"])
    run([sys.executable, "physical_sm_vacuum_local_feasibility_v20.py"])
    run([sys.executable, "physical_sm_source_algebra_equality_frontier_v20.py"])
    run([sys.executable, "exact_physical_sm_five_amplitude_equality_v20.py"])
    run([sys.executable, "exact_physical_sm_hard_projector_hessians_v20.py"])
    run([sys.executable, "exact_physical_sm_easy_21_hessians_v20.py"])
    run([sys.executable, "exact_physical_sm_last_six_hessians_v20.py"])
    run([sys.executable, "exact_physical_sm_37_row_aggregate_v20.py"])
    run([sys.executable, "exact_physical_sm_local_equality_orbit_v20.py"])
    run([sys.executable, "exact_physical_sm_g4_g5_branch_mismatch_v20.py", "--check"])
    run([sys.executable, "conditional_physical_sm_eft_hessian_spectrum_v20.py"])
    run([sys.executable, "exact_eft_g6_g7_parameterized_matching_v20.py"])
    run([sys.executable, "final_g6_eft_mathematical_gate_v20.py"])
    run([sys.executable, "exact_authoritative_so10_u1x_gauge_betas_v20.py"])
    run([sys.executable, "exact_physical_sm_heavy_vector_masses_v20.py"])
    run([sys.executable, "exact_physical_sm_heavy_vector_msbar_matching_v20.py"])
    run([sys.executable, "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py"])
    run([sys.executable, "pyrate3_so10_u1x_gauge_beta_replay_v20.py"])
    run([sys.executable, "exact_normalized_so10_yukawa_cgcs_v20.py"])
    run([sys.executable, "exact_eft_g7_threshold_nonidentifiability_v20.py"])
    run([sys.executable, "exact_physical_g7_component_threshold_contract_v20.py"])
    run([sys.executable, "exact_physical_sm_g6_g7_closure_frontier_v20.py"])
    run([sys.executable, "exact_physical_sm_g8_identifiability_frontier_v20.py"])
    run([sys.executable, "sarah_pyrate_so10_210_betas_v20.py", "--check"])
    run([sys.executable, "g1_g8_gate_ledger_v20.py"])
    run([sys.executable, "final_g3_acceptance_gate_v20.py"])
    run([sys.executable, "g1_g8_execution_roadmap_v20.py"])
    run([sys.executable, "-B", "canonical_g1_scalar_ring_dim6_frontier_v21.py", "--check"])
    run([sys.executable, "-B", "canonical_g1_complete_operator_ring_dim6_v21.py", "--check"])
    run([sys.executable, "-B", "canonical_g2_exact_contraction_basis_v21.py", "--check"])
    run([sys.executable, "-B", "canonical_g2_full_component_projection_dim6_v21.py", "--check"])
    run([sys.executable, "-B", "canonical_g3_physical_ew_global_vacuum_v21.py", "--check"])
    run([sys.executable, "canonical_g1_g8_gauged_u1x_v21.py", "--check"])
    run([sys.executable, "authoritative_full_model_gate_v20.py"])
    run(
        [
            sys.executable,
            "theory_validation_matrix_v20.py",
            "--no-write",
        ]
    )
    run(
        [
            sys.executable,
            "theory_confirmation_verdict_v20.py",
            "--no-write",
        ]
    )
    run(
        [
            sys.executable,
            "ultimate_theory_gate_v20.py",
            "--no-write",
        ]
    )
    contract = json.loads(
        (ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json").read_text()
    )
    model_scaffold_audit = json.loads(
        (ROOT / "SARAH_PYRATE_MODEL_FILE_V20_VERDICT.json").read_text()
    )
    renormalizable_g1_component_tensor = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
        ).read_text()
    )
    gauged_g2 = json.loads(
        (ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json").read_text()
    )
    mathematical_g2 = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
        ).read_text()
    )
    exact_rank = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json"
        ).read_text()
    )
    exact_quotient = json.loads(
        (ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json").read_text()
    )
    exact_pd_rank = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
        ).read_text()
    )
    exact_a_square = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json"
        ).read_text()
    )
    exact_sos = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json"
        ).read_text()
    )
    exact_global_counterexample = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.json"
        ).read_text()
    )
    exact_kernel_bound = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json"
        ).read_text()
    )
    exact_replacement = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json"
        ).read_text()
    )
    exact_su5_pd = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json"
        ).read_text()
    )
    exact_su5_hsx = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
        ).read_text()
    )
    exact_su5_hsx_hessian = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
        ).read_text()
    )
    exact_su5_phi_orbit = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
        ).read_text()
    )
    exact_su5_phi_local = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
        ).read_text()
    )
    exact_su5_phi_su3 = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json"
        ).read_text()
    )
    exact_su5_equality = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
        ).read_text()
    )
    exact_su5_gap = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
        ).read_text()
    )
    exact_fixed_f_bound = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_bound = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_full_bound = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_rank1_su3_slice = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
        ).read_text()
    )
    exact_rank1_su4_stabilizer = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"
        ).read_text()
    )
    exact_rank1_su4_phi210_intertwiners = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_aligned_carriers = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_phi210_quadratic_basis = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_augmented_sos_census = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_augmented_sos_cubic_map = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
        ).read_text()
    )
    exact_rank1_su4_augmented_sos_quartic_map = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
        ).read_text()
    )
    exact_rank1_su4_augmented_sos_psd_target = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
        ).read_text()
    )
    exact_rank1_su4_corrected_publication = (
        corrected_rank1.load_validated_publication()
    )
    exact_alternative_sos = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
        ).read_text()
    )
    exact_eft_g3 = json.loads(
        (ROOT / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json").read_text()
    )
    final_g3 = json.loads((ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.json").read_text())
    final_g3_eft = json.loads(
        (ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json").read_text()
    )
    final_g4_eft = json.loads(
        (ROOT / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json").read_text()
    )
    final_g5_eft = json.loads(
        (ROOT / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json").read_text()
    )
    exact_eft_g6_spectrum = json.loads(
        (ROOT / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json").read_text()
    )
    g6_sm_provenance = json.loads(
        (ROOT / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json").read_text()
    )
    g6_g7_parameterized_matching = json.loads(
        (ROOT / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json").read_text()
    )
    final_g6_eft = json.loads(
        (ROOT / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json").read_text()
    )
    authoritative_gauge_betas = json.loads(
        (ROOT / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json").read_text()
    )
    pyrate3_gauge_replay = json.loads(
        (ROOT / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json").read_text()
    )
    exact_eft_g7_nonidentifiability = json.loads(
        (
            ROOT / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
        ).read_text()
    )
    physical_g7_component_threshold = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
        ).read_text()
    )
    normalized_yukawa_cgcs = json.loads(
        (ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json").read_text()
    )
    physical_sm_vacuum = json.loads(
        (ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json").read_text()
    )
    physical_sm_source_equality_frontier = json.loads(
        (
            ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json"
        ).read_text()
    )
    physical_sm_five_amplitude = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json").read_text()
    )
    physical_sm_hard_projector_hessians = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json").read_text()
    )
    physical_sm_easy_21_hessians = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json").read_text()
    )
    physical_sm_last_six_hessians = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json").read_text()
    )
    physical_sm_37_row_aggregate = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json").read_text()
    )
    physical_sm_local_equality_orbit = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json").read_text()
    )
    physical_sm_g4_g5_branch_mismatch = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json").read_text()
    )
    conditional_physical_sm_eft_hessian_spectrum = json.loads(
        (
            ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json"
        ).read_text()
    )
    physical_sm_heavy_vector_masses = json.loads(
        (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json").read_text()
    )
    physical_sm_heavy_vector_msbar_matching = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
        ).read_text()
    )
    physical_sm_vector_rxi = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json"
        ).read_text()
    )
    physical_sm_g6_g7_frontier = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json"
        ).read_text()
    )
    physical_sm_g8_frontier = json.loads(
        (
            ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
        ).read_text()
    )
    legacy_so10_210_beta_diagnostic = json.loads(
        (ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    g3_candidate = json.loads(
        (ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json").read_text()
    )
    gauged_g3 = json.loads(
        (ROOT / "GAUGED_U1X_G3_STABILITY_V20.json").read_text()
    )
    corrected_common_kernel = json.loads(
        (ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json").read_text()
    )
    matrix = json.loads(
        (ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json").read_text()
    )
    canonical_v21 = json.loads(
        (ROOT / "CANONICAL_G1_G8_GAUGED_U1X_V21.json").read_text()
    )
    canonical_g3_evidence = json.loads(
        (ROOT / "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json").read_text()
    )
    authoritative = json.loads(
        (ROOT / "AUTHORITATIVE_FULL_MODEL_GATE_V20.json").read_text()
    )
    ultimate = json.loads(
        (ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json").read_text()
    )
    canonical_integrity = authoritative_gate._canonical_evidence_complete(
        canonical_v21
    )
    canonical_rows = {
        row["qualified_gate_id"]: row for row in canonical_v21.get("gates", [])
    }
    canonical_g1_closed = bool(
        canonical_integrity
        and canonical_rows.get(
            authoritative_gate.canonical_gates.G1_ID, {}
        ).get("closed")
        is True
    )
    canonical_g2_closed = bool(
        canonical_integrity
        and canonical_rows.get(
            authoritative_gate.canonical_gates.G2_ID, {}
        ).get("closed")
        is True
    )
    canonical_g3_closed = bool(
        canonical_integrity
        and canonical_rows.get(
            authoritative_gate.canonical_gates.G3_ID, {}
        ).get("closed")
        is True
    )
    require(
        canonical_g3_closed
        and canonical_g3_evidence["closure_complete"] is True
        and canonical_g3_evidence["n_failed"] == 0
        and canonical_g3_evidence["qualified_gate_id"]
        == authoritative_gate.canonical_gates.G3_ID
        and canonical_g3_evidence["stationarity_and_Hessian"]["exact_total_value"]
        == "-1"
        and canonical_g3_evidence["stationarity_and_Hessian"][
            "exact_gradient_nonzero_entries"
        ]
        == 0
        and canonical_g3_evidence["stationarity_and_Hessian"]["exact_rank"]
        == 448
        and canonical_g3_evidence["stationarity_and_Hessian"]["exact_nullity"]
        == 38
        and canonical_g3_evidence["global_orbit"]["broken_gauge_directions"]
        == 37
        and canonical_g3_evidence["global_orbit"][
            "all_global_minima_one_continuous_symmetry_orbit"
        ]
        is True,
        "canonical G3 exact global-vacuum theorem failed",
    )
    require(
        canonical_g1_closed or contract["n_failed"] == 0,
        "authoritative X-contract diagnostic failed before canonical G1 closure",
    )
    require(
        canonical_g1_closed
        or (
            not contract["contract_consistent"]
            and contract["static_contract_consistent"] is True
            and contract["blocker"]
            == "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
        ),
        "exact-X external-execution blocker was misclassified",
    )
    root_scaffold = contract["executable_scaffold_contract"]
    root_external = contract["external_model_validation"]
    require(
        root_scaffold["model_syntax_class"]
        == "sarah_native"
        and root_scaffold["legacy_pseudo_sarah_grammar"] is False
        and root_scaffold["tool_native_sarah_syntax"] is True
        and root_scaffold["statically_executable_model_contract"] is True
        and root_scaffold["scalar_charges_match_manuscript"] is True
        and root_scaffold["fermion_catalogue_exact"] is True
        and root_scaffold["lagrangian"][
            "registered_in_GaugeES_LagrangianInput"
        ]
        is True,
        "native SARAH static contract failed",
    )
    require(
        canonical_g1_closed
        or (
        root_external["valid"] is False
        and root_external["present"] is False
        and root_external["checks"]["legacy_v2_schema_is_not_promoted"] is True
        and root_external["expected_trusted_sarah_release_manifest_path"]
        == "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"
        and root_external["expected_trusted_sarah_release_manifest_sha256"]
        == "c28f08d56a488050b96ce3491473f22fe1b673aad8ac3ac3d0e590dd60e70d91"
        and root_external["expected_trusted_sarah_release_manifest_size_bytes"]
        == 198868
        and root_external["trusted_sarah_release_manifest"]["valid"] is True
        and root_external["trusted_sarah_release_manifest"]["schema"]
        == "sarah-canonical-source-tree-v1"
        and root_external["trusted_sarah_release_manifest"]["release"]
        == {
            "archive": {
                "filename": "SARAH-4.15.3.tar.gz",
                "sha256": "6ee5c12d21a38f9de7f08b5b8db368b6653d7bfbcc8e45189016be87743729fb",
                "size_bytes": 2902331,
                "url": "https://sarah.hepforge.org/downloads/?f=SARAH-4.15.3.tar.gz",
            },
            "name": "SARAH",
            "version": "4.15.3",
        }
        and root_external["trusted_sarah_release_manifest"]["tree"]["file_count"]
        == 1056
        and root_external["trusted_sarah_release_manifest"]["tree"]["size_bytes"]
        == 20165588
        and root_external["trusted_sarah_release_manifest"]["tree"]["sha256"]
        == "de92b2de859efa7a0c4f5fdfb642d9f1ff8e1b071057bc8d4c295f6e2b6f8337"
        and root_external["checks"]["captured_process_log_is_hash_bound"]
        is False
        and contract["repository_external_input_manifest"]["valid"] is True
        and contract["repository_external_input_manifest"]["expected"]["schema"]
        == "so10-exact-x-input-manifest-v2"
        and contract["repository_external_input_manifest"]["expected"]["sha256"]
        == "da2526363b0b61a45060d656ae79ba4d8a092906b409c83460a5763a18f9765f"
        ),
        "external model evidence or repository input manifest was misclassified",
    )
    require(
        canonical_g1_closed
        or (
        model_scaffold_audit["n_failed"] == 0
        and model_scaffold_audit["overall_state"] == "BLOCKED"
        and model_scaffold_audit["status"]
        == "SARAH_NATIVE_STATIC_CONTRACT__EXTERNAL_VALIDATION_BLOCKED"
        and model_scaffold_audit["flag"]["sarah_model_tool_native"] is True
        and model_scaffold_audit["flag"][
            "sarah_static_contract_consistent"
        ]
        is True
        and model_scaffold_audit["flag"]["pyrate_model_tool_native"] is False
        and model_scaffold_audit["flag"]["charge_locks_encoded"] is True
        and model_scaffold_audit["flag"]["external_validation_v3_valid"] is False
        and model_scaffold_audit["flag"]["external_validation_v2_valid"] is False
        and model_scaffold_audit["flag"][
            "live_sarah_or_pyrate_executable_run"
        ]
        is False
        ),
        "native SARAH static/external execution boundary changed",
    )
    g1_counts = renormalizable_g1_component_tensor["counts"]
    g1_classification = renormalizable_g1_component_tensor["classification"]
    g1_integration = renormalizable_g1_component_tensor["integration"]
    require(
        renormalizable_g1_component_tensor["status"]
        == "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_RING_CLOSED"
        and renormalizable_g1_component_tensor["overall_state"]
        == "CLOSED_SUBPROBLEM"
        and renormalizable_g1_component_tensor["model_contract_id"]
        == MODEL_CONTRACT_ID
        and renormalizable_g1_component_tensor["core_sha256"]
        == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        and hashlib.sha256(
            (
                ROOT / "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
            ).read_bytes()
        ).hexdigest()
        == RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (
                ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
            ).read_bytes()
        ).hexdigest()
        == RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON_RAW_SHA256
        and renormalizable_g1_component_tensor["n_failed"] == 0
        and all(renormalizable_g1_component_tensor["checks"].values())
        and g1_counts["Hermitian_conjugacy_orbits"] == 28
        and g1_counts["invariant_directions"] == 44
        and g1_counts["real_parameters"] == 51
        and g1_counts["tensor_families"] == 18
        and g1_counts["real_field_dimension"] == 486
        and g1_classification["scoped_mathematical_G1_closed"] is True
        and (
            canonical_g1_closed
            or (
                g1_classification["authoritative_G1_promoted_closed"] is False
                and g1_classification["release_G1_verified"] is False
            )
        )
        and all(value is True for value in g1_integration.values())
        and (
            canonical_g1_closed
            or renormalizable_g1_component_tensor["release_blockers"]
            == ["AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"]
        ),
        "renormalizable mathematical G1 theorem failed or exceeded its release scope",
    )
    require(
        exact_rank["n_failed"] == 0
        and exact_rank["certified"] is True
        and exact_rank["rank"] == 13
        and exact_rank["nullity"] == 38
        and exact_rank["checks"]["exact_rank_upper_bound_13_certified"] is True
        and exact_rank["checks"]["exact_rank_lower_bound_13_certified"] is True,
        "standalone exact stationarity-rank certificate failed",
    )
    require(gauged_g2["n_failed"] == 0, "gauged U(1)_X G2 audit failed")
    require(
        gauged_g2["counts"]["invariant_directions"] == 44
        and gauged_g2["counts"]["real_parameters"] == 51
        and gauged_g2["counts"]["real_field_dimension"] == 486,
        "gauged U(1)_X G2 dimensions changed",
    )
    g2_counts = mathematical_g2["counts"]
    g2_closure = mathematical_g2["closure"]
    g2_classification = mathematical_g2["classification"]
    require(
        mathematical_g2["status"]
        == "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSED_RELEASE_OPEN"
        and mathematical_g2["overall_state"] == "CLOSED_SUBPROBLEM"
        and mathematical_g2["model_contract_id"] == MODEL_CONTRACT_ID
        and mathematical_g2["core_sha256"]
        == RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_gauged_u1x_g2_mathematical_closure_v20.py").read_bytes()
        ).hexdigest()
        == RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (
                ROOT / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
            ).read_bytes()
        ).hexdigest()
        == RENORMALIZABLE_G2_MATHEMATICAL_JSON_RAW_SHA256
        and mathematical_g2["n_failed"] == 0
        and all(mathematical_g2["checks"].values())
        and g2_counts["invariant_directions"] == 44
        and g2_counts["real_parameters"] == 51
        and g2_counts["base_tensor_families"] == 18
        and g2_counts["real_field_dimension"] == 486
        and mathematical_g2["stationarity"]["exact_rank"] == 13
        and mathematical_g2["stationarity"]["exact_nullity"] == 38
        and g2_closure["terminal_mathematical_G1_prerequisite_closed"] is True
        and g2_closure["full_component_potential_G2_mathematically_closed"]
        is True
        and (
            canonical_g2_closed
            or g2_closure["external_model_execution_contract_closed"] is False
        )
        and g2_classification["mathematical_renormalizable_G2_closed"] is True
        and (
            canonical_g2_closed
            or (
                g2_classification["authoritative_G2_promoted_closed"] is False
                and g2_classification["release_G2_verified"] is False
            )
        )
        and g2_classification["renormalizable_model_mutated"] is False
        and g2_classification["new_physics_required_for_G2"] is False
        and all(value is True for value in mathematical_g2["integration"].values())
        and mathematical_g2["integration_blockers"] == []
        and (
            canonical_g2_closed
            or mathematical_g2["release_blockers"]
            == ["AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"]
        ),
        "renormalizable mathematical G2 theorem failed or exceeded its release scope",
    )
    require(
        gauged_g2["stationary_Hessian_bridge"]["promoted_stationarity_matrix"][
            "rank"
        ]
        == 13
        and gauged_g2["stationary_Hessian_bridge"][
            "promoted_stationarity_matrix"
        ]["nullity"]
        == 38,
        "gauged U(1)_X G2 stationarity rank/nullity changed",
    )
    require(
        gauged_g2["flags"]["exact_Delta_R_projector_zero_certificate"] is True
        and gauged_g2["flags"][
            "exact_projector_zero_corrected_normalized_SVD_rank_13"
        ] is True
        and gauged_g2["flags"]["stationarity_rank_13_exactly_certified"] is True
        and gauged_g2["flags"]["stationarity_nullity_38_exactly_certified"] is True
        and gauged_g2["flags"][
            "stationarity_rank_upper_bound_13_exactly_certified"
        ]
        is True
        and gauged_g2["flags"][
            "exact_Sigma_conventions_bound_to_live_compiler_chart"
        ]
        is True
        and gauged_g2["flags"]["exact_Phi_int64_preflight_safety_certified"]
        is True
        and gauged_g2["flags"][
            "compiler_gradients_bound_to_exact_nonzero_13x13_minor"
        ]
        is True
        and gauged_g2["flags"][
            "exact_informed_13_row_constraint_representation_ready"
        ]
        is True
        and gauged_g2["flags"][
            "exact_P24_trace_288_bound_to_compiled_dense_Hessian"
        ]
        is True,
        "gauged U(1)_X G2 rank-evidence scope changed",
    )
    require(
        exact_quotient["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_quotient["certified"] is True
        and exact_quotient["exact_certificate"]["certified"] is True
        and exact_quotient["live_compiler_binding"]["compiler_binding_passes"]
        is True
        and exact_quotient["gauge_quotient_dimension_including_axion"] == 449
        and exact_quotient["massive_transverse_quotient_dimension"] == 448,
        "standalone exact physical-quotient certificate failed",
    )
    require(
        exact_a_square["n_failed"] == 0
        and exact_a_square["status"] == "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        and exact_a_square["certificate"]["unique_weights"]
        == ["40", "72", "28", "-8", "-12", "12"]
        and exact_a_square["certificate"]["identity_residuals"]
        == ["0", "0", "0", "0", "0", "0"]
        and exact_a_square["certificate"]["source_binding_exact"] is True
        and exact_a_square["certificate"]["proof_grade"] is True
        and exact_a_square["flags"][
            "A_square_recoupling_exactly_source_bound"
        ]
        is True
        and exact_a_square["flags"]["G3_closed"] is False,
        "exact A-square recoupling certificate failed or was over-promoted",
    )
    require(
        exact_sos["n_failed"] == 0
        and exact_sos["status"]
        == "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        and exact_sos["overall_state"] == "CLOSED_SUBPROBLEM"
        and exact_sos["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_sos["coefficient_binding"]["nonzero_parameter_count"] == 27
        and exact_sos["boundedness"]["source_binding_exact"] is True
        and exact_sos["stationarity"]["source_binding_exact"] is True
        and exact_sos["flags"][
            "complete_27_parameter_SOS_identity_exactly_source_bound"
        ]
        is True
        and exact_sos["flags"]["complete_potential_BFB_exactly_certified"]
        is True
        and exact_sos["flags"][
            "selected_vacuum_stationarity_exactly_certified"
        ]
        is True
        and exact_sos["flags"]["selected_vacuum_global_minimum_certified"]
        is False
        and exact_sos["flags"]["selected_vacuum_unique_modulo_symmetry"]
        is False
        and exact_sos["flags"]["full_Hessian_exactly_source_bound"] is False
        and exact_sos["flags"]["strict_local_minimum_certified"] is False
        and exact_sos["flags"]["G3_closed"] is False,
        "exact SOS/BFB/stationarity subcertificate failed or over-promoted",
    )
    pd_ranks = exact_pd_rank["direct_exact_ranks"]
    pd_extension = exact_pd_rank["exact_full_kernel_argument"]
    require(
        exact_pd_rank["n_failed"] == 0
        and exact_pd_rank["status"]
        == "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        and exact_pd_rank["overall_state"] == "OPEN"
        and pd_ranks["K"] == {"rank": 278, "nullity": 184, "PSD": True}
        and pd_ranks["H_Phi"] == {"rank": 186, "nullity": 276, "PSD": True}
        and pd_ranks["H_Phi_plus_K"]
        == {"rank": 429, "nullity": 33, "PSD": True}
        and pd_extension["exact_P_plus_Delta_gauge_orbit"]["exact_orbit_rank"]
        == 33
        and pd_extension["explicit_quotient_constraint_Jacobian"]["shape"]
        == [26, 24]
        and pd_extension["explicit_quotient_constraint_Jacobian"][
            "exact_rational_rank"
        ]
        == 19
        and pd_extension["exact_full_Hessian_rank"] == 448
        and pd_extension["remaining_kernel_dimension"] == 38
        and pd_extension["source_binding_exact"] is True
        and pd_extension["proof_grade"] is True
        and exact_pd_rank["direct_P_plus_Delta_certificate"][
            "source_binding_exact"
        ]
        is True
        and exact_pd_rank["direct_P_plus_Delta_certificate"]["proof_grade"]
        is True
        and exact_pd_rank["flags"]["conditional_exact_LDL_on_reconstructed_matrix"]
        is False
        and exact_pd_rank["flags"]["direct_exact_source_binding"] is True
        and exact_pd_rank["flags"]["proof_grade_P_plus_Delta_PSD"] is True
        and exact_pd_rank["flags"]["proof_grade_full_rank_448"] is True
        and exact_pd_rank["flags"][
            "strict_transverse_Hessian_positive_certified"
        ]
        is True
        and exact_pd_rank["flags"]["global_minimum_certified"] is False
        and exact_pd_rank["flags"]["global_uniqueness_certified"] is False
        and exact_pd_rank["flags"]["G3_closed"] is False,
        "direct exact P+Delta/full-transverse certificate failed or over-promoted",
    )
    require(
        exact_global_counterexample["n_failed"] == 0
        and exact_global_counterexample["flags"][
            "lower_energy_field_witness_exactly_certified"
        ]
        is True
        and exact_global_counterexample["flags"][
            "selected_vacuum_global_minimum_disproved"
        ]
        is True
        and exact_global_counterexample["flags"]["G3_closed"] is False
        and exact_global_counterexample["flags"]["whole_model_excluded"] is False,
        "exact global counterexample failed or was promoted to a model-wide no-go",
    )
    require(
        exact_kernel_bound["n_failed"] == 0
        and exact_kernel_bound["flags"][
            "fixed_P_strict_local_global_no_go_exact"
        ]
        is True
        and exact_kernel_bound["flags"]["fixed_P_branch_closed_negative"]
        is True
        and exact_kernel_bound["flags"]["G3_closed"] is False
        and exact_kernel_bound["flags"]["whole_model_excluded"] is False,
        "fixed-P exact gap-curvature no-go failed or exceeded its scope",
    )
    require(
        exact_replacement["n_failed"] == 0
        and exact_replacement["flags"][
            "replacement_full_stationarity_exact"
        ]
        is True
        and exact_replacement["flags"][
            "replacement_symmetry_orbit_rank_exact"
        ]
        is True
        and exact_replacement["flags"][
            "replacement_target_gauge_symmetry_correct"
        ]
        is False
        and exact_replacement["flags"][
            "replacement_strict_local_minimum_proof_grade"
        ]
        is False
        and exact_replacement["flags"]["G3_closed"] is False,
        "lower replacement orbit was misclassified",
    )
    su5_scope = exact_su5_pd["scope"]
    require(
        exact_su5_pd["n_failed"] == 0
        and exact_su5_pd["status"]
        == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
        and su5_scope["Phi_Sigma_global_minimum_exact"] is True
        and su5_scope["Phi_Sigma_stationarity_exact"] is True
        and su5_scope["SO10_to_SM_stabilizer_dimension_exact"] is True
        and su5_scope["Phi_Sigma_Hessian_rank_429_nullity_33_exact"] is True
        and su5_scope["Phi_Sigma_quotient_strictly_positive_exact"] is True
        and su5_scope["Phi_Sigma_equality_set_locally_one_orbit"] is True
        and su5_scope["full_486_field_stationarity"] is False
        and su5_scope["global_orbit_uniqueness"] is False
        and su5_scope["G3_closed"] is False,
        "SU(5)+Delta exact PD certificate failed or was over-promoted",
    )
    hsx_flags = exact_su5_hsx["flag"]
    hsx_orbit = exact_su5_hsx["chiral_H_candidate"]["exact_orbit"]
    hsx_live = exact_su5_hsx["live_full_gradient_and_quotient_Hessian"]
    require(
        exact_su5_hsx["n_failed"] == 0
        and hsx_flags["real_H_e6_extension_exactly_excluded"] is True
        and hsx_flags["chiral_H_exact_stationary_candidate_constructed"] is True
        and hsx_flags["full_quartic_BFB_certified"] is True
        and hsx_flags["full_global_minimum_certified"] is False
        and hsx_flags["G3_closed"] is False
        and [
            hsx_orbit["SO10_rank"],
            hsx_orbit["SO10_plus_U1X_rank"],
            hsx_orbit["SO10_plus_U1X_plus_PQ_rank"],
        ]
        == [36, 37, 38]
        and hsx_live["transverse_dimension"] == 448
        and hsx_live["proof_grade"] is False
        and hsx_live["negative_transverse_eigenvalues_below_minus_1e_minus_9"]
        == 0
        and hsx_live["zero_transverse_eigenvalues_at_1e_minus_9"] == 0,
        "SU(5)+Delta chiral-H frontier failed or numerical inertia was over-promoted",
    )
    exact_hessian_flags = exact_su5_hsx_hessian["flags"]
    exact_hessian_closed = (
        exact_su5_hsx_hessian["status"]
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and exact_su5_hsx_hessian["overall_state"]
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and all(
            exact_hessian_flags[name] is True
            for name in (
                "exact_rank_448",
                "exact_nullity_38",
                "exact_PSD",
                "strict_quotient",
                "proof_grade",
                "source_binding",
            )
        )
    )
    exact_hessian_open = (
        exact_su5_hsx_hessian["status"]
        == "EXACT_HESSIAN_CERTIFICATE_INCOMPLETE"
        and exact_su5_hsx_hessian["overall_state"] == "G3_EXACT_LOCAL_TEST_OPEN"
        and exact_hessian_flags["proof_grade"] is False
    )
    require(
        exact_su5_hsx_hessian["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_su5_hsx_hessian.get("n_failed", 0) == 0
        and exact_su5_hsx_hessian["G3_closed"] is False
        and (exact_hessian_closed or exact_hessian_open),
        "SU(5)+Delta exact Hessian audit failed or over-promoted G3",
    )
    phi_orbit_scope = exact_su5_phi_orbit["scope"]
    require(
        exact_su5_phi_orbit["n_failed"] == 0
        and exact_su5_phi_orbit["status"]
        == "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
        and exact_su5_phi_orbit["overall_state"]
        == "SHARP_COUNTEREXAMPLE_AND_REDUCTION"
        and exact_su5_phi_orbit["checks"][
            "literal_single_orbit_lemma_is_refuted"
        ]
        is True
        and exact_su5_phi_orbit["checks"][
            "corrected_signed_global_lemma_not_overclaimed"
        ]
        is True
        and phi_orbit_scope["literal_plus_orbit_only_statement_refuted"] is True
        and phi_orbit_scope["complete_SU4_invariant_slice_classified"] is True
        and phi_orbit_scope["all_arbitrary_real_four_forms_classified"] is False
        and phi_orbit_scope["corrected_signed_two_orbit_theorem_proved"] is False
        and phi_orbit_scope["PD_global_equality_orbit_classification_complete"]
        is False
        and phi_orbit_scope["G3_closed"] is False
        and phi_orbit_scope["whole_model_excluded"] is False
        and exact_su5_phi_orbit["corrected_global_lemma"]["proved"] is False,
        "literal Phi orbit refutation/signed-open audit was not reproduced",
    )
    phi_local_scope = exact_su5_phi_local["scope"]
    require(
        exact_su5_phi_local["n_failed"] == 0
        and exact_su5_phi_local["status"]
        == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
        and exact_su5_phi_local["overall_state"]
        == "LOCAL_COMPONENT_THEOREM_CLOSED"
        and phi_local_scope["plus_F_local_component_classified"] is True
        and phi_local_scope["minus_F_local_component_classified"] is True
        and phi_local_scope["signed_orbit_locally_isolated"] is True
        and phi_local_scope["explicit_neighborhood_radius_available"] is False
        and phi_local_scope["disconnected_distant_components_excluded"] is False
        and phi_local_scope["corrected_signed_global_orbit_theorem_proved"]
        is False
        and phi_local_scope["PD_global_equality_orbit_classification_complete"]
        is False
        and phi_local_scope["G3_closed"] is False
        and phi_local_scope["whole_model_excluded"] is False,
        "signed Phi local-component theorem failed or over-promoted globality",
    )
    phi_su3_scope = exact_su5_phi_su3["scope"]
    phi_su3_checks = exact_su5_phi_su3["checks"]
    require(
        exact_su5_phi_su3["n_failed"] == 0
        and exact_su5_phi_su3["status"]
        == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
        and exact_su5_phi_su3["overall_state"] == "SU3_FIXED_SLICE_CLOSED"
        and phi_su3_checks["displayed_space_is_complete_SU3_fixed_space"]
        is True
        and phi_su3_checks["restricted_projector_rowspace_reduced_exactly"]
        is True
        and phi_su3_checks[
            "eight_nondiagonal_directions_have_real_SOS_obstruction"
        ]
        is True
        and phi_su3_checks["complete_SU3_fixed_slice_is_signed_Kahler_orbit"]
        is True
        and phi_su3_scope[
            "complete_16_real_dimensional_SU3_fixed_space_classified"
        ]
        is True
        and phi_su3_scope[
            "all_nonzero_slice_solutions_are_signed_Kahler_squares"
        ]
        is True
        and phi_su3_scope["all_arbitrary_real_four_forms_classified"] is False
        and phi_su3_scope["disconnected_distant_components_excluded"] is False
        and phi_su3_scope["corrected_signed_global_orbit_theorem_proved"] is False
        and phi_su3_scope["G3_closed"] is False
        and phi_su3_scope["whole_model_excluded"] is False,
        "complete SU(3)-fixed Phi slice failed or over-promoted globality",
    )
    equality_scope = exact_su5_equality["scope"]
    equality_lemma = exact_su5_equality["remaining_global_lemma"]
    equality_global = exact_su5_equality["Phi_global_signed_zero_theorem"]
    require(
        exact_su5_equality["n_failed"] == 0
        and exact_su5_equality["status"]
        == "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
        and exact_su5_equality["overall_state"]
        == "GLOBAL_EQUALITY_ORBITS_CLOSED"
        and equality_scope["fixed_F_Sigma_global_equality_classified"] is True
        and equality_scope[
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        ]
        is True
        and equality_scope["global_equality_orbit_classification_complete"]
        is True
        and equality_scope["quantitative_beta_global_coercivity_proved"] is False
        and equality_lemma["proved"] is True
        and equality_lemma["source_bound_certificate_available"] is True
        and equality_lemma["quantitative_orbit_distance_bound_proved"] is False
        and equality_global["frozen_source_sha256"]
        == "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
        and equality_global["core_sha256"]
        == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
        and equality_global["external_theorem_dependency"]["kind"]
        == "published subgroup-classification theorem"
        and equality_lemma["numerical_search_is_not_a_substitute"] is True
        and equality_scope["G3_closed"] is False,
        "SU(5)+Delta equality classification was not fail-closed",
    )
    gap_flags = exact_su5_gap["flags"]
    require(
        exact_su5_gap["n_failed"] == 0
        and exact_su5_gap["status"]
        == "GLOBAL_GAP_REDUCED_TO_QUANTITATIVE_COERCIVITY"
        and gap_flags["lower_witness_found"] is False
        and gap_flags["conditional_small_positive_beta_route_exists"] is True
        and gap_flags["beta_1_over_20_global_minimum_certified"] is False
        and gap_flags["PD_equality_orbits_classified"] is True
        and gap_flags["global_equality_orbits_classified"] is False
        and gap_flags["G3_closed"] is False
        and exact_su5_gap["small_beta_global_reduction"]["hypotheses"][
            "exact_full_486_Hessian_kernel_equals_the_38_symmetry_tangents"
        ]
        is True
        and exact_su5_gap["final_acceptance_test"]["currently_passes"] is False,
        "chiral-H global-gap reduction failed or was over-promoted",
    )
    fixed_f_scope = exact_fixed_f_bound["scope"]
    fixed_f_checks = exact_fixed_f_bound["checks"]
    require(
        exact_fixed_f_bound["n_failed"] == 0
        and exact_fixed_f_bound["status"]
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and exact_fixed_f_bound["overall_state"]
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_checks["mixed_offkernel_gap_at_least_6_over_5_exact"] is True
        and fixed_f_checks["pure_hplus_current_error_bound_exact"] is True
        and fixed_f_checks["kernel_chirality_cross_zero_exact"] is True
        and fixed_f_checks["cross_block_bound_exact"] is True
        and fixed_f_checks["rational_inside_outside_patch_positive"] is True
        and fixed_f_checks["full_fixed_F_equality_orbit_exact"] is True
        and fixed_f_scope["Phi_fixed_to_F"] is True
        and fixed_f_scope["H_arbitrary"] is True
        and fixed_f_scope["Sigma_arbitrary"] is True
        and fixed_f_scope["beta_equals_1_over_20"] is True
        and fixed_f_scope["global_gap_nonnegative_on_full_fixed_F_stratum"]
        is True
        and fixed_f_scope["equality_is_selected_SU5_flag_orbit"] is True
        and fixed_f_scope["arbitrary_Phi_proved"] is False
        and fixed_f_scope["G3_closed"] is False,
        "fixed-F full off-kernel gap certificate failed or over-promoted G3",
    )
    max_negative_scope = exact_max_negative_bound["scope"]
    max_negative_checks = exact_max_negative_bound["checks"]
    require(
        exact_max_negative_bound["n_failed"] == 0
        and exact_max_negative_bound["status"]
        == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
        and exact_max_negative_bound["overall_state"]
        == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
        and exact_max_negative_bound["model_contract_id"]
        == MODEL_CONTRACT_ID
        and max_negative_checks["exact_rank_168_nullity_42"] is True
        and max_negative_checks["kernel_splits_35_plus_7_exactly"] is True
        and max_negative_checks["live_HSX_and_PD_coefficients_bound_exactly"]
        is True
        and max_negative_checks[
            "N_and_C00_C11_contraction_identities_computed_exactly"
        ]
        is True
        and max_negative_checks[
            "Phi_radial_plus_I54_lower_bound_1_over_141"
        ]
        is True
        and max_negative_checks["worst_radial_current_minimum_exact"] is True
        and max_negative_checks["strict_positive_stratum_margin_exact"] is True
        and max_negative_checks[
            "u_zero_and_v_zero_radial_boundaries_closed_exactly"
        ]
        is True
        and exact_max_negative_bound["exact_stratum_gap"]["strict_margin"]
        == "7859/140295000"
        and max_negative_scope[
            "strongest_all_zero_max_negative_route_excluded"
        ]
        is True
        and max_negative_scope[
            "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
        ]
        is True
        and max_negative_scope[
            "normalized_affine_stratum_requires_u_gt_0_v_gt_0"
        ]
        is True
        and max_negative_scope[
            "u_zero_and_v_zero_boundaries_closed_separately"
        ]
        is True
        and max_negative_scope["nonzero_residual_cancellations_excluded"] is False
        and max_negative_scope["arbitrary_Phi_global_gap_proved"] is False
        and max_negative_scope["G3_closed"] is False,
        "max-negative all-zero-residual certificate failed or over-promoted G3",
    )
    max_negative_full_scope = exact_max_negative_full_bound["scope"]
    max_negative_full_checks = exact_max_negative_full_bound["checks"]
    require(
        exact_max_negative_full_bound["n_failed"] == 0
        and exact_max_negative_full_bound["status"]
        == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
        and exact_max_negative_full_bound["overall_state"]
        == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
        and exact_max_negative_full_bound["model_contract_id"]
        == MODEL_CONTRACT_ID
        and max_negative_full_scope["Sigma_on_pure_Delta_orbit"] is True
        and max_negative_full_scope["Phi_arbitrary_real_210"] is True
        and max_negative_full_scope["nonzero_Phi_Sigma_residuals_covered"]
        is True
        and max_negative_full_scope["nonzero_chiral_Phi_H_residual_covered"]
        is True
        and max_negative_full_scope["u_v_all_nonnegative"] is True
        and max_negative_full_scope["restricted_gap_global_minimum"] == "1/5000"
        and max_negative_full_scope["arbitrary_Sigma_orientation_proved"]
        is False
        and max_negative_full_scope["G3_closed"] is False
        and all(max_negative_full_checks.values()),
        "max-negative full-residual pure-Delta certificate failed or over-promoted G3",
    )
    rank1_scope = exact_max_negative_rank1_su3_slice["scope"]
    rank1_checks = exact_max_negative_rank1_su3_slice["checks"]
    rank1_required_checks = (
        "rank1_live_residual_source_exact",
        "explicit_endpoint_current_and_self_projectors_exactly",
        "slice_basis_Gram_exact",
        "rank1_common_affine_kernel_rank160_nullity50_exact",
        "angular_projector_Gram_symmetric_exact",
        "angular_projector_int64_overflow_preflight_exact",
        "anchor_polynomial_reconstructed_exactly",
        "rational_SOS_polynomial_identity_exact",
        "rational_SOS_Gram_positive_definite_exact",
        "anchor_at_least_3_over_200_exact",
        "radial_patch_global_minimum_1_over_5000_exact",
        "attaining_slice_witness_evaluated_from_live_arrays_exact",
    )
    require(
        exact_max_negative_rank1_su3_slice["n_failed"] == 0
        and exact_max_negative_rank1_su3_slice["failed_checks"] == []
        and exact_max_negative_rank1_su3_slice["status"]
        == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
        and exact_max_negative_rank1_su3_slice["overall_state"]
        == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
        and exact_max_negative_rank1_su3_slice["model_contract_id"]
        == MODEL_CONTRACT_ID
        and rank1_scope["H_fixed_to_h_minus"] is True
        and rank1_scope[
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
        ]
        is True
        and rank1_scope["Phi_restricted_to_four_real_SU3_fixed_variables"]
        is True
        and rank1_scope["Phi_slice_real_dimension"] == 4
        and rank1_scope["full_SU3_fixed_space_real_dimension"] == 16
        and rank1_scope["full_SU3_fixed_space_proved"] is False
        and rank1_scope["u_v_arbitrary_nonnegative"] is True
        and rank1_scope["arbitrary_real_Phi"] is False
        and rank1_scope["arbitrary_max_negative_Sigma"] is False
        and rank1_scope["G3_closed"] is False
        and rank1_scope["whole_model_excluded"] is False
        and all(rank1_checks[name] is True for name in rank1_required_checks)
        and rank1_checks["arbitrary_rank1_Phi_proved"] is False
        and rank1_checks["arbitrary_Sigma35_proved"] is False
        and rank1_checks["G3_closed"] is False
        and exact_max_negative_rank1_su3_slice["SOS"][
            "strict_anchor_lower_bound"
        ]
        == "3/200"
        and exact_max_negative_rank1_su3_slice["radial_patch"][
            "restricted_global_minimum"
        ]
        == "1/5000",
        "rank-one SU(3) four-dimensional slice certificate failed or overclaimed G3",
    )
    (
        rank1_su4_stabilizer_exact,
        rank1_su4_phi210_intertwiners_exact,
        rank1_su4_aligned_carriers_exact,
        rank1_su4_phi210_quadratic_basis_exact,
        rank1_su4_augmented_sos_census_exact,
        rank1_su4_augmented_sos_cubic_map_exact,
        rank1_su4_augmented_sos_quartic_map_exact,
        rank1_su4_corrected_endpoint_exact,
    ) = rank1_su4_release_predicates(
        exact_rank1_su4_stabilizer,
        exact_rank1_su4_phi210_intertwiners,
        exact_rank1_su4_aligned_carriers,
        exact_rank1_su4_phi210_quadratic_basis,
        exact_rank1_su4_augmented_sos_census,
        exact_rank1_su4_augmented_sos_cubic_map,
        exact_rank1_su4_augmented_sos_quartic_map,
        exact_rank1_su4_augmented_sos_psd_target,
        exact_rank1_su4_corrected_publication,
    )
    require(
        rank1_su4_stabilizer_exact,
        "rank-one SU(4) stabilizer infrastructure drifted or overclaimed scope",
    )
    require(
        rank1_su4_phi210_intertwiners_exact,
        (
            "rank-one SU(4) Phi210 intertwiner infrastructure drifted, lost "
            "provenance, or overclaimed scope"
        ),
    )
    require(
        rank1_su4_aligned_carriers_exact,
        "rank-one SU(4) aligned-carrier/real-map certificate drifted or overclaimed scope",
    )
    require(
        rank1_su4_phi210_quadratic_basis_exact,
        "rank-one SU(4) Phi210 invariant quadratic-basis certificate drifted or overclaimed G3",
    )
    require(
        rank1_su4_augmented_sos_census_exact,
        "rank-one SU(4) augmented-SOS census drifted or overclaimed a coordinate map, PSD result, arbitrary-Phi bound, or G3",
    )
    require(
        rank1_su4_augmented_sos_cubic_map_exact,
        "rank-one SU(4) augmented cubic map drifted or promoted its abstract zero placeholder to a physical target, PSD result, arbitrary-Phi bound, or G3",
    )
    cubic_scope = exact_rank1_su4_augmented_sos_cubic_map["scope"]
    cubic_map = exact_rank1_su4_augmented_sos_cubic_map["cubic_coordinate_map"]
    require(
        cubic_map["abstract_zero_placeholder_is_not_a_physical_G3_target"]
        is True
        and cubic_map["physical_G3_gap_target_vector_constructed"] is False
        and cubic_map["physical_G3_gap_cubic_zero_RHS_certified"] is False
        and all(
            cubic_scope[name] is False
            for name in (
                "degree_zero_coefficient_map_constructed",
                "degree_one_coefficient_map_constructed",
                "degree_two_coefficient_map_constructed",
                "degree_four_coefficient_map_constructed",
                "full_6585_by_19594_Schur_coordinate_matrix_constructed",
                "physical_G3_gap_target_vector_constructed",
                "physical_G3_gap_cubic_zero_RHS_certified",
                "augmented_Schur_SOS_SDP_constructed",
                "augmented_Schur_SOS_SDP_feasibility_certified",
                "augmented_Schur_SOS_SDP_infeasibility_certified",
                "arbitrary_real_Phi_lower_bound_proved",
                "arbitrary_rank1_Phi_proved",
                "G3_closed",
                "whole_model_validated",
                "whole_model_excluded",
            )
        ),
        "cubic-map placeholder or open-scope contract was promoted beyond the exact theorem",
    )
    require(
        rank1_su4_augmented_sos_quartic_map_exact,
        "rank-one SU(4) augmented quartic map drifted or promoted its rank-only interface to a physical target, PSD congruence, SDP, arbitrary-Phi theorem, or G3",
    )
    quartic_scope = exact_rank1_su4_augmented_sos_quartic_map["scope"]
    quartic_map = exact_rank1_su4_augmented_sos_quartic_map[
        "coefficient_map_certificate"
    ]
    require(
        quartic_map["shape"] == [6_057, 18_085]
        and quartic_map["nnz"] == 115_641
        and quartic_map["rank_over_Q_exact"] == 6_057
        and quartic_map["kernel_dimension_over_Q_exact"] == 12_028
        and all(
            quartic_scope[name] is False
            for name in (
                "physical_quartic_target_constructed",
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
                "semidefinite_feasibility_solved",
                "arbitrary_Phi_stationarity_or_lower_bound_proved",
                "G3_closed",
            )
        ),
        "quartic-map open-scope contract was promoted beyond the exact theorem",
    )
    require(
        rank1_su4_corrected_endpoint_exact,
        "rank-one SU(4) corrected fixed-endpoint theorem drifted, lost byte provenance, or overclaimed G3",
    )
    psd_target_scope = exact_rank1_su4_augmented_sos_psd_target["scope"]
    psd_routes = exact_rank1_su4_augmented_sos_psd_target[
        "standard_PSD_coordinate_routes"
    ]
    corrected_view = corrected_rank1.central_view(
        exact_rank1_su4_corrected_publication
    )
    require(
        psd_routes["real_type_block_count"] == 9
        and psd_routes["complex_Hermitian_block_count"] == 13
        and psd_routes["all_22_cones_have_standard_coordinate_routes"] is True
        and psd_routes["standard_total_parameter_count"] == 19_594
        and gate_ledger._rank1_su4_augmented_sos_psd_target_exact(
            exact_rank1_su4_augmented_sos_psd_target,
            exact_rank1_su4_augmented_sos_census,
            exact_rank1_su4_augmented_sos_cubic_map,
            exact_rank1_su4_augmented_sos_quartic_map,
        ) is False
        and corrected_view["legacy_v20_physical_target_valid"] is False
        and corrected_view["legacy_v20_primal_valid"] is False
        and corrected_view["map_shape"] == [6_585, 19_594]
        and corrected_view["map_common_denominator"] == 256
        and corrected_view["map_nnz"] == 138_550
        and corrected_view["map_numerator_csr_sha256"]
        == corrected_rank1.EXPECTED_MAP_SHA256
        and corrected_view["target_common_denominator"] == 576_000
        and corrected_view["target_nonzero_count"] == 512
        and corrected_view["target_numerator_sha256"]
        == corrected_rank1.EXPECTED_TARGET_SHA256
        and corrected_view["exact_coefficient_equalities"] == 6_585
        and corrected_view["strict_positive_Gram_blocks"] == 22
        and corrected_view["strict_positive_LDL_pivots"] == 824
        and corrected_view["arbitrary_real_Phi_at_fixed_endpoint"] is True
        and corrected_view["strict_positive_off_homogeneous_origin"] is True
        and corrected_view["A_greater_than_3_over_200_at_t1"] is True
        and corrected_view["p_zero_set_at_t1_empty"] is True
        and corrected_view["global_Sigma_proved"] is False
        and corrected_view["general_H_proved"] is False
        and corrected_view["full_H_proved"] is False
        and corrected_view["full_Hessian_proved"] is False
        and corrected_view["G3_closed"] is False,
        "corrected endpoint theorem or superseded-v20 rejection contract drifted",
    )
    alternative_flags = exact_alternative_sos["flags"]
    require(
        exact_alternative_sos["n_failed"] == 0
        and exact_alternative_sos["status"]
        == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
        and exact_alternative_sos["overall_state"] == "G3_GLOBAL_ALTERNATIVE_OPEN"
        and alternative_flags[
            "all_vanishing_45_current_Gram_completion_excluded"
        ]
        is True
        and alternative_flags["all_vanishing_affine_SOS_completion_excluded"]
        is True
        and alternative_flags[
            "all_vanishing_unique_chiral_quartic_completion_excluded"
        ]
        is True
        and alternative_flags[
            "nonvanishing_residual_gradient_cancellation_excluded"
        ]
        is False
        and alternative_flags["different_vacuum_orbit_excluded"] is False
        and alternative_flags["globally_certifiable_alternative_found"] is False
        and alternative_flags["G3_closed"] is False
        and alternative_flags["whole_model_excluded"] is False,
        "alternative global-SOS audit failed or overclaimed its no-go scope",
    )
    require(
        final_g3["n_failed"] == 0
        and final_g3["overall_state"] == "OPEN"
        and final_g3["classification"]["mathematical_G3_closed"] is False
        and final_g3["classification"]["release_G3_verified"] is False
        and final_g3["classification"]["theory_still_viable"] is True,
        "final G3 acceptance gate failed or promoted incomplete evidence",
    )
    eft_flags = exact_eft_g3["closure_flags"]
    eft_scope = exact_eft_g3["scope_boundary"]
    require(
        exact_eft_g3["status"]
        == "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3"
        and eft_scope["EFT_dimension_six_extension"] is True
        and eft_scope["authoritative_renormalizable_51_parameter_model"] is False
        and eft_flags["arbitrary_486_real_field_global_lower_bound"] is True
        and eft_flags["global_equality_orbit_unique_mod_declared_symmetries"]
        is True
        and eft_flags["full_Hessian_PSD_rank_448_nullity_38"] is True
        and eft_flags["G3_closed_for_EFT_extended_model"] is True
        and eft_flags["G3_closed_for_original_renormalizable_model"] is False
        and eft_flags["G4_closed"] is False,
        "dimension-six EFT G3 theorem failed or changed its scope",
    )
    eft_classification = final_g3_eft["classification"]
    eft_contract = final_g3_eft["contract"]
    eft_release_criteria = final_g3_eft["release_criteria"]
    require(
        final_g3_eft["status"]
        == "FINAL_EFT_G3_ACCEPTANCE__MATHEMATICAL_PASS_RELEASE_OPEN"
        and final_g3_eft["core_sha256"]
        == "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
        and eft_contract["base_model_contract_id"] == MODEL_CONTRACT_ID
        and eft_contract["authoritative_renormalizable_parameter_count"] == 51
        and eft_contract["selected_nonzero_renormalizable_parameter_count"] == 27
        and eft_contract["authoritative_51_parameter_contract_unchanged"] is True
        and eft_classification["mathematical_G3_closed_for_EFT_model"] is True
        and eft_classification[
            "mathematical_G3_closed_for_original_renormalizable_model"
        ]
        is False
        and eft_classification["release_G3_verified_for_EFT_model"] is False
        and eft_classification["renormalizable_gate_mutated"] is False
        and eft_classification["G4_closed"] is False
        and eft_release_criteria["G1_promoted_closed"] is False
        and eft_release_criteria["G2_promoted_closed"] is False,
        "parallel EFT G3 gate failed or mutated the renormalizable contract",
    )
    eft_g4_classification = final_g4_eft["classification"]
    eft_g4_contract = final_g4_eft["contract"]
    eft_g4_release_criteria = final_g4_eft["release_criteria"]
    require(
        final_g4_eft["status"]
        == "FINAL_EFT_G4_MATHEMATICAL_PASS_RELEASE_OPEN"
        and final_g4_eft["core_sha256"]
        == "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
        and eft_g4_contract["base_model_contract_id"] == MODEL_CONTRACT_ID
        and eft_g4_contract["EFT_model_contract_id"]
        == eft_contract["EFT_model_contract_id"]
        and eft_g4_contract["authoritative_51_parameter_contract_unchanged"]
        is True
        and eft_g4_classification["mathematical_G4_closed_for_EFT_model"]
        is True
        and eft_g4_classification[
            "mathematical_G4_closed_for_original_renormalizable_model"
        ]
        is False
        and eft_g4_classification["release_G4_verified_for_EFT_model"] is False
        and eft_g4_classification[
            "authoritative_renormalizable_G4_gate_mutated"
        ]
        is False
        and eft_g4_classification["whole_model_validated"] is False
        and eft_g4_release_criteria["G1_promoted_closed"] is False
        and eft_g4_release_criteria["G2_promoted_closed"] is False
        and eft_g4_release_criteria["release_G3_verified_for_EFT_model"]
        is False
        and eft_g4_release_criteria[
            "parallel_EFT_G4_integrated_into_release_orchestrators"
        ]
        is True
        and final_g4_eft["production_mapping"][
            "release_integration_completed"
        ]
        is True
        and "release_integration_required"
        not in final_g4_eft["production_mapping"]
        and set(final_g4_eft["release_blockers"])
        == {
            "Lambda_EFT_and_positive_Wilson_matching_approved",
            "radiative_stability_completed",
            "external_extended_model_contract_executed",
            "G1_promoted_closed",
            "G2_promoted_closed",
            "release_G3_verified_for_EFT_model",
        },
        "parallel EFT G4 gate failed or mutated the renormalizable contract",
    )
    eft_g5_classification = final_g5_eft["classification"]
    eft_g5_contract = final_g5_eft["contract"]
    eft_g5_release_criteria = final_g5_eft["release_criteria"]
    require(
        final_g5_eft["status"]
        == "FINAL_EFT_G5_MATHEMATICAL_GATE__MATHEMATICAL_PASS_RELEASE_OPEN"
        and final_g5_eft["core_sha256"]
        == "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
        and eft_g5_contract["base_model_contract_id"] == MODEL_CONTRACT_ID
        and eft_g5_contract["EFT_model_contract_id"]
        == eft_contract["EFT_model_contract_id"]
        and eft_g5_contract["authoritative_renormalizable_parameter_count"]
        == 51
        and eft_g5_contract["selected_nonzero_renormalizable_parameter_count"]
        == 27
        and eft_g5_contract["dimension_six_operator_count"] == 1
        and eft_g5_contract["authoritative_51_parameter_contract_unchanged"]
        is True
        and eft_g5_classification["mathematical_G5_closed_for_EFT_model"]
        is True
        and eft_g5_classification["release_G5_verified_for_EFT_model"] is False
        and eft_g5_classification["authoritative_renormalizable_G5_closed"]
        is False
        and eft_g5_classification[
            "authoritative_renormalizable_G5_blocked_by_model_contract"
        ]
        is True
        and eft_g5_classification["authoritative_renormalizable_G5_mutated"]
        is False
        and eft_g5_classification["immutable_EFT_G3_gate_mutated"] is False
        and eft_g5_classification["new_SOS_claimed"] is False
        and eft_g5_classification["whole_model_excluded"] is False
        and eft_g5_release_criteria["G1_promoted_closed"] is False
        and eft_g5_release_criteria["G2_promoted_closed"] is False
        and eft_g5_release_criteria[
            "downstream_parallel_G5_integration_completed"
        ]
        is True
        and final_g5_eft["production_mapping"][
            "downstream_integration_completed"
        ]
        is True
        and set(final_g5_eft["release_blockers"])
        == {
            "Lambda_EFT_and_positive_Wilson_matching_approved",
            "radiative_stability_completed",
            "external_extended_model_contract_executed",
            "G1_promoted_closed",
            "G2_promoted_closed",
        },
        "parallel EFT G5 gate failed or mutated authoritative release scope",
    )
    eft_g6_spectrum_classification = exact_eft_g6_spectrum["classification"]
    eft_g6_factorization = exact_eft_g6_spectrum["exact_factorization"]
    eft_g6_quotient = exact_eft_g6_spectrum["physical_quotient"]
    require(
        exact_eft_g6_spectrum["status"]
        == "EXACT_EFT_TREE_LEVEL_PHYSICAL_SCALAR_SPECTRUM"
        and exact_eft_g6_spectrum["core_sha256"]
        == "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
        and exact_eft_g6_spectrum["model_contract_id"]
        == eft_contract["EFT_model_contract_id"]
        and eft_g6_spectrum_classification[
            "EFT_dimension6_tree_level_mathematical_G6_closed"
        ]
        is True
        and eft_g6_spectrum_classification["EFT_release_G6_verified"] is False
        and eft_g6_spectrum_classification[
            "renormalizable_authoritative_G6_closed"
        ]
        is False
        and eft_g6_factorization["total_algebraic_degree"] == 486
        and eft_g6_factorization["zero_multiplicity"] == 38
        and eft_g6_factorization["positive_massive_multiplicity"] == 448
        and eft_g6_factorization["all_nonzero_roots_strictly_positive"] is True
        and eft_g6_quotient["gauge_quotient_dimension"] == 449
        and eft_g6_quotient["physical_PQ_axion_count"] == 1
        and eft_g6_quotient["all_38_zero_modes_are_unphysical"] is False
        and exact_eft_g6_spectrum["mixing_classification"]["complete"] is True
        and exact_eft_g6_spectrum["uncertainty_scope"][
            "physical_threshold_uncertainties_complete"
        ]
        is False,
        "legacy exact EFT G6 factorization drifted before corrected interpretation",
    )
    provenance_classification = g6_sm_provenance["classification"]
    matching_classification = g6_g7_parameterized_matching["classification"]
    require(
        g6_sm_provenance["status"]
        == "EXACT_G6_SM_PROVENANCE_MISMATCH_PROVED__G6_RELEASE_OPEN"
        and g6_sm_provenance["n_failed"] == 0
        and all(g6_sm_provenance["checks"].values())
        and provenance_classification[
            "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89"
        ]
        is True
        and provenance_classification[
            "mathematical_tree_level_mass_factorization_remains_valid"
        ]
        is True
        and provenance_classification[
            "prior_positive_mathematical_G6_as_physical_SM_spectrum_valid"
        ]
        is False
        and provenance_classification["mathematical_physical_G6_closed"] is False
        and provenance_classification["release_level_G6_complete"] is False
        and g6_g7_parameterized_matching["status"]
        == "EXACT_G6_SCALING_AND_FORMAL_G89_THRESHOLD__PHYSICAL_STABILIZER_MISMATCH__G7_OPEN"
        and matching_classification[
            "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete"
        ]
        is True
        and matching_classification["frozen_U1em_identification_correct"] is False
        and matching_classification["physical_SM_scalar_thresholds_identified"]
        is False
        and matching_classification["positive_G7_closed"] is False,
        "corrected G6 provenance or formal G89 matching failed",
    )
    eft_g6_classification = final_g6_eft["classification"]
    eft_g6_release_criteria = final_g6_eft["release_criteria"]
    require(
        final_g6_eft["status"]
        == "FINAL_EFT_G6_FORMAL_SU3_X_U1_89_FACTOR_PASS__PHYSICAL_G6_OPEN"
        and final_g6_eft["contract"]["base_model_contract_id"]
        == MODEL_CONTRACT_ID
        and final_g6_eft["contract"]["EFT_model_contract_id"]
        == eft_contract["EFT_model_contract_id"]
        and eft_g6_classification[
            "formal_SU3_x_U1_89_tree_mass_factorization_closed"
        ]
        is True
        and eft_g6_classification["mathematical_physical_G6_closed"] is False
        and eft_g6_classification["mathematical_G6_closed_for_EFT_model"] is False
        and eft_g6_classification["release_G6_verified_for_EFT_model"] is False
        and eft_g6_classification["authoritative_renormalizable_G6_closed"] is False
        and eft_g6_classification["authoritative_G6_gate_mutated"] is False
        and eft_g6_classification["whole_model_validated"] is False
        and eft_g6_release_criteria[
            "formal_SU3_x_U1_89_tree_mass_factorization_complete"
        ]
        is True
        and eft_g6_release_criteria["mathematical_physical_SM_G6_complete"]
        is False
        and eft_g6_release_criteria[
            "absolute_Lambda_EFT_and_Wilson_matching_approved"
        ]
        is False
        and eft_g6_release_criteria["loop_running_and_pole_mass_spectrum_complete"]
        is False
        and eft_g6_release_criteria["threshold_uncertainty_budget_complete"]
        is False
        and eft_g6_release_criteria[
            "parallel_EFT_G6_integrated_into_release_orchestrators"
        ]
        is True
        and set(final_g6_eft["release_blockers"])
        >= {
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
        },
        "superseding formal G6 gate failed or promoted physical G6",
    )
    gauge_beta_classification = authoritative_gauge_betas["classification"]
    require(
        authoritative_gauge_betas["status"]
        == "EXACT_NONYUKAWA_GAUGE_POLYNOMIAL_CLOSED__FULL_G7_OPEN"
        and authoritative_gauge_betas["n_failed"] == 0
        and all(authoritative_gauge_betas["checks"].values())
        and gauge_beta_classification[
            "exact_nonyukawa_two_loop_gauge_polynomial_closed"
        ]
        is True
        and gauge_beta_classification["full_two_loop_gauge_beta_closed"] is False
        and gauge_beta_classification["component_threshold_matching_closed"]
        is False
        and gauge_beta_classification["physical_G6_input_accepted_for_G7"]
        is False
        and gauge_beta_classification["mathematical_G7_closed"] is False
        and gauge_beta_classification["release_G7_verified"] is False,
        "gauge-only RGE subtheorem drifted or promoted full G7",
    )
    pyrate3_classification = pyrate3_gauge_replay["classification"]
    pyrate3_binding = pyrate3_gauge_replay["source_binding"]
    pyrate3_execution = pyrate3_gauge_replay["executed_input_provenance"]
    require(
        pyrate3_gauge_replay["status"]
        == "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN"
        and pyrate3_gauge_replay["core_sha256"]
        == PYRATE3_GAUGE_REPLAY_CORE_SHA256
        and pyrate3_gauge_replay["source_sha256"]
        == PYRATE3_GAUGE_REPLAY_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json").read_bytes()
        ).hexdigest()
        == PYRATE3_GAUGE_REPLAY_JSON_RAW_SHA256
        and pyrate3_binding["canonical_model"]["raw_sha256"]
        == PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256
        and pyrate3_binding["frozen_replay_data"]["raw_sha256"]
        == PYRATE3_GAUGE_REPLAY_DATA_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "models" / "SO10U1XGaugeAuditV20.model").read_bytes()
        ).hexdigest()
        == PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256
        and hashlib.sha256(
            (
                ROOT
                / "data"
                / "PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json"
            ).read_bytes()
        ).hexdigest()
        == PYRATE3_GAUGE_REPLAY_DATA_RAW_SHA256
        and pyrate3_execution["executed_model_path"]
        == "models/SO10U1XGaugeAudit.model"
        and pyrate3_execution["tracked_canonical_model_path"]
        == "models/SO10U1XGaugeAuditV20.model"
        and pyrate3_execution["executed_model_sha256"]
        == PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256
        and pyrate3_execution["tracked_canonical_model_sha256"]
        == PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256
        and pyrate3_execution["byte_identical_rename"] is True
        and pyrate3_gauge_replay["n_failed"] == 0
        and all(pyrate3_gauge_replay["checks"].values())
        and pyrate3_gauge_replay["comparison"]["all_coefficients_match"] is True
        and pyrate3_classification[
            "second_implementation_for_scoped_gauge_subtheorem"
        ]
        is True
        and pyrate3_classification["full_two_loop_gauge_beta_closed"] is False
        and pyrate3_classification["physical_G6_threshold_matching_closed"]
        is False
        and pyrate3_classification["mathematical_G7_closed"] is False
        and pyrate3_classification["release_G7_verified"] is False,
        "independent PyR@TE replay drifted or promoted full G7",
    )
    eft_g7_classification = exact_eft_g7_nonidentifiability["classification"]
    eft_g7_integration = exact_eft_g7_nonidentifiability["integration"]
    eft_g7_collision = exact_eft_g7_nonidentifiability[
        "formal_U1_89_abstract_restriction_example"
    ]
    eft_g7_scale = exact_eft_g7_nonidentifiability[
        "absolute_scale_counterexample"
    ]
    eft_g7_scope = exact_eft_g7_nonidentifiability["reduced_RGE_model_scope"]
    require(
        exact_eft_g7_nonidentifiability["status"]
        == "FORMAL_U1_89_ABSTRACT_RESTRICTION_NONINJECTIVE__NO_PHYSICAL_G7_CLAIM"
        and exact_eft_g7_nonidentifiability["core_sha256"]
        == EFT_G7_THRESHOLD_NONIDENTIFIABILITY_CORE_SHA256
        and exact_eft_g7_nonidentifiability["n_failed"] == 0
        and exact_eft_g7_nonidentifiability["failures"] == []
        and bool(exact_eft_g7_nonidentifiability["checks"])
        and all(exact_eft_g7_nonidentifiability["checks"].values())
        and eft_g7_collision["same_frozen_G6_masses"] is True
        and eft_g7_collision["restriction_map_noninjective"] is True
        and eft_g7_collision["one_loop_coefficients_differ"] is True
        and eft_g7_collision["physical_QED_interpretation_valid"] is False
        and eft_g7_collision["physical_electroweak_interpretation_valid"]
        is False
        and eft_g7_collision["completion_A"][
            "complex_scalar_one_loop_delta_b2"
        ]
        == "0"
        and eft_g7_collision["completion_A"][
            "complex_scalar_one_loop_delta_bY"
        ]
        == "1/3"
        and eft_g7_collision["completion_B"][
            "complex_scalar_one_loop_delta_b2"
        ]
        == "1/6"
        and eft_g7_collision["completion_B"][
            "complex_scalar_one_loop_delta_bY"
        ]
        == "1/6"
        and eft_g7_scale["same_normalized_G6_spectrum"] is True
        and eft_g7_scale["threshold_log_shift"] == "ln(2)"
        and eft_g7_scale["absolute_scale_unidentified"] is True
        and eft_g7_scope["full_210_quartic_basis_present"] is False
        and eft_g7_scope["lambda4_CGC_present"] is False
        and eft_g7_scope["dimension6_O6_lock_present"] is False
        and eft_g7_scope["two_loop_SO10_complete"] is False
        and eft_g7_scope["piecewise_component_threshold_matching_complete"]
        is False
        and eft_g7_classification[
            "formal_U1_89_abstract_restriction_noninjectivity_proved"
        ]
        is True
        and eft_g7_classification[
            "exact_physical_EFT_G7_input_nonidentifiability_proved"
        ]
        is False
        and eft_g7_classification[
            "historical_electroweak_lift_interpretation_valid"
        ]
        is False
        and eft_g7_classification["mathematical_EFT_G7_closed"] is False
        and eft_g7_classification["EFT_release_G7_verified"] is False
        and eft_g7_classification["authoritative_renormalizable_G7_closed"]
        is False
        and eft_g7_classification["positive_G7_certified"] is False
        and eft_g7_classification["negative_G7_no_go_certified"] is False
        and set(eft_g7_integration)
        == {
            "ledger_consumes_obstruction",
            "roadmap_consumes_obstruction",
            "validation_matrix_consumes_obstruction",
            "release_orchestrators_and_workflows_consume_obstruction",
        }
        and all(value is True for value in eft_g7_integration.values())
        and set(exact_eft_g7_nonidentifiability["release_blockers"])
        == {
            "ELECTROWEAK_AND_INTERMEDIATE_REPRESENTATION_PROVENANCE_REQUIRED",
            "ABSOLUTE_SCALE_AND_WILSON_MATCHING_REQUIRED",
            "COMPLETE_COMPONENT_THRESHOLD_MATCHING_REQUIRED",
            "COMPLETE_GAUGE_YUKAWA_SCALAR_SOFT_EFT_TWO_LOOP_SYSTEM_REQUIRED",
            "SECOND_INDEPENDENT_IMPLEMENTATION_REQUIRED",
            "AUTHORITATIVE_G1_THROUGH_G6_REQUIRED",
        },
        "formal U1_89 restriction audit failed or promoted a physical G7 claim",
    )
    physical_g7_scoped = gate_ledger._physical_g7_component_threshold_contract(
        physical_g7_component_threshold,
        raw_sha256=hashlib.sha256(
            (
                ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
            ).read_bytes()
        ).hexdigest(),
        source_raw_sha256=hashlib.sha256(
            (
                ROOT / "exact_physical_g7_component_threshold_contract_v20.py"
            ).read_bytes()
        ).hexdigest(),
        test_raw_sha256=hashlib.sha256(
            (
                ROOT
                / "test_exact_physical_g7_component_threshold_contract_v20.py"
            ).read_bytes()
        ).hexdigest(),
        markdown_raw_sha256=hashlib.sha256(
            (
                ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md"
            ).read_bytes()
        ).hexdigest(),
    )
    require(
        physical_g7_component_threshold["status"]
        == "EXACT_PHYSICAL_MATTER_BRANCHING_AND_PARAMETERIZED_ONE_LOOP_THRESHOLDS_CLOSED__FULL_G7_OPEN"
        and physical_g7_component_threshold["core_sha256"]
        == PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256
        and physical_g7_scoped["source_raw_sha256"]
        == PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256
        and physical_g7_scoped["test_raw_sha256"]
        == PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256
        and physical_g7_scoped["raw_sha256"]
        == PHYSICAL_G7_COMPONENT_THRESHOLD_JSON_RAW_SHA256
        and physical_g7_scoped["markdown_raw_sha256"]
        == PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256
        and physical_g7_scoped["source_bound"] is True
        and physical_g7_scoped["authoritative_inventory_closed"] is True
        and physical_g7_scoped["continuous_gauge_anomalies_closed"] is True
        and physical_g7_scoped["exact_one_loop_gauge_coefficients_closed"] is True
        and physical_g7_scoped[
            "exact_two_loop_nonyukawa_gauge_flow_closed"
        ]
        is True
        and physical_g7_scoped[
            "independent_official_PyRATE3_gauge_replay_closed"
        ]
        is True
        and physical_g7_scoped["physical_PS_SM_matter_branching_closed"] is True
        and physical_g7_scoped[
            "parameterized_one_loop_matter_threshold_kernel_closed"
        ]
        is True
        and physical_g7_scoped[
            "physical_component_pole_mass_matrices_closed"
        ]
        is False
        and physical_g7_scoped["heavy_vector_matching_closed"] is False
        and physical_g7_scoped["physical_G7_closed"] is False
        and physical_g7_scoped["mathematical_G7_closed"] is False
        and physical_g7_scoped["release_G7_verified"] is False
        and physical_g7_scoped["authoritative_renormalizable_G7_closed"] is False
        and physical_g7_scoped["positive_G7_certified"] is False
        and physical_g7_scoped["negative_G7_no_go_certified"] is False,
        "physical PS/SM G7 component-threshold contract drifted or promoted full G7",
    )
    normalized_yukawa_cgcs_scoped = (
        gate_ledger._normalized_so10_yukawa_cgc_contract(
            normalized_yukawa_cgcs,
            raw_sha256=hashlib.sha256(
                (ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json").read_bytes()
            ).hexdigest(),
            source_raw_sha256=hashlib.sha256(
                (ROOT / "exact_normalized_so10_yukawa_cgcs_v20.py").read_bytes()
            ).hexdigest(),
            test_raw_sha256=hashlib.sha256(
                (ROOT / "test_exact_normalized_so10_yukawa_cgcs_v20.py").read_bytes()
            ).hexdigest(),
            markdown_raw_sha256=hashlib.sha256(
                (ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md").read_bytes()
            ).hexdigest(),
        )
    )
    require(
        normalized_yukawa_cgcs["status"]
        == "EXACT_NORMALIZED_SO10_REPRESENTATION_YUKAWA_CGCS_CLOSED__FLAVOR_RGE_AND_FULL_G7_OPEN"
        and normalized_yukawa_cgcs["core_sha256"]
        == NORMALIZED_YUKAWA_CGCS_CORE_SHA256
        and normalized_yukawa_cgcs_scoped["source_raw_sha256"]
        == NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256
        and normalized_yukawa_cgcs_scoped["test_raw_sha256"]
        == NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256
        and normalized_yukawa_cgcs_scoped["raw_sha256"]
        == NORMALIZED_YUKAWA_CGCS_JSON_RAW_SHA256
        and normalized_yukawa_cgcs_scoped["markdown_raw_sha256"]
        == NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256
        and normalized_yukawa_cgcs_scoped["source_bound"] is True
        and normalized_yukawa_cgcs_scoped["normalized_10_CGCs_closed"] is True
        and normalized_yukawa_cgcs_scoped["normalized_126bar_CGCs_closed"]
        is True
        and normalized_yukawa_cgcs_scoped[
            "normalized_singlet_duality_CGC_closed"
        ]
        is True
        and normalized_yukawa_cgcs_scoped[
            "canonical_304_Weyl_sparse_embedding_closed"
        ]
        is True
        and normalized_yukawa_cgcs_scoped[
            "all_declared_representation_CGCs_closed"
        ]
        is True
        and normalized_yukawa_cgcs_scoped["flavor_boundary_values_closed"]
        is False
        and normalized_yukawa_cgcs_scoped["SARAH_Dot_conversion_closed"]
        is False
        and normalized_yukawa_cgcs_scoped[
            "full_one_two_loop_Yukawa_betas_closed"
        ]
        is False
        and normalized_yukawa_cgcs_scoped[
            "physical_threshold_matching_and_running_closed"
        ]
        is False
        and normalized_yukawa_cgcs_scoped["full_yukawa_sector_closed"] is False
        and normalized_yukawa_cgcs_scoped["physical_G7_closed"] is False
        and normalized_yukawa_cgcs_scoped["mathematical_G7_closed"] is False
        and normalized_yukawa_cgcs_scoped["release_G7_verified"] is False,
        "normalized SO(10) Yukawa-CGC contract drifted or promoted flavor/RGE/full G7",
    )
    physical_sm_scoped = gate_ledger._physical_sm_vacuum_truth_overlay(
        physical_sm_vacuum,
        raw_sha256=hashlib.sha256(
            (ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json").read_bytes()
        ).hexdigest(),
        source_raw_sha256=hashlib.sha256(
            (ROOT / "physical_sm_vacuum_local_feasibility_v20.py").read_bytes()
        ).hexdigest(),
        test_raw_sha256=hashlib.sha256(
            (ROOT / "test_physical_sm_vacuum_local_feasibility_v20.py").read_bytes()
        ).hexdigest(),
        markdown_raw_sha256=hashlib.sha256(
            (ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md").read_bytes()
        ).hexdigest(),
    )
    require(
        physical_sm_vacuum["status"]
        == "PHYSICAL_SM_RECONSTRUCTED_GLOBAL_EFT_CERTIFICATE__DIRECT_SOURCE_ALGEBRA_AND_GLOBAL_EQUALITY_ORBIT_OPEN"
        and physical_sm_vacuum["integrity"]["core_sha256"]
        == PHYSICAL_SM_VACUUM_CORE_SHA256
        and physical_sm_scoped["source_raw_sha256"]
        == PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256
        and physical_sm_scoped["test_raw_sha256"]
        == PHYSICAL_SM_VACUUM_TEST_RAW_SHA256
        and physical_sm_scoped["raw_sha256"] == PHYSICAL_SM_VACUUM_JSON_RAW_SHA256
        and physical_sm_scoped["markdown_raw_sha256"]
        == PHYSICAL_SM_VACUUM_MD_RAW_SHA256
        and physical_sm_scoped["source_bound"] is True
        and physical_sm_scoped["physical_SM_target_exactly_constructed"] is True
        and physical_sm_scoped["standard_SU3C_x_U1em_stabilizer_proved"] is True
        and physical_sm_scoped[
            "reconstructed_stationary_transverse_PSD_witness_available"
        ]
        is True
        and physical_sm_scoped[
            "direct_source_algebra_stationary_PSD_witness_available"
        ]
        is False
        and physical_sm_scoped["source_bound_global_equality_orbit_proved"]
        is False
        and physical_sm_scoped["old_selected_EFT_stabilizer_label_superseded"]
        is True
        and physical_sm_scoped["old_selected_EFT_target_actual_stabilizer"]
        == "SU(3)_C x U(1)_89"
        and physical_sm_scoped["physical_SM_G3_closed"] is False
        and physical_sm_scoped["physical_SM_G4_closed"] is False
        and physical_sm_scoped["physical_SM_G5_closed"] is False
        and physical_sm_scoped["physical_SM_G6_closed"] is False
        and physical_sm_scoped["physical_SM_G7_closed"] is False,
        "physical-SM vacuum truth overlay drifted or promoted physical G3-G7",
    )
    physical_sm_source_equality_scoped = (
        gate_ledger._physical_sm_source_algebra_equality_frontier_contract(
            physical_sm_source_equality_frontier,
            raw_sha256=hashlib.sha256(
                (
                    ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json"
                ).read_bytes()
            ).hexdigest(),
            source_raw_sha256=hashlib.sha256(
                (
                    ROOT / "physical_sm_source_algebra_equality_frontier_v20.py"
                ).read_bytes()
            ).hexdigest(),
            test_raw_sha256=hashlib.sha256(
                (
                    ROOT
                    / "test_physical_sm_source_algebra_equality_frontier_v20.py"
                ).read_bytes()
            ).hexdigest(),
            markdown_raw_sha256=hashlib.sha256(
                (
                    ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md"
                ).read_bytes()
            ).hexdigest(),
        )
    )
    require(
        physical_sm_source_equality_frontier["status"]
        == "RADIAL_EQUALITY_CLOSED__FULL_SOURCE_ALGEBRA_AND_EQUALITY_ORBIT_OPEN"
        and physical_sm_source_equality_frontier["integrity"]["core_sha256"]
        == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256
        and physical_sm_source_equality_scoped["source_raw_sha256"]
        == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_SOURCE_RAW_SHA256
        and physical_sm_source_equality_scoped["test_raw_sha256"]
        == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_TEST_RAW_SHA256
        and physical_sm_source_equality_scoped["raw_sha256"]
        == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_JSON_RAW_SHA256
        and physical_sm_source_equality_scoped["markdown_raw_sha256"]
        == PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_MD_RAW_SHA256
        and physical_sm_source_equality_scoped["source_bound"] is True
        and physical_sm_source_equality_scoped[
            "radial_stationary_equality_classified_exactly"
        ]
        is True
        and physical_sm_source_equality_scoped[
            "direct_source_algebra_stationary_Hessian_available"
        ]
        is False
        and physical_sm_source_equality_scoped[
            "complete_nonradial_equality_orbit_proved"
        ]
        is False
        and physical_sm_source_equality_scoped["physical_SM_G3_closed"] is False
        and physical_sm_source_equality_scoped["physical_SM_G4_closed"] is False
        and physical_sm_source_equality_scoped["physical_SM_G5_closed"] is False,
        "physical-SM source/equality frontier drifted or promoted the direct Hessian/full G3-G5",
    )
    require(
        physical_sm_five_amplitude["schema"]
        == "exact_physical_sm_five_amplitude_equality_v20"
        and physical_sm_five_amplitude["status"]
        == "EXACT_FIVE_AMPLITUDE_STATIONARY_EQUALITY_CLASSIFIED__FULL_486_ORBIT_OPEN"
        and physical_sm_five_amplitude["integrity"]["core_sha256"]
        == PHYSICAL_SM_FIVE_AMPLITUDE_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_five_amplitude_equality_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_FIVE_AMPLITUDE_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_five_amplitude_equality_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_FIVE_AMPLITUDE_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_FIVE_AMPLITUDE_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_FIVE_AMPLITUDE_MD_RAW_SHA256
        and physical_sm_five_amplitude["n_checks"] == 12
        and physical_sm_five_amplitude["n_failed"] == 0
        and all(physical_sm_five_amplitude["checks"].values())
        and physical_sm_five_amplitude["restriction"]["ambient_real_field_dimension"]
        == 486
        and physical_sm_five_amplitude["restriction"]["slice_dimension"] == 5
        and physical_sm_five_amplitude["restriction"][
            "polynomial_fitting_or_float_sampling_used"
        ]
        is False
        and physical_sm_five_amplitude["restriction"][
            "exact_algebra_is_conditional_on_frozen_upstream_witness_table"
        ]
        is True
        and physical_sm_five_amplitude["restriction"][
            "witness_coefficients_directly_derived_from_integer_projector_source_algebra"
        ]
        is False
        and physical_sm_five_amplitude["exact_Groebner_certificate"][
            "reduced_Groebner_basis"
        ]
        == ["h**2 - 1", "d**2 - 1", "s**2 - 1", "x**2 - 1", "p - 1"]
        and physical_sm_five_amplitude["exact_Groebner_certificate"][
            "complex_solution_count_with_multiplicity"
        ]
        == 16
        and physical_sm_five_amplitude["exact_Groebner_certificate"][
            "all_solutions_real"
        ]
        is True
        and physical_sm_five_amplitude["exact_Groebner_certificate"][
            "target_slice_Hessian_positive_definite"
        ]
        is True
        and physical_sm_five_amplitude["discrete_variants"]["count"] == 16
        and physical_sm_five_amplitude["discrete_variants"][
            "exact_discrete_sign_symmetries_of_selected_witness"
        ]
        is True
        and physical_sm_five_amplitude["discrete_variants"][
            "continuous_SO10_x_U1X_x_PQ_orbit_equivalence_classified"
        ]
        is False
        and physical_sm_five_amplitude["closure_claims"][
            "five_real_amplitude_slice_stationary_equality_classified"
        ]
        is True
        and physical_sm_five_amplitude["closure_claims"][
            "full_486_field_stationary_equality_classified"
        ]
        is False
        and physical_sm_five_amplitude["closure_claims"][
            "direct_source_algebra_full_486_Hessian_available"
        ]
        is False
        and physical_sm_five_amplitude["closure_claims"]["physical_SM_G3_closed"]
        is False
        and physical_sm_five_amplitude["closure_claims"]["physical_SM_G4_closed"]
        is False
        and physical_sm_five_amplitude["closure_claims"]["physical_SM_G5_closed"]
        is False,
        "physical-SM five-amplitude equality theorem drifted or overclaimed full G3-G5",
    )
    require(
        physical_sm_hard_projector_hessians["schema"]
        == "exact_physical_sm_hard_projector_hessians_v20"
        and physical_sm_hard_projector_hessians["status"]
        == "EXACT_TEN_HARD_PROJECTOR_HESSIANS__FULL_37_ROW_AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
        and physical_sm_hard_projector_hessians["integrity"]["core_sha256"]
        == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_hard_projector_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_hard_projector_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD_RAW_SHA256
        and physical_sm_hard_projector_hessians["n_checks"] == 11
        and physical_sm_hard_projector_hessians["n_failed"] == 0
        and physical_sm_hard_projector_hessians["failures"] == []
        and all(physical_sm_hard_projector_hessians["checks"].values())
        and physical_sm_hard_projector_hessians["scope_accounting"][
            "active_witness_row_count"
        ]
        == 37
        and physical_sm_hard_projector_hessians["scope_accounting"][
            "exact_source_rows_certified_here"
        ]
        == 10
        and physical_sm_hard_projector_hessians["scope_accounting"][
            "remaining_active_row_count"
        ]
        == 27
        and len(
            physical_sm_hard_projector_hessians["scope_accounting"][
                "remaining_active_rows"
            ]
        )
        == 27
        and physical_sm_hard_projector_hessians["claims"][
            "exact_source_algebra_Hessians_for_all_10_O27_O44_rows"
        ]
        is True
        and physical_sm_hard_projector_hessians["claims"][
            "exact_source_algebra_Hessians_for_all_37_active_witness_rows"
        ]
        is False
        and physical_sm_hard_projector_hessians["claims"][
            "exact_full_witness_aggregate_stationarity"
        ]
        is False
        and physical_sm_hard_projector_hessians["claims"][
            "exact_full_witness_symmetry_kernel"
        ]
        is False
        and physical_sm_hard_projector_hessians["claims"][
            "exact_full_witness_rank_448_and_PSD"
        ]
        is False
        and physical_sm_hard_projector_hessians["claims"][
            "full_486_field_global_equality_orbit_classified"
        ]
        is False
        and all(
            physical_sm_hard_projector_hessians["claims"][gate] is False
            for gate in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
        "physical-SM hard-projector Hessians drifted or promoted the open 27-row/full G3-G5 problem",
    )
    require(
        physical_sm_easy_21_hessians["schema"]
        == "exact_physical_sm_easy_21_hessians_v20"
        and physical_sm_easy_21_hessians["status"]
        == "EXACT_21_NONHARD_HESSIANS__COMBINED_31_OF_37_SOURCE_ROWS__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
        and physical_sm_easy_21_hessians["integrity"]["core_sha256"]
        == PHYSICAL_SM_EASY_21_HESSIANS_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_easy_21_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_EASY_21_HESSIANS_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_easy_21_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_EASY_21_HESSIANS_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_EASY_21_HESSIANS_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_EASY_21_HESSIANS_MD_RAW_SHA256
        and physical_sm_easy_21_hessians["n_checks"] == 7
        and physical_sm_easy_21_hessians["n_failed"] == 0
        and physical_sm_easy_21_hessians["failures"] == []
        and all(physical_sm_easy_21_hessians["checks"].values())
        and physical_sm_easy_21_hessians["scope_accounting"][
            "active_witness_rows"
        ]
        == 37
        and physical_sm_easy_21_hessians["scope_accounting"][
            "rows_certified_here"
        ]
        == 21
        and physical_sm_easy_21_hessians["scope_accounting"][
            "hard_theorem_rows"
        ]
        == 10
        and physical_sm_easy_21_hessians["scope_accounting"][
            "combined_exact_source_rows"
        ]
        == 31
        and physical_sm_easy_21_hessians["scope_accounting"][
            "remaining_row_count"
        ]
        == 6
        and len(physical_sm_easy_21_hessians["scope_accounting"]["remaining_rows"])
        == 6
        and physical_sm_easy_21_hessians["claims"][
            "exact_source_algebra_Hessians_for_21_rows_here"
        ]
        is True
        and physical_sm_easy_21_hessians["claims"][
            "combined_with_hard_theorem_exact_source_rows"
        ]
        == 31
        and physical_sm_easy_21_hessians["claims"][
            "exact_source_algebra_Hessians_for_all_37_active_rows"
        ]
        is False
        and physical_sm_easy_21_hessians["claims"][
            "exact_full_witness_aggregate_stationarity"
        ]
        is False
        and physical_sm_easy_21_hessians["claims"][
            "exact_full_witness_symmetry_kernel"
        ]
        is False
        and physical_sm_easy_21_hessians["claims"][
            "exact_full_witness_rank_448_and_PSD"
        ]
        is False
        and physical_sm_easy_21_hessians["claims"][
            "full_486_field_global_equality_orbit_classified"
        ]
        is False
        and all(
            physical_sm_easy_21_hessians["claims"][gate] is False
            for gate in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
        "physical-SM easy-21 Hessians drifted or promoted the open six-row/full G3-G5 problem",
    )
    require(
        physical_sm_last_six_hessians["schema"]
        == "exact_physical_sm_last_six_hessians_v20"
        and physical_sm_last_six_hessians["status"]
        == "EXACT_LAST_SIX_SOURCE_HESSIANS__ALL_37_ROWS_AVAILABLE__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
        and physical_sm_last_six_hessians["integrity"]["core_sha256"]
        == PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_last_six_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_last_six_hessians_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LAST_SIX_HESSIANS_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LAST_SIX_HESSIANS_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LAST_SIX_HESSIANS_MD_RAW_SHA256
        and physical_sm_last_six_hessians["n_checks"] == 6
        and physical_sm_last_six_hessians["n_failed"] == 0
        and physical_sm_last_six_hessians["failures"] == []
        and all(physical_sm_last_six_hessians["checks"].values())
        and physical_sm_last_six_hessians["scope_accounting"]["hard_rows"] == 10
        and physical_sm_last_six_hessians["scope_accounting"]["easy_rows"] == 21
        and physical_sm_last_six_hessians["scope_accounting"]["last_rows"] == 6
        and physical_sm_last_six_hessians["scope_accounting"][
            "total_active_source_Hessians_available"
        ]
        == 37
        and physical_sm_last_six_hessians["claims"][
            "exact_last_six_source_Hessians"
        ]
        is True
        and physical_sm_last_six_hessians["claims"][
            "all_37_active_source_Hessians_available_across_three_theorems"
        ]
        is True
        and physical_sm_last_six_hessians["claims"][
            "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here"
        ]
        is False
        and physical_sm_last_six_hessians["claims"][
            "full_486_field_global_equality_orbit_classified"
        ]
        is False
        and all(
            physical_sm_last_six_hessians["claims"][gate] is False
            for gate in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
        "physical-SM last-six Hessians drifted or promoted the open aggregate/global G3-G5 problem",
    )
    require(
        physical_sm_37_row_aggregate["schema"]
        == "exact_physical_sm_37_row_aggregate_v20"
        and physical_sm_37_row_aggregate["status"]
        == "EXACT_ALL_37_SOURCE_AGGREGATE_STATIONARY_KERNEL_RANK_PSD__GLOBAL_EQUALITY_ORBIT_OPEN"
        and physical_sm_37_row_aggregate["integrity"]["core_sha256"]
        == PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_37_row_aggregate_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_37_row_aggregate_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_37_ROW_AGGREGATE_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_37_ROW_AGGREGATE_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_37_ROW_AGGREGATE_MD_RAW_SHA256
        and physical_sm_37_row_aggregate["n_checks"] == 9
        and physical_sm_37_row_aggregate["n_failed"] == 0
        and physical_sm_37_row_aggregate["failures"] == []
        and all(physical_sm_37_row_aggregate["checks"].values())
        and physical_sm_37_row_aggregate["source_aggregate_assembly"][
            "active_row_count"
        ]
        == 37
        and physical_sm_37_row_aggregate["source_aggregate_assembly"][
            "nonzero_entries"
        ]
        == 5840
        and physical_sm_37_row_aggregate["source_aggregate_assembly"][
            "entrywise_identity_to_historical_reconstructed_rational_aggregate"
        ]
        is True
        and physical_sm_37_row_aggregate["exact_stationarity"][
            "exact_potential_value"
        ]
        == "-1"
        and physical_sm_37_row_aggregate["exact_stationarity"][
            "exact_gradient_is_zero"
        ]
        is True
        and physical_sm_37_row_aggregate["exact_kernel_and_rank"]["exact_rank"]
        == 448
        and physical_sm_37_row_aggregate["exact_kernel_and_rank"]["exact_nullity"]
        == 38
        and physical_sm_37_row_aggregate["exact_kernel_and_rank"][
            "kernel_equals_exact_symmetry_tangent_span"
        ]
        is True
        and physical_sm_37_row_aggregate["exact_PSD_certificate"][
            "strictly_positive_exact_pivot_count"
        ]
        == 448
        and physical_sm_37_row_aggregate["exact_PSD_certificate"][
            "full_Hessian_is_positive_semidefinite"
        ]
        is True
        and physical_sm_37_row_aggregate["scope_boundary"][
            "source_bound_local_stationary_Hessian_problem_complete"
        ]
        is True
        and physical_sm_37_row_aggregate["scope_boundary"][
            "global_equality_orbit_classification_complete"
        ]
        is False
        and physical_sm_37_row_aggregate["claims"][
            "all_37_active_Hessians_derived_from_exact_source_algebra"
        ]
        is True
        and physical_sm_37_row_aggregate["claims"][
            "exact_source_aggregate_is_PSD_and_strictly_positive_mod_symmetry"
        ]
        is True
        and physical_sm_37_row_aggregate["claims"][
            "full_486_field_global_equality_orbit_classified"
        ]
        is False
        and all(
            physical_sm_37_row_aggregate["claims"][gate] is False
            for gate in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
        "physical-SM 37-row aggregate drifted or promoted the open global G3-G5 problem",
    )
    require(
        physical_sm_local_equality_orbit["schema"]
        == "exact_physical_sm_local_equality_orbit_v20"
        and physical_sm_local_equality_orbit["status"]
        == "EXACT_FULL_486_LOCAL_EQUALITY_ORBIT_AND_16_SIGN_ORBIT__GLOBAL_EQUALITY_OPEN"
        and physical_sm_local_equality_orbit["integrity"]["core_sha256"]
        == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_local_equality_orbit_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_local_equality_orbit_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD_RAW_SHA256
        and physical_sm_local_equality_orbit["n_checks"] == 13
        and physical_sm_local_equality_orbit["n_failed"] == 0
        and physical_sm_local_equality_orbit["failures"] == []
        and all(physical_sm_local_equality_orbit["checks"].values())
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "ambient_real_dimension"
        ]
        == 486
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "target_orbit_dimension"
        ]
        == 38
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "normal_slice_dimension"
        ]
        == 448
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "quantitative_radius"
        ]
        is None
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "hypotheses"
        ]["Hessian_kernel_equals_orbit_tangent"]
        is True
        and physical_sm_local_equality_orbit["local_orbit_theorem"][
            "hypotheses"
        ]["Hessian_positive_definite_on_a_transverse_complement"]
        is True
        and len(physical_sm_local_equality_orbit["sixteen_sign_orbit"]["rows"])
        == 16
        and all(
            row["actual_486_coordinate_endpoint_matches_amplitude_variant"]
            is True
            for row in physical_sm_local_equality_orbit["sixteen_sign_orbit"][
                "rows"
            ]
        )
        and physical_sm_local_equality_orbit["scope_boundary"][
            "not_just_five_amplitude_slice"
        ]
        is True
        and physical_sm_local_equality_orbit["scope_boundary"][
            "theorem_is_full_486_dimensional_but_local_near_the_entire_compact_orbit"
        ]
        is True
        and physical_sm_local_equality_orbit["scope_boundary"][
            "distant_or_disconnected_equality_components_excluded"
        ]
        is False
        and physical_sm_local_equality_orbit["scope_boundary"][
            "global_polynomial_ideal_or_global_SOS_orbit_separator_supplied"
        ]
        is False
        and physical_sm_local_equality_orbit["claims"][
            "exists_K_invariant_open_neighborhood_U_of_target_orbit"
        ]
        is True
        and physical_sm_local_equality_orbit["claims"][
            "Crit_V_intersection_U_equals_target_orbit"
        ]
        is True
        and physical_sm_local_equality_orbit["claims"][
            "stationary_V_minus_one_locus_intersection_U_equals_target_orbit"
        ]
        is True
        and physical_sm_local_equality_orbit["claims"][
            "all_16_five_amplitude_sign_variants_one_continuous_K_orbit"
        ]
        is True
        and physical_sm_local_equality_orbit["claims"][
            "quantitative_radius_for_U_proved"
        ]
        is False
        and physical_sm_local_equality_orbit["claims"][
            "complete_486_field_global_equality_orbit_classified"
        ]
        is False
        and all(
            physical_sm_local_equality_orbit["claims"][gate] is False
            for gate in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
        "physical-SM local equality orbit drifted, claimed a radius/global result, or promoted G3-G5",
    )
    require(
        physical_sm_g4_g5_branch_mismatch["schema"]
        == "exact_physical_sm_g4_g5_branch_mismatch_v1"
        and physical_sm_g4_g5_branch_mismatch["status"]
        == "EXACT_FIVE_AMPLITUDE_VS_PHYSICAL_EW_BRANCH_MISMATCH_PROVED__CANONICAL_G4_G5_AND_DOWNSTREAM_G6_G8_OPEN"
        and physical_sm_g4_g5_branch_mismatch["integrity"]["core_sha256"]
        == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_g4_g5_branch_mismatch_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD_RAW_SHA256
        and physical_sm_g4_g5_branch_mismatch["n_checks"] == 10
        and physical_sm_g4_g5_branch_mismatch["n_failed"] == 0
        and physical_sm_g4_g5_branch_mismatch["failures"] == []
        and all(physical_sm_g4_g5_branch_mismatch["checks"].values())
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "exact_branch_mismatch_proved"
        ]
        is True
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "global_no_go_for_all_possible_physical_EW_branches"
        ]
        is False
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "new_hierarchy_mechanism_ruled_out"
        ]
        is False
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "physical_G4_G5_G6_G7_G8_closed"
        ]
        is False
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "release_G4_G5_G6_G7_G8_closed"
        ]
        is False
        and physical_sm_g4_g5_branch_mismatch["scope"][
            "authoritative_G4_G5_G6_G7_G8_closed"
        ]
        is False
        and all(
            value is False
            for boundary in physical_sm_g4_g5_branch_mismatch[
                "gate_acceptance_boundary"
            ].values()
            for key, value in boundary.items()
            if key.endswith("_closed")
        ),
        "physical-SM G4/G5 branch mismatch drifted, overclaimed a global no-go, or promoted G4-G8",
    )
    scalar_spectrum_scoped = (
        gate_ledger._conditional_physical_sm_eft_hessian_spectrum_contract(
            conditional_physical_sm_eft_hessian_spectrum,
            raw_sha256=hashlib.sha256(
                (
                    ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json"
                ).read_bytes()
            ).hexdigest(),
            source_raw_sha256=hashlib.sha256(
                (ROOT / "conditional_physical_sm_eft_hessian_spectrum_v20.py").read_bytes()
            ).hexdigest(),
            test_raw_sha256=hashlib.sha256(
                (
                    ROOT / "test_conditional_physical_sm_eft_hessian_spectrum_v20.py"
                ).read_bytes()
            ).hexdigest(),
            markdown_raw_sha256=hashlib.sha256(
                (
                    ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md"
                ).read_bytes()
            ).hexdigest(),
        )
    )
    require(
        conditional_physical_sm_eft_hessian_spectrum["status"]
        == "CONDITIONAL_EXACT_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM__SOURCE_ALGEBRA_POLE_AND_RELEASE_CLOSURE_OPEN"
        and conditional_physical_sm_eft_hessian_spectrum["integrity"]["core_sha256"]
        == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256
        and scalar_spectrum_scoped["source_raw_sha256"]
        == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_SOURCE_RAW_SHA256
        and scalar_spectrum_scoped["test_raw_sha256"]
        == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_TEST_RAW_SHA256
        and scalar_spectrum_scoped["raw_sha256"]
        == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_JSON_RAW_SHA256
        and scalar_spectrum_scoped["markdown_raw_sha256"]
        == CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_MD_RAW_SHA256
        and scalar_spectrum_scoped["source_bound"] is True
        and scalar_spectrum_scoped[
            "conditional_reconstructed_tree_scalar_spectrum_closed"
        ]
        is True
        and scalar_spectrum_scoped["conditional_tree_Hessian_factorization_closed"]
        is True
        and scalar_spectrum_scoped["conditional_tree_sector_assignment_closed"]
        is True
        and conditional_physical_sm_eft_hessian_spectrum[
            "squared_EFT_spectrum"
        ]["total_root_count_with_multiplicity"]
        == 486
        and conditional_physical_sm_eft_hessian_spectrum[
            "squared_EFT_spectrum"
        ]["positive_root_count_with_multiplicity"]
        == 448
        and conditional_physical_sm_eft_hessian_spectrum[
            "squared_EFT_spectrum"
        ]["zero_root_count_with_multiplicity"]
        == 38
        and scalar_spectrum_scoped[
            "source_algebra_derived_tree_scalar_spectrum_closed"
        ]
        is False
        and scalar_spectrum_scoped["physical_scalar_pole_spectrum_closed"]
        is False
        and scalar_spectrum_scoped["physical_G6_closed"] is False
        and scalar_spectrum_scoped["release_G6_verified"] is False,
        "conditional physical-SM tree Hessian spectrum drifted or promoted physical/pole/release G6",
    )
    heavy_vectors_scoped = gate_ledger._physical_sm_heavy_vector_mass_contract(
        physical_sm_heavy_vector_masses,
        raw_sha256=hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json").read_bytes()
        ).hexdigest(),
        source_raw_sha256=hashlib.sha256(
            (ROOT / "exact_physical_sm_heavy_vector_masses_v20.py").read_bytes()
        ).hexdigest(),
        test_raw_sha256=hashlib.sha256(
            (ROOT / "test_exact_physical_sm_heavy_vector_masses_v20.py").read_bytes()
        ).hexdigest(),
        markdown_raw_sha256=hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md").read_bytes()
        ).hexdigest(),
    )
    require(
        physical_sm_heavy_vector_masses["status"]
        == "EXACT_PARAMETERIZED_PHYSICAL_SM_HEAVY_VECTOR_MASS_THEOREM_CLOSED__LOOP_MATCHING_AND_FULL_G6_G7_OPEN"
        and physical_sm_heavy_vector_masses["core_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256
        and heavy_vectors_scoped["source_raw_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MASSES_SOURCE_RAW_SHA256
        and heavy_vectors_scoped["test_raw_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MASSES_TEST_RAW_SHA256
        and heavy_vectors_scoped["raw_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MASSES_JSON_RAW_SHA256
        and heavy_vectors_scoped["markdown_raw_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MASSES_MD_RAW_SHA256
        and heavy_vectors_scoped["source_bound"] is True
        and heavy_vectors_scoped[
            "exact_parameterized_tree_vector_mass_matrix_closed"
        ]
        is True
        and heavy_vectors_scoped[
            "exact_vector_rank_kernel_and_Goldstone_image_closed"
        ]
        is True
        and heavy_vectors_scoped[
            "exact_SU3C_x_U1em_vector_sector_resolution_closed"
        ]
        is True
        and heavy_vectors_scoped[
            "parameterized_vector_threshold_log_inputs_closed"
        ]
        is True
        and physical_sm_heavy_vector_masses["rank_kernel_Goldstone"][
            "exact_gram_rank"
        ]
        == 37
        and physical_sm_heavy_vector_masses["rank_kernel_Goldstone"][
            "exact_gram_nullity"
        ]
        == 9
        and heavy_vectors_scoped["absolute_physical_vector_masses_closed"]
        is False
        and heavy_vectors_scoped["pole_vector_masses_closed"] is False
        and heavy_vectors_scoped["vector_Goldstone_ghost_matching_closed"] is False
        and heavy_vectors_scoped[
            "complete_one_loop_vector_threshold_matching_closed"
        ]
        is False
        and heavy_vectors_scoped["physical_G6_closed"] is False
        and heavy_vectors_scoped["physical_G7_closed"] is False,
        "physical-SM heavy-vector contract drifted or promoted pole/full G6/G7",
    )
    require(
        physical_sm_heavy_vector_msbar_matching["status"]
        == "EXACT_COMBINED_HEAVY_VECTOR_GHOST_GOLDSTONE_MSBAR_MATCHING_CLOSED__ARBITRARY_RXI_POLE_PRE_EW_AND_FULL_G7_OPEN"
        and physical_sm_heavy_vector_msbar_matching["core_sha256"]
        == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_heavy_vector_msbar_matching_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_MD_RAW_SHA256
        and physical_sm_heavy_vector_msbar_matching["scope"][
            "combined_heavy_vector_FPghost_Goldstone_MSbar_matching"
        ]
        is True
        and physical_sm_heavy_vector_msbar_matching["scope"][
            "finite_MSbar_vector_constant"
        ]
        is True
        and physical_sm_heavy_vector_msbar_matching["exact_group_factors"][
            "complex_index_totals"
        ]
        == {"SU3": "5/2", "QED": "32/3"}
        and physical_sm_heavy_vector_msbar_matching["scope"][
            "arbitrary_Rxi_sector_resolved_determinants"
        ]
        is False
        and physical_sm_heavy_vector_msbar_matching["scope"]["pole_mass_thresholds"]
        is False
        and physical_sm_heavy_vector_msbar_matching["scope"][
            "SM_symmetric_pre_EW_threshold"
        ]
        is False
        and physical_sm_heavy_vector_msbar_matching["scope"]["physical_G6"]
        is False
        and physical_sm_heavy_vector_msbar_matching["scope"]["physical_G7"]
        is False,
        "physical-SM heavy-vector MS-bar matching drifted or promoted Rxi/pole/pre-EW/full G6/G7",
    )
    require(
        physical_sm_vector_rxi["status"]
        == "EXACT_ALL_37_BROKEN_DIRECTION_RXI_VACUUM_DETERMINANT_CANCELLATION_CLOSED__BACKGROUND_FIELD_POLE_AND_FULL_G6_G7_OPEN"
        and physical_sm_vector_rxi["core_sha256"]
        == PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_VECTOR_RXI_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_VECTOR_RXI_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_VECTOR_RXI_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_VECTOR_RXI_MD_RAW_SHA256
        and physical_sm_vector_rxi["scope"][
            "arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation"
        ]
        is True
        and physical_sm_vector_rxi["scope"][
            "all_37_broken_real_directions_resolved"
        ]
        is True
        and physical_sm_vector_rxi["direction_census"][
            "total_broken_real_directions"
        ]
        == 37
        and physical_sm_vector_rxi["scope"][
            "background_covariant_heat_kernel_matching_coefficient"
        ]
        is False
        and physical_sm_vector_rxi["scope"][
            "sector_resolved_general_background_gauge_determinants"
        ]
        is False
        and physical_sm_vector_rxi["scope"]["one_loop_vector_pole_masses"]
        is False
        and physical_sm_vector_rxi["scope"]["physical_G6"] is False
        and physical_sm_vector_rxi["scope"]["physical_G7"] is False,
        "physical-SM Rxi vacuum cancellation drifted or promoted general-background/pole/full G6/G7",
    )
    require(
        physical_sm_g6_g7_frontier["status"]
        == "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_AND_NONIDENTIFIABILITY_CLOSED__PHYSICAL_G6_G7_REMAIN_OPEN"
        and physical_sm_g6_g7_frontier["core_sha256"]
        == PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_g6_g7_closure_frontier_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G6_G7_FRONTIER_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_g6_g7_closure_frontier_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G6_G7_FRONTIER_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G6_G7_FRONTIER_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G6_G7_FRONTIER_MD_RAW_SHA256
        and physical_sm_g6_g7_frontier["scope"][
            "continuous_nonidentifiability_proved"
        ]
        is True
        and physical_sm_g6_g7_frontier["scope"][
            "minimal_closure_path_machine_readable"
        ]
        is True
        and len(physical_sm_g6_g7_frontier["minimal_closure_path"]) == 7
        and physical_sm_g6_g7_frontier["scope"]["unique_pole_spectrum"]
        is False
        and physical_sm_g6_g7_frontier["scope"]["unique_threshold_vector"]
        is False
        and physical_sm_g6_g7_frontier["scope"]["unique_full_RGE_trajectory"]
        is False
        and physical_sm_g6_g7_frontier["scope"]["physical_G6"] is False
        and physical_sm_g6_g7_frontier["scope"]["physical_G7"] is False
        and physical_sm_g6_g7_frontier["scope"]["release_G6"] is False
        and physical_sm_g6_g7_frontier["scope"]["release_G7"] is False,
        "physical-SM G6/G7 closure frontier drifted or promoted a nonidentified/full gate",
    )
    require(
        physical_sm_g8_frontier["status"]
        == "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_CLOSED__PHYSICAL_RELEASE_AUTHORITATIVE_G8_OPEN"
        and physical_sm_g8_frontier["core_sha256"]
        == PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
        and hashlib.sha256(
            (ROOT / "exact_physical_sm_g8_identifiability_frontier_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G8_FRONTIER_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_exact_physical_sm_g8_identifiability_frontier_v20.py").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G8_FRONTIER_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G8_FRONTIER_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md").read_bytes()
        ).hexdigest()
        == PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256
        and physical_sm_g8_frontier["n_failed"] == 0
        and physical_sm_g8_frontier["failures"] == []
        and all(physical_sm_g8_frontier["checks"].values())
        and len(physical_sm_g8_frontier["acceptance_matrix"]) == 5
        and all(
            row["passed"] is False
            for row in physical_sm_g8_frontier["acceptance_matrix"].values()
        )
        and physical_sm_g8_frontier["scope"][
            "continuous_absolute_scale_nonidentifiability_proved"
        ]
        is True
        and physical_sm_g8_frontier["scope"][
            "flavor_and_interference_nonidentifiability_audited"
        ]
        is True
        and physical_sm_g8_frontier["scope"][
            "unique_proton_lifetime_or_distribution"
        ]
        is False
        and physical_sm_g8_frontier["scope"]["physical_G8"] is False
        and physical_sm_g8_frontier["scope"]["release_G8"] is False
        and physical_sm_g8_frontier["scope"]["authoritative_G8"] is False
        and physical_sm_g8_frontier["scope"][
            "negative_no_go_for_future_G8_closure"
        ]
        is False
        and physical_sm_g8_frontier["repository_frozen_experimental_input"][
            "current_PDG_review_numeric_verification_performed"
        ]
        is True
        and physical_sm_g8_frontier["repository_frozen_experimental_input"][
            "complete_live_all_channel_limit_verification_performed"
        ]
        is False,
        "physical-SM G8 identifiability frontier drifted or promoted a conditional/nonidentified prediction",
    )
    legacy_flags = legacy_so10_210_beta_diagnostic.get("flag", {})
    require(
        legacy_so10_210_beta_diagnostic.get("status")
        == "CORRECTED_SO10_NONYUKAWA_GAUGE_POLYNOMIAL__FULL_G7_OPEN"
        and legacy_so10_210_beta_diagnostic.get("n_checks") == 11
        and legacy_so10_210_beta_diagnostic.get("n_failed") == 0
        and legacy_so10_210_beta_diagnostic.get("failures") == []
        and legacy_so10_210_beta_diagnostic.get("content", {})
        .get("casimirs", {})
        .get("16")
        == 45.0 / 8.0
        and hashlib.sha256(
            (ROOT / "sarah_pyrate_so10_210_betas_v20.py").read_bytes()
        ).hexdigest()
        == LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "test_sarah_pyrate_so10_210_betas_v20.py").read_bytes()
        ).hexdigest()
        == LEGACY_SO10_210_BETA_DIAGNOSTIC_TEST_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json").read_bytes()
        ).hexdigest()
        == LEGACY_SO10_210_BETA_DIAGNOSTIC_JSON_RAW_SHA256
        and hashlib.sha256(
            (ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20.md").read_bytes()
        ).hexdigest()
        == LEGACY_SO10_210_BETA_DIAGNOSTIC_MD_RAW_SHA256
        and legacy_flags.get("sarah_validated_210_betas") is False
        and legacy_flags.get("live_sarah_or_pyrate_executable_run") is False
        and legacy_flags.get("two_loop_so10_gauge_complete_for_content") is False
        and legacy_flags.get("two_loop_so10_nonyukawa_gauge_polynomial_complete")
        is True
        and legacy_flags.get("two_loop_quartic_betas_complete") is False
        and legacy_flags.get("exact_unique_proton_lifetime") is False
        and legacy_flags.get("whole_model_excluded") is False
        and legacy_flags.get("pyrate_sarah_mv_formulas_ingested") is True
        and "remain OPEN" in legacy_so10_210_beta_diagnostic.get("verdict", "")
        and "full SARAH/PyR@TE scalar sector"
        in " ".join(
            legacy_so10_210_beta_diagnostic.get("next_exact_calculation", [])
        ),
        "legacy SO(10)+210 diagnostic drifted or promoted full physical/mathematical/release G7",
    )
    candidate_coefficients = g3_candidate["coefficient_vector"]
    require(
        g3_candidate["n_failed"] == 0
        and candidate_coefficients["nonzero_count"] == 27
        and candidate_coefficients["maximum_absolute_coefficient"] == 73 / 8
        and candidate_coefficients["symbolic_nonzero"][
            "lambda::O48_B01_Phi_self_quartics"
        ]
        == "-21/200"
        and g3_candidate["flags"][
            "positive_J0_normalization_is_without_loss_of_generality"
        ]
        is False
        and g3_candidate["flags"][
            "P_plus_Delta_Qsqrt2_component_LDL_conditional"
        ]
        is False
        and g3_candidate["flags"][
            "A_square_recoupling_exactly_source_bound"
        ]
        is True
        and g3_candidate["flags"]["complete_potential_BFB_exactly_certified"]
        is True
        and g3_candidate["flags"][
            "selected_vacuum_stationarity_exactly_compiler_certified"
        ]
        is True
        and g3_candidate["flags"]["full_448_kernel_count_conditional"] is False
        and g3_candidate["flags"][
            "P_plus_Delta_source_binding_exactly_certified"
        ]
        is True
        and g3_candidate["flags"]["full_448_kernel_count_exact"] is True
        and g3_candidate["flags"]["full_448_PSD_feasibility_certified"] is True
        and g3_candidate["flags"]["strict_local_minimum_certified"] is True
        and g3_candidate["flags"][
            "selected_vacuum_global_minimum_certified"
        ]
        is False
        and g3_candidate["flags"][
            "selected_vacuum_global_minimum_disproved"
        ]
        is True
        and g3_candidate["flags"][
            "exact_lower_energy_field_witness_certified"
        ]
        is True
        and g3_candidate["flags"]["constructive_candidate_rejected_for_G3"]
        is True
        and g3_candidate["flags"]["selected_vacuum_unique_modulo_symmetry"]
        is False
        and g3_candidate["flags"]["G3_closed"] is False,
        "constructive exact local G3 candidate failed or was globally over-promoted",
    )
    require(gauged_g3["n_failed"] == 0, "gauged U(1)_X G3 audit failed")
    require(
        gauged_g3["status"]
        == "G3_SELECTED_VACUUM_REJECTED_BY_EXACT_GLOBAL_COUNTEREXAMPLE"
        and gauged_g3["overall_state"] == "OPEN",
        "gauged U(1)_X G3 exact global-counterexample state changed",
    )
    require(
        gauged_g3["coverage"]["invariant_directions"] == 44
        and gauged_g3["coverage"]["real_parameters"] == 51
        and gauged_g3["coverage"]["real_field_dimension"] == 486
        and gauged_g3["coverage"]["gauge_quotient_dimension_including_axion"]
        == 449
        and gauged_g3["coverage"]["massive_transverse_quotient_dimension"]
        == 448,
        "gauged U(1)_X G3 dimensions changed",
    )
    require(
        gauged_g3["flags"][
            "gauge_quotient_dimension_449_including_axion_certified"
        ]
        is True
        and gauged_g3["flags"][
            "massive_transverse_quotient_dimension_448_certified"
        ]
        is True
        and gauged_g3["flags"]["stationarity_rank_13_exactly_certified"] is True
        and gauged_g3["flags"]["stationarity_nullity_38_exactly_certified"]
        is True
        and gauged_g3["flags"][
            "exact_three_structural_zero_gradient_certificates"
        ]
        is True
        and gauged_g3["flags"][
            "G3_exact_informed_13_row_constraints_ready"
        ]
        is True
        and gauged_g3["flags"][
            "legacy_reference_equilibrated_common_kernel_135_invalidated"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_sparse_27_parameter_candidate_found"
        ]
        is True
        and gauged_g3["flags"][
            "historical_positive_J0_normalization_invalidated"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_candidate_conditional_rank448_evidence"
        ]
        is False
        and gauged_g3["flags"][
            "constructive_candidate_direct_exact_source_binding"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_candidate_exact_rank448_certificate"
        ]
        is True
        and gauged_g3["flags"]["G3_fixed_vacuum_strict_minimum_certified"]
        is True
        and gauged_g3["flags"]["G3_fixed_vacuum_PSD_feasible_certified"]
        is True
        and gauged_g3["flags"]["complete_potential_BFB"] is True
        and gauged_g3["flags"][
            "G3_selected_vacuum_global_no_go_certified"
        ]
        is True
        and gauged_g3["flags"][
            "exact_lower_energy_field_witness_certified"
        ]
        is True
        and gauged_g3["flags"]["constructive_candidate_rejected_for_G3"]
        is True
        and gauged_g3["flags"]["global_competing_extrema_exhausted"] is False
        and gauged_g3["flags"]["G3_closed"] is False
        and gauged_g3["flags"]["whole_model_validated"] is False
        and gauged_g3["flags"]["whole_model_excluded"] is False,
        "gauged U(1)_X G3 scope was over-promoted",
    )
    corrected = corrected_common_kernel["corrected_common_kernel_diagnostic"]
    require(
        corrected_common_kernel["n_failed"] == 0
        and corrected_common_kernel["overall_state"] == "OPEN"
        and corrected_common_kernel["flags"][
            "legacy_common_kernel_dimension_135_invalidated"
        ]
        is True
        and corrected_common_kernel["flags"][
            "exact_H6_radial_flat_direction_refuted"
        ]
        is True
        and corrected["corrected_common_kernel"]["rank"] == 448
        and corrected["corrected_common_kernel"]["nullity"] == 0
        and corrected["proof_grade"] is False
        and corrected["certified_PSD_feasibility"] is False
        and corrected["certified_no_go"] is False,
        "corrected G3 common-kernel evidence changed scope",
    )
    canonical_integrity = authoritative_gate._canonical_evidence_complete(
        canonical_v21
    )
    canonical_closed = bool(
        canonical_integrity
        and canonical_v21["closure_counts"] == {"closed": 8, "open": 0}
        and canonical_v21["overall_state"] == "PASS"
        and canonical_v21["classification"]["whole_model_validated"] is True
    )
    first_three_closed = all(
        row["closed"] is True
        for row in canonical_v21["gates"]
        if row["gate_number"] <= 3
    )
    expected_state = "PASS" if canonical_closed else "BLOCKED"
    require(
        canonical_integrity
        and canonical_v21["n_failed"] == 0
        and canonical_v21["classification"][
            "legacy_bare_gate_numbers_authoritative"
        ]
        is False,
        "canonical V21 G1-G8 producer integrity failed",
    )
    require(
        authoritative["canonical_g1_g8"] == canonical_v21
        and authoritative["canonical_g1_g8_summary"]
        == canonical_v21["closure_counts"]
        and authoritative["classification"]["all_g1_g8_closed"]
        is canonical_closed
        and authoritative["classification"]["whole_model_validated"]
        is canonical_closed
        and authoritative["flag"][
            "legacy_ledger_controls_authoritative_closure"
        ]
        is False
        and authoritative["legacy_g1_g8_evidence"][
            "authoritative_for_closure"
        ]
        is False,
        "authoritative full-model report disagrees with canonical V21 state",
    )
    require(
        matrix["canonical_G1_G8_V21"] == canonical_v21
        and matrix["canonical_authoritative_consistency"][
            "authoritative_report_matches_canonical_state"
        ]
        is True
        and matrix["overall_state"] == expected_state
        and matrix["full_theory_validated"] is canonical_closed,
        "validation matrix disagrees with canonical-authoritative state",
    )
    require(
        ultimate["canonical_G1_G8_V21"] == canonical_v21
        and ultimate["canonical_authoritative_consistency"][
            "authoritative_report_matches_canonical_state"
        ]
        is True
        and ultimate["overall_state"] == expected_state
        and ultimate["internal_candidate_approved"] is first_three_closed
        and ultimate["full_phenomenology_approved"] is canonical_closed,
        "ultimate gate disagrees with canonical-authoritative state",
    )

    suite = unittest.defaultTestLoader.discover(str(ROOT))
    n_tests = suite.countTestCases()
    require(n_tests >= 154, f"expected at least 154 tests, found {n_tests}")
    run([sys.executable, "-m", "unittest", "-v"])
    run_pytest_with_private_basetemp(
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "test_exact_x_symmetry_consistency_gate_v20.py",
            "test_g1_exact_declared_symmetry_character_census_v20.py",
            "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "test_gauged_u1x_scalar_contract_v20.py",
            "test_gauged_u1x_g2_derivative_audit_v20.py",
            "test_exact_gauged_u1x_g2_mathematical_closure_v20.py",
            "test_canonical_g2_exact_contraction_basis_v21.py",
            "test_canonical_g2_full_component_projection_dim6_v21.py",
            "test_verify_canonical_g2_full_component_projection_dim6_v21.py",
            "test_canonical_g3_physical_ew_global_vacuum_v21.py",
            "test_verify_canonical_g3_physical_ew_global_vacuum_v21.py",
            "test_exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "test_exact_gauged_u1x_physical_quotient_v20.py",
            "test_exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
            "test_exact_gauged_u1x_g3_a_square_recoupling_v20.py",
            "test_exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
            "test_exact_gauged_u1x_g3_global_counterexample_v20.py",
            "test_exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
            "test_exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
            "test_exact_phi_zero_degree8_conductor_identity_v20.py",
            "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
            "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
            "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "test_corrected_rank1_endpoint_v21.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "test_exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
            "test_final_g3_eft_acceptance_gate_v20.py",
            "test_final_g4_eft_mathematical_gate_v20.py",
            "test_final_g5_eft_mathematical_gate_v20.py",
            "test_exact_eft_physical_scalar_spectrum_v20.py",
            "test_exact_g6_sm_provenance_feasibility_v20.py",
            "test_conditional_physical_sm_eft_hessian_spectrum_v20.py",
            "test_exact_eft_g6_g7_parameterized_matching_v20.py",
            "test_final_g6_eft_mathematical_gate_v20.py",
            "test_exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "test_exact_physical_sm_heavy_vector_masses_v20.py",
            "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
            "test_exact_physical_sm_g6_g7_closure_frontier_v20.py",
            "test_exact_physical_sm_g8_identifiability_frontier_v20.py",
            "test_sarah_pyrate_so10_210_betas_v20.py",
            "test_physical_sm_source_algebra_equality_frontier_v20.py",
            "test_exact_physical_sm_five_amplitude_equality_v20.py",
            "test_exact_physical_sm_hard_projector_hessians_v20.py",
            "test_exact_physical_sm_easy_21_hessians_v20.py",
            "test_exact_physical_sm_last_six_hessians_v20.py",
            "test_exact_physical_sm_37_row_aggregate_v20.py",
            "test_exact_physical_sm_local_equality_orbit_v20.py",
            "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py",
            "test_pyrate3_so10_u1x_gauge_beta_replay_v20.py",
            "test_exact_normalized_so10_yukawa_cgcs_v20.py",
            "test_exact_eft_g7_threshold_nonidentifiability_v20.py",
            "test_exact_physical_g7_component_threshold_contract_v20.py",
            "test_physical_sm_vacuum_local_feasibility_v20.py",
            "test_g1_g8_gate_ledger_v20.py",
            "test_final_g3_acceptance_gate_v20.py",
            "test_gauged_u1x_g3_sos_candidate_v20.py",
            "test_gauged_u1x_g3_stability_v20.py",
            "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
            "test_g1_g8_execution_roadmap_v20.py",
            "test_theory_validation_matrix_v20.py",
            "test_replicate_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "--check",
        ]
    )

    # Build the manuscript out of tree: the committed PDF is frozen by the
    # corrected-endpoint integration manifest and SHA256SUMS, so validation
    # must never rewrite its bytes.
    pdflatex = shutil.which("pdflatex")
    require(pdflatex is not None, "pdflatex is required")
    with tempfile.TemporaryDirectory(prefix="so10-latex-") as latex_directory:
        build_root = Path(latex_directory)
        miktex_install = Path(pdflatex).resolve().parents[3]
        miktex_config = build_root / "miktex-config"
        miktex_data = build_root / "miktex-data"
        miktex_config.mkdir()
        miktex_data.mkdir()
        miktex_startup = build_root / "miktexstartup.ini"
        miktex_startup.write_text(
            "[Setup]\n"
            "Version=26.2\n"
            "[Auto]\n"
            "Config=Portable\n"
            "[Paths]\n"
            f"CommonConfig={miktex_config.as_posix()}\n"
            f"CommonData={miktex_data.as_posix()}\n"
            f"CommonInstall={miktex_install.as_posix()}\n"
            f"UserConfig={miktex_config.as_posix()}\n"
            f"UserData={miktex_data.as_posix()}\n"
            f"UserInstall={miktex_install.as_posix()}\n",
            encoding="utf-8",
        )
        miktex_environment = {
            "MIKTEX_COMMONSTARTUPFILE": str(miktex_startup),
            "MIKTEX_USERSTARTUPFILE": str(miktex_startup),
        }
        latex = [
            pdflatex,
            "--disable-installer",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build_root}",
            TEX.name,
        ]
        built_pdf = build_root / PDF.name
        built_log = build_root / LOG.name
        run(latex, environment_overrides=miktex_environment)
        run(latex, environment_overrides=miktex_environment)
        stable = hashlib.sha256(built_pdf.read_bytes()).hexdigest()
        run(latex, environment_overrides=miktex_environment)
        rebuilt = hashlib.sha256(built_pdf.read_bytes()).hexdigest()
        require(
            rebuilt == stable, "PDF is not byte-reproducible after stabilization"
        )

        forbidden = (
            "LaTeX Warning",
            "Package hyperref Warning",
            "Overfull \\hbox",
            "Underfull \\hbox",
            "Overfull \\vbox",
            "Underfull \\vbox",
            "undefined references",
            "multiply defined",
        )
        log_text = built_log.read_text(errors="replace")
        hits = [marker for marker in forbidden if marker in log_text]
        require(not hits, f"LaTeX log defects: {hits}")
        require(built_pdf.read_bytes()[:5] == b"%PDF-", "invalid PDF header")
        require(built_pdf.stat().st_size > 100_000, "PDF unexpectedly small")

        pdfinfo = shutil.which("pdfinfo")
        require(pdfinfo is not None, "pdfinfo is required")
        pdfinfo_environment = os.environ.copy()
        pdfinfo_environment.update(miktex_environment)
        metadata = subprocess.run(
            [pdfinfo, str(built_pdf)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
            env=pdfinfo_environment,
        ).stdout
        require(
            "Pages:           14" in metadata,
            "expected a fourteen-page manuscript",
        )
    require(PDF.read_bytes()[:5] == b"%PDF-", "invalid frozen PDF header")
    require(PDF.stat().st_size > 100_000, "frozen PDF unexpectedly small")

    core = [
        ROOT / "README.md",
        ROOT / "REFEREE_AUDIT_v20.md",
        ROOT / "V20_ERROR_AUDIT.md",
        TEX,
        PDF,
        ROOT / "decay_safe_completion_v20.py",
        ROOT / "decay_threshold_v20.py",
        ROOT / "audit_v20_errors.py",
        ROOT / "physics_push_v20.py",
        ROOT / "full_fermion_matching_v20.py",
        ROOT / "portal_tensors_abcd_v20.py",
        ROOT / "physical_cf_matching_v20.py",
        ROOT / "global_flavour_fit_v20.py",
        ROOT / "cmb_public_data_pipeline_v20.py",
        ROOT / "empirical_roadmap_lock_v20.py",
        ROOT / "next_phenomenology_lock_v20.py",
        ROOT / "close_open_gaps_v20.py",
        ROOT / "verify_tan_beta_profile_semantics.py",
        ROOT / "tan_beta_profile_v20.py",
        ROOT / "reanalysis_portal_beta_v20.py",
        ROOT / "FERMION_PORTAL_CURRENT_THEOREM.md",
        ROOT / "FULL_FERMION_MATCHING_V20_VERDICT.json",
        ROOT / "PORTAL_TENSORS_ABCD_V20_VERDICT.json",
        ROOT / "PHYSICAL_CF_MATCHING_V20_VERDICT.json",
        ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        ROOT / "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
        ROOT / "EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json",
        ROOT / "NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json",
        ROOT / "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
        ROOT / "TAN_BETA_PROFILE_V20_VERDICT.json",
        ROOT / "V20_PORTAL_BETA_REANALYSIS_VERDICT.json",
        ROOT / "models" / "SO10Z17AxionV20.m",
        ROOT / "models" / "EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json",
        ROOT / "models" / "SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json",
        ROOT / "tools" / "validate-exact-x-model.wls",
        ROOT / "run_exact_x_sarah_validation_v20.py",
        ROOT / "models" / "SO10Z17AxionV20_pyrate.yaml",
        ROOT / "exact_x_symmetry_consistency_gate_v20.py",
        ROOT / "sarah_pyrate_210n_model_file_v20.py",
        ROOT / "test_sarah_pyrate_210n_model_file_v20.py",
        ROOT / "SARAH_PYRATE_MODEL_FILE_V20_VERDICT.json",
        ROOT / "SARAH_PYRATE_MODEL_FILE_V20.md",
        ROOT / "gauged_u1x_scalar_contract_v20.py",
        ROOT / "gauged_u1x_g2_derivative_audit_v20.py",
        ROOT / "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        ROOT / "exact_gauged_u1x_physical_quotient_v20.py",
        ROOT / "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
        ROOT / "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        ROOT / "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        ROOT / "exact_gauged_u1x_g3_global_counterexample_v20.py",
        ROOT / "exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        ROOT / "final_g3_acceptance_gate_v20.py",
        ROOT / "gauged_u1x_g3_sos_candidate_v20.py",
        ROOT / "gauged_u1x_g3_stability_v20.py",
        ROOT / "gauged_u1x_g3_corrected_common_kernel_v20.py",
        ROOT / "test_gauged_u1x_g3_stability_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_global_counterexample_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        ROOT / "test_final_g3_acceptance_gate_v20.py",
        ROOT / "test_replicate_v20.py",
        ROOT / "test_gauged_u1x_g3_sos_candidate_v20.py",
        ROOT / "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
        ROOT / "g1_g8_gate_ledger_v20.py",
        ROOT / "g1_g8_execution_roadmap_v20.py",
        ROOT / "authoritative_full_model_gate_v20.py",
        ROOT / "theory_validation_matrix_v20.py",
        ROOT / "theory_confirmation_verdict_v20.py",
        ROOT / "ultimate_theory_gate_v20.py",
        ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json",
        ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
        ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.md",
        ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.json",
        ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.md",
        ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
        ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.md",
        ROOT / "GAUGED_U1X_G3_STABILITY_V20.json",
        ROOT / "GAUGED_U1X_G3_STABILITY_V20.md",
        ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json",
        ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.md",
        ROOT / "G1_G8_GATE_LEDGER_V20.json",
        ROOT / "G1_G8_EXECUTION_ROADMAP_V20.json",
        ROOT / "AUTHORITATIVE_FULL_MODEL_GATE_V20.json",
        ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json",
        ROOT / "THEORY_CONFIRMATION_VERDICT.json",
        ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json",
        V20_ENGINE,
        V20_VERDICT,
        ROOT / "test_decay_safe_completion_v20.py",
        ROOT / "test_decay_threshold_v20.py",
        ROOT / "test_audit_v20_errors.py",
        ROOT / "test_physics_push_v20.py",
        ROOT / "test_gauged_u1x_g2_derivative_audit_v20.py",
        ROOT / "test_exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        ROOT / "test_exact_gauged_u1x_physical_quotient_v20.py",
        ROOT / "so10_axion_v17_engine.py",
        V17_VERDICT,
        ROOT / "so10_axion_v19_engine.py",
        V19_VERDICT,
        ROOT / "requirements.txt",
        Path(__file__),
    ]
    core.extend(ROOT / relative for relative in FINAL_THEOREM_CORE_PATHS)
    external_model_attestation = (
        ROOT / "models" / "EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"
    )
    if external_model_attestation.exists():
        core.append(external_model_attestation)
    require(all(path.exists() for path in core), "release core is incomplete")
    committed_sums = (ROOT / "SHA256SUMS").read_text(encoding="utf-8")
    write_checksums(core)
    regenerated_sums = (ROOT / "SHA256SUMS").read_text(encoding="utf-8")
    if regenerated_sums != committed_sums:
        drifted = sorted(
            {
                line.split("  ", 1)[1]
                for line in (
                    set(regenerated_sums.splitlines())
                    ^ set(committed_sums.splitlines())
                )
            }
        )
        require(
            False,
            "release checksum regeneration drifted from the frozen "
            f"SHA256SUMS entries: {drifted}",
        )
    print(
        f"RELEASE GATE PASS: v17 65/65; v19 59/59; v20 42/42; "
        f"tests {n_tests}/{n_tests}; clean 14-page PDF; scientific state "
        f"{'PASS' if canonical_closed else 'BLOCKED'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
