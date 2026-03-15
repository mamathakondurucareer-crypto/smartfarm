"""Farm-wide constants, thresholds, and configuration values."""

# ── Pond Species ──
FISH_SPECIES = ["murrel", "rohu", "catla", "grass_carp", "common_carp"]
CRAB_SPECIES = ["mud_crab"]

# ── Greenhouse Crops ──
GH_CROPS = ["green_chilli", "tomato", "cucumber", "ridge_gourd", "bitter_gourd"]

# ── Vertical Farm Crops ──
VF_CROPS = ["spinach", "coriander", "fenugreek", "amaranthus"]

# ── Field Crops ──
FIELD_CROPS = ["turmeric", "ginger"]

# ── Market Cities ──
MARKETS = {
    "hyderabad": {"distance_km": 400, "revenue_share": 0.35},
    "chennai": {"distance_km": 180, "revenue_share": 0.25},
    "vijayawada": {"distance_km": 280, "revenue_share": 0.15},
    "kadapa": {"distance_km": 200, "revenue_share": 0.10},
    "nellore": {"distance_km": 15, "revenue_share": 0.15},
}

# ── Departments ──
DEPARTMENTS = [
    "aquaculture", "greenhouse", "poultry", "field_crops",
    "nursery", "packhouse", "maintenance", "management", "technology",
]

# ── Inventory Categories ──
INVENTORY_CATEGORIES = [
    "fish_feed", "poultry_feed", "seeds", "seedling_trays", "fertilizers",
    "chemicals_pesticides", "packaging_materials", "fuel", "spare_parts",
    "safety_equipment", "office_supplies", "cleaning_supplies", "veterinary",
]

# ── Automation Systems ──
AUTOMATION_SYSTEMS = [
    "irrigation", "aeration", "fish_feeder", "egg_belt",
    "manure_scraper", "gh_climate", "lighting", "drone",
]

# ── Revenue Streams ──
REVENUE_STREAMS = [
    "aquaculture", "greenhouse", "vertical_farm", "field_crops",
    "poultry_eggs", "duck_eggs", "honey", "nursery",
    "solar_export", "compost", "direct_marketing", "consulting", "agri_tourism",
]

# ── Expense Categories ──
EXPENSE_CATEGORIES = [
    "feed", "seed", "fertilizer", "chemical", "fuel", "electricity", "water",
    "labour", "salary", "maintenance", "logistics", "packaging", "rent",
    "insurance", "professional_fees", "office", "marketing", "technology", "miscellaneous",
]
