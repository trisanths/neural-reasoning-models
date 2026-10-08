"""The general check: ordinary questions any competent model should answer.

The comparison this directory runs is about one narrow ability, and a report
that measured only that ability would say nothing about how these models
compare overall. So the same harness is pointed at ordinary factual, numeric
and commonsense questions, written as forced choice over four candidates so
that `src/norm/cmpwork/grade.py` grades them by the same rule and the chance
floor is 0.25 by construction.

The questions are deliberately unremarkable. Nothing here is a trick, and
nothing here is in the benchmark's invented vocabulary.
"""
from __future__ import annotations

import gzip
import json
import os

Q = [
    ("fact", "What is the capital city of Japan?",
     "tokyo", ["tokyo", "osaka", "kyoto", "seoul"]),
    ("fact", "Which planet in our solar system is the largest?",
     "jupiter", ["jupiter", "saturn", "neptune", "earth"]),
    ("fact", "What gas do plants take in from the air for photosynthesis?",
     "carbon dioxide", ["carbon dioxide", "oxygen", "nitrogen", "hydrogen"]),
    ("fact", "Who wrote the play Romeo and Juliet?",
     "shakespeare", ["shakespeare", "dickens", "chaucer", "milton"]),
    ("fact", "What is the chemical symbol for gold?",
     "au", ["au", "ag", "gd", "go"]),
    ("fact", "On which continent is the country Kenya?",
     "africa", ["africa", "asia", "europe", "australia"]),
    ("fact", "What is the largest ocean on Earth?",
     "pacific", ["pacific", "atlantic", "indian", "arctic"]),
    ("fact", "In which organ of the human body does most digestion of "
     "food into nutrients take place?",
     "intestine", ["intestine", "liver", "lung", "kidney"]),
    ("fact", "What is the freezing point of water at sea level in degrees "
     "Celsius?", "zero", ["zero", "ten", "thirty", "hundred"]),
    ("fact", "Which language has the most native speakers in Brazil?",
     "portuguese", ["portuguese", "spanish", "french", "english"]),
    ("num", "What is 17 plus 26?", "43", ["43", "33", "44", "53"]),
    ("num", "What is 12 times 12?", "144", ["144", "124", "148", "132"]),
    ("num", "A shirt costs 20 dollars and is reduced by 25 percent. "
     "What is the new price in dollars?", "15", ["15", "16", "18", "5"]),
    ("num", "What is half of 250?", "125", ["125", "150", "120", "500"]),
    ("num", "If a train travels 60 kilometres in 45 minutes, how many "
     "kilometres does it travel in one hour?", "80", ["80", "60", "75", "90"]),
    ("num", "What is the next number in the sequence 2, 6, 12, 20, 30?",
     "42", ["42", "40", "36", "44"]),
    ("num", "A box holds 8 rows of 7 pencils. How many pencils is that?",
     "56", ["56", "54", "63", "48"]),
    ("num", "What is 100 minus 37?", "63", ["63", "73", "67", "53"]),
    ("reason", "Tom is taller than Amir. Amir is taller than Bea. Who is "
     "the tallest of the three?", "tom", ["tom", "amir", "bea", "nobody"]),
    ("reason", "All birds in this aviary are green. Pip is a bird in this "
     "aviary. What colour is Pip?",
     "green", ["green", "blue", "red", "unknown"]),
    ("reason", "You put an ice cube in a hot pan. What happens to the ice?",
     "melts", ["melts", "freezes", "hardens", "grows"]),
    ("reason", "Sara left her umbrella at home and it started raining "
     "heavily while she walked. What is she most likely to be when she "
     "arrives?", "wet", ["wet", "dry", "warm", "early"]),
    ("reason", "A shop opens at 9 and closes at 5. It is 7 in the evening. "
     "Is the shop open or closed?", "closed", ["closed", "open", "busy",
                                               "empty"]),
    ("reason", "If today is Wednesday, what day will it be in two days?",
     "friday", ["friday", "thursday", "saturday", "monday"]),
    ("reason", "Every book on the top shelf is red. The blue book is on "
     "some shelf in the room. Can the blue book be on the top shelf?",
     "no", ["no", "yes", "maybe", "always"]),
    ("reason", "A cup of tea is left on a desk in a cool room for an hour. "
     "Is it hotter or cooler than when it was poured?",
     "cooler", ["cooler", "hotter", "boiling", "frozen"]),
]


def main():
    out = "results/extern/general_items.jsonl.gz"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with gzip.open(out, "wt") as fh:
        for i, (fam, q, gold, opts) in enumerate(Q):
            text = (q + "\n\nChoose one of: " + ", ".join(opts) + ".")
            fh.write(json.dumps({
                "id": f"gen/{fam}/{i}", "cond": "general", "family": fam,
                "split": "general", "fid": "general", "gold": gold,
                "options": opts, "floor": 1.0 / len(opts), "n_pages": 1,
                "n": 1, "item_key": f"gen/{fam}/{i}", "text": text,
                "question": q}) + "\n")
    print("wrote", out, len(Q), "items")
    from collections import Counter
    print(Counter(f for f, _, _, _ in Q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
