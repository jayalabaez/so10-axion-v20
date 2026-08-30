from __future__ import annotations

import susy_v45_discrete_r_audit as audit


def test_required_terms_and_mu_for_benchmarks() -> None:
    for order, q, qc in ((5, 2, 2), (6, 1, 1)):
        charges = audit.charges_for(order, q, qc)
        terms = audit.required_term_audit(order, charges)
        assert terms["all_allowed"]
        assert terms["mu_HH_forbidden"]


def test_inherited_z4_is_mixed_nonuniversal() -> None:
    row = audit.anomaly_rows(4, audit.charges_for(4, 1, 1))
    assert row["standard_residues_mod_eta"] == {"SU4": 0, "SU2L": 1, "SU2R": 1}
    assert not row["mixed_equal_level_universal"]


def test_z5_and_z6_pass_only_the_integrated_exact_screen() -> None:
    for order, q, qc in ((5, 2, 2), (6, 1, 1)):
        row = audit.anomaly_rows(order, audit.charges_for(order, q, qc))
        assert row["mixed_exact_no_GS"]
        assert row["gravity_exact_screen"]


def test_scan_orders_are_stable() -> None:
    result = audit.scan_integrated_candidates(96)
    assert result["orders_passing_the_conventional_exact_integrated_screen"] == [3, 5, 6, 10, 15, 30]


def test_quartic_epsilon_polynomial_is_nonzero() -> None:
    assert audit.explicit_quartic_value() == 4


def test_forced_degree20_witnesses_are_u1f_neutral() -> None:
    theorem = audit.forcing_theorem()
    assert theorem["plus_witness"]["degree"] == 20
    assert theorem["plus_witness"]["orientation"] == 12
    assert theorem["plus_witness"]["U1F"] == 0
    assert theorem["minus_witness"]["orientation"] == -12
    assert theorem["minus_witness"]["U1F"] == 0


def test_forcing_congruence_computationally_through_order_96() -> None:
    """Every required-term/equal-level assignment obeys both witness charges."""

    for order in range(3, 97):
        modulus = 2 * audit.eta(order)
        for q in range(order):
            for qc in range(order):
                h = (2 - q - qc) % order
                for t in range(order):
                    # The common shift cancels, so use the reduced rows.
                    a4 = 8 - 6 * h
                    al = 12 * q + 2 * h - 10 - 4 * t
                    ar = 12 * qc + 2 * h - 10 + 4 * t
                    if (a4 - al) % modulus or (a4 - ar) % modulus:
                        continue
                    a = q
                    b = (2 - t - a) % order
                    c = qc
                    d = (2 + t - c) % order
                    assert (12 * q + 4 * (a + b)) % order == 2 % order
                    assert (12 * qc + 4 * (c + d)) % order == 2 % order


def test_massive_pair_anomaly_matching_identity() -> None:
    for order in range(3, 97):
        modulus = audit.eta(order)
        for r in range(order):
            rbar = (2 - r) % order
            # Any integer Dynkin index gives a trivial standard anomaly shift.
            for index in (1, 2, 4, 35):
                assert (index * ((r - 1) + (rbar - 1))) % modulus == 0


def test_report_is_fail_closed_and_self_consistent() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert not report["decision"]["inherited_Z4R_retained_as_exact"]
    assert not report["decision"]["any_candidate_forbids_first_oriented_local_W_invariant"]
    assert not report["decision"]["ordinary_exact_R_massive_packet_repair_exists"]
    assert not report["decision"]["discrete_R_sector_complete"]
