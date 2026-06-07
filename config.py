"""
Configuration constants for the Commerce Coaching Institute Scraper.
"""

import os

# ─── Paths ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "institutes.db")

# ─── Categories ──────────────────────────────────────────────────────
CATEGORIES = [
    "B.com",
    "Baf",
    "Bba",
    "Commerce",
]

# ─── Query Templates ─────────────────────────────────────────────────
# Each template is formatted with {category} and {city}
QUERY_TEMPLATES = [
    "{category} Classes in {city}",
    "{category} Coaching Institute {city}",
]

# ─── Search Settings (Stage 2) ───────────────────────────────────────
SEARCH_MAX_RESULTS = 10            # results per query
SEARCH_DELAY_MIN = 2.0             # minimum seconds between queries
SEARCH_DELAY_MAX = 4.0             # maximum seconds between queries

# Domains to skip during discovery (not institute websites)
EXCLUDED_DOMAINS = {
    # ── Social media ──
    "youtube.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "linkedin.com", "quora.com", "reddit.com",
    "pinterest.com", "t.me", "telegram.org", "whatsapp.com",
    # ── General reference / marketplaces ──
    "wikipedia.org", "amazon.com", "amazon.in", "flipkart.com",
    "play.google.com", "apps.apple.com",
    # ── Job / HR portals ──
    "glassdoor.com", "glassdoor.co.in", "indeed.com", "naukri.com",
    "shine.com", "monster.com", "internshala.com", "freshersworld.com",
    # ── Gaming sites (CS = Counter-Strike false positives) ──
    "steampowered.com", "store.steampowered.com", "counter-strike.net",
    "store.epicgames.com", "epicgames.com", "valvesoftware.com",
    "igdb.com", "pcgamingwiki.com",
    # ── Education aggregators / listing sites (not actual institutes) ──
    "justdial.com", "sulekha.com", "urbanpro.com", "shiksha.com",
    "collegedunia.com", "getmyuni.com", "careers360.com",
    "caclubindia.com", "selfstudys.com", "toprankers.com",
    "embibe.com", "vedantu.com", "byjus.com", "unacademy.com",
    "edufever.com", "schoolsuniverse.com", "gurukulgalaxy.com",
    "instituterank.com", "locanto.com", "locanto.me", "locanto.in",
    "jagranjosh.com", "studylib.net", "targetstudy.com",
    "entranceindia.com", "aglasem.com", "gradeup.co", "testbook.com",
    "prepp.in", "adda247.com", "teachoo.com", "doubtnut.com",
    "toppr.com", "leverageedu.com", "geeksforgeeks.org", "w3schools.com",
    "coursetakers.com", "collegedekho.com", "shikshacoach.com",
    "codegnan.com", "justcityplace.com", "techtrainees.com",
    "caexams.in", "vishwasca.com",
    # ── Generic coaching aggregators (list many non-commerce institutes) ──
    "bestcoaching.app", "addressguru.in", "edial.in",
    "chunocollege.com", "successcds.net", "safalta.com",
    "e-hometutors.com", "tutorindia.com", "myprivatetutor.com",
    # ── Coding / tech platforms (CS = Computer Science false positives) ──
    "ccbp.in", "britishschooloflanguages.com",
    "codecademy.com", "coursera.org", "udemy.com", "edx.org",
    "khanacademy.org", "simplilearn.com", "intellipaat.com",
    "greatlearning.com", "scaler.com", "masaischool.com",
    "codeacademy.com", "freecodecamp.org", "hackerrank.com",
    # ── News / general content ──
    "indiatoday.in", "timesofindia.indiatimes.com", "ndtv.com",
    "thehindu.com", "hindustantimes.com", "livemint.com",
    "moneycontrol.com", "financialexpress.com",
    "economictimes.indiatimes.com", "businesstoday.in",
    # ── Finance / non-education ──
    "goodreturns.in", "bankbazaar.com", "policybazaar.com",
    "groww.in", "zerodha.com",
    # ── Travel / food / lifestyle ──
    "tripadvisor.com", "tripadvisor.in", "zomato.com", "swiggy.com",
    "makemytrip.com", "goibibo.com",
    # ── Government / regulatory bodies (not coaching institutes) ──
    "icai.org", "icsi.edu", "icmai.in",
    # ── Google properties ──
    "google.com", "google.co.in", "maps.google.com",
    # ── More aggregator / listing / irrelevant sites ──
    "coursetakers.com", "collegedekho.com", "shikshacoach.com",
    "codegnan.com", "justcityplace.com", "techtrainees.com",
    "caexams.in", "vishwasca.com", "click.in", "indianyellowpages.com",
    "careermaniaa.com", "webindia123.com", "realtrainings.com",
    "teacheron.com", "slideserve.com", "iimskills.com",
    "proschoolonline.com", "thewallstreetschool.com",
}

# ─── Relevance Validation ────────────────────────────────────────────
# STRICT: A record MUST contain at least one COMMERCE-SPECIFIC keyword.
# Generic words like "coaching", "classes", "institute" are NOT enough.
COMMERCE_KEYWORDS = [
    # Chartered Accountancy
    "chartered accountant", "ca foundation", "ca inter", "ca intermediate",
    "ca final", "ca coaching", "ca classes", "ca course", "ca institute",
    "ca tuition", "c.a.", "ca exam",
    # Company Secretary
    "company secretary", "cs foundation", "cs executive", "cs professional",
    "cs coaching", "cs classes", "c.s.",
    # Cost & Management Accountancy
    "cost account", "cma foundation", "cma inter", "cma final",
    "cma coaching", "cma classes", "c.m.a.", "cost management",
    # Other commerce qualifications
    "acca", "cfa", "b.com", "bcom", "b.com coaching", "bba", "baf", "bachelor of business", "bachelor of accounting",
    # Commerce subjects/domains
    "commerce coaching", "commerce classes", "commerce tuition",
    "commerce institute", "commerce academy",
    "accounting", "accountancy", "taxation", "tax coaching",
    "audit", "gst", "income tax", "tally",
    "financial accounting", "cost accounting",
    "business studies", "economics tuition",
    # Professional bodies
    "icai", "icsi", "icmai",
]

# If ANY of these appear in the name, REJECT the record even if it matched
# a commerce keyword somewhere in the page text.
IRRELEVANT_NAME_KEYWORDS = [
    # Medical
    "neet", "medical college", "medical admission", "mbbs", "dental",
    # Engineering
    "jee", "iit", "nit", "gate exam", "engineering college",
    # Government exams (not commerce)
    "upsc", "ias", "ips", "appsc", "ssc ", "rrb", "nda",
    "railway", "defence", "police", "army",
    # Coding / tech
    "full stack", "python", "java", "coding", "programming",
    "software engineer", "web development", "data science",
    "machine learning", "artificial intelligence",
    # MBA / management (not commerce coaching)
    "cat coaching", "cat exam", "mba admission", "iim ",
    "gmat", "mat exam", "xat exam",
    # Schools
    "gold rate", "weather", "news",
    # Irrelevant education
    "ielts", "toefl", "pte", "gre ", "sat exam",
    "spoken english", "language classes",
]

# If any of these phrases appear in the title/name, it's likely an aggregator listicle
JUNK_TITLE_PHRASES = [
    "best 10", "top 10", "top 5", "best coaching in",
    "list of", "classified ads", "yellow pages",
    "directory", "fees, placements & reviews",
]

# Phrases that indicate the "address" field actually contains junk content
JUNK_ADDRESS_PHRASES = [
    # UI elements
    "click", "subscribe", "unblock", "notification",
    "cookie", "accept", "allow", "download",
    "login", "sign up", "sign in", "register",
    "share", "follow us", "get directions", "view on map",
    "read more", "learn more", "view more",
    "loading", "please wait", "required fields",
    # Not addresses
    "ratings", "reviews", "salary", "experience", "lac", "lpa",
    "pros:", "cons:", "here is why", "here's why",
    "contact details", "email",
    "best 10", "top 10", "best coaching", "best online",
    "engineering colleges", "search tutors",
    "associate software", "software engineer",
    "admission", "cut off", "eligibility",
]

# ─── Address Validation ──────────────────────────────────────────────
# An extracted address should look like an Indian physical address.
# Must contain at least one of these patterns to be considered valid.
ADDRESS_INDICATORS = [
    # Indian PIN codes (6 digits)
    # (checked via regex in code, not here)
    # Location words common in Indian addresses
    "road", "street", "lane", "nagar", "colony", "sector",
    "plot", "block", "floor", "building", "tower",
    "near", "opposite", "behind", "beside", "next to",
    "phase", "pocket", "enclave", "vihar", "puram",
    "gali", "mohalla", "chowk", "marg", "path",
    "cross", "main", "layout", "extension", "ext.",
    # Specific to addresses
    "no.", "no:", "#", "flat", "house", "door",
    "ground floor", "1st floor", "2nd floor", "3rd floor",
    # Indian state/city indicators in address
    "india", "pin", "pincode",
]

# ─── Extraction Settings (Stage 3) ───────────────────────────────────
REQUEST_TIMEOUT = 10               # seconds
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
EXTRACT_DELAY_MIN = 1.0            # minimum seconds between page fetches
EXTRACT_DELAY_MAX = 2.5            # maximum seconds between page fetches

# ─── Deduplication Settings (Stage 4) ────────────────────────────────
NAME_SIMILARITY_THRESHOLD = 0.85   # 0.0 to 1.0, for fuzzy name matching

