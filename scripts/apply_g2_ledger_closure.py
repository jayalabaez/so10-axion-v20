from pathlib import Path


def replace_all(path: str, old: str, new: str, *, count: int | None = None) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    observed = text.count(old)
    if observed == 0:
        raise RuntimeError(f"pattern not found in {path}: {old[:80]!r}")
    if count is not None and observed != count:
        raise RuntimeError(f"expected {count} matches in {path}, found {observed}: {old[:80]!r}")
    p.write_text(text.replace(old, new), encoding="utf-8")


ledger = "live_g2_derivative_coverage_ledger_v20.py"
replace_all(ledger,
'''At this stage twelve base families have draft implementations of complete
486-real gradients and 486x486 Hessians.  Six quartic families remain.  This
ledger does not promote those implementations without execution and does not
close G2, stationarity, the vacuum problem, or any downstream gate.
''',
'''All eighteen authoritative base families now have exact full-coordinate
486-real gradients and 486x486 Hessians.  This ledger closes the G2 derivative
assembly only after checking the exact 18-family, 64-direction, 91-parameter
partition and a combined directional reconstruction.  It does not close
stationarity, the vacuum problem, or any downstream gate.
''')
replace_all(ledger,
'''import live_g2_exact_phi2_hdagh_derivatives_v20 as phi2h
''',
'''import live_g2_exact_phi2_hdagh_derivatives_v20 as phi2h
import live_g2_exact_phi_self_quartic_derivatives_v20 as phi_self
import live_g2_exact_sigma_self_quartic_derivatives_v20 as sigma_self
import live_g2_exact_unique_hsigma_chiral_derivatives_v20 as unique_hsigma
import live_g2_exact_final_mixed_quartic_derivatives_v20 as final_mixed
''')
replace_all(ledger,
'''    ("Phi2_HdagH_channels", (phi2h.BASE_FAMILY,), phi2h.all_direction_derivatives),
)

EXPECTED_REMAINING_FAMILIES = (
    "126bar_self_projectors",
    "unique_Hdag_Sigma2_Sigmadag",
    "unique_Hdag2_Sigma2",
    "Phi2_Sigma_projectors",
    "Phi2_Hdag_Sigma_210_1050",
    "Phi_self_quartics",
)
''',
'''    ("Phi2_HdagH_channels", (phi2h.BASE_FAMILY,), phi2h.all_direction_derivatives),
    ("Phi_self_quartics", (phi_self.BASE_FAMILY,), phi_self.all_direction_derivatives),
    ("Sigma_self_quartics", (sigma_self.BASE_FAMILY,), sigma_self.all_direction_derivatives),
    ("unique_HSigma_chiral", tuple(unique_hsigma.SELECTED_FAMILIES), unique_hsigma.all_direction_derivatives),
    ("final_mixed_quartics", tuple(final_mixed.SELECTED_FAMILIES), final_mixed.all_direction_derivatives),
)

EXPECTED_REMAINING_FAMILIES: tuple[str, ...] = ()
''')
replace_all(ledger,
'''    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
''',
'''    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
''')
replace_all(ledger, '"covered_family_count_is_12": len(covered) == 12,', '"covered_family_count_is_18": len(covered) == 18,')
replace_all(ledger,
'''        "remaining_family_count_is_6": len(remaining_families) == 6,
        "remaining_family_set_matches_declared_frontier": set(remaining_families)
        == set(EXPECTED_REMAINING_FAMILIES),
        "remaining_directions_nonzero": len(remaining_rows) > 0,
        "remaining_parameters_nonzero": len(remaining_parameter_ids) > 0,
        "complete_64_direction_derivatives_not_claimed": len(rows) < 64,
        "G2_not_closed": True,
''',
'''        "all_18_base_families_covered": len(remaining_families) == 0,
        "remaining_family_set_empty": set(remaining_families)
        == set(EXPECTED_REMAINING_FAMILIES),
        "all_64_direction_derivatives_complete": len(rows) == len(live_directions) == 64,
        "all_91_real_parameter_derivatives_complete": (
            len(parameter_id_set) == len(live_parameters) == 91
        ),
        "remaining_directions_zero": len(remaining_rows) == 0,
        "remaining_parameters_zero": len(remaining_parameter_ids) == 0,
        "G2_closed": True,
''')
replace_all(ledger, '"G2_DERIVATIVE_COVERAGE_12_OF_18_FAMILIES_ASSEMBLED"', '"G2_DERIVATIVE_COVERAGE_18_OF_18_FAMILIES_CLOSED"')
replace_all(ledger, '"overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",', '"overall_state": "CLOSED" if not failures else "EXECUTION_FAIL",')
replace_all(ledger,
'''                "twelve_full_coordinate_family_adapters_implemented": not failures,
                "all_implemented_direction_gradients_assembled": not failures,
                "all_implemented_direction_Hessians_assembled": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
''',
'''                "eighteen_full_coordinate_family_adapters_implemented": not failures,
                "all_implemented_direction_gradients_assembled": not failures,
                "all_implemented_direction_Hessians_assembled": not failures,
                "all_64_direction_gradients_complete": not failures,
                "all_64_direction_Hessians_complete": not failures,
                "all_91_real_parameter_derivatives_complete": not failures,
                "G2_closed": not failures,
''')
replace_all(ledger,
'''            "next_exact_target": (
                "Implement and verify the six remaining quartic adapters: "
                + ", ".join(remaining_families)
                + "."
            ),
            "verdict": (
                "The draft derivative chain covers twelve of eighteen authoritative "
                "base families with full 486-real gradients and Hessians and one "
                "combined fail-closed assembly. Six quartic families remain. Hosted "
                "execution is still required before promotion, and G2 remains PARTIAL."
            ),
''',
'''            "next_exact_target": (
                "Proceed to G3: solve the full stationarity system and classify all "
                "competing extrema using the closed 486-real G2 potential derivatives."
            ),
            "verdict": (
                "All eighteen authoritative G2 base families, all 64 invariant "
                "directions, and all 91 real parameters are assembled into one exact "
                "486-real gradient and symmetric 486x486 Hessian with no ownership, "
                "direction, or parameter gaps. G2 is closed; stationarity, vacuum "
                "selection, and G3-G8 remain open."
            ),
''')

test = "test_live_g2_derivative_coverage_ledger_v20.py"
for old, new in (
    ("test_report_passes_without_closing_G2", "test_report_closes_G2_without_closing_downstream_gates"),
    ('coverage["base_families_implemented"] == 12', 'coverage["base_families_implemented"] == 18'),
    ('coverage["base_families_remaining"] == 6', 'coverage["base_families_remaining"] == 0'),
    ('0 < coverage["directions_implemented"] < 64', 'coverage["directions_implemented"] == 64'),
    ('coverage["directions_remaining"] > 0', 'coverage["directions_remaining"] == 0'),
    ('0 < coverage["real_parameters_implemented"] < 91', 'coverage["real_parameters_implemented"] == 91'),
    ('coverage["real_parameters_remaining"] > 0', 'coverage["real_parameters_remaining"] == 0'),
    ('report["flags"]["twelve_full_coordinate_family_adapters_implemented"]', 'report["flags"]["eighteen_full_coordinate_family_adapters_implemented"]'),
    ('assert report["flags"]["all_64_direction_gradients_complete"] is False', 'assert report["flags"]["all_64_direction_gradients_complete"] is True'),
    ('assert report["flags"]["all_64_direction_Hessians_complete"] is False', 'assert report["flags"]["all_64_direction_Hessians_complete"] is True'),
    ('assert report["flags"]["G2_closed"] is False', 'assert report["flags"]["G2_closed"] is True'),
    ('assert len(covered) == 12', 'assert len(covered) == 18'),
    ('assert len(set(covered)) == 12', 'assert len(set(covered)) == 18'),
):
    replace_all(test, old, new)
replace_all(test,
'''    assert set(covered).isdisjoint(remaining)
    assert set(covered) | remaining == all_families
''',
'''    assert remaining == set()
    assert set(covered) == all_families
''')
replace_all(test,
'''def test_exact_remaining_frontier_is_declared():
    report = mod.build_report()
    assert set(report["coverage"]["remaining_families"]) == set(
        mod.EXPECTED_REMAINING_FAMILIES
    )
    assert report["coverage"]["remaining_families"]
    assert "six remaining quartic adapters" in report["next_exact_target"]
''',
'''def test_no_remaining_G2_frontier_and_G3_is_next():
    report = mod.build_report()
    assert report["coverage"]["remaining_families"] == []
    assert mod.EXPECTED_REMAINING_FAMILIES == ()
    assert report["coverage"]["directions_remaining"] == 0
    assert report["coverage"]["real_parameters_remaining"] == 0
    assert "Proceed to G3" in report["next_exact_target"]
''')

workflow = ".github/workflows/live-g2-derivative-coverage-ledger.yml"
replace_all(workflow,
'''      - live_g2_exact_phi2_hdagh_derivatives_v20.py
      - live_g2_arbitrary_component_potential_values_v20.py
''',
'''      - live_g2_exact_phi2_hdagh_derivatives_v20.py
      - live_g2_exact_phi_self_quartic_derivatives_v20.py
      - live_g2_exact_sigma_self_quartic_derivatives_v20.py
      - live_g2_exact_unique_hsigma_chiral_derivatives_v20.py
      - live_g2_exact_final_mixed_quartic_derivatives_v20.py
      - live_g2_arbitrary_component_potential_values_v20.py
''', count=2)
replace_all(workflow,
'''    timeout-minutes: 420
    steps:
''',
'''    timeout-minutes: 420
    env:
      OPENBLAS_NUM_THREADS: "1"
      OMP_NUM_THREADS: "1"
      MKL_NUM_THREADS: "1"
      NUMEXPR_NUM_THREADS: "1"
    steps:
''')
replace_all(workflow,
'''            live_g2_exact_phi2_hdagh_derivatives_v20.py \\
            live_g2_derivative_coverage_ledger_v20.py \\
''',
'''            live_g2_exact_phi2_hdagh_derivatives_v20.py \\
            live_g2_exact_phi_self_quartic_derivatives_v20.py \\
            live_g2_exact_sigma_self_quartic_derivatives_v20.py \\
            live_g2_exact_unique_hsigma_chiral_derivatives_v20.py \\
            live_g2_exact_final_mixed_quartic_derivatives_v20.py \\
            live_g2_derivative_coverage_ledger_v20.py \\
''')
replace_all(workflow,
'''            test_live_g2_exact_phi2_hdagh_derivatives_v20.py \\
            test_live_g2_derivative_coverage_ledger_v20.py
''',
'''            test_live_g2_exact_phi2_hdagh_derivatives_v20.py \\
            test_live_g2_exact_phi_self_quartic_derivatives_v20.py \\
            test_live_g2_exact_sigma_self_quartic_derivatives_v20.py \\
            test_live_g2_exact_unique_hsigma_chiral_derivatives_v20.py \\
            test_live_g2_exact_final_mixed_quartic_derivatives_v20.py \\
            test_live_g2_derivative_coverage_ledger_v20.py
''')
for old, new in (
    ("assert c['base_families_implemented']==12", "assert c['base_families_implemented']==18"),
    ("assert c['base_families_remaining']==6", "assert c['base_families_remaining']==0"),
    ("assert 0<c['directions_implemented']<64", "assert c['directions_implemented']==64"),
    ("assert c['directions_remaining']>0", "assert c['directions_remaining']==0"),
    ("assert 0<c['real_parameters_implemented']<91", "assert c['real_parameters_implemented']==91"),
    ("assert c['real_parameters_remaining']>0", "assert c['real_parameters_remaining']==0"),
    ("assert report['flags']['twelve_full_coordinate_family_adapters_implemented']", "assert report['flags']['eighteen_full_coordinate_family_adapters_implemented']"),
    ("assert not report['flags']['all_64_direction_gradients_complete']", "assert report['flags']['all_64_direction_gradients_complete']"),
    ("assert not report['flags']['all_64_direction_Hessians_complete']", "assert report['flags']['all_64_direction_Hessians_complete']"),
    ("assert not report['flags']['G2_closed']", "assert report['flags']['G2_closed']"),
):
    replace_all(workflow, old, new)
replace_all(workflow,
'''          assert set(c['remaining_families'])=={
              '126bar_self_projectors',
              'unique_Hdag_Sigma2_Sigmadag',
              'unique_Hdag2_Sigma2',
              'Phi2_Sigma_projectors',
              'Phi2_Hdag_Sigma_210_1050',
              'Phi_self_quartics',
          }
''',
'''          assert c['remaining_families']==[]
          assert report['overall_state']=='CLOSED'
''')
replace_all(workflow,
'''          assert report['flags']['all_64_direction_Hessians_complete']
          assert report['flags']['G2_closed']
''',
'''          assert report['flags']['all_64_direction_Hessians_complete']
          assert report['flags']['all_91_real_parameter_derivatives_complete']
          assert report['flags']['G2_closed']
''')

print("G2 ledger closure patch applied")
