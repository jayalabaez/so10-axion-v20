# SUSY V38 G1 ultraviolet-origin audit

- Status: `V38_G1_4D_HIGGSED_U1X_NO_GO_PROVED__U1H_ISOLATED_PARENT_AUDITED__5D_ETA_INFLOW_EFT_PACKET_EXPLICIT__FULL_G1_FAIL_CLOSED`
- Core: `0e420f82ec85ad41e64cc4724d9e6dc89e131541ec1d0cc6c0397ead7252ec3f`
- Full G1 closed: **no**.

## Exact result

With primitive continuous U(1)_X lifts of the V37 Z66 charges, the doubled mixed Pati--Salam anomaly is `[-8, -8, -8]`.  It is nonzero modulo both `66` and the even-order relaxed modulus `33`. Therefore an ordinary four-dimensional Higgsed-U(1)_X parent cannot cancel it with only massive Pati--Salam thresholds while retaining the exact Z66 selector.

The proof assumes Pati--Salam is unbroken at the threshold, all breaking VEVs have charge in `66 Z`, and every added non-singlet has an ordinary full-rank symmetry-preserving mass matrix.  Each representation block then shifts the mixed anomaly by zero modulo 66 (at most modulo 33 for the familiar even-order real-representation ambiguity).  The V37 residue is `-8`, so it cannot be removed.  A single ordinary compact GS axion with charge 66 also fails: its integer level would have to solve `66 k=8`.

## What is now explicit

The Z85 spectator has a clean isolated U(1)_H parent: its cubic, gravitational, and Pati--Salam mixed gauge anomalies vanish, and a charge `+/-85` Higgs pair leaves Z85.  Its one-loop supersymmetric Abelian coefficient is `b_H=23974`; maintaining two decades of perturbative headroom requires approximately `g_H < 0.02674` at the breaking scale.  The simultaneous U(1)_X x U(1)_H theory still has cross anomalies and is not claimed complete.

A local five-dimensional interval EFT is also made concrete.  Place the V37 packet on one boundary and an exact inverse-anomaly PS-conjugate packet on the other.  Every listed continuous U(1), mixed, and chiral-matter R row then sums to zero, and an APS/Dai--Freed eta-invariant supplies the quantized inflow description.  This is a valid anomaly-EFT scaffold, not a microscopic UV completion: the mirror-wall gap, full R/gravitino/PS-centre bordism, KK thresholds, and all V37 dynamical matching remain open.

## Decision

V38 closes a false route rather than hiding it: a conventional 4D Higgsed U(1)_X solution is excluded under stated assumptions.  The viable route is an explicitly specified 5D inflow/topological completion, which still needs microscopic dynamics before G1 can be promoted.

References: [Hsieh, discrete gauge anomalies](https://arxiv.org/abs/1808.02881), [Ibanez, heavy fermions and discrete anomalies](https://arxiv.org/abs/hep-ph/9210211), [Witten--Yonekura, eta-inflow](https://arxiv.org/abs/1909.08775), and [von Gersdorff--Quiros, localized orbifold anomalies](https://arxiv.org/abs/hep-th/0305024).

5D continuous-row cancellation: `true`.
