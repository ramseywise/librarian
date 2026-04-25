import re
import unicodedata

# Categorized for maintainability
WINE_DATA = {
    # Core word in multiple languages
    "core": ["wine", "vin", "wein", "wijn", "vinho", "vino"],
    # Colour / style labels (many double as French/Italian/Spanish adjectives)
    "types": [
        # Colours
        "rouge",
        "blanc",
        "bianco",
        "blanco",
        "tinto",
        "rosso",
        "weiss",
        "weiß",
        "rosé",
        # Sparkling styles
        "sparkling",
        "champagne",
        "prosecco",
        "cava",
        "cremant",  # accent-stripped form of crémant
        "sekt",
        "petnat",  # accent-stripped pét-nat
        # Fortified / dessert
        "port",
        "sherry",
        "madeira",
        "marsala",
        "sauternes",
        # Emerging styles
        "orange",  # orange wine — matched on "orange wine" context
        "natural",  # natural wine
        "biodynamic",
        "organic",
    ],
    # Grape varietals
    "varietals": [
        # Whites
        "riesling",
        "chardonnay",
        "sauvignon",
        "pinot",
        "viognier",
        "gewurztraminer",  # accent-stripped
        "muscat",
        "moscato",
        "chenin",
        "albarino",  # accent-stripped albariño
        "gruner",  # grüner veltliner
        "torrontes",  # torrontés
        "verdejo",
        "vermentino",
        # Reds
        "cabernet",
        "merlot",
        "malbec",
        "syrah",
        "shiraz",
        "tempranillo",
        "grenache",
        "garnacha",
        "nebbiolo",
        "sangiovese",
        "barbera",
        "mouvedre",  # accent-stripped mourvèdre
        "monastrell",
        "zinfandel",
        "primitivo",
        "carmenere",  # carménère
        "montepulciano",
        "dolcetto",
        "corvina",
    ],
    # Appellations / regions
    "regions": [
        # France
        "bordeaux",
        "burgundy",
        "champagne",
        "loire",
        "rhone",  # rhône
        "alsace",
        "provence",
        "languedoc",
        # Italy
        "tuscany",
        "chianti",
        "barolo",
        "barbaresco",
        "brunello",
        "piedmont",
        "veneto",
        "sicily",
        "amarone",
        # Spain
        "rioja",
        "ribera",
        "priorat",
        # Portugal
        "douro",
        "alentejo",
        # Americas
        "napa",
        "sonoma",
        "mendoza",
        # Rest of world
        "barossa",
        "marlborough",
        "stellenbosch",
        "mosel",
        "rheingau",
    ],
    # Technical / tasting / production vocabulary
    "technical": [
        # Tasting descriptors
        "tannin",
        "acidity",
        "aroma",
        "bouquet",
        "nose",
        "finish",
        "mouthfeel",
        "body",
        "balance",
        "minerality",
        "typicity",
        "structure",
        # Winemaking
        "terroir",
        "vintage",
        "cuvee",  # cuvée
        "oak",
        "cellar",
        "malolactic",
        "maceration",
        "fermentation",
        "lees",
        "brix",
        "appellation",
        "blend",
        "varietal",
        # Serving / equipment
        "sommelier",
        "decanter",
        "glassware",
        "pairing",
        # Establishment
        "winery",
        "domaine",
        "chateau",  # château
        "negociant",  # négociant
        "producer",
        "vineyard",
        "viticulture",
        "oenology",
        "enology",
    ],
}

# Flatten into a single list
ALL_KEYWORDS = [item for sublist in WINE_DATA.values() for item in sublist]

# Pluralisation: handles simple +s AND the -y → -ies form
#   winery → wineries, variety → varieties, while sommelier → sommeliers still works
WINE_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in ALL_KEYWORDS) + r")(?:ies|s)?\b",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    """Removes accents: 'cuvée' -> 'cuvee'"""
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def is_wine_related(text: str) -> bool:
    if not text:
        return False
    # Normalize and check
    clean_text = normalize_text(text)
    return bool(WINE_RE.search(clean_text))
