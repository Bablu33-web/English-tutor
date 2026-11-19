import streamlit as st
import json
import os
import io
from gtts import gTTS
import speech_recognition as sr

# --- UI Configuration ---
st.set_page_config(page_title="English Tutor", layout="centered")

# --- Data Handling ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

st.title("📚 English Tutor")

selected_level = st.selectbox("🎯 Select Level", list(data.keys()))
level_sentences = data[selected_level]

if 'idx' not in st.session_state: st.session_state.idx = 0
if st.session_state.idx >= len(level_sentences): st.session_state.idx = 0
current_item = level_sentences[st.session_state.idx]

# --- Display ---
progress = (st.session_state.idx + 1) / len(level_sentences)
st.progress(progress)
st.write(f"**Sentence {st.session_state.idx + 1} / {len(level_sentences)}**")
st.markdown(f"### {current_item['en']}")
# Correct labels
st.write(f"**Pronunciation:** {current_item['te']}")
st.write(f"**Meaning:** {current_item['meaning']}")

# --- Actions ---
if st.button("🔊 Listen"):
    tts = gTTS(text=current_item['en'], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp); fp.seek(0)
    st.audio(fp, format="audio/mp3")

# --- Practice ---
audio_input = st.audio_input("🎤 Record your voice")
if audio_input:
    st.info("Analyzing...")
    with open("temp.wav", "wb") as f: f.write(audio_input.read())
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio_data).lower()
            if recognized_text == current_item['en'].lower().strip("?.!"):
                st.success("✅ Perfect!")
            else:
                st.warning("⚠️ Try again!")
        except: st.error("Couldn't hear you clearly.")
    if os.path.exists("temp.wav"): os.remove("temp.wav")

if st.button("➡️ Next Sentence"):
    st.session_state.idx = (st.session_state.idx + 1) % len(level_sentences)
    st.rerun()
