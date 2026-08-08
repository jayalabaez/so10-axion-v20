# Exact rank-one SU(4) Phi210 quadratic basis -- v20

**Status:** `EXACT_RANK1_SU4_PHI210_QUADRATIC_BASIS_CERTIFIED`

The complete 45-dimensional real symmetric SU(4)-invariant quadratic-form space on the live canonical Phi210 chart is now explicit and exact. This is basis infrastructure only: the augmented SOS SDP, the arbitrary-Phi bound, and G3 remain open.

## Exact construction

- canonical live space: `Phi210 = Lambda^4(R^10)`;
- Cartan weight-zero symmetric monomials: `551`;
- remaining exact constraint rank/nullity: `506/45`;
- explicit primitive integer matrices: `45` of shape `210 x 210`;
- live invariance: every matrix commutes with all `15` exact Phi210 stabilizer generators;
- exact independence: upper-triangle rank `45` modulo `1000003`;
- polynomial convention: diagonal `Q_ii`, off-diagonal `2 Q_ij`, with primitive coefficient rows exposed by the API;
- completeness census: `(10+10+3+1)+(16+1+4)=45`;
- ordered basis SHA-256: `27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694`;
- exact Gram SHA-256: `17d352a43fc0a555df3d2abbe0f59f1ceecc89498648a84703bcf0ccd9c23124`.

## Scientific boundary

- invariant quadratic basis: `CLOSED`;
- full augmented Schur/SOS SDP: `OPEN`;
- arbitrary-real-Phi lower bound: `OPEN`;
- G3: `OPEN`;
- whole theory: neither validated nor excluded by this result.

**Next:** Use this ordered reconstruction basis together with the exact aligned carrier actions to assemble the full augmented SU(4)-equivariant degree-2 Schur/SOS system, including every real/Hermitian isotypic PSD block and every homogenizing cross term.
