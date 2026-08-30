# SUSY V53 elementary filter Hessian audit

Status: `V53_ELEMENTARY_RENORMALIZABLE_FOUR_10_FILTER_PLUS_PX_DRIVER__FULL_218_HESSIAN_RANK181_NULLITY37__33_GAUGE_PLUS4_WEAK_HIGGS__COLOR_RANK24_WEAK_RANK12_NULLITY4__DRIVER_RANK2__SHAPING_SYMMETRY_AND_UV_ANOMALIES_OPEN__NO_G2_PROMOTION`

Core SHA-256: `993b549668243b06d082a7def8591c63141dfa402d6372b133c19cfa8f8b6ff6`

## Outcome

The cross-coupled DW source, a four-vector Chen-style filter, and the minimal `P,X`
driver now coexist in one explicit elementary renormalizable action. At `P=v=1`, `X=0`
and zero vector VEVs, every added F term vanishes and the driver Hessian is nonsingular.

The complete `218 x 218` Hessian has exact rank
`181` and nullity `37`. Its nullity decomposes
as `33` broken-gauge directions plus exactly `4` weak Higgs coordinates, with zero extras.
The full Ward product vanishes exactly.

## Filter ranks

The color block is `24 x 24` with rank
`24` and no kernel. The weak block is `16 x
16` with rank `12` and nullity `4`.
This holds on the open set where `P lambdaP`, `mh`, `lambdaB Bcolor`, and `m2` are nonzero;
no equality among independent coefficients is required.

## Perturbativity

Including the DW source, four vectors, and three matter `16`s gives `sum T=42`
and `b=18`. At `g=0.73`, the formal pole is
`3.7569e+03` times the matching scale.

## Fail-closed boundary

No complete shaping symmetry has been supplied. The elementary action is explicit, but a generic
additional `H1^2` invariant fills the intended weak kernel. The all-operator selector census, its
anomalies, proton decay, thresholds, and UV origin therefore remain open. No G2 clause is promoted.

The filter structure follows [Chen and Zhang](https://arxiv.org/abs/1410.5625); the DW source
motivation is anchored by [Barr and Raby](https://arxiv.org/abs/hep-ph/9705366).
