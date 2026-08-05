#!/usr/bin/env python3
"""CQIT receiver bridge for the SO(10) x Z17 v20 37 GHz axion target.

This module does not add a new interaction to the axion model. Galactic axion
conversion photons are generated inside the haloscope, so the cosmological
redshift operator of CQIT is the identity (z=0) for the laboratory signal.
The useful integration is instead a receiver null model:

    measured spectrum = receiver(noise, loss, template mismatch)[axion source]

Only reproducible residuals after calibration are candidates for additional
physics. Passing this module does not validate the SO(10) model or discover an
axion.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np

C_M_S = 299_792_458.0
DEFAULT_NU_HZ = 37.11e9
DEFAULT_HALO_Q = 1.0e6


def redshifted_mode_parameters(center_frequency_hz: float, bandwidth_hz: float, z: float) -> tuple[float, float]:
    """CQIT mode dilation. For locally generated haloscope photons use z=0."""
    if center_frequency_hz <= 0 or bandwidth_hz <= 0 or z <= -1:
        raise ValueError("invalid frequency, bandwidth, or redshift")
    scale = 1.0 + z
    return center_frequency_hz / scale, bandwidth_hz / scale


def normalized_mode_capture(signal: Iterable[float], template: Iterable[float]) -> float:
    """Squared normalized overlap in [0, 1] for a real matched-filter template."""
    s = np.asarray(signal, dtype=float)
    t = np.asarray(template, dtype=float)
    if s.shape != t.shape or s.ndim != 1 or s.size < 2:
        raise ValueError("signal and template must be same-length 1D arrays")
    ns = float(np.linalg.norm(s))
    nt = float(np.linalg.norm(t))
    if ns == 0.0 or nt == 0.0:
        raise ValueError("signal and template norms must be nonzero")
    overlap = float(np.dot(s, t) / (ns * nt))
    return float(np.clip(overlap * overlap, 0.0, 1.0))


def gaussian_lineshape(freq_hz: Iterable[float], center_hz: float, sigma_hz: float) -> np.ndarray:
    if center_hz <= 0 or sigma_hz <= 0:
        raise ValueError("center and sigma must be positive")
    f = np.asarray(freq_hz, dtype=float)
    return np.exp(-0.5 * ((f - center_hz) / sigma_hz) ** 2)


def gaussian_template_capture(
    frequency_offset_hz: float,
    signal_sigma_hz: float,
    template_sigma_hz: float | None = None,
    grid_sigma_extent: float = 10.0,
) -> float:
    """Numerically evaluate capture for shifted Gaussian power templates."""
    if signal_sigma_hz <= 0 or grid_sigma_extent <= 2:
        raise ValueError("invalid Gaussian parameters")
    template_sigma_hz = signal_sigma_hz if template_sigma_hz is None else template_sigma_hz
    if template_sigma_hz <= 0:
        raise ValueError("template sigma must be positive")
    extent = grid_sigma_extent * max(signal_sigma_hz, template_sigma_hz, abs(frequency_offset_hz), 1.0)
    grid = np.linspace(-extent, extent, 20001)
    signal = np.exp(-0.5 * (grid / signal_sigma_hz) ** 2)
    template = np.exp(-0.5 * ((grid - frequency_offset_hz) / template_sigma_hz) ** 2)
    return normalized_mode_capture(signal, template)


@dataclass(frozen=True)
class CoherenceBudget:
    center_frequency_hz: float
    halo_q: float
    linewidth_hz: float
    coherence_time_s: float
    integration_time_s: float
    independent_coherence_intervals: float

    def as_dict(self) -> dict:
        return asdict(self)


def axion_coherence_budget(
    center_frequency_hz: float = DEFAULT_NU_HZ,
    halo_q: float = DEFAULT_HALO_Q,
    integration_time_s: float = 7.0 * 86400.0,
) -> CoherenceBudget:
    """Return linewidth and coherence budget using tau_c = 1/(pi Delta nu)."""
    if center_frequency_hz <= 0 or halo_q <= 0 or integration_time_s <= 0:
        raise ValueError("frequency, Q and integration time must be positive")
    linewidth = center_frequency_hz / halo_q
    tau = 1.0 / (math.pi * linewidth)
    return CoherenceBudget(
        center_frequency_hz=float(center_frequency_hz),
        halo_q=float(halo_q),
        linewidth_hz=float(linewidth),
        coherence_time_s=float(tau),
        integration_time_s=float(integration_time_s),
        independent_coherence_intervals=float(integration_time_s / tau),
    )


@dataclass(frozen=True)
class ReceiverBudget:
    ideal_snr: float
    detector_efficiency: float
    mode_capture: float
    excess_noise_factor: float
    calibrated_signal_fraction: float
    effective_snr: float
    coupling_bias_if_uncorrected: float
    coupling_correction_factor: float

    def as_dict(self) -> dict:
        return asdict(self)


def receiver_budget(
    ideal_snr: float,
    detector_efficiency: float = 1.0,
    mode_capture: float = 1.0,
    excess_noise_factor: float = 1.0,
) -> ReceiverBudget:
    """Apply receiver loss/mismatch to radiometer SNR.

    Signal power is proportional to g_agamma^2. If detector efficiency and
    template capture are ignored, the inferred coupling is biased by the square
    root of their product.
    """
    if ideal_snr < 0 or not (0 <= detector_efficiency <= 1) or not (0 <= mode_capture <= 1):
        raise ValueError("invalid SNR or receiver probabilities")
    if excess_noise_factor < 1:
        raise ValueError("excess_noise_factor must be >= 1")
    signal_fraction = detector_efficiency * mode_capture
    effective_snr = ideal_snr * signal_fraction / excess_noise_factor
    bias = math.sqrt(signal_fraction)
    correction = math.inf if bias == 0 else 1.0 / bias
    return ReceiverBudget(
        ideal_snr=float(ideal_snr),
        detector_efficiency=float(detector_efficiency),
        mode_capture=float(mode_capture),
        excess_noise_factor=float(excess_noise_factor),
        calibrated_signal_fraction=float(signal_fraction),
        effective_snr=float(effective_snr),
        coupling_bias_if_uncorrected=float(bias),
        coupling_correction_factor=float(correction),
    )


def candidate_screen(
    effective_snr: float,
    frequency_ghz: float,
    linewidth_hz: float,
    independent_repeats: int,
    scan_window_ghz: tuple[float, float] = (36.6, 37.6),
    expected_linewidth_hz: float = DEFAULT_NU_HZ / DEFAULT_HALO_Q,
    linewidth_tolerance_fraction: float = 0.5,
    veto_triggered: bool = False,
    threshold_snr: float = 5.0,
) -> dict:
    """Conservative candidate triage; not a statistical discovery theorem."""
    if threshold_snr <= 0 or independent_repeats < 0 or linewidth_hz <= 0:
        raise ValueError("invalid screen inputs")
    lo, hi = scan_window_ghz
    line_ok = abs(linewidth_hz - expected_linewidth_hz) <= linewidth_tolerance_fraction * expected_linewidth_hz
    checks = {
        "snr": effective_snr >= threshold_snr,
        "frequency_window": lo <= frequency_ghz <= hi,
        "halo_linewidth": bool(line_ok),
        "independent_repeats": independent_repeats >= 2,
        "instrumental_veto_clear": not veto_triggered,
    }
    passed = all(checks.values())
    return {
        "checks": checks,
        "candidate_survives_triage": bool(passed),
        "discovery_claim_allowed": False,
        "reason": (
            "survives software triage; physical rescan and independent experiment required"
            if passed
            else "fails at least one receiver/null-test criterion"
        ),
    }


def build_bridge_report() -> dict:
    """Build the CQIT-to-axion integration verdict using v20 defaults."""
    try:
        from haloscope_scan_37ghz_v20 import benchmark_window, scan_forecast
        bench = benchmark_window()
        forecast = scan_forecast()
        nu_hz = float(bench["nu_central_Hz"])
        q_halo = float(bench["halo_Q"])
        ideal_snr = float(forecast["expected_SNR"])
    except ImportError:
        nu_hz = DEFAULT_NU_HZ
        q_halo = DEFAULT_HALO_Q
        ideal_snr = 5.0
        bench = {
            "nu_central_Hz": nu_hz,
            "nu_central_GHz": nu_hz / 1e9,
            "halo_Q": q_halo,
            "recommended_scan_GHz": [36.6, 37.6],
        }
        forecast = {"expected_SNR": ideal_snr, "source": "fallback defaults"}

    coherence = axion_coherence_budget(nu_hz, q_halo)
    local_center, local_bw = redshifted_mode_parameters(nu_hz, coherence.linewidth_hz, z=0.0)
    capture = gaussian_template_capture(0.25 * coherence.linewidth_hz, coherence.linewidth_hz / 2.355)
    receiver = receiver_budget(ideal_snr, detector_efficiency=0.75, mode_capture=capture, excess_noise_factor=1.2)
    screen = candidate_screen(
        effective_snr=receiver.effective_snr,
        frequency_ghz=nu_hz / 1e9,
        linewidth_hz=coherence.linewidth_hz,
        independent_repeats=1,
    )
    return {
        "status": "CQIT receiver bridge complete",
        "scientific_scope": {
            "new_axion_interaction_added": False,
            "cosmological_redshift_relevant_to_haloscope_signal": False,
            "laboratory_redshift_parameter": 0.0,
            "local_mode_identity_verified": bool(local_center == nu_hz and local_bw == coherence.linewidth_hz),
            "useful_integration": "receiver loss, template mismatch, coherence, noise, and residual triage",
        },
        "benchmark": bench,
        "source_forecast": forecast,
        "coherence": coherence.as_dict(),
        "receiver_example": receiver.as_dict(),
        "candidate_example": screen,
        "claims": {
            "validates_so10_model": False,
            "detects_axion": False,
            "new_physics": False,
            "improves_falsification_and_receiver_accounting": True,
        },
    }


def write_report(out_json: str | Path = "AXION_CQIT_BRIDGE_V20_VERDICT.json") -> dict:
    report = build_bridge_report()
    Path(out_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report = write_report()
    print(json.dumps(report, indent=2, sort_keys=True))
