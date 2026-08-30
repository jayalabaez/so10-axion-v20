# SUSY V50 Clifford tensor extension

Status: `V50_NORMALIZED_120_45_210_CLIFFORD_MAPS_CERTIFIED__FULL_PS_BRANCHING_AND_PHI_SIGMA_120_126_ARRAYS_OPEN__G2_FAIL_CLOSED`  
Core SHA-256: `697957744751578a7db6a749385b3b6dbee4d9e17871a953b870fd23c9a37eab`

## Newly certified maps

- `16x16_to_120`: shape [120, 16, 16], Gram `0`, covariance `0`
- `16x16bar_to_45`: shape [45, 16, 16], Gram `0`, covariance `0`
- `16x16bar_to_210`: shape [210, 16, 16], Gram `0`, covariance `0`

All maps use the repository's charge-conjugation matrix, chirality assignment, increasing Cartesian-index basis, and ordered-pair Hilbert–Schmidt metric. Together with the upstream 10, 126bar and singlet tensors, this closes the missing Clifford representation channels.

## Remaining irreducible C7 blocker

The full `Phi(210) x Sigma(126) -> 120,126` arrays still require exhaustive Gram/covariance emission. More importantly, the repository does not yet contain common-phase unitary Cartesian-to-PS branching matrices for 120, 126/126bar and 210 tied to the V49 H/Hc trace convention. Without them the tensors cannot be contracted entry-by-entry with the PS kernel. G2 therefore remains open.
