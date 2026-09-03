# SUSY V104: exact Q2 core reduction on the original quartic

Status: V104_Q2_CORE_REDUCTION__LEADING_PAIR_RESULTANT_NONZERO__Q2_CONFINED_TO_PROPER_SUBVARIETY__ALL_BRANCH_GATES_OPEN

Core SHA256: b22468dd4bd4ab3c77839ba8fa561deee01a539f23fc64e176c4660a169cc41c

This is a bounded research step on the separate SUSY/C8 branch, not a completed theory. All G1-G8 remain OPEN, canonical V21 scope is unchanged, and no route parent is accepted.

## The Q2 leading coefficient factors exactly

On the surviving chart Q2 (t nonzero, L=0, M nonzero) the L=0 leading residual is the exact quadratic A2 q^2 + A1 q + A0. Its leading coefficient factors as A2 = -1296 t^6 M with M = -alpha t^2 + 4 p t + 64, so A2 is manifestly nonzero on Q2 and the quadratic is genuine.

The q-discriminant Delta = A1^2 - 4 A2 A0 is independent of h. A rational q on Q2 therefore requires Delta to be a square in C(X), a condition on t, p and the fixed parameters alone, decoupled from h.

## Exact q-elimination and the M-squared cores

After substituting the reconstructed r and reducing q^2 through the quadratic, every remaining residual N4..N0 becomes exactly linear in q, N_i -> ell_i q + m_i. The pairwise eliminations R_i = A2 m_i^2 - A1 ell_i m_i + A0 ell_i^2 and C_ij = ell_i m_j - ell_j m_i are necessary on Q2. The q-reduction multiplies through by powers of A2 = -1296 t^6 M; that M-power is nonzero on Q2 and is divided out exactly, leaving integer-coefficient cores R4core = R4/(t^6 M^2) and C43core = C43/(t^3 M^2).

## The leading pair confines Q2 to a proper subvariety

Both R4core and C43core vanish on any Q2 point. Their h-resultant is a nonzero polynomial in (t,p): at the bound coefficient payload it takes the nonzero values 28, 97, 91 modulo 101 at the fixed slices (2,1), (3,1), (2,3), all with M nonzero. Hence Q2 cannot contain an open two-parameter family; its solutions lie on the proper subvariety Res_h(R4core,C43core)=0, together with the retained ell4=ell3=0 degeneracy. Q2 is neither solved nor excluded, and no rational-function degree bound in X is assumed.

## Scope and next obligation

The Q1 chart, the height-37 and height-148 target systems, general rational sections and the exact Mordell-Weil rank are untouched. Original rank 0..11, torsion 1, the coefficient payload and every gate are unchanged. Tests verify arithmetic, lineage and scope, not experimental confirmation.

F105_Q2_RESIDUAL_CLOSURE_Q1_AND_TARGET_SYSTEMS_WITH_COVARIANT_ACTION_REPAIR

Impose the remaining Q2 residuals N2,N1,N0 with their cross conditions C42,C32,C4i and the Delta-square condition on the confined subvariety; decide Q2 over C(X) with a certificate, or open the Q1 chart by the same method. No rank or point promotion without a certificate.

Construct the covariant action repair required by F104: a globally defined normal/internal tensor or diagonal G-structure carrying normal charge 1 with all old representations and a recomputed vacuum; do not install a neutral constant or a formal inverse eta character by declaration. Continue the height-37/148 target tails with all primitivity and global-tail obligations. Complete nonlinear QK/F/D, Higgs-zero matching, full quantum action, soft spectrum, unification and cosmology on the same data.

## Primary sources
- [Schutt-Shioda: intersection-height and minimal-degree framework; Section14.2 warns that coefficient counting is a heuristic, not a no-solution proof. The Q2 leading-coefficient identity, q-elimination and resultant confinement are derived here.](https://arxiv.org/pdf/0907.0298)
- [Short Weierstrass coordinates and rational group operations; no square-root extension or rescaling of the fixed Jacobian is used.](https://www.jmilne.org/math/Books/EC2.pdf)
- [Sturmfels: Sylvester resultant and exact elimination; a fixed nonzero specialized determinant certifies only the named generic elimination.](https://math.berkeley.edu/~bernd/cbms.pdf)
