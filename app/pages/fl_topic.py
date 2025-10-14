import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
from openai import OpenAI

# ------------------------------------
# 🧠 INITIAL SETUP
# ------------------------------------
st.set_page_config(page_title="Finance Tutor", layout="wide")

if "user_name" not in st.session_state:
    st.session_state.user_name = "Lohith"
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ("Finance Fundamentals", 0, "Introduction to Finance")
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "english"  # english, telugu, hindi, tamil, kannada

# ------------------------------------
# 🌐 TRANSLATION DICTIONARY
# ------------------------------------
translations = {
    "english": {
        "welcome": "Welcome",
        "learning_material": "Learning Material",
        "topic_intro": "This is where the learning content for this topic will appear — videos, notes, or quizzes.",
        "take_quiz": "Take Quiz",
        "quiz_completed": "Quiz completed! You can proceed to the next topic.",
        "next": "Next",
        "previous": "Previous",
        "back": "Back to Dashboard",
        "speak_button": "🔊 Listen to Lesson",
        "mic_button": "🎙️ Speak to Chatbot",
    },
    "తెలుగు (Telugu)": {
        "welcome": "స్వాగతం",
        "learning_material": "పాఠ్యాంశం",
        "topic_intro": "ఈ అంశానికి సంబంధించిన వీడియోలు, గమనికలు లేదా క్విజ్‌లు ఇక్కడ కనిపిస్తాయి.",
        "take_quiz": "క్విజ్ ప్రారంభించండి",
        "quiz_completed": "క్విజ్ పూర్తయింది! తదుపరి అంశానికి వెళ్ళవచ్చు.",
        "next": "తర్వాత",
        "previous": "మునుపటి",
        "back": "డాష్‌బోర్డ్‌కి తిరిగి",
        "speak_button": "🔊 పాఠాన్ని వినండి",
        "mic_button": "🎙️ బాట్‌తో మాట్లాడండి",
    },
    "हिंदी (Hindi)": {
        "welcome": "स्वागत है",
        "learning_material": "अध्ययन सामग्री",
        "topic_intro": "यहाँ इस विषय की सामग्री दिखाई देगी — वीडियो, नोट्स या क्विज़।",
        "take_quiz": "क्विज़ शुरू करें",
        "quiz_completed": "क्विज़ पूरा हुआ! अब आप अगले विषय पर जा सकते हैं।",
        "next": "अगला",
        "previous": "पिछला",
        "back": "डैशबोर्ड पर वापस जाएं",
        "speak_button": "🔊 पाठ सुनें",
        "mic_button": "🎙️ चैटबॉट से बात करें",
    },
    "தமிழ் (Tamil)": {
        "welcome": "வரவேற்கிறோம்",
        "learning_material": "கற்றல் உள்ளடக்கம்",
        "topic_intro": "இந்த தலைப்புக்கான வீடியோக்கள், குறிப்புகள் அல்லது வினாடி வினா இங்கே தோன்றும்.",
        "take_quiz": "வினாடி வினா தொடங்கவும்",
        "quiz_completed": "வினாடி வினா முடிந்தது! அடுத்த தலைப்புக்குச் செல்லலாம்.",
        "next": "அடுத்தது",
        "previous": "முந்தையது",
        "back": "டாஷ்போர்டுக்கு திரும்பவும்",
        "speak_button": "🔊 பாடத்தை கேட்கவும்",
        "mic_button": "🎙️ போட் உடன் பேசவும்",
    },
    "ಕನ್ನಡ (Kannada)": {
        "welcome": "ಸ್ವಾಗತ",
        "learning_material": "ಅಧ್ಯಯನ ವಿಷಯ",
        "topic_intro": "ಈ ವಿಷಯಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ವೀಡಿಯೊಗಳು, ಟಿಪ್ಪಣಿಗಳು ಅಥವಾ ಕ್ವಿಜ್‌ಗಳು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.",
        "take_quiz": "ಕ್ವಿಜ್ ಪ್ರಾರಂಭಿಸಿ",
        "quiz_completed": "ಕ್ವಿಜ್ ಪೂರ್ಣಗೊಂಡಿದೆ! ಮುಂದಿನ ವಿಷಯಕ್ಕೆ ಹೋಗಬಹುದು.",
        "next": "ಮುಂದಿನದು",
        "previous": "ಹಿಂದಿನದು",
        "back": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",
        "speak_button": "🔊 ಪಾಠವನ್ನು ಕೇಳಿ",
        "mic_button": "🎙️ ಬಾಟ್‌ನೊಂದಿಗೆ ಮಾತನಾಡಿ",
    }
}

# ------------------------------------
# 🎧 TTS FUNCTION
# ------------------------------------
def get_tts_lang(language):
    mapping = {
        "english": "en",
        "తెలుగు (Telugu)": "te",
        "हिंदी (Hindi)": "hi",
        "தமிழ் (Tamil)": "ta",
        "ಕನ್ನಡ (Kannada)": "kn",
    }
    return mapping.get(language, "en")

def speak_text(text, language):
    """Generate voice from text."""
    lang_code = get_tts_lang(language)
    tts = gTTS(text=text, lang=lang_code)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/mp3")

# ------------------------------------
# 📘 PAGE HEADER
# ------------------------------------
chapter_name, topic_index, topic_title = st.session_state.selected_topic
t = translations[st.session_state.language]

st.markdown(
    f"""
    <div style="background-color:#0f1724; padding:18px; border-radius:10px; color:white;">
        <h2>👋 {t['welcome']}, {st.session_state.user_name}!</h2>
        <p>📘 {chapter_name} | 🧩 {topic_title}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------
# 📚 LEARNING MATERIAL
# ------------------------------------
st.markdown(f"### 📖 {t['learning_material']}")
st.info(t["topic_intro"])

col1, col2 = st.columns([1, 1])
with col1:
    if st.button(t["speak_button"], key="speaker_button"):
        speak_text(t["topic_intro"], st.session_state.language)
with col2:
    st.write("")  # spacing

# ------------------------------------
# 🧠 QUIZ SECTION
# ------------------------------------
st.write("---")
st.subheader("🧠 " + t["take_quiz"])

if not st.session_state.quiz_completed:
    if st.button("🚀 Start Quiz"):
        with st.expander("📋 Quiz", expanded=True):
            answer = st.radio(
                "What is the main goal of finance?",
                ["A) Spending money", "B) Managing money efficiently", "C) Avoiding all investments"],
                key="quiz_radio"
            )
            if st.button("✅ Submit Quiz"):
                if answer == "B) Managing money efficiently":
                    st.session_state.quiz_completed = True
                    st.success(t["quiz_completed"])
                else:
                    st.error("❌ Try again.")
else:
    st.success(t["quiz_completed"])

# ------------------------------------
# 💬 CHATBOT WITH VOICE (MIC + SPEAKER in input ribbon)
# ------------------------------------
st.write("---")
st.markdown("### 🤖 Chatbot Assistant")

# Chat history display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Chat input ribbon with mic and speaker ---
chat_col1, chat_col2, chat_col3 = st.columns([8, 1, 1])

# Text input box
with chat_col1:
    user_input = st.chat_input("Ask your question...")

# Mic button
with chat_col2:
    mic_audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="🛑",
        just_once=True,
        use_container_width=True,
        key="chat_mic",
    )

# Speaker button
with chat_col3:
    if st.button("🔊", key="chat_speaker"):
        if st.session_state.messages:
            speak_text(st.session_state.messages[-1]["content"], st.session_state.language)
        else:
            st.warning("No response to speak yet.")

# --- Process input or voice ---
if mic_audio:
    st.audio(mic_audio["bytes"])
    st.success("🎙️ Voice captured successfully!")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = f"That's an insightful question about {topic_title}!"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ------------------------------------
# 🚪 NAVIGATION
# ------------------------------------
st.write("---")
col1, col2, col3 = st.columns([1, 1, 2])
col1.button(f"⬅️ {t['previous']}")
col2.button(f"➡️ {t['next']}", disabled=not st.session_state.quiz_completed)
col3.button(f"🏠 {t['back']}")


#To Do
# reply = f"That's a great question about {topic_title}! Here’s a short explanation..."
# with something like:

# python
# Copy code
# client = OpenAI(api_key="YOUR_KEY")
# resp = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=st.session_state.messages
# )
# reply = resp.choices[0].message.content
