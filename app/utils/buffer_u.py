
import streamlit as st


def to_buffer(user_input, reply):
    if user_input:
        add_to_buffer("user", user_input)
        # Display chat history
        for msg in st.session_state.buffer:
            with st.chat_message(msg["role"]):
                # st.markdown(msg["content"])
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

def add_to_buffer(role, content):
    st.session_state.buffer.append({"role": role, "content": content})
    if len(st.session_state.buffer) > 10:
        st.session_state.buffer = st.session_state.buffer[-10:]

def to_buffer_rag(user_input, reply, image_path=None):
    """Store conversation in correct sequence: user → reply → image"""
    
    add_to_buffer_rag("user", user_input, "text")
    add_to_buffer_rag("assistant", reply, "text")

    if image_path:
        add_to_buffer_rag("assistant", image_path, "image")

    st.rerun()


def add_to_buffer_rag(role, content, type="text"):
    st.session_state.buffer.append({
        "role": role,
        "content": content,
        "type": type
    })

    # Limit chat memory
    st.session_state.buffer = st.session_state.buffer[-10:]

def clear_buffer():
    cc_button_name = "🚮 Clear Chat"
    cc_key = "clear_chat_history"
    ch_clear_msg = "Chat history cleared!"
    bin_icon = "🗑️"

    if st.button(cc_button_name, key=cc_key):
            st.session_state.messages = []
            st.session_state.buffer = []
            st.toast(ch_clear_msg, icon=bin_icon)
            st.rerun()   # 🔥 immediately refresh UI

def force_clear_buffer():
        st.session_state.messages = []
        st.session_state.buffer = []