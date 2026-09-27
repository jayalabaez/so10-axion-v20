# G3 SM Pati-Salam decoupled singlet family -- v20

**Status:** `SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_EXACT__STATUS_NEUTRAL` (`EXACT_VACUUM_FAMILY_WITH_R_S_INDEPENDENT_OF_R0__NO_BENCHMARK__NO_GATE_CHANGE`)

**Theorem claimed:** `True`

## Theorem

For every r0, rS, x0 > 0, real kappa with kappa^2 < 8 rS^2 and eps >= 0, the decoupled-singlet member V (the committed 27-parameter SM Pati-Salam map with O04 = -2 rS^2 and O06 = 2|kappa| rS + eps) satisfies V >= V0 = -1 - r0^4/8 - rS^4 - x0^4/32 and {V = V0} = G.(p, r0 sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ (given the committed equality-set theorem's rS-free parts).  The domain is sharp: V >= V0 fails for every kappa^2 > 8 rS^2 (exact violating points), while at kappa^2 = 8 rS^2 the bound and the equality set still hold (lambda_eff = 0); the certified domain is the open kappa^2 < 8 rS^2.  Exact over Q at (r0, rS, x0, kappa) = (1/5,1/5,1,-1/20), (1/5,1,1,-1/100), (1/5,1,1,-1/4) and the stress point (1/5,5,1,-5/4) (outside the |c| < 12 perturbative box, eps window 12 - 2|kappa| rS empty; an exact family member only): grad V(q0) = 0, the 486 x 486 Hessian has inertia 447/39/0 at eps = 0 (kernel = 35 orbit tangents + 4 real doublet directions) and 451/35/0 at eps = r0^2/100 and r0^2/10^6 (kernel = the orbit tangents), identical to the committed witness at rS = r0.  The orbit ranks are 33/34/35 at rS in {1/10, 1/5, 1, 2}; F_PQ^2 = 9248 rS^2 x0^2/(16 rS^2 + 289 x0^2) with S share 289 x0^2/(16 rS^2 + 289 x0^2), Phi17 share 16 rS^2/(16 rS^2 + 289 x0^2) and no Sigma share.  The model file gives N_X = 0, N_PQ = -34, E/N = 8/3 and N_DW = 1 modulo gauge (axion period 2 pi/68).

## Physics status (read first)

- **certifies**: the tree-level vacuum family only: the committed 27-parameter SM Pati-Salam map with |S| = rS independent of r0 (O04 = -2 rS^2, O06 = 2|kappa| rS + eps)
- **does_not_choose_a_benchmark**: this report does NOT choose a benchmark: its (r0, rS, kappa) points are certificate points, not benchmarks
- **does_not_change_G3_or_G4**: this report does NOT change G3 or G4 closure: the committed rS = r0 witness (r0 = 1/5, x0 = 1, kappa = -r0/4, 0 < eps < 599/50) remains the closing instance; no gate status, ledger entry or roadmap text changes
- **open_research**: the physics viability of decoupling (y_s <= ~0.35 from two-loop running, the reduced-Planck Landau/perturbativity criterion, and a v_R / f_a / m_a benchmark such as BM-DA1) is open research pending user decisions DA', (d) and the kappa placement
- **axion_mass**: m_a = 153.5 ueV is not a prediction of the family: f_a = v_S v_Phi/sqrt((4 v_S)^2 + (17 v_Phi)^2) (v_F = sqrt2 <F>, N_DW = 1 modulo gauge) depends on rS, which the family leaves free
- **kappa_placement**: kappa = -r0^2/(4 rS) keeps O06 = r0^2/2 and the H block of the witness (heavy Im-10_H doublet at M_I) with |kappa| rS = r0^2/4; kappa = -rS/4 puts that doublet at <S>; neither placement is chosen here

## Verdict

Exact over Q (77 checks): the committed SM Pati-Salam map with |S| = rS independent of r0 changes only O04 = -2 rS^2 and O06 = 2|kappa| rS + eps; the eight-term SOS identity holds for every kappa^2 < 8 rS^2 and eps >= 0, so V >= V0 = -1 - r0^4/8 - rS^4 - x0^4/32 with {V = V0} = G.(p, r0 sigma_std, 0, rS, x0) (sharp: V >= V0 fails for every kappa^2 > 8 rS^2; at kappa^2 = 8 rS^2 it still holds with lambda_eff = 0); the exact 486 x 486 Hessian at 4 points is 447/39/0 at eps = 0 and 451/35/0 at eps > 0 (kernel T35; the rS = 5 point is a stress point outside the |c| < 12 perturbative box with an empty eps window), identical to the committed witness at rS = r0; the orbit ranks stay 33/34/35; F_PQ^2 = 9248 rS^2 x0^2/(16 rS^2 + 289 x0^2) with no Sigma share; the model file gives N = -34, E/N = 8/3 and N_DW = 1 modulo gauge.  Status-neutral: no benchmark is chosen, G3 and G4 stay closed on the committed rS = r0 witness, and the physics viability of decoupling (y_s, the Landau criterion, v_R/f_a/m_a) is open research; m_a = 153.5 ueV is not a prediction of the family.

FLOAT64 corroboration, outside the exact check count: 8/8 passed (live compiler at (1/5, 1, 1, -1/100), anchor point audit at rS = 1000 r0, violating direction, endpoints).

Checks: 77/77 passed.

## Family points

| label | (r0, rS, x0, kappa) | O04 | O06 | O12 | V0 | lambda_eff | eps window upper | perturbative member | tuned / raised / tiny inertia | gap tuned (mult) |
|---|---|---|---|---|---|---|---|---|---|---|
| rS_eq_r0_witness | `(1/5, 1/5, 1, -1/20)` | `-2/25` | `1/50` | `-1/20` | `-20661/20000` | `127/64` | `599/50` | `True` | `447/39/0 / 451/35/0 / 451/35/0` | `1/2400` (`14`) |
| rS_1_kappa_minus_r0sq_over_4rS | `(1/5, 1, 1, -1/100)` | `-2` | `1/50` | `-1/100` | `-40629/20000` | `79999/40000` | `599/50` | `True` | `447/39/0 / 451/35/0 / 451/35/0` | `1/2400` (`14`) |
| rS_1_kappa_minus_rS_over_4 | `(1/5, 1, 1, -1/4)` | `-2` | `1/2` | `-1/4` | `-40629/20000` | `127/64` | `23/2` | `True` | `447/39/0 / 451/35/0 / 451/35/0` | `1/2400` (`14`) |
| rS_5_kappa_minus_rS_over_4_stress | `(1/5, 5, 1, -5/4)` | `-50` | `25/2` | `-5/4` | `-12520629/20000` | `127/64` | `-1/2` | `False` | `447/39/0 / 451/35/0 / 451/35/0` | `1/2400` (`14`) |

## H and S blocks (eps = 0)

| label | H chart curvatures (value: count) | S u-block | S radial mass^2 | difference vs witness |
|---|---|---|---|---|
| rS_eq_r0_witness | `{'0': 4, '1': 6, '1/25': 4, '26/25': 6}` | `[['8/25', '0'], ['0', '0']]` | `4/25` | `none` |
| rS_1_kappa_minus_r0sq_over_4rS | `{'0': 4, '1': 6, '1/25': 4, '26/25': 6}` | `[['8', '0'], ['0', '0']]` | `4` | `S/S` |
| rS_1_kappa_minus_rS_over_4 | `{'0': 4, '1': 10, '2': 6}` | `[['8', '0'], ['0', '0']]` | `4` | `H/H, S/S` |
| rS_5_kappa_minus_rS_over_4_stress | `{'0': 4, '1': 6, '25': 4, '26': 6}` | `[['200', '0'], ['0', '0']]` | `100` | `H/H, S/S` |

## G4 axion, vectors and chart norm by rS

| rS | F_PQ^2 | S share | Phi17 share | v_a^2 | D_u minors (SO10, +X, +PQ) | chart norm^2 |
|---|---|---|---|---|---|---|
| `1/10` | `2312/7229` | `7225/7229` | `4/7229` | `1/14458` | `1/512000000000, 1/1280000000000, -17/1280000000000` | `31/10` |
| `1/5` | `9248/7241` | `7225/7241` | `16/7241` | `2/7241` | `1/512000000000, 1/640000000000, -17/640000000000` | `79/25` |
| `1` | `9248/305` | `289/305` | `16/305` | `2/305` | `1/512000000000, 1/128000000000, -17/128000000000` | `127/25` |
| `2` | `36992/353` | `289/353` | `64/353` | `8/353` | `1/512000000000, 1/64000000000, -17/64000000000` | `277/25` |
| `5` | `231200/689` | `289/689` | `400/689` | `50/689` | `1/512000000000, 1/25600000000, -17/25600000000` | `1327/25` |

Route A (symbolic, all rS): F_PQ^2 = `9248*rS**2*x0**2/(16*rS**2 + 289*x0**2)`, S share `289*x0**2/(16*rS**2 + 289*x0**2)`, Phi17 share `16*rS**2/(16*rS**2 + 289*x0**2)`; v_a = F_PQ/68 = v_S v_Phi/sqrt((4 v_S)^2 + (17 v_Phi)^2), v_S = sqrt2 rS, v_Phi = sqrt2 x0 (chart units M_GUT).

## Model-file anomaly

| quantity | value |
|---|---|
| N_X | `0` |
| N_PQ | `-34` |
| 2N | `-68` |
| E_PQ | `-272/3` |
| E/N | `8/3` |
| N_Vs | `0` |
| global U(1) dimension | `3` |
| general N_SU3 | `-34*beta` |
| axion period modulo gauge | `2 pi/68` |
| N_DW modulo gauge | `1` |
| N_DW cover (S phase) | `17` |

Caveats:

- N_DW = 1 holds modulo gauge only: the one-wall object is the (l, n) = (13, -3) string sector with Phi17 winding and S-winding 2 pi/17 (axion_so10_theory_v20.tex); if Phi17 breaks before inflation the S-only strings carry 17 walls, and the post-inflation branch is conditional on the (13, -3) string's existence and production
- the anomaly and N_DW do not depend on rS; f_a = v_a/N_DW = F_PQ/68 does

## FLOAT64 evidence (outside the exact check count)

| item | FLOAT64 value |
|---|---|
| F1 max abs Hessian difference (tuned / raised) | `8.7374552038e-14` / `8.7374552038e-14` |
| F1 V - V0 (tuned) | `-3.10862446895e-15` |
| F2 anchor rS = 1000 r0: max abs gradient (tolerance), V - V0 (tolerance) | `1.77635920472e-15` (`1e-12`), `-8.881784197e-16` (`1.031266427e-12`) |
| F2 projected negative / zero; lightest / (r0^2/96) | `0` / `4`; `0.998545067349` |
| F3 compiler minus exact | `-2.98882012889e-15` |
| F4 fast evaluator relative difference | `9.24995583087e-14` |
| F4 endpoints on / inconclusive / off orbit | `2` / `0` / `0` |

| FLOAT64 check | passed |
|---|---|
| `float_F1_live_compiler_hessian_and_gradient_match_exact_within_1e_minus_12` | `True` |
| `float_F1_live_lattice_and_V_minus_V0` | `True` |
| `float_F2_anchor_gradient_and_V_minus_V0` | `True` |
| `float_F2_anchor_lightest_massive_r0sq_over_96_and_eps_variant` | `True` |
| `float_F2_anchor_ranks_33_34_35_and_projected_inertia_0_4` | `True` |
| `float_F3_violating_direction_matches_exact` | `True` |
| `float_F4_converged_endpoints_on_orbit` | `True` |
| `float_F4_fast_evaluator_matches_compiler` | `True` |

## Checks

| check | passed |
|---|---|
| `anomaly_E_over_N_8_over_3_from_SM_content_of_16` | `True` |
| `anomaly_N_DW_1_modulo_gauge_period_2pi_over_68` | `True` |
| `anomaly_N_PQ_minus_34_independent_of_spectator_split` | `True` |
| `anomaly_contract_kappaH_and_O38_X_and_PQ_neutral` | `True` |
| `anomaly_global_U1_space_is_3_dimensional_X_PQ_Vs` | `True` |
| `anomaly_model_X_charges_solve_every_LagHC_term_and_N_X_0` | `True` |
| `anomaly_model_file_parsed_9_fermion_16s_5_scalars_with_declared_reps_11_LagHC_terms` | `True` |
| `anomaly_scalar_charges_match_repository_X_and_PQ_tables` | `True` |
| `axion_in_kernel_of_eps_member_hessian_at_every_point` | `True` |
| `candidate_map_with_rS_eps_equals_expanded_sos_map_plus_eps_three_signs` | `True` |
| `committed_exact_hessian_report_certified_and_equal_to_rS_eq_r0_certificates` | `True` |
| `equality_set_premises_from_committed_report` | `True` |
| `family_V0_and_lambda_eff_closed_forms_symbolic` | `True` |
| `family_map_27_parameters_inside_51_parameter_contract` | `True` |
| `family_map_changes_only_O04_and_O06_symbolic` | `True` |
| `family_map_equals_witness_map_at_rS_equal_r0_symbolic_and_benchmarks` | `True` |
| `family_map_has_no_S_portal_parameters` | `True` |
| `family_operator_ids_equal_witness_operator_ids` | `True` |
| `g4_axion_closed_forms_and_period_at_rS_1` | `True` |
| `g4_axion_closed_forms_and_period_at_rS_1_over_10` | `True` |
| `g4_axion_closed_forms_and_period_at_rS_1_over_5` | `True` |
| `g4_axion_closed_forms_and_period_at_rS_2` | `True` |
| `g4_axion_closed_forms_and_period_at_rS_5` | `True` |
| `g4_axion_route_A_symbolic_closed_form_all_rS` | `True` |
| `g4_rS_eq_r0_values_equal_committed_G4_report` | `True` |
| `g4_vectors_and_chart_norm_at_rS_1` | `True` |
| `g4_vectors_and_chart_norm_at_rS_1_over_10` | `True` |
| `g4_vectors_and_chart_norm_at_rS_1_over_5` | `True` |
| `g4_vectors_and_chart_norm_at_rS_2` | `True` |
| `g4_vectors_and_chart_norm_at_rS_5` | `True` |
| `kappa_bound_sharp_curve_identity_exact` | `True` |
| `kappa_bound_violated_beyond_boundary_at_exact_rational_witnesses` | `True` |
| `kappa_boundary_bound_and_equality_set_hold_curve_and_completed_square_exact` | `True` |
| `kappa_minus_r0sq_over_4rS_point_keeps_witness_O06_and_H_block` | `True` |
| `lambda_eff_equals_2_minus_kappa_sq_over_4rS_sq_at_every_point` | `True` |
| `p3_family_P3_HS_domain_holds_strictly_at_sample_points` | `True` |
| `p3_family_P3_HS_square_completion_identities_exact_symbolic` | `True` |
| `p3_family_P3_S_Phi17_charge_matrix_nonsingular` | `True` |
| `p3_family_P3_V_phase_independent_at_H0` | `True` |
| `p3_family_P3_all_27_operators_X_and_PQ_neutral` | `True` |
| `p3_family_P3_charges_consistent_across_sources` | `True` |
| `p3_family_P3_explicit_group_element_reaches_all_phases` | `True` |
| `p3_family_P3_operator_count_27_and_25_at_kappa_0` | `True` |
| `p3_family_P3_orbit_tangent_rank_35_kernel_12_pure_so10` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__H_and_S_blocks_closed_form_and_decoupled` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__difference_from_witness_only_on_H_and_S_blocks` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__gaps_r0sq_over_96_mult_14_and_eps_mult_4` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__linear_in_eps_and_doublet_eigenvalue_eps` | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__H_and_S_blocks_closed_form_and_decoupled` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__difference_from_witness_only_on_H_and_S_blocks` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__gaps_r0sq_over_96_mult_14_and_eps_mult_4` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__linear_in_eps_and_doublet_eigenvalue_eps` | `True` |
| `point_rS_1_kappa_minus_rS_over_4__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__H_and_S_blocks_closed_form_and_decoupled` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__difference_from_witness_only_on_H_and_S_blocks` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__gaps_r0sq_over_96_mult_14_and_eps_mult_4` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__linear_in_eps_and_doublet_eigenvalue_eps` | `True` |
| `point_rS_5_kappa_minus_rS_over_4_stress__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4` | `True` |
| `point_rS_eq_r0_witness__H_and_S_blocks_closed_form_and_decoupled` | `True` |
| `point_rS_eq_r0_witness__difference_from_witness_only_on_H_and_S_blocks` | `True` |
| `point_rS_eq_r0_witness__eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient` | `True` |
| `point_rS_eq_r0_witness__gaps_r0sq_over_96_mult_14_and_eps_mult_4` | `True` |
| `point_rS_eq_r0_witness__linear_in_eps_and_doublet_eigenvalue_eps` | `True` |
| `point_rS_eq_r0_witness__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4` | `True` |
| `rS_eq_r0_hessians_and_certificates_identical_to_witness_module` | `True` |
| `sos_eight_terms_expand_to_family_map_kappa_negative` | `True` |
| `sos_eight_terms_expand_to_family_map_kappa_positive` | `True` |
| `sos_eight_terms_expand_to_family_map_kappa_zero` | `True` |
| `sos_expanded_map_equals_family_map_at_every_point_exact` | `True` |
| `tangent_ranks_33_34_35_minors_and_SM_stabilizer_at_rS_1` | `True` |
| `tangent_ranks_33_34_35_minors_and_SM_stabilizer_at_rS_1_over_10` | `True` |
| `tangent_ranks_33_34_35_minors_and_SM_stabilizer_at_rS_1_over_5` | `True` |
| `tangent_ranks_33_34_35_minors_and_SM_stabilizer_at_rS_2` | `True` |

## Scope

**proved_exactly**

- the family coefficient map (symbolic): only O04 = -2 rS^2 and O06 = 2|kappa| rS + eps change; 27 parameters inside the 51-parameter contract; no S portal; V0 and lambda_eff closed forms
- the eight-term SOS identity with T6 at rS and T9 = eps N_H for kappa < 0, > 0 and = 0, and the sharpness of kappa^2 < 8 rS^2 (exact curve identity and rational violating points beyond it) and the boundary kappa^2 = 8 rS^2 (exact completed square: the bound and the equality set still hold there, lambda_eff = 0; elementary sign argument as in P3)
- P3 at rS (bracket algebra, charges, phases, operator neutrality, integer tangent ranks) at the HS points
- exact 486 x 486 Hessians over Q at the four family points (tuned 447/39/0, eps members 451/35/0, gaps, H/S blocks), the rS = r0 point identical to the committed witness; the rS = 5 point is a stress point outside the |c| < 12 perturbative box (empty eps window), an exact member only
- tangent ranks 33/34/35 and the SM stabilizer at rS in {1/10, 1/5, 1, 2}; the G4 axion (F_PQ^2, composition, period 2 pi/68) and vector/chart sections at rS in {1/10, 1/5, 1, 2, 5}; route A for all rS
- the model-file anomaly (declared representations checked): N_X = 0, N_PQ = -34, E/N = 8/3, N_DW = 1 modulo gauge

**relies_on_committed**

- G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; P1/P2 contain no S and carry over verbatim)
- G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to this report's rS = r0 certificates)
- G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json (equal to this report's rS = r0 G4 values)
- GAUGED_U1X_SCALAR_CONTRACT_V20.json (gauge SO(10) x U(1)_X, accidental global PQ)
- models/SO10Z17AxionV20.m (fermion content, X charges, Yukawa/portal terms)

**float64_evidence_only**

- the live compiler Hessian and gradient at (1/5, 1, 1, -1/100) against the exact one (F1)
- the compiler point audit at the hierarchy anchor with rS = 1000 r0 (F2)
- the compiler value along the violating direction (F3)
- the rS-aware fast evaluator and minimisation endpoints at (1/5, 1, 1, -1/100) (F4)

**not_proved_or_out_of_scope**

- a member with a nonzero S portal (O22, O26, O34, O38, O43): not certified; the S portals stay 0
- the G6 tree spectrum and G8 flavour no-go re-pins at a decoupled point (roadmap PR 3)
- two-loop running with y_s, the reduced-Planck Landau criterion, and v_R / f_a / m_a numbers (roadmap PR 4, research)
- the committed exact Hessian report's flags.other_r0_x0_kappa_certified stays False: the family certificates live only in this report
- no manuscript change

**status_neutrality**

status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20, g4_sm_closure_binding_v20 or any roadmap/readiness module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed, and the committed rS = r0 witness remains the G3 and G4 closing instance

Runtime: 106 s.
