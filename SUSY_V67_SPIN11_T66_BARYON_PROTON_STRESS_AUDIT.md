# SUSY V67 Spin(11) T66 baryon/proton stress audit

Status: `V67_SPIN11_T66_BARYON_PROTON_STRESS__V66_ROUTE_AND_MASTER_CORES_BOUND__UPTYPE_PORTAL_SCHUR_COMPLEMENT_EXACT__PRE_MAJORANA_DELTA_B_EQUALS_DELTA_L_EQUALS_MINUS_ONE__SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_ONE_SIDED_SELECTOR_NO_GO__CONDITIONAL_IR_BARYON_TRIALITY_LINEAR_MOD3_AND_CUBIC_MOD9_PASS_BUT_NOT_LOCALLY_EMBEDDED__H66_CENTRAL_GAUGE_PROXY_FAILS__T66_CENTRAL_GAUGE_PROXY_PASSES__NO_LIFETIME_PREDICTION__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS`

Canonical core: `859ecfc4185738bd4e1cb8ecc0c14d3640f3c3abd588b8ce67a167f4771d738f`

## Decision

G7 receives a material exact advance but remains **OPEN**.  The displayed T66
conjugate up-type portal generates a baryon-violating Schur operator.  Under
the assumptions stated below, no family-dependent Abelian selector commuting
with the unified multiplets can allow the wanted portal and GM-neutral mass
while symmetry-forbidding every conjugate portal.  A conditional IR `Z3`
baryon-triality assignment passes the standard linear and integer-parent cubic
checks, but it splits Spin(10)/Pati-Salam multiplets and is therefore not a
repair of the current 5D action.

The current Spin(11) action remains **REJECTED**.  H66 and T66 remain candidate
extensions only.  No proton lifetime is predicted and no gate is promoted.

## Bound lineage

- V66 route core: `07593002755158c96647701da7453b1942114424a5d3aff5318ebb891a2964ae`
- V66 master core: `499382834b9b63a23e10dbc16106dfb1db0f2bfeae17163862afd4f1467e9fa4`
- V55 comparison core: `6959457039b2828c1602e0e0e225b90a24da402260c24b39535a6c3783cbc665`

## Exact T66 up-type Schur complement

`W=M10 Uc_X U_X + (1/2) lambda_ij epsilon^abc Uc_X,a dc_i,b dc_j,c + rho_kl U_X^a uc_k,a Nc_l`

With `A=(1/2) lambda_ij epsilon dc_i dc_j`, `B=rho_kl uc_k Nc_l`, and
`lambda_ij=-lambda_ji`, the exact elimination is

`-1/2 J^T M_H^-1 J = -A B/M10`,

hence

`W_eff=-(lambda_ij rho_kl/(2 M10)) epsilon^abc uc_k,a dc_i,b dc_j,c Nc_l`.

Before Majorana-neutrino matching it carries
`Delta B=-1` and
`Delta L=-1`, while conserving `B-L`.
The fixed tensor convention is
`theta_{l r}=sum_m (M_N^-1)_{l m} (y_nu)_{r m} v_u`.  After eliminating `Nc` and
inserting `v_u`, `C5_{ijkr}=+(lambda_ij/(2 M10)) sum_l rho_{k l} theta_{l r}; omit 1/2 when summing only i<j`.  The resulting
`uc dc dc L Hu` field monomial instead has `Delta B=-1`, `Delta L=+1` and
`Delta(B-L)=-2`; the Majorana insertion supplies the two-unit change.

## Unified-selector no-go

Family charges may differ.  Structural full rank supplies a determinant
permutation `sigma` with `f_i+f_sigma(i)=w`.  If `C F_i F_j` is allowed, then
`c=w-f_i-f_j`; GM neutrality gives `cbar=-c`.  The complementary pair obeys

`cbar+f_sigma(i)+f_sigma(j)=-c+(w-f_i)+(w-f_j)=w`.

Thus at least one conjugate portal is selector-allowed.  This does not prove
that its Wilson coefficient is nonzero.  The executable scan covers arbitrary
three-family charges for ordinary and R selectors with `2 <= N <= 24`:
179998 charge assignments,
2590 structurally
full-rank assignments and 7770
wanted-portal cases, with 0
counterexamples.  A common determinant permutation makes the proof factorwise
for products.  Nonzero Higgs charge, direct/charged-spurion masses, split
multiplets, non-Abelian/topological rules and texture zeros remain outside the
theorem.

## Conditional IR baryon triality

One representative charge order is

`[Q,Uc,Dc,L,Ec,Nc,Hu,Hd]=[0,2,1,2,2,0,1,2] mod 3`,

with

`[QX,UcX,EcX,QbarX,UX,EX]=[0,1,2,0,2,1] mod 3`.

This keeps all vectorlike masses, MSSM Yukawas, `mu`, `Nc Nc`, the three
`lambda` portals and the Qbar/Ebar `rho` portals, while forbidding `UX Uc Nc`
and the displayed `Delta B=1` superpotential classes.

| Anomaly numerator | Value | Residue | Role |
|---|---:|---:|---|
| A2_2T | 9 | 0 mod 3 | standard linear |
| A3_2T | 12 | 0 mod 3 | standard linear |
| AYY_6Y_integer | 954 | 0 mod 3 | extra representative U(1) ledger only |
| AYZZ_6Y_integer | -90 | 0 mod 3 | extra representative U(1) ledger only |
| AZZZ | 207 | 0 mod 9 | standard integer-parent cubic |
| Agrav | 63 | 0 mod 3 | standard linear |

The standard linear residues vanish mod 3 and `AZZZ=207`
vanishes mod 9, as required for the integer-charge parent used in the standard
B3 classification.  The `YYZ` and `YZZ` rows are extra representative-
normalization checks, not universal low-energy anomaly constraints.  Within
the explicitly stated finite charge/portal ansatz, the scan finds no `Z2`
solution and one `Z3` B3 orbit up to inversion and an integer-hypercharge shift;
it is not a universal discrete-symmetry classification.

B3 is an additional conditional selector, not a replacement for the inherited
`Z4R -> Z2` matter parity.  B3 alone allows `L L Ec` and `L Q Dc`; the retained
matter parity is what forbids those odd-matter terms.  This remains an **IR
escape only**: it cannot simply be placed on either existing unified wall.  A
new local/topological embedding, wall anomaly/GS ledger and Dai-Freed
computation are mandatory.

## Conditional dimension-five stress

Using only the repository-frozen V55 scaling comparison at the illustrative
common T66 threshold gives

- `M10 = 1.383905252e+04 GeV`;
- required `M_eff > 5.488346121e+19 GeV`;
- `|lambda rho theta_N D_flavour| < 2.521534213e-16`.

This is a feasibility bound, not a T66 lifetime calculation.  An order-one
unprotected portal fails this comparison by many orders of magnitude.

## H66/T66 dimension-six proxy matrix

The frozen conditional identification is `M_X=MG`, `alpha_X=alphaU`.

| Branch | Proxy tau (yr) | tau/limit | Required M_X/MG | Scoped result |
|---|---:|---:|---:|---|
| H66 | 1.559728944e+33 | 0.0649887 | 1.980571510 | central proxy fails; branch not globally rejected |
| T66 | 1.436901640e+35 | 5.98709 | 0.639287261 | central proxy passes; G7 not closed |

H66 therefore needs `M_X > 4.688170168e+15 GeV` under the frozen
proxy.  T66 passes that one diagnostic if
`M_X > 7.776173204e+15 GeV`, but its dimension-five exotic portal
remains the sharper obstruction.

## Primary sources

- [What is the Discrete Gauge Symmetry of the MSSM?](https://arxiv.org/abs/hep-ph/0512163): family-independent B3 classification, linear anomaly conditions, purely-Abelian caveats and the integer-parent cubic condition
- [Search for proton decay via p to e+ pi0 and p to mu+ pi0 with an enlarged fiducial volume in Super-Kamiokande I-IV](https://arxiv.org/abs/2010.16098): p to e+ pi0 lower limit used by the frozen gauge proxy
- [Search for Proton Decay via p to nu K+ using 260 kiloton-year data](https://arxiv.org/abs/1408.1195): inherited through the exact V55 comparison core
- [Constraining Proton Lifetime in SO(10) with Stabilized Doublet-Triplet Splitting](https://arxiv.org/abs/1003.2625): inherited through the exact V55 comparison core

## G2-G8 closability ranking

| Rank | Gate | Topic | Reason |
|---:|---|---|---|
| 1 | G7 | proton/baryon | exact selectors and proxy inputs exist; full matching remains |
| 2 | G4 | protected hierarchy | projector exact, but V64 null pair and GM coefficient block |
| 3 | G5 | LSP/exotic phenomenology | R parity exact; mass, lifetime, relic and collider calculations absent |
| 4 | G2 | coefficient action/flavour/soft | broad Wilsonian action and KK determinant reconstruction required |
| 5 | G3 | vacuum/compactification | hidden vacuum, saxion and full Hessian absent |
| 6 | G6 | cosmological history | inflation, reheating, defects and moduli history absent |
| 7 | G8 | UV/global quantum completion | UV regulator, Dai-Freed phase and predictivity score absent |

## Fail-closed boundary

Still required in one action: the physical X/Y and KK pole spectrum, local B3
or alternative portal protection, localized/global anomaly completion,
mass-basis Wilson tensors, neutrino/flavour data, SUSY dressing and running,
channel-specific lattice inputs, and correlated uncertainties.  Consequently
G1-G8 remain open with zero promotions.
