# SUSY V56 two-site link-parity selector audit

Status: `V56_CHANGED_TWO_SITE_SO10xSO10_ARCHITECTURE__CONNECTED_PATH_SELECTOR_ONLY__DESIRED_h_B_H2_ALLOWED__h_A_H2_AND_L_h_H2_FORBIDDEN__BUT_FACTORIZED_DEGREE6_ADJOINT_LINK_INVARIANT_REOPENS_DIRECT_MASS__MINIMAL_LEFT_POLE165x_AND_R1_TRANSPLANT_POLE16x__NO_GATE_PROMOTION`

Core SHA-256: `334778d7082f133c14c800c97b20a82a01394366e8903b46669e6a7d54b186c0`

## Result

Two-site locality plus Z2 link parity allows h B H2 and forbids the named elementary fillers, and it protects every connected endpoint path. It is not a selector for the full invariant ring. The degree-six factorized invariant (h Omega H2) Tr(A B Omegabar^T) is allowed and nonzero because Tr(A0 B0)=-6; it restores the direct weak mass and rank40. Pure-link determinant/cofactor contractions pass, but adjoint factorization kills the design. Minimal running is also poor. No gate is promoted.

## Minimal changed action

Use `Spin(10)_L x Spin(10)_R`. Place `H1,barh,h` on the left site and `H2` on the right.
An even `(10,10)` link `B` supplies the missing VEV, while odd links `Omega,Omegabar` acquire
identity VEVs. The allowed filter is

`P H1 barh + S barh h + h B H2 + (T/2) H2^2`.

The direct `h A H2` and `L h H2` expressions are not product-gauge invariants. Their identity-link
completions contain one odd `Omega` and are Z2-forbidden. The desired `h B H2` term is allowed.

## Corrected selector scope

Spin10 center/vector-index parity at either site requires 1+Nlink to be even, so a left vector and a right vector require an odd number Nlink of bifundamental tensors, including epsilon contractions. Z2 invariance requires an even number NOmega of odd identity links. Therefore NB=Nlink-NOmega is odd, so every allowed connected path contains at least one even missing-VEV B link.

The explicit word census checks every odd link length through `9`
and finds no connected-path counterexample.

The full invariant ring nevertheless fails at degree six:

`(h_L^T Omega H2_R) Tr(A_L B Omegabar^T)`.

It is gauge invariant and Z2-even, and `Tr(A0 B0)=-6`.
It therefore becomes a direct `h H2` mass. Pure-link determinant and cofactor contractions have only
even B coefficients in the weak block, but the disconnected adjoint trace evades that protection.

## Filter ranks

The exact 40-coordinate filter matrix has rank `36` and nullity
`4`. Color rank is `24` with no kernel; weak rank is
`12` with nullity `4`. Adding the forbidden direct
`h H2` control raises the full rank to `40`.

## Running and fail-closed boundary

The minimum filter/link ledger has per-site `b_L=29`
and `b_R=7`; the left pole is only
`165.524` times matching.
Transplanting the R1 source raises the left beta coefficient to `53`
and lowers its pole ratio to `16.372`.

The three required bifundamentals already add `300`
chiral coordinates and index 30 to each site before the source and drivers are completed. The missing-VEV
alignment of the bifundamental, unwanted diagonal `1+54` components, full product-group Hessian, matter
operators, thresholds and perturbativity are open. No result from the one-site R1 action is promoted.

The theory-space mechanism is motivated by the four-dimensional moose construction of
[Arkani-Hamed, Cohen and Georgi](https://arxiv.org/abs/hep-th/0104005).
