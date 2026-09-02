import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v97_equivariant_mass_defect_index_audit as audit


class TestV97EquivariantMassDefectIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_pinned_parents_and_roundtrip(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["embedded_v96_transport_core"], audit.TRANSPORT_CORE)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        audit.validate_certificate(self.report)

    def test_rehashed_parent_change_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v96_master"][0]:
                value = json.loads(result)
                value["next_required_action"]["id"] = "CLOSE_G1"
                value["core_sha256"] = audit.canonical_sha(value)
                return json.dumps(value)
            return result
        with patch.object(Path, "read_text", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_frozen_source_pin_change_rejected(self):
        original = audit.file_sha
        def changed(path):
            return "0"*64 if path.name == "v96_local_transport_quantization_audit.py" else original(path)
        with patch.object(audit, "file_sha", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_clifford_principal_symbol_and_mass(self):
        row = self.report["conditional_Dirac_operator"]
        matrices = {k: sp.Matrix(v) for k, v in row["Clifford_matrices"].items()}
        kx, ky, mr, mi = sp.symbols("kx ky mr mi", real=True)
        H = kx*matrices["alpha_s"]+ky*matrices["alpha_t"]+mr*matrices["beta_Re"]+mi*matrices["beta_Im"]
        self.assertEqual(audit.clean(H*H), (kx*kx+ky*ky+mr*mr+mi*mi)*sp.eye(4))
        self.assertEqual(H.conjugate().T, H)
        grading = matrices["chiral_grading_left_positive"]
        self.assertEqual(grading*H+H*grading, sp.zeros(4))
        self.assertTrue(all(row["Clifford_checks"].values()))

    def test_normal_and_six_dimensional_chiralities(self):
        matrices = {k: sp.Matrix(v) for k, v in self.report["conditional_Dirac_operator"]["Clifford_matrices"].items()}
        N = matrices["normal_generator"]
        self.assertEqual(list(N.diagonal()), [-sp.Rational(1, 2), sp.Rational(1, 2), sp.Rational(1, 2), -sp.Rational(1, 2)])
        self.assertEqual(matrices["Gamma6"], -matrices["chiral_grading_left_positive"]*2*N)
        self.assertEqual(list(matrices["Gamma6"].diagonal()), [1, -1, 1, -1])
        expected = sp.diag(1/audit.ZETA, audit.ZETA, audit.ZETA, 1/audit.ZETA)
        self.assertEqual((sp.exp(sp.I*sp.pi*N/2)-expected).applyfunc(lambda v: sp.simplify(sp.expand_complex(v))), sp.zeros(4))

    def test_frozen_spin_times_internal_rotations(self):
        expected = {2: (sp.diag(sp.I, -sp.I), -sp.eye(2)), -2: (-sp.eye(2), sp.diag(-sp.I, sp.I))}
        for q in (2, -2):
            block = audit.charge_block(q)
            self.assertEqual(block["left"], expected[q][0])
            self.assertEqual(block["right"], expected[q][1])
            self.assertEqual(audit.clean(block["left"]**4), sp.eye(2))
            self.assertEqual(audit.clean(block["right"]**4), sp.eye(2))

    def test_kinetic_and_mass_covariance_not_only_intertwiner(self):
        substitutions = {audit.dp: sp.I*audit.dp, audit.dm: -sp.I*audit.dm, audit.m: sp.I*audit.m, audit.mb: -sp.I*audit.mb}
        for q in (2, -2):
            b = audit.charge_block(q)
            rotated = b["D"].subs(substitutions, simultaneous=True)
            self.assertEqual(audit.clean(rotated*b["left"]-b["right"]*b["D"]), sp.zeros(2))
            # Forgetting the derivative's vector rotation is not covariant.
            wrong = b["D"].subs({audit.m: sp.I*audit.m, audit.mb: -sp.I*audit.mb}, simultaneous=True)
            self.assertNotEqual(audit.clean(wrong*b["left"]-b["right"]*b["D"]), sp.zeros(2))

    def test_first_nonzero_Fourier_orbit_is_covariant_and_gapped(self):
        momenta = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        shift = sp.zeros(4)
        for j in range(4):
            shift[(j+1) % 4, j] = 1
        plus = sp.diag(*(sp.I*x-y for x, y in momenta))
        minus = sp.diag(*(sp.I*x+y for x, y in momenta))
        D = sp.diag(plus, minus)
        for q in (2, -2):
            b = audit.charge_block(q)
            L = sp.diag(*(phase*shift for phase in b["left"].diagonal()))
            R = sp.diag(*(phase*shift for phase in b["right"].diagonal()))
            self.assertEqual(D*L, R*D)
            self.assertEqual(D.conjugate().T*D, sp.eye(8))
            self.assertEqual(audit.projector(L, 4).rank(), 2)
            self.assertEqual(audit.projector(R, 4).rank(), 2)

    def test_C4_projectors_are_true_integer_projectors(self):
        for k in range(4):
            P = audit.projector(sp.Matrix([[sp.I**k]]), 4)
            self.assertEqual(P*P, P)
            self.assertEqual(P.conjugate().T, P)
            self.assertEqual(P.rank(), int(k == 0))
        for q in (2, -2):
            b = audit.charge_block(q)
            self.assertEqual(audit.projector(b["left"], 4), sp.zeros(2))
            self.assertEqual(audit.projector(b["right"], 4), sp.zeros(2))

    def test_actual_linear_vortex_Gaussian_equations(self):
        a, x, y = audit.alpha, audit.xx, audit.yy
        g = sp.exp(-a*(x*x+y*y)/2)
        for w in (1, -1):
            mu = a*(x+sp.I*w*y)
            v = g*sp.Matrix([1, w])
            self.assertEqual(audit.apply_D(v, mu, adjoint=w == -1), sp.zeros(2, 1))
            self.assertNotEqual(audit.apply_D(v, mu, adjoint=w == 1), sp.zeros(2, 1))

    def test_oscillator_square_identities_on_nontrivial_polynomials(self):
        a, x, y = audit.alpha, audit.xx, audit.yy
        v = sp.Matrix([x**3+sp.I*x*y+y**2, y**3-x**2+2*sp.I*y])
        osc = sp.Matrix([-sp.diff(z, x, 2)-sp.diff(z, y, 2)+a*a*(x*x+y*y)*z for z in v])
        for w in (1, -1):
            mu = a*(x+sp.I*w*y)
            first = audit.apply_D(audit.apply_D(v, mu), mu, adjoint=True)
            second = audit.apply_D(audit.apply_D(v, mu, adjoint=True), mu)
            expected_first = osc-2*a*audit.S1*v if w == 1 else osc
            expected_second = osc if w == 1 else osc+2*a*audit.S1*v
            self.assertEqual(audit.clean(first-expected_first), sp.zeros(2, 1))
            self.assertEqual(audit.clean(second-expected_second), sp.zeros(2, 1))

    def test_unique_linear_core_ground_state_and_normalization(self):
        a = audit.alpha
        r = sp.Symbol("r", nonnegative=True)
        norm = sp.integrate(2*(a/(2*sp.pi))*sp.exp(-a*r*r)*2*sp.pi*r, (r, 0, sp.oo))
        self.assertEqual(norm, 1)
        for n in range(10):
            energies = [2*a*(n+1)-2*a, 2*a*(n+1)+2*a]
            self.assertEqual(sum(energy == 0 for energy in energies), int(n == 0))
        for row in audit.local_oscillator_math():
            self.assertTrue(all(row["checks"].values()))

    def test_pole_regularization_reverses_winding(self):
        z, zb = sp.symbols("z zb")
        self.assertEqual(sp.cancel((1/z)/(1+1/(z*zb))-zb/(1+z*zb)), 0)
        row = self.report["isolated_core_index_and_projection"]["per_cover_charge_block"]
        self.assertEqual([r["winding_of_this_mu"] for r in row if r["continuous_charge"] == 2], [-1, -1, 1, 1])
        self.assertEqual([r["winding_of_this_mu"] for r in row if r["continuous_charge"] == -2], [1, 1, -1, -1])

    def test_all_core_stabilizer_actions_and_projectors(self):
        for row in self.report["isolated_core_index_and_projection"]["per_cover_charge_block"]:
            b = audit.charge_block(row["continuous_charge"])
            w = row["winding_of_this_mu"]
            R = b["left"] if w == 1 else b["right"]
            core = sp.Matrix([1, w])
            stabilizer = R**(4//row["stabilizer_order"])
            self.assertEqual(stabilizer*core, -core)
            self.assertEqual(sp.Matrix(row["local_projector"]), sp.zeros(1))
            self.assertEqual(row["linear_core_invariant_kernel_dimension"], 0)

    def test_C2_orbit_induction_not_division_by_two(self):
        row = self.report["isolated_core_index_and_projection"]["physical_C2_orbit_representation"]
        A = sp.Matrix(row["generator_A"])
        self.assertEqual(A*A, -sp.eye(2))
        self.assertEqual(A**4, sp.eye(2))
        self.assertEqual([sp.trace(A**j) for j in range(4)], [2, 0, -2, 0])
        self.assertEqual(audit.character_multiplicities([sp.trace(A**j) for j in range(4)]), [0, 1, 0, 1])
        self.assertEqual(audit.projector(A, 4), sp.zeros(2))

    def test_compact_index_characters_from_constant_fibers(self):
        expected = {2: [0, 2, -4, 2], -2: [0, -2, 4, -2]}
        for q in (2, -2):
            b = audit.charge_block(q)
            chars = audit.index_characters(b["left"], b["right"])
            self.assertEqual(chars, expected[q])
            self.assertEqual(sum(chars)/4, 0)
            self.assertEqual(sum(audit.character_multiplicities(chars)), 0)
            self.assertNotEqual(chars, [0, 0, 0, 0])

    def test_local_induced_index_matches_every_group_element(self):
        induced = sp.Matrix([[0, -1], [1, 0]])
        for q in (2, -2):
            b = audit.charge_block(q)
            local = [(1 if q == 2 else -1)*(sp.trace(induced**j)-2*(-1)**j) for j in range(4)]
            self.assertEqual(local, audit.index_characters(b["left"], b["right"]))

    def test_virtual_character_integrality_is_not_positivity(self):
        for row in self.report["compact_equivariant_index"]["charge_block_results"]:
            chars = [sp.sympify(v) for v in row["characters_identity_A_A2_A3"]]
            mult = audit.character_multiplicities(chars)
            self.assertEqual(mult, row["multiplicities_chi0_chi1_chi2_chi3"])
            self.assertTrue(any(v < 0 for v in mult))
            self.assertEqual([sum(max(v, 0) for v in mult), sum(max(-v, 0) for v in mult)], [2, 2])
            self.assertEqual(row["invariant_signed_index"], 0)

    def test_charge_conjugation_maps_opposite_four_dimensional_chirality(self):
        plus, minus = audit.charge_block(2), audit.charge_block(-2)
        x, y = audit.xx, audit.yy
        vec = sp.Matrix([x**2+sp.I*y, x*y-sp.I*y**2])
        mu_plus = x-sp.I*y
        mu_minus = sp.conjugate(mu_plus)
        lhs = audit.apply_D(audit.S3*sp.conjugate(vec), mu_minus, adjoint=True)
        rhs = -audit.S3*sp.conjugate(audit.apply_D(vec, mu_plus))
        self.assertEqual(audit.clean(lhs-rhs), sp.zeros(2, 1))
        self.assertEqual(audit.clean(minus["right"]*audit.S3-audit.S3*sp.conjugate(plus["left"])), sp.zeros(2))
        self.assertTrue(all(self.report["charge_reality_and_counting"]["checks"].values()))

    def test_mass_uniform_bound_is_exact(self):
        s = sp.Symbol("s", nonnegative=True)
        difference = sp.Rational(1, 2)-s/(1+s*s)
        self.assertEqual(sp.cancel(difference-(s-1)**2/(2*(s*s+1))), 0)
        self.assertEqual(difference.subs(s, 1), 0)
        for value in [0, sp.Rational(1, 7), sp.Rational(2, 3), 1, 2, 17]:
            self.assertGreaterEqual(difference.subs(s, value), 0)

    def test_square_torus_first_nonzero_momentum_bound(self):
        momenta = [(a, b) for a in range(-5, 6) for b in range(-5, 6) if (a, b) != (0, 0)]
        squares = [a*a+b*b for a, b in momenta]
        self.assertEqual(min(squares), 1)
        self.assertEqual(squares.count(1), 4)
        L = sp.Symbol("L", positive=True)
        lam = 2*sp.pi/L
        self.assertEqual(2*sp.pi/L-lam/2, sp.pi/L)
        self.assertEqual(lam*L/(4*sp.pi), sp.Rational(1, 2))

    def test_small_mass_bound_does_not_claim_all_mass_gap(self):
        row = self.report["small_mass_compact_gap"]
        self.assertEqual(row["left_and_right_projected_kernel_dimensions_in_that_range"], [0, 0])
        self.assertFalse(row["gap_at_every_mass_or_with_extra_backgrounds_established"])
        self.assertFalse(row["forced_mass_zeros_alone_force_physical_massless_fields"])
        self.assertFalse(row["absence_of_massless_modes_cancels_local_anomalies"])

    def test_common_neutral_twist_does_not_change_mass_ratio(self):
        for s in range(4):
            z = sp.I**s
            H1 = sp.diag(z*audit.ZETA**3, sp.conjugate(z)*audit.ZETA**5)
            H2 = sp.diag(z*audit.ZETA**5, sp.conjugate(z)*audit.ZETA**3)
            self.assertEqual(audit.clean(H1*H2.inv()), sp.diag(-sp.I, sp.I))
            self.assertEqual(audit.clean(H1**4), -sp.eye(2))
        rows = self.report["common_character_counterfactual"]["rows"]
        self.assertEqual([r["plus_charge_invariant_index"] for r in rows], [0, 1, -2, 1])
        self.assertEqual([r["is_the_frozen_absolute_lift"] for r in rows], [True, False, False, False])

    def test_alternative_local_projection_equals_compact_index(self):
        b = audit.charge_block(2)
        for s in range(4):
            z = sp.I**s
            chars = audit.index_characters(z*b["left"], z*b["right"])
            compact = audit.character_multiplicities(chars)[0]
            c4 = audit.projector(sp.Matrix([[-z]]), 4).rank()
            c2 = audit.projector(sp.Matrix([[-z*z]]), 2).rank()
            self.assertEqual(compact, -2*c4+c2)

    def test_counting_and_scope_not_promoted(self):
        local = self.report["isolated_core_index_and_projection"]
        compact = self.report["compact_equivariant_index"]
        reality = self.report["charge_reality_and_counting"]
        self.assertFalse(local["cover_winding_divided_by_stabilizer_or_cover_degree_used_as_multiplicity"])
        self.assertFalse(local["linear_core_models_are_exact_solutions_of_frozen_global_profile"])
        self.assertFalse(compact["zero_index_proves_zero_total_kernel"])
        self.assertFalse(reality["independent_physical_Weyl_multiplicity_is_sum_of_two_complex_charge_tables"])
        self.assertTrue(reality["conjugate_charge_block_must_not_be_counted_twice"])

    def test_no_gate_or_full_action_promotion(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["accepted_extensions"], 0)
        self.assertEqual(row["closed_gates"], [])
        for key in ("all_mass_scales_compact_spectrum_determined", "full_SMW_Gammahat_same_action_sector_constructed", "mixed_gauge_or_finite_relative_anomaly_canceled_by_this_calculation", "all_possible_defect_completions_excluded", "same_action_parent_accepted"):
            self.assertFalse(row[key])

    def test_rehashed_all_mass_gap_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["small_mass_compact_gap"]["gap_at_every_mass_or_with_extra_backgrounds_established"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_spectrum_doubling_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["charge_reality_and_counting"]["independent_physical_Weyl_multiplicity_is_sum_of_two_complex_charge_tables"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_invalid_representations_rejected(self):
        with self.assertRaises(ValueError):
            audit.charge_block(1)
        with self.assertRaises(ValueError):
            audit.projector(sp.Matrix([[2]]), 4)
        with self.assertRaises(ValueError):
            audit.character_multiplicities([0, sp.Rational(1, 3), 0, 0])
        with self.assertRaises(ValueError):
            audit.character_multiplicities([0, 1])


if __name__ == "__main__":
    unittest.main()
