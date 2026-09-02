import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v98_transport_physical_realization_audit as audit


class TestV98PhysicalCarrier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_parent_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k:v[1] for k,v in audit.PARENTS.items()})
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        audit.validate_certificate(self.report)

    def test_rehashed_parent_mutation_rejected(self):
        original = Path.read_text
        def changed(path,*args,**kwargs):
            value = original(path,*args,**kwargs)
            if path.name == audit.PARENTS["v97_master"][0]:
                report = json.loads(value)
                report["next_required_action"]["id"] = "ACCEPT_PHYSICAL_CARRIER"
                report["core_sha256"] = audit.canonical_sha(report)
                return json.dumps(report)
            return value
        with patch.object(Path,"read_text",changed):
            with self.assertRaises(RuntimeError): audit.load_parents()

    def test_source_pin_is_fresh_after_pure_cache(self):
        audit._pure_json()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()

    def test_portable_source_hash(self):
        for value in (b"a\nb\n",b"a\r\nb\r\n"):
            with patch.object(Path,"read_bytes",return_value=value):
                self.assertEqual(audit.portable_sha(Path("unused")),audit.hashlib.sha256(b"a\nb\n").hexdigest())

    def test_full_hyper_SMW_half_trace_I8(self):
        z,t = sp.symbols("z t")
        ahat = 1-audit.P1*t*t/24+(7*audit.P1**2-4*audit.P2)*t**4/5760
        pair = sum(((z*t)**k+(-z*t)**k)/(2*sp.factorial(k)) for k in range(5))
        self.assertEqual(sp.expand(ahat*pair).coeff(t,4),audit.I8(z))
        self.assertNotEqual(sp.expand(ahat*pair).coeff(t,4),2*audit.I8(z))

    def test_complete_character_equations_and_regular_kernel(self):
        matrix = sp.Matrix(self.report["positive_hyper_character_realization"]["real_integer_constraint_matrix"])
        self.assertEqual(matrix.rank(),3)
        self.assertEqual(matrix.nullspace(),[sp.ones(4,1)])
        for c in range(-3,4):
            for A in range(abs(c),abs(c)+4):
                counts = audit.phase_counts(c,A)
                self.assertEqual(matrix*sp.Matrix(counts),sp.Matrix([c,c,-2*c]))
                for j in (1,2,3):
                    actual = sum(counts[m]*sp.I**(m*j) for m in range(4))
                    self.assertEqual(sp.simplify(actual-c*(sp.I**j-sp.I**(2*j))),0)

    def test_positive_family_minimum_by_independent_integer_enumeration(self):
        for c in (1,-2):
            solutions = []
            for N0,N1,N2,N3 in product(range(5),repeat=4):
                if N0-N2 == c and N1-N3 == c and N0-N1+N2-N3 == -2*c:
                    solutions.append((N0,N1,N2,N3))
            self.assertTrue(solutions)
            self.assertEqual(min(map(sum,solutions)),4*abs(c))
            self.assertTrue(all(v == tuple(audit.phase_counts(c,v[0])) for v in solutions))
        self.assertEqual(sum(4*abs(c) for c in audit.C.values()),16)

    def test_minimal_phase_allocations_both_orientations(self):
        plus = {n:audit.phase_counts(c) for n,c in audit.C.items()}
        minus = {n:audit.phase_counts(-c) for n,c in audit.C.items()}
        self.assertEqual(plus,{0:[1,2,0,1],1:[2,0,4,2],2:[1,2,0,1]})
        self.assertEqual(minus,{0:[1,0,2,1],1:[2,4,0,2],2:[1,0,2,1]})
        for orientation in (1,-1):
            self.assertEqual(sum(r["multiplicity"] for r in audit.positive_blocks(orientation)),16)

    def test_regular_phase_family_has_zero_nonidentity_full_kernel(self):
        z = sp.Symbol("z")
        for order in (2,4):
            self.assertEqual(sp.expand(sum(audit.local_I6(order,m,z) for m in range(4))),0)
        self.assertNotEqual(4*audit.I8(z),0)

    def test_full_SMW_matrix_trace_matches_local_polynomial(self):
        z = sp.Symbol("z",real=True)
        for phase in range(4):
            h = sp.simplify(audit.ZETA*sp.I**phase)
            H = sp.diag(h,sp.conjugate(h))
            Q = sp.diag(z,-z)
            for order in (2,4):
                matrix = H if order == 4 else audit.clean(H*H)
                traced = audit.kernel.full_SMW_polynomial(matrix,Q,order).subs(audit.kernel.f,1)
                self.assertEqual(sp.expand(traced-audit.local_I6(order,phase,z)),0)

    def test_positive_profile_matches_every_normal_and_gravity_term(self):
        for orientation in (1,-1):
            rows = audit.positive_blocks(orientation)
            c4 = audit.local_sum(rows,4)
            c2 = audit.local_sum(rows,2)
            self.assertEqual(sp.expand(c4-orientation*audit.target_P()/4),0)
            self.assertEqual(sp.expand(2*c2+orientation*audit.target_P()/2),0)
            self.assertFalse(c4.has(audit.x,audit.p))
            self.assertEqual(sp.expand(2*c4+2*c2),0)

    def test_all_explicit_matrix_reality_and_translation_checks(self):
        for row in self.report["explicit_matrices_and_SMW_packaging"]["rows"]:
            H,K,U = [sp.Matrix(row[key]) for key in ("effective_H","external_C8_K","flavor_U_V")]
            self.assertEqual(audit.clean(H.T*audit.J*H),audit.J)
            self.assertEqual(audit.clean(audit.J*sp.conjugate(H)-H*audit.J),sp.zeros(2))
            self.assertEqual(audit.clean(H**4),-sp.eye(2))
            self.assertEqual(U*K*K,sp.eye(2))
            self.assertTrue(all(row["checks"].values()))

    def test_free_N1_projectors_produce_eight_chirals_not_sixteen(self):
        total = 0
        for row in self.report["explicit_matrices_and_SMW_packaging"]["rows"]:
            plus,minus = sp.sympify(row["N1_plus_phase"]),sp.sympify(row["N1_minus_phase"])
            ranks = [int(audit.projector(plus)),int(audit.projector(minus))]
            self.assertEqual(ranks,row["N1_constant_projector_ranks"])
            self.assertEqual(sp.simplify(plus*minus*sp.I),1)
            total += row["multiplicity"]*sum(ranks)
        self.assertEqual(total,8)

    def test_zero_mode_visible_and_common_flavor_charge_table(self):
        rows = self.report["positive_hyper_constant_spectrum"]["charge_and_chirality_rows"]
        self.assertEqual([(r["covering_U1_charge"],r["W_charge"],r["multiplicity"]) for r in rows],[(0,1,1),(0,-1,1),(2,1,2),(-2,-1,2),(4,1,1),(-4,-1,1)])
        self.assertEqual(sum(r["multiplicity"] for r in rows),8)
        for power in (1,3):
            self.assertEqual(sum(r["multiplicity"]*(r["D_power"]*audit.d+r["W_charge"]*audit.w)**power for r in rows).expand(),0)

    def test_bulk_moments_and_exact_polynomial(self):
        counts = {0:4,1:8,2:4}
        self.assertEqual([sum(N*n**k for n,N in counts.items()) for k in range(5)],[16,16,24,40,72])
        exact = sp.expand(sum(N*audit.I8(n*audit.d+audit.w) for n,N in counts.items()))
        saved = sp.sympify(self.report["positive_hyper_bulk_and_flavor_anomalies"]["common_root_bulk_I8"])
        self.assertEqual(sp.expand(exact-saved),0)
        self.assertEqual(saved.coeff(audit.P2),-sp.Rational(1,90))
        self.assertEqual(saved.subs({audit.d:0,audit.w:0}),(7*audit.P1**2-4*audit.P2)/360)

    def test_pure_gravity_cost_and_scope(self):
        row = self.report["positive_hyper_bulk_and_flavor_anomalies"]
        self.assertEqual(row["delta_H_V_T"],[16,0,0])
        self.assertEqual(row["delta_H_minus_V_plus_29T"],16)
        self.assertFalse(row["ordinary_GS_quadratic_four_form_factorization_can_cancel_this_P2_term"])
        self.assertFalse(row["all_extensions_with_new_vector_tensor_or_other_sectors_excluded"])
        self.assertIn("old vector/tensor/gravity spectrum unchanged",row["restricted_no_go"])

    def test_hypothetical_neutral_replacement_cancels_only_rank_gravity(self):
        row = self.report["positive_hyper_bulk_and_flavor_anomalies"]["hypothetical_neutral_replacement"]
        remaining = sp.sympify(row["remaining_common_root_delta_I8"])
        original = sp.sympify(self.report["positive_hyper_bulk_and_flavor_anomalies"]["common_root_bulk_I8"])
        self.assertEqual(sp.expand(remaining-original+16*audit.I8(0)),0)
        self.assertEqual(remaining.coeff(audit.P2),0)
        self.assertEqual(remaining.coeff(audit.P1,2),0)
        self.assertNotEqual(remaining,0)
        for key in ("new_gauge_normal_flavor_and_mixed_anomalies_cancel","old_neutral_states_and_projectors_identified","old_localized_anomaly_or_zero_mode_subtraction_computed","same_action_replacement_adopted"):
            self.assertFalse(row[key])

    def test_full_flavor_roots_are_retained_in_bulk_and_local_polynomials(self):
        rows = self.report["positive_hyper_bulk_and_flavor_anomalies"]["full_multiplicity_flavor_polynomial_rows"]
        names = [name for row in rows for name in row["extra_flavor_Chern_roots"]]
        self.assertEqual(len(names),16)
        self.assertEqual(len(set(names)),16)
        for row in rows:
            roots = [sp.sympify(z) for z in row["full_positive_half_roots"]]
            self.assertEqual(sp.expand(sp.sympify(row["I8"])-sum(audit.I8(z) for z in roots)),0)
            self.assertEqual(sp.expand(sp.sympify(row["C4_I6"])-sum(audit.local_I6(4,row["phase"],z) for z in roots)),0)

    def test_full_flavor_integrated_index_matches_independent_zero_modes(self):
        data = self.report["positive_hyper_bulk_and_flavor_anomalies"]
        rows = data["full_multiplicity_flavor_polynomial_rows"]
        integrated = sp.expand(sum(2*sp.sympify(row["C4_I6"])+2*sp.sympify(row["C2_cover_I6"]) for row in rows).subs(audit.x,0))
        zero = sp.expand(sum((1 if row["phase"]==0 else -1)*sum(audit.I6(sp.sympify(z)) for z in row["full_positive_half_roots"]) for row in rows if row["phase"] in (0,3)))
        self.assertEqual(integrated,zero)
        self.assertNotEqual(zero,0)
        self.assertEqual(sp.expand(integrated-sp.sympify(data["integrated_x_zero_flavor_polynomial"])),0)

    def test_flavor_compensator_changes_target_and_counterprofile(self):
        self.assertEqual(sp.expand(audit.target_P(audit.u+audit.v)-audit.target_P(audit.u)),audit.d**2*audit.v)
        self.assertEqual(audit.target_P(audit.u+audit.v).subs(audit.v,-audit.u),audit.d**3)
        for orientation in (1,-1):
            self.assertEqual(sp.expand(audit.local_sum(audit.positive_blocks(orientation),4).subs(audit.w,audit.u+audit.v)-orientation*audit.target_P(audit.u+audit.v)/4),0)
        row = self.report["positive_hyper_character_realization"]["realizations"][1]
        residual = [sp.expand(sp.sympify(z).subs(audit.w,audit.u+audit.v)) for z in row["remaining_profile_with_original_target"]]
        self.assertEqual(residual,[-audit.d**2*audit.v/4,-audit.d**2*audit.v/4,audit.d**2*audit.v/2])

    def test_opposite_chirality_positive_counts_and_bulk_cancellation(self):
        row = self.report["opposite_chirality_realization"]
        self.assertEqual(sum(r["multiplicity"] for r in row["rows"]),8)
        self.assertEqual([sum(r["multiplicity"] for r in row["rows"] if r["six_dimensional_chirality"]==sign) for sign in (1,-1)],[4,4])
        polynomial = sp.expand(sum(r["multiplicity"]*r["six_dimensional_chirality"]*audit.I8(r["D_power"]*audit.d+audit.w) for r in row["rows"]))
        self.assertEqual(polynomial,0)
        self.assertEqual(audit.local_sum(row["rows"],4),audit.target_P()/4)

    def test_opposite_chirality_fresh_constant_projectors(self):
        for row in self.report["opposite_chirality_realization"]["rows"]:
            phases = [sp.sympify(v) for v in row["positive_half_left_right_rotation"]]
            self.assertEqual([int(audit.projector(z)) for z in phases],[0,0])
            self.assertEqual([int(audit.projector(sp.conjugate(z))) for z in phases],[0,0])
        self.assertFalse(self.report["opposite_chirality_realization"]["spatial_mass_operator_or_nonconstant_mass_spectrum_computed"])
        self.assertFalse(self.report["opposite_chirality_realization"]["V97_charge_two_Dirac_gap_reused"])

    def test_opposite_chirality_new_R_flavor_mismatch_is_not_discarded(self):
        w1,w2 = audit.u+audit.v1+audit.r1*audit.y,audit.u+audit.v2+audit.r2*audit.y
        actual = sp.expand(sum(c*(audit.I8(n*audit.d+w1)-audit.I8(n*audit.d+w2)) for n,c in audit.C.items()))
        expected = audit.d**2*(w1-w2)*(audit.d+(w1+w2)/2)
        self.assertEqual(sp.expand(actual-expected),0)
        self.assertNotEqual(actual,0)
        row = self.report["opposite_chirality_realization"]
        self.assertEqual(sp.expand(actual-sp.sympify(row["general_R_flavor_mismatch_I8"])),0)
        self.assertTrue(row["R_charges_r1_r2_in_diagnostic_are_not_assigned_to_standard_hyperinos"])

    def test_actual_geometric_kernel_failure_is_independent_of_chirality(self):
        row = self.report["geometric_and_flavor_scope"]
        for chirality in (-1,1):
            for normal_spin in (-1,1):
                self.assertEqual((-1)**(1+normal_spin),1)
                self.assertEqual((-1)**(1+normal_spin+1),-1)
        self.assertEqual(row["D_on_each_M_twisted_field"],-1)
        self.assertFalse(row["opposite_6D_chirality_repairs_D"])
        self.assertFalse(row["independent_internal_F_or_R_character_repairs_D"])

    def test_nonabelian_compensator_not_claimed_in_commuting_flavor(self):
        q = sp.diag(1,-1)
        off = sp.Matrix([[0,1],[1,0]])
        self.assertNotEqual(q*off-off*q,sp.zeros(2))
        row = self.report["explicit_matrices_and_SMW_packaging"]
        self.assertFalse(row["full_independent_SU2_F_representation_asserted"])
        self.assertFalse(row["independent_discrete_R4_assignment_for_new_fields_frozen"])
        self.assertFalse(self.report["geometric_and_flavor_scope"]["full_frozen_Sp267_flavor_embedding_constructed"])
        self.assertFalse(self.report["positive_hyper_character_realization"]["full_frozen_nonabelian_flavor_representation_constructed"])
        self.assertIn("tensor-product", self.report["positive_hyper_character_realization"]["multiplicity_domain"])

    def test_hyper_R_singlet_is_not_a_new_R_assignment(self):
        row = self.report["positive_hyper_bulk_and_flavor_anomalies"]
        self.assertEqual(row["new_SU2_R_Witten_doublets_from_hyperinos"],0)
        self.assertFalse(sp.sympify(row["common_root_bulk_I8"]).has(audit.y))
        self.assertFalse(row["independent_discrete_R_flavor_and_global_anomalies_completed"])

    def test_cached_math_returns_copies_and_not_hidden_parent_checks(self):
        original = json.loads(audit._pure_json())
        original["positive_hyper_constant_spectrum"]["N1_chiral_multiplet_count"] = 0
        self.assertEqual(json.loads(audit._pure_json())["positive_hyper_constant_spectrum"]["N1_chiral_multiplet_count"],8)

    def test_rehashed_bulk_anomaly_erasure_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["positive_hyper_bulk_and_flavor_anomalies"]["irreducible_P2_coefficient"] = "0"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_rehashed_gate_and_gap_promotion_rejected(self):
        for section,key in (("terminal_decision","same_action_parent_accepted"),("positive_hyper_constant_spectrum","V97_Dirac_gap_applied_to_this_carrier")):
            changed = copy.deepcopy(self.report)
            changed[section][key] = True
            changed["core_sha256"] = audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_no_quantum_action_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["accepted_extensions"],0)
        self.assertEqual(row["closed_gates"],[])
        for key in ("unchanged_bulk_spectrum_plus_hyper_only_repair_viable","opposite_chirality_hyper_only_6D_N1_completion_constructed","original_normal_M_Gammahat_kernel_repaired_by_independent_flavor","full_relative_quantized_transport_or_global_anomaly_cancellation_constructed","same_action_parent_accepted"):
            self.assertFalse(row[key])

    def test_invalid_multiplicities_and_orientations_rejected(self):
        for args in ((2,1),(-2,1),(1,-1),(sp.Rational(1,2),None)):
            with self.assertRaises(ValueError): audit.phase_counts(*args)
        with self.assertRaises(ValueError): audit.positive_blocks(0)


if __name__ == "__main__":
    unittest.main()
