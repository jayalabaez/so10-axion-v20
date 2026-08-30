# V37 non-anomaly gate audit

Status: `V37_NONANOMALY_AUDIT_COMPLETE__CANONICAL_GLOBAL_SUSY_BRANCH_AND_ANOMALON_RANK_CERTIFIED__NO_PHYSICAL_POLE_SOFT_RUNNING_PROTON_OR_LIKELIHOOD_CLOSURE`

This audit does **not** add a free soft benchmark. It separates exact
properties of the declared V37 EFT from data which the source does not
contain. The strict full-theory result remains **0/8** gates.

## Exact EFT subresults

- The anomalon tree mass block has determinant `a^2*b^2*c` and is
  generically rank 5 when `a*b*c != 0`.
- In the canonical global-SUSY truncation, the two-driver equations force
  `Sbc Sc=vPS^2` and `P Pb=fPQ^2` when `Delta != 0`; the representative has
  `F=D=0`. Since this potential is a sum of squares, it is a global
  zero-energy minimum **only in that truncation**. The radial holomorphic
  Hessian has generic rank 4.
- SARAH has live one- and two-loop supersymmetric RGEs, with one-loop PS
  coefficients `[1, 5, 9]`.

## Decisive boundaries

The source deliberately disables every soft term and declares only `GaugeES`;
there is no SPheno/boundary file. Thus it cannot produce a physical pole
spectrum, radiative EWSB solution, or a threshold-matched uncertainty band.

The external `Z4R` and `Z5610` assignments forbid bare `Q^4` and `Qc^4` in
the superpotential, but permit each of `X*Q^4/M^2, X*Qc^4/M^2, Zp*Q^4/M^2, Zp*Qc^4/M^2`.
These vanish on the canonical `X=Zp=0` branch but become ordinary
four-matter dimension-five superpotential operators if the drivers acquire
SUSY-breaking VEVs. Their Wilson flavour tensors are neither calculated nor
bounded. This prevents a proton-lifetime claim.

Likewise, symmetry permits independent flavour matrices such as `YQQ` and
`yNQ`; the allowed choices `YQQ=0` and `YQQ=y I` already give inequivalent
fermion spectra. No CKM/PMNS or joint likelihood is therefore predicted.

## Promotion rule

Do not close any remaining gate by assigning soft masses, thresholds, Wilson
coefficients, or data priors by hand. A genuine completion must derive them
from one microscopic source together with the Kähler/gauge-kinetic sector and
the full PS-to-SM matching calculation.

Core SHA-256: `5db7eb779af1a0c762fabb913bc14af03c18d01e30b53d46fb6838ed0a76dde4`
