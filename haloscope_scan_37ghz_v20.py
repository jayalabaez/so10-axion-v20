#!/usr/bin/env python3
"""37 GHz haloscope scan package for the v20 axion benchmark.

IMPORTANT
---------
This module does **not** operate a physical haloscope and does **not**
detect dark matter.  It produces the complete numerical scan forecast,
Dicke radiometer SNR map, expected signal power, lineshape templates and
exclusion/discovery criteria that an experiment (MADMAX / ALPHA / ORGAN)
would need to target the window

    nu = 36.6 – 37.6 GHz    (m_a = 151.5 – 155.6 µeV)

at the v20 coupling g_agamma ~ 2.335e-14 GeV^{-1}.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


# Physical constants
HBAR_EV_S = 6.582119569e-16  # eV s
H_EV_HZ = 4.135667696e-15  # eV/Hz
C_M_S = 2.99792458e8
K_B = 1.380649e-23  # J/K
EV_TO_J = 1.602176634e-19

# v20 benchmark
MA_UEV = 153.5
MA_UEV_UNC = 2.0
G_AGG = 2.335e-14  # GeV^{-1}
G_AGG_UNC = 0.125e-14
E_OVER_N = 8.0 / 3.0
FA_GEV = 6.313855e11 / 17.0  # v_S/17

# Local DM
RHO_DM_GEV_CM3 = 0.45  # GeV/cm^3
V_0 = 220e3  # m/s circular
V_ESC = 544e3
SIGMA_V = V_0 / math.sqrt(2.0)


def mass_uev_to_hz(m_uev: float) -> float:
    # E = m c^2 ; f = E/h ; m in µeV
    m_ev = m_uev * 1.0e-6
    return m_ev / H_EV_HZ


def hz_to_mass_uev(freq_hz: float) -> float:
    return freq_hz * H_EV_HZ * 1.0e6


def benchmark_window() -> dict:
    nu0 = mass_uev_to_hz(MA_UEV)
    nu_lo = mass_uev_to_hz(MA_UEV - MA_UEV_UNC)
    nu_hi = mass_uev_to_hz(MA_UEV + MA_UEV_UNC)
    # Halo linewidth ~ nu / Q_halo with Q~1e6
    q_halo = 1.0e6
    return {
        "m_a_ueV": MA_UEV,
        "m_a_uncertainty_ueV": MA_UEV_UNC,
        "nu_central_Hz": nu0,
        "nu_central_GHz": nu0 / 1e9,
        "window_GHz": [nu_lo / 1e9, nu_hi / 1e9],
        "recommended_scan_GHz": [36.6, 37.6],
        "g_agamma_GeV_inv": G_AGG,
        "g_agamma_uncertainty": G_AGG_UNC,
        "E_over_N": E_OVER_N,
        "f_a_GeV": FA_GEV,
        "halo_Q": q_halo,
        "linewidth_kHz": (nu0 / q_halo) / 1e3,
    }


def axion_lineshape(freq_hz: np.ndarray, nu_a: float) -> np.ndarray:
    """Standard isothermal-sphere axion lineshape (approx. Maxwellian)."""
    # beta = v^2/c^2 distribution -> df/f ~ order 1e-6
    width = nu_a / 1.0e6
    x = (freq_hz - nu_a) / width
    # One-sided roughly for galactic rest; use symmetric Gaussian proxy
    pdf = np.exp(-0.5 * x**2) / (math.sqrt(2.0 * math.pi) * width)
    return pdf


def expected_power_cavity(
    g_agamma: float,
    b_tesla: float,
    volume_m3: float,
    c_form: float = 0.5,
    rho_gev_cm3: float = RHO_DM_GEV_CM3,
) -> float:
    """Order-of-magnitude cavity power (SI watts).

    P ~ g^2 B^2 V rho / m_a * C  (natural units converted).
    Normalised so that a 10 T, 1 L, C=0.5 cavity at DFSZ-ish coupling
    near 1 GHz gives ~1e-23 W scale; used only comparatively at 37 GHz
    where cavity volume must shrink.
    """
    # Convert g from GeV^{-1} ; use practical formula from ADMX literature:
    # P = 1.55e-22 W * (g/1e-12)^2 * (B/10T)^2 * (V/100L) * (C/0.5)
    #     * (rho/0.45) * min(Q_l, Q_a)/1e5  * ...
    # At 37 GHz a cylindrical cavity V shrinks ~ 1/nu^3 relative to 1 GHz.
    g12 = g_agamma / 1.0e-12
    v_l = volume_m3 * 1.0e3  # litres
    return (
        1.55e-22
        * g12**2
        * (b_tesla / 10.0) ** 2
        * (v_l / 100.0)
        * (c_form / 0.5)
        * (rho_gev_cm3 / 0.45)
    )


def expected_power_dielectric(
    g_agamma: float,
    b_tesla: float,
    area_m2: float,
    boost_beta2: float,
    rho_gev_cm3: float = RHO_DM_GEV_CM3,
) -> float:
    """MADMAX-like dielectric haloscope power (watts).

    Calibrated so that a full-scale 10 T, 1 m^2, beta2~5e4 setup at the
    DFSZ-like coupling ~2e-14 GeV^{-1} yields ~1e-22 W near 100 µeV
    (order of magnitude matching published MADMAX projections).
    """
    return (
        1.0e-22
        * (g_agamma / 2.0e-14) ** 2
        * (b_tesla / 10.0) ** 2
        * (area_m2 / 1.0)
        * (boost_beta2 / 5.0e4)
        * (rho_gev_cm3 / 0.45)
        * (100.0 / MA_UEV)
    )


def dicke_sensitivity(
    t_sys_k: float,
    bandwidth_hz: float,
    t_int_s: float,
    snr: float = 5.0,
) -> float:
    """Minimum detectable power from Dicke radiometer equation."""
    return snr * K_B * t_sys_k * math.sqrt(bandwidth_hz / t_int_s)


def scan_forecast(
    scan_lo_ghz: float = 36.6,
    scan_hi_ghz: float = 37.6,
    channel_mhz: float = 40.0,
    t_sys_k: float = 8.0,
    t_per_channel_s: float = 7.0 * 24.0 * 3600.0,  # 7 days / 40 MHz window
    b_tesla: float = 10.0,
    area_m2: float = 1.0,
    boost_beta2: float = 1.0e5,
    snr_discovery: float = 5.0,
) -> dict:
    n_channels = max(1, int(round((scan_hi_ghz - scan_lo_ghz) * 1e3 / channel_mhz)))
    p_sig = expected_power_dielectric(G_AGG, b_tesla, area_m2, boost_beta2)
    bw = mass_uev_to_hz(MA_UEV) / 1.0e6
    p_min = dicke_sensitivity(t_sys_k, bw, t_per_channel_s, snr_discovery)
    snr = p_sig / dicke_sensitivity(t_sys_k, bw, t_per_channel_s, snr=1.0)
    lam = C_M_S / (37.11e9)
    v_cav = (0.5 * lam) ** 3
    p_cav = expected_power_cavity(G_AGG, b_tesla, v_cav)
    return {
        "technology": "dielectric_disk_stack_MADMAX_like",
        "scan_GHz": [scan_lo_ghz, scan_hi_ghz],
        "n_channels": n_channels,
        "channel_MHz": channel_mhz,
        "t_sys_K": t_sys_k,
        "t_per_channel_s": t_per_channel_s,
        "total_integration_days": n_channels * t_per_channel_s / 86400.0,
        "B_T": b_tesla,
        "area_m2": area_m2,
        "boost_beta2": boost_beta2,
        "expected_signal_power_W": p_sig,
        "dicke_pmin_5sigma_W": p_min,
        "expected_SNR": snr,
        "discovery_threshold_SNR": snr_discovery,
        "reaches_v20_coupling": bool(snr >= snr_discovery),
        "cavity_comparison": {
            "volume_m3": v_cav,
            "expected_power_W": p_cav,
            "note": "traditional cavity volume is tiny at 37 GHz; dielectric/plasma preferred",
        },
        "collaborations": ["MADMAX", "ALPHA", "ORGAN"],
        "reference_assumption": (
            "7 days per 40 MHz window, Tsys=8 K, beta2=5e4, B=10 T, A=1 m^2 "
            "(MADMAX full-scale order-of-magnitude)"
        ),
    }


def mock_scan_spectrum(
    seed: int = 20,
    inject_signal: bool = True,
    scan_lo_ghz: float = 36.6,
    scan_hi_ghz: float = 37.6,
) -> dict:
    """Simulate a radiometer scan across the window (noise + optional signal)."""
    rng = np.random.default_rng(seed)
    forecast = scan_forecast(scan_lo_ghz, scan_hi_ghz)
    n = max(forecast["n_channels"] * 40, 50)  # finer bins inside windows
    freqs = np.linspace(scan_lo_ghz * 1e9, scan_hi_ghz * 1e9, n)
    bw = mass_uev_to_hz(MA_UEV) / 1.0e6
    p_noise_rms = dicke_sensitivity(
        forecast["t_sys_K"], bw, forecast["t_per_channel_s"], snr=1.0
    )
    baseline = p_noise_rms * (1.0 + 0.05 * rng.normal(size=n))
    noise = p_noise_rms * rng.normal(size=n)
    spectrum = baseline + noise
    injected = None
    true_snr = 0.0
    if inject_signal:
        nu_a = mass_uev_to_hz(MA_UEV)
        shape = axion_lineshape(freqs, nu_a)
        shape /= max(shape.max(), 1e-300)
        spectrum = spectrum + forecast["expected_signal_power_W"] * shape
        injected = {
            "nu_GHz": nu_a / 1e9,
            "m_a_ueV": MA_UEV,
            "peak_power_W": float(forecast["expected_signal_power_W"]),
        }
        true_snr = float(forecast["expected_SNR"])
    # Matched filter against known lineshape
    nu_a = mass_uev_to_hz(MA_UEV)
    template = axion_lineshape(freqs, nu_a)
    template /= max(np.linalg.norm(template), 1e-300)
    residual = spectrum - baseline
    filt = float(np.dot(residual, template) / max(p_noise_rms, 1e-45))
    discovery = bool(inject_signal and true_snr >= forecast["discovery_threshold_SNR"])
    return {
        "inject_signal": inject_signal,
        "injected": injected,
        "matched_filter_SNR": filt,
        "expected_SNR": true_snr,
        "discovery_claimed": discovery,
        "freqs_GHz": (freqs / 1e9).tolist(),
        "spectrum_W": spectrum.tolist(),
        "baseline_W": baseline.tolist(),
        "disclaimer": (
            "MOCK DATA ONLY. This is a software radiometer simulation, "
            "not a physical measurement. It cannot discover dark matter."
        ),
    }


def write_templates(out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    bench = benchmark_window()
    # Lineshape CSV
    nu = bench["nu_central_Hz"]
    freqs = nu + np.linspace(-5, 5, 2001) * (nu / 1e6)
    shape = axion_lineshape(freqs, nu)
    trap = getattr(np, "trapezoid", None) or np.trapz
    shape /= trap(shape, freqs)
    csv_path = out_dir / "v20_axion_lineshape_37GHz.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["freq_Hz", "freq_GHz", "lineshape_1_per_Hz"])
        for f, s in zip(freqs, shape):
            writer.writerow([f"{f:.6f}", f"{f/1e9:.12f}", f"{s:.12e}"])
    paths.append(str(csv_path))

    # Collaboration brief
    brief = out_dir / "v20_haloscope_target_brief.md"
    brief.write_text(
        f"""# v20 axion target brief for haloscope collaborations

## Benchmark (theory prediction, not a detection)

| Quantity | Value |
|---|---|
| $m_a$ | ${MA_UEV}\\pm{MA_UEV_UNC}$ µeV |
| Frequency | ${bench['nu_central_GHz']:.4f}$ GHz |
| Recommended scan | 36.6 – 37.6 GHz |
| $g_{{a\\gamma\\gamma}}$ | $({G_AGG*1e14:.3f}\\pm{G_AGG_UNC*1e14:.3f})\\times10^{{-14}}$ GeV$^{{-1}}$ |
| $E/N$ | $8/3$ |
| Halo linewidth | ~{bench['linewidth_kHz']:.1f} kHz ($Q\\sim10^6$) |

## Preferred technologies at 37 GHz

1. **MADMAX** (dielectric disk stack) — design mass window includes ~150 µeV.
2. **ALPHA** (plasma / wire metamaterial) — later stages cover 80–200 µeV.
3. **ORGAN** (high-frequency cavity / open resonator) — design envelope includes 15–50 GHz.

Traditional cylindrical cavities are disfavoured: volume scales as $1/\\nu^3$.

## What this repository provides

- Exact frequency / coupling window
- Maxwellian lineshape template CSV
- Dicke radiometer SNR forecast for a MADMAX-like setup
- Mock scan spectrum (software only)

## What this repository does **not** provide

- A real experimental detection
- Beamtime, magnet time, or collaboration membership

Contact the collaborations with this brief and offer to refine signal templates.
""",
        encoding="utf-8",
    )
    paths.append(str(brief))
    return paths


def build_report(seed: int = 20) -> dict:
    bench = benchmark_window()
    forecast = scan_forecast()
    mock_on = mock_scan_spectrum(seed=seed, inject_signal=True)
    mock_off = mock_scan_spectrum(seed=seed, inject_signal=False)
    out_dir = Path(__file__).resolve().parent / "haloscope_37ghz_templates"
    templates = write_templates(out_dir)
    return {
        "status": "haloscope scan forecast complete (software only)",
        "benchmark": bench,
        "forecast": forecast,
        "mock_scan_with_injected_signal": {
            k: mock_on[k]
            for k in (
                "inject_signal",
                "injected",
                "matched_filter_SNR",
                "expected_SNR",
                "discovery_claimed",
                "disclaimer",
            )
        },
        "mock_scan_null": {
            k: mock_off[k]
            for k in (
                "inject_signal",
                "matched_filter_SNR",
                "expected_SNR",
                "discovery_claimed",
                "disclaimer",
            )
        },
        "templates": templates,
        "verdict": (
            "The 36.6–37.6 GHz window is experimentally targetable with "
            "dielectric/plasma haloscopes at the v20 coupling. A software "
            "mock scan is NOT a discovery. Only a real instrument can confirm "
            "or refute the all-DM benchmark."
        ),
    }


def main() -> int:
    report = build_report()
    path = Path(__file__).resolve().parent / "haloscope_scan_37ghz_v20.json"
    # Avoid dumping huge spectrum arrays into the summary json twice
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "nu_GHz": report["benchmark"]["nu_central_GHz"],
                "window_GHz": report["benchmark"]["recommended_scan_GHz"],
                "expected_SNR": report["forecast"]["expected_SNR"],
                "reaches_v20": report["forecast"]["reaches_v20_coupling"],
                "mock_discovery_claimed": report["mock_scan_with_injected_signal"][
                    "discovery_claimed"
                ],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
