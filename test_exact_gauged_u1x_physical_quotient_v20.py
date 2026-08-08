"""Regressions for the exact gauged-U(1)_X physical quotient certificate."""

import copy
import json

import exact_gauged_u1x_physical_quotient_v20 as quotient


def test_integer_minor_and_nullspace_certify_removed_rank_38() -> None:
    report = quotient.exact_quotient_certificate()

    assert report["arithmetic_domain"].startswith("Z")
    assert report["certified"] is True
    assert report["failures"] == []
    assert report["SO10"]["rank"] == 36
    assert report["SO10"]["stabilizer_dimension"] == 9
    assert report["SO10"]["minor"]["shape"] == [36, 36]
    assert report["SO10"]["minor"]["determinant"] == "1"
    assert len(report["SO10"]["right_nullspace"]) == 9
    assert report["SO10"]["null_vector_rank"] == 9

    gauge = report["gauged_symmetry"]
    assert gauge["rank"] == 37
    assert gauge["right_nullity"] == 9
    assert gauge["minor"]["shape"] == [37, 37]
    assert gauge["minor"]["determinant"] == "-2"
    assert gauge["null_vector_rank"] == 9
    assert gauge["gauge_quotient_dimension_including_axion"] == 449

    full = report["full_removed_symmetry"]
    assert full["rank"] == 38
    assert full["right_nullity"] == 9
    assert full["minor"]["shape"] == [38, 38]
    assert full["minor"]["determinant"] == "34"
    assert full["all_null_residuals_exactly_zero"] is True
    assert full["null_vector_rank"] == 9
    assert len(full["right_nullspace"]) == 9
    assert report["gauge_quotient_dimension_including_axion"] == 449
    assert report["massive_transverse_quotient_dimension"] == 448
    assert report["physical_quotient_dimension"] == 448


def test_u1x_and_pq_are_exactly_independent_on_s_and_phi17() -> None:
    phase = quotient.exact_quotient_certificate()["U1X_PQ_independence"]

    assert phase["rows"] == ["S.y", "Phi17.y"]
    assert phase["columns"] == ["U1X", "PQ"]
    assert phase["minor"] == [[4, 4], [17, 0]]
    assert phase["determinant"] == -68


def test_exact_matrix_is_directly_bound_to_live_canonical_tangents() -> None:
    binding = quotient.live_compiler_binding_audit()

    assert binding["exact_matrix_shape"] == [486, 47]
    assert binding["live_matrix_shape"] == [486, 47]
    assert binding["all_block_scales_nonzero"] is True
    assert binding["maximum_absolute_residual"] < 1.0e-15
    assert binding["maximum_unscaled_residual"] < 1.0e-15
    assert binding["compiler_binding_passes"] is True


def test_full_report_requires_exact_certificate_and_compiler_binding() -> None:
    report = quotient.build_report()

    assert report["status"] == "EXACT_PHYSICAL_QUOTIENT_CERTIFIED"
    assert report["certified"] is True
    assert report["gauge_quotient_dimension_including_axion"] == 449
    assert report["massive_transverse_quotient_dimension"] == 448
    assert report["physical_quotient_dimension"] == 448


def test_artifacts_are_deterministic_concise_and_proof_critical(tmp_path) -> None:
    report = quotient.build_report()
    out_json = tmp_path / "certificate.json"
    out_md = tmp_path / "certificate.md"

    quotient.write_report(report, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_markdown = out_md.read_text(encoding="utf-8")
    quotient.write_report(report, out_json=out_json, out_md=out_md)

    assert out_json.read_text(encoding="utf-8") == first_json
    assert out_md.read_text(encoding="utf-8") == first_markdown
    assert first_json == quotient.render_json(report)
    assert first_json.endswith("\n")
    loaded = json.loads(first_json)
    assert loaded["certified"] is True
    assert loaded["gauge_quotient_dimension_including_axion"] == 449
    assert loaded["massive_transverse_quotient_dimension"] == 448

    assert "SO(10)+U(1)_X gauge rank: `37`" in first_markdown
    assert "gauge quotient including the physical axion: `449`" in first_markdown
    assert "massive/transverse Hessian quotient: `448`" in first_markdown
    assert "live compiler maximum unscaled residual: `0.0`" in first_markdown
    assert "primitive_integer_vector" not in first_markdown


def test_cli_write_path_returns_zero_and_emits_json(monkeypatch, capsys) -> None:
    report = quotient.build_report()
    writes = []
    monkeypatch.setattr(quotient, "build_report", lambda: report)
    monkeypatch.setattr(
        quotient,
        "write_report",
        lambda value: writes.append(value),
    )

    assert quotient.main(["--write"]) == 0
    assert writes == [report]
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["status"] == "EXACT_PHYSICAL_QUOTIENT_CERTIFIED"
    assert emitted["certified"] is True


def test_cli_fails_closed_if_exact_proof_or_compiler_binding_fails(
    monkeypatch, capsys
) -> None:
    for failing_path in ("exact", "binding"):
        report = copy.deepcopy(quotient.build_report())
        report["certified"] = True
        if failing_path == "exact":
            report["exact_certificate"]["certified"] = False
        else:
            report["live_compiler_binding"]["compiler_binding_passes"] = False
        monkeypatch.setattr(quotient, "build_report", lambda report=report: report)

        assert quotient.main([]) == 1
        emitted = json.loads(capsys.readouterr().out)
        assert quotient.report_passes(emitted) is False
