"""
validate_v3_dataset.py — Deep quality validation for fine_tuning_dataset_v3.jsonl
"""

import json
import re
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATASET_FILE = "fine_tuning_dataset_v3.jsonl"

BANNED_HEADLINE_STARTERS = [
    "Discover", "Experience", "Elevate", "Unleash", "Unlock",
    "Redefine", "Embrace", "Transform",
]
BANNED_HEADLINE_PHRASES = [
    "The Future of", "Beyond Ordinary", "Where X Meets Y", "Next-Level",
]
BANNED_CAPTION_PHRASES = [
    "product displayed on", "gradient background", "sleek product photography",
    "the product sits",
]
REQUIRED_FIELDS = [
    "headline", "caption", "tone", "visual_style", "conceptual_technique",
    "call_to_action", "emotion", "typography_style", "color_scheme",
]

CATEGORY_KEYWORDS = {
    "Tech": ["apple", "samsung", "sony", "google", "bose", "nintendo", "steam", "dji",
             "dyson", "adobe", "spotify", "notion", "calm", "duolingo", "masterclass",
             "razer", "beats", "bang", "leica", "gopro", "ring", "kindle", "instant pot"],
    "Luxury": ["rolex", "omega", "hermes", "gucci", "chanel", "tom ford", "la mer",
               "aston martin", "bvlgari", "montblanc", "loewe", "rimowa", "diptyque",
               "victorinox"],
    "Fashion": ["nike", "adidas", "new balance", "lululemon", "zara", "patagonia",
                "allbirds", "crocs", "uniqlo", "fjallraven", "warby parker", "away"],
    "Food/Bev": ["coca-cola", "oatly", "nespresso", "heineken", "tabasco", "godiva",
                 "haagen-dazs", "starbucks", "red bull", "liquid death"],
    "Auto": ["tesla", "porsche", "jeep", "bmw", "rivian", "mercedes", "aston martin"],
    "Beauty": ["glossier", "fenty", "dove", "aesop", "olaplex"],
    "Home": ["ikea", "muji", "sonos", "le creuset", "yeti", "stanley", "zwilling",
             "casper", "weber"],
    "Sport/Outdoor": ["peloton", "theragun", "brompton", "arc'teryx", "gopro"],
    "Other": ["lego", "marshall", "moleskine", "national geographic", "airbnb"],
}


def load_dataset(path):
    lines = []
    errors = []
    with open(path, encoding="utf-8") as f:
        for i, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append((i, json.loads(raw)))
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: invalid JSON — {e}")
    return lines, errors


def word_overlap(a, b):
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def detect_category(brand_product_text):
    t = brand_product_text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return cat
    return "Other"


def main():
    print("=" * 60)
    print(f"Validating: {DATASET_FILE}")
    print("=" * 60)

    # ── Load ──────────────────────────────────────────────────────
    lines, json_errors = load_dataset(DATASET_FILE)
    print(f"\n[1] STRUCTURAL INTEGRITY")
    print(f"  Total lines loaded: {len(lines)}")
    if json_errors:
        for e in json_errors:
            print(f"  ERROR: {e}")
    else:
        print(f"  [OK] All lines are valid JSON")

    system_prompts = set()
    structural_errors = []
    entries = []

    for lineno, obj in lines:
        msgs = obj.get("messages", [])
        if len(msgs) != 3:
            structural_errors.append(f"Line {lineno}: expected 3 messages, got {len(msgs)}")
            continue
        roles = [m.get("role") for m in msgs]
        if roles != ["system", "user", "assistant"]:
            structural_errors.append(f"Line {lineno}: wrong roles {roles}")
            continue
        system_prompts.add(msgs[0]["content"])

        # Check assistant is valid JSON
        try:
            brief = json.loads(msgs[2]["content"])
        except json.JSONDecodeError as e:
            structural_errors.append(f"Line {lineno}: assistant content is not valid JSON — {e}")
            continue

        entries.append({
            "lineno": lineno,
            "system": msgs[0]["content"],
            "user": msgs[1]["content"],
            "brief": brief,
        })

    if structural_errors:
        print(f"\n  STRUCTURAL ERRORS ({len(structural_errors)}):")
        for e in structural_errors:
            print(f"    {e}")
    else:
        print(f"  [OK] All entries have correct 3-message structure with correct roles")

    print(f"  Unique system prompts: {len(system_prompts)}")
    if len(system_prompts) == 1:
        print(f"  [OK] System prompt is consistent")
    else:
        print(f"  ERROR: Multiple system prompts found!")
        for i, sp in enumerate(system_prompts):
            print(f"    Prompt {i+1}: {sp[:80]}...")

    # Cross-check system prompt against prompts.py
    try:
        from ad_generator.prompts import CREATIVE_BRIEF_SYSTEM_PROMPT
        actual = list(system_prompts)[0] if system_prompts else ""
        if actual == CREATIVE_BRIEF_SYSTEM_PROMPT:
            print(f"  [OK] System prompt matches prompts.py byte-for-byte")
        else:
            print(f"  ERROR: System prompt does NOT match prompts.py!")
            print(f"    Dataset:   {repr(actual[:100])}")
            print(f"    prompts.py:{repr(CREATIVE_BRIEF_SYSTEM_PROMPT[:100])}")
    except ImportError as e:
        print(f"  WARN: Could not import prompts.py to cross-check: {e}")

    # ── Content Quality ───────────────────────────────────────────
    print(f"\n[2] CONTENT QUALITY ({len(entries)} valid entries)")

    missing_fields = []
    empty_fields = []
    banned_headlines = []
    short_captions = []
    thin_tones = []
    headlines = []
    captions = []
    banned_caption_hits = []

    for e in entries:
        b = e["brief"]
        ln = e["lineno"]

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in b:
                missing_fields.append(f"Line {ln}: missing field '{field}'")
            elif not str(b[field]).strip():
                empty_fields.append(f"Line {ln}: empty field '{field}'")

        headline = str(b.get("headline", ""))
        caption = str(b.get("caption", ""))
        tone = str(b.get("tone", ""))

        headlines.append((ln, headline))
        captions.append((ln, caption))

        # Banned starters
        for starter in BANNED_HEADLINE_STARTERS:
            if headline.startswith(starter):
                banned_headlines.append(f"Line {ln}: headline starts with '{starter}': \"{headline}\"")

        # Banned phrases in headline
        for phrase in BANNED_HEADLINE_PHRASES:
            if phrase.lower() in headline.lower():
                banned_headlines.append(f"Line {ln}: headline contains banned phrase '{phrase}': \"{headline}\"")

        # Banned caption phrases
        for phrase in BANNED_CAPTION_PHRASES:
            if phrase.lower() in caption.lower():
                banned_caption_hits.append(f"Line {ln}: caption contains '{phrase}': \"{caption[:80]}\"")

        # Caption length
        if len(caption) < 40:
            short_captions.append(f"Line {ln}: caption too short ({len(caption)} chars): \"{caption}\"")

        # Tone descriptors
        if "," not in tone:
            thin_tones.append(f"Line {ln}: tone has only 1 descriptor: \"{tone}\"")

    def report_issues(label, issues, critical=True):
        if issues:
            tag = "ERROR" if critical else "WARN"
            print(f"  {tag}: {label} ({len(issues)} issues):")
            for issue in issues[:10]:
                print(f"    {issue}")
            if len(issues) > 10:
                print(f"    ... and {len(issues) - 10} more")
        else:
            print(f"  [OK] {label}")

    report_issues("Missing required fields", missing_fields)
    report_issues("Empty required fields", empty_fields)
    report_issues("Generic/banned headlines", banned_headlines)
    report_issues("Banned caption phrases", banned_caption_hits)
    report_issues("Short captions (<40 chars)", short_captions)
    report_issues("Thin tone descriptors (no comma)", thin_tones, critical=False)

    # Duplicate headlines
    headline_texts = [h[1] for h in headlines]
    dup_headlines = [h for h, c in Counter(headline_texts).items() if c > 1]
    if dup_headlines:
        print(f"  ERROR: Duplicate headlines ({len(dup_headlines)}):")
        for d in dup_headlines:
            print(f"    \"{d}\"")
    else:
        print(f"  [OK] No duplicate headlines ({len(set(headline_texts))} unique)")

    # Near-duplicate captions (>80% word overlap)
    near_dups = []
    cap_list = [(ln, cap) for ln, cap in captions]
    for i in range(len(cap_list)):
        for j in range(i + 1, len(cap_list)):
            ov = word_overlap(cap_list[i][1], cap_list[j][1])
            if ov > 0.8:
                near_dups.append(
                    f"Lines {cap_list[i][0]} & {cap_list[j][0]}: {ov:.0%} overlap\n"
                    f"      A: \"{cap_list[i][1][:70]}\"\n"
                    f"      B: \"{cap_list[j][1][:70]}\""
                )
    if near_dups:
        print(f"  WARN: Near-duplicate captions (>80% word overlap) — {len(near_dups)} pairs:")
        for nd in near_dups[:5]:
            print(f"    {nd}")
    else:
        print(f"  [OK] No near-duplicate captions")

    # ── Distribution ──────────────────────────────────────────────
    print(f"\n[3] DISTRIBUTION CHECK")

    # Category distribution
    categories = Counter()
    brand_counts = Counter()
    for e in entries:
        user_msg = e["user"]
        # Extract brand from user message "Brand: X"
        m = re.search(r"Brand:\s*(.+)", user_msg)
        brand = m.group(1).strip() if m else "Unknown"
        brand_counts[brand] += 1
        cat = detect_category(user_msg)
        categories[cat] += 1

    print(f"  Category distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        flag = " <-- LOW" if count < 5 else ""
        print(f"    {cat:<20} {count}{flag}")

    # Brands appearing > 3 times
    over_repr = [(b, c) for b, c in brand_counts.items() if c > 3]
    if over_repr:
        print(f"\n  WARN: Brands appearing >3 times:")
        for b, c in sorted(over_repr, key=lambda x: -x[1]):
            print(f"    {b}: {c}")
    else:
        print(f"\n  [OK] No brand appears more than 3 times")

    # Top 10 tone words
    tone_words = Counter()
    for e in entries:
        tone = str(e["brief"].get("tone", "")).lower()
        for word in re.split(r"[,\s]+", tone):
            word = word.strip()
            if word:
                tone_words[word] += 1
    print(f"\n  Top 10 tone words:")
    for word, count in tone_words.most_common(10):
        print(f"    {word:<20} {count}")

    # ── Summary ───────────────────────────────────────────────────
    all_errors = (
        json_errors + structural_errors + missing_fields + empty_fields
        + banned_headlines + banned_caption_hits + short_captions + dup_headlines
    )
    print(f"\n{'=' * 60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Valid entries:     {len(entries)}")
    print(f"  Critical errors:   {len(all_errors)}")
    print(f"  Warnings:          {len(near_dups) + len(thin_tones) + len(over_repr)}")
    if len(entries) >= 100:
        print(f"  [OK] Dataset meets minimum threshold (100 examples)")
    else:
        print(f"  ERROR: Dataset below minimum threshold (need 100, have {len(entries)})")

    if all_errors:
        print(f"\n  Action required: fix {len(all_errors)} critical errors before training")
        return 1
    else:
        print(f"\n  Dataset is ready for SFT training")
        return 0


if __name__ == "__main__":
    sys.exit(main())
