# G3 SM Pati-Salam witness: perturbative-unitarity normalisation -- v20

**Status:** `SM_PATI_SALAM_WITNESS_UNITARITY__COMMITTED_NONPERTURBATIVE__RESCALED_MEMBER_SINGLET_CHANNEL_PERTURBATIVE_EXACT__STATUS_NEUTRAL` (`COMMITTED_WITNESS_SINGLET_A0_21_65__OVERALL_ONE_FIFTIETH_MEMBER_A0_0_433__NO_GATE_CHANGE`)

**Record claimed:** `True`

## Verdict

Exact (57 checks): at the committed G3 witness the tree-level singlet-channel matrix has a0_max = 21.654 (exactly between 21 and 22; the 210 singlet entry alone is 21.565), so the benchmark normalisation is non-perturbative.  Scaling whole SOS terms by positive factors keeps the certificate exactly; the overall x1/50 member keeps the vacuum, the SOS identity, the equality set and the inertia 447/39/0 (451/35/0 raised), with gap r0^2/4800, and has a0_max = 0.4331 < 1/2 in the computed channel.  s_max lies in (1/44, 1/43); rescaling only the 210 block by 1/50 leaves a0_max = 1.98.  Status-neutral: no gate changes, the committed witness remains the G3 closing instance, non-singlet channels are not computed and the D12 thresholds are not recomputed.

FLOAT64 corroboration, outside the exact check count: 2/2 passed (live compiler: O36 = lambda_H N_H^2 at random unit H; Q(p) = 1 and T_Phi(p) = -1).

Checks: 57/57 passed.

## Statement

Tree level, s -> infinity, coupled SO(10) x U(1)_X x U(1)_PQ singlet two-particle channel of the five scalar blocks: at the committed G3 witness the singlet-channel matrix is exactly -4 N^-1 E with alpha = (1084, 44, 16645/448, 4, 1/8), beta_{Phi|Sigma} = 205/4, beta_{Sigma|Phi} = 123/2, beta_{H|Phi} = 12 and no other pair, so 21 < a0_max < 22 (a0_max = 21.654): the committed normalisation is non-perturbative.  Scaling every SOS term of the committed identity by its own positive factor keeps the SOS identity, the vacuum, the equality set and the Hessian inertia; the overall x1/50 member has H_u = H_u(witness)/50, inertia 447/39/0 (451/35/0 raised), smallest nonzero eigenvalue r0^2/4800, V0/50 and a0_max = 0.4331 < 1/2 in the computed channel; s_max lies in (1/44, 1/43); rescaling the 210 block alone by 1/50 leaves a0_max = 1.98.

## Method (EXACT lemma)

- **matrix**: M_AA = -alpha_A, M_AB = -sqrt(n_B/n_A) beta_{A|B}; eig M = eig(-4 N^-1 E); a0 = eig/(16 pi)
- **mixed**: E[V_AB] = (1/4) Lap_A Lap_B V_AB = (n_B/2) beta_{A|B}, beta_{A|B} = Tr_A Hess_q V_AB(x_B unit)
- **pi_bounds**: 333/106 < pi < 22/7: max|eig| < 1332/53 certifies a0 < 1/2, max|eig| > 176/7 certifies a0 > 1/2
- **self**: E[V4_A] = (1/8) Lap^2 V4_A = (n_A/4) alpha_A, alpha_A = Tr Hess_q V4_A(e)
- **unitarity**: |a0| <= 1/2
- **regime**: tree level, s -> infinity: quartic contact terms only (trilinear exchange falls off as 1/s)
- **irreducibility premise**: Phi (210, real type), H (10 (x) C with U(1)_X), Sigma (126bar), S and Phi17 (charged singlets) are irreducible real representations of SO(10) x U(1)_X x U(1)_PQ, so Lap of an invariant quartic restricted to a block is c |x_A|^2 (standard representation theory; checked for H with sympy and for Sigma against the dimension-weighted channel sum)

| block | n (reals) | q-trace factor | vev chart norm^2 |
|---|---|---|---|
| Phi | `210` | `1` | `1` |
| H | `20` | `1/2` | `0` |
| Sigma | `252` | `1/2` | `2/25` |
| S | `2` | `1/2` | `2/25` |
| Phi17 | `2` | `1/2` | `2` |

## Committed witness (EXACT)

| block | alpha_A | self a0 = alpha/(16 pi) (NUM) | channel |
|---|---|---|---|
| Phi | `1084` | `21.5655` | 210 singlet channel |
| H | `44` | `0.875352` | 10_H singlet |
| Sigma | `16645/448` | `0.739156` | 126bar singlet |
| S | `4` | `0.0795775` | S |
| Phi17 | `1/8` | `0.0024868` | Phi17 |

| pair | beta |
|---|---|
| `H\|Phi` | `12` |
| `Phi\|H` | `126` |
| `Phi\|Sigma` | `205/4` |
| `Sigma\|Phi` | `123/2` |

- -4 N^-1 E (rows Phi, H, Sigma, S, Phi17): `[['-1084', '-12', '-123/2', '0', '0'], ['-126', '-44', '0', '0', '0'], ['-205/4', '0', '-16645/448', '0', '0'], ['0', '0', '0', '-4', '0'], ['0', '0', '0', '0', '-1/8']]`
- characteristic polynomial: `(lam + 4)*(8*lam + 1)*(448*lam**3 + 521989*lam**2 + 38053952*lam + 706602920)/3584`
- largest |eig| in `['49180333/45184', '55270187/50779']`; a0_max in `[21.645228, 21.654514]` (exact rational enclosure)
- eigenvalues (NUM): `-1088.4458, -43.040835, -33.667427, -4, -0.125`; a0_max = `21.65394`
- 21 < a0_max < 22: (16 x 21 x 22/7) N/4 +- E is not positive semidefinite for one sign and (16 x 22 x 333/106) N/4 +- E is positive definite for both signs (exact inertia)

## Rescaling lemma (EXACT)

For s_k > 0, V(s) = sum_k s_k T_k (parameter map c(s) = sum_k s_k c_k) satisfies V(s) - V0(s) = sum_k s_k (T_k - m_k) >= 0 with V0(s) = sum_k s_k m_k; {V(s) = V0(s)} = cap_k {T_k = m_k} = G.q0 (unchanged: every T_k attains m_k at q0); Hess V(s)(q0) = sum_k s_k Hess T_k(q0) with every Hess T_k(q0) PSD, so its kernel is cap_k ker Hess T_k(q0), independent of s: inertia 447/39/0 for every positive scaling

| group | terms | gradient 0 at q0 | Hessian inertia +/-/0 | value at q0 | expected minimum |
|---|---|---|---|---|---|
| A_square+C_square | A_square, C_square | `True` | `211/0/275` | `0` | `0` |
| T_HPhi | T_HPhi | `True` | `12/0/474` | `0` | `0` |
| T_HS | T_HS | `True` | `11/0/475` | `-1/625` | `-1/625` |
| T_Phi | T_Phi | `True` | `186/0/300` | `-1` | `-1` |
| T_X | T_X | `True` | `1/0/485` | `-1/32` | `-1/32` |
| W | W | `True` | `231/0/255` | `-1/5000` | `-1/5000` |

Proper-subset counterexamples:

- O27_only_x1/50: grad V(q0) supported on Sigma with u0 . grad = -49/3125 != 0: the Sigma radius moves (exact)
- O48_only_x1/50: grad_Phi(q0) = (s - 1) grad Q(p) = (s - 1) 4 p != 0: |Phi| moves (exact)

## Members

| member | term scales | inertia (benchmark) | a0_max (NUM) | a0 <= 1/2 (exact) |
|---|---|---|---|---|
| overall x1/50 | all `1/50` | `447/39/0` (raised `451/35/0`) | `0.433079` | `True` |
| blockwise test point (not a benchmark) | `{'A_square': '1/50', 'C_square': '1/50', 'T_HPhi': '1/10', 'T_HS': '1/4', 'T_Phi': '1/50', 'T_X': '1', 'W': '1/2'}` | `447/39/0` | `0.461413` | `True` |
| T_Phi only x1/50 | `T_Phi: 1/50` | (whole term: certificate kept) | `1.9793` | `False` |
| overall x1/40 | all `1/40` | | `0.541349` | `False` |

- H_u(member) = H_u(witness)/50: numerators identical `True`, denominators `2016000` -> `100800000`
- gap re-check at `1/120000` = r0^2 x `1/4800`: benchmark (neg/zero/pos) `[39, 14, 433]`, raised `[35, 14, 437]`
- the raised variant adds eps = r0^2/100 to O06 after scaling (unscaled offset): its doublet at r0^2/100 lies above the scaled remnants at s r0^2/96 = r0^2/4800, which are the lightest massive states
- hessian.exact_certificate tests the gap target r0^2/96 (raised: eps), valid only for the committed normalisation; it is re-checked here at s r0^2/96
- V0 = `-20661/1000000`, lambda_eff = `127/3200`
- s_max in `['1/44', '1/43']` (a0_max(s) = s a0_max(1); at s = 1/44 max|eig| < 1332/53 < 8 pi, at s = 1/43 max|eig| > 176/7 > 8 pi)
- T_Phi only: the 210 self entry drops to 1084/50 but the H (44) and Sigma (16645/448) self entries and the Phi-Sigma (sqrt(6/5) 205/4) and Phi-H (sqrt(2/21) 126) mixings are untouched and each exceeds 8 pi; corrects the rescue synthesis PR-4 line 'Rescale the 210 block by 0.02 or less' (research record)

Per-block necessary conditions:

- T_HS: 22 lambda_H s_HS <= 8 pi, i.e. lambda_H <= 4 pi/11 at s_HS = 1
- T_Phi: s_TPhi <= 8 pi/1084 = 2 pi/271 (< 44/1897 with pi < 22/7)
- W: s_W <= 8 pi/(16645/448) = 3584 pi/16645
- statement: max|eig M| >= max_A |M_AA| (Rayleigh), so a0 <= 1/2 needs s_A alpha_A <= 8 pi for every block

## What changes at the x1/50 member

- every tree mass^2 (Hessian eigenvalue) scales by s = 1/50 (exact: H_u(s) = s H_u(1)); masses x `0.141421`
- vevs: unchanged: the same vacuum q0 = (p, 0, r0 sigma_std, r0, x0) (exact zero gradient); gauge-boson masses: unchanged (vevs and gauge couplings only)
- lambda_eff: `127/64` -> `127/3200`
- eps windows: `{'member_doublet_is_lightest_for_eps_below': '1/120000', 'member_perturbative_box': '29999/2500', 'witness_doublet_is_lightest_for_eps_below': '1/2400', 'witness_perturbative_box': '599/50'}`; eps enters quadratically (no effect on the s -> infinity amplitude); the |c| < 12 box of the committed eps family moves to 12 - 2 s |kappa| r0, and the eps doublet is the lightest massive state only below s r0^2/96
- the D12 GUT thresholds, the G6 remnant RG no-go numbers and the G7 research running assume the committed normalisation and are not recomputed at the rescaled member

## Research record (not re-derived)

scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit only; the source files are not in the repository and were hashed at generation time (the session scratch area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at runtime

| entry | source | key | sha256 |
|---|---|---|---|
| final_g6_row | wfRESCUE/FINAL.md | section 3 table, G6 | `90f29e8ea8bc7a2b...` |
| mc_a0_max | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.a0_max | `3e0d46fdf37a4948...` |
| mc_eigenvalues | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.eigs | `3e0d46fdf37a4948...` |
| mc_samples | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.n_mc | `3e0d46fdf37a4948...` |
| mc_singlet_matrix | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.M_singlet | `3e0d46fdf37a4948...` |
| mc_singlet_matrix_error | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.M_err | `3e0d46fdf37a4948...` |
| sigma_self_M_SS_exact | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.M_SS_exact | `3e0d46fdf37a4948...` |
| sigma_self_a0_exact | wfRESCUE/D-G6-certification/s03_unitarity.json | witness.a0_sigma_exact | `3e0d46fdf37a4948...` |
| synthesis_pr4_rescale_line | wfRESCUE/SYNTHESIS.md | section 4, PR-4 | `a805b3272a2a2ec1...` |
| synthesis_witness_a0 | wfRESCUE/SYNTHESIS.md | section 1, route D verifier corrections | `a805b3272a2a2ec1...` |
| verify_sigma_channel_formula | wfRESCUE/D-G6-certification/VERIFY_physics.md | SO(10) Sigma-singlet channel | `7a979d737afaa8d7...` |

Largest deviation of the exact matrix from the Monte Carlo record: `1.943` sigma.

## FLOAT64 evidence (outside the exact check count)

- F1 O36 compiler values at random unit H: `0.5, 0.5, 0.5` (target `0.5`, max deviation `5.55e-16`)
- F2 Q(p) = `1`, T_Phi(p) = `-1`

| FLOAT64 check | passed |
|---|---|
| `float_F1_compiler_O36_value_equals_lambda_H_N_H_squared_at_random_unit_H` | `True` |
| `float_F2_compiler_Q_at_p_equals_1_and_T_Phi_at_p_equals_minus_1` | `True` |

## Checks

| check | label | passed |
|---|---|---|
| `T_Phi_only_1_over_50_not_perturbative_exact` | EXACT | `True` |
| `a0_max_between_21_and_22_exact` | EXACT | `True` |
| `alpha_H_22_per_unit_lambda_H_and_trace_independent_of_unit_vector` | EXACT | `True` |
| `alpha_Sigma_equals_dimension_weighted_channel_sum` | EXACT | `True` |
| `beta_H_Phi_equals_two_trace_Q_H_of_the_wedge_square` | EXACT | `True` |
| `block_dimensions_and_congruence_factors_match_chart` | EXACT | `True` |
| `blockwise_test_member_a0_below_half_exact` | EXACT | `True` |
| `blockwise_test_member_inertia_447_39_0_kernel_T35_plus_doublets` | EXACT | `True` |
| `characteristic_polynomial_factorises_with_pinned_cubic` | EXACT | `True` |
| `chart_norms_at_q0_equal_1_2r0sq_2r0sq_2x0sq` | EXACT | `True` |
| `committed_Phi_H_Sigma_self_entries_exceed_half_S_Phi17_below_exact` | EXACT | `True` |
| `committed_Phi_Sigma_and_Phi_H_mixings_exceed_the_bound_exact` | EXACT | `True` |
| `committed_equality_set_artifact_proved` | EXACT | `True` |
| `committed_exact_hessian_artifact_certified_and_equal_to_fresh_witness_certificates` | EXACT | `True` |
| `euler_degree_matches_table_for_every_unit_with_nonzero_gradient` | EXACT | `True` |
| `euler_values_at_q0_sum_to_V0` | EXACT | `True` |
| `every_other_pair_zero_S_and_Phi17_decouple` | EXACT | `True` |
| `every_unit_computable_term_group_hessian_psd_at_q0_exact` | EXACT | `True` |
| `every_unit_computable_term_group_stationary_at_q0_exact` | EXACT | `True` |
| `gaussian_biquadratic_moment_identity_exact` | EXACT | `True` |
| `gaussian_fourth_moment_identity_exact` | EXACT | `True` |
| `h_self_identity_I1_plus_I54_equals_NH_squared_sympy` | EXACT | `True` |
| `kappa_margin_scale_invariant_under_T_HS_scaling_sympy` | EXACT | `True` |
| `largest_root_isolated_exactly_and_a0_enclosed` | EXACT | `True` |
| `lee_quigg_thacker_calibration_a0_3_lambda_over_8_pi` | EXACT | `True` |
| `member_V0_equals_s_V0_and_sum_of_scaled_minima` | EXACT | `True` |
| `member_a0_below_half_exact` | EXACT | `True` |
| `member_benchmark_inertia_447_39_0_kernel_T35_plus_doublets` | EXACT | `True` |
| `member_gradient_exactly_zero` | EXACT | `True` |
| `member_hessian_equals_s_times_witness_hessian_exact` | EXACT | `True` |
| `member_is_whole_term_scaling_with_positive_factors` | EXACT | `True` |
| `member_lambda_eff_equals_127_over_3200` | EXACT | `True` |
| `member_per_block_necessary_conditions_hold_exact` | EXACT | `True` |
| `member_raised_O06_inertia_451_35_0_kernel_T35` | EXACT | `True` |
| `member_singlet_matrix_equals_s_times_witness` | EXACT | `True` |
| `member_smallest_nonzero_eigenvalue_s_r0sq_over_96_multiplicity_14_both_variants` | EXACT | `True` |
| `num_eigenvalues_consistent_with_exact_characteristic_polynomial` | NUM | `True` |
| `overall_1_over_40_not_perturbative_exact` | EXACT | `True` |
| `phi_sigma_consistency_n_Sigma_beta_equals_n_Phi_beta_equals_12915` | EXACT | `True` |
| `proper_subset_scaling_O27_only_moves_Sigma_radius_exact` | EXACT | `True` |
| `proper_subset_scaling_O48_only_moves_Phi_radius_exact` | EXACT | `True` |
| `quartic_unit_supports_within_declared_blocks_and_no_S_or_Phi17_portal` | EXACT | `True` |
| `rational_matrix_Phi_H_Sigma_block_equals_pinned` | EXACT | `True` |
| `research_MC_a0_max_within_3_sigma_of_exact` | RESEARCH_RECORD consistency | `True` |
| `research_MC_matrix_within_3_sigma_of_exact` | RESEARCH_RECORD consistency | `True` |
| `research_entries_labelled_with_provenance_and_pinned_digest` | RESEARCH_RECORD consistency | `True` |
| `research_sigma_self_entry_equals_exact_16645_over_448` | RESEARCH_RECORD consistency | `True` |
| `s_max_between_1_over_44_and_1_over_43_exact` | EXACT | `True` |
| `scaled_map_and_V0_linear_identity_sympy_residual_zero` | EXACT | `True` |
| `singlet_alphas_equal_pinned_exact_values` | EXACT | `True` |
| `singlet_betas_equal_pinned_exact_values` | EXACT | `True` |
| `sos_term_partition_equals_benchmark_coefficients_at_witness` | EXACT | `True` |
| `sos_term_partition_sums_to_committed_map_symbolically` | EXACT | `True` |
| `term_group_values_at_q0_equal_committed_minima` | EXACT | `True` |
| `unit_coverage_of_committed_map_exact` | EXACT | `True` |
| `unit_list_equals_classification_table` | EXACT | `True` |
| `zero_gradient_units_classified_by_field_content_and_exact_vev_scaling` | EXACT | `True` |

## Scope

**claimed**

- the exact tree-level s -> infinity singlet-channel matrix of the committed witness (five scalar blocks) and 21 < a0_max < 22 (a0_max = 21.654): the committed normalisation is non-perturbative
- the rescaling lemma: whole SOS terms scaled by positive factors keep the SOS identity, the vacuum, the equality set and the Hessian inertia (exact per-term stationarity/PSD at q0; blockwise test point)
- proper-subset scalings (O48 alone, O27 alone) break stationarity at q0 (exact)
- the overall x1/50 member: H_u = H_u(witness)/50, 447/39/0 and 451/35/0, gap r0^2/4800, V0/50, lambda_eff = 127/3200 and a0_max = 0.4331 < 1/2 in the computed channel (exact rational bound)
- s_max in (1/44, 1/43); x1/40 and the T_Phi-only x1/50 rescaling are not perturbative (exact)

**not_claimed**

- non-singlet two-particle channels are not computed: |a0| <= 1/2 is shown in the singlet channel only (a necessary condition, not full perturbative unitarity)
- finite-energy partial waves (trilinear exchange) and loop-level perturbativity or running are not computed
- the D12 GUT thresholds, the G6 remnant RG no-go and the G7 running are not recomputed at the rescaled member; they assume the committed normalisation
- no benchmark is chosen: the committed witness remains the G3 closing instance and this adds one perturbative family member; the blockwise point is a lemma test point
- no gate status, ledger entry, internal candidate or manuscript text changes

**relies_on_committed**

- G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; the equality set of every whole-term member is the same intersection of term zero sets)
- G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to the fresh witness certificates)
- g3_sm_pati_salam_exact_hessian_v20 binding units (bound to the live compiler in that module)
- g3_sm_pati_salam_candidate_v20 SOS identity (term partition = expanded_sos_coefficient_map)

**status_neutrality**

status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20 or any roadmap/readiness module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed; the committed witness remains the G3 closing instance and the internal candidate is unchanged

Runtime: 27 s.
