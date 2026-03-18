"""
AdCraft Pro — High-Quality Training Dataset Generator (v3)

Takes 29 hand-curated seed examples of real ad creative briefs and uses
GPT-4o to generate ~120 new examples at the same quality bar.

Strategy:
  1. Parse seed examples from the input file
  2. Define a diverse brand × category matrix (80+ brand/product combos)
  3. For each combo, pick 3 random seeds as few-shot examples
  4. Ask GPT-4o to generate a brief at the same quality bar
  5. Validate: all 9 fields present, headline isn't generic, caption describes a scene
  6. Format as OpenAI fine-tuning JSONL (system/user/assistant messages)
  7. Merge with the ~20 good examples from the original dataset

Output: fine_tuning_dataset_v3.jsonl — ready for SFT training

Usage:
    pip install openai python-dotenv
    python generate_training_data_v3.py

Cost estimate: ~$0.40–0.60 for 120 examples with GPT-4o
"""

import json
import os
import random
import re
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Must match ad_generator/prompts.py EXACTLY
CREATIVE_BRIEF_SYSTEM_PROMPT = (
    "You are an expert advertising creative director. Given a brand and product, "
    "generate a complete ad creative brief including copy and visual direction. "
    "Respond only in JSON."
)

REQUIRED_FIELDS = [
    "headline", "caption", "tone", "visual_style",
    "conceptual_technique", "call_to_action", "emotion",
    "typography_style", "color_scheme",
]

OUTPUT_FILE = "fine_tuning_dataset_v3.jsonl"
GENERATION_MODEL = "gpt-4o"  # Used to GENERATE the training data (not the model being trained)

# ---------------------------------------------------------------------------
# Brand × Product matrix — diverse industries & categories
# ---------------------------------------------------------------------------

BRAND_PRODUCT_MATRIX = [
    # Technology
    ("Apple", "MacBook Air M4", "Technology", "premium", "minimalist"),
    ("Samsung", "Galaxy Z Fold 6", "Technology", "innovative", "futuristic"),
    ("Sony", "WH-1000XM6 headphones", "Technology", "immersive", "sleek studio"),
    ("Google", "Pixel 9 Pro", "Technology", "friendly", "clean and colorful"),
    ("Bose", "QuietComfort Ultra earbuds", "Technology", "serene", "atmospheric"),
    ("Nintendo", "Switch 2", "Gaming", "playful", "vibrant cartoon"),
    ("Steam Deck", "OLED handheld gaming PC", "Gaming", "bold", "neon-lit"),
    ("DJI", "Mini 4 Pro drone", "Technology", "adventurous", "aerial cinematic"),
    ("Dyson", "V15 Detect vacuum", "Home Appliances", "scientific", "clinical precision"),
    ("Dyson", "Supersonic hair dryer", "Beauty Tech", "empowering", "luxurious tech"),

    # Fashion & Luxury
    ("Rolex", "Submariner Date", "Luxury Watches", "prestigious", "dramatic lighting"),
    ("Omega", "Speedmaster Moonwatch", "Luxury Watches", "legendary", "cosmic noir"),
    ("Hermès", "Birkin 25", "Luxury Fashion", "exclusive", "editorial tableau"),
    ("Gucci", "Bamboo 1947 bag", "Luxury Fashion", "eclectic", "maximalist renaissance"),
    ("Nike", "Air Max Dn", "Streetwear", "bold", "kinetic urban"),
    ("Adidas", "Samba OG", "Streetwear", "retro", "vintage film grain"),
    ("New Balance", "550 sneakers", "Streetwear", "understated", "muted lifestyle"),
    ("Patagonia", "Nano Puff jacket", "Outdoor", "rugged", "nature documentary"),
    ("Lululemon", "Align leggings", "Activewear", "mindful", "soft-focus wellness"),
    ("Zara", "linen blazer", "Fast Fashion", "editorial", "high-fashion photography"),

    # Food & Beverage
    ("Coca-Cola", "Original", "Beverages", "nostalgic", "iconic Americana"),
    ("Oatly", "Oat Milk Barista Edition", "Beverages", "irreverent", "hand-drawn illustration"),
    ("Nespresso", "Vertuo Next", "Coffee", "sophisticated", "dark luxe studio"),
    ("Heineken", "Silver lager", "Beer", "cosmopolitan", "nightlife photography"),
    ("Tabasco", "Original Red Sauce", "Condiments", "fiery", "explosive macro"),
    ("Godiva", "Dark Chocolate Truffles", "Confectionery", "indulgent", "rich chiaroscuro"),
    ("Liquid Death", "Mountain Water", "Beverages", "rebellious", "heavy metal artwork"),
    ("Häagen-Dazs", "Vanilla Bean ice cream", "Ice Cream", "luxurious", "sensual macro"),
    ("Starbucks", "Pumpkin Spice Latte", "Coffee", "cozy", "warm autumn aesthetic"),
    ("Red Bull", "Energy Drink", "Energy", "extreme", "action sports composite"),

    # Automotive
    ("Tesla", "Model S Plaid", "Automotive", "futuristic", "sleek CGI render"),
    ("Porsche", "911 GT3 RS", "Automotive", "visceral", "high-speed photography"),
    ("Jeep", "Wrangler Rubicon", "Automotive", "rugged", "epic landscape"),
    ("BMW", "i5 M60", "Automotive", "dynamic", "moody studio"),
    ("Rivian", "R1S SUV", "Automotive", "adventurous", "golden hour wilderness"),
    ("Mercedes-Benz", "EQS sedan", "Automotive", "opulent", "architectural noir"),

    # Beauty & Personal Care
    ("Glossier", "Cloud Paint blush", "Beauty", "effortless", "dewy soft-focus"),
    ("Fenty Beauty", "Pro Filt'r Foundation", "Beauty", "inclusive", "bold editorial"),
    ("Chanel", "N°5 perfume", "Fragrance", "timeless", "cinematic black and white"),
    ("Tom Ford", "Oud Wood cologne", "Fragrance", "seductive", "dark amber moody"),
    ("Dove", "Body Wash", "Personal Care", "real", "natural light lifestyle"),
    ("Aesop", "Resurrection hand wash", "Skincare", "architectural", "brutalist minimalism"),
    ("La Mer", "Crème de la Mer", "Skincare", "mythical", "oceanic depth"),
    ("Olaplex", "No.3 Hair Perfector", "Haircare", "scientific", "lab-meets-luxury"),

    # Home & Lifestyle
    ("IKEA", "KALLAX shelf unit", "Furniture", "clever", "Scandinavian bright"),
    ("Muji", "Aroma Diffuser", "Lifestyle", "zen", "Japanese minimalism"),
    ("Sonos", "Era 300 speaker", "Audio", "immersive", "spatial sound visualization"),
    ("Dyson", "Purifier Big Quiet", "Home Appliances", "clean", "clinical white-space"),
    ("Le Creuset", "Dutch Oven", "Cookware", "heritage", "rustic French kitchen"),
    ("Yeti", "Rambler tumbler", "Outdoor Gear", "indestructible", "adventure proof"),
    ("Peloton", "Bike+", "Fitness", "motivating", "high-energy studio"),
    ("Theragun", "PRO Plus", "Wellness", "powerful", "athletic performance"),

    # Miscellaneous / Services
    ("Spotify", "Premium", "Music Streaming", "vibrant", "abstract data art"),
    ("Airbnb", "Unique Stays", "Travel", "wanderlust", "dreamy editorial"),
    ("Duolingo", "Language Learning App", "Education", "fun", "playful illustration"),
    ("Adobe", "Creative Cloud", "Software", "creative", "digital collage"),
    ("Notion", "Workspace", "Productivity", "minimal", "structured elegance"),
    ("Masterclass", "Online Learning", "Education", "aspirational", "cinematic portrait"),
    ("Calm", "Meditation App", "Wellness", "peaceful", "gradient nature"),
    ("National Geographic", "Magazine Subscription", "Media", "awe-inspiring", "photojournalistic"),

    # Extra variety — less common categories
    ("Lego", "Botanical Collection", "Toys", "creative", "colorful macro"),
    ("Marshall", "Stanmore III speaker", "Audio", "rock & roll", "vintage amplifier aesthetic"),
    ("Brompton", "C Line folding bicycle", "Cycling", "clever", "urban commute"),
    ("Moleskine", "Classic Notebook", "Stationery", "intellectual", "warm still life"),
    ("Bang & Olufsen", "Beoplay H100 headphones", "Audio", "sculptural", "gallery display"),
    ("Victorinox", "Swiss Army Knife", "Tools", "versatile", "clean product array"),
    ("Fjällräven", "Kånken backpack", "Outdoor", "cheerful", "bright Scandinavian"),
    ("GoPro", "HERO13 Black", "Camera", "adventurous", "first-person action"),
    ("Rimowa", "Original Cabin suitcase", "Travel", "iconic", "aluminum geometric"),
    ("Loewe", "Puzzle bag", "Luxury Fashion", "artistic", "surrealist still life"),

    # Additional for reaching 120+
    ("Allbirds", "Tree Dasher 2 running shoes", "Sustainable Fashion", "natural", "earthy studio"),
    ("Away", "The Carry-On suitcase", "Travel", "modern", "flat-lay packing"),
    ("Warby Parker", "prescription glasses", "Eyewear", "approachable", "bright portrait"),
    ("Casper", "Original Mattress", "Sleep", "dreamy", "cloud-soft surrealism"),
    ("Ring", "Video Doorbell Pro 2", "Smart Home", "protective", "split-screen day/night"),
    ("Instant Pot", "Duo Plus pressure cooker", "Kitchen", "efficient", "steamy food photography"),
    ("Crocs", "Classic Clog", "Footwear", "unapologetic", "pop art maximalist"),
    ("Stanley", "Quencher tumbler", "Drinkware", "trendy", "lifestyle flat-lay"),
    ("Kindle", "Paperwhite Signature Edition", "Electronics", "bookish", "cozy reading nook"),
    ("Uniqlo", "Ultra Light Down jacket", "Fashion", "practical", "clean Japanese minimal"),
    ("Zwilling", "Pro chef knife", "Kitchenware", "precise", "dramatic culinary"),
    ("Aston Martin", "DB12", "Automotive", "refined", "cinematic grand tourer"),
    ("Bvlgari", "Serpenti Viper necklace", "Jewelry", "mesmerizing", "serpentine art nouveau"),
    ("Montblanc", "Meisterstück fountain pen", "Luxury Goods", "distinguished", "executive portrait"),
    ("Leica", "Q3 camera", "Photography", "purist", "documentary grain"),
    ("Razer", "Blade 18 gaming laptop", "Gaming", "aggressive", "RGB neon cyberpunk"),
    ("Arc'teryx", "Alpha SV jacket", "Outdoor", "extreme", "alpine storm"),
    ("Beats", "Studio Pro headphones", "Audio", "streetwise", "bold color blocking"),
    ("Diptyque", "Baies candle", "Home Fragrance", "refined", "Parisian still life"),
    ("Weber", "Spirit II gas grill", "Outdoor Cooking", "convivial", "backyard golden hour"),
]


# ---------------------------------------------------------------------------
# GPT-4o generation prompt
# ---------------------------------------------------------------------------

GENERATION_META_PROMPT = """You are helping create training data for a fine-tuned ad creative director model.

Given a brand, product, and some creative direction, generate a single ad creative brief as a JSON object with EXACTLY these 9 fields:

1. "headline" — A genuinely creative, memorable ad headline. NOT generic slogans like "Discover Excellence" or "Experience the Future." Think award-winning copywriting: wordplay, provocation, double meanings, cultural references, emotional hooks. Study these examples from real campaigns:
   - "Last Berry Standing" (Häagen-Dazs)
   - "D _ CK" (shower gel — dirty mind humor)
   - "Gifts sure to hit the perfect note." (Apple AirPods)
   - "Jazz do it." (Nike × Miles Davis)

2. "caption" — A vivid description of the SPECIFIC visual scene in the ad. Must describe concrete visual elements (objects, lighting, composition, what the viewer sees). NOT vague descriptions like "product on gradient background." Example: "A flaccid, drooping bell handle stands in contrast to a row of upright, sturdy ones to symbolize erectile dysfunction."

3. "tone" — 2-3 specific tone words (e.g., "cheeky, provocative, humorous" NOT just "professional")

4. "visual_style" — Specific visual treatment (e.g., "surrealist double exposure, warm golden hour lighting" NOT just "modern")

5. "conceptual_technique" — The advertising technique used (e.g., "object substitution, visual shorthand" NOT just "product showcase")

6. "call_to_action" — The specific CTA. Can be "None (Brand Awareness)" if it's a brand piece.

7. "emotion" — 2-3 specific emotions the ad should evoke (e.g., "amusement, surprise, cleanliness")

8. "typography_style" — Specific font recommendation and treatment (e.g., "Futura-esque geometric sans-serif, clean and modern" NOT just "sans-serif")

9. "color_scheme" — Specific palette tied to the brand (e.g., "McDonald's goldenrod yellow and coffee bean brown" NOT just "warm colors")

CRITICAL RULES:
- The headline MUST be creative and specific to this brand/product. No filler. No corporate speak.
- The caption MUST describe a concrete, filmable/photographable visual scene. What do we SEE?
- Every field must be specific enough that a designer could execute it without asking follow-up questions.
- The ad concept should feel like it could win a Cannes Lion or a D&AD Pencil.
- Respond with ONLY the JSON object. No markdown, no explanation, no backticks.

Here are {num_examples} examples of the quality bar you must match:

{examples}

Now generate a brief for:
Brand: {brand}
Product: {product}
Category: {category}
Suggested tone direction: {tone}
Suggested visual direction: {visual_style}

Remember: match the creativity and specificity of the examples above. The headline and caption are the most important fields — they must be genuinely creative and visually concrete."""


# ---------------------------------------------------------------------------
# Seed loader
# ---------------------------------------------------------------------------

def load_seeds(path: str) -> list[dict]:
    """Parse seed examples from the text file (mixed JSON formats)."""
    text = Path(path).read_text(encoding="utf-8-sig")

    objects = []
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(text[start : i + 1])
                    if "headline" in obj and "caption" in obj:
                        objects.append(obj)
                except json.JSONDecodeError:
                    pass
                start = None

    print(f"[seeds] Loaded {len(objects)} seed examples")
    return objects


# ---------------------------------------------------------------------------
# Quality validation
# ---------------------------------------------------------------------------

# Headlines that indicate GPT-4o fell into generic slop
BANNED_HEADLINE_PATTERNS = [
    r"^discover\b",
    r"^experience\b",
    r"^elevate\b",
    r"^unleash\b",
    r"^unlock\b",
    r"^redefine\b",
    r"^embrace\b",
    r"^transform\b",
    r"the future of\b",
    r"beyond\s+(the\s+)?ordinary",
    r"^where\s+\w+\s+meets\s+\w+",
    r"next[\s-]level",
    r"^more than (just )?a\b",
]

BANNED_CAPTION_PATTERNS = [
    r"product (is )?(shown|displayed|placed|set) (on|against) a .*(gradient|solid|plain)",
    r"(clean|simple|elegant) gradient background",
    r"^the product sits",
    r"^a (simple|clean|elegant) (shot|image|photo) of the product",
]


def validate_example(obj: dict) -> tuple[bool, str]:
    """Validate a generated example. Returns (is_valid, reason)."""
    # Check all 9 fields present and non-empty
    for field in REQUIRED_FIELDS:
        if field not in obj or not str(obj[field]).strip():
            return False, f"Missing or empty field: {field}"

    headline = obj["headline"].strip().lower()
    caption = obj["caption"].strip().lower()

    # Check headline isn't generic
    for pattern in BANNED_HEADLINE_PATTERNS:
        if re.search(pattern, headline, re.IGNORECASE):
            return False, f"Generic headline detected: '{obj['headline']}'"

    # Check caption describes a real scene
    if len(obj["caption"]) < 40:
        return False, f"Caption too short ({len(obj['caption'])} chars)"

    for pattern in BANNED_CAPTION_PATTERNS:
        if re.search(pattern, caption, re.IGNORECASE):
            return False, f"Generic caption detected"

    # Check tone/emotion have at least 2 descriptors
    if "," not in obj.get("tone", ""):
        return False, "Tone should have 2+ descriptors"

    return True, "OK"


# ---------------------------------------------------------------------------
# JSONL formatter (matches training format exactly)
# ---------------------------------------------------------------------------

def format_as_training_example(
    brand: str,
    product: str,
    tone: str,
    visual_style: str,
    technique: str,
    brief: dict,
) -> dict:
    """Format a single example as an OpenAI fine-tuning message."""
    return {
        "messages": [
            {
                "role": "system",
                "content": CREATIVE_BRIEF_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Create an ad for:\n"
                    f"Brand: {brand}\n"
                    f"Product type: {product}\n"
                    f"Tone: {tone}\n"
                    f"Visual style: {visual_style}\n"
                    f"Conceptual technique: {technique}\n"
                    f"Format: image"
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(brief, ensure_ascii=False),
            },
        ]
    }


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------

def generate_dataset(
    seeds: list[dict],
    matrix: list[tuple],
    output_path: str,
    max_retries: int = 2,
):
    """Generate the full training dataset."""
    client = OpenAI()
    results = []
    failures = []

    total = len(matrix)
    print(f"\n[generate] Generating {total} examples using {GENERATION_MODEL}...")
    print(f"[generate] Output: {output_path}\n")

    for idx, (brand, product, category, tone, vis_style) in enumerate(matrix):
        # Pick 3 random seeds as few-shot examples (rotate to avoid repetition)
        few_shot = random.sample(seeds, min(3, len(seeds)))
        examples_text = "\n\n".join(
            f"Example {i+1}:\n{json.dumps(ex, indent=2, ensure_ascii=False)}"
            for i, ex in enumerate(few_shot)
        )

        prompt = GENERATION_META_PROMPT.format(
            num_examples=len(few_shot),
            examples=examples_text,
            brand=brand,
            product=product,
            category=category,
            tone=tone,
            visual_style=vis_style,
        )

        # Try generating with retries
        for attempt in range(max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=GENERATION_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,  # High temp for creative diversity
                    max_tokens=600,
                )

                raw = response.choices[0].message.content.strip()
                # Strip markdown fences if present
                raw = re.sub(r"^```json\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

                brief = json.loads(raw)
                is_valid, reason = validate_example(brief)

                if is_valid:
                    # Format the user message tone/style from the brief itself
                    # (so training data is self-consistent)
                    training_ex = format_as_training_example(
                        brand=brand,
                        product=product,
                        tone=brief["tone"],
                        visual_style=brief["visual_style"],
                        technique=brief["conceptual_technique"],
                        brief=brief,
                    )
                    results.append(training_ex)
                    print(f"  [{idx+1}/{total}] [OK] {brand} {product}: \"{brief['headline'][:50]}\"")
                    break
                else:
                    if attempt < max_retries:
                        print(f"  [{idx+1}/{total}] [retry] Retry {attempt+1} ({reason})")
                        time.sleep(0.5)
                    else:
                        print(f"  [{idx+1}/{total}] [FAIL] {brand} {product}: {reason}")
                        failures.append((brand, product, reason))

            except json.JSONDecodeError as e:
                if attempt < max_retries:
                    print(f"  [{idx+1}/{total}] [retry] JSON parse error, retry {attempt+1}")
                    time.sleep(0.5)
                else:
                    print(f"  [{idx+1}/{total}] [FAIL] {brand} {product}: JSON parse failed")
                    failures.append((brand, product, f"JSON: {e}"))

            except Exception as e:
                if attempt < max_retries:
                    print(f"  [{idx+1}/{total}] [retry] API error, retry {attempt+1}: {e}")
                    time.sleep(1)
                else:
                    print(f"  [{idx+1}/{total}] [FAIL] {brand} {product}: {e}")
                    failures.append((brand, product, str(e)))

        # Rate limiting — small delay between requests
        time.sleep(0.3)

    # ── Also convert seed examples into training format ──
    print(f"\n[seeds] Converting {len(seeds)} seed examples to training format...")
    try:
        from seed_brand_map import SEED_BRAND_MAP
    except ImportError:
        SEED_BRAND_MAP = {}

    seed_training = []
    for seed in seeds:
        headline = seed.get("headline", "")
        brand_info = SEED_BRAND_MAP.get(headline)

        if brand_info:
            brand, product, category = brand_info
        else:
            # Fallback: use headline words
            brand = headline.split()[0] if headline else "Brand"
            product = "flagship product"

        training_ex = format_as_training_example(
            brand=brand,
            product=product,
            tone=seed.get("tone", "creative"),
            visual_style=seed.get("visual_style", "modern"),
            technique=seed.get("conceptual_technique", "visual metaphor"),
            brief=seed,
        )
        seed_training.append(training_ex)

    # ── Write output ──
    all_examples = results + seed_training
    random.shuffle(all_examples)  # Shuffle so seeds are mixed in

    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"DATASET GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  GPT-4o generated:  {len(results)}")
    print(f"  Seed examples:     {len(seed_training)}")
    print(f"  Total examples:    {len(all_examples)}")
    print(f"  Failures:          {len(failures)}")
    print(f"  Output:            {output_path}")
    print(f"{'='*60}")

    if failures:
        print(f"\nFailed entries:")
        for brand, product, reason in failures:
            print(f"  - {brand} {product}: {reason}")

    # ── Validation summary ──
    print(f"\n[validate] Running final validation on {output_path}...")
    validate_output_file(output_path)

    return all_examples


def validate_output_file(path: str):
    """Validate the final JSONL file."""
    errors = 0
    system_prompts = set()

    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            try:
                row = json.loads(line)
                msgs = row["messages"]
                assert len(msgs) == 3, f"Expected 3 messages, got {len(msgs)}"
                assert msgs[0]["role"] == "system"
                assert msgs[1]["role"] == "user"
                assert msgs[2]["role"] == "assistant"
                system_prompts.add(msgs[0]["content"])

                # Validate assistant content is valid JSON with required fields
                brief = json.loads(msgs[2]["content"])
                for field in REQUIRED_FIELDS:
                    assert field in brief, f"Missing field: {field}"

            except Exception as e:
                print(f"  Line {lineno}: {e}")
                errors += 1

    print(f"  Total lines: {lineno}")
    print(f"  Errors: {errors}")
    print(f"  Unique system prompts: {len(system_prompts)}")
    if len(system_prompts) == 1:
        print(f"  [OK] System prompt is consistent across all examples")
    else:
        print(f"  [FAIL] WARNING: Multiple system prompts found!")
        for sp in system_prompts:
            print(f"    - {sp[:80]}...")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Look for seeds file
    seed_paths = [
        "seeds.txt",
        "Untitled_document.txt",
        os.path.join("data", "seeds.txt"),
    ]

    seed_file = None
    for p in seed_paths:
        if os.path.exists(p):
            seed_file = p
            break

    if seed_file is None:
        print("ERROR: No seed file found. Place your seed examples in seeds.txt")
        print("Looked in:", seed_paths)
        sys.exit(1)

    seeds = load_seeds(seed_file)
    if len(seeds) < 5:
        print(f"ERROR: Only {len(seeds)} seeds found. Need at least 5.")
        sys.exit(1)

    # Generate!
    generate_dataset(
        seeds=seeds,
        matrix=BRAND_PRODUCT_MATRIX,
        output_path=OUTPUT_FILE,
    )