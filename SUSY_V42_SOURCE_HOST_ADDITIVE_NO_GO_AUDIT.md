# V42 source–host additive-separation no-go

Status: `V42_ADDITIVE_SOURCE_HOST_SEPARATION_NO_GO_CERTIFIED_FOR_NEUTRAL_PARAMETERS__COUPLED_VACUUM_AND_SPURION_EXTENSIONS_FAIL_CLOSED`

The V41 `U(1)_F -> Z9` source is a valid isolated canonical-SUSY
construction, but it is not symmetrically separated from the existing V40
`X` and `Zp` driver system.  This audit proves that an extra additive label
cannot supply that separation while the present naked linear terms are kept.

## Starting ledger

`STheta`, `X`, and `Zp` have identical V40 signatures:
`{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}`,
`{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}`, and
`{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}`.  All
36 existing renormalizable V40
terms pass the old product check.  The following source–host mixings also
pass it:

| Bridge | `(U1F, Z5610, PQ, Z4R)` charges | Allowed |
|---|---|---|
| `X_ThetaPlus_ThetaMinus` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `Zp_ThetaPlus_ThetaMinus` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `X_STheta_STheta` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `Zp_STheta_STheta` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `STheta_X_X` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `STheta_X_Zp` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |
| `STheta_Zp_Zp` | `{'u1f': 0, 'z5610': 0, 'pq': 0, 'r4': 2}` | yes |

## Exact additive no-go

For an arbitrary additive factor `A`, let `w` be the superpotential target
charge.  Neutral-parameter naked linear terms require
`q(STheta)=q(X)=q(Zp)=w`.  The required stabilizer cubic
`STheta ThetaPlus ThetaMinus` then requires
`q(ThetaPlus)+q(ThetaMinus)=0`.  Consequently both
`X ThetaPlus ThetaMinus` and `Zp ThetaPlus ThetaMinus` have charge `w` and
are allowed.  The proof applies componentwise to any product of additive
factors, including ordinary/discrete/R-type choices.  It uses only a required
subset of the source/host ledger, so imposing the remaining V40 host terms
cannot evade the implication.

An exhaustive finite check of cyclic factors `Z_N`, `2 <= N <= 64`, tested
89439 consistent assignments and found
0 counterexamples.

## Consequence for the V41 branch

The generic allowed piece is

`W = kappa STheta(ThetaPlus ThetaMinus-mu_F^2) + lambda_X X ThetaPlus ThetaMinus + lambda_Z Zp ThetaPlus ThetaMinus + W_host`.

On the isolated-source × unperturbed-host branch,
`F_X=lambda_X mu_F^2` and `F_Zp=lambda_Z mu_F^2`.  Thus that product branch
is not generically F-flat for nonzero `mu_F^2`; setting both lambdas to zero
is a tuning, not a symmetry consequence in this class.  A fully coupled
source–host F/D solution may still exist, but has not been solved or claimed.

A charged-spurion/dynamical-linear-term mechanism falls outside the theorem
and is a new model requiring a full residual-symmetry, anomaly, induced-term,
mass-rank, and coupled-vacuum audit.  No G gate is closed here.

Core SHA-256: `1c84d92745aa78d8eef7b9dad7f3644abc84a388d8260ba04985b7026a6c9c29`
