import json
import shutil

import pytest

import susy_v24_ps_source_contract as source


def test_exact_z4r_z11_charge_assignment() -> None:
    expected = {
        "H": (0, 0),
        "Q": (1, 0),
        "Qc": (1, 0),
        "X": (2, 0),
        "Sc": (0, 0),
        "Sbc": (0, 0),
        "Sigma": (2, 0),
        "PsiBar": (3, 10),
        "Psi": (1, 0),
        "PsiC": (1, 0),
        "PsiCBar": (3, 10),
        "P": (2, 1),
        "N": (1, 0),
    }
    assert {
        row["name"]: (row["Z4R_charge"], row["Z11_charge"])
        for row in source.FIELDS
    } == expected


def test_exhaustive_renormalizable_census_equals_landed_W() -> None:
    census = source.exhaustive_renormalizable_census()
    allowed = {
        tuple(sorted(row["monomial"]))
        for row in census
        if row["allowed_in_superpotential"]
    }
    landed = {
        tuple(sorted(row["monomial"]))
        for row in source.RENORMALIZABLE_OPERATORS
    }
    assert len(census) == 80
    assert len(allowed) == 18
    assert allowed == landed
    assert all(row["PS_singlet_multiplicity"] == 1 for row in source.RENORMALIZABLE_OPERATORS)


def test_required_and_forbidden_operator_ledger() -> None:
    required = {row["key"]: row for row in source.RENORMALIZABLE_OPERATORS}
    assert {
        "X_H_H",
        "X_Sigma_Sigma",
        "Q_H_PsiC",
        "Psi_H_Qc",
        "Psi_H_PsiC",
        "P_PsiBar_Q",
        "P_PsiBar_Psi",
        "P_PsiCBar_Qc",
        "P_PsiCBar_PsiC",
        "Sbc_Qc_N",
        "Sbc_PsiC_N",
        "N_N",
    } <= required.keys()
    assert all(row["allowed_in_superpotential"] for row in required.values())

    audited = {row["key"]: row for row in source.FORBIDDEN_AND_LEADING}
    for key in (
        "bare_mu",
        "bare_PS_mass",
        "bare_sextet_mass",
        "bare_X_mass",
        "bare_left_vector_mass",
        "bare_right_vector_mass",
        "P_to_10",
        "bilinear_RPV",
        "HQS_RPV",
        "QQQQ",
        "QcQcQcQc",
    ):
        assert not audited[key]["allowed_in_superpotential"]
    assert audited["P_to_11"]["allowed_in_superpotential"]
    assert audited["Majorana_EFT"]["allowed_in_superpotential"]


def test_sarah_sextet_symbol_and_multiline_W_regressions() -> None:
    assert "SuperFields[[7]]  = {Sig6" in source.MODEL_TEXT
    assert "X.Sig6.Sig6" in source.MODEL_TEXT
    assert "Sc.Sc.Sig6" in source.MODEL_TEXT
    assert "Sbc.Sbc.Sig6" in source.MODEL_TEXT
    assert "X.Sigma.Sigma" not in source.MODEL_TEXT
    assert "SuperPotential = (" in source.MODEL_TEXT
    assert "V24RenormalizableOperatorClassCount" not in source.MODEL_TEXT
    assert "processed_W_full_structural_multiset_exact" in source.VALIDATOR_TEXT
    assert '"Dot::dotsh"' in source.VALIDATOR_TEXT


def test_discrete_continuous_and_GS_anomaly_ledgers() -> None:
    anomaly = source.anomaly_ledger()
    assert anomaly["Z4R_mixed_visible_representatives"] == {"SU4": 7, "SU2L": 5, "SU2R": 1}
    assert anomaly["Z4R_mixed_mod2"] == {"SU4": 1, "SU2L": 1, "SU2R": 1}
    assert anomaly["Z4R_visible_gravitational_representative"] == 20
    assert anomaly["Z4R_gravitational_GS_condition_closed"]
    assert anomaly["Z11_mixed_visible_signed_representatives"] == {"SU4": -2, "SU2L": -2, "SU2R": -2}
    assert anomaly["Z11_mixed_mod11"] == {"SU4": 9, "SU2L": 9, "SU2R": 9}
    assert anomaly["Z11_gravitational_signed_representative"] == -15
    assert anomaly["Z11_gravitational_mod11"] == 7 == anomaly["Z11_gravitational_24rho_mod11"]
    assert anomaly["Z11_gravitational_GS_condition_closed"]
    gs = anomaly["GS_topological_source_contract"]
    assert gs["Kac_Moody_levels"] == {"k4": 1, "kL": 1, "kR": 1}
    assert gs["Z4R_shift_theta_GS_mod1"] == "-1/2"
    assert gs["Z11_shift_theta_GS_mod1"] == "-9/11"
    assert not anomaly["dynamical_GS_modulus_stabilization_landed"]
    assert not anomaly["UV_realization_of_discrete_GS_landed"]

    continuous = source.continuous_anomaly_and_beta_ledger()
    assert continuous["continuous_gauge_anomalies_cancel"]
    assert continuous["SU2L_Witten_doublet_count"] == 22
    assert continuous["SU2R_Witten_doublet_count"] == 30
    assert continuous["one_loop_b_PS"] == {"SU4": 1, "SU2L": 5, "SU2R": 9}


def test_table6_redressing_quality_matter_parity_and_wall_boundary() -> None:
    ledger = source.higher_operator_ledger()
    assert len(ledger["superpotential_rows"]) == 18
    assert len(ledger["Kahler_rows"]) == 41
    pure_w = ledger["leading_pure_superpotential_breaker"]
    pure_k = ledger["leading_pure_Kahler_breaker"]
    assert (pure_w["P_power"], pure_w["Pdag_power"], pure_w["w0_power"]) == (11, 0, 0)
    assert (pure_k["P_power"], pure_k["Pdag_power"], pure_k["w0_power"]) == (11, 0, 1)
    assert ledger["conditional_P_only_W_quality_estimate_log10_Delta_theta"] == -25
    assert ledger["conditional_P_only_K_quality_estimate_log10_Delta_theta"] == -51
    for row in ledger["superpotential_rows"] + ledger["Kahler_rows"]:
        if row["allowed_P_Pdag_w0_dressing_exists"]:
            assert row["dressed_Z11_mod11"] == 0
            assert row["dressed_Z4R_mod4"] == (0 if row["operator_class"] == "Kahler" else 2)
            assert row["net_PQ_violation"] != 0
        else:
            assert row["base_Z4R_mod4"] % 2 == 1
    assert ledger["matter_parity"]["exact_to_all_P_and_w0_orders"]
    assert ledger["conditional_P_only_wall_arithmetic"]["gcd"] == 1
    assert ledger["conditional_P_only_wall_arithmetic"]["is_not_a_physical_wall_proof"]
    assert not ledger["physical_wall_vacuum_structure_closed"]
    assert ledger["physical_wall_requires_dynamical_GS_axion_and_argP_mixing"]
    assert not ledger["physical_mixed_axion_quality_closed"]


def test_normalized_tensors_and_generic_PS_rank() -> None:
    tensor = source.tensor_ledger()
    assert tensor["all_renormalizable_multiplicities_are_one"]
    assert tensor["EFT_Sbc2_Qc2_bosonic_singlet_multiplicity"] == 2
    assert tensor["N_exchange_selected_channel_multiplicity"] == 1
    vacuum = source.vacuum_and_rank_ledger()
    hessian = vacuum["generic_PS_breaking_sector_chiral_W_Hessian"]
    witness = hessian["rational_witness"]
    labels, matrix = source.construct_breaking_hessian(
        kappa=witness["kappa"],
        lambda_s=witness["lambdaS"],
        lambda_sb=witness["lambdaSb"],
        vev=witness["vPS"],
    )
    assert labels == hessian["component_ordering"]
    assert source._fraction_rank(matrix) == hessian["computed_exact_rank"] == 14
    assert len(labels) - source._fraction_rank(matrix) == hessian["computed_nullity"] == 9
    assert len(hessian["exact_RREF_pivot_columns_zero_based"]) == 14
    assert hessian["radial_block"]["computed_rank"] == 2
    assert hessian["colored_block"]["computed_rank"] == 12
    assert len(hessian["identically_zero_rows"]) == 8
    assert all(row["exact_rank"] == 14 for row in hessian["coefficient_perturbation_ranks"])
    assert "not a gauge-fixed" in hessian["scope_boundary"]
    assert vacuum["breaking_sector_physical_chiral_nullity_after_super_Higgs"] == 0
    assert vacuum["chiral_families_left_after_P_VEV"] == 3
    assert vacuum["chiral_families_right_after_P_VEV"] == 3
    assert not vacuum["physical_axion_domain_wall_number_closed"]


def test_frozen_bundle_is_self_consistent_and_has_no_obsolete_model() -> None:
    assert {
        path.name for path in (source.ROOT / "models").glob("PSZ4RZ*SUSYV24")
    } == {"PSZ4RZ11SUSYV24"}
    assert source.MODEL_DIR.name == "PSZ4RZ11SUSYV24"
    assert source.check_all(live_sarah=False) == 0
    report = json.loads(source.OUT_JSON.read_text(encoding="utf-8"))
    assert report["core_sha256"] == source.canonical_sha(report)
    assert all(report["checks"].values())
    assert report["sarah_Start_attestation"]["all_required_checks_pass"]
    assert report["sarah_Start_attestation"]["processed_superpotential_term_count"] == 18
    assert report["sarah_Start_attestation"]["checks"]["processed_W_full_structural_multiset_exact"]
    assert report["sarah_Start_attestation"]["checks"]["processed_component_superpotential_nonzero"]
    assert report["sarah_Start_attestation"]["checks"]["full_process_log_free_of_Dot_dotsh"]
    assert report["physics_to_SARAH_symbol_map"]["Sigma"] == "Sig6"


@pytest.mark.skipif(
    shutil.which("wolframscript") is None or not (source.SARAH_ROOT / "SARAH.m").is_file(),
    reason="live Wolfram/SARAH toolchain is unavailable",
)
def test_live_sarah_start_attestation() -> None:
    fresh, output = source.run_sarah_validator()
    assert fresh["all_required_checks_pass"], output
    assert fresh["processed_superpotential_term_count"] == 18
    assert "Dot::dotsh" not in output
    assert fresh["checks"] == json.loads(source.OUT_JSON.read_text(encoding="utf-8"))["sarah_Start_attestation"]["checks"]
