# SO(10) axion v20 — executable G1–G8 roadmap

**Authoritative claim boundary:** this is a candidate-theory closure program. A novel calculation is not an empirical discovery, and no new-particle claim is permitted without independent review and experimental evidence.

## Critical path

`G1 → G2 → G3/G4/G5 → G6 → G7 → G8`

No downstream gate may be called closed while a dependency remains incomplete. A mathematically correct terminal result may be `THEORY_FAIL`.

## Current gate ledger

| Gate | Status | Completed subtheorems | Terminal blocker | Tracking |
|---|---:|---|---|---:|
| G1 | CLOSED | Exact 18-family tensor ring; 64 invariant directions; 91 real parameters | None | #176 |
| G2 | CLOSED | Exact potential, gradient, and 486x486 Hessian on the canonical chart | None | #176 |
| G3 | PARTIAL | Full 486x91 stationarity; exact 486x486 witness Hessian; 449-mode quotient; saddle/no-witness search | Find a tachyon-free stationary member, then prove BFB and global preference | #178 |
| G4 | PARTIAL | Combined 36-direction SO(10)→U(1)EM basis; independent PQ axion; full witness quotient | Positive quotient spectrum at a surviving G3 member | #178 |
| G5 | PARTIAL | Pure/reduced BFB; neutral and fixed-background H10 BFB; five-field radial EW-portal BFB | Stratified/copotivity proof for the complete G2 potential | #86 |
| G6 | PARTIAL | Selected triplet Clebsches and Nambu blocks; signed diagnostics; fixed-background H10 spectrum | Complete positive physical scalar spectrum with SM irreps, mixing, and uncertainties | #106 |
| G7 | OPEN | Verified one-loop chain and calibrated diagnostic two-loop proxy | Source-validated SO(10)+210 two-loop system, complete G6 matching, and independent reproduction | #126 |
| G8 | PARTIAL | Fail-closed gauge envelope; scalar stress tests; conditional interference diagnostics | Unique G3 vacuum, G6 spectrum, G7 running, mass-basis flavour/Wilson tensors, phases, and uncertainties | #106 |

## Execution waves

### Wave 1 — Close G1

1. Compute the complete charge-filtered mixed Molien/Haar or equivalent Hilbert series.
2. Prove multiplicities, algebraic independence, conjugation structure, and syzygies.
3. Construct canonical tensor representatives and kinetic normalizations.
4. Reproduce the count with an independent implementation.

**Acceptance:** no guessed multiplicity or Clebsch; every G2 coefficient has a normalized machine-checkable G1 witness.

### Wave 2 — Close G2

1. Define one canonical PS/SM component basis.
2. Project every G1 invariant into the component potential.
3. Generate symbolic gradients, Hessian blocks, and operator-provenance maps.
4. Test dimensions, Hermiticity, rephasings, permutations, and forbidden zeros.

**Acceptance:** every component matrix entry traces to one allowed normalized invariant.

### Wave 3 — Close G3/G4/G5

1. Solve all amplitude and phase stationarity equations.
2. Enumerate boundary, symmetry-enhanced, and competing extrema.
3. Build the combined SO(10)→U(1)EM gauge tangent basis and quotient the Hessian.
4. Require no non-axion physical zero or negative modes.
5. Prove BFB on every large-field stratum of the complete potential.

**Acceptance:** target vacuum is stationary, globally preferred, gauge-quotiented, and bounded.

### Wave 4 — Close G6

1. Diagonalize the complete non-SUSY component Hessian.
2. Emit each SM-irrep eigenmass, multiplicity, mixing, uncertainty, and provenance.
3. Reject tachyonic or singular points before threshold/proton calculations.

**Acceptance:** complete positive physical spectrum with no SUSY-fermion/gaugino contamination.

### Wave 5 — Close G7

1. Derive or ingest the complete two-loop gauge/Yukawa beta functions for the actual field content.
2. Match every G6 component at its eigenmass and run VEVs/Yukawa matrices.
3. Record scheme conversions and uncertainties.
4. Reproduce with an independent symbolic or numerical implementation.

**Acceptance:** two independent calculations agree within declared tolerances.

### Wave 6 — Close G8

1. Rotate gauge and scalar interactions into the physical mass basis.
2. Compute channel Wilson coefficients, running, hadronic matching, phases, and interference.
3. Propagate CG, threshold, flavour, RGE, and hadronic uncertainties.
4. Compare all channels with current limits without converting a conditional failure into whole-model exclusion.

**Acceptance:** one uniquely selected physical vacuum produces the reported lifetime distribution.

## Executed in PR #129

The reduced radial fields `(P_210, Delta_R, S, Phi17, h_EW)` now include all four nonzero `h^2 r_i^2` portals. The implementation:

- reconstructs the equivalent unshifted quadratic mass parameters;
- verifies target stationarity;
- proves radial BFB and Hessian positivity using `H=2 diag(v) B diag(v)`;
- quantifies the enormous Higgs-sector cancellation from generic portals;
- derives portal bounds for a tuning budget of ten;
- verifies a sequestered benchmark;
- keeps complete tensor backreaction, global vacuum, whole-model validation, and discovery flags false.

This closes a reduced G3/G5 subgate only. It also shows that mathematical existence does not solve the electroweak hierarchy problem: a UV sequestering or hierarchy mechanism is still required.
