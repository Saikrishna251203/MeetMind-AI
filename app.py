from dotenv import load_dotenv
import os
load_dotenv()
import streamlit as st
from groq import Groq
import re
import time

# CONFIG
st.set_page_config(page_title="MeetMind AI", layout="wide")

# API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# SESSION STATE
if "text" not in st.session_state:
    st.session_state.text = ""

if "output" not in st.session_state:
    st.session_state.output = ""

# CUSTOM CSS
st.markdown("""
<style>
body {background-color: #0f172a; color: white;}
.stTextArea textarea {background-color: #1e293b; color: white;}
.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
}
.highlight {color: #38bdf8; font-weight: bold;}
h4 {color: #facc15;}
</style>
""", unsafe_allow_html=True)

# TITLE
st.title("🚀 MeetMind AI")
st.markdown("Turn meetings into structured insights instantly")

# LAYOUT
col1, col2 = st.columns(2)

# INPUT SIDE
with col1:
    st.subheader("📥 Input")

    # SAMPLE BUTTON
    if st.button("Use Sample"):
        st.session_state.text = "Team discussed project deadline. Rahul will complete backend. Deadline April 20."

    # CLEAR BUTTON
    if st.button("Clear"):
        st.session_state.text = ""

    # WORD COUNT
    text = st.text_area("Paste Meeting Transcript", height=250, value=st.session_state.text, key="input_text_area")
    st.session_state.text = text  # keep session state in sync
    st.metric("Words", len(text.split()))

    tone = st.selectbox("Choose Style", ["Professional", "Simple", "Detailed"])

    generate = st.button("✨ Generate Insights")

# OUTPUT SIDE
with col2:
    st.subheader("📤 Output")

    if generate and text:
        with st.spinner("Analyzing..."):

            # PROGRESS BAR
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            prompt = f"""
            Analyze meeting and give clearly:

            SUMMARY:
            KEY DECISIONS:
            ACTION ITEMS:

            Style: {tone}

            Meeting:
            {text}
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.session_state.output = response.choices[0].message.content

    # DISPLAY OUTPUT (PERSISTENT)
    if st.session_state.output:

        st.success("Analysis Complete ✅")

        output = st.session_state.output

        # KEYWORD HIGHLIGHT
        keywords = ["deadline", "decision", "important"]
        for word in keywords:
            output = re.sub(f"(?i){word}", f"<span class='highlight'>{word}</span>", output)

        # SPLIT SECTIONS
        sections = output.split("\n")

        summary, decisions, actions = "", "", ""
        current = None

        for line in sections:
            if "summary" in line.lower():
                current = "summary"
            elif "decision" in line.lower():
                current = "decisions"
            elif "action" in line.lower():
                current = "actions"
            else:
                if current == "summary":
                    summary += line + "\n"
                elif current == "decisions":
                    decisions += line + "\n"
                elif current == "actions":
                    actions += line + "\n"

        # CARDS
        st.markdown(f"<div class='card'><h4>📝 Summary</h4>{summary}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><h4>📌 Key Decisions</h4>{decisions}</div>", unsafe_allow_html=True)

        # CHECKLIST
        st.markdown("<div class='card'><h4>✅ Action Items</h4>", unsafe_allow_html=True)
        for i, item in enumerate(actions.split("\n")):
            if item.strip():
                st.checkbox(item, key=f"action_{i}")
        st.markdown("</div>", unsafe_allow_html=True)

        # RAW OUTPUT
        st.code(output)

        # DOWNLOAD
        st.download_button("📥 Download Output", output, file_name="meeting_summary.txt")