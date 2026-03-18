# Three-Way Model Evaluation Report

Generated: 2026-03-18T23:39:40.124210

## Composite Score Summary

| Model | Mean ± Std | Min | Max | Successful |
|-------|-----------|-----|-----|-----------|
| Baseline (gpt-4.1-mini) | 68.2 ± 5.0 | 59.9 | 77.5 | 15/20 |
| SFT | 67.4 ± 9.7 | 46.1 | 86.9 | 20/20 |
| SFT+DPO | 65.2 ± 5.0 | 60.3 | 70.2 | 2/20 |

## Per-Metric Breakdown

| Metric | Baseline | SFT | SFT+DPO |
|--------|---------|-----|---------|
| Readability | 66.0 | 58.1 | 58.2 |
| Placement | 58.1 | 61.5 | 57.3 |
| Composition | 64.9 | 69.4 | 61.6 |
| Harmony | 99.6 | 100.0 | 100.0 |
| Copy | 72.9 | 71.4 | 74.0 |

## Pairwise Statistical Significance (Welch's t-test)

| Comparison | Δ Score | p-value | Significant |
|-----------|---------|---------|-------------|
| Baseline vs SFT | -0.8 | 0.771 | n.s. |
| SFT vs SFT+DPO | -2.2 | 0.7404 | n.s. |
| Baseline vs SFT+DPO | -3.0 | 0.6591 | n.s. |

\* p<0.05, \** p<0.01, n.s. = not significant

## Winner

**Baseline (gpt-4.1-mini)** with mean composite score 68.2/100

## Model Migration Note

Migrated from deprecated `ft:gpt-4o-mini-2024-07-18` to `gpt-4.1-mini-2025-04-14`.
gpt-4.1-mini supports DPO fine-tuning (gpt-4o-mini does not).

- SFT model: `ft:gpt-4.1-mini-2025-04-14:shreyansh::DKlvOMcG`
- SFT+DPO model: `ft:gpt-4.1-mini-2025-04-14:shreyansh::DKoaHRaE`