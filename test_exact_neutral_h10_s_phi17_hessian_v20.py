#!/usr/bin/env python3
import numpy as np
import exact_neutral_h10_s_phi17_hessian_v20 as mod

def test_invariant_census():
    r=mod.build_report()
    assert r['n_failed']==0, r['failures']
    assert r['counts']=={
        'complex_monomials':36,
        'hermitian_orbits':23,
        'real_coefficient_directions':36,
        'H10_monomials':15,
        'H10_orbits':10,
    }

def test_exact_neutral_representation_contract():
    r=mod.representation()
    assert r['available'], r
    assert abs(r['Hu']['Q'])<1e-12
    assert abs(r['Hd']['Q'])<1e-12
    assert abs(r['Hu_dot_Hd']-1.0)<1e-12
    assert abs(r['weak_pair_factor_two']-2.0)<1e-12

def test_hessian_and_gauge_quotient():
    b=mod.benchmark()
    assert b['gradient_max']<1e-12
    assert b['zero_modes']==2
    assert b['negative_modes']==0
    assert b['symmetry']['Hg']<1e-12
    assert b['symmetry']['HPQ']<1e-12
    assert b['symmetry']['alignment']<1e-10
    assert b['quotient']['zero_modes']==1
    assert b['quotient']['negative_modes']==0
    assert b['quotient']['remaining_zero']=='PQ'
    assert b['cross_max']<1e-12

def test_spectrum_regression():
    expected=np.array([0.,0.,1.3,6.4,11.733333333333333,12.635861962038092,24.49747137129524,45.])
    got=np.array(mod.benchmark()['eigenvalues'])
    assert np.max(np.abs(got-expected))<1e-10

def test_fail_closed_scope():
    f=mod.build_report()['flag']
    assert f['neutral_invariant_census_complete']
    assert f['neutral_hessian_complete']
    assert f['PQ_zero_after_gauge_quotient']
    assert not f['charged_color_H10_complete']
    assert not f['full_210_126_10_S_Phi17_hessian']
    assert not f['whole_model_validated']
    assert not f['discovery']
