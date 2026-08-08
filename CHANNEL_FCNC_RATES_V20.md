# Channel-level FCNC rates — v20

**Status:** `CHANNEL_LEVEL_FCNC_RATES_IMPLEMENTED__UV_COMPONENT_MATCHING_AND_POINTWISE_LIKELIHOODS_OPEN`

## Hierarchical conditional benchmark

- BR(mu -> e a): 2.834978e-32
- BR(K+ -> pi+ a): 9.737785e-31
- Pointwise experimental likelihoods: **not implemented**

## Generation-dependent counterexample

- BR(mu -> e a): 1.951706e-07
- BR(K+ -> pi+ a): 3.650033e-11

## Remaining for closure

- derive component-specific left/right PQ currents after all thresholds
- propagate the complete portal-Yukawa posterior rather than two examples
- ingest the pointwise TWIST angular-asymmetry likelihood
- ingest the pointwise NA62 K+->pi+X limit curve and correlations
- include form-factor covariance and matching-scale uncertainty

## Verdict

The repository now computes explicit mu->e a and K->pi a partial widths and branching ratios from left/right mass-basis matrices. The hierarchical benchmark is conditionally testable, while a generation-dependent portal can be much more constrained. Full finite-model FCNC closure remains open because component-specific UV currents and pointwise experimental likelihoods are not fixed.
