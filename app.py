import streamlit as st
from dotenv import load_dotenv
import os
import html

from translator import get_video_id, get_transcript, translate_to_bangla


# =========================================================
# Configuration
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="YouTube Bangla Translator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# API Key Check
# =========================================================

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY পাওয়া যায়নি। আপনার .env file check করুন।")
    st.stop()


# =========================================================
# Session State Initialization
# =========================================================

if "url_input" not in st.session_state:
    st.session_state.url_input = ""


def clear_text():
    st.session_state.url_input = ""


# =========================================================
# Custom CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans Bengali', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(255, 0, 80, 0.13),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(90, 70, 255, 0.14),
            transparent 30%
        ),
        #080b14;
    color: #ffffff;
}

#MainMenu, header, footer {
    visibility: hidden;
}

.block-container {
    max-width: 850px;
    padding-top: 50px;
    padding-bottom: 60px;
}

.hero {
    text-align: center;
    margin-bottom: 30px;
}

.hero h1 {
    margin: 0;
    font-size: clamp(38px, 5vw, 65px);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #ffffff 20%, #cfd5ff 50%, #ff5c82 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    margin-top: 18px;
    color: #929bb2;
    font-size: 16px;
    line-height: 1.6;
}

.input-card {
    margin-top: 20px;
    padding: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    backdrop-filter: blur(20px);
}

.stTextInput > div > div {
    background: #111522 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}

.stTextInput input {
    color: white !important;
    font-size: 16px !important;
    padding: 15px !important;
}

.stTextInput input::placeholder {
    color: #687188 !important;
}

/* Primary translate button style */
div[data-testid="stButton"] > button[kind="primary"] {
    width: 100%;
    padding: 14px 20px;
    border: none !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #ff003c, #ff416c) !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(255,0,60,0.35);
}

/* Secondary clear button style */
div[data-testid="stButton"] > button[kind="secondary"] {
    width: 100%;
    padding: 14px 20px;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
    color: #aeb6ca !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
}

.result-container {
    margin-top: 40px;
    padding: 25px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
}

.result-title {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 15px;
}

.translation {
    padding: 22px;
    background: #0d111c;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    color: #e7eaf2;
    font-family: 'Noto Sans Bengali', 'Inter', sans-serif;
    font-size: 16px;
    line-height: 1.8;
    white-space: pre-wrap;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# Hero Section
# =========================================================

st.markdown("""
<div class="hero">
    <h1>
        YouTube থেকে<br>
        বাংলায় বুঝুন
    </h1>
    <p>
        যেকোনো ভাষার YouTube ভিডিওর transcript সংগ্রহ করে সহজ ও natural বাংলায় অনুবাদ করুন।
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# Input & Action Buttons
# =========================================================

st.markdown('<div class="input-card">', unsafe_allow_html=True)

video_input = st.text_input(
    "YouTube URL",
    placeholder="Paste YouTube video link অথবা Video ID...",
    label_visibility="collapsed",
    key="url_input"
)

col1, col2 = st.columns([3, 1])

with col1:
    translate = st.button("🚀 Translate to Bangla", type="primary", use_container_width=True)

with col2:
    st.button("🗑️ Clear", type="secondary", on_click=clear_text, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# Translation Logic
# =========================================================

if translate:
    if not video_input.strip():
        st.warning("⚠️ প্রথমে একটি YouTube link অথবা Video ID দিন।")
    else:
        try:
            with st.spinner("🔎 YouTube video খোঁজা হচ্ছে..."):
                video_id = get_video_id(video_input)

            with st.spinner("📝 Video transcript সংগ্রহ করা হচ্ছে..."):
                transcript, language = get_transcript(video_id)

            with st.spinner("🤖 AI বাংলা translation তৈরি করছে..."):
                bangla_text = translate_to_bangla(transcript)

            # Result Display
            st.markdown("""
            <div class="result-container">
                <div class="result-title">🇧🇩 বাংলা অনুবাদ</div>
            """, unsafe_allow_html=True)

            st.markdown(
                f"""
                <div style="color:#7f899f; font-size:13px; margin-bottom:15px;">
                    Original language: <b style="color:#c8cedc;">{html.escape(str(language))}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            safe_text = html.escape(bangla_text)
            st.markdown(
                f"""
                <div class="translation">{safe_text}</div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download বাংলা Translation",
                data=bangla_text,
                file_name="bangla_translation.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"❌ Translation করা যায়নি\n\n{str(e)}")