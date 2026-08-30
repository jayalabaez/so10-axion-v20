# V50 full same-action quadratic collar audit

Status: `V50_FULL_SAME_ACTION_QUADRATIC_COLLAR_DERIVED__A_XI_C_AND_O7_O8_IN_ONE_PATH_ORDERED_GENERATOR__VARIATIONAL_LAGRANGIAN_DOMAIN_AND_POSITIVE_ADMISSIBLE_CONE_CERTIFIED__UNDIVIDED_BULK_ENDPOINT_POLE_RESIDUE_WILSON_WITNESS_PASSES__C3_AND_QUADRATIC_C4_CLOSED__C7_COMPONENT_MATCHING_PARTIAL__G2_OPEN`

## Verdict

V50 removes the V49 quadratic strong-collar gap.  General symmetric `A`,
symmetric `Xi`, arbitrary `C`, and the independent O7/O8 normal-derivative
blocks now arise from one integration-by-parts-complete action, one
path-ordered transfer, and one variational endpoint domain.  The undivided
enlarged characteristic retains the endpoint auxiliary states and produces a
deterministic pole, residue, Euclidean-locality and Wilson witness.

**C3 passes at the declared quadratic-action level.  C4 passes on the
explicit positive admissible cone.  C7 remains partial, and G2 remains open.**
The missing C7 objects are normalized SO(10)-to-PS portal and
normal-derivative Clebsches plus the resulting physical component Wilson
array.  C2 and C5 are separate unresolved regulator/rematching clauses.

## One action and one generator

For `psi=(H,Hc)`, begin literally with

`Hc^T(I+R7) D5 H + (D5 Hc)^T R8 H`.

Define

```text
D = [[0,R8^T],[I+R7,0]],
J = D-D^T = [[0,-K^T],[K,0]],       K=I+R7-R8,
S = (D+D^T)/2,
Q = [[A,C^T],[C,Xi]]-m epsilon Z+S'.
```

Exact collar integration by parts gives

`L=psi^T J psi'/2-psi^T Q psi/2+[psi^T S psi/2]'`.

Thus `O7-O8` changes `J`, while `O7+O8` supplies the `S'` potential and the
retained endpoint counterterm.  The variational equation and Darboux map are

```text
J psi'=(Q-J'/2)psi,
z=diag(I,K^T)psi,
T_col=P exp integral_0^1 G_can(t,m) dt.
```

The three blocks

`G=[[C,Xi],[-A,-C^T]]`, with `A=A^T`, `Xi=Xi^T`,

span all of `sp(2n)`: the executable `n=4` basis has rank
36 out of the expected
36.
The representative profile is genuinely noncommuting, with commutator norm
`0.064212`.

## Variational domain and positive norm

In Darboux coordinates use the host graph `p0=P0 q0` and source graph
`p1=-P1 q1`.  Hermitian endpoint pencils make both graphs maximal isotropic
for the Green form `[u^dagger J0 v]_0^1`.  Energy-dependent rational pencils
are never treated as fixed boundary conditions: their positive-metric
auxiliary states remain in the enlarged domain and determinant.

The sufficient positive cone is:

1. `sigma_min K(t)>0` uniformly;
2. the full collar Kahler metric is positive, equivalently including the
   mixed-block Schur inequality;
3. direct endpoint `Z0,Z1` are positive semidefinite;
4. auxiliary endpoint `W0,W1` are positive definite.

The witness has `min sigma(K)=0.962123`,
full collar metric minimum eigenvalue `0.320388`,
and mixed Schur-complement minimum eigenvalue
`0.330344`.  This is a nonempty open
positive cone, not a claim that arbitrary Wilson coefficients are healthy.

The total real-slice J-unitarity residual is
`7.772e-16`.  Step doubling changes the
path-ordered transfer by `3.509e-05`.

## Undivided pole and Wilson witness

Let the total transfer be `[[R,P],[Q,T]]`.  With positive-metric auxiliary
states `(chi0,chi1)`, the certificate constructs the polynomial/entire block
system directly on `(q0,chi0,chi1)`.  Off auxiliary poles it obeys

`det F_full = det(H0-mW0) det(H1-mW1) det Gamma_reduced`

with maximum relative residual
`6.423e-16`.  No
factor is divided away in the spectrum calculation.

The first three positive signed roots are
`[1.1200300921052984, 1.2111016312759602, 2.5245205552627645]`.  The first is simple;
the full-matrix near-pole residue error is
`4.717e-06`.  The representative
same-action host response has norm
`4.83502` and the Euclidean
source-to-host ratio `||G(8i)||/||G(4i)||` is
`0.0171352`.

## Clause decision

- **C3 — `PASS_AT_DECLARED_QUADRATIC_ACTION_LEVEL`.** Every retained A,Xi,C and O7/O8 quadratic block now comes from one IBP-complete action, one path-ordered transfer, and one variational maximal-isotropic endpoint domain. Auxiliary wall states are retained.
- **C4 — `PASS_ON_EXPLICIT_POSITIVE_ADMISSIBLE_CONE_AT_QUADRATIC_LEVEL`.** Uniform K invertibility, positive full Kahler Schur complements, positive endpoint Z, and positive auxiliary W give a positive full quadratic norm. The deterministic same-action witness lies strictly inside this nonempty open cone.
- **C7 — `PARTIAL`.** The complete abstract A/Xi/C/O7/O8 transfer, undivided enlarged characteristic, pole residues and Wilson response are now same-action.

The transfer accepts either the finite-range V49 coefficient kernel or a
local constrained profile through the same `(A,Xi,C,R7,R8,Z)` callback.  That
interface does not itself decide C2.  A second independent profile rematch and
loop subtraction remain C5.

Therefore the full ledger stays **G1 closed; G2--G8 open (1/8)**.

Core SHA-256: `5b91b9f9c85241e09853892550c2323b3b84e27b972668c130917a2db2baa086`
