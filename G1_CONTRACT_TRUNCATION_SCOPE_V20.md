# G1 contract-truncation scope: 26 allowed, 10 declared, 16 undeclared fermion bilinears (v20, status-neutral)

- Status: `G1_CONTRACT_TRUNCATION_SCOPE__26_ALLOWED_10_DECLARED_16_UNDECLARED__EXACT__NO_GATE_CHANGE`
- Overall state: `DECLARED_CONTRACT_IS_A_SYMMETRY_UNPROTECTED_TRUNCATION_EXACT__RADIATIVE_GENERATION_ARGUED_NOT_COMPUTED`
- Checks: 37/37 pass (expected 37)
- No gate status changes: G1 stays CLOSED and is scoped as the attestation of a truncation; no coupling is added.

## Verdict

EXACT (37 checks): the SARAH-attested contract is a truncation. SO(10) x U(1)_X x Z17 (Z17 = X mod 17 for every field) allows 26 renormalizable fermion bilinears; 10 are declared and 16 are not (Delta126bar.F.P, Delta126bar.F.R, Delta126bar.P.P, Delta126bar.P.R, Delta126bar.R.R, H10.P.P, H10.P.R, H10.R.R, Phi17.F.Rbar, Phi17.P.Rbar, conj[Delta126bar].Pbar.Rbar, conj[H10].Pbar.Rbar, conj[Phi17].F.Pbar, conj[Phi17].R.Pbar, conj[S].P.Qbar, conj[S].R.Qbar; labels in the model file's field basis). The truncation is not a basis choice: the undeclared couplings span 48 real generation-expanded dimensions, more than the 25 of U(5) on the five X = 1 sixteens, the only field-redefinition factor that mixes distinct multiplets. The declared terms and the full allowed set (with the scalar links) have the same 3-dimensional U(1) kernel span{X, PQ, Nspec}; every omitted coupling is PQ neutral and an integer combination of declared terms, so no U(1) and no multiplet-diagonal phase symmetry of the declared Lagrangian protects it; F, P and R carry identical charges. Each omitted coupling involves P, R, Pbar, Rbar or Qbar; Phi17.F.Rbar and conj[Phi17].F.Pbar are F-Rbar and F-Pbar mass mixings. Radiative generation is argued, not computed. The G8 dimension-4 analysis already includes all 26 couplings. Status-neutral: G1 stays CLOSED as the attestation of a truncation; no coupling is added.

## Labels

- ARGUMENT: reasoning recorded with its premises; not computed here.
- BOUND: read fail-closed from a committed certificate JSON or recomputed through a committed module; any read error, missing key or mismatch makes the check False.
- EXACT: integer / fractions.Fraction arithmetic on the parsed model file and the repository PQ table (no floats).

## Model file [EXACT]

- File: `models/SO10Z17AxionV20.m` (sha256 of the LF-normalised text `08373718806a297b9b257d5320d22e03e69f0682ea7488f146a105659182c325`).

| field | kind | SO(10) | X | Z17 | generations | real | PQ | N17 | Nspec |
|---|---|---|---|---|---|---|---|---|---|
| Phi210 | scalar | 210 | 0 | 0 | 1 | True | 0 | 0 | 0 |
| Delta126bar | scalar | -126 | -2 | 15 | 1 | False | -2 | 0 | 0 |
| H10 | scalar | 10 | -2 | 15 | 1 | False | -2 | 0 | 0 |
| S | scalar | 1 | 4 | 4 | 1 | False | 4 | 0 | 0 |
| Phi17 | scalar | 1 | 17 | 0 | 1 | False | 0 | 1 | 0 |
| F | fermion | 16 | 1 | 1 | 3 | False | 1 | 0 | 0 |
| P | fermion | 16 | 1 | 1 | 1 | False | 1 | 0 | 0 |
| R | fermion | 16 | 1 | 1 | 1 | False | 1 | 0 | 0 |
| SpecS | fermion | 16 | 2 | 2 | 5 | False | 2 | 0 | 1 |
| SpecB | fermion | -16 | -6 | 11 | 5 | False | -6 | 0 | -1 |
| Q | fermion | 16 | 14 | 14 | 1 | False | -3 | 1 | 0 |
| Pbar | fermion | -16 | 16 | 16 | 1 | False | -1 | 1 | 0 |
| Qbar | fermion | -16 | 3 | 3 | 1 | False | 3 | 0 | 0 |
| Rbar | fermion | -16 | -18 | 16 | 1 | False | -1 | -1 | 0 |

| LagHC coefficient | monomial | kind | X sum | Z17 sum mod 17 |
|---|---|---|---|---|
| Y10 | `F.F.H10` | fermion_bilinear | 0 | 0 |
| Y126 | `F.F.Delta126bar` | fermion_bilinear | 0 | 0 |
| yP | `conj[Phi17].P.Pbar` | fermion_bilinear | 0 | 0 |
| yQ | `conj[Phi17].Q.Qbar` | fermion_bilinear | 0 | 0 |
| yR | `Phi17.R.Rbar` | fermion_bilinear | 0 | 0 |
| ys | `S.SpecS.SpecB` | fermion_bilinear | 0 | 0 |
| lambdaP | `P.F.H10` | fermion_bilinear | 0 | 0 |
| lambdaR | `R.F.H10` | fermion_bilinear | 0 | 0 |
| lambdaQB | `conj[S].Qbar.F` | fermion_bilinear | 0 | 0 |
| lambdaQR | `S.Q.Rbar` | fermion_bilinear | 0 | 0 |
| kappaH | `H10.H10.S` | scalar_link | 0 | 0 |

- LagNoHC terms (all X and Z17 neutral): `m210Sq/2 Phi210.Phi210`, `m126Sq conj[Delta126bar].Delta126bar`, `m10Sq conj[H10].H10`, `mSSq conj[S].S`, `m17Sq conj[Phi17].Phi17`, `lambdaS/2 conj[S].S.conj[S].S`, `lambda17/2 conj[Phi17].Phi17.conj[Phi17].Phi17`, `lambdaS17 conj[S].S.conj[Phi17].Phi17`.

## Z17 [EXACT]

- Z17 = X mod 17 for every contract field, so every X-neutral monomial is Z17-neutral: the residual Z17 adds no condition to the census or the kernels.
- X-allowed couplings removed by Z17: none.

## Census [EXACT]

- Method: combinations_with_replacement of the 9 fermion multiplets (model-file order) x every scalar option (each scalar and its conjugate; Phi210 is real); SO(10) singlet test from 16x16 = 10 + 120 + 126, 16x16bar = 1 + 45 + 210, 16bar x 16bar = 10 + 120 + 126bar; U(1)_X and Z17 neutrality; a coupling is declared when a LagHC fermion bilinear has the same multiset of fields.
- Allowed 26, declared 10, undeclared 16; generation-expanded 74; bare 16.16bar masses: none; Phi210 couplings: none.
- Undeclared by bilinear class: 16.16: 8, 16.16bar: 6, 16bar.16bar: 2.
- Field redefinitions: declared 100 and undeclared 48 real generation-expanded dimensions; mixing classes F/P/R (U(5), 25 real); declared-orbit bound 125 < 148.
- The 16-label list refers to the model file's field basis: F, P and R are charge-degenerate, so a U(5) rotation of the five X = 1 sixteens (F x3, P, R) can move couplings between declared and undeclared labels. The truncation is basis independent: the undeclared couplings span 24 complex = 48 real generation-expanded dimensions, while the only gauge-covariant (SO(10) x U(1)_X), linear, kinetic-term-preserving field-redefinition factor that mixes distinct multiplets is that U(5) (25 real dimensions); every other factor rotates the generations of a single multiplet or rephases it and maps the declared coupling space to itself. The orbit of the declared couplings (100 real dimensions) under all field redefinitions therefore has real dimension at most 100 + 25 = 125 < 148, the real dimension of all 26 couplings, so a generic Lagrangian with all 26 couplings is not field-redefinition-equivalent to a declared one.
- Method: fields grouped by (kind, SO(10) representation, X); complex scalars also with the conjugate of a field of the conjugate quantum numbers; a class with n generations in total has the redefinition group U(n) (O(n) for real scalars); a class is mixing when it contains two or more distinct multiplets; generation-expanded coupling counts as in the census (g(g+1)/2 for a repeated multiplet, g1 g2 otherwise), one complex coefficient each.

| coupling | scalar rep | class | declared | coefficient | PQ sum | N17 sum |
|---|---|---|---|---|---|---|
| `Delta126bar.F.F` | -126 | 16.16 | True | Y126 | 0 | 0 |
| `H10.F.F` | 10 | 16.16 | True | Y10 | 0 | 0 |
| `Delta126bar.F.P` | -126 | 16.16 | False | - | 0 | 0 |
| `H10.F.P` | 10 | 16.16 | True | lambdaP | 0 | 0 |
| `Delta126bar.F.R` | -126 | 16.16 | False | - | 0 | 0 |
| `H10.F.R` | 10 | 16.16 | True | lambdaR | 0 | 0 |
| `conj[Phi17].F.Pbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `conj[S].F.Qbar` | 1 | 16.16bar | True | lambdaQB | 0 | 0 |
| `Phi17.F.Rbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `Delta126bar.P.P` | -126 | 16.16 | False | - | 0 | 0 |
| `H10.P.P` | 10 | 16.16 | False | - | 0 | 0 |
| `Delta126bar.P.R` | -126 | 16.16 | False | - | 0 | 0 |
| `H10.P.R` | 10 | 16.16 | False | - | 0 | 0 |
| `conj[Phi17].P.Pbar` | 1 | 16.16bar | True | yP | 0 | 0 |
| `conj[S].P.Qbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `Phi17.P.Rbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `Delta126bar.R.R` | -126 | 16.16 | False | - | 0 | 0 |
| `H10.R.R` | 10 | 16.16 | False | - | 0 | 0 |
| `conj[Phi17].R.Pbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `conj[S].R.Qbar` | 1 | 16.16bar | False | - | 0 | 0 |
| `Phi17.R.Rbar` | 1 | 16.16bar | True | yR | 0 | 0 |
| `S.SpecS.SpecB` | 1 | 16.16bar | True | ys | 0 | 0 |
| `conj[Phi17].Q.Qbar` | 1 | 16.16bar | True | yQ | 0 | 0 |
| `S.Q.Rbar` | 1 | 16.16bar | True | lambdaQR | 0 | 0 |
| `conj[Delta126bar].Pbar.Rbar` | 126 | 16bar.16bar | False | - | 0 | 0 |
| `conj[H10].Pbar.Rbar` | 10 | 16bar.16bar | False | - | 0 | 0 |

## U(1) kernels [EXACT]

- Unknowns: Phi210, Delta126bar, H10, S, Phi17, F, P, R, SpecS, SpecB, Q, Pbar, Qbar, Rbar.
- Phi210 is a real field, so no U(1) acts on it: the row e_Phi210 is added to every system.
- charges are per multiplet (all generations of F, SpecS and SpecB share one charge); generation-wise phases are covered by the lattice section (with generic flavour matrices every generation-wise phase symmetry is multiplet-diagonal).

| system | kernel dimension | equals span{X, PQ, Nspec} |
|---|---|---|
| declared_LagHC | 3 | True |
| declared_LagHC_plus_G1_scalar_links | 3 | True |
| allowed_26_plus_kappaH | 3 | True |
| allowed_26_plus_kappaH_plus_G1_scalar_links | 3 | True |
| allowed_26_without_scalar_links | 4 | - (S charge free) |

- Scalar links: kappaH = +2H10 +S; 20 nontrivial G1 census links.
- F, P, R identical under every kernel element: True.
- The U(1) kernel of the 11 declared LagHC terms, with or without the G1 scalar links, and of all 26 allowed couplings plus kappaH (with or without the G1 scalar links) is the same 3-dimensional span of X, PQ and spectator number (X = PQ + 17 N17); without any scalar link the 26 couplings leave S's charge free (dimension 4). Every undeclared coupling is therefore neutral under every U(1) of the declared Lagrangian, and F, P and R carry identical charges.

## PQ and anomaly [EXACT]

- Source: exact_x_symmetry_consistency_gate_v20.EXPECTED_SCALAR_CHARGES and EXPECTED_FERMION_SECTORS ((PQ, X) pairs; fermion sectors keyed by SO(10) representation and X).
- All allowed couplings PQ neutral: True; all undeclared PQ neutral: True.
- Scalar monomials of degree <= 4: 715 count tuples, 55 X-neutral, PQ violations: none.
- Anomaly: T_16 = 2, N_X = 0, N_PQ = -34, N_spec = 0, N17 = 2 (mixed SO(10)^2 x U(1) coefficient N = sum over fermion multiplets of generations x T(16) x q with T(16) = T(16bar) = 2 (the colour index of a 16 in units T(3) = 1/2)).
- All 26 allowed couplings are PQ neutral and every X-neutral renormalizable scalar monomial is PQ neutral, so PQ is accidental at the renormalizable level and the truncation changes neither the PQ symmetry nor its anomaly N = -34.

## Integer lattice [EXACT]

- Method: rational particular solution c0 of sum_k c_k D_k = target (D_k the 11 LagHC charge vectors, Fraction RREF) plus integer multiples of the primitive relation r; L1(c0 + t r) is convex in t, every integer t between the extreme breakpoints -c_i/r_i is scanned and the minimal-L1 integral solution is kept (tied minima differ by multiples of the relation; the tie is broken by the lexicographically largest coefficient vector in LagHC order, i.e. the largest Y10 coefficient); every certificate is re-verified exactly at assembly.
- Declared order: Y10, Y126, yP, yQ, yR, ys, lambdaP, lambdaR, lambdaQB, lambdaQR, kappaH; rank 10; relation Y10: 1, yQ: 1, yR: 1, lambdaR: -1, lambdaQB: -1, lambdaQR: -1 (sum = 0).
- Every scan covers its breakpoints: True; tied minimal-L1 solutions (resolved by the stated tie-break): Phi17.F.Rbar: 2, conj[Delta126bar].Pbar.Rbar: 2, conj[H10].Pbar.Rbar: 2, conj[S].R.Qbar: 2.

| target | certificate (coefficient: multiplicity) | L1 |
|---|---|---|
| `Delta126bar.F.P` | Y10: -1, Y126: 1, lambdaP: 1 | 3 |
| `Delta126bar.F.R` | Y10: -1, Y126: 1, lambdaR: 1 | 3 |
| `Delta126bar.P.P` | Y10: -2, Y126: 1, lambdaP: 2 | 5 |
| `Delta126bar.P.R` | Y10: -2, Y126: 1, lambdaP: 1, lambdaR: 1 | 5 |
| `Delta126bar.R.R` | Y10: -2, Y126: 1, lambdaR: 2 | 5 |
| `H10.P.P` | Y10: -1, lambdaP: 2 | 3 |
| `H10.P.R` | Y10: -1, lambdaP: 1, lambdaR: 1 | 3 |
| `H10.R.R` | Y10: -1, lambdaR: 2 | 3 |
| `Phi17.F.Rbar` | Y10: 1, yR: 1, lambdaR: -1 | 3 |
| `Phi17.P.Rbar` | yR: 1, lambdaP: 1, lambdaR: -1 | 3 |
| `conj[Delta126bar].Pbar.Rbar` | Y10: 2, Y126: -1, yP: 1, yR: 1, lambdaP: -1, lambdaR: -1 | 7 |
| `conj[H10].Pbar.Rbar` | Y10: 1, yP: 1, yR: 1, lambdaP: -1, lambdaR: -1 | 5 |
| `conj[Phi17].F.Pbar` | Y10: 1, yP: 1, lambdaP: -1 | 3 |
| `conj[Phi17].R.Pbar` | yP: 1, lambdaP: -1, lambdaR: 1 | 3 |
| `conj[S].P.Qbar` | Y10: -1, lambdaP: 1, lambdaQB: 1 | 3 |
| `conj[S].R.Qbar` | yQ: 1, yR: 1, lambdaQR: -1 | 3 |
| P-F | Y10: -1, lambdaP: 1 | 2 |
| R-F | Y10: -1, lambdaR: 1 | 2 |

- Each undeclared coupling's charge vector is an integer combination of the 11 declared LagHC monomials (verified exactly), so every phase rotation of the 14 multiplets (continuous or discrete) that leaves the declared terms invariant also leaves the undeclared coupling invariant; with generic flavour matrices every generation-wise phase symmetry is multiplet-diagonal.
- Spurion note: the combination is the spurion monomial of declared couplings with the coupling's charges (a negative coefficient is a complex conjugate); its degree is a selection-rule order only, not a computed loop order.

## Vectorlike sector [EXACT, membership]

| undeclared coupling | vectorlike-sector fields | class | F-16bar mass mixing |
|---|---|---|---|
| `Delta126bar.F.P` | P | 16.16 | False |
| `Delta126bar.F.R` | R | 16.16 | False |
| `Delta126bar.P.P` | P | 16.16 | False |
| `Delta126bar.P.R` | P, R | 16.16 | False |
| `Delta126bar.R.R` | R | 16.16 | False |
| `H10.P.P` | P | 16.16 | False |
| `H10.P.R` | P, R | 16.16 | False |
| `H10.R.R` | R | 16.16 | False |
| `Phi17.F.Rbar` | Rbar | 16.16bar | True |
| `Phi17.P.Rbar` | P, Rbar | 16.16bar | False |
| `conj[Delta126bar].Pbar.Rbar` | Pbar, Rbar | 16bar.16bar | False |
| `conj[H10].Pbar.Rbar` | Pbar, Rbar | 16bar.16bar | False |
| `conj[Phi17].F.Pbar` | Pbar | 16.16bar | True |
| `conj[Phi17].R.Pbar` | R, Pbar | 16.16bar | False |
| `conj[S].P.Qbar` | P, Qbar | 16.16bar | False |
| `conj[S].R.Qbar` | R, Qbar | 16.16bar | False |

- Every undeclared coupling involves at least one of P, R, Pbar, Rbar, Qbar (the vectorlike sector), none involves Q, SpecS or SpecB, and exactly two (Phi17.F.Rbar, conj[Phi17].F.Pbar) are F-Rbar and F-Pbar mass mixings once Phi17 has its vev; mass-eigenstate composition is not computed here.

## Cross-checks [BOUND]

- Live G8 contract section (g8_sm_pati_salam_flavour_nogo_v20.contract_section): allowed_labels_match = True; computed = True; declared_flags_match = True; model_contract_id_matches = True; undeclared_match = True.
- G8 flavour no-go JSON: allowed_count_26 = True; dimension4.X1_sixteens_F_P_R = True; dimension4.light_state_lemma_uses_general_16_16_10H_coupling = True; dimension4.lists_equal_census.Delta126bar_yukawas = True; dimension4.lists_equal_census.H10_yukawas = True; dimension4.lists_equal_census.conj_H10_yukawas = True; dimension4.lists_equal_census.sixteenbar_pair_couplings = True; dimension4.lists_equal_census.vectorlike_mass_couplings = True; dimension4.undeclared_contained = True; dimension4.union_is_the_allowed_set = True; dimension4.vectorlike_rank_8_on_all_allowed_pairs = True; model_sha256_matches = True; report = G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json; status = G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN; status_and_zero_failed = True; undeclared_equals_census = True; undeclared_equals_expected = True.
- G8 structural-obstruction JSON: census_matches = True; field_level_couplings_equal_allowed_set = True; generation_expanded_74 = True; no_X_neutral_16bar_16_pair = True; report = G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json; status = G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION__SOS_CERTIFIED_FAMILY_FLAVOUR_DEAD__RECORDED__NO_GATE_CHANGE; status_and_zero_failed = True.
- G1 symmetry-census JSON: bound = True; every_multidegree_X_PQ_Z17_neutral = True; multidegrees_34 = True; nontrivial_links = 20; nontrivial_links_20 = True; report = G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json; status = EXACT_GAUGED_U1X_RENORMALIZABLE_MULTIPLICITY_CENSUS_COMPLETE__COMPILER_REAUDIT_OPEN; status_and_zero_failed = True.

## G8 dimension-4 coverage [BOUND]

- The committed G8 flavour analysis lists every allowed coupling (contract.H10_yukawas, Delta126bar_yukawas, vectorlike_mass_couplings, sixteenbar_pair_couplings include the 16 undeclared ones) and its light-state lemma uses the general 16.16.10_H coupling on the X = 1 sixteens, so at the dimension-4 level the truncation does not lift the G8 witness-branch flavour obstruction (its rank-8 light-state assumption carries over).

## Radiative stability [ARGUMENT, not computed]

- No U(1) and no multiplet-diagonal phase symmetry of the declared Lagrangian protects the 16 omitted couplings (EXACT, kernel and lattice sections), so by naturalness the truncation is not expected to be stable under renormalisation. This is an argument: radiative generation is not computed here.
- One-loop example: In the model file's field basis the one-loop Yukawa RGE contains (Y Y^dagger Y)_PP &#8835; lambda_P Y10^* lambda_P for the 16.16.10_H matrix Y on the X = 1 sixteens; this comes from the fermion wave-function (P-F kinetic-mixing) term and is basis dependent (the vertex term with a holomorphically coupled complex H10 cancels). SO(10) group factors are not computed.
- Not claimed: that any omitted coupling is generated at one loop with a nonzero coefficient; RG closure of the declared Lagrangian modulo field redefinitions; the loop order at which each omitted coupling first appears; the phenomenology of the omitted couplings.

## Scope

**argued_not_computed**
- radiative generation of the omitted couplings (radiative.statement)

**claimed**
- EXACT: census 26 allowed / 10 declared / 16 undeclared (74 generation-expanded), Z17 = X mod 17
- EXACT: dimension count: the undeclared couplings (48 real generation-expanded dimensions) exceed the mixing field redefinitions (U(5) on F x3, P, R: 25), so the truncation is not a basis choice (the 16-label list refers to the model file's field basis)
- EXACT: U(1) kernels (dimension 3 = span{X, PQ, Nspec}; 4 without scalar links) and F/P/R charge degeneracy
- EXACT: PQ neutrality of all 26 couplings, accidental PQ at the renormalizable level, N = -34
- EXACT: integer-lattice certificates for the 16 undeclared couplings and for P-F, R-F
- EXACT: vectorlike-sector membership and the two F-16bar mass mixings
- BOUND: equality with the committed G8 contract census and structural-obstruction census; G8 dimension-4 coverage

**not_claimed**
- no coupling is added (adding them would be a new contract)
- no gate status changes; G1 stays CLOSED and is scoped as the attestation of a truncation
- no symmetry beyond multiplet-diagonal phase rotations is analysed
- no exclusion of the SO(10) contract

## Flags

- `F_P_R_charge_degenerate_exact`: True
- `G1_reopened`: False
- `all_allowed_couplings_PQ_neutral_exact`: True
- `changes_g8_flavour_conclusion`: False
- `couplings_added_to_contract`: False
- `declared_lagrangian_is_a_truncation_exact`: True
- `evidence_only`: True
- `falsifies_so10_contract`: False
- `g8_dimension4_analysis_covers_all_allowed_couplings`: True
- `gate_status_changed`: False
- `one_loop_generation_claimed_exact`: False
- `radiative_generation_computed`: False
- `rg_closure_modulo_field_redefinitions_analysed`: False
- `truncation_not_removable_by_field_redefinitions_exact`: True
- `undeclared_couplings_unprotected_by_any_U1_exact`: True
- `undeclared_couplings_unprotected_by_any_multiplet_diagonal_phase_symmetry_exact`: True

## Checks

- PASS `census.allowed_26`
- PASS `census.declared_10_subset_of_allowed`
- PASS `census.generation_expanded_74`
- PASS `census.no_bare_16_16bar_mass_and_no_Phi210_coupling`
- PASS `census.undeclared_16_exact_list`
- PASS `census.undeclared_48_real_dimensions_exceed_mixing_field_redefinitions_25`
- PASS `census.undeclared_bilinear_classes_8_6_2`
- PASS `cross.g1_census_json_bound_and_links_neutral`
- PASS `cross.g8_dimension4_lists_cover_all_allowed_couplings`
- PASS `cross.g8_json_model_sha256_matches`
- PASS `cross.g8_json_recorded_and_lists_match`
- PASS `cross.g8_live_contract_section_matches`
- PASS `cross.structural_obstruction_json_census_matches`
- PASS `kernel.F_P_R_identical_under_every_kernel_element`
- PASS `kernel.allowed_26_plus_kappaH_dimension_3`
- PASS `kernel.allowed_26_plus_kappaH_plus_G1_links_dimension_3`
- PASS `kernel.allowed_26_without_scalar_links_dimension_4`
- PASS `kernel.declared_LagHC_dimension_3`
- PASS `kernel.declared_LagHC_plus_G1_links_dimension_3`
- PASS `kernel.every_dimension_3_kernel_equals_span_X_PQ_Nspec`
- PASS `lattice.P_minus_F_and_R_minus_F_are_integer_combinations`
- PASS `lattice.declared_rows_rank_10_one_relation`
- PASS `lattice.every_undeclared_is_an_integer_combination_of_declared_terms`
- PASS `model.LagHC_11_terms_10_fermion_bilinears_1_scalar_link`
- PASS `model.declared_terms_X_and_Z17_neutral`
- PASS `model.parsed_14_multiplets_9_fermions_5_scalars`
- PASS `pq.X_minus_PQ_equals_17_N17`
- PASS `pq.all_16_undeclared_couplings_PQ_neutral`
- PASS `pq.all_26_allowed_couplings_PQ_neutral`
- PASS `pq.anomaly_N_X_0_N_PQ_minus_34_N_spec_0`
- PASS `pq.charges_match_repository_contract`
- PASS `pq.renormalizable_scalar_monomials_X_neutral_implies_PQ_neutral`
- PASS `scope.status_neutral_flags`
- PASS `sector.every_undeclared_involves_P_R_Pbar_Rbar_or_Qbar`
- PASS `sector.exactly_two_F_16bar_mass_mixings`
- PASS `sector.no_undeclared_involves_Q_SpecS_SpecB`
- PASS `z17.equals_X_mod_17_for_every_field`
