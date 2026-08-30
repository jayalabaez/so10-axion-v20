# V60 multipath G1 frontier master audit

Status: `V60_MULTIPATH_G1_FRONTIER_MASTER__V59_MASTER_AND_LIVE_ORBIFOLDER_CORE_BOUND__V59_ROUTE_A_SUPERSEDED__92_STATE_CORRECTED_CHARGE_AMBIGUITY_RESOLVED_CONDITIONALLY__SIX_GAMMA_SHIFTS_EXACT__EVERY_ODD_CORRECTED_PLANE_R_COMBINATION_NONUNIVERSAL__AVAILABLE_U1_AND_PRINTED_SPACE_GROUP_MIXINGS_CANNOT_REPAIR__KAPPL_CANDIDATE_REJECTED_AS_G1_COMPLETION__NO_ODD_PLANE_R_COMBINATION_CLASS_PRESERVES_TAU__LOCAL_THRESHOLD_AXION_COMPLETION_OPEN__NOT_A_UNIVERSAL_HETEROTIC_NO_GO__V59_SPIN11_AND_GAUGED_U1R_ROUTES_CARRIED_FORWARD__NO_CROSS_ROUTE_SPLICING__G1_TO_G8_OPEN`

## Result

**The live regeneration rejects the Kappl candidate as the desired G1
completion in the tested corrected Abelian basis. It does not prove a universal
heterotic no-go. G1--G8 remain OPEN.**

This distinct V60 master supersedes only the V59 heterotic route-A row. It
binds the prior V59 master and directly rebinds the unchanged Spin(11) and
gauged-U(1)R cores. No route-local gain is spliced into another action.

## Exact supersession

```text
V59 route A: 38747dee7e8bafdae38ddea1408c8163d625ff6cb836aaa97304f4479624250b
V60 route A: 096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd
V59 master:  9a74431ca080341d56225c6cc85edb937d3cafaa902bbacb556dbb325d78d24a
```

The old published-table non-identifiability was correct but is no longer the
operative frontier. Live Orbifolder output now supplies a conditional,
source-locked 92-state reconstruction. The V59 master and route files were not
modified.

## Conditional 92-state reconstruction

All 92 regenerated massless chiral multiplets pass the affine `h_g` equations;
all have zero oscillator contribution. The formula is

```text
qX + R2_corrected + 2 n3 (mod 4)
(1-A_g) mu = (rho2-1) lambda for h_g=(1,mu)
```

Exactly six fields change by two modulo four:

| Field | Orbifolder number | gamma_h | old q | corrected q |
|---|---:|---:|---:|---:|
| F_41 | 102 | 1/2 | 0 | 2 |
| F_42 | 103 | 1/2 | 2 | 0 |
| F_80 | 180 | 1/2 | 0 | 2 |
| F_81 | 181 | 1/2 | 2 | 0 |
| F_91 | 202 | 1/2 | 0 | 2 |
| F_92 | 203 | 1/2 | 2 | 0 |

## Corrected hidden-anomaly rejection

With factor order

```text
['SU3_C', 'SU2_L', 'SU3_hidden', 'SU2_hidden_1', 'SU2_hidden_2']
```

the anomaly representatives and residues are

```text
A_G       = ['3', '1', '7', '2', '2']
A_G mod 2 = ['1', '1', '1', '0', '0'].
```

The visible `SU(3)C`, `SU(2)L`, and hidden `SU(3)` residues are one; the two
hidden `SU(2)` residues are zero. Thus the corrected generator is not universal.

The exhaustive corrected-plane scan tests
`32` odd
coefficient triples. Its only residue patterns are
`{'0,0,0,1,1': 16, '1,1,1,0,0': 16}`;
neither is universal. All nine printed continuous-U(1) anomaly columns are
universal shifts and cannot change relative residues. All
`64`
binary combinations of the six printed non-R space-group generators likewise
produce no repair.

This rejects the Kappl candidate within the complete tested
`plane-R x U(1)^9 x SG` basis.

## Why this is not a full physical no-go

For the freely acting translation, the tested second-plane rotation obeys

```text
rho2(tau) = ['0', '1/2', '0', '-1/2', '0', '1/2']
rho2(tau) = tau - e4: True
rho2(tau) in the space-group conjugacy orbit: False
```

No class-preserving `h_tau` exists for `rho2` in the tested space group. The
stronger full-plane enumeration uses the bound tau orbit:

```text
point-group occupied-component flip counts = [0, 2]
odd-sum plane-R flip counts                 = [1, 3]
odd-sum combinations tested                 = 32
class-preserving combinations               = 0
```

Point-group conjugation changes an even number of tau's occupied
half-components. Every superpotential-charge-two plane-R combination changes
an odd number. Thus none of the 32 R-type combinations is class-preserving on
tau. This still does not exclude a sector-permuting winding or generalized
symmetry, so the conditional 92-state ledger is not promoted to a theorem about
every winding sector. These obligations also remain open:

- derive the action of rho2 on all freely twisted/winding sectors when conjugacy classes are permuted
- compute local/fixed-locus anomaly phases and any localized counterterms
- compute moduli-dependent threshold corrections for the corrected mixed generator
- derive the complete quantized axion coupling and transformation matrix
- recheck the corrected generator after the selected singlet VEVs and mass diagonalization

The exact claim is candidate rejection, not a universal heterotic theorem.

## Carried routes

Route B remains `MATHEMATICAL_CANDIDATE_WITH_SCOPED_SELECTOR_NO_GO`: it has two weak and zero colored
chiral zero modes plus the full-rank rank-breaking block, but its scoped
commuting-Abelian selector no-go and Dai--Freed/UV obligations remain.

Route C remains `INTEGRATED_BULK_ADVANCE_WITH_EXACT_EXISTING_LOCAL_GS_REJECTION`: its integrated lattice and 270-singlet
parity solution pass, but the existing bulk GS direction fails at GG,
flipped-GG, and Pati--Salam fixed points.

## No cross-route splicing

Strict G1 must be proved by one versioned action. Conditional heterotic charges, a Spin(11) projector, and a gauged-U1R lattice cannot be conjoined across inequivalent actions.

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: live regeneration resolves the 92-state charge ambiguity conditionally but rejects the Kappl candidate in the tested corrected Abelian basis through hidden-anomaly non-universality. The rho(tau) class-preservation failure and local/threshold/axion deficits prevent a full physical no-go. Spin(11) and gauged-U1R remain independently open. |
| G2 | OPEN | OPEN: V60 adds no same-action proof of G2; the prior fail-closed frontier remains: OPEN: no V59 route proves G2 in the same action; the bound V58 baseline remains: OPEN: the complete coefficient-level 4D Wilsonian W, K, gauge-kinetic functions, soft sector, and a numerical controlled F-root have not been reconstructed. |
| G3 | OPEN | OPEN: V60 adds no same-action proof of G3; the prior fail-closed frontier remains: OPEN: no V59 route proves G3 in the same action; the bound V58 baseline remains: OPEN: no full physical vacuum quotient, stabilized spectrum, and complete Hessian/KK analysis is certified here. |
| G4 | OPEN | OPEN: V60 adds no same-action proof of G4; the prior fail-closed frontier remains: OPEN: no V59 route proves G4 in the same action; the bound V58 baseline remains: OPEN WITH STRONG ADVANCE: the source gives one massless Higgs pair, a full-rank triplet matrix, and perturbative all-order mu protection; later physical hierarchy tests remain. |
| G5 | OPEN | OPEN: V60 adds no same-action proof of G5; the prior fail-closed frontier remains: OPEN: no V59 route proves G5 in the same action; the bound V58 baseline remains: OPEN: no dark-sector and cosmological history is selected or solved. |
| G6 | OPEN | OPEN: V60 adds no same-action proof of G6; the prior fail-closed frontier remains: OPEN: no V59 route proves G6 in the same action; the bound V58 baseline remains: OPEN: precision thresholds, full running, pole spectrum, and uncertainty propagation are absent. |
| G7 | OPEN | OPEN: V60 adds no same-action proof of G7; the prior fail-closed frontier remains: OPEN: no V59 route proves G7 in the same action; the bound V58 baseline remains: OPEN WITH STRONG ADVANCE: matter parity removes dimension four proton decay and Z4R suppresses dimension five operators, but no complete lifetime calculation exists. |
| G8 | OPEN | OPEN: V60 adds no same-action proof of G8; the prior fail-closed frontier remains: OPEN: no V59 route proves G8 in the same action; the bound V58 baseline remains: OPEN WITH STRONG ADVANCE: full-rank Yukawas and a rank-11 singlet-neutrino sector exist, but no mediator-complete numerical CKM/PMNS likelihood is certified. |

## Fail-closed decision

The regenerated ledger rejects this Kappl candidate as the desired G1 completion in the complete tested corrected Abelian basis. It does not prove all heterotic realizations impossible, nor a full physical symmetry no-go for the freely quotiented CFT. No same-action route closes G1, and G1--G8 remain open.

Primary-source provenance and external regeneration hashes remain in the
canonically bound route artifacts; this master adds no new literature claim.

Core SHA-256: `35395532eaf625886b704ed25b7fa8525482ec1d53b94ccc96e7858d6425898e`
