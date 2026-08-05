# Corrected Phi-H-Sigmabar CGC campaign — v20

**Status:** `PHYSICAL_CGC_CAMPAIGN_CORRECTED__EFJX_BOUND_WITHDRAWN`  
**State:** `BLOCKED`

The PR #89 `8.8e29` Clebsch no-go is withdrawn. Aulakh Appendix E/F/J/X are mixed chiral-gauge fermion/gaugino matrices and their `g` is the SO(10) gauge coupling, not the superpotential `gamma` coupling.

The replacement direct calculation constructs the canonically normalized non-supersymmetric `10 x 126` map for

`lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c.`

with the complete `(p,a,omega)` singlet basis. Its numerical SVD agrees with a closed analytic `3+3+2+2` spectrum and independently matches the genuine published `gamma`-dependent chiral triplet/doublet Clebsches.

## Withdrawn result

- Former `|c_norm|` requirement: `8.807091841170979e29`
- Current value: `null`
- Reason: wrong E/F/J/X gauge/gamma comparison target
- `old_8p8e29_bound_valid`: `false`

## Remaining blockers

- `OPEN` complete non-supersymmetric invariant ring
- `OPEN` direct component mass-squared matrix using all invariants
- `OPEN` global stationarity, boundedness, and competing extrema
- `OPEN` gauge-projected full component Hessian
- `OPEN` physical thresholds and exact unique proton lifetime

The direct portal tensor is derived. The complete scalar theory is not.
