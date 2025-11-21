import streamlit as st
from utils import audio_u
from utils import buffer_u


def chat_buttons(input_msg, asst_text):
    fallback_text = 'Currently this audio feature is not supported'
    warning_msg = "No response to speak yet."
    speaker_key = "chat_speaker"
    cc_key = "clear_chat_history"
    audio_foramt = "audio/mp3"
    cc_button_name = "🚮 Clear Chat"
    speaker_icon = "🔊"
    bin_icon = "🗑️"
    ch_clear_msg = "Chat history cleared!"

    # --- Chatbot section with mic & speaker in ribbon ---
    st.write("---")
    st.markdown(f"### {asst_text}")

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    chat_col1, chat_col2, chat_col3 = st.columns([8, 1, 1])

    with chat_col1:
        user_input = st.chat_input(input_msg)


    # with chat_col2:
    #     st.write("Record your voice below:")
    #     audio_input = st.audio_input("🎧 Record your voice")


    with chat_col2:
        if st.button(speaker_icon, key=speaker_key):
            if st.session_state.messages:
                # speak_text(st.session_state.messages[-1]["content"], st.session_state.language)
                audio = audio_u.safe_speak(st.session_state.messages[-1]["content"], fallback_text)
            else:
                audio = audio_u.safe_speak(warning_msg, warning_msg)
                st.warning(warning_msg)

            if audio:
                    st.audio(audio, format=audio_foramt)

    with chat_col3:
        buffer_u.clear_buffer()


    return user_input