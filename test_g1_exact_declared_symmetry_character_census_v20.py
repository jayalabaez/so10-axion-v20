#!/usr/bin/env python3
import g1_exact_declared_symmetry_character_census_v20 as census

# Trusted-base PR synchronization marker; assertions are unchanged.


def test_fundamental_character_dimensions():
    assert census.character_dimension(census.vector_character()) == 10
    assert census.character_dimension(census.chiral_spinor_character()) == 16
    assert census.character_dimension(census.rep126_character()) == 126
    assert census.character_dimension(census.rep126bar_character()) == 126
    assert census.character_dimension(census.rep210_character()) == 210


def test_known_representation_multiplicities():
    rows = census.census(False)
    assert census.singlet_multiplicity(census.symmetric_rep_character('H', 2)) == 1
    assert census.singlet_multiplicity(census.symmetric_rep_character('P', 3)) == 1
    assert census.singlet_multiplicity(census.symmetric_rep_character('P', 4)) == 4
    assert census.find_multiplicity(rows, D=2, Db=2) == 4
    assert census.find_multiplicity(rows, P=2, D=1, Db=1) == 6
    assert census.find_multiplicity(rows, P=2, H=1, Hb=1) == 3
    assert census.find_multiplicity(rows, P=2, H=1, Db=1) == 2
    assert census.find_multiplicity(rows, H=1, Hb=1, D=1, Db=1) == 2
    assert census.find_multiplicity(rows, H=2, Hb=2) == 2


def test_live_declared_symmetry_counts():
    report = census.build_report()
    assert report['n_failed'] == 0, report['failures']
    counts = report['counts']
    assert counts['charge_and_so10_allowed_multidegrees'] == 74
    assert counts['hermitian_conjugacy_orbits'] == 48
    assert counts['total_complex_invariant_multiplicity'] == 91
    assert counts['total_potential_orbit_multiplicity'] == 64
    assert counts['total_real_potential_parameters'] == 91


def test_historical_X_subcensus_reproduced_exactly():
    report = census.build_report()
    old = report['historical_continuous_X_comparison']['counts']
    assert old['charge_and_so10_allowed_multidegrees'] == 34
    assert old['hermitian_conjugacy_orbits'] == 28
    assert old['total_complex_invariant_multiplicity'] == 51
    assert old['total_potential_orbit_multiplicity'] == 44
    assert old['total_real_potential_parameters'] == 51
    live = {
        tuple(row['count_tuple']): row['so10_singlet_multiplicity']
        for row in census.census(False)
    }
    for row in census.census(True):
        assert live[tuple(row['count_tuple'])] == row['so10_singlet_multiplicity']


def test_merged_subsector_cross_checks():
    report = census.build_report()
    assert report['cross_checks']['singlet_only'] == {
        'multidegrees': 21,
        'conjugacy_orbits': 13,
        'complex_invariant_multiplicity': 21,
        'potential_orbit_multiplicity': 13,
        'real_parameters': 21,
    }
    assert report['cross_checks']['H10_S_Phi17'] == {
        'multidegrees': 35,
        'conjugacy_orbits': 22,
        'complex_invariant_multiplicity': 36,
        'potential_orbit_multiplicity': 23,
        'real_parameters': 36,
    }


def test_live_charge_contract_and_conjugacy():
    rows = census.census(False)
    assert any(row['charge']['X'] != 0 for row in rows)
    for row in rows:
        assert row['charge']['PQ'] == 0
        assert row['charge']['Z17'] == 0
        conjugate = tuple(row['conjugate_count_tuple'])
        assert census.charge_neutral(conjugate, require_x=False)
        assert row['so10_singlet_multiplicity'] == census.find_multiplicity(
            rows,
            **{
                field: count
                for field, count in zip(census.FIELD_ORDER, conjugate)
            },
        )


def test_fail_closed_scope():
    report = census.build_report()
    assert report['overall_state'] == 'BLOCKED'
    assert report['closure']['declared_symmetry_charge_multidegrees_degree_le_4_closed']
    assert report['closure']['so10_singlet_multiplicities_degree_le_4_closed']
    assert report['closure']['historical_X_filtered_44_superseded']
    assert not report['closure']['explicit_component_tensor_basis_closed']
    assert not report['closure']['full_component_potential_G2_closed']
    assert not report['flags']['g1_closed']
    assert not report['flags']['whole_model_validated']
