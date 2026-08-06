#!/usr/bin/env python3
import numpy as np
import exact_full_h10_fixed_gut_hessian_v20 as mod


def test_p_background_channel_projector():
    r=mod.p_background_channel_operators()
    assert abs(r['p_norm']-1.0)<1e-12
    assert abs(r['q54_trace'])<1e-12
    assert r['colour_projector_rank']==6
    assert r['colour_projector_idempotence_residual']<1e-12
    assert np.max(np.abs(np.sort(r['colour_projector_eigenvalues'])-np.array([0.]*4+[1.]*6)))<1e-12
    assert r['p_squared_45_dual_norm']<1e-12
    assert r['pati_salam_commutator_residual']<1e-12


def test_electroweak_gauge_certificate():
    r=mod.electroweak_tangent_certificate()
    assert r['H_tangent_rank']==3
    assert r['P_invariance_max']<1e-12
    assert r['DeltaR_invariance_max']<1e-12


def test_full_hessian_and_quotient():
    b=mod.full_hessian_benchmark()
    assert b['gradient_max']<1e-12
    assert b['zero_modes']==4
    assert b['negative_modes']==0
    assert b['symmetry']['gauge_rank']==3
    assert b['symmetry']['gauge_residual']<1e-12
    assert b['symmetry']['PQ_residual']<1e-12
    assert b['symmetry']['null_alignment_residual']<1e-10
    assert b['gauge_quotient']['dimension']==21
    assert b['gauge_quotient']['zero_modes']==1
    assert b['gauge_quotient']['negative_modes']==0
    assert b['gauge_quotient']['remaining_zero']=='PQ'
    assert b['CP_even_odd_cross_residual']<1e-12


def test_spectrum_clusters():
    expected=np.array(
        [0.]*4+[1.3]+[5.]*6+[6.4]*3+[11.4]*6+
        [11.733333333333333,12.635861962038092,24.49747137129524,45.]
    )
    got=np.array(mod.full_hessian_benchmark()['hessian_eigenvalues'])
    assert np.max(np.abs(np.sort(got)-np.sort(expected)))<1e-10


def test_report_and_fail_closed_scope():
    r=mod.build_report()
    assert r['n_failed']==0, r['failures']
    f=r['flag']
    assert f['all_20_real_H10_components_included']
    assert f['three_electroweak_goldstones_identified']
    assert f['PQ_zero_after_gauge_quotient']
    assert f['fixed_GUT_background_H10_hessian_complete']
    assert not f['simultaneous_210_126bar_10_S_Phi17_stationarity']
    assert not f['full_backreacted_multifield_hessian']
    assert not f['global_vacuum_proved']
    assert not f['whole_model_validated']
    assert not f['empirical_discovery']
