# V74 Spin(11) bridge and endpoint-obstruction audit

Status: `V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT__V73_ROUTE_AND_MASTER_CORES_BOUND__COMMON_K_COCHARACTER_LATTICE_EXACT__NU_AB_PRIMITIVE_ORDINARY_INTEGRAL__LEVEL_ONE_DIFFERENTIAL_CUP_BRIDGE_PASS__SPIN_PERIOD_GCD_TWO__SMOOTH_SPIN11_TENSOR_RESTRICTION_NO_GO__LOCAL_VECTOR_LINEAR_BF_SCAFFOLD_PASS__PERTURBATIVE_I8_VECTOR_LINEAR_PAIR_CANCELS__QUARTER_ENDPOINT_SPECTATOR_THEOREM_EXACT__ORDINARY_AND_FREE_CURVATURE_SPIN_CANDIDATE_BRIDGE_CANNOT_CANCEL_SPECTATOR__TORSION_ONLY_ETA_REJECTED__COEFFICIENT_FOUR_OVERSHOOTS_THREE_UNITS__DIRECT_FIVE_REPAIR_PHENOMENOLOGY_REJECTED__CONDITIONAL_LOCAL_BRIDGE_ONLY__G1_TO_G8_OPEN`

Core SHA-256: `853833b9206e0eacb3a57ef72b7615c4d8c2b28b87a99155c93dc46d803e5603`

## Exact common-K bridge

The full common Abelian cocharacter lattice is

`Lambda_K={(nu,A,B) in Z^3 | nu-A-B=0 mod2}`.

The honest line classes `nu`, `A=c1(det E2)` and `B=c1(det E3)` therefore
define the integral class `r=nu A B`.  Its CP2 x CP1 period is
`1`, so it is primitive.
The inverse level-one anomaly theory is

`rcheck_bridge=-c1check(N) cup c1check(det E2) cup c1check(det E3)`,

with holonomy `Z_bridge(Y5)=Hol_Y5(rcheck_bridge)`.  This is
an exact quantized common-K bridge.  It is new physics, not an existing tensor
trivialization: `r` is nonzero free and the restriction

`p1(V11)=A^2+B^2-2[c2(E2)+c2(E3)]`

contains no `A B` term.  The T2/Z4 action also has no codimension-one K fixed
stratum, so a physical implementation needs a K-reducing defect, its Z4 orbit,
and cap/source data.

## Spin periods and the endpoint theorem

On spin six-manifolds `r=Sq^2(AB)` modulo two, hence all periods are even.
The `(S2)^3` witness has period
`2`, proving that the
free-curvature candidate level lattice is half-integral.  This period argument
does not construct the full differential/Dai--Freed refinement.

This does not solve the endpoints.  The unit corner class has period
`25/4`.  Any ordinary integral local
completion therefore leaves spectators

`S00=-1/4`
and
`S11=1/4`
modulo integers.  The bridge evaluates to
`{'z00': 6, 'z11': -6}`; integer levels shift by multiples of
six and free-curvature candidate spin half-levels by multiples of three.
Neither changes a
quarter class.  A flat/torsion eta phase cannot change nonzero perturbative
curvature; a viable eta theory must add the opposite free index density and
all of its correlated terms.

The coefficient-four class is integral, but it cancels four anomaly units
rather than the required one and overshoots by
`150` in the
V71/V72 mixed ledger.  It is a spectrum redesign, not a repair of the bound
action.

## Conditional supersymmetric scaffold

Let `J2=delta11-delta00`.  The local four-form construction uses

`H5=dC4+omega5_LAB`

and

`S_BF=-2pi i integral_M6 C4 wedge J2`.

Its variation is exactly the missing opposite endpoint `A B` inflow.  One
neutral vector plus one four-form linear multiplet has the off-shell
vector--linear density and opposite-chirality fermions with smooth
perturbative anomaly polynomial `+P_R-P_R=0`.  Pointwise equivariant
cancellation is still open until compatible Z4 lifts are constructed.  With
compatible parities the BF coupling can make the pair massive.  This is only
a local scaffold: the normal Lorentz/R connection is
not an ordinary Yang--Mills vector, the mixed normal-supergravity deformed
linear superform is absent, the equivariant defect is unbuilt, and the pair
contributes zero to the quarter spectator.

The existing physical anti-self-dual tensor-multiplet two-form (opposite
duality to gravity `B+`) and the new four-form linear multiplet are distinct
fields.

## Alternative repairs

The profile identity is

`k0 ell^2+k1 ellprime^2=[(k0+k1)(A^2+B^2)+2(k0-k1)AB]/4`.

Within the displayed pure `(ell^2,ellprime^2)` determinant-square ansatz, only
the zero profile vanishes on the overlap.  A formal one-Weyl vector-type
`5_(+2)` ledger cancels the local mixed residual algebraically, but no literal
continuous SU2R multiplet or local supersymmetric lift has been constructed;
the row already leaves an unpaired chiral colored five and a pure SU5 cubic
anomaly, while a massive conjugate erases the desired mixed index.  The common
bifundamental diagnostic produces `-nu A B` only as incomplete,
gauge-anomalous interface matter.  Smooth unprojected Spin11-invariant
characteristic/GS couplings cannot generate `A B`; projector-weighted bulk
matter was not exhaustively classified here.

## Fail-closed decision

V74 constructs an exact quantized level-one common-K bridge and a conditional vector-linear BF scaffold with cancelling perturbative I8.  It proves that the displayed smooth Spin11 invariant-characteristic tensor coupling cannot generate the bridge and that the bridge cannot change the forced quarter endpoint spectator.  Coefficient four and minimal matter routes redesign or spoil the action.  The selected scaffold is not a complete microscopic action.

Remaining obligations:

- construct the mixed normal-supergravity/K-defect deformed linear superform
- supply a quotient-quantized refined endpoint sector carrying the opposite quarter free curvature and all correlated terms
- construct the Z4-equivariant defect orbit, isotropy lifts, cap/source data and flat Dai--Freed phase
- derive parities and the complete spectrum proving the vector-linear BF pair is massive with no chiral remainder
- recompute the full pointwise SU2R, normal, gravitational and discrete-R anomaly ledger with the new defect
- solve the defect BPS/FI equations, kinetic positivity, moduli stabilization and the full Hessian
- retain the V73 KK determinant, regulator, thresholds, flavor, proton and cosmology obligations

G1-G8 remain OPEN.

## Primary sources

- [Products in Generalized Differential Cohomology](https://arxiv.org/abs/1112.4173): multiplicative differential cohomology, integration and relative theories; framework for the differential cup product used here
- [Anomaly Inflow and the eta-Invariant](https://arxiv.org/abs/1909.08775): eta-invariant description of perturbative and nonperturbative fermion anomaly inflow; it does not construct the V74 defect
- [The anomalous current multiplet in 6D minimal supersymmetry](https://arxiv.org/abs/1511.06582): deformed six-dimensional linear multiplets for chiral anomalies; the ordinary-YM construction does not supply the normal-SUGRA defect
- [Off-Shell N=(1,0) Linear Multiplets in Six Dimensions](https://arxiv.org/abs/2010.14655): off-shell vector-linear density and four-form linear multiplet; used only as the local BF scaffold
- [Higher dimensional supersymmetry in 4D superspace](https://arxiv.org/abs/hep-th/0101233): rigid superspace anomaly-inflow and super-Chern-Simons framework; not a curved six-dimensional normal-bundle completion
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): fixed-locus anomaly and Green--Schwarz/Chern--Simons exchange conditions; motivates the pointwise and globally-vanishing tests
- [Quantization of anomaly coefficients in 6D N=(1,0) supergravity](https://arxiv.org/abs/1711.04777): integral string-charge and global Green--Schwarz quantization framework; it does not authorize the new K defect
