import os
import streamlit as st
from dotenv import load_dotenv

def get_openai_key():
    key = None

    try:
        if st.session_state.get("runtime") == "streamlit":
            try:
                key = st.secrets["openai_api_key"]
                if not key:
                    raise ValueError("Empty key in Streamlit secrets.")
                print(f'✅ OpenAPI key loaded from {st.session_state.get("runtime")} successfully!!')
            except Exception as e:
                st.error(f"⚠️ Failed to load key from Streamlit secrets: {e}")
                st.stop()

        else:
            try:
                load_dotenv()
                key = os.getenv("OPENAI_API_KEY")
                if not key:
                    raise ValueError("OPENAI_API_KEY not found in .env file.")
                print(f'✅ OpenAPI key loaded from {st.session_state.get("runtime")} successfully!!')
            except Exception as e:
                st.error(f"⚠️ Failed to load key from .env file: {e}")
                st.stop()

    except Exception as e:
        st.error(f"🚫 Unexpected error loading API key: {e}")
        st.stop()
    print(f'In get_openai_key : {key}')
    return key
