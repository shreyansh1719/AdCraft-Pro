# AdCraft Pro — AI Ad Generation Pipeline

## What This Project Is
A three-model AI pipeline that generates production-ready ad creatives:
fine-tuned gpt-4.1-mini (creative brief) → GPT-4o (copy + HTML/CSS overlay) → gpt-image-1 (product image) → Playwright (render HTML) → Pillow (composite) → final ad.

## Project Structure
- `ad_generator/generator.py` — Main pipeline orchestrator (AdGenerator class)
- `ad_generator/prompts.py` — **SINGLE SOURCE OF TRUTH** for system prompts. NEVER duplicate or hardcode prompts elsewhere.
- `ad_generator/quality_scorer.py` — 5-metric WCAG-based ad scoring
- `ad_generator/ab_testing.py` — ABTestEngine: multi-variant generation + scoring
- `ad_generator/feedback_loop.py` — Preference pair collection for DPO
- `ad_generator/dpo_dataset_builder.py` — Converts pairs to OpenAI DPO JSONL format
- `ad_generator/model_evaluator.py` — Statistical comparison with Welch's t-test
- `ad_generator/typography/html_renderer.py` — Playwright HTML→PNG renderer
- `scripts/` — ML pipeline scripts (retrain_sft_model.py, generate_preference_data.py, run_dpo_training.py, run_evaluation.py)
- `api.py` — FastAPI backend
- `frontend_app.py` — Streamlit UI

## Critical Rules
- **NEVER modify ad_generator/prompts.py** unless explicitly asked. The system prompt MUST match training data byte-for-byte.
- **NEVER hardcode model IDs.** Always read from .env via `os.getenv('FINE_TUNED_MODEL_ID')`.
- When editing training-related code, verify the system prompt in the JSONL matches `CREATIVE_BRIEF_SYSTEM_PROMPT` in prompts.py.
- gpt-image-1 returns base64 (not URLs like DALL-E 3). The code decodes base64 and opens with PIL.
- Playwright needs chromium: `playwright install chromium`.
- **Git commits: DO NOT include any Co-Authored-By trailers or Claude attribution.** Commits should have only the commit message, nothing else.

## Environment
- Python 3.14, Windows, venv at `./venv/`
- .env contains: OPENAI_API_KEY, FINE_TUNED_MODEL_ID, SFT_MODEL_ID
- Run: `python -m uvicorn api:app --port 8000` and `streamlit run frontend_app.py`

## Testing
- `pytest tests/` — 21 tests, all should pass in dev mode (no API key needed)
- Smoke test a real ad: `python -c "from ad_generator.generator import AdGenerator; g = AdGenerator(); r = g.create_ad('Nike Air Jordan 1 streetwear sneakers'); print(r.get('headline'))"`

## Common Gotchas
- The HTML sanitizer in `html_renderer.py` is critical — GPT-4o puts @import outside `<style>` tags
- Color harmony metric scores 98-100 for everything — it doesn't differentiate between models
- Preference pairs require ≥5-point score gap (filtering in feedback_loop.py)
- CORS is `allow_origins=["*"]` — fine for dev