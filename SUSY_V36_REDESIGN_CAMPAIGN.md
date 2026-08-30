# SUSY V36 theory redesign

- Status: `V36_REDESIGN_EXECUTED__EXACT_Z66_SELECTOR__MINIMAL_FIVE_ANOMALON_PURE_FINITE_COUNTERCLASS__FULL_RANK_RENORMALIZABLE_MASSES__LOCAL_TWO_RADIAL_FTERM_RANK4__LIVE_SARAH_ONE_TWO_LOOP_RGES__NONUNIVERSAL_GS_FULL_BORDISM_AND_QUALITY_SEQUESTERING_CONDITIONAL__ESTABLISHED_FULL_PREDICTIVE_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY`
- Core: `1ceca3ef915150b380ed278162412381e9917cf1ae2a768eb1cc083d112b3f4d`
- Declared 4D EFT gates: **0/8**
- Established full predictive gates: **0/8**

## Decision

Adopt V36 as the next research EFT candidate.  It closes the pure finite selector and anomalon-mass subproblems, defines the conditional mixed GS arithmetic explicitly, and rejects a direct charged repair that would erase the QCD axion.  G1 and the complete theory remain open.

## What changed

The old `Z33` selector and the anomalon parity are one exact untwisted `Z66`,
with charge map `q66=2*q33+33*p`.  The live source contains 20 chiral
superfields and 34 processed renormalizable superpotential terms.  `P` and
`Pbar` have charges 2 and 64, so their VEVs leave a residual `Z2`; every new
anomalon is odd and every original field is even.

The exact Spin x Z66 conditions evaluate to
`2 Delta_s1 = 0 mod 66`
and
`(n^2+3n+2) Delta_s3 = 0 mod 396`.
The old Z33 subgroup audit also gives zero linear residue mod 33 and zero cubic
residue mod 99.

## Minimal anomaly countersector

After adding `Pbar`, an exhaustive unordered charge search proves that fewer
than five PS-singlet anomalons cannot simultaneously cancel the pure finite
class and have a generic full-rank renormalizable mass matrix.  The five
minimal witnesses are [2, 6, 16, 26, 32], [2, 15, 16, 17, 32], [5, 8, 16, 26, 27], [9, 14, 16, 20, 23], [12, 14, 16, 20, 20].  V36 selects `[2,15,16,17,32]`, lifted to
Z66 charges `[37,63,65,1,31]`.

In the order `(A2,A15,A16,A17,A32)`, the mass determinant is
`a^2*b^2*c`.  It is nonzero for `a*b*c != 0`; the allowed `d`
and `mu` entries are retained but are not needed for rank.

## Vacuum and quality

The two neutral drivers constrain `U=Sbar*S` and `V=P*Pbar`.  When
`det(K)=kappaPS*rhoPQ-kappaPQ*rhoPS != 0`, the local driver/radial holomorphic
Hessian has rank 4.
The PQ Goldstone multiplet remains, as it should; saxion stabilization and
global vacuum selection still require the Kahler/soft sector.

The first pure VEV-supported PQ-breaking superpotential monomials are
`P^33` and `Pbar^33`.  At the frozen benchmark, a unit coefficient gives
`log10|theta_shift|=-160.604`.
The complete singlet operator ring breaks the optimally chosen PQ current first
at degree 10, through
operators containing heavy anomalons.  They vanish on the classical `A_i=0`
vacuum, but their soft/loop matching is not known.  A shifting GS field can also
dress lower powers, so all-harmonic quality, GS stabilization, and cosmology
remain open.

## Live symbolic model and matching

SARAH 4.15.3 initialized `PSZ4RZ66SUSYV36` and derived one- and two-loop
RGEs for 3 gauge, 28
trilinear, 2 bilinear, and
3 linear coupling rows.  Soft terms
remain intentionally disabled because no mediation source has been derived.

V36 freezes the exact PS-to-SM gauge matching, vectorlike light/heavy projectors,
the seesaw bridge, and the split vectorlike thresholds.  It forbids independent
ad-hoc threshold knobs.  The three irreducible PS-breaking flavour Wilson
matrices remain explicit likelihood inputs rather than fake predictions.

## Important rejected repair

One vectorlike `16+16bar` plus `Pbar` cancels all Z33 matter anomalies and is a
complete SO(10) threshold.  It is **not** adopted: invariance of `X*P*Pbar` and
`Pbar*16*16bar` forces its continuous PQ anomaly to cancel the visible QCD-PQ
anomaly exactly.  The surviving current has `N=0`, so the QCD axion is lost.

More elaborate charged matter can retain the axion and remove the GS sector
algebraically, but simultaneous exact-selector and Z4R cancellation forces
`Delta b_a >=29` for every PS factor in the vectorlike mass-pair ansatz.  The
optimistic one-loop pole ratios are already below 25, far short of the required
cutoff ratio 100.  This is why V36 keeps the explicit conditional topological
sector instead of hiding a Landau-pole problem in large representations.

## Gate verdict

G1 is **not closed**.  Its pure finite counterclass and full-rank anomalon-mass
subproblems are explicit, and the nonuniversal GS arithmetic is defined, but a
microscopic GS/Stueckelberg origin and the full `Spin^Z4R x Z66` bordism audit
remain required.  G2--G8 also remain open.  The strict complete-theory count is
therefore **0/8**.

## Replay

```bash
python -B susy_v36_redesign_campaign.py --check
python -m pytest -q test_susy_v36_redesign_campaign.py
wolframscript -file tools/validate-susy-v36-redesign.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3
```

## Primary sources

- [Discrete gauge anomalies revisited](https://arxiv.org/abs/1808.02881)
- [Discrete R symmetries for the MSSM and its singlet extensions](https://arxiv.org/abs/1102.3595)
- [Discrete R Symmetries and Anomalies](https://arxiv.org/abs/1212.4371)
- [Heavy fields and the axion quality problem](https://arxiv.org/abs/2212.00102)
- [Two-loop RGEs for softly broken N=1 SUSY](https://arxiv.org/abs/hep-ph/9311340)
