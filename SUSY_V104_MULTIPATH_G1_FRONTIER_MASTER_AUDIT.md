# SUSY V104 multipath frontier master

Status: V104_MASTER__EXACT_Q2_CORE_REDUCTION_APPENDED__LEADING_PAIR_RESULTANT_NONZERO__Q2_CONFINED_NOT_SOLVED__ALL_BRANCH_GATES_OPEN

Core SHA256: ecaff36a770c6d3bea417b7ddfa7238345b0508e62e2c320aa7d2d6ccc13e064

All 31 historical route records are preserved exactly, and B104 is appended as unaccepted route 32. All G1-G8 in the separate SUSY/C8 branch remain OPEN. Canonical V21 scope is unchanged; this is a bounded research step, not a completed theory.

## The exact Q2 core reduction

On the surviving original quartic chart Q2 (t nonzero, L=0, M nonzero) the L=0 leading residual is the exact quadratic A2 q^2 + A1 q + A0, with A2 = -1296 t^6 M and M = -alpha t^2 + 4 p t + 64 nonzero on Q2. The q-discriminant Delta = A1^2 - 4 A2 A0 is independent of h, so a rational q requires Delta to be a square in C(X) as a condition on t, p and the parameters alone.

After reconstructing r and reducing q^2 through the quadratic, every remaining residual becomes linear in q. The pairwise q-eliminations are necessary on Q2 and, once the spurious M-power from A2 is divided out, give integer-coefficient cores R4core = R4/(t^6 M^2) and C43core = C43/(t^3 M^2). Their h-resultant is a nonzero polynomial, taking the values 28, 97 and 91 modulo 101 at the fixed slices (2,1), (3,1) and (2,3) with M nonzero. Hence Q2 cannot contain an open two-parameter family; it is confined to a proper subvariety, neither solved nor excluded.

## Scope

The Q1 chart, the height-37 and height-148 target systems, general rational sections and the exact Mordell-Weil rank are untouched. Original rank 0..11, torsion 1, the coefficient payload and every gate are unchanged. The physics covariant-action repair required by F104 remains open. Tests verify arithmetic, lineage and scope, not experimental confirmation.

## Acceptance and next obligation

There are zero accepted extensions.

- A1: OBSTRUCTED_FOR_NEUTRAL_CONSTANT_ANSATZ_RESTRICTED_WITNESSES_RETAINED
- A2: PASS_RESTRICTED_DIAGNOSTICS_FULL_GAMMAHAT_INFLOW_OPEN
- A3: DOUBLE_PIVOT_BOUNDARY_EXCLUDED__Q2_CONFINED_TO_PROPER_SUBVARIETY__Q1_OPEN
- A4: EXACT_TRIANGULAR_REDUCTIONS_GLOBAL_TAILS_UNSOLVED
- A5: OPEN_NO_ACCEPTED_PARENT

F105_Q2_RESIDUAL_CLOSURE_Q1_AND_TARGET_SYSTEMS_WITH_COVARIANT_ACTION_REPAIR

Impose the remaining Q2 residuals N2,N1,N0 with their cross conditions C42,C32,C4i and the Delta-square condition on the confined subvariety; decide Q2 over C(X) with a certificate, or open the Q1 chart by the same method. No rank or point promotion without a certificate.

Construct the covariant action repair required by F104: a globally defined normal/internal tensor or diagonal G-structure carrying normal charge 1 with all old representations and a recomputed vacuum; do not install a neutral constant or a formal inverse eta character by declaration. Continue the height-37/148 target tails with all primitivity and global-tail obligations. Complete nonlinear QK/F/D, Higgs-zero matching, full quantum action, soft spectrum, unification and cosmology on the same data.

[Detailed V104 Q2 derivation](SUSY_V104_Q2_CORE_REDUCTION_AUDIT.md)

## Primary sources

- [Schutt-Shioda: intersection-height and minimal-degree framework; Section14.2 warns that coefficient counting is a heuristic, not a no-solution proof. The Q2 leading-coefficient identity, q-elimination and resultant confinement are derived here.](https://arxiv.org/pdf/0907.0298)
- [Short Weierstrass coordinates and rational group operations; no square-root extension or rescaling of the fixed Jacobian is used.](https://www.jmilne.org/math/Books/EC2.pdf)
- [Sturmfels: Sylvester resultant and exact elimination; a fixed nonzero specialized determinant certifies only the named generic elimination.](https://math.berkeley.edu/~bernd/cbms.pdf)
