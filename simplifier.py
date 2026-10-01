import json
import re
import html
from pathlib import Path

from text_analyzer import analyze_text, highlight_jargon

BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "jargon_dictionary.json", "r", encoding="utf-8") as f:
    JARGON = json.load(f)

# FLAN-T5 is optional. The application always has a local fallback,
# so it can run without downloading a large model.
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
except Exception:
    torch = None
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None

MODEL_NAME = "google/flan-t5-small"


def _load_model():
    if AutoTokenizer is None or AutoModelForSeq2SeqLM is None or torch is None:
        return None, None
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        return tokenizer, model
    except Exception:
        return None, None


try:
    import streamlit as st

    @st.cache_resource(show_spinner=False)
    def load_model():
        return _load_model()
except Exception:
    def load_model():
        return _load_model()


def _generate(prompt, max_new_tokens=180):
    tokenizer, model = load_model()
    if tokenizer is None or model is None:
        return None
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            output = model.generate(
                **inputs, max_new_tokens=max_new_tokens, num_beams=4, early_stopping=True
            )
        return tokenizer.decode(output[0], skip_special_tokens=True).strip()
    except Exception:
        return None


def rule_based_beginner(text):
    replacements = {
        "utilize": "use", "utilizes": "uses", "approximately": "about",
        "demonstrate": "show", "demonstrates": "shows", "facilitate": "help",
        "facilitates": "helps", "subsequently": "later", "numerous": "many",
        "commence": "start", "terminate": "end", "obtain": "get",
        "assistance": "help", "methodology": "method", "implementation": "building and using",
        "computation": "calculation", "comprehensive": "complete", "configuration": "setup",
        "optimization": "improvement", "parameters": "settings", "predominantly": "mostly",
        "individuals": "people",
    }
    result = text
    for old, new in replacements.items():
        result = re.sub(r"\b" + re.escape(old) + r"\b", new, result, flags=re.I)
    for term, data in JARGON.items():
        result = re.sub(r"(?<!\w)" + re.escape(term) + r"(?!\w)", data["full_form"], result, flags=re.I)
    # Avoid awkward duplication when the source already contains the full form.
    for term, data in JARGON.items():
        full = re.escape(data["full_form"])
        result = re.sub(rf"\b{full}\s*\(\s*{full}\s*\)", data["full_form"], result, flags=re.I)
    return (
        "Here is the same idea in simpler words:\n\n" + result +
        "\n\n💡 Think of it as taking a difficult explanation and rewriting it using everyday words."
    )


def rule_based_intermediate(text):
    result = text
    for term, data in JARGON.items():
        result = re.sub(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            lambda m, t=term, d=data: f"{m.group(0)} ({d['simple']})",
            result,
            flags=re.I,
        )
    # If the source already has "Full Form (ACRONYM)", add the simple meaning
    # inside the existing parentheses instead of nesting another explanation.
    for term, data in JARGON.items():
        full = re.escape(data["full_form"])
        simple = data["simple"]
        result = re.sub(
            rf"({full}\s*\(\s*{re.escape(term)})\s*\([^)]*\)(\s*\))",
            lambda m, s=simple: f"{m.group(1)} — {s}{m.group(2)}",
            result, flags=re.I
        )
    return result


def generate_levels(text, analysis):
    beginner_prompt = f"""Explain the following technical or academic text like you are explaining it to a 10-year-old.
Keep the original meaning, use very simple English, explain difficult terms, add one short everyday analogy when useful, do not invent facts, and keep it concise.

Text:\n{text}"""
    intermediate_prompt = f"""Rewrite the following technical or academic text for a college student who understands basic concepts but may not know advanced jargon.
Preserve the meaning, use simpler vocabulary, keep important technical concepts, expand important acronyms, do not add unsupported facts, and keep it concise.

Text:\n{text}"""

    beginner = _generate(beginner_prompt)
    intermediate = _generate(intermediate_prompt)
    if not beginner:
        beginner = rule_based_beginner(text)
    if not intermediate:
        intermediate = rule_based_intermediate(text)

    b = analyze_text(beginner)
    i = analyze_text(intermediate)
    metrics = {
        "Metric": ["Word count", "Average sentence length", "Syllables", "Long words"],
        "Original": [analysis["word_count"], round(analysis["avg_sentence_length"], 1), analysis["syllables"], analysis["long_word_count"]],
        "Beginner": [b["word_count"], round(b["avg_sentence_length"], 1), b["syllables"], b["long_word_count"]],
        "Intermediate": [i["word_count"], round(i["avg_sentence_length"], 1), i["syllables"], i["long_word_count"]],
    }
    return {
        "beginner": beginner,
        "intermediate": intermediate,
        "advanced": highlight_jargon(html.escape(text)),
        "metrics": metrics,
    }
