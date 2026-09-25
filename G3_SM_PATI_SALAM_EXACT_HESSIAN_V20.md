# G3 SM Pati-Salam exact full Hessian -- v20

**Status:** `SM_PATI_SALAM_EXACT_FULL_HESSIAN_RANK_447_NULLITY_39_CERTIFIED__G3_OPEN`

**Theorem claimed:** `True`

Exact over Q at the SM Pati-Salam benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0) of g3_sm_pati_salam_candidate_v20: grad V(q0) = 0; the complete 486 x 486 Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) is positive semidefinite with rank 447 and nullity 39; its kernel is the 35-dimensional tangent space of the SO(10) x U(1)_X x U(1)_PQ orbit plus the 4 real light-doublet directions Re H_6..9; it is positive definite on a 447-dimensional coordinate complement of the kernel; its smallest nonzero eigenvalue is r0^2/96.  With O06 raised by r0^2/100: rank 451, nullity 35, kernel = the orbit tangent space, smallest nonzero eigenvalue r0^2/100.  Entries are derived from integer source tensors in the radical-free coordinates q = D u, D = diag(1^210, sqrt(2)^276) (Sylvester); the compiler = exact-operator identity is exact per operator and float64 end to end (bound to <= 1e-12).

Exact over Q: at the SM Pati-Salam benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0) the gradient vanishes and the complete 486 x 486 Hessian is PSD with rank 447 and nullity 39; its kernel is exactly the 35 SO(10) x U(1)_X x U(1)_PQ orbit tangents plus the 4 real light-doublet directions, it is positive definite on a 447-dimensional coordinate complement of the kernel, and its smallest nonzero eigenvalue is exactly r0^2/96.  It is therefore NOT strictly positive on the 451-dimensional symmetry quotient (4 exact non-symmetry zero modes; flags.strict_quotient_positive = False in the repository's sense).  With O06 raised by r0^2/100 the rank is 451, the nullity 35 and the kernel is exactly the symmetry orbit (strictly positive on the symmetry quotient).  For the whole family O06 = 2|kappa| r0 + eps (V_eps = V + eps N_H): {V_eps = V0} = G.q0 for every eps >= 0 (L1, given the equality-set theorem), and for every eps > 0 the Hessian at q0 is PSD with kernel exactly the 35 orbit tangents, i.e. rank 451, nullity 35 and strictly positive on the symmetry quotient (L2; inertia 451/35/0 re-certified at eps = r0^2/100 and r0^2/10^6); the doublet Re H_6..9 has mass^2 exactly eps, light but massive for eps << r0^2, so electroweak symmetry is still not broken, and the tuned eps = 0 limit is not a strict minimum on the symmetry quotient.  The entries are derived from integer source tensors in the radical-free coordinates u = D^-1 q (Sylvester's law of inertia), and the exact matrix agrees with the live compiler Hessian to within 1e-12 and rounds from it on the exact lattice (float64 binding).  This report does not close G3 by itself: G3 is decided by final_g3_acceptance_gate_v20 through its sm_pati_salam track, whose witness is an eps > 0 member; the candidate's physics caveats are unchanged and routed downstream (G4, G6-G8).

Checks: 52/52 passed.

## Congruence

- q = D u, u_Phi = q_Phi, u_c = q_c/sqrt(2) = (Re c, Im c) for c in H10, Sigma126bar, S, Phi17; H_u = D Hess_q D (chain rule for the linear change q = D u).
- in the chart only the Phi-Sigma block carries sqrt(2) (Hess_q[Phi, Sigma] in Q/sqrt(2)); every H_u entry is rational.
- D is real diagonal and invertible, so Hess_q and H_u have the same rank, nullity and signature, ker Hess_q = D ker H_u, and Hess_q - lambda I = D^-1 (H_u - lambda D^2) D^-1.

## Exact certificate

| quantity | benchmark | O06 raised |
|---|---|---|
| O06 | `1/50` | `51/2500` |
| common denominator of H_u | `2016000` | `10080000` |
| gradient exactly zero | `True` | `True` |
| support components (largest) | `65` (`16`) | `65` (`16`) |
| inertia (+/0/-) | `447/39/0` | `451/35/0` |
| rank / nullity | `447/39` | `451/35` |
| kernel spanning set (exact rank) | 35 symmetry tangents + 4 real light-doublet directions (`39`) | 35 symmetry tangents (`35`) |
| kernel equals spanning set | `True` | `True` |
| PD on pivot complement (dim) | `True` (`447`) | `True` (`451`) |
| strictly positive on symmetry quotient (zero modes beyond orbit) | `False` (`4`) | `True` (`0`) |
| smallest nonzero eigenvalue / r0^2 (multiplicity) | `1/96` (`14`) | `1/100` (`4`) |
| max abs exact - live (chart) | `8.74e-14` | `8.74e-14` |
| max abs exact - live gradient | `4.92e-14` | `4.92e-14` |
| live x denominator rounds to exact numerator (max residual) | `True` (`3.45e-07`) | `True` (`1.72e-06`) |

## Binding units (exact operator vs weighted compiler rows)

| unit | parameters | max abs Hessian difference | relative |
|---|---|---|---|
| O03 \|Phi17\|^2 | 1 | `0` | `0` |
| O04 \|S\|^2 | 1 | `0` | `0` |
| O05 N_Sigma | 1 | `2.22e-16` | `2.22e-16` |
| O06 N_H | 1 | `2.22e-16` | `2.22e-16` |
| O07 \|Phi\|^2 | 1 | `0` | `0` |
| O14 Sigma^dag M_Phi Sigma | 1 | `4.44e-16` | `2.22e-16` |
| O20 \|Phi17\|^4 | 1 | `8.88e-16` | `1.48e-16` |
| O23 \|S\|^4 | 1 | `2.78e-17` | `2.78e-17` |
| O27 I_1050bar | 1 | `1.39e-17` | `1.39e-17` |
| O27 I_2772bar | 1 | `2.43e-17` | `2.43e-17` |
| O27 I_4125 | 1 | `6.25e-17` | `6.25e-17` |
| O27 I_54 | 1 | `2.39e-18` | `2.39e-18` |
| O36 I_1(H) (quartic in H) | 1 | `0` | `0` |
| O36 I_54(H) (quartic in H) | 1 | `0` | `0` |
| O44 \|\|M_Phi Sigma\|\|^2 + \|\|C_Phi Sigma\|\|^2 | 6 | `6.95e-13` | `1.74e-13` |
| O46 (3/5) I_1 - I_54 = H^dag(\|Phi\|^2 - C(Phi))H | 2 | `2.22e-16` | `2.22e-16` |
| O48 J0 | 1 | `0` | `0` |
| O48 J2 | 1 | `0` | `0` |
| O48 J3 | 1 | `0` | `0` |
| O48 J4 | 1 | `0` | `0` |
| re::O12 2 Re[conj(H.H) conj(S)] | 1 | `5.55e-17` | `5.55e-17` |

## eps family: O06 = 2|kappa| r0 + eps

**Member:** V_eps = V + eps N_H: O06 = 2|kappa| r0 + eps, the other 26 benchmark couplings unchanged, eps >= 0

**Theorem claimed:** `True` (30/30 checks)

For every eps >= 0 let V_eps = V + eps N_H (O06 = 2|kappa| r0 + eps, the other 26 couplings of the benchmark r0 = 1/5, x0 = 1, kappa = -r0/4 unchanged; N_H = H^dag H is the compiler operator O06).  (L1) N_H = |u_H|^2 >= 0 with equality iff H = 0, and H = 0 on {V = V0}, so V_eps >= V >= V0 and {V_eps = V0} = {V = V0} = G.q0, G = SO(10) x U(1)_X x U(1)_PQ; V_eps is G-invariant, has the same quartic part (BFB unchanged) and grad V_eps(q0) = 0.  (L2) Hess_u V_eps(q0) = H_u + eps Hess_u N_H with Hess_u N_H = 2 P_H (Hess_q N_H = P_H in the chart); both terms are PSD, so for every eps > 0 the Hessian is PSD with kernel ker H_u cap ker P_H = the 35-dimensional G-orbit tangent space (rank 451, nullity 35), strictly positive on the 451-dimensional symmetry quotient.  The H block decouples at q0 and Re H_6..9 are exact eigenvectors of Hess_q V_eps(q0) with eigenvalue eps (the doublet mass^2 in units of M_GUT^2), the smallest nonzero eigenvalue with multiplicity exactly 4 for 0 < eps < r0^2/96.  L1 rests on the equality-set theorem (committed report, proved status required); L2 and the doublet statement are exact over Q; exact inertia 451/35/0 is re-certified at eps = r0^2/100 and r0^2/10^6.

**Required statement (final G3 gate, SM Pati-Salam track):** For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0.

**Currently passes:** `True` (eps window `0 < eps < 599/50`; closes G3 by itself: `False`)

- L1: V_eps = V + eps N_H with N_H = |u_H|^2 >= 0 (equality iff H = 0).  Hence V_eps >= V >= V0, and V_eps(q) = V0 iff V(q) = V0 and eps N_H(q) = 0.  On {V = V0} = G.q0 we have H = 0, so {V_eps = V0} = {V = V0} = G.q0 for every eps >= 0.  N_H is G-invariant (so V_eps is), quadratic (so the quartic part and the bound V4 >= |q|^4/167 are unchanged), and grad V_eps(q0) = grad V(q0) + eps grad N_H(q0) = 0.
- L1 relies on `G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (committed; read, not rebuilt)` with status `SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN`.
- L2: Hess_u V_eps(q0) = H_u + eps B with B = Hess_u N_H = 2 P_H.  For symmetric PSD A, B and eps > 0, x^T (A + eps B) x = x^T A x + eps x^T B x and x^T M x = 0 iff M x = 0 for PSD M, so A + eps B is PSD and ker(A + eps B) = ker A cap ker B.  ker H_u = span(T35) + span(D4) with D4 inside the H block and T35 zero there, so B T35 = 0, B D4 = 2 D4 and ker H_u cap ker B = span(T35): for every eps > 0 the Hessian is PSD with rank 451, nullity 35, kernel exactly the G-orbit tangent space, strictly positive on the 451-dimensional symmetry quotient.
- Doublet: At q0 the H block of Hess V decouples and is diagonal in the chart with curvatures 0 (Re H_6..9, the tuned doublet), r0^2 (Im H_6..9), 1 (Re H_0..5) and 1 + r0^2 (Im H_0..5); Hess_q N_H = P_H adds eps to each.  So Re H_6..9 are exact eigenvectors of Hess_q V_eps(q0) with eigenvalue eps for every eps >= 0 (the doublet mass^2 in units of M_GUT^2); the rest of the spectrum is eps-independent with nullity 35 and no eigenvalue in (0, r0^2/96), so for 0 < eps < r0^2/96 eps is the smallest nonzero eigenvalue with multiplicity exactly 4.
- H-block chart curvatures at q0 (value/r0^2: multiplicity): `0`: 4, `1`: 4, `25`: 6, `26`: 6
- Physical reading: eps = (m_D/M_GUT)^2: the SM doublet Re H_6..9 is light but massive for 0 < eps << r0^2, and eps -> 0+ is the tuned massless limit, which is PSD but not strictly positive on the symmetry quotient (447/39).  Electroweak symmetry is not broken on any member (H = 0 and the tree-level doublet mass^2 eps >= 0).

| eps | eps/r0^2 | O06 | inertia (+/0/-) | kernel = orbit | smallest nonzero eigenvalue (multiplicity) |
|---|---|---|---|---|---|
| `1/2500` | `1/100` | `51/2500` | `451/35/0` | `True` | `1/2500` (`4`) |
| `1/25000000` | `1/1000000` | `500001/25000000` | `451/35/0` | `True` | `1/25000000` (`4`) |

| eps-family check | passed |
|---|---|
| `L1_N_H_homogeneous_quadratic_so_quartic_part_unchanged` | `True` |
| `L1_N_H_invariant_under_G` | `True` |
| `L1_N_H_is_sum_of_squares_of_u_H` | `True` |
| `L1_O06_compiler_direction_is_unit_Hdag_i_H_i_without_dressing` | `True` |
| `L1_O06_unit_hessian_is_hess_u_N_H_equal_2_P_H` | `True` |
| `L1_V_eps_differs_from_V_only_in_O06_by_eps` | `True` |
| `L1_benchmark_inside_equality_domain_kappa_squared_below_8_r0_squared` | `True` |
| `L1_chart_convention_H_equals_x_plus_i_y_over_sqrt2` | `True` |
| `L1_equality_report_proved_status_and_premises` | `True` |
| `L1_grad_V_eps_vanishes_at_q0_for_every_eps` | `True` |
| `L1_operator_dictionary_maps_O06_to_N_H` | `True` |
| `L2_D4_inside_H_block` | `True` |
| `L2_H0_PSD_exact` | `True` |
| `L2_H0_kernel_is_span_T35_plus_D4` | `True` |
| `L2_T35_vanishes_on_H_block` | `True` |
| `L2_consistency_raised_eps_r0sq_over_100_inertia_451_35_0_kernel_T35` | `True` |
| `L2_consistency_tiny_eps_r0sq_over_10e6_inertia_451_35_0_kernel_T35` | `True` |
| `L2_dim_ker_H0_cap_ker_hess_N_H_equals_35` | `True` |
| `L2_hess_N_H_annihilates_T35_and_doubles_D4` | `True` |
| `L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0` | `True` |
| `L2_raised_minus_benchmark_equals_eps_hess_N_H_exact` | `True` |
| `L2_rank_T35_35_rank_D4_4_rank_T35_plus_D4_39` | `True` |
| `L2_tiny_minus_benchmark_equals_eps_hess_N_H_exact` | `True` |
| `diagnostic_float64_compiler_O06_row_at_q0_is_chart_P_H_bitwise` | `True` |
| `doublet_H_block_curvatures_are_0_r0sq_1_and_1_plus_r0sq_as_stated` | `True` |
| `doublet_H_block_decouples_from_the_rest_at_q0` | `True` |
| `doublet_H_block_diagonal_Re_H6_9_curvature_0_others_positive` | `True` |
| `doublet_Re_H6_9_exact_eigenvectors_with_eigenvalue_eps_at_raised_and_tiny` | `True` |
| `doublet_eps_is_smallest_nonzero_eigenvalue_multiplicity_4_at_raised_and_tiny` | `True` |
| `doublet_rest_block_has_no_eigenvalue_in_open_interval_0_to_r0sq_over_96` | `True` |

## Checks

| check | passed |
|---|---|
| `candidate_recorded_float64_claims_present_and_consistent` | `True` |
| `coefficients_O06_equals_2_abs_kappa_r0` | `True` |
| `coefficients_O12_equals_kappa` | `True` |
| `coefficients_O44_coefficients_equal_one_eighth_A_plus_C` | `True` |
| `coefficients_O46_coefficients_equal_wedge_weights` | `True` |
| `coefficients_O48_coefficients_equal_exact_210_J_couplings` | `True` |
| `coefficients_benchmark_has_27_parameters` | `True` |
| `every_benchmark_parameter_in_exactly_one_unit` | `True` |
| `every_unit_matches_its_compiler_rows` | `True` |
| `exact_PSD` | `True` |
| `exact_gradient_vanishes` | `True` |
| `exact_hessian_annihilates_35_symmetry_tangents` | `True` |
| `exact_hessian_annihilates_4_doublet_directions` | `True` |
| `exact_hessian_symmetric` | `True` |
| `exact_nullity_39` | `True` |
| `exact_rank_447` | `True` |
| `kernel_equals_symmetry_tangents_plus_light_doublet` | `True` |
| `live_compiler_hessian_matches_exact_to_1e_minus_12` | `True` |
| `live_compiler_hessian_rounds_to_exact_lattice` | `True` |
| `live_numerical_inertia_0_39_447` | `True` |
| `live_symmetry_matrix_inside_exact_tangent_span` | `True` |
| `raised_O06_exact_PSD` | `True` |
| `raised_O06_exact_gradient_vanishes` | `True` |
| `raised_O06_exact_hessian_symmetric` | `True` |
| `raised_O06_exact_rank_451_nullity_35` | `True` |
| `raised_O06_kernel_equals_symmetry_tangents` | `True` |
| `raised_O06_smallest_nonzero_eigenvalue_is_the_lift_exact` | `True` |
| `raised_O06_strictly_positive_on_kernel_complement` | `True` |
| `raised_live_compiler_hessian_matches_exact_to_1e_minus_12` | `True` |
| `raised_live_compiler_hessian_rounds_to_exact_lattice` | `True` |
| `smallest_nonzero_eigenvalue_is_r0_squared_over_96_exact` | `True` |
| `strictly_positive_on_kernel_complement` | `True` |
| `tangent_matrix_matches_equality_module_ranks_33_34_35` | `True` |
| `tangent_plus_doublet_rank_39_exact` | `True` |
| `tangent_rank_35_exact` | `True` |
| `upstream_A_square_recoupling_exact` | `True` |
| `upstream_C_p_sigma_std_vanishes` | `True` |
| `upstream_C_square_recoupling_exact` | `True` |
| `upstream_J_at_p_equals_equality_module_values` | `True` |
| `upstream_M_p_sigma_std_equals_2_sigma_std` | `True` |
| `upstream_O48_order_is_J0_J2_J3_J4` | `True` |
| `upstream_Q_H_integer_equals_diag_1x6_0x4` | `True` |
| `upstream_cubic_operator_exactly_hermitian` | `True` |
| `upstream_phi_generators_equal_projector_source` | `True` |
| `upstream_phi_pair_casimir_symmetric` | `True` |
| `upstream_phi_quartic_background_and_response_symmetric` | `True` |
| `upstream_sigma_generators_exact_and_antihermitian` | `True` |
| `upstream_sigma_gram_matrices_hermitian` | `True` |
| `upstream_sigma_pair_casimir_self_adjoint` | `True` |
| `upstream_sigma_std_pair_is_pure_2772bar` | `True` |
| `upstream_sigma_std_raw_norm_squared_16` | `True` |
| `upstream_wedge_identity_exact` | `True` |

## Scope

**exact_premises_reused**

- A-square and C-square recouplings (exact_gauged_u1x_g3_a_square_recoupling_v20, exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_mixed_certificate)
- ||H wedge Phi||^2 = (3/5) I_1 - I_54 (exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_wedge_certificate)
- the compiler operators O07, O48, O14, O05, O27, O06, O12, O36, O04, O23, O03, O20 are the stated polynomials in the stated normalisation (the source modules' definitions)
- the symmetry tangent matrix and its ranks 33/34/35 (g3_sm_pati_salam_equality_set_v20)
- eps_family L1 only: the equality-set theorem V >= V0, {V = V0} = G.q0 with H = 0 there (committed G3_SM_PATI_SALAM_EQUALITY_SET_V20.json, proved status required; cited classical theorems and hand-argued steps, decision D6)

**float64_evidence_only**

- compiler = exact operators end to end: every binding unit, the assembled Hessian (<= 1e-12 in M_GUT^2) and the exact-lattice rounding are float64 comparisons with the live compiler

**not_proved_or_out_of_scope**

- strict positivity on the symmetry quotient at the tuned benchmark (the repository's strict_quotient_positive / kernel = symmetry tangents, as in the chiral-H 448/38 certificate): it is exactly FALSE here (kernel 35 + 4); the eps > 0 members (O06 = 2|kappa| r0 + eps, the raised variant eps = r0^2/100 among them) have kernel = orbit and strict quotient positivity, the tuned eps = 0 limit does not
- electroweak symmetry breaking on the eps family: H = 0 and the tree-level doublet mass^2 is eps >= 0
- other r0, x0 or kappa: the unit functions accept them, but only the benchmark is certified and bound
- G3 closure by this report alone: G3 is decided only by final_g3_acceptance_gate_v20 through its sm_pati_salam track (g3_sm_target_track_v20), which reads this report; the global minimality and the equality set are the candidate's and the equality module's results, not re-proved here
- the candidate's physics caveats (tuned doublet-triplet splitting and O06, sub-M_I coloured remnants, RG content, Higgs quartic, no electroweak breaking or Yukawa sector)

**proved_exactly**

- grad V(q0) = 0 and the complete 486 x 486 Hessian at the benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0): PSD, rank 447, nullity 39, kernel = 35 G-orbit tangents (+) 4 real light-doublet directions, positive definite on the 447-dimensional pivot complement, smallest nonzero eigenvalue r0^2/96 (multiplicity 14); hence NOT strictly positive on the 451-dimensional symmetry quotient (4 exact zero directions Re H_6..9 that are not symmetry directions)
- the O06 + r0^2/100 variant: PSD, rank 451, nullity 35, kernel = the 35 G-orbit tangents, positive definite on the pivot complement, smallest nonzero eigenvalue r0^2/100 (the lifted doublet)
- the eps family O06 = 2|kappa| r0 + eps (eps_family): L2, for every eps > 0 the Hessian at q0 is PSD with kernel exactly the 35 G-orbit tangents (rank 451, strictly positive on the 451-dimensional symmetry quotient; inertia 451/35/0 re-certified at eps = r0^2/100 and r0^2/10^6), and Re H_6..9 have mass^2 exactly eps (the lightest level, multiplicity 4, for 0 < eps < r0^2/96); L1, {V_eps = V0} = G.q0 for every eps >= 0, given the equality-set theorem
- all entries derived from integer / Gaussian-integer source tensors with Fraction scalars in the radical-free coordinates u (q = D u); Sylvester's law carries rank, nullity, signature and the eigenvalue counts to the chart

## Candidate float64 claims decided here

Source: G3_SM_PATI_SALAM_CANDIDATE_V20.json compiler['1/5'] (float64 claims of g3_sm_pati_salam_candidate_v20); all present and consistent: `True`.

Runtime: 59 s.
