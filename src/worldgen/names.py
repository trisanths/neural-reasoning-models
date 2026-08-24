"""Synthetic name grammar.

Names are built from consonant-vowel syllables so they never collide with
real-world entities. A blocklist of frequent real names is checked anyway,
per SPEC.md section 2, and generation retries on a hit.
"""

ONSETS = ["b", "d", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z",
          "br", "dr", "gr", "kl", "pl", "tr", "st", "vr"]
VOWELS = ["a", "e", "i", "o", "u"]
CODAS = ["", "", "", "n", "r", "s", "l", "m", "x"]

COMPANY_SUFFIXES = ["Corp", "Group", "Holdings", "Systems", "Industries",
                    "Partners", "Logistics", "Labs"]

BLOCKLIST = {
    "apple", "google", "amazon", "microsoft", "meta", "tesla", "intel",
    "oracle", "nvidia", "samsung", "toyota", "boeing", "siemens", "nestle",
    "london", "paris", "berlin", "tokyo", "madrid", "moscow", "beijing",
    "delhi", "cairo", "rome", "vienna", "dublin", "oslo", "lima", "kyoto",
    "john", "mary", "james", "robert", "michael", "linda", "david", "sarah",
    "maria", "anna", "peter", "thomas", "karen", "nancy", "lisa", "susan",
    "france", "germany", "japan", "brazil", "canada", "india", "china",
    "texas", "ohio", "utah", "kenya", "chile", "peru", "cuba", "chad",
    "mali", "iran", "iraq", "laos", "nepal", "oman", "qatar", "spain",
}


def _syllable(rng):
    return (ONSETS[int(rng.integers(len(ONSETS)))]
            + VOWELS[int(rng.integers(len(VOWELS)))]
            + CODAS[int(rng.integers(len(CODAS)))])


def make_word(rng, min_syllables=2, max_syllables=3):
    """Return one capitalized synthetic word not on the blocklist."""
    while True:
        n = int(rng.integers(min_syllables, max_syllables + 1))
        word = "".join(_syllable(rng) for _ in range(n))
        if word.lower() not in BLOCKLIST and 4 <= len(word) <= 14:
            return word.capitalize()


def company_name(rng):
    return f"{make_word(rng)} {COMPANY_SUFFIXES[int(rng.integers(len(COMPANY_SUFFIXES)))]}"


def person_name(rng):
    return f"{make_word(rng, 2, 2)} {make_word(rng, 2, 3)}"


def place_name(rng):
    return make_word(rng, 2, 3)


def unique_names(rng, kind, count):
    """Return count distinct names of the given kind: company, person, place."""
    maker = {"company": company_name, "person": person_name, "place": place_name}[kind]
    seen = set()
    out = []
    while len(out) < count:
        name = maker(rng)
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out
