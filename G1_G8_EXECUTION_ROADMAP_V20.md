# SO(10) axion v20 — executable G1–G8 roadmap

**Status:** `G1_G8_EXECUTION_ROADMAP_READY__G1_G2_CLOSED__G3_PARTIAL`

G1 and G2 are closed and the exact G3 witness is a physical saddle. The remaining program is dependency ordered; G3 cannot close until a tachyon-free stationary member survives BFB and competing-extrema tests.

## Critical path

`G1 → G2 → G3/G4/G5 → G6 → G7 → G8`

## Gate ledger

| Gate | Status | Immediate blocker | Issue |
|---|---:|---|---:|
| G1 | CLOSED | none | #176 |
| G2 | CLOSED | none | #176 |
| G3 | PARTIAL | find a tachyon-free stationary member, then prove BFB and global preference | #178 |
| G4 | PARTIAL | positive quotient spectrum at a surviving G3 member | #178 |
| G5 | PARTIAL | copositivity/stratified BFB proof for the complete G2 tensor potential | #86 |
| G6 | PARTIAL | complete positive gauge-quotiented scalar spectrum with SM irreps and mixing | #106 |
| G7 | OPEN | complete source-validated SO(10)+210 two-loop beta system and independent reproduction | #126 |
| G8 | PARTIAL | unique G3 vacuum, G6 spectrum, G7 running, mass-basis flavour/Wilson tensors, phases, and uncertainties | #106 |

## Execution tasks

### W1-G1-MOLIEN — `COMPLETED`

- Gates: `G1`
- Issue: `#176`
- Deliverable: complete mixed Hilbert/Molien series and independent tensor representatives
- Acceptance: multiplicities, independence, syzygies, conjugation, and normalizations are machine verified

### W2-G2-PROJECTION — `COMPLETED`

- Gates: `G2`
- Issue: `#176`
- Deliverable: single canonical component potential and operator-provenance graph
- Acceptance: every component entry traces to one normalized G1 invariant with correct dimension and charge

### W3-G3G5-EW-BACKREACTION — `EXECUTED_IN_THIS_CHANGE`

- Gates: `G3, G5`
- Issue: `#125`
- Deliverable: all reduced h^2 r_i^2 portals, mass retuning, radial stationarity/BFB, and tuning bounds
- Acceptance: positive quartic form and Hessian, exact target stationarity, fail-closed full-tensor flags

### W3-G3-FULL-STATIONARITY — `EXECUTED__STATIONARY_SADDLE`

- Gates: `G3`
- Issue: `#178`
- Deliverable: all-component stationarity, physical Hessian classification, and stable-family search
- Acceptance: a tachyon-free stationary member is below every enumerated boundary and symmetry-enhanced extremum

### W3-G4-FULL-QUOTIENT — `EXECUTED__QUOTIENT_SADDLE`

- Gates: `G4`
- Issue: `#178`
- Deliverable: normalized combined SO(10) to U(1)_EM gauge tangent basis and quotient Hessian
- Acceptance: exact gauge-null count and no non-axion zero or negative physical modes

### W3-G5-FULL-BFB — `READY_ON_CLOSED_G1_G2`

- Gates: `G5`
- Issue: `#86`
- Deliverable: large-field-stratum BFB/copotivity certificate for the complete potential
- Acceptance: every asymptotic field direction is covered without random-scan substitution

### W4-G6-SPECTRUM — `BLOCKED_ON_G3_G4_G5`

- Gates: `G6`
- Issue: `#106`
- Deliverable: all physical scalar eigenmasses, SM irreps, multiplicities, mixings, and uncertainties
- Acceptance: positive spectrum, complete provenance, basis invariance, and no SUSY matrix contamination

### W5-G7-TWO-LOOP — `BLOCKED_ON_G6_AND_EXTERNAL_VALIDATION`

- Gates: `G7`
- Issue: `#126`
- Deliverable: complete two-loop betas, component matching, running VEVs, and two implementations
- Acceptance: independent calculations agree within declared tolerances

### W6-G8-PROTON — `BLOCKED_ON_G3_G6_G7`

- Gates: `G8`
- Issue: `#106`
- Deliverable: mass-basis Wilson coefficients, running, hadronic matching, phases, interference, and uncertainties
- Acceptance: one uniquely selected vacuum produces the reported lifetime distribution

## Scientific claim boundary

A mathematically consistent candidate, a novel calculation, and an empirical discovery are distinct. No discovery claim is permitted without independent review and experimental evidence.
