# Extensive confirmation / falsification campaign

**Status:** PASS — 53 checks, 0 failed
**Unittest discovery:** 261 tests available in package

## Coverage

- A anomaly conventions
- B portal uniqueness (portal basis) + free-lattice honesty
- C Monte Carlo mass blocks
- D operator frontier P<=7
- E kernel SciPy cross-check
- F flavour multi-seed
- G seesaw v_R scan
- H Wilson |C| boundary
- I haloscope sensitivity grid
- J injected engine failures
- K golden anchors
- L Z17 residue uniqueness
- M lifetime floors + Clifford
- N soft-overclaim detectors
- O physical portal current + corrected tan(beta) profile

## Section results

### A_anomaly — PASS (5/5)
- [PASS] cancel under permutation ((1, 16), (14, 3), (1, -18)): `(0, 0, 0)`
- [PASS] cancel under permutation ((14, 3), (1, 16), (1, -18)): `(0, 0, 0)`
- [PASS] cancel under permutation ((1, -18), (14, 3), (1, 16)): `(0, 0, 0)`
- [PASS] global X -> -X keeps cancellation: `both sides flip`
- [PASS] one-pair discriminant remains -15: `-15`

### B_portal — PASS (4/4)
- [PASS] canonical triple unique in stated portal basis: `[((1, 16), (14, 3), (1, -18))]`
- [PASS] enlarged portal basis cannot create one-pair solution: `discriminant -15 is portal-independent`
- [PASS] free Diophantine lattice admits alternate cubic=1037 triples: `found_other=2/5000 (uniqueness is NOT lattice-level)`
- [PASS] none of those free-lattice alternates lie in the portal catalogue: `portal_alts=0, canonicalish=0`

### C_mass — PASS (3/3)
- [PASS] 200 random 5x2 blocks always leave 3 light families: `unique_counts=[3]`
- [PASS] rank-1 adversarial block leaves 4 lights (detected): `rank=1`
- [PASS] generic assumption is required for 3-family claim: `non-generic rank drops are physically tuned, not accidental`

### D_frontier — PASS (3/3)
- [PASS] no vacuum closure through P=7: `None`
- [PASS] first closure at P=8 with Q_PQ=-68: `Closure(planck_power=8, pq=-68, spectator_vector=0, operators=(Operator(dimension=5, x=0, pq=-17, spectator_vector=-1, n_fermions=2, labels=('Q', 'b', 'Sd', 'Sd')), Operator(dimension=5, x=0, pq=-17, spectator_vector=-1, n_fermions=2, labels=('Q', 'b', 'Sd', 'Sd')), Operator(dimension=5, x=0, pq=-17, spectator_vector=-1, n_fermions=2, labels=('Q', 'b', 'Sd', 'Sd')), Operator(dimension=5, x=0, pq=-17, spectator_vector=-1, n_fermions=2, labels=('Q', 'b', 'Sd', 'Sd')), Operator(dimension=8, x=0, pq=0, spectator_vector=4, n_fermions=4, labels=('s', 's', 's', 's', 'Sd', 'Sd'))))`
- [PASS] P<=7 still empty with dim<=20 catalogue: `frontier_states=36`

### E_kernel — PASS (3/3)
- [PASS] SciPy log-quadrature matches decimal kernel: `rel=3.331e-16, analytic=1.000000e+00, numeric=1.000000e+00`
- [PASS] chirality chain positive across mf scan: `[True, True, True, True, True]`
- [PASS] P=8 amplitude finite and positive: `9.817785e-52`

### F_flavour — PASS (5/5)
- [PASS] package best fit is finite and perturbative: `chi2=0.020, tag=natural_1e14, y126=0.3453`
- [PASS] corrected exact v_R=v_S benchmark is not viable (chi2>30): `chi2_v20=594.240`
- [PASS] multi-seed v20-scale fits remain finite: `min=113.934, median=2178.792`
- [PASS] natural 1e14 scale often beats or matches v20 median: `med_nat=5.174, med_v20=2178.792`
- [PASS] at least one multi-seed start yields perturbative v20 fit: `perturbative_seeds=10/10`

### G_seesaw — PASS (2/2)
- [PASS] Type-I Dirac yukawa perturbative from 1e11 to 1e15 GeV: `[('1.0e+11', '0.013'), ('6.3e+11', '0.032'), ('1.0e+12', '0.041'), ('1.0e+13', '0.129'), ('1.0e+14', '0.407'), ('1.0e+15', '1.287')]`
- [PASS] single-scale v_R=v_S is more stressed than 1e14 in full Clebsch fit: `documented by flavour package chi2_v20 > chi2_natural`

### H_wilson — PASS (4/4)
- [PASS] O(1) mild-shrink safe: `1.349702770863388`
- [PASS] O(1) mild-grow safe: `0.7409038653453398`
- [PASS] critical Planck |C| for quality violation is >> 1: `C_crit_lower_bound~1.861e+07`
- [PASS] forced 1e6 scenario remains tracked: `safe=True`

### I_halo — PASS (3/3)
- [PASS] benchmark frequency inside 36.6–37.6 GHz: `37.1161`
- [PASS] full-scale grid can reach coupling in some configs: `reaches=3/18`
- [PASS] mock scan disclaimer forbids discovery claim: `MOCK DATA ONLY. This is a software radiometer simulation, no`

### J_inject — PASS (3/3)
- [PASS] so10_axion_v20_engine.py inject-failure exits nonzero: `rc=1`
- [PASS] so10_axion_v19_engine.py inject-failure exits nonzero: `rc=1`
- [PASS] so10_axion_v17_engine.py inject-failure exits nonzero: `rc=1`

### K_golden — PASS (4/4)
- [PASS] light anomaly matches golden: `(-34, -272, -16592)`
- [PASS] M_I golden: `6.313855e+11`
- [PASS] M_GUT golden: `9.917565e+15`
- [PASS] P=8 reconstruction group_ok: `group`

### L_z17 — PASS (2/2)
- [PASS] unique residue pair {2,11}: `[(2, 11)]`
- [PASS] minimal k=5: `k=5+17m`

### M_lifetime — PASS (3/3)
- [PASS] all components decay at lambda=1e-8: `{'Q_L': '2.495e-24', 'L_L': '7.486e-24', 'u_R': '4.991e-24', 'd_R': '4.991e-24', 'e_R': '1.497e-23', 'nu_R': '1.497e-23'}`
- [PASS] portal floor +1% decays all components before 1s: `floor=3.869e-20`
- [PASS] every 16 index has strength 10: `Clifford identity`

### N_overclaim — PASS (4/4)
- [PASS] detector armed: correct inequality is Gamma <= massless benchmark: `armed`
- [PASS] detector armed: v20 'perturbative to M_Pl with alpha=1/40' claim fails under single RG trajectory: `armed`
- [PASS] detector armed: manuscript portal list is incomplete: `armed`
- [PASS] continuous alpha_inv(vPhi) != 40: `16.647`

### O_fermion — PASS (5/5)
- [PASS] moving-frame identity is algebraically verified: `worst=5.984e-11`
- [PASS] physical projected current remains portal dependent: `shift=4.000e+00`
- [PASS] random Yukawa misalignment can generate FCNC current: `3.252e+00`
- [PASS] aligned central tan(beta)=1.5 benchmark reproduced: `(0.040723981900,-0.472149321267,0.006583710407)`
- [PASS] corrected fixed-vR profile does not establish unique tan(beta): `best tanbeta=2.000, chi2=51.103`

## Cannot confirm in-repo

- physical detection of the 153.5 ueV axion
- lattice (13,-3) string network
- independent human referee diagrammatic audit

## Verdict

Extensive in-repo confirmation battery completed. Hard internal structure survives adversarial attacks; soft overclaims remain correctly flagged. The corrected single-scale flavour benchmark fails and full fermion matching is open; only the core field-theory construction is internally confirmed.
