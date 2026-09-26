# G6 SM Pati-Salam exact tree-level threshold spectrum -- v20

**Status:** `G6_SM_PATI_SALAM_TREE_SPECTRUM_EXACT__TREE_LEVEL_ONLY__NOT_WIRED`

**Theorem claimed:** `True`

Exact over Q(r0, x0, eps) for the G3 witness family V_PS,eps (kappa = -r0/4, O06 = 2|kappa| r0 + eps) at q0 = (p, 0, r0 sigma_std, r0, x0): grad V(q0) = 0 identically; det(H_u - lambda D^2) factors into 28 irreducible factors (24 linear with closed-form levels, two cubics and two quadratics over Q[r0]); every root other than lambda = 0 (multiplicity 35) is strictly positive for all r0, x0, eps > 0, so the tree-level Hessian spectrum at q0 has exactly 35 zero modes (34 eaten Goldstones + the axion) and 451 positive levels, with SM labels from exact integer Casimirs; it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum (0 < eps < 12 - 2|kappa| r0); re-certified point-exactly at the benchmark (r0 = 1/5, x0 = 1) and at the physical member (r0 = 51544138/809635808795, x0 = 10^17 GeV/M_GUT), eps = r0^2/100.  Tree level only.

Exact tree-level Hessian spectrum at q0 of the G3 witness family V_PS,eps, parametric in (r0, x0, eps) (the vacuum/threshold spectrum wherever G3 certifies q0 as the global minimum, 0 < eps < 12 - 2|kappa| r0): the gradient vanishes identically and the pencil factors into 28 irreducible factors over Q(r0, x0, eps) on 65 support components; for every r0, x0, eps > 0 there are 35 zero modes (34 eaten Goldstones + the axion) and 451 strictly positive levels, 0 negative (sign-alternation certificate, Sturm on 0 < r0 <= 1/5), with exact SM labels and mixings; both the benchmark and the physical member (canonical Phi17 scale) are re-certified point-exactly.  The 10_H triplets decouple exactly (issue #106 sub-ledger); |G(Delta, 6_Sigma)| = 28*sqrt(2)*(32 + 117*r0^2)/(1360 + 4316*r0^2 + 117*r0^4) M_GUT^-2, not exactly r0-independent (limit 56*sqrt(2)/85 as r0 -> 0, variation 1.70% on (0, 1/5]); the axion norm is F_PQ^2 = 32 r0^2 578 x0^2/(32 r0^2 + 578 x0^2) and, the axion angle having period 2 pi/68 modulo the gauge group, the periodicity scale is v_a = F_PQ/68 (physical member, illustrative: F_PQ = 3.572e+12 GeV, v_a = 5.252e+10 GeV; f_a = v_a/N_DW is not computed).  Tree level only: one-loop positivity is NOT certified (R1 open), electroweak symmetry is not broken (H = 0, eps > 0), sub-M_I coloured 126bar states remain, and G6 is not wired (no gate change; G6 stays BLOCKED).

Checks: 81/81 passed.

## Witness

- Family: V_PS,eps = V_PS + eps N_H, kappa = -r0/4, O06 = 2|kappa| r0 + eps (g3_sm_target_track_v20, decision D2)
- Vacuum: q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)
- Parametric domain: r0 > 0, x0 > 0, eps > 0 for the Hessian at the stationary point q0 (Sturm confirmation on 0 < r0 <= 1/5); it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum, 0 < eps < 12 - 2|kappa| r0
- benchmark: r0 = `1/5`, x0 = `1`, eps = `1/2500`
- physical: r0 = `51544138/809635808795`, x0 = `1000000000000/99175647989`, eps = `664199540540761/16387753572078344983800625`

## Parametric factorisation over Q(r0, x0, eps)

Support components: `65`; Hessian monomials: `1, eps, x0^2, r0, r0^2`.
Levels are eigenvalues of Hess_q (mass^2 in M_GUT^2); SM content is per root, in real dimensions.

| # | factor (monic in lam) | mult. | SM content per root | positivity |
|---|---|---|---|---|
| 0 | `lam = 0` | 35 | (1,1)_\|Y\|=0: 3, (1,1)_\|Y\|=1: 2, (3,1)_\|Y\|=2/3: 6, (3,2)_\|Y\|=1/6: 12, (3,2)_\|Y\|=5/6: 12 | zero modes |
| 1 | `lam = eps` | 4 | (1,2)_\|Y\|=1/2: 4 | sign alternation |
| 2 | `lam = 1/96*r0^2` | 14 | (1,1)_\|Y\|=2: 2, (6,1)_\|Y\|=4/3: 12 | sign alternation + Sturm |
| 3 | `lam^3 - (109/72 + 107/32*r0^2)*lam^2 + (5/9 + 4309/2304*r0^2 + 11/36*r0^4)*lam - (85/2592*r0^2 + 1079/10368*r0^4 + 13/4608*r0^6)` | 6 | (3,1)_\|Y\|=1/3: 6 | sign alternation + Sturm |
| 4 | `lam = 37/576*r0^2` | 18 | (3,1)_\|Y\|=4/3: 6, (6,1)_\|Y\|=1/3: 12 | sign alternation + Sturm |
| 5 | `lam = 353/3360*r0^2` | 12 | (6,1)_\|Y\|=2/3: 12 | sign alternation + Sturm |
| 6 | `lam = 1/2*r0^2` | 1 | (1,1)_\|Y\|=0: 1 | sign alternation + Sturm |
| 7 | `lam = eps + r0^2` | 4 | (1,2)_\|Y\|=1/2: 4 | sign alternation |
| 8 | `lam = 1/8*x0^2` | 1 | (1,1)_\|Y\|=0: 1 | sign alternation |
| 9 | `lam = 4*r0^2` | 1 | (1,1)_\|Y\|=0: 1 | sign alternation + Sturm |
| 10 | `lam^2 - (2 + 10/3*r0^2)*lam + (3/4 + 1/4*r0^2 + 13/48*r0^4)` | 4 | (1,2)_\|Y\|=1/2: 4 | sign alternation + Sturm |
| 11 | `lam = 1/2` | 12 | (3,2)_\|Y\|=1/6: 12 | sign alternation + Sturm |
| 12 | `lam = 1/2 + 1/96*r0^2` | 44 | (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | sign alternation + Sturm |
| 13 | `lam = 1/2 + 37/576*r0^2` | 48 | (1,2)_\|Y\|=1/2: 4, (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | sign alternation + Sturm |
| 14 | `lam = 1/2 + 353/3360*r0^2` | 12 | (3,2)_\|Y\|=1/6: 12 | sign alternation + Sturm |
| 15 | `lam = 5/8 + 37/576*r0^2` | 6 | (3,1)_\|Y\|=1/3: 6 | sign alternation + Sturm |
| 16 | `lam = 8/9` | 75 | (1,3)_\|Y\|=0: 3, (3,1)_\|Y\|=5/3: 6, (3,3)_\|Y\|=2/3: 18, (8,1)_\|Y\|=0: 8, (8,1)_\|Y\|=1: 16, (8,3)_\|Y\|=0: 24 | sign alternation + Sturm |
| 17 | `lam^2 - (148/45 + 3*r0^2)*lam + (32/15 + 256/45*r0^2)` | 6 | (3,1)_\|Y\|=2/3: 6 | sign alternation + Sturm |
| 18 | `lam = 1 + eps` | 6 | (3,1)_\|Y\|=1/3: 6 | sign alternation |
| 19 | `lam = 8/9 + 3*r0^2` | 2 | (1,1)_\|Y\|=1: 2 | sign alternation + Sturm |
| 20 | `lam = 1 + eps + r0^2` | 6 | (3,1)_\|Y\|=1/3: 6 | sign alternation |
| 21 | `lam^3 - (508/45 + 10*r0^2)*lam^2 + (256/9 + 4156/45*r0^2)*lam - (256/15 + 416/3*r0^2)` | 1 | (1,1)_\|Y\|=0: 1 | sign alternation + Sturm |
| 22 | `lam = 3/2` | 64 | (1,2)_\|Y\|=3/2: 4, (3,2)_\|Y\|=5/6: 12, (6,2)_\|Y\|=1/6: 24, (6,2)_\|Y\|=5/6: 24 | sign alternation + Sturm |
| 23 | `lam = 3/2 + 3*r0^2` | 12 | (3,2)_\|Y\|=1/6: 12 | sign alternation + Sturm |
| 24 | `lam = 2 + 1/96*r0^2` | 36 | (6,3)_\|Y\|=1/3: 36 | sign alternation + Sturm |
| 25 | `lam = 2 + 37/576*r0^2` | 18 | (3,3)_\|Y\|=1/3: 18 | sign alternation + Sturm |
| 26 | `lam = 2 + 353/3360*r0^2` | 6 | (1,3)_\|Y\|=1: 6 | sign alternation + Sturm |
| 27 | `lam = 12/5` | 8 | (8,1)_\|Y\|=0: 8 | sign alternation + Sturm |

## Point certificate: benchmark

Root counts (negative/zero/positive): `0/35/451`; distinct levels: `34`; factors irreducible over Q: `True`.

| factor | m^2/r0^2 | m/M_I | mult. | SM content | block weights |
|---|---|---|---|---|---|
| 0.0 | `0` | 0 | 35 | (1,1)_\|Y\|=0: 3, (1,1)_\|Y\|=1: 2, (3,1)_\|Y\|=2/3: 6, (3,2)_\|Y\|=1/6: 12, (3,2)_\|Y\|=5/6: 12 | Phi17 0.02857, Phi210 0.6603, S 0.02857, Sigma126bar 0.2825 |
| 1.0 | `1/100` | 0.1 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1 |
| 2.0 | `1/96` | 0.102062 | 14 | (1,1)_\|Y\|=2: 2, (6,1)_\|Y\|=4/3: 12 | Sigma126bar 1 |
| 3.0 | `0.0589507` | 0.242798 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 5.478e-08, Sigma126bar 1 |
| 4.0 | `37/576` | 0.253448 | 18 | (3,1)_\|Y\|=4/3: 6, (6,1)_\|Y\|=1/3: 12 | Sigma126bar 1 |
| 5.0 | `353/3360` | 0.324129 | 12 | (6,1)_\|Y\|=2/3: 12 | Sigma126bar 1 |
| 6.0 | `1/2` | 0.707107 | 1 | (1,1)_\|Y\|=0: 1 | Sigma126bar 1 |
| 7.0 | `101/100` | 1.00499 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1 |
| 8.0 | `25/8` | 1.76777 | 1 | (1,1)_\|Y\|=0: 1 | Phi17 1 |
| 9.0 | `4` | 2 | 1 | (1,1)_\|Y\|=0: 1 | S 1 |
| 10.0 | `11.3096` | 3.36297 | 4 | (1,2)_\|Y\|=1/2: 4 | Phi210 0.04147, Sigma126bar 0.9585 |
| 11.0 | `25/2` | 3.53553 | 12 | (3,2)_\|Y\|=1/6: 12 | Phi210 0.1071, Sigma126bar 0.8929 |
| 12.0 | `1201/96` | 3.53701 | 44 | (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1 |
| 13.0 | `7237/576` | 3.54461 | 48 | (1,2)_\|Y\|=1/2: 4, (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1 |
| 14.0 | `42353/3360` | 3.55036 | 12 | (3,2)_\|Y\|=1/6: 12 | Sigma126bar 1 |
| 3.1 | `14.9891` | 3.87157 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 0.06013, Sigma126bar 0.9399 |
| 15.0 | `9037/576` | 3.96096 | 6 | (3,1)_\|Y\|=1/3: 6 | Sigma126bar 1 |
| 16.0 | `200/9` | 4.71405 | 75 | (1,3)_\|Y\|=0: 3, (3,1)_\|Y\|=5/3: 6, (3,3)_\|Y\|=2/3: 18, (8,1)_\|Y\|=0: 8, (8,1)_\|Y\|=1: 16, (8,3)_\|Y\|=0: 24 | Phi210 1 |
| 17.0 | `24.1679` | 4.91609 | 6 | (3,1)_\|Y\|=2/3: 6 | Phi210 1 |
| 18.0 | `2501/100` | 5.001 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1 |
| 19.0 | `227/9` | 5.02217 | 2 | (1,1)_\|Y\|=1: 2 | Phi210 1 |
| 20.0 | `2601/100` | 5.1 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1 |
| 3.2 | `26.1429` | 5.11302 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 0.9399, Sigma126bar 0.06013 |
| 21.0 | `27.6835` | 5.26152 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |
| 22.0 | `75/2` | 6.12372 | 64 | (1,2)_\|Y\|=3/2: 4, (3,2)_\|Y\|=5/6: 12, (6,2)_\|Y\|=1/6: 24, (6,2)_\|Y\|=5/6: 24 | Phi210 1 |
| 23.0 | `81/2` | 6.36396 | 12 | (3,2)_\|Y\|=1/6: 12 | Phi210 0.9669, Sigma126bar 0.03307 |
| 10.1 | `42.0238` | 6.48257 | 4 | (1,2)_\|Y\|=1/2: 4 | Phi210 0.9585, Sigma126bar 0.04147 |
| 24.0 | `4801/96` | 7.0718 | 36 | (6,3)_\|Y\|=1/3: 36 | Sigma126bar 1 |
| 25.0 | `28837/576` | 7.07561 | 18 | (3,3)_\|Y\|=1/3: 18 | Sigma126bar 1 |
| 26.0 | `168353/3360` | 7.07849 | 6 | (1,3)_\|Y\|=1: 6 | Sigma126bar 1 |
| 27.0 | `60` | 7.74597 | 8 | (8,1)_\|Y\|=0: 8 | Phi210 1 |
| 17.1 | `61.0543` | 7.81373 | 6 | (3,1)_\|Y\|=2/3: 6 | Phi210 1 |
| 21.1 | `63.4807` | 7.96748 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |
| 21.2 | `201.058` | 14.1795 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |

## Point certificate: physical

Root counts (negative/zero/positive): `0/35/451`; distinct levels: `34`; factors irreducible over Q: `True`.

| factor | m^2/r0^2 | m/M_I | m [GeV] | mult. | SM content | block weights |
|---|---|---|---|---|---|---|
| 0.0 | `0` | 0 | 0 | 35 | (1,1)_\|Y\|=0: 3, (1,1)_\|Y\|=1: 2, (3,1)_\|Y\|=2/3: 6, (3,2)_\|Y\|=1/6: 12, (3,2)_\|Y\|=5/6: 12 | Phi17 0.02857, Phi210 0.6857, S 0.02857, Sigma126bar 0.2571 |
| 1.0 | `1/100` | 0.1 | 6.31386e+10 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1 |
| 2.0 | `1/96` | 0.102062 | 6.44405e+10 | 14 | (1,1)_\|Y\|=2: 2, (6,1)_\|Y\|=4/3: 12 | Sigma126bar 1 |
| 3.0 | `0.0590278` | 0.242956 | 1.53399e+11 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 7.168e-29, Sigma126bar 1 |
| 4.0 | `37/576` | 0.253448 | 1.60024e+11 | 18 | (3,1)_\|Y\|=4/3: 6, (6,1)_\|Y\|=1/3: 12 | Sigma126bar 1 |
| 5.0 | `353/3360` | 0.324129 | 2.0465e+11 | 12 | (6,1)_\|Y\|=2/3: 12 | Sigma126bar 1 |
| 6.0 | `1/2` | 0.707107 | 4.46457e+11 | 1 | (1,1)_\|Y\|=0: 1 | Sigma126bar 1 |
| 7.0 | `101/100` | 1.00499 | 6.34535e+11 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1 |
| 9.0 | `4` | 2 | 1.26277e+12 | 1 | (1,1)_\|Y\|=0: 1 | S 1 |
| 10.0 | `1.23365e+08` | 11107 | 7.01278e+15 | 4 | (1,2)_\|Y\|=1/2: 4 | Phi210 6.08e-09, Sigma126bar 1 |
| 11.0 | `1.23365e+08` | 11107 | 7.01278e+15 | 12 | (3,2)_\|Y\|=1/6: 12 | Phi210 1.216e-08, Sigma126bar 1 |
| 12.0 | `1.23365e+08` | 11107 | 7.01278e+15 | 44 | (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1 |
| 13.0 | `1.23365e+08` | 11107 | 7.01278e+15 | 48 | (1,2)_\|Y\|=1/2: 4, (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1 |
| 14.0 | `1.23365e+08` | 11107 | 7.01278e+15 | 12 | (3,2)_\|Y\|=1/6: 12 | Sigma126bar 1 |
| 3.1 | `1.54206e+08` | 12418 | 7.84052e+15 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 1.637e-08, Sigma126bar 1 |
| 15.0 | `1.54206e+08` | 12418 | 7.84052e+15 | 6 | (3,1)_\|Y\|=1/3: 6 | Sigma126bar 1 |
| 16.0 | `2.19315e+08` | 14809.3 | 9.35037e+15 | 75 | (1,3)_\|Y\|=0: 3, (3,1)_\|Y\|=5/3: 6, (3,3)_\|Y\|=2/3: 18, (8,1)_\|Y\|=0: 8, (8,1)_\|Y\|=1: 16, (8,3)_\|Y\|=0: 24 | Phi210 1 |
| 17.0 | `2.19315e+08` | 14809.3 | 9.35037e+15 | 6 | (3,1)_\|Y\|=2/3: 6 | Phi210 1 |
| 19.0 | `2.19315e+08` | 14809.3 | 9.35037e+15 | 2 | (1,1)_\|Y\|=1: 2 | Phi210 1 |
| 3.2 | `2.19315e+08` | 14809.3 | 9.35037e+15 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 1, Sigma126bar 1.637e-08 |
| 21.0 | `2.19315e+08` | 14809.3 | 9.35037e+15 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |
| 18.0 | `2.46729e+08` | 15707.6 | 9.91756e+15 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1 |
| 20.0 | `2.46729e+08` | 15707.6 | 9.91756e+15 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1 |
| 22.0 | `3.70094e+08` | 19237.8 | 1.21465e+16 | 64 | (1,2)_\|Y\|=3/2: 4, (3,2)_\|Y\|=5/6: 12, (6,2)_\|Y\|=1/6: 24, (6,2)_\|Y\|=5/6: 24 | Phi210 1 |
| 23.0 | `3.70094e+08` | 19237.8 | 1.21465e+16 | 12 | (3,2)_\|Y\|=1/6: 12 | Phi210 1, Sigma126bar 4.053e-09 |
| 10.1 | `3.70094e+08` | 19237.8 | 1.21465e+16 | 4 | (1,2)_\|Y\|=1/2: 4 | Phi210 1, Sigma126bar 6.08e-09 |
| 24.0 | `4.93459e+08` | 22213.9 | 1.40256e+16 | 36 | (6,3)_\|Y\|=1/3: 36 | Sigma126bar 1 |
| 25.0 | `4.93459e+08` | 22213.9 | 1.40256e+16 | 18 | (3,3)_\|Y\|=1/3: 18 | Sigma126bar 1 |
| 26.0 | `4.93459e+08` | 22213.9 | 1.40256e+16 | 6 | (1,3)_\|Y\|=1: 6 | Sigma126bar 1 |
| 27.0 | `5.9215e+08` | 24334.1 | 1.53642e+16 | 8 | (8,1)_\|Y\|=0: 8 | Phi210 1 |
| 17.1 | `5.9215e+08` | 24334.1 | 1.53642e+16 | 6 | (3,1)_\|Y\|=2/3: 6 | Phi210 1 |
| 21.1 | `5.9215e+08` | 24334.1 | 1.53642e+16 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |
| 21.2 | `1.97383e+09` | 44427.9 | 2.80511e+16 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1 |
| 8.0 | `3.1356e+09` | 55996.4 | 3.53553e+16 | 1 | (1,1)_\|Y\|=0: 1 | Phi17 1 |

## Triplet sub-ledger (issue #106)

The 10_H colour triplets (Re/Im H_0..5; C3 = 4/3, C2L = 0, Y^2 = 1/9) are exactly block-diagonal from the 126bar/210 triplets for every (r0, x0, eps): every Hessian monomial and every binding unit has a vanishing H x (non-H) block, and the five H-linear portal directions (ten re/im parameters, each a parameter of the scalar contract) have coefficient identically 0.  Their levels are 1 + eps (Re) and 1 + eps + r0^2 (Im) in M_GUT^2.

| unit | H x non-H block zero | Re H triplet | Im H triplet |
|---|---|---|---|
| O03 \|Phi17\|^2 | `True` | `0` | `0` |
| O04 \|S\|^2 | `True` | `0` | `0` |
| O05 N_Sigma | `True` | `0` | `0` |
| O06 N_H | `True` | `eps + 1/2*r0^2` | `eps + 1/2*r0^2` |
| O07 \|Phi\|^2 | `True` | `0` | `0` |
| O14 Sigma^dag M_Phi Sigma | `True` | `0` | `0` |
| O20 \|Phi17\|^4 | `True` | `0` | `0` |
| O23 \|S\|^4 | `True` | `0` | `0` |
| O27 I_1050bar | `True` | `0` | `0` |
| O27 I_2772bar | `True` | `0` | `0` |
| O27 I_4125 | `True` | `0` | `0` |
| O27 I_54 | `True` | `0` | `0` |
| O36 I_1(H) (quartic in H) | `True` | `0` | `0` |
| O36 I_54(H) (quartic in H) | `True` | `0` | `0` |
| O44 \|\|M_Phi Sigma\|\|^2 + \|\|C_Phi Sigma\|\|^2 | `True` | `0` | `0` |
| O46 (3/5) I_1 - I_54 = H^dag(\|Phi\|^2 - C(Phi))H | `True` | `1` | `1` |
| O48 J0 | `True` | `0` | `0` |
| O48 J2 | `True` | `0` | `0` |
| O48 J3 | `True` | `0` | `0` |
| O48 J4 | `True` | `0` | `0` |
| re::O12 2 Re[conj(H.H) conj(S)] | `True` | `-1/2*r0^2` | `1/2*r0^2` |

H-linear portals (coefficient): `im::O15_B01_Phi_Hdag_Sigma` = 0, `im::O28_B01_unique_Hdag_Sigma2_Sigmadag` = 0, `im::O38_B01_Phi_Hdag_Sigmadag` = 0, `im::O45_B01_Phi2_Hdag_Sigma_210_1050` = 0, `im::O45_B02_Phi2_Hdag_Sigma_210_1050` = 0, `re::O15_B01_Phi_Hdag_Sigma` = 0, `re::O28_B01_unique_Hdag_Sigma2_Sigmadag` = 0, `re::O38_B01_Phi_Hdag_Sigmadag` = 0, `re::O45_B01_Phi2_Hdag_Sigma_210_1050` = 0, `re::O45_B02_Phi2_Hdag_Sigma_210_1050` = 0

Phi/Sigma triplet mass matrix, operator provenance (fragment pairs: monomials):

- O05 N_Sigma: Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: 1, r0^2; Sigma126bar (6,1,1) = 6_Sigma x Sigma126bar (6,1,1) = 6_Sigma: 1, r0^2
- O07 |Phi|^2: Phi210 (15,1,3) x Phi210 (15,1,3): 1
- O14 Sigma^dag M_Phi Sigma: Phi210 (15,1,3) x Sigma126bar (10bar,1,3) = Delta_R: r0; Phi210 (15,1,3) x Sigma126bar (6,1,1) = 6_Sigma: r0; Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: 1
- O27 I_1050bar: Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: r0^2; Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (6,1,1) = 6_Sigma: r0^2; Sigma126bar (6,1,1) = 6_Sigma x Sigma126bar (6,1,1) = 6_Sigma: r0^2
- O27 I_2772bar: Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: r0^2; Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (6,1,1) = 6_Sigma: r0^2; Sigma126bar (6,1,1) = 6_Sigma x Sigma126bar (6,1,1) = 6_Sigma: r0^2
- O27 I_4125: Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: r0^2; Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (6,1,1) = 6_Sigma: r0^2; Sigma126bar (6,1,1) = 6_Sigma x Sigma126bar (6,1,1) = 6_Sigma: r0^2
- O44 ||M_Phi Sigma||^2 + ||C_Phi Sigma||^2: Phi210 (15,1,3) x Phi210 (15,1,3): r0^2; Phi210 (15,1,3) x Sigma126bar (10bar,1,3) = Delta_R: r0; Phi210 (15,1,3) x Sigma126bar (6,1,1) = 6_Sigma: r0; Sigma126bar (10bar,1,3) = Delta_R x Sigma126bar (10bar,1,3) = Delta_R: 1; Sigma126bar (6,1,1) = 6_Sigma x Sigma126bar (6,1,1) = 6_Sigma: 1
- O48 J0: Phi210 (15,1,3) x Phi210 (15,1,3): 1
- O48 J2: Phi210 (15,1,3) x Phi210 (15,1,3): 1
- O48 J3: Phi210 (15,1,3) x Phi210 (15,1,3): 1
- O48 J4: Phi210 (15,1,3) x Phi210 (15,1,3): 1

## B-violating propagator (3,1)_1/3

(3,1)_|Y|=1/3 sector: G = (Hess_q restricted to the isotypic subspace)^-1 in canonical chart fields, units M_GUT^-2; in u = D^-1 q it is A^-1, A = D^-2 H_u, with the D2 metric.  |G(Delta, 6_Sigma)| is the operator norm of the block from Delta_R = Sigma126bar (10bar,1,3) to 6_Sigma = Sigma126bar (6,1,1); by Schur it is the same scalar on each of the six real copies (one per support component), which is checked exactly.

- |G(Delta, 6_Sigma)|^2 = `1568*(32 + 117*r0^2)^2/(1360 + 4316*r0^2 + 117*r0^4)^2` M_GUT^-4
- |G(Delta, 6_Sigma)| = `28*sqrt(2)*(32 + 117*r0^2)/(1360 + 4316*r0^2 + 117*r0^4)` M_GUT^-2
- G(Delta, Delta) = `8*(2880 + 9232*r0^2 + 585*r0^4)/(r0^2*(1360 + 4316*r0^2 + 117*r0^4))` M_GUT^-2
- r0 -> 0 limit: `56*sqrt(2)/85` = 0.931717; exactly r0-independent: `False`; relative O(r0^2) coefficient `1313/2720`; monotone on (0, 1/5]: `True`, variation 0.0170096
- benchmark: |G| = 0.947565 M_GUT^-2 (relative deviation from the limit 0.0170096)
- physical: |G| = 0.931717 M_GUT^-2 (relative deviation from the limit 1.95648e-09)

Pati-Salam fragment weights of the Phi/Sigma (3,1)_1/3 levels (floats of exact values in Q or Q(lambda)):

- benchmark, factor 3, root 0 (m^2/r0^2 = 0.0589507): Phi210 (15,1,3) 5.47773e-08, Sigma126bar (10bar,1,3) = Delta_R 0.999995, Sigma126bar (6,1,1) = 6_Sigma 5.0314e-06
- benchmark, factor 3, root 1 (m^2/r0^2 = 14.9891): Phi210 (15,1,3) 0.0601331, Sigma126bar (10bar,1,3) = Delta_R 4.98176e-06, Sigma126bar (6,1,1) = 6_Sigma 0.939862
- benchmark, factor 3, root 2 (m^2/r0^2 = 26.1429): Phi210 (15,1,3) 0.939867, Sigma126bar (10bar,1,3) = Delta_R 1.04426e-07, Sigma126bar (6,1,1) = 6_Sigma 0.0601331
- benchmark, factor 15, root 0 (m^2/r0^2 = 9037/576): Phi210 (15,1,3) 0, Sigma126bar (10bar,1,3) = Delta_R 0, Sigma126bar (6,1,1) = 6_Sigma 1
- physical, factor 3, root 0 (m^2/r0^2 = 0.0590278): Phi210 (15,1,3) 7.1683e-29, Sigma126bar (10bar,1,3) = Delta_R 1, Sigma126bar (6,1,1) = 6_Sigma 4.96866e-20
- physical, factor 3, root 1 (m^2/r0^2 = 1.54206e+08): Phi210 (15,1,3) 1.63693e-08, Sigma126bar (10bar,1,3) = Delta_R 4.96866e-20, Sigma126bar (6,1,1) = 6_Sigma 1
- physical, factor 3, root 2 (m^2/r0^2 = 2.19315e+08): Phi210 (15,1,3) 1, Sigma126bar (10bar,1,3) = Delta_R 4.021e-28, Sigma126bar (6,1,1) = 6_Sigma 1.63693e-08
- physical, factor 15, root 0 (m^2/r0^2 = 1.54206e+08): Phi210 (15,1,3) 0, Sigma126bar (10bar,1,3) = Delta_R 0, Sigma126bar (6,1,1) = 6_Sigma 1

## Axion

- F_PQ^2 = |a|^2 = 32 r0^2 * 578 x0^2/(32 r0^2 + 578 x0^2) = 2 r0^2 x0^2 68^2/(16 r0^2 + 289 x0^2) (derived: `9248*r0^2*x0^2/(289*x0^2 + 16*r0^2)`)
- S phase fraction `289*x0^2/(289*x0^2 + 16*r0^2)`, Phi17 phase fraction `16*r0^2/(289*x0^2 + 16*r0^2)`
- Period modulo the gauge group: `2 pi/68`; v_a^2 = `2*r0^2*x0^2/(289*x0^2 + 16*r0^2)` (v_a^2 = F_PQ^2/68^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2)).
- F_PQ is NOT the axion decay constant: the periodicity scale is v_a = F_PQ/68, and f_a = v_a/N_DW is not computed here (it needs the fermion PQ charges / the QCD anomaly coefficient).
- benchmark: |a|^2 = `9248/7241` (1.27717 M_GUT^2), v_a^2 = `2/7241` M_GUT^2
- physical: |a|^2 = `383907334432559858000000000000000000000000/2960037988963184002619946567759493650314410616081` (1.29697e-07 M_GUT^2), v_a^2 = `83024942567595125000000000000000000000/2960037988963184002619946567759493650314410616081` M_GUT^2; illustrative F_PQ = 3.57166e+12 GeV, v_a = 5.25244e+10 GeV
- G4 cross-check: state `present`, available `True`, agrees `True`

## Routed caveats

- `phi17_benchmark_scale` (resolved: `False`): the physical member uses the canonical x0 = 10^17 GeV/M_GUT; the Phi17 radial level is x0^2/8 exactly (m = 10^17 GeV/sqrt(8)) and the whole tree certificate is parametric in x0; not wired
- `positivity_without_EWSB` (resolved: `False`): tree-level positivity certified for eps > 0; Electroweak symmetry is not broken at the witness: H = 0 and the doublet Re H_6..9 has tree mass^2 exactly eps > 0 (Im H_6..9: r0^2 + eps).  The EWSB member eps < 0 (O06 below 2|kappa| r0) is not certified here: its vacuum has H != 0 and needs exact units at H != 0 and a new G3/G4 certificate.
- `sub_M_I_coloured_126bar_states` (resolved: `False`): At tree level, coloured 126bar states lie below M_I for every 0 < r0 <= 1/5: (6,1)_4/3 at r0^2/96, (3,1)_4/3 and (6,1)_1/3 at 37 r0^2/576, (6,1)_2/3 at 353 r0^2/3360 and the (3,1)_1/3 root of the cubic with lambda/r0^2 -> 17/288; coloured_scalars_only_at_M_GUT is structurally False in this family (masses scale as r0^2 M_GUT^2)

## Disclosures

- Electroweak symmetry is not broken at the witness: H = 0 and the doublet Re H_6..9 has tree mass^2 exactly eps > 0 (Im H_6..9: r0^2 + eps).  The EWSB member eps < 0 (O06 below 2|kappa| r0) is not certified here: its vacuum has H != 0 and needs exact units at H != 0 and a new G3/G4 certificate.
- R1 (one-loop Coleman-Weinberg risk, not certified here): prior float estimates (scratch; Landau gauge, MS-bar, no fermions, tree couplings held fixed; effective-potential curvatures, not pole masses) give negative one-loop shifts of 5 to 63 times the tree values for the six light 126bar remnant multiplets ((6,1)_4/3, (1,1)_2, (3,1)_1/3, (6,1)_1/3, (3,1)_4/3, (6,1)_2/3) for every renormalisation scale in [M_I, M_GUT]; the shifts scale like r0^2, so the risk persists at the physical member.  An independent second method is being run separately; until it concludes, positivity beyond tree level is NOT certified.

## Scope

**exact_premises_reused**

- the committed binding units and their source tensors (g3_sm_pati_salam_exact_hessian_v20), whose compiler binding is float64 end to end (that module's scope); the degree <= 3 structure of their scalars is read off binding_units' code (rho = r0/4 and the singlet vevs, powers <= 3)
- the candidate coefficient map (g3_sm_pati_salam_candidate_v20) and the equality module's tangent matrix and charges

**not_proved_or_out_of_scope**

- positivity beyond tree level (R1 open, being checked separately)
- electroweak symmetry breaking (H = 0 at the witness; the eps < 0 member is not certified)
- uncertainties of the threshold spectrum (G6 acceptance); RG running and matching (G7); proton decay rates and Yukawas (G8)
- GeV values: illustrative (anchor M_GUT, which this field content does not reproduce)
- the axion decay constant f_a = v_a/N_DW (needs the fermion PQ charges / the QCD anomaly); F_PQ is 68 times the periodicity scale v_a and is not f_a
- the vacuum property of q0 outside the G3 witness window (for eps >= 12 - 2|kappa| r0 the parametric statements are about the Hessian at the stationary point only)
- G6 wiring: no ledger, gate, workflow or README change; G6 stays BLOCKED

**proved_exactly**

- tree-level Hessian spectrum at the stationary point q0 of V_PS,eps for all r0, x0, eps > 0 (kappa = -r0/4): 28 irreducible factors over Q(r0, x0, eps), 35 zero modes (34 eaten Goldstones + the axion, G4) and 451 strictly positive levels, SM labels from exact integer Casimirs; it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum (0 < eps < 12 - 2|kappa| r0)
- the binding-unit piece scalars are the monomials s(1, 1) r0^a x0^b (a, b <= 3) for all (r0, x0): exact agreement on the 4 x 4 grid r0 in {1, 2, 3, 5}, x0 in {1, 3, 7, 11}, given the by-construction premise that every binding_units scalar has degree <= 3 in r0 and in x0
- point certificates at the benchmark (r0 = 1/5, x0 = 1) and the physical member (r0 = 51544138/809635808795, x0 = 10^17 GeV/M_GUT), eps = r0^2/100: irreducibility, Sturm root counts, levels, labels and mixings
- issue #106 triplet sub-ledger: 10_H triplets exactly block-diagonal from the 126bar/210 triplets
- G(Delta, 6_Sigma) exactly; the axion norm F_PQ^2 in closed form, the period 2 pi/68 of the axion angle modulo the gauge group and v_a^2 = F_PQ^2/68^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2)

## Checks

| check | passed |
|---|---|
| `H_linear_portals_identically_zero` | `True` |
| `H_triplet_coordinates_are_singleton_triplet_components` | `True` |
| `H_triplet_levels_1_plus_eps_and_1_plus_r0sq_plus_eps` | `True` |
| `H_x_nonH_block_identically_zero` | `True` |
| `axion_PQ_sigma_part_in_gauge_span` | `True` |
| `axion_agrees_with_G4_report_when_present` | `True` |
| `axion_benchmark_9248_over_7241` | `True` |
| `axion_cartan_sum_is_pure_sigma_phase` | `True` |
| `axion_norm_equals_closed_form` | `True` |
| `axion_orthogonal_to_X_tangent` | `True` |
| `axion_period_2pi_over_68_and_v_a_closed_form` | `True` |
| `axion_so10_tangents_vanish_on_singlets` | `True` |
| `benchmark_28_factors_irreducible_over_Q` | `True` |
| `benchmark_34_distinct_levels` | `True` |
| `benchmark_all_roots_real` | `True` |
| `benchmark_block_weights_sum_to_one` | `True` |
| `benchmark_component_charpolys_equal_specialised_factors` | `True` |
| `benchmark_eigenspaces_semisimple` | `True` |
| `benchmark_factors_pairwise_distinct` | `True` |
| `benchmark_gradient_zero` | `True` |
| `benchmark_labels_confirmed_by_eigenspace_intersections` | `True` |
| `benchmark_root_counts_0_35_451` | `True` |
| `benchmark_triplet_fragment_weights_sum_to_one` | `True` |
| `casimir_integer_generators_equal_candidate_chart_generator` | `True` |
| `compiler_float64_light_spectra_match_parametric_levels_at_4_r0` | `True` |
| `component_charpolys_equal_product_of_factors` | `True` |
| `direct_physical_gradient_zero_and_coverage` | `True` |
| `every_nonzero_parameter_in_exactly_one_unit` | `True` |
| `every_other_factor_sign_alternation_certified` | `True` |
| `every_r0_only_factor_sturm_certified_on_0_lt_r0_le_1_5` | `True` |
| `every_unit_H_block_decoupled` | `True` |
| `factor_leading_coefficients_constant` | `True` |
| `factor_table_matches_pinned_closed_forms` | `True` |
| `gradient_vanishes_identically_in_r0_x0_eps` | `True` |
| `hessian_monomials_are_1_r0_r0sq_eps_x0sq` | `True` |
| `irreducible_factors_28` | `True` |
| `labels_casimirs_block_diagonal_on_support_components` | `True` |
| `labels_every_joint_eigenvalue_is_a_standard_sm_label` | `True` |
| `labels_isotypic_charpolys_factor_into_global_factors` | `True` |
| `labels_isotypic_multiplicities_sum_to_component_multiplicities` | `True` |
| `labels_joint_casimir_eigenspaces_span_each_component` | `True` |
| `labels_label_multiplicities_are_whole_sm_multiplets` | `True` |
| `labels_pencil_leaves_every_isotypic_piece_invariant` | `True` |
| `labels_sm_casimirs_commute_with_every_hessian_monomial` | `True` |
| `light_triplet_branch_17_over_288` | `True` |
| `linear_factors_24` | `True` |
| `nonlinear_discriminants_positive_on_0_lt_r0_le_1_5` | `True` |
| `phi_sigma_triplet_sector_six_copies_with_four_fragments` | `True` |
| `physical_28_factors_irreducible_over_Q` | `True` |
| `physical_34_distinct_levels` | `True` |
| `physical_M_GUT_matches_candidate_anchor` | `True` |
| `physical_all_roots_real` | `True` |
| `physical_block_weights_sum_to_one` | `True` |
| `physical_canonical_phi17_scale_matches` | `True` |
| `physical_canonical_x0_matches_float` | `True` |
| `physical_component_charpolys_equal_specialised_factors` | `True` |
| `physical_eigenspaces_semisimple` | `True` |
| `physical_factors_pairwise_distinct` | `True` |
| `physical_gradient_zero` | `True` |
| `physical_labels_confirmed_by_eigenspace_intersections` | `True` |
| `physical_r0_physical_matches_candidate_report` | `True` |
| `physical_root_counts_0_35_451` | `True` |
| `physical_triplet_fragment_weights_sum_to_one` | `True` |
| `positive_count_451_parametric` | `True` |
| `propagator_identical_in_all_six_copies` | `True` |
| `propagator_limit_6272_over_7225` | `True` |
| `propagator_monotone_on_0_lt_r0_le_1_5` | `True` |
| `propagator_squared_closed_form` | `True` |
| `sub_M_I_coloured_classification_complete` | `True` |
| `sub_M_I_coloured_content_exact` | `True` |
| `support_components_65` | `True` |
| `symbolic_equals_committed_exact_hessian_eps_0` | `True` |
| `symbolic_equals_committed_exact_hessian_eps_r0sq_over_100` | `True` |
| `symbolic_equals_committed_exact_hessian_eps_r0sq_over_10e6` | `True` |
| `symbolic_equals_direct_recomputation_at_off_benchmark_point` | `True` |
| `symbolic_equals_direct_recomputation_at_physical_member` | `True` |
| `symbolic_hessian_exactly_symmetric` | `True` |
| `total_dimension_486` | `True` |
| `unit_piece_scalars_are_monomials_of_degree_le_3_on_4x4_grid` | `True` |
| `zero_factor_is_lambda_with_multiplicity_35` | `True` |
| `zero_modes_are_broken_generators_plus_X_PQ` | `True` |

Runtime: 37 s.
