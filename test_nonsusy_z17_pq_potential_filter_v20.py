#!/usr/bin/env python3
import nonsusy_z17_pq_potential_filter_v20 as mod


class TestDeclaredFilter:
    def setup_method(self):
        self.report = mod.build_report()
        self.ops = {row["name"]: row for row in self.report["operators"]}

    def test_status_and_flags(self):
        assert self.report["status"] == (
            "NONSUSY_SO10_U1X_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN"
        )
        assert self.report["n_failed"] == 0, self.report["failures"]
        flags = self.report["flag"]
        assert flags["z17_pq_filter_applied"]
        assert flags["z17_pq_x_filter_applied"]
        assert flags["continuous_x_filter_applied"]
        assert not flags["phi17_phase_sensitive_low_dimension_terms_retained"]
        assert flags["bare_10_squared_forbidden"]
        assert flags["ten2_S_allowed"]
        assert flags["mixed_dagger_cubic_retained"]
        assert flags["mixed_dagger_cubic_requires_complete_hessian_reaudit"]
        assert not flags["complete_so10_scalar_potential"]

    def test_declared_gauged_x_behavior(self):
        assert self.ops["Phi17^3"]["status"] == "CHARGE_FORBIDDEN"
        assert self.ops["10_H^2 S Phi17"]["status"] == "CHARGE_FORBIDDEN"
        assert self.report["counterfactual_no_X_comparison"][
            "Phi17^3_status"
        ] == "ALLOWED"
        assert self.report["counterfactual_no_X_comparison"][
            "mixed_dagger_cubic_status"
        ] == "ALLOWED"
        assert self.report["counterfactual_no_X_comparison"][
            "not_the_declared_model"
        ]

    def test_core_so10_and_pq_results(self):
        assert self.ops["bare_10_H^2"]["status"] == "CHARGE_FORBIDDEN"
        assert self.ops["10_H^2 S"]["status"] == "ALLOWED"
        assert self.ops["210_H 10_H^dag 10_H"]["status"] == "SO10_FORBIDDEN"
        mixed = self.ops["210_H 10_H_dag 126bar_H"]
        assert mixed["status"] == "ALLOWED"
        assert mixed["charge_totals"] == {"PQ": 0, "X": 0, "Z17": 0}
        assert mixed["feeds_triplet_mass"] is True
        assert "210_H 10_H_dag 126bar_H" in self.report[
            "allowed_feeding_M_T"
        ]
        assert self.ops["210_H^dag 210_H 10_H^dag 10_H"]["status"] == "ALLOWED"
        assert self.ops["126bar_H^2 10_H^2 S^2"]["charge_allowed"]["all"]

    def test_charge_helper_and_modes(self):
        total = mod._total_charge({"10_H": 2, "S": 1})
        assert total == {"PQ": 0, "X": 0, "Z17": 0}
        cubic = mod._total_charge(
            {"210_H": 1, "10_H_dag": 1, "126bar_H": 1}
        )
        assert cubic == {"PQ": 0, "X": 0, "Z17": 0}
        assert mod._allowed(cubic, require_x=True)["all"]
        assert mod._allowed(cubic, require_x=True)["all"]
        phi3 = mod._total_charge({"Phi17": 3})
        assert not mod._allowed(phi3, require_x=True)["all"]
        assert not mod._allowed(phi3, require_x=True)["all"]
        assert mod._allowed(phi3, require_x=False)["all"]
