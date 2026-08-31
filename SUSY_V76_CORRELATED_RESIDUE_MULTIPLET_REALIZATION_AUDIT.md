# V76 correlated-residue and multiplet-realization audit

Status: `V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT__V75_ROUTE_AND_MASTER_CORES_BOUND__UNIVERSAL_CLEAN_QUARTER_HALF_INDEX_NO_GO_EXACT__SEVEN_WEYL_LOCAL_PARENT_RESIDUE_INVERSE_EXACT__TWO_CORNER_COMMON_SUM_QUARTER_PERIOD_NO_GO_EXACT__V74_AB_BRIDGE_CANNOT_REPAIR__GENERAL_PURE_GAUGE_TWO_CORNER_QUARTER_NO_GO_EXACT__TOTAL_TWO_CORNER_FREE_INDEX_ODD_QUARTER_NO_GO_EXACT__FOUR_LINE_DIAGONAL_CORRELATED_ETA_REPRESENTATIVE_EXACT__V75_LEVEL4_COMPONENT_CENTERS_PASS__COMPLETE_6D_MULTIPLETS_ABSENT__MINIMAL_SINGLET_CHIRAL_DRIVERS_EXCLUDED__NORMAL_CHARGED_NOWHERE_ZERO_DRIVER_OBSTRUCTION_EXACT__SPIN_GAUGE_LOCKING_CHANGES_ACTION__FULL_EQUIVARIANT_PARENT_DETERMINANT_SELECTED_OPEN__G1_TO_G8_OPEN`

Core SHA-256: `5c971c7730d8b2ff90f60df4791381517edc59a2c30600aeeb476baf5ef48e1a`

## What survives

The strongest result is representation-independent.  The two bound residues
have total period
`-5/4` on CP3 and
`9/4` on the
spin cubic threefold.  Honest local Weyl indices and ordinary bridges add
integers; standard signed half-eta copies add only half-integers.  The
remaining odd quarter cannot vanish.

There is nevertheless an exact correlated target: summing the four honest
line indices `c_(eps,tau)=(nu+eps A+tau B)/2` gives

`sum I(c_eps_tau)=(1/4)nu(A^2+B^2)+nu(nu^2-p1)/12`.

It has integral periods `3` and `11` on the two witnesses.  The desired
diagonal quarter therefore exists only together with the forced
`S_eta=nu(nu^2-p1)/12` spectator; V75's exact theorem excludes removing that
spectator with ordinary neutral determinants or standard half-eta copies.

The seven-Weyl full-quotient module has exact moments
`Q1=-3`, `Q3=3/4` and
`normal-X^2=-125`.  Its polynomial is

`C7=-(5/2)nu ell^2+(1/8)nu(nu^2+p1)`,

so it cancels the bound V71 normal/gravitational residue locally.  All seven
entries pass the standard hyper-type component-center rule.  This is a real
local result, not yet a two-corner theory.

## Exact two-corner rejection

The two bundle identities are `2ell=A+B` and
`2ellprime=A-B`.  Since the parent residue has the same sign
at both corners, the post-cancellation terms add to

`-(5/4)nu(A^2+B^2)`.

This is linearly independent of the V74 bridge class
`k nu A B, k in Z`.  Its required inverse has period
`65/4` on CP3 and
`195/4` on
the spin cubic threefold, with fractional parts `1/4` and `3/4`.  It is in
neither the ordinary index lattice nor the permissive half-index lattice.
Flipping one endpoint also fails because it doubles rather than cancels that
corner's parent residue.

The result is not peculiar to the seven-Weyl representative.  For any local
repair `T+g nu ell^2` that retains only pure gauge curvature, integrality on
the two admissible CP3 half-cocharacters forces
`g=-5/2+4Z`.  Even
the deliberately permissive half-index image only enlarges this to
`g=-5/2+2Z`.
At two corners the coefficient of `nu(A^2+B^2)` is therefore respectively
`3/4 mod Z` or an odd quarter.  An integer `nu A B` bridge cannot remove it,
and the optional flavor quotient cannot help because `v=0` remains an
admissible subbackground.

## Multiplets and the mass-driver obstruction

Every V75 level-four component passes the appropriate quotient rule:
SU2R-singlet fermions have the hyper-type pattern and SU2R doublets have the
vector/tensor-type pattern.  The aggregate result is
`COMPONENT_CENTER_PASS__COMPLETE_6D_MULTIPLET_AND_ACTION_ABSENT`.  Complete six-dimensional partner fields, reality
conditions, orbifold profiles, kinetic terms and supersymmetry transformations
are still absent.

The square-torus chain check does preserve one useful part of V75: for a path
between the two order-four points, the four-image cover chain obeys
`partial Gamma=4(p1-p0)`.  It is a plausible
topological scaffold for a level-four opposite-corner profile.  It supplies
neither the missing quotient delta normalization nor a common BPS projector;
same-sign corner sources also require compensating order-two sources or bulk
flux.

More strongly, a nonzero normal-charge `q` scalar is a section of `N^q`.
A nowhere-zero section trivializes that line.  On the admissible CP3 witness
`c1(N)=H`, none of the proposed `q=+/-2,-4` drivers can therefore be
everywhere nonzero.  Allowing a zero divisor makes the mass matrix lose rank
there and leaves modes or an anomaly-matching WZ/eta phase.  Spin-gauge
locking could evade this only by adding a new gauge line and changing the
tangential structure and complete anomaly ledger; it is not a completion of
the current action.
The scalar representations themselves are honest, but their minimal neutral
SU2R-singlet N=1 chiral fermion partners fail the bound center rule.  A
vector/tensor-type SU2R-doublet lift could pass only with all of its additional
fields and anomalies, which have not been built.

## Fail-closed decision

V76 closes two tempting free-field continuations without closing a theory gate.  A representation-independent two-witness theorem excludes every ordinary localized-Weyl, integer-bridge and standard half-eta completion of the total equal-corner residue.  A four-line index gives an exact correlated representative of the required diagonal quarter but forces an eta-gravity spectator.  The seven-Weyl module cancels the bound residue at one corner but its forced same-sign two-corner gauge sum has forbidden quarter periods and is not an integer/half-index AB bridge.  Every pure-gauge local inverse has the same two-corner diagonal-quarter obstruction, including the optional-flavor extension.  Every V75 level-four component passes its quotient-center multiplet pattern, but no complete 6D multiplets are present and its normal-charged mass drivers cannot be nowhere zero on the admissible CP3 bundle.  The present action remains rejected; the research program remains viable only through a full same-action equivariant determinant or genuinely new correlated/changed-structure physics.

Remaining obligations:

- compute one regulator-consistent full parent determinant including gravitino, tensorino, self-dual fields, ghosts, SU2R and every fixed-stratum character
- compute the exact equivariant Spin-SU2R-U5(-flavor) bordism group, flat phases and capped T2/Z4 extension
- if spin-gauge locking is retained, specify U1_g charges, flux quantization, kinetic terms, Higgs sector and the completely recomputed local/global anomaly polynomial
- classify correlated higher-spin, self-dual, Wu-Chern-Simons and interacting quarter-refined endpoint sectors
- construct complete bulk or defect supermultiplets, parities, isotropy lifts, F/D/BPS equations and a positive full Hessian
- only after a same-action spectrum exists, recompute KK determinants, thresholds, unification, proton operators, flavor, collider limits, reheating, relics and BBN

G1-G8 remain OPEN.

## Primary sources

- [Eta-Invariants and Determinant Lines](https://arxiv.org/abs/hep-th/9405012): eta invariants obey determinant-line variation and gluing laws; the citation does not construct the missing equivariant orbifold phase
- [Anomaly Inflow and the eta-Invariant](https://arxiv.org/abs/1909.08775): fermion anomalies are encoded by eta-invariant inflow; this supports the index-period test, not a microscopic V76 endpoint sector
- [Anomalies on Six Dimensional Orbifolds](https://arxiv.org/abs/hep-th/0612212): localized integer residues may be canceled by suitable localized fermions and remnant gravitational symmetries act on localized fields; the paper does not supply the present multiplet or mass action
- [All Couplings of Minimal Six-dimensional Supergravity](https://arxiv.org/abs/hep-th/0101074): a 6D (1,0) vector has an SU2R-doublet gaugino, a tensor has an SU2R-doublet tensorino, and a hyper has an SU2R-singlet hyperino; complete couplings include all bosonic and fermionic partners
- [6D Supersymmetry, Projective Superspace and 4D, N=1 Superfields](https://arxiv.org/abs/hep-th/0508187): a 6D hypermultiplet requires a complete 4D N=1 superfield pair/CNM description; an isolated endpoint Weyl ledger is not such a lift
- [Quantum Corrections to Non-Abelian SUSY Theories on Orbifolds](https://arxiv.org/abs/hep-th/0602155): the 6D vector decomposes into V and Sigma with distinct T2/ZN phases; this fixes the ordinary Z4 projection diagnostic and does not construct the proposed higher-normal-charge endpoint fields
- [Supersymmetric theories with compact extra dimensions in N=1 superfields](https://arxiv.org/abs/hep-th/0106256): 5D vector and hypermultiplets split into opposite-parity N=1 halves at an orbifold boundary; T2/Z4 has no such fixed wall
- [Off-Shell N=(1,0) Linear Multiplets in Six Dimensions](https://arxiv.org/abs/2010.14655): the off-shell vector-linear density uses full ordinary multiplets; it does not by itself turn the normal Lorentz connection into an independent Yang-Mills vector multiplet
- [Curvature squared invariants in six-dimensional N=(1,0) supergravity](https://arxiv.org/abs/1808.00459): supersymmetric curvature invariants require complete Weyl/compensator multiplets and auxiliary fields, not an isolated normal-curvature term
- [Supersymmetry anomalies in N=1 conformal supergravity](https://arxiv.org/abs/1902.06717): Wess-Zumino consistency ties an R anomaly to a Q-supersymmetry anomaly; a formal bosonic axion term is not a full superinvariant
- [Remarks on the Green-Schwarz terms of six-dimensional supergravity theories](https://arxiv.org/abs/1808.01334): global 6D Green-Schwarz terms depend on the integral string-charge lattice and characteristic gravitational coefficient
- [The global anomaly of the self-dual field in general backgrounds](https://arxiv.org/abs/1309.6642): self-dual-field anomalies are refined global theories; adding such a field changes the complete higher-dimensional anomaly system
- [Anomaly of the Electromagnetic Duality of Maxwell Theory](https://arxiv.org/abs/1905.08943): Maxwell duality can have fractional refined anomalies, but in a different duality/tangential structure from the required normal-U1 class
- [Anomaly Cancellation in Six Dimensions](https://arxiv.org/abs/hep-th/9304104): six-dimensional anomaly cancellation constrains complete bulk multiplet spectra and Green-Schwarz couplings
