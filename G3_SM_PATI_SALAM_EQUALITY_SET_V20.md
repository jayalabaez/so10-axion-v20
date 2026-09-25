# G3 SM Pati-Salam equality set -- v20

**Status:** `SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN`

**Theorem claimed:** `True`

For every r0 > 0, x0 > 0 and real kappa with kappa^2 < 8 r0^2, the SM Pati-Salam benchmark potential V of g3_sm_pati_salam_candidate_v20 on the canonical 486-real chart (the 27-parameter family, 25 nonzero parameters at kappa = 0; V is the candidate's adapted SOS form, which equals the compiler potential exactly coefficient by coefficient and for each source-bound operator, and in float64 end to end) satisfies V >= V0 = -1 - r0^4/8 - r0^4 - x0^4/32 and {V = V0} = G.(p, r0 sigma_std, 0, r0, x0) = {(Phi, Sigma, 0, S, Phi17) : (Phi, Sigma) in SO(10).(p, r0 sigma_std), |S| = r0, |Phi17| = x0}, G = SO(10) x U(1)_X x U(1)_PQ, p = e6789, sigma_std = z1^z2^z3^z4^z5.  The global minimum is unique modulo G; the orbit has tangent dimension 35 at the vacuum.  Here U(1)_PQ is the contract's accidental global symmetry (all 27 operators are PQ-neutral); modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (tangent rank 34 < 35; Phi17^4 conj(S)^17 has PQ charge -68), the axion direction.  Classical theorems are cited as listed in cited_theorems.  Corollary: the 210-only potential -2 v^2 |Phi|^2 + Q(Phi) has global-minimum set exactly SO(10).(v p).

Exact: for every r0 > 0, x0 > 0 and kappa^2 < 8 r0^2 the equality set {V = V0} of the SM Pati-Salam benchmark potential (27 parameters, 25 nonzero at kappa = 0; V is the candidate's adapted SOS form, which equals the compiler potential exactly coefficient by coefficient and for each source-bound operator, and in float64 end to end) is the single orbit G.(p, r0 sigma_std, 0, r0, x0), G = SO(10) x U(1)_X x U(1)_PQ, so its global minimum is unique modulo G, and the 210-only Pati-Salam vacuum orbit of exact_210 is unique.  Caveat: U(1)_PQ is the contract's accidental global symmetry (all 27 operators are PQ-neutral); modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (tangent rank 34 < 35; Phi17^4 conj(S)^17 has PQ charge -68), the axion direction, so the flag must not be read as uniqueness modulo the gauge group SO(10) x U(1)_X.  The proof combines exact integer/rational certificates (projector completeness, chart 210 action = natural Lambda^4 action, SO(10)-equivariance of the Pluecker interior and wedge tensors, invariant-theory identities for the 210, the Sym^2(126bar) channel structure, equivariance, the omega^2 and Wirtinger-Pfaffian identities, u(5) line stabiliser, charges, symbolic H/S square completion) with cited classical theorems (Pluecker relations, Kostant/Lichtenstein quadrics, Iwasawa, Wirtinger equality case, U(5) transitivity, highest-weight generation and Weyl dimension formula (Humphreys)) and elementary steps argued in the text (not machine-checked): Cauchy-Schwarz |H.H| <= N_H and the H/S sign argument, the Gram-Schmidt orbit step, integration of the Lie-algebra identities over connected SO(10) and U(5), the Iwasawa N and A action on sigma_std, and the corollary's rescaling (scope.elementary_not_machine_checked).  G3 stays open: the candidate is not wired into the gate and its physics caveats are unchanged.

Checks: 45/45 passed.

| check | passed |
|---|---|
| `NUM_float64_corroboration_finds_no_contradiction` | `True` |
| `P0_candidate_exact_certificate_passes` | `True` |
| `P0_coefficient_map_equals_SOS_expansion_for_kappa_negative_positive_zero` | `True` |
| `P0_eight_terms_expand_to_the_candidate_operator_map_with_constant_minus_V0` | `True` |
| `P0_generators_are_so10_representations` | `True` |
| `P0_pair_casimirs_commute_with_so10` | `True` |
| `P0_self_weights_at_least_one` | `True` |
| `P0_sym2_126bar_projectors_orthogonal_and_complete` | `True` |
| `P0_sym2_210_projectors_orthogonal_and_complete` | `True` |
| `P1_J0_J2_J3_J4_independent_at_declared_fit_points` | `True` |
| `P1_Q_equals_J0_plus_I45_I210_I5940` | `True` |
| `P1_channel_norms_in_J_basis_exact_and_match_repository` | `True` |
| `P1_channel_norms_sum_to_J0` | `True` |
| `P1_chart_210_action_is_natural_on_Lambda4` | `True` |
| `P1_crossing_identities_exact_validated_and_match_repository` | `True` |
| `P1_equality_set_J_vector_equals_J_at_p` | `True` |
| `P1_equality_system_square_4x4_and_nonsingular` | `True` |
| `P1_moments_int64_overflow_bound_holds` | `True` |
| `P1_p_has_unit_norm_and_zero_extra_channels` | `True` |
| `P1_pluecker_defect_detects_decomposability` | `True` |
| `P1_pluecker_defect_exact_J_combination_validated` | `True` |
| `P1_pluecker_defect_vanishes_on_equality_set` | `True` |
| `P1_pluecker_tensors_intertwine_natural_actions` | `True` |
| `P1_stabilizer_of_p_is_so6_plus_so4` | `True` |
| `P1_sym4_210_has_exactly_4_invariants` | `True` |
| `P2_2772bar_channel_equals_V_2lambda` | `True` |
| `P2_M_and_C_exactly_equivariant_and_M_hermitian` | `True` |
| `P2_chart_126bar_is_irreducible_V_lambda` | `True` |
| `P2_coefficient_map_uses_these_self_weights` | `True` |
| `P2_flipped_competitor_is_on_the_orbit` | `True` |
| `P2_phase_generator_L01_in_stab_p` | `True` |
| `P2_self_weights_force_sigma_purity` | `True` |
| `P2_sigma_M_sigma_is_2_norm2_omega2_over_2` | `True` |
| `P2_sigma_std_pure_2772bar_and_vacuum_squares_vanish` | `True` |
| `P2_u5_stabilises_the_line_of_sigma_std` | `True` |
| `P2_wirtinger_pfaffian_identity` | `True` |
| `P3_HS_domain_holds_strictly_at_sample_points` | `True` |
| `P3_HS_square_completion_identities_exact_symbolic` | `True` |
| `P3_S_Phi17_charge_matrix_nonsingular` | `True` |
| `P3_V_phase_independent_at_H0` | `True` |
| `P3_all_27_operators_X_and_PQ_neutral` | `True` |
| `P3_charges_consistent_across_sources` | `True` |
| `P3_explicit_group_element_reaches_all_phases` | `True` |
| `P3_operator_count_27_and_25_at_kappa_0` | `True` |
| `P3_orbit_tangent_rank_35_kernel_12_pure_so10` | `True` |

## P0 -- the squares are squares

- V - V0 is the sum of eight terms, each >= 0: (|Phi|^2-1)^2 + I45 + I210 + I5940; (1/8)||(M_Phi-2)Sigma||^2; (1/8)||C_Phi Sigma||^2; (1/8)(W' - N^2) = (1/8) sum_q (w_q - 1) I_q; (1/8)(N_Sigma - r0^2)^2; V_HS + r0^4; ||H wedge Phi||^2; (1/32)(|Phi17|^2 - x0^2)^2
- Sym^2(210): K symmetric, product over nodes [-4, 0, 2, 6, 12, 14, 16, 24] vanishes on 22155 columns: `True`
- Sym^2(126bar): K Hermitian, (K-15)(K-7)(K-1)(K+5) = 0 on 8001 columns: `True`; channel dimensions `{'1050bar': '1050', '2772bar': '2772', '4125': '4125', '54': '54'}`
- eight terms expand to the candidate's operator map, constant -V0 (kappa < 0, > 0, = 0): `True`; operators compared `[27, 27, 25]`

## P1 -- Phi

- chart 210 action = natural Lambda^4 action (all 45 generators, exact): `True`
- interior and wedge tensors intertwine the natural Lambda^1, Lambda^3, Lambda^4, Lambda^5 actions (45 generators, exact), Lambda^3 and Lambda^5 actions antisymmetric, so D is SO(10)-invariant: `True`
- dim Sym^4(210)^SO(10) = `4`; J-basis determinant at the declared fit points ['random_sparse_0', 'random_sparse_1', 'random_sparse_2', 'random_sparse_3'] `-310727853917798400`
- (J0, I45, I210, I5940) determinant `-1/258048000`; equality-set J vector `['1', '24', '192', '3552']` = J(p) `['1', '24', '192', '3552']`
- Pluecker defect D = `['-42/5', '33/40', '-7/40', '1/160']` . (J0, J2, J3, J4) = `['0', '-20', '18', '8']` . (J0, I45, I210, I5940); validated at 20 further exact points
- D at named forms: `{'(e0+e4)^(e1+e5)^e2^e3 (decomposable)': 0, '(e01+e23+e45)^(e67+e89)': 84, 'e0123 + e0145 + e2345': 12, 'e0123 + e4567': 8, 'e01^(e23+e45)': 4, 'p = e6789': 0}`

## P2 -- Sigma

1. Sigma (x) Sigma in V(2 lambda), Sigma != 0 (N = r0^2)  =>  Sigma in G_C.sigma_std  [Kostant/Lichtenstein]
2. G_C = K A N, N sigma_std = sigma_std, A sigma_std in R_{>0} sigma_std  =>  Sigma = r0 g sigma_std, g in SO(10)  [Iwasawa]
3. (M_p - 2) g sigma_std = 0  =>  (M_{p'} - 2) sigma_std = 0, p' = g^-1 p  [exact equivariance]
4. <sigma, M_{p'} sigma> = 2|sigma|^2 <p', omega^2/2>  =>  <p', omega^2/2> = 1  [exact identity]
5. Wirtinger equality  =>  p' is a J0-complex 2-plane with complex orientation  [Federer 1.8.2]
6. U(5) transitive on those planes, <p, omega^2/2> = 1  =>  p' = u p, u in U(5)
7. u^-1 sigma_std = e^{i theta} sigma_std (u(5) stabilises the line, exact)  =>  Sigma = r0 (g u exp(theta L01)) sigma_std, g u exp(theta L01) in Stab(p)

- Weyl dimensions: V(lambda) `126`, V(2 lambda) `2772`
- W' - N^2 coefficients `{'1050bar': '1', '2772bar': '0', '4125': '1/16', '54': '1'}`
- <sigma, M_Phi sigma> = 32 <Phi, omega^2/2> (raw |sigma|^2 = 16); <p, omega^2/2> = 1
- centraliser of J0: dimension 25; line stabiliser dimension 25

## P3 -- H, S, Phi17, phases

- (S, Phi17) charge matrix (rows X, PQ) `[[4, 17], [4, 0]]`, det `-68`; explicit element `{'L01_angle': 'a/2', 'PQ_angle': 'a/4 - b/17', 'X_angle': 'b/17'}`
- tangent ranks so(10) / +X / +PQ: `33` / `34` / `35`; kernel `12`
- without PQ: `Phi17^4 conj(S)^17` has X charge `0` and PQ charge `-68`; the monomial is SO(10) x U(1)_X-invariant and has nonzero PQ charge; on {V = V0} it equals x0^4 r0^17 e^(i phase) with every phase attained (P3 explicit element), so modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (tangent rank 34 < 35), the axion direction; uniqueness modulo symmetry needs U(1)_PQ
- H/S for all (r0, kappa): Cauchy-Schwarz |H.H| <= N_H (elementary, not machine-checked) reduces V_HS + r0^4 to the reduced form; the square-completion identities are exact sympy identities in symbolic (N_H, |S|, |kappa|, r0); the sign argument in HS_bracket_algebra.argument (elementary, argued in the text) finishes the proof for every kappa^2 < 8 r0^2.  HS_points are rational sample points of the domain condition only.

## Equality conditions

- |Phi| = 1 and I_45 = I_210 = I_5940 = 0
- (M_Phi - 2) Sigma = 0
- C_Phi Sigma = 0
- I_54 = I_1050bar = I_4125 = 0, i.e. Sigma (x) Sigma in 2772bar = V(2 lambda)
- N_Sigma = r0^2
- H = 0 and |S| = r0
- H wedge Phi = 0 (implied by H = 0)
- |Phi17| = x0

## Cited classical theorems

- Pluecker relations: xi != 0 is decomposable iff (iota_alpha xi) ^ xi = 0 for all alpha -- P. Griffiths, J. Harris, Principles of Algebraic Geometry (Wiley, 1978), pp. 209-211 (P1)
- Kostant's quadrics, set-theoretic form: {v in V(lambda) : v (x) v in V(2 lambda)} = G_C.v_lambda u {0} -- W. Lichtenstein, Proc. Amer. Math. Soc. 84 (1982) 605-608 (P2(iv))
- Iwasawa decomposition G_C = K A N of the complex group SO(10,C) with K = SO(10) -- K. Iwasawa, Ann. of Math. 50 (1949) 507-558; A. W. Knapp, Lie Groups Beyond an Introduction, 2nd ed. (2002), Thm. 6.46 (P2(iv))
- Wirtinger inequality <xi, omega^p/p!> <= 1 for unit simple 2p-vectors, equality iff xi is a complex p-plane with its complex orientation -- H. Federer, Geometric Measure Theory (1969), 1.8.2; R. Harvey, H. B. Lawson, Acta Math. 148 (1982) 47-157 (P2(vii) (an elementary Pfaffian proof is also recorded))
- U(n) is transitive on Gr_C(k, n) and preserves complex orientations -- standard (extend a unitary basis of the k-plane) (P2(vii))
- a highest-weight vector of a finite-dimensional so(10,C)-module generates an irreducible submodule; Weyl dimension formula -- J. E. Humphreys, Introduction to Lie Algebras and Representation Theory, sections 20-21 and 24.3 (P2(i)-(ii))
- U(5)-invariant 4-forms on R^10 = C^5 are spanned by omega^2 -- classical (the (2,2)-part; Harvey-Lawson 1982) (NOT used: P2(vi) is verified directly on every basis 4-form)

## Numerical corroboration (float64, evidence only)

- V_Phi minimisations: 12/12 reach -1, all on SO(10).p: `True`
- pure elements of Eig_2(M_p) mapped onto sigma_std by a constructed h in SO(6)xSO(4): `True` (max overlap defect 1.11e-16)
- Wirtinger: random max 0.841, local maxima reach 1 on J0-invariant planes: `True`
- full-chart minimisations: gaps `['9.1e-14', '1.44e-13']`, on the vacuum orbit: `[True, True]`

## Scope

**cited_not_machine_checked**

- Pluecker relations: xi != 0 is decomposable iff (iota_alpha xi) ^ xi = 0 for all alpha
- Kostant's quadrics, set-theoretic form: {v in V(lambda) : v (x) v in V(2 lambda)} = G_C.v_lambda u {0}
- Iwasawa decomposition G_C = K A N of the complex group SO(10,C) with K = SO(10)
- Wirtinger inequality <xi, omega^p/p!> <= 1 for unit simple 2p-vectors, equality iff xi is a complex p-plane with its complex orientation
- U(n) is transitive on Gr_C(k, n) and preserves complex orientations
- a highest-weight vector of a finite-dimensional so(10,C)-module generates an irreducible submodule; Weyl dimension formula

**elementary_not_machine_checked**

- Cauchy-Schwarz |H.H| <= N_H (|sum_i H_i^2| <= sum_i |H_i|^2), used in P3 to reduce V_HS + r0^4 to the symbolically certified form
- the sign argument of HS_bracket_algebra.argument (cases |S| <= r0 and |S| > r0), which turns the exact sympy square-completion identities into V_HS + r0^4 >= 0 with equality iff H = 0 and |S| = r0 (P3)
- the Gram-Schmidt orbit step: a unit decomposable 4-vector equals u1^u2^u3^u4 with orthonormal u_i, and completing to a positively oriented orthonormal basis gives g in SO(10) with (Lambda^4 g) e6789 = Phi (P1)
- integrating the exact Lie-algebra identities over the connected groups: over SO(10), the invariance of D (from the checked intertwining identities, D' = 2 tr(T^T X5 T) - 2 tr(T^T T X3) = 0; P1) and the equivariance of M_Phi and C_Phi (P2(v)); over U(5), the u(5) line stabilisation of sigma_std (P2(viii))
- N sigma_std = sigma_std and A sigma_std in R_{>0} sigma_std for the Iwasawa factors N and A, from the checked weight (1,1,1,1,1) and positive-root data (P2(iv))
- the corollary's reduction: V_v = (|Phi|^2 - v^2)^2 - v^4 + I_45 + I_210 + I_5940 (from the checked Q = J0 + I_45 + I_210 + I_5940) and the rescaling Phi -> Phi/v

**float64_evidence_only**

- numerical_corroboration (V_Phi minimisations, pure elements of Eig_2(M_p), Wirtinger sampling, full-chart minimisations)
- end-to-end compiler = SOS form (the candidate's fast-evaluator validation)

**not_proved_or_out_of_scope**

- uniqueness modulo SO(10) x U(1)_X alone: false.  Uniqueness uses U(1)_PQ, an accidental symmetry of this benchmark (all 27 operators PQ-neutral); modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (rank 34 < 35), labelled by the phase of Phi17^4 conj(S)^17 (the axion direction)
- kappa^2 = 8 r0^2 (the H/S equality set is unchanged there, but the domain is kappa^2 < 8 r0^2)
- potentials outside the candidate's 27-parameter family
- G3 closure: the candidate is not wired into the G3 gate
- the candidate's model-level caveats: tuned doublet-triplet splitting and O05 cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs quartic, no electroweak breaking, no realistic Yukawa sector

**proved_exactly**

- {V = V0} = G.vacuum, G = SO(10) x U(1)_X x U(1)_PQ, for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2 (V is the candidate's adapted SOS form, which equals the compiler potential exactly coefficient by coefficient and for each source-bound operator, and in float64 end to end; cited classical theorems as listed; elementary steps argued in the text (not machine-checked): Cauchy-Schwarz |H.H| <= N_H and the H/S sign argument, the Gram-Schmidt orbit step, integration of the Lie-algebra identities over connected SO(10) and U(5), the Iwasawa N and A action on sigma_std, and the corollary's rescaling (scope.elementary_not_machine_checked))
- the chart 210 action is the natural Lambda^4 action (exact, all 45 generators)
- the integer interior (Lambda^3 x Lambda^4 -> Lambda^1) and wedge (Lambda^1 x Lambda^4 -> Lambda^5) tensors intertwine the natural actions of all 45 generators, and the Lambda^3, Lambda^5 actions are antisymmetric (exact), so the Pluecker defect is SO(10)-invariant
- the eight SOS terms expand to the candidate's coefficient map operator by operator, constant -V0 (sympy, kappa < 0, > 0, = 0)
- the Lagrange projectors on Sym^2(210) and Sym^2(126bar) are orthogonal and complete (minimal polynomials)
- every SO(10)-invariant quartic of the 210 is constant on {|Phi| = 1, I45 = I210 = I5940 = 0}; the Pluecker defect is -20 I45 + 18 I210 + 8 I5940
- 2772bar = V(2 lambda) (exact traces and Weyl dimensions); sigma_std is its highest-weight generator
- <sigma, M_Phi sigma> = 2|sigma|^2 <Phi, omega^2/2> and the Wirtinger-Pfaffian identity (all basis 4-forms)
- u(5) = line stabiliser of sigma_std; L01 in Stab(p) rotates its phase
- charge matrix det -68, X/PQ neutrality of all 27 operators, tangent rank 35 with 12-dim pure-so(10) kernel
- corollary: exact_210 Pati-Salam global orbit is unique
