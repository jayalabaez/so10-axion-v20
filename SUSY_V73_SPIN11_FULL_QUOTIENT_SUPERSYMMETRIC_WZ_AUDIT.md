# V73 Spin(11) full-quotient supersymmetric WZ audit

Status: `V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT__V72_ROUTE_AND_MASTER_CORES_BOUND__EXACT_CHARACTER_AND_COCHARACTER_LATTICES__INHERITED_NORMAL_VECTOR_NORMALIZATION_PINNED__KAPPA_D_PURE_WZ_PERIOD_25_OVER_4__MINIMUM_PURE_MULTIPLIER_FOUR__F72_PURE_ORDINARY_WZ_REJECTED__CORRELATED_E5R_LEVEL_ONE_CLASS_INTEGRAL_BUT_FORCES_SU2R_TERM__OPTIONAL_FLAVOR_TERMS_EXACT__COMMON_U2_U3_RESIDUE_NU_AB_NONZERO__P0_NOT_AFFINE_AXION__AXINO_PARTNER_LEDGER_EXACT__PLAIN_OPPOSITE_SLOPE_TENSOR_REJECTED__TENSOR_BRIDGE_INFLOW_FRONTIER_SELECTED_UNACCEPTED__G1_TO_G8_OPEN`

Core SHA-256: `1ef4890b81885f5a16196865dd8772d9d3b70a20958829481c2397fd9b044c44`

## Exact full-quotient result

The full representation rules are `k+2x=0 mod 5` and `n+x+r=0 mod 2`,
with `x+f=0 mod 2` when the optional flavor quotient is installed.  The local
charge-five character is not a standalone line of the diagonal quotient.

V71's inherited convention is `fL=c1(N)=nu`, with the primitive Spin(2) root
equal to `nu/2`.  On the exact diagonal cocharacter,

`nu=1, ell=5/2, rhoR=1/2`.

Therefore the V72 pure class has period
`25/4` and its minimal pure
integral multiplier is
`4`.  The
U5tilde-restricted level-one check remains correct, but the isolated ordinary
full-quotient WZ term is rejected.  A spin/eta-refined invertible theory could
change this conclusion only after it is explicitly constructed.

The apparent period `25/8` obtained by inserting the primitive Spin root
`sigma=nu/2` while retaining `DeltaA=50` is only a hybrid convention.  A
consistent Spin-weight ledger uses `n=2qL`, doubles `DeltaA` to `100`, and
returns the same physical class `nu ell^2` and multiplier four.

## Correlated local repair

The honest associated bundle `E5R=1_(+5) tensor 2_R` has

`c2(E5R)=ell^2+c2(R)`.

Thus `nu c2(E5R)` is integral at level one, but it necessarily adds the
mixed normal-R term `nu c2(R)`.  With the flavor completion the class becomes
`nu[(ell+v)^2+c2(R)]`, adding X-F and F-squared terms as well.  These omitted
anomaly ledgers prevent acceptance.

The numerical bulk R coefficient remains open.  A provisional `11/16` attempt
is not certified because the total SU2R/isotropy phases, symplectic-Majorana
factor, and Rarita/tensor ghost characters have not been derived in one raw
equivariant calculation.  One conclusion is coefficient-independent: every
inherited bulk R source has the same corner lift, so a common coefficient `C`
leaves `(C+1,C-1)` after the correlated levels and cannot cancel both.  The E5R
route therefore requires a genuinely new antisymmetric `(-1,+1)` source and a
complete R-character computation.

## Exact corner mismatch

On the common U(2)xU(3),

`2 ell=A+B`, `2 ellprime=A-B`, and therefore
`ell^2-ellprime^2=A B`.

The opposite profile leaves `nu A B`.
Consequently a zero numerical coefficient sum does not construct one global
ordinary transfer cocycle.

Adding SU(5) characteristic terms cannot evade this result.  The unique
two-corner correction that glues is `+p1(V10)/4` at z00 and `-p1(V10)/4`
at z11.  That is the bulk Spin(11) gauge direction itself, so it cannot repair
the orthogonal anomaly.  Ordinary integrality of `p1(V10)/4` is not assumed.

## N=1 multiplet result

An affine axion chiral has homogeneous R=0 and an axino of normal charge
-1/2, with `I6=(-x^3+x p1)/48`.  One neutral R=2 fermion of charge +1/2 has
the opposite polynomial.  Their exact pair ledger is
`['0', '0']`, preserving the local
Delta=-10 condition.

A schematic flat-N1 descent contains the affine Kahler/Stueckelberg
combination, an A-dependent gauge kinetic term for the full correlated bundle,
and the Bardeen/generalized Chern--Simons term that preserves the fixed-group
gauge current.  In a provisional unit normalization it gives
`m00 k00=+1` and `m11 k11=-1`.  This is not yet the required curved
normal/Lorentz-R supergravity action: the axion period, large-rotation unit,
trace normalization, and off-shell embedding remain open.  The real axion
partner also shifts the boundary gauge kinetic function, whose positivity and
stabilization are uncomputed.

The provisional P0 is not the axion: it has the R=2/qpsi=+1/2 representation
type of a partner, but it is already counted in F72's base anomaly ledger and
cannot cancel a newly added axino.  With no new classical `nu^3` or
`nu p1(T)` axion couplings, no extra compensating fermions, and the inherited
Delta=-10 ledger unchanged, the minimal two-axion repair uses two new R=2
partners.  This field choice is not forced by supersymmetry alone.  Also,
`singular at P0=0; a nonzero charge-two P0 background breaks Z4R to Z2R, re-admitting the mu and 16^4 operator classes, and cannot be imported as a regular affine axion`.
Moreover P0 fails
the ordinary neutral-hyper center pattern:
`False`.

The selected structural frontier reuses the existing 6D tensor/linear
multiplet and explicitly includes a required new bridge/inflow sector with
perturbative curvature `-nu A B`.  Because `nu A B` is a nonzero free de-Rham
class, a torsion or zero-curvature eta refinement cannot erase it.  A spin/eta
realization carrying `-nu A B` is itself the bridge.  The pre-existing tensor
adds no new localized axino, but the unknown supersymmetric bridge may require
new boundary multiplets.  The plain opposite-slope tensor is rejected.

## Fail-closed decision

V73 retains V72's correctly scoped U5tilde-restricted result and rejects its extension to a pure full-quotient ordinary WZ counterterm.  The exact diagonal-cocharacter period is 25/4.  Correlated SU2R and normal-line completions are locally integral, and the N=1 axino/partner ledger can be balanced exactly, but their forced spectator anomalies are not cancelled. The plain opposite-slope tensor also fails by the nonzero common residue. The selected frontier is therefore the existing tensor plus a genuinely new bridge/inflow sector of curvature -nu A B.  A spin-eta realization is admissible only as such a bridge, not as a torsion escape.

Remaining obligations:

- derive the raw gaugino, gravitino, tensorino and ghost SU2R equivariant characters and the complete localized R ledger
- add and quantize an antisymmetric (-1,+1) nu c2(R) source if the E5R route is retained
- construct either two honest localized axion/linear multiplets or a regular existing-tensor coupling
- supply a bridge/transgression that cancels the common nu A B residue, or redesign the profile
- construct the full equivariant differential cocycle including torsion and fixed-stratum data
- compute the regulator and eta/Dai-Freed phases on the actual combined quotient
- identify a global vector-type source for P0 and all its projected partners
- retain the complete V72 KK, vacuum, soft, unification, flavor, proton and cosmology obligations

G1-G8 remain OPEN.
