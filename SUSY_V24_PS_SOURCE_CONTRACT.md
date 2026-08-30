# SUSY V24 Pati--Salam source contract

Status: `V24_PS_Z11_NONZERO_W_SOURCE_LANDED__G1_G2_PARTIAL__GS_MODULUS_UV_AND_FULL_COMPONENT_HESSIAN_OPEN`

This is a constructive Kawamura--Raby Pati--Salam source architecture with the derived anomaly-universal `Z4R x Z11` selector. It has a symmetry-complete, nonzero superpotential and genuinely initializes in SARAH. The `Z11` selector is a new derived variant, not the paper's published `Z5` benchmark.

## Exact source result

- All `18` gauge- and selector-allowed renormalizable operator classes are explicit, including `X H^2`, `X Sigma^2`, all fourth-family Yukawas, all PQ mass rows, and all neutral-messenger mixings.
- Every renormalizable PS contraction has singlet multiplicity one. The original `(Sbc Qc)^2/Lambda` EFT operator has two bosonic PS contractions; singlet-`N` exchange selects one normalized channel and can have family rank three.
- The exact constructed 23-component PS-breaking-sector `W_IJ` has rank `14/23`; its `9` null directions are the gauge Goldstone multiplets. This is not a full-theory or gauge-fixed scalar-potential Hessian.
- SARAH attestation: exit `0`, `SARAH 4.15.3`, processed superpotential terms `18`, all required checks `True`. The SARAH-only sextet symbol is `Sig6`; the physics ledgers retain `Sigma`.
- The exhaustive Table-6 redressing contains `18` superpotential and `41` Kahler bases. Pure `P` breaking first occurs as `P^11/Lambda^8` in W and as `w0 P^11` in K. The source scaling gives the conditional P-only estimate `log10 Delta theta = -25`; physical mixed-axion quality is not closed.
- `<P>` leaves the exact `(Z4R)^2` matter parity. Every odd-parity RPV monomial remains forbidden after arbitrary `P` and `w0` insertions.
- `gcd(11,4)=1` says a `P^11` perturbation would lift a purely `P`-axion `N_DW=4` potential. It is not a physical wall proof here: anomalous `Z11` requires a shifting GS axion, so the actual axion mixing and wall-vacuum structure remain open.

## Honest anomaly boundary

- `Z4R`: mixed anomalies are universal `{'SU4': 1, 'SU2L': 1, 'SU2R': 1}` modulo 2, but nonzero; Green--Schwarz cancellation is required.
- `Z11`: signed mixed representatives are `{'SU4': -2, 'SU2L': -2, 'SU2R': -2}`, hence universal residue `{'SU4': 9, 'SU2L': 9, 'SU2R': 9}`. Its signed gravitational representative is `-15`, with residue `7 = 24*9 mod 11`.
- The visible `Z4R` gravitational representative is `20` (residue `0 = 24*1 mod 2`).
- An explicit non-SARAH GS topological source contract is landed with `k4=kL=kR=1` and shifts `Delta theta_GS=-1/2` under `Z4R`, `-9/11` under `Z11`. A dynamical modulus, its stabilization, and a UV realization are deliberately not claimed.

## Remaining boundary

G1 and G2 are both partial. The finite selector, nonzero source, normalized renormalizable tensors, Table-6 higher-operator census, continuous/discrete anomaly ledgers, and generic breaking ranks are real. The dynamical GS axion/modulus, stabilization/UV realization, physical axion quality and wall structure, bases beyond the audited sector, a gauge-fixed full component Hessian, soft/PQ vacuum, SM matching, and pole spectrum remain open.

Core SHA-256: `d408aa7d7d3096ac917f5bd6f4f37576aace4cd78709bf4810b8e036dc2d93a8`

Primary source: https://arxiv.org/abs/2009.04582
