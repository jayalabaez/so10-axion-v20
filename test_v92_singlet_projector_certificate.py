import copy
import itertools
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import sympy as sp

import v92_singlet_projector_certificate as audit


def matrix(rows):
    return sp.Matrix([[sp.sympify(x) for x in row] for row in rows])


class TestV92SingletProjectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents=audit.load_parents()
        cls.contract=audit.source_contract(cls.parents)
        cls.report=audit.build_certificate()

    def test_canonical_pinned_parents(self):
        self.assertEqual(self.report["input_core_hashes"],
                         {key:core for key,(_,core) in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))

    def test_changed_parent_is_rejected(self):
        read=Path.read_text
        def corrupted(path,*args,**kwargs):
            text=read(path,*args,**kwargs)
            if path.name==audit.PARENTS["v91"][0]:
                value=json.loads(text)
                value["quantized_scout"]["singlet_counts_by_q0_q2_q4_q6_q8"][0]+=1
                return json.dumps(value)
            return text
        with patch.object(Path,"read_text",corrupted):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_four_orbit_matrices_come_from_pinned_source(self):
        a,u,v=(self.contract[k] for k in ("A4","U4","V4"))
        self.assertEqual(u,sp.diag(sp.I,-1,-sp.I,-1))
        self.assertEqual(v,sp.diag(-1,sp.I,-1,-sp.I))
        self.assertEqual(a*u*a.inv(),v)
        self.assertEqual(a*v*a.inv(),u.inv())
        self.assertEqual(a**4,sp.eye(4))
        self.assertEqual(audit.constant_projector(a,u,v),sp.zeros(4))

    def test_complete_267_allocations(self):
        for key in ("two_mode_unaligned_witness","eleven_mode_normal_aligned_witness"):
            row=self.report[key]
            self.assertEqual(row["total_6D_hypers"],267)
            self.assertEqual(row["complex_symplectic_dimension"],534)
            self.assertEqual(row["hyper_counts_by_q"],[[0,144],[2,3],[4,19],[6,11],[8,90]])
            self.assertEqual(sum(b["copies"]*b["certificate"]["hyper_count"]
                                 for b in row["direct_sum_blocks"]),267)

    def test_all_block_square_relations_and_hyper_pairing(self):
        for name in ("two_mode_unaligned_witness","eleven_mode_normal_aligned_witness"):
            for block in self.report[name]["direct_sum_blocks"]:
                row=block["certificate"]
                a=matrix(row["effective_plus"]["A"])
                am=matrix(row["effective_minus_column"]["A"])
                self.assertEqual(audit.clean(am.T*a),-sp.I*sp.eye(a.rows))
                self.assertTrue(all(row["square_relations"]["plus"].values()))
                self.assertTrue(all(row["square_relations"]["minus"].values()))

    def test_charge_pairing_distinguishes_continuous_and_finite(self):
        row4=audit.block_certificate(4,"line",0,1,self.contract)
        row8=audit.block_certificate(8,"line",0,1,self.contract)
        self.assertEqual(row4["continuous_symplectic_charge_diagonal"],[4,-4])
        self.assertEqual(row4["finite_q8_symplectic_pair"],[4,4])
        self.assertEqual(row8["continuous_symplectic_charge_diagonal"],[8,-8])
        self.assertEqual(row8["finite_q8_symplectic_pair"],[0,0])
        self.assertTrue(all(row4["SMW_flavor_checks"].values()))
        self.assertTrue(all(row8["SMW_flavor_checks"].values()))

    def test_translation_compensation_at_q2_and_q6(self):
        for q in (2,6):
            row=audit.block_certificate(q,"line",0,1,self.contract)
            self.assertEqual(row["C8_translation_phase"],-1)
            self.assertEqual(row["compensating_flavor_translation_factor"],-1)
            f=row["underlying_flavor"]
            self.assertEqual(audit.clean(matrix(f["U"])*matrix(f["external_k"])**2),sp.eye(2))

    def test_gammahat_kernel_annihilated(self):
        for block in self.report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
            row=block["certificate"]
            for parity in row["Gammahat_kernel_parities"].values():
                for k in self.contract["kernel"].values():
                    self.assertEqual(sum(a*b for a,b in zip(parity,k))%2,0)
            for field in row["Gammahat_kernel_action_exponents_mod2"].values():
                self.assertEqual(set(field.values()),{0})

    def test_flavor_quaternionic_reality_by_actual_matrices(self):
        for block in self.report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
            row=block["certificate"]["underlying_flavor"]
            j=matrix(row["symplectic_J"])
            self.assertEqual(j*sp.conjugate(j),-sp.eye(j.rows))
            for name in ("A","U","V","external_k"):
                a=matrix(row[name])
                self.assertTrue(audit.zero(a.T*j*a-j))
                self.assertTrue(audit.zero(j*sp.conjugate(a)-a*j))

    def test_all_four_strata_projectors_are_orthogonal(self):
        for block in self.report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
            for point,row in block["certificate"]["strata"].items():
                self.assertEqual(row["order"],4 if point in ("z00","z11") else 2)
                self.assertEqual(row["normal_weight"],1)
                for prefix in ("plus","minus","hyperino"):
                    p=matrix(row[prefix+"_projector"])
                    a=matrix(row[prefix+"_matrix"])
                    self.assertTrue(audit.zero(p*p-p))
                    self.assertTrue(audit.zero(p.conjugate().T-p))
                    self.assertTrue(audit.zero(a*p-p))

    def test_SMW_half_count_not_doubled_hypers(self):
        for block in self.report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
            row=block["certificate"]
            modes=row["constant_modes"]
            self.assertEqual(modes["complex_hyperino"],2*(modes["plus"]+modes["minus"]))
            self.assertEqual(modes["SMW_independent_Weyl"],modes["plus"]+modes["minus"])
            self.assertTrue(all(row["hyperino_checks"].values()))

    def test_local_projector_count_is_not_global_count(self):
        row=audit.block_certificate(0,"four_orbit",0,1,self.contract)
        self.assertEqual(row["constant_modes"]["SMW_independent_Weyl"],0)
        self.assertEqual(row["strata"]["z00"]["ranks_plus_minus_complex_hyperino"],[1,1,4])
        self.assertEqual(row["strata"]["z11"]["ranks_plus_minus_complex_hyperino"],[1,1,4])

    def test_line_family_constant_kernel_formula_all_m_eta(self):
        for m,eta in itertools.product(range(4),(-1,1)):
            a,u,v=audit.effective_matrices("line",m,eta,self.contract)
            self.assertEqual(audit.constant_projector(a,u,v).rank(),int(m==0 and eta==1))
            am=-sp.I*a.inv().T
            self.assertEqual(audit.constant_projector(am,u.inv().T,v.inv().T).rank(),int(m==3 and eta==1))

    def test_two_mode_and_eleven_mode_witnesses_differ(self):
        two=self.report["two_mode_unaligned_witness"]
        eleven=self.report["eleven_mode_normal_aligned_witness"]
        self.assertEqual(two["constant_N1_signed_continuous_charges"],[-8,8])
        self.assertEqual(two["constant_N1_chiral_count"],2)
        self.assertEqual(eleven["constant_N1_chiral_count"],11)
        self.assertEqual(eleven["constant_N1_signed_continuous_charges"],[-8,2,2,2,4,4,4,6,6,6,8])
        self.assertEqual(eleven["constant_uncharged_N1_chiral_count"],0)
        self.assertEqual(two["normal_Delta_by_corner"],{"z00":263,"z11":263})
        self.assertEqual(eleven["normal_Delta_by_corner"],{"z00":-11,"z11":-11})

    def test_new_gaugino_choice_is_not_imported_as_frozen(self):
        row=self.report["conditional_normal_channel"]
        self.assertFalse(row["this_U1_lift_was_previously_frozen"])
        self.assertEqual(row["new_U1_gaugino_addition_over192"],[11,1])
        self.assertEqual(row["new_base_over192"],[97,-13])
        self.assertEqual(row["target_for_alignment_with_x_p1_T6"],-11)

    def test_normal_channel_alignment_not_total_anomaly_cancellation(self):
        row=self.report["conditional_normal_channel"]
        for point in ("z00","z11"):
            aligned=row["witness_coefficients"]["eleven_mode_normal_aligned"][point]
            unaligned=row["witness_coefficients"]["two_mode_unaligned"][point]
            self.assertEqual(aligned["coefficients_x3_xp_over192"],[-24,-24])
            self.assertTrue(aligned["aligned_with_x_p1_T6"])
            self.assertEqual(unaligned["coefficients_x3_xp_over192"],[2990,250])
            self.assertFalse(unaligned["aligned_with_x_p1_T6"])
        self.assertFalse(row["normal_alignment_is_full_fixed_wall_anomaly_cancellation"])

    def test_extra_mode_and_charge_moment_scope(self):
        row=self.report["conditional_normal_channel"]
        self.assertEqual(row["minimum_constant_chiral_modes_under_two_equal_corner_target"],11)
        self.assertEqual(row["nine_additional_modes_beyond_two_Phi_under_this_target"],9)
        self.assertEqual(row["sign_choices_for_nine_selected_extra_modes"],512)
        self.assertEqual(row["sign_choices_cancel_both_4D_U1_linear_and_cubic_moments_without_other_sectors"],0)
        self.assertFalse(row["extra_modes_must_be_charged_in_every_possible_assignment"])
        self.assertFalse(row["nonzero_4D_singlet_cubic_moment_is_a_full_anomaly_no_go"])
        self.assertEqual(self.report["eleven_mode_normal_aligned_witness"]["constant_chiral_charge_moments"],{"TrQ":36,"TrQ3":864})
        self.assertFalse(self.report["new_flavor_sector"]["independent_4D_Z4R_charges_of_new_singlets_frozen"])
        self.assertFalse(self.report["new_flavor_sector"]["orbifold_rotation_m_is_the_independent_4D_Z4R_charge"])

    def test_no_gate_or_action_promotion(self):
        row=self.report["terminal_decision"]
        self.assertTrue(row["smooth_singlet_matrix_projector_witnesses_constructed"])
        self.assertTrue(row["constant_mode_counts_derived_from_joint_kernels"])
        self.assertFalse(row["unique_projector_assignment_selected"])
        self.assertFalse(row["full_orbibundle_or_quantum_action_accepted"])
        self.assertFalse(row["full_fixed_wall_anomaly_cancelled"])
        self.assertEqual(row["closed_gates"],[])

    def test_rehashed_scope_and_numeric_mutations_rejected(self):
        for section,key,value in (
            ("terminal_decision","full_fixed_wall_anomaly_cancelled",True),
            ("two_mode_unaligned_witness","constant_N1_chiral_count",267),
        ):
            candidate=copy.deepcopy(self.report)
            candidate[section][key]=value
            candidate["core_sha256"]=audit.canonical_sha(candidate)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(candidate)

    def test_output_is_JSON_serializable(self):
        self.assertEqual(json.loads(json.dumps(self.report)),self.report)


if __name__=="__main__":
    unittest.main()
