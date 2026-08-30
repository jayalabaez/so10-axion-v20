# V39 split-six baryon-operator audit

Status: `V39_SPLIT_SIX_Z3_LOCAL_SOURCE_BLOCK_VALIDATED__DEGREE9_QC4_VEV_DRESSING_EXPLICIT__G7_AND_G8_OPEN`

V39 makes one minimal architectural change to V37: the single PS six becomes
`SigC + SigBc`, and a new ordinary `Z3` is imposed. The intended scope is a
source-level repair of the direct driver-dressed four-matter operators; it is
not a claimed complete theory.

## Exact selector result

The unsplit V37 terms force `4 q(Q)=4 q(Qc)=0` for every extra ordinary
additive selector. The split six removes that implication. The retained-term,
mixed-PS-residue search through odd orders 3--99 finds its first solution at
`N=3`. V39 uses
`q(Q,Qc,Sc,Sbc,SigC,SigBc)=(1,2,2,1,2,1)`.

Thus the local source charges are `[('X Q Q Q Q', 1), ('X Qc Qc Qc Qc', 2), ('Zp Q Q Q Q', 1), ('Zp Qc Qc Qc Qc', 2)]`:
none is neutral. Every one of the 32 displayed superpotential terms is `Z3`
neutral and has external `Z4R` charge two.

The pure finite convention passes, the mixed PS residues are
`{'SU4': 42, 'SU2L': 24, 'SU2R': 48}` modulo 3, and the two
listed raw cross residues are both zero modulo 3. These are necessary checks,
not a product-bordism or discrete-R completion.

The active 21-field `(Z5610,Z4R,Z3,PQ)` lattice is re-enumerated rather than
inherited by deletion.  It has exact first-breaking equalities W degree 33
and Kähler degree 32; the gauge-singlet attainment witnesses are `P^33` and
`P^6 A32^21 A16dag (A17dag)^4`.

## Narrow VEV result and remaining boundary

For exactly four left-handed `Q` fields and only canonical PS/PQ VEV
insertions, the SU(4) and `Z3` count forces a surplus of identical rank-one
PS VEVs; their SU(2)_R epsilon contraction vanishes. This proves a narrow
holomorphic `X/Zp Q^4` dressing result on that branch. The mirror `Qc^4`
ring fails explicitly because `Qc` itself carries SU(2)_R.

The concrete allowed counterexample is
`X [epsilon_SU2R delta_SU4 (Qc Sbc)]^4/M^6`, and likewise with `Zp`.
Both degree-nine operators have `Z3=0`, `Z5610=0`, `PQ=0`, and `Z4R=2`.
After four `Sbc` insertions take their canonical PS-breaking VEV, the operator
is generically nonzero.  This is an operator-ring counterexample, not by itself
a proton-decay amplitude: The standard SM-singlet Sbc VEV selects a particular Qc component. This disproves an all-ring algebraic protection claim but does not alone establish a proton-decay amplitude; component, flavour, SUSY-dressing, and hadronic matching remain required.

G7 remains open: `full Qc^4 and mixed heavy-field operator ring; Kahler/soft spurion operators and the deformed vacuum; component spectrum, Wilson matching, SUSY dressing and RG; flavour tensors and hadronic matrix elements`.

G8 retains the Yukawa and type-I-seesaw source terms but remains open:
`a derived flavour texture or UV flavour sector; charged-fermion and neutrino fit; threshold/RG evolution with a spectrum; versioned joint likelihood and covariance`.

The model has an executable SARAH validator at
`tools/validate-susy-v39-baryon-repair.wls`. It must be
run with SARAH 4.15.3 before any downstream RGE or spectrum statement.

Core SHA-256: `6bbd94b07c108f989e4538e7afb56085a749dfc47d1048d95a13e3fc977ad933`
