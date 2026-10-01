import json
import re
from pathlib import Path

try:
    import textstat
except ImportError:
    textstat = None

BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "jargon_dictionary.json", "r", encoding="utf-8") as f:
    JARGON = json.load(f)


def _syllable_count(text: str) -> int:
    if textstat is not None:
        return textstat.syllable_count(text)
    total = 0
    for word in re.findall(r"[A-Za-z]+", text.lower()):
        groups = re.findall(r"[aeiouy]+", word)
        count = max(1, len(groups))
        if word.endswith("e") and count > 1:
            count -= 1
        total += count
    return total


def _reading_ease(text: str) -> float:
    if textstat is not None:
        return float(textstat.flesch_reading_ease(text))
    words = re.findall(r"\b[A-Za-z]+(?:['-][A-Za-z]+)*\b", text)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    if not words:
        return 0.0
    syllables = _syllable_count(text)
    return 206.835 - 1.015 * (len(words) / max(len(sentences), 1)) - 84.6 * (syllables / len(words))


def analyze_text(text: str):
    text = text.strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    words = re.findall(r"\b[\w'-]+\b", text)

    matched = []
    lowered = text.lower()
    for term in sorted(JARGON.keys(), key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
        if re.search(pattern, lowered):
            matched.append(term)

    syllables = _syllable_count(text)
    readability_score = _reading_ease(text)
    if readability_score >= 70:
        readability = "Easy"
    elif readability_score >= 50:
        readability = "Moderate"
    else:
        readability = "Difficult"

    avg_sentence_length = len(words) / max(len(sentences), 1)
    long_word_count = sum(
        1 for word in words if len(re.findall(r"[aeiouy]+", word.lower())) >= 3
    )

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": avg_sentence_length,
        "syllables": syllables,
        "long_word_count": long_word_count,
        "readability": readability,
        "matched_terms": matched,
    }


def highlight_jargon(text: str):
    result = text
    for term in sorted(JARGON.keys(), key=len, reverse=True):
        data = JARGON[term]
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        replacement = (
            f'<span title="{data["simple"]}" '
            f'style="background:#fff3a3;padding:2px 5px;border-radius:4px;">'
            f'{term} <small>({data["simple"]})</small></span>'
        )
        result = pattern.sub(replacement, result)
    return result
