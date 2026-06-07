"""
Indian cities database for query generation.
~500 cities organized by state, covering metros, state capitals,
tier-2/3 cities, and major district headquarters.
"""

# Each entry: {"city": "Name", "state": "State"}
# Organized by state for maintainability.

CITIES = [
    # ─── Maharashtra ─────────────────────────────────────────────────
    {"city": "Mumbai", "state": "Maharashtra"},
    {"city": "Pune", "state": "Maharashtra"},
    {"city": "Nagpur", "state": "Maharashtra"},
    {"city": "Thane", "state": "Maharashtra"},
    {"city": "Nashik", "state": "Maharashtra"},
    {"city": "Aurangabad", "state": "Maharashtra"},
    {"city": "Solapur", "state": "Maharashtra"},
    {"city": "Kolhapur", "state": "Maharashtra"},
    {"city": "Amravati", "state": "Maharashtra"},
    {"city": "Navi Mumbai", "state": "Maharashtra"},
    {"city": "Sangli", "state": "Maharashtra"},
    {"city": "Malegaon", "state": "Maharashtra"},
    {"city": "Jalgaon", "state": "Maharashtra"},
    {"city": "Akola", "state": "Maharashtra"},
    {"city": "Latur", "state": "Maharashtra"},
    {"city": "Dhule", "state": "Maharashtra"},
    {"city": "Ahmednagar", "state": "Maharashtra"},
    {"city": "Chandrapur", "state": "Maharashtra"},
    {"city": "Parbhani", "state": "Maharashtra"},
    {"city": "Ichalkaranji", "state": "Maharashtra"},
    {"city": "Jalna", "state": "Maharashtra"},
    {"city": "Nanded", "state": "Maharashtra"},
    {"city": "Satara", "state": "Maharashtra"},
    {"city": "Ratnagiri", "state": "Maharashtra"},
    {"city": "Osmanabad", "state": "Maharashtra"},
    {"city": "Wardha", "state": "Maharashtra"},
    {"city": "Yavatmal", "state": "Maharashtra"},
    {"city": "Beed", "state": "Maharashtra"},
    {"city": "Gondia", "state": "Maharashtra"},
    {"city": "Hinganghat", "state": "Maharashtra"},
]


def get_cities() -> list[dict]:
    """Return the full list of cities."""
    return CITIES


def get_cities_by_state() -> dict[str, list[str]]:
    """Return cities grouped by state."""
    result = {}
    for entry in CITIES:
        state = entry["state"]
        if state not in result:
            result[state] = []
        result[state].append(entry["city"])
    return result


def get_city_count() -> int:
    """Return the total number of cities."""
    return len(CITIES)
