import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
from openai import OpenAI
from pages import fl_config
from app import openai_api_prompts as oap
import json
from google_sheets.gsheets_operations import get_mappings


def run():
    # --- Hide sidebar and adjust layout ---
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            section[data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
            .block-container {
                padding-left: 6rem;
                padding-right: 2rem;
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Page setup ---
    st.set_page_config(page_title="Finance Tutor", layout="wide")

    # --- Initialize session state variables ---
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Lohith"
    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = ("Finance Fundamentals", 0, "Introduction to Finance")
    if "canon_topic_index" not in st.session_state:
        st.session_state.canon_topic_index = (0, 0)
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "English"

    # --- Text-to-Speech helpers ---
    def get_tts_lang(language):
        mapping = {
            "English": "en",
            "తెలుగు (Telugu)": "te",
            "हिंदी (Hindi)": "hi",
            "தமிழ் (Tamil)": "ta",
            "ಕನ್ನಡ (Kannada)": "kn",
        }
        return mapping.get(language, "en")

    def speak_text(text, language):
        lang_code = get_tts_lang(language)
        try:
            tts = gTTS(text=text, lang=lang_code)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Error generating audio: {e}")

    # --- Header & language setup ---
    lang = st.session_state.language
    t = fl_config.translations[lang]
    chapter_name, topic_index, topic_title = st.session_state.selected_topic

    st.markdown(
        f"""
        <div style="background-color:#0f1724; padding:18px; border-radius:10px; color:white;">
            <h2>👋 {t['welcome']}, {st.session_state.user_name}!</h2>
            <p>📘 {chapter_name} | 🧩 {topic_title}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Language selector ---
    prev_lang = st.session_state.language
    st.markdown(f"### {fl_config.translations[prev_lang]['choose_language']}")

    language = st.selectbox(
        "",
        options=list(fl_config.translations.keys()),
        index=list(fl_config.translations.keys()).index(prev_lang),
        key="language_selector",
    )

    if language != prev_lang:
        st.session_state.language = language
        new_lang = st.session_state.language

        s_index, i = st.session_state.canon_topic_index
        localized_section_list = list(fl_config.topics_language[new_lang].keys())

        if s_index < len(localized_section_list):
            localized_section_name = localized_section_list[s_index]
        else:
            localized_section_name = st.session_state.selected_topic[0]

        localized_topic_list = fl_config.topics_language[new_lang].get(localized_section_name, [])

        if i < len(localized_topic_list):
            localized_topic_title = localized_topic_list[i]
        else:
            localized_topic_title = st.session_state.selected_topic[2]

        st.session_state.selected_topic = (
            localized_section_name,
            i,
            localized_topic_title,
        )
        st.rerun()

    # mapping = {"Introduction to Finance": "A1", "ఆర్థికానికి పరిచయం": "B1", ...}

    # --- Reload translation variables ---
    lang = st.session_state.language
    t = fl_config.translations[lang]
    chapter_name, topic_index, topic_title = st.session_state.selected_topic

    # --- Learning material section ---
    st.markdown(f"### 📖 {t['learning_material']}")

    # Get Google Sheets worksheet object
    sheet = st.session_state['topics_sheet']

    # Get the cell based on the topic (from mapping)
    cell = get_mappings().get(topic_title)

    if not cell:
        st.error("⚠️ No mapping found for this topic.")
    else:
        # --- Try to retrieve from cache or Google Sheets ---
        topic_cache = st.session_state.get('topic_cache_data', {})
        topic_value = topic_cache.get(topic_title)

        # --- Layout for buttons ---
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button(t["speak_button"], key="speaker_button"):
                speak_text(f"{topic_title}. " + t["topic_intro"], st.session_state.language)

        with col2:
            # 🔄 Refresh button: clear cache and regenerate only for this topic
            if st.button("♻️ New Response", key="refresh_button"):
                st.session_state['topic_cache_data'].pop(topic_title, None)
                st.info("🔄 Regenerating lesson content... please wait.")
                try:
                    new_content = oap.learning_material()
                    if new_content:
                        st.session_state['topic_cache_data'][topic_title] = new_content
                        sheet.update_acell(cell, new_content)
                        st.success("✅ Lesson updated successfully!")
                        st.rerun()  # refresh Streamlit UI
                except Exception as e:
                    st.error(f"❌ Error while regenerating content: {e}")

        # --- Retrieve content (cached, sheet, or new) ---
        if topic_value is None:
            try:
                sheet_value = sheet.acell(cell).value
            except Exception:
                sheet_value = None

            if sheet_value:
                print(f"✅ Retrieved content for '{topic_title}' from Google Sheets.")
                st.write(sheet_value)
                topic_cache[topic_title] = sheet_value
            else:
                content = oap.learning_material()
                if content:
                    st.write(content)
                    topic_cache[topic_title] = content
                    sheet.update_acell(cell, content)
        else:
            print(f"♻️ Retrieved '{topic_title}' content from local cache.")
            st.write(topic_value)

        # --- Update cache in session ---
        st.session_state['topic_cache_data'] = topic_cache

    # --- Quiz section ---
    st.write("---")
    st.subheader("🧠 " + t["take_quiz"])

    if not st.session_state.quiz_completed:
        quiz_question = f"Regarding **{topic_title}**, what is the main goal of finance?"

        if st.button("🚀 Start Quiz"):
            with st.expander("📋 Quiz", expanded=True):
                answer = st.radio(
                    quiz_question,
                    ["A) Spending money", "B) Managing money efficiently", "C) Avoiding all investments"],
                    key="quiz_radio",
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

    # --- Chatbot section with mic & speaker in ribbon ---
    st.write("---")
    st.markdown(f"### {t['assistant']}")

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input + mic + speaker ribbon
    chat_col1, chat_col2, chat_col3 = st.columns([8, 1, 1])

    with chat_col1:
        user_input = st.chat_input("Ask your question...")

    with chat_col2:
        mic_audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="🛑",
            just_once=True,
            use_container_width=True,
            key="chat_mic",
        )

    with chat_col3:
        if st.button("🔊", key="chat_speaker"):
            if st.session_state.messages:
                speak_text(st.session_state.messages[-1]["content"], st.session_state.language)
            else:
                st.warning("No response to speak yet.")

    # Process input or voice
    if mic_audio:
        st.audio(mic_audio["bytes"])
        st.success("🎙️ Voice captured successfully! (Transcription logic goes here)")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = f"That's an insightful question about {topic_title}! Here is a short dummy reply."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # --- Navigation buttons ---
    st.write("---")

    def go_previous_step():
        st.session_state['page_status'] = 'financial_literacy'
        st.switch_page("pages/financial_literacy.py")

    def mark_complete_and_go_next():
        current_canon_name, current_topic_idx, _ = st.session_state.selected_topic
        if "completed_topics" in st.session_state:
            st.session_state.completed_topics[current_canon_name][current_topic_idx] = "Yes"
        st.toast("Topic completed! Proceeding to the next lesson.")
        st.switch_page("pages/financial_literacy.py")

    def go_to_dashboard():
        st.session_state['page_status'] = 'welcome'
        del st.session_state.selected_option
        st.switch_page("pages/welcome.py")

    col1, col2, col3 = st.columns([1, 1, 2])

    # Previous button
    if col1.button(f"⬅️ {t['previous']}"):
        go_previous_step()

    # Next button (enabled only after quiz)
    if col2.button(f"➡️ {t['next']}", disabled=not st.session_state.quiz_completed):
        mark_complete_and_go_next()

    # Back to dashboard button
    if col3.button(f"🏠 {t['back']}"):
        go_to_dashboard()


# ... (rest of the initialization code remains the same)
if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'login' # Start at login/home page
    st.switch_page("pages/login.py")

if 'username' not in st.session_state:
    # A username doesn't exist yet, so we don't set a default display name.
    # We just ensure the key exists, but it's okay to leave it blank or None for now.
    st.session_state['username'] = None 

if st.session_state['page_status'] == 'fl_topic':
    print(f"page state : {st.session_state['page_status']}")
    run()
