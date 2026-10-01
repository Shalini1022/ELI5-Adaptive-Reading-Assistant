import streamlit as st
from text_analyzer import analyze_text
from simplifier import generate_levels

st.set_page_config(page_title="ELI5 Adaptive Reading Assistant", page_icon="📚", layout="wide")
st.title("📚 ELI5 Adaptive Reading Assistant")
st.caption("Turn dense academic or technical text into three adaptive reading levels.")
st.info("Paste a technical or academic paragraph. The app detects jargon and creates Beginner, Intermediate, and Advanced versions.")

text = st.text_area(
    "Paste your complex text here", height=220,
    placeholder="Example: Natural Language Processing (NLP) enables computational systems to analyze and interpret human language."
)
col1, col2 = st.columns([1, 1])
with col1:
    run = st.button("✨ Simplify Text", type="primary", use_container_width=True)
with col2:
    show_analysis = st.checkbox("Show NLP analysis", value=True)

if run:
    if not text.strip():
        st.warning("Please paste some text first.")
        st.stop()
    with st.spinner("Analyzing text and generating reading levels..."):
        analysis = analyze_text(text)
        levels = generate_levels(text, analysis)

    st.subheader("📖 Reading Levels")
    beginner, intermediate, advanced = st.tabs(["🟢 Beginner", "🟡 Intermediate", "🔵 Advanced"])
    with beginner:
        st.markdown("### Beginner — Analogy-Driven")
        st.write(levels["beginner"])
        st.caption("Uses simple vocabulary and an everyday explanation.")
    with intermediate:
        st.markdown("### Intermediate — Simplified Jargon")
        st.write(levels["intermediate"])
        st.caption("Keeps important concepts while explaining difficult terms.")
    with advanced:
        st.markdown("### Advanced — Original + Definitions")
        st.markdown(levels["advanced"], unsafe_allow_html=True)
        st.caption("Keeps the original text and adds definitions for detected terms.")

    if show_analysis:
        st.divider()
        st.subheader("📊 NLP Text Analysis")
        a, b, c, d = st.columns(4)
        a.metric("Words", analysis["word_count"])
        b.metric("Sentences", analysis["sentence_count"])
        c.metric("Avg. sentence length", f'{analysis["avg_sentence_length"]:.1f}')
        d.metric("Syllables", analysis["syllables"])
        e, f, g = st.columns(3)
        e.metric("Long words", analysis["long_word_count"])
        f.metric("Readability", analysis["readability"])
        f.caption("Approximate Flesch reading ease")
        g.metric("Detected terms", len(analysis["matched_terms"]))
        st.write("**Detected jargon / acronyms:**")
        st.write(", ".join(analysis["matched_terms"]) if analysis["matched_terms"] else "No terms from the built-in dictionary were detected.")
        st.write("**Before → After metrics**")
        st.table(levels["metrics"])

st.divider()
st.caption("Built with Python • Streamlit • NLP rules • Optional FLAN-T5-small • TextStat • Custom jargon dictionary")
