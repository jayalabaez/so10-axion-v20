# SUSY V105: Q2 evidence repair and complete residual reduction

Status: V105_V104_CORE_EVIDENCE_RETRACTED__CORRECTED_Q2_CONFINEMENT_AND_FULL_RECONSTRUCTION_ATLAS__ALL_GATES_OPEN

Core SHA256: 75d6be819200079760202dd9cd4dadf13cb0978717edf677149caa00eb8aa045

All G1-G8 remain OPEN. This checkpoint repairs a concrete error in V104 and advances the exact Q2 reduction; it does not solve Q2, construct a physical target, establish new physics or complete the theory. Historical files remain frozen, but the invalid evidence is explicitly superseded.

## What failed in V104

The original variable order is (t,p,q,h,alpha,beta,gamma,delta,epsilon). V104's manual converter reads powers[4] for h and powers[5:] for parameters. Executing that exact source maps h to 1, alpha to h, beta to alpha, gamma to beta, delta to gamma and epsilon to delta. In particular it sends the nonzero polynomial h-1 to zero. All five actual residual polynomials fail round-trip comparison. This is not a harmless change of notation: the leading quadratic used a different, correct conversion, so incompatible systems were mixed.

The derived V104 cores and determinant values 28,97,91 are therefore retracted as evidence about the original Q2 chart. The independently calculated A2=-1296 t^6 M identity and the h-independent discriminant remain correct. Hashes and the old snapshot tests only establish self-consistency; they did not test the missing source-polynomial identity.

## Correct conversion and five exact identities

V105 delegates symbol ordering to the polynomial ring and checks every basis symbol, mixed monomials, and each original residual. Write F=A2 q^2+A1 q+A0, where M=-alpha t^2+4pt+64, and reconstruct r from L=0. All five remaining source numerators N4,...,N0 obey exact universal polynomial identities A2^s_i N_i=Q_i F+t^k_i(ell_i q+mu_i). The pairs (s_i,k_i) are (2,12),(2,12),(3,18),(3,18),(4,24). Since t and M are nonzero on Q2, these identities are equivalent to the original residual equations once F=0.

The ell/mu h-degrees are respectively (1,2),(1,2),(2,2),(2,2),(2,3). The full coefficient expressions and quotient hashes are saved in the JSON certificate. Independent dense polynomial division starts again from the V103 residuals at rational and finite-field specializations, rather than comparing the new converter with itself. Parent cores and source pins are rechecked even after the pure calculation cache is warm; returned reports are not mutable cached state.

## Corrected confinement is reestablished

Set R_i=A2 mu_i^2-A1 ell_i mu_i+A0 ell_i^2 and C_ij=ell_i mu_j-ell_j mu_i. Every Q2 point satisfies all five R_i and all ten C_ij. The corrected leading cores retain exact removable factors t^6 M^2 and t^3 M^2, but now have h-degrees 4 and 3 and contain 1815 and 930 terms. Their explicitly assembled 7-by-7 Sylvester determinants are 81,14,16 modulo 101 at X=1 and (t,p)=(2,1),(3,1),(2,3). All fixed degrees are preserved and M is nonzero at each witness.

Thus the determinant polynomial in X,t,p is not identically zero. Every common h root makes it vanish, including degenerate leading coefficients. The projection of Q2 is confined to this proper zero locus by a new valid proof, not by V104's corrupted cores. No pole bound on rational t(X),p(X), no modular affine-emptiness inference and no rank specialization is used. The nonzero polynomial does not exclude its own zero locus and therefore does not exclude Q2.

The independently committed V105 index correction (commit 3cf518b) is preserved and source-bound. Its four N4/N3 linear coefficients agree identically with this reduction. Its raw determinant values 65,52,20 differ only by normalization: Res_h(R4,C43)=t^30 M^14 Res_h(R4core,C43core). All three residues match this exact scaling law. The two corrected audits therefore agree; neither restores V104's invalid 28,97,91 evidence.

## A complete common-root case split

For any index i with ell_i nonzero, the five conditions R_i=0 and C_ij=0 for the other four indices are necessary and sufficient for a common original-field root, reconstructed uniquely as q=-mu_i/ell_i. The exact identities are ell_i^2 F(-mu_i/ell_i)=R_i and ell_i(ell_j q+mu_j)=C_ij. The discriminant square is automatic here: Delta=(A1-2 A2 mu_i/ell_i)^2. There are five disjoint regular charts, choosing the first nonzero ell in order 4,3,2,1,0.

If all five ell_i vanish, the five norm conditions force all five mu_i to vanish because A2 is nonzero in a field. The quadratic then has a root over C(X) precisely when Delta is a square in C(X), including zero. This sixth, zero-slope case is retained, as are repeated roots. All fifteen polynomial conditions suffice over the algebraic closure, but not over C(X) on this exceptional case without its square condition. Pairwise norms alone are insufficient: q-1 and q+1 each meet q^2-1 but have no common root with each other.

This is a point-set equivalence over a field, not an equality of scheme ideals and not a solution for t,p,h. Only the leading two cores are expanded; the other thirteen conditions are saved exactly in factored form using the complete ell/mu coefficients. No regular chart or exceptional locus is proved empty or populated.

## Unchanged physics and next obligation

Q1, both height-37/148 global target systems, original rank bounds 0..11, torsion order 1, and the normal-covariance/anomaly obstructions retain their previous scope. No original nonzero section, new particle sector, vacuum, inflow or complete microscopic parent is constructed. The physics repair remains an obligation, not an assumption.

F106_Q2_RECONSTRUCTION_CHARTS_Q1_TARGETS_AND_COVARIANT_ACTION_REPAIR

Work on the corrected Q2 reconstruction atlas: for each first nonzero ell_i, solve R_i=0 and the four C_ij=0 over C(X), then reconstruct q=-mu_i/ell_i. Separately solve the all-ell=all-mu=0 locus with its Delta-square condition. Alternatively advance Q1 or a certified rank method. Retain fixed degrees and all valuation/pivot boundaries in any generic exclusion; no isolated modular no-point search or equation count certifies it.

The full physics obligation remains unchanged: construct actual globally normal-covariant tensors or a lifted diagonal structure, then a same-action QK/F/D vacuum, full Gammahat anomaly/inflow and Higgs-zero matching. Solve the height37/148 global tails with primitivity and complete the soft spectrum, unification and cosmology. A formal tensor line or inverse eta character is not a constructed physical repair.

## Primary sources

- [Polynomial rings bind monomial exponent tuples to an explicit generator ordering. V105 uses from_expr and independently checks all basis symbols and source-polynomial round trips; the old indexing error is reproduced directly from its frozen source.](https://docs.sympy.org/latest/modules/polys/internals.html)
- [Chapter4 gives the Sylvester resultant framework. V105 uses an explicitly assembled fixed-degree7x7 determinant for a necessary projection equation, not a generic no-point inference from a modular search.](https://math.berkeley.edu/~bernd/cbms.pdf)
- [The inherited elliptic-surface height and globally integral degree framework is retained. This step repairs algebra for the existing original quartic only and does not change rank, height targets, or physical gates.](https://arxiv.org/pdf/0907.0298)
