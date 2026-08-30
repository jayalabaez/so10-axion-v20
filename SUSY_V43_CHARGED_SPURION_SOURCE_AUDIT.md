# V43 charged-spurion source audit

Status: `V43_CHARGED_SPURION_F_TERM_SOURCE_SEPARATION_CERTIFIED__MINIMAL_GAUGED_D_FLAT_AND_ANOMALY_COMPLETION_NO_GO_CERTIFIED__NO_FULL_GATE_CLOSED`

## What the spurion changes

V42 assumed a neutral numerical `STheta` linear coefficient.  This minimal
redesign instead uses

`W_source = kappa STheta ThetaPlus ThetaMinus + M_Omega STheta Omega`

with `q_S(STheta)=+1`, `q_S(ThetaPlus)=0`,
`q_S(ThetaMinus)=q_S(Omega)=-1`, while `X` and `Zp` remain `U(1)_S` neutral.
The old naked `STheta` term is removed; its effective coefficient is
`M_Omega<Omega>`.  The anomalon charges are reassigned only as needed to keep
their old Theta-mediated masses allowed.  All 35
retained V40 terms plus the new mixing pass every listed charge check.

The degree-one-to-three abelian-invariant superset contains
`3` source--host rows and
`0` rows involving an
`X/Zp` driver.  The three raw source--host rows each contain exactly one
non-singlet Pati--Salam host factor and are therefore excluded by a necessary
PS-singlet test; the potentially PS-invariant list and the direct `X/Zp` list
are both zero.  This is stronger than a gauge-contraction scan for the
surviving rows, since a gauge invariant portal would first have to be abelian
invariant.

For the restricted all-order ring containing only one `X/Zp` and source
fields, `U(1)_F` requires equal `ThetaPlus/ThetaMinus` powers and `U(1)_S`
then requires `n(STheta)=n(Theta pair)+n(Omega)`.  Thus every nontrivial
allowed portal contains `STheta` and vanishes on the source F branch.  This
does *not* classify arbitrary higher-dimensional operators with V40 host
fields.

## Coupled F equations

With all anomalons at the origin, the source equations are

`F_STheta=kappa ThetaPlus ThetaMinus+M_Omega Omega`,
`F_ThetaPlus=kappa STheta ThetaMinus`,
`F_ThetaMinus=kappa STheta ThetaPlus`, and `F_Omega=M_Omega STheta`.

Therefore `STheta=0` and
`Omega=-(kappa/M_Omega)ThetaPlus ThetaMinus` give zero source F terms.
Because the renormalizable source--host portal scan is empty, every F-flat
host solution can be combined with this formal source branch.  The original
V41 Theta-mediated anomalon mass matrices remain allowed and have their old
full-rank witness.  This is a genuine F-term result, summarized in the audit
as `True`.

## Why it is not yet a new gauge theory

For a gauged `U(1)_S` and zero FI term, `D_F=0` sets
`|ThetaPlus|^2=|ThetaMinus|^2=v^2`, while the same F branch gives

`D_S/g_S=-v^2-|Omega|^2<0`.

So the minimal gauged field set has no zero-FI D-flat branch.  A positive
constant FI term gives a formal branch with
`x=(-1+sqrt(1+4 alpha xi_S))/(2 alpha)` and retains `Z9` because the nonzero
`U(1)_F` VEV charges are `+9,-9` and `Omega` is neutral.  But that FI datum
and a consistent `U(1)_S` UV completion are extra assumptions.

Indeed the raw new local rows are `{'PS_squared_U1S': {'SU4': 0, 'SU2L': 0, 'SU2R': 4}, 'gravity_U1S': 9, 'U1S_cubed': 9, 'U1F_squared_U1S': -56, 'U1F_U1S_squared': -2}`; they do not
cancel.  This audit does not silently invoke a Green--Schwarz or spectator
repair.

The most obvious no-FI compensator, a neutral `OmegaBar` of `U(1)_S=+1`,
also fails: both `X Omega OmegaBar` and `Zp Omega OmegaBar` are allowed.  They
give `partial_X W_host + lambda_X Omega OmegaBar` and its `Zp` analogue, so a
nonzero compensator VEV re-sources the host driver equations.

## Verdict

The charged spurion is a real escape from the *F-term algebra* of V42, but
not a completed source theory.  It identifies the required next physics:
an anomaly-free, D-flat, non-neutral-compensator or UV/inflow completion that
retains the portal proof after all new VEVs and higher operators are audited.
No G gate is closed.

Core SHA-256: `2b94159dac9311f14790956bd8fbbf5222ea7c4dfa2aa4a9091975e7bc74de8d`
