# SUSY V50 second-profile and Clebsch audit

Status: `V50_SECOND_PROFILE_STRONG_COLLAR_OBSTRUCTION_AND_EXACT_SYMPLECTIC_REMATCH_CERTIFIED__COMPONENT_TENSOR_COVERAGE_PARTIAL__G2_FAIL_CLOSED`  
Core SHA-256: `58d96f2b01a0ca5b63afc8d825be43c9c89f9efad8d1d903c54f88b4a6d2d323`

## Result

The corrected strong collar has `Hc(s)=-(s/epsilon) Lambda H`. Consequently Hc-Hc and odd-profile H-Hc operators are leading O(1) data. The generalized pencil contains an independent leading odd-profile generator `C`; it is not set to zero by parity.

Two normalized profiles were integrated independently. For noncommuting strong blocks, the transfer difference tends to a nonzero thin-wall value (`0.1110746`), while the commuting control decreases by a factor `0.1217435`. The obstruction consists of ordered `[Xi,C]` and nested-commutator profile moments. The exact remedy `C_T=T_square T_smooth^-1` rematches to residual `2.48e-16` and is symplectic to `2.34e-14`. Since the complete Hamiltonian blocks span `sp(2n)`, it can be represented locally by Hamiltonian layers; its coefficients remain profile-dependent renormalized Wilson data rather than predictions.

## Component-data audit

The repository contains more than abstract D5 data: normalized `16x16x10`, `16x16x126bar`, and `16x16barx1` tensors can instantiate the matching family-current subset, and selected Cartesian 210-126/Phi-Sigma projector families are reusable in their named channels. However, these files do not form one convention-locked package covering every retained 10-H/Hc source portal, conjugate holomorphic channel, and normal-derivative vertex. Therefore this is a finite partial component certificate, not the complete physical Wilson array.

## Gate recommendation

`C1 PARTIAL; C2 PASS; C3 PARTIAL; C4 PASS; C5 FAIL; C6 fixed-order PASS; C7 PARTIAL.`

**Keep G2 open.** Closure requires a frozen regulator/renormalization prescription, a complete leading counterterm census derived from the superspace action, normalized component tensors for every retained portal, and their explicit contraction into the Wilson array.
