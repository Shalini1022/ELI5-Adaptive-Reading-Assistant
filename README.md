# ELI5 Adaptive Reading Assistant

A beginner-friendly NLP application that converts dense academic or technical text into three reading levels:

- **Beginner:** simple wording with an everyday explanation
- **Intermediate:** simplified jargon while preserving important concepts
- **Advanced:** original text with inline definitions

## How it works

1. `text_analyzer.py` analyzes words, sentences, readability, syllables, long words, and dictionary terms.
2. `simplifier.py` creates the three levels and calculates comparison metrics.
3. `jargon_dictionary.json` provides explanations for common technical terms.
4. The project has a **local rule-based fallback**, so it can run without downloading an AI model.
5. FLAN-T5-small is optional. If `transformers` and `torch` are installed and the model is available, the app can use them for generated Beginner/Intermediate explanations.

## Recommended Python

Python **3.10–3.14** is suitable for the lightweight default setup.

## Run on Windows

### Option 1 — easiest
Double-click `run_windows.bat`.

### Option 2 — VS Code / PowerShell

```powershell
cd "path\to\ELI5_Adaptive_Reading_Assistant"
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the `http://localhost:8501` address shown in the terminal.

## Important

The ZIP intentionally does **not** include a virtual environment. A `venv` is machine-specific and makes the project unnecessarily large. The included batch file creates it automatically.
