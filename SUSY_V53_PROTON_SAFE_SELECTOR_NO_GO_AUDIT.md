# V53 proton-safe selector audit

Status: `V53_EXACT_DEGREE4_SPIN10_INVARIANT_CENSUS__CYCLIC_AND_PRODUCT_SELECTOR_NO_GO__REQUIRED_HIGGS_YUKAWA_AND_DOUBLE_SEESAW_TERMS_FORCE_F16_POWER4_ALLOWED__R_SYMMETRY_SOURCE_MASS_CUBIC_CONFLICT__SEARCH_N2_TO64_EMPTY__PROTON_SAFE_SELECTOR_REQUIRES_ACTION_CHANGE__NO_GATE_PROMOTION`

## Verdict

No cyclic non-R or conventional discrete-R selector can make the unchanged V52
`54+45+16+bar16+10+4N+3(16F)` action proton-safe while retaining every declared
source, DT, Yukawa and double-seesaw term.  This is an exact operator-congruence
no-go, not a failed guess at charges.

The exact D5 census through superpotential degree four contains
`66` nonzero
multidegrees and `365`
invariant directions.  Degree-four `F16^4` alone has multiplicity
`6`
after the three family copies are included.  Degree counts are `{'1': {'multidegrees': 1, 'invariant_multiplicity': 4}, '2': {'multidegrees': 6, 'invariant_multiplicity': 17}, '3': {'multidegrees': 15, 'invariant_multiplicity': 66}, '4': {'multidegrees': 44, 'invariant_multiplicity': 278}}`.

## Exact obstruction

- Non-R: `FFH` and `H2` imply `4 qF=0`, exactly the `F^4` charge.  With an
  unbroken spinor-Higgs VEV, `F barC N` and `NN` independently force the same result.
- R: `E2` and `E3` require `qE=0` and `qW=0`; a conventional `qW=2` symmetry
  therefore has only the `N|2` cases and reduces to the non-R obstruction.
- Product groups do not help because both statements hold factor by factor.

The exhaustive check over every `Z_N` and `Z_N^R` for `2<=N<=64` finds zero
assignments that allow the required terms and forbid `F16^4`.  No candidate
survives long enough for anomaly cancellation to rescue it.

## Smallest honest escape

The action must change: replace the tuned `H2/EH2` DT block, replace four
Majorana singlets by at least three Dirac pairs, and construct an anomaly-safe
parent/spectator sector.  The report includes a `Z5` operator-level illustration,
but explicitly does not call it anomaly complete.

No G2, G7 or G8 gate is promoted.

Core SHA-256: `3ad9373cb18224f72bfcedc0457378c996966cc5cbef5e4e3f4f3772e592e58b`
