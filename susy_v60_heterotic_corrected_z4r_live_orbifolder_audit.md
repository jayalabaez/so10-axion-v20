# V60 corrected Z4R live-Orbifolder audit

- Status: `V60_LIVE_ORBIFOLDER_92_STATE_RECONSTRUCTION_PASS__SIX_GAMMA_CORRECTIONS_EXACT__ALL_THREE_CORRECTED_PLANE_R_LEDGERS_EXACT__FULL_4CUBED_ODD_SUM_SCAN_NONUNIVERSAL__AVAILABLE_U1_AND_SPACE_GROUP_MIXINGS_DO_NOT_REPAIR__ALL_32_ODD_PLANE_R_FREE_TAU_CLASS_PRESERVATION_FAIL__LOCAL_THRESHOLD_AXION_LEDGER_UNKNOWN__STRICT_G1_OPEN`
- Canonical core: `096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd`
- Regenerated chiral fields: `92`
- Vendored fixture: `susy_v60_heterotic_corrected_z4r_live_orbifolder_fixture.json` (`79ef2c19fd0b9a563ac36a06a3099e4b240966ef3dd8fe968fe4029d9b237f51`)
- Reproduction requires neither the original temporary tree nor an Orbifolder executable.
- Strict result: **G1 remains open; no gate promotion.**

## Result

The live Orbifolder regeneration removes the V59 publication-data ambiguity for the 92 massless chiral multiplets. For the second-plane rotation, the exact affine equation is

```text
(1-A_g) mu = (rho2-1) lambda,    h_g=(1,mu),
mu=-n3 e3-n4 e4 in T(1,0) and T(1,1).
```

Because Orbifolder orders its gamma basis as `(theta,omega,e1,e2,e3,e4,e5,e6,tau)`,

```text
gamma_hg = -n3 gamma_5 - n4 gamma_6 mod 1,
R2_new  = -2 J2 - 4 gamma_hg mod 4,
qZ4R    = qX + R2_new + 2 n3 mod 4.
```

Exactly six charges shift:

| Field | internal no. | sector | n | representation | gamma_h | old | corrected |
|---|---:|---|---|---|---:|---:|---:|
| F_41 | 102 | [1, 0] | [0, 0, 1, 0, 1, 1] | [1, 1, 1, 2, 1] | 1/2 | 0 | 2 |
| F_42 | 103 | [1, 0] | [0, 0, 1, 0, 1, 1] | [1, 1, 1, 1, 2] | 1/2 | 2 | 0 |
| F_80 | 180 | [1, 1] | [0, 0, 1, 1, 0, 0] | [1, 1, 1, 1, 2] | 1/2 | 0 | 2 |
| F_81 | 181 | [1, 1] | [0, 0, 1, 1, 0, 0] | [1, 1, 1, 2, 1] | 1/2 | 2 | 0 |
| F_91 | 202 | [1, 1] | [1, 0, 1, 1, 0, 0] | [1, 1, 1, 1, 2] | 1/2 | 0 | 2 |
| F_92 | 203 | [1, 1] | [1, 0, 1, 1, 0, 0] | [1, 1, 1, 2, 1] | 1/2 | 2 | 0 |

## Non-Abelian mixed anomalies at the orbifold point

The representative convention is `q=0,1,2,3`, with `A_G=C2(G)+sum(q-1)T(R)` and `eta=2`.

| Factor | old A | old mod 2 | corrected A | corrected mod 2 |
|---|---:|---:|---:|---:|
| SU3_C | 3 | 1 | 3 | 1 |
| SU2_L | 1 | 1 | 1 | 1 |
| SU3_hidden | 7 | 1 | 7 | 1 |
| SU2_hidden_1 | 3 | 1 | 2 | 0 |
| SU2_hidden_2 | 1 | 1 | 2 | 0 |

Corrected residues are `['1', '1', '1', '0', '0']` and are **not universal**.

The same derivation was performed independently for all three plane rotations. Their residue vectors in factor order `(SU3_C,SU2_L,SU3_hidden,SU2_hidden_1,SU2_hidden_2)` are:

- `R1`: `['0', '0', '0', '1', '1']`
- `R2`: `['0', '0', '0', '1', '1']`
- `R3`: `['1', '1', '1', '0', '0']`

The exhaustive scan tested all `32` triples `c_i in Z4` with odd `c1+c2+c3`, which are precisely the combinations whose superpotential charge is 2. The residue-pattern counts are `{'1,1,1,0,0': 16, '0,0,0,1,1': 16}`; universal cases: `0`.

## Mixing repair audit

The exact Orbifolder continuous-anomaly matrix has the same first-column anomaly `15` for all five factors and zero in the other eight columns. Thus every continuous-U(1) mixing leaves all pairwise anomaly differences unchanged.

All `64` binary combinations of the six printed non-R space-group generators were checked. Universal solutions: `0`.
Each printed space-group generator shifts either none or all five anomaly residues, so it cannot alter their relative pattern. Consequently no Abelian combination in the corrected plane-R x U(1)^9 x printed-space-group basis restores universality.

JHEP 01 (2019) 055 independently derives an exact non-R SG-flavor `Z4` for affine class `Z2xZ2-5-1`, but its massless charges are all even. Its faithful massless action is therefore only `Z2`; it is not an extra order-four R candidate. The later original-basis charge formula is not used in this certificate because that basis map was not independently source-derived here.

This no-repair statement is limited to the explicitly regenerated U(1) and space-group charge basis. It does not rule out sector-permuting actions, threshold terms, localized counterterms, or additional axionic structure.

## Full-CFT fail-closed obstruction

The free generator is `tau=['0', '1/2', '0', '1/2', '0', '1/2']`, while `rho2(tau)=['0', '1/2', '0', '-1/2', '0', '1/2']=tau-e4`. For a pure translation, conjugation can only send `tau` to `B tau` for a point-group element `B`. The `Z2 x Z2` point group flips an even number of planes, but every odd-sum plane-R combination flips an odd number. Therefore none of the `32` candidates with superpotential charge 2 maps `tau` into its point-group conjugacy orbit. No class-preserving `h_tau` exists for any of them, so the direct Eq. (3.40) hypothesis fails for the full freely quotiented CFT.

This is not a physical no-go: the rotation may permute winding sectors and require an enlarged treatment. It is decisive against claiming that the 92-state anomaly calculation alone proves a globally gauged Z4R.

## Sources

- [Kappl et al., arXiv:1012.4574](https://arxiv.org/abs/1012.4574), Eqs. (3.11)-(3.12), (E.1)-(E.6), Table E.2 and Appendix A.2.
- [Cabo Bizet et al., arXiv:1308.5669](https://arxiv.org/abs/1308.5669), Eqs. (3.25)-(3.40) and (4.43)-(4.46).
- [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34), Sec. 3.3.6 and Table 3.1.
- [Orbifolder AELR_v1_0 dataset](https://data.mendeley.com/datasets/zrcpg6s3yw/1), DOI `10.17632/zrcpg6s3yw.1`; the original download and every regenerated raw output remain hash-pinned in the fixture.
- [Ramos-Sanchez and Vaudrevange, JHEP 01 (2019) 055](https://doi.org/10.1007/JHEP01(2019)055), Eqs. (3.47)-(3.51).

## Verdict

The corrected 92-state calculation is complete and reproducible, but it worsens the result: the five non-Abelian residues are relatively non-universal and the available printed U(1)/space-group mixings do not repair them. The full free-quotient action, local/threshold anomalies and quantized axion ledger remain unresolved. Strict G1 stays open.
