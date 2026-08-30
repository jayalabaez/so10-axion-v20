# V41 U(1)F-to-Z9 source-sector audit

Status: `V41_U1F_TO_Z9_RENORMALIZABLE_SOURCE_BRANCH_AND_ANOMALON_MASSABILITY_CERTIFIED_ON_A_CANONICAL_SUSY_BRANCH__EMBEDDING_KAEHLER_SOFT_AND_FULL_THEORY_GATES_FAIL_CLOSED`

This is a source-level existence calculation for the V40 `U(1)_F -> Z9`
selector, not a complete Pati--Salam theory or a full G-gate closure.

## Concrete renormalizable source

The declared source is

`W_F = kappa STheta(ThetaPlus ThetaMinus-mu_F^2)`

`+ ThetaPlus[L0 lambdaL Lminus9 + lambdaMinus27 Eminus2 Eminus7]`

`+ ThetaMinus[R0 lambdaR Rplus9 + lambda45 E4 E5 + lambda36 E3 E6]`

`+ y1 Q H Fc + y2 F Sc NDirac + M_F F Fc`.

All 10 listed terms are neutral under `U(1)_F`, `Z9`,
`Z5610`, and the supplied PQ charge, and carry superpotential `Z4R` charge
two.  The `F/Fc` pair is a vectorlike tree-level messenger: eliminating it
gives `-(y1 y2/M_F) Q H Sc NDirac`.

## Canonical F/D-flat branch

At zero host backgrounds and zero anomalon/messenger VEVs, choose
`<STheta>=0` and `<ThetaPlus><ThetaMinus>=mu_F^2`.  The canonical D equation
has a solution even with a finite FI datum; at `xi_F=0`,
`|ThetaPlus|=|ThetaMinus|=v_F`.  The nonzero VEV charges are `+9,-9`, whose
gcd is `9`;
the unbroken gauge group is exactly `Z9`.

For full-rank `lambdaL`, `lambdaR`, and nonzero singlet couplings, all listed
anomalon pairs acquire masses proportional to `v_F`.  The stabilizer/radial
mode is massive, the relative Theta mode is eaten by the massive `U(1)_F`
vector multiplet, and the `F/Fc` messenger has mass `M_F`.

The ordinary anomaly recheck totals are `{'SU4': 0, 'SU2L': 0, 'SU2R': 0, 'gravity': 0, 'cubic': 0}`.

## What is still open

`STheta`, `X`, and `Zp` have the same listed PS, `U(1)_F`, `Z4R`, `Z5610`,
and PQ signatures.  Therefore the existing product symmetries allow terms
such as `X ThetaPlus ThetaMinus`; the isolated source is not a protected
separation from the host driver sector.  Its consequence is:

> The isolated source superpotential is an existence construction, not a symmetry-protected separation from the existing X/Zp driver sector.  A full V41 source must either solve the coupled F equations or provide an additional UV/sequestering mechanism and audit every resulting operator.

An arbitrary Kahler/soft sector can also destabilize an anomalon direction.
The branch preserves `Z9` only while every field whose `U(1)_F` charge is not
a multiple of nine remains at zero.  No full Kahler/soft global vacuum,
product-anomaly completion, pole spectrum, flavour fit, or G gate is claimed.

Core SHA-256: `6ee1a126abe5b20eb308602c0cd95d0b239101fe3cbc1ebe33817f458976507d`
