# AdCraft Pro CBQA Evaluation Report

Generated: 2026-03-19 02:47

---

## 1. Executive Summary

CBQA evaluated creative briefs from 3 models across 25 products using a 7-dimension, 18-sub-metric rubric (180 points). Baseline (gpt-4.1-mini, untuned) scored 73.2/100 (+/- 6.4). SFT+DPO v3 scored 73.6/100 (+/- 4.2), a difference of +0.4 pts (p=0.818, Cohen's d=0.065). CBQA measures only the fine-tuned model's direct output quality, isolating it from downstream image generation and HTML rendering confounds.

## 2. Methodology

- **Pointwise Rubric**: 7 dimensions, 18 sub-metrics, 180 max raw points normalized to 0-100
- **LLM-as-Judge**: GPT-4o with G-Eval chain-of-thought reasoning before scoring (temperature=0)
- **Pairwise Evaluation**: 3 model pairs x 25 products x 2 position swaps = 150 comparisons
- **Bias Mitigation**: Each comparison run twice with positions swapped; inconsistent results marked unstable
- **Reliability Check**: 15 random briefs re-scored; Pearson r and MAD computed
- **Models**: Baseline (gpt-4.1-mini), SFT v3 (ft:DKlvOMcG), SFT+DPO v3 (ft:DKoaHRaE)

## 3. Pointwise Results

### Overall Composite Score

| Model | Mean +/- Std | Median | Min | Max | Grade |
|-------|--------------|--------|-----|-----|-------|
| Baseline | 73.2 +/- 6.4 | 73.3 | 60.6 | 82.8 | B |
| SFT v3 | 74.1 +/- 4.4 | 73.3 | 67.2 | 82.8 | B |
| SFT+DPO v3 | 73.6 +/- 4.2 | 73.3 | 65.0 | 82.2 | B |

### Per-Dimension Breakdown

| Dimension | Weight | Baseline | SFT v3 | SFT+DPO v3 | B vs DPO |
|-----------|--------|----------|--------|------------|---------|
| Headline | 20% | 63.2 | 68.7 | 69.7 | +6.5 |
| Caption | 20% | 85.8 | 82.0 | 81.1 | -4.7 |
| Strategy | 15% | 75.1 | 74.0 | 74.7 | -0.4 |
| Tone | 10% | 89.0 | 88.0 | 87.0 | -2.0 |
| Visual Style | 10% | 53.6 | 41.8 | 38.4 | -15.2 |
| Cta | 5% | 86.0 | 91.2 | 92.0 | +6.0 |
| Production | 10% | 62.8 | 79.0 | 77.2 | +14.4 |

### Statistical Significance (Welch's t-test)

| Comparison | Delta | t-stat | p-value | 95% CI | Cohen's d | Sig |
|-----------|-------|--------|---------|--------|-----------|-----|
| Baseline vs SFT | +0.87 | -0.555 | 0.5817 | (-2.2, 3.9) | 0.157 | n.s. |
| SFT vs SFT+DPO | -0.51 | 0.423 | 0.6743 | (-2.9, 1.9) | -0.120 | n.s. |
| Baseline vs SFT+DPO | +0.35 | -0.231 | 0.8181 | (-2.6, 3.4) | 0.065 | n.s. |

## 4. Pairwise Results

### Overall Win Rates

#### BASELINE vs DPO

| Dimension | A Wins | B Wins | Ties | Unstable | B Win Rate | p-value | Sig |
|-----------|--------|--------|------|----------|------------|---------|-----|
| Headline | 20 | 0 | 0 | 5 | 0.0% | 1.0000 | n.s. |
| Visual Concept | 5 | 11 | 0 | 9 | 68.8% | 0.1051 | n.s. |
| Strategic Thinking | 25 | 0 | 0 | 0 | 0.0% | 1.0000 | n.s. |
| Brand Alignment | 22 | 1 | 2 | 0 | 8.0% | 1.0000 | n.s. |
| Overall | 25 | 0 | 0 | 0 | 0.0% | 1.0000 | n.s. |

#### BASELINE vs SFT

| Dimension | A Wins | B Wins | Ties | Unstable | B Win Rate | p-value | Sig |
|-----------|--------|--------|------|----------|------------|---------|-----|
| Headline | 23 | 0 | 0 | 2 | 0.0% | 1.0000 | n.s. |
| Visual Concept | 7 | 11 | 0 | 7 | 61.1% | 0.2403 | n.s. |
| Strategic Thinking | 25 | 0 | 0 | 0 | 0.0% | 1.0000 | n.s. |
| Brand Alignment | 22 | 0 | 3 | 0 | 6.0% | 1.0000 | n.s. |
| Overall | 24 | 0 | 0 | 1 | 0.0% | 1.0000 | n.s. |

#### SFT vs DPO

| Dimension | A Wins | B Wins | Ties | Unstable | B Win Rate | p-value | Sig |
|-----------|--------|--------|------|----------|------------|---------|-----|
| Headline | 8 | 4 | 2 | 11 | 35.7% | 0.9713 | n.s. |
| Visual Concept | 8 | 7 | 1 | 9 | 46.9% | 0.7728 | n.s. |
| Strategic Thinking | 2 | 2 | 21 | 0 | 50.0% | 1.0000 | n.s. |
| Brand Alignment | 2 | 6 | 8 | 9 | 62.5% | 0.8949 | n.s. |
| Overall | 6 | 5 | 0 | 14 | 45.5% | 0.7256 | n.s. |

## 5. Reliability Metrics

- **n pairs**: 15
- **Pearson r**: 0.748 (>0.8 = high reliability)
- **p-value**: 0.0013
- **Mean Absolute Deviation**: 3.0 points
- **Run 1 mean**: 73.0 | **Run 2 mean**: 73.0

## 6. Key Findings

1. **Strongest improvement from fine-tuning**: Production (+14.4 pts normalized)
2. **Least improvement**: Visual Style (-15.2 pts normalized)
3. **SFT vs Baseline**: +0.9 pts
4. **DPO over SFT**: -0.5 pts
5. **Overall DPO vs Baseline**: +0.4 pts (p=0.818)

### Comparison with Previous Evaluation (Composite Scoring)

The previous evaluation (v2 dataset, n=10 products) measured:
- Readability (WCAG contrast) — controlled by GPT-4o, not the fine-tuned model
- Text placement accuracy — controlled by HTML/CSS renderer
- Color harmony — controlled by GPT-4o
- Composition — controlled by image generation

**80% of the previous score measured downstream pipeline factors the fine-tuned model does not control.**

CBQA measures only the 9-field creative brief output directly. This isolates whether fine-tuning
actually improves strategic thinking, headline quality, and visual direction.

## 7. Per-Product Results

| Product | Baseline | SFT v3 | SFT+DPO | Best Headline (DPO) |
|---------|----------|--------|---------|---------------------|
| Glossier Cloud Paint blush | 70.6 | 69.4 | 82.2 | Blush Rush: Swipe, Smile, Repeat |
| Marshall Stanmore III speaker | 81.7 | 79.4 | 81.1 | AMPLIFY YOUR LEGACY |
| Adidas Samba OG retro sneakers | 78.9 | 73.9 | 77.8 | STEP INTO HISTORY. |
| Levi's 501 Original jeans | 78.9 | 79.4 | 77.8 | Buttoned Up Since '46 |
| Nike Air Jordan 1 streetwear sneake | 79.4 | 81.1 | 77.2 | LACE UP LEGENDS |
| Omega Speedmaster Moonwatch | 81.7 | 78.9 | 77.2 | Time Flies Beyond the Stratosphere |
| Coca-Cola Original classic beverage | 74.4 | 78.9 | 76.1 | Pop the Happiness |
| Beats Studio Pro headphones | 70.6 | 73.3 | 75.6 | Dial Up Your Soundscape |
| Apple AirPods Pro wireless earbuds | 70.6 | 71.7 | 75.0 | Soundtrack of Your Silence |
| Heineken Silver premium lager | 73.9 | 73.3 | 74.4 | Sip into the Silver Lining |
| Patagonia Nano Puff outdoor jacket | 72.2 | 72.8 | 74.4 | Puff, Don't Fluff: The Eco-Warrior's Warm Hug |
| Tesla Model S electric sedan | 63.9 | 70.6 | 73.9 | Drive the Future, Silently. |
| Nespresso Vertuo coffee machine | 62.8 | 68.9 | 73.3 | Brewed to Perfection, Vertically. |
| Rolex Submariner luxury dive watch | 82.8 | 82.8 | 73.3 | Time to Dive into Legacy |
| Godiva Dark Chocolate Truffles | 68.3 | 71.7 | 72.8 | A Moment of Pure Temptation |
| IKEA KALLAX shelf unit | 60.6 | 73.3 | 72.8 | SHELVES OF POSSIBILITIES |
| Arc'teryx Alpha SV hardshell jacket | 73.3 | 80.6 | 71.7 | Shell of a Different Weather |
| Sony PlayStation 5 Pro gaming conso | 72.2 | 76.1 | 71.1 | Level Up Reality |
| Dyson Airwrap hair styling tool | 76.7 | 70.0 | 70.6 | Style in the Air |
| Porsche 911 GT3 RS sports car | 67.8 | 75.0 | 70.6 | Unleash the Track Within. |
| Samsung Galaxy S25 Ultra smartphone | 62.8 | 73.3 | 70.6 | Pixel Perfect Evolution |
| Rimowa Original Cabin suitcase | 71.7 | 67.2 | 70.0 | Rimowa Original Cabin |
| Oatly oat milk dairy alternative | 81.7 | 70.6 | 69.4 | Oat of This World! |
| Aesop Resurrection hand wash | 75.0 | 69.4 | 65.6 | Hands Down, The Best Part of Your Day |
| Chanel No. 5 perfume fragrance | 78.3 | 70.6 | 65.0 | I AM WHAT I AM |