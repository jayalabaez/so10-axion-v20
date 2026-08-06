#!/usr/bin/env python3
import g1_exact_declared_symmetry_character_census_v20 as census
import live_g1_tensor_closure_ledger_v20 as ledger


def test_all_eighteen_base_families_are_present():
    assert len(ledger.BASE_FAMILIES) == 18
    # Base families are reused by singlet dressings; their undressed
    # multiplicities sum to 34, while the 48 dressed orbits sum to 64.
    assert sum(base['multiplicity'] for base in ledger.BASE_FAMILIES.values()) == 34
    assert all(base['basis'] for base in ledger.BASE_FAMILIES.values())
    assert all(base['normalization'] for base in ledger.BASE_FAMILIES.values())


def test_live_census_is_fully_covered():
    report = ledger.build_report()
    assert report['n_failed'] == 0, report
    assert report['counts']['charge_and_so10_allowed_multidegrees'] == 74
    assert report['counts']['hermitian_conjugacy_orbits'] == 48
    assert report['counts']['independent_invariant_coefficients'] == 64
    assert report['counts']['real_potential_parameters'] == 91
    assert len(report['operator_orbits']) == 48
    assert sum(row['multiplicity'] for row in report['operator_orbits']) == 64
    assert sum(len(row['basis']) for row in report['operator_orbits']) == 64


def test_every_canonical_conjugacy_orbit_maps_after_singlet_stripping():
    """Guard the H/Hdag and 126bar/126bar-dag orientation boundary."""
    orbits = census.orbits(census.census(False))
    assert len(orbits) == 48
    for orbit in orbits:
        stripped_key = tuple(int(value) for value in orbit['orbit_key'][:5])
        assert stripped_key in ledger.BASE_FAMILIES, {
            'representative': orbit['representative'],
            'members': orbit['members'],
            'stripped_key': stripped_key,
        }
        assert (
            ledger.BASE_FAMILIES[stripped_key]['multiplicity']
            == orbit['so10_singlet_multiplicity']
        )

    # Explicitly lock the chiral orientations most vulnerable to accidental
    # conjugation swaps when the full nine-field orbit key is canonicalized.
    expected = {
        (0, 0, 1, 2, 1): 'Hdag_Sigma2_Sigmadag',
        (0, 0, 2, 2, 0): 'Hdag2_Sigma2',
        (2, 0, 1, 1, 0): 'Phi2_Hdag_Sigma',
        (1, 0, 1, 1, 0): 'Phi_Hdag_Sigma',
        (1, 0, 1, 0, 1): 'Phi_Hdag_Sigmadag',
    }
    for key, family_id in expected.items():
        assert ledger.BASE_FAMILIES[key]['id'] == family_id


def test_sources_and_normalizations_are_complete():
    report = ledger.build_report()
    assert not report['missing_source_modules']
    assert not report['missing_base_keys']
    assert not report['multiplicity_mismatches']
    assert not report['normalization_missing']
    for row in report['operator_orbits']:
        assert row['sources']
        assert row['normalization']
        assert len(row['basis']) == row['multiplicity']


def test_g1_closes_without_overclaiming_downstream_gates():
    report = ledger.build_report()
    assert report['status'] == 'LIVE_G1_RENORMALIZABLE_TENSOR_RING_CLOSED'
    assert report['closure']['G1_invariant_ring_and_component_tensors_closed']
    assert report['closure']['explicit_tensor_basis_all_64_directions_closed']
    assert report['closure']['normalization_all_64_directions_specified']
    assert not report['closure']['G2_complete_projected_component_potential_closed']
    assert not report['closure']['G3_global_vacuum_closed']
    assert not report['closure']['G8_unique_proton_decay_closed']
    assert not report['flags']['all_g1_g8_closed']
    assert not report['flags']['whole_model_validated']
