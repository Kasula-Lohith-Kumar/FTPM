import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
from openai import OpenAI
from app.pages import fl_config

# ------------------------------------
# 🧠 INITIAL SETUP
# ------------------------------------
st.set_page_config(page_title="Finance Tutor", layout="wide")

# Ensure required state variables are initialized (defensive programming)
if "user_name" not in st.session_state:
    st.session_state.user_name = "Lohith"
if "selected_topic" not in st.session_state:
    # Default topic structure: (canonical_section_name, topic_index, localized_topic_name)
    st.session_state.selected_topic = ("Finance Fundamentals", 0, "Introduction to Finance")
if "canon_topic_index" not in st.session_state:
    # Default index structure: (section_index, topic_index)
    st.session_state.canon_topic_index = (0, 0) 
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "English"  # Must match a key in fl_config.translations

# ------------------------------------
# 🎧 TTS FUNCTION
# ------------------------------------
def get_tts_lang(language):
    """Maps the display language name to the gTTS language code."""
    mapping = {
        "English": "en",
        "తెలుగు (Telugu)": "te",
        "हिंदी (Hindi)": "hi",
        "தமிழ் (Tamil)": "ta",
        "ಕನ್ನಡ (Kannada)": "kn",
    }
    return mapping.get(language, "en")

def speak_text(text, language):
    """Generate voice from text."""
    lang_code = get_tts_lang(language)
    try:
        tts = gTTS(text=text, lang=lang_code)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"Error generating audio: {e}")

# ------------------------------------
# 📘 PAGE HEADER & LANGUAGE LOGIC
# ------------------------------------
# Initial load of language/translations
lang = st.session_state.language
t = fl_config.translations[lang]
chapter_name, topic_index, topic_title = st.session_state.selected_topic

st.markdown(
    f"""
    <div style="background-color:#0f1724; padding:18px; border-radius:10px; color:white;">
        <h2>👋 {t['welcome']}, {st.session_state.user_name}!</h2>
        <p>📘 {st.session_state.selected_topic[0]} | 🧩 {st.session_state.selected_topic[2]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- LANGUAGE SELECTION ---
prev_lang = st.session_state.language
st.markdown(f"### {fl_config.translations[prev_lang]['choose_language']}")

language = st.selectbox(
    "",
    options=list(fl_config.translations.keys()),
    index=list(fl_config.translations.keys()).index(prev_lang),
    key="language_selector",
)

# ⭐ FIX: Update selected_topic state immediately before rerunning ⭐
if language != prev_lang:
    st.session_state.language = language
    new_lang = st.session_state.language
    
    # Get canonical index set in financial_literacy.py (s_index, i)
    s_index, i = st.session_state.canon_topic_index

    # 1. Get the list of localized section names for the new language
    localized_section_list = list(fl_config.topics_language[new_lang].keys())
    
    # 2. Get the localized section name using the canonical index
    # We defensively use min() to handle potential length mismatches, 
    # though ideally the structure is consistent.
    if s_index < len(localized_section_list):
        localized_section_name = localized_section_list[s_index]
    else:
        # Fallback to current (likely English) name if index is out of bounds
        localized_section_name = st.session_state.selected_topic[0] 

    # 3. Get the list of localized topic names for that section
    localized_topic_list = fl_config.topics_language[new_lang].get(localized_section_name, [])

    # 4. Get the localized topic title using the canonical topic index
    if i < len(localized_topic_list):
        localized_topic_title = localized_topic_list[i]
    else:
        # Fallback to current topic title if index is out of bounds
        localized_topic_title = st.session_state.selected_topic[2] 

    # 5. Update st.session_state.selected_topic with the new localized strings
    st.session_state.selected_topic = (
        localized_section_name,   # Localized Section Name
        i,                        # Topic Index (canonical)
        localized_topic_title     # Localized Topic Title
    )

    # st.rerun() executes after all state updates in this block are complete, 
    # so the new state will be used on the next run.
    st.rerun()

# Reload current language variables after potential change
lang = st.session_state.language
t = fl_config.translations[lang]
chapter_name, topic_index, topic_title = st.session_state.selected_topic # Re-unpack updated state

# ------------------------------------
# 📚 LEARNING MATERIAL
# ------------------------------------
st.markdown(f"### 📖 {t['learning_material']}")
st.info(f"**{topic_title}:** " + t["topic_intro"])

col1, col2 = st.columns([1, 1])
with col1:
    if st.button(t["speak_button"], key="speaker_button"):
        # The text spoken should be the learning material content, 
        # but for this demo, we'll use the topic_intro string.
        speak_text(f"{topic_title}. " + t["topic_intro"], st.session_state.language)
with col2:
    st.write("")  # spacing

# ------------------------------------
# 🧠 QUIZ SECTION
# ------------------------------------
st.write("---")
st.subheader("🧠 " + t["take_quiz"])

if not st.session_state.quiz_completed:
    # Use topic_title in the quiz content for localization context
    quiz_question = f"Regarding **{topic_title}**, what is the main goal of finance?"
    
    if st.button("🚀 Start Quiz"):
        with st.expander("📋 Quiz", expanded=True):
            answer = st.radio(
                quiz_question,
                ["A) Spending money", "B) Managing money efficiently", "C) Avoiding all investments"],
                key="quiz_radio"
            )
            if st.button("✅ Submit Quiz"):
                if answer == "B) Managing money efficiently":
                    st.session_state.quiz_completed = True
                    st.success(t["quiz_completed"])
                    st.toast(t["quiz_completed"])
                else:
                    st.error("❌ Try again.")
else:
    st.success(t["quiz_completed"])

# ------------------------------------
# 💬 CHATBOT WITH VOICE (MIC + SPEAKER in input ribbon)
# ------------------------------------
st.write("---")
st.markdown(f"### {t['assistant']}")

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
    # Logic to transcribe mic_audio and set user_input would go here
    st.audio(mic_audio["bytes"])
    st.success("🎙️ Voice captured successfully! (Transcription logic goes here)")
    # For now, we'll pretend transcription happened and use a dummy input
    # user_input = "Tell me more about " + topic_title # Use this line if you want to test the full chat flow

if user_input:
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Generate response (Placeholder for OpenAI call)
    # The actual OpenAI call should be outside this section 
    # to prevent immediate UI rendering issues, but for simplicity:
    reply = f"That's an insightful question about {topic_title}! Here is a short dummy reply."
    
    # 3. Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun() # Rerun to display the new messages

# ------------------------------------
# 🚪 NAVIGATION
# ------------------------------------
st.write("---")

# Navigation callback functions
def go_to_dashboard():
    st.switch_page("financial_literacy.py")

def mark_complete_and_go_next():
    # Placeholder: Logic to mark current topic as 'Yes' and calculate the next one
    
    # Current topic is marked as complete:
    current_canon_name, current_topic_idx, _ = st.session_state.selected_topic
    if "completed_topics" in st.session_state:
        st.session_state.completed_topics[current_canon_name][current_topic_idx] = "Yes"
    
    st.toast("Topic completed! Proceeding to the next lesson.")
    go_to_dashboard() # For now, just go back to refresh the dashboard

col1, col2, col3 = st.columns([1, 1, 2])

# Previous button (always enabled, goes back to dashboard)
col1.button(f"⬅️ {t['previous']}", on_click=go_to_dashboard)

# Next button (disabled until quiz is complete)
# In a real app, this should calculate the next topic and set selected_topic/canon_topic_index
col2.button(
    f"➡️ {t['next']}", 
    disabled=not st.session_state.quiz_completed,
    on_click=mark_complete_and_go_next
)

# Back to Dashboard button
col3.button(f"🏠 {t['back']}", on_click=go_to_dashboard)