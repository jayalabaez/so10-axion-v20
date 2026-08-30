# SUSY V54 non-Abelian filter route audit

Core: `b6f8f135b794c1ac25a478af90dbf18aa29b1fa791ab11cf59fc46829f051331`

Status: `V54_SU2F_NONABELIAN_FILTER__CHARGED_Z8_SOURCE_SPURION__EXACT255_DECLARED_ACTION_RANK215_NULL40_GAUGE36_PLUS_WEAK4__GENERIC_ALLOWED_S_H_A_H_FILLS_WEAK_KERNEL__NO_GATE_PROMOTION`

## Exact redesign witness

The gauged `SU(2)_F` filter uses `H=(10,2)`, three singlet vectors `U,V,W`,
two flavor doublets `P,Q`, and a neutral driver.  A charge-4 `Z8` singlet `S`
replaces the incompatible A/B cross coefficients by `SAB` and `SEAB/Lambda`.

The 178-coordinate source has rank 145 and nullity 33;
its kernel is exactly the rank-33 broken Spin(10) orbit.  The SU(2)_F driver has
rank 2 and nullity 3, exactly its complexified gauge orbit.

The 50-coordinate filter has rank 46, color rank 30,
and weak rank 16 with weak nullity 4.
Including anomaly spectators, the declared 255-coordinate action
has rank 215 and nullity 40 = 36 gauge + 4 weak.

## Fatal symmetry completion

The same selector necessarily allows `S epsilon_ab H_a^T A H_b / Lambda`.
The identity is `s+a+b=0`, `2h+b=0`, `2b=0`, hence
`s+2h+a=-2b=0`.  Since the exact A vacuum is nonzero in the weak blocks,
this operator raises the weak rank to 20 and the full
same-action rank to 219; only the 36 gauge
directions remain.  `S(16_F)^4/Lambda^2` is also allowed at degree five.

## Anomalies and running

One 10 spectator pair of charges (1,3) and one singlet pair of charges (0,4),
massive through S, cancel the conservative mod-8 mixed, gravitational, and cubic
residues.  The SU(2)_F Witten count is 12 and its one-loop coefficient is zero.
The anomaly-repaired EFT has Spin(10) b=21 and pole ratio
1159.16.  A clean two-45 renormalizable completion
has b=37 and pole ratio 54.84.

## Verdict

The SU(2)_F filter and charged-spurion source have an exact same-action witness, but the selector itself allows S H A H, which removes the Higgs pair.  The minimal source-spurion redesign is therefore rejected.
No G1-G8 gate is promoted.

Primary comparisons: [Chen-Zhang](https://arxiv.org/abs/1410.5625),
[SU(2) global anomaly check](https://arxiv.org/abs/hep-lat/0209098), and
[four-dimensional R-symmetry no-go](https://arxiv.org/abs/1109.4797).
