# G3 SM Pati-Salam O36 lambda_H Higgs-quartic member -- v20

**Status:** `SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_EXACT__TREE_LEVEL__STATUS_NEUTRAL` (`EXACT_O36_LAMBDA_H_MEMBER__TREE_LIGHT_DOUBLET_QUARTIC_FREE__NO_BENCHMARK__NO_GATE_CHANGE`)

**Theorem claimed:** `True`

Labels: EXACT (sympy or Fraction arithmetic), NUM (float64 recomputed here), RESEARCH_RECORD (not re-derived; sha256 provenance).

## Theorem (EXACT)

For every r0, rS, x0 > 0, lambda_H > 0, real kappa with kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1) and eps >= 0, the O36 member (the decoupled-singlet map with O36_B01 = O36_B02 = lambda_H instead of 2; 27 parameters inside the 51-parameter contract) satisfies V >= V0 = -1 - r0^4/8 - rS^4 - x0^4/32 with {V = V0} = G.(p, r0 sigma_std, 0, rS, x0), G = SO(10) x U(1)_X x U(1)_PQ (given the committed family certificate and the committed equality-set theorem's lambda_H-free parts).  The H quartic is lambda_H N_H^2 exactly (I_1 + I_54 = N_H^2), and after Cauchy-Schwarz the H/S block is lambda_H (N_H - |kappa| t/lambda_H)^2 + t^2 (lambda_S u^2 - kappa^2/lambda_H) + eps N_H, t = |S| - rS, u = |S| + rS (sympy residual 0).  The domain is sharp at eps = 0: V >= V0 fails for every kappa^2 > 4 lambda_H lambda_S rS^2 when eps = 0 (exact violating points), while on the boundary the bound and the equality set still hold; for eps > 0 the exact domain of the H/S block is |kappa| <= 2 sqrt(lambda_H lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the certified margin is sufficient there but not sharp.  The equality set holds for every lambda_H > 0 in the domain because T1-T5, T7, T8 are kappa-free.  The tree light-doublet quartic is lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) > 0, a free positive parameter (lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS)), and V4 >= lambda_H |q|^4/(165 lambda_H + 4).  Exact over Q at (1/5, 1, 1, -1/100) with lambda_H in {2, 1/100, 1/1000} and at the witness point (1/5, 1/5, 1, -1/20) with lambda_H = 1/10: grad V(q0) = 0 and the 486 x 486 Hessian is bit-identical to the lambda_H = 2 member (447/39/0 at eps = 0, kernel = 35 orbit tangents + 4 doublet directions, gap r0^2/96 x 14; 451/35/0 at eps = r0^2/100).  Tree level only.

## Physics status (read first)

- **certifies**: the tree-level O36 lambda_H member of the SOS-certified decoupled-singlet family only: the family map with O36_B01 = O36_B02 = lambda_H (committed 2), certified for kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1); its light-doublet tree quartic lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) is a free positive parameter
- **does_not_choose_a_benchmark**: this report does NOT choose a benchmark: its (r0, rS, x0, kappa, lambda_H) points are certificate points, not benchmarks
- **does_not_change_G3_G4_G5**: the committed witness (lambda_H = 2, rS = r0, kappa = -r0/4) remains the G3 and G4 closing instance and G5 stays bound to the committed lambda_H = 2 coefficient vector; no gate status, ledger entry or roadmap text changes
- **tree_level_only**: lambda_eff is the tree-level light-doublet quartic; the one-loop quartic matching at v_R (research estimate +-0.004) is not computed, and the running of lambda_H is research-recorded only
- **higgs_matching_is_research**: research record (CONDITIONAL): tree matching of lambda_SM(v_R) at the research benchmarks BM-DA1/BM-E needs lambda_H(M_GUT) ~ 0.036-0.104, inside the certified domain; that running used an anti-SOS Delta_R region point (G6 assumed fixed); the a1/lh2 sensitivity rows are outside the certified member (an H-Sigma portal and O36_B01 != O36_B02), and one further row needs lambda_H < 0; the G7 evidence on these benchmarks is recorded separately (g7_decoupled_singlet_benchmark_evidence_v20)

## Verdict

Exact (48 checks): setting the H self-quartics O36_B01 = O36_B02 = lambda_H (committed 2) in the decoupled-singlet map keeps the SOS certificate for every kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1): I_1 + I_54 = N_H^2 (sympy, 10 complex variables) and, after Cauchy-Schwarz, the H/S block is lambda_H (N_H - |kappa| t/lambda_H)^2 + t^2 (lambda_S u^2 - kappa^2/lambda_H) + eps N_H (sympy residual 0); the margin is sharp at eps = 0 (exact violating points beyond it; for eps > 0 the exact domain is |kappa| <= 2 sqrt(lambda_H lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the margin is sufficient but not sharp) and the bound still holds on the boundary.  V0, the equality set and the exact 486 x 486 Hessian at q0 are unchanged (bit-identical at 4 member points; 447/39/0 and 451/35/0).  The tree light-doublet quartic lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) is a free positive parameter (lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS), -1.5625e-14 at rS = 1000 r0), and V4 >= lambda_H |q|^4/(165 lambda_H + 4).  Tree level only: the one-loop matching at v_R (research estimate +-0.004) is not computed, lambda_SM(v_R) is matched only in the research record (CONDITIONAL), no benchmark is chosen, the committed lambda_H = 2 witness remains the G3/G4 closing instance, G5 stays bound to it, and no gate changes.

FLOAT64 corroboration (NUM), outside the exact check count: 3/3 passed (live O36 rows vanish at q0, compiler O36 directions = I_1 and I_54, compiler violating value).

Checks: 48/48 passed.

## Member points (EXACT)

| label | (r0, rS, x0, kappa) | lambda_H | margin 4 lambda_H rS^2 - kappa^2 | lambda_eff | V0 | eps window upper | perturbative member | Hessian = lambda_H 2 member | tuned / raised inertia | gap tuned (mult) |
|---|---|---|---|---|---|---|---|---|---|---|
| rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2 | `(1/5, 1, 1, -1/100)` | `2` | `79999/10000` | `79999/40000` | `-40629/20000` | `599/50` | `True` | `True` | `447/39/0 / 451/35/0` | `1/2400` (`14`) |
| rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100 | `(1/5, 1, 1, -1/100)` | `1/100` | `399/10000` | `399/40000` | `-40629/20000` | `599/50` | `True` | `True` | `447/39/0 / 451/35/0` | `1/2400` (`14`) |
| rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000 | `(1/5, 1, 1, -1/100)` | `1/1000` | `39/10000` | `39/40000` | `-40629/20000` | `599/50` | `True` | `True` | `447/39/0 / 451/35/0` | `1/2400` (`14`) |
| rS_eq_r0_witness__lambda_H_1_over_10 | `(1/5, 1/5, 1, -1/20)` | `1/10` | `27/2000` | `27/320` | `-20661/20000` | `599/50` | `True` | `True` | `447/39/0 / 451/35/0` | `1/2400` (`14`) |

## SOS identity (EXACT, sympy)

- T6' = lambda_H N_H^2 + (2|kappa| rS + eps) N_H + 2 kappa Re(conj(H.H) conj(S)) + lambda_S (|S|^2 - rS^2)^2 (lambda_S = O23 = 1 in the map; O04 = -2 lambda_S rS^2)
- Cauchy-Schwarz: 2 kappa Re(conj(H.H) conj(S)) >= -2|kappa| |H.H| |S| >= -2|kappa| N_H |S| (|H.H| <= N_H: h_self.cauchy_schwarz_identity), so T6' >= R(N_H, |S|)
- R = lambda_H (N - k t/lambda_H)^2 + t^2 (lambda_S u^2 - k^2/lambda_H) + eps N, t = s - rS, u = s + rS (residual `0`)
- reduction to the committed identity at lambda_H = 2: `{'committed_identity_residual_candidate': '0', 'completed_square_at_lambda_H_2_minus_committed': '0', 'reduced_form_at_lambda_H_2_minus_committed': '0'}`
- sign argument: t >= 0: u >= 2 rS, so the bracket is >= 4 lambda_S rS^2 - k^2/lambda_H + lambda_S t (t + 4 rS) > 0 when k^2 < 4 lambda_H lambda_S rS^2, hence R > 0 unless t = 0 and N = 0; t < 0: R = lambda_H N^2 + 2 k N |t| + lambda_S t^2 u^2 + eps N with every term >= 0 and lambda_S t^2 u^2 > 0 (u > 0).  Zero set: t = 0, N_H = 0, i.e. H = 0 and |S| = rS
- domain: kappa^2 < 4 lambda_H lambda_S rS^2, equivalently lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) > 0
- boundary bracket: `lambda_S*(-rS + s)*(3*rS + s)`; at kappa^2 = 4 lambda_H lambda_S rS^2 (lambda_eff = 0) the bracket is lambda_S t (s + 3 rS) >= 0 for t >= 0 and the t < 0 argument is unchanged, so V >= V0 and the equality set still hold on the boundary; the certified domain is the open kappa^2 < 4 lambda_H lambda_S rS^2 (the committed convention)
- operator level: V_member - V0 = T1 + ... + T5 + T6' + T7 + T8 with T6' = T6 + T9 + (lambda_H - 2)(I_1 + I_54) = T6 + T9 + (lambda_H - 2) N_H^2 (the family's eight-term identity plus the H self-identity)

## H self-identities (EXACT, sympy)

- I_1 + I_54 - N_H^2 = `0`
- N_H^2 - |H.H|^2 = sum_{i<j} |conj(H_i) H_j - conj(H_j) H_i|^2 (so |H.H| <= N_H): residual `0`
- a I_1 + b I_54 = b N_H^2 + (a - b) I_1; at H = e_0 (I_1 = 1/10, N_H^2 = 1) and at the null vector H = e_0 + i e_1 (I_1 = 0, N_H^2 = 4) the identity a I_1 + b I_54 = c N_H^2 forces a = c = b
- every monomial of I_1 and I_54 has degree 4, so their value, gradient and Hessian vanish at H = 0 (the O36 binding units of g3_sm_pati_salam_exact_hessian_v20 have empty pieces for this reason)

## Sharpness (EXACT)

H = h e_6 real (weak-doublet direction), S = rS + t real, kappa < 0, N_H = h^2 = |kappa| t/lambda_H: V - V0 = t^2 [lambda_S (2 rS + t)^2 - kappa^2/lambda_H] (for kappa > 0 the same with H = i h e_6) (residual `0`).

| rS | lambda_H | abs kappa | t | margin | V - V0 |
|---|---|---|---|---|---|
| `1` | `1/100` | `21/100` | `1/1000` | `-41/10000` | `-405999/1000000000000` |
| `1` | `1/1000` | `7/100` | `1/10000` | `-9/10000` | `-89959999/10000000000000000` |
| `1` | `2` | `3` | `3/100` | `-1` | `-34119/100000000` |

## Light-doublet tree quartic (EXACT, series)

- lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) (series: `-k**2/(4*lambda_S*rS**2) + k*l34/(2*lambda_S*rS) - l34**2/(4*lambda_S) + lambda_H`)
- with O34: lambda_H - (|kappa| - l34 rS)^2/(4 lambda_S rS^2) (series identity only; an O34 member is an S portal and is NOT certified here)
- at kappa = -r0^2/(4 rS): lambda_eff - lambda_H = `-r0**4/(64*lambda_S*rS**4)`; at rS = 1000 r0: `-1/64000000000000` = `-1.5625e-14`

## Boundedness from below (EXACT)

- V4(q) >= |q|^4 / sum(beta^2/alpha) with alpha_NH = lambda_H (the candidate's Cauchy-Schwarz argument): constant `lambda_H/(165*lambda_H + 4)`, values `{'1/100': '1/565', '1/1000': '1/4165', '2': '1/167'}`
- G5 stays bound to the committed lambda_H = 2 coefficient vector (constant 1/167); this report records the member's constant only (status-neutral)

## Equality set (EXACT bindings)

{V = V0} is the intersection of the zero sets of the SOS terms (each >= 0): {V_member = V0} = Z(T1..T5, T7, T8) and Z(T6'), with Z(T6') = {H = 0, |S| = rS} = Z(T6) (sos_identity.sign_argument; T9 = eps N_H is part of T6').  T1-T5, T7 and T8 are kappa-free (kappa enters the SOS map only through O06 and O12, i.e. T6: sos_non_T6_terms_kappa_free_three_signs), so the set equals {V_family(kappa') = V0} = G.q0 for any kappa' with kappa'^2 < 8 rS^2 (e.g. kappa' = 0) by the committed decoupled-singlet family certificate (rS) and the committed equality-set theorem (P1/P2 contain no H or S and carry over verbatim; charges, phases, operator neutrality and the tangent ranks are lambda_H-free).  This covers lambda_H > 2 with 8 rS^2 <= kappa^2 < 4 lambda_H lambda_S rS^2, where the family at the same kappa is not certified

## Research record (RESEARCH_RECORD, not re-derived)

scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit only; the source files are not in the repository and were hashed at generation time (the session scratch area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at runtime.

| entry | source | sha256 | meaning |
|---|---|---|---|
| `e1_float_hessian_and_plane_scan` | `E-G7-completion/e1_quartic_member.json` | `2e3e64a139b4d8df...` | float64 live-compiler Hessian at q0 identical for every lambda_H (max difference 0), projected inertia 0 negative / 4 zero, lightest massive r0^2/96, and the (\|S\|, light doublet) plane scan minimum gap (all rows equal) |
| `e1_lambda_eff_exact_strings` | `E-G7-completion/e1_quartic_member.json` | `2e3e64a139b4d8df...` | research exact lambda_eff = lambda_H - kappa^2/(4 rS^2) at (r0, rS, x0, kappa) = (1/5, 1, 1, -1/100) per lambda_H (re-derived exactly by this module) |
| `e1_lambda_eff_numerical_projection` | `E-G7-completion/e1_quartic_member.json` | `2e3e64a139b4d8df...` | float64 tree quartic of the light doublet by projection (V minimised over every other field at fixed doublet amplitude, fit V - V0 = c2 a^2 + c4 a^4 + c6 a^6, lambda = 4 c4) at (1/5, 1, 1, -1/100) |
| `e3_lambda_H_required_BM_DA1` | `E-G7-completion/e3_quartic_rg.json` | `b49b21f4191af7a0...` | CONDITIONAL tree matching of lambda_SM(v_R) (PDG 2024, three-loop curve) through the one-loop PS-EFT running v_R..M_GUT: the required lambda_H(M_GUT) per Yukawa variant (W witness box, Tn top + Dirac nu, T top only, T0 no Yukawa) and with a +-0.004 one-loop threshold shift; the running uses D's anti-SOS Delta_R region point (rho = 1e3), i.e. assumes G6 fixed |
| `e3_lambda_H_required_BM_E` | `E-G7-completion/e3_quartic_rg.json` | `b49b21f4191af7a0...` | as e3_lambda_H_required_BM_DA1 at BM-E (rho = 10^2.5, D remnants); CONDITIONAL in the same way |
| `e3b_sensitivity_lambda_H` | `E-G7-completion/e3b_quartic_sens.json` | `20617026db9b1ed7...` | sensitivity of the required lambda_H(M_GUT) to the Delta_R sector (lam_(35,5) x0.7/x1.3, D's lam_GUT corners) for Yukawa variants T and W, and to two GUT-threshold deformations that are NOT boundary conditions of the certified member: a1 = +-0.02 (an H-Sigma portal (D^+D)(h^+h) at M_GUT, not in the 27-parameter member map) and lh2 = +-0.02 (O36_B01 != O36_B02, not lambda_H N_H^2) |
| `v4_kappa_correction_DA_prime` | `E-G7-completion/verify-physics/v4_e1_check.json` | `b879932351e08ac8...` | lambda_H - lambda_eff = (v_R/v_S)^4/64 for kappa = -r0^2/(4 rS) in the research DA' convention (r0 <-> v_R, rS <-> v_S); independent verifier sympy check of the O36 H/S block |
| `v_sos_sampling` | `E-G7-completion/verify-feasibility/v_sos.json` | `4974fd881893c270...` | independent verifier: sympy residual of the completed square and the minimum of the unreduced T6'/(1 + N^2 + \|S\|^4) over 2e5 random samples under a strict margin (sample count from the script, range(200000)) |

Consistency: `{'e1_exact_strings_equal_module': True, 'e1_projection_max_relative_deviation': 7.39376255932e-05, 'e3_required_lambda_H_inside_certified_domain': {'BM-DA1': True, 'BM-E': True}, 'e3b_lambda_H_ranges': {'BM-DA1': {'T': [0.036707398525, 0.15705084065], 'W': [-0.00901156314302, 0.103984420275]}, 'BM-E': {'T': [0.0415675206997, 0.111568271338], 'W': [5.81259739402e-05, 0.067561503296]}}, 'e3b_rows_outside_domain': {'BM-DA1': ['W_Delta_GUT_hi'], 'BM-E': []}, 'e3b_rows_outside_member_map': {'BM-DA1': ['T_a1G=+0.02', 'T_a1G=-0.02', 'T_lh2G=+0.02', 'T_lh2G=-0.02', 'W_a1G=+0.02', 'W_a1G=-0.02', 'W_lh2G=+0.02', 'W_lh2G=-0.02'], 'BM-E': ['T_a1G=+0.02', 'T_a1G=-0.02', 'T_lh2G=+0.02', 'T_lh2G=-0.02', 'W_a1G=+0.02', 'W_a1G=-0.02', 'W_lh2G=+0.02', 'W_lh2G=-0.02']}, 'v4_BM-DA1_relative_deviation': 0.0, 'v4_BM-E_relative_deviation': 0.0}`

Conditional: the e3/e3b running used D's anti-SOS Delta_R region point with G6 assumed fixed and a one-loop PS-EFT; lambda_SM(v_R) is matched at tree level only; BM-DA1/BM-E are research benchmarks, not chosen here.

## FLOAT64 evidence (NUM, outside the exact check count)

| item | value |
|---|---|
| F1 live O36 rows at q0 (abs value, max abs gradient, max abs Hessian) | `{'lambda::O36_B01_H_self_quartics': {'abs_value': 0.0, 'max_abs_gradient': 0.0, 'max_abs_hessian': 0.0}, 'lambda::O36_B02_H_self_quartics': {'abs_value': 0.0, 'max_abs_gradient': 0.0, 'max_abs_hessian': 0.0}}` |
| F2 compiler O36 vs I_1, I_54, lambda_H N_H^2: max relative difference | `4.72438574264e-16` |
| F3 compiler V - V0 on the violating curve (exact) | `-4.05999002862e-07` (`-405999/1000000000000`) |

| FLOAT64 check | passed |
|---|---|
| `float_F1_live_O36_rows_value_gradient_hessian_zero_at_q0` | `True` |
| `float_F2_compiler_O36_directions_equal_I1_I54_and_lambda_H_NH2` | `True` |
| `float_F3_compiler_matches_exact_violating_value` | `True` |

## Checks

| check | label | passed |
|---|---|---|
| `bfb_quartic_constant_lambda_H_over_165_lambda_H_plus_4_symbolic_points_and_committed_1_over_167` | EXACT | `True` |
| `committed_family_report_certified_77_checks_0_failed_float_consistent` | EXACT | `True` |
| `equality_set_premises_from_committed_report` | EXACT | `True` |
| `h_self_I1_I54_homogeneous_quartics_value_gradient_hessian_vanish_at_H0` | EXACT | `True` |
| `h_self_I1_plus_I54_equals_NH_squared_sympy_20_real_variables` | EXACT | `True` |
| `h_self_NH2_minus_abs_HdotH2_equals_45_current_sum_of_squares_sympy` | EXACT | `True` |
| `h_self_quartic_multiple_of_NH2_iff_O36_B01_eq_O36_B02_and_member_entries_equal_lambda_H` | EXACT | `True` |
| `lambda_eff_equals_lambda_H_minus_candidate_S_exchange_shift_at_every_point` | EXACT | `True` |
| `lambda_eff_minus_lambda_H_is_minus_r0_4_over_64_lambda_S_rS_4_at_kappa_minus_r0sq_over_4rS` | EXACT | `True` |
| `lambda_eff_series_closed_form_with_and_without_O34_symbolic` | EXACT | `True` |
| `member_V0_equals_family_V0_lambda_H_free_symbolic` | EXACT | `True` |
| `member_operator_ids_equal_witness_and_committed_P3_operator_ids` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000__benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000__hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000__margin_positive_and_lambda_eff_closed_form` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000__member_map_27_parameters_in_contract_changes_only_O36_vs_family_map` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000__raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100__benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100__hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100__margin_positive_and_lambda_eff_closed_form` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100__member_map_27_parameters_in_contract_changes_only_O36_vs_family_map` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100__raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2__benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2__hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2__margin_positive_and_lambda_eff_closed_form` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2__member_map_27_parameters_in_contract_changes_only_O36_vs_family_map` | EXACT | `True` |
| `point_rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2__raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4` | EXACT | `True` |
| `point_rS_eq_r0_witness__lambda_H_1_over_10__benchmark_certificate_447_39_0_kernel_T35_plus_D4_gap_r0sq_over_96_mult_14` | EXACT | `True` |
| `point_rS_eq_r0_witness__lambda_H_1_over_10__hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants` | EXACT | `True` |
| `point_rS_eq_r0_witness__lambda_H_1_over_10__margin_positive_and_lambda_eff_closed_form` | EXACT | `True` |
| `point_rS_eq_r0_witness__lambda_H_1_over_10__member_map_27_parameters_in_contract_changes_only_O36_vs_family_map` | EXACT | `True` |
| `point_rS_eq_r0_witness__lambda_H_1_over_10__raised_O06_certificate_451_35_0_kernel_T35_gap_r0sq_over_100_mult_4` | EXACT | `True` |
| `research_record_consistent_with_exact_values_and_disclosed_outliers` | RESEARCH_RECORD | `True` |
| `research_record_entries_labelled_with_provenance` | RESEARCH_RECORD | `True` |
| `sharpness_curve_identity_exact` | EXACT | `True` |
| `sharpness_only_at_eps_0_exact_eps_positive_domain` | EXACT | `True` |
| `sharpness_other_sos_terms_vanish_on_curve_Q_H_row_and_column_6_zero` | EXACT | `True` |
| `sharpness_violating_points_exact_beyond_margin` | EXACT | `True` |
| `sos_T6_prime_equals_T6_plus_T9_plus_lambda_H_minus_2_times_I1_plus_I54_three_signs` | EXACT | `True` |
| `sos_family_eight_term_expansion_passes_three_kappa_signs` | EXACT | `True` |
| `sos_hs_boundary_bracket_equals_lambda_S_t_times_s_plus_3rS` | EXACT | `True` |
| `sos_hs_completed_square_identity_symbolic_residual_zero` | EXACT | `True` |
| `sos_hs_completed_square_reduces_to_committed_identity_at_lambda_H_2_lambda_S_1` | EXACT | `True` |
| `sos_hs_margin_equivalent_to_lambda_eff_positive_symbolic` | EXACT | `True` |
| `sos_hs_sign_argument_identities_exact` | EXACT | `True` |
| `sos_member_map_equals_family_sos_map_plus_eps_except_O36_equal_lambda_H_three_signs` | EXACT | `True` |
| `sos_non_T6_terms_kappa_free_three_signs` | EXACT | `True` |
| `witness_point_member_certificates_equal_committed_exact_hessian_report` | EXACT | `True` |

## Scope

**claimed**

- EXACT: I_1 + I_54 = N_H^2 and N_H^2 - |H.H|^2 = sum of squares (sympy, 20 real variables); the H quartic is lambda_H N_H^2 iff O36_B01 = O36_B02
- EXACT: the O36 member's SOS identity for every kappa^2 < 4 lambda_H lambda_S rS^2 (lambda_S = O23 = 1) and eps >= 0 (sympy residual 0; reduces to the committed identity at lambda_H = 2), valid on the boundary, and sharp at eps = 0 (exact violating points beyond it); for eps > 0 the exact H/S-block domain is |kappa| <= 2 sqrt(lambda_H lambda_S) rS + sqrt(2 eps sqrt(lambda_H lambda_S)), so the margin is sufficient but not sharp there
- EXACT: V0 and the equality set unchanged for every lambda_H > 0 in the domain (T1-T5, T7, T8 are kappa-free; bound to the committed equality-set and family artifacts)
- EXACT: the 486 x 486 Hessian over Q bit-identical to the lambda_H = 2 member at (1/5, 1, 1, -1/100) for lambda_H in {2, 1/100, 1/1000} and at the witness point for lambda_H = 1/10 (447/39/0, 451/35/0), and the witness-point certificates equal to the committed exact-Hessian report
- EXACT: lambda_eff = lambda_H - kappa^2/(4 lambda_S rS^2) (series), a free positive parameter; lambda_eff - lambda_H = -r0^4/(64 rS^4) at kappa = -r0^2/(4 rS)
- EXACT: V4 >= lambda_H |q|^4/(165 lambda_H + 4)
- NUM: the live compiler's O36 rows vanish at q0, its O36 directions equal I_1 and I_54, and it reproduces the exact violating value

**not_claimed**

- no benchmark is chosen: the (r0, rS, x0, kappa, lambda_H) points are certificate points
- tree level only: the one-loop quartic matching at v_R (research estimate +-0.004) is not computed, and the RG running of lambda_H is research-recorded only (CONDITIONAL)
- lambda_SM(v_R) is not matched by this certificate; the required lambda_H(M_GUT) values are research records at research benchmarks (BM-DA1, BM-E) with an anti-SOS Delta_R point (G6 assumed fixed); the a1/lh2 sensitivity rows are outside the certified member (an H-Sigma portal and O36_B01 != O36_B02), and one further row needs lambda_H < 0 (outside the certified domain)
- no S-portal member (O34 or others) is certified; the O34 lambda_eff formula is a series identity only
- the committed witness (lambda_H = 2) stays the G3/G4 closing instance and G5 stays bound to the committed lambda_H = 2 vector; no gate status changes and nothing is wired into the ledger
- the G6 tree spectrum, G7 running and G8 flavour are unchanged by O36 at tree level (O36 is quartic in H and invisible at q0) and are not re-derived here
- no manuscript change

**relies_on_committed**

- G3_SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_V20.json (certified, 77 checks, 0 failed; the rS family, its eight-term SOS identity, tangent ranks and P3 at rS)
- G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (proved status; P1/P2 contain no H or S)
- G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (certified; equal to the witness-point member certificates)

**status_neutrality**

status-neutral: not read by g1_g8_gate_ledger_v20, final_g3_acceptance_gate_v20, g4_sm_closure_binding_v20 or any roadmap/readiness module; G1-G5 stay CLOSED, G6 OPEN, G7/G8 BLOCKED exactly as committed, the committed lambda_H = 2 witness remains the G3 and G4 closing instance, and G5 stays bound to the committed coefficient vector

Runtime: 31 s.
