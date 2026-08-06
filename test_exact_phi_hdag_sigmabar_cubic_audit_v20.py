#!/usr/bin/env python3

import exact_phi_hdag_sigmabar_cubic_audit_v20 as gate


def test_charge_contract_and_catalogue_omission():
    audit = gate.charge_audit()
    assert audit["totals"] == {"PQ": 0, "X": 0, "Z17": 0}
    assert audit["declared_contract"]["all"] is True
    assert audit["historical_X_comparison"]["all"] is True
    assert audit["present_in_current_catalogue"] is False


def test_unique_representation_channel():
    audit = gate.representation_audit()
    assert audit["dimensions"] == {
        "10": 10,
        "126bar": 126,
        "210": 210,
        "1050bar": 1050,
    }
    assert audit["dimension_identity"] is True
    assert audit["maximum_character_residual"] < 1.0e-40
    assert audit["210_multiplicity"] == 1


def test_direct_cubic_and_so10_invariance():
    audit = gate.invariance_audit()
    assert audit["generic_cubic_abs"] > 1.0e-6
    assert audit["maximum_infinitesimal_invariance_residual"] < 1.0e-11
    assert audit["phase_structures_distinct"] is True


def test_p_delta_background_impact():
    impact = gate.background_impact()
    assert impact["p_plus_DeltaR_H_tadpole_norm_per_unit_coefficient"] < 1.0e-12
    assert impact["H_Sigmabar_mixed_block_at_p"]["rank"] > 0
    assert impact["H_Phi_mixed_block_at_DeltaR"]["rank"] > 0


def test_report_fail_closed():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["operator_exists_and_is_declared_symmetry_allowed"] is True
    assert report["flag"]["operator_catalogue_currently_incomplete"] is True
    assert report["flag"]["p_DeltaR_tadpole_from_operator"] is False
    assert report["flag"]["p_DeltaR_mixed_Hessian_changed_for_nonzero_coefficient"] is True
    assert report["flag"]["prior_fixed_background_and_coupled_vacua_unconditional"] is False
    assert report["flag"]["complete_mixed_invariant_ring"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False


# The reusable trusted-base G1 workflow is registered on the moving base branch.
