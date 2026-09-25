# G3 SM Pati-Salam gate readiness (dry run) -- v20

**Status:** `G3_SM_TARGET_READINESS_DRY_RUN__NO_GATE_STATUS_CHANGED`

**Gate status changed:** `False` -- **G3 closed:** `False`

DRY RUN ONLY -- this is not a G3 closure. This module changed no gate status, gate report, ledger entry, workflow or checksum: the final G3 gate stays OPEN and the ledger's G3 stays OPEN. Of the final gate's 20 criteria, 7 are proof routes specific to the chiral-H candidate; of the other 13, the Pati-Salam target satisfies 11 exactly (2 of them, all_PD_equality_orbits_classified_exactly, beta_global_gap_and_unique_equality_exact, only under decision(s) D6: they rest on cited classical theorems and hand-argued steps that are not machine-checked). would_close_G3_mathematically_if_SM_track_added is False; blocking: full_Hessian_rank_448_nullity_38_exact, full_448_quotient_strictly_positive_exact. Both Hessian criteria are exactly false at the tuned benchmark under their literal analogues (rank 451 / nullity 35 and kernel = the 35-dimensional orbit): the certified rank/nullity is 447/39 and the kernel is the 35 orbit tangents plus 4 tuned light-doublet directions, so the 451-dimensional symmetry quotient is not strictly positive. The remaining 11 of the 13 non-route-specific criteria are satisfied exactly. With the planner's replacement criterion S11 in place of both Hessian criteria (rank 447 / nullity 39, kernel = orbit tangents plus the exactly identified tuned doublet, lifted at quartic order by lambda_eff = 127/64 > 0) the result would be True, subject to decisions D2 and D6 (adopting S11 changes the gate contract). On the SM track witness family: O06 = 2|kappa| r0 + eps, eps > 0 (V_eps = V + eps N_H), inside the perturbative window 0 < eps < 599/50 (O06_eps = 2|kappa| r0 + eps < 12 < 4 pi; couplings_perturbative is certified only there, while L1 and L2 hold for every eps > 0), the literal criteria are met exactly: all 13 of the 13 non-route-specific criteria are SATISFIED_EXACT, including both Hessian criteria (for every eps > 0 the Hessian at q0 is PSD with kernel exactly the 35-dimensional orbit, 451/35, strictly positive on the symmetry quotient; L2) and the equality-set and global-gap criteria ({V_eps = V0} = G.q0 for every eps >= 0 by L1 plus the equality report), so would_close_G3_mathematically_on_eps_member_if_SM_track_added = True, presuming decision(s) D2, D6 with the wiring conjunct S9 not evaluated. The tuned eps = 0 limit is not a strict minimum on the symmetry quotient (447/39); the O06-raised member is eps = r0^2/100 (on_O06_raised_member = True). The doublet has mass^2 eps M_GUT^2, light for eps << r0^2, but electroweak symmetry is not broken. Decisive theorem: semantic agreement True (same 486-real chart, same G = SO(10) x U(1)_X x U(1)_PQ, V and q0 replaced by the SM benchmark), exact textual agreement False (the equality module emits no required_statement yet); the gate's conjunct required_statement == theorem (wiring, S9) is not evaluated here. Under the planner's proposed routing (decision D5, pending; the ledger/roadmap wave-3 G3 deliverable currently says the PS candidate still needs its model-level caveats resolved), G3 would carry the disclosures (accidental U(1)_PQ, benchmark-only Hessian, float64 end-to-end binding, cited theorems, family scope) and the tuned-doublet Hessian kernel (resolved by D2: S11 at the tuned point, or an eps > 0 witness), while the coloured remnants, EWSB, RG content, Higgs quartic, Yukawas and G5's coupling vector would belong to G4-G8 (the doublet zero modes also as G4/G6 classification items), and DT/O05/hierarchy naturalness would lie outside G1-G8; otherwise these caveats remain G3-wave requirements.

## Readiness booleans

- `would_close_G3_mathematically_if_SM_track_added`: `False`
- `science_criteria_all_satisfied_exact`: `False`
- `release_criteria_all_satisfied_exact`: `True`
- `integrity_checks_all_pass`: `True`
- `with_planner_S11_replacement_criterion`: `True` (replaces the literal analogues of BOTH Hessian criteria (full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_exact) by S11 (rank 447 / nullity 39, kernel = orbit tangents (+) exactly identified tuned doublet, quartic lift 127/64 > 0); would be True subject to decisions D2 (adopting S11 changes the gate contract) and D6)
- `on_O06_raised_member`: `True` (the raised member (O06 + r0^2/100) lies outside the candidate's 27-parameter family, so the global-minimum and equality-set artifacts alone do not cover it; it is the eps = r0^2/100 member of the eps family, and this boolean equals the eps-member boolean for it (S12 value and eps-family coverage required))
- `would_close_G3_mathematically_on_eps_member_if_SM_track_added`: `True` (decisions presumed: `D2`, `D6`; wiring conjuncts not evaluated: required_statement == theorem (wiring; S9))
- blocking criteria: `full_Hessian_rank_448_nullity_38_exact`, `full_448_quotient_strictly_positive_exact`
- decisions presumed by SATISFIED_EXACT: `D6` (criteria: `all_PD_equality_orbits_classified_exactly`, `beta_global_gap_and_unique_equality_exact`)
- literal conjuncts not evaluated: `beta_global_gap_and_unique_equality_exact`: required_statement == theorem (wiring; S9)
- definition: True only if every readiness integrity check passes and every non-route-specific criterion of the final gate (science and release) is SATISFIED_EXACT under its mathematical analogue; the wiring conjunct required_statement == theorem (S9) is excluded, and SATISFIED_EXACT for the equality-set and global-gap criteria presumes decision D6 (cited classical theorems and hand-argued steps accepted as G3-grade inputs)
- caveat routing status: `PROPOSED_UNDER_D5__NOT_CURRENT_REPO_DEFINITION`

## Criterion table

| final-gate criterion | kind | chiral-H | Pati-Salam analogue | PS value | classification | grade | justification |
|---|---|---|---|---|---|---|---|
| `G1_G2_exact_scoped_calculations_complete` | science | `True` | shared_G1_G2_exact_scoped_calculations_complete | `True` | **SATISFIED_EXACT** | exact | Shared prerequisite, identical for both targets: the ledger's G1/G2 scoped statuses are COMPLETE and the PS coupling vector lies in the same 51-parameter exact-X contract. |
| `full_candidate_exactly_stationary` | science | `True` | sm_candidate_exactly_stationary | `True` | **SATISFIED_EXACT** | exact | Exact: stationarity follows from the exact SOS global minimum (every r0 > 0) and is bound to the compiler state; the exact Hessian report also finds the full 486-component gradient exactly 0. |
| `full_homogeneous_quartic_BFB_exact` | science | `True` | sm_full_homogeneous_quartic_BFB_exact | `True` | **SATISFIED_EXACT** | exact | Exact: the candidate's source-bound SOS certificate gives V4 >= \|q\|^4/167, and 1/167 = 1/sum(beta^2/alpha) is recomputed here from its recorded rationals. |
| `target_unbroken_algebra_is_standard_model` | science | `False` | sm_target_unbroken_algebra_is_standard_model_exact | `True` | **SATISFIED_EXACT** | exact | Exact integer stabilizer computation, confirmed independently by the sigma-hypercharge audit (p with the Y = 0 singlet leaves exactly the standard SM); the chiral-H point fails this. |
| `target_symmetry_orbit_ranks_36_37_38_exact` | science | `True` | sm_symmetry_orbit_ranks_33_34_35_exact | `True` | **SATISFIED_EXACT** | exact | Exact integer ranks from the equality module (P3), consistent with the candidate's exact 12-dimensional SM stabilizer (45 - 33 = 12); the chiral-H ranks 36/37/38 belong to a 9-dimensional stabilizer and do not transfer. |
| `couplings_perturbative` | science | `True` | sm_couplings_perturbative_exact | `True` | **SATISFIED_EXACT** | exact | Exact rational comparison (73/8 < 12 and pi > 3); the gate's chiral-H criterion compares floats against 4 pi with 28 couplings. |
| `full_Hessian_rank_448_nullity_38_exact` | science | `True` | sm_full_Hessian_rank_451_nullity_35_exact | `False` | **FAILED** | exact | Exactly false at the tuned benchmark: exact rank/nullity 447/39 instead of the literal 451/35; the certified kernel is 35 symmetry tangents + 4 real light-doublet directions, i.e. 4 tuned light-doublet zero modes beyond the 35-dimensional orbit. [false exact evidence: G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.exact_rank, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.exact_nullity] |
| `full_448_quotient_strictly_positive_exact` | science | `True` | sm_full_451_quotient_strictly_positive_exact | `False` | **FAILED** | exact | Exactly false at the tuned benchmark: the certified kernel is 35 symmetry tangents + 4 real light-doublet directions (exact nullity 39 vs orbit dimension 35; exact_PSD True), so the 451-dimensional symmetry quotient has an exact 4-dimensional kernel and the Hessian is positive definite only on a 447-dimensional complement of its kernel. [false exact evidence: G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:flags.strict_quotient_positive, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:flags.strictly_positive_on_symmetry_quotient, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:flags.all_zero_modes_are_symmetry_tangents, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.strictly_positive_on_symmetry_quotient, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.zero_modes_beyond_symmetry_orbit, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.exact_nullity, G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:exact_certificate.kernel_spanning_set] |
| `full_fixed_F_offkernel_gap_and_equality_exact` | science | `True` | none (chiral-H route: fixed Phi = F stratum) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: the chiral-H proof bounds V on the fixed Phi = F stratum first because its SOS does not cover arbitrary Phi at once. PS counterpart: the adapted SOS27 identity bounds V_PS on the whole chart for arbitrary Phi at once (holds). |
| `max_negative_all_zero_residual_route_excluded_exactly` | science | `True` | none (chiral-H route: maximally-negative pure-Delta sector, zero residuals) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: this excludes a Sigma sector where the chiral-H SOS completion could fail; the PS proof has no such sector. PS counterpart: V_PS - V0 is a sum of eight terms each >= 0 on the whole chart (P0), with no residual sectors (holds). |
| `max_negative_pure_Delta_full_residual_gap_excluded_exactly` | science | `True` | none (chiral-H route: maximally-negative pure-Delta sector, all residuals) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: residual-gap bound specific to the chiral-H SOS reduction. PS counterpart: the eight-term SOS expansion matches the coefficient map exactly (kappa < 0, > 0, = 0) (holds). |
| `rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3` | science | `True` | none (chiral-H route: rank-one SU(3) four-dimensional Phi slice) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: a slice of the chiral-H rank-one Phi program. PS counterpart: the exact 210 bound V_Phi >= -1 holds for every real Phi, saturated on SO(10).p (holds). |
| `rank1_SU4_representation_infrastructure_ready_without_closing_G3` | science | `True` | none (chiral-H route: rank-one SU(4) Schur SOS infrastructure) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: infrastructure for the chiral-H fixed-endpoint Schur SOS/SDP program; the PS proof needs no SDP. PS counterpart: a closed-form SOS identity (symbolic, all r0 > 0) replaces the SDP program (holds). |
| `signed_Phi_orbits_locally_isolated_exactly` | science | `True` | none (chiral-H route: signed +-F Phi orbits) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: local isolation of the signed Phi = +-F orbits of the chiral-H route. PS counterpart: the Phi minimum set is the single global orbit SO(10).p (exact_210 corollary of P1) (holds). |
| `complete_SU3_fixed_Phi_slice_classified_exactly` | science | `True` | none (chiral-H route: SU(3)-fixed Phi slice) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: slice-by-slice Phi classification of the chiral-H route. PS counterpart: P1 classifies every Phi with \|Phi\| = 1, I45 = I210 = I5940 = 0 at once via the Pluecker defect (holds). |
| `all_PD_equality_orbits_classified_exactly` | science | `False` | sm_equality_set_single_G_orbit_exact | `True` | **SATISFIED_EXACT** | exact (cited classical theorems + 6 hand-argued steps; D6) | Exact proof (P0-P3; 45 checks) that rests on 6 cited classical theorems and 6 hand-argued elementary steps that are not machine-checked (pinned verbatim here); counting it as exact presumes decision D6 (accept cited classical theorems as G3-grade inputs), which is pending.  Uniqueness uses the accidental U(1)_PQ, which the gate's theorem already quotients by. |
| `beta_global_gap_and_unique_equality_exact` | science | `False` | sm_global_gap_and_unique_equality_exact | `True` | **SATISFIED_EXACT** | exact (cited classical theorems + 6 hand-argued steps; D6) | Exact up to pinned hand-argued steps: the adapted SOS27 identity (symbolic in r0, x0, kappa; 16 exact certificate checks) gives V_PS >= V0 with V(q0) = V0, but its H/S sector bound V_HS >= -r0^4 also uses the hand-argued Cauchy-Schwarz step \|H.H\| <= N_H and the sign case analysis (\|S\| <= r0, \|S\| > r0) that turns the exact sympy square-completion identities into the inequality (not machine-checked); the equality module proves {V_PS = V0} = G.q0 with 6 cited classical theorems and 6 hand-argued steps.  Counting it as exact presumes decision D6 (pending). |
| `authoritative_external_model_contract_executed` | release | `True` | authoritative_external_model_contract_executed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger contract_consistent = True and every PS report carries the authoritative contract id. |
| `G1_promoted_closed` | release | `True` | G1_promoted_closed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger gates.G1.status == 'CLOSED'. |
| `G2_promoted_closed` | release | `True` | G2_promoted_closed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger gates.G2.status == 'CLOSED'. |

Counts: SATISFIED_EXACT 11, SATISFIED_FLOAT_ONLY 0, FAILED 2, ROUTE_SPECIFIC_NOT_APPLICABLE 7.

## SM track witness family: O06 = 2|kappa| r0 + eps, eps > 0

V_eps = V_PS + eps N_H: O06 = 2|kappa| r0 + eps, the other 26 benchmark couplings unchanged, same vacuum q0 = (p, 0, r0 sigma_std, r0, x0) and same G. Evidence: G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json eps_family (L1: equality set, L2: Hessian kernel, doublet mass^2 = eps) plus the benchmark evidence.

- `would_close_G3_mathematically_on_eps_member_if_SM_track_added`: `True`
- eps window: 0 < eps < `599/50` (O06_eps = 2|kappa| r0 + eps < 12 < 4 pi); raised member eps = `1/2500`, tiny member eps = `1/25000000`
- blocking criteria: none
- conditional on decisions: `all_PD_equality_orbits_classified_exactly`: D6, `beta_global_gap_and_unique_equality_exact`: D6
- physics: the doublet Re H_6..9 has tree-level mass^2 eps M_GUT^2: light but massive for eps << r0^2, eps -> 0+ is the tuned massless limit; H = 0, so electroweak symmetry is not broken on any member
- planner D2: D2's second option ('the O06-raised member ... needs the equality-set theorem extended to O06 >= 2|kappa| r0'): that extension is L1 of the exact Hessian report's eps_family, and the whole eps > 0 family (not only eps = r0^2/100) meets the literal Hessian criteria

| final-gate criterion | kind | eps-member analogue | value | classification | grade | justification |
|---|---|---|---|---|---|---|
| `G1_G2_exact_scoped_calculations_complete` | science | eps_member_shared_G1_G2_exact_scoped_calculations_complete | `True` | **SATISFIED_EXACT** | exact | Shared prerequisite: ledger G1/G2 COMPLETE, and V_eps differs from V only in the O06 coefficient (exact). |
| `full_candidate_exactly_stationary` | science | eps_member_exactly_stationary | `True` | **SATISFIED_EXACT** | exact | Exact: the benchmark gradient vanishes exactly, grad N_H vanishes at H = 0, and V_eps >= V0 = V_eps(q0). |
| `full_homogeneous_quartic_BFB_exact` | science | eps_member_full_homogeneous_quartic_BFB_exact | `True` | **SATISFIED_EXACT** | exact | Exact: the benchmark's source-bound bound V4 >= \|q\|^4/167 and N_H homogeneous of degree 2 (sympy, census counts (H, Hbar) = (1, 1)). |
| `target_unbroken_algebra_is_standard_model` | science | eps_member_target_unbroken_algebra_is_standard_model_exact | `True` | **SATISFIED_EXACT** | exact | Exact integer stabilizer computation at q0 (unchanged), confirmed by the sigma-hypercharge audit. |
| `target_symmetry_orbit_ranks_36_37_38_exact` | science | eps_member_symmetry_orbit_ranks_33_34_35_exact | `True` | **SATISFIED_EXACT** | exact | Exact integer ranks from the equality module (P3), independent of the O06 coefficient. |
| `couplings_perturbative` | science | eps_member_couplings_perturbative_exact | `True` | **SATISFIED_EXACT** | exact | Exact rational comparisons (pi > 3); only O06 moves with eps (eps_family L1 coefficient shift). |
| `full_Hessian_rank_448_nullity_38_exact` | science | eps_member_full_Hessian_rank_451_nullity_35_exact | `True` | **SATISFIED_EXACT** | exact | Exact: Hess V_eps(q0) = H_0 + eps Hess N_H with both PSD, so its kernel is ker H_0 cap ker Hess N_H = span(T35) (H_0 PSD with kernel T35 + D4, Hess_u N_H = 2 P_H, D4 inside the H block, T35 zero there, rank 39; all exact over Q); inertia 451/35/0 re-certified by exact LDL at eps = r0^2/100 and r0^2/10^6. |
| `full_448_quotient_strictly_positive_exact` | science | eps_member_full_451_quotient_strictly_positive_exact | `True` | **SATISFIED_EXACT** | exact | Exact: a PSD matrix whose kernel is exactly the orbit tangent space is strictly positive on the quotient; L2 gives PSD and kernel = span(T35) for every eps > 0 (the tuned eps = 0 limit, 447/39, is not). |
| `full_fixed_F_offkernel_gap_and_equality_exact` | science | none (chiral-H route: fixed Phi = F stratum) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: the chiral-H proof bounds V on the fixed Phi = F stratum first because its SOS does not cover arbitrary Phi at once. PS counterpart: the adapted SOS27 identity bounds V_PS on the whole chart for arbitrary Phi at once (holds). |
| `max_negative_all_zero_residual_route_excluded_exactly` | science | none (chiral-H route: maximally-negative pure-Delta sector, zero residuals) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: this excludes a Sigma sector where the chiral-H SOS completion could fail; the PS proof has no such sector. PS counterpart: V_PS - V0 is a sum of eight terms each >= 0 on the whole chart (P0), with no residual sectors (holds). |
| `max_negative_pure_Delta_full_residual_gap_excluded_exactly` | science | none (chiral-H route: maximally-negative pure-Delta sector, all residuals) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: residual-gap bound specific to the chiral-H SOS reduction. PS counterpart: the eight-term SOS expansion matches the coefficient map exactly (kappa < 0, > 0, = 0) (holds). |
| `rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3` | science | none (chiral-H route: rank-one SU(3) four-dimensional Phi slice) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: a slice of the chiral-H rank-one Phi program. PS counterpart: the exact 210 bound V_Phi >= -1 holds for every real Phi, saturated on SO(10).p (holds). |
| `rank1_SU4_representation_infrastructure_ready_without_closing_G3` | science | none (chiral-H route: rank-one SU(4) Schur SOS infrastructure) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: infrastructure for the chiral-H fixed-endpoint Schur SOS/SDP program; the PS proof needs no SDP. PS counterpart: a closed-form SOS identity (symbolic, all r0 > 0) replaces the SDP program (holds). |
| `signed_Phi_orbits_locally_isolated_exactly` | science | none (chiral-H route: signed +-F Phi orbits) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: local isolation of the signed Phi = +-F orbits of the chiral-H route. PS counterpart: the Phi minimum set is the single global orbit SO(10).p (exact_210 corollary of P1) (holds). |
| `complete_SU3_fixed_Phi_slice_classified_exactly` | science | none (chiral-H route: SU(3)-fixed Phi slice) | `True` | **ROUTE_SPECIFIC_NOT_APPLICABLE** | n/a (route-specific) | Proof route used only for the chiral-H SU(5)+Delta candidate. Not applicable: slice-by-slice Phi classification of the chiral-H route. PS counterpart: P1 classifies every Phi with \|Phi\| = 1, I45 = I210 = I5940 = 0 at once via the Pluecker defect (holds). |
| `all_PD_equality_orbits_classified_exactly` | science | eps_member_equality_set_single_G_orbit_exact | `True` | **SATISFIED_EXACT** | exact (cited classical theorems + 6 hand-argued steps; D6) | Exact given the equality-set theorem for V (P0-P3; 6 cited classical theorems and 6 hand-argued steps, pinned verbatim here), plus one exact step (L1) recorded by the exact Hessian report; counting it as exact presumes decision D6 (pending), as for the benchmark. |
| `beta_global_gap_and_unique_equality_exact` | science | eps_member_global_gap_and_unique_equality_exact | `True` | **SATISFIED_EXACT** | exact (cited classical theorems + 6 hand-argued steps; D6) | Exact up to the same pinned hand-argued steps and cited theorems as the benchmark (decision D6): V_PS >= V0 with {V_PS = V0} = G.q0, and L1 carries both to V_PS,eps exactly (N_H >= 0, zero exactly at H = 0). |
| `authoritative_external_model_contract_executed` | release | authoritative_external_model_contract_executed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger contract_consistent = True and every PS report carries the authoritative contract id. |
| `G1_promoted_closed` | release | G1_promoted_closed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger gates.G1.status == 'CLOSED'. |
| `G2_promoted_closed` | release | G2_promoted_closed (shared) | `True` | **SATISFIED_EXACT** | exact | Non-numerical status evidence: ledger gates.G2.status == 'CLOSED'. |

Counts: SATISFIED_EXACT 13, SATISFIED_FLOAT_ONLY 0, FAILED 0, ROUTE_SPECIFIC_NOT_APPLICABLE 7.

## Decisive theorem

- Final gate: For every 486-real field q, V_beta(q)-V_beta(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0.
- SM counterpart: For every 486-real field q, V_PS(q)-V_PS(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0.
- Equality module: For every r0 > 0, x0 > 0 and real kappa with kappa^2 < 8 r0^2, the SM Pati-Salam benchmark potential V of g3_sm_pati_salam_candidate_v20 on the canonical 486-real chart (the 27-parameter family, 25 nonzero parameters at kappa = 0; V is the candidate's adapted SOS form, which equals the compiler potential exactly coefficient by coefficient and for each source-bound operator, and in float64 end to end) satisfies V >= V0 = -1 - r0^4/8 - r0^4 - x0^4/32 and {V = V0} = G.(p, r0 sigma_std, 0, r0, x0) = {(Phi, Sigma, 0, S, Phi17) : (Phi, Sigma) in SO(10).(p, r0 sigma_std), |S| = r0, |Phi17| = x0}, G = SO(10) x U(1)_X x U(1)_PQ, p = e6789, sigma_std = z1^z2^z3^z4^z5.  The global minimum is unique modulo G; the orbit has tangent dimension 35 at the vacuum.  Here U(1)_PQ is the contract's accidental global symmetry (all 27 operators are PQ-neutral); modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (tangent rank 34 < 35; Phi17^4 conj(S)^17 has PQ charge -68), the axion direction.  Classical theorems are cited as listed in cited_theorems.  Corollary: the 210-only potential -2 v^2 |Phi|^2 + Q(Phi) has global-minimum set exactly SO(10).(v p).
- Exact textual agreement: `False`; required_statement emitted: `False`; semantic agreement: `True`
- Symmetry group (normalised): gate `SO(10)xU(1)_XxPQ`, equality module `SO(10)xU(1)_XxPQ`

| semantic component | holds |
|---|---|
| `same_field_chart_486_real` | `True` |
| `lower_bound_V_ge_V0_on_whole_chart` | `True` |
| `equality_set_is_exactly_the_orbit_of_q0` | `True` |
| `same_symmetry_group_G` | `True` |
| `uniqueness_quotient_includes_accidental_PQ_in_both` | `True` |
| `q0_is_the_sm_benchmark_vacuum` | `True` |
| `benchmark_inside_theorem_domain_kappa_squared_below_8_r0_squared` | `True` |

Differences:

- the equality module's theorem is a longer sentence, not the gate's one-line statement: exact textual agreement is False, and the module emits no final_acceptance_test.required_statement (planner item S9, a wiring step, not a mathematical gap)
- the equality module is stronger: it holds for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2, not only at the benchmark r0 = 1/5, x0 = 1, kappa = -1/20
- the equality module's V is the candidate's adapted SOS form, equal to the compiler potential exactly coefficient by coefficient and per source-bound operator, and in float64 end to end

## The Hessian criteria

`full_Hessian_rank_448_nullity_38_exact` (literal analogue `sm_full_Hessian_rank_451_nullity_35_exact`: **FAILED**)

- certified facts (exact, not the literal analogue): rank 447, nullity 39, inertia (+/0/-) 447/39/0, flags.exact_rank_447 = True, flags.exact_nullity_39 = True, exact_PSD = True
- the planner's S11 (see full_448_quotient_strictly_positive_exact.alternative_analogues) would replace this criterion and the quotient criterion together by 'rank 447 / nullity 39, kernel = orbit (+) tuned doublet'; the O06-raised member (S12) meets the literal 451/35 exactly
- benchmark-only: exact Hessian flags.other_r0_x0_kappa_certified = False
- the float64 analogue (no projected zero mode) also fails: the candidate records 4 projected zero modes beside symmetry rank 35; the exact report's live numerical inertia (zero modes at 1e-10) is 39

`full_448_quotient_strictly_positive_exact` (literal analogue `sm_full_451_quotient_strictly_positive_exact`: **FAILED**)

- the PS exact Hessian report uses the repository's meaning: flags.strict_quotient_positive = False (kernel = symmetry tangents, as in the chiral-H certificate); its flags.positive_definite_on_complement_of_39_dim_kernel = True is positivity on a complement of the full kernel (orbit + tuned doublet), which any PSD matrix has once its kernel is identified, and is not this criterion
- the 4 flat quadratic directions are not flat globally: the equality set is exactly the G-orbit, and the doublet is lifted at quartic order by lambda_eff = 127/64 > 0 (exact)
- `S11_kernel_is_orbit_plus_tuned_light_doublet_exact`: value `True`. Planner replacement criterion S11, replacing BOTH full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_exact: proof-grade, source-bound exact rank 447 / nullity 39 with ker Hess V(q0) = T35 (+) D4 exactly (35 orbit tangents plus the 4 real light-doublet directions Re H_6..9), PSD, positive definite on a 447-dimensional complement, smallest nonzero eigenvalue r0^2/96, and the doublet lifted at quartic order by lambda_eff = 127/64 > 0.
- `S12_O06_raised_member_rank_451_nullity_35_exact`: value `True`. Planner control S12: raising O06 by r0^2/100 gives rank 451, nullity 35, kernel exactly the orbit tangents, strictly positive on the symmetry quotient, smallest nonzero eigenvalue r0^2/100 -- both literal Hessian criteria hold exactly for that member.

## Criteria satisfied exactly only under pending decisions

- `all_PD_equality_orbits_classified_exactly`: D6; grade: exact (cited classical theorems + 6 hand-argued steps; D6)
- `beta_global_gap_and_unique_equality_exact`: D6; grade: exact (cited classical theorems + 6 hand-argued steps; D6)

## Proposed additional criteria (planner; not in the booleans)

- `S11_sm_Hessian_kernel_is_35_symmetry_plus_4_light_doublet_exact`: `True`
- `S12_sm_O06_raised_control_rank_451_nullity_35_exact`: `True`
- `ledger_G3_status_matches_gate_closure`: `True`
- `G5_BFB_evidence_covers_closing_coupling_vector`: `False`

## Physics caveats by gate (proposed routing, decision D5 pending)

Routing status: `PROPOSED_UNDER_D5__NOT_CURRENT_REPO_DEFINITION`. Current repository text: ledger wave 3 (closure_waves[3].deliverable) and roadmap W3-G3-FULL-STATIONARITY: 'it still needs its model-level caveats resolved and gate integration'; the model-level caveats (the equality set's scope lists tuned DT splitting and the O05 cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs quartic, no EWSB and no Yukawa sector) still need to be resolved in the G3 wave. The gate column below is the planner's proposal; under the current text every model-level caveat remains a G3-wave requirement.

| caveat | proposed gate | also | model-level | effect on G3 (proposed) | basis | evidence | value |
|---|---|---|---|---|---|---|---|
| The minimum is unique modulo G = SO(10) x U(1)_X x U(1)_PQ; modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits (the axion direction, Phi17^4 conj(S)^17). | **G3** | G4 | `False` | disclosure in the closure scope; no blocker (same G as FINAL_THEOREM) | final gate FINAL_THEOREM already quotients by PQ; ledger G4: 'axion directions' | `flags.unique_modulo_SO10_x_U1X_alone` | `False` |
| At the tuned benchmark the exact Hessian kernel is the 35 orbit tangents plus 4 real light-doublet directions (Re H_6..9): the symmetry quotient is not strictly positive. | **G3** | G4, G6 | `False` | fails both Hessian criteria under the literal contract (451/35, kernel = orbit) at the tuned benchmark; decision D2 (S11, or the eps > 0 member O06 = 2\|kappa\| r0 + eps, on which both hold exactly) | final gate criteria full_Hessian_rank_448_nullity_38_exact (exact_rank_448, exact_nullity_38) and full_448_quotient_strictly_positive_exact (exact_PSD, strict_quotient_positive, kernel_equals_38_symmetry_tangents); ledger G4: 'classify all remaining Hessian zero and negative modes' | `flags.kernel_equals_35_symmetry_tangents_plus_4_light_doublet` | `True` |
| The exact Hessian is certified at r0 = 1/5, x0 = 1, kappa = -r0/4 only (with the O06 + eps family through that point); the global theorem holds for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2. | **G3** |  | `False` | proposed disclosure in the closure scope (the G3 witness is the r0 = 1/5 benchmark) | proposed closure-scope disclosure (planner; not in repo) | `flags.other_r0_x0_kappa_certified` | `False` |
| V_PS is the adapted SOS form; it equals the compiler potential exactly per coefficient and per source-bound operator, and only in float64 end to end. | **G3** |  | `False` | disclosure; float evidence stays diagnostic | same binding status as the accepted chiral-H exact Hessian (source-bound exact entries, float64 compiler cross-check) | `scope.float64_evidence_only` | `<list of 2 items>` |
| The equality-set proof cites 6 classical theorems (Pluecker, Kostant-Lichtenstein, Iwasawa, Wirtinger, U(n) transitivity, highest weight/Weyl) and 6 elementary steps that are not machine-checked. | **G3** |  | `False` | the equality-set and global-gap criteria count as exact only under D6; proposed: pinned allowlist here, disclosure in README and manuscript | no repository text admits cited or non-machine-checked inputs at G3 grade; pending decision D6 (accept cited classical theorems as G3-grade inputs) | `scope.cited_not_machine_checked` | `<list of 6 items>` |
| Potentials outside the candidate's 27-parameter family are not covered by the global theorem, except the O06 + eps members (the O06-raised member among them), which the exact Hessian report's eps_family L1 covers given that theorem. | **G3** |  | `False` | proposed disclosure in the closure scope | proposed closure-scope wording (planner; not in repo): 'exact SM-preserving global vacuum of the declared 27-parameter exact-X benchmark' | `scope.not_proved_or_out_of_scope` | `<list of 5 items>` |
| The ledger's G4 spec pins the old point's rank-37/38 (449/448) quotients; at the PS vacuum the ranks are 34 (gauge + X; 452 including the axion) and 35 (451). | **G4** |  | `False` | none (G4 respecification) | ledger G4: 'carry the exact rank-37 gauge quotient ... to an accepted G3 witness, recomputing if its stabilizer changes' | `gates.G4.open_scope` | `<list of 2 items>` |
| G5 is CLOSED on the historical 27-parameter SOS vector, which differs from the PS vector (O27_B03/B04 swapped; O05, O06 and re::O12 differ at h = 0); G3, G5 and G6 must refer to one vector. | **G5** |  | `False` | none (G5 rebind) | ledger G5 closed scope: 'source-bound complete-potential SOS/BFB certificate' (decision D4) | `gates.G5.authoritative_closed_scope` | `<list of 1 items>` |
| 126bar (10bar,1,3) remnants (6,1)_4/3, (3,1)_1/3, (3,1)_4/3, (6,1)_1/3, (6,1)_2/3 lie below M_I; only the 10_H triplets sit at M_GUT. | **G6** | G8 | `True` | none | ledger G6: 'emit the complete positive spectrum' | `flags.coloured_scalars_only_at_M_GUT` | `False` |
| H = 0 at the vacuum: no EWSB.  At the tuned benchmark one doublet is massless at tree level, so the spectrum is not positive; on the eps > 0 member it is light but massive (mass^2 eps M_GUT^2), still without EWSB. | **G6** | G4 | `True` | none (the 4 zero modes are G4/G6 classification items) | ledger G6: 'emit the complete positive spectrum' | `flags.electroweak_symmetry_breaking_realized` | `False` |
| x0 = 1 at every benchmark (canonical x0 ~ 10.08); the GeV masses are illustrative. | **G6** | G7 | `True` | none | roadmap W4-G6 acceptance: 'all eigenmasses, irreps, mixings, and uncertainties are complete' | `flags.physical_benchmark_uses_canonical_phi17_scale` | `False` |
| The anchor's betas assume a light (15,2,2) above M_I and a 2HDM below; the candidate has neither and re-solving moves M_I and M_GUT. | **G7** |  | `True` | none (the G3 theorem holds for every r0 > 0, so it does not depend on the anchor) | ledger G7: 'Validated two-loop RGE and threshold matching' | `flags.rg_anchor_field_content_reproduced` | `False` |
| Tree-level lambda_eff = 127/64 (m_h ~ 195 GeV); tree-level minimality forbids the slightly negative lambda(M_I) the SM running prefers. | **G7** | G6 | `True` | none (a potential future G6/G7 FAIL, not a G3 issue) | ledger G7: 'Validated two-loop RGE and threshold matching' | `flags.higgs_mass_compatible` | `False` |
| The light doublet is an equal 5/5bar mixture (tan beta = 1): with 10_H-only Yukawas m_t = m_b at matching. | **G7** | G8 | `True` | none | ledger G7/G8 definitions | `checks.light_doublet_is_equal_5_5bar_mixture` | `True` |
| The H-linear portals O15, O38, O45, O28 vanish: no realistic Yukawa sector. | **G8** | theory_validation_matrix flavour gate | `True` | none | roadmap W6-G8 acceptance: 'one authoritative vacuum fixes all Wilson, running, phase, and uncertainty inputs' | `flags.realistic_yukawa_sector` | `False` |
| (3,1)_1/3 at ~0.24 M_I carries proton-decay mediator quantum numbers and couples to 16.16 through the 126bar Yukawa. | **G8** | G6 | `True` | none | ledger G8: 'Proton-decay prediction and falsification' | `flags.coloured_scalars_only_at_M_GUT` | `False` |
| O46_1 = -(3/5) O46_54 (to ~2e-28) and O06 = 2\|kappa\| r0 (to ~4e-20) are tuned; no symmetry enforces them. | **OUTSIDE_G1_G8** | G3 closure_scope disclosure | `True` | proposed: disclosure in the closure scope (planner wording 'tuned DT/M_I relations'; not in repo) | manuscript remaining tasks (axion_so10_theory_v20.tex: 'a radiatively stable v_Phi/v_S hierarchy'); no G1-G8 ledger definition names naturalness (the separate irreducible_gap_closure_contract_v20, with its own G-numbering, requires 'radiative stability or symmetry protection demonstrated' for its G4 hierarchy mechanism) | `flags.doublet_triplet_splitting_natural` | `False` |
| O05 = (1/8)(4 - 2 r0^2) cancels the Phi-induced (10bar,1,3) mass to ~(M_I/M_GUT)^2 ~ 4e-9; its radiative stability is not addressed. | **OUTSIDE_G1_G8** |  | `True` | none under the proposed routing | manuscript remaining tasks (axion_so10_theory_v20.tex): 'a radiatively stable v_Phi/v_S hierarchy' | `candidate.exact_nonzero_coefficients.lambda::O05_B01_126bar_norm` | `49/100` |
| Radiative stability of the M_I/M_GUT hierarchy is not addressed. | **OUTSIDE_G1_G8** |  | `True` | none under the proposed routing | manuscript remaining tasks (axion_so10_theory_v20.tex) | `scope.open` | `<list of 9 items>` |

## Planner option analysis (summary)

Planner's reading of the repository's G3 definition: an exact global-vacuum theorem with uniqueness modulo symmetry at an SM-preserving point of the declared potential, certified through the final gate on the full 486-real chart; the gate's own contract adds an exact full-Hessian rank/nullity certificate. No text requires a particular candidate, a physical hierarchy, a Higgs mass, natural DT splitting or RG consistency.

In tension with it: the ledger/roadmap wave-3 G3 deliverable (G1_G8_GATE_LEDGER_V20 closure_waves[3], g1_g8_execution_roadmap_v20 task W3-G3-FULL-STATIONARITY) says the PS candidate 'still needs its model-level caveats resolved and gate integration'; the equality set lists those caveats (tuned DT splitting and the O05 cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs quartic, no EWSB, no Yukawa sector); routing them out of G3 is decision D5, pending.

- **i_either_track_closes**: add an SM track; G3 closes if either track passes
- **ii_retarget_entirely**: retarget the gate to the PS candidate
- **iii_separate_SM_gate**: keep the gate; add a separate 'G3 on SM target' gate
- **i_prime_hybrid** (recommended): SM track is the only closure route; chiral-H kept as an integrity-checked diagnostic track that never closes G3; SM evaluation in a pure json/pathlib module (g3_sm_target_track_v20.py) imported by both ledger and final gate (no cycle); ledger_G3_status_matches_gate_closure check

Decisions needed:

- **D1**: structure: (i') recommended vs (ii) or (iii)
- **D2**: G3 witness: the tuned benchmark with exact kernel 35 + 4 (recommended; needs the S11 replacement criterion) or the O06-raised member (literal 451/35, no light Higgs; needs the equality-set theorem extended to O06 >= 2|kappa| r0)
- **D3**: internal-candidate semantics: (A) G1-G3 CLOSED approves an internal candidate (edit validate_release, ultimate/confirmation tests, tiers) or (B, recommended) also require empty downstream_caveats or G4 CLOSED
- **D4**: G5: rebind to the PS vector (recommended) or keep both vectors and require them to match
- **D5**: wave-3 clause: route 'model-level caveats' to G4/G6/G7/G8 (recommended) or keep them as G3 requirements (keeps G3 open indefinitely)
- **D6**: accept cited classical theorems as G3-grade inputs, with the pinned allowlist and disclosure

## Integration gaps

| item | state | detail |
|---|---|---|
| exact full-Hessian certificate for the PS target (planner step 1) | `DONE` | G3_SM_PATI_SALAM_EXACT_HESSIAN_V20 (447/39 exact; raised control 451/35); its tests run in current-main-full-reaudit.yml (pr-direct-tensor-gate) and rebuild the report in memory against the committed artifact, but the artifact is not regenerated (--write) in the CI chain and is not yet in validate_release_v20 core lists or SHA256SUMS |
| equality module emits final_acceptance_test.required_statement == SM_FINAL_THEOREM (S9) | `OPEN` | wiring for the decisive-theorem string binding: a conjunct of the gate's existing criterion beta_global_gap_and_unique_equality_exact (gap_acceptance.required_statement == FINAL_THEOREM), not evaluated by this dry run |
| candidate scope.open still lists the exact Hessian certificate as open | `OK` | refresh g3_sm_pati_salam_candidate_v20 scope once the exact Hessian is wired in |
| equality-set flag candidate_wired_into_g3_gate | `OPEN` | retire or rename during integration (planner step 2) |
| eps-family extension of the equality set and the Hessian to O06 = 2\|kappa\| r0 + eps (L1, L2) | `DONE` | G3_SM_PATI_SALAM_EXACT_HESSIAN_V20 eps_family: {V_eps = V0} = G.q0 for every eps >= 0 (given the equality-set theorem) and kernel = orbit, 451/35, for every eps > 0; its tests run in current-main-full-reaudit.yml (pr-direct-tensor-gate) and rebuild the report in memory against the committed artifact, but the artifact is not regenerated (--write) in the CI chain and is not yet in validate_release_v20 core lists or SHA256SUMS |
| decision D2 on full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_exact for the tuned benchmark | `OPEN` | adopt S11 (rank 447 / nullity 39, kernel = orbit (+) tuned doublet) in place of both, or take the eps > 0 member (O06 = 2\|kappa\| r0 + eps) as the SM-track witness: it meets both literal criteria exactly (eps_member), with no gate-contract change |
| decision D6 on cited classical theorems and hand-argued steps as G3-grade inputs | `OPEN` | all_PD_equality_orbits_classified_exactly and beta_global_gap_and_unique_equality_exact count as SATISFIED_EXACT here only under D6 |
| decision D5 on the wave-3 clause (model-level caveats) | `OPEN` | the current ledger/roadmap wave-3 G3 deliverable says the PS candidate 'still needs its model-level caveats resolved'; the caveat routing in this report is the planner's proposal |
| G5 rebind to the PS coupling vector (D4) | `OPEN` | the G5-certified vector differs from the PS vector |
| pure SM-track module g3_sm_target_track_v20.py, final-gate tracks layout, ledger/roadmap/matrix/confirmation/ultimate/validate_release updates, workflows, tests, README/manuscript, refreeze | `OPEN` | planner steps 3-11; none is performed by this dry run |

## Readiness integrity checks

| check | passed |
|---|---|
| `final_gate_report_executes` | `True` |
| `final_gate_criteria_match_readiness_map` | `True` |
| `ledger_executes` | `True` |
| `sigma_hypercharge_audit_executes` | `True` |
| `sm_candidate_report_executes` | `True` |
| `sm_equality_set_report_executes` | `True` |
| `sm_exact_hessian_report_executes` | `True` |
| `sm_exact_hessian_eps_family_executes` | `True` |
| `sm_candidate_equality_set_hessian_cross_bound` | `True` |
| `sm_reports_do_not_overclaim` | `True` |
| `sm_model_level_caveats_disclosed` | `True` |
| `sm_unchecked_proof_inputs_pinned` | `True` |
| `sm_float_evidence_not_promoted` | `True` |

## Inputs

| artifact | loaded | error | sha256 (LF) |
|---|---|---|---|
| `FINAL_G3_ACCEPTANCE_GATE_V20.json` | `True` | `None` | `60eb9384f9c1fb78c4734c55c2eda796c7a758a7fa72176112e7799bc6f4b926` |
| `G3_SM_PATI_SALAM_CANDIDATE_V20.json` | `True` | `None` | `997c30e1965287ffce6a47afcf2ab01a2c2c456ceebe984d2419bf6640271fbe` |
| `G3_SM_PATI_SALAM_EQUALITY_SET_V20.json` | `True` | `None` | `44bd4521206f620faf41a81112a435367bc5464559bfc9e56aef5f244cdfc647` |
| `G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json` | `True` | `None` | `3c1ad7b8f193711c9df11bb0b4b749a58ea82aeff560282c51e4eef84c8a3aca` |
| `G3_SIGMA_HYPERCHARGE_AUDIT_V20.json` | `True` | `None` | `1c631edc5b4dffdc4d2aad0c0de64d2104989dc5339306311d6d3cc9d59adbb3` |
| `G1_G8_GATE_LEDGER_V20.json` | `True` | `None` | `dddba7d5188d3a1fb120117659d852a9734904b83b099e2750562680fa58724e` |
