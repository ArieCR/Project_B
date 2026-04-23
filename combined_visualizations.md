# Combined Visualizations

A single-page viewer (`combined_visualizations.html`) that embeds all interactive HTML visualizations via iframes, auto-resized to fit their content.

## Visualizations

| # | Title | File |
|---|-------|------|
| Introduction I | Compression Animation | `visualize_Introduction_I_compression_animation.html` |
| Introduction II | OFDM Modulation | `visualize_Introduction_II_OFDM_Modulation.html` |
| 1.5 | OFDM Explorer | `visualize_1_5_ofdm_explorer.html` |
| 2.2 | LTE Bandwidth vs RBs | `visualize_2_2_LTE_bandwidth_vs_rbs.html` |
| 2.3 | LTE Duplexing | `visualize_2_3_lte_duplexing.html` |
| 2.6 | OFDMA Downlink Scheduler | `visualize_2_6_ofdma_downlink_scheduler.html` |
| 2.7 | Different Modulation Schemes | `visualize_2_7_Different_modulation_schemes.html` |
| 3.2 | Transmission Reception Layer | `visualize_3_2_transmission_reception_layer.html` |

## Section notes

**2.3 LTE Duplexing** — Interactive FDD/TDD toggle with an animated time-frequency plot. Shows how LTE separates uplink and downlink via frequency (FDD) or time slots (TDD), with pros/cons for each mode.

**2.6 OFDMA Downlink Scheduler** — Drag-and-drop demo of a simplified 64-tile OFDM grid. Three phones can be repositioned in a cell; the scheduler reallocates data tiles based on channel quality (CQI) and maps modulation schemes (QPSK / 16QAM / 64QAM) to each phone in real time.

## Usage

Open `combined_visualizations.html` directly in a browser. Each iframe loads and auto-resizes on the `load` event. All source files must remain in the same directory.
