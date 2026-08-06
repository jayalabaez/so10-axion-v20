#!/usr/bin/env python3
from __future__ import annotations

import next_gen_triplet_portal_norm_square_gate_v20 as portal
import nonsusy_charge_allowed_mt_v20 as signed_mt2
import nonsusy_z17_pq_potential_filter_v20 as signed_filter
import so10_kronecker_existence_mt_lock_v20 as signed_kron
import triplet_proxy_contamination_audit_v20 as contamination


def test_signed_chain_executes_from_clean_source_checkout() -> None:
    reports = {
        "signed_filter": signed_filter.build_report(),
        "signed_mt2": signed_mt2.build_report(),
        "signed_kron": signed_kron.build_report(),
        "contamination": contamination.build_report(),
        "portal": portal.build_report(),
    }
    failures = {
        name: report.get("failures")
        for name, report in reports.items()
        if report.get("n_failed", 1) != 0
    }
    assert not failures, failures


def test_signed_chain_remains_fail_closed() -> None:
    mt2 = signed_mt2.build_report()
    kron = signed_kron.build_report()
    audit = contamination.build_report()
    top = portal.build_report()

    assert mt2["flag"]["mass_squared_matrix_used"] is True
    assert mt2["flag"]["forbidden_210_10dag10_absent"] is True
    assert mt2["flag"]["forbidden_10_126_S_absent"] is True
    assert mt2["flag"]["physical_component_CG_complete"] is False
    assert mt2["flag"]["physical_triplet_spectrum_complete"] is False
    assert mt2["flag"]["exact_unique_proton_lifetime"] is False
    assert mt2["flag"]["whole_model_excluded"] is False

    assert kron["flag"]["lambda4_offdiag_allowed_but_CG_open"] is True
    assert kron["flag"]["physical_component_CG_complete"] is False
    assert audit["flag"]["legacy_physical_triplet_chain_invalidated"] is True
    assert audit["flag"]["physical_triplet_spectrum_complete"] is False

    assert top["flag"]["exact_quartic_t2bar_t4bar_mixing_inserted"] is True
    assert top["flag"]["complete_component_potential"] is False
    assert top["flag"]["physical_triplet_spectrum_complete"] is False
    assert top["flag"]["exact_unique_proton_lifetime"] is False
    assert top["flag"]["whole_model_validated"] is False
    assert top["flag"]["empirical_discovery"] is False
