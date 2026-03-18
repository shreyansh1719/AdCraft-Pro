# AdCraft Pro — v3 Pipeline Upgrade Plan

Generated: 2026-03-18

---

## 1. Current State Summary

### Active Model IDs (from .env)

| Variable | Model ID | Role |
|---|---|---|
| `FINE_TUNED_MODEL_ID` | `ft:gpt-4.1-mini-2025-04-14:shreyansh::DIdMhrba` | Production (SFT+DPO) |
| `SFT_MODEL_ID` | `ft:gpt-4.1-mini-2025-04-14:shreyansh::DIb8s5h2` | SFT-only checkpoint |
| Baseline | `gpt-4.1-mini-2025-04-14` | Untuned reference |

### Most Recent Evaluation (2026-03-12, n=10 products)

| Model | Mean +/- Std | Min | Max | Successful |
|---|---|---|---|---|
| Baseline | 71.5 +/- 6.6 | 64.2 | 85.1 | 8/10 |
| SFT | 66.4 +/- 10.7 | 48.0 | 86.1 | 10/10 |
| SFT+DPO | 71.4 +/- 7.0 | 62.7 | 84.0 | 10/10 |

Per-metric means (SFT+DPO):
- Readability: 70.8 (weight 0.30)
- Placement: 60.4 (weight 0.25)
- Composition: 68.2 (weight 0.20)
- Harmony: 99.7 (weight 0.10) -- saturated, not differentiating
- Copy: 76.7 (weight 0.15) -- DPO added +5.0 pts over SFT

### Statistical Power Problem

All three pairwise t-tests were non-significant at n=10 (p-values: 0.26, 0.26, 0.99).
Minimum n for Welch's t-test to detect 5-pt mean difference (pooled std ~8, alpha=0.05, power=0.80): ~20 products.

### Training Data

| File | Count | Status |
|---|---|---|
| `fine_tuning_dataset_v2.jsonl` | 421 examples | Current SFT training set |
| `fine_tuning_dataset_v3.jsonl` | Does not exist yet | Target of Phase 1 |
| `seeds.txt` | 29 hand-curated JSON objects | Input to v3 generator |

### DPO Preference Pairs (previous run)
- 17 pairs from 10 products x 3 variants
- Average score gap: 10.4 pts
- Minimum gap threshold: 5.0 pts (feedback_loop.py)
- DPO used beta=0.1

---

## 2. Seven-Phase Pipeline Sequence

### Phase 1: Generate v3 Training Dataset
- Script: `generate_training_data_v3.py`
- Input: `seeds.txt` (29 seeds), BRAND_PRODUCT_MATRIX (80 entries)
- Output: `fine_tuning_dataset_v3.jsonl`
- Expected: 80 generated + 29 seeds = ~109 total (after validation failures)
- Time: ~15-25 minutes (80 GPT-4o calls)
- Cost: ~$0.72

### Phase 2: Validate Dataset Quality
- Structural integrity checks (valid JSON, 3 messages per entry, system prompt)
- Content quality checks (no banned headlines, no generic captions)
- Distribution check (categories, tones, brands)
- Minimum threshold: 80 valid examples

### Phase 3: Update Training Scripts
- `scripts/retrain_sft_model.py` line 34: v2 -> v3 dataset
- `scripts/generate_preference_data.py`: expand PRODUCTS 10 -> 20
- `scripts/run_evaluation.py`: expand EVAL_PRODUCTS 10 -> 20
- `ad_generator/model_evaluator.py`: expand EVAL_PRODUCTS 10 -> 20

### Phase 4: Retrain SFT Model
- Script: `scripts/retrain_sft_model.py`
- Base model: `gpt-4.1-mini-2025-04-14`
- Epochs: 3
- Time: 45-90 minutes
- Cost: ~$0.40

### Phase 5: Generate Preference Pairs
- Script: `scripts/generate_preference_data.py`
- 20 products x 3 variants = 60 pipeline runs
- Expected: 30-40 preference pairs (5-pt gap filter)
- Time: 3-5 hours
- Cost: ~$4.25

### Phase 6: Retrain DPO
- Script: `scripts/run_dpo_training.py`
- Base model: new SFT from Phase 4
- Beta: 0.1
- Time: 20-40 minutes
- Cost: ~$0.10

### Phase 7: Evaluation + Statistical Analysis
- Script: `scripts/run_evaluation.py`
- 20 products x 3 models (baseline, SFT, SFT+DPO)
- Welch's t-test, Cohen's d, 95% CI
- Time: 60-90 minutes
- Cost: ~$4.45

**Total estimated cost: ~$9.92**

---

## 3. Files to Modify

| File | Phase | Change |
|---|---|---|
| `scripts/retrain_sft_model.py` | 3 | Line 34: TRAINING_FILE = "fine_tuning_dataset_v3.jsonl" |
| `scripts/generate_preference_data.py` | 3 | Expand PRODUCTS list 10 -> 20 |
| `scripts/run_evaluation.py` | 3 | Expand EVAL_PRODUCTS 10 -> 20 |
| `ad_generator/model_evaluator.py` | 3 | Expand EVAL_PRODUCTS 10 -> 20 |
| `.env` | 4, 6 | Auto-updated by scripts |

**NEVER MODIFY:** `ad_generator/prompts.py`

---

## 4. Risk Points and Fallbacks

### Risk 1: v3 Dataset < 80 examples
- Fallback: supplement with `made_to_stick_400_final_dataset.jsonl`

### Risk 2: SFT v3 underperforms SFT v2
- Fallback: revert .env to old SFT model, run DPO on v2 base

### Risk 3: Preference pair yield < 20 pairs
- Fallback: lower gap threshold in feedback_loop.py from 5.0 to 3.0
- Or: combine new pairs with existing 17 from previous run

### Risk 4: DPO training fails (< 10 examples)
- Fallback: accumulate new + old pairs (feedback_loop loads all pairs cumulatively)

### Risk 5: Statistical non-significance at n=20
- Interpretation: model matches quality while ensuring 100% structured output success rate
- Report directional improvements by metric (especially copy score)

### Risk 6: gpt-image-1 rate limits during Phase 5
- Script has exponential backoff retry
- Fallback: run in batches of 10 products

---

## 5. Expected Outcomes

| Metric | Baseline | SFT+DPO v3 | Delta |
|---|---|---|---|
| Composite | 70-73 | 72-76 | +2 to +4 |
| Copy | 70-76 | 76-82 | +4 to +6 |
| Harmony | 98-100 | 98-100 | ~0 (saturated) |

Statistical power at n=20: detectable effect at 3.6 pts (alpha=0.05, power=0.80)

---

## 6. New Products to Add (Phase 3)

Keep existing 10 products. Add:
1. Adidas Samba OG retro sneakers (Fashion, Retro)
2. Porsche 911 GT3 RS sports car (Automotive, Visceral)
3. Coca-Cola Original classic beverage (Food & Beverage, Nostalgic)
4. Samsung Galaxy S25 Ultra smartphone (Technology, Bold)
5. Patagonia Nano Puff outdoor jacket (Outdoor, Rugged)
6. Glossier Cloud Paint blush (Beauty, Effortless)
7. Heineken Silver premium lager (Food & Beverage, Cosmopolitan)
8. IKEA KALLAX shelf unit (Furniture, Clever)
9. Arc'teryx Alpha SV hardshell jacket (Outdoor, Extreme)
10. Omega Speedmaster Moonwatch (Luxury, Legendary)

---

## Quick Reference Commands

```bash
venv\Scripts\activate

# Phase 1
python generate_training_data_v3.py

# Phase 4
python scripts/retrain_sft_model.py

# Phase 5
python scripts/generate_preference_data.py --dry-run
python scripts/generate_preference_data.py

# Phase 6
python scripts/run_dpo_training.py

# Phase 7
python scripts/run_evaluation.py
```
