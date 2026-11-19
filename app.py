import streamlit as st
import json
import os
import io
from gtts import gTTS
import speech_recognition as sr

# --- UI Configuration ---
st.set_page_config(page_title="English Tutor", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 60px; font-weight: bold; background-color: #800020; color: white; border: none; font-size: 18px; }
    .stButton>button:hover { background-color: #5d0017; color: white; }
    .stAudioInput { font-size: 24px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Data Handling ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

st.title("📚 English Tutor")

# --- Logic for Level/Sentence ---
selected_level = st.selectbox("🎯 Select Level", list(data.keys()))
level_sentences = data[selected_level]

if 'last_level' not in st.session_state: st.session_state.last_level = selected_level
if 'idx' not in st.session_state: st.session_state.idx = 0

if st.session_state.last_level != selected_level:
    st.session_state.idx = 0
    st.session_state.last_level = selected_level

if st.session_state.idx >= len(level_sentences): st.session_state.idx = 0
current_item = level_sentences[st.session_state.idx]

# --- Display ---
st.progress((st.session_state.idx + 1) / len(level_sentences))
st.write(f"**Sentence {st.session_state.idx + 1} / {len(level_sentences)}**")
st.markdown(f"### {current_item['en']}")
st.write(f"**Pronunciation:** {current_item['te']}")
st.write(f"**Meaning:** {current_item['meaning']}")

# --- Listen ---
if st.button("🔊 Listen"):
    tts = gTTS(text=current_item['en'], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp); fp.seek(0)
    st.audio(fp, format="audio/mp3")

# --- Practice ---
st.subheader("🎤 Practice")
# key=str(st.session_state.idx) forces the component to reload (be fresh) when the sentence changes
audio_input = st.audio_input("Record your voice", key=f"audio_{st.session_state.idx}")

if audio_input:
    st.info("Analyzing...")
    with open("temp.wav", "wb") as f: f.write(audio_input.read())
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio_data).lower()
            target_text = current_item['en'].lower().strip("?.!")

            target_words = target_text.split()
            user_words = recognized_text.split()

            result_html = "You said: "
            is_correct = True

            # Compare up to the length of the longer list
            for i in range(max(len(target_words), len(user_words))):
                user_word = user_words[i] if i < len(user_words) else None
                target_word = target_words[i] if i < len(target_words) else None

                if user_word == target_word:
                    result_html += f"<span style='color:green'>{user_word}</span> "
                else:
                    is_correct = False
                    if user_word:
                        result_html += f"<span style='color:red'>{user_word}</span> "
                    else:
                        result_html += f"<span style='color:red'>[missing]</span> "

            st.markdown(result_html, unsafe_allow_html=True)

            if is_correct: st.success("✅ Perfect!")
            else: st.warning("⚠️ Try again!")
        except: st.error("Couldn't hear you clearly.")
    if os.path.exists("temp.wav"): os.remove("temp.wav")

# --- Navigation ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Previous"):
        if st.session_state.idx > 0:
            st.session_state.idx -= 1
            st.rerun()
with col2:
    if st.button("➡️ Next"):
        if st.session_state.idx < len(level_sentences) - 1:
            st.session_state.idx += 1
            st.rerun()
