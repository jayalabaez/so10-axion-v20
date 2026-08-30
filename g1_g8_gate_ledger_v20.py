#!/usr/bin/env python3
"""Contract-aware, fail-closed G1-G8 ledger for the v20 candidate.

The manuscript's gauged U(1)_X contract is authoritative.  The repository now
contains a statically consistent, tool-native SARAH input for that gauge
contract and a genuine hash-bound Wolfram/SARAH v3 execution attestation.
The authoritative G1 scope is therefore closed.  The former
64-direction/91-parameter G1/G2 calculations and
their 449-dimensional G3 quotient remain valuable, but only as explicitly
scoped historical Option-C subtheorems.

Scientific blocking is not an audit execution failure: a correct current
report has ``n_failed=0``, ``overall_state=BLOCKED``, and no closed gates.  The
exact-X 44-direction/51-parameter multiplicity census, the source-bound
component-tensor G1 ring, and the complete source-bound mathematical G2
component potential are closed subtheorems. Their authoritative promotion
remains fail-closed on the external SARAH execution attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as exact_x
import g1_exact_declared_symmetry_character_census_v20 as gauged_g1
import gauged_u1x_g2_derivative_audit_v20 as gauged_g2
import nonsusy_z17_pq_potential_filter_v20 as gauged_filter
import live_g1_tensor_closure_ledger_v20 as historical_g1
import live_g2_derivative_coverage_ledger_v20 as historical_g2
import g3_full_hessian_classification_v20 as historical_g3_hessian
import g3_stationary_stability_search_v20 as historical_g3_search
import corrected_rank1_endpoint_v21 as corrected_rank1

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "G1_G8_GATE_LEDGER_V20.md"
EXACT_X_V3_SOURCE = ROOT / "exact_x_symmetry_consistency_gate_v20.py"
EXACT_X_V3_TEST = ROOT / "test_exact_x_symmetry_consistency_gate_v20.py"
EXACT_X_V3_JSON = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"
EXACT_X_V3_MD = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md"
EXACT_X_V3_INPUT_MANIFEST = (
    ROOT / "models" / "EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json"
)
EXACT_X_V3_TRUSTED_SARAH_MANIFEST = (
    ROOT / "models" / "SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"
)
EXACT_X_V3_SOURCE_RAW_SHA256 = (
    "5c70efb039b795f94a6b03e8681ad512af837c48f4496948f918eae7faa529d8"
)
EXACT_X_V3_TEST_RAW_SHA256 = (
    "9397d65593994f9267845e08d92235a9b934cdea7053dcc7292c8c1f752253ee"
)
EXACT_X_V3_JSON_RAW_SHA256 = (
    "c0393187fc07848a218830cc23cd59c1ecaaa091ea004f59b3777370ffcef2fa"
)
EXACT_X_V3_MD_RAW_SHA256 = (
    "d6c3d3cf2e38542206e8963c91190dfa377a0a3fa697292e576caa6faf3a2a49"
)
EXACT_X_V3_INPUT_MANIFEST_RAW_SHA256 = (
    "1a6c8f8d79186801c840ddb63c30ee518b73c1929642be2139a7d01ed8c41a2f"
)
EXACT_X_V3_TRUSTED_SARAH_MANIFEST_RAW_SHA256 = (
    "c28f08d56a488050b96ce3491473f22fe1b673aad8ac3ac3d0e590dd60e70d91"
)
EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256 = (
    "de92b2de859efa7a0c4f5fdfb642d9f1ff8e1b071057bc8d4c295f6e2b6f8337"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE = (
    ROOT / "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256 = (
    "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256 = (
    "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f"
)
RENORMALIZABLE_G1_DIRECTION_MAP_SHA256 = (
    "657b739208f46ece75bfed977aa30ce1baa25f7aeed861b81007e81c7551684d"
)
RENORMALIZABLE_G2_MATHEMATICAL_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
)
RENORMALIZABLE_G2_MATHEMATICAL_SOURCE = (
    ROOT / "exact_gauged_u1x_g2_mathematical_closure_v20.py"
)
# Replaced by the terminal producer pins after downstream integration is
# complete.  Keeping explicit constants makes every consumer fail closed.
RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256 = (
    "eb11744d0dbc9ceb883e8a6063177d8e3e370b1dcdc2c4e3eba97541b53d8fc4"
)
RENORMALIZABLE_G2_MATHEMATICAL_RAW_SHA256 = (
    "de105a206685a236dcddc4cb70d98d756d87b9641e02150c41493897e01f7ff0"
)
RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256 = (
    "5f56a55a7c9597918c530ad6c77252ed161a206ad0dffbf25651e32f4f590a8b"
)
G3_SOS_JSON = ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json"
G3_PD_JSON = ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
G3_A_SQUARE_JSON = ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json"
G3_SOS_BFB_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json"
G3_KERNEL_BOUND_JSON = ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json"
G3_REPLACEMENT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json"
G3_SU5_PD_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json"
G3_SU5_HSX_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
G3_SU5_HSX_EXACT_HESSIAN_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
)
G3_SU5_EQUALITY_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
G3_SU5_PHI_ORBIT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
G3_SU5_PHI_LOCAL_COMPONENT_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
)
G3_SU5_PHI_SU3_SLICE_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json"
)
G3_SU5_GAP_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
G3_ALTERNATIVE_GLOBAL_SOS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
)
FINAL_G3_EFT_ACCEPTANCE_JSON = ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256 = (
    "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0"
)
FINAL_G4_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)
FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256 = (
    "98664542a4e1bbfba233652737826b974963a31c2e86a15e2d73fda1457d987b"
)
FINAL_G5_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256 = (
    "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
)
FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256 = (
    "6d6e4fd9932a03e35146afb1bca850666e883aaed5e23b73b81f0f703e4e7db9"
)
FINAL_G6_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G6_EFT_GATE_SOURCE = ROOT / "final_g6_eft_mathematical_gate_v20.py"
FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256 = (
    "3b06ae240c7fce18723f0ce77966e894e688dee65f56859239ff5cf552b1323c"
)
FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256 = (
    "8bd98401ed6e2540ae7968a5b6a51a8e49abd98943252dec159c873d73a13f6c"
)
FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256 = (
    "16eba20b834ebca25b3a8b91d867ddee76b1676791b18aa86db32a6ebc77af4e"
)
FINAL_G6_EFT_SPECTRUM_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256 = (
    "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36"
)
FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256 = (
    "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416"
)
EFT_G7_NONIDENTIFIABILITY_JSON = (
    ROOT / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
)
EFT_G7_NONIDENTIFIABILITY_SOURCE = (
    ROOT / "exact_eft_g7_threshold_nonidentifiability_v20.py"
)
# Provisional pins are replaced once every integration flag is promoted.
EFT_G7_NONIDENTIFIABILITY_CORE_SHA256 = (
    "93a8ea1abeb3cec2521cb043057b29646bd9c368f8e8bcc7e2d819f42a7dc741"
)
EFT_G7_NONIDENTIFIABILITY_RAW_SHA256 = (
    "778f96c8760a43be5214b215e08a6308d6198b84ebff9edd7729e75203b13cae"
)
EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256 = (
    "16e4a011e759df3a31664bcac2711b5270598551f1e2791c8f629f9bb6483406"
)
G6_SM_PROVENANCE_JSON = ROOT / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json"
G6_SM_PROVENANCE_SOURCE = ROOT / "exact_g6_sm_provenance_feasibility_v20.py"
# Replaced by the terminal producer pins before reports are regenerated.  The
# sentinel values deliberately keep every physical G6 consumer fail closed.
G6_SM_PROVENANCE_CORE_SHA256 = (
    "0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39"
)
G6_SM_PROVENANCE_RAW_SHA256 = (
    "a8daa4fb1dadbea48b25ad671a18f8d467384979769772be628a43f75054f6fa"
)
G6_SM_PROVENANCE_SOURCE_RAW_SHA256 = (
    "8bb67fb09c1cd3b57bf2c02e9ed7f1242a955c5a81ceb7d44dd48435c82618c1"
)
G6_G7_PARAMETERIZED_MATCHING_JSON = (
    ROOT / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json"
)
G6_G7_PARAMETERIZED_MATCHING_SOURCE = (
    ROOT / "exact_eft_g6_g7_parameterized_matching_v20.py"
)
G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256 = (
    "0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f"
)
G6_G7_PARAMETERIZED_MATCHING_RAW_SHA256 = (
    "b1bbf35b23a272eadc0a8520f0dac32fb342c7f1f3886088db2d9158acfd5ae9"
)
G6_G7_PARAMETERIZED_MATCHING_SOURCE_RAW_SHA256 = (
    "4653653de5f7f29b8dd12b7a3d1e387aafab2a193137c08dc2e4be942dceee42"
)
AUTHORITATIVE_GAUGE_BETAS_JSON = (
    ROOT / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json"
)
AUTHORITATIVE_GAUGE_BETAS_SOURCE = (
    ROOT / "exact_authoritative_so10_u1x_gauge_betas_v20.py"
)
AUTHORITATIVE_GAUGE_BETAS_CORE_SHA256 = (
    "714796e4e8f1aa768d9e9f8434c6919aca854d33541b2bccc779f96933345752"
)
AUTHORITATIVE_GAUGE_BETAS_RAW_SHA256 = (
    "f5c12e8b8f9ec40976f675a743d5fd5d8cf4e98ab2087d92e3cf855c756c75eb"
)
AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256 = (
    "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6"
)
PYRATE3_GAUGE_REPLAY_JSON = ROOT / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json"
PYRATE3_GAUGE_REPLAY_SOURCE = ROOT / "pyrate3_so10_u1x_gauge_beta_replay_v20.py"
PYRATE3_GAUGE_REPLAY_MODEL = ROOT / "models" / "SO10U1XGaugeAuditV20.model"
PYRATE3_GAUGE_REPLAY_DATA = (
    ROOT / "data" / "PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json"
)
PYRATE3_GAUGE_REPLAY_CORE_SHA256 = (
    "63f097be00c5da69982909b79b5ac9c64c1080efa142ae5d419820fb260cbccf"
)
PYRATE3_GAUGE_REPLAY_RAW_SHA256 = (
    "e17dcc1dc939c8475b6827f4c781f3f5fce6c728cf5aa6511287066087b01fd4"
)
PYRATE3_GAUGE_REPLAY_SOURCE_RAW_SHA256 = (
    "74b70c7d403bd5fc1cefc30ab1a58dd5c6e74c99672c81e9b2a2c59e34a1c42a"
)
PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256 = (
    "18191bc9db705ed9e8a89eff214ad967bac37830c91fede82c418d38ce0c949e"
)
PYRATE3_GAUGE_REPLAY_DATA_RAW_SHA256 = (
    "047632c3e81f8eb2dcc1cd922b8d3e34c300743693e18606ff8953e28ccd280b"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_JSON = (
    ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_MD = (
    ROOT / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE = (
    ROOT / "exact_physical_g7_component_threshold_contract_v20.py"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_TEST = (
    ROOT / "test_exact_physical_g7_component_threshold_contract_v20.py"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256 = (
    "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_SHA256 = (
    "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256 = (
    "23b78d68d4732da2160d7b3911aa3ac0c7e6f9bce59e58228d4a6c755b21d071"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256 = (
    "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256 = (
    "bdceea8f8e10f566119793c0e0cfc31316bd9704aab89a1b70a9fdc880f7cd4a"
)
NORMALIZED_YUKAWA_CGCS_JSON = ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json"
NORMALIZED_YUKAWA_CGCS_MD = ROOT / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md"
NORMALIZED_YUKAWA_CGCS_SOURCE = ROOT / "exact_normalized_so10_yukawa_cgcs_v20.py"
NORMALIZED_YUKAWA_CGCS_TEST = ROOT / "test_exact_normalized_so10_yukawa_cgcs_v20.py"
NORMALIZED_YUKAWA_CGCS_CORE_SHA256 = (
    "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7"
)
NORMALIZED_YUKAWA_CGCS_RAW_SHA256 = (
    "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b"
)
NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256 = (
    "5acbb5eb78451b8f37f1d8b990962a7ad4c39fe1974cb4720cf2131a85c14112"
)
NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256 = (
    "432faa3fdf5adebf25015f7f2fda7f040d89d86bce31f6c85b4cc56e37eb14df"
)
NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256 = (
    "450321d322634630c3a6713d16f08fbefdba71b7b2bc886f0d95dc4dcf093a02"
)
PHYSICAL_SM_VACUUM_JSON = ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json"
PHYSICAL_SM_VACUUM_MD = ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md"
PHYSICAL_SM_VACUUM_SOURCE = ROOT / "physical_sm_vacuum_local_feasibility_v20.py"
PHYSICAL_SM_VACUUM_TEST = ROOT / "test_physical_sm_vacuum_local_feasibility_v20.py"
PHYSICAL_SM_VACUUM_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)
PHYSICAL_SM_VACUUM_RAW_SHA256 = (
    "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315"
)
PHYSICAL_SM_VACUUM_MD_RAW_SHA256 = (
    "d312fb960e7a458fadf38977573315a6d0a5eee37437c49c149589abd36416c3"
)
PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256 = (
    "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c"
)
PHYSICAL_SM_VACUUM_TEST_RAW_SHA256 = (
    "3b688b8a2bd33a03e19edf4225568a3eaef96b4580f7d9ea23c38857dc069f5c"
)
PHYSICAL_SM_SOURCE_EQUALITY_JSON = (
    ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json"
)
PHYSICAL_SM_SOURCE_EQUALITY_MD = (
    ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md"
)
PHYSICAL_SM_SOURCE_EQUALITY_SOURCE = (
    ROOT / "physical_sm_source_algebra_equality_frontier_v20.py"
)
PHYSICAL_SM_SOURCE_EQUALITY_TEST = (
    ROOT / "test_physical_sm_source_algebra_equality_frontier_v20.py"
)
PHYSICAL_SM_SOURCE_EQUALITY_CORE_SHA256 = (
    "5d6f01c0ed131dcbc2813fa93f0bd81987178f2dac051e67b6db538b5a55f13d"
)
PHYSICAL_SM_SOURCE_EQUALITY_SOURCE_RAW_SHA256 = (
    "3ab97985eb2d178aa1d7b77d2c1e9e30f6134599456fce07e0a071856fc7557f"
)
PHYSICAL_SM_SOURCE_EQUALITY_TEST_RAW_SHA256 = (
    "e9d5200cbecdb22cbda4479607430f936e03e16b7c4663283abbbece99c7b770"
)
PHYSICAL_SM_SOURCE_EQUALITY_RAW_SHA256 = (
    "96d00f47eb5365dd9ff43ace871a04252aeb4b3a5d2543f03870091ff78760f2"
)
PHYSICAL_SM_SOURCE_EQUALITY_MD_RAW_SHA256 = (
    "e2d7b84c06ba706991a4bb123df3894569f2ee14f330a1b64030ab7656fce9ed"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD = (
    ROOT / "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE = (
    ROOT / "exact_physical_sm_five_amplitude_equality_v20.py"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST = (
    ROOT / "test_exact_physical_sm_five_amplitude_equality_v20.py"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256 = (
    "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE_RAW_SHA256 = (
    "777b11664047574432405373b71bf30ed473fa735bdce56ef95be43dccc76972"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST_RAW_SHA256 = (
    "23b5491460efa8bc09d4b4d978619df808f5c796baf07ae6a5aa271dd693049e"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_SHA256 = (
    "61bca8d55230b798b1d45ae4496c2b1b39490f73d0596e671478a388f72449ce"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD_RAW_SHA256 = (
    "5a22cb172ff26ac698ca19bb722590cf15368c30d37190a211e5f5f1eff214d6"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD = (
    ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE = (
    ROOT / "exact_physical_sm_hard_projector_hessians_v20.py"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST = (
    ROOT / "test_exact_physical_sm_hard_projector_hessians_v20.py"
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
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_SHA256 = (
    "b8a498926d1ba6a7f07f9c64b56443a14fba098514a8d5cb3e8358bbf7baabfa"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD_RAW_SHA256 = (
    "47b44edaa79546d294fe7d2a50ae53de764259422967356d74b79235bddc2159"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD = (
    ROOT / "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE = (
    ROOT / "exact_physical_sm_g4_g5_branch_mismatch_v20.py"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST = (
    ROOT / "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py"
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
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_SHA256 = (
    "a94429e7838141cfd7a0860faa93b0a8ee23e9b8e8985222546ce552c9debe06"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD_RAW_SHA256 = (
    "7cdde1e96c5a47da405ed3c8f89324b807a0032e087e36732d6b986e49cbba9e"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_MD = (
    ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE = (
    ROOT / "exact_physical_sm_last_six_hessians_v20.py"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_TEST = (
    ROOT / "test_exact_physical_sm_last_six_hessians_v20.py"
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
PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_SHA256 = (
    "fe1a92c3bc8e809c41abb88a85f3cf0198c88f7a70482b3f26359d6df78907c5"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_MD_RAW_SHA256 = (
    "74117a1f5c8a8add31ff82d7034dda32061fb5349b1d8662453cfcc2b266590e"
)
PHYSICAL_SM_37_ROW_AGGREGATE_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json"
)
PHYSICAL_SM_37_ROW_AGGREGATE_MD = (
    ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md"
)
PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE = (
    ROOT / "exact_physical_sm_37_row_aggregate_v20.py"
)
PHYSICAL_SM_37_ROW_AGGREGATE_TEST = (
    ROOT / "test_exact_physical_sm_37_row_aggregate_v20.py"
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
PHYSICAL_SM_37_ROW_AGGREGATE_RAW_SHA256 = (
    "66bafa7e00ce543abea0e29b8be586cca8ecb1c5417204fc0ec75f6736c984b3"
)
PHYSICAL_SM_37_ROW_AGGREGATE_MD_RAW_SHA256 = (
    "d0ddb600e27b69ad1f45af832fc4381006ef2471dfcf4b028b155b7210bb2fcd"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD = (
    ROOT / "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE = (
    ROOT / "exact_physical_sm_local_equality_orbit_v20.py"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST = (
    ROOT / "test_exact_physical_sm_local_equality_orbit_v20.py"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256 = (
    "8ddf130f5212db6e918425b093d9b68278f22154f43fc5c1734812f8057768be"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE_PORTABLE_LF_SHA256 = (
    "5358c084cd46bdf154fd42505e51d28dc75c6817d392e9bbad5b0d47c55184c7"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST_PORTABLE_LF_SHA256 = (
    "100488ad2c0173134be41ef52e17c82cc9445fc481bf922d4c36a6b7fe0b8f12"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_LF_SHA256 = (
    "4a443274dbd6e5f3887161dde5bbdb8e7410d4c951e307b7105587f99d9001c0"
)
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD_PORTABLE_LF_SHA256 = (
    "2284d1cd3666af797116d2d150963eae05be8be27420e85132f24e66de2a2ee7"
)
PHYSICAL_SM_HEAVY_VECTOR_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json"
)
PHYSICAL_SM_HEAVY_VECTOR_MD = (
    ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md"
)
PHYSICAL_SM_HEAVY_VECTOR_SOURCE = (
    ROOT / "exact_physical_sm_heavy_vector_masses_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_TEST = (
    ROOT / "test_exact_physical_sm_heavy_vector_masses_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_CORE_SHA256 = (
    "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
)
PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256 = (
    "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587"
)
PHYSICAL_SM_HEAVY_VECTOR_TEST_RAW_SHA256 = (
    "6f5bd8638cfdd593e722055f74c2de761865b4391720b1b4a11ae9089eb61b42"
)
PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256 = (
    "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0"
)
PHYSICAL_SM_HEAVY_VECTOR_MD_RAW_SHA256 = (
    "47b598aed6af33a89ecc47598d5280258e0b5304a23a8873764c9c4778768fff"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD = (
    ROOT / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE = (
    ROOT / "exact_physical_sm_heavy_vector_msbar_matching_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST = (
    ROOT / "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_CORE_SHA256 = (
    "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE_RAW_SHA256 = (
    "d6c69059b679342b0aff843044eef15e540f0c68836b41f432c878883aad3192"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST_RAW_SHA256 = (
    "e3b9118379cb6bc83e63646c4147a056f5cadc3faed13bc9c25bf42882f83b46"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256 = (
    "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD_RAW_SHA256 = (
    "130ec2f078e429cc6b19c7d9013fb803d4ffad9069a24509120f6467f9e72afe"
)
PHYSICAL_SM_VECTOR_RXI_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json"
)
PHYSICAL_SM_VECTOR_RXI_MD = (
    ROOT / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md"
)
PHYSICAL_SM_VECTOR_RXI_SOURCE = (
    ROOT / "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py"
)
PHYSICAL_SM_VECTOR_RXI_TEST = (
    ROOT / "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py"
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
PHYSICAL_SM_VECTOR_RXI_RAW_SHA256 = (
    "e1553d18c5acb9fd738dfc8c16277a634ae42bca2960296656eee57a78101221"
)
PHYSICAL_SM_VECTOR_RXI_MD_RAW_SHA256 = (
    "b549642e47656257c90b13361715c1602f202548ba4e01f068d26ffa163a4286"
)
PHYSICAL_SM_G6_G7_FRONTIER_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json"
)
PHYSICAL_SM_G6_G7_FRONTIER_MD = (
    ROOT / "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md"
)
PHYSICAL_SM_G6_G7_FRONTIER_SOURCE = (
    ROOT / "exact_physical_sm_g6_g7_closure_frontier_v20.py"
)
PHYSICAL_SM_G6_G7_FRONTIER_TEST = (
    ROOT / "test_exact_physical_sm_g6_g7_closure_frontier_v20.py"
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
PHYSICAL_SM_G6_G7_FRONTIER_RAW_SHA256 = (
    "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a"
)
PHYSICAL_SM_G6_G7_FRONTIER_MD_RAW_SHA256 = (
    "ffea781db860ee162b8a61252900c44315ae2b9afa24561e6395a1be4e16af3b"
)
PHYSICAL_SM_G8_FRONTIER_JSON = (
    ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
)
PHYSICAL_SM_G8_FRONTIER_MD = (
    ROOT / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md"
)
PHYSICAL_SM_G8_FRONTIER_SOURCE = (
    ROOT / "exact_physical_sm_g8_identifiability_frontier_v20.py"
)
PHYSICAL_SM_G8_FRONTIER_TEST = (
    ROOT / "test_exact_physical_sm_g8_identifiability_frontier_v20.py"
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
PHYSICAL_SM_G8_FRONTIER_RAW_SHA256 = (
    "bb58ef10bef730cefa8da4cee342711e1033134a5e9468febed5cc0f8a93acac"
)
PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256 = (
    "b946701143bbbf68c1a528e1ac671e65066410808c49fdb906624cff25fc5c17"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON = (
    ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD = (
    ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE = (
    ROOT / "conditional_physical_sm_eft_hessian_spectrum_v20.py"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST = (
    ROOT / "test_conditional_physical_sm_eft_hessian_spectrum_v20.py"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_CORE_SHA256 = (
    "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE_RAW_SHA256 = (
    "4d1c146f9ab9cd9679bdef7f5c145381c5d53871e62f79c1e59864a5aec981c9"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST_RAW_SHA256 = (
    "80ea03cbc4c6079e937d0a133e40ef172e3ffa72f7b2aad36d587f0b5436033d"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_RAW_SHA256 = (
    "6a4354baac91881b796e70d86e529158fe8c51a0a2a9e1dc9ba876130c3510ef"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD_RAW_SHA256 = (
    "60e5907263e06f9340d364ecd01f495b1cd470482a409f4ec6a27d86bdd6508e"
)
EFT_MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
G3_SU5_FIXED_F_OFFKERNEL_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
)
G3_RANK1_SU4_STABILIZER_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"
)
G3_RANK1_SU4_PHI210_INTERTWINERS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
)
G3_RANK1_SU4_ALIGNED_CARRIERS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
)
G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
)
RANK1_SU4_ORDERED_LABELS = (
    "H1",
    "H2",
    "H3",
    "X12",
    "Y12",
    "X13",
    "Y13",
    "X14",
    "Y14",
    "X23",
    "Y23",
    "X24",
    "Y24",
    "X34",
    "Y34",
)
RANK1_SU4_MODULAR_PRIME = 1_000_003
RANK1_SU4_BRANCHING = {
    "1": 4, "4": 4, "4bar": 4, "6": 4, "10": 1,
    "10bar": 1, "15": 2, "20": 2, "20bar": 2, "20prime": 1,
}

STATUS_CLOSED = "CLOSED"
STATUS_PARTIAL = "PARTIAL"
STATUS_OPEN = "OPEN"
STATUS_BLOCKED = "BLOCKED"

AUTHORITATIVE_CONTRACT_ID = "gauged_u1x_phi17_v20"
HISTORICAL_CONTRACT_ID = "historical_option_c_no_x_v20"
STATIC_CONTRACT_BLOCKER = exact_x.STATIC_CONTRACT_BLOCKER
CONTRACT_BLOCKER = exact_x.EXTERNAL_EXECUTION_BLOCKER
EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS = frozenset(
    {
        "anomaly_check_succeeded",
        "artifact_is_structured_json_object",
        "captured_process_log_has_all_required_pass_markers",
        "captured_process_log_has_no_fail_markers",
        "captured_process_log_is_hash_bound",
        "external_process_command_matches_tool",
        "external_process_command_recorded",
        "external_process_exit_code_zero",
        "external_process_was_executed",
        "external_tool_version_recorded",
        "gauge_invariance_check_succeeded",
        "gauge_invariance_check_was_not_disabled",
        "generated_at_is_not_in_future",
        "generated_at_is_timezone_aware",
        "input_manifest_entries_are_structured",
        "input_manifest_has_exact_required_files",
        "input_manifest_paths_are_unique",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "lagrangian_construction_succeeded",
        "legacy_v2_schema_is_not_promoted",
        "model_initialization_succeeded",
        "model_parse_succeeded",
        "model_path_is_exact_repository_model",
        "model_sha256_matches_exact_bytes",
        "model_size_matches_exact_bytes",
        "primary_model_is_bound_in_input_manifest",
        "probe_and_driver_wolfram_markers_match_runtime",
        "process_log_identifies_attested_tool_version",
        "resolved_wolfram_kernel_is_hash_bound_and_unchanged",
        "resolved_wolfram_launcher_is_hash_bound_and_unchanged",
        "runtime_probe_command_matches_contract",
        "runtime_probe_command_recorded",
        "runtime_probe_exit_code_zero",
        "runtime_probe_log_is_hash_bound",
        "sarah_source_tree_is_bound_to_command",
        "sarah_source_tree_is_exactly_trusted",
        "sarah_source_tree_was_unchanged_during_execution",
        "schema_is_supported",
        "supported_external_tool_identified",
        "tool_native_model_format_matches_path",
        "tool_release_binding_matches_repository_manifest",
        "trusted_release_manifest_matches_repository_bytes",
        "trusted_sarah_release_manifest_is_canonical",
        "trusted_sarah_release_manifest_is_input_bound",
        "validation_driver_is_bound_to_command",
        "validation_driver_matches_repository_bytes",
    }
)
EXPECTED_EXACT_X_V3_ABSENT_TRUE_CHECKS = frozenset(
    {
        "captured_process_log_has_no_fail_markers",
        "gauge_invariance_check_was_not_disabled",
        "input_manifest_paths_are_unique",
        "legacy_v2_schema_is_not_promoted",
        "trusted_sarah_release_manifest_is_canonical",
    }
)
EXPECTED_EXACT_X_V3_INPUT_MANIFEST_CHECKS = frozenset(
    {
        "artifact_is_structured_json_object",
        "files_match_exact_repository_inputs",
        "manifest_sha256_matches_exact_entries",
        "schema_is_supported",
        "trusted_sarah_release_manifest_is_canonical",
    }
)
EXPECTED_EXACT_X_V3_TRUSTED_TREE_CHECKS = frozenset(
    {
        "artifact_is_structured_json_object",
        "release_name_is_sarah",
        "release_version_is_exactly_trusted",
        "schema_is_supported",
        "source_tree_entries_are_strictly_structured",
        "source_tree_file_count_is_exactly_trusted",
        "source_tree_file_count_matches_entries",
        "source_tree_paths_are_sorted_and_unique",
        "source_tree_sha256_is_exactly_trusted",
        "source_tree_sha256_matches_entries",
        "source_tree_size_is_exactly_trusted",
        "source_tree_size_matches_entries",
        "upstream_archive_filename_is_exactly_trusted",
        "upstream_archive_sha256_is_exactly_trusted",
        "upstream_archive_size_is_exactly_trusted",
        "upstream_archive_url_is_exactly_trusted",
    }
)
EXPECTED_EXACT_X_V3_INPUT_FILES = (
    {
        "format": "sarah-mathematica",
        "path": "models/SO10Z17AxionV20.m",
        "role": "primary_model",
        "sha256": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "size_bytes": 5182,
    },
    {
        "format": "wolfram-language",
        "path": "tools/validate-exact-x-model.wls",
        "role": "validation_driver",
        "sha256": "1d1dea122de1d3465cd0af14e10574b87bf72594de69e3a888fc7bcba5d1e281",
        "size_bytes": 10529,
    },
    {
        "format": "sarah-source-tree-manifest",
        "path": "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json",
        "role": "trusted_sarah_release_manifest",
        "sha256": EXACT_X_V3_TRUSTED_SARAH_MANIFEST_RAW_SHA256,
        "size_bytes": 198868,
    },
)

DEPENDENCIES: dict[str, list[str]] = {
    "MODEL_CONTRACT": [],
    "G1": ["MODEL_CONTRACT"],
    "G2": ["G1"],
    "G3": ["G2"],
    "G4": ["G2", "G3"],
    "G5": ["G1", "G2"],
    "G6": ["G3", "G4", "G5"],
    "G7": ["G6"],
    "G8": ["G3", "G6", "G7"],
}


def _root_contract_evidence_complete(x_report: dict[str, Any]) -> bool:
    """Require native syntax plus fully bound v3 execution evidence."""
    scaffold = x_report.get("executable_scaffold_contract", {})
    lagrangian = scaffold.get("lagrangian", {})
    external = x_report.get("external_model_validation", {})
    external_checks = external.get("checks", {})
    return bool(
        scaffold.get("model_syntax_class") == "sarah_native"
        and scaffold.get("tool_native_sarah_syntax") is True
        and scaffold.get("statically_executable_model_contract") is True
        and lagrangian.get("registered_in_GaugeES_LagrangianInput") is True
        and external.get("schema") == exact_x.EXTERNAL_VALIDATION_SCHEMA
        and external.get("present") is True
        and external.get("valid") is True
        and external.get("fresh_for_exact_model_bytes") is True
        and set(external_checks) == EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
        and all(
            external_checks.get(name) is True
            for name in EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
        )
    )


def _exact_x_v3_fail_closed_contract(
    report: dict[str, Any],
    *,
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    json_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
    input_manifest_raw_sha256: str = "",
    trusted_sarah_manifest_raw_sha256: str = "",
    external_validation_file_present: bool = True,
) -> dict[str, Any]:
    """Bind the exact-X v3 execution state without freezing it as absent.

    The current release has no attestation, but a genuine, fully bound v3
    execution must be able to move this diagnostic from BLOCKED to PASS after
    its report pins are deliberately refreshed.  Both branches are checked
    exactly; a partial or self-labelled attestation satisfies neither.
    """
    scaffold = report.get("executable_scaffold_contract", {})
    lagrangian = scaffold.get("lagrangian", {})
    repository_manifest = report.get("repository_external_input_manifest", {})
    manifest_checks = repository_manifest.get("checks", {})
    trusted = repository_manifest.get("trusted_sarah_release_manifest", {})
    trusted_checks = trusted.get("checks", {})
    trusted_release = trusted.get("release", {})
    trusted_archive = trusted_release.get("archive", {})
    trusted_tree = trusted.get("tree", {})
    external = report.get("external_model_validation", {})
    external_checks = external.get("checks", {})
    expected_manifest = repository_manifest.get("expected", {})
    expected_files = expected_manifest.get("files", [])
    checks = {
        "all_six_raw_pins_exact": (
            source_raw_sha256 == EXACT_X_V3_SOURCE_RAW_SHA256
            and test_raw_sha256 == EXACT_X_V3_TEST_RAW_SHA256
            and json_raw_sha256 == EXACT_X_V3_JSON_RAW_SHA256
            and markdown_raw_sha256 == EXACT_X_V3_MD_RAW_SHA256
            and input_manifest_raw_sha256
            == EXACT_X_V3_INPUT_MANIFEST_RAW_SHA256
            and trusted_sarah_manifest_raw_sha256
            == EXACT_X_V3_TRUSTED_SARAH_MANIFEST_RAW_SHA256
        ),
        "static_native_contract_exact": (
            report.get("status")
            == (
                "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__CONSISTENT"
                if report.get("contract_consistent") is True
                else "AUTHORITATIVE_GAUGED_U1X_CONTRACT_AUDIT_COMPLETE__BLOCKED"
            )
            and report.get("overall_state")
            == ("PASS" if report.get("contract_consistent") is True else "BLOCKED")
            and report.get("n_checks") == 25
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and report.get("audit_failures") == []
            and report.get("static_contract_consistent") is True
            and scaffold.get("model_syntax_class") == "sarah_native"
            and scaffold.get("tool_native_sarah_syntax") is True
            and scaffold.get("statically_executable_model_contract") is True
            and lagrangian.get("registered_in_GaugeES_LagrangianInput") is True
        ),
        "input_manifest_v2_exact_and_pre_execution_only": (
            repository_manifest.get("present") is True
            and repository_manifest.get("valid") is True
            and repository_manifest.get("load_error") is None
            and repository_manifest.get("driver_load_error") is None
            and repository_manifest.get("trusted_release_manifest_load_error")
            is None
            and repository_manifest.get("role")
            == "Pre-execution content manifest only; it is not an external SARAH execution attestation."
            and set(manifest_checks) == EXPECTED_EXACT_X_V3_INPUT_MANIFEST_CHECKS
            and all(
                manifest_checks.get(name) is True
                for name in EXPECTED_EXACT_X_V3_INPUT_MANIFEST_CHECKS
            )
            and expected_manifest.get("schema")
            == exact_x.EXTERNAL_INPUT_MANIFEST_SCHEMA
            and expected_manifest.get("sha256")
            == "0f9050ef8e9ac9cd0a398e7fb8d59b12675d51065610d8dbf4903b87fcd7c313"
            and expected_files == list(EXPECTED_EXACT_X_V3_INPUT_FILES)
        ),
        "trusted_SARAH_4_15_3_manifest_and_tree_exact": (
            trusted.get("present") is True
            and trusted.get("valid") is True
            and trusted.get("schema")
            == exact_x.TRUSTED_SARAH_RELEASE_MANIFEST_SCHEMA
            and set(trusted_checks) == EXPECTED_EXACT_X_V3_TRUSTED_TREE_CHECKS
            and all(
                trusted_checks.get(name) is True
                for name in EXPECTED_EXACT_X_V3_TRUSTED_TREE_CHECKS
            )
            and trusted_release.get("name") == "SARAH"
            and trusted_release.get("version") == "4.15.3"
            and trusted_archive.get("filename") == "SARAH-4.15.3.tar.gz"
            and trusted_archive.get("sha256")
            == "6ee5c12d21a38f9de7f08b5b8db368b6653d7bfbcc8e45189016be87743729fb"
            and trusted_tree.get("file_count") == 1056
            and trusted_tree.get("calculated_file_count") == 1056
            and trusted_tree.get("size_bytes") == 20165588
            and trusted_tree.get("calculated_size_bytes") == 20165588
            and trusted_tree.get("sha256")
            == EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
            and trusted_tree.get("calculated_sha256")
            == EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256
        ),
        "v3_external_attestation_state_is_exact": (
            exact_x.EXTERNAL_VALIDATION_SCHEMA
            == "so10-exact-x-external-model-validation-v3"
            and set(external_checks) == EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
            and external.get("expected_trusted_sarah_release_manifest_sha256")
            == EXACT_X_V3_TRUSTED_SARAH_MANIFEST_RAW_SHA256
            and (
                (
                    report.get("contract_consistent") is True
                    and external_validation_file_present is True
                    and external.get("present") is True
                    and external.get("valid") is True
                    and external.get("schema") == exact_x.EXTERNAL_VALIDATION_SCHEMA
                    and external.get("fresh_for_exact_model_bytes") is True
                    and external.get("load_error") is None
                    and all(
                        external_checks.get(name) is True
                        for name in EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
                    )
                    and _root_contract_evidence_complete(report) is True
                )
                or (
                    report.get("contract_consistent") is False
                    and external.get("present") is False
                    and external_validation_file_present is False
                    and external.get("valid") is False
                    and external.get("schema") is None
                    and external.get("fresh_for_exact_model_bytes") is False
                    and external.get("sarah_source_tree") == {}
                    and external.get("wolfram_runtime") == {}
                    and external.get("load_error") is None
                    and all(
                        external_checks.get(name)
                        is (name in EXPECTED_EXACT_X_V3_ABSENT_TRUE_CHECKS)
                        for name in EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
                    )
                    and _root_contract_evidence_complete(report) is False
                )
            )
        ),
        "authoritative_contract_state_is_exact": (
            (
                report.get("contract_consistent") is True
                and report.get("blocker") is None
                and report.get("scientific_blockers") == []
                and _root_contract_evidence_complete(report) is True
            )
            or (
                report.get("contract_consistent") is False
                and report.get("blocker") == CONTRACT_BLOCKER
                and report.get("scientific_blockers") == [CONTRACT_BLOCKER]
                and _root_contract_evidence_complete(report) is False
            )
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EXACT_X_V3_FAIL_CLOSED_CONTRACT",
        "source_bound": source_bound,
        "static_native_contract_closed": bool(source_bound),
        "input_manifest_v2_closed": bool(source_bound),
        "trusted_SARAH_4_15_3_source_tree_manifest_closed": bool(source_bound),
        "trusted_SARAH_source_tree_file_count": 1056 if source_bound else None,
        "trusted_SARAH_source_tree_core_sha256": (
            EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256 if source_bound else None
        ),
        "external_attestation_schema_required": exact_x.EXTERNAL_VALIDATION_SCHEMA,
        "external_v3_execution_attestation_present": bool(
            source_bound and external.get("valid") is True
        ),
        "resolved_Wolfram_runtime_bound": bool(
            source_bound
            and external_checks.get(
                "resolved_wolfram_launcher_is_hash_bound_and_unchanged"
            )
            is True
            and external_checks.get(
                "resolved_wolfram_kernel_is_hash_bound_and_unchanged"
            )
            is True
        ),
        "runtime_probe_log_bound": bool(
            source_bound
            and external_checks.get("runtime_probe_log_is_hash_bound") is True
        ),
        "validation_process_log_bound": bool(
            source_bound
            and external_checks.get("captured_process_log_is_hash_bound") is True
        ),
        "contract_consistent": bool(
            source_bound and report.get("contract_consistent") is True
        ),
        "authoritative_G1_closed": bool(
            source_bound and report.get("contract_consistent") is True
        ),
        "release_G1_verified": bool(
            source_bound and report.get("contract_consistent") is True
        ),
        "blocker": None if report.get("contract_consistent") is True else CONTRACT_BLOCKER,
        "checks": checks,
    }


def _acyclic_dependencies() -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        if node not in DEPENDENCIES:
            return False
        visiting.add(node)
        if not all(visit(parent) for parent in DEPENDENCIES[node]):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in DEPENDENCIES)


def _historical_option_c_subtheorems() -> dict[str, Any]:
    """Preserve prior calculations without promoting them across contracts."""
    return {
        "model_contract_id": HISTORICAL_CONTRACT_ID,
        "authoritative_for_gauged_model": False,
        "scope_warning": (
            "These results are conditional theorems of the historical no-X "
            "potential and cannot close the manuscript's gauged-U(1)_X gates."
        ),
        "source_contract_ids": {
            "G1": historical_g1.MODEL_CONTRACT_ID,
            "G2": historical_g2.MODEL_CONTRACT_ID,
            "G3_hessian": historical_g3_hessian.MODEL_CONTRACT_ID,
            "G3_search": historical_g3_search.MODEL_CONTRACT_ID,
        },
        "G1": {
            "scoped_status": "CLOSED_UNDER_HISTORICAL_OPTION_C",
            "base_tensor_families": 18,
            "invariant_directions": 64,
            "real_potential_parameters": 91,
        },
        "G2": {
            "scoped_status": "CLOSED_UNDER_HISTORICAL_OPTION_C",
            "real_field_dimension": 486,
            "gradient_entries": 486,
            "dense_Hessian_shape": [486, 486],
            "symmetric_Hessian_entries": 118341,
        },
        "G3": {
            "scoped_status": "PHYSICAL_SADDLE_UNDER_HISTORICAL_OPTION_C",
            "stationary_tadpoles": 486,
            "massive_physical_quotient_dimension": 449,
            "anchored_witness_negative_modes": 46,
            "anchored_witness_zero_modes": 0,
            "anchored_witness_positive_modes": 403,
            "stationary_affine_dimension": 77,
            "stability_search_iterations": 80,
            "best_minimum_equilibrated_eigenvalue": -0.025502339625368114,
            "strict_local_minimum_found": False,
            "whole_gauged_model_excluded": False,
        },
    }


@lru_cache(maxsize=1)
def _load_or_build_gauged_g2_report() -> dict[str, Any]:
    """Reuse the release artifact; build it when the ledger runs standalone."""
    if gauged_g2.OUT_JSON.exists():
        try:
            report = json.loads(gauged_g2.OUT_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report = None
        if (
            isinstance(report, dict)
            and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and "stationary_Hessian_bridge" in report
            and "counts" in report
            and "flags" in report
            and report["flags"].get(
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            )
            is True
            and report["flags"].get(
                "stationarity_rank_13_exactly_certified"
            )
            is True
            and report["flags"].get(
                "stationarity_nullity_38_exactly_certified"
            )
            is True
        ):
            return report
    return gauged_g2.build_report()


def _load_json_artifact(path: Path) -> dict[str, Any]:
    """Load a required release artifact without silently rebuilding its claims."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _renormalizable_g1_component_tensor_closure(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
) -> dict[str, Any]:
    """Validate the source-bound mathematical G1 theorem without fabricating release."""
    closure = report.get("closure", {})
    classification = report.get("classification", {})
    counts = report.get("counts", {})
    integration = report.get("integration", {})
    release_blockers = set(report.get("release_blockers", []))
    integration_keys = {
        "consumed_by_central_G1_G8_ledger",
        "consumed_by_execution_roadmap",
        "consumed_by_validation_matrix",
        "release_orchestrators_execute_read_only",
    }
    integration_values = {
        name: integration.get(name) for name in sorted(integration_keys)
    }
    integration_complete = bool(
        set(integration) == integration_keys
        and all(value is True for value in integration_values.values())
    )
    integration_pending = bool(
        set(integration) == integration_keys
        and all(value is False for value in integration_values.values())
    )
    integration_blocker = "G1_COMPONENT_TENSOR_CLOSURE_DOWNSTREAM_INTEGRATION_REQUIRED"
    integration_state_fail_closed = bool(
        (integration_complete and integration_blocker not in release_blockers)
        or (integration_pending and integration_blocker in release_blockers)
    )
    direction_ids = list(report.get("direction_ids", []))
    parameter_ids = list(report.get("parameter_ids", []))
    family_ids = list(report.get("family_ids", []))
    embedded_checks = report.get("checks", {})
    source_hashes = report.get("source_sha256", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_RING_CLOSED"
            and report.get("overall_state") == "CLOSED_SUBPROBLEM"
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256
        ),
        "source_raw_sha256_exact": (
            source_raw_sha256
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        ),
        "model_contract_exact": (
            report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        ),
        "canonical_direction_map_exact": (
            report.get("canonical_direction_map_sha256")
            == RENORMALIZABLE_G1_DIRECTION_MAP_SHA256
        ),
        "counts_exact": (
            counts.get("multidegrees") == 34
            and counts.get("Hermitian_conjugacy_orbits") == 28
            and counts.get("invariant_directions") == 44
            and counts.get("self_conjugate_directions") == 37
            and counts.get("complex_paired_directions") == 7
            and counts.get("real_parameters") == 51
            and counts.get("tensor_families") == 18
            and counts.get("real_field_dimension") == 486
        ),
        "canonical_ids_are_complete_and_unique": (
            len(direction_ids) == len(set(direction_ids)) == 44
            and len(parameter_ids) == len(set(parameter_ids)) == 51
            and len(family_ids) == len(set(family_ids)) == 18
            and sum(item.startswith("lambda::") for item in parameter_ids) == 37
            and sum(item.startswith("re::") for item in parameter_ids) == 7
            and sum(item.startswith("im::") for item in parameter_ids) == 7
        ),
        "all_embedded_mathematical_checks_pass": (
            len(embedded_checks) == 21
            and all(value is True for value in embedded_checks.values())
        ),
        "all_source_hashes_are_portable_sha256": (
            report.get("source_hash_convention")
            == "text bytes canonicalized to LF before SHA-256"
            and len(source_hashes) == 18
            and all(
                isinstance(value, str)
                and len(value) == 64
                and set(value).issubset(set("0123456789abcdef"))
                for value in source_hashes.values()
            )
        ),
        "mathematical_G1_closure_exact": (
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
        "mathematical_not_authoritative_or_release": (
            classification.get("scoped_mathematical_G1_closed") is True
            and classification.get("authoritative_G1_promoted_closed") is False
            and classification.get("release_G1_verified") is False
            and classification.get("renormalizable_model_mutated") is False
            and classification.get("new_physics_required_for_G1") is False
        ),
        "external_SARAH_blocker_preserved": CONTRACT_BLOCKER in release_blockers,
        "downstream_integration_state_is_fail_closed": integration_state_fail_closed,
    }
    source_bound = all(checks.values())
    return {
        "namespace": "RENORMALIZABLE_G1_COMPONENT_TENSOR_CLOSURE",
        "artifact": RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON.name,
        "source": RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE.name,
        "expected_core_sha256": RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "expected_direction_map_sha256": RENORMALIZABLE_G1_DIRECTION_MAP_SHA256,
        "direction_map_sha256": report.get("canonical_direction_map_sha256"),
        "model_contract_id": report.get("model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G1_closed_for_renormalizable_model": bool(
            source_bound
            and classification.get("scoped_mathematical_G1_closed") is True
        ),
        "authoritative_G1_promoted_closed": False,
        "release_G1_verified": False,
        "renormalizable_model_mutated": False,
        "new_physics_required_for_G1": False,
        "downstream_integration_completed": integration_complete,
        "integration": integration_values,
        "release_blockers": list(report.get("release_blockers", [])) if source_bound else [],
        "counts": dict(counts) if source_bound else {},
        "checks": checks,
    }


def _renormalizable_g2_mathematical_closure(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
) -> dict[str, Any]:
    """Validate mathematical G2 without fabricating authoritative release."""
    counts = report.get("counts", {})
    closure = report.get("closure", {})
    classification = report.get("classification", {})
    integration = report.get("integration", {})
    integration_blockers = list(report.get("integration_blockers", []))
    release_blockers = list(report.get("release_blockers", []))
    embedded_checks = report.get("checks", {})
    artifact_hashes = report.get("artifact_sha256", {})
    derivative_coverage = report.get("derivative_coverage", {})
    ward_coverage = report.get("Ward_identity_coverage", {})
    stationarity = report.get("stationarity", {})
    integration_keys = {
        "consumed_by_central_G1_G8_ledger",
        "consumed_by_execution_roadmap",
        "consumed_by_validation_matrix",
        "release_orchestrators_execute_read_only",
    }
    integration_values = {
        name: integration.get(name) for name in sorted(integration_keys)
    }
    integration_complete = bool(
        set(integration) == integration_keys
        and all(value is True for value in integration_values.values())
    )
    integration_pending = bool(
        set(integration) == integration_keys
        and all(value is False for value in integration_values.values())
    )
    expected_integration_blocker = (
        "G2_MATHEMATICAL_CLOSURE_NOT_YET_WIRED_TO_ALL_DOWNSTREAM_CONSUMERS"
    )
    integration_state_fail_closed = bool(
        (integration_complete and not integration_blockers)
        or (
            integration_pending
            and integration_blockers == [expected_integration_blocker]
        )
    )
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSED_RELEASE_OPEN"
            and report.get("overall_state") == "CLOSED_SUBPROBLEM"
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == RENORMALIZABLE_G2_MATHEMATICAL_RAW_SHA256,
        "source_raw_sha256_exact": (
            source_raw_sha256
            == RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256
        ),
        "model_contract_exact": report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID,
        "terminal_G1_core_exact": (
            report.get("upstream_cores", {}).get("terminal_mathematical_G1")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        ),
        "counts_exact": counts == {
            "invariant_directions": 44,
            "real_parameters": 51,
            "base_tensor_families": 18,
            "real_field_dimension": 486,
            "gradient_entries_per_parameter": 486,
            "Hessian_shape_per_parameter": [486, 486],
            "symmetric_Hessian_entries_per_parameter": 118341,
            "upstream_derivative_audit_checks": 49,
        },
        "all_embedded_mathematical_checks_pass": (
            report.get("n_checks") == len(embedded_checks) == 17
            and all(value is True for value in embedded_checks.values())
        ),
        "sixteen_upstream_artifacts_are_hash_bound": (
            len(artifact_hashes) == 16
            and all(
                isinstance(value, str)
                and len(value) == 64
                and set(value).issubset(set("0123456789abcdef"))
                for value in artifact_hashes.values()
            )
        ),
        "complete_derivative_and_Ward_coverage": (
            len(derivative_coverage) == 5
            and all(value is True for value in derivative_coverage.values())
            and len(ward_coverage) == 12
            and all(value is True for value in ward_coverage.values())
        ),
        "exact_stationarity_13_38_is_compiler_bound": (
            stationarity.get("matrix_shape") == [486, 51]
            and stationarity.get("exact_rank") == 13
            and stationarity.get("exact_nullity") == 38
            and stationarity.get("exact_nonzero_13x13_minor") is True
            and stationarity.get("exact_rank_upper_factorization") is True
            and stationarity.get("compiler_minor_binding") is True
            and stationarity.get("stationary_witness_P24_trace") == 288
            and stationarity.get("stationary_Hessian_compiler_binding") is True
            and stationarity.get("float64_SVD_is_diagnostic_only") is True
        ),
        "mathematical_G2_closure_exact": (
            closure.get("terminal_mathematical_G1_prerequisite_closed") is True
            and closure.get("full_component_potential_G2_mathematically_closed")
            is True
            and closure.get("values_gradients_Hessians_and_Ward_identities_closed")
            is True
            and closure.get("exact_stationarity_rank_nullity_closed") is True
            and closure.get("external_model_execution_contract_closed") is False
        ),
        "mathematical_not_authoritative_or_release": (
            classification.get("mathematical_renormalizable_G2_closed") is True
            and classification.get("authoritative_G2_promoted_closed") is False
            and classification.get("release_G2_verified") is False
            and classification.get("renormalizable_model_mutated") is False
            and classification.get("new_physics_required_for_G2") is False
            and classification.get("G3_closed_by_this_theorem") is False
        ),
        "external_SARAH_blocker_preserved": release_blockers == [CONTRACT_BLOCKER],
        "downstream_integration_state_is_fail_closed": integration_state_fail_closed,
    }
    source_bound = all(checks.values())
    return {
        "namespace": "RENORMALIZABLE_G2_MATHEMATICAL_CLOSURE",
        "artifact": RENORMALIZABLE_G2_MATHEMATICAL_JSON.name,
        "source": RENORMALIZABLE_G2_MATHEMATICAL_SOURCE.name,
        "expected_core_sha256": RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": RENORMALIZABLE_G2_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": RENORMALIZABLE_G2_MATHEMATICAL_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "model_contract_id": report.get("model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G2_closed_for_renormalizable_model": bool(
            source_bound
            and classification.get("mathematical_renormalizable_G2_closed") is True
        ),
        "authoritative_G2_promoted_closed": False,
        "release_G2_verified": False,
        "renormalizable_model_mutated": False,
        "new_physics_required_for_G2": False,
        "G3_closed_by_this_theorem": False,
        "downstream_integration_completed": integration_complete,
        "integration": integration_values,
        "integration_blockers": integration_blockers if source_bound else [],
        "release_blockers": release_blockers if source_bound else [],
        "counts": dict(counts) if source_bound else {},
        "checks": checks,
    }


def _parallel_eft_g3_acceptance(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate and expose the EFT G3 result without mutating G3 or G4."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G3_ACCEPTANCE__MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256
        ),
        "base_contract_exact": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        ),
        "EFT_contract_exact": (
            contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
        ),
        "authoritative_parameter_count_51": (
            contract.get("authoritative_renormalizable_parameter_count") == 51
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "selected_nonzero_parameter_count_27": (
            contract.get("selected_nonzero_renormalizable_parameter_count")
            == 27
        ),
        "single_dimension_six_operator": (
            contract.get("dimension_six_operator_count") == 1
            and mathematical_checks.get("operator_is_dimension_six_EFT") is True
        ),
        "EFT_mathematical_G3_closed": (
            classification.get("mathematical_G3_closed_for_EFT_model") is True
            and mathematical_checks.get("EFT_mathematical_G3_flag") is True
            and mathematical_checks.get("arbitrary_486_field_lower_bound")
            is True
            and mathematical_checks.get("selected_global_minimum") is True
            and mathematical_checks.get("unique_declared_symmetry_orbit")
            is True
        ),
        "renormalizable_G3_unchanged_and_open": (
            classification.get(
                "mathematical_G3_closed_for_original_renormalizable_model"
            )
            is False
            and classification.get("renormalizable_gate_mutated") is False
            and mathematical_checks.get("renormalizable_G3_not_relabelled")
            is True
            and production_mapping.get("do_not_flip")
            == "FINAL_G3_ACCEPTANCE_GATE_V20 for the renormalizable model"
        ),
        "G4_not_closed": (
            classification.get("G4_closed") is False
            and mathematical_checks.get("G4_not_relabelled") is True
        ),
        "EFT_release_open": (
            classification.get("release_G3_verified_for_EFT_model") is False
            and required_release_blockers.issubset(
                set(report.get("release_blockers", []))
            )
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            production_mapping.get("new_parallel_gate_required")
            == "EFT_G3_ACCEPTANCE"
        ),
        "parallel_production_mapping_integrated": (
            classification.get("production_gate_integrated") is True
            and release_criteria.get("authoritative_EFT_contract_registered")
            is True
            and release_criteria.get("clean_production_gate_integration_completed")
            is True
        ),
        "whole_model_not_excluded": (
            classification.get("whole_model_excluded") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G3_ACCEPTANCE",
        "artifact": FINAL_G3_EFT_ACCEPTANCE_JSON.name,
        "expected_core_sha256": FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G3_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G3_closed_for_EFT_model")
            is True
        ),
        "release_G3_verified_for_EFT_model": False,
        "mathematical_G3_closed_for_original_renormalizable_model": False,
        "renormalizable_gate_mutated": False,
        "G4_closed": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g4_mathematical(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate the parallel EFT G4 theorem without promoting legacy G4."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    hessian = report.get("exact_Hessian_classification", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
        "release_G3_verified_for_EFT_model",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G4_MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256
        ),
        "contract_exact_and_renormalizable_contract_unchanged": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "upstream_cores_exact": (
            report.get("theorem_core_sha256")
            == "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
            and report.get("upstream_G3_gate_core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "exact_physical_hessian_classification": (
            hessian.get("full_real_dimension") == 486
            and hessian.get("gauge_quotient_dimension_including_axion") == 449
            and hessian.get("massless_physical_axion_modes") == 1
            and hessian.get("massive_transverse_dimension") == 448
            and hessian.get("negative_modes") == 0
            and hessian.get("unexplained_zero_modes") == 0
            and hessian.get("strictly_positive_massive_transverse_modes") == 448
            and hessian.get("Hessian_rank") == 448
            and hessian.get("Hessian_nullity") == 38
            and hessian.get("positive_kappa_family", {}).get(
                "rank448_nullity38_for_every_positive_kappa"
            )
            is True
        ),
        "EFT_mathematical_G4_closed": (
            classification.get("mathematical_G4_closed_for_EFT_model") is True
        ),
        "renormalizable_G4_unchanged_and_open": (
            classification.get(
                "mathematical_G4_closed_for_original_renormalizable_model"
            )
            is False
            and classification.get(
                "authoritative_renormalizable_G4_gate_mutated"
            )
            is False
            and production_mapping.get("do_not_flip")
            == "authoritative renormalizable G4"
        ),
        "EFT_release_open": (
            classification.get("release_G4_verified_for_EFT_model") is False
            and set(report.get("release_blockers", []))
            == required_release_blockers
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            production_mapping.get("new_parallel_gate")
            == "EFT_G4_MATHEMATICAL"
            and production_mapping.get("release_integration_completed") is True
            and "release_integration_required" not in production_mapping
        ),
        "parallel_integration_completed": (
            release_criteria.get(
                "parallel_EFT_G4_integrated_into_release_orchestrators"
            )
            is True
        ),
        "whole_model_not_validated": (
            classification.get("whole_model_validated") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G4_MATHEMATICAL",
        "artifact": FINAL_G4_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G4_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G4_closed_for_EFT_model")
            is True
        ),
        "release_G4_verified_for_EFT_model": False,
        "mathematical_G4_closed_for_original_renormalizable_model": False,
        "authoritative_renormalizable_G4_gate_mutated": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g5_mathematical(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate the parallel EFT G5 theorem without promoting legacy G5."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    proof_reuse = report.get("proof_reuse", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G5_MATHEMATICAL_GATE__MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256
        ),
        "contract_exact_and_renormalizable_contract_unchanged": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("real_field_dimension") == 486
            and contract.get("authoritative_renormalizable_parameter_count")
            == 51
            and contract.get("selected_nonzero_renormalizable_parameter_count")
            == 27
            and contract.get("dimension_six_operator_count") == 1
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "frozen_theorem_composition_exact": (
            proof_reuse.get("kind")
            == "composition_of_existing_frozen_exact_theorems"
            and proof_reuse.get("new_SOS_constructed_or_claimed") is False
            and proof_reuse.get("EFT_theorem_core_sha256")
            == "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
            and proof_reuse.get("O6_theorem_core_sha256")
            == "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
            and proof_reuse.get("immutable_EFT_G3_gate_core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
            and report.get("exact_global_lower_bound") == "-40661/20000"
        ),
        "EFT_mathematical_G5_closed": (
            classification.get("mathematical_G5_closed_for_EFT_model") is True
            and classification.get("new_SOS_claimed") is False
        ),
        "renormalizable_G5_unchanged_and_blocked": (
            classification.get("authoritative_renormalizable_G5_closed")
            is False
            and classification.get(
                "authoritative_renormalizable_G5_blocked_by_model_contract"
            )
            is True
            and classification.get("authoritative_renormalizable_G5_blocker")
            == CONTRACT_BLOCKER
            and classification.get("authoritative_renormalizable_G5_mutated")
            is False
            and production_mapping.get("do_not_flip")
            == (
                "authoritative G5 in G1_G8_GATE_LEDGER_V20 for the "
                "renormalizable model"
            )
        ),
        "EFT_release_open": (
            classification.get("release_G5_verified_for_EFT_model") is False
            and set(report.get("release_blockers", []))
            == required_release_blockers
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            report.get("namespace") == "EFT_G5_MATHEMATICAL"
            and production_mapping.get("new_parallel_gate")
            == "EFT_G5_MATHEMATICAL"
            and production_mapping.get("downstream_integration_completed")
            is True
        ),
        "parallel_integration_completed": (
            release_criteria.get("downstream_parallel_G5_integration_completed")
            is True
        ),
        "whole_model_not_excluded": (
            classification.get("whole_model_excluded") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G5_MATHEMATICAL",
        "artifact": FINAL_G5_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G5_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G5_closed_for_EFT_model")
            is True
        ),
        "release_G5_verified_for_EFT_model": False,
        "authoritative_renormalizable_G5_closed": False,
        "authoritative_renormalizable_G5_blocked_by_model_contract": True,
        "authoritative_renormalizable_G5_mutated": False,
        "new_SOS_claimed": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _g6_sm_provenance_audit(
    report: dict[str, Any], *, raw_sha256: str = "", source_raw_sha256: str = ""
) -> dict[str, Any]:
    """Bind the exact proof that the frozen G6 stabilizer is not physical Q."""
    classification = report.get("classification", {})
    background = report.get("selected_background_audit", {})
    commutant = report.get("mass_pencil_commutant", {})
    projector = report.get("projector_feasibility", {})
    naive_swap = report.get("independent_live_true_SM_singlet_swap_diagnostic", {})
    embedded_checks = report.get("checks", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_G6_SM_PROVENANCE_MISMATCH_PROVED__G6_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256") == G6_SM_PROVENANCE_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == G6_SM_PROVENANCE_RAW_SHA256,
        "source_raw_sha256_exact": (
            source_raw_sha256 == G6_SM_PROVENANCE_SOURCE_RAW_SHA256
        ),
        "contract_exact": report.get("model_contract_id") == EFT_MODEL_CONTRACT_ID,
        "all_embedded_checks_pass": (
            report.get("n_failed") == 0
            and report.get("failures") == []
            and bool(embedded_checks)
            and all(value is True for value in embedded_checks.values())
        ),
        "actual_stabilizer_and_physical_mismatch_exact": (
            classification.get(
                "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89"
            )
            is True
            and classification.get("frozen_G6_physical_U1em_provenance_complete")
            is False
            and background.get("therefore_F_and_P_are_not_SO10_conjugate") is True
            and background.get("selected_full_target_tangents", {}).get(
                "actual_G89_nnz"
            )
            == 0
            and background.get("selected_full_target_tangents", {}).get(
                "standard_Q3_nnz"
            )
            > 0
        ),
        "standard_SM_mass_projectors_do_not_exist": (
            projector.get("frozen_G6_mass_eigenspace_standard_SU2L_x_U1Y_labels")
            == "NOT_DEFINED_BY_SIMULTANEOUS_PROJECTORS"
            and commutant.get("actual_G89", {}).get("nnz") == 0
            and commutant.get("standard_Q3", {}).get("nnz", 0) > 0
            and commutant.get("standard_Y6", {}).get("nnz", 0) > 0
        ),
        "formal_factorization_retained_but_physical_G6_open": (
            classification.get("mathematical_tree_level_mass_factorization_remains_valid")
            is True
            and classification.get("frozen_G6_per_mass_state_SU2L_x_U1Y_provenance_complete")
            is False
            and classification.get("frozen_G6_Pati_Salam_threshold_provenance_complete")
            is False
            and classification.get("release_level_G6_complete") is False
            and classification.get("positive_G7_threshold_input_complete") is False
            and classification.get("mathematical_physical_G6_closed") is False
            and classification.get(
                "prior_positive_mathematical_G6_as_physical_SM_spectrum_valid"
            )
            is False
        ),
        "required_recalculation_retained": len(report.get("required_recalculation", []))
        >= 5,
        "naive_true_SM_singlet_swap_rejected_by_live_diagnostic": (
            naive_swap.get("naive_swap_is_stationary") is False
            and naive_swap.get("naive_swap_is_locally_stable") is False
            and naive_swap.get("gradient_entries_above_1e_minus_9", 0) > 0
            and naive_swap.get("minimum_full_Hessian_eigenvalue", 0) < 0
            and naive_swap.get("proof_grade") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "G6_PHYSICAL_STABILIZER_AND_SM_PROVENANCE_AUDIT",
        "artifact": G6_SM_PROVENANCE_JSON.name,
        "source": G6_SM_PROVENANCE_SOURCE.name,
        "expected_core_sha256": G6_SM_PROVENANCE_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": G6_SM_PROVENANCE_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": G6_SM_PROVENANCE_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "source_bound": source_bound,
        "formal_tree_mass_factorization_valid": bool(
            source_bound
            and classification.get(
                "mathematical_tree_level_mass_factorization_remains_valid"
            )
            is True
        ),
        "actual_residual_group": (
            "SU(3)_C x U(1)_89" if source_bound else None
        ),
        "physical_U1em_provenance_complete": False,
        "per_mass_state_SU2L_x_U1Y_provenance_complete": False,
        "Pati_Salam_threshold_provenance_complete": False,
        "physical_mathematical_G6_closed": False,
        "release_G6_verified": False,
        "positive_G7_threshold_input_complete": False,
        "naive_true_SM_singlet_swap_stationary": False,
        "naive_true_SM_singlet_swap_locally_stable": False,
        "required_recalculation": (
            list(report.get("required_recalculation", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parameterized_g6_g7_matching(
    report: dict[str, Any], *, raw_sha256: str = "", source_raw_sha256: str = ""
) -> dict[str, Any]:
    """Bind the maximal formal G89 threshold result without calling it QED."""
    classification = report.get("classification", {})
    stabilizer = report.get("physical_stabilizer_audit", {})
    thresholds = report.get("exact_residual_scalar_thresholds", {})
    guard = thresholds.get("interpretation_guard", {})
    comparison = thresholds.get("independent_implementation_comparison", {})
    family = report.get("dimensionful_EFT_family", {}).get(
        "nonidentifiability_proof", {}
    )
    pole = report.get("loop_and_pole_mass_boundary", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_G6_SCALING_AND_FORMAL_G89_THRESHOLD__PHYSICAL_STABILIZER_MISMATCH__G7_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == G6_G7_PARAMETERIZED_MATCHING_RAW_SHA256,
        "source_raw_sha256_exact": (
            source_raw_sha256
            == G6_G7_PARAMETERIZED_MATCHING_SOURCE_RAW_SHA256
        ),
        "contract_exact": report.get("model_contract_id") == EFT_MODEL_CONTRACT_ID,
        "formal_G89_threshold_determinants_exact": (
            classification.get(
                "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete"
            )
            is True
            and comparison.get("agreement") is True
            and comparison.get("maximum_sector_log_determinant_difference", 1.0)
            <= comparison.get("tolerance", 0.0)
            and guard.get("abelian_generator") == "G_(8,9)"
            and guard.get("physical_electromagnetic_interpretation_allowed")
            is False
            and guard.get("physical_hypercharge_interpretation_allowed") is False
            and guard.get("Pati_Salam_matching_interpretation_allowed") is False
        ),
        "physical_stabilizer_mismatch_exact": (
            stabilizer.get("G89_equals_standard_electromagnetism") is False
            and stabilizer.get("physical_U1em_sector_labels_valid") is False
            and stabilizer.get("selected_vacuum_preserves_standard_electromagnetism")
            is False
            and stabilizer.get("three_Q_standard")
            == "3 Q_std=3 G67-(G01+G23+G45)"
            and stabilizer.get("three_Q_standard_exact_vacuum_action", {})
            .get("Delta_R", {})
            .get("integer_squared_norm")
            == 72
            and stabilizer.get("three_Q_standard_exact_vacuum_action", {})
            .get("H", {})
            .get("integer_squared_norm")
            == 18
            and stabilizer.get("selected_full_target_tangent", {}).get(
                "integer_squared_norm"
            )
            == 90
        ),
        "scale_and_Wilson_family_nonidentified": (
            family.get("M0_solvable_from_frozen_G6") is False
            and family.get("Wilson_coefficient_or_cutoff_separately_solvable")
            is False
            and family.get("dimensionful_observable_in_frozen_G6") is False
        ),
        "physical_threshold_and_pole_claims_fail_closed": (
            classification.get("G6_dimensionful_family_parameterized_exactly")
            is True
            and classification.get("G6_normalized_tree_spectrum_reused_exactly")
            is True
            and classification.get("frozen_U1em_identification_correct") is False
            and classification.get("standard_electromagnetic_vacuum_preserved")
            is False
            and classification.get("selected_chiral_H_neutral_under_standard_Q")
            is False
            and classification.get("selected_Delta_R_neutral_under_standard_Q")
            is False
            and classification.get("physical_SM_scalar_thresholds_identified")
            is False
            and classification.get("SM_or_PS_component_threshold_matching_complete")
            is False
            and classification.get("absolute_scale_and_Wilson_matching_complete")
            is False
            and classification.get("loop_and_pole_mass_corrections_complete")
            is False
            and pole.get("pole_masses_identified") is False
            and pole.get("renormalized_self_energy_Pi_identified") is False
        ),
        "G7_not_promoted": (
            classification.get("two_loop_RGE_complete") is False
            and classification.get("positive_G7_closed") is False
            and len(report.get("positive_G7_missing_inputs", [])) >= 7
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "G6_G7_PARAMETERIZED_FORMAL_G89_MATCHING",
        "artifact": G6_G7_PARAMETERIZED_MATCHING_JSON.name,
        "source": G6_G7_PARAMETERIZED_MATCHING_SOURCE.name,
        "expected_core_sha256": G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": G6_G7_PARAMETERIZED_MATCHING_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            G6_G7_PARAMETERIZED_MATCHING_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "source_bound": source_bound,
        "formal_SU3_x_U1_89_threshold_determinants_complete": bool(
            source_bound
            and classification.get(
                "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete"
            )
            is True
        ),
        "physical_SM_scalar_thresholds_identified": False,
        "absolute_scale_and_Wilson_matching_complete": False,
        "loop_and_pole_mass_corrections_complete": False,
        "physical_mathematical_G6_closed": False,
        "release_G6_verified": False,
        "mathematical_G7_closed": False,
        "release_G7_verified": False,
        "positive_G7_missing_inputs": (
            list(report.get("positive_G7_missing_inputs", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _authoritative_gauge_beta_subtheorem(
    report: dict[str, Any], *, raw_sha256: str = "", source_raw_sha256: str = ""
) -> dict[str, Any]:
    """Bind corrected gauge-only one/two-loop polynomials; keep full G7 open."""
    classification = report.get("classification", {})
    all_active = report.get("regimes", {}).get("all_active_above_vPhi", {})
    one_loop = all_active.get("a_one_loop", {})
    two_loop = all_active.get("b_two_loop_nonyukawa", {})
    embedded_checks = report.get("checks", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_NONYUKAWA_GAUGE_POLYNOMIAL_CLOSED__FULL_G7_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256") == AUTHORITATIVE_GAUGE_BETAS_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == AUTHORITATIVE_GAUGE_BETAS_RAW_SHA256,
        "source_raw_sha256_exact": (
            source_raw_sha256 == AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256
        ),
        "contract_exact": report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID,
        "all_embedded_checks_pass": (
            report.get("n_failed") == 0
            and report.get("failures") == []
            and bool(embedded_checks)
            and all(value is True for value in embedded_checks.values())
        ),
        "corrected_coefficients_exact": (
            one_loop == {"SO10": "52/3", "X": "10843"}
            and two_loop.get("SO10")
            == {"SO10": "25013/6", "X": "4536"}
            and two_loop.get("X")
            == {"SO10": "204120", "X": "7242180"}
        ),
        "scoped_classification_exact": (
            classification.get("authoritative_field_inventory_closed") is True
            and classification.get("exact_nonyukawa_two_loop_gauge_polynomial_closed")
            is True
            and classification.get("full_two_loop_gauge_beta_closed") is False
            and classification.get(
                "full_two_loop_Yukawa_scalar_dimensionful_EFT_system_closed"
            )
            is False
            and classification.get("component_threshold_matching_closed") is False
            and classification.get("physical_G6_input_accepted_for_G7") is False
            and classification.get("mathematical_G7_closed") is False
            and classification.get("release_G7_verified") is False
        ),
        "release_blockers_retained": len(report.get("release_blockers", [])) >= 6,
    }
    source_bound = all(checks.values())
    return {
        "namespace": "AUTHORITATIVE_GAUGE_ONLY_RGE_SUBTHEOREM",
        "artifact": AUTHORITATIVE_GAUGE_BETAS_JSON.name,
        "source": AUTHORITATIVE_GAUGE_BETAS_SOURCE.name,
        "expected_core_sha256": AUTHORITATIVE_GAUGE_BETAS_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": AUTHORITATIVE_GAUGE_BETAS_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "source_bound": source_bound,
        "authoritative_field_inventory_closed": bool(
            source_bound
            and classification.get("authoritative_field_inventory_closed") is True
        ),
        "exact_nonyukawa_two_loop_gauge_polynomial_closed": bool(
            source_bound
            and classification.get(
                "exact_nonyukawa_two_loop_gauge_polynomial_closed"
            )
            is True
        ),
        "full_two_loop_gauge_beta_closed": False,
        "component_threshold_matching_closed": False,
        "physical_G6_input_accepted_for_G7": False,
        "mathematical_G7_closed": False,
        "release_G7_verified": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _pyrate3_gauge_replay_subtheorem(
    report: dict[str, Any], *, raw_sha256: str = "", source_raw_sha256: str = "",
    model_raw_sha256: str = "", data_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the independent official-PyR@TE gauge-only replay."""
    classification = report.get("classification", {})
    embedded_checks = report.get("checks", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": report.get("status")
        == "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN",
        "core_sha256_exact": report.get("core_sha256")
        == PYRATE3_GAUGE_REPLAY_CORE_SHA256,
        "raw_sha256_exact": raw_sha256 == PYRATE3_GAUGE_REPLAY_RAW_SHA256,
        "source_raw_sha256_exact": source_raw_sha256
        == PYRATE3_GAUGE_REPLAY_SOURCE_RAW_SHA256,
        "model_raw_sha256_exact": model_raw_sha256
        == PYRATE3_GAUGE_REPLAY_MODEL_RAW_SHA256,
        "data_raw_sha256_exact": data_raw_sha256
        == PYRATE3_GAUGE_REPLAY_DATA_RAW_SHA256,
        "all_embedded_checks_pass": (
            report.get("n_failed") == 0
            and report.get("failures") == []
            and bool(embedded_checks)
            and all(value is True for value in embedded_checks.values())
        ),
        "independent_scoped_replay_exact": (
            classification.get("independent_gauge_polynomial_replay_closed") is True
            and classification.get("second_implementation_for_scoped_gauge_subtheorem")
            is True
        ),
        "full_G7_fail_closed": (
            classification.get("full_two_loop_gauge_beta_closed") is False
            and classification.get(
                "full_Yukawa_scalar_dimensionful_EFT_system_closed"
            )
            is False
            and classification.get("physical_G6_threshold_matching_closed") is False
            and classification.get("mathematical_G7_closed") is False
            and classification.get("release_G7_verified") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY",
        "artifact": PYRATE3_GAUGE_REPLAY_JSON.name,
        "source": PYRATE3_GAUGE_REPLAY_SOURCE.name,
        "expected_core_sha256": PYRATE3_GAUGE_REPLAY_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "source_bound": source_bound,
        "second_implementation_for_scoped_gauge_subtheorem": bool(source_bound),
        "full_two_loop_gauge_beta_closed": False,
        "physical_G6_threshold_matching_closed": False,
        "mathematical_G7_closed": False,
        "release_G7_verified": False,
        "remaining_blockers": (
            list(report.get("remaining_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }
def _parallel_eft_g6_spectrum(
    report: dict[str, Any], *, raw_sha256: str = "", gate_source_raw_sha256: str = "",
    provenance_audit: dict[str, Any] | None = None,
    parameterized_matching: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Retain the formal exact spectrum while rejecting physical G6 closure."""
    if provenance_audit is None:
        provenance_audit = {}
    if parameterized_matching is None:
        parameterized_matching = {}
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    spectrum = report.get("spectrum_summary", {})
    artifacts = report.get("artifact_sha256", {})
    upstream = report.get("upstream_cores", {})
    release_criteria = report.get("release_criteria", {})
    release_blockers = set(report.get("release_blockers", []))
    false_release_criteria = {
        name for name, value in release_criteria.items() if value is False
    }
    integration_criterion = release_criteria.get(
        "parallel_EFT_G6_integrated_into_release_orchestrators"
    )
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G6_FORMAL_SU3_X_U1_89_FACTOR_PASS__PHYSICAL_G6_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256") == FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
        "gate_source_raw_sha256_exact": (
            gate_source_raw_sha256 == FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256
        ),
        "contract_exact": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("scope")
            == (
                "normalized exact formal SU3C x U1_89 tree-level dimension-six "
                "EFT mass factorization; not a physical SM spectrum"
            )
        ),
        "spectrum_source_and_JSON_raw_pins_exact": (
            artifacts.get("spectrum_source")
            == FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256
            and artifacts.get("spectrum_JSON")
            == FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256
        ),
        "upstream_cores_and_gate_JSON_pins_exact": (
            upstream.get("spectrum") == FINAL_G6_EFT_SPECTRUM_CORE_SHA256
            and upstream.get("G4") == FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256
            and upstream.get("G5") == FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256
            and artifacts.get("G4_gate_JSON")
            == FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256
            and artifacts.get("G5_gate_JSON")
            == FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256
            and upstream.get("G6_physical_provenance")
            == G6_SM_PROVENANCE_CORE_SHA256
            and upstream.get("G6_G7_parameterized_matching")
            == G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256
            and artifacts.get("G6_provenance_source")
            == G6_SM_PROVENANCE_SOURCE_RAW_SHA256
            and artifacts.get("G6_provenance_JSON")
            == G6_SM_PROVENANCE_RAW_SHA256
            and artifacts.get("G6_G7_parameterized_matching_source")
            == G6_G7_PARAMETERIZED_MATCHING_SOURCE_RAW_SHA256
            and artifacts.get("G6_G7_parameterized_matching_JSON")
            == G6_G7_PARAMETERIZED_MATCHING_RAW_SHA256
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "frozen_formal_exact_tree_level_factorization": (
            spectrum.get("ambient_real_fields") == 486
            and spectrum.get("gauge_quotient_dimension") == 449
            and spectrum.get("ungauged_PQ_zero_modes") == 1
            and spectrum.get("positive_massive_modes") == 448
            and spectrum.get("primitive_factors") == 45
            and spectrum.get("distinct_mass_squared_roots_including_zero") == 61
            and spectrum.get("residual_group") == "SU(3)_C x U(1)_89"
            and spectrum.get("physical_U1em_interpretation_valid") is False
            and spectrum.get("mixing_subspaces_complete") is True
        ),
        "corrected_claim_boundary_fail_closed": (
            classification.get("formal_SU3_x_U1_89_tree_mass_factorization_closed")
            is True
            and classification.get("prior_positive_physical_G6_interpretation_valid")
            is False
            and classification.get("mathematical_physical_G6_closed") is False
            and classification.get("mathematical_G6_closed_for_EFT_model") is False
            and release_criteria.get(
                "formal_SU3_x_U1_89_tree_mass_factorization_complete"
            )
            is True
            and release_criteria.get("mathematical_physical_SM_G6_complete")
            is False
        ),
        "renormalizable_authoritative_G6_unchanged": (
            classification.get("authoritative_renormalizable_G6_closed") is False
            and classification.get("authoritative_G6_gate_mutated") is False
        ),
        "EFT_release_open_and_criteria_fail_closed": (
            classification.get("release_G6_verified_for_EFT_model") is False
            and false_release_criteria
            and all(isinstance(value, bool) for value in release_criteria.values())
            and release_blockers == false_release_criteria
        ),
        "parallel_integration_state_classified": (
            isinstance(integration_criterion, bool)
            and (
                "parallel_EFT_G6_integrated_into_release_orchestrators"
                in release_blockers
            )
            is (not integration_criterion)
        ),
        "whole_model_not_validated": (
            classification.get("whole_model_validated") is False
        ),
        "physical_stabilizer_mismatch_source_bound": (
            provenance_audit.get("source_bound") is True
            and provenance_audit.get("formal_tree_mass_factorization_valid") is True
            and provenance_audit.get("actual_residual_group")
            == "SU(3)_C x U(1)_89"
            and provenance_audit.get("physical_U1em_provenance_complete") is False
            and provenance_audit.get("physical_mathematical_G6_closed") is False
        ),
        "formal_matching_reinterpreted_as_G89": (
            parameterized_matching.get("source_bound") is True
            and parameterized_matching.get(
                "formal_SU3_x_U1_89_threshold_determinants_complete"
            )
            is True
            and parameterized_matching.get("physical_SM_scalar_thresholds_identified")
            is False
            and parameterized_matching.get("physical_mathematical_G6_closed")
            is False
        ),
    }
    source_bound = all(checks.values())
    corrected_release_blockers = set(report.get("release_blockers", []))
    corrected_release_blockers.difference_update(
        {
            "PHYSICAL_SM_STABILIZER_AND_VACUUM_REQUIRED",
            "RECOMPUTED_PHYSICAL_SM_HESSIAN_AND_SPECTRUM_REQUIRED",
            "PER_STATE_SM_AND_PATI_SALAM_PROVENANCE_REQUIRED",
            "SM_preserving_staged_vacuum_verified",
            "per_state_SM_and_Pati_Salam_provenance_complete",
        }
    )
    corrected_release_blockers.update(
        {
            "DIRECT_SOURCE_ALGEBRA_PHYSICAL_SM_SCALAR_HESSIAN_REQUIRED",
            "PHYSICAL_SM_GLOBAL_EQUALITY_ORBIT_REQUIRED",
            "DIMENSIONFUL_SCALE_COUPLINGS_AND_POLE_SELF_ENERGY_MASSES_REQUIRED",
            "GAUGE_FIXING_CONSISTENT_VECTOR_GOLDSTONE_GHOST_FINITE_MATCHING_REQUIRED",
        }
    )
    return {
        "namespace": "EFT_G6_FORMAL_SU3_X_U1_89_TREE_SPECTRUM",
        "artifact": FINAL_G6_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_gate_source_raw_sha256": FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256,
        "gate_source_raw_sha256": gate_source_raw_sha256,
        "expected_spectrum_core_sha256": FINAL_G6_EFT_SPECTRUM_CORE_SHA256,
        "spectrum_core_sha256": upstream.get("spectrum"),
        "expected_spectrum_source_raw_sha256": (
            FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256
        ),
        "spectrum_source_raw_sha256": artifacts.get("spectrum_source"),
        "expected_spectrum_JSON_raw_sha256": FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256,
        "spectrum_JSON_raw_sha256": artifacts.get("spectrum_JSON"),
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "formal_SU3_x_U1_89_tree_factorization_closed": bool(source_bound),
        "prior_positive_physical_G6_interpretation_valid": False,
        "physical_stabilizer_audit_source_bound": bool(
            provenance_audit.get("source_bound") is True
        ),
        "mathematical_G6_closed_for_EFT_model": False,
        "physical_mathematical_G6_closed": False,
        "release_G6_verified_for_EFT_model": False,
        "authoritative_renormalizable_G6_closed": False,
        "authoritative_G6_gate_mutated": False,
        "whole_model_validated": False,
        "parallel_integration_completed": bool(source_bound),
        "spectrum_summary": dict(spectrum) if source_bound else {},
        "corrected_residual_group": (
            "SU(3)_C x U(1)_89" if source_bound else None
        ),
        "physical_U1em_provenance_complete": False,
        "physical_SM_scalar_thresholds_identified": False,
        "release_blockers": (
            sorted(corrected_release_blockers) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g7_nonidentifiability(
    report: dict[str, Any], *, raw_sha256: str = "", source_raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate the historical formal U(1)_89 example without a physical claim."""
    classification = report.get("classification", {})
    integration = report.get("integration", {})
    counterexample = report.get("formal_U1_89_abstract_restriction_example", {})
    scale = report.get("absolute_scale_counterexample", {})
    reduced = report.get("reduced_RGE_model_scope", {})
    embedded_checks = report.get("checks", {})
    expected_integration = {
        "ledger_consumes_obstruction",
        "roadmap_consumes_obstruction",
        "validation_matrix_consumes_obstruction",
        "release_orchestrators_and_workflows_consume_obstruction",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FORMAL_U1_89_ABSTRACT_RESTRICTION_NONINJECTIVE__NO_PHYSICAL_G7_CLAIM"
        ),
        "core_sha256_exact": (
            report.get("core_sha256") == EFT_G7_NONIDENTIFIABILITY_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == EFT_G7_NONIDENTIFIABILITY_RAW_SHA256,
        "source_raw_sha256_exact": (
            source_raw_sha256 == EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256
        ),
        "contract_exact": report.get("model_contract_id") == EFT_MODEL_CONTRACT_ID,
        "all_embedded_checks_pass": (
            report.get("n_failed") == 0
            and bool(embedded_checks)
            and all(value is True for value in embedded_checks.values())
        ),
        "formal_U1_89_restriction_example_exact": (
            counterexample.get("restriction_map_noninjective") is True
            and counterexample.get("same_frozen_G6_masses") is True
            and counterexample.get("one_loop_coefficients_differ") is True
            and counterexample.get("physical_QED_interpretation_valid") is False
            and counterexample.get("physical_electroweak_interpretation_valid")
            is False
            and counterexample.get("scope")
            == (
                "abstract lifts of formal q89=0,1 labels only; the names in the "
                "historical completion rows are not assigned to physical states"
            )
            and counterexample.get("completion_A", {}).get(
                "complex_scalar_one_loop_delta_b2"
            )
            == "0"
            and counterexample.get("completion_A", {}).get(
                "complex_scalar_one_loop_delta_bY"
            )
            == "1/3"
            and counterexample.get("completion_B", {}).get(
                "complex_scalar_one_loop_delta_b2"
            )
            == "1/6"
            and counterexample.get("completion_B", {}).get(
                "complex_scalar_one_loop_delta_bY"
            )
            == "1/6"
        ),
        "absolute_scale_counterexample_exact": (
            scale.get("same_normalized_G6_spectrum") is True
            and scale.get("absolute_scale_unidentified") is True
            and scale.get("threshold_log_shift") == "ln(2)"
        ),
        "reduced_RGE_scope_fail_closed": (
            reduced.get("full_210_quartic_basis_present") is False
            and reduced.get("lambda4_CGC_present") is False
            and reduced.get("dimension6_O6_lock_present") is False
            and reduced.get("two_loop_SO10_complete") is False
            and reduced.get("piecewise_component_threshold_matching_complete")
            is False
        ),
        "formal_only_classification_exact": (
            classification.get(
                "formal_U1_89_abstract_restriction_noninjectivity_proved"
            )
            is True
            and classification.get(
                "exact_physical_EFT_G7_input_nonidentifiability_proved"
            )
            is False
            and classification.get("historical_electroweak_lift_interpretation_valid")
            is False
            and classification.get("mathematical_EFT_G7_closed") is False
            and classification.get("EFT_release_G7_verified") is False
            and classification.get("authoritative_renormalizable_G7_closed")
            is False
            and classification.get("positive_G7_certified") is False
            and classification.get("negative_G7_no_go_certified") is False
        ),
        "integration_schema_exact": set(integration) == expected_integration,
        "positive_requirements_and_release_blockers_retained": (
            len(report.get("positive_closure_requirements", [])) == 5
            and bool(report.get("release_blockers", []))
        ),
    }
    source_bound = all(checks.values())
    integration_completed = bool(
        set(integration) == expected_integration
        and all(integration.get(name) is True for name in expected_integration)
    )
    return {
        "namespace": "FORMAL_U1_89_ABSTRACT_RESTRICTION_AUDIT",
        "artifact": EFT_G7_NONIDENTIFIABILITY_JSON.name,
        "source": EFT_G7_NONIDENTIFIABILITY_SOURCE.name,
        "expected_core_sha256": EFT_G7_NONIDENTIFIABILITY_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": EFT_G7_NONIDENTIFIABILITY_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "source_bound": source_bound,
        "formal_U1_89_abstract_restriction_noninjectivity_proved": bool(
            source_bound
            and classification.get(
                "formal_U1_89_abstract_restriction_noninjectivity_proved"
            )
            is True
        ),
        "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
        "historical_electroweak_lift_interpretation_valid": False,
        "mathematical_EFT_G7_closed": False,
        "EFT_release_G7_verified": False,
        "authoritative_renormalizable_G7_closed": False,
        "positive_G7_certified": False,
        "negative_G7_no_go_certified": False,
        "downstream_integration_completed": integration_completed,
        "formal_U1_89_restriction_map_noninjective": bool(
            source_bound
            and counterexample.get("restriction_map_noninjective") is True
        ),
        "absolute_scale_unidentified": bool(
            source_bound and scale.get("absolute_scale_unidentified") is True
        ),
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "positive_closure_requirements": (
            list(report.get("positive_closure_requirements", []))
            if source_bound
            else []
        ),
        "checks": checks,
    }


def _physical_g7_component_threshold_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the physical PS/SM component kernel without promoting full G7."""
    expected_top_level = {
        "status",
        "contract_id",
        "source_binding",
        "primary_formula_sources",
        "scheme_and_basis",
        "tree_level_matching",
        "heavy_vector_provenance_not_yet_matched",
        "authoritative_field_inventory",
        "interaction_beta_inventory",
        "representation_audits",
        "exact_UV_per_field_gauge_ledgers",
        "UV_two_loop_gauge_flow",
        "matter_component_threshold_theorem",
        "valid_mass_bundles_before_or_at_U1X_breaking",
        "adversarial_guards",
        "completion_matrix",
        "implementation_hooks",
        "release_blockers",
        "checks",
        "n_checks",
        "n_failed",
        "failures",
        "verdict",
        "core_sha256",
    }
    expected_positive = {
        "authoritative_19_Weyl_and_5_scalar_inventory",
        "continuous_gauge_anomaly_cancellation",
        "exact_one_loop_full_inventory_gauge_coefficients",
        "exact_two_loop_nonyukawa_full_inventory_gauge_coefficients",
        "independent_official_PyRATE3_gauge_replay",
        "complete_physical_PS_and_SM_matter_branching",
        "parameterized_one_loop_matter_component_threshold_kernel",
    }
    expected_open = {
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
    }
    expected_blockers = [
        "PHYSICAL_G6_POLE_MASS_MATRICES_WITH_SM_AND_PS_PROVENANCE",
        "HEAVY_VECTOR_GOLDSTONE_GHOST_MATCHING_IN_DECLARED_SCHEME",
        "NORMALIZED_304_WEYL_YUKAWA_TENSOR_EMBEDDINGS",
        "FULL_51_PARAMETER_SCALAR_AND_DIMENSIONFUL_BETA_SYSTEM",
        "DIMENSION_SIX_EFT_OPERATOR_MIXING_IF_EFT_RETAINED",
        "SECOND_INDEPENDENT_FULL_RGE_THRESHOLD_IMPLEMENTATION",
        "BOUNDARY_DATA_AND_MATCHING_SCALES_WITH_COVARIANCE",
    ]
    expected_sources = {
        "authoritative_model": (
            "models\\SO10Z17AxionV20.m",
            "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
            "raw",
        ),
        "authoritative_gauge_source": (
            "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256,
            "raw",
        ),
        "authoritative_gauge_report": (
            "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json",
            AUTHORITATIVE_GAUGE_BETAS_RAW_SHA256,
            "raw",
        ),
        "independent_official_PyRATE3_replay": (
            "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json",
            PYRATE3_GAUGE_REPLAY_RAW_SHA256,
            "raw",
        ),
        "standard_PS_SM_embedding": (
            "exact_126bar_triplet_clebsch_v20.py",
            "c5954c21561f44ea183af17b4cd1205007c0b30021f4cca0a9fc4f96852c103a",
            "portable_text",
        ),
    }
    completion = report.get("completion_matrix", {})
    sources = report.get("source_binding", {})
    inventory = report.get("authoritative_field_inventory", [])
    uv = report.get("UV_two_loop_gauge_flow", {})
    vectors = report.get("heavy_vector_provenance_not_yet_matched", {})
    guards = report.get("adversarial_guards", {})
    embedded_checks = report.get("checks", {})
    checks = {
        "artifact_present": bool(report),
        "status_and_contract_exact": (
            report.get("status")
            == "EXACT_PHYSICAL_MATTER_BRANCHING_AND_PARAMETERIZED_ONE_LOOP_THRESHOLDS_CLOSED__FULL_G7_OPEN"
            and report.get("contract_id")
            == "physical_g7_component_threshold_contract_v20"
        ),
        "schema_exact": set(report) == expected_top_level,
        "core_sha256_exact": (
            report.get("core_sha256")
            == PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256
            and test_raw_sha256
            == PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256
            and markdown_raw_sha256
            == PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256
        ),
        "source_binding_schema_and_hashes_exact": (
            set(sources) == set(expected_sources)
            and all(
                sources.get(name)
                == {"path": path, "sha256": digest, "mode": mode}
                for name, (path, digest, mode) in expected_sources.items()
            )
        ),
        "all_embedded_checks_pass_exactly": (
            report.get("n_checks") == 31
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(embedded_checks) == 31
            and all(value is True for value in embedded_checks.values())
        ),
        "completion_schema_and_truth_values_exact": (
            set(completion) == expected_positive | expected_open
            and all(completion.get(name) is True for name in expected_positive)
            and all(completion.get(name) is False for name in expected_open)
        ),
        "authoritative_inventory_dimensions_exact": (
            isinstance(inventory, list)
            and len(inventory) == 14
            and sum(
                int(row.get("generations", 0))
                for row in inventory
                if row.get("statistics") == "Weyl"
            )
            == 19
            and sum(int(row.get("real_scalar_coordinates", 0)) for row in inventory)
            == 486
            and any(
                row.get("name") == "Delta126bar"
                and row.get("branching_rep") == "126bar"
                for row in inventory
            )
        ),
        "standard_embedding_and_threshold_scheme_exact": (
            report.get("scheme_and_basis", {}).get("hypercharge")
            == "Y=T3R+(B-L)/2"
            and report.get("scheme_and_basis", {}).get(
                "GUT_normalized_abelian_coupling"
            )
            == "g1=sqrt(5/3)*gY"
            and report.get("tree_level_matching", {}).get("PS_to_SM", {}).get(
                "alpha1_inverse"
            )
            == "(2/5) alpha4^-1+(3/5) alpha2R^-1"
        ),
        "parameterized_matter_threshold_scope_exact": (
            report.get("matter_component_threshold_theorem", {}).get(
                "mixed_block_formula"
            )
            == (
                "for identical SM irreps, sum_a ln(M_a/mu)=(1/2) ln det("
                "M_pole^2/mu^2); thresholds are basis invariant"
            )
            and completion.get(
                "parameterized_one_loop_matter_component_threshold_kernel"
            )
            is True
            and completion.get("physical_component_pole_mass_matrices") is False
        ),
        "two_loop_gauge_flow_scoped_exact": (
            uv.get("all_active_a") == {"SO10": "52/3", "X": "10843"}
            and uv.get("all_active_b_nonyukawa")
            == {
                "SO10": {"SO10": "25013/6", "X": "4536"},
                "X": {"SO10": "204120", "X": "7242180"},
            }
            and uv.get("Y4_status")
            == "symbolic only; normalized full Yukawa tensors are required"
            and completion.get("full_two_loop_Yukawa_betas") is False
        ),
        "heavy_vector_matching_counted_but_open": (
            vectors.get("SO10_to_PS", {}).get("real_vector_dimension") == 24
            and vectors.get("PS_to_SM", {}).get("real_vector_dimension") == 9
            and vectors.get("EW_to_QED", {}).get("real_vector_dimension") == 3
            and vectors.get(
                "one_loop_vector_Goldstone_ghost_matching_implemented"
            )
            is False
        ),
        "legacy_and_heuristic_inputs_excluded": (
            guards.get("G89_never_used_as_hypercharge") is True
            and guards.get("reduced_legacy_PyRATE_models_never_used") is True
            and guards.get("incomplete_SARAH_scalar_potential_never_promoted")
            is True
            and not any(
                token in str(report)
                for token in (
                    "two_loop_thresholds_v20.py",
                    "yukawa_rge_2loop_v20.py",
                    "quartic_soft_betas_v20.py",
                )
            )
        ),
        "release_blockers_exact": report.get("release_blockers") == expected_blockers,
        "full_physical_math_release_G7_fail_closed": (
            completion.get("physical_G6_input_available") is False
            and completion.get("mathematical_G7_closed") is False
            and completion.get("release_G7_verified") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT",
        "artifact": PHYSICAL_G7_COMPONENT_THRESHOLD_JSON.name,
        "markdown": PHYSICAL_G7_COMPONENT_THRESHOLD_MD.name,
        "source": PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE.name,
        "test": PHYSICAL_G7_COMPONENT_THRESHOLD_TEST.name,
        "expected_core_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_markdown_raw_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256,
        "markdown_raw_sha256": markdown_raw_sha256,
        "expected_source_raw_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "source_bound": source_bound,
        "authoritative_inventory_closed": bool(
            source_bound
            and completion.get("authoritative_19_Weyl_and_5_scalar_inventory")
            is True
        ),
        "continuous_gauge_anomalies_closed": bool(
            source_bound
            and completion.get("continuous_gauge_anomaly_cancellation") is True
        ),
        "exact_one_loop_gauge_coefficients_closed": bool(
            source_bound
            and completion.get("exact_one_loop_full_inventory_gauge_coefficients")
            is True
        ),
        "exact_two_loop_nonyukawa_gauge_flow_closed": bool(
            source_bound
            and completion.get(
                "exact_two_loop_nonyukawa_full_inventory_gauge_coefficients"
            )
            is True
        ),
        "independent_official_PyRATE3_gauge_replay_closed": bool(
            source_bound
            and completion.get("independent_official_PyRATE3_gauge_replay")
            is True
        ),
        "physical_PS_SM_matter_branching_closed": bool(
            source_bound
            and completion.get("complete_physical_PS_and_SM_matter_branching")
            is True
        ),
        "parameterized_one_loop_matter_threshold_kernel_closed": bool(
            source_bound
            and completion.get(
                "parameterized_one_loop_matter_component_threshold_kernel"
            )
            is True
        ),
        "physical_component_pole_mass_matrices_closed": False,
        "heavy_vector_matching_closed": False,
        "full_two_loop_Yukawa_scalar_dimensionful_EFT_system_closed": False,
        "physical_G7_closed": False,
        "mathematical_G7_closed": False,
        "release_G7_verified": False,
        "authoritative_renormalizable_G7_closed": False,
        "positive_G7_certified": False,
        "negative_G7_no_go_certified": False,
        "downstream_integration_completed": bool(source_bound),
        "release_blockers": expected_blockers if source_bound else [],
        "checks": checks,
    }


def _normalized_so10_yukawa_cgc_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind exact representation CGCs while leaving flavor/RGE/full G7 open."""
    expected_top_level = {
        "status",
        "contract_id",
        "dependencies",
        "conventions",
        "canonical_304_weyl_inventory",
        "weyl_multiplet_count",
        "weyl_component_count",
        "normalized_tensors",
        "chirality_obstruction",
        "covariance",
        "symmetric_square_theorem",
        "declared_yukawa_closure",
        "total_generic_flavor_sparse_support_count",
        "scope",
        "blockers",
        "checks",
        "core_sha256",
    }
    expected_scope = {
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
    expected_blockers = [
        "Fix the conversion between this explicit -1/2 identical-Weyl convention and SARAH's implicit Dot contractions.",
        "Supply or fit the symbolic flavor tensors and their boundary conditions.",
        "Compile independently replayed one- and two-loop Yukawa, scalar and dimensionful beta functions.",
        "Derive physical component masses, mixing matrices and finite threshold matching before claiming G7.",
    ]
    expected_dependencies = {
        "authoritative_model": {
            "path": "models\\SO10Z17AxionV20.m",
            "sha256": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
            "mode": "raw",
        },
        "audited_clifford_backend": {
            "path": "spin10_referee_audit.py",
            "sha256": "daf80f5ab2b4480e5e03b025bd685dd1ffdce91a4cb0435774dd52ad702b72c9",
            "mode": "portable_text",
        },
        "canonical_scalar_five_form_backend": {
            "path": "direct_phi_h_sigmabar_tensor_v20.py",
            "sha256": "3a87470a06362a2a4c05eac6b71fe9cd4cd6c9b8a41732786184cbfeae89fac4",
            "mode": "portable_text",
        },
        "standard_embedding_and_hodge_audit": {
            "path": "exact_126bar_triplet_clebsch_v20.py",
            "sha256": "c5954c21561f44ea183af17b4cd1205007c0b30021f4cca0a9fc4f96852c103a",
            "mode": "portable_text",
        },
    }
    expected_positive_checks = {
        "authoritative_sources_match_frozen_hashes",
        "all_ten_declared_yukawa_symbols_found",
        "canonical_inventory_has_19_weyl_multiplets",
        "canonical_inventory_has_304_weyl_components",
        "minus_chirality_has_standard_model_16_weights",
        "plus_chirality_is_conjugate_16bar",
        "vector_has_ten_symmetric_matrices",
        "vector_normalized_gram_is_identity",
        "physical_126bar_has_126_symmetric_matrices",
        "physical_126bar_normalized_gram_is_identity",
        "physical_126bar_complement_shortcut_agrees",
        "opposite_spinor_chirality_annihilates_physical_126bar",
        "ten_and_126bar_are_exactly_orthogonal",
        "ten_plus_126bar_complete_symmetric_square",
        "singlet_duality_map_is_unitary",
        "singlet_dual_basis_normalized_gram_is_identity",
        "all_45_vector_covariance_residuals_zero",
        "all_45_126bar_covariance_residuals_zero",
        "all_45_singlet_covariance_residuals_zero",
        "vector_sparse_count_is_160",
        "physical_126bar_sparse_count_is_2016",
        "singlet_sparse_count_is_16",
        "all_embedded_support_indices_lie_in_304_inventory",
        "all_declared_representation_cgcs_closed",
    }
    expected_negative_checks = {
        "flavor_boundary_values_closed",
        "sarah_symbol_normalization_closed",
        "full_yukawa_rge_closed",
        "full_physical_G7_closed",
    }
    tensors = report.get("normalized_tensors", {})
    closure = report.get("declared_yukawa_closure", [])
    checks_report = report.get("checks", {})
    scope = report.get("scope", {})
    checks = {
        "artifact_present": bool(report),
        "status_contract_and_schema_exact": (
            report.get("status")
            == "EXACT_NORMALIZED_SO10_REPRESENTATION_YUKAWA_CGCS_CLOSED__FLAVOR_RGE_AND_FULL_G7_OPEN"
            and report.get("contract_id")
            == "exact_normalized_so10_yukawa_cgcs_v20"
            and set(report) == expected_top_level
        ),
        "core_and_all_four_raw_pins_exact": (
            report.get("core_sha256") == NORMALIZED_YUKAWA_CGCS_CORE_SHA256
            and raw_sha256 == NORMALIZED_YUKAWA_CGCS_RAW_SHA256
            and source_raw_sha256 == NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256
            and test_raw_sha256 == NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256
            and markdown_raw_sha256 == NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256
        ),
        "dependency_schema_paths_hashes_modes_exact": report.get("dependencies")
        == expected_dependencies,
        "completion_scope_exact": scope == expected_scope,
        "embedded_checks_schema_and_truth_values_exact": (
            set(checks_report) == expected_positive_checks | expected_negative_checks
            and all(checks_report.get(name) is True for name in expected_positive_checks)
            and all(checks_report.get(name) is False for name in expected_negative_checks)
        ),
        "canonical_304_component_inventory_exact": (
            report.get("weyl_multiplet_count") == 19
            and report.get("weyl_component_count") == 304
            and isinstance(report.get("canonical_304_weyl_inventory"), list)
            and len(report.get("canonical_304_weyl_inventory", [])) == 9
            and sum(
                int(row.get("generations", 0)) * 16
                for row in report.get("canonical_304_weyl_inventory", [])
            )
            == 304
        ),
        "normalized_10_126bar_and_singlet_tensors_exact": (
            set(tensors) == {"10", "126bar", "singlet_dual_basis"}
            and tensors.get("10", {}).get("shape") == [10, 16, 16]
            and tensors.get("10", {}).get("denominator") == 4
            and tensors.get("10", {}).get("nonzero_count") == 160
            and tensors.get("10", {}).get("numerator_sha256_i16_real_imag_C_order")
            == "29d520d5b7e4a8fe2f35ac6e124c56a3947e04796b1ea1ac0cda0ecabc244a49"
            and tensors.get("126bar", {}).get("shape") == [126, 16, 16]
            and tensors.get("126bar", {}).get("denominator") == 8
            and tensors.get("126bar", {}).get("nonzero_count") == 2016
            and tensors.get("126bar", {}).get(
                "numerator_sha256_i16_real_imag_C_order"
            )
            == "659a997d9b97adb56cb0269ddf53197c3e0049e0359aea42fb7983139d936daf"
            and tensors.get("singlet_dual_basis", {}).get("shape") == [1, 16, 16]
            and tensors.get("singlet_dual_basis", {}).get("nonzero_count") == 16
        ),
        "chirality_covariance_and_sym2_exact": (
            report.get("chirality_obstruction", {}).get(
                "correct_minus_chirality_contraction_rank"
            )
            == 126
            and report.get("chirality_obstruction", {}).get(
                "wrong_plus_chirality_is_identically_zero"
            )
            is True
            and report.get("covariance", {}).get("generators_tested_per_channel")
            == 45
            and report.get("covariance", {}).get("exact_integer_residual_maxima")
            == {"10": 0, "126bar": 0, "singlet": 0}
            and report.get("symmetric_square_theorem", {}).get("dim_Sym2_16")
            == 136
            and report.get("symmetric_square_theorem", {}).get("10_plus_126")
            == 136
            and report.get("symmetric_square_theorem", {}).get(
                "orthonormal_complete_projector_verified_exactly"
            )
            is True
        ),
        "ten_declared_sparse_embeddings_scoped_exact": (
            isinstance(closure, list)
            and len(closure) == 10
            and all(row.get("representation_CGC_closed") is True for row in closure)
            and all(
                row.get("flavor_tensor_preserved_symbolically") is True
                for row in closure
            )
            and report.get("total_generic_flavor_sparse_support_count") == 21056
        ),
        "sarah_and_flavor_normalization_explicitly_open": (
            report.get("conventions", {}).get("sarah_Dot_conversion")
            == "open; no numerical conversion factor inferred"
            and scope.get("flavor_tensor_values_or_textures") is False
            and scope.get("sarah_implicit_contraction_normalization") is False
        ),
        "full_yukawa_RGE_threshold_and_G7_fail_closed": (
            scope.get("one_or_two_loop_Yukawa_betas") is False
            and scope.get("threshold_matching_and_running") is False
            and scope.get("full_yukawa_sector") is False
            and scope.get("mathematical_G7") is False
            and scope.get("release_G7") is False
            and report.get("blockers") == expected_blockers
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "NORMALIZED_SO10_YUKAWA_CGC_CONTRACT",
        "artifact": NORMALIZED_YUKAWA_CGCS_JSON.name,
        "markdown": NORMALIZED_YUKAWA_CGCS_MD.name,
        "source": NORMALIZED_YUKAWA_CGCS_SOURCE.name,
        "test": NORMALIZED_YUKAWA_CGCS_TEST.name,
        "expected_core_sha256": NORMALIZED_YUKAWA_CGCS_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": NORMALIZED_YUKAWA_CGCS_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256,
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "normalized_10_CGCs_closed": bool(source_bound),
        "normalized_126bar_CGCs_closed": bool(source_bound),
        "normalized_singlet_duality_CGC_closed": bool(source_bound),
        "canonical_304_Weyl_sparse_embedding_closed": bool(source_bound),
        "all_declared_representation_CGCs_closed": bool(source_bound),
        "flavor_boundary_values_closed": False,
        "SARAH_Dot_conversion_closed": False,
        "full_one_two_loop_Yukawa_betas_closed": False,
        "physical_threshold_matching_and_running_closed": False,
        "full_yukawa_sector_closed": False,
        "physical_G7_closed": False,
        "mathematical_G7_closed": False,
        "release_G7_verified": False,
        "authoritative_renormalizable_G7_closed": False,
        "blockers": expected_blockers if source_bound else [],
        "checks": checks,
    }


def _physical_sm_vacuum_truth_overlay(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Supersede the historical physical-SM label without promoting G3-G7."""
    expected_top_level = {
        "schema",
        "model_contract_id",
        "status",
        "source_binding",
        "target",
        "exact_symmetry",
        "live_local_feasibility",
        "exact_reconstructed_Hessian_rank",
        "exact_radial_EFT_BFB_completion",
        "squared_stationarity_global_EFT_completion",
        "closure_claims",
        "supersession",
        "logical_summary",
        "next_required_proofs",
        "integrity",
    }
    expected_claims = {
        "physical_SM_G3": False,
        "physical_SM_G4": False,
        "physical_SM_G5": False,
        "physical_SM_G6": False,
        "physical_SM_G7": False,
    }
    expected_next = [
        "derive every reconstructed Q+sqrt(2)Q stationarity entry directly from source algebra",
        "derive every reconstructed rational Hessian entry directly from source algebra",
        "classify every zero of Vren+1 and grad(Vren) to prove the complete global equality orbit",
        "derive the physical pole spectrum and threshold matching only afterward",
    ]
    source_binding = report.get("source_binding", {})
    dependencies = source_binding.get("dependencies", {})
    dependency_validation = dependencies.get("validation", {})
    target = report.get("target", {})
    symmetry = report.get("exact_symmetry", {})
    hessian = report.get("exact_reconstructed_Hessian_rank", {})
    reconstruction = hessian.get("reconstruction", {})
    radial = report.get("exact_radial_EFT_BFB_completion", {})
    squared = report.get("squared_stationarity_global_EFT_completion", {})
    summary = report.get("logical_summary", {})
    supersession = report.get("supersession", {})
    claims = report.get("closure_claims", {})
    checks = {
        "artifact_present": bool(report),
        "schema_contract_status_exact": (
            report.get("schema") == "physical_sm_vacuum_local_feasibility_v1"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("status")
            == "PHYSICAL_SM_RECONSTRUCTED_GLOBAL_EFT_CERTIFICATE__DIRECT_SOURCE_ALGEBRA_AND_GLOBAL_EQUALITY_ORBIT_OPEN"
        ),
        "top_level_schema_exact": set(report) == expected_top_level,
        "core_and_all_four_raw_pins_exact": (
            report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_VACUUM_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_VACUUM_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_VACUUM_MD_RAW_SHA256
        ),
        "self_source_binding_exact": (
            source_binding.get("path") == PHYSICAL_SM_VACUUM_SOURCE.name
            and source_binding.get("sha256")
            == PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256
            and source_binding.get("portable_lf_sha256")
            == PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256
        ),
        "twenty_dependency_bindings_validated": (
            isinstance(dependencies.get("files"), dict)
            and len(dependencies.get("files", {})) == 20
            and dependency_validation.get("dependency_file_count") == 20
            and dependency_validation.get("all_dependency_files_present") is True
            and dependency_validation.get(
                "provenance_core_matches_imported_expected_pin"
            )
            is True
            and dependency_validation.get("scalar_contract_frozen_has_zero_failures")
            is True
            and dependency_validation.get("G2_derivative_audit_frozen_has_zero_failures")
            is True
            and dependency_validation.get("physical_quotient_frozen_certified")
            is True
        ),
        "standard_SM_target_and_stabilizer_exact": (
            target.get("chart_dimension") == 486
            and target.get("lattice_denominator") == 20
            and target.get("standard_Q3_annihilates_full_target") is True
            and target.get("bare_G89_annihilates_full_target") is False
            and symmetry.get("exact_stabilizer_is_su3C_plus_u1em") is True
            and symmetry.get("all_expected_ranks_proved") is True
            and symmetry.get("standard_unbroken_basis", {}).get("dimension") == 9
            and symmetry.get("standard_unbroken_basis", {}).get(
                "annihilates_target_exactly"
            )
            is True
        ),
        "reconstructed_exact_linear_algebra_scoped": (
            hessian.get("exact_reconstructed_rank") == 448
            and hessian.get("exact_reconstructed_nullity") == 38
            and hessian.get("kernel_equals_full_symmetry_tangent_span") is True
            and reconstruction.get("canonical_sparse_matrix_sha256")
            == "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458"
            and reconstruction.get("source_algebra_derivation_complete") is False
            and reconstruction.get("denominator_bound_source_derived") is False
            and hessian.get("source_proof_grade") is False
        ),
        "constructed_EFT_completions_scoped_not_physical": (
            radial.get("nonnegative_for_all_real_fields") is True
            and radial.get("does_not_prove_target_global_minimum") is True
            and squared.get("nonnegative_for_all_real_fields") is True
            and squared.get("target_is_a_global_minimum") is True
            and squared.get("global_zero_locus_classification_open") is True
        ),
        "logical_boundary_exact": (
            summary.get("physical_SM_target_exactly_constructed") is True
            and summary.get("standard_SU3C_x_U1em_stabilizer_proved") is True
            and summary.get("exact_rational_witness_on_reconstructed_stationarity_lattice")
            is True
            and summary.get("exact_rank_448_on_reconstructed_Hessian_lattice")
            is True
            and summary.get("source_bound_exact_stationary_PSD_witness_available")
            is False
            and summary.get("source_bound_global_equality_orbit_proved") is False
            and summary.get("global_minimum_orbit_classified") is False
            and summary.get("physical_G6_closed") is False
        ),
        "historical_stabilizer_label_superseded_exact": (
            supersession.get("old_selected_EFT_target_actual_stabilizer")
            == "SU(3)_C x U(1)_89"
            and supersession.get("old_selected_EFT_target_was_standard_SU3C_x_U1em")
            is False
            and supersession.get("new_target_exact_stabilizer")
            == "standard SU(3)_C x U(1)_em"
            and supersession.get(
                "old_abstract_EFT_mathematical_theorems_may_remain_true_in_formal_scope"
            )
            is True
            and supersession.get(
                "old_abstract_EFT_theorems_do_not_close_physical_SM_G3_G4_G5"
            )
            is True
        ),
        "all_physical_SM_G3_through_G7_fail_closed": claims == expected_claims,
        "next_required_proofs_exact": report.get("next_required_proofs")
        == expected_next,
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_VACUUM_TRUTH_OVERLAY",
        "artifact": PHYSICAL_SM_VACUUM_JSON.name,
        "markdown": PHYSICAL_SM_VACUUM_MD.name,
        "source": PHYSICAL_SM_VACUUM_SOURCE.name,
        "test": PHYSICAL_SM_VACUUM_TEST.name,
        "expected_core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_SM_VACUUM_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_SM_VACUUM_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": PHYSICAL_SM_VACUUM_MD_RAW_SHA256,
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "physical_SM_target_exactly_constructed": bool(
            source_bound and summary.get("physical_SM_target_exactly_constructed")
        ),
        "standard_SU3C_x_U1em_stabilizer_proved": bool(
            source_bound and summary.get("standard_SU3C_x_U1em_stabilizer_proved")
        ),
        "reconstructed_stationary_transverse_PSD_witness_available": bool(
            source_bound
            and summary.get(
                "exact_rational_witness_on_reconstructed_stationarity_lattice"
            )
            and summary.get("exact_rank_448_on_reconstructed_Hessian_lattice")
        ),
        "direct_source_algebra_stationary_PSD_witness_available": False,
        "source_bound_global_equality_orbit_proved": False,
        "old_selected_EFT_stabilizer_label_superseded": bool(
            source_bound
            and supersession.get("old_selected_EFT_target_was_standard_SU3C_x_U1em")
            is False
        ),
        "old_selected_EFT_target_actual_stabilizer": (
            "SU(3)_C x U(1)_89" if source_bound else None
        ),
        "old_abstract_EFT_mathematical_G3_G4_G5_retained_in_formal_scope": bool(
            source_bound
            and supersession.get(
                "old_abstract_EFT_mathematical_theorems_may_remain_true_in_formal_scope"
            )
        ),
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "physical_SM_G6_closed": False,
        "physical_SM_G7_closed": False,
        "release_verified": False,
        "authoritative_renormalizable_closure": False,
        "next_required_proofs": expected_next if source_bound else [],
        "checks": checks,
    }


def _physical_sm_source_algebra_equality_frontier_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the exact radial equality theorem without promoting physical G3--G5."""
    expected_top_level = {
        "schema",
        "status",
        "model_contract_id",
        "n_checks",
        "n_failed",
        "failures",
        "checks",
        "source_bindings",
        "source_row_lattice_frontier",
        "exact_radial_equality",
        "closure_claims",
        "next_required_calculation",
        "integrity",
    }
    expected_checks = {
        "foundation_core_pin_matches": True,
        "all_37_nonzero_witness_parameters_are_Hermitian": True,
        "observed_source_Hessian_row_lcm_is_126000": True,
        "aggregate_reconstructed_Hessian_lcm_is_frozen": True,
        "aggregate_cancellation_remains_fail_closed": True,
        "exact_radial_gcd_is_t_minus_1": True,
        "full_equality_orbit_remains_fail_closed": True,
        "physical_G3_G4_G5_remain_false": True,
    }
    expected_claims = {
        "radial_stationary_equality_classified_exactly": True,
        "direct_source_algebra_stationary_Hessian_available": False,
        "complete_global_equality_orbit_proved": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "old_formal_U1_89_EFT_scope_promoted": False,
    }
    expected_next = [
        "replace every active float projector row by exact integer/Fraction arithmetic and prove the fixed row lattices before evaluation",
        "prove the summed stationary Hessian numerator and its rank/PSD without continued-fraction reconstruction",
        "solve or exclude all non-radial common zeros of Vren+1 and grad(Vren), modulo SO(10)xU(1)_XxPQ",
    ]
    source = report.get("source_row_lattice_frontier", {})
    radial = report.get("exact_radial_equality", {})
    binding = report.get("source_bindings", {}).get("foundation", {})
    claims = report.get("closure_claims", {})
    checks = {
        "artifact_schema_status_and_full_shape_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "physical_sm_source_algebra_equality_frontier_v20"
            and report.get("status")
            == "RADIAL_EQUALITY_CLOSED__FULL_SOURCE_ALGEBRA_AND_EQUALITY_ORBIT_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("n_checks") == 8
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and report.get("checks") == expected_checks
        ),
        "core_and_all_four_raw_pins_exact": (
            report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_SOURCE_EQUALITY_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_SOURCE_EQUALITY_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_SM_SOURCE_EQUALITY_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_SOURCE_EQUALITY_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_SOURCE_EQUALITY_MD_RAW_SHA256
        ),
        "foundation_binding_exact": (
            set(report.get("source_bindings", {})) == {"foundation"}
            and binding
            == {
                "source": PHYSICAL_SM_VACUUM_SOURCE.name,
                "source_raw_sha256": PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
                "source_portable_lf_sha256": PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
                "json": PHYSICAL_SM_VACUUM_JSON.name,
                "core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
                "expected_core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
                "core_pin_matches": True,
            }
        ),
        "observed_row_lattice_is_diagnostic_not_source_proof": (
            source.get("evidence_kind")
            == "float_compiler_rational_lattice_census_only"
            and source.get("supported_parameter_count") == 37
            and source.get(
                "all_supported_parameters_are_Hermitian_lambda_components"
            )
            is True
            and source.get("Hessian_rows", {}).get("observed_denominator_lcm")
            == 126000
            and source.get("Hessian_rows", {}).get(
                "source_derived_denominator_bound"
            )
            is False
            and source.get("reconstructed_aggregate_Hessian_nonzero_entries")
            == 5840
            and source.get("reconstructed_aggregate_Hessian_denominator_lcm")
            == 6300103327590
            and source.get("aggregate_cancellation_source_proved") is False
            and source.get("direct_exact_projector_arithmetic_used_for_rows")
            is False
            and source.get("source_algebra_derivation_complete") is False
            and source.get("proof_grade") is False
        ),
        "radial_gcd_theorem_exact_and_scoped": (
            radial.get("evidence_kind")
            == "exact_Q_homogeneity_and_univariate_polynomial_gcd"
            and radial.get("radial_line") == "q=t*q_star with real t"
            and radial.get("coefficient_sum_V_at_t1") == "-1"
            and radial.get("gcd_V_plus_1_and_dV_dt_monic") == "t - 1"
            and radial.get("V_at_t1_is_minus_one") is True
            and radial.get("target_is_stationary_on_radial_line") is True
            and radial.get("target_is_only_radial_stationary_equality_point")
            is True
            and radial.get("full_486_field_equality_orbit_classified") is False
            and radial.get("physical_SM_G3_closed") is False
            and radial.get("physical_SM_G4_closed") is False
            and radial.get("physical_SM_G5_closed") is False
        ),
        "closure_boundary_and_next_calculation_exact": (
            claims == expected_claims
            and report.get("next_required_calculation") == expected_next
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER",
        "artifact": PHYSICAL_SM_SOURCE_EQUALITY_JSON.name,
        "markdown": PHYSICAL_SM_SOURCE_EQUALITY_MD.name,
        "source": PHYSICAL_SM_SOURCE_EQUALITY_SOURCE.name,
        "test": PHYSICAL_SM_SOURCE_EQUALITY_TEST.name,
        "expected_core_sha256": PHYSICAL_SM_SOURCE_EQUALITY_CORE_SHA256,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_SM_SOURCE_EQUALITY_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": PHYSICAL_SM_SOURCE_EQUALITY_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_SM_SOURCE_EQUALITY_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": PHYSICAL_SM_SOURCE_EQUALITY_MD_RAW_SHA256,
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "radial_stationary_equality_classified_exactly": bool(
            source_bound
            and radial.get("target_is_only_radial_stationary_equality_point")
        ),
        "radial_gcd": "t - 1" if source_bound else None,
        "observed_source_Hessian_row_lcm": 126000 if source_bound else None,
        "reconstructed_aggregate_Hessian_lcm": (
            6300103327590 if source_bound else None
        ),
        "direct_source_algebra_stationary_Hessian_available": False,
        "complete_nonradial_equality_orbit_proved": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "old_formal_U1_89_EFT_scope_promoted": False,
        "release_verified": False,
        "next_required_calculation": expected_next if source_bound else [],
        "checks": checks,
    }


def _physical_sm_five_amplitude_equality_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the exact five-amplitude equality theorem without promoting G3--G5."""
    expected_top_level = {
        "schema",
        "status",
        "model_contract_id",
        "n_checks",
        "n_failed",
        "failures",
        "checks",
        "source_bindings",
        "restriction",
        "exact_polynomial",
        "exact_Groebner_certificate",
        "discrete_variants",
        "closure_claims",
        "remaining_scope",
        "integrity",
    }
    expected_embedded_checks = {
        "all_source_portable_lf_and_core_pins_match",
        "source_table_has_28_nonzero_target_contributions",
        "all_37_witness_rows_have_even_H_Sigma_S_Phi17_parity",
        "aggregate_polynomial_has_21_monomials",
        "aggregate_denominator_is_frozen",
        "exact_target_value_is_minus_one",
        "all_five_target_slice_derivatives_vanish",
        "Groebner_basis_is_exact_expected_basis",
        "ideals_equal_by_mutual_exact_reduction",
        "exactly_16_real_discrete_sign_variants",
        "target_is_strict_minimum_on_five_amplitude_slice",
        "full_486_and_physical_G3_G4_G5_remain_fail_closed",
    }
    expected_claims = {
        "exact_radial_theorem_strictly_extended": True,
        "five_real_amplitude_slice_stationary_equality_classified": True,
        "full_486_field_stationary_equality_classified": False,
        "declared_continuous_symmetry_orbit_equivalence_of_16_variants_proved": False,
        "direct_source_algebra_full_486_Hessian_available": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    expected_remaining_scope = [
        "derive the complete 486-real stationary Hessian directly from integer/Gaussian-integer projector algebra",
        "classify stationary equality points with arbitrary non-amplitude field components",
        "classify the sixteen discrete variants under the declared continuous symmetry only with explicit exact group elements",
    ]
    core_keys = (
        "schema",
        "status",
        "model_contract_id",
        "source_bindings",
        "restriction",
        "exact_polynomial",
        "exact_Groebner_certificate",
        "discrete_variants",
        "closure_claims",
        "remaining_scope",
    )
    embedded_checks = report.get("checks", {})
    source_bindings = report.get("source_bindings", {})
    binding_files = source_bindings.get("files", {})
    restriction = report.get("restriction", {})
    polynomial = report.get("exact_polynomial", {})
    certificate = report.get("exact_Groebner_certificate", {})
    variants = report.get("discrete_variants", {})
    claims = report.get("closure_claims", {})
    core_payload = (
        {key: report[key] for key in core_keys}
        if all(key in report for key in core_keys)
        else {}
    )
    expected_basis = [
        "h**2 - 1",
        "d**2 - 1",
        "s**2 - 1",
        "x**2 - 1",
        "p - 1",
    ]
    checks = {
        "artifact_schema_status_core_and_raw_pins_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "exact_physical_sm_five_amplitude_equality_v20"
            and report.get("status")
            == "EXACT_FIVE_AMPLITUDE_STATIONARY_EQUALITY_CLASSIFIED__FULL_486_ORBIT_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE_RAW_SHA256
            and test_raw_sha256
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST_RAW_SHA256
            and markdown_raw_sha256
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD_RAW_SHA256
        ),
        "embedded_checks_and_dependency_binding_exact": (
            set(embedded_checks) == expected_embedded_checks
            and all(
                embedded_checks.get(name) is True
                for name in expected_embedded_checks
            )
            and report.get("n_checks") == 12
            and report.get("n_failed") == 0
            and report.get("failures") == []
            and len(binding_files) == 14
            and all(
                set(row)
                == {
                    "portable_lf_sha256",
                    "expected_portable_lf_sha256",
                    "matches",
                }
                and row.get("portable_lf_sha256")
                == row.get("expected_portable_lf_sha256")
                and row.get("matches") is True
                for row in binding_files.values()
            )
            and all(
                _file_sha256(ROOT / path) == row.get("portable_lf_sha256")
                for path, row in binding_files.items()
            )
            and source_bindings.get("foundation_core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
            and source_bindings.get("expected_foundation_core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
            and source_bindings.get("all_portable_lf_and_core_pins_match") is True
        ),
        "five_real_amplitude_restriction_exact_and_reconstructed": (
            restriction.get("ambient_real_field_dimension") == 486
            and restriction.get("slice_dimension") == 5
            and restriction.get("map")
            == "(Phi,H,Sigma,S,Phi17)=(p Phi*,h H*,d Sigma*,s S*,x Phi17*)"
            and restriction.get("amplitudes_are_real") is True
            and restriction.get("polynomial_fitting_or_float_sampling_used")
            is False
            and restriction.get(
                "exact_algebra_is_conditional_on_frozen_upstream_witness_table"
            )
            is True
            and restriction.get(
                "witness_coefficients_directly_derived_from_integer_projector_source_algebra"
            )
            is False
            and restriction.get(
                "target_invariant_table_is_portable_lf_hash_bound_to_normalized_source_modules"
            )
            is True
            and restriction.get(
                "target_invariant_table_independently_rederived_by_integer_arithmetic_in_this_artifact"
            )
            is False
            and restriction.get("renormalizable_witness_nonzero_parameter_count")
            == 37
            and restriction.get("nonzero_target_contribution_count") == 28
            and polynomial.get("common_denominator") == 1050017221265
            and polynomial.get("aggregate_monomial_count") == 21
            and len(polynomial.get("source_contributions", [])) == 28
        ),
        "Groebner_ideal_and_16_real_sign_variants_exact": (
            certificate.get("coefficient_domain") == "QQ"
            and certificate.get("monomial_order") == "grevlex"
            and certificate.get("variables") == ["p", "h", "d", "s", "x"]
            and certificate.get("source_generator_count") == 6
            and len(certificate.get("source_generators", [])) == 6
            and certificate.get("reduced_Groebner_basis") == expected_basis
            and certificate.get("expected_reduced_Groebner_basis")
            == expected_basis
            and certificate.get("observed_basis_equals_expected") is True
            and certificate.get("source_ideal_contained_in_expected_ideal")
            is True
            and certificate.get("expected_ideal_contained_in_source_ideal")
            is True
            and certificate.get("ideals_equal_by_mutual_exact_reduction")
            is True
            and certificate.get("ideal_zero_dimensional") is True
            and certificate.get(
                "ideal_is_radical_from_squarefree_separated_basis"
            )
            is True
            and certificate.get("complex_solution_count_with_multiplicity")
            == 16
            and certificate.get("all_solutions_real") is True
            and certificate.get("solution_set")
            == "p=1; h,d,s,x independently in {-1,+1}"
            and len(
                certificate.get(
                    "target_slice_Hessian_leading_principal_minors", []
                )
            )
            == 5
            and certificate.get("target_slice_Hessian_positive_definite")
            is True
        ),
        "discrete_not_continuous_orbit_boundary_exact": (
            variants.get("count") == 16
            and variants.get("description")
            == "p=1 with independent signs of h,d,s,x"
            and variants.get("full_witness_support_row_count") == 37
            and variants.get("zero_at_target_but_parity_checked_row_count") == 9
            and variants.get("all_support_rows_even_in_h_d_s_x") is True
            and variants.get("exact_discrete_sign_symmetries_of_selected_witness")
            is True
            and variants.get(
                "full_486_stationarity_inherited_from_upstream_target_under_discrete_sign_symmetry"
            )
            is True
            and variants.get(
                "continuous_SO10_x_U1X_x_PQ_orbit_equivalence_classified"
            )
            is False
        ),
        "closure_boundary_and_remaining_scope_exact": (
            claims == expected_claims
            and report.get("remaining_scope") == expected_remaining_scope
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY",
        "artifact": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON.name,
        "markdown": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD.name,
        "source": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE.name,
        "test": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST.name,
        "expected_core_sha256": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": (
            PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD_RAW_SHA256
        ),
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "exact_radial_theorem_strictly_extended": bool(source_bound),
        "five_real_amplitude_slice_stationary_equality_classified": bool(
            source_bound
        ),
        "exact_real_discrete_sign_variant_count": 16 if source_bound else None,
        "target_strict_minimum_on_five_amplitude_slice": bool(source_bound),
        "full_486_field_stationary_equality_classified": False,
        "continuous_symmetry_orbit_equivalence_of_16_variants_proved": False,
        "direct_source_algebra_full_486_Hessian_available": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "release_verified": False,
        "remaining_scope": expected_remaining_scope if source_bound else [],
        "checks": checks,
    }


def _semantic_json_file_sha256(path: Path) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ""
    return _canonical_json_line_sha256(value)


def _physical_sm_hard_projector_hessians_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind ten exact source Hessians while keeping the 37-row theorem open."""
    expected_top = {
        "schema", "status", "model_contract_id", "source_bindings", "target",
        "arithmetic_contract", "certified_rows", "family_certificates",
        "scope_accounting", "claims", "checks", "n_checks", "n_failed",
        "failures", "integrity",
    }
    expected_claims = {
        "exact_source_algebra_Hessians_for_all_10_O27_O44_rows": True,
        "exact_source_algebra_Hessians_for_all_37_active_witness_rows": False,
        "exact_full_witness_aggregate_stationarity": False,
        "exact_full_witness_symmetry_kernel": False,
        "exact_full_witness_rank_448_and_PSD": False,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    expected_check_names = {
        "all_source_portable_lf_pins_match",
        "physical_target_is_exact_20_lattice_vector_in_486_chart",
        "exactly_10_hard_rows_certified",
        "all_10_Hessians_are_entrywise_symmetric_over_Q",
        "all_10_exact_Euler_jet_identities_hold",
        "O27_projector_sum_reconstructs_direct_source_Hessian_exactly",
        "O44_projector_sum_reconstructs_direct_source_Hessian_exactly",
        "all_signed_int64_preflights_pass",
        "remaining_active_row_count_is_explicitly_27",
        "full_37_row_aggregate_claim_is_fail_closed",
        "global_equality_and_G3_G4_G5_claims_are_fail_closed",
    }
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    target = report.get("target", {})
    arithmetic = report.get("arithmetic_contract", {})
    rows = report.get("certified_rows", [])
    families = report.get("family_certificates", {})
    scope = report.get("scope_accounting", {})
    claims = report.get("claims", {})
    embedded_checks = report.get("checks", {})
    core_payload = {key: value for key, value in report.items() if key != "integrity"}
    row_ids = [row.get("direction_id") for row in rows]
    checks = {
        "artifact_schema_status_core_and_raw_pins_exact": (
            set(report) == expected_top
            and report.get("schema") == "exact_physical_sm_hard_projector_hessians_v20"
            and report.get("status") == "EXACT_TEN_HARD_PROJECTOR_HESSIANS__FULL_37_ROW_AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD_RAW_SHA256
        ),
        "six_live_portable_dependencies_exact": (
            bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 6
            and all(
                set(row) == {"portable_lf_sha256", "expected_portable_lf_sha256", "matches"}
                and row.get("matches") is True
                and row.get("portable_lf_sha256")
                == row.get("expected_portable_lf_sha256")
                == _file_sha256(ROOT / relative)
                for relative, row in files.items()
            )
        ),
        "ten_exact_486_Hessians_and_family_reconstruction": (
            len(rows) == 10
            and len(set(row_ids)) == 10
            and row_ids == sorted(row_ids)
            and sum(name.startswith("O27_") for name in row_ids) == 4
            and sum(name.startswith("O44_") for name in row_ids) == 6
            and all(
                row.get("Hessian", {}).get("dimension") == 486
                and row.get("Hessian", {}).get("symmetric_entrywise_over_Q") is True
                and isinstance(row.get("Hessian", {}).get("canonical_sparse_rational_sha256"), str)
                and len(row.get("Hessian", {}).get("canonical_sparse_rational_sha256", "")) == 64
                and row.get("exact_target_jet_from_homogeneity", {}).get("Hq_equals_3_gradient_exactly") is True
                and row.get("exact_target_jet_from_homogeneity", {}).get("q_dot_gradient_equals_4V_exactly") is True
                for row in rows
            )
            and families.get("O27_126bar_self_projectors", {}).get(
                "four_projector_Hessians_reconstruct_unprojected_norm_quartic_entrywise_over_Q"
            ) is True
            and families.get("O44_Phi2_Sigma_projectors", {}).get(
                "six_channel_Hessians_reconstruct_unprojected_contraction_entrywise_over_Q"
            ) is True
        ),
        "exact_arithmetic_target_and_scope_boundary": (
            arithmetic.get("exact_domains") == ["Z", "Gaussian integers Z[i]", "Q"]
            and arithmetic.get("floating_point_used_to_construct_or_accept_Hessians") is False
            and arithmetic.get("finite_difference_autodiff_or_rational_recognition_used") is False
            and target.get("chart_dimension") == 486
            and target.get("lattice_denominator") == 20
            and target.get("lattice_norm_squared") == 1632
            and target.get("support_size") == 21
            and scope.get("active_witness_row_count") == 37
            and scope.get("exact_source_rows_certified_here") == 10
            and scope.get("remaining_active_row_count") == 27
            and len(scope.get("remaining_active_rows", [])) == 27
            and claims == expected_claims
        ),
        "embedded_checks_exact": (
            set(embedded_checks) == expected_check_names
            and all(embedded_checks.get(name) is True for name in expected_check_names)
            and report.get("n_checks") == 11
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_HARD_PROJECTOR_HESSIANS",
        "source_bound": source_bound,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "exact_source_Hessian_row_count": 10 if source_bound else None,
        "remaining_active_row_count": 27 if source_bound else None,
        "all_10_O27_O44_source_Hessians_closed": bool(source_bound),
        "all_37_active_source_Hessians_closed": False,
        "full_witness_stationarity_rank_PSD_closed": False,
        "full_486_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "release_verified": False,
        "checks": checks,
    }


def _physical_sm_last_six_hessians_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the last six source Hessians; leave aggregate/global G3-G5 open."""
    expected_top = {
        "schema", "status", "model_contract_id", "source_bindings",
        "arithmetic_contract", "certified_rows", "family_certificates",
        "scope_accounting", "claims", "checks", "n_checks", "n_failed",
        "failures", "integrity",
    }
    expected_files = {
        "exact_mixed_45_triplet_channel_v20.py",
        "exact_phi2_hdagh_channel_family_v20.py",
        "exact_physical_sm_easy_21_hessians_v20.py",
        "exact_physical_sm_hard_projector_hessians_v20.py",
        "gauged_u1x_g2_derivative_audit_v20.py",
        "live_g2_canonical_486_field_chart_v20.py",
        "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
        "live_g2_exact_phi2_hdagh_derivatives_v20.py",
        "live_g2_exact_remaining_cubic_derivatives_v20.py",
        "physical_sm_vacuum_local_feasibility_v20.py",
    }
    expected_claims = {
        "all_37_active_source_Hessians_available_across_three_theorems": True,
        "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here": False,
        "exact_last_six_source_Hessians": True,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    rows = report.get("certified_rows", [])
    scope = report.get("scope_accounting", {})
    claims = report.get("claims", {})
    arithmetic = report.get("arithmetic_contract", {})
    embedded_checks = report.get("checks", {})
    core_payload = {key: value for key, value in report.items() if key != "integrity"}
    row_ids = [row.get("direction_id") for row in rows]
    checks = {
        "artifact_schema_status_core_and_raw_pins_exact": (
            set(report) == expected_top
            and report.get("schema") == "exact_physical_sm_last_six_hessians_v20"
            and report.get("status")
            == "EXACT_LAST_SIX_SOURCE_HESSIANS__ALL_37_ROWS_AVAILABLE__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_LAST_SIX_HESSIANS_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_LAST_SIX_HESSIANS_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_LAST_SIX_HESSIANS_MD_RAW_SHA256
        ),
        "ten_live_portable_dependencies_exact": (
            bindings.get("all_portable_lf_pins_match") is True
            and set(files) == expected_files
            and all(
                set(row) == {"portable_lf_sha256", "matches"}
                and row.get("matches") is True
                and row.get("portable_lf_sha256") == _file_sha256(ROOT / relative)
                for relative, row in files.items()
            )
        ),
        "six_exact_486_Hessians_and_Euler_identities": (
            len(rows) == 6
            and len(set(row_ids)) == 6
            and row_ids == sorted(row_ids)
            and sum(str(name).startswith("O14_") for name in row_ids) == 1
            and sum(str(name).startswith("O35_") for name in row_ids) == 2
            and sum(str(name).startswith("O46_") for name in row_ids) == 3
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
        "all_37_available_but_aggregate_and_physical_claims_fail_closed": (
            arithmetic.get("floating_point_used_to_construct_or_accept_Hessians") is False
            and arithmetic.get("finite_difference_autodiff_or_rational_recognition_used") is False
            and scope.get("easy_rows") == 21
            and scope.get("hard_rows") == 10
            and scope.get("last_rows") == 6
            and scope.get("total_active_source_Hessians_available") == 37
            and claims == expected_claims
            and set(embedded_checks) == {
                "O14_operator_Hermitian", "all_G3_G4_G5_and_global_claims_fail_closed",
                "all_Hessians_symmetric", "all_exact_Euler_identities",
                "exactly_six_rows", "source_pins_match",
            }
            and all(embedded_checks.values())
            and report.get("n_checks") == 6
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_LAST_SIX_HESSIANS",
        "source_bound": source_bound,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "exact_last_six_source_Hessians_closed": bool(source_bound),
        "all_37_active_source_Hessians_available": bool(source_bound),
        "exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed": False,
        "full_486_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "release_verified": False,
        "checks": checks,
    }


def _physical_sm_37_row_aggregate_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind exact local source-Hessian closure without promoting global G3-G5."""
    expected_top = {
        "schema", "status", "model_contract_id", "source_bindings",
        "arithmetic_contract", "source_aggregate_assembly", "witness",
        "exact_stationarity", "exact_kernel_and_rank", "exact_PSD_certificate",
        "scope_boundary", "claims", "checks", "n_checks", "n_failed",
        "failures", "integrity",
    }
    expected_check_names = {
        "all_37_rows_present", "all_generator_columns_annihilated",
        "exact_PSD", "exact_rank_and_kernel", "exact_source_Hq_consistency",
        "exact_value_and_stationarity", "global_equality_and_G3_G4_G5_fail_closed",
        "source_aggregate_matches_historical_reconstruction_entrywise",
        "source_pins_match",
    }
    expected_claims = {
        "all_37_active_Hessians_derived_from_exact_source_algebra": True,
        "exact_source_aggregate_is_PSD_and_strictly_positive_mod_symmetry": True,
        "exact_source_aggregate_kernel_is_38_dimensional_symmetry_span": True,
        "exact_source_aggregate_rank_is_448": True,
        "exact_source_aggregate_value_minus_one_and_stationary": True,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    assembly = report.get("source_aggregate_assembly", {})
    witness = report.get("witness", {})
    stationarity = report.get("exact_stationarity", {})
    kernel = report.get("exact_kernel_and_rank", {})
    modular = kernel.get("modular_lower_bound_certificate", {})
    psd = report.get("exact_PSD_certificate", {})
    scope = report.get("scope_boundary", {})
    arithmetic = report.get("arithmetic_contract", {})
    claims = report.get("claims", {})
    embedded_checks = report.get("checks", {})
    core_payload = {key: value for key, value in report.items() if key != "integrity"}
    checks = {
        "artifact_schema_status_core_and_raw_pins_exact": (
            set(report) == expected_top
            and report.get("schema") == "exact_physical_sm_37_row_aggregate_v20"
            and report.get("status")
            == "EXACT_ALL_37_SOURCE_AGGREGATE_STATIONARY_KERNEL_RANK_PSD__GLOBAL_EQUALITY_ORBIT_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_37_ROW_AGGREGATE_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_37_ROW_AGGREGATE_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_37_ROW_AGGREGATE_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_37_ROW_AGGREGATE_MD_RAW_SHA256
        ),
        "eight_live_portable_dependencies_exact": (
            bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 8
            and all(
                set(row) == {"portable_lf_sha256", "matches"}
                and row.get("matches") is True
                and row.get("portable_lf_sha256") == _file_sha256(ROOT / relative)
                for relative, row in files.items()
            )
        ),
        "all_37_source_rows_and_exact_stationarity": (
            assembly.get("active_row_count") == 37
            and assembly.get("nonzero_entries") == 5840
            and assembly.get("denominator") == 6300103327590
            and assembly.get("canonical_sparse_Q_sqrt2_serialization_sha256")
            == "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458"
            and assembly.get("entrywise_identity_to_historical_reconstructed_rational_aggregate") is True
            and witness.get("coefficient_count") == 37
            and len(witness.get("exact_rational_coefficients", {})) == 37
            and len(witness.get("row_homogeneous_degrees", {})) == 37
            and stationarity.get("exact_potential_value") == "-1"
            and stationarity.get("exact_gradient_nonzero_entries") == 0
            and stationarity.get("exact_gradient_is_zero") is True
            and stationarity.get("aggregate_Hq_matches_weighted_source_Hq_entrywise") is True
            and len(stationarity.get("per_row_exact_target_values", {})) == 37
        ),
        "exact_kernel_rank_and_PSD_certificate": (
            kernel.get("exact_generator_column_count") == 47
            and kernel.get("annihilated_generator_columns") == 47
            and kernel.get("all_47_generator_columns_annihilated_entrywise") is True
            and kernel.get("exact_symmetry_tangent_span_dimension") == 38
            and kernel.get("exact_rank") == 448
            and kernel.get("exact_nullity") == 38
            and kernel.get("kernel_equals_exact_symmetry_tangent_span") is True
            and modular.get("prime") == 1009
            and modular.get("rank") == 448
            and modular.get("principal_minor_determinant_mod_prime") == 870
            and modular.get("principal_minor_is_nonzero") is True
            and len(modular.get("principal_pivot_indices", [])) == 448
            and psd.get("principal_minor_dimension") == 448
            and psd.get("strictly_positive_exact_pivot_count") == 448
            and psd.get("all_exact_pivots_strictly_positive") is True
            and psd.get("exact_divisibility_checks") == 29671711
            and psd.get("positive_pivot_sha256_chain")
            == "58b41d4c2be5fbc31b0ada79b653e84561e0db629a3d600053d44d760824c259"
            and psd.get("principal_minor_is_positive_definite_by_Sylvester") is True
            and psd.get("full_Hessian_is_positive_semidefinite") is True
            and psd.get("full_Hessian_is_positive_definite_mod_kernel") is True
        ),
        "local_scope_exact_but_global_and_physical_G3_G5_fail_closed": (
            arithmetic.get("floating_point_used_to_construct_or_accept_any_claim") is False
            and arithmetic.get("finite_difference_autodiff_or_rational_recognition_used") is False
            and scope.get("source_bound_local_stationary_Hessian_problem_complete") is True
            and scope.get("global_equality_orbit_classification_complete") is False
            and claims == expected_claims
            and set(embedded_checks) == expected_check_names
            and all(embedded_checks.get(name) is True for name in expected_check_names)
            and report.get("n_checks") == 9
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_37_ROW_AGGREGATE",
        "source_bound": source_bound,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "all_37_active_Hessians_source_derived": bool(source_bound),
        "exact_source_aggregate_value_minus_one_and_stationary": bool(source_bound),
        "exact_source_aggregate_kernel_dimension": 38 if source_bound else None,
        "exact_source_aggregate_rank": 448 if source_bound else None,
        "exact_source_aggregate_PSD_and_strict_mod_symmetry": bool(source_bound),
        "source_bound_local_stationary_Hessian_problem_complete": bool(source_bound),
        "full_486_global_equality_orbit_closed": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "release_verified": False,
        "checks": checks,
    }


def _physical_sm_local_equality_orbit_contract(
    report: dict[str, Any],
    *,
    portable_lf_sha256: str = "",
    source_portable_lf_sha256: str = "",
    test_portable_lf_sha256: str = "",
    markdown_portable_lf_sha256: str = "",
) -> dict[str, Any]:
    """Bind the full-486 local orbit theorem without asserting global equality."""
    expected_top = {
        "schema", "status", "model_contract_id", "source_bindings",
        "local_orbit_theorem", "sixteen_sign_orbit", "scope_boundary",
        "claims", "checks", "n_checks", "n_failed", "failures", "integrity",
    }
    expected_check_names = {
        "actual_486_target_and_representation_embedding_source_verified",
        "all_16_five_amplitude_variants_are_one_declared_continuous_orbit",
        "all_equivariant_Morse_Bott_slice_hypotheses_hold",
        "dependency_pins_match",
        "every_sign_row_group_action_matches_all_actual_nonzero_target_coordinates",
        "every_sign_row_has_verified_exact_phase_action",
        "exactly_16_sign_rows",
        "five_amplitude_exact_solution_ideal_and_bit_order_source_bound",
        "full_486_local_stationary_equality_locus_is_exactly_one_K_orbit",
        "full_486_local_stationary_locus_is_exactly_one_K_orbit",
        "global_G3_G4_G5_remain_fail_closed",
        "no_quantitative_neighborhood_radius_claimed",
        "upstream_core_pins_match",
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
    bindings = report.get("source_bindings", {})
    files = bindings.get("files", {})
    theorem = report.get("local_orbit_theorem", {})
    hypotheses = theorem.get("hypotheses", {})
    signs = report.get("sixteen_sign_orbit", {})
    sign_rows = signs.get("rows", [])
    embedding = signs.get("actual_target_representation_embedding", {})
    embedding_checks = embedding.get("checks", {})
    scope = report.get("scope_boundary", {})
    claims = report.get("claims", {})
    embedded_checks = report.get("checks", {})
    core_payload = {key: value for key, value in report.items() if key != "integrity"}
    checks = {
        "artifact_schema_status_core_and_four_portable_pins_exact": (
            set(report) == expected_top
            and report.get("schema") == "exact_physical_sm_local_equality_orbit_v20"
            and report.get("status")
            == "EXACT_FULL_486_LOCAL_EQUALITY_ORBIT_AND_16_SIGN_ORBIT__GLOBAL_EQUALITY_OPEN"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_CORE_SHA256
            and portable_lf_sha256
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_LF_SHA256
            and source_portable_lf_sha256
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE_PORTABLE_LF_SHA256
            and test_portable_lf_sha256
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST_PORTABLE_LF_SHA256
            and markdown_portable_lf_sha256
            == PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD_PORTABLE_LF_SHA256
        ),
        "seven_live_portable_dependencies_exact": (
            bindings.get("all_portable_lf_pins_match") is True
            and len(files) == 7
            and all(
                set(row)
                == {"portable_lf_sha256", "expected_portable_lf_sha256", "matches"}
                and row.get("matches") is True
                and row.get("portable_lf_sha256")
                == row.get("expected_portable_lf_sha256")
                == _file_sha256(ROOT / relative)
                for relative, row in files.items()
            )
        ),
        "full_486_local_Morse_Bott_orbit_theorem_exact": (
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
        "sixteen_sign_variants_are_one_continuous_K_orbit_exact": (
            len(sign_rows) == 16
            and len({tuple(row.get("bits_h_d_s_x", [])) for row in sign_rows}) == 16
            and {tuple(row.get("bits_h_d_s_x", [])) for row in sign_rows}
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
                for row in sign_rows
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
        "local_positive_scope_but_radius_global_and_physical_G3_G5_fail_closed": (
            claims == expected_claims
            and scope
            == {
                "distant_or_disconnected_equality_components_excluded": False,
                "global_polynomial_ideal_or_global_SOS_orbit_separator_supplied": False,
                "not_just_five_amplitude_slice": True,
                "theorem_is_full_486_dimensional_but_local_near_the_entire_compact_orbit": True,
            }
            and set(embedded_checks) == expected_check_names
            and all(embedded_checks.get(name) is True for name in expected_check_names)
            and report.get("n_checks") == 13
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_LOCAL_EQUALITY_ORBIT",
        "source_bound": source_bound,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "full_486_local_stationary_orbit_classified": bool(source_bound),
        "full_486_local_stationary_equality_orbit_classified": bool(source_bound),
        "all_16_sign_variants_one_continuous_K_orbit": bool(source_bound),
        "target_orbit_strict_local_minimum_mod_K": bool(source_bound),
        "quantitative_neighborhood_radius_proved": False,
        "complete_486_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "release_verified": False,
        "checks": checks,
    }


def _physical_sm_g4_g5_branch_mismatch_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the exact branch mismatch without claiming a global hierarchy no-go."""
    core_keys = (
        "schema", "status", "contract_id", "model_contract_id", "source_binding",
        "exact_branch_mismatch", "unit_rescaling_audit_0_through_100",
        "gate_acceptance_boundary", "scope", "next_required_work",
    )
    core_payload = {key: report[key] for key in core_keys} if all(key in report for key in core_keys) else {}
    binding = report.get("source_binding", {})
    files = binding.get("files", {})
    mismatch = report.get("exact_branch_mismatch", {})
    exact = mismatch.get("exact_mismatch", {})
    audit = report.get("unit_rescaling_audit_0_through_100", {})
    gates = report.get("gate_acceptance_boundary", {})
    scope = report.get("scope", {})
    embedded_checks = report.get("checks", {})
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
    dependency_modes_ok = True
    for row in files.values():
        path = ROOT / str(row.get("path", ""))
        mode = row.get("binding_mode")
        observed = _file_sha256(path) if mode == "portable_lf" else _semantic_json_file_sha256(path)
        dependency_modes_ok = bool(
            dependency_modes_ok
            and mode in {"portable_lf", "semantic_json"}
            and row.get("matches") is True
            and row.get("observed_sha256") == row.get("expected_sha256") == observed
        )
    all_gate_flags_false = all(
        value is False
        for gate in gates.values()
        for key, value in gate.items()
        if key.endswith("_closed") or key.startswith("promoted_by_this_")
    )
    checks = {
        "artifact_schema_status_core_and_raw_pins_exact": (
            report.get("schema") == "exact_physical_sm_g4_g5_branch_mismatch_v1"
            and report.get("status") == "EXACT_FIVE_AMPLITUDE_VS_PHYSICAL_EW_BRANCH_MISMATCH_PROVED__CANONICAL_G4_G5_AND_DOWNSTREAM_G6_G8_OPEN"
            and report.get("contract_id") == "exact_physical_sm_g4_g5_branch_mismatch_v20"
            and report.get("model_contract_id") == "gauged_u1x_phi17_v20"
            and report.get("integrity", {}).get("core_sha256")
            == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
            and _canonical_json_line_sha256(core_payload)
            == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_CORE_SHA256
            and raw_sha256 == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD_RAW_SHA256
        ),
        "seven_live_dependencies_and_parent_cores_exact": (
            binding.get("all_dependency_pins_match") is True
            and binding.get("shared_model_contract_id") == "gauged_u1x_phi17_v20"
            and binding.get("five_amplitude_core_sha256")
            == PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256
            and binding.get("physical_SM_foundation_core_sha256")
            == PHYSICAL_SM_VACUUM_CORE_SHA256
            and len(files) == 7
            and dependency_modes_ok
        ),
        "exact_nonremovable_branch_mismatch_and_101_audit": (
            mismatch.get("five_amplitude_branch", {}).get("H_over_Phi_squared") == "2"
            and exact.get("ratios_are_equal") is False
            and exact.get("mismatch_exceeds_10_pow_26_in_squared_ratio") is True
            and exact.get("common_unit_rescaling_can_remove_mismatch") is False
            and audit.get("case_range") == [0, 100]
            and audit.get("case_count") == 101
            and audit.get("identity_case") == 50
            and audit.get("all_common_rescalings_preserve_ratio") is True
            and audit.get("records_sha256")
            == "1783b73db34801957825decc3c6e7619f31275935d68e1dd067e36f7eecb0c87"
        ),
        "canonical_G4_through_G8_and_global_no_go_fail_closed": (
            set(gates) == {"G4", "G5", "G6", "G7", "G8"}
            and all_gate_flags_false
            and scope == {
                "exact_branch_mismatch_proved": True,
                "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G4": False,
                "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G5": False,
                "global_no_go_for_all_possible_physical_EW_branches": False,
                "new_hierarchy_mechanism_ruled_out": False,
                "physical_G4_G5_G6_G7_G8_closed": False,
                "release_G4_G5_G6_G7_G8_closed": False,
                "authoritative_G4_G5_G6_G7_G8_closed": False,
            }
        ),
        "embedded_checks_exact": (
            set(embedded_checks) == expected_check_names
            and all(embedded_checks.get(name) is True for name in expected_check_names)
            and report.get("n_checks") == 10
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_G4_G5_BRANCH_MISMATCH",
        "source_bound": source_bound,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "exact_branch_mismatch_proved": bool(source_bound),
        "unit_rescaling_case_count": 101 if source_bound else None,
        "current_five_amplitude_target_is_canonical_physical_EW_branch": False,
        "global_no_go_for_other_physical_EW_branches": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "physical_SM_G6_closed": False,
        "physical_SM_G7_closed": False,
        "physical_SM_G8_closed": False,
        "release_verified": False,
        "checks": checks,
    }


def _physical_sm_heavy_vector_mass_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind reconstructed physical-SM tree vector masses without closing G6/G7."""
    expected_top_level = {
        "core_sha256",
        "contract_id",
        "status",
        "source_binding",
        "normalization",
        "exact_matrix",
        "rank_kernel_Goldstone",
        "unbroken_basis_labels",
        "sector_resolution",
        "massive_non_neutral_multiplets",
        "neutral_massive_sector",
        "parameterized_threshold_interface",
        "checks",
        "scope",
        "blockers",
    }
    expected_sources = {
        "physical_SM_target_source": {
            "path": "physical_sm_vacuum_local_feasibility_v20.py",
            "sha256": PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "physical_SM_target_report": {
            "path": "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
            "sha256": PHYSICAL_SM_VACUUM_RAW_SHA256,
            "mode": "raw",
        },
        "canonical_486_real_chart": {
            "path": "live_g2_canonical_486_field_chart_v20.py",
            "sha256": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
            "mode": "portable_text",
        },
        "authoritative_gauge_normalization": {
            "path": "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "sha256": AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "authoritative_model": {
            "path": "models\\SO10Z17AxionV20.m",
            "sha256": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
            "mode": "raw",
        },
    }
    expected_scope = {
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
    positive_check_names = {
        "all_dependencies_match_frozen_hashes",
        "target_denominator_is_20",
        "canonical_chart_kinetic_is_identity",
        "SO10_generator_rescaling_matches_T10_one",
        "tangent_matrix_is_486_by_46",
        "exact_tangent_matches_live_chart_without_residual",
        "gram_matrix_is_exact_symmetric_integer",
        "five_field_block_grams_sum_exactly",
        "sparse_upper_triangle_reconstructs_all_nonzero_entries",
        "exact_massive_rank_is_37",
        "exact_unbroken_nullity_is_9",
        "standard_su3C_u1em_basis_is_complete_kernel",
        "Goldstone_image_dimension_is_37",
        "one_accidental_PQ_direction_is_uneaten",
        "mass_gram_commutes_with_color",
        "mass_gram_commutes_with_Q3_squared",
        "joint_sector_projectors_are_complete",
        "all_non_neutral_sector_polynomials_exact",
        "all_non_neutral_multiplicities_exact",
        "non_neutral_massive_real_dimension_is_34",
        "three_neutral_massive_roots_complete_rank_37",
        "one_loop_SU3_index_sum_is_5_over_2",
        "one_loop_QED_index_sum_is_32_over_3",
    }
    negative_check_names = {
        "physical_scale_and_coupling_boundaries_fixed",
        "pole_masses_fixed",
        "vector_Goldstone_ghost_matching_closed",
        "finite_scheme_constants_closed",
        "SM_symmetric_pre_EW_threshold_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    expected_blockers = [
        "Choose a physical dimensionful target scale and renormalized g10,gX boundary values.",
        "Derive pole masses and the gauge-fixing-consistent vector, Goldstone and ghost threshold coefficient.",
        "Fix finite scheme constants and the matching-scale prescription.",
        "Construct the pre-electroweak SU(3)xSU(2)xU(1) matching step; the full target preserves only SU(3)xU(1)em.",
        "Combine with a source-exact physical scalar Hessian and the full Yukawa/scalar/dimensionful RGE system before G6/G7 closure.",
    ]
    embedded_checks = report.get("checks", {})
    normalization = report.get("normalization", {})
    matrix = report.get("exact_matrix", {})
    kernel = report.get("rank_kernel_Goldstone", {})
    sectors = report.get("sector_resolution", {})
    neutral = report.get("neutral_massive_sector", {})
    threshold = report.get("parameterized_threshold_interface", {})
    checks = {
        "artifact_present": bool(report),
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("contract_id")
            == "exact_physical_sm_heavy_vector_masses_v20"
            and report.get("status")
            == "EXACT_PARAMETERIZED_PHYSICAL_SM_HEAVY_VECTOR_MASS_THEOREM_CLOSED__LOOP_MATCHING_AND_FULL_G6_G7_OPEN"
            and report.get("core_sha256")
            == PHYSICAL_SM_HEAVY_VECTOR_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_MD_RAW_SHA256
        ),
        "dependency_bindings_exact": report.get("source_binding")
        == expected_sources,
        "embedded_checks_truth_boundary_exact": (
            set(embedded_checks) == positive_check_names | negative_check_names
            and all(embedded_checks.get(name) is True for name in positive_check_names)
            and all(
                embedded_checks.get(name) is False for name in negative_check_names
            )
        ),
        "scope_truth_boundary_exact": report.get("scope") == expected_scope,
        "canonical_normalization_and_parameter_domain_exact": (
            normalization.get("normalization_matches") is True
            and normalization.get("canonical_Tr10_H2") == "1"
            and normalization.get("authoritative_T10") == "1"
            and normalization.get("target_lattice") == "n=20 q"
            and normalization.get("parameter_domain") == "g10>0, gX>0, v>0"
        ),
        "exact_matrix_rank_kernel_and_unbroken_group_exact": (
            matrix.get("shape") == [46, 46]
            and matrix.get("sparse_upper_triangle_nonzero_entries") == 81
            and matrix.get("block_sum_equals_full_gram") is True
            and matrix.get("bare_gram_sha256_i64_C_order")
            == "8e58eb233efa3d3e1d02965104a9b568ab9e17143c417d8629f7232fd68efa33"
            and kernel.get("exact_gram_rank") == 37
            and kernel.get("exact_gram_nullity") == 9
            and kernel.get("declared_basis_is_complete_kernel") is True
            and kernel.get("unbroken_algebra") == "su(3)_C + u(1)_em"
            and kernel.get("gauge_Goldstone_image_dimension") == 37
            and kernel.get("uneaten_accidental_PQ_dimension") == 1
        ),
        "exact_sector_and_threshold_input_scope_exact": (
            sectors.get("joint_projectors_sum_to_identity") is True
            and sectors.get("joint_dimension_sum") == 46
            and sectors.get("all_sector_mass_polynomials_exact") is True
            and sectors.get("all_sector_multiplicities_exact") is True
            and len(report.get("massive_non_neutral_multiplets", [])) == 7
            and neutral.get("massive_roots") == 3
            and neutral.get("massless_neutral_vector")
            == "Q3=3G67-G01-G23-G45"
            and threshold.get("unbroken_group_at_full_target")
            == "SU(3)_C x U(1)_em"
            and threshold.get("total_indices")
            == {"SU3": "5/2", "QED": "32/3"}
            and threshold.get("complete_vector_Goldstone_ghost_matching")
            is False
            and threshold.get("finite_scheme_constants") is False
        ),
        "blockers_exact_and_G6_G7_fail_closed": (
            report.get("blockers") == expected_blockers
            and report.get("scope", {}).get("physical_G6") is False
            and report.get("scope", {}).get("physical_G7") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_HEAVY_VECTOR_MASS_CONTRACT",
        "artifact": PHYSICAL_SM_HEAVY_VECTOR_JSON.name,
        "markdown": PHYSICAL_SM_HEAVY_VECTOR_MD.name,
        "source": PHYSICAL_SM_HEAVY_VECTOR_SOURCE.name,
        "test": PHYSICAL_SM_HEAVY_VECTOR_TEST.name,
        "expected_core_sha256": PHYSICAL_SM_HEAVY_VECTOR_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256,
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_MD_RAW_SHA256,
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "exact_parameterized_tree_vector_mass_matrix_closed": bool(source_bound),
        "exact_vector_rank_kernel_and_Goldstone_image_closed": bool(source_bound),
        "exact_SU3C_x_U1em_vector_sector_resolution_closed": bool(source_bound),
        "parameterized_vector_threshold_log_inputs_closed": bool(source_bound),
        "absolute_physical_vector_masses_closed": False,
        "pole_vector_masses_closed": False,
        "vector_Goldstone_ghost_matching_closed": False,
        "complete_one_loop_vector_threshold_matching_closed": False,
        "physical_scalar_spectrum_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "release_G6_verified": False,
        "release_G7_verified": False,
        "blockers": expected_blockers if source_bound else [],
        "checks": checks,
    }


def _physical_sm_heavy_vector_msbar_matching_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the combined heavy-gauge MS-bar kernel without closing G6/G7."""
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
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "exact_heavy_vector_mass_report": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256,
            "mode": "raw",
        },
        "authoritative_SO10_normalization": {
            "path": "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "sha256": AUTHORITATIVE_GAUGE_BETAS_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "authoritative_model": {
            "path": "models\\SO10Z17AxionV20.m",
            "sha256": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
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
    expected_positive_checks = {
        "all_dependencies_match_frozen_hashes",
        "primary_equations_identified_by_DOI_and_number",
        "scheme_is_nonsupersymmetric_MSbar",
        "tree_running_masses_declared",
        "seven_charged_complex_multiplets_complete",
        "charged_real_vector_dimension_is_34",
        "neutral_massive_vector_dimension_is_3",
        "total_massive_and_Goldstone_dimensions_are_37",
        "complex_SU3_index_is_5_over_2",
        "complex_QED_index_is_32_over_3",
        "real_SU3_broken_index_is_5",
        "real_QED_broken_index_is_64_over_3",
        "QED_embedding_index_is_8_over_3",
        "U1X_has_zero_tree_embedding_in_SU3_and_QED",
        "SU3_finite_constant_is_minus_5_over_12pi",
        "QED_finite_constant_is_minus_16_over_9pi",
        "SU3_log_coefficient_is_35_over_4pi",
        "QED_log_coefficient_is_112_over_3pi",
        "Hall_and_B15_implementations_agree",
        "mass_theorem_weighted_log_interface_agrees",
        "combined_vector_FPghost_Goldstone_MSbar_kernel_closed",
        "finite_MSbar_vector_constant_closed",
        "Goldstone_double_count_guard_active",
    }
    expected_negative_checks = {
        "arbitrary_Rxi_determinant_cancellation_rederived",
        "pole_mass_conversion_closed",
        "SM_symmetric_pre_EW_matching_closed",
        "complete_scalar_fermion_threshold_matching_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    expected_blockers = [
        "Derive the general-background-R_xi vector/longitudinal/Goldstone/FP-ghost quadratic operators and an independent xi-cancellation identity if a sector-resolved proof is required.",
        "Compute one-loop pole corrections to the seven tree running vector masses and declare the tadpole/VEV renormalization prescription.",
        "Construct a stationary SM-symmetric pre-electroweak vacuum and its SU(3)xSU(2)xU(1) heavy-vector spectrum; the terminal target already preserves only SU(3)xU(1)em.",
        "Combine with the Goldstone-projected physical scalar Hessian, fermion masses, and the full two-loop Yukawa/scalar/dimensionful Wilson flow before any physical G7 claim.",
    ]
    embedded_checks = report.get("checks", {})
    scope = report.get("scope", {})
    scheme = report.get("scheme_contract", {})
    group = report.get("exact_group_factors", {})
    obstruction = report.get("gauge_parameter_obstruction", {})
    interface = report.get("consumer_interface", {})
    multiplets = report.get("massive_charged_multiplets", [])
    sources = report.get("primary_equation_sources", [])
    checks = {
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("contract_id")
            == "exact_physical_sm_heavy_vector_msbar_matching_v20"
            and report.get("status")
            == "EXACT_COMBINED_HEAVY_VECTOR_GHOST_GOLDSTONE_MSBAR_MATCHING_CLOSED__ARBITRARY_RXI_POLE_PRE_EW_AND_FULL_G7_OPEN"
            and report.get("core_sha256")
            == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST_RAW_SHA256
            and markdown_raw_sha256
            == PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD_RAW_SHA256
        ),
        "dependency_bindings_exact": report.get("source_binding")
        == expected_sources,
        "primary_equation_provenance_exact": (
            isinstance(sources, list)
            and len(sources) == 3
            and [row.get("doi") for row in sources]
            == [
                "10.1103/PhysRevD.91.075016",
                "10.1103/PhysRevD.108.055003",
                "10.1016/0550-3213(81)90498-3",
            ]
            and sources[0].get("equations") == ["(2)", "(3)"]
            and sources[1].get("equations") == ["(B14)", "(B15)"]
        ),
        "embedded_checks_truth_boundary_exact": (
            set(embedded_checks)
            == expected_positive_checks | expected_negative_checks
            and all(
                embedded_checks.get(name) is True
                for name in expected_positive_checks
            )
            and all(
                embedded_checks.get(name) is False
                for name in expected_negative_checks
            )
        ),
        "scope_truth_boundary_exact": scope == expected_scope,
        "scheme_and_per_vector_kernel_exact": (
            scheme.get("renormalization_scheme")
            == "non-supersymmetric MS-bar"
            and scheme.get("mass_definition") == "tree_running_mass"
            and scheme.get("per_complex_vector")
            == "Delta_i=-T_i/(6*pi)+7*T_i/(2*pi)*log(M_tree/mu)"
            and scheme.get("gauge_parameter")
            == "not an input; published combined result only; explicit xi is rejected"
        ),
        "exact_group_factors_and_coefficients": (
            group.get("charged_complex_multiplets") == 7
            and group.get("charged_real_vectors") == 34
            and group.get("neutral_massive_vectors") == 3
            and group.get("all_massive_vectors") == 37
            and group.get("Goldstone_image_dimension") == 37
            and group.get("uneaten_accidental_PQ_dimension") == 1
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
        "multiplets_and_consumer_guard_exact": (
            isinstance(multiplets, list)
            and len(multiplets) == 7
            and sum(row.get("real_vector_dimension", -100) for row in multiplets)
            == 34
            and interface.get("Goldstone_exclusion_guard")
            == "assert_goldstone_exclusion(37)"
            and interface.get("later_scalar_consumer_requirement")
            == "exclude all 37 gauge-Goldstone image directions; retain the one uneaten accidental-PQ direction if it is otherwise physical"
        ),
        "combined_result_and_Rxi_boundary_exact": (
            obstruction.get("combined_MSbar_matching_closed") is True
            and obstruction.get("arbitrary_Rxi_sector_resolved_matching_closed")
            is False
            and len(
                obstruction.get("missing_for_independent_xi_cancellation_proof", [])
            )
            == 4
        ),
        "blockers_exact_and_G6_G7_fail_closed": (
            report.get("blockers") == expected_blockers
            and scope.get("complete_one_loop_model_matching") is False
            and scope.get("physical_G6") is False
            and scope.get("physical_G7") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CONTRACT",
        "artifact": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON.name,
        "markdown": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD.name,
        "source": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE.name,
        "test": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST.name,
        "expected_core_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST_RAW_SHA256,
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": (
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD_RAW_SHA256
        ),
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed": bool(
            source_bound
        ),
        "finite_MSbar_vector_constant_closed": bool(source_bound),
        "exact_SU3_and_physical_QED_group_factors_closed": bool(source_bound),
        "Goldstone_double_count_guard_active": bool(source_bound),
        "per_complex_vector_matching_formula": (
            scheme.get("per_complex_vector") if source_bound else None
        ),
        "complex_index_totals": (
            group.get("complex_index_totals") if source_bound else {}
        ),
        "combined_threshold_coefficients": (
            group.get("combined_threshold_coefficients") if source_bound else {}
        ),
        "arbitrary_Rxi_sector_resolved_matching_closed": False,
        "pole_mass_conversion_closed": False,
        "SM_symmetric_pre_EW_matching_closed": False,
        "complete_scalar_fermion_threshold_matching_closed": False,
        "complete_one_loop_model_matching_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "release_G6_verified": False,
        "release_G7_verified": False,
        "blockers": expected_blockers if source_bound else [],
        "checks": checks,
    }


def _conditional_physical_sm_eft_hessian_spectrum_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the reconstructed conditional tree scalar spectrum only."""
    expected_top_level = {
        "Hren_factorization",
        "closure_claims",
        "exact_sector_assignment",
        "exact_standard_commutators",
        "integrity",
        "kernel_and_physics_boundary",
        "kinetic_normalization",
        "proof_boundary",
        "schema",
        "source_binding",
        "squared_EFT_spectrum",
        "status",
    }
    expected_claims = {
        "conditional_reconstructed_squared_EFT_spectrum": True,
        "conditional_reconstructed_tree_Hessian_factorization": True,
        "conditional_reconstructed_tree_Hessian_sector_assignment": True,
        "pole_spectrum_G6": False,
        "release_G6": False,
        "source_bound_physical_G6": False,
    }
    expected_foundation = {
        "foundation_JSON_sha256": PHYSICAL_SM_VACUUM_RAW_SHA256,
        "foundation_core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
        "foundation_source_sha256": PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
        "foundation_sparse_Hessian_sha256": (
            "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458"
        ),
    }
    binding = report.get("source_binding", {})
    foundation = binding.get("foundation", {})
    factorization = report.get("Hren_factorization", {})
    sectors = report.get("exact_sector_assignment", {})
    commutators = report.get("exact_standard_commutators", {})
    kinetic = report.get("kinetic_normalization", {})
    spectrum = report.get("squared_EFT_spectrum", {})
    boundary = report.get("kernel_and_physics_boundary", {})
    proof = report.get("proof_boundary", {})
    checks = {
        "artifact_present": bool(report),
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "conditional_physical_sm_eft_hessian_spectrum_v1"
            and report.get("status")
            == "CONDITIONAL_EXACT_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM__SOURCE_ALGEBRA_POLE_AND_RELEASE_CLOSURE_OPEN"
            and report.get("integrity", {}).get("core_sha256")
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_RAW_SHA256
            and source_raw_sha256
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE_RAW_SHA256
            and test_raw_sha256
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST_RAW_SHA256
            and markdown_raw_sha256
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD_RAW_SHA256
        ),
        "foundation_and_source_dependencies_exact": (
            foundation.get("expected") == expected_foundation
            and foundation.get("actual") == expected_foundation
            and foundation.get("all_terminal_foundation_pins_match") is True
            and foundation.get("foundation_source_portable_lf_sha256")
            == PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256
            and binding.get("kinetic_chart_path")
            == "live_g2_canonical_486_field_chart_v20.py"
            and binding.get("kinetic_chart_sha256")
            == "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e"
            and binding.get("self_path")
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE.name
            and binding.get("self_sha256")
            == CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE_RAW_SHA256
        ),
        "closure_truth_boundary_exact": report.get("closure_claims")
        == expected_claims,
        "conditional_factorization_and_sector_census_exact": (
            factorization.get("field_dimension") == 486
            and factorization.get("coordinate_component_count") == 43
            and factorization.get("maximum_component_size") == 30
            and factorization.get("characteristic_degree_sum") == 486
            and factorization.get("distinct_irreducible_factor_count") == 45
            and sectors.get("method")
            == "exact factor-kernel restriction and exact joint Casimir/Q3-squared eigenspace ranks"
            and sectors.get("sector_count") == 12
            and sectors.get("sector_dimension_sum") == 486
            and sectors.get("all_factor_spaces_exactly_exhausted") is True
        ),
        "standard_symmetry_and_canonical_kinetic_exact": (
            commutators.get(
                "all_standard_SU3C_Q3_and_Casimir_commutators_vanish_exactly"
            )
            is True
            and kinetic.get("field_dimension") == 486
            and kinetic.get("generalized_kinetic_metric") == "K=I_486"
            and kinetic.get("Euclidean_eigenproblem_is_canonically_normalized")
            is True
            and kinetic.get("all_486_basis_norms_equal_one_half") is True
            and kinetic.get("all_adversarial_cross_terms_are_zero") is True
        ),
        "squared_tree_spectrum_rank_nullity_exact": (
            spectrum.get("spectral_variable") == "y=rho/(2b)"
            and spectrum.get("total_root_count_with_multiplicity") == 486
            and spectrum.get("positive_root_count_with_multiplicity") == 448
            and spectrum.get("zero_root_count_with_multiplicity") == 38
            and spectrum.get("no_unrecorded_exact_squared_root_collisions") is True
            and boundary.get("exact_reconstructed_H_rank") == 448
            and boundary.get("exact_reconstructed_H_nullity") == 38
            and boundary.get("gauged_orbit_kernel_dimension") == 37
            and boundary.get("global_PQ_axion_kernel_dimension") == 1
        ),
        "conditional_tree_only_physics_boundary_exact": (
            proof
            == {
                "exact_on_reconstructed_rational_Hessian": True,
                "pole_and_release_claims": False,
                "tree_level_only": True,
                "upstream_denominator_bound_source_derived": False,
                "upstream_source_algebra_derivation_complete": False,
            }
            and boundary.get("rho_is_a_pole_mass_squared") is False
            and boundary.get("physical_G6_closed") is False
            and boundary.get("release_G6_closed") is False
            and boundary.get("missing_for_pole_mass")
            == [
                "dimensionful symmetry-breaking scale and b normalization",
                "loop self-energies and renormalization prescription",
                "RG evolution and component threshold matching",
            ]
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CONTRACT",
        "artifact": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON.name,
        "markdown": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD.name,
        "source": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE.name,
        "test": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST.name,
        "expected_core_sha256": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_CORE_SHA256,
        "core_sha256": report.get("integrity", {}).get("core_sha256"),
        "expected_raw_sha256": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "expected_test_raw_sha256": (
            CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST_RAW_SHA256
        ),
        "test_raw_sha256": test_raw_sha256,
        "expected_markdown_raw_sha256": (
            CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD_RAW_SHA256
        ),
        "markdown_raw_sha256": markdown_raw_sha256,
        "source_bound": source_bound,
        "conditional_reconstructed_tree_scalar_spectrum_closed": bool(
            source_bound
        ),
        "conditional_tree_Hessian_factorization_closed": bool(source_bound),
        "conditional_tree_sector_assignment_closed": bool(source_bound),
        "source_algebra_derived_tree_scalar_spectrum_closed": False,
        "physical_scalar_pole_spectrum_closed": False,
        "dimensionful_physical_scalar_masses_closed": False,
        "physical_G6_closed": False,
        "release_G6_verified": False,
        "physical_G7_closed": False,
        "release_G7_verified": False,
        "checks": checks,
    }


def _physical_sm_vector_rxi_vacuum_cancellation_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind only the zero-background R_xi vacuum determinant theorem."""
    expected_top_level = {
        "schema",
        "contract_id",
        "status",
        "core_sha256",
        "source_binding",
        "quadratic_operator_scope",
        "one_real_broken_direction_theorem",
        "direction_census",
        "multiplet_ledger",
        "all_37_direction_identity",
        "hundred_point_exact_audit",
        "checks",
        "scope",
        "blockers",
        "verdict",
        "n_checks",
        "n_failed",
        "failures",
    }
    expected_sources = {
        "physical_SM_heavy_vector_mass_source": {
            "path": "exact_physical_sm_heavy_vector_masses_v20.py",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "physical_SM_heavy_vector_mass_report": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256,
            "mode": "raw",
        },
        "physical_SM_heavy_vector_MSbar_source": {
            "path": "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE_RAW_SHA256,
            "mode": "raw",
        },
        "physical_SM_heavy_vector_MSbar_report": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
            "sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256,
            "mode": "raw",
        },
    }
    expected_scope = {
        "arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation": True,
        "all_37_broken_real_directions_resolved": True,
        "charged_and_neutral_mass_sectors_included": True,
        "Goldstone_FPghost_double_count_guard": True,
        "background_covariant_heat_kernel_matching_coefficient": False,
        "sector_resolved_general_background_gauge_determinants": False,
        "one_loop_vector_pole_masses": False,
        "tadpole_and_VEV_renormalization_prescription": False,
        "complete_scalar_and_fermion_thresholds": False,
        "physical_G6": False,
        "physical_G7": False,
        "release_G6": False,
        "release_G7": False,
    }
    expected_checks = {
        "all_dependency_hashes_match",
        "mass_and_matching_cores_match",
        "one_direction_D_xiM_exponent_cancels",
        "only_field_independent_minus_half_log_xi_remains",
        "vacuum_normalized_unphysical_determinant_is_one",
        "Goldstone_count_matches_mass_rank",
        "all_37_broken_directions_exhausted",
        "charged_direction_count_is_34",
        "neutral_direction_count_is_3",
        "global_PQ_mode_not_miscounted_as_Goldstone",
        "hundred_exact_cases_cover_0_through_99",
        "hundred_exact_cases_pass",
        "upstream_combined_MSbar_kernel_closed",
        "background_field_heat_kernel_not_overclaimed",
        "pole_masses_not_overclaimed",
        "physical_G6_G7_fail_closed",
    }
    current_blockers = [
        "Derive a background-covariant vector/Goldstone/FP-ghost operator and heat-kernel replay if an independent derivation of the already frozen Hall/Ellis-Wells coefficient is required.",
        "Supply renormalized couplings, VEVs, scalar/Yukawa tensors, a tadpole prescription, and the transverse self-energies needed to solve every vector pole equation.",
        "Consume the closed exact source-derived 37-row Hessian and its exact eaten-direction quotient to construct the complete scalar and fermion mass/mixing matrices, pole self-energies, and thresholds.",
        "Construct the stationary pre-electroweak SU(3)xSU(2)xU(1) stage and complete the Yukawa/scalar/dimensionful/EFT flow.",
    ]
    checks_in = report.get("checks", {})
    direction = report.get("direction_census", {})
    theorem = report.get("one_real_broken_direction_theorem", {})
    all_directions = report.get("all_37_direction_identity", {})
    audit100 = report.get("hundred_point_exact_audit", {})
    operator_scope = report.get("quadratic_operator_scope", {})
    checks = {
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "exact_physical_sm_vector_rxi_vacuum_cancellation_v1"
            and report.get("contract_id")
            == "exact_physical_sm_vector_rxi_vacuum_cancellation_v20"
            and report.get("status")
            == "EXACT_ALL_37_BROKEN_DIRECTION_RXI_VACUUM_DETERMINANT_CANCELLATION_CLOSED__BACKGROUND_FIELD_POLE_AND_FULL_G6_G7_OPEN"
            and report.get("core_sha256")
            == PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
            and _canonical_json_line_sha256(
                {key: value for key, value in report.items() if key != "core_sha256"}
            )
            == PHYSICAL_SM_VECTOR_RXI_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_SM_VECTOR_RXI_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_SM_VECTOR_RXI_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_VECTOR_RXI_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_VECTOR_RXI_MD_RAW_SHA256
        ),
        "dependency_bindings_exact": report.get("source_binding")
        == expected_sources,
        "embedded_checks_exact": (
            set(checks_in) == expected_checks
            and all(checks_in.get(name) is True for name in expected_checks)
            and report.get("n_checks") == len(expected_checks)
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "scope_truth_boundary_exact": report.get("scope") == expected_scope,
        "operator_scope_exact": (
            operator_scope.get("background")
            == "constant stationary scalar vacuum; zero background gauge field"
            and operator_scope.get("gauge") == "linear R_xi with xi>0"
            and operator_scope.get("spacetime")
            == "flat four-dimensional vacuum"
            and operator_scope.get("mass_definition")
            == "positive tree running mass eigenvalue"
        ),
        "one_direction_identity_exact": (
            theorem.get("D_xiM_net_exponent") == "0"
            and theorem.get("field_independent_log_xi_coefficient") == "-1/2"
            and theorem.get("normalized_unphysical_determinant") == 1
            and theorem.get("physical_D_M_exponent") == "3/2"
        ),
        "all_37_direction_census_exact": (
            direction.get("total_gauge_dimension") == 46
            and direction.get("total_broken_real_directions") == 37
            and direction.get("gauge_Goldstone_directions") == 37
            and direction.get("complex_FP_ghost_pairs") == 37
            and direction.get("charged_non_neutral_real_directions") == 34
            and direction.get("neutral_massive_real_directions") == 3
            and direction.get("massless_unbroken_real_directions") == 9
            and direction.get("uneaten_global_PQ_direction_excluded") == 1
            and all_directions.get(
                "vacuum_normalized_unphysical_squared_determinant"
            )
            == "1"
            and all_directions.get("remaining_physical_polarizations") == 111
        ),
        "hundred_exact_cases_exact": (
            audit100.get("case_count") == 100
            and audit100.get("case_range") == [0, 99]
            and audit100.get("all_exact_rational_cases_pass") is True
            and audit100.get("record_sha256")
            == "ea6e659e3753099a60842b6e4c515dd3b052426333954ec76dad8c8bffba194d"
        ),
        "upstream_snapshot_blockers_core_bound": (
            isinstance(report.get("blockers"), list)
            and len(report.get("blockers", [])) == 4
            and _canonical_json_line_sha256(report.get("blockers"))
            == "ef00917b3323b78a5d840ff4866acbe81ede25e3b792e5b3488261874365f5a7"
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION",
        "source_bound": source_bound,
        "zero_background_Rxi_vacuum_determinant_cancellation_closed": bool(
            source_bound
        ),
        "all_37_broken_directions_closed": bool(source_bound),
        "Goldstone_FPghost_double_count_guard_closed": bool(source_bound),
        "background_covariant_heat_kernel_matching_closed": False,
        "sector_resolved_general_background_determinants_closed": False,
        "pole_vector_masses_closed": False,
        "complete_scalar_fermion_thresholds_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "release_G6_verified": False,
        "release_G7_verified": False,
        "blockers": current_blockers if source_bound else [],
        "checks": checks,
    }


def _physical_sm_g6_g7_closure_frontier_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the negative closure frontier without promoting G6 or G7."""
    expected_top_level = {
        "schema",
        "contract_id",
        "status",
        "core_sha256",
        "source_binding",
        "completed_and_open_matrix",
        "exact_nonidentifiability_witnesses",
        "hundred_case_vector_scale_audit",
        "minimal_closure_path",
        "checks",
        "scope",
        "verdict",
        "n_checks",
        "n_failed",
        "failures",
    }
    expected_scope = {
        "corrected_physical_SM_terminal_artifacts_composed": True,
        "continuous_nonidentifiability_proved": True,
        "minimal_closure_path_machine_readable": True,
        "unique_absolute_tree_spectrum": False,
        "unique_pole_spectrum": False,
        "unique_threshold_vector": False,
        "unique_full_RGE_trajectory": False,
        "physical_G6": False,
        "physical_G7": False,
        "release_G6": False,
        "release_G7": False,
    }
    expected_checks = {
        "all_dependency_raw_and_core_hashes_match",
        "every_closed_scope_item_is_true",
        "every_open_scope_item_is_true",
        "scalar_completion_has_448_massive_modes",
        "conditional_scalar_spectrum_is_not_pole_spectrum",
        "scalar_b_scale_is_not_identified",
        "vector_scale_is_not_identified",
        "vector_SU3_scale_shift_is_35_over_4",
        "vector_QED_scale_shift_is_112_over_3",
        "ten_symbolic_flavor_tensors_present",
        "fifty_complex_flavor_entries_remain",
        "zero_and_nonzero_Yukawa_boundaries_change_Y4",
        "hundred_vector_scale_witnesses_cover_0_through_99",
        "minimal_path_is_strictly_ordered",
        "physical_G6_fail_closed",
        "physical_G7_fail_closed",
    }
    expected_sources = {
        "physical_SM_vacuum_foundation": {
            "path": "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
            "raw_sha256": PHYSICAL_SM_VACUUM_RAW_SHA256,
            "core_sha256": PHYSICAL_SM_VACUUM_CORE_SHA256,
        },
        "conditional_physical_SM_scalar_spectrum": {
            "path": "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json",
            "raw_sha256": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_RAW_SHA256,
            "core_sha256": CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_CORE_SHA256,
        },
        "physical_SM_heavy_vector_masses": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256,
            "core_sha256": PHYSICAL_SM_HEAVY_VECTOR_CORE_SHA256,
        },
        "physical_SM_heavy_vector_MSbar_matching": {
            "path": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
            "raw_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256,
            "core_sha256": PHYSICAL_SM_HEAVY_VECTOR_MSBAR_CORE_SHA256,
        },
        "physical_SM_vector_Rxi_vacuum_cancellation": {
            "path": "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json",
            "raw_sha256": PHYSICAL_SM_VECTOR_RXI_RAW_SHA256,
            "core_sha256": PHYSICAL_SM_VECTOR_RXI_CORE_SHA256,
        },
        "normalized_SO10_Yukawa_CGCs": {
            "path": "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
            "raw_sha256": NORMALIZED_YUKAWA_CGCS_RAW_SHA256,
            "core_sha256": NORMALIZED_YUKAWA_CGCS_CORE_SHA256,
        },
        "physical_G7_component_threshold_contract": {
            "path": "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
            "raw_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_SHA256,
            "core_sha256": PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256,
        },
    }
    checks_in = report.get("checks", {})
    matrix = report.get("completed_and_open_matrix", {})
    witnesses = report.get("exact_nonidentifiability_witnesses", {})
    vector = witnesses.get("vector_common_scale", {})
    scalar = witnesses.get("scalar_EFT_b_scale", {})
    flavor = witnesses.get("flavor_boundaries", {})
    audit100 = report.get("hundred_case_vector_scale_audit", {})
    closure_path = report.get("minimal_closure_path", [])
    checks = {
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "exact_physical_sm_g6_g7_closure_frontier_v1"
            and report.get("contract_id")
            == "exact_physical_sm_g6_g7_closure_frontier_v20"
            and report.get("status")
            == "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_AND_NONIDENTIFIABILITY_CLOSED__PHYSICAL_G6_G7_REMAIN_OPEN"
            and report.get("core_sha256")
            == PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
            and _canonical_json_line_sha256(
                {key: value for key, value in report.items() if key != "core_sha256"}
            )
            == PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_SM_G6_G7_FRONTIER_RAW_SHA256
            and source_raw_sha256
            == PHYSICAL_SM_G6_G7_FRONTIER_SOURCE_RAW_SHA256
            and test_raw_sha256
            == PHYSICAL_SM_G6_G7_FRONTIER_TEST_RAW_SHA256
            and markdown_raw_sha256
            == PHYSICAL_SM_G6_G7_FRONTIER_MD_RAW_SHA256
        ),
        "dependency_bindings_exact": report.get("source_binding")
        == expected_sources,
        "embedded_checks_exact": (
            set(checks_in) == expected_checks
            and all(checks_in.get(name) is True for name in expected_checks)
            and report.get("n_checks") == len(expected_checks)
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "scope_truth_boundary_exact": report.get("scope") == expected_scope,
        "completion_and_open_matrix_exact": (
            set(matrix) == {"closed", "open"}
            and len(matrix.get("closed", {})) == 8
            and len(matrix.get("open", {})) == 11
            and all(value is True for value in matrix.get("closed", {}).values())
            and all(value is True for value in matrix.get("open", {}).values())
        ),
        "nonidentifiability_witnesses_exact": (
            vector.get("absolute_vector_scale_identified") is False
            and vector.get("threshold_changes") is True
            and vector.get("log_shift_coefficients")
            == {"SU3": "35/4", "QED": "112/3"}
            and scalar.get("dimensionful_scalar_scale_identified") is False
            and scalar.get("massive_mode_count") == 448
            and scalar.get("b_scale_ratio_kappa") == "3"
            and flavor.get("symbol_count") == 10
            and flavor.get("raw_complex_entries_before_flavour_quotients")
            == 50
            and flavor.get("raw_real_degrees_before_flavour_quotients") == 100
            and flavor.get("flavor_boundary_values_identified") is False
        ),
        "hundred_scale_cases_exact": (
            audit100.get("case_count") == 100
            and audit100.get("case_range") == [0, 99]
            and audit100.get("all_are_distinct_from_lambda_one") is True
            and audit100.get("record_sha256")
            == "4c290e7a376ac3121aeadbf15ea39874d8986612caa65be68e75e6a062dbad14"
        ),
        "minimal_closure_path_exact": (
            isinstance(closure_path, list)
            and len(closure_path) == 7
            and [row.get("order") for row in closure_path]
            == list(range(1, 8))
            and closure_path[0].get("deliverable")
            == "authoritative external model execution"
            and closure_path[-1].get("deliverable")
            == "independent replay and release"
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER",
        "source_bound": source_bound,
        "corrected_terminal_artifacts_composed": bool(source_bound),
        "continuous_nonidentifiability_proved": bool(source_bound),
        "minimal_closure_path_machine_readable": bool(source_bound),
        "unique_absolute_tree_spectrum": False,
        "unique_pole_spectrum": False,
        "unique_threshold_vector": False,
        "unique_full_RGE_trajectory": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
        "release_G6_verified": False,
        "release_G7_verified": False,
        "closed_scope": sorted(matrix.get("closed", {})) if source_bound else [],
        "precise_open_scope": sorted(matrix.get("open", {}))
        if source_bound
        else [],
        "minimal_closure_path": closure_path if source_bound else [],
        "checks": checks,
    }


def _physical_sm_g8_identifiability_frontier_contract(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
    test_raw_sha256: str = "",
    markdown_raw_sha256: str = "",
) -> dict[str, Any]:
    """Bind the exact G8 non-identifiability theorem without promoting G8."""
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
    expected_scope = {
        "canonical_G8_contract_audited": True,
        "continuous_absolute_scale_nonidentifiability_proved": True,
        "flavor_and_interference_nonidentifiability_audited": True,
        "repository_frozen_single_channel_constraint_computed": True,
        "negative_no_go_for_future_G8_closure": False,
        "unique_proton_lifetime_or_distribution": False,
        "physical_G8": False,
        "release_G8": False,
        "authoritative_G8": False,
        "whole_model_excluded_by_conditional_points": False,
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
    checks_in = report.get("checks", {})
    checks = {
        "schema_status_core_exact": (
            set(report) == expected_top_level
            and report.get("schema")
            == "exact_physical_sm_g8_identifiability_frontier_v1"
            and report.get("contract_id")
            == "exact_physical_sm_g8_identifiability_frontier_v20"
            and report.get("status")
            == "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_CLOSED__PHYSICAL_RELEASE_AUTHORITATIVE_G8_OPEN"
            and report.get("core_sha256")
            == PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
            and _canonical_json_line_sha256(
                {key: value for key, value in report.items() if key != "core_sha256"}
            )
            == PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
        ),
        "all_four_raw_artifact_pins_exact": (
            raw_sha256 == PHYSICAL_SM_G8_FRONTIER_RAW_SHA256
            and source_raw_sha256 == PHYSICAL_SM_G8_FRONTIER_SOURCE_RAW_SHA256
            and test_raw_sha256 == PHYSICAL_SM_G8_FRONTIER_TEST_RAW_SHA256
            and markdown_raw_sha256 == PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256
        ),
        "embedded_checks_exact": (
            set(checks_in) == expected_checks
            and all(checks_in.get(name) is True for name in expected_checks)
            and report.get("n_checks") == len(expected_checks)
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "scope_truth_boundary_exact": report.get("scope") == expected_scope,
        "canonical_G8_contract_exact": (
            canonical.get("gap_id")
            == "canonical.gauged_u1x.phenomenology.v21.G8.unique_proton_lifetime_distribution"
            and canonical.get("required_artifact")
            == "CANONICAL_G8_UNIQUE_PROTON_LIFETIME_V21.json"
            and canonical.get("required_evidence_schema")
            == "canonical_gauged_u1x_gate_evidence_v1"
            and canonical.get("definition_sha256")
            == "1ecc4a5ae0cb1c51a24438f56f4181a2e1cc03c0fc17bc4ca2c0ce522be75df5"
            and canonical.get("dependencies")
            == [
                "canonical.gauged_u1x.phenomenology.v21.G5.calg_axion_phase_revalidation",
                "canonical.gauged_u1x.phenomenology.v21.G6.full_nonsusy_two_loop_chain",
                "canonical.gauged_u1x.phenomenology.v21.G7.physical_pole_threshold_spectrum",
            ]
            and len(canonical.get("acceptance", [])) == 5
        ),
        "all_five_acceptance_criteria_fail_closed": (
            list(acceptance) == [f"criterion_{index}" for index in range(1, 6)]
            and all(row.get("passed") is False for row in acceptance.values())
        ),
        "exact_scale_and_limit_crossing_witness": (
            vector.get("partial_lifetime_ratio_at_fixed_dimensionless_data")
            == "16"
            and vector.get("threshold_log_coefficients")
            == {"SU3": "35/4", "QED": "112/3"}
            and vector.get("absolute_vector_scale_identified") is False
            and crossing.get("below_limit_completion", {}).get(
                "lifetime_margin_over_limit"
            )
            == "1/16"
            and crossing.get("above_limit_completion", {}).get(
                "lifetime_margin_over_limit"
            )
            == "16"
            and crossing.get("same_normalized_vector_spectrum") is True
            and crossing.get("model_classification_identified_without_absolute_scale")
            is False
        ),
        "flavor_and_interference_witness_exact": (
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
        "scale_grid_0_through_100_exact": (
            audit.get("case_range") == [0, 100]
            and audit.get("case_count") == 101
            and audit.get("identity_case") == 50
            and audit.get("all_scaling_identities_exact") is True
            and audit.get("records_sha256")
            == "7402efea7c377a709a4bb33ec08a0e717418973c38e3e684de54ea92489311cd"
        ),
        "PDG_2025_numeric_constraint_exact_but_not_unique_prediction": (
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
        ),
        "minimal_exhibited_free_vector_exact": (
            minimum.get("coordinates") == ["lambda_v"]
            and minimum.get("real_dimension") == 1
            and minimum.get("claim_of_global_parameter_minimality") is False
            and free_vector.get(
                "exhibited_raw_real_dimension_including_v_b_and_all_flavor_entries"
            )
            == 102
        ),
        "theory_vs_measured_vs_laboratory_boundary_exact": (
            len(missing.get("continuous_boundary_values_or_distributions", []))
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
    source_bound = all(checks.values())
    return {
        "namespace": "PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER",
        "source_bound": source_bound,
        "canonical_G8_contract_audited": bool(source_bound),
        "continuous_absolute_scale_nonidentifiability_proved": bool(source_bound),
        "flavor_and_interference_nonidentifiability_audited": bool(source_bound),
        "repository_frozen_PDG_2025_single_channel_constraint_verified": bool(
            source_bound
        ),
        "minimal_exhibited_joint_free_real_dimension": 1 if source_bound else None,
        "unique_proton_lifetime_or_distribution": False,
        "physical_G8_closed": False,
        "release_G8_verified": False,
        "authoritative_G8_closed": False,
        "whole_model_excluded_by_conditional_points": False,
        "all_acceptance_criteria_pass": False,
        "precise_missing_inputs": missing if source_bound else {},
        "checks": checks,
    }


def _physical_g7_recalculated_input_resolution(
    component_thresholds: dict[str, Any],
    normalized_yukawa_cgcs: dict[str, Any],
    heavy_vectors: dict[str, Any],
    heavy_vector_msbar_matching: dict[str, Any],
    vector_rxi_vacuum_cancellation: dict[str, Any],
    conditional_scalar_spectrum: dict[str, Any],
    closure_frontier: dict[str, Any],
) -> dict[str, Any]:
    """Overlay newly closed scoped inputs and retain only precise open work."""
    source_bound = bool(
        component_thresholds.get("source_bound") is True
        and normalized_yukawa_cgcs.get("source_bound") is True
        and heavy_vectors.get("source_bound") is True
        and heavy_vector_msbar_matching.get("source_bound") is True
        and vector_rxi_vacuum_cancellation.get("source_bound") is True
        and conditional_scalar_spectrum.get("source_bound") is True
        and closure_frontier.get("source_bound") is True
    )
    resolved_scoped_inputs = {
        "physical_PS_SM_matter_branching": bool(
            source_bound
            and component_thresholds.get("physical_PS_SM_matter_branching_closed")
            is True
        ),
        "parameterized_one_loop_matter_threshold_kernel": bool(
            source_bound
            and component_thresholds.get(
                "parameterized_one_loop_matter_threshold_kernel_closed"
            )
            is True
        ),
        "normalized_SO10_representation_CGCs": bool(
            source_bound
            and normalized_yukawa_cgcs.get(
                "all_declared_representation_CGCs_closed"
            )
            is True
        ),
        "canonical_304_Weyl_sparse_embedding": bool(
            source_bound
            and normalized_yukawa_cgcs.get(
                "canonical_304_Weyl_sparse_embedding_closed"
            )
            is True
        ),
        "exact_parameterized_physical_SM_tree_vector_mass_matrix": bool(
            source_bound
            and heavy_vectors.get(
                "exact_parameterized_tree_vector_mass_matrix_closed"
            )
            is True
        ),
        "exact_heavy_vector_physical_target_provenance": bool(source_bound),
        "exact_vector_rank_kernel_and_Goldstone_image": bool(
            source_bound
            and heavy_vectors.get(
                "exact_vector_rank_kernel_and_Goldstone_image_closed"
            )
            is True
        ),
        "exact_SU3C_U1em_vector_sector_resolution": bool(
            source_bound
            and heavy_vectors.get(
                "exact_SU3C_x_U1em_vector_sector_resolution_closed"
            )
            is True
        ),
        "parameterized_vector_threshold_log_inputs": bool(
            source_bound
            and heavy_vectors.get(
                "parameterized_vector_threshold_log_inputs_closed"
            )
            is True
        ),
        "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel": bool(
            source_bound
            and heavy_vector_msbar_matching.get(
                "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
            )
            is True
        ),
        "finite_MSbar_heavy_vector_constant": bool(
            source_bound
            and heavy_vector_msbar_matching.get(
                "finite_MSbar_vector_constant_closed"
            )
            is True
        ),
        "heavy_vector_Goldstone_double_count_guard": bool(
            source_bound
            and heavy_vector_msbar_matching.get(
                "Goldstone_double_count_guard_active"
            )
            is True
        ),
        "zero_background_Rxi_vacuum_determinant_cancellation": bool(
            source_bound
            and vector_rxi_vacuum_cancellation.get(
                "zero_background_Rxi_vacuum_determinant_cancellation_closed"
            )
            is True
        ),
        "conditional_reconstructed_tree_scalar_spectrum": bool(
            source_bound
            and conditional_scalar_spectrum.get(
                "conditional_reconstructed_tree_scalar_spectrum_closed"
            )
            is True
        ),
        "continuous_G6_G7_nonidentifiability_frontier": bool(
            source_bound
            and closure_frontier.get("continuous_nonidentifiability_proved")
            is True
        ),
    }
    precise_open_inputs = {
        "SARAH_implicit_Dot_to_identical_Weyl_contraction_conversion": False,
        "flavor_tensor_values_textures_and_boundary_conditions": False,
        "complete_one_and_two_loop_Yukawa_beta_system": False,
        "background_covariant_heat_kernel_and_general_background_determinants": False,
        "one_loop_tree_to_pole_vector_mass_conversion_and_tadpole_VEV_scheme": False,
        "stationary_SM_symmetric_pre_EW_heavy_vector_matching": False,
        "complete_scalar_and_fermion_threshold_matching": False,
        "matching_scheme_physical_scale_and_running_coupling_boundaries": False,
        "source_algebra_derived_physical_scalar_Hessian": False,
        "physical_scalar_pole_masses": False,
        "complete_scalar_dimensionful_and_EFT_beta_system": False,
        "second_independent_full_RGE_threshold_implementation": False,
    }
    return {
        "namespace": "PHYSICAL_G7_RECALCULATED_INPUT_RESOLUTION",
        "source_bound": source_bound,
        "resolved_scoped_inputs": resolved_scoped_inputs,
        "all_resolved_scoped_inputs_closed": bool(
            source_bound and all(resolved_scoped_inputs.values())
        ),
        "superseded_stale_blockers": {
            "normalized_304_Weyl_Yukawa_tensor_embeddings_open": bool(
                source_bound
                and resolved_scoped_inputs[
                    "normalized_SO10_representation_CGCs"
                ]
                and resolved_scoped_inputs[
                    "canonical_304_Weyl_sparse_embedding"
                ]
            ),
            "heavy_vector_provenance_and_tree_mass_matrix_not_matched": bool(
                source_bound
                and resolved_scoped_inputs[
                    "exact_heavy_vector_physical_target_provenance"
                ]
                and resolved_scoped_inputs[
                    "exact_parameterized_physical_SM_tree_vector_mass_matrix"
                ]
            ),
            "generic_heavy_vector_Goldstone_ghost_matching_open": bool(
                source_bound
                and resolved_scoped_inputs[
                    "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel"
                ]
                and resolved_scoped_inputs["finite_MSbar_heavy_vector_constant"]
            ),
        },
        "precise_open_inputs": precise_open_inputs,
        "physical_G6_closed": False,
        "mathematical_G7_closed": False,
        "physical_G7_closed": False,
        "release_G7_verified": False,
    }


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_line_sha256(value: Any) -> str:
    """Hash canonical JSON with the producer contract's terminal newline."""
    payload = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    try:
        # Git may materialize text sources with CRLF on Windows.  The frozen
        # provenance certificates use the repository's canonical LF bytes.
        payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(payload).hexdigest()
    except OSError:
        return ""


def _raw_file_sha256(path: Path) -> str:
    """Hash the exact artifact bytes without newline canonicalization."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _rank1_su4_stabilizer_infrastructure_exact(report: dict[str, Any]) -> bool:
    """Validate the fixed-endpoint SU(4) stabilizer without promoting G3."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    tangent = report.get("joint_stabilizer_tangent", {})
    endpoint = tangent.get("fixed_endpoint", {})
    source_actions = tangent.get("source_actions", {})
    phi210 = report.get("Phi210_action", {})
    required_checks = (
        "fifteen_correct_shifted_SU4_generators_exact",
        "fixed_h_minus_q_over_4_endpoint_bound_exact",
        "joint_tangent_rank_30_modular_lower_bound_exact",
        "explicit_fifteen_dimensional_kernel_upper_bound_exact",
        "joint_stabilizer_kernel_exhausted_exactly_by_SU4",
        "old_offset_zero_SU4_embedding_rejected_by_h_minus_exactly",
        "integral_SU4_Lie_structure_constants_close_exactly",
        "Phi210_actions_integral_skew_faithful_and_Lie_exact",
    )
    required_scope_keys = {
        "G3_closed",
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4",
        "arbitrary_Phi_Schur_SOS_SDP_constructed",
        "arbitrary_Phi_Schur_SOS_SDP_feasible",
        "arbitrary_max_negative_Sigma_proved",
        "arbitrary_rank1_Phi_bound_proved",
        "common_continuous_stabilizer_identified_as_SU4",
        "exact_Phi210_SU4_action_available_for_next_stage",
        "infrastructure_only",
        "whole_model_excluded",
    }
    required_endpoint_keys = {
        "H",
        "H_numerator_norm_squared",
        "Sigma",
        "endpoint_binding_exact",
        "integer_tangent_numerators",
        "q",
        "q_coordinate_norm_squared",
    }
    generator_basis = report.get("generator_basis", {})
    lie_algebra = report.get("Lie_algebra", {})
    wrong_offset = tangent.get("wrong_offset_zero_SU4_negative_control", {})
    return bool(
        report.get("n_checks") == len(required_checks)
        and report.get("n_failed") == 0
        and report.get("failed_checks") == []
        and report.get("status")
        == "EXACT_RANK1_SU4_STABILIZER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "STABILIZER_INFRASTRUCTURE_CLOSED__ARBITRARY_PHI_SDP_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and set(checks) == set(required_checks)
        and set(scope) == required_scope_keys
        and set(endpoint) == required_endpoint_keys
        and all(checks.get(name) is True for name in required_checks)
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get(
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4"
        )
        is True
        and scope.get("common_continuous_stabilizer_identified_as_SU4") is True
        and scope.get("exact_Phi210_SU4_action_available_for_next_stage") is True
        and scope.get("infrastructure_only") is True
        and scope.get("arbitrary_Phi_Schur_SOS_SDP_constructed") is False
        and scope.get("arbitrary_Phi_Schur_SOS_SDP_feasible") is False
        and scope.get("arbitrary_rank1_Phi_bound_proved") is False
        and scope.get("arbitrary_max_negative_Sigma_proved") is False
        and scope.get("G3_closed") is False
        and scope.get("whole_model_excluded") is False
        and tangent.get("proof_grade") is True
        and tangent.get("prime") == RANK1_SU4_MODULAR_PRIME
        and tangent.get("displayed_kernel_rank_mod_prime") == 15
        and tangent.get("displayed_kernel_residual_max_abs") == 0
        and tangent.get("exact_tangent_rank_over_Q_R") == 30
        and tangent.get("exact_tangent_nullity") == 15
        and tangent.get("displayed_kernel_shape") == [45, 15]
        and tangent.get("explicit_kernel_is_complete") is True
        and tangent.get("joint_tangent_rank_mod_prime") == 30
        and tangent.get("joint_tangent_shape") == [272, 45]
        and tangent.get("rank_lower_bound_over_Q_R") == 30
        and tangent.get("kernel_upper_bound_on_tangent_rank") == 30
        and endpoint.get("endpoint_binding_exact") is True
        and endpoint.get("H") == "h_-=(e0-i e1)/sqrt(2)"
        and endpoint.get("Sigma") == "q/4"
        and endpoint.get("q")
        == "q=(e0+i e1)(e2+i e3)(e4+i e5)(e6+i e7)(e8+i e9)"
        and endpoint.get("H_numerator_norm_squared") == 2
        and endpoint.get("q_coordinate_norm_squared") == 16
        and source_actions.get("SO10_generator_count") == 45
        and source_actions.get("H_action_shape") == [45, 10, 10]
        and source_actions.get("Sigma_action_shape") == [45, 126, 126]
        and source_actions.get("ordered_generator_labels_match_exactly") is True
        and source_actions.get("H_generators_integral_real_skew") is True
        and source_actions.get(
            "Sigma_generators_Gaussian_integral_antihermitian"
        )
        is True
        and wrong_offset.get("H_tangent_residual_max_abs") == 1
        and wrong_offset.get("Sigma_tangent_residual_max_abs") == 0
        and wrong_offset.get("joint_tangent_residual_max_abs") == 1
        and wrong_offset.get("does_not_stabilize_fixed_h_minus") is True
        and wrong_offset.get("wrong_embedding_rejected_exactly") is True
        and phi210.get("proof_grade") is True
        and phi210.get("prime") == RANK1_SU4_MODULAR_PRIME
        and phi210.get("representation") == "real Lambda^4(R^10) = Phi210"
        and phi210.get("action_count") == 15
        and phi210.get("action_shapes") == [[210, 210]]
        and phi210.get("ordered_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and phi210.get("all_action_dtypes_integral") is True
        and phi210.get("maximum_abs_action_entry") == 1
        and phi210.get("flattened_action_rank_mod_prime") == 15
        and phi210.get("skew_transpose_max_abs_residual") == 0
        and phi210.get("Lie_commutator_reconstruction_max_abs") == 0
        and bool(phi210.get("source_binding"))
        and generator_basis.get("proof_grade") is True
        and generator_basis.get("prime") == RANK1_SU4_MODULAR_PRIME
        and generator_basis.get("generator_count") == 15
        and generator_basis.get("Cartan_generator_count") == 3
        and generator_basis.get("offdiagonal_generator_count") == 12
        and generator_basis.get("complex_planes")
        == [[2, 3], [4, 5], [6, 7], [8, 9]]
        and generator_basis.get("coefficient_matrix_shape") == [45, 15]
        and generator_basis.get("coefficient_rank_mod_prime") == 15
        and generator_basis.get("ordered_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and generator_basis.get("all_coefficients_are_signed_units") is True
        and generator_basis.get("all_support_is_in_indices_2_through_9") is True
        and lie_algebra.get("proof_grade") is True
        and lie_algebra.get("Lie_algebra_dimension") == 15
        and lie_algebra.get("basis_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and lie_algebra.get("Cartan_commutator_max_abs") == 0
        and lie_algebra.get("Jacobi_max_abs_residual") == 0
        and lie_algebra.get("antisymmetry_max_abs_residual") == 0
        and lie_algebra.get("coefficient_commutator_reconstruction_max_abs") == 0
        and lie_algebra.get("vector_commutator_reconstruction_max_abs") == 0
        and lie_algebra.get("maximum_abs_structure_constant") == 2
        and lie_algebra.get("coordinate_block_unimodular") is True
        and lie_algebra.get("structure_constants_integral") is True
    )


def _rank1_su4_phi210_intertwiners_exact(
    report: dict[str, Any], stabilizer_report: dict[str, Any]
) -> bool:
    """Validate the 210 intertwiner census and every open-scope guard."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("companion_stabilizer_provenance", {})
    intertwiner = report.get("intertwiner", {})
    rows = intertwiner.get("intertwinings", [])
    carriers = report.get("carriers", {})
    carrier_rows = carriers.get("carriers", [])
    character = report.get("character_branching", {})
    integral_c8 = report.get("integral_C8", {})
    companion_tangent = stabilizer_report.get("joint_stabilizer_tangent", {})
    companion_phi210 = stabilizer_report.get("Phi210_action", {})
    required_true_checks = (
        "Gaussian_exterior_basis_Bdagger_B_equals_16I_exact",
        "all_15_live_SU4_intertwinings_exact",
        "Cartan_weights_exact",
        "SSYT_character_branching_exact",
        "integral_C8_spectrum_and_minimal_polynomial_exact",
        "deterministic_25_carrier_decomposition_complete",
        "Sym2_invariant_multiplicity_is_45_exact",
        "companion_model_contract_matches_exactly",
        "companion_stabilizer_report_green_and_endpoint_scoped",
        "companion_h_minus_q_over_4_tangent_provenance_exact",
        "companion_Phi210_action_provenance_exact",
        "companion_embedded_certificates_match_live_inputs",
    )
    required_false_checks = {
        "SU4_Schur_SDP_constructed",
        "arbitrary_Phi_bound_proved",
        "G3_closed",
    }
    required_scope_keys = {
        "G3_closed",
        "H_fixed_to_h_minus",
        "Phi210_complexified_representation_resolved",
        "SU4_invariant_quadratic_form_basis_constructed",
        "Schur_SOS_SDP_constructed",
        "Sigma_fixed_to_q_over_4",
        "Sym2_SU4_invariant_dimension_45_proved",
        "arbitrary_rank1_Phi_proved",
        "arbitrary_real_Phi_lower_bound_proved",
        "companion_stabilizer_provenance_exact",
        "deterministic_irreducible_carriers_complete",
        "rank1_endpoint_SU4_stabilizer_used",
        "whole_model_excluded",
    }
    required_provenance_keys = {
        "Phi210_action_proof_grade",
        "all_required_provenance_exact",
        "fixed_endpoint",
        "model_contract_id",
        "module",
        "n_failed",
        "overall_state",
        "status",
        "tangent_proof_grade",
    }
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and report.get("n_checks") == 15
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and report.get("status")
        == "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and set(checks) == set(required_true_checks) | required_false_checks
        and set(scope) == required_scope_keys
        and set(provenance) == required_provenance_keys
        and all(checks.get(name) is True for name in required_true_checks)
        and checks.get("SU4_Schur_SDP_constructed") is False
        and checks.get("arbitrary_Phi_bound_proved") is False
        and checks.get("G3_closed") is False
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get("Sigma_fixed_to_q_over_4") is True
        and scope.get("rank1_endpoint_SU4_stabilizer_used") is True
        and scope.get("companion_stabilizer_provenance_exact") is True
        and scope.get("Phi210_complexified_representation_resolved") is True
        and scope.get("deterministic_irreducible_carriers_complete") is True
        and scope.get("Sym2_SU4_invariant_dimension_45_proved") is True
        and scope.get("SU4_invariant_quadratic_form_basis_constructed") is False
        and scope.get("Schur_SOS_SDP_constructed") is False
        and scope.get("arbitrary_real_Phi_lower_bound_proved") is False
        and scope.get("arbitrary_rank1_Phi_proved") is False
        and scope.get("G3_closed") is False
        and scope.get("whole_model_excluded") is False
        and provenance.get("all_required_provenance_exact") is True
        and provenance.get("module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and provenance.get("model_contract_id")
        == stabilizer_report.get("model_contract_id")
        and provenance.get("n_failed") == stabilizer_report.get("n_failed")
        and provenance.get("status") == stabilizer_report.get("status")
        and provenance.get("overall_state")
        == stabilizer_report.get("overall_state")
        and provenance.get("fixed_endpoint")
        == companion_tangent.get("fixed_endpoint")
        and provenance.get("tangent_proof_grade")
        == companion_tangent.get("proof_grade")
        and provenance.get("Phi210_action_proof_grade")
        == companion_phi210.get("proof_grade")
        and intertwiner.get("proof_grade") is True
        and intertwiner.get("exterior_basis_shape") == [210, 210]
        and intertwiner.get("exterior_basis_Bdagger_B_equals_16I_exact") is True
        and intertwiner.get("one_form_Gram_real_exact") is True
        and intertwiner.get("one_form_Gram_imaginary_zero_exact") is True
        and intertwiner.get("Cartan_weight_diagonalization_exact") is True
        and intertwiner.get("n_distinct_Cartan_weights") == 65
        and intertwiner.get("zero_weight_multiplicity") == 12
        and intertwiner.get("intertwining_count") == 15
        and intertwiner.get("all_15_intertwinings_exact") is True
        and isinstance(rows, list)
        and len(rows) == 15
        and all(
            row.get("exact") is True
            and row.get("real_residual_max_abs") == 0
            and row.get("imaginary_residual_max_abs") == 0
            for row in rows
            if isinstance(row, dict)
        )
        and all(isinstance(row, dict) for row in rows)
        and [row.get("generator") for row in rows]
        == list(RANK1_SU4_ORDERED_LABELS)
        and character.get("proof_grade") is True
        and character.get("exterior_dimension") == 210
        and character.get("SSYT_reconstructed_dimension") == 210
        and character.get("all_SSYT_dimensions_exact") is True
        and character.get("SSYT_character_identity_exact") is True
        and integral_c8.get("proof_grade") is True
        and integral_c8.get("shape") == [210, 210]
        and integral_c8.get("integral") is True
        and integral_c8.get("symmetric_exact") is True
        and integral_c8.get("commutes_with_all_15_generators_exact") is True
        and integral_c8.get("spectrum_exact_over_Q") is True
        and integral_c8.get("minimal_polynomial_exact") is True
        and integral_c8.get("minimal_polynomial_annihilates_exact") is True
        and integral_c8.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and integral_c8.get("minimal_polynomial_roots")
        == [0, 15, 20, 32, 36, 39, 48]
        and integral_c8.get("annihilator_intermediate_maxima")[-1:] == [0]
        and integral_c8.get("modular_nullities_sum") == 210
        and integral_c8.get("modular_eigenspace_nullities")
        == {
            "0": 4,
            "15": 32,
            "20": 24,
            "32": 30,
            "36": 20,
            "39": 80,
            "48": 20,
        }
        and integral_c8.get("expected_spectrum_multiplicities")
        == {
            "0": 4,
            "15": 32,
            "20": 24,
            "32": 30,
            "36": 20,
            "39": 80,
            "48": 20,
        }
        and integral_c8.get("canonical_Phi210_symmetric_exact") is True
        and integral_c8.get("canonical_to_exterior_C8_intertwining_exact") is True
        and integral_c8.get("imaginary_part_zero_exact") is True
        and integral_c8.get("int64_arithmetic_safe") is True
        and carriers.get("proof_grade") is True
        and carriers.get("carrier_count") == 25
        and carriers.get("concatenated_carrier_shape") == [210, 210]
        and carriers.get("concatenated_carrier_rank_mod_prime") == 210
        and carriers.get("Sym2_Phi210_SU4_singlet_dimension") == 45
        and carriers.get("SU4_invariant_quadratic_multiplicity_sector_dimension")
        == 45
        and "future_Schur_SDP_multiplicity_matrix_dimension" not in carriers
        and carriers.get("natural_exterior_block_count") == 16
        and isinstance(carrier_rows, list)
        and len(carrier_rows) == 25
        and all(
            isinstance(row, dict)
            and row.get("C8_eigen_equation_exact") is True
            and row.get("SSYT_character_exact") is True
            and row.get("exact_modular_rank") == row.get("expected_dimension")
            for row in carrier_rows
        )
        and carriers.get("all_15_generators_preserve_natural_blocks_exact")
        is True
        and carriers.get("all_carrier_dimensions_eigenvalues_characters_exact")
        is True
    )


def _rank1_su4_aligned_carriers_exact(
    report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    stabilizer_report: dict[str, Any],
) -> bool:
    """Fail closed on the literal 25-carrier alignment and physical real maps."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("upstream_provenance", {})
    source = provenance.get("source_contract", {})
    alignment = report.get("alignment", {})
    alignment_provenance = report.get("alignment_provenance", {})
    carriers = alignment.get("carriers", [])
    families = alignment.get("families", [])
    true_checks = {
        "model_contract_and_endpoint_provenance_exact",
        "upstream_source_bytes_match_pinned_contract_exact",
        "upstream_full_schema_and_literal_certificates_exact",
        "upstream_intertwiner_report_green_and_scope_exact",
        "upstream_live_Gaussian_intertwiner_exact",
        "upstream_25_carrier_census_exact",
        "upstream_embedded_certificates_match_live_inputs",
        "alignment_full_schema_and_literals_exact",
        "integral_A3_Chevalley_system_exact",
        "integer_and_rational_arithmetic_safety_exact",
        "deterministic_lowering_words_align_all_25_carriers_exact",
        "common_source_actions_on_all_equivalent_copies_exact",
        "physical_live_Phi210_embeddings_exact",
        "physical_conjugation_and_real_structures_exact",
        "aligned_25_carrier_direct_sum_rank_210_exact",
    }
    false_checks = {
        "SU4_invariant_quadratic_basis_constructed",
        "Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved",
        "G3_closed",
    }
    true_scope = {
        "H_fixed_to_h_minus", "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "aligned_complexified_Phi210_carriers_constructed",
        "physical_real_structure_and_Gaussian_embeddings_constructed",
    }
    false_scope = {
        "SU4_invariant_quadratic_form_basis_constructed",
        "Schur_SOS_SDP_constructed", "arbitrary_real_Phi_lower_bound_proved",
        "arbitrary_rank1_Phi_proved", "G3_closed", "whole_model_excluded",
    }
    provenance_keys = {
        "module", "model_contract_id", "status", "n_failed",
        "intertwiner_proof_grade", "carrier_proof_grade",
        "embedded_certificates_match", "source_contract",
        "source_contract_exact", "upstream_report_sha256",
        "expected_upstream_report_sha256",
        "upstream_intertwiner_certificate_sha256",
        "expected_upstream_intertwiner_certificate_sha256",
        "upstream_carrier_certificate_sha256",
        "expected_upstream_carrier_certificate_sha256",
        "full_schema_and_literals_exact", "all_required_provenance_exact",
    }
    source_keys = {
        "upstream_module", "upstream_module_sha256",
        "expected_upstream_module_sha256", "stabilizer_module",
        "stabilizer_module_sha256", "expected_stabilizer_module_sha256",
        "both_modules_resolve_to_repository_root_exact",
        "source_bytes_match_pinned_contract_exact", "proof_grade",
    }
    alignment_keys = {
        "proof_grade", "modular_prime", "generator_labels",
        "simple_Chevalley_system", "family_count", "families", "carrier_count",
        "carriers", "expected_irrep_multiplicities",
        "observed_irrep_multiplicities", "upstream_carrier_order_exact",
        "all_family_word_counts_equal_dimensions", "all_25_carriers_exact",
        "all_equivalent_copies_use_common_source_actions_exact",
        "concatenated_aligned_basis_shape",
        "concatenated_aligned_basis_rank_mod_prime",
        "concatenated_aligned_basis_sha256", "exact_rank_argument",
        "exterior_conjugation_shape",
        "exterior_conjugation_signed_permutation_exact",
        "exterior_conjugation_square_equals_identity_exact",
        "Gaussian_basis_conjugation_is_physical_exact",
        "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact",
        "all_25_conjugate_carrier_maps_exact",
        "all_25_conjugate_maps_involutive_exact",
        "conjugation_compatible_with_all_15_generators_exact",
        "complex_type_carrier_count", "self_conjugate_real_type_carrier_count",
        "rational_matrix_convention",
        "exact_integer_and_rational_arithmetic_safety",
    }
    carrier_keys = {
        "name", "irrep", "copy_index", "highest_weight", "dimension",
        "natural_block", "lowering_word_count", "lowering_word_maximum_length",
        "basis_maximum_absolute_entry", "basis_sha256",
        "aligned_rank_mod_prime", "highest_weight_primitive_and_raising_annihilated",
        "C8_eigen_equation_exact", "all_15_common_source_actions_intertwine_exact",
        "natural_block_support_exact", "source_action_denominators",
        "exterior_gram_sha256", "canonical_basis_real_sha256",
        "canonical_basis_imaginary_sha256",
        "all_15_live_canonical_Phi210_actions_intertwine_exact",
        "reality_kind", "conjugate_carrier_name", "conjugation_map_denominator",
        "conjugation_map_sha256", "conjugation_involution_exact",
        "physical_conjugation_embedding_exact",
    }
    family_keys = {
        "irrep", "dimension", "multiplicity", "reference_carrier_name",
        "lowering_words", "lowering_word_sha256", "common_source_action_count",
        "common_source_actions_sha256",
    }
    names = {row.get("name") for row in carriers if isinstance(row, dict)}
    rows_by_name = {
        row.get("name"): row for row in carriers if isinstance(row, dict)
    }
    upstream_intertwiner = intertwiners_report.get("intertwiner", {})
    upstream_carriers = intertwiners_report.get("carriers", {})
    expected_alignment_hash = (
        "f74b7845b57472f62773c398fa927b551b5d9d09f86bd7defb92a6ed71adbe15"
    )
    return bool(
        _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _canonical_json_sha256(report)
        == "d2da0572dc33a1f3f88b5ac5df3343201650ca660498f34ff59806a607015c67"
        and set(report) == {
            "status", "overall_state", "model_contract_id", "n_checks",
            "n_failed", "failures", "checks", "upstream_provenance",
            "alignment", "alignment_provenance", "scope", "next_exact_target",
            "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "SU4_ALIGNED_CARRIERS_CLOSED__INVARIANT_BASIS_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == 19
        and report.get("n_failed") == 0 and report.get("failures") == []
        and set(checks) == true_checks | false_checks
        and all(checks.get(key) is True for key in true_checks)
        and all(checks.get(key) is False for key in false_checks)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("status") == intertwiners_report.get("status")
        and provenance.get("n_failed") == 0
        and all(
            provenance.get(key) is True
            for key in (
                "intertwiner_proof_grade", "carrier_proof_grade",
                "embedded_certificates_match", "source_contract_exact",
                "full_schema_and_literals_exact", "all_required_provenance_exact",
            )
        )
        and provenance.get("upstream_report_sha256")
        == provenance.get("expected_upstream_report_sha256")
        == _canonical_json_sha256(intertwiners_report)
        and provenance.get("upstream_intertwiner_certificate_sha256")
        == provenance.get("expected_upstream_intertwiner_certificate_sha256")
        == _canonical_json_sha256(upstream_intertwiner)
        and provenance.get("upstream_carrier_certificate_sha256")
        == provenance.get("expected_upstream_carrier_certificate_sha256")
        == _canonical_json_sha256(upstream_carriers)
        and set(source) == source_keys
        and source.get("upstream_module") == provenance.get("module")
        and source.get("stabilizer_module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and source.get("upstream_module_sha256")
        == source.get("expected_upstream_module_sha256")
        == _file_sha256(ROOT / source.get("upstream_module", ""))
        and source.get("stabilizer_module_sha256")
        == source.get("expected_stabilizer_module_sha256")
        == _file_sha256(ROOT / source.get("stabilizer_module", ""))
        and all(
            source.get(key) is True
            for key in (
                "both_modules_resolve_to_repository_root_exact",
                "source_bytes_match_pinned_contract_exact", "proof_grade",
            )
        )
        and set(alignment_provenance) == {
            "certificate_sha256", "expected_live_certificate_sha256",
            "full_schema_and_literals_exact",
        }
        and alignment_provenance.get("full_schema_and_literals_exact") is True
        and alignment_provenance.get("certificate_sha256")
        == alignment_provenance.get("expected_live_certificate_sha256")
        == _canonical_json_sha256(alignment) == expected_alignment_hash
        and set(alignment) == alignment_keys
        and alignment.get("proof_grade") is True
        and alignment.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and alignment.get("generator_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and alignment.get("family_count") == len(families) == 10
        and alignment.get("carrier_count") == len(carriers) == len(names) == 25
        and alignment.get("expected_irrep_multiplicities") == RANK1_SU4_BRANCHING
        and alignment.get("observed_irrep_multiplicities") == RANK1_SU4_BRANCHING
        and alignment.get("concatenated_aligned_basis_shape") == [210, 210]
        and alignment.get("concatenated_aligned_basis_rank_mod_prime") == 210
        and alignment.get("exterior_conjugation_shape") == [210, 210]
        and alignment.get("complex_type_carrier_count") == 14
        and alignment.get("self_conjugate_real_type_carrier_count") == 11
        and all(
            alignment.get(key) is True
            for key in (
                "upstream_carrier_order_exact", "all_family_word_counts_equal_dimensions",
                "all_25_carriers_exact",
                "all_equivalent_copies_use_common_source_actions_exact",
                "exterior_conjugation_signed_permutation_exact",
                "exterior_conjugation_square_equals_identity_exact",
                "Gaussian_basis_conjugation_is_physical_exact",
                "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact",
                "all_25_conjugate_carrier_maps_exact",
                "all_25_conjugate_maps_involutive_exact",
                "conjugation_compatible_with_all_15_generators_exact",
            )
        )
        and sum(row.get("dimension", 0) for row in carriers) == 210
        and all(
            isinstance(row, dict) and set(row) == carrier_keys
            and row.get("irrep") in RANK1_SU4_BRANCHING
            and row.get("dimension") == row.get("lowering_word_count")
            == row.get("aligned_rank_mod_prime")
            and row.get("conjugate_carrier_name") in names
            and rows_by_name[row.get("conjugate_carrier_name")].get(
                "conjugate_carrier_name"
            ) == row.get("name")
            and row.get("conjugation_map_denominator", 0) > 0
            and all(value > 0 for value in row.get("source_action_denominators", []))
            and all(
                row.get(key) is True
                for key in (
                    "highest_weight_primitive_and_raising_annihilated",
                    "C8_eigen_equation_exact",
                    "all_15_common_source_actions_intertwine_exact",
                    "natural_block_support_exact",
                    "all_15_live_canonical_Phi210_actions_intertwine_exact",
                    "conjugation_involution_exact",
                    "physical_conjugation_embedding_exact",
                )
            )
            for row in carriers
        )
        and all(
            isinstance(row, dict) and set(row) == family_keys
            and row.get("irrep") in RANK1_SU4_BRANCHING
            and row.get("multiplicity") == RANK1_SU4_BRANCHING[row.get("irrep")]
            and row.get("dimension") == len(row.get("lowering_words", []))
            and row.get("common_source_action_count") == 15
            and row.get("reference_carrier_name") in names
            for row in families
        )
        and alignment.get("simple_Chevalley_system", {}).get("proof_grade") is True
        and alignment.get("simple_Chevalley_system", {}).get(
            "all_actions_integral_real"
        ) is True
        and alignment.get("simple_Chevalley_system", {}).get(
            "all_12_Serre_relations_exact"
        ) is True
        and alignment.get("exact_integer_and_rational_arithmetic_safety", {}).get(
            "proof_grade"
        ) is True
        and alignment.get("exact_integer_and_rational_arithmetic_safety", {}).get(
            "all_live_conservative_bounds_fit_int64"
        ) is True
    )


def _rank1_su4_phi210_quadratic_basis_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact 45-dimensional live invariant basis."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    constraint = report.get("constraint_system", {})
    census = report.get("real_form_completeness", {})
    basis = report.get("quadratic_basis", {})
    construction = report.get("construction_metadata", {})
    reconstruction = report.get("reconstruction_api", {})
    rows = basis.get("ordered_basis_metadata", [])
    check_keys = {
        "model_contract_and_live_companions_exact",
        "Cartan_reduced_constraint_nullity_45_exact",
        "real_form_completeness_upper_bound_45_exact",
        "explicit_real_symmetric_integral_basis_exact",
        "all_basis_matrices_live_invariant_exact",
        "lower_and_upper_dimensions_match_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus", "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used", "canonical_real_Phi210_chart_used",
        "SU4_invariant_quadratic_form_basis_constructed",
        "SU4_invariant_quadratic_form_basis_complete",
        "SU4_invariant_quadratic_form_dimension_45_exact",
    }
    false_scope = {
        "augmented_homogeneous_Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved", "arbitrary_rank1_Phi_proved",
        "G3_closed", "whole_model_validated", "whole_model_excluded",
    }
    provenance_keys = {
        "stabilizer_module", "stabilizer_module_sha256", "intertwiner_module",
        "intertwiner_module_sha256", "companion_model_contract_id",
        "stabilizer_status", "intertwiner_status",
        "stabilizer_report_equals_live_report_exact",
        "intertwiner_report_equals_live_report_exact",
        "carrier_certificate_equals_embedded_and_live_exact",
        "all_required_live_provenance_exact",
    }
    constraint_keys = {
        "proof_grade", "Cartan_generator_count", "non_Cartan_generator_count",
        "Cartan_weight_zero_symmetric_monomial_count", "reduced_constraint_shape",
        "reduced_constraint_nnz", "reduced_constraint_maximum_absolute_entry",
        "modular_prime", "reduced_constraint_rank_mod_prime", "free_column_count",
        "integer_nullspace_shape", "integer_nullspace_maximum_absolute_entry",
        "integer_nullspace_nnz", "integer_nullspace_residual_zero_exact",
        "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact",
        "exact_rational_rank", "exact_rational_nullity", "rank_nullity_argument",
        "constraint_sha256", "nullspace_sha256",
    }
    census_keys = {
        "proof_grade", "complexified_branching", "expected_complexified_branching",
        "branching_exact", "self_conjugate_real_types",
        "self_conjugate_symmetric_pairing_dimension",
        "complex_types_with_conjugates", "complex_Hermitian_real_dimension",
        "total_real_symmetric_invariant_dimension_upper_bound",
        "dimension_identity", "real_form_argument",
    }
    basis_keys = {
        "proof_grade", "matrix_count", "matrix_shape", "all_shapes_210_by_210_exact",
        "all_entries_integral_exact", "all_matrices_symmetric_exact",
        "all_matrices_primitive_exact", "all_canonical_first_entries_positive_exact",
        "all_45_commute_with_all_15_live_Phi210_generators_exact",
        "upper_triangle_column_rank_mod_prime", "modular_prime", "independence_argument",
        "minimum_nnz", "maximum_nnz", "total_nnz", "maximum_absolute_entry",
        "basis_sha256", "ordered_basis_metadata", "Gram_shape", "Gram_rank_mod_prime",
        "Gram_minimum_diagonal", "Gram_maximum_diagonal", "Gram_sha256",
        "polynomial_monomial_count", "polynomial_upper_triangle_convention",
        "integer_matrix_to_primitive_polynomial_scale_factors",
        "primitive_polynomial_rows_exact", "primitive_polynomial_basis_rank_mod_prime",
        "primitive_polynomial_basis_sha256",
    }
    construction_keys = {
        "modular_pivot_upper_triangle_coordinates",
        "modular_pivot_upper_triangle_flat_indices",
        "nonzero_real_imaginary_candidate_count", "selected_candidate_indices",
        "selected_candidate_origins",
    }
    reconstruction_keys = {
        "basis_accessor", "Gram_accessor", "exact_reconstruction_accessor",
        "integral_evaluation_accessor", "primitive_polynomial_accessor",
        "matrix_to_polynomial_accessor", "polynomial_to_matrix_accessor",
        "formula", "polynomial_convention", "rational_return_convention",
        "exact_arithmetic_contract", "ordered_basis_hash", "Gram_hash",
    }
    expected_hashes = {
        "constraint": "cddac4827dc47c663c8ca7b4ebe9ccb2338103ae5daf917c4eb615f4c3659d90",
        "nullspace": "a92c9fc421809623e50a0c7dc043d546cd866e7acaa819cffab3ae52da3998d6",
        "basis": "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694",
        "gram": "17d352a43fc0a555df3d2abbe0f59f1ceecc89498648a84703bcf0ccd9c23124",
        "polynomial": "a9d417aa7210143ad6bd69f62dce358239673b6c0c7bc545f9b65ec586002caa",
    }
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _canonical_json_sha256(report)
        == "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
        and set(report) == {
            "status", "overall_state", "model_contract_id", "n_checks",
            "n_failed", "failures", "checks", "source_provenance",
            "constraint_system", "real_form_completeness", "quadratic_basis",
            "construction_metadata", "reconstruction_api", "scope",
            "next_exact_target", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_PHI210_QUADRATIC_BASIS_CERTIFIED"
        and report.get("overall_state")
        == "SU4_INVARIANT_QUADRATIC_BASIS_CLOSED__AUGMENTED_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0 and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("companion_model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("stabilizer_status") == stabilizer_report.get("status")
        and provenance.get("intertwiner_status") == intertwiners_report.get("status")
        and provenance.get("stabilizer_module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and provenance.get("intertwiner_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("stabilizer_module_sha256")
        == _file_sha256(ROOT / provenance.get("stabilizer_module", ""))
        and provenance.get("intertwiner_module_sha256")
        == _file_sha256(ROOT / provenance.get("intertwiner_module", ""))
        and all(
            provenance.get(key) is True
            for key in (
                "stabilizer_report_equals_live_report_exact",
                "intertwiner_report_equals_live_report_exact",
                "carrier_certificate_equals_embedded_and_live_exact",
                "all_required_live_provenance_exact",
            )
        )
        and set(constraint) == constraint_keys
        and constraint.get("proof_grade") is True
        and constraint.get("Cartan_generator_count") == 3
        and constraint.get("non_Cartan_generator_count") == 12
        and constraint.get("Cartan_weight_zero_symmetric_monomial_count") == 551
        and constraint.get("reduced_constraint_shape") == [5952, 551]
        and constraint.get("reduced_constraint_rank_mod_prime") == 506
        and constraint.get("exact_rational_rank") == 506
        and constraint.get("exact_rational_nullity") == 45
        and constraint.get("free_column_count") == 45
        and constraint.get("integer_nullspace_shape") == [551, 45]
        and constraint.get("integer_nullspace_residual_zero_exact") is True
        and constraint.get(
            "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact"
        ) is True
        and constraint.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and constraint.get("constraint_sha256") == expected_hashes["constraint"]
        and constraint.get("nullspace_sha256") == expected_hashes["nullspace"]
        and set(census) == census_keys
        and census.get("proof_grade") is True
        and census.get("branching_exact") is True
        and census.get("complexified_branching") == RANK1_SU4_BRANCHING
        and census.get("expected_complexified_branching") == RANK1_SU4_BRANCHING
        and census.get("self_conjugate_symmetric_pairing_dimension") == 24
        and census.get("complex_Hermitian_real_dimension") == 21
        and census.get("total_real_symmetric_invariant_dimension_upper_bound") == 45
        and census.get("self_conjugate_real_types") == {
            "1": {"multiplicity": 4, "symmetric_pairings": 10},
            "6": {"multiplicity": 4, "symmetric_pairings": 10},
            "15": {"multiplicity": 2, "symmetric_pairings": 3},
            "20prime": {"multiplicity": 1, "symmetric_pairings": 1},
        }
        and census.get("complex_types_with_conjugates") == {
            "4/4bar": {"multiplicity": 4, "Hermitian_real_dimension": 16},
            "10/10bar": {"multiplicity": 1, "Hermitian_real_dimension": 1},
            "20/20bar": {"multiplicity": 2, "Hermitian_real_dimension": 4},
        }
        and set(basis) == basis_keys
        and basis.get("proof_grade") is True
        and basis.get("matrix_count") == len(rows) == 45
        and basis.get("matrix_shape") == [210, 210]
        and basis.get("all_shapes_210_by_210_exact") is True
        and basis.get("all_entries_integral_exact") is True
        and basis.get("all_matrices_symmetric_exact") is True
        and basis.get("all_matrices_primitive_exact") is True
        and basis.get(
            "all_45_commute_with_all_15_live_Phi210_generators_exact"
        ) is True
        and basis.get("upper_triangle_column_rank_mod_prime") == 45
        and basis.get("Gram_shape") == [45, 45]
        and basis.get("Gram_rank_mod_prime") == 45
        and basis.get("primitive_polynomial_basis_rank_mod_prime") == 45
        and basis.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and basis.get("basis_sha256") == expected_hashes["basis"]
        and basis.get("Gram_sha256") == expected_hashes["gram"]
        and basis.get("primitive_polynomial_basis_sha256")
        == expected_hashes["polynomial"]
        and all(
            isinstance(row, dict)
            and set(row) == {
                "basis_index", "nnz", "maximum_absolute_entry",
                "Frobenius_norm_squared", "matrix_sha256",
            }
            and row.get("basis_index") == index
            and isinstance(row.get("matrix_sha256"), str)
            and len(row.get("matrix_sha256")) == 64
            for index, row in enumerate(rows)
        )
        and set(construction) == construction_keys
        and construction.get("nonzero_real_imaginary_candidate_count") == 73
        and len(construction.get("selected_candidate_indices", [])) == 45
        and len(construction.get("selected_candidate_origins", [])) == 45
        and len(construction.get("modular_pivot_upper_triangle_coordinates", [])) == 45
        and len(construction.get("modular_pivot_upper_triangle_flat_indices", [])) == 45
        and set(reconstruction) == reconstruction_keys
        and reconstruction.get("ordered_basis_hash") == expected_hashes["basis"]
        and reconstruction.get("Gram_hash") == expected_hashes["gram"]
        and reconstruction.get("formula") == "Q(c)=sum_{a=0}^{44} c_a Q_a"
        and set(reconstruction.get("exact_arithmetic_contract", {})) == {
            "integral_evaluation", "rational_reconstruction",
            "polynomial_encoding", "live_basis_maximum_absolute_entry",
        }
        and reconstruction.get("exact_arithmetic_contract", {}).get(
            "live_basis_maximum_absolute_entry"
        ) == 8
    )


def _rank1_su4_augmented_sos_census_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
    quadratic_report: dict[str, Any],
) -> bool:
    """Fail closed on the abstract augmented-SOS census, not on a PSD claim."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    representation = report.get("augmented_representation", {})
    target = report.get("invariant_quartic_target", {})
    universal = report.get("universal_multiplication_and_section", {})
    coefficient_map = report.get("abstract_coefficient_map_census", {})
    cubic = coefficient_map.get("cubic_cross_sector", {})
    public_apis = report.get("public_exact_APIs", {})
    check_keys = {
        "Frobenius_Schur_indicators_computed_and_real_types_exact",
        "Schur_parameter_19594_grade_census_exact",
        "abstract_invariant_map_ranks_and_kernels_exact",
        "augmented_dimension_35_isotypic_types_and_824_copies_exact",
        "coordinate_map_absence_declared_fail_closed",
        "cubic_abstract_zero_interface_reserved_without_physical_claim",
        "frozen_aligned_carrier_and_quadratic_basis_APIs_exact",
        "invariant_target_6585_grade_census_exact",
        "live_Phi210_character_and_exact_branching_certified",
        "nine_real_and_thirteen_complex_isotypic_blocks_exact",
        "real_symmetric_and_complex_Hermitian_conventions_complete",
        "universal_GL211_equivariant_section_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "augmented_homogeneous_representation_census_constructed",
        "all_22_real_Hermitian_Schur_block_sizes_certified",
        "abstract_invariant_grade_ranks_certified",
        "quadratic_target_invariant_basis_dimension_45_bound_live",
        "universal_GL211_multiplication_and_rational_section_constructed",
    }
    false_scope = {
        "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed",
        "ordered_invariant_cubic_basis_constructed",
        "ordered_invariant_quartic_basis_constructed",
        "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
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
    }
    provenance_keys = {
        "aligned_module", "aligned_report_sha256", "aligned_source_sha256",
        "alignment_certificate_sha256", "all_required_frozen_API_provenance_exact",
        "expected_aligned_report_sha256", "expected_aligned_source_sha256",
        "expected_alignment_certificate_sha256", "expected_quadratic_basis_sha256",
        "expected_quadratic_report_sha256", "expected_quadratic_source_sha256",
        "model_contract_id", "proof_grade", "quadratic_basis_matrix_count",
        "quadratic_basis_sha256", "quadratic_module", "quadratic_report_sha256",
        "quadratic_source_sha256",
    }
    representation_keys = {
        "Frobenius_Schur_classification_computed_exact", "Phi210_branching",
        "Phi210_branching_expected_exact", "Phi210_character_sha256",
        "Phi210_weight_character_dimension", "Phi210_weight_count",
        "Schur_real_parameter_count", "Schur_real_parameter_grade_counts",
        "Sym2Phi_character_sha256", "Sym2Phi_dimension",
        "all_Gelfand_Tsetlin_character_dimensions_match_Weyl_exact",
        "augmented_character_sha256", "augmented_homogeneous_dimension",
        "complex_Hermitian_block_count", "complex_irreducible_copy_count",
        "complex_irreducible_copy_grade_counts_t2_tPhi_Phi2", "complex_irrep_rows",
        "complex_isotypic_type_count", "expected_augmented_multiplicities_exact",
        "proof_grade", "real_isotypic_block_count", "real_isotypic_blocks",
        "real_symmetric_block_count", "represented_real_dimension",
    }
    target_keys = {
        "Weyl_group_order", "expected_symmetric_power_dimensions",
        "invariant_equation_count", "invariant_equation_grade_counts",
        "proof_grade", "symmetric_power_character_sha256",
        "symmetric_power_dimensions", "target_sector",
        "trivial_multiplicity_extraction",
    }
    universal_keys = {
        "all_representative_identities_exact",
        "equality_and_grade_pattern_representative_count",
        "invariant_restriction_surjective_exact", "invariant_surjectivity_argument",
        "linear_dimension", "linear_space",
        "multiplication_after_section_is_identity_exact", "multiplication_formula",
        "proof_grade", "quadratic_monomial_dimension", "quadratic_monomial_space",
        "raw_domain_grade_dimensions", "raw_grade_kernel_dimensions",
        "raw_grade_ranks_exact", "raw_quartic_polynomial_dimension",
        "raw_symmetric_Gram_dimension", "raw_target_grade_dimensions",
        "section_formula", "section_is_GL211_equivariant_by_naturality_exact",
        "section_preserves_Phi_degree_exact",
    }
    coefficient_map_keys = {
        "Schur_coordinate_matrix_constructed",
        "Schur_coordinate_matrix_shape_when_constructed",
        "abstract_grade_kernel_dimensions_exact", "abstract_grade_ranks_exact",
        "abstract_total_kernel_dimension_exact", "abstract_total_rank_exact",
        "cubic_cross_sector", "domain_real_parameter_grade_counts", "map",
        "missing_coordinate_data", "proof_grade",
        "surjectivity_is_abstract_not_a_coordinate_matrix",
        "target_invariant_row_grade_counts",
    }
    cubic_keys = {
        "abstract_interface_RHS", "abstract_zero_RHS_interface_contract_reserved",
        "abstract_zero_RHS_row_count_reserved",
        "all_1414_cross_variables_present_in_census_exact",
        "all_478_cubic_target_rows_reserved_exact", "block_rows",
        "invariant_target_row_count", "nonzero_block_row_count",
        "physical_G3_gap_cubic_zero_RHS_certified",
        "physical_G3_gap_target_vector_constructed", "real_Schur_variable_count",
        "source", "zero_RHS_is_interface_contract_not_a_physical_vector_certificate",
    }
    public_api_keys = {
        "Frobenius_Schur_indicator", "Phi_character", "Schur_grade_counts",
        "augmented_character", "character_decompositions", "polarized_Gram_section",
        "polarized_tensor_section", "raw_Gram_entry_map", "real_isotypic_blocks",
        "symmetric_power_character", "target_grade_counts",
    }
    expected_aligned_report = (
        "d2da0572dc33a1f3f88b5ac5df3343201650ca660498f34ff59806a607015c67"
    )
    expected_aligned_source = (
        "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
    )
    expected_alignment = (
        "f74b7845b57472f62773c398fa927b551b5d9d09f86bd7defb92a6ed71adbe15"
    )
    expected_quadratic_report = (
        "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
    )
    expected_quadratic_source = (
        "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
    )
    expected_quadratic_basis = (
        "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
    )
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _rank1_su4_phi210_quadratic_basis_exact(
            quadratic_report, stabilizer_report, intertwiners_report,
            aligned_report,
        )
        and _file_sha256(
            ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        ) == "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
        and _canonical_json_sha256(report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and set(report) == {
            "abstract_coefficient_map_census", "augmented_representation",
            "blocking_gap", "checks", "failures", "invariant_quartic_target",
            "model_contract_id", "n_checks", "n_failed", "next_exact_target",
            "overall_state", "public_exact_APIs", "scope", "source_provenance",
            "status", "universal_multiplication_and_section", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("proof_grade") is True
        and provenance.get("all_required_frozen_API_provenance_exact") is True
        and provenance.get("aligned_module")
        == "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
        and provenance.get("quadratic_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
        and provenance.get("aligned_report_sha256")
        == provenance.get("expected_aligned_report_sha256")
        == _canonical_json_sha256(aligned_report)
        == expected_aligned_report
        and provenance.get("aligned_source_sha256")
        == provenance.get("expected_aligned_source_sha256")
        == _file_sha256(ROOT / provenance.get("aligned_module", ""))
        == expected_aligned_source
        and provenance.get("alignment_certificate_sha256")
        == provenance.get("expected_alignment_certificate_sha256")
        == _canonical_json_sha256(aligned_report.get("alignment", {}))
        == expected_alignment
        and provenance.get("quadratic_report_sha256")
        == provenance.get("expected_quadratic_report_sha256")
        == _canonical_json_sha256(quadratic_report)
        == expected_quadratic_report
        and provenance.get("quadratic_source_sha256")
        == provenance.get("expected_quadratic_source_sha256")
        == _file_sha256(ROOT / provenance.get("quadratic_module", ""))
        == expected_quadratic_source
        and provenance.get("quadratic_basis_sha256")
        == provenance.get("expected_quadratic_basis_sha256")
        == quadratic_report.get("quadratic_basis", {}).get("basis_sha256")
        == expected_quadratic_basis
        and provenance.get("quadratic_basis_matrix_count") == 45
        and set(representation) == representation_keys
        and representation.get("proof_grade") is True
        and representation.get("Phi210_weight_character_dimension") == 210
        and representation.get("Sym2Phi_dimension") == 22_155
        and representation.get("augmented_homogeneous_dimension") == 22_366
        and representation.get("represented_real_dimension") == 22_366
        and representation.get("complex_isotypic_type_count") == 35
        and representation.get("complex_irreducible_copy_count") == 824
        and representation.get("complex_irreducible_copy_grade_counts_t2_tPhi_Phi2")
        == [1, 25, 798]
        and representation.get("real_isotypic_block_count") == 22
        and representation.get("real_symmetric_block_count") == 9
        and representation.get("complex_Hermitian_block_count") == 13
        and representation.get("Schur_real_parameter_count") == 19_594
        and representation.get("Schur_real_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and len(representation.get("complex_irrep_rows", [])) == 35
        and len(representation.get("real_isotypic_blocks", [])) == 22
        and all(
            isinstance(row, dict)
            and set(row) == {
                "complex_dimension", "dynkin", "multiplicity_Phi",
                "multiplicity_Sym2Phi", "multiplicity_augmented",
            }
            for row in representation.get("complex_irrep_rows", [])
        )
        and all(
            isinstance(row, dict)
            and set(row) == {
                "Frobenius_Schur_indicator", "Frobenius_Schur_type",
                "Frobenius_Schur_type_argument", "PSD_cone", "conjugate_dynkin",
                "coordinate_convention",
                "cubic_tPhi_to_Phi2_cross_real_parameter_count",
                "graded_multiplicities_t2_tPhi_Phi2", "irrep_complex_dimension",
                "multiplicity_matrix_order", "real_Schur_parameter_count",
                "real_block_kind", "real_parameter_grade_counts",
                "representative_dynkin", "represented_real_dimension",
                "self_conjugate", "young_diagram_box_count",
            }
            for row in representation.get("real_isotypic_blocks", [])
        )
        and set(target) == target_keys
        and target.get("proof_grade") is True
        and target.get("invariant_equation_count") == 6_585
        and target.get("invariant_equation_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and target.get("symmetric_power_dimensions")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and target.get("expected_symmetric_power_dimensions")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and set(universal) == universal_keys
        and universal.get("proof_grade") is True
        and universal.get("linear_dimension") == 211
        and universal.get("quadratic_monomial_dimension") == 22_366
        and universal.get("raw_symmetric_Gram_dimension") == 250_130_161
        and universal.get("raw_quartic_polynomial_dimension") == 84_957_251
        and universal.get("multiplication_after_section_is_identity_exact") is True
        and universal.get("section_is_GL211_equivariant_by_naturality_exact") is True
        and universal.get("section_preserves_Phi_degree_exact") is True
        and universal.get("invariant_restriction_surjective_exact") is True
        and universal.get("raw_grade_ranks_exact")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and set(coefficient_map) == coefficient_map_keys
        and coefficient_map.get("proof_grade") is True
        and coefficient_map.get("domain_real_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and coefficient_map.get("target_invariant_row_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and coefficient_map.get("abstract_grade_ranks_exact")
        == [1, 4, 45, 478, 6_057]
        and coefficient_map.get("abstract_grade_kernel_dimensions_exact")
        == [0, 0, 45, 936, 12_028]
        and coefficient_map.get("abstract_total_rank_exact") == 6_585
        and coefficient_map.get("abstract_total_kernel_dimension_exact") == 13_009
        and coefficient_map.get("Schur_coordinate_matrix_constructed") is False
        and coefficient_map.get("Schur_coordinate_matrix_shape_when_constructed")
        == [6_585, 19_594]
        and coefficient_map.get("surjectivity_is_abstract_not_a_coordinate_matrix")
        is True
        and set(cubic) == cubic_keys
        and cubic.get("real_Schur_variable_count") == 1_414
        and cubic.get("invariant_target_row_count") == 478
        and cubic.get("nonzero_block_row_count") == 7
        and len(cubic.get("block_rows", [])) == 7
        and cubic.get("abstract_interface_RHS") == "zero"
        and cubic.get("abstract_zero_RHS_row_count_reserved") == 478
        and cubic.get("abstract_zero_RHS_interface_contract_reserved") is True
        and cubic.get("all_1414_cross_variables_present_in_census_exact") is True
        and cubic.get("all_478_cubic_target_rows_reserved_exact") is True
        and cubic.get("zero_RHS_is_interface_contract_not_a_physical_vector_certificate")
        is True
        and cubic.get("physical_G3_gap_target_vector_constructed") is False
        and cubic.get("physical_G3_gap_cubic_zero_RHS_certified") is False
        and all(
            isinstance(row, dict)
            and set(row) == {
                "Phi2_multiplicity", "real_block_kind",
                "real_cross_parameter_count", "representative_dynkin",
                "tPhi_multiplicity",
            }
            for row in cubic.get("block_rows", [])
        )
        and set(public_apis) == public_api_keys
    )


def _rank1_su4_augmented_sos_cubic_map_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
    quadratic_report: dict[str, Any],
    census_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact cubic Schur map, never on a physical RHS."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    targets = report.get("Sym2_target_carriers", {})
    pairings = report.get("contragredient_pairings", {})
    domain = report.get("physical_cubic_domain", {})
    cubic_map = report.get("cubic_coordinate_map", {})
    arithmetic = report.get("exact_arithmetic_safety", {})
    public_apis = report.get("public_exact_APIs", {})
    target_families = targets.get("families", [])
    pairing_families = pairings.get("families", [])
    block_rows = domain.get("all_22_augmented_block_rows", [])

    check_keys = {
        "abstract_478_coordinate_zero_placeholder_exact_and_nonphysical",
        "all_1414_complexified_cross_tensors_constructed_exact",
        "all_22_real_Hermitian_block_rows_and_1414_variables_exact",
        "all_required_Sym2_highest_weight_carriers_exact",
        "all_target_carriers_use_frozen_common_words_and_actions_exact",
        "all_ten_contragredient_pairings_exact",
        "exact_rank_478_and_kernel_936_certified",
        "explicit_integer_478_by_1414_coordinate_map_exact",
        "frozen_census_aligned_quadratic_and_intertwiner_provenance_exact",
        "full_SDP_and_G3_absence_declared_fail_closed",
        "integer_rational_and_modular_arithmetic_safety_exact",
        "physical_realification_rank_1414_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed",
        "explicit_478_by_1414_cubic_coordinate_map_constructed",
        "cubic_map_rank_478_and_kernel_dimension_936_exact",
        "abstract_478_coordinate_zero_placeholder_available",
    }
    false_scope = {
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
    }
    provenance_keys = {
        "aligned_module", "aligned_n_failed", "aligned_source_sha256",
        "aligned_status", "all_required_frozen_provenance_exact",
        "census_module", "census_n_failed",
        "census_physical_G3_gap_cubic_zero_RHS_certified",
        "census_physical_G3_gap_target_vector_constructed",
        "census_report_sha256", "census_source_sha256", "census_status",
        "expected_aligned_source_sha256", "expected_census_report_sha256",
        "expected_census_source_sha256", "expected_intertwiner_source_sha256",
        "expected_quadratic_basis_sha256", "expected_quadratic_report_sha256",
        "expected_quadratic_source_sha256", "intertwiner_module",
        "intertwiner_source_sha256", "live_Schur_parameter_grade_counts",
        "live_target_invariant_grade_counts", "model_contract_id", "proof_grade",
        "quadratic_basis_sha256", "quadratic_module",
        "quadratic_report_sha256", "quadratic_source_sha256",
    }
    target_keys = {
        "all_common_lowering_word_carriers_have_full_rank_exact",
        "all_copies_aligned_by_exact_highest_weight_universality",
        "all_highest_vectors_raise_to_zero_exact",
        "all_highest_weight_nullities_match_character_census_exact",
        "all_reference_copies_intertwine_9_Chevalley_actions_exact",
        "families", "irrep_family_count", "proof_grade", "representation",
        "total_complex_carrier_copy_count", "total_isotypic_dimension",
    }
    target_family_keys = {
        "checked_Chevalley_action_count", "concatenated_nnz",
        "concatenated_rank_by_highest_weight_evaluation_exact",
        "concatenated_sha256", "concatenated_shape", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "copy_count", "dimension",
        "every_copy_alignment_follows_from_highest_weight_universality_exact",
        "every_copy_full_rank_mod_prime", "free_columns",
        "highest_vectors_maximum_absolute_entry", "highest_vectors_nnz",
        "highest_vectors_sha256", "highest_weight",
        "highest_weight_evaluation_rank_argument", "individual_copy_ranks_mod_prime",
        "irrep", "lowering_word_count", "maximum_absolute_entry",
        "maximum_rational_reconstruction_denominator", "modular_rank", "nullity",
        "proof_grade", "raising_residual_zero_exact", "rank_nullity_argument",
        "reference_copy_all_9_Chevalley_actions_intertwine_exact",
        "source_Chevalley_imaginary_residuals_zero_exact",
        "source_weight_space_dimension",
    }
    pairing_keys = {
        "all_15_compact_tensor_equations_exact",
        "all_pairing_spaces_one_dimensional_exact", "families",
        "pairing_family_count", "proof_grade",
    }
    pairing_family_keys = {
        "all_15_compact_tensor_invariance_equations_exact", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "dimension", "exact_nullity",
        "matrix_maximum_absolute_entry", "matrix_nnz", "matrix_sha256",
        "maximum_rational_reconstruction_denominator", "modular_rank",
        "proof_grade", "rank_nullity_argument", "source_irrep",
        "target_contragredient_irrep", "weight_zero_variable_count",
    }
    domain_keys = {
        "Gram_symmetric_off_diagonal_multiplier", "all_22_augmented_block_rows",
        "all_22_block_provenance_rows_exact",
        "all_multiplications_commute_with_physical_conjugation_exact",
        "all_selected_vectors_satisfy_physical_real_structure_exact",
        "complexified_domain_basis_count", "complexified_raw_image_total_nnz",
        "complexified_raw_tensor_total_nnz", "domain_basis_metadata_sha256",
        "domain_modular_elimination_fill", "domain_modular_pivot_count",
        "expected_complexified_counts_by_irrep", "nonzero_cubic_block_count",
        "observed_complexified_counts_by_irrep", "physical_basis_count",
        "physical_candidate_count", "physical_component_counts",
        "physical_real_block_counts", "proof_grade",
    }
    block_row_keys = {
        "Phi2_multiplicity", "all_variables_constructed_exact",
        "constructed_physical_basis_variable_count",
        "expected_cubic_cross_real_parameter_count", "real_block_kind",
        "representative_dynkin", "tPhi_multiplicity",
    }
    map_keys = {
        "Gram_convention", "abstract_zero_interface_placeholder_dtype",
        "abstract_zero_interface_placeholder_nnz",
        "abstract_zero_interface_placeholder_shape",
        "abstract_zero_placeholder_is_not_a_physical_G3_target",
        "all_478_abstract_interface_placeholder_entries_zero_exact",
        "coordinate_map_maximum_absolute_entry", "coordinate_map_nnz",
        "coordinate_map_sha256", "coordinate_map_shape", "exact_kernel_dimension",
        "exact_rank", "full_physical_image_maximum_absolute_entry",
        "full_physical_image_nnz", "full_physical_image_sha256",
        "full_physical_image_shape", "independent_domain_column_indices",
        "modular_prime", "physical_G3_gap_cubic_zero_RHS_certified",
        "physical_G3_gap_target_vector_constructed", "proof_grade",
        "rank_argument", "rank_mod_prime",
        "selected_minor_determinant_nonzero_mod_prime",
        "selected_minor_rank_mod_prime", "selected_minor_sha256",
        "source_coordinate_space", "target_coordinate_metadata_sha256",
        "target_coordinate_space", "target_imaginary_coordinate_count",
        "target_pivot_row_count", "target_real_coordinate_count",
    }
    arithmetic_keys = {
        "Fraction_based_constraint_denominator_clearing_exact",
        "Python_integer_sparse_aggregation_exact",
        "all_recorded_bounds_fit_signed_int64",
        "checked_sparse_products_reject_unsafe_int64_bounds",
        "conservative_live_product_absolute_bound", "maximum_live_absolute_entry",
        "modular_rational_reconstruction_verified_over_Z_exact",
        "modular_row_update_absolute_bound", "proof_grade",
        "signed_int64_maximum", "storage_dtype",
    }
    public_api_keys = {
        "abstract_zero_interface_placeholder", "coordinate_map",
        "domain_metadata", "map_convention", "target_metadata",
    }
    expected_counts = {
        "1": 180, "4": 240, "4bar": 240, "6": 248, "10": 39,
        "10bar": 39, "20": 124, "20bar": 124, "20prime": 42, "15": 138,
    }
    expected_real_blocks = {
        "(0, 0, 0)": 180, "(0, 0, 1)": 480, "(0, 0, 2)": 78,
        "(0, 1, 0)": 248, "(0, 1, 1)": 248, "(0, 2, 0)": 42,
        "(1, 0, 1)": 138,
    }
    expected_census_source = (
        "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
    )
    expected_census_report = (
        "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
    )
    expected_aligned_source = (
        "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
    )
    expected_intertwiner_source = (
        "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49"
    )
    expected_quadratic_source = (
        "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
    )
    expected_quadratic_report = (
        "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
    )
    expected_quadratic_basis = (
        "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
    )
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _rank1_su4_phi210_quadratic_basis_exact(
            quadratic_report, stabilizer_report, intertwiners_report,
            aligned_report,
        )
        and _rank1_su4_augmented_sos_census_exact(
            census_report, stabilizer_report, intertwiners_report,
            aligned_report, quadratic_report,
        )
        and _file_sha256(
            ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
        ) == "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
        and _canonical_json_sha256(report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and set(report) == {
            "Sym2_target_carriers", "checks", "contragredient_pairings",
            "cubic_coordinate_map", "exact_arithmetic_safety", "failures",
            "model_contract_id", "n_checks", "n_failed", "next_exact_target",
            "overall_state", "physical_cubic_domain", "public_exact_APIs",
            "scope", "source_provenance", "status", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_CUBIC_MAP_CLOSED__FULL_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("proof_grade") is True
        and provenance.get("all_required_frozen_provenance_exact") is True
        and provenance.get("census_module")
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        and provenance.get("census_source_sha256")
        == provenance.get("expected_census_source_sha256")
        == _file_sha256(ROOT / provenance.get("census_module", ""))
        == expected_census_source
        and provenance.get("census_report_sha256")
        == provenance.get("expected_census_report_sha256")
        == _canonical_json_sha256(census_report)
        == expected_census_report
        and provenance.get("census_status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and provenance.get("census_n_failed") == 0
        and provenance.get("census_physical_G3_gap_target_vector_constructed")
        is False
        and provenance.get("census_physical_G3_gap_cubic_zero_RHS_certified")
        is False
        and provenance.get("aligned_module")
        == "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
        and provenance.get("aligned_source_sha256")
        == provenance.get("expected_aligned_source_sha256")
        == _file_sha256(ROOT / provenance.get("aligned_module", ""))
        == expected_aligned_source
        and provenance.get("aligned_status")
        == "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
        and provenance.get("aligned_n_failed") == 0
        and provenance.get("intertwiner_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("intertwiner_source_sha256")
        == provenance.get("expected_intertwiner_source_sha256")
        == _file_sha256(ROOT / provenance.get("intertwiner_module", ""))
        == expected_intertwiner_source
        and provenance.get("quadratic_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
        and provenance.get("quadratic_source_sha256")
        == provenance.get("expected_quadratic_source_sha256")
        == _file_sha256(ROOT / provenance.get("quadratic_module", ""))
        == expected_quadratic_source
        and provenance.get("quadratic_report_sha256")
        == provenance.get("expected_quadratic_report_sha256")
        == _canonical_json_sha256(quadratic_report)
        == expected_quadratic_report
        and provenance.get("quadratic_basis_sha256")
        == provenance.get("expected_quadratic_basis_sha256")
        == quadratic_report.get("quadratic_basis", {}).get("basis_sha256")
        == expected_quadratic_basis
        and provenance.get("live_Schur_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and provenance.get("live_target_invariant_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and set(targets) == target_keys
        and targets.get("proof_grade") is True
        and targets.get("irrep_family_count") == 10
        and targets.get("total_complex_carrier_copy_count") == 540
        and targets.get("total_isotypic_dimension") == 6_032
        and len(target_families) == 10
        and {row.get("irrep") for row in target_families}
        == {"1", "4", "4bar", "6", "10", "10bar", "20", "20bar", "20prime", "15"}
        and all(
            isinstance(row, dict)
            and set(row) == target_family_keys
            and row.get("proof_grade") is True
            for row in target_families
        )
        and all(
            targets.get(key) is True
            for key in (
                "all_common_lowering_word_carriers_have_full_rank_exact",
                "all_copies_aligned_by_exact_highest_weight_universality",
                "all_highest_vectors_raise_to_zero_exact",
                "all_highest_weight_nullities_match_character_census_exact",
                "all_reference_copies_intertwine_9_Chevalley_actions_exact",
            )
        )
        and set(pairings) == pairing_keys
        and pairings.get("proof_grade") is True
        and pairings.get("pairing_family_count") == 10
        and pairings.get("all_pairing_spaces_one_dimensional_exact") is True
        and pairings.get("all_15_compact_tensor_equations_exact") is True
        and len(pairing_families) == 10
        and all(
            isinstance(row, dict)
            and set(row) == pairing_family_keys
            and row.get("exact_nullity") == 1
            and row.get("all_15_compact_tensor_invariance_equations_exact") is True
            and row.get("proof_grade") is True
            for row in pairing_families
        )
        and set(domain) == domain_keys
        and domain.get("proof_grade") is True
        and domain.get("complexified_domain_basis_count") == 1_414
        and domain.get("physical_candidate_count") == 2_754
        and domain.get("physical_basis_count") == 1_414
        and domain.get("domain_modular_pivot_count") == 1_414
        and domain.get("expected_complexified_counts_by_irrep") == expected_counts
        and domain.get("observed_complexified_counts_by_irrep") == expected_counts
        and domain.get("physical_component_counts")
        == {"imaginary_minus": 667, "real_plus": 747}
        and domain.get("physical_real_block_counts") == expected_real_blocks
        and domain.get("all_multiplications_commute_with_physical_conjugation_exact")
        is True
        and domain.get("all_selected_vectors_satisfy_physical_real_structure_exact")
        is True
        and domain.get("all_22_block_provenance_rows_exact") is True
        and domain.get("nonzero_cubic_block_count") == 7
        and domain.get("Gram_symmetric_off_diagonal_multiplier") == 2
        and domain.get("domain_basis_metadata_sha256")
        == "765a0f92ef26b1e8335e212595389ddc73e4a54274fd2b3450f04b9bd56383a5"
        and len(block_rows) == 22
        and all(
            isinstance(row, dict)
            and set(row) == block_row_keys
            and row.get("all_variables_constructed_exact") is True
            for row in block_rows
        )
        and sum(
            int(row.get("constructed_physical_basis_variable_count", 0))
            for row in block_rows
        ) == 1_414
        and set(cubic_map) == map_keys
        and cubic_map.get("proof_grade") is True
        and cubic_map.get("full_physical_image_shape") == [43_820, 1_414]
        and cubic_map.get("full_physical_image_nnz") == 287_472
        and cubic_map.get("full_physical_image_maximum_absolute_entry") == 32
        and cubic_map.get("full_physical_image_sha256")
        == "f2b09f7a6596469b25e1f8c0dc2eb109029f99ac9b774f8deaf335432161e0fb"
        and cubic_map.get("coordinate_map_shape") == [478, 1_414]
        and cubic_map.get("coordinate_map_nnz") == 3_145
        and cubic_map.get("coordinate_map_maximum_absolute_entry") == 32
        and cubic_map.get("coordinate_map_sha256")
        == "77035bb3e5960879c54da3673670eb024b4ed0c0e60752fcc26973eee023941a"
        and cubic_map.get("modular_prime") == 1_000_003
        and cubic_map.get("rank_mod_prime") == 478
        and cubic_map.get("selected_minor_rank_mod_prime") == 478
        and cubic_map.get("selected_minor_determinant_nonzero_mod_prime") is True
        and cubic_map.get("selected_minor_sha256")
        == "6a27a6bb10d4c486e2ae6b0232bd871be088ede4f64daa706c0df66da0a9017f"
        and cubic_map.get("exact_rank") == 478
        and cubic_map.get("exact_kernel_dimension") == 936
        and len(cubic_map.get("independent_domain_column_indices", [])) == 478
        and len(set(cubic_map.get("independent_domain_column_indices", []))) == 478
        and cubic_map.get("target_pivot_row_count") == 478
        and cubic_map.get("target_real_coordinate_count") == 272
        and cubic_map.get("target_imaginary_coordinate_count") == 206
        and cubic_map.get("target_coordinate_metadata_sha256")
        == "fb3f4a2c9fde59b087cc1d95c4f08685ac51b720df354ff0cc2090c37536a482"
        and cubic_map.get("abstract_zero_interface_placeholder_shape") == [478]
        and cubic_map.get("abstract_zero_interface_placeholder_dtype") == "int64"
        and cubic_map.get("abstract_zero_interface_placeholder_nnz") == 0
        and cubic_map.get("all_478_abstract_interface_placeholder_entries_zero_exact")
        is True
        and cubic_map.get("abstract_zero_placeholder_is_not_a_physical_G3_target")
        is True
        and cubic_map.get("physical_G3_gap_target_vector_constructed") is False
        and cubic_map.get("physical_G3_gap_cubic_zero_RHS_certified") is False
        and set(arithmetic) == arithmetic_keys
        and arithmetic.get("proof_grade") is True
        and arithmetic.get("all_recorded_bounds_fit_signed_int64") is True
        and arithmetic.get("checked_sparse_products_reject_unsafe_int64_bounds")
        is True
        and arithmetic.get("conservative_live_product_absolute_bound")
        == 22_686_720
        and arithmetic.get("modular_row_update_absolute_bound")
        == 1_000_005_000_006
        and arithmetic.get("signed_int64_maximum") == 9_223_372_036_854_775_807
        and set(public_apis) == public_api_keys
        and public_apis.get("coordinate_map") == "exact_cubic_coordinate_map()"
        and public_apis.get("abstract_zero_interface_placeholder")
        == "abstract_zero_cubic_interface_placeholder()"
        and public_apis.get("domain_metadata") == "cubic_domain_basis_metadata()"
        and public_apis.get("target_metadata") == "cubic_target_coordinate_metadata()"
    )


def _rank1_su4_augmented_sos_quartic_map_exact(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact quartic Schur map, never on PSD or G3."""
    scope = report.get("scope", {})
    dimensions = report.get("dimensions", {})
    provenance = report.get("provenance", {})
    carriers = report.get("carrier_certificate", {})
    pairings = report.get("pairing_certificate", {})
    realification = report.get("realification_certificate", {})
    invariance = report.get("representative_invariance_certificate", {})
    coefficient_map = report.get("coefficient_map_certificate", {})
    cache_contract = report.get("cache_and_mutation_contract", {})
    arithmetic = report.get("arithmetic_contract", {})

    true_scope = {
        "homogeneous_quartic_Schur_coefficient_map_constructed_exact",
        "all_35_complex_carrier_families_constructed_exact",
        "all_22_real_block_pairings_constructed_exact",
    }
    false_scope = {
        "physical_quartic_target_constructed",
        "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
        "semidefinite_feasibility_solved",
        "arbitrary_Phi_stationarity_or_lower_bound_proved",
        "G3_closed",
    }
    carrier_row_keys = {
        "alternate_prime_nullity", "alternate_prime_rank",
        "concatenated_maximum_absolute_entry", "concatenated_nnz",
        "concatenated_sha256", "concatenated_shape", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "copy_count", "dimension",
        "highest_weight", "maximum_rational_reconstruction_denominator",
        "nullity", "raising_residual_zero_exact",
    }
    pairing_row_keys = {
        "component_metric_sha256", "conjugate_dynkin", "copy_count",
        "dimension", "pairing_maximum_absolute_entry", "pairing_nnz",
        "pairing_sha256", "positive_inverse_metric_normalization_exact",
        "rational_inverse_denominator", "real_block_kind",
        "representative_dynkin", "self_conjugate",
    }
    realification_row_keys = {
        "PSD_cone", "block_index", "conjugate_dynkin",
        "first_domain_ordinal", "multiplicity", "past_last_domain_ordinal",
        "physical_component_counts", "quartic_parameter_count",
        "real_block_kind", "real_type_fixed_basis_recipe_sha256",
        "representative_dynkin", "self_conjugate",
    }
    invariance_row_keys = {
        "all_9_Chevalley_tensor_residuals_zero_exact",
        "representative_diagonal_image_physically_real_exact",
        "representative_dynkin", "symmetric_tensor_nnz",
        "symmetric_tensor_sha256",
    }
    map_keys = {
        "coordinate_map_CSR", "coordinate_map_block_nnz",
        "coordinate_map_sha256", "density",
        "estimated_dense_int32_bytes_avoided",
        "estimated_dense_int64_bytes_avoided", "first_modular_prime",
        "first_pass_image_count_until_full_rank",
        "first_prime_elimination_fill", "first_prime_maximum_basis_vector_nnz",
        "first_prime_rank", "full_image_stream_sha256",
        "full_stream_image_count", "kernel_dimension_over_Q_exact",
        "maximum_full_image_absolute_coefficient", "maximum_full_image_nnz",
        "nnz", "physical_component_counts",
        "pivot_physical_quartic_coordinates",
        "pivot_physical_quartic_coordinates_sha256", "proof_grade",
        "rank_argument", "rank_over_Q_exact", "second_modular_prime",
        "second_prime_elimination_fill",
        "second_prime_maximum_basis_vector_nnz",
        "second_prime_selected_minor_rank", "selected_domain_columns",
        "selected_domain_columns_sha256", "shape",
    }
    csr = coefficient_map.get("coordinate_map_CSR", {})
    census_source = provenance.get("census_source", "")
    cubic_source = provenance.get("cubic_source", "")
    return bool(
        _file_sha256(
            ROOT
            / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
        ) == "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1"
        and _canonical_json_sha256(report)
        == "ac48f6e6183a5b51ced47fcb8f4a1a9218df9bcf0951b632d8644f2a3d850f68"
        and _canonical_json_sha256(census_report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and _canonical_json_sha256(cubic_report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and set(report) == {
            "arithmetic_contract", "cache_and_mutation_contract",
            "carrier_certificate", "coefficient_map_certificate",
            "dimensions", "honest_conclusion", "model_contract_id",
            "overall_state", "pairing_certificate", "proof_grade",
            "provenance", "realification_certificate",
            "representative_invariance_certificate", "scope", "status",
        }
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_QUARTIC_MAP_CLOSED__PHYSICAL_TARGET_SDP_AND_G3_OPEN"
        and report.get("proof_grade") is True
        and isinstance(report.get("honest_conclusion"), str)
        and "G3 remain open" in report.get("honest_conclusion", "")
        and set(scope) == true_scope | false_scope
        and all(scope.get(name) is True for name in true_scope)
        and all(scope.get(name) is False for name in false_scope)
        and set(dimensions) == {
            "Phi", "Sym2_Phi", "complex_isotypic_types",
            "irreducible_copies", "quartic_domain", "quartic_kernel",
            "quartic_target", "real_Schur_blocks",
        }
        and dimensions == {
            "Phi": 210, "Sym2_Phi": 22_155,
            "complex_isotypic_types": 35, "irreducible_copies": 798,
            "real_Schur_blocks": 22, "quartic_domain": 18_085,
            "quartic_target": 6_057, "quartic_kernel": 12_028,
        }
        and set(provenance) == {
            "census_overall_state", "census_source",
            "census_source_sha256_canonical_LF", "census_status",
            "cubic_overall_state", "cubic_source",
            "cubic_source_sha256_canonical_LF", "cubic_status",
            "dependency_hashes_match_exact", "pinned_grade_counts",
            "proof_grade",
        }
        and provenance.get("proof_grade") is True
        and provenance.get("dependency_hashes_match_exact") is True
        and provenance.get("pinned_grade_counts") == {
            "domain": [1, 4, 90, 1_414, 18_085],
            "target": [1, 4, 45, 478, 6_057],
            "kernel": [0, 0, 45, 936, 12_028],
        }
        and census_source
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        and provenance.get("census_source_sha256_canonical_LF")
        == _file_sha256(ROOT / census_source)
        == "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
        and provenance.get("census_status") == census_report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and provenance.get("census_overall_state")
        == census_report.get("overall_state")
        == "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"
        and cubic_source
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
        and provenance.get("cubic_source_sha256_canonical_LF")
        == _file_sha256(ROOT / cubic_source)
        == "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
        and provenance.get("cubic_status") == cubic_report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED"
        and provenance.get("cubic_overall_state")
        == cubic_report.get("overall_state")
        == "SU4_AUGMENTED_CUBIC_MAP_CLOSED__FULL_SDP_AND_G3_OPEN"
        and set(carriers) == {
            "all_exact_highest_nullities_match_at_two_primes",
            "all_exact_raising_residuals_zero", "complex_isotypic_family_count",
            "estimated_CSR_storage_bytes_int64", "families_sha256",
            "irreducible_copy_count", "maximum_absolute_carrier_entry",
            "proof_grade", "rows", "total_carrier_dimension_with_multiplicity",
            "total_concatenated_nnz",
        }
        and carriers.get("proof_grade") is True
        and carriers.get("complex_isotypic_family_count") == 35
        and carriers.get("irreducible_copy_count") == 798
        and carriers.get("total_carrier_dimension_with_multiplicity") == 22_155
        and carriers.get("total_concatenated_nnz") == 177_751
        and carriers.get("maximum_absolute_carrier_entry") == 13_824
        and carriers.get("all_exact_highest_nullities_match_at_two_primes") is True
        and carriers.get("all_exact_raising_residuals_zero") is True
        and len(carriers.get("rows", [])) == 35
        and all(set(row) == carrier_row_keys for row in carriers.get("rows", []))
        and set(pairings) == {
            "all_pairings_are_positive_integer_multiples_of_inverse_metrics_exact",
            "component_metric", "maximum_absolute_pairing_entry",
            "pairings_sha256", "proof_grade", "real_block_count", "rows",
        }
        and pairings.get("proof_grade") is True
        and pairings.get("real_block_count") == 22
        and pairings.get("maximum_absolute_pairing_entry") == 4_976_640
        and pairings.get(
            "all_pairings_are_positive_integer_multiples_of_inverse_metrics_exact"
        ) is True
        and len(pairings.get("rows", [])) == 22
        and all(set(row) == pairing_row_keys for row in pairings.get("rows", []))
        and set(realification) == {
            "all_real_type_fixed_bases_checked_at_both_primes", "block_count",
            "domain_dimension", "integer_realification_convention",
            "ordered_tensor_multiplication_convention", "proof_grade",
            "real_type_warning_for_future_SDP", "rows",
        }
        and realification.get("proof_grade") is True
        and realification.get("block_count") == 22
        and realification.get("domain_dimension") == 18_085
        and realification.get("all_real_type_fixed_bases_checked_at_both_primes")
        is True
        and "must be constructed before an SDP"
        in realification.get("real_type_warning_for_future_SDP", "")
        and len(realification.get("rows", [])) == 22
        and all(
            set(row) == realification_row_keys
            for row in realification.get("rows", [])
        )
        and set(invariance) == {
            "all_22_representative_diagonal_images_physically_real_exact",
            "all_22_representatives_all_9_Chevalley_residuals_zero_exact",
            "proof_grade", "representative_count", "rows",
        }
        and invariance.get("proof_grade") is True
        and invariance.get("representative_count") == 22
        and invariance.get(
            "all_22_representatives_all_9_Chevalley_residuals_zero_exact"
        ) is True
        and invariance.get(
            "all_22_representative_diagonal_images_physically_real_exact"
        ) is True
        and len(invariance.get("rows", [])) == 22
        and all(set(row) == invariance_row_keys for row in invariance.get("rows", []))
        and set(coefficient_map) == map_keys
        and coefficient_map.get("proof_grade") is True
        and coefficient_map.get("shape") == [6_057, 18_085]
        and coefficient_map.get("nnz") == 115_641
        and coefficient_map.get("coordinate_map_sha256")
        == "ebb7b8b5cbca5d1c6e1f41d1e83e7229e2b885ec4fd34e23f305c788a4a1eb9b"
        and coefficient_map.get("full_image_stream_sha256")
        == "4807d170ed880cb4bcccaed29d054826d136d0057326fe2d1b252e1ff109422d"
        and coefficient_map.get("first_modular_prime") == 1_000_003
        and coefficient_map.get("second_modular_prime") == 1_000_033
        and coefficient_map.get("first_prime_rank") == 6_057
        and coefficient_map.get("second_prime_selected_minor_rank") == 6_057
        and coefficient_map.get("rank_over_Q_exact") == 6_057
        and coefficient_map.get("kernel_dimension_over_Q_exact") == 12_028
        and coefficient_map.get("first_pass_image_count_until_full_rank") == 16_140
        and coefficient_map.get("full_stream_image_count") == 18_085
        and coefficient_map.get("maximum_full_image_nnz") == 21_072
        and coefficient_map.get("maximum_full_image_absolute_coefficient")
        == 27_869_184
        and len(coefficient_map.get("selected_domain_columns", [])) == 6_057
        and len(set(coefficient_map.get("selected_domain_columns", []))) == 6_057
        and len(coefficient_map.get("pivot_physical_quartic_coordinates", []))
        == 6_057
        and set(csr) == {"data", "indices", "indptr"}
        and len(csr.get("data", [])) == 115_641
        and len(csr.get("indices", [])) == 115_641
        and len(csr.get("indptr", [])) == 6_058
        and set(cache_contract) == {
            "private_lru_caches_used_for_exact_heavy_objects",
            "public_carrier_and_pairing_data_return_deep_copies",
            "public_sparse_map_returns_defensive_copy",
            "unverified_external_binary_cache_used",
        }
        and cache_contract.get("private_lru_caches_used_for_exact_heavy_objects")
        is True
        and cache_contract.get("public_carrier_and_pairing_data_return_deep_copies")
        is True
        and cache_contract.get("public_sparse_map_returns_defensive_copy") is True
        and cache_contract.get("unverified_external_binary_cache_used") is False
        and set(arithmetic) == {
            "first_modular_prime", "integer_carriers_pairings_images_and_coordinate_map",
            "rational_operations_restricted_to_exact_metric_inversion",
            "second_modular_prime",
            "signed_int64_results_checked_or_python_integer_fallback",
        }
        and arithmetic.get("first_modular_prime") == 1_000_003
        and arithmetic.get("second_modular_prime") == 1_000_033
        and arithmetic.get("integer_carriers_pairings_images_and_coordinate_map")
        is True
        and arithmetic.get("rational_operations_restricted_to_exact_metric_inversion")
        is True
        and arithmetic.get("signed_int64_results_checked_or_python_integer_fallback")
        is True
    )


def _rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
    quartic_report: dict[str, Any],
) -> bool:
    """Recognize the rejected v20 payload and its retained route schema.

    The standard-cone congruences and lower-grade source APIs are retained as
    generation inputs for v21.  The assembled v20 target was built with the
    wrong quartic chart and is never accepted as a physical target or primal.
    """
    scope = report.get("scope", {})
    routes = report.get("standard_PSD_coordinate_routes", {})
    physical = report.get("physical_target", {})
    full_target = physical.get("full_graded_chart", {})
    quartic_target = physical.get("quartic", {})
    provenance = report.get("provenance", {})
    rejection = report.get("rejection", {})
    expected_hashes = provenance.get("expected_dependency_hashes", {})
    actual_hashes = provenance.get("actual_dependency_hashes", {})
    bindings = provenance.get("dependency_file_bindings", {})

    true_scope = {
        "all_22_standard_PSD_coordinate_routes_constructed",
        "all_nine_real_type_standard_PSD_congruences_constructed",
        "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates",
        "legacy_physical_target_rejected",
        "structural_PSD_routes_retained_for_v21_generation",
    }
    false_scope = {
        "coefficient_map_reparameterized_in_standard_PSD_coordinates",
        "semidefinite_feasibility_solved",
        "exact_primal_PSD_certificate_constructed",
        "exact_dual_Farkas_certificate_constructed",
        "arbitrary_Phi_lower_bound_proved",
        "equality_orbit_classification_proved",
        "full_486_field_Hessian_classification_proved",
        "physical_target_formula_all_five_grades_constructed",
        "physical_target_full_6585_row_vector_constructed",
        "G3_closed",
    }
    pinned_dependency_hashes = {
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json":
            "505f846291320e0671ff1208dc34339d0c2302f24ab80e9569b73d6479b2db8a",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json":
            "056e1a90c028f0aaca8fb17f2f53dfb02d5e7a33230ec3675537d2778755266a",
        "exact_gauged_u1x_g3_pd_rank_certificate_v20.py":
            "e2499baf3f7a572df7647ca02f109666a549c9e2c1989110c682ee584e0483c6",
        "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py":
            "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py":
            "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py":
            "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py":
            "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
        "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py":
            "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49",
        "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py":
            "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060",
        "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py":
            "6b2cfe46503833d8ac81dae385bef1bfa192bc0d4aa1dce392f2513b270aa14b",
        "exact_phisigma_casimir_projectors_v20.py":
            "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355",
    }
    binding_exact = bool(
        set(bindings) == set(pinned_dependency_hashes)
        and all(
            binding.get("imported_file_basename") == name
            and binding.get("repository_local_path") == name
            and binding.get("required_parent") == "."
            and binding.get("portable_sha256") == digest
            for name, digest in pinned_dependency_hashes.items()
            for binding in (bindings.get(name, {}),)
        )
    )
    live_dependencies_exact = all(
        _file_sha256(ROOT / name) == digest
        for name, digest in pinned_dependency_hashes.items()
    )
    prior_quartic_scope = quartic_report.get("scope", {})
    return bool(
        _file_sha256(
            ROOT
            / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
        ) == "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8"
        and _canonical_json_sha256(report)
        == "ebd1ec3edf7a02fc3919b55f61906d56269f490d28e70703e25c1c8b88e93566"
        and _canonical_json_sha256(census_report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and _canonical_json_sha256(cubic_report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and _canonical_json_sha256(quartic_report)
        == "ac48f6e6183a5b51ced47fcb8f4a1a9218df9bcf0951b632d8644f2a3d850f68"
        and set(report) == {
            "claim_boundary", "exact_arithmetic_safety", "model_contract_id",
            "overall_state", "physical_target", "proof_grade", "provenance",
            "rejection", "scope", "standard_PSD_coordinate_routes", "status",
        }
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("status")
        == "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY"
        and report.get("overall_state")
        == "STRUCTURAL_PSD_ROUTES_RETAINED__V20_PHYSICAL_TARGET_REJECTED__SUPERSEDED_BY_V21"
        and report.get("proof_grade") is False
        and rejection == {
            "corrected_certificate_raw_sha256":
                "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03",
            "corrected_map_numerator_csr_sha256":
                "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16",
            "corrected_publication_manifest_raw_sha256":
                "7ecf96a12321b9df5e7d118ce0fb83e65ad9859516b520936408ec4d46a11017",
            "corrected_target_numerator_sha256":
                "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf",
            "reason": (
                "The v20 extremal-minor raw-Schur reconstruction does not equal "
                "the collapsed ordered-spectral physical quartic, and the "
                "grade-0/grade-1 map normalization is wrong."
            ),
            "retained_content": (
                "The 22 standard PSD-coordinate congruence routes are structural "
                "generation provenance only."
            ),
            "superseded_by": "corrected_rank1_publication_v21",
            "v20_physical_target_accepted": False,
            "v20_primal_or_arbitrary_Phi_theorem_accepted": False,
        }
        and set(scope) == true_scope | false_scope
        and all(scope.get(name) is True for name in true_scope)
        and all(scope.get(name) is False for name in false_scope)
        and routes.get("all_22_cones_have_standard_coordinate_routes") is True
        and routes.get("real_type_block_count") == 9
        and len(routes.get("real_type_rows", [])) == 9
        and routes.get("complex_Hermitian_block_count") == 13
        and len(routes.get("complex_Hermitian_rows", [])) == 13
        and routes.get("standard_real_parameter_count") == 7_979
        and routes.get("standard_complex_parameter_count") == 11_615
        and routes.get("standard_total_parameter_count") == 19_594
        and physical.get("accepted_as_physical_target") is False
        and physical.get("constant") == {"numerator": 237, "denominator": 200}
        and physical.get("cubic", {}).get("row_count") == 478
        and physical.get("cubic", {}).get("all_target_rows_zero_exact") is True
        and quartic_target.get("row_count") == 6_057
        and quartic_target.get("common_denominator") == 3_375
        and quartic_target.get("nonzero_count") == 825
        and quartic_target.get("numerator_sha256")
        == "38476cff340ef8702735d48d7dbdf644ed41f8dc4a359264d33d966f177145ad"
        and quartic_target.get("pivot_physical_quartic_coordinates_sha256")
        == "f33cb0163f3cdc4a3480cb55e09329888c8cf0641cc0acab4cb01f8075058ce4"
        and quartic_target.get("all_i_times_anti_real_rows_zero_exact") is True
        and quartic_target.get("proof_grade") is False
        and full_target.get("grade_lengths") == [1, 4, 45, 478, 6_057]
        and full_target.get("row_count") == 6_585
        and full_target.get("common_denominator") == 1_728_000
        and full_target.get("total_nonzero_count") == 845
        and full_target.get("nonzero_count_by_grade") == {
            "constant": 1, "linear": 2, "quadratic": 17,
            "cubic": 0, "quartic": 825,
        }
        and full_target.get("numerator_sha256")
        == "e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630"
        and len(full_target.get("numerator", [])) == 6_585
        and full_target.get("primitive_common_fraction") is True
        and full_target.get("proof_grade") is False
        and provenance.get("repository_local_dependency_root") == "."
        and provenance.get("all_dependency_files_required_beside_this_module")
        is True
        and provenance.get("dependency_hash_algorithm")
        == "SHA256 of UTF-8 text after LF normalization"
        and "no external shadow can satisfy it"
        in provenance.get("source_module_path_binding", "")
        and expected_hashes == pinned_dependency_hashes
        and actual_hashes == pinned_dependency_hashes
        and provenance.get("all_dependency_hashes_match_exact") is True
        and binding_exact
        and live_dependencies_exact
        and prior_quartic_scope.get("physical_quartic_target_constructed")
        is False
        and prior_quartic_scope.get(
            "standard_PSD_congruences_for_real_type_fixed_bases_constructed"
        ) is False
        and prior_quartic_scope.get("semidefinite_feasibility_solved") is False
        and prior_quartic_scope.get(
            "arbitrary_Phi_stationarity_or_lower_bound_proved"
        ) is False
        and prior_quartic_scope.get("G3_closed") is False
    )


def _rank1_su4_augmented_sos_psd_target_exact(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
    quartic_report: dict[str, Any],
) -> bool:
    """The v20 assembled physical target is superseded and always rejected."""
    del report, census_report, cubic_report, quartic_report
    return False


def _gauged_u1x_g3_frontier(
    sos_report: dict[str, Any],
    pd_report: dict[str, Any],
    a_square_report: dict[str, Any],
    sos_bfb_report: dict[str, Any],
    kernel_bound_report: dict[str, Any],
    replacement_report: dict[str, Any],
    su5_pd_report: dict[str, Any],
    su5_hsx_report: dict[str, Any],
    su5_hsx_exact_hessian_report: dict[str, Any],
    su5_equality_report: dict[str, Any],
    su5_phi_orbit_report: dict[str, Any],
    su5_phi_local_component_report: dict[str, Any],
    su5_phi_su3_slice_report: dict[str, Any],
    su5_gap_report: dict[str, Any],
    su5_fixed_f_offkernel_report: dict[str, Any],
    su5_max_negative_zero_residual_report: dict[str, Any],
    su5_max_negative_full_residual_report: dict[str, Any],
    su5_max_negative_rank1_su3_slice_report: dict[str, Any],
    rank1_su4_stabilizer_report: dict[str, Any],
    rank1_su4_phi210_intertwiners_report: dict[str, Any],
    rank1_su4_aligned_carriers_report: dict[str, Any],
    rank1_su4_phi210_quadratic_basis_report: dict[str, Any],
    rank1_su4_augmented_sos_census_report: dict[str, Any],
    rank1_su4_augmented_sos_cubic_map_report: dict[str, Any],
    rank1_su4_augmented_sos_quartic_map_report: dict[str, Any],
    rank1_su4_augmented_sos_psd_target_report: dict[str, Any],
    rank1_su4_corrected_publication: dict[str, Any],
    alternative_global_sos_report: dict[str, Any],
) -> dict[str, Any]:
    """Bind rejected branches and the surviving SU(5)+Delta G3 frontier."""
    sos_flags = sos_report.get("flags", {})
    coefficients = sos_report.get("coefficient_vector", {})
    symbolic = coefficients.get("symbolic_nonzero", {})
    quotient = sos_report.get("symmetry_quotient", {})
    nested_pd = sos_report.get("exact_rank_certificate", {})
    nested_a_square = sos_report.get(
        "exact_A_square_recoupling_certificate", {}
    )
    nested_global_counterexample = sos_report.get(
        "exact_global_counterexample_certificate", {}
    )
    nested_global_flags = nested_global_counterexample.get("flags", {})

    pd_flags = pd_report.get("flags", {})
    nested_sos_bfb = sos_report.get(
        "exact_SOS_BFB_stationarity_certificate", {}
    )
    pd_direct = pd_report.get("direct_P_plus_Delta_certificate", {})
    pd_core = pd_report.get("direct_exact_ranks", {}).get(
        "H_Phi_plus_K", {}
    )
    pd_extension = pd_report.get("exact_full_kernel_argument", {})

    a_flags = a_square_report.get("flags", {})
    a_certificate = a_square_report.get("certificate", {})
    sos_bfb_flags = sos_bfb_report.get("flags", {})
    kernel_flags = kernel_bound_report.get("flags", {})
    replacement_flags = replacement_report.get("flags", {})
    su5_scope = su5_pd_report.get("scope", {})
    hsx_flags = su5_hsx_report.get("flag", {})
    hsx_candidate = su5_hsx_report.get("chiral_H_candidate", {})
    hsx_orbit = hsx_candidate.get("exact_orbit", {})
    hsx_bfb = su5_hsx_report.get("BFB_certificate", {})
    hsx_hessian = su5_hsx_report.get("live_full_gradient_and_quotient_Hessian", {})
    hsx_global = su5_hsx_report.get("global_status", {})
    hsx_exact_flags = su5_hsx_exact_hessian_report.get("flags", {})
    equality_scope = su5_equality_report.get("scope", {})
    equality_lemma = su5_equality_report.get("remaining_global_lemma", {})
    equality_global = su5_equality_report.get(
        "Phi_global_signed_zero_theorem", {}
    )
    phi_orbit_scope = su5_phi_orbit_report.get("scope", {})
    phi_orbit_lemma = su5_phi_orbit_report.get("corrected_global_lemma", {})
    phi_local_scope = su5_phi_local_component_report.get("scope", {})
    phi_su3_scope = su5_phi_su3_slice_report.get("scope", {})
    phi_su3_checks = su5_phi_su3_slice_report.get("checks", {})
    gap_flags = su5_gap_report.get("flags", {})
    gap_acceptance = su5_gap_report.get("final_acceptance_test", {})
    gap_reduction = su5_gap_report.get("small_beta_global_reduction", {})
    fixed_f_offkernel_scope = su5_fixed_f_offkernel_report.get("scope", {})
    fixed_f_offkernel_checks = su5_fixed_f_offkernel_report.get("checks", {})
    max_negative_scope = su5_max_negative_zero_residual_report.get("scope", {})
    max_negative_checks = su5_max_negative_zero_residual_report.get("checks", {})
    max_negative_full_scope = su5_max_negative_full_residual_report.get(
        "scope", {}
    )
    max_negative_full_checks = su5_max_negative_full_residual_report.get(
        "checks", {}
    )
    rank1_su3_scope = su5_max_negative_rank1_su3_slice_report.get("scope", {})
    rank1_su3_checks = su5_max_negative_rank1_su3_slice_report.get("checks", {})
    rank1_su4_stabilizer_scope = rank1_su4_stabilizer_report.get("scope", {})
    rank1_su4_stabilizer_checks = rank1_su4_stabilizer_report.get("checks", {})
    rank1_su4_intertwiner_scope = rank1_su4_phi210_intertwiners_report.get(
        "scope", {}
    )
    rank1_su4_intertwiner_checks = rank1_su4_phi210_intertwiners_report.get(
        "checks", {}
    )
    rank1_su4_aligned_scope = rank1_su4_aligned_carriers_report.get(
        "scope", {}
    )
    rank1_su4_quadratic_scope = rank1_su4_phi210_quadratic_basis_report.get(
        "scope", {}
    )
    rank1_su4_census_scope = rank1_su4_augmented_sos_census_report.get(
        "scope", {}
    )
    rank1_su4_cubic_scope = rank1_su4_augmented_sos_cubic_map_report.get(
        "scope", {}
    )
    rank1_su4_quartic_scope = rank1_su4_augmented_sos_quartic_map_report.get(
        "scope", {}
    )
    rank1_su4_quartic_map = rank1_su4_augmented_sos_quartic_map_report.get(
        "coefficient_map_certificate", {}
    )
    rank1_su4_psd_target_scope = rank1_su4_augmented_sos_psd_target_report.get(
        "scope", {}
    )
    rank1_su4_psd_routes = rank1_su4_augmented_sos_psd_target_report.get(
        "standard_PSD_coordinate_routes", {}
    )
    rank1_su4_physical_target = rank1_su4_augmented_sos_psd_target_report.get(
        "physical_target", {}
    )
    rank1_su4_full_target = rank1_su4_physical_target.get(
        "full_graded_chart", {}
    )
    rank1_su4_quartic_target = rank1_su4_physical_target.get("quartic", {})
    rank1_su4_corrected_exact = (
        corrected_rank1.corrected_fixed_endpoint_theorem_exact(
            rank1_su4_corrected_publication
        )
    )
    rank1_su4_corrected_view = (
        corrected_rank1.central_view(rank1_su4_corrected_publication)
        if rank1_su4_corrected_exact
        else {}
    )
    alternative_flags = alternative_global_sos_report.get("flags", {})

    artifacts_present = {
        "SOS_candidate": bool(sos_report),
        "direct_exact_PD_rank": bool(pd_report),
        "exact_A_square_recoupling": bool(a_square_report),
        "exact_SOS_BFB_stationarity": bool(sos_bfb_report),
        "fixed_P_kernel_no_go": bool(kernel_bound_report),
        "lower_replacement_orbit": bool(replacement_report),
        "SU5_Delta_PD_global_SOS": bool(su5_pd_report),
        "SU5_Delta_HSX_extension": bool(su5_hsx_report),
        "SU5_Delta_HSX_exact_Hessian": bool(su5_hsx_exact_hessian_report),
        "SU5_Delta_equality_orbit": bool(su5_equality_report),
        "SU5_Delta_Phi_orbit_lemma_audit": bool(su5_phi_orbit_report),
        "SU5_Delta_Phi_local_component_theorem": bool(
            su5_phi_local_component_report
        ),
        "SU5_Delta_Phi_SU3_fixed_slice_theorem": bool(
            su5_phi_su3_slice_report
        ),
        "SU5_Delta_chiral_global_gap_reduction": bool(su5_gap_report),
        "SU5_fixed_F_full_offkernel_bound": bool(su5_fixed_f_offkernel_report),
        "SU5_max_negative_all_zero_residual_bound": bool(
            su5_max_negative_zero_residual_report
        ),
        "SU5_max_negative_full_residual_pure_Delta_bound": bool(
            su5_max_negative_full_residual_report
        ),
        "SU5_max_negative_rank1_SU3_four_dimensional_slice_bound": bool(
            su5_max_negative_rank1_su3_slice_report
        ),
        "rank1_SU4_stabilizer_infrastructure": bool(rank1_su4_stabilizer_report),
        "rank1_SU4_Phi210_intertwiner_infrastructure": bool(
            rank1_su4_phi210_intertwiners_report
        ),
        "rank1_SU4_aligned_carrier_infrastructure": bool(
            rank1_su4_aligned_carriers_report
        ),
        "rank1_SU4_Phi210_quadratic_basis": bool(
            rank1_su4_phi210_quadratic_basis_report
        ),
        "rank1_SU4_augmented_SOS_census": bool(
            rank1_su4_augmented_sos_census_report
        ),
        "rank1_SU4_augmented_SOS_cubic_map": bool(
            rank1_su4_augmented_sos_cubic_map_report
        ),
        "rank1_SU4_augmented_SOS_quartic_map": bool(
            rank1_su4_augmented_sos_quartic_map_report
        ),
        "rank1_SU4_legacy_v20_PSD_routes_and_rejected_target": bool(
            rank1_su4_augmented_sos_psd_target_report
        ),
        "rank1_SU4_corrected_fixed_endpoint_publication_v21": bool(
            rank1_su4_corrected_publication
        ),
        "alternative_global_SOS_audit": bool(alternative_global_sos_report),
    }
    a_square_exact = bool(
        a_square_report.get("status") == "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        and a_square_report.get("overall_state") == "CLOSED_SUBPROBLEM"
        and a_square_report.get("n_failed") == 0
        and a_certificate.get("source_binding_exact") is True
        and a_certificate.get("proof_grade") is True
        and a_certificate.get("unique_weights")
        == ["40", "72", "28", "-8", "-12", "12"]
        and a_flags.get("A_square_recoupling_exactly_source_bound") is True
        and a_flags.get("complete_potential_BFB_exactly_certified") is False
        and a_flags.get("full_Hessian_exactly_source_bound") is False
        and a_flags.get("strict_local_minimum_certified") is False
        and a_flags.get("G3_closed") is False
    )
    sos_bfb_exact = bool(
        sos_bfb_report.get("status")
        == "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        and sos_bfb_report.get("overall_state") == "CLOSED_SUBPROBLEM"
        and sos_bfb_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and sos_bfb_report.get("n_failed") == 0
        and sos_bfb_flags.get(
            "complete_27_parameter_SOS_identity_exactly_source_bound"
        )
        is True
        and sos_bfb_flags.get("complete_potential_BFB_exactly_certified") is True
        and sos_bfb_flags.get("selected_vacuum_stationarity_exactly_certified")
        is True
        and sos_bfb_flags.get("selected_vacuum_global_minimum_certified") is False
        and sos_bfb_flags.get("selected_vacuum_unique_modulo_symmetry") is False
        and sos_bfb_flags.get("G3_closed") is False
    )
    pd_direct_and_fail_closed = bool(
        pd_report.get("status")
        == "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        and pd_report.get("overall_state") == STATUS_OPEN
        and pd_report.get("n_failed") == 0
        and pd_direct.get("source_binding_exact") is True
        and pd_direct.get("proof_grade") is True
        and pd_core == {"rank": 429, "nullity": 33, "PSD": True}
        and pd_extension.get("exact_full_Hessian_rank") == 448
        and pd_extension.get("remaining_kernel_dimension") == 38
        and pd_extension.get("source_binding_exact") is True
        and pd_extension.get("proof_grade") is True
        and pd_flags.get("conditional_exact_LDL_on_reconstructed_matrix") is False
        and pd_flags.get("direct_exact_source_binding") is True
        and pd_flags.get("proof_grade_P_plus_Delta_PSD") is True
        and pd_flags.get("proof_grade_full_rank_448") is True
        and pd_flags.get("strict_transverse_Hessian_positive_certified") is True
        and pd_flags.get("strict_local_minimum_certified_here") is False
        and pd_flags.get("global_minimum_certified") is False
        and pd_flags.get("global_uniqueness_certified") is False
        and pd_flags.get("G3_closed") is False
        and pd_flags.get("whole_model_validated") is False
        and pd_flags.get("whole_model_excluded") is False
    )
    sos_exact_local_and_globally_rejected = bool(
        sos_report.get("status")
        == "EXACT_BFB_STATIONARY_STRICT_LOCAL_MINIMUM__GLOBAL_COUNTEREXAMPLE"
        and sos_report.get("overall_state") == STATUS_OPEN
        and sos_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and sos_report.get("n_failed") == 0
        and coefficients.get("nonzero_count") == 27
        and coefficients.get("maximum_absolute_coefficient") == 9.125
        and symbolic.get("lambda::O48_B01_Phi_self_quartics") == "-21/200"
        and quotient.get("SO10_plus_U1X_plus_global_PQ_rank") == 38
        and quotient.get("massive_transverse_dimension") == 448
        and sos_flags.get("exact_sparse_51_parameter_candidate_constructed") is True
        and sos_flags.get("candidate_inside_4pi_box") is True
        and sos_flags.get(
            "positive_J0_normalization_is_without_loss_of_generality"
        )
        is False
        and sos_flags.get("manifest_BFB_decomposition_candidate_constructed") is True
        and sos_flags.get("A_square_recoupling_exactly_source_bound") is True
        and sos_flags.get("complete_potential_BFB_exactly_certified") is True
        and sos_flags.get(
            "selected_vacuum_stationarity_exactly_compiler_certified"
        )
        is True
        and sos_flags.get("selected_vacuum_global_minimum_certified") is False
        and sos_flags.get("selected_vacuum_global_minimum_disproved") is True
        and sos_flags.get("selected_vacuum_unique_modulo_symmetry") is False
        and sos_flags.get("exact_lower_energy_field_witness_certified") is True
        and sos_flags.get("constructive_candidate_rejected_for_G3") is True
        and sos_flags.get("P_plus_Delta_Qsqrt2_component_LDL_conditional") is False
        and sos_flags.get("P_plus_Delta_source_binding_exactly_certified") is True
        and sos_flags.get("full_448_kernel_count_conditional") is False
        and sos_flags.get("full_448_kernel_count_exact") is True
        and sos_flags.get("full_448_PSD_feasibility_certified") is True
        and sos_flags.get("strict_local_minimum_certified") is True
        and sos_flags.get("G3_closed") is False
        and sos_flags.get("whole_model_validated") is False
        and sos_flags.get("whole_model_excluded") is False
        and nested_pd.get("status") == pd_report.get("status")
        and nested_pd.get("direct_exact_ranks", {}).get("H_Phi_plus_K", {})
        == pd_core
        and nested_sos_bfb.get("status") == sos_bfb_report.get("status")
        and nested_a_square.get("status") == a_square_report.get("status")
        and nested_a_square.get("certificate", {}).get("unique_weights")
        == a_certificate.get("unique_weights")
        and nested_global_counterexample.get("n_failed") == 0
        and nested_global_flags.get(
            "lower_energy_field_witness_exactly_certified"
        )
        is True
        and nested_global_flags.get("selected_vacuum_global_minimum_disproved")
        is True
    )
    fixed_p_no_go_exact = bool(
        kernel_bound_report.get("n_failed") == 0
        and kernel_flags.get("fixed_P_strict_local_global_no_go_exact") is True
        and kernel_flags.get("fixed_P_branch_closed_negative") is True
        and kernel_flags.get("G3_closed") is False
        and kernel_flags.get("whole_model_excluded") is False
    )
    replacement_wrong_symmetry = bool(
        replacement_report.get("n_failed") == 0
        and replacement_flags.get("replacement_full_stationarity_exact") is True
        and replacement_flags.get("replacement_symmetry_orbit_rank_exact") is True
        and replacement_flags.get("replacement_target_gauge_symmetry_correct")
        is False
        and replacement_flags.get("replacement_strict_local_minimum_proof_grade")
        is False
        and replacement_flags.get("replacement_global_minimum_established")
        is False
        and replacement_flags.get("G3_closed") is False
    )
    su5_pd_exact_frontier = bool(
        su5_pd_report.get("n_failed") == 0
        and su5_pd_report.get("status")
        == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
        and su5_scope.get("Phi_Sigma_global_minimum_exact") is True
        and su5_scope.get("Phi_Sigma_stationarity_exact") is True
        and su5_scope.get("SO10_to_SM_stabilizer_dimension_exact") is True
        and su5_scope.get("Phi_Sigma_Hessian_rank_429_nullity_33_exact") is True
        and su5_scope.get("Phi_Sigma_quotient_strictly_positive_exact") is True
        and su5_scope.get("Phi_Sigma_equality_set_locally_one_orbit") is True
        and su5_scope.get("full_486_field_stationarity") is False
        and su5_scope.get("global_orbit_uniqueness") is False
        and su5_scope.get("G3_closed") is False
    )
    su5_hsx_honest_frontier = bool(
        su5_hsx_report.get("n_failed") == 0
        and su5_hsx_report.get("status")
        == "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
        and su5_hsx_report.get("overall_state")
        == "G3_PROMISING_CANDIDATE_NOT_CLOSED"
        and su5_hsx_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and hsx_flags.get("real_H_e6_extension_exactly_excluded") is True
        and hsx_flags.get("chiral_H_exact_stationary_candidate_constructed")
        is True
        and hsx_flags.get("full_486_gradient_zero_live") is True
        and hsx_flags.get(
            "strict_448_quotient_local_minimum_high_confidence_numeric"
        )
        is True
        and hsx_flags.get("full_quartic_BFB_certified") is True
        and hsx_flags.get("full_global_minimum_certified") is False
        and hsx_flags.get("G3_closed") is False
        and hsx_flags.get("whole_model_excluded") is False
        and hsx_orbit.get("SO10_rank") == 36
        and hsx_orbit.get("SO10_plus_U1X_rank") == 37
        and hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank") == 38
        and hsx_orbit.get("physical_quotient_dimension") == 448
        and hsx_orbit.get("source_binding_exact") is True
        and hsx_bfb.get("homogeneous_quartic_BFB_certified") is True
        and hsx_bfb.get("finite_field_global_gap_certified") is False
        and hsx_hessian.get("proof_grade") is False
        and hsx_hessian.get("transverse_dimension") == 448
        and hsx_hessian.get("negative_transverse_eigenvalues_below_minus_1e_minus_9")
        == 0
        and hsx_hessian.get("zero_transverse_eigenvalues_at_1e_minus_9") == 0
        and hsx_global.get("full_homogeneous_quartic_BFB_exact") is True
        and hsx_global.get("beta_deformed_finite_field_global_gap_exact") is False
        and hsx_global.get("global_equality_orbits_classified") is False
        and hsx_global.get("G3_closed") is False
    )
    su5_hsx_exact_hessian_closed = bool(
        su5_hsx_exact_hessian_report.get("status")
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and su5_hsx_exact_hessian_report.get("overall_state")
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and su5_hsx_exact_hessian_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and su5_hsx_exact_hessian_report.get("n_failed") == 0
        and hsx_exact_flags.get("exact_rank_448") is True
        and hsx_exact_flags.get("exact_nullity_38") is True
        and hsx_exact_flags.get("exact_PSD") is True
        and hsx_exact_flags.get("strict_quotient_positive") is True
        and hsx_exact_flags.get("kernel_equals_38_symmetry_tangents") is True
        and hsx_exact_flags.get("source_binding_exact") is True
        and hsx_exact_flags.get("proof_grade") is True
        and su5_hsx_exact_hessian_report.get("G3_closed") is False
    )
    su5_equality_honestly_reduced = bool(
        su5_equality_report.get("n_failed") == 0
        and su5_equality_report.get("status")
        == "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
        and su5_equality_report.get("overall_state")
        == "GLOBAL_EQUALITY_ORBITS_CLOSED"
        and equality_scope.get("fixed_F_Sigma_global_equality_classified") is True
        and equality_scope.get(
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        )
        is True
        and equality_scope.get(
            "fixed_Delta_two_tau_plus_representatives_equivalent"
        )
        is True
        and equality_scope.get("literal_single_Phi_orbit_statement_refuted")
        is True
        and equality_scope.get("minus_F_mixed_branch_excluded_exact") is True
        and equality_scope.get("corrected_signed_Phi_orbit_theorem_open") is False
        and equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        is True
        and equality_scope.get("signed_Phi_orbits_locally_isolated_exactly")
        is True
        and equality_scope.get("complete_SU3_fixed_Phi_slice_classified_exactly")
        is True
        and equality_scope.get("distant_disconnected_Phi_components_excluded")
        is True
        and equality_scope.get(
            "all_arbitrary_Phi_global_equalities_classified"
        )
        is True
        and equality_scope.get("global_equality_orbit_classification_complete")
        is True
        and equality_scope.get("quantitative_beta_global_coercivity_proved")
        is False
        and equality_scope.get("G3_closed") is False
        and equality_scope.get("whole_model_excluded") is False
        and equality_lemma.get("proved") is True
        and equality_lemma.get("literal_single_orbit_version_refuted") is True
        and equality_lemma.get("corrected_signed_two_orbit_version") is True
        and equality_lemma.get("source_bound_certificate_available") is True
        and equality_lemma.get("source_bound_partial_certificate_available") is True
        and equality_lemma.get("signed_orbits_locally_isolated_exactly") is True
        and equality_lemma.get("complete_SU3_fixed_slice_classified_exactly")
        is True
        and equality_lemma.get("SU3_fixed_slice_real_dimension") == 16
        and equality_lemma.get("distant_disconnected_components_excluded") is True
        and equality_lemma.get("quantitative_orbit_distance_bound_proved")
        is False
        and equality_lemma.get("numerical_search_is_not_a_substitute") is True
        and equality_global.get("frozen_source_sha256")
        == "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
        and equality_global.get("core_sha256")
        == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
        and equality_global.get("external_theorem_dependency", {}).get("kind")
        == "published subgroup-classification theorem"
    )
    su5_phi_orbit_audit_honest = bool(
        su5_phi_orbit_report.get("status")
        == "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
        and su5_phi_orbit_report.get("overall_state")
        == "SHARP_COUNTEREXAMPLE_AND_REDUCTION"
        and su5_phi_orbit_report.get("n_failed") == 0
        and phi_orbit_scope.get("literal_plus_orbit_only_statement_refuted")
        is True
        and phi_orbit_scope.get("complete_SU4_invariant_slice_classified")
        is True
        and phi_orbit_scope.get("corrected_signed_two_orbit_theorem_proved")
        is False
        and phi_orbit_scope.get("all_arbitrary_real_four_forms_classified")
        is False
        and phi_orbit_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and phi_orbit_scope.get("G3_closed") is False
        and phi_orbit_scope.get("whole_model_excluded") is False
        and phi_orbit_lemma.get("proved") is False
        and phi_orbit_lemma.get("counterexample_found") is False
    )
    su5_phi_local_components_closed = bool(
        su5_phi_local_component_report.get("status")
        == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
        and su5_phi_local_component_report.get("overall_state")
        == "LOCAL_COMPONENT_THEOREM_CLOSED"
        and su5_phi_local_component_report.get("n_failed") == 0
        and phi_local_scope.get("plus_F_local_component_classified") is True
        and phi_local_scope.get("minus_F_local_component_classified") is True
        and phi_local_scope.get("signed_orbit_locally_isolated") is True
        and phi_local_scope.get("explicit_neighborhood_radius_available") is False
        and phi_local_scope.get("disconnected_distant_components_excluded")
        is False
        and phi_local_scope.get("corrected_signed_global_orbit_theorem_proved")
        is False
        and phi_local_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and phi_local_scope.get("G3_closed") is False
        and phi_local_scope.get("whole_model_excluded") is False
    )
    su5_phi_su3_slice_closed = bool(
        su5_phi_su3_slice_report.get("status")
        == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
        and su5_phi_su3_slice_report.get("overall_state")
        == "SU3_FIXED_SLICE_CLOSED"
        and su5_phi_su3_slice_report.get("n_failed") == 0
        and phi_su3_checks.get("displayed_space_is_complete_SU3_fixed_space")
        is True
        and phi_su3_checks.get("restricted_projector_rowspace_reduced_exactly")
        is True
        and phi_su3_checks.get(
            "eight_nondiagonal_directions_have_real_SOS_obstruction"
        )
        is True
        and phi_su3_checks.get("complete_SU3_fixed_slice_is_signed_Kahler_orbit")
        is True
        and phi_su3_scope.get(
            "complete_16_real_dimensional_SU3_fixed_space_classified"
        )
        is True
        and phi_su3_scope.get(
            "all_nonzero_slice_solutions_are_signed_Kahler_squares"
        )
        is True
        and phi_su3_scope.get("all_arbitrary_real_four_forms_classified") is False
        and phi_su3_scope.get("disconnected_distant_components_excluded") is False
        and phi_su3_scope.get("corrected_signed_global_orbit_theorem_proved")
        is False
        and phi_su3_scope.get("G3_closed") is False
        and phi_su3_scope.get("whole_model_excluded") is False
    )
    su5_chiral_gap_honestly_reduced = bool(
        su5_gap_report.get("n_failed") == 0
        and su5_gap_report.get("status")
        == "GLOBAL_GAP_REDUCED_TO_QUANTITATIVE_COERCIVITY"
        and su5_gap_report.get("overall_state") == "FINAL_G3_TEST_OPEN"
        and su5_gap_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and gap_flags.get("lower_witness_found") is False
        and gap_flags.get("conditional_small_positive_beta_route_exists") is True
        and gap_flags.get("beta_1_over_20_global_minimum_certified") is False
        and gap_flags.get("PD_equality_orbits_classified") is True
        and gap_flags.get("global_equality_orbits_classified") is False
        and gap_flags.get("G3_closed") is False
        and gap_flags.get("whole_model_excluded") is False
        and gap_acceptance.get("currently_passes") is False
        and gap_reduction.get("theorem_ready") is False
        and gap_reduction.get("beta_equals_1_over_20_covered_by_theorem") is False
    )
    su5_fixed_f_full_gap_closed = bool(
        su5_fixed_f_offkernel_report.get("n_failed") == 0
        and su5_fixed_f_offkernel_report.get("status")
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and su5_fixed_f_offkernel_report.get("overall_state")
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_offkernel_checks.get(
            "mixed_offkernel_gap_at_least_6_over_5_exact"
        )
        is True
        and fixed_f_offkernel_checks.get("pure_hplus_current_error_bound_exact")
        is True
        and fixed_f_offkernel_checks.get("kernel_chirality_cross_zero_exact")
        is True
        and fixed_f_offkernel_checks.get("cross_block_bound_exact") is True
        and fixed_f_offkernel_checks.get("rational_inside_outside_patch_positive")
        is True
        and fixed_f_offkernel_checks.get("full_fixed_F_equality_orbit_exact")
        is True
        and fixed_f_offkernel_scope.get("Phi_fixed_to_F") is True
        and fixed_f_offkernel_scope.get("H_arbitrary") is True
        and fixed_f_offkernel_scope.get("Sigma_arbitrary") is True
        and fixed_f_offkernel_scope.get("beta_equals_1_over_20") is True
        and fixed_f_offkernel_scope.get(
            "global_gap_nonnegative_on_full_fixed_F_stratum"
        )
        is True
        and fixed_f_offkernel_scope.get("equality_is_selected_SU5_flag_orbit")
        is True
        and fixed_f_offkernel_scope.get("arbitrary_Phi_proved") is False
        and fixed_f_offkernel_scope.get("G3_closed") is False
    )
    su5_max_negative_all_zero_route_excluded = bool(
        su5_max_negative_zero_residual_report.get("n_failed") == 0
        and su5_max_negative_zero_residual_report.get("status")
        == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
        and su5_max_negative_zero_residual_report.get("overall_state")
        == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
        and su5_max_negative_zero_residual_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and max_negative_checks.get("exact_rank_168_nullity_42") is True
        and max_negative_checks.get("kernel_splits_35_plus_7_exactly") is True
        and max_negative_checks.get("live_HSX_and_PD_coefficients_bound_exactly")
        is True
        and max_negative_checks.get(
            "N_and_C00_C11_contraction_identities_computed_exactly"
        )
        is True
        and max_negative_checks.get(
            "Phi_radial_plus_I54_lower_bound_1_over_141"
        )
        is True
        and max_negative_checks.get("worst_radial_current_minimum_exact") is True
        and max_negative_checks.get("strict_positive_stratum_margin_exact") is True
        and max_negative_checks.get(
            "u_zero_and_v_zero_radial_boundaries_closed_exactly"
        )
        is True
        and su5_max_negative_zero_residual_report.get("exact_stratum_gap", {}).get(
            "strict_margin"
        )
        == "7859/140295000"
        and max_negative_scope.get(
            "strongest_all_zero_max_negative_route_excluded"
        )
        is True
        and max_negative_scope.get(
            "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
        )
        is True
        and max_negative_scope.get(
            "normalized_affine_stratum_requires_u_gt_0_v_gt_0"
        )
        is True
        and max_negative_scope.get(
            "u_zero_and_v_zero_boundaries_closed_separately"
        )
        is True
        and max_negative_scope.get("nonzero_residual_cancellations_excluded")
        is False
        and max_negative_scope.get("arbitrary_Phi_global_gap_proved") is False
        and max_negative_scope.get("G3_closed") is False
    )
    su5_max_negative_full_residual_pure_delta_closed = bool(
        su5_max_negative_full_residual_report.get("n_failed") == 0
        and su5_max_negative_full_residual_report.get("status")
        == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
        and su5_max_negative_full_residual_report.get("overall_state")
        == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
        and su5_max_negative_full_residual_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and max_negative_full_scope.get("Sigma_on_pure_Delta_orbit") is True
        and max_negative_full_scope.get(
            "H_current_saturates_I45_equals_minus_NH_NSigma"
        )
        is True
        and max_negative_full_scope.get("Phi_arbitrary_real_210") is True
        and max_negative_full_scope.get("nonzero_Phi_Sigma_residuals_covered")
        is True
        and max_negative_full_scope.get("nonzero_chiral_Phi_H_residual_covered")
        is True
        and max_negative_full_scope.get("u_v_all_nonnegative") is True
        and max_negative_full_scope.get("restricted_gap_global_minimum")
        == "1/5000"
        and max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        is False
        and max_negative_full_scope.get("G3_closed") is False
        and all(
            max_negative_full_checks.get(name) is True
            for name in (
                "live_restricted_residual_normalizations_exact",
                "single_4125_covariant_Cauchy_bound_exact",
                "anchor_quadratic_has_exact_positive_spectral_floor",
                "anchor_lower_bound_strictly_exceeds_1_over_50",
                "piecewise_u_v_completion_covers_nonnegative_quadrant",
                "exact_1_over_5000_saturation_exhibited",
                "arbitrary_real_Phi_covered",
                "mixed_and_chiral_residuals_not_assumed_zero",
                "arbitrary_Sigma_orientation_not_overclaimed",
                "G3_not_overclaimed",
            )
        )
    )
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
    su5_max_negative_rank1_su3_slice_closed = bool(
        su5_max_negative_rank1_su3_slice_report.get("n_failed") == 0
        and su5_max_negative_rank1_su3_slice_report.get("failed_checks") == []
        and su5_max_negative_rank1_su3_slice_report.get("status")
        == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
        and su5_max_negative_rank1_su3_slice_report.get("overall_state")
        == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
        and su5_max_negative_rank1_su3_slice_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and rank1_su3_scope.get("H_fixed_to_h_minus") is True
        and rank1_su3_scope.get(
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
        )
        is True
        and rank1_su3_scope.get(
            "Phi_restricted_to_four_real_SU3_fixed_variables"
        )
        is True
        and rank1_su3_scope.get("Phi_slice_real_dimension") == 4
        and rank1_su3_scope.get("full_SU3_fixed_space_real_dimension") == 16
        and rank1_su3_scope.get("full_SU3_fixed_space_proved") is False
        and rank1_su3_scope.get("u_v_arbitrary_nonnegative") is True
        and rank1_su3_scope.get("arbitrary_real_Phi") is False
        and rank1_su3_scope.get("arbitrary_max_negative_Sigma") is False
        and rank1_su3_scope.get("G3_closed") is False
        and rank1_su3_scope.get("whole_model_excluded") is False
        and all(
            rank1_su3_checks.get(name) is True
            for name in rank1_required_checks
        )
        and rank1_su3_checks.get("arbitrary_rank1_Phi_proved") is False
        and rank1_su3_checks.get("arbitrary_Sigma35_proved") is False
        and rank1_su3_checks.get("G3_closed") is False
        and su5_max_negative_rank1_su3_slice_report.get("SOS", {}).get(
            "strict_anchor_lower_bound"
        )
        == "3/200"
        and su5_max_negative_rank1_su3_slice_report.get("radial_patch", {}).get(
            "restricted_global_minimum"
        )
        == "1/5000"
    )
    rank1_su4_stabilizer_infrastructure_exact = (
        _rank1_su4_stabilizer_infrastructure_exact(rank1_su4_stabilizer_report)
    )
    rank1_su4_phi210_intertwiners_exact = (
        _rank1_su4_phi210_intertwiners_exact(
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_stabilizer_report,
        )
    )
    rank1_su4_aligned_carriers_exact = _rank1_su4_aligned_carriers_exact(
        rank1_su4_aligned_carriers_report,
        rank1_su4_phi210_intertwiners_report,
        rank1_su4_stabilizer_report,
    )
    rank1_su4_phi210_quadratic_basis_exact = (
        _rank1_su4_phi210_quadratic_basis_exact(
            rank1_su4_phi210_quadratic_basis_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
        )
    )
    rank1_su4_augmented_sos_census_exact = (
        _rank1_su4_augmented_sos_census_exact(
            rank1_su4_augmented_sos_census_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
            rank1_su4_phi210_quadratic_basis_report,
        )
    )
    rank1_su4_augmented_sos_cubic_map_exact = (
        _rank1_su4_augmented_sos_cubic_map_exact(
            rank1_su4_augmented_sos_cubic_map_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
            rank1_su4_phi210_quadratic_basis_report,
            rank1_su4_augmented_sos_census_report,
        )
    )
    rank1_su4_augmented_sos_quartic_map_exact = (
        rank1_su4_augmented_sos_census_exact
        and rank1_su4_augmented_sos_cubic_map_exact
        and _rank1_su4_augmented_sos_quartic_map_exact(
            rank1_su4_augmented_sos_quartic_map_report,
            rank1_su4_augmented_sos_census_report,
            rank1_su4_augmented_sos_cubic_map_report,
        )
    )
    rank1_su4_legacy_psd_routes_and_stale_payload_well_formed = (
        rank1_su4_augmented_sos_quartic_map_exact
        and _rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
            rank1_su4_augmented_sos_psd_target_report,
            rank1_su4_augmented_sos_census_report,
            rank1_su4_augmented_sos_cubic_map_report,
            rank1_su4_augmented_sos_quartic_map_report,
        )
    )
    alternative_global_sos_honestly_open = bool(
        alternative_global_sos_report.get("n_failed") == 0
        and alternative_global_sos_report.get("status")
        == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
        and alternative_global_sos_report.get("overall_state")
        == "G3_GLOBAL_ALTERNATIVE_OPEN"
        and alternative_flags.get(
            "all_vanishing_45_current_Gram_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "all_vanishing_affine_SOS_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "all_vanishing_unique_chiral_quartic_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "nonvanishing_residual_gradient_cancellation_excluded"
        )
        is False
        and alternative_flags.get("different_vacuum_orbit_excluded") is False
        and alternative_flags.get("globally_certifiable_alternative_found") is False
        and alternative_flags.get("current_candidate_global_minimum_certified")
        is False
        and alternative_flags.get("G3_closed") is False
        and alternative_flags.get("whole_model_excluded") is False
    )
    integrity_pass = bool(
        all(artifacts_present.values())
        and a_square_exact
        and sos_bfb_exact
        and pd_direct_and_fail_closed
        and sos_exact_local_and_globally_rejected
        and fixed_p_no_go_exact
        and replacement_wrong_symmetry
        and su5_pd_exact_frontier
        and su5_hsx_honest_frontier
        and su5_hsx_exact_hessian_closed
        and su5_equality_honestly_reduced
        and su5_phi_orbit_audit_honest
        and su5_phi_local_components_closed
        and su5_phi_su3_slice_closed
        and su5_chiral_gap_honestly_reduced
        and su5_fixed_f_full_gap_closed
        and su5_max_negative_all_zero_route_excluded
        and su5_max_negative_full_residual_pure_delta_closed
        and su5_max_negative_rank1_su3_slice_closed
        and rank1_su4_stabilizer_infrastructure_exact
        and rank1_su4_phi210_intertwiners_exact
        and rank1_su4_aligned_carriers_exact
        and rank1_su4_phi210_quadratic_basis_exact
        and rank1_su4_augmented_sos_census_exact
        and rank1_su4_augmented_sos_cubic_map_exact
        and rank1_su4_augmented_sos_quartic_map_exact
        and rank1_su4_legacy_psd_routes_and_stale_payload_well_formed
        and rank1_su4_corrected_exact
        and alternative_global_sos_honestly_open
    )
    return {
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "overall_state": STATUS_OPEN if integrity_pass else "EXECUTION_FAIL",
        "artifacts_present": artifacts_present,
        "integrity_pass": integrity_pass,
        "exact_A_square_recoupling_source_bound": a_square_exact,
        "exact_SOS_BFB_stationarity_source_bound": sos_bfb_exact,
        "direct_exact_PD_rank_honestly_scoped": pd_direct_and_fail_closed,
        "SOS_candidate_exact_local_and_globally_rejected": (
            sos_exact_local_and_globally_rejected
        ),
        "fixed_P_branch_exactly_excluded": fixed_p_no_go_exact,
        "lower_replacement_rejected_for_wrong_symmetry": replacement_wrong_symmetry,
        "SU5_Delta_PD_exact_global_frontier": su5_pd_exact_frontier,
        "SU5_Delta_PD_exact_Hessian_rank": 429
        if su5_pd_exact_frontier
        else None,
        "SU5_Delta_PD_exact_Hessian_nullity": 33
        if su5_pd_exact_frontier
        else None,
        "SU5_Delta_PD_full_486_extension_open": not bool(
            su5_scope.get("full_486_field_stationarity")
        ),
        "SU5_Delta_PD_disconnected_equality_orbits_open": not bool(
            equality_scope.get("global_equality_orbit_classification_complete")
        ),
        "SU5_Delta_PD_equality_orbits_classified_exactly": bool(
            equality_scope.get("global_equality_orbit_classification_complete")
        ),
        "SU5_Delta_HSX_honest_frontier": su5_hsx_honest_frontier,
        "SU5_Delta_HSX_nonzero_real_parameters": (
            su5_hsx_report.get("coefficient_map", {}).get("nonzero_count")
        ),
        "SU5_Delta_HSX_maximum_absolute_coefficient": (
            su5_hsx_report.get("coefficient_map", {}).get(
                "maximum_absolute_coefficient"
            )
        ),
        "SU5_Delta_HSX_exact_symmetry_ranks": [
            hsx_orbit.get("SO10_rank"),
            hsx_orbit.get("SO10_plus_U1X_rank"),
            hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank"),
        ],
        "SU5_Delta_HSX_transverse_dimension": hsx_hessian.get(
            "transverse_dimension"
        ),
        "SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric": hsx_hessian.get(
            "minimum_transverse_eigenvalue"
        ),
        "SU5_Delta_HSX_full_Hessian_proof_grade": hsx_hessian.get("proof_grade"),
        "SU5_Delta_HSX_exact_Hessian_closed": su5_hsx_exact_hessian_closed,
        "SU5_Delta_HSX_exact_Hessian_rank": 448
        if su5_hsx_exact_hessian_closed
        else None,
        "SU5_Delta_HSX_exact_Hessian_nullity": 38
        if su5_hsx_exact_hessian_closed
        else None,
        "SU5_Delta_HSX_exact_Hessian_PSD": hsx_exact_flags.get("exact_PSD"),
        "SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry": hsx_exact_flags.get(
            "kernel_equals_38_symmetry_tangents"
        ),
        "SU5_Delta_HSX_exact_quotient_positive": hsx_exact_flags.get(
            "strict_quotient_positive"
        ),
        "SU5_Delta_HSX_full_quartic_BFB_exact": hsx_global.get(
            "full_homogeneous_quartic_BFB_exact"
        ),
        "SU5_Delta_HSX_finite_field_global_gap_open": not bool(
            hsx_global.get("beta_deformed_finite_field_global_gap_exact")
        ),
        "SU5_Delta_HSX_global_equality_classification_open": not bool(
            hsx_global.get("global_equality_orbits_classified")
        ),
        "SU5_Delta_equality_honestly_reduced": su5_equality_honestly_reduced,
        "SU5_Delta_Phi_orbit_audit_honest": su5_phi_orbit_audit_honest,
        "SU5_Delta_literal_single_Phi_orbit_refuted": phi_orbit_scope.get(
            "literal_plus_orbit_only_statement_refuted"
        ),
        "SU5_Delta_signed_Phi_orbit_theorem_open": not bool(
            equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        ),
        "SU5_Delta_signed_Phi_orbit_theorem_closed": bool(
            equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        ),
        "SU5_Delta_SU4_Phi_slice_classified": phi_orbit_scope.get(
            "complete_SU4_invariant_slice_classified"
        ),
        "SU5_Delta_signed_Phi_local_components_closed": (
            su5_phi_local_components_closed
        ),
        "SU5_Delta_distant_Phi_components_excluded": equality_scope.get(
            "distant_disconnected_Phi_components_excluded"
        ),
        "SU5_Delta_Phi_SU3_fixed_slice_closed": su5_phi_su3_slice_closed,
        "SU5_Delta_Phi_SU3_fixed_slice_dimension": 16
        if su5_phi_su3_slice_closed
        else None,
        "SU5_Delta_fixed_F_Sigma_one_orbit_exact": equality_scope.get(
            "fixed_F_Sigma_global_equality_classified"
        ),
        "SU5_Delta_diagonal_Phi_slice_one_orbit_exact": equality_scope.get(
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        ),
        "SU5_Delta_global_Phi_orbit_lemma_open": not bool(
            equality_lemma.get("proved")
        ),
        "SU5_Delta_global_Phi_orbit_lemma_closed": bool(
            equality_lemma.get("proved")
        ),
        "SU5_Delta_global_Phi_orbit_theorem_core_sha256": equality_global.get(
            "core_sha256"
        ),
        "SU5_Delta_global_Phi_orbit_external_dependency": equality_global.get(
            "external_theorem_dependency", {}
        ).get("theorem"),
        "SU5_Delta_global_Phi_orbit_lemma": equality_lemma.get("statement"),
        "SU5_Delta_chiral_global_gap_honestly_reduced": (
            su5_chiral_gap_honestly_reduced
        ),
        "SU5_Delta_chiral_lower_witness_found": gap_flags.get(
            "lower_witness_found"
        ),
        "SU5_Delta_chiral_small_beta_route_exists": gap_flags.get(
            "conditional_small_positive_beta_route_exists"
        ),
        "SU5_Delta_chiral_beta_1_over_20_global_certified": gap_flags.get(
            "beta_1_over_20_global_minimum_certified"
        ),
        "SU5_Delta_chiral_final_acceptance_test_passes": gap_acceptance.get(
            "currently_passes"
        ),
        "SU5_fixed_F_full_offkernel_gap_closed": su5_fixed_f_full_gap_closed,
        "SU5_fixed_F_gap_equality_is_selected_flag": fixed_f_offkernel_scope.get(
            "equality_is_selected_SU5_flag_orbit"
        ),
        "SU5_arbitrary_Phi_offstratum_gap_open": not bool(
            fixed_f_offkernel_scope.get("arbitrary_Phi_proved")
        ),
        "SU5_max_negative_all_zero_residual_route_excluded": (
            su5_max_negative_all_zero_route_excluded
        ),
        "SU5_max_negative_all_zero_residual_strict_margin": (
            su5_max_negative_zero_residual_report.get("exact_stratum_gap", {}).get(
                "strict_margin"
            )
        ),
        "SU5_max_negative_pure_Delta_full_residual_gap_closed": (
            su5_max_negative_full_residual_pure_delta_closed
        ),
        "SU5_max_negative_pure_Delta_full_residual_minimum": (
            max_negative_full_scope.get("restricted_gap_global_minimum")
        ),
        "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed": (
            su5_max_negative_rank1_su3_slice_closed
        ),
        "SU5_max_negative_rank1_SU3_slice_dimension": rank1_su3_scope.get(
            "Phi_slice_real_dimension"
        ),
        "SU5_max_negative_rank1_SU3_ambient_dimension": rank1_su3_scope.get(
            "full_SU3_fixed_space_real_dimension"
        ),
        "SU5_max_negative_rank1_SU3_slice_minimum": (
            su5_max_negative_rank1_su3_slice_report.get("radial_patch", {}).get(
                "restricted_global_minimum"
            )
        ),
        "SU5_max_negative_arbitrary_rank1_Phi_open": not bool(
            rank1_su3_checks.get("arbitrary_rank1_Phi_proved")
        ),
        "rank1_SU4_stabilizer_infrastructure_exact": (
            rank1_su4_stabilizer_infrastructure_exact
        ),
        "rank1_SU4_joint_stabilizer_dimension": (
            rank1_su4_stabilizer_report.get("joint_stabilizer_tangent", {}).get(
                "exact_tangent_nullity"
            )
        ),
        "rank1_SU4_Phi210_intertwiner_infrastructure_exact": (
            rank1_su4_phi210_intertwiners_exact
        ),
        "rank1_SU4_Phi210_carrier_count": (
            rank1_su4_phi210_intertwiners_report.get("carriers", {}).get(
                "carrier_count"
            )
        ),
        "rank1_SU4_Sym2_invariant_dimension": (
            rank1_su4_phi210_intertwiners_report.get("carriers", {}).get(
                "Sym2_Phi210_SU4_singlet_dimension"
            )
        ),
        "rank1_SU4_aligned_carriers_exact": rank1_su4_aligned_carriers_exact,
        "rank1_SU4_aligned_direct_sum_rank": (
            rank1_su4_aligned_carriers_report.get("alignment", {}).get(
                "concatenated_aligned_basis_rank_mod_prime"
            )
        ),
        "rank1_SU4_physical_real_maps_exact": bool(
            rank1_su4_aligned_scope.get(
                "physical_real_structure_and_Gaussian_embeddings_constructed"
            )
            is True
        ),
        "rank1_SU4_Phi210_quadratic_basis_exact": (
            rank1_su4_phi210_quadratic_basis_exact
        ),
        "rank1_SU4_quadratic_constraint_shape": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("reduced_constraint_shape")
        ),
        "rank1_SU4_quadratic_constraint_rank": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("exact_rational_rank")
        ),
        "rank1_SU4_quadratic_constraint_nullity": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("exact_rational_nullity")
        ),
        "rank1_SU4_quadratic_basis_count": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("matrix_count")
        ),
        "rank1_SU4_quadratic_basis_rank": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("upper_triangle_column_rank_mod_prime")
        ),
        "rank1_SU4_quadratic_live_invariance_exact": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("all_45_commute_with_all_15_live_Phi210_generators_exact")
        ),
        "rank1_SU4_Schur_SOS_SDP_open": (
            rank1_su4_quadratic_scope.get(
                "augmented_homogeneous_Schur_SOS_SDP_constructed"
            )
            is False
        ),
        "rank1_SU4_arbitrary_Phi_bound_open": (
            rank1_su4_quadratic_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_SOS_census_exact": (
            rank1_su4_augmented_sos_census_exact
        ),
        "rank1_SU4_augmented_homogeneous_dimension": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("augmented_homogeneous_dimension")
        ),
        "rank1_SU4_augmented_complex_isotypic_type_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_isotypic_type_count")
        ),
        "rank1_SU4_augmented_complex_irreducible_copy_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_irreducible_copy_count")
        ),
        "rank1_SU4_augmented_real_isotypic_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("real_isotypic_block_count")
        ),
        "rank1_SU4_augmented_real_symmetric_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("real_symmetric_block_count")
        ),
        "rank1_SU4_augmented_complex_Hermitian_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_Hermitian_block_count")
        ),
        "rank1_SU4_augmented_Schur_real_parameter_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("Schur_real_parameter_count")
        ),
        "rank1_SU4_augmented_invariant_equation_count": (
            rank1_su4_augmented_sos_census_report.get(
                "invariant_quartic_target", {}
            ).get("invariant_equation_count")
        ),
        "rank1_SU4_augmented_abstract_total_rank": (
            rank1_su4_augmented_sos_census_report.get(
                "abstract_coefficient_map_census", {}
            ).get("abstract_total_rank_exact")
        ),
        "rank1_SU4_augmented_abstract_total_kernel_dimension": (
            rank1_su4_augmented_sos_census_report.get(
                "abstract_coefficient_map_census", {}
            ).get("abstract_total_kernel_dimension_exact")
        ),
        "rank1_SU4_augmented_coordinate_Schur_map_open": (
            rank1_su4_census_scope.get(
                "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_isotypic_maps_open": (
            rank1_su4_census_scope.get(
                "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_physical_target_open": (
            rank1_su4_census_scope.get(
                "physical_G3_gap_target_vector_constructed"
            ) is False
            and rank1_su4_census_scope.get(
                "physical_G3_gap_cubic_zero_RHS_certified"
            ) is False
        ),
        "rank1_SU4_augmented_Schur_SOS_SDP_open": (
            rank1_su4_census_scope.get("augmented_Schur_SOS_SDP_constructed")
            is False
            and rank1_su4_census_scope.get(
                "augmented_Schur_SOS_SDP_feasibility_certified"
            ) is False
            and rank1_su4_census_scope.get(
                "augmented_Schur_SOS_SDP_infeasibility_certified"
            ) is False
        ),
        "rank1_SU4_augmented_arbitrary_Phi_bound_open": (
            rank1_su4_census_scope.get("arbitrary_real_Phi_lower_bound_proved")
            is False
            and rank1_su4_census_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_cubic_map_exact": (
            rank1_su4_augmented_sos_cubic_map_exact
        ),
        "rank1_SU4_augmented_cubic_carrier_copy_count": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "Sym2_target_carriers", {}
            ).get("total_complex_carrier_copy_count")
        ),
        "rank1_SU4_augmented_cubic_real_variable_count": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "physical_cubic_domain", {}
            ).get("physical_basis_count")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_shape": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("coordinate_map_shape")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_nnz": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("coordinate_map_nnz")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_rank": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("exact_rank")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("exact_kernel_dimension")
        ),
        "rank1_SU4_augmented_cubic_zero_placeholder_nonphysical": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("abstract_zero_placeholder_is_not_a_physical_G3_target")
            is True
            and rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("physical_G3_gap_target_vector_constructed") is False
            and rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("physical_G3_gap_cubic_zero_RHS_certified") is False
        ),
        "rank1_SU4_augmented_cubic_other_graded_maps_open": all(
            rank1_su4_cubic_scope.get(name) is False
            for name in (
                "degree_zero_coefficient_map_constructed",
                "degree_one_coefficient_map_constructed",
                "degree_two_coefficient_map_constructed",
                "degree_four_coefficient_map_constructed",
            )
        ),
        "rank1_SU4_augmented_cubic_full_coordinate_map_open": (
            rank1_su4_cubic_scope.get(
                "full_6585_by_19594_Schur_coordinate_matrix_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_cubic_physical_target_open": (
            rank1_su4_cubic_scope.get(
                "physical_G3_gap_target_vector_constructed"
            ) is False
            and rank1_su4_cubic_scope.get(
                "physical_G3_gap_cubic_zero_RHS_certified"
            ) is False
        ),
        "rank1_SU4_augmented_cubic_Schur_SOS_SDP_open": all(
            rank1_su4_cubic_scope.get(name) is False
            for name in (
                "augmented_Schur_SOS_SDP_constructed",
                "augmented_Schur_SOS_SDP_feasibility_certified",
                "augmented_Schur_SOS_SDP_infeasibility_certified",
            )
        ),
        "rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open": (
            rank1_su4_cubic_scope.get("arbitrary_real_Phi_lower_bound_proved")
            is False
            and rank1_su4_cubic_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_cubic_G3_open": (
            rank1_su4_cubic_scope.get("G3_closed") is False
            and rank1_su4_cubic_scope.get("whole_model_validated") is False
            and rank1_su4_cubic_scope.get("whole_model_excluded") is False
        ),
        "rank1_SU4_augmented_quartic_map_exact": (
            rank1_su4_augmented_sos_quartic_map_exact
        ),
        "rank1_SU4_augmented_quartic_carrier_family_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("complex_isotypic_types")
        ),
        "rank1_SU4_augmented_quartic_irreducible_copy_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("irreducible_copies")
        ),
        "rank1_SU4_augmented_quartic_real_block_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("real_Schur_blocks")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_shape": (
            rank1_su4_quartic_map.get("shape")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_nnz": (
            rank1_su4_quartic_map.get("nnz")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_rank": (
            rank1_su4_quartic_map.get("rank_over_Q_exact")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension": (
            rank1_su4_quartic_map.get("kernel_dimension_over_Q_exact")
        ),
        "rank1_SU4_augmented_quartic_physical_target_open": (
            rank1_su4_quartic_scope.get("physical_quartic_target_constructed")
            is False
        ),
        "rank1_SU4_augmented_quartic_standard_PSD_congruences_open": (
            rank1_su4_quartic_scope.get(
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_quartic_SDP_open": (
            rank1_su4_quartic_scope.get("semidefinite_feasibility_solved")
            is False
        ),
        "rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open": (
            rank1_su4_quartic_scope.get(
                "arbitrary_Phi_stationarity_or_lower_bound_proved"
            ) is False
        ),
        "rank1_SU4_augmented_quartic_G3_open": (
            rank1_su4_quartic_scope.get("G3_closed") is False
        ),
        "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed": (
            rank1_su4_legacy_psd_routes_and_stale_payload_well_formed
        ),
        "rank1_SU4_legacy_v20_physical_target_valid": False,
        "rank1_SU4_legacy_v20_primal_valid": False,
        "rank1_SU4_augmented_standard_PSD_route_count": (
            rank1_su4_psd_routes.get("real_type_block_count", 0)
            + rank1_su4_psd_routes.get("complex_Hermitian_block_count", 0)
        ),
        "rank1_SU4_augmented_standard_PSD_parameter_count": (
            rank1_su4_psd_routes.get("standard_total_parameter_count")
        ),
        "rank1_SU4_augmented_real_type_PSD_congruences_exact": (
            rank1_su4_psd_target_scope.get(
                "all_nine_real_type_standard_PSD_congruences_constructed"
            ) is True
        ),
        "rank1_SU4_augmented_complex_Hermitian_coordinates_exact": (
            rank1_su4_psd_target_scope.get(
                "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates"
            ) is True
        ),
        "rank1_SU4_corrected_fixed_endpoint_theorem_exact": (
            rank1_su4_corrected_exact
        ),
        "rank1_SU4_corrected_publication_manifest_sha256": (
            rank1_su4_corrected_view.get("publication_manifest_raw_sha256")
        ),
        "rank1_SU4_corrected_positive_Gram_map_shape": (
            rank1_su4_corrected_view.get("map_shape")
        ),
        "rank1_SU4_corrected_positive_Gram_map_common_denominator": (
            rank1_su4_corrected_view.get("map_common_denominator")
        ),
        "rank1_SU4_corrected_positive_Gram_map_nnz": (
            rank1_su4_corrected_view.get("map_nnz")
        ),
        "rank1_SU4_corrected_positive_Gram_map_sha256": (
            rank1_su4_corrected_view.get("map_numerator_csr_sha256")
        ),
        "rank1_SU4_corrected_physical_target_common_denominator": (
            rank1_su4_corrected_view.get("target_common_denominator")
        ),
        "rank1_SU4_corrected_physical_target_nonzero_count": (
            rank1_su4_corrected_view.get("target_nonzero_count")
        ),
        "rank1_SU4_corrected_physical_target_sha256": (
            rank1_su4_corrected_view.get("target_numerator_sha256")
        ),
        "rank1_SU4_corrected_exact_coefficient_equalities": (
            rank1_su4_corrected_view.get("exact_coefficient_equalities")
        ),
        "rank1_SU4_corrected_strict_positive_Gram_blocks": (
            rank1_su4_corrected_view.get("strict_positive_Gram_blocks")
        ),
        "rank1_SU4_corrected_strict_positive_LDL_pivots": (
            rank1_su4_corrected_view.get("strict_positive_LDL_pivots")
        ),
        "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint": (
            rank1_su4_corrected_view.get(
                "arbitrary_real_Phi_at_fixed_endpoint"
            )
        ),
        "rank1_SU4_corrected_strict_positive_off_homogeneous_origin": (
            rank1_su4_corrected_view.get(
                "strict_positive_off_homogeneous_origin"
            )
        ),
        "rank1_SU4_corrected_A_greater_than_3_over_200_at_t1": (
            rank1_su4_corrected_view.get("A_greater_than_3_over_200_at_t1")
        ),
        "rank1_SU4_corrected_p_zero_set_at_t1_empty": (
            rank1_su4_corrected_view.get("p_zero_set_at_t1_empty")
        ),
        "rank1_SU4_corrected_global_Sigma_proved": (
            rank1_su4_corrected_view.get("global_Sigma_proved")
        ),
        "rank1_SU4_corrected_general_H_proved": (
            rank1_su4_corrected_view.get("general_H_proved")
        ),
        "rank1_SU4_corrected_full_H_proved": (
            rank1_su4_corrected_view.get("full_H_proved")
        ),
        "rank1_SU4_corrected_full_Hessian_proved": (
            rank1_su4_corrected_view.get("full_Hessian_proved")
        ),
        "rank1_SU4_corrected_G3_closed": (
            rank1_su4_corrected_view.get("G3_closed")
        ),
        "SU5_max_negative_arbitrary_Sigma_orientation_open": not bool(
            rank1_su3_scope.get("arbitrary_max_negative_Sigma")
        ),
        "SU5_arbitrary_Phi_nonzero_residual_cancellations_open": not bool(
            max_negative_full_scope.get("nonzero_Phi_Sigma_residuals_covered")
            and max_negative_full_scope.get(
                "nonzero_chiral_Phi_H_residual_covered"
            )
        ),
        "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open": not bool(
            max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        ),
        "SU5_arbitrary_Phi_uniform_coercivity_open": not bool(
            max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        ),
        "alternative_global_SOS_audit_honestly_open": (
            alternative_global_sos_honestly_open
        ),
        "all_vanishing_global_SOS_replacements_excluded": bool(
            alternative_flags.get(
                "all_vanishing_45_current_Gram_completion_excluded"
            )
            and alternative_flags.get(
                "all_vanishing_affine_SOS_completion_excluded"
            )
            and alternative_flags.get(
                "all_vanishing_unique_chiral_quartic_completion_excluded"
            )
        ),
        "nonvanishing_residual_global_SOS_replacements_excluded": (
            alternative_flags.get(
                "nonvanishing_residual_gradient_cancellation_excluded"
            )
        ),
        "candidate_nonzero_real_parameters": coefficients.get("nonzero_count"),
        "candidate_real_parameter_count": 51,
        "candidate_maximum_absolute_coefficient": coefficients.get(
            "maximum_absolute_coefficient"
        ),
        "candidate_J0": symbolic.get(
            "lambda::O48_B01_Phi_self_quartics"
        ),
        "exact_PD_rank": pd_core.get("rank"),
        "exact_PD_nullity": pd_core.get("nullity"),
        "exact_full_Hessian_rank": pd_extension.get(
            "exact_full_Hessian_rank"
        ),
        "direct_exact_PD_source_binding": pd_flags.get(
            "direct_exact_source_binding"
        ),
        "complete_potential_BFB_exactly_certified": sos_flags.get(
            "complete_potential_BFB_exactly_certified"
        ),
        "strict_local_minimum_certified": sos_flags.get(
            "strict_local_minimum_certified"
        ),
        "selected_vacuum_stationarity_exactly_certified": sos_flags.get(
            "selected_vacuum_stationarity_exactly_compiler_certified"
        ),
        "global_minimum_certified": sos_flags.get(
            "selected_vacuum_global_minimum_certified"
        ),
        "selected_global_minimum_disproved": sos_flags.get(
            "selected_vacuum_global_minimum_disproved"
        ),
        "exact_lower_energy_field_witness_certified": sos_flags.get(
            "exact_lower_energy_field_witness_certified"
        ),
        "constructive_candidate_rejected_for_G3": sos_flags.get(
            "constructive_candidate_rejected_for_G3"
        ),
        "global_uniqueness_certified": sos_flags.get(
            "selected_vacuum_unique_modulo_symmetry"
        ),
        "G3_closed": sos_flags.get("G3_closed"),
        "whole_model_validated": sos_flags.get("whole_model_validated"),
        "whole_model_excluded": sos_flags.get("whole_model_excluded"),
        "remaining_exact_step": pd_report.get("next_exact_step"),
    }


def _gauged_u1x_scalar_subtheorems(
    g1_report: dict[str, Any],
    g1_component_tensor_closure: dict[str, Any],
    g2_report: dict[str, Any],
    g2_mathematical_closure: dict[str, Any],
    *,
    contract_consistent: bool,
) -> dict[str, Any]:
    """Expose completed scalar calculations without closing whole-model gates."""
    g1_closure = g1_report.get("closure", {})
    g1_flags = g1_report.get("flags", {})
    g1_multiplicity_census_complete = bool(
        g1_report.get("n_failed") == 0
        and g1_closure.get(
            "declared_symmetry_charge_multidegrees_degree_le_4_closed"
        )
        is True
        and g1_closure.get("so10_singlet_multiplicities_degree_le_4_closed")
        is True
        and g1_closure.get("gauged_u1x_44_direction_subcensus_closed") is True
        and g1_flags.get("renormalizable_G1_multiplicity_census_closed") is True
    )
    g1_component_tensors_complete = bool(
        g1_component_tensor_closure.get("source_bound") is True
        and g1_component_tensor_closure.get(
            "mathematical_G1_closed_for_renormalizable_model"
        )
        is True
        and g1_component_tensor_closure.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and g1_component_tensor_closure.get("direction_map_sha256")
        == RENORMALIZABLE_G1_DIRECTION_MAP_SHA256
    )
    full_g1_closed = bool(
        g1_multiplicity_census_complete
        and g1_component_tensors_complete
    )
    g2_scoped_audit_complete = bool(
        g2_report.get("n_failed") == 0
        and g2_report.get("flags", {}).get("G2_gauged_u1x_derivatives_certified")
        is True
    )
    full_g2_mathematical_closed = bool(
        full_g1_closed
        and g2_scoped_audit_complete
        and g2_mathematical_closure.get("source_bound") is True
        and g2_mathematical_closure.get(
            "mathematical_G2_closed_for_renormalizable_model"
        )
        is True
        and g2_mathematical_closure.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
    )
    stationary = g2_report["stationary_Hessian_bridge"][
        "promoted_stationarity_matrix"
    ]
    return {
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "scope": (
            "exact-X-neutral renormalizable scalar potential on the canonical "
            "486-real field chart"
        ),
        "whole_model_gate_closure": False,
        "promoted_to_authoritative_G1_G2": bool(
            contract_consistent and full_g2_mathematical_closed
        ),
        "blocked_only_from_promotion_by_model_contract_mismatch": (
            not contract_consistent and full_g1_closed
        ),
        "renormalizable_G1_component_tensor_closure": (
            g1_component_tensor_closure
        ),
        "renormalizable_G2_mathematical_closure": g2_mathematical_closure,
        "G1": {
            "scoped_status": (
                "COMPLETE_GAUGED_U1X_MULTIPLICITY_CENSUS__FULL_G1_OPEN"
                if g1_multiplicity_census_complete and not full_g1_closed
                else "COMPLETE_GAUGED_U1X_FULL_COMPONENT_TENSOR_INTEGRATION"
                if full_g1_closed
                else "GAUGED_U1X_MULTIPLICITY_CENSUS_INCOMPLETE"
            ),
            "multiplicity_census_complete": g1_multiplicity_census_complete,
            "explicit_component_tensor_subset_integration_complete": (
                g1_component_tensors_complete
            ),
            "mathematical_component_tensor_closure_complete": (
                g1_component_tensors_complete
            ),
            "character_census_remains_multiplicity_only": bool(
                g1_closure.get("explicit_component_tensor_subset_integration_closed")
                is False
                and g1_flags.get("g1_explicit_tensor_subset_reaudit_open") is True
                and g1_flags.get("g1_closed") is False
            ),
            "full_G1_closed": full_g1_closed,
            "full_renormalizable_G1_mathematical_ring_closed": full_g1_closed,
            "authoritative_G1_promoted_closed": bool(
                contract_consistent and full_g1_closed
            ),
            "release_G1_verified": bool(contract_consistent and full_g1_closed),
            "remaining_exact_target": (
                "CLOSED_ON_CURRENT_AUTHORITATIVE_CONTRACT"
                if contract_consistent and full_g1_closed
                else "Supply the hash-bound external SARAH v3 source-tree/runtime/log attestation."
                if full_g1_closed
                else "Restore the source-bound 44-direction component-tensor theorem."
            ),
            "hermitian_conjugacy_orbits": g1_report["counts"][
                "hermitian_conjugacy_orbits"
            ],
            "invariant_directions": g1_report["counts"][
                "total_potential_orbit_multiplicity"
            ],
            "real_potential_parameters": g1_report["counts"][
                "total_real_potential_parameters"
            ],
        },
        "G2": {
            "scoped_status": (
                "COMPLETE_GAUGED_U1X_FULL_MATHEMATICAL_COMPONENT_POTENTIAL"
                if full_g2_mathematical_closed
                else "COMPLETE_GAUGED_U1X_DENSE_DERIVATIVE_AUDIT__FULL_G2_OPEN"
                if g2_scoped_audit_complete
                else "GAUGED_U1X_DENSE_DERIVATIVE_AUDIT_INCOMPLETE"
            ),
            "scoped_derivative_audit_complete": g2_scoped_audit_complete,
            "mathematical_component_potential_closure_complete": (
                full_g2_mathematical_closed
            ),
            "full_renormalizable_G2_mathematical_potential_closed": (
                full_g2_mathematical_closed
            ),
            "authoritative_promotion_blocked_on_full_G1": not full_g1_closed,
            "authoritative_promotion_blocked_on_model_contract": (
                not contract_consistent
            ),
            "authoritative_promotion_ready_after_model_contract": bool(
                full_g2_mathematical_closed
            ),
            "authoritative_G2_promoted_closed": bool(
                contract_consistent and full_g2_mathematical_closed
            ),
            "release_G2_verified": bool(
                contract_consistent and full_g2_mathematical_closed
            ),
            "remaining_exact_target": (
                "CLOSED_ON_CURRENT_AUTHORITATIVE_CONTRACT"
                if contract_consistent and full_g2_mathematical_closed
                else "Supply the hash-bound external SARAH v3 source-tree/runtime/log attestation."
                if full_g2_mathematical_closed
                else "Restore the source-bound mathematical G2 closure theorem."
            ),
            "invariant_directions": g2_report["counts"]["invariant_directions"],
            "real_potential_parameters": g2_report["counts"]["real_parameters"],
            "real_field_dimension": g2_report["counts"]["real_field_dimension"],
            "gradient_entries_per_parameter": g2_report["counts"][
                "gradient_entries_per_parameter"
            ],
            "dense_Hessian_shape": g2_report["counts"][
                "Hessian_shape_per_parameter"
            ],
            "promoted_stationarity_rank": stationary["rank"],
            "promoted_stationarity_nullity": stationary["nullity"],
            "raw_dense_rank_14_certified": g2_report["flags"][
                "raw_dense_rank_14_is_certified"
            ],
            "exact_Delta_R_projector_zero_certificate": g2_report["flags"][
                "exact_Delta_R_projector_zero_certificate"
            ],
            "exact_projector_zero_corrected_normalized_SVD_rank_13": g2_report["flags"][
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            ],
            "stationarity_rank_13_exactly_certified": g2_report["flags"][
                "stationarity_rank_13_exactly_certified"
            ],
            "stationarity_nullity_38_exactly_certified": g2_report["flags"][
                "stationarity_nullity_38_exactly_certified"
            ],
            "G3_closed": g2_report["flags"]["G3_closed"],
        },
    }


def _expected_gate_statuses(
    contract_consistent: bool,
    *,
    g1_full_component_tensors_closed: bool = False,
    g2_scoped_derivatives_complete: bool = True,
) -> dict[str, str]:
    """Return the next scientifically honest frontier for the contract state."""
    if not contract_consistent:
        return {f"G{i}": STATUS_BLOCKED for i in range(1, 9)}
    g1_status = (
        STATUS_CLOSED if g1_full_component_tensors_closed else STATUS_OPEN
    )
    g2_status = (
        STATUS_CLOSED
        if g1_status == STATUS_CLOSED and g2_scoped_derivatives_complete
        else STATUS_OPEN
        if g1_status == STATUS_CLOSED
        else STATUS_BLOCKED
    )
    return {
        "G1": g1_status,
        "G2": g2_status,
        "G3": STATUS_OPEN if g2_status == STATUS_CLOSED else STATUS_BLOCKED,
        "G4": STATUS_BLOCKED,
        "G5": (
            STATUS_CLOSED
            if g1_status == STATUS_CLOSED and g2_status == STATUS_CLOSED
            else STATUS_BLOCKED
        ),
        "G6": STATUS_BLOCKED,
        "G7": STATUS_BLOCKED,
        "G8": STATUS_BLOCKED,
    }


def _build_gates(
    *,
    contract_consistent: bool,
    contract_blocker: str = CONTRACT_BLOCKER,
    scoped: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    specifications = {
        "G1": (
            "Invariant ring and component Clebsch tensors",
            [
                "obtain a real hash-bound external SARAH execution attestation for authoritative G1 promotion",
            ],
        ),
        "G2": (
            "Fully projected non-SUSY component potential",
            [
                "promote the source-bound complete mathematical 44/51/486 component potential after executable-contract repair",
            ],
        ),
        "G3": (
            "Stationarity and global vacuum",
            [
                "classify every competing stationary symmetry orbit and compare exact potential values",
                "prove global minimality and uniqueness, or exhibit a lower competing extremum",
            ],
        ),
        "G4": (
            "Gauge quotient, axion directions, and physical Hessian",
            [
                "carry the exact rank-37 gauge quotient (449, axion included) and rank-38 massive/transverse quotient (448) to an accepted G3 witness, recomputing if its stabilizer changes",
                "classify all remaining Hessian zero and negative modes at that witness",
            ],
        ),
        "G5": (
            "Boundedness from below",
            [
                "promote the completed source-bound SOS/BFB certificate after repairing the executable model contract"
            ],
        ),
        "G6": (
            "Physical threshold spectrum",
            ["await authoritative G3/G4/G5 and emit the complete positive spectrum"],
        ),
        "G7": (
            "Validated two-loop RGE and threshold matching",
            [
                "supply independent UV threshold data that make the exact EFT restriction map injective, then validate the complete gauged-X two-loop beta system"
            ],
        ),
        "G8": (
            "Proton-decay prediction and falsification",
            ["await authoritative G3/G6/G7 before any unique lifetime claim"],
        ),
    }
    g1_full_component_tensors_closed = bool(
        scoped and scoped["G1"]["full_G1_closed"] is True
    )
    g2_full_mathematical_potential_closed = bool(
        scoped
        and scoped["G2"].get(
            "full_renormalizable_G2_mathematical_potential_closed", False
        )
        is True
    )
    statuses = _expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_full_mathematical_potential_closed,
    )
    gates: dict[str, dict[str, Any]] = {}
    for name, (title, open_scope) in specifications.items():
        status = statuses[name]
        unsatisfied = [
            dependency
            for dependency in DEPENDENCIES[name]
            if (
                dependency == "MODEL_CONTRACT" and not contract_consistent
            ) or (
                dependency != "MODEL_CONTRACT"
                and statuses.get(dependency) != STATUS_CLOSED
            )
        ]
        if status == STATUS_BLOCKED:
            blocking_root = (
                contract_blocker
                if not contract_consistent
                else "DEPENDENCY_NOT_CLOSED"
            )
        else:
            blocking_root = None
        gates[name] = {
            "status": status,
            "authoritative_model_contract_id": AUTHORITATIVE_CONTRACT_ID,
            "blocking_root": blocking_root,
            "unsatisfied_dependencies": unsatisfied,
            "closed_on_current_authoritative_contract": status == STATUS_CLOSED,
            "closure_route_defined": True,
            "title": title,
            "dependencies": list(DEPENDENCIES[name]),
            "authoritative_closed_scope": (
                [
                    "promoted exact-X multiplicity census and explicit component Clebsch tensors"
                    if name == "G1"
                    else (
                        "promoted exact-X dense derivative and Ward audit"
                        if name == "G2"
                        else "source-bound complete-potential SOS/BFB certificate"
                    )
                ]
                if status == STATUS_CLOSED
                else []
            ),
            "open_scope": [] if status == STATUS_CLOSED else open_scope,
            "historical_option_c_evidence_retained": name in {"G1", "G2", "G3", "G4"},
        }
        if scoped is not None and name in {"G1", "G2"}:
            gates[name]["scoped_calculation_status"] = scoped[name]["scoped_status"]
            gates[name]["scoped_calculation_complete"] = bool(
                scoped[name].get(
                    "multiplicity_census_complete"
                    if name == "G1"
                    else "scoped_derivative_audit_complete"
                )
            )
            gates[name]["full_gate_calculation_complete"] = bool(
                scoped[name].get("full_G1_closed")
                if name == "G1"
                else scoped[name].get(
                    "full_renormalizable_G2_mathematical_potential_closed"
                )
            )
            gates[name]["scoped_calculation_evidence"] = scoped[name]
    return gates


def _build_report_from_inputs(
    *,
    x_report: dict[str, Any],
    g1_report: dict[str, Any],
    g2_report: dict[str, Any],
    filter_report: dict[str, Any],
    g1_component_tensor_report: dict[str, Any] | None = None,
    g1_component_tensor_raw_sha256: str | None = None,
    g1_component_tensor_source_raw_sha256: str | None = None,
    g2_mathematical_report: dict[str, Any] | None = None,
    g2_mathematical_raw_sha256: str | None = None,
    g2_mathematical_source_raw_sha256: str | None = None,
    g3_sos_report: dict[str, Any] | None = None,
    g3_pd_report: dict[str, Any] | None = None,
    g3_a_square_report: dict[str, Any] | None = None,
    g3_sos_bfb_report: dict[str, Any] | None = None,
    g3_kernel_bound_report: dict[str, Any] | None = None,
    g3_replacement_report: dict[str, Any] | None = None,
    g3_su5_pd_report: dict[str, Any] | None = None,
    g3_su5_hsx_report: dict[str, Any] | None = None,
    g3_su5_hsx_exact_hessian_report: dict[str, Any] | None = None,
    g3_su5_equality_report: dict[str, Any] | None = None,
    g3_su5_phi_orbit_report: dict[str, Any] | None = None,
    g3_su5_phi_local_component_report: dict[str, Any] | None = None,
    g3_su5_phi_su3_slice_report: dict[str, Any] | None = None,
    g3_su5_gap_report: dict[str, Any] | None = None,
    g3_su5_fixed_f_offkernel_report: dict[str, Any] | None = None,
    g3_su5_max_negative_zero_residual_report: dict[str, Any] | None = None,
    g3_su5_max_negative_full_residual_report: dict[str, Any] | None = None,
    g3_su5_max_negative_rank1_su3_slice_report: dict[str, Any] | None = None,
    g3_rank1_su4_stabilizer_report: dict[str, Any] | None = None,
    g3_rank1_su4_phi210_intertwiners_report: dict[str, Any] | None = None,
    g3_rank1_su4_aligned_carriers_report: dict[str, Any] | None = None,
    g3_rank1_su4_phi210_quadratic_basis_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_census_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_cubic_map_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_quartic_map_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_psd_target_report: dict[str, Any] | None = None,
    g3_rank1_su4_corrected_publication: dict[str, Any] | None = None,
    g3_alternative_global_sos_report: dict[str, Any] | None = None,
    final_g3_eft_acceptance_report: dict[str, Any] | None = None,
    final_g3_eft_acceptance_raw_sha256: str | None = None,
    final_g4_eft_mathematical_report: dict[str, Any] | None = None,
    final_g4_eft_mathematical_raw_sha256: str | None = None,
    final_g5_eft_mathematical_report: dict[str, Any] | None = None,
    final_g5_eft_mathematical_raw_sha256: str | None = None,
    final_g6_eft_mathematical_report: dict[str, Any] | None = None,
    final_g6_eft_mathematical_raw_sha256: str | None = None,
    final_g6_eft_gate_source_raw_sha256: str | None = None,
    g6_sm_provenance_report: dict[str, Any] | None = None,
    g6_sm_provenance_raw_sha256: str | None = None,
    g6_sm_provenance_source_raw_sha256: str | None = None,
    g6_g7_parameterized_matching_report: dict[str, Any] | None = None,
    g6_g7_parameterized_matching_raw_sha256: str | None = None,
    g6_g7_parameterized_matching_source_raw_sha256: str | None = None,
    authoritative_gauge_betas_report: dict[str, Any] | None = None,
    authoritative_gauge_betas_raw_sha256: str | None = None,
    authoritative_gauge_betas_source_raw_sha256: str | None = None,
    pyrate3_gauge_replay_report: dict[str, Any] | None = None,
    pyrate3_gauge_replay_raw_sha256: str | None = None,
    pyrate3_gauge_replay_source_raw_sha256: str | None = None,
    pyrate3_gauge_replay_model_raw_sha256: str | None = None,
    pyrate3_gauge_replay_data_raw_sha256: str | None = None,
    eft_g7_nonidentifiability_report: dict[str, Any] | None = None,
    eft_g7_nonidentifiability_raw_sha256: str | None = None,
    eft_g7_nonidentifiability_source_raw_sha256: str | None = None,
    physical_g7_component_threshold_report: dict[str, Any] | None = None,
    physical_g7_component_threshold_raw_sha256: str | None = None,
    physical_g7_component_threshold_source_raw_sha256: str | None = None,
    physical_g7_component_threshold_test_raw_sha256: str | None = None,
    physical_g7_component_threshold_markdown_raw_sha256: str | None = None,
    normalized_yukawa_cgcs_report: dict[str, Any] | None = None,
    normalized_yukawa_cgcs_raw_sha256: str | None = None,
    normalized_yukawa_cgcs_source_raw_sha256: str | None = None,
    normalized_yukawa_cgcs_test_raw_sha256: str | None = None,
    normalized_yukawa_cgcs_markdown_raw_sha256: str | None = None,
    physical_sm_vacuum_report: dict[str, Any] | None = None,
    physical_sm_vacuum_raw_sha256: str | None = None,
    physical_sm_vacuum_source_raw_sha256: str | None = None,
    physical_sm_vacuum_test_raw_sha256: str | None = None,
    physical_sm_vacuum_markdown_raw_sha256: str | None = None,
    physical_sm_heavy_vector_report: dict[str, Any] | None = None,
    physical_sm_heavy_vector_raw_sha256: str | None = None,
    physical_sm_heavy_vector_source_raw_sha256: str | None = None,
    physical_sm_heavy_vector_test_raw_sha256: str | None = None,
    physical_sm_heavy_vector_markdown_raw_sha256: str | None = None,
    physical_sm_heavy_vector_msbar_report: dict[str, Any] | None = None,
    physical_sm_heavy_vector_msbar_raw_sha256: str | None = None,
    physical_sm_heavy_vector_msbar_source_raw_sha256: str | None = None,
    physical_sm_heavy_vector_msbar_test_raw_sha256: str | None = None,
    physical_sm_heavy_vector_msbar_markdown_raw_sha256: str | None = None,
    physical_sm_vector_rxi_report: dict[str, Any] | None = None,
    physical_sm_vector_rxi_raw_sha256: str | None = None,
    physical_sm_vector_rxi_source_raw_sha256: str | None = None,
    physical_sm_vector_rxi_test_raw_sha256: str | None = None,
    physical_sm_vector_rxi_markdown_raw_sha256: str | None = None,
    conditional_physical_sm_scalar_spectrum_report: dict[str, Any] | None = None,
    conditional_physical_sm_scalar_spectrum_raw_sha256: str | None = None,
    conditional_physical_sm_scalar_spectrum_source_raw_sha256: str | None = None,
    conditional_physical_sm_scalar_spectrum_test_raw_sha256: str | None = None,
    conditional_physical_sm_scalar_spectrum_markdown_raw_sha256: str | None = None,
    physical_sm_g6_g7_frontier_report: dict[str, Any] | None = None,
    physical_sm_g6_g7_frontier_raw_sha256: str | None = None,
    physical_sm_g6_g7_frontier_source_raw_sha256: str | None = None,
    physical_sm_g6_g7_frontier_test_raw_sha256: str | None = None,
    physical_sm_g6_g7_frontier_markdown_raw_sha256: str | None = None,
    physical_sm_g8_frontier_report: dict[str, Any] | None = None,
    physical_sm_g8_frontier_raw_sha256: str | None = None,
    physical_sm_g8_frontier_source_raw_sha256: str | None = None,
    physical_sm_g8_frontier_test_raw_sha256: str | None = None,
    physical_sm_g8_frontier_markdown_raw_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a ledger from fresh reports, including repaired-contract states."""
    declared_contract_consistent = bool(x_report["contract_consistent"])
    contract_evidence_complete = _root_contract_evidence_complete(x_report)
    contract_consistent = bool(
        declared_contract_consistent and contract_evidence_complete
    )
    contract_blocker = str(x_report.get("blocker") or CONTRACT_BLOCKER)
    exact_x_v3_contract = _exact_x_v3_fail_closed_contract(
        x_report,
        source_raw_sha256=_raw_file_sha256(EXACT_X_V3_SOURCE),
        test_raw_sha256=_raw_file_sha256(EXACT_X_V3_TEST),
        json_raw_sha256=_raw_file_sha256(EXACT_X_V3_JSON),
        markdown_raw_sha256=_raw_file_sha256(EXACT_X_V3_MD),
        input_manifest_raw_sha256=_raw_file_sha256(EXACT_X_V3_INPUT_MANIFEST),
        trusted_sarah_manifest_raw_sha256=_raw_file_sha256(
            EXACT_X_V3_TRUSTED_SARAH_MANIFEST
        ),
        external_validation_file_present=exact_x.EXTERNAL_VALIDATION.is_file(),
    )
    historical = _historical_option_c_subtheorems()
    if g1_component_tensor_report is None:
        g1_component_tensor_report = _load_json_artifact(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON
        )
    if g1_component_tensor_raw_sha256 is None:
        g1_component_tensor_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON
        )
    if g1_component_tensor_source_raw_sha256 is None:
        g1_component_tensor_source_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE
        )
    g1_component_tensor_closure = _renormalizable_g1_component_tensor_closure(
        g1_component_tensor_report,
        raw_sha256=g1_component_tensor_raw_sha256,
        source_raw_sha256=g1_component_tensor_source_raw_sha256,
    )
    if g2_mathematical_report is None:
        g2_mathematical_report = _load_json_artifact(
            RENORMALIZABLE_G2_MATHEMATICAL_JSON
        )
    if g2_mathematical_raw_sha256 is None:
        g2_mathematical_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G2_MATHEMATICAL_JSON
        )
    if g2_mathematical_source_raw_sha256 is None:
        g2_mathematical_source_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G2_MATHEMATICAL_SOURCE
        )
    g2_mathematical_closure = _renormalizable_g2_mathematical_closure(
        g2_mathematical_report,
        raw_sha256=g2_mathematical_raw_sha256,
        source_raw_sha256=g2_mathematical_source_raw_sha256,
    )
    scoped = _gauged_u1x_scalar_subtheorems(
        g1_report,
        g1_component_tensor_closure,
        g2_report,
        g2_mathematical_closure,
        contract_consistent=contract_consistent,
    )
    g1_full_component_tensors_closed = bool(scoped["G1"]["full_G1_closed"])
    g2_scoped_derivatives_complete = bool(
        scoped["G2"]["scoped_derivative_audit_complete"]
    )
    g2_full_mathematical_potential_closed = bool(
        scoped["G2"]["full_renormalizable_G2_mathematical_potential_closed"]
    )
    if g3_sos_report is None:
        g3_sos_report = _load_json_artifact(G3_SOS_JSON)
    if g3_pd_report is None:
        g3_pd_report = _load_json_artifact(G3_PD_JSON)
    if g3_a_square_report is None:
        g3_a_square_report = _load_json_artifact(G3_A_SQUARE_JSON)
    if g3_sos_bfb_report is None:
        g3_sos_bfb_report = _load_json_artifact(G3_SOS_BFB_JSON)
    if g3_kernel_bound_report is None:
        g3_kernel_bound_report = _load_json_artifact(G3_KERNEL_BOUND_JSON)
    if g3_replacement_report is None:
        g3_replacement_report = _load_json_artifact(G3_REPLACEMENT_JSON)
    if g3_su5_pd_report is None:
        g3_su5_pd_report = _load_json_artifact(G3_SU5_PD_JSON)
    if g3_su5_hsx_report is None:
        g3_su5_hsx_report = _load_json_artifact(G3_SU5_HSX_JSON)
    if g3_su5_hsx_exact_hessian_report is None:
        g3_su5_hsx_exact_hessian_report = _load_json_artifact(
            G3_SU5_HSX_EXACT_HESSIAN_JSON
        )
    if g3_su5_equality_report is None:
        g3_su5_equality_report = _load_json_artifact(G3_SU5_EQUALITY_JSON)
    if g3_su5_phi_orbit_report is None:
        g3_su5_phi_orbit_report = _load_json_artifact(G3_SU5_PHI_ORBIT_JSON)
    if g3_su5_phi_local_component_report is None:
        g3_su5_phi_local_component_report = _load_json_artifact(
            G3_SU5_PHI_LOCAL_COMPONENT_JSON
        )
    if g3_su5_phi_su3_slice_report is None:
        g3_su5_phi_su3_slice_report = _load_json_artifact(
            G3_SU5_PHI_SU3_SLICE_JSON
        )
    if g3_su5_gap_report is None:
        g3_su5_gap_report = _load_json_artifact(G3_SU5_GAP_JSON)
    if g3_su5_fixed_f_offkernel_report is None:
        g3_su5_fixed_f_offkernel_report = _load_json_artifact(
            G3_SU5_FIXED_F_OFFKERNEL_JSON
        )
    if g3_su5_max_negative_zero_residual_report is None:
        g3_su5_max_negative_zero_residual_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON
        )
    if g3_su5_max_negative_full_residual_report is None:
        g3_su5_max_negative_full_residual_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON
        )
    if g3_su5_max_negative_rank1_su3_slice_report is None:
        g3_su5_max_negative_rank1_su3_slice_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON
        )
    if g3_rank1_su4_stabilizer_report is None:
        g3_rank1_su4_stabilizer_report = _load_json_artifact(
            G3_RANK1_SU4_STABILIZER_JSON
        )
    if g3_rank1_su4_phi210_intertwiners_report is None:
        g3_rank1_su4_phi210_intertwiners_report = _load_json_artifact(
            G3_RANK1_SU4_PHI210_INTERTWINERS_JSON
        )
    if g3_rank1_su4_aligned_carriers_report is None:
        g3_rank1_su4_aligned_carriers_report = _load_json_artifact(
            G3_RANK1_SU4_ALIGNED_CARRIERS_JSON
        )
    if g3_rank1_su4_phi210_quadratic_basis_report is None:
        g3_rank1_su4_phi210_quadratic_basis_report = _load_json_artifact(
            G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON
        )
    if g3_rank1_su4_augmented_sos_census_report is None:
        g3_rank1_su4_augmented_sos_census_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON
        )
    if g3_rank1_su4_augmented_sos_cubic_map_report is None:
        g3_rank1_su4_augmented_sos_cubic_map_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON
        )
    if g3_rank1_su4_augmented_sos_quartic_map_report is None:
        g3_rank1_su4_augmented_sos_quartic_map_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON
        )
    if g3_rank1_su4_augmented_sos_psd_target_report is None:
        g3_rank1_su4_augmented_sos_psd_target_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON
        )
    if g3_rank1_su4_corrected_publication is None:
        g3_rank1_su4_corrected_publication = (
            corrected_rank1.load_validated_publication()
        )
    if g3_alternative_global_sos_report is None:
        g3_alternative_global_sos_report = _load_json_artifact(
            G3_ALTERNATIVE_GLOBAL_SOS_JSON
        )
    eft_acceptance_loaded_from_disk = final_g3_eft_acceptance_report is None
    if eft_acceptance_loaded_from_disk:
        final_g3_eft_acceptance_report = _load_json_artifact(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        )
    if final_g3_eft_acceptance_raw_sha256 is None:
        final_g3_eft_acceptance_raw_sha256 = (
            _raw_file_sha256(FINAL_G3_EFT_ACCEPTANCE_JSON)
            if eft_acceptance_loaded_from_disk
            else ""
        )
    parallel_eft_g3_acceptance = _parallel_eft_g3_acceptance(
        final_g3_eft_acceptance_report,
        raw_sha256=final_g3_eft_acceptance_raw_sha256,
    )
    eft_g4_loaded_from_disk = final_g4_eft_mathematical_report is None
    if eft_g4_loaded_from_disk:
        final_g4_eft_mathematical_report = _load_json_artifact(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        )
    if final_g4_eft_mathematical_raw_sha256 is None:
        final_g4_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G4_EFT_MATHEMATICAL_JSON)
            if eft_g4_loaded_from_disk
            else ""
        )
    parallel_eft_g4_mathematical = _parallel_eft_g4_mathematical(
        final_g4_eft_mathematical_report,
        raw_sha256=final_g4_eft_mathematical_raw_sha256,
    )
    eft_g5_loaded_from_disk = final_g5_eft_mathematical_report is None
    if eft_g5_loaded_from_disk:
        final_g5_eft_mathematical_report = _load_json_artifact(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        )
    if final_g5_eft_mathematical_raw_sha256 is None:
        final_g5_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G5_EFT_MATHEMATICAL_JSON)
            if eft_g5_loaded_from_disk
            else ""
        )
    parallel_eft_g5_mathematical = _parallel_eft_g5_mathematical(
        final_g5_eft_mathematical_report,
        raw_sha256=final_g5_eft_mathematical_raw_sha256,
    )
    eft_g6_loaded_from_disk = final_g6_eft_mathematical_report is None
    if eft_g6_loaded_from_disk:
        final_g6_eft_mathematical_report = _load_json_artifact(
            FINAL_G6_EFT_MATHEMATICAL_JSON
        )
    if final_g6_eft_mathematical_raw_sha256 is None:
        final_g6_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G6_EFT_MATHEMATICAL_JSON)
            if eft_g6_loaded_from_disk
            else ""
        )
    if final_g6_eft_gate_source_raw_sha256 is None:
        final_g6_eft_gate_source_raw_sha256 = _raw_file_sha256(
            FINAL_G6_EFT_GATE_SOURCE
        )
    provenance_loaded_from_disk = g6_sm_provenance_report is None
    if provenance_loaded_from_disk:
        g6_sm_provenance_report = _load_json_artifact(G6_SM_PROVENANCE_JSON)
    if g6_sm_provenance_raw_sha256 is None:
        g6_sm_provenance_raw_sha256 = (
            _raw_file_sha256(G6_SM_PROVENANCE_JSON)
            if provenance_loaded_from_disk
            else ""
        )
    if g6_sm_provenance_source_raw_sha256 is None:
        g6_sm_provenance_source_raw_sha256 = _raw_file_sha256(
            G6_SM_PROVENANCE_SOURCE
        )
    g6_sm_provenance = _g6_sm_provenance_audit(
        g6_sm_provenance_report,
        raw_sha256=g6_sm_provenance_raw_sha256,
        source_raw_sha256=g6_sm_provenance_source_raw_sha256,
    )
    matching_loaded_from_disk = g6_g7_parameterized_matching_report is None
    if matching_loaded_from_disk:
        g6_g7_parameterized_matching_report = _load_json_artifact(
            G6_G7_PARAMETERIZED_MATCHING_JSON
        )
    if g6_g7_parameterized_matching_raw_sha256 is None:
        g6_g7_parameterized_matching_raw_sha256 = (
            _raw_file_sha256(G6_G7_PARAMETERIZED_MATCHING_JSON)
            if matching_loaded_from_disk
            else ""
        )
    if g6_g7_parameterized_matching_source_raw_sha256 is None:
        g6_g7_parameterized_matching_source_raw_sha256 = _raw_file_sha256(
            G6_G7_PARAMETERIZED_MATCHING_SOURCE
        )
    g6_g7_parameterized_matching = _parameterized_g6_g7_matching(
        g6_g7_parameterized_matching_report,
        raw_sha256=g6_g7_parameterized_matching_raw_sha256,
        source_raw_sha256=g6_g7_parameterized_matching_source_raw_sha256,
    )
    parallel_eft_g6_spectrum = _parallel_eft_g6_spectrum(
        final_g6_eft_mathematical_report,
        raw_sha256=final_g6_eft_mathematical_raw_sha256,
        gate_source_raw_sha256=final_g6_eft_gate_source_raw_sha256,
        provenance_audit=g6_sm_provenance,
        parameterized_matching=g6_g7_parameterized_matching,
    )
    gauge_betas_loaded_from_disk = authoritative_gauge_betas_report is None
    if gauge_betas_loaded_from_disk:
        authoritative_gauge_betas_report = _load_json_artifact(
            AUTHORITATIVE_GAUGE_BETAS_JSON
        )
    if authoritative_gauge_betas_raw_sha256 is None:
        authoritative_gauge_betas_raw_sha256 = (
            _raw_file_sha256(AUTHORITATIVE_GAUGE_BETAS_JSON)
            if gauge_betas_loaded_from_disk
            else ""
        )
    if authoritative_gauge_betas_source_raw_sha256 is None:
        authoritative_gauge_betas_source_raw_sha256 = _raw_file_sha256(
            AUTHORITATIVE_GAUGE_BETAS_SOURCE
        )
    authoritative_gauge_betas = _authoritative_gauge_beta_subtheorem(
        authoritative_gauge_betas_report,
        raw_sha256=authoritative_gauge_betas_raw_sha256,
        source_raw_sha256=authoritative_gauge_betas_source_raw_sha256,
    )
    pyrate_loaded_from_disk = pyrate3_gauge_replay_report is None
    if pyrate_loaded_from_disk:
        pyrate3_gauge_replay_report = _load_json_artifact(PYRATE3_GAUGE_REPLAY_JSON)
    if pyrate3_gauge_replay_raw_sha256 is None:
        pyrate3_gauge_replay_raw_sha256 = _raw_file_sha256(
            PYRATE3_GAUGE_REPLAY_JSON
        )
    if pyrate3_gauge_replay_source_raw_sha256 is None:
        pyrate3_gauge_replay_source_raw_sha256 = _raw_file_sha256(
            PYRATE3_GAUGE_REPLAY_SOURCE
        )
    if pyrate3_gauge_replay_model_raw_sha256 is None:
        pyrate3_gauge_replay_model_raw_sha256 = _raw_file_sha256(
            PYRATE3_GAUGE_REPLAY_MODEL
        )
    if pyrate3_gauge_replay_data_raw_sha256 is None:
        pyrate3_gauge_replay_data_raw_sha256 = _raw_file_sha256(
            PYRATE3_GAUGE_REPLAY_DATA
        )
    pyrate3_gauge_replay = _pyrate3_gauge_replay_subtheorem(
        pyrate3_gauge_replay_report,
        raw_sha256=pyrate3_gauge_replay_raw_sha256,
        source_raw_sha256=pyrate3_gauge_replay_source_raw_sha256,
        model_raw_sha256=pyrate3_gauge_replay_model_raw_sha256,
        data_raw_sha256=pyrate3_gauge_replay_data_raw_sha256,
    )
    g7_loaded_from_disk = eft_g7_nonidentifiability_report is None
    if g7_loaded_from_disk:
        eft_g7_nonidentifiability_report = _load_json_artifact(
            EFT_G7_NONIDENTIFIABILITY_JSON
        )
    if eft_g7_nonidentifiability_raw_sha256 is None:
        eft_g7_nonidentifiability_raw_sha256 = (
            _raw_file_sha256(EFT_G7_NONIDENTIFIABILITY_JSON)
            if g7_loaded_from_disk
            else ""
        )
    if eft_g7_nonidentifiability_source_raw_sha256 is None:
        eft_g7_nonidentifiability_source_raw_sha256 = _raw_file_sha256(
            EFT_G7_NONIDENTIFIABILITY_SOURCE
        )
    parallel_eft_g7_nonidentifiability = _parallel_eft_g7_nonidentifiability(
        eft_g7_nonidentifiability_report,
        raw_sha256=eft_g7_nonidentifiability_raw_sha256,
        source_raw_sha256=eft_g7_nonidentifiability_source_raw_sha256,
    )
    physical_g7_loaded_from_disk = physical_g7_component_threshold_report is None
    if physical_g7_loaded_from_disk:
        physical_g7_component_threshold_report = _load_json_artifact(
            PHYSICAL_G7_COMPONENT_THRESHOLD_JSON
        )
    if physical_g7_component_threshold_raw_sha256 is None:
        physical_g7_component_threshold_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_G7_COMPONENT_THRESHOLD_JSON)
            if physical_g7_loaded_from_disk
            else ""
        )
    if physical_g7_component_threshold_source_raw_sha256 is None:
        physical_g7_component_threshold_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE
        )
    if physical_g7_component_threshold_test_raw_sha256 is None:
        physical_g7_component_threshold_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_TEST
        )
    if physical_g7_component_threshold_markdown_raw_sha256 is None:
        physical_g7_component_threshold_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_G7_COMPONENT_THRESHOLD_MD
        )
    physical_g7_component_threshold = _physical_g7_component_threshold_contract(
        physical_g7_component_threshold_report,
        raw_sha256=physical_g7_component_threshold_raw_sha256,
        source_raw_sha256=physical_g7_component_threshold_source_raw_sha256,
        test_raw_sha256=physical_g7_component_threshold_test_raw_sha256,
        markdown_raw_sha256=physical_g7_component_threshold_markdown_raw_sha256,
    )
    yukawa_cgcs_loaded_from_disk = normalized_yukawa_cgcs_report is None
    if yukawa_cgcs_loaded_from_disk:
        normalized_yukawa_cgcs_report = _load_json_artifact(
            NORMALIZED_YUKAWA_CGCS_JSON
        )
    if normalized_yukawa_cgcs_raw_sha256 is None:
        normalized_yukawa_cgcs_raw_sha256 = (
            _raw_file_sha256(NORMALIZED_YUKAWA_CGCS_JSON)
            if yukawa_cgcs_loaded_from_disk
            else ""
        )
    if normalized_yukawa_cgcs_source_raw_sha256 is None:
        normalized_yukawa_cgcs_source_raw_sha256 = _raw_file_sha256(
            NORMALIZED_YUKAWA_CGCS_SOURCE
        )
    if normalized_yukawa_cgcs_test_raw_sha256 is None:
        normalized_yukawa_cgcs_test_raw_sha256 = _raw_file_sha256(
            NORMALIZED_YUKAWA_CGCS_TEST
        )
    if normalized_yukawa_cgcs_markdown_raw_sha256 is None:
        normalized_yukawa_cgcs_markdown_raw_sha256 = _raw_file_sha256(
            NORMALIZED_YUKAWA_CGCS_MD
        )
    normalized_yukawa_cgcs = _normalized_so10_yukawa_cgc_contract(
        normalized_yukawa_cgcs_report,
        raw_sha256=normalized_yukawa_cgcs_raw_sha256,
        source_raw_sha256=normalized_yukawa_cgcs_source_raw_sha256,
        test_raw_sha256=normalized_yukawa_cgcs_test_raw_sha256,
        markdown_raw_sha256=normalized_yukawa_cgcs_markdown_raw_sha256,
    )
    physical_sm_loaded_from_disk = physical_sm_vacuum_report is None
    if physical_sm_loaded_from_disk:
        physical_sm_vacuum_report = _load_json_artifact(PHYSICAL_SM_VACUUM_JSON)
    if physical_sm_vacuum_raw_sha256 is None:
        physical_sm_vacuum_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_VACUUM_JSON)
            if physical_sm_loaded_from_disk
            else ""
        )
    if physical_sm_vacuum_source_raw_sha256 is None:
        physical_sm_vacuum_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VACUUM_SOURCE
        )
    if physical_sm_vacuum_test_raw_sha256 is None:
        physical_sm_vacuum_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VACUUM_TEST
        )
    if physical_sm_vacuum_markdown_raw_sha256 is None:
        physical_sm_vacuum_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VACUUM_MD
        )
    physical_sm_vacuum = _physical_sm_vacuum_truth_overlay(
        physical_sm_vacuum_report,
        raw_sha256=physical_sm_vacuum_raw_sha256,
        source_raw_sha256=physical_sm_vacuum_source_raw_sha256,
        test_raw_sha256=physical_sm_vacuum_test_raw_sha256,
        markdown_raw_sha256=physical_sm_vacuum_markdown_raw_sha256,
    )
    physical_sm_source_equality_report = _load_json_artifact(
        PHYSICAL_SM_SOURCE_EQUALITY_JSON
    )
    physical_sm_source_equality = (
        _physical_sm_source_algebra_equality_frontier_contract(
            physical_sm_source_equality_report,
            raw_sha256=_raw_file_sha256(PHYSICAL_SM_SOURCE_EQUALITY_JSON),
            source_raw_sha256=_raw_file_sha256(
                PHYSICAL_SM_SOURCE_EQUALITY_SOURCE
            ),
            test_raw_sha256=_raw_file_sha256(PHYSICAL_SM_SOURCE_EQUALITY_TEST),
            markdown_raw_sha256=_raw_file_sha256(PHYSICAL_SM_SOURCE_EQUALITY_MD),
        )
    )
    physical_sm_five_amplitude_equality_report = _load_json_artifact(
        PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
    )
    physical_sm_five_amplitude_equality = (
        _physical_sm_five_amplitude_equality_contract(
            physical_sm_five_amplitude_equality_report,
            raw_sha256=_raw_file_sha256(
                PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
            ),
            source_raw_sha256=_raw_file_sha256(
                PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE
            ),
            test_raw_sha256=_raw_file_sha256(
                PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST
            ),
            markdown_raw_sha256=_raw_file_sha256(
                PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD
            ),
        )
    )
    physical_sm_hard_projector_hessians_report = _load_json_artifact(
        PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON
    )
    physical_sm_hard_projector_hessians = (
        _physical_sm_hard_projector_hessians_contract(
            physical_sm_hard_projector_hessians_report,
            raw_sha256=_raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON),
            source_raw_sha256=_raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE),
            test_raw_sha256=_raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST),
            markdown_raw_sha256=_raw_file_sha256(PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD),
        )
    )
    physical_sm_last_six_hessians_report = _load_json_artifact(
        PHYSICAL_SM_LAST_SIX_HESSIANS_JSON
    )
    physical_sm_last_six_hessians = _physical_sm_last_six_hessians_contract(
        physical_sm_last_six_hessians_report,
        raw_sha256=_raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_JSON),
        source_raw_sha256=_raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE),
        test_raw_sha256=_raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_TEST),
        markdown_raw_sha256=_raw_file_sha256(PHYSICAL_SM_LAST_SIX_HESSIANS_MD),
    )
    physical_sm_37_row_aggregate_report = _load_json_artifact(
        PHYSICAL_SM_37_ROW_AGGREGATE_JSON
    )
    physical_sm_37_row_aggregate = _physical_sm_37_row_aggregate_contract(
        physical_sm_37_row_aggregate_report,
        raw_sha256=_raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_JSON),
        source_raw_sha256=_raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE),
        test_raw_sha256=_raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_TEST),
        markdown_raw_sha256=_raw_file_sha256(PHYSICAL_SM_37_ROW_AGGREGATE_MD),
    )
    physical_sm_local_equality_orbit_report = _load_json_artifact(
        PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON
    )
    physical_sm_local_equality_orbit = _physical_sm_local_equality_orbit_contract(
        physical_sm_local_equality_orbit_report,
        portable_lf_sha256=_file_sha256(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON),
        source_portable_lf_sha256=_file_sha256(
            PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE
        ),
        test_portable_lf_sha256=_file_sha256(PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST),
        markdown_portable_lf_sha256=_file_sha256(
            PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD
        ),
    )
    physical_sm_g4_g5_branch_mismatch_report = _load_json_artifact(
        PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON
    )
    physical_sm_g4_g5_branch_mismatch = (
        _physical_sm_g4_g5_branch_mismatch_contract(
            physical_sm_g4_g5_branch_mismatch_report,
            raw_sha256=_raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON),
            source_raw_sha256=_raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE),
            test_raw_sha256=_raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST),
            markdown_raw_sha256=_raw_file_sha256(PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD),
        )
    )
    heavy_vector_loaded_from_disk = physical_sm_heavy_vector_report is None
    if heavy_vector_loaded_from_disk:
        physical_sm_heavy_vector_report = _load_json_artifact(
            PHYSICAL_SM_HEAVY_VECTOR_JSON
        )
    if physical_sm_heavy_vector_raw_sha256 is None:
        physical_sm_heavy_vector_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_HEAVY_VECTOR_JSON)
            if heavy_vector_loaded_from_disk
            else ""
        )
    if physical_sm_heavy_vector_source_raw_sha256 is None:
        physical_sm_heavy_vector_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_SOURCE
        )
    if physical_sm_heavy_vector_test_raw_sha256 is None:
        physical_sm_heavy_vector_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_TEST
        )
    if physical_sm_heavy_vector_markdown_raw_sha256 is None:
        physical_sm_heavy_vector_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_MD
        )
    physical_sm_heavy_vector = _physical_sm_heavy_vector_mass_contract(
        physical_sm_heavy_vector_report,
        raw_sha256=physical_sm_heavy_vector_raw_sha256,
        source_raw_sha256=physical_sm_heavy_vector_source_raw_sha256,
        test_raw_sha256=physical_sm_heavy_vector_test_raw_sha256,
        markdown_raw_sha256=physical_sm_heavy_vector_markdown_raw_sha256,
    )
    heavy_vector_msbar_loaded_from_disk = (
        physical_sm_heavy_vector_msbar_report is None
    )
    if heavy_vector_msbar_loaded_from_disk:
        physical_sm_heavy_vector_msbar_report = _load_json_artifact(
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON
        )
    if physical_sm_heavy_vector_msbar_raw_sha256 is None:
        physical_sm_heavy_vector_msbar_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON)
            if heavy_vector_msbar_loaded_from_disk
            else ""
        )
    if physical_sm_heavy_vector_msbar_source_raw_sha256 is None:
        physical_sm_heavy_vector_msbar_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE
        )
    if physical_sm_heavy_vector_msbar_test_raw_sha256 is None:
        physical_sm_heavy_vector_msbar_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST
        )
    if physical_sm_heavy_vector_msbar_markdown_raw_sha256 is None:
        physical_sm_heavy_vector_msbar_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD
        )
    physical_sm_heavy_vector_msbar = (
        _physical_sm_heavy_vector_msbar_matching_contract(
            physical_sm_heavy_vector_msbar_report,
            raw_sha256=physical_sm_heavy_vector_msbar_raw_sha256,
            source_raw_sha256=(
                physical_sm_heavy_vector_msbar_source_raw_sha256
            ),
            test_raw_sha256=physical_sm_heavy_vector_msbar_test_raw_sha256,
            markdown_raw_sha256=(
                physical_sm_heavy_vector_msbar_markdown_raw_sha256
            ),
        )
    )
    vector_rxi_loaded_from_disk = physical_sm_vector_rxi_report is None
    if vector_rxi_loaded_from_disk:
        physical_sm_vector_rxi_report = _load_json_artifact(
            PHYSICAL_SM_VECTOR_RXI_JSON
        )
    if physical_sm_vector_rxi_raw_sha256 is None:
        physical_sm_vector_rxi_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_VECTOR_RXI_JSON)
            if vector_rxi_loaded_from_disk
            else ""
        )
    if physical_sm_vector_rxi_source_raw_sha256 is None:
        physical_sm_vector_rxi_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VECTOR_RXI_SOURCE
        )
    if physical_sm_vector_rxi_test_raw_sha256 is None:
        physical_sm_vector_rxi_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VECTOR_RXI_TEST
        )
    if physical_sm_vector_rxi_markdown_raw_sha256 is None:
        physical_sm_vector_rxi_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_VECTOR_RXI_MD
        )
    physical_sm_vector_rxi = (
        _physical_sm_vector_rxi_vacuum_cancellation_contract(
            physical_sm_vector_rxi_report,
            raw_sha256=physical_sm_vector_rxi_raw_sha256,
            source_raw_sha256=physical_sm_vector_rxi_source_raw_sha256,
            test_raw_sha256=physical_sm_vector_rxi_test_raw_sha256,
            markdown_raw_sha256=physical_sm_vector_rxi_markdown_raw_sha256,
        )
    )
    conditional_scalar_loaded_from_disk = (
        conditional_physical_sm_scalar_spectrum_report is None
    )
    if conditional_scalar_loaded_from_disk:
        conditional_physical_sm_scalar_spectrum_report = _load_json_artifact(
            CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON
        )
    if conditional_physical_sm_scalar_spectrum_raw_sha256 is None:
        conditional_physical_sm_scalar_spectrum_raw_sha256 = (
            _raw_file_sha256(CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON)
            if conditional_scalar_loaded_from_disk
            else ""
        )
    if conditional_physical_sm_scalar_spectrum_source_raw_sha256 is None:
        conditional_physical_sm_scalar_spectrum_source_raw_sha256 = (
            _raw_file_sha256(CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE)
        )
    if conditional_physical_sm_scalar_spectrum_test_raw_sha256 is None:
        conditional_physical_sm_scalar_spectrum_test_raw_sha256 = (
            _raw_file_sha256(CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST)
        )
    if conditional_physical_sm_scalar_spectrum_markdown_raw_sha256 is None:
        conditional_physical_sm_scalar_spectrum_markdown_raw_sha256 = (
            _raw_file_sha256(CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD)
        )
    conditional_physical_sm_scalar_spectrum = (
        _conditional_physical_sm_eft_hessian_spectrum_contract(
            conditional_physical_sm_scalar_spectrum_report,
            raw_sha256=conditional_physical_sm_scalar_spectrum_raw_sha256,
            source_raw_sha256=(
                conditional_physical_sm_scalar_spectrum_source_raw_sha256
            ),
            test_raw_sha256=(
                conditional_physical_sm_scalar_spectrum_test_raw_sha256
            ),
            markdown_raw_sha256=(
                conditional_physical_sm_scalar_spectrum_markdown_raw_sha256
            ),
        )
    )
    closure_frontier_loaded_from_disk = (
        physical_sm_g6_g7_frontier_report is None
    )
    if closure_frontier_loaded_from_disk:
        physical_sm_g6_g7_frontier_report = _load_json_artifact(
            PHYSICAL_SM_G6_G7_FRONTIER_JSON
        )
    if physical_sm_g6_g7_frontier_raw_sha256 is None:
        physical_sm_g6_g7_frontier_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_G6_G7_FRONTIER_JSON)
            if closure_frontier_loaded_from_disk
            else ""
        )
    if physical_sm_g6_g7_frontier_source_raw_sha256 is None:
        physical_sm_g6_g7_frontier_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G6_G7_FRONTIER_SOURCE
        )
    if physical_sm_g6_g7_frontier_test_raw_sha256 is None:
        physical_sm_g6_g7_frontier_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G6_G7_FRONTIER_TEST
        )
    if physical_sm_g6_g7_frontier_markdown_raw_sha256 is None:
        physical_sm_g6_g7_frontier_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G6_G7_FRONTIER_MD
        )
    physical_sm_g6_g7_frontier = (
        _physical_sm_g6_g7_closure_frontier_contract(
            physical_sm_g6_g7_frontier_report,
            raw_sha256=physical_sm_g6_g7_frontier_raw_sha256,
            source_raw_sha256=physical_sm_g6_g7_frontier_source_raw_sha256,
            test_raw_sha256=physical_sm_g6_g7_frontier_test_raw_sha256,
            markdown_raw_sha256=physical_sm_g6_g7_frontier_markdown_raw_sha256,
        )
    )
    g8_frontier_loaded_from_disk = physical_sm_g8_frontier_report is None
    if g8_frontier_loaded_from_disk:
        physical_sm_g8_frontier_report = _load_json_artifact(
            PHYSICAL_SM_G8_FRONTIER_JSON
        )
    if physical_sm_g8_frontier_raw_sha256 is None:
        physical_sm_g8_frontier_raw_sha256 = (
            _raw_file_sha256(PHYSICAL_SM_G8_FRONTIER_JSON)
            if g8_frontier_loaded_from_disk
            else ""
        )
    if physical_sm_g8_frontier_source_raw_sha256 is None:
        physical_sm_g8_frontier_source_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G8_FRONTIER_SOURCE
        )
    if physical_sm_g8_frontier_test_raw_sha256 is None:
        physical_sm_g8_frontier_test_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G8_FRONTIER_TEST
        )
    if physical_sm_g8_frontier_markdown_raw_sha256 is None:
        physical_sm_g8_frontier_markdown_raw_sha256 = _raw_file_sha256(
            PHYSICAL_SM_G8_FRONTIER_MD
        )
    physical_sm_g8_frontier = (
        _physical_sm_g8_identifiability_frontier_contract(
            physical_sm_g8_frontier_report,
            raw_sha256=physical_sm_g8_frontier_raw_sha256,
            source_raw_sha256=physical_sm_g8_frontier_source_raw_sha256,
            test_raw_sha256=physical_sm_g8_frontier_test_raw_sha256,
            markdown_raw_sha256=physical_sm_g8_frontier_markdown_raw_sha256,
        )
    )
    physical_g7_recalculated_inputs = _physical_g7_recalculated_input_resolution(
        physical_g7_component_threshold,
        normalized_yukawa_cgcs,
        physical_sm_heavy_vector,
        physical_sm_heavy_vector_msbar,
        physical_sm_vector_rxi,
        conditional_physical_sm_scalar_spectrum,
        physical_sm_g6_g7_frontier,
    )
    g3_frontier = _gauged_u1x_g3_frontier(
        g3_sos_report,
        g3_pd_report,
        g3_a_square_report,
        g3_sos_bfb_report,
        g3_kernel_bound_report,
        g3_replacement_report,
        g3_su5_pd_report,
        g3_su5_hsx_report,
        g3_su5_hsx_exact_hessian_report,
        g3_su5_equality_report,
        g3_su5_phi_orbit_report,
        g3_su5_phi_local_component_report,
        g3_su5_phi_su3_slice_report,
        g3_su5_gap_report,
        g3_su5_fixed_f_offkernel_report,
        g3_su5_max_negative_zero_residual_report,
        g3_su5_max_negative_full_residual_report,
        g3_su5_max_negative_rank1_su3_slice_report,
        g3_rank1_su4_stabilizer_report,
        g3_rank1_su4_phi210_intertwiners_report,
        g3_rank1_su4_aligned_carriers_report,
        g3_rank1_su4_phi210_quadratic_basis_report,
        g3_rank1_su4_augmented_sos_census_report,
        g3_rank1_su4_augmented_sos_cubic_map_report,
        g3_rank1_su4_augmented_sos_quartic_map_report,
        g3_rank1_su4_augmented_sos_psd_target_report,
        g3_rank1_su4_corrected_publication,
        g3_alternative_global_sos_report,
    )
    gates = _build_gates(
        contract_consistent=contract_consistent,
        contract_blocker=contract_blocker,
        scoped=scoped,
    )
    gates["G3"]["constructive_frontier_evidence"] = g3_frontier
    gates["G5"]["constructive_frontier_evidence"] = g3_frontier
    gates["G1"]["exact_X_v3_fail_closed_contract"] = exact_x_v3_contract
    for gate_name in ("G3", "G4", "G5"):
        gates[gate_name]["physical_SM_source_algebra_equality_frontier"] = (
            physical_sm_source_equality
        )
        gates[gate_name]["physical_SM_five_amplitude_equality"] = (
            physical_sm_five_amplitude_equality
        )
        gates[gate_name]["physical_SM_hard_projector_Hessians"] = (
            physical_sm_hard_projector_hessians
        )
        gates[gate_name]["physical_SM_last_six_Hessians"] = (
            physical_sm_last_six_hessians
        )
        gates[gate_name]["physical_SM_37_row_aggregate"] = (
            physical_sm_37_row_aggregate
        )
        gates[gate_name]["physical_SM_local_equality_orbit"] = (
            physical_sm_local_equality_orbit
        )
    for gate_name in ("G4", "G5", "G6", "G7", "G8"):
        gates[gate_name]["physical_SM_G4_G5_branch_mismatch"] = (
            physical_sm_g4_g5_branch_mismatch
        )
    gates["G6"]["physical_stabilizer_audit"] = g6_sm_provenance
    gates["G6"]["physical_SM_heavy_vector_mass_contract"] = (
        physical_sm_heavy_vector
    )
    gates["G6"]["physical_SM_heavy_vector_MSbar_matching_contract"] = (
        physical_sm_heavy_vector_msbar
    )
    gates["G6"]["physical_SM_vector_Rxi_vacuum_cancellation_contract"] = (
        physical_sm_vector_rxi
    )
    gates["G6"]["conditional_physical_SM_EFT_Hessian_spectrum_contract"] = (
        conditional_physical_sm_scalar_spectrum
    )
    gates["G6"]["physical_SM_G6_G7_closure_frontier"] = (
        physical_sm_g6_g7_frontier
    )
    for gate_name in ("G3", "G4", "G5", "G6", "G7", "G8"):
        gates[gate_name]["physical_SM_truth_overlay"] = physical_sm_vacuum
    gates["G8"]["physical_SM_G8_identifiability_frontier"] = (
        physical_sm_g8_frontier
    )
    gates["G7"]["certified_input_obstruction"] = {
        "legacy_threshold_nonidentifiability": parallel_eft_g7_nonidentifiability,
        "physical_stabilizer_mismatch": g6_sm_provenance,
        "parameterized_formal_G89_matching": g6_g7_parameterized_matching,
        "authoritative_gauge_only_RGE": authoritative_gauge_betas,
        "independent_PyRATE3_gauge_only_replay": pyrate3_gauge_replay,
        "physical_PS_SM_component_threshold_contract": (
            physical_g7_component_threshold
        ),
        "normalized_SO10_representation_Yukawa_CGCs": normalized_yukawa_cgcs,
        "physical_SM_vacuum_truth_overlay": physical_sm_vacuum,
        "physical_SM_heavy_vector_mass_contract": physical_sm_heavy_vector,
        "physical_SM_heavy_vector_MSbar_matching_contract": (
            physical_sm_heavy_vector_msbar
        ),
        "physical_SM_vector_Rxi_vacuum_cancellation_contract": (
            physical_sm_vector_rxi
        ),
        "conditional_physical_SM_EFT_Hessian_spectrum_contract": (
            conditional_physical_sm_scalar_spectrum
        ),
        "physical_SM_G6_G7_closure_frontier": physical_sm_g6_g7_frontier,
        "recalculated_scoped_input_resolution": physical_g7_recalculated_inputs,
    }

    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == STATUS_BLOCKED]

    gauged_counts = g1_report["counts"]
    historical_ids = set(historical["source_contract_ids"].values())
    expected_statuses = _expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_full_mathematical_potential_closed,
    )
    contract_state_classified = (
        contract_consistent
        and x_report.get("blocker") is None
        and not x_report.get("scientific_blockers", [])
    ) or (
        not contract_consistent
        and x_report.get("blocker") == contract_blocker
        and contract_blocker in x_report.get("scientific_blockers", [])
    )

    def dependency_closed(dependency: str) -> bool:
        if dependency == "MODEL_CONTRACT":
            return contract_consistent
        return statuses[dependency] == STATUS_CLOSED

    checks = {
        "exact_X_audit_executes": x_report["n_failed"] == 0,
        "exact_X_v3_contract_state_is_fail_closed_and_consistent": (
            (
                exact_x_v3_contract["source_bound"] is True
                and exact_x_v3_contract["static_native_contract_closed"] is True
                and exact_x_v3_contract[
                    "trusted_SARAH_4_15_3_source_tree_manifest_closed"
                ]
                is True
                and exact_x_v3_contract[
                    "external_v3_execution_attestation_present"
                ]
                is False
                and exact_x_v3_contract["resolved_Wolfram_runtime_bound"] is False
                and exact_x_v3_contract["contract_consistent"] is False
                and exact_x_v3_contract["authoritative_G1_closed"] is False
                and gates["G1"]["status"] == STATUS_BLOCKED
            )
            or (
                contract_consistent is True
                and _root_contract_evidence_complete(x_report) is True
                and exact_x_v3_contract["source_bound"] is True
                and exact_x_v3_contract[
                    "external_v3_execution_attestation_present"
                ]
                is True
                and exact_x_v3_contract["resolved_Wolfram_runtime_bound"] is True
                and exact_x_v3_contract["contract_consistent"] is True
                and exact_x_v3_contract["authoritative_G1_closed"] is True
                and gates["G1"]["status"] == STATUS_CLOSED
            )
        ),
        "parallel_EFT_G3_acceptance_is_source_bound_and_release_open": (
            parallel_eft_g3_acceptance["source_bound"] is True
            and parallel_eft_g3_acceptance[
                "mathematical_G3_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g3_acceptance[
                "release_G3_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g3_acceptance[
                "mathematical_G3_closed_for_original_renormalizable_model"
            ]
            is False
            and parallel_eft_g3_acceptance["renormalizable_gate_mutated"]
            is False
            and parallel_eft_g3_acceptance["G4_closed"] is False
        ),
        "parallel_EFT_G4_mathematical_is_source_bound_and_release_open": (
            parallel_eft_g4_mathematical["source_bound"] is True
            and parallel_eft_g4_mathematical[
                "mathematical_G4_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g4_mathematical[
                "release_G4_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g4_mathematical[
                "mathematical_G4_closed_for_original_renormalizable_model"
            ]
            is False
            and parallel_eft_g4_mathematical[
                "authoritative_renormalizable_G4_gate_mutated"
            ]
            is False
        ),
        "parallel_EFT_G5_mathematical_is_source_bound_and_release_open": (
            parallel_eft_g5_mathematical["source_bound"] is True
            and parallel_eft_g5_mathematical[
                "mathematical_G5_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g5_mathematical[
                "release_G5_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g5_mathematical[
                "authoritative_renormalizable_G5_closed"
            ]
            is False
            and parallel_eft_g5_mathematical[
                "authoritative_renormalizable_G5_mutated"
            ]
            is False
            and parallel_eft_g5_mathematical["new_SOS_claimed"] is False
        ),
        "parallel_EFT_G6_formal_spectrum_is_bound_but_physical_G6_open": (
            parallel_eft_g6_spectrum["source_bound"] is True
            and parallel_eft_g6_spectrum[
                "formal_SU3_x_U1_89_tree_factorization_closed"
            ]
            is True
            and parallel_eft_g6_spectrum[
                "mathematical_G6_closed_for_EFT_model"
            ]
            is False
            and parallel_eft_g6_spectrum["physical_mathematical_G6_closed"]
            is False
            and parallel_eft_g6_spectrum["physical_U1em_provenance_complete"]
            is False
            and parallel_eft_g6_spectrum[
                "release_G6_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g6_spectrum[
                "authoritative_renormalizable_G6_closed"
            ]
            is False
            and parallel_eft_g6_spectrum["authoritative_G6_gate_mutated"]
            is False
            and parallel_eft_g6_spectrum["whole_model_validated"] is False
        ),
        "G6_physical_stabilizer_mismatch_is_source_bound": (
            g6_sm_provenance["source_bound"] is True
            and g6_sm_provenance["formal_tree_mass_factorization_valid"] is True
            and g6_sm_provenance["actual_residual_group"]
            == "SU(3)_C x U(1)_89"
            and g6_sm_provenance["physical_U1em_provenance_complete"] is False
            and g6_sm_provenance["physical_mathematical_G6_closed"] is False
            and g6_sm_provenance["release_G6_verified"] is False
        ),
        "parameterized_formal_G89_matching_is_bound_and_not_physical_G7": (
            g6_g7_parameterized_matching["source_bound"] is True
            and g6_g7_parameterized_matching[
                "formal_SU3_x_U1_89_threshold_determinants_complete"
            ]
            is True
            and g6_g7_parameterized_matching[
                "physical_SM_scalar_thresholds_identified"
            ]
            is False
            and g6_g7_parameterized_matching["physical_mathematical_G6_closed"]
            is False
            and g6_g7_parameterized_matching["mathematical_G7_closed"] is False
            and g6_g7_parameterized_matching["release_G7_verified"] is False
        ),
        "authoritative_gauge_beta_subtheorem_bound_but_full_G7_open": (
            authoritative_gauge_betas["source_bound"] is True
            and authoritative_gauge_betas[
                "exact_nonyukawa_two_loop_gauge_polynomial_closed"
            ]
            is True
            and authoritative_gauge_betas["full_two_loop_gauge_beta_closed"]
            is False
            and authoritative_gauge_betas["component_threshold_matching_closed"]
            is False
            and authoritative_gauge_betas["physical_G6_input_accepted_for_G7"]
            is False
            and authoritative_gauge_betas["mathematical_G7_closed"] is False
            and authoritative_gauge_betas["release_G7_verified"] is False
        ),
        "independent_PyRATE3_gauge_replay_bound_but_full_G7_open": (
            pyrate3_gauge_replay["source_bound"] is True
            and pyrate3_gauge_replay[
                "second_implementation_for_scoped_gauge_subtheorem"
            ]
            is True
            and pyrate3_gauge_replay["full_two_loop_gauge_beta_closed"] is False
            and pyrate3_gauge_replay["physical_G6_threshold_matching_closed"]
            is False
            and pyrate3_gauge_replay["mathematical_G7_closed"] is False
            and pyrate3_gauge_replay["release_G7_verified"] is False
        ),
        "formal_U1_89_restriction_audit_is_source_bound_and_G7_open": (
            parallel_eft_g7_nonidentifiability["source_bound"] is True
            and parallel_eft_g7_nonidentifiability[
                "formal_U1_89_abstract_restriction_noninjectivity_proved"
            ]
            is True
            and parallel_eft_g7_nonidentifiability[
                "exact_physical_EFT_G7_input_nonidentifiability_proved"
            ]
            is False
            and parallel_eft_g7_nonidentifiability[
                "formal_U1_89_restriction_map_noninjective"
            ]
            is True
            and parallel_eft_g7_nonidentifiability[
                "historical_electroweak_lift_interpretation_valid"
            ]
            is False
            and parallel_eft_g7_nonidentifiability["absolute_scale_unidentified"]
            is True
            and parallel_eft_g7_nonidentifiability[
                "mathematical_EFT_G7_closed"
            ]
            is False
            and parallel_eft_g7_nonidentifiability[
                "EFT_release_G7_verified"
            ]
            is False
            and parallel_eft_g7_nonidentifiability[
                "authoritative_renormalizable_G7_closed"
            ]
            is False
            and parallel_eft_g7_nonidentifiability["positive_G7_certified"]
            is False
            and parallel_eft_g7_nonidentifiability[
                "negative_G7_no_go_certified"
            ]
            is False
            and parallel_eft_g7_nonidentifiability[
                "downstream_integration_completed"
            ]
            is True
            and statuses["G7"] == STATUS_BLOCKED
            and statuses["G8"] == STATUS_BLOCKED
        ),
        "physical_G7_component_threshold_contract_is_bound_and_fail_closed": (
            physical_g7_component_threshold["source_bound"] is True
            and physical_g7_component_threshold[
                "authoritative_inventory_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "continuous_gauge_anomalies_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "exact_one_loop_gauge_coefficients_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "exact_two_loop_nonyukawa_gauge_flow_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "independent_official_PyRATE3_gauge_replay_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "physical_PS_SM_matter_branching_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "parameterized_one_loop_matter_threshold_kernel_closed"
            ]
            is True
            and physical_g7_component_threshold[
                "physical_component_pole_mass_matrices_closed"
            ]
            is False
            and physical_g7_component_threshold["physical_G7_closed"] is False
            and physical_g7_component_threshold["mathematical_G7_closed"]
            is False
            and physical_g7_component_threshold["release_G7_verified"] is False
            and physical_g7_component_threshold[
                "authoritative_renormalizable_G7_closed"
            ]
            is False
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "physical_SM_vacuum_overlay_supersedes_old_label_and_fails_closed": (
            physical_sm_vacuum["source_bound"] is True
            and physical_sm_vacuum["physical_SM_target_exactly_constructed"]
            is True
            and physical_sm_vacuum["standard_SU3C_x_U1em_stabilizer_proved"]
            is True
            and physical_sm_vacuum[
                "reconstructed_stationary_transverse_PSD_witness_available"
            ]
            is True
            and physical_sm_vacuum[
                "direct_source_algebra_stationary_PSD_witness_available"
            ]
            is False
            and physical_sm_vacuum["source_bound_global_equality_orbit_proved"]
            is False
            and physical_sm_vacuum[
                "old_selected_EFT_stabilizer_label_superseded"
            ]
            is True
            and physical_sm_vacuum["old_selected_EFT_target_actual_stabilizer"]
            == "SU(3)_C x U(1)_89"
            and physical_sm_vacuum["physical_SM_G3_closed"] is False
            and physical_sm_vacuum["physical_SM_G4_closed"] is False
            and physical_sm_vacuum["physical_SM_G5_closed"] is False
            and physical_sm_vacuum["physical_SM_G6_closed"] is False
            and physical_sm_vacuum["physical_SM_G7_closed"] is False
        ),
        "physical_SM_radial_equality_is_exact_but_G3_G4_G5_remain_open": (
            physical_sm_source_equality["source_bound"] is True
            and physical_sm_source_equality[
                "radial_stationary_equality_classified_exactly"
            ]
            is True
            and physical_sm_source_equality["radial_gcd"] == "t - 1"
            and physical_sm_source_equality[
                "direct_source_algebra_stationary_Hessian_available"
            ]
            is False
            and physical_sm_source_equality[
                "complete_nonradial_equality_orbit_proved"
            ]
            is False
            and physical_sm_source_equality["physical_SM_G3_closed"] is False
            and physical_sm_source_equality["physical_SM_G4_closed"] is False
            and physical_sm_source_equality["physical_SM_G5_closed"] is False
        ),
        "physical_SM_five_amplitude_equality_is_exact_but_full_G3_G4_G5_remain_open": (
            physical_sm_five_amplitude_equality["source_bound"] is True
            and physical_sm_five_amplitude_equality[
                "exact_radial_theorem_strictly_extended"
            ]
            is True
            and physical_sm_five_amplitude_equality[
                "five_real_amplitude_slice_stationary_equality_classified"
            ]
            is True
            and physical_sm_five_amplitude_equality[
                "exact_real_discrete_sign_variant_count"
            ]
            == 16
            and physical_sm_five_amplitude_equality[
                "target_strict_minimum_on_five_amplitude_slice"
            ]
            is True
            and physical_sm_five_amplitude_equality[
                "full_486_field_stationary_equality_classified"
            ]
            is False
            and physical_sm_five_amplitude_equality[
                "continuous_symmetry_orbit_equivalence_of_16_variants_proved"
            ]
            is False
            and physical_sm_five_amplitude_equality[
                "direct_source_algebra_full_486_Hessian_available"
            ]
            is False
            and physical_sm_five_amplitude_equality["physical_SM_G3_closed"]
            is False
            and physical_sm_five_amplitude_equality["physical_SM_G4_closed"]
            is False
            and physical_sm_five_amplitude_equality["physical_SM_G5_closed"]
            is False
        ),
        "physical_SM_hard_projector_bundle_exactly_closes_its_10_row_scope": (
            physical_sm_hard_projector_hessians["source_bound"] is True
            and physical_sm_hard_projector_hessians["exact_source_Hessian_row_count"] == 10
            and physical_sm_hard_projector_hessians["remaining_active_row_count"] == 27
            and physical_sm_hard_projector_hessians["all_10_O27_O44_source_Hessians_closed"] is True
            and physical_sm_hard_projector_hessians["all_37_active_source_Hessians_closed"] is False
            and physical_sm_hard_projector_hessians["full_witness_stationarity_rank_PSD_closed"] is False
            and physical_sm_hard_projector_hessians["full_486_global_equality_orbit_closed"] is False
            and physical_sm_hard_projector_hessians["physical_SM_G3_closed"] is False
            and physical_sm_hard_projector_hessians["physical_SM_G4_closed"] is False
            and physical_sm_hard_projector_hessians["physical_SM_G5_closed"] is False
        ),
        "physical_SM_last_six_bundle_makes_all_37_rows_available_for_the_aggregate": (
            physical_sm_last_six_hessians["source_bound"] is True
            and physical_sm_last_six_hessians[
                "exact_last_six_source_Hessians_closed"
            ]
            is True
            and physical_sm_last_six_hessians[
                "all_37_active_source_Hessians_available"
            ]
            is True
            and physical_sm_last_six_hessians[
                "exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"
            ]
            is False
            and physical_sm_last_six_hessians[
                "full_486_global_equality_orbit_closed"
            ]
            is False
            and all(
                physical_sm_last_six_hessians[f"physical_SM_{gate}_closed"]
                is False
                for gate in ("G3", "G4", "G5")
            )
        ),
        "physical_SM_exact_37_row_local_Hessian_closed_but_global_equality_G3_G5_open": (
            physical_sm_37_row_aggregate["source_bound"] is True
            and physical_sm_37_row_aggregate[
                "all_37_active_Hessians_source_derived"
            ]
            is True
            and physical_sm_37_row_aggregate[
                "exact_source_aggregate_value_minus_one_and_stationary"
            ]
            is True
            and physical_sm_37_row_aggregate[
                "exact_source_aggregate_kernel_dimension"
            ]
            == 38
            and physical_sm_37_row_aggregate["exact_source_aggregate_rank"] == 448
            and physical_sm_37_row_aggregate[
                "exact_source_aggregate_PSD_and_strict_mod_symmetry"
            ]
            is True
            and physical_sm_37_row_aggregate[
                "source_bound_local_stationary_Hessian_problem_complete"
            ]
            is True
            and physical_sm_37_row_aggregate[
                "full_486_global_equality_orbit_closed"
            ]
            is False
            and all(
                physical_sm_37_row_aggregate[f"physical_SM_{gate}_closed"]
                is False
                for gate in ("G3", "G4", "G5")
            )
        ),
        "physical_SM_full_486_local_equality_orbit_and_16_sign_orbit_closed_but_global_G3_G5_open": (
            physical_sm_local_equality_orbit["source_bound"] is True
            and physical_sm_local_equality_orbit[
                "full_486_local_stationary_orbit_classified"
            ]
            is True
            and physical_sm_local_equality_orbit[
                "full_486_local_stationary_equality_orbit_classified"
            ]
            is True
            and physical_sm_local_equality_orbit[
                "all_16_sign_variants_one_continuous_K_orbit"
            ]
            is True
            and physical_sm_local_equality_orbit[
                "target_orbit_strict_local_minimum_mod_K"
            ]
            is True
            and physical_sm_local_equality_orbit[
                "quantitative_neighborhood_radius_proved"
            ]
            is False
            and physical_sm_local_equality_orbit[
                "complete_486_global_equality_orbit_classified"
            ]
            is False
            and all(
                physical_sm_local_equality_orbit[f"physical_SM_{gate}_closed"]
                is False
                for gate in ("G3", "G4", "G5")
            )
        ),
        "physical_SM_five_amplitude_branch_mismatch_is_exact_but_G4_G8_open": (
            physical_sm_g4_g5_branch_mismatch["source_bound"] is True
            and physical_sm_g4_g5_branch_mismatch["exact_branch_mismatch_proved"] is True
            and physical_sm_g4_g5_branch_mismatch["unit_rescaling_case_count"] == 101
            and physical_sm_g4_g5_branch_mismatch["current_five_amplitude_target_is_canonical_physical_EW_branch"] is False
            and physical_sm_g4_g5_branch_mismatch["global_no_go_for_other_physical_EW_branches"] is False
            and all(
                physical_sm_g4_g5_branch_mismatch[f"physical_SM_G{gate}_closed"] is False
                for gate in range(4, 9)
            )
        ),
        "physical_SM_heavy_vectors_are_exact_scoped_and_G6_G7_open": (
            physical_sm_heavy_vector["source_bound"] is True
            and physical_sm_heavy_vector[
                "exact_parameterized_tree_vector_mass_matrix_closed"
            ]
            is True
            and physical_sm_heavy_vector[
                "exact_vector_rank_kernel_and_Goldstone_image_closed"
            ]
            is True
            and physical_sm_heavy_vector[
                "exact_SU3C_x_U1em_vector_sector_resolution_closed"
            ]
            is True
            and physical_sm_heavy_vector[
                "parameterized_vector_threshold_log_inputs_closed"
            ]
            is True
            and physical_sm_heavy_vector[
                "absolute_physical_vector_masses_closed"
            ]
            is False
            and physical_sm_heavy_vector["pole_vector_masses_closed"] is False
            and physical_sm_heavy_vector[
                "vector_Goldstone_ghost_matching_closed"
            ]
            is False
            and physical_sm_heavy_vector["physical_G6_closed"] is False
            and physical_sm_heavy_vector["physical_G7_closed"] is False
            and statuses["G6"] == STATUS_BLOCKED
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "physical_SM_heavy_vector_MSbar_kernel_is_exact_scoped_and_G6_G7_open": (
            physical_sm_heavy_vector_msbar["source_bound"] is True
            and physical_sm_heavy_vector_msbar[
                "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
            ]
            is True
            and physical_sm_heavy_vector_msbar[
                "finite_MSbar_vector_constant_closed"
            ]
            is True
            and physical_sm_heavy_vector_msbar[
                "Goldstone_double_count_guard_active"
            ]
            is True
            and physical_sm_heavy_vector_msbar[
                "arbitrary_Rxi_sector_resolved_matching_closed"
            ]
            is False
            and physical_sm_heavy_vector_msbar["pole_mass_conversion_closed"]
            is False
            and physical_sm_heavy_vector_msbar[
                "SM_symmetric_pre_EW_matching_closed"
            ]
            is False
            and physical_sm_heavy_vector_msbar["physical_G6_closed"] is False
            and physical_sm_heavy_vector_msbar["physical_G7_closed"] is False
            and statuses["G6"] == STATUS_BLOCKED
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "physical_SM_zero_background_Rxi_vacuum_cancellation_is_exact_scoped": (
            physical_sm_vector_rxi["source_bound"] is True
            and physical_sm_vector_rxi[
                "zero_background_Rxi_vacuum_determinant_cancellation_closed"
            ]
            is True
            and physical_sm_vector_rxi["all_37_broken_directions_closed"]
            is True
            and physical_sm_vector_rxi[
                "Goldstone_FPghost_double_count_guard_closed"
            ]
            is True
            and physical_sm_vector_rxi[
                "background_covariant_heat_kernel_matching_closed"
            ]
            is False
            and physical_sm_vector_rxi[
                "sector_resolved_general_background_determinants_closed"
            ]
            is False
            and physical_sm_vector_rxi["pole_vector_masses_closed"] is False
            and physical_sm_vector_rxi["physical_G6_closed"] is False
            and physical_sm_vector_rxi["physical_G7_closed"] is False
            and statuses["G6"] == STATUS_BLOCKED
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "conditional_physical_SM_scalar_spectrum_is_scoped_and_G6_open": (
            conditional_physical_sm_scalar_spectrum["source_bound"] is True
            and conditional_physical_sm_scalar_spectrum[
                "conditional_reconstructed_tree_scalar_spectrum_closed"
            ]
            is True
            and conditional_physical_sm_scalar_spectrum[
                "conditional_tree_Hessian_factorization_closed"
            ]
            is True
            and conditional_physical_sm_scalar_spectrum[
                "conditional_tree_sector_assignment_closed"
            ]
            is True
            and conditional_physical_sm_scalar_spectrum[
                "source_algebra_derived_tree_scalar_spectrum_closed"
            ]
            is False
            and conditional_physical_sm_scalar_spectrum[
                "physical_scalar_pole_spectrum_closed"
            ]
            is False
            and conditional_physical_sm_scalar_spectrum["physical_G6_closed"]
            is False
            and conditional_physical_sm_scalar_spectrum["release_G6_verified"]
            is False
            and statuses["G6"] == STATUS_BLOCKED
        ),
        "physical_SM_G6_G7_closure_frontier_is_exact_negative_result": (
            physical_sm_g6_g7_frontier["source_bound"] is True
            and physical_sm_g6_g7_frontier[
                "corrected_terminal_artifacts_composed"
            ]
            is True
            and physical_sm_g6_g7_frontier[
                "continuous_nonidentifiability_proved"
            ]
            is True
            and physical_sm_g6_g7_frontier[
                "minimal_closure_path_machine_readable"
            ]
            is True
            and len(physical_sm_g6_g7_frontier["minimal_closure_path"]) == 7
            and physical_sm_g6_g7_frontier["unique_pole_spectrum"] is False
            and physical_sm_g6_g7_frontier["unique_threshold_vector"] is False
            and physical_sm_g6_g7_frontier["unique_full_RGE_trajectory"]
            is False
            and physical_sm_g6_g7_frontier["physical_G6_closed"] is False
            and physical_sm_g6_g7_frontier["physical_G7_closed"] is False
            and physical_sm_g6_g7_frontier["release_G6_verified"] is False
            and physical_sm_g6_g7_frontier["release_G7_verified"] is False
            and statuses["G6"] == STATUS_BLOCKED
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "physical_SM_G8_identifiability_frontier_is_exact_negative_result": (
            physical_sm_g8_frontier["source_bound"] is True
            and physical_sm_g8_frontier["canonical_G8_contract_audited"] is True
            and physical_sm_g8_frontier[
                "continuous_absolute_scale_nonidentifiability_proved"
            ]
            is True
            and physical_sm_g8_frontier[
                "flavor_and_interference_nonidentifiability_audited"
            ]
            is True
            and physical_sm_g8_frontier[
                "repository_frozen_PDG_2025_single_channel_constraint_verified"
            ]
            is True
            and physical_sm_g8_frontier[
                "minimal_exhibited_joint_free_real_dimension"
            ]
            == 1
            and physical_sm_g8_frontier[
                "unique_proton_lifetime_or_distribution"
            ]
            is False
            and physical_sm_g8_frontier["physical_G8_closed"] is False
            and physical_sm_g8_frontier["release_G8_verified"] is False
            and physical_sm_g8_frontier["authoritative_G8_closed"] is False
            and physical_sm_g8_frontier[
                "whole_model_excluded_by_conditional_points"
            ]
            is False
            and physical_sm_g8_frontier["all_acceptance_criteria_pass"] is False
            and statuses["G8"] == STATUS_BLOCKED
        ),
        "recalculated_G7_input_view_supersedes_stale_broad_blockers": (
            physical_g7_recalculated_inputs["source_bound"] is True
            and physical_g7_recalculated_inputs[
                "all_resolved_scoped_inputs_closed"
            ]
            is True
            and all(
                physical_g7_recalculated_inputs[
                    "superseded_stale_blockers"
                ].values()
            )
            and all(
                value is False
                for value in physical_g7_recalculated_inputs[
                    "precise_open_inputs"
                ].values()
            )
            and physical_g7_recalculated_inputs["physical_G6_closed"] is False
            and physical_g7_recalculated_inputs["physical_G7_closed"] is False
            and physical_g7_recalculated_inputs["release_G7_verified"] is False
        ),
        "normalized_SO10_Yukawa_CGCs_are_exact_scoped_and_G7_open": (
            normalized_yukawa_cgcs["source_bound"] is True
            and normalized_yukawa_cgcs["normalized_10_CGCs_closed"] is True
            and normalized_yukawa_cgcs["normalized_126bar_CGCs_closed"] is True
            and normalized_yukawa_cgcs[
                "normalized_singlet_duality_CGC_closed"
            ]
            is True
            and normalized_yukawa_cgcs[
                "canonical_304_Weyl_sparse_embedding_closed"
            ]
            is True
            and normalized_yukawa_cgcs[
                "all_declared_representation_CGCs_closed"
            ]
            is True
            and normalized_yukawa_cgcs["flavor_boundary_values_closed"]
            is False
            and normalized_yukawa_cgcs["SARAH_Dot_conversion_closed"] is False
            and normalized_yukawa_cgcs[
                "full_one_two_loop_Yukawa_betas_closed"
            ]
            is False
            and normalized_yukawa_cgcs[
                "physical_threshold_matching_and_running_closed"
            ]
            is False
            and normalized_yukawa_cgcs["full_yukawa_sector_closed"] is False
            and normalized_yukawa_cgcs["physical_G7_closed"] is False
            and normalized_yukawa_cgcs["mathematical_G7_closed"] is False
            and normalized_yukawa_cgcs["release_G7_verified"] is False
            and statuses["G7"] == STATUS_BLOCKED
        ),
        "parallel_EFT_G4_G5_G6_G7_do_not_promote_authoritative_frontier": (
            statuses == expected_statuses
            and (
                contract_consistent
                or all(
                    statuses[name] == STATUS_BLOCKED
                    for name in ("G3", "G4", "G5", "G6", "G7", "G8")
                )
            )
        ),
        "consistent_contract_requires_tool_native_bound_evidence": bool(
            not declared_contract_consistent or contract_evidence_complete
        ),
        "legacy_pseudo_sarah_cannot_close_model_contract": bool(
            x_report.get("executable_scaffold_contract", {}).get(
                "model_syntax_class"
            )
            != "legacy_pseudo_sarah_metadata"
            or not contract_consistent
        ),
        "authoritative_contract_state_classified": contract_state_classified,
        "gauged_G1_character_report_executes": g1_report["n_failed"] == 0,
        "gauged_G1_contract_id_is_authoritative": (
            g1_report["model_contract_id"] == AUTHORITATIVE_CONTRACT_ID
        ),
        "gauged_G1_counts_are_28_44_51": (
            gauged_counts["hermitian_conjugacy_orbits"] == 28
            and gauged_counts["total_potential_orbit_multiplicity"] == 44
            and gauged_counts["total_real_potential_parameters"] == 51
        ),
        "gauged_G1_multiplicity_census_is_complete": (
            scoped["G1"]["multiplicity_census_complete"] is True
        ),
        "gauged_G1_component_tensor_theorem_is_source_bound_and_mathematically_closed": (
            g1_component_tensor_closure["source_bound"] is True
            and g1_component_tensor_closure[
                "mathematical_G1_closed_for_renormalizable_model"
            ]
            is True
            and scoped["G1"][
                "explicit_component_tensor_subset_integration_complete"
            ]
            is True
            and scoped["G1"]["full_G1_closed"] is True
        ),
        "gauged_G1_character_census_remains_multiplicity_only": (
            scoped["G1"]["character_census_remains_multiplicity_only"] is True
            and g1_report.get("flags", {}).get(
                "g1_explicit_tensor_subset_reaudit_open"
            )
            is True
            and g1_report.get("flags", {}).get("g1_closed") is False
        ),
        "full_G1_never_closes_without_source_bound_component_tensor_theorem": (
            statuses["G1"] != STATUS_CLOSED
            or (
                contract_consistent
                and g1_component_tensor_closure["source_bound"] is True
                and g1_component_tensor_closure[
                    "mathematical_G1_closed_for_renormalizable_model"
                ]
                is True
                and scoped["G1"][
                    "explicit_component_tensor_subset_integration_complete"
                ]
                is True
                and scoped["G1"]["full_G1_closed"] is True
            )
        ),
        "gauged_scalar_filter_executes": filter_report["n_failed"] == 0,
        "gauged_scalar_filter_enforces_X": filter_report[
            "declared_symmetry_contract"
        ]["continuous_X_imposed"]
        is True,
        "gauged_G2_dense_derivative_audit_passes": (
            g2_report["n_failed"] == 0
            and g2_report["model_contract_id"] == AUTHORITATIVE_CONTRACT_ID
            and g2_report["flags"]["G2_gauged_u1x_derivatives_certified"] is True
        ),
        "gauged_G2_mathematical_theorem_is_source_bound_and_closed": (
            g2_mathematical_closure["source_bound"] is True
            and g2_mathematical_closure[
                "mathematical_G2_closed_for_renormalizable_model"
            ]
            is True
            and scoped["G2"][
                "full_renormalizable_G2_mathematical_potential_closed"
            ]
            is True
        ),
        "gauged_G2_counts_are_44_51_486": (
            g2_report["counts"]["invariant_directions"] == 44
            and g2_report["counts"]["real_parameters"] == 51
            and g2_report["counts"]["real_field_dimension"] == 486
            and g2_report["counts"]["Hessian_shape_per_parameter"] == [486, 486]
        ),
        "gauged_G2_exact_rank_nullity_are_13_38": (
            scoped["G2"]["promoted_stationarity_rank"] == 13
            and scoped["G2"]["promoted_stationarity_nullity"] == 38
            and scoped["G2"]["raw_dense_rank_14_certified"] is False
            and scoped["G2"]["exact_Delta_R_projector_zero_certificate"] is True
            and scoped["G2"][
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            ] is True
            and scoped["G2"]["stationarity_rank_13_exactly_certified"] is True
            and scoped["G2"]["stationarity_nullity_38_exactly_certified"] is True
        ),
        "gauged_G1_and_G2_full_mathematical_calculations_are_complete": (
            gates["G1"]["scoped_calculation_complete"] is True
            and gates["G2"]["scoped_calculation_complete"] is True
            and gates["G2"]["full_gate_calculation_complete"] is True
            and gates["G1"]["full_gate_calculation_complete"]
            == scoped["G1"]["full_G1_closed"]
            and scoped["G2"]["authoritative_promotion_blocked_on_full_G1"]
            == (not scoped["G1"]["full_G1_closed"])
        ),
        "full_G2_never_closes_without_source_bound_mathematical_theorem": (
            statuses["G2"] != STATUS_CLOSED
            or (
                contract_consistent
                and statuses["G1"] == STATUS_CLOSED
                and g2_mathematical_closure["source_bound"] is True
                and g2_mathematical_closure[
                    "mathematical_G2_closed_for_renormalizable_model"
                ]
                is True
                and scoped["G2"][
                    "full_renormalizable_G2_mathematical_potential_closed"
                ]
                is True
            )
        ),
        "historical_sources_share_scoped_contract": historical_ids
        == {HISTORICAL_CONTRACT_ID},
        "historical_64_91_results_preserved": (
            historical["G1"]["invariant_directions"] == 64
            and historical["G1"]["real_potential_parameters"] == 91
        ),
        "historical_449_saddle_and_search_preserved": (
            historical["G3"]["massive_physical_quotient_dimension"] == 449
            and historical["G3"]["anchored_witness_negative_modes"] == 46
            and historical["G3"]["stability_search_iterations"] == 80
            and historical["G3"]["best_minimum_equilibrated_eigenvalue"]
            == -0.025502339625368114
        ),
        "gauged_G3_required_constructive_artifacts_present": all(
            g3_frontier["artifacts_present"].values()
        ),
        "gauged_G3_exact_A_square_recoupling_source_bound": (
            g3_frontier["exact_A_square_recoupling_source_bound"] is True
        ),
        "gauged_G3_exact_SOS_BFB_stationarity_source_bound": (
            g3_frontier["exact_SOS_BFB_stationarity_source_bound"] is True
        ),
        "gauged_G3_direct_exact_PD_rank_is_honestly_scoped": (
            g3_frontier["direct_exact_PD_rank_honestly_scoped"] is True
        ),
        "gauged_G3_SOS_candidate_exact_local_and_globally_rejected": (
            g3_frontier["SOS_candidate_exact_local_and_globally_rejected"] is True
        ),
        "gauged_G3_failed_branches_and_SU5_PD_frontier_exactly_classified": (
            g3_frontier["fixed_P_branch_exactly_excluded"] is True
            and g3_frontier[
                "lower_replacement_rejected_for_wrong_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_PD_exact_global_frontier"] is True
            and g3_frontier["SU5_Delta_PD_full_486_extension_open"] is True
            and g3_frontier[
                "SU5_Delta_PD_disconnected_equality_orbits_open"
            ]
            is False
            and g3_frontier["SU5_Delta_PD_equality_orbits_classified_exactly"]
            is True
        ),
        "gauged_G3_SU5_HSX_extension_is_promising_and_fail_closed": (
            g3_frontier["SU5_Delta_HSX_honest_frontier"] is True
            and g3_frontier["SU5_Delta_HSX_nonzero_real_parameters"] == 28
            and g3_frontier["SU5_Delta_HSX_maximum_absolute_coefficient"] == 11.0
            and g3_frontier["SU5_Delta_HSX_exact_symmetry_ranks"]
            == [36, 37, 38]
            and g3_frontier["SU5_Delta_HSX_transverse_dimension"] == 448
            and g3_frontier["SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric"]
            > 0.0
            and g3_frontier["SU5_Delta_HSX_full_Hessian_proof_grade"] is False
            and g3_frontier["SU5_Delta_HSX_full_quartic_BFB_exact"] is True
            and g3_frontier["SU5_Delta_HSX_finite_field_global_gap_open"] is True
            and g3_frontier[
                "SU5_Delta_HSX_global_equality_classification_open"
            ]
            is True
        ),
        "gauged_G3_SU5_HSX_full_Hessian_is_exactly_closed": (
            g3_frontier["SU5_Delta_HSX_exact_Hessian_closed"] is True
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_rank"] == 448
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_nullity"] == 38
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_PSD"] is True
            and g3_frontier[
                "SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_HSX_exact_quotient_positive"] is True
        ),
        "gauged_G3_SU5_equality_problem_is_exactly_reduced_and_fail_closed": (
            g3_frontier["SU5_Delta_equality_honestly_reduced"] is True
            and g3_frontier["SU5_Delta_Phi_orbit_audit_honest"] is True
            and g3_frontier[
                "SU5_Delta_literal_single_Phi_orbit_refuted"
            ]
            is True
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_open"] is False
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_closed"] is True
            and g3_frontier["SU5_Delta_SU4_Phi_slice_classified"] is True
            and g3_frontier[
                "SU5_Delta_signed_Phi_local_components_closed"
            ]
            is True
            and g3_frontier["SU5_Delta_distant_Phi_components_excluded"]
            is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"] is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"] == 16
            and g3_frontier["SU5_Delta_fixed_F_Sigma_one_orbit_exact"] is True
            and g3_frontier["SU5_Delta_diagonal_Phi_slice_one_orbit_exact"]
            is True
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_open"] is False
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_closed"] is True
            and g3_frontier[
                "SU5_Delta_global_Phi_orbit_theorem_core_sha256"
            ]
            == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
        ),
        "gauged_G3_SU5_chiral_global_gap_is_reduced_and_fail_closed": (
            g3_frontier["SU5_Delta_chiral_global_gap_honestly_reduced"] is True
            and g3_frontier["SU5_fixed_F_full_offkernel_gap_closed"] is True
            and g3_frontier["SU5_fixed_F_gap_equality_is_selected_flag"] is True
            and g3_frontier["SU5_arbitrary_Phi_offstratum_gap_open"] is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_route_excluded"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_strict_margin"
            ]
            == "7859/140295000"
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_gap_closed"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_minimum"
            ]
            == "1/5000"
            and g3_frontier[
                "SU5_arbitrary_Phi_nonzero_residual_cancellations_open"
            ]
            is False
            and g3_frontier[
                "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"
            ]
            is True
            and g3_frontier["SU5_arbitrary_Phi_uniform_coercivity_open"] is True
            and g3_frontier["SU5_Delta_chiral_lower_witness_found"] is False
            and g3_frontier["SU5_Delta_chiral_small_beta_route_exists"] is True
            and g3_frontier[
                "SU5_Delta_chiral_beta_1_over_20_global_certified"
            ]
            is False
            and g3_frontier[
                "SU5_Delta_chiral_final_acceptance_test_passes"
            ]
            is False
        ),
        "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed": (
            g3_frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
            is True
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_dimension"] == 4
            and g3_frontier["SU5_max_negative_rank1_SU3_ambient_dimension"]
            == 16
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_minimum"]
            == "1/5000"
            and g3_frontier["SU5_max_negative_arbitrary_rank1_Phi_open"]
            is True
            and g3_frontier[
                "SU5_max_negative_arbitrary_Sigma_orientation_open"
            ]
            is True
            and g3_frontier["G3_closed"] is False
        ),
        "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed": (
            g3_frontier["rank1_SU4_stabilizer_infrastructure_exact"] is True
            and g3_frontier["rank1_SU4_joint_stabilizer_dimension"] == 15
            and g3_frontier[
                "rank1_SU4_Phi210_intertwiner_infrastructure_exact"
            ]
            is True
            and g3_frontier["rank1_SU4_Phi210_carrier_count"] == 25
            and g3_frontier["rank1_SU4_Sym2_invariant_dimension"] == 45
            and g3_frontier["rank1_SU4_aligned_carriers_exact"] is True
            and g3_frontier["rank1_SU4_aligned_direct_sum_rank"] == 210
            and g3_frontier["rank1_SU4_physical_real_maps_exact"] is True
            and g3_frontier["rank1_SU4_Phi210_quadratic_basis_exact"] is True
            and g3_frontier["rank1_SU4_quadratic_constraint_shape"]
            == [5952, 551]
            and g3_frontier["rank1_SU4_quadratic_constraint_rank"] == 506
            and g3_frontier["rank1_SU4_quadratic_constraint_nullity"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_count"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_rank"] == 45
            and g3_frontier[
                "rank1_SU4_quadratic_live_invariance_exact"
            ] is True
            and g3_frontier["rank1_SU4_Schur_SOS_SDP_open"] is True
            and g3_frontier["rank1_SU4_arbitrary_Phi_bound_open"] is True
            and g3_frontier["rank1_SU4_augmented_SOS_census_exact"] is True
            and g3_frontier["rank1_SU4_augmented_homogeneous_dimension"]
            == 22_366
            and g3_frontier[
                "rank1_SU4_augmented_complex_isotypic_type_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_complex_irreducible_copy_count"
            ] == 824
            and g3_frontier["rank1_SU4_augmented_real_isotypic_block_count"]
            == 22
            and g3_frontier[
                "rank1_SU4_augmented_real_symmetric_block_count"
            ] == 9
            and g3_frontier[
                "rank1_SU4_augmented_complex_Hermitian_block_count"
            ] == 13
            and g3_frontier["rank1_SU4_augmented_Schur_real_parameter_count"]
            == 19_594
            and g3_frontier["rank1_SU4_augmented_invariant_equation_count"]
            == 6_585
            and g3_frontier["rank1_SU4_augmented_abstract_total_rank"]
            == 6_585
            and g3_frontier[
                "rank1_SU4_augmented_abstract_total_kernel_dimension"
            ] == 13_009
            and g3_frontier["rank1_SU4_augmented_coordinate_Schur_map_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_isotypic_maps_open"] is True
            and g3_frontier["rank1_SU4_augmented_physical_target_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_arbitrary_Phi_bound_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_cubic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_carrier_copy_count"
            ] == 540
            and g3_frontier[
                "rank1_SU4_augmented_cubic_real_variable_count"
            ] == 1_414
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_shape"
            ] == [478, 1_414]
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_nnz"
            ] == 3_145
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_rank"
            ] == 478
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"
            ] == 936
            and g3_frontier[
                "rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_other_graded_maps_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_full_coordinate_map_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_cubic_G3_open"] is True
            and g3_frontier["rank1_SU4_augmented_quartic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_carrier_family_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_quartic_irreducible_copy_count"
            ] == 798
            and g3_frontier[
                "rank1_SU4_augmented_quartic_real_block_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_shape"
            ] == [6_057, 18_085]
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_nnz"
            ] == 115_641
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_rank"
            ] == 6_057
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"
            ] == 12_028
            and g3_frontier[
                "rank1_SU4_augmented_quartic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_SDP_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_quartic_G3_open"] is True
            and g3_frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ] is True
            and g3_frontier["rank1_SU4_legacy_v20_physical_target_valid"]
            is False
            and g3_frontier["rank1_SU4_legacy_v20_primal_valid"] is False
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_route_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_parameter_count"
            ] == 19_594
            and g3_frontier[
                "rank1_SU4_augmented_real_type_PSD_congruences_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_complex_Hermitian_coordinates_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_fixed_endpoint_theorem_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_publication_manifest_sha256"
            ] == corrected_rank1.EXPECTED_MANIFEST_RAW_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_shape"
            ] == [6_585, 19_594]
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_common_denominator"
            ] == 256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_nnz"
            ] == 138_550
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_sha256"
            ] == corrected_rank1.EXPECTED_MAP_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_common_denominator"
            ] == 576_000
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_nonzero_count"
            ] == 512
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_sha256"
            ] == corrected_rank1.EXPECTED_TARGET_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_exact_coefficient_equalities"
            ] == 6_585
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_Gram_blocks"
            ] == 22
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_LDL_pivots"
            ] == 824
            and g3_frontier[
                "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_off_homogeneous_origin"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_A_greater_than_3_over_200_at_t1"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_p_zero_set_at_t1_empty"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_global_Sigma_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_general_H_proved"] is False
            and g3_frontier["rank1_SU4_corrected_full_H_proved"] is False
            and g3_frontier[
                "rank1_SU4_corrected_full_Hessian_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_G3_closed"] is False
            and g3_frontier["G3_closed"] is False
            and g3_frontier["whole_model_excluded"] is False
        ),
        "gauged_G3_alternative_global_SOS_routes_are_honestly_audited": (
            g3_frontier["alternative_global_SOS_audit_honestly_open"] is True
            and g3_frontier[
                "all_vanishing_global_SOS_replacements_excluded"
            ]
            is True
            and g3_frontier[
                "nonvanishing_residual_global_SOS_replacements_excluded"
            ]
            is False
        ),
        "gauged_G3_constructive_frontier_is_27_51_429_33_448": (
            g3_frontier["candidate_nonzero_real_parameters"] == 27
            and g3_frontier["candidate_real_parameter_count"] == 51
            and g3_frontier["candidate_maximum_absolute_coefficient"] == 9.125
            and g3_frontier["candidate_J0"] == "-21/200"
            and g3_frontier["exact_PD_rank"] == 429
            and g3_frontier["exact_PD_nullity"] == 33
            and g3_frontier["exact_full_Hessian_rank"] == 448
        ),
        "gauged_G3_local_minimum_and_global_counterexample_certified": (
            g3_frontier["integrity_pass"] is True
            and g3_frontier["direct_exact_PD_source_binding"] is True
            and g3_frontier["complete_potential_BFB_exactly_certified"] is True
            and g3_frontier[
                "selected_vacuum_stationarity_exactly_certified"
            ]
            is True
            and g3_frontier["strict_local_minimum_certified"] is True
            and g3_frontier["global_minimum_certified"] is False
            and g3_frontier["selected_global_minimum_disproved"] is True
            and g3_frontier[
                "exact_lower_energy_field_witness_certified"
            ]
            is True
            and g3_frontier["constructive_candidate_rejected_for_G3"] is True
            and g3_frontier["global_uniqueness_certified"] is False
            and g3_frontier["G3_closed"] is False
            and g3_frontier["whole_model_validated"] is False
            and g3_frontier["whole_model_excluded"] is False
        ),
        "dependency_graph_acyclic": _acyclic_dependencies(),
        "model_contract_precedes_G1": DEPENDENCIES["G1"] == ["MODEL_CONTRACT"],
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "gate_frontier_matches_contract_state": statuses == expected_statuses,
        "closed_gates_have_closed_dependencies": all(
            all(dependency_closed(parent) for parent in DEPENDENCIES[name])
            for name in closed
        ),
        "open_gates_have_closed_dependencies": all(
            all(dependency_closed(parent) for parent in DEPENDENCIES[name])
            for name in open_gates
        ),
        "G5_closure_respects_full_G1_G2_dependencies": (
            statuses["G5"] == expected_statuses["G5"]
            and not any(
                statuses[f"G{i}"] == STATUS_CLOSED for i in (3, 4, 6, 7, 8)
            )
        ),
        "whole_model_neither_validated_nor_excluded": (
            x_report["flag"]["whole_model_validated"] is False
            and x_report["flag"]["whole_model_excluded"] is False
            and historical["G3"]["whole_gauged_model_excluded"] is False
        ),
    }
    audit_failures = [name for name, passed in checks.items() if not passed]

    if audit_failures:
        status = "G1_G8_LEDGER_AUDIT_EXECUTION_FAILED"
        overall_state = "EXECUTION_FAIL"
    elif contract_consistent and statuses["G1"] == STATUS_CLOSED and statuses[
        "G2"
    ] == STATUS_CLOSED:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
            "G1_G2_G5_CLOSED__G3_GLOBAL_OPEN"
        )
        overall_state = STATUS_OPEN
    elif contract_consistent:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
            "G1_COMPONENT_TENSOR_INTEGRATION_OPEN__G2_DEPENDENCY_BLOCKED"
        )
        overall_state = STATUS_OPEN
    else:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED__"
            "MATHEMATICAL_G1_COMPONENT_RING_AND_G2_COMPONENT_POTENTIAL_CLOSED"
        )
        overall_state = STATUS_BLOCKED

    scientific_blockers = [
        "GAUGED_U1X_G3_G8_CLOSURE_REQUIRED",
        "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN",
        "G6_GLOBAL_EQUALITY_SCALE_FULL_MASS_MIXING_POLE_AND_THRESHOLD_INPUTS_REQUIRED",
        "G7_FULL_TWO_LOOP_SYSTEM_AND_COMPONENT_MATCHING_REQUIRED",
    ]
    if not g1_full_component_tensors_closed:
        scientific_blockers[0:0] = [
            "G1_EXPLICIT_COMPONENT_TENSOR_INTEGRATION_OPEN",
            "G2_AUTHORITATIVE_PROMOTION_BLOCKED_ON_FULL_G1",
        ]
    if not contract_consistent:
        scientific_blockers[0:0] = list(
            x_report.get("scientific_blockers") or [contract_blocker]
        )

    closure_waves = [
        {
            "wave": 0,
            "id": "MODEL_CONTRACT",
            "status": STATUS_CLOSED if contract_consistent else STATUS_BLOCKED,
            "deliverable": (
                "Execute the shipped hash-bound validation driver with a real "
                "SARAH installation and retain its v3 source-tree/runtime/log attestation."
            ),
        },
        {
            "wave": 1,
            "gates": ["G1"],
            "status": gates["G1"]["status"],
            "scoped_calculation_status": (
                "SOURCE_BOUND_FULL_RENORMALIZABLE_G1_MATHEMATICAL_RING_CLOSED"
            ),
            "deliverable": (
                "Promote the source-bound 44-direction/51-parameter mathematical "
                "G1 theorem only after the external SARAH contract attestation."
            ),
        },
        {
            "wave": 2,
            "gates": ["G2"],
            "status": gates["G2"]["status"],
            "scoped_calculation_status": (
                "SOURCE_BOUND_FULL_RENORMALIZABLE_G2_MATHEMATICAL_POTENTIAL_CLOSED"
            ),
            "deliverable": (
                "Promote the source-bound complete 44/51/486 mathematical component "
                "potential after the external SARAH contract is authoritative."
            ),
        },
        {
            "wave": 3,
            "gates": ["G3", "G4", "G5"],
            "status": (
                "G3_OPEN__G4_BLOCKED_ON_G3__G5_CLOSED"
                if statuses["G3"] == STATUS_OPEN
                else "BLOCKED_ON_G2"
            ),
            "deliverable": (
                "Promote the source-bound BFB, exact selected stationarity, and "
                "strict-local-minimum certificate after contract repair, while "
                "retaining the exact counterexample that rejects globality. To "
                "close G3, prove uniform coercivity for arbitrary non-pure-Delta "
                "Sigma orientations on the surviving SU(5)+Delta chiral-H "
                "branch. Its full 486-real Hessian is now exactly PSD "
                "with rank/nullity 448/38 and symmetry kernel exactly 38; the "
                "complete maximally-negative pure-Delta sector is already "
                "excluded for arbitrary real Phi and nonzero residuals with "
                "sharp gap 1/5000. The prior four-real-dimensional SU(3) "
                "regression is historical and subsumed. At fixed H=h_- and "
                "Sigma=q/4, the corrected v21 exact theorem covers every real "
                "Phi210. Its exact SU(4) "
                "stabilizer, aligned rank-210 carrier real maps, and explicit "
                "complete 45-element Phi210 invariant quadratic basis feed an "
                "exact 22366-dimensional augmented census with 35 isotypic "
                "types/824 copies, 22 real/Hermitian blocks, 19594 Schur "
                "parameters, and 6585 invariant rows. The complete cubic "
                "interface is explicit: all 1414 real cross variables map "
                "through a 478x1414 integer matrix of exact rank 478 and kernel "
                "dimension 936. Its zero placeholder is not a physical target. "
                "The homogeneous quartic interface is also exact: its "
                "6057x18085 integer map has rank 6057 and kernel dimension "
                "12028. The legacy v20 assembled physical target is rejected. "
                "The corrected 6585x19594 standard positive-Gram map, corrected "
                "ordered-spectral target, and exact strict 22-block/824-pivot "
                "primal prove p(t,Phi)>0 off the homogeneous origin, hence "
                "A(Phi)>3/200 at t=1 for every real Phi210. For that "
                "historical fixed-H/Sigma frontier, global Sigma, general/full "
                "H, and its then-unassembled Hessian remained open. The current "
                "physical-SM branch instead has an exact source-derived 37-row "
                "Hessian; its complete global equality orbit and physical G3 "
                "remain open."
            ),
        },
        {
            "wave": 4,
            "gates": ["G6"],
            "status": "BLOCKED__LOCAL_SOURCE_HESSIAN_CLOSED__GLOBAL_EQUALITY_SCALE_MASS_MIXING_POLE_THRESHOLD_AND_RELEASE_G6_OPEN",
            "deliverable": (
                "Preserve the formal SU(3)_C x U(1)_89 factorization only as an "
                "abstract result. The corrected SU(3)_C x U(1)_em target and "
                "stabilizer, conditional reconstructed 486-state scalar tree "
                "spectrum, and exact parameterized heavy-vector matrix, provenance, "
                "rank/kernel, sectors, and threshold logs are closed scoped inputs. "
                "The exact source-derived all-37 Hessian is stationary at V=-1, "
                "has kernel/rank 38/448, and is PSD strictly modulo symmetry. "
                "Classify the complete global equality orbit, fix absolute scales "
                "and couplings, construct the full scalar and fermion mass/mixing "
                "matrices, solve the scalar/vector/fermion pole self-energies, and "
                "complete all thresholds."
            ),
        },
        {
            "wave": 5,
            "gates": ["G7"],
            "status": "BLOCKED__PHYSICAL_G6_INPUT_AND_FULL_TWO_LOOP_MATCHING_OPEN",
            "deliverable": (
                "Start from the corrected physical G6 spectrum, then complete "
                "the Yukawa/scalar/EFT two-loop system, absolute scale and Wilson "
                "matching, and stage-by-stage component thresholds. The exact "
                "gauge-only polynomial and formal G89 determinants are scoped "
                "subtheorems, not physical G7 closure."
            ),
        },
        {"wave": 6, "gates": ["G8"], "status": "BLOCKED_ON_G3_G6_G7"},
    ]

    verdict = (
        "The ledger audit succeeds and the repaired gauged-U(1)_X contract "
        "promotes full G1, including the multiplicity census and explicit "
        "component tensors, plus the G2 dense derivative theorem to CLOSED. A "
        "perturbative 27-of-51 SOS candidate with J0=-21/200 has a "
        "source-bound complete-potential BFB proof, exact stationarity, direct "
        "P+Delta rank/nullity 429/33, and a proof of positivity on all 448 "
        "transverse Hessian directions. The selected orbit is a strict local "
        "minimum, but an exact field witness is lower by 25*r^4/19008 and "
        "rejects it as the global vacuum. The fixed-P branch is now excluded "
        "exactly, and its lower replacement has the wrong gauge stabilizer. A "
        "new SU(5)+Delta branch is an exact global Phi/Sigma minimum with exact "
        "quotient rank 429. The later provenance audit shows that its frozen "
        "abelian stabilizer is U(1)_89, not physical electromagnetism. Its chiral-H full "
        "Hessian is exactly PSD with rank/nullity 448/38 and kernel precisely the "
        "38 symmetry tangents. The complete maximally-negative pure-Delta sector "
        "is excluded for arbitrary real Phi and all nonzero residuals, with sharp "
        "gap 1/5000. The prior four-real-dimensional SU(3) regression is "
        "historical and subsumed. At fixed H=h_- and Sigma=q/4, the corrected "
        "v21 exact theorem covers every real Phi210. The "
        "exact SU(4) stabilizer, aligned rank-210 carrier real maps, and explicit "
        "complete 45-element Phi210 invariant quadratic basis feed the exact "
        "22366-dimensional augmented census (35 types/824 copies, 22 blocks, "
        "19594 parameters, 6585 rows). The complete cubic Schur interface is "
        "explicit, with 1414 real variables and an exact-rank-478, 478x1414 "
        "integer map whose kernel has dimension 936. Its reserved zero vector "
        "is not a physical G3 target. The exact quartic Schur map has shape "
        "6057x18085, rank 6057, and kernel dimension 12028. The legacy v20 "
        "assembled physical target is rejected. The corrected 6585x19594 "
        "standard positive-Gram map, ordered-spectral target, and exact strict "
        "22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin, "
        "hence A(Phi)>3/200 at t=1 for every real Phi210. For that historical "
        "fixed-H/Sigma frontier, global Sigma, general/full H, and its "
        "then-unassembled Hessian remained open. The current physical-SM branch "
        "instead has an exact source-derived 37-row Hessian; its complete global "
        "equality orbit and physical G3 remain open. "
        "G5 is CLOSED; G4 and G6-G8 remain "
        "dependency-blocked. Historical "
        "Option-C evidence remains scoped and closes no gauged-model gate."
        if contract_consistent
        and statuses["G1"] == STATUS_CLOSED
        and statuses["G2"] == STATUS_CLOSED
        else "The ledger audit succeeds, but all G1-G8 gates are BLOCKED. The "
        "gauged-U(1)_X SARAH input, charge catalogues, Lagrangian registration, "
        "and hash-bound validation bundle are now statically consistent; Wave 0 "
        "still requires a real external SARAH execution attestation. The gauged G1 "
        "multiplicity census, source-bound normalized component-tensor ring, and G2 "
        "dense derivative theorem are recertified as 44 directions, 51 parameters, "
        "18 tensor families, and 486 fields. Three structural gradient "
        "columns vanish exactly; matching exact lower- and upper-rank certificates "
        "prove stationarity rank/nullity 13/38. "
        "The character census remains explicitly multiplicity-only; the separate G1 "
        "theorem supplies its complete source-bound tensor integration without changing "
        "that census scope. G1 and the G2 scoped audit cannot be promoted until the "
        "external model contract closes. A perturbative "
        "27-of-51 SOS candidate with J0=-21/200 is explicit. Exact source-bound "
        "SOS identities prove complete-potential BFB and stationarity. Direct "
        "Gaussian-integer/Fraction/Q(sqrt(2)) assembly gives P+Delta rank/nullity "
        "429/33, and the exact extension leaves only 38 symmetry tangents, proving "
        "a strict local minimum on all 448 transverse directions. An exact "
        "symmetry-inequivalent field configuration is lower by 25*r^4/19008, "
        "so this selected global vacuum and candidate are rejected. The fixed-P "
        "branch is exactly excluded, and the lower stationary replacement has "
        "the wrong gauge symmetry. A new SU(5)+Delta Phi/Sigma branch has an "
        "exact global SOS minimum and exact quotient rank/nullity 429/33. Its "
        "chiral-H full-field extension is exactly BFB and stationary for the "
        "frozen representative. The provenance audit identifies its abelian "
        "stabilizer as U(1)_89 rather than physical electromagnetism. The "
        "source-bound 486-real Hessian is "
        "exactly PSD with rank/nullity 448/38, and its kernel is exactly the 38 "
        "symmetry tangents. The literal one-orbit Phi lemma is refuted by -F; the "
        "complete maximally-negative pure-Delta sector is excluded for arbitrary "
        "real Phi and all nonzero residuals with sharp gap 1/5000. The prior "
        "four-real-dimensional SU(3) regression is historical and subsumed. "
        "At fixed H=h_- and Sigma=q/4, the corrected v21 exact theorem covers "
        "every real Phi210. Its exact SU(4) stabilizer, aligned "
        "rank-210 carrier real maps, explicit complete 45-element Phi210 "
        "invariant quadratic basis, and exact augmented census are certified. "
        "The complete cubic interface now has all 1414 real Schur cross "
        "variables and an exact-rank-478, 478x1414 map with kernel dimension "
        "936; its abstract zero placeholder is not the physical gap target. "
        "The homogeneous quartic interface is now an exact-rank-6057, "
        "6057x18085 map with kernel dimension 12028. The legacy v20 assembled "
        "physical target is rejected. The corrected 6585x19594 standard "
        "positive-Gram map, ordered-spectral target, and exact strict "
        "22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin, "
        "hence A(Phi)>3/200 at t=1 for every real Phi210. For that historical "
        "fixed-H/Sigma frontier, global Sigma, general/full H, and its "
        "then-unassembled Hessian remained open. The current physical-SM branch "
        "instead has an exact source-derived 37-row Hessian; its complete global "
        "equality orbit and physical G3 remain open. The "
        "historical 64/91 "
        "derivative theorem, 449-dimensional "
        "quotient, 46-mode saddle, and 80-iteration no-PSD search are preserved "
        "as Option-C subtheorems and neither validate nor exclude the gauged model."
    )
    if contract_consistent and statuses["G1"] == STATUS_OPEN:
        verdict = (
            "The ledger audit succeeds and the gauged-U(1)_X executable contract "
            "is consistent, but full G1 remains OPEN. Its exact renormalizable "
            "multiplicity census is complete at 28 Hermitian conjugacy orbits, "
            "44 invariant directions, and 51 real parameters; the explicit "
            "component-tensor/Clebsch integration is still open. The exact "
            "44/51/486 G2 derivative and Ward-identity audit is a complete scoped "
            "subtheorem with stationarity rank/nullity 13/38, but authoritative "
            "G2 remains dependency-BLOCKED until full G1 closes. Consequently G3, "
            "G4, G5, G6, G7, and G8 remain dependency-BLOCKED, and no full-model "
            "gate is promoted by contract repair alone. Historical Option-C "
            "evidence remains scoped and closes no gauged-model gate."
        )
    verdict += (
        " In the dimension-six EFT namespace, the frozen 486-degree tree mass "
        "factorization remains exact as a formal SU(3)_C x U(1)_89 result: it "
        "contains 38 zero roots and 448 positive roots. The source-bound "
        "provenance audit proves that U(1)_89 is not standard electromagnetism "
        "and that the standard SM projectors do not commute with the frozen "
        "mass pencil. Physical/mathematical, release, and authoritative G6 are "
        "therefore all false. A corrected SU(3)_C x U(1)_em target/stabilizer, "
        "a conditional reconstructed 486-state scalar tree spectrum, and an exact "
        "parameterized heavy-vector tree matrix with physical provenance, rank/kernel, "
        "sector resolution, and threshold-log inputs are now closed scoped results. "
        "The exact source-derived all-37 physical-branch Hessian, stationarity, "
        "38-dimensional symmetry kernel, rank 448, and PSD certificate are closed. "
        "Physical G6 still requires the complete global equality-orbit proof, "
        "absolute scales and couplings, full scalar and fermion mass/mixing "
        "matrices with pole self-energies, and complete thresholds."
        if parallel_eft_g6_spectrum[
            "formal_SU3_x_U1_89_tree_factorization_closed"
        ]
        else " The corrected formal G6 spectrum view is missing or invalid."
    )
    verdict += (
        " The parameterized calculation closes only formal SU(3)_C x U(1)_89 "
        "scalar determinants and proves the absolute scale/Wilson family is "
        "unidentified. The corrected authoritative gauge-only one/two-loop "
        "polynomial is exact. The physical PS/SM matter branching and "
        "parameterized one-loop matter threshold kernel are also exact. "
        "The normalized 10/126bar/singlet representation CGCs and canonical sparse "
        "304-Weyl embedding are exact, as are the parameterized physical-SM vector "
        "tree inputs. The combined heavy-vector/FP-ghost/Goldstone non-supersymmetric "
        "MS-bar kernel and its finite vector constant are exact, with all 37 eaten "
        "directions guarded against scalar double counting. The zero-background "
        "vacuum determinant cancellation is exact for arbitrary positive R_xi "
        "across all 37 broken directions; this is not a background-covariant "
        "heat-kernel or pole-mass result. Exact vector-scale, scalar-b, and flavor "
        "families prove the remaining absolute spectrum, threshold vector, and full "
        "flow are not identifiable from the frozen inputs. SARAH implicit/identical-"
        "Weyl contraction conversion, flavor "
        "tensors and boundaries, the complete Yukawa/scalar/dimensionful/EFT flow, "
        "background-covariant general-field determinants, the stationary "
        "pre-electroweak matching stage, tree-to-pole conversion with a declared "
        "tadpole/VEV scheme, complete scalar/fermion thresholds, physical scale and "
        "running boundaries remain open. Mathematical, "
        "release, and authoritative G7 are false, and G8 remains dependent on G7."
        if g6_g7_parameterized_matching["source_bound"]
        and authoritative_gauge_betas["source_bound"]
        and physical_g7_component_threshold["source_bound"]
        and physical_sm_heavy_vector_msbar["source_bound"]
        and physical_sm_vector_rxi["source_bound"]
        and physical_sm_g6_g7_frontier["source_bound"]
        else " The corrected G7 subtheorem bundle is missing or invalid."
    )

    return {
        "status": status,
        "overall_state": overall_state,
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "declared_contract_consistent": declared_contract_consistent,
        "contract_evidence_complete": contract_evidence_complete,
        "contract_consistent": contract_consistent,
        "scientific_blockers": scientific_blockers,
        "n_checks": len(checks),
        "n_failed": len(audit_failures),
        "failures": audit_failures,
        "audit_failures": audit_failures,
        "checks": checks,
        "model_contract_reports": {
            "exact_X": x_report,
            "gauged_G1_character_census": g1_report,
            "gauged_G1_component_tensor_closure": g1_component_tensor_report,
            "gauged_G2_derivative_audit": g2_report,
            "gauged_G2_mathematical_closure": g2_mathematical_report,
            "gauged_scalar_filter": filter_report,
            "gauged_G3_SOS_candidate": g3_sos_report,
            "gauged_G3_direct_exact_PD_rank": g3_pd_report,
            "gauged_G3_exact_A_square_recoupling": g3_a_square_report,
            "gauged_G3_exact_SOS_BFB_stationarity": g3_sos_bfb_report,
            "gauged_G3_fixed_P_kernel_no_go": g3_kernel_bound_report,
            "gauged_G3_lower_replacement_orbit": g3_replacement_report,
            "gauged_G3_SU5_Delta_PD_global_SOS": g3_su5_pd_report,
            "gauged_G3_SU5_Delta_HSX_extension": g3_su5_hsx_report,
            "gauged_G3_SU5_Delta_HSX_exact_Hessian": (
                g3_su5_hsx_exact_hessian_report
            ),
            "gauged_G3_SU5_Delta_equality_orbit": g3_su5_equality_report,
            "gauged_G3_SU5_Delta_Phi_orbit_lemma_audit": (
                g3_su5_phi_orbit_report
            ),
            "gauged_G3_SU5_Delta_Phi_local_component_theorem": (
                g3_su5_phi_local_component_report
            ),
            "gauged_G3_SU5_Delta_Phi_SU3_fixed_slice_theorem": (
                g3_su5_phi_su3_slice_report
            ),
            "gauged_G3_SU5_Delta_chiral_global_gap": g3_su5_gap_report,
            "gauged_G3_SU5_fixed_F_full_offkernel_bound": (
                g3_su5_fixed_f_offkernel_report
            ),
            "gauged_G3_SU5_max_negative_all_zero_residual_bound": (
                g3_su5_max_negative_zero_residual_report
            ),
            "gauged_G3_SU5_max_negative_full_residual_pure_Delta_bound": (
                g3_su5_max_negative_full_residual_report
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound": (
                g3_su5_max_negative_rank1_su3_slice_report
            ),
            "gauged_G3_rank1_SU4_stabilizer_infrastructure": (
                g3_rank1_su4_stabilizer_report
            ),
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure": (
                g3_rank1_su4_phi210_intertwiners_report
            ),
            "gauged_G3_rank1_SU4_aligned_carrier_infrastructure": (
                g3_rank1_su4_aligned_carriers_report
            ),
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis": (
                g3_rank1_su4_phi210_quadratic_basis_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_census": (
                g3_rank1_su4_augmented_sos_census_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_cubic_map": (
                g3_rank1_su4_augmented_sos_cubic_map_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_quartic_map": (
                g3_rank1_su4_augmented_sos_quartic_map_report
            ),
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target": (
                g3_rank1_su4_augmented_sos_psd_target_report
            ),
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21": (
                g3_rank1_su4_corrected_publication
            ),
            "gauged_G3_alternative_global_SOS_audit": (
                g3_alternative_global_sos_report
            ),
            "parallel_EFT_G3_acceptance_gate": final_g3_eft_acceptance_report,
            "parallel_EFT_G4_mathematical_gate": (
                final_g4_eft_mathematical_report
            ),
            "parallel_EFT_G5_mathematical_gate": (
                final_g5_eft_mathematical_report
            ),
            "parallel_EFT_G6_mathematical_gate": (
                final_g6_eft_mathematical_report
            ),
            "G6_SM_provenance_feasibility_audit": g6_sm_provenance_report,
            "G6_G7_parameterized_formal_G89_matching": (
                g6_g7_parameterized_matching_report
            ),
            "authoritative_SO10_U1X_gauge_beta_subtheorem": (
                authoritative_gauge_betas_report
            ),
            "independent_PyRATE3_gauge_beta_replay": (
                pyrate3_gauge_replay_report
            ),
            "parallel_EFT_G7_input_nonidentifiability": (
                eft_g7_nonidentifiability_report
            ),
            "physical_G7_component_threshold_contract": (
                physical_g7_component_threshold_report
            ),
            "normalized_SO10_Yukawa_CGCs": normalized_yukawa_cgcs_report,
            "physical_SM_vacuum_local_feasibility": physical_sm_vacuum_report,
            "physical_SM_source_algebra_equality_frontier": (
                physical_sm_source_equality_report
            ),
            "physical_SM_five_amplitude_equality": (
                physical_sm_five_amplitude_equality_report
            ),
            "physical_SM_hard_projector_Hessians": (
                physical_sm_hard_projector_hessians_report
            ),
            "physical_SM_last_six_Hessians": (
                physical_sm_last_six_hessians_report
            ),
            "physical_SM_37_row_aggregate": (
                physical_sm_37_row_aggregate_report
            ),
            "physical_SM_local_equality_orbit": (
                physical_sm_local_equality_orbit_report
            ),
            "physical_SM_G4_G5_branch_mismatch": (
                physical_sm_g4_g5_branch_mismatch_report
            ),
            "physical_SM_heavy_vector_masses": physical_sm_heavy_vector_report,
            "physical_SM_heavy_vector_MSbar_matching": (
                physical_sm_heavy_vector_msbar_report
            ),
            "physical_SM_vector_Rxi_vacuum_cancellation": (
                physical_sm_vector_rxi_report
            ),
            "conditional_physical_SM_EFT_Hessian_spectrum": (
                conditional_physical_sm_scalar_spectrum_report
            ),
            "physical_SM_G6_G7_closure_frontier": (
                physical_sm_g6_g7_frontier_report
            ),
            "physical_SM_G8_identifiability_frontier": (
                physical_sm_g8_frontier_report
            ),
        },
        "exact_X_v3_fail_closed_contract": exact_x_v3_contract,
        "renormalizable_G1_component_tensor_closure": (
            g1_component_tensor_closure
        ),
        "renormalizable_G2_mathematical_closure": g2_mathematical_closure,
        "gauged_u1x_scalar_subtheorems": scoped,
        "gauged_u1x_g3_constructive_frontier": g3_frontier,
        "parallel_EFT_G3_acceptance": parallel_eft_g3_acceptance,
        "parallel_EFT_G4_mathematical": parallel_eft_g4_mathematical,
        "parallel_EFT_G5_mathematical": parallel_eft_g5_mathematical,
        "parallel_EFT_G6_spectrum": parallel_eft_g6_spectrum,
        "G6_SM_provenance_audit": g6_sm_provenance,
        "G6_G7_parameterized_matching": g6_g7_parameterized_matching,
        "authoritative_gauge_beta_subtheorem": authoritative_gauge_betas,
        "independent_PyRATE3_gauge_replay": pyrate3_gauge_replay,
        "parallel_EFT_G7_nonidentifiability": (
            parallel_eft_g7_nonidentifiability
        ),
        "physical_G7_component_threshold_contract": (
            physical_g7_component_threshold
        ),
        "normalized_SO10_Yukawa_CGC_contract": normalized_yukawa_cgcs,
        "physical_SM_vacuum_truth_overlay": physical_sm_vacuum,
        "physical_SM_source_algebra_equality_frontier": (
            physical_sm_source_equality
        ),
        "physical_SM_five_amplitude_equality_contract": (
            physical_sm_five_amplitude_equality
        ),
        "physical_SM_hard_projector_Hessians_contract": (
            physical_sm_hard_projector_hessians
        ),
        "physical_SM_last_six_Hessians_contract": (
            physical_sm_last_six_hessians
        ),
        "physical_SM_37_row_aggregate_contract": (
            physical_sm_37_row_aggregate
        ),
        "physical_SM_local_equality_orbit_contract": (
            physical_sm_local_equality_orbit
        ),
        "physical_SM_G4_G5_branch_mismatch_contract": (
            physical_sm_g4_g5_branch_mismatch
        ),
        "physical_SM_heavy_vector_mass_contract": physical_sm_heavy_vector,
        "physical_SM_heavy_vector_MSbar_matching_contract": (
            physical_sm_heavy_vector_msbar
        ),
        "physical_SM_vector_Rxi_vacuum_cancellation_contract": (
            physical_sm_vector_rxi
        ),
        "conditional_physical_SM_EFT_Hessian_spectrum_contract": (
            conditional_physical_sm_scalar_spectrum
        ),
        "physical_SM_G6_G7_closure_frontier_contract": (
            physical_sm_g6_g7_frontier
        ),
        "physical_SM_G8_identifiability_frontier_contract": (
            physical_sm_g8_frontier
        ),
        "physical_G7_recalculated_input_resolution": (
            physical_g7_recalculated_inputs
        ),
        "historical_option_c_subtheorems": historical,
        "dependencies": DEPENDENCIES,
        "gates": gates,
        "summary": {
            "closed": closed,
            "partial": partial,
            "open": open_gates,
            "blocked": blocked,
            "n_closed": len(closed),
            "n_partial": len(partial),
            "n_open": len(open_gates),
            "n_blocked": len(blocked),
        },
        "closure_waves": closure_waves,
        "feasibility": {
            "closure_program_defined": True,
            "current_authoritative_closed_gates": len(closed),
            "historical_subtheorems_reusable_after_contract_filtering": True,
            "gauged_G1_multiplicity_census_complete": scoped["G1"][
                "multiplicity_census_complete"
            ],
            "gauged_G1_full_component_tensor_integration_complete": scoped["G1"][
                "full_G1_closed"
            ],
            "gauged_G2_dense_derivative_scoped_subtheorem_complete": scoped["G2"][
                "scoped_derivative_audit_complete"
            ],
            "gauged_G2_full_mathematical_component_potential_complete": scoped[
                "G2"
            ]["full_renormalizable_G2_mathematical_potential_closed"],
            "gauged_G3_constructive_candidate_available": g3_frontier[
                "integrity_pass"
            ],
            "gauged_G3_direct_exact_source_binding_complete": g3_frontier[
                "direct_exact_PD_source_binding"
            ]
            is True,
            "guarantee_model_survives_recertification": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": verdict,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    return _build_report_from_inputs(
        x_report=exact_x.build_report(),
        g1_report=gauged_g1.build_report(),
        g2_report=_load_or_build_gauged_g2_report(),
        filter_report=gauged_filter.build_report(),
        g3_sos_report=_load_json_artifact(G3_SOS_JSON),
        g3_pd_report=_load_json_artifact(G3_PD_JSON),
        g3_a_square_report=_load_json_artifact(G3_A_SQUARE_JSON),
        g3_sos_bfb_report=_load_json_artifact(G3_SOS_BFB_JSON),
        g3_kernel_bound_report=_load_json_artifact(G3_KERNEL_BOUND_JSON),
        g3_replacement_report=_load_json_artifact(G3_REPLACEMENT_JSON),
        g3_su5_pd_report=_load_json_artifact(G3_SU5_PD_JSON),
        g3_su5_hsx_report=_load_json_artifact(G3_SU5_HSX_JSON),
        g3_su5_hsx_exact_hessian_report=_load_json_artifact(
            G3_SU5_HSX_EXACT_HESSIAN_JSON
        ),
        g3_su5_equality_report=_load_json_artifact(G3_SU5_EQUALITY_JSON),
        g3_su5_phi_orbit_report=_load_json_artifact(G3_SU5_PHI_ORBIT_JSON),
        g3_su5_phi_local_component_report=_load_json_artifact(
            G3_SU5_PHI_LOCAL_COMPONENT_JSON
        ),
        g3_su5_phi_su3_slice_report=_load_json_artifact(
            G3_SU5_PHI_SU3_SLICE_JSON
        ),
        g3_su5_gap_report=_load_json_artifact(G3_SU5_GAP_JSON),
        g3_su5_fixed_f_offkernel_report=_load_json_artifact(
            G3_SU5_FIXED_F_OFFKERNEL_JSON
        ),
        g3_su5_max_negative_zero_residual_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON
        ),
        g3_su5_max_negative_full_residual_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON
        ),
        g3_su5_max_negative_rank1_su3_slice_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON
        ),
        g3_rank1_su4_stabilizer_report=_load_json_artifact(
            G3_RANK1_SU4_STABILIZER_JSON
        ),
        g3_rank1_su4_phi210_intertwiners_report=_load_json_artifact(
            G3_RANK1_SU4_PHI210_INTERTWINERS_JSON
        ),
        g3_rank1_su4_aligned_carriers_report=_load_json_artifact(
            G3_RANK1_SU4_ALIGNED_CARRIERS_JSON
        ),
        g3_rank1_su4_phi210_quadratic_basis_report=_load_json_artifact(
            G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON
        ),
        g3_rank1_su4_augmented_sos_census_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON
        ),
        g3_rank1_su4_augmented_sos_cubic_map_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON
        ),
        g3_rank1_su4_augmented_sos_quartic_map_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON
        ),
        g3_rank1_su4_augmented_sos_psd_target_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON
        ),
        g3_rank1_su4_corrected_publication=(
            corrected_rank1.load_validated_publication()
        ),
        g3_alternative_global_sos_report=_load_json_artifact(
            G3_ALTERNATIVE_GLOBAL_SOS_JSON
        ),
        final_g3_eft_acceptance_report=_load_json_artifact(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        ),
        final_g3_eft_acceptance_raw_sha256=_raw_file_sha256(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        ),
        final_g4_eft_mathematical_report=_load_json_artifact(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        ),
        final_g4_eft_mathematical_raw_sha256=_raw_file_sha256(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        ),
        final_g5_eft_mathematical_report=_load_json_artifact(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        ),
        final_g5_eft_mathematical_raw_sha256=_raw_file_sha256(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        ),
    )


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# G1-G8 contract-aware gate ledger - v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        f"**Contract consistent:** `{report['contract_consistent']}`",
        "",
        report["verdict"],
        "",
        "## Critical path",
        "",
        "`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`",
        "",
        "## Parallel EFT G3-G7 classifications",
        "",
        (
            "- Exact-X v3 trusted SARAH 4.15.3 tree bound / external runtime "
            "attestation present / authoritative G1: "
            f"**{report['exact_X_v3_fail_closed_contract']['trusted_SARAH_4_15_3_source_tree_manifest_closed']}**/"
            f"**{report['exact_X_v3_fail_closed_contract']['external_v3_execution_attestation_present']}**/"
            f"**{report['exact_X_v3_fail_closed_contract']['authoritative_G1_closed']}**"
        ),
        (
            "- Dimension-six EFT mathematical G3: "
            f"**{report['parallel_EFT_G3_acceptance']['mathematical_G3_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G3 verified: "
            f"**{report['parallel_EFT_G3_acceptance']['release_G3_verified_for_EFT_model']}**"
        ),
        (
            "- Dimension-six EFT mathematical G4: "
            f"**{report['parallel_EFT_G4_mathematical']['mathematical_G4_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G4 verified: "
            f"**{report['parallel_EFT_G4_mathematical']['release_G4_verified_for_EFT_model']}**"
        ),
        (
            "- Dimension-six EFT mathematical G5: "
            f"**{report['parallel_EFT_G5_mathematical']['mathematical_G5_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G5 verified: "
            f"**{report['parallel_EFT_G5_mathematical']['release_G5_verified_for_EFT_model']}**"
        ),
        (
            "- Formal SU(3)_C x U(1)_89 tree factorization: "
            f"**{report['parallel_EFT_G6_spectrum']['formal_SU3_x_U1_89_tree_factorization_closed']}**"
        ),
        (
            "- Physical/mathematical EFT G6: "
            f"**{report['parallel_EFT_G6_spectrum']['mathematical_G6_closed_for_EFT_model']}**"
        ),
        (
            "- Exact G6 physical-stabilizer mismatch: "
            f"**{report['G6_SM_provenance_audit']['source_bound']}**"
        ),
        (
            "- Physical PS/SM matter branching and parameterized one-loop "
            "matter thresholds: "
            f"**{report['physical_G7_component_threshold_contract']['source_bound']}**"
        ),
        (
            "- Normalized SO(10) representation Yukawa CGCs for `10`, "
            "`126bar`, and singlet channels: "
            f"**{report['normalized_SO10_Yukawa_CGC_contract']['source_bound']}**"
        ),
        (
            "- Combined heavy-vector/FP-ghost/Goldstone MS-bar matching and "
            "finite vector constant: "
            f"**{report['physical_SM_heavy_vector_MSbar_matching_contract']['source_bound']}**"
        ),
        (
            "- Arbitrary-positive-R_xi zero-background vacuum determinant "
            "cancellation for all 37 broken directions: "
            f"**{report['physical_SM_vector_Rxi_vacuum_cancellation_contract']['source_bound']}**"
        ),
        (
            "- Exact G6/G7 non-identifiability frontier and seven-step closure "
            "path: "
            f"**{report['physical_SM_G6_G7_closure_frontier_contract']['source_bound']}**"
        ),
        (
            "- Exact G8 identifiability frontier, 101-case scale audit, and "
            "PDG-2025 current-limit verification: "
            f"**{report['physical_SM_G8_identifiability_frontier_contract']['source_bound']}**"
        ),
        "- Background-covariant general-field determinants, vector pole conversion, a stationary pre-EW stage, complete scalar/fermion thresholds, flavor boundaries, SARAH `Dot` conversion, Yukawa beta functions, and full G7 remain open.",
        (
            "- Reconstructed physical-SM target and exact standard stabilizer "
            "overlay: "
            f"**{report['physical_SM_vacuum_truth_overlay']['source_bound']}**"
        ),
        (
            "- Exact five-real-amplitude stationary-equality classification "
            "(16 discrete sign variants; full 486-field/continuous-orbit proof open): "
            f"**{report['physical_SM_five_amplitude_equality_contract']['source_bound']}**"
        ),
        (
            "- Exact source-algebra hard projector Hessians (the staged 10/37-row "
            "input; the succeeding 37-row aggregate closes stationarity/rank/PSD): "
            f"**{report['physical_SM_hard_projector_Hessians_contract']['source_bound']}**"
        ),
        (
            "- Exact last-six source Hessians (all 37 active source Hessians made "
            "available; the succeeding aggregate closes stationarity/kernel/rank/PSD): "
            f"**{report['physical_SM_last_six_Hessians_contract']['source_bound']}**"
        ),
        (
            "- Exact source-derived 37-row aggregate local Hessian theorem "
            "(stationary, 38-mode symmetry kernel, rank 448, PSD; global equality open): "
            f"**{report['physical_SM_37_row_aggregate_contract']['source_bound']}**"
        ),
        (
            "- Exact full-486 local stationary/equality orbit and continuous "
            "equivalence of all 16 sign variants (quantitative radius/global equality open): "
            f"**{report['physical_SM_local_equality_orbit_contract']['source_bound']}**"
        ),
        (
            "- Exact five-amplitude versus physical-EW branch mismatch "
            "(not a global hierarchy no-go; G4-G8 open): "
            f"**{report['physical_SM_G4_G5_branch_mismatch_contract']['source_bound']}**"
        ),
        "- The old selected EFT target is `SU(3)_C x U(1)_89`, not the Standard-Model vacuum; its abstract G3/G4/G5 proofs remain formal only.",
        "- Physical Standard-Model G3/G4/G5/G6/G7/G8: `False`/`False`/`False`/`False`/`False`/`False`.",
        "- Mathematical/release/authoritative G6: `False`/`False`/`False`.",
        "- Mathematical/release/authoritative G7: `False`/`False`/`False`.",
        "- The authoritative renormalizable G3-G8 frontier is unchanged.",
        "",
        "## Authoritative gates",
        "",
    ]
    lines.extend(
        (
            f"- `{name}`: `{row['status']}` - "
            + (
                ", ".join(row["authoritative_closed_scope"])
                if row["status"] == STATUS_CLOSED
                else row["open_scope"][0]
            )
        )
        for name, row in report["gates"].items()
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
