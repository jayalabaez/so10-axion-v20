#!/usr/bin/env python3
import nonsusy_z17_pq_potential_filter_v20 as mod

class TestDeclaredFilter:
    def setup_method(self):
        self.report=mod.build_report(); self.ops={r['name']:r for r in self.report['operators']}
    def test_status_and_flags(self):
        assert self.report['status']=='NONSUSY_Z17_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN'
        assert self.report['n_failed']==0, self.report['failures']
        f=self.report['flag']
        assert f['z17_pq_filter_applied']
        assert not f['z17_pq_x_filter_applied']
        assert not f['continuous_x_filter_applied']
        assert f['phi17_low_dimension_terms_retained']
        assert f['bare_10_squared_forbidden'] and f['ten2_S_allowed']
        assert not f['complete_so10_scalar_potential']
    def test_declared_no_x_behavior(self):
        assert self.ops['Phi17^3']['status']=='ALLOWED'
        assert self.ops['10_H^2 S Phi17']['status']=='ALLOWED'
        assert self.report['historical_continuous_X_comparison']['Phi17^3_status']=='CHARGE_FORBIDDEN'
    def test_core_so10_and_pq_results(self):
        assert self.ops['bare_10_H^2']['status']=='CHARGE_FORBIDDEN'
        assert self.ops['10_H^2 S']['status']=='ALLOWED'
        assert self.ops['210_H 10_H^dag 10_H']['status']=='SO10_FORBIDDEN'
        assert self.ops['210_H^dag 210_H 10_H^dag 10_H']['status']=='ALLOWED'
        assert self.ops['126bar_H^2 10_H^2 S^2']['charge_allowed']['all']
    def test_charge_helper_and_modes(self):
        total=mod._total_charge({'10_H':2,'S':1})
        assert total=={'PQ':0,'X':0,'Z17':0}
        phi3=mod._total_charge({'Phi17':3})
        assert mod._allowed(phi3)['all']
        assert not mod._allowed(phi3,require_x=True)['all']
