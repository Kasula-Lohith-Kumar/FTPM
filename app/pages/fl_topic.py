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

    # --- Helper to normalize quiz data ---
    def normalize_quiz_output(raw):
        """Standardize quiz data to always return a list of question dicts."""
        if raw is None:
            return None
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for key in ("questions", "quiz", "items"):
                if key in raw and isinstance(raw[key], list):
                    return raw[key]
            vals = [v for v in raw.values() if isinstance(v, dict) and "question" in v]
            if vals:
                return vals
        return None
    # --- Detect language change and regenerate quiz ---
    last_lang = st.session_state.get("last_quiz_language")
    if (
        st.session_state.language and st.session_state.language != last_lang
    ):
        st.info(f"🌐 Language changed to **{st.session_state.language}** — regenerating quiz...")
        try:
            raw_quiz = oap.generate_quiz()
            qs = normalize_quiz_output(raw_quiz)
            if qs and len(qs) > 0:
                st.session_state.quiz_questions = qs[:5]
                st.session_state.quiz_answers = {}
                st.session_state.quiz_feedback = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_completed = False
                st.session_state.last_quiz_language = st.session_state.language
                st.rerun()
            else:
                st.warning("Could not regenerate quiz for the new language.")
        except Exception as e:
            st.error(f"Error regenerating quiz for new language: {e}")
            
    # --- Quiz section ---
    st.write("---")
    st.subheader("🧠 " + t["take_quiz"])

    # ✅ Initialize session state variables once
    st.session_state.setdefault("last_quiz_language", None)
    st.session_state.setdefault("quiz_questions", None)
    st.session_state.setdefault("quiz_answers", {})
    st.session_state.setdefault("quiz_feedback", {})
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("quiz_completed", False)


        # Detect language change and regenerate quiz (only after normalize_quiz_output is defined)
    if (
        "language" in st.session_state
        and st.session_state.language
        and st.session_state.language != st.session_state.last_quiz_language
    ):
        st.info(f"🌐 Language changed to **{st.session_state.language}** — regenerating quiz...")
        try:
            raw_quiz = oap.generate_quiz()
            qs = normalize_quiz_output(raw_quiz)
            if qs and len(qs) > 0:
                st.session_state.quiz_questions = qs[:5]
                st.session_state.quiz_answers = {}
                st.session_state.quiz_feedback = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_completed = False
                st.session_state.last_quiz_language = st.session_state.language
                # rerun compat for old/new Streamlit
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.warning("Could not regenerate quiz for the new language.")
        except Exception as e:
            st.error(f"Error regenerating quiz for new language: {e}")

    # Ensure these session_state keys exist
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_feedback" not in st.session_state:
        st.session_state.quiz_feedback = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False
    if "last_quiz_language" not in st.session_state:
        st.session_state.last_quiz_language = None


    # When user clicks Start (or if we don't have questions yet) generate quiz questions
    start_button = st.button("🚀 Start Quiz")
    if start_button and not st.session_state.quiz_questions:
        try:
            raw_quiz = oap.generate_quiz()  # your existing function that returns 5 questions
            qs = normalize_quiz_output(raw_quiz)
            if not qs or len(qs) < 1:
                st.error("Could not parse quiz questions from the generator. Please try again.")
            else:
                # Keep only first 5 questions (or exactly 5 if generator returns 5)
                st.session_state.quiz_questions = qs[:5]
                st.session_state.quiz_answers = {}
                st.session_state.quiz_feedback = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_completed = False
                st.rerun()
        except Exception as e:
            st.error(f"Error generating quiz: {e}")

    # If we already have quiz questions and quiz not completed, show them
    if not st.session_state.quiz_completed:
        if st.session_state.quiz_questions:
            topic_title = st.session_state.selected_topic[0] if "selected_topic" in st.session_state else "Topic"
            st.markdown(f"**Topic:** {topic_title}")

            with st.form(key="quiz_form"):
                # show all questions with radio buttons
                for i, q in enumerate(st.session_state.quiz_questions):
                    q_text = q.get("question") if isinstance(q, dict) else str(q)
                    options = q.get("options") if isinstance(q, dict) else []
                    answer_key = f"q{i}_radio"

                    # If options exist, display as radio with index-prefixed labels preserved
                    if options and isinstance(options, (list, tuple)):
                        st.radio(f"Q{i+1}. {q_text}", options, key=answer_key)
                    else:
                        # fallback: show a text input if options missing (shouldn't happen)
                        st.text_input(f"Q{i+1}. {q_text} — (no options returned by generator)", key=answer_key)

                submit_all = st.form_submit_button("✅ Submit All")

                if submit_all:
                    # Evaluate all answers
                    any_wrong = False
                    st.session_state.quiz_feedback = {}
                    for i, q in enumerate(st.session_state.quiz_questions):
                        options = q.get("options") if isinstance(q, dict) else []
                        correct = q.get("answer") if isinstance(q, dict) else None
                        user_sel = st.session_state.get(f"q{i}_radio")
                        # Normalize comparisons: exact-match required per your earlier requirement.
                        if user_sel is None:
                            # No selection made
                            st.session_state.quiz_feedback[i] = {
                                "result": "no_answer",
                                "message": "No answer selected."
                            }
                            any_wrong = True
                        elif correct is None:
                            st.session_state.quiz_feedback[i] = {
                                "result": "unknown",
                                "message": "Correct answer not available to evaluate."
                            }
                            any_wrong = True
                        else:
                            if user_sel == correct:
                                st.session_state.quiz_feedback[i] = {
                                    "result": "correct",
                                    "message": "✔️ Correct"
                                }
                            else:
                                st.session_state.quiz_feedback[i] = {
                                    "result": "wrong",
                                    "message": f"❌ Answer provided is wrong — correct answer: **{correct}**",
                                    "your_answer": user_sel
                                }
                                any_wrong = True

                    st.session_state.quiz_submitted = True
                    # show feedback immediately below the form
                    for i, q in enumerate(st.session_state.quiz_questions):
                        fb = st.session_state.quiz_feedback.get(i, {})
                        q_text = q.get("question") if isinstance(q, dict) else str(q)
                        if fb.get("result") == "correct":
                            st.success(f"Q{i+1}. {q_text} — {fb['message']}")
                        elif fb.get("result") == "wrong":
                            st.error(f"Q{i+1}. {q_text} — {fb['message']}")
                        elif fb.get("result") == "no_answer":
                            st.warning(f"Q{i+1}. {q_text} — {fb['message']}")
                        else:
                            st.info(f"Q{i+1}. {q_text} — {fb.get('message','Evaluated.')}")

                    # After evaluating all, mark overall completion (you asked to set True later)
                    st.session_state.quiz_completed = True
                    # Optional UI acknowledgements
                    st.success(t["quiz_completed"])
                    try:
                        st.toast(t["quiz_completed"])
                    except Exception:
                        pass  # st.toast may not be available in all Streamlit versions
        else:
            st.info("Click **Start Quiz** to generate 5 questions for this topic.")
    else:
        # quiz already completed
        st.success(t["quiz_completed"])
        # display feedback / stored answers if available
        if st.session_state.get("quiz_feedback"):
            st.write("### Your results")
            for i, q in enumerate(st.session_state.quiz_questions or []):
                fb = st.session_state.quiz_feedback.get(i, {})
                q_text = q.get("question") if isinstance(q, dict) else str(q)
                if fb.get("result") == "correct":
                    st.success(f"Q{i+1}. {q_text} — ✔️ Correct")
                elif fb.get("result") == "wrong":
                    st.error(f"Q{i+1}. {q_text} — ❌ Wrong — correct answer: **{q.get('answer')}** — Your answer: {fb.get('your_answer')}")
                elif fb.get("result") == "no_answer":
                    st.warning(f"Q{i+1}. {q_text} — No answer selected.")
                else:
                    st.info(f"Q{i+1}. {q_text} — {fb.get('message','Evaluated.')}")


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
        user_input = st.chat_input("💬 ChatBot with 5-Messages Memory, Ask your question ...")


    with chat_col2:
        st.write("Record your voice below:")
        audio_input = st.audio_input("🎧 Record your voice")


    with chat_col3:
        if st.button("🔊", key="chat_speaker"):
            if st.session_state.messages:
                speak_text(st.session_state.messages[-1]["content"], st.session_state.language)
            else:
                st.warning("No response to speak yet.")

    # Process input or voice
    if audio_input:
        st.info("⏳ Transcribing...")
        try:
            text = oap.audio_transcription(audio_input)
            st.success("✅ Transcribed Text:")
            st.write(text)
        except Exception as e:
            st.error(f"❌ Transcription failed: {e}")


    if user_input:
        oap.add_to_buffer("user", user_input)
        # Display chat history
        for msg in st.session_state.buffer:
            with st.chat_message(msg["role"]):
                # st.markdown(msg["content"])
                reply = oap.chat_bot()
                st.session_state.messages.append({"role": "user", "content": user_input})
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
            st.session_state['page_status'] = 'financial_literacy'
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