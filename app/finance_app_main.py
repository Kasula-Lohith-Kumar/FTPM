import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from pages import home
import registration as r
import json
from google_sheets import gsheets_config as gsc

# Hides the default sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .block-container {
            padding-left: 6rem;
            padding-right: 2rem;
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

def is_streamlit_cloud() -> bool:
    """Detect if running inside Streamlit Cloud deployment."""
    return "STREAMLIT_RUNTIME" in os.environ

def load_key_file_data():
    """
    Loads Google Service Account credentials.
    Handles both local and Streamlit Cloud environments safely.
    """
    try:
        if is_streamlit_cloud():
            print("🌐 STREAMLIT_RUNTIME detected — loading from Streamlit secrets...")
            key_data = json.loads(st.secrets["gcp_service_account"])
        else:
            print("💻 LOCAL_RUNTIME detected — loading from local JSON file...")
            with open(gsc.LOCAL_KEY_PATH, "r") as file:
                key_data = json.load(file)
        
        print("✅ Successfully loaded GCP key data.")
        return key_data

    except FileNotFoundError as e:
        print(f"❌ Local key file not found: {e}")
        st.error("Local service account key file missing.")
        return None

    except KeyError as e:
        print(f"❌ Missing key in Streamlit secrets: {e}")
        st.error("Missing 'gcp_service_account' entry in Streamlit secrets.")
        return None

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        st.error("Service account file contains invalid JSON.")
        return None

    except Exception as e:
        print(f"⚠️ Unexpected error while loading key data: {e}")
        st.error(f"Unexpected error: {e}")
        return None


if __name__ == "__main__":

    gsc.KEY_FILE_DATA = load_key_file_data()

    if 'page_status' not in st.session_state:
        st.session_state['page_status'] = 'home'

    # show_home_content()
    if st.session_state['page_status'] == 'home':
        home.show_home_content()

    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.switch_page("pages/welcome.py")

    # if st.session_state['page_status'] == 'welcome':
    #     welcome.run()

    elif st.session_state['page_status'] == 'auth':
        authentiation.show_auth_options()

    elif st.session_state['page_status'] == 'dashboard':
        st.title("Welcome to Your Portfolio Dashboard! 📈")
        # This is where your main app functionality would live
        if st.button("Logout"):
            st.session_state['page_status'] = 'home'
            # st.experimental_rerun()