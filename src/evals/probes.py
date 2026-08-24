"""Knowledge probes for real world facts, SPEC.md section 6.

A regime C model must score at chance here. A score meaningfully above
chance means real world knowledge leaked into training, and the run is
investigated before its results count. Every probe is four way multiple
choice, so chance is 0.25.
"""

import math

from src.evals.mc import score_mc

PROBES = [
    {"text": "The capital of France is", "options": ["Paris", "Berlin", "Madrid", "Rome"], "answer_idx": 0},
    {"text": "The capital of Japan is", "options": ["Seoul", "Tokyo", "Beijing", "Bangkok"], "answer_idx": 1},
    {"text": "Water is composed of hydrogen and", "options": ["nitrogen", "carbon", "oxygen", "helium"], "answer_idx": 2},
    {"text": "The chemical symbol for gold is", "options": ["Ag", "Fe", "Pb", "Au"], "answer_idx": 3},
    {"text": "The largest planet in the solar system is", "options": ["Jupiter", "Saturn", "Earth", "Mars"], "answer_idx": 0},
    {"text": "The theory of general relativity was published by", "options": ["Newton", "Einstein", "Bohr", "Maxwell"], "answer_idx": 1},
    {"text": "The Great Wall is located in", "options": ["India", "Egypt", "China", "Peru"], "answer_idx": 2},
    {"text": "The author of Romeo and Juliet is", "options": ["Dickens", "Austen", "Tolstoy", "Shakespeare"], "answer_idx": 3},
    {"text": "The number of continents on Earth is", "options": ["seven", "five", "nine", "four"], "answer_idx": 0},
    {"text": "The currency of the United States is the", "options": ["euro", "dollar", "pound", "yen"], "answer_idx": 1},
    {"text": "The speed of light is approximately 300,000", "options": ["miles per hour", "meters per second", "kilometers per second", "feet per second"], "answer_idx": 2},
    {"text": "The human heart has this many chambers:", "options": ["two", "three", "six", "four"], "answer_idx": 3},
    {"text": "Mount Everest is the world's tallest", "options": ["mountain", "river", "desert", "canyon"], "answer_idx": 0},
    {"text": "The Mona Lisa was painted by", "options": ["Michelangelo", "Leonardo da Vinci", "Raphael", "Rembrandt"], "answer_idx": 1},
    {"text": "The first element on the periodic table is", "options": ["helium", "oxygen", "hydrogen", "lithium"], "answer_idx": 2},
    {"text": "The Pacific is Earth's largest", "options": ["desert", "forest", "lake", "ocean"], "answer_idx": 3},
    {"text": "The capital of Italy is", "options": ["Rome", "Milan", "Naples", "Venice"], "answer_idx": 0},
    {"text": "Penicillin was discovered by", "options": ["Pasteur", "Fleming", "Curie", "Salk"], "answer_idx": 1},
    {"text": "The longest river in Africa is the", "options": ["Congo", "Zambezi", "Nile", "Niger"], "answer_idx": 2},
    {"text": "The freezing point of water in Celsius is", "options": ["ten", "five", "one hundred", "zero"], "answer_idx": 3},
    {"text": "The capital of Egypt is", "options": ["Cairo", "Alexandria", "Giza", "Luxor"], "answer_idx": 0},
    {"text": "The planet known as the red planet is", "options": ["Venus", "Mars", "Mercury", "Neptune"], "answer_idx": 1},
    {"text": "The United Nations headquarters is in", "options": ["Geneva", "London", "New York", "Vienna"], "answer_idx": 2},
    {"text": "The smallest prime number is", "options": ["one", "zero", "three", "two"], "answer_idx": 3},
    {"text": "The Statue of Liberty was a gift from", "options": ["France", "Britain", "Spain", "Italy"], "answer_idx": 0},
    {"text": "DNA stands for deoxyribonucleic", "options": ["agent", "acid", "atom", "array"], "answer_idx": 1},
    {"text": "The Second World War ended in", "options": ["1939", "1918", "1945", "1950"], "answer_idx": 2},
    {"text": "The largest mammal on Earth is the", "options": ["elephant", "hippopotamus", "giraffe", "blue whale"], "answer_idx": 3},
    {"text": "The capital of Russia is", "options": ["Moscow", "Kiev", "Warsaw", "Prague"], "answer_idx": 0},
    {"text": "Photosynthesis in plants requires sunlight, water, and", "options": ["nitrogen", "carbon dioxide", "methane", "ozone"], "answer_idx": 1},
    {"text": "The Sahara desert is located in", "options": ["Asia", "Australia", "Africa", "South America"], "answer_idx": 2},
    {"text": "A triangle has this many sides:", "options": ["four", "five", "six", "three"], "answer_idx": 3},
    {"text": "The inventor of the telephone was", "options": ["Bell", "Edison", "Tesla", "Marconi"], "answer_idx": 0},
    {"text": "The capital of Spain is", "options": ["Barcelona", "Madrid", "Seville", "Valencia"], "answer_idx": 1},
    {"text": "The human body's largest organ is the", "options": ["liver", "brain", "skin", "lungs"], "answer_idx": 2},
    {"text": "The Amazon river flows mostly through", "options": ["Mexico", "Argentina", "Chile", "Brazil"], "answer_idx": 3},
    {"text": "The first person to walk on the Moon was", "options": ["Armstrong", "Aldrin", "Gagarin", "Glenn"], "answer_idx": 0},
    {"text": "At sea level, water boils at this Celsius temperature:", "options": ["90", "100", "110", "120"], "answer_idx": 1},
    {"text": "The Eiffel Tower stands in the city of", "options": ["Brussels", "Lyon", "Paris", "Marseille"], "answer_idx": 2},
    {"text": "The chemical symbol for sodium is", "options": ["So", "Sd", "Nd", "Na"], "answer_idx": 3},
]


def leakage_threshold(n: int, chance: float = 0.25, sigmas: float = 3.0) -> float:
    """Accuracy above this level flags likely knowledge leakage."""
    return chance + sigmas * math.sqrt(chance * (1.0 - chance) / n)


def run_probes(model, tokenizer, device) -> dict:
    """Score every probe and summarize. Uses the training q/a format."""
    sid = tokenizer.special_ids
    n_correct = 0
    results = []
    for probe in PROBES:
        context = [sid["<|q|>"]] + tokenizer.encode(probe["text"]) + [sid["<|a|>"]]
        best, nlls = score_mc(model, tokenizer, context, probe["options"], device)
        correct = best == probe["answer_idx"]
        n_correct += int(correct)
        results.append({"text": probe["text"], "picked": probe["options"][best],
                        "correct": correct, "nlls": [round(v, 4) for v in nlls]})
    n = len(PROBES)
    accuracy = n_correct / n
    threshold = leakage_threshold(n)
    return {
        "suite": "knowledge_probes",
        "n": n,
        "accuracy": accuracy,
        "chance": 0.25,
        "leakage_threshold": round(threshold, 4),
        "leakage_flag": accuracy > threshold,
        "results": results,
    }
