# SUSY V39 live-soft and boundary audit

- Status: `V39_ACTIVE_Z3_SOURCE_AND_FORMAL_SOFT_TWO_LOOP_RGES_DERIVED__5D_GAUGINO_MEDIATION_TRAJECTORY_SOLVED__SINGLET_AND_POLE_BOUNDARY_OPEN`
- Core: `9748910f3a511307f12d6c39c20aa8db9cc86ec2d7bfb4cf45cc66af5c82e40d`
- Full G2/G3/G4/G6 closure: **no**.

## Live result

SARAH initialized both the declared active V39 source and a transient
formal-soft mirror of its 21-field split-six/Z3 field content, then
completed its two-loop calculation.  The derived soft rows are trilinear
`27`, bilinear `1`, linear
`3`, scalar-mass `28`, and
gaugino `3`.

## 5D gaugino-mediation witness

For `gU=0.7`, `Mc/vPS=100.0`
and `M1/2=50000.0 GeV`, assuming `U1X,U1H` are broken
or localized above `Mc`, the analytic gauge-only
one-loop solution gives positive soft mass-squared to every PS-charged chiral
multiplet.  The exact singlets remain unlifted:
`X, P, Nv, Pbar, Zp, A2, A32, A15, A17, A16, D2, Db2, D17, Db17, D16, Db16`.

This is the decisive boundary: gaugino mediation is a viable calculational
route, but it cannot determine the PQ/driver/anomalon vacuum, mu/Bmu, the
broken-phase pole matrices, or threshold covariance without a microscopic
singlet mediation sector.  No full gate is promoted.

Literature basis: [5D SO(10) gaugino mediation](https://arxiv.org/abs/0808.3598),
[orbifold SO(10)/Pati--Salam construction](https://arxiv.org/abs/0803.1758), and
[SARAH](https://arxiv.org/abs/0909.2863).
