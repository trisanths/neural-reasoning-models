"""Frequent English common nouns and verbs the scrubber must not touch.

The list has exactly 200 distinct lowercase words: 100 nouns then 100
verbs, drawn from standard frequency lists. The common word
preservation test feeds these through scrub_document and requires them
back unchanged.
"""

COMMON_WORDS = [
    # nouns
    "time", "year", "people", "way", "day", "man", "thing", "woman",
    "life", "child",
    "world", "school", "state", "family", "student", "group", "country",
    "problem", "hand", "part",
    "place", "case", "week", "company", "system", "program", "question",
    "work", "government", "number",
    "night", "point", "home", "water", "room", "mother", "area", "money",
    "story", "fact",
    "month", "lot", "right", "study", "book", "eye", "job", "word",
    "business", "issue",
    "side", "kind", "head", "house", "service", "friend", "father",
    "power", "hour", "game",
    "line", "end", "member", "law", "car", "city", "community", "name",
    "team", "minute",
    "idea", "body", "information", "back", "parent", "face", "level",
    "office", "door", "health",
    "person", "art", "war", "history", "party", "result", "change",
    "morning", "reason", "research",
    "girl", "guy", "moment", "air", "teacher", "force", "education",
    "foot", "boy", "age",
    # verbs
    "be", "have", "do", "say", "get", "make", "go", "know", "take",
    "see",
    "come", "think", "look", "want", "give", "use", "find", "tell",
    "ask", "seem",
    "feel", "try", "leave", "call", "become", "mean", "keep", "let",
    "begin", "help",
    "talk", "turn", "start", "show", "hear", "play", "run", "move",
    "like", "live",
    "believe", "hold", "bring", "happen", "write", "provide", "sit",
    "stand", "lose", "pay",
    "meet", "include", "continue", "set", "learn", "lead", "understand",
    "watch", "follow", "stop",
    "create", "speak", "read", "allow", "add", "spend", "grow", "open",
    "walk", "win",
    "offer", "remember", "love", "consider", "appear", "buy", "wait",
    "serve", "die", "send",
    "expect", "build", "stay", "fall", "cut", "reach", "kill", "remain",
    "suggest", "raise",
    "pass", "sell", "require", "report", "decide", "pull", "return",
    "explain", "hope", "carry",
]
