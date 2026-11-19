import streamlit as st
import json
import os
import io
from gtts import gTTS
import speech_recognition as sr
import streamlit.components.v1 as components

# --- UI & JS Feedback ---
st.set_page_config(page_title="English Tutor", layout="centered")

# JavaScript for Vibration and Sound
feedback_js = """
<script>
function triggerFeedback(type) {
    // Vibration: 200ms for wrong, 100ms for correct
    if (navigator.vibrate) {
        if (type === 'wrong') navigator.vibrate(300);
        else navigator.vibrate(100);
    }
    // Sound: Web Audio API (works without external files)
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    osc.connect(ctx.destination);
    osc.frequency.value = (type === 'correct') ? 880 : 220;
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
}
</script>
"""
st.markdown(feedback_js, unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 60px; font-weight: bold; background-color: #800020; color: white; border: none; font-size: 18px; }
    .stButton>button:hover { background-color: #5d0017; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Data Handling ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

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
st.write(f"**Pronunciation:** {current_item['te']}")
st.write(f"**Meaning:** {current_item['meaning']}")

if st.button("🔊 Listen"):
    tts = gTTS(text=current_item['en'], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp); fp.seek(0)
    st.audio(fp, format="audio/mp3")

# --- Practice ---
st.subheader("🎤 Practice")
audio_input = st.audio_input("Record", key=f"audio_{st.session_state.idx}")

if audio_input:
    st.info("Analyzing...")
    with open("temp.wav", "wb") as f: f.write(audio_input.read())
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio_data).lower()
            target_text = current_item['en'].lower().strip("?.!")
            
            # Logic for color feedback
            target_words = target_text.split()
            user_words = recognized_text.split()
            result_html = "You said: "
            is_correct = True
            for i in range(max(len(target_words), len(user_words))):
                u = user_words[i] if i < len(user_words) else None
                t = target_words[i] if i < len(target_words) else None
                if u == t: result_html += f"<span style='color:green'>{u}</span> "
                else: 
                    is_correct = False
                    result_html += f"<span style='color:red'>{u if u else '[missed]'}</span> "
            st.markdown(result_html, unsafe_allow_html=True)
            
            # Trigger JS feedback
            if is_correct: 
                st.success("✅ Perfect!")
                st.markdown(f"<script>triggerFeedback('correct')</script>", unsafe_allow_html=True)
            else: 
                st.warning("⚠️ Try again!")
                st.markdown(f"<script>triggerFeedback('wrong')</script>", unsafe_allow_html=True)
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
