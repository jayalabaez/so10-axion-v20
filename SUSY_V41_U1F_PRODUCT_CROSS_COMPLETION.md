# V41 U(1)F product cross-anomaly audit

Status: `V41_U1F_X_H_CUBIC_CROSS_BLOCK_CANCELLED_AT_P_PB_THRESHOLD__RESIDUAL_PRESERVING_THETA_THRESHOLD_NO_GO_PROVED__PRODUCT_UV_COMPLETION_FAIL_CLOSED`

This is a bounded anomaly calculation, not a complete theory or a promoted G1
solution.  It separates an exact obstruction for a residual-preserving threshold
from a conditional later-threshold workaround.

## Exact cubic cross block

| Triangle row | V40 | New singlets | Net |
|---|---:|---:|---:|
| F_X_squared | -360 | 360 | 0 |
| F_squared_X | -270 | 270 | 0 |
| F_H_squared | 0 | 0 | 0 |
| F_squared_H | 0 | 0 | 0 |
| F_X_H | 6 | -6 | 0 |

The four new PS-singlet chiral fields are massed by
`Pb ChiAPlus ChiAMinus` and `P ChiBPlus ChiBMinus`.  Every listed continuous,
Z9, Z5610, PQ, and Z4R term check passes.  On a nonzero P/Pb background the
two 2-by-2 blocks have full rank four.  The construction uses exactly two mass
pairs in the stated class; one P/Pb pair would require the non-square
`f^2=135` to produce the required `C_F^2X=+270`.

The combined finite audit still passes: Z9 linear residue
`0`, cubic residue
`0`, and both displayed
Z9-Z5610 residues are zero.

## What is obstructed

For a threshold massed only by an X/H-neutral Theta field,
`(f,x,h)` pairs with `(±9-f,-x,-h)`.  Thus
`Delta C_FXH=±9*x*h`, always zero modulo nine.  V40 needs an increment
`-6 = 3 mod 9`, so no
finite collection of such residual-preserving ordinary pairs can solve it.

A single compact axion shifting only by the minimal F charge nine also fails
in the stated integer-level convention: `9 k_XH=-6` has no integer solution.
A specified multi-axion/topological response remains a distinct, unprovided
possibility.

## Boundary

The workaround is deliberately outside the V38 unbroken-Z66 theorem: P/Pb
carry X charges `+2/-2`, so their VEVs break that old direction.  It preserves
the V40 Z9 proof only conditionally, assuming the four new threshold scalars do
not condense.  It does not cancel the remaining X/H, Z4R, gravitational,
global/bordism, vacuum, running, flavour, cosmology, or mixed-operator rows.
For example its non-F increments are `{'X_cubed': -450, 'H_cubed': 0, 'X_squared_H': 40, 'X_H_squared': -2, 'X_gravity': 0, 'H_gravity': 0, 'Delta_b_F_N1SUSY': 306, 'Delta_b_X_N1SUSY': 254, 'Delta_b_H_N1SUSY': 2, 'Delta_b_XH_N1SUSY': -20}`.

`F^2 X H` is shown only as a degree-four diagnostic, not treated as a 4D
triangle anomaly.

References: [Ibanez](https://arxiv.org/abs/hep-ph/9210211),
[Gonzalez-Rey](https://arxiv.org/abs/hep-th/9602178), and
[Witten--Yonekura](https://arxiv.org/abs/1909.08775).

Core SHA-256: `20a38e9d31e8c68351bed352cbe881ef1390ee322b7056734260e8f79981e555`
