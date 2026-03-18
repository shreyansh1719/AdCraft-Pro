"""
Seed-to-brand mapping for the 29 hand-curated examples.

Since the seeds don't explicitly state brand/product in a structured way,
this file maps each headline to the correct brand and product info so the
training JSONL user messages are accurate.

This is imported by generate_training_data_v3.py when converting seeds.
"""

# Maps headline -> (brand, product, category)
SEED_BRAND_MAP = {
    "Gifts sure to hit the perfect note.": ("Apple", "AirPods", "Technology"),
    "SUN CARE": ("Nivea", "Sun Protect SPF 50", "Skincare"),
    "CASIO": ("Casio", "G-Shock watch", "Watches"),
    "ON YOUR WAY. SO YOU CAN SLEEP LONGER.": ("McDonald's", "McCafé coffee", "Fast Food"),
    "D _ CK": ("Old Spice", "Shower Gel", "Personal Care"),
    "VIAGRA": ("Pfizer", "Viagra", "Pharmaceutical"),
    "Some sparks need protection.": ("Durex", "Classic condoms", "Health"),
    "Break the block.": ("Sudafed", "Nasal Decongestant", "Pharmaceutical"),
    "WHAT GOES IN THE OCEAN GOES IN YOU.": ("Surfrider Foundation", "Ocean Conservation Campaign", "Non-Profit"),
    "Brightness: 100%": ("Colgate", "Optic White toothpaste", "Oral Care"),
    "SWAROVSKI": ("Swarovski", "Crystal Ring", "Jewelry"),
    "A bond that's timeless": ("Tim Hortons", "Original Blend Coffee", "Fast Food"),
    "A bond that\u2019s timeless": ("Tim Hortons", "Original Blend Coffee", "Fast Food"),
    "Think bigger. Build faster.": ("Figma", "Design Tool", "Software"),
    "INTRODUCING OUR NEW COLLECTION": ("Ralph Lauren", "Linen Collection", "Fashion"),
    "Miracles happen, but don't count on them.": ("Anmol", "Life Insurance", "Insurance"),
    "WE HELP YOUR BRAND GROW.": ("Maya Jans", "Brand Consulting", "Agency"),
    "6 Months of Disney+ On Us": ("Amazon Music", "Music Streaming + Disney Bundle", "Streaming"),
    "Balloon": ("Balloon", "Short Film", "Entertainment"),
    "Become Someone Else": ("MintVinetu", "Bookstore", "Retail"),
    "Worldwide Delivery": ("FedEx", "International Shipping", "Logistics"),
    "Need Space?": ("IKEA", "HEMNES Shoe Cabinet", "Furniture"),
    "Leave Nothing Behind!": ("LifeProof", "Rugged Phone Case", "Accessories"),
    "Designed to Fit in Any Environment": ("MINI", "Cooper", "Automotive"),
    "Wake Up to the Adventure Inside You!": ("Crusoe", "Men's Innerwear", "Fashion"),
    "If You Really Want to Touch Someone, Send Them a Letter.": ("Australia Post", "Letter Service", "Postal"),
    "CHARGE YOUR ENERGY": ("Red Bull", "Energy Drink", "Beverages"),
    "Jazz do it.": ("Nike", "Air Force 1", "Sportswear"),
    "AirPods Max": ("Apple", "AirPods Max", "Technology"),
    "Supercharge your fitness and wellness": ("Apple", "Apple Watch Ultra", "Technology"),
    "FLY HIGH WITH THE POWERHOUSE": ("KTM", "Duke 390", "Motorcycle"),
}