# V56-R1 M-dressed-B topology / Hessian audit

Status: `V56_R1_ZERO_NEW_FIELD_M_DRESSED_B_TOPOLOGY__A_EQUALS_L_NOT_B__EXACT_FD_FLAT_EFFECTIVE_SOURCE_RANK143_KERNEL33__DYNAMICAL_229_COORDINATE_H191_NULL38_EQUALS34_GAUGE_PLUS4_WEAK__COMPLETE_RENORMALIZABLE_U1_CENSUS_HAS_61_OPERATORS_AND_OMITTED_DRIVER_COUPLINGS__RENORMALIZABLE_FILTER_ROBUST_BUT_FORCED_DEGREE4_KhAH2_AND_LKhH2_FILL_WEAK_RANK16__ALL_ORDER_EFT_TOPOLOGY_REJECTED__NO_GATE_PROMOTION`

Core SHA-256: `700122eddf3e303c760030c6346402489bc0bc6c9814f7ac6f17519019e16684`

## Minimal topology change

No field or Spin(10) representation is added.  Four B-containing source terms are changed:

- `M B^2 -> T B^2`
- `M A B -> M^2 A B/Lambda`
- `E A B -> M E A B/Lambda`
- `E B^2 -> M^2 E B^2/Lambda^2`

The exact charge solution is `q(E,A,B,L,M,T)=(-2,1,3,1,-2,-6)`.  Thus the
V55 equality becomes `q(A)=q(L)=1 != q(B)=3`.  The required `h B H2` is neutral,
while `h A H2` and `L h H2` each have charge
`-2` and are forbidden.

Simply deleting the charge-linking cubics does not work: the only nontrivial exact
one-cubic cross branch has source rank 131 and twelve physical zero modes.  The dressed
terms retain their effective Hessian at the unit-spurion vacuum.

## Exact declared-action Hessian

The effective 176-coordinate source remains exactly F/D-flat with rank
`143` and nullity `33`, equal to
its Spin(10) orbit.  Recomputing all M/T derivatives changes the source gradient to
`[0, 0, -75, 420, 2415, 2700, 0]`, fixes driver VEVs to
`[-1920, 75, 1350, 420, 75, 0]`, and leaves every spurion F residual zero.

The full declared `229`-coordinate action has Hessian rank
`191` and nullity `38`.  An explicit
annihilated span proves the kernel is exactly 34 gauge plus four weak-Higgs modes, with
zero extra modes.

## Symmetry-completion boundary

The complete degree-three SO(10)xU(1) census contains `61`
operators: `47` singlet monomials,
`11` singlet-times-bilinear operators, and
`3` pure non-singlet cubics.  It permits
`D3 A^2`, `D4 A^2`, `D5 A B`, and `D6 H1 barh`, among other singlet-sector terms omitted
from the declared witness.

At strictly renormalizable order the filter itself is robust: its only extra term is
`D6 H1 barh`, which merely renormalizes the existing link.  Its generic weak rank remains
12 and its weak nullity remains four.

## Fatal all-order stress test

The renormalizable result does not survive the EFT completion.  Two exact total-degree-four
invariants are already forced:

- `K h^T A H2/Lambda`
- `L K h^T H2/Lambda`

Both are neutral.  The first uses the standard `10 x 45 x 10` contraction; the second uses
the vector bilinear.  At the exact vacuum each raises the weak rank from 12 to 16.  Their
weak determinants are respectively
`6561` and
`1`.

The proposed degree-five `h^T A^3 H2` and `L h^T A^2 H2` chains are also exact invariants
and also give weak rank 16.  A complete E/A/B matrix-chain and nonzero-VEV-singlet search
through total degree eight confirms that the first fatal degree is
`4`.  Moreover, the required charge equations force both
degree-four classes factorwise for every ordinary additive selector retaining this topology.

## Verdict

This is an exact mathematical certificate for the renormalizable truncation, but the
all-order M-dressed-B topology is rejected.  No gate is promoted.  A successor must change
the K/L driver relations or abandon this charge solution; adding messengers alone cannot
remove the forced degree-four fillers.
