# G6 remnant RG no-go on the SOS witness family (v20)

**Status:** `G6_SM_PATI_SALAM_REMNANT_RG__NOT_CLOSABLE_ON_SOS_WITNESS_FAMILY__G6_OPEN`
**Overall state:** `SOS_WITNESS_FAMILY_TREE_MATCHING_DISJOINT_FROM_ONE_LOOP_REMNANT_REGION__G6_OPEN`
**G6 status:** `OPEN` (evidence only; this module never changes a gate status)
**Tree certificate scope:** tree level at mu = M_GUT
**Checks:** 58/58 passed

G6 is not closable on the SOS-certified witness family at one loop with tree-level matching, with the stated approximations. Exact tree-level matching of the Delta_R = (10bar,1,3) EFT at mu = M_GUT gives lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3) >= 0 on every SOS-safe weight vector (and exactly 1/128 at the witness, whose tree levels 1/96, 17/288, 37/576, 353/3360 and 1/2 reproduce the G6 certificate), while the RG-improved one-loop-positive remnant region needs lambda4 - lambda5 < 0 at M_GUT (-0.416 at rho = 1e3 for its best point, whose FJ pole masses are recomputed here and xi independent to <= 1e-12; the region itself is a sampled, box-bounded research scan, so its lambda4 - lambda5 < 0 is a sampling statement, not a proof over all couplings). The certified witness runs tachyonic: lambda5 crosses zero at 4.68e16 GeV (rho = 1e3). Only the tree-matching statement is robust: the only computed one-loop M_GUT threshold (at the witness, assumed weight independent, not verified) shifts lambda4 - lambda5 by -0.57 (gX = g), which removes the lambda4 >= lambda5 obstruction; the remaining separation is 0.042 at rho = 1e3 and closes at 1.20 to 1.73 times that threshold (and is smaller at rho = 1e4 and without spectators with the alpha^-1 = 23.78 threshold). G6 stays OPEN; the G6 tree certificate is scoped to tree level at mu = M_GUT; G3 and G4 are unchanged; G6 is not shown impossible in the contract (an anti-SOS G3 witness might exist); closing G6 would need controlled weight-dependent M_GUT thresholds and two-loop quartic running and, unless those thresholds open an SOS-safe route, an anti-SOS G3 witness.

## Flags

- `G6_closed`: `False`
- `G6_gate_wired`: `False`
- `anti_sos_g3_witness_excluded`: `False`
- `best_region_points_one_loop_pole_positive_recomputed`: `True`
- `best_region_points_outside_sos_image_at_tree_matching`: `True`
- `changes_g3_g4_closure`: `False`
- `disjointness_robust_to_one_loop_threshold`: `False`
- `evidence_only`: `True`
- `g6_impossible_in_contract_claimed`: `False`
- `landau_cw_curvature_masses_positive_at_best_points`: `True`
- `not_closable_on_sos_witness_family`: `True`
- `one_loop_beta_coefficients_exact_rational`: `True`
- `one_loop_gut_threshold_w_independence_verified`: `False`
- `pole_mass_scale_variation_recomputed_in_module`: `False`
- `pole_masses_recomputed_in_module`: `True`
- `region_scan_exhaustive_beyond_sampled_box`: `False`
- `region_volume_and_tuning_recomputed_in_module`: `False`
- `report_closes_g6_by_itself`: `False`
- `sos_family_tree_matching_forces_lam4_ge_lam5_exact`: `True`
- `tree_certificate_valid_below_M_GUT`: `False`
- `tree_matching_map_exact`: `True`
- `two_loop_quartic_running_included`: `False`
- `witness_210_exchange_vanishes_exact`: `True`
- `witness_radiatively_unstable_at_physical_hierarchy`: `True`
- `witness_tree_levels_reproduce_g6_exact`: `True`

## (A) group_theory (EXACT)

Tree mass matrix A (m^2/v^2 = A lambda):

| state | (20',1) | (35,1) | (45,3) | (20',5) | (35,5) |
| --- | --- | --- | --- | --- | --- |
| (6,1)_4/3 | 0 | 0 | 0 | 4/3 | -4/3 |
| (1,1)_2 | 0 | 4/3 | 0 | 0 | -4/3 |
| (3,1)_1/3 | 0 | 0 | 1 | 0 | -1 |
| (6,1)_1/3 | 0 | 0 | 1 | 2/3 | -5/3 |
| (3,1)_4/3 | 0 | 2/3 | 1 | 0 | -5/3 |
| (6,1)_2/3 | 4/9 | 2/9 | 1 | 2/9 | -17/9 |
| (1,1)_0 radial | 0 | 0 | 0 | 0 | 4 |

Sym^2(Delta_R) dimensions: (20',1) 20, (35,1) 35, (45,3) 135, (20',5) 100, (35,5) 175

Fierz vectors f_c (Q_c = sum_k f_ck V_k):

| channel | (20',1) | (35,1) | (45,3) | (20',5) | (35,5) |
| --- | --- | --- | --- | --- | --- |
| (1,1,1) | 1 | 1 | 1 | 1 | 1 |
| (1,1,3) | -2 | -2 | -1 | 1 | 1 |
| (15,1,1) | -3/2 | 3/2 | -1/2 | -3/2 | 3/2 |
| (15,1,3) | 3 | -3 | 1/2 | -3/2 | 3/2 |

One-loop scalar tensor Q[(i,j)][k] (exact):

| (i,j) | (20',1) | (35,1) | (45,3) | (20',5) | (35,5) |
| --- | --- | --- | --- | --- | --- |
| 0,0 | 124/27 | 32/27 | -32/81 | 16/27 | 32/27 |
| 0,1 | 112/27 | 32/27 | -224/81 | 112/27 | 32/27 |
| 0,2 | -16/3 | -32/3 | 16/3 | 8/3 | 16/3 |
| 0,3 | 160/27 | 320/27 | 160/81 | 16/27 | 32/27 |
| 0,4 | 560/27 | 160/27 | 560/81 | 56/27 | 16/27 |
| 1,1 | 28/27 | 200/27 | -140/81 | 28/27 | 92/27 |
| 1,2 | -56/3 | -40/3 | 28/3 | 28/3 | 20/3 |
| 1,3 | 560/27 | 160/27 | 560/81 | 56/27 | 16/27 |
| 1,4 | 280/27 | 920/27 | 700/81 | 28/27 | 92/27 |
| 2,2 | 18 | 18 | 4 | 18 | 18 |
| 2,3 | 40/3 | 80/3 | 80/3 | 16/3 | 32/3 |
| 2,4 | 140/3 | 100/3 | 140/3 | 56/3 | 40/3 |
| 3,3 | 40/27 | 80/27 | 160/81 | 292/27 | 368/27 |
| 3,4 | 280/27 | 80/27 | 1120/81 | 1288/27 | 368/27 |
| 4,4 | 70/27 | 230/27 | 700/81 | 322/27 | 1166/27 |

Gauge tensor G[k]:

| monomial | (20',1) | (35,1) | (45,3) | (20',5) | (35,5) |
| --- | --- | --- | --- | --- | --- |
| g4^2gR^2 | 36 | -36 | 6 | -18 | 18 |
| g4^4 | 9/2 | 45/2 | -3/2 | 9/2 | 45/2 |
| gR^4 | 18 | 18 | 3 | 9 | 9 |

Witness 16 pi^2 beta (g4^2 = 9/25, gR^2 = 1/4): 540798191/211680000, 111806803/338688000, -10773671491/10160640000, -1491898817/1693440000, 3310549871/677376000

## (B) chart_binding (EXACT)

c_qk (I_q restricted to Delta_R = sum_k c_qk V_k):

| q | (20',1) | (35,1) | (45,3) | (20',5) | (35,5) |
| --- | --- | --- | --- | --- | --- |
| 1050bar | 1/2 | 0 | 4/9 | 0 | 0 |
| 2772bar | 1/10 | 0 | 1/9 | 0 | 1 |
| 4125 | 1/7 | 1 | 4/9 | 1 | 0 |
| 54 | 9/35 | 0 | 0 | 0 | 0 |

Krylov basis: 30 vectors, realified rank 60 (mod p); witness portal residual on Delta_R: 0.

## (C) matching (EXACT)

- gap identity: lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3)
- witness lambda(M_GUT) = 989/4480, 17/128, 53/288, 17/128, 1/8; lambda4 - lambda5 = 1/128
- witness tree levels (r0^2 units): (1,1)_0 radial 1/2, (1,1)_2 1/96, (3,1)_1/3 17/288, (3,1)_4/3 37/576, (6,1)_1/3 37/576, (6,1)_2/3 353/3360, (6,1)_4/3 1/96
- historical (unswapped) weights: lambda4 - lambda5 = -1/128

## (D) running (FLOAT, recomputed)

| profile | lambda5 = 0 (GeV) | max abs lambda > 4 pi (GeV) | max abs lambda > 1e3 (GeV) | lambda4 - lambda5 at M_GUT | tree LP slack | slack with threshold gX1 | gX0 | SOS grid tree vacua |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rho1e3 | 4.68088e+16 | 4.02141e+13 | 3.00929e+13 | -0.416087 | 0.208044 | 0.041547 | 0.0913654 | 0 |
| rho1e4 | 1.17116e+16 | 1.35703e+12 | 1.03436e+12 | -0.312122 | 0.156061 | 0.0542967 | 0.0699538 | 0 |
| no_spec | 1.21018e+15 | 5.64025e+10 | 4.3565e+10 | -0.244822 | 0.122411 | 0.0379814 | 0.0536385 | 0 |

Threshold fragility (rho = 1e3, gX = g): slack <= 0.03 at 1.20365 x threshold, exact reach at 1.73276 x threshold; gX = 0 minimum slack over scale [0, 8]: 0.0431975.

Min LP slack with the research witness threshold, both coupling pairings (record-only; the pairing used is marked *):

| profile | 4 pi/g^2 at M_GUT | M_GUT/M_X | alpha^-1 = 23.78, gX1 | gX0 | alpha^-1 = 40, gX1 | gX0 |
| --- | --- | --- | --- | --- | --- | --- |
| rho1e3 | 20.2-21.0 | 1.94559 | 0.041547* | 0.0913654* | 0.0757082 | 0.0913654 |
| rho1e4 | 28.0-29.0 | 2.26786 | 0.0201355 | 0.0699538 | 0.0542967* | 0.0699538* |
| no_spec | 46.2-47.5 | 2.80182 | 0.00382018 | 0.0536385 | 0.0379814* | 0.0536385* |

Threshold shift of lambda4 - lambda5: alphainv23.78_gX0.0 -0.271789, alphainv23.78_gX1.0 -0.570699, alphainv40.0_gX0.0 -0.2757, alphainv40.0_gX1.0 -0.369643.

SOS-safe grid: no SOS grid point runs perturbatively to v_R with a tree vacuum: rho1e3: 2560 of 2560 exceed |lambda| = 1000 above v_R; rho1e4: 2560 of 2560 exceed |lambda| = 1000 above v_R; no_spec: 2556 of 2560 exceed |lambda| = 1000 above v_R, the 4 others reach v_R with lambda5(v_R) <= -28.7 (min -183); this is a statement about perturbative flows from SOS-safe tree matching, not a vacuum analysis at non-perturbative couplings.

Tolerances: regression tolerances against this module's own discretisation (RK4 on np.interp of the tabulated gauge profile, the research and skeptic method, so the research comparisons are like for like), not accuracy statements; the method error is measured in running.accuracy_estimate against a joint gauge + quartic RK4 without interpolation (about 2e-6 absolute in lambda(M_GUT), 1e-6 in lambda4 - lambda5 and 1e-5 relative in the lambda5 crossing).

| profile | max abs dlambda(M_GUT) | abs d(lambda4 - lambda5) | crossing ratio - 1 | reference self-convergence |
| --- | --- | --- | --- | --- |
| rho1e3 | 2.10515e-06 | 1.04552e-06 | 8.35808e-06 | 1.23768e-12 |
| rho1e4 | 8.1283e-07 | 3.80049e-07 | 5.99737e-06 | 1.49103e-13 |
| no_spec | 3.06186e-07 | 1.08722e-07 | 9.08903e-07 | 8.66474e-13 |

Accuracy (joint RK4 of (alpha_4^-1, alpha_L^-1, alpha_R^-1, y_PS, lambda_1..5) without interpolation, uniform steps <= 0.02 and <= 0.01 on each side of ln(rho M_I); the finer one is the reference): within budget `True`.

## (E) one_loop_masses (FLOAT)

FJ R_xi one-loop pole masses m^2/v_R^2 at xi = 1 (recomputed; xi spread over {0, 0.5, 1, 3, 10}, min VF_L, FJ vev shifts):

| profile | (6,1)_4/3 | (1,1)_2 | (3,1)_1/3 | (6,1)_1/3 | (3,1)_4/3 | (6,1)_2/3 | (1,1)_0 radial | xi spread | min VF_L | dv Feynman | dv Landau |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rho1e3 | 0.129478 | 0.145993 | 0.128398 | 0.210383 | 0.212527 | 0.152512 | 0.181292 | 5.09037e-14 | 0.0941547 | 0.1871 | 0.176421 |
| rho1e4 | 0.147382 | 0.279593 | 0.149888 | 0.240839 | 0.30217 | 0.153385 | 0.200146 | 1.74305e-14 | 0.110514 | 0.186693 | 0.17607 |
| no_spec | 0.152001 | 0.18466 | 0.144107 | 0.236357 | 0.247282 | 0.240329 | 0.196101 | 2.15938e-14 | 0.104945 | 0.195207 | 0.184622 |

Landau-gauge p = 0 vev-fixed CW curvature masses:

| profile | (6,1)_4/3 | (1,1)_2 | (3,1)_1/3 | (6,1)_1/3 | (3,1)_4/3 | (6,1)_2/3 | (1,1)_0 radial |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rho1e3 | 0.0841375 | 0.0983526 | 0.0839591 | 0.139131 | 0.141691 | 0.101725 | 0.148223 |
| rho1e4 | 0.0966178 | 0.191529 | 0.0993089 | 0.160466 | 0.203999 | 0.103044 | 0.158824 |
| no_spec | 0.0987399 | 0.124196 | 0.0943021 | 0.156151 | 0.165107 | 0.160598 | 0.153461 |

one-loop FJ R_xi pole masses at the three best region points (recomputed, xi in {0, 0.5, 1, 3, 10}), the vev-fixed Landau masses VF_L and Landau-gauge p = 0 CW curvature masses; the renormalisation-scale variation of the pole masses stays RESEARCH_RECORD

## (F) research_record (not re-derived)

scratch research outputs of 2026-09-26 (study D-D, wfDA/D and wfDA/review); not in the repository; hashes recorded for audit only and not verifiable from the repository

| entry | label | source | key | sha256 |
| --- | --- | --- | --- | --- |
| BG_max_quantiles | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].BG_q | df5087df4e5bc279... |
| UV_volume_region | RESEARCH_RECORD | d18_tuning_rho1e3.json (d18_tuning.py) | UV_volume_region | 361388aa9f5eccc2... |
| best_controlled_pole_reference | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].best_controlled.{pole_by_xi, tree, VF_L} | df5087df4e5bc279... |
| best_core_lam_GUT_rho1e3 | RESEARCH_RECORD | d22_controlled_rho1e3.json (d22_controlled.py) | best_core.lam_GUT | 0f36280f9ecd528e... |
| box_extension_no_spec | RESEARCH_RECORD | d23_box_extension_no_spec.json (d23_box_extension.py) | {ext_box, N, n_tree_pos_path_unitary, share_inside_prod_box} | 353cf488c6ee9bc4... |
| box_extension_rho1e3 | RESEARCH_RECORD | d23_box_extension_rho1e3.json (d23_box_extension.py) | {ext_box, N, n_tree_pos_path_unitary, share_inside_prod_box} | 0708eb0407f21c8b... |
| fj_vs_vf_vev_shift | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].best_controlled.{dv_feyn, dv_landau} | df5087df4e5bc279... |
| gut_thresholds | RESEARCH_RECORD_INPUT | d12_matching.json (d12_matching.py) | threshold.<key>.dlam_threshold | f35ae578794cb7fe... |
| matching_min_max_selfcoupling_w_over_8 | RESEARCH_RECORD | d18_tuning_rho1e3.json (d18_tuning.py) | matching_d0.0.min_max_selfcoupling_w_over_8_quantiles | 361388aa9f5eccc2... |
| matching_tree_LP | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].matching | df5087df4e5bc279... |
| n_core_all_scales_no_spec | RESEARCH_RECORD | d22_controlled_no_spec.json (d22_controlled.py) | n_core_all_scales | 6e89e32edbbde23b... |
| n_core_all_scales_rho1e3 | RESEARCH_RECORD | d22_controlled_rho1e3.json (d22_controlled.py) | n_core_all_scales | 0f36280f9ecd528e... |
| n_core_all_scales_rho1e4 | RESEARCH_RECORD | d22_controlled_rho1e4.json (d22_controlled.py) | n_core_all_scales | 29025a73ddc8a891... |
| pole_mass_scale_variation_recomputed_in_module | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | rho1e3.scale_variation | df5087df4e5bc279... |
| pole_mass_xi_spread | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].best_controlled.xi_spread | df5087df4e5bc279... |
| portals_and_majorana | RESEARCH_RECORD | d16_portals_f.json (d16_portals_f.py) | rho1e3.<case>.n_path_unitary_tree_pos | 2d376a514ff698b8... |
| profile_M_X | RESEARCH_RECORD_INPUT | profiles.json (d6_profiles.py) | <tag>.M_X | d253ca54be7e905d... |
| profile_boundary_values | RESEARCH_RECORD_INPUT | profiles.pkl (d6_profiles.py) | <tag>.y[0] | db86478396d7fee4... |
| profile_scales | RESEARCH_RECORD_INPUT | profiles.json (d6_profiles.py) | <tag>.{M_I, M_GUT, rho} | d253ca54be7e905d... |
| profile_summaries | RESEARCH_RECORD_INPUT | d19_witness_sos.json (d19_witness_sos.py) | <tag>.profile.{g_vR, g_MGUT, alpha_inv_U} | 5c9f15c0b013be5e... |
| ps_gauge_coefficients | RESEARCH_RECORD_INPUT | u2_coefficients.json (wfGNG/U2 (PyR@TE)) | models.U2PS, delta_PS_spectators | 03f361ed4a91c506... |
| region_counts | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].{N_box, n_path_unitary, region_FJ, region_FJ_VF, region_u_le_half} | df5087df4e5bc279... |
| region_fraction_of_V_pos | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].tuning.region_fraction_of_V_pos | df5087df4e5bc279... |
| region_gap_outside_production_box_recorded | RESEARCH_RECORD | d23_box_extension_rho1e3.json (d23_box_extension.py) | share_inside_prod_box | 0708eb0407f21c8b... |
| region_gap_quantiles_no_spec | RESEARCH_RECORD | d13_region_no_spec.json (d13_region_prod.py) | region_lam4_minus_lam5_GUT_quantiles | 3e6c32f9e0ce8c5b... |
| region_gap_quantiles_rho1e3 | RESEARCH_RECORD | d13_region_rho1e3.json (d13_region_prod.py) | region_lam4_minus_lam5_GUT_quantiles | baf89f1118c1c755... |
| region_gap_quantiles_rho1e4 | RESEARCH_RECORD | d13_region_rho1e4.json (d13_region_prod.py) | region_lam4_minus_lam5_GUT_quantiles | 7a24d52cbb540a09... |
| region_points | RESEARCH_RECORD_INPUT | d20_summary.json (d20_summary.py) | [tag].best_controlled.lam_vR | df5087df4e5bc279... |
| region_scan_box_no_spec | RESEARCH_RECORD | d13_region_no_spec.json (d13_region_prod.py) | {box, N_box, n_prefilter, d_th} | 3e6c32f9e0ce8c5b... |
| region_scan_box_rho1e3 | RESEARCH_RECORD | d13_region_rho1e3.json (d13_region_prod.py) | {box, N_box, n_prefilter, d_th} | baf89f1118c1c755... |
| region_scan_box_rho1e4 | RESEARCH_RECORD | d13_region_rho1e4.json (d13_region_prod.py) | {box, N_box, n_prefilter, d_th} | 7a24d52cbb540a09... |
| region_u_quantiles | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].u_q | df5087df4e5bc279... |
| scale_variation | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | rho1e3.scale_variation | df5087df4e5bc279... |
| skeptic_cw_masses | RESEARCH_RECORD | r_d_indep.json (r_d_indep.py (skeptic)) | I4.<tag>.rows[].CW_p0_vevfixed_mine | 663c8b15e85328a1... |
| skeptic_running | RESEARCH_RECORD | r_d_running.json (r_d_running.py (skeptic)) | <tag>.{lam_MGUT_mine, witness_lam5_zero_crossing_GeV, lam4_minus_lam5_MGUT} | 983b579879c7184b... |
| skeptic_witness_betas | RESEARCH_RECORD | r_d_indep.json (r_d_indep.py (skeptic)) | beta_mine_witness_g4_0.6_gR_0.5 | 663c8b15e85328a1... |
| sos_grid_tree | RESEARCH_RECORD | d19_witness_sos.json (d19_witness_sos.py) | <tag>.sos_grid | 5c9f15c0b013be5e... |
| sos_grid_with_threshold | RESEARCH_RECORD | d21_threshold_matching.json (d21_threshold_matching.py) | <tag>.sos_grid_plus_threshold_gX* | 2a8305720493b145... |
| sphere_min | RESEARCH_RECORD | d20_summary.json (d20_summary.py) | [tag].sphere | df5087df4e5bc279... |
| threshold_LP | RESEARCH_RECORD | d21_threshold_matching.json (d21_threshold_matching.py) | rho1e3.LP_sos_minus_threshold_gX* | 2a8305720493b145... |
| threshold_quality | RESEARCH_RECORD | d12_matching.json (d12_matching.py) | threshold.<key>.{r0_stability_max, fit_resid} | f35ae578794cb7fe... |
| threshold_w_independence_verified | RESEARCH_RECORD | wfDA_review.md (skeptic review, part D) | D: flaws and caveats | 8e1ac0bd123f4850... |
| two_loop_quartic_running | RESEARCH_RECORD | wfDA_review.md (skeptic review, part D) | D: uncertain | 8e1ac0bd123f4850... |
| witness_crossing_grid_limited | RESEARCH_RECORD | d19_witness_sos.json (d19_witness_sos.py) | <tag>.witness.lam5_zero_crossing_GeV | 5c9f15c0b013be5e... |

## Scope

**float_recomputed**

- running (D): PS gauge profiles, witness lambda5 zero crossings and runaway above v_R, the three best region points run to M_GUT, tree LP margins, threshold LP margins for both coupling pairings (record-only), BFB-only reach, a 2560-point SOS-safe grid, and the method accuracy against a joint gauge + quartic RK4 without interpolation
- one_loop_masses (E): FJ R_xi one-loop pole masses at the three best region points for xi in {0, 0.5, 1, 3, 10} (xi independence), the vev-fixed Landau masses VF_L with the FJ vev shifts, and Landau-gauge p = 0 vev-fixed CW curvature masses

**not_proved_or_out_of_scope**

- anti-SOS G3 witnesses (outside degree-2 SOS certification): not excluded
- the one-loop region as a whole: it is a sampled, box-bounded set (1.5M points per profile); its gap < 0 at M_GUT is a sampling statement, not a proof over all couplings
- robustness beyond tree matching: with the recorded witness M_GUT threshold the lambda4 >= lambda5 obstruction is removed and the separation is marginal (0.042 at rho = 1e3, closing at 1.2 to 1.73 times that threshold; smaller at rho = 1e4 and without spectators with the alpha^-1 = 23.78 threshold); only the tree-matching statement is robust
- two-loop quartic beta functions
- the M_GUT one-loop threshold as a function of the weights w (assumed weight independent, not verified) and of the coupling at which it is taken
- the renormalisation-scale variation of the pole masses (research-recorded, not recomputed)
- region volume and tuning statistics (research-recorded, prior dependent)
- electroweak symmetry breaking
- heavy-Sigma exchange O(r0^2) corrections (r0 ~ 1e-8)
- the h/S portals and the Majorana Yukawa f (research: they only shrink the region)
- y_s / spectator Yukawas (Delta-only EFT)
- the rho = 1e3 profile premise of study D (A2's strict window prefers rho >= 10^3.8, where the region is larger)

**proved_exactly**

- group_theory (A): integer model of Delta_R = (10bar,1,3); Sym^2 irreps; SM-singlet vacuum; SM labels; tree mass matrix; Fierz vectors; 210 channels; one-loop beta tensors as exact rationals (SM Higgs identity on the same code path)
- chart_binding (B): c_qk of the 126bar self-quartics restricted to Delta_R in the repository chart; witness portal squares vanish on Delta_R
- matching (C): tree map at mu = M_GUT, gap identity lambda4 - lambda5 = (w_4125 - w_2772)/8 + 3 beta_(15,1,1) + 3 beta_(15,1,3) >= 0 on W_SOS (Farkas certificate), witness levels = the committed G6 tree levels

**research_recorded**

- the one-loop region itself: 1.5M sampled lambda(v_R) points per profile in a finite IR box with a tree prefilter (d13), and its box-extension check (d23)
- region volume and tuning (fraction of V_pos, UV volume, Barbieri-Giudice quantiles), path-unitarity quantiles
- the 400-point tree matching LP per profile and the 300-point threshold LP (d13/d20, d21)
- the renormalisation-scale variation of the pole masses
- the one-loop M_GUT thresholds (computed at the witness only, at alpha^-1 = 23.78 and 40)

**status_statement:** G6 stays OPEN; this module is evidence only and never changes a gate status

## Disclosures

- `pole_scheme_dependence`: median relative pole-mass change 0.49 at Q = sqrt2 v_R and 0.74 at Q = 2 v_R; Q = v_R/sqrt2 removes every region point (research-recorded)
- `region_sampling`: the one-loop region is a sampled, box-bounded set: 1.5M uniform lambda(v_R) points per profile in [-0.8, 0.8] x [-0.1, 0.8] x [-0.1, 0.35] x [-0.1, 0.45] x [0, 0.08] after a tree prefilter (remnant levels > -0.1 v_R^2); its maximum lambda4 - lambda5 < 0 at M_GUT and '0 of 400 reachable' are sample statistics, not a proof over all couplings; an extended box puts 99.7% (rho = 1e3) and 97.5% (no spectators) of the UV volume inside the production box, and the gap sign of the rest was not recorded
- `scale_statement_rho_specific`: no point positive at all three scale choices holds at rho = 1e3 only
- `sigma_not_global_min_in_region`: at rho = 1e3 sigma is the global minimum of the tree quartic at v_R in 43 of 60 region points (not in 17)
- `threshold_fragility`: the only computed one-loop M_GUT threshold (at the witness; alpha^-1 = 23.78, gX = g) shifts lambda4 - lambda5 by -0.571, 73 times the witness tree gap 1/128 and larger than the rho = 1e3 region gap -0.416: it removes the lambda4 >= lambda5 obstruction (the rho = 1e3 target gap becomes +0.155) and leaves a sup-norm LP margin of 0.042 in other components, which closes at 1.20 (slack <= 0.03) to 1.73 (exact reach) times that threshold. The thresholds were computed at alpha^-1 = 23.78 and 40, while 4 pi/g^2 at the matching scale M_GUT (1.9 to 2.8 times M_X) is 20.2-21.0 (rho1e3), 28.0-29.0 (rho1e4), 46.2-47.5 (no_spec); with the alpha^-1 = 23.78 threshold the rho = 1e4 margin is 0.0201 and the no-spectator margin 0.0038 (gX = g), below the research slack 0.03, and at rho = 1e3 the threshold was taken at a weaker coupling than at M_GUT: only the tree-level version of the disjointness is robust
- `xi_spread_actual`: the FJ pole masses at the three best points are xi independent over xi in {0, 0.5, 1, 3, 10} to at most 1.85e-13 in the research record (rho = 1e3; 1.6e-14 and 7.7e-14 at rho = 1e4 and without spectators) and to <= 1e-12 when recomputed here (one_loop_masses.fj_pole_masses_over_v_R_squared)

## Checks

- PASS `chart.c_qk_columns_sum_to_one`
- PASS `chart.c_qk_exact`
- PASS `chart.completeness_at_points`
- PASS `chart.krylov_basis_spans_delta_R_exactly`
- PASS `chart.ps_pair_minimal_polynomials_at_points`
- PASS `chart.ps_pair_operators_calibrated_on_sigma_std`
- PASS `chart.sigma_std_pure_35_5_and_pure_2772bar`
- PASS `chart.witness_portal_squares_annihilate_delta_R`
- PASS `chart.witness_weights_bound_to_committed_candidate`
- PASS `group_theory.beta_gauge_tensor_exact`
- PASS `group_theory.beta_route_reproduces_sm_higgs`
- PASS `group_theory.beta_scalar_tensor_exact`
- PASS `group_theory.beta_scalar_tensor_o60_point_136`
- PASS `group_theory.delta_R_casimirs_9_2_and_2`
- PASS `group_theory.exchange_channels_of_210_never_lower_gap`
- PASS `group_theory.fierz_vectors_exact`
- PASS `group_theory.integer_generators_close_su4_su2R`
- PASS `group_theory.quartic_basis_completeness`
- PASS `group_theory.real_dimension_bookkeeping_60`
- PASS `group_theory.remnant_rows_sum_to_zero_radial_row_4`
- PASS `group_theory.sm_state_labels_exact`
- PASS `group_theory.sym2_irrep_dimensions`
- PASS `group_theory.sym2_minimal_polynomials`
- PASS `group_theory.tree_mass_matrix_exact`
- PASS `group_theory.vacuum_is_sm_singlet_with_9_broken_generators`
- PASS `group_theory.witness_betas_exact`
- PASS `matching.gap_identity_exact`
- PASS `matching.historical_unswapped_weights_violate_gap`
- PASS `matching.lambda2_equals_lambda4_without_exchange`
- PASS `matching.sos_family_forces_gap_nonnegative`
- PASS `matching.tree_map_symbolic`
- PASS `matching.tree_vacuum_requires_positive_gap`
- PASS `matching.witness_couplings_exact`
- PASS `matching.witness_tree_levels_exact`
- PASS `matching.witness_tree_levels_match_committed_g6_certificate`
- PASS `one_loop.cw_masses_match_independent_record`
- PASS `one_loop.cw_masses_positive_at_region_points`
- PASS `one_loop.fj_pole_masses_match_research_record`
- PASS `one_loop.fj_pole_masses_positive_all_xi`
- PASS `one_loop.fj_pole_masses_xi_independent`
- PASS `one_loop.vev_fixed_landau_masses_positive_and_dv_controlled`
- PASS `research_record.consistent_with_recomputation`
- PASS `research_record.entries_labelled_with_provenance`
- PASS `research_record.unverified_items_not_claimed`
- PASS `running.bfb_only_matching_exact_at_region_points`
- PASS `running.discretisation_accuracy_within_budget`
- PASS `running.gauge_profiles_reproduce_recorded_inputs`
- PASS `running.region_points_run_up`
- PASS `running.region_points_tree_positive_at_v_R`
- PASS `running.region_points_violate_sos_gap_at_M_GUT`
- PASS `running.sos_safe_grid_has_no_perturbative_tree_vacuum_at_v_R`
- PASS `running.threshold_matching_min_slack_pinned`
- PASS `running.threshold_scale_to_reach_sos_family`
- PASS `running.tree_matching_min_slack_is_half_gap`
- PASS `running.witness_betas_float_match_research`
- PASS `running.witness_flow_nonperturbative_before_v_R`
- PASS `running.witness_lambda5_zero_crossing`
- PASS `scope.g6_open_and_evidence_only`
